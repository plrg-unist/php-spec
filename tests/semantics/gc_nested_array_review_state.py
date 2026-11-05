#!/usr/bin/env python3
"""Independent COW-component and real self-copy snapshot GC fronts."""
import argparse

import gc_caller_materialized_state as ordinary
import gc_nested_array_sources as sources
import gc_nested_array_review_sources as snapshot
import shutdown_state_review as runner


STAGE = 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* -- if pgccall.PASS = 0 -- if S.GC.NEXT = 2'


def common(captures):
    return [
        'S.CURRENT = (pcallcontext)',
        'pgccall.CALLER = (pcallcontext)',
        'pcallcontext.TARGET = CLOSURE_TARGET n_closure',
        'pcallcontext.INSTANCE = (n_closure)',
        'pcallcontext.RECEIVER = eps',
        'pcallcontext.WRAPPER = eps',
        f'S.OBJECTS[n_closure] = REALCLOSURE porigin_template ({captures}) eps',
        'H = $heap_graph(S)',
        '$heap_valid(H)',
        '$closure_callable(S, n_closure)',
        '$gc_materialized_caller_target(S, CLOSURE_TARGET n_closure, pcallcontext.CALLSITE)',
        '$gc_materialized_callback_context(S)',
        '$gc_ordinary_node(S, HOBJECT n_closure)',
        f'$node_children(S, HOBJECT n_closure) = $closure_items_nodes({captures})',
        f'$gc_trace_children(S, HOBJECT n_closure) = $closure_items_nodes({captures})',
        '(HOBJECT n_closure) <- $machine_roots(S)',
        '$heap_owners(H, HOBJECT n_closure) = 2',
        f'pnode_capture* = $heap_reach($closure_items_nodes({captures}), eps, H.EDGES)',
        'pnode_pool* = $heap_reach($pools_nodes(S.POOLS), eps, H.EDGES)',
        '$gc_direct_graph_nodes(S, pnode_capture*, H.EDGES, pnode_pool*)',
        '$gc_nested_array_edges($heap_live_edges(H.EDGES, pnode_capture*))',
        f'~$gc_plain_captures(S, {captures})',
        'S.GLOBALTABLE = (psymboltable_global)',
        '$lookup(psymboltable_global.ENV, $ptascii("weakLeaf")) = (n_weak_cell)',
        'S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
        'S.OBJECTS[n_weak] = WEAKREFERENCE (n_leaf)',
        '$node_children(S, HOBJECT n_weak) = eps',
        '$heap_edge_owners(HOBJECT n_leaf, H.EDGES, [HOBJECT n_weak]) = 0',
        'pgcplan = $gc_plan(S, pgccall)',
        '$gc_buffer_valid(S, S.GC)',
    ]


COW_CAPTURES = '[DIRECT (PARRAY n_original), DIRECT (POBJECT n_other)]'
FLAT_CAPTURES = '[DIRECT (PARRAY n_old_inner), DIRECT (POBJECT n_other)]'
COW = common(COW_CAPTURES) + [
    'S.ARRAYS[n_original].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_old_inner)), ENTRY (KINT 1) (DIRECT (PARRAY n_old_inner))]',
    '$lookup(S.ENV, $ptascii("token")) = (n_local_cell)',
    'S.STORE[n_local_cell] = DEFINED (PARRAY n_local)',
    'S.ARRAYS[n_local].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_new_inner)), ENTRY (KINT 1) (DIRECT (PARRAY n_old_inner))]',
    'S.ARRAYS[n_old_inner].ITEMS = [ENTRY (KSTRING $ptascii("leaf")) (DIRECT (POBJECT n_leaf))]',
    'S.ARRAYS[n_new_inner].ITEMS = [ENTRY (KSTRING $ptascii("leaf")) (DIRECT (POBJECT n_leaf)), ENTRY (KSTRING $ptascii("tag")) (DIRECT (PINT 17))]',
    '$heap_owners(H, HARRAY n_original) = 1',
    '$heap_owners(H, HARRAY n_local) = 1',
    '$heap_owners(H, HARRAY n_old_inner) = 3',
    '$heap_owners(H, HARRAY n_new_inner) = 1',
    '$heap_owners(H, HOBJECT n_leaf) = 2',
    '$heap_owners(H, HOBJECT n_other) = 2',
    '~((HARRAY n_local) <- pnode_capture*)',
    '~((HARRAY n_new_inner) <- pnode_capture*)',
    'S_flat = S[.OBJECTS[n_closure] = REALCLOSURE porigin_template (' + FLAT_CAPTURES + ') eps][.HELD = S.HELD ++ [HARRAY n_original]]',
    '$closure_callable(S_flat, n_closure)',
    '$gc_materialized_caller_target(S_flat, CLOSURE_TARGET n_closure, pcallcontext.CALLSITE)',
    '(HOBJECT n_closure) <- $machine_roots(S_flat)',
    f'$node_children(S_flat, HOBJECT n_closure) = $closure_items_nodes({FLAT_CAPTURES})',
    f'$gc_trace_children(S_flat, HOBJECT n_closure) = $closure_items_nodes({FLAT_CAPTURES})',
    'H_flat = $heap_graph(S_flat)',
    '$heap_valid(H_flat)',
    f'pnode_flat* = $heap_reach($closure_items_nodes({FLAT_CAPTURES}), eps, H_flat.EDGES)',
    '$gc_direct_graph_nodes(S_flat, pnode_flat*, H_flat.EDGES, $heap_reach($pools_nodes(S_flat.POOLS), eps, H_flat.EDGES))',
    f'$gc_plain_captures(S_flat, {FLAT_CAPTURES})',
    '$gc_nested_array_edges(H_flat.EDGES)',
    '~$gc_nested_array_edges($heap_live_edges(H_flat.EDGES, pnode_flat*))',
    '~((HOBJECT n_other) <- $node_children(S_flat, HARRAY n_old_inner))',
    f'~$gc_shared_array_captures(S_flat, {FLAT_CAPTURES}, n_old_inner, false)',
    '~$gc_ordinary_node(S_flat, HOBJECT n_closure)',
]

SNAPSHOT_CAPTURES = '[DIRECT (PARRAY n_outer)]'
SNAPSHOT = common(SNAPSHOT_CAPTURES) + [
    'S.ARRAYS[n_outer].ITEMS = [ENTRY (KSTRING $ptascii("leaf")) (DIRECT (POBJECT n_leaf)), ENTRY (KSTRING $ptascii("self")) (DIRECT (PARRAY n_old))]',
    'S.ARRAYS[n_old].ITEMS = [ENTRY (KSTRING $ptascii("leaf")) (DIRECT (POBJECT n_leaf))]',
    'n_outer =/= n_old',
    'S.OBJECTS[n_leaf] = STDINSTANCE',
    '$node_children(S, HOBJECT n_leaf) = eps',
    '$node_children(S, HARRAY n_outer) = [HOBJECT n_leaf, HARRAY n_old]',
    '$node_children(S, HARRAY n_old) = [HOBJECT n_leaf]',
    '$heap_owners(H, HARRAY n_outer) = 2',
    '$heap_owners(H, HARRAY n_old) = 1',
    '$heap_owners(H, HOBJECT n_leaf) = 2',
    '$heap_edge_owners(HOBJECT n_leaf, H.EDGES, [HARRAY n_outer]) = 1',
    '$heap_edge_owners(HOBJECT n_leaf, H.EDGES, [HARRAY n_old]) = 1',
    '$heap_edge_owners(HOBJECT n_leaf, H.EDGES, [HOBJECT n_closure]) = 0',
    '~((HARRAY n_outer) <- $heap_reach($heap_children(HARRAY n_outer, H.EDGES), eps, H.EDGES))',
    '~((HARRAY n_old) <- $heap_reach($heap_children(HARRAY n_old, H.EDGES), eps, H.EDGES))',
    '$lookup(S.ENV, $ptascii("token")) = (n_local_cell)',
    'S.STORE[n_local_cell] = DEFINED (PARRAY n_outer)',
    '$lookup(S.ENV, $ptascii("leaf")) = eps',
    '$lookup(psymboltable_global.ENV, $ptascii("leaf")) = eps',
    '$lookup(psymboltable_global.ENV, $ptascii("token")) = eps',
    '$gc_slot_find(S.GC.BUFFER, HARRAY n_outer, 0) = (n_outer_slot)',
    '$gc_slot_find(S.GC.BUFFER, HARRAY n_old, 0) = (n_old_slot)',
    '$gc_slot_find(S.GC.BUFFER, HOBJECT n_leaf, 0) = (n_leaf_slot)',
    '$(n_outer_slot < n_old_slot)',
    '$(n_old_slot < n_leaf_slot)',
]
for node in ['HARRAY n_outer', 'HARRAY n_old', 'HOBJECT n_leaf']:
    SNAPSHOT += [
        f'$heap_count({node}, $gc_nodes(S.GC.BUFFER)) = 1',
        f'$gc_slot_find(pgcplan.BUFFER, {node}, 0) = eps',
        f'~(({node}) <- $gc_white(pgcplan.GRAPH, $gc_eligible_nodes(pgcplan.BUFFER)))',
    ]
for label, child in [('cycle', 'n_outer'), ('self', 'n_old')]:
    SNAPSHOT += [
        f'S_{label} = S[.ARRAYS[n_old].ITEMS = [ENTRY (KSTRING $ptascii("leaf")) (DIRECT (PARRAY {child}))]]',
        f'$closure_callable(S_{label}, n_closure)',
        f'$gc_materialized_caller_target(S_{label}, CLOSURE_TARGET n_closure, pcallcontext.CALLSITE)',
        f'H_{label} = $heap_graph(S_{label})',
        f'pnode_{label}* = $heap_reach([HARRAY n_outer], eps, H_{label}.EDGES)',
        f'$gc_direct_array_entries(S_{label}.ARRAYS[n_old].ITEMS)',
        f'$gc_nested_array_edges($heap_live_edges(H_{label}.EDGES, pnode_{label}*))',
        f'~$gc_direct_graph_nodes(S_{label}, pnode_{label}*, H_{label}.EDGES, $heap_reach($pools_nodes(S_{label}.POOLS), eps, H_{label}.EDGES))',
        f'~$gc_ordinary_node(S_{label}, HOBJECT n_closure)',
    ]

CASES = {
    'independent-cow-component': {
        'source': sources.PATHS['nested-local-cow'].read_text(),
        'stage': STAGE, 'checks': COW, 'timeout': 240,
    },
    'independent-self-copy': {
        'source': snapshot.SOURCE.read_text(),
        'stage': STAGE, 'checks': SNAPSHOT, 'timeout': 240,
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
