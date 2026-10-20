#!/usr/bin/env python3
"""Real selected modulo target, late RHS wrapper, and atomic integer store."""
import base64
import json
import arithmetic_warning_protocol as shared
import modassign_selected_warning_cases as cases

CASES = ('modassign-selected-warning-rebound-right',)
HELPERS = shared.HELPERS + r'''
dec $modassign_selected_task(ptask) : bool
def $modassign_selected_task(MOD_ASSIGN_SELECTED_WARNING pintegeroperation n_bits i_left n_stage) = true
def $modassign_selected_task(ERROR_HANDLER_INVOKE perrorcall) = $modassign_selected_task(perrorcall.RESUME)
def $modassign_selected_task(ERROR_HANDLER_RESULT perrorcall) = $modassign_selected_task(perrorcall.RESUME)
def $modassign_selected_task(ERROR_HANDLER_CLEAN perrorcall) = $modassign_selected_task(perrorcall.RESUME)
def $modassign_selected_task(ptask) = false -- otherwise
dec $modassign_selected_tasks(ptask*) : bool
def $modassign_selected_tasks(eps) = false
def $modassign_selected_tasks(ptask :: ptask_tail*) = ($modassign_selected_task(ptask) \/ $modassign_selected_tasks(ptask_tail*))
dec $modassign_selected_handler_frame(pframe) : bool
def $modassign_selected_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = MOD_ASSIGN_SELECTED_WARNING pintegeroperation n_bits i_left 1
  -- if perrorcall.TARGET =/= eps
def $modassign_selected_handler_frame(pframe) = false -- otherwise
dec $modassign_selected_entered(pframe*) : bool
def $modassign_selected_entered(eps) = false
def $modassign_selected_entered(pframe :: pframe_tail*) = ($modassign_selected_handler_frame(pframe) \/ $modassign_selected_entered(pframe_tail*))
dec $modassign_selected_frontier(pstate, nat) : bool
def $modassign_selected_frontier(S, 0) = ($modassign_selected_warning_plan(S) =/= eps)
def $modassign_selected_frontier(S, 1) = true
  -- if S.TODO = (MOD_ASSIGN_SELECTED_WARNING pintegeroperation n_bits i_left 0) :: ptask_tail*
def $modassign_selected_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = MOD_ASSIGN_SELECTED_WARNING pintegeroperation n_bits i_left 1
  -- if perrorcall.TARGET = eps
def $modassign_selected_frontier(S, 3) = (S.CURRENT =/= eps /\ $modassign_selected_entered(S.FRAMES))
def $modassign_selected_frontier(S, 4) = true
  -- if S.TODO = (MOD_ASSIGN_SELECTED_WARNING pintegeroperation n_bits i_left 1) :: ptask_tail*
def $modassign_selected_frontier(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprAssignOpMod expression_left expression_right metadata)
  -- if S.RESULT = KNOWN (PINT i)
  -- if ~$modassign_selected_tasks(S.TODO)
def $modassign_selected_frontier(S, 6) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if ~$modassign_selected_tasks(S.TODO)
def $modassign_selected_frontier(S, n) = false -- otherwise
dec $modassign_selected_seek(pstate, nat, nat) : pstate
def $modassign_selected_seek(S, n_stage, n) = S -- if $modassign_selected_frontier(S, n_stage)
def $modassign_selected_seek(S, n_stage, n) = S
  -- if ~$modassign_selected_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $modassign_selected_seek(S, n_stage, n) = S
  -- if ~$modassign_selected_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $modassign_selected_seek(S, n_stage, n) = $modassign_selected_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$modassign_selected_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    checks = [
        'S_initial = $php_run(@PROGRAM@, 0, @PATH@)',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $modassign_selected_seek(S_initial, 0, 2000)',
        'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]',
        '$modassign_selected_frontier(S_entry, 0)',
        '$modassign_selected_warning_plan(S_entry) = (MOD_ASSIGN_SELECTED_WARNING pintegeroperation n_bits 12 0)',
        'n_bits = 4623226492472524800',
        'pintegeroperation.OP = MODULO',
        '~pintegeroperation.SWAPPED',
        'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_left',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))',
        '$modassign_selected_warning_source(S_entry, pintegeroperation)',
        '$modassign_selected_warning_snapshot(S_entry, pintegeroperation, n_bits)',
        '$modassign_warning_plan(S_entry) = eps',
        '$modassign_both_warning_plan(S_entry) = eps',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("replacementLeft")) = (n_replacement_left)',
        '$lookup(S_entry.ENV, $ptascii("replacementRight")) = (n_replacement_right)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'n_left =/= n_right',
        'S_entry.STORE[n_left] = DEFINED (PFLOAT n_bits)',
        'S_entry.STORE[n_right] = DEFINED (PINT 0)',
        'S_entry.STORE[n_replacement_left] = DEFINED (PINT 77)',
        'S_entry.STORE[n_replacement_right] = DEFINED (PINT 5)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 2',
        '$call_descriptors_valid(S_entry)',
        '$heap_valid($heap_graph(S_entry))',
        'S_entry.TODO = ptask_old :: ptask_tail*',
        '$modassign_selected_warning_plan(S_entry[.ORIGIN = eps]) = eps',
        '$modassign_selected_warning_plan(S_entry[.TODO = (COMPOUND_APPLY ADD (BASE_VALUE pintegeroperation.LEFT) false 25) :: ptask_tail*]) = eps',
        '$modassign_selected_warning_plan(S_entry[.TODO = (COMPOUND_APPLY MODULO (BASE_VALUE pintegeroperation.LEFT) false 24) :: ptask_tail*]) = eps',
        '$modassign_selected_warning_plan(S_entry[.REFCELLS = eps]) = eps',
        '$modassign_selected_warning_plan(S_entry[.ALLOCATIONS = eps]) = eps',
        '$modassign_selected_warning_plan(S_entry[.PROPREFS = [{CELL n_left, SOURCES eps}]]) = eps',
        '$modassign_selected_warning_plan(S_entry[.PROPREFS = [{CELL n_right, SOURCES eps}]]) = eps',
        '$modassign_selected_warning_plan(S_entry[.STORE[n_left] = UNDEFINED]) = eps',
        '$modassign_selected_warning_plan(S_entry[.STORE[n_right] = UNDEFINED]) = eps',
        '$modassign_selected_warning_plan(S_entry[.STORE[n_left] = DEFINED (PINT 12)]) = eps',
        '$modassign_selected_warning_plan(S_entry[.STORE[n_right] = DEFINED (PFLOAT n_bits)]) = eps',
        '$modassign_selected_warning_plan(S_entry[.ERRORHANDLER.CALLBACK = eps]) = eps',
        '$modassign_selected_warning_plan(S_entry[.ERRORHANDLER.LEVELS = 2]) = eps',
        '~$modassign_selected_warning_valid(S_entry, pintegeroperation[.OP = ADD], n_bits, 12, 0)',
        '~$modassign_selected_warning_valid(S_entry, pintegeroperation[.LINE = 24], n_bits, 12, 0)',
        '~$modassign_selected_warning_valid(S_entry, pintegeroperation[.RIGHTPOINTER = INTEGER_CELL n_right], n_bits, 12, 0)',
        '~$modassign_selected_warning_valid(S_entry, pintegeroperation, n_bits, 13, 0)',
        '~$modassign_selected_warning_valid(S_entry, pintegeroperation, n_bits, 12, 2)',
        'PhpStep: S_entry ~> S_begin_atomic',
        'S_begin_atomic = S_entry[.TODO = (MOD_ASSIGN_SELECTED_WARNING pintegeroperation n_bits 12 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = ROOT n_left]',
        'S_begin_budget = $drive_steps(S_entry, 1)',
        'S_begin_budget.COMPLETION = BUDGET',
        'S_begin = S_begin_budget[.COMPLETION = NORMAL]',
        'S_begin = S_begin_atomic',
        '$modassign_selected_frontier(S_begin, 1)',
        '$task_nodes(MOD_ASSIGN_SELECTED_WARNING pintegeroperation n_bits 12 0) = eps',
        'S_call_found = $modassign_selected_seek(S_begin, 2, 100)',
        '$modassign_selected_frontier(S_call_found, 2)',
        'S_call = S_call_found[.COMPLETION = NORMAL]',
        'S_call.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.TARGET = eps',
        'perrorcall.RESUME = MOD_ASSIGN_SELECTED_WARNING pintegeroperation n_bits 12 1',
        'perrorcall.SITE = pintegeroperation.SITE',
        'perrorcall.LINE = 25',
        'perrorcall.LEVEL = 8192',
        'perrorcall.MESSAGE = ($ptascii("Implicit conversion from float 12.5 to int loses precision"))',
        '$error_call_valid(S_call, perrorcall)',
        '$call_descriptors_valid(S_call)',
        'S_entered = $modassign_selected_seek(S_call, 3, 100)',
        '$modassign_selected_frontier(S_entered, 3)',
        '$modassign_selected_entered(S_entered.FRAMES)',
        '$call_descriptors_valid(S_entered)',
        'S_return_found = $modassign_selected_seek(S_entered, 4, 2000)',
        '$modassign_selected_frontier(S_return_found, 4)',
        'S_return = S_return_found[.COMPLETION = NORMAL]',
        'S_return.TODO = (MOD_ASSIGN_SELECTED_WARNING pintegeroperation n_bits 12 1) :: ptask_tail*',
        '$modassign_selected_warning_valid(S_return, pintegeroperation, n_bits, 12, 1)',
        '~$modassign_selected_warning_valid(S_return, pintegeroperation, n_bits, 12, 0)',
        '$lookup(S_return.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_return.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_return.ENV, $ptascii("left")) = (n_replacement_left)',
        '$lookup(S_return.ENV, $ptascii("right")) = (n_replacement_right)',
        'S_return.STORE[n_left] = DEFINED (PINT 99)',
        'S_return.STORE[n_right] = DEFINED (PINT 0)',
        'S_return.STORE[n_replacement_left] = DEFINED (PINT 77)',
        'S_return.STORE[n_replacement_right] = DEFINED (PINT 5)',
        'S_return.STORE[n_calls] = DEFINED (PINT 1)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)',
        '$integer_pointer_value(S_return, pintegeroperation.LEFTPOINTER) = (PINT 99)',
        '$integer_pointer_value(S_return, pintegeroperation.RIGHTPOINTER) = (PINT 5)',
        '$modassign_selected_warning_right(S_return, pintegeroperation) = (5)',
        '$modassign_selected_warning_target(S_return, pintegeroperation)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 1',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_replacement_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_replacement_right) = 2',
        '$modassign_selected_warning_right(S_return[.STORE[n_right] = DEFINED (PINT 9)], pintegeroperation) = (5)',
        '$modassign_selected_warning_right(S_return[.STORE[n_replacement_right] = UNDEFINED], pintegeroperation) = eps',
        '$modassign_selected_warning_valid(S_return[.STORE[n_replacement_right] = UNDEFINED], pintegeroperation, n_bits, 12, 1)',
        '~$modassign_selected_warning_target(S_return[.PROPREFS = [{CELL n_left, SOURCES eps}]], pintegeroperation)',
        '$call_descriptors_valid(S_return)',
        '$heap_valid($heap_graph(S_return))',
        'S_return.EVENTS[0:|S_entry.EVENTS|] = S_entry.EVENTS',
        'S_return.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        'PhpStep: S_return ~> S_atomic',
        'S_atomic = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (PINT 2)][.LOCATION = ROOT n_left][.STORE[n_left] = DEFINED (PINT 2)]',
        'S_result_budget = $drive_steps(S_return, 1)',
        'S_result_budget.COMPLETION = BUDGET',
        'S_result = S_result_budget[.COMPLETION = NORMAL]',
        '$modassign_selected_frontier(S_result, 5)',
        'S_result.RESULT = KNOWN (PINT 2)',
        'S_result.TODO = ptask_tail*',
        'S_result.LOCATION = ROOT n_left',
        'S_result.STORE = S_atomic.STORE',
        'S_result.STORE[n_v] = DEFINED (PINT 100)',
        'S_result.ENV = S_return.ENV',
        'S_result.REFCELLS = S_return.REFCELLS',
        'S_result.ALLOCATIONS = S_return.ALLOCATIONS',
        'S_result.EVENTS = S_return.EVENTS',
        'S_result.STRINGDATA = S_return.STRINGDATA',
        'S_result.ARRAYS = S_return.ARRAYS',
        'S_result.OBJECTS = S_return.OBJECTS',
        '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_left) = 1',
        '$call_descriptors_valid(S_result)',
        '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 4000)',
        'S_done.COMPLETION = NORMAL',
        'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps',
        'S_done.CURRENT = eps',
        'S_done.FRAMES = eps',
        'S_done.HELD = eps',
        'S_done.STORE[n_left] = DEFINED (PINT 6)',
        'S_done.STORE[n_right] = DEFINED (PINT 4)',
        'S_done.STORE[n_replacement_left] = DEFINED (PINT 8)',
        'S_done.STORE[n_replacement_right] = DEFINED (PINT 9)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        'S_done.STORE[n_v] = DEFINED (PINT 2)',
        '$integer_outputs(S_done.EVENTS) = (@STDOUT@)',
        '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
    ]
    checks[0] = checks[0].replace('@PROGRAM@', program).replace('@PATH@', json.dumps(base64.b64encode(bytes(path)).decode()))
    checks = [check.replace('@STDOUT@', '[' + ','.join(map(str, stdout)) + ']') for check in checks]
    assert len(checks) == len(set(checks))
    return checks
