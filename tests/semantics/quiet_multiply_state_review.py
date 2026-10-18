#!/usr/bin/env python3
"""Reached TMP/VAR multiplication keeps copied raw types after origin repair."""
import base64
import json

import quiet_multiply_review_cases as cases
import quiet_multiply_protocol as shared

CASES = ('quiet-multiply-tmp-var-copy',)
REVIEW_HELPERS = r'''
dec $quiet_multiply_review_diagnostic(pevent) : nat
def $quiet_multiply_review_diagnostic(DIAGNOSTIC text n* z) = 1
def $quiet_multiply_review_diagnostic(DIAGNOSTIC_SOURCE n_source text n* z) = 1
def $quiet_multiply_review_diagnostic(DIAGNOSTIC_STACK text n* z n_trace*) = 1
def $quiet_multiply_review_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n* z n_trace*) = 1
def $quiet_multiply_review_diagnostic(pevent) = 0 -- otherwise
dec $quiet_multiply_review_diagnostics(pevent*) : nat
def $quiet_multiply_review_diagnostics(eps) = 0
def $quiet_multiply_review_diagnostics(pevent :: pevent_tail*) = $($quiet_multiply_review_diagnostic(pevent) + $quiet_multiply_review_diagnostics(pevent_tail*))
'''


def conditions(name, program, path, stdout):
    message = '$ptascii("Unsupported operand types: float * string")'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $quiet_multiply_seek(S_initial, 5000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]', '$quiet_multiply_frontier(S_entry)',
        'S_entry.TODO = (BINARY_RIGHT MULTIPLY poperand_left 25) :: ptask_tail*',
        'S_entry.RESULT = poperand_right', 'S_entry.ORIGIN = (porigin)',
        'poperand_left = KNOWN pvalue_left', 'poperand_right = KNOWN pvalue_right',
        '$integer_operand_source(S_entry, porigin, [PCFIELD 0], poperand_left)',
        '$integer_operand_source(S_entry, porigin, [PCFIELD 1], poperand_right)',
        '$integer_slot_rank(S_entry, porigin, [PCFIELD 0], poperand_left) = (2)',
        '$integer_slot_rank(S_entry, porigin, [PCFIELD 1], poperand_right) = (4)',
        '$operand_nodes(poperand_left) = eps', '$operand_nodes(poperand_right) = eps',
        '$integer_pointer_select(S_entry, poperand_left) = (INTEGER_COPY pvalue_left)',
        '$integer_pointer_select(S_entry, poperand_right) = (INTEGER_COPY pvalue_right)',
        '$string_bytes(pvalue_left) = ($ptascii("bad5"))', '$string_carrier_valid(S_entry, pvalue_left)',
        'pvalue_right = PFLOAT 4612811918334230528',
        '$coerce_number(pvalue_left) = BADNUMBER',
        '$coerce_number(pvalue_right) = COERCED (NFLOAT 4612811918334230528) false',
        '$quiet_multiply_scalar(S_entry, pvalue_left)', '$quiet_multiply_scalar(S_entry, pvalue_right)',
        '$quiet_multiply_error(S_entry, poperand_left, poperand_right, pvalue_left, pvalue_right, 25)',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("sourceCalls")) = (n_source_calls)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'S_entry.STORE[n_left] = DEFINED (PINT 12)', 'S_entry.STORE[n_right] = DEFINED pvalue_right',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', 'S_entry.STORE[n_source_calls] = DEFINED (PINT 1)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '$integer_pointer_value(S_entry, INTEGER_CV ($ptascii("left"))) = (PINT 12)',
        '$integer_pointer_value(S_entry, INTEGER_COPY pvalue_left) = (pvalue_left)',
        '$coerce_number(PINT 12) = COERCED (NINT 12) false',
        '$integer_operator_plan(S_entry) = eps', '$arithmetic_add_plan(S_entry) = eps',
        '$arithmetic_div_plan(S_entry) = eps', '$submul_warning_plan(S_entry) = eps',
        '$power_conversion_warning_plan(S_entry) = eps', '$arithmetic_cv_plan(S_entry) = eps',
        '$arithmetic_mixed_plan(S_entry) = eps', '$arithmetic_copy_plan(S_entry) = eps',
        '$arithmetic_owned_plan(S_entry) = eps', '$power_warning_plan(S_entry) = eps',
        'S_entry.FRAMES = eps', 'S_entry.CURRENT = eps', 'S_entry.HELD = eps',
        '$quiet_multiply_review_diagnostics(S_entry.EVENTS) = 0',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'PhpStep: S_entry ~> S_raw',
        'S_raw = S_entry[.TODO = ptask_tail*][.RESULT = KNOWN pvalue_right][.BASE = BASE_VALUE (KNOWN PNULL)][.COMPLETION = THROWN "TypeError" (' + message + ') 25]',
        'S_error_budget = $drive_steps(S_entry, 1)', 'S_error_budget.COMPLETION = BUDGET',
        'S_error = S_error_budget[.COMPLETION = NORMAL]',
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        'S_error.RESULT = KNOWN PNULL', 'S_error.CURRENT = eps',
        'n_error = |S_entry.OBJECTS|', 'S_error.OBJECTS[n_error] = THROWABLE pthrowable',
        'S_error.OBJECTS = S_entry.OBJECTS ++ [THROWABLE pthrowable]',
        'pthrowable.KIND = "TypeError"', 'pthrowable.ORIGIN = (porigin)',
        '$throwable_field(S_error, n_error, "line") = PINT 25',
        '$string_bytes($throwable_field(S_error, n_error, "message")) = (' + message + ')',
        '$throwable_previous_id(S_error, n_error) = eps', '$throwable_live(S_error, n_error)',
        '$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]',
        '$heap_owners($heap_prune($heap_graph(S_error)), HOBJECT n_error) = 1',
        'S_error.STORE = S_entry.STORE', 'S_error.ENV = S_entry.ENV',
        'S_error.REFCELLS = S_entry.REFCELLS', 'S_error.EVENTS = S_entry.EVENTS',
        'S_error.STRINGDATA = S_entry.STRINGDATA',
        'S_error.ARRAYS[0:|S_entry.ARRAYS|] = S_entry.ARRAYS',
        '$quiet_multiply_review_diagnostics(S_error.EVENTS) = 0',
        '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
        'S_done = $drive_steps(S_error, 5000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_done_left)',
        '$lookup(S_done.ENV, $ptascii("right")) = (n_done_right)',
        '$lookup(S_done.ENV, $ptascii("v")) = (n_done_v)',
        'S_done.STORE[n_done_left] = DEFINED (PINT 7)', 'S_done.STORE[n_done_right] = DEFINED (PINT 8)',
        'S_done.STORE[n_done_v] = DEFINED (PINT 100)',
        'S_done.STORE[n_calls] = DEFINED (PINT 0)', 'S_done.STORE[n_source_calls] = DEFINED (PINT 1)',
        '$quiet_multiply_review_diagnostics(S_done.EVENTS) = 0',
        '$quiet_multiply_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_entry, 0) = S_entry[.COMPLETION = BUDGET]', '$drive_steps(S_entry, 7000) = S_done',
    ]
    assert len(checks) == len(set(checks))
    return checks
