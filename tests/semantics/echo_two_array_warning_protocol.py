#!/usr/bin/env python3
"""Reach two echo array warnings with live second-CV selection and retirement."""
import base64
import json

import integer_operator_warning_protocol as shared
import echo_two_array_warning_cases as cases

CASES = ('echo-two-arrays-both-default', 'echo-two-arrays-second-throw')
HELPERS = shared.HELPERS + r'''
dec $echo_array_handler_frame(pframe) : bool
def $echo_array_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ECHO_ARRAY_WARNING pechoarraywarning 1
  -- if perrorcall.TARGET =/= eps
def $echo_array_handler_frame(pframe) = false -- otherwise
dec $echo_array_entered(pframe*) : bool
def $echo_array_entered(eps) = false
def $echo_array_entered(pframe :: pframe_tail*) = ($echo_array_handler_frame(pframe) \/ $echo_array_entered(pframe_tail*))
dec $echo_array_frontier(pstate, nat) : bool
def $echo_array_frontier(S, 0) = true
  -- if S.TODO = (EMIT 32) :: ptask_tail*
  -- if $echo_array_plan(S) =/= eps
def $echo_array_frontier(S, 7) = true
  -- if S.TODO = (EMIT 33) :: ptask_tail*
  -- if $echo_array_plan(S) =/= eps
def $echo_array_frontier(S, 1) = true
  -- if S.TODO = (ECHO_ARRAY_WARNING pechoarraywarning 0) :: ptask_tail*
def $echo_array_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ECHO_ARRAY_WARNING pechoarraywarning 1
  -- if perrorcall.TARGET = eps
def $echo_array_frontier(S, 3) = (S.CURRENT =/= eps /\ $echo_array_entered(S.FRAMES))
def $echo_array_frontier(S, 4) = true
  -- if S.TODO = (ECHO_ARRAY_WARNING pechoarraywarning 1) :: ptask_tail*
def $echo_array_frontier(S, 5) = true
  -- if S.TODO = (EMIT z) :: ptask_tail*
  -- if S.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING $ptascii("Array"))
def $echo_array_frontier(S, 6) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if $integer_outputs(S.EVENTS) = ($ptascii("H:1:2:32:Array to string conversion:1;ArrayH:2:2:33:Array to string conversion:1;Array"))
def $echo_array_frontier(S, n) = false -- otherwise
dec $echo_array_seek(pstate, nat, nat) : pstate
def $echo_array_seek(S, n_stage, n) = S -- if $echo_array_frontier(S, n_stage)
def $echo_array_seek(S, n_stage, n) = S
  -- if ~$echo_array_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $echo_array_seek(S, n_stage, n) = S
  -- if ~$echo_array_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $echo_array_seek(S, n_stage, n) = $echo_array_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$echo_array_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


FIRST = 'H:1:2:32:Array to string conversion:1;Array'
SECOND_HANDLER = FIRST + 'H:2:2:33:Array to string conversion:1;'
SECOND_OUTPUT = SECOND_HANDLER + 'Array'


def conditions(name, program, path, stdout):
    throwing = name.endswith('second-throw')
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(label, start, stage):
        checks.extend([f'{label}_found = $echo_array_seek({start}, {stage}, 4000)',
                       f'{label}_found.COMPLETION = NORMAL \\/ {label}_found.COMPLETION = BUDGET',
                       f'{label} = {label}_found[.COMPLETION = NORMAL]',
                       f'$echo_array_frontier({label}, {stage})'])

    def step(label, start):
        checks.extend([f'{label}_budget = $drive_steps({start}, 1)',
                       f'{label}_budget.COMPLETION = BUDGET',
                       f'{label} = {label}_budget[.COMPLETION = NORMAL]'])

    seek('S_first_entry', 'S_initial', 0)
    checks += [
        'S_first_entry.TODO = (EMIT 32) :: ptask_first_tail*',
        'S_first_entry.ORIGIN = (porigin_first)',
        '$echo_array_plan(S_first_entry) = (pechoarraywarning_first)',
        'pechoarraywarning_first.SITE = porigin_first',
        'pechoarraywarning_first.LINE = 32',
        'pechoarraywarning_first.INPUT = VARIABLE ($ptascii("a")) 32',
        '$echo_array_source(S_first_entry, pechoarraywarning_first)',
        '$lookup(S_first_entry.ENV, $ptascii("a")) = (n_a)',
        '$lookup(S_first_entry.ENV, $ptascii("b")) = (n_b)',
        '$lookup(S_first_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_first_entry.ENV, $ptascii("later_calls")) = (n_later_calls)',
        'S_first_entry.STORE[n_a] = DEFINED (PARRAY n_array_a)',
        'S_first_entry.STORE[n_b] = DEFINED (PINT 7)',
        'S_first_entry.STORE[n_calls] = DEFINED (PINT 0)',
        'S_first_entry.STORE[n_later_calls] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_first_entry)), HARRAY n_array_a) = 2',
        '$heap_owners($heap_prune($heap_graph(S_first_entry[.POOLS = eps])), HARRAY n_array_a) = 1',
        '$call_descriptors_valid(S_first_entry)', '$heap_valid($heap_graph(S_first_entry))',
    ]
    seek('S_entry', 'S_first_entry', 7)
    checks += [
        'S_entry.TODO = (EMIT 33) :: (ORIGIN_RETURN (porigin_echo)) :: (AT porigin_separator (EVAL expression_separator)) :: (AT porigin_separator (EMIT 34)) :: (AT porigin_later (EVAL expression_later)) :: (AT porigin_later (EMIT 35)) :: ptask_rest*',
        'S_entry.ORIGIN = (porigin_second)',
        '$origin_child((porigin_echo), [PCFIELD 0, PCINDEX 0]) = (porigin_first)',
        '$origin_child((porigin_echo), [PCFIELD 0, PCINDEX 1]) = (porigin_second)',
        '$origin_child((porigin_echo), [PCFIELD 0, PCINDEX 2]) = (porigin_separator)',
        '$origin_child((porigin_echo), [PCFIELD 0, PCINDEX 3]) = (porigin_later)',
        '$echo_array_plan(S_entry) = (pechoarraywarning)',
        'pechoarraywarning.SITE = porigin_second',
        'pechoarraywarning.LINE = 33',
        'pechoarraywarning.INPUT = VARIABLE ($ptascii("b")) 33',
        '$echo_emit_source(S_entry, porigin_second, 33)',
        '$integer_operand_source(S_entry, porigin_second, eps, pechoarraywarning.INPUT)',
        '$echo_array_source(S_entry, pechoarraywarning)',
        '$origin_node(S_entry.SOURCES, porigin_separator) = (expression_separator)',
        '$origin_node(S_entry.SOURCES, porigin_later) = (expression_later)',
        '$echo_emit_source(S_entry[.ORIGIN = (porigin_separator)], porigin_separator, 34)',
        '$echo_emit_source(S_entry[.ORIGIN = (porigin_later)], porigin_later, 35)',
        'S_entry.OUTPUTBUFFERS = eps',
        '$lookup(S_entry.ENV, $ptascii("a")) = eps',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_a) = 0',
        '~((HCELL n_a) <- S_entry.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_array_a) = 1',
        '$heap_owners($heap_prune($heap_graph(S_entry[.POOLS = eps])), HARRAY n_array_a) = 0',
        '(HARRAY n_array_a) <- S_entry.ALLOCATIONS',
        '$lookup(S_entry.ENV, $ptascii("b")) = (n_b)',
        'S_entry.STORE[n_b] = DEFINED (PARRAY n_array_b)',
        'S_entry.ARRAYS[n_array_b].ITEMS =/= eps',
        '$array_string_cast_items(S_entry.ARRAYS[n_array_b].ITEMS)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_array_b) = 1',
        '$heap_owners($heap_prune($heap_graph(S_entry[.POOLS = eps])), HARRAY n_array_b) = 1',
        '(HARRAY n_array_b) <- S_entry.ALLOCATIONS',
        '$array_string_cast_snapshot(S_entry, pechoarraywarning.INPUT)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 1)',
        'S_entry.STORE[n_later_calls] = DEFINED (PINT 0)',
        '$integer_outputs(S_entry.EVENTS) = ($ptascii("' + FIRST + '"))',
        '(DIAGNOSTIC "Warning" ($ptascii("Array to string conversion")) 32) <- S_entry.EVENTS',
        '$echo_array_plan(S_entry[.ORIGIN = (porigin_first)]) = eps',
        '$echo_array_plan(S_entry[.STORE[n_b] = DEFINED (PINT 7)]) = eps',
        '~$echo_array_source(S_entry, pechoarraywarning[.LINE = 32])',
        '~$echo_array_source(S_entry, pechoarraywarning[.SITE = porigin_first])',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'S_entry.TODO = ptask_old :: ptask_tail*',
        'PhpStep: S_entry ~> S_begin_raw',
        'S_begin_raw = S_entry[.TODO = (ECHO_ARRAY_WARNING pechoarraywarning 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture = S_begin_raw',
        '$echo_array_valid(S_capture, pechoarraywarning, 0)',
        '$task_nodes(ECHO_ARRAY_WARNING pechoarraywarning 0) = eps',
        '$integer_outputs(S_capture.EVENTS) = ($ptascii("' + FIRST + '"))',
        'S_capture.STORE = S_entry.STORE',
        'S_buffer_capture = S_capture[.OUTPUTBUFFERS = [{ID S_capture.OUTPUTSEQ, HANDLER eps, CHUNK 0, FLAGS 112, SIZE 16384, BYTES eps}]][.OUTPUTSEQ = $(S_capture.OUTPUTSEQ + 1)]',
        '$output_state_valid(S_buffer_capture)',
        '~$echo_array_valid(S_buffer_capture, pechoarraywarning, 0)',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ECHO_ARRAY_WARNING pechoarraywarning 1',
        'perrorcall.TARGET = eps',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = 33',
        'perrorcall.MESSAGE = $ptascii("Array to string conversion")',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = 32])',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        '$echo_array_handler_frame(pframe)',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_saved*',
        'perrorcall_entered.RESUME = ECHO_ARRAY_WARNING pechoarraywarning 1',
        'perrorcall_entered.TARGET =/= eps',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if throwing:
        seek('S_throw', 'S_entered', 6)
        checks += [
            'S_throw.TODO = (THROW_SEARCH n_exception) :: ptask_caller*',
            '$lookup(S_throw.ENV, $ptascii("b")) = eps',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_b) = 0',
            '~((HCELL n_b) <- S_throw.ALLOCATIONS)',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HARRAY n_array_b) = 0',
            '~((HARRAY n_array_b) <- S_throw.ALLOCATIONS)',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HARRAY n_array_a) = 1',
            'S_throw.STORE[n_calls] = DEFINED (PINT 2)',
            'S_throw.STORE[n_later_calls] = DEFINED (PINT 0)',
            '$lookup(S_throw.ENV, $ptascii("second")) = (n_second_cell)',
            'S_throw.STORE[n_second_cell] = DEFINED (POBJECT n_exception)',
            '$task_nodes(THROW_SEARCH n_exception) = [HOBJECT n_exception]',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_exception) = 2',
            '$throwable_live(S_throw, n_exception)',
            '$throwable_previous_id(S_throw, n_exception) = eps',
            '$throwable_field(S_throw, n_exception, "line") = PINT 28',
            '$integer_outputs(S_throw.EVENTS) = ($ptascii("' + SECOND_OUTPUT + '"))',
            'S_buffer_throw = S_throw[.ORIGIN = (pechoarraywarning.SITE)][.OUTPUTBUFFERS = [{ID S_throw.OUTPUTSEQ, HANDLER eps, CHUNK 1, FLAGS 112, SIZE 16384, BYTES eps}]][.OUTPUTSEQ = $(S_throw.OUTPUTSEQ + 1)]',
            '$output_state_valid(S_buffer_throw)',
            '$echo_array_valid(S_buffer_throw, pechoarraywarning, 1)',
            'S_buffer_discard = $error_read_discard(S_buffer_throw, ECHO_ARRAY_WARNING pechoarraywarning 1)',
            'S_buffer_discard.COMPLETION = UNSUPPORTED "echo array output buffer changed during Warning"',
            '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
            'S_done = $drive_steps(S_throw, 4000)',
        ]
    else:
        seek('S_return', 'S_entered', 4)
        checks += [
            'S_return.TODO = (ECHO_ARRAY_WARNING pechoarraywarning 1) :: ptask_tail*',
            '$lookup(S_return.ENV, $ptascii("b")) = eps',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_b) = 0',
            '~((HCELL n_b) <- S_return.ALLOCATIONS)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_array_b) = 0',
            '~((HARRAY n_array_b) <- S_return.ALLOCATIONS)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_array_a) = 1',
            'S_return.STORE[n_calls] = DEFINED (PINT 2)',
            'S_return.STORE[n_later_calls] = DEFINED (PINT 0)',
            '$echo_array_valid(S_return, pechoarraywarning, 1)',
            '~$array_string_cast_snapshot(S_return, pechoarraywarning.INPUT)',
            '$integer_outputs(S_return.EVENTS) = ($ptascii("' + SECOND_HANDLER + '"))',
            '(DIAGNOSTIC "Warning" ($ptascii("Array to string conversion")) 33) <- S_return.EVENTS',
            'S_buffer_return = S_return[.OUTPUTBUFFERS = [{ID S_return.OUTPUTSEQ, HANDLER eps, CHUNK 1, FLAGS 112, SIZE 16384, BYTES eps}]][.OUTPUTSEQ = $(S_return.OUTPUTSEQ + 1)]',
            '$output_state_valid(S_buffer_return)',
            '$echo_array_valid(S_buffer_return, pechoarraywarning, 1)',
            'PhpStep: S_buffer_return ~> S_buffer_boundary',
            'S_buffer_boundary.COMPLETION = UNSUPPORTED "echo array output buffer changed during Warning"',
            'PhpStep: S_return ~> S_cached_raw',
            'S_cached_raw = S_return[.TODO = (EMIT pechoarraywarning.LINE) :: ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING $ptascii("Array"))][.BASE = BASE_VALUE (KNOWN (PSTRING_CARRIER INTERNED_STRING $ptascii("Array")))]',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        ]
        step('S_cached', 'S_return')
        checks += [
            'S_cached = S_cached_raw',
            '$echo_array_frontier(S_cached, 5)',
            'S_cached.STORE[n_later_calls] = DEFINED (PINT 0)',
            '$integer_outputs(S_cached.EVENTS) = ($ptascii("' + SECOND_HANDLER + '"))',
            '$call_descriptors_valid(S_cached)', '$heap_valid($heap_graph(S_cached))',
        ]
        step('S_second_output', 'S_cached')
        checks += [
            'S_second_output.RESULT = KNOWN PNULL',
            'S_second_output.TODO = (ORIGIN_RETURN (porigin_echo)) :: (AT porigin_separator (EVAL expression_separator)) :: (AT porigin_separator (EMIT 34)) :: (AT porigin_later (EVAL expression_later)) :: (AT porigin_later (EMIT 35)) :: ptask_rest*',
            'S_second_output.STORE[n_later_calls] = DEFINED (PINT 0)',
            '$integer_outputs(S_second_output.EVENTS) = ($ptascii("' + SECOND_OUTPUT + '"))',
            '$call_descriptors_valid(S_second_output)', '$heap_valid($heap_graph(S_second_output))',
            'S_done = $drive_steps(S_second_output, 4000)',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
        'S_done.STORE[n_calls] = DEFINED (PINT 2)',
        'S_done.STORE[n_later_calls] = DEFINED (PINT ' + ('0' if throwing else '1') + ')',
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
