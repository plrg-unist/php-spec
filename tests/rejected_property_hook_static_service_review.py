#!/usr/bin/env python3
"""Independent rejected hook validation phase and parser-stop controls."""
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

SOURCE = ROOT / 'tests/semantics/property_hook_static_rejections'
MULTI_SOURCE = ROOT / 'tests/semantics/multiproperty_hook_rejections'
b64 = lambda data: base64.b64encode(data).decode()
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
PROBE = r'''<?php declare(strict_types=1);
require '@ROOT@/frontend/autoload.php';
require '@ROOT@/frontend/EvalLexer.php';
require '@ROOT@/frontend/RejectedHeaderParser.php';
$version = PhpParser\PhpVersion::fromComponents(8, 5);
$records = [];
foreach ([
    'unknown' => 'class C{public int $x{foo;}}',
    'get-parameters' => 'class C{public int $x{get(){return 1;}}}',
    'empty-property' => 'class C{public int $x{}}',
    'empty-promoted' => 'class C{function __construct(public int $x {}){}}',
] as $name => $source) {
    $errors = new PhpParser\ErrorHandler\Collecting();
    $ast = (new PhpParser\Parser\Php8(new EvalLexer(), $version))->parse($source, $errors);
    assert(is_array($ast) && count($errors->getErrors()) === 1);
    $records[] = ['id' => 'ordinary-' . $name, 'error' => $errors->getErrors()[0]->getRawMessage()];
}
foreach ([
    'unknown' => ['class C{public int $x{foo{declare(encoding=1);}}} declare(encoding=2); echo ;', 2, 'Syntax error'],
    'get-parameters' => ['class C{public int $x{get(){declare(encoding=1);return 1;}}} declare(encoding=2); echo ;', 2, 'Syntax error'],
    'empty-property' => ['class C{public int $x{}} declare(encoding=2); echo ;', 1, 'Syntax error'],
    'empty-promoted' => ['class C{function __construct(public int $x {}){}} declare(encoding=2); echo ;', 1, 'Syntax error'],
    'bad-modifier' => ['declare(encoding=1); class C{public int $x{foo=>1; public get=>2;}} declare(encoding=2); echo ;', 1, 'Cannot use the public modifier on a property hook'],
    'multi-property-grammar' => ['class C{public $p,$q {get{declare(encoding=2);return 1;}}} declare(encoding=3); echo ;', 0, 'Invalid multi-property hook syntax'],
    'ordinary-multiple' => ['class C{public $p,$q;function f(){declare(encoding=1);}} declare(encoding=2); echo ;', 2, 'Syntax error'],
    'hook-before-comma' => ['class C{public $p{get{declare(encoding=1);return 1;}},$q;} declare(encoding=2); echo ;', 1, 'Syntax error'],
] as $name => [$source, $count, $errorPrefix]) {
    $parser = new RejectedHeaderParser(new RejectedEvalLexer(), $version);
    $caught = null;
    try { $parser->parse($source, new PhpParser\ErrorHandler\Collecting()); }
    catch (PhpParser\Error $error) { $caught = $error->getRawMessage(); }
    assert($parser->parsingStarted && $caught !== null);
    assert(count($parser->headers) === $count && str_starts_with($caught, $errorPrefix));
    $records[] = ['id' => 'rejected-' . $name, 'headers' => $count, 'foreign_stop' => $caught];
}
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
                packet.update(requested=b64(b'hooks.php'), resolved=b64(b'/review/hooks.php'),
                    opened=b64(b'/review/hooks.php'))
            result = frontend.parse(packet)
            assert CLI['rejected_encoding_warning_lines'](result) == case['warning_lines']
            assert not result['diagnostics'] and all(result[key] == value for key, value in packet.items() if key != 'op')
            assert not result['accepted'] and result['line'] == case['line']
            assert result['category'] == ('parser_static_rejection' if case['kind'] == 'CompileError' else 'parser_rejection')
            assert base64.b64decode(result['message']) == case['message'].encode()
            expected_headers = len(case['warning_lines']) + int(name.startswith('nonliteral-before-unknown'))
            assert len(result.get('headers', [])) == expected_headers
            records.append({'id': name, 'source_sha256': hashlib.sha256(source).hexdigest(),
                'warnings': case['warning_lines'], 'headers': len(result.get('headers', []))})
        for name, case in json.loads((MULTI_SOURCE / 'cases.json').read_text()).items():
            source = (MULTI_SOURCE / name / 'unit.php').read_bytes()
            mode = case['mode']
            packet = {'op': 'parse-' + mode, 'id': '12', 'mode': mode,
                'profile': 'cli-raw-85', 'source': b64(source)}
            if mode == 'file':
                packet.update(requested=b64(b'multi.php'), resolved=b64(b'/review/multi.php'),
                    opened=b64(b'/review/multi.php'))
            result = frontend.parse(packet)
            assert not result['diagnostics']
            assert not result['accepted'] and result['category'] == 'parser_rejection'
            assert result['line'] == case['line']
            assert base64.b64decode(result['message']) == case['message'].encode()
            assert [header['beginLine'] for header in result.get('headers', [])] == case['warning_lines']
            assert CLI['rejected_encoding_warning_lines'](result) == case['warning_lines']
            records.append({'id': 'multiproperty-' + name, 'mode': mode,
                'source_sha256': hashlib.sha256(source).hexdigest(),
                'warnings': case['warning_lines'], 'headers': len(result.get('headers', []))})
        for modifier in ('public', 'protected', 'private', 'static', 'abstract', 'readonly',
                'public(set)', 'protected(set)', 'private(set)', 'final final',
                'final public', 'public final', 'final', ''):
            source = (b'declare(encoding=1);\nclass C{public int $x{'
                + modifier.encode() + b' get=>1;}}\ndeclare(encoding=2);\necho ;')
            packet = {'op': 'parse-eval', 'id': '11', 'mode': 'eval',
                'profile': 'cli-raw-85', 'source': b64(source)}
            result = frontend.parse(packet)
            valid = modifier in ('final', '')
            assert not result['accepted'] and result['category'] == ('parser_rejection' if valid else 'parser_static_rejection')
            assert result['line'] == (4 if valid else 2)
            assert len(result.get('headers', [])) == (2 if valid else 1)
            assert CLI['rejected_encoding_warning_lines'](result) == ([1, 3] if valid else [1])
            message = (b'syntax error, unexpected token ";"' if valid else
                b'Multiple final modifiers are not allowed' if modifier == 'final final' else
                ('Cannot use the ' + ('public' if modifier in ('final public', 'public final') else modifier)
                    + ' modifier on a property hook').encode())
            assert base64.b64decode(result['message']) == message
            records.append({'id': 'modifier-' + (modifier or 'none'), 'mode': 'eval',
                'source_sha256': hashlib.sha256(source).hexdigest(),
                'warnings': [1, 3] if valid else [1], 'headers': 2 if valid else 1})
        for mode in ('eval', 'file'):
            source = b'class C{public $p,$q {get{declare(encoding=2);return 1;}}}\ndeclare(encoding=3);\necho ;'
            if mode == 'file': source = b'<?php\n' + source
            packet = {'op': 'parse-' + mode, 'id': '10', 'mode': mode,
                'profile': 'cli-raw-85', 'source': b64(source)}
            if mode == 'file':
                packet.update(requested=b64(b'multi.php'), resolved=b64(b'/review/multi.php'),
                    opened=b64(b'/review/multi.php'))
            result = frontend.parse(packet)
            assert not result['accepted'] and result['category'] == 'parser_rejection'
            assert result['line'] == 1 + int(mode == 'file')
            assert base64.b64decode(result['message']) == b'syntax error, unexpected token "{", expecting "," or ";"'
            assert len(result.get('headers', [])) == 0
            assert CLI['rejected_encoding_warning_lines'](result) == []
            assert (frontend.output / 'stderr').read_bytes() == bytes(frontend.recorded_stderr)
            assert CLI['dynamic_parser_stderr'](result, mode, b'')
            records.append({'id': 'multi-property-grammar', 'mode': mode,
                'source_sha256': hashlib.sha256(source).hexdigest(), 'foreign_headers': 0,
                'native_warning_lines': [], 'source_agreement_credit': 0})
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
    multi_hashes = json.loads((MULTI_SOURCE / 'hashes.json').read_text())
    assert hashes == {name: sha(SOURCE / name) for name in hashes}
    assert multi_hashes == {name: sha(MULTI_SOURCE / name) for name in multi_hashes}
    paths = [Path(__file__), SOURCE / 'cases.json', SOURCE / 'hashes.json',
        *(SOURCE / name for name in hashes), MULTI_SOURCE / 'cases.json', MULTI_SOURCE / 'hashes.json',
        *(MULTI_SOURCE / name for name in multi_hashes), *(ROOT / name for name in (
            'frontend/RejectedHeaderParser.php', 'frontend/worker.php', 'frontend/EvalLexer.php',
            'frontend/FileLexer.php', 'frontend/encoding-literal.php', '.tools/php/bin/php',
            '.tools/php-file.so', 'spec/schema.json', 'tests/semantics/profile.json',
            'tests/semantics/encoding_declare_protocol.py', 'tests/semantics/recorded_worker.py',
            'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    assert before['.tools/php/bin/php'] == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'profile': types.PROFILE,
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'source_agreement_credit': 0,
        'refusal_controls': 0, 'passed': False}
    try:
        report['records'], report['process'] = run(out)
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in paths}
        report['passed'] = report['head_stable'] and report['inputs_stable']
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']; print('pass', len(report['records']))


if __name__ == '__main__': main()
