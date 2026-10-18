#!/usr/bin/env python3
"""Reached single-LEFT continuations enter existing delayed RHS conversions."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import single_left_bridge_review_cases as cases
import single_left_bridge_protocol as shared

REVIEW_HELPERS = r'''
dec $single_left_review_diagnostic(pevent, text) : nat
def $single_left_review_diagnostic(DIAGNOSTIC text n* z, text) = 1
def $single_left_review_diagnostic(DIAGNOSTIC_SOURCE n_source text n* z, text) = 1
def $single_left_review_diagnostic(DIAGNOSTIC_STACK text n* z n_trace*, text) = 1
def $single_left_review_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n* z n_trace*, text) = 1
def $single_left_review_diagnostic(pevent, text) = 0 -- otherwise
dec $single_left_review_diagnostics(pevent*, text) : nat
def $single_left_review_diagnostics(eps, text) = 0
def $single_left_review_diagnostics(pevent :: pevent_tail*, text) = $($single_left_review_diagnostic(pevent, text) + $single_left_review_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    family, single_tag, both_tag, operation, left_value, right_value, mode = {
        'single-left-bridge-mod-null-default': ('modassign', 'MOD_ASSIGN_WARNING', 'MOD_ASSIGN_BOTH_LEFT', 'MODULO', 'PINT 99', 'PNULL', 'zero'),
        'single-left-bridge-xor-negative-reference-default': ('bitassign', 'BIT_ASSIGN_WARNING', 'BIT_ASSIGN_BOTH_LEFT', 'BITXOR', 'PINT 99', 'PFLOAT 13832806255468478464', 'xor'),
        'single-left-bridge-shift-array-default': ('shiftassign', 'SHIFT_ASSIGN_WARNING', 'SHIFT_ASSIGN_BOTH_LEFT', 'SHIFTRIGHT', 'PBOOL false', 'PARRAY n_array', 'array'),
    }[name]
    single = lambda stage: f'{single_tag} pintegeroperation n_target n_right n_bits_left i_left {stage}'
    both = lambda stage: f'{both_tag} pintegeroperation n_target n_right n_bits_left i_left {stage}'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_plan_found = $single_left_bridge_seek(S_initial, 0, 4000)',
        r'S_plan_found.COMPLETION = NORMAL \/ S_plan_found.COMPLETION = BUDGET',
        'S_plan = S_plan_found[.COMPLETION = NORMAL]', '$single_left_bridge_frontier(S_plan, 0)',
        f'${family}_warning_plan(S_plan) = (' + single(0) + ')',
        f'${family}_both_warning_plan(S_plan) = eps',
        'S_marker_budget = $drive_steps(S_plan, 1)', 'S_marker_budget.COMPLETION = BUDGET',
        'S = S_marker_budget[.COMPLETION = NORMAL]', '$single_left_bridge_frontier(S, 1)',
        'S.TODO = (' + single(0) + ') :: ptask_tail*',
        'n_bits_left = 4623226492472524800', 'i_left = 12',
        'pintegeroperation.OP = ' + operation, '~pintegeroperation.SWAPPED',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LINE = 25', 'S.ORIGIN = (pintegeroperation.SITE)',
        '$lookup(S.ENV, $ptascii("left")) = (n_target)', '$lookup(S.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S.ENV, $ptascii("v")) = (n_v)', '$lookup(S.ENV, $ptascii("calls")) = (n_calls)',
        'S.STORE[n_target] = DEFINED (PFLOAT n_bits_left)', 'S.STORE[n_right] = DEFINED (PINT 3)',
        'S.STORE[n_v] = DEFINED (PINT 100)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        '~(n_target <- S.REFCELLS)', '~(n_right <- S.REFCELLS)',
        '$call_task_valid(S, ' + single(0) + ')', '~$call_task_valid(S, ' + both(0) + ')',
        f'~${family}_warning_valid(S, pintegeroperation, n_target, n_right, 4623789442425946112, 13, 0)',
        '$task_nodes(' + single(0) + ') = eps',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'S_return_found = $single_left_bridge_seek(S, 4, 4000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', '$single_left_bridge_frontier(S_return, 4)',
        'S_return.TODO = (' + single(1) + ') :: ptask_tail*',
        'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
        '$lookup(S_return.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S_return.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_return.ENV, $ptascii("alias")) = (n_target)',
        'S_return.STORE[n_target] = DEFINED (' + left_value + ')',
        'S_return.STORE[n_right] = DEFINED (' + right_value + ')',
        'S_return.STORE[n_v] = DEFINED (PINT 100)', 'S_return.STORE[n_calls] = DEFINED (PINT 1)',
        'n_target <- S_return.REFCELLS', '~(n_right <- S_return.REFCELLS)',
        '$call_task_valid(S_return, ' + single(1) + ')', '~$call_task_valid(S_return, ' + single(0) + ')',
        '$modassign_warning_ready(S_return, pintegeroperation, n_target, n_right) = eps',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_target) = 2',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 1',
        'S_return.ERRORHANDLER = S.ERRORHANDLER',
        '$single_left_review_diagnostics(S_return.EVENTS, "Deprecated") = ' + ('0' if mode == 'xor' else '1'),
        '$single_left_review_diagnostics(S_return.EVENTS, "Warning") = 0',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'S_bridge_budget = $drive_steps(S_return, 1)', 'S_bridge_budget.COMPLETION = BUDGET',
        'S_bridge = S_bridge_budget[.COMPLETION = NORMAL]', '$single_left_bridge_frontier(S_bridge, 5)',
        'S_bridge = S_return[.TODO = (' + both(1) + ') :: ptask_tail*]',
        '$call_task_valid(S_bridge, ' + both(1) + ')', '~$call_task_valid(S_bridge, ' + both(0) + ')',
        '$task_nodes(' + both(1) + ') = eps',
        '$call_descriptors_valid(S_bridge)', '$heap_valid($heap_graph(S_bridge))',
    ]
    if mode == 'xor':
        right = lambda stage: f'BIT_ASSIGN_BOTH_RIGHT pintegeroperation n_target n_right n_bits_left i_left n_bits_right i_right {stage}'
        checks += [
            '$modassign_both_right_snapshot(S_bridge, pintegeroperation, n_target, n_right) = ((13832806255468478464, (-1)))',
            'S_right_budget = $drive_steps(S_bridge, 1)', 'S_right_budget.COMPLETION = BUDGET',
            'S_right = S_right_budget[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_right, 5)',
            'S_right.TODO = (' + right(0) + ') :: ptask_tail*',
            'n_bits_right = 13832806255468478464', 'i_right = (-1)',
            '$call_task_valid(S_right, ' + right(0) + ')', '$task_nodes(' + right(0) + ') = eps',
            'S_second_budget = $drive_steps(S_right, 1)', 'S_second_budget.COMPLETION = BUDGET',
            'S_second = S_second_budget[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_second, 6)',
            'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = ' + right(1), 'perrorcall.TARGET = eps',
            'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 25',
            'perrorcall.MESSAGE = $ptascii("Implicit conversion from float -1.5 to int loses precision")',
            '$error_call_valid(S_second, perrorcall)',
            'perrorcall_changed = perrorcall[.RESUME = BIT_ASSIGN_BOTH_RIGHT pintegeroperation n_target n_right n_bits_left i_left 13836183955189006336 (-2) 1][.MESSAGE = $ptascii("Implicit conversion from float -2.5 to int loses precision")][.EVENT = DIAGNOSTIC "Deprecated" ($ptascii("Implicit conversion from float -2.5 to int loses precision")) 25]',
            '~$error_call_valid(S_second, perrorcall_changed)',
            'S_late_found = $bitassign_both_seek(S_second, 8, 4000)',
            r'S_late_found.COMPLETION = NORMAL \/ S_late_found.COMPLETION = BUDGET',
            'S_late = S_late_found[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_late, 8)',
            'S_late.TODO = (' + right(1) + ') :: ptask_tail*',
            '$lookup(S_late.ENV, $ptascii("left")) = (n_target)',
            '$lookup(S_late.ENV, $ptascii("alias")) = (n_target)',
            '$lookup(S_late.ENV, $ptascii("right")) = (n_target)',
            'S_late.STORE[n_target] = DEFINED (PINT 88)', 'S_late.STORE[n_calls] = DEFINED (PINT 2)',
            '$call_task_valid(S_late, ' + right(1) + ')', '~$call_task_valid(S_late, ' + right(0) + ')',
            '$heap_owners($heap_prune($heap_graph(S_late)), HCELL n_target) = 3',
            '$single_left_review_diagnostics(S_late.EVENTS, "Deprecated") = 1',
            '$powerassign_warning_ready(S_late, pintegeroperation, n_target)',
            '$integer_binary(pintegeroperation.OP, i_left, i_right) = IRESULT (-13)',
            'S_commit_budget = $drive_steps(S_late, 1)', 'S_commit_budget.COMPLETION = BUDGET',
            'S_commit = S_commit_budget[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_commit, 9)',
            'S_commit.TODO = ptask_tail*', 'S_commit.RESULT = KNOWN (PINT (-13))',
            '$lookup(S_commit.ENV, $ptascii("left")) = (n_new)', 'n_new = |S_late.STORE|',
            'S_commit.CELL = n_new', 'S_commit.LOCATION = ROOT n_new', '~(n_new <- S_commit.REFCELLS)',
            '$lookup(S_commit.ENV, $ptascii("alias")) = (n_target)',
            '$lookup(S_commit.ENV, $ptascii("right")) = (n_target)',
            'S_commit.STORE = S_late.STORE ++ [DEFINED (PINT (-13))]',
            'S_commit.ALLOCATIONS = S_late.ALLOCATIONS ++ [HCELL n_new]',
            'S_commit.REFCELLS = S_late.REFCELLS', 'S_commit.EVENTS = S_late.EVENTS',
            'S_commit.STRINGDATA = S_late.STRINGDATA', 'S_commit.ARRAYS = S_late.ARRAYS',
            '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_target) = 2',
            '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_new) = 1',
            '$call_descriptors_valid(S_commit)', '$heap_valid($heap_graph(S_commit))',
            'S_done = $drive_steps(S_commit, 4000)',
            '$lookup(S_done.ENV, $ptascii("left")) = (n_new)',
            'S_done.STORE[n_new] = DEFINED (PINT 7)', 'S_done.STORE[n_target] = DEFINED (PINT 6)',
            'S_done.STORE[n_v] = DEFINED (PINT (-13))', 'S_done.STORE[n_calls] = DEFINED (PINT 2)',
        ]
    else:
        kind, message = ('DivisionByZeroError', 'Modulo by zero') if mode == 'zero' else ('TypeError', 'Unsupported operand types: bool >> array')
        if mode == 'zero':
            checks += ['$bothassign_quiet_scalar_snapshot(S_bridge, pintegeroperation, n_target, n_right) = (0)']
        else:
            checks += [
                'parray_right = S_bridge.ARRAYS[n_array]',
                '$entry_lookup(parray_right.ITEMS, KINT 0) = (DIRECT (PINT 3))',
                '$heap_count(HARRAY n_array, $pools_nodes(S_bridge.POOLS)) = 1',
                '$heap_owners($heap_prune($heap_graph(S_bridge)), HARRAY n_array) = 2',
                '$bothassign_type_failure_operands(S_bridge, pintegeroperation, n_target, n_right) = ((PBOOL false, PARRAY n_array))',
            ]
        checks += [
            'S_error_budget = $drive_steps(S_bridge, 1)', 'S_error_budget.COMPLETION = BUDGET',
            'S_error = S_error_budget[.COMPLETION = NORMAL]', f'${family}_both_frontier(S_error, 10)',
            'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*', 'S_error.RESULT = KNOWN PNULL',
            'n_error = |S_bridge.OBJECTS|', 'S_error.OBJECTS[n_error] = THROWABLE pthrowable',
            'S_error.OBJECTS = S_bridge.OBJECTS ++ [THROWABLE pthrowable]',
            'pthrowable.KIND = ' + json.dumps(kind), 'pthrowable.ORIGIN = (pintegeroperation.SITE)',
            '$throwable_field(S_error, n_error, "line") = PINT 25',
            '$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii(' + json.dumps(message) + '))',
            '$throwable_previous_id(S_error, n_error) = eps', '$throwable_live(S_error, n_error)',
            '$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]',
            '$heap_owners($heap_prune($heap_graph(S_error)), HOBJECT n_error) = 1',
            'S_error.STORE = S_bridge.STORE', 'S_error.ENV = S_bridge.ENV',
            'S_error.REFCELLS = S_bridge.REFCELLS', 'S_error.EVENTS = S_bridge.EVENTS',
            'S_error.STRINGDATA = S_bridge.STRINGDATA', 'S_error.ARRAYS[0:|S_bridge.ARRAYS|] = S_bridge.ARRAYS',
            '$heap_owners($heap_prune($heap_graph(S_error)), HCELL n_target) = 2',
            '$heap_owners($heap_prune($heap_graph(S_error)), HCELL n_right) = 1',
            '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
            'S_done = $drive_steps(S_error, 4000)',
            '$lookup(S_done.ENV, $ptascii("left")) = (n_target)',
            'S_done.STORE[n_target] = DEFINED (PINT 7)', 'S_done.STORE[n_v] = DEFINED (PINT 100)',
            'S_done.STORE[n_right] = DEFINED (' + right_value + ')', 'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        ]
        if mode == 'array':
            checks += [
                'S_error.ARRAYS[n_array] = parray_right', 'S_done.ARRAYS[n_array] = parray_right',
                '$heap_owners($heap_prune($heap_graph(S_error)), HARRAY n_array) = 2',
                '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_array) = 2',
            ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("alias")) = (n_target)',
        '$single_left_review_diagnostics(S_done.EVENTS, "Deprecated") = 1',
        '$single_left_review_diagnostics(S_done.EVENTS, "Warning") = 0',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_plan, 5000) = S_done', '$drive_steps(S, 5000) = S_done',
        '$drive_steps(S_return, 5000) = S_done', '$drive_steps(S_bridge, 5000) = S_done',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path, required=True)
    args, _ = parser.parse_known_args()
    watched = [Path(__file__), Path(shared.__file__), Path(cases.__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    shared.cases, shared.CASES, shared.conditions = cases, tuple(cases.CASES), conditions
    shared.HELPERS += REVIEW_HELPERS
    passed = shared.main()
    assert before == {str(path): digest(path) for path in watched}
    report = json.loads((args.output / 'report.json').read_bytes())
    report['review_inputs'] = before
    report['review_scope'] = 'Initial PINT3 selects a genuine single-LEFT warning and refuses BOTH stage0; actual returned single1 changes only TODO to BOTH1, then NULL modulo zero/no store, negative-float XOR/default RHS reference and detached owners3 to2, or live bool>>array TypeError with pool+cell owners2; native outputs and whole/budget equality'
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
