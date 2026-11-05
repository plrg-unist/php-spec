#!/usr/bin/env python3
"""Independent namespace validation phase, header receipts and parser stops."""
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
    'mixed-before': (b'namespace A {}\nnamespace B;\ndeclare(encoding=1);\necho ;', [3], 4),
    'code-before': (b'echo "BAD|";namespace A;\ndeclare(encoding=1);\necho ;', [2], 3),
    'nested-before': (b'namespace A { namespace B {} }\ndeclare(encoding=1);\necho ;', [2], 3),
    'nested-after': (b'namespace A { namespace B {declare(encoding=1);} }\ndeclare(encoding=2);\necho ;', [1, 2], 3),
    'nested-repeat-after': (b'namespace A { namespace B {declare(encoding=1);} }\ndeclare(encoding=2,encoding=3);\necho ;', [1, 2, 2], 3),
    'inner-nonliteral': (b'namespace A { namespace B {declare(encoding=1,encoding=true);} }\ndeclare(encoding=2);\necho ;', [1], 1),
    'syntax-before': (b'echo ;namespace A {namespace B{}}\ndeclare(encoding=1);', [], 1),
    'nested-outer-body': (b'namespace A { namespace B {}\ndeclare(encoding=1);}\necho ;', [2], 3),
    'complete-nested': (b'namespace A {namespace B{}}\ndeclare(encoding=1);', [2], None),
    'complete-mixed': (b'namespace A{} namespace B;\ndeclare(encoding=1);', [2], None),
}
PROBE = r'''<?php declare(strict_types=1);
require '@ROOT@/frontend/autoload.php';
require '@ROOT@/frontend/FileLexer.php';
require '@ROOT@/frontend/EvalLexer.php';
require '@ROOT@/frontend/RejectedHeaderParser.php';
$version = PhpParser\PhpVersion::fromComponents(8,5); $records = [];
$source = 'namespace A {namespace B{}}';
$errors = new PhpParser\ErrorHandler\Collecting();
$ast = (new PhpParser\Parser\Php8(new EvalLexer(),$version))->parse($source,$errors);
assert(is_array($ast) && count($errors->getErrors()) === 1);
assert($errors->getErrors()[0]->getRawMessage() === 'Namespace declarations cannot be nested');
assert(namespaceStructureErrorMatches($errors->getErrors()[0],$ast));
$thrown = false;
try { (new PhpParser\Parser\Php8(new EvalLexer(),$version))->parse($source); }
catch (PhpParser\Error $error) { $thrown = $error->getRawMessage() === 'Namespace declarations cannot be nested'; }
assert($thrown); $records[] = ['id'=>'ordinary-parser-validation-preserved'];
foreach ([
    'recursive'=>'namespace A{namespace B{namespace C{}}}declare(encoding=1);echo ;declare(encoding=2);',
    'grammar-stop'=>'namespace A{namespace B{}}echo ;declare(encoding=2);',
    'other-validation'=>'namespace A{namespace B{}}class C{readonly function f(){}}declare(encoding=2);echo ;'
] as $name=>$source) {
    $parser = new RejectedHeaderParser(new RejectedEvalLexer(),$version); $caught = null;
    try { $parser->parse($source,new PhpParser\ErrorHandler\Collecting()); }
    catch (PhpParser\Error $error) { $caught = $error->getRawMessage(); }
    assert($parser->parsingStarted && $caught !== null);
    assert($caught !== 'Namespace declarations cannot be nested');
    assert(count($parser->headers) === ($name==='recursive' ? 1 : 0));
    if ($name==='other-validation') assert($caught==='Invalid modifier for method');
    else assert(str_contains($caught,'Syntax error'));
    $records[] = ['id'=>$name,'headers'=>count($parser->headers),'error'=>$caught];
}
echo json_encode($records, JSON_THROW_ON_ERROR), "\n";
'''


def run(out):
    frontend = ParserWorker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    records = []
    try:
        for mode in ('eval', 'file'):
            for name, (source, lines, line) in CASES.items():
                if mode == 'file':
                    source, lines = b'<?php\n' + source, [value + 1 for value in lines]
                    if line is not None: line += 1
                packet = {'op': 'parse-' + mode, 'id': '9', 'mode': mode, 'profile': 'cli-raw-85', 'source': b64(source)}
                if mode == 'file': packet.update(requested=b64(b'ns.php'), resolved=b64(b'/review/ns.php'), opened=b64(b'/review/ns.php'))
                result = frontend.parse(packet)
                assert not result['diagnostics'] and all(result[key] == value for key, value in packet.items() if key != 'op')
                assert result['accepted'] is (line is None)
                if line is not None:
                    assert result['line'] == line
                    assert CLI['rejected_encoding_warning_lines'](result) == lines
                    assert result['category'] == ('parser_static_rejection' if name == 'inner-nonliteral' else 'parser_rejection')
                    assert len(result.get('headers', [])) == (2 if name in ('nested-after', 'nested-repeat-after', 'inner-nonliteral') else int(bool(lines)))
                records.append({'id': name, 'mode': mode, 'warning_lines': lines, 'accepted': result['accepted'],
                    'source_sha256': hashlib.sha256(source).hexdigest()})
    finally:
        frontend.close()
    path = out / 'namespace.php'; path.write_text(PROBE.replace('@ROOT@', str(ROOT)))
    process = recorded([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(path)], out / 'namespace', 15)
    assert process['exit'] == 0 and not process['timeout'] and not process['group_after']
    assert not (out / 'namespace.stderr').read_bytes()
    records.extend(json.loads((out / 'namespace.stdout').read_text()))
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
