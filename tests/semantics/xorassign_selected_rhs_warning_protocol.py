#!/usr/bin/env python3
"""Reached protected XOR text and cancellation before its precision diagnostic."""
import base64
import json
import xorassign_selected_warning_protocol as shared
import xorassign_selected_rhs_warning_cases as cases

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $xorassign_selected_rhs_task(ptask) : bool
def $xorassign_selected_rhs_task(XOR_ASSIGN_SELECTED_WARNING pintegeroperation n_bits i_left n_stage) = true
def $xorassign_selected_rhs_task(XOR_ASSIGN_SELECTED_RIGHT_WARNING pintegeroperation n_bits i_left pintegerconversion n_cursor) = true
def $xorassign_selected_rhs_task(ERROR_HANDLER_INVOKE perrorcall) = $xorassign_selected_rhs_task(perrorcall.RESUME)
def $xorassign_selected_rhs_task(ERROR_HANDLER_RESULT perrorcall) = $xorassign_selected_rhs_task(perrorcall.RESUME)
def $xorassign_selected_rhs_task(ERROR_HANDLER_CLEAN perrorcall) = $xorassign_selected_rhs_task(perrorcall.RESUME)
def $xorassign_selected_rhs_task(ptask) = false -- otherwise
dec $xorassign_selected_rhs_tasks(ptask*) : bool
def $xorassign_selected_rhs_tasks(eps) = false
def $xorassign_selected_rhs_tasks(ptask :: ptask_tail*) = ($xorassign_selected_rhs_task(ptask) \/ $xorassign_selected_rhs_tasks(ptask_tail*))
dec $xorassign_selected_rhs_handler_frame(pframe, nat) : bool
def $xorassign_selected_rhs_handler_frame(pframe, 0) = $xorassign_selected_handler_frame(pframe)
def $xorassign_selected_rhs_handler_frame(pframe, n) = true
  -- if n = 1 \/ n = 2
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = XOR_ASSIGN_SELECTED_RIGHT_WARNING pintegeroperation n_bits i_left pintegerconversion n
  -- if perrorcall.TARGET =/= eps
def $xorassign_selected_rhs_handler_frame(pframe, n) = false -- otherwise
dec $xorassign_selected_rhs_entered(pframe*, nat) : bool
def $xorassign_selected_rhs_entered(eps, n) = false
def $xorassign_selected_rhs_entered(pframe :: pframe_tail*, n) = ($xorassign_selected_rhs_handler_frame(pframe, n) \/ $xorassign_selected_rhs_entered(pframe_tail*, n))
dec $xorassign_selected_rhs_frontier(pstate, nat) : bool
def $xorassign_selected_rhs_frontier(S, n) = $xorassign_selected_frontier(S, n) -- if $(n <= 4)
def $xorassign_selected_rhs_frontier(S, 5) = true
  -- if S.TODO = (XOR_ASSIGN_SELECTED_RIGHT_WARNING pintegeroperation n_bits i_left pintegerconversion 0) :: ptask_tail*
def $xorassign_selected_rhs_frontier(S, 6) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = XOR_ASSIGN_SELECTED_RIGHT_WARNING pintegeroperation n_bits i_left pintegerconversion 1
  -- if perrorcall.TARGET = eps
def $xorassign_selected_rhs_frontier(S, 7) = true
  -- if S.TODO = (XOR_ASSIGN_SELECTED_RIGHT_WARNING pintegeroperation n_bits i_left pintegerconversion 1) :: ptask_tail*
def $xorassign_selected_rhs_frontier(S, 8) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = XOR_ASSIGN_SELECTED_RIGHT_WARNING pintegeroperation n_bits i_left pintegerconversion 2
  -- if perrorcall.TARGET = eps
def $xorassign_selected_rhs_frontier(S, 9) = true
  -- if S.TODO = (XOR_ASSIGN_SELECTED_RIGHT_WARNING pintegeroperation n_bits i_left pintegerconversion 2) :: ptask_tail*
def $xorassign_selected_rhs_frontier(S, 10) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprAssignOpBitwiseXor expression_left expression_right metadata)
  -- if S.RESULT = KNOWN (PINT i)
  -- if ~$xorassign_selected_rhs_tasks(S.TODO)
def $xorassign_selected_rhs_frontier(S, 11) = (S.CURRENT =/= eps /\ $xorassign_selected_rhs_entered(S.FRAMES, 1))
def $xorassign_selected_rhs_frontier(S, 12) = (S.CURRENT =/= eps /\ $xorassign_selected_rhs_entered(S.FRAMES, 2))
def $xorassign_selected_rhs_frontier(S, 13) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if ~$xorassign_selected_rhs_tasks(S.TODO)
def $xorassign_selected_rhs_frontier(S, n) = false -- otherwise
dec $xorassign_selected_rhs_seek(pstate, nat, nat) : pstate
def $xorassign_selected_rhs_seek(S, n_stage, n) = S -- if $xorassign_selected_rhs_frontier(S, n_stage)
def $xorassign_selected_rhs_seek(S, n_stage, n) = S
  -- if ~$xorassign_selected_rhs_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $xorassign_selected_rhs_seek(S, n_stage, n) = S
  -- if ~$xorassign_selected_rhs_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $xorassign_selected_rhs_seek(S, n_stage, n) = $xorassign_selected_rhs_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$xorassign_selected_rhs_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    old = lambda stage: f'XOR_ASSIGN_SELECTED_WARNING pintegeroperation n_bits i_left {stage}'
    marker = lambda cursor: f'XOR_ASSIGN_SELECTED_RIGHT_WARNING pintegeroperation n_bits i_left pintegerconversion {cursor}'
    valid = lambda state, cursor: f'$xorassign_selected_rhs_warning_valid({state}, pintegeroperation, n_bits, i_left, pintegerconversion, {cursor})'
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')', 'S_initial.COMPLETION = BUDGET']
    def seek(state, before, stage):
        checks.extend([f'{state}_found = $xorassign_selected_rhs_seek({before}, {stage}, 4000)',
                       f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
                       f'{state} = {state}_found[.COMPLETION = NORMAL]', f'$xorassign_selected_rhs_frontier({state}, {stage})'])
    def step(state, before):
        checks.extend([f'{state}_budget = $drive_steps({before}, 1)', f'{state}_budget.COMPLETION = BUDGET', f'{state} = {state}_budget[.COMPLETION = NORMAL]'])
    seek('S_entry', 'S_initial', 0)
    checks += [
        '$xorassign_selected_warning_plan(S_entry) = (' + old(0) + ')',
        'n_bits = 4623226492472524800', 'i_left = 12',
        '$xorassign_selected_warning_source(S_entry, pintegeroperation)', '$xorassign_selected_warning_snapshot(S_entry, pintegeroperation, n_bits)',
        'pintegeroperation.OP = BITXOR', '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23', 'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_left', 'pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_right', 'n_left =/= n_right',
        '$lookup(S_entry.ENV, $ptascii("leftAlias")) = (n_left)', '$lookup(S_entry.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("replacementLeft")) = (n_replacement_left)', '$lookup(S_entry.ENV, $ptascii("replacementRight")) = (n_replacement_right)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)', '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)', 'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        'S_entry.STORE[n_left] = DEFINED (PFLOAT n_bits)', 'S_entry.STORE[n_right] = DEFINED (PINT 2)',
        'S_entry.STORE[n_replacement_left] = DEFINED (PINT 77)', 'S_entry.STORE[n_replacement_right] = DEFINED (PINT 7)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)', 'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 2', '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 2',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
    ]
    step('S_begin', 'S_entry')
    checks += ['S_begin.TODO = (' + old(0) + ') :: ptask_tail*']
    seek('S_first_call', 'S_begin', 2)
    checks += ['S_first_call.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*', 'perrorcall_first.RESUME = ' + old(1),
               'perrorcall_first.LEVEL = 8192', 'perrorcall_first.LINE = 25', 'perrorcall_first.TARGET = eps', '$error_call_valid(S_first_call, perrorcall_first)']
    seek('S_first_entered', 'S_first_call', 3)
    checks += ['$xorassign_selected_rhs_entered(S_first_entered.FRAMES, 0)', '$call_descriptors_valid(S_first_entered)']
    seek('S_right', 'S_first_entered', 4)
    checks += [
        'S_right.TODO = (' + old(1) + ') :: ptask_tail*', '$xorassign_selected_warning_valid(S_right, pintegeroperation, n_bits, i_left, 1)',
        '$lookup(S_right.ENV, $ptascii("left")) = (n_left)', '$lookup(S_right.ENV, $ptascii("right")) = (n_replacement_right)',
        'S_right.STORE[n_left] = DEFINED (PINT 99)', 'S_right.STORE[n_right] = DEFINED pvalue_right',
        '$string_bytes(pvalue_right) = ($ptascii("5.5tail"))', '$string_carrier_valid(S_right, pvalue_right)',
        '$integer_pointer_value(S_right, pintegeroperation.RIGHTPOINTER) = (pvalue_right)',
        '$integer_pointer_value(S_right, INTEGER_CV ($ptascii("right"))) = (PINT 7)',
        '$xorassign_selected_warning_right(S_right, pintegeroperation) = eps', '$xorassign_selected_warning_failure_operands(S_right, pintegeroperation) = eps',
        '$xorassign_selected_rhs_warning_snapshot(S_right, pintegeroperation) = (pintegerconversion)',
        '$integer_conversion(pvalue_right) = (pintegerconversion)', 'pintegerconversion.INPUT = pvalue_right', 'pintegerconversion.VALUE = 5',
        'pintegerconversion.NOTICES = [(2, $ptascii("A non-numeric value encountered")), (8192, $ptascii("Implicit conversion from float-string \\"5.5tail\\" to int loses precision"))]',
        '$xorassign_selected_rhs_warning_plan(S_right) = (' + marker(0) + ')', valid('S_right', 0),
        '$heap_owners($heap_prune($heap_graph(S_right)), HCELL n_left) = 2', '$heap_owners($heap_prune($heap_graph(S_right)), HCELL n_right) = 1',
        '$heap_owners($heap_prune($heap_graph(S_right)), HCELL n_replacement_right) = 2', '$call_descriptors_valid(S_right)', '$heap_valid($heap_graph(S_right))',
        '$xorassign_selected_rhs_warning_conversion(PSTRING ($ptascii("5.5"))) = eps',
        '$xorassign_selected_rhs_warning_conversion(PSTRING ($ptascii("5tail"))) = eps',
        '$xorassign_selected_rhs_warning_conversion(PSTRING ($ptascii("bad"))) = eps',
        '$xorassign_selected_rhs_warning_plan(S_right[.ORIGIN = eps]) = eps', '$xorassign_selected_rhs_warning_plan(S_right[.CODE = eps]) = eps',
        '$xorassign_selected_rhs_warning_plan(S_right[.TODO = (' + old(0) + ') :: ptask_tail*]) = eps',
        '$xorassign_selected_rhs_warning_plan(S_right[.STORE[n_right] = DEFINED (PINT 7)]) = eps',
        '$xorassign_selected_rhs_warning_plan(S_right[.ALLOCATIONS = eps]) = eps', '$xorassign_selected_rhs_warning_plan(S_right[.REFCELLS = eps]) = eps',
        '$xorassign_selected_rhs_warning_plan(S_right[.PROPREFS = [{CELL n_right, SOURCES eps}]]) = eps',
        '$xorassign_selected_rhs_warning_plan(S_right[.PROPREFS = [{CELL n_left, SOURCES eps}]]) = eps',
        '~$xorassign_selected_rhs_warning_valid(S_right, pintegeroperation[.OP = BITOR], n_bits, i_left, pintegerconversion, 0)',
        '~$xorassign_selected_rhs_warning_valid(S_right, pintegeroperation[.LINE = 24], n_bits, i_left, pintegerconversion, 0)',
        '~$xorassign_selected_rhs_warning_valid(S_right, pintegeroperation[.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))], n_bits, i_left, pintegerconversion, 0)',
        '~$xorassign_selected_rhs_warning_valid(S_right, pintegeroperation, n_bits, i_left, pintegerconversion[.VALUE = 6], 0)',
        '~' + valid('S_right', 3),
        'PhpStep: S_right ~> S_capture_atomic', 'S_capture_atomic = S_right[.TODO = (' + marker(0) + ') :: ptask_tail*]',
    ]
    step('S_capture', 'S_right')
    checks += ['S_capture = S_capture_atomic', '$xorassign_selected_rhs_frontier(S_capture, 5)', valid('S_capture', 0),
               '$task_nodes(' + marker(0) + ') = eps', '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))']
    step('S_warning', 'S_capture')
    checks += [
        '$xorassign_selected_rhs_frontier(S_warning, 6)', 'S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall_warning) :: ptask_tail*',
        'perrorcall_warning.RESUME = ' + marker(1), 'perrorcall_warning.TARGET = eps', 'perrorcall_warning.SITE = pintegeroperation.SITE',
        'perrorcall_warning.LEVEL = 2', 'perrorcall_warning.LINE = 25', 'perrorcall_warning.MESSAGE = ($ptascii("A non-numeric value encountered"))',
        '$error_call_valid(S_warning, perrorcall_warning)', '$call_descriptors_valid(S_warning)',
        '~$error_call_valid(S_warning, perrorcall_warning[.LEVEL = 8192])', '~$error_call_valid(S_warning, perrorcall_warning[.LINE = 24])',
        '~$error_call_valid(S_warning, perrorcall_warning[.RESUME = ' + marker(2) + '])',
    ]
    seek('S_warning_entered', 'S_warning', 11)
    checks += ['$xorassign_selected_rhs_entered(S_warning_entered.FRAMES, 1)', '$call_descriptors_valid(S_warning_entered)']
    seek('S_throw', 'S_warning_entered', 13)
    checks += [
        'S_throw.TODO = (THROW_SEARCH n_second) :: ptask_caller*', 'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps',
        '~$xorassign_selected_rhs_tasks(S_throw.TODO)', '~$xorassign_selected_tasks(S_throw.TODO)',
        '$lookup(S_throw.ENV, $ptascii("leftAlias")) = (n_left)', '$lookup(S_throw.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_throw.ENV, $ptascii("left")) = (n_replacement_left)', '$lookup(S_throw.ENV, $ptascii("right")) = (n_replacement_right)',
        'S_throw.STORE[n_left] = DEFINED (PINT 88)', 'S_throw.STORE[n_right] = DEFINED (PINT 7)',
        'S_throw.STORE[n_replacement_left] = DEFINED (PINT 77)', 'S_throw.STORE[n_replacement_right] = DEFINED (PINT 7)',
        'S_throw.STORE[n_v] = DEFINED (PINT 100)', 'S_throw.STORE[n_calls] = DEFINED (PINT 2)',
        '$xorassign_selected_rhs_warning_snapshot(S_throw, pintegeroperation) = eps', '~' + valid('S_throw', 0), valid('S_throw', 1),
        '$string_bytes(pintegerconversion.INPUT) = ($ptascii("5.5tail"))', '$string_carrier_valid(S_throw, pintegerconversion.INPUT)',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_left) = 1', '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_right) = 1',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_replacement_left) = 2', '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_replacement_right) = 2',
        '$throwable_live(S_throw, n_second)', '$throwable_previous_id(S_throw, n_second) = eps', '$throwable_field(S_throw, n_second, "line") = PINT 20',
        '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]', '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
        '$xorassign_selected_diagnostics(S_throw.EVENTS, "Warning") = 0', '$xorassign_selected_diagnostics(S_throw.EVENTS, "Deprecated") = 0',
        'S_throw.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA', '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
        'S_done = $drive_steps(S_throw, 4000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_left] = DEFINED (PINT 6)', 'S_done.STORE[n_right] = DEFINED (PINT 4)',
        'S_done.STORE[n_replacement_left] = DEFINED (PINT 8)', 'S_done.STORE[n_replacement_right] = DEFINED (PINT 9)',
        'S_done.STORE[n_v] = DEFINED (PINT 100)', 'S_done.STORE[n_calls] = DEFINED (PINT 2)',
        '$lookup(S_done.ENV, $ptascii("leftAlias")) = (n_left)', '$lookup(S_done.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_replacement_left)', '$lookup(S_done.ENV, $ptascii("right")) = (n_replacement_right)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_left) = 1', '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_right) = 1',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement_left) = 2', '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement_right) = 2',
        '$xorassign_selected_diagnostics(S_done.EVENTS, "Warning") = 0', '$xorassign_selected_diagnostics(S_done.EVENTS, "Deprecated") = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])', '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]', '$drive_steps(S_warning, 0) = S_warning[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
