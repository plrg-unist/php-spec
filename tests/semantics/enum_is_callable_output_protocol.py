#!/usr/bin/env python3
"""Source-reached caller-CV output for a literal generated enum method."""
import hashlib
import json
import subprocess

import enum_is_callable_protocol as base

ROOT = base.ROOT
OUT = base.OUT
MODULES = base.MODULES
WATCHED = [ROOT / 'spec/semantics/modules.json',
           ROOT / 'tests/semantics/enum_is_callable_cases.json',
           ROOT / 'tests/semantics/enum_is_callable_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_output_protocol.py',
           ROOT / 'tests/semantics/profile.json',
           ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *MODULES]

SEND_PREFIX = r'''
dec $eio_front(pstate) : bool
def $eio_front(S) = true
  -- if S.TODO = (CONFIG_SEND pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_IS_CALLABLE
  -- if pconfigcall.INDEX = 2
  -- if $enum_is_callable_ref_argument(S, pconfigcall)
def $eio_front(S) = false -- otherwise
dec $eio_seek(pstate, nat) : pstate
def $eio_seek(S, 0) = S
def $eio_seek(S, n) = S
  -- if $(n > 0) /\ $eio_front(S)
def $eio_seek(S, n) = $eio_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if $(n > 0) /\ ~$eio_front(S)
'''


if __name__ == '__main__':
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    row = base.CASES['enum-is-callable-third-output-cv']
    checks = [
        'S_initial = ' + base.checked_source(row),
        'S_initial.COMPLETION = BUDGET',
        'S_send = $eio_seek(S_initial, 2000)',
        '$eio_front(S_send)',
        'S_send.TODO = (CONFIG_SEND pconfigcall_send) :: ptask_send_tail*',
        'pconfigcall_send.SENT = [NAMED_SENT (KNOWN pvalue_input), NAMED_SENT (KNOWN (PBOOL false))]',
        '$intrinsic_argument(S_send, pconfigcall_send.SITE, 2) = ((NExprVariable (BYTES text_output) metadata_output, false, eps, porigin_output, z_output))',
        '$reference_cv(NExprVariable (BYTES text_output) metadata_output) = (n_name*)',
        'S_send.RESULT = VARIABLE n_name* z_variable',
        '$lookup(S_send.ENV, n_name*) = (n_cell)',
        '(HCELL n_cell) <- S_send.ALLOCATIONS',
        'S_send.STORE[n_cell] = DEFINED pvalue_old',
        '$string_bytes(pvalue_old) = ($ptascii("before"))',
        '$propref_at(S_send.PROPREFS, n_cell) = eps',
        '$reference_coercion_at(S_send.REFCOERCIONS, n_cell) = eps',
        '$enum_is_callable_ref_cell(S_send, pconfigcall_send, pvalue_input) = (n_cell)',
        '$call_task_valid(S_send, CONFIG_SEND pconfigcall_send)',
        'S_ref = $drive_steps(S_send[.COMPLETION = NORMAL], 1)',
        'S_ref.TODO = (CONFIG_ARGS pconfigcall_ref) :: ptask_send_tail*',
        'pconfigcall_ref.INDEX = 3',
        'pconfigcall_ref.SENT = [NAMED_SENT (KNOWN pvalue_input), NAMED_SENT (KNOWN (PBOOL false)), NAMED_SENT (REFERENCE n_cell)]',
        'n_cell <- S_ref.REFCELLS',
        'S_ref.STORE[n_cell] = S_send.STORE[n_cell]',
        '$config_call_valid(S_ref, pconfigcall_ref)',
        'S_invoke = $eic_seek(S_ref, 0, 2000)',
        '$eic_front(S_invoke)',
        'S_invoke.TODO = (CONFIG_INVOKE pconfigcall_invoke) :: ptask_invoke_tail*',
        'pconfigcall_invoke.SENT = pconfigcall_ref.SENT',
        '$enum_is_callable_ref_slots_valid(S_invoke, pconfigcall_invoke)',
        '$config_invoke_valid(S_invoke, pconfigcall_invoke)',
        'n_forged = |S_invoke.STORE|',
        '~$enum_is_callable_ref_slots_valid(S_invoke, pconfigcall_invoke[.SENT = [NAMED_SENT (KNOWN pvalue_input), NAMED_SENT (KNOWN (PBOOL false)), NAMED_SENT (REFERENCE n_forged)]])',
        'S_unbound = S_invoke[.ENV = $unbind(S_invoke.ENV, n_name*)]',
        '~$enum_is_callable_ref_slots_valid(S_unbound, pconfigcall_invoke)',
        'S_written = $drive_steps(S_invoke[.COMPLETION = NORMAL], 1)',
        'S_written.STORE[n_cell] = DEFINED (PSTRING $ptascii("NameCheck::from"))',
        'S_written.RESULT = KNOWN (PBOOL true)',
        'S_written.TODO = ptask_invoke_tail*',
        'S_written.EVENTS = S_invoke.EVENTS',
        'S_written.CLASSCONSTANTCACHE = S_invoke.CLASSCONSTANTCACHE',
        'S_zero = $drive_steps(S_written, 0)',
        'S_zero.COMPLETION = BUDGET',
        'S_done = $drive(S_zero[.COMPLETION = NORMAL], 5000)',
        'S_done.COMPLETION = NORMAL',
        '$eic_output(S_done.EVENTS) = $ptascii("' + row['expected_normal_stdout'] + '")',
    ]
    fixture = OUT / 'output-cv.watsup'
    fixture.write_text(base.PREFIX + SEND_PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                       + ''.join('  -- if ' + check + '\n' for check in checks))
    command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
               *map(str, MODULES), str(fixture)]
    result = subprocess.run(command, capture_output=True, timeout=120)
    (OUT / 'command.json').write_text(json.dumps(command) + '\n')
    (OUT / 'stdout').write_bytes(result.stdout)
    (OUT / 'stderr').write_bytes(result.stderr)
    record = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'checks': len(checks), 'exit': result.returncode,
              'stdout': result.stdout.decode(errors='replace'),
              'stderr': result.stderr.decode(errors='replace'),
              'stable': before == {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                   for path in WATCHED}, 'direct_inputs': before}
    (OUT / 'report.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: record[k] for k in ['revision', 'checks', 'exit', 'stdout', 'stderr', 'stable']}), OUT, flush=True)
    assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr and record['stable'], OUT
