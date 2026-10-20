#!/usr/bin/env python3
"""Borrowed object-cast Warning, immediate retirement and canceled delivery."""
import base64
import json

import object_numeric_cast_warning_cases as cases
import integer_operator_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $object_numeric_cast_task(ptask) : bool
def $object_numeric_cast_task(OBJECT_NUMERIC_CAST_WARNING porigin pcast poperand z n) = true
def $object_numeric_cast_task(ERROR_HANDLER_INVOKE perrorcall) = $object_numeric_cast_task(perrorcall.RESUME)
def $object_numeric_cast_task(ERROR_HANDLER_RESULT perrorcall) = $object_numeric_cast_task(perrorcall.RESUME)
def $object_numeric_cast_task(ERROR_HANDLER_CLEAN perrorcall) = $object_numeric_cast_task(perrorcall.RESUME)
def $object_numeric_cast_task(ptask) = false -- otherwise
dec $object_numeric_cast_tasks(ptask*) : bool
def $object_numeric_cast_tasks(eps) = false
def $object_numeric_cast_tasks(ptask :: ptask_tail*) = ($object_numeric_cast_task(ptask) \/ $object_numeric_cast_tasks(ptask_tail*))
dec $object_numeric_cast_handler_frame(pframe) : bool
def $object_numeric_cast_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = OBJECT_NUMERIC_CAST_WARNING porigin pcast poperand z 1
  -- if perrorcall.TARGET =/= eps
def $object_numeric_cast_handler_frame(pframe) = false -- otherwise
dec $object_numeric_cast_entered(pframe*) : bool
def $object_numeric_cast_entered(eps) = false
def $object_numeric_cast_entered(pframe :: pframe_tail*) = ($object_numeric_cast_handler_frame(pframe) \/ $object_numeric_cast_entered(pframe_tail*))
dec $object_numeric_cast_frontier(pstate, nat) : bool
def $object_numeric_cast_frontier(S, 0) = ($object_numeric_cast_plan(S) =/= eps)
def $object_numeric_cast_frontier(S, 1) = true
  -- if S.TODO = (OBJECT_NUMERIC_CAST_WARNING porigin pcast poperand z 0) :: ptask_tail*
def $object_numeric_cast_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = OBJECT_NUMERIC_CAST_WARNING porigin pcast poperand z 1
  -- if perrorcall.TARGET = eps
def $object_numeric_cast_frontier(S, 3) = (S.CURRENT =/= eps /\ $object_numeric_cast_entered(S.FRAMES))
def $object_numeric_cast_frontier(S, 4) = true
  -- if S.TODO = (OBJECT_NUMERIC_CAST_WARNING porigin pcast poperand z 1) :: ptask_tail*
def $object_numeric_cast_frontier(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (pcnode)
  -- if $object_numeric_cast_operator(pcnode) =/= eps
  -- if S.RESULT = KNOWN pvalue
  -- if pvalue <- [PINT 1, PFLOAT 4607182418800017408]
  -- if ~$object_numeric_cast_tasks(S.TODO)
def $object_numeric_cast_frontier(S, 6) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n_exception) :: ptask_tail*
  -- if ~$object_numeric_cast_tasks(S.TODO)
def $object_numeric_cast_frontier(S, n) = false -- otherwise
dec $object_numeric_cast_seek(pstate, nat, nat) : pstate
def $object_numeric_cast_seek(S, n_stage, n) = S -- if $object_numeric_cast_frontier(S, n_stage)
def $object_numeric_cast_seek(S, n_stage, n) = S
  -- if ~$object_numeric_cast_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $object_numeric_cast_seek(S, n_stage, n) = S
  -- if ~$object_numeric_cast_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $object_numeric_cast_seek(S, n_stage, n) = $object_numeric_cast_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$object_numeric_cast_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
dec $object_numeric_cast_diagnostic(pevent, text) : nat
def $object_numeric_cast_diagnostic(DIAGNOSTIC text n_message* z, text) = 1
def $object_numeric_cast_diagnostic(DIAGNOSTIC_SOURCE n_source text n_message* z, text) = 1
def $object_numeric_cast_diagnostic(DIAGNOSTIC_STACK text n_message* z n_trace*, text) = 1
def $object_numeric_cast_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n_message* z n_trace*, text) = 1
def $object_numeric_cast_diagnostic(pevent, text) = 0 -- otherwise
dec $object_numeric_cast_diagnostics(pevent*, text) : nat
def $object_numeric_cast_diagnostics(eps, text) = 0
def $object_numeric_cast_diagnostics(pevent :: pevent_tail*, text) = $($object_numeric_cast_diagnostic(pevent, text) + $object_numeric_cast_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $object_numeric_cast_seek({before}, {stage}, 4000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$object_numeric_cast_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$object_numeric_cast_plan(S_entry) = (porigin, pcast, poperand, z)',
        'pcast = CASTINT', 'poperand = VARIABLE ($ptascii("x")) 25', 'z = 25',
        'S_entry.RESULT = poperand',
        '$object_numeric_cast_source(S_entry, porigin, pcast, poperand, z)',
        '$object_numeric_cast_snapshot(S_entry, poperand)',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)',
        '$lookup(S_entry.ENV, $ptascii("weak")) = (n_weak_cell)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
        'S_entry.STORE[n_x] = DEFINED (POBJECT n_object)',
        'S_entry.OBJECTS[n_object] = STDINSTANCE',
        'S_entry.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
        'S_entry.OBJECTS[n_weak] = WEAKREFERENCE (n_object)',
        '$weakref_get(S_entry, n_weak) = POBJECT n_object',
        '$node_children(S_entry, HOBJECT n_weak) = eps',
        'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '~(n_x <- S_entry.REFCELLS)',
        '$integer_pointer_select(S_entry, poperand) = (INTEGER_CV ($ptascii("x")))',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HOBJECT n_object) = 1',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        'S_entry.ERRORHANDLER.LEVELS = 2',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$object_numeric_cast_plan(S_entry[.ORIGIN = eps]) = eps',
        '$object_numeric_cast_plan(S_entry[.CODE = eps]) = eps',
        '$object_numeric_cast_plan(S_entry[.RESULT = KNOWN (POBJECT n_object)]) = eps',
        '$object_numeric_cast_plan(S_entry[.STORE[n_x] = UNDEFINED]) = eps',
        '$object_numeric_cast_plan(S_entry[.REFCELLS = [n_x]]) = eps',
        '$object_numeric_cast_plan(S_entry[.STORE[n_x] = DEFINED (PINT 99)]) = eps',
        '$object_numeric_cast_plan(S_entry[.OBJECTS[n_object] = WEAKREFERENCE eps]) = eps',
        '$object_numeric_cast_plan(S_entry[.ERRORHANDLER.CALLBACK = eps]) = eps',
        '$object_numeric_cast_plan(S_entry[.ERRORHANDLER.LEVELS = 8192]) = eps',
        '~$object_numeric_cast_source(S_entry, porigin, CASTFLOAT, poperand, z)',
        '~$object_numeric_cast_source(S_entry, porigin, pcast, poperand, 24)',
        '~$object_numeric_cast_source(S_entry, porigin, pcast, VARIABLE ($ptascii("v")) 25, z)',
        '~$object_numeric_cast_warning_valid(S_entry, porigin, pcast, poperand, z, 2)',
        'S_entry.TODO = ptask_old :: ptask_tail*',
        'PhpStep: S_entry ~> S_begin_raw',
        'S_begin_raw = S_entry[.TODO = (OBJECT_NUMERIC_CAST_WARNING porigin pcast poperand z 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture = S_begin_raw', '$object_numeric_cast_frontier(S_capture, 1)',
        '$object_numeric_cast_warning_valid(S_capture, porigin, pcast, poperand, z, 0)',
        '$task_nodes(OBJECT_NUMERIC_CAST_WARNING porigin pcast poperand z 0) = eps',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HOBJECT n_object) = 1',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        '$object_numeric_cast_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = OBJECT_NUMERIC_CAST_WARNING porigin pcast poperand z 1',
        'perrorcall.TARGET = eps', 'perrorcall.LEVEL = 2', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = $ptascii("Object of class stdClass could not be converted to int")',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 8192])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = 24])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += ['$object_numeric_cast_entered(S_entered.FRAMES)', '$call_descriptors_valid(S_entered)']
    seek('S_throw', 'S_entered', 6)
    checks += [
        'S_throw.TODO = (THROW_SEARCH n_second) :: ptask_caller*',
        '~$object_numeric_cast_tasks(S_throw.TODO)',
        'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps',
        'S_throw.STORE[n_x] = DEFINED (PINT 99)',
        'S_throw.STORE[n_v] = DEFINED (PINT 100)',
        'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
        '$lookup(S_throw.ENV, $ptascii("x")) = (n_x)',
        '$object_numeric_cast_source(S_throw, porigin, pcast, poperand, z)',
        '~$object_numeric_cast_snapshot(S_throw, poperand)',
        '~$object_numeric_cast_warning_valid(S_throw, porigin, pcast, poperand, z, 0)',
        '$object_numeric_cast_warning_valid(S_throw, porigin, pcast, poperand, z, 1)',
        'S_throw.OBJECTS[n_weak] = S_entry.OBJECTS[n_weak]',
        '$weakref_get(S_throw, n_weak) = PNULL',
        '$node_children(S_throw, HOBJECT n_weak) = eps',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_object) = 0',
        '~((HOBJECT n_object) <- S_throw.ALLOCATIONS)',
        '(HOBJECT n_weak) <- S_throw.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_x) = 1',
        '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
        '$throwable_live(S_throw, n_second)',
        '$throwable_previous_id(S_throw, n_second) = eps',
        '$throwable_field(S_throw, n_second, "line") = PINT 20',
        '$object_numeric_cast_diagnostics(S_throw.EVENTS, "Warning") = 0',
        '$object_numeric_cast_diagnostics(S_throw.EVENTS, "Deprecated") = 0',
        '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
        'S_done = $drive_steps(S_throw, 4000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_x] = DEFINED (PINT 8)',
        'S_done.STORE[n_v] = DEFINED (PINT 100)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        '$weakref_get(S_done, n_weak) = PNULL',
        '~((HOBJECT n_object) <- S_done.ALLOCATIONS)',
        '$throwable_previous_id(S_done, n_second) = eps',
        '$object_numeric_cast_diagnostics(S_done.EVENTS, "Warning") = 0',
        '$object_numeric_cast_diagnostics(S_done.EVENTS, "Deprecated") = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_dispatch, 0) = S_dispatch[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
