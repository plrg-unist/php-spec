#!/usr/bin/env python3
"""Reached owning result references, multiplicity and cancellation retirement."""
import base64
import json

import owned_arithmetic_review_cases as cases
import owned_arithmetic_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = r'''
dec $owned_arithmetic_review_diagnostic(pevent, text) : nat
def $owned_arithmetic_review_diagnostic(DIAGNOSTIC text n* z, text) = 1
def $owned_arithmetic_review_diagnostic(DIAGNOSTIC_SOURCE n_source text n* z, text) = 1
def $owned_arithmetic_review_diagnostic(DIAGNOSTIC_STACK text n* z n_trace*, text) = 1
def $owned_arithmetic_review_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n* z n_trace*, text) = 1
def $owned_arithmetic_review_diagnostic(pevent, text) = 0 -- otherwise
dec $owned_arithmetic_review_diagnostics(pevent*, text) : nat
def $owned_arithmetic_review_diagnostics(eps, text) = 0
def $owned_arithmetic_review_diagnostics(pevent :: pevent_tail*, text) = $($owned_arithmetic_review_diagnostic(pevent, text) + $owned_arithmetic_review_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    same, failure, zero = (name == item for item in CASES)
    operation = 'ADD' if same else ('SUBTRACT' if failure else 'DIVIDE')
    owned_name = 'shared' if same else ('left' if failure else 'right')
    roots = '[HCELL n_owned, HCELL n_owned]' if same else '[HCELL n_owned]'
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
            f'{state}_found = $owned_arithmetic_seek({before}, {stage}, 5000)',
            rf'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$owned_arithmetic_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    def owner(state, count):
        checks.append(f'$heap_owners($heap_prune($heap_graph({state})), HCELL n_owned) = {count}')

    seek('S_plan', 'S_initial', 0)
    checks += [
        '$arithmetic_owned_plan(S_plan) = (pintegeroperation)',
        '$arithmetic_owned_valid(S_plan, pintegeroperation)', '$arithmetic_cv_valid(S_plan, pintegeroperation)',
        '$arithmetic_cv_plan(S_plan) = eps', '$arithmetic_mixed_plan(S_plan) = eps', '$arithmetic_copy_plan(S_plan) = eps',
        '$arithmetic_add_plan(S_plan) = eps', '$arithmetic_div_plan(S_plan) = eps',
        '$submul_warning_plan(S_plan) = eps', '$power_conversion_warning_plan(S_plan) = eps',
        'pintegeroperation.OP = ' + operation, '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
        '$arithmetic_add_selected(S_plan, pintegeroperation)',
        '$lookup(S_plan.ENV, $ptascii("' + owned_name + '")) = (n_owned)',
        '$lookup(S_plan.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_plan.ENV, $ptascii("sourceCalls")) = (n_source_calls)',
        '$lookup(S_plan.ENV, $ptascii("v")) = (n_v)',
        'S_plan.STORE[n_calls] = DEFINED (PINT 0)',
        'S_plan.STORE[n_source_calls] = DEFINED (PINT ' + ('2' if same else '1') + ')',
        'S_plan.STORE[n_v] = DEFINED (PINT 100)',
        '$arithmetic_owned_cell_valid(S_plan, n_owned)', 'n_owned <- S_plan.REFCELLS',
        '(HCELL n_owned) <- S_plan.ALLOCATIONS',
        '$arithmetic_cv_value(S_plan, pintegeroperation.LEFTPOINTER) = (pvalue_left)',
        '$arithmetic_cv_value(S_plan, pintegeroperation.RIGHTPOINTER) = (' + ('pvalue_initial_right' if same else 'pvalue_right') + ')',
        'pnumber_left = NINT 12',
        '$arithmetic_add_conversion(pvalue_left) = ((pnumber_left, ' + ('false' if zero else 'true') + '))',
        '$operand_nodes(pintegeroperation.LEFT) ++ $operand_nodes(pintegeroperation.RIGHT) = ' + roots,
        '$call_descriptors_valid(S_plan)', '$heap_valid($heap_graph(S_plan))',
    ]
    owner('S_plan', 3 if same else 2)
    if same:
        checks += [
            'pintegeroperation.LEFT = REFERENCE n_owned', 'pintegeroperation.RIGHT = REFERENCE n_owned',
            'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_owned', 'pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_owned',
            'pvalue_left = pvalue_initial_right', 'S_plan.STORE[n_owned] = DEFINED pvalue_left',
            '$string_bytes(pvalue_left) = ($ptascii("12tail"))',
        ]
    else:
        checks += [
            'pintegeroperation.' + ('LEFT' if failure else 'RIGHT') + ' = REFERENCE n_owned',
            'pintegeroperation.' + ('LEFTPOINTER' if failure else 'RIGHTPOINTER') + ' = INTEGER_CELL n_owned',
            'pintegeroperation.' + ('RIGHT' if failure else 'LEFT') + ' = KNOWN ' + ('pvalue_right' if failure else 'pvalue_left'),
            'pintegeroperation.' + ('RIGHTPOINTER' if failure else 'LEFTPOINTER') + ' = INTEGER_COPY ' + ('pvalue_right' if failure else 'pvalue_left'),
            'S_plan.STORE[n_owned] = DEFINED ' + ('pvalue_left' if failure else 'pvalue_right'),
            '$string_bytes(' + ('pvalue_left' if failure else 'pvalue_right') + ') = ($ptascii("' + ('12tail' if failure else '0tail') + '"))',
        ]
        checks += ['$string_bytes(pvalue_right) = ($ptascii("bad"))', '$arithmetic_add_conversion(pvalue_right) = eps'] if failure else ['pvalue_left = PINT 12']
    step('S_begin', 'S_plan')
    checks += [
        'S_plan.TODO = ptask_old :: ptask_tail*',
        'S_begin = S_plan[.TODO = (' + convert('ARITHMETIC_LEFT') + ') :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$call_task_valid(S_begin, ' + convert('ARITHMETIC_LEFT') + ')',
        '$task_nodes(' + convert('ARITHMETIC_LEFT') + ') = ' + roots,
    ]
    owner('S_begin', 3 if same else 2)
    if zero:
        step('S_pending', 'S_begin')
        checks += [
            'S_pending = S_begin[.TODO = (' + convert(phase) + ') :: ptask_tail*][.RESULT = KNOWN PNULL]',
            'S_pending.STORE[n_calls] = DEFINED (PINT 0)', 'pnumber_right = NINT 0',
            '$arithmetic_add_conversion(pvalue_right) = ((pnumber_right, true))',
        ]
        step('S_capture', 'S_pending')
        checks += ['S_capture = S_pending[.TODO = (' + right_warning(0) + ') :: ptask_tail*]']
        raw, number, part, fresh_stage, entered_stage, return_stage = 'pvalue_right', 'pnumber_right', phase, 7, 11, 8
    else:
        step('S_capture', 'S_begin')
        checks += ['S_capture = S_begin[.TODO = (' + left_warning(0) + ') :: ptask_tail*]']
        raw, number, part, fresh_stage, entered_stage, return_stage = 'pvalue_left', 'pnumber_left', 'ARITHMETIC_LEFT', 3, 10, 4
    captured_warning = warning(part, raw, number, 0)
    returned_warning = warning(part, raw, number, 1)
    checks += [
        '$task_nodes(' + captured_warning + ') = ' + roots,
        '$arithmetic_cv_warning_valid(S_capture, pintegeroperation, ' + part + ', ' + raw + ', ' + number + ', 0)',
    ]
    step('S_first', 'S_capture')
    checks += [
        '$owned_arithmetic_frontier(S_first, ' + str(fresh_stage) + ')',
        'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
        'perrorcall_first.RESUME = ' + returned_warning, 'perrorcall_first.TARGET = eps',
        'perrorcall_first.LEVEL = 2', 'perrorcall_first.LINE = 25', '$error_call_valid(S_first, perrorcall_first)',
        '$task_nodes(perrorcall_first.RESUME) = ' + roots,
    ]
    seek('S_entered', 'S_first', entered_stage)
    checks += ['$plain_arithmetic_entered(S_entered.FRAMES, ' + ('1' if zero else '0') + ')', '$call_descriptors_valid(S_entered)']
    seek('S_return', 'S_entered', return_stage)
    checks += [
        'S_return.TODO = (' + returned_warning + ') :: ptask_tail*',
        '$arithmetic_cv_warning_valid(S_return, pintegeroperation, ' + part + ', ' + raw + ', ' + number + ', 1)',
        '$arithmetic_owned_valid(S_return, pintegeroperation)', '$arithmetic_owned_cell_valid(S_return, n_owned)',
        '$lookup(S_return.ENV, $ptascii("' + owned_name + '")) = eps',
        'S_return.STORE[n_calls] = DEFINED (PINT 1)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
        'S_return.STRINGDATA[0:|S_plan.STRINGDATA|] = S_plan.STRINGDATA',
        '$owned_arithmetic_review_diagnostics(S_return.EVENTS, "Warning") = ' + ('0' if same else '1'),
    ]
    owner('S_return', 2 if same else 1)
    if same:
        checks += [
            'S_return.STORE[n_owned] = DEFINED pvalue_right', '$string_bytes(pvalue_right) = ($ptascii("5tail"))',
            '$arithmetic_add_conversion(pvalue_right) = ((NINT 5, true))',
            '$arithmetic_cv_value(S_return, pintegeroperation.RIGHTPOINTER) = (pvalue_right)',
        ]
        step('S_pending', 'S_return')
        checks += ['S_pending = S_return[.TODO = (' + convert(phase) + ') :: ptask_tail*][.RESULT = KNOWN PNULL]', 'pnumber_right = NINT 5']
        step('S_second_capture', 'S_pending')
        checks += ['S_second_capture = S_pending[.TODO = (' + right_warning(0) + ') :: ptask_tail*]']
        step('S_second', 'S_second_capture')
        checks += [
            '$owned_arithmetic_frontier(S_second, 7)',
            'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
            'perrorcall_second.RESUME = ' + right_warning(1), 'perrorcall_second.TARGET = eps',
            '$error_call_valid(S_second, perrorcall_second)', '$task_nodes(perrorcall_second.RESUME) = ' + roots,
        ]
        seek('S_second_entered', 'S_second', 11)
        checks += ['$plain_arithmetic_entered(S_second_entered.FRAMES, 1)', '$call_descriptors_valid(S_second_entered)']
        seek('S_final', 'S_second_entered', 8)
        checks += [
            'S_final.TODO = (' + right_warning(1) + ') :: ptask_tail*',
            '$arithmetic_cv_warning_valid(S_final, pintegeroperation, ' + phase + ', pvalue_right, pnumber_right, 1)',
            '$lookup(S_final.ENV, $ptascii("shared")) = (n_fresh)', 'n_fresh =/= n_owned',
            'S_final.STORE[n_fresh] = DEFINED (PINT 88)', 'S_final.STORE[n_owned] = DEFINED pvalue_right',
            '$arithmetic_cv_value(S_final, pintegeroperation.RIGHTPOINTER) = (pvalue_right)',
            'S_final.STORE[n_calls] = DEFINED (PINT 2)', '$owned_arithmetic_review_diagnostics(S_final.EVENTS, "Warning") = 1',
        ]
        owner('S_final', 2)
        checks += [
            'PhpStep: S_final ~> S_atomic',
            'S_atomic = S_final[.TODO = ptask_tail*][.RESULT = KNOWN (PINT 17)]',
        ]
        step('S_result', 'S_final')
        checks += [
            'S_result.TODO = ptask_tail*', 'S_result.RESULT = KNOWN (PINT 17)',
            'S_result.STORE = S_final.STORE', 'S_result.ENV = S_final.ENV',
            'S_result.REFCELLS = S_final.REFCELLS', 'S_result.EVENTS = S_final.EVENTS',
            'S_result.STRINGDATA = S_final.STRINGDATA',
            '~((HCELL n_owned) <- S_result.ALLOCATIONS)',
            '$task_nodes(' + right_warning(1) + ') = [HCELL n_owned, HCELL n_owned]',
        ]
    else:
        if failure:
            checks += [
                'S_return.STORE[n_owned] = DEFINED (PBOOL false)',
                '$arithmetic_cv_value(S_return, pintegeroperation.LEFTPOINTER) = (PBOOL false)',
                '$arithmetic_cv_value(S_return, pintegeroperation.RIGHTPOINTER) = (pvalue_right)',
                '$lookup(S_return.ENV, $ptascii("right")) = (n_right)',
                'S_return.STORE[n_right] = DEFINED pvalue_repaired', '$string_bytes(pvalue_repaired) = ($ptascii("5tail"))',
                '$arithmetic_add_conversion(pvalue_repaired) = ((NINT 5, true))',
            ]
            step('S_pending', 'S_return')
            checks += [
                'S_pending = S_return[.TODO = (' + convert(phase) + ') :: ptask_tail*][.RESULT = KNOWN PNULL]',
                '$arithmetic_cv_failure_operands(S_pending, pintegeroperation, ' + phase + ') = ((PBOOL false, pvalue_right))',
            ]
            before = 'S_pending'
        else:
            checks += [
                'S_return.STORE[n_owned] = DEFINED (PINT 7)',
                '$arithmetic_cv_value(S_return, pintegeroperation.RIGHTPOINTER) = (PINT 7)',
            ]
            before = 'S_return'
        step('S_result', before)
        checks += [
            '$owned_arithmetic_frontier(S_result, 9)', 'S_result.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
            'S_result.RESULT = KNOWN PNULL', 'S_result.CURRENT = eps', 'n_error = |' + before + '.OBJECTS|',
            'S_result.OBJECTS[n_error] = THROWABLE pthrowable',
            'S_result.OBJECTS = ' + before + '.OBJECTS ++ [THROWABLE pthrowable]',
            'pthrowable.KIND = "' + ('TypeError' if failure else 'DivisionByZeroError') + '"',
            'pthrowable.ORIGIN = (pintegeroperation.SITE)',
            '$throwable_field(S_result, n_error, "line") = PINT 25',
            '$string_bytes($throwable_field(S_result, n_error, "message")) = ($ptascii("' + ('Unsupported operand types: bool - string' if failure else 'Division by zero') + '"))',
            '$throwable_previous_id(S_result, n_error) = eps', '$throwable_live(S_result, n_error)',
            '$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]',
            '$heap_owners($heap_prune($heap_graph(S_result)), HOBJECT n_error) = 1',
            'S_result.STORE = ' + before + '.STORE', 'S_result.ENV = ' + before + '.ENV',
            'S_result.REFCELLS = ' + before + '.REFCELLS', 'S_result.EVENTS = ' + before + '.EVENTS',
            'S_result.STRINGDATA = ' + before + '.STRINGDATA',
            'S_result.ARRAYS[0:|' + before + '.ARRAYS|] = ' + before + '.ARRAYS',
        ]
    owner('S_result', 0)
    checks += [
        '~$plain_arithmetic_tasks(S_result.TODO)', '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 5000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("' + owned_name + '")) = (n_done_owned)', 'n_done_owned =/= n_owned',
        'S_done.STORE[n_done_owned] = DEFINED (PINT ' + ('8' if zero else '7') + ')',
        '$lookup(S_done.ENV, $ptascii("v")) = (n_done_v)',
        'S_done.STORE[n_done_v] = DEFINED (PINT ' + ('17' if same else '100') + ')',
        'S_done.STORE[n_calls] = DEFINED (PINT ' + ('2' if same else '1') + ')',
        'S_done.STORE[n_source_calls] = DEFINED (PINT ' + ('2' if same else '1') + ')',
        '$owned_arithmetic_review_diagnostics(S_done.EVENTS, "Warning") = 1',
        '$owned_arithmetic_review_diagnostics(S_done.EVENTS, "Deprecated") = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_plan, 0) = S_plan[.COMPLETION = BUDGET]', '$drive_steps(S_plan, 7000) = S_done',
    ]
    owner('S_done', 0)
    if not same:
        checks += [
            '$lookup(S_done.ENV, $ptascii("left")) = (n_done_left)', '$lookup(S_done.ENV, $ptascii("right")) = (n_done_right)',
            'S_done.STORE[n_done_left] = DEFINED (PINT 7)', 'S_done.STORE[n_done_right] = DEFINED (PINT 8)',
        ]
    return checks
