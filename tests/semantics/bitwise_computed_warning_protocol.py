#!/usr/bin/env python3
"""Reached computed-TMP bitwise conversion order and second-warning cancellation."""
import base64
import json

import bitwise_computed_warning_cases as cases
import integer_operator_warning_protocol as shared

CASES = (
    'computed-left-and-default',
    'computed-left-xor-second-throw',
    'computed-left-mul-or-default',
    'computed-left-div-xor-default',
)
OPS = {'and': ('BITAND', 4), 'or': ('BITOR', 13), 'xor': ('BITXOR', 9)}
RIGHT_BITS = 4617878467915022336  # 5.5
LEFT_BITS = 4623226492472524800   # 12.5
CHANGED_BITS = 4612811918334230528  # 2.5

HELPERS = shared.HELPERS + r'''
dec $computed_frame(pframe, nat) : bool
def $computed_frame(pframe, 1) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 1
  -- if perrorcall.TARGET =/= eps
def $computed_frame(pframe, 2) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i) pintegerconversion 1
  -- if perrorcall.TARGET =/= eps
def $computed_frame(pframe, n) = false -- otherwise
dec $computed_frames(pframe*, nat) : bool
def $computed_frames(eps, n) = false
def $computed_frames(pframe :: pframe_tail*, n) = ($computed_frame(pframe, n) \/ $computed_frames(pframe_tail*, n))
dec $computed_frontier(pstate, nat) : bool
def $computed_frontier(S, 0) = ($integer_operator_plan(S) =/= eps)
def $computed_frontier(S, 1) = true
  -- if S.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 0) :: ptask_tail*
def $computed_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 1
  -- if perrorcall.TARGET = eps
def $computed_frontier(S, 3) = true
  -- if S.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 1) :: ptask_tail*
def $computed_frontier(S, 5) = true
  -- if S.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i) pintegerconversion 0) :: ptask_tail*
def $computed_frontier(S, 6) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i) pintegerconversion 1
  -- if perrorcall.TARGET = eps
def $computed_frontier(S, 7) = true
  -- if S.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i) pintegerconversion 1) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $computed_frontier(S, 8) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $computed_frontier(S, 9) = (S.CURRENT =/= eps /\ $computed_frames(S.FRAMES, 1))
def $computed_frontier(S, 10) = (S.CURRENT =/= eps /\ $computed_frames(S.FRAMES, 2))
def $computed_frontier(S, n) = false -- otherwise
dec $computed_seek(pstate, nat, nat) : pstate
def $computed_seek(S, n_stage, n) = S -- if $computed_frontier(S, n_stage)
def $computed_seek(S, n_stage, n) = S
  -- if ~$computed_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $computed_seek(S, n_stage, n) = S
  -- if ~$computed_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $computed_seek(S, n_stage, n) = $computed_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$computed_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
dec $computed_diagnostic(pevent) : nat
def $computed_diagnostic(DIAGNOSTIC "Deprecated" n_message* z) = 1
def $computed_diagnostic(DIAGNOSTIC_SOURCE n_source "Deprecated" n_message* z) = 1
def $computed_diagnostic(pevent) = 0 -- otherwise
dec $computed_diagnostics(pevent*) : nat
def $computed_diagnostics(eps) = 0
def $computed_diagnostics(pevent :: pevent_tail*) = $($computed_diagnostic(pevent) + $computed_diagnostics(pevent_tail*))
'''


def conditions(name, program, path, stdout):
    stem = name.split('-')
    op, result = OPS[stem[2] if stem[2] in OPS else stem[3]]
    throws = name.endswith('-throw')
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $computed_seek({before}, {stage}, 3000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$computed_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$integer_operator_plan(S_entry) = (pintegeroperation)',
        'S_entry.TODO = (BINARY_RIGHT ' + op + ' poperand_left 24) :: ptask_tail*',
        'S_entry.ORIGIN = (porigin)', 'pintegeroperation.SITE = porigin',
        'pintegeroperation.OP = ' + op, 'pintegeroperation.LINE = 24',
        'pintegeroperation.SWAPPED',
        'pintegeroperation.LEFT = KNOWN (PFLOAT ' + str(LEFT_BITS) + ')',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 24',
        'pintegeroperation.LEFTPOINTER = INTEGER_COPY (PFLOAT ' + str(LEFT_BITS) + ')',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))',
        '$integer_operand_source(S_entry, porigin, [PCFIELD 0], pintegeroperation.LEFT)',
        '$integer_operand_source(S_entry, porigin, [PCFIELD 1], pintegeroperation.RIGHT)',
        '$integer_slot_rank(S_entry, porigin, [PCFIELD 0], pintegeroperation.LEFT) = (2)',
        '$integer_slot_rank(S_entry, porigin, [PCFIELD 1], pintegeroperation.RIGHT) = (8)',
        '$integer_phase_pointer(pintegeroperation, INTEGER_LEFT) = pintegeroperation.RIGHTPOINTER',
        '$integer_phase_pointer(pintegeroperation, INTEGER_RIGHT 5) = pintegeroperation.LEFTPOINTER',
        '$integer_operation_valid(S_entry, pintegeroperation)',
        '~$integer_operation_valid(S_entry, pintegeroperation[.SWAPPED = false])',
        '~$integer_operation_valid(S_entry, pintegeroperation[.LINE = 25])',
        '~$integer_operation_valid(S_entry, pintegeroperation[.OP = MODULO])',
        '$integer_operator_plan(S_entry[.ORIGIN = eps]) = eps',
        '$integer_operator_plan(S_entry[.CODE = eps]) = eps',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'S_entry.STORE[n_left] = DEFINED (PFLOAT ' + str(LEFT_BITS) + ')',
        'S_entry.STORE[n_right] = DEFINED (PFLOAT ' + str(RIGHT_BITS) + ')',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '$task_nodes(BINARY_RIGHT ' + op + ' poperand_left 24) = eps',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'PhpStep: S_entry ~> S_begin_atomic',
        'S_begin_atomic = S_entry[.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation INTEGER_LEFT) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_begin', 'S_entry')
    checks += ['S_begin = S_begin_atomic', '$call_descriptors_valid(S_begin)']
    seek('S_first', 'S_begin', 1)
    checks += [
        'S_first.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pconversion_first 0) :: ptask_tail*',
        'pconversion_first.INPUT = PFLOAT ' + str(RIGHT_BITS),
        'pconversion_first.VALUE = 5', '|pconversion_first.NOTICES| = 1',
        '$integer_warning_valid(S_first, pintegeroperation, INTEGER_LEFT, pconversion_first, 0)',
        '~$integer_warning_valid(S_first, pintegeroperation, INTEGER_LEFT, pconversion_first[.VALUE = 6], 0)',
        '$task_nodes(INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pconversion_first 0) = eps',
    ]
    step('S_dispatch_first', 'S_first')
    checks += [
        '$computed_frontier(S_dispatch_first, 2)',
        'S_dispatch_first.TODO = (ERROR_HANDLER_INVOKE pcall_first) :: ptask_tail*',
        'pcall_first.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pconversion_first 1',
        'pcall_first.LINE = 24', 'pcall_first.LEVEL = 8192',
        'pcall_first.MESSAGE = $ptascii("Implicit conversion from float 5.5 to int loses precision")',
        '$error_call_valid(S_dispatch_first, pcall_first)',
        '~$error_call_valid(S_dispatch_first, pcall_first[.LINE = 25])',
    ]
    seek('S_entered_first', 'S_dispatch_first', 9)
    checks += ['$computed_frames(S_entered_first.FRAMES, 1)', 'S_entered_first.CURRENT =/= eps']
    seek('S_return_first', 'S_entered_first', 3)
    checks += [
        'S_return_first.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pconversion_first 1) :: ptask_tail*',
        'S_return_first.STORE[n_left] = DEFINED (PINT 99)',
        'S_return_first.STORE[n_right] = DEFINED (PFLOAT ' + str(CHANGED_BITS) + ')',
        'S_return_first.STORE[n_calls] = DEFINED (PINT 1)',
        'S_return_first.STORE[n_v] = DEFINED (PINT 100)',
        '$integer_warning_valid(S_return_first, pintegeroperation, INTEGER_LEFT, pconversion_first, 1)',
        '$integer_pointer_value(S_return_first, pintegeroperation.RIGHTPOINTER) = (PFLOAT ' + str(CHANGED_BITS) + ')',
        '$integer_pointer_value(S_return_first, pintegeroperation.LEFTPOINTER) = (PFLOAT ' + str(LEFT_BITS) + ')',
        '$computed_diagnostics(S_return_first.EVENTS) = 1',
        '$call_descriptors_valid(S_return_first)',
    ]
    seek('S_second', 'S_return_first', 5)
    checks += [
        'S_second.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT 5) pconversion_second 0) :: ptask_tail*',
        'pconversion_second.INPUT = PFLOAT ' + str(LEFT_BITS),
        'pconversion_second.VALUE = 12', '|pconversion_second.NOTICES| = 1',
        '$integer_warning_valid(S_second, pintegeroperation, INTEGER_RIGHT 5, pconversion_second, 0)',
        '$task_nodes(INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT 5) pconversion_second 0) = eps',
        '$integer_pointer_value(S_second, pintegeroperation.LEFTPOINTER) = (PFLOAT ' + str(LEFT_BITS) + ')',
    ]
    step('S_dispatch_second', 'S_second')
    checks += [
        '$computed_frontier(S_dispatch_second, 6)',
        'S_dispatch_second.TODO = (ERROR_HANDLER_INVOKE pcall_second) :: ptask_tail*',
        'pcall_second.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT 5) pconversion_second 1',
        'pcall_second.LINE = 24', 'pcall_second.LEVEL = 8192',
        'pcall_second.MESSAGE = $ptascii("Implicit conversion from float 12.5 to int loses precision")',
        '$error_call_valid(S_dispatch_second, pcall_second)',
        '~$error_call_valid(S_dispatch_second, pcall_second[.MESSAGE = pcall_first.MESSAGE])',
    ]
    seek('S_entered_second', 'S_dispatch_second', 10)
    checks += ['$computed_frames(S_entered_second.FRAMES, 2)', 'S_entered_second.CURRENT =/= eps']
    seek('S_post', 'S_entered_second', 8 if throws else 7)
    checks += [
        'S_post.STORE[n_left] = DEFINED (PINT 99)',
        'S_post.STORE[n_right] = DEFINED (PINT 88)',
        'S_post.STORE[n_calls] = DEFINED (PINT 2)',
        'S_post.STORE[n_v] = DEFINED (PINT 100)',
        '$computed_diagnostics(S_post.EVENTS) = ' + ('1' if throws else '2'),
        '$call_descriptors_valid(S_post)', '$heap_valid($heap_graph(S_post))',
    ]
    if throws:
        checks += [
            'S_post.TODO = (THROW_SEARCH n_failure) :: ptask_tail*',
            '$throwable_live(S_post, n_failure)',
            '$throwable_field(S_post, n_failure, "line") = PINT 20',
        ]
    else:
        checks += [
            'S_post.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT 5) pconversion_second 1) :: ptask_tail*',
            '$integer_warning_valid(S_post, pintegeroperation, INTEGER_RIGHT 5, pconversion_second, 1)',
            '$integer_binary(' + op + ', 12, 5) = IRESULT ' + str(result),
            '$integer_binary(' + op + ', 12, 2) = IRESULT ' + str({'BITAND': 0, 'BITOR': 14, 'BITXOR': 14}[op]),
        ]
    checks += [
        'S_done = $drive_steps(S_post, 3000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps',
        'S_done.STORE[n_v] = DEFINED (PINT ' + str(100 if throws else result) + ')',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_first, 0) = S_first[.COMPLETION = BUDGET]',
        '$drive_steps(S_second, 0) = S_second[.COMPLETION = BUDGET]',
        '$drive_steps(S_post, 0) = S_post[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks


def main():
    shared.sources, shared.CASES, shared.HELPERS, shared.conditions = cases, CASES, HELPERS, conditions
    return shared.main()


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
