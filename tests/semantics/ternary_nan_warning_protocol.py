#!/usr/bin/env python3
"""A shorthand NaN condition delivers its post-Warning live float value."""
import base64
import json

import ternary_nan_warning_cases as cases
import integer_operator_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $ternary_nan_task(ptask) : bool
def $ternary_nan_task(TERNARY_NAN_WARNING pboolnotnanwarning ptask_original n) = true
def $ternary_nan_task(SELECT_VALUE phpType5 expression z_cond z_true z_false) = true
def $ternary_nan_task(VALUE_COPY z) = true
def $ternary_nan_task(ERROR_HANDLER_INVOKE perrorcall) = $ternary_nan_task(perrorcall.RESUME)
def $ternary_nan_task(ERROR_HANDLER_RESULT perrorcall) = $ternary_nan_task(perrorcall.RESUME)
def $ternary_nan_task(ERROR_HANDLER_CLEAN perrorcall) = $ternary_nan_task(perrorcall.RESUME)
def $ternary_nan_task(ptask) = false -- otherwise
dec $ternary_nan_tasks(ptask*) : bool
def $ternary_nan_tasks(eps) = false
def $ternary_nan_tasks(ptask :: ptask_tail*) = ($ternary_nan_task(ptask) \/ $ternary_nan_tasks(ptask_tail*))
dec $ternary_nan_handler_frame(pframe) : bool
def $ternary_nan_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = TERNARY_NAN_WARNING pboolnotnanwarning ptask_original 1
  -- if perrorcall.TARGET =/= eps
def $ternary_nan_handler_frame(pframe) = false -- otherwise
dec $ternary_nan_entered(pframe*) : bool
def $ternary_nan_entered(eps) = false
def $ternary_nan_entered(pframe :: pframe_tail*) = ($ternary_nan_handler_frame(pframe) \/ $ternary_nan_entered(pframe_tail*))
dec $ternary_nan_origin(pstate) : bool
def $ternary_nan_origin(S) = true
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprTernary expression_cond ABSENT expression_false metadata)
def $ternary_nan_origin(S) = false -- otherwise
dec $ternary_nan_frontier(pstate, nat) : bool
def $ternary_nan_frontier(S, 0) = ($ternary_nan_plan(S) =/= eps)
def $ternary_nan_frontier(S, 1) = true
  -- if S.TODO = (TERNARY_NAN_WARNING pboolnotnanwarning ptask_original 0) :: ptask_tail*
def $ternary_nan_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = TERNARY_NAN_WARNING pboolnotnanwarning ptask_original 1
  -- if perrorcall.TARGET = eps
def $ternary_nan_frontier(S, 3) = (S.CURRENT =/= eps /\ $ternary_nan_entered(S.FRAMES))
def $ternary_nan_frontier(S, 4) = true
  -- if S.TODO = (TERNARY_NAN_WARNING pboolnotnanwarning ptask_original 1) :: ptask_tail*
def $ternary_nan_frontier(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps /\ $ternary_nan_origin(S)
  -- if S.RESULT = KNOWN pvalue
  -- if ~$ternary_nan_tasks(S.TODO)
def $ternary_nan_frontier(S, 6) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprTernary expression_cond ABSENT expression_false metadata)
  -- if S.TODO = ptask_at :: (VALUE_COPY z) :: ptask_tail*
  -- if ptask_at = $at_task($origin_child((porigin), [PCFIELD 2]), EVAL expression_false)
  -- if S.RESULT = KNOWN PNULL
def $ternary_nan_frontier(S, 7) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if ~$ternary_nan_tasks(S.TODO)
def $ternary_nan_frontier(S, 8) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("k")
def $ternary_nan_frontier(S, 9) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps /\ $ternary_nan_origin(S)
  -- if S.TODO = (VALUE_COPY z) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue
def $ternary_nan_frontier(S, n) = false -- otherwise
dec $ternary_nan_seek(pstate, nat, nat) : pstate
def $ternary_nan_seek(S, n_stage, n) = S -- if $ternary_nan_frontier(S, n_stage)
def $ternary_nan_seek(S, n_stage, n) = S
  -- if ~$ternary_nan_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $ternary_nan_seek(S, n_stage, n) = S
  -- if ~$ternary_nan_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $ternary_nan_seek(S, n_stage, n) = $ternary_nan_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$ternary_nan_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
dec $ternary_nan_diagnostic(pevent, text) : nat
def $ternary_nan_diagnostic(DIAGNOSTIC text n_message* z, text) = 1
def $ternary_nan_diagnostic(DIAGNOSTIC_SOURCE n_source text n_message* z, text) = 1
def $ternary_nan_diagnostic(DIAGNOSTIC_STACK text n_message* z n_trace*, text) = 1
def $ternary_nan_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n_message* z n_trace*, text) = 1
def $ternary_nan_diagnostic(pevent, text) = 0 -- otherwise
dec $ternary_nan_diagnostics(pevent*, text) : nat
def $ternary_nan_diagnostics(eps, text) = 0
def $ternary_nan_diagnostics(pevent :: pevent_tail*, text) = $($ternary_nan_diagnostic(pevent, text) + $ternary_nan_diagnostics(pevent_tail*, text))
'''

def conditions(name, program, path, stdout):
    assert name in CASES
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $ternary_nan_seek({before}, {stage}, 3000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$ternary_nan_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$ternary_nan_plan(S_entry) = ((pboolnotnanwarning, ptask_original))',
        'ptask_original = SELECT_VALUE ABSENT expression_false 24 0 25',
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
        '$ternary_nan_source(S_entry, pboolnotnanwarning, ptask_original)',
        '$integer_operand_source(S_entry, pboolnotnanwarning.SITE, [PCFIELD 0], pboolnotnanwarning.INPUT)',
        '$boolnot_nan_ready(S_entry, pboolnotnanwarning) = (pboolnotnanwarning.BITS)',
        '$boolnot_nan_snapshot(S_entry, pboolnotnanwarning)',
        '~(n_x <- S_entry.REFCELLS)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        '$short_nan_plan(S_entry) = eps', '$boolnot_nan_plan(S_entry) = eps',
        '~$boolnot_nan_source(S_entry, pboolnotnanwarning)',
        'S_entry.EVENTS = eps', '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$ternary_nan_plan(S_entry[.ORIGIN = eps]) = eps',
        '$ternary_nan_plan(S_entry[.CODE = eps]) = eps',
        '$ternary_nan_plan(S_entry[.RESULT = KNOWN (PFLOAT pboolnotnanwarning.BITS)]) = eps',
        '$ternary_nan_plan(S_entry[.TODO = [SHORT_RESULT false expression_false 24 25]]) = eps',
        '$ternary_nan_plan(S_entry[.ERRORHANDLER.CALLBACK = eps]) = eps',
        '$ternary_nan_plan(S_entry[.ERRORHANDLER.LEVELS = 8192]) = eps',
        '$ternary_nan_plan(S_entry[.REFCELLS = [n_x]]) = eps',
        '$ternary_nan_plan(S_entry[.STORE[n_x] = DEFINED (PFLOAT 0)]) = eps',
        '$ternary_nan_plan(S_entry[.ALLOCATIONS = eps]) = eps',
        '~$ternary_nan_source(S_entry, pboolnotnanwarning, SELECT_VALUE expression_false expression_false 24 25 25)',
        '~$ternary_nan_source(S_entry, pboolnotnanwarning, SELECT_VALUE ABSENT expression_false 24 24 25)',
        '~$ternary_nan_source(S_entry, pboolnotnanwarning, SELECT_VALUE ABSENT expression_false 24 0 24)',
        '~$ternary_nan_source(S_entry, pboolnotnanwarning, TRUTH_RESULT false 24)',
        '~$ternary_nan_source(S_entry, pboolnotnanwarning[.LINE = 25], ptask_original)',
        '~$ternary_nan_source(S_entry, pboolnotnanwarning[.INPUT = VARIABLE ($ptascii("rhs")) 24], ptask_original)',
        '~$ternary_nan_source(S_entry, pboolnotnanwarning[.BITS = 0], ptask_original)',
        '~$ternary_nan_source(S_entry, pboolnotnanwarning[.CELL = |S_entry.STORE|], ptask_original)',
        'PhpStep: S_entry ~> S_capture_atomic',
        'S_capture_atomic = S_entry[.TODO = (TERNARY_NAN_WARNING pboolnotnanwarning ptask_original 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture = S_capture_atomic', '$ternary_nan_frontier(S_capture, 1)',
        '$ternary_nan_warning_valid(S_capture, pboolnotnanwarning, ptask_original, 0)',
        '$ternary_nan_warning_valid(S_capture, pboolnotnanwarning, ptask_original, 1)',
        '~$ternary_nan_warning_valid(S_capture, pboolnotnanwarning, ptask_original, 2)',
        '$task_nodes(TERNARY_NAN_WARNING pboolnotnanwarning ptask_original 0) = eps',
        '$task_nodes(ptask_original) = eps',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_x) = 1',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        '$ternary_nan_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = TERNARY_NAN_WARNING pboolnotnanwarning ptask_original 1',
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
        '$ternary_nan_entered(S_entered.FRAMES)', 'S_entered.CURRENT =/= eps',
        'S_entered.FRAMES = pframe :: pframe_tail*', '$ternary_nan_handler_frame(pframe)',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_saved*',
        'perrorcall_entered.TARGET =/= eps',
        'perrorcall_entered.RESUME = TERNARY_NAN_WARNING pboolnotnanwarning ptask_original 1',
        '$call_descriptors_valid(S_entered)',
    ]
    seek('S_return', 'S_entered', 4)
    checks += [
        'S_return.TODO = (TERNARY_NAN_WARNING pboolnotnanwarning ptask_original 1) :: ptask_tail*',
        '$lookup(S_return.ENV, $ptascii("x")) = (n_x)',
        'S_return.STORE[n_x] = DEFINED (PFLOAT 4607182418800017408)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)',
        'S_return.STORE[n_calls] = DEFINED (PINT 1)', 'S_return.STORE[n_rhs] = DEFINED (PINT 0)',
        '$ternary_nan_source(S_return, pboolnotnanwarning, ptask_original)',
        '$boolnot_nan_ready(S_return, pboolnotnanwarning) = (4607182418800017408)',
        '$number_bool(NFLOAT 4607182418800017408) = (true, false)',
        '~$boolnot_nan_snapshot(S_return, pboolnotnanwarning)',
        '~$ternary_nan_warning_valid(S_return, pboolnotnanwarning, ptask_original, 0)',
        '$ternary_nan_warning_valid(S_return, pboolnotnanwarning, ptask_original, 1)',
        '~$error_call_valid(S_return, perrorcall)', '$error_call_valid(S_return, perrorcall_entered)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_x) = 1',
        '$ternary_nan_diagnostics(S_return.EVENTS, "Warning") = 1',
        '$ternary_nan_diagnostics(S_return.EVENTS, "Deprecated") = 0',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'PhpStep: S_return ~> S_value_atomic',
        'S_value_atomic = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (PFLOAT 4607182418800017408)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        # Derived no-rewarning, opposite truth and representation controls.
        'S_nan = S_return[.STORE[n_x] = DEFINED (PFLOAT pboolnotnanwarning.BITS)]',
        'PhpStep: S_nan ~> S_nan_value',
        'S_nan_value = S_nan[.TODO = ptask_tail*][.RESULT = KNOWN (PFLOAT pboolnotnanwarning.BITS)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_nan_value.EVENTS = S_return.EVENTS',
        'S_zero = S_return[.STORE[n_x] = DEFINED (PFLOAT 0)]',
        'PhpStep: S_zero ~> S_fallback',
        'S_fallback = S_zero[.TODO = [$at_task($origin_child((pboolnotnanwarning.SITE), [PCFIELD 2]), EVAL expression_false), VALUE_COPY 25] ++ ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$ternary_nan_frontier(S_fallback, 6)',
        'S_retyped = S_return[.STORE[n_x] = DEFINED (PINT 1)]',
        'PhpStep: S_retyped ~> S_boundary',
        'S_boundary = S_retyped[.COMPLETION = UNSUPPORTED "shorthand ternary NaN changed CV representation"]',
    ]
    step('S_value', 'S_return')
    checks += [
        'S_value = S_value_atomic', '$ternary_nan_frontier(S_value, 5)',
        'S_value.RESULT =/= KNOWN (PBOOL true)', 'S_value.RESULT =/= KNOWN (PFLOAT pboolnotnanwarning.BITS)',
        'S_value.STORE = S_return.STORE', 'S_value.ENV = S_return.ENV',
        'S_value.ALLOCATIONS = S_return.ALLOCATIONS', 'S_value.EVENTS = S_return.EVENTS',
        'S_value.STORE[n_v] = DEFINED (PINT 100)', 'S_value.STORE[n_rhs] = DEFINED (PINT 0)',
        '$ternary_nan_plan(S_value) = eps', '$call_descriptors_valid(S_value)', '$heap_valid($heap_graph(S_value))',
        'S_done = $drive_steps(S_value, 3000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("x")) = (n_x)', 'S_done.STORE[n_x] = DEFINED (PINT 8)',
        'S_done.STORE[n_v] = DEFINED (PFLOAT 4607182418800017408)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)', 'S_done.STORE[n_rhs] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_x) = 1',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$ternary_nan_diagnostics(S_done.EVENTS, "Warning") = 1',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
