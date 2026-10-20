#!/usr/bin/env python3
"""Genuine plain += second-Warning capture and supplied-throw fronts."""
import base64
import json
import addassign_cv_warning_protocol as shared
import addassign_rhs_warning_cases as cases

CASES = ('addassign-rhs-warning-second-throw',)
HELPERS = shared.HELPERS + r'''

dec $addassign_rhs_warning_task(ptask) : bool
def $addassign_rhs_warning_task(ARITHMETIC_ADDASSIGN_CV_RIGHT_WARNING pintegeroperation pvalue_left pnumber_left pvalue_right pnumber_right n) = true
def $addassign_rhs_warning_task(ERROR_HANDLER_INVOKE perrorcall) = $addassign_rhs_warning_task(perrorcall.RESUME)
def $addassign_rhs_warning_task(ERROR_HANDLER_RESULT perrorcall) = $addassign_rhs_warning_task(perrorcall.RESUME)
def $addassign_rhs_warning_task(ERROR_HANDLER_CLEAN perrorcall) = $addassign_rhs_warning_task(perrorcall.RESUME)
def $addassign_rhs_warning_task(ptask) = $addassign_cv_task(ptask) -- otherwise
dec $addassign_rhs_warning_tasks(ptask*) : bool
def $addassign_rhs_warning_tasks(eps) = false
def $addassign_rhs_warning_tasks(ptask :: ptask_tail*) = ($addassign_rhs_warning_task(ptask) \/ $addassign_rhs_warning_tasks(ptask_tail*))
dec $addassign_rhs_warning_handler_frame(pframe, nat) : bool
def $addassign_rhs_warning_handler_frame(pframe, 0) = $addassign_cv_handler_frame(pframe)
def $addassign_rhs_warning_handler_frame(pframe, 1) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_ADDASSIGN_CV_RIGHT_WARNING pintegeroperation pvalue_left pnumber_left pvalue_right pnumber_right 1
  -- if perrorcall.TARGET =/= eps
def $addassign_rhs_warning_handler_frame(pframe, n) = false -- otherwise
dec $addassign_rhs_warning_entered(pframe*, nat) : bool
def $addassign_rhs_warning_entered(eps, n) = false
def $addassign_rhs_warning_entered(pframe :: pframe_tail*, n) = ($addassign_rhs_warning_handler_frame(pframe, n) \/ $addassign_rhs_warning_entered(pframe_tail*, n))
dec $addassign_rhs_warning_frontier(pstate, nat) : bool
def $addassign_rhs_warning_frontier(S, n) = $addassign_cv_frontier(S, n) -- if $(n <= 4)
def $addassign_rhs_warning_frontier(S, 5) = true
  -- if S.TODO = (ARITHMETIC_ADDASSIGN_CV_RIGHT_WARNING pintegeroperation pvalue_left pnumber_left pvalue_right pnumber_right 0) :: ptask_tail*
def $addassign_rhs_warning_frontier(S, 6) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_ADDASSIGN_CV_RIGHT_WARNING pintegeroperation pvalue_left pnumber_left pvalue_right pnumber_right 1
  -- if perrorcall.TARGET = eps
def $addassign_rhs_warning_frontier(S, 7) = (S.CURRENT =/= eps /\ $addassign_rhs_warning_entered(S.FRAMES, 1))
def $addassign_rhs_warning_frontier(S, 8) = true
  -- if S.TODO = (ARITHMETIC_ADDASSIGN_CV_RIGHT_WARNING pintegeroperation pvalue_left pnumber_left pvalue_right pnumber_right 1) :: ptask_tail*
def $addassign_rhs_warning_frontier(S, 9) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if ~$addassign_rhs_warning_tasks(S.TODO)
def $addassign_rhs_warning_frontier(S, n) = false -- otherwise
dec $addassign_rhs_warning_seek(pstate, nat, nat) : pstate
def $addassign_rhs_warning_seek(S, n_stage, n) = S -- if $addassign_rhs_warning_frontier(S, n_stage)
def $addassign_rhs_warning_seek(S, n_stage, n) = S
  -- if ~$addassign_rhs_warning_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $addassign_rhs_warning_seek(S, n_stage, n) = S
  -- if ~$addassign_rhs_warning_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $addassign_rhs_warning_seek(S, n_stage, n) = $addassign_rhs_warning_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$addassign_rhs_warning_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $addassign_rhs_warning_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]', '$addassign_rhs_warning_frontier(S_entry, 0)',
        '$arithmetic_addassign_cv_plan(S_entry) = ((pintegeroperation, pvalue_left, NFLOAT 4623226492472524800))',
        'pintegeroperation.OP = ADD', '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("left"))',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))',
        '$arithmetic_addassign_cv_source(S_entry, pintegeroperation)',
        '$arithmetic_addassign_plan(S_entry) = eps',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("alias")) = (n_alias)',
        '$lookup(S_entry.ENV, $ptascii("supplied")) = (n_supplied)',
        'S_entry.STORE[n_supplied] = DEFINED (POBJECT n_exception)',
        'n_left =/= n_right', '~(n_left <- S_entry.REFCELLS)', '~(n_right <- S_entry.REFCELLS)',
        '$string_bytes(pvalue_left) = ($ptascii("12.5tail"))',
        'S_entry.STORE[n_left] = DEFINED pvalue_left', 'S_entry.STORE[n_right] = DEFINED (PINT 2)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)', 'S_entry.STORE[n_alias] = DEFINED (PINT 0)',
        '$heap_valid($heap_graph(S_entry))',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 1',
        'S_entry.TODO = ptask_entry :: ptask_tail*',
        'S_first = $drive_steps(S_entry, 1)', '$addassign_rhs_warning_frontier(S_first, 1)',
        'S_first.TODO = (ARITHMETIC_ADDASSIGN_CV_WARNING pintegeroperation pvalue_left (NFLOAT 4623226492472524800) 0) :: ptask_tail*',
        'S_first_call = $addassign_rhs_warning_seek(S_first, 2, 100)', '$addassign_rhs_warning_frontier(S_first_call, 2)',
        'S_first_call.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*', 'perrorcall_first.TARGET = eps',
        '$error_call_valid(S_first_call, perrorcall_first)', '$call_descriptors_valid(S_first_call)',
        'S_first_enter = $addassign_rhs_warning_seek(S_first_call, 3, 100)', '$addassign_rhs_warning_frontier(S_first_enter, 3)',
        '$addassign_rhs_warning_entered(S_first_enter.FRAMES, 0)', '$call_descriptors_valid(S_first_enter)',
        'S_return_found = $addassign_rhs_warning_seek(S_first_enter, 4, 2000)', '$addassign_rhs_warning_frontier(S_return_found, 4)',
        'S_return = S_return_found[.COMPLETION = NORMAL]',
        'S_return.TODO = (ARITHMETIC_ADDASSIGN_CV_WARNING pintegeroperation pvalue_left (NFLOAT 4623226492472524800) 1) :: ptask_tail*',
        'S_return.STORE[n_left] = DEFINED (PINT 99)',
        'S_return.STORE[n_right] = DEFINED pvalue_right', '$string_bytes(pvalue_right) = ($ptascii("5.5tail"))',
        '$arithmetic_addassign_cv_ready(S_return, pintegeroperation) = eps',
        '$arithmetic_addassign_cv_right_snapshot(S_return, pintegeroperation) = ((pvalue_right, NFLOAT 4617878467915022336))',
        '$arithmetic_addassign_cv_right_target(S_return, pintegeroperation)',
        '$arithmetic_addassign_cv_warning_valid(S_return, pintegeroperation, pvalue_left, NFLOAT 4623226492472524800, 1)',
        '~$arithmetic_addassign_cv_warning_valid(S_return, pintegeroperation, pvalue_left, NFLOAT 4623226492472524800, 0)',
        '$arithmetic_addassign_cv_right_snapshot(S_return[.ORIGIN = eps], pintegeroperation) = eps',
        '$arithmetic_addassign_cv_right_snapshot(S_return, pintegeroperation[.OP = DIVIDE]) = eps',
        '$arithmetic_addassign_cv_right_snapshot(S_return, pintegeroperation[.LINE = 24]) = eps',
        '$arithmetic_addassign_cv_right_snapshot(S_return[.STORE[n_right] = UNDEFINED], pintegeroperation) = eps',
        '$arithmetic_addassign_cv_right_snapshot(S_return[.STORE[n_right] = DEFINED (PINT 5)], pintegeroperation) = eps',
        '$arithmetic_addassign_cv_right_snapshot(S_return[.REFCELLS = [n_right]], pintegeroperation) = eps',
        '$arithmetic_addassign_cv_right_snapshot(S_return[.PROPREFS = [{CELL n_right, SOURCES eps}]], pintegeroperation) = eps',
        '~$arithmetic_addassign_cv_right_target(S_return[.STORE[n_left] = UNDEFINED], pintegeroperation)',
        '~$arithmetic_addassign_cv_right_target(S_return[.PROPREFS = [{CELL n_left, SOURCES eps}]], pintegeroperation)',
        '~$arithmetic_addassign_cv_right_target(S_return[.STORE[n_left] = DEFINED (POBJECT n_exception)], pintegeroperation)',
        'S_capture_budget = $drive_steps(S_return, 1)', 'S_capture_budget.COMPLETION = BUDGET',
        'S_capture = S_capture_budget[.COMPLETION = NORMAL]', '$addassign_rhs_warning_frontier(S_capture, 5)',
        'S_capture.TODO = ptask_rhs :: ptask_tail*',
        'ptask_rhs = ARITHMETIC_ADDASSIGN_CV_RIGHT_WARNING pintegeroperation pvalue_left (NFLOAT 4623226492472524800) pvalue_right (NFLOAT 4617878467915022336) 0',
        'PhpStep: S_return ~> S_capture', 'S_capture = S_return[.TODO = ptask_rhs :: ptask_tail*]',
        '$task_nodes(ptask_rhs) = eps', '$call_task_valid(S_capture, ptask_rhs)',
        '$arithmetic_addassign_cv_right_warning_valid(S_capture, pintegeroperation, pvalue_left, NFLOAT 4623226492472524800, pvalue_right, NFLOAT 4617878467915022336, 0)',
        '~$arithmetic_addassign_cv_right_warning_valid(S_capture, pintegeroperation, pvalue_left, NFLOAT 4623226492472524800, pvalue_right, NFLOAT 4617878467915022336, 2)',
        'S_second_call = $addassign_rhs_warning_seek(S_capture, 6, 100)', '$addassign_rhs_warning_frontier(S_second_call, 6)',
        'S_second_call.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*', 'perrorcall_second.TARGET = eps',
        'perrorcall_second.SITE = pintegeroperation.SITE', 'perrorcall_second.LINE = 25', 'perrorcall_second.LEVEL = 2',
        'perrorcall_second.RESUME = ARITHMETIC_ADDASSIGN_CV_RIGHT_WARNING pintegeroperation pvalue_left (NFLOAT 4623226492472524800) pvalue_right (NFLOAT 4617878467915022336) 1',
        '$error_call_valid(S_second_call, perrorcall_second)', '$call_descriptors_valid(S_second_call)',
        'S_second_call.STORE[n_left] = DEFINED (PINT 99)',
        'S_second_enter = $addassign_rhs_warning_seek(S_second_call, 7, 100)', '$addassign_rhs_warning_frontier(S_second_enter, 7)',
        '$addassign_rhs_warning_entered(S_second_enter.FRAMES, 1)', '$call_descriptors_valid(S_second_enter)',
        'S_throw_found = $addassign_rhs_warning_seek(S_second_enter, 9, 2000)', '$addassign_rhs_warning_frontier(S_throw_found, 9)',
        'S_throw = S_throw_found[.COMPLETION = NORMAL]', 'S_throw.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        '~$addassign_rhs_warning_tasks(S_throw.TODO)', 'S_throw.FRAMES = eps', 'S_throw.CURRENT = eps',
        '$lookup(S_throw.ENV, $ptascii("left")) = (n_left)', '$lookup(S_throw.ENV, $ptascii("alias")) = (n_left)',
        '$lookup(S_throw.ENV, $ptascii("right")) = (n_right)', 'n_left <- S_throw.REFCELLS', '~(n_right <- S_throw.REFCELLS)',
        'S_throw.STORE[n_left] = DEFINED (PINT 88)', 'S_throw.STORE[n_right] = DEFINED (PINT 7)',
        'S_throw.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_right) = 1',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_exception) = 2', '$heap_valid($heap_graph(S_throw))',
        'S_throw.EVENTS[0:|S_entry.EVENTS|] = S_entry.EVENTS',
        'S_throw.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        'S_done = $drive_steps(S_throw, 5000)', 'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        '~$addassign_rhs_warning_tasks(S_done.TODO)',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_left)', '$lookup(S_done.ENV, $ptascii("alias")) = (n_left)',
        'S_done.STORE[n_left] = DEFINED (PINT 7)', 'S_done.STORE[n_right] = DEFINED (PINT 8)',
        'S_done.STORE[n_v] = DEFINED (PINT 100)',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        'S_done.EXITSTATUS = 0',
        '$drive_steps(S_entry, 10000) = S_done',
        'S_zero = $drive_steps(S_capture, 0)', 'S_zero = S_capture[.COMPLETION = BUDGET]',
    ]
    assert len(checks)==len(set(checks))
    return checks
