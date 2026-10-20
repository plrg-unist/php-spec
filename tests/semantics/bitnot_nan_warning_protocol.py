#!/usr/bin/env python3
"""Reached NaN range Warning, pending precision notice and supplied Exception."""
import base64
import json

import bitnot_nan_warning_cases as cases
import bitnot_warning_protocol as shared

CASES = ('bitnot-nan-pending-ineligible-precision',)
HELPERS = shared.HELPERS + r'''
dec $bitnot_nan_task(ptask) : bool
def $bitnot_nan_task(BITNOT_NAN_WARNING pbitnotwarning n n_pending?) = true
def $bitnot_nan_task(ERROR_HANDLER_INVOKE perrorcall) = $bitnot_nan_task(perrorcall.RESUME)
def $bitnot_nan_task(ERROR_HANDLER_RESULT perrorcall) = $bitnot_nan_task(perrorcall.RESUME)
def $bitnot_nan_task(ERROR_HANDLER_CLEAN perrorcall) = $bitnot_nan_task(perrorcall.RESUME)
def $bitnot_nan_task(ptask) = false -- otherwise
dec $bitnot_nan_tasks(ptask*) : bool
def $bitnot_nan_tasks(eps) = false
def $bitnot_nan_tasks(ptask :: ptask_tail*) = ($bitnot_nan_task(ptask) \/ $bitnot_nan_tasks(ptask_tail*))
dec $bitnot_nan_handler_frame(pframe, nat) : bool
def $bitnot_nan_handler_frame(pframe, n_phase) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = BITNOT_NAN_WARNING pbitnotwarning n eps
  -- if n = $(n_phase + 1)
  -- if perrorcall.TARGET =/= eps
def $bitnot_nan_handler_frame(pframe, n_phase) = false -- otherwise
dec $bitnot_nan_entered(pframe*, nat) : bool
def $bitnot_nan_entered(eps, n_phase) = false
def $bitnot_nan_entered(pframe :: pframe_tail*, n_phase) = ($bitnot_nan_handler_frame(pframe, n_phase) \/ $bitnot_nan_entered(pframe_tail*, n_phase))
dec $bitnot_nan_frontier(pstate, nat) : bool
def $bitnot_nan_frontier(S, 0) = ($bitnot_nan_warning_plan(S) =/= eps)
def $bitnot_nan_frontier(S, 1) = true
  -- if S.TODO = (BITNOT_NAN_WARNING pbitnotwarning 0 eps) :: ptask_tail*
def $bitnot_nan_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = BITNOT_NAN_WARNING pbitnotwarning 1 eps
  -- if perrorcall.TARGET = eps
def $bitnot_nan_frontier(S, 3) = (S.CURRENT =/= eps /\ $bitnot_nan_entered(S.FRAMES, 0))
def $bitnot_nan_frontier(S, 4) = true
  -- if S.TODO = (BITNOT_NAN_WARNING pbitnotwarning 1 eps) :: ptask_tail*
def $bitnot_nan_frontier(S, 5) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = BITNOT_NAN_WARNING pbitnotwarning 2 eps
  -- if perrorcall.TARGET = eps
def $bitnot_nan_frontier(S, 6) = (S.CURRENT =/= eps /\ $bitnot_nan_entered(S.FRAMES, 1))
def $bitnot_nan_frontier(S, 7) = true
  -- if S.TODO = (BITNOT_NAN_WARNING pbitnotwarning 2 eps) :: ptask_tail*
def $bitnot_nan_frontier(S, 8) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprBitwiseNot expression metadata)
  -- if S.RESULT = KNOWN (PINT i)
  -- if ~$bitnot_nan_tasks(S.TODO)
def $bitnot_nan_frontier(S, 9) = true
  -- if S.TODO = (BITNOT_NAN_WARNING pbitnotwarning 1 (n_exception)) :: ptask_tail*
def $bitnot_nan_frontier(S, 10) = true
  -- if S.TODO = (BITNOT_NAN_WARNING pbitnotwarning 2 (n_exception)) :: ptask_tail*
def $bitnot_nan_frontier(S, 11) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n_exception) :: ptask_tail*
  -- if ~$bitnot_nan_tasks(S.TODO)
def $bitnot_nan_frontier(S, n) = false -- otherwise
dec $bitnot_nan_seek(pstate, nat, nat) : pstate
def $bitnot_nan_seek(S, n_stage, n) = S -- if $bitnot_nan_frontier(S, n_stage)
def $bitnot_nan_seek(S, n_stage, n) = S
  -- if ~$bitnot_nan_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $bitnot_nan_seek(S, n_stage, n) = S
  -- if ~$bitnot_nan_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $bitnot_nan_seek(S, n_stage, n) = $bitnot_nan_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$bitnot_nan_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
dec $bitnot_nan_diagnostic(pevent, text) : nat
def $bitnot_nan_diagnostic(DIAGNOSTIC text n_message* z, text) = 1
def $bitnot_nan_diagnostic(DIAGNOSTIC_SOURCE n_source text n_message* z, text) = 1
def $bitnot_nan_diagnostic(DIAGNOSTIC_STACK text n_message* z n_trace*, text) = 1
def $bitnot_nan_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n_message* z n_trace*, text) = 1
def $bitnot_nan_diagnostic(pevent, text) = 0 -- otherwise
dec $bitnot_nan_diagnostics(pevent*, text) : nat
def $bitnot_nan_diagnostics(eps, text) = 0
def $bitnot_nan_diagnostics(pevent :: pevent_tail*, text) = $($bitnot_nan_diagnostic(pevent, text) + $bitnot_nan_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET']
    def seek(state, before, stage):
        checks.extend([f'{state}_found = $bitnot_nan_seek({before}, {stage}, 3000)',
                       f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
                       f'{state} = {state}_found[.COMPLETION = NORMAL]', f'$bitnot_nan_frontier({state}, {stage})'])
    def step(state, before):
        checks.extend([f'{state}_budget = $drive_steps({before}, 1)', f'{state}_budget.COMPLETION = BUDGET',
                       f'{state} = {state}_budget[.COMPLETION = NORMAL]'])
    seek('S_entry', 'S_initial', 0)
    checks += [
        '$bitnot_nan_warning_plan(S_entry) = (pbitnotwarning)', '$bitnot_warning_plan(S_entry) = eps',
        '$bitnot_nan_source_valid(S_entry, pbitnotwarning)', '$bitnot_snapshot(S_entry, pbitnotwarning)',
        'pbitnotwarning.LINE = 25', 'pbitnotwarning.INPUT = VARIABLE ($ptascii("x")) 25',
        'pbitnotwarning.BITS = 9221120237041090560', 'pbitnotwarning.VALUE = 0',
        '$float_long(pbitnotwarning.BITS, true) = (0, [RANGEWARNING, PRECISIONLOSS])',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)', '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)', '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
        'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        'S_entry.STORE[n_x] = DEFINED (PFLOAT pbitnotwarning.BITS)', 'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', '~(n_x <- S_entry.REFCELLS)',
        '$integer_pointer_select(S_entry, pbitnotwarning.INPUT) = (INTEGER_CV ($ptascii("x")))',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        'S_entry.ERRORHANDLER.LEVELS = 2', '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$bitnot_nan_warning_plan(S_entry[.ORIGIN = eps]) = eps',
        '$bitnot_nan_warning_plan(S_entry[.CODE = eps]) = eps',
        '$bitnot_nan_warning_plan(S_entry[.RESULT = KNOWN PNULL]) = eps',
        '$bitnot_nan_warning_plan(S_entry[.STORE[n_x] = UNDEFINED]) = eps',
        '$bitnot_nan_warning_plan(S_entry[.REFCELLS = [n_x]]) = eps',
        '$bitnot_nan_warning_plan(S_entry[.ERRORHANDLER.CALLBACK = eps]) = eps',
        '$bitnot_nan_warning_plan(S_entry[.ERRORHANDLER.LEVELS = 8192]) = eps',
        '~$bitnot_nan_source_valid(S_entry, pbitnotwarning[.LINE = 24])',
        '~$bitnot_nan_source_valid(S_entry, pbitnotwarning[.INPUT = VARIABLE ($ptascii("v")) 25])',
        '~$bitnot_nan_source_valid(S_entry, pbitnotwarning[.BITS = 18446744073709551616])',
        '~$bitnot_nan_source_valid(S_entry, pbitnotwarning[.VALUE = 1])',
        'pbitnotwarning_finite = pbitnotwarning[.BITS = 4612811918334230528][.VALUE = 2]',
        '~$bitnot_nan_source_valid(S_entry, pbitnotwarning_finite)',
        '$bitnot_source_valid(S_entry, pbitnotwarning_finite)',
        '~$bitnot_nan_warning_valid(S_entry, pbitnotwarning, 3, eps)',
        '~$bitnot_nan_warning_valid(S_entry, pbitnotwarning, 0, (n_second))',
        'S_entry.TODO = ptask_old :: ptask_tail*', 'PhpStep: S_entry ~> S_begin_raw',
        'S_begin_raw = S_entry[.TODO = (BITNOT_NAN_WARNING pbitnotwarning 0 eps) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_capture', 'S_entry')
    checks += ['S_capture = S_begin_raw', '$bitnot_nan_frontier(S_capture, 1)',
               '$bitnot_nan_warning_valid(S_capture, pbitnotwarning, 0, eps)',
               '$task_nodes(BITNOT_NAN_WARNING pbitnotwarning 0 eps) = eps',
               '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))']
    step('S_dispatch', 'S_capture')
    checks += ['S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
               '$bitnot_nan_frontier(S_dispatch, 2)', 'perrorcall.RESUME = BITNOT_NAN_WARNING pbitnotwarning 1 eps',
               'perrorcall.TARGET = eps', 'perrorcall.LEVEL = 2', 'perrorcall.LINE = 25',
               'perrorcall.MESSAGE = $ptascii("The float NAN is not representable as an int, cast occurred")',
               '$error_call_valid(S_dispatch, perrorcall)', '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 8192])',
               '~$error_call_valid(S_dispatch, perrorcall[.LINE = 24])',
               '~$error_call_valid(S_dispatch, perrorcall[.RESUME = BITNOT_NAN_WARNING pbitnotwarning_finite 1 eps])',
               '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))']
    seek('S_entered', 'S_dispatch', 3)
    checks += ['$bitnot_nan_entered(S_entered.FRAMES, 0)', '$call_descriptors_valid(S_entered)']
    seek('S_pending', 'S_entered', 9)
    checks += ['S_pending.TODO = (BITNOT_NAN_WARNING pbitnotwarning 1 (n_second)) :: ptask_caller*',
               'S_pending.CURRENT = eps', 'S_pending.FRAMES = eps',
               'S_pending.STORE[n_x] = DEFINED (PINT 99)', 'S_pending.STORE[n_v] = DEFINED (PINT 100)',
               'S_pending.STORE[n_calls] = DEFINED (PINT 1)',
               '$lookup(S_pending.ENV, $ptascii("x")) = (n_x)',
               '~$bitnot_snapshot(S_pending, pbitnotwarning)',
               '$bitnot_nan_warning_valid(S_pending, pbitnotwarning, 1, (n_second))',
               '~$error_handler_eligible(S_pending, 8192)', 'S_pending.ERRORHANDLER.CALLBACK = S_entry.ERRORHANDLER.CALLBACK',
               '$task_nodes(BITNOT_NAN_WARNING pbitnotwarning 1 (n_second)) = [HOBJECT n_second]',
               '$heap_owners($heap_prune($heap_graph(S_pending)), HOBJECT n_second) = 2',
               '$throwable_live(S_pending, n_second)', '$throwable_previous_id(S_pending, n_second) = eps',
               '$throwable_field(S_pending, n_second, "line") = PINT 20',
               '$bitnot_nan_diagnostics(S_pending.EVENTS, "Warning") = 0',
               '$bitnot_nan_diagnostics(S_pending.EVENTS, "Deprecated") = 0',
               'S_pending.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
               '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
               'pevent_precision = DIAGNOSTIC "Deprecated" ($ptascii("Implicit conversion from float NAN to int loses precision")) 25',
               'PhpStep: S_pending ~> S_default_raw',
               'S_default_raw = $error_dispatch(S_pending, 8192, $ptascii("Implicit conversion from float NAN to int loses precision"), 25, pevent_precision, BITNOT_NAN_WARNING pbitnotwarning 2 (n_second))',
               'S_default_raw.EVENTS = S_pending.EVENTS ++ $display_events(S_pending, $event_source(S_pending, pevent_precision))',
               'S_default_raw.STORE = S_pending.STORE', 'S_default_raw.ENV = S_pending.ENV',
               'S_default_raw.REFCELLS = S_pending.REFCELLS', 'S_default_raw.RESULT = S_pending.RESULT',
               'S_default_raw.ALLOCATIONS = S_pending.ALLOCATIONS', 'S_default_raw.STRINGDATA = S_pending.STRINGDATA']
    step('S_reported', 'S_pending')
    checks += ['S_reported = S_default_raw', '$bitnot_nan_frontier(S_reported, 10)',
               '$bitnot_nan_warning_valid(S_reported, pbitnotwarning, 2, (n_second))',
               '$bitnot_nan_diagnostics(S_reported.EVENTS, "Warning") = 0',
               '$bitnot_nan_diagnostics(S_reported.EVENTS, "Deprecated") = 1',
               '$heap_owners($heap_prune($heap_graph(S_reported)), HOBJECT n_second) = 2',
               '$call_descriptors_valid(S_reported)', '$heap_valid($heap_graph(S_reported))',
               'PhpStep: S_reported ~> S_throw_raw',
               'S_throw_raw = S_reported[.TODO = (THROW_SEARCH n_second) :: ptask_caller*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]']
    step('S_throw', 'S_reported')
    checks += ['S_throw = S_throw_raw', '$bitnot_nan_frontier(S_throw, 11)',
               '~$bitnot_nan_tasks(S_throw.TODO)', 'S_throw.STORE[n_x] = DEFINED (PINT 99)',
               'S_throw.STORE[n_v] = DEFINED (PINT 100)', 'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
               '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]',
               '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
               '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
               'S_done = $drive_steps(S_throw, 3000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
               'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
               'S_done.STORE[n_x] = DEFINED (PINT 99)', 'S_done.STORE[n_v] = DEFINED (PINT 100)',
               'S_done.STORE[n_calls] = DEFINED (PINT 1)',
               '$throwable_previous_id(S_done, n_second) = eps',
               '$bitnot_nan_diagnostics(S_done.EVENTS, "Warning") = 0',
               '$bitnot_nan_diagnostics(S_done.EVENTS, "Deprecated") = 1',
               '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
               '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
               '$drive_steps(S_pending, 0) = S_pending[.COMPLETION = BUDGET]',
               '$drive_steps(S_reported, 0) = S_reported[.COMPLETION = BUDGET]']
    assert len(checks) == len(set(checks))
    return checks
