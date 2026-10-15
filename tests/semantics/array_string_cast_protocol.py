#!/usr/bin/env python3
"""Production array-cast warning, borrowed lifetime and cancellation fronts."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import array_string_cast_cases as cases
import arithmetic_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $array_string_cast_task(ptask) : bool
def $array_string_cast_task(ARRAY_STRING_CAST_WARNING porigin poperand z n) = true
def $array_string_cast_task(ERROR_HANDLER_INVOKE perrorcall) = $array_string_cast_task(perrorcall.RESUME)
def $array_string_cast_task(ERROR_HANDLER_RESULT perrorcall) = $array_string_cast_task(perrorcall.RESUME)
def $array_string_cast_task(ERROR_HANDLER_CLEAN perrorcall) = $array_string_cast_task(perrorcall.RESUME)
def $array_string_cast_task(ptask) = false -- otherwise
dec $array_string_cast_tasks(ptask*) : bool
def $array_string_cast_tasks(eps) = false
def $array_string_cast_tasks(ptask :: ptask_tail*) = ($array_string_cast_task(ptask) \/ $array_string_cast_tasks(ptask_tail*))
dec $array_string_cast_handler_frame(pframe) : bool
def $array_string_cast_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARRAY_STRING_CAST_WARNING porigin poperand z 1
  -- if perrorcall.TARGET =/= eps
def $array_string_cast_handler_frame(pframe) = false -- otherwise
dec $array_string_cast_entered(pframe*) : bool
def $array_string_cast_entered(eps) = false
def $array_string_cast_entered(pframe :: pframe_tail*) = ($array_string_cast_handler_frame(pframe) \/ $array_string_cast_entered(pframe_tail*))
dec $array_string_cast_frontier(pstate, nat) : bool
def $array_string_cast_frontier(S, 0) = ($array_string_cast_plan(S) =/= eps)
def $array_string_cast_frontier(S, 1) = true
  -- if S.TODO = (ARRAY_STRING_CAST_WARNING porigin poperand z 0) :: ptask_tail*
def $array_string_cast_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARRAY_STRING_CAST_WARNING porigin poperand z 1
  -- if perrorcall.TARGET = eps
def $array_string_cast_frontier(S, 3) = (S.CURRENT =/= eps /\ $array_string_cast_entered(S.FRAMES))
def $array_string_cast_frontier(S, 4) = true
  -- if S.TODO = (ARRAY_STRING_CAST_WARNING porigin poperand z 1) :: ptask_tail*
def $array_string_cast_frontier(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprCastString expression metadata)
  -- if S.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("Array")))
  -- if ~$array_string_cast_tasks(S.TODO)
def $array_string_cast_frontier(S, 6) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if ~$array_string_cast_tasks(S.TODO)
def $array_string_cast_frontier(S, n) = false -- otherwise
dec $array_string_cast_seek(pstate, nat, nat) : pstate
def $array_string_cast_seek(S, n_stage, n) = S -- if $array_string_cast_frontier(S, n_stage)
def $array_string_cast_seek(S, n_stage, n) = S
  -- if ~$array_string_cast_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $array_string_cast_seek(S, n_stage, n) = S
  -- if ~$array_string_cast_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $array_string_cast_seek(S, n_stage, n) = $array_string_cast_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$array_string_cast_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    thrown = name.endswith('-throw')
    line = 11 if thrown else 10
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $array_string_cast_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]', '$array_string_cast_frontier(S_entry, 0)',
        '$array_string_cast_plan(S_entry) = ((porigin, poperand, ' + str(line) + '))',
        'poperand = VARIABLE ($ptascii("input")) ' + str(line),
        '$lookup(S_entry.ENV, $ptascii("input")) = (n_input)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'S_entry.STORE[n_input] = DEFINED (PARRAY n_array)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
        '~(n_input <- S_entry.REFCELLS)', '~(n_array <- S_entry.GC.IMMUTABLE)',
        '$array_string_cast_source(S_entry, porigin, poperand, ' + str(line) + ')',
        '$array_string_cast_snapshot(S_entry, poperand)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_array) = 1',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$array_string_cast_plan(S_entry[.RESULT = KNOWN (PARRAY n_array)]) = eps',
        '$array_string_cast_plan(S_entry[.STORE[n_input] = UNDEFINED]) = eps',
        '~$array_string_cast_snapshot(S_entry[.GC.IMMUTABLE = S_entry.GC.IMMUTABLE ++ [n_array]], poperand)',
        '~$array_string_cast_snapshot(S_entry[.ARRAYS[n_array].ITEMS = eps], poperand)',
        '~$array_string_cast_items([ENTRY (KINT 0) UNINITIALIZED])',
        '~$array_string_cast_items([ENTRY (KINT 0) (ALIAS n_input)])',
        '~$array_string_cast_items([ENTRY (KINT 0) (DIRECT (PARRAY n_array))])',
        'S_capture_budget = $drive_steps(S_entry, 1)', 'S_capture_budget.COMPLETION = BUDGET',
        'S_capture = S_capture_budget[.COMPLETION = NORMAL]', '$array_string_cast_frontier(S_capture, 1)',
        'S_capture.TODO = (ARRAY_STRING_CAST_WARNING porigin poperand ' + str(line) + ' 0) :: ptask_tail*',
        'S_capture.RESULT = KNOWN PNULL', 'S_capture.BASE = BASE_VALUE (KNOWN PNULL)',
        '$task_nodes(ARRAY_STRING_CAST_WARNING porigin poperand ' + str(line) + ' 0) = eps',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HARRAY n_array) = 1',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
        '(porigin_bad) = $origin_child((porigin), [PCFIELD 0])',
        'S_source_bad = S_capture[.ORIGIN = (porigin_bad)][.TODO = (ARRAY_STRING_CAST_WARNING porigin_bad poperand ' + str(line) + ' 0) :: ptask_tail*]',
        '$array_string_cast_snapshot(S_source_bad, poperand)',
        '$heap_valid($heap_graph(S_source_bad))', '~$call_descriptors_valid(S_source_bad)',
        'S_stage_bad = S_capture[.TODO = (ARRAY_STRING_CAST_WARNING porigin poperand ' + str(line) + ' 2) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_stage_bad))', '~$call_descriptors_valid(S_stage_bad)',
        'S_dispatch_budget = $drive_steps(S_capture, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]', '$array_string_cast_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.TARGET = eps',
        'perrorcall.RESUME = ARRAY_STRING_CAST_WARNING porigin poperand ' + str(line) + ' 1',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'S_entered_found = $array_string_cast_seek(S_dispatch, 3, 2000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', '$array_string_cast_frontier(S_entered, 3)',
        'S_entered.FRAMES = pframe :: pframe_tail*', '$array_string_cast_handler_frame(pframe)',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_saved*',
        'perrorcall_entered.RESUME = ARRAY_STRING_CAST_WARNING porigin poperand ' + str(line) + ' 1',
        'perrorcall_entered.TARGET =/= eps',
        '$heap_owners($heap_prune($heap_graph(S_entered)), HARRAY n_array) = 1',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if thrown:
        checks += [
            '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
            'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            'S_owning = S_capture[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_second))]]',
            '$heap_valid($heap_graph(S_owning))', '~$array_string_cast_snapshot(S_owning, poperand)',
            '~$call_descriptors_valid(S_owning)',
            'S_throw_found = $array_string_cast_seek(S_entered, 6, 2000)',
            r'S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET',
            'S_throw = S_throw_found[.COMPLETION = NORMAL]', '$array_string_cast_frontier(S_throw, 6)',
            'S_throw.TODO = (THROW_SEARCH n_second) :: ptask_throw*',
            'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps', '~$array_string_cast_tasks(S_throw.TODO)',
            'S_throw.STORE[n_input] = DEFINED (PINT 99)',
            'S_throw.STORE[n_v] = DEFINED (PINT 100)',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HARRAY n_array) = 0',
            '$throwable_live(S_throw, n_second)', '$throwable_previous_id(S_throw, n_second) = eps',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
            'S_throw.ERRORHANDLER = S_entry.ERRORHANDLER',
            '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
            'S_done = $drive_steps(S_throw, 2000)', '$drive_steps(S_dispatch, 2000) = S_done',
            'S_done.STORE[n_v] = DEFINED (PINT 100)',
        ]
    else:
        checks += [
            'S_return_found = $array_string_cast_seek(S_entered, 4, 2000)',
            r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
            'S_return = S_return_found[.COMPLETION = NORMAL]', '$array_string_cast_frontier(S_return, 4)',
            'S_return.TODO = (ARRAY_STRING_CAST_WARNING porigin poperand ' + str(line) + ' 1) :: ptask_tail*',
            'S_return.STORE[n_input] = DEFINED (PINT 99)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
            '~$array_string_cast_snapshot(S_return, poperand)',
            '$array_string_cast_warning_valid(S_return, porigin, poperand, ' + str(line) + ', 1)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_array) = 0',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
            'S_result_budget = $drive_steps(S_return, 1)', 'S_result_budget.COMPLETION = BUDGET',
            'S_result = S_result_budget[.COMPLETION = NORMAL]', '$array_string_cast_frontier(S_result, 5)',
            'S_result.TODO = ptask_tail*',
            'S_result.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("Array")))',
            'S_result.BASE = BASE_VALUE (KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("Array"))))',
            'S_result.STORE = S_return.STORE', 'S_result.ARRAYS = S_return.ARRAYS',
            'S_result.ALLOCATIONS = S_return.ALLOCATIONS', 'S_result.EVENTS = S_return.EVENTS',
            'S_result.STORE[n_v] = DEFINED (PINT 100)',
            '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
            'S_done = $drive_steps(S_result, 2000)', '$drive_steps(S_return, 2000) = S_done',
            'S_done.STORE[n_v] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("Array")))',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_input] = DEFINED (PINT 99)',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_capture, 2000) = S_done',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path, required=True)
    args, _ = parser.parse_known_args()
    watched = [Path(__file__), Path(cases.__file__), Path(shared.__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    shared.cases, shared.CASES, shared.HELPERS, shared.conditions = cases, CASES, HELPERS, conditions
    passed = shared.main()
    assert before == {str(path): digest(path) for path in watched}
    report = json.loads((args.output / 'report.json').read_bytes())
    report['array_string_cast_inputs'] = before
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
