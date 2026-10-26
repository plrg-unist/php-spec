#!/usr/bin/env python3
"""Reached array print conversion, interned output, and pending throw."""
import base64
import json

import integer_operator_warning_protocol as shared
import print_array_warning_cases as cases

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $print_array_handler_frame(pframe) : bool
def $print_array_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = PRINT_ARRAY_WARNING pprintarraywarning 1
  -- if perrorcall.TARGET =/= eps
def $print_array_handler_frame(pframe) = false -- otherwise
dec $print_array_entered(pframe*) : bool
def $print_array_entered(eps) = false
def $print_array_entered(pframe :: pframe_tail*) = ($print_array_handler_frame(pframe) \/ $print_array_entered(pframe_tail*))
dec $print_array_frontier(pstate, nat) : bool
def $print_array_frontier(S, 0) = ($print_array_plan(S) =/= eps)
def $print_array_frontier(S, 1) = true
  -- if S.TODO = (PRINT_ARRAY_WARNING pprintarraywarning 0) :: ptask_tail*
def $print_array_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = PRINT_ARRAY_WARNING pprintarraywarning 1
  -- if perrorcall.TARGET = eps
def $print_array_frontier(S, 3) = (S.CURRENT =/= eps /\ $print_array_entered(S.FRAMES))
def $print_array_frontier(S, 4) = true
  -- if S.TODO = (PRINT_ARRAY_WARNING pprintarraywarning 1) :: ptask_tail*
def $print_array_frontier(S, 5) = true
  -- if S.TODO = (PRINT_EMIT porigin z) :: ptask_tail*
  -- if S.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING $ptascii("Array"))
def $print_array_frontier(S, 6) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if $integer_outputs(S.EVENTS) = ($ptascii("H:2:24:Array to string conversion:1;Array"))
def $print_array_frontier(S, n) = false -- otherwise
dec $print_array_seek(pstate, nat, nat) : pstate
def $print_array_seek(S, n_stage, n) = S -- if $print_array_frontier(S, n_stage)
def $print_array_seek(S, n_stage, n) = S
  -- if ~$print_array_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $print_array_seek(S, n_stage, n) = S
  -- if ~$print_array_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $print_array_seek(S, n_stage, n) = $print_array_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$print_array_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    throwing = name == 'print-array-pending-throw'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(label, start, stage):
        checks.extend([f'{label}_found = $print_array_seek({start}, {stage}, 4000)',
                       f'{label}_found.COMPLETION = NORMAL \\/ {label}_found.COMPLETION = BUDGET',
                       f'{label} = {label}_found[.COMPLETION = NORMAL]',
                       f'$print_array_frontier({label}, {stage})'])

    def step(label, start):
        checks.extend([f'{label}_budget = $drive_steps({start}, 1)',
                       f'{label}_budget.COMPLETION = BUDGET',
                       f'{label} = {label}_budget[.COMPLETION = NORMAL]'])

    seek('S_entry', 'S_initial', 0)
    checks += [
        'S_entry.TODO = (PRINT_EMIT porigin_print 24) :: ptask_tail*',
        'S_entry.ORIGIN = (porigin_print)',
        'S_entry.OUTPUTBUFFERS = eps',
        '$print_array_plan(S_entry) = (pprintarraywarning)',
        'pprintarraywarning.SITE = porigin_print',
        'pprintarraywarning.LINE = 24',
        'pprintarraywarning.INPUT = VARIABLE ($ptascii("a")) 24',
        '$print_task_valid(S_entry, porigin_print, 24)',
        '$integer_operand_source(S_entry, porigin_print, [PCFIELD 0], pprintarraywarning.INPUT)',
        '$print_array_source(S_entry, pprintarraywarning)',
        '$array_string_cast_snapshot(S_entry, pprintarraywarning.INPUT)',
        '$lookup(S_entry.ENV, $ptascii("a")) = (n_a)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        'S_entry.STORE[n_a] = DEFINED (PARRAY n_array)',
        'S_entry.ARRAYS[n_array].ITEMS =/= eps',
        '$array_string_cast_items(S_entry.ARRAYS[n_array].ITEMS)',
        '(HARRAY n_array) <- S_entry.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_array) = 1',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_a) = 1',
        '$print_array_plan(S_entry[.ORIGIN = eps]) = eps',
        '$print_array_plan(S_entry[.CODE = eps]) = eps',
        '$print_array_plan(S_entry[.RESULT = KNOWN (PARRAY n_array)]) = eps',
        '$print_array_plan(S_entry[.STORE[n_a] = DEFINED (PINT 99)]) = eps',
        '~$print_array_source(S_entry, pprintarraywarning[.LINE = 23])',
        '~$print_array_source(S_entry, pprintarraywarning[.INPUT = VARIABLE ($ptascii("v")) 24])',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'S_entry.TODO = ptask_old :: ptask_tail*',
        'PhpStep: S_entry ~> S_begin_raw',
        'S_begin_raw = S_entry[.TODO = (PRINT_ARRAY_WARNING pprintarraywarning 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture = S_begin_raw',
        'S_capture.TODO = (PRINT_ARRAY_WARNING pprintarraywarning 0) :: ptask_tail*',
        '$print_array_valid(S_capture, pprintarraywarning, 0)',
        '$task_nodes(PRINT_ARRAY_WARNING pprintarraywarning 0) = eps',
        '$integer_outputs(S_capture.EVENTS) = eps',
        'S_capture.STORE = S_entry.STORE',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
        'S_buffer_capture = S_capture[.OUTPUTBUFFERS = [{ID S_capture.OUTPUTSEQ, HANDLER eps, CHUNK 0, FLAGS 112, SIZE 16384, BYTES eps}]][.OUTPUTSEQ = $(S_capture.OUTPUTSEQ + 1)]',
        '$output_state_valid(S_buffer_capture)',
        '$print_array_source(S_buffer_capture, pprintarraywarning)',
        '$array_string_cast_snapshot(S_buffer_capture, pprintarraywarning.INPUT)',
        '~$print_array_valid(S_buffer_capture, pprintarraywarning, 0)',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = PRINT_ARRAY_WARNING pprintarraywarning 1',
        'perrorcall.TARGET = eps',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = 24',
        'perrorcall.MESSAGE = $ptascii("Array to string conversion")',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 8192])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = 23])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        '$print_array_handler_frame(pframe)',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_saved*',
        'perrorcall_entered.RESUME = PRINT_ARRAY_WARNING pprintarraywarning 1',
        'perrorcall_entered.TARGET =/= eps',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if throwing:
        seek('S_throw', 'S_entered', 6)
        checks += [
            'S_throw.TODO = (THROW_SEARCH n_exception) :: ptask_caller*',
            '$lookup(S_throw.ENV, $ptascii("a")) = eps',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_a) = 0',
            '~((HCELL n_a) <- S_throw.ALLOCATIONS)',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HARRAY n_array) = 0',
            '~((HARRAY n_array) <- S_throw.ALLOCATIONS)',
            'S_throw.STORE[n_v] = DEFINED (PINT 100)',
            'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
            '$lookup(S_throw.ENV, $ptascii("second")) = (n_second_cell)',
            'S_throw.STORE[n_second_cell] = DEFINED (POBJECT n_exception)',
            '$task_nodes(THROW_SEARCH n_exception) = [HOBJECT n_exception]',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_exception) = 2',
            '$throwable_live(S_throw, n_exception)',
            '$throwable_previous_id(S_throw, n_exception) = eps',
            '$throwable_field(S_throw, n_exception, "line") = PINT 20',
            '$integer_outputs(S_throw.EVENTS) = ($ptascii("H:2:24:Array to string conversion:1;Array"))',
            'S_buffer_throw = S_throw[.ORIGIN = (pprintarraywarning.SITE)][.OUTPUTBUFFERS = [{ID S_throw.OUTPUTSEQ, HANDLER eps, CHUNK 0, FLAGS 112, SIZE 16384, BYTES eps}]][.OUTPUTSEQ = $(S_throw.OUTPUTSEQ + 1)]',
            '$output_state_valid(S_buffer_throw)',
            '$print_array_valid(S_buffer_throw, pprintarraywarning, 1)',
            'S_buffer_discard = $error_read_discard(S_buffer_throw, PRINT_ARRAY_WARNING pprintarraywarning 1)',
            'S_buffer_discard.COMPLETION = UNSUPPORTED "print array output buffer changed during Warning"',
            '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
            'S_done = $drive_steps(S_throw, 4000)',
        ]
    else:
        seek('S_return', 'S_entered', 4)
        checks += [
            'S_return.TODO = (PRINT_ARRAY_WARNING pprintarraywarning 1) :: ptask_tail*',
            '$lookup(S_return.ENV, $ptascii("a")) = eps',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_a) = 0',
            '~((HCELL n_a) <- S_return.ALLOCATIONS)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_array) = 0',
            '~((HARRAY n_array) <- S_return.ALLOCATIONS)',
            'S_return.STORE[n_v] = DEFINED (PINT 100)',
            'S_return.STORE[n_calls] = DEFINED (PINT 1)',
            '$print_array_valid(S_return, pprintarraywarning, 1)',
            '~$array_string_cast_snapshot(S_return, pprintarraywarning.INPUT)',
            'S_buffer_return = S_return[.OUTPUTBUFFERS = [{ID S_return.OUTPUTSEQ, HANDLER eps, CHUNK 0, FLAGS 112, SIZE 16384, BYTES eps}]][.OUTPUTSEQ = $(S_return.OUTPUTSEQ + 1)]',
            '$output_state_valid(S_buffer_return)',
            '$print_array_valid(S_buffer_return, pprintarraywarning, 1)',
            'PhpStep: S_buffer_return ~> S_buffer_boundary',
            'S_buffer_boundary.COMPLETION = UNSUPPORTED "print array output buffer changed during Warning"',
            '$integer_outputs(S_return.EVENTS) = ($ptascii("H:2:24:Array to string conversion:1;"))',
            '(DIAGNOSTIC "Warning" perrorcall.MESSAGE 24) <- S_return.EVENTS',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
            'PhpStep: S_return ~> S_cached_raw',
            'S_cached_raw = S_return[.TODO = (PRINT_EMIT pprintarraywarning.SITE pprintarraywarning.LINE) :: ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING $ptascii("Array"))][.BASE = BASE_VALUE (KNOWN (PSTRING_CARRIER INTERNED_STRING $ptascii("Array")))]',
        ]
        step('S_cached', 'S_return')
        checks += [
            'S_cached = S_cached_raw',
            '$print_array_frontier(S_cached, 5)',
            'S_cached.STORE[n_v] = DEFINED (PINT 100)',
            '$integer_outputs(S_cached.EVENTS) = ($ptascii("H:2:24:Array to string conversion:1;"))',
            '$call_descriptors_valid(S_cached)', '$heap_valid($heap_graph(S_cached))',
        ]
        step('S_printed', 'S_cached')
        checks += [
            'S_printed.RESULT = KNOWN (PINT 1)',
            'S_printed.STORE[n_v] = DEFINED (PINT 100)',
            '$integer_outputs(S_printed.EVENTS) = ($ptascii("H:2:24:Array to string conversion:1;Array"))',
            '$call_descriptors_valid(S_printed)', '$heap_valid($heap_graph(S_printed))',
            'S_done = $drive_steps(S_printed, 4000)',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        'S_done.STORE[n_v] = DEFINED (PINT ' + ('100' if throwing else '1') + ')',
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
