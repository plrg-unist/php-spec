#!/usr/bin/env python3
"""Source-reached saved LEFT conversion versus its rebound CV and old CELL."""
import base64
import hashlib
import json
from pathlib import Path

import integer_reference_left_object_right_warning_cases as cases
import integer_operator_warning_protocol as shared
from integer_object_right_warning_protocol import HELPERS as COMMON_HELPERS

CASES = ('mod-write-repair', 'and-retain-int-typeerror', 'xor-repair', 'shl-handler-throw', 'both-shared-boundary')
LEFT_BITS = 4623226492472524800  # 12.5
OPS = {'mod': ('MODULO', 2), 'and': ('BITAND', 4), 'xor': ('BITXOR', 9), 'shl': ('SHIFTLEFT', 384)}
HELPERS = COMMON_HELPERS + r'''
dec $left_object_boundary_front(pstate) : bool
def $left_object_boundary_front(S) = true
  -- if S.TODO = (BINARY_RIGHT MODULO poperand_left z) :: ptask_tail*
  -- if $integer_pointer_select(S, poperand_left) = (INTEGER_CELL n_left)
  -- if $integer_pointer_select(S, S.RESULT) = (INTEGER_CELL n_right)
  -- if $integer_pointer_value(S, INTEGER_CELL n_right) = (pvalue_right)
  -- if $integer_plain_stdclass(S, pvalue_right)
def $left_object_boundary_front(S) = false -- otherwise
dec $left_object_seek_boundary(pstate, nat) : pstate
def $left_object_seek_boundary(S, n) = S -- if $left_object_boundary_front(S)
def $left_object_seek_boundary(S, n) = S
  -- if ~$left_object_boundary_front(S)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $left_object_seek_boundary(S, n) = S
  -- if ~$left_object_boundary_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $left_object_seek_boundary(S, n) = $left_object_seek_boundary($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$left_object_boundary_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def boundary_conditions(program, path):
    return [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $left_object_seek_boundary(S_initial, 2200)',
        'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]', '$left_object_boundary_front(S_entry)',
        'S_entry.TODO = (BINARY_RIGHT MODULO poperand_left 24) :: ptask_tail*',
        'S_entry.RESULT = VARIABLE ($ptascii("right")) 24',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("alias")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'n_left <- S_entry.REFCELLS', 'n_right <- S_entry.REFCELLS',
        'S_entry.STORE[n_left] = DEFINED (PFLOAT ' + str(LEFT_BITS) + ')',
        'S_entry.STORE[n_right] = DEFINED (POBJECT n_object)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 2',
        '$integer_object_right_borrowed(S_entry, INTEGER_CELL n_left)',
        '$integer_object_right_borrowed(S_entry, INTEGER_CELL n_right)',
        '~$integer_object_right_initial(S_entry, poperand_left, S_entry.RESULT, PFLOAT ' + str(LEFT_BITS) + ', POBJECT n_object, false)',
        '$integer_operator_plan(S_entry) = eps',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'S_done = $drive_steps(S_entry, 2200)',
        'S_done.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"',
        'S_done.STORE[n_v] = DEFINED (PINT 100)',
        '$integer_outputs(S_done.EVENTS) = eps',
    ]


def conditions(name, program, path, stdout):
    if name == 'both-shared-boundary':
        return boundary_conditions(program, path)
    stem = name.split('-')[0]
    op, result = OPS[stem]
    writes = '-write-' in name or 'retain-int' in name or name.endswith('handler-throw')
    throws = name.endswith('handler-throw')
    fails = 'retain' in name
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $integer_seek({before}, {stage}, 2200)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$integer_frontier({state}, {stage})',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$integer_operator_plan(S_entry) = (pintegeroperation)',
        'S_entry.TODO = (BINARY_RIGHT ' + op + ' poperand_left 24) :: ptask_tail*',
        'S_entry.ORIGIN = (porigin)', 'pintegeroperation.SITE = porigin',
        'pintegeroperation.OP = ' + op, 'pintegeroperation.LINE = 24', '~pintegeroperation.SWAPPED',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 24',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 24',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_old)',
        '$lookup(S_entry.ENV, $ptascii("alias")) = (n_old)',
        '$lookup(S_entry.ENV, $ptascii("replacement")) = (n_new)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'n_old =/= n_new', 'n_old <- S_entry.REFCELLS',
        '~(n_new <- S_entry.REFCELLS)', '~(n_right <- S_entry.REFCELLS)',
        'S_entry.STORE[n_old] = DEFINED (PFLOAT ' + str(LEFT_BITS) + ')',
        'S_entry.STORE[n_new] = DEFINED (PBOOL true)',
        'S_entry.STORE[n_right] = DEFINED (POBJECT n_object)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_old',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))',
        '$integer_object_right_borrowed(S_entry, pintegeroperation.LEFTPOINTER)',
        '$integer_object_right_borrowed(S_entry, pintegeroperation.RIGHTPOINTER)',
        '$integer_object_right_initial(S_entry, pintegeroperation.LEFT, pintegeroperation.RIGHT, PFLOAT ' + str(LEFT_BITS) + ', POBJECT n_object, false)',
        '~$integer_object_right_initial(S_entry, pintegeroperation.LEFT, pintegeroperation.RIGHT, PFLOAT ' + str(LEFT_BITS) + ', POBJECT n_object, true)',
        '$integer_operation_valid(S_entry, pintegeroperation)',
        '~$integer_operation_valid(S_entry, pintegeroperation[.LINE = 25])',
        '$integer_operator_plan(S_entry[.ORIGIN = eps]) = eps',
        '$task_nodes(INTEGER_OPERATOR_CONVERT pintegeroperation INTEGER_LEFT) = eps',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_old) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HOBJECT n_object) = 1',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'PhpStep: S_entry ~> S_begin',
        'S_begin = S_entry[.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation INTEGER_LEFT) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_begin.STORE = S_entry.STORE', 'S_begin.ALLOCATIONS = S_entry.ALLOCATIONS',
    ]
    seek('S_capture', 'S_begin', 1)
    checks += [
        'S_capture.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 0) :: ptask_tail*',
        'pintegerconversion.INPUT = PFLOAT ' + str(LEFT_BITS), 'pintegerconversion.VALUE = 12',
        'pintegerconversion.NOTICES = [(8192, $ptascii("Implicit conversion from float 12.5 to int loses precision"))]',
        '$integer_warning_valid(S_capture, pintegeroperation, INTEGER_LEFT, pintegerconversion, 0)',
        '$task_nodes(INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 0) = eps',
        'PhpStep: S_capture ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 1',
        'perrorcall.LINE = 24', 'perrorcall.LEVEL = 8192', '$error_call_valid(S_dispatch, perrorcall)',
    ]
    if throws:
        post = 'S_throw'
        checks += [
            'S_throw_found = $object_integer_seek_throw(S_dispatch, 2200)',
            'S_throw_found.COMPLETION = NORMAL \\/ S_throw_found.COMPLETION = BUDGET',
            'S_throw = S_throw_found[.COMPLETION = NORMAL]', '$object_integer_throw_front(S_throw)',
            'S_throw.TODO = (THROW_SEARCH n_failure) :: ptask_throw_tail*',
            '$lookup(S_throw.ENV, $ptascii("failure")) = (n_failure_cell)',
            'S_throw.STORE[n_failure_cell] = DEFINED (POBJECT n_failure)',
            '$throwable_live(S_throw, n_failure)',
            '$throwable_field(S_throw, n_failure, "line") = PINT 20',
            '$throwable_field(S_throw, n_failure, "previous") = PNULL',
        ]
    else:
        seek('S_return', 'S_dispatch', 3)
        checks += [
            'S_return.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 1) :: ptask_tail*',
            '$integer_warning_valid(S_return, pintegeroperation, INTEGER_LEFT, pintegerconversion, 1)',
            '$integer_operation_valid(S_return, pintegeroperation)',
            '~$integer_object_right_borrowed(S_return, pintegeroperation.LEFTPOINTER)',
            '$integer_pointer_value(S_return, INTEGER_CV ($ptascii("left"))) = (PBOOL true)',
            '$integer_pointer_value(S_return, pintegeroperation.LEFTPOINTER) = (' + ('PINT 99' if writes else 'PFLOAT ' + str(LEFT_BITS)) + ')',
        ]
        seek('S_right', 'S_return', 4)
        checks += [
            'S_right.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT 12)) :: ptask_tail*',
            '$integer_operation_valid(S_right, pintegeroperation)',
            '$task_nodes(INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT 12)) = eps',
        ]
        if fails:
            post = 'S_throw'
            checks += [
                '$integer_pointer_value(S_right, pintegeroperation.RIGHTPOINTER) = (POBJECT n_object)',
                'PhpStep: S_right ~> S_failure', 'S_failure = $integer_failure(S_right, pintegeroperation)',
                'S_failure.COMPLETION = THROWN "TypeError" ($ptascii("Unsupported operand types: int & stdClass")) 24',
                'S_throw_budget = $drive_steps(S_right, 1)', 'S_throw_budget.COMPLETION = BUDGET',
                'S_throw = S_throw_budget[.COMPLETION = NORMAL]',
                'S_throw.TODO = (THROW_SEARCH n_failure) :: ptask_tail*',
                '$object_name(S_throw, n_failure) = $ptascii("TypeError")',
                '$throwable_field(S_throw, n_failure, "line") = PINT 24',
                '$throwable_field(S_throw, n_failure, "previous") = PNULL',
            ]
        else:
            post = 'S_ready'
            seek('S_ready', 'S_right', 5)
            checks += [
                'S_ready.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT 12) pintegerconversion_right 0) :: ptask_tail*',
                'pintegerconversion_right.INPUT = PINT 5', 'pintegerconversion_right.VALUE = 5',
                'pintegerconversion_right.NOTICES = eps',
                '$integer_binary(' + op + ', 12, 5) = IRESULT ' + str(result),
            ]
    checks += [
        f'$lookup({post}.ENV, $ptascii("left")) = (n_new)',
        f'$lookup({post}.ENV, $ptascii("alias")) = (n_old)',
        f'{post}.STORE[n_old] = DEFINED (' + ('PINT 99' if writes else 'PFLOAT ' + str(LEFT_BITS)) + ')',
        f'{post}.STORE[n_new] = DEFINED (PBOOL true)',
        f'{post}.STORE[n_right] = DEFINED (' + ('POBJECT n_object' if fails else 'PINT 5') + ')',
        f'{post}.STORE[n_calls] = DEFINED (PINT 1)', f'{post}.STORE[n_v] = DEFINED (PINT 100)',
        f'$heap_owners($heap_prune($heap_graph({post})), HCELL n_old) = 1',
        f'$heap_owners($heap_prune($heap_graph({post})), HCELL n_new) = 2',
        f'$heap_owners($heap_prune($heap_graph({post})), HOBJECT n_object) = ' + ('1' if fails else '0'),
        f'$call_descriptors_valid({post})', f'$heap_valid($heap_graph({post}))',
        f'S_done = $drive_steps({post}, 2200)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps',
        'S_done.STORE[n_old] = DEFINED (PINT 7)', 'S_done.STORE[n_new] = DEFINED (PBOOL true)',
        'S_done.STORE[n_v] = DEFINED (PINT ' + str(100 if fails or throws else result) + ')',
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
