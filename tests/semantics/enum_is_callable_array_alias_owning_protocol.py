#!/usr/bin/env python3
"""Source-reached owning rebound arrays in enum callable output."""
import argparse
import hashlib
import json
import subprocess
import time

import enum_is_callable_variable_array_protocol as variable
import enum_is_callable_output_unique_protocol as unique

saved = variable.saved
base = variable.base
ROOT, OUT, MODULES = variable.ROOT, variable.OUT, variable.MODULES
WATCHED = [ROOT / 'spec/semantics/modules.json',
           ROOT / 'tests/semantics/enum_is_callable_cases.json',
           ROOT / 'tests/semantics/enum_is_callable_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_output_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_saved_input_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_variable_array_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_output_unique_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_array_alias_owning_protocol.py',
           ROOT / 'tests/semantics/profile.json',
           ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *MODULES]


def owner(label, suffix):
    row, checks = variable.begin(label, 'alias-owning-' + suffix, 'FirstCheck::from')
    checks += variable.send(label)
    checks += [
        f'$lookup(S_{label}_send.ENV, $ptascii("call")) = (n_{label}_output)',
        f'$lookup(S_{label}_send.ENV, $ptascii("name")) = (n_{label}_output)',
        f'S_{label}_send.STORE[n_{label}_output] = DEFINED (PARRAY n_{label}_old)',
        f'n_{label}_old =/= n_{label}_array',
        f'$enum_is_callable_rebound_array_child(S_{label}_send, n_{label}_output) = ((n_{label}_old, n_{label}_child))',
        f'S_{label}_send.ARRAYS[n_{label}_old].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_{label}_child)), ENTRY (KINT 1) (DIRECT pvalue_{label}_method)]',
        f'$string_bytes(pvalue_{label}_method) = ($ptascii("tryFrom"))',
        f'$enum_is_callable_ref_array_alias_old(S_{label}_send, pconfigcall_{label}_send, n_{label}_output, PARRAY n_{label}_old, penumqueryinput_{label}.VALUE, pconfigcall_{label}_send.LINE)',
        f'S_{label}_ref = $drive_steps(S_{label}_send[.COMPLETION = NORMAL], 1)',
        f'S_{label}_ref.TODO = (CONFIG_ARGS pconfigcall_{label}_ref) :: (ENUM_IS_CALLABLE_INPUT penumqueryinput_{label}) :: ptask_{label}_tail*',
        f'pconfigcall_{label}_ref.SENT = [NAMED_SENT (KNOWN (PARRAY n_{label}_array)), NAMED_SENT (KNOWN (PBOOL false)), NAMED_SENT (REFERENCE n_{label}_output)]',
        f'S_{label}_invoke = $eis_seek(S_{label}_ref, pconfigcall_{label}_first.SITE, 3, 3000)',
        f'$eis_site(S_{label}_invoke, pconfigcall_{label}_first.SITE, 3)',
        f'S_{label}_invoke.TODO = (CONFIG_INVOKE pconfigcall_{label}_invoke) :: (ENUM_IS_CALLABLE_INPUT penumqueryinput_{label}) :: ptask_{label}_tail*',
        f'$config_invoke_valid(S_{label}_invoke, pconfigcall_{label}_invoke)',
        f'$enum_is_callable_ref_array_alias_old(S_{label}_invoke, pconfigcall_{label}_invoke, n_{label}_output, PARRAY n_{label}_old, penumqueryinput_{label}.VALUE, pconfigcall_{label}_invoke.LINE)',
    ]
    return row, checks


def retained():
    row, checks = owner('retained', 'retained-owner')
    checks += [
        '$lookup(S_retained_invoke.ENV, $ptascii("hold")) = (n_hold)',
        'n_hold =/= n_retained_output',
        'S_retained_invoke.STORE[n_hold] = DEFINED (PARRAY n_retained_old)',
        '$($heap_owners($heap_graph(S_retained_invoke), HARRAY n_retained_old) > 1)',
        '~$enum_is_callable_ref_last(S_retained_invoke, n_retained_output, pconfigcall_retained_invoke.LINE)',
        '$enum_is_callable_output_capture(S_retained_invoke, pconfigcall_retained_invoke) = eps',
        'S_retained_write = $write_cell_checked(S_retained_invoke[.COMPLETION = NORMAL], n_retained_output, PSTRING penumqueryinput_retained.VALUE, pconfigcall_retained_invoke.LINE)',
        'S_retained_write.COMPLETION = NORMAL',
        '$($heap_owners($heap_graph(S_retained_write), HARRAY n_retained_old) > 0)',
        '$($heap_owners($heap_graph(S_retained_write), HOBJECT n_retained_child) > 0)',
        'S_retained_after = $drive_steps(S_retained_invoke[.COMPLETION = NORMAL], 1)',
        'S_retained_after.COMPLETION = BUDGET',
        'S_retained_after.STORE[n_retained_output] = DEFINED (PSTRING penumqueryinput_retained.VALUE)',
        'S_retained_after.STORE[n_hold] = DEFINED (PARRAY n_retained_old)',
        '$($heap_owners($heap_graph(S_retained_after), HARRAY n_retained_old) > 0)',
        '$($heap_owners($heap_graph(S_retained_after), HOBJECT n_retained_child) > 0)',
        'S_retained_done = $drive(S_retained_after[.COMPLETION = NORMAL], 10000)',
        'S_retained_done.COMPLETION = NORMAL',
        '$eic_output(S_retained_done.EVENTS) = $ptascii(' + json.dumps(row['expected_normal_stdout']) + ')',
    ]
    return checks


def thrown():
    row, checks = owner('thrown', 'throwing-child')
    checks += [
        '$enum_is_callable_ref_last(S_thrown_invoke, n_thrown_output, pconfigcall_thrown_invoke.LINE)',
        '$enum_is_callable_output_capture(S_thrown_invoke, pconfigcall_thrown_invoke) = (penumqueryoutput)',
        'penumqueryoutput.OLDARRAY = (n_thrown_old)',
        'penumqueryoutput.OLD = n_thrown_child',
        'penumqueryoutput.NAME = penumqueryinput_thrown.VALUE',
        '$enum_is_callable_output_valid(S_thrown_invoke, penumqueryoutput)',
        'penumqueryoutput_forged = penumqueryoutput[.OLDARRAY = (n_thrown_array)]',
        '~$enum_is_callable_output_valid(S_thrown_invoke, penumqueryoutput_forged)',
        '$lookup(S_thrown_invoke.ENV, $ptascii("ok")) = (n_thrown_ok)',
        'S_thrown_invoke.STORE[n_thrown_ok] = DEFINED pvalue_thrown_ok',
        '$string_bytes(pvalue_thrown_ok) = ($ptascii("UNCHANGED"))',
        'S_thrown_invoke.ARRAYS[n_thrown_old] = parray_thrown_old',
        'n_thrown_after = $(n_thrown_old + 1)',
        'n_thrown_remaining = $nabs($(|S_thrown_invoke.ARRAYS| - n_thrown_after))',
        'parray_thrown_alias = parray_thrown_old[.ITEMS = [ENTRY (KINT 0) (ALIAS n_thrown_ok), ENTRY (KINT 1) (DIRECT pvalue_thrown_method)]]',
        'S_thrown_alias = S_thrown_invoke[.ARRAYS = S_thrown_invoke.ARRAYS[0:n_thrown_old] ++ [parray_thrown_alias] ++ S_thrown_invoke.ARRAYS[n_thrown_after:n_thrown_remaining]]',
        '$enum_is_callable_rebound_array_child(S_thrown_alias, n_thrown_output) = eps',
        '~$enum_is_callable_ref_last(S_thrown_alias, n_thrown_output, pconfigcall_thrown_invoke.LINE)',
        '$enum_is_callable_ref_array_alias_old(S_thrown_alias, pconfigcall_thrown_invoke, n_thrown_output, PARRAY n_thrown_old, penumqueryinput_thrown.VALUE, pconfigcall_thrown_invoke.LINE) = false',
        'S_thrown_clear = $drive_steps(S_thrown_invoke[.COMPLETION = NORMAL], 1)',
        'S_thrown_clear.STORE[n_thrown_output] = DEFINED PNULL',
        'S_thrown_clear.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_initial) :: (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput) :: ptask_thrown_tail*',
        'pdestructionoperation_initial.SOURCE = ENUM_IS_CALLABLE_CLEAR penumqueryoutput',
        '$eager_operation_source_guard(S_thrown_clear, pdestructionoperation_initial)',
        'S_thrown_entry = $eiu_seek(S_thrown_clear, penumqueryoutput, true, 3000)',
        '$eiu_entry(S_thrown_entry, penumqueryoutput)',
        'S_thrown_entry.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_thrown_entry_tail*',
        'pdestructorcall.OBJECT = n_thrown_child',
        'S_thrown_entry.STORE[n_thrown_output] = DEFINED PNULL',
        'S_thrown_exit = $eiu_seek(S_thrown_entry, penumqueryoutput, false, 7000)',
        '$eiu_exit(S_thrown_exit, penumqueryoutput)',
        'S_thrown_exit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput) :: ptask_thrown_tail*',
        'pdestructionoperation.PENDING = (n_exception)',
        '$throwable_live(S_thrown_exit, n_exception)',
        '$string_bytes($throwable_field(S_thrown_exit, n_exception, "message")) = ($ptascii("drop"))',
        '$enum_is_callable_output_valid(S_thrown_exit, penumqueryoutput)',
        '~$enum_is_callable_output_valid(S_thrown_exit, penumqueryoutput_forged)',
        '$eic_output(S_thrown_exit.EVENTS) = $ptascii("REBIND|D-null|")',
        'S_thrown_atomic = $drive_steps(S_thrown_exit[.COMPLETION = NORMAL], 1)',
        'S_thrown_atomic.STORE[n_thrown_output] = DEFINED (PSTRING penumqueryoutput.NAME)',
        'S_thrown_atomic.STORE[n_thrown_ok] = S_thrown_invoke.STORE[n_thrown_ok]',
        'S_thrown_atomic.TODO = (THROW_SEARCH n_exception) :: ptask_thrown_tail*',
        'S_thrown_atomic.RESULT = KNOWN PNULL',
        'S_thrown_zero = $drive_steps(S_thrown_exit[.COMPLETION = NORMAL], 0)',
        'S_thrown_zero.COMPLETION = BUDGET',
        '$drive_steps(S_thrown_zero[.COMPLETION = NORMAL], 1) = S_thrown_atomic',
    ]
    return checks


if __name__ == '__main__':
    groups = {'retained': retained, 'throw': thrown}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=[*groups], required=True)
    args = parser.parse_args()
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    checks = groups[args.group]()
    fixture = OUT / 'array-alias-owning.watsup'
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
              'group': args.group, 'checks': len(checks), 'exit': result.returncode,
              'timeout_seconds': 240, 'timed_out': timed_out,
              'elapsed': time.monotonic() - start,
              'stdout': result.stdout.decode(errors='replace'),
              'stderr': result.stderr.decode(errors='replace'),
              'stable': before == {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                  for path in WATCHED}, 'direct_inputs': before}
    (OUT / 'report.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: record[k] for k in ['revision', 'group', 'checks', 'exit', 'timed_out', 'stdout', 'stderr', 'stable']}), OUT, flush=True)
    assert result.returncode == 0 and not timed_out and result.stdout == b'true\n' and not result.stderr and record['stable'], OUT
