#!/usr/bin/env python3
"""Reached acquired string-cast array ownership and Warning continuation."""
import base64
import json

import integer_operator_warning_protocol as shared
import cast_owned_array_warning_cases as cases

CASES = ('cast-acquired-array-false-default', 'cast-acquired-array-pending-throw')
HELPERS = shared.HELPERS + r'''
dec $cast_owned_handler_frame(pframe) : bool
def $cast_owned_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CAST_OWNED_ARRAY_WARNING pcastownedarraywarning 1
  -- if perrorcall.TARGET =/= eps
def $cast_owned_handler_frame(pframe) = false -- otherwise
dec $cast_owned_entered(pframe*) : bool
def $cast_owned_entered(eps) = false
def $cast_owned_entered(pframe :: pframe_tail*) = ($cast_owned_handler_frame(pframe) \/ $cast_owned_entered(pframe_tail*))
dec $cast_owned_frontier(pstate, nat) : bool
def $cast_owned_frontier(S, 0) = ($cast_owned_array_plan(S) =/= eps)
def $cast_owned_frontier(S, 1) = true
  -- if S.TODO = (CAST_OWNED_ARRAY_WARNING pcastownedarraywarning 0) :: ptask_tail*
def $cast_owned_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CAST_OWNED_ARRAY_WARNING pcastownedarraywarning 1
  -- if perrorcall.TARGET = eps
def $cast_owned_frontier(S, 3) = (S.CURRENT =/= eps /\ $cast_owned_entered(S.FRAMES))
def $cast_owned_frontier(S, 4) = true
  -- if S.TODO = (CAST_OWNED_ARRAY_WARNING pcastownedarraywarning 1) :: ptask_tail*
def $cast_owned_frontier(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING $ptascii("Array"))
def $cast_owned_frontier(S, 6) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: (ORIGIN_RETURN porigin) :: (WRITE_NAME ptbytes z) :: ptask_tail*
  -- if $integer_outputs(S.EVENTS) = ($ptascii("P;H:2:25:Array to string conversion:1;"))
def $cast_owned_frontier(S, 7) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CAST_OWNED_ARRAY_WARNING pcastownedarraywarning 1
  -- if $integer_outputs(S.EVENTS) = ($ptascii("P;H:2:25:Array to string conversion:1;"))
def $cast_owned_frontier(S, n) = false -- otherwise
dec $cast_owned_seek(pstate, nat, nat) : pstate
def $cast_owned_seek(S, n_stage, n) = S -- if $cast_owned_frontier(S, n_stage)
def $cast_owned_seek(S, n_stage, n) = S
  -- if ~$cast_owned_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $cast_owned_seek(S, n_stage, n) = S
  -- if ~$cast_owned_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $cast_owned_seek(S, n_stage, n) = $cast_owned_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$cast_owned_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    throwing = name.endswith('pending-throw')
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(label, start, stage):
        checks.extend([f'{label}_found = $cast_owned_seek({start}, {stage}, 4000)',
                       f'{label}_found.COMPLETION = NORMAL \\/ {label}_found.COMPLETION = BUDGET',
                       f'{label} = {label}_found[.COMPLETION = NORMAL]',
                       f'$cast_owned_frontier({label}, {stage})'])

    def step(label, start):
        checks.extend([f'{label}_budget = $drive_steps({start}, 1)',
                       f'{label}_budget.COMPLETION = BUDGET',
                       f'{label} = {label}_budget[.COMPLETION = NORMAL]'])

    seek('S_entry', 'S_initial', 0)
    checks += [
        'S_entry.TODO = (CAST_RESULT CASTSTRING 25) :: ptask_tail*',
        'S_entry.ORIGIN = (porigin_cast)',
        'S_entry.RESULT = KNOWN (PARRAY n_array)',
        'S_entry.OUTPUTBUFFERS = eps',
        '$cast_owned_array_plan(S_entry) = (pcastownedarraywarning)',
        'pcastownedarraywarning.SITE = porigin_cast',
        'pcastownedarraywarning.LINE = 25',
        'pcastownedarraywarning.ARRAY = n_array',
        '$cast_owned_array_source(S_entry, pcastownedarraywarning)',
        '$cast_owned_array_snapshot(S_entry, pcastownedarraywarning)',
        '$origin_node(S_entry.SOURCES, porigin_cast) = (NExprCastString expression metadata)',
        '$lookup(S_entry.ENV, $ptascii("a")) = (n_a)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("made")) = (n_made)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        'S_entry.STORE[n_a] = DEFINED (PARRAY n_array)',
        'S_entry.STORE[n_v] = DEFINED pvalue_old',
        '$string_bytes(pvalue_old) = ($ptascii("old"))',
        'S_entry.STORE[n_made] = DEFINED (PINT 1)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '(HARRAY n_array) <- S_entry.ALLOCATIONS',
        '$array_string_cast_items(S_entry.ARRAYS[n_array].ITEMS)',
        'S_entry.ARRAYS[n_array].ITEMS =/= eps',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_array) = 2',
        '$cast_owned_array_plan(S_entry[.ORIGIN = eps]) = eps',
        '$cast_owned_array_plan(S_entry[.RESULT = KNOWN (PINT 7)]) = eps',
        '~$cast_owned_array_source(S_entry, pcastownedarraywarning[.LINE = 24])',
        '~$cast_owned_array_snapshot(S_entry[.GC.IMMUTABLE = S_entry.GC.IMMUTABLE ++ [n_array]], pcastownedarraywarning)',
        '$integer_outputs(S_entry.EVENTS) = ($ptascii("P;"))',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'S_entry.TODO = ptask_old :: ptask_tail*',
        'PhpStep: S_entry ~> S_begin_raw',
        'S_begin_raw = S_entry[.TODO = (CAST_OWNED_ARRAY_WARNING pcastownedarraywarning 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture = S_begin_raw',
        '$task_nodes(CAST_OWNED_ARRAY_WARNING pcastownedarraywarning 0) = [HARRAY n_array]',
        '$cast_owned_array_valid(S_capture, pcastownedarraywarning, 0)',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HARRAY n_array) = 2',
        'S_capture.RESULT = KNOWN PNULL',
        'S_capture.STORE = S_entry.STORE',
        '$integer_outputs(S_capture.EVENTS) = ($ptascii("P;"))',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
        'S_buffer_capture = S_capture[.OUTPUTBUFFERS = [{ID S_capture.OUTPUTSEQ, HANDLER eps, CHUNK 0, FLAGS 112, SIZE 16384, BYTES eps}]][.OUTPUTSEQ = $(S_capture.OUTPUTSEQ + 1)]',
        '$output_state_valid(S_buffer_capture)',
        '~$cast_owned_array_valid(S_buffer_capture, pcastownedarraywarning, 0)',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = CAST_OWNED_ARRAY_WARNING pcastownedarraywarning 1',
        'perrorcall.TARGET = eps',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = $ptascii("Array to string conversion")',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = 24])',
        '$heap_owners($heap_prune($heap_graph(S_dispatch)), HARRAY n_array) = 2',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        '$cast_owned_handler_frame(pframe)',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if throwing:
        seek('S_pending', 'S_entered', 7)
        checks += [
            'S_pending.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_pending) :: ptask_pending*',
            'perrorcall_pending.RESUME = CAST_OWNED_ARRAY_WARNING pcastownedarraywarning 1',
            '$lookup(S_pending.ENV, $ptascii("a")) = eps',
            '$heap_owners($heap_prune($heap_graph(S_pending)), HARRAY n_array) = 1',
            '(HARRAY n_array) <- S_pending.ALLOCATIONS',
            '$integer_outputs(S_pending.EVENTS) = ($ptascii("P;H:2:25:Array to string conversion:1;"))',
            '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
        ]
        step('S_throw', 'S_pending')
        checks += [
            '$cast_owned_frontier(S_throw, 6)',
            'S_throw.TODO = (THROW_SEARCH n_exception) :: ptask_caller*',
            '$lookup(S_throw.ENV, $ptascii("a")) = eps',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_a) = 0',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HARRAY n_array) = 0',
            '~((HARRAY n_array) <- S_throw.ALLOCATIONS)',
            'S_throw.STORE[n_v] = DEFINED pvalue_old',
            'S_throw.STORE[n_made] = DEFINED (PINT 1)',
            'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
            '$lookup(S_throw.ENV, $ptascii("second")) = (n_second)',
            'S_throw.STORE[n_second] = DEFINED (POBJECT n_exception)',
            '$throwable_live(S_throw, n_exception)',
            '$throwable_previous_id(S_throw, n_exception) = eps',
            '$throwable_field(S_throw, n_exception, "line") = PINT 20',
            '$task_nodes(THROW_SEARCH n_exception) = [HOBJECT n_exception]',
            '$integer_outputs(S_throw.EVENTS) = ($ptascii("P;H:2:25:Array to string conversion:1;"))',
            '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
            'S_done = $drive_steps(S_throw, 4000)',
        ]
    else:
        seek('S_return', 'S_entered', 4)
        checks += [
            'S_return.TODO = (CAST_OWNED_ARRAY_WARNING pcastownedarraywarning 1) :: ptask_tail*',
            '$lookup(S_return.ENV, $ptascii("a")) = eps',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_a) = 0',
            '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_array) = 1',
            '(HARRAY n_array) <- S_return.ALLOCATIONS',
            'S_return.STORE[n_v] = DEFINED pvalue_old',
            'S_return.STORE[n_calls] = DEFINED (PINT 1)',
            '$cast_owned_array_valid(S_return, pcastownedarraywarning, 1)',
            '$cast_owned_array_snapshot(S_return, pcastownedarraywarning)',
            '(DIAGNOSTIC "Warning" perrorcall.MESSAGE 25) <- S_return.EVENTS',
            '$integer_outputs(S_return.EVENTS) = ($ptascii("P;H:2:25:Array to string conversion:1;"))',
            'S_buffer_return = S_return[.OUTPUTBUFFERS = [{ID S_return.OUTPUTSEQ, HANDLER eps, CHUNK 0, FLAGS 112, SIZE 16384, BYTES eps}]][.OUTPUTSEQ = $(S_return.OUTPUTSEQ + 1)]',
            '$output_state_valid(S_buffer_return)',
            '$cast_owned_array_valid(S_buffer_return, pcastownedarraywarning, 1)',
            'PhpStep: S_buffer_return ~> S_buffer_boundary',
            'S_buffer_boundary.COMPLETION = UNSUPPORTED "owned array string cast buffer changed during Warning"',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        ]
        step('S_result', 'S_return')
        checks += [
            '$cast_owned_frontier(S_result, 5)',
            'S_result.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING $ptascii("Array"))',
            'S_result.TODO = ptask_tail*',
            '$heap_owners($heap_prune($heap_graph(S_result)), HARRAY n_array) = 0',
            '~((HARRAY n_array) <- S_result.ALLOCATIONS)',
            'S_result.STORE[n_v] = DEFINED pvalue_old',
            '$integer_outputs(S_result.EVENTS) = ($ptascii("P;H:2:25:Array to string conversion:1;"))',
            '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
            'S_done = $drive_steps(S_result, 4000)',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
        'S_done.STORE[n_made] = DEFINED (PINT 1)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        'S_done.STORE[n_v] = DEFINED pvalue_done',
        '$string_bytes(pvalue_done) = ($ptascii("' + ('old' if throwing else 'Array') + '"))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks


def main():
    shared.sources, shared.CASES, shared.HELPERS, shared.conditions = cases, CASES, HELPERS, conditions
    return shared.main()


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
