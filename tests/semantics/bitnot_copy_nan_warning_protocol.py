#!/usr/bin/env python3
"""Reached copied-NaN BITNOT notice and saved-result continuations."""
import base64
import json

import bitnot_copy_nan_warning_cases as cases
import bitnot_nan_warning_protocol as nan
import bitnot_warning_protocol as shared

CASES = ('copy-nan-pending-ineligible-precision', 'copy-nan-selected-two-notices')
HELPERS = nan.HELPERS


def conditions(name, program, path, stdout):
    assert name in CASES
    pending = name == 'copy-nan-pending-ineligible-precision'
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
        '$bitnot_copy_plan(S_entry) = eps', '$bitnot_warning_plan(S_entry) = eps',
        'pbitnotwarning.INPUT = KNOWN (PFLOAT pbitnotwarning.BITS)',
        'pbitnotwarning.BITS = 9221120237041090560', 'pbitnotwarning.VALUE = 0',
        'pbitnotwarning.LINE = 25',
        '$float_long(pbitnotwarning.BITS, true) = (0, [RANGEWARNING, PRECISIONLOSS])',
        '$integer_pointer_select(S_entry, pbitnotwarning.INPUT) = (INTEGER_COPY (PFLOAT pbitnotwarning.BITS))',
        '$integer_operand_source(S_entry, pbitnotwarning.SITE, [PCFIELD 0], pbitnotwarning.INPUT)',
        '$bitnot_nan_source_valid(S_entry, pbitnotwarning)', '$bitnot_snapshot(S_entry, pbitnotwarning)',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        'S_entry.STORE[n_x] = DEFINED (PFLOAT pbitnotwarning.BITS)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$bitnot_nan_warning_plan(S_entry[.ORIGIN = eps]) = eps',
        '$bitnot_nan_warning_plan(S_entry[.CODE = eps]) = eps',
        '$bitnot_nan_warning_plan(S_entry[.RESULT = KNOWN PNULL]) = eps',
        '~$bitnot_nan_source_valid(S_entry, pbitnotwarning[.LINE = 24])',
        '~$bitnot_nan_source_valid(S_entry, pbitnotwarning[.VALUE = 1])',
        '~$bitnot_nan_source_valid(S_entry, pbitnotwarning[.INPUT = VARIABLE ($ptascii("x")) 25])',
        '~$bitnot_nan_source_valid(S_entry, pbitnotwarning[.BITS = 18446744073709551616])',
        'S_entry.TODO = ptask_old :: ptask_tail*',
        'PhpStep: S_entry ~> S_begin_raw',
        'S_begin_raw = S_entry[.TODO = (BITNOT_NAN_WARNING pbitnotwarning 0 eps) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture = S_begin_raw',
        'S_capture.TODO = (BITNOT_NAN_WARNING pbitnotwarning 0 eps) :: ptask_tail*',
        '$bitnot_nan_warning_valid(S_capture, pbitnotwarning, 0, eps)',
        '$task_nodes(BITNOT_NAN_WARNING pbitnotwarning 0 eps) = eps',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = BITNOT_NAN_WARNING pbitnotwarning 1 eps',
        'perrorcall.TARGET = eps', 'perrorcall.LEVEL = 2', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = $ptascii("The float NAN is not representable as an int, cast occurred")',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 8192])',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += ['$bitnot_nan_entered(S_entered.FRAMES, 0)', '$call_descriptors_valid(S_entered)']
    if pending:
        seek('S_pending', 'S_entered', 9)
        checks += [
            'S_pending.TODO = (BITNOT_NAN_WARNING pbitnotwarning 1 (n_second)) :: ptask_caller*',
            '$lookup(S_pending.ENV, $ptascii("x")) = eps',
            'S_pending.STORE[n_x] = DEFINED (PINT 99)',
            'S_pending.STORE[n_v] = DEFINED (PINT 100)',
            'S_pending.STORE[n_calls] = DEFINED (PINT 1)',
            '$heap_owners($heap_prune($heap_graph(S_pending)), HCELL n_x) = 0',
            '~((HCELL n_x) <- S_pending.ALLOCATIONS)',
            '$integer_pointer_value(S_pending, INTEGER_COPY (PFLOAT pbitnotwarning.BITS)) = (PFLOAT pbitnotwarning.BITS)',
            '$bitnot_snapshot(S_pending, pbitnotwarning)',
            '$bitnot_nan_warning_valid(S_pending, pbitnotwarning, 1, (n_second))',
            '~$error_handler_eligible(S_pending, 8192)',
            '$lookup(S_pending.ENV, $ptascii("second")) = (n_second_cell)',
            'S_pending.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            '$task_nodes(BITNOT_NAN_WARNING pbitnotwarning 1 (n_second)) = [HOBJECT n_second]',
            '$heap_owners($heap_prune($heap_graph(S_pending)), HOBJECT n_second) = 2',
            '$throwable_live(S_pending, n_second)',
            '$throwable_previous_id(S_pending, n_second) = eps',
            '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
        ]
        step('S_reported', 'S_pending')
        checks += [
            'S_reported.TODO = (BITNOT_NAN_WARNING pbitnotwarning 2 (n_second)) :: ptask_caller*',
            '$bitnot_nan_diagnostics(S_reported.EVENTS, "Deprecated") = 1',
            '$bitnot_nan_warning_valid(S_reported, pbitnotwarning, 2, (n_second))',
            '$call_descriptors_valid(S_reported)', '$heap_valid($heap_graph(S_reported))',
        ]
        step('S_throw', 'S_reported')
        checks += [
            'S_throw.TODO = (THROW_SEARCH n_second) :: ptask_caller*',
            '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]',
            'S_throw.STORE[n_v] = DEFINED (PINT 100)',
            '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
            'S_done = $drive_steps(S_throw, 4000)',
        ]
    else:
        seek('S_left', 'S_entered', 4)
        checks += [
            'S_left.TODO = (BITNOT_NAN_WARNING pbitnotwarning 1 eps) :: ptask_tail*',
            'S_left.STORE[n_x] = DEFINED (PINT 99)',
            'S_left.STORE[n_calls] = DEFINED (PINT 1)',
            '$lookup(S_left.ENV, $ptascii("pick")) = (n_pick)',
            'S_left.STORE[n_pick] = DEFINED (PBOOL false)',
            '$bitnot_snapshot(S_left, pbitnotwarning)',
            '$bitnot_nan_warning_valid(S_left, pbitnotwarning, 1, eps)',
            '$call_descriptors_valid(S_left)', '$heap_valid($heap_graph(S_left))',
        ]
        step('S_second', 'S_left')
        checks += [
            'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
            'perrorcall_second.RESUME = BITNOT_NAN_WARNING pbitnotwarning 2 eps',
            'perrorcall_second.LEVEL = 8192', 'perrorcall_second.LINE = 25',
            '$error_call_valid(S_second, perrorcall_second)',
            '$call_descriptors_valid(S_second)', '$heap_valid($heap_graph(S_second))',
        ]
        seek('S_return', 'S_second', 7)
        checks += [
            'S_return.TODO = (BITNOT_NAN_WARNING pbitnotwarning 2 eps) :: ptask_tail*',
            '$lookup(S_return.ENV, $ptascii("x")) = eps',
            'S_return.STORE[n_x] = DEFINED (PINT 99)',
            'S_return.STORE[n_pick] = DEFINED (PBOOL false)',
            'S_return.STORE[n_calls] = DEFINED (PINT 2)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_x) = 0',
            '~((HCELL n_x) <- S_return.ALLOCATIONS)',
            '$integer_pointer_value(S_return, INTEGER_COPY (PFLOAT pbitnotwarning.BITS)) = (PFLOAT pbitnotwarning.BITS)',
            '$bitnot_snapshot(S_return, pbitnotwarning)',
            '$bitnot_nan_warning_valid(S_return, pbitnotwarning, 2, eps)',
            '$bitnot_nan_diagnostics(S_return.EVENTS, "Deprecated") = 1',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        ]
        step('S_result', 'S_return')
        checks += [
            'S_result.RESULT = KNOWN (PINT $(-1))',
            'S_result.STORE[n_v] = DEFINED (PINT 100)',
            'S_result.STORE[n_pick] = DEFINED (PBOOL false)',
            '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
            'S_done = $drive_steps(S_result, 4000)',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
        'S_done.STORE[n_calls] = DEFINED (PINT ' + ('1' if pending else '2') + ')',
        'S_done.STORE[n_v] = DEFINED (PINT ' + ('100' if pending else '$(-1)') + ')',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks


def main():
    shared.cases, shared.CASES, shared.HELPERS, shared.conditions = cases, CASES, HELPERS, conditions
    return shared.main()


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
