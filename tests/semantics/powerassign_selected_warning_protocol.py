#!/usr/bin/env python3
"""Reached selected power captures and mandatory store before a supplied throw."""
import base64
import json

import powerassign_selected_warning_cases as cases
import integer_operator_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $powerassign_selected_task(ptask) : bool
def $powerassign_selected_task(POWER_ASSIGN_SELECTED_WARNING pintegeroperation n_target pnumber_left pnumber_right n_stage n_pending?) = true
def $powerassign_selected_task(ERROR_HANDLER_INVOKE perrorcall) = $powerassign_selected_task(perrorcall.RESUME)
def $powerassign_selected_task(ERROR_HANDLER_RESULT perrorcall) = $powerassign_selected_task(perrorcall.RESUME)
def $powerassign_selected_task(ERROR_HANDLER_CLEAN perrorcall) = $powerassign_selected_task(perrorcall.RESUME)
def $powerassign_selected_task(ptask) = false -- otherwise
dec $powerassign_selected_tasks(ptask*) : bool
def $powerassign_selected_tasks(eps) = false
def $powerassign_selected_tasks(ptask :: ptask_tail*) = ($powerassign_selected_task(ptask) \/ $powerassign_selected_tasks(ptask_tail*))
dec $powerassign_selected_handler_frame(pframe) : bool
def $powerassign_selected_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = POWER_ASSIGN_SELECTED_WARNING pintegeroperation n_target pnumber_left pnumber_right 1 eps
  -- if perrorcall.TARGET =/= eps
def $powerassign_selected_handler_frame(pframe) = false -- otherwise
dec $powerassign_selected_entered(pframe*) : bool
def $powerassign_selected_entered(eps) = false
def $powerassign_selected_entered(pframe :: pframe_tail*) = ($powerassign_selected_handler_frame(pframe) \/ $powerassign_selected_entered(pframe_tail*))
dec $powerassign_selected_frontier(pstate, nat) : bool
def $powerassign_selected_frontier(S, 0) = ($powerassign_selected_warning_plan(S) =/= eps)
def $powerassign_selected_frontier(S, 1) = true
  -- if S.TODO = (POWER_ASSIGN_SELECTED_WARNING pintegeroperation n_target pnumber_left pnumber_right 0 eps) :: ptask_tail*
def $powerassign_selected_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = POWER_ASSIGN_SELECTED_WARNING pintegeroperation n_target pnumber_left pnumber_right 1 eps
  -- if perrorcall.TARGET = eps
def $powerassign_selected_frontier(S, 3) = (S.CURRENT =/= eps /\ $powerassign_selected_entered(S.FRAMES))
def $powerassign_selected_frontier(S, 4) = true
  -- if S.TODO = (POWER_ASSIGN_SELECTED_WARNING pintegeroperation n_target pnumber_left pnumber_right 1 eps) :: ptask_tail*
def $powerassign_selected_frontier(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprAssignOpPow expression_left expression_right metadata)
  -- if S.RESULT = KNOWN (PFLOAT n)
  -- if ~$powerassign_selected_tasks(S.TODO)
def $powerassign_selected_frontier(S, 6) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if ~$powerassign_selected_tasks(S.TODO)
def $powerassign_selected_frontier(S, 7) = true
  -- if S.TODO = (POWER_ASSIGN_SELECTED_WARNING pintegeroperation n_target pnumber_left pnumber_right 1 (n_exception)) :: ptask_tail*
def $powerassign_selected_frontier(S, n) = false -- otherwise
dec $powerassign_selected_seek(pstate, nat, nat) : pstate
def $powerassign_selected_seek(S, n_stage, n) = S -- if $powerassign_selected_frontier(S, n_stage)
def $powerassign_selected_seek(S, n_stage, n) = S
  -- if ~$powerassign_selected_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $powerassign_selected_seek(S, n_stage, n) = S
  -- if ~$powerassign_selected_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $powerassign_selected_seek(S, n_stage, n) = $powerassign_selected_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$powerassign_selected_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''

def conditions(name, program, path, stdout):
    assert name in CASES
    result = 'PFLOAT 9218868437227405312'
    marker = lambda stage, pending='eps': f'POWER_ASSIGN_SELECTED_WARNING pintegeroperation n_left (NINT 0) (NINT (-2)) {stage} {pending}'
    valid = lambda state, stage, pending='eps': f'$powerassign_selected_warning_valid({state}, pintegeroperation, n_left, NINT 0, NINT (-2), {stage}, {pending})'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $powerassign_selected_seek({before}, {stage}, 5000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$powerassign_selected_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$powerassign_selected_warning_plan(S_entry) = (' + marker(0) + ')',
        '$powerassign_warning_plan(S_entry) = eps',
        '$powerassign_selected_warning_source(S_entry, pintegeroperation)',
        'pintegeroperation.OP = POWER', '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_left',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_right', 'n_left =/= n_right',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("replacementLeft")) = (n_replacement_left)',
        '$lookup(S_entry.ENV, $ptascii("replacementRight")) = (n_replacement_right)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)', '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
        'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        'S_entry.STORE[n_left] = DEFINED (PINT 0)', 'S_entry.STORE[n_right] = DEFINED (PINT (-2))',
        'S_entry.STORE[n_replacement_left] = DEFINED (PINT 77)',
        'S_entry.STORE[n_replacement_right] = DEFINED (PINT 7)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', 'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.ERRORHANDLER.LEVELS = 8192', '$error_handler_eligible(S_entry, 8192)', '~$error_handler_eligible(S_entry, 2)',
        '$powerassign_selected_warning_snapshot(S_entry, pintegeroperation, n_left, NINT 0, NINT (-2))',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 2',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$powerassign_selected_warning_plan(S_entry[.ORIGIN = eps]) = eps',
        '$powerassign_selected_warning_plan(S_entry[.ERRORHANDLER.CALLBACK = eps]) = eps',
        '$powerassign_selected_warning_plan(S_entry[.ERRORHANDLER.LEVELS = 2]) = eps',
        '$powerassign_selected_warning_plan(S_entry[.REFCELLS = eps]) = eps',
        '$powerassign_selected_warning_plan(S_entry[.STORE[n_right] = UNDEFINED]) = eps',
        '$powerassign_selected_warning_plan(S_entry[.STORE[n_left] = DEFINED (PINT 1)]) = eps',
        '$powerassign_selected_warning_plan(S_entry[.STORE[n_left] = DEFINED (POBJECT n_second)]) = eps',
        '$powerassign_selected_warning_plan(S_entry[.ALLOCATIONS = eps]) = eps',
        '$powerassign_selected_warning_plan(S_entry[.PROPREFS = [{CELL n_left, SOURCES eps}]]) = eps',
        '$powerassign_selected_warning_plan(S_entry[.PROPREFS = [{CELL n_right, SOURCES eps}]]) = eps',
        '~$powerassign_selected_warning_source(S_entry, pintegeroperation[.OP = DIVIDE])',
        '~$powerassign_selected_warning_source(S_entry, pintegeroperation[.SWAPPED = true])',
        '~$powerassign_selected_warning_source(S_entry, pintegeroperation[.LINE = 24])',
        '~$powerassign_selected_warning_source(S_entry, pintegeroperation[.LEFT = VARIABLE ($ptascii("v")) 23])',
        '~$powerassign_selected_warning_source(S_entry, pintegeroperation[.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))])',
        'S_entry.TODO = ptask_old :: ptask_tail*', 'PhpStep: S_entry ~> S_capture',
        'S_capture = S_entry[.TODO = (' + marker(0) + ') :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = ROOT n_left]',
        valid('S_capture', 0), '$task_nodes(' + marker(0) + ') = eps',
        '~$powerassign_selected_warning_valid(S_capture, pintegeroperation, n_left, NFLOAT 0, NINT (-2), 0, eps)',
        '~$powerassign_selected_warning_valid(S_capture, pintegeroperation, n_right, NINT 0, NINT (-2), 1, eps)',
        '~$powerassign_selected_warning_valid(S_capture, pintegeroperation, n_left, NINT 0, NINT (-2), 2, eps)',
        '~$powerassign_selected_warning_valid(S_capture, pintegeroperation, n_left, NINT 0, NINT (-9223372036854775809), 1, eps)',
        '~' + valid('S_capture', 0, '(n_second)'),
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(1), 'perrorcall.TARGET = eps',
        'perrorcall.SITE = pintegeroperation.SITE', 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 25',
        '$error_call_valid(S_dispatch, perrorcall)', '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'perrorcall_number = perrorcall[.RESUME = POWER_ASSIGN_SELECTED_WARNING pintegeroperation n_left (NINT 0) (NINT (-3)) 1 eps]',
        '~$error_call_valid(S_dispatch, perrorcall_number)',
        'perrorcall_line = perrorcall[.LINE = 24]', '~$error_call_valid(S_dispatch, perrorcall_line)',
        'perrorcall_message = perrorcall[.MESSAGE = eps][.EVENT = DIAGNOSTIC "Deprecated" eps 25]',
        '~$error_call_valid(S_dispatch, perrorcall_message)',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += ['$powerassign_selected_entered(S_entered.FRAMES)', '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))']
    seek('S_pending', 'S_entered', 7)
    checks += [
        'S_pending.TODO = (' + marker(1, '(n_second)') + ') :: ptask_tail*',
        'S_pending.CURRENT = eps', 'S_pending.FRAMES = eps', 'S_pending.ERRORHANDLER = S_entry.ERRORHANDLER',
        'S_pending.STORE[n_left] = DEFINED (PINT 88)', 'S_pending.STORE[n_right] = DEFINED (PINT 7)',
        'S_pending.STORE[n_calls] = DEFINED (PINT 1)', 'S_pending.STORE[n_v] = DEFINED (PINT 100)',
        '$lookup(S_pending.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_pending.ENV, $ptascii("left")) = (n_replacement_left)',
        '$lookup(S_pending.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_pending.ENV, $ptascii("right")) = (n_replacement_right)',
        'S_pending.STORE[n_replacement_left] = DEFINED (PINT 77)',
        'S_pending.STORE[n_replacement_right] = DEFINED (PINT 7)',
        '$powerassign_selected_warning_source(S_pending, pintegeroperation)', '~$arithmetic_add_selected(S_pending, pintegeroperation)',
        valid('S_pending', 1, '(n_second)'), '~' + valid('S_pending', 0, '(n_second)'),
        '$powerassign_selected_warning_ready(S_pending, pintegeroperation, n_left)',
        '~$powerassign_selected_warning_ready(S_pending, pintegeroperation, n_replacement_left)',
        '~$powerassign_selected_warning_ready(S_pending[.STORE[n_left] = UNDEFINED], pintegeroperation, n_left)',
        '~$powerassign_selected_warning_ready(S_pending[.PROPREFS = [{CELL n_left, SOURCES eps}]], pintegeroperation, n_left)',
        '~$powerassign_selected_warning_ready(S_pending[.STORE[n_left] = DEFINED (POBJECT n_second)], pintegeroperation, n_left)',
        '$task_nodes(' + marker(1, '(n_second)') + ') = [HOBJECT n_second]',
        '$heap_owners($heap_prune($heap_graph(S_pending)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_pending)), HCELL n_right) = 1',
        '$heap_owners($heap_prune($heap_graph(S_pending)), HCELL n_replacement_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_pending)), HCELL n_replacement_right) = 2',
        '$heap_owners($heap_prune($heap_graph(S_pending)), HOBJECT n_second) = 2',
        '$throwable_live(S_pending, n_second)', '$throwable_previous_id(S_pending, n_second) = eps',
        'S_pending.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
        'PhpStep: S_pending ~> S_atomic',
        'S_atomic = S_pending[.TODO = (THROW_SEARCH n_second) :: ptask_tail*][.STORE[n_left] = DEFINED (' + result + ')][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = ROOT n_left]',
    ]
    step('S_commit', 'S_pending')
    checks += [
        '$powerassign_selected_frontier(S_commit, 6)', 'S_commit.TODO = S_atomic.TODO',
        'S_commit.RESULT = KNOWN PNULL', 'S_commit.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_commit.STORE = S_atomic.STORE', 'S_commit.LOCATION = ROOT n_left',
        'S_commit.ENV = S_pending.ENV', 'S_commit.REFCELLS = S_pending.REFCELLS',
        'S_commit.ALLOCATIONS = S_pending.ALLOCATIONS', 'S_commit.ARRAYS = S_pending.ARRAYS', 'S_commit.OBJECTS = S_pending.OBJECTS',
        'S_commit.EVENTS = S_pending.EVENTS', 'S_commit.STRINGDATA = S_pending.STRINGDATA',
        '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_commit)), HOBJECT n_second) = 2',
        'S_commit.STORE[n_v] = DEFINED (PINT 100)',
        '~$powerassign_selected_tasks(S_commit.TODO)', '$call_descriptors_valid(S_commit)', '$heap_valid($heap_graph(S_commit))',
        'S_done = $drive_steps(S_commit, 5000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_v] = DEFINED (PINT 100)', 'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        '$lookup(S_done.ENV, $ptascii("leftAlias")) = (n_left)', 'S_done.STORE[n_left] = DEFINED (PINT 6)',
        '$lookup(S_done.ENV, $ptascii("rightAlias")) = (n_right)', 'S_done.STORE[n_right] = DEFINED (PINT 4)',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_replacement_left)',
        '$lookup(S_done.ENV, $ptascii("replacementLeft")) = (n_replacement_left)',
        'S_done.STORE[n_replacement_left] = DEFINED (PINT 8)',
        '$lookup(S_done.ENV, $ptascii("right")) = (n_replacement_right)',
        '$lookup(S_done.ENV, $ptascii("replacementRight")) = (n_replacement_right)',
        'S_done.STORE[n_replacement_right] = DEFINED (PINT 9)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_right) = 1',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement_right) = 2',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_entry, 7000) = S_done',
        '$drive_steps(S_pending, 0) = S_pending[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
