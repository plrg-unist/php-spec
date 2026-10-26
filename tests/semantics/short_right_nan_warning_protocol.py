#!/usr/bin/env python3
"""Reached selected-RIGHT NaN warning and short-circuit completion states."""
import base64
import json

import short_right_nan_warning_cases as cases
import integer_operator_warning_protocol as shared

CASES = ('right-nan-symbolic-and-normal', 'right-nan-keyword-or-throw')
HELPERS = shared.HELPERS + r'''
dec $right_nan_task(ptask) : bool
def $right_nan_task(SHORT_RIGHT_NAN_WARNING pboolnotnanwarning n) = true
def $right_nan_task(TRUTH_RESULT false z) = true
def $right_nan_task(ERROR_HANDLER_INVOKE perrorcall) = $right_nan_task(perrorcall.RESUME)
def $right_nan_task(ERROR_HANDLER_RESULT perrorcall) = $right_nan_task(perrorcall.RESUME)
def $right_nan_task(ERROR_HANDLER_CLEAN perrorcall) = $right_nan_task(perrorcall.RESUME)
def $right_nan_task(ptask) = false -- otherwise
dec $right_nan_tasks(ptask*) : bool
def $right_nan_tasks(eps) = false
def $right_nan_tasks(ptask :: ptask_tail*) = ($right_nan_task(ptask) \/ $right_nan_tasks(ptask_tail*))
dec $right_nan_handler_frame(pframe) : bool
def $right_nan_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = SHORT_RIGHT_NAN_WARNING pboolnotnanwarning 1
  -- if perrorcall.TARGET =/= eps
def $right_nan_handler_frame(pframe) = false -- otherwise
dec $right_nan_entered(pframe*) : bool
def $right_nan_entered(eps) = false
def $right_nan_entered(pframe :: pframe_tail*) = ($right_nan_handler_frame(pframe) \/ $right_nan_entered(pframe_tail*))
dec $right_nan_frontier(pstate, nat) : bool
def $right_nan_frontier(S, 0) = ($short_right_nan_plan(S) =/= eps)
def $right_nan_frontier(S, 1) = true
  -- if S.TODO = (SHORT_RIGHT_NAN_WARNING pboolnotnanwarning 0) :: ptask_tail*
def $right_nan_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = SHORT_RIGHT_NAN_WARNING pboolnotnanwarning 1
  -- if perrorcall.TARGET = eps
def $right_nan_frontier(S, 3) = (S.CURRENT =/= eps /\ $right_nan_entered(S.FRAMES))
def $right_nan_frontier(S, 4) = true
  -- if S.TODO = (SHORT_RIGHT_NAN_WARNING pboolnotnanwarning 1) :: ptask_tail*
def $right_nan_frontier(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.RESULT = KNOWN (PBOOL b)
  -- if ~$right_nan_tasks(S.TODO)
def $right_nan_frontier(S, 6) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if ~$right_nan_tasks(S.TODO)
def $right_nan_frontier(S, n) = false -- otherwise
dec $right_nan_seek(pstate, nat, nat) : pstate
def $right_nan_seek(S, n_stage, n) = S -- if $right_nan_frontier(S, n_stage)
def $right_nan_seek(S, n_stage, n) = S
  -- if ~$right_nan_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $right_nan_seek(S, n_stage, n) = S
  -- if ~$right_nan_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $right_nan_seek(S, n_stage, n) = $right_nan_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$right_nan_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
dec $right_nan_diagnostic(pevent, text) : nat
def $right_nan_diagnostic(DIAGNOSTIC text n_message* z, text) = 1
def $right_nan_diagnostic(DIAGNOSTIC_SOURCE n_source text n_message* z, text) = 1
def $right_nan_diagnostic(DIAGNOSTIC_STACK text n_message* z n_trace*, text) = 1
def $right_nan_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n_message* z n_trace*, text) = 1
def $right_nan_diagnostic(pevent, text) = 0 -- otherwise
dec $right_nan_diagnostics(pevent*, text) : nat
def $right_nan_diagnostics(eps, text) = 0
def $right_nan_diagnostics(pevent :: pevent_tail*, text) = $($right_nan_diagnostic(pevent, text) + $right_nan_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    throws = name.endswith('-throw')
    initial = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]
    checks = initial

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $right_nan_seek({before}, {stage}, 3000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$right_nan_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$short_right_nan_plan(S_entry) = (pboolnotnanwarning)',
        'S_entry.TODO = (TRUTH_RESULT false 25) :: ptask_tail*',
        'S_entry.ORIGIN = (porigin)',
        '$origin_node(S_entry.SOURCES, porigin) = (pcnode)',
        '$truth_short_source(pcnode) = ((b_or, expression_left, expression_right))',
        'b_or = ' + ('true' if throws else 'false'),
        '$code_expression_at_source(S_entry, porigin, [PCFIELD 1]) = (25)',
        '$integer_operand_source(S_entry, porigin, [PCFIELD 1], pboolnotnanwarning.INPUT)',
        'pboolnotnanwarning.SITE = porigin', 'pboolnotnanwarning.LINE = 25',
        'pboolnotnanwarning.INPUT = VARIABLE ($ptascii("x")) 25',
        'S_entry.RESULT = pboolnotnanwarning.INPUT',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)', 'pboolnotnanwarning.CELL = n_x',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("left_calls")) = (n_left_calls)',
        'S_entry.STORE[n_x] = DEFINED (PFLOAT pboolnotnanwarning.BITS)',
        '$fparts_nan($float_decode(pboolnotnanwarning.BITS))',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        'S_entry.STORE[n_left_calls] = DEFINED (PINT 1)',
        '$integer_outputs(S_entry.EVENTS) = ([76,59])',
        '(HCELL n_x) <- S_entry.ALLOCATIONS', '~(n_x <- S_entry.REFCELLS)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        '$short_right_nan_source(S_entry, pboolnotnanwarning)',
        '$boolnot_nan_snapshot(S_entry, pboolnotnanwarning)',
        '$short_right_nan_warning_valid(S_entry, pboolnotnanwarning, 0)',
        '$short_right_nan_plan(S_entry[.ORIGIN = eps]) = eps',
        '$short_right_nan_plan(S_entry[.CODE = eps]) = eps',
        '$short_right_nan_plan(S_entry[.RESULT = KNOWN (PFLOAT pboolnotnanwarning.BITS)]) = eps',
        '$short_right_nan_plan(S_entry[.TODO = [TRUTH_RESULT false 24]]) = eps',
        '$short_right_nan_plan(S_entry[.ERRORHANDLER.LEVELS = 8192]) = eps',
        '$short_right_nan_plan(S_entry[.REFCELLS = [n_x]]) = eps',
        '$short_right_nan_plan(S_entry[.STORE[n_x] = DEFINED (PFLOAT 0)]) = eps',
        '~$short_right_nan_source(S_entry, pboolnotnanwarning[.LINE = 24])',
        '~$short_right_nan_source(S_entry, pboolnotnanwarning[.INPUT = VARIABLE ($ptascii("v")) 25])',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'PhpStep: S_entry ~> S_capture_atomic',
        'S_capture_atomic = S_entry[.TODO = (SHORT_RIGHT_NAN_WARNING pboolnotnanwarning 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    if throws:
        checks += [
            '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
            'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture = S_capture_atomic',
        '$task_nodes(SHORT_RIGHT_NAN_WARNING pboolnotnanwarning 0) = eps',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_x) = 1',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        '$right_nan_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = SHORT_RIGHT_NAN_WARNING pboolnotnanwarning 1',
        'perrorcall.TARGET = eps', 'perrorcall.SITE = pboolnotnanwarning.SITE',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = $ptascii("unexpected NAN value was coerced to bool")',
        'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE 25',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = 24])',
        '$integer_outputs(S_dispatch.EVENTS) = ([76,59])',
        '$call_descriptors_valid(S_dispatch)',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += [
        'S_entered.CURRENT =/= eps', '$right_nan_entered(S_entered.FRAMES)',
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_saved*',
        'perrorcall_entered.RESUME = SHORT_RIGHT_NAN_WARNING pboolnotnanwarning 1',
        'perrorcall_entered.TARGET =/= eps',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    seek('S_post', 'S_entered', 6 if throws else 4)
    checks += [
        'S_post.CURRENT = eps', 'S_post.FRAMES = eps',
        'S_post.STORE[n_x] = DEFINED (PFLOAT ' + ('4607182418800017408' if throws else '0') + ')',
        'S_post.STORE[n_v] = DEFINED (PINT 100)',
        'S_post.STORE[n_calls] = DEFINED (PINT 1)',
        'S_post.STORE[n_left_calls] = DEFINED (PINT 1)',
        '$boolnot_nan_ready(S_post, pboolnotnanwarning) = (' + ('4607182418800017408' if throws else '0') + ')',
        '~$boolnot_nan_snapshot(S_post, pboolnotnanwarning)',
        '$short_right_nan_source(S_post, pboolnotnanwarning)',
        '$right_nan_diagnostics(S_post.EVENTS, "Warning") = ' + ('0' if throws else '1'),
        '$call_descriptors_valid(S_post)', '$heap_valid($heap_graph(S_post))',
    ]
    if throws:
        checks += [
            'S_post.TODO = (THROW_SEARCH n_second) :: ptask_caller*',
            '~$right_nan_tasks(S_post.TODO)',
            '$throwable_live(S_post, n_second)',
            '$throwable_previous_id(S_post, n_second) = eps',
            '$throwable_field(S_post, n_second, "line") = PINT 20',
            '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]',
            'S_done = $drive_steps(S_post, 3000)',
        ]
    else:
        checks += [
            'S_post.TODO = (SHORT_RIGHT_NAN_WARNING pboolnotnanwarning 1) :: ptask_tail*',
            '$short_right_nan_warning_valid(S_post, pboolnotnanwarning, 1)',
            '~$short_right_nan_warning_valid(S_post, pboolnotnanwarning, 0)',
            '$error_call_valid(S_post, perrorcall_entered)',
            'PhpStep: S_post ~> S_bool_atomic',
            'S_bool_atomic = S_post[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
            'S_same_nan = S_post[.STORE[n_x] = DEFINED (PFLOAT pboolnotnanwarning.BITS)]',
            'PhpStep: S_same_nan ~> S_same_nan_out',
            'S_same_nan_out = S_same_nan[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL true)][.BASE = BASE_VALUE (KNOWN PNULL)]',
            'S_same_nan_out.EVENTS = S_post.EVENTS',
            'S_retyped = S_post[.STORE[n_x] = DEFINED (PINT 0)]',
            'PhpStep: S_retyped ~> S_refused',
            'S_refused = S_retyped[.COMPLETION = UNSUPPORTED "short-circuit RIGHT NaN changed CV representation"]',
        ]
        step('S_bool', 'S_post')
        checks += [
            'S_bool = S_bool_atomic', 'S_bool.RESULT = KNOWN (PBOOL false)',
            '~$right_nan_tasks(S_bool.TODO)',
            'S_bool.EVENTS = S_post.EVENTS',
            'S_done = $drive_steps(S_bool, 3000)',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
        'S_done.STORE[n_x] = DEFINED (PINT 8)',
        'S_done.STORE[n_v] = DEFINED (' + ('PINT 100' if throws else 'PBOOL false') + ')',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        'S_done.STORE[n_left_calls] = DEFINED (PINT 1)',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_post, 0) = S_post[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks


def main():
    shared.sources, shared.CASES, shared.HELPERS, shared.conditions = cases, CASES, HELPERS, conditions
    return shared.main()


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
