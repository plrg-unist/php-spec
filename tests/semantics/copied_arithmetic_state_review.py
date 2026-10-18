#!/usr/bin/env python3
"""Reached copied inputs, live versus frozen TypeError labels and cached floats."""
import base64
import json

import copied_arithmetic_review_cases as cases
import copied_arithmetic_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = r'''
dec $copied_arithmetic_review_diagnostic(pevent, text) : nat
def $copied_arithmetic_review_diagnostic(DIAGNOSTIC text n* z, text) = 1
def $copied_arithmetic_review_diagnostic(DIAGNOSTIC_SOURCE n_source text n* z, text) = 1
def $copied_arithmetic_review_diagnostic(DIAGNOSTIC_STACK text n* z n_trace*, text) = 1
def $copied_arithmetic_review_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n* z n_trace*, text) = 1
def $copied_arithmetic_review_diagnostic(pevent, text) = 0 -- otherwise
dec $copied_arithmetic_review_diagnostics(pevent*, text) : nat
def $copied_arithmetic_review_diagnostics(eps, text) = 0
def $copied_arithmetic_review_diagnostics(pevent :: pevent_tail*, text) = $($copied_arithmetic_review_diagnostic(pevent, text) + $copied_arithmetic_review_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    right_copy, left_copy, multiply = (name == item for item in CASES)
    operation = 'MULTIPLY' if multiply else ('SUBTRACT' if right_copy else 'ADD')
    left_number = 'NFLOAT 4623226492472524800' if multiply else 'NINT 12'
    result = 'PFLOAT 4634538268099084288' if multiply else 'PINT 100'
    phase = 'ARITHMETIC_RIGHT pnumber_left'
    convert = lambda part: f'ARITHMETIC_CV_CONVERT pintegeroperation ({part})'
    warning = lambda part, raw, number, stage: f'ARITHMETIC_CV_WARNING pintegeroperation ({part}) {raw} {number} {stage}'
    left_warning = lambda stage: warning('ARITHMETIC_LEFT', 'pvalue_left', 'pnumber_left', stage)
    right_warning = lambda stage: warning(phase, 'pvalue_right', 'pnumber_right', stage)
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $copied_arithmetic_seek({before}, {stage}, 5000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$copied_arithmetic_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_plan', 'S_initial', 0)
    checks += [
        '$arithmetic_copy_plan(S_plan) = (pintegeroperation)',
        '$arithmetic_copy_valid(S_plan, pintegeroperation)', '$arithmetic_cv_valid(S_plan, pintegeroperation)',
        '$arithmetic_cv_plan(S_plan) = eps', '$arithmetic_mixed_plan(S_plan) = eps',
        '$arithmetic_add_plan(S_plan) = eps', '$arithmetic_div_plan(S_plan) = eps',
        '$submul_warning_plan(S_plan) = eps', '$power_conversion_warning_plan(S_plan) = eps',
        'pintegeroperation.OP = ' + operation, '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
        '$arithmetic_add_selected(S_plan, pintegeroperation)',
        '$lookup(S_plan.ENV, $ptascii("left")) = (n_left)', '$lookup(S_plan.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_plan.ENV, $ptascii("calls")) = (n_calls)', '$lookup(S_plan.ENV, $ptascii("v")) = (n_v)',
        'n_left =/= n_right', 'S_plan.STORE[n_left] = DEFINED pvalue_left',
        'S_plan.STORE[n_right] = DEFINED pvalue_right',
        '$arithmetic_cv_value(S_plan, pintegeroperation.LEFTPOINTER) = (pvalue_left)',
        '$arithmetic_cv_value(S_plan, pintegeroperation.RIGHTPOINTER) = (pvalue_right)',
        'pintegeroperation.LEFTPOINTER = ' + ('INTEGER_CELL n_left' if right_copy else 'INTEGER_COPY pvalue_left'),
        'pintegeroperation.RIGHTPOINTER = ' + ('INTEGER_CV ($ptascii("right"))' if left_copy else 'INTEGER_COPY pvalue_right'),
        '$operand_nodes(pintegeroperation.LEFT) = eps', '$operand_nodes(pintegeroperation.RIGHT) = eps',
        'pnumber_left = ' + left_number,
        '$arithmetic_add_conversion(pvalue_left) = ((pnumber_left, ' + ('false' if multiply else 'true') + '))',
        '$string_bytes(pvalue_left) = ($ptascii("' + ('12.5' if multiply else '12tail') + '"))',
        '$string_bytes(pvalue_right) = ($ptascii("' + ('5.5tail' if multiply else 'bad') + '"))',
        'S_plan.STORE[n_calls] = DEFINED (PINT 0)', 'S_plan.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_plan)), HCELL n_left) = ' + ('2' if right_copy else '1'),
        '$heap_owners($heap_prune($heap_graph(S_plan)), HCELL n_right) = 1',
        '$call_descriptors_valid(S_plan)', '$heap_valid($heap_graph(S_plan))',
    ]
    if right_copy:
        checks += [
            'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23',
            'pintegeroperation.RIGHT = KNOWN pvalue_right',
            '$lookup(S_plan.ENV, $ptascii("leftAlias")) = (n_left)', 'n_left <- S_plan.REFCELLS',
        ]
    else:
        checks += ['pintegeroperation.LEFT = KNOWN pvalue_left', '~(n_left <- S_plan.REFCELLS)']
        checks += ['pintegeroperation.RIGHT = KNOWN pvalue_right'] if multiply else ['pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25']
    if multiply:
        checks += [
            '$integer_slot_rank(S_plan, pintegeroperation.SITE, [PCFIELD 0], pintegeroperation.LEFT) = (4)',
            '$integer_slot_rank(S_plan, pintegeroperation.SITE, [PCFIELD 1], pintegeroperation.RIGHT) = (2)',
        ]
    else:
        checks += ['$arithmetic_add_conversion(pvalue_right) = eps']
    step('S_begin', 'S_plan')
    checks += [
        'S_plan.TODO = ptask_old :: ptask_tail*',
        'S_begin = S_plan[.TODO = (' + convert('ARITHMETIC_LEFT') + ') :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$call_task_valid(S_begin, ' + convert('ARITHMETIC_LEFT') + ')',
        '$task_nodes(' + convert('ARITHMETIC_LEFT') + ') = eps',
    ]
    if not multiply:
        step('S_capture', 'S_begin')
        checks += [
            'S_capture = S_begin[.TODO = (' + left_warning(0) + ') :: ptask_tail*]',
            '$arithmetic_cv_warning_valid(S_capture, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, pnumber_left, 0)',
        ]
        step('S_first', 'S_capture')
        checks += [
            '$copied_arithmetic_frontier(S_first, 3)',
            'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
            'perrorcall_first.RESUME = ' + left_warning(1), 'perrorcall_first.TARGET = eps',
            'perrorcall_first.LEVEL = 2', 'perrorcall_first.LINE = 25', '$error_call_valid(S_first, perrorcall_first)',
        ]
        seek('S_entered', 'S_first', 10)
        checks += ['$plain_arithmetic_entered(S_entered.FRAMES, 0)', '$call_descriptors_valid(S_entered)']
        seek('S_return', 'S_entered', 4)
        checks += [
            'S_return.TODO = (' + left_warning(1) + ') :: ptask_tail*',
            '$arithmetic_cv_warning_valid(S_return, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, pnumber_left, 1)',
            'S_return.STORE[n_left] = DEFINED (PBOOL false)',
            'S_return.STORE[n_calls] = DEFINED (PINT 1)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
            'S_return.STRINGDATA[0:|S_plan.STRINGDATA|] = S_plan.STRINGDATA',
            '$copied_arithmetic_review_diagnostics(S_return.EVENTS, "Warning") = 1',
        ]
        checks += [
            'S_return.STORE[n_right] = DEFINED pvalue_repaired', '$string_bytes(pvalue_repaired) = ($ptascii("5tail"))',
            '$arithmetic_cv_value(S_return, pintegeroperation.RIGHTPOINTER) = (pvalue_right)',
            '$arithmetic_add_conversion(pvalue_repaired) = ((NINT 5, true))',
            '$integer_pointer_value(S_return, INTEGER_CV ($ptascii("right"))) = (pvalue_repaired)',
        ] if right_copy else [
            'S_return.STORE[n_right] = DEFINED pvalue_right',
            '$arithmetic_cv_value(S_return, pintegeroperation.LEFTPOINTER) = (pvalue_left)',
            '$integer_pointer_value(S_return, INTEGER_CV ($ptascii("left"))) = (PBOOL false)',
        ]
        step('S_pending', 'S_return')
        checks += [
            'S_pending = S_return[.TODO = (' + convert(phase) + ') :: ptask_tail*][.RESULT = KNOWN PNULL]',
            '$arithmetic_cv_failure_operands(S_pending, pintegeroperation, ' + phase + ') = ((' + ('PBOOL false' if right_copy else 'pvalue_left') + ', pvalue_right))',
            '$arithmetic_cv_failure_operands(S_pending, pintegeroperation, ARITHMETIC_LEFT) = eps',
        ]
        step('S_result', 'S_pending')
        checks += [
            '$copied_arithmetic_frontier(S_result, 9)', 'S_result.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
            'S_result.RESULT = KNOWN PNULL', 'S_result.CURRENT = eps', 'n_error = |S_pending.OBJECTS|',
            'S_result.OBJECTS[n_error] = THROWABLE pthrowable',
            'S_result.OBJECTS = S_pending.OBJECTS ++ [THROWABLE pthrowable]',
            'pthrowable.KIND = "TypeError"', 'pthrowable.ORIGIN = (pintegeroperation.SITE)',
            '$throwable_field(S_result, n_error, "line") = PINT 25',
            '$string_bytes($throwable_field(S_result, n_error, "message")) = ($ptascii("Unsupported operand types: ' + ('bool - string' if right_copy else 'string + string') + '"))',
            '$throwable_previous_id(S_result, n_error) = eps', '$throwable_live(S_result, n_error)',
            '$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]',
            '$heap_owners($heap_prune($heap_graph(S_result)), HOBJECT n_error) = 1',
            'S_result.STORE = S_pending.STORE', 'S_result.ENV = S_pending.ENV',
            'S_result.REFCELLS = S_pending.REFCELLS', 'S_result.EVENTS = S_pending.EVENTS',
            'S_result.STRINGDATA = S_pending.STRINGDATA',
            'S_result.ARRAYS[0:|S_pending.ARRAYS|] = S_pending.ARRAYS',
        ]
    else:
        step('S_pending', 'S_begin')
        checks += [
            'S_pending = S_begin[.TODO = (' + convert(phase) + ') :: ptask_tail*][.RESULT = KNOWN PNULL]',
            'S_pending.STORE[n_calls] = DEFINED (PINT 0)',
            'pnumber_right = NFLOAT 4617878467915022336',
            '$arithmetic_add_conversion(pvalue_right) = ((pnumber_right, true))',
        ]
        step('S_capture', 'S_pending')
        checks += [
            'S_capture = S_pending[.TODO = (' + right_warning(0) + ') :: ptask_tail*]',
            '$arithmetic_cv_warning_valid(S_capture, pintegeroperation, ' + phase + ', pvalue_right, pnumber_right, 0)',
        ]
        step('S_first', 'S_capture')
        checks += [
            '$copied_arithmetic_frontier(S_first, 7)',
            'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
            'perrorcall_first.RESUME = ' + right_warning(1), 'perrorcall_first.TARGET = eps',
            'perrorcall_first.LEVEL = 2', 'perrorcall_first.LINE = 25', '$error_call_valid(S_first, perrorcall_first)',
        ]
        seek('S_entered', 'S_first', 11)
        checks += ['$plain_arithmetic_entered(S_entered.FRAMES, 1)', '$call_descriptors_valid(S_entered)']
        seek('S_return', 'S_entered', 8)
        checks += [
            'S_return.TODO = (' + right_warning(1) + ') :: ptask_tail*',
            '$arithmetic_cv_warning_valid(S_return, pintegeroperation, ' + phase + ', pvalue_right, pnumber_right, 1)',
            '$arithmetic_cv_warning_valid(S_return, pintegeroperation, ' + phase + ', pvalue_right, pnumber_right, 0)',
            '$lookup(S_return.ENV, $ptascii("left")) = eps', '$lookup(S_return.ENV, $ptascii("right")) = eps',
            '$arithmetic_cv_value(S_return, pintegeroperation.LEFTPOINTER) = (pvalue_left)',
            '$arithmetic_cv_value(S_return, pintegeroperation.RIGHTPOINTER) = (pvalue_right)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_left) = 0',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 0',
            'S_return.STORE[n_calls] = DEFINED (PINT 1)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
            '$copied_arithmetic_review_diagnostics(S_return.EVENTS, "Warning") = 1',
            'S_return.STRINGDATA[0:|S_plan.STRINGDATA|] = S_plan.STRINGDATA',
            '$num_mul(pnumber_left, pnumber_right) = NFLOAT 4634538268099084288',
        ]
        step('S_result', 'S_return')
        checks += ['S_result = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (' + result + ')]']
    checks += [
        '~$plain_arithmetic_tasks(S_result.TODO)', '$call_descriptors_valid(S_result)',
        '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 5000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_done_left)',
        '$lookup(S_done.ENV, $ptascii("right")) = (n_done_right)',
        'S_done.STORE[n_done_left] = DEFINED (PINT ' + ('6' if right_copy else '7') + ')',
        'S_done.STORE[n_done_right] = DEFINED (PINT 8)',
        '$lookup(S_done.ENV, $ptascii("v")) = (n_done_v)', 'S_done.STORE[n_done_v] = DEFINED (' + result + ')',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        '$copied_arithmetic_review_diagnostics(S_done.EVENTS, "Warning") = 1',
        '$copied_arithmetic_review_diagnostics(S_done.EVENTS, "Deprecated") = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_plan, 0) = S_plan[.COMPLETION = BUDGET]', '$drive_steps(S_plan, 7000) = S_done',
    ]
    if right_copy:
        checks += [
            'n_done_left = n_left', '$lookup(S_done.ENV, $ptascii("leftAlias")) = (n_left)',
            '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_left) = 2',
            '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_left) = 2',
        ]
    if multiply:
        checks += ['n_done_left =/= n_left', 'n_done_right =/= n_right']
    return checks
