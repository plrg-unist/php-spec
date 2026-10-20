#!/usr/bin/env python3
"""A thrown explicit NaN cast has one notice and no result delivery."""
import base64
import json

import int_cast_range_warning_review_cases as cases
import int_cast_range_warning_protocol as shared

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
            f'{state}_found = $int_cast_range_seek({before}, {stage}, 3000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$int_cast_range_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$int_cast_range_plan(S_entry) = (pbitnotwarning)',
        '$bitnot_warning_plan(S_entry) = eps',
        '$bitnot_nan_warning_plan(S_entry) = eps',
        '$bitnot_range_warning_plan(S_entry) = eps',
        'pbitnotwarning.LINE = 25',
        'pbitnotwarning.INPUT = VARIABLE ($ptascii("x")) 25',
        'pbitnotwarning.BITS = 9221120237041090560',
        'pbitnotwarning.VALUE = 0',
        '$float_long(pbitnotwarning.BITS, false) = (0, [RANGEWARNING])',
        '$float_long(pbitnotwarning.BITS, true) = (0, [RANGEWARNING, PRECISIONLOSS])',
        'n_message* = $ptascii("The float NAN is not representable as an int, cast occurred")',
        '$integer_float_notices([RANGEWARNING], pbitnotwarning.BITS) = [(2, n_message*)]',
        '$int_cast_range_source_valid(S_entry, pbitnotwarning)',
        '$bitnot_snapshot(S_entry, pbitnotwarning)',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
        'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        'S_entry.STORE[n_x] = DEFINED (PFLOAT pbitnotwarning.BITS)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        'S_entry.ERRORHANDLER.LEVELS = 2',
        '~(n_x <- S_entry.REFCELLS)',
        '$integer_pointer_select(S_entry, pbitnotwarning.INPUT) = (INTEGER_CV ($ptascii("x")))',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        'S_entry.EVENTS = eps',
        '$call_descriptors_valid(S_entry)',
        '$heap_valid($heap_graph(S_entry))',
        'S_entry.TODO = ptask_old :: ptask_tail*',
        'PhpStep: S_entry ~> S_capture_atomic',
        'S_capture_atomic = S_entry[.TODO = (INT_CAST_RANGE_WARNING pbitnotwarning 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture = S_capture_atomic',
        '$int_cast_range_frontier(S_capture, 1)',
        '$int_cast_range_warning_valid(S_capture, pbitnotwarning, 0)',
        '$task_nodes(INT_CAST_RANGE_WARNING pbitnotwarning 0) = eps',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_x) = 1',
        '$call_descriptors_valid(S_capture)',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        '$int_cast_range_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = INT_CAST_RANGE_WARNING pbitnotwarning 1',
        'perrorcall.TARGET = eps',
        'perrorcall.SITE = pbitnotwarning.SITE',
        'perrorcall.LINE = 25',
        'perrorcall.LEVEL = 2',
        'perrorcall.MESSAGE = n_message*',
        'perrorcall.EVENT = DIAGNOSTIC "Warning" n_message* 25',
        '$error_call_valid(S_dispatch, perrorcall)',
        'S_dispatch.EVENTS = S_entry.EVENTS',
        '$call_descriptors_valid(S_dispatch)',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += [
        '$bitnot_entered(S_entered.FRAMES)',
        'S_entered.CURRENT =/= eps',
        '$call_descriptors_valid(S_entered)',
    ]
    seek('S_throw', 'S_entered', 6)
    checks += [
        'S_throw.TODO = (THROW_SEARCH n_second) :: ptask_caller*',
        'S_throw.CURRENT = eps',
        'S_throw.FRAMES = eps',
        '~$bitnot_tasks(S_throw.TODO)',
        '$lookup(S_throw.ENV, $ptascii("x")) = eps',
        'S_throw.STORE[n_x] = DEFINED (PINT 99)',
        'S_throw.STORE[n_v] = DEFINED (PINT 100)',
        'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_x) = 0',
        '~((HCELL n_x) <- S_throw.ALLOCATIONS)',
        '$integer_pointer_value(S_throw, INTEGER_CV ($ptascii("x"))) = eps',
        '$int_cast_range_source_valid(S_throw, pbitnotwarning)',
        '~$bitnot_snapshot(S_throw, pbitnotwarning)',
        '~$int_cast_range_warning_valid(S_throw, pbitnotwarning, 0)',
        '$int_cast_range_warning_valid(S_throw, pbitnotwarning, 1)',
        '$task_nodes(INT_CAST_RANGE_WARNING pbitnotwarning 1) = eps',
        '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
        '$throwable_live(S_throw, n_second)',
        '$throwable_previous_id(S_throw, n_second) = eps',
        '$throwable_field(S_throw, n_second, "line") = PINT 20',
        '$int_cast_range_diagnostics(S_throw.EVENTS, "Warning") = 0',
        '$int_cast_range_diagnostics(S_throw.EVENTS, "Deprecated") = 0',
        'S_throw.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_throw)',
        '$heap_valid($heap_graph(S_throw))',
        'S_done = $drive_steps(S_throw, 3000)',
        'S_done.COMPLETION = NORMAL',
        'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps',
        'S_done.FRAMES = eps',
        'S_done.CURRENT = eps',
        'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("x")) = (n_fresh_x)',
        'n_fresh_x =/= n_x',
        'S_done.STORE[n_fresh_x] = DEFINED (PINT 8)',
        'S_done.STORE[n_x] = DEFINED (PINT 99)',
        'S_done.STORE[n_v] = DEFINED (PINT 100)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_x) = 0',
        '~((HCELL n_x) <- S_done.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_fresh_x) = 1',
        '$int_cast_range_diagnostics(S_done.EVENTS, "Warning") = 0',
        '$int_cast_range_diagnostics(S_done.EVENTS, "Deprecated") = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_throw, 0) = S_throw[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
