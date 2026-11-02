#!/usr/bin/env python3
"""Reached finite scalar captures and one-level array children of a live GC caller."""
import argparse

import gc_caller_materialized_state as ordinary
import gc_finite_capture_sources as sources
import gc_scalar_array_caller_state as scalar
import shutdown_state_review as runner


old_order = 'REALCLOSURE porigin_template ([DIRECT (PINT 11), DIRECT (PARRAY n_array)]) eps'
new_order = 'REALCLOSURE porigin_template ([DIRECT (PARRAY n_array), DIRECT (PINT 11)]) eps'
reversed_checks = [check.replace(old_order, new_order)
                   for check in scalar.CASES['scalar-array-captured-direct-caller']['checks']]

CASES = {
    'finite-reversed-captures': {
        'source': sources.family.CASES['finite-reversed-captures'].decode(),
        'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* '
                 '-- if pgccall.PASS = 0 -- if S.GC.NEXT = 2',
        'checks': [
            *reversed_checks,
            '$gc_one_array_capture([DIRECT (PARRAY n_array), DIRECT (PINT 11)], n_array)',
            '~$gc_legacy_array_shape(S, [DIRECT (PARRAY n_array), DIRECT (PINT 11)], n_array)',
            '$gc_plain_array_entries(S, S.ARRAYS[n_array].ITEMS)',
        ], 'timeout': 240,
    },
    'finite-three-distinct-mixed-key': {
        'source': sources.family.CASES['finite-three-distinct-mixed-key'].decode(),
        'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* '
                 '-- if pgccall.PASS = 0 -- if S.GC.NEXT = 2',
        'checks': [
            *ordinary.COMMON,
            'pcallcontext.TARGET = CLOSURE_TARGET n_closure',
            'pcallcontext.INSTANCE = (n_closure)',
            'pcallcontext.RECEIVER = eps',
            'pcallcontext.WRAPPER = eps',
            'S.OBJECTS[n_closure] = REALCLOSURE porigin_template ([DIRECT (PARRAY n_array), DIRECT (PINT 11)]) eps',
            '(HOBJECT n_closure) <- S.ALLOCATIONS',
            '(HARRAY n_array) <- S.ALLOCATIONS',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_first)), ENTRY (KSTRING $ptascii("middle")) (DIRECT (POBJECT n_middle)), ENTRY (KINT 1) (DIRECT (POBJECT n_second)), ENTRY (KSTRING $ptascii("tag")) (DIRECT (PINT 7))]',
            'n_first =/= n_middle /\\ n_first =/= n_second /\\ n_middle =/= n_second',
            '(HOBJECT n_first) <- S.ALLOCATIONS',
            '(HOBJECT n_middle) <- S.ALLOCATIONS',
            '(HOBJECT n_second) <- S.ALLOCATIONS',
            'S.OBJECTS[n_first] = STDINSTANCE',
            'S.OBJECTS[n_middle] = STDINSTANCE',
            'S.OBJECTS[n_second] = STDINSTANCE',
            '~$gc_immutable_array(S, n_array)',
            '~$gc_proxy(S, n_array)',
            '~((HARRAY n_array) <- $heap_reach($pools_nodes(S.POOLS), eps, $heap_graph(S).EDGES))',
            '$gc_one_array_capture([DIRECT (PARRAY n_array), DIRECT (PINT 11)], n_array)',
            '~$gc_legacy_array_shape(S, [DIRECT (PARRAY n_array), DIRECT (PINT 11)], n_array)',
            '$gc_plain_array_entries(S, S.ARRAYS[n_array].ITEMS)',
            '$node_children(S, HOBJECT n_closure) = [HARRAY n_array]',
            '$node_children(S, HARRAY n_array) = [HOBJECT n_first, HOBJECT n_middle, HOBJECT n_second]',
            '$gc_trace_children(S, HARRAY n_array) = [HOBJECT n_first, HOBJECT n_middle, HOBJECT n_second]',
            '$heap_unique($node_children(S, HARRAY n_array))',
            '$node_children(S, HOBJECT n_first) = eps',
            '$node_children(S, HOBJECT n_middle) = eps',
            '$node_children(S, HOBJECT n_second) = eps',
            '$gc_trace_children(S, HOBJECT n_first) = eps',
            '$gc_trace_children(S, HOBJECT n_middle) = eps',
            '$gc_trace_children(S, HOBJECT n_second) = eps',
            '(HARRAY n_array) <- $gc_nodes(S.GC.BUFFER)',
            '$gc_slot_find(S.GC.BUFFER, HARRAY n_array, 0) = (n_array_slot)',
            '(HOBJECT n_first) <- $gc_nodes(S.GC.BUFFER)',
            '$gc_slot_find(S.GC.BUFFER, HOBJECT n_first, 0) = (n_first_slot)',
            '$(n_array_slot < n_first_slot)',
            '~((HOBJECT n_middle) <- $gc_nodes(S.GC.BUFFER))',
            '~((HOBJECT n_second) <- $gc_nodes(S.GC.BUFFER))',
            '$gc_buffer_valid(S, S.GC)',
            '$gc_slot_find(pgcplan.BUFFER, HARRAY n_array, 0) = eps',
            '$gc_slot_find(pgcplan.BUFFER, HOBJECT n_first, 0) = eps',
            '$gc_ordinary_node(S, HOBJECT n_closure)',
            '$gc_ordinary_nodes(S, S.ALLOCATIONS)',
            'S.OBJECTS[n_held] = INSTANCE porigin_held',
            'S.GLOBALTABLE = (psymboltable_global)',
            '$lookup(psymboltable_global.ENV, $ptascii("collector")) = (n_collector_cell)',
            'S.STORE[n_collector_cell] = DEFINED (POBJECT n_closure)',
            '~$gc_ordinary_node(S[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_first)), ENTRY (KSTRING $ptascii("middle")) (DIRECT (POBJECT n_middle)), ENTRY (KINT 1) (DIRECT (POBJECT n_first)), ENTRY (KSTRING $ptascii("tag")) (DIRECT (PINT 7))]], HOBJECT n_closure)',
            '~$gc_ordinary_node(S[.OBJECTS[n_closure] = REALCLOSURE porigin_template ([DIRECT (PARRAY n_array), DIRECT (PINT 11), DIRECT (POBJECT n_first)]) eps], HOBJECT n_closure)',
            '~$gc_plain_array_entries(S, [ENTRY (KINT 0) (ALIAS n_collector_cell)])',
            '~$gc_plain_array_entries(S, [ENTRY (KINT 0) (INDIRECT n_held $ptascii("head"))])',
            '~$gc_plain_array_entries(S, [ENTRY (KINT 0) (DIRECT (POBJECT n_held))])',
            '~$gc_plain_array_entries(S, [ENTRY (KINT 0) (DIRECT (PARRAY n_array))])',
            '~$gc_plain_array_entries(S, [ENTRY (KINT 0) (DIRECT PUNDEFINED)])',
            '~$gc_one_array_capture([DIRECT (PARRAY n_array), DIRECT (POBJECT n_held)], n_array)',
            '~$gc_one_array_capture([DIRECT (PARRAY n_array), DIRECT (PARRAY n_array)], n_array)',
            '~$gc_one_array_capture([DIRECT PUNDEFINED, DIRECT (PARRAY n_array)], n_array)',
            'S_pool = S[.POOLS = {UNIT 999, CONSTANTS [PCONSTANT ([PCINDEX 0]) (PARRAY n_array)]} :: S.POOLS]',
            '(HARRAY n_array) <- $heap_reach($pools_nodes(S_pool.POOLS), eps, $heap_graph(S_pool).EDGES)',
            '~$gc_ordinary_node(S_pool, HOBJECT n_closure)',
            'S_proxy = S[.OBJECTTABLES = S.OBJECTTABLES ++ [{OBJECT n_held, TABLE n_array}]]',
            '$gc_proxy(S_proxy, n_array)',
            '~$gc_ordinary_node(S_proxy, HOBJECT n_closure)',
            '~$gc_ordinary_node(S[.GC.ACTIVE = eps], HOBJECT n_closure)',
            '~$gc_ordinary_node(S[.GC.ACTIVE = (pgccall[.CALLER = eps])], HOBJECT n_closure)',
            '$dynamic_site(S, (porigin_outer_call))',
            '$gc_materialized_caller_target(S, CLOSURE_TARGET n_closure, (porigin_outer_call))',
            '$call_context_roots(S.CURRENT) = [HOBJECT n_closure]',
            '$lookup(psymboltable_global.ENV, $ptascii("token")) = (n_token_global_cell)',
            'S.STORE[n_token_global_cell] = DEFINED (PARRAY n_array)',
            '$lookup(S.ENV, $ptascii("token")) = (n_token_local_cell)',
            'S.STORE[n_token_local_cell] = DEFINED (PARRAY n_array)',
            '$heap_owners($heap_graph(S), HOBJECT n_closure) = 2',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_first) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_middle) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_second) = 2',
            '(HARRAY n_array) <- $heap_reach([HOBJECT n_closure], eps, H.EDGES)',
            '(HOBJECT n_first) <- $heap_reach([HOBJECT n_closure], eps, H.EDGES)',
            '(HOBJECT n_middle) <- $heap_reach([HOBJECT n_closure], eps, H.EDGES)',
            '(HOBJECT n_second) <- $heap_reach([HOBJECT n_closure], eps, H.EDGES)',
            '~((HARRAY n_array) <- $gc_white(H, $gc_eligible_nodes(pgcplan.BUFFER)))',
            '~((HOBJECT n_first) <- $gc_white(H, $gc_eligible_nodes(pgcplan.BUFFER)))',
            '~((HOBJECT n_middle) <- $gc_white(H, $gc_eligible_nodes(pgcplan.BUFFER)))',
            '~((HOBJECT n_second) <- $gc_white(H, $gc_eligible_nodes(pgcplan.BUFFER)))',
            '$lookup(S.ENV, $ptascii("held")) = (n_held_cell)',
            'S.STORE[n_held_cell] = DEFINED (POBJECT n_held)',
            '$heap_owners($heap_graph(S), HOBJECT n_held) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_drop) = 1',
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
