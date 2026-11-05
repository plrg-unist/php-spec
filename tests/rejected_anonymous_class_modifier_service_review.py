#!/usr/bin/env python3
"""Rejected anonymous-class flags retain only headers before their modifiers."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from encoding_declare_protocol import CLI, ParserWorker
from error_handler_run import recorded
import static_types as types

SOURCE = ROOT / 'tests/semantics/anonymous_class_modifier_rejections'
b64 = lambda data: base64.b64encode(data).decode()
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
PROBE = r'''<?php declare(strict_types=1);
require '@ROOT@/frontend/autoload.php';
require '@ROOT@/frontend/EvalLexer.php';
require '@ROOT@/frontend/RejectedHeaderParser.php';
$version = PhpParser\PhpVersion::fromComponents(8, 5);
$records = [];
foreach ([
    'anonymous-abstract' => 'new abstract class{};',
    'anonymous-final' => 'new final class{};',
    'anonymous-readonly' => 'new readonly class{};',
    'named-final' => 'final class C{}',
] as $name => $source) {
    $errors = new PhpParser\ErrorHandler\Collecting();
    $ast = (new PhpParser\Parser\Php8(new EvalLexer(), $version))->parse($source, $errors);
    assert(is_array($ast) && !$errors->hasErrors());
    $records[] = ['id' => 'ordinary-' . $name, 'errors' => 0];
}
foreach ([
    'abstract' => ['declare(encoding=1);new abstract class{function f(){declare(encoding=2);}};declare(encoding=3);echo ;', 1, 'Invalid modifier for anonymous class'],
    'attributed-final' => ['new #[A(function(){declare(encoding=1);})] final class(function(){declare(encoding=2);}){};declare(encoding=3);echo ;', 1, 'Invalid modifier for anonymous class'],
    'readonly' => ['new readonly class{function f(){declare(encoding=1);}};declare(encoding=2);echo ;', 2, 'Syntax error'],
    'named-after-new' => ['new C;abstract class self{function f(){declare(encoding=1);}}declare(encoding=2);echo ;', 2, 'Syntax error'],
    'nested-named-after-new' => ['function f(){new C;final class parent{function g(){declare(encoding=1);}}}declare(encoding=2);echo ;', 2, 'Syntax error'],
    'first-attributed-abstract' => ['#[A] abstract class self{function f(){declare(encoding=1);}}declare(encoding=2);echo ;', 2, 'Syntax error'],
    'first-attributed-final' => ['#[A] final class parent{function f(){declare(encoding=1);}}declare(encoding=2);echo ;', 2, 'Syntax error'],
] as $name => [$source, $count, $prefix]) {
    $parser = new RejectedHeaderParser(new RejectedEvalLexer(), $version);
    $caught = null;
    try { $parser->parse($source, new PhpParser\ErrorHandler\Collecting()); }
    catch (PhpParser\Error $error) { $caught = $error->getRawMessage(); }
    assert($parser->parsingStarted && $caught !== null);
    assert(count($parser->headers) === $count && str_starts_with($caught, $prefix));
    $records[] = ['id' => 'rejected-' . $name, 'headers' => $count, 'foreign_stop' => $caught];
}
echo json_encode($records, JSON_THROW_ON_ERROR), "\n";
'''


def run(out):
    frontend = ParserWorker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    records = []
    try:
        for name, case in json.loads((SOURCE / 'cases.json').read_text()).items():
            source = (SOURCE / name / 'unit.php').read_bytes(); mode = case['mode']
            packet = {'op': 'parse-' + mode, 'id': '1', 'mode': mode,
                'profile': 'cli-raw-85', 'source': b64(source)}
            if mode == 'file':
                packet.update(requested=b64(b'classes.php'), resolved=b64(b'/review/classes.php'),
                    opened=b64(b'/review/classes.php'))
            result = frontend.parse(packet)
            assert not result['accepted'] and result['line'] == case['line']
            assert result['category'] == ('parser_static_rejection' if case['kind'] == 'CompileError' else 'parser_rejection')
            assert base64.b64decode(result['message']) == case['message'].encode()
            assert [header['beginLine'] for header in result.get('headers', [])] == case['warning_lines']
            assert CLI['rejected_encoding_warning_lines'](result) == case['warning_lines']
            records.append({'id': name, 'source_sha256': hashlib.sha256(source).hexdigest(),
                'warnings': case['warning_lines'], 'headers': len(result.get('headers', []))})
    finally:
        frontend.close()
    path = out / 'probe.php'; path.write_text(PROBE.replace('@ROOT@', str(ROOT)))
    process = recorded([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(path)], out / 'probe', 15)
    assert process['exit'] == 0 and not process['timeout'] and not process['group_after']
    assert not (out / 'probe.stderr').read_bytes()
    records.extend(json.loads((out / 'probe.stdout').read_text()))
    return records, process


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    hashes = json.loads((SOURCE / 'hashes.json').read_text())
    assert hashes == {name: sha(SOURCE / name) for name in hashes}
    paths = [Path(__file__), SOURCE / 'cases.json', SOURCE / 'hashes.json',
        *(SOURCE / name for name in hashes), *(ROOT / name for name in (
            'frontend/RejectedHeaderParser.php', 'frontend/worker.php', 'frontend/EvalLexer.php',
            'frontend/FileLexer.php', 'frontend/encoding-literal.php', '.tools/php/bin/php',
            '.tools/php-file.so', 'spec/schema.json', 'tests/semantics/profile.json',
            'tests/semantics/encoding_declare_protocol.py', 'tests/semantics/recorded_worker.py',
            'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py',
            'vendor/php-parser/lib/PhpParser/ParserAbstract.php', 'vendor/php-parser/lib/PhpParser/Parser/Php8.php'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    assert before['.tools/php/bin/php'] == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'profile': types.PROFILE,
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'source_agreement_credit': 0, 'passed': False}
    try:
        report['records'], report['process'] = run(out)
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in paths}
        report['passed'] = report['head_stable'] and report['inputs_stable']
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']; print('pass', len(report['records']))


if __name__ == '__main__': main()
