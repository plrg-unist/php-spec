#!/usr/bin/env python3
"""Cached concat assignment detaches a late alias only on normal commit."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import concatassign_array_warning_review_cases as cases
import concatassign_array_warning_protocol as shared

REVIEW_HELPERS = r"""
dec $concatassign_array_review_warning(pevent) : nat
def $concatassign_array_review_warning(DIAGNOSTIC "Warning" n* z) = 1
def $concatassign_array_review_warning(pevent) = 0 -- otherwise
dec $concatassign_array_review_warnings(pevent*) : nat
def $concatassign_array_review_warnings(eps) = 0
def $concatassign_array_review_warnings(pevent :: pevent_tail*) = $($concatassign_array_review_warning(pevent) + $concatassign_array_review_warnings(pevent_tail*))
"""


def conditions(name, program, path, stdout):
    marker = lambda stage: 'CONCATASSIGN_ARRAY_WARNING porigin poperand_left poperand_right pvalue_cached 18 ' + str(stage)
    return [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $concatassign_array_seek(S_initial, 1, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$concatassign_array_frontier(S, 1)',
        'S.TODO = (' + marker(0) + ') :: ptask_tail*',
        'poperand_left = VARIABLE ($ptascii("left")) 16',
        'poperand_right = VARIABLE ($ptascii("right")) 18',
        'pvalue_cached = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("before"))',
        'S.STRINGDATA[n_string] = $ptascii("before")',
        '$lookup(S.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S.ENV, $ptascii("v")) = (n_v)',
        'S.STORE[n_left] = DEFINED pvalue_cached',
        'S.STORE[n_right] = DEFINED (PARRAY n_array)',
        'S.STORE[n_v] = DEFINED (PINT 100)',
        'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
        '~(n_left <- S.REFCELLS)', '~(n_right <- S.REFCELLS)',
        'S.LOCATION = ROOT n_left', 'S.RESULT = KNOWN PNULL',
        'S.BASE = BASE_VALUE (KNOWN PNULL)', 'S.ORIGIN = (porigin)',
        '$concatassign_array_valid(S, porigin, poperand_left, poperand_right, pvalue_cached, 18, 0)',
        '$task_nodes(' + marker(0) + ') = eps',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_array) = 1',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '$concatassign_array_review_warnings(S.EVENTS) = 0',
        'S_dispatch_budget = $drive_steps(S, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(1), 'perrorcall.TARGET = eps',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'S_return_found = $concatassign_array_seek(S_dispatch, 4, 2000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', '$concatassign_array_frontier(S_return, 4)',
        'S_return.TODO = (' + marker(1) + ') :: ptask_tail*',
        'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
        '$lookup(S_return.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_return.ENV, $ptascii("alias")) = (n_left)',
        'n_left <- S_return.REFCELLS',
        'S_return.STORE[n_left] = DEFINED pvalue_after',
        '$string_bytes(pvalue_after) = ($ptascii("after"))',
        '$lookup(S_return.ENV, $ptascii("right")) = eps',
        'S_return.STORE[n_v] = DEFINED (PINT 100)',
        '$concatassign_array_valid(S_return, porigin, poperand_left, poperand_right, pvalue_cached, 18, 1)',
        '~$concatassign_array_valid(S_return, porigin, poperand_left, poperand_right, pvalue_cached, 18, 0)',
        '$concatassign_array_ready(S_return, poperand_left)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 0',
        '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_array) = 0',
        '$concatassign_array_review_warnings(S_return.EVENTS) = 1',
        '(DIAGNOSTIC "Warning" ($ptascii("Array to string conversion")) 18) <- S_return.EVENTS',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'S_commit_budget = $drive_steps(S_return, 1)', 'S_commit_budget.COMPLETION = BUDGET',
        'S_commit = S_commit_budget[.COMPLETION = NORMAL]', '$concatassign_array_frontier(S_commit, 5)',
        'S_commit.TODO = ptask_tail*', '~$concatassign_array_tasks(S_commit.TODO)',
        'S_commit.RESULT = KNOWN pvalue_result',
        'pvalue_result = PSTRING_CARRIER (REQUEST_STRING n_result) ($ptascii("beforeArray"))',
        'n_result = |S_return.STRINGDATA|',
        'S_commit.STRINGDATA = S_return.STRINGDATA ++ [$ptascii("beforeArray")]',
        'n_new = |S_return.STORE|', 'n_new =/= n_left',
        'S_commit.CELL = n_new', 'S_commit.LOCATION = ROOT n_new',
        '$lookup(S_commit.ENV, $ptascii("left")) = (n_new)',
        '$lookup(S_commit.ENV, $ptascii("alias")) = (n_left)',
        '~(n_new <- S_commit.REFCELLS)',
        'S_commit.STORE = S_return.STORE ++ [DEFINED pvalue_result]',
        'S_commit.STORE[n_left] = DEFINED pvalue_after',
        'S_commit.STORE[n_v] = DEFINED (PINT 100)',
        'S_commit.ALLOCATIONS = S_return.ALLOCATIONS ++ [HCELL n_new]',
        'S_commit.ARRAYS = S_return.ARRAYS', 'S_commit.OBJECTS = S_return.OBJECTS',
        'S_commit.EVENTS = S_return.EVENTS',
        '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_new) = 1',
        '$call_descriptors_valid(S_commit)', '$heap_valid($heap_graph(S_commit))',
        'S_done = $drive_steps(S_commit, 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_new)',
        '$lookup(S_done.ENV, $ptascii("alias")) = (n_left)',
        'S_done.STORE[n_new] = DEFINED pvalue_later',
        '$string_bytes(pvalue_later) = ($ptascii("later"))',
        'S_done.STORE[n_left] = DEFINED pvalue_after',
        'S_done.STORE[n_v] = DEFINED pvalue_result',
        '$lookup(S_done.ENV, $ptascii("right")) = eps',
        '$concatassign_array_review_warnings(S_done.EVENTS) = 1',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 2000) = S_done',
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
    report['review_scope'] = 'Actual late-alias normal commit: cached first request string, new plain CELL/LOCATION, retained old alias, default Warning18 and budgets; production continuations only'
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
