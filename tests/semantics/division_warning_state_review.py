#!/usr/bin/env python3
"""Genuine cached-zero division, false fallback and caller error frontiers."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import division_warning_review_cases as cases
import division_warning_protocol as shared

REVIEW_HELPERS = r'''
dec $review_warning_item(pevent) : nat
def $review_warning_item(DIAGNOSTIC "Warning" n* z) = 1
def $review_warning_item(pevent) = 0 -- otherwise
dec $review_warnings(pevent*) : nat
def $review_warnings(eps) = 0
def $review_warnings(pevent :: pevent_tail*) = $($review_warning_item(pevent) + $review_warnings(pevent_tail*))
'''


def conditions(name, program, path, stdout):
    return [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $division_seek(S_initial, 6, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$division_frontier(S, 6)',
        'S.TODO = (ARITHMETIC_DIV_WARNING pintegeroperation (ARITHMETIC_RIGHT (NINT 12)) pvalue (NINT 0) 0) :: ptask_tail*',
        'pintegeroperation.OP = DIVIDE',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_left',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_right', 'n_left =/= n_right',
        'S.STORE[n_left] = DEFINED (PINT 99)',
        '$integer_pointer_value(S, pintegeroperation.RIGHTPOINTER) = (pvalue)',
        '$string_bytes(pvalue) = ($ptascii("0tail"))',
        '$arithmetic_div_warning_valid(S, pintegeroperation, ARITHMETIC_RIGHT (NINT 12), pvalue, NINT 0, 0)',
        '$task_nodes(ARITHMETIC_DIV_WARNING pintegeroperation (ARITHMETIC_RIGHT (NINT 12)) pvalue (NINT 0) 0) = eps',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_right) = 2',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '$review_warnings(S.EVENTS) = 0',
        '~$arithmetic_div_warning_valid(S, pintegeroperation, ARITHMETIC_RIGHT (NINT 12), pvalue, NINT 1, 0)',
        '~$arithmetic_div_warning_valid(S, pintegeroperation, ARITHMETIC_RIGHT (NINT 12), PSTRING ($ptascii("99tail")), NINT 99, 0)',
        'S_bad = S[.TODO = (ARITHMETIC_DIV_WARNING pintegeroperation (ARITHMETIC_RIGHT (NINT 12)) (PSTRING ($ptascii("99tail"))) (NINT 99) 0) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_bad))', '~$call_descriptors_valid(S_bad)',
        'S_dispatch_budget = $drive_steps(S, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.TARGET = eps',
        'perrorcall.RESUME = ARITHMETIC_DIV_WARNING pintegeroperation (ARITHMETIC_RIGHT (NINT 12)) pvalue (NINT 0) 1',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'perrorcall_bad = perrorcall[.RESUME = ARITHMETIC_DIV_WARNING pintegeroperation (ARITHMETIC_RIGHT (NINT 12)) (PSTRING ($ptascii("99tail"))) (NINT 99) 1]',
        '~$error_call_valid(S_dispatch, perrorcall_bad)',
        'S_dispatch_bad = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall_bad) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_dispatch_bad))', '~$call_descriptors_valid(S_dispatch_bad)',
        'S_return_found = $division_seek(S_dispatch, 8, 2000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', '$division_frontier(S_return, 8)',
        'S_return.TODO = (ARITHMETIC_DIV_WARNING pintegeroperation (ARITHMETIC_RIGHT (NINT 12)) pvalue (NINT 0) 1) :: ptask_tail*',
        'S_return.STORE[n_left] = DEFINED (PINT 99)',
        '$integer_pointer_value(S_return, pintegeroperation.RIGHTPOINTER) = (PINT 7)',
        '$arithmetic_div_warning_valid(S_return, pintegeroperation, ARITHMETIC_RIGHT (NINT 12), pvalue, NINT 0, 1)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 2',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        '$review_warnings(S_return.EVENTS) = 1',
        '(DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) pintegeroperation.LINE) <- S_return.EVENTS',
        'S_throw_budget = $drive_steps(S_return, 1)', 'S_throw_budget.COMPLETION = BUDGET',
        'S_throw = S_throw_budget[.COMPLETION = NORMAL]', '$division_frontier(S_throw, 9)',
        'S_throw.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        'S_throw.RESULT = KNOWN PNULL', 'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps',
        '~$division_tasks(S_throw.TODO)',
        'S_throw.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "DivisionByZeroError"',
        'pthrowable.ORIGIN = (pintegeroperation.SITE)',
        '$throwable_field(S_throw, n_error, "line") = PINT pintegeroperation.LINE',
        '$string_bytes($throwable_field(S_throw, n_error, "message")) = ($ptascii("Division by zero"))',
        '$throwable_previous_id(S_throw, n_error) = eps', '$throwable_live(S_throw, n_error)',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_error) = 1',
        '$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]',
        '$lookup(S_throw.ENV, $ptascii("v")) = (n_v)', 'S_throw.STORE[n_v] = DEFINED (PINT 100)',
        'S_throw.STORE[n_left] = DEFINED (PINT 99)', 'S_throw.STORE[n_right] = DEFINED (PINT 7)',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_right) = 2',
        '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
        '$review_warnings(S_throw.EVENTS) = 1',
        'S_done = $drive_steps(S_throw, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$review_warnings(S_done.EVENTS) = 1',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 2000) = S_done', '$drive_steps(S_dispatch, 2000) = S_done',
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
    report['review_scope'] = 'Genuine RIGHT-zero warning and caller Error frontiers; no raw step or forged continuation'
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
