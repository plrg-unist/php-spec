#!/usr/bin/env python3
"""Reached duplicate direct array edges under the sole rooted Closure owner."""
import argparse

import gc_caller_materialized_state as ordinary
import gc_duplicate_edge_sources as sources
import shutdown_state_review as runner


CASES = {
    'duplicate-retained-only': {
        'source': sources.PATHS['duplicate-retained-only'].read_text(),
        'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* '
                 '-- if pgccall.PASS = 0 -- if S.GC.NEXT = 2',
        'checks': [
            *ordinary.COMMON,
            'pcallcontext.TARGET = CLOSURE_TARGET n_closure',
            'pcallcontext.INSTANCE = (n_closure)',
            'pcallcontext.RECEIVER = eps',
            'pcallcontext.WRAPPER = eps',
            'S.OBJECTS[n_closure] = REALCLOSURE porigin_template ([DIRECT (PARRAY n_array)]) eps',
            '(HOBJECT n_closure) <- S.ALLOCATIONS',
            '(HARRAY n_array) <- S.ALLOCATIONS',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_leaf)), ENTRY (KINT 1) (DIRECT (POBJECT n_leaf))]',
            '(HOBJECT n_leaf) <- S.ALLOCATIONS',
            'S.OBJECTS[n_leaf] = STDINSTANCE',
            '~$gc_immutable_array(S, n_array)',
            '~$gc_proxy(S, n_array)',
            '~((HARRAY n_array) <- $heap_reach($pools_nodes(S.POOLS), eps, $heap_graph(S).EDGES))',
            '$gc_possible_root(S, HARRAY n_array)',
            '$target_function(S, CLOSURE_TARGET n_closure) = (pfunction_closure)',
            '$function_at(S.CLOSURETEMPLATES, porigin_template) = (pfunction_closure)',
            '$node_children(S, HOBJECT n_closure) = [HARRAY n_array]',
            '$node_children(S, HARRAY n_array) = [HOBJECT n_leaf, HOBJECT n_leaf]',
            '$gc_trace_children(S, HARRAY n_array) = [HOBJECT n_leaf, HOBJECT n_leaf]',
            '~$heap_unique($node_children(S, HARRAY n_array))',
            '$node_children(S, HOBJECT n_leaf) = eps',
            '$gc_trace_children(S, HOBJECT n_leaf) = eps',
            '$gc_plain_array_entries(S, S.ARRAYS[n_array].ITEMS)',
            '~$gc_legacy_array_shape(S, [DIRECT (PARRAY n_array)], n_array)',
            '(HARRAY n_array) <- $gc_nodes(S.GC.BUFFER)',
            '$gc_slot_find(S.GC.BUFFER, HARRAY n_array, 0) = (n_array_slot)',
            '(HOBJECT n_leaf) <- $gc_nodes(S.GC.BUFFER)',
            '$gc_slot_find(S.GC.BUFFER, HOBJECT n_leaf, 0) = (n_leaf_slot)',
            '$(n_array_slot < n_leaf_slot)',
            '$gc_slot_find(S.GC.BUFFER, HOBJECT n_leaf, $(n_leaf_slot + 1)) = eps',
            '$gc_buffer_valid(S, S.GC)',
            '$gc_slot_find(pgcplan.BUFFER, HARRAY n_array, 0) = eps',
            '$gc_slot_find(pgcplan.BUFFER, HOBJECT n_leaf, 0) = eps',
            '$gc_ordinary_node(S, HOBJECT n_closure)',
            '$gc_ordinary_nodes(S, S.ALLOCATIONS)',
            '~$gc_ordinary_node(S[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_leaf)), ENTRY (KINT 1) (DIRECT (PARRAY n_array))]], HOBJECT n_closure)',
            '~$gc_ordinary_node(S[.OBJECTS[n_closure] = REALCLOSURE porigin_template ([DIRECT (PARRAY n_array), DIRECT (POBJECT n_leaf)]) eps], HOBJECT n_closure)',
            '~$gc_ordinary_node(S[.GC.ACTIVE = eps], HOBJECT n_closure)',
            '~$gc_ordinary_node(S[.GC.ACTIVE = (pgccall[.CALLER = eps])], HOBJECT n_closure)',
            '$dynamic_site(S, (porigin_outer_call))',
            '$dynamic_fixed_name(S, porigin_outer_call) = eps',
            '$gc_materialized_caller_target(S, CLOSURE_TARGET n_closure, (porigin_outer_call))',
            '$call_context_roots(S.CURRENT) = [HOBJECT n_closure]',
            'S.GLOBALTABLE = (psymboltable_global)',
            '$lookup(psymboltable_global.ENV, $ptascii("collector")) = (n_collector_cell)',
            'S.STORE[n_collector_cell] = DEFINED (POBJECT n_closure)',
            '(HCELL n_collector_cell) <- $machine_roots(S)',
            '$lookup(psymboltable_global.ENV, $ptascii("token")) = eps',
            '$lookup(psymboltable_global.ENV, $ptascii("leaf")) = eps',
            '$lookup(psymboltable_global.ENV, $ptascii("leaf2")) = eps',
            '$lookup(psymboltable_global.ENV, $ptascii("weakLeaf")) = (n_weakleaf_cell)',
            'S.STORE[n_weakleaf_cell] = DEFINED (POBJECT n_weakleaf)',
            'S.OBJECTS[n_weakleaf] = WEAKREFERENCE (n_leaf)',
            '$lookup(S.ENV, $ptascii("token")) = (n_token_local_cell)',
            'S.STORE[n_token_local_cell] = DEFINED (PARRAY n_array)',
            '$lookup(S.ENV, $ptascii("copy")) = eps',
            '$lookup(S.ENV, $ptascii("leafCopy")) = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_closure) = 2',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_leaf) = 2',
            '(HARRAY n_array) <- $heap_reach([HOBJECT n_closure], eps, H.EDGES)',
            '(HOBJECT n_leaf) <- $heap_reach([HOBJECT n_closure], eps, H.EDGES)',
            '~((HARRAY n_array) <- $gc_white(H, $gc_eligible_nodes(pgcplan.BUFFER)))',
            '~((HOBJECT n_leaf) <- $gc_white(H, $gc_eligible_nodes(pgcplan.BUFFER)))',
            '$lookup(S.ENV, $ptascii("held")) = (n_held_cell)',
            'S.STORE[n_held_cell] = DEFINED (POBJECT n_held)',
            '$heap_owners($heap_graph(S), HOBJECT n_held) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_drop) = 1',
            '~$gc_materialized_caller_target(S, CLOSURE_TARGET n_closure, (pgccall.CALL.SITE))',
            '~$gc_materialized_caller_target(S[.SOURCES = eps], CLOSURE_TARGET n_closure, (porigin_outer_call))',
        ], 'timeout': 240,
    },
}


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
