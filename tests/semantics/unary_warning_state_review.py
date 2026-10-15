#!/usr/bin/env python3
"""Genuine unary-minus boundary float capture, sign delivery and false fallback."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import unary_warning_review_cases as cases
import unary_warning_protocol as shared

REVIEW_HELPERS = r'''
dec $unary_review_warning(pevent) : nat
def $unary_review_warning(DIAGNOSTIC "Warning" n* z) = 1
def $unary_review_warning(pevent) = 0 -- otherwise
dec $unary_review_warnings(pevent*) : nat
def $unary_review_warnings(eps) = 0
def $unary_review_warnings(pevent :: pevent_tail*) = $($unary_review_warning(pevent) + $unary_review_warnings(pevent_tail*))
'''


def conditions(name, program, path, stdout):
    return [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $unary_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]', '$unary_frontier(S_entry, 0)',
        '$arithmetic_unary_plan(S_entry) = (punarywarning)',
        'punarywarning.OP = NEGATIVE', 'punarywarning.LINE = 11',
        'punarywarning.INPUT = VARIABLE ($ptascii("x")) 11',
        '$string_bytes(punarywarning.VALUE) = ($ptascii("-9223372036854775808tail"))',
        'punarywarning.NUMBER = NFLOAT 14114281232179134464',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)',
        'S_entry.STORE[n_x] = DEFINED punarywarning.VALUE',
        '$arithmetic_unary_snapshot(S_entry, punarywarning)',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '~$arithmetic_unary_valid(S_entry, punarywarning[.OP = POSITIVE])',
        '~$arithmetic_unary_valid(S_entry, punarywarning[.LINE = 10])',
        '~$arithmetic_unary_valid(S_entry, punarywarning[.INPUT = VARIABLE ($ptascii("v")) 11])',
        'S_capture_budget = $drive_steps(S_entry, 1)', 'S_capture_budget.COMPLETION = BUDGET',
        'S_capture = S_capture_budget[.COMPLETION = NORMAL]', '$unary_frontier(S_capture, 1)',
        'S_capture.TODO = (ARITHMETIC_UNARY_WARNING punarywarning 0) :: ptask_tail*',
        'S_capture.STORE = S_entry.STORE', 'S_capture.ALLOCATIONS = S_entry.ALLOCATIONS',
        '$task_nodes(ARITHMETIC_UNARY_WARNING punarywarning 0) = eps',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_x) = 1',
        '$arithmetic_unary_warning_valid(S_capture, punarywarning, 0)',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
        '~$arithmetic_unary_warning_valid(S_capture, punarywarning, 2)',
        'punarywarning_bad = punarywarning[.VALUE = PSTRING ($ptascii("99tail"))][.NUMBER = NINT 99]',
        'S_capture_bad = S_capture[.TODO = (ARITHMETIC_UNARY_WARNING punarywarning_bad 0) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_capture_bad))', '~$call_descriptors_valid(S_capture_bad)',
        'S_line_bad = S_capture[.TODO = (ARITHMETIC_UNARY_WARNING (punarywarning[.LINE = 10]) 0) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_line_bad))', '~$call_descriptors_valid(S_line_bad)',
        '$unary_review_warnings(S_capture.EVENTS) = 0',
        'S_dispatch_budget = $drive_steps(S_capture, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]', '$unary_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.TARGET = eps',
        'perrorcall.RESUME = ARITHMETIC_UNARY_WARNING punarywarning 1',
        'perrorcall.LINE = 11', '$error_call_valid(S_dispatch, perrorcall)',
        '$task_nodes(perrorcall.RESUME) = eps',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'perrorcall_bad = perrorcall[.RESUME = ARITHMETIC_UNARY_WARNING punarywarning_bad 1]',
        '~$error_call_valid(S_dispatch, perrorcall_bad)',
        'S_dispatch_bad = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall_bad) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_dispatch_bad))', '~$call_descriptors_valid(S_dispatch_bad)',
        'S_return_found = $unary_seek(S_dispatch, 4, 2000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', '$unary_frontier(S_return, 4)',
        'S_return.TODO = (ARITHMETIC_UNARY_WARNING punarywarning 1) :: ptask_tail*',
        'S_return.STORE[n_x] = DEFINED (PINT 99)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_x) = 1',
        '~$arithmetic_unary_snapshot(S_return, punarywarning)',
        '$arithmetic_unary_warning_valid(S_return, punarywarning, 1)',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        '$unary_review_warnings(S_return.EVENTS) = 1',
        '(DIAGNOSTIC "Warning" ($ptascii("A non-numeric value encountered")) 11) <- S_return.EVENTS',
        'S_delivered_budget = $drive_steps(S_return, 1)', 'S_delivered_budget.COMPLETION = BUDGET',
        'S_delivered = S_delivered_budget[.COMPLETION = NORMAL]', '$unary_frontier(S_delivered, 5)',
        'S_delivered.TODO = ptask_tail*',
        'S_delivered.RESULT = KNOWN (PFLOAT 4890909195324358656)',
        'S_delivered.STORE[n_x] = DEFINED (PINT 99)',
        '$lookup(S_delivered.ENV, $ptascii("v")) = (n_v)',
        'S_delivered.STORE[n_v] = DEFINED (PINT 100)',
        '~$unary_tasks(S_delivered.TODO)',
        '$call_descriptors_valid(S_delivered)', '$heap_valid($heap_graph(S_delivered))',
        'S_done = $drive_steps(S_delivered, 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$unary_review_warnings(S_done.EVENTS) = 1',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_capture, 2000) = S_done', '$drive_steps(S_dispatch, 2000) = S_done',
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
    report['review_scope'] = 'Genuine unary-minus boundary float capture, default warning and sign delivery; no raw or forged continuation'
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
