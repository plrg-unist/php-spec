#!/usr/bin/env python3
"""Selected right shift target, delayed count and negative-count failure."""
import base64
import json
import arithmetic_warning_protocol as shared
import shiftassign_selected_warning_cases as cases

CASES = ('shiftassign-selected-warning-negative-count',)
HELPERS = shared.HELPERS + r'''
dec $shiftassign_selected_task(ptask) : bool
def $shiftassign_selected_task(SHIFT_ASSIGN_SELECTED_WARNING pintegeroperation n_bits i_left n_stage) = true
def $shiftassign_selected_task(ERROR_HANDLER_INVOKE perrorcall) = $shiftassign_selected_task(perrorcall.RESUME)
def $shiftassign_selected_task(ERROR_HANDLER_RESULT perrorcall) = $shiftassign_selected_task(perrorcall.RESUME)
def $shiftassign_selected_task(ERROR_HANDLER_CLEAN perrorcall) = $shiftassign_selected_task(perrorcall.RESUME)
def $shiftassign_selected_task(ptask) = false -- otherwise
dec $shiftassign_selected_tasks(ptask*) : bool
def $shiftassign_selected_tasks(eps) = false
def $shiftassign_selected_tasks(ptask :: ptask_tail*) = ($shiftassign_selected_task(ptask) \/ $shiftassign_selected_tasks(ptask_tail*))
dec $shiftassign_selected_handler_frame(pframe) : bool
def $shiftassign_selected_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = SHIFT_ASSIGN_SELECTED_WARNING pintegeroperation n_bits i_left 1
  -- if perrorcall.TARGET =/= eps
def $shiftassign_selected_handler_frame(pframe) = false -- otherwise
dec $shiftassign_selected_entered(pframe*) : bool
def $shiftassign_selected_entered(eps) = false
def $shiftassign_selected_entered(pframe :: pframe_tail*) = ($shiftassign_selected_handler_frame(pframe) \/ $shiftassign_selected_entered(pframe_tail*))
dec $shiftassign_selected_frontier(pstate, nat) : bool
def $shiftassign_selected_frontier(S, 0) = ($shiftassign_selected_warning_plan(S) =/= eps)
def $shiftassign_selected_frontier(S, 1) = true
  -- if S.TODO = (SHIFT_ASSIGN_SELECTED_WARNING pintegeroperation n_bits i_left 0) :: ptask_tail*
def $shiftassign_selected_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = SHIFT_ASSIGN_SELECTED_WARNING pintegeroperation n_bits i_left 1
  -- if perrorcall.TARGET = eps
def $shiftassign_selected_frontier(S, 3) = (S.CURRENT =/= eps /\ $shiftassign_selected_entered(S.FRAMES))
def $shiftassign_selected_frontier(S, 4) = true
  -- if S.TODO = (SHIFT_ASSIGN_SELECTED_WARNING pintegeroperation n_bits i_left 1) :: ptask_tail*
def $shiftassign_selected_frontier(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprAssignOpShiftRight expression_left expression_right metadata)
  -- if S.RESULT = KNOWN (PINT i)
  -- if ~$shiftassign_selected_tasks(S.TODO)
def $shiftassign_selected_frontier(S, 6) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if ~$shiftassign_selected_tasks(S.TODO)
def $shiftassign_selected_frontier(S, n) = false -- otherwise
dec $shiftassign_selected_seek(pstate, nat, nat) : pstate
def $shiftassign_selected_seek(S, n_stage, n) = S -- if $shiftassign_selected_frontier(S, n_stage)
def $shiftassign_selected_seek(S, n_stage, n) = S
  -- if ~$shiftassign_selected_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $shiftassign_selected_seek(S, n_stage, n) = S
  -- if ~$shiftassign_selected_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $shiftassign_selected_seek(S, n_stage, n) = $shiftassign_selected_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$shiftassign_selected_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
dec $shiftassign_selected_diagnostic(pevent, text) : nat
def $shiftassign_selected_diagnostic(DIAGNOSTIC text n* z, text) = 1
def $shiftassign_selected_diagnostic(DIAGNOSTIC_SOURCE n_source text n* z, text) = 1
def $shiftassign_selected_diagnostic(DIAGNOSTIC_STACK text n* z n_trace*, text) = 1
def $shiftassign_selected_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n* z n_trace*, text) = 1
def $shiftassign_selected_diagnostic(pevent, text) = 0 -- otherwise
dec $shiftassign_selected_diagnostics(pevent*, text) : nat
def $shiftassign_selected_diagnostics(eps, text) = 0
def $shiftassign_selected_diagnostics(pevent :: pevent_tail*, text) = $($shiftassign_selected_diagnostic(pevent, text) + $shiftassign_selected_diagnostics(pevent_tail*, text))

'''


def conditions(name, program, path, stdout):
    assert name in CASES
    marker = lambda stage, op='pintegeroperation': f'SHIFT_ASSIGN_SELECTED_WARNING {op} n_bits i_left {stage}'
    valid = lambda state, stage: f'$shiftassign_selected_warning_valid({state}, pintegeroperation, n_bits, i_left, {stage})'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $shiftassign_selected_seek({before}, {stage}, 4000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$shiftassign_selected_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$shiftassign_selected_warning_plan(S_entry) = (' + marker(0) + ')',
        '$shiftassign_warning_plan(S_entry) = eps',
        '$shiftassign_selected_warning_source(S_entry, pintegeroperation)',
        '$shiftassign_selected_warning_snapshot(S_entry, pintegeroperation, n_bits)',
        'n_bits = 13846598529327300608', 'i_left = (-12)',
        'pintegeroperation.OP = SHIFTRIGHT', '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_target',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S_entry.ENV, $ptascii("leftAlias")) = (n_target)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_old_right)',
        '$lookup(S_entry.ENV, $ptascii("rightAlias")) = (n_old_right)',
        '$lookup(S_entry.ENV, $ptascii("replacementLeft")) = (n_replacement_left)',
        '$lookup(S_entry.ENV, $ptascii("replacementRight")) = (n_replacement_right)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'S_entry.STORE[n_target] = DEFINED (PFLOAT n_bits)',
        'S_entry.STORE[n_old_right] = DEFINED (PINT 2)',
        'S_entry.STORE[n_replacement_left] = DEFINED (PINT 77)',
        'S_entry.STORE[n_replacement_right] = DEFINED (PINT $(-1))',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', 'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'n_target <- S_entry.REFCELLS', 'n_old_right <- S_entry.REFCELLS',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_target) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_old_right) = 2',
        '$shiftassign_selected_warning_right(S_entry, pintegeroperation) = (2)',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
    ]
    checks += [
        'S_entry.TODO = ptask_original :: ptask_original_tail*',
        '$shiftassign_selected_warning_plan(S_entry[.ORIGIN = eps]) = eps',
        '$shiftassign_selected_warning_plan(S_entry[.TODO = (COMPOUND_APPLY SHIFTLEFT (BASE_VALUE pintegeroperation.LEFT) false 25) :: ptask_original_tail*]) = eps',
        '$shiftassign_selected_warning_plan(S_entry[.TODO = (COMPOUND_APPLY MODULO (BASE_VALUE pintegeroperation.LEFT) false 25) :: ptask_original_tail*]) = eps',
        '$shiftassign_selected_warning_plan(S_entry[.TODO = (COMPOUND_APPLY SHIFTRIGHT (BASE_VALUE pintegeroperation.LEFT) false 24) :: ptask_original_tail*]) = eps',
        '$shiftassign_selected_warning_plan(S_entry[.REFCELLS = eps]) = eps',
        '$shiftassign_selected_warning_plan(S_entry[.ALLOCATIONS = eps]) = eps',
        '$shiftassign_selected_warning_plan(S_entry[.PROPREFS = [{CELL n_target, SOURCES eps}]]) = eps',
        '$shiftassign_selected_warning_plan(S_entry[.PROPREFS = [{CELL n_old_right, SOURCES eps}]]) = eps',
        '$shiftassign_selected_warning_plan(S_entry[.STORE[n_target] = UNDEFINED]) = eps',
        '$shiftassign_selected_warning_plan(S_entry[.STORE[n_old_right] = UNDEFINED]) = eps',
        '$shiftassign_selected_warning_plan(S_entry[.STORE[n_target] = DEFINED (PINT $(-12))]) = eps',
        '$shiftassign_selected_warning_plan(S_entry[.STORE[n_old_right] = DEFINED (PFLOAT n_bits)]) = eps',
        '$shiftassign_selected_warning_plan(S_entry[.ERRORHANDLER.CALLBACK = eps]) = eps',
        '$shiftassign_selected_warning_plan(S_entry[.ERRORHANDLER.LEVELS = 2]) = eps',
        '~$shiftassign_selected_warning_valid(S_entry, pintegeroperation[.OP = SHIFTLEFT], n_bits, i_left, 0)',
        '~$shiftassign_selected_warning_valid(S_entry, pintegeroperation[.LINE = 24], n_bits, i_left, 0)',
        '~$shiftassign_selected_warning_valid(S_entry, pintegeroperation[.RIGHTPOINTER = INTEGER_CELL n_old_right], n_bits, i_left, 0)',
        '~$shiftassign_selected_warning_valid(S_entry, pintegeroperation, n_bits, 12, 0)',
        '~$shiftassign_selected_warning_valid(S_entry, pintegeroperation, n_bits, i_left, 2)',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture.TODO = (' + marker(0) + ') :: ptask_tail*',
        'S_capture.RESULT = KNOWN PNULL', 'S_capture.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_capture.LOCATION = ROOT n_target', valid('S_capture', 0),
        '$task_nodes(' + marker(0) + ') = eps',
        'S_capture.STORE = S_entry.STORE', 'S_capture.ENV = S_entry.ENV',
        '$shiftassign_selected_diagnostics(S_capture.EVENTS, "Deprecated") = 0',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(1), 'perrorcall.TARGET = eps',
        'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = $ptascii("Implicit conversion from float -12.5 to int loses precision")',
        '$error_call_valid(S_dispatch, perrorcall)', '$call_descriptors_valid(S_dispatch)',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += ['S_entered.CURRENT =/= eps', 'S_entered.FRAMES =/= eps', '$call_descriptors_valid(S_entered)']
    seek('S_return', 'S_entered', 4)
    checks += [
        'S_return.TODO = (' + marker(1) + ') :: ptask_tail*',
        'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
        '$lookup(S_return.ENV, $ptascii("leftAlias")) = (n_target)',
        '$lookup(S_return.ENV, $ptascii("rightAlias")) = (n_old_right)',
        '$lookup(S_return.ENV, $ptascii("left")) = (n_replacement_left)',
        '$lookup(S_return.ENV, $ptascii("right")) = (n_replacement_right)',
        'S_return.STORE[n_target] = DEFINED (PINT 88)',
        'S_return.STORE[n_old_right] = DEFINED (PINT 2)',
        'S_return.STORE[n_replacement_left] = DEFINED (PINT 77)',
        'S_return.STORE[n_replacement_right] = DEFINED (PINT $(-1))',
        'S_return.STORE[n_calls] = DEFINED (PINT 1)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
        '$integer_pointer_value(S_return, pintegeroperation.LEFTPOINTER) = (PINT 88)',
        '$integer_pointer_value(S_return, pintegeroperation.RIGHTPOINTER) = (PINT $(-1))',
        '$integer_pointer_value(S_return, INTEGER_CELL n_old_right) = (PINT 2)',
        valid('S_return', 1), '~' + valid('S_return', 0),
        '$shiftassign_selected_warning_target(S_return, pintegeroperation)',
        '~$shiftassign_selected_warning_target(S_return[.PROPREFS = [{CELL n_target, SOURCES eps}]], pintegeroperation)',
        '$shiftassign_selected_warning_valid(S_return[.PROPREFS = [{CELL n_target, SOURCES eps}]], pintegeroperation, n_bits, i_left, 1)',
        '$shiftassign_selected_warning_right(S_return[.STORE[n_old_right] = DEFINED (PINT 9)], pintegeroperation) = (-1)',
        '$shiftassign_selected_warning_right(S_return[.STORE[n_replacement_right] = UNDEFINED], pintegeroperation) = eps',
        '$shiftassign_selected_warning_valid(S_return[.STORE[n_replacement_right] = UNDEFINED], pintegeroperation, n_bits, i_left, 1)',

        '$shiftassign_selected_warning_right(S_return, pintegeroperation) = (-1)',
        '$integer_binary(SHIFTRIGHT, i_left, (-1)) = NEGSHIFT', '$integer_binary(SHIFTRIGHT, i_left, 2) = IRESULT $(-3)',
        'pintegeroperation_old_right = pintegeroperation[.RIGHTPOINTER = INTEGER_CELL n_old_right]',
        '~$shiftassign_selected_warning_source(S_return, pintegeroperation_old_right)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_old_right) = 1',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_replacement_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_replacement_right) = 2',
        '$shiftassign_selected_diagnostics(S_return.EVENTS, "Deprecated") = 0',
        '$shiftassign_selected_diagnostics(S_return.EVENTS, "Warning") = 0',
        'S_return.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'PhpStep: S_return ~> S_atomic',
        'S_atomic = S_return[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.COMPLETION = THROWN "ArithmeticError" ($ptascii("Bit shift by negative number")) 25]',
    ]
    step('S_error', 'S_return')
    checks += [
        '$shiftassign_selected_frontier(S_error, 6)',
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        'S_error.RESULT = KNOWN PNULL', 'S_error.CURRENT = eps', 'S_error.FRAMES = eps',
        'n_error = |S_return.OBJECTS|', 'S_error.OBJECTS[n_error] = THROWABLE pthrowable',
        'pthrowable.KIND = "ArithmeticError"', 'pthrowable.ORIGIN = (pintegeroperation.SITE)',
        'S_error.OBJECTS = S_return.OBJECTS ++ [THROWABLE pthrowable]',
        '$throwable_field(S_error, n_error, "line") = PINT 25',
        '$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("Bit shift by negative number"))',
        '$throwable_previous_id(S_error, n_error) = eps', '$throwable_live(S_error, n_error)',
        '$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]',
        '$heap_owners($heap_prune($heap_graph(S_error)), HOBJECT n_error) = 1',
        'S_error.STORE = S_return.STORE', 'S_error.ENV = S_return.ENV',
        'S_error.REFCELLS = S_return.REFCELLS', 'S_error.EVENTS = S_return.EVENTS',
        'S_error.ARRAYS[0:|S_return.ARRAYS|] = S_return.ARRAYS',
        'S_error.STRINGDATA[0:|S_return.STRINGDATA|] = S_return.STRINGDATA',
        '$heap_owners($heap_prune($heap_graph(S_error)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S_error)), HCELL n_old_right) = 1',
        '$heap_owners($heap_prune($heap_graph(S_error)), HCELL n_replacement_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_error)), HCELL n_replacement_right) = 2',
        '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
        'S_done = $drive_steps(S_error, 4000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_target] = DEFINED (PINT 6)',
        'S_done.STORE[n_old_right] = DEFINED (PINT 4)',
        'S_done.STORE[n_replacement_left] = DEFINED (PINT 8)',
        'S_done.STORE[n_replacement_right] = DEFINED (PINT 9)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)', 'S_done.STORE[n_v] = DEFINED (PINT 100)',
        '$lookup(S_done.ENV, $ptascii("leftAlias")) = (n_target)',
        '$lookup(S_done.ENV, $ptascii("rightAlias")) = (n_old_right)',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_replacement_left)',
        '$lookup(S_done.ENV, $ptascii("right")) = (n_replacement_right)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_old_right) = 1',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement_right) = 2',
        '$shiftassign_selected_diagnostics(S_done.EVENTS, "Deprecated") = 0',
        '$shiftassign_selected_diagnostics(S_done.EVENTS, "Warning") = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
