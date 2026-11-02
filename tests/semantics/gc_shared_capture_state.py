#!/usr/bin/env python3
"""Reached direct Closure captures sharing one childless array leaf."""
import argparse

import gc_caller_materialized_state as ordinary
import gc_shared_capture_sources as sources
import shutdown_state_review as runner


def checks(captures, children):
    extra_array = captures[:-1] + ', DIRECT (PARRAY n_array)]'
    extra_object = captures[:-1] + ', DIRECT (POBJECT n_other)]'
    return [
        *ordinary.COMMON,
        'pcallcontext.TARGET = CLOSURE_TARGET n_closure',
        'pcallcontext.INSTANCE = (n_closure)',
        'pcallcontext.RECEIVER = eps',
        'pcallcontext.WRAPPER = eps',
        f'S.OBJECTS[n_closure] = REALCLOSURE porigin_template ({captures}) eps',
        '(HOBJECT n_closure) <- S.ALLOCATIONS',
        '(HARRAY n_array) <- S.ALLOCATIONS',
        'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_leaf))]',
        '(HOBJECT n_leaf) <- S.ALLOCATIONS',
        'S.OBJECTS[n_leaf] = STDINSTANCE',
        '~$gc_immutable_array(S, n_array)',
        '~$gc_proxy(S, n_array)',
        '~((HARRAY n_array) <- $heap_reach($pools_nodes(S.POOLS), eps, $heap_graph(S).EDGES))',
        '$target_function(S, CLOSURE_TARGET n_closure) = (pfunction_closure)',
        '$function_at(S.CLOSURETEMPLATES, porigin_template) = (pfunction_closure)',
        f'$gc_capture_array_nodes({captures}) = [HARRAY n_array]',
        f'$gc_shared_array_captures(S, {captures}, n_array, false)',
        f'$closure_items_nodes({captures}) = {children}',
        f'$node_children(S, HOBJECT n_closure) = {children}',
        f'$gc_trace_children(S, HOBJECT n_closure) = {children}',
        '$node_children(S, HARRAY n_array) = [HOBJECT n_leaf]',
        '$gc_trace_children(S, HARRAY n_array) = [HOBJECT n_leaf]',
        '$node_children(S, HOBJECT n_leaf) = eps',
        '$gc_trace_children(S, HOBJECT n_leaf) = eps',
        '$gc_plain_array_entries(S, S.ARRAYS[n_array].ITEMS)',
        '$heap_edge_owners(HOBJECT n_leaf, H.EDGES, [HOBJECT n_closure]) = 1',
        '$heap_edge_owners(HOBJECT n_leaf, H.EDGES, [HARRAY n_array]) = 1',
        '(HARRAY n_array) <- $gc_nodes(S.GC.BUFFER)',
        '$gc_slot_find(S.GC.BUFFER, HARRAY n_array, 0) = (n_array_slot)',
        '(HOBJECT n_leaf) <- $gc_nodes(S.GC.BUFFER)',
        '$gc_slot_find(S.GC.BUFFER, HOBJECT n_leaf, 0) = (n_leaf_slot)',
        '$(n_array_slot < n_leaf_slot)',
        '$heap_count(HOBJECT n_leaf, $gc_nodes(S.GC.BUFFER)) = 1',
        '$gc_buffer_valid(S, S.GC)',
        '$gc_slot_find(pgcplan.BUFFER, HARRAY n_array, 0) = eps',
        '$gc_slot_find(pgcplan.BUFFER, HOBJECT n_leaf, 0) = eps',
        '$gc_ordinary_node(S, HOBJECT n_closure)',
        '$gc_ordinary_nodes(S, S.ALLOCATIONS)',
        '~$gc_shared_array_captures(S[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]], '
        f'{captures}, n_array, false)',
        '~$gc_ordinary_node(S[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]], HOBJECT n_closure)',
        f'$gc_capture_array_nodes({extra_array}) = [HARRAY n_array, HARRAY n_array]',
        f'~$gc_ordinary_node(S[.OBJECTS[n_closure] = REALCLOSURE porigin_template '
        f'({extra_array}) eps], HOBJECT n_closure)',
        'n_other = |S.OBJECTS|',
        'S_extra = S[.OBJECTS = S.OBJECTS ++ [STDINSTANCE]]'
        '[.ALLOCATIONS = S.ALLOCATIONS ++ [HOBJECT n_other]]',
        'S_extra.OBJECTS[n_other] = STDINSTANCE',
        '$node_children(S_extra, HOBJECT n_other) = eps',
        f'$gc_capture_array_nodes({extra_object}) = [HARRAY n_array]',
        f'~$gc_shared_array_captures(S_extra, {extra_object}, n_array, false)',
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
        '$lookup(psymboltable_global.ENV, $ptascii("weakLeaf")) = (n_weakleaf_cell)',
        'S.STORE[n_weakleaf_cell] = DEFINED (POBJECT n_weakleaf)',
        'S.OBJECTS[n_weakleaf] = WEAKREFERENCE (n_leaf)',
        '$lookup(S.ENV, $ptascii("token")) = (n_token_local_cell)',
        'S.STORE[n_token_local_cell] = DEFINED (PARRAY n_array)',
        '$lookup(S.ENV, $ptascii("leaf")) = (n_leaf_local_cell)',
        'S.STORE[n_leaf_local_cell] = DEFINED (POBJECT n_leaf)',
        '$lookup(S.ENV, $ptascii("copy")) = eps',
        '$lookup(S.ENV, $ptascii("leafCopy")) = eps',
        '$heap_owners($heap_graph(S), HOBJECT n_closure) = 2',
        '$heap_owners($heap_graph(S), HARRAY n_array) = 2',
        '$heap_owners($heap_graph(S), HOBJECT n_leaf) = 3',
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
    ]


FORWARD = '[DIRECT (PARRAY n_array), DIRECT (POBJECT n_leaf)]'
REVERSED = '[DIRECT (POBJECT n_leaf), DIRECT (PARRAY n_array)]'
STAGE = 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* -- if pgccall.PASS = 0 -- if S.GC.NEXT = 2'
CASES = {
    'shared-array-leaf': {
        'source': sources.PATHS['shared-array-leaf'].read_text(),
        'stage': STAGE,
        'checks': checks(FORWARD, '[HARRAY n_array, HOBJECT n_leaf]'),
        'timeout': 240,
    },
    'shared-leaf-array-reversed': {
        'source': sources.PATHS['shared-leaf-array-reversed'].read_text(),
        'stage': STAGE,
        'checks': checks(REVERSED, '[HOBJECT n_leaf, HARRAY n_array]'),
        'timeout': 240,
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
