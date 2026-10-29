#!/usr/bin/env python3
"""Reached handler capability, receiver/field owners and callback teardown."""
import base64
import hashlib
import json
from pathlib import Path

import integer_standard_handler_right_warning_cases as cases
import integer_operator_warning_protocol as shared
from integer_object_right_warning_protocol import HELPERS

CASES = ('mod-repair-destructor', 'xor-cell-rebind', 'mod-materialized-stdclass', 'shl-supplied-throw')
LEFT_BITS = 4623226492472524800
OPS = {'mod': 'MODULO', 'xor': 'BITXOR', 'shl': 'SHIFTLEFT'}


def conditions(name, program, path, stdout):
    op = OPS[name.split('-')[0]]
    cell = name == 'xor-cell-rebind'
    table = name == 'mod-materialized-stdclass'
    throws = name == 'shl-supplied-throw'
    repaired = name == 'mod-repair-destructor'
    live_right = 5 if cell or table else 7
    right_pointer = 'INTEGER_CELL n_right' if cell else 'INTEGER_CV ($ptascii("right"))'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $integer_seek({before}, {stage}, 4000)',
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
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("strings")) = (n_strings)',
        '$lookup(S_entry.ENV, $ptascii("drops")) = (n_drops)',
        '$lookup(S_entry.ENV, $ptascii("tokenDrops")) = (n_token_drops)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("weakRight")) = (n_weak_right_cell)',
        '$lookup(S_entry.ENV, $ptascii("weakChild")) = (n_weak_child_cell)',
        'S_entry.STORE[n_left] = DEFINED (PFLOAT ' + str(LEFT_BITS) + ')',
        'S_entry.STORE[n_right] = DEFINED (POBJECT n_receiver)',
        'S_entry.STORE[n_weak_right_cell] = DEFINED (POBJECT n_weak_right)',
        'S_entry.STORE[n_weak_child_cell] = DEFINED (POBJECT n_weak_child)',
        '$weakref_get(S_entry, n_weak_right) = POBJECT n_receiver',
        '$weakref_get(S_entry, n_weak_child) = POBJECT n_child',
        '$objectprops_at(S_entry.OBJECTPROPS, n_receiver) = (ppropertyslot*)',
        '$property_slot_at(ppropertyslot*, $ptascii("payload")) = (ppropertyslot_payload)',
        'ppropertyslot_payload.STATE = PROP_VALUE (DIRECT (POBJECT n_child))',
        'pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("left"))',
        'pintegeroperation.RIGHTPOINTER = ' + right_pointer,
        '$integer_standard_object_handlers(S_entry, POBJECT n_receiver)',
        '~$integer_plain_stdclass(S_entry, POBJECT n_receiver)',
        '$integer_object_right_initial(S_entry, pintegeroperation.LEFT, pintegeroperation.RIGHT, PFLOAT ' + str(LEFT_BITS) + ', POBJECT n_receiver, false)',
        '$integer_operation_valid(S_entry, pintegeroperation)',
        '~$integer_operation_valid(S_entry, pintegeroperation[.LINE = 41])',
        '$integer_operator_plan(S_entry[.ORIGIN = eps]) = eps',
        '$task_nodes(INTEGER_OPERATOR_CONVERT pintegeroperation INTEGER_LEFT) = eps',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HOBJECT n_receiver) = 1',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HOBJECT n_child) = 1',
        'S_entry.OBJECTS[n_weak_right] = WEAKREFERENCE (n_receiver)',
        '(HOBJECT n_weak_right) <- S_entry.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HOBJECT n_weak_right) = 1',
        '~$integer_standard_object_handlers(S_entry, POBJECT n_weak_right)',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'PhpStep: S_entry ~> S_begin',
        'S_begin.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation INTEGER_LEFT) :: ptask_tail*',
        'S_begin.STORE = S_entry.STORE', 'S_begin.ALLOCATIONS = S_entry.ALLOCATIONS',
    ]
    if cell:
        checks += [
            '$lookup(S_entry.ENV, $ptascii("rightAlias")) = (n_right)',
            '$lookup(S_entry.ENV, $ptascii("newRight")) = (n_new_right)',
            'n_right <- S_entry.REFCELLS',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 2',
        ]
    else:
        checks += ['~(n_right <- S_entry.REFCELLS)']
    if table:
        checks += [
            'S_entry.OBJECTS[n_receiver] = STDINSTANCE',
            '$lookup(S_entry.ENV, $ptascii("snapshot")) = (n_snapshot)',
            'S_entry.STORE[n_snapshot] = DEFINED (PARRAY n_table)',
            '$object_table_at(S_entry.OBJECTTABLES, n_receiver) = (n_table)',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_table) = 2',
        ]
    else:
        checks += [
            'S_entry.OBJECTS[n_receiver] = INSTANCE porigin_right',
            '$object_name(S_entry, n_receiver) = $ptascii("RightBox")',
            '$class_at(S_entry.CLASSES, porigin_right) = (pclassdesc_right)',
            '$class_named(S_entry.CLASSNAMES, $ptascii("rightbase")) = (porigin_base)',
            '$class_at(S_entry.CLASSES, porigin_base) = (pclassdesc_base)',
            '$class_named(S_entry.CLASSNAMES, $ptascii("token")) = (porigin_token)',
            '$class_at(S_entry.CLASSES, porigin_token) = (pclassdesc_token)',
            'S_entry.CLASSES = [pclassdesc_token, pclassdesc_base, pclassdesc_right]',
            'S_entry.LINKEDPARENTS = [CLASSLINK porigin_base STDCLASS_PARENT, CLASSLINK porigin_right (SOURCE_PARENT porigin_base)]',
            '$class_links_valid(S_entry)', '$declaration_history_valid(S_entry)',
            '$integer_standard_class_handlers(S_entry, porigin_right, |S_entry.CLASSES|)',
            '$object_table_at(S_entry.OBJECTTABLES, n_receiver) = eps',
        ]
        if repaired:
            # Four derived state mutations; six guard assertions, no reached-source credit.
            checks += [
                'S_no_publication = S_entry[.CLASSNAMES = eps]',
                '~$integer_standard_object_handlers(S_no_publication, POBJECT n_receiver)',
                'S_wrong_link = S_entry[.LINKEDPARENTS = [CLASSLINK porigin_base STDCLASS_PARENT, CLASSLINK porigin_right STDCLASS_PARENT]]',
                '~$integer_standard_object_handlers(S_wrong_link, POBJECT n_receiver)',
                'S_missing_link = S_entry[.LINKEDPARENTS = [CLASSLINK porigin_base STDCLASS_PARENT]]',
                '~$integer_standard_object_handlers(S_missing_link, POBJECT n_receiver)',
                'S_wrong_source = S_entry[.CLASSES = [pclassdesc_token, pclassdesc_base, pclassdesc_right[.PARENT = eps]]][.LINKEDPARENTS = [CLASSLINK porigin_base STDCLASS_PARENT]]',
                '$class_links_valid(S_wrong_source)',
                '~$declaration_history_valid(S_wrong_source)',
                '~$integer_standard_object_handlers(S_wrong_source, POBJECT n_receiver)',
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
            'S_throw_found = $object_integer_seek_throw(S_dispatch, 4000)',
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
            '$integer_pointer_value(S_return, pintegeroperation.LEFTPOINTER) = (PINT 99)',
            '$task_nodes(INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 1) = eps',
        ]
        seek('S_right', 'S_return', 4)
        checks += ['S_right.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT 12)) :: ptask_tail*']
        if cell:
            post = 'S_throw'
            checks += [
                '$integer_pointer_value(S_right, pintegeroperation.RIGHTPOINTER) = (POBJECT n_receiver)',
                '$integer_pointer_value(S_right, INTEGER_CV ($ptascii("right"))) = (PINT 5)',
                '$integer_standard_object_handlers(S_right, POBJECT n_receiver)',
                'PhpStep: S_right ~> S_failure',
                'S_failure.COMPLETION = THROWN "TypeError" ($ptascii("Unsupported operand types: int ^ RightBox")) 40',
                'S_failure.TODO = ptask_tail*', 'S_failure.STORE = S_right.STORE',
                'S_throw_budget = $drive_steps(S_right, 1)', 'S_throw_budget.COMPLETION = BUDGET',
                'S_throw = S_throw_budget[.COMPLETION = NORMAL]',
                'S_throw.TODO = (THROW_SEARCH n_failure) :: ptask_tail*',
                '$object_name(S_throw, n_failure) = $ptascii("TypeError")',
                '$throwable_field(S_throw, n_failure, "line") = PINT 40',
                '$throwable_field(S_throw, n_failure, "previous") = PNULL',
            ]
        else:
            post = 'S_ready'
            seek('S_ready', 'S_right', 5)
            checks += [
                'S_ready.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT 12) pintegerconversion_right 0) :: ptask_tail*',
                'pintegerconversion_right.INPUT = PINT ' + str(live_right),
                'pintegerconversion_right.VALUE = ' + str(live_right), 'pintegerconversion_right.NOTICES = eps',
                '$integer_binary(MODULO, 12, ' + str(live_right) + ') = IRESULT ' + ('2' if table else '5'),
            ]
    retired = not cell
    child_retired = repaired or throws
    checks += [
        f'{post}.STORE[n_left] = DEFINED (PINT 99)',
        f'{post}.STORE[n_v] = DEFINED (PINT 100)', f'{post}.STORE[n_calls] = DEFINED (PINT 1)',
        f'{post}.STORE[n_strings] = DEFINED (PINT 0)',
        f'{post}.STORE[n_drops] = DEFINED (PINT ' + ('1' if repaired or throws else '0') + ')',
        f'{post}.STORE[n_token_drops] = DEFINED (PINT ' + ('1' if child_retired else '0') + ')',
        f'$integer_pointer_value({post}, INTEGER_CV ($ptascii("right"))) = (PINT ' + str(live_right) + ')',
        f'$weakref_get({post}, n_weak_right) = ' + ('PNULL' if retired else 'POBJECT n_receiver'),
        f'$weakref_get({post}, n_weak_child) = ' + ('PNULL' if child_retired else 'POBJECT n_child'),
        f'$heap_owners($heap_prune($heap_graph({post})), HOBJECT n_receiver) = ' + ('0' if retired else '1'),
        f'$heap_owners($heap_prune($heap_graph({post})), HOBJECT n_child) = ' + ('0' if child_retired else '1'),
        '$task_nodes(INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT 12)) = eps',
        f'$call_descriptors_valid({post})', f'$heap_valid($heap_graph({post}))',
    ]
    if retired:
        checks += [f'~$integer_standard_object_handlers({post}, POBJECT n_receiver)']
    if cell:
        checks += [
            f'$lookup({post}.ENV, $ptascii("right")) = (n_new_right)',
            f'$lookup({post}.ENV, $ptascii("rightAlias")) = (n_right)',
            f'{post}.STORE[n_right] = DEFINED (POBJECT n_receiver)',
            f'$heap_owners($heap_prune($heap_graph({post})), HCELL n_right) = 1',
            f'$heap_owners($heap_prune($heap_graph({post})), HCELL n_new_right) = 2',
        ]
    if table:
        checks += [
            f'{post}.STORE[n_snapshot] = DEFINED (PARRAY n_table)',
            f'$heap_owners($heap_prune($heap_graph({post})), HARRAY n_table) = 1',
        ]
    checks += [
        f'S_done = $drive_steps({post}, 4000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps',
        '$weakref_get(S_done, n_weak_right) = PNULL', '$weakref_get(S_done, n_weak_child) = PNULL',
        '$heap_owners($heap_prune($heap_graph(S_done)), HOBJECT n_receiver) = 0',
        '$heap_owners($heap_prune($heap_graph(S_done)), HOBJECT n_child) = 0',
        'S_done.STORE[n_strings] = DEFINED (PINT 0)',
        'S_done.STORE[n_drops] = DEFINED (PINT ' + ('0' if table else '1') + ')',
        'S_done.STORE[n_token_drops] = DEFINED (PINT 1)',
        'S_done.STORE[n_v] = DEFINED (PINT ' + ('100' if cell or throws else '2' if table else '5') + ')',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        f'$drive_steps({post}, 0) = {post}[.COMPLETION = BUDGET]',
    ]
    if table:
        checks += ['$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_table) = 0']
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
