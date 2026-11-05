#!/usr/bin/env python3
"""Independent captured-wrapper and nested payload COW ownership checks."""
import argparse

import gc_caller_materialized_state as ordinary
import gc_reference_capture_review_sources as sources
import shutdown_state_review as runner


CAPTURES = '[ALIAS n_token_cell, ALIAS n_other_cell, ALIAS n_same_cell, ALIAS n_same_cell]'
CHECKS = [
    *ordinary.COMMON,
    'pcallcontext.TARGET = CLOSURE_TARGET n_closure',
    'pcallcontext.INSTANCE = (n_closure)',
    'pcallcontext.RECEIVER = eps',
    'pcallcontext.WRAPPER = eps',
    f'S.OBJECTS[n_closure] = REALCLOSURE porigin_template ({CAPTURES}) eps',
    '$closure_callable(S, n_closure)',
    '$gc_materialized_caller_target(S, CLOSURE_TARGET n_closure, pcallcontext.CALLSITE)',
    '$gc_ordinary_node(S, HOBJECT n_closure)',
    f'$closure_items_nodes({CAPTURES}) = [HCELL n_token_cell, HCELL n_other_cell, HCELL n_same_cell, HCELL n_same_cell]',
    f'$node_children(S, HOBJECT n_closure) = $closure_items_nodes({CAPTURES})',
    f'$gc_trace_children(S, HOBJECT n_closure) = $closure_items_nodes({CAPTURES})',
    f'$gc_reference_captures(S, {CAPTURES}, false)',
    f'~$gc_direct_captures({CAPTURES})',
    f'pnode_capture* = $heap_reach($closure_items_nodes({CAPTURES}), eps, H.EDGES)',
    'pnode_pool* = $heap_reach($pools_nodes(S.POOLS), eps, H.EDGES)',
    '$gc_reference_graph_nodes(S, pnode_capture*, H.EDGES, pnode_pool*)',
    '$heap_owners(H, HOBJECT n_closure) = 2',
    '(HOBJECT n_closure) <- $machine_roots(S)',
    'n_token_cell =/= n_other_cell',
    'n_token_cell =/= n_same_cell',
    'n_other_cell =/= n_same_cell',
    '$lookup(S.ENV, $ptascii("alias")) = (n_same_cell)',
    'S.STORE[n_token_cell] = DEFINED (PARRAY n_token_array)',
    'S.STORE[n_other_cell] = DEFINED (PARRAY n_other_array)',
    'S.STORE[n_same_cell] = DEFINED (PARRAY n_same_array)',
    'S.ARRAYS[n_token_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_token_inner)), ENTRY (KINT 1) (DIRECT (PARRAY n_old_inner))]',
    'S.ARRAYS[n_other_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_old_inner)), ENTRY (KINT 1) (DIRECT (PARRAY n_old_inner))]',
    'S.ARRAYS[n_same_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_same_inner)), ENTRY (KINT 1) (DIRECT (PARRAY n_old_inner))]',
    'S.ARRAYS[n_old_inner].ITEMS = [ENTRY (KSTRING $ptascii("leaf")) (DIRECT (POBJECT n_leaf)), ENTRY (KSTRING $ptascii("a")) (DIRECT (PINT 0)), ENTRY (KSTRING $ptascii("x")) (DIRECT (PINT 0))]',
    'S.ARRAYS[n_token_inner].ITEMS = [ENTRY (KSTRING $ptascii("leaf")) (DIRECT (POBJECT n_leaf)), ENTRY (KSTRING $ptascii("a")) (DIRECT (PINT 17)), ENTRY (KSTRING $ptascii("x")) (DIRECT (PINT 0))]',
    'S.ARRAYS[n_same_inner].ITEMS = [ENTRY (KSTRING $ptascii("leaf")) (DIRECT (POBJECT n_leaf)), ENTRY (KSTRING $ptascii("a")) (DIRECT (PINT 0)), ENTRY (KSTRING $ptascii("x")) (DIRECT (PINT 23))]',
    '$heap_owners(H, HARRAY n_old_inner) = 4',
    '$heap_owners(H, HOBJECT n_leaf) = 3',
    '$heap_edge_owners(HOBJECT n_leaf, H.EDGES, [HARRAY n_old_inner, HARRAY n_token_inner, HARRAY n_same_inner]) = 3',
    '$heap_edge_owners(HCELL n_same_cell, H.EDGES, [HOBJECT n_closure]) = 2',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV, $ptascii("weakLeaf")) = (n_weak_cell)',
    'S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
    'S.OBJECTS[n_weak] = WEAKREFERENCE (n_leaf)',
    '$node_children(S, HOBJECT n_weak) = eps',
    '$heap_edge_owners(HOBJECT n_leaf, H.EDGES, [HOBJECT n_weak]) = 0',
    '$gc_buffer_valid(S, S.GC)',
    'pgc_probe = S.GC[.BUFFER = eps][.FREE = eps]',
]

for name, owners in [('token', 2), ('other', 2), ('same', 4)]:
    CHECKS += [
        f'$lookup(S.ENV, $ptascii("{name}")) = (n_{name}_cell)',
        f'$ordinary_reference_value(S, n_{name}_cell) = (PARRAY n_{name}_array)',
        f'$node_children(S, HCELL n_{name}_cell) = [HARRAY n_{name}_array]',
        f'$gc_trace_children(S, HCELL n_{name}_cell) = [HARRAY n_{name}_array]',
        f'$heap_owners(H, HCELL n_{name}_cell) = {owners}',
        f'$heap_owners(H, HARRAY n_{name}_array) = 1',
        f'$heap_edge_owners(HARRAY n_{name}_array, H.EDGES, [HCELL n_{name}_cell]) = 1',
        f'$heap_edge_owners(HARRAY n_{name}_array, H.EDGES, [HOBJECT n_closure]) = 0',
        f'$gc_slot_find(S.GC.BUFFER, HCELL n_{name}_cell, 0) = eps',
        f'~$gc_possible_root(S, HCELL n_{name}_cell)',
        f'$gc_nodes($gc_decrement(S, pgc_probe, HCELL n_{name}_cell).BUFFER) = [HARRAY n_{name}_array]',
    ]
for node in ['HARRAY n_token_array', 'HARRAY n_other_array', 'HARRAY n_same_array',
             'HARRAY n_token_inner', 'HARRAY n_old_inner', 'HARRAY n_same_inner',
             'HOBJECT n_leaf']:
    CHECKS += [
        f'({node}) <- pnode_capture*',
        f'$heap_count({node}, $gc_nodes(S.GC.BUFFER)) = 1',
        f'~(({node}) <- $gc_white(pgcplan.GRAPH, $gc_eligible_nodes(pgcplan.BUFFER)))',
        f'$gc_slot_find(pgcplan.BUFFER, {node}, 0) = eps',
    ]
for name in ['token_inner', 'same_inner']:
    CHECKS.append(f'$heap_owners(H, HARRAY n_{name}) = 1')
slots = ['token_array', 'other_array', 'same_array', 'token_inner', 'old_inner', 'same_inner', 'leaf']
for name in slots:
    node = 'HOBJECT' if name == 'leaf' else 'HARRAY'
    CHECKS.append(f'$gc_slot_find(S.GC.BUFFER, {node} n_{name}, 0) = (n_slot_{name})')
for before, after in zip(slots, slots[1:]):
    CHECKS.append(f'$(n_slot_{before} < n_slot_{after})')

CHECKS += [
    'S_rebound = S[.STORE[n_token_cell] = DEFINED (PARRAY n_other_array)][.HELD = S.HELD ++ [HARRAY n_token_array]]',
    '$closure_callable(S_rebound, n_closure)',
    '$gc_materialized_caller_target(S_rebound, CLOSURE_TARGET n_closure, pcallcontext.CALLSITE)',
    '$gc_ordinary_node(S_rebound, HOBJECT n_closure)',
    'H_rebound = $heap_graph(S_rebound)',
    '$heap_valid(H_rebound)',
    '$heap_owners(H_rebound, HARRAY n_other_array) = 2',
    '$node_children(S_rebound, HCELL n_token_cell) = [HARRAY n_other_array]',
    '$gc_nodes($gc_decrement(S_rebound, pgc_probe, HCELL n_token_cell).BUFFER) = [HARRAY n_other_array]',
    '$gc_nodes($gc_decrements(S_rebound, pgc_probe, [HCELL n_token_cell, HCELL n_other_cell]).BUFFER) = [HARRAY n_other_array]',
]
for label, mutation in [
        ('alias_entry', '.ARRAYS[n_other_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_token_cell), ENTRY (KINT 1) (DIRECT (PARRAY n_old_inner))]'),
        ('closure_cycle', '.STORE[n_token_cell] = DEFINED (POBJECT n_closure)')]:
    CHECKS += [
        f'S_{label} = S[{mutation}]',
        f'$closure_callable(S_{label}, n_closure)',
        f'$gc_materialized_caller_target(S_{label}, CLOSURE_TARGET n_closure, pcallcontext.CALLSITE)',
        f'$gc_reference_captures(S_{label}, {CAPTURES}, false)',
        f'H_{label} = $heap_graph(S_{label})',
        f'pnode_{label}* = $heap_reach($closure_items_nodes({CAPTURES}), eps, H_{label}.EDGES)',
        f'~$gc_reference_graph_nodes(S_{label}, pnode_{label}*, H_{label}.EDGES, $heap_reach($pools_nodes(S_{label}.POOLS), eps, H_{label}.EDGES))',
        f'~$gc_ordinary_node(S_{label}, HOBJECT n_closure)',
    ]

CASES = {'independent-reference-payload-cow': {
    'source': sources.SOURCE.read_text(),
    'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* -- if pgccall.PASS = 0 -- if S.GC.NEXT = 2',
    'checks': CHECKS, 'timeout': 240,
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
