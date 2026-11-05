#!/usr/bin/env python3
"""Source-reached enum array alias output after a second-argument rebind."""
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
           ROOT / 'tests/semantics/enum_is_callable_array_alias_rebound_protocol.py',
           ROOT / 'tests/semantics/profile.json',
           ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *MODULES]


def rebound(label, suffix, name):
    row, checks = variable.begin(label, 'alias-rebound-' + suffix, name)
    checks += variable.send(label)
    checks += [
        f'$lookup(S_{label}_send.ENV, $ptascii("call")) = (n_{label}_output)',
        f'$lookup(S_{label}_send.ENV, $ptascii("name")) = (n_{label}_output)',
        f'S_{label}_send.STORE[n_{label}_output] = DEFINED (PARRAY n_{label}_old)',
        f'n_{label}_old =/= n_{label}_array',
        f'S_{label}_send.ARRAYS[n_{label}_old].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_{label}_receiver), ENTRY (KINT 1) (DIRECT pvalue_{label}_method)]',
        f'$enum_array_string_valid(S_{label}_send, pvalue_{label}_receiver)',
        f'$enum_array_string_valid(S_{label}_send, pvalue_{label}_method)',
        f'$enum_is_callable_ref_array_alias_old(S_{label}_send, pconfigcall_{label}_send, n_{label}_output, PARRAY n_{label}_old, penumqueryinput_{label}.VALUE, pconfigcall_{label}_send.LINE)',
        f'$($heap_owners($heap_graph(S_{label}_send), HARRAY n_{label}_array) > 0)',
        f'S_{label}_ref = $drive_steps(S_{label}_send[.COMPLETION = NORMAL], 1)',
        f'S_{label}_ref.TODO = (CONFIG_ARGS pconfigcall_{label}_ref) :: (ENUM_IS_CALLABLE_INPUT penumqueryinput_{label}) :: ptask_{label}_tail*',
        f'pconfigcall_{label}_ref.SENT = [NAMED_SENT (KNOWN (PARRAY n_{label}_array)), NAMED_SENT (KNOWN (PBOOL false)), NAMED_SENT (REFERENCE n_{label}_output)]',
        f'S_{label}_invoke = $eis_seek(S_{label}_ref, pconfigcall_{label}_first.SITE, 3, 3000)',
        f'$eis_site(S_{label}_invoke, pconfigcall_{label}_first.SITE, 3)',
        f'S_{label}_invoke.TODO = (CONFIG_INVOKE pconfigcall_{label}_invoke) :: (ENUM_IS_CALLABLE_INPUT penumqueryinput_{label}) :: ptask_{label}_tail*',
        f'$enum_is_callable_ref_array_alias_old(S_{label}_invoke, pconfigcall_{label}_invoke, n_{label}_output, PARRAY n_{label}_old, penumqueryinput_{label}.VALUE, pconfigcall_{label}_invoke.LINE)',
        f'$config_invoke_valid(S_{label}_invoke, pconfigcall_{label}_invoke)',
        f'S_{label}_done = $drive(S_{label}_invoke[.COMPLETION = NORMAL], 8000)',
        f'S_{label}_done.COMPLETION = NORMAL',
        f'S_{label}_done.STORE[n_{label}_output] = DEFINED (PSTRING penumqueryinput_{label}.VALUE)',
        f'$eic_output(S_{label}_done.EVENTS) = $ptascii(' + json.dumps(row['expected_normal_stdout']) + ')',
    ]
    return checks


def raw():
    checks = rebound('raw', 'raw-class-rebind', '\\firstcheck::FROM')
    checks += [
        '$string_bytes(pvalue_raw_receiver) = ($ptascii("OtherCheck"))',
        '$string_bytes(pvalue_raw_method) = ($ptascii("tryFrom"))',
        '$enum_is_callable_variable_array_name(S_raw_send, PARRAY n_raw_old) = ($ptascii("OtherCheck::tryFrom"))',
        'penumqueryinput_wrong_id = penumqueryinput_raw[.ARRAY = (n_raw_old)][.VALUE = $ptascii("OtherCheck::tryFrom")]',
        '$enum_is_callable_input_source(S_raw_send, penumqueryinput_wrong_id)',
        'S_wrong_id = S_raw_send[.TODO = (CONFIG_SEND pconfigcall_raw_send) :: (ENUM_IS_CALLABLE_INPUT penumqueryinput_wrong_id) :: ptask_raw_tail*]',
        '$enum_is_callable_saved(S_wrong_id, pconfigcall_raw_send, PARRAY n_raw_array) = eps',
        '$enum_is_callable_ref_array_alias_old(S_wrong_id, pconfigcall_raw_send, n_raw_output, PARRAY n_raw_old, penumqueryinput_raw.VALUE, pconfigcall_raw_send.LINE) = false',
        '$lookup(S_raw_send.ENV, $ptascii("ok")) = (n_raw_ok)',
        'S_raw_send.STORE[n_raw_ok] = DEFINED (PSTRING $ptascii("UNCHANGED"))',
        'S_raw_send.ARRAYS[n_raw_old] = parray_raw_old',
        'n_raw_after = $(n_raw_old + 1)',
        'n_raw_remaining = $nabs($(|S_raw_send.ARRAYS| - n_raw_after))',
        'parray_raw_alias = parray_raw_old[.ITEMS = [ENTRY (KINT 0) (ALIAS n_raw_ok), ENTRY (KINT 1) (DIRECT pvalue_raw_method)]]',
        'S_raw_alias = S_raw_send[.ARRAYS = S_raw_send.ARRAYS[0:n_raw_old] ++ [parray_raw_alias] ++ S_raw_send.ARRAYS[n_raw_after:n_raw_remaining]]',
        '$typed_callback_array(S_raw_alias, n_raw_old)',
        '$enum_is_callable_ref_array_alias_old(S_raw_alias, pconfigcall_raw_send, n_raw_output, PARRAY n_raw_old, penumqueryinput_raw.VALUE, pconfigcall_raw_send.LINE) = false',
    ]
    return checks


def case():
    checks = rebound('case', 'case-rebind', 'FirstCheck::TRYFROM')
    checks += [
        'S_case_first.ARRAYS[n_case_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_case_object)), ENTRY (KINT 1) (DIRECT pvalue_case_original_method)]',
        '$enum_case_object(S_case_first, n_case_object) = (pclassconstantdesc_case)',
        '$enum_is_callable_target(S_case_first, PARRAY n_case_array) = ((pclassconstantdesc_case.OWNER, $ptascii("TRYFROM"), true))',
        '$string_bytes(pvalue_case_original_method) = ($ptascii("TRYFROM"))',
    ]
    return checks


def retained():
    checks = rebound('retained', 'retained-rebound', 'FirstCheck::from')
    checks += [
        '$lookup(S_retained_send.ENV, $ptascii("hold")) = (n_hold)',
        'n_hold =/= n_retained_output',
        'S_retained_send.STORE[n_hold] = DEFINED (PARRAY n_retained_old)',
        '$($heap_owners($heap_graph(S_retained_send), HARRAY n_retained_old) > 1)',
        'S_retained_done.STORE[n_hold] = DEFINED (PARRAY n_retained_old)',
        '$($heap_owners($heap_graph(S_retained_done), HARRAY n_retained_old) > 0)',
        '$enum_is_callable_variable_array_name(S_retained_done, PARRAY n_retained_old) = ($ptascii("OtherCheck::tryFrom"))',
    ]
    return checks


def control():
    row, checks = variable.begin('control', 'alias-rebound-owning-rebound-control', 'FirstCheck::from')
    checks += [
        'S_control_send = $eis_seek(S_control_cap, pconfigcall_control_first.SITE, 2, 7000)',
        '$eis_site(S_control_send, pconfigcall_control_first.SITE, 2)',
        'S_control_send.TODO = (CONFIG_SEND pconfigcall_control_send) :: (ENUM_IS_CALLABLE_INPUT penumqueryinput_control) :: ptask_control_tail*',
        'pconfigcall_control_send.SENT = [NAMED_SENT (KNOWN (PARRAY n_control_array)), NAMED_SENT (KNOWN (PBOOL false))]',
        '$enum_is_callable_saved(S_control_send, pconfigcall_control_send, PARRAY n_control_array) = (penumqueryinput_control)',
        '$enum_is_callable_ref_name(S_control_send, pconfigcall_control_send, PARRAY n_control_array) = (penumqueryinput_control.VALUE)',
        '$lookup(S_control_send.ENV, $ptascii("call")) = (n_control_output)',
        '$lookup(S_control_send.ENV, $ptascii("name")) = (n_control_output)',
        'S_control_send.STORE[n_control_output] = DEFINED (PARRAY n_control_old)',
        'n_control_old =/= n_control_array',
        'S_control_send.ARRAYS[n_control_old].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_child)), ENTRY (KINT 1) (DIRECT pvalue_control_method)]',
        '$typed_callback_array(S_control_send, n_control_old)',
        '~$enum_array_string_valid(S_control_send, POBJECT n_child)',
        '$enum_is_callable_ref_array_alias_old(S_control_send, pconfigcall_control_send, n_control_output, PARRAY n_control_old, penumqueryinput_control.VALUE, pconfigcall_control_send.LINE) = false',
        '$enum_is_callable_ref_cell(S_control_send, pconfigcall_control_send, PARRAY n_control_array) = eps',
    ]
    return checks


def thrown():
    row, checks = variable.begin('thrown', 'alias-rebound-throw-before-output', 'FirstCheck::from')
    checks += [
        'S_thrown_done = $drive(S_thrown_cap[.COMPLETION = NORMAL], 8000)',
        'S_thrown_done.COMPLETION = NORMAL',
        '$lookup(S_thrown_done.ENV, $ptascii("call")) = (n_thrown_cell)',
        '$lookup(S_thrown_done.ENV, $ptascii("name")) = (n_thrown_cell)',
        'S_thrown_done.STORE[n_thrown_cell] = DEFINED (PARRAY n_thrown_old)',
        'n_thrown_old =/= n_thrown_array',
        '$enum_is_callable_variable_array_name(S_thrown_done, PARRAY n_thrown_old) = ($ptascii("OtherCheck::tryFrom"))',
        '$lookup(S_thrown_done.ENV, $ptascii("ok")) = (n_thrown_ok)',
        'S_thrown_done.STORE[n_thrown_ok] = DEFINED (PSTRING $ptascii("UNCHANGED"))',
        '$eic_output(S_thrown_done.EVENTS) = $ptascii(' + json.dumps(row['expected_normal_stdout']) + ')',
    ]
    return checks


if __name__ == '__main__':
    groups = {'raw': raw, 'case': case, 'retained': retained,
              'control': control, 'throw': thrown}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=['all', *groups], default='all')
    args = parser.parse_args()
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    selected = groups.values() if args.group == 'all' else [groups[args.group]]
    checks = [check for group in selected for check in group()]
    fixture = OUT / 'array-alias-rebound.watsup'
    fixture.write_text(base.PREFIX + saved.PREFIX
                       + '\ndec $main() : bool\ndef $main() = true\n'
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
              'timeout_seconds': 180, 'timed_out': timed_out,
              'elapsed': time.monotonic() - start,
              'stdout': result.stdout.decode(errors='replace'),
              'stderr': result.stderr.decode(errors='replace'),
              'stable': before == {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                  for path in WATCHED}, 'direct_inputs': before}
    (OUT / 'report.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: record[k] for k in ['revision', 'group', 'checks', 'exit', 'timed_out', 'stdout', 'stderr', 'stable']}), OUT, flush=True)
    assert result.returncode == 0 and not timed_out and result.stdout == b'true\n' and not result.stderr and record['stable'], OUT
