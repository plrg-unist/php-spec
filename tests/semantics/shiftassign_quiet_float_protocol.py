#!/usr/bin/env python3
"""Reached quiet integral-float counts after the first shift warning."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import shiftassign_quiet_float_cases as cases
import shiftassign_both_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS


def conditions(name, program, path, stdout):
    thrown = name.endswith('-handler-throw')
    operation = 'SHIFTLEFT' if '-left-' in name else 'SHIFTRIGHT'
    result = '(-48)' if operation == 'SHIFTLEFT' else '(-3)'
    left = lambda stage: 'SHIFT_ASSIGN_BOTH_LEFT pintegeroperation n_target n_right n_bits_left i_left ' + str(stage)
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $shiftassign_both_seek(S_initial, 1, 3000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$shiftassign_both_frontier(S, 1)',
        'S.TODO = (' + left(0) + ') :: ptask_tail*',
        'n_bits_left = 13846598529327300608', 'i_left = (-12)',
        'pintegeroperation.OP = ' + operation, '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 24',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("left"))',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))',
        '$lookup(S.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S.ENV, $ptascii("v")) = (n_v)', '$lookup(S.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)',
        'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        'S.STORE[n_target] = DEFINED (PFLOAT n_bits_left)',
        'S.STORE[n_right] = DEFINED (PFLOAT 4620974692658839552)',
        'S.STORE[n_calls] = DEFINED (PINT 0)', 'S.STORE[n_v] = DEFINED (PINT 100)',
        '~(n_target <- S.REFCELLS)', '~(n_right <- S.REFCELLS)',
        'S.RESULT = KNOWN PNULL', 'S.BASE = BASE_VALUE (KNOWN PNULL)', 'S.LOCATION = ROOT n_target',
        '$call_task_valid(S, ' + left(0) + ')', '$task_nodes(' + left(0) + ') = eps',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_right) = 1',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'S_dispatch_budget = $drive_steps(S, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]', '$shiftassign_both_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + left(1), 'perrorcall.TARGET = eps',
        'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = $ptascii("Implicit conversion from float -12.5 to int loses precision")',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'S_entered_found = $shiftassign_both_seek(S_dispatch, 3, 3000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', '$shiftassign_both_frontier(S_entered, 3)',
        '$shiftassign_both_entered(S_entered.FRAMES, 0)',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if thrown:
        checks += [
            'S_throw_found = $shiftassign_both_seek(S_entered, 10, 3000)',
            r'S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET',
            'S_throw = S_throw_found[.COMPLETION = NORMAL]', '$shiftassign_both_frontier(S_throw, 10)',
            'S_throw.TODO = (THROW_SEARCH n_second) :: ptask_throw*',
            'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps', '~$shiftassign_both_tasks(S_throw.TODO)',
            '$lookup(S_throw.ENV, $ptascii("left")) = (n_target)',
            '$lookup(S_throw.ENV, $ptascii("alias")) = (n_target)',
            'n_target <- S_throw.REFCELLS', 'S_throw.STORE[n_target] = DEFINED (PINT 99)',
            'S_throw.STORE[n_right] = DEFINED (PFLOAT 4611686018427387904)',
            'S_throw.STORE[n_v] = DEFINED (PINT 100)', 'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
            '$throwable_live(S_throw, n_second)', '$throwable_previous_id(S_throw, n_second) = eps',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_target) = 2',
            'S_throw.ERRORHANDLER = S.ERRORHANDLER',
            '$shiftassign_both_deprecations(S_throw.EVENTS) = 0',
            '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
            'S_done = $drive_steps(S_throw, 3000)', '$drive_steps(S_entered, 3000) = S_done',
            '$lookup(S_done.ENV, $ptascii("left")) = (n_target)',
            '$lookup(S_done.ENV, $ptascii("alias")) = (n_target)',
            'S_done.STORE[n_target] = DEFINED (PINT 7)', 'S_done.STORE[n_v] = DEFINED (PINT 100)',
        ]
    else:
        checks += [
            'S_return_found = $shiftassign_both_seek(S_entered, 4, 3000)',
            r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
            'S_return = S_return_found[.COMPLETION = NORMAL]', '$shiftassign_both_frontier(S_return, 4)',
            'S_return.TODO = (' + left(1) + ') :: ptask_tail*',
            'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
            'S_return.STORE[n_target] = DEFINED (PINT 99)',
            'S_return.STORE[n_right] = DEFINED (PFLOAT 4611686018427387904)',
            'S_return.STORE[n_v] = DEFINED (PINT 100)', 'S_return.STORE[n_calls] = DEFINED (PINT 1)',
            '$lookup(S_return.ENV, $ptascii("alias")) = (n_target)', 'n_target <- S_return.REFCELLS',
            '$call_task_valid(S_return, ' + left(1) + ')', '~$call_task_valid(S_return, ' + left(0) + ')',
            'S_return.ERRORHANDLER = S.ERRORHANDLER',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_target) = 2',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
            '$float_long(4611686018427387904, true) = (2, eps)',
            '$modassign_both_integral_snapshot(S_return, pintegeroperation, n_target, n_right) = ((4611686018427387904, 2))',
            '$modassign_warning_ready(S_return, pintegeroperation, n_target, n_right) = eps',
            '$modassign_both_right_snapshot(S_return, pintegeroperation, n_target, n_right) = eps',
            '$modassign_both_integral_snapshot(S_return[.STORE[n_right] = DEFINED (PINT 2)], pintegeroperation, n_target, n_right) = eps',
            '$modassign_both_integral_snapshot(S_return[.STORE[n_right] = DEFINED (PFLOAT 4612811918334230528)], pintegeroperation, n_target, n_right) = eps',
            '$modassign_both_integral_snapshot(S_return[.STORE[n_right] = DEFINED (PFLOAT 9218868437227405312)], pintegeroperation, n_target, n_right) = eps',
            '$modassign_both_integral_snapshot(S_return[.STORE[n_right] = DEFINED (PFLOAT 4890909195324358656)], pintegeroperation, n_target, n_right) = eps',
            '$modassign_both_integral_snapshot(S_return[.STORE[n_right] = DEFINED PNULL], pintegeroperation, n_target, n_right) = eps',
            '$modassign_both_integral_snapshot(S_return[.REFCELLS = S_return.REFCELLS ++ [n_right]], pintegeroperation, n_target, n_right) = eps',
            '$modassign_both_integral_snapshot(S_return[.ALLOCATIONS = eps], pintegeroperation, n_target, n_right) = eps',
            '$modassign_both_integral_snapshot(S_return[.ENV = eps][.GLOBALTABLE = eps], pintegeroperation, n_target, n_right) = eps',
            '$modassign_both_integral_snapshot(S_return, pintegeroperation, n_v, n_right) = eps',
            '$modassign_both_integral_snapshot(S_return, pintegeroperation, n_target, n_v) = eps',
            '$modassign_both_integral_snapshot(S_return[.PROPREFS = [{CELL n_target, SOURCES eps}]], pintegeroperation, n_target, n_right) = eps',
            '$modassign_both_integral_snapshot(S_return[.STORE[n_target] = DEFINED (POBJECT n_second)], pintegeroperation, n_target, n_right) = eps',
            '$integer_binary(pintegeroperation.OP, i_left, 2) = IRESULT ' + result,
            'S_commit_budget = $drive_steps(S_return, 1)', 'S_commit_budget.COMPLETION = BUDGET',
            'S_commit = S_commit_budget[.COMPLETION = NORMAL]', '$shiftassign_both_frontier(S_commit, 9)',
            'S_commit.TODO = ptask_tail*', 'S_commit.RESULT = KNOWN (PINT ' + result + ')',
            '~$shiftassign_both_frontier(S_commit, 5)', '~$shiftassign_both_frontier(S_commit, 11)',
            '$lookup(S_commit.ENV, $ptascii("left")) = (n_new)', 'n_new = |S_return.STORE|',
            'S_commit.CELL = n_new', 'S_commit.LOCATION = ROOT n_new', '~(n_new <- S_commit.REFCELLS)',
            '$lookup(S_commit.ENV, $ptascii("alias")) = (n_target)',
            'S_commit.STORE = S_return.STORE ++ [DEFINED (PINT ' + result + ')]',
            'S_commit.ALLOCATIONS = S_return.ALLOCATIONS ++ [HCELL n_new]',
            'S_commit.STORE[n_target] = DEFINED (PINT 99)',
            'S_commit.STORE[n_v] = DEFINED (PINT 100)',
            'S_commit.EVENTS = S_return.EVENTS',
            '$shiftassign_both_deprecations(S_commit.EVENTS) = 0',
            '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_target) = 1',
            '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_new) = 1',
            '$call_descriptors_valid(S_commit)', '$heap_valid($heap_graph(S_commit))',
            'S_done = $drive_steps(S_commit, 3000)', '$drive_steps(S_return, 3000) = S_done',
            'S_done.STORE[n_new] = DEFINED (PINT 7)',
            'S_done.STORE[n_target] = DEFINED (PINT 99)', 'S_done.STORE[n_v] = DEFINED (PINT ' + result + ')',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_right] = DEFINED (PFLOAT 4611686018427387904)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)', '$shiftassign_both_deprecations(S_done.EVENTS) = 0',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]', '$drive_steps(S, 3000) = S_done',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path, required=True)
    args, _ = parser.parse_known_args()
    watched = [Path(__file__), Path(cases.__file__), Path(shared.__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    shared.cases, shared.CASES, shared.HELPERS, shared.conditions = cases, CASES, HELPERS, conditions
    passed = shared.main()
    assert before == {str(path): digest(path) for path in watched}
    report = json.loads((args.output / 'report.json').read_bytes())
    report['quiet_float_inputs'] = before
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
