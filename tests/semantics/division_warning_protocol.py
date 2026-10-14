#!/usr/bin/env python3
"""Production-reached division holders and the resulting caller Throwable."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import division_warning_cases as cases
import arithmetic_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $division_task(ptask) : bool
def $division_task(ARITHMETIC_DIV_CONVERT pintegeroperation parithmeticphase) = true
def $division_task(ARITHMETIC_DIV_WARNING pintegeroperation parithmeticphase pvalue pnumber n) = true
def $division_task(ERROR_HANDLER_INVOKE perrorcall) = $division_task(perrorcall.RESUME)
def $division_task(ERROR_HANDLER_RESULT perrorcall) = $division_task(perrorcall.RESUME)
def $division_task(ERROR_HANDLER_CLEAN perrorcall) = $division_task(perrorcall.RESUME)
def $division_task(ptask) = false -- otherwise
dec $division_tasks(ptask*) : bool
def $division_tasks(eps) = false
def $division_tasks(ptask :: ptask_tail*) = ($division_task(ptask) \/ $division_tasks(ptask_tail*))
dec $division_frontier(pstate, nat) : bool
def $division_frontier(S, 0) = ($arithmetic_div_plan(S) =/= eps)
def $division_frontier(S, 1) = true
  -- if S.TODO = (ARITHMETIC_DIV_CONVERT pintegeroperation ARITHMETIC_LEFT) :: ptask_tail*
def $division_frontier(S, 2) = true
  -- if S.TODO = (ARITHMETIC_DIV_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 0) :: ptask_tail*
def $division_frontier(S, 3) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_DIV_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 1
def $division_frontier(S, 4) = true
  -- if S.TODO = (ARITHMETIC_DIV_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 1) :: ptask_tail*
def $division_frontier(S, 5) = true
  -- if S.TODO = (ARITHMETIC_DIV_CONVERT pintegeroperation (ARITHMETIC_RIGHT pnumber)) :: ptask_tail*
def $division_frontier(S, 6) = true
  -- if S.TODO = (ARITHMETIC_DIV_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue pnumber_right 0) :: ptask_tail*
def $division_frontier(S, 7) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_DIV_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue pnumber_right 1
def $division_frontier(S, 8) = true
  -- if S.TODO = (ARITHMETIC_DIV_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue pnumber_right 1) :: ptask_tail*
def $division_frontier(S, 9) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if ~$division_tasks(S.TODO)
def $division_frontier(S, n) = false -- otherwise
dec $division_seek(pstate, nat, nat) : pstate
def $division_seek(S, n_stage, n) = S -- if $division_frontier(S, n_stage)
def $division_seek(S, n_stage, n) = S
  -- if ~$division_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $division_seek(S, n_stage, n) = S
  -- if ~$division_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $division_seek(S, n_stage, n) = $division_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$division_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    return [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $division_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]', '$division_frontier(S_entry, 0)',
        '$arithmetic_div_plan(S_entry) = (pintegeroperation)',
        '$arithmetic_div_valid(S_entry, pintegeroperation)',
        '$arithmetic_add_selected(S_entry, pintegeroperation)',
        'pintegeroperation.OP = DIVIDE', '~pintegeroperation.SWAPPED',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_left',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_right', 'n_left =/= n_right',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("rightAlias")) = (n_right)',
        '$integer_pointer_value(S_entry, pintegeroperation.LEFTPOINTER) = (pvalue_left)',
        '$string_bytes(pvalue_left) = ($ptascii("12tail"))',
        '$integer_pointer_value(S_entry, pintegeroperation.RIGHTPOINTER) = (PINT 2)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 2',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '~$arithmetic_div_valid(S_entry, pintegeroperation[.OP = ADD])',
        '~$arithmetic_div_valid(S_entry, pintegeroperation[.SWAPPED = true])',
        '~$arithmetic_div_valid(S_entry, pintegeroperation[.LINE = $(pintegeroperation.LINE + 1)])',
        '~$arithmetic_div_valid(S_entry, pintegeroperation[.LEFT = pintegeroperation.RIGHT])',
        '~$arithmetic_div_valid(S_entry[.ORIGIN = eps], pintegeroperation)',
        '~$arithmetic_div_valid(S_entry[.CODE = eps], pintegeroperation)',
        'pintegeroperation_other = pintegeroperation[.RIGHTPOINTER = INTEGER_CELL n_left]',
        'S_begin_budget = $drive_steps(S_entry, 1)', 'S_begin_budget.COMPLETION = BUDGET',
        'S_begin = S_begin_budget[.COMPLETION = NORMAL]',
        'S_begin.TODO = (ARITHMETIC_DIV_CONVERT pintegeroperation ARITHMETIC_LEFT) :: ptask_tail*',
        'S_begin.STORE = S_entry.STORE', 'S_begin.ALLOCATIONS = S_entry.ALLOCATIONS',
        '$task_nodes(ARITHMETIC_DIV_CONVERT pintegeroperation ARITHMETIC_LEFT) = eps',
        'S_other = S_begin[.TODO = (ARITHMETIC_DIV_CONVERT pintegeroperation_other ARITHMETIC_LEFT) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_other))', '~$call_descriptors_valid(S_other)',
        'S_phase_bad = S_begin[.TODO = (ARITHMETIC_DIV_CONVERT pintegeroperation (ARITHMETIC_RIGHT (NINT 9223372036854775808))) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_phase_bad))', '~$call_descriptors_valid(S_phase_bad)',
        '$call_descriptors_valid(S_begin)', '$heap_valid($heap_graph(S_begin))',
        'S_capture_budget = $drive_steps(S_begin, 1)', 'S_capture_budget.COMPLETION = BUDGET',
        'S_capture = S_capture_budget[.COMPLETION = NORMAL]',
        'S_capture.TODO = (ARITHMETIC_DIV_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_left (NINT 12) 0) :: ptask_tail*',
        '$arithmetic_div_warning_valid(S_capture, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NINT 12, 0)',
        '~$arithmetic_div_warning_valid(S_capture, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NINT 13, 0)',
        '~$arithmetic_div_warning_valid(S_capture, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NINT 12, 2)',
        'S_capture_bad = S_capture[.TODO = (ARITHMETIC_DIV_WARNING pintegeroperation ARITHMETIC_LEFT (PSTRING ($ptascii("99tail"))) (NINT 99) 0) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_capture_bad))', '~$call_descriptors_valid(S_capture_bad)',
        'S_capture.STORE = S_entry.STORE', 'S_capture.ALLOCATIONS = S_entry.ALLOCATIONS',
        '$task_nodes(ARITHMETIC_DIV_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_left (NINT 12) 0) = eps',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
        'S_dispatch_budget = $drive_steps(S_capture, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.TARGET = eps',
        'perrorcall.RESUME = ARITHMETIC_DIV_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_left (NINT 12) 1',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 8192])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        'perrorcall_bad = perrorcall[.RESUME = ARITHMETIC_DIV_WARNING pintegeroperation ARITHMETIC_LEFT (PSTRING ($ptascii("99tail"))) (NINT 99) 1]',
        'S_dispatch_bad = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall_bad) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_dispatch_bad))', '~$call_descriptors_valid(S_dispatch_bad)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'S_return_found = $division_seek(S_dispatch, 4, 2000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', '$division_frontier(S_return, 4)',
        'S_return.STORE[n_left] = DEFINED (PINT 99)', 'S_return.STORE[n_right] = DEFINED (PINT 0)',
        '$arithmetic_div_warning_valid(S_return, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NINT 12, 1)',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'S_right_budget = $drive_steps(S_return, 1)', 'S_right_budget.COMPLETION = BUDGET',
        'S_right = S_right_budget[.COMPLETION = NORMAL]',
        'S_right.TODO = (ARITHMETIC_DIV_CONVERT pintegeroperation (ARITHMETIC_RIGHT (NINT 12))) :: ptask_tail*',
        '$integer_pointer_value(S_right, pintegeroperation.RIGHTPOINTER) = (PINT 0)',
        '$task_nodes(ARITHMETIC_DIV_CONVERT pintegeroperation (ARITHMETIC_RIGHT (NINT 12))) = eps',
        '$call_descriptors_valid(S_right)', '$heap_valid($heap_graph(S_right))',
        'S_throw_budget = $drive_steps(S_right, 1)', 'S_throw_budget.COMPLETION = BUDGET',
        'S_throw = S_throw_budget[.COMPLETION = NORMAL]', '$division_frontier(S_throw, 9)',
        'S_throw.TODO = (THROW_SEARCH n_error) :: ptask_throw_tail*',
        'S_throw.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "DivisionByZeroError"',
        'pthrowable.ORIGIN = (pintegeroperation.SITE)',
        '$throwable_field(S_throw, n_error, "line") = PINT pintegeroperation.LINE',
        '$string_bytes($throwable_field(S_throw, n_error, "message")) = ($ptascii("Division by zero"))',
        '$throwable_previous_id(S_throw, n_error) = eps', '$throwable_live(S_throw, n_error)',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_error) = 1',
        '$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]',
        '~$division_tasks(S_throw.TODO)',
        '$lookup(S_throw.ENV, $ptascii("v")) = (n_v)', 'S_throw.STORE[n_v] = DEFINED (PINT 100)',
        'S_throw.STORE[n_left] = DEFINED (PINT 99)', 'S_throw.STORE[n_right] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_right) = 2',
        '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
        'S_done = $drive_steps(S_throw, 2000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_begin, 2000) = S_done', '$drive_steps(S_capture, 2000) = S_done',
    ]


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path, required=True)
    args, _ = parser.parse_known_args()
    watched = [Path(__file__), Path(cases.__file__), Path(shared.__file__)]
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    before = {str(p): digest(p) for p in watched}
    shared.cases, shared.CASES, shared.conditions, shared.HELPERS = cases, CASES, conditions, HELPERS
    passed = shared.main()
    assert before == {str(p): digest(p) for p in watched}
    report = json.loads((args.output / 'report.json').read_bytes())
    report['division_inputs'] = before
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
