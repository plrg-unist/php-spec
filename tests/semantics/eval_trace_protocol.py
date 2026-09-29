#!/usr/bin/env python3
"""Inspect source-derived eval exception frames while getTrace is unsupported."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ('parse-in-function',
     b"<?php function f(){try{eval('echo ;');}catch(ParseError $e){echo 'C';}} f();",
     b'echo ;', 'ParseError', ('f',)),
    ('compile-reject-in-function',
     b"<?php function f(){try{eval('class A { final abstract private function g(); }');}catch(CompileError $e){echo 'C';}} f();",
     b'class A { final abstract private function g(); }', 'CompileError', ('f',)),
    ('class-link',
     b"<?php try{eval('class C extends Missing {}');}catch(Error $e){echo 'C';}",
     b'class C extends Missing {}', 'Error', ('eval',)),
    ('function-defined-by-eval',
     b"<?php try{eval('function f(){1/0;} f();');}catch(DivisionByZeroError $e){echo 'C';}",
     b'function f(){1/0;} f();', 'DivisionByZeroError', ('f', 'eval')),
    ('direct-new-error',
     b"<?php try{eval('throw new Error(\"x\");');}catch(Error $e){echo 'C';}",
     b'throw new Error("x");', 'Error', ('eval',)),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = Path(tempfile.mkdtemp(prefix='eval-trace-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    inputs = [*modules, ROOT / 'spec/semantics/modules.json', runner,
              ROOT / '_build/default/adapter/main.exe', ROOT / 'frontend/worker.php',
              ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
              ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/recorded_worker.py',
              ROOT / 'tests/semantics/static_types.py', ROOT / 'frontend/wire.py',
              ROOT / 'tests/validate.py', Path(__file__)]
    before = {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    records = []
    for name, source, eval_bytes, kind, frame_names in CASES:
        directory = out / name
        directory.mkdir()
        source_path = directory / 'source.php'
        source_path.write_bytes(source)
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                           'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], directory / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            eval_parsed = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
                                            'profile': 'cli-raw-85',
                                            'source': base64.b64encode(eval_bytes).decode()})
            if eval_parsed['accepted']:
                eval_checked = adapter.request({'op': 'check', 'ast': eval_parsed['ast'], 'fixture': True})
        finally:
            frontend.close()
            adapter.close()
        initial = '$php_run(' + checked['fixture'] + ', 300, ' + json.dumps(
            base64.b64encode(str(source_path).encode()).decode()) + ')'
        if eval_parsed['accepted']:
            response = '(SOURCE_ACCEPT n pevalcontext.BYTES ' + eval_checked['fixture'] + ')'
        else:
            assert eval_parsed['category'] in ('parser_rejection', 'parser_static_rejection')
            message = list(base64.b64decode(eval_parsed['message']))
            rejected = ('SOURCE_PARSE_REJECT' if eval_parsed['category'] == 'parser_rejection'
                        else 'SOURCE_COMPILE_REJECT')
            response = '(' + rejected + ' n pevalcontext.BYTES (' + str(message) + ') ' + str(eval_parsed['line']) + ')'
        conditions = [
            'S = ' + initial,
            'S.COMPLETION = SOURCE_PENDING',
            'S.EVALCONTEXTS = pevalcontext :: pevalcontext_tail*',
            'n = pevalcontext.UNIT',
            '$call_descriptors_valid(S)',
            'S_done = $eval_continue(S, ' + response + ')',
            'S_done.COMPLETION = NORMAL',
            '$call_descriptors_valid(S_done)',
            'n_object = $(|S_done.OBJECTS| - 1)',
            'S_done.OBJECTS[n_object] = THROWABLE pthrowable',
            'pthrowable.KIND = ' + json.dumps(kind),
            'pthrowable.TRACE = [' + ','.join('ptraceframe_' + str(i) for i in range(len(frame_names))) + ']',
        ]
        for index, frame_name in enumerate(frame_names):
            frame = 'ptraceframe_' + str(index)
            expected_file = ('pevalcontext.FILE' if name == 'function-defined-by-eval' and index == 0
                             else '$call_sourcefile(S.FILES, pevalcontext.SITE)')
            conditions.extend([frame + '.NAME = $ptascii(' + json.dumps(frame_name) + ')',
                               frame + '.FILE = ' + expected_file,
                               frame + '.LINE = 1'])
        fixture = directory / 'protocol.watsup'
        fixture.write_text('dec $main() : bool\ndef $main() = true\n' + ''.join(
                               '  -- if ' + condition + '\n' for condition in conditions))
        command = [str(runner), *map(str, modules), str(fixture)]
        result = subprocess.run(command, capture_output=True, timeout=300)
        (directory / 'command.json').write_text(json.dumps(command) + '\n')
        (directory / 'stdout').write_bytes(result.stdout)
        (directory / 'stderr').write_bytes(result.stderr)
        passed = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        records.append({'id': name, 'pass': passed, 'assertions': len(conditions),
                        'source_sha256': digest(source_path), 'fixture_sha256': digest(fixture),
                        'runner_exit_status': result.returncode})
        print(name, passed, flush=True)
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    report = {'result': 'pass' if all(row['pass'] for row in records) else 'fail',
              'inputs': before, 'records': records,
              'scope': 'Internal generated TRACE fields; getTrace source calls remain Unsupported.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
