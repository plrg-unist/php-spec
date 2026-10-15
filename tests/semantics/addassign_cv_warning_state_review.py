#!/usr/bin/env python3
"""Plain compound commit detaches a late alias after a default warning."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import addassign_cv_warning_review_cases as cases
import addassign_cv_warning_protocol as shared

REVIEW_HELPERS = r'''
dec $addassign_cv_review_warning_item(pevent) : nat
def $addassign_cv_review_warning_item(DIAGNOSTIC "Warning" n* z) = 1
def $addassign_cv_review_warning_item(pevent) = 0 -- otherwise
dec $addassign_cv_review_warnings(pevent*) : nat
def $addassign_cv_review_warnings(eps) = 0
def $addassign_cv_review_warnings(pevent :: pevent_tail*) = $($addassign_cv_review_warning_item(pevent) + $addassign_cv_review_warnings(pevent_tail*))
'''


def conditions(name, program, path, stdout):
    return [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $addassign_cv_seek(S_initial, 1, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$addassign_cv_frontier(S, 1)',
        'S.TODO = (ARITHMETIC_ADDASSIGN_CV_WARNING pintegeroperation pvalue (NINT 12) 0) :: ptask_tail*',
        'pintegeroperation.LINE = 13',
        'pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("left"))',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))',
        '$lookup(S.ENV, $ptascii("left")) = (n_old)',
        '$lookup(S.ENV, $ptascii("right")) = (n_right)', 'n_old =/= n_right',
        '$lookup(S.ENV, $ptascii("v")) = (n_v)',
        '~(n_old <- S.REFCELLS)', '~(n_right <- S.REFCELLS)',
        'S.STORE[n_old] = DEFINED pvalue', '$string_bytes(pvalue) = ($ptascii("12tail"))',
        'S.STORE[n_right] = DEFINED (PINT 2)', 'S.STORE[n_v] = DEFINED (PINT 100)',
        '$arithmetic_addassign_cv_source(S, pintegeroperation)',
        '$arithmetic_addassign_cv_warning_valid(S, pintegeroperation, pvalue, NINT 12, 0)',
        '$task_nodes(ARITHMETIC_ADDASSIGN_CV_WARNING pintegeroperation pvalue (NINT 12) 0) = eps',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_old) = 1',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_right) = 1',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '$addassign_cv_review_warnings(S.EVENTS) = 0',
        'S_dispatch_budget = $drive_steps(S, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.TARGET = eps',
        'perrorcall.RESUME = ARITHMETIC_ADDASSIGN_CV_WARNING pintegeroperation pvalue (NINT 12) 1',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'S_return_found = $addassign_cv_seek(S_dispatch, 4, 2000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', '$addassign_cv_frontier(S_return, 4)',
        'S_return.TODO = (ARITHMETIC_ADDASSIGN_CV_WARNING pintegeroperation pvalue (NINT 12) 1) :: ptask_tail*',
        '$lookup(S_return.ENV, $ptascii("left")) = (n_old)',
        '$lookup(S_return.ENV, $ptascii("alias")) = (n_old)',
        '$lookup(S_return.ENV, $ptascii("right")) = (n_right)',
        'S_return.STORE[n_old] = DEFINED pvalue_changed',
        '$string_bytes(pvalue_changed) = ($ptascii("notnumeric"))',
        'S_return.STORE[n_right] = DEFINED (PINT 5)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)',
        'n_old <- S_return.REFCELLS', '~(n_right <- S_return.REFCELLS)',
        '~$arithmetic_add_selected(S_return, pintegeroperation)',
        '$arithmetic_addassign_cv_warning_valid(S_return, pintegeroperation, pvalue, NINT 12, 1)',
        '~$arithmetic_addassign_cv_warning_valid(S_return, pintegeroperation, pvalue, NINT 12, 0)',
        '$arithmetic_addassign_cv_ready(S_return, pintegeroperation) = (NINT 5)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_old) = 2',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 1',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        '$addassign_cv_review_warnings(S_return.EVENTS) = 1',
        '(DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) 13) <- S_return.EVENTS',
        'S_selection_bad = S_return[.STORE = $set_cell(S_return.STORE, n_old, DEFINED pvalue)][.TODO = (ARITHMETIC_ADDASSIGN_CV_WARNING pintegeroperation pvalue (NINT 12) 0) :: ptask_tail*]',
        '$integer_pointer_value(S_selection_bad, pintegeroperation.LEFTPOINTER) = (pvalue)',
        '~$arithmetic_add_selected(S_selection_bad, pintegeroperation)',
        '$heap_valid($heap_graph(S_selection_bad))',
        '~$arithmetic_addassign_cv_warning_valid(S_selection_bad, pintegeroperation, pvalue, NINT 12, 0)',
        '~$call_descriptors_valid(S_selection_bad)',
        'pintegeroperation_bad = pintegeroperation[.LEFTPOINTER = INTEGER_CELL n_old]',
        '~$arithmetic_addassign_cv_source(S_return, pintegeroperation_bad)',
        'S_pointer_bad = S_return[.TODO = (ARITHMETIC_ADDASSIGN_CV_WARNING pintegeroperation_bad pvalue (NINT 12) 1) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_pointer_bad))', '~$call_descriptors_valid(S_pointer_bad)',
        'S_right_ref = $reference_cell(S_return, n_right)',
        '$heap_valid($heap_graph(S_right_ref))',
        '$arithmetic_addassign_cv_ready(S_right_ref, pintegeroperation) = eps',
        'S_result_budget = $drive_steps(S_return, 1)', 'S_result_budget.COMPLETION = BUDGET',
        'S_result = S_result_budget[.COMPLETION = NORMAL]',
        'S_result.RESULT = KNOWN (PINT 17)', 'S_result.TODO = ptask_tail*',
        '$lookup(S_result.ENV, $ptascii("left")) = (n_new)',
        'n_new = |S_return.STORE|', 'n_new =/= n_old',
        'S_result.CELL = n_new', 'S_result.LOCATION = ROOT n_new',
        'S_result.STORE = S_return.STORE ++ [DEFINED (PINT 17)]',
        '$lookup(S_result.ENV, $ptascii("alias")) = (n_old)',
        'S_result.STORE[n_old] = DEFINED pvalue_changed',
        'S_result.STORE[n_right] = DEFINED (PINT 5)',
        'S_result.STORE[n_v] = DEFINED (PINT 100)',
        'n_old <- S_result.REFCELLS', '~(n_new <- S_result.REFCELLS)',
        '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_old) = 1',
        '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_new) = 1',
        'S_result.ALLOCATIONS = S_return.ALLOCATIONS ++ [HCELL n_new]',
        'S_result.OBJECTS = S_return.OBJECTS',
        '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_new)',
        '$lookup(S_done.ENV, $ptascii("alias")) = (n_old)',
        'S_done.STORE[n_new] = DEFINED (PINT 17)',
        'S_done.STORE[n_old] = DEFINED (PINT 88)',
        'S_done.STORE[n_v] = DEFINED (PINT 17)',
        '$addassign_cv_review_warnings(S_done.EVENTS) = 1',
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
    report['review_scope'] = 'Initially plain CV, late alias, new non-reference destination and retained alias owner; production steps only'
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
