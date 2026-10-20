#!/usr/bin/env python3
"""Both NaN notices finish before complementing after the original CV retires."""
import base64
import json

import bitnot_nan_warning_review_cases as cases
import bitnot_nan_warning_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = ''


def conditions(name, program, path, stdout):
    assert name in CASES
    marker = lambda stage: f'BITNOT_NAN_WARNING pbitnotwarning {stage} eps'
    valid = lambda state, stage: f'$bitnot_nan_warning_valid({state}, pbitnotwarning, {stage}, eps)'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $bitnot_nan_seek({before}, {stage}, 4000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$bitnot_nan_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$bitnot_nan_warning_plan(S_entry) = (pbitnotwarning)',
        '$bitnot_warning_plan(S_entry) = eps',
        '$bitnot_nan_source_valid(S_entry, pbitnotwarning)',
        'pbitnotwarning.INPUT = VARIABLE ($ptascii("x")) 25',
        'pbitnotwarning.LINE = 25', 'pbitnotwarning.VALUE = 0',
        '$float_decode(pbitnotwarning.BITS) = NOTNUMBER n_nan',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'S_entry.STORE[n_x] = DEFINED (PFLOAT pbitnotwarning.BITS)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', 'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '$integer_pointer_select(S_entry, pbitnotwarning.INPUT) = (INTEGER_CV ($ptascii("x")))',
        '$bitnot_snapshot(S_entry, pbitnotwarning)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture.TODO = (' + marker(0) + ') :: ptask_tail*',
        'S_capture.RESULT = KNOWN PNULL', 'S_capture.BASE = BASE_VALUE (KNOWN PNULL)',
        valid('S_capture', 0), '$task_nodes(' + marker(0) + ') = eps',
        '$call_descriptors_valid(S_capture)',
    ]
    step('S_first', 'S_capture')
    checks += [
        'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
        'perrorcall_first.RESUME = ' + marker(1), 'perrorcall_first.TARGET = eps',
        'perrorcall_first.LEVEL = 2', 'perrorcall_first.LINE = 25',
        'perrorcall_first.MESSAGE = $ptascii("The float NAN is not representable as an int, cast occurred")',
        '$error_call_valid(S_first, perrorcall_first)', '$call_descriptors_valid(S_first)',
    ]
    seek('S_first_entered', 'S_first', 3)
    checks += ['$bitnot_nan_entered(S_first_entered.FRAMES, 0)', '$call_descriptors_valid(S_first_entered)']
    seek('S_left', 'S_first_entered', 4)
    checks += [
        'S_left.TODO = (' + marker(1) + ') :: ptask_tail*',
        'S_left.STORE[n_x] = DEFINED (PINT 99)',
        'S_left.STORE[n_calls] = DEFINED (PINT 1)', 'S_left.STORE[n_v] = DEFINED (PINT 100)',
        valid('S_left', 1), '~' + valid('S_left', 0), '~$bitnot_snapshot(S_left, pbitnotwarning)',
        '$bitnot_nan_diagnostics(S_left.EVENTS, "Warning") = 0',
        '$bitnot_nan_diagnostics(S_left.EVENTS, "Deprecated") = 0',
        '$call_descriptors_valid(S_left)',
    ]
    step('S_second', 'S_left')
    checks += [
        'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
        'perrorcall_second.RESUME = ' + marker(2), 'perrorcall_second.TARGET = eps',
        'perrorcall_second.LEVEL = 8192', 'perrorcall_second.LINE = 25',
        'perrorcall_second.MESSAGE = $ptascii("Implicit conversion from float NAN to int loses precision")',
        '$error_call_valid(S_second, perrorcall_second)', '$call_descriptors_valid(S_second)',
    ]
    seek('S_second_entered', 'S_second', 6)
    checks += ['$bitnot_nan_entered(S_second_entered.FRAMES, 1)', '$call_descriptors_valid(S_second_entered)']
    seek('S_return', 'S_second_entered', 7)
    checks += [
        'S_return.TODO = (' + marker(2) + ') :: ptask_tail*',
        'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
        '$lookup(S_return.ENV, $ptascii("x")) = eps',
        'S_return.STORE[n_x] = DEFINED (PINT 99)',
        'S_return.STORE[n_calls] = DEFINED (PINT 2)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_x) = 0',
        '~((HCELL n_x) <- S_return.ALLOCATIONS)',
        '$integer_pointer_value(S_return, INTEGER_CV ($ptascii("x"))) = eps',
        valid('S_return', 2), '$task_nodes(' + marker(2) + ') = eps',
        '$bitnot_nan_diagnostics(S_return.EVENTS, "Warning") = 0',
        '$bitnot_nan_diagnostics(S_return.EVENTS, "Deprecated") = 1',
        'S_return.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'PhpStep: S_return ~> S_atomic',
        'S_atomic = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (PINT $(-1))]',
    ]
    step('S_result', 'S_return')
    checks += [
        '$bitnot_nan_frontier(S_result, 8)',
        'S_result.TODO = ptask_tail*', 'S_result.RESULT = KNOWN (PINT $(-1))',
        'S_result.STORE = S_return.STORE', 'S_result.ENV = S_return.ENV',
        'S_result.REFCELLS = S_return.REFCELLS', 'S_result.ALLOCATIONS = S_return.ALLOCATIONS',
        'S_result.EVENTS = S_return.EVENTS', 'S_result.STRINGDATA = S_return.STRINGDATA',
        'S_result.ARRAYS = S_return.ARRAYS', 'S_result.OBJECTS = S_return.OBJECTS',
        '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 4000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("x")) = eps',
        'S_done.STORE[n_x] = DEFINED (PINT 99)',
        'S_done.STORE[n_calls] = DEFINED (PINT 2)', 'S_done.STORE[n_v] = DEFINED (PINT $(-1))',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_x) = 0',
        '$bitnot_nan_diagnostics(S_done.EVENTS, "Warning") = 0',
        '$bitnot_nan_diagnostics(S_done.EVENTS, "Deprecated") = 1',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_left, 0) = S_left[.COMPLETION = BUDGET]',
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
