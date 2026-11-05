#!/usr/bin/env python3
"""Independent rejected trait alias cutoff and ordinary-parser controls."""
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

SOURCE = ROOT / 'tests/semantics/trait_alias_modifier_rejections'
b64 = lambda data: base64.b64encode(data).decode()
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
PROBE = r'''<?php declare(strict_types=1);
require '@ROOT@/frontend/autoload.php';
require '@ROOT@/frontend/EvalLexer.php';
require '@ROOT@/frontend/RejectedHeaderParser.php';
$version = PhpParser\PhpVersion::fromComponents(8, 5);
$records = [];
foreach ([
    'named' => ['trait T{function f(){}} class C{use T{f as readonly g;}} declare(encoding=2); echo ;', 0, 'Invalid modifier for trait alias'],
    'unnamed' => ['trait T{function f(){}} class C{use T{f as private(set);}} declare(encoding=2); echo ;', 0, 'Invalid modifier for trait alias'],
    'missing-semicolon' => ['trait T{function f(){}} class C{use T{f as readonly g}} declare(encoding=2); echo ;', 0, 'Syntax error'],
    'ordinary-alias' => ['trait T{function f(){}} class C{use T{f as g;}} declare(encoding=2); echo ;', 1, 'Syntax error'],
    'precedence' => ['trait T{function f(){}} trait U{function f(){}} class C{use T,U{T::f insteadof U;}} declare(encoding=2); echo ;', 1, 'Syntax error'],
    'trait-host' => ['trait T{function f(){}} trait U{use T{f as readonly g;}} declare(encoding=2); echo ;', 0, 'Invalid modifier for trait alias'],
    'method-control' => ['class C{readonly function f(){declare(encoding=1);}} declare(encoding=2); echo ;', 0, 'Invalid modifier for method'],
    'constant-control' => ['class C{readonly const X=(function(){declare(encoding=1);});} declare(encoding=2); echo ;', 0, 'Invalid modifier for class constant'],
] as $name => [$source, $count, $errorPrefix]) {
    $parser = new RejectedHeaderParser(new RejectedEvalLexer(), $version);
    $caught = null;
    try { $parser->parse($source, new PhpParser\ErrorHandler\Collecting()); }
    catch (PhpParser\Error $error) { $caught = $error->getRawMessage(); }
    assert($parser->parsingStarted && $caught !== null);
    assert(count($parser->headers) === $count && str_starts_with($caught, $errorPrefix));
    $records[] = ['id' => $name, 'headers' => $count, 'foreign_stop' => $caught];
}
$source = 'trait T{function f(){}} class C{use T{f as readonly g;}}';
$errors = new PhpParser\ErrorHandler\Collecting();
$ordinary = (new PhpParser\Parser\Php8(new EvalLexer(), $version))->parse($source, $errors);
assert(is_array($ordinary) && count($ordinary) === 2 && count($errors->getErrors()) === 0);
$records[] = ['id' => 'ordinary-parser-unchanged', 'statements' => count($ordinary)];
echo json_encode($records, JSON_THROW_ON_ERROR), "\n";
'''


def run(out):
    cases = json.loads((SOURCE / 'cases.json').read_text())
    frontend = ParserWorker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    records = []
    try:
        for name, case in cases.items():
            source = (SOURCE / name / 'unit.php').read_bytes()
            mode = case['mode']
            packet = {'op': 'parse-' + mode, 'id': '9', 'mode': mode,
                'profile': 'cli-raw-85', 'source': b64(source)}
            if mode == 'file':
                packet.update(requested=b64(b'alias.php'), resolved=b64(b'/review/alias.php'),
                    opened=b64(b'/review/alias.php'))
            result = frontend.parse(packet)
            assert CLI['rejected_encoding_warning_lines'](result) == case['warning_lines']
            assert not result['diagnostics'] and all(result[key] == value for key, value in packet.items() if key != 'op')
            assert not result['accepted'] and result['line'] == case['line']
            assert result['category'] == ('parser_static_rejection' if case['kind'] == 'CompileError' else 'parser_rejection')
            assert base64.b64decode(result['message']) == case['message'].encode()
            assert len(result.get('headers', [])) == len(case['warning_lines'])
            records.append({'id': name, 'source_sha256': hashlib.sha256(source).hexdigest(),
                'warnings': case['warning_lines'], 'headers': len(result.get('headers', []))})
        for mode in ('eval', 'file'):
            for modifier in ('public', 'protected', 'private', 'static', 'abstract', 'final'):
                for named in (False, True):
                    source = (b'trait T{function f(){}}\nclass C{use T{f as '
                        + modifier.encode() + (b' g' if named else b'')
                        + b';}}\ndeclare(encoding=2);\necho ;')
                    if mode == 'file': source = b'<?php\n' + source
                    packet = {'op': 'parse-' + mode, 'id': '10', 'mode': mode,
                        'profile': 'cli-raw-85', 'source': b64(source)}
                    if mode == 'file':
                        packet.update(requested=b64(b'valid.php'), resolved=b64(b'/review/valid.php'),
                            opened=b64(b'/review/valid.php'))
                    result = frontend.parse(packet)
                    delta = int(mode == 'file')
                    assert not result['accepted'] and result['category'] == 'parser_rejection'
                    assert result['line'] == 4 + delta and base64.b64decode(result['message']) == b'syntax error, unexpected token ";"'
                    assert CLI['rejected_encoding_warning_lines'](result) == [3 + delta]
                    assert len(result.get('headers', [])) == 1
                    records.append({'id': 'valid-' + modifier + ('-named' if named else '-unnamed'),
                        'mode': mode, 'source_sha256': hashlib.sha256(source).hexdigest(),
                        'warnings': [3 + delta], 'headers': 1})
            source = b'trait T{function f(){}}\ntrait U{use T{f as readonly g;}}\ndeclare(encoding=2);\necho ;'
            if mode == 'file': source = b'<?php\n' + source
            packet = {'op': 'parse-' + mode, 'id': '11', 'mode': mode,
                'profile': 'cli-raw-85', 'source': b64(source)}
            if mode == 'file':
                packet.update(requested=b64(b'trait.php'), resolved=b64(b'/review/trait.php'),
                    opened=b64(b'/review/trait.php'))
            result = frontend.parse(packet)
            delta = int(mode == 'file')
            assert not result['accepted'] and result['category'] == 'parser_static_rejection'
            assert result['line'] == 2 + delta
            assert base64.b64decode(result['message']) == b'Cannot use the readonly modifier on a method'
            assert CLI['rejected_encoding_warning_lines'](result) == [] and not result.get('headers')
            records.append({'id': 'trait-host', 'mode': mode,
                'source_sha256': hashlib.sha256(source).hexdigest(), 'warnings': [], 'headers': 0})
    finally:
        frontend.close()
    path = out / 'probe.php'
    path.write_text(PROBE.replace('@ROOT@', str(ROOT)))
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
            'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py'))]
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
