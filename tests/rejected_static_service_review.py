#!/usr/bin/env python3
"""Independent compiler-only validation phases and retained parse-time stops."""
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

b64 = lambda data: base64.b64encode(data).decode()
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
CASES = {
    'class-self': (b'class self{}\ndeclare(encoding=1);\necho ;', [2], 3, 'ParseError', 1),
    'class-parent': (b'class parent{}\ndeclare(encoding=1);\necho ;', [2], 3, 'ParseError', 1),
    'interface-self': (b'interface self{}\ndeclare(encoding=1);\necho ;', [2], 3, 'ParseError', 1),
    'enum-self': (b'enum self{}\ndeclare(encoding=1);\necho ;', [2], 3, 'ParseError', 1),
    'extends-self': (b'class C extends self{}\ndeclare(encoding=1);\necho ;', [2], 3, 'ParseError', 1),
    'implements-parent': (b'class C implements parent{}\ndeclare(encoding=1);\necho ;', [2], 3, 'ParseError', 1),
    'use-alias-self': (b'use Foo as self;\ndeclare(encoding=1);\necho ;', [2], 3, 'ParseError', 1),
    'static-constructor': (b'class C{static function __construct(){}}\ndeclare(encoding=1);\necho ;', [2], 3, 'ParseError', 1),
    'try-without-catch': (b'try {}\ndeclare(encoding=1);\necho ;', [2], 3, 'ParseError', 1),
    'duplicate-modifier': (b'abstract abstract class C{}\ndeclare(encoding=1);\necho ;', [], 1, 'CompileError', 0),
    'syntax-before-self': (b'echo ;class self{}\ndeclare(encoding=1);', [], 1, 'ParseError', 0),
    'nonliteral-before-self': (b'declare(encoding=1,encoding=true);\nclass self{}\ndeclare(encoding=2);\necho ;', [1], 1, 'CompileError', 2),
    'class-self-body': (b'class self{function f(){declare(encoding=1);}}\ndeclare(encoding=2,encoding=3);\necho ;', [1, 2, 2], 3, 'ParseError', 2),
    'static-destructor': (b'class C{static function __destruct(){}}\ndeclare(encoding=1);\necho ;', [2], 3, 'ParseError', 1),
    'static-clone': (b'class C{static function __clone(){}}\ndeclare(encoding=1);\necho ;', [2], 3, 'ParseError', 1),
    'readonly-method': (b'class C{readonly function f(){}}\ndeclare(encoding=1);\necho ;', [], 1, 'CompileError', 0),
    'interface-extends-parent': (b'interface I extends parent{}\ndeclare(encoding=1);\necho ;', [2], 3, 'ParseError', 1),
    'enum-implements-self': (b'enum E implements self{}\ndeclare(encoding=1);\necho ;', [2], 3, 'ParseError', 1),
    'anonymous-extends-self': (b'$a=new class extends self{};\ndeclare(encoding=1);\necho ;', [2], 3, 'ParseError', 1),
    'readonly-method-body': (b'class C{readonly function f(){declare(encoding=1);}}\ndeclare(encoding=2);\necho ;', [], 1, 'CompileError', 1),
}
PROBE = r'''<?php declare(strict_types=1);
require '@ROOT@/frontend/autoload.php';
require '@ROOT@/frontend/FileLexer.php';
require '@ROOT@/frontend/EvalLexer.php';
require '@ROOT@/frontend/RejectedHeaderParser.php';
$version = PhpParser\PhpVersion::fromComponents(8,5); $records = [];
foreach ([
    'class'=>'class self{}', 'interface'=>'interface self{}', 'enum'=>'enum self{}',
    'magic'=>'class C{static function __construct(){}}', 'try'=>'try {}',
    'readonly'=>'class C{readonly function f(){}}'
] as $name=>$source) {
    $errors = new PhpParser\ErrorHandler\Collecting();
    $ast = (new PhpParser\Parser\Php8(new EvalLexer(),$version))->parse($source,$errors);
    assert(is_array($ast) && count($errors->getErrors()) === 1);
    $expected = $errors->getErrors()[0]->getRawMessage(); $caught = null;
    try { (new PhpParser\Parser\Php8(new EvalLexer(),$version))->parse($source); }
    catch (PhpParser\Error $error) { $caught = $error->getRawMessage(); }
    assert($caught === $expected); $records[] = ['id'=>'ordinary-'.$name,'error'=>$caught];
}
foreach ([
    'modifier'=>'abstract abstract class C{}declare(encoding=2);echo ;',
    'readonly'=>'class C{readonly function f(){}}declare(encoding=2);echo ;',
    'grammar'=>'class self{}echo ;declare(encoding=2);'
] as $name=>$source) {
    $parser = new RejectedHeaderParser(new RejectedEvalLexer(),$version); $caught = null;
    try { $parser->parse($source,new PhpParser\ErrorHandler\Collecting()); }
    catch (PhpParser\Error $error) { $caught = $error->getRawMessage(); }
    assert($parser->parsingStarted && $caught !== null && $parser->headers === []);
    if ($name==='grammar') assert(str_contains($caught,'Syntax error'));
    elseif ($name==='readonly') assert(str_contains($caught,'cannot be readonly'));
    else assert(str_contains($caught,'Multiple abstract modifiers'));
    $records[] = ['id'=>'rejected-stop-'.$name,'error'=>$caught];
}
echo json_encode($records, JSON_THROW_ON_ERROR), "\n";
'''


def run(out):
    frontend = ParserWorker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    records = []
    try:
        for mode in ('eval', 'file'):
            for name, (source, lines, line, kind, count) in CASES.items():
                if mode == 'file':
                    source, lines, line = b'<?php\n' + source, [value + 1 for value in lines], line + 1
                packet = {'op': 'parse-' + mode, 'id': '9', 'mode': mode, 'profile': 'cli-raw-85', 'source': b64(source)}
                if mode == 'file': packet.update(requested=b64(b'static.php'), resolved=b64(b'/review/static.php'), opened=b64(b'/review/static.php'))
                refusal = name == 'readonly-method-body'
                if refusal:
                    result = frontend.request(packet)
                    raw = (frontend.output / 'stderr').read_bytes()
                    delta = raw[len(frontend.recorded_stderr):]; frontend.recorded_stderr.extend(delta)
                    assert not delta and not CLI['dynamic_parser_stderr'](result, mode, delta)
                    assert CLI['rejected_encoding_warning_lines'](result) == [2 if mode == 'file' else 1]
                else:
                    result = frontend.parse(packet)
                    assert CLI['rejected_encoding_warning_lines'](result) == lines
                assert not result['diagnostics'] and all(result[key] == value for key, value in packet.items() if key != 'op')
                assert not result['accepted'] and result['line'] == line
                assert result['category'] == ('parser_static_rejection' if kind == 'CompileError' else 'parser_rejection')
                assert len(result.get('headers', [])) == count
                records.append({'id': name, 'mode': mode, 'warning_lines': lines, 'refusal': refusal,
                    'source_sha256': hashlib.sha256(source).hexdigest()})
    finally:
        frontend.close()
    path = out / 'static.php'; path.write_text(PROBE.replace('@ROOT@', str(ROOT)))
    process = recorded([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(path)], out / 'static', 15)
    assert process['exit'] == 0 and not process['timeout'] and not process['group_after']
    assert not (out / 'static.stderr').read_bytes()
    records.extend(json.loads((out / 'static.stdout').read_text()))
    return records, process


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    paths = [Path(__file__), *(ROOT / name for name in ('frontend/RejectedHeaderParser.php', 'frontend/worker.php',
        'frontend/EvalLexer.php', 'frontend/FileLexer.php', 'frontend/encoding-literal.php', 'bin/php-semantics',
        '.tools/php/bin/php', '.tools/php-file.so', 'spec/schema.json', 'tests/semantics/profile.json',
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
