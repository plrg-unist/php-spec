#!/usr/bin/env python3
"""Reached SUB/MUL scalar holders, selected cells and abrupt continuations."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import submul_warning_cases as cases
import arithmetic_warning_protocol as shared
import integer_operator_warning_protocol as prior

CASES = ('submul-sub-cached', 'submul-mul-second-throw')
HELPERS = prior.HELPERS + r'''

dec $submul_task(ptask) : bool
def $submul_task(SUBMUL_CONVERT pintegeroperation parithmeticphase) = true
def $submul_task(SUBMUL_WARNING pintegeroperation parithmeticphase pvalue pnumber n) = true
def $submul_task(ERROR_HANDLER_INVOKE perrorcall) = $submul_task(perrorcall.RESUME)
def $submul_task(ERROR_HANDLER_RESULT perrorcall) = $submul_task(perrorcall.RESUME)
def $submul_task(ERROR_HANDLER_CLEAN perrorcall) = $submul_task(perrorcall.RESUME)
def $submul_task(ptask) = false -- otherwise
dec $submul_tasks(ptask*) : bool
def $submul_tasks(eps) = false
def $submul_tasks(ptask :: ptask_tail*) = ($submul_task(ptask) \/ $submul_tasks(ptask_tail*))

dec $submul_frame(pframe, nat) : bool
def $submul_frame(pframe, 0) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.TARGET =/= eps
  -- if perrorcall.RESUME = SUBMUL_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 1
def $submul_frame(pframe, 1) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.TARGET =/= eps
  -- if perrorcall.RESUME = SUBMUL_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue pnumber_right 1
def $submul_frame(pframe, n) = false -- otherwise
dec $submul_entered(pframe*, nat) : bool
def $submul_entered(eps, n) = false
def $submul_entered(pframe :: pframe_tail*, n) = ($submul_frame(pframe, n) \/ $submul_entered(pframe_tail*, n))

dec $submul_frontier(pstate, nat) : bool
def $submul_frontier(S, 0) = ($submul_warning_plan(S) =/= eps)
def $submul_frontier(S, 1) = true
  -- if S.TODO = (SUBMUL_CONVERT pintegeroperation ARITHMETIC_LEFT) :: ptask_tail*
def $submul_frontier(S, 2) = true
  -- if S.TODO = (SUBMUL_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 0) :: ptask_tail*
def $submul_frontier(S, 3) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = SUBMUL_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 1
  -- if perrorcall.TARGET = eps
def $submul_frontier(S, 4) = true
  -- if S.TODO = (SUBMUL_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 1) :: ptask_tail*
def $submul_frontier(S, 5) = true
  -- if S.TODO = (SUBMUL_CONVERT pintegeroperation (ARITHMETIC_RIGHT pnumber)) :: ptask_tail*
def $submul_frontier(S, 6) = true
  -- if S.TODO = (SUBMUL_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue pnumber_right 0) :: ptask_tail*
def $submul_frontier(S, 7) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = SUBMUL_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue pnumber_right 1
  -- if perrorcall.TARGET = eps
def $submul_frontier(S, 8) = true
  -- if S.TODO = (SUBMUL_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue pnumber_right 1) :: ptask_tail*
def $submul_frontier(S, 9) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if ~$submul_tasks(S.TODO)
def $submul_frontier(S, 10) = (S.CURRENT =/= eps /\ $submul_entered(S.FRAMES, 0))
def $submul_frontier(S, 11) = (S.CURRENT =/= eps /\ $submul_entered(S.FRAMES, 1))
def $submul_frontier(S, n) = false -- otherwise
dec $submul_seek(pstate, nat, nat) : pstate
def $submul_seek(S, n_stage, n) = S -- if $submul_frontier(S, n_stage)
def $submul_seek(S, n_stage, n) = S
  -- if ~$submul_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $submul_seek(S, n_stage, n) = S
  -- if ~$submul_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $submul_seek(S, n_stage, n) = $submul_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$submul_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    thrown = name == CASES[1]
    operation = 'MULTIPLY' if thrown else 'SUBTRACT'
    left = lambda stage: f'SUBMUL_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_left (NINT 12) {stage}'
    right = lambda stage: f'SUBMUL_WARNING pintegeroperation (ARITHMETIC_RIGHT (NINT 12)) pvalue_right (NINT 5) {stage}'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_entry_found = $submul_seek(S_initial, 0, 5000)',
        r'S_entry_found.COMPLETION = NORMAL \/ S_entry_found.COMPLETION = BUDGET',
        'S_entry = S_entry_found[.COMPLETION = NORMAL]', '$submul_frontier(S_entry, 0)',
        '$submul_warning_plan(S_entry) = (pintegeroperation)', '$submul_valid(S_entry, pintegeroperation)',
        'pintegeroperation.OP = ' + operation, '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23', 'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_left', 'pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_right', 'n_left =/= n_right',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)', '$lookup(S_entry.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)', '$lookup(S_entry.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)', '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("supplied")) = (n_supplied_cell)', 'S_entry.STORE[n_supplied_cell] = DEFINED (POBJECT n_supplied)',
        'n_left <- S_entry.REFCELLS', 'n_right <- S_entry.REFCELLS',
        'S_entry.STORE[n_left] = DEFINED pvalue_left', '$string_bytes(pvalue_left) = ($ptascii("12tail"))',
        'S_entry.STORE[n_right] = DEFINED pvalue_initial_right',
        'pvalue_initial_right = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("bad5"))',
        'S_entry.STRINGDATA[n_string] = $ptascii("bad5")', '$submul_initial_value(S_entry, pvalue_initial_right)',
        '$arithmetic_add_conversion(pvalue_initial_right) = eps',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)', 'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 2', '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 2',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'S_begin_budget = $drive_steps(S_entry, 1)', 'S_begin_budget.COMPLETION = BUDGET',
        'S_begin = S_begin_budget[.COMPLETION = NORMAL]', '$submul_frontier(S_begin, 1)',
        'S_entry.TODO = ptask_old :: ptask_tail*',
        'S_begin = S_entry[.TODO = (SUBMUL_CONVERT pintegeroperation ARITHMETIC_LEFT) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$call_task_valid(S_begin, SUBMUL_CONVERT pintegeroperation ARITHMETIC_LEFT)', '$task_nodes(SUBMUL_CONVERT pintegeroperation ARITHMETIC_LEFT) = eps',
        'S_capture_budget = $drive_steps(S_begin, 1)', 'S_capture_budget.COMPLETION = BUDGET',
        'S_capture = S_capture_budget[.COMPLETION = NORMAL]', '$submul_frontier(S_capture, 2)',
        'S_capture.TODO = (' + left(0) + ') :: ptask_tail*',
        '$submul_warning_valid(S_capture, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NINT 12, 0)',
        '$task_nodes(' + left(0) + ') = eps', 'S_capture.STORE = S_entry.STORE', 'S_capture.ALLOCATIONS = S_entry.ALLOCATIONS',
    ]
    if not thrown:
        checks += [
            '~$submul_valid(S_entry, pintegeroperation[.OP = MULTIPLY])', '~$submul_valid(S_entry, pintegeroperation[.SWAPPED = true])',
            '~$submul_valid(S_entry, pintegeroperation[.LINE = 24])', '~$submul_valid(S_entry, pintegeroperation[.LEFT = pintegeroperation.RIGHT])',
            '~$submul_valid(S_entry[.ORIGIN = eps], pintegeroperation)', '$submul_warning_plan(S_entry[.REFCELLS = eps]) = eps',
            '~$submul_initial_value(S_entry, PUNDEFINED)', '~$submul_initial_value(S_entry, PARRAY 0)', '~$submul_initial_value(S_entry, POBJECT 0)',
            '~$submul_initial_value(S_entry, PINT 9223372036854775808)', '~$submul_initial_value(S_entry, PFLOAT 18446744073709551616)',
            '~$submul_initial_value(S_entry, PSTRING_CARRIER (REQUEST_STRING (|S_entry.STRINGDATA|)) ($ptascii("bad5")))',
            '~$submul_warning_valid(S_capture, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NINT 13, 0)',
            '~$submul_warning_valid(S_capture, pintegeroperation, ARITHMETIC_LEFT, PSTRING ($ptascii("13tail")), NINT 13, 0)',
            '~$submul_warning_valid(S_capture, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NINT 12, 2)',
        ]
    checks += [
        'S_first_budget = $drive_steps(S_capture, 1)', 'S_first_budget.COMPLETION = BUDGET',
        'S_first = S_first_budget[.COMPLETION = NORMAL]', '$submul_frontier(S_first, 3)',
        'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
        'perrorcall_first.RESUME = ' + left(1), 'perrorcall_first.TARGET = eps', 'perrorcall_first.LEVEL = 2', 'perrorcall_first.LINE = 25',
        '$error_call_valid(S_first, perrorcall_first)',
        'S_entered_found = $submul_seek(S_first, 10, 5000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', '$submul_entered(S_entered.FRAMES, 0)',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
        'S_return_found = $submul_seek(S_entered, 4, 5000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', 'S_return.TODO = (' + left(1) + ') :: ptask_tail*',
        'S_return.STORE[n_left] = DEFINED (PINT 99)', 'S_return.STORE[n_right] = DEFINED pvalue_right',
        '$string_bytes(pvalue_right) = ($ptascii("5tail"))', 'S_return.STORE[n_calls] = DEFINED (PINT 1)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
        '$submul_warning_valid(S_return, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NINT 12, 1)',
        '~$submul_warning_valid(S_return, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NINT 12, 0)',
        'S_right_budget = $drive_steps(S_return, 1)', 'S_right_budget.COMPLETION = BUDGET',
        'S_right = S_right_budget[.COMPLETION = NORMAL]', '$submul_frontier(S_right, 5)',
        'S_right.TODO = (SUBMUL_CONVERT pintegeroperation (ARITHMETIC_RIGHT (NINT 12))) :: ptask_tail*',
        'S_second_capture_budget = $drive_steps(S_right, 1)', 'S_second_capture_budget.COMPLETION = BUDGET',
        'S_second_capture = S_second_capture_budget[.COMPLETION = NORMAL]', '$submul_frontier(S_second_capture, 6)',
        'S_second_capture.TODO = (' + right(0) + ') :: ptask_tail*', '$call_task_valid(S_second_capture, ' + right(0) + ')',
        'S_second_budget = $drive_steps(S_second_capture, 1)', 'S_second_budget.COMPLETION = BUDGET',
        'S_second = S_second_budget[.COMPLETION = NORMAL]', '$submul_frontier(S_second, 7)',
        'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
        'perrorcall_second.RESUME = ' + right(1), 'perrorcall_second.TARGET = eps',
        'perrorcall_second.LEVEL = 2', 'perrorcall_second.LINE = 25', '$error_call_valid(S_second, perrorcall_second)',
        'S_second_entered_found = $submul_seek(S_second, 11, 5000)',
        r'S_second_entered_found.COMPLETION = NORMAL \/ S_second_entered_found.COMPLETION = BUDGET',
        'S_second_entered = S_second_entered_found[.COMPLETION = NORMAL]', '$submul_entered(S_second_entered.FRAMES, 1)',
    ]
    if thrown:
        checks += [
            'S_throw_found = $submul_seek(S_second_entered, 9, 5000)',
            r'S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET',
            'S_throw = S_throw_found[.COMPLETION = NORMAL]', '$submul_frontier(S_throw, 9)',
            'S_throw.TODO = (THROW_SEARCH n_supplied) :: ptask_throw*', 'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps', '~$submul_tasks(S_throw.TODO)',
            '$throwable_live(S_throw, n_supplied)', '$throwable_previous_id(S_throw, n_supplied) = eps', '$throwable_field(S_throw, n_supplied, "line") = PINT 20',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_supplied) = 2',
            'S_throw.STORE[n_left] = DEFINED (PINT 88)', 'S_throw.STORE[n_right] = DEFINED (PINT 7)',
            'S_throw.STORE[n_v] = DEFINED (PINT 100)', 'S_throw.STORE[n_calls] = DEFINED (PINT 2)',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_left) = 2', '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_right) = 2',
            'S_throw.ERRORHANDLER = S_entry.ERRORHANDLER', '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
            'S_done = $drive_steps(S_throw, 5000)', 'S_done.STORE[n_v] = DEFINED (PINT 100)',
        ]
    else:
        checks += [
            '~$error_call_valid(S_first, perrorcall_first[.LEVEL = 8192])', '~$error_call_valid(S_first, perrorcall_first[.MESSAGE = eps])',
            '~$error_call_valid(S_first, perrorcall_first[.RESUME = SUBMUL_WARNING pintegeroperation ARITHMETIC_LEFT (PSTRING ($ptascii("13tail"))) (NINT 13) 1])',
            '~$error_call_valid(S_second, perrorcall_second[.LINE = 24])',
            'S_late_found = $submul_seek(S_second_entered, 8, 5000)',
            r'S_late_found.COMPLETION = NORMAL \/ S_late_found.COMPLETION = BUDGET',
            'S_late = S_late_found[.COMPLETION = NORMAL]', 'S_late.TODO = (' + right(1) + ') :: ptask_tail*',
            'S_late.STORE[n_left] = DEFINED (PINT 88)', 'S_late.STORE[n_right] = DEFINED (PINT 7)',
            'S_late.STORE[n_v] = DEFINED (PINT 100)', 'S_late.STORE[n_calls] = DEFINED (PINT 2)',
            '$call_task_valid(S_late, ' + right(1) + ')', '~$call_task_valid(S_late, ' + right(0) + ')',
            'S_result_budget = $drive_steps(S_late, 1)', 'S_result_budget.COMPLETION = BUDGET',
            'S_result = S_result_budget[.COMPLETION = NORMAL]',
            'S_result = S_late[.TODO = ptask_tail*][.RESULT = KNOWN (PINT 7)]',
            '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_left) = 2', '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_right) = 2',
            '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
            'S_done = $drive_steps(S_result, 5000)', 'S_done.STORE[n_v] = DEFINED (PINT 7)',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_left)', '$lookup(S_done.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_done.ENV, $ptascii("right")) = (n_right)', '$lookup(S_done.ENV, $ptascii("rightAlias")) = (n_right)',
        'S_done.STORE[n_left] = DEFINED (PINT 1)', 'S_done.STORE[n_right] = DEFINED (PINT 2)', 'S_done.STORE[n_calls] = DEFINED (PINT 2)',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_entry, 6000) = S_done', '$drive_steps(S_begin, 6000) = S_done', '$drive_steps(S_capture, 6000) = S_done',
        '$drive_steps(S_first, 6000) = S_done', '$drive_steps(S_entered, 6000) = S_done', '$drive_steps(S_return, 6000) = S_done',
        '$drive_steps(S_second, 6000) = S_done',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path, required=True)
    args, _ = parser.parse_known_args()
    watched = [Path(__file__), Path(cases.__file__), Path(shared.__file__), Path(prior.__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    shared.cases, shared.CASES, shared.HELPERS, shared.conditions = cases, CASES, HELPERS, conditions
    passed = shared.main()
    assert before == {str(path): digest(path) for path in watched}
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
