#!/usr/bin/env python3
"""Genuine selected-scalar ADD failure and ordinary TypeError delivery."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import arithmetic_failure_cases as cases
import arithmetic_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS


def conditions(name, program, path, stdout):
    return [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $arithmetic_seek(S_initial, 5, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_right = S_found[.COMPLETION = NORMAL]', '$arithmetic_frontier(S_right, 5)',
        'S_right.TODO = (ARITHMETIC_ADD_CONVERT pintegeroperation (ARITHMETIC_RIGHT (NINT 12))) :: ptask_tail*',
        'pintegeroperation.OP = ADD', 'pintegeroperation.LINE = 11', '~pintegeroperation.SWAPPED',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_left',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_right', 'n_left =/= n_right',
        '$lookup(S_right.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_right.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_right.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_right.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_right.ENV, $ptascii("v")) = (n_v)',
        'S_right.STORE[n_left] = DEFINED (PBOOL true)',
        'S_right.STORE[n_right] = DEFINED pvalue_right',
        '$string_bytes(pvalue_right) = ($ptascii("notnumeric"))',
        'S_right.STORE[n_v] = DEFINED (PINT 100)',
        '$arithmetic_add_conversion(PBOOL true) = ((NINT 1, false))',
        '$arithmetic_add_conversion(pvalue_right) = eps',
        '$arithmetic_add_failure_operands(S_right, pintegeroperation, ARITHMETIC_RIGHT (NINT 12)) = ((PBOOL true, pvalue_right))',
        '$arithmetic_add_failure_operands(S_right, pintegeroperation, ARITHMETIC_LEFT) = eps',
        '$arithmetic_add_failure_operands(S_right, pintegeroperation[.OP = DIVIDE], ARITHMETIC_RIGHT (NINT 12)) = eps',
        '$arithmetic_add_failure_operands(S_right, pintegeroperation[.LINE = 12], ARITHMETIC_RIGHT (NINT 12)) = eps',
        '$arithmetic_add_failure_operands(S_right, pintegeroperation, ARITHMETIC_RIGHT (NINT 9223372036854775808)) = eps',
        '$arithmetic_add_failure_operands(S_right[.STORE[n_left] = UNDEFINED], pintegeroperation, ARITHMETIC_RIGHT (NINT 12)) = eps',
        '$arithmetic_add_failure_operands(S_right[.ORIGIN = eps], pintegeroperation, ARITHMETIC_RIGHT (NINT 12)) = eps',
        '$arithmetic_add_failure_operands(S_right[.CODE = eps], pintegeroperation, ARITHMETIC_RIGHT (NINT 12)) = eps',
        '$task_nodes(ARITHMETIC_ADD_CONVERT pintegeroperation (ARITHMETIC_RIGHT (NINT 12))) = eps',
        '$heap_owners($heap_prune($heap_graph(S_right)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_right)), HCELL n_right) = 2',
        '$integer_outputs(S_right.EVENTS) = ($ptascii("H:2:1:11;"))',
        '$call_descriptors_valid(S_right)', '$heap_valid($heap_graph(S_right))',
        'S_line_bad = S_right[.TODO = (ARITHMETIC_ADD_CONVERT (pintegeroperation[.LINE = 12]) (ARITHMETIC_RIGHT (NINT 12))) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_line_bad))', '~$call_descriptors_valid(S_line_bad)',
        'S_phase_bad = S_right[.TODO = (ARITHMETIC_ADD_CONVERT pintegeroperation (ARITHMETIC_RIGHT (NINT 9223372036854775808))) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_phase_bad))', '~$call_descriptors_valid(S_phase_bad)',
        'S_throw_budget = $drive_steps(S_right, 1)', 'S_throw_budget.COMPLETION = BUDGET',
        'S_throw = S_throw_budget[.COMPLETION = NORMAL]', '$arithmetic_frontier(S_throw, 9)',
        'S_throw.TODO = (THROW_SEARCH n_error) :: ptask_throw_tail*',
        'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps',
        'S_throw.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "TypeError"',
        'pthrowable.ORIGIN = (pintegeroperation.SITE)',
        '$throwable_field(S_throw, n_error, "line") = PINT 11',
        '$string_bytes($throwable_field(S_throw, n_error, "message")) = ($ptascii("Unsupported operand types: bool + string"))',
        '$throwable_previous_id(S_throw, n_error) = eps', '$throwable_live(S_throw, n_error)',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_error) = 1',
        '$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]',
        '~$arithmetic_tasks(S_throw.TODO)',
        'S_throw.STORE[n_left] = DEFINED (PBOOL true)', 'S_throw.STORE[n_right] = DEFINED pvalue_right',
        'S_throw.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_right) = 2',
        'S_throw.ERRORHANDLER = S_right.ERRORHANDLER',
        '$integer_outputs(S_throw.EVENTS) = ($ptascii("H:2:1:11;"))',
        '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
        'S_done = $drive_steps(S_throw, 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_right, 0) = S_right[.COMPLETION = BUDGET]',
        '$drive_steps(S_right, 2000) = S_done', '$drive_steps(S_throw, 0) = S_throw[.COMPLETION = BUDGET]',
    ]


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path, required=True)
    args, _ = parser.parse_known_args()
    watched = [Path(__file__), Path(cases.__file__), Path(shared.__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    shared.cases, shared.CASES, shared.HELPERS, shared.conditions = cases, CASES, HELPERS, conditions
    passed = shared.main()
    assert before == {str(path): digest(path) for path in watched}
    report = json.loads((args.output / 'report.json').read_bytes())
    report['failure_inputs'] = before
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
