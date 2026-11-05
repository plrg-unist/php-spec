#!/usr/bin/env python3
"""Reached nested DIRECT-array DAGs preserve sharing and local COW owners."""
import argparse

import gc_caller_materialized_state as ordinary
import gc_nested_array_sources as sources
import shutdown_state_review as runner


STAGE = 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* -- if pgccall.PASS = 0 -- if S.GC.NEXT = 2'


def common(captures, children):
    return [
        *ordinary.COMMON,
        'pcallcontext.TARGET = CLOSURE_TARGET n_closure',
        'pcallcontext.INSTANCE = (n_closure)',
        'pcallcontext.RECEIVER = eps',
        'pcallcontext.WRAPPER = eps',
        f'S.OBJECTS[n_closure] = REALCLOSURE porigin_template ({captures}) eps',
        f'$node_children(S, HOBJECT n_closure) = {children}',
        f'$gc_trace_children(S, HOBJECT n_closure) = {children}',
        f'$gc_direct_captures({captures})',
        f'~$gc_plain_captures(S, {captures})',
        'H_capture = $heap_graph(S)',
        f'pnode_capture* = $heap_reach($closure_items_nodes({captures}), eps, H_capture.EDGES)',
        'pnode_pool* = $heap_reach($pools_nodes(S.POOLS), eps, H_capture.EDGES)',
        '$gc_nested_array_edges($heap_live_edges(H_capture.EDGES, pnode_capture*))',
        '$gc_direct_graph_nodes(S, pnode_capture*, H_capture.EDGES, pnode_pool*)',
        '$gc_ordinary_node(S, HOBJECT n_closure)',
        '$gc_ordinary_nodes(S, S.ALLOCATIONS)',
        '$closure_callable(S, n_closure)',
        '$gc_materialized_caller_target(S, CLOSURE_TARGET n_closure, pcallcontext.CALLSITE)',
        '$heap_owners(H_capture, HOBJECT n_closure) = 2',
        'S.GLOBALTABLE = (psymboltable_global)',
        '$lookup(psymboltable_global.ENV, $ptascii("collector")) = (n_collector_cell)',
        'S.STORE[n_collector_cell] = DEFINED (POBJECT n_closure)',
        '$lookup(psymboltable_global.ENV, $ptascii("leaf")) = eps',
        '$lookup(psymboltable_global.ENV, $ptascii("inner")) = eps',
        '$lookup(psymboltable_global.ENV, $ptascii("token")) = eps',
        '$lookup(psymboltable_global.ENV, $ptascii("weakLeaf")) = (n_weakleaf_cell)',
        'S.STORE[n_weakleaf_cell] = DEFINED (POBJECT n_weakleaf)',
        'S.OBJECTS[n_weakleaf] = WEAKREFERENCE (n_leaf)',
        'S.OBJECTS[n_leaf] = STDINSTANCE',
        '$node_children(S, HOBJECT n_leaf) = eps',
        '$gc_trace_children(S, HOBJECT n_leaf) = eps',
        '$node_children(S, HOBJECT n_weakleaf) = eps',
        '$gc_slot_find(S.GC.BUFFER, HOBJECT n_leaf, 0) = (n_leaf_slot)',
        '$heap_count(HOBJECT n_leaf, $gc_nodes(S.GC.BUFFER)) = 1',
        '$gc_slot_find(pgcplan.BUFFER, HOBJECT n_leaf, 0) = eps',
        '~((HOBJECT n_leaf) <- $gc_white(H, $gc_eligible_nodes(pgcplan.BUFFER)))',
        '$lookup(S.ENV, $ptascii("leafCopy")) = eps',
        '$lookup(S.ENV, $ptascii("copy")) = eps',
        '$lookup(S.ENV, $ptascii("innerCopy")) = eps',
        '$gc_buffer_valid(S, S.GC)',
        'S_unrooted = S[.CURRENT = (pcallcontext[.INSTANCE = eps])]',
        '~((HOBJECT n_closure) <- $machine_roots(S_unrooted))',
        '~$gc_ordinary_node(S_unrooted, HOBJECT n_closure)',
        '~$gc_ordinary_node(S[.GC.ACTIVE = eps], HOBJECT n_closure)',
        '~$gc_ordinary_node(S[.GC.ACTIVE = (pgccall[.CALLER = eps])], HOBJECT n_closure)',
        '~$gc_ordinary_node(S[.SOURCES = eps], HOBJECT n_closure)',
        '~$gc_direct_captures([DIRECT PNULL, UNINITIALIZED])',
        '~$gc_direct_captures([DIRECT PNULL, DIRECT PUNDEFINED])',
        '~$gc_direct_captures([INDIRECT n_held $ptascii("head")])',
    ]


def arrays(rows):
    result = []
    for name, owners, children, buffered in rows:
        result += [
            f'(HARRAY {name}) <- S.ALLOCATIONS',
            f'~$gc_immutable_array(S, {name})',
            f'~$gc_proxy(S, {name})',
            f'~((HARRAY {name}) <- pnode_pool*)',
            f'$gc_direct_array_entries(S.ARRAYS[{name}].ITEMS)',
            f'$node_children(S, HARRAY {name}) = {children}',
            f'$gc_trace_children(S, HARRAY {name}) = {children}',
            f'$heap_owners(H_capture, HARRAY {name}) = {owners}',
            f'~((HARRAY {name}) <- $heap_reach($heap_children(HARRAY {name}, H_capture.EDGES), eps, H_capture.EDGES))',
            f'~((HARRAY {name}) <- $gc_white(H, $gc_eligible_nodes(pgcplan.BUFFER)))',
            f'$gc_slot_find(pgcplan.BUFFER, HARRAY {name}, 0) = eps',
        ]
        if buffered:
            result += [
                f'$gc_slot_find(S.GC.BUFFER, HARRAY {name}, 0) = (n_slot_{name})',
                f'$heap_count(HARRAY {name}, $gc_nodes(S.GC.BUFFER)) = 1',
                f'$(n_slot_{name} < n_leaf_slot)',
            ]
        else:
            result += [f'~((HARRAY {name}) <- $gc_nodes(S.GC.BUFFER))']
    return result


def refusal(label, mutation, captures):
    return [
        f'S_{label} = {mutation}',
        f'$closure_callable(S_{label}, n_closure)',
        f'$gc_materialized_caller_target(S_{label}, CLOSURE_TARGET n_closure, pcallcontext.CALLSITE)',
        f'H_{label} = $heap_graph(S_{label})',
        f'pnode_bad_{label}* = $heap_reach($closure_items_nodes({captures}), eps, H_{label}.EDGES)',
        f'~$gc_direct_graph_nodes(S_{label}, pnode_bad_{label}*, H_{label}.EDGES, $heap_reach($pools_nodes(S_{label}.POOLS), eps, H_{label}.EDGES))',
        f'~$gc_ordinary_node(S_{label}, HOBJECT n_closure)',
    ]


DAG_CAPTURES = '[DIRECT (PARRAY n_outer), DIRECT (PARRAY n_inner), DIRECT (POBJECT n_leaf)]'
DAG = common(DAG_CAPTURES, '[HARRAY n_outer, HARRAY n_inner, HOBJECT n_leaf]') + [
    'S.ARRAYS[n_outer].ITEMS = [ENTRY (KSTRING $ptascii("deep")) (DIRECT (PARRAY n_parent))]',
    'S.ARRAYS[n_parent].ITEMS = [ENTRY (KSTRING $ptascii("left")) (DIRECT (PARRAY n_inner)), ENTRY (KSTRING $ptascii("right")) (DIRECT (PARRAY n_inner))]',
    'S.ARRAYS[n_inner].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_leaf)), ENTRY (KINT 1) (DIRECT (POBJECT n_leaf))]',
    r'n_outer =/= n_parent /\ n_outer =/= n_inner /\ n_parent =/= n_inner',
    '$heap_edge_owners(HARRAY n_parent, H_capture.EDGES, [HARRAY n_outer]) = 1',
    '$heap_edge_owners(HARRAY n_inner, H_capture.EDGES, [HARRAY n_parent]) = 2',
    '$heap_edge_owners(HARRAY n_inner, H_capture.EDGES, [HOBJECT n_closure]) = 1',
    '$heap_edge_owners(HOBJECT n_leaf, H_capture.EDGES, [HARRAY n_inner]) = 2',
    '$heap_edge_owners(HOBJECT n_leaf, H_capture.EDGES, [HOBJECT n_closure]) = 1',
    '$heap_owners(H_capture, HOBJECT n_leaf) = 4',
    '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)',
    'S.STORE[n_second_cell] = DEFINED (PARRAY n_outer)',
    '$lookup(S.ENV, $ptascii("inner")) = (n_inner_cell)',
    'S.STORE[n_inner_cell] = DEFINED (PARRAY n_inner)',
    '$lookup(S.ENV, $ptascii("leaf")) = (n_leaf_cell)',
    'S.STORE[n_leaf_cell] = DEFINED (POBJECT n_leaf)',
    '$lookup(S.ENV, $ptascii("token")) = eps',
    '$lookup(S.ENV, $ptascii("parentCopy")) = eps',
    '$lookup(psymboltable_global.ENV, $ptascii("second")) = eps',
] + arrays([
    ('n_outer', 2, '[HARRAY n_parent]', True),
    ('n_parent', 1, '[HARRAY n_inner, HARRAY n_inner]', True),
    ('n_inner', 4, '[HOBJECT n_leaf, HOBJECT n_leaf]', True),
]) + [
    r'$(n_slot_n_outer < n_slot_n_parent) /\ $(n_slot_n_parent < n_slot_n_inner)',
    'n_bad_array = |S.ARRAYS|',
    'S.POOLS = ppool :: ppool_tail*',
]
for label, item in [('cycle', 'DIRECT (PARRAY n_inner)'),
                    ('missing', 'DIRECT (PARRAY n_bad_array)'),
                    ('alias', 'ALIAS n_inner_cell'),
                    ('indirect', 'INDIRECT n_held $ptascii("head")'),
                    ('undefined', 'DIRECT PUNDEFINED'),
                    ('uninitialized', 'UNINITIALIZED'),
                    ('dtor', 'DIRECT (POBJECT n_held)')]:
    DAG += refusal(label, f'S[.ARRAYS[n_inner].ITEMS = [ENTRY (KINT 0) ({item})]]', DAG_CAPTURES)
DAG += refusal('backedge', 'S[.ARRAYS[n_inner].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_parent))]]', DAG_CAPTURES)
DAG += refusal('proxy', 'S[.OBJECTTABLES = S.OBJECTTABLES ++ [{OBJECT n_held, TABLE n_inner}]]', DAG_CAPTURES)
DAG += refusal('pool', 'S[.POOLS = ppool[.CONSTANTS = [PCONSTANT ([PCINDEX 0]) (PARRAY n_parent)]] :: ppool_tail*]', DAG_CAPTURES)
DAG += refusal('immutable', 'S[.ARRAYS[n_inner] = $array_empty()][.GC.IMMUTABLE = S.GC.IMMUTABLE ++ [n_inner]]', DAG_CAPTURES)

COW_CAPTURES = '[DIRECT (PARRAY n_original), DIRECT (POBJECT n_other)]'
COW = common(COW_CAPTURES, '[HARRAY n_original, HOBJECT n_other]') + [
    'S.ARRAYS[n_original].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_old_inner)), ENTRY (KINT 1) (DIRECT (PARRAY n_old_inner))]',
    '$lookup(S.ENV, $ptascii("token")) = (n_token_cell)',
    'S.STORE[n_token_cell] = DEFINED (PARRAY n_local)',
    'S.ARRAYS[n_local].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_new_inner)), ENTRY (KINT 1) (DIRECT (PARRAY n_old_inner))]',
    'S.ARRAYS[n_old_inner].ITEMS = [ENTRY (KSTRING $ptascii("leaf")) (DIRECT (POBJECT n_leaf))]',
    'S.ARRAYS[n_new_inner].ITEMS = [ENTRY (KSTRING $ptascii("leaf")) (DIRECT (POBJECT n_leaf)), ENTRY (KSTRING $ptascii("tag")) (DIRECT (PINT 17))]',
    r'n_original =/= n_local /\ n_original =/= n_old_inner /\ n_original =/= n_new_inner',
    r'n_local =/= n_old_inner /\ n_local =/= n_new_inner /\ n_old_inner =/= n_new_inner',
    '$heap_edge_owners(HARRAY n_old_inner, H_capture.EDGES, [HARRAY n_original]) = 2',
    '$heap_edge_owners(HARRAY n_old_inner, H_capture.EDGES, [HARRAY n_local]) = 1',
    '$heap_edge_owners(HARRAY n_new_inner, H_capture.EDGES, [HARRAY n_local]) = 1',
    '$heap_edge_owners(HOBJECT n_leaf, H_capture.EDGES, [HARRAY n_old_inner]) = 1',
    '$heap_edge_owners(HOBJECT n_leaf, H_capture.EDGES, [HARRAY n_new_inner]) = 1',
    '$heap_edge_owners(HOBJECT n_leaf, H_capture.EDGES, [HOBJECT n_closure]) = 0',
    '$heap_owners(H_capture, HOBJECT n_leaf) = 2',
    '$heap_owners(H_capture, HOBJECT n_other) = 2',
    '$lookup(S.ENV, $ptascii("otherLeaf")) = (n_other_cell)',
    'S.STORE[n_other_cell] = DEFINED (POBJECT n_other)',
    'S.OBJECTS[n_other] = STDINSTANCE',
    '$node_children(S, HOBJECT n_other) = eps',
    '$gc_trace_children(S, HOBJECT n_other) = eps',
    '$lookup(S.ENV, $ptascii("leaf")) = eps',
    '$lookup(S.ENV, $ptascii("olderCopy")) = eps',
    '$lookup(psymboltable_global.ENV, $ptascii("otherLeaf")) = eps',
    '$lookup(psymboltable_global.ENV, $ptascii("weakOther")) = (n_weakother_cell)',
    'S.STORE[n_weakother_cell] = DEFINED (POBJECT n_weakother)',
    'S.OBJECTS[n_weakother] = WEAKREFERENCE (n_other)',
    '(HARRAY n_original) <- pnode_capture*',
    '(HARRAY n_old_inner) <- pnode_capture*',
    '~((HARRAY n_local) <- pnode_capture*)',
    '~((HARRAY n_new_inner) <- pnode_capture*)',
] + arrays([
    ('n_original', 1, '[HARRAY n_old_inner, HARRAY n_old_inner]', False),
    ('n_local', 1, '[HARRAY n_new_inner, HARRAY n_old_inner]', True),
    ('n_old_inner', 3, '[HOBJECT n_leaf]', True),
    ('n_new_inner', 1, '[HOBJECT n_leaf]', True),
]) + [
    r'$(n_slot_n_local < n_slot_n_new_inner) /\ $(n_slot_n_new_inner < n_slot_n_old_inner)',
]

CASES = {name: {'source': sources.PATHS[name].read_text(), 'stage': STAGE,
                 'checks': assertions, 'timeout': 240}
         for name, assertions in [('nested-shared-dag', DAG), ('nested-local-cow', COW)]}
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
