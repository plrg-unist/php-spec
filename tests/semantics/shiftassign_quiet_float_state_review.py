#!/usr/bin/env python3
"""Quiet negative and wide float counts preserve the cached LEFT and alias semantics."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import shiftassign_quiet_float_review_cases as cases
import shiftassign_quiet_float_protocol as shared

REVIEW_HELPERS = r"""
dec $shiftassign_quiet_float_review_deprecation(pevent) : nat
def $shiftassign_quiet_float_review_deprecation(DIAGNOSTIC "Deprecated" n* z) = 1
def $shiftassign_quiet_float_review_deprecation(pevent) = 0 -- otherwise
dec $shiftassign_quiet_float_review_deprecations(pevent*) : nat
def $shiftassign_quiet_float_review_deprecations(eps) = 0
def $shiftassign_quiet_float_review_deprecations(pevent :: pevent_tail*) = $($shiftassign_quiet_float_review_deprecation(pevent) + $shiftassign_quiet_float_review_deprecations(pevent_tail*))
"""


def conditions(name, program, path, stdout):
    wide = name.endswith("-wide-default")
    bits = "4634204016564240384" if wide else "13830554455654793216"
    count = "64" if wide else "(-1)"
    left = lambda stage: 'SHIFT_ASSIGN_BOTH_LEFT pintegeroperation n_target n_right n_bits_left i_left ' + str(stage)
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $shiftassign_both_seek(S_initial, 1, 4000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$shiftassign_both_frontier(S, 1)',
        'S.TODO = (' + left(0) + ') :: ptask_tail*',
        'n_bits_left = 13846598529327300608', 'i_left = (-12)',
        'pintegeroperation.OP = SHIFTRIGHT', '~pintegeroperation.SWAPPED',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("left"))',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))',
        'pintegeroperation.LINE = 25', 'S.ORIGIN = (pintegeroperation.SITE)',
        '$lookup(S.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S.ENV, $ptascii("calls")) = (n_calls)',
        'S.STORE[n_target] = DEFINED (PFLOAT n_bits_left)',
        'S.STORE[n_right] = DEFINED (PFLOAT 4620974692658839552)',
        'S.STORE[n_v] = DEFINED (PINT 100)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        '~(n_target <- S.REFCELLS)', '~(n_right <- S.REFCELLS)',
        'S.LOCATION = ROOT n_target', 'S.RESULT = KNOWN PNULL',
        'S.BASE = BASE_VALUE (KNOWN PNULL)',
        '$call_task_valid(S, ' + left(0) + ')',
        '~$call_task_valid(S, SHIFT_ASSIGN_BOTH_LEFT pintegeroperation n_target n_right 13847161479280721920 (-13) 0)',
        '$task_nodes(' + left(0) + ') = eps',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_right) = 1',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '$shiftassign_quiet_float_review_deprecations(S.EVENTS) = 0',
        'S_first_budget = $drive_steps(S, 1)', 'S_first_budget.COMPLETION = BUDGET',
        'S_first = S_first_budget[.COMPLETION = NORMAL]', '$shiftassign_both_frontier(S_first, 2)',
        'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
        'perrorcall_first.RESUME = ' + left(1), 'perrorcall_first.TARGET = eps',
        'perrorcall_first.LEVEL = 8192', 'perrorcall_first.LINE = 25',
        'perrorcall_first.MESSAGE = $ptascii("Implicit conversion from float -12.5 to int loses precision")',
        '$error_call_valid(S_first, perrorcall_first)',
        '$call_descriptors_valid(S_first)', '$heap_valid($heap_graph(S_first))',
        'S_left_found = $shiftassign_both_seek(S_first, 4, 4000)',
        r'S_left_found.COMPLETION = NORMAL \/ S_left_found.COMPLETION = BUDGET',
        'S_left = S_left_found[.COMPLETION = NORMAL]', '$shiftassign_both_frontier(S_left, 4)',
        'S_left.TODO = (' + left(1) + ') :: ptask_tail*',
        'S_left.CURRENT = eps', 'S_left.FRAMES = eps',
        '$lookup(S_left.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S_left.ENV, $ptascii("alias")) = (n_target)',
        '$lookup(S_left.ENV, $ptascii("right")) = (n_right)',
        'n_target <- S_left.REFCELLS', '~(n_right <- S_left.REFCELLS)',
        'S_left.STORE[n_target] = DEFINED (PINT 99)',
        'S_left.STORE[n_right] = DEFINED (PFLOAT ' + bits + ')',
        'S_left.STORE[n_v] = DEFINED (PINT 100)', 'S_left.STORE[n_calls] = DEFINED (PINT 1)',
        '$call_task_valid(S_left, ' + left(1) + ')',
        '~$call_task_valid(S_left, ' + left(0) + ')',
        'S_left.ERRORHANDLER = S.ERRORHANDLER',
        '$heap_owners($heap_prune($heap_graph(S_left)), HCELL n_target) = 2',
        '$shiftassign_quiet_float_review_deprecations(S_left.EVENTS) = 1',
        '$call_descriptors_valid(S_left)', '$heap_valid($heap_graph(S_left))',
        '(DIAGNOSTIC "Deprecated" ($ptascii("Implicit conversion from float -12.5 to int loses precision")) 25) <- S_left.EVENTS',
        '$float_long(' + bits + ', true) = (' + count + ', eps)',
        '$modassign_both_integral_snapshot(S_left, pintegeroperation, n_target, n_right) = ((' + bits + ', ' + count + '))',
        '$modassign_warning_ready(S_left, pintegeroperation, n_target, n_right) = eps',
        '$modassign_both_right_snapshot(S_left, pintegeroperation, n_target, n_right) = eps',
        '$modassign_both_integral_snapshot(S_left[.STORE[n_right] = DEFINED (PFLOAT 13832806255468478464)], pintegeroperation, n_target, n_right) = eps',
        '$modassign_both_integral_snapshot(S_left[.STORE[n_right] = DEFINED (PFLOAT 9221120237041090560)], pintegeroperation, n_target, n_right) = eps',
        '$integer_binary(pintegeroperation.OP, i_left, ' + count + ') = ' + ('IRESULT (-1)' if wide else 'NEGSHIFT'),
    ]
    if wide:
        checks += [
            'S_commit_budget = $drive_steps(S_left, 1)', 'S_commit_budget.COMPLETION = BUDGET',
            'S_commit = S_commit_budget[.COMPLETION = NORMAL]', '$shiftassign_both_frontier(S_commit, 9)',
            'S_commit.TODO = ptask_tail*', '~$shiftassign_both_tasks(S_commit.TODO)',
            'S_commit.RESULT = KNOWN (PINT (-1))',
            '~$shiftassign_both_frontier(S_commit, 5)', '~$shiftassign_both_frontier(S_commit, 11)',
            '$lookup(S_commit.ENV, $ptascii("left")) = (n_new)', 'n_new = |S_left.STORE|',
            'S_commit.CELL = n_new', 'S_commit.LOCATION = ROOT n_new', '~(n_new <- S_commit.REFCELLS)',
            '$lookup(S_commit.ENV, $ptascii("alias")) = (n_target)',
            'S_commit.STORE = S_left.STORE ++ [DEFINED (PINT (-1))]',
            'S_commit.ALLOCATIONS = S_left.ALLOCATIONS ++ [HCELL n_new]',
            'S_commit.STORE[n_target] = DEFINED (PINT 99)',
            'S_commit.STORE[n_right] = DEFINED (PFLOAT ' + bits + ')',
            'S_commit.STORE[n_v] = DEFINED (PINT 100)', 'S_commit.STORE[n_calls] = DEFINED (PINT 1)',
            '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_target) = 1',
            '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_new) = 1',
            '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_right) = 1',
            'S_commit.EVENTS = S_left.EVENTS',
            '$call_descriptors_valid(S_commit)', '$heap_valid($heap_graph(S_commit))',
            'S_done = $drive_steps(S_commit, 4000)',
            '$lookup(S_done.ENV, $ptascii("left")) = (n_new)',
            'S_done.STORE[n_new] = DEFINED (PINT 7)',
            'S_done.STORE[n_target] = DEFINED (PINT 99)',
        ]
    else:
        checks += [
            'S_error_budget = $drive_steps(S_left, 1)', 'S_error_budget.COMPLETION = BUDGET',
            'S_error = S_error_budget[.COMPLETION = NORMAL]', '$shiftassign_both_frontier(S_error, 10)',
            'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
            '~$shiftassign_both_tasks(S_error.TODO)',
            'S_error.RESULT = KNOWN PNULL', 'S_error.CURRENT = eps', 'S_error.FRAMES = eps',
            'n_error = |S_left.OBJECTS|',
            'S_error.OBJECTS[n_error] = THROWABLE pthrowable',
            'S_error.OBJECTS = S_left.OBJECTS ++ [THROWABLE pthrowable]',
            'pthrowable.KIND = "ArithmeticError"', 'pthrowable.ORIGIN = (pintegeroperation.SITE)',
            '$throwable_field(S_error, n_error, "line") = PINT 25',
            '$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("Bit shift by negative number"))',
            '$throwable_previous_id(S_error, n_error) = eps', '$throwable_live(S_error, n_error)',
            '$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]',
            '$heap_owners($heap_prune($heap_graph(S_error)), HOBJECT n_error) = 1',
            'S_error.STORE = S_left.STORE', 'S_error.ENV = S_left.ENV',
            'S_error.REFCELLS = S_left.REFCELLS', 'S_error.EVENTS = S_left.EVENTS',
            '$heap_owners($heap_prune($heap_graph(S_error)), HCELL n_target) = 2',
            '$heap_owners($heap_prune($heap_graph(S_error)), HCELL n_right) = 1',
            '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
            'S_done = $drive_steps(S_error, 4000)',
            '$lookup(S_done.ENV, $ptascii("left")) = (n_target)',
            'S_done.STORE[n_target] = DEFINED (PINT 7)',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("alias")) = (n_target)',
        'S_done.STORE[n_right] = DEFINED (PFLOAT ' + bits + ')',
        'S_done.STORE[n_v] = DEFINED (PINT ' + ('(-1)' if wide else '100') + ')', 'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        '$shiftassign_quiet_float_review_deprecations(S_done.EVENTS) = 1',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 4000) = S_done', '$drive_steps(S_left, 4000) = S_done',
        '$drive_steps(S_first, 4000) = S_done',
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
    report['review_scope'] = 'One default LEFT deprecation, quiet float count and historical negative LEFT: negative count raises fresh ArithmeticError25 without store/detachment; wide count stores signed(-1) in a new CELL/LOCATION and detaches alias99, exact events/owners/whole-budget equality; new composition only, no threshold evidence renewal'
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
