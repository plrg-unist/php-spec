#!/usr/bin/env python3
"""Reached finite Closure capture graphs preserve physical edge multiplicity."""
import argparse

import gc_caller_materialized_state as ordinary
import gc_multi_array_sources as sources
import shutdown_state_review as runner


STAGE = 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* -- if pgccall.PASS = 0 -- if S.GC.NEXT = 2'


def checks(captures, closure_nodes, arrays, leaf_owners, direct_leaf, other=False):
    result = [
        *ordinary.COMMON,
        'pcallcontext.TARGET = CLOSURE_TARGET n_closure',
        'pcallcontext.INSTANCE = (n_closure)',
        'pcallcontext.RECEIVER = eps',
        'pcallcontext.WRAPPER = eps',
        f'S.OBJECTS[n_closure] = REALCLOSURE porigin_template ({captures}) eps',
        '(HOBJECT n_closure) <- S.ALLOCATIONS',
        f'$closure_items_nodes({captures}) = {closure_nodes}',
        f'$node_children(S, HOBJECT n_closure) = {closure_nodes}',
        f'$gc_trace_children(S, HOBJECT n_closure) = {closure_nodes}',
        f'$gc_plain_captures(S, {captures})',
        '$gc_ordinary_node(S, HOBJECT n_closure)',
        '$gc_ordinary_nodes(S, S.ALLOCATIONS)',
        '$target_function(S, CLOSURE_TARGET n_closure) = (pfunction_closure)',
        '$function_at(S.CLOSURETEMPLATES, porigin_template) = (pfunction_closure)',
        'S.GLOBALTABLE = (psymboltable_global)',
        '$lookup(psymboltable_global.ENV, $ptascii("collector")) = (n_collector_cell)',
        'S.STORE[n_collector_cell] = DEFINED (POBJECT n_closure)',
        '(HCELL n_collector_cell) <- $machine_roots(S)',
        '$lookup(psymboltable_global.ENV, $ptascii("token")) = eps',
        '$lookup(psymboltable_global.ENV, $ptascii("second")) = eps',
        '$lookup(psymboltable_global.ENV, $ptascii("leaf")) = eps',
        '$lookup(S.ENV, $ptascii("token")) = (n_token_local_cell)',
        'S.STORE[n_token_local_cell] = DEFINED (PARRAY n_array)',
        '$lookup(S.ENV, $ptascii("copy")) = eps',
        '$lookup(S.ENV, $ptascii("secondCopy")) = eps',
        '$lookup(S.ENV, $ptascii("leafCopy")) = eps',
        '$lookup(psymboltable_global.ENV, $ptascii("weakLeaf")) = (n_weakleaf_cell)',
        'S.STORE[n_weakleaf_cell] = DEFINED (POBJECT n_weakleaf)',
        'S.OBJECTS[n_weakleaf] = WEAKREFERENCE (n_leaf)',
        '(HOBJECT n_leaf) <- S.ALLOCATIONS',
        'S.OBJECTS[n_leaf] = STDINSTANCE',
        '$node_children(S, HOBJECT n_leaf) = eps',
        '$gc_trace_children(S, HOBJECT n_leaf) = eps',
        '$heap_owners(H, HOBJECT n_closure) = 2',
        f'$heap_owners(H, HOBJECT n_leaf) = {leaf_owners}',
        '(HOBJECT n_leaf) <- $heap_reach([HOBJECT n_closure], eps, H.EDGES)',
        '$gc_slot_find(S.GC.BUFFER, HOBJECT n_leaf, 0) = (n_leaf_slot)',
        '$heap_count(HOBJECT n_leaf, $gc_nodes(S.GC.BUFFER)) = 1',
        '$gc_slot_find(pgcplan.BUFFER, HOBJECT n_leaf, 0) = eps',
        '~((HOBJECT n_leaf) <- $gc_white(H, $gc_eligible_nodes(pgcplan.BUFFER)))',
        '$gc_buffer_valid(S, S.GC)',
        '$call_context_roots(S.CURRENT) = [HOBJECT n_closure]',
        '$lookup(S.ENV, $ptascii("held")) = (n_held_cell)',
        'S.STORE[n_held_cell] = DEFINED (POBJECT n_held)',
        '$heap_owners(H, HOBJECT n_held) = 2',
        '$heap_owners(H, HOBJECT n_drop) = 1',
        'S_unrooted = S[.CURRENT = (pcallcontext[.INSTANCE = eps])]',
        '~((HOBJECT n_closure) <- $machine_roots(S_unrooted))',
        '~$gc_ordinary_node(S_unrooted, HOBJECT n_closure)',
        '~$gc_ordinary_node(S[.GC.ACTIVE = eps], HOBJECT n_closure)',
        '~$gc_ordinary_node(S[.GC.ACTIVE = (pgccall[.CALLER = eps])], HOBJECT n_closure)',
        '$dynamic_site(S, (porigin_outer_call))',
        '$gc_materialized_caller_target(S, CLOSURE_TARGET n_closure, (porigin_outer_call))',
        '~$gc_materialized_caller_target(S, CLOSURE_TARGET n_closure, (pgccall.CALL.SITE))',
        '~$gc_materialized_caller_target(S[.SOURCES = eps], CLOSURE_TARGET n_closure, (porigin_outer_call))',
    ]
    for array, local, owners, children, edges in arrays:
        result += [
            f'(HARRAY {array}) <- S.ALLOCATIONS',
            f'~$gc_immutable_array(S, {array})',
            f'~$gc_proxy(S, {array})',
            f'~((HARRAY {array}) <- $heap_reach($pools_nodes(S.POOLS), eps, H.EDGES))',
            f'$gc_plain_array_entries(S, S.ARRAYS[{array}].ITEMS)',
            f'$node_children(S, HARRAY {array}) = {children}',
            f'$gc_trace_children(S, HARRAY {array}) = {children}',
            f'$heap_edge_owners(HOBJECT n_leaf, H.EDGES, [HARRAY {array}]) = {edges}',
            f'$heap_owners(H, HARRAY {array}) = {owners}',
            f'$lookup(S.ENV, $ptascii("{local}")) = (n_{local}_cell)',
            f'S.STORE[n_{local}_cell] = DEFINED (PARRAY {array})',
            f'(HARRAY {array}) <- $heap_reach([HOBJECT n_closure], eps, H.EDGES)',
            f'$gc_slot_find(S.GC.BUFFER, HARRAY {array}, 0) = (n_{local}_slot)',
            f'$(n_{local}_slot < n_leaf_slot)',
            f'$heap_count(HARRAY {array}, $gc_nodes(S.GC.BUFFER)) = 1',
            f'$gc_slot_find(pgcplan.BUFFER, HARRAY {array}, 0) = eps',
            f'~((HARRAY {array}) <- $gc_white(H, $gc_eligible_nodes(pgcplan.BUFFER)))',
        ]
    result += [
        f'$heap_edge_owners(HOBJECT n_leaf, H.EDGES, [HOBJECT n_closure]) = {direct_leaf}',
        '$gc_plain_captures(S, [DIRECT (PARRAY n_array), DIRECT (PARRAY n_array)])',
        '~$gc_plain_captures(S, [DIRECT (PARRAY n_array), DIRECT (PARRAY n_array), ALIAS n_token_local_cell])',
        '~$gc_plain_captures(S, [DIRECT (PARRAY n_array), DIRECT (PARRAY n_array), INDIRECT n_held $ptascii("head")])',
        '~$gc_plain_captures(S, [DIRECT (PARRAY n_array), DIRECT (PARRAY n_array), DIRECT PUNDEFINED])',
        '~$gc_plain_captures(S, [DIRECT (PARRAY n_array), DIRECT (PARRAY n_array), DIRECT (POBJECT n_held)])',
        'n_bad_array = |S.ARRAYS|',
        'n_bad_object = |S.OBJECTS|',
        '~$gc_plain_captures(S, [DIRECT (PARRAY n_array), DIRECT (PARRAY n_bad_array)])',
        '~$gc_plain_captures(S, [DIRECT (PARRAY n_array), DIRECT (PARRAY n_array), DIRECT (POBJECT n_bad_object)])',
    ]
    if other:
        result += [
            '(HOBJECT n_other) <- S.ALLOCATIONS',
            'S.OBJECTS[n_other] = STDINSTANCE',
            '$node_children(S, HOBJECT n_other) = eps',
            '$gc_trace_children(S, HOBJECT n_other) = eps',
            '$lookup(psymboltable_global.ENV, $ptascii("otherLeaf")) = eps',
            '$lookup(psymboltable_global.ENV, $ptascii("weakOther")) = (n_weakother_cell)',
            'S.STORE[n_weakother_cell] = DEFINED (POBJECT n_weakother)',
            'S.OBJECTS[n_weakother] = WEAKREFERENCE (n_other)',
        ]
    return result


DISTINCT_CAPTURES = '[DIRECT (PARRAY n_array), DIRECT (POBJECT n_leaf), DIRECT (PARRAY n_second), DIRECT (POBJECT n_other)]'
DISTINCT = checks(DISTINCT_CAPTURES, '[HARRAY n_array, HOBJECT n_leaf, HARRAY n_second, HOBJECT n_other]', [
    ('n_array', 'token', 2, '[HOBJECT n_leaf, HOBJECT n_leaf]', 2),
    ('n_second', 'second', 2, '[HOBJECT n_leaf, HOBJECT n_other]', 1),
], 5, 1, other=True) + [
    'n_array =/= n_second',
    'n_leaf =/= n_other',
    f'$gc_capture_array_nodes({DISTINCT_CAPTURES}) = [HARRAY n_array, HARRAY n_second]',
    'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_leaf)), ENTRY (KINT 1) (DIRECT (POBJECT n_leaf))]',
    'S.ARRAYS[n_second].ITEMS = [ENTRY (KSTRING $ptascii("shared")) (DIRECT (POBJECT n_leaf)), ENTRY (KSTRING $ptascii("own")) (DIRECT (POBJECT n_other))]',
    '$heap_edge_owners(HARRAY n_array, H.EDGES, [HOBJECT n_closure]) = 1',
    '$heap_edge_owners(HARRAY n_second, H.EDGES, [HOBJECT n_closure]) = 1',
    '$heap_owners(H, HOBJECT n_other) = 3',
    '$gc_slot_find(S.GC.BUFFER, HOBJECT n_other, 0) = (n_other_slot)',
    '$heap_count(HOBJECT n_other, $gc_nodes(S.GC.BUFFER)) = 1',
    r'$(n_token_slot < n_second_slot) /\ $(n_second_slot < n_leaf_slot) /\ $(n_leaf_slot < n_other_slot)',
    '$gc_slot_find(pgcplan.BUFFER, HOBJECT n_other, 0) = eps',
    '$lookup(S.ENV, $ptascii("otherCopy")) = eps',
    'S.POOLS = ppool :: ppool_tail*',
    'S_pool = S[.POOLS = ppool[.CONSTANTS = [PCONSTANT ([PCINDEX 0]) (PARRAY n_second)]] :: ppool_tail*]',
    f'~$gc_plain_captures(S_pool, {DISTINCT_CAPTURES})',
    '~$gc_ordinary_node(S_pool, HOBJECT n_closure)',
    'S_proxy = S[.OBJECTTABLES = S.OBJECTTABLES ++ [{OBJECT n_held, TABLE n_second}]]',
    '$gc_proxy(S_proxy, n_second)',
    f'~$gc_plain_captures(S_proxy, {DISTINCT_CAPTURES})',
    '~$gc_ordinary_node(S_proxy, HOBJECT n_closure)',
    f'~$gc_plain_captures(S[.ALLOCATIONS = $destruction_nodes_delete(S.ALLOCATIONS, [HARRAY n_second])], {DISTINCT_CAPTURES})',
    f'~$gc_plain_captures(S[.ALLOCATIONS = $destruction_nodes_delete(S.ALLOCATIONS, [HOBJECT n_other])], {DISTINCT_CAPTURES})',
    'S_immutable = S[.ARRAYS[n_second] = $array_empty()][.GC.IMMUTABLE = S.GC.IMMUTABLE ++ [n_second]]',
    '$gc_immutable_array(S_immutable, n_second)',
    f'~$gc_plain_captures(S_immutable, {DISTINCT_CAPTURES})',
    '~$gc_ordinary_node(S_immutable, HOBJECT n_closure)',
    'S_child = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS, n_other, [{DECL eps, NAME ($ptascii("back")), STATE PROP_VALUE (DIRECT (POBJECT n_held))}])]',
    '$node_children(S_child, HOBJECT n_other) = [HOBJECT n_held]',
    f'~$gc_plain_captures(S_child, {DISTINCT_CAPTURES})',
    '~$gc_ordinary_node(S_child, HOBJECT n_closure)',
]
for bad in ['DIRECT (PARRAY n_array)', 'DIRECT (POBJECT n_held)', 'ALIAS n_token_local_cell', 'INDIRECT n_held $ptascii("head")', 'DIRECT PUNDEFINED']:
    DISTINCT += [
        f'~$gc_plain_captures(S[.ARRAYS[n_second].ITEMS = [ENTRY (KINT 0) ({bad})]], {DISTINCT_CAPTURES})',
        f'~$gc_ordinary_node(S[.ARRAYS[n_second].ITEMS = [ENTRY (KINT 0) ({bad})]], HOBJECT n_closure)',
    ]

REPEATED_CAPTURES = '[DIRECT (PARRAY n_array), DIRECT (PINT 11), DIRECT (PARRAY n_array)]'
REPEATED = checks(REPEATED_CAPTURES, '[HARRAY n_array, HARRAY n_array]', [
    ('n_array', 'token', 4, '[HOBJECT n_leaf, HOBJECT n_leaf]', 2),
], 2, 0) + [
    f'$gc_capture_array_nodes({REPEATED_CAPTURES}) = [HARRAY n_array, HARRAY n_array]',
    'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_leaf)), ENTRY (KINT 1) (DIRECT (POBJECT n_leaf))]',
    '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)',
    'S.STORE[n_second_cell] = DEFINED (PARRAY n_array)',
    '$heap_edge_owners(HARRAY n_array, H.EDGES, [HOBJECT n_closure]) = 2',
    '$heap_count(HARRAY n_array, $closure_items_nodes([DIRECT (PARRAY n_array), DIRECT (PARRAY n_array)])) = 2',
    '$gc_slot_find(S.GC.BUFFER, HARRAY n_array, 0) = (n_token_slot)',
    '$heap_count(HARRAY n_array, $gc_nodes(S.GC.BUFFER)) = 1',
]

THREE_CAPTURES = '[DIRECT (POBJECT n_other), DIRECT (PARRAY n_third), DIRECT (PINT 11), DIRECT (PARRAY n_second), DIRECT (PARRAY n_array)]'
THREE = checks(THREE_CAPTURES, '[HOBJECT n_other, HARRAY n_third, HARRAY n_second, HARRAY n_array]', [
    ('n_array', 'token', 2, '[HOBJECT n_leaf]', 1),
    ('n_second', 'second', 2, '[HOBJECT n_leaf]', 1),
    ('n_third', 'third', 2, 'eps', 0),
], 2, 0, other=True) + [
    r'n_array =/= n_second /\ n_array =/= n_third /\ n_second =/= n_third',
    'n_leaf =/= n_other',
    f'$gc_capture_array_nodes({THREE_CAPTURES}) = [HARRAY n_third, HARRAY n_second, HARRAY n_array]',
    'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_leaf))]',
    'S.ARRAYS[n_second].ITEMS = [ENTRY (KSTRING $ptascii("shared")) (DIRECT (POBJECT n_leaf))]',
    'S.ARRAYS[n_third].ITEMS = [ENTRY (KSTRING $ptascii("value")) (DIRECT (PINT 17))]',
    '$heap_edge_owners(HOBJECT n_other, H.EDGES, [HARRAY n_array, HARRAY n_second, HARRAY n_third]) = 0',
    '$heap_edge_owners(HOBJECT n_other, H.EDGES, [HOBJECT n_closure]) = 1',
    '$heap_owners(H, HOBJECT n_other) = 2',
    r'$(n_token_slot < n_second_slot) /\ $(n_second_slot < n_third_slot) /\ $(n_third_slot < n_leaf_slot)',
    '~((HOBJECT n_other) <- $gc_nodes(S.GC.BUFFER))',
    '$lookup(psymboltable_global.ENV, $ptascii("third")) = eps',
    '$lookup(S.ENV, $ptascii("thirdCopy")) = eps',
]

CASES = {name: {'source': sources.PATHS[name].read_text(), 'stage': STAGE,
                 'checks': assertions, 'timeout': 240}
         for name, assertions in [('distinct-shared', DISTINCT),
                                  ('repeated-array', REPEATED),
                                  ('three-reordered', THREE)]}


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
