#!/usr/bin/env python3
"""The captured range float determines the complement after source retirement."""
import base64
import json

import bitnot_range_warning_review_cases as cases
import bitnot_range_warning_protocol as shared

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
            f'{state}_found = $bitnot_range_seek({before}, {stage}, 3000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$bitnot_range_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$bitnot_range_warning_plan(S_entry) = (pbitnotwarning)',
        '$bitnot_warning_plan(S_entry) = eps', '$bitnot_nan_warning_plan(S_entry) = eps',
        'pbitnotwarning.LINE = 25',
        'pbitnotwarning.INPUT = VARIABLE ($ptascii("x")) 25',
        'pbitnotwarning.BITS = 4890909195324358656',
        'pbitnotwarning.VALUE = $(-9223372036854775808)',
        '$float_long(pbitnotwarning.BITS, true) = ($(-9223372036854775808), [RANGEWARNING])',
        'n_message* = $ptascii("The float 9.223372036854776E+18 is not representable as an int, cast occurred")',
        '$integer_float_notices([RANGEWARNING], pbitnotwarning.BITS) = [(2, n_message*)]',
        '$bitnot_range_source_valid(S_entry, pbitnotwarning)',
        '$bitnot_snapshot(S_entry, pbitnotwarning)',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        'S_entry.STORE[n_x] = DEFINED (PFLOAT pbitnotwarning.BITS)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '~(n_x <- S_entry.REFCELLS)',
        '$integer_pointer_select(S_entry, pbitnotwarning.INPUT) = (INTEGER_CV ($ptascii("x")))',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        'S_entry.EVENTS = eps',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'S_entry.TODO = ptask_old :: ptask_tail*',
        'PhpStep: S_entry ~> S_capture_atomic',
        'S_capture_atomic = S_entry[.TODO = (BITNOT_RANGE_WARNING pbitnotwarning 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture = S_capture_atomic', '$bitnot_range_frontier(S_capture, 1)',
        '$bitnot_range_warning_valid(S_capture, pbitnotwarning, 0)',
        '$task_nodes(BITNOT_RANGE_WARNING pbitnotwarning 0) = eps',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_x) = 1',
        '$call_descriptors_valid(S_capture)',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        '$bitnot_range_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = BITNOT_RANGE_WARNING pbitnotwarning 1',
        'perrorcall.TARGET = eps', 'perrorcall.SITE = pbitnotwarning.SITE',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = n_message*',
        'perrorcall.EVENT = DIAGNOSTIC "Warning" n_message* 25',
        '$error_call_valid(S_dispatch, perrorcall)',
        'S_dispatch.EVENTS = S_entry.EVENTS', '$call_descriptors_valid(S_dispatch)',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += [
        '$bitnot_entered(S_entered.FRAMES)', 'S_entered.CURRENT =/= eps',
        '$call_descriptors_valid(S_entered)',
    ]
    seek('S_return', 'S_entered', 4)
    checks += [
        'S_return.TODO = (BITNOT_RANGE_WARNING pbitnotwarning 1) :: ptask_tail*',
        '$lookup(S_return.ENV, $ptascii("x")) = eps',
        'S_return.STORE[n_x] = DEFINED (PINT 99)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)',
        'S_return.STORE[n_calls] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_x) = 0',
        '~((HCELL n_x) <- S_return.ALLOCATIONS)',
        '$integer_pointer_value(S_return, INTEGER_CV ($ptascii("x"))) = eps',
        '$bitnot_range_source_valid(S_return, pbitnotwarning)',
        '~$bitnot_snapshot(S_return, pbitnotwarning)',
        '~$bitnot_range_warning_valid(S_return, pbitnotwarning, 0)',
        '$bitnot_range_warning_valid(S_return, pbitnotwarning, 1)',
        '$task_nodes(BITNOT_RANGE_WARNING pbitnotwarning 1) = eps',
        '(DIAGNOSTIC "Warning" n_message* 25) <- S_return.EVENTS',
        'S_return.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'PhpStep: S_return ~> S_atomic',
        'S_atomic = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (PINT 9223372036854775807)]',
    ]
    step('S_result', 'S_return')
    checks += [
        'S_result = S_atomic', '$bitnot_range_frontier(S_result, 5)',
        'S_result.RESULT = KNOWN (PINT 9223372036854775807)',
        'S_result.STORE = S_return.STORE', 'S_result.ENV = S_return.ENV',
        'S_result.REFCELLS = S_return.REFCELLS', 'S_result.ALLOCATIONS = S_return.ALLOCATIONS',
        'S_result.EVENTS = S_return.EVENTS', 'S_result.STRINGDATA = S_return.STRINGDATA',
        'S_result.ARRAYS = S_return.ARRAYS', 'S_result.OBJECTS = S_return.OBJECTS',
        '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 3000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("x")) = (n_fresh_x)',
        'n_fresh_x =/= n_x', 'S_done.STORE[n_fresh_x] = DEFINED (PINT 8)',
        'S_done.STORE[n_x] = DEFINED (PINT 99)',
        'S_done.STORE[n_v] = DEFINED (PINT 9223372036854775807)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_x) = 0',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_fresh_x) = 1',
        '~((HCELL n_x) <- S_done.ALLOCATIONS)',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
        '$drive_steps(S_result, 0) = S_result[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
