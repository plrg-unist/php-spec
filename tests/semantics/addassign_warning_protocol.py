#!/usr/bin/env python3
"""Production compound ADD selected target, warning, store and throw fronts."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import addassign_warning_cases as cases
import arithmetic_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $addassign_task(ptask) : bool
def $addassign_task(ARITHMETIC_ADDASSIGN_WARNING pintegeroperation pvalue pnumber n) = true
def $addassign_task(ERROR_HANDLER_INVOKE perrorcall) = $addassign_task(perrorcall.RESUME)
def $addassign_task(ERROR_HANDLER_RESULT perrorcall) = $addassign_task(perrorcall.RESUME)
def $addassign_task(ERROR_HANDLER_CLEAN perrorcall) = $addassign_task(perrorcall.RESUME)
def $addassign_task(ptask) = false -- otherwise
dec $addassign_tasks(ptask*) : bool
def $addassign_tasks(eps) = false
def $addassign_tasks(ptask :: ptask_tail*) = ($addassign_task(ptask) \/ $addassign_tasks(ptask_tail*))
dec $addassign_handler_frame(pframe) : bool
def $addassign_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_ADDASSIGN_WARNING pintegeroperation pvalue pnumber 1
  -- if perrorcall.TARGET =/= eps
def $addassign_handler_frame(pframe) = false -- otherwise
dec $addassign_entered(pframe*) : bool
def $addassign_entered(eps) = false
def $addassign_entered(pframe :: pframe_tail*) = ($addassign_handler_frame(pframe) \/ $addassign_entered(pframe_tail*))
dec $addassign_numeric_operand(poperand) : bool
def $addassign_numeric_operand(KNOWN (PINT i)) = true
def $addassign_numeric_operand(KNOWN (PFLOAT n)) = true
def $addassign_numeric_operand(poperand) = false -- otherwise
dec $addassign_frontier(pstate, nat) : bool
def $addassign_frontier(S, 0) = ($arithmetic_addassign_plan(S) =/= eps)
def $addassign_frontier(S, 1) = true
  -- if S.TODO = (ARITHMETIC_ADDASSIGN_WARNING pintegeroperation pvalue pnumber 0) :: ptask_tail*
def $addassign_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_ADDASSIGN_WARNING pintegeroperation pvalue pnumber 1
  -- if perrorcall.TARGET = eps
def $addassign_frontier(S, 3) = (S.CURRENT =/= eps /\ $addassign_entered(S.FRAMES))
def $addassign_frontier(S, 4) = true
  -- if S.TODO = (ARITHMETIC_ADDASSIGN_WARNING pintegeroperation pvalue pnumber 1) :: ptask_tail*
def $addassign_frontier(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (pcnode)
  -- if pcnode = NExprAssignOpPlus expression_left expression_right metadata
  -- if $addassign_numeric_operand(S.RESULT)
  -- if ~$addassign_tasks(S.TODO)
def $addassign_frontier(S, 6) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if ~$addassign_tasks(S.TODO)
def $addassign_frontier(S, n) = false -- otherwise
dec $addassign_seek(pstate, nat, nat) : pstate
def $addassign_seek(S, n_stage, n) = S -- if $addassign_frontier(S, n_stage)
def $addassign_seek(S, n_stage, n) = S
  -- if ~$addassign_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $addassign_seek(S, n_stage, n) = S
  -- if ~$addassign_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $addassign_seek(S, n_stage, n) = $addassign_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$addassign_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''

def conditions(name, program, path, stdout):
    thrown = name == 'addassign-leading-handler-throw'
    line = 12 if thrown else 11
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $addassign_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]', '$addassign_frontier(S_entry, 0)',
        '$arithmetic_addassign_plan(S_entry) = ((pintegeroperation, pvalue, NINT 12))',
        'pintegeroperation.OP = ADD', '~pintegeroperation.SWAPPED',
        'pintegeroperation.LINE = ' + str(line),
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) ' + str(line),
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) ' + str(line),
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_left',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_right', 'n_left =/= n_right',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$string_bytes(pvalue) = ($ptascii("12tail"))',
        'S_entry.STORE[n_left] = DEFINED pvalue',
        'S_entry.STORE[n_right] = DEFINED (PINT 2)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '$arithmetic_addassign_source(S_entry, pintegeroperation)',
        '$arithmetic_add_selected(S_entry, pintegeroperation)',
        '$arithmetic_addassign_ready(S_entry, pintegeroperation) = (NINT 2)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 2',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$arithmetic_addassign_plan(S_entry[.RESULT = KNOWN PNULL]) = eps',
        '$arithmetic_addassign_plan(S_entry[.STORE[n_left] = UNDEFINED]) = eps',
        '~$arithmetic_addassign_source(S_entry, pintegeroperation[.OP = DIVIDE])',
        '~$arithmetic_addassign_source(S_entry, pintegeroperation[.LINE = $(pintegeroperation.LINE + 1)])',
        '~$arithmetic_addassign_source(S_entry, pintegeroperation[.LEFT = VARIABLE ($ptascii("v")) ' + str(line) + '])',
        '~$arithmetic_addassign_source(S_entry[.ORIGIN = eps], pintegeroperation)',
        '~$arithmetic_addassign_source(S_entry[.CODE = eps], pintegeroperation)',
        'S_capture_budget = $drive_steps(S_entry, 1)', 'S_capture_budget.COMPLETION = BUDGET',
        'S_capture = S_capture_budget[.COMPLETION = NORMAL]', '$addassign_frontier(S_capture, 1)',
        'S_capture.TODO = (ARITHMETIC_ADDASSIGN_WARNING pintegeroperation pvalue (NINT 12) 0) :: ptask_tail*',
        'S_capture.RESULT = KNOWN PNULL', 'S_capture.LOCATION = ROOT n_left',
        'S_capture.STORE = S_entry.STORE', 'S_capture.ALLOCATIONS = S_entry.ALLOCATIONS',
        'S_capture.EVENTS = S_entry.EVENTS',
        '$task_nodes(ARITHMETIC_ADDASSIGN_WARNING pintegeroperation pvalue (NINT 12) 0) = eps',
        '$arithmetic_addassign_warning_valid(S_capture, pintegeroperation, pvalue, NINT 12, 0)',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
        'pvalue_bad = PSTRING ($ptascii("99tail"))',
        '~$arithmetic_addassign_warning_valid(S_capture, pintegeroperation, pvalue_bad, NINT 99, 0)',
        '~$arithmetic_addassign_warning_valid(S_capture, pintegeroperation, pvalue, NINT 13, 0)',
        '~$arithmetic_addassign_warning_valid(S_capture, pintegeroperation, pvalue, NINT 12, 2)',
        'S_capture_bad = S_capture[.TODO = (ARITHMETIC_ADDASSIGN_WARNING pintegeroperation pvalue_bad (NINT 99) 0) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_capture_bad))', '~$call_descriptors_valid(S_capture_bad)',
        'pintegeroperation_bad = pintegeroperation[.LEFTPOINTER = pintegeroperation.RIGHTPOINTER]',
        'S_pointer_bad = S_capture[.TODO = (ARITHMETIC_ADDASSIGN_WARNING pintegeroperation_bad pvalue (NINT 12) 0) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_pointer_bad))', '~$call_descriptors_valid(S_pointer_bad)',
        'S_dispatch_budget = $drive_steps(S_capture, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]', '$addassign_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.TARGET = eps',
        'perrorcall.RESUME = ARITHMETIC_ADDASSIGN_WARNING pintegeroperation pvalue (NINT 12) 1',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'perrorcall_bad = perrorcall[.RESUME = ARITHMETIC_ADDASSIGN_WARNING pintegeroperation pvalue_bad (NINT 99) 1]',
        '~$error_call_valid(S_dispatch, perrorcall_bad)',
        'S_dispatch_bad = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall_bad) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_dispatch_bad))', '~$call_descriptors_valid(S_dispatch_bad)',
        'perrorcall_message_bad = perrorcall[.MESSAGE = eps][.EVENT = DIAGNOSTIC "Warning" eps ' + str(line) + ']',
        '~$error_call_valid(S_dispatch, perrorcall_message_bad)',
        'S_message_bad = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall_message_bad) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_message_bad))', '~$call_descriptors_valid(S_message_bad)',
        'S_entered_found = $addassign_seek(S_dispatch, 3, 2000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', '$addassign_frontier(S_entered, 3)',
        'S_entered.FRAMES = pframe :: pframe_tail*', '$addassign_handler_frame(pframe)',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_saved*',
        'perrorcall_entered.RESUME = ARITHMETIC_ADDASSIGN_WARNING pintegeroperation pvalue (NINT 12) 1',
        'perrorcall_entered.TARGET =/= eps',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if thrown:
        checks += [
            '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
            'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            'S_owning = S_capture[.STORE[n_left] = DEFINED (POBJECT n_second)]',
            '$heap_valid($heap_graph(S_owning))',
            '$arithmetic_addassign_ready(S_owning, pintegeroperation) = eps',
            'S_throw_found = $addassign_seek(S_entered, 6, 2000)',
            r'S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET',
            'S_throw = S_throw_found[.COMPLETION = NORMAL]', '$addassign_frontier(S_throw, 6)',
            'S_throw.TODO = (THROW_SEARCH n_second) :: ptask_throw*',
            'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps', '~$addassign_tasks(S_throw.TODO)',
            'S_throw.STORE[n_left] = DEFINED (PINT 99)',
            'S_throw.STORE[n_right] = DEFINED (PINT 5)',
            'S_throw.STORE[n_v] = DEFINED (PINT 100)',
            '$throwable_live(S_throw, n_second)', '$throwable_previous_id(S_throw, n_second) = eps',
            '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_left) = 2',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_right) = 2',
            'S_throw.ERRORHANDLER = S_entry.ERRORHANDLER',
            '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
            'S_done = $drive_steps(S_throw, 2000)', '$drive_steps(S_dispatch, 2000) = S_done',
        ]
    else:
        checks += [
            'S_return_found = $addassign_seek(S_entered, 4, 2000)',
            r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
            'S_return = S_return_found[.COMPLETION = NORMAL]', '$addassign_frontier(S_return, 4)',
            'S_return.TODO = (ARITHMETIC_ADDASSIGN_WARNING pintegeroperation pvalue (NINT 12) 1) :: ptask_tail*',
            'S_return.STORE[n_left] = DEFINED (PINT 99)',
            'S_return.STORE[n_right] = DEFINED (PINT 5)',
            'S_return.STORE[n_v] = DEFINED (PINT 100)',
            '$arithmetic_addassign_warning_valid(S_return, pintegeroperation, pvalue, NINT 12, 1)',
            '$arithmetic_addassign_ready(S_return, pintegeroperation) = (NINT 5)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_left) = 2',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 2',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
            '$arithmetic_addassign_ready(S_return[.STORE[n_left] = UNDEFINED], pintegeroperation) = eps',
            '$arithmetic_addassign_ready(S_return[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)], pintegeroperation) = eps',
            '$arithmetic_addassign_ready(S_return, pintegeroperation[.LEFTPOINTER = INTEGER_CELL (|S_return.STORE|)]) = eps',
            # A pure PROPREF-presence projection, not an authenticated typed source or driven state.
            '$arithmetic_addassign_ready(S_return[.PROPREFS = [{CELL n_left, SOURCES eps}]], pintegeroperation) = eps',
            '$arithmetic_addassign_ready(S_return[.STORE[n_right] = DEFINED (PSTRING ($ptascii("5tail")))], pintegeroperation) = eps',
            '$arithmetic_addassign_ready(S_return[.STORE[n_right] = DEFINED (PSTRING ($ptascii("notnumeric")))], pintegeroperation) = eps',
            'S_result_budget = $drive_steps(S_return, 1)', 'S_result_budget.COMPLETION = BUDGET',
            'S_result = S_result_budget[.COMPLETION = NORMAL]', '$addassign_frontier(S_result, 5)',
            'S_result.RESULT = KNOWN (PINT 17)', 'S_result.TODO = ptask_tail*',
            'S_result.LOCATION = ROOT n_left', '~$addassign_tasks(S_result.TODO)',
            'S_expected = S_return[.STORE[n_left] = DEFINED (PINT 17)]',
            'S_result.STORE = S_expected.STORE', 'S_result.ENV = S_return.ENV',
            'S_result.ALLOCATIONS = S_return.ALLOCATIONS', 'S_result.OBJECTS = S_return.OBJECTS',
            'S_result.STORE[n_v] = DEFINED (PINT 100)',
            '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
            'S_done = $drive_steps(S_result, 2000)', '$drive_steps(S_return, 2000) = S_done',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
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
    report['addassign_inputs'] = before
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
