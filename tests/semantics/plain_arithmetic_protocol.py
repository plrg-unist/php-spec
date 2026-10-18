#!/usr/bin/env python3
"""Reached initially plain-CV arithmetic holders and diagnostic continuations."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import plain_arithmetic_cases as cases
import arithmetic_warning_protocol as shared
import integer_operator_warning_protocol as prior

CASES = ('plain-arithmetic-add-right-warning', 'plain-arithmetic-power-deprecated', 'plain-arithmetic-power-deprecated-throw')
HELPERS = prior.HELPERS + r'''

dec $plain_arithmetic_task(ptask) : bool
def $plain_arithmetic_task(ARITHMETIC_CV_CONVERT pintegeroperation parithmeticphase) = true
def $plain_arithmetic_task(ARITHMETIC_CV_WARNING pintegeroperation parithmeticphase pvalue pnumber n) = true
def $plain_arithmetic_task(ARITHMETIC_CV_DEPRECATED pintegeroperation pnumber_left pnumber_right n) = true
def $plain_arithmetic_task(ERROR_HANDLER_INVOKE perrorcall) = $plain_arithmetic_task(perrorcall.RESUME)
def $plain_arithmetic_task(ERROR_HANDLER_RESULT perrorcall) = $plain_arithmetic_task(perrorcall.RESUME)
def $plain_arithmetic_task(ERROR_HANDLER_CLEAN perrorcall) = $plain_arithmetic_task(perrorcall.RESUME)
def $plain_arithmetic_task(ptask) = false -- otherwise
dec $plain_arithmetic_tasks(ptask*) : bool
def $plain_arithmetic_tasks(eps) = false
def $plain_arithmetic_tasks(ptask :: ptask_tail*) = ($plain_arithmetic_task(ptask) \/ $plain_arithmetic_tasks(ptask_tail*))

dec $plain_arithmetic_frame(pframe, nat) : bool
def $plain_arithmetic_frame(pframe, 0) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.TARGET =/= eps
  -- if perrorcall.RESUME = ARITHMETIC_CV_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 1
def $plain_arithmetic_frame(pframe, 1) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.TARGET =/= eps
  -- if perrorcall.RESUME = ARITHMETIC_CV_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue pnumber_right 1
def $plain_arithmetic_frame(pframe, 2) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.TARGET =/= eps
  -- if perrorcall.RESUME = ARITHMETIC_CV_DEPRECATED pintegeroperation pnumber_left pnumber_right 1
def $plain_arithmetic_frame(pframe, n) = false -- otherwise
dec $plain_arithmetic_entered(pframe*, nat) : bool
def $plain_arithmetic_entered(eps, n) = false
def $plain_arithmetic_entered(pframe :: pframe_tail*, n) = ($plain_arithmetic_frame(pframe, n) \/ $plain_arithmetic_entered(pframe_tail*, n))

dec $plain_arithmetic_frontier(pstate, nat) : bool
def $plain_arithmetic_frontier(S, 0) = ($arithmetic_cv_plan(S) =/= eps)
def $plain_arithmetic_frontier(S, 1) = true
  -- if S.TODO = (ARITHMETIC_CV_CONVERT pintegeroperation ARITHMETIC_LEFT) :: ptask_tail*
def $plain_arithmetic_frontier(S, 2) = true
  -- if S.TODO = (ARITHMETIC_CV_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 0) :: ptask_tail*
def $plain_arithmetic_frontier(S, 3) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_CV_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 1
  -- if perrorcall.TARGET = eps
def $plain_arithmetic_frontier(S, 4) = true
  -- if S.TODO = (ARITHMETIC_CV_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 1) :: ptask_tail*
def $plain_arithmetic_frontier(S, 5) = true
  -- if S.TODO = (ARITHMETIC_CV_CONVERT pintegeroperation (ARITHMETIC_RIGHT pnumber)) :: ptask_tail*
def $plain_arithmetic_frontier(S, 6) = true
  -- if S.TODO = (ARITHMETIC_CV_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue pnumber_right 0) :: ptask_tail*
def $plain_arithmetic_frontier(S, 7) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_CV_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue pnumber_right 1
  -- if perrorcall.TARGET = eps
def $plain_arithmetic_frontier(S, 8) = true
  -- if S.TODO = (ARITHMETIC_CV_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue pnumber_right 1) :: ptask_tail*
def $plain_arithmetic_frontier(S, 9) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if ~$plain_arithmetic_tasks(S.TODO)
def $plain_arithmetic_frontier(S, 10) = (S.CURRENT =/= eps /\ $plain_arithmetic_entered(S.FRAMES, 0))
def $plain_arithmetic_frontier(S, 11) = (S.CURRENT =/= eps /\ $plain_arithmetic_entered(S.FRAMES, 1))
def $plain_arithmetic_frontier(S, 12) = true
  -- if S.TODO = (ARITHMETIC_CV_DEPRECATED pintegeroperation pnumber_left pnumber_right 0) :: ptask_tail*
def $plain_arithmetic_frontier(S, 13) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_CV_DEPRECATED pintegeroperation pnumber_left pnumber_right 1
  -- if perrorcall.TARGET = eps
def $plain_arithmetic_frontier(S, 14) = (S.CURRENT =/= eps /\ $plain_arithmetic_entered(S.FRAMES, 2))
def $plain_arithmetic_frontier(S, 15) = true
  -- if S.TODO = (ARITHMETIC_CV_DEPRECATED pintegeroperation pnumber_left pnumber_right 1) :: ptask_tail*
def $plain_arithmetic_frontier(S, n) = false -- otherwise
dec $plain_arithmetic_seek(pstate, nat, nat) : pstate
def $plain_arithmetic_seek(S, n_stage, n) = S -- if $plain_arithmetic_frontier(S, n_stage)
def $plain_arithmetic_seek(S, n_stage, n) = S
  -- if ~$plain_arithmetic_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $plain_arithmetic_seek(S, n_stage, n) = S
  -- if ~$plain_arithmetic_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $plain_arithmetic_seek(S, n_stage, n) = $plain_arithmetic_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$plain_arithmetic_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def power_conditions(name, program, path, stdout):
    thrown = name == CASES[2]
    operation = 'POWER'
    left = lambda stage: f'ARITHMETIC_CV_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_left (NINT 0) {stage}'
    right = lambda stage: f'ARITHMETIC_CV_WARNING pintegeroperation (ARITHMETIC_RIGHT (NINT 0)) pvalue_right (NINT (-2)) {stage}'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_entry_found = $plain_arithmetic_seek(S_initial, 0, 5000)',
        r'S_entry_found.COMPLETION = NORMAL \/ S_entry_found.COMPLETION = BUDGET',
        'S_entry = S_entry_found[.COMPLETION = NORMAL]', '$plain_arithmetic_frontier(S_entry, 0)',
        '$arithmetic_cv_plan(S_entry) = (pintegeroperation)', '$arithmetic_cv_valid(S_entry, pintegeroperation)',
        'pintegeroperation.OP = ' + operation, '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23', 'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("left"))', 'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))', '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)', '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)', '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)', '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("supplied")) = (n_supplied_cell)', 'S_entry.STORE[n_supplied_cell] = DEFINED (POBJECT n_supplied)',
        '~(n_left <- S_entry.REFCELLS)', '~(n_right <- S_entry.REFCELLS)',
        'S_entry.STORE[n_left] = DEFINED pvalue_left', '$string_bytes(pvalue_left) = ($ptascii("0tail"))',
        'S_entry.STORE[n_right] = DEFINED pvalue_initial_right',
        'pvalue_initial_right = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("bad5"))',
        'S_entry.STRINGDATA[n_string] = $ptascii("bad5")', '$submul_initial_value(S_entry, pvalue_initial_right)',
        '$arithmetic_add_conversion(pvalue_initial_right) = eps',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)', 'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 1', '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 1',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'S_begin_budget = $drive_steps(S_entry, 1)', 'S_begin_budget.COMPLETION = BUDGET',
        'S_begin = S_begin_budget[.COMPLETION = NORMAL]', '$plain_arithmetic_frontier(S_begin, 1)',
        'S_entry.TODO = ptask_old :: ptask_tail*',
        'S_begin = S_entry[.TODO = (ARITHMETIC_CV_CONVERT pintegeroperation ARITHMETIC_LEFT) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$call_task_valid(S_begin, ARITHMETIC_CV_CONVERT pintegeroperation ARITHMETIC_LEFT)', '$task_nodes(ARITHMETIC_CV_CONVERT pintegeroperation ARITHMETIC_LEFT) = eps',
        'S_capture_budget = $drive_steps(S_begin, 1)', 'S_capture_budget.COMPLETION = BUDGET',
        'S_capture = S_capture_budget[.COMPLETION = NORMAL]', '$plain_arithmetic_frontier(S_capture, 2)',
        'S_capture.TODO = (' + left(0) + ') :: ptask_tail*',
        '$arithmetic_cv_warning_valid(S_capture, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NINT 0, 0)',
        '$task_nodes(' + left(0) + ') = eps', 'S_capture.STORE = S_entry.STORE', 'S_capture.ALLOCATIONS = S_entry.ALLOCATIONS',
    ]
    if not thrown:
        checks += [
            '~$arithmetic_cv_valid(S_entry, pintegeroperation[.OP = MULTIPLY])', '~$arithmetic_cv_valid(S_entry, pintegeroperation[.SWAPPED = true])',
            '~$arithmetic_cv_valid(S_entry, pintegeroperation[.LINE = 24])', '~$arithmetic_cv_valid(S_entry, pintegeroperation[.LEFT = pintegeroperation.RIGHT])',
            '~$arithmetic_cv_valid(S_entry[.ORIGIN = eps], pintegeroperation)', '$arithmetic_cv_plan(S_entry[.REFCELLS = [n_left]]) = eps',
            '~$submul_initial_value(S_entry, PUNDEFINED)', '~$submul_initial_value(S_entry, PARRAY 0)', '~$submul_initial_value(S_entry, POBJECT 0)',
            '~$submul_initial_value(S_entry, PINT 9223372036854775808)', '~$submul_initial_value(S_entry, PFLOAT 18446744073709551616)',
            '~$submul_initial_value(S_entry, PSTRING_CARRIER (REQUEST_STRING (|S_entry.STRINGDATA|)) ($ptascii("bad5")))',
            '~$arithmetic_cv_warning_valid(S_capture, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NINT 1, 0)',
            '~$arithmetic_cv_warning_valid(S_capture, pintegeroperation, ARITHMETIC_LEFT, PSTRING ($ptascii("1tail")), NINT 1, 0)',
            '~$arithmetic_cv_warning_valid(S_capture, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NINT 0, 2)',
        ]
    checks += [
        'S_first_budget = $drive_steps(S_capture, 1)', 'S_first_budget.COMPLETION = BUDGET',
        'S_first = S_first_budget[.COMPLETION = NORMAL]', '$plain_arithmetic_frontier(S_first, 3)',
        'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
        'perrorcall_first.RESUME = ' + left(1), 'perrorcall_first.TARGET = eps', 'perrorcall_first.LEVEL = 2', 'perrorcall_first.LINE = 25',
        '$error_call_valid(S_first, perrorcall_first)',
        'S_entered_found = $plain_arithmetic_seek(S_first, 10, 5000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', '$plain_arithmetic_entered(S_entered.FRAMES, 0)',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
        'S_return_found = $plain_arithmetic_seek(S_entered, 4, 5000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', 'S_return.TODO = (' + left(1) + ') :: ptask_tail*',
        'S_return.STORE[n_left] = DEFINED (PINT 99)', 'S_return.STORE[n_right] = DEFINED pvalue_right',
        '$string_bytes(pvalue_right) = ($ptascii("-2tail"))', 'S_return.STORE[n_calls] = DEFINED (PINT 1)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
        '$arithmetic_cv_warning_valid(S_return, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NINT 0, 1)',
        '~$arithmetic_cv_warning_valid(S_return, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NINT 0, 0)',
        'S_right_budget = $drive_steps(S_return, 1)', 'S_right_budget.COMPLETION = BUDGET',
        'S_right = S_right_budget[.COMPLETION = NORMAL]', '$plain_arithmetic_frontier(S_right, 5)',
        'S_right.TODO = (ARITHMETIC_CV_CONVERT pintegeroperation (ARITHMETIC_RIGHT (NINT 0))) :: ptask_tail*',
        'S_second_capture_budget = $drive_steps(S_right, 1)', 'S_second_capture_budget.COMPLETION = BUDGET',
        'S_second_capture = S_second_capture_budget[.COMPLETION = NORMAL]', '$plain_arithmetic_frontier(S_second_capture, 6)',
        'S_second_capture.TODO = (' + right(0) + ') :: ptask_tail*', '$call_task_valid(S_second_capture, ' + right(0) + ')',
        'S_second_budget = $drive_steps(S_second_capture, 1)', 'S_second_budget.COMPLETION = BUDGET',
        'S_second = S_second_budget[.COMPLETION = NORMAL]', '$plain_arithmetic_frontier(S_second, 7)',
        'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
        'perrorcall_second.RESUME = ' + right(1), 'perrorcall_second.TARGET = eps',
        'perrorcall_second.LEVEL = 2', 'perrorcall_second.LINE = 25', '$error_call_valid(S_second, perrorcall_second)',
        'S_second_entered_found = $plain_arithmetic_seek(S_second, 11, 5000)',
        r'S_second_entered_found.COMPLETION = NORMAL \/ S_second_entered_found.COMPLETION = BUDGET',
        'S_second_entered = S_second_entered_found[.COMPLETION = NORMAL]', '$plain_arithmetic_entered(S_second_entered.FRAMES, 1)',
    ]
    checks += [
        'S_late_found = $plain_arithmetic_seek(S_second_entered, 8, 5000)',
        r'S_late_found.COMPLETION = NORMAL \/ S_late_found.COMPLETION = BUDGET',
        'S_late = S_late_found[.COMPLETION = NORMAL]', 'S_late.TODO = (' + right(1) + ') :: ptask_tail*',
        'S_late.STORE[n_left] = DEFINED (PINT 88)', 'S_late.STORE[n_right] = DEFINED (PINT 7)',
        'S_late.STORE[n_v] = DEFINED (PINT 100)', 'S_late.STORE[n_calls] = DEFINED (PINT 2)',
        '$call_task_valid(S_late, ' + right(1) + ')', '~$call_task_valid(S_late, ' + right(0) + ')',
        'S_deprecated_budget = $drive_steps(S_late, 1)', 'S_deprecated_budget.COMPLETION = BUDGET',
        'S_deprecated = S_deprecated_budget[.COMPLETION = NORMAL]', '$plain_arithmetic_frontier(S_deprecated, 12)',
        'S_deprecated = S_late[.TODO = (ARITHMETIC_CV_DEPRECATED pintegeroperation (NINT 0) (NINT (-2)) 0) :: ptask_tail*][.RESULT = KNOWN PNULL]',
        '$arithmetic_cv_deprecated_valid(S_deprecated, pintegeroperation, NINT 0, NINT (-2), 0)',
        '~$power_warning_snapshot(S_deprecated, pintegeroperation, NINT 0, NINT (-2))',
        '$task_nodes(ARITHMETIC_CV_DEPRECATED pintegeroperation (NINT 0) (NINT (-2)) 0) = eps',
        'S_final_budget = $drive_steps(S_deprecated, 1)', 'S_final_budget.COMPLETION = BUDGET',
        'S_final = S_final_budget[.COMPLETION = NORMAL]', '$plain_arithmetic_frontier(S_final, 13)',
        'S_final.TODO = (ERROR_HANDLER_INVOKE perrorcall_final) :: ptask_tail*',
        'perrorcall_final.RESUME = ARITHMETIC_CV_DEPRECATED pintegeroperation (NINT 0) (NINT (-2)) 1',
        'perrorcall_final.TARGET = eps', 'perrorcall_final.LEVEL = 8192', 'perrorcall_final.LINE = 25',
        'perrorcall_final.MESSAGE = $ptascii("Power of base 0 and negative exponent is deprecated")',
        '$error_call_valid(S_final, perrorcall_final)',
        'S_final.STORE[n_left] = DEFINED (PINT 88)', 'S_final.STORE[n_right] = DEFINED (PINT 7)',
        'S_final_entered_found = $plain_arithmetic_seek(S_final, 14, 5000)',
        r'S_final_entered_found.COMPLETION = NORMAL \/ S_final_entered_found.COMPLETION = BUDGET',
        'S_final_entered = S_final_entered_found[.COMPLETION = NORMAL]', '$plain_arithmetic_entered(S_final_entered.FRAMES, 2)',
        '$call_descriptors_valid(S_final_entered)', '$heap_valid($heap_graph(S_final_entered))',
    ]
    if not thrown:
        checks += [
            '~$error_call_valid(S_first, perrorcall_first[.RESUME = ARITHMETIC_CV_WARNING pintegeroperation ARITHMETIC_LEFT (PSTRING ($ptascii("1tail"))) (NINT 1) 1])',
            '~$error_call_valid(S_second, perrorcall_second[.LINE = 24])',
            '~$arithmetic_cv_deprecated_valid(S_deprecated, pintegeroperation, NINT 0, NINT (-2), 2)',
            '~$arithmetic_cv_deprecated_valid(S_deprecated, pintegeroperation, NFLOAT 18446744073709551616, NINT (-2), 0)',
            '~$error_call_valid(S_final, perrorcall_final[.LINE = 24])', '~$error_call_valid(S_final, perrorcall_final[.LEVEL = 2])',
            '~$error_call_valid(S_final, perrorcall_final[.MESSAGE = eps])',
            '~$error_call_valid(S_final, perrorcall_final[.RESUME = POWER_WARNING pintegeroperation (NINT 0) (NINT (-2)) 1])',
            'S_final_return_found = $plain_arithmetic_seek(S_final_entered, 15, 5000)',
            r'S_final_return_found.COMPLETION = NORMAL \/ S_final_return_found.COMPLETION = BUDGET',
            'S_final_return = S_final_return_found[.COMPLETION = NORMAL]', '$plain_arithmetic_frontier(S_final_return, 15)',
            'S_final_return.TODO = (ARITHMETIC_CV_DEPRECATED pintegeroperation (NINT 0) (NINT (-2)) 1) :: ptask_tail*',
            'S_final_return.STORE[n_left] = DEFINED (PINT 77)', 'S_final_return.STORE[n_right] = DEFINED (PINT 9)',
            'S_final_return.STORE[n_calls] = DEFINED (PINT 3)', 'S_final_return.STORE[n_v] = DEFINED (PINT 100)',
            '$arithmetic_cv_deprecated_valid(S_final_return, pintegeroperation, NINT 0, NINT (-2), 1)',
            'S_result_budget = $drive_steps(S_final_return, 1)', 'S_result_budget.COMPLETION = BUDGET',
            'S_result = S_result_budget[.COMPLETION = NORMAL]',
            'S_result = S_final_return[.TODO = ptask_tail*][.RESULT = KNOWN (PFLOAT 9218868437227405312)]',
            '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_left) = 1', '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_right) = 1',
            '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
            'S_done = $drive_steps(S_result, 5000)', 'S_done.STORE[n_v] = DEFINED (PFLOAT 9218868437227405312)',
        ]
    else:
        checks += [
            'S_throw_found = $plain_arithmetic_seek(S_final_entered, 9, 5000)',
            r'S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET',
            'S_throw = S_throw_found[.COMPLETION = NORMAL]', '$plain_arithmetic_frontier(S_throw, 9)',
            'S_throw.TODO = (THROW_SEARCH n_supplied) :: ptask_throw*', 'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps', '~$plain_arithmetic_tasks(S_throw.TODO)',
            '$throwable_live(S_throw, n_supplied)', '$throwable_previous_id(S_throw, n_supplied) = eps', '$throwable_field(S_throw, n_supplied, "line") = PINT 20',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_supplied) = 2',
            'S_throw.STORE[n_left] = DEFINED (PINT 77)', 'S_throw.STORE[n_right] = DEFINED (PINT 9)',
            'S_throw.STORE[n_v] = DEFINED (PINT 100)', 'S_throw.STORE[n_calls] = DEFINED (PINT 3)',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_left) = 1', '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_right) = 1',
            'S_throw.ERRORHANDLER = S_entry.ERRORHANDLER', '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
            'S_done = $drive_steps(S_throw, 5000)', 'S_done.STORE[n_v] = DEFINED (PINT 100)',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_left)', '$lookup(S_done.ENV, $ptascii("right")) = (n_right)', 'S_done.STORE[n_left] = DEFINED (PINT 1)', 'S_done.STORE[n_right] = DEFINED (PINT 2)', 'S_done.STORE[n_calls] = DEFINED (PINT 3)',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_entry, 6000) = S_done',
        '$drive_steps(S_final, 0) = S_final[.COMPLETION = BUDGET]',
    ]
    return checks


def quiet_conditions(name, program, path, stdout):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_entry_found = $plain_arithmetic_seek(S_initial, 0, 5000)',
        r'S_entry_found.COMPLETION = NORMAL \/ S_entry_found.COMPLETION = BUDGET',
        'S_entry = S_entry_found[.COMPLETION = NORMAL]', '$plain_arithmetic_frontier(S_entry, 0)',
        '$arithmetic_cv_operation(S_entry) = (pintegeroperation)',
        '$arithmetic_cv_plan(S_entry) = (pintegeroperation)', '$arithmetic_cv_valid(S_entry, pintegeroperation)',
        '$arithmetic_add_selected(S_entry, pintegeroperation)', 'pintegeroperation.OP = ADD', '~pintegeroperation.SWAPPED',
        'pintegeroperation.LINE = 25', 'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("left"))', 'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))', '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)', '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)', '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)', '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        'S_entry.STORE[n_left] = DEFINED (PINT 12)', 'S_entry.STORE[n_right] = DEFINED pvalue_right',
        '$string_bytes(pvalue_right) = ($ptascii("5tail"))',
        '$arithmetic_add_conversion(PINT 12) = ((NINT 12, false))', '$arithmetic_add_conversion(pvalue_right) = ((NINT 5, true))',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)', 'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 1',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$arithmetic_cv_operation(S_entry[.REFCELLS = [n_left]]) = eps',
        '$arithmetic_cv_operation(S_entry[.ALLOCATIONS = eps]) = eps',
        '$arithmetic_cv_operation(S_entry[.ENV = eps]) = eps',
        '$arithmetic_cv_operation(S_entry[.ORIGIN = eps]) = eps',
        '$arithmetic_cv_operation(S_entry[.CODE = eps]) = eps',
        '$arithmetic_cv_operation(S_entry[.STORE[n_left] = DEFINED PUNDEFINED]) = eps',
        '$arithmetic_cv_operation(S_entry[.STORE[n_left] = DEFINED (PARRAY 0)]) = eps',
        '$arithmetic_cv_plan(S_entry[.STORE[n_left] = DEFINED (PSTRING ($ptascii("bad")))]) = eps',
        '$arithmetic_cv_plan(S_entry[.STORE[n_right] = DEFINED (PINT 5)]) = eps',
        '$arithmetic_cv_plan(S_entry[.STORE[n_right] = DEFINED (PSTRING ($ptascii("bad")))]) = eps',
        '$arithmetic_cv_operation(S_entry[.STORE[n_right] = DEFINED (PSTRING_CARRIER (REQUEST_STRING (|S_entry.STRINGDATA|)) ($ptascii("5tail")))]) = eps',
        'S_begin_budget = $drive_steps(S_entry, 1)', 'S_begin_budget.COMPLETION = BUDGET',
        'S_begin = S_begin_budget[.COMPLETION = NORMAL]', '$plain_arithmetic_frontier(S_begin, 1)',
        'S_entry.TODO = ptask_old :: ptask_tail*',
        'S_begin = S_entry[.TODO = (ARITHMETIC_CV_CONVERT pintegeroperation ARITHMETIC_LEFT) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$call_task_valid(S_begin, ARITHMETIC_CV_CONVERT pintegeroperation ARITHMETIC_LEFT)',
        '$task_nodes(ARITHMETIC_CV_CONVERT pintegeroperation ARITHMETIC_LEFT) = eps',
        'S_quiet_budget = $drive_steps(S_begin, 1)', 'S_quiet_budget.COMPLETION = BUDGET',
        'S_quiet = S_quiet_budget[.COMPLETION = NORMAL]', '$plain_arithmetic_frontier(S_quiet, 5)', '~$plain_arithmetic_frontier(S_quiet, 2)',
        'S_quiet = S_begin[.TODO = (ARITHMETIC_CV_CONVERT pintegeroperation (ARITHMETIC_RIGHT (NINT 12))) :: ptask_tail*][.RESULT = KNOWN PNULL]',
        'S_quiet.STORE[n_calls] = DEFINED (PINT 0)',
        '$call_task_valid(S_quiet, ARITHMETIC_CV_CONVERT pintegeroperation (ARITHMETIC_RIGHT (NINT 12)))',
        'S_capture_budget = $drive_steps(S_quiet, 1)', 'S_capture_budget.COMPLETION = BUDGET',
        'S_capture = S_capture_budget[.COMPLETION = NORMAL]', '$plain_arithmetic_frontier(S_capture, 6)',
        'S_capture = S_quiet[.TODO = (ARITHMETIC_CV_WARNING pintegeroperation (ARITHMETIC_RIGHT (NINT 12)) pvalue_right (NINT 5) 0) :: ptask_tail*]',
        '$arithmetic_cv_warning_valid(S_capture, pintegeroperation, ARITHMETIC_RIGHT (NINT 12), pvalue_right, NINT 5, 0)',
        '$task_nodes(ARITHMETIC_CV_WARNING pintegeroperation (ARITHMETIC_RIGHT (NINT 12)) pvalue_right (NINT 5) 0) = eps',
        'S_dispatch_budget = $drive_steps(S_capture, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]', '$plain_arithmetic_frontier(S_dispatch, 7)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ARITHMETIC_CV_WARNING pintegeroperation (ARITHMETIC_RIGHT (NINT 12)) pvalue_right (NINT 5) 1',
        'perrorcall.TARGET = eps', 'perrorcall.LEVEL = 2', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = $ptascii("A non-numeric value encountered")', '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.RESUME = ARITHMETIC_CV_WARNING pintegeroperation (ARITHMETIC_RIGHT (NINT 12)) (PSTRING ($ptascii("6tail"))) (NINT 6) 1])',
        'S_return_found = $plain_arithmetic_seek(S_dispatch, 8, 5000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', '$plain_arithmetic_frontier(S_return, 8)',
        'S_return.TODO = (ARITHMETIC_CV_WARNING pintegeroperation (ARITHMETIC_RIGHT (NINT 12)) pvalue_right (NINT 5) 1) :: ptask_tail*',
        'S_return.STORE[n_left] = DEFINED (PINT 99)', 'S_return.STORE[n_right] = DEFINED (PINT 7)',
        'S_return.STORE[n_calls] = DEFINED (PINT 1)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
        '$arithmetic_cv_warning_valid(S_return, pintegeroperation, ARITHMETIC_RIGHT (NINT 12), pvalue_right, NINT 5, 1)',
        '~$arithmetic_cv_warning_valid(S_return, pintegeroperation, ARITHMETIC_RIGHT (NINT 12), pvalue_right, NINT 5, 0)',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'S_result_budget = $drive_steps(S_return, 1)', 'S_result_budget.COMPLETION = BUDGET',
        'S_result = S_result_budget[.COMPLETION = NORMAL]',
        'S_result = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (PINT 17)]',
        '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_right) = 1',
        '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 5000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_v] = DEFINED (PINT 17)', 'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_left)', '$lookup(S_done.ENV, $ptascii("right")) = (n_right)', 'S_done.STORE[n_left] = DEFINED (PINT 1)', 'S_done.STORE[n_right] = DEFINED (PINT 2)',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_entry, 6000) = S_done', '$drive_steps(S_dispatch, 0) = S_dispatch[.COMPLETION = BUDGET]',
    ]
    return checks


def conditions(name, program, path, stdout):
    checks = quiet_conditions(name, program, path, stdout) if name == CASES[0] else power_conditions(name, program, path, stdout)
    if name == CASES[0]:
        checks += [
            '$arithmetic_cv_value(S_entry, pintegeroperation.LEFTPOINTER) = (PINT 12)',
            '$arithmetic_cv_value(S_entry[.REFCELLS = [n_right]], pintegeroperation.RIGHTPOINTER) = eps',
            '$arithmetic_cv_plan(S_entry[.REFCELLS = [n_right]]) = eps',
        ]
    elif name == CASES[1]:
        checks += [
            '$arithmetic_cv_value(S_entry, pintegeroperation.RIGHTPOINTER) = (pvalue_initial_right)',
            '~$error_call_valid(S_first[.REFCELLS = [n_right]], perrorcall_first)',
            '$error_call_valid(S_second[.REFCELLS = [n_left]], perrorcall_second)',
            '~$arithmetic_cv_fresh(S_second[.REFCELLS = [n_right]], pintegeroperation, ARITHMETIC_RIGHT (NINT 0), pvalue_right)',
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
