#!/usr/bin/env python3
"""Reached power-assignment capture, normal store and pending-throw store fronts."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import powerassign_warning_cases as cases
import arithmetic_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $powerassign_task(ptask) : bool
def $powerassign_task(POWER_ASSIGN_WARNING pintegeroperation n_target pnumber_left pnumber_right n_stage n_pending?) = true
def $powerassign_task(ERROR_HANDLER_INVOKE perrorcall) = $powerassign_task(perrorcall.RESUME)
def $powerassign_task(ERROR_HANDLER_RESULT perrorcall) = $powerassign_task(perrorcall.RESUME)
def $powerassign_task(ERROR_HANDLER_CLEAN perrorcall) = $powerassign_task(perrorcall.RESUME)
def $powerassign_task(ptask) = false -- otherwise
dec $powerassign_tasks(ptask*) : bool
def $powerassign_tasks(eps) = false
def $powerassign_tasks(ptask :: ptask_tail*) = ($powerassign_task(ptask) \/ $powerassign_tasks(ptask_tail*))
dec $powerassign_handler_frame(pframe) : bool
def $powerassign_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = POWER_ASSIGN_WARNING pintegeroperation n_target pnumber_left pnumber_right 1 eps
  -- if perrorcall.TARGET =/= eps
def $powerassign_handler_frame(pframe) = false -- otherwise
dec $powerassign_entered(pframe*) : bool
def $powerassign_entered(eps) = false
def $powerassign_entered(pframe :: pframe_tail*) = ($powerassign_handler_frame(pframe) \/ $powerassign_entered(pframe_tail*))
dec $powerassign_frontier(pstate, nat) : bool
def $powerassign_frontier(S, 0) = ($powerassign_warning_plan(S) =/= eps)
def $powerassign_frontier(S, 1) = true
  -- if S.TODO = (POWER_ASSIGN_WARNING pintegeroperation n_target pnumber_left pnumber_right 0 eps) :: ptask_tail*
def $powerassign_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = POWER_ASSIGN_WARNING pintegeroperation n_target pnumber_left pnumber_right 1 eps
  -- if perrorcall.TARGET = eps
def $powerassign_frontier(S, 3) = (S.CURRENT =/= eps /\ $powerassign_entered(S.FRAMES))
def $powerassign_frontier(S, 4) = true
  -- if S.TODO = (POWER_ASSIGN_WARNING pintegeroperation n_target pnumber_left pnumber_right 1 eps) :: ptask_tail*
def $powerassign_frontier(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprAssignOpPow expression_left expression_right metadata)
  -- if S.RESULT = KNOWN (PFLOAT n)
  -- if ~$powerassign_tasks(S.TODO)
def $powerassign_frontier(S, 6) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if ~$powerassign_tasks(S.TODO)
def $powerassign_frontier(S, 7) = true
  -- if S.TODO = (POWER_ASSIGN_WARNING pintegeroperation n_target pnumber_left pnumber_right 1 (n_exception)) :: ptask_tail*
def $powerassign_frontier(S, n) = false -- otherwise
dec $powerassign_seek(pstate, nat, nat) : pstate
def $powerassign_seek(S, n_stage, n) = S -- if $powerassign_frontier(S, n_stage)
def $powerassign_seek(S, n_stage, n) = S
  -- if ~$powerassign_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $powerassign_seek(S, n_stage, n) = S
  -- if ~$powerassign_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $powerassign_seek(S, n_stage, n) = $powerassign_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$powerassign_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    thrown = name.endswith('-throw')
    line = 14 if thrown else 12
    marker = lambda stage, target='n_target', base='(NINT 0)', exponent='(NINT (-2))', pending='eps', op='pintegeroperation': f'POWER_ASSIGN_WARNING {op} {target} {base} {exponent} {stage} {pending}'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $powerassign_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]', '$powerassign_frontier(S_entry, 0)',
        '$powerassign_warning_plan(S_entry) = (' + marker(0) + ')',
        'pintegeroperation.OP = POWER', '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = ' + str(line),
        'pintegeroperation.LEFT = VARIABLE ($ptascii("base")) ' + str(line - 1),
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("exponent")) ' + str(line),
        'pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("base"))',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("exponent"))',
        '$lookup(S_entry.ENV, $ptascii("base")) = (n_target)',
        '$lookup(S_entry.ENV, $ptascii("exponent")) = (n_exponent)', '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'S_entry.STORE[n_target] = DEFINED (PINT 0)', 'S_entry.STORE[n_exponent] = DEFINED (PINT (-2))',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)', '~(n_target <- S_entry.REFCELLS)', '~(n_exponent <- S_entry.REFCELLS)',
        '$powerassign_warning_source(S_entry, pintegeroperation)',
        '$powerassign_warning_snapshot(S_entry, pintegeroperation, n_target, NINT 0, NINT (-2))',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$powerassign_warning_plan(S_entry[.REFCELLS = S_entry.REFCELLS ++ [n_target]]) = eps',
        '$powerassign_warning_plan(S_entry[.STORE[n_exponent] = UNDEFINED]) = eps',
        'S_capture_budget = $drive_steps(S_entry, 1)', 'S_capture_budget.COMPLETION = BUDGET',
        'S_capture = S_capture_budget[.COMPLETION = NORMAL]', '$powerassign_frontier(S_capture, 1)',
        'S_capture.TODO = (' + marker(0) + ') :: ptask_tail*',
        'S_capture.RESULT = KNOWN PNULL', 'S_capture.BASE = BASE_VALUE (KNOWN PNULL)', 'S_capture.LOCATION = ROOT n_target',
        '$task_nodes(' + marker(0) + ') = eps',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_exponent) = 1',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
        'pintegeroperation_line = pintegeroperation[.LINE = ' + str(line - 1) + ']',
        'S_line_bad = S_capture[.TODO = (' + marker(0, op='pintegeroperation_line') + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_line_bad))', '~$call_descriptors_valid(S_line_bad)',
        'pintegeroperation_op = pintegeroperation[.OP = ADD]',
        'S_op_bad = S_capture[.TODO = (' + marker(0, op='pintegeroperation_op') + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_op_bad))', '~$call_descriptors_valid(S_op_bad)',
        'S_target_bad = S_capture[.TODO = (' + marker(0, target='n_exponent') + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_target_bad))', '~$call_descriptors_valid(S_target_bad)',
        'S_number_bad = S_capture[.TODO = (' + marker(0, base='(NFLOAT 0)') + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_number_bad))', '~$call_descriptors_valid(S_number_bad)',
        'S_range_bad = S_capture[.TODO = (' + marker(1, exponent='(NINT (-9223372036854775809))') + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_range_bad))', '~$call_descriptors_valid(S_range_bad)',
        'S_dispatch_budget = $drive_steps(S_capture, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]', '$powerassign_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(1), 'perrorcall.TARGET = eps',
        'perrorcall.SITE = pintegeroperation.SITE', 'perrorcall.LINE = ' + str(line), 'perrorcall.LEVEL = 8192',
        '$error_call_valid(S_dispatch, perrorcall)', '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'perrorcall_number = perrorcall[.RESUME = ' + marker(1, exponent='(NINT (-3))') + ']',
        '~$error_call_valid(S_dispatch, perrorcall_number)',
        'S_dispatch_number = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall_number) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_dispatch_number))', '~$call_descriptors_valid(S_dispatch_number)',
        'perrorcall_message = perrorcall[.MESSAGE = eps][.EVENT = DIAGNOSTIC "Deprecated" eps ' + str(line) + ']',
        '~$error_call_valid(S_dispatch, perrorcall_message)',
        'S_dispatch_message = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall_message) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_dispatch_message))', '~$call_descriptors_valid(S_dispatch_message)',
        'S_entered_found = $powerassign_seek(S_dispatch, 3, 2000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', '$powerassign_frontier(S_entered, 3)',
        '$powerassign_entered(S_entered.FRAMES)', '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if thrown:
        checks += [
            '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)', 'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            'S_pending_bad = S_capture[.TODO = (' + marker(0, pending='(n_second)') + ') :: ptask_tail*]',
            '$heap_valid($heap_graph(S_pending_bad))', '~$call_descriptors_valid(S_pending_bad)',
            'S_pending_found = $powerassign_seek(S_entered, 7, 2000)',
            r'S_pending_found.COMPLETION = NORMAL \/ S_pending_found.COMPLETION = BUDGET',
            'S_pending = S_pending_found[.COMPLETION = NORMAL]', '$powerassign_frontier(S_pending, 7)',
            'S_pending.TODO = (' + marker(1, pending='(n_second)') + ') :: ptask_tail*',
            'S_pending.CURRENT = eps', 'S_pending.FRAMES = eps', 'S_pending.ERRORHANDLER = S_entry.ERRORHANDLER',
            '$lookup(S_pending.ENV, $ptascii("base")) = (n_target)', '$lookup(S_pending.ENV, $ptascii("alias")) = (n_target)',
            'n_target <- S_pending.REFCELLS', 'S_pending.STORE[n_target] = DEFINED (PINT 2)',
            'S_pending.STORE[n_exponent] = DEFINED (PINT 3)', 'S_pending.STORE[n_v] = DEFINED (PINT 100)',
            '$task_nodes(' + marker(1, pending='(n_second)') + ') = [HOBJECT n_second]',
            '$heap_owners($heap_prune($heap_graph(S_pending)), HCELL n_target) = 2',
            '$heap_owners($heap_prune($heap_graph(S_pending)), HOBJECT n_second) = 2',
            '$powerassign_warning_valid(S_pending, pintegeroperation, n_target, NINT 0, NINT (-2), 1, (n_second))',
            '$powerassign_warning_ready(S_pending, pintegeroperation, n_target)',
            '~$powerassign_warning_ready(S_pending, pintegeroperation, n_exponent)',
            '~$powerassign_warning_ready(S_pending[.STORE[n_target] = DEFINED (POBJECT n_second)], pintegeroperation, n_target)',
            '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
            'S_commit_budget = $drive_steps(S_pending, 1)', 'S_commit_budget.COMPLETION = BUDGET',
            'S_commit = S_commit_budget[.COMPLETION = NORMAL]', '$powerassign_frontier(S_commit, 6)',
            'S_commit.TODO = (THROW_SEARCH n_second) :: ptask_tail*', 'S_commit.RESULT = KNOWN PNULL',
            'S_commit.BASE = BASE_VALUE (KNOWN PNULL)', '~$powerassign_tasks(S_commit.TODO)',
            '$lookup(S_commit.ENV, $ptascii("base")) = (n_new)', 'n_new = |S_pending.STORE|',
            'S_commit.CELL = n_new', 'S_commit.LOCATION = ROOT n_new', '~(n_new <- S_commit.REFCELLS)',
            '$lookup(S_commit.ENV, $ptascii("alias")) = (n_target)',
            'S_commit.STORE = S_pending.STORE ++ [DEFINED (PFLOAT 9218868437227405312)]',
            'S_commit.ALLOCATIONS = S_pending.ALLOCATIONS ++ [HCELL n_new]',
            'S_commit.STORE[n_target] = DEFINED (PINT 2)', 'S_commit.STORE[n_v] = DEFINED (PINT 100)',
            '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_target) = 1',
            '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_new) = 1',
            '$heap_owners($heap_prune($heap_graph(S_commit)), HOBJECT n_second) = 2',
            'S_commit.ARRAYS = S_pending.ARRAYS', 'S_commit.OBJECTS = S_pending.OBJECTS',
            'S_commit.STRINGDATA = S_pending.STRINGDATA', 'S_commit.EVENTS = S_pending.EVENTS',
            '$throwable_live(S_commit, n_second)', '$throwable_previous_id(S_commit, n_second) = eps',
            '$call_descriptors_valid(S_commit)', '$heap_valid($heap_graph(S_commit))',
            'S_done = $drive_steps(S_commit, 2000)', '$drive_steps(S_pending, 2000) = S_done',
            'S_done.STORE[n_v] = DEFINED (PINT 100)', 'S_done.STORE[n_new] = DEFINED (PINT 7)',
            'S_done.STORE[n_target] = DEFINED (PINT 2)',
        ]
    else:
        checks += [
            'S_return_found = $powerassign_seek(S_entered, 4, 2000)',
            r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
            'S_return = S_return_found[.COMPLETION = NORMAL]', '$powerassign_frontier(S_return, 4)',
            'S_return.TODO = (' + marker(1) + ') :: ptask_tail*',
            'S_return.STORE[n_target] = DEFINED (PINT 2)', 'S_return.STORE[n_exponent] = DEFINED (PINT 3)',
            'S_return.STORE[n_v] = DEFINED (PINT 100)',
            '$powerassign_warning_valid(S_return, pintegeroperation, n_target, NINT 0, NINT (-2), 1, eps)',
            '~$powerassign_warning_snapshot(S_return, pintegeroperation, n_target, NINT 0, NINT (-2))',
            '$powerassign_warning_ready(S_return, pintegeroperation, n_target)',
            'S_pruned = S_return[.ALLOCATIONS = eps]',
            '$powerassign_warning_valid(S_pruned, pintegeroperation, n_target, NINT 0, NINT (-2), 1, eps)',
            '~$powerassign_warning_ready(S_pruned, pintegeroperation, n_target)',
            '~$powerassign_warning_ready(S_return[.ENV = eps][.GLOBALTABLE = eps], pintegeroperation, n_target)',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
            'S_commit_budget = $drive_steps(S_return, 1)', 'S_commit_budget.COMPLETION = BUDGET',
            'S_commit = S_commit_budget[.COMPLETION = NORMAL]', '$powerassign_frontier(S_commit, 5)',
            'S_commit.TODO = ptask_tail*', 'S_commit.RESULT = KNOWN (PFLOAT 9218868437227405312)',
            'S_commit.CELL = n_target', 'S_commit.LOCATION = ROOT n_target',
            'S_commit.STORE = $set_cell(S_return.STORE, n_target, DEFINED (PFLOAT 9218868437227405312))',
            'S_commit.ENV = S_return.ENV', 'S_commit.ALLOCATIONS = S_return.ALLOCATIONS',
            'S_commit.EVENTS = S_return.EVENTS', 'S_commit.STORE[n_v] = DEFINED (PINT 100)',
            '$call_descriptors_valid(S_commit)', '$heap_valid($heap_graph(S_commit))',
            'S_done = $drive_steps(S_commit, 2000)', '$drive_steps(S_return, 2000) = S_done',
            'S_done.STORE[n_v] = DEFINED (PFLOAT 9218868437227405312)',
            'S_done.STORE[n_target] = DEFINED (PFLOAT 9218868437227405312)',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_exponent] = DEFINED (PINT 3)', '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
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
    report['powerassign_inputs'] = before
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
