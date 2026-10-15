#!/usr/bin/env python3
"""Reached mixed-list source-cell replacement, reference acquisition and cleanup."""
import base64
import hashlib
import json
from pathlib import Path

import list_reference_missing_warning_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 6) = true
  -- if S.TODO = (LIST_FETCH (REFERENCE n_source) n expression true phpType13* z) :: ptask_tail*
'''


def conditions(name, program, path, stdout):
    null = name.endswith('replace-null')
    thrown = name.endswith('throw-retire')
    args = 'REFERENCE n_source, 0, expression, phpType13*, z, KINT 0'
    marker = 'LIST_MISSING_RESULT (REFERENCE n_source) 0 expression phpType13* z (KINT 0)'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $list_warning_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]',
        '$list_missing_plan(S) = ((REFERENCE n_source, 0, expression, phpType13*, z, KINT 0))',
        'S.TODO = (LIST_FETCH (REFERENCE n_source) 0 expression false phpType13* z) :: ptask_tail*',
        'S.ORIGIN = (porigin)', '$lookup(S.ENV, $ptascii("a")) = (n_source)',
        'S.STORE[n_source] = DEFINED (PARRAY n_before)', 'n_source <- S.REFCELLS',
        '$lookup(S.ENV, $ptascii("x")) = (n_x)', 'S.STORE[n_x] = DEFINED (PINT 7)',
        '$lookup(S.ENV, $ptascii("y")) = (n_y)', 'S.STORE[n_y] = DEFINED (PINT 8)',
        '$lookup(S.ENV, $ptascii("dest")) = (n_dest)', 'S.STORE[n_dest] = DEFINED (PINT 100)',
        '$list_missing_array(S, REFERENCE n_source) = (n_before)',
        '$list_missing_array(S, REFERENCE (|S.STORE|)) = eps',
        '$entry_lookup(S.ARRAYS[n_before].ITEMS, KINT 0) = eps',
        '$list_missing_source(S, ' + args + ')',
        '~$list_missing_source(S, REFERENCE n_source, 0, expression, phpType13*, $(z + 1), KINT 0)',
        '~$list_missing_source(S, REFERENCE n_source, 1, expression, phpType13*, z, KINT 0)',
        '~$list_missing_source(S, REFERENCE n_source, 0, expression, eps, z, KINT 0)',
        '~$list_missing_source(S, REFERENCE n_source, 0, expression, phpType13*, z, KINT 9)',
        '~$list_missing_source(S, KNOWN (PARRAY n_before), 0, expression, phpType13*, z, KINT 0)',
        '~$list_missing_source(S[.ORIGIN = eps], ' + args + ')',
        '~$list_missing_source(S[.SOURCES = eps], ' + args + ')',
        '~$list_missing_source(S[.ALLOCATIONS = eps], ' + args + ')',
        '~$list_missing_source(S[.REFCELLS = eps], ' + args + ')',
        '~$list_missing_source(S, REFERENCE (|S.STORE|), 0, expression, phpType13*, z, KINT 0)',
        '$list_missing_plan(S[.RESULT = KNOWN (PINT 9)]) = eps',
        '$task_nodes(' + marker + ') = [HCELL n_source]',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_source) = 2',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker,
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(z + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 512])',
        '~$error_call_valid(S_dispatch, perrorcall[.SITE = PORIGIN 9 eps])',
        '$task_nodes(ERROR_HANDLER_INVOKE perrorcall) = [HCELL n_source]',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.ARRAYS = S.ARRAYS',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
    ]
    if not null:
        checks += [
            '$lookup(S.ENV, $ptascii("q")) = (n_q)', 'S.STORE[n_q] = DEFINED (PINT 2)',
            '$entry_lookup(S.ARRAYS[n_before].ITEMS, KINT 1) = (ALIAS n_q)',
            '$heap_count(HARRAY n_before, $pools_nodes(S.POOLS)) = 0',
            '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_before) = 1',
            '$heap_owners($heap_prune($heap_graph(S)), HCELL n_q) = 2',
        ]
    if thrown:
        checks += [
            '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)',
            'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            'S_pending_found = $list_warning_seek(S_dispatch, 5, 2000)',
            r'S_pending_found.COMPLETION = NORMAL \/ S_pending_found.COMPLETION = BUDGET',
            'S_pending = S_pending_found[.COMPLETION = NORMAL]', '$list_warning_frontier(S_pending, 5)',
            'S_pending.TODO = (THROW_SEARCH n_second) :: ptask_pending*',
            'S_pending.ERRORHANDLER = S.ERRORHANDLER',
            '$lookup(S_pending.ENV, $ptascii("a")) = eps', '$lookup(S_pending.ENV, $ptascii("q")) = eps',
            '~((HCELL n_source) <- S_pending.ALLOCATIONS)',
            '~((HARRAY n_before) <- S_pending.ALLOCATIONS)', '~((HCELL n_q) <- S_pending.ALLOCATIONS)',
            'S_pending.STORE[n_x] = DEFINED (PINT 99)', 'S_pending.STORE[n_y] = DEFINED (PINT 8)',
            'S_pending.STORE[n_dest] = DEFINED (PINT 100)',
            '$throwable_previous_id(S_pending, n_second) = eps',
            '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
            'S_done = $drive_steps(S_pending, 2000)',
            'S_done.STORE[n_x] = DEFINED (PINT 99)', 'S_done.STORE[n_y] = DEFINED (PINT 8)',
            'S_done.STORE[n_dest] = DEFINED (PINT 100)',
        ]
    else:
        checks += [
            'S_return_found = $list_warning_seek(S_dispatch, 2, 2000)',
            r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
            'S_return = S_return_found[.COMPLETION = NORMAL]',
            'S_return.TODO = (' + marker + ') :: ptask_tail*',
            'S_return.ERRORHANDLER = S.ERRORHANDLER', '$list_missing_source(S_return, ' + args + ')',
            'S_return.STORE[n_x] = DEFINED (PINT 99)', 'S_return.STORE[n_y] = DEFINED (PINT 8)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_source) = 2',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        ]
        if null:
            checks += ['S_return.STORE[n_source] = DEFINED PNULL', '$list_missing_array(S_return, REFERENCE n_source) = eps']
        else:
            checks += [
                'S_return.STORE[n_source] = DEFINED (PARRAY n_replacement)', 'n_replacement =/= n_before',
                '$entry_lookup(S_return.ARRAYS[n_replacement].ITEMS, KINT 0) = (DIRECT (PINT 11))',
                '$entry_lookup(S_return.ARRAYS[n_replacement].ITEMS, KINT 1) = (DIRECT (PINT 22))',
                '~((HARRAY n_before) <- S_return.ALLOCATIONS)', 'S_return.STORE[n_q] = DEFINED (PINT 33)',
                '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_q) = 1',
            ]
        checks += [
            'PhpStep: S_return ~> S_store',
            'S_store.TODO = $list_fetched_tasks(S_return[.RESULT = KNOWN PNULL], REFERENCE n_source, 0, expression, false, phpType13*, z) ++ ptask_tail*',
            'S_store.RESULT = KNOWN PNULL', 'S_store.STORE = S_return.STORE', 'S_store.ARRAYS = S_return.ARRAYS',
            '$call_descriptors_valid(S_store)', '$heap_valid($heap_graph(S_store))',
            'S_next_found = $list_warning_seek(S_store, 6, 2000)',
            r'S_next_found.COMPLETION = NORMAL \/ S_next_found.COMPLETION = BUDGET',
            'S_next = S_next_found[.COMPLETION = NORMAL]',
            'S_next.TODO = (LIST_FETCH (REFERENCE n_source) 1 expression_next true eps z_next) :: ptask_tail*',
            'S_next.STORE[n_x] = DEFINED PNULL', 'S_next.STORE[n_y] = DEFINED (PINT 8)',
            'PhpStep: S_next ~> S_bound',
            'S_bound.TODO = (AT porigin_y (LIST_STORE expression_next (REFERENCE n_leaf) true z_y)) :: (LIST_NEXT (REFERENCE n_source) 2 eps z_follow) :: ptask_tail*',
            'S_bound.STORE[n_source] = DEFINED (PARRAY n_after)',
            '$entry_lookup(S_bound.ARRAYS[n_after].ITEMS, KINT 1) = (ALIAS n_leaf)',
            'n_leaf <- S_bound.REFCELLS', 'S_bound.STORE[n_y] = DEFINED (PINT 8)',
            '$heap_owners($heap_prune($heap_graph(S_bound)), HCELL n_leaf) = 2',
            '$call_descriptors_valid(S_bound)', '$heap_valid($heap_graph(S_bound))',
            'S_done = $drive_steps(S_bound, 2000)', 'S_done.STORE[n_x] = DEFINED PNULL',
            '~((HCELL n_source) <- S_done.ALLOCATIONS)', '~((HARRAY n_after) <- S_done.ALLOCATIONS)',
            '~((HCELL n_leaf) <- S_done.ALLOCATIONS)',
        ]
        checks += ['S_bound.STORE[n_leaf] = DEFINED PNULL'] if null else ['S_bound.STORE[n_leaf] = DEFINED (PINT 22)', '~((HCELL n_q) <- S_done.ALLOCATIONS)']
    return checks + [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.HELD = eps', '~$list_warning_tasks(S_done.TODO)',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]', '$drive_steps(S, 2000) = S_done',
        '$drive_steps(S_dispatch, 2000) = S_done',
    ]


if __name__ == '__main__':
    own = Path(__file__)
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    passed = shared.run(cases, conditions, HELPERS)
    assert before == hashlib.sha256(own.read_bytes()).hexdigest()
    raise SystemExit(0 if passed else 1)
