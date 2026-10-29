#!/usr/bin/env python3
"""Source-reached integer snapshots before a live stdClass RHS conversion."""
import base64
import hashlib
import json
from pathlib import Path

import integer_object_right_warning_cases as cases
import integer_operator_warning_protocol as shared

CASES = ('mod-replace', 'and-retain-typeerror', 'xor-handler-throw')
LEFT_BITS = 4623226492472524800  # 12.5
CHANGED_BITS = 4636702106982547456  # 99.5
OPS = {'mod': ('MODULO', 2), 'and': ('BITAND', 4), 'xor': ('BITXOR', 9)}
HELPERS = shared.HELPERS + r'''
dec $object_integer_throw_front(pstate) : bool
def $object_integer_throw_front(S) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $object_integer_throw_front(S) = false -- otherwise
dec $object_integer_seek_throw(pstate, nat) : pstate
def $object_integer_seek_throw(S, n) = S -- if $object_integer_throw_front(S)
def $object_integer_seek_throw(S, n) = S
  -- if ~$object_integer_throw_front(S)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $object_integer_seek_throw(S, n) = S
  -- if ~$object_integer_throw_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $object_integer_seek_throw(S, n) = $object_integer_seek_throw($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$object_integer_throw_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    op, result = OPS[name.split('-')[0]]
    throws = name.endswith('handler-throw')
    retains = 'retain' in name
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $integer_seek({before}, {stage}, 2000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$integer_frontier({state}, {stage})',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$integer_operator_plan(S_entry) = (pintegeroperation)',
        'S_entry.TODO = (BINARY_RIGHT ' + op + ' poperand_left 24) :: ptask_tail*',
        'S_entry.ORIGIN = (porigin)', 'pintegeroperation.SITE = porigin',
        'pintegeroperation.OP = ' + op, 'pintegeroperation.LINE = 24',
        '~pintegeroperation.SWAPPED',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 24',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 24',
        'pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("left"))',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'S_entry.STORE[n_left] = DEFINED (PFLOAT ' + str(LEFT_BITS) + ')',
        'S_entry.STORE[n_right] = DEFINED (POBJECT n_object)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '$integer_plain_stdclass(S_entry, POBJECT n_object)',
        '~$integer_plain_stdclass(S_entry[.ALLOCATIONS = eps], POBJECT n_object)',
        '$integer_object_right_initial(S_entry, pintegeroperation.LEFT, pintegeroperation.RIGHT, PFLOAT ' + str(LEFT_BITS) + ', POBJECT n_object, false)',
        '~$integer_object_right_initial(S_entry, pintegeroperation.LEFT, pintegeroperation.RIGHT, PINT 12, POBJECT n_object, false)',
        '~$integer_object_right_initial(S_entry, pintegeroperation.LEFT, pintegeroperation.RIGHT, PFLOAT ' + str(LEFT_BITS) + ', POBJECT n_object, true)',
        '~$integer_object_right_initial(S_entry, pintegeroperation.LEFT, KNOWN (POBJECT n_object), PFLOAT ' + str(LEFT_BITS) + ', POBJECT n_object, false)',
        '$integer_operation_valid(S_entry, pintegeroperation)',
        '~$integer_operation_valid(S_entry, pintegeroperation[.LINE = 25])',
        '~$integer_operation_valid(S_entry, pintegeroperation[.SWAPPED = true])',
        '$integer_operator_plan(S_entry[.ORIGIN = eps]) = eps',
        '$integer_operator_plan(S_entry[.CODE = eps]) = eps',
        '$task_nodes(INTEGER_OPERATOR_CONVERT pintegeroperation INTEGER_LEFT) = eps',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HOBJECT n_object) = 1',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'PhpStep: S_entry ~> S_begin',
        'S_begin = S_entry[.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation INTEGER_LEFT) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_begin.STORE = S_entry.STORE', 'S_begin.ALLOCATIONS = S_entry.ALLOCATIONS',
    ]
    seek('S_capture', 'S_begin', 1)
    checks += [
        'S_capture.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 0) :: ptask_tail*',
        'pintegerconversion.INPUT = PFLOAT ' + str(LEFT_BITS),
        'pintegerconversion.VALUE = 12',
        'pintegerconversion.NOTICES = [(8192, $ptascii("Implicit conversion from float 12.5 to int loses precision"))]',
        '$integer_warning_valid(S_capture, pintegeroperation, INTEGER_LEFT, pintegerconversion, 0)',
        '~$integer_warning_valid(S_capture, pintegeroperation, INTEGER_LEFT, pintegerconversion[.VALUE = 99], 0)',
        '$task_nodes(INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 0) = eps',
        'PhpStep: S_capture ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 1',
        'perrorcall.LINE = 24', 'perrorcall.LEVEL = 8192',
        'perrorcall.MESSAGE = $ptascii("Implicit conversion from float 12.5 to int loses precision")',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = 25])',
        '$call_descriptors_valid(S_dispatch)',
    ]
    if throws:
        post = 'S_throw'
        checks += [
            'S_throw_found = $object_integer_seek_throw(S_dispatch, 2000)',
            'S_throw_found.COMPLETION = NORMAL \\/ S_throw_found.COMPLETION = BUDGET',
            'S_throw = S_throw_found[.COMPLETION = NORMAL]',
            '$object_integer_throw_front(S_throw)',
            'S_throw.TODO = (THROW_SEARCH n_failure) :: ptask_throw_tail*',
            '$lookup(S_throw.ENV, $ptascii("failure")) = (n_failure_cell)',
            'S_throw.STORE[n_failure_cell] = DEFINED (POBJECT n_failure)',
            '$throwable_live(S_throw, n_failure)',
            '$throwable_field(S_throw, n_failure, "line") = PINT 20',
            '$throwable_field(S_throw, n_failure, "previous") = PNULL',
            'S_throw.STORE[n_right] = DEFINED (PINT 5)',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_object) = 0',
        ]
    else:
        seek('S_return', 'S_dispatch', 3)
        checks += [
            'S_return.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 1) :: ptask_tail*',
            '$integer_warning_valid(S_return, pintegeroperation, INTEGER_LEFT, pintegerconversion, 1)',
            '$integer_pointer_value(S_return, pintegeroperation.LEFTPOINTER) = (PFLOAT ' + str(CHANGED_BITS) + ')',
            '$call_descriptors_valid(S_return)',
        ]
        seek('S_right', 'S_return', 4)
        checks += [
            'S_right.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT 12)) :: ptask_tail*',
            '$integer_operation_valid(S_right, pintegeroperation)',
            '$task_nodes(INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT 12)) = eps',
        ]
        if retains:
            post = 'S_throw'
            checks += [
                'S_right.STORE[n_right] = DEFINED (POBJECT n_object)',
                '$integer_plain_stdclass(S_right, POBJECT n_object)',
                '$integer_conversion(POBJECT n_object) = eps',
                'S_changed_type = $integer_failure(S_right[.STORE[n_left] = DEFINED (PINT 99)], pintegeroperation)',
                'S_changed_type.COMPLETION = THROWN "TypeError" ($ptascii("Unsupported operand types: int & stdClass")) 24',
                'PhpStep: S_right ~> S_failure',
                'S_failure = $integer_failure(S_right, pintegeroperation)',
                'S_failure.COMPLETION = THROWN "TypeError" ($ptascii("Unsupported operand types: float & stdClass")) 24',
                'S_throw_budget = $drive_steps(S_right, 1)',
                'S_throw_budget.COMPLETION = BUDGET',
                'S_throw = S_throw_budget[.COMPLETION = NORMAL]',
                'S_throw.TODO = (THROW_SEARCH n_failure) :: ptask_tail*',
                '$object_name(S_throw, n_failure) = $ptascii("TypeError")',
                '$throwable_field(S_throw, n_failure, "line") = PINT 24',
                '$throwable_field(S_throw, n_failure, "message") = pvalue_message',
                '$string_bytes(pvalue_message) = ($ptascii("Unsupported operand types: float & stdClass"))',
                '$throwable_field(S_throw, n_failure, "previous") = PNULL',
                '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_object) = 1',
            ]
        else:
            post = 'S_ready'
            seek('S_ready', 'S_right', 5)
            checks += [
                'S_ready.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT 12) pintegerconversion_right 0) :: ptask_tail*',
                'S_ready.STORE[n_right] = DEFINED (PINT 5)',
                'pintegerconversion_right.INPUT = PINT 5',
                'pintegerconversion_right.VALUE = 5', 'pintegerconversion_right.NOTICES = eps',
                '$integer_binary(' + op + ', 12, 5) = IRESULT ' + str(result),
                '$heap_owners($heap_prune($heap_graph(S_ready)), HOBJECT n_object) = 0',
            ]
    checks += [
        f'{post}.STORE[n_left] = DEFINED (PFLOAT ' + str(CHANGED_BITS) + ')',
        f'{post}.STORE[n_calls] = DEFINED (PINT 1)',
        f'{post}.STORE[n_v] = DEFINED (PINT 100)',
        f'$call_descriptors_valid({post})', f'$heap_valid($heap_graph({post}))',
        f'S_done = $drive_steps({post}, 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps',
        'S_done.STORE[n_v] = DEFINED (PINT ' + str(100 if throws or retains else result) + ')',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        f'$drive_steps({post}, 0) = {post}[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks


def main():
    path = Path(__file__)
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    shared.sources, shared.CASES, shared.HELPERS, shared.conditions = cases, CASES, HELPERS, conditions
    passed = shared.main()
    assert before == hashlib.sha256(path.read_bytes()).hexdigest()
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
