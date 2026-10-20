#!/usr/bin/env python3
"""The second self-addition Warning throws after both real numeric captures."""
import base64
import json

import addassign_self_warning_review_cases as cases
import addassign_self_warning_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = ''


def conditions(name, program, path, stdout):
    assert name in CASES
    left_number = 'NFLOAT 4623226492472524800'
    right_number = 'NFLOAT 4617878467915022336'
    first = lambda stage: f'ARITHMETIC_ADDASSIGN_CV_WARNING pintegeroperation pvalue_left ({left_number}) {stage}'
    second = lambda stage: f'ARITHMETIC_ADDASSIGN_CV_RIGHT_WARNING pintegeroperation pvalue_left ({left_number}) pvalue_right ({right_number}) {stage}'
    valid = lambda state, stage: f'$arithmetic_addassign_cv_right_warning_valid({state}, pintegeroperation, pvalue_left, {left_number}, pvalue_right, {right_number}, {stage})'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $addassign_self_seek({before}, {stage}, 3000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$addassign_self_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$arithmetic_addassign_self_plan(S_entry) = ((pintegeroperation, pvalue_left, ' + left_number + '))',
        '$arithmetic_addassign_cv_plan(S_entry) = eps',
        '$arithmetic_addassign_plan(S_entry) = eps',
        '$arithmetic_addassign_repair_plan(S_entry) = eps',
        'pintegeroperation.OP = ADD',
        '~pintegeroperation.SWAPPED',
        'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("x")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("x")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("x"))',
        'pintegeroperation.RIGHTPOINTER = pintegeroperation.LEFTPOINTER',
        '$arithmetic_addassign_cv_source(S_entry, pintegeroperation)',
        '$arithmetic_add_selected(S_entry, pintegeroperation)',
        'S_entry.TODO = (COMPOUND_APPLY ADD (BASE_VALUE pintegeroperation.LEFT) true 25) :: ptask_tail*',
        'S_entry.RESULT = pintegeroperation.RIGHT',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
        'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_exception)',
        'S_entry.STORE[n_x] = DEFINED pvalue_left',
        '$string_bytes(pvalue_left) = ($ptascii("12.5tail"))',
        '$string_carrier_valid(S_entry, pvalue_left)',
        '$arithmetic_add_conversion(pvalue_left) = ((' + left_number + ', true))',
        '$integer_pointer_value(S_entry, pintegeroperation.RIGHTPOINTER) = (pvalue_left)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '~(n_x <- S_entry.REFCELLS)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        'S_entry.EVENTS = eps',
        '$call_descriptors_valid(S_entry)',
        '$heap_valid($heap_graph(S_entry))',
        'PhpStep: S_entry ~> S_begin_atomic',
        'S_begin_atomic = S_entry[.TODO = (' + first(0) + ') :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = ROOT n_x]',
    ]
    step('S_begin', 'S_entry')
    checks += [
        'S_begin = S_begin_atomic',
        '$addassign_self_frontier(S_begin, 1)',
        '$task_nodes(' + first(0) + ') = eps',
        '$arithmetic_addassign_cv_warning_valid(S_begin, pintegeroperation, pvalue_left, ' + left_number + ', 0)',
    ]
    step('S_first_call', 'S_begin')
    checks += [
        '$addassign_self_frontier(S_first_call, 2)',
        'S_first_call.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
        'perrorcall_first.RESUME = ' + first(1),
        'perrorcall_first.TARGET = eps',
        'perrorcall_first.SITE = pintegeroperation.SITE',
        'perrorcall_first.LEVEL = 2',
        'perrorcall_first.LINE = 25',
        'perrorcall_first.MESSAGE = $ptascii("A non-numeric value encountered")',
        '$error_call_valid(S_first_call, perrorcall_first)',
        '$call_descriptors_valid(S_first_call)',
    ]
    seek('S_first_entered', 'S_first_call', 3)
    checks += [
        '$addassign_rhs_warning_entered(S_first_entered.FRAMES, 0)',
        '$call_descriptors_valid(S_first_entered)',
    ]
    seek('S_left', 'S_first_entered', 4)
    checks += [
        'S_left.TODO = (' + first(1) + ') :: ptask_tail*',
        'S_left.STORE[n_x] = DEFINED pvalue_right',
        '$string_bytes(pvalue_right) = ($ptascii("5.5tail"))',
        '$string_carrier_valid(S_left, pvalue_right)',
        '$arithmetic_add_conversion(pvalue_right) = ((' + right_number + ', true))',
        '$integer_pointer_value(S_left, pintegeroperation.LEFTPOINTER) = (pvalue_right)',
        '$integer_pointer_value(S_left, pintegeroperation.RIGHTPOINTER) = (pvalue_right)',
        'S_left.STORE[n_v] = DEFINED (PINT 100)',
        'S_left.STORE[n_calls] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_left)), HCELL n_x) = 1',
        '$arithmetic_addassign_cv_warning_valid(S_left, pintegeroperation, pvalue_left, ' + left_number + ', 1)',
        '~$arithmetic_addassign_cv_warning_valid(S_left, pintegeroperation, pvalue_left, ' + left_number + ', 0)',
        '$arithmetic_addassign_cv_ready(S_left, pintegeroperation) = eps',
        '$arithmetic_addassign_cv_right_snapshot(S_left, pintegeroperation) = ((pvalue_right, ' + right_number + '))',
        '$arithmetic_addassign_cv_right_target(S_left, pintegeroperation)',
        '$addassign_self_diagnostics(S_left.EVENTS, "Warning") = 0',
        '$call_descriptors_valid(S_left)',
        '$heap_valid($heap_graph(S_left))',
        'PhpStep: S_left ~> S_capture_atomic',
        'S_capture_atomic = S_left[.TODO = (' + second(0) + ') :: ptask_tail*]',
    ]
    step('S_capture', 'S_left')
    checks += [
        'S_capture = S_capture_atomic',
        '$addassign_self_frontier(S_capture, 5)',
        valid('S_capture', 0),
        '$task_nodes(' + second(0) + ') = eps',
    ]
    step('S_second_call', 'S_capture')
    checks += [
        '$addassign_self_frontier(S_second_call, 6)',
        'S_second_call.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
        'perrorcall_second.RESUME = ' + second(1),
        'perrorcall_second.TARGET = eps',
        'perrorcall_second.SITE = pintegeroperation.SITE',
        'perrorcall_second.LEVEL = 2',
        'perrorcall_second.LINE = 25',
        'perrorcall_second.MESSAGE = perrorcall_first.MESSAGE',
        '$error_call_valid(S_second_call, perrorcall_second)',
        '$call_descriptors_valid(S_second_call)',
    ]
    seek('S_second_entered', 'S_second_call', 7)
    checks += [
        '$addassign_rhs_warning_entered(S_second_entered.FRAMES, 1)',
        '$call_descriptors_valid(S_second_entered)',
    ]
    seek('S_throw', 'S_second_entered', 9)
    checks += [
        'S_throw.TODO = (THROW_SEARCH n_exception) :: ptask_caller*',
        'S_throw.CURRENT = eps',
        'S_throw.FRAMES = eps',
        '~$addassign_rhs_warning_tasks(S_throw.TODO)',
        '$lookup(S_throw.ENV, $ptascii("x")) = (n_x)',
        'S_throw.STORE[n_x] = DEFINED (PINT 88)',
        'S_throw.STORE[n_v] = DEFINED (PINT 100)',
        'S_throw.STORE[n_calls] = DEFINED (PINT 2)',
        '$integer_pointer_value(S_throw, pintegeroperation.LEFTPOINTER) = (PINT 88)',
        '$integer_pointer_value(S_throw, pintegeroperation.RIGHTPOINTER) = (PINT 88)',
        '~(n_x <- S_throw.REFCELLS)',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_x) = 1',
        valid('S_throw', 1),
        '~' + valid('S_throw', 0),
        '$arithmetic_addassign_cv_right_snapshot(S_throw, pintegeroperation) = eps',
        '$arithmetic_addassign_cv_right_target(S_throw, pintegeroperation)',
        '$task_nodes(' + second(1) + ') = eps',
        '$task_nodes(THROW_SEARCH n_exception) = [HOBJECT n_exception]',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_exception) = 2',
        '$throwable_live(S_throw, n_exception)',
        '$throwable_previous_id(S_throw, n_exception) = eps',
        '$throwable_field(S_throw, n_exception, "line") = PINT 20',
        '$addassign_self_diagnostics(S_throw.EVENTS, "Warning") = 0',
        '$addassign_self_diagnostics(S_throw.EVENTS, "Deprecated") = 0',
        'S_throw.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_throw)',
        '$heap_valid($heap_graph(S_throw))',
        'S_done = $drive_steps(S_throw, 3000)',
        'S_done.COMPLETION = NORMAL',
        'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps',
        'S_done.FRAMES = eps',
        'S_done.CURRENT = eps',
        'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("x")) = (n_x)',
        'S_done.STORE[n_x] = DEFINED (PINT 8)',
        'S_done.STORE[n_v] = DEFINED (PINT 100)',
        'S_done.STORE[n_calls] = DEFINED (PINT 2)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_x) = 1',
        '$addassign_self_diagnostics(S_done.EVENTS, "Warning") = 0',
        '$addassign_self_diagnostics(S_done.EVENTS, "Deprecated") = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_throw, 0) = S_throw[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
