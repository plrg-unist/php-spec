#!/usr/bin/env python3
"""Nested pool edges stay physical through COW, deletion, and supplied throw."""
import base64
import json

import array_literal_null_key_constant_subtree_review_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_state_review import driven, seek
from array_literal_float_wrapped_mixed_cv_state_review import empty_biases, pair
from array_literal_null_key_constant_array_state_review import HELPERS


def items(state, name, entries):
    return (f'{state}.ARRAYS[{name}].ITEMS = ['
            + ', '.join(f'ENTRY ({key}) (DIRECT ({value}))' for key, value in entries) + ']')


def graph(thrown):
    if thrown:
        return [
            ('n_value', (), [('KINT 0', 'PARRAY n_left'), ('KINT 1', 'PARRAY n_right')]),
            ('n_left', (0,), [('KINT 0', 'PARRAY n_leaf0'), ('KINT 1', 'PARRAY n_leaf1')]),
            ('n_leaf0', (0, 0), [('KINT 0', 'PINT 2'), ('KINT 1', 'PINT 8')]),
            ('n_leaf1', (0, 1), [('KINT 0', 'PINT 3'), ('KINT 1', 'PINT 7')]),
            ('n_right', (1,), [('KINT 0', 'PARRAY n_leaf2'), ('KINT 1', 'PARRAY n_empty')]),
            ('n_leaf2', (1, 0), [('KINT 0', 'PINT 4'), ('KINT 1', 'PINT 6')]),
            ('n_empty', (1, 1), []),
        ]
    return [
        ('n_value', (), [('KSTRING ($ptascii("left"))', 'PARRAY n_left'), ('KSTRING ($ptascii("right"))', 'PARRAY n_right')]),
        ('n_left', (0,), [('KSTRING ($ptascii("deep"))', 'PARRAY n_deep'), ('KSTRING ($ptascii("empty"))', 'PARRAY n_empty')]),
        ('n_deep', (0, 0), [('KINT 0', 'PARRAY n_leaf0'), ('KINT 1', 'PARRAY n_leaf1')]),
        ('n_leaf0', (0, 0, 0), [('KINT 0', 'PINT 2'), ('KINT 1', 'PINT 8')]),
        ('n_leaf1', (0, 0, 1), [('KINT 0', 'PINT 3'), ('KINT 1', 'PINT 7')]),
        ('n_empty', (0, 1), []),
        ('n_right', (1,), [('KINT 0', 'PARRAY n_leaf2'), ('KINT 1', 'PARRAY n_leaf3')]),
        ('n_leaf2', (1, 0), [('KINT 0', 'PINT 4'), ('KINT 1', 'PINT 6')]),
        ('n_leaf3', (1, 1), [('KINT 0', 'PINT 5'), ('KINT 1', 'PINT 9')]),
    ]


def preserved(state, nodes, root_owners):
    checks = []
    for name, _, entries in nodes:
        checks += [items(state, name, entries), f'(HARRAY {name}) <- {state}.ALLOCATIONS',
                   f'$heap_count(HARRAY {name}, $pools_nodes({state}.POOLS)) = 1',
                   f'$heap_owners($heap_graph({state}), HARRAY {name}) = {root_owners if name == "n_value" else 2}']
    return checks


def conditions(name, program, path, stdout):
    thrown = name.endswith('supplied-throw')
    nodes = graph(thrown)
    marker = 'ARRAY_KEY_NULL_CONST_RESULT n_a n_value phpType13* z'
    args = 'n_a, n_value, phpType13*, z'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + empty_biases('S_initial') + seek('S_initial', 20, 'S') + [
        '$array_null_const_plan(S) = ((' + args + '))', f'z = {11 if thrown else 10}',
        'S.RESULT = KNOWN (PARRAY n_value)', 'S.BASE = BASE_VALUE (KNOWN PNULL)',
        'S.TODO = (ARRAY_VALUE n_a (VARIABLE n_key_name* z_key) phpType13* z) :: ptask_tail*',
        'S.ORIGIN = (PORIGIN n_unit pcpath)', 'pcpath_value = pcpath ++ [PCFIELD 1]',
        '$compiled_read(S, PORIGIN n_unit pcpath_value) = (PARRAY n_value)',
        '$array_null_const_source(S, ' + args + ')', '$array_null_const_ready(S, n_a, n_value)',
        '$array_null_key_plan(S) = eps', '$array_null_value_plan(S) = eps', '$array_null_tmp_plan(S) = eps',
        '$lookup(S.ENV, $ptascii("seed")) = (n_seed)', 'S.STORE[n_seed] = DEFINED (PINT 2)',
        '$lookup(S.ENV, $ptascii("calls")) = (n_calls)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        '$lookup(S.ENV, $ptascii("key")) = (n_key)', 'S.STORE[n_key] = DEFINED PNULL',
    ]
    for node, indices, entries in nodes:
        checks.append(items('S', node, entries))
        suffix = ''.join(f', PCFIELD 0, PCINDEX {index}, PCFIELD 1' for index in indices)
        checks += [f'$pool_value(S.POOLS, PORIGIN n_unit (pcpath_value ++ [{suffix[2:]}])) = (PARRAY {node})',
                   f'$heap_count(HARRAY {node}, $pools_nodes(S.POOLS)) = 1',
                   f'$heap_owners($heap_graph(S), HARRAY {node}) = 2']
        if indices:
            checks += [f'$heap_count(HARRAY {node}, $machine_roots(S)) = 1',
                       f'$heap_count(HARRAY {node}, $task_nodes({marker})) = 0']
    checks += [
        '$array_null_const_items(S, S.ARRAYS[n_value].ITEMS, [n_a, n_value])',
        'S_alias = S[.REFCELLS = n_seed :: S.REFCELLS][.ARRAYS[n_leaf0].ITEMS = [ENTRY (KINT 0) (ALIAS n_seed)]]',
        '$heap_valid($heap_graph(S_alias))',
        '~$array_null_const_ready(S_alias, n_a, n_value)',
        'S_debt = S[.LITERALARRAYDEBTS = [n_leaf0]]', '~$array_null_const_ready(S_debt, n_a, n_value)',
        'S_cycle = S[.ARRAYS[n_leaf0].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf0))]]',
        '~$array_null_const_ready(S_cycle, n_a, n_value)',
        'S_back = S[.ARRAYS[n_leaf0].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_value))]]',
        '~$array_null_const_ready(S_back, n_a, n_value)',
        'S_builder = S[.ARRAYS[n_leaf0].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_a))]]',
        '~$array_null_const_ready(S_builder, n_a, n_value)',
        'S_bounds = S[.ARRAYS[n_leaf0].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY (|S.ARRAYS|)))]]',
        '~$array_null_const_ready(S_bounds, n_a, n_value)',
        '~$array_null_const_ready(S[.ALLOCATIONS = [HARRAY n_a, HARRAY n_value]], n_a, n_value)',
        'S_dag = S[.ARRAYS[n_value].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf0)), ENTRY (KINT 1) (DIRECT (PARRAY n_leaf0))]]',
        '$heap_count(HARRAY n_leaf0, $entries_nodes(S_dag.ARRAYS[n_value].ITEMS)) = 2',
        '$array_null_const_ready(S_dag, n_a, n_value)', '$heap_valid($heap_graph(S_dag))',
        '$heap_valid($heap_graph(S))', '$call_descriptors_valid(S)',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, '$error_call_valid(S_dispatch, perrorcall)',
        '$task_nodes(' + marker + ') = [HARRAY n_a, HARRAY n_value]',
        'S_dispatch.ARRAYS = S.ARRAYS', 'S_dispatch.STORE = S.STORE',
    ] + preserved('S_dispatch', nodes, 2) + empty_biases('S_dispatch') + driven('S', 'S_dispatch', 'S_driven') + seek('S_driven', 23, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
        'perrorcall_entered.RESUME = ' + marker,
    ] + preserved('S_entered', nodes, 2)
    copies = []
    if thrown:
        checks += [
            '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)', 'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', '$lookup(S.ENV, $ptascii("later")) = (n_later)',
            'S_object = S[.ARRAYS[n_leaf0].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_second))]]',
            '~$array_null_const_ready(S_object, n_a, n_value)',
        ] + seek('S_entered', 24, 'S_discard') + [
            'S_discard.TODO = (THROW_SEARCH n_second) :: (ERROR_HANDLER_RESULT perrorcall_discard) :: ptask_pending*',
            'perrorcall_discard.RESUME = ' + marker,
            '$entry_lookup(S_discard.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PINT 8))',
            'S_popped = S_discard[.TODO = (THROW_SEARCH n_second) :: ptask_pending*]',
            '$error_read_discard(S_popped, ' + marker + ') = S_popped',
        ] + preserved('S_popped', nodes, 1) + [
            'PhpStep: S_discard ~> S_released', 'S_released.STORE = S_discard.STORE',
        ] + driven('S_discard', 'S_released', 'S_release_driven') + seek('S_release_driven', 14, 'S_catch') + [
            'S_catch.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_after*',
            'S_catch.STORE[n_dest] = DEFINED (PINT 99)', 'S_catch.STORE[n_later] = DEFINED (PINT 7)',
            '$throwable_previous_id(S_catch, n_second) = eps', '~((HARRAY n_a) <- S_catch.ALLOCATIONS)',
        ] + preserved('S_catch', nodes, 1) + seek('S_catch', 15, 'S_read')
    else:
        checks += seek('S_entered', 21, 'S_resume') + [
            'S_resume.TODO = (' + marker + ') :: ptask_after*', '$array_null_const_ready(S_resume, n_a, n_value)',
            'S_resume.STORE[n_seed] = DEFINED (PINT 99)', 'S_resume.STORE[n_key] = DEFINED (PINT 9)',
            'PhpStep: S_resume ~> S_insert',
            '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_value))',
            'S_insert.STORE = S_resume.STORE',
        ] + preserved('S_insert', nodes, 2) + driven('S_resume', 'S_insert', 'S_insert_driven') + seek('S_insert_driven', 17, 'S_copied') + [
            '$lookup(S_copied.ENV, $ptascii("copy")) = (n_copy_cell)', 'S_copied.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)',
            '$entry_lookup(S_copied.ARRAYS[n_copy].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_copy_value))',
            '$entry_lookup(S_copied.ARRAYS[n_copy_value].ITEMS, KSTRING ($ptascii("left"))) = (DIRECT (PARRAY n_copy_left))',
            '$entry_lookup(S_copied.ARRAYS[n_copy_left].ITEMS, KSTRING ($ptascii("deep"))) = (DIRECT (PARRAY n_copy_deep))',
            '$entry_lookup(S_copied.ARRAYS[n_copy_deep].ITEMS, KINT 0) = (DIRECT (PARRAY n_copy_leaf0))',
            '$entry_lookup(S_copied.ARRAYS[n_copy_value].ITEMS, KSTRING ($ptascii("right"))) = (DIRECT (PARRAY n_copy_right))',
            '$entry_lookup(S_copied.ARRAYS[n_copy_right].ITEMS, KINT 1) = (DIRECT (PARRAY n_copy_leaf3))',
            pair('S_copied', 'n_copy_leaf0', 66, 8), pair('S_copied', 'n_copy_leaf3', 5, 99),
            '$entry_lookup(S_copied.ARRAYS[n_copy_deep].ITEMS, KINT 1) = (DIRECT (PARRAY n_leaf1))',
            '$entry_lookup(S_copied.ARRAYS[n_copy_left].ITEMS, KSTRING ($ptascii("empty"))) = (DIRECT (PARRAY n_empty))',
            '$entry_lookup(S_copied.ARRAYS[n_copy_right].ITEMS, KINT 0) = (DIRECT (PARRAY n_leaf2))',
        ]
        for node, _, entries in nodes:
            checks += [items('S_copied', node, entries),
                       f'$heap_owners($heap_graph(S_copied), HARRAY {node}) = {3 if node in ("n_leaf1", "n_empty", "n_leaf2") else 2}']
        copies = ['n_copy', 'n_copy_value', 'n_copy_left', 'n_copy_deep', 'n_copy_leaf0', 'n_copy_right', 'n_copy_leaf3']
        checks += seek('S_copied', 15, 'S_read') + [
            '$lookup(S_read.ENV, $ptascii("copy")) = eps',
            '$lookup(S_read.ENV, $ptascii("a")) = (n_a_cell)', 'S_read.STORE[n_a_cell] = DEFINED (PARRAY n_a)',
            'S_read.ARRAYS[n_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KINT 4) (DIRECT (PINT 66))]',
        ]
    checks += preserved('S_read', nodes, 1) + [
        'S_read.STORE[n_seed] = DEFINED (PINT 99)', 'S_read.STORE[n_key] = DEFINED (PINT 9)',
        'S_read.STORE[n_calls] = DEFINED (PINT 1)', '$heap_valid($heap_graph(S_read))', '$call_descriptors_valid(S_read)',
        '$drive_steps(S_read, 0) = S_read[.COMPLETION = BUDGET]',
        'S_split = $drive_steps(S_read, 1)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL], 2000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.HELD = eps', '~((HARRAY n_a) <- S_done.ALLOCATIONS)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
    ] + preserved('S_done', nodes, 1) + empty_biases('S_done')
    for state in ('S_read', 'S_done'):
        checks += [f'~((HARRAY {node}) <- {state}.ALLOCATIONS)' for node in copies]
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
