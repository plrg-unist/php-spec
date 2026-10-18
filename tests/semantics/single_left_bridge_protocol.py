#!/usr/bin/env python3
"""Authenticate single-LEFT handoff into the existing delayed conversion suffix."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import single_left_bridge_cases as cases
import arithmetic_warning_protocol as shared
import leading_string_protocol as prior

CASES = ('single-left-mod-leading-carrier', 'single-left-right-float', 'single-left-and-integral')
HELPERS = prior.HELPERS + r'''
dec $single_left_bridge_marker(ptask, nat) : bool
def $single_left_bridge_marker(MOD_ASSIGN_WARNING pintegeroperation n_target n_right n_bits i_left n_stage, n_stage) = true
def $single_left_bridge_marker(SHIFT_ASSIGN_WARNING pintegeroperation n_target n_right n_bits i_left n_stage, n_stage) = true
def $single_left_bridge_marker(BIT_ASSIGN_WARNING pintegeroperation n_target n_right n_bits i_left n_stage, n_stage) = true
def $single_left_bridge_marker(ptask, n_stage) = false -- otherwise
dec $single_left_bridge_task(ptask) : bool
def $single_left_bridge_task(ptask) = true -- if $single_left_bridge_marker(ptask, 0) \/ $single_left_bridge_marker(ptask, 1)
def $single_left_bridge_task(ERROR_HANDLER_INVOKE perrorcall) = $single_left_bridge_task(perrorcall.RESUME)
def $single_left_bridge_task(ERROR_HANDLER_RESULT perrorcall) = $single_left_bridge_task(perrorcall.RESUME)
def $single_left_bridge_task(ERROR_HANDLER_CLEAN perrorcall) = $single_left_bridge_task(perrorcall.RESUME)
def $single_left_bridge_task(ptask) = $leading_string_task(ptask) -- otherwise
dec $single_left_bridge_tasks(ptask*) : bool
def $single_left_bridge_tasks(eps) = false
def $single_left_bridge_tasks(ptask :: ptask_tail*) = ($single_left_bridge_task(ptask) \/ $single_left_bridge_tasks(ptask_tail*))
dec $single_left_bridge_frame(pframe) : bool
def $single_left_bridge_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.TARGET =/= eps
  -- if $single_left_bridge_marker(perrorcall.RESUME, 1)
def $single_left_bridge_frame(pframe) = false -- otherwise
dec $single_left_bridge_entered(pframe*) : bool
def $single_left_bridge_entered(eps) = false
def $single_left_bridge_entered(pframe :: pframe_tail*) = ($single_left_bridge_frame(pframe) \/ $single_left_bridge_entered(pframe_tail*))
dec $single_left_bridge_frontier(pstate, nat) : bool
def $single_left_bridge_frontier(S, 0) = ($modassign_warning_plan(S) =/= eps \/ $shiftassign_warning_plan(S) =/= eps \/ $bitassign_warning_plan(S) =/= eps)
def $single_left_bridge_frontier(S, 1) = true
  -- if S.TODO = ptask :: ptask_tail*
  -- if $single_left_bridge_marker(ptask, 0)
def $single_left_bridge_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.TARGET = eps
  -- if $single_left_bridge_marker(perrorcall.RESUME, 1)
def $single_left_bridge_frontier(S, 3) = (S.CURRENT =/= eps /\ $single_left_bridge_entered(S.FRAMES))
def $single_left_bridge_frontier(S, 4) = true
  -- if S.TODO = ptask :: ptask_tail*
  -- if $single_left_bridge_marker(ptask, 1)
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $single_left_bridge_frontier(S, 5) = ($modassign_both_frontier(S, 4) \/ $shiftassign_both_frontier(S, 4) \/ $bitassign_both_frontier(S, 4))
def $single_left_bridge_frontier(S, n_stage) = false -- otherwise
dec $single_left_bridge_seek(pstate, nat, nat) : pstate
def $single_left_bridge_seek(S, n_stage, n) = S -- if $single_left_bridge_frontier(S, n_stage)
def $single_left_bridge_seek(S, n_stage, n) = S
  -- if ~$single_left_bridge_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $single_left_bridge_seek(S, n_stage, n) = S
  -- if ~$single_left_bridge_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $single_left_bridge_seek(S, n_stage, n) = $single_left_bridge_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$single_left_bridge_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    family, single_tag, both_tag, operation, rhs, result, live_left, live_right, calls = {
        CASES[0]: ('modassign', 'MOD_ASSIGN_WARNING', 'MOD_ASSIGN_BOTH_LEFT', 'MODULO', 'PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("05tail"))', '2', '88', 'PINT 7', 2),
        CASES[1]: ('shiftassign', 'SHIFT_ASSIGN_WARNING', 'SHIFT_ASSIGN_BOTH_LEFT', 'SHIFTRIGHT', 'PFLOAT 4612811918334230528', '3', '88', 'PINT 1', 2),
        CASES[2]: ('bitassign', 'BIT_ASSIGN_WARNING', 'BIT_ASSIGN_BOTH_LEFT', 'BITAND', 'PFLOAT 4617315517961601024', '4', '99', 'PFLOAT 4617315517961601024', 1),
    }[name]
    single = lambda stage: f'{single_tag} pintegeroperation n_target n_right n_bits_left i_left {stage}'
    both = lambda stage: f'{both_tag} pintegeroperation n_target n_right n_bits_left i_left {stage}'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_plan_found = $single_left_bridge_seek(S_initial, 0, 4000)',
        r'S_plan_found.COMPLETION = NORMAL \/ S_plan_found.COMPLETION = BUDGET',
        'S_plan = S_plan_found[.COMPLETION = NORMAL]', '$single_left_bridge_frontier(S_plan, 0)',
        f'${family}_warning_plan(S_plan) = (' + single(0) + ')', f'${family}_both_warning_plan(S_plan) = eps',
        'S_marker_budget = $drive_steps(S_plan, 1)', 'S_marker_budget.COMPLETION = BUDGET',
        'S = S_marker_budget[.COMPLETION = NORMAL]', '$single_left_bridge_frontier(S, 1)',
        'S.TODO = (' + single(0) + ') :: ptask_tail*', 'n_bits_left = 4623226492472524800', 'i_left = 12',
        'pintegeroperation.OP = ' + operation, '~pintegeroperation.SWAPPED',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23', 'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LINE = 25', 'S.ORIGIN = (pintegeroperation.SITE)',
        '$lookup(S.ENV, $ptascii("left")) = (n_target)', '$lookup(S.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S.ENV, $ptascii("v")) = (n_v)', '$lookup(S.ENV, $ptascii("calls")) = (n_calls)',
        'S.STORE[n_target] = DEFINED (PFLOAT n_bits_left)', 'S.STORE[n_right] = DEFINED (PINT 3)',
        'S.STORE[n_v] = DEFINED (PINT 100)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        '~(n_target <- S.REFCELLS)', '~(n_right <- S.REFCELLS)',
        '$call_task_valid(S, ' + single(0) + ')', '~$call_task_valid(S, ' + both(0) + ')',
        '$task_nodes(' + single(0) + ') = eps', '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    ]
    if name == CASES[0]:
        checks += [
            'S_first_budget = $drive_steps(S, 1)', 'S_first_budget.COMPLETION = BUDGET',
            'S_first = S_first_budget[.COMPLETION = NORMAL]', '$single_left_bridge_frontier(S_first, 2)',
            'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
            'perrorcall_first.RESUME = ' + single(1), 'perrorcall_first.TARGET = eps',
            'perrorcall_first.LEVEL = 8192', 'perrorcall_first.LINE = 25', '$error_call_valid(S_first, perrorcall_first)',
            'S_first_entered_found = $single_left_bridge_seek(S_first, 3, 4000)',
            r'S_first_entered_found.COMPLETION = NORMAL \/ S_first_entered_found.COMPLETION = BUDGET',
            'S_first_entered = S_first_entered_found[.COMPLETION = NORMAL]', '$single_left_bridge_entered(S_first_entered.FRAMES)',
        ]
    checks += [
        'S_return_found = $single_left_bridge_seek(S, 4, 4000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', '$single_left_bridge_frontier(S_return, 4)',
        'S_return.TODO = (' + single(1) + ') :: ptask_tail*', 'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
        '$lookup(S_return.ENV, $ptascii("left")) = (n_target)', '$lookup(S_return.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_return.ENV, $ptascii("alias")) = (n_target)',
        'S_return.STORE[n_target] = DEFINED (PINT 99)', 'S_return.STORE[n_right] = DEFINED (' + rhs + ')',
        'S_return.STORE[n_v] = DEFINED (PINT 100)', 'S_return.STORE[n_calls] = DEFINED (PINT 1)',
        'n_target <- S_return.REFCELLS', '~(n_right <- S_return.REFCELLS)',
        '$call_task_valid(S_return, ' + single(1) + ')', '~$call_task_valid(S_return, ' + single(0) + ')',
        '$modassign_warning_ready(S_return, pintegeroperation, n_target, n_right) = eps',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_target) = 2',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 1',
        '$modassign_both_deprecations(S_return.EVENTS) = 0', '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'S_bridge_budget = $drive_steps(S_return, 1)', 'S_bridge_budget.COMPLETION = BUDGET',
        'S_bridge = S_bridge_budget[.COMPLETION = NORMAL]', '$single_left_bridge_frontier(S_bridge, 5)',
        'S_bridge = S_return[.TODO = (' + both(1) + ') :: ptask_tail*]',
        '$call_task_valid(S_bridge, ' + both(1) + ')', '~$call_task_valid(S_bridge, ' + both(0) + ')',
        '$task_nodes(' + both(1) + ') = eps', '$call_descriptors_valid(S_bridge)', '$heap_valid($heap_graph(S_bridge))',
    ]
    if name == CASES[0]:
        pending = lambda stage: f'BOTH_ASSIGN_STRING_WARNING pintegeroperation n_target n_right n_bits_left i_left pvalue_saved 5 {stage}'
        checks += [
            'S_bridge.STORE[n_right] = DEFINED pvalue_saved', 'pvalue_saved = ' + rhs,
            'S_bridge.STRINGDATA[n_string] = $ptascii("05tail")', '$string_carrier_valid(S_bridge, pvalue_saved)',
            '$bothassign_leading_string_snapshot(S_bridge, pintegeroperation, n_target, n_right) = ((pvalue_saved, 5))',
            'S_right_budget = $drive_steps(S_bridge, 1)', 'S_right_budget.COMPLETION = BUDGET',
            'S_right = S_right_budget[.COMPLETION = NORMAL]', '$leading_string_frontier(S_right, 5)',
            'S_right.TODO = (' + pending(0) + ') :: ptask_tail*', '$call_task_valid(S_right, ' + pending(0) + ')',
            'S_second_budget = $drive_steps(S_right, 1)', 'S_second_budget.COMPLETION = BUDGET',
            'S_second = S_second_budget[.COMPLETION = NORMAL]', '$leading_string_frontier(S_second, 6)',
            'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
            'perrorcall_second.RESUME = ' + pending(1), 'perrorcall_second.TARGET = eps',
            'perrorcall_second.LEVEL = 2', 'perrorcall_second.LINE = 25', '$error_call_valid(S_second, perrorcall_second)',
            'S_entered_found = $leading_string_seek(S_second, 7, 4000)',
            r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
            'S_entered = S_entered_found[.COMPLETION = NORMAL]', '$leading_string_entered(S_entered.FRAMES, 1)',
            'S_late_found = $leading_string_seek(S_entered, 8, 4000)',
            r'S_late_found.COMPLETION = NORMAL \/ S_late_found.COMPLETION = BUDGET',
            'S_late = S_late_found[.COMPLETION = NORMAL]', '$leading_string_frontier(S_late, 8)',
            'S_late.TODO = (' + pending(1) + ') :: ptask_tail*', '$call_task_valid(S_late, ' + pending(1) + ')',
            '~$call_task_valid(S_late, ' + pending(0) + ')', '$string_carrier_valid(S_late, pvalue_saved)',
            'S_late.STRINGDATA[0:|S_bridge.STRINGDATA|] = S_bridge.STRINGDATA',
        ]
    elif name == CASES[1]:
        pending = lambda stage: f'SHIFT_ASSIGN_BOTH_RIGHT pintegeroperation n_target n_right n_bits_left i_left n_bits_right i_right {stage}'
        checks += [
            '$modassign_both_right_snapshot(S_bridge, pintegeroperation, n_target, n_right) = ((4612811918334230528, 2))',
            'S_right_budget = $drive_steps(S_bridge, 1)', 'S_right_budget.COMPLETION = BUDGET',
            'S_right = S_right_budget[.COMPLETION = NORMAL]', '$shiftassign_both_frontier(S_right, 5)',
            'S_right.TODO = (' + pending(0) + ') :: ptask_tail*', 'n_bits_right = 4612811918334230528', 'i_right = 2',
            '$call_task_valid(S_right, ' + pending(0) + ')',
            'S_second_budget = $drive_steps(S_right, 1)', 'S_second_budget.COMPLETION = BUDGET',
            'S_second = S_second_budget[.COMPLETION = NORMAL]', '$shiftassign_both_frontier(S_second, 6)',
            'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
            'perrorcall_second.RESUME = ' + pending(1), 'perrorcall_second.TARGET = eps',
            'perrorcall_second.LEVEL = 8192', 'perrorcall_second.LINE = 25', '$error_call_valid(S_second, perrorcall_second)',
            'S_entered_found = $shiftassign_both_seek(S_second, 7, 4000)',
            r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
            'S_entered = S_entered_found[.COMPLETION = NORMAL]', '$shiftassign_both_entered(S_entered.FRAMES, 1)',
            'S_late_found = $shiftassign_both_seek(S_entered, 8, 4000)',
            r'S_late_found.COMPLETION = NORMAL \/ S_late_found.COMPLETION = BUDGET',
            'S_late = S_late_found[.COMPLETION = NORMAL]', '$shiftassign_both_frontier(S_late, 8)',
            'S_late.TODO = (' + pending(1) + ') :: ptask_tail*', '$call_task_valid(S_late, ' + pending(1) + ')',
            '~$call_task_valid(S_late, ' + pending(0) + ')',
        ]
    else:
        checks += ['$modassign_both_integral_snapshot(S_bridge, pintegeroperation, n_target, n_right) = ((4617315517961601024, 5))', 'S_late = S_bridge']
    checks += [
        'S_late.STORE[n_target] = DEFINED (PINT ' + live_left + ')',
        'S_late.STORE[n_right] = DEFINED (' + live_right + ')', 'S_late.STORE[n_v] = DEFINED (PINT 100)',
        'S_late.STORE[n_calls] = DEFINED (PINT ' + str(calls) + ')',
        '$lookup(S_late.ENV, $ptascii("alias")) = (n_target)',
        '$heap_owners($heap_prune($heap_graph(S_late)), HCELL n_target) = 2',
        '$powerassign_warning_ready(S_late, pintegeroperation, n_target)', '$modassign_both_deprecations(S_late.EVENTS) = 0',
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
        'S_done.STORE[n_new] = DEFINED (PINT 7)', 'S_done.STORE[n_target] = DEFINED (PINT ' + live_left + ')',
        'S_done.STORE[n_v] = DEFINED (PINT ' + result + ')', 'S_done.STORE[n_right] = DEFINED (' + live_right + ')',
        'S_done.STORE[n_calls] = DEFINED (PINT ' + str(calls) + ')',
        '$modassign_both_deprecations(S_done.EVENTS) = 0', '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]', '$drive_steps(S_plan, 5000) = S_done',
        '$drive_steps(S, 5000) = S_done', '$drive_steps(S_return, 5000) = S_done', '$drive_steps(S_bridge, 5000) = S_done',
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
    report = json.loads((args.output / 'report.json').read_bytes())
    report['single_left_bridge_inputs'] = before
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
