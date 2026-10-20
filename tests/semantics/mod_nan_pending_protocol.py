#!/usr/bin/env python3
"""A pending NaN modulo conversion reports precision before restoring the throw."""
import base64
import json

import mod_nan_pending_cases as cases
import integer_operator_warning_protocol as shared

CASES = ('mod-nan-pending-ineligible-precision',)
HELPERS = shared.HELPERS + r'''
dec $mod_nan_task(ptask) : bool
def $mod_nan_task(INTEGER_OPERATOR_CONVERT pintegeroperation pintegerphase) = true
def $mod_nan_task(INTEGER_OPERATOR_WARNING pintegeroperation pintegerphase pintegerconversion n) = true
def $mod_nan_task(MOD_NAN_PENDING pintegeroperation pintegerconversion n n_exception) = true
def $mod_nan_task(ERROR_HANDLER_INVOKE perrorcall) = $mod_nan_task(perrorcall.RESUME)
def $mod_nan_task(ERROR_HANDLER_RESULT perrorcall) = $mod_nan_task(perrorcall.RESUME)
def $mod_nan_task(ERROR_HANDLER_CLEAN perrorcall) = $mod_nan_task(perrorcall.RESUME)
def $mod_nan_task(ptask) = false -- otherwise
dec $mod_nan_tasks(ptask*) : bool
def $mod_nan_tasks(eps) = false
def $mod_nan_tasks(ptask :: ptask_tail*) = ($mod_nan_task(ptask) \/ $mod_nan_tasks(ptask_tail*))
dec $mod_nan_handler_frame(pframe, nat) : bool
def $mod_nan_handler_frame(pframe, n_cursor) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion n_cursor
  -- if perrorcall.TARGET =/= eps
def $mod_nan_handler_frame(pframe, n_cursor) = false -- otherwise
dec $mod_nan_entered(pframe*, nat) : bool
def $mod_nan_entered(eps, n_cursor) = false
def $mod_nan_entered(pframe :: pframe_tail*, n_cursor) = ($mod_nan_handler_frame(pframe, n_cursor) \/ $mod_nan_entered(pframe_tail*, n_cursor))
dec $mod_nan_frontier(pstate, nat) : bool
def $mod_nan_frontier(S, 0) = ($integer_operator_plan(S) =/= eps)
def $mod_nan_frontier(S, 1) = true
  -- if S.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 0) :: ptask_tail*
def $mod_nan_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 1
  -- if perrorcall.TARGET = eps
def $mod_nan_frontier(S, 3) = (S.CURRENT =/= eps /\ $mod_nan_entered(S.FRAMES, 1))
def $mod_nan_frontier(S, 4) = true
  -- if S.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 1) :: ptask_tail*
def $mod_nan_frontier(S, 5) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 2
  -- if perrorcall.TARGET = eps
def $mod_nan_frontier(S, 6) = (S.CURRENT =/= eps /\ $mod_nan_entered(S.FRAMES, 2))
def $mod_nan_frontier(S, 7) = true
  -- if S.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 2) :: ptask_tail*
def $mod_nan_frontier(S, 8) = true
  -- if S.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT i)) :: ptask_tail*
def $mod_nan_frontier(S, 9) = true
  -- if S.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i) pintegerconversion 0) :: ptask_tail*
def $mod_nan_frontier(S, 10) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprBinaryOpMod expression_left expression_right metadata)
  -- if S.RESULT = KNOWN (PINT i)
  -- if ~$mod_nan_tasks(S.TODO)
def $mod_nan_frontier(S, 11) = true
  -- if S.TODO = (MOD_NAN_PENDING pintegeroperation pintegerconversion 0 n_exception) :: ptask_tail*
def $mod_nan_frontier(S, 12) = true
  -- if S.TODO = (MOD_NAN_PENDING pintegeroperation pintegerconversion 1 n_exception) :: ptask_tail*
def $mod_nan_frontier(S, 13) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n_exception) :: ptask_tail*
  -- if ~$mod_nan_tasks(S.TODO)
def $mod_nan_frontier(S, n) = false -- otherwise
dec $mod_nan_seek(pstate, nat, nat) : pstate
def $mod_nan_seek(S, n_stage, n) = S -- if $mod_nan_frontier(S, n_stage)
def $mod_nan_seek(S, n_stage, n) = S
  -- if ~$mod_nan_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $mod_nan_seek(S, n_stage, n) = S
  -- if ~$mod_nan_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $mod_nan_seek(S, n_stage, n) = $mod_nan_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$mod_nan_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
dec $mod_nan_diagnostic(pevent, text) : nat
def $mod_nan_diagnostic(DIAGNOSTIC text n_message* z, text) = 1
def $mod_nan_diagnostic(DIAGNOSTIC_SOURCE n_source text n_message* z, text) = 1
def $mod_nan_diagnostic(DIAGNOSTIC_STACK text n_message* z n_trace*, text) = 1
def $mod_nan_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n_message* z n_trace*, text) = 1
def $mod_nan_diagnostic(pevent, text) = 0 -- otherwise
dec $mod_nan_diagnostics(pevent*, text) : nat
def $mod_nan_diagnostics(eps, text) = 0
def $mod_nan_diagnostics(pevent :: pevent_tail*, text) = $($mod_nan_diagnostic(pevent, text) + $mod_nan_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $mod_nan_seek({before}, {stage}, 4000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$mod_nan_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$integer_operator_plan(S_entry) = (pintegeroperation)',
        '$integer_operation_valid(S_entry, pintegeroperation)',
        'pintegeroperation.OP = MODULO', '~pintegeroperation.SWAPPED',
        'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("x")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("y")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("x"))',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("y"))',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)',
        '$lookup(S_entry.ENV, $ptascii("y")) = (n_y)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
        'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        'S_entry.STORE[n_x] = DEFINED (PFLOAT 9221120237041090560)',
        'S_entry.STORE[n_y] = DEFINED (PINT 5)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        'S_entry.ERRORHANDLER.LEVELS = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_y) = 1',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
    ]
    seek('S_capture', 'S_entry', 1)
    checks += [
        'S_capture.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 0) :: ptask_tail*',
        'pintegerconversion.INPUT = PFLOAT 9221120237041090560',
        'pintegerconversion.VALUE = 0',
        'pintegerconversion.NOTICES = [(2, $ptascii("The float NAN is not representable as an int, cast occurred")), (8192, $ptascii("Implicit conversion from float NAN to int loses precision"))]',
        '$integer_warning_valid(S_capture, pintegeroperation, INTEGER_LEFT, pintegerconversion, 0)',
        '$mod_nan_pending_source(S_capture, pintegeroperation, pintegerconversion)',
        '$task_nodes(INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 0) = eps',
        '~$mod_nan_pending_source(S_capture[.ORIGIN = eps], pintegeroperation, pintegerconversion)',
        '~$mod_nan_pending_source(S_capture[.CODE = eps], pintegeroperation, pintegerconversion)',
        '~$mod_nan_pending_source(S_capture, pintegeroperation[.OP = SHIFTRIGHT], pintegerconversion)',
        '~$mod_nan_pending_source(S_capture, pintegeroperation[.SWAPPED = true], pintegerconversion)',
        '~$mod_nan_pending_source(S_capture, pintegeroperation[.LINE = 24], pintegerconversion)',
        '~$mod_nan_pending_source(S_capture, pintegeroperation[.LEFT = VARIABLE ($ptascii("y")) 23], pintegerconversion)',
        '~$mod_nan_pending_source(S_capture, pintegeroperation[.LEFTPOINTER = INTEGER_CELL n_x], pintegerconversion)',
        '~$mod_nan_pending_source(S_capture, pintegeroperation[.RIGHTPOINTER = INTEGER_CELL n_y], pintegerconversion)',
        '~$mod_nan_pending_source(S_capture, pintegeroperation, pintegerconversion[.INPUT = PINT 0])',
        '~$mod_nan_pending_source(S_capture, pintegeroperation, pintegerconversion[.VALUE = 1])',
        '~$mod_nan_pending_source(S_capture, pintegeroperation, pintegerconversion[.NOTICES = eps])',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        '$mod_nan_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 1',
        'perrorcall.TARGET = eps', 'perrorcall.LEVEL = 2', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = $ptascii("The float NAN is not representable as an int, cast occurred")',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 8192])',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += ['$mod_nan_entered(S_entered.FRAMES, 1)', '$call_descriptors_valid(S_entered)']
    seek('S_pending', 'S_entered', 11)
    checks += [
        'S_pending.TODO = (MOD_NAN_PENDING pintegeroperation pintegerconversion 0 n_second) :: ptask_caller*',
        'S_pending.CURRENT = eps', 'S_pending.FRAMES = eps',
        'S_pending.STORE[n_x] = DEFINED (PINT 99)',
        'S_pending.STORE[n_y] = DEFINED (PINT 0)',
        'S_pending.STORE[n_v] = DEFINED (PINT 100)',
        'S_pending.STORE[n_calls] = DEFINED (PINT 1)',
        '$integer_pointer_value(S_pending, pintegeroperation.LEFTPOINTER) = (PINT 99)',
        '$integer_pointer_value(S_pending, pintegeroperation.RIGHTPOINTER) = (PINT 0)',
        '$mod_nan_pending_source(S_pending, pintegeroperation, pintegerconversion)',
        '$mod_nan_pending_valid(S_pending, pintegeroperation, pintegerconversion, 0, n_second)',
        '~$mod_nan_pending_valid(S_pending, pintegeroperation, pintegerconversion, 2, n_second)',
        '~$error_handler_eligible(S_pending, 8192)',
        'S_pending.ERRORHANDLER.CALLBACK = S_entry.ERRORHANDLER.CALLBACK',
        '$task_nodes(MOD_NAN_PENDING pintegeroperation pintegerconversion 0 n_second) = [HOBJECT n_second]',
        '$heap_owners($heap_prune($heap_graph(S_pending)), HOBJECT n_second) = 2',
        '$heap_owners($heap_prune($heap_graph(S_pending)), HCELL n_x) = 1',
        '$heap_owners($heap_prune($heap_graph(S_pending)), HCELL n_y) = 1',
        '$throwable_live(S_pending, n_second)',
        '$throwable_previous_id(S_pending, n_second) = eps',
        '$throwable_field(S_pending, n_second, "line") = PINT 20',
        '$mod_nan_diagnostics(S_pending.EVENTS, "Warning") = 0',
        '$mod_nan_diagnostics(S_pending.EVENTS, "Deprecated") = 0',
        'S_pending.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
        'pevent_precision = DIAGNOSTIC "Deprecated" ($ptascii("Implicit conversion from float NAN to int loses precision")) 25',
        'PhpStep: S_pending ~> S_default_raw',
        'S_default_raw = $error_dispatch(S_pending, 8192, $ptascii("Implicit conversion from float NAN to int loses precision"), 25, pevent_precision, MOD_NAN_PENDING pintegeroperation pintegerconversion 1 n_second)',
        'S_default_raw.EVENTS = S_pending.EVENTS ++ $display_events(S_pending, $event_source(S_pending, pevent_precision))',
        'S_default_raw.STORE = S_pending.STORE', 'S_default_raw.ENV = S_pending.ENV',
        'S_default_raw.REFCELLS = S_pending.REFCELLS',
        'S_default_raw.RESULT = S_pending.RESULT',
        'S_default_raw.ALLOCATIONS = S_pending.ALLOCATIONS',
        'S_default_raw.STRINGDATA = S_pending.STRINGDATA',
        'S_default_raw.OBJECTS = S_pending.OBJECTS',
        'S_default_raw.ARRAYS = S_pending.ARRAYS',
        'S_default_raw.ERRORFATALTRACE = eps',
    ]
    step('S_reported', 'S_pending')
    checks += [
        'S_reported = S_default_raw', '$mod_nan_frontier(S_reported, 12)',
        '$mod_nan_pending_valid(S_reported, pintegeroperation, pintegerconversion, 1, n_second)',
        '$mod_nan_diagnostics(S_reported.EVENTS, "Warning") = 0',
        '$mod_nan_diagnostics(S_reported.EVENTS, "Deprecated") = 1',
        '$heap_owners($heap_prune($heap_graph(S_reported)), HOBJECT n_second) = 2',
        '$call_descriptors_valid(S_reported)', '$heap_valid($heap_graph(S_reported))',
        'PhpStep: S_reported ~> S_throw_raw',
        'S_throw_raw = S_reported[.TODO = (THROW_SEARCH n_second) :: ptask_caller*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_throw', 'S_reported')
    checks += [
        'S_throw = S_throw_raw', '$mod_nan_frontier(S_throw, 13)',
        '~$mod_nan_tasks(S_throw.TODO)',
        'S_throw.STORE[n_x] = DEFINED (PINT 99)',
        'S_throw.STORE[n_y] = DEFINED (PINT 0)',
        'S_throw.STORE[n_v] = DEFINED (PINT 100)',
        'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
        'S_throw.OBJECTS = S_pending.OBJECTS', 'S_throw.ARRAYS = S_pending.ARRAYS',
        '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
        '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
        'S_done = $drive_steps(S_throw, 4000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_x] = DEFINED (PINT 8)',
        'S_done.STORE[n_y] = DEFINED (PINT 9)',
        'S_done.STORE[n_v] = DEFINED (PINT 100)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        '$throwable_previous_id(S_done, n_second) = eps',
        '$mod_nan_diagnostics(S_done.EVENTS, "Warning") = 0',
        '$mod_nan_diagnostics(S_done.EVENTS, "Deprecated") = 1',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_pending, 0) = S_pending[.COMPLETION = BUDGET]',
        '$drive_steps(S_reported, 0) = S_reported[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
