#!/usr/bin/env python3
"""Reached reference captures separate wrapper owners from payload edges."""
import argparse

import gc_caller_materialized_state as ordinary
import gc_reference_capture_sources as sources
import shutdown_state_review as runner


STAGE = 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* -- if pgccall.PASS = 0 -- if S.GC.NEXT = 2'


def common(captures, children, cells):
    result = [
        *ordinary.COMMON,
        'pcallcontext.TARGET = CLOSURE_TARGET n_closure',
        'pcallcontext.INSTANCE = (n_closure)',
        'pcallcontext.RECEIVER = eps',
        'pcallcontext.WRAPPER = eps',
        f'S.OBJECTS[n_closure] = REALCLOSURE porigin_template ({captures}) eps',
        f'$closure_items_nodes({captures}) = {children}',
        f'$node_children(S, HOBJECT n_closure) = {children}',
        f'$gc_trace_children(S, HOBJECT n_closure) = {children}',
        f'$gc_reference_captures(S, {captures}, false)',
        f'~$gc_direct_captures({captures})',
        'H_ref = $heap_graph(S)',
        f'pnode_ref* = $heap_reach($closure_items_nodes({captures}), eps, H_ref.EDGES)',
        'pnode_pool* = $heap_reach($pools_nodes(S.POOLS), eps, H_ref.EDGES)',
        '$gc_reference_graph_nodes(S, pnode_ref*, H_ref.EDGES, pnode_pool*)',
        '$gc_ordinary_node(S, HOBJECT n_closure)',
        '$gc_ordinary_nodes(S, S.ALLOCATIONS)',
        '$closure_callable(S, n_closure)',
        '$gc_materialized_caller_target(S, CLOSURE_TARGET n_closure, pcallcontext.CALLSITE)',
        '$heap_owners(H_ref, HOBJECT n_closure) = 2',
        '$call_context_roots(S.CURRENT) = [HOBJECT n_closure]',
        'S.GLOBALTABLE = (psymboltable_global)',
        '$lookup(psymboltable_global.ENV, $ptascii("collector")) = (n_collector_cell)',
        'S.STORE[n_collector_cell] = DEFINED (POBJECT n_closure)',
        '$lookup(S.ENV, $ptascii("copy")) = eps',
        'S_unrooted = S[.CURRENT = (pcallcontext[.INSTANCE = eps])]',
        '~((HOBJECT n_closure) <- $machine_roots(S_unrooted))',
        '~$gc_ordinary_node(S_unrooted, HOBJECT n_closure)',
        '~$gc_ordinary_node(S[.GC.ACTIVE = eps], HOBJECT n_closure)',
        '~$gc_ordinary_node(S[.GC.ACTIVE = (pgccall[.CALLER = eps])], HOBJECT n_closure)',
        '~$gc_ordinary_node(S[.SOURCES = eps], HOBJECT n_closure)',
        '~$gc_reference_captures(S, [DIRECT PNULL], false)',
        '~$gc_reference_captures(S, [UNINITIALIZED], false)',
        '~$gc_reference_captures(S, [DIRECT PUNDEFINED], false)',
        '~$gc_reference_captures(S, [INDIRECT n_held $ptascii("head")], false)',
        'n_bad_cell = |S.STORE|',
        '~$gc_reference_captures(S, [ALIAS n_bad_cell], false)',
        'S_done = $drive(S, 2000)',
        'S_done.COMPLETION = NORMAL',
        'H_done = $heap_graph(S_done)',
        '$heap_valid(H_done)',
        '~((HOBJECT n_closure) <- S_done.ALLOCATIONS)',
    ]
    for cell, local, owners, capture_edges, local_roots in cells:
        result += [
            f'$lookup(S.ENV, $ptascii("{local}")) = ({cell})',
            f'{cell} <- S.REFCELLS',
            f'(HCELL {cell}) <- S.ALLOCATIONS',
            f'$heap_count(HCELL {cell}, S.ALLOCATIONS) = 1',
            f'$ordinary_reference_value(S, {cell}) = (pvalue_payload)',
            f'$gc_reference_payload_valid(S, pvalue_payload)',
            f'$node_children(S, HCELL {cell}) = $value_nodes(pvalue_payload)',
            f'$gc_trace_children(S, HCELL {cell}) = $value_nodes(pvalue_payload)',
            f'$propref_at(S.PROPREFS, {cell}) = eps',
            f'$reference_coercion_at(S.REFCOERCIONS, {cell}) = eps',
            f'$parameter_backing_at(S.PARAMETERBACKINGS, {cell}) = eps',
            f'$heap_owners(H_ref, HCELL {cell}) = {owners}',
            f'$heap_edge_owners(HCELL {cell}, H_ref.EDGES, [HOBJECT n_closure]) = {capture_edges}',
            f'$heap_count(HCELL {cell}, $environment_nodes(S.ENV)) = {local_roots}',
            f'$gc_slot_find(S.GC.BUFFER, HCELL {cell}, 0) = eps',
            f'~((HCELL {cell}) <- pnode_pool*)',
            f'~((HCELL {cell}) <- S_done.ALLOCATIONS)',
            f'$heap_owners(H_done, HCELL {cell}) = 0',
        ]
    return result


def refusal(label, mutation, captures, graph=True):
    result = [
        f'S_{label} = {mutation}',
        f'$closure_callable(S_{label}, n_closure)',
        f'$gc_materialized_caller_target(S_{label}, CLOSURE_TARGET n_closure, pcallcontext.CALLSITE)',
        f'~$gc_reference_captures(S_{label}, {captures}, false)',
        f'~$gc_ordinary_node(S_{label}, HOBJECT n_closure)',
    ]
    if graph:
        result += [
            f'H_{label} = $heap_graph(S_{label})',
            f'pnode_bad_{label}* = $heap_reach($closure_items_nodes({captures}), eps, H_{label}.EDGES)',
            f'~$gc_reference_graph_nodes(S_{label}, pnode_bad_{label}*, H_{label}.EDGES, $heap_reach($pools_nodes(S_{label}.POOLS), eps, H_{label}.EDGES))',
        ]
    return result


def array_case(shared):
    captures = '[ALIAS n_first, ALIAS n_first]' if shared else '[ALIAS n_first, ALIAS n_second]'
    children = '[HCELL n_first, HCELL n_first]' if shared else '[HCELL n_first, HCELL n_second]'
    cells = [('n_first', 'token', 4, 2, 2)] if shared else [
        ('n_first', 'token', 2, 1, 1), ('n_second', 'other', 2, 1, 1)]
    checks = common(captures, children, cells) + [
        'S.STORE[n_first] = DEFINED (PARRAY n_array)',
        'pvalue_payload = PARRAY n_array',
        '$lookup(S.ENV, $ptascii("other")) = (n_first)' if shared else
        'S.STORE[n_second] = DEFINED (PARRAY n_array)',
        '$lookup(psymboltable_global.ENV, $ptascii("token")) = eps',
        '$lookup(psymboltable_global.ENV, $ptascii("other")) = eps',
        '$lookup(psymboltable_global.ENV, $ptascii("leaf")) = eps',
        '$lookup(psymboltable_global.ENV, $ptascii("weakLeaf")) = (n_weakleaf_cell)',
        'S.STORE[n_weakleaf_cell] = DEFINED (POBJECT n_weakleaf)',
        'S.OBJECTS[n_weakleaf] = WEAKREFERENCE (n_leaf)',
        'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_leaf)), ENTRY (KINT 1) (DIRECT (POBJECT n_leaf))]',
        'S.OBJECTS[n_leaf] = STDINSTANCE',
        '$node_children(S, HOBJECT n_leaf) = eps',
        '$gc_trace_children(S, HOBJECT n_leaf) = eps',
        '$node_children(S, HARRAY n_array) = [HOBJECT n_leaf, HOBJECT n_leaf]',
        '$gc_trace_children(S, HARRAY n_array) = [HOBJECT n_leaf, HOBJECT n_leaf]',
        '$heap_edge_owners(HARRAY n_array, H_ref.EDGES, [HCELL n_first]) = 1',
        f'$heap_owners(H_ref, HARRAY n_array) = {1 if shared else 2}',
        '$heap_edge_owners(HOBJECT n_leaf, H_ref.EDGES, [HARRAY n_array]) = 2',
        '$heap_owners(H_ref, HOBJECT n_leaf) = 2',
        '$node_children(S, HOBJECT n_weakleaf) = eps',
        '$gc_slot_find(S.GC.BUFFER, HARRAY n_array, 0) = (n_array_slot)',
        '$gc_slot_find(S.GC.BUFFER, HOBJECT n_leaf, 0) = (n_leaf_slot)',
        '$(n_array_slot < n_leaf_slot)',
        '$heap_count(HARRAY n_array, $gc_nodes(S.GC.BUFFER)) = 1',
        '$heap_count(HOBJECT n_leaf, $gc_nodes(S.GC.BUFFER)) = 1',
        '$gc_slot_find(pgcplan.BUFFER, HARRAY n_array, 0) = eps',
        '$gc_slot_find(pgcplan.BUFFER, HOBJECT n_leaf, 0) = eps',
        '~((HARRAY n_array) <- $gc_white(H, $gc_eligible_nodes(pgcplan.BUFFER)))',
        '~((HOBJECT n_leaf) <- $gc_white(H, $gc_eligible_nodes(pgcplan.BUFFER)))',
        '$lookup(S.ENV, $ptascii("otherCopy")) = eps',
        '$lookup(S.ENV, $ptascii("leafCopy")) = eps',
        'pgc_empty = S.GC[.BUFFER = eps][.FREE = eps]',
        'pgc_payload = $gc_decrement(S, pgc_empty, HCELL n_first)',
        '$gc_nodes(pgc_payload.BUFFER) = [HARRAY n_array]',
        '$gc_nodes($gc_decrement(S, pgc_payload, HCELL n_first).BUFFER) = [HARRAY n_array]',
        '~((HARRAY n_array) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_leaf) <- S_done.ALLOCATIONS)',
        '$heap_edge_owners(HARRAY n_array, H_done.EDGES, [HCELL n_first]) = 0',
    ]
    if not shared:
        checks += ['n_first =/= n_second', '$heap_edge_owners(HARRAY n_array, H_ref.EDGES, [HCELL n_second]) = 1']
    checks += refusal('debt', 'S[.LITERALREFDEBTS = S.LITERALREFDEBTS ++ [n_first]]', captures)
    checks += refusal('source', 'S[.PROPREFS = S.PROPREFS ++ [{CELL n_first, SOURCES eps}]]', captures)
    checks += [
        'S_alias = S[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_first)]]',
        '$closure_callable(S_alias, n_closure)',
        '$gc_materialized_caller_target(S_alias, CLOSURE_TARGET n_closure, pcallcontext.CALLSITE)',
        f'$gc_reference_captures(S_alias, {captures}, false)',
        'H_alias = $heap_graph(S_alias)',
        f'pnode_bad_alias* = $heap_reach($closure_items_nodes({captures}), eps, H_alias.EDGES)',
        '~$gc_reference_graph_nodes(S_alias, pnode_bad_alias*, H_alias.EDGES, $heap_reach($pools_nodes(S_alias.POOLS), eps, H_alias.EDGES))',
        '~$gc_ordinary_node(S_alias, HOBJECT n_closure)',
    ]
    return checks


STRING_CAPTURES = '[ALIAS n_value]'
STRING = common(STRING_CAPTURES, '[HCELL n_value]', [('n_value', 'v', 2, 1, 1)]) + [
    'S.STORE[n_value] = DEFINED (PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("head-tail-inside")))',
    'pvalue_payload = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("head-tail-inside"))',
    '$string_carrier_valid(S, pvalue_payload)',
    '$(n_string < |S.STRINGDATA|)',
    'S.STRINGDATA[n_string] = $ptascii("head-tail-inside")',
    '$lookup(psymboltable_global.ENV, $ptascii("v")) = (n_new_value)',
    'n_new_value =/= n_value',
    'S.STORE[n_new_value] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("new-global")))',
    '~(n_new_value <- S.REFCELLS)',
    '$heap_owners(H_ref, HCELL n_new_value) = 1',
    '$node_children(S, HCELL n_value) = eps',
    '$gc_trace_children(S, HCELL n_value) = eps',
    'pgc_empty = S.GC[.BUFFER = eps][.FREE = eps]',
    '$gc_decrement(S, pgc_empty, HCELL n_value) = pgc_empty',
    'n_bad_string = |S.STRINGDATA|',
]
STRING += refusal('string_oob', 'S[.STORE[n_value] = DEFINED (PSTRING_CARRIER (REQUEST_STRING n_bad_string) ($ptascii("head-tail-inside")))]', STRING_CAPTURES)
STRING += refusal('string_bytes', 'S[.STORE[n_value] = DEFINED (PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("changed")))]', STRING_CAPTURES)
STRING += refusal('string_raw', 'S[.STORE[n_value] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([256]))]', STRING_CAPTURES)

CASES = {name: {'source': sources.PATHS[name].read_text(), 'stage': STAGE,
                 'checks': checks, 'timeout': 240}
         for name, checks in [('shared-cell', array_case(True)),
                              ('distinct-cells', array_case(False)),
                              ('request-string-rebind', STRING)]}
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
