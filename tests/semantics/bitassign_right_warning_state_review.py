#!/usr/bin/env python3
"""A saved negative RIGHT remains an XOR mask through the callback."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import bitassign_right_warning_review_cases as cases
import bitassign_right_warning_protocol as shared

REVIEW_HELPERS = r"""
dec $bitassign_right_review_deprecation(pevent) : nat
def $bitassign_right_review_deprecation(DIAGNOSTIC "Deprecated" n* z) = 1
def $bitassign_right_review_deprecation(pevent) = 0 -- otherwise
dec $bitassign_right_review_deprecations(pevent*) : nat
def $bitassign_right_review_deprecations(eps) = 0
def $bitassign_right_review_deprecations(pevent :: pevent_tail*) = $($bitassign_right_review_deprecation(pevent) + $bitassign_right_review_deprecations(pevent_tail*))
"""


def conditions(name, program, path, stdout):
    marker = lambda stage: 'BIT_ASSIGN_RIGHT_WARNING pintegeroperation n_target n_right i_left n_bits i_right ' + str(stage)
    return [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $bitassign_right_seek(S_initial, 1, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$bitassign_right_frontier(S, 1)',
        'S.TODO = (' + marker(0) + ') :: ptask_tail*',
        'i_left = 12', 'n_bits = 13832806255468478464', 'i_right = (-1)',
        'pintegeroperation.OP = BITXOR', '~pintegeroperation.SWAPPED',
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
        '$bitassign_right_warning_valid(S, pintegeroperation, n_target, n_right, i_left, n_bits, i_right, 0)',
        '~$bitassign_right_warning_valid(S, pintegeroperation, n_target, n_right, 13, n_bits, i_right, 0)',
        '~$bitassign_right_warning_valid(S, pintegeroperation, n_target, n_right, i_left, 13836183955189006336, (-2), 0)',
        '$task_nodes(' + marker(0) + ') = eps',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_right) = 1',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '$bitassign_right_review_deprecations(S.EVENTS) = 0',
        'S_dispatch_budget = $drive_steps(S, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(1), 'perrorcall.TARGET = eps',
        'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 16',
        '$error_call_valid(S_dispatch, perrorcall)',
        'perrorcall_changed = perrorcall[.RESUME = BIT_ASSIGN_RIGHT_WARNING pintegeroperation n_target n_right 13 13836183955189006336 (-2) 1][.MESSAGE = $ptascii("Implicit conversion from float -2.5 to int loses precision")][.EVENT = DIAGNOSTIC "Deprecated" ($ptascii("Implicit conversion from float -2.5 to int loses precision")) 16]',
        '~$error_call_valid(S_dispatch, perrorcall_changed)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'S_return_found = $bitassign_right_seek(S_dispatch, 4, 2000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', '$bitassign_right_frontier(S_return, 4)',
        'S_return.TODO = (' + marker(1) + ') :: ptask_tail*',
        'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
        '$lookup(S_return.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S_return.ENV, $ptascii("alias")) = (n_target)',
        '$lookup(S_return.ENV, $ptascii("right")) = (n_right)',
        'n_target <- S_return.REFCELLS', '~(n_right <- S_return.REFCELLS)',
        'S_return.STORE[n_target] = DEFINED (PINT 99)',
        'S_return.STORE[n_right] = DEFINED (PINT 10)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)',
        '$bitassign_right_warning_valid(S_return, pintegeroperation, n_target, n_right, i_left, n_bits, i_right, 1)',
        '~$bitassign_right_warning_valid(S_return, pintegeroperation, n_target, n_right, i_left, n_bits, i_right, 0)',
        '$powerassign_warning_ready(S_return, pintegeroperation, n_target)',
        '$integer_binary(pintegeroperation.OP, i_left, i_right) = IRESULT (-13)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_target) = 2',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 1',
        '$bitassign_right_review_deprecations(S_return.EVENTS) = 1',
        '(DIAGNOSTIC "Deprecated" ($ptascii("Implicit conversion from float -1.5 to int loses precision")) 16) <- S_return.EVENTS',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'S_commit_budget = $drive_steps(S_return, 1)', 'S_commit_budget.COMPLETION = BUDGET',
        'S_commit = S_commit_budget[.COMPLETION = NORMAL]', '$bitassign_right_frontier(S_commit, 5)',
        'S_commit.TODO = ptask_tail*', '~$bitassign_right_tasks(S_commit.TODO)',
        'S_commit.RESULT = KNOWN (PINT (-13))',
        '$lookup(S_commit.ENV, $ptascii("left")) = (n_new)', 'n_new = |S_return.STORE|',
        'S_commit.CELL = n_new', 'S_commit.LOCATION = ROOT n_new', '~(n_new <- S_commit.REFCELLS)',
        '$lookup(S_commit.ENV, $ptascii("alias")) = (n_target)',
        'S_commit.STORE = S_return.STORE ++ [DEFINED (PINT (-13))]',
        'S_commit.ALLOCATIONS = S_return.ALLOCATIONS ++ [HCELL n_new]',
        'S_commit.STORE[n_target] = DEFINED (PINT 99)',
        'S_commit.STORE[n_right] = DEFINED (PINT 10)',
        'S_commit.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_new) = 1',
        '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_right) = 1',
        'S_commit.EVENTS = S_return.EVENTS',
        '$call_descriptors_valid(S_commit)', '$heap_valid($heap_graph(S_commit))',
        'S_done = $drive_steps(S_commit, 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_new)',
        '$lookup(S_done.ENV, $ptascii("alias")) = (n_target)',
        'S_done.STORE[n_new] = DEFINED (PINT 7)',
        'S_done.STORE[n_target] = DEFINED (PINT 99)',
        'S_done.STORE[n_right] = DEFINED (PINT 10)',
        'S_done.STORE[n_v] = DEFINED (PINT (-13))',
        '$bitassign_right_review_deprecations(S_done.EVENTS) = 1',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 2000) = S_done', '$drive_steps(S_return, 2000) = S_done',
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
    report['review_scope'] = 'Actual cached negative RIGHT XOR mask: fresh both-cache public refusals, actual new CELL/LOCATION and detached alias owners, default Deprecated16, whole/budget equality; production continuations only'
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
