#!/usr/bin/env python3
"""Two genuine deprecations retain a negative XOR mask and detach a late alias."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import bitassign_both_warning_review_cases as cases
import bitassign_both_warning_protocol as shared

REVIEW_HELPERS = r"""
dec $bitassign_both_review_deprecation(pevent) : nat
def $bitassign_both_review_deprecation(DIAGNOSTIC "Deprecated" n* z) = 1
def $bitassign_both_review_deprecation(pevent) = 0 -- otherwise
dec $bitassign_both_review_deprecations(pevent*) : nat
def $bitassign_both_review_deprecations(eps) = 0
def $bitassign_both_review_deprecations(pevent :: pevent_tail*) = $($bitassign_both_review_deprecation(pevent) + $bitassign_both_review_deprecations(pevent_tail*))
"""


def conditions(name, program, path, stdout):
    left = lambda stage: 'BIT_ASSIGN_BOTH_LEFT pintegeroperation n_target n_right n_bits_left i_left ' + str(stage)
    right = lambda stage: 'BIT_ASSIGN_BOTH_RIGHT pintegeroperation n_target n_right n_bits_left i_left n_bits_right i_right ' + str(stage)
    return [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $bitassign_both_seek(S_initial, 1, 4000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S, 1)',
        'S.TODO = (' + left(0) + ') :: ptask_tail*',
        'n_bits_left = 4623226492472524800', 'i_left = 12',
        'pintegeroperation.OP = BITXOR', '~pintegeroperation.SWAPPED',
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
        '~$call_task_valid(S, BIT_ASSIGN_BOTH_LEFT pintegeroperation n_target n_right 4623789442425946112 13 0)',
        '$task_nodes(' + left(0) + ') = eps',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_right) = 1',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '$bitassign_both_review_deprecations(S.EVENTS) = 0',
        'S_first_budget = $drive_steps(S, 1)', 'S_first_budget.COMPLETION = BUDGET',
        'S_first = S_first_budget[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_first, 2)',
        'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
        'perrorcall_first.RESUME = ' + left(1), 'perrorcall_first.TARGET = eps',
        'perrorcall_first.LEVEL = 8192', 'perrorcall_first.LINE = 25',
        'perrorcall_first.MESSAGE = $ptascii("Implicit conversion from float 12.5 to int loses precision")',
        '$error_call_valid(S_first, perrorcall_first)',
        '$call_descriptors_valid(S_first)', '$heap_valid($heap_graph(S_first))',
        'S_left_found = $bitassign_both_seek(S_first, 4, 4000)',
        r'S_left_found.COMPLETION = NORMAL \/ S_left_found.COMPLETION = BUDGET',
        'S_left = S_left_found[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_left, 4)',
        'S_left.TODO = (' + left(1) + ') :: ptask_tail*',
        'S_left.CURRENT = eps', 'S_left.FRAMES = eps',
        '$lookup(S_left.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S_left.ENV, $ptascii("alias")) = (n_target)',
        '$lookup(S_left.ENV, $ptascii("right")) = (n_right)',
        'n_target <- S_left.REFCELLS', '~(n_right <- S_left.REFCELLS)',
        'S_left.STORE[n_target] = DEFINED (PINT 99)',
        'S_left.STORE[n_right] = DEFINED (PFLOAT 13832806255468478464)',
        'S_left.STORE[n_v] = DEFINED (PINT 100)', 'S_left.STORE[n_calls] = DEFINED (PINT 1)',
        '$call_task_valid(S_left, ' + left(1) + ')',
        '~$call_task_valid(S_left, ' + left(0) + ')',
        'S_left.ERRORHANDLER = S.ERRORHANDLER',
        '$heap_owners($heap_prune($heap_graph(S_left)), HCELL n_target) = 2',
        '$bitassign_both_review_deprecations(S_left.EVENTS) = 0',
        '$call_descriptors_valid(S_left)', '$heap_valid($heap_graph(S_left))',
        'S_right_budget = $drive_steps(S_left, 1)', 'S_right_budget.COMPLETION = BUDGET',
        'S_right = S_right_budget[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_right, 5)',
        'S_right.TODO = (' + right(0) + ') :: ptask_tail*',
        'n_bits_right = 13832806255468478464', 'i_right = (-1)',
        'S_right.STORE = S_left.STORE', 'S_right.ENV = S_left.ENV',
        'S_right.REFCELLS = S_left.REFCELLS', 'S_right.EVENTS = S_left.EVENTS',
        '$call_task_valid(S_right, ' + right(0) + ')',
        '~$call_task_valid(S_right, BIT_ASSIGN_BOTH_RIGHT pintegeroperation n_target n_right n_bits_left i_left 13836183955189006336 (-2) 0)',
        '$task_nodes(' + right(0) + ') = eps',
        '$heap_owners($heap_prune($heap_graph(S_right)), HCELL n_target) = 2',
        '$heap_owners($heap_prune($heap_graph(S_right)), HCELL n_right) = 1',
        '$call_descriptors_valid(S_right)', '$heap_valid($heap_graph(S_right))',
        'S_second_budget = $drive_steps(S_right, 1)', 'S_second_budget.COMPLETION = BUDGET',
        'S_second = S_second_budget[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_second, 6)',
        'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
        'perrorcall_second.RESUME = ' + right(1), 'perrorcall_second.TARGET = eps',
        'perrorcall_second.LEVEL = 8192', 'perrorcall_second.LINE = 25',
        'perrorcall_second.MESSAGE = $ptascii("Implicit conversion from float -1.5 to int loses precision")',
        '$error_call_valid(S_second, perrorcall_second)',
        'perrorcall_changed = perrorcall_second[.RESUME = BIT_ASSIGN_BOTH_RIGHT pintegeroperation n_target n_right n_bits_left i_left 13836183955189006336 (-2) 1][.MESSAGE = $ptascii("Implicit conversion from float -2.5 to int loses precision")][.EVENT = DIAGNOSTIC "Deprecated" ($ptascii("Implicit conversion from float -2.5 to int loses precision")) 25]',
        '~$error_call_valid(S_second, perrorcall_changed)',
        '$call_descriptors_valid(S_second)', '$heap_valid($heap_graph(S_second))',
        'S_return_found = $bitassign_both_seek(S_second, 8, 4000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_return, 8)',
        'S_return.TODO = (' + right(1) + ') :: ptask_tail*',
        'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
        '$lookup(S_return.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S_return.ENV, $ptascii("alias")) = (n_target)',
        '$lookup(S_return.ENV, $ptascii("right")) = (n_right)',
        'n_target <- S_return.REFCELLS', '~(n_right <- S_return.REFCELLS)',
        'S_return.STORE[n_target] = DEFINED (PINT 88)',
        'S_return.STORE[n_right] = DEFINED (PINT 10)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)', 'S_return.STORE[n_calls] = DEFINED (PINT 2)',
        '$call_task_valid(S_return, ' + right(1) + ')',
        '~$call_task_valid(S_return, ' + right(0) + ')',
        '$powerassign_warning_ready(S_return, pintegeroperation, n_target)',
        '$integer_binary(pintegeroperation.OP, i_left, i_right) = IRESULT (-13)',
        'S_return.ERRORHANDLER = S.ERRORHANDLER',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_target) = 2',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 1',
        '$bitassign_both_review_deprecations(S_return.EVENTS) = 1',
        '(DIAGNOSTIC "Deprecated" ($ptascii("Implicit conversion from float -1.5 to int loses precision")) 25) <- S_return.EVENTS',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'S_commit_budget = $drive_steps(S_return, 1)', 'S_commit_budget.COMPLETION = BUDGET',
        'S_commit = S_commit_budget[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_commit, 9)',
        'S_commit.TODO = ptask_tail*', '~$bitassign_both_tasks(S_commit.TODO)',
        'S_commit.RESULT = KNOWN (PINT (-13))',
        '$lookup(S_commit.ENV, $ptascii("left")) = (n_new)', 'n_new = |S_return.STORE|',
        'S_commit.CELL = n_new', 'S_commit.LOCATION = ROOT n_new', '~(n_new <- S_commit.REFCELLS)',
        '$lookup(S_commit.ENV, $ptascii("alias")) = (n_target)',
        'S_commit.STORE = S_return.STORE ++ [DEFINED (PINT (-13))]',
        'S_commit.ALLOCATIONS = S_return.ALLOCATIONS ++ [HCELL n_new]',
        'S_commit.STORE[n_target] = DEFINED (PINT 88)',
        'S_commit.STORE[n_right] = DEFINED (PINT 10)',
        'S_commit.STORE[n_v] = DEFINED (PINT 100)', 'S_commit.STORE[n_calls] = DEFINED (PINT 2)',
        '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_new) = 1',
        '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_right) = 1',
        'S_commit.EVENTS = S_return.EVENTS',
        '$call_descriptors_valid(S_commit)', '$heap_valid($heap_graph(S_commit))',
        'S_done = $drive_steps(S_commit, 4000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_new)',
        '$lookup(S_done.ENV, $ptascii("alias")) = (n_target)',
        'S_done.STORE[n_new] = DEFINED (PINT 7)',
        'S_done.STORE[n_target] = DEFINED (PINT 88)',
        'S_done.STORE[n_right] = DEFINED (PINT 10)',
        'S_done.STORE[n_v] = DEFINED (PINT (-13))', 'S_done.STORE[n_calls] = DEFINED (PINT 2)',
        '$bitassign_both_review_deprecations(S_done.EVENTS) = 1',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 4000) = S_done', '$drive_steps(S_left, 4000) = S_done',
        '$drive_steps(S_right, 4000) = S_done', '$drive_steps(S_return, 4000) = S_done',
    ]


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
    report['review_scope'] = 'Two actual bitwise deprecations: historical LEFT, fresh negative second RHS cache, default second diagnostic then real XOR new CELL/LOCATION and detached alias owners, whole/budget equality; production continuations only'
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
