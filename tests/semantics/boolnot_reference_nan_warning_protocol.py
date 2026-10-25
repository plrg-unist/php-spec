#!/usr/bin/env python3
"""Boolean NOT rereads a retained reference cell after source CV rebinding."""
import base64
import json

import boolnot_reference_nan_warning_cases as cases
import integer_operator_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $boolnot_reference_nan_task(ptask) : bool
def $boolnot_reference_nan_task(BOOLNOT_REFERENCE_NAN_WARNING pboolnotnanwarning n) = true
def $boolnot_reference_nan_task(ERROR_HANDLER_INVOKE perrorcall) = $boolnot_reference_nan_task(perrorcall.RESUME)
def $boolnot_reference_nan_task(ERROR_HANDLER_RESULT perrorcall) = $boolnot_reference_nan_task(perrorcall.RESUME)
def $boolnot_reference_nan_task(ERROR_HANDLER_CLEAN perrorcall) = $boolnot_reference_nan_task(perrorcall.RESUME)
def $boolnot_reference_nan_task(ptask) = false -- otherwise
dec $boolnot_reference_nan_tasks(ptask*) : bool
def $boolnot_reference_nan_tasks(eps) = false
def $boolnot_reference_nan_tasks(ptask :: ptask_tail*) = ($boolnot_reference_nan_task(ptask) \/ $boolnot_reference_nan_tasks(ptask_tail*))
dec $boolnot_reference_nan_handler_frame(pframe) : bool
def $boolnot_reference_nan_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = BOOLNOT_REFERENCE_NAN_WARNING pboolnotnanwarning 1
  -- if perrorcall.TARGET =/= eps
def $boolnot_reference_nan_handler_frame(pframe) = false -- otherwise
dec $boolnot_reference_nan_entered(pframe*) : bool
def $boolnot_reference_nan_entered(eps) = false
def $boolnot_reference_nan_entered(pframe :: pframe_tail*) = ($boolnot_reference_nan_handler_frame(pframe) \/ $boolnot_reference_nan_entered(pframe_tail*))
dec $boolnot_reference_nan_frontier(pstate, nat) : bool
def $boolnot_reference_nan_frontier(S, 0) = ($boolnot_reference_nan_plan(S) =/= eps)
def $boolnot_reference_nan_frontier(S, 1) = true
  -- if S.TODO = (BOOLNOT_REFERENCE_NAN_WARNING pboolnotnanwarning 0) :: ptask_tail*
def $boolnot_reference_nan_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = BOOLNOT_REFERENCE_NAN_WARNING pboolnotnanwarning 1
  -- if perrorcall.TARGET = eps
def $boolnot_reference_nan_frontier(S, 3) = (S.CURRENT =/= eps /\ $boolnot_reference_nan_entered(S.FRAMES))
def $boolnot_reference_nan_frontier(S, 4) = true
  -- if S.TODO = (BOOLNOT_REFERENCE_NAN_WARNING pboolnotnanwarning 1) :: ptask_tail*
def $boolnot_reference_nan_frontier(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprBooleanNot expression metadata)
  -- if S.RESULT = KNOWN (PBOOL b)
  -- if ~$boolnot_reference_nan_tasks(S.TODO)
def $boolnot_reference_nan_frontier(S, 6) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if ~$boolnot_reference_nan_tasks(S.TODO)
def $boolnot_reference_nan_frontier(S, n) = false -- otherwise
dec $boolnot_reference_nan_seek(pstate, nat, nat) : pstate
def $boolnot_reference_nan_seek(S, n_stage, n) = S -- if $boolnot_reference_nan_frontier(S, n_stage)
def $boolnot_reference_nan_seek(S, n_stage, n) = S
  -- if ~$boolnot_reference_nan_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $boolnot_reference_nan_seek(S, n_stage, n) = S
  -- if ~$boolnot_reference_nan_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $boolnot_reference_nan_seek(S, n_stage, n) = $boolnot_reference_nan_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$boolnot_reference_nan_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
dec $boolnot_reference_nan_diagnostic(pevent, text) : nat
def $boolnot_reference_nan_diagnostic(DIAGNOSTIC text n_message* z, text) = 1
def $boolnot_reference_nan_diagnostic(DIAGNOSTIC_SOURCE n_source text n_message* z, text) = 1
def $boolnot_reference_nan_diagnostic(DIAGNOSTIC_STACK text n_message* z n_trace*, text) = 1
def $boolnot_reference_nan_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n_message* z n_trace*, text) = 1
def $boolnot_reference_nan_diagnostic(pevent, text) = 0 -- otherwise
dec $boolnot_reference_nan_diagnostics(pevent*, text) : nat
def $boolnot_reference_nan_diagnostics(eps, text) = 0
def $boolnot_reference_nan_diagnostics(pevent :: pevent_tail*, text) = $($boolnot_reference_nan_diagnostic(pevent, text) + $boolnot_reference_nan_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $boolnot_reference_nan_seek({before}, {stage}, 3000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$boolnot_reference_nan_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$boolnot_reference_nan_plan(S_entry) = (pboolnotnanwarning)',
        'pboolnotnanwarning.LINE = 25', 'pboolnotnanwarning.INPUT = VARIABLE ($ptascii("x")) 25',
        'S_entry.RESULT = pboolnotnanwarning.INPUT',
        'S_entry.TODO = (TRUTH_RESULT true 25) :: ptask_tail*',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_old)',
        '$lookup(S_entry.ENV, $ptascii("alias")) = (n_old)', 'pboolnotnanwarning.CELL = n_old',
        '$lookup(S_entry.ENV, $ptascii("replacement")) = (n_new)', 'n_old =/= n_new',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        'S_entry.STORE[n_old] = DEFINED (PFLOAT pboolnotnanwarning.BITS)',
        '$fparts_nan($float_decode(pboolnotnanwarning.BITS))',
        'S_entry.STORE[n_new] = DEFINED (PFLOAT 4607182418800017408)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)', 'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        'n_old <- S_entry.REFCELLS', '~(n_new <- S_entry.REFCELLS)',
        '$integer_pointer_select(S_entry, pboolnotnanwarning.INPUT) = (INTEGER_CELL n_old)',
        '$boolnot_nan_source(S_entry, pboolnotnanwarning)',
        '$boolnot_reference_nan_ready(S_entry, pboolnotnanwarning) = (pboolnotnanwarning.BITS)',
        '$boolnot_reference_nan_snapshot(S_entry, pboolnotnanwarning)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_old) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_new) = 1',
        '$boolnot_nan_plan(S_entry) = eps', '$boolnot_nan_ready(S_entry, pboolnotnanwarning) = eps',
        'S_entry.EVENTS = eps', '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$boolnot_reference_nan_plan(S_entry[.ORIGIN = eps]) = eps',
        '$boolnot_reference_nan_plan(S_entry[.CODE = eps]) = eps',
        '$boolnot_reference_nan_plan(S_entry[.RESULT = KNOWN (PFLOAT pboolnotnanwarning.BITS)]) = eps',
        '$boolnot_reference_nan_plan(S_entry[.TODO = [TRUTH_RESULT false 25]]) = eps',
        '$boolnot_reference_nan_plan(S_entry[.ERRORHANDLER.CALLBACK = eps]) = eps',
        '$boolnot_reference_nan_plan(S_entry[.ERRORHANDLER.LEVELS = 8192]) = eps',
        '$boolnot_reference_nan_plan(S_entry[.REFCELLS = eps]) = eps',
        '$boolnot_reference_nan_plan(S_entry[.STORE[n_old] = DEFINED (PFLOAT 0)]) = eps',
        '$boolnot_reference_nan_ready(S_entry[.STORE[n_old] = DEFINED (PINT 0)], pboolnotnanwarning) = eps',
        '$boolnot_reference_nan_ready(S_entry[.ALLOCATIONS = eps], pboolnotnanwarning) = eps',
        '$boolnot_reference_nan_ready(S_entry[.PROPREFS = [{CELL n_old, SOURCES eps}]], pboolnotnanwarning) = eps',
        '$boolnot_reference_nan_ready(S_entry[.REFCOERCIONS = [{CELL n_old, SITE pboolnotnanwarning.SITE, LINE 25, VALUE eps}]], pboolnotnanwarning) = eps',
        '$boolnot_reference_nan_ready(S_entry[.PARAMETERBACKINGS = [{FUNCTION pboolnotnanwarning.SITE, INDEX 0, CELL n_old, LINE 25, VALUE eps}]], pboolnotnanwarning) = eps',
        '$boolnot_reference_nan_ready(S_entry[.LITERALREFRETAINED = [n_old]], pboolnotnanwarning) = eps',
        '$boolnot_reference_nan_ready(S_entry[.LITERALREFDEBTS = [n_old]], pboolnotnanwarning) = eps',
        '~$boolnot_reference_nan_snapshot(S_entry[.ENV = eps], pboolnotnanwarning)',
        '~$boolnot_reference_nan_warning_valid(S_entry, pboolnotnanwarning[.CELL = n_new], 0)',
        '~$boolnot_reference_nan_warning_valid(S_entry, pboolnotnanwarning[.LINE = 24], 0)',
        '~$boolnot_reference_nan_warning_valid(S_entry, pboolnotnanwarning[.INPUT = VARIABLE ($ptascii("alias")) 25], 0)',
        '~$boolnot_reference_nan_warning_valid(S_entry, pboolnotnanwarning[.BITS = 0], 0)',
        'PhpStep: S_entry ~> S_capture_atomic',
        'S_capture_atomic = S_entry[.TODO = (BOOLNOT_REFERENCE_NAN_WARNING pboolnotnanwarning 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture = S_capture_atomic', '$boolnot_reference_nan_frontier(S_capture, 1)',
        '$boolnot_reference_nan_warning_valid(S_capture, pboolnotnanwarning, 0)',
        '$boolnot_reference_nan_warning_valid(S_capture, pboolnotnanwarning, 1)',
        '~$boolnot_reference_nan_warning_valid(S_capture, pboolnotnanwarning, 2)',
        '$task_nodes(BOOLNOT_REFERENCE_NAN_WARNING pboolnotnanwarning 0) = eps',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_old) = 2',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        '$boolnot_reference_nan_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = BOOLNOT_REFERENCE_NAN_WARNING pboolnotnanwarning 1',
        'perrorcall.TARGET = eps', 'perrorcall.SITE = pboolnotnanwarning.SITE',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = $ptascii("unexpected NAN value was coerced to bool")',
        'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE 25',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 8192])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = 24])',
        'S_dispatch.EVENTS = eps', '$call_descriptors_valid(S_dispatch)',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += [
        '$boolnot_reference_nan_entered(S_entered.FRAMES)', 'S_entered.CURRENT =/= eps',
        'S_entered.FRAMES = pframe :: pframe_tail*', '$boolnot_reference_nan_handler_frame(pframe)',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_saved*',
        'perrorcall_entered.TARGET =/= eps',
        'perrorcall_entered.RESUME = BOOLNOT_REFERENCE_NAN_WARNING pboolnotnanwarning 1',
        '$call_descriptors_valid(S_entered)',
    ]
    seek('S_return', 'S_entered', 4)
    checks += [
        'S_return.TODO = (BOOLNOT_REFERENCE_NAN_WARNING pboolnotnanwarning 1) :: ptask_tail*',
        '$lookup(S_return.ENV, $ptascii("alias")) = (n_old)',
        '$lookup(S_return.ENV, $ptascii("x")) = (n_new)',
        '$lookup(S_return.ENV, $ptascii("replacement")) = (n_new)',
        'S_return.STORE[n_old] = DEFINED (PFLOAT 0)',
        'S_return.STORE[n_new] = DEFINED (PFLOAT 4607182418800017408)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)', 'S_return.STORE[n_calls] = DEFINED (PINT 1)',
        'n_old <- S_return.REFCELLS', 'n_new <- S_return.REFCELLS',
        '$integer_pointer_select(S_return, pboolnotnanwarning.INPUT) = (INTEGER_CELL n_new)',
        '$integer_pointer_value(S_return, INTEGER_CELL n_new) = (PFLOAT 4607182418800017408)',
        '$boolnot_reference_nan_ready(S_return, pboolnotnanwarning) = (0)',
        '$number_bool(NFLOAT 0) = (false, false)',
        '$boolnot_nan_source(S_return, pboolnotnanwarning)',
        '~$boolnot_reference_nan_snapshot(S_return, pboolnotnanwarning)',
        '~$boolnot_reference_nan_warning_valid(S_return, pboolnotnanwarning, 0)',
        '$boolnot_reference_nan_warning_valid(S_return, pboolnotnanwarning, 1)',
        '~$error_call_valid(S_return, perrorcall)', '$error_call_valid(S_return, perrorcall_entered)',
        '$boolnot_nan_ready(S_return, pboolnotnanwarning) = eps',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_old) = 1',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_new) = 2',
        '$task_nodes(BOOLNOT_REFERENCE_NAN_WARNING pboolnotnanwarning 1) = eps',
        '$boolnot_reference_nan_diagnostics(S_return.EVENTS, "Warning") = 1',
        '$boolnot_reference_nan_diagnostics(S_return.EVENTS, "Deprecated") = 0',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'PhpStep: S_return ~> S_atomic',
        'S_atomic = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL true)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        # Derived controls discriminate pointer identity and skip a second warning.
        'S_new_changed = S_return[.STORE[n_new] = DEFINED (PINT 99)]',
        'PhpStep: S_new_changed ~> S_old_result',
        'S_old_result = S_new_changed[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL true)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_nan = S_return[.STORE[n_old] = DEFINED (PFLOAT pboolnotnanwarning.BITS)]',
        'PhpStep: S_nan ~> S_nan_result',
        'S_nan_result = S_nan[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_nan_result.EVENTS = S_return.EVENTS',
        'S_retyped = S_return[.STORE[n_old] = DEFINED (PINT 0)]',
        'PhpStep: S_retyped ~> S_boundary',
        'S_boundary = S_retyped[.COMPLETION = UNSUPPORTED "boolean NOT NaN changed reference representation"]',
    ]
    step('S_result', 'S_return')
    checks += [
        'S_result = S_atomic', '$boolnot_reference_nan_frontier(S_result, 5)',
        'S_result.STORE = S_return.STORE', 'S_result.ENV = S_return.ENV',
        'S_result.ALLOCATIONS = S_return.ALLOCATIONS', 'S_result.REFCELLS = S_return.REFCELLS',
        'S_result.EVENTS = S_return.EVENTS', 'S_result.STRINGDATA = S_return.STRINGDATA',
        '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 3000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("alias")) = (n_old)',
        '$lookup(S_done.ENV, $ptascii("x")) = (n_new)',
        '$lookup(S_done.ENV, $ptascii("replacement")) = (n_new)',
        'S_done.STORE[n_old] = DEFINED (PFLOAT 0)', 'S_done.STORE[n_new] = DEFINED (PINT 8)',
        'S_done.STORE[n_v] = DEFINED (PBOOL true)', 'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_old) = 1',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_new) = 2',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$boolnot_reference_nan_diagnostics(S_done.EVENTS, "Warning") = 1',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
