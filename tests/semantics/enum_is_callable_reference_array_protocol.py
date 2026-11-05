#!/usr/bin/env python3
"""Reached enum query member-output alias and early-argument-throw invariants."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

import enum_is_callable_saved_input_protocol as saved

base = saved.base
ROOT, OUT, MODULES = saved.ROOT, saved.OUT, saved.MODULES
WATCHED = [*saved.WATCHED, Path(__file__)]
PREFIX = r'''
dec $eir_throw(pstate) : bool
def $eir_throw(S) = true -- if S.TODO = (THROW_SEARCH n) :: ptask*
def $eir_throw(S) = false -- otherwise
dec $eir_seek_throw(pstate, nat) : pstate
def $eir_seek_throw(S, 0) = S
def $eir_seek_throw(S, n) = S -- if $(n > 0) /\ $eir_throw(S)
def $eir_seek_throw(S, n) = $eir_seek_throw($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if $(n > 0) /\ ~$eir_throw(S)
'''


def begin(label, suffix, name):
    row = base.CASES['enum-is-callable-third-output-reference-' + suffix]
    checks = [
        f'S_{label}_initial = ' + saved.checked(row, label),
        f'S_{label}_initial.COMPLETION = BUDGET',
        f'S_{label}_first = $eis_seek_first(S_{label}_initial, 4000)',
        f'$eis_first(S_{label}_first)',
        f'S_{label}_first.TODO = (CONFIG_SEND pconfigcall_{label}_first) :: ptask_{label}_tail*',
        f'$enum_is_callable_capture(S_{label}_first, pconfigcall_{label}_first) = (penumqueryinput_{label})',
        f'penumqueryinput_{label}.ARRAY = (n_{label}_array)',
        f'penumqueryinput_{label}.VALUE = $ptascii({json.dumps(name)})',
        f'penumqueryinput_{label}.ITEMS = S_{label}_first.ARRAYS[n_{label}_array].ITEMS',
        f'$enum_is_callable_array_snapshot(S_{label}_first, n_{label}_array, penumqueryinput_{label}.VALUES)',
        f'$enum_is_callable_input_source(S_{label}_first, penumqueryinput_{label})',
        f'$task_nodes(ENUM_IS_CALLABLE_INPUT penumqueryinput_{label}) = eps',
        f'S_{label}_cap = $drive_steps(S_{label}_first[.COMPLETION = NORMAL], 1)',
        f'S_{label}_cap.TODO = (CONFIG_ARGS pconfigcall_{label}_cap) :: (ENUM_IS_CALLABLE_INPUT penumqueryinput_{label}) :: ptask_{label}_tail*',
        f'pconfigcall_{label}_cap.SENT = [NAMED_SENT (KNOWN (PARRAY n_{label}_array))]',
        f'$call_task_valid(S_{label}_cap, ENUM_IS_CALLABLE_INPUT penumqueryinput_{label})',
        f'$heap_graph(S_{label}_cap) = $heap_graph(S_{label}_cap[.TODO = (CONFIG_ARGS pconfigcall_{label}_cap) :: ptask_{label}_tail*])',
    ]
    return row, checks


def alias():
    row, checks = begin('alias', 'member-output-alias', 'RefCheck::from')
    checks += [
        'penumqueryinput_alias.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_alias_receiver), ENTRY (KINT 1) (ALIAS n_alias_method)]',
        'S_alias_invoke = $eis_seek(S_alias_cap, pconfigcall_alias_first.SITE, 3, 4000)',
        '$eis_site(S_alias_invoke, pconfigcall_alias_first.SITE, 3)',
        'S_alias_invoke.TODO = (CONFIG_INVOKE pconfigcall_alias_invoke) :: (ENUM_IS_CALLABLE_INPUT penumqueryinput_alias) :: ptask_alias_tail*',
        'pconfigcall_alias_invoke.SENT = [NAMED_SENT (KNOWN (PARRAY n_alias_array)), NAMED_SENT (KNOWN (PBOOL false)), NAMED_SENT (REFERENCE n_alias_method)]',
        '$enum_is_callable_ref_slots_valid(S_alias_invoke, pconfigcall_alias_invoke)',
        '$node_children(S_alias_invoke, HARRAY n_alias_array) = [HCELL n_alias_method]',
        'S_alias_after = $drive_steps(S_alias_invoke[.COMPLETION = NORMAL], 1)',
        'S_alias_after.TODO = ptask_alias_tail*',
        'S_alias_after.RESULT = KNOWN (PBOOL true)',
        'S_alias_after.STORE[n_alias_method] = DEFINED (PSTRING $ptascii("RefCheck::from"))',
        '$enum_is_callable_variable_array_name(S_alias_after, PARRAY n_alias_array) = ($ptascii("RefCheck::RefCheck::from"))',
        'S_alias_done = $drive(S_alias_after[.COMPLETION = NORMAL], 5000)',
        'S_alias_done.COMPLETION = NORMAL',
        '$eic_output(S_alias_done.EVENTS) = $ptascii(' + json.dumps(row['expected_normal_stdout']) + ')',
    ]
    return checks


def thrown():
    row, checks = begin('throw', 'throw-second', 'FirstCheck::from')
    checks += [
        'S_throw_search = $eir_seek_throw(S_throw_cap, 6000)',
        '$eir_throw(S_throw_search)',
        'S_throw_search.TODO = (THROW_SEARCH n_throw) :: ptask_throw_search*',
        '$throwable_live(S_throw_search, n_throw)',
        'S_throw_search.FRAMES = pframe_throw :: pframe_throw_tail*',
        '$eis_has(pframe_throw.TODO, penumqueryinput_throw)',
        '$lookup(S_throw_cap.ENV, $ptascii("name")) = (n_throw_output)',
        '$lookup(S_throw_cap.ENV, $ptascii("ok")) = (n_throw_result)',
        'S_throw_search.STORE[n_throw_output] = S_throw_cap.STORE[n_throw_output]',
        'S_throw_search.STORE[n_throw_result] = S_throw_cap.STORE[n_throw_result]',
        'S_throw_done = $drive(S_throw_search[.COMPLETION = NORMAL], 7000)',
        'S_throw_done.COMPLETION = NORMAL',
        'S_throw_done.FRAMES = eps',
        '~$eis_has(S_throw_done.TODO, penumqueryinput_throw)',
        'S_throw_done.STORE[n_throw_output] = S_throw_cap.STORE[n_throw_output]',
        'S_throw_done.STORE[n_throw_result] = S_throw_cap.STORE[n_throw_result]',
        '$eic_output(S_throw_done.EVENTS) = $ptascii(' + json.dumps(row['expected_normal_stdout']) + ')',
        'S_throw_zero = $drive_steps(S_throw_search[.COMPLETION = NORMAL], 0)',
        'S_throw_zero.COMPLETION = BUDGET',
        '$drive(S_throw_zero[.COMPLETION = NORMAL], 7000) = S_throw_done',
    ]
    return checks


if __name__ == '__main__':
    groups = {'alias': alias, 'throw': thrown}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(groups), required=True)
    args = parser.parse_args()
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    checks = groups[args.group]()
    fixture = OUT / 'reference-array.watsup'
    fixture.write_text(base.PREFIX + saved.PREFIX + PREFIX
                       + '\ndec $main() : bool\ndef $main() = true\n'
                       + ''.join('  -- if ' + check + '\n' for check in checks))
    command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
               *map(str, MODULES), str(fixture)]
    (OUT / 'command.json').write_text(json.dumps(command) + '\n')
    start = time.monotonic()
    try:
        result = subprocess.run(command, capture_output=True, timeout=240)
    except subprocess.TimeoutExpired as error:
        result = subprocess.CompletedProcess(command, 124, error.stdout or b'', error.stderr or b'')
    (OUT / 'stdout').write_bytes(result.stdout)
    (OUT / 'stderr').write_bytes(result.stderr)
    record = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'group': args.group, 'checks': len(checks), 'exit': result.returncode,
              'timeout_seconds': 240, 'elapsed': time.monotonic() - start,
              'stdout': result.stdout.decode(errors='replace'),
              'stderr': result.stderr.decode(errors='replace'),
              'stable': before == {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                  for path in WATCHED}, 'direct_inputs': before}
    (OUT / 'report.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: record[k] for k in ['revision', 'group', 'checks', 'exit', 'stdout', 'stderr', 'stable']}), OUT, flush=True)
    assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr and record['stable'], OUT
