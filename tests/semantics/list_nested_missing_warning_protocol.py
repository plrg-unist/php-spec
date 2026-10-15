#!/usr/bin/env python3
"""Reached inner-list warnings, both array owners, compiler lines and unwind."""
import base64
import hashlib
import json
from pathlib import Path

import list_nested_missing_warning_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 6) = true
  -- if S.TODO = (THROW_SEARCH n) :: (TRY_END porigin) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
'''


def conditions(name, program, path, stdout):
    keyed = name.endswith('inner-keyed')
    thrown = name.endswith('inner-throw')
    index, key, line = (1, 3, 14) if keyed else (0, 0, 14 if thrown else 13)
    outer_index = 1 if thrown else 0
    x, y, tail = (8, 9, 10) if keyed else (7, 8, 9)
    fetched = 6 if keyed else 33
    args = f'KNOWN (PARRAY n_inner), {index}, expression, phpType13*, z, KINT {key}'
    marker = f'LIST_MISSING_RESULT (KNOWN (PARRAY n_inner)) {index} expression phpType13* z (KINT {key})'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $list_warning_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET', 'S = S_found[.COMPLETION = NORMAL]',
        f'$list_missing_plan(S) = ((KNOWN (PARRAY n_inner), {index}, expression, phpType13*, z, KINT {key}))',
        f'S.TODO = (LIST_FETCH (KNOWN (PARRAY n_inner)) {index} expression false phpType13* z) :: ptask_tail*',
        f'z = {line}', 'S.ORIGIN = (porigin)',
        f'$reference_origin_parent(porigin, 3) = ((porigin_outer, [PCFIELD 0, PCINDEX {outer_index}, PCFIELD 1]))',
        '$origin_node(S.SOURCES, porigin_outer) = (expression_outer)',
        '$list_pattern(expression_outer) = (phpType13_outer*)',
        '~$list_missing_flat(phpType13_outer*)', '$list_missing_nested_items(phpType13_outer*)',
        '$list_missing_nested_items([NArrayItem ABSENT expression_outer (BOOLEAN false) (BOOLEAN false) eps])',
        '~$list_missing_nested_items([NArrayItem ABSENT expression (BOOLEAN true) (BOOLEAN false) eps])',
        '$list_missing_nested_context(S, porigin) = (z_initial)',
        '$reference_origin_parent(porigin_outer, 1) = ((porigin_assign, [PCFIELD 0]))',
        '$origin_node(S.SOURCES, porigin_assign) = (NExprAssign expression_outer expression_rhs metadata_assign)',
        'porigin_assign = PORIGIN n_unit pcpath_assign', 'S.SOURCES[n_unit] = pcunit',
        'S_wide = S[.SOURCES[n_unit] = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_assign (NExprAssign expression_outer (NScalarInt (INTEGER 1) eps) metadata_assign)) :: pcunit.OCCURRENCES]]',
        '$list_missing_nested_context(S_wide, porigin) = eps', '~$list_missing_source(S_wide, ' + args + ')',
        '$lookup(S.ENV, $ptascii("a")) = (n_a)', 'S.STORE[n_a] = DEFINED (PARRAY n_outer)',
        f'$entry_lookup(S.ARRAYS[n_outer].ITEMS, KINT {outer_index}) = (DIRECT (PARRAY n_inner))', 'n_outer =/= n_inner',
        '$lookup(S.ENV, $ptascii("x")) = (n_x)', f'S.STORE[n_x] = DEFINED (PINT {x})',
        '$lookup(S.ENV, $ptascii("y")) = (n_y)', f'S.STORE[n_y] = DEFINED (PINT {y})',
        '$lookup(S.ENV, $ptascii("tail")) = (n_tail)', f'S.STORE[n_tail] = DEFINED (PINT {tail})',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        '$list_missing_source(S, ' + args + ')',
        f'~$list_missing_source(S, KNOWN (PARRAY n_inner), {index}, expression, phpType13*, $(z + 1), KINT {key})',
        f'~$list_missing_source(S, KNOWN (PARRAY n_inner), {index}, expression, eps, z, KINT {key})',
        f'~$list_missing_source(S, KNOWN (PARRAY n_inner), {index}, expression, phpType13*, z, KINT 9)',
        '~$list_missing_source(S[.ORIGIN = eps], ' + args + ')', '~$list_missing_source(S[.SOURCES = eps], ' + args + ')',
        '~$list_missing_source(S[.CODE = eps], ' + args + ')', '~$list_missing_source(S[.ALLOCATIONS = eps], ' + args + ')',
        f'~$list_missing_source(S, KNOWN (PARRAY (|S.ARRAYS|)), {index}, expression, phpType13*, z, KINT {key})',
        f'~$list_missing_source(S, REFERENCE n_a, {index}, expression, phpType13*, z, KINT {key})',
        '$list_missing_plan(S[.RESULT = KNOWN (PINT 9)]) = eps',
        'n_pool_inner = $heap_count(HARRAY n_inner, $pools_nodes(S.POOLS))',
        'n_pool_outer = $heap_count(HARRAY n_outer, $pools_nodes(S.POOLS))',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_inner) = $(2 + n_pool_inner)',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_outer) = $(2 + n_pool_outer)',
        '$heap_count(HARRAY n_inner, $tasks_nodes(S.TODO)) = 1', '$heap_count(HARRAY n_outer, $tasks_nodes(S.TODO)) = 1',
        '$task_nodes(' + marker + ') = [HARRAY n_inner]',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_dispatch', 'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'S_entered_found = $list_warning_seek(S_dispatch, 3, 2000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', 'S_entered.CURRENT =/= eps',
        'S_entered.FRAMES = pframe :: eps',
        '$heap_count(HARRAY n_inner, $tasks_nodes(pframe.TODO)) = 1',
        '$heap_count(HARRAY n_outer, $tasks_nodes(pframe.TODO)) = 1',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if not keyed:
        checks += [
            'n_pool_inner = 0', 'n_pool_outer = 0', '$lookup(S.ENV, $ptascii("q")) = (n_q)',
            '$entry_lookup(S.ARRAYS[n_inner].ITEMS, KINT 1) = (ALIAS n_q)',
            '$heap_owners($heap_prune($heap_graph(S)), HCELL n_q) = 2',
        ]
    if keyed or thrown:
        checks += ['$lookup(S.ENV, $ptascii("before")) = (n_before)', 'S.STORE[n_before] = DEFINED (PINT 5)']
    if thrown:
        checks += [
            '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)', 'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            'S_discard_found = $list_warning_seek(S_entered, 5, 2000)',
            r'S_discard_found.COMPLETION = NORMAL \/ S_discard_found.COMPLETION = BUDGET',
            'S_discard = S_discard_found[.COMPLETION = NORMAL]',
            '$heap_count(HARRAY n_inner, $tasks_nodes(S_discard.TODO)) = 0',
            '$heap_count(HARRAY n_outer, $tasks_nodes(S_discard.TODO)) = 1',
            '$heap_owners($heap_prune($heap_graph(S_discard)), HARRAY n_inner) = 1',
            '$heap_owners($heap_prune($heap_graph(S_discard)), HARRAY n_outer) = 1',
            '$heap_owners($heap_prune($heap_graph(S_discard)), HCELL n_q) = 1',
            '$call_descriptors_valid(S_discard)', '$heap_valid($heap_graph(S_discard))',
            'S_pending_found = $list_warning_seek(S_discard, 6, 2000)',
            r'S_pending_found.COMPLETION = NORMAL \/ S_pending_found.COMPLETION = BUDGET',
            'S_pending = S_pending_found[.COMPLETION = NORMAL]', 'S_pending.TODO = (THROW_SEARCH n_second) :: ptask_pending*',
            '~((HARRAY n_inner) <- S_pending.ALLOCATIONS)', '~((HARRAY n_outer) <- S_pending.ALLOCATIONS)',
            '~((HCELL n_q) <- S_pending.ALLOCATIONS)', 'S_pending.ERRORHANDLER = S.ERRORHANDLER',
            'S_pending.STORE[n_before] = DEFINED (PINT 5)', 'S_pending.STORE[n_x] = DEFINED (PINT 99)',
            'S_pending.STORE[n_y] = DEFINED (PINT 8)', 'S_pending.STORE[n_tail] = DEFINED (PINT 9)',
            'S_pending.STORE[n_dest] = DEFINED (PINT 100)', '$throwable_previous_id(S_pending, n_second) = eps',
            '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))', 'S_done = $drive_steps(S_pending, 2000)',
        ]
    else:
        checks += [
            'S_return_found = $list_warning_seek(S_entered, 2, 2000)',
            r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
            'S_return = S_return_found[.COMPLETION = NORMAL]', 'S_return.TODO = (' + marker + ') :: ptask_tail*',
            '$list_missing_source(S_return, ' + args + ')', 'S_return.ERRORHANDLER = S.ERRORHANDLER',
            'S_return.STORE[n_a] = DEFINED (PARRAY n_rebound)', 'n_rebound =/= n_outer',
            'S_return.STORE[n_x] = DEFINED (PINT 99)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_outer) = $(1 + n_pool_outer)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_inner) = $(2 + n_pool_inner)',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
            'PhpStep: S_return ~> S_store',
            f'S_store.TODO = $list_fetched_tasks(S_return[.RESULT = KNOWN PNULL], KNOWN (PARRAY n_inner), {index}, expression, false, phpType13*, z) ++ ptask_tail*',
            'S_store.STORE = S_return.STORE', 'S_store.ARRAYS = S_return.ARRAYS', 'S_store.RESULT = KNOWN PNULL',
            'S_next_found = $list_warning_seek(S_store, 4, 2000)',
            r'S_next_found.COMPLETION = NORMAL \/ S_next_found.COMPLETION = BUDGET',
            'S_next = S_next_found[.COMPLETION = NORMAL]',
            f'S_next.TODO = (LIST_FETCH (KNOWN (PARRAY n_inner)) {index + 1} expression_next false eps z_next) :: ptask_next*',
            'S_next.STORE[n_x] = DEFINED PNULL', f'S_next.STORE[n_y] = DEFINED (PINT {y})',
            'PhpStep: S_next ~> S_read',
            f'S_read.TODO = (AT porigin_y (LIST_STORE expression_next (KNOWN (PINT {fetched})) false z_y)) :: (LIST_NEXT (KNOWN (PARRAY n_inner)) {index + 2} eps z_follow) :: ptask_next*',
            'S_read.STORE = S_next.STORE', 'S_read.ARRAYS = S_next.ARRAYS',
            '$call_descriptors_valid(S_read)', '$heap_valid($heap_graph(S_read))', 'S_done = $drive_steps(S_read, 2000)',
            'S_done.STORE[n_x] = DEFINED PNULL', f'S_done.STORE[n_y] = DEFINED (PINT {fetched})',
            f'S_done.STORE[n_tail] = DEFINED (PINT {4 if keyed else 3})',
        ]
        if keyed:
            checks += ['S_done.STORE[n_before] = DEFINED (PINT 21)', 'S_done.STORE[n_dest] = DEFINED (PARRAY n_outer)',
                '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_outer) = $(1 + n_pool_outer)',
                '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_inner) = $(1 + n_pool_inner)']
        else:
            checks += ['~((HARRAY n_outer) <- S_done.ALLOCATIONS)', '~((HARRAY n_inner) <- S_done.ALLOCATIONS)', '~((HCELL n_q) <- S_done.ALLOCATIONS)']
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
