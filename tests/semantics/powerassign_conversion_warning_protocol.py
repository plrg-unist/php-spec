#!/usr/bin/env python3
"""Reached selected power conversions and final-deprecation store obligations."""
import base64
import json
import integer_operator_warning_protocol as shared
import powerassign_conversion_warning_cases as cases

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''

dec $powerassign_conversion_task(ptask) : bool
def $powerassign_conversion_task(ARITHMETIC_POWERASSIGN_CONVERT pintegeroperation parithmeticphase) = true
def $powerassign_conversion_task(ARITHMETIC_POWERASSIGN_WARNING pintegeroperation parithmeticphase pvalue pnumber n) = true
def $powerassign_conversion_task(POWER_ASSIGN_CONVERTED_DEPRECATED pintegeroperation pnumber_left pnumber_right n_stage n_pending?) = true
def $powerassign_conversion_task(ERROR_HANDLER_INVOKE perrorcall) = $powerassign_conversion_task(perrorcall.RESUME)
def $powerassign_conversion_task(ERROR_HANDLER_RESULT perrorcall) = $powerassign_conversion_task(perrorcall.RESUME)
def $powerassign_conversion_task(ERROR_HANDLER_CLEAN perrorcall) = $powerassign_conversion_task(perrorcall.RESUME)
def $powerassign_conversion_task(ptask) = false -- otherwise
dec $powerassign_conversion_tasks(ptask*) : bool
def $powerassign_conversion_tasks(eps) = false
def $powerassign_conversion_tasks(ptask :: ptask_tail*) = ($powerassign_conversion_task(ptask) \/ $powerassign_conversion_tasks(ptask_tail*))
dec $powerassign_conversion_handler_frame(pframe, nat) : bool
def $powerassign_conversion_handler_frame(pframe, 0) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_POWERASSIGN_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 1
  -- if perrorcall.TARGET =/= eps
def $powerassign_conversion_handler_frame(pframe, 1) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_POWERASSIGN_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue pnumber_right 1
  -- if perrorcall.TARGET =/= eps
def $powerassign_conversion_handler_frame(pframe, 2) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = POWER_ASSIGN_CONVERTED_DEPRECATED pintegeroperation pnumber_left pnumber_right 1 eps
  -- if perrorcall.TARGET =/= eps
def $powerassign_conversion_handler_frame(pframe, n) = false -- otherwise
dec $powerassign_conversion_entered(pframe*, nat) : bool
def $powerassign_conversion_entered(eps, n) = false
def $powerassign_conversion_entered(pframe :: pframe_tail*, n) = ($powerassign_conversion_handler_frame(pframe, n) \/ $powerassign_conversion_entered(pframe_tail*, n))
dec $powerassign_conversion_numeric(poperand) : bool
def $powerassign_conversion_numeric(KNOWN (PINT i)) = true
def $powerassign_conversion_numeric(KNOWN (PFLOAT n)) = true
def $powerassign_conversion_numeric(poperand) = false -- otherwise
dec $powerassign_conversion_frontier(pstate, nat) : bool
def $powerassign_conversion_frontier(S, 0) = ($arithmetic_powerassign_plan(S) =/= eps)
def $powerassign_conversion_frontier(S, 1) = true
  -- if S.TODO = (ARITHMETIC_POWERASSIGN_CONVERT pintegeroperation ARITHMETIC_LEFT) :: ptask_tail*
def $powerassign_conversion_frontier(S, 2) = true
  -- if S.TODO = (ARITHMETIC_POWERASSIGN_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 0) :: ptask_tail*
def $powerassign_conversion_frontier(S, 3) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_POWERASSIGN_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 1
def $powerassign_conversion_frontier(S, 4) = true
  -- if S.TODO = (ARITHMETIC_POWERASSIGN_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 1) :: ptask_tail*
def $powerassign_conversion_frontier(S, 5) = true
  -- if S.TODO = (ARITHMETIC_POWERASSIGN_CONVERT pintegeroperation (ARITHMETIC_RIGHT pnumber)) :: ptask_tail*
def $powerassign_conversion_frontier(S, 6) = true
  -- if S.TODO = (ARITHMETIC_POWERASSIGN_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue pnumber_right 0) :: ptask_tail*
def $powerassign_conversion_frontier(S, 7) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_POWERASSIGN_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue pnumber_right 1
def $powerassign_conversion_frontier(S, 8) = true
  -- if S.TODO = (ARITHMETIC_POWERASSIGN_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue pnumber_right 1) :: ptask_tail*
def $powerassign_conversion_frontier(S, 9) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if ~$powerassign_conversion_tasks(S.TODO)
def $powerassign_conversion_frontier(S, 10) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprAssignOpPow expression_left expression_right metadata)
  -- if $powerassign_conversion_numeric(S.RESULT)
  -- if ~$powerassign_conversion_tasks(S.TODO)
def $powerassign_conversion_frontier(S, 11) = (S.CURRENT =/= eps /\ $powerassign_conversion_entered(S.FRAMES, 0))
def $powerassign_conversion_frontier(S, 12) = (S.CURRENT =/= eps /\ $powerassign_conversion_entered(S.FRAMES, 1))
def $powerassign_conversion_frontier(S, 13) = true
  -- if S.TODO = (POWER_ASSIGN_CONVERTED_DEPRECATED pintegeroperation pnumber_left pnumber_right 0 eps) :: ptask_tail*
def $powerassign_conversion_frontier(S, 14) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = POWER_ASSIGN_CONVERTED_DEPRECATED pintegeroperation pnumber_left pnumber_right 1 eps
  -- if perrorcall.TARGET = eps
def $powerassign_conversion_frontier(S, 15) = (S.CURRENT =/= eps /\ $powerassign_conversion_entered(S.FRAMES, 2))
def $powerassign_conversion_frontier(S, 16) = true
  -- if S.TODO = (POWER_ASSIGN_CONVERTED_DEPRECATED pintegeroperation pnumber_left pnumber_right 1 eps) :: ptask_tail*
def $powerassign_conversion_frontier(S, 17) = true
  -- if S.TODO = (POWER_ASSIGN_CONVERTED_DEPRECATED pintegeroperation pnumber_left pnumber_right 1 (n_exception)) :: ptask_tail*
def $powerassign_conversion_frontier(S, n) = false -- otherwise
dec $powerassign_conversion_seek(pstate, nat, nat) : pstate
def $powerassign_conversion_seek(S, n_stage, n) = S -- if $powerassign_conversion_frontier(S, n_stage)
def $powerassign_conversion_seek(S, n_stage, n) = S
  -- if ~$powerassign_conversion_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $powerassign_conversion_seek(S, n_stage, n) = S
  -- if ~$powerassign_conversion_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $powerassign_conversion_seek(S, n_stage, n) = $powerassign_conversion_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$powerassign_conversion_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    final_throw = name == 'powerassign-conversion-final-throw'
    left_number = 'NINT 0'
    right_number = 'NINT (-2)'
    right_phase = 'ARITHMETIC_RIGHT (' + left_number + ')'
    warning = lambda phase, raw, number, stage: f'ARITHMETIC_POWERASSIGN_WARNING pintegeroperation ({phase}) {raw} ({number}) {stage}'
    valid = lambda state, phase, raw, number, stage: f'$arithmetic_powerassign_warning_valid({state}, pintegeroperation, {phase}, {raw}, {number}, {stage})'
    marker = lambda stage, pending='eps': f'POWER_ASSIGN_CONVERTED_DEPRECATED pintegeroperation ({left_number}) ({right_number}) {stage} {pending}'
    final_valid = lambda state, stage, pending='eps': f'$powerassign_converted_deprecated_valid({state}, pintegeroperation, {left_number}, {right_number}, {stage}, {pending})'
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET']

    def seek(state, before, stage):
        checks.extend([f'{state}_found = $powerassign_conversion_seek({before}, {stage}, 5000)',
                       f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
                       f'{state} = {state}_found[.COMPLETION = NORMAL]',
                       f'$powerassign_conversion_frontier({state}, {stage})'])

    def step(state, before):
        checks.extend([f'{state}_budget = $drive_steps({before}, 1)',
                       f'{state}_budget.COMPLETION = BUDGET',
                       f'{state} = {state}_budget[.COMPLETION = NORMAL]'])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$arithmetic_powerassign_plan(S_entry) = (pintegeroperation)',
        '$arithmetic_powerassign_source(S_entry, pintegeroperation)',
        '$arithmetic_divassign_plan(S_entry) = eps',
        '$powerassign_selected_warning_plan(S_entry) = eps', '$powerassign_warning_plan(S_entry) = eps',
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
        'S_entry.STORE[n_left] = DEFINED pvalue_left', '$string_bytes(pvalue_left) = ($ptascii("0tail"))',
        '$string_carrier_valid(S_entry, pvalue_left)', 'S_entry.STORE[n_right] = DEFINED (PINT 2)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', 'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 2',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'S_entry.TODO = ptask_old :: ptask_tail*', 'PhpStep: S_entry ~> S_begin',
        'S_begin = S_entry[.TODO = (ARITHMETIC_POWERASSIGN_CONVERT pintegeroperation ARITHMETIC_LEFT) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = ROOT n_left]',
        '$task_nodes(ARITHMETIC_POWERASSIGN_CONVERT pintegeroperation ARITHMETIC_LEFT) = eps',
    ]
    if not final_throw:
        checks += [
        '~$arithmetic_powerassign_source(S_entry, pintegeroperation[.OP = ADD])',
        '~$arithmetic_powerassign_source(S_entry, pintegeroperation[.LINE = 24])',
        '~$arithmetic_powerassign_source(S_entry, pintegeroperation[.SWAPPED = true])',
        '$arithmetic_powerassign_plan(S_entry[.ORIGIN = eps]) = eps',
        '$arithmetic_powerassign_plan(S_entry[.CODE = eps]) = eps',
        '$arithmetic_powerassign_plan(S_entry[.TODO = (BINARY_RIGHT POWER pintegeroperation.LEFT 25) :: ptask_tail*]) = eps',
        '$arithmetic_powerassign_plan(S_entry[.STORE[n_left] = DEFINED (PINT 12)]) = eps',
        '$arithmetic_powerassign_plan(S_entry[.STORE[n_right] = UNDEFINED]) = eps',
        '$arithmetic_powerassign_plan(S_entry[.STORE[n_right] = DEFINED (PSTRING ($ptascii("bad")))]) = eps',
        '$arithmetic_powerassign_plan(S_entry[.ALLOCATIONS = eps]) = eps',
        '$arithmetic_powerassign_plan(S_entry[.ERRORHANDLER.CALLBACK = eps]) = eps',
        '$arithmetic_powerassign_plan(S_entry[.ERRORHANDLER.LEVELS = 8192]) = eps',
        '$arithmetic_powerassign_plan(S_entry[.REFCELLS = eps]) = eps',
        '$arithmetic_powerassign_plan(S_entry[.STORE[n_left] = UNDEFINED]) = eps',
        '$arithmetic_powerassign_plan(S_entry[.PROPREFS = [{CELL n_left, SOURCES eps}]]) = eps',
        '$arithmetic_powerassign_plan(S_entry[.PROPREFS = [{CELL n_right, SOURCES eps}]]) = eps',
        '$arithmetic_powerassign_input(S_entry[.STORE[n_right] = DEFINED (PARRAY 0)], pintegeroperation, ARITHMETIC_RIGHT (NINT 12)) = eps',
        '~$call_task_valid(S_begin, ARITHMETIC_POWERASSIGN_CONVERT pintegeroperation (ARITHMETIC_RIGHT (NINT 9223372036854775808)))',
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
    checks += [
        '~' + valid('S_capture_left', 'ARITHMETIC_LEFT', 'pvalue_left', 'NINT 13', 0),
        '~' + valid('S_capture_left', 'ARITHMETIC_LEFT', 'pvalue_left', left_number, 2),
        '~$error_call_valid(S_first, perrorcall_left[.LEVEL = 8192])',
        '~$error_call_valid(S_first, perrorcall_left[.LINE = 24])',
    ]
    seek('S_first_entered', 'S_first', 11)
    checks += ['$powerassign_conversion_entered(S_first_entered.FRAMES, 0)', '$call_descriptors_valid(S_first_entered)']
    seek('S_left', 'S_first_entered', 4)
    checks += [
        'S_left.TODO = (' + warning('ARITHMETIC_LEFT', 'pvalue_left', left_number, 1) + ') :: ptask_tail*',
        'S_left.STORE[n_left] = DEFINED (PINT 99)', 'S_left.STORE[n_right] = DEFINED pvalue_right',
        '$string_bytes(pvalue_right) = ($ptascii("-2tail"))',
        '$arithmetic_add_conversion(pvalue_right) = ((NINT (-2), true))',
        'S_left.STORE[n_calls] = DEFINED (PINT 1)', 'S_left.STORE[n_v] = DEFINED (PINT 100)',
        '$lookup(S_left.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_left.ENV, $ptascii("right")) = (n_replacement_right)',
        '$integer_pointer_value(S_left, pintegeroperation.RIGHTPOINTER) = (pvalue_right)',
        'S_left.STORE[n_replacement_right] = DEFINED (PINT 7)',
        '$arithmetic_powerassign_source(S_left, pintegeroperation)', '~$arithmetic_add_selected(S_left, pintegeroperation)',
        valid('S_left', 'ARITHMETIC_LEFT', 'pvalue_left', left_number, 1),
        '~' + valid('S_left', 'ARITHMETIC_LEFT', 'pvalue_left', left_number, 0),
        '$heap_owners($heap_prune($heap_graph(S_left)), HCELL n_right) = 1',
        '$heap_owners($heap_prune($heap_graph(S_left)), HCELL n_replacement_right) = 2',
    ]
    step('S_right', 'S_left')
    checks += ['S_right.TODO = (ARITHMETIC_POWERASSIGN_CONVERT pintegeroperation (' + right_phase + ')) :: ptask_tail*']
    step('S_capture_right', 'S_right')
    checks += [
        'S_capture_right.TODO = (' + warning(right_phase, 'pvalue_right', 'NINT (-2)', 0) + ') :: ptask_tail*',
        valid('S_capture_right', right_phase, 'pvalue_right', 'NINT (-2)', 0),
        '$task_nodes(' + warning(right_phase, 'pvalue_right', 'NINT (-2)', 0) + ') = eps',
    ]
    seek('S_second', 'S_capture_right', 7)
    checks += [
        'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_right) :: ptask_tail*',
        'perrorcall_right.RESUME = ' + warning(right_phase, 'pvalue_right', 'NINT (-2)', 1),
        'perrorcall_right.TARGET = eps', 'perrorcall_right.LEVEL = 2', 'perrorcall_right.LINE = 25',
        '$error_call_valid(S_second, perrorcall_right)', '$call_descriptors_valid(S_second)',
    ]
    seek('S_second_entered', 'S_second', 12)
    checks += ['$powerassign_conversion_entered(S_second_entered.FRAMES, 1)', '$call_descriptors_valid(S_second_entered)']
    checks += ['$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
               'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
               'S_entry.ERRORHANDLER.LEVELS = 8194', '$error_handler_eligible(S_entry, 2)', '$error_handler_eligible(S_entry, 8192)']
    if final_throw:
        seek('S_return', 'S_second_entered', 8)
        checks += ['S_return.TODO = (' + warning(right_phase, 'pvalue_right', right_number, 1) + ') :: ptask_tail*',
                   'S_return.STORE[n_left] = DEFINED (PINT 88)', 'S_return.STORE[n_right] = DEFINED (PINT 7)',
                   'S_return.STORE[n_calls] = DEFINED (PINT 2)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
                   '$lookup(S_return.ENV, $ptascii("left")) = (n_replacement_left)',
                   '$lookup(S_return.ENV, $ptascii("right")) = (n_replacement_right)',
                   valid('S_return', right_phase, 'pvalue_right', right_number, 1),
                   '~' + valid('S_return', right_phase, 'pvalue_right', right_number, 0),
                   '$arithmetic_powerassign_target(S_return, pintegeroperation)',
                   '~$arithmetic_powerassign_target(S_return[.STORE[n_left] = DEFINED (PSTRING ($ptascii("88")))], pintegeroperation)',
                   '~$arithmetic_powerassign_target(S_return[.STORE[n_left] = UNDEFINED], pintegeroperation)',
                   'PhpStep: S_return ~> S_bridge',
                   'S_bridge = S_return[.TODO = (' + marker(0) + ') :: ptask_tail*][.RESULT = KNOWN PNULL]']
        step('S_final', 'S_return')
        checks += ['S_final = S_bridge', final_valid('S_final', 0), '$task_nodes(' + marker(0) + ') = eps',
                   '~$powerassign_selected_warning_snapshot(S_final, pintegeroperation, n_left, NINT 0, NINT (-2))',
                   '~$powerassign_selected_warning_valid(S_final, pintegeroperation, n_left, NINT 0, NINT (-2), 0, eps)',
                   '~' + final_valid('S_final', 2), '~' + final_valid('S_final', 0, '(n_second)'),
                   '~$powerassign_converted_deprecated_valid(S_final, pintegeroperation, NINT 1, NINT (-2), 0, eps)',
                   '$drive_steps(S_final, 0) = S_final[.COMPLETION = BUDGET]']
        step('S_deprecated', 'S_final')
        checks += ['S_deprecated.TODO = (ERROR_HANDLER_INVOKE perrorcall_final) :: ptask_tail*',
                   'perrorcall_final.RESUME = ' + marker(1), 'perrorcall_final.TARGET = eps',
                   'perrorcall_final.LEVEL = 8192', 'perrorcall_final.LINE = 25',
                   '$error_call_valid(S_deprecated, perrorcall_final)', '$call_descriptors_valid(S_deprecated)',
                   '~$error_call_valid(S_deprecated, perrorcall_final[.LEVEL = 2])',
                   '~$error_call_valid(S_deprecated, perrorcall_final[.LINE = 24])']
        seek('S_final_entered', 'S_deprecated', 15)
        checks += ['$powerassign_conversion_entered(S_final_entered.FRAMES, 2)', '$call_descriptors_valid(S_final_entered)']
        seek('S_pending', 'S_final_entered', 17)
        checks += ['S_pending.TODO = (' + marker(1, '(n_second)') + ') :: ptask_tail*',
                   'S_pending.CURRENT = eps', 'S_pending.FRAMES = eps',
                   'S_pending.ERRORHANDLER = S_entry.ERRORHANDLER',
                   'S_pending.STORE[n_left] = DEFINED (PINT 66)', 'S_pending.STORE[n_right] = DEFINED (PINT 7)',
                   'S_pending.STORE[n_calls] = DEFINED (PINT 3)', 'S_pending.STORE[n_v] = DEFINED (PINT 100)',
                   '$lookup(S_pending.ENV, $ptascii("leftAlias")) = (n_left)',
                   '$lookup(S_pending.ENV, $ptascii("left")) = (n_replacement_left)',
                   '$lookup(S_pending.ENV, $ptascii("rightAlias")) = (n_right)',
                   '$lookup(S_pending.ENV, $ptascii("right")) = (n_replacement_right)',
                   '$arithmetic_powerassign_source(S_pending, pintegeroperation)', '~$arithmetic_add_selected(S_pending, pintegeroperation)',
                   final_valid('S_pending', 1, '(n_second)'), '~' + final_valid('S_pending', 0, '(n_second)'),
                   '$arithmetic_powerassign_target(S_pending, pintegeroperation)',
                   '$task_nodes(' + marker(1, '(n_second)') + ') = [HOBJECT n_second]',
                   '$heap_owners($heap_prune($heap_graph(S_pending)), HOBJECT n_second) = 2',
                   '$heap_owners($heap_prune($heap_graph(S_pending)), HCELL n_left) = 1',
                   '$heap_owners($heap_prune($heap_graph(S_pending)), HCELL n_right) = 1',
                   '$throwable_live(S_pending, n_second)', '$throwable_previous_id(S_pending, n_second) = eps',
                   '$throwable_field(S_pending, n_second, "line") = PINT 20',
                   'S_pending.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
                   '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
                   'PhpStep: S_pending ~> S_atomic',
                   'S_atomic = S_pending[.TODO = (THROW_SEARCH n_second) :: ptask_tail*][.STORE[n_left] = DEFINED (PFLOAT 9218868437227405312)][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = ROOT n_left]']
        step('S_throw', 'S_pending')
        checks += ['$powerassign_conversion_frontier(S_throw, 9)', 'S_throw.TODO = S_atomic.TODO',
                   'S_throw.STORE = S_atomic.STORE', 'S_throw.RESULT = KNOWN PNULL',
                   'S_throw.BASE = BASE_VALUE (KNOWN PNULL)', 'S_throw.LOCATION = ROOT n_left',
                   'S_throw.ENV = S_pending.ENV', 'S_throw.REFCELLS = S_pending.REFCELLS',
                   'S_throw.ALLOCATIONS = S_pending.ALLOCATIONS', 'S_throw.ARRAYS = S_pending.ARRAYS',
                   'S_throw.OBJECTS = S_pending.OBJECTS', 'S_throw.EVENTS = S_pending.EVENTS',
                   'S_throw.STRINGDATA = S_pending.STRINGDATA',
                   '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
                   'S_throw.STORE[n_v] = DEFINED (PINT 100)',
                   '$drive_steps(S_pending, 0) = S_pending[.COMPLETION = BUDGET]']
    else:
        seek('S_throw', 'S_second_entered', 9)
        checks += ['S_throw.TODO = (THROW_SEARCH n_second) :: ptask_caller*',
                   'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps',
                   'S_throw.STORE[n_left] = DEFINED (PINT 88)', 'S_throw.STORE[n_right] = DEFINED (PINT 7)',
                   'S_throw.STORE[n_calls] = DEFINED (PINT 2)', 'S_throw.STORE[n_v] = DEFINED (PINT 100)',
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
                   '$drive_steps(S_second, 0) = S_second[.COMPLETION = BUDGET]']
    checks += ['~$powerassign_conversion_tasks(S_throw.TODO)', '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
               'S_done = $drive_steps(S_throw, 5000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
               'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
               'S_done.STORE[n_left] = DEFINED (PINT 6)', 'S_done.STORE[n_right] = DEFINED (PINT 4)',
               'S_done.STORE[n_replacement_left] = DEFINED (PINT 8)', 'S_done.STORE[n_replacement_right] = DEFINED (PINT 9)',
               'S_done.STORE[n_calls] = DEFINED (PINT ' + str(3 if final_throw else 2) + ')',
               'S_done.STORE[n_v] = DEFINED (PINT 100)',
               '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
               '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))']
    if not final_throw:
        checks += ['$drive_steps(S_entry, 7000) = S_done']
    assert len(checks) == len(set(checks))
    return checks
