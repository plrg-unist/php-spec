#!/usr/bin/env python3
"""A selected float copy keeps its saved long after the source CV retires."""
import base64
import json

import bitnot_copy_warning_review_cases as cases
import bitnot_copy_warning_protocol as shared

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
            f'{state}_found = $bitnot_copy_seek({before}, {stage}, 3000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$bitnot_copy_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$bitnot_copy_plan(S_entry) = (pbitnotwarning)',
        '$bitnot_warning_plan(S_entry) = eps',
        '$bitnot_range_warning_plan(S_entry) = eps',
        '$bitnot_nan_warning_plan(S_entry) = eps',
        'pbitnotwarning.LINE = 25',
        'pbitnotwarning.INPUT = KNOWN (PFLOAT pbitnotwarning.BITS)',
        'S_entry.RESULT = pbitnotwarning.INPUT',
        'pbitnotwarning.BITS = 4623226492472524800',
        'pbitnotwarning.VALUE = 12',
        '$integer_operand_source(S_entry, pbitnotwarning.SITE, [PCFIELD 0], pbitnotwarning.INPUT)',
        '$integer_pointer_select(S_entry, pbitnotwarning.INPUT) = (INTEGER_COPY (PFLOAT pbitnotwarning.BITS))',
        '$bitnot_source_valid(S_entry, pbitnotwarning)',
        '$bitnot_snapshot(S_entry, pbitnotwarning)',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)',
        '$lookup(S_entry.ENV, $ptascii("pick")) = (n_pick)',
        '$lookup(S_entry.ENV, $ptascii("other")) = (n_other)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        'S_entry.STORE[n_x] = DEFINED (PFLOAT pbitnotwarning.BITS)',
        'S_entry.STORE[n_pick] = DEFINED (PBOOL true)',
        'S_entry.STORE[n_other] = DEFINED (PFLOAT 4628996729495093248)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '~(n_x <- S_entry.REFCELLS)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        'S_entry.EVENTS = eps',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'S_entry.TODO = ptask_old :: ptask_tail*',
        'PhpStep: S_entry ~> S_capture_atomic',
        'S_capture_atomic = S_entry[.TODO = (BITNOT_WARNING pbitnotwarning 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture = S_capture_atomic', '$bitnot_copy_frontier(S_capture, 1)',
        '$bitnot_warning_valid(S_capture, pbitnotwarning, 0)',
        '$bitnot_warning_valid(S_capture, pbitnotwarning, 1)',
        '$task_nodes(BITNOT_WARNING pbitnotwarning 0) = eps',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_x) = 1',
        '$call_descriptors_valid(S_capture)',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        '$bitnot_copy_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = BITNOT_WARNING pbitnotwarning 1',
        'perrorcall.TARGET = eps', 'perrorcall.SITE = pbitnotwarning.SITE',
        'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = $ptascii("Implicit conversion from float 12.5 to int loses precision")',
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
        'S_return.TODO = (BITNOT_WARNING pbitnotwarning 1) :: ptask_tail*',
        '$lookup(S_return.ENV, $ptascii("x")) = eps',
        '$lookup(S_return.ENV, $ptascii("pick")) = (n_pick)',
        '$lookup(S_return.ENV, $ptascii("other")) = (n_other)',
        'S_return.STORE[n_x] = DEFINED (PINT 99)',
        'S_return.STORE[n_pick] = DEFINED (PBOOL false)',
        'S_return.STORE[n_other] = DEFINED (PFLOAT 4628996729495093248)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)',
        'S_return.STORE[n_calls] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_x) = 0',
        '~((HCELL n_x) <- S_return.ALLOCATIONS)',
        '$integer_pointer_value(S_return, INTEGER_CV ($ptascii("x"))) = eps',
        '$integer_pointer_value(S_return, INTEGER_COPY (PFLOAT pbitnotwarning.BITS)) = (PFLOAT pbitnotwarning.BITS)',
        '$bitnot_source_valid(S_return, pbitnotwarning)',
        '$bitnot_snapshot(S_return, pbitnotwarning)',
        '$bitnot_warning_valid(S_return, pbitnotwarning, 0)',
        '$bitnot_warning_valid(S_return, pbitnotwarning, 1)',
        '$error_call_valid(S_return, perrorcall)',
        '$task_nodes(BITNOT_WARNING pbitnotwarning 1) = eps',
        '$bitnot_copy_diagnostics(S_return.EVENTS, "Deprecated") = 1',
        '$bitnot_copy_diagnostics(S_return.EVENTS, "Warning") = 0',
        'S_return.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'PhpStep: S_return ~> S_atomic',
        'S_atomic = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (PINT $(-13))]',
    ]
    step('S_result', 'S_return')
    checks += [
        'S_result = S_atomic', '$bitnot_copy_frontier(S_result, 5)',
        'S_result.RESULT = KNOWN (PINT $(-13))',
        'S_result.TODO = ptask_tail*', 'S_result.STORE = S_return.STORE',
        'S_result.ENV = S_return.ENV', 'S_result.REFCELLS = S_return.REFCELLS',
        'S_result.ALLOCATIONS = S_return.ALLOCATIONS',
        'S_result.EVENTS = S_return.EVENTS', 'S_result.STRINGDATA = S_return.STRINGDATA',
        'S_result.ARRAYS = S_return.ARRAYS', 'S_result.OBJECTS = S_return.OBJECTS',
        '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 3000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("x")) = (n_x_new)',
        'n_x_new =/= n_x',
        '$lookup(S_done.ENV, $ptascii("other")) = (n_other)',
        'S_done.STORE[n_x] = DEFINED (PINT 99)',
        'S_done.STORE[n_x_new] = DEFINED (PINT 8)',
        'S_done.STORE[n_other] = DEFINED (PFLOAT 4628996729495093248)',
        'S_done.STORE[n_pick] = DEFINED (PBOOL false)',
        'S_done.STORE[n_v] = DEFINED (PINT $(-13))',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_x) = 0',
        '~((HCELL n_x) <- S_done.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_x_new) = 1',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
        '$drive_steps(S_result, 0) = S_result[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
