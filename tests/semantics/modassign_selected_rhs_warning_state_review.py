#!/usr/bin/env python3
"""A freshly selected modulo divisor can retire after its long is captured."""
import base64
import json

import modassign_selected_rhs_warning_review_cases as cases

CASES = tuple(cases.CASES)
REVIEW_HELPERS = ''


def conditions(name, program, path, stdout):
    assert name in CASES
    left_bits = 4623226492472524800
    right_bits = 4617878467915022336
    marker = lambda stage: f'MOD_ASSIGN_SELECTED_RIGHT_WARNING pintegeroperation {left_bits} 12 {right_bits} 5 {stage}'
    valid = lambda state, stage: f'$modassign_selected_right_warning_valid({state}, pintegeroperation, {left_bits}, 12, {right_bits}, 5, {stage})'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $modassign_selected_rhs_seek({before}, {stage}, 3500)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$modassign_selected_rhs_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        f'$modassign_selected_warning_plan(S_entry) = (MOD_ASSIGN_SELECTED_WARNING pintegeroperation {left_bits} 12 0)',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_left',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))',
        'pintegeroperation.LINE = 25',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_old_right)',
        '$lookup(S_entry.ENV, $ptascii("replacementLeft")) = (n_replacement_left)',
        '$lookup(S_entry.ENV, $ptascii("replacementRight")) = (n_new_right)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        f'S_entry.STORE[n_left] = DEFINED (PFLOAT {left_bits})',
        'S_entry.STORE[n_old_right] = DEFINED (PINT 0)',
        f'S_entry.STORE[n_new_right] = DEFINED (PFLOAT {right_bits})',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_old_right) = 2',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'S_entry.TODO = ptask_old :: ptask_entry_tail*',
        'PhpStep: S_entry ~> S_begin_raw',
        f'S_begin_raw = S_entry[.TODO = (MOD_ASSIGN_SELECTED_WARNING pintegeroperation {left_bits} 12 0) :: ptask_entry_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = ROOT n_left]',
    ]
    step('S_begin', 'S_entry')
    checks += ['S_begin = S_begin_raw']
    seek('S_first_dispatch', 'S_begin', 2)
    checks += [
        'S_first_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_first_tail*',
        f'perrorcall_first.RESUME = MOD_ASSIGN_SELECTED_WARNING pintegeroperation {left_bits} 12 1',
        'perrorcall_first.TARGET = eps', 'perrorcall_first.LEVEL = 8192',
        'perrorcall_first.LINE = 25',
        'perrorcall_first.MESSAGE = $ptascii("Implicit conversion from float 12.5 to int loses precision")',
        '$error_call_valid(S_first_dispatch, perrorcall_first)',
    ]
    seek('S_first_entered', 'S_first_dispatch', 3)
    checks += ['$modassign_selected_entered(S_first_entered.FRAMES)', '$call_descriptors_valid(S_first_entered)']
    seek('S_first_return', 'S_first_entered', 4)
    checks += [
        f'S_first_return.TODO = (MOD_ASSIGN_SELECTED_WARNING pintegeroperation {left_bits} 12 1) :: ptask_caller*',
        f'$modassign_selected_warning_valid(S_first_return, pintegeroperation, {left_bits}, 12, 1)',
        '$lookup(S_first_return.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_first_return.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_first_return.ENV, $ptascii("rightAlias")) = (n_old_right)',
        '$lookup(S_first_return.ENV, $ptascii("right")) = (n_new_right)',
        'S_first_return.STORE[n_left] = DEFINED (PINT 99)',
        'S_first_return.STORE[n_old_right] = DEFINED (PINT 0)',
        f'S_first_return.STORE[n_new_right] = DEFINED (PFLOAT {right_bits})',
        'S_first_return.STORE[n_calls] = DEFINED (PINT 1)',
        'S_first_return.STORE[n_v] = DEFINED (PINT 100)',
        '$modassign_selected_warning_right(S_first_return, pintegeroperation) = eps',
        f'$modassign_selected_right_warning_plan(S_first_return) = ({marker(0)})',
        f'$modassign_selected_right_warning_snapshot(S_first_return, pintegeroperation, {right_bits})',
        f'~$modassign_selected_right_warning_snapshot(S_first_return[.ENV = (BIND ($ptascii("right")) n_old_right) :: $unbind(S_first_return.ENV, $ptascii("right"))], pintegeroperation, {right_bits})',
        '$heap_owners($heap_prune($heap_graph(S_first_return)), HCELL n_old_right) = 1',
        '$heap_owners($heap_prune($heap_graph(S_first_return)), HCELL n_new_right) = 2',
        '$call_descriptors_valid(S_first_return)', '$heap_valid($heap_graph(S_first_return))',
        'PhpStep: S_first_return ~> S_capture_raw',
        f'S_capture_raw = S_first_return[.TODO = ({marker(0)}) :: ptask_caller*]',
    ]
    step('S_capture', 'S_first_return')
    checks += ['S_capture = S_capture_raw', '$modassign_selected_rhs_frontier(S_capture, 5)',
               valid('S_capture', 0), '$task_nodes(' + marker(0) + ') = eps']
    step('S_dispatch', 'S_capture')
    checks += [
        '$modassign_selected_rhs_frontier(S_dispatch, 6)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_right) :: ptask_caller*',
        'perrorcall_right.RESUME = ' + marker(1),
        'perrorcall_right.TARGET = eps', 'perrorcall_right.LEVEL = 8192',
        'perrorcall_right.LINE = 25',
        'perrorcall_right.MESSAGE = $ptascii("Implicit conversion from float 5.5 to int loses precision")',
        '$error_call_valid(S_dispatch, perrorcall_right)',
    ]
    seek('S_entered', 'S_dispatch', 7)
    checks += ['$modassign_selected_rhs_entered(S_entered.FRAMES)', '$call_descriptors_valid(S_entered)']
    seek('S_return', 'S_entered', 8)
    checks += [
        'S_return.TODO = (' + marker(1) + ') :: ptask_caller*',
        'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
        valid('S_return', 1),
        f'~$modassign_selected_right_warning_snapshot(S_return, pintegeroperation, {right_bits})',
        '$integer_pointer_value(S_return, pintegeroperation.RIGHTPOINTER) = eps',
        '$lookup(S_return.ENV, $ptascii("right")) = eps',
        '$lookup(S_return.ENV, $ptascii("replacementRight")) = eps',
        '$lookup(S_return.ENV, $ptascii("left")) = (n_replacement_left)',
        '$lookup(S_return.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_return.ENV, $ptascii("rightAlias")) = (n_old_right)',
        'S_return.STORE[n_left] = DEFINED (PINT 88)',
        'S_return.STORE[n_old_right] = DEFINED (PINT 0)',
        'S_return.STORE[n_new_right] = DEFINED (PINT 7)',
        'S_return.STORE[n_replacement_left] = DEFINED (PINT 77)',
        'S_return.STORE[n_calls] = DEFINED (PINT 2)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_old_right) = 1',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_new_right) = 0',
        '~((HCELL n_new_right) <- S_return.ALLOCATIONS)',
        '$integer_pointer_value(S_return, INTEGER_CELL n_new_right) = eps',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_replacement_left) = 2',
        '$modassign_selected_warning_target(S_return, pintegeroperation)',
        '$modassign_selected_rhs_diagnostics(S_return.EVENTS, "Deprecated") = 1',
        '$modassign_selected_rhs_diagnostics(S_return.EVENTS, "Warning") = 0',
        'S_return.EVENTS[0:|S_first_return.EVENTS|] = S_first_return.EVENTS',
        'S_return.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'PhpStep: S_return ~> S_atomic',
        'S_atomic = S_return[.TODO = ptask_caller*][.RESULT = KNOWN (PINT 2)][.LOCATION = ROOT n_left][.STORE[n_left] = DEFINED (PINT 2)]',
    ]
    step('S_result', 'S_return')
    checks += [
        '$modassign_selected_rhs_frontier(S_result, 9)',
        'S_result.RESULT = KNOWN (PINT 2)', 'S_result.TODO = ptask_caller*',
        'S_result.LOCATION = ROOT n_left', 'S_result.STORE = S_atomic.STORE',
        'S_result.ENV = S_return.ENV', 'S_result.REFCELLS = S_return.REFCELLS',
        'S_result.ALLOCATIONS = S_return.ALLOCATIONS', 'S_result.EVENTS = S_return.EVENTS',
        'S_result.STRINGDATA = S_return.STRINGDATA', 'S_result.ARRAYS = S_return.ARRAYS',
        'S_result.OBJECTS = S_return.OBJECTS',
        '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_left) = 1',
        '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 3500)', 'S_done.COMPLETION = NORMAL',
        'S_done.EXITSTATUS = 0', 'S_done.TODO = eps', 'S_done.CURRENT = eps',
        'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_left] = DEFINED (PINT 6)',
        'S_done.STORE[n_old_right] = DEFINED (PINT 4)',
        'S_done.STORE[n_replacement_left] = DEFINED (PINT 8)',
        'S_done.STORE[n_new_right] = DEFINED (PINT 7)',
        'S_done.STORE[n_v] = DEFINED (PINT 2)',
        'S_done.STORE[n_calls] = DEFINED (PINT 2)',
        '$lookup(S_done.ENV, $ptascii("right")) = eps',
        '$lookup(S_done.ENV, $ptascii("replacementRight")) = eps',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_new_right) = 0',
        '~((HCELL n_new_right) <- S_done.ALLOCATIONS)',
        '$modassign_selected_rhs_diagnostics(S_done.EVENTS, "Deprecated") = 1',
        '$modassign_selected_rhs_diagnostics(S_done.EVENTS, "Warning") = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_first_return, 0) = S_first_return[.COMPLETION = BUDGET]',
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
