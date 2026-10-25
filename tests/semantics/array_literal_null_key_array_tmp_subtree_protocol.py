#!/usr/bin/env python3
"""Nonpool TMP roots retain physical child edges across callback COW and retirement."""
import base64
import json

import array_literal_null_key_array_tmp_subtree_cases as cases
import list_missing_warning_protocol as shared
from array_literal_null_key_array_tmp_protocol import HELPERS as BASE_HELPERS
from array_literal_null_key_constant_subtree_state_review import items
from array_literal_float_array_cv_state_review import driven, seek
from array_literal_float_wrapped_mixed_cv_state_review import empty_biases, pair

HELPERS = BASE_HELPERS + r'''
def $list_warning_frontier(S, 16) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask_tail*
  -- if $base64(text) = $ptascii("C:")
'''


def graph(dag):
    if dag:
        return [
            ('n_value', (), False, [('KINT 0', 'PARRAY n_row'), ('KINT 1', 'PARRAY n_row'), ('KINT 2', 'PARRAY n_right')]),
            ('n_row', (0,), False, [('KINT 0', 'PINT 2'), ('KINT 1', 'PINT 7')]),
            ('n_right', (2,), True, [('KINT 0', 'PARRAY n_pair'), ('KINT 1', 'PARRAY n_empty')]),
            ('n_pair', (2, 0), True, [('KINT 0', 'PINT 5'), ('KINT 1', 'PINT 9')]),
            ('n_empty', (2, 1), True, []),
        ]
    return [
        ('n_value', (), False, [('KINT 0', 'PARRAY n_left'), ('KINT 1', 'PARRAY n_right')]),
        ('n_left', (0,), False, [('KINT 0', 'PARRAY n_leaf'), ('KINT 1', 'PINT 8')]),
        ('n_leaf', (0, 0), False, [('KINT 0', 'PINT 2'), ('KINT 1', 'PINT 7')]),
        ('n_right', (1,), True, [('KINT 0', 'PARRAY n_pair'), ('KINT 1', 'PARRAY n_empty')]),
        ('n_pair', (1, 0), True, [('KINT 0', 'PINT 3'), ('KINT 1', 'PINT 4')]),
        ('n_empty', (1, 1), True, []),
    ]


def frozen(state, nodes):
    return [check for node, _, _, entries in nodes for check in
            [items(state, node, entries), f'(HARRAY {node}) <- {state}.ALLOCATIONS']]


def conditions(name, program, path, stdout):
    dag = name.endswith('shared-child')
    nodes = graph(dag)
    args = 'n_a, n_value, phpType13*, z'
    marker = 'ARRAY_KEY_NULL_TMP_RESULT n_a n_value phpType13* z'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + empty_biases('S_initial') + seek('S_initial', 10, 'S') + [
        '$array_null_tmp_plan(S) = ((' + args + '))', 'z = 10',
        'S.RESULT = KNOWN (PARRAY n_value)', 'S.ORIGIN = (PORIGIN n_unit pcpath)',
        'pcpath_value = pcpath ++ [PCFIELD 1]', '$compiled_read(S, PORIGIN n_unit pcpath_value) = eps',
        '$code_at(S.CODE, n_unit) = (pcode)', '$code_expression(pcode.EXPRESSIONS, pcpath_value) = ((10, false))',
        '$array_null_tmp_source(S, ' + args + ')', '$array_null_tmp_ready(S, n_a, n_value)',
        '~$array_null_value_ready(S, n_a, n_value)',
        '$array_null_key_plan(S) = eps', '$array_null_value_plan(S) = eps', '$array_null_const_plan(S) = eps',
        '$lookup(S.ENV, $ptascii("seed")) = (n_seed)',
        f'S.STORE[n_seed] = DEFINED (PINT {2 if dag else 3})',
        '$lookup(S.ENV, $ptascii("key")) = (n_key)', 'S.STORE[n_key] = DEFINED PNULL',
        '$lookup(S.ENV, $ptascii("tail")) = (n_tail)', 'S.STORE[n_tail] = DEFINED (PINT 7)',
        '$heap_count(HARRAY n_value, $machine_roots(S)) = 1',
        '$heap_owners($heap_graph(S), HARRAY n_value) = 1',
        '$heap_count(HARRAY n_value, $pools_nodes(S.POOLS)) = 0',
        '~$array_null_tmp_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_null_tmp_source(S, n_a, n_value, phpType13*, 11)',
        '$heap_valid($heap_graph(S))', '$call_descriptors_valid(S)',
    ]
    for node, indices, pooled, entries in nodes:
        checks += [items('S', node, entries), f'(HARRAY {node}) <- S.ALLOCATIONS',
                   f'$heap_count(HARRAY {node}, $pools_nodes(S.POOLS)) = {int(pooled)}',
                   f'$heap_owners($heap_graph(S), HARRAY {node}) = {4 if dag and node == "n_row" else 2 if pooled else 1}']
        suffix = ', '.join(f'PCFIELD 0, PCINDEX {index}, PCFIELD 1' for index in indices)
        origin = 'PORIGIN n_unit (pcpath_value ++ [' + suffix + '])'
        checks.append(f'$pool_value(S.POOLS, {origin}) = ' + (f'(PARRAY {node})' if pooled else 'eps'))
        if indices:
            checks.append(f'$heap_count(HARRAY {node}, $task_nodes({marker})) = 0')
    if dag:
        checks += [
            '$lookup(S.ENV, $ptascii("row")) = (n_row_cell)', 'S.STORE[n_row_cell] = DEFINED (PARRAY n_row)',
            '$lookup(S.ENV, $ptascii("held")) = (n_held_cell)', 'S.STORE[n_held_cell] = DEFINED (PARRAY n_row)',
            'n_held_cell =/= n_row_cell', '$heap_count(HARRAY n_row, $entries_nodes(S.ARRAYS[n_value].ITEMS)) = 2',
        ]
    checks += [
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 10',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$task_nodes(' + marker + ') = [HARRAY n_a, HARRAY n_value]',
        '$heap_count(HCELL n_seed, $task_nodes(' + marker + ')) = 0',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_value) = 1',
    ] + frozen('S_dispatch', nodes) + driven('S', 'S_dispatch', 'S_driven') + seek('S_driven', 13, 'S_entered') + [
        '$heap_owners($heap_graph(S_entered), HARRAY n_value) = 1',
    ] + seek('S_entered', 11, 'S_resume') + [
        'S_resume.TODO = (' + marker + ') :: ptask_after*',
        '$array_null_tmp_source(S_resume, ' + args + ')', '$array_null_tmp_ready(S_resume, n_a, n_value)',
        '$array_null_tmp_ready(S_resume[.ENV = eps], n_a, n_value)',
        'S_resume.STORE[n_key] = DEFINED (PINT 9)', 'S_resume.STORE[n_tail] = DEFINED (PINT 66)',
        '$heap_owners($heap_graph(S_resume), HARRAY n_value) = 1',
        '$error_read_discard(S_resume, ' + marker + ') = S_resume',
    ] + frozen('S_resume', nodes)
    if dag:
        checks += [
            'S_resume.STORE[n_row_cell] = DEFINED (PARRAY n_row_live)', 'n_row_live =/= n_row',
            'S_resume.STORE[n_held_cell] = DEFINED (PARRAY n_held_live)', 'n_held_live =/= n_row',
            pair('S_resume', 'n_row_live', 44, 7), pair('S_resume', 'n_held_live', 2, 55),
            '$heap_owners($heap_graph(S_resume), HARRAY n_row) = 2',
        ]
    else:
        checks += ['S_resume.STORE[n_seed] = DEFINED (PINT 44)']
    checks += [
        'PhpStep: S_resume ~> S_insert',
        '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_value))',
        '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT 9) = eps', 'S_insert.STORE = S_resume.STORE',
        '$heap_count(HARRAY n_value, $machine_roots(S_insert)) = 0',
        '$heap_owners($heap_graph(S_insert), HARRAY n_value) = 1',
    ] + frozen('S_insert', nodes) + driven('S_resume', 'S_insert', 'S_insert_driven')
    if dag:
        checks += seek('S_insert_driven', 16, 'S_copy') + [
            '$lookup(S_copy.ENV, $ptascii("copy")) = (n_copy_cell)', 'S_copy.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)',
            '$entry_lookup(S_copy.ARRAYS[n_copy].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_copy_value))',
            'n_copy_value =/= n_value',
            items('S_copy', 'n_copy_value', [('KINT 0', 'PARRAY n_copy_row'), ('KINT 1', 'PARRAY n_row'), ('KINT 2', 'PARRAY n_right')]),
            'n_copy_row =/= n_row', pair('S_copy', 'n_copy_row', 66, 7), pair('S_copy', 'n_row', 2, 7),
            '$heap_owners($heap_graph(S_copy), HARRAY n_row) = 3',
            '$heap_owners($heap_graph(S_copy), HARRAY n_right) = 3',
            '$heap_owners($heap_graph(S_copy), HARRAY n_pair) = 2',
            '$heap_owners($heap_graph(S_copy), HARRAY n_empty) = 2',
            pair('S_copy', 'n_row_live', 44, 88), pair('S_copy', 'n_held_live', 77, 55),
        ] + seek('S_copy', 15, 'S_read') + [
            'S_read.ARRAYS[n_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KINT 4) (DIRECT (PINT 66))]',
            '~((HARRAY n_value) <- S_read.ALLOCATIONS)', '~((HARRAY n_row) <- S_read.ALLOCATIONS)',
            '~((HARRAY n_copy) <- S_read.ALLOCATIONS)', '~((HARRAY n_copy_value) <- S_read.ALLOCATIONS)',
            '~((HARRAY n_copy_row) <- S_read.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_read), HARRAY n_right) = 1',
            pair('S_read', 'n_row_live', 44, 88), pair('S_read', 'n_held_live', 77, 55),
        ]
        retired = ['n_a', 'n_value', 'n_row', 'n_row_live', 'n_held_live', 'n_copy', 'n_copy_value', 'n_copy_row']
    else:
        checks += seek('S_insert_driven', 15, 'S_read') + [
            '$lookup(S_read.ENV, $ptascii("copy")) = (n_copy_cell)', 'S_read.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)',
            '$entry_lookup(S_read.ARRAYS[n_copy].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_copy_value))',
            items('S_read', 'n_copy_value', [('KINT 0', 'PARRAY n_copy_left'), ('KINT 1', 'PARRAY n_copy_right')]),
            items('S_read', 'n_copy_left', [('KINT 0', 'PARRAY n_copy_leaf'), ('KINT 1', 'PINT 8')]),
            items('S_read', 'n_copy_right', [('KINT 0', 'PARRAY n_copy_pair'), ('KINT 1', 'PARRAY n_copy_empty')]),
            pair('S_read', 'n_copy_leaf', 55, 7), pair('S_read', 'n_copy_pair', 3, 77),
            items('S_read', 'n_copy_empty', [('KINT 0', 'PINT 88')]),
            '$lookup(S_read.ENV, $ptascii("fresh")) = (n_fresh_cell)', 'S_read.STORE[n_fresh_cell] = DEFINED (PARRAY n_fresh)',
            items('S_read', 'n_fresh', [('KINT 0', 'PARRAY n_fresh_left')]),
            items('S_read', 'n_fresh_left', [('KINT 0', 'PARRAY n_fresh_leaf'), ('KINT 1', 'PINT 8')]),
            pair('S_read', 'n_fresh_leaf', 44, 7), 'n_fresh_leaf =/= n_leaf', 'n_fresh_leaf =/= n_copy_leaf',
            'S_read.STORE[n_seed] = DEFINED (PINT 99)',
        ] + frozen('S_read', nodes)
        for copy, original in [('n_copy_value', 'n_value'), ('n_copy_left', 'n_left'), ('n_copy_leaf', 'n_leaf'),
                               ('n_copy_right', 'n_right'), ('n_copy_pair', 'n_pair'), ('n_copy_empty', 'n_empty')]:
            checks.append(f'{copy} =/= {original}')
        retired = ['n_a', 'n_value', 'n_left', 'n_leaf', 'n_copy', 'n_copy_value', 'n_copy_left', 'n_copy_leaf',
                   'n_copy_right', 'n_copy_pair', 'n_copy_empty', 'n_fresh', 'n_fresh_left', 'n_fresh_leaf']
    checks += [
        '$heap_valid($heap_graph(S_read))', '$call_descriptors_valid(S_read)',
        '$drive_steps(S_read, 0) = S_read[.COMPLETION = BUDGET]',
        'S_split = $drive_steps(S_read, 1)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL], 3000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps', 'S_done.POOLS = S.POOLS',
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
    ] + empty_biases('S_read') + empty_biases('S_done')
    checks += [f'~((HARRAY {node}) <- S_done.ALLOCATIONS)' for node in retired]
    for node, _, pooled, entries in nodes:
        if pooled:
            checks += [items('S_done', node, entries), f'(HARRAY {node}) <- S_done.ALLOCATIONS',
                       f'$heap_owners($heap_graph(S_done), HARRAY {node}) = {1 if node == "n_right" else 2}']
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
