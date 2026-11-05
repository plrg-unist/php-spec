#!/usr/bin/env python3
"""Source-reached enum callable-name receipts for variable arrays."""
import argparse
import hashlib
import json
import subprocess
import time

import enum_is_callable_saved_input_protocol as saved

base = saved.base
ROOT, OUT, MODULES = saved.ROOT, saved.OUT, saved.MODULES
WATCHED = [ROOT / 'spec/semantics/modules.json',
           ROOT / 'tests/semantics/enum_is_callable_cases.json',
           ROOT / 'tests/semantics/enum_is_callable_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_output_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_saved_input_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_variable_array_protocol.py',
           ROOT / 'tests/semantics/profile.json',
           ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *MODULES]


def begin(label, suffix, name):
    row = base.CASES['enum-is-callable-third-output-variable-array-' + suffix]
    checks = [
        f'S_{label}_initial = ' + saved.checked(row, label),
        f'S_{label}_initial.COMPLETION = BUDGET',
        f'S_{label}_first = $eis_seek_first(S_{label}_initial, 4000)',
        f'$eis_first(S_{label}_first)',
        f'S_{label}_first.TODO = (CONFIG_SEND pconfigcall_{label}_first) :: ptask_{label}_tail*',
        f'pconfigcall_{label}_first.INDEX = 0 /\\ pconfigcall_{label}_first.SENT = eps',
        f'$enum_is_callable_capture(S_{label}_first, pconfigcall_{label}_first) = (penumqueryinput_{label})',
        f'penumqueryinput_{label}.ARRAY = (n_{label}_array)',
        f'penumqueryinput_{label}.VALUE = $ptascii({json.dumps(name)})',
        f'$enum_is_callable_variable_array_name(S_{label}_first, PARRAY n_{label}_array) = (penumqueryinput_{label}.VALUE)',
        f'$enum_is_callable_input_source(S_{label}_first, penumqueryinput_{label})',
        f'$task_nodes(ENUM_IS_CALLABLE_INPUT penumqueryinput_{label}) = eps',
        f'S_{label}_cap = $drive_steps(S_{label}_first[.COMPLETION = NORMAL], 1)',
        f'S_{label}_cap.TODO = (CONFIG_ARGS pconfigcall_{label}_cap) :: (ENUM_IS_CALLABLE_INPUT penumqueryinput_{label}) :: ptask_{label}_tail*',
        f'pconfigcall_{label}_cap.SENT = [NAMED_SENT (KNOWN (PARRAY n_{label}_array))]',
        f'$enum_is_callable_input_match(S_{label}_cap, penumqueryinput_{label}, PARRAY n_{label}_array)',
        f'$call_task_valid(S_{label}_cap, ENUM_IS_CALLABLE_INPUT penumqueryinput_{label})',
        f'$($heap_owners($heap_graph(S_{label}_cap), HARRAY n_{label}_array) > 0)',
    ]
    return row, checks


def send(label):
    return [
        f'S_{label}_send = $eis_seek(S_{label}_cap, pconfigcall_{label}_first.SITE, 2, 7000)',
        f'$eis_site(S_{label}_send, pconfigcall_{label}_first.SITE, 2)',
        f'S_{label}_send.TODO = (CONFIG_SEND pconfigcall_{label}_send) :: (ENUM_IS_CALLABLE_INPUT penumqueryinput_{label}) :: ptask_{label}_tail*',
        f'pconfigcall_{label}_send.SENT = [NAMED_SENT (KNOWN (PARRAY n_{label}_array)), NAMED_SENT (KNOWN (PBOOL false))]',
        f'$enum_is_callable_saved(S_{label}_send, pconfigcall_{label}_send, PARRAY n_{label}_array) = (penumqueryinput_{label})',
        f'$enum_is_callable_ref_name(S_{label}_send, pconfigcall_{label}_send, PARRAY n_{label}_array) = (penumqueryinput_{label}.VALUE)',
        f'$enum_is_callable_ref_cell(S_{label}_send, pconfigcall_{label}_send, PARRAY n_{label}_array) = (n_{label}_output)',
    ]


def direct():
    row, checks = begin('direct', 'direct', 'FirstCheck::from')
    checks += [
        'S_direct_first.ARRAYS[n_direct_array].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_direct_receiver), ENTRY (KINT 1) (DIRECT pvalue_direct_method)]',
        '$string_bytes(pvalue_direct_receiver) = ($ptascii("FirstCheck"))',
        '$string_bytes(pvalue_direct_method) = ($ptascii("from"))',
        '$enum_is_callable_target(S_direct_first, PARRAY n_direct_array) = ((porigin_direct, $ptascii("from"), false))',
    ]
    checks += send('direct')
    previous = 'direct_cap'
    for index, name in [('lower', 'firstcheck::FROM'),
                        ('slash', '\\FirstCheck::FROM'),
                        ('case', 'FirstCheck::TRYFROM')]:
        checks += [
            f'S_{index}_first = $eis_seek_first(S_{previous}, 7000)',
            f'$eis_first(S_{index}_first)',
            f'S_{index}_first.TODO = (CONFIG_SEND pconfigcall_{index}_first) :: ptask_{index}_tail*',
            f'$enum_is_callable_capture(S_{index}_first, pconfigcall_{index}_first) = (penumqueryinput_{index})',
            f'penumqueryinput_{index}.ARRAY = (n_{index}_array)',
            f'penumqueryinput_{index}.VALUE = $ptascii({json.dumps(name)})',
            f'$enum_is_callable_variable_array_name(S_{index}_first, PARRAY n_{index}_array) = (penumqueryinput_{index}.VALUE)',
            f'S_{index}_cap = $drive_steps(S_{index}_first[.COMPLETION = NORMAL], 1)',
        ]
        previous = f'{index}_cap'
    checks += [
        'S_case_first.ARRAYS[n_case_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_case_object)), ENTRY (KINT 1) (DIRECT pvalue_case_method)]',
        '$enum_case_object(S_case_first, n_case_object) = (pclassconstantdesc_case)',
        '$enum_is_callable_target(S_case_first, PARRAY n_case_array) = ((pclassconstantdesc_case.OWNER, $ptascii("TRYFROM"), true))',
        '$string_bytes(pvalue_case_method) = ($ptascii("TRYFROM"))',
        'S_direct_done = $drive(S_case_cap[.COMPLETION = NORMAL], 10000)',
        'S_direct_done.COMPLETION = NORMAL',
        '$eic_output(S_direct_done.EVENTS) = $ptascii(' + json.dumps(row['expected_normal_stdout']) + ')',
    ]
    return checks


def rebind():
    row, checks = begin('rebind', 'rebind-second', 'FirstCheck::from')
    checks += send('rebind')
    checks += [
        '$lookup(S_rebind_send.ENV, $ptascii("call")) = (n_rebind_source)',
        'S_rebind_send.STORE[n_rebind_source] = DEFINED (PARRAY n_rebound_array)',
        'n_rebound_array =/= n_rebind_array',
        '$enum_is_callable_variable_array_name(S_rebind_send, PARRAY n_rebound_array) = ($ptascii("OtherCheck::tryFrom"))',
        'penumqueryinput_wrong_id = penumqueryinput_rebind[.ARRAY = (n_rebound_array)][.VALUE = $ptascii("OtherCheck::tryFrom")]',
        '$enum_is_callable_input_source(S_rebind_send, penumqueryinput_wrong_id)',
        '$enum_is_callable_saved(S_rebind_send[.TODO = (CONFIG_SEND pconfigcall_rebind_send) :: (ENUM_IS_CALLABLE_INPUT penumqueryinput_wrong_id) :: ptask_rebind_tail*], pconfigcall_rebind_send, PARRAY n_rebind_array) = eps',
        'penumqueryinput_wrong_name = penumqueryinput_rebind[.VALUE = $ptascii("OtherCheck::tryFrom")]',
        '~$enum_is_callable_input_source(S_rebind_send, penumqueryinput_wrong_name)',
        'penumqueryinput_wrong_origin = penumqueryinput_rebind[.ARGUMENT = pconfigcall_rebind_send.SITE]',
        '~$enum_is_callable_input_source(S_rebind_send, penumqueryinput_wrong_origin)',
        '$enum_is_callable_ref_array_alias_old(S_rebind_send, pconfigcall_rebind_send, n_rebind_source, PARRAY n_rebound_array, penumqueryinput_rebind.VALUE, pconfigcall_rebind_send.LINE) = false',
        'S_rebind_send.ARRAYS[n_rebind_array] = parray_original',
        'parray_original.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_original_receiver), ENTRY (KINT 1) (DIRECT pvalue_original_method)]',
        'S_alias_store = S_rebind_send[.STORE = $set_cell(S_rebind_send.STORE, n_rebind_output, DEFINED (PSTRING $ptascii("FirstCheck")))]',
        'parray_alias = parray_original[.ITEMS = [ENTRY (KINT 0) (ALIAS n_rebind_output), ENTRY (KINT 1) (DIRECT pvalue_original_method)]]',
        'S_alias_member = S_alias_store[.ARRAYS = S_alias_store.ARRAYS[0:n_rebind_array] ++ [parray_alias] ++ S_alias_store.ARRAYS[$(n_rebind_array + 1):|S_alias_store.ARRAYS|]]',
        '$typed_callback_array(S_alias_member, n_rebind_array)',
        '$enum_is_callable_variable_array_name(S_alias_member, PARRAY n_rebind_array) = eps',
        '$enum_is_callable_saved(S_alias_member, pconfigcall_rebind_send, PARRAY n_rebind_array) = eps',
        'parray_shape = parray_original[.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_original_receiver), ENTRY (KINT 2) (DIRECT pvalue_original_method)]]',
        'S_bad_shape = S_rebind_send[.ARRAYS = S_rebind_send.ARRAYS[0:n_rebind_array] ++ [parray_shape] ++ S_rebind_send.ARRAYS[$(n_rebind_array + 1):|S_rebind_send.ARRAYS|]]',
        '$enum_is_callable_variable_array_name(S_bad_shape, PARRAY n_rebind_array) = eps',
        'S_rebind_done = $drive(S_rebind_send[.COMPLETION = NORMAL], 10000)',
        'S_rebind_done.COMPLETION = NORMAL',
        '$eic_output(S_rebind_done.EVENTS) = $ptascii(' + json.dumps(row['expected_normal_stdout']) + ')',
    ]
    return checks


def alias():
    row, checks = begin('alias', 'alias', 'FirstCheck::from')
    checks += send('alias')
    checks += [
        '$lookup(S_alias_send.ENV, $ptascii("call")) = (n_alias_output)',
        'S_alias_send.STORE[n_alias_output] = DEFINED (PARRAY n_alias_array)',
        '$enum_is_callable_ref_old(S_alias_send, n_alias_output, PARRAY n_alias_array, penumqueryinput_alias.VALUE, pconfigcall_alias_send.LINE) = false',
        '$enum_is_callable_ref_array_alias_old(S_alias_send, pconfigcall_alias_send, n_alias_output, PARRAY n_alias_array, penumqueryinput_alias.VALUE, pconfigcall_alias_send.LINE)',
        'S_alias_after = $drive(S_alias_send[.COMPLETION = NORMAL], 5000)',
        'S_alias_after.COMPLETION = NORMAL',
        'S_alias_after.STORE[n_alias_output] = DEFINED (PSTRING $ptascii("FirstCheck::from"))',
        '$eic_output(S_alias_after.EVENTS) = $ptascii(' + json.dumps(row['expected_normal_stdout']) + ')',
    ]
    return checks


if __name__ == '__main__':
    groups = {'direct': direct, 'rebind': rebind, 'alias': alias}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=['all', *groups], default='all')
    args = parser.parse_args()
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    selected = groups.values() if args.group == 'all' else [groups[args.group]]
    checks = [check for group in selected for check in group()]
    fixture = OUT / 'variable-array.watsup'
    fixture.write_text(base.PREFIX + saved.PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                       + ''.join('  -- if ' + check + '\n' for check in checks))
    command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
               *map(str, MODULES), str(fixture)]
    (OUT / 'command.json').write_text(json.dumps(command) + '\n')
    start = time.monotonic()
    timed_out = False
    try:
        result = subprocess.run(command, capture_output=True, timeout=180)
    except subprocess.TimeoutExpired as error:
        timed_out = True
        result = subprocess.CompletedProcess(command, 124, error.stdout or b'', error.stderr or b'')
    (OUT / 'stdout').write_bytes(result.stdout)
    (OUT / 'stderr').write_bytes(result.stderr)
    record = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'group': args.group, 'checks': len(checks), 'exit': result.returncode,
              'timeout_seconds': 180, 'timed_out': timed_out, 'elapsed': time.monotonic() - start,
              'stdout': result.stdout.decode(errors='replace'),
              'stderr': result.stderr.decode(errors='replace'),
              'stable': before == {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                  for path in WATCHED}, 'direct_inputs': before}
    (OUT / 'report.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: record[k] for k in ['revision', 'group', 'checks', 'exit', 'timed_out', 'stdout', 'stderr', 'stable']}), OUT, flush=True)
    assert result.returncode == 0 and not timed_out and result.stdout == b'true\n' and not result.stderr and record['stable'], OUT
