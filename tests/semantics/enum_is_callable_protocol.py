#!/usr/bin/env python3
"""Source-reached published enum is_callable query guards."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(tempfile.mkdtemp(prefix='enum-is-callable-protocol-', dir=ROOT / '.tools'))
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import request_environment as request
from recorded_worker import Worker

CASES = {row['id']: row for row in json.loads((ROOT / 'tests/semantics/enum_is_callable_cases.json').read_text())}
MODULES = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
WATCHED = [ROOT / 'spec/semantics/modules.json', ROOT / 'tests/semantics/enum_is_callable_cases.json',
           ROOT / 'tests/semantics/enum_is_callable_protocol.py', ROOT / 'tests/semantics/profile.json',
           ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *MODULES]
PREFIX = r'''
dec $eic_front(pstate) : bool
def $eic_front(S) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_IS_CALLABLE
def $eic_front(S) = false -- otherwise
dec $eic_seek(pstate, nat, nat) : pstate
def $eic_seek(S, n_query, 0) = S
def $eic_seek(S, 0, n) = S
  -- if $(n > 0) /\ $eic_front(S)
def $eic_seek(S, n_query, n) = $eic_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n_query - 1)), $nabs($(n - 1)))
  -- if $(n > 0) /\ $(n_query > 0) /\ $eic_front(S)
def $eic_seek(S, n_query, n) = $eic_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_query, $nabs($(n - 1)))
  -- if $(n > 0) /\ ~$eic_front(S)
dec $eic_output_item(pevent) : ptbytes
def $eic_output_item(OUTPUT n*) = n*
def $eic_output_item(pevent) = eps -- otherwise
dec $eic_output(pevent*) : ptbytes
def $eic_output(eps) = eps
def $eic_output(pevent :: pevent_tail*) = $eic_output_item(pevent) ++ $eic_output(pevent_tail*)
'''


def checked_source(row):
    source = OUT / 'source.php'
    source.write_bytes(row['source'].encode())
    assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256']
    frontend = adapter = None
    try:
        frontend = Worker([str(request.t.PHP), '-n', *request.t.FLAGS, '-d',
                           'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], OUT / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], OUT / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': request.b64(source.read_bytes())})
        assert parsed['ok'] and parsed['accepted']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok']
    finally:
        if frontend:
            frontend.close()
        if adapter:
            adapter.close()
    return '$php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')'


if __name__ == '__main__':
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    row = CASES['enum-is-callable-published-prefix']
    checks = [
        'S_initial = ' + checked_source(row),
        'S_initial.COMPLETION = BUDGET',
        'S_first = $eic_seek(S_initial, 0, 2000)',
        '$eic_front(S_first)',
        'S_first.TODO = (CONFIG_INVOKE pconfigcall_first) :: ptask_first_tail*',
        'pconfigcall_first.SENT = [NAMED_SENT (KNOWN pvalue_first)]',
        '$string_bytes(pvalue_first) = ($ptascii("ImmediateInt::from"))',
        '$config_invoke_valid(S_first, pconfigcall_first)',
        '$enum_is_callable_result(S_first, pvalue_first, false) = (true)',
        'S_first_after = $drive_steps(S_first[.COMPLETION = NORMAL], 1)',
        'S_first_after.RESULT = KNOWN (PBOOL true)',
        'S_first_after.CLASSCONSTANTCACHE = S_first.CLASSCONSTANTCACHE',
        'S_case = $eic_seek(S_first_after, 1, 2000)',
        '$eic_front(S_case)',
        'S_case.TODO = (CONFIG_INVOKE pconfigcall_case) :: ptask_case_tail*',
        'pconfigcall_case.SENT = [NAMED_SENT (KNOWN (PARRAY n_case_array))]',
        '$enum_is_callable_target(S_case, PARRAY n_case_array) = ((porigin_case_class, ptbytes_method, true))',
        'ptbytes_method = $ptascii("from")',
        'S_case.ARRAYS[n_case_array] = parray_case',
        '$entry_lookup(parray_case.ITEMS, KINT 0) = (pitem_receiver)',
        '$entry_value(S_case, pitem_receiver) = POBJECT n_case',
        '(HOBJECT n_case) <- S_case.ALLOCATIONS',
        '$enum_is_callable_receiver(S_case[.ALLOCATIONS = eps], POBJECT n_case) = eps',
        '$config_invoke_valid(S_case, pconfigcall_case)',
        'S_case_after = $drive_steps(S_case[.COMPLETION = NORMAL], 1)',
        'S_case_after.RESULT = KNOWN (PBOOL true)',
        'S_case_after.CLASSCONSTANTCACHE = S_case.CLASSCONSTANTCACHE',
        'S_negative = $eic_seek(S_case_after, 1, 2000)',
        '$eic_front(S_negative)',
        'S_negative.TODO = (CONFIG_INVOKE pconfigcall_negative) :: ptask_negative_tail*',
        'pconfigcall_negative.SENT = [NAMED_SENT (KNOWN pvalue_negative)]',
        '$string_bytes(pvalue_negative) = ($ptascii("ImmediatePure::from"))',
        '$enum_is_callable_target(S_negative, pvalue_negative) = ((porigin_pure, ptbytes_negative, false))',
        '$enum_generated_kind(S_negative, porigin_pure, ptbytes_negative) = eps',
        '$effective_method(S_negative, porigin_pure, ptbytes_negative, |S_negative.CLASSES|) = eps',
        '~$array_magic(S_negative, porigin_pure)',
        '$config_invoke_valid(S_negative, pconfigcall_negative)',
        '$enum_is_callable_result(S_negative, pvalue_negative, false) = (false)',
        'S_zero = $drive_steps(S_negative, 0)',
        'S_zero.COMPLETION = BUDGET',
        'S_done = $drive(S_zero[.COMPLETION = NORMAL], 5000)',
        'S_done.COMPLETION = NORMAL',
        '$eic_output(S_done.EVENTS) = $ptascii("' + row['expected_normal_stdout'] + '")',
    ]
    fixture = OUT / 'main.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                       + ''.join('  -- if ' + check + '\n' for check in checks))
    command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
               *map(str, MODULES), str(fixture)]
    result = subprocess.run(command, capture_output=True, timeout=120)
    (OUT / 'command.json').write_text(json.dumps(command) + '\n')
    (OUT / 'stdout').write_bytes(result.stdout)
    (OUT / 'stderr').write_bytes(result.stderr)
    record = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'checks': len(checks), 'exit': result.returncode,
              'stdout': result.stdout.decode(errors='replace'), 'stderr': result.stderr.decode(errors='replace'),
              'stable': before == {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                   for path in WATCHED}, 'direct_inputs': before}
    (OUT / 'report.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: record[k] for k in ['revision', 'checks', 'exit', 'stdout', 'stderr', 'stable']}), OUT, flush=True)
    assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr and record['stable'], OUT
