#!/usr/bin/env python3
"""Nested mixed source authority, writable descent and staged cell cleanup."""
import base64
import hashlib
import json
from pathlib import Path

import list_nested_reference_missing_warning_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 6) = true
  -- if S.TODO = (LIST_FETCH (REFERENCE n_source) n expression true phpType13* z) :: ptask_tail*
def $list_warning_frontier(S, 7) = true
  -- if S.TODO = (LIST_FETCH (REFERENCE n_source) n expression false phpType13* z) :: ptask_tail*
  -- if $list_missing_array(S, REFERENCE n_source) = eps
def $list_warning_frontier(S, 8) = true
  -- if S.TODO = (THROW_SEARCH n) :: (TRY_END porigin) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
'''


def conditions(name, program, path, stdout):
    known = name.endswith('root-replace')
    null = name.endswith('root-null-descent')
    thrown = not known and not null
    operand = 'KNOWN (PARRAY n_inner)' if known else 'REFERENCE n_source'
    args = operand + ', 0, expression, phpType13*, z, KINT 0'
    marker = 'LIST_MISSING_RESULT (' + operand + ') 0 expression phpType13* z (KINT 0)'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $list_warning_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET', 'S = S_found[.COMPLETION = NORMAL]',
        '$list_missing_plan(S) = ((' + args + '))',
        'S.TODO = (LIST_FETCH (' + operand + ') 0 expression false phpType13* z) :: ptask_tail*',
        f'z = {14 if known else 16 if null else 15}', 'S.RESULT = KNOWN (PINT 0)', 'S.ORIGIN = (porigin)',
        '$lookup(S.ENV, $ptascii("a")) = (n_root_cell)', 'S.STORE[n_root_cell] = DEFINED (PARRAY n_root)',
        'n_root_cell <- S.REFCELLS', '$heap_count(HCELL n_root_cell, $tasks_nodes(S.TODO)) = 1',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_root_cell) = 2',
    ]
    if known:
        checks += [
            '$reference_origin_parent(porigin, 3) = ((porigin_root, [PCFIELD 0, PCINDEX 0, PCFIELD 1]))',
            '$entry_lookup(S.ARRAYS[n_root].ITEMS, KINT 0) = (DIRECT (PARRAY n_inner))',
            '$heap_count(HARRAY n_inner, $tasks_nodes(S.TODO)) = 1',
            '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_inner) = 2',
        ]
    elif null:
        checks += ['porigin_root = porigin', 'n_source = n_root_cell']
    else:
        checks += [
            '$reference_origin_parent(porigin, 3) = ((porigin_parent, [PCFIELD 0, PCINDEX 1, PCFIELD 1]))',
            '$reference_origin_parent(porigin_parent, 3) = ((porigin_root, [PCFIELD 0, PCINDEX 1, PCFIELD 1]))',
            '$entry_lookup(S.ARRAYS[n_root].ITEMS, KINT 1) = (ALIAS n_parent_cell)',
            'S.STORE[n_parent_cell] = DEFINED (PARRAY n_parent)',
            '$entry_lookup(S.ARRAYS[n_parent].ITEMS, KINT 1) = (ALIAS n_source)',
            'S.STORE[n_source] = DEFINED (PARRAY n_inner)',
        ]
        for cell in ('n_parent_cell', 'n_source'):
            checks += [f'{cell} <- S.REFCELLS', f'$heap_count(HCELL {cell}, $tasks_nodes(S.TODO)) = 1',
                       f'$heap_owners($heap_prune($heap_graph(S)), HCELL {cell}) = 2']
    checks += [
        '$origin_node(S.SOURCES, porigin_root) = (expression_root)', '$list_pattern(expression_root) = (phpType13_root*)',
        '~$list_missing_flat(phpType13_root*)', '$list_references(phpType13_root*)',
        '~$list_missing_nested_items(phpType13_root*)', '$list_missing_nested_mixed_items(phpType13_root*)',
        '$list_missing_nested_mixed_items([NArrayItem ABSENT expression_root (BOOLEAN false) (BOOLEAN false) eps])',
        '$list_missing_nested_mixed_items([NArrayItem ABSENT expression (BOOLEAN true) (BOOLEAN false) eps])',
        '~$list_missing_nested_items([NArrayItem ABSENT expression (BOOLEAN true) (BOOLEAN false) eps])',
        '~$list_missing_nested_mixed_items([NArrayItem ABSENT expression_root (BOOLEAN true) (BOOLEAN false) eps])',
        '~$list_missing_nested_mixed_items([NArrayItem ABSENT expression (BOOLEAN false) (BOOLEAN true) eps])',
        '$reference_origin_parent(porigin_root, 1) = ((porigin_assign, [PCFIELD 0]))',
        '$origin_node(S.SOURCES, porigin_assign) = (NExprAssign expression_root expression_rhs metadata_assign)',
        '$list_value_cv(expression_rhs) = ($ptascii("a"))',
        'porigin_assign = PORIGIN n_unit pcpath_assign', 'S.SOURCES[n_unit] = pcunit',
        'S_literal = S[.SOURCES[n_unit] = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_assign (NExprAssign expression_root (NExprArray (SEQUENCE eps) eps) metadata_assign)) :: pcunit.OCCURRENCES]]',
        '$list_missing_nested_context(S_literal, porigin) = eps', '~$list_missing_source(S_literal, ' + args + ')',
        '$list_missing_nested_context(S, porigin) = (z)',
        '$origin_node(S.SOURCES, porigin) = (expression_pattern)', '$list_pattern(expression_pattern) = (phpType13_all*)',
        ('~' if known else '') + '$list_references(phpType13_all*)',
        '$list_missing_source(S, ' + args + ')',
        '~$list_missing_source(S, ' + operand + ', 0, expression, phpType13*, $(z + 1), KINT 0)',
        '~$list_missing_source(S, ' + operand + ', 0, expression, eps, z, KINT 0)',
        '~$list_missing_source(S, ' + operand + ', 0, expression, phpType13*, z, KINT 9)',
        '~$list_missing_source(S[.CODE = eps], ' + args + ')', '~$list_missing_source(S[.ALLOCATIONS = eps], ' + args + ')',
        '$list_missing_array(S, ' + operand + ') = (n_current_array)',
        '$lookup(S.ENV, $ptascii("x")) = (n_x)', 'S.STORE[n_x] = DEFINED (PINT 7)',
        '$lookup(S.ENV, $ptascii("y")) = (n_y)', 'S.STORE[n_y] = DEFINED (PINT 8)',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
    ]
    if known:
        checks += ['~$list_missing_source(S, REFERENCE n_root_cell, 0, expression, phpType13*, z, KINT 0)']
    else:
        checks += ['~$list_missing_source(S, KNOWN (PARRAY n_current_array), 0, expression, phpType13*, z, KINT 0)',
                   '~$list_missing_source(S[.REFCELLS = eps], ' + args + ')']
    if not null:
        checks += ['$lookup(S.ENV, $ptascii("q")) = (n_q)', 'S.STORE[n_q] = DEFINED (PINT 2)',
                   '$entry_lookup(S.ARRAYS[n_inner].ITEMS, KINT 1) = (ALIAS n_q)',
                   '$heap_owners($heap_prune($heap_graph(S)), HCELL n_q) = 2']
    checks += [
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_dispatch', 'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        'S_entered_found = $list_warning_seek(S_dispatch, 3, 2000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', 'S_entered.CURRENT =/= eps', 'S_entered.FRAMES = pframe :: eps',
        '$heap_count(HCELL n_root_cell, $tasks_nodes(pframe.TODO)) = 1',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if known:
        checks += ['$heap_count(HARRAY n_inner, $tasks_nodes(pframe.TODO)) = 1']
    elif thrown:
        checks += [f'$heap_count(HCELL {cell}, $tasks_nodes(pframe.TODO)) = 1' for cell in ('n_parent_cell', 'n_source')]
    if thrown:
        checks += [
            '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)', 'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            'S_discard_found = $list_warning_seek(S_entered, 5, 2000)',
            r'S_discard_found.COMPLETION = NORMAL \/ S_discard_found.COMPLETION = BUDGET', 'S_discard = S_discard_found[.COMPLETION = NORMAL]',
            '$lookup(S_discard.ENV, $ptascii("a")) = eps', '$lookup(S_discard.ENV, $ptascii("q")) = eps',
        ]
        for cell, owners, tasks in [('n_root_cell', 1, 1), ('n_parent_cell', 2, 1), ('n_source', 1, 0), ('n_q', 1, 0)]:
            checks += [f'$heap_owners($heap_prune($heap_graph(S_discard)), HCELL {cell}) = {owners}',
                       f'$heap_count(HCELL {cell}, $tasks_nodes(S_discard.TODO)) = {tasks}']
        checks += [f'$heap_owners($heap_prune($heap_graph(S_discard)), HARRAY {array}) = 1' for array in ('n_root', 'n_parent', 'n_inner')]
        checks += [
            '$heap_valid($heap_graph(S_discard))', 'S_pending_found = $list_warning_seek(S_discard, 8, 2000)',
            r'S_pending_found.COMPLETION = NORMAL \/ S_pending_found.COMPLETION = BUDGET', 'S_pending = S_pending_found[.COMPLETION = NORMAL]',
            'S_pending.TODO = (THROW_SEARCH n_second) :: (TRY_END porigin_try) :: ptask_pending*',
            'S_pending.ERRORHANDLER = S.ERRORHANDLER', '$throwable_previous_id(S_pending, n_second) = eps',
        ]
        checks += [f'~((HCELL {cell}) <- S_pending.ALLOCATIONS)' for cell in ('n_root_cell', 'n_parent_cell', 'n_source', 'n_q')]
        checks += [f'~((HARRAY {array}) <- S_pending.ALLOCATIONS)' for array in ('n_root', 'n_parent', 'n_inner')]
        checks += ['$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
                   'S_done = $drive_steps(S_pending, 2000)', 'S_done.STORE[n_x] = DEFINED (PINT 99)',
                   'S_done.STORE[n_y] = DEFINED (PINT 8)', 'S_done.STORE[n_dest] = DEFINED (PINT 100)']
        for var, value in [('outerbefore', 9), ('before', 5), ('near', 50), ('tail', 70)]:
            checks += [f'$lookup(S_done.ENV, $ptascii("{var}")) = (n_{var})', f'S_done.STORE[n_{var}] = DEFINED (PINT {value})']
    else:
        checks += [
            'S_return_found = $list_warning_seek(S_entered, 2, 2000)',
            r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
            'S_return = S_return_found[.COMPLETION = NORMAL]', 'S_return.TODO = (' + marker + ') :: ptask_tail*',
            '$list_missing_source(S_return, ' + args + ')', 'S_return.ERRORHANDLER = S.ERRORHANDLER',
            'S_return.STORE[n_x] = DEFINED (PINT 99)', 'PhpStep: S_return ~> S_store',
            'S_store.TODO = $list_fetched_tasks(S_return[.RESULT = KNOWN PNULL], ' + operand + ', 0, expression, false, phpType13*, z) ++ ptask_tail*',
            'S_store.STORE = S_return.STORE', 'S_store.ARRAYS = S_return.ARRAYS',
        ]
        if known:
            checks += [
                'S_return.STORE[n_root_cell] = DEFINED (PARRAY n_replaced)', 'n_replaced =/= n_root',
                '~((HARRAY n_root) <- S_return.ALLOCATIONS)',
                '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_inner) = 1',
                'S_return.STORE[n_q] = DEFINED (PINT 33)',
                'S_next_found = $list_warning_seek(S_store, 4, 2000)',
                r'S_next_found.COMPLETION = NORMAL \/ S_next_found.COMPLETION = BUDGET', 'S_next = S_next_found[.COMPLETION = NORMAL]',
                'S_next.TODO = (LIST_FETCH (KNOWN (PARRAY n_inner)) 1 expression_y false eps z_y) :: ptask_y*',
                'S_next.STORE[n_x] = DEFINED PNULL', 'S_next.STORE[n_y] = DEFINED (PINT 8)', 'PhpStep: S_next ~> S_read',
                'S_read.TODO = (AT porigin_y (LIST_STORE expression_y (KNOWN (PINT 33)) false z_store_y)) :: (LIST_NEXT (KNOWN (PARRAY n_inner)) 2 eps z_follow_y) :: ptask_y*',
                'S_ref_found = $list_warning_seek(S_read, 6, 2000)',
                r'S_ref_found.COMPLETION = NORMAL \/ S_ref_found.COMPLETION = BUDGET', 'S_ref = S_ref_found[.COMPLETION = NORMAL]',
                'S_ref.TODO = (LIST_FETCH (REFERENCE n_root_cell) 1 expression_tail true eps z_tail) :: ptask_ref*',
                'S_ref.STORE[n_y] = DEFINED (PINT 33)', '~((HARRAY n_inner) <- S_ref.ALLOCATIONS)',
                '$heap_owners($heap_prune($heap_graph(S_ref)), HCELL n_q) = 1', 'PhpStep: S_ref ~> S_acquired',
                'S_acquired.STORE[n_root_cell] = DEFINED (PARRAY n_after)', 'n_after =/= n_replaced',
                '$entry_lookup(S_acquired.ARRAYS[n_after].ITEMS, KINT 1) = (ALIAS n_tail_ref)',
                'S_acquired.STORE[n_tail_ref] = DEFINED (PINT 40)', 'n_tail_ref <- S_acquired.REFCELLS',
                'S_done = $drive_steps(S_acquired, 2000)', 'S_done.STORE[n_y] = DEFINED (PINT 55)',
                '~((HARRAY n_inner) <- S_done.ALLOCATIONS)', '~((HARRAY n_after) <- S_done.ALLOCATIONS)',
                '~((HCELL n_q) <- S_done.ALLOCATIONS)', '~((HCELL n_tail_ref) <- S_done.ALLOCATIONS)',
            ]
        else:
            checks += [
                'S_return.STORE[n_root_cell] = DEFINED PNULL', '$list_missing_array(S_return, REFERENCE n_source) = eps',
                '$lookup(S.ENV, $ptascii("z")) = (n_z)', 'S_return.STORE[n_y] = DEFINED (PINT 88)', 'S_return.STORE[n_z] = DEFINED (PINT 77)',
                'S_ref_found = $list_warning_seek(S_store, 6, 2000)',
                r'S_ref_found.COMPLETION = NORMAL \/ S_ref_found.COMPLETION = BUDGET', 'S_ref = S_ref_found[.COMPLETION = NORMAL]',
                'S_ref.TODO = (LIST_FETCH (REFERENCE n_root_cell) 1 expression_child true eps z_child) :: ptask_ref*',
                'S_ref.STORE[n_x] = DEFINED PNULL', 'S_ref.STORE[n_root_cell] = DEFINED PNULL', 'PhpStep: S_ref ~> S_acquired',
                'S_acquired.STORE[n_root_cell] = DEFINED (PARRAY n_created_root)', 'n_created_root =/= n_root',
                '$entry_lookup(S_acquired.ARRAYS[n_created_root].ITEMS, KINT 1) = (ALIAS n_child)',
                'S_acquired.STORE[n_child] = DEFINED PNULL', 'n_child <- S_acquired.REFCELLS',
                'S_acquired.TODO = (AT porigin_child (LIST_PATTERN expression_child (REFERENCE n_child) z_child)) :: (LIST_NEXT (REFERENCE n_root_cell) 2 eps z_follow) :: ptask_ref*',
                'S_null_found = $list_warning_seek(S_acquired, 7, 2000)',
                r'S_null_found.COMPLETION = NORMAL \/ S_null_found.COMPLETION = BUDGET', 'S_null = S_null_found[.COMPLETION = NORMAL]',
                'S_null.TODO = (LIST_FETCH (REFERENCE n_child) 0 expression_y false phpType13_y* z_y) :: ptask_y*',
                'S_null.STORE[n_child] = DEFINED PNULL', '$list_missing_plan(S_null) = eps', 'PhpStep: S_null ~> S_yread',
                'S_yread.STORE = S_null.STORE', 'S_yread.ARRAYS = S_null.ARRAYS', 'S_yread.EVENTS = S_null.EVENTS',
                'S_z_found = $list_warning_seek(S_yread, 6, 2000)',
                r'S_z_found.COMPLETION = NORMAL \/ S_z_found.COMPLETION = BUDGET', 'S_z = S_z_found[.COMPLETION = NORMAL]',
                'S_z.TODO = (LIST_FETCH (REFERENCE n_child) 1 expression_z true eps z_z) :: ptask_z*',
                'S_z.STORE[n_y] = DEFINED PNULL', 'S_z.STORE[n_z] = DEFINED (PINT 77)', 'PhpStep: S_z ~> S_zacquired',
                'S_zacquired.STORE[n_child] = DEFINED (PARRAY n_created_child)',
                '$entry_lookup(S_zacquired.ARRAYS[n_created_child].ITEMS, KINT 1) = (ALIAS n_slot)',
                'S_zacquired.STORE[n_slot] = DEFINED PNULL', 'n_slot <- S_zacquired.REFCELLS',
                'S_done = $drive_steps(S_zacquired, 2000)', 'S_done.STORE[n_y] = DEFINED PNULL',
            ]
            checks += [f'~((HCELL {cell}) <- S_done.ALLOCATIONS)' for cell in ('n_child', 'n_slot')]
            checks += [f'~((HARRAY {array}) <- S_done.ALLOCATIONS)' for array in ('n_created_root', 'n_created_child')]
            checks += ['$lookup(S_done.ENV, $ptascii("calls")) = (n_calls)', 'S_done.STORE[n_calls] = DEFINED (PINT 1)']
        checks += ['S_done.STORE[n_x] = DEFINED PNULL', '~((HCELL n_root_cell) <- S_done.ALLOCATIONS)',
                   '$lookup(S_done.ENV, $ptascii("a")) = eps', '$lookup(S_done.ENV, $ptascii("dest")) = eps']
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
