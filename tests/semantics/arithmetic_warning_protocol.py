#!/usr/bin/env python3
"""Source-reached arithmetic holders, selected cells and warning cleanup."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import arithmetic_warning_cases as cases
import integer_operator_warning_protocol as runner

ROOT = Path(__file__).resolve().parents[2]
CASES = tuple(cases.CASES)
HELPERS = runner.HELPERS + r'''
dec $arithmetic_task(ptask) : bool
def $arithmetic_task(ARITHMETIC_ADD_CONVERT pintegeroperation parithmeticphase) = true
def $arithmetic_task(ARITHMETIC_ADD_WARNING pintegeroperation parithmeticphase pvalue pnumber n) = true
def $arithmetic_task(ERROR_HANDLER_INVOKE perrorcall) = $arithmetic_task(perrorcall.RESUME)
def $arithmetic_task(ERROR_HANDLER_RESULT perrorcall) = $arithmetic_task(perrorcall.RESUME)
def $arithmetic_task(ERROR_HANDLER_CLEAN perrorcall) = $arithmetic_task(perrorcall.RESUME)
def $arithmetic_task(ptask) = false -- otherwise
dec $arithmetic_tasks(ptask*) : bool
def $arithmetic_tasks(eps) = false
def $arithmetic_tasks(ptask :: ptask_tail*) = ($arithmetic_task(ptask) \/ $arithmetic_tasks(ptask_tail*))
dec $arithmetic_frontier(pstate, nat) : bool
def $arithmetic_frontier(S, 0) = ($arithmetic_add_plan(S) =/= eps)
def $arithmetic_frontier(S, 1) = true
  -- if S.TODO = (ARITHMETIC_ADD_CONVERT pintegeroperation ARITHMETIC_LEFT) :: ptask_tail*
def $arithmetic_frontier(S, 2) = true
  -- if S.TODO = (ARITHMETIC_ADD_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 0) :: ptask_tail*
def $arithmetic_frontier(S, 3) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_ADD_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 1
def $arithmetic_frontier(S, 4) = true
  -- if S.TODO = (ARITHMETIC_ADD_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 1) :: ptask_tail*
def $arithmetic_frontier(S, 5) = true
  -- if S.TODO = (ARITHMETIC_ADD_CONVERT pintegeroperation (ARITHMETIC_RIGHT pnumber)) :: ptask_tail*
def $arithmetic_frontier(S, 6) = true
  -- if S.TODO = (ARITHMETIC_ADD_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue pnumber_right 0) :: ptask_tail*
def $arithmetic_frontier(S, 7) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_ADD_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue pnumber_right 1
def $arithmetic_frontier(S, 8) = true
  -- if S.TODO = (ARITHMETIC_ADD_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue pnumber_right 1) :: ptask_tail*
def $arithmetic_frontier(S, 9) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if ~$arithmetic_tasks(S.TODO)
def $arithmetic_frontier(S, n) = false -- otherwise
dec $arithmetic_seek(pstate, nat, nat) : pstate
def $arithmetic_seek(S, n_stage, n) = S -- if $arithmetic_frontier(S, n_stage)
def $arithmetic_seek(S, n_stage, n) = S
  -- if ~$arithmetic_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $arithmetic_seek(S, n_stage, n) = S
  -- if ~$arithmetic_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $arithmetic_seek(S, n_stage, n) = $arithmetic_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$arithmetic_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    throws = name == CASES[1]
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_entry_found = $arithmetic_seek(S_initial, 0, 2000)',
        r'S_entry_found.COMPLETION = NORMAL \/ S_entry_found.COMPLETION = BUDGET',
        'S_entry = S_entry_found[.COMPLETION = NORMAL]',
        '$arithmetic_frontier(S_entry, 0)',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$arithmetic_add_plan(S_entry) = (pintegeroperation)',
        '$arithmetic_add_valid(S_entry, pintegeroperation)', '$arithmetic_add_selected(S_entry, pintegeroperation)',
        'pintegeroperation.OP = ADD', '~pintegeroperation.SWAPPED',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_left',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_right', 'n_left =/= n_right',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("rightAlias")) = (n_right)',
        'n_left <- S_entry.REFCELLS', 'n_right <- S_entry.REFCELLS',
        '$integer_pointer_value(S_entry, pintegeroperation.LEFTPOINTER) = (pvalue_left)',
        '$string_bytes(pvalue_left) = ($ptascii("12tail"))',
        '$integer_pointer_value(S_entry, pintegeroperation.RIGHTPOINTER) = (PINT 2)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 2',
        '~$arithmetic_add_valid(S_entry, pintegeroperation[.OP = SUBTRACT])',
        '~$arithmetic_add_valid(S_entry, pintegeroperation[.SWAPPED = true])',
        '~$arithmetic_add_valid(S_entry, pintegeroperation[.LINE = $(pintegeroperation.LINE + 1)])',
        '~$arithmetic_add_valid(S_entry, pintegeroperation[.LEFT = pintegeroperation.RIGHT])',
        '~$arithmetic_add_valid(S_entry[.ORIGIN = eps], pintegeroperation)',
        '~$arithmetic_add_valid(S_entry[.CODE = eps], pintegeroperation)',
        '~$arithmetic_add_phase_valid(ARITHMETIC_RIGHT (NINT 9223372036854775808))',
        '~$arithmetic_add_phase_valid(ARITHMETIC_RIGHT (NFLOAT 18446744073709551616))',
        'pintegeroperation_other = pintegeroperation[.RIGHTPOINTER = INTEGER_CELL n_left]',
        '~$arithmetic_add_selected(S_entry, pintegeroperation_other)',
        'S_begin_budget = $drive_steps(S_entry, 1)', 'S_begin_budget.COMPLETION = BUDGET',
        'S_begin = S_begin_budget[.COMPLETION = NORMAL]',
        'S_begin.TODO = (ARITHMETIC_ADD_CONVERT pintegeroperation ARITHMETIC_LEFT) :: ptask_tail*',
        'S_begin.STORE = S_entry.STORE', 'S_begin.ALLOCATIONS = S_entry.ALLOCATIONS',
        '$task_nodes(ARITHMETIC_ADD_CONVERT pintegeroperation ARITHMETIC_LEFT) = eps',
        '$call_task_valid(S_begin, ARITHMETIC_ADD_CONVERT pintegeroperation ARITHMETIC_LEFT)',
        '~$call_task_valid(S_begin, ARITHMETIC_ADD_CONVERT pintegeroperation_other ARITHMETIC_LEFT)',
        'S_other_pointer = S_begin[.TODO = (ARITHMETIC_ADD_CONVERT pintegeroperation_other ARITHMETIC_LEFT) :: ptask_tail*]',
        '~$call_descriptors_valid(S_other_pointer)',
        '$call_descriptors_valid(S_begin)', '$heap_valid($heap_graph(S_begin))',
        'S_capture_budget = $drive_steps(S_begin, 1)', 'S_capture_budget.COMPLETION = BUDGET',
        'S_capture = S_capture_budget[.COMPLETION = NORMAL]',
        'S_capture.TODO = (ARITHMETIC_ADD_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_left (NINT 12) 0) :: ptask_tail*',
        '$arithmetic_add_warning_valid(S_capture, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NINT 12, 0)',
        '~$arithmetic_add_warning_valid(S_capture, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NINT 13, 0)',
        '~$arithmetic_add_warning_valid(S_capture, pintegeroperation, ARITHMETIC_LEFT, PSTRING ($ptascii("99tail")), NINT 99, 0)',
        '~$arithmetic_add_warning_valid(S_capture, pintegeroperation_other, ARITHMETIC_LEFT, pvalue_left, NINT 12, 0)',
        '~$arithmetic_add_warning_valid(S_capture, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NINT 12, 2)',
        'S_other_capture = S_capture[.TODO = (ARITHMETIC_ADD_WARNING pintegeroperation ARITHMETIC_LEFT (PSTRING ($ptascii("99tail"))) (NINT 99) 0) :: ptask_tail*]',
        '~$call_descriptors_valid(S_other_capture)',
        'S_capture.STORE = S_entry.STORE', 'S_capture.ALLOCATIONS = S_entry.ALLOCATIONS',
        '$task_nodes(ARITHMETIC_ADD_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_left (NINT 12) 0) = eps',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
        'S_dispatch_budget = $drive_steps(S_capture, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.TARGET = eps',
        'perrorcall.RESUME = ARITHMETIC_ADD_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_left (NINT 12) 1',
        '$error_call_valid(S_dispatch, perrorcall)', '$call_descriptors_valid(S_dispatch)',
        '$heap_valid($heap_graph(S_dispatch))',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 8192])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        '~$error_call_valid(S_dispatch, perrorcall[.RESUME = ARITHMETIC_ADD_WARNING pintegeroperation ARITHMETIC_LEFT (PSTRING ($ptascii("99tail"))) (NINT 99) 1])',
        '~$error_call_valid(S_dispatch, perrorcall[.RESUME = ARITHMETIC_ADD_WARNING pintegeroperation_other ARITHMETIC_LEFT pvalue_left (NINT 12) 1])',
        'S_other_dispatch = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall[.RESUME = ARITHMETIC_ADD_WARNING pintegeroperation ARITHMETIC_LEFT (PSTRING ($ptascii("99tail"))) (NINT 99) 1]) :: ptask_tail*]',
        '~$call_descriptors_valid(S_other_dispatch)',
        'S_other_dispatch_pointer = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall[.RESUME = ARITHMETIC_ADD_WARNING pintegeroperation_other ARITHMETIC_LEFT pvalue_left (NINT 12) 1]) :: ptask_tail*]',
        '~$call_descriptors_valid(S_other_dispatch_pointer)',
        '$heap_owners($heap_prune($heap_graph(S_dispatch)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_dispatch)), HCELL n_right) = 2',
    ]
    if throws:
        checks += [
            'S_throw_found = $arithmetic_seek(S_dispatch, 9, 2000)',
            r'S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET',
            'S_throw = S_throw_found[.COMPLETION = NORMAL]',
            '$arithmetic_frontier(S_throw, 9)',
            'S_throw.TODO = (THROW_SEARCH n_second) :: ptask_throw_tail*',
            '$lookup(S_throw.ENV, $ptascii("second")) = (n_second_cell)',
            'S_throw.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            '$throwable_live(S_throw, n_second)', '$throwable_previous_id(S_throw, n_second) = eps',
            '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
            '~$arithmetic_tasks(S_throw.TODO)',
            '$lookup(S_throw.ENV, $ptascii("v")) = (n_v)', 'S_throw.STORE[n_v] = DEFINED (PINT 100)',
            'S_throw.STORE[n_left] = DEFINED (PINT 99)', 'S_throw.STORE[n_right] = DEFINED (PINT 5)',
            'S_throw.ERRORHANDLER = S_entry.ERRORHANDLER',
            '$integer_outputs(S_throw.EVENTS) = ($ptascii("H:2:1;"))',
            '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
            'S_done = $drive_steps(S_throw, 2000)',
            '$drive_steps(S_dispatch, 2000) = S_done',
        ]
    else:
        checks += [
            'S_return_found = $arithmetic_seek(S_dispatch, 4, 2000)',
            r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
            'S_return = S_return_found[.COMPLETION = NORMAL]',
            '$arithmetic_frontier(S_return, 4)',
            'S_return.TODO = (ARITHMETIC_ADD_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_left (NINT 12) 1) :: ptask_tail*',
            'S_return.STORE[n_left] = DEFINED (PINT 99)', 'S_return.STORE[n_right] = DEFINED (PINT 5)',
            '$arithmetic_add_warning_valid(S_return, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NINT 12, 1)',
            '$integer_pointer_value(S_return, pintegeroperation.LEFTPOINTER) = (PINT 99)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_left) = 2',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 2',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
            'S_right_budget = $drive_steps(S_return, 1)', 'S_right_budget.COMPLETION = BUDGET',
            'S_right = S_right_budget[.COMPLETION = NORMAL]',
            'S_right.TODO = (ARITHMETIC_ADD_CONVERT pintegeroperation (ARITHMETIC_RIGHT (NINT 12))) :: ptask_tail*',
            '$integer_pointer_value(S_right, pintegeroperation.RIGHTPOINTER) = (PINT 5)',
            '$call_descriptors_valid(S_right)', '$heap_valid($heap_graph(S_right))',
            'S_result_budget = $drive_steps(S_right, 1)', 'S_result_budget.COMPLETION = BUDGET',
            'S_result = S_result_budget[.COMPLETION = NORMAL]',
            'S_result.TODO = ptask_tail*', 'S_result.RESULT = KNOWN (PINT 17)',
            'S_result.STORE = S_right.STORE', 'S_result.ALLOCATIONS = S_right.ALLOCATIONS',
            '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
            'S_done = $drive_steps(S_result, 2000)',
            '$drive_steps(S_dispatch, 2000) = S_done',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_begin, 2000) = S_done', '$drive_steps(S_capture, 2000) = S_done',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path)
    args, _ = parser.parse_known_args()
    out = args.output
    if out is None:
        out = Path(tempfile.mkdtemp(prefix='arithmetic-warning-', dir=ROOT / '.tools'))
        sys.argv += ['--output', str(out)]
    watched = [Path(__file__), Path(cases.__file__), Path(runner.__file__),
               ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/recorded_worker.py',
               ROOT / 'tests/semantics/error_handler_run.py', ROOT / '.tools/php/bin/php',
               ROOT / '.tools/php-file.so', ROOT / '_build/default/adapter/main.exe']
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    before = {str(p): digest(p) for p in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT) == b''
    runner.CASES, runner.HELPERS, runner.conditions = CASES, HELPERS, conditions
    runner.sources, runner.__file__ = cases, __file__
    passed = runner.main()
    assert before == {str(p): digest(p) for p in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    assert subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT) == b''
    report = json.loads((out / 'report.json').read_bytes())
    report['revision'], report['helper_inputs'] = revision, before
    for row in report['rows']:
        assert row['native']['interruption'] is None and row['native']['group_after'] == []
        if 'model' in row:
            result = row['model']
            row['passed'] = row['passed'] and result['interruption'] is None and result['group_after'] == []
            row['passed'] = row['passed'] and (out / (row['id'] + '-model.stdout')).read_bytes() == b'true\n'
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed and all(row.get('passed', True) for row in report['rows'])


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
