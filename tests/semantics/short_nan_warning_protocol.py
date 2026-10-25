#!/usr/bin/env python3
"""Live NaN LEFT truth controls whether the AND right expression executes."""
import base64
import json

import short_nan_warning_cases as cases
import integer_operator_warning_protocol as shared

CASES = ('short-nan-warning-symbolic-and-skip',)
HELPERS = shared.HELPERS + r'''
dec $short_nan_task(ptask) : bool
def $short_nan_task(SHORT_NAN_WARNING pboolnotnanwarning ptask_original n) = true
def $short_nan_task(SHORT_RESULT b expression z_left z_right) = true
def $short_nan_task(TRUTH_RESULT false z) = true
def $short_nan_task(ERROR_HANDLER_INVOKE perrorcall) = $short_nan_task(perrorcall.RESUME)
def $short_nan_task(ERROR_HANDLER_RESULT perrorcall) = $short_nan_task(perrorcall.RESUME)
def $short_nan_task(ERROR_HANDLER_CLEAN perrorcall) = $short_nan_task(perrorcall.RESUME)
def $short_nan_task(ptask) = false -- otherwise
dec $short_nan_tasks(ptask*) : bool
def $short_nan_tasks(eps) = false
def $short_nan_tasks(ptask :: ptask_tail*) = ($short_nan_task(ptask) \/ $short_nan_tasks(ptask_tail*))
dec $short_nan_handler_frame(pframe) : bool
def $short_nan_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = SHORT_NAN_WARNING pboolnotnanwarning ptask_original 1
  -- if perrorcall.TARGET =/= eps
def $short_nan_handler_frame(pframe) = false -- otherwise
dec $short_nan_entered(pframe*) : bool
def $short_nan_entered(eps) = false
def $short_nan_entered(pframe :: pframe_tail*) = ($short_nan_handler_frame(pframe) \/ $short_nan_entered(pframe_tail*))
dec $short_nan_origin(pstate) : bool
def $short_nan_origin(S) = true
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (pcnode)
  -- if $truth_short_source(pcnode) =/= eps
def $short_nan_origin(S) = false -- otherwise
dec $short_nan_frontier(pstate, nat) : bool
def $short_nan_frontier(S, 0) = ($short_nan_plan(S) =/= eps)
def $short_nan_frontier(S, 1) = true
  -- if S.TODO = (SHORT_NAN_WARNING pboolnotnanwarning ptask_original 0) :: ptask_tail*
def $short_nan_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = SHORT_NAN_WARNING pboolnotnanwarning ptask_original 1
  -- if perrorcall.TARGET = eps
def $short_nan_frontier(S, 3) = (S.CURRENT =/= eps /\ $short_nan_entered(S.FRAMES))
def $short_nan_frontier(S, 4) = true
  -- if S.TODO = (SHORT_NAN_WARNING pboolnotnanwarning ptask_original 1) :: ptask_tail*
def $short_nan_frontier(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps /\ $short_nan_origin(S)
  -- if S.TODO = (SHORT_RESULT b_or expression z_left z_right) :: ptask_tail*
  -- if S.RESULT = KNOWN (PBOOL b)
def $short_nan_frontier(S, 6) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps /\ $short_nan_origin(S)
  -- if S.RESULT = KNOWN (PBOOL b)
  -- if ~$short_nan_tasks(S.TODO)
def $short_nan_frontier(S, 7) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if ~$short_nan_tasks(S.TODO)
def $short_nan_frontier(S, 8) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("k")
def $short_nan_frontier(S, 9) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps /\ $short_nan_origin(S)
  -- if S.TODO = (TRUTH_RESULT false z) :: ptask_tail*
  -- if S.RESULT = KNOWN (PBOOL b)
def $short_nan_frontier(S, n) = false -- otherwise
dec $short_nan_seek(pstate, nat, nat) : pstate
def $short_nan_seek(S, n_stage, n) = S -- if $short_nan_frontier(S, n_stage)
def $short_nan_seek(S, n_stage, n) = S
  -- if ~$short_nan_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $short_nan_seek(S, n_stage, n) = S
  -- if ~$short_nan_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $short_nan_seek(S, n_stage, n) = $short_nan_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$short_nan_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
dec $short_nan_diagnostic(pevent, text) : nat
def $short_nan_diagnostic(DIAGNOSTIC text n_message* z, text) = 1
def $short_nan_diagnostic(DIAGNOSTIC_SOURCE n_source text n_message* z, text) = 1
def $short_nan_diagnostic(DIAGNOSTIC_STACK text n_message* z n_trace*, text) = 1
def $short_nan_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n_message* z n_trace*, text) = 1
def $short_nan_diagnostic(pevent, text) = 0 -- otherwise
dec $short_nan_diagnostics(pevent*, text) : nat
def $short_nan_diagnostics(eps, text) = 0
def $short_nan_diagnostics(pevent :: pevent_tail*, text) = $($short_nan_diagnostic(pevent, text) + $short_nan_diagnostics(pevent_tail*, text))
'''

def conditions(name, program, path, stdout):
    assert name in CASES
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $short_nan_seek({before}, {stage}, 3000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$short_nan_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$short_nan_plan(S_entry) = ((pboolnotnanwarning, ptask_original))',
        'ptask_original = SHORT_RESULT false expression_right 24 25',
        'S_entry.TODO = ptask_original :: ptask_tail*',
        'pboolnotnanwarning.LINE = 24', 'pboolnotnanwarning.INPUT = VARIABLE ($ptascii("x")) 24',
        'S_entry.RESULT = pboolnotnanwarning.INPUT',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)', 'pboolnotnanwarning.CELL = n_x',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("rhs")) = (n_rhs)',
        'S_entry.STORE[n_x] = DEFINED (PFLOAT pboolnotnanwarning.BITS)',
        '$fparts_nan($float_decode(pboolnotnanwarning.BITS))',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', 'S_entry.STORE[n_rhs] = DEFINED (PINT 0)',
        '$short_nan_source(S_entry, pboolnotnanwarning, ptask_original)',
        '$integer_operand_source(S_entry, pboolnotnanwarning.SITE, [PCFIELD 0], pboolnotnanwarning.INPUT)',
        '$boolnot_nan_ready(S_entry, pboolnotnanwarning) = (pboolnotnanwarning.BITS)',
        '$boolnot_nan_snapshot(S_entry, pboolnotnanwarning)',
        '~(n_x <- S_entry.REFCELLS)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        '$boolnot_nan_plan(S_entry) = eps', '$boolnot_reference_nan_plan(S_entry) = eps',
        '~$boolnot_nan_source(S_entry, pboolnotnanwarning)',
        'S_entry.EVENTS = eps', '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$short_nan_plan(S_entry[.ORIGIN = eps]) = eps',
        '$short_nan_plan(S_entry[.CODE = eps]) = eps',
        '$short_nan_plan(S_entry[.RESULT = KNOWN (PFLOAT pboolnotnanwarning.BITS)]) = eps',
        '$short_nan_plan(S_entry[.TODO = [TRUTH_RESULT false 24]]) = eps',
        '$short_nan_plan(S_entry[.ERRORHANDLER.CALLBACK = eps]) = eps',
        '$short_nan_plan(S_entry[.ERRORHANDLER.LEVELS = 8192]) = eps',
        '$short_nan_plan(S_entry[.REFCELLS = [n_x]]) = eps',
        '$short_nan_plan(S_entry[.STORE[n_x] = DEFINED (PFLOAT 0)]) = eps',
        '$short_nan_plan(S_entry[.ALLOCATIONS = eps]) = eps',
        '~$short_nan_source(S_entry, pboolnotnanwarning, SHORT_RESULT true expression_right 24 25)',
        '~$short_nan_source(S_entry, pboolnotnanwarning, SHORT_RESULT false expression_right 24 24)',
        '~$short_nan_source(S_entry, pboolnotnanwarning, TRUTH_RESULT false 24)',
        '~$short_nan_source(S_entry, pboolnotnanwarning[.LINE = 25], ptask_original)',
        '~$short_nan_source(S_entry, pboolnotnanwarning[.INPUT = VARIABLE ($ptascii("rhs")) 24], ptask_original)',
        '~$short_nan_source(S_entry, pboolnotnanwarning[.BITS = 0], ptask_original)',
        '~$short_nan_source(S_entry, pboolnotnanwarning[.CELL = |S_entry.STORE|], ptask_original)',
        'PhpStep: S_entry ~> S_capture_atomic',
        'S_capture_atomic = S_entry[.TODO = (SHORT_NAN_WARNING pboolnotnanwarning ptask_original 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture = S_capture_atomic', '$short_nan_frontier(S_capture, 1)',
        '$short_nan_warning_valid(S_capture, pboolnotnanwarning, ptask_original, 0)',
        '$short_nan_warning_valid(S_capture, pboolnotnanwarning, ptask_original, 1)',
        '~$short_nan_warning_valid(S_capture, pboolnotnanwarning, ptask_original, 2)',
        '$task_nodes(SHORT_NAN_WARNING pboolnotnanwarning ptask_original 0) = eps',
        '$task_nodes(ptask_original) = eps',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_x) = 1',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        '$short_nan_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = SHORT_NAN_WARNING pboolnotnanwarning ptask_original 1',
        'perrorcall.TARGET = eps', 'perrorcall.SITE = pboolnotnanwarning.SITE',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = 24',
        'perrorcall.MESSAGE = $ptascii("unexpected NAN value was coerced to bool")',
        'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE 24',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 8192])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = 25])',
        'S_dispatch.EVENTS = eps', '$call_descriptors_valid(S_dispatch)',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += [
        '$short_nan_entered(S_entered.FRAMES)', 'S_entered.CURRENT =/= eps',
        'S_entered.FRAMES = pframe :: pframe_tail*', '$short_nan_handler_frame(pframe)',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_saved*',
        'perrorcall_entered.TARGET =/= eps',
        'perrorcall_entered.RESUME = SHORT_NAN_WARNING pboolnotnanwarning ptask_original 1',
        '$call_descriptors_valid(S_entered)',
    ]
    seek('S_return', 'S_entered', 4)
    checks += [
        'S_return.TODO = (SHORT_NAN_WARNING pboolnotnanwarning ptask_original 1) :: ptask_tail*',
        '$lookup(S_return.ENV, $ptascii("x")) = (n_x)',
        'S_return.STORE[n_x] = DEFINED (PFLOAT 0)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)',
        'S_return.STORE[n_calls] = DEFINED (PINT 1)', 'S_return.STORE[n_rhs] = DEFINED (PINT 0)',
        '$short_nan_source(S_return, pboolnotnanwarning, ptask_original)',
        '$boolnot_nan_ready(S_return, pboolnotnanwarning) = (0)',
        '~$boolnot_nan_snapshot(S_return, pboolnotnanwarning)',
        '~$short_nan_warning_valid(S_return, pboolnotnanwarning, ptask_original, 0)',
        '$short_nan_warning_valid(S_return, pboolnotnanwarning, ptask_original, 1)',
        '~$error_call_valid(S_return, perrorcall)', '$error_call_valid(S_return, perrorcall_entered)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_x) = 1',
        '$short_nan_diagnostics(S_return.EVENTS, "Warning") = 1',
        '$short_nan_diagnostics(S_return.EVENTS, "Deprecated") = 0',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'PhpStep: S_return ~> S_bool_atomic',
        'S_bool_atomic = S_return[.TODO = ptask_original :: ptask_tail*][.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        # Derived live truth/no-rewarning/refusal controls do not add native cases.
        'S_truthy = S_return[.STORE[n_x] = DEFINED (PFLOAT 4607182418800017408)]',
        'PhpStep: S_truthy ~> S_truthy_bool',
        'S_truthy_bool = S_truthy[.TODO = ptask_original :: ptask_tail*][.RESULT = KNOWN (PBOOL true)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_nan = S_return[.STORE[n_x] = DEFINED (PFLOAT pboolnotnanwarning.BITS)]',
        'PhpStep: S_nan ~> S_nan_bool',
        'S_nan_bool = S_nan[.TODO = ptask_original :: ptask_tail*][.RESULT = KNOWN (PBOOL true)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_nan_bool.EVENTS = S_return.EVENTS',
        'S_retyped = S_return[.STORE[n_x] = DEFINED (PINT 0)]',
        'PhpStep: S_retyped ~> S_boundary',
        'S_boundary = S_retyped[.COMPLETION = UNSUPPORTED "short-circuit NaN changed CV representation"]',
    ]
    step('S_bool', 'S_return')
    checks += [
        'S_bool = S_bool_atomic', '$short_nan_frontier(S_bool, 5)',
        'S_bool.STORE = S_return.STORE', 'S_bool.ENV = S_return.ENV',
        'S_bool.ALLOCATIONS = S_return.ALLOCATIONS', 'S_bool.EVENTS = S_return.EVENTS',
        '$short_nan_plan(S_bool) = eps', '$call_descriptors_valid(S_bool)',
        'PhpStep: S_bool ~> S_skip_atomic',
        'S_skip_atomic.TODO = ptask_tail*', 'S_skip_atomic.RESULT = KNOWN (PBOOL false)',
        'S_skip_atomic.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_skip_atomic.STORE = S_bool.STORE', 'S_skip_atomic.EVENTS = S_bool.EVENTS',
    ]
    step('S_skip', 'S_bool')
    checks += [
        '$short_nan_frontier(S_skip, 6)', 'S_skip.TODO = ptask_tail*',
        'S_skip.RESULT = KNOWN (PBOOL false)',
        'S_skip.STORE = S_return.STORE', 'S_skip.ENV = S_return.ENV',
        'S_skip.STORE[n_v] = DEFINED (PINT 100)', 'S_skip.STORE[n_rhs] = DEFINED (PINT 0)',
        'S_skip.EVENTS = S_return.EVENTS', '$call_descriptors_valid(S_skip)', '$heap_valid($heap_graph(S_skip))',
        'S_done = $drive_steps(S_skip, 3000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("x")) = (n_x)', 'S_done.STORE[n_x] = DEFINED (PINT 8)',
        'S_done.STORE[n_v] = DEFINED (PBOOL false)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)', 'S_done.STORE[n_rhs] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_x) = 1',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$short_nan_diagnostics(S_done.EVENTS, "Warning") = 1',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
        '$drive_steps(S_bool, 0) = S_bool[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
