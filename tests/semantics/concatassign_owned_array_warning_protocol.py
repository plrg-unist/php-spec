#!/usr/bin/env python3
"""Reached acquired RHS array and selected CV across used concat assignment."""
import base64
import json

import concatassign_owned_array_warning_cases as cases
import integer_operator_warning_protocol as shared

CASES = tuple(name for name in cases.CASES if not name.endswith('scalar-control'))
HELPERS = shared.HELPERS + r'''
dec $concatassign_owned_handler_frame(pframe) : bool
def $concatassign_owned_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CONCATASSIGN_OWNED_ARRAY_WARNING pconcatassignownedarraywarning 1
  -- if perrorcall.TARGET =/= eps
def $concatassign_owned_handler_frame(pframe) = false -- otherwise
dec $concatassign_owned_entered(pframe*) : bool
def $concatassign_owned_entered(eps) = false
def $concatassign_owned_entered(pframe :: pframe_tail*) = ($concatassign_owned_handler_frame(pframe) \/ $concatassign_owned_entered(pframe_tail*))
dec $concatassign_owned_frontier(pstate, nat) : bool
def $concatassign_owned_frontier(S, 0) = ($concatassign_owned_array_plan(S) =/= eps)
def $concatassign_owned_frontier(S, 1) = true
  -- if S.TODO = (CONCATASSIGN_OWNED_ARRAY_WARNING pconcatassignownedarraywarning 0) :: ptask_tail*
def $concatassign_owned_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CONCATASSIGN_OWNED_ARRAY_WARNING pconcatassignownedarraywarning 1
  -- if perrorcall.TARGET = eps
def $concatassign_owned_frontier(S, 3) = (S.CURRENT =/= eps /\ $concatassign_owned_entered(S.FRAMES))
def $concatassign_owned_frontier(S, 4) = true
  -- if S.TODO = (CONCATASSIGN_OWNED_ARRAY_WARNING pconcatassignownedarraywarning 1) :: ptask_tail*
def $concatassign_owned_frontier(S, 5) = true
  -- if S.TODO = (CONCATASSIGN_OWNED_ARRAY_COMMIT pconcatassignownedarraywarning) :: (CONCATASSIGN_OWNED_ARRAY_RELEASE pconcatassignownedarraywarning) :: ptask_tail*
  -- if S.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("Array")))
def $concatassign_owned_frontier(S, 6) = true
  -- if S.TODO = (CONCATASSIGN_OWNED_ARRAY_RELEASE pconcatassignownedarraywarning) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("AArray"))
def $concatassign_owned_frontier(S, 7) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CONCATASSIGN_OWNED_ARRAY_WARNING pconcatassignownedarraywarning 1
def $concatassign_owned_frontier(S, 8) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ORIGIN_RETURN porigin) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $concatassign_owned_frontier(S, n) = false -- otherwise
dec $concatassign_owned_seek(pstate, nat, nat) : pstate
def $concatassign_owned_seek(S, n_stage, n) = S -- if $concatassign_owned_frontier(S, n_stage)
def $concatassign_owned_seek(S, n_stage, n) = S
  -- if ~$concatassign_owned_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $concatassign_owned_seek(S, n_stage, n) = S
  -- if ~$concatassign_owned_frontier(S, n_stage)
  -- if S.TODO = eps \/ n = 0
def $concatassign_owned_seek(S, n_stage, n) = $concatassign_owned_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$concatassign_owned_frontier(S, n_stage)
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
        checks.extend([f'{label}_found = $concatassign_owned_seek({start}, {stage}, 5000)',
                       f'{label}_found.COMPLETION = NORMAL \\/ {label}_found.COMPLETION = BUDGET',
                       f'{label} = {label}_found[.COMPLETION = NORMAL]',
                       f'$concatassign_owned_frontier({label}, {stage})'])

    def step(label, start):
        checks.extend([f'{label}_budget = $drive_steps({start}, 1)',
                       f'{label}_budget.COMPLETION = BUDGET',
                       f'{label} = {label}_budget[.COMPLETION = NORMAL]'])

    seek('S_entry', 'S_initial', 0)
    checks += [
        'S_entry.TODO = (COMPOUND_APPLY CONCAT (BASE_VALUE poperand_left) false 23) :: ptask_tail*',
        'S_entry.ORIGIN = (porigin_compound)',
        'S_entry.RESULT = KNOWN (PARRAY n_array)',
        'S_entry.OUTPUTBUFFERS = eps',
        '$concatassign_owned_array_plan(S_entry) = (pconcatassignownedarraywarning)',
        'pconcatassignownedarraywarning.SITE = porigin_compound',
        'pconcatassignownedarraywarning.LINE = 23',
        'pconcatassignownedarraywarning.LEFTOP = poperand_left',
        'pconcatassignownedarraywarning.ARRAY = n_array',
        'pconcatassignownedarraywarning.CELL = n_lhs',
        '$string_bytes(pconcatassignownedarraywarning.LEFT) = ($ptascii("A"))',
        '$concatassign_owned_array_source(S_entry, pconcatassignownedarraywarning)',
        '$concatassign_owned_array_snapshot(S_entry, pconcatassignownedarraywarning)',
        '$lookup(S_entry.ENV, $ptascii("a")) = (n_a)',
        '$lookup(S_entry.ENV, $ptascii("lhs")) = (n_lhs)',
        '$lookup(S_entry.ENV, $ptascii("value")) = (n_value)',
        '$lookup(S_entry.ENV, $ptascii("made")) = (n_made)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        'S_entry.STORE[n_a] = DEFINED (PARRAY n_array)',
        'S_entry.STORE[n_lhs] = DEFINED pvalue_A',
        '$string_bytes(pvalue_A) = ($ptascii("A"))',
        'S_entry.STORE[n_value] = DEFINED pvalue_old',
        '$string_bytes(pvalue_old) = ($ptascii("old"))',
        'S_entry.STORE[n_made] = DEFINED (PINT 1)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_array) = 2',
        '$integer_outputs(S_entry.EVENTS) = ($ptascii("P;"))',
        '$concatassign_owned_array_plan(S_entry[.ORIGIN = eps]) = eps',
        '$concatassign_owned_array_plan(S_entry[.RESULT = KNOWN (PINT 7)]) = eps',
        '~$concatassign_owned_array_source(S_entry, pconcatassignownedarraywarning[.LINE = 22])',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'S_entry.TODO = ptask_old :: ptask_tail*',
        'PhpStep: S_entry ~> S_begin_raw',
        'S_begin_raw.TODO = (CONCATASSIGN_OWNED_ARRAY_WARNING pconcatassignownedarraywarning 0) :: ptask_tail*',
    ]
    step('S_begin', 'S_entry')
    checks += [
        'S_begin = S_begin_raw',
        'S_begin.LOCATION = ROOT n_lhs',
        'S_begin.RESULT = KNOWN PNULL',
        '$task_nodes(CONCATASSIGN_OWNED_ARRAY_WARNING pconcatassignownedarraywarning 0) = [HARRAY n_array] ++ $value_nodes(pconcatassignownedarraywarning.LEFT)',
        '$heap_owners($heap_prune($heap_graph(S_begin)), HARRAY n_array) = 2',
        '$concatassign_owned_array_valid(S_begin, pconcatassignownedarraywarning, 0)',
        '$concatassign_owned_array_selected(S_begin, pconcatassignownedarraywarning)',
        '$call_descriptors_valid(S_begin)', '$heap_valid($heap_graph(S_begin))',
        'S_buffer_begin = S_begin[.OUTPUTBUFFERS = [{ID S_begin.OUTPUTSEQ, HANDLER eps, CHUNK 0, FLAGS 112, SIZE 16384, BYTES eps}]][.OUTPUTSEQ = $(S_begin.OUTPUTSEQ + 1)]',
        '$output_state_valid(S_buffer_begin)',
        '~$concatassign_owned_array_valid(S_buffer_begin, pconcatassignownedarraywarning, 0)',
    ]
    step('S_dispatch', 'S_begin')
    checks += [
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = CONCATASSIGN_OWNED_ARRAY_WARNING pconcatassignownedarraywarning 1',
        'perrorcall.TARGET = eps',
        'perrorcall.LINE = 23', 'perrorcall.LEVEL = 2',
        'perrorcall.MESSAGE = $ptascii("Array to string conversion")',
        'perrorcall.SITE = porigin_compound',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = 22])',
        '$heap_owners($heap_prune($heap_graph(S_dispatch)), HARRAY n_array) = 2',
        '$integer_outputs(S_dispatch.EVENTS) = ($ptascii("P;"))',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
    ]
    seek('S_handler_entered', 'S_dispatch', 3)
    checks += [
        'S_handler_entered.FRAMES = pframe_handler :: pframe_handler_tail*',
        '$concatassign_owned_handler_frame(pframe_handler)',
        '$call_descriptors_valid(S_handler_entered)', '$heap_valid($heap_graph(S_handler_entered))',
    ]
    if throwing:
        seek('S_pending', 'S_handler_entered', 7)
        checks += [
            'S_pending.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_pending) :: ptask_pending*',
            'perrorcall_pending.RESUME = CONCATASSIGN_OWNED_ARRAY_WARNING pconcatassignownedarraywarning 1',
            '$lookup(S_pending.ENV, $ptascii("a")) = eps',
            'S_pending.STORE[n_lhs] = DEFINED pvalue_B',
            '$string_bytes(pvalue_B) = ($ptascii("B"))',
            'S_pending.STORE[n_value] = DEFINED pvalue_old',
            '$heap_owners($heap_prune($heap_graph(S_pending)), HARRAY n_array) = 1',
            '$integer_outputs(S_pending.EVENTS) = ($ptascii("P;H:2:23:Array to string conversion:1:1;"))',
            '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
        ]
        step('S_throw', 'S_pending')
        checks += [
            '$concatassign_owned_frontier(S_throw, 8)',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HARRAY n_array) = 0',
            '~((HARRAY n_array) <- S_throw.ALLOCATIONS)',
            'S_throw.STORE[n_lhs] = DEFINED pvalue_B',
            'S_throw.STORE[n_value] = DEFINED pvalue_old',
            '$lookup(S_throw.ENV, $ptascii("second")) = (n_second)',
            'S_throw.STORE[n_second] = DEFINED (POBJECT n_exception)',
            '$throwable_live(S_throw, n_exception)',
            '$throwable_field(S_throw, n_exception, "line") = PINT 20',
            '$integer_outputs(S_throw.EVENTS) = ($ptascii("P;H:2:23:Array to string conversion:1:1;"))',
            '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
            'S_done = $drive_steps(S_throw, 5000)',
        ]
    else:
        seek('S_return', 'S_handler_entered', 4)
        checks += [
            'S_return.TODO = (CONCATASSIGN_OWNED_ARRAY_WARNING pconcatassignownedarraywarning 1) :: ptask_tail*',
            '$lookup(S_return.ENV, $ptascii("a")) = eps',
            'S_return.STORE[n_lhs] = DEFINED pvalue_B',
            '$string_bytes(pvalue_B) = ($ptascii("B"))',
            'S_return.STORE[n_value] = DEFINED pvalue_old',
            'S_return.STORE[n_calls] = DEFINED (PINT 1)',
            '$concatassign_owned_array_valid(S_return, pconcatassignownedarraywarning, 1)',
            '$concatassign_owned_array_selected(S_return, pconcatassignownedarraywarning)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_array) = 1',
            '$integer_outputs(S_return.EVENTS) = ($ptascii("P;H:2:23:Array to string conversion:1:1;"))',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
            'S_buffer_return = S_return[.OUTPUTBUFFERS = [{ID S_return.OUTPUTSEQ, HANDLER eps, CHUNK 0, FLAGS 112, SIZE 16384, BYTES eps}]][.OUTPUTSEQ = $(S_return.OUTPUTSEQ + 1)]',
            '$output_state_valid(S_buffer_return)',
            '$concatassign_owned_array_valid(S_buffer_return, pconcatassignownedarraywarning, 1)',
            'PhpStep: S_buffer_return ~> S_buffer_boundary',
            'S_buffer_boundary.COMPLETION = UNSUPPORTED "concatenation assignment acquired right changed output buffer or target"',
        ]
        step('S_resume', 'S_return')
        checks += [
            '$concatassign_owned_frontier(S_resume, 5)',
            '$task_nodes(CONCATASSIGN_OWNED_ARRAY_COMMIT pconcatassignownedarraywarning) = eps',
            '$task_nodes(CONCATASSIGN_OWNED_ARRAY_RELEASE pconcatassignownedarraywarning) = [HARRAY n_array] ++ $value_nodes(pconcatassignownedarraywarning.LEFT)',
            'S_resume.STORE[n_lhs] = DEFINED pvalue_B',
            'S_resume.STORE[n_value] = DEFINED pvalue_old',
            '$heap_owners($heap_prune($heap_graph(S_resume)), HARRAY n_array) = 1',
            '$integer_outputs(S_resume.EVENTS) = ($ptascii("P;H:2:23:Array to string conversion:1:1;"))',
            '$call_descriptors_valid(S_resume)', '$heap_valid($heap_graph(S_resume))',
            'S_retarget = S_resume[.LOCATION = ROOT n_made]',
            '~$concatassign_owned_array_selected(S_retarget, pconcatassignownedarraywarning)',
            'PhpStep: S_retarget ~> S_retarget_boundary',
            'S_retarget_boundary.COMPLETION = UNSUPPORTED "concatenation assignment acquired right changed output buffer or target"',
        ]
        step('S_commit', 'S_resume')
        checks += [
            '$concatassign_owned_frontier(S_commit, 6)',
            'S_commit.STORE[n_lhs] = DEFINED pvalue_AArray',
            '$string_bytes(pvalue_AArray) = ($ptascii("AArray"))',
            'S_commit.STORE[n_value] = DEFINED pvalue_old',
            '$heap_owners($heap_prune($heap_graph(S_commit)), HARRAY n_array) = 1',
            '$integer_outputs(S_commit.EVENTS) = ($ptascii("P;H:2:23:Array to string conversion:1:1;"))',
            '$call_descriptors_valid(S_commit)', '$heap_valid($heap_graph(S_commit))',
        ]
        step('S_retired', 'S_commit')
        checks += [
            '$heap_owners($heap_prune($heap_graph(S_retired)), HARRAY n_array) = 0',
            '~((HARRAY n_array) <- S_retired.ALLOCATIONS)',
            'S_retired.STORE[n_lhs] = DEFINED pvalue_AArray',
            'S_retired.STORE[n_value] = DEFINED pvalue_old',
            '$integer_outputs(S_retired.EVENTS) = ($ptascii("P;H:2:23:Array to string conversion:1:1;"))',
            '$call_descriptors_valid(S_retired)', '$heap_valid($heap_graph(S_retired))',
            'S_done = $drive_steps(S_retired, 5000)',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
        'S_done.STORE[n_made] = DEFINED (PINT 1)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        'S_done.STORE[n_lhs] = DEFINED pvalue_lhs_done',
        '$string_bytes(pvalue_lhs_done) = ($ptascii("' + ('B' if throwing else 'AArray') + '"))',
        'S_done.STORE[n_value] = DEFINED pvalue_done',
        '$string_bytes(pvalue_done) = ($ptascii("' + ('old' if throwing else 'AArray') + '"))',
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
