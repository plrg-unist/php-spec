#!/usr/bin/env python3
"""Reached recursive source contexts and every captured-array continuation."""
import base64
import hashlib
import json
from pathlib import Path

import list_recursive_missing_warning_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 6) = true
  -- if S.TODO = (THROW_SEARCH n) :: (TRY_END porigin) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
'''


def conditions(name, program, path, stdout):
    keyed = name.endswith('depth4-keyed')
    thrown = name.endswith('depth4-throw')
    chain = ['root', 'upper', 'parent', 'inner'] if keyed or thrown else ['root', 'parent', 'inner']
    origins = ['porigin_' + node if node != 'inner' else 'porigin' for node in chain]
    branch = 1 if thrown else 0
    index, key, line = (1, 3, 15) if keyed else (0, 0, 16 if thrown else 12)
    x, y = (8, 9) if keyed else (7, 8)
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
        '$lookup(S.ENV, $ptascii("a")) = (n_a)', 'S.STORE[n_a] = DEFINED (PARRAY n_root)',
    ]
    for parent, child in zip(reversed(origins[:-1]), reversed(origins[1:])):
        checks += [f'$reference_origin_parent({child}, 3) = (({parent}, [PCFIELD 0, PCINDEX {branch}, PCFIELD 1]))',
                   f'$list_missing_nested_context(S, {parent}) = (z_{parent})']
    checks += [
        '$origin_node(S.SOURCES, porigin_root) = (expression_root)', '$list_pattern(expression_root) = (phpType13_root*)',
        '~$list_missing_flat(phpType13_root*)', '$list_missing_nested_items(phpType13_root*)',
        '$list_missing_nested_items([NArrayItem ABSENT expression_root (BOOLEAN false) (BOOLEAN false) eps])',
        '~$list_missing_nested_items([NArrayItem ABSENT expression (BOOLEAN true) (BOOLEAN false) eps])',
        '~$list_missing_nested_items([NArrayItem ABSENT expression (BOOLEAN false) (BOOLEAN true) eps])',
        '$list_missing_nested_context(S, porigin) = (z_initial)',
        '$reference_origin_parent(porigin_root, 1) = ((porigin_assign, [PCFIELD 0]))',
        '$origin_node(S.SOURCES, porigin_assign) = (NExprAssign expression_root expression_rhs metadata_assign)',
        'porigin_assign = PORIGIN n_unit pcpath_assign', 'S.SOURCES[n_unit] = pcunit',
        'S_wide = S[.SOURCES[n_unit] = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_assign (NExprAssign expression_root (NScalarInt (INTEGER 1) eps) metadata_assign)) :: pcunit.OCCURRENCES]]',
        '$list_missing_nested_context(S_wide, porigin) = eps', '~$list_missing_source(S_wide, ' + args + ')',
        '$lookup(S.ENV, $ptascii("x")) = (n_x)', f'S.STORE[n_x] = DEFINED (PINT {x})',
        '$lookup(S.ENV, $ptascii("y")) = (n_y)', f'S.STORE[n_y] = DEFINED (PINT {y})',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        '$list_missing_source(S, ' + args + ')',
        f'~$list_missing_source(S, KNOWN (PARRAY n_inner), {index}, expression, phpType13*, $(z + 1), KINT {key})',
        f'~$list_missing_source(S, KNOWN (PARRAY n_inner), {index}, expression, eps, z, KINT {key})',
        f'~$list_missing_source(S, REFERENCE n_a, {index}, expression, phpType13*, z, KINT {key})',
        '~$list_missing_source(S[.CODE = eps], ' + args + ')', '~$list_missing_source(S[.ALLOCATIONS = eps], ' + args + ')',
    ]
    for parent, child in zip(chain[:-1], chain[1:]):
        checks += [f'$entry_lookup(S.ARRAYS[n_{parent}].ITEMS, KINT {branch}) = (DIRECT (PARRAY n_{child}))', f'n_{parent} =/= n_{child}']
    for node in chain:
        checks += [f'n_pool_{node} = $heap_count(HARRAY n_{node}, $pools_nodes(S.POOLS))',
                   f'$heap_owners($heap_prune($heap_graph(S)), HARRAY n_{node}) = $(2 + n_pool_{node})',
                   f'$heap_count(HARRAY n_{node}, $tasks_nodes(S.TODO)) = 1']
    checks += [
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_dispatch', 'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker, '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        'S_entered_found = $list_warning_seek(S_dispatch, 3, 2000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', 'S_entered.CURRENT =/= eps', 'S_entered.FRAMES = pframe :: eps',
    ]
    for node in chain:
        checks += [f'$heap_count(HARRAY n_{node}, $tasks_nodes(pframe.TODO)) = 1']
    checks += ['$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))']
    if not keyed:
        checks += ['$lookup(S.ENV, $ptascii("q")) = (n_q)', '$entry_lookup(S.ARRAYS[n_inner].ITEMS, KINT 1) = (ALIAS n_q)',
                   '$heap_owners($heap_prune($heap_graph(S)), HCELL n_q) = 2']
        checks += [f'n_pool_{node} = 0' for node in chain]
    if keyed or thrown:
        checks += ['$lookup(S.ENV, $ptascii("before")) = (n_before)', 'S.STORE[n_before] = DEFINED (PINT 5)']
    if thrown:
        checks += [
            '$lookup(S.ENV, $ptascii("outerbefore")) = (n_outerbefore)', 'S.STORE[n_outerbefore] = DEFINED (PINT 9)',
            '$lookup(S.ENV, $ptascii("midbefore")) = (n_midbefore)', 'S.STORE[n_midbefore] = DEFINED (PINT 7)',
            '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)', 'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            'S_discard_found = $list_warning_seek(S_entered, 5, 2000)',
            r'S_discard_found.COMPLETION = NORMAL \/ S_discard_found.COMPLETION = BUDGET', 'S_discard = S_discard_found[.COMPLETION = NORMAL]',
        ]
        for node in chain:
            checks += [f'$heap_count(HARRAY n_{node}, $tasks_nodes(S_discard.TODO)) = {0 if node == "inner" else 1}',
                       f'$heap_owners($heap_prune($heap_graph(S_discard)), HARRAY n_{node}) = {1 if node in ("root", "inner") else 2}']
        checks += [
            '$heap_owners($heap_prune($heap_graph(S_discard)), HCELL n_q) = 1', '$heap_valid($heap_graph(S_discard))',
            'S_pending_found = $list_warning_seek(S_discard, 6, 2000)',
            r'S_pending_found.COMPLETION = NORMAL \/ S_pending_found.COMPLETION = BUDGET',
            'S_pending = S_pending_found[.COMPLETION = NORMAL]', 'S_pending.TODO = (THROW_SEARCH n_second) :: ptask_pending*',
            'S_pending.ERRORHANDLER = S.ERRORHANDLER', '$throwable_previous_id(S_pending, n_second) = eps',
        ]
        checks += [f'~((HARRAY n_{node}) <- S_pending.ALLOCATIONS)' for node in chain]
        checks += ['~((HCELL n_q) <- S_pending.ALLOCATIONS)', '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
                   'S_done = $drive_steps(S_pending, 2000)', 'S_done.STORE[n_x] = DEFINED (PINT 99)', 'S_done.STORE[n_y] = DEFINED (PINT 8)',
                   'S_done.STORE[n_outerbefore] = DEFINED (PINT 9)', 'S_done.STORE[n_midbefore] = DEFINED (PINT 7)',
                   'S_done.STORE[n_before] = DEFINED (PINT 5)', 'S_done.STORE[n_dest] = DEFINED (PINT 100)']
    else:
        checks += [
            'S_return_found = $list_warning_seek(S_entered, 2, 2000)',
            r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
            'S_return = S_return_found[.COMPLETION = NORMAL]', 'S_return.TODO = (' + marker + ') :: ptask_tail*',
            '$list_missing_source(S_return, ' + args + ')', 'S_return.ERRORHANDLER = S.ERRORHANDLER',
            'S_return.STORE[n_a] = DEFINED (PARRAY n_rebound)', 'n_rebound =/= n_root', 'S_return.STORE[n_x] = DEFINED (PINT 99)',
        ]
        for node in chain:
            checks += [f'$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_{node}) = $({1 if node == "root" else 2} + n_pool_{node})']
        checks += [
            'PhpStep: S_return ~> S_store',
            f'S_store.TODO = $list_fetched_tasks(S_return[.RESULT = KNOWN PNULL], KNOWN (PARRAY n_inner), {index}, expression, false, phpType13*, z) ++ ptask_tail*',
            'S_store.STORE = S_return.STORE', 'S_store.ARRAYS = S_return.ARRAYS',
            'S_next_found = $list_warning_seek(S_store, 4, 2000)',
            r'S_next_found.COMPLETION = NORMAL \/ S_next_found.COMPLETION = BUDGET', 'S_next = S_next_found[.COMPLETION = NORMAL]',
            f'S_next.TODO = (LIST_FETCH (KNOWN (PARRAY n_inner)) {index + 1} expression_next false eps z_next) :: ptask_next*',
            'S_next.STORE[n_x] = DEFINED PNULL', f'S_next.STORE[n_y] = DEFINED (PINT {y})', 'PhpStep: S_next ~> S_read',
            f'S_read.TODO = (AT porigin_y (LIST_STORE expression_next (KNOWN (PINT {fetched})) false z_y)) :: (LIST_NEXT (KNOWN (PARRAY n_inner)) {index + 2} eps z_follow) :: ptask_next*',
            'S_read.STORE = S_next.STORE', 'S_read.ARRAYS = S_next.ARRAYS', 'S_done = $drive_steps(S_read, 2000)',
            'S_done.STORE[n_x] = DEFINED PNULL', f'S_done.STORE[n_y] = DEFINED (PINT {fetched})',
            '$lookup(S_done.ENV, $ptascii("near")) = (n_near)', f'S_done.STORE[n_near] = DEFINED (PINT {7 if keyed else 3})',
            '$lookup(S_done.ENV, $ptascii("tail")) = (n_tail)', f'S_done.STORE[n_tail] = DEFINED (PINT {9 if keyed else 4})',
        ]
        if keyed:
            checks += ['S_done.STORE[n_before] = DEFINED (PINT 21)', 'S_done.STORE[n_dest] = DEFINED (PARRAY n_root)',
                       '$lookup(S_done.ENV, $ptascii("middle")) = (n_middle)', 'S_done.STORE[n_middle] = DEFINED (PINT 8)']
            checks += [f'$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_{node}) = $(1 + n_pool_{node})' for node in chain]
        else:
            checks += [f'~((HARRAY n_{node}) <- S_done.ALLOCATIONS)' for node in chain] + ['~((HCELL n_q) <- S_done.ALLOCATIONS)']
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
