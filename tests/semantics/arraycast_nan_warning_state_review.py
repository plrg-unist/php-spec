#!/usr/bin/env python3
"""A supplied NaN array-cast handler Exception preserves the caller and live float CV."""
import base64
import json

import arraycast_nan_warning_review_cases as cases

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
            f'{state}_found = $arraycast_nan_seek({before}, {stage}, 3000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$arraycast_nan_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$arraycast_nan_plan(S_entry) = (pboolnotnanwarning)',
        'pboolnotnanwarning.LINE = 25',
        'pboolnotnanwarning.INPUT = VARIABLE ($ptascii("x")) 25',
        'S_entry.RESULT = pboolnotnanwarning.INPUT',
        'S_entry.TODO = (CAST_RESULT CASTARRAY 25) :: ptask_tail*',
        '$boolnot_nan_plan(S_entry) = eps',
        '~$boolnot_nan_source(S_entry, pboolnotnanwarning)',
        '$boolcast_nan_plan(S_entry) = eps',
        '~$boolcast_nan_source(S_entry, pboolnotnanwarning)',
        '$fparts_nan($float_decode(pboolnotnanwarning.BITS))',
        '$integer_operand_source(S_entry, pboolnotnanwarning.SITE, [PCFIELD 0], pboolnotnanwarning.INPUT)',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)',
        'pboolnotnanwarning.CELL = n_x',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
        'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        'S_entry.STORE[n_x] = DEFINED (PFLOAT pboolnotnanwarning.BITS)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '~(n_x <- S_entry.REFCELLS)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        '$arraycast_nan_source(S_entry, pboolnotnanwarning)',
        '$boolnot_nan_ready(S_entry, pboolnotnanwarning) = (pboolnotnanwarning.BITS)',
        '$boolnot_nan_snapshot(S_entry, pboolnotnanwarning)',
        '$arraycast_nan_warning_valid(S_entry, pboolnotnanwarning, 0)',
        '$arraycast_nan_warning_valid(S_entry, pboolnotnanwarning, 1)',
        'S_entry.EVENTS = eps',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'PhpStep: S_entry ~> S_capture_atomic',
        'S_capture_atomic = S_entry[.TODO = (ARRAYCAST_NAN_WARNING pboolnotnanwarning 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture = S_capture_atomic', '$arraycast_nan_frontier(S_capture, 1)',
        '$task_nodes(ARRAYCAST_NAN_WARNING pboolnotnanwarning 0) = eps',
        '$arraycast_nan_warning_valid(S_capture, pboolnotnanwarning, 0)',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_x) = 1',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        '$arraycast_nan_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ARRAYCAST_NAN_WARNING pboolnotnanwarning 1',
        'perrorcall.TARGET = eps', 'perrorcall.SITE = pboolnotnanwarning.SITE',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = $ptascii("unexpected NAN value was coerced to array")',
        'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE 25',
        '$error_call_valid(S_dispatch, perrorcall)',
        'S_dispatch.EVENTS = S_entry.EVENTS',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += [
        '$arraycast_nan_entered(S_entered.FRAMES)', 'S_entered.CURRENT =/= eps',
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_saved*',
        'perrorcall_entered.RESUME = ARRAYCAST_NAN_WARNING pboolnotnanwarning 1',
        'perrorcall_entered.TARGET =/= eps',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    seek('S_throw', 'S_entered', 6)
    checks += [
        'S_throw.TODO = (THROW_SEARCH n_second) :: ptask_caller*',
        'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps', '~$arraycast_nan_tasks(S_throw.TODO)',
        '$lookup(S_throw.ENV, $ptascii("x")) = (n_x)',
        'S_throw.STORE[n_x] = DEFINED (PFLOAT 0)',
        'S_throw.STORE[n_v] = DEFINED (PINT 100)',
        'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
        '~(n_x <- S_throw.REFCELLS)',
        '(HCELL n_x) <- S_throw.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_x) = 1',
        '$arraycast_nan_source(S_throw, pboolnotnanwarning)',
        '$boolnot_nan_ready(S_throw, pboolnotnanwarning) = (0)',
        '~$boolnot_nan_snapshot(S_throw, pboolnotnanwarning)',
        '~$arraycast_nan_warning_valid(S_throw, pboolnotnanwarning, 0)',
        '$arraycast_nan_warning_valid(S_throw, pboolnotnanwarning, 1)',
        '~$error_call_valid(S_throw, perrorcall)',
        '$error_call_valid(S_throw, perrorcall_entered)',
        '$task_nodes(ARRAYCAST_NAN_WARNING pboolnotnanwarning 1) = eps',
        '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
        '$throwable_live(S_throw, n_second)',
        '$throwable_previous_id(S_throw, n_second) = eps',
        '$throwable_field(S_throw, n_second, "line") = PINT 20',
        '$arraycast_nan_diagnostics(S_throw.EVENTS, "Warning") = 0',
        '$arraycast_nan_diagnostics(S_throw.EVENTS, "Deprecated") = 0',
        'S_throw.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
        'S_done = $drive_steps(S_throw, 3000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("x")) = (n_x)',
        'S_done.STORE[n_x] = DEFINED (PINT 8)',
        'S_done.STORE[n_v] = DEFINED (PINT 100)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        '(HCELL n_x) <- S_done.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_x) = 1',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_throw, 0) = S_throw[.COMPLETION = BUDGET]',
        'S_same_value_other_cell = S_throw[.ENV = [BIND ($ptascii("x")) n_v]][.STORE[n_v] = DEFINED (PFLOAT 0)]',
        '$boolnot_nan_ready(S_same_value_other_cell, pboolnotnanwarning) = eps',
        'S_retyped = S_throw[.TODO = [ARRAYCAST_NAN_WARNING pboolnotnanwarning 1]][.STORE[n_x] = DEFINED (PINT 0)]',
        '$boolnot_nan_ready(S_retyped, pboolnotnanwarning) = eps',
        'PhpStep: S_retyped ~> S_refused',
        'S_refused = S_retyped[.COMPLETION = UNSUPPORTED "array cast NaN changed CV representation"]',
    ]
    assert len(checks) == len(set(checks))
    return checks
