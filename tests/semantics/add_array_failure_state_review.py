#!/usr/bin/env python3
"""ADD rejects the selected old RHS array despite its rebound variable name."""
import base64
import json

import add_array_failure_review_cases as cases
import add_array_failure_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = r'''
dec $add_array_failure_review_diagnostic(pevent, text) : nat
def $add_array_failure_review_diagnostic(DIAGNOSTIC text n* z, text) = 1
def $add_array_failure_review_diagnostic(DIAGNOSTIC_SOURCE n_source text n* z, text) = 1
def $add_array_failure_review_diagnostic(DIAGNOSTIC_STACK text n* z n_trace*, text) = 1
def $add_array_failure_review_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n* z n_trace*, text) = 1
def $add_array_failure_review_diagnostic(pevent, text) = 0 -- otherwise
dec $add_array_failure_review_diagnostics(pevent*, text) : nat
def $add_array_failure_review_diagnostics(eps, text) = 0
def $add_array_failure_review_diagnostics(pevent :: pevent_tail*, text) = $($add_array_failure_review_diagnostic(pevent, text) + $add_array_failure_review_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $arithmetic_seek({before}, {stage}, 3000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$arithmetic_frontier({state}, {stage})',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$arithmetic_add_plan(S_entry) = (pintegeroperation)', '$arithmetic_add_valid(S_entry, pintegeroperation)',
        '$arithmetic_add_selected(S_entry, pintegeroperation)',
        'pintegeroperation.OP = ADD', '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_left', 'pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_right',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)', '$lookup(S_entry.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)', '$lookup(S_entry.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("replacement")) = (n_replacement)', 'n_replacement =/= n_right',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)', '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'n_left =/= n_right', 'n_left <- S_entry.REFCELLS', 'n_right <- S_entry.REFCELLS',
        'S_entry.STORE[n_left] = DEFINED pvalue_left', '$string_bytes(pvalue_left) = ($ptascii("12.5tail"))',
        '$arithmetic_add_conversion(pvalue_left) = ((NFLOAT 4623226492472524800, true))',
        'S_entry.STORE[n_right] = DEFINED (PINT 2)', 'S_entry.STORE[n_replacement] = DEFINED (PINT 7)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', 'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 2',
        '$heap_valid($heap_graph(S_entry))', '$call_descriptors_valid(S_entry)',
        'S_entry.TODO = ptask_old :: ptask_tail*', 'PhpStep: S_entry ~> S_begin',
        'S_begin = S_entry[.TODO = (ARITHMETIC_ADD_CONVERT pintegeroperation ARITHMETIC_LEFT) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_capture_budget = $drive_steps(S_begin, 1)', 'S_capture_budget.COMPLETION = BUDGET',
        'S_capture = S_capture_budget[.COMPLETION = NORMAL]',
        'S_capture.TODO = (ARITHMETIC_ADD_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_left (NFLOAT 4623226492472524800) 0) :: ptask_tail*',
    ]
    seek('S_first', 'S_capture', 3)
    checks += [
        'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.TARGET = eps', 'perrorcall.LEVEL = 2', 'perrorcall.LINE = 25',
        'perrorcall.RESUME = ARITHMETIC_ADD_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_left (NFLOAT 4623226492472524800) 1',
        '$error_call_valid(S_first, perrorcall)', '$call_descriptors_valid(S_first)',
    ]
    seek('S_left', 'S_first', 4)
    checks += [
        'S_left.TODO = (ARITHMETIC_ADD_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_left (NFLOAT 4623226492472524800) 1) :: ptask_tail*',
        '$arithmetic_add_warning_valid(S_left, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NFLOAT 4623226492472524800, 1)',
        '~$arithmetic_add_warning_valid(S_left, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NFLOAT 4623226492472524800, 0)',
        '$lookup(S_left.ENV, $ptascii("right")) = (n_replacement)',
        '$lookup(S_left.ENV, $ptascii("rightAlias")) = (n_right)',
        'S_left.STORE[n_left] = DEFINED (PBOOL false)', 'S_left.STORE[n_right] = DEFINED (PARRAY n_array)',
        'S_left.STORE[n_replacement] = DEFINED (PINT 7)',
        'S_left.STORE[n_calls] = DEFINED (PINT 1)', 'S_left.STORE[n_v] = DEFINED (PINT 100)',
        'S_left.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2))]',
        '$integer_pointer_select(S_left, pintegeroperation.RIGHT) = (INTEGER_CELL n_replacement)',
        '$integer_pointer_value(S_left, pintegeroperation.RIGHTPOINTER) = (PARRAY n_array)',
        '$integer_pointer_value(S_left, INTEGER_CELL n_replacement) = (PINT 7)',
        '~$arithmetic_add_selected(S_left, pintegeroperation)', '$arithmetic_add_valid(S_left, pintegeroperation)',
        '$heap_owners($heap_prune($heap_graph(S_left)), HCELL n_right) = 1',
        '$heap_owners($heap_prune($heap_graph(S_left)), HCELL n_replacement) = 2',
        'S_before_budget = $drive_steps(S_left, 1)', 'S_before_budget.COMPLETION = BUDGET',
        'S_before = S_before_budget[.COMPLETION = NORMAL]', 'PhpStep: S_left ~> S_before',
        'S_before = S_left[.TODO = (ARITHMETIC_ADD_CONVERT pintegeroperation (ARITHMETIC_RIGHT (NFLOAT 4623226492472524800))) :: ptask_tail*][.RESULT = KNOWN PNULL]',
        '$arithmetic_add_failure_operands(S_before, pintegeroperation, ARITHMETIC_RIGHT (NFLOAT 4623226492472524800)) = eps',
        '$arithmetic_add_array_failure_operands(S_before, pintegeroperation, ARITHMETIC_RIGHT (NFLOAT 4623226492472524800)) = ((PBOOL false, PARRAY n_array))',
        '$arithmetic_add_conversion(PARRAY n_array) = eps',
        '$heap_count(HARRAY n_array, $pools_nodes(S_before.POOLS)) = 1',
        '$heap_owners($heap_prune($heap_graph(S_before)), HARRAY n_array) = 2',
        '$add_array_failure_review_diagnostics(S_before.EVENTS, "Warning") = 1',
        'S_before.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        'PhpStep: S_before ~> S_atomic',
        'S_atomic = S_before[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.COMPLETION = THROWN "TypeError" ($ptascii("Unsupported operand types: bool + array")) 25]',
        'S_error_budget = $drive_steps(S_before, 1)', 'S_error_budget.COMPLETION = BUDGET',
        'S_error = S_error_budget[.COMPLETION = NORMAL]',
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*', 'S_error.CURRENT = eps', 'S_error.FRAMES = eps',
        'S_error.RESULT = KNOWN PNULL', 'n_error = |S_before.OBJECTS|',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable',
        'S_error.OBJECTS = S_before.OBJECTS ++ [THROWABLE pthrowable]',
        'pthrowable.KIND = "TypeError"', 'pthrowable.ORIGIN = (pintegeroperation.SITE)',
        '$throwable_field(S_error, n_error, "line") = PINT 25',
        '$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("Unsupported operand types: bool + array"))',
        '$throwable_previous_id(S_error, n_error) = eps', '$throwable_live(S_error, n_error)',
        '$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]',
        '$heap_owners($heap_prune($heap_graph(S_error)), HOBJECT n_error) = 1',
        'S_error.STORE = S_before.STORE', 'S_error.ENV = S_before.ENV', 'S_error.REFCELLS = S_before.REFCELLS',
        'S_error.EVENTS = S_before.EVENTS', 'S_error.STRINGDATA = S_before.STRINGDATA',
        'S_error.ARRAYS[0:|S_before.ARRAYS|] = S_before.ARRAYS',
        '$heap_owners($heap_prune($heap_graph(S_error)), HARRAY n_array) = 2',
        '~$arithmetic_tasks(S_error.TODO)', '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
        'S_done = $drive_steps(S_error, 5000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_left)', '$lookup(S_done.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_done.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_done.ENV, $ptascii("right")) = (n_replacement)',
        '$lookup(S_done.ENV, $ptascii("replacement")) = (n_replacement)',
        'S_done.STORE[n_left] = DEFINED (PINT 7)', 'S_done.STORE[n_right] = DEFINED (PINT 3)',
        'S_done.STORE[n_replacement] = DEFINED (PINT 8)',
        'S_done.STORE[n_v] = DEFINED (PINT 100)', 'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        'S_done.ARRAYS[n_array].ITEMS = S_before.ARRAYS[n_array].ITEMS',
        '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_array) = 1',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_right) = 1',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement) = 2',
        '$add_array_failure_review_diagnostics(S_done.EVENTS, "Warning") = 1',
        '$add_array_failure_review_diagnostics(S_done.EVENTS, "Deprecated") = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_entry, 7000) = S_done',
        '$drive_steps(S_before, 0) = S_before[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
