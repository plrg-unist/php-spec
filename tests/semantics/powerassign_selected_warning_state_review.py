#!/usr/bin/env python3
"""Signed cached power stores through the old reference after RHS retirement."""
import base64
import json

import powerassign_selected_warning_review_cases as cases
import powerassign_selected_warning_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = r'''
dec $powerassign_selected_review_diagnostic(pevent, text) : nat
def $powerassign_selected_review_diagnostic(DIAGNOSTIC text n* z, text) = 1
def $powerassign_selected_review_diagnostic(DIAGNOSTIC_SOURCE n_source text n* z, text) = 1
def $powerassign_selected_review_diagnostic(DIAGNOSTIC_STACK text n* z n_trace*, text) = 1
def $powerassign_selected_review_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n* z n_trace*, text) = 1
def $powerassign_selected_review_diagnostic(pevent, text) = 0 -- otherwise
dec $powerassign_selected_review_diagnostics(pevent*, text) : nat
def $powerassign_selected_review_diagnostics(eps, text) = 0
def $powerassign_selected_review_diagnostics(pevent :: pevent_tail*, text) = $($powerassign_selected_review_diagnostic(pevent, text) + $powerassign_selected_review_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    left_number = 'NFLOAT 9223372036854775808'
    right_number = 'NINT (-3)'
    result = 'PFLOAT 18442240474082181120'
    marker = lambda stage: f'POWER_ASSIGN_SELECTED_WARNING pintegeroperation n_left ({left_number}) ({right_number}) {stage} eps'
    valid = lambda state, stage: f'$powerassign_selected_warning_valid({state}, pintegeroperation, n_left, {left_number}, {right_number}, {stage}, eps)'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $powerassign_selected_seek({before}, {stage}, 5000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$powerassign_selected_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$powerassign_selected_warning_plan(S_entry) = (' + marker(0) + ')',
        '$powerassign_warning_plan(S_entry) = eps',
        '$powerassign_selected_warning_source(S_entry, pintegeroperation)',
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
        'S_entry.STORE[n_left] = DEFINED (PFLOAT 9223372036854775808)',
        'S_entry.STORE[n_right] = DEFINED (PINT (-3))',
        'S_entry.STORE[n_replacement_left] = DEFINED (PINT 77)',
        'S_entry.STORE[n_replacement_right] = DEFINED (PINT 7)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', 'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '$powerassign_selected_warning_snapshot(S_entry, pintegeroperation, n_left, ' + left_number + ', ' + right_number + ')',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 2',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'S_entry.TODO = ptask_old :: ptask_tail*', 'PhpStep: S_entry ~> S_capture',
        'S_capture = S_entry[.TODO = (' + marker(0) + ') :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = ROOT n_left]',
        valid('S_capture', 0), '$task_nodes(' + marker(0) + ') = eps',
        '~$powerassign_selected_warning_valid(S_capture, pintegeroperation, n_left, NFLOAT 0, ' + right_number + ', 0, eps)',
        '$powerassign_selected_review_diagnostics(S_capture.EVENTS, "Deprecated") = 0',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(1), 'perrorcall.TARGET = eps',
        'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 25',
        '$error_call_valid(S_dispatch, perrorcall)', '$call_descriptors_valid(S_dispatch)',
        'perrorcall_positive = perrorcall[.RESUME = POWER_ASSIGN_SELECTED_WARNING pintegeroperation n_left (NFLOAT 0) (' + right_number + ') 1 eps]',
        '~$error_call_valid(S_dispatch, perrorcall_positive)',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += ['$powerassign_selected_entered(S_entered.FRAMES)', '$call_descriptors_valid(S_entered)']
    seek('S_return', 'S_entered', 4)
    checks += [
        'S_return.TODO = (' + marker(1) + ') :: ptask_tail*',
        'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
        'S_return.STORE[n_left] = DEFINED (PINT 88)', 'S_return.STORE[n_right] = DEFINED (PINT 7)',
        'S_return.STORE[n_calls] = DEFINED (PINT 1)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
        '$lookup(S_return.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_return.ENV, $ptascii("left")) = (n_replacement_left)',
        '$lookup(S_return.ENV, $ptascii("replacementLeft")) = (n_replacement_left)',
        '$lookup(S_return.ENV, $ptascii("rightAlias")) = eps',
        '$lookup(S_return.ENV, $ptascii("right")) = (n_replacement_right)',
        '$lookup(S_return.ENV, $ptascii("replacementRight")) = (n_replacement_right)',
        'S_return.STORE[n_replacement_left] = DEFINED (PINT 77)',
        'S_return.STORE[n_replacement_right] = DEFINED (PINT 7)',
        'n_left =/= n_replacement_left', 'n_right =/= n_replacement_right',
        '$integer_pointer_select(S_return, pintegeroperation.LEFT) = (INTEGER_CELL n_replacement_left)',
        '$integer_pointer_select(S_return, pintegeroperation.RIGHT) = (INTEGER_CELL n_replacement_right)',
        '$integer_pointer_value(S_return, pintegeroperation.LEFTPOINTER) = (PINT 88)',
        '$integer_pointer_value(S_return, pintegeroperation.RIGHTPOINTER) = eps',
        '$powerassign_selected_warning_source(S_return, pintegeroperation)', '~$arithmetic_add_selected(S_return, pintegeroperation)',
        valid('S_return', 1), '~' + valid('S_return', 0),
        '$powerassign_selected_warning_ready(S_return, pintegeroperation, n_left)',
        '~$powerassign_selected_warning_ready(S_return, pintegeroperation, n_replacement_left)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 0',
        '~((HCELL n_right) <- S_return.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_replacement_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_replacement_right) = 2',
        '$powerassign_selected_review_diagnostics(S_return.EVENTS, "Deprecated") = 1',
        '$powerassign_selected_review_diagnostics(S_return.EVENTS, "Warning") = 0',
        'S_return.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'PhpStep: S_return ~> S_atomic',
        'S_atomic = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (' + result + ')][.LOCATION = ROOT n_left][.STORE[n_left] = DEFINED (' + result + ')]',
    ]
    step('S_commit', 'S_return')
    checks += [
        '$powerassign_selected_frontier(S_commit, 5)', 'S_commit.TODO = S_atomic.TODO',
        'S_commit.RESULT = S_atomic.RESULT', 'S_commit.STORE = S_atomic.STORE',
        'S_commit.LOCATION = ROOT n_left', 'S_commit.ENV = S_return.ENV',
        'S_commit.REFCELLS = S_return.REFCELLS', 'S_commit.ALLOCATIONS = S_return.ALLOCATIONS',
        'S_commit.ARRAYS = S_return.ARRAYS', 'S_commit.OBJECTS = S_return.OBJECTS',
        'S_commit.EVENTS = S_return.EVENTS', 'S_commit.STRINGDATA = S_return.STRINGDATA',
        '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_right) = 0',
        '~$powerassign_selected_tasks(S_commit.TODO)', '$call_descriptors_valid(S_commit)', '$heap_valid($heap_graph(S_commit))',
        'S_done = $drive_steps(S_commit, 5000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_v] = DEFINED (' + result + ')', 'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        '$lookup(S_done.ENV, $ptascii("leftAlias")) = (n_left)', 'S_done.STORE[n_left] = DEFINED (PINT 6)',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_replacement_left)',
        '$lookup(S_done.ENV, $ptascii("replacementLeft")) = (n_replacement_left)',
        'S_done.STORE[n_replacement_left] = DEFINED (PINT 8)',
        '$lookup(S_done.ENV, $ptascii("right")) = (n_replacement_right)',
        '$lookup(S_done.ENV, $ptascii("replacementRight")) = (n_replacement_right)',
        'S_done.STORE[n_replacement_right] = DEFINED (PINT 9)',
        '$lookup(S_done.ENV, $ptascii("rightAlias")) = eps',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_right) = 0',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement_right) = 2',
        '$powerassign_selected_review_diagnostics(S_done.EVENTS, "Deprecated") = 1',
        '$powerassign_selected_review_diagnostics(S_done.EVENTS, "Warning") = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_entry, 7000) = S_done',
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
