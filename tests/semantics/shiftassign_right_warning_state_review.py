#!/usr/bin/env python3
"""Cached negative and wide shift counts preserve the original operands."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import shiftassign_right_warning_review_cases as cases
import shiftassign_right_warning_protocol as shared

REVIEW_HELPERS = r"""
dec $shiftassign_right_review_deprecation(pevent) : nat
def $shiftassign_right_review_deprecation(DIAGNOSTIC "Deprecated" n* z) = 1
def $shiftassign_right_review_deprecation(pevent) = 0 -- otherwise
dec $shiftassign_right_review_deprecations(pevent*) : nat
def $shiftassign_right_review_deprecations(eps) = 0
def $shiftassign_right_review_deprecations(pevent :: pevent_tail*) = $($shiftassign_right_review_deprecation(pevent) + $shiftassign_right_review_deprecations(pevent_tail*))
"""


def conditions(name, program, path, stdout):
    wide = name.endswith('-wide-default')
    left, bits, right, spelling = ('(-12)', '4634239200936329216', '64', '64.5') if wide else ('12', '13832806255468478464', '(-1)', '-1.5')
    marker = lambda stage: 'SHIFT_ASSIGN_RIGHT_WARNING pintegeroperation n_target n_right i_left n_bits i_right ' + str(stage)
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $shiftassign_right_seek(S_initial, 1, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$shiftassign_right_frontier(S, 1)',
        'S.TODO = (' + marker(0) + ') :: ptask_tail*',
        'i_left = ' + left, 'n_bits = ' + bits, 'i_right = ' + right,
        'pintegeroperation.OP = SHIFTRIGHT', '~pintegeroperation.SWAPPED',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 14',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 16',
        'pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("left"))',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))',
        'pintegeroperation.LINE = 16', 'S.ORIGIN = (pintegeroperation.SITE)',
        '$lookup(S.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S.ENV, $ptascii("v")) = (n_v)',
        'S.STORE[n_target] = DEFINED (PINT i_left)',
        'S.STORE[n_right] = DEFINED (PFLOAT n_bits)',
        'S.STORE[n_v] = DEFINED (PINT 100)',
        '~(n_target <- S.REFCELLS)', '~(n_right <- S.REFCELLS)',
        'S.LOCATION = ROOT n_target', 'S.RESULT = KNOWN PNULL',
        'S.BASE = BASE_VALUE (KNOWN PNULL)',
        '$shiftassign_right_warning_valid(S, pintegeroperation, n_target, n_right, i_left, n_bits, i_right, 0)',
        '$modassign_right_warning_snapshot(S, pintegeroperation, n_target, n_right, i_left, n_bits)',
        '$task_nodes(' + marker(0) + ') = eps',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_right) = 1',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '$shiftassign_right_review_deprecations(S.EVENTS) = 0',
        'S_dispatch_budget = $drive_steps(S, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(1), 'perrorcall.TARGET = eps',
        'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 16',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'S_return_found = $shiftassign_right_seek(S_dispatch, 4, 2000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', '$shiftassign_right_frontier(S_return, 4)',
        'S_return.TODO = (' + marker(1) + ') :: ptask_tail*',
        'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
        '$lookup(S_return.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S_return.ENV, $ptascii("alias")) = (n_target)',
        '$lookup(S_return.ENV, $ptascii("right")) = (n_right)',
        'n_target <- S_return.REFCELLS', '~(n_right <- S_return.REFCELLS)',
        'S_return.STORE[n_target] = DEFINED (PINT 99)',
        'S_return.STORE[n_right] = DEFINED (PINT 2)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)',
        '$shiftassign_right_warning_valid(S_return, pintegeroperation, n_target, n_right, i_left, n_bits, i_right, 1)',
        '~$shiftassign_right_warning_valid(S_return, pintegeroperation, n_target, n_right, i_left, n_bits, i_right, 0)',
        '$powerassign_warning_ready(S_return, pintegeroperation, n_target)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_target) = 2',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 1',
        '$shiftassign_right_review_deprecations(S_return.EVENTS) = 1',
        '(DIAGNOSTIC "Deprecated" ($ptascii("Implicit conversion from float ' + spelling + ' to int loses precision")) 16) <- S_return.EVENTS',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
    ]
    if wide:
        checks += [
            '$integer_binary(pintegeroperation.OP, i_left, i_right) = IRESULT (-1)',
            'S_commit_budget = $drive_steps(S_return, 1)', 'S_commit_budget.COMPLETION = BUDGET',
            'S_commit = S_commit_budget[.COMPLETION = NORMAL]', '$shiftassign_right_frontier(S_commit, 5)',
            'S_commit.TODO = ptask_tail*', 'S_commit.RESULT = KNOWN (PINT (-1))',
            '$lookup(S_commit.ENV, $ptascii("left")) = (n_new)', 'n_new = |S_return.STORE|',
            'S_commit.CELL = n_new', 'S_commit.LOCATION = ROOT n_new', '~(n_new <- S_commit.REFCELLS)',
            '$lookup(S_commit.ENV, $ptascii("alias")) = (n_target)',
            'S_commit.STORE = S_return.STORE ++ [DEFINED (PINT (-1))]',
            'S_commit.ALLOCATIONS = S_return.ALLOCATIONS ++ [HCELL n_new]',
            'S_commit.STORE[n_target] = DEFINED (PINT 99)', 'S_commit.STORE[n_v] = DEFINED (PINT 100)',
            '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_target) = 1',
            '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_new) = 1',
            'S_commit.EVENTS = S_return.EVENTS',
            '$call_descriptors_valid(S_commit)', '$heap_valid($heap_graph(S_commit))',
            'S_done = $drive_steps(S_commit, 2000)', '$drive_steps(S_return, 2000) = S_done',
            '$lookup(S_done.ENV, $ptascii("left")) = (n_new)',
            '$lookup(S_done.ENV, $ptascii("alias")) = (n_target)',
            'S_done.STORE[n_new] = DEFINED (PINT 7)',
            'S_done.STORE[n_target] = DEFINED (PINT 99)',
            'S_done.STORE[n_v] = DEFINED (PINT (-1))',
        ]
    else:
        checks += [
            '$integer_binary(pintegeroperation.OP, i_left, i_right) = NEGSHIFT',
            'S_error_budget = $drive_steps(S_return, 1)', 'S_error_budget.COMPLETION = BUDGET',
            'S_error = S_error_budget[.COMPLETION = NORMAL]', '$shiftassign_right_frontier(S_error, 6)',
            'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
            'S_error.RESULT = KNOWN PNULL', 'S_error.CURRENT = eps', 'S_error.FRAMES = eps',
            '~$shiftassign_right_tasks(S_error.TODO)',
            'S_error.OBJECTS[n_error] = THROWABLE pthrowable',
            'pthrowable.KIND = "ArithmeticError"', 'pthrowable.ORIGIN = (pintegeroperation.SITE)',
            'n_error = |S_return.OBJECTS|',
            'S_error.OBJECTS = S_return.OBJECTS ++ [THROWABLE pthrowable]',
            '$throwable_field(S_error, n_error, "line") = PINT 16',
            '$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("Bit shift by negative number"))',
            '$throwable_previous_id(S_error, n_error) = eps', '$throwable_live(S_error, n_error)',
            '$heap_owners($heap_prune($heap_graph(S_error)), HOBJECT n_error) = 1',
            '$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]',
            'S_error.STORE = S_return.STORE', 'S_error.ENV = S_return.ENV',
            'S_error.REFCELLS = S_return.REFCELLS', 'S_error.EVENTS = S_return.EVENTS',
            'S_error.STORE[n_target] = DEFINED (PINT 99)',
            'S_error.STORE[n_right] = DEFINED (PINT 2)',
            'S_error.STORE[n_v] = DEFINED (PINT 100)',
            '$heap_owners($heap_prune($heap_graph(S_error)), HCELL n_target) = 2',
            '$heap_owners($heap_prune($heap_graph(S_error)), HCELL n_right) = 1',
            '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
            'S_done = $drive_steps(S_error, 2000)',
            '$lookup(S_done.ENV, $ptascii("left")) = (n_target)',
            '$lookup(S_done.ENV, $ptascii("alias")) = (n_target)',
            'S_done.STORE[n_target] = DEFINED (PINT 7)',
            'S_done.STORE[n_v] = DEFINED (PINT 100)',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_right] = DEFINED (PINT 2)',
        '$shiftassign_right_review_deprecations(S_done.EVENTS) = 1',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 2000) = S_done', '$drive_steps(S_return, 2000) = S_done',
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
    report['review_scope'] = 'Actual cached negative-count ArithmeticError and cached64 signed result: no-store alias preservation versus real detachment/new CELL, default Deprecated16, ownership and budgets; production continuations only'
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
