#!/usr/bin/env python3
"""A cached unary sign survives retirement of its selected source reference."""
import base64
import json

import unary_reference_warning_review_cases as cases
import unary_reference_warning_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = r'''
dec $unary_reference_review_diagnostic(pevent) : nat
def $unary_reference_review_diagnostic(DIAGNOSTIC "Warning" n* z) = 1
def $unary_reference_review_diagnostic(DIAGNOSTIC_SOURCE n_source "Warning" n* z) = 1
def $unary_reference_review_diagnostic(DIAGNOSTIC_STACK "Warning" n* z n_trace*) = 1
def $unary_reference_review_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source "Warning" n* z n_trace*) = 1
def $unary_reference_review_diagnostic(pevent) = 0 -- otherwise
dec $unary_reference_review_warnings(pevent*) : nat
def $unary_reference_review_warnings(eps) = 0
def $unary_reference_review_warnings(pevent :: pevent_tail*) = $($unary_reference_review_diagnostic(pevent) + $unary_reference_review_warnings(pevent_tail*))
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $unary_reference_seek({before}, {stage}, 3000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$unary_reference_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$arithmetic_unary_reference_plan(S_entry) = (punarywarning)',
        '$arithmetic_unary_plan(S_entry) = eps',
        'punarywarning.OP = NEGATIVE', 'punarywarning.LINE = 25',
        'punarywarning.INPUT = VARIABLE ($ptascii("x")) 25',
        '$string_bytes(punarywarning.VALUE) = ($ptascii("0.0tail"))',
        '$string_carrier_valid(S_entry, punarywarning.VALUE)',
        'punarywarning.NUMBER = NFLOAT 0',
        '$arithmetic_unary_valid(S_entry, punarywarning)',
        '$arithmetic_unary_snapshot(S_entry, punarywarning)',
        '$integer_pointer_select(S_entry, punarywarning.INPUT) = (INTEGER_CELL n_x)',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)',
        '$lookup(S_entry.ENV, $ptascii("alias")) = (n_x)',
        '$lookup(S_entry.ENV, $ptascii("replacement")) = (n_replacement)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        'n_x =/= n_replacement',
        'S_entry.STORE[n_x] = DEFINED punarywarning.VALUE',
        'S_entry.STORE[n_replacement] = DEFINED (PINT 77)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_replacement) = 1',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'S_entry.TODO = ptask_old :: ptask_tail*',
        'PhpStep: S_entry ~> S_capture_atomic',
        'S_capture_atomic = S_entry[.TODO = (ARITHMETIC_UNARY_WARNING punarywarning 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture.TODO = (ARITHMETIC_UNARY_WARNING punarywarning 0) :: ptask_tail*',
        '$arithmetic_unary_warning_valid(S_capture, punarywarning, 0)',
        '$task_nodes(ARITHMETIC_UNARY_WARNING punarywarning 0) = eps',
        'S_capture.STORE = S_entry.STORE', 'S_capture.ENV = S_entry.ENV',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_x) = 2',
        '$call_descriptors_valid(S_capture)',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ARITHMETIC_UNARY_WARNING punarywarning 1',
        'perrorcall.TARGET = eps', 'perrorcall.SITE = punarywarning.SITE',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = $ptascii("A non-numeric value encountered")',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$unary_reference_review_warnings(S_dispatch.EVENTS) = 0',
        '$call_descriptors_valid(S_dispatch)',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += [
        '$unary_entered(S_entered.FRAMES)', 'S_entered.CURRENT =/= eps',
        '$call_descriptors_valid(S_entered)',
    ]
    seek('S_return', 'S_entered', 4)
    checks += [
        'S_return.TODO = (ARITHMETIC_UNARY_WARNING punarywarning 1) :: ptask_tail*',
        '$lookup(S_return.ENV, $ptascii("x")) = (n_replacement)',
        '$lookup(S_return.ENV, $ptascii("replacement")) = (n_replacement)',
        '$lookup(S_return.ENV, $ptascii("alias")) = eps',
        'S_return.STORE[n_x] = DEFINED (PINT 99)',
        'S_return.STORE[n_replacement] = DEFINED (PINT 77)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)',
        'S_return.STORE[n_calls] = DEFINED (PINT 1)',
        '$integer_pointer_select(S_return, punarywarning.INPUT) = (INTEGER_CELL n_replacement)',
        '$integer_pointer_value(S_return, INTEGER_CELL n_x) = eps',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_x) = 0',
        '~((HCELL n_x) <- S_return.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_replacement) = 2',
        '$arithmetic_unary_valid(S_return, punarywarning)',
        '~$arithmetic_unary_snapshot(S_return, punarywarning)',
        '~$arithmetic_unary_warning_valid(S_return, punarywarning, 0)',
        '$arithmetic_unary_warning_valid(S_return, punarywarning, 1)',
        '$task_nodes(ARITHMETIC_UNARY_WARNING punarywarning 1) = eps',
        '$unary_reference_review_warnings(S_return.EVENTS) = 1',
        'S_return.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'PhpStep: S_return ~> S_atomic',
        'S_atomic = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (PFLOAT 9223372036854775808)]',
    ]
    step('S_result', 'S_return')
    checks += [
        '$unary_reference_frontier(S_result, 5)',
        'S_result.RESULT = KNOWN (PFLOAT 9223372036854775808)',
        'S_result.TODO = ptask_tail*', 'S_result.STORE = S_return.STORE',
        'S_result.ENV = S_return.ENV', 'S_result.REFCELLS = S_return.REFCELLS',
        'S_result.ALLOCATIONS = S_return.ALLOCATIONS',
        'S_result.EVENTS = S_return.EVENTS', 'S_result.STRINGDATA = S_return.STRINGDATA',
        'S_result.ARRAYS = S_return.ARRAYS', 'S_result.OBJECTS = S_return.OBJECTS',
        '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 3000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("x")) = (n_replacement)',
        '$lookup(S_done.ENV, $ptascii("replacement")) = (n_replacement)',
        '$lookup(S_done.ENV, $ptascii("alias")) = eps',
        'S_done.STORE[n_replacement] = DEFINED (PINT 8)',
        'S_done.STORE[n_v] = DEFINED (PFLOAT 9223372036854775808)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_x) = 0',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement) = 2',
        '~((HCELL n_x) <- S_done.ALLOCATIONS)',
        '$unary_reference_review_warnings(S_done.EVENTS) = 1',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
        '$drive_steps(S_result, 0) = S_result[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
