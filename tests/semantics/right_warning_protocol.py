#!/usr/bin/env python3
"""Reached quiet-LEFT/right-warning entry into existing arithmetic continuations."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import right_warning_cases as cases
import arithmetic_warning_protocol as shared
import integer_operator_warning_protocol as prior
import division_warning_protocol as division
import submul_warning_protocol as submul
import power_conversion_protocol as power

CASES = ('right-warning-add-cached',)
assert submul.HELPERS.startswith(prior.HELPERS) and power.HELPERS.startswith(prior.HELPERS)
HELPERS = division.HELPERS + submul.HELPERS[len(prior.HELPERS):] + power.HELPERS[len(prior.HELPERS):]


def conditions(name, program, path, stdout):
    return [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_entry_found = $arithmetic_seek(S_initial, 0, 5000)',
        r'S_entry_found.COMPLETION = NORMAL \/ S_entry_found.COMPLETION = BUDGET',
        'S_entry = S_entry_found[.COMPLETION = NORMAL]', '$arithmetic_frontier(S_entry, 0)',
        '$arithmetic_right_warning_operation(S_entry) = (pintegeroperation)',
        '$arithmetic_add_plan(S_entry) = (pintegeroperation)', '$arithmetic_add_valid(S_entry, pintegeroperation)',
        '$arithmetic_add_selected(S_entry, pintegeroperation)', 'pintegeroperation.OP = ADD', '~pintegeroperation.SWAPPED',
        'pintegeroperation.LINE = 25', 'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_left', 'pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_right', 'n_left =/= n_right',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)', '$lookup(S_entry.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)', '$lookup(S_entry.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)', '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        'S_entry.STORE[n_left] = DEFINED (PINT 12)', 'S_entry.STORE[n_right] = DEFINED pvalue_right',
        '$string_bytes(pvalue_right) = ($ptascii("5tail"))',
        '$arithmetic_add_conversion(PINT 12) = ((NINT 12, false))', '$arithmetic_add_conversion(pvalue_right) = ((NINT 5, true))',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)', 'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 2',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$arithmetic_right_warning_operation(S_entry[.REFCELLS = eps]) = eps',
        '$arithmetic_right_warning_operation(S_entry[.ALLOCATIONS = eps]) = eps',
        '$arithmetic_right_warning_operation(S_entry[.ENV = eps]) = eps',
        '$arithmetic_right_warning_operation(S_entry[.ORIGIN = eps]) = eps',
        '$arithmetic_right_warning_operation(S_entry[.CODE = eps]) = eps',
        '$arithmetic_right_warning_operation(S_entry[.STORE[n_left] = DEFINED PUNDEFINED]) = eps',
        '$arithmetic_right_warning_operation(S_entry[.STORE[n_left] = DEFINED (PARRAY 0)]) = eps',
        '$arithmetic_right_warning_operation(S_entry[.STORE[n_left] = DEFINED (PSTRING ($ptascii("12tail")))]) = eps',
        '$arithmetic_right_warning_operation(S_entry[.STORE[n_right] = DEFINED (PINT 5)]) = eps',
        '$arithmetic_right_warning_operation(S_entry[.STORE[n_right] = DEFINED (PSTRING ($ptascii("bad")))]) = eps',
        '$arithmetic_right_warning_operation(S_entry[.STORE[n_right] = DEFINED (PSTRING_CARRIER (REQUEST_STRING (|S_entry.STRINGDATA|)) ($ptascii("5tail")))]) = eps',
        'S_begin_budget = $drive_steps(S_entry, 1)', 'S_begin_budget.COMPLETION = BUDGET',
        'S_begin = S_begin_budget[.COMPLETION = NORMAL]', '$arithmetic_frontier(S_begin, 1)',
        'S_entry.TODO = ptask_old :: ptask_tail*',
        'S_begin = S_entry[.TODO = (ARITHMETIC_ADD_CONVERT pintegeroperation ARITHMETIC_LEFT) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$call_task_valid(S_begin, ARITHMETIC_ADD_CONVERT pintegeroperation ARITHMETIC_LEFT)',
        '$task_nodes(ARITHMETIC_ADD_CONVERT pintegeroperation ARITHMETIC_LEFT) = eps',
        'S_quiet_budget = $drive_steps(S_begin, 1)', 'S_quiet_budget.COMPLETION = BUDGET',
        'S_quiet = S_quiet_budget[.COMPLETION = NORMAL]', '$arithmetic_frontier(S_quiet, 5)', '~$arithmetic_frontier(S_quiet, 2)',
        'S_quiet = S_begin[.TODO = (ARITHMETIC_ADD_CONVERT pintegeroperation (ARITHMETIC_RIGHT (NINT 12))) :: ptask_tail*][.RESULT = KNOWN PNULL]',
        'S_quiet.STORE[n_calls] = DEFINED (PINT 0)',
        '$call_task_valid(S_quiet, ARITHMETIC_ADD_CONVERT pintegeroperation (ARITHMETIC_RIGHT (NINT 12)))',
        'S_capture_budget = $drive_steps(S_quiet, 1)', 'S_capture_budget.COMPLETION = BUDGET',
        'S_capture = S_capture_budget[.COMPLETION = NORMAL]', '$arithmetic_frontier(S_capture, 6)',
        'S_capture = S_quiet[.TODO = (ARITHMETIC_ADD_WARNING pintegeroperation (ARITHMETIC_RIGHT (NINT 12)) pvalue_right (NINT 5) 0) :: ptask_tail*]',
        '$arithmetic_add_warning_valid(S_capture, pintegeroperation, ARITHMETIC_RIGHT (NINT 12), pvalue_right, NINT 5, 0)',
        '$task_nodes(ARITHMETIC_ADD_WARNING pintegeroperation (ARITHMETIC_RIGHT (NINT 12)) pvalue_right (NINT 5) 0) = eps',
        'S_dispatch_budget = $drive_steps(S_capture, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]', '$arithmetic_frontier(S_dispatch, 7)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ARITHMETIC_ADD_WARNING pintegeroperation (ARITHMETIC_RIGHT (NINT 12)) pvalue_right (NINT 5) 1',
        'perrorcall.TARGET = eps', 'perrorcall.LEVEL = 2', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = $ptascii("A non-numeric value encountered")', '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.RESUME = ARITHMETIC_ADD_WARNING pintegeroperation (ARITHMETIC_RIGHT (NINT 12)) (PSTRING ($ptascii("6tail"))) (NINT 6) 1])',
        'S_return_found = $arithmetic_seek(S_dispatch, 8, 5000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', '$arithmetic_frontier(S_return, 8)',
        'S_return.TODO = (ARITHMETIC_ADD_WARNING pintegeroperation (ARITHMETIC_RIGHT (NINT 12)) pvalue_right (NINT 5) 1) :: ptask_tail*',
        'S_return.STORE[n_left] = DEFINED (PINT 99)', 'S_return.STORE[n_right] = DEFINED (PINT 7)',
        'S_return.STORE[n_calls] = DEFINED (PINT 1)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
        '$arithmetic_add_warning_valid(S_return, pintegeroperation, ARITHMETIC_RIGHT (NINT 12), pvalue_right, NINT 5, 1)',
        '~$arithmetic_add_warning_valid(S_return, pintegeroperation, ARITHMETIC_RIGHT (NINT 12), pvalue_right, NINT 5, 0)',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'S_result_budget = $drive_steps(S_return, 1)', 'S_result_budget.COMPLETION = BUDGET',
        'S_result = S_result_budget[.COMPLETION = NORMAL]',
        'S_result = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (PINT 17)]',
        '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_right) = 2',
        '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 5000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_v] = DEFINED (PINT 17)', 'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_left)', '$lookup(S_done.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_done.ENV, $ptascii("right")) = (n_right)', '$lookup(S_done.ENV, $ptascii("rightAlias")) = (n_right)',
        'S_done.STORE[n_left] = DEFINED (PINT 1)', 'S_done.STORE[n_right] = DEFINED (PINT 2)',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_entry, 6000) = S_done', '$drive_steps(S_dispatch, 0) = S_dispatch[.COMPLETION = BUDGET]',
    ]


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path, required=True)
    args, _ = parser.parse_known_args()
    watched = [Path(__file__), Path(cases.__file__), Path(shared.__file__), Path(prior.__file__),
               Path(division.__file__), Path(submul.__file__), Path(power.__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    shared.cases, shared.CASES, shared.HELPERS, shared.conditions = cases, CASES, HELPERS, conditions
    passed = shared.main()
    assert before == {str(path): digest(path) for path in watched}
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
