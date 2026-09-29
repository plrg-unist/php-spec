#!/usr/bin/env python3
"""Check a source-derived, paused class constant inside an eval unit."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SOURCE = b"<?php try { eval('return self::class;'); } catch(Error $e) { echo $e->getMessage(); }"
EVAL_SOURCE = b'return self::class;'
PREFIX = r'''
dec $class_head(pstate) : bool
def $class_head(S) = true
  -- if S.TODO = (EVAL (NExprClassConstFetch (NName (BYTES text_name) metadata_name) (NIdentifier (BYTES text_member) metadata_member) metadata)) :: ptask*
def $class_head(S) = false -- otherwise
dec $class_seek(pstate, nat) : pstate
def $class_seek(S, n) = S -- if $class_head(S)
def $class_seek(S, 0) = S -- if ~$class_head(S)
def $class_seek(S, n) = $class_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$class_head(S) /\ $(n > 0)
'''


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = Path(tempfile.mkdtemp(prefix='eval-class-scope-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    inputs = [*modules, ROOT / 'spec/semantics/modules.json', runner,
              ROOT / '_build/default/adapter/main.exe', ROOT / 'frontend/worker.php',
              ROOT / 'frontend/EvalLexer.php', ROOT / '.tools/php/bin/php',
              ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/profile.json',
              ROOT / 'tests/semantics/recorded_worker.py',
              ROOT / 'tests/semantics/static_types.py', ROOT / 'frontend/wire.py',
              ROOT / 'tests/validate.py', Path(__file__)]
    before = {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    source_path = out / 'source.php'
    source_path.write_bytes(SOURCE)
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(SOURCE).decode()})
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        eval_parsed = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
                                        'profile': 'cli-raw-85',
                                        'source': base64.b64encode(EVAL_SOURCE).decode()})
        assert eval_parsed['accepted'], eval_parsed
        eval_checked = adapter.request({'op': 'check', 'ast': eval_parsed['ast'], 'fixture': True})
    finally:
        frontend.close()
        adapter.close()
    initial = '$php_run(' + checked['fixture'] + ', 300, ' + json.dumps(
        base64.b64encode(str(source_path).encode()).decode()) + ')'
    response = '(SOURCE_ACCEPT 1 (' + str(list(EVAL_SOURCE)) + ') ' + eval_checked['fixture'] + ')'
    checks = [
        'S = ' + initial,
        'S.COMPLETION = SOURCE_PENDING',
        'S_resume = $eval_resume(S, ' + response + ')',
        'S_resume.COMPLETION = NORMAL',
        'S_task = $class_seek(S_resume, 30)',
        'S_task.TODO = (EVAL (NExprClassConstFetch (NName (BYTES text_name) metadata_name) (NIdentifier (BYTES text_member) metadata_member) metadata)) :: ptask_tail*',
        '$ptlc($base64(text_name)) = $ptascii("self")',
        '$ptlc($base64(text_member)) = $ptascii("class")',
        '$method_source_task(S_task, NExprClassConstFetch (NName (BYTES text_name) metadata_name) (NIdentifier (BYTES text_member) metadata_member) metadata)',
        '$call_task_valid(S_task, EVAL (NExprClassConstFetch (NName (BYTES text_name) metadata_name) (NIdentifier (BYTES text_member) metadata_member) metadata))',
        '~$call_task_valid(S_task[.ORIGIN = eps], EVAL (NExprClassConstFetch (NName (BYTES text_name) metadata_name) (NIdentifier (BYTES text_member) metadata_member) metadata))',
        '~$call_task_valid(S_task[.ORIGIN = (PORIGIN 999 eps)], EVAL (NExprClassConstFetch (NName (BYTES text_name) metadata_name) (NIdentifier (BYTES text_member) metadata_member) metadata))',
        '$call_descriptors_valid(S_task)',
    ]
    fixture = out / 'protocol.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- if ' + condition + '\n' for condition in checks))
    command = [str(runner), *map(str, modules), str(fixture)]
    (out / 'command.json').write_text(json.dumps(command) + '\n')
    result = subprocess.run(command, capture_output=True, timeout=300)
    (out / 'stdout').write_bytes(result.stdout)
    (out / 'stderr').write_bytes(result.stderr)
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    passed = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
    report = {'result': 'pass' if passed else 'fail', 'assertions': len(checks),
              'inputs': before, 'source_sha256': digest(source_path),
              'fixture_sha256': digest(fixture), 'runner_exit_status': result.returncode,
              'scope': 'Checked eval AST; source-derived class constant task and forged origin guards.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('eval-class-scope', passed, len(checks), flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
