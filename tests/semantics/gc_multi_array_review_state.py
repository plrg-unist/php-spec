#!/usr/bin/env python3
"""Independent reached GC graph, weak-owner and pooled-ancestor controls."""
import argparse

import gc_caller_materialized_state as ordinary
import gc_multi_array_sources as sources
import shutdown_state_review as runner


CAPTURES = '[DIRECT (PARRAY n_array), DIRECT (POBJECT n_leaf), DIRECT (PARRAY n_second), DIRECT (POBJECT n_other)]'
ONE_CAPTURES = '[DIRECT (PARRAY n_array), DIRECT (POBJECT n_other), DIRECT (PINT 11), DIRECT PNULL]'
CHECKS = [
    'S.CURRENT = (pcallcontext)',
    'pgccall.CALLER = (pcallcontext)',
    'pcallcontext.TARGET = CLOSURE_TARGET n_closure',
    'pcallcontext.INSTANCE = (n_closure)',
    f'S.OBJECTS[n_closure] = REALCLOSURE porigin_template ({CAPTURES}) eps',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV, $ptascii("collector")) = (n_collector)',
    'S.STORE[n_collector] = DEFINED (POBJECT n_closure)',
    '$lookup(psymboltable_global.ENV, $ptascii("weakLeaf")) = (n_weak_cell)',
    'S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
    'S.OBJECTS[n_weak] = WEAKREFERENCE (n_leaf)',
    'H = $heap_graph(S)',
    '$heap_valid(H)',
    '$node_children(S, HOBJECT n_weak) = eps',
    '$heap_edge_owners(HOBJECT n_leaf, H.EDGES, [HOBJECT n_weak]) = 0',
    '$heap_edge_owners(HOBJECT n_leaf, H.EDGES, [HARRAY n_array]) = 2',
    '$heap_edge_owners(HOBJECT n_leaf, H.EDGES, [HARRAY n_second]) = 1',
    '$heap_edge_owners(HOBJECT n_leaf, H.EDGES, [HOBJECT n_closure]) = 1',
    '$heap_owners(H, HOBJECT n_leaf) = 5',
    '$heap_owners(H, HOBJECT n_other) = 3',
    '$heap_owners(H, HARRAY n_array) = 2',
    '$heap_owners(H, HARRAY n_second) = 2',
    '$heap_owners(H, HOBJECT n_closure) = 2',
    f'$gc_capture_array_nodes({CAPTURES}) = [HARRAY n_array, HARRAY n_second]',
    f'$gc_plain_captures(S, {CAPTURES})',
    '$gc_ordinary_node(S, HOBJECT n_closure)',
    '$gc_materialized_callback_context(S)',
    '$gc_slot_find(S.GC.BUFFER, HARRAY n_array, 0) = (n_array_slot)',
    '$gc_slot_find(S.GC.BUFFER, HARRAY n_second, 0) = (n_second_slot)',
    '$gc_slot_find(S.GC.BUFFER, HOBJECT n_leaf, 0) = (n_leaf_slot)',
    '$(n_array_slot < n_second_slot)',
    '$(n_second_slot < n_leaf_slot)',
    '$heap_count(HARRAY n_array, $gc_nodes(S.GC.BUFFER)) = 1',
    '$heap_count(HARRAY n_second, $gc_nodes(S.GC.BUFFER)) = 1',
    '$heap_count(HOBJECT n_leaf, $gc_nodes(S.GC.BUFFER)) = 1',
    'pgcplan = $gc_plan(S, pgccall)',
    '$gc_slot_find(pgcplan.BUFFER, HARRAY n_array, 0) = eps',
    '$gc_slot_find(pgcplan.BUFFER, HARRAY n_second, 0) = eps',
    '$gc_slot_find(pgcplan.BUFFER, HOBJECT n_leaf, 0) = eps',
    'S_unrooted = S[.CURRENT = (pcallcontext[.INSTANCE = eps])]',
    '~((HOBJECT n_closure) <- $machine_roots(S_unrooted))',
    '~$gc_ordinary_node(S_unrooted, HOBJECT n_closure)',
    '~$gc_ordinary_node(S[.SOURCES = eps], HOBJECT n_closure)',
    f'S_one = S[.OBJECTS[n_closure] = REALCLOSURE porigin_template ({ONE_CAPTURES}) eps]',
    f'$gc_plain_captures(S_one, {ONE_CAPTURES})',
    '$closure_callable(S_one, n_closure)',
    '$gc_materialized_caller_target(S_one, CLOSURE_TARGET n_closure, pcallcontext.CALLSITE)',
    f'$gc_capture_array_nodes({ONE_CAPTURES}) = [HARRAY n_array]',
    '~((HOBJECT n_other) <- $node_children(S_one, HARRAY n_array))',
    '~$gc_ordinary_node(S_one, HOBJECT n_closure)',
    '~$gc_plain_captures(S, [DIRECT (PARRAY n_array), DIRECT (PARRAY n_second), UNINITIALIZED])',
    '~$gc_plain_captures(S, [DIRECT (PARRAY n_array), UNINITIALIZED, DIRECT (PARRAY n_second)])',
    'n_pool = |S.ARRAYS|',
    'parray_pool = $array_empty()',
    'S.POOLS = ppool :: ppool_tail*',
    'S_pool = S[.ARRAYS = S.ARRAYS ++ [parray_pool[.ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_second))]][.NEXT = 1]]][.ALLOCATIONS = S.ALLOCATIONS ++ [HARRAY n_pool]][.POOLS = ppool[.CONSTANTS = [PCONSTANT ([PCINDEX 0]) (PARRAY n_pool)]] :: ppool_tail*]',
    '$gc_plain_array_entries(S_pool, S_pool.ARRAYS[n_array].ITEMS)',
    '$gc_plain_array_entries(S_pool, S_pool.ARRAYS[n_second].ITEMS)',
    '~$gc_immutable_array(S_pool, n_second)',
    '~$gc_proxy(S_pool, n_second)',
    '~((HARRAY n_array) <- $heap_reach($pools_nodes(S_pool.POOLS), eps, $heap_graph(S_pool).EDGES))',
    '(HARRAY n_second) <- $heap_reach($pools_nodes(S_pool.POOLS), eps, $heap_graph(S_pool).EDGES)',
    f'~$gc_plain_captures(S_pool, {CAPTURES})',
    '~$gc_ordinary_node(S_pool, HOBJECT n_closure)',
    'n_retired = |S.OBJECTS|',
    'S_retired = S[.OBJECTS = S.OBJECTS ++ [STDINSTANCE]][.OBJECTTABLES = S.OBJECTTABLES ++ [{OBJECT n_retired, TABLE n_second}]]',
    '~((HOBJECT n_retired) <- S_retired.ALLOCATIONS)',
    '~$gc_proxy(S_retired, n_second)',
    f'$gc_plain_captures(S_retired, {CAPTURES})',
    '$gc_ordinary_node(S_retired, HOBJECT n_closure)',
]
CASES = {'independent-shared-D': {
    'source': sources.PATHS['distinct-shared'].read_text(),
    'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* -- if pgccall.PASS = 0 -- if S.GC.NEXT = 2',
    'checks': CHECKS,
    'timeout': 240,
}}


RECORDED = ordinary.RECORDED


def strict_recorded(command, directory, stem, environment, cap):
    return RECORDED([command[0], '--sl', *command[1:]], directory, stem, environment, cap)


runner.CASES = CASES
runner.recorded = strict_recorded
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if runner.run(args.case) else 1)
