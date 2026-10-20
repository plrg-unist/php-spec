#!/usr/bin/env python3
"""Modulo reads the current divisor only after both saved NaN notices return."""
import base64
import json

import mod_nan_pending_review_cases as cases
import mod_nan_pending_protocol as shared

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
            f'{state}_found = $mod_nan_seek({before}, {stage}, 4000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$mod_nan_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$integer_operator_plan(S_entry) = (pintegeroperation)',
        '$integer_operation_valid(S_entry, pintegeroperation)',
        'pintegeroperation.OP = MODULO', '~pintegeroperation.SWAPPED',
        'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("x")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("y")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("x"))',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("y"))',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)',
        '$lookup(S_entry.ENV, $ptascii("y")) = (n_y)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'S_entry.STORE[n_x] = DEFINED (PFLOAT n_bits)',
        '$float_decode(n_bits) = NOTNUMBER n_nan',
        'S_entry.STORE[n_y] = DEFINED (PINT 0)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '$integer_binary(MODULO, 0, 0) = INTZERO',
        '$integer_binary(MODULO, 88, 5) = IRESULT 3',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_y) = 1',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
    ]
    seek('S_capture', 'S_entry', 1)
    checks += [
        'S_capture.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 0) :: ptask_tail*',
        'pintegerconversion.INPUT = PFLOAT n_bits', 'pintegerconversion.VALUE = 0',
        'pintegerconversion.NOTICES = [(2, $ptascii("The float NAN is not representable as an int, cast occurred")), (8192, $ptascii("Implicit conversion from float NAN to int loses precision"))]',
        '$integer_conversion(PFLOAT n_bits) = (pintegerconversion)',
        '$integer_warning_valid(S_capture, pintegeroperation, INTEGER_LEFT, pintegerconversion, 0)',
        '$mod_nan_pending_source(S_capture, pintegeroperation, pintegerconversion)',
        '$task_nodes(INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 0) = eps',
        '$call_descriptors_valid(S_capture)',
    ]
    step('S_first', 'S_capture')
    checks += [
        '$mod_nan_frontier(S_first, 2)',
        'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
        'perrorcall_first.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 1',
        'perrorcall_first.LEVEL = 2', 'perrorcall_first.LINE = 25',
        'perrorcall_first.TARGET = eps',
        'perrorcall_first.MESSAGE = $ptascii("The float NAN is not representable as an int, cast occurred")',
        '$error_call_valid(S_first, perrorcall_first)', '$call_descriptors_valid(S_first)',
    ]
    seek('S_first_entered', 'S_first', 3)
    checks += ['$mod_nan_entered(S_first_entered.FRAMES, 1)', '$call_descriptors_valid(S_first_entered)']
    seek('S_left', 'S_first_entered', 4)
    checks += [
        'S_left.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 1) :: ptask_tail*',
        'S_left.STORE[n_x] = DEFINED (PINT 99)',
        'S_left.STORE[n_y] = DEFINED (PINT 0)',
        'S_left.STORE[n_calls] = DEFINED (PINT 1)',
        'S_left.STORE[n_v] = DEFINED (PINT 100)',
        '$integer_pointer_value(S_left, pintegeroperation.LEFTPOINTER) = (PINT 99)',
        '$integer_pointer_value(S_left, pintegeroperation.RIGHTPOINTER) = (PINT 0)',
        '$integer_warning_valid(S_left, pintegeroperation, INTEGER_LEFT, pintegerconversion, 1)',
        '$mod_nan_diagnostics(S_left.EVENTS, "Warning") = 0',
        '$mod_nan_diagnostics(S_left.EVENTS, "Deprecated") = 0',
        '$call_descriptors_valid(S_left)',
    ]
    step('S_second', 'S_left')
    checks += [
        '$mod_nan_frontier(S_second, 5)',
        'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
        'perrorcall_second.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 2',
        'perrorcall_second.LEVEL = 8192', 'perrorcall_second.LINE = 25',
        'perrorcall_second.TARGET = eps',
        'perrorcall_second.MESSAGE = $ptascii("Implicit conversion from float NAN to int loses precision")',
        '$error_call_valid(S_second, perrorcall_second)', '$call_descriptors_valid(S_second)',
    ]
    seek('S_second_entered', 'S_second', 6)
    checks += ['$mod_nan_entered(S_second_entered.FRAMES, 2)', '$call_descriptors_valid(S_second_entered)']
    seek('S_return', 'S_second_entered', 7)
    checks += [
        'S_return.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 2) :: ptask_tail*',
        'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
        'S_return.STORE[n_x] = DEFINED (PINT 88)',
        'S_return.STORE[n_y] = DEFINED (PINT 5)',
        'S_return.STORE[n_calls] = DEFINED (PINT 2)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)',
        '$integer_pointer_value(S_return, pintegeroperation.LEFTPOINTER) = (PINT 88)',
        '$integer_pointer_value(S_return, pintegeroperation.RIGHTPOINTER) = (PINT 5)',
        '$integer_warning_valid(S_return, pintegeroperation, INTEGER_LEFT, pintegerconversion, 2)',
        '$mod_nan_pending_source(S_return, pintegeroperation, pintegerconversion)',
        '$mod_nan_diagnostics(S_return.EVENTS, "Warning") = 0',
        '$mod_nan_diagnostics(S_return.EVENTS, "Deprecated") = 1',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'PhpStep: S_return ~> S_left_atomic',
        'S_left_atomic = S_return[.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT 0)) :: ptask_tail*][.RESULT = KNOWN PNULL]',
    ]
    step('S_right', 'S_return')
    checks += [
        '$mod_nan_frontier(S_right, 8)',
        'S_right.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT 0)) :: ptask_tail*',
        'S_right.STORE = S_return.STORE', 'S_right.ENV = S_return.ENV',
        'S_right.EVENTS = S_return.EVENTS',
        'PhpStep: S_right ~> S_right_atomic',
        'S_right_atomic.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT 0) pintegerconversion_right 0) :: ptask_tail*',
        'S_right_atomic = S_right[.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT 0) pintegerconversion_right 0) :: ptask_tail*]',
        'pintegerconversion_right.INPUT = PINT 5',
        'pintegerconversion_right.VALUE = 5', 'pintegerconversion_right.NOTICES = eps',
    ]
    step('S_right_capture', 'S_right')
    checks += [
        '$mod_nan_frontier(S_right_capture, 9)',
        'S_right_capture.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT 0) pintegerconversion_right 0) :: ptask_tail*',
        '$integer_warning_valid(S_right_capture, pintegeroperation, INTEGER_RIGHT 0, pintegerconversion_right, 0)',
        '$call_descriptors_valid(S_right_capture)',
        'PhpStep: S_right_capture ~> S_result_atomic',
        'S_result_atomic = S_right_capture[.TODO = ptask_tail*][.RESULT = KNOWN (PINT 0)]',
    ]
    step('S_result', 'S_right_capture')
    checks += [
        '$mod_nan_frontier(S_result, 10)',
        'S_result.TODO = ptask_tail*', 'S_result.RESULT = KNOWN (PINT 0)',
        'S_result.STORE = S_return.STORE', 'S_result.ENV = S_return.ENV',
        'S_result.REFCELLS = S_return.REFCELLS',
        'S_result.ALLOCATIONS = S_return.ALLOCATIONS',
        'S_result.STRINGDATA = S_return.STRINGDATA',
        'S_result.ARRAYS = S_return.ARRAYS', 'S_result.OBJECTS = S_return.OBJECTS',
        'S_result.EVENTS = S_return.EVENTS',
        '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_x) = 1',
        '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_y) = 1',
        '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 4000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.CURRENT = eps',
        'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_x] = DEFINED (PINT 8)',
        'S_done.STORE[n_y] = DEFINED (PINT 9)',
        'S_done.STORE[n_v] = DEFINED (PINT 0)',
        'S_done.STORE[n_calls] = DEFINED (PINT 2)',
        '$mod_nan_diagnostics(S_done.EVENTS, "Warning") = 0',
        '$mod_nan_diagnostics(S_done.EVENTS, "Deprecated") = 1',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_left, 0) = S_left[.COMPLETION = BUDGET]',
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
