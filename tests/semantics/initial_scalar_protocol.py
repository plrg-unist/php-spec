#!/usr/bin/env python3
"""Reached scalar RHS entry, LEFT-first dispatch and delayed numeric storage."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import initial_scalar_cases as cases
import arithmetic_warning_protocol as shared
import leading_string_protocol as prior

CASES = ('initial-scalar-mod-repaired-carrier', 'initial-scalar-and-integral-entry')
HELPERS = prior.HELPERS


def conditions(name, program, path, stdout):
    carrier = name == CASES[0]
    family, tag, op, initial, produced, result = (
        ('modassign', 'MOD_ASSIGN_BOTH_LEFT', 'MODULO', 'PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("bad5"))', 'PFLOAT 4617878467915022336', '2') if carrier else
        ('bitassign', 'BIT_ASSIGN_BOTH_LEFT', 'BITAND', 'PFLOAT 4621819117588971520', 'PFLOAT 4617315517961601024', '4')
    )
    left = lambda stage: f'{tag} pintegeroperation n_target n_right n_bits_left i_left {stage}'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', f'S_plan_found = ${family}_both_seek(S_initial, 0, 4000)',
        r'S_plan_found.COMPLETION = NORMAL \/ S_plan_found.COMPLETION = BUDGET',
        'S_plan = S_plan_found[.COMPLETION = NORMAL]', f'${family}_both_frontier(S_plan, 0)',
        f'${family}_both_warning_plan(S_plan) = (' + left(0) + ')', f'${family}_warning_plan(S_plan) = eps',
        'S_capture_budget = $drive_steps(S_plan, 1)', 'S_capture_budget.COMPLETION = BUDGET',
        'S = S_capture_budget[.COMPLETION = NORMAL]', f'${family}_both_frontier(S, 1)',
        'S.TODO = (' + left(0) + ') :: ptask_tail*', 'n_bits_left = 4623226492472524800', 'i_left = 12',
        'pintegeroperation.OP = ' + op, '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23', 'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("left"))', 'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))',
        '$lookup(S.ENV, $ptascii("left")) = (n_target)', '$lookup(S.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S.ENV, $ptascii("v")) = (n_v)', '$lookup(S.ENV, $ptascii("calls")) = (n_calls)',
        'S.STORE[n_target] = DEFINED (PFLOAT n_bits_left)', 'S.STORE[n_right] = DEFINED (' + initial + ')',
        'S.STORE[n_v] = DEFINED (PINT 100)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        '~(n_target <- S.REFCELLS)', '~(n_right <- S.REFCELLS)',
        '$bothassign_initial_right_valid(S, ' + initial + ')', '$modassign_both_snapshot(S, pintegeroperation, n_target, n_right, n_bits_left)',
        '$call_task_valid(S, ' + left(0) + ')', '$task_nodes(' + left(0) + ') = eps',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    ]
    if carrier:
        checks += [
            'S.STRINGDATA[n_string] = $ptascii("bad5")', '$string_carrier_valid(S, ' + initial + ')',
            '$string_long($ptascii("bad5")) = STRINTERROR',
        ]
        for value in ['PNULL', 'PBOOL false', 'PBOOL true', 'PFLOAT 4617315517961601024',
                      'PFLOAT 4623226492472524800', 'PFLOAT 9223372036854775808',
                      'PSTRING ($ptascii("bad5"))', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("7tail"))']:
            checks += ['$bothassign_initial_right_valid(S, ' + value + ')']
        for value in ['PUNDEFINED', 'PINT 3', 'PARRAY 0', 'POBJECT 0', 'PFLOAT 9221120237041090560',
                      'PFLOAT 9218868437227405312', 'PFLOAT 4890909195324358656', 'PFLOAT 18446744073709551616',
                      'PSTRING ([256])', 'PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("bad5"))',
                      'PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("other"))']:
            checks += ['~$bothassign_initial_right_valid(S, ' + value + ')']
        checks += [
            '~$modassign_both_snapshot(S[.REFCELLS = S.REFCELLS ++ [n_right]], pintegeroperation, n_target, n_right, n_bits_left)',
            '~$modassign_both_snapshot(S[.ALLOCATIONS = eps], pintegeroperation, n_target, n_right, n_bits_left)',
            '~$modassign_both_snapshot(S[.ENV = eps], pintegeroperation, n_target, n_right, n_bits_left)',
            '~$call_task_valid(S, ' + left(0).replace('pintegeroperation', 'pintegeroperation[.SWAPPED = true]') + ')',
            '~$call_task_valid(S, ' + left(0).replace('pintegeroperation', 'pintegeroperation[.LINE = 24]') + ')',
        ]
    checks += [
        'S_dispatch_budget = $drive_steps(S, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]', f'${family}_both_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
        'perrorcall_first.RESUME = ' + left(1), 'perrorcall_first.TARGET = eps',
        'perrorcall_first.LEVEL = 8192', 'perrorcall_first.LINE = 25',
        'perrorcall_first.MESSAGE = $ptascii("Implicit conversion from float 12.5 to int loses precision")',
        '$error_call_valid(S_dispatch, perrorcall_first)',
        f'S_entered_found = ${family}_both_seek(S_dispatch, 3, 4000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', f'${family}_both_entered(S_entered.FRAMES, 0)',
        f'S_return_found = ${family}_both_seek(S_entered, 4, 4000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', f'${family}_both_frontier(S_return, 4)',
        'S_return.TODO = (' + left(1) + ') :: ptask_tail*', 'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
        'S_return.STORE[n_target] = DEFINED (PINT 99)', 'S_return.STORE[n_right] = DEFINED (' + produced + ')',
        'S_return.STORE[n_calls] = DEFINED (PINT 1)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
        '$lookup(S_return.ENV, $ptascii("alias")) = (n_target)', 'n_target <- S_return.REFCELLS',
        '$call_task_valid(S_return, ' + left(1) + ')', '~$call_task_valid(S_return, ' + left(0) + ')',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_target) = 2',
        '$modassign_both_deprecations(S_return.EVENTS) = 0',
    ]
    if carrier:
        right = lambda stage: f'MOD_ASSIGN_BOTH_RIGHT pintegeroperation n_target n_right n_bits_left i_left 4617878467915022336 5 {stage}'
        checks += [
            'S_return.STRINGDATA[0:|S.STRINGDATA|] = S.STRINGDATA',
            '$modassign_both_right_snapshot(S_return, pintegeroperation, n_target, n_right) = ((4617878467915022336, 5))',
            'S_right_budget = $drive_steps(S_return, 1)', 'S_right_budget.COMPLETION = BUDGET',
            'S_right = S_right_budget[.COMPLETION = NORMAL]', 'S_right.TODO = (' + right(0) + ') :: ptask_tail*',
            'S_second_budget = $drive_steps(S_right, 1)', 'S_second_budget.COMPLETION = BUDGET',
            'S_second = S_second_budget[.COMPLETION = NORMAL]', 'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
            'perrorcall_second.RESUME = ' + right(1), 'perrorcall_second.TARGET = eps',
            'perrorcall_second.LEVEL = 8192', 'perrorcall_second.LINE = 25', '$error_call_valid(S_second, perrorcall_second)',
            'S_second_entered_found = $modassign_both_seek(S_second, 7, 4000)',
            r'S_second_entered_found.COMPLETION = NORMAL \/ S_second_entered_found.COMPLETION = BUDGET',
            'S_second_entered = S_second_entered_found[.COMPLETION = NORMAL]', '$modassign_both_entered(S_second_entered.FRAMES, 1)',
            'S_late_found = $modassign_both_seek(S_second_entered, 8, 4000)',
            r'S_late_found.COMPLETION = NORMAL \/ S_late_found.COMPLETION = BUDGET',
            'S_late = S_late_found[.COMPLETION = NORMAL]', 'S_late.TODO = (' + right(1) + ') :: ptask_tail*',
            'S_late.STORE[n_target] = DEFINED (PINT 88)', 'S_late.STORE[n_right] = DEFINED (PINT 7)',
            'S_late.STORE[n_calls] = DEFINED (PINT 2)',
        ]
    else:
        checks += ['$modassign_both_integral_snapshot(S_return, pintegeroperation, n_target, n_right) = ((4617315517961601024, 5))', 'S_late = S_return']
    checks += [
        '$powerassign_warning_ready(S_late, pintegeroperation, n_target)',
        'S_commit_budget = $drive_steps(S_late, 1)', 'S_commit_budget.COMPLETION = BUDGET',
        'S_commit = S_commit_budget[.COMPLETION = NORMAL]', f'${family}_both_frontier(S_commit, 9)',
        'S_commit.TODO = ptask_tail*', 'S_commit.RESULT = KNOWN (PINT ' + result + ')',
        '$lookup(S_commit.ENV, $ptascii("left")) = (n_new)', 'n_new = |S_late.STORE|',
        'S_commit.CELL = n_new', 'S_commit.LOCATION = ROOT n_new', '~(n_new <- S_commit.REFCELLS)',
        '$lookup(S_commit.ENV, $ptascii("alias")) = (n_target)',
        'S_commit.STORE = S_late.STORE ++ [DEFINED (PINT ' + result + ')]',
        'S_commit.ALLOCATIONS = S_late.ALLOCATIONS ++ [HCELL n_new]', 'S_commit.REFCELLS = S_late.REFCELLS',
        'S_commit.EVENTS = S_late.EVENTS', 'S_commit.STRINGDATA = S_late.STRINGDATA', 'S_commit.ARRAYS = S_late.ARRAYS',
        '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_new) = 1',
        '$call_descriptors_valid(S_commit)', '$heap_valid($heap_graph(S_commit))',
        'S_done = $drive_steps(S_commit, 4000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_new)', '$lookup(S_done.ENV, $ptascii("alias")) = (n_target)',
        'S_done.STORE[n_new] = DEFINED (PINT 7)', 'S_done.STORE[n_target] = DEFINED (PINT ' + ('88' if carrier else '99') + ')',
        'S_done.STORE[n_v] = DEFINED (PINT ' + result + ')',
        '$modassign_both_deprecations(S_done.EVENTS) = 0', '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_plan, 5000) = S_done', '$drive_steps(S, 5000) = S_done',
        '$drive_steps(S_dispatch, 5000) = S_done', '$drive_steps(S_entered, 5000) = S_done', '$drive_steps(S_return, 5000) = S_done',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path, required=True)
    args, _ = parser.parse_known_args()
    watched = [Path(__file__), Path(cases.__file__), Path(prior.__file__), Path(shared.__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    shared.cases, shared.CASES, shared.HELPERS, shared.conditions = cases, CASES, HELPERS, conditions
    passed = shared.main()
    assert before == {str(path): digest(path) for path in watched}
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
