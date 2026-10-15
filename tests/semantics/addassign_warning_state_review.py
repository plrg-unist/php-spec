#!/usr/bin/env python3
"""Compound ADD writes its retained cell after the target name is rebound."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import addassign_warning_review_cases as cases
import addassign_warning_protocol as shared

REVIEW_HELPERS = r'''
dec $addassign_review_warning_item(pevent) : nat
def $addassign_review_warning_item(DIAGNOSTIC "Warning" n* z) = 1
def $addassign_review_warning_item(pevent) = 0 -- otherwise
dec $addassign_review_warnings(pevent*) : nat
def $addassign_review_warnings(eps) = 0
def $addassign_review_warnings(pevent :: pevent_tail*) = $($addassign_review_warning_item(pevent) + $addassign_review_warnings(pevent_tail*))
'''


def conditions(name, program, path, stdout):
    return [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $addassign_seek(S_initial, 1, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$addassign_frontier(S, 1)',
        'S.TODO = (ARITHMETIC_ADDASSIGN_WARNING pintegeroperation pvalue (NINT 12) 0) :: ptask_tail*',
        'pintegeroperation.LINE = 13',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_left',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_right', 'n_left =/= n_right',
        '$lookup(S.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S.ENV, $ptascii("v")) = (n_v)',
        'S.STORE[n_left] = DEFINED pvalue', '$string_bytes(pvalue) = ($ptascii("12tail"))',
        'S.STORE[n_right] = DEFINED (PINT 2)', 'S.STORE[n_v] = DEFINED (PINT 100)',
        '$arithmetic_addassign_warning_valid(S, pintegeroperation, pvalue, NINT 12, 0)',
        '$task_nodes(ARITHMETIC_ADDASSIGN_WARNING pintegeroperation pvalue (NINT 12) 0) = eps',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_right) = 2',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '$addassign_review_warnings(S.EVENTS) = 0',
        'S_dispatch_budget = $drive_steps(S, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.TARGET = eps',
        'perrorcall.RESUME = ARITHMETIC_ADDASSIGN_WARNING pintegeroperation pvalue (NINT 12) 1',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'S_return_found = $addassign_seek(S_dispatch, 4, 2000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', '$addassign_frontier(S_return, 4)',
        'S_return.TODO = (ARITHMETIC_ADDASSIGN_WARNING pintegeroperation pvalue (NINT 12) 1) :: ptask_tail*',
        '$lookup(S_return.ENV, $ptascii("left")) = (n_new)', 'n_new =/= n_left',
        '$lookup(S_return.ENV, $ptascii("leftAlias")) = (n_left)',
        'S_return.STORE[n_left] = DEFINED pvalue', 'S_return.STORE[n_new] = DEFINED (PINT 99)',
        'S_return.STORE[n_right] = DEFINED (PINT 5)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
        '~$arithmetic_add_selected(S_return, pintegeroperation)',
        '$arithmetic_addassign_warning_valid(S_return, pintegeroperation, pvalue, NINT 12, 1)',
        '~$arithmetic_addassign_warning_valid(S_return, pintegeroperation, pvalue, NINT 12, 0)',
        'S_fresh_bad = S_return[.TODO = (ARITHMETIC_ADDASSIGN_WARNING pintegeroperation pvalue (NINT 12) 0) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_fresh_bad))', '~$call_descriptors_valid(S_fresh_bad)',
        '$arithmetic_addassign_ready(S_return, pintegeroperation) = (NINT 5)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 2',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        '$addassign_review_warnings(S_return.EVENTS) = 1',
        '(DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) 13) <- S_return.EVENTS',
        'S_result_budget = $drive_steps(S_return, 1)', 'S_result_budget.COMPLETION = BUDGET',
        'S_result = S_result_budget[.COMPLETION = NORMAL]',
        'S_result.RESULT = KNOWN (PINT 17)', 'S_result.TODO = ptask_tail*',
        'S_result.LOCATION = ROOT n_left',
        'S_result.STORE[n_left] = DEFINED (PINT 17)', 'S_result.STORE[n_new] = DEFINED (PINT 99)',
        'S_result.STORE[n_right] = DEFINED (PINT 5)', 'S_result.STORE[n_v] = DEFINED (PINT 100)',
        'S_result.ALLOCATIONS = S_return.ALLOCATIONS', 'S_result.OBJECTS = S_return.OBJECTS',
        '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_left) = 1',
        '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$addassign_review_warnings(S_done.EVENTS) = 1',
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
    report['review_scope'] = 'Retained compound destination with owner2-to1 name rebinding; production steps only'
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
