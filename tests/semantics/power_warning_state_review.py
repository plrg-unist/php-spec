#!/usr/bin/env python3
"""Signed-zero power capture survives a false handler and live operand writes."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import power_warning_review_cases as cases
import power_warning_protocol as shared

REVIEW_HELPERS = r"""
dec $power_review_deprecation(pevent) : nat
def $power_review_deprecation(DIAGNOSTIC "Deprecated" n* z) = 1
def $power_review_deprecation(pevent) = 0 -- otherwise
dec $power_review_deprecations(pevent*) : nat
def $power_review_deprecations(eps) = 0
def $power_review_deprecations(pevent :: pevent_tail*) = $($power_review_deprecation(pevent) + $power_review_deprecations(pevent_tail*))
"""


def conditions(name, program, path, stdout):
    marker = lambda stage: 'POWER_WARNING pintegeroperation pnumber_base pnumber_exponent ' + str(stage)
    return [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $power_seek(S_initial, 1, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$power_frontier(S, 1)',
        'S.TODO = (' + marker(0) + ') :: ptask_tail*',
        'pnumber_base = NFLOAT 9223372036854775808',
        'pnumber_exponent = NINT (-3)',
        'pintegeroperation.OP = POWER', '~pintegeroperation.SWAPPED',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("base")) 13',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("exponent")) 15',
        'pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("base"))',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("exponent"))',
        'pintegeroperation.LINE = 15', 'S.ORIGIN = (pintegeroperation.SITE)',
        '$lookup(S.ENV, $ptascii("base")) = (n_base)',
        '$lookup(S.ENV, $ptascii("exponent")) = (n_exponent)',
        '$lookup(S.ENV, $ptascii("v")) = (n_v)',
        'S.STORE[n_base] = DEFINED (PFLOAT 9223372036854775808)',
        'S.STORE[n_exponent] = DEFINED (PINT (-3))',
        'S.STORE[n_v] = DEFINED (PINT 100)',
        '~(n_base <- S.REFCELLS)', '~(n_exponent <- S.REFCELLS)',
        'S.RESULT = KNOWN PNULL', 'S.BASE = BASE_VALUE (KNOWN PNULL)',
        '$power_warning_valid(S, pintegeroperation, pnumber_base, pnumber_exponent, 0)',
        '$task_nodes(' + marker(0) + ') = eps',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_base) = 1',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_exponent) = 1',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '$power_review_deprecations(S.EVENTS) = 0',
        '~$power_warning_valid(S, pintegeroperation, NFLOAT 0, pnumber_exponent, 0)',
        'S_positive = S[.TODO = (POWER_WARNING pintegeroperation (NFLOAT 0) pnumber_exponent 0) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_positive))', '~$call_descriptors_valid(S_positive)',
        'S_dispatch_budget = $drive_steps(S, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(1), 'perrorcall.TARGET = eps',
        'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 15',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'perrorcall_positive = perrorcall[.RESUME = POWER_WARNING pintegeroperation (NFLOAT 0) pnumber_exponent 1]',
        '~$error_call_valid(S_dispatch, perrorcall_positive)',
        'S_dispatch_positive = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall_positive) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_dispatch_positive))', '~$call_descriptors_valid(S_dispatch_positive)',
        'S_return_found = $power_seek(S_dispatch, 4, 2000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', '$power_frontier(S_return, 4)',
        'S_return.TODO = (' + marker(1) + ') :: ptask_tail*',
        'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
        'S_return.STORE[n_base] = DEFINED (PINT 4)',
        'S_return.STORE[n_exponent] = DEFINED (PINT 2)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)',
        '$power_warning_valid(S_return, pintegeroperation, pnumber_base, pnumber_exponent, 1)',
        '~$power_warning_valid(S_return, pintegeroperation, pnumber_base, pnumber_exponent, 0)',
        '$power_review_deprecations(S_return.EVENTS) = 1',
        '(DIAGNOSTIC "Deprecated" ($ptascii("Power of base 0 and negative exponent is deprecated")) 15) <- S_return.EVENTS',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'S_delivery_budget = $drive_steps(S_return, 1)', 'S_delivery_budget.COMPLETION = BUDGET',
        'S_delivery = S_delivery_budget[.COMPLETION = NORMAL]', '$power_frontier(S_delivery, 5)',
        'S_delivery.TODO = ptask_tail*', '~$power_tasks(S_delivery.TODO)',
        'S_delivery.RESULT = KNOWN (PFLOAT 18442240474082181120)',
        'S_delivery.STORE = S_return.STORE',
        'S_delivery.ALLOCATIONS = S_return.ALLOCATIONS',
        'S_delivery.ARRAYS = S_return.ARRAYS', 'S_delivery.OBJECTS = S_return.OBJECTS',
        'S_delivery.STRINGDATA = S_return.STRINGDATA', 'S_delivery.EVENTS = S_return.EVENTS',
        'S_delivery.STORE[n_v] = DEFINED (PINT 100)',
        '$call_descriptors_valid(S_delivery)', '$heap_valid($heap_graph(S_delivery))',
        'S_done = $drive_steps(S_delivery, 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_v] = DEFINED (PFLOAT 18442240474082181120)',
        'S_done.STORE[n_base] = DEFINED (PINT 4)',
        'S_done.STORE[n_exponent] = DEFINED (PINT 2)',
        '$power_review_deprecations(S_done.EVENTS) = 1',
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
    report['review_scope'] = 'Actual signed-zero capture and negative-infinity delivery through false/default handler; fresh sign-cache refusals, unchanged storage, sentinel and budgets; production continuations only'
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
