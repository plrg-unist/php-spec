#!/usr/bin/env python3
"""Reached ADD distinguishes live rejection from quiet selected-RHS repair."""
import base64
import json

import add_repair_review_cases as cases
import add_repair_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = r'''
dec $add_repair_review_diagnostic(pevent, text) : nat
def $add_repair_review_diagnostic(DIAGNOSTIC text n* z, text) = 1
def $add_repair_review_diagnostic(DIAGNOSTIC_SOURCE n_source text n* z, text) = 1
def $add_repair_review_diagnostic(DIAGNOSTIC_STACK text n* z n_trace*, text) = 1
def $add_repair_review_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n* z n_trace*, text) = 1
def $add_repair_review_diagnostic(pevent, text) = 0 -- otherwise
dec $add_repair_review_diagnostics(pevent*, text) : nat
def $add_repair_review_diagnostics(eps, text) = 0
def $add_repair_review_diagnostics(pevent :: pevent_tail*, text) = $($add_repair_review_diagnostic(pevent, text) + $add_repair_review_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    rebound = name == CASES[1]
    warning = lambda phase, raw, number, stage: f'ARITHMETIC_ADD_WARNING pintegeroperation ({phase}) {raw} ({number}) {stage}'
    left = lambda stage: warning('ARITHMETIC_LEFT', 'pvalue_left', 'NINT 12', stage)
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $add_repair_seek({before}, {stage}, 5000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$add_repair_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$arithmetic_add_repair_plan(S_entry) = (pintegeroperation)', '$arithmetic_add_plan(S_entry) = eps',
        '$arithmetic_add_valid(S_entry, pintegeroperation)', '$arithmetic_add_selected(S_entry, pintegeroperation)',
        'pintegeroperation.OP = ADD', '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_left',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_right', 'n_left =/= n_right',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)', '$lookup(S_entry.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)', '$lookup(S_entry.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)', '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'S_entry.STORE[n_left] = DEFINED pvalue_left', '$string_bytes(pvalue_left) = ($ptascii("12tail"))',
        '$arithmetic_add_conversion(pvalue_left) = ((NINT 12, true))',
        'S_entry.STORE[n_right] = DEFINED pvalue_initial_right',
        'pvalue_initial_right = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("bad5"))',
        'S_entry.STRINGDATA[n_string] = $ptascii("bad5")', '$string_carrier_valid(S_entry, pvalue_initial_right)',
        '$arithmetic_add_conversion(pvalue_initial_right) = eps',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', 'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 2',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'S_entry.TODO = ptask_old :: ptask_tail*', 'PhpStep: S_entry ~> S_begin',
        'S_begin = S_entry[.TODO = (ARITHMETIC_ADD_CONVERT pintegeroperation ARITHMETIC_LEFT) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$task_nodes(ARITHMETIC_ADD_CONVERT pintegeroperation ARITHMETIC_LEFT) = eps',
    ]
    if rebound:
        checks += [
            '$lookup(S_entry.ENV, $ptascii("replacement")) = (n_replacement)', 'n_replacement =/= n_right',
            'S_entry.STORE[n_replacement] = DEFINED pvalue_replacement',
            '$string_bytes(pvalue_replacement) = ($ptascii("2tail"))',
        ]
    step('S_capture', 'S_begin')
    checks += ['S_capture.TODO = (' + left(0) + ') :: ptask_tail*']
    step('S_first', 'S_capture')
    checks += [
        'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_left) :: ptask_tail*',
        'perrorcall_left.RESUME = ' + left(1), 'perrorcall_left.TARGET = eps',
        'perrorcall_left.LEVEL = 2', 'perrorcall_left.LINE = 25', '$error_call_valid(S_first, perrorcall_left)',
    ]
    seek('S_first_entered', 'S_first', 10)
    checks += ['$add_repair_entered(S_first_entered.FRAMES, 0)', '$call_descriptors_valid(S_first_entered)']
    seek('S_left', 'S_first_entered', 4)
    checks += [
        'S_left.TODO = (' + left(1) + ') :: ptask_tail*',
        'S_left.STORE[n_calls] = DEFINED (PINT 1)', 'S_left.STORE[n_v] = DEFINED (PINT 100)',
        '$arithmetic_add_warning_valid(S_left, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NINT 12, 1)',
    ]
    if rebound:
        checks += [
            'S_left.STORE[n_left] = DEFINED (PINT 99)',
            'S_left.STORE[n_right] = DEFINED pvalue_right', '$string_bytes(pvalue_right) = ($ptascii("5.5"))',
            '$arithmetic_add_conversion(pvalue_right) = ((NFLOAT 4617878467915022336, false))',
            '$lookup(S_left.ENV, $ptascii("right")) = (n_replacement)',
            '$lookup(S_left.ENV, $ptascii("rightAlias")) = (n_right)',
            '~$arithmetic_add_selected(S_left, pintegeroperation)',
            '$heap_owners($heap_prune($heap_graph(S_left)), HCELL n_right) = 1',
            '$heap_owners($heap_prune($heap_graph(S_left)), HCELL n_replacement) = 2',
        ]
    else:
        checks += ['S_left.STORE[n_left] = DEFINED (PBOOL false)',
                   'S_left.STORE[n_right] = DEFINED pvalue_initial_right']
    step('S_right', 'S_left')
    checks += ['S_right.TODO = (ARITHMETIC_ADD_CONVERT pintegeroperation (ARITHMETIC_RIGHT (NINT 12))) :: ptask_tail*']
    if rebound:
        checks += [
            '$integer_pointer_select(S_right, pintegeroperation.RIGHT) = (INTEGER_CELL n_replacement)',
            '$integer_pointer_value(S_right, pintegeroperation.RIGHTPOINTER) = (pvalue_right)',
        ]
        checks += [
            'S_before = S_right',
            '$arithmetic_add_failure_operands(S_before, pintegeroperation, ARITHMETIC_RIGHT (NINT 12)) = eps',
            '$integer_pointer_value(S_before, pintegeroperation.RIGHTPOINTER) = (pvalue_right)',
            '$arithmetic_add_conversion(pvalue_replacement) = ((NINT 2, true))',
        ]
    else:
        checks += [
            'S_before = S_right',
            '$arithmetic_add_failure_operands(S_before, pintegeroperation, ARITHMETIC_RIGHT (NINT 12)) = ((PBOOL false, pvalue_initial_right))',
            '$arithmetic_add_conversion(PBOOL false) = ((NINT 0, false))',
        ]
    checks += [
        'S_before.STORE[n_v] = DEFINED (PINT 100)',
        '$add_repair_review_diagnostics(S_before.EVENTS, "Warning") = 1',
        'S_before.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        'S_before.STRINGDATA[n_string] = $ptascii("bad5")',
        'PhpStep: S_before ~> S_atomic',
    ]
    if rebound:
        checks += [
            'S_atomic = S_before[.TODO = ptask_tail*][.RESULT = KNOWN (PFLOAT 4625619029774565376)]',
        ]
        step('S_result', 'S_before')
        checks += [
            'S_result = S_atomic',
            'S_result.STORE[n_v] = DEFINED (PINT 100)',
            'S_result.STORE[n_calls] = DEFINED (PINT 1)',
            'S_result.STORE[n_left] = DEFINED (PINT 99)',
            'S_result.STORE[n_right] = DEFINED pvalue_right',
            'S_result.STORE[n_replacement] = DEFINED pvalue_replacement',
            '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_right) = 1',
            '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_replacement) = 2',
            '~$arithmetic_tasks(S_result.TODO)', '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
            'S_done = $drive_steps(S_result, 5000)',
        ]
    else:
        message = '$ptascii("Unsupported operand types: bool + string")'
        checks += [
            'S_atomic = S_before[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.COMPLETION = THROWN "TypeError" (' + message + ') 25]',
        ]
        step('S_error', 'S_before')
        checks += [
            'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
            'S_error.CURRENT = eps', 'S_error.RESULT = KNOWN PNULL',
            'n_error = |S_before.OBJECTS|', 'S_error.OBJECTS[n_error] = THROWABLE pthrowable',
            'S_error.OBJECTS = S_before.OBJECTS ++ [THROWABLE pthrowable]',
            'pthrowable.KIND = "TypeError"', 'pthrowable.ORIGIN = (pintegeroperation.SITE)',
            '$throwable_field(S_error, n_error, "line") = PINT 25',
            '$string_bytes($throwable_field(S_error, n_error, "message")) = (' + message + ')',
            '$throwable_previous_id(S_error, n_error) = eps', '$throwable_live(S_error, n_error)',
            '$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]',
            '$heap_owners($heap_prune($heap_graph(S_error)), HOBJECT n_error) = 1',
            'S_error.STORE = S_before.STORE', 'S_error.ENV = S_before.ENV', 'S_error.REFCELLS = S_before.REFCELLS',
            'S_error.EVENTS = S_before.EVENTS', 'S_error.STRINGDATA = S_before.STRINGDATA',
            'S_error.ARRAYS[0:|S_before.ARRAYS|] = S_before.ARRAYS',
            '~$arithmetic_tasks(S_error.TODO)', '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
            'S_done = $drive_steps(S_error, 5000)',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        '$lookup(S_done.ENV, $ptascii("leftAlias")) = (n_left)', 'S_done.STORE[n_left] = DEFINED (PINT 7)',
        '$lookup(S_done.ENV, $ptascii("rightAlias")) = (n_right)',
    ]
    if rebound:
        checks += [
            'S_done.STORE[n_v] = DEFINED (PFLOAT 4625619029774565376)',
            'S_done.STORE[n_right] = DEFINED (PINT 6)', 'S_done.STORE[n_replacement] = DEFINED (PINT 8)',
            '$lookup(S_done.ENV, $ptascii("right")) = (n_replacement)',
            '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_right) = 1',
            '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement) = 2',
        ]
    else:
        checks += ['S_done.STORE[n_v] = DEFINED (PINT 100)', 'S_done.STORE[n_right] = DEFINED (PINT 8)',
                   '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_right) = 2']
    checks += [
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_left) = 2',
        '$add_repair_review_diagnostics(S_done.EVENTS, "Warning") = 1',
        '$add_repair_review_diagnostics(S_done.EVENTS, "Deprecated") = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_entry, 7000) = S_done', '$drive_steps(S_first, 0) = S_first[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
