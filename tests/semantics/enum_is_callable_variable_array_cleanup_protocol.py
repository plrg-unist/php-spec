#!/usr/bin/env python3
"""Source-reached array receipt through a throwing output destructor."""
import hashlib
import json
import subprocess
import time

import enum_is_callable_saved_input_protocol as saved
import enum_is_callable_output_unique_protocol as unique

base = saved.base
ROOT, OUT, MODULES = saved.ROOT, saved.OUT, saved.MODULES
WATCHED = [ROOT / 'spec/semantics/modules.json',
           ROOT / 'tests/semantics/enum_is_callable_cases.json',
           ROOT / 'tests/semantics/enum_is_callable_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_output_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_saved_input_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_output_unique_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_variable_array_cleanup_protocol.py',
           ROOT / 'tests/semantics/profile.json',
           ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *MODULES]

if __name__ == '__main__':
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    row = base.CASES['enum-is-callable-third-output-variable-array-throw-destructor']
    checks = [
        'S_initial = ' + saved.checked(row, 'throw-array'),
        'S_initial.COMPLETION = BUDGET',
        'S_first = $eis_seek_first(S_initial, 4000)',
        '$eis_first(S_first)',
        'S_first.TODO = (CONFIG_SEND pconfigcall_first) :: ptask_tail*',
        '$enum_is_callable_capture(S_first, pconfigcall_first) = (penumqueryinput)',
        'penumqueryinput.ARRAY = (n_array)',
        'penumqueryinput.VALUE = $ptascii("FirstCheck::from")',
        '$enum_is_callable_input_source(S_first, penumqueryinput)',
        'S_cap = $drive_steps(S_first[.COMPLETION = NORMAL], 1)',
        'S_cap.TODO = (CONFIG_ARGS pconfigcall_cap) :: (ENUM_IS_CALLABLE_INPUT penumqueryinput) :: ptask_tail*',
        'pconfigcall_cap.SENT = [NAMED_SENT (KNOWN (PARRAY n_array))]',
        'S_send = $eis_seek(S_cap, pconfigcall_first.SITE, 2, 7000)',
        'S_send.TODO = (CONFIG_SEND pconfigcall_send) :: (ENUM_IS_CALLABLE_INPUT penumqueryinput) :: ptask_tail*',
        'pconfigcall_send.SENT = [NAMED_SENT (KNOWN (PARRAY n_array)), NAMED_SENT (KNOWN (PBOOL false))]',
        '$enum_is_callable_saved(S_send, pconfigcall_send, PARRAY n_array) = (penumqueryinput)',
        '$enum_is_callable_ref_name(S_send, pconfigcall_send, PARRAY n_array) = (penumqueryinput.VALUE)',
        'S_ref = $drive_steps(S_send[.COMPLETION = NORMAL], 1)',
        'S_ref.TODO = (CONFIG_ARGS pconfigcall_ref) :: (ENUM_IS_CALLABLE_INPUT penumqueryinput) :: ptask_tail*',
        'pconfigcall_ref.SENT = [NAMED_SENT (KNOWN (PARRAY n_array)), NAMED_SENT (KNOWN (PBOOL false)), NAMED_SENT (REFERENCE n_output)]',
        'S_invoke = $eic_seek(S_ref, 0, 3000)',
        '$eic_front(S_invoke)',
        'S_invoke.TODO = (CONFIG_INVOKE pconfigcall_invoke) :: (ENUM_IS_CALLABLE_INPUT penumqueryinput) :: ptask_tail*',
        'pconfigcall_invoke.SENT = pconfigcall_ref.SENT',
        '$config_invoke_valid(S_invoke, pconfigcall_invoke)',
        '$enum_is_callable_output_capture(S_invoke, pconfigcall_invoke) = (penumqueryoutput)',
        'penumqueryoutput.INPUT = (penumqueryinput)',
        'penumqueryoutput.CELL = n_output',
        'penumqueryoutput.NAME = penumqueryinput.VALUE',
        '$task_nodes(ENUM_IS_CALLABLE_OUTPUT penumqueryoutput) = [HARRAY n_array, HCELL n_output]',
        '$enum_is_callable_output_valid(S_invoke, penumqueryoutput)',
        'S_clear = $drive_steps(S_invoke[.COMPLETION = NORMAL], 1)',
        'S_clear.STORE[n_output] = DEFINED PNULL',
        'S_clear.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_initial) :: (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput) :: ptask_tail*',
        'pdestructionoperation_initial.SOURCE = ENUM_IS_CALLABLE_CLEAR penumqueryoutput',
        '$eager_operation_source_guard(S_clear, pdestructionoperation_initial)',
        'S_entry = $eiu_seek(S_clear, penumqueryoutput, true, 3000)',
        '$eiu_entry(S_entry, penumqueryoutput)',
        'S_entry.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_entry_tail*',
        'pdestructorcall.OBJECT = penumqueryoutput.OLD',
        'S_entry.STORE[n_output] = DEFINED PNULL',
        'S_exit = $eiu_seek(S_entry, penumqueryoutput, false, 7000)',
        '$eiu_exit(S_exit, penumqueryoutput)',
        'S_exit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput) :: ptask_tail*',
        'pdestructionoperation.PENDING = (n_exception)',
        '$throwable_live(S_exit, n_exception)',
        '$string_bytes($throwable_field(S_exit, n_exception, "message")) = ($ptascii("drop"))',
        '$lookup(S_exit.ENV, $ptascii("call")) = (n_call_cell)',
        'S_exit.STORE[n_call_cell] = DEFINED (PARRAY n_rebound)',
        'n_rebound =/= n_array',
        '$enum_is_callable_variable_array_name(S_exit, PARRAY n_rebound) = ($ptascii("OtherCheck::tryFrom"))',
        '$task_nodes(ENUM_IS_CALLABLE_OUTPUT penumqueryoutput) = [HARRAY n_array, HCELL n_output]',
        '$($heap_owners($heap_graph(S_exit), HARRAY n_array) > 0)',
        '$enum_is_callable_output_valid(S_exit, penumqueryoutput)',
        'penumqueryinput_forged = penumqueryinput[.ARRAY = (n_rebound)][.VALUE = $ptascii("OtherCheck::tryFrom")]',
        'penumqueryoutput_forged = penumqueryoutput[.INPUT = (penumqueryinput_forged)]',
        '~$enum_is_callable_output_valid(S_exit, penumqueryoutput_forged)',
        'S_atomic = $drive_steps(S_exit[.COMPLETION = NORMAL], 1)',
        'S_atomic.STORE[n_output] = DEFINED (PSTRING penumqueryoutput.NAME)',
        'S_atomic.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        'S_atomic.RESULT = KNOWN PNULL',
        'S_zero = $drive_steps(S_exit[.COMPLETION = NORMAL], 0)',
        'S_zero.COMPLETION = BUDGET',
        '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = S_atomic',
        'S_done = $drive(S_atomic[.COMPLETION = NORMAL], 10000)',
        'S_done.COMPLETION = NORMAL',
        '$eic_output(S_done.EVENTS) = $ptascii(' + json.dumps(row['expected_normal_stdout']) + ')',
        '$lookup(S_done.ENV, $ptascii("ok")) = (n_ok)',
        'S_done.STORE[n_ok] = DEFINED pvalue_ok',
        '$string_bytes(pvalue_ok) = ($ptascii("UNCHANGED"))',
    ]
    fixture = OUT / 'variable-array-cleanup.watsup'
    fixture.write_text(base.PREFIX + saved.PREFIX + unique.PREFIX
                       + '\ndec $main() : bool\ndef $main() = true\n'
                       + ''.join('  -- if ' + check + '\n' for check in checks))
    command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
               *map(str, MODULES), str(fixture)]
    (OUT / 'command.json').write_text(json.dumps(command) + '\n')
    start = time.monotonic()
    timed_out = False
    try:
        result = subprocess.run(command, capture_output=True, timeout=240)
    except subprocess.TimeoutExpired as error:
        timed_out = True
        result = subprocess.CompletedProcess(command, 124, error.stdout or b'', error.stderr or b'')
    (OUT / 'stdout').write_bytes(result.stdout)
    (OUT / 'stderr').write_bytes(result.stderr)
    record = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'checks': len(checks), 'exit': result.returncode,
              'timeout_seconds': 240, 'timed_out': timed_out, 'elapsed': time.monotonic() - start,
              'stdout': result.stdout.decode(errors='replace'),
              'stderr': result.stderr.decode(errors='replace'),
              'stable': before == {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                  for path in WATCHED}, 'direct_inputs': before}
    (OUT / 'report.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: record[k] for k in ['revision', 'checks', 'exit', 'timed_out', 'stdout', 'stderr', 'stable']}), OUT, flush=True)
    assert result.returncode == 0 and not timed_out and result.stdout == b'true\n' and not result.stderr and record['stable'], OUT
