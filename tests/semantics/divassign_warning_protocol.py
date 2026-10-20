#!/usr/bin/env python3
"""Reached selected-reference compound division captures, stores and cancellation."""
import base64
import json
import integer_operator_warning_protocol as shared
import divassign_warning_cases as cases

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''

dec $divassign_task(ptask) : bool
def $divassign_task(ARITHMETIC_DIVASSIGN_CONVERT pintegeroperation parithmeticphase) = true
def $divassign_task(ARITHMETIC_DIVASSIGN_WARNING pintegeroperation parithmeticphase pvalue pnumber n) = true
def $divassign_task(ERROR_HANDLER_INVOKE perrorcall) = $divassign_task(perrorcall.RESUME)
def $divassign_task(ERROR_HANDLER_RESULT perrorcall) = $divassign_task(perrorcall.RESUME)
def $divassign_task(ERROR_HANDLER_CLEAN perrorcall) = $divassign_task(perrorcall.RESUME)
def $divassign_task(ptask) = false -- otherwise
dec $divassign_tasks(ptask*) : bool
def $divassign_tasks(eps) = false
def $divassign_tasks(ptask :: ptask_tail*) = ($divassign_task(ptask) \/ $divassign_tasks(ptask_tail*))
dec $divassign_handler_frame(pframe, nat) : bool
def $divassign_handler_frame(pframe, 0) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_DIVASSIGN_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 1
  -- if perrorcall.TARGET =/= eps
def $divassign_handler_frame(pframe, 1) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_DIVASSIGN_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue pnumber_right 1
  -- if perrorcall.TARGET =/= eps
def $divassign_handler_frame(pframe, n) = false -- otherwise
dec $divassign_entered(pframe*, nat) : bool
def $divassign_entered(eps, n) = false
def $divassign_entered(pframe :: pframe_tail*, n) = ($divassign_handler_frame(pframe, n) \/ $divassign_entered(pframe_tail*, n))
dec $divassign_numeric(poperand) : bool
def $divassign_numeric(KNOWN (PINT i)) = true
def $divassign_numeric(KNOWN (PFLOAT n)) = true
def $divassign_numeric(poperand) = false -- otherwise
dec $divassign_frontier(pstate, nat) : bool
def $divassign_frontier(S, 0) = ($arithmetic_divassign_plan(S) =/= eps)
def $divassign_frontier(S, 1) = true
  -- if S.TODO = (ARITHMETIC_DIVASSIGN_CONVERT pintegeroperation ARITHMETIC_LEFT) :: ptask_tail*
def $divassign_frontier(S, 2) = true
  -- if S.TODO = (ARITHMETIC_DIVASSIGN_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 0) :: ptask_tail*
def $divassign_frontier(S, 3) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_DIVASSIGN_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 1
def $divassign_frontier(S, 4) = true
  -- if S.TODO = (ARITHMETIC_DIVASSIGN_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 1) :: ptask_tail*
def $divassign_frontier(S, 5) = true
  -- if S.TODO = (ARITHMETIC_DIVASSIGN_CONVERT pintegeroperation (ARITHMETIC_RIGHT pnumber)) :: ptask_tail*
def $divassign_frontier(S, 6) = true
  -- if S.TODO = (ARITHMETIC_DIVASSIGN_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue pnumber_right 0) :: ptask_tail*
def $divassign_frontier(S, 7) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_DIVASSIGN_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue pnumber_right 1
def $divassign_frontier(S, 8) = true
  -- if S.TODO = (ARITHMETIC_DIVASSIGN_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue pnumber_right 1) :: ptask_tail*
def $divassign_frontier(S, 9) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if ~$divassign_tasks(S.TODO)
def $divassign_frontier(S, 10) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprAssignOpDiv expression_left expression_right metadata)
  -- if $divassign_numeric(S.RESULT)
  -- if ~$divassign_tasks(S.TODO)
def $divassign_frontier(S, 11) = (S.CURRENT =/= eps /\ $divassign_entered(S.FRAMES, 0))
def $divassign_frontier(S, 12) = (S.CURRENT =/= eps /\ $divassign_entered(S.FRAMES, 1))
def $divassign_frontier(S, n) = false -- otherwise
dec $divassign_seek(pstate, nat, nat) : pstate
def $divassign_seek(S, n_stage, n) = S -- if $divassign_frontier(S, n_stage)
def $divassign_seek(S, n_stage, n) = S
  -- if ~$divassign_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $divassign_seek(S, n_stage, n) = S
  -- if ~$divassign_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $divassign_seek(S, n_stage, n) = $divassign_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$divassign_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    thrown = name == 'divassign-warning-second-throw'
    left_number = 'NFLOAT 4623226492472524800'
    right_phase = 'ARITHMETIC_RIGHT (' + left_number + ')'
    warning = lambda phase, raw, number, stage: f'ARITHMETIC_DIVASSIGN_WARNING pintegeroperation ({phase}) {raw} ({number}) {stage}'
    valid = lambda state, phase, raw, number, stage: f'$arithmetic_divassign_warning_valid({state}, pintegeroperation, {phase}, {raw}, {number}, {stage})'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $divassign_seek({before}, {stage}, 5000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$divassign_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$arithmetic_divassign_plan(S_entry) = (pintegeroperation)',
        '$arithmetic_divassign_source(S_entry, pintegeroperation)',
        '$arithmetic_div_plan(S_entry) = eps', '$arithmetic_addassign_plan(S_entry) = eps',
        'pintegeroperation.OP = DIVIDE', '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
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
        'S_entry.STORE[n_left] = DEFINED pvalue_left', '$string_bytes(pvalue_left) = ($ptascii("12.5tail"))',
        '$string_carrier_valid(S_entry, pvalue_left)', 'S_entry.STORE[n_right] = DEFINED (PINT 2)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', 'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 2',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'S_entry.TODO = ptask_old :: ptask_tail*', 'PhpStep: S_entry ~> S_begin',
        'S_begin = S_entry[.TODO = (ARITHMETIC_DIVASSIGN_CONVERT pintegeroperation ARITHMETIC_LEFT) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = ROOT n_left]',
        '$task_nodes(ARITHMETIC_DIVASSIGN_CONVERT pintegeroperation ARITHMETIC_LEFT) = eps',
    ]
    if not thrown:
        checks += [
            '~$arithmetic_divassign_source(S_entry, pintegeroperation[.OP = ADD])',
            '~$arithmetic_divassign_source(S_entry, pintegeroperation[.LINE = 24])',
            '~$arithmetic_divassign_source(S_entry, pintegeroperation[.SWAPPED = true])',
            '$arithmetic_divassign_plan(S_entry[.ORIGIN = eps]) = eps',
            '$arithmetic_divassign_plan(S_entry[.CODE = eps]) = eps',
            '$arithmetic_divassign_plan(S_entry[.TODO = (BINARY_RIGHT DIVIDE pintegeroperation.LEFT 25) :: ptask_tail*]) = eps',
            '$arithmetic_divassign_plan(S_entry[.STORE[n_left] = DEFINED (PINT 12)]) = eps',
            '$arithmetic_divassign_plan(S_entry[.STORE[n_right] = UNDEFINED]) = eps',
            '$arithmetic_divassign_plan(S_entry[.STORE[n_right] = DEFINED (PSTRING ($ptascii("bad")))]) = eps',
            '$arithmetic_divassign_plan(S_entry[.ALLOCATIONS = eps]) = eps',
            '$arithmetic_divassign_plan(S_entry[.PROPREFS = [{CELL n_right, SOURCES eps}]]) = eps',
            '$arithmetic_divassign_input(S_entry[.STORE[n_right] = DEFINED (PARRAY 0)], pintegeroperation, ARITHMETIC_RIGHT (NINT 12)) = eps',
            '~$call_task_valid(S_begin, ARITHMETIC_DIVASSIGN_CONVERT pintegeroperation (ARITHMETIC_RIGHT (NINT 9223372036854775808)))',
        ]
    step('S_capture_left', 'S_begin')
    checks += [
        'S_capture_left.TODO = (' + warning('ARITHMETIC_LEFT', 'pvalue_left', left_number, 0) + ') :: ptask_tail*',
        valid('S_capture_left', 'ARITHMETIC_LEFT', 'pvalue_left', left_number, 0),
        'S_capture_left.STORE = S_entry.STORE', 'S_capture_left.EVENTS = S_entry.EVENTS',
    ]
    seek('S_first', 'S_capture_left', 3)
    checks += [
        'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_left) :: ptask_tail*',
        'perrorcall_left.RESUME = ' + warning('ARITHMETIC_LEFT', 'pvalue_left', left_number, 1),
        'perrorcall_left.TARGET = eps', 'perrorcall_left.LEVEL = 2', 'perrorcall_left.LINE = 25',
        '$error_call_valid(S_first, perrorcall_left)', '$call_descriptors_valid(S_first)',
    ]
    if not thrown:
        checks += [
            '~' + valid('S_capture_left', 'ARITHMETIC_LEFT', 'pvalue_left', 'NINT 13', 0),
            '~' + valid('S_capture_left', 'ARITHMETIC_LEFT', 'pvalue_left', left_number, 2),
            '~$error_call_valid(S_first, perrorcall_left[.LEVEL = 8192])',
            '~$error_call_valid(S_first, perrorcall_left[.LINE = 24])',
        ]
    seek('S_first_entered', 'S_first', 11)
    checks += ['$divassign_entered(S_first_entered.FRAMES, 0)', '$call_descriptors_valid(S_first_entered)']
    seek('S_left', 'S_first_entered', 4)
    checks += [
        'S_left.TODO = (' + warning('ARITHMETIC_LEFT', 'pvalue_left', left_number, 1) + ') :: ptask_tail*',
        'S_left.STORE[n_left] = DEFINED (PINT 99)', 'S_left.STORE[n_right] = DEFINED pvalue_right',
        '$string_bytes(pvalue_right) = ($ptascii("5tail"))',
        '$arithmetic_add_conversion(pvalue_right) = ((NINT 5, true))',
        'S_left.STORE[n_calls] = DEFINED (PINT 1)', 'S_left.STORE[n_v] = DEFINED (PINT 100)',
        '$lookup(S_left.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_left.ENV, $ptascii("right")) = (n_replacement_right)',
        '$integer_pointer_value(S_left, pintegeroperation.RIGHTPOINTER) = (pvalue_right)',
        'S_left.STORE[n_replacement_right] = DEFINED (PINT 7)',
        '$arithmetic_divassign_source(S_left, pintegeroperation)', '~$arithmetic_add_selected(S_left, pintegeroperation)',
        valid('S_left', 'ARITHMETIC_LEFT', 'pvalue_left', left_number, 1),
        '~' + valid('S_left', 'ARITHMETIC_LEFT', 'pvalue_left', left_number, 0),
        '$heap_owners($heap_prune($heap_graph(S_left)), HCELL n_right) = 1',
        '$heap_owners($heap_prune($heap_graph(S_left)), HCELL n_replacement_right) = 2',
    ]
    step('S_right', 'S_left')
    checks += ['S_right.TODO = (ARITHMETIC_DIVASSIGN_CONVERT pintegeroperation (' + right_phase + ')) :: ptask_tail*']
    step('S_capture_right', 'S_right')
    checks += [
        'S_capture_right.TODO = (' + warning(right_phase, 'pvalue_right', 'NINT 5', 0) + ') :: ptask_tail*',
        valid('S_capture_right', right_phase, 'pvalue_right', 'NINT 5', 0),
        '$task_nodes(' + warning(right_phase, 'pvalue_right', 'NINT 5', 0) + ') = eps',
    ]
    seek('S_second', 'S_capture_right', 7)
    checks += [
        'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_right) :: ptask_tail*',
        'perrorcall_right.RESUME = ' + warning(right_phase, 'pvalue_right', 'NINT 5', 1),
        'perrorcall_right.TARGET = eps', 'perrorcall_right.LEVEL = 2', 'perrorcall_right.LINE = 25',
        '$error_call_valid(S_second, perrorcall_right)', '$call_descriptors_valid(S_second)',
    ]
    seek('S_second_entered', 'S_second', 12)
    checks += ['$divassign_entered(S_second_entered.FRAMES, 1)', '$call_descriptors_valid(S_second_entered)']
    if thrown:
        checks += [
            '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
            'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        ]
        seek('S_throw', 'S_second_entered', 9)
        checks += [
            'S_throw.TODO = (THROW_SEARCH n_second) :: ptask_caller*',
            'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps', '~$divassign_tasks(S_throw.TODO)',
            'S_throw.STORE[n_left] = DEFINED (PINT 88)', 'S_throw.STORE[n_right] = DEFINED (PINT 7)',
            'S_throw.STORE[n_v] = DEFINED (PINT 100)', 'S_throw.STORE[n_calls] = DEFINED (PINT 2)',
            '$lookup(S_throw.ENV, $ptascii("leftAlias")) = (n_left)',
            '$lookup(S_throw.ENV, $ptascii("left")) = (n_replacement_left)',
            '$lookup(S_throw.ENV, $ptascii("rightAlias")) = (n_right)',
            '$lookup(S_throw.ENV, $ptascii("right")) = (n_replacement_right)',
            'S_throw.STORE[n_replacement_left] = DEFINED (PINT 77)',
            'S_throw.STORE[n_replacement_right] = DEFINED (PINT 7)',
            '$throwable_live(S_throw, n_second)', '$throwable_previous_id(S_throw, n_second) = eps',
            '$throwable_field(S_throw, n_second, "line") = PINT 20',
            '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_left) = 1',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_right) = 1',
            'S_throw.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
            '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
            'S_done = $drive_steps(S_throw, 5000)',
        ]
    else:
        seek('S_return', 'S_second_entered', 8)
        checks += [
            'S_return.TODO = (' + warning(right_phase, 'pvalue_right', 'NINT 5', 1) + ') :: ptask_tail*',
            valid('S_return', right_phase, 'pvalue_right', 'NINT 5', 1),
            '~' + valid('S_return', right_phase, 'pvalue_right', 'NINT 5', 0),
            'S_return.STORE[n_left] = DEFINED (PINT 88)', 'S_return.STORE[n_right] = DEFINED (PINT 7)',
            'S_return.STORE[n_v] = DEFINED (PINT 100)', 'S_return.STORE[n_calls] = DEFINED (PINT 2)',
            '$lookup(S_return.ENV, $ptascii("leftAlias")) = (n_left)',
            '$lookup(S_return.ENV, $ptascii("left")) = (n_replacement_left)',
            '$lookup(S_return.ENV, $ptascii("rightAlias")) = (n_right)',
            '$lookup(S_return.ENV, $ptascii("right")) = (n_replacement_right)',
            'S_return.STORE[n_replacement_left] = DEFINED (PINT 77)',
            'S_return.STORE[n_replacement_right] = DEFINED (PINT 7)',
            '$arithmetic_divassign_target(S_return, pintegeroperation)',
            '$arithmetic_divassign_target(S_return[.STORE[n_left] = UNDEFINED], pintegeroperation) = false',
            '$arithmetic_divassign_target(S_return[.PROPREFS = [{CELL n_left, SOURCES eps}]], pintegeroperation) = false',
            'S_return.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
            'PhpStep: S_return ~> S_atomic',
            'S_atomic = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (PFLOAT 4612811918334230528)][.LOCATION = ROOT n_left][.STORE[n_left] = DEFINED (PFLOAT 4612811918334230528)]',
        ]
        step('S_result', 'S_return')
        checks += [
            '$divassign_frontier(S_result, 10)', 'S_result.RESULT = KNOWN (PFLOAT 4612811918334230528)',
            'S_result.LOCATION = ROOT n_left', 'S_result.TODO = ptask_tail*',
            'S_result.STORE = S_atomic.STORE', 'S_result.ENV = S_return.ENV',
            'S_result.REFCELLS = S_return.REFCELLS', 'S_result.ALLOCATIONS = S_return.ALLOCATIONS',
            'S_result.EVENTS = S_return.EVENTS', 'S_result.STRINGDATA = S_return.STRINGDATA',
            '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_left) = 1',
            '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_right) = 1',
            '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_replacement_left) = 2',
            '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_replacement_right) = 2',
            '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
            'S_done = $drive_steps(S_result, 5000)',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_left] = DEFINED (PINT 6)', 'S_done.STORE[n_right] = DEFINED (PINT 4)',
        'S_done.STORE[n_replacement_left] = DEFINED (PINT 8)',
        'S_done.STORE[n_replacement_right] = DEFINED (PINT 9)', 'S_done.STORE[n_calls] = DEFINED (PINT 2)',
        'S_done.STORE[n_v] = DEFINED (PINT 100)' if thrown else 'S_done.STORE[n_v] = DEFINED (PFLOAT 4612811918334230528)',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_entry, 7000) = S_done',
        '$drive_steps(S_second, 0) = S_second[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
