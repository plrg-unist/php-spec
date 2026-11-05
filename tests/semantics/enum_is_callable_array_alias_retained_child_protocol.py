#!/usr/bin/env python3
"""Source-reached enum output after its rebound array loses an object child."""
import argparse
import hashlib
import json
import subprocess
import time

import enum_is_callable_variable_array_protocol as variable

saved = variable.saved
base = variable.base
ROOT, OUT, MODULES = variable.ROOT, variable.OUT, variable.MODULES
WATCHED = [ROOT / 'spec/semantics/modules.json',
           ROOT / 'tests/semantics/enum_is_callable_cases.json',
           ROOT / 'tests/semantics/enum_is_callable_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_output_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_saved_input_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_variable_array_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_array_alias_retained_child_protocol.py',
           ROOT / 'tests/semantics/profile.json',
           ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *MODULES]


def before_output(label, suffix):
    row, checks = variable.begin(label, 'alias-retained-child-' + suffix, 'FirstCheck::from')
    checks += variable.send(label)
    checks += [
        f'$lookup(S_{label}_send.ENV, $ptascii("call")) = (n_{label}_output)',
        f'$lookup(S_{label}_send.ENV, $ptascii("name")) = (n_{label}_output)',
        f'S_{label}_send.STORE[n_{label}_output] = DEFINED (PARRAY n_{label}_old)',
        f'n_{label}_old =/= n_{label}_array',
        f'$enum_is_callable_rebound_array_child(S_{label}_send, n_{label}_output) = ((n_{label}_old, n_{label}_child))',
        f'$lookup(S_{label}_send.ENV, $ptascii("holdChild")) = (n_{label}_holder)',
        f'n_{label}_holder =/= n_{label}_output',
        f'$enum_is_callable_ref_array_alias_old(S_{label}_send, pconfigcall_{label}_send, n_{label}_output, PARRAY n_{label}_old, penumqueryinput_{label}.VALUE, pconfigcall_{label}_send.LINE)',
        f'S_{label}_ref = $drive_steps(S_{label}_send[.COMPLETION = NORMAL], 1)',
        f'S_{label}_ref.TODO = (CONFIG_ARGS pconfigcall_{label}_ref) :: (ENUM_IS_CALLABLE_INPUT penumqueryinput_{label}) :: ptask_{label}_tail*',
        f'pconfigcall_{label}_ref.SENT = [NAMED_SENT (KNOWN (PARRAY n_{label}_array)), NAMED_SENT (KNOWN (PBOOL false)), NAMED_SENT (REFERENCE n_{label}_output)]',
        f'S_{label}_invoke = $eis_seek(S_{label}_ref, pconfigcall_{label}_first.SITE, 3, 3000)',
        f'$eis_site(S_{label}_invoke, pconfigcall_{label}_first.SITE, 3)',
        f'S_{label}_invoke.TODO = (CONFIG_INVOKE pconfigcall_{label}_invoke) :: (ENUM_IS_CALLABLE_INPUT penumqueryinput_{label}) :: ptask_{label}_tail*',
        f'$config_invoke_valid(S_{label}_invoke, pconfigcall_{label}_invoke)',
    ]
    return row, checks


def held():
    row, checks = before_output('held', 'held')
    checks += [
        'S_held_send.STORE[n_held_holder] = DEFINED (POBJECT n_held_child)',
        '~$enum_is_callable_ref_last(S_held_invoke, n_held_output, pconfigcall_held_invoke.LINE)',
        '$enum_is_callable_output_capture(S_held_invoke, pconfigcall_held_invoke) = eps',
        'S_held_write = $write_cell_checked(S_held_invoke[.COMPLETION = NORMAL], n_held_output, PSTRING penumqueryinput_held.VALUE, pconfigcall_held_invoke.LINE)',
        'S_held_write.COMPLETION = NORMAL',
        '$heap_owners($heap_graph(S_held_write), HARRAY n_held_old) = 0',
        '$heap_owners($heap_graph(S_held_write), HOBJECT n_held_child) = 2',
        '(HOBJECT n_held_child) <- $heap_prune($heap_graph(S_held_write)).NODES',
        '~((HARRAY n_held_old) <- $gc_prune_nodes(S_held_write))',
        '$enum_is_callable_rebound_array_old_valid(S_held_invoke, S_held_write, n_held_output, n_held_old, pconfigcall_held_invoke.LINE)',
        '$lookup(S_held_invoke.ENV, $ptascii("ok")) = (n_held_ok)',
        'S_held_invoke.STORE[n_held_ok] = DEFINED pvalue_held_ok',
        '$string_bytes(pvalue_held_ok) = ($ptascii("UNCHANGED"))',
        'S_held_holderless = S_held_invoke[.STORE = $set_cell(S_held_invoke.STORE, n_held_holder, DEFINED PNULL)]',
        'n_fake = |S_held_holderless.ARRAYS|',
        'S_held_holderless.ARRAYS[n_held_old] = parray_fake',
        'S_held_forged = S_held_holderless[.ARRAYS = S_held_holderless.ARRAYS ++ [parray_fake]][.ALLOCATIONS = S_held_holderless.ALLOCATIONS ++ [HARRAY n_fake]]',
        'S_held_forged_write = $write_cell_checked(S_held_forged[.COMPLETION = NORMAL], n_held_output, PSTRING penumqueryinput_held.VALUE, pconfigcall_held_invoke.LINE)',
        'S_held_forged_write.COMPLETION = NORMAL',
        '$heap_owners($heap_graph(S_held_forged_write), HARRAY n_held_old) = 0',
        '$heap_owners($heap_graph(S_held_forged_write), HOBJECT n_held_child) = 2',
        '~((HOBJECT n_held_child) <- $heap_prune($heap_graph(S_held_forged_write)).NODES)',
        '~$enum_is_callable_rebound_array_old_valid(S_held_forged, S_held_forged_write, n_held_output, n_held_old, pconfigcall_held_invoke.LINE)',
        '$enum_is_callable_ref_array_alias_old(S_held_forged, pconfigcall_held_invoke, n_held_output, PARRAY n_held_old, penumqueryinput_held.VALUE, pconfigcall_held_invoke.LINE) = false',
        'S_held_after = $drive_steps(S_held_invoke[.COMPLETION = NORMAL], 1)',
        'S_held_after.COMPLETION = BUDGET',
        'S_held_after.STORE[n_held_output] = DEFINED (PSTRING penumqueryinput_held.VALUE)',
        'S_held_after.STORE[n_held_holder] = DEFINED (POBJECT n_held_child)',
        'S_held_after.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_held) :: ptask_held_after_tail*',
        '(HARRAY n_held_old) <- $destruction_job_nodes(pdestructionrelease_held.JOBS)',
        '$destructor_release_valid(S_held_after, pdestructionrelease_held)',
        '$heap_owners($heap_graph(S_held_after), HARRAY n_held_old) = 1',
        'S_held_done = $drive(S_held_after[.COMPLETION = NORMAL], 10000)',
        'S_held_done.COMPLETION = NORMAL',
        '$eic_output(S_held_done.EVENTS) = $ptascii(' + json.dumps(row['expected_normal_stdout']) + ')',
    ]
    return checks


def released():
    row, checks = before_output('released', 'preoutput-release')
    checks += [
        'S_released_send.STORE[n_released_holder] = DEFINED PNULL',
        '$enum_is_callable_ref_last(S_released_invoke, n_released_output, pconfigcall_released_invoke.LINE)',
        '$enum_is_callable_output_capture(S_released_invoke, pconfigcall_released_invoke) = (penumqueryoutput_released)',
        'penumqueryoutput_released.OLDARRAY = (n_released_old)',
        'penumqueryoutput_released.OLD = n_released_child',
        'penumqueryoutput_released.NAME = penumqueryinput_released.VALUE',
        '$enum_is_callable_output_valid(S_released_invoke, penumqueryoutput_released)',
        'S_released_clear = $drive_steps(S_released_invoke[.COMPLETION = NORMAL], 1)',
        'S_released_clear.STORE[n_released_output] = DEFINED PNULL',
        'S_released_clear.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_released) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_released) :: (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput_released) :: ptask_released_tail*',
        'pdestructionoperation_released.SOURCE = ENUM_IS_CALLABLE_CLEAR penumqueryoutput_released',
        '$eager_operation_source_guard(S_released_clear, pdestructionoperation_released)',
        'S_released_done = $drive(S_released_clear[.COMPLETION = NORMAL], 10000)',
        'S_released_done.COMPLETION = NORMAL',
        '$eic_output(S_released_done.EVENTS) = $ptascii(' + json.dumps(row['expected_normal_stdout']) + ')',
    ]
    return checks


if __name__ == '__main__':
    groups = {'held': held, 'released': released}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=[*groups], required=True)
    args = parser.parse_args()
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    checks = groups[args.group]()
    fixture = OUT / 'array-alias-retained-child.watsup'
    fixture.write_text(base.PREFIX + saved.PREFIX
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
