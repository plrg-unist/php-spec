#!/usr/bin/env python3
"""A rebound zero RHS fails after LEFT capture without changing the old target."""
import base64
import json

import modassign_selected_warning_review_cases as cases
import modassign_selected_warning_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = r'''
dec $modassign_selected_review_diagnostic(pevent, text) : nat
def $modassign_selected_review_diagnostic(DIAGNOSTIC text n* z, text) = 1
def $modassign_selected_review_diagnostic(DIAGNOSTIC_SOURCE n_source text n* z, text) = 1
def $modassign_selected_review_diagnostic(DIAGNOSTIC_STACK text n* z n_trace*, text) = 1
def $modassign_selected_review_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n* z n_trace*, text) = 1
def $modassign_selected_review_diagnostic(pevent, text) = 0 -- otherwise
dec $modassign_selected_review_diagnostics(pevent*, text) : nat
def $modassign_selected_review_diagnostics(eps, text) = 0
def $modassign_selected_review_diagnostics(pevent :: pevent_tail*, text) = $($modassign_selected_review_diagnostic(pevent, text) + $modassign_selected_review_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    marker = lambda stage, op='pintegeroperation': f'MOD_ASSIGN_SELECTED_WARNING {op} n_bits i_left {stage}'
    valid = lambda state, stage: f'$modassign_selected_warning_valid({state}, pintegeroperation, n_bits, i_left, {stage})'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $modassign_selected_seek({before}, {stage}, 4000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$modassign_selected_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$modassign_selected_warning_plan(S_entry) = (' + marker(0) + ')',
        '$modassign_warning_plan(S_entry) = eps',
        '$modassign_selected_warning_source(S_entry, pintegeroperation)',
        '$modassign_selected_warning_snapshot(S_entry, pintegeroperation, n_bits)',
        'n_bits = 4623226492472524800', 'i_left = 12',
        'pintegeroperation.OP = MODULO', '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
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
        'S_entry.STORE[n_old_right] = DEFINED (PINT 5)',
        'S_entry.STORE[n_replacement_left] = DEFINED (PINT 77)',
        'S_entry.STORE[n_replacement_right] = DEFINED (PINT 0)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', 'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'n_target <- S_entry.REFCELLS', 'n_old_right <- S_entry.REFCELLS',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_target) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_old_right) = 2',
        '$modassign_selected_warning_right(S_entry, pintegeroperation) = (5)',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture.TODO = (' + marker(0) + ') :: ptask_tail*',
        'S_capture.RESULT = KNOWN PNULL', 'S_capture.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_capture.LOCATION = ROOT n_target', valid('S_capture', 0),
        '$task_nodes(' + marker(0) + ') = eps',
        'S_capture.STORE = S_entry.STORE', 'S_capture.ENV = S_entry.ENV',
        '$modassign_selected_review_diagnostics(S_capture.EVENTS, "Deprecated") = 0',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(1), 'perrorcall.TARGET = eps',
        'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = $ptascii("Implicit conversion from float 12.5 to int loses precision")',
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
        'S_return.STORE[n_old_right] = DEFINED (PINT 5)',
        'S_return.STORE[n_replacement_left] = DEFINED (PINT 77)',
        'S_return.STORE[n_replacement_right] = DEFINED (PINT 0)',
        'S_return.STORE[n_calls] = DEFINED (PINT 1)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
        '$integer_pointer_value(S_return, pintegeroperation.LEFTPOINTER) = (PINT 88)',
        '$integer_pointer_value(S_return, pintegeroperation.RIGHTPOINTER) = (PINT 0)',
        '$integer_pointer_value(S_return, INTEGER_CELL n_old_right) = (PINT 5)',
        valid('S_return', 1), '~' + valid('S_return', 0),
        '$modassign_selected_warning_target(S_return, pintegeroperation)',
        '$modassign_selected_warning_right(S_return, pintegeroperation) = (0)',
        '$long_mod(i_left, 0) = INTZERO', '$long_mod(i_left, 5) = IRESULT 2',
        'pintegeroperation_old_right = pintegeroperation[.RIGHTPOINTER = INTEGER_CELL n_old_right]',
        '~$modassign_selected_warning_source(S_return, pintegeroperation_old_right)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_old_right) = 1',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_replacement_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_replacement_right) = 2',
        '$modassign_selected_review_diagnostics(S_return.EVENTS, "Deprecated") = 1',
        '$modassign_selected_review_diagnostics(S_return.EVENTS, "Warning") = 0',
        'S_return.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'PhpStep: S_return ~> S_atomic',
        'S_atomic = S_return[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) 25]',
    ]
    step('S_error', 'S_return')
    checks += [
        '$modassign_selected_frontier(S_error, 6)',
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        'S_error.RESULT = KNOWN PNULL', 'S_error.CURRENT = eps', 'S_error.FRAMES = eps',
        'n_error = |S_return.OBJECTS|', 'S_error.OBJECTS[n_error] = THROWABLE pthrowable',
        'pthrowable.KIND = "DivisionByZeroError"', 'pthrowable.ORIGIN = (pintegeroperation.SITE)',
        'S_error.OBJECTS = S_return.OBJECTS ++ [THROWABLE pthrowable]',
        '$throwable_field(S_error, n_error, "line") = PINT 25',
        '$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("Modulo by zero"))',
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
        '$modassign_selected_review_diagnostics(S_done.EVENTS, "Deprecated") = 1',
        '$modassign_selected_review_diagnostics(S_done.EVENTS, "Warning") = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
