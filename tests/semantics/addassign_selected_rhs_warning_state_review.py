#!/usr/bin/env python3
"""Selected += stores held numbers through the old target after RHS retirement."""
import base64
import json

import addassign_selected_rhs_warning_review_cases as cases
import addassign_selected_rhs_warning_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = r'''
dec $selected_rhs_review_diagnostic(pevent, text) : nat
def $selected_rhs_review_diagnostic(DIAGNOSTIC text n* z, text) = 1
def $selected_rhs_review_diagnostic(DIAGNOSTIC_SOURCE n_source text n* z, text) = 1
def $selected_rhs_review_diagnostic(DIAGNOSTIC_STACK text n* z n_trace*, text) = 1
def $selected_rhs_review_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n* z n_trace*, text) = 1
def $selected_rhs_review_diagnostic(pevent, text) = 0 -- otherwise
dec $selected_rhs_review_diagnostics(pevent*, text) : nat
def $selected_rhs_review_diagnostics(eps, text) = 0
def $selected_rhs_review_diagnostics(pevent :: pevent_tail*, text) = $($selected_rhs_review_diagnostic(pevent, text) + $selected_rhs_review_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    left_number = 'NFLOAT 4623226492472524800'
    right_number = 'NFLOAT 4617878467915022336'
    result = 'PFLOAT 4625759767262920704'
    old = lambda stage: f'ARITHMETIC_ADDASSIGN_WARNING pintegeroperation pvalue_left ({left_number}) {stage}'
    right = lambda stage: f'ARITHMETIC_ADDASSIGN_RIGHT_WARNING pintegeroperation pvalue_left ({left_number}) pvalue_right ({right_number}) {stage}'
    valid = lambda state, stage: f'$arithmetic_addassign_right_warning_valid({state}, pintegeroperation, pvalue_left, {left_number}, pvalue_right, {right_number}, {stage})'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $selected_rhs_warning_seek({before}, {stage}, 5000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$selected_rhs_warning_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$arithmetic_addassign_plan(S_entry) = ((pintegeroperation, pvalue_left, ' + left_number + '))',
        '$arithmetic_addassign_source(S_entry, pintegeroperation)', '$arithmetic_add_selected(S_entry, pintegeroperation)',
        '$arithmetic_addassign_cv_plan(S_entry) = eps',
        'pintegeroperation.OP = ADD', '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_left',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_right', 'n_left =/= n_right',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("replacementLeft")) = (n_replacement_left)',
        '$lookup(S_entry.ENV, $ptascii("replacementRight")) = (n_replacement_right)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'S_entry.STORE[n_left] = DEFINED pvalue_left',
        '$string_bytes(pvalue_left) = ($ptascii("12.5tail"))', '$string_carrier_valid(S_entry, pvalue_left)',
        'S_entry.STORE[n_right] = DEFINED (PINT 2)',
        'S_entry.STORE[n_replacement_left] = DEFINED (PINT 77)',
        'S_entry.STORE[n_replacement_right] = DEFINED (PINT 7)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', 'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 2',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'S_entry.TODO = ptask_old :: ptask_tail*', 'PhpStep: S_entry ~> S_begin',
        'S_begin = S_entry[.TODO = (' + old(0) + ') :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = ROOT n_left]',
    ]
    step('S_first', 'S_begin')
    checks += [
        'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_left) :: ptask_tail*',
        'perrorcall_left.RESUME = ' + old(1), 'perrorcall_left.TARGET = eps',
        'perrorcall_left.LEVEL = 2', 'perrorcall_left.LINE = 25', '$error_call_valid(S_first, perrorcall_left)',
    ]
    seek('S_first_entered', 'S_first', 3)
    checks += ['$selected_rhs_warning_entered(S_first_entered.FRAMES, 0)', '$call_descriptors_valid(S_first_entered)']
    seek('S_left', 'S_first_entered', 4)
    checks += [
        'S_left.TODO = (' + old(1) + ') :: ptask_tail*',
        'S_left.STORE[n_left] = DEFINED (PINT 99)', 'S_left.STORE[n_right] = DEFINED pvalue_right',
        '$string_bytes(pvalue_right) = ($ptascii("5.5tail"))',
        '$arithmetic_add_conversion(pvalue_right) = ((' + right_number + ', true))',
        'S_left.STORE[n_calls] = DEFINED (PINT 1)', 'S_left.STORE[n_v] = DEFINED (PINT 100)',
        '$lookup(S_left.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_left.ENV, $ptascii("right")) = (n_replacement_right)',
        '$lookup(S_left.ENV, $ptascii("replacementRight")) = (n_replacement_right)',
        'n_right =/= n_replacement_right',
        '$integer_pointer_select(S_left, pintegeroperation.RIGHT) = (INTEGER_CELL n_replacement_right)',
        '$integer_pointer_value(S_left, pintegeroperation.RIGHTPOINTER) = (pvalue_right)',
        '$arithmetic_addassign_source(S_left, pintegeroperation)', '~$arithmetic_add_selected(S_left, pintegeroperation)',
        '$arithmetic_addassign_warning_valid(S_left, pintegeroperation, pvalue_left, ' + left_number + ', 1)',
        '$arithmetic_addassign_ready(S_left, pintegeroperation) = eps',
        '$arithmetic_addassign_right_snapshot(S_left, pintegeroperation) = ((pvalue_right, ' + right_number + '))',
        '$heap_owners($heap_prune($heap_graph(S_left)), HCELL n_right) = 1',
        '$heap_owners($heap_prune($heap_graph(S_left)), HCELL n_replacement_right) = 2',
        '$selected_rhs_review_diagnostics(S_left.EVENTS, "Warning") = 0',
        'PhpStep: S_left ~> S_capture',
        'S_capture = S_left[.TODO = (' + right(0) + ') :: ptask_tail*]', valid('S_capture', 0),
        '$task_nodes(' + right(0) + ') = eps',
    ]
    step('S_second', 'S_capture')
    checks += [
        'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_right) :: ptask_tail*',
        'perrorcall_right.RESUME = ' + right(1), 'perrorcall_right.TARGET = eps',
        'perrorcall_right.LEVEL = 2', 'perrorcall_right.LINE = 25', '$error_call_valid(S_second, perrorcall_right)',
        '$call_descriptors_valid(S_second)',
    ]
    seek('S_second_entered', 'S_second', 7)
    checks += ['$selected_rhs_warning_entered(S_second_entered.FRAMES, 1)', '$call_descriptors_valid(S_second_entered)']
    seek('S_return', 'S_second_entered', 8)
    checks += [
        'S_return.TODO = (' + right(1) + ') :: ptask_tail*',
        'S_return.STORE[n_left] = DEFINED (PINT 88)', 'S_return.STORE[n_calls] = DEFINED (PINT 2)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)',
        '$lookup(S_return.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_return.ENV, $ptascii("left")) = (n_replacement_left)',
        '$lookup(S_return.ENV, $ptascii("replacementLeft")) = (n_replacement_left)',
        'n_left =/= n_replacement_left',
        '$lookup(S_return.ENV, $ptascii("rightAlias")) = eps',
        '$lookup(S_return.ENV, $ptascii("right")) = (n_replacement_right)',
        'S_return.STORE[n_replacement_left] = DEFINED (PINT 77)',
        'S_return.STORE[n_replacement_right] = DEFINED (PINT 7)',
        '$integer_pointer_select(S_return, pintegeroperation.LEFT) = (INTEGER_CELL n_replacement_left)',
        '$integer_pointer_value(S_return, pintegeroperation.LEFTPOINTER) = (PINT 88)',
        '$integer_pointer_value(S_return, pintegeroperation.RIGHTPOINTER) = eps',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 0',
        '~((HCELL n_right) <- S_return.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_replacement_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_replacement_right) = 2',
        valid('S_return', 1), '~' + valid('S_return', 0),
        '$arithmetic_addassign_right_snapshot(S_return, pintegeroperation) = eps',
        '$arithmetic_addassign_right_target(S_return, pintegeroperation)',
        '$selected_rhs_review_diagnostics(S_return.EVENTS, "Warning") = 1',
        'S_return.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'PhpStep: S_return ~> S_atomic',
        'S_atomic = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (' + result + ')][.LOCATION = ROOT n_left][.STORE[n_left] = DEFINED (' + result + ')]',
        '|S_atomic.STORE| = |S_return.STORE|',
        'S_atomic.ENV = S_return.ENV', 'S_atomic.REFCELLS = S_return.REFCELLS',
        '~$selected_rhs_warning_tasks(S_atomic.TODO)',
    ]
    step('S_result', 'S_return')
    checks += [
        'S_result.TODO = S_atomic.TODO', 'S_result.RESULT = S_atomic.RESULT',
        'S_result.STORE = S_atomic.STORE', 'S_result.ENV = S_atomic.ENV',
        'S_result.REFCELLS = S_atomic.REFCELLS', 'S_result.LOCATION = ROOT n_left',
        '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_left) = 1',
        '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 5000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_v] = DEFINED (' + result + ')', 'S_done.STORE[n_calls] = DEFINED (PINT 2)',
        '$lookup(S_done.ENV, $ptascii("leftAlias")) = (n_left)', 'S_done.STORE[n_left] = DEFINED (PINT 6)',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_replacement_left)',
        '$lookup(S_done.ENV, $ptascii("replacementLeft")) = (n_replacement_left)',
        'S_done.STORE[n_replacement_left] = DEFINED (PINT 8)',
        '$lookup(S_done.ENV, $ptascii("right")) = (n_replacement_right)',
        '$lookup(S_done.ENV, $ptascii("replacementRight")) = (n_replacement_right)',
        'S_done.STORE[n_replacement_right] = DEFINED (PINT 7)',
        '$lookup(S_done.ENV, $ptascii("rightAlias")) = eps',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_right) = 0',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement_right) = 2',
        '$selected_rhs_review_diagnostics(S_done.EVENTS, "Warning") = 1',
        '$selected_rhs_review_diagnostics(S_done.EVENTS, "Deprecated") = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_entry, 7000) = S_done',
        '$drive_steps(S_second, 0) = S_second[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
