#!/usr/bin/env python3
"""Reached dynamic ancestor contexts, silent NULL descent and throw cleanup."""
import base64
import hashlib
import json
from pathlib import Path

import list_recursive_cv_missing_warning_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 6) = true
  -- if S.TODO = (THROW_SEARCH n) :: (TRY_END porigin) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 7) = true
  -- if S.TODO = (LIST_FETCH (KNOWN PNULL) 0 expression false phpType13* z) :: ptask_tail*
  -- if S.RESULT = VARIABLE ($ptascii("middle")) z_key
def $list_warning_frontier(S, 8) = true
  -- if S.TODO = (LIST_FETCH (KNOWN PNULL) 0 expression false phpType13* z) :: ptask_tail*
  -- if S.RESULT = KNOWN (PINT 0)
def $list_warning_frontier(S, 9) = true
  -- if S.TODO = (LIST_FETCH (KNOWN PNULL) 1 expression false phpType13* z) :: ptask_tail*
'''


def seek(start, stage, result):
    return [f'{result}_found = $list_warning_seek({start}, {stage}, 2000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def conditions(name, program, path, stdout):
    null = name.endswith('ancestor-null')
    thrown = name.endswith('depth3-throw')
    array = 'n_root' if null else 'n_inner'
    operand = 'REFERENCE n_inner_cell' if thrown else f'KNOWN (PARRAY {array})'
    key = 'KSTRING ($ptascii("gone"))' if thrown else 'KINT 0'
    key_name = 'outer' if null else 'key'
    line = 18 if thrown else 17
    args = f'{operand}, 0, expression, phpType13*, z, {key}'
    marker = f'LIST_MISSING_RESULT ({operand}) 0 expression phpType13* z ({key})'
    branch = 1 if thrown else 0
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S')
    checks += [
        '$list_missing_plan(S) = ((' + args + '))',
        f'S.TODO = (LIST_FETCH ({operand}) 0 expression false phpType13* z) :: ptask_tail*',
        f'$list_missing_array(S, {operand}) = ({array})',
        f'z = {line}', 'S.ORIGIN = (porigin)',
        f'S.RESULT = VARIABLE ($ptascii("{key_name}")) z',
        '$list_missing_recursive_cv_item(S, porigin, 0, expression, phpType13*, z) = (S.RESULT)',
        f'$lookup(S.ENV, $ptascii("{key_name}")) = (n_key_cell)',
        'S.STORE[n_key_cell] = DEFINED pvalue_key', '$list_missing_quiet_key(pvalue_key) = (' + key + ')',
        '$lookup(S.ENV, $ptascii("a")) = (n_a)', 'S.STORE[n_a] = DEFINED (PARRAY n_root)',
        '$lookup(S.ENV, $ptascii("x")) = (n_x)', 'S.STORE[n_x] = DEFINED (PINT 7)',
        '$lookup(S.ENV, $ptascii("y")) = (n_y)', 'S.STORE[n_y] = DEFINED (PINT 8)',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        '$list_missing_source(S, ' + args + ')',
        '$list_missing_recursive_cv_context(S, porigin) = (z_initial)',
        '$list_missing_recursive_cv_operand_source(S, porigin, ' + operand + ')',
        f'~$list_missing_source(S, KNOWN PNULL, 0, expression, phpType13*, z, {key})',
        f'~$list_missing_source(S, {operand}, 1, expression, phpType13*, z, {key})',
        f'~$list_missing_source(S, {operand}, 0, expression, eps, z, {key})',
        f'~$list_missing_source(S, {operand}, 0, expression, phpType13*, $(z + 1), {key})',
        '~$list_missing_source(S[.SOURCES = eps], ' + args + ')',
        '~$list_missing_source(S[.CODE = eps], ' + args + ')',
        '~$list_missing_source(S[.ALLOCATIONS = eps], ' + args + ')',
        '$list_missing_plan(S[.RESULT = KNOWN pvalue_key]) = eps',
        '$list_missing_plan(S[.RESULT = VARIABLE ($ptascii("other")) z]) = eps',
        f'$list_missing_plan(S[.RESULT = VARIABLE ($ptascii("{key_name}")) $(z + 1)]) = eps',
        '$list_missing_plan(S[.STORE[n_key_cell] = UNDEFINED]) = eps',
        '$list_missing_plan(S[.STORE[n_key_cell] = DEFINED PNULL]) = eps',
        '$list_missing_plan(S[.STORE[n_key_cell] = DEFINED (PARRAY n_root)]) = eps',
        '$list_missing_plan(S[.STORE[n_key_cell] = DEFINED (PFLOAT 4609434218613702656)]) = eps',
        f'$entry_lookup(S.ARRAYS[{array}].ITEMS, {key}) = eps',
    ]
    if null:
        checks += ['pvalue_key = PBOOL false', 'porigin_root = porigin',
                   '$list_missing_integer_cv_item(S, 0, expression, phpType13*, z) = eps',
                   '$list_missing_nested_context(S, porigin) = (z_initial)']
    else:
        checks += [
            '$list_missing_integer_cv_item(S, 0, expression, phpType13*, z) = (S.RESULT)',
            '$list_missing_nested_context(S, porigin) = eps',
            f'$reference_origin_parent(porigin, 3) = ((porigin_mid, [PCFIELD 0, PCINDEX {branch}, PCFIELD 1]))',
            f'$reference_origin_parent(porigin_mid, 3) = ((porigin_root, [PCFIELD 0, PCINDEX {branch}, PCFIELD 1]))',
            '$list_missing_recursive_cv_context(S, porigin_mid) = (z_mid)',
            '$list_missing_recursive_cv_context(S, porigin_root) = (z_root)',
            '$origin_node(S.SOURCES, porigin_root) = (expression_root)', '$list_pattern(expression_root) = (phpType13_root*)',
            '$origin_node(S.SOURCES, porigin_mid) = (expression_mid)', '$list_pattern(expression_mid) = (phpType13_mid*)',
            f'$list_missing_recursive_cv_item_line(S, porigin_root, phpType13_root*, {branch}, z_root) = ((expression_mid, phpType13_root_tail*, z_mid))',
            f'$list_missing_recursive_cv_item_line(S, porigin_mid, phpType13_mid*, {branch}, z_mid) = ((expression_inner, phpType13_mid_tail*, z_initial))',
            '$origin_node(S.SOURCES, porigin) = (expression_inner)',
            '$lookup(S.ENV, $ptascii("outer")) = (n_outer_key_cell)',
            '$lookup(S.ENV, $ptascii("middle")) = (n_middle_key_cell)',
            '$lookup(S.ENV, $ptascii("q")) = (n_q)', 'S.STORE[n_q] = DEFINED (PINT 2)',
            '$entry_lookup(S.ARRAYS[n_inner].ITEMS, KINT 1) = (ALIAS n_q)',
            '$heap_owners($heap_prune($heap_graph(S)), HCELL n_q) = 2',
        ]
        checks += ['pvalue_key = PSTRING_CARRIER pstringidentity ($ptascii("gone"))',
                   '$string_carrier_valid(S, pvalue_key)'] if thrown else ['pvalue_key = PBOOL false']
    checks += [
        '$origin_node(S.SOURCES, porigin_root) = (expression_root)', '$list_pattern(expression_root) = (phpType13_root*)',
        '~$list_missing_flat(phpType13_root*)', '$list_missing_nested_mixed_items(phpType13_root*)',
        '$reference_origin_parent(porigin_root, 1) = ((porigin_assign, [PCFIELD 0]))',
        '$origin_node(S.SOURCES, porigin_assign) = (NExprAssign expression_root expression_rhs metadata_assign)',
        'porigin_assign = PORIGIN n_unit pcpath_assign', 'S.SOURCES[n_unit] = pcunit',
        'S_literal = S[.SOURCES[n_unit] = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_assign (NExprAssign expression_root (NExprArray (SEQUENCE eps) eps) metadata_assign)) :: pcunit.OCCURRENCES]]',
        '$list_missing_recursive_cv_context(S_literal, porigin) = eps', '~$list_missing_source(S_literal, ' + args + ')',
    ]
    nodes = ['root'] if null else ['root', 'mid', 'inner']
    if thrown:
        checks += ['n_root_cell = n_a',
                   '$entry_lookup(S.ARRAYS[n_root].ITEMS, KINT 1) = (ALIAS n_mid_cell)',
                   'S.STORE[n_mid_cell] = DEFINED (PARRAY n_mid)',
                   '$entry_lookup(S.ARRAYS[n_mid].ITEMS, KINT 1) = (ALIAS n_inner_cell)',
                   'S.STORE[n_inner_cell] = DEFINED (PARRAY n_inner)']
        for node in nodes:
            checks += [f'n_{node}_cell <- S.REFCELLS',
                       f'$heap_count(HCELL n_{node}_cell, $tasks_nodes(S.TODO)) = 1',
                       f'$heap_owners($heap_prune($heap_graph(S)), HCELL n_{node}_cell) = 2',
                       f'$heap_owners($heap_prune($heap_graph(S)), HARRAY n_{node}) = 1',
                       f'$heap_count(HARRAY n_{node}, $pools_nodes(S.POOLS)) = 0']
    else:
        if not null:
            checks += ['$entry_lookup(S.ARRAYS[n_root].ITEMS, KINT 0) = (DIRECT (PARRAY n_mid))',
                       '$entry_lookup(S.ARRAYS[n_mid].ITEMS, KINT 0) = (DIRECT (PARRAY n_inner))']
        for node in nodes:
            checks += [f'n_pool_{node} = $heap_count(HARRAY n_{node}, $pools_nodes(S.POOLS))',
                       f'$heap_count(HARRAY n_{node}, $tasks_nodes(S.TODO)) = 1',
                       f'$heap_owners($heap_prune($heap_graph(S)), HARRAY n_{node}) = $(2 + n_pool_{node})']
        checks += ['$(n_pool_root > 0)'] if null else [f'n_pool_{node} = 0' for node in nodes]
    checks += [
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_dispatch', 'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
    ] + seek('S_dispatch', 3, 'S_entered') + [
        'S_entered.CURRENT =/= eps', 'S_entered.FRAMES = pframe :: eps',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    for node in nodes:
        kind = f'HCELL n_{node}_cell' if thrown else f'HARRAY n_{node}'
        checks += [f'$heap_count({kind}, $tasks_nodes(pframe.TODO)) = 1']
    if thrown:
        checks += ['$lookup(S.ENV, $ptascii("before")) = (n_before)', 'S.STORE[n_before] = DEFINED (PINT 5)',
                   '$lookup(S.ENV, $ptascii("outerbefore")) = (n_outerbefore)', 'S.STORE[n_outerbefore] = DEFINED (PINT 9)',
                   '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)', 'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)']
        checks += seek('S_entered', 5, 'S_discard')
        for node in nodes:
            checks += [f'$heap_count(HCELL n_{node}_cell, $tasks_nodes(S_discard.TODO)) = {0 if node == "inner" else 1}',
                       f'$heap_owners($heap_prune($heap_graph(S_discard)), HCELL n_{node}_cell) = {2 if node == "mid" else 1}',
                       f'$heap_owners($heap_prune($heap_graph(S_discard)), HARRAY n_{node}) = 1']
        checks += ['$heap_owners($heap_prune($heap_graph(S_discard)), HCELL n_q) = 1'] + seek('S_discard', 6, 'S_pending')
        checks += ['S_pending.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_pending*',
                   'S_pending.ERRORHANDLER = S.ERRORHANDLER', '$throwable_previous_id(S_pending, n_second) = eps']
        for node in nodes:
            checks += [f'~((HCELL n_{node}_cell) <- S_pending.ALLOCATIONS)', f'~((HARRAY n_{node}) <- S_pending.ALLOCATIONS)']
        checks += ['~((HCELL n_q) <- S_pending.ALLOCATIONS)', '~((HCELL n_key_cell) <- S_pending.ALLOCATIONS)',
                   '~((HCELL n_outer_key_cell) <- S_pending.ALLOCATIONS)', '~((HCELL n_middle_key_cell) <- S_pending.ALLOCATIONS)',
                   '$lookup(S_pending.ENV, $ptascii("a")) = eps', '$lookup(S_pending.ENV, $ptascii("key")) = eps',
                   '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
                   'S_done = $drive_steps(S_pending, 2000)',
                   'S_done.STORE[n_x] = DEFINED (PINT 99)', 'S_done.STORE[n_y] = DEFINED (PINT 8)',
                   'S_done.STORE[n_before] = DEFINED (PINT 5)', 'S_done.STORE[n_outerbefore] = DEFINED (PINT 9)',
                   'S_done.STORE[n_dest] = DEFINED (PINT 100)']
    else:
        checks += seek('S_entered', 2, 'S_return') + [
            'S_return.TODO = (' + marker + ') :: ptask_tail*', '$list_missing_source(S_return, ' + args + ')',
            '$list_missing_recursive_cv_context(S_return, porigin) = (z_initial)',
            'S_return.ERRORHANDLER = S.ERRORHANDLER', 'S_return.STORE[n_x] = DEFINED (PINT 99)',
            'S_return.STORE[n_a] = DEFINED (PARRAY n_live)', 'n_live =/= n_root',
            'S_return.STORE[n_key_cell] = DEFINED (PFLOAT n_changed)', '$float_long(n_changed, true) = (1, [PRECISIONLOSS])',
            'PhpStep: S_return ~> S_schedule',
            f'S_schedule.TODO = $list_fetched_tasks(S_return[.RESULT = KNOWN PNULL], {operand}, 0, expression, false, phpType13*, z) ++ ptask_tail*',
            'S_schedule.STORE = S_return.STORE', 'S_schedule.ARRAYS = S_return.ARRAYS', 'S_schedule.RESULT = KNOWN PNULL',
        ]
        if null:
            checks += ['$lookup(S_return.ENV, $ptascii("middle")) = (n_middle_key_cell)',
                       'S_return.STORE[n_y] = DEFINED (PINT 88)',
                       '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_root) = $(1 + n_pool_root)']
            checks += seek('S_schedule', 7, 'S_null_key') + [
                'S_null_key.TODO = (LIST_FETCH (KNOWN PNULL) 0 expression_child false phpType13_child* z_child) :: ptask_child*',
                'S_null_key.RESULT = VARIABLE ($ptascii("middle")) z_child',
                'S_null_key.STORE[n_middle_key_cell] = DEFINED (PFLOAT n_middle_bits)',
                '$float_long(n_middle_bits, true) = (2, [PRECISIONLOSS])', '$list_missing_plan(S_null_key) = eps',
                'PhpStep: S_null_key ~> S_null_descend', 'S_null_descend.STORE = S_null_key.STORE',
                'S_null_descend.ARRAYS = S_null_key.ARRAYS',
                'S_null_descend.TODO = (AT porigin_child (LIST_PATTERN expression_child (KNOWN PNULL) z_child)) :: ptask_null_tail*',
                'S_null_descend_driven = $drive_steps(S_null_key, 1)',
                'S_null_descend_driven.TODO = S_null_descend.TODO',
            ] + seek('S_null_descend_driven', 8, 'S_null_x') + [
                'S_null_x.STORE[n_x] = DEFINED (PINT 99)', 'S_null_x.STORE[n_y] = DEFINED (PINT 88)',
                'PhpStep: S_null_x ~> S_null_x_read', 'S_null_x_read.RESULT = KNOWN PNULL',
                'S_null_x_driven = $drive_steps(S_null_x, 1)', 'S_null_x_driven.TODO = S_null_x_read.TODO',
            ] + seek('S_null_x_driven', 9, 'S_null_y') + [
                'S_null_y.STORE[n_x] = DEFINED PNULL', 'S_null_y.STORE[n_y] = DEFINED (PINT 88)',
                '$list_missing_plan(S_null_y) = eps', 'PhpStep: S_null_y ~> S_null_y_read',
                'S_null_y_read.RESULT = KNOWN PNULL',
                'S_done = $drive_steps(S_null_y, 2000)', 'S_done.STORE[n_x] = DEFINED PNULL', 'S_done.STORE[n_y] = DEFINED PNULL',
                '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_root) = n_pool_root',
                '(HARRAY n_root) <- S_done.ALLOCATIONS',
            ]
        else:
            checks += ['S_return.STORE[n_y] = DEFINED (PINT 8)', 'S_return.STORE[n_outer_key_cell] = DEFINED PNULL',
                       'S_return.STORE[n_middle_key_cell] = DEFINED (PFLOAT n_middle_bits)',
                       '$float_long(n_middle_bits, true) = (1, [PRECISIONLOSS])',
                       '$lookup(S_return.ENV, $ptascii("q")) = eps', 'S_return.STORE[n_q] = DEFINED (PINT 33)',
                       '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_q) = 1']
            for node in nodes:
                checks += [f'$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_{node}) = {1 if node == "root" else 2}']
            checks += seek('S_schedule', 4, 'S_next') + [
                'S_next.TODO = (LIST_FETCH (KNOWN (PARRAY n_inner)) 1 expression_y false eps z_y) :: ptask_y*',
                'S_next.RESULT = VARIABLE ($ptascii("next")) z_y',
                '$lookup(S_next.ENV, $ptascii("next")) = (n_next_key_cell)',
                'S_next.STORE[n_next_key_cell] = DEFINED pvalue_next', '$string_bytes(pvalue_next) = ($ptascii("1"))',
                '$list_missing_quiet_key(pvalue_next) = (KINT 1)',
                'S_next.STORE[n_x] = DEFINED PNULL', 'S_next.STORE[n_y] = DEFINED (PINT 8)',
                'PhpStep: S_next ~> S_read',
                'S_read.TODO = (AT porigin_y (LIST_STORE expression_y (KNOWN (PINT 33)) false z_store_y)) :: ptask_read*',
                'S_read.STORE = S_next.STORE', 'S_read.ARRAYS = S_next.ARRAYS',
                'S_read_driven_found = $drive_steps(S_next, 1)', 'S_read_driven_found.COMPLETION = BUDGET',
                'S_read_driven = S_read_driven_found[.COMPLETION = NORMAL]', 'S_read_driven.TODO = S_read.TODO',
                'S_read_driven.STORE = S_read.STORE', 'S_read_driven.ARRAYS = S_read.ARRAYS',
                'S_done = $drive_steps(S_read_driven, 2000)', 'S_done.STORE[n_x] = DEFINED PNULL',
                'S_done.STORE[n_y] = DEFINED (PINT 33)',
            ]
            for node in nodes:
                checks += [f'~((HARRAY n_{node}) <- S_done.ALLOCATIONS)']
            checks += ['~((HCELL n_q) <- S_done.ALLOCATIONS)',
                       '$lookup(S_done.ENV, $ptascii("near")) = (n_near)', 'S_done.STORE[n_near] = DEFINED (PINT 3)']
        checks += ['$lookup(S_done.ENV, $ptascii("tail")) = (n_tail)', f'S_done.STORE[n_tail] = DEFINED (PINT {3 if null else 4})']
    return checks + [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]', '$drive_steps(S, 2000) = S_done',
    ]


if __name__ == '__main__':
    own = Path(__file__)
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    passed = shared.run(cases, conditions, HELPERS)
    assert before == hashlib.sha256(own.read_bytes()).hexdigest()
    raise SystemExit(0 if passed else 1)
