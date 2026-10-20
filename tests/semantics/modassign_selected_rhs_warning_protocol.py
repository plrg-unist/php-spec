#!/usr/bin/env python3
"""Reached modulo RHS conversion, cached zero and fresh Error without storage."""
import base64
import json

import modassign_selected_rhs_warning_cases as cases
import modassign_selected_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''

dec $modassign_selected_rhs_diagnostic(pevent, text) : nat
def $modassign_selected_rhs_diagnostic(DIAGNOSTIC text n* z, text) = 1
def $modassign_selected_rhs_diagnostic(DIAGNOSTIC_SOURCE n_source text n* z, text) = 1
def $modassign_selected_rhs_diagnostic(DIAGNOSTIC_STACK text n* z n_trace*, text) = 1
def $modassign_selected_rhs_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n* z n_trace*, text) = 1
def $modassign_selected_rhs_diagnostic(pevent, text) = 0 -- otherwise
dec $modassign_selected_rhs_diagnostics(pevent*, text) : nat
def $modassign_selected_rhs_diagnostics(eps, text) = 0
def $modassign_selected_rhs_diagnostics(pevent :: pevent_tail*, text) = $($modassign_selected_rhs_diagnostic(pevent, text) + $modassign_selected_rhs_diagnostics(pevent_tail*, text))

dec $modassign_selected_rhs_task(ptask) : bool
def $modassign_selected_rhs_task(MOD_ASSIGN_SELECTED_WARNING pintegeroperation n_bits i_left n_stage) = true
def $modassign_selected_rhs_task(MOD_ASSIGN_SELECTED_RIGHT_WARNING pintegeroperation n_left_bits i_left n_right_bits i_right n_stage) = true
def $modassign_selected_rhs_task(ERROR_HANDLER_INVOKE perrorcall) = $modassign_selected_rhs_task(perrorcall.RESUME)
def $modassign_selected_rhs_task(ERROR_HANDLER_RESULT perrorcall) = $modassign_selected_rhs_task(perrorcall.RESUME)
def $modassign_selected_rhs_task(ERROR_HANDLER_CLEAN perrorcall) = $modassign_selected_rhs_task(perrorcall.RESUME)
def $modassign_selected_rhs_task(ptask) = false -- otherwise
dec $modassign_selected_rhs_tasks(ptask*) : bool
def $modassign_selected_rhs_tasks(eps) = false
def $modassign_selected_rhs_tasks(ptask :: ptask_tail*) = ($modassign_selected_rhs_task(ptask) \/ $modassign_selected_rhs_tasks(ptask_tail*))
dec $modassign_selected_rhs_handler_frame(pframe) : bool
def $modassign_selected_rhs_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = MOD_ASSIGN_SELECTED_RIGHT_WARNING pintegeroperation n_left_bits i_left n_right_bits i_right 1
  -- if perrorcall.TARGET =/= eps
def $modassign_selected_rhs_handler_frame(pframe) = false -- otherwise
dec $modassign_selected_rhs_entered(pframe*) : bool
def $modassign_selected_rhs_entered(eps) = false
def $modassign_selected_rhs_entered(pframe :: pframe_tail*) = ($modassign_selected_rhs_handler_frame(pframe) \/ $modassign_selected_rhs_entered(pframe_tail*))
dec $modassign_selected_rhs_frontier(pstate, nat) : bool
def $modassign_selected_rhs_frontier(S, n) = $modassign_selected_frontier(S, n) -- if $(n <= 4)
def $modassign_selected_rhs_frontier(S, 5) = true
  -- if S.TODO = (MOD_ASSIGN_SELECTED_RIGHT_WARNING pintegeroperation n_left_bits i_left n_right_bits i_right 0) :: ptask_tail*
def $modassign_selected_rhs_frontier(S, 6) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = MOD_ASSIGN_SELECTED_RIGHT_WARNING pintegeroperation n_left_bits i_left n_right_bits i_right 1
  -- if perrorcall.TARGET = eps
def $modassign_selected_rhs_frontier(S, 7) = (S.CURRENT =/= eps /\ $modassign_selected_rhs_entered(S.FRAMES))
def $modassign_selected_rhs_frontier(S, 8) = true
  -- if S.TODO = (MOD_ASSIGN_SELECTED_RIGHT_WARNING pintegeroperation n_left_bits i_left n_right_bits i_right 1) :: ptask_tail*
def $modassign_selected_rhs_frontier(S, 9) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprAssignOpMod expression_left expression_right metadata)
  -- if S.RESULT = KNOWN (PINT i)
  -- if ~$modassign_selected_rhs_tasks(S.TODO)
def $modassign_selected_rhs_frontier(S, 10) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n_exception) :: ptask_tail*
  -- if ~$modassign_selected_rhs_tasks(S.TODO)
def $modassign_selected_rhs_frontier(S, n) = false -- otherwise
dec $modassign_selected_rhs_seek(pstate, nat, nat) : pstate
def $modassign_selected_rhs_seek(S, n_stage, n) = S -- if $modassign_selected_rhs_frontier(S, n_stage)
def $modassign_selected_rhs_seek(S, n_stage, n) = S
  -- if ~$modassign_selected_rhs_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $modassign_selected_rhs_seek(S, n_stage, n) = S
  -- if ~$modassign_selected_rhs_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $modassign_selected_rhs_seek(S, n_stage, n) = $modassign_selected_rhs_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$modassign_selected_rhs_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    marker = lambda stage: f'MOD_ASSIGN_SELECTED_RIGHT_WARNING pintegeroperation n_left_bits 12 n_right_bits 0 {stage}'
    valid = lambda state, stage: f'$modassign_selected_right_warning_valid({state}, pintegeroperation, n_left_bits, 12, n_right_bits, 0, {stage})'
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET']
    def seek(state, before, stage):
        checks.extend([f'{state}_found = $modassign_selected_rhs_seek({before}, {stage}, 4000)',
                       f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
                       f'{state} = {state}_found[.COMPLETION = NORMAL]', f'$modassign_selected_rhs_frontier({state}, {stage})'])
    def step(state, before):
        checks.extend([f'{state}_budget = $drive_steps({before}, 1)', f'{state}_budget.COMPLETION = BUDGET',
                       f'{state} = {state}_budget[.COMPLETION = NORMAL]'])
    seek('S_entry', 'S_initial', 0)
    checks += [
        '$modassign_selected_warning_plan(S_entry) = (MOD_ASSIGN_SELECTED_WARNING pintegeroperation n_left_bits 12 0)',
        'n_left_bits = 4623226492472524800', 'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_left',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))',
        '$modassign_selected_warning_source(S_entry, pintegeroperation)',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)', '$lookup(S_entry.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_old_right)', '$lookup(S_entry.ENV, $ptascii("rightAlias")) = (n_old_right)',
        '$lookup(S_entry.ENV, $ptascii("replacementLeft")) = (n_new_left)',
        '$lookup(S_entry.ENV, $ptascii("replacementRight")) = (n_new_right)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)', '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        'S_entry.STORE[n_left] = DEFINED (PFLOAT n_left_bits)', 'S_entry.STORE[n_old_right] = DEFINED (PINT 5)',
        'S_entry.STORE[n_new_left] = DEFINED (PINT 77)',
        'S_entry.STORE[n_new_right] = DEFINED (PFLOAT 4602678819172646912)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)', 'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_old_right) = 2',
        '$modassign_selected_right_warning_plan(S_entry) = eps',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
    ]
    seek('S_first', 'S_entry', 2)
    checks += ['S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
               'perrorcall_first.RESUME = MOD_ASSIGN_SELECTED_WARNING pintegeroperation n_left_bits 12 1',
               'perrorcall_first.TARGET = eps', 'perrorcall_first.LEVEL = 8192',
               'perrorcall_first.MESSAGE = $ptascii("Implicit conversion from float 12.5 to int loses precision")',
               '$error_call_valid(S_first, perrorcall_first)', '$call_descriptors_valid(S_first)']
    seek('S_first_entered', 'S_first', 3)
    checks += ['$modassign_selected_entered(S_first_entered.FRAMES)', '$call_descriptors_valid(S_first_entered)']
    seek('S_right', 'S_first_entered', 4)
    checks += ['S_right.TODO = (MOD_ASSIGN_SELECTED_WARNING pintegeroperation n_left_bits 12 1) :: ptask_tail*',
               '$modassign_selected_right_warning_plan(S_right) = (' + marker(0) + ')',
               'n_right_bits = 4602678819172646912', '$float_long(n_right_bits, true) = (0, [PRECISIONLOSS])',
               '$modassign_selected_warning_right(S_right, pintegeroperation) = eps',
               '$lookup(S_right.ENV, $ptascii("right")) = (n_new_right)',
               'n_old_right =/= n_new_right', 'S_right.STORE[n_old_right] = DEFINED (PINT 5)',
               'S_right.STORE[n_left] = DEFINED (PINT 99)', 'S_right.STORE[n_calls] = DEFINED (PINT 1)',
               '$integer_pointer_select(S_right, pintegeroperation.RIGHT) = (INTEGER_CELL n_new_right)',
               '$integer_pointer_value(S_right, pintegeroperation.RIGHTPOINTER) = (PFLOAT n_right_bits)',
               '$modassign_selected_right_warning_snapshot(S_right, pintegeroperation, n_right_bits)',
               '$heap_owners($heap_prune($heap_graph(S_right)), HCELL n_old_right) = 1',
               '$heap_owners($heap_prune($heap_graph(S_right)), HCELL n_new_right) = 2',
               '$call_descriptors_valid(S_right)', '$heap_valid($heap_graph(S_right))',
               '$modassign_selected_right_warning_plan(S_right[.ORIGIN = eps]) = eps',
               '$modassign_selected_right_warning_plan(S_right[.CODE = eps]) = eps',
               '$modassign_selected_right_warning_plan(S_right[.TODO = eps]) = eps',
               '$modassign_selected_right_warning_plan(S_right[.REFCELLS = eps]) = eps',
               '$modassign_selected_right_warning_plan(S_right[.ALLOCATIONS = eps]) = eps',
               '$modassign_selected_right_warning_plan(S_right[.PROPREFS = [{CELL n_new_right, SOURCES eps}]]) = eps',
               'S_quiet = S_right[.STORE[n_new_right] = DEFINED (PINT 5)]',
               '$modassign_selected_warning_right(S_quiet, pintegeroperation) = (5)',
               '$modassign_selected_right_warning_plan(S_quiet) = eps',
               '~$modassign_selected_right_warning_valid(S_right, pintegeroperation, n_left_bits, 12, 4617878467915022336, 5, 0)',
               '~$modassign_selected_right_warning_valid(S_right, pintegeroperation, n_left_bits, 12, n_right_bits, 1, 0)',
               '~$modassign_selected_right_warning_valid(S_right, pintegeroperation, n_left_bits, 12, 18446744073709551616, 0, 0)',
               '~' + valid('S_right', 2),
               '~$modassign_selected_right_warning_valid(S_right, pintegeroperation[.OP = ADD], n_left_bits, 12, n_right_bits, 0, 0)',
               '~$modassign_selected_right_warning_valid(S_right, pintegeroperation[.LINE = 24], n_left_bits, 12, n_right_bits, 0, 0)',
               '$modassign_selected_right_warning_snapshot(S_right, pintegeroperation[.RIGHTPOINTER = INTEGER_CELL n_new_right], n_right_bits)',
               '~$modassign_selected_right_warning_valid(S_right, pintegeroperation[.RIGHTPOINTER = INTEGER_CELL n_new_right], n_left_bits, 12, n_right_bits, 0, 0)',
               'PhpStep: S_right ~> S_capture_raw',
               'S_capture_raw = S_right[.TODO = (' + marker(0) + ') :: ptask_tail*]']
    step('S_capture', 'S_right')
    checks += ['S_capture = S_capture_raw', '$modassign_selected_rhs_frontier(S_capture, 5)',
               valid('S_capture', 0), '$task_nodes(' + marker(0) + ') = eps',
               '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))']
    step('S_second', 'S_capture')
    checks += ['S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
               '$modassign_selected_rhs_frontier(S_second, 6)', 'perrorcall_second.RESUME = ' + marker(1),
               'perrorcall_second.TARGET = eps', 'perrorcall_second.LEVEL = 8192', 'perrorcall_second.LINE = 25',
               'perrorcall_second.MESSAGE = $ptascii("Implicit conversion from float 0.5 to int loses precision")',
               '$error_call_valid(S_second, perrorcall_second)',
               '~$error_call_valid(S_second, perrorcall_second[.LEVEL = 2])',
               '~$error_call_valid(S_second, perrorcall_second[.LINE = 24])',
               '$call_descriptors_valid(S_second)', '$heap_valid($heap_graph(S_second))']
    seek('S_second_entered', 'S_second', 7)
    checks += ['$modassign_selected_rhs_entered(S_second_entered.FRAMES)', '$call_descriptors_valid(S_second_entered)']
    seek('S_return', 'S_second_entered', 8)
    checks += ['S_return.TODO = (' + marker(1) + ') :: ptask_tail*',
               'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
               '$lookup(S_return.ENV, $ptascii("left")) = (n_new_left)',
               '$lookup(S_return.ENV, $ptascii("leftAlias")) = (n_left)',
               '$lookup(S_return.ENV, $ptascii("right")) = (n_new_right)',
               'S_return.STORE[n_left] = DEFINED (PINT 88)', 'S_return.STORE[n_new_left] = DEFINED (PINT 77)',
               'S_return.STORE[n_old_right] = DEFINED (PINT 5)', 'S_return.STORE[n_new_right] = DEFINED (PINT 5)',
               'S_return.STORE[n_v] = DEFINED (PINT 100)', 'S_return.STORE[n_calls] = DEFINED (PINT 2)',
               '$modassign_selected_warning_right(S_return, pintegeroperation) = (5)',
               '~$modassign_selected_right_warning_snapshot(S_return, pintegeroperation, n_right_bits)',
               valid('S_return', 1), '~' + valid('S_return', 0),
               '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_left) = 1',
               '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_new_left) = 2',
               '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_new_right) = 2',
               '$modassign_selected_rhs_diagnostics(S_return.EVENTS, "Deprecated") = 0',
               '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
               'PhpStep: S_return ~> S_atomic',
               'S_atomic = $integer_result(S_return[.TODO = ptask_tail*][.RESULT = KNOWN PNULL], INTZERO, 25)',
               'S_atomic.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 25',
               'S_atomic.STORE = S_return.STORE', 'S_atomic.ENV = S_return.ENV',
               'S_atomic.REFCELLS = S_return.REFCELLS', 'S_atomic.EVENTS = S_return.EVENTS',
               'S_atomic.ALLOCATIONS = S_return.ALLOCATIONS']
    step('S_error', 'S_return')
    checks += ['$modassign_selected_rhs_frontier(S_error, 10)',
               'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
               '$throwable_live(S_error, n_error)', '$object_name(S_error, n_error) = $ptascii("DivisionByZeroError")',
               '$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("Modulo by zero"))',
               '$throwable_field(S_error, n_error, "line") = PINT 25', '$throwable_previous_id(S_error, n_error) = eps',
               '$heap_owners($heap_prune($heap_graph(S_error)), HOBJECT n_error) = 1',
               'S_error.STORE = S_return.STORE', 'S_error.ENV = S_return.ENV',
               'S_error.ARRAYS[0:|S_return.ARRAYS|] = S_return.ARRAYS',
               'S_error.STRINGDATA[0:|S_return.STRINGDATA|] = S_return.STRINGDATA',
               '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
               'S_done = $drive_steps(S_error, 4000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
               'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
               'S_done.STORE[n_left] = DEFINED (PINT 6)', 'S_done.STORE[n_old_right] = DEFINED (PINT 4)',
               'S_done.STORE[n_new_left] = DEFINED (PINT 8)', 'S_done.STORE[n_new_right] = DEFINED (PINT 9)',
               'S_done.STORE[n_v] = DEFINED (PINT 100)', 'S_done.STORE[n_calls] = DEFINED (PINT 2)',
               '$lookup(S_done.ENV, $ptascii("e")) = (n_e)', 'S_done.STORE[n_e] = DEFINED (POBJECT n_error)',
               '$modassign_selected_rhs_diagnostics(S_done.EVENTS, "Deprecated") = 0',
               '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
               '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
               '$drive_steps(S_right, 0) = S_right[.COMPLETION = BUDGET]',
               '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]']
    assert len(checks) == len(set(checks))
    return checks
