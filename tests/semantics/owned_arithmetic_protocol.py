#!/usr/bin/env python3
"""Reached arithmetic reference-result owners and historical numeric holders."""
import base64
import json

import owned_arithmetic_cases as cases
import plain_arithmetic_protocol as prior

CASES = ('owned-arithmetic-mul-swapped-refassign', 'owned-arithmetic-power-deprecated-throw')
HELPERS = prior.HELPERS + r'''
dec $owned_arithmetic_frontier(pstate, nat) : bool
def $owned_arithmetic_frontier(S, 0) = ($arithmetic_owned_plan(S) =/= eps)
def $owned_arithmetic_frontier(S, n) = $plain_arithmetic_frontier(S, n) -- if n =/= 0
dec $owned_arithmetic_seek(pstate, nat, nat) : pstate
def $owned_arithmetic_seek(S, n_stage, n) = S -- if $owned_arithmetic_frontier(S, n_stage)
def $owned_arithmetic_seek(S, n_stage, n) = S
  -- if ~$owned_arithmetic_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $owned_arithmetic_seek(S, n_stage, n) = S
  -- if ~$owned_arithmetic_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $owned_arithmetic_seek(S, n_stage, n) = $owned_arithmetic_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$owned_arithmetic_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    multiply = name == CASES[0]
    first_number, second_number = ('NINT 5', 'NINT 12') if multiply else ('NINT 0', 'NINT (-2)')
    roots = '[HCELL n_left]' if multiply else '[HCELL n_left, HCELL n_right]'
    phase = 'ARITHMETIC_RIGHT (' + first_number + ')'
    convert = lambda part: 'ARITHMETIC_CV_CONVERT pintegeroperation (' + part + ')'
    warning = lambda part, raw, number, stage: f'ARITHMETIC_CV_WARNING pintegeroperation ({part}) {raw} ({number}) {stage}'
    left = lambda stage: warning('ARITHMETIC_LEFT', 'pvalue_first', first_number, stage)
    right = lambda stage: warning(phase, 'pvalue_second', second_number, stage)
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $owned_arithmetic_seek({before}, {stage}, 5000)',
            rf'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]', f'$owned_arithmetic_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([f'{state}_budget = $drive_steps({before}, 1)', f'{state}_budget.COMPLETION = BUDGET',
                       f'{state} = {state}_budget[.COMPLETION = NORMAL]'])

    def owner(state, node, count):
        checks.append(f'$heap_owners($heap_prune($heap_graph({state})), HCELL {node}) = {count}')

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$arithmetic_owned_plan(S_entry) = (pintegeroperation)', '$arithmetic_owned_valid(S_entry, pintegeroperation)',
        '$arithmetic_cv_valid(S_entry, pintegeroperation)', '$arithmetic_add_selected(S_entry, pintegeroperation)',
        '$arithmetic_cv_plan(S_entry) = eps', '$arithmetic_mixed_plan(S_entry) = eps', '$arithmetic_copy_plan(S_entry) = eps',
        'pintegeroperation.OP = ' + ('MULTIPLY' if multiply else 'POWER'),
        'pintegeroperation.SWAPPED' if multiply else '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = REFERENCE n_left', 'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_left',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)', '$lookup(S_entry.ENV, $ptascii("sourceCalls")) = (n_source_calls)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)', 'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        'S_entry.STORE[n_source_calls] = DEFINED (PINT ' + ('0' if multiply else '2') + ')',
        '$operand_nodes(pintegeroperation.LEFT) ++ $operand_nodes(pintegeroperation.RIGHT) = ' + roots,
        '$arithmetic_owned_cell_valid(S_entry, n_left)', 'n_left <- S_entry.REFCELLS',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
    ]
    if multiply:
        checks += [
            'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
            'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))',
            '$lookup(S_entry.ENV, $ptascii("alias")) = (n_left)', '~(n_right <- S_entry.REFCELLS)',
            'S_entry.STORE[n_left] = DEFINED pvalue_bad', '$string_bytes(pvalue_bad) = ($ptascii("bad5"))',
            '$arithmetic_add_conversion(pvalue_bad) = eps',
            'S_entry.STORE[n_right] = DEFINED pvalue_first', '$string_bytes(pvalue_first) = ($ptascii("5tail"))',
            '$integer_slot_rank(S_entry, pintegeroperation.SITE, [PCFIELD 0], pintegeroperation.LEFT) = (4)',
            '$integer_slot_rank(S_entry, pintegeroperation.SITE, [PCFIELD 1], pintegeroperation.RIGHT) = (8)',
            '$arithmetic_cv_pointer(pintegeroperation, ARITHMETIC_LEFT) = pintegeroperation.RIGHTPOINTER',
            '$arithmetic_cv_pointer(pintegeroperation, ' + phase + ') = pintegeroperation.LEFTPOINTER',
            '~$arithmetic_owned_valid(S_entry, pintegeroperation[.OP = ADD])',
            '~$arithmetic_owned_valid(S_entry, pintegeroperation[.SWAPPED = false])',
            '~$arithmetic_owned_valid(S_entry, pintegeroperation[.LINE = 24])',
            '~$arithmetic_owned_valid(S_entry[.ORIGIN = eps], pintegeroperation)',
            '$arithmetic_owned_plan(S_entry[.ALLOCATIONS = eps]) = eps',
        ]
        for state in ('S_entry[.REFCELLS = eps]', 'S_entry[.STORE[n_left] = DEFINED PUNDEFINED]',
                      'S_entry[.STORE[n_left] = DEFINED (PARRAY 0)]', 'S_entry[.STORE[n_left] = DEFINED (POBJECT 0)]',
                      'S_entry[.PROPREFS = [{CELL n_left, SOURCES eps}]]',
                      'S_entry[.REFCOERCIONS = [{CELL n_left, SITE pintegeroperation.SITE, LINE 25, VALUE ($ptascii("0"))}]]',
                      'S_entry[.PARAMETERBACKINGS = [{FUNCTION pintegeroperation.SITE, INDEX 0, CELL n_left, LINE 25, VALUE ($ptascii("0"))}]]'):
            checks.append('$arithmetic_owned_plan(' + state + ') = eps')
        owner('S_entry', 'n_left', 3)
    else:
        checks += [
            'pintegeroperation.RIGHT = REFERENCE n_right', 'pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_right',
            'n_right <- S_entry.REFCELLS', '$arithmetic_owned_cell_valid(S_entry, n_right)',
            'S_entry.STORE[n_left] = DEFINED pvalue_first', '$string_bytes(pvalue_first) = ($ptascii("0tail"))',
            'S_entry.STORE[n_right] = DEFINED pvalue_bad', '$string_bytes(pvalue_bad) = ($ptascii("bad5"))',
            '$arithmetic_add_conversion(pvalue_bad) = eps',
            '$lookup(S_entry.ENV, $ptascii("supplied")) = (n_supplied_cell)',
            'S_entry.STORE[n_supplied_cell] = DEFINED (POBJECT n_supplied)',
        ]
        for node in ('n_left', 'n_right'):owner('S_entry', node, 2)
    checks.append('$arithmetic_add_conversion(pvalue_first) = ((' + first_number + ', true))')
    step('S_begin', 'S_entry')
    checks += ['S_entry.TODO = ptask_old :: ptask_tail*',
               'S_begin = S_entry[.TODO = (' + convert('ARITHMETIC_LEFT') + ') :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
               '$task_nodes(' + convert('ARITHMETIC_LEFT') + ') = ' + roots]
    step('S_capture', 'S_begin')
    checks += ['S_capture = S_begin[.TODO = (' + left(0) + ') :: ptask_tail*]',
               '$task_nodes(' + left(0) + ') = ' + roots]
    step('S_first', 'S_capture')
    checks += ['$owned_arithmetic_frontier(S_first, 3)', 'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
               'perrorcall_first.RESUME = ' + left(1), 'perrorcall_first.TARGET = eps',
               '$error_call_valid(S_first, perrorcall_first)', '$task_nodes(perrorcall_first.RESUME) = ' + roots]
    seek('S_entered', 'S_first', 10)
    checks += ['$plain_arithmetic_entered(S_entered.FRAMES, 0)', '$call_descriptors_valid(S_entered)']
    seek('S_return', 'S_entered', 4)
    checks += ['S_return.TODO = (' + left(1) + ') :: ptask_tail*',
               '$lookup(S_return.ENV, $ptascii("left")) = eps',
               'S_return.STORE[n_calls] = DEFINED (PINT 1)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
               '$arithmetic_cv_warning_valid(S_return, pintegeroperation, ARITHMETIC_LEFT, pvalue_first, ' + first_number + ', 1)',
               '~$arithmetic_cv_warning_valid(S_return, pintegeroperation, ARITHMETIC_LEFT, pvalue_first, ' + first_number + ', 0)',
               '$arithmetic_owned_valid(S_return, pintegeroperation)',
               'S_return.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA']
    if multiply:
        checks += ['$lookup(S_return.ENV, $ptascii("alias")) = eps', 'S_return.STORE[n_right] = DEFINED (PINT 7)',
                   'S_return.STORE[n_left] = DEFINED pvalue_second', '$string_bytes(pvalue_second) = ($ptascii("12tail"))']
    else:
        checks += ['$lookup(S_return.ENV, $ptascii("right")) = eps', 'S_return.STORE[n_left] = DEFINED (PINT 99)',
                   'S_return.STORE[n_right] = DEFINED pvalue_second', '$string_bytes(pvalue_second) = ($ptascii("-2tail"))']
    owner('S_return', 'n_left', 1)
    if not multiply:owner('S_return', 'n_right', 1)
    checks.append('$arithmetic_add_conversion(pvalue_second) = ((' + second_number + ', true))')
    step('S_pending', 'S_return')
    checks += ['S_pending = S_return[.TODO = (' + convert(phase) + ') :: ptask_tail*][.RESULT = KNOWN PNULL]',
               '$arithmetic_cv_value(S_pending, $arithmetic_cv_pointer(pintegeroperation, ' + phase + ')) = (pvalue_second)']
    step('S_second_capture', 'S_pending')
    checks += ['S_second_capture = S_pending[.TODO = (' + right(0) + ') :: ptask_tail*]']
    step('S_second', 'S_second_capture')
    checks += ['$owned_arithmetic_frontier(S_second, 7)', 'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
               'perrorcall_second.RESUME = ' + right(1), 'perrorcall_second.TARGET = eps',
               '$error_call_valid(S_second, perrorcall_second)', '$task_nodes(perrorcall_second.RESUME) = ' + roots]
    seek('S_second_entered', 'S_second', 11)
    checks += ['$plain_arithmetic_entered(S_second_entered.FRAMES, 1)', '$call_descriptors_valid(S_second_entered)']
    seek('S_late', 'S_second_entered', 8)
    checks += ['S_late.TODO = (' + right(1) + ') :: ptask_tail*', 'S_late.STORE[n_calls] = DEFINED (PINT 2)',
               'S_late.STORE[n_v] = DEFINED (PINT 100)',
               '$arithmetic_cv_warning_valid(S_late, pintegeroperation, ' + phase + ', pvalue_second, ' + second_number + ', 1)',
               '$arithmetic_cv_warning_valid(S_late, pintegeroperation, ' + phase + ', pvalue_second, ' + second_number + ', 0)',
               '$arithmetic_owned_valid(S_late, pintegeroperation)']
    owner('S_late', 'n_left', 1)
    if multiply:
        checks += ['S_late.STORE[n_right] = DEFINED (PINT 8)', 'S_late.STORE[n_left] = DEFINED pvalue_second',
                   '$lookup(S_late.ENV, $ptascii("left")) = eps', '$lookup(S_late.ENV, $ptascii("alias")) = eps',
                   'PhpStep: S_late ~> S_atomic',
                   'S_atomic = S_late[.TODO = ptask_tail*][.RESULT = KNOWN (PINT 60)]']
        step('S_result', 'S_late')
        checks += ['S_result.RESULT = KNOWN (PINT 60)', 'S_result.TODO = ptask_tail*',
                   'S_result.STORE = S_late.STORE', 'S_result.ENV = S_late.ENV', 'S_result.REFCELLS = S_late.REFCELLS',
                   'S_result.EVENTS = S_late.EVENTS', 'S_result.STRINGDATA = S_late.STRINGDATA',
                   '~((HCELL n_left) <- S_result.ALLOCATIONS)', 'S_done = $drive_steps(S_result, 5000)',
                   'S_done.STORE[n_v] = DEFINED (PINT 60)']
        owner('S_result', 'n_left', 0)
    else:
        checks += ['S_late.STORE[n_left] = DEFINED (PINT 99)', 'S_late.STORE[n_right] = DEFINED pvalue_second',
                   '$lookup(S_late.ENV, $ptascii("left")) = (n_fresh_left)', '$lookup(S_late.ENV, $ptascii("right")) = (n_fresh_right)',
                   'n_fresh_left =/= n_left', 'n_fresh_right =/= n_right',
                   'S_late.STORE[n_fresh_left] = DEFINED (PINT 88)', 'S_late.STORE[n_fresh_right] = DEFINED (PINT 7)']
        owner('S_late', 'n_right', 1)
        step('S_deprecated', 'S_late')
        final = 'ARITHMETIC_CV_DEPRECATED pintegeroperation (NINT 0) (NINT (-2))'
        checks += ['S_deprecated = S_late[.TODO = (' + final + ' 0) :: ptask_tail*][.RESULT = KNOWN PNULL]',
                   '$arithmetic_cv_deprecated_valid(S_deprecated, pintegeroperation, NINT 0, NINT (-2), 0)',
                   '$task_nodes(' + final + ' 0) = ' + roots]
        step('S_final', 'S_deprecated')
        checks += ['$owned_arithmetic_frontier(S_final, 13)', 'S_final.TODO = (ERROR_HANDLER_INVOKE perrorcall_final) :: ptask_tail*',
                   'perrorcall_final.RESUME = ' + final + ' 1', 'perrorcall_final.TARGET = eps',
                   'perrorcall_final.LEVEL = 8192', 'perrorcall_final.LINE = 25', '$error_call_valid(S_final, perrorcall_final)',
                   '$task_nodes(perrorcall_final.RESUME) = ' + roots]
        seek('S_final_entered', 'S_final', 14)
        checks += ['$plain_arithmetic_entered(S_final_entered.FRAMES, 2)', '$call_descriptors_valid(S_final_entered)']
        seek('S_throw', 'S_final_entered', 9)
        checks += ['S_throw.TODO = (THROW_SEARCH n_supplied) :: ptask_throw*', 'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps',
                   '~$plain_arithmetic_tasks(S_throw.TODO)', '$throwable_live(S_throw, n_supplied)',
                   '$throwable_previous_id(S_throw, n_supplied) = eps', '$throwable_field(S_throw, n_supplied, "line") = PINT 20',
                   '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_supplied) = 2',
                   'S_throw.STORE[n_fresh_left] = DEFINED (PINT 77)', 'S_throw.STORE[n_fresh_right] = DEFINED (PINT 9)',
                   'S_throw.STORE[n_v] = DEFINED (PINT 100)', 'S_throw.STORE[n_calls] = DEFINED (PINT 3)',
                   '~((HCELL n_left) <- S_throw.ALLOCATIONS)', '~((HCELL n_right) <- S_throw.ALLOCATIONS)',
                   '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
                   'S_done = $drive_steps(S_throw, 5000)', 'S_done.STORE[n_v] = DEFINED (PINT 100)',
                   '$drive_steps(S_final, 0) = S_final[.COMPLETION = BUDGET]']
        for node in ('n_left', 'n_right'):owner('S_throw', node, 0)
    checks += ['S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
               '$lookup(S_done.ENV, $ptascii("left")) = (n_done_left)', '$lookup(S_done.ENV, $ptascii("right")) = (n_done_right)',
               'n_done_left =/= n_left', 'S_done.STORE[n_done_left] = DEFINED (PINT 1)', 'S_done.STORE[n_done_right] = DEFINED (PINT 2)',
               'S_done.STORE[n_source_calls] = DEFINED (PINT ' + ('0' if multiply else '2') + ')',
               '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
               '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
               '$drive_steps(S_entry, 7000) = S_done', '$drive_steps(S_entry, 0) = S_entry[.COMPLETION = BUDGET]']
    owner('S_done', 'n_left', 0)
    if not multiply:owner('S_done', 'n_right', 0)
    assert len(checks) == len(set(checks))
    return checks
