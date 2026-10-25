#!/usr/bin/env python3
"""A sole TMP root keeps dynamic child edges, then cascades without pool loss."""
import base64
import json

import array_literal_null_key_array_tmp_subtree_review_cases as cases
import list_missing_warning_protocol as shared
from array_literal_float_array_cv_state_review import driven, seek
from array_literal_float_wrapped_mixed_cv_state_review import empty_biases, pair
from array_literal_null_key_array_tmp_state_review import HELPERS as BASE_HELPERS

HELPERS = BASE_HELPERS + r'''
dec $tmp_subtree_deprecations(pevent*) : nat
def $tmp_subtree_deprecations(eps) = 0
def $tmp_subtree_deprecations((DIAGNOSTIC "Deprecated" ptbytes z) :: pevent*) = $(1 + $tmp_subtree_deprecations(pevent*))
def $tmp_subtree_deprecations(pevent :: pevent*) = $tmp_subtree_deprecations(pevent*) -- otherwise
'''


def graph(thrown):
    if thrown:
        return [
            ('n_value', (), False, [('KINT 0', 'PARRAY n_left'), ('KINT 1', 'PARRAY n_right')]),
            ('n_left', (0,), False, [('KINT 0', 'PARRAY n_leaf0'), ('KINT 1', 'PARRAY n_leaf1')]),
            ('n_leaf0', (0, 0), False, [('KINT 0', 'PINT 2'), ('KINT 1', 'PINT 8')]),
            ('n_leaf1', (0, 1), True, [('KINT 0', 'PINT 3'), ('KINT 1', 'PINT 7')]),
            ('n_right', (1,), False, [('KINT 0', 'PARRAY n_leaf2'), ('KINT 1', 'PARRAY n_empty')]),
            ('n_leaf2', (1, 0), False, [('KINT 0', 'PINT 3'), ('KINT 1', 'PINT 6')]),
            ('n_empty', (1, 1), True, []),
        ]
    return [
        ('n_value', (), False, [('KSTRING ($ptascii("left"))', 'PARRAY n_left'), ('KSTRING ($ptascii("right"))', 'PARRAY n_right')]),
        ('n_left', (0,), False, [('KSTRING ($ptascii("deep"))', 'PARRAY n_deep'), ('KSTRING ($ptascii("empty"))', 'PARRAY n_empty')]),
        ('n_deep', (0, 0), False, [('KINT 0', 'PARRAY n_leaf0'), ('KINT 1', 'PARRAY n_leaf1')]),
        ('n_leaf0', (0, 0, 0), False, [('KINT 0', 'PINT 2'), ('KINT 1', 'PINT 8')]),
        ('n_leaf1', (0, 0, 1), False, [('KINT 0', 'PINT 3'), ('KINT 1', 'PINT 7')]),
        ('n_empty', (0, 1), True, []),
        ('n_right', (1,), False, [('KINT 0', 'PARRAY n_leaf2'), ('KINT 1', 'PARRAY n_leaf3')]),
        ('n_leaf2', (1, 0), False, [('KINT 0', 'PINT 4'), ('KINT 1', 'PINT 6')]),
        ('n_leaf3', (1, 1), True, [('KINT 0', 'PINT 5'), ('KINT 1', 'PINT 9')]),
    ]


def items(state, node, entries):
    return f'{state}.ARRAYS[{node}].ITEMS = [' + ', '.join(
        f'ENTRY ({key}) (DIRECT ({value}))' for key, value in entries) + ']'


def retained_pools(state, nodes):
    checks = []
    for node, _, pooled, entries in nodes:
        if pooled:
            checks += [
                f'(HARRAY {node}) <- {state}.ALLOCATIONS', items(state, node, entries),
                f'$heap_count(HARRAY {node}, $pools_nodes({state}.POOLS)) = 1',
                f'$heap_owners($heap_graph({state}), HARRAY {node}) = 1',
            ]
        else:
            checks.append(f'~((HARRAY {node}) <- {state}.ALLOCATIONS)')
    return checks


def expected_stderr(name, path):
    if name.endswith('supplied-throw'):
        return b''
    return (b'Deprecated: Using null as an array offset is deprecated, use an empty string instead in '
            + bytes(path) + b' on line 10\n')


def conditions(name, program, path, stdout):
    thrown = name.endswith('supplied-throw')
    line = 11 if thrown else 10
    nodes = graph(thrown)
    args = 'n_a, n_value, phpType13*, z'
    marker = 'ARRAY_KEY_NULL_TMP_RESULT n_a n_value phpType13* z'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 20, 'S') + [
        '$array_null_tmp_plan(S) = ((' + args + '))', f'z = {line}',
        'S.RESULT = KNOWN (PARRAY n_value)', 'n_a =/= n_value',
        'S.TODO = (ARRAY_VALUE n_a (VARIABLE n_key_name* z_key) phpType13* z) :: ptask_tail*',
        'S.ORIGIN = (PORIGIN n_unit pcpath)', 'pcpath_value = pcpath ++ [PCFIELD 1]',
        '$compiled_read(S, PORIGIN n_unit pcpath_value) = eps',
        '$code_at(S.CODE, n_unit) = (pcode)',
        '$code_expression(pcode.EXPRESSIONS, pcpath_value) = ((z, false))',
        '$array_null_tmp_source(S, ' + args + ')', '$array_null_tmp_ready(S, n_a, n_value)',
        '~$array_null_value_ready(S, n_a, n_value)',
        '$array_null_key_plan(S) = eps', '$array_null_value_plan(S) = eps',
        '$array_null_const_plan(S) = eps', '$array_float_key_plan(S) = eps',
        '~$array_null_tmp_source(S[.ORIGIN = eps], ' + args + ')',
        '~$array_null_tmp_source(S[.CODE = eps], ' + args + ')',
        '~$array_null_tmp_source(S, n_a, n_value, phpType13*, $(z + 1))',
        '$lookup(S.ENV, $ptascii("seed")) = (n_seed)',
        f'S.STORE[n_seed] = DEFINED (PINT {4 if thrown else 5})',
        '$lookup(S.ENV, $ptascii("key")) = (n_key)', 'S.STORE[n_key] = DEFINED PNULL',
        '$lookup(S.ENV, $ptascii("calls")) = (n_calls)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        '$array_null_tmp_plan(S[.STORE[n_key] = DEFINED (PINT 9)]) = eps',
        '$array_null_tmp_plan(S[.RESULT = KNOWN PNULL]) = eps',
        '~$array_null_tmp_ready(S, n_a, n_a)',
        '$heap_count(HARRAY n_value, $machine_roots(S)) = 1',
    ]
    for node, indices, pooled, entries in nodes:
        checks += [items('S', node, entries), f'(HARRAY {node}) <- S.ALLOCATIONS',
                   f'$heap_count(HARRAY {node}, $pools_nodes(S.POOLS)) = {int(pooled)}',
                   f'$heap_owners($heap_graph(S), HARRAY {node}) = {2 if pooled else 1}']
        suffix = ', '.join(f'PCFIELD 0, PCINDEX {index}, PCFIELD 1' for index in indices)
        origin = 'PORIGIN n_unit (pcpath_value ++ [' + suffix + '])'
        checks.append(f'$pool_value(S.POOLS, {origin}) = ' + (f'(PARRAY {node})' if pooled else 'eps'))
        if indices:
            checks.append(f'$heap_count(HARRAY {node}, $task_nodes({marker})) = 0')
    checks += [
        '$array_null_tmp_ready(S, n_a, n_leaf0)', '$array_null_value_ready(S, n_a, n_leaf0)',
        '~$array_null_tmp_ready(S, n_a, n_empty)',
        '~$array_null_tmp_ready(S, n_a, (|S.ARRAYS|))',
        '~$array_null_tmp_ready(S, (|S.ARRAYS|), n_value)',
        'S_alias = S[.REFCELLS = n_seed :: S.REFCELLS][.ARRAYS[n_leaf0].ITEMS = [ENTRY (KINT 0) (ALIAS n_seed)]]',
        '$heap_valid($heap_graph(S_alias))', '~$array_null_tmp_ready(S_alias, n_a, n_value)',
        'S_cycle = S[.ARRAYS[n_leaf0].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf0))]]',
        '~$array_null_tmp_ready(S_cycle, n_a, n_value)',
        'S_back = S[.ARRAYS[n_leaf0].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_value))]]',
        '~$array_null_tmp_ready(S_back, n_a, n_value)',
        'S_builder = S[.ARRAYS[n_leaf0].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_a))]]',
        '~$array_null_tmp_ready(S_builder, n_a, n_value)',
        'S_bounds = S[.ARRAYS[n_leaf0].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY (|S.ARRAYS|)))]]',
        '~$array_null_tmp_ready(S_bounds, n_a, n_value)',
        '~$array_null_tmp_ready(S[.ALLOCATIONS = [HARRAY n_a, HARRAY n_value]], n_a, n_value)',
        'S_dag = S[.ARRAYS[n_value].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf0)), ENTRY (KINT 1) (DIRECT (PARRAY n_leaf0))]]',
        '$heap_valid($heap_graph(S_dag))', '$array_null_tmp_ready(S_dag, n_a, n_value)',
        '$heap_owners($heap_graph(S_dag), HARRAY n_leaf0) = 2',
        'S_debt = S_dag[.LITERALARRAYDEBTS = [n_leaf0]]',
        '$heap_valid($heap_graph(S_debt))', '~$array_null_tmp_ready(S_debt, n_a, n_value)',
        '~$array_null_tmp_ready(S[.LITERALARRAYDEBTS = [n_value]], n_a, n_value)',
        '$heap_valid($heap_graph(S))', '$call_descriptors_valid(S)',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, 'perrorcall.LINE = z', 'perrorcall.LEVEL = 8192',
        'perrorcall.MESSAGE = $list_null_key_message()', '$error_call_valid(S_dispatch, perrorcall)',
        '$task_nodes(' + marker + ') = [HARRAY n_a, HARRAY n_value]',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_value) = 1',
        '$heap_owners($heap_graph(S_dispatch), HARRAY n_leaf0) = 1',
    ] + empty_biases('S_dispatch') + driven('S', 'S_dispatch', 'S_driven') + seek('S_driven', 23, 'S_entered') + [
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_caller*',
        'perrorcall_entered.RESUME = ' + marker,
        '$heap_count(HARRAY n_value, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HARRAY n_leaf0, $tasks_nodes(pframe.TODO)) = 0',
        '$heap_owners($heap_graph(S_entered), HARRAY n_value) = 1',
    ]
    copies = []
    if thrown:
        checks += [
            '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)',
            'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', '$lookup(S.ENV, $ptascii("later")) = (n_later)',
            'S_object = S[.ARRAYS[n_leaf0].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_second))]]',
            '$heap_valid($heap_graph(S_object))', '~$array_null_tmp_ready(S_object, n_a, n_value)',
        ] + seek('S_entered', 24, 'S_discard') + [
            'S_discard.TODO = (THROW_SEARCH n_second) :: (ERROR_HANDLER_RESULT perrorcall_discard) :: ptask_pending*',
            'perrorcall_discard.RESUME = ' + marker,
            '$entry_lookup(S_discard.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PINT 8))',
            '$heap_owners($heap_graph(S_discard), HARRAY n_value) = 1',
            'S_popped = S_discard[.TODO = (THROW_SEARCH n_second) :: ptask_pending*]',
            '$heap_owners($heap_graph(S_popped), HARRAY n_value) = 0',
            '$heap_owners($heap_graph(S_popped), HARRAY n_leaf0) = 1',
            '$error_read_discard(S_popped, ' + marker + ') = S_popped',
            'PhpStep: S_discard ~> S_released', 'S_released.STORE = S_discard.STORE',
        ] + driven('S_discard', 'S_released', 'S_release_driven') + seek('S_release_driven', 14, 'S_catch') + [
            'S_catch.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_after*',
            'S_catch.STORE[n_dest] = DEFINED (PINT 99)', 'S_catch.STORE[n_later] = DEFINED (PINT 7)',
            '$throwable_previous_id(S_catch, n_second) = eps',
            '~((HARRAY n_a) <- S_catch.ALLOCATIONS)',
        ] + retained_pools('S_catch', nodes) + seek('S_catch', 15, 'S_read')
    else:
        checks += seek('S_entered', 21, 'S_resume') + [
            'S_resume.TODO = (' + marker + ') :: ptask_after*',
            '$array_null_tmp_source(S_resume, ' + args + ')', '$array_null_tmp_ready(S_resume, n_a, n_value)',
            '$array_null_tmp_ready(S_resume[.ENV = eps], n_a, n_value)',
            'S_resume.STORE[n_seed] = DEFINED (PINT 99)', 'S_resume.STORE[n_key] = DEFINED (PINT 9)',
            '$tmp_subtree_deprecations(S_resume.EVENTS) = 1',
            'S_bad = S_resume[.REFCELLS = n_seed :: S_resume.REFCELLS][.ARRAYS[n_leaf0].ITEMS = [ENTRY (KINT 0) (ALIAS n_seed)]]',
            '$heap_valid($heap_graph(S_bad))', '$array_null_tmp_source(S_bad, ' + args + ')',
            '$error_read_discard(S_bad, ' + marker + ') = S_bad[.COMPLETION = UNSUPPORTED "array literal null-key temporary array during throw"]',
            'PhpStep: S_bad ~> S_bad_out',
            'S_bad_out.COMPLETION = UNSUPPORTED "array literal null-key temporary array after callback"',
            'S_bad_out.STORE = S_bad.STORE',
            'PhpStep: S_resume ~> S_insert',
            '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_value))',
            '$entry_lookup(S_insert.ARRAYS[n_a].ITEMS, KINT 9) = eps', 'S_insert.STORE = S_resume.STORE',
            '$heap_count(HARRAY n_value, $machine_roots(S_insert)) = 0',
            '$heap_owners($heap_graph(S_insert), HARRAY n_value) = 1',
            '$heap_owners($heap_graph(S_insert), HARRAY n_leaf0) = 1',
        ] + driven('S_resume', 'S_insert', 'S_insert_driven') + seek('S_insert_driven', 17, 'S_copied') + [
            '$lookup(S_copied.ENV, $ptascii("copy")) = (n_copy_cell)',
            'S_copied.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_a',
            '$entry_lookup(S_copied.ARRAYS[n_copy].ITEMS, KSTRING eps) = (DIRECT (PARRAY n_copy_value))',
            '$entry_lookup(S_copied.ARRAYS[n_copy_value].ITEMS, KSTRING ($ptascii("left"))) = (DIRECT (PARRAY n_copy_left))',
            '$entry_lookup(S_copied.ARRAYS[n_copy_left].ITEMS, KSTRING ($ptascii("deep"))) = (DIRECT (PARRAY n_copy_deep))',
            '$entry_lookup(S_copied.ARRAYS[n_copy_deep].ITEMS, KINT 0) = (DIRECT (PARRAY n_copy_leaf0))',
            '$entry_lookup(S_copied.ARRAYS[n_copy_value].ITEMS, KSTRING ($ptascii("right"))) = (DIRECT (PARRAY n_copy_right))',
            '$entry_lookup(S_copied.ARRAYS[n_copy_right].ITEMS, KINT 1) = (DIRECT (PARRAY n_copy_leaf3))',
            pair('S_copied', 'n_leaf0', 2, 8), pair('S_copied', 'n_copy_leaf0', 66, 8),
            pair('S_copied', 'n_leaf3', 5, 9), pair('S_copied', 'n_copy_leaf3', 5, 99),
            '$entry_lookup(S_copied.ARRAYS[n_copy_deep].ITEMS, KINT 1) = (DIRECT (PARRAY n_leaf1))',
            '$entry_lookup(S_copied.ARRAYS[n_copy_left].ITEMS, KSTRING ($ptascii("empty"))) = (DIRECT (PARRAY n_empty))',
            '$entry_lookup(S_copied.ARRAYS[n_copy_right].ITEMS, KINT 0) = (DIRECT (PARRAY n_leaf2))',
            '$heap_owners($heap_graph(S_copied), HARRAY n_leaf0) = 1',
            '$heap_owners($heap_graph(S_copied), HARRAY n_leaf1) = 2',
            '$heap_owners($heap_graph(S_copied), HARRAY n_leaf2) = 2',
            '$heap_owners($heap_graph(S_copied), HARRAY n_empty) = 3',
            '$heap_owners($heap_graph(S_copied), HARRAY n_leaf3) = 2',
        ]
        copies = ['n_copy', 'n_copy_value', 'n_copy_left', 'n_copy_deep', 'n_copy_leaf0', 'n_copy_right', 'n_copy_leaf3']
        checks += [f'{copy} =/= {original}' for copy, original in zip(copies, ['n_a', 'n_value', 'n_left', 'n_deep', 'n_leaf0', 'n_right', 'n_leaf3'])]
        checks += seek('S_copied', 15, 'S_read') + [
            '$lookup(S_read.ENV, $ptascii("copy")) = eps',
            'S_read.ARRAYS[n_a].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)), ENTRY (KINT 4) (DIRECT (PINT 66))]',
        ]
    checks += retained_pools('S_read', nodes) + [
        'S_read.CURRENT = eps', 'S_read.FRAMES = eps', 'S_read.GLOBALTABLE = eps',
        'S_read.STORE[n_seed] = DEFINED (PINT 99)', 'S_read.STORE[n_key] = DEFINED (PINT 9)',
        'S_read.STORE[n_calls] = DEFINED (PINT 1)',
        f'$tmp_subtree_deprecations(S_read.EVENTS) = {0 if thrown else 1}',
        '$heap_valid($heap_graph(S_read))', '$call_descriptors_valid(S_read)',
        '$drive_steps(S_read, 0) = S_read[.COMPLETION = BUDGET]',
        'S_split = $drive_steps(S_read, 1)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL], 3000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '~((HARRAY n_a) <- S_done.ALLOCATIONS)', '~((HCELL n_seed) <- S_done.ALLOCATIONS)',
        '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
    ] + retained_pools('S_done', nodes) + empty_biases('S_read') + empty_biases('S_done')
    checks += [f'~((HARRAY {copy}) <- S_done.ALLOCATIONS)' for copy in copies]
    if thrown:
        checks.append('~((HOBJECT n_second) <- S_done.ALLOCATIONS)')
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS, expected_stderr=expected_stderr) else 1)
