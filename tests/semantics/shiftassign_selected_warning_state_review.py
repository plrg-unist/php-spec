#!/usr/bin/env python3
"""Selected right shift keeps its saved sign and reads the rebound count."""
import base64
import json

import shiftassign_selected_warning_review_cases as cases
import shiftassign_selected_warning_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = r'''
dec $shiftassign_selected_review_diagnostic(pevent, text) : nat
def $shiftassign_selected_review_diagnostic(DIAGNOSTIC text n* z, text) = 1
def $shiftassign_selected_review_diagnostic(DIAGNOSTIC_SOURCE n_source text n* z, text) = 1
def $shiftassign_selected_review_diagnostic(DIAGNOSTIC_STACK text n* z n_trace*, text) = 1
def $shiftassign_selected_review_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n* z n_trace*, text) = 1
def $shiftassign_selected_review_diagnostic(pevent, text) = 0 -- otherwise
dec $shiftassign_selected_review_diagnostics(pevent*, text) : nat
def $shiftassign_selected_review_diagnostics(eps, text) = 0
def $shiftassign_selected_review_diagnostics(pevent :: pevent_tail*, text) = $($shiftassign_selected_review_diagnostic(pevent, text) + $shiftassign_selected_review_diagnostics(pevent_tail*, text))
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
        '$shiftassign_warning_plan(S_entry) = eps', '$shiftassign_both_warning_plan(S_entry) = eps',
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
        'S_entry.STORE[n_replacement_right] = DEFINED (PINT 64)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', 'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'n_target =/= n_old_right', 'n_target <- S_entry.REFCELLS', 'n_old_right <- S_entry.REFCELLS',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_target) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_old_right) = 2',
        '$shiftassign_selected_warning_right(S_entry, pintegeroperation) = (2)',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture.TODO = (' + marker(0) + ') :: ptask_tail*',
        'S_capture.RESULT = KNOWN PNULL', 'S_capture.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_capture.LOCATION = ROOT n_target', valid('S_capture', 0),
        '$task_nodes(' + marker(0) + ') = eps',
        'S_capture.STORE = S_entry.STORE', 'S_capture.ENV = S_entry.ENV',
        'S_capture.ALLOCATIONS = S_entry.ALLOCATIONS',
        '$shiftassign_selected_review_diagnostics(S_capture.EVENTS, "Deprecated") = 0',
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
        'S_return.STORE[n_target] = DEFINED (PINT 99)',
        'S_return.STORE[n_old_right] = DEFINED (PINT 2)',
        'S_return.STORE[n_replacement_left] = DEFINED (PINT 77)',
        'S_return.STORE[n_replacement_right] = DEFINED (PINT 64)',
        'S_return.STORE[n_calls] = DEFINED (PINT 1)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
        '$integer_pointer_value(S_return, pintegeroperation.LEFTPOINTER) = (PINT 99)',
        '$integer_pointer_value(S_return, pintegeroperation.RIGHTPOINTER) = (PINT 64)',
        '$integer_pointer_value(S_return, INTEGER_CELL n_old_right) = (PINT 2)',
        valid('S_return', 1), '~' + valid('S_return', 0),
        '$shiftassign_selected_warning_target(S_return, pintegeroperation)',
        '$shiftassign_selected_warning_right(S_return, pintegeroperation) = (64)',
        '$integer_binary(SHIFTRIGHT, i_left, 64) = IRESULT $(-1)',
        '$integer_binary(SHIFTRIGHT, i_left, 2) = IRESULT $(-3)',
        '$integer_binary(SHIFTRIGHT, 99, 64) = IRESULT 0',
        'pintegeroperation_old_right = pintegeroperation[.RIGHTPOINTER = INTEGER_CELL n_old_right]',
        '~$shiftassign_selected_warning_source(S_return, pintegeroperation_old_right)',
        '$integer_right_pointer(SHIFTRIGHT, pintegeroperation.RIGHT, INTEGER_CELL n_old_right) = pintegeroperation.RIGHTPOINTER',
        '$integer_right_pointer(BITXOR, pintegeroperation.RIGHT, INTEGER_CELL n_old_right) = INTEGER_CELL n_old_right',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_old_right) = 1',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_replacement_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_replacement_right) = 2',
        '$shiftassign_selected_review_diagnostics(S_return.EVENTS, "Deprecated") = 1',
        '$shiftassign_selected_review_diagnostics(S_return.EVENTS, "Warning") = 0',
        'S_return.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'PhpStep: S_return ~> S_atomic',
        'S_atomic = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (PINT $(-1))][.LOCATION = ROOT n_target][.STORE[n_target] = DEFINED (PINT $(-1))]',
    ]
    step('S_commit', 'S_return')
    checks += [
        '$shiftassign_selected_frontier(S_commit, 5)',
        'S_commit.RESULT = KNOWN (PINT $(-1))', 'S_commit.LOCATION = ROOT n_target',
        'S_commit.STORE = S_atomic.STORE', 'S_commit.ENV = S_return.ENV',
        'S_commit.REFCELLS = S_return.REFCELLS', 'S_commit.ALLOCATIONS = S_return.ALLOCATIONS',
        'S_commit.EVENTS = S_return.EVENTS', 'S_commit.OBJECTS = S_return.OBJECTS',
        'S_commit.ARRAYS = S_return.ARRAYS', 'S_commit.STRINGDATA = S_return.STRINGDATA',
        '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_old_right) = 1',
        '$call_descriptors_valid(S_commit)', '$heap_valid($heap_graph(S_commit))',
        'S_done = $drive_steps(S_commit, 4000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_target] = DEFINED (PINT 6)',
        'S_done.STORE[n_old_right] = DEFINED (PINT 4)',
        'S_done.STORE[n_replacement_left] = DEFINED (PINT 8)',
        'S_done.STORE[n_replacement_right] = DEFINED (PINT 9)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)', 'S_done.STORE[n_v] = DEFINED (PINT $(-1))',
        '$lookup(S_done.ENV, $ptascii("leftAlias")) = (n_target)',
        '$lookup(S_done.ENV, $ptascii("rightAlias")) = (n_old_right)',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_replacement_left)',
        '$lookup(S_done.ENV, $ptascii("right")) = (n_replacement_right)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_old_right) = 1',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement_right) = 2',
        '$shiftassign_selected_review_diagnostics(S_done.EVENTS, "Deprecated") = 1',
        '$shiftassign_selected_review_diagnostics(S_done.EVENTS, "Warning") = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
