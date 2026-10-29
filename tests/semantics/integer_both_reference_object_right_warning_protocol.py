#!/usr/bin/env python3
"""Reached both-cell conversion snapshots, selected types and two rebinds."""
import base64
import hashlib
import json
from pathlib import Path

import integer_both_reference_object_right_warning_cases as cases
import integer_operator_warning_protocol as shared
from integer_object_right_warning_protocol import HELPERS

CASES = ('mod-rebind', 'xor-write-both', 'and-left-int-typeerror', 'xor-handler-throw')
LEFT_BITS = 4623226492472524800  # 12.5
RIGHT_BITS = 4617878467915022336  # 5.5
OPS = {'mod': ('MODULO', 2), 'xor': ('BITXOR', 14), 'and': ('BITAND', 4)}


def conditions(name, program, path, stdout):
    stem = name.split('-')[0]
    op, result = OPS[stem]
    bitwise = stem != 'mod'
    writes = name != 'mod-rebind'
    writes_right = '-write-' in name
    throws = name.endswith('handler-throw')
    fails = 'typeerror' in name
    live_right = 0 if throws else 5
    old_right = 'PFLOAT ' + str(RIGHT_BITS) if throws else ('PINT 2' if writes_right else 'POBJECT n_object')
    pointer = 'INTEGER_CELL n_old_right' if bitwise else 'INTEGER_CV ($ptascii("right"))'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $integer_seek({before}, {stage}, 2400)',
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
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_old_left)',
        '$lookup(S_entry.ENV, $ptascii("leftAlias")) = (n_old_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_old_right)',
        '$lookup(S_entry.ENV, $ptascii("rightAlias")) = (n_old_right)',
        '$lookup(S_entry.ENV, $ptascii("newLeft")) = (n_new_left)',
        '$lookup(S_entry.ENV, $ptascii("newRight")) = (n_new_right)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'n_old_left =/= n_new_left', 'n_old_right =/= n_new_right',
        'n_old_left <- S_entry.REFCELLS', 'n_old_right <- S_entry.REFCELLS',
        '~(n_new_left <- S_entry.REFCELLS)', '~(n_new_right <- S_entry.REFCELLS)',
        'S_entry.STORE[n_old_left] = DEFINED (PFLOAT ' + str(LEFT_BITS) + ')',
        'S_entry.STORE[n_old_right] = DEFINED (POBJECT n_object)',
        'S_entry.STORE[n_new_left] = DEFINED (PBOOL true)',
        'S_entry.STORE[n_new_right] = DEFINED (PINT ' + str(live_right) + ')',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_old_left',
        'pintegeroperation.RIGHTPOINTER = ' + pointer,
        '$integer_pointer_select(S_entry, pintegeroperation.RIGHT) = (INTEGER_CELL n_old_right)',
        '$integer_object_right_borrowed(S_entry, INTEGER_CELL n_old_left)',
        '$integer_object_right_borrowed(S_entry, INTEGER_CELL n_old_right)',
        '$integer_object_right_initial(S_entry, pintegeroperation.LEFT, pintegeroperation.RIGHT, PFLOAT ' + str(LEFT_BITS) + ', POBJECT n_object, false)',
        '~$integer_object_right_initial(S_entry, pintegeroperation.LEFT, pintegeroperation.RIGHT, PFLOAT ' + str(LEFT_BITS) + ', POBJECT n_object, true)',
        '$integer_operation_valid(S_entry, pintegeroperation)',
        '~$integer_operation_valid(S_entry, pintegeroperation[.LINE = 25])',
        '$integer_operator_plan(S_entry[.ORIGIN = eps]) = eps',
        '$task_nodes(INTEGER_OPERATOR_CONVERT pintegeroperation INTEGER_LEFT) = eps',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_old_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_old_right) = 2',
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
            'S_throw_found = $object_integer_seek_throw(S_dispatch, 2400)',
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
            '~$integer_object_right_borrowed(S_return, INTEGER_CELL n_old_left)',
            '~$integer_object_right_borrowed(S_return, INTEGER_CELL n_old_right)',
            '$integer_pointer_value(S_return, INTEGER_CV ($ptascii("left"))) = (PBOOL true)',
            '$integer_pointer_value(S_return, INTEGER_CV ($ptascii("right"))) = (PINT 5)',
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
            right = 2 if bitwise else 5
            checks += [
                'S_ready.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT 12) pintegerconversion_right 0) :: ptask_tail*',
                'pintegerconversion_right.INPUT = PINT ' + str(right),
                'pintegerconversion_right.VALUE = ' + str(right), 'pintegerconversion_right.NOTICES = eps',
                '$integer_binary(' + op + ', 12, ' + str(right) + ') = IRESULT ' + str(result),
            ]
    checks += [
        f'$lookup({post}.ENV, $ptascii("left")) = (n_new_left)',
        f'$lookup({post}.ENV, $ptascii("leftAlias")) = (n_old_left)',
        f'$lookup({post}.ENV, $ptascii("right")) = (n_new_right)',
        f'$lookup({post}.ENV, $ptascii("rightAlias")) = (n_old_right)',
        f'{post}.STORE[n_old_left] = DEFINED (' + ('PINT 99' if writes else 'PFLOAT ' + str(LEFT_BITS)) + ')',
        f'{post}.STORE[n_old_right] = DEFINED (' + old_right + ')',
        f'{post}.STORE[n_new_left] = DEFINED (PBOOL true)',
        f'{post}.STORE[n_new_right] = DEFINED (PINT ' + str(live_right) + ')',
        f'{post}.STORE[n_calls] = DEFINED (PINT 1)', f'{post}.STORE[n_v] = DEFINED (PINT 100)',
        f'$heap_owners($heap_prune($heap_graph({post})), HCELL n_old_left) = 1',
        f'$heap_owners($heap_prune($heap_graph({post})), HCELL n_old_right) = 1',
        f'$heap_owners($heap_prune($heap_graph({post})), HCELL n_new_left) = 2',
        f'$heap_owners($heap_prune($heap_graph({post})), HCELL n_new_right) = 2',
        f'$heap_owners($heap_prune($heap_graph({post})), HOBJECT n_object) = ' + ('0' if writes_right or throws else '1'),
        f'$call_descriptors_valid({post})', f'$heap_valid($heap_graph({post}))',
        f'S_done = $drive_steps({post}, 2400)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps',
        'S_done.STORE[n_old_left] = DEFINED (PINT 7)', 'S_done.STORE[n_old_right] = DEFINED (PINT 3)',
        'S_done.STORE[n_new_left] = DEFINED (PBOOL true)',
        'S_done.STORE[n_new_right] = DEFINED (PINT ' + str(live_right) + ')',
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
