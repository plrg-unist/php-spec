#!/usr/bin/env python3
"""Shared selected CELLs still capture LEFT and RIGHT at different times."""
import base64
import json

import addassign_repair_review_cases as cases
import addassign_repair_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = r'''
dec $addassign_repair_review_diagnostic(pevent) : nat
def $addassign_repair_review_diagnostic(DIAGNOSTIC "Warning" n* z) = 1
def $addassign_repair_review_diagnostic(DIAGNOSTIC_SOURCE n_source "Warning" n* z) = 1
def $addassign_repair_review_diagnostic(DIAGNOSTIC_STACK "Warning" n* z n_trace*) = 1
def $addassign_repair_review_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source "Warning" n* z n_trace*) = 1
def $addassign_repair_review_diagnostic(pevent) = 0 -- otherwise
dec $addassign_repair_review_warnings(pevent*) : nat
def $addassign_repair_review_warnings(eps) = 0
def $addassign_repair_review_warnings(pevent :: pevent_tail*) = $($addassign_repair_review_diagnostic(pevent) + $addassign_repair_review_warnings(pevent_tail*))
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    left = 'NFLOAT 4623226492472524800'
    right = 'NFLOAT 4617878467915022336'
    result = 'PFLOAT 4625759767262920704'
    first = lambda n: f'ARITHMETIC_ADDASSIGN_WARNING pintegeroperation pvalue_left ({left}) {n}'
    second = lambda n: f'ARITHMETIC_ADDASSIGN_RIGHT_WARNING pintegeroperation pvalue_left ({left}) pvalue_right ({right}) {n}'
    valid = lambda s, n: f'$arithmetic_addassign_right_warning_valid({s}, pintegeroperation, pvalue_left, {left}, pvalue_right, {right}, {n})'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $addassign_repair_seek({before}, {stage}, 4000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$addassign_repair_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$arithmetic_addassign_repair_plan(S_entry) = ((pintegeroperation, pvalue_left, ' + left + '))',
        '$arithmetic_addassign_plan(S_entry) = eps', '$arithmetic_addassign_cv_plan(S_entry) = eps',
        '$arithmetic_addassign_source(S_entry, pintegeroperation)',
        'pintegeroperation.OP = ADD', '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_shared',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_shared',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_shared)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_shared)',
        '$lookup(S_entry.ENV, $ptascii("alias")) = (n_shared)',
        '$lookup(S_entry.ENV, $ptascii("replacementLeft")) = (n_replacement_left)',
        '$lookup(S_entry.ENV, $ptascii("replacementRight")) = (n_replacement_right)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        'S_entry.STORE[n_shared] = DEFINED pvalue_left',
        '$string_bytes(pvalue_left) = ($ptascii("12.5tail"))',
        'S_entry.STORE[n_replacement_left] = DEFINED (PINT 77)',
        'S_entry.STORE[n_replacement_right] = DEFINED (PINT 7)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)', 'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_shared) = 3',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_replacement_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_replacement_right) = 1',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'S_entry.TODO = ptask_old :: ptask_tail*', 'PhpStep: S_entry ~> S_begin',
        'S_begin = S_entry[.TODO = (' + first(0) + ') :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = ROOT n_shared]',
    ]
    seek('S_first', 'S_begin', 2)
    checks += [
        'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_left) :: ptask_tail*',
        'perrorcall_left.RESUME = ' + first(1),
        'perrorcall_left.TARGET = eps', 'perrorcall_left.LEVEL = 2', 'perrorcall_left.LINE = 25',
        '$error_call_valid(S_first, perrorcall_left)', '$call_descriptors_valid(S_first)',
    ]
    seek('S_first_entered', 'S_first', 3)
    checks += ['$selected_rhs_warning_entered(S_first_entered.FRAMES, 0)', '$call_descriptors_valid(S_first_entered)']
    seek('S_left', 'S_first_entered', 4)
    checks += [
        'S_left.TODO = (' + first(1) + ') :: ptask_tail*',
        'S_left.STORE[n_shared] = DEFINED pvalue_right',
        '$string_bytes(pvalue_right) = ($ptascii("5.5tail"))',
        'S_left.STORE[n_calls] = DEFINED (PINT 1)', 'S_left.STORE[n_v] = DEFINED (PINT 100)',
        '$lookup(S_left.ENV, $ptascii("left")) = (n_shared)',
        '$lookup(S_left.ENV, $ptascii("alias")) = (n_shared)',
        '$lookup(S_left.ENV, $ptascii("right")) = (n_replacement_right)',
        '$integer_pointer_select(S_left, pintegeroperation.RIGHT) = (INTEGER_CELL n_replacement_right)',
        '$integer_pointer_value(S_left, pintegeroperation.LEFTPOINTER) = (pvalue_right)',
        '$integer_pointer_value(S_left, pintegeroperation.RIGHTPOINTER) = (pvalue_right)',
        '$arithmetic_addassign_ready(S_left, pintegeroperation) = eps',
        '$arithmetic_addassign_right_snapshot(S_left, pintegeroperation) = ((pvalue_right, ' + right + '))',
        '$arithmetic_addassign_warning_valid(S_left, pintegeroperation, pvalue_left, ' + left + ', 1)',
        '~$arithmetic_addassign_warning_valid(S_left, pintegeroperation, pvalue_left, ' + left + ', 0)',
        '$heap_owners($heap_prune($heap_graph(S_left)), HCELL n_shared) = 2',
        '$heap_owners($heap_prune($heap_graph(S_left)), HCELL n_replacement_right) = 2',
        'PhpStep: S_left ~> S_capture_atomic',
        'S_capture_atomic = S_left[.TODO = (' + second(0) + ') :: ptask_tail*]',
    ]
    step('S_capture', 'S_left')
    checks += [
        'S_capture.TODO = (' + second(0) + ') :: ptask_tail*',
        valid('S_capture', 0), '$task_nodes(' + second(0) + ') = eps',
        'S_capture.STORE = S_left.STORE', 'S_capture.ENV = S_left.ENV',
        'pvalue_counterfeit = PSTRING ($ptascii("7tail"))',
        'S_counterfeit = S_capture[.STORE[n_replacement_right] = DEFINED pvalue_counterfeit]',
        '~$arithmetic_addassign_right_warning_valid(S_counterfeit, pintegeroperation, pvalue_left, ' + left + ', pvalue_counterfeit, NINT 7, 0)',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
    ]
    step('S_second', 'S_capture')
    checks += [
        'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_right) :: ptask_tail*',
        'perrorcall_right.RESUME = ' + second(1),
        'perrorcall_right.TARGET = eps', 'perrorcall_right.LEVEL = 2', 'perrorcall_right.LINE = 25',
        '$error_call_valid(S_second, perrorcall_right)', '$call_descriptors_valid(S_second)',
    ]
    seek('S_second_entered', 'S_second', 7)
    checks += ['$selected_rhs_warning_entered(S_second_entered.FRAMES, 1)', '$call_descriptors_valid(S_second_entered)']
    seek('S_return', 'S_second_entered', 8)
    checks += [
        'S_return.TODO = (' + second(1) + ') :: ptask_tail*',
        'S_return.STORE[n_shared] = DEFINED (PINT 88)',
        'S_return.STORE[n_calls] = DEFINED (PINT 2)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
        '$lookup(S_return.ENV, $ptascii("alias")) = (n_shared)',
        '$lookup(S_return.ENV, $ptascii("left")) = (n_replacement_left)',
        '$lookup(S_return.ENV, $ptascii("right")) = (n_replacement_right)',
        'S_return.STORE[n_replacement_left] = DEFINED (PINT 77)',
        'S_return.STORE[n_replacement_right] = DEFINED (PINT 7)',
        '$integer_pointer_value(S_return, pintegeroperation.LEFTPOINTER) = (PINT 88)',
        '$integer_pointer_value(S_return, pintegeroperation.RIGHTPOINTER) = (PINT 88)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_shared) = 1',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_replacement_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_replacement_right) = 2',
        valid('S_return', 1), '~' + valid('S_return', 0),
        '$arithmetic_addassign_right_snapshot(S_return, pintegeroperation) = eps',
        '$arithmetic_addassign_right_target(S_return, pintegeroperation)',
        '$addassign_repair_review_warnings(S_return.EVENTS) = 1',
        'S_return.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'PhpStep: S_return ~> S_atomic',
        'S_atomic = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (' + result + ')][.LOCATION = ROOT n_shared][.STORE[n_shared] = DEFINED (' + result + ')]',
    ]
    step('S_result', 'S_return')
    checks += [
        'S_result.RESULT = KNOWN (' + result + ')', 'S_result.TODO = ptask_tail*',
        'S_result.STORE = S_atomic.STORE', 'S_result.STORE[n_v] = DEFINED (PINT 100)',
        'S_result.LOCATION = ROOT n_shared', 'S_result.ENV = S_return.ENV',
        'S_result.REFCELLS = S_return.REFCELLS', 'S_result.ALLOCATIONS = S_return.ALLOCATIONS',
        'S_result.EVENTS = S_return.EVENTS', 'S_result.STRINGDATA = S_return.STRINGDATA',
        'S_result.ARRAYS = S_return.ARRAYS', 'S_result.OBJECTS = S_return.OBJECTS',
        '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_shared) = 1',
        '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 4000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_v] = DEFINED (' + result + ')', 'S_done.STORE[n_shared] = DEFINED (PINT 6)',
        'S_done.STORE[n_calls] = DEFINED (PINT 2)',
        'S_done.STORE[n_replacement_left] = DEFINED (PINT 8)',
        'S_done.STORE[n_replacement_right] = DEFINED (PINT 9)',
        '$lookup(S_done.ENV, $ptascii("alias")) = (n_shared)',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_replacement_left)',
        '$lookup(S_done.ENV, $ptascii("right")) = (n_replacement_right)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_shared) = 1',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement_right) = 2',
        '$addassign_repair_review_warnings(S_done.EVENTS) = 1',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_left, 0) = S_left[.COMPLETION = BUDGET]',
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
