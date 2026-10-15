#!/usr/bin/env python3
"""Reached fractional-RHS modulo capture, late-alias stores and cancellation."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import modassign_right_warning_cases as cases
import arithmetic_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $modassign_right_task(ptask) : bool
def $modassign_right_task(MOD_ASSIGN_RIGHT_WARNING pintegeroperation n_target n_right i_left n_bits i_right n_stage) = true
def $modassign_right_task(ERROR_HANDLER_INVOKE perrorcall) = $modassign_right_task(perrorcall.RESUME)
def $modassign_right_task(ERROR_HANDLER_RESULT perrorcall) = $modassign_right_task(perrorcall.RESUME)
def $modassign_right_task(ERROR_HANDLER_CLEAN perrorcall) = $modassign_right_task(perrorcall.RESUME)
def $modassign_right_task(ptask) = false -- otherwise
dec $modassign_right_tasks(ptask*) : bool
def $modassign_right_tasks(eps) = false
def $modassign_right_tasks(ptask :: ptask_tail*) = ($modassign_right_task(ptask) \/ $modassign_right_tasks(ptask_tail*))
dec $modassign_right_handler_frame(pframe) : bool
def $modassign_right_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = MOD_ASSIGN_RIGHT_WARNING pintegeroperation n_target n_right i_left n_bits i_right 1
  -- if perrorcall.TARGET =/= eps
def $modassign_right_handler_frame(pframe) = false -- otherwise
dec $modassign_right_entered(pframe*) : bool
def $modassign_right_entered(eps) = false
def $modassign_right_entered(pframe :: pframe_tail*) = ($modassign_right_handler_frame(pframe) \/ $modassign_right_entered(pframe_tail*))
dec $modassign_right_frontier(pstate, nat) : bool
def $modassign_right_frontier(S, 0) = ($modassign_right_warning_plan(S) =/= eps)
def $modassign_right_frontier(S, 1) = true
  -- if S.TODO = (MOD_ASSIGN_RIGHT_WARNING pintegeroperation n_target n_right i_left n_bits i_right 0) :: ptask_tail*
def $modassign_right_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = MOD_ASSIGN_RIGHT_WARNING pintegeroperation n_target n_right i_left n_bits i_right 1
  -- if perrorcall.TARGET = eps
def $modassign_right_frontier(S, 3) = (S.CURRENT =/= eps /\ $modassign_right_entered(S.FRAMES))
def $modassign_right_frontier(S, 4) = true
  -- if S.TODO = (MOD_ASSIGN_RIGHT_WARNING pintegeroperation n_target n_right i_left n_bits i_right 1) :: ptask_tail*
def $modassign_right_frontier(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprAssignOpMod expression_left expression_right metadata)
  -- if S.RESULT = KNOWN (PINT i)
  -- if ~$modassign_right_tasks(S.TODO)
def $modassign_right_frontier(S, 6) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if ~$modassign_right_tasks(S.TODO)
def $modassign_right_frontier(S, n) = false -- otherwise
dec $modassign_right_seek(pstate, nat, nat) : pstate
def $modassign_right_seek(S, n_stage, n) = S -- if $modassign_right_frontier(S, n_stage)
def $modassign_right_seek(S, n_stage, n) = S
  -- if ~$modassign_right_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $modassign_right_seek(S, n_stage, n) = S
  -- if ~$modassign_right_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $modassign_right_seek(S, n_stage, n) = $modassign_right_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$modassign_right_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    thrown = name.endswith('-throw')
    line = 14 if thrown else 13
    marker = lambda stage, target='n_target', left='12', bits='n_bits', right='5', op='pintegeroperation': f'MOD_ASSIGN_RIGHT_WARNING {op} {target} n_right {left} {bits} {right} {stage}'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $modassign_right_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]', '$modassign_right_frontier(S_entry, 0)',
        '$modassign_right_warning_plan(S_entry) = (' + marker(0) + ')',
        'n_bits = 4617878467915022336', 'pintegeroperation.OP = MODULO', '~pintegeroperation.SWAPPED',
        'pintegeroperation.LINE = ' + str(line),
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) ' + str(line - 1),
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) ' + str(line),
        'pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("left"))',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)', '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'S_entry.STORE[n_target] = DEFINED (PINT 12)', 'S_entry.STORE[n_right] = DEFINED (PFLOAT n_bits)',
        '~(n_target <- S_entry.REFCELLS)', '~(n_right <- S_entry.REFCELLS)',
        '$modassign_right_warning_snapshot(S_entry, pintegeroperation, n_target, n_right, 12, n_bits)',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$modassign_right_warning_plan(S_entry[.REFCELLS = S_entry.REFCELLS ++ [n_target]]) = eps',
        '$modassign_right_warning_plan(S_entry[.REFCELLS = S_entry.REFCELLS ++ [n_right]]) = eps',
        'S_capture_budget = $drive_steps(S_entry, 1)', 'S_capture_budget.COMPLETION = BUDGET',
        'S_capture = S_capture_budget[.COMPLETION = NORMAL]', '$modassign_right_frontier(S_capture, 1)',
        'S_capture.TODO = (' + marker(0) + ') :: ptask_tail*',
        'S_capture.RESULT = KNOWN PNULL', 'S_capture.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_capture.LOCATION = ROOT n_target', '$task_nodes(' + marker(0) + ') = eps',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_right) = 1',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
        'pintegeroperation_line = pintegeroperation[.LINE = ' + str(line - 1) + ']',
        'S_line_bad = S_capture[.TODO = (' + marker(0, op='pintegeroperation_line') + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_line_bad))', '~$call_descriptors_valid(S_line_bad)',
        'S_target_bad = S_capture[.TODO = (' + marker(0, target='n_v') + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_target_bad))', '~$call_descriptors_valid(S_target_bad)',
        'S_range_bad = S_capture[.TODO = (' + marker(1, bits='18446744073709551616') + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_range_bad))', '~$call_descriptors_valid(S_range_bad)',
        'S_left_bad = S_capture[.TODO = (' + marker(1, left='9223372036854775808') + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_left_bad))', '~$call_descriptors_valid(S_left_bad)',
        'S_dispatch_budget = $drive_steps(S_capture, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]', '$modassign_right_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(1), 'perrorcall.TARGET = eps',
        'perrorcall.LEVEL = 8192', 'perrorcall.LINE = ' + str(line),
        '$error_call_valid(S_dispatch, perrorcall)', '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'perrorcall_left = perrorcall[.RESUME = ' + marker(1, left='13') + ']',
        '$modassign_right_warning_valid(S_dispatch, pintegeroperation, n_target, n_right, 13, n_bits, 5, 1)',
        '~$error_call_valid(S_dispatch, perrorcall_left)',
        'S_dispatch_left = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall_left) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_dispatch_left))', '~$call_descriptors_valid(S_dispatch_left)',
        'n_message_bad* = $ptascii("Implicit conversion from float 6.5 to int loses precision")',
        'perrorcall_right = perrorcall[.RESUME = ' + marker(1, bits='4619004367821864960', right='6') + '][.MESSAGE = n_message_bad*][.EVENT = DIAGNOSTIC "Deprecated" n_message_bad* ' + str(line) + ']',
        '$modassign_right_warning_valid(S_dispatch, pintegeroperation, n_target, n_right, 12, 4619004367821864960, 6, 1)',
        '~$error_call_valid(S_dispatch, perrorcall_right)',
        'S_dispatch_right = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall_right) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_dispatch_right))', '~$call_descriptors_valid(S_dispatch_right)',
        'S_entered_found = $modassign_right_seek(S_dispatch, 3, 2000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', '$modassign_right_frontier(S_entered, 3)',
        '$modassign_right_entered(S_entered.FRAMES)', '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if thrown:
        checks += [
            '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
            'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            '~$powerassign_warning_ready(S_capture[.STORE[n_target] = DEFINED (POBJECT n_second)], pintegeroperation, n_target)',
            'S_throw_found = $modassign_right_seek(S_entered, 6, 2000)',
            r'S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET',
            'S_throw = S_throw_found[.COMPLETION = NORMAL]', '$modassign_right_frontier(S_throw, 6)',
            'S_throw.TODO = (THROW_SEARCH n_second) :: ptask_throw*',
            'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps', '~$modassign_right_tasks(S_throw.TODO)',
            '$lookup(S_throw.ENV, $ptascii("left")) = (n_target)', '$lookup(S_throw.ENV, $ptascii("alias")) = (n_target)',
            'n_target <- S_throw.REFCELLS', 'S_throw.STORE[n_target] = DEFINED (PINT 99)',
            'S_throw.STORE[n_right] = DEFINED (PINT 7)', 'S_throw.STORE[n_v] = DEFINED (PINT 100)',
            '$throwable_live(S_throw, n_second)', '$throwable_previous_id(S_throw, n_second) = eps',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_target) = 2',
            'S_throw.ERRORHANDLER = S_entry.ERRORHANDLER', '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
            'S_done = $drive_steps(S_throw, 2000)', '$drive_steps(S_dispatch, 2000) = S_done',
            '$lookup(S_done.ENV, $ptascii("left")) = (n_target)', '$lookup(S_done.ENV, $ptascii("alias")) = (n_target)',
            'S_done.STORE[n_target] = DEFINED (PINT 7)', 'S_done.STORE[n_v] = DEFINED (PINT 100)',
        ]
    else:
        checks += [
            'S_return_found = $modassign_right_seek(S_entered, 4, 2000)',
            r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
            'S_return = S_return_found[.COMPLETION = NORMAL]', '$modassign_right_frontier(S_return, 4)',
            'S_return.TODO = (' + marker(1) + ') :: ptask_tail*',
            'S_return.STORE[n_target] = DEFINED (PINT 99)', 'S_return.STORE[n_right] = DEFINED (PINT 7)',
            'S_return.STORE[n_v] = DEFINED (PINT 100)',
            '$lookup(S_return.ENV, $ptascii("alias")) = (n_target)', 'n_target <- S_return.REFCELLS',
            '$modassign_right_warning_valid(S_return, pintegeroperation, n_target, n_right, 12, n_bits, 5, 1)',
            '~$modassign_right_warning_snapshot(S_return, pintegeroperation, n_target, n_right, 12, n_bits)',
            '$powerassign_warning_ready(S_return, pintegeroperation, n_target)',
            '~$powerassign_warning_ready(S_return[.ALLOCATIONS = eps], pintegeroperation, n_target)',
            '~$powerassign_warning_ready(S_return, pintegeroperation, n_v)',
            '~$powerassign_warning_ready(S_return[.ENV = eps][.GLOBALTABLE = eps], pintegeroperation, n_target)',
            '~$powerassign_warning_ready(S_return[.PROPREFS = [{CELL n_target, SOURCES eps}]], pintegeroperation, n_target)',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
            'S_commit_budget = $drive_steps(S_return, 1)', 'S_commit_budget.COMPLETION = BUDGET',
            'S_commit = S_commit_budget[.COMPLETION = NORMAL]', '$modassign_right_frontier(S_commit, 5)',
            'S_commit.TODO = ptask_tail*', 'S_commit.RESULT = KNOWN (PINT 2)',
            '$lookup(S_commit.ENV, $ptascii("left")) = (n_new)', 'n_new = |S_return.STORE|',
            'S_commit.CELL = n_new', 'S_commit.LOCATION = ROOT n_new', '~(n_new <- S_commit.REFCELLS)',
            '$lookup(S_commit.ENV, $ptascii("alias")) = (n_target)',
            'S_commit.STORE = S_return.STORE ++ [DEFINED (PINT 2)]',
            'S_commit.ALLOCATIONS = S_return.ALLOCATIONS ++ [HCELL n_new]',
            'S_commit.STORE[n_target] = DEFINED (PINT 99)', 'S_commit.STORE[n_v] = DEFINED (PINT 100)',
            '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_target) = 1',
            '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_new) = 1',
            'S_commit.EVENTS = S_return.EVENTS',
            '$call_descriptors_valid(S_commit)', '$heap_valid($heap_graph(S_commit))',
            'S_done = $drive_steps(S_commit, 2000)', '$drive_steps(S_return, 2000) = S_done',
            'S_done.STORE[n_new] = DEFINED (PINT 7)', 'S_done.STORE[n_target] = DEFINED (PINT 99)',
            'S_done.STORE[n_v] = DEFINED (PINT 2)',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_right] = DEFINED (PINT 7)', '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]', '$drive_steps(S_capture, 2000) = S_done',
    ]
    return checks


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
    report['modassign_right_inputs'] = before
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
