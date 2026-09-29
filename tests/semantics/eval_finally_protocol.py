#!/usr/bin/env python3
"""Check source-derived eval pauses inside pending finally transfers."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ('return',
     b"<?php function f(){try{return 1;}finally{echo eval('return 2;');}} echo '|',f();",
     b'return 2;',
     'S.TODO = (EVAL_AWAIT n) :: ptask_a :: ptask_b :: ptask_c :: (FINALLY_RETURN porigin_try porigin_source poperand) :: (FINALLY_PHASE porigin_try 2) :: ptask_tail*'),
    ('throw',
     b'''<?php function f(){try{throw new Error('A');}finally{eval('echo "F";');}}try{f();}catch(Error $e){echo $e->getMessage();}''',
     b'echo "F";',
     'S.TODO = (EVAL_AWAIT n) :: ptask_a :: ptask_b :: ptask_c :: (FINALLY_RESUME porigin_try (n_object)) :: (FINALLY_PHASE porigin_try 1) :: ptask_tail*'),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = Path(tempfile.mkdtemp(prefix='eval-finally-protocol-', dir=ROOT / '.tools'))
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
    for name, source, eval_bytes, marker in CASES:
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
            parsed_eval = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
                                            'profile': 'cli-raw-85',
                                            'source': base64.b64encode(eval_bytes).decode()})
            assert parsed_eval['accepted'], parsed_eval
            eval_fixture = adapter.request({'op': 'check', 'ast': parsed_eval['ast'],
                                            'fixture': True})['fixture']
        finally:
            frontend.close()
            adapter.close()
        initial = '$php_run(' + checked['fixture'] + ', 500, ' + json.dumps(
            base64.b64encode(str(source_path).encode()).decode()) + ')'
        response = '(SOURCE_ACCEPT 1 (' + str(list(eval_bytes)) + ') ' + eval_fixture + ')'
        conditions = [
            'S = ' + initial,
            'S.COMPLETION = SOURCE_PENDING',
            'S.EVALCONTEXTS = pevalcontext :: eps',
            'n = pevalcontext.UNIT',
            marker,
            '$call_descriptors_valid(S)',
            'S_done = $eval_continue(S, ' + response + ')',
            'S_done.COMPLETION = NORMAL',
            'S_done.EVALCONTEXTS = eps',
            '$call_descriptors_valid(S_done)',
        ]
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
              'scope': 'Source-derived pending finalizer owners during eval parser pause.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
