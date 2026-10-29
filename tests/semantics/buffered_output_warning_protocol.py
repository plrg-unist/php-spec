#!/usr/bin/env python3
"""Reached default-buffer capture across print, echo, and NaN warnings."""
import base64
import json

import buffered_output_warning_cases as cases
import integer_operator_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $buffer_warning_task(ptask, nat) : bool
def $buffer_warning_task(PRINT_ARRAY_WARNING pprintarraywarning n, n) = true
def $buffer_warning_task(PRINT_NAN_WARNING pprintnanwarning n, n) = true
def $buffer_warning_task(ECHO_ARRAY_WARNING pechoarraywarning n, n) = true
def $buffer_warning_task(ptask, n) = false -- otherwise
dec $buffer_warning_frontier(pstate, nat) : bool
def $buffer_warning_frontier(S, 0) = ($print_array_plan(S) =/= eps \/ $print_nan_plan(S) =/= eps \/ $echo_array_plan(S) =/= eps)
def $buffer_warning_frontier(S, 1) = true
  -- if S.TODO = ptask :: ptask_tail*
  -- if $buffer_warning_task(ptask, 0)
def $buffer_warning_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if $buffer_warning_task(perrorcall.RESUME, 1)
def $buffer_warning_frontier(S, 3) = true
  -- if S.TODO = ptask :: ptask_tail*
  -- if $buffer_warning_task(ptask, 1)
def $buffer_warning_frontier(S, 4) = true
  -- if S.TODO = (PRINT_EMIT porigin z) :: ptask_tail*
  -- if S.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING $ptascii("Array"))
def $buffer_warning_frontier(S, 4) = true
  -- if S.TODO = (PRINT_EMIT porigin z) :: ptask_tail*
  -- if S.RESULT = KNOWN (PSTRING $ptascii("NAN"))
def $buffer_warning_frontier(S, 4) = true
  -- if S.TODO = (EMIT z) :: ptask_tail*
  -- if S.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING $ptascii("Array"))
def $buffer_warning_frontier(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if S.OUTPUTBUFFERS = poutputbuffer :: eps
  -- if poutputbuffer.BYTES = $ptascii("I;Array")
def $buffer_warning_frontier(S, n) = false -- otherwise
dec $buffer_warning_seek(pstate, nat, nat) : pstate
def $buffer_warning_seek(S, n_stage, n) = S -- if $buffer_warning_frontier(S, n_stage)
def $buffer_warning_seek(S, n_stage, n) = S
  -- if ~$buffer_warning_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $buffer_warning_seek(S, n_stage, n) = S
  -- if ~$buffer_warning_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $buffer_warning_seek(S, n_stage, n) = $buffer_warning_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$buffer_warning_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    throwing = name.endswith('pending-throw')
    echo = name.startswith('echo-')
    nan = name.startswith('print-nan-')
    warning = 'pprintnanwarning' if nan else ('pechoarraywarning' if echo else 'pprintarraywarning')
    plan = '$print_nan_plan' if nan else ('$echo_array_plan' if echo else '$print_array_plan')
    valid = '$print_nan_valid' if nan else ('$echo_array_valid' if echo else '$print_array_valid')
    source = '$print_nan_source' if nan else ('$echo_array_source' if echo else '$print_array_source')
    task = ('PRINT_NAN_WARNING' if nan else ('ECHO_ARRAY_WARNING' if echo else 'PRINT_ARRAY_WARNING'))
    cached = 'NAN' if nan else 'Array'
    message = 'unexpected NAN value was coerced to string' if nan else 'Array to string conversion'
    output = 'H:2:24:' + message + ':1;'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(label, start, stage):
        checks.extend([f'{label}_found = $buffer_warning_seek({start}, {stage}, 5000)',
                       f'{label}_found.COMPLETION = NORMAL \\/ {label}_found.COMPLETION = BUDGET',
                       f'{label} = {label}_found[.COMPLETION = NORMAL]',
                       f'$buffer_warning_frontier({label}, {stage})'])

    def step(label, start):
        checks.extend([f'{label}_budget = $drive_steps({start}, 1)',
                       f'{label}_budget.COMPLETION = BUDGET',
                       f'{label} = {label}_budget[.COMPLETION = NORMAL]'])

    seek('S_entry', 'S_initial', 0)
    checks += [
        'S_entry.OUTPUTBUFFERS = eps',
        f'{plan}(S_entry) = ({warning})',
        f'{warning}.BUFFERSEQ = S_entry.OUTPUTSEQ',
        f'{warning}.LINE = 24',
        f'{warning}.INPUT = VARIABLE ($ptascii("a")) 24',
        f'{source}(S_entry, {warning})',
        '$lookup(S_entry.ENV, $ptascii("a")) = (n_a)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("later_calls")) = (n_later)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        'S_entry.STORE[n_later] = DEFINED (PINT 0)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '$warning_output_buffer(S_entry, S_entry.OUTPUTSEQ)',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
    ]
    if nan:
        checks += [f'{warning}.BITS = 9221120237041090560',
                   f'{warning}.TEXT = $ptascii("NAN")',
                   'S_entry.STORE[n_a] = DEFINED (PFLOAT 9221120237041090560)',
                   f'$print_nan_snapshot(S_entry, {warning})']
    else:
        checks += ['S_entry.STORE[n_a] = DEFINED (PARRAY n_array)',
                   '(HARRAY n_array) <- S_entry.ALLOCATIONS',
                   '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_array) = 1',
                   f'$array_string_cast_snapshot(S_entry, {warning}.INPUT)']
    if echo:
        checks += [
            'S_entry.TODO = (EMIT 24) :: (ORIGIN_RETURN (porigin_echo)) :: (AT porigin_separator (EVAL expression_separator)) :: (AT porigin_separator (EMIT 25)) :: (AT porigin_later (EVAL expression_later)) :: (AT porigin_later (EMIT 26)) :: ptask_rest*',
            f'{warning}.SITE = porigin_first',
            '$origin_child((porigin_echo), [PCFIELD 0, PCINDEX 0]) = (porigin_first)',
            '$origin_child((porigin_echo), [PCFIELD 0, PCINDEX 1]) = (porigin_separator)',
            '$origin_child((porigin_echo), [PCFIELD 0, PCINDEX 2]) = (porigin_later)',
            '$echo_emit_source(S_entry[.ORIGIN = (porigin_later)], porigin_later, 26)',
        ]
    else:
        checks += ['S_entry.TODO = (PRINT_EMIT porigin_print 24) :: ptask_tail*',
                   f'{warning}.SITE = porigin_print']
    checks += [
        f'{plan}(S_entry[.OUTPUTBUFFERS = [{{ID S_entry.OUTPUTSEQ, HANDLER eps, CHUNK 0, FLAGS 112, SIZE 16384, BYTES eps}}]][.OUTPUTSEQ = $(S_entry.OUTPUTSEQ + 1)]) = eps',
        'PhpStep: S_entry ~> S_begin_raw',
        f'S_begin_raw.TODO = ({task} {warning} 0) :: ptask_begin_tail*',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture = S_begin_raw',
        f'{valid}(S_capture, {warning}, 0)',
        '$integer_outputs(S_capture.EVENTS) = eps',
        'S_capture.OUTPUTBUFFERS = eps',
        f'$warning_output_buffer(S_capture, {warning}.BUFFERSEQ)',
        'S_changed_capture = S_capture[.OUTPUTSEQ = $(S_capture.OUTPUTSEQ + 1)]',
        f'~{valid}(S_changed_capture, {warning}, 0)',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_dispatch_tail*',
        f'perrorcall.RESUME = {task} {warning} 1',
        'perrorcall.LEVEL = 2',
        'perrorcall.LINE = 24',
        f'perrorcall.MESSAGE = $ptascii("{message}")',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
    ]
    if throwing:
        seek('S_throw', 'S_dispatch', 5)
        checks += [
            'S_throw.TODO = (THROW_SEARCH n_exception) :: ptask_throw_tail*',
            'S_throw.OUTPUTBUFFERS = poutputbuffer_throw :: eps',
            f'S_throw.OUTPUTSEQ = $({warning}.BUFFERSEQ + 1)',
            f'poutputbuffer_throw.ID = {warning}.BUFFERSEQ',
            'poutputbuffer_throw.HANDLER = eps', 'poutputbuffer_throw.CHUNK = 0',
            'poutputbuffer_throw.FLAGS = 112',
            'poutputbuffer_throw.BYTES = $ptascii("I;Array")',
            '$output_state_valid(S_throw)',
            f'$warning_output_buffer(S_throw, {warning}.BUFFERSEQ)',
            '$lookup(S_throw.ENV, $ptascii("a")) = eps',
            'S_throw.STORE[n_v] = DEFINED (PINT 100)',
            'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
            'S_throw.STORE[n_later] = DEFINED (PINT 0)',
            '$lookup(S_throw.ENV, $ptascii("second")) = (n_second)',
            'S_throw.STORE[n_second] = DEFINED (POBJECT n_exception)',
            '$throwable_live(S_throw, n_exception)',
            '$throwable_previous_id(S_throw, n_exception) = eps',
            '$throwable_field(S_throw, n_exception, "line") = PINT 20',
            f'$integer_outputs(S_throw.EVENTS) = ($ptascii("{output}"))',
            f'S_before_write = S_throw[.ORIGIN = ({warning}.SITE)][.OUTPUTBUFFERS = [poutputbuffer_throw[.BYTES = $ptascii("I;")]]]',
            f'{valid}(S_before_write, {warning}, 1)',
            f'S_after_write = $error_read_discard(S_before_write, {task} {warning} 1)',
            'S_after_write.OUTPUTBUFFERS = poutputbuffer_after :: eps',
            'poutputbuffer_after.BYTES = $ptascii("I;Array")',
            'S_after_write.TODO = S_before_write.TODO',
            'S_after_write.STORE = S_before_write.STORE',
            'S_after_write.EVENTS = S_before_write.EVENTS',
            f'S_invalid_throw = S_before_write[.OUTPUTBUFFERS = [poutputbuffer_throw[.CHUNK = 8][.BYTES = $ptascii("I;")]]]',
            '$output_state_valid(S_invalid_throw)',
            f'~$warning_output_buffer(S_invalid_throw, {warning}.BUFFERSEQ)',
            f'S_refused_throw = $error_read_discard(S_invalid_throw, {task} {warning} 1)',
            f'S_refused_throw.COMPLETION = UNSUPPORTED "{"echo" if echo else "print"} array output buffer changed during Warning"',
            '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
            'S_done = $drive_steps(S_throw, 5000)',
        ]
        checks += ['$heap_owners($heap_prune($heap_graph(S_throw)), HARRAY n_array) = 0',
                   '~((HARRAY n_array) <- S_throw.ALLOCATIONS)']
    else:
        seek('S_return', 'S_dispatch', 3)
        checks += [
            f'S_return.TODO = ({task} {warning} 1) :: ptask_return_tail*',
            'S_return.OUTPUTBUFFERS = poutputbuffer_return :: eps',
            f'S_return.OUTPUTSEQ = $({warning}.BUFFERSEQ + 1)',
            f'poutputbuffer_return.ID = {warning}.BUFFERSEQ',
            'poutputbuffer_return.HANDLER = eps', 'poutputbuffer_return.CHUNK = 0',
            'poutputbuffer_return.FLAGS = 112',
            'poutputbuffer_return.BYTES = $ptascii("I;")',
            '$output_state_valid(S_return)',
            f'$warning_output_buffer(S_return, {warning}.BUFFERSEQ)',
            f'{valid}(S_return, {warning}, 1)',
            '$lookup(S_return.ENV, $ptascii("a")) = eps',
            'S_return.STORE[n_v] = DEFINED (PINT 100)',
            'S_return.STORE[n_calls] = DEFINED (PINT 1)',
            'S_return.STORE[n_later] = DEFINED (PINT 0)',
            f'$integer_outputs(S_return.EVENTS) = ($ptascii("{output}"))',
            '(DIAGNOSTIC "Warning" perrorcall.MESSAGE 24) <- S_return.EVENTS',
            'S_nested = S_return[.OUTPUTBUFFERS = [{ID S_return.OUTPUTSEQ, HANDLER eps, CHUNK 0, FLAGS 112, SIZE 16384, BYTES eps}, poutputbuffer_return]][.OUTPUTSEQ = $(S_return.OUTPUTSEQ + 1)]',
            '$output_state_valid(S_nested)',
            f'~$warning_output_buffer(S_nested, {warning}.BUFFERSEQ)',
            'PhpStep: S_nested ~> S_refused',
            f'S_refused.COMPLETION = UNSUPPORTED "{"echo" if echo else "print"} {"NaN" if nan else "array"} output buffer changed during Warning"',
            'S_reopened = S_return[.OUTPUTBUFFERS = [{ID S_return.OUTPUTSEQ, HANDLER eps, CHUNK 0, FLAGS 112, SIZE 16384, BYTES $ptascii("I;")}]][.OUTPUTSEQ = $(S_return.OUTPUTSEQ + 1)]',
            '$output_state_valid(S_reopened)',
            f'~$warning_output_buffer(S_reopened, {warning}.BUFFERSEQ)',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        ]
        if nan:
            checks += [f'~$print_nan_snapshot(S_return, {warning})']
        else:
            checks += [f'~$array_string_cast_snapshot(S_return, {warning}.INPUT)',
                       '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_array) = 0',
                       '~((HARRAY n_array) <- S_return.ALLOCATIONS)']
        seek('S_cached', 'S_return', 4)
        checks += [
            'S_cached.OUTPUTBUFFERS = poutputbuffer_cached :: eps',
            'poutputbuffer_cached.BYTES = $ptascii("I;")',
            f'$integer_outputs(S_cached.EVENTS) = ($ptascii("{output}"))',
            '$call_descriptors_valid(S_cached)', '$heap_valid($heap_graph(S_cached))',
        ]
        step('S_written', 'S_cached')
        checks += [
            'S_written.OUTPUTBUFFERS = poutputbuffer_written :: eps',
            f'poutputbuffer_written.BYTES = $ptascii("I;{cached}")',
            f'$integer_outputs(S_written.EVENTS) = ($ptascii("{output}"))',
            'S_written.STORE[n_later] = DEFINED (PINT 0)',
            '$call_descriptors_valid(S_written)', '$heap_valid($heap_graph(S_written))',
            'S_done = $drive_steps(S_written, 5000)',
        ]
        if echo:
            checks += [
                'S_written.TODO = (ORIGIN_RETURN (porigin_echo)) :: (AT porigin_separator (EVAL expression_separator)) :: (AT porigin_separator (EMIT 25)) :: (AT porigin_later (EVAL expression_later)) :: (AT porigin_later (EMIT 26)) :: ptask_rest*',
                'S_written.RESULT = KNOWN PNULL',
                'S_written.STORE[n_v] = DEFINED (PINT 100)',
            ]
        else:
            checks += [
                'S_written.RESULT = KNOWN (PINT 1)',
                'S_written.STORE[n_v] = DEFINED (PINT 100)',
            ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
        'S_done.OUTPUTBUFFERS = eps',
        f'S_done.OUTPUTSEQ = $({warning}.BUFFERSEQ + 1)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        'S_done.STORE[n_later] = DEFINED (PINT ' + ('1' if echo and not throwing else '0') + ')',
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
