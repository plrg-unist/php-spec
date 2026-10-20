#!/usr/bin/env python3
"""Same-CV self ADD converts RIGHT after the first Warning callback."""
import base64
import json

import addassign_self_warning_cases as cases
import addassign_rhs_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $addassign_self_frontier(pstate, nat) : bool
def $addassign_self_frontier(S, 0) = ($arithmetic_addassign_self_plan(S) =/= eps)
def $addassign_self_frontier(S, n) = $addassign_rhs_warning_frontier(S, n)
  -- if $(n > 0 /\ n <= 9)
def $addassign_self_frontier(S, 10) = ($addassign_cv_frontier(S, 5) /\ ~$addassign_rhs_warning_tasks(S.TODO))
def $addassign_self_frontier(S, n) = false -- otherwise
dec $addassign_self_seek(pstate, nat, nat) : pstate
def $addassign_self_seek(S, n_stage, n) = S -- if $addassign_self_frontier(S, n_stage)
def $addassign_self_seek(S, n_stage, n) = S
  -- if ~$addassign_self_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $addassign_self_seek(S, n_stage, n) = S
  -- if ~$addassign_self_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $addassign_self_seek(S, n_stage, n) = $addassign_self_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$addassign_self_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
dec $addassign_self_diagnostic(pevent, text) : nat
def $addassign_self_diagnostic(DIAGNOSTIC text n_message* z, text) = 1
def $addassign_self_diagnostic(DIAGNOSTIC_SOURCE n_source text n_message* z, text) = 1
def $addassign_self_diagnostic(DIAGNOSTIC_STACK text n_message* z n_trace*, text) = 1
def $addassign_self_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n_message* z n_trace*, text) = 1
def $addassign_self_diagnostic(pevent, text) = 0 -- otherwise
dec $addassign_self_diagnostics(pevent*, text) : nat
def $addassign_self_diagnostics(eps, text) = 0
def $addassign_self_diagnostics(pevent :: pevent_tail*, text) = $($addassign_self_diagnostic(pevent, text) + $addassign_self_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $addassign_self_seek({before}, {stage}, 3000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$addassign_self_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$arithmetic_addassign_self_plan(S_entry) = ((pintegeroperation, pvalue_left, NFLOAT 4623226492472524800))',
        '$arithmetic_addassign_cv_plan(S_entry) = eps',
        '$arithmetic_addassign_plan(S_entry) = eps',
        '$arithmetic_addassign_repair_plan(S_entry) = eps',
        'pintegeroperation.OP = ADD',
        '~pintegeroperation.SWAPPED',
        'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("x")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("x")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("x"))',
        'pintegeroperation.RIGHTPOINTER = pintegeroperation.LEFTPOINTER',
        'S_entry.TODO = (COMPOUND_APPLY ADD (BASE_VALUE pintegeroperation.LEFT) true 25) :: ptask_tail*',
        '$arithmetic_addassign_cv_source(S_entry, pintegeroperation)',
        '$arithmetic_add_selected(S_entry, pintegeroperation)',
        '$integer_pointer_select(S_entry, pintegeroperation.LEFT) = (pintegeroperation.LEFTPOINTER)',
        '$integer_pointer_select(S_entry, pintegeroperation.RIGHT) = (pintegeroperation.RIGHTPOINTER)',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        'S_entry.STORE[n_x] = DEFINED pvalue_left',
        '$string_bytes(pvalue_left) = ($ptascii("12.5tail"))',
        '$arithmetic_add_conversion(pvalue_left) = ((NFLOAT 4623226492472524800, true))',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '~(n_x <- S_entry.REFCELLS)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        'S_entry.EVENTS = eps',
        '$call_descriptors_valid(S_entry)',
        '$heap_valid($heap_graph(S_entry))',
        '$arithmetic_addassign_self_plan(S_entry[.ORIGIN = eps]) = eps',
        '$arithmetic_addassign_self_plan(S_entry[.CODE = eps]) = eps',
        '$arithmetic_addassign_self_plan(S_entry[.RESULT = KNOWN pvalue_left]) = eps',
        '$arithmetic_addassign_self_plan(S_entry[.RESULT = VARIABLE ($ptascii("v")) 25]) = eps',
        '$arithmetic_addassign_self_plan(S_entry[.STORE[n_x] = UNDEFINED]) = eps',
        '$arithmetic_addassign_self_plan(S_entry[.STORE[n_x] = DEFINED (PINT 5)]) = eps',
        '$arithmetic_addassign_self_plan(S_entry[.REFCELLS = [n_x]]) = eps',
        '$arithmetic_addassign_self_plan(S_entry[.ALLOCATIONS = eps]) = eps',
        '$arithmetic_addassign_self_plan(S_entry[.PROPREFS = [{CELL n_x, SOURCES eps}]]) = eps',
        '$arithmetic_addassign_self_plan(S_entry[.ERRORHANDLER.CALLBACK = eps]) = eps',
        '$arithmetic_addassign_self_plan(S_entry[.ERRORHANDLER.LEVELS = 8192]) = eps',
        '$arithmetic_addassign_self_plan(S_entry[.TODO = (COMPOUND_APPLY ADD (BASE_VALUE pintegeroperation.LEFT) false 25) :: ptask_tail*]) = eps',
        '~$arithmetic_addassign_cv_source(S_entry, pintegeroperation[.OP = DIVIDE])',
        '~$arithmetic_addassign_cv_source(S_entry, pintegeroperation[.LINE = 24])',
        '~$arithmetic_addassign_cv_source(S_entry, pintegeroperation[.SWAPPED = true])',
        '~$arithmetic_addassign_cv_source(S_entry, pintegeroperation[.LEFTPOINTER = INTEGER_CELL n_x])',
        'PhpStep: S_entry ~> S_begin_atomic',
        'S_begin_atomic = S_entry[.TODO = (ARITHMETIC_ADDASSIGN_CV_WARNING pintegeroperation pvalue_left (NFLOAT 4623226492472524800) 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.LOCATION = ROOT n_x]',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture = S_begin_atomic',
        '$addassign_self_frontier(S_capture, 1)',
        '$arithmetic_addassign_cv_warning_valid(S_capture, pintegeroperation, pvalue_left, NFLOAT 4623226492472524800, 0)',
        '$task_nodes(ARITHMETIC_ADDASSIGN_CV_WARNING pintegeroperation pvalue_left (NFLOAT 4623226492472524800) 0) = eps',
        '$call_descriptors_valid(S_capture)',
    ]
    step('S_first_call', 'S_capture')
    checks += [
        '$addassign_self_frontier(S_first_call, 2)',
        'S_first_call.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
        'perrorcall_first.RESUME = ARITHMETIC_ADDASSIGN_CV_WARNING pintegeroperation pvalue_left (NFLOAT 4623226492472524800) 1',
        'perrorcall_first.TARGET = eps',
        'perrorcall_first.LINE = 25',
        'perrorcall_first.LEVEL = 2',
        'perrorcall_first.MESSAGE = $ptascii("A non-numeric value encountered")',
        '$error_call_valid(S_first_call, perrorcall_first)',
        '~$error_call_valid(S_first_call, perrorcall_first[.LINE = 24])',
        '~$error_call_valid(S_first_call, perrorcall_first[.LEVEL = 8192])',
        '$call_descriptors_valid(S_first_call)',
    ]
    seek('S_first_entered', 'S_first_call', 3)
    checks += [
        '$addassign_rhs_warning_entered(S_first_entered.FRAMES, 0)',
        '$call_descriptors_valid(S_first_entered)',
    ]
    seek('S_first_return', 'S_first_entered', 4)
    checks += [
        'S_first_return.TODO = (ARITHMETIC_ADDASSIGN_CV_WARNING pintegeroperation pvalue_left (NFLOAT 4623226492472524800) 1) :: ptask_tail*',
        'S_first_return.CURRENT = eps',
        'S_first_return.FRAMES = eps',
        '$lookup(S_first_return.ENV, $ptascii("x")) = (n_x)',
        'S_first_return.STORE[n_x] = DEFINED pvalue_right',
        '$string_bytes(pvalue_right) = ($ptascii("5.5tail"))',
        '$integer_pointer_value(S_first_return, pintegeroperation.LEFTPOINTER) = (pvalue_right)',
        '$integer_pointer_value(S_first_return, pintegeroperation.RIGHTPOINTER) = (pvalue_right)',
        'S_first_return.STORE[n_v] = DEFINED (PINT 100)',
        'S_first_return.STORE[n_calls] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_first_return)), HCELL n_x) = 1',
        '$arithmetic_addassign_cv_warning_valid(S_first_return, pintegeroperation, pvalue_left, NFLOAT 4623226492472524800, 1)',
        '~$arithmetic_addassign_cv_warning_valid(S_first_return, pintegeroperation, pvalue_left, NFLOAT 4623226492472524800, 0)',
        '$arithmetic_addassign_cv_ready(S_first_return, pintegeroperation) = eps',
        '$arithmetic_addassign_cv_right_snapshot(S_first_return, pintegeroperation) = ((pvalue_right, NFLOAT 4617878467915022336))',
        '$arithmetic_addassign_cv_right_target(S_first_return, pintegeroperation)',
        '$addassign_self_diagnostics(S_first_return.EVENTS, "Warning") = 0',
        '$call_descriptors_valid(S_first_return)',
        '$heap_valid($heap_graph(S_first_return))',
        'PhpStep: S_first_return ~> S_rhs_atomic',
        'S_rhs_atomic = S_first_return[.TODO = (ARITHMETIC_ADDASSIGN_CV_RIGHT_WARNING pintegeroperation pvalue_left (NFLOAT 4623226492472524800) pvalue_right (NFLOAT 4617878467915022336) 0) :: ptask_tail*]',
    ]
    step('S_rhs_capture', 'S_first_return')
    checks += [
        'S_rhs_capture = S_rhs_atomic',
        '$addassign_self_frontier(S_rhs_capture, 5)',
        '$task_nodes(ARITHMETIC_ADDASSIGN_CV_RIGHT_WARNING pintegeroperation pvalue_left (NFLOAT 4623226492472524800) pvalue_right (NFLOAT 4617878467915022336) 0) = eps',
        '$arithmetic_addassign_cv_right_warning_valid(S_rhs_capture, pintegeroperation, pvalue_left, NFLOAT 4623226492472524800, pvalue_right, NFLOAT 4617878467915022336, 0)',
        '$call_descriptors_valid(S_rhs_capture)',
    ]
    step('S_second_call', 'S_rhs_capture')
    checks += [
        '$addassign_self_frontier(S_second_call, 6)',
        'S_second_call.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
        'perrorcall_second.RESUME = ARITHMETIC_ADDASSIGN_CV_RIGHT_WARNING pintegeroperation pvalue_left (NFLOAT 4623226492472524800) pvalue_right (NFLOAT 4617878467915022336) 1',
        'perrorcall_second.TARGET = eps',
        'perrorcall_second.LINE = 25',
        'perrorcall_second.LEVEL = 2',
        'perrorcall_second.MESSAGE = perrorcall_first.MESSAGE',
        '$error_call_valid(S_second_call, perrorcall_second)',
        '$call_descriptors_valid(S_second_call)',
    ]
    seek('S_second_entered', 'S_second_call', 7)
    checks += [
        '$addassign_rhs_warning_entered(S_second_entered.FRAMES, 1)',
        '$call_descriptors_valid(S_second_entered)',
    ]
    seek('S_second_return', 'S_second_entered', 8)
    checks += [
        'S_second_return.TODO = (ARITHMETIC_ADDASSIGN_CV_RIGHT_WARNING pintegeroperation pvalue_left (NFLOAT 4623226492472524800) pvalue_right (NFLOAT 4617878467915022336) 1) :: ptask_tail*',
        'S_second_return.CURRENT = eps',
        'S_second_return.FRAMES = eps',
        '$lookup(S_second_return.ENV, $ptascii("x")) = (n_x)',
        'S_second_return.STORE[n_x] = DEFINED (PINT 88)',
        'S_second_return.STORE[n_v] = DEFINED (PINT 100)',
        'S_second_return.STORE[n_calls] = DEFINED (PINT 2)',
        '$arithmetic_addassign_cv_right_snapshot(S_second_return, pintegeroperation) = eps',
        '$arithmetic_addassign_cv_right_warning_valid(S_second_return, pintegeroperation, pvalue_left, NFLOAT 4623226492472524800, pvalue_right, NFLOAT 4617878467915022336, 1)',
        '~$arithmetic_addassign_cv_right_warning_valid(S_second_return, pintegeroperation, pvalue_left, NFLOAT 4623226492472524800, pvalue_right, NFLOAT 4617878467915022336, 0)',
        '$arithmetic_addassign_cv_right_target(S_second_return, pintegeroperation)',
        '$heap_owners($heap_prune($heap_graph(S_second_return)), HCELL n_x) = 1',
        '$addassign_self_diagnostics(S_second_return.EVENTS, "Warning") = 1',
        '$addassign_self_diagnostics(S_second_return.EVENTS, "Deprecated") = 0',
        '$call_descriptors_valid(S_second_return)',
        '$heap_valid($heap_graph(S_second_return))',
        'PhpStep: S_second_return ~> S_atomic',
        'S_atomic = $arithmetic_addassign_cv_write(S_second_return[.TODO = ptask_tail*][.RESULT = KNOWN (PFLOAT 4625759767262920704)], $ptascii("x"), PFLOAT 4625759767262920704)',
        'S_atomic.STORE[n_x] = DEFINED (PFLOAT 4625759767262920704)',
        'S_atomic.STORE[n_v] = DEFINED (PINT 100)',
        'S_atomic.ENV = S_second_return.ENV',
        'S_atomic.ALLOCATIONS = S_second_return.ALLOCATIONS',
        'S_atomic.REFCELLS = S_second_return.REFCELLS',
        'S_atomic.CELL = n_x',
        'S_atomic.LOCATION = ROOT n_x',
        'S_atomic.EVENTS = S_second_return.EVENTS',
    ]
    step('S_result', 'S_second_return')
    checks += [
        'S_result.TODO = S_atomic.TODO',
        'S_result.RESULT = S_atomic.RESULT',
        'S_result.STORE = S_atomic.STORE',
        'S_result.ENV = S_atomic.ENV',
        'S_result.REFCELLS = S_atomic.REFCELLS',
        'S_result.LOCATION = S_atomic.LOCATION',
        'S_result.CELL = S_atomic.CELL',
        '$addassign_self_frontier(S_result, 10)',
        '$call_descriptors_valid(S_result)',
        '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 3000)',
        'S_done.COMPLETION = NORMAL',
        'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps',
        'S_done.FRAMES = eps',
        'S_done.CURRENT = eps',
        'S_done.HELD = eps',
        'S_done.STORE[n_x] = DEFINED (PINT 8)',
        'S_done.STORE[n_v] = DEFINED (PFLOAT 4625759767262920704)',
        'S_done.STORE[n_calls] = DEFINED (PINT 2)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_x) = 1',
        '$addassign_self_diagnostics(S_done.EVENTS, "Warning") = 1',
        '$addassign_self_diagnostics(S_done.EVENTS, "Deprecated") = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_rhs_capture, 0) = S_rhs_capture[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
