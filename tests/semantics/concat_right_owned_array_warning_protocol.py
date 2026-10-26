#!/usr/bin/env python3
"""Reached acquired RIGHT array ownership after an actual LEFT method."""
import base64
import json

import concat_right_owned_array_warning_cases as cases
import integer_operator_warning_protocol as shared

CASES = tuple(name for name in cases.CASES if not name.endswith('scalar-control'))
HELPERS = shared.HELPERS + r'''
dec $concat_right_array_handler_frame(pframe) : bool
def $concat_right_array_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CONCAT_RIGHT_ARRAY_WARNING pconcatrightarraywarning 1
  -- if perrorcall.TARGET =/= eps
def $concat_right_array_handler_frame(pframe) = false -- otherwise
dec $concat_right_array_entered(pframe*) : bool
def $concat_right_array_entered(eps) = false
def $concat_right_array_entered(pframe :: pframe_tail*) = ($concat_right_array_handler_frame(pframe) \/ $concat_right_array_entered(pframe_tail*))
dec $concat_right_array_frontier(pstate, nat) : bool
def $concat_right_array_frontier(S, 0) = ($concat_right_array_plan(S) =/= eps)
def $concat_right_array_frontier(S, 1) = true
  -- if S.TODO = (CONCAT_RIGHT_ARRAY_WARNING pconcatrightarraywarning 0) :: ptask_tail*
def $concat_right_array_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CONCAT_RIGHT_ARRAY_WARNING pconcatrightarraywarning 1
  -- if perrorcall.TARGET = eps
def $concat_right_array_frontier(S, 3) = (S.CURRENT =/= eps /\ $concat_right_array_entered(S.FRAMES))
def $concat_right_array_frontier(S, 4) = true
  -- if S.TODO = (CONCAT_RIGHT_ARRAY_WARNING pconcatrightarraywarning 1) :: ptask_tail*
def $concat_right_array_frontier(S, 5) = true
  -- if S.TODO = (CONCAT_AFTER_RIGHT porigin pvalue_left z) :: (CONCAT_RIGHT_ARRAY_RELEASE pconcatrightarraywarning) :: ptask_tail*
  -- if S.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("Array")))
def $concat_right_array_frontier(S, 6) = true
  -- if S.TODO = (CONCAT_RIGHT_ARRAY_RELEASE pconcatrightarraywarning) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("LArray"))
def $concat_right_array_frontier(S, 7) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CONCAT_RIGHT_ARRAY_WARNING pconcatrightarraywarning 1
def $concat_right_array_frontier(S, 8) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ORIGIN_RETURN porigin) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $concat_right_array_frontier(S, 9) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_object porigin_method
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n_object porigin_left z) :: (CONCAT_AFTER_LEFT porigin_concat (KNOWN (PARRAY n_array)) false z) :: ptask_tail*
def $concat_right_array_frontier(S, n) = false -- otherwise
dec $concat_right_array_seek(pstate, nat, nat) : pstate
def $concat_right_array_seek(S, n_stage, n) = S -- if $concat_right_array_frontier(S, n_stage)
def $concat_right_array_seek(S, n_stage, n) = S
  -- if ~$concat_right_array_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $concat_right_array_seek(S, n_stage, n) = S
  -- if ~$concat_right_array_frontier(S, n_stage)
  -- if S.TODO = eps \/ n = 0
def $concat_right_array_seek(S, n_stage, n) = $concat_right_array_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$concat_right_array_frontier(S, n_stage)
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
        checks.extend([f'{label}_found = $concat_right_array_seek({start}, {stage}, 5000)',
                       f'{label}_found.COMPLETION = NORMAL \\/ {label}_found.COMPLETION = BUDGET',
                       f'{label} = {label}_found[.COMPLETION = NORMAL]',
                       f'$concat_right_array_frontier({label}, {stage})'])

    def step(label, start):
        checks.extend([f'{label}_budget = $drive_steps({start}, 1)',
                       f'{label}_budget.COMPLETION = BUDGET',
                       f'{label} = {label}_budget[.COMPLETION = NORMAL]'])

    seek('S_left_entered', 'S_initial', 9)
    checks += [
        'S_left_entered.CURRENT = (pcallcontext_left)',
        'pcallcontext_left.TARGET = METHOD_TARGET n_old porigin_method',
        'pcallcontext_left.CALLSITE = (porigin_left)',
        'S_left_entered.FRAMES = pframe_left :: pframe_tail*',
        'pframe_left.TODO = (STRINGIFY_RESULT n_old porigin_left 36) :: (CONCAT_AFTER_LEFT porigin_concat (KNOWN (PARRAY n_array)) false 36) :: ptask_tail*',
        'S_left_entered.GLOBALTABLE = (psymboltable_global)',
        '$lookup(psymboltable_global.ENV, $ptascii("a")) = (n_a)',
        '$lookup(psymboltable_global.ENV, $ptascii("left")) = (n_left)',
        '$lookup(psymboltable_global.ENV, $ptascii("other")) = (n_othercell)',
        '$lookup(psymboltable_global.ENV, $ptascii("result")) = (n_result)',
        '$lookup(psymboltable_global.ENV, $ptascii("made")) = (n_made)',
        '$lookup(psymboltable_global.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(psymboltable_global.ENV, $ptascii("left_calls")) = (n_left_calls)',
        '$lookup(psymboltable_global.ENV, $ptascii("other_calls")) = (n_other_calls)',
        'S_left_entered.STORE[n_a] = DEFINED (PARRAY n_array)',
        'S_left_entered.STORE[n_left] = DEFINED (POBJECT n_old)',
        'S_left_entered.STORE[n_othercell] = DEFINED (POBJECT n_other)',
        'S_left_entered.STORE[n_result] = DEFINED pvalue_old',
        '$string_bytes(pvalue_old) = ($ptascii("old"))',
        'S_left_entered.STORE[n_made] = DEFINED (PINT 1)',
        'S_left_entered.STORE[n_calls] = DEFINED (PINT 0)',
        'S_left_entered.STORE[n_left_calls] = DEFINED (PINT 0)',
        'S_left_entered.STORE[n_other_calls] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_left_entered)), HARRAY n_array) = 2',
        '$integer_outputs(S_left_entered.EVENTS) = ($ptascii("P;"))',
        '$call_descriptors_valid(S_left_entered)', '$heap_valid($heap_graph(S_left_entered))',
    ]
    seek('S_entry', 'S_left_entered', 0)
    checks += [
        'S_entry.TODO = (CONCAT_AFTER_LEFT porigin_concat (KNOWN (PARRAY n_array)) false 36) :: ptask_tail*',
        'S_entry.ORIGIN = $origin_child((porigin_concat), [PCFIELD 0])',
        'S_entry.RESULT = KNOWN pvalue_left',
        '$string_bytes(pvalue_left) = ($ptascii("L"))',
        'S_entry.OUTPUTBUFFERS = eps',
        '$concat_right_array_plan(S_entry) = (pconcatrightarraywarning)',
        'pconcatrightarraywarning.SITE = porigin_concat',
        'pconcatrightarraywarning.LINE = 36',
        'pconcatrightarraywarning.ARRAY = n_array',
        'pconcatrightarraywarning.LEFT = pvalue_left',
        '$concat_right_array_source(S_entry, pconcatrightarraywarning)',
        '$concat_right_array_snapshot(S_entry, pconcatrightarraywarning)',
        'S_entry.STORE[n_left] = DEFINED (POBJECT n_other)',
        'S_entry.STORE[n_result] = DEFINED pvalue_old',
        'S_entry.STORE[n_left_calls] = DEFINED (PINT 1)',
        'S_entry.STORE[n_other_calls] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_array) = 2',
        '$integer_outputs(S_entry.EVENTS) = ($ptascii("P;L;"))',
        '$concat_right_array_plan(S_entry[.ORIGIN = eps]) = eps',
        '$concat_right_array_plan(S_entry[.TODO = (CONCAT_AFTER_LEFT porigin_concat (KNOWN (PINT 7)) false 36) :: ptask_tail*]) = eps',
        '~$concat_right_array_source(S_entry, pconcatrightarraywarning[.LINE = 35])',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'S_entry.TODO = ptask_old :: ptask_tail*',
        'PhpStep: S_entry ~> S_begin_raw',
        'S_begin_raw.TODO = (CONCAT_RIGHT_ARRAY_WARNING pconcatrightarraywarning 0) :: ptask_tail*',
    ]
    step('S_begin', 'S_entry')
    checks += [
        'S_begin = S_begin_raw',
        'S_begin.ORIGIN = $origin_child((porigin_concat), [PCFIELD 1])',
        'S_begin.RESULT = KNOWN PNULL',
        '$task_nodes(CONCAT_RIGHT_ARRAY_WARNING pconcatrightarraywarning 0) = [HARRAY n_array] ++ $value_nodes(pvalue_left)',
        '$heap_owners($heap_prune($heap_graph(S_begin)), HARRAY n_array) = 2',
        '$concat_right_array_valid(S_begin, pconcatrightarraywarning, 0)',
        '$call_descriptors_valid(S_begin)', '$heap_valid($heap_graph(S_begin))',
        'S_buffer_begin = S_begin[.OUTPUTBUFFERS = [{ID S_begin.OUTPUTSEQ, HANDLER eps, CHUNK 0, FLAGS 112, SIZE 16384, BYTES eps}]][.OUTPUTSEQ = $(S_begin.OUTPUTSEQ + 1)]',
        '$output_state_valid(S_buffer_begin)',
        '~$concat_right_array_valid(S_buffer_begin, pconcatrightarraywarning, 0)',
    ]
    step('S_dispatch', 'S_begin')
    checks += [
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = CONCAT_RIGHT_ARRAY_WARNING pconcatrightarraywarning 1',
        'perrorcall.TARGET = eps',
        'perrorcall.LINE = 36', 'perrorcall.LEVEL = 2',
        'perrorcall.MESSAGE = $ptascii("Array to string conversion")',
        'perrorcall.SITE = $origin_child((porigin_concat), [PCFIELD 1])',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = 35])',
        '$heap_owners($heap_prune($heap_graph(S_dispatch)), HARRAY n_array) = 2',
        '$integer_outputs(S_dispatch.EVENTS) = ($ptascii("P;L;"))',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
    ]
    seek('S_handler_entered', 'S_dispatch', 3)
    checks += [
        'S_handler_entered.FRAMES = pframe_handler :: pframe_handler_tail*',
        '$concat_right_array_handler_frame(pframe_handler)',
        '$call_descriptors_valid(S_handler_entered)', '$heap_valid($heap_graph(S_handler_entered))',
    ]
    if throwing:
        seek('S_pending', 'S_handler_entered', 7)
        checks += [
            'S_pending.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_pending) :: ptask_pending*',
            'perrorcall_pending.RESUME = CONCAT_RIGHT_ARRAY_WARNING pconcatrightarraywarning 1',
            '$lookup(S_pending.ENV, $ptascii("a")) = eps',
            'S_pending.STORE[n_left] = DEFINED (POBJECT n_other)',
            'S_pending.STORE[n_other_calls] = DEFINED (PINT 0)',
            '$heap_owners($heap_prune($heap_graph(S_pending)), HARRAY n_array) = 1',
            '$integer_outputs(S_pending.EVENTS) = ($ptascii("P;L;H:2:36:Array to string conversion:1;"))',
            '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
        ]
        step('S_throw', 'S_pending')
        checks += [
            '$concat_right_array_frontier(S_throw, 8)',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HARRAY n_array) = 0',
            '~((HARRAY n_array) <- S_throw.ALLOCATIONS)',
            'S_throw.STORE[n_result] = DEFINED pvalue_old',
            'S_throw.STORE[n_left_calls] = DEFINED (PINT 1)',
            'S_throw.STORE[n_other_calls] = DEFINED (PINT 0)',
            '$lookup(S_throw.ENV, $ptascii("second")) = (n_second)',
            'S_throw.STORE[n_second] = DEFINED (POBJECT n_exception)',
            '$throwable_live(S_throw, n_exception)',
            '$throwable_field(S_throw, n_exception, "line") = PINT 33',
            '$integer_outputs(S_throw.EVENTS) = ($ptascii("P;L;H:2:36:Array to string conversion:1;"))',
            '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
            'S_done = $drive_steps(S_throw, 5000)',
        ]
    else:
        seek('S_return', 'S_handler_entered', 4)
        checks += [
            'S_return.TODO = (CONCAT_RIGHT_ARRAY_WARNING pconcatrightarraywarning 1) :: ptask_tail*',
            '$lookup(S_return.ENV, $ptascii("a")) = eps',
            'S_return.STORE[n_left] = DEFINED (POBJECT n_other)',
            'S_return.STORE[n_calls] = DEFINED (PINT 1)',
            'S_return.STORE[n_result] = DEFINED pvalue_old',
            '$concat_right_array_valid(S_return, pconcatrightarraywarning, 1)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_array) = 1',
            '$integer_outputs(S_return.EVENTS) = ($ptascii("P;L;H:2:36:Array to string conversion:1;"))',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
            'S_buffer_return = S_return[.OUTPUTBUFFERS = [{ID S_return.OUTPUTSEQ, HANDLER eps, CHUNK 0, FLAGS 112, SIZE 16384, BYTES eps}]][.OUTPUTSEQ = $(S_return.OUTPUTSEQ + 1)]',
            '$output_state_valid(S_buffer_return)',
            '$concat_right_array_valid(S_buffer_return, pconcatrightarraywarning, 1)',
            'PhpStep: S_buffer_return ~> S_buffer_boundary',
            'S_buffer_boundary.COMPLETION = UNSUPPORTED "concatenation acquired right changed output buffer"',
        ]
        step('S_resume', 'S_return')
        checks += [
            '$concat_right_array_frontier(S_resume, 5)',
            'S_resume.TODO = (CONCAT_AFTER_RIGHT porigin_concat pvalue_left 36) :: (CONCAT_RIGHT_ARRAY_RELEASE pconcatrightarraywarning) :: ptask_tail*',
            'S_resume.ORIGIN = $origin_child((porigin_concat), [PCFIELD 1])',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_array) = 1',
            'S_resume.STORE[n_result] = DEFINED pvalue_old',
            '$integer_outputs(S_resume.EVENTS) = ($ptascii("P;L;H:2:36:Array to string conversion:1;"))',
            '$call_descriptors_valid(S_resume)', '$heap_valid($heap_graph(S_resume))',
        ]
        seek('S_release', 'S_resume', 6)
        checks += [
            'S_release.TODO = (CONCAT_RIGHT_ARRAY_RELEASE pconcatrightarraywarning) :: ptask_tail*',
            'S_release.STORE[n_result] = DEFINED pvalue_old',
            'S_release.STORE[n_left_calls] = DEFINED (PINT 1)',
            'S_release.STORE[n_other_calls] = DEFINED (PINT 0)',
            '$heap_owners($heap_prune($heap_graph(S_release)), HARRAY n_array) = 1',
            '$integer_outputs(S_release.EVENTS) = ($ptascii("P;L;H:2:36:Array to string conversion:1;"))',
            '$call_descriptors_valid(S_release)', '$heap_valid($heap_graph(S_release))',
        ]
        step('S_retired', 'S_release')
        checks += [
            '$heap_owners($heap_prune($heap_graph(S_retired)), HARRAY n_array) = 0',
            '~((HARRAY n_array) <- S_retired.ALLOCATIONS)',
            'S_retired.STORE[n_result] = DEFINED pvalue_old',
            '$integer_outputs(S_retired.EVENTS) = ($ptascii("P;L;H:2:36:Array to string conversion:1;"))',
            '$call_descriptors_valid(S_retired)', '$heap_valid($heap_graph(S_retired))',
            'S_done = $drive_steps(S_retired, 5000)',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
        'S_done.STORE[n_made] = DEFINED (PINT 1)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        'S_done.STORE[n_left_calls] = DEFINED (PINT 1)',
        'S_done.STORE[n_other_calls] = DEFINED (PINT 0)',
        'S_done.STORE[n_result] = DEFINED pvalue_done',
        '$string_bytes(pvalue_done) = ($ptascii("' + ('old' if throwing else 'LArray') + '"))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_begin, 0) = S_begin[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks


def main():
    shared.sources, shared.CASES, shared.HELPERS, shared.conditions = cases, CASES, HELPERS, conditions
    return shared.main()


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
