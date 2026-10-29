#!/usr/bin/env python3
"""Reached borrowed-CELL versus delayed-CV reads for an object RIGHT."""
import base64
import hashlib
import json
from pathlib import Path

import integer_reference_object_right_warning_cases as cases
import integer_operator_warning_protocol as shared
from integer_object_right_warning_protocol import HELPERS

CASES = ('mod-rebind', 'and-rebind', 'xor-write-rebind', 'shl-handler-throw')
LEFT_BITS = 4623226492472524800  # 12.5
CHANGED_BITS = 4636702106982547456  # 99.5
OPS = {'mod': ('MODULO', 2), 'and': ('BITAND', 4), 'xor': ('BITXOR', 14), 'shl': ('SHIFTLEFT', 384)}


def conditions(name, program, path, stdout):
    stem = name.split('-')[0]
    op, result = OPS[stem]
    bitwise = stem in ('and', 'xor')
    writes = '-write-' in name
    throws = name.endswith('handler-throw')
    fails = bitwise and not writes
    pointer = 'INTEGER_CELL n_old' if bitwise else 'INTEGER_CV ($ptascii("right"))'
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
        'pintegeroperation.OP = ' + op, 'pintegeroperation.LINE = 24',
        '~pintegeroperation.SWAPPED',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 24',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 24',
        'pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("left"))',
        'pintegeroperation.RIGHTPOINTER = ' + pointer,
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_old)',
        '$lookup(S_entry.ENV, $ptascii("alias")) = (n_old)',
        '$lookup(S_entry.ENV, $ptascii("replacement")) = (n_new)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'n_old =/= n_new', 'n_old <- S_entry.REFCELLS',
        '~(n_left <- S_entry.REFCELLS)', '~(n_new <- S_entry.REFCELLS)',
        'S_entry.STORE[n_left] = DEFINED (PFLOAT ' + str(LEFT_BITS) + ')',
        'S_entry.STORE[n_old] = DEFINED (POBJECT n_object)',
        'S_entry.STORE[n_new] = DEFINED (PINT 5)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '$integer_pointer_select(S_entry, pintegeroperation.RIGHT) = (INTEGER_CELL n_old)',
        '$integer_plain_stdclass(S_entry, POBJECT n_object)',
        '$integer_object_right_borrowed(S_entry, INTEGER_CELL n_old)',
        '~$integer_object_right_borrowed(S_entry, INTEGER_COPY (POBJECT n_object))',
        '$integer_object_right_initial(S_entry, pintegeroperation.LEFT, pintegeroperation.RIGHT, PFLOAT ' + str(LEFT_BITS) + ', POBJECT n_object, false)',
        '~$integer_object_right_initial(S_entry, pintegeroperation.LEFT, pintegeroperation.RIGHT, PFLOAT ' + str(LEFT_BITS) + ', POBJECT n_object, true)',
        '$integer_operation_valid(S_entry, pintegeroperation)',
        '~$integer_operation_valid(S_entry, pintegeroperation[.LINE = 25])',
        '~$integer_operation_valid(S_entry, pintegeroperation[.SWAPPED = true])',
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
        'pintegerconversion.INPUT = PFLOAT ' + str(LEFT_BITS),
        'pintegerconversion.VALUE = 12',
        'pintegerconversion.NOTICES = [(8192, $ptascii("Implicit conversion from float 12.5 to int loses precision"))]',
        '$integer_warning_valid(S_capture, pintegeroperation, INTEGER_LEFT, pintegerconversion, 0)',
        '$task_nodes(INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 0) = eps',
        'PhpStep: S_capture ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 1',
        'perrorcall.LINE = 24', 'perrorcall.LEVEL = 8192',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = 25])',
    ]
    if throws:
        post = 'S_throw'
        checks += [
            'S_throw_found = $object_integer_seek_throw(S_dispatch, 2200)',
            'S_throw_found.COMPLETION = NORMAL \\/ S_throw_found.COMPLETION = BUDGET',
            'S_throw = S_throw_found[.COMPLETION = NORMAL]',
            '$object_integer_throw_front(S_throw)',
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
            '~$integer_object_right_borrowed(S_return, INTEGER_CELL n_old)',
        ]
        seek('S_right', 'S_return', 4)
        checks += [
            'S_right.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT 12)) :: ptask_tail*',
            '$integer_operation_valid(S_right, pintegeroperation)',
            '$task_nodes(INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT 12)) = eps',
            '$integer_pointer_value(S_right, INTEGER_CV ($ptascii("right"))) = (PINT 5)',
        ]
        if fails:
            post = 'S_throw'
            checks += [
                '$integer_pointer_value(S_right, pintegeroperation.RIGHTPOINTER) = (POBJECT n_object)',
                '$integer_conversion(POBJECT n_object) = eps',
                'PhpStep: S_right ~> S_failure',
                'S_failure = $integer_failure(S_right, pintegeroperation)',
                'S_failure.COMPLETION = THROWN "TypeError" ($ptascii("Unsupported operand types: float & stdClass")) 24',
                'S_throw_budget = $drive_steps(S_right, 1)',
                'S_throw_budget.COMPLETION = BUDGET',
                'S_throw = S_throw_budget[.COMPLETION = NORMAL]',
                'S_throw.TODO = (THROW_SEARCH n_failure) :: ptask_tail*',
                '$object_name(S_throw, n_failure) = $ptascii("TypeError")',
                '$throwable_field(S_throw, n_failure, "line") = PINT 24',
                '$throwable_field(S_throw, n_failure, "previous") = PNULL',
            ]
        else:
            post = 'S_ready'
            seek('S_ready', 'S_right', 5)
            right = 2 if writes else 5
            checks += [
                'S_ready.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT 12) pintegerconversion_right 0) :: ptask_tail*',
                'pintegerconversion_right.INPUT = PINT ' + str(right),
                'pintegerconversion_right.VALUE = ' + str(right),
                'pintegerconversion_right.NOTICES = eps',
                '$integer_pointer_value(S_ready, pintegeroperation.RIGHTPOINTER) = (PINT ' + str(right) + ')',
                '$integer_binary(' + op + ', 12, ' + str(right) + ') = IRESULT ' + str(result),
            ]
    checks += [
        f'$lookup({post}.ENV, $ptascii("right")) = (n_new)',
        f'$lookup({post}.ENV, $ptascii("alias")) = (n_old)',
        f'n_old <- {post}.REFCELLS', f'n_new <- {post}.REFCELLS',
        f'{post}.STORE[n_old] = DEFINED (' + ('PINT 2' if writes else 'POBJECT n_object') + ')',
        f'{post}.STORE[n_new] = DEFINED (PINT 5)',
        f'{post}.STORE[n_left] = DEFINED (PFLOAT ' + str(CHANGED_BITS) + ')',
        f'{post}.STORE[n_calls] = DEFINED (PINT 1)',
        f'{post}.STORE[n_v] = DEFINED (PINT 100)',
        f'$heap_owners($heap_prune($heap_graph({post})), HCELL n_old) = 1',
        f'$heap_owners($heap_prune($heap_graph({post})), HCELL n_new) = 2',
        f'$heap_owners($heap_prune($heap_graph({post})), HOBJECT n_object) = ' + ('0' if writes else '1'),
        f'$call_descriptors_valid({post})', f'$heap_valid($heap_graph({post}))',
        f'S_done = $drive_steps({post}, 2200)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps',
        'S_done.STORE[n_old] = DEFINED (PINT 7)',
        'S_done.STORE[n_new] = DEFINED (PINT 5)',
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
