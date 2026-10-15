#!/usr/bin/env python3
"""Source-reached concat array warnings, selected RHS and cancellation fronts."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import concat_array_warning_cases as cases
import arithmetic_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $concat_array_task(ptask) : bool
def $concat_array_task(CONCAT_ARRAY_LEFT_WARNING porigin poperand_left poperand_right n_cell z n) = true
def $concat_array_task(CONCAT_ARRAY_RIGHT_WARNING porigin poperand_left poperand_right z n) = true
def $concat_array_task(ERROR_HANDLER_INVOKE perrorcall) = $concat_array_task(perrorcall.RESUME)
def $concat_array_task(ERROR_HANDLER_RESULT perrorcall) = $concat_array_task(perrorcall.RESUME)
def $concat_array_task(ERROR_HANDLER_CLEAN perrorcall) = $concat_array_task(perrorcall.RESUME)
def $concat_array_task(ptask) = false -- otherwise
dec $concat_array_tasks(ptask*) : bool
def $concat_array_tasks(eps) = false
def $concat_array_tasks(ptask :: ptask_tail*) = ($concat_array_task(ptask) \/ $concat_array_tasks(ptask_tail*))
dec $concat_array_stage(ptask, nat) : bool
def $concat_array_stage(CONCAT_ARRAY_LEFT_WARNING porigin poperand_left poperand_right n_cell z n, n) = true
def $concat_array_stage(CONCAT_ARRAY_RIGHT_WARNING porigin poperand_left poperand_right z n, n) = true
def $concat_array_stage(ptask, n) = false -- otherwise
dec $concat_array_legacy_task(ptask) : bool
def $concat_array_legacy_task(CONCAT_AFTER_LEFT porigin poperand b z) = true
def $concat_array_legacy_task(CONCAT_AFTER_RIGHT porigin pvalue z) = true
def $concat_array_legacy_task(ptask) = false -- otherwise
dec $concat_array_legacy(ptask*) : bool
def $concat_array_legacy(eps) = false
def $concat_array_legacy(ptask :: ptask_tail*) = ($concat_array_legacy_task(ptask) \/ $concat_array_legacy(ptask_tail*))
dec $concat_array_handler_frame(pframe) : bool
def $concat_array_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if $concat_array_stage(perrorcall.RESUME, 1)
  -- if perrorcall.TARGET =/= eps
def $concat_array_handler_frame(pframe) = false -- otherwise
dec $concat_array_entered(pframe*) : bool
def $concat_array_entered(eps) = false
def $concat_array_entered(pframe :: pframe_tail*) = ($concat_array_handler_frame(pframe) \/ $concat_array_entered(pframe_tail*))
dec $concat_array_frontier(pstate, nat) : bool
def $concat_array_frontier(S, 0) = ($concat_array_plan(S) =/= eps)
def $concat_array_frontier(S, 1) = true
  -- if S.TODO = ptask :: ptask_tail*
  -- if $concat_array_stage(ptask, 0)
def $concat_array_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if $concat_array_stage(perrorcall.RESUME, 1)
  -- if perrorcall.TARGET = eps
def $concat_array_frontier(S, 3) = (S.CURRENT =/= eps /\ $concat_array_entered(S.FRAMES))
def $concat_array_frontier(S, 4) = true
  -- if S.TODO = ptask :: ptask_tail*
  -- if $concat_array_stage(ptask, 1)
def $concat_array_frontier(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("Array")))
  -- if ~$concat_array_tasks(S.TODO)
  -- if $concat_array_legacy(S.TODO)
def $concat_array_frontier(S, 6) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if ~$concat_array_tasks(S.TODO) /\ ~$concat_array_legacy(S.TODO)
def $concat_array_frontier(S, n) = false -- otherwise
dec $concat_array_seek(pstate, nat, nat) : pstate
def $concat_array_seek(S, n_stage, n) = S -- if $concat_array_frontier(S, n_stage)
def $concat_array_seek(S, n_stage, n) = S
  -- if ~$concat_array_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $concat_array_seek(S, n_stage, n) = S
  -- if ~$concat_array_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $concat_array_seek(S, n_stage, n) = $concat_array_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$concat_array_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    thrown = name.endswith('-throw')
    line = 13 if thrown else 12
    left = 'VARIABLE ($ptascii("left")) ' + str(line - 1)
    right = 'VARIABLE ($ptascii("right")) ' + str(line)
    marker = lambda stage: 'CONCAT_ARRAY_LEFT_WARNING porigin_parent poperand_left poperand_right n_right ' + str(line) + ' ' + str(stage)
    consumer = 'CONCAT_AFTER_LEFT porigin_parent poperand_right false ' + str(line)
    valid = lambda state, stage: '$concat_array_left_valid(' + state + ', porigin_parent, poperand_left, poperand_right, n_right, ' + str(line) + ', ' + str(stage) + ')'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $concat_array_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]', '$concat_array_frontier(S_entry, 0)',
        'S_entry.ORIGIN = (porigin_parent)',
        'poperand_left = ' + left, 'poperand_right = ' + right,
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'S_entry.STORE[n_left] = DEFINED (PARRAY n_array)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
        '~(n_left <- S_entry.REFCELLS)', '~(n_right <- S_entry.REFCELLS)',
        '$concat_array_plan(S_entry) = ((porigin_child, ' + marker(0) + ', ' + consumer + '))',
        '$origin_child((porigin_parent), [PCFIELD 0]) = (porigin_child)',
        '$concat_array_source(S_entry, porigin_parent, poperand_left, poperand_right, ' + str(line) + ')',
        '$concat_array_string(S_entry, poperand_right) = (n_right, pvalue_before)',
        '$string_bytes(pvalue_before) = ($ptascii("before"))',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_array) = 1',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$concat_array_plan(S_entry[.STORE[n_right] = UNDEFINED]) = eps',
        '$concat_array_plan(S_entry[.REFCELLS = S_entry.REFCELLS ++ [n_right]]) = eps',
        'S_capture_budget = $drive_steps(S_entry, 1)', 'S_capture_budget.COMPLETION = BUDGET',
        'S_capture = S_capture_budget[.COMPLETION = NORMAL]', '$concat_array_frontier(S_capture, 1)',
        'S_capture.ORIGIN = (porigin_child)',
        'S_capture.TODO = (' + marker(0) + ') :: (' + consumer + ') :: ptask_tail*',
        'S_capture.RESULT = KNOWN PNULL', 'S_capture.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_capture.STORE = S_entry.STORE', 'S_capture.ARRAYS = S_entry.ARRAYS',
        'S_capture.ALLOCATIONS = S_entry.ALLOCATIONS',
        '$task_nodes(' + marker(0) + ') = eps',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HARRAY n_array) = 1',
        valid('S_capture', 0), '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
        'S_bad_stage = S_capture[.TODO = (CONCAT_ARRAY_LEFT_WARNING porigin_parent poperand_left poperand_right n_right ' + str(line) + ' 2) :: (' + consumer + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_bad_stage))', '~$call_descriptors_valid(S_bad_stage)',
        'S_bad_consumer = S_capture[.TODO = (' + marker(0) + ') :: (CONCAT_AFTER_LEFT porigin_parent poperand_left false ' + str(line) + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_bad_consumer))', '~$call_descriptors_valid(S_bad_consumer)',
        'S_bad_cell = S_capture[.TODO = (CONCAT_ARRAY_LEFT_WARNING porigin_parent poperand_left poperand_right n_left ' + str(line) + ' 0) :: (' + consumer + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_bad_cell))', '~$call_descriptors_valid(S_bad_cell)',
        'S_bad_source = S_capture[.TODO = (CONCAT_ARRAY_LEFT_WARNING porigin_child poperand_left poperand_right n_right ' + str(line) + ' 0) :: (' + consumer + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_bad_source))', '~$call_descriptors_valid(S_bad_source)',
        'S_dispatch_budget = $drive_steps(S_capture, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]', '$concat_array_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: (' + consumer + ') :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(1), 'perrorcall.TARGET = eps',
        'perrorcall.SITE = porigin_child', 'perrorcall.LINE = ' + str(line),
        '$error_call_valid(S_dispatch, perrorcall)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'perrorcall_bad = perrorcall[.MESSAGE = eps][.EVENT = DIAGNOSTIC "Warning" eps ' + str(line) + ']',
        'S_bad_message = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall_bad) :: (' + consumer + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_bad_message))', '~$error_call_valid(S_bad_message, perrorcall_bad)', '~$call_descriptors_valid(S_bad_message)',
        'S_entered_found = $concat_array_seek(S_dispatch, 3, 2000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', '$concat_array_frontier(S_entered, 3)',
        'S_entered.FRAMES = pframe :: pframe_tail*', '$concat_array_handler_frame(pframe)',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: (' + consumer + ') :: ptask_saved*',
        'perrorcall_entered.RESUME = ' + marker(1), 'perrorcall_entered.TARGET =/= eps',
        '$heap_owners($heap_prune($heap_graph(S_entered)), HARRAY n_array) = 1',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if thrown:
        checks += [
            '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
            'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            '~$concat_array_right_cell(S_entry[.STORE[n_right] = DEFINED (POBJECT n_second)], poperand_right, n_right)',
            'S_throw_found = $concat_array_seek(S_entered, 6, 2000)',
            r'S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET',
            'S_throw = S_throw_found[.COMPLETION = NORMAL]', '$concat_array_frontier(S_throw, 6)',
            'S_throw.TODO = (THROW_SEARCH n_second) :: ptask_throw*',
            'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps',
            '~$concat_array_tasks(S_throw.TODO)', '~$concat_array_legacy(S_throw.TODO)',
            '$lookup(S_throw.ENV, $ptascii("left")) = eps',
            '$concat_array_string(S_throw, poperand_right) = (n_right, pvalue_after)',
            '$string_bytes(pvalue_after) = ($ptascii("after"))',
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
            'S_return_found = $concat_array_seek(S_entered, 4, 2000)',
            r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
            'S_return = S_return_found[.COMPLETION = NORMAL]', '$concat_array_frontier(S_return, 4)',
            'S_return.TODO = (' + marker(1) + ') :: (' + consumer + ') :: ptask_tail*',
            '$lookup(S_return.ENV, $ptascii("left")) = eps',
            'S_return.STORE[n_v] = DEFINED (PINT 100)',
            '$concat_array_string(S_return, poperand_right) = (n_right, pvalue_after)',
            '$string_bytes(pvalue_after) = ($ptascii("after"))',
            '~$array_string_cast_snapshot(S_return, poperand_left)', valid('S_return', 1),
            '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_array) = 0',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
            'S_pruned = S_return[.ALLOCATIONS = eps]',
            valid('S_pruned', 1), '~$concat_array_right_cell(S_pruned, poperand_right, n_right)',
            '~$concat_array_right_cell(S_return[.ENV = eps][.GLOBALTABLE = eps], poperand_right, n_right)',
            '~$concat_array_right_cell(S_return[.REFCELLS = S_return.REFCELLS ++ [n_right]], poperand_right, n_right)',
            '~$concat_array_right_cell(S_return[.STORE[n_right] = UNDEFINED], poperand_right, n_right)',
            '~$concat_array_right_cell(S_return[.STORE[n_right] = DEFINED (PINT 5)], poperand_right, n_right)',
            'S_rebound = S_return[.ENV = [BIND ($ptascii("right")) n_v]][.STORE[n_v] = DEFINED pvalue_after]',
            '$concat_array_string(S_rebound, poperand_right) = (n_v, pvalue_after)',
            '~$concat_array_right_cell(S_rebound, poperand_right, n_right)',
            'S_result_budget = $drive_steps(S_return, 1)', 'S_result_budget.COMPLETION = BUDGET',
            'S_result = S_result_budget[.COMPLETION = NORMAL]', '$concat_array_frontier(S_result, 5)',
            'S_result.TODO = (' + consumer + ') :: ptask_tail*',
            'S_result.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("Array")))',
            'S_result.STORE = S_return.STORE', 'S_result.ARRAYS = S_return.ARRAYS',
            'S_result.ALLOCATIONS = S_return.ALLOCATIONS', 'S_result.EVENTS = S_return.EVENTS',
            'S_result.STORE[n_v] = DEFINED (PINT 100)',
            '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
            'S_concat_budget = $drive_steps(S_result, 2)', 'S_concat_budget.COMPLETION = BUDGET',
            'S_concat = S_concat_budget[.COMPLETION = NORMAL]',
            'S_concat.RESULT = KNOWN pvalue_concat', '$string_bytes(pvalue_concat) = ($ptascii("Arrayafter"))',
            'S_concat.STORE[n_v] = DEFINED (PINT 100)',
            '~$concat_array_tasks(S_concat.TODO)', '~$concat_array_legacy(S_concat.TODO)',
            '$call_descriptors_valid(S_concat)', '$heap_valid($heap_graph(S_concat))',
            'S_done = $drive_steps(S_concat, 2000)', '$drive_steps(S_return, 2000) = S_done',
            'S_done.STORE[n_v] = DEFINED pvalue_concat',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("left")) = eps',
        '$concat_array_string(S_done, poperand_right) = (n_right, pvalue_after)',
        '$string_bytes(pvalue_after) = ($ptascii("after"))',
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
    report['concat_array_inputs'] = before
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
