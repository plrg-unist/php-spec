#!/usr/bin/env python3
"""Converted signed power preserves captured numbers through final Deprecated."""
import base64
import json

import powerassign_conversion_warning_review_cases as cases
import powerassign_conversion_warning_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = r'''
dec $powerassign_conversion_review_diagnostic(pevent, text) : nat
def $powerassign_conversion_review_diagnostic(DIAGNOSTIC text n* z, text) = 1
def $powerassign_conversion_review_diagnostic(DIAGNOSTIC_SOURCE n_source text n* z, text) = 1
def $powerassign_conversion_review_diagnostic(DIAGNOSTIC_STACK text n* z n_trace*, text) = 1
def $powerassign_conversion_review_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n* z n_trace*, text) = 1
def $powerassign_conversion_review_diagnostic(pevent, text) = 0 -- otherwise
dec $powerassign_conversion_review_diagnostics(pevent*, text) : nat
def $powerassign_conversion_review_diagnostics(eps, text) = 0
def $powerassign_conversion_review_diagnostics(pevent :: pevent_tail*, text) = $($powerassign_conversion_review_diagnostic(pevent, text) + $powerassign_conversion_review_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    left_number = 'NFLOAT 9223372036854775808'
    right_number = 'NINT $(-3)'
    right_phase = 'ARITHMETIC_RIGHT (' + left_number + ')'
    warning = lambda phase, raw, number, stage: f'ARITHMETIC_POWERASSIGN_WARNING pintegeroperation ({phase}) {raw} ({number}) {stage}'
    deprecated = lambda stage: f'POWER_ASSIGN_CONVERTED_DEPRECATED pintegeroperation ({left_number}) ({right_number}) {stage} eps'
    deprecated_valid = lambda state, stage: f'$powerassign_converted_deprecated_valid({state}, pintegeroperation, {left_number}, {right_number}, {stage}, eps)'
    valid = lambda state, phase, raw, number, stage: f'$arithmetic_powerassign_warning_valid({state}, pintegeroperation, {phase}, {raw}, {number}, {stage})'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $powerassign_conversion_seek({before}, {stage}, 5000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$powerassign_conversion_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$arithmetic_powerassign_plan(S_entry) = (pintegeroperation)',
        '$arithmetic_powerassign_source(S_entry, pintegeroperation)',
        '$arithmetic_div_plan(S_entry) = eps', '$arithmetic_addassign_plan(S_entry) = eps',
        'pintegeroperation.OP = POWER', '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
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
        '$string_bytes(pvalue_left) = ($ptascii("-0.0tail"))', '$string_carrier_valid(S_entry, pvalue_left)',
        'S_entry.STORE[n_right] = DEFINED (PINT 2)',
        'S_entry.STORE[n_replacement_left] = DEFINED (PINT 77)',
        'S_entry.STORE[n_replacement_right] = DEFINED (PINT 7)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', 'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 2',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'S_entry.TODO = ptask_old :: ptask_tail*', 'PhpStep: S_entry ~> S_begin',
        'S_begin = S_entry[.TODO = (ARITHMETIC_POWERASSIGN_CONVERT pintegeroperation ARITHMETIC_LEFT) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = ROOT n_left]',
    ]
    seek('S_first', 'S_begin', 3)
    checks += [
        'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_left) :: ptask_tail*',
        'perrorcall_left.RESUME = ' + warning('ARITHMETIC_LEFT', 'pvalue_left', left_number, 1),
        'perrorcall_left.TARGET = eps', 'perrorcall_left.LEVEL = 2', 'perrorcall_left.LINE = 25',
        '$error_call_valid(S_first, perrorcall_left)', '$call_descriptors_valid(S_first)',
        '$powerassign_conversion_review_diagnostics(S_first.EVENTS, "Warning") = 0',
    ]
    seek('S_first_entered', 'S_first', 11)
    checks += ['$powerassign_conversion_entered(S_first_entered.FRAMES, 0)', '$call_descriptors_valid(S_first_entered)']
    seek('S_left', 'S_first_entered', 4)
    checks += [
        'S_left.TODO = (' + warning('ARITHMETIC_LEFT', 'pvalue_left', left_number, 1) + ') :: ptask_tail*',
        'S_left.STORE[n_left] = DEFINED (PINT 99)', 'S_left.STORE[n_right] = DEFINED pvalue_right',
        '$string_bytes(pvalue_right) = ($ptascii("-3tail"))',
        '$arithmetic_add_conversion(pvalue_right) = ((NINT $(-3), true))',
        'S_left.STORE[n_calls] = DEFINED (PINT 1)', 'S_left.STORE[n_v] = DEFINED (PINT 100)',
        '$lookup(S_left.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_left.ENV, $ptascii("right")) = (n_replacement_right)',
        '$lookup(S_left.ENV, $ptascii("replacementRight")) = (n_replacement_right)',
        'n_right =/= n_replacement_right',
        '$integer_pointer_select(S_left, pintegeroperation.RIGHT) = (INTEGER_CELL n_replacement_right)',
        '$integer_pointer_value(S_left, pintegeroperation.RIGHTPOINTER) = (pvalue_right)',
        '$arithmetic_powerassign_source(S_left, pintegeroperation)', '~$arithmetic_add_selected(S_left, pintegeroperation)',
        valid('S_left', 'ARITHMETIC_LEFT', 'pvalue_left', left_number, 1),
        '~' + valid('S_left', 'ARITHMETIC_LEFT', 'pvalue_left', left_number, 0),
        '$heap_owners($heap_prune($heap_graph(S_left)), HCELL n_right) = 1',
        '$heap_owners($heap_prune($heap_graph(S_left)), HCELL n_replacement_right) = 2',
    ]
    seek('S_capture', 'S_left', 6)
    checks += [
        'S_capture.TODO = (' + warning(right_phase, 'pvalue_right', 'NINT $(-3)', 0) + ') :: ptask_tail*',
        '$arithmetic_powerassign_input(S_capture, pintegeroperation, ' + right_phase + ') = (pvalue_right)',
        valid('S_capture', right_phase, 'pvalue_right', 'NINT $(-3)', 0),
        '$task_nodes(' + warning(right_phase, 'pvalue_right', 'NINT $(-3)', 0) + ') = eps',
        'pvalue_counterfeit = PSTRING ($ptascii("7tail"))',
        'S_current_counterfeit = S_capture[.STORE[n_replacement_right] = DEFINED pvalue_counterfeit]',
        '~' + valid('S_current_counterfeit', right_phase, 'pvalue_counterfeit', 'NINT 7', 0),
        'S_capture.STORE = S_left.STORE', 'S_capture.EVENTS = S_left.EVENTS',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
    ]
    step('S_second', 'S_capture')
    checks += [
        'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_right) :: ptask_tail*',
        'perrorcall_right.RESUME = ' + warning(right_phase, 'pvalue_right', 'NINT $(-3)', 1),
        'perrorcall_right.TARGET = eps', 'perrorcall_right.LEVEL = 2', 'perrorcall_right.LINE = 25',
        '$error_call_valid(S_second, perrorcall_right)', '$call_descriptors_valid(S_second)',
    ]
    seek('S_second_entered', 'S_second', 12)
    checks += ['$powerassign_conversion_entered(S_second_entered.FRAMES, 1)', '$call_descriptors_valid(S_second_entered)']
    seek('S_return', 'S_second_entered', 8)
    checks += [
        'S_return.TODO = (' + warning(right_phase, 'pvalue_right', 'NINT $(-3)', 1) + ') :: ptask_tail*',
        'S_return.STORE[n_left] = DEFINED (PINT 88)', 'S_return.STORE[n_right] = DEFINED (PINT 7)',
        'S_return.STORE[n_calls] = DEFINED (PINT 2)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
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
        '$arithmetic_powerassign_input(S_return, pintegeroperation, ' + right_phase + ') = eps',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 0',
        '~((HCELL n_right) <- S_return.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_replacement_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_replacement_right) = 2',
        valid('S_return', right_phase, 'pvalue_right', 'NINT $(-3)', 1),
        '~' + valid('S_return', right_phase, 'pvalue_right', 'NINT $(-3)', 0),
        '$arithmetic_powerassign_target(S_return, pintegeroperation)',
        '$powerassign_conversion_review_diagnostics(S_return.EVENTS, "Warning") = 0',
        'S_return.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'PhpStep: S_return ~> S_prepare_atomic',
        'S_prepare_atomic = S_return[.TODO = (' + deprecated(0) + ') :: ptask_tail*]',
    ]
    step('S_prepare', 'S_return')
    checks += [
        '$powerassign_conversion_frontier(S_prepare, 13)',
        'S_prepare.TODO = (' + deprecated(0) + ') :: ptask_tail*',
        deprecated_valid('S_prepare', 0),
        '$call_task_valid(S_prepare, ' + deprecated(0) + ')',
        '$task_nodes(' + deprecated(0) + ') = eps',
        'S_prepare.STORE = S_return.STORE', 'S_prepare.EVENTS = S_return.EVENTS',
        '~$powerassign_selected_warning_valid(S_prepare, pintegeroperation, n_left, ' + left_number + ', ' + right_number + ', 0, eps)',
        '~' + deprecated_valid('S_prepare[.STORE[n_left] = DEFINED (PSTRING ($ptascii("88tail")))]', 0),
        '$call_descriptors_valid(S_prepare)',
    ]
    step('S_third', 'S_prepare')
    checks += [
        'S_third.TODO = (ERROR_HANDLER_INVOKE perrorcall_final) :: ptask_tail*',
        'perrorcall_final.RESUME = ' + deprecated(1),
        'perrorcall_final.TARGET = eps', 'perrorcall_final.LEVEL = 8192',
        'perrorcall_final.LINE = 25', 'perrorcall_final.SITE = pintegeroperation.SITE',
        'perrorcall_final.MESSAGE = $ptascii("Power of base 0 and negative exponent is deprecated")',
        '$error_call_valid(S_third, perrorcall_final)', '$call_descriptors_valid(S_third)',
        'S_third.STORE[n_calls] = DEFINED (PINT 2)', 'S_third.STORE[n_left] = DEFINED (PINT 88)',
        '$powerassign_conversion_review_diagnostics(S_third.EVENTS, "Warning") = 0',
        '$powerassign_conversion_review_diagnostics(S_third.EVENTS, "Deprecated") = 0',
    ]
    seek('S_third_entered', 'S_third', 15)
    checks += ['$powerassign_conversion_entered(S_third_entered.FRAMES, 2)', '$call_descriptors_valid(S_third_entered)']
    seek('S_final', 'S_third_entered', 16)
    checks += [
        'S_final.TODO = (' + deprecated(1) + ') :: ptask_tail*',
        deprecated_valid('S_final', 1),
        'S_final.STORE[n_left] = DEFINED (PINT 66)', 'S_final.STORE[n_right] = DEFINED (PINT 7)',
        'S_final.STORE[n_v] = DEFINED (PINT 100)', 'S_final.STORE[n_calls] = DEFINED (PINT 3)',
        '$lookup(S_final.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_final.ENV, $ptascii("left")) = (n_replacement_left)',
        '$lookup(S_final.ENV, $ptascii("right")) = (n_replacement_right)',
        '$lookup(S_final.ENV, $ptascii("rightAlias")) = eps',
        'S_final.STORE[n_replacement_left] = DEFINED (PINT 77)',
        'S_final.STORE[n_replacement_right] = DEFINED (PINT 7)',
        '$integer_pointer_value(S_final, pintegeroperation.RIGHTPOINTER) = eps',
        '$arithmetic_powerassign_target(S_final, pintegeroperation)',
        '$heap_owners($heap_prune($heap_graph(S_final)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_final)), HCELL n_right) = 0',
        '~((HCELL n_right) <- S_final.ALLOCATIONS)',
        '$powerassign_conversion_review_diagnostics(S_final.EVENTS, "Warning") = 0',
        '$powerassign_conversion_review_diagnostics(S_final.EVENTS, "Deprecated") = 1',
        'S_final.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_final)', '$heap_valid($heap_graph(S_final))',
        'PhpStep: S_final ~> S_atomic',
        'S_atomic = S_final[.TODO = ptask_tail*][.RESULT = KNOWN (PFLOAT 18442240474082181120)][.LOCATION = ROOT n_left][.STORE[n_left] = DEFINED (PFLOAT 18442240474082181120)]',
    ]
    step('S_result', 'S_final')
    checks += [
        'S_result.RESULT = KNOWN (PFLOAT 18442240474082181120)',
        'S_result.TODO = ptask_tail*', 'S_result.LOCATION = ROOT n_left',
        'S_result.STORE = S_atomic.STORE', 'S_result.STORE[n_v] = DEFINED (PINT 100)',
        'S_result.ENV = S_final.ENV', 'S_result.REFCELLS = S_final.REFCELLS',
        'S_result.ALLOCATIONS = S_final.ALLOCATIONS',
        'S_result.EVENTS = S_final.EVENTS', 'S_result.STRINGDATA = S_final.STRINGDATA',
        'S_result.ARRAYS = S_final.ARRAYS', 'S_result.OBJECTS = S_final.OBJECTS',
        '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_right) = 0',
        '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_replacement_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_replacement_right) = 2',
        '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 5000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_v] = DEFINED (PFLOAT 18442240474082181120)', 'S_done.STORE[n_calls] = DEFINED (PINT 3)',
        '$lookup(S_done.ENV, $ptascii("leftAlias")) = (n_left)', 'S_done.STORE[n_left] = DEFINED (PINT 6)',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_replacement_left)',
        '$lookup(S_done.ENV, $ptascii("replacementLeft")) = (n_replacement_left)',
        'S_done.STORE[n_replacement_left] = DEFINED (PINT 8)',
        '$lookup(S_done.ENV, $ptascii("right")) = (n_replacement_right)',
        '$lookup(S_done.ENV, $ptascii("replacementRight")) = (n_replacement_right)',
        'S_done.STORE[n_replacement_right] = DEFINED (PINT 9)',
        '$lookup(S_done.ENV, $ptascii("rightAlias")) = eps',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_right) = 0',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement_right) = 2',
        '$powerassign_conversion_review_diagnostics(S_done.EVENTS, "Warning") = 0',
        '$powerassign_conversion_review_diagnostics(S_done.EVENTS, "Deprecated") = 1',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
        '$drive_steps(S_final, 0) = S_final[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
