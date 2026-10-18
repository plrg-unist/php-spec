#!/usr/bin/env python3
"""Reached quiet negative-zero copy remains historical after both origins vanish."""
import base64
import json

import quiet_power_copy_review_cases as cases
import quiet_power_copy_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = r'''
dec $quiet_power_copy_review_diagnostic(pevent, text) : nat
def $quiet_power_copy_review_diagnostic(DIAGNOSTIC text n* z, text) = 1
def $quiet_power_copy_review_diagnostic(DIAGNOSTIC_SOURCE n_source text n* z, text) = 1
def $quiet_power_copy_review_diagnostic(DIAGNOSTIC_STACK text n* z n_trace*, text) = 1
def $quiet_power_copy_review_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n* z n_trace*, text) = 1
def $quiet_power_copy_review_diagnostic(pevent, text) = 0 -- otherwise
dec $quiet_power_copy_review_diagnostics(pevent*, text) : nat
def $quiet_power_copy_review_diagnostics(eps, text) = 0
def $quiet_power_copy_review_diagnostics(pevent :: pevent_tail*, text) = $($quiet_power_copy_review_diagnostic(pevent, text) + $quiet_power_copy_review_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    zero = 'NFLOAT 9223372036854775808'
    exponent = 'NINT (-3)'
    marker = lambda stage: f'ARITHMETIC_CV_DEPRECATED pintegeroperation ({zero}) ({exponent}) {stage}'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $quiet_power_copy_seek({before}, {stage}, 5000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$quiet_power_copy_frontier({state}, {stage})',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$quiet_power_copy_plan(S_entry) = ((pintegeroperation, ' + zero + ', ' + exponent + '))',
        '$arithmetic_copy_valid(S_entry, pintegeroperation)', '$arithmetic_cv_valid(S_entry, pintegeroperation)',
        '$arithmetic_copy_plan(S_entry) = eps', '$arithmetic_cv_plan(S_entry) = eps',
        '$power_warning_plan(S_entry) = eps', '$power_conversion_warning_plan(S_entry) = eps',
        '$error_handler_eligible(S_entry, 8192)', '~$error_handler_eligible(S_entry, 2)',
        '$arithmetic_add_named(S_entry)', 'pintegeroperation.OP = POWER', '~pintegeroperation.SWAPPED',
        'pintegeroperation.LINE = 25', 'pintegeroperation.LEFT = KNOWN pvalue_left',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_COPY pvalue_left',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))',
        '$integer_slot_rank(S_entry, pintegeroperation.SITE, [PCFIELD 0], pintegeroperation.LEFT) = (2)',
        '$integer_slot_rank(S_entry, pintegeroperation.SITE, [PCFIELD 1], pintegeroperation.RIGHT) = (8)',
        '$operand_nodes(pintegeroperation.LEFT) = eps', '$operand_nodes(pintegeroperation.RIGHT) = eps',
        'pvalue_left = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("-0.0"))',
        'S_entry.STRINGDATA[n_string] = $ptascii("-0.0")', '$string_carrier_valid(S_entry, pvalue_left)',
        '$arithmetic_add_conversion(pvalue_left) = ((' + zero + ', false))',
        '$arithmetic_add_conversion(PINT (-3)) = ((' + exponent + ', false))',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'S_entry.STORE[n_left] = DEFINED pvalue_left', 'S_entry.STORE[n_right] = DEFINED (PINT (-3))',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', 'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '~(n_left <- S_entry.REFCELLS)', '~(n_right <- S_entry.REFCELLS)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 1',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'S_entry.TODO = ptask_old :: ptask_tail*',
        'PhpStep: S_entry ~> S_begin',
        'S_begin = S_entry[.TODO = (' + marker(0) + ') :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$arithmetic_cv_deprecated_valid(S_begin, pintegeroperation, ' + zero + ', ' + exponent + ', 0)',
        '$task_nodes(' + marker(0) + ') = eps',
        'S_final_budget = $drive_steps(S_begin, 1)', 'S_final_budget.COMPLETION = BUDGET',
        'S_final = S_final_budget[.COMPLETION = NORMAL]', '$plain_arithmetic_frontier(S_final, 13)',
        'S_final.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(1), 'perrorcall.TARGET = eps',
        'perrorcall.SITE = pintegeroperation.SITE', 'perrorcall.LINE = 25', 'perrorcall.LEVEL = 8192',
        'perrorcall.MESSAGE = $ptascii("Power of base 0 and negative exponent is deprecated")',
        '$error_call_valid(S_final, perrorcall)',
    ]
    seek('S_entered', 'S_final', 14)
    checks += ['$plain_arithmetic_entered(S_entered.FRAMES, 2)', '$call_descriptors_valid(S_entered)']
    seek('S_return', 'S_entered', 15)
    checks += [
        'S_return.TODO = (' + marker(1) + ') :: ptask_tail*',
        '$lookup(S_return.ENV, $ptascii("left")) = eps', '$lookup(S_return.ENV, $ptascii("right")) = eps',
        '$arithmetic_cv_value(S_return, INTEGER_CV ($ptascii("left"))) = eps',
        '$arithmetic_cv_value(S_return, INTEGER_CV ($ptascii("right"))) = eps',
        'S_return.STORE[n_calls] = DEFINED (PINT 1)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_left) = 0',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 0',
        '~((HCELL n_left) <- S_return.ALLOCATIONS)', '~((HCELL n_right) <- S_return.ALLOCATIONS)',
        'S_return.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        'S_return.STRINGDATA[n_string] = $ptascii("-0.0")', '$string_carrier_valid(S_return, pvalue_left)',
        '$arithmetic_cv_deprecated_valid(S_return, pintegeroperation, ' + zero + ', ' + exponent + ', 1)',
        '$quiet_power_copy_review_diagnostics(S_return.EVENTS, "Warning") = 0',
        '$quiet_power_copy_review_diagnostics(S_return.EVENTS, "Deprecated") = 1',
        'S_return.ERRORHANDLER = S_entry.ERRORHANDLER',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'PhpStep: S_return ~> S_atomic',
        'S_atomic = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (PFLOAT 18442240474082181120)]',
        'S_result_budget = $drive_steps(S_return, 1)', 'S_result_budget.COMPLETION = BUDGET',
        'S_result = S_result_budget[.COMPLETION = NORMAL]',
        'S_result.RESULT = KNOWN (PFLOAT 18442240474082181120)', 'S_result.TODO = ptask_tail*',
        'S_result.STORE = S_return.STORE', 'S_result.ENV = S_return.ENV',
        'S_result.REFCELLS = S_return.REFCELLS', 'S_result.EVENTS = S_return.EVENTS',
        'S_result.STRINGDATA = S_return.STRINGDATA',
        'S_done = $drive_steps(S_result, 5000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_v] = DEFINED (PFLOAT 18442240474082181120)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_new_left)',
        '$lookup(S_done.ENV, $ptascii("right")) = (n_new_right)',
        'n_new_left =/= n_left', 'n_new_right =/= n_right',
        'S_done.STORE[n_new_left] = DEFINED (PINT 7)', 'S_done.STORE[n_new_right] = DEFINED (PINT 8)',
        '$quiet_power_copy_review_diagnostics(S_done.EVENTS, "Warning") = 0',
        '$quiet_power_copy_review_diagnostics(S_done.EVENTS, "Deprecated") = 1',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_entry, 6000) = S_done', '$drive_steps(S_final, 0) = S_final[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
