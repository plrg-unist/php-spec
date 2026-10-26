#!/usr/bin/env python3
"""Reached copied range-only BITNOT callbacks and saved complement."""
import base64
import json

import bitnot_copy_range_warning_cases as cases
import bitnot_range_warning_protocol as range_shared
import bitnot_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = range_shared.HELPERS


def conditions(name, program, path, stdout):
    assert name in CASES
    throwing = name == 'copy-range-inf-supplied-throw'
    bits = 9218868437227405312 if throwing else 4890909195324358656
    value = '0' if throwing else '$(-9223372036854775808)'
    result = '$(-1)' if throwing else '9223372036854775807'
    message = ('The float INF is not representable as an int, cast occurred' if throwing
               else 'The float 9.223372036854776E+18 is not representable as an int, cast occurred')
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $bitnot_range_seek({before}, {stage}, 4000)',
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
        '$bitnot_warning_plan(S_entry) = eps', '$bitnot_copy_plan(S_entry) = eps',
        '$bitnot_nan_warning_plan(S_entry) = eps',
        'pbitnotwarning.INPUT = KNOWN (PFLOAT pbitnotwarning.BITS)',
        f'pbitnotwarning.BITS = {bits}', f'pbitnotwarning.VALUE = {value}',
        'pbitnotwarning.LINE = 25',
        f'$float_long(pbitnotwarning.BITS, true) = ({value}, [RANGEWARNING])',
        '$integer_pointer_select(S_entry, pbitnotwarning.INPUT) = (INTEGER_COPY (PFLOAT pbitnotwarning.BITS))',
        '$integer_operand_source(S_entry, pbitnotwarning.SITE, [PCFIELD 0], pbitnotwarning.INPUT)',
        '$bitnot_range_source_valid(S_entry, pbitnotwarning)', '$bitnot_snapshot(S_entry, pbitnotwarning)',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        'S_entry.STORE[n_x] = DEFINED (PFLOAT pbitnotwarning.BITS)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$bitnot_range_warning_plan(S_entry[.ORIGIN = eps]) = eps',
        '$bitnot_range_warning_plan(S_entry[.CODE = eps]) = eps',
        '$bitnot_range_warning_plan(S_entry[.RESULT = KNOWN PNULL]) = eps',
        '$bitnot_range_warning_plan(S_entry[.RESULT = KNOWN (PFLOAT 4623226492472524800)]) = eps',
        '$bitnot_range_warning_plan(S_entry[.RESULT = KNOWN (PFLOAT 9221120237041090560)]) = eps',
        '~$bitnot_range_source_valid(S_entry, pbitnotwarning[.LINE = 24])',
        '~$bitnot_range_source_valid(S_entry, pbitnotwarning[.VALUE = 1])',
        '~$bitnot_range_source_valid(S_entry, pbitnotwarning[.INPUT = VARIABLE ($ptascii("x")) 25])',
        '~$bitnot_range_source_valid(S_entry, pbitnotwarning[.BITS = 18446744073709551616])',
        'S_entry.TODO = ptask_old :: ptask_tail*',
        'PhpStep: S_entry ~> S_begin_raw',
        'S_begin_raw = S_entry[.TODO = (BITNOT_RANGE_WARNING pbitnotwarning 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture = S_begin_raw',
        'S_capture.TODO = (BITNOT_RANGE_WARNING pbitnotwarning 0) :: ptask_tail*',
        '$bitnot_range_warning_valid(S_capture, pbitnotwarning, 0)',
        '$task_nodes(BITNOT_RANGE_WARNING pbitnotwarning 0) = eps',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = BITNOT_RANGE_WARNING pbitnotwarning 1',
        'perrorcall.TARGET = eps', 'perrorcall.LEVEL = 2', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = $ptascii(' + json.dumps(message) + ')',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 8192])',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += ['$bitnot_entered(S_entered.FRAMES)', '$call_descriptors_valid(S_entered)']
    if throwing:
        seek('S_throw', 'S_entered', 6)
        checks += [
            'S_throw.TODO = (THROW_SEARCH n_second) :: ptask_caller*',
            '$lookup(S_throw.ENV, $ptascii("x")) = eps',
            'S_throw.STORE[n_x] = DEFINED (PINT 99)',
            'S_throw.STORE[n_v] = DEFINED (PINT 100)',
            'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_x) = 0',
            '~((HCELL n_x) <- S_throw.ALLOCATIONS)',
            '$integer_pointer_value(S_throw, INTEGER_COPY (PFLOAT pbitnotwarning.BITS)) = (PFLOAT pbitnotwarning.BITS)',
            '$bitnot_snapshot(S_throw, pbitnotwarning)',
            '$lookup(S_throw.ENV, $ptascii("second")) = (n_second_cell)',
            'S_throw.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
            '$throwable_live(S_throw, n_second)',
            '$throwable_previous_id(S_throw, n_second) = eps',
            '$throwable_field(S_throw, n_second, "line") = PINT 20',
            '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
            'S_done = $drive_steps(S_throw, 4000)',
        ]
    else:
        seek('S_return', 'S_entered', 4)
        checks += [
            'S_return.TODO = (BITNOT_RANGE_WARNING pbitnotwarning 1) :: ptask_tail*',
            '$lookup(S_return.ENV, $ptascii("x")) = eps',
            'S_return.STORE[n_x] = DEFINED (PINT 99)',
            'S_return.STORE[n_v] = DEFINED (PINT 100)',
            'S_return.STORE[n_calls] = DEFINED (PINT 1)',
            '$lookup(S_return.ENV, $ptascii("pick")) = (n_pick)',
            'S_return.STORE[n_pick] = DEFINED (PBOOL false)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_x) = 0',
            '~((HCELL n_x) <- S_return.ALLOCATIONS)',
            '$integer_pointer_value(S_return, INTEGER_COPY (PFLOAT pbitnotwarning.BITS)) = (PFLOAT pbitnotwarning.BITS)',
            '$bitnot_snapshot(S_return, pbitnotwarning)',
            '$bitnot_range_warning_valid(S_return, pbitnotwarning, 1)',
            '(DIAGNOSTIC "Warning" perrorcall.MESSAGE 25) <- S_return.EVENTS',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
            'PhpStep: S_return ~> S_result_raw',
            f'S_result_raw = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (PINT {result})]',
        ]
        step('S_result', 'S_return')
        checks += [
            'S_result = S_result_raw', '$bitnot_range_frontier(S_result, 5)',
            f'S_result.RESULT = KNOWN (PINT {result})',
            'S_result.STORE[n_v] = DEFINED (PINT 100)',
            'S_result.STORE[n_pick] = DEFINED (PBOOL false)',
            '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
            'S_done = $drive_steps(S_result, 4000)',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        'S_done.STORE[n_v] = DEFINED (PINT ' + ('100' if throwing else result) + ')',
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
