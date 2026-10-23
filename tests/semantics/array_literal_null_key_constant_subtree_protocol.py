#!/usr/bin/env python3
"""Nested pool edges remain physical while roots and COW owners change."""
import base64
import json

import array_literal_null_key_constant_subtree_cases as cases
import list_missing_warning_protocol as shared
from array_literal_null_key_constant_array_protocol import HELPERS
from array_literal_float_array_cv_state_review import driven, seek
from array_literal_float_wrapped_mixed_cv_state_review import empty_biases, pair


def conditions(name, program, path, stdout):
    repeated = name.endswith('repeated')
    args = 'n_a, n_value, phpType13*, z'
    marker = 'ARRAY_KEY_NULL_CONST_RESULT n_a n_value phpType13* z'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 20, 'S') + [
        '$array_null_const_plan(S) = ((' + args + '))', f'z = {5 if repeated else 9}',
        'S.RESULT = KNOWN (PARRAY n_value)', 'S.ORIGIN = (PORIGIN n_unit pcpath)',
        '$compiled_read(S, PORIGIN n_unit (pcpath ++ [PCFIELD 1])) = (PARRAY n_value)',
        'S.ARRAYS[n_value].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_left)), ENTRY (KINT 1) (DIRECT (PARRAY n_right))]',
        '$pool_value(S.POOLS, PORIGIN n_unit (pcpath ++ [PCFIELD 1, PCFIELD 0, PCINDEX 0, PCFIELD 1])) = (PARRAY n_left)',
        '$pool_value(S.POOLS, PORIGIN n_unit (pcpath ++ [PCFIELD 1, PCFIELD 0, PCINDEX 1, PCFIELD 1])) = (PARRAY n_right)',
        '$entries_nodes(S.ARRAYS[n_value].ITEMS) = [HARRAY n_left, HARRAY n_right]',
        '~$literal_reference_flat_items(S, S.ARRAYS[n_value].ITEMS)',
        '$array_null_const_items(S, S.ARRAYS[n_value].ITEMS, [n_a, n_value])',
        '$heap_count(HARRAY n_value, $pools_nodes(S.POOLS)) = 1',
        '$heap_owners($heap_graph(S), HARRAY n_value) = 2',
        '$heap_count(HARRAY n_left, $pools_nodes(S.POOLS)) = 1',
        '$heap_count(HARRAY n_right, $pools_nodes(S.POOLS)) = 1',
        '$heap_owners($heap_graph(S), HARRAY n_left) = 2',
        '$heap_owners($heap_graph(S), HARRAY n_right) = 2',
        '$pool_at(S.POOLS, n_unit) = (ppool)',
        'S_root_only = S[.POOLS = [ppool[.CONSTANTS = [PCONSTANT (pcpath ++ [PCFIELD 1]) (PARRAY n_value)]]]]',
        '$compiled_read(S_root_only, PORIGIN n_unit (pcpath ++ [PCFIELD 1])) = (PARRAY n_value)',
        '$heap_count(HARRAY n_left, $pools_nodes(S_root_only.POOLS)) = 0',
        '$heap_owners($heap_graph(S_root_only), HARRAY n_left) = 1',
        '$array_null_const_ready(S_root_only, n_a, n_value)',
        '$array_null_tmp_plan(S) = eps', '$array_null_value_plan(S) = eps', '$array_null_key_plan(S) = eps',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, '$error_call_valid(S_dispatch, perrorcall)',
        '$task_nodes(' + marker + ') = [HARRAY n_a, HARRAY n_value]',
        '$heap_count(HARRAY n_left, $task_nodes(' + marker + ')) = 0',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_value) = 2',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_left) = 2',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_right) = 2',
    ] + driven('S', 'S_dispatch', 'S_dispatch_driven') + seek('S_dispatch_driven', 23, 'S_entered') + [
        '$heap_owners($heap_graph(S_entered), HARRAY n_value) = 2',
        '$heap_owners($heap_graph(S_entered), HARRAY n_left) = 2',
        '$heap_owners($heap_graph(S_entered), HARRAY n_right) = 2',
    ] + seek('S_entered', 21, 'S_resume') + [
        'S_resume.TODO = (' + marker + ') :: ptask_after*',
        '$array_null_const_source(S_resume, ' + args + ')', '$array_null_const_ready(S_resume, n_a, n_value)',
        'S_resume.ARRAYS[n_value] = S.ARRAYS[n_value]',
        'S_resume.ARRAYS[n_left] = S.ARRAYS[n_left]', 'S_resume.ARRAYS[n_right] = S.ARRAYS[n_right]',
        '$error_read_discard(S_resume, ' + marker + ') = S_resume',
        'PhpStep: S_resume ~> S_insert',
        '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_value))',
        'S_insert.STORE = S_resume.STORE',
        '$heap_owners($heap_graph(S_insert), HARRAY n_value) = 2',
        '$heap_owners($heap_graph(S_insert), HARRAY n_left) = 2',
        '$heap_owners($heap_graph(S_insert), HARRAY n_right) = 2',
    ] + driven('S_resume', 'S_insert', 'S_insert_driven')
    if repeated:
        checks += [pair('S', 'n_left', 2, 7), pair('S', 'n_right', 2, 8)] + seek('S_insert_driven', 25, 'S_first') + [
            '$lookup(S_first.ENV, $ptascii("a")) = (n_a_cell)', 'S_first.STORE[n_a_cell] = DEFINED (PARRAY n_a)',
            '$entry_lookup(S_first.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_value))',
            '$lookup(S_first.ENV, $ptascii("copy")) = (n_copy_cell)', 'S_first.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)',
            '$entry_lookup(S_first.ARRAYS[n_copy].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_copy_value))',
            'n_copy_value =/= n_value',
            '$entry_lookup(S_first.ARRAYS[n_copy_value].ITEMS, KINT 0) = (DIRECT (PARRAY n_left))',
            '$entry_lookup(S_first.ARRAYS[n_copy_value].ITEMS, KINT 1) = (DIRECT (PARRAY n_copy_right))',
            'n_copy_right =/= n_right', pair('S_first', 'n_copy_right', 2, 77),
            '$lookup(S_first.ENV, $ptascii("held")) = (n_held_cell)', 'S_first.STORE[n_held_cell] = DEFINED (PARRAY n_left)',
            '$heap_owners($heap_graph(S_first), HARRAY n_left) = 4',
            '$heap_owners($heap_graph(S_first), HARRAY n_right) = 2',
        ] + seek('S_first', 20, 'S_second') + [
            '$array_null_const_plan(S_second) = ((n_b, n_value, phpType13*, z))', 'n_b =/= n_a',
            'S_second.ORIGIN = S.ORIGIN', 'S_second.POOLS = S.POOLS',
            '$heap_owners($heap_graph(S_second), HARRAY n_value) = 3',
            '$heap_owners($heap_graph(S_second), HARRAY n_left) = 4',
            '$heap_owners($heap_graph(S_second), HARRAY n_right) = 2',
        ] + seek('S_second', 21, 'S_second_resume') + [
            'S_second_resume.TODO = (ARRAY_KEY_NULL_CONST_RESULT n_b n_value phpType13* z) :: ptask_second*',
            'S_second_resume.STORE[n_held_cell] = DEFINED (PARRAY n_held)', 'n_held =/= n_left', pair('S_second_resume', 'n_held', 44, 7),
            '$entry_lookup(S_second_resume.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_a_value))',
            'n_a_value =/= n_value',
            '$entry_lookup(S_second_resume.ARRAYS[n_a_value].ITEMS, KINT 0) = (DIRECT (PARRAY n_a_left))',
            'n_a_left =/= n_left', pair('S_second_resume', 'n_a_left', 2, 99),
            pair('S_second_resume', 'n_left', 2, 7), pair('S_second_resume', 'n_right', 2, 8),
            '$heap_owners($heap_graph(S_second_resume), HARRAY n_value) = 2',
            '$heap_owners($heap_graph(S_second_resume), HARRAY n_left) = 3',
            '$heap_owners($heap_graph(S_second_resume), HARRAY n_right) = 3',
        ] + seek('S_second_resume', 15, 'S_read') + [
            '$lookup(S_read.ENV, $ptascii("b")) = (n_b_cell)', 'S_read.STORE[n_b_cell] = DEFINED (PARRAY n_b)',
            '$entry_lookup(S_read.ARRAYS[n_b].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_b_value))', 'n_b_value =/= n_value',
            '$entry_lookup(S_read.ARRAYS[n_b_value].ITEMS, KINT 0) = (DIRECT (PARRAY n_b_left))',
            'n_b_left =/= n_left', pair('S_read', 'n_b_left', 55, 7),
            pair('S_read', 'n_a_left', 2, 99), pair('S_read', 'n_held', 44, 7), pair('S_read', 'n_copy_right', 2, 77),
            '$heap_owners($heap_graph(S_read), HARRAY n_left) = 3',
            '$heap_owners($heap_graph(S_read), HARRAY n_right) = 4',
        ]
        retired = ('n_a', 'n_b', 'n_copy', 'n_a_value', 'n_copy_value', 'n_b_value', 'n_a_left', 'n_b_left', 'n_copy_right', 'n_held')
        originals = ('n_value', 'n_left', 'n_right')
    else:
        checks += [
            'S.ARRAYS[n_left].ITEMS = eps', '$array_immutable(S, n_left)',
            'S.ARRAYS[n_right].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_empty))]',
            'S.ARRAYS[n_empty].ITEMS = eps', '$array_immutable(S, n_empty)',
            '$heap_count(HARRAY n_empty, $pools_nodes(S.POOLS)) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_empty) = 2',
        ] + seek('S_insert_driven', 15, 'S_read') + [
            '$lookup(S_read.ENV, $ptascii("a")) = (n_a_cell)', 'S_read.STORE[n_a_cell] = DEFINED (PARRAY n_a)',
            '$entry_lookup(S_read.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_a_value))', 'n_a_value =/= n_value',
            '$entry_lookup(S_read.ARRAYS[n_a_value].ITEMS, KINT 0) = (DIRECT (PARRAY n_a_left))',
            'S_read.ARRAYS[n_a_left].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 66))]',
            '$entry_lookup(S_read.ARRAYS[n_a_value].ITEMS, KINT 1) = (DIRECT (PARRAY n_right))',
            '$lookup(S_read.ENV, $ptascii("copy")) = (n_copy_cell)', 'S_read.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)',
            '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_copy_value))',
            '$entry_lookup(S_read.ARRAYS[n_copy_value].ITEMS, KINT 0) = (DIRECT (PARRAY n_copy_left))',
            'S_read.ARRAYS[n_copy_left].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 55))]',
            '$entry_lookup(S_read.ARRAYS[n_copy_value].ITEMS, KINT 1) = (DIRECT (PARRAY n_copy_right))',
            '$entry_lookup(S_read.ARRAYS[n_copy_right].ITEMS, KINT 0) = (DIRECT (PARRAY n_copy_empty))',
            'S_read.ARRAYS[n_copy_empty].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 77))]',
            '$lookup(S_read.ENV, $ptascii("held")) = (n_held_cell)', 'S_read.STORE[n_held_cell] = DEFINED (PARRAY n_empty)',
            '$heap_owners($heap_graph(S_read), HARRAY n_left) = 2',
            '$heap_owners($heap_graph(S_read), HARRAY n_right) = 3',
            '$heap_owners($heap_graph(S_read), HARRAY n_empty) = 3',
        ]
        retired = ('n_a', 'n_copy', 'n_a_value', 'n_copy_value', 'n_a_left', 'n_copy_left', 'n_copy_right', 'n_copy_empty')
        originals = ('n_value', 'n_left', 'n_right', 'n_empty')
    checks += [
        '$heap_owners($heap_graph(S_read), HARRAY n_value) = 1',
        '$call_descriptors_valid(S_read)', '$heap_valid($heap_graph(S_read))',
        '$drive_steps(S_read, 0) = S_read[.COMPLETION = BUDGET]',
        'S_split = $drive_steps(S_read, 1)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL], 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$heap_owners($heap_graph(S_done), HARRAY n_value) = 1',
        '$heap_owners($heap_graph(S_done), HARRAY n_left) = 2',
        '$heap_owners($heap_graph(S_done), HARRAY n_right) = 2',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
    ] + empty_biases('S_done')
    for array in originals:
        checks += [f'(HARRAY {array}) <- S_done.ALLOCATIONS', f'S_done.ARRAYS[{array}] = S.ARRAYS[{array}]']
    for array in retired:
        checks.append(f'~((HARRAY {array}) <- S_done.ALLOCATIONS)')
    if not repeated:
        checks.append('$heap_owners($heap_graph(S_done), HARRAY n_empty) = 2')
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
