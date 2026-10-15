#!/usr/bin/env python3
"""A cached-zero RHS raises a caller Error while preserving the late alias."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import modassign_right_warning_review_cases as cases
import modassign_right_warning_protocol as shared

REVIEW_HELPERS = r"""
dec $modassign_right_review_deprecation(pevent) : nat
def $modassign_right_review_deprecation(DIAGNOSTIC "Deprecated" n* z) = 1
def $modassign_right_review_deprecation(pevent) = 0 -- otherwise
dec $modassign_right_review_deprecations(pevent*) : nat
def $modassign_right_review_deprecations(eps) = 0
def $modassign_right_review_deprecations(pevent :: pevent_tail*) = $($modassign_right_review_deprecation(pevent) + $modassign_right_review_deprecations(pevent_tail*))
"""


def conditions(name, program, path, stdout):
    marker = lambda stage, left='i_left', bits='n_bits', right='i_right', op='pintegeroperation': 'MOD_ASSIGN_RIGHT_WARNING ' + op + ' n_target n_right ' + left + ' ' + bits + ' ' + right + ' ' + str(stage)
    return [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $modassign_right_seek(S_initial, 1, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$modassign_right_frontier(S, 1)',
        'S.TODO = (' + marker(0) + ') :: ptask_tail*',
        'i_left = 12', 'n_bits = 4602678819172646912', 'i_right = 0',
        'pintegeroperation.OP = MODULO', '~pintegeroperation.SWAPPED',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 14',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 16',
        'pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("left"))',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))',
        'pintegeroperation.LINE = 16', 'S.ORIGIN = (pintegeroperation.SITE)',
        '$lookup(S.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S.ENV, $ptascii("v")) = (n_v)',
        'S.STORE[n_target] = DEFINED (PINT 12)',
        'S.STORE[n_right] = DEFINED (PFLOAT n_bits)',
        'S.STORE[n_v] = DEFINED (PINT 100)',
        '~(n_target <- S.REFCELLS)', '~(n_right <- S.REFCELLS)',
        'S.LOCATION = ROOT n_target', 'S.RESULT = KNOWN PNULL',
        'S.BASE = BASE_VALUE (KNOWN PNULL)',
        '$modassign_right_warning_valid(S, pintegeroperation, n_target, n_right, i_left, n_bits, i_right, 0)',
        '$modassign_right_warning_snapshot(S, pintegeroperation, n_target, n_right, i_left, n_bits)',
        '$task_nodes(' + marker(0) + ') = eps',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_right) = 1',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        '~$modassign_right_warning_valid(S, pintegeroperation, n_target, n_right, 13, n_bits, i_right, 0)',
        '~$modassign_right_warning_valid(S, pintegeroperation, n_target, n_right, i_left, n_bits, 1, 0)',
        '~$modassign_right_warning_valid(S, pintegeroperation, n_target, n_right, 9223372036854775808, n_bits, i_right, 1)',
        '~$modassign_right_warning_valid(S, pintegeroperation, n_target, n_right, i_left, n_bits, i_right, 2)',
        'pintegeroperation_line = pintegeroperation[.LINE = 15]',
        'S_line_bad = S[.TODO = (' + marker(0, op='pintegeroperation_line') + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_line_bad))', '~$call_descriptors_valid(S_line_bad)',
        '$modassign_right_review_deprecations(S.EVENTS) = 0',
        'S_dispatch_budget = $drive_steps(S, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(1), 'perrorcall.TARGET = eps',
        'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 16',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'n_message_bad* = $ptascii("Implicit conversion from float 1.5 to int loses precision")',
        'perrorcall_cache = perrorcall[.RESUME = ' + marker(1, bits='4609434218613702656', right='1') + '][.MESSAGE = n_message_bad*][.EVENT = DIAGNOSTIC "Deprecated" n_message_bad* 16]',
        '$modassign_right_warning_valid(S_dispatch, pintegeroperation, n_target, n_right, i_left, 4609434218613702656, 1, 1)',
        '~$error_call_valid(S_dispatch, perrorcall_cache)',
        'S_dispatch_bad = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall_cache) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_dispatch_bad))', '~$call_descriptors_valid(S_dispatch_bad)',
        'S_return_found = $modassign_right_seek(S_dispatch, 4, 2000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', '$modassign_right_frontier(S_return, 4)',
        'S_return.TODO = (' + marker(1) + ') :: ptask_tail*',
        'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
        '$lookup(S_return.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S_return.ENV, $ptascii("alias")) = (n_target)',
        '$lookup(S_return.ENV, $ptascii("right")) = (n_right)',
        'n_target <- S_return.REFCELLS', '~(n_right <- S_return.REFCELLS)',
        'S_return.STORE[n_target] = DEFINED (PINT 99)',
        'S_return.STORE[n_right] = DEFINED (PINT 5)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)',
        '$modassign_right_warning_valid(S_return, pintegeroperation, n_target, n_right, i_left, n_bits, i_right, 1)',
        '~$modassign_right_warning_valid(S_return, pintegeroperation, n_target, n_right, i_left, n_bits, i_right, 0)',
        '$powerassign_warning_ready(S_return, pintegeroperation, n_target)',
        '$long_mod(i_left, i_right) = INTZERO',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_target) = 2',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 1',
        '$modassign_right_review_deprecations(S_return.EVENTS) = 1',
        '(DIAGNOSTIC "Deprecated" ($ptascii("Implicit conversion from float 0.5 to int loses precision")) 16) <- S_return.EVENTS',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'S_error_budget = $drive_steps(S_return, 1)', 'S_error_budget.COMPLETION = BUDGET',
        'S_error = S_error_budget[.COMPLETION = NORMAL]', '$modassign_right_frontier(S_error, 6)',
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        'S_error.RESULT = KNOWN PNULL', 'S_error.CURRENT = eps', 'S_error.FRAMES = eps',
        '~$modassign_right_tasks(S_error.TODO)',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable',
        'pthrowable.KIND = "DivisionByZeroError"', 'pthrowable.ORIGIN = (pintegeroperation.SITE)',
        'n_error = |S_return.OBJECTS|',
        'S_error.OBJECTS = S_return.OBJECTS ++ [THROWABLE pthrowable]',
        '$throwable_field(S_error, n_error, "line") = PINT 16',
        '$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("Modulo by zero"))',
        '$throwable_previous_id(S_error, n_error) = eps', '$throwable_live(S_error, n_error)',
        '$heap_owners($heap_prune($heap_graph(S_error)), HOBJECT n_error) = 1',
        '$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]',
        'S_error.STORE = S_return.STORE', 'S_error.ENV = S_return.ENV',
        'S_error.REFCELLS = S_return.REFCELLS', 'S_error.EVENTS = S_return.EVENTS',
        'S_error.STORE[n_target] = DEFINED (PINT 99)',
        'S_error.STORE[n_right] = DEFINED (PINT 5)',
        'S_error.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_error)), HCELL n_target) = 2',
        '$heap_owners($heap_prune($heap_graph(S_error)), HCELL n_right) = 1',
        '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
        'S_done = $drive_steps(S_error, 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S_done.ENV, $ptascii("alias")) = (n_target)',
        'S_done.STORE[n_target] = DEFINED (PINT 7)',
        'S_done.STORE[n_right] = DEFINED (PINT 5)',
        'S_done.STORE[n_v] = DEFINED (PINT 100)',
        '$modassign_right_review_deprecations(S_done.EVENTS) = 1',
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
    report['review_scope'] = 'Actual cached LEFT12/RIGHT0 despite live RHS5: fresh caller DivisionByZeroError, unchanged target/alias/store, default Deprecated16, later write-through and budgets; production continuations only'
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
