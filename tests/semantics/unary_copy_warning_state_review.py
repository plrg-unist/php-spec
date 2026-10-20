#!/usr/bin/env python3
"""A selected ternary copy keeps its unary sign after source retirement."""
import base64
import json

import unary_copy_warning_review_cases as cases
import unary_copy_warning_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = ''


def conditions(name, program, path, stdout):
    assert name in CASES
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $unary_copy_seek({before}, {stage}, 3000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$unary_copy_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$arithmetic_unary_copy_plan(S_entry) = (punarywarning)',
        '$arithmetic_unary_plan(S_entry) = eps',
        '$arithmetic_unary_reference_plan(S_entry) = eps',
        'punarywarning.OP = NEGATIVE', 'punarywarning.LINE = 25',
        'punarywarning.INPUT = KNOWN punarywarning.VALUE',
        'S_entry.RESULT = punarywarning.INPUT',
        '$string_bytes(punarywarning.VALUE) = ($ptascii("0.0tail"))',
        '$string_carrier_valid(S_entry, punarywarning.VALUE)',
        'punarywarning.NUMBER = NFLOAT 0',
        '$integer_operand_source(S_entry, punarywarning.SITE, [PCFIELD 0], punarywarning.INPUT)',
        '$integer_pointer_select(S_entry, punarywarning.INPUT) = (INTEGER_COPY punarywarning.VALUE)',
        '$arithmetic_unary_valid(S_entry, punarywarning)',
        '$arithmetic_unary_snapshot(S_entry, punarywarning)',
        '$lookup(S_entry.ENV, $ptascii("source")) = (n_source)',
        '$lookup(S_entry.ENV, $ptascii("pick")) = (n_pick)',
        '$lookup(S_entry.ENV, $ptascii("other")) = (n_other)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        'S_entry.STORE[n_source] = DEFINED punarywarning.VALUE',
        'S_entry.STORE[n_pick] = DEFINED (PBOOL true)',
        'S_entry.STORE[n_other] = DEFINED (PINT 7)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '~(n_source <- S_entry.REFCELLS)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_source) = 1',
        'S_entry.EVENTS = eps',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'S_entry.TODO = ptask_old :: ptask_tail*',
        'PhpStep: S_entry ~> S_capture_atomic',
        'S_capture_atomic = S_entry[.TODO = (ARITHMETIC_UNARY_WARNING punarywarning 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture = S_capture_atomic', '$unary_copy_frontier(S_capture, 1)',
        '$arithmetic_unary_warning_valid(S_capture, punarywarning, 0)',
        '$arithmetic_unary_warning_valid(S_capture, punarywarning, 1)',
        '$task_nodes(ARITHMETIC_UNARY_WARNING punarywarning 0) = eps',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_source) = 1',
        '$call_descriptors_valid(S_capture)',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        '$unary_copy_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ARITHMETIC_UNARY_WARNING punarywarning 1',
        'perrorcall.TARGET = eps', 'perrorcall.SITE = punarywarning.SITE',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = $ptascii("A non-numeric value encountered")',
        '$error_call_valid(S_dispatch, perrorcall)',
        'S_dispatch.EVENTS = S_entry.EVENTS', '$call_descriptors_valid(S_dispatch)',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += [
        '$unary_entered(S_entered.FRAMES)', 'S_entered.CURRENT =/= eps',
        '$call_descriptors_valid(S_entered)',
    ]
    seek('S_return', 'S_entered', 4)
    checks += [
        'S_return.TODO = (ARITHMETIC_UNARY_WARNING punarywarning 1) :: ptask_tail*',
        '$lookup(S_return.ENV, $ptascii("source")) = eps',
        '$lookup(S_return.ENV, $ptascii("pick")) = (n_pick)',
        '$lookup(S_return.ENV, $ptascii("other")) = (n_other)',
        'S_return.STORE[n_source] = DEFINED (PINT 99)',
        'S_return.STORE[n_pick] = DEFINED (PBOOL false)',
        'S_return.STORE[n_other] = DEFINED (PINT 7)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)',
        'S_return.STORE[n_calls] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_source) = 0',
        '~((HCELL n_source) <- S_return.ALLOCATIONS)',
        '$integer_pointer_value(S_return, INTEGER_CV ($ptascii("source"))) = eps',
        '$integer_pointer_value(S_return, INTEGER_COPY punarywarning.VALUE) = (punarywarning.VALUE)',
        '$arithmetic_unary_valid(S_return, punarywarning)',
        '$arithmetic_unary_snapshot(S_return, punarywarning)',
        '$arithmetic_unary_warning_valid(S_return, punarywarning, 0)',
        '$arithmetic_unary_warning_valid(S_return, punarywarning, 1)',
        '$task_nodes(ARITHMETIC_UNARY_WARNING punarywarning 1) = eps',
        '(DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) 25) <- S_return.EVENTS',
        'S_return.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'PhpStep: S_return ~> S_atomic',
        'S_atomic = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (PFLOAT 9223372036854775808)]',
    ]
    step('S_result', 'S_return')
    checks += [
        'S_result = S_atomic', '$unary_copy_frontier(S_result, 5)',
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
        '$lookup(S_done.ENV, $ptascii("source")) = eps',
        '$lookup(S_done.ENV, $ptascii("other")) = (n_other)',
        'S_done.STORE[n_source] = DEFINED (PINT 99)',
        'S_done.STORE[n_other] = DEFINED (PINT 8)',
        'S_done.STORE[n_pick] = DEFINED (PBOOL false)',
        'S_done.STORE[n_v] = DEFINED (PFLOAT 9223372036854775808)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_source) = 0',
        '~((HCELL n_source) <- S_done.ALLOCATIONS)',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
        '$drive_steps(S_result, 0) = S_result[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
