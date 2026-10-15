#!/usr/bin/env python3
"""Source-reached concatenation assignment cache, commit and cancellation fronts."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import concatassign_array_warning_cases as cases
import arithmetic_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $concatassign_array_task(ptask) : bool
def $concatassign_array_task(CONCATASSIGN_ARRAY_WARNING porigin poperand_left poperand_right pvalue z n) = true
def $concatassign_array_task(ERROR_HANDLER_INVOKE perrorcall) = $concatassign_array_task(perrorcall.RESUME)
def $concatassign_array_task(ERROR_HANDLER_RESULT perrorcall) = $concatassign_array_task(perrorcall.RESUME)
def $concatassign_array_task(ERROR_HANDLER_CLEAN perrorcall) = $concatassign_array_task(perrorcall.RESUME)
def $concatassign_array_task(ptask) = false -- otherwise
dec $concatassign_array_tasks(ptask*) : bool
def $concatassign_array_tasks(eps) = false
def $concatassign_array_tasks(ptask :: ptask_tail*) = ($concatassign_array_task(ptask) \/ $concatassign_array_tasks(ptask_tail*))
dec $concatassign_array_handler_frame(pframe) : bool
def $concatassign_array_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CONCATASSIGN_ARRAY_WARNING porigin poperand_left poperand_right pvalue z 1
  -- if perrorcall.TARGET =/= eps
def $concatassign_array_handler_frame(pframe) = false -- otherwise
dec $concatassign_array_entered(pframe*) : bool
def $concatassign_array_entered(eps) = false
def $concatassign_array_entered(pframe :: pframe_tail*) = ($concatassign_array_handler_frame(pframe) \/ $concatassign_array_entered(pframe_tail*))
dec $concatassign_array_frontier(pstate, nat) : bool
def $concatassign_array_frontier(S, 0) = ($concatassign_array_plan(S) =/= eps)
def $concatassign_array_frontier(S, 1) = true
  -- if S.TODO = (CONCATASSIGN_ARRAY_WARNING porigin poperand_left poperand_right pvalue z 0) :: ptask_tail*
def $concatassign_array_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CONCATASSIGN_ARRAY_WARNING porigin poperand_left poperand_right pvalue z 1
  -- if perrorcall.TARGET = eps
def $concatassign_array_frontier(S, 3) = (S.CURRENT =/= eps /\ $concatassign_array_entered(S.FRAMES))
def $concatassign_array_frontier(S, 4) = true
  -- if S.TODO = (CONCATASSIGN_ARRAY_WARNING porigin poperand_left poperand_right pvalue z 1) :: ptask_tail*
def $concatassign_array_frontier(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprAssignOpConcat expression_left expression_right metadata)
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) =/= eps
  -- if ~$concatassign_array_tasks(S.TODO)
def $concatassign_array_frontier(S, 6) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if ~$concatassign_array_tasks(S.TODO)
def $concatassign_array_frontier(S, n) = false -- otherwise
dec $concatassign_array_seek(pstate, nat, nat) : pstate
def $concatassign_array_seek(S, n_stage, n) = S -- if $concatassign_array_frontier(S, n_stage)
def $concatassign_array_seek(S, n_stage, n) = S
  -- if ~$concatassign_array_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $concatassign_array_seek(S, n_stage, n) = S
  -- if ~$concatassign_array_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $concatassign_array_seek(S, n_stage, n) = $concatassign_array_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$concatassign_array_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    thrown = name.endswith('-throw')
    line = 15 if thrown else 13
    def marker(stage, value='pvalue_cached', origin='porigin', diagnostic=line):
        return f'CONCATASSIGN_ARRAY_WARNING {origin} poperand_left poperand_right {value} {diagnostic} {stage}'
    def valid(state, stage):
        return f'$concatassign_array_valid({state}, porigin, poperand_left, poperand_right, pvalue_cached, {line}, {stage})'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $concatassign_array_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]', '$concatassign_array_frontier(S_entry, 0)',
        '$concatassign_array_plan(S_entry) = (' + marker(0) + ')',
        'poperand_left = VARIABLE ($ptascii("left")) ' + str(line - 1),
        'poperand_right = VARIABLE ($ptascii("right")) ' + str(line),
        'pvalue_cached = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("before"))',
        'S_entry.STRINGDATA[n_string] = $ptascii("before")',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'S_entry.STORE[n_left] = DEFINED pvalue_cached',
        'S_entry.STORE[n_right] = DEFINED (PARRAY n_array)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '~(n_left <- S_entry.REFCELLS)', '~(n_right <- S_entry.REFCELLS)',
        'S_entry.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
        '$concatassign_array_source(S_entry, porigin, poperand_left, poperand_right, ' + str(line) + ')',
        '$concatassign_array_ready(S_entry, poperand_left)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_array) = 1',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$concatassign_array_plan(S_entry[.RESULT = KNOWN (PARRAY n_array)]) = eps',
        '$concatassign_array_plan(S_entry[.REFCELLS = S_entry.REFCELLS ++ [n_left]]) = eps',
        '$concatassign_array_plan(S_entry[.GC.IMMUTABLE = S_entry.GC.IMMUTABLE ++ [n_array]]) = eps',
        'S_capture_budget = $drive_steps(S_entry, 1)', 'S_capture_budget.COMPLETION = BUDGET',
        'S_capture = S_capture_budget[.COMPLETION = NORMAL]', '$concatassign_array_frontier(S_capture, 1)',
        'S_capture.TODO = (' + marker(0) + ') :: ptask_tail*',
        'S_capture.RESULT = KNOWN PNULL', 'S_capture.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_capture.LOCATION = ROOT n_left', '$task_nodes(' + marker(0) + ') = eps',
        valid('S_capture', 0), '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
        'pvalue_bad = PSTRING_CARRIER INTERNED_STRING ($ptascii("wrong"))',
        'S_cache_bad = S_capture[.TODO = (' + marker(0, 'pvalue_bad') + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_cache_bad))', '~$call_descriptors_valid(S_cache_bad)',
        'pvalue_flip = PSTRING_CARRIER INTERNED_STRING ($ptascii("before"))',
        'S_carrier_bad = S_capture[.TODO = (' + marker(0, 'pvalue_flip') + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_carrier_bad))', '~$call_descriptors_valid(S_carrier_bad)',
        '(porigin_child) = $origin_child((porigin), [PCFIELD 1])',
        'S_source_bad = S_capture[.ORIGIN = (porigin_child)][.TODO = (' + marker(0, origin='porigin_child') + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_source_bad))', '~$call_descriptors_valid(S_source_bad)',
        'S_line_bad = S_capture[.TODO = (' + marker(0, diagnostic=line - 1) + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_line_bad))', '~$call_descriptors_valid(S_line_bad)',
        'S_stage_bad = S_capture[.TODO = (' + marker(2) + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_stage_bad))', '~$call_descriptors_valid(S_stage_bad)',
        'S_dispatch_budget = $drive_steps(S_capture, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]', '$concatassign_array_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(1), 'perrorcall.TARGET = eps',
        'perrorcall.SITE = porigin', 'perrorcall.LINE = ' + str(line),
        '$error_call_valid(S_dispatch, perrorcall)', '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'perrorcall_cache_bad = perrorcall[.RESUME = ' + marker(1, 'pvalue_bad') + ']',
        'S_dispatch_bad = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall_cache_bad) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_dispatch_bad))', '~$error_call_valid(S_dispatch_bad, perrorcall_cache_bad)', '~$call_descriptors_valid(S_dispatch_bad)',
        'perrorcall_message_bad = perrorcall[.MESSAGE = eps][.EVENT = DIAGNOSTIC "Warning" eps ' + str(line) + ']',
        'S_message_bad = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall_message_bad) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_message_bad))', '~$error_call_valid(S_message_bad, perrorcall_message_bad)', '~$call_descriptors_valid(S_message_bad)',
        'S_entered_found = $concatassign_array_seek(S_dispatch, 3, 2000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', '$concatassign_array_frontier(S_entered, 3)',
        'S_entered.FRAMES = pframe :: pframe_tail*', '$concatassign_array_handler_frame(pframe)',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_saved*',
        'perrorcall_entered.RESUME = ' + marker(1), 'perrorcall_entered.TARGET =/= eps',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if thrown:
        checks += [
            '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
            'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            'S_owning = S_capture[.STORE[n_left] = DEFINED (POBJECT n_second)]',
            '$heap_valid($heap_graph(S_owning))', '~$concatassign_array_ready(S_owning, poperand_left)',
            'S_throw_found = $concatassign_array_seek(S_entered, 6, 2000)',
            r'S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET',
            'S_throw = S_throw_found[.COMPLETION = NORMAL]', '$concatassign_array_frontier(S_throw, 6)',
            'S_throw.TODO = (THROW_SEARCH n_second) :: ptask_throw*',
            'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps', '~$concatassign_array_tasks(S_throw.TODO)',
            '$lookup(S_throw.ENV, $ptascii("left")) = (n_left)',
            '$lookup(S_throw.ENV, $ptascii("alias")) = (n_left)',
            'n_left <- S_throw.REFCELLS', '$lookup(S_throw.ENV, $ptascii("right")) = eps',
            'S_throw.STORE[n_left] = DEFINED pvalue_after', '$string_bytes(pvalue_after) = ($ptascii("after"))',
            'S_throw.STORE[n_v] = DEFINED (PINT 100)',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HARRAY n_array) = 0',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_left) = 2',
            '$throwable_live(S_throw, n_second)', '$throwable_previous_id(S_throw, n_second) = eps',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
            'S_throw.ERRORHANDLER = S_entry.ERRORHANDLER',
            '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
            'S_done = $drive_steps(S_throw, 2000)', '$drive_steps(S_dispatch, 2000) = S_done',
            '$lookup(S_done.ENV, $ptascii("left")) = (n_left)', '$lookup(S_done.ENV, $ptascii("alias")) = (n_left)',
            'S_done.STORE[n_left] = DEFINED pvalue_later', '$string_bytes(pvalue_later) = ($ptascii("later"))',
            'S_done.STORE[n_v] = DEFINED (PINT 100)',
        ]
    else:
        checks += [
            'S_return_found = $concatassign_array_seek(S_entered, 4, 2000)',
            r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
            'S_return = S_return_found[.COMPLETION = NORMAL]', '$concatassign_array_frontier(S_return, 4)',
            'S_return.TODO = (' + marker(1) + ') :: ptask_tail*',
            '$lookup(S_return.ENV, $ptascii("left")) = (n_left)', '$lookup(S_return.ENV, $ptascii("right")) = eps',
            'S_return.STORE[n_left] = DEFINED pvalue_after', '$string_bytes(pvalue_after) = ($ptascii("after"))',
            'S_return.STORE[n_v] = DEFINED (PINT 100)', valid('S_return', 1), '~' + valid('S_return', 0),
            '$concatassign_array_ready(S_return, poperand_left)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_array) = 0',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
            '~$concatassign_array_ready(S_return[.STORE[n_left] = UNDEFINED], poperand_left)',
            '~$concatassign_array_ready(S_return[.ENV = eps][.GLOBALTABLE = eps], poperand_left)',
            # Pure allocation-only projection; no heap-valid or execution claim.
            '~$concatassign_array_ready(S_return[.ALLOCATIONS = eps], poperand_left)',
            # Pure PROPREF-presence projection; no authenticated typed target or execution claim.
            '~$concatassign_array_ready(S_return[.PROPREFS = [{CELL n_left, SOURCES eps}]], poperand_left)',
            'S_result_budget = $drive_steps(S_return, 1)', 'S_result_budget.COMPLETION = BUDGET',
            'S_result = S_result_budget[.COMPLETION = NORMAL]', '$concatassign_array_frontier(S_result, 5)',
            'S_result.TODO = ptask_tail*',
            'S_result.RESULT = KNOWN pvalue_result',
            'pvalue_result = PSTRING_CARRIER (REQUEST_STRING n_result) ($ptascii("beforeArray"))',
            'n_result = |S_return.STRINGDATA|',
            'S_result.STRINGDATA = S_return.STRINGDATA ++ [$ptascii("beforeArray")]',
            '$lookup(S_result.ENV, $ptascii("left")) = (n_left)',
            'S_result.LOCATION = ROOT n_left', 'S_result.CELL = n_left',
            'S_expected_store = S_return[.STORE[n_left] = DEFINED pvalue_result]',
            'S_result.STORE = S_expected_store.STORE', 'S_result.ARRAYS = S_return.ARRAYS',
            'S_result.OBJECTS = S_return.OBJECTS', 'S_result.EVENTS = S_return.EVENTS',
            'S_result.STORE[n_v] = DEFINED (PINT 100)',
            '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
            'S_done = $drive_steps(S_result, 2000)', '$drive_steps(S_return, 2000) = S_done',
            'S_done.STORE[n_left] = DEFINED pvalue_result', 'S_done.STORE[n_v] = DEFINED pvalue_result',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("right")) = eps',
        '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_array) = 0',
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
    report['concatassign_array_inputs'] = before
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
