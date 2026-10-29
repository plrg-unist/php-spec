#!/usr/bin/env python3
"""Reached owning LEFT replacements, raw failure names and last-owner release."""
import base64
import hashlib
import json
from pathlib import Path

import integer_late_owning_left_warning_cases as cases
import integer_operator_warning_protocol as shared
from integer_object_right_warning_protocol import HELPERS

CASES = ('xor-both-object-error', 'mod-cell-array-error', 'shl-cv-repair-control', 'mod-cell-handler-throw')
LEFT_BITS = 4623226492472524800
OPS = {'xor': 'BITXOR', 'mod': 'MODULO', 'shl': 'SHIFTLEFT'}


def conditions(name, program, path, stdout):
    op = OPS[name.split('-')[0]]
    cell = '-cv-' not in name
    both = '-both-' in name
    throws = name.endswith('handler-throw')
    succeeds = name.endswith('repair-control')
    array = '-array-' in name
    target = 'leftAlias' if cell else 'left'
    left_pointer = 'INTEGER_CELL n_left' if cell else 'INTEGER_CV ($ptascii("left"))'
    right_pointer = 'INTEGER_CELL n_right' if both else 'INTEGER_CV ($ptascii("right"))'
    initial_right = 'PARRAY n_array' if array else 'POBJECT n_right_object'
    message = 'Unsupported operand types: LateLeft ' + cases.OPS[name.split('-')[0]] + (' array' if array else ' stdClass')
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $integer_seek({before}, {stage}, 3000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$integer_frontier({state}, {stage})',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$integer_operator_plan(S_entry) = (pintegeroperation)',
        'S_entry.TODO = (BINARY_RIGHT ' + op + ' poperand_left 40) :: ptask_tail*',
        'pintegeroperation.OP = ' + op, 'pintegeroperation.LINE = 40', '~pintegeroperation.SWAPPED',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 40',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 40',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("newLeft")) = (n_new_left)',
        '$lookup(S_entry.ENV, $ptascii("newRight")) = (n_new_right)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("drops")) = (n_drops)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'S_entry.STORE[n_left] = DEFINED (PFLOAT ' + str(LEFT_BITS) + ')',
        'S_entry.STORE[n_right] = DEFINED (' + initial_right + ')',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'pintegeroperation.LEFTPOINTER = ' + left_pointer,
        'pintegeroperation.RIGHTPOINTER = ' + right_pointer,
        '$integer_operation_valid(S_entry, pintegeroperation)',
        '~$integer_operation_valid(S_entry, pintegeroperation[.LINE = 41])',
        '$integer_operator_plan(S_entry[.ORIGIN = eps]) = eps',
        '$task_nodes(INTEGER_OPERATOR_CONVERT pintegeroperation INTEGER_LEFT) = eps',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'PhpStep: S_entry ~> S_begin',
        'S_begin.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation INTEGER_LEFT) :: ptask_tail*',
        'S_begin.STORE = S_entry.STORE', 'S_begin.ALLOCATIONS = S_entry.ALLOCATIONS',
    ]
    if cell:
        checks += [
            '$lookup(S_entry.ENV, $ptascii("leftAlias")) = (n_left)',
            'n_left <- S_entry.REFCELLS',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 2',
        ]
    else:
        checks += ['~(n_left <- S_entry.REFCELLS)']
    if both:
        checks += [
            '$lookup(S_entry.ENV, $ptascii("rightAlias")) = (n_right)',
            'n_right <- S_entry.REFCELLS',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 2',
        ]
    seek('S_capture', 'S_begin', 1)
    checks += [
        'S_capture.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 0) :: ptask_tail*',
        'pintegerconversion.INPUT = PFLOAT ' + str(LEFT_BITS), 'pintegerconversion.VALUE = 12',
        'pintegerconversion.NOTICES = [(8192, $ptascii("Implicit conversion from float 12.5 to int loses precision"))]',
        '$integer_warning_valid(S_capture, pintegeroperation, INTEGER_LEFT, pintegerconversion, 0)',
        '~$integer_warning_valid(S_capture, pintegeroperation, INTEGER_LEFT, pintegerconversion[.VALUE = 99], 0)',
        'PhpStep: S_capture ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 1',
        'perrorcall.LINE = 40', 'perrorcall.LEVEL = 8192', '$error_call_valid(S_dispatch, perrorcall)',
    ]
    if throws:
        post = 'S_throw'
        checks += [
            'S_throw_found = $object_integer_seek_throw(S_dispatch, 3000)',
            'S_throw_found.COMPLETION = NORMAL \\/ S_throw_found.COMPLETION = BUDGET',
            'S_throw = S_throw_found[.COMPLETION = NORMAL]', '$object_integer_throw_front(S_throw)',
            'S_throw.TODO = (THROW_SEARCH n_failure) :: ptask_throw_tail*',
            '$lookup(S_throw.ENV, $ptascii("failure")) = (n_failure_cell)',
            'S_throw.STORE[n_failure_cell] = DEFINED (POBJECT n_failure)',
            '$throwable_field(S_throw, n_failure, "line") = PINT 36',
            '$throwable_field(S_throw, n_failure, "previous") = PNULL',
        ]
    else:
        seek('S_return', 'S_dispatch', 3)
        checks += [
            'S_return.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 1) :: ptask_tail*',
            '$integer_warning_valid(S_return, pintegeroperation, INTEGER_LEFT, pintegerconversion, 1)',
            '$integer_operation_valid(S_return, pintegeroperation)',
            '$task_nodes(INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 1) = eps',
        ]
        seek('S_right', 'S_return', 4)
        checks += [
            'S_right.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT 12)) :: ptask_tail*',
            '$integer_operation_valid(S_right, pintegeroperation)',
            '$integer_pointer_value(S_right, pintegeroperation.LEFTPOINTER) = (POBJECT n_late)',
        ]
        if succeeds:
            post = 'S_ready'
            seek('S_ready', 'S_right', 5)
            checks += [
                'S_ready.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT 12) pintegerconversion_right 0) :: ptask_tail*',
                'pintegerconversion_right.INPUT = PINT 5', 'pintegerconversion_right.VALUE = 5',
                'pintegerconversion_right.NOTICES = eps',
                '$integer_binary(SHIFTLEFT, 12, 5) = IRESULT 384',
            ]
        else:
            post = 'S_throw'
            checks += [
                '$integer_pointer_value(S_right, pintegeroperation.RIGHTPOINTER) = (' + initial_right + ')',
                'PhpStep: S_right ~> S_failure', 'S_failure = $integer_failure(S_right, pintegeroperation)',
                'S_failure.COMPLETION = THROWN "TypeError" ($ptascii(' + json.dumps(message) + ')) 40',
                'S_failure.TODO = ptask_tail*', 'S_failure.STORE = S_right.STORE',
                'S_failure.ALLOCATIONS = S_right.ALLOCATIONS',
                # Derived helper-state guards, not extra reached sources.
                'S_first_phase = $integer_failure(S_right[.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation INTEGER_LEFT) :: ptask_tail*], pintegeroperation)',
                'S_first_phase.COMPLETION = UNSUPPORTED "integer operator object or expired pointer"',
                'S_missing_allocation = $integer_failure(S_right[.ALLOCATIONS = eps], pintegeroperation)',
                'S_missing_allocation.COMPLETION = UNSUPPORTED "integer operator object or expired pointer"',
                'S_throw_budget = $drive_steps(S_right, 1)', 'S_throw_budget.COMPLETION = BUDGET',
                'S_throw = S_throw_budget[.COMPLETION = NORMAL]',
                'S_throw.TODO = (THROW_SEARCH n_failure) :: ptask_tail*',
                '$object_name(S_throw, n_failure) = $ptascii("TypeError")',
                '$throwable_field(S_throw, n_failure, "line") = PINT 40',
                '$throwable_field(S_throw, n_failure, "previous") = PNULL',
            ]
    checks += [
        f'$lookup({post}.ENV, $ptascii("{target}")) = (n_left)',
        f'{post}.STORE[n_left] = DEFINED (POBJECT n_late)',
        f'$object_name({post}, n_late) = $ptascii("LateLeft")',
        f'$(n_late < |{post}.OBJECTS|)', f'(HOBJECT n_late) <- {post}.ALLOCATIONS',
        f'$lookup({post}.ENV, $ptascii("weak")) = (n_weak_cell)',
        f'{post}.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
        f'$weakref_get({post}, n_weak) = POBJECT n_late',
        f'{post}.STORE[n_calls] = DEFINED (PINT 1)', f'{post}.STORE[n_drops] = DEFINED (PINT 0)',
        f'{post}.STORE[n_v] = DEFINED (PINT 100)',
        f'$heap_owners($heap_prune($heap_graph({post})), HOBJECT n_late) = 1',
        '$task_nodes(INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT 12)) = eps',
        f'$call_descriptors_valid({post})', f'$heap_valid($heap_graph({post}))',
    ]
    if cell:
        checks += [
            f'$lookup({post}.ENV, $ptascii("left")) = (n_new_left)',
            f'{post}.STORE[n_new_left] = DEFINED (PINT 99)',
            f'$heap_owners($heap_prune($heap_graph({post})), HCELL n_left) = 1',
            f'$heap_owners($heap_prune($heap_graph({post})), HCELL n_new_left) = 2',
        ]
    if both:
        checks += [
            f'$lookup({post}.ENV, $ptascii("right")) = (n_new_right)',
            f'$lookup({post}.ENV, $ptascii("rightAlias")) = (n_right)',
            f'{post}.STORE[n_right] = DEFINED (POBJECT n_right_object)',
            f'{post}.STORE[n_new_right] = DEFINED (PINT 5)',
            f'$heap_owners($heap_prune($heap_graph({post})), HCELL n_right) = 1',
            f'$heap_owners($heap_prune($heap_graph({post})), HCELL n_new_right) = 2',
        ]
    if not array:
        checks += [f'$heap_owners($heap_prune($heap_graph({post})), HOBJECT n_right_object) = ' + ('0' if succeeds or throws else '1')]
    checks += [
        f'S_done = $drive_steps({post}, 3000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps',
        '$weakref_get(S_done, n_weak) = PNULL',
        '~((HOBJECT n_late) <- S_done.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HOBJECT n_late) = 0',
        'S_done.STORE[n_drops] = DEFINED (PINT 1)',
        'S_done.STORE[n_v] = DEFINED (PINT ' + ('384' if succeeds else '100') + ')',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        f'$drive_steps({post}, 0) = {post}[.COMPLETION = BUDGET]',
    ]
    if cell:
        checks += [
            '$lookup(S_done.ENV, $ptascii("leftAlias")) = eps',
            '$integer_pointer_value(S_done, INTEGER_CELL n_left) = eps',
            'S_done.STORE[n_new_left] = DEFINED (PINT 99)',
        ]
    else:
        checks += ['S_done.STORE[n_left] = DEFINED (PINT 7)']
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
