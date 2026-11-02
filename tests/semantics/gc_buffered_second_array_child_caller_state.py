#!/usr/bin/env python3
"""Reached collection through one buffered array with both childless entries buffered."""
import argparse

import gc_caller_materialized_state as ordinary
import gc_buffered_second_array_child_caller_sources as sources
import shutdown_state_review as runner


CASES = {
    'buffered-second-array-child-direct-caller': {
        'source': sources.family.CASES['buffered-second-array-child-direct-caller'].decode(),
        'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* '
                 '-- if pgccall.PASS = 0 -- if S.GC.NEXT = 3',
        'checks': [
            *ordinary.COMMON,
            'pcallcontext.TARGET = CLOSURE_TARGET n_closure',
            'pcallcontext.INSTANCE = (n_closure)',
            'pcallcontext.RECEIVER = eps',
            'pcallcontext.WRAPPER = eps',
            'S.OBJECTS[n_closure] = REALCLOSURE porigin_template ([DIRECT (PARRAY n_array)]) eps',
            '(HOBJECT n_closure) <- S.ALLOCATIONS',
            '(HARRAY n_array) <- S.ALLOCATIONS',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_first)), ENTRY (KINT 1) (DIRECT (POBJECT n_second))]',
            'n_first =/= n_second',
            '(HOBJECT n_first) <- S.ALLOCATIONS',
            'S.OBJECTS[n_first] = STDINSTANCE',
            '(HOBJECT n_second) <- S.ALLOCATIONS',
            'S.OBJECTS[n_second] = STDINSTANCE',
            '~$gc_immutable_array(S, n_array)',
            '$gc_possible_root(S, HARRAY n_array)',
            '$target_function(S, CLOSURE_TARGET n_closure) = (pfunction_closure)',
            '$function_at(S.CLOSURETEMPLATES, porigin_template) = (pfunction_closure)',
            '$node_children(S, HOBJECT n_closure) = [HARRAY n_array]',
            '$node_children(S, HARRAY n_array) = [HOBJECT n_first, HOBJECT n_second]',
            '$gc_trace_children(S, HARRAY n_array) = [HOBJECT n_first, HOBJECT n_second]',
            '$node_children(S, HOBJECT n_first) = eps',
            '$gc_trace_children(S, HOBJECT n_first) = eps',
            '$node_children(S, HOBJECT n_second) = eps',
            '$gc_trace_children(S, HOBJECT n_second) = eps',
            '(HARRAY n_array) <- $gc_nodes(S.GC.BUFFER)',
            '$gc_slot_find(S.GC.BUFFER, HARRAY n_array, 0) = (n_array_slot)',
            '(HOBJECT n_first) <- $gc_nodes(S.GC.BUFFER)',
            '$gc_slot_find(S.GC.BUFFER, HOBJECT n_first, 0) = (n_first_slot)',
            '$(n_array_slot < n_first_slot)',
            '(HOBJECT n_second) <- $gc_nodes(S.GC.BUFFER)',
            '$gc_slot_find(S.GC.BUFFER, HOBJECT n_second, 0) = (n_second_slot)',
            '$(n_first_slot < n_second_slot)',
            '$gc_buffer_valid(S, S.GC)',
            '$gc_slot_find(pgcplan.BUFFER, HARRAY n_array, 0) = eps',
            '$gc_slot_find(pgcplan.BUFFER, HOBJECT n_first, 0) = eps',
            '$gc_slot_find(pgcplan.BUFFER, HOBJECT n_second, 0) = eps',
            '$gc_ordinary_node(S, HOBJECT n_closure)',
            '$gc_ordinary_node(S, HARRAY n_array)',
            '$gc_ordinary_node(S, HOBJECT n_first)',
            '$gc_ordinary_node(S, HOBJECT n_second)',
            '~$gc_ordinary_node(S[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_first)), ENTRY (KINT 1) (DIRECT (POBJECT n_first))]], HOBJECT n_closure)',
            '$gc_ordinary_nodes(S, S.ALLOCATIONS)',
            '~$gc_ordinary_node(S[.GC.ACTIVE = eps], HOBJECT n_closure)',
            '~$gc_ordinary_node(S[.GC.ACTIVE = (pgccall[.CALLER = eps])], HOBJECT n_closure)',
            '~$gc_ordinary_node(S[.OBJECTS[n_wh] = REALCLOSURE porigin_template eps eps], HOBJECT n_wh)',
            '$dynamic_site(S, (porigin_outer_call))',
            '$dynamic_fixed_name(S, porigin_outer_call) = eps',
            '$gc_materialized_caller_target(S, CLOSURE_TARGET n_closure, (porigin_outer_call))',
            '$call_context_roots(S.CURRENT) = [HOBJECT n_closure]',
            'S.GLOBALTABLE = (psymboltable_global)',
            '$lookup(psymboltable_global.ENV, $ptascii("collector")) = (n_collector_cell)',
            'S.STORE[n_collector_cell] = DEFINED (POBJECT n_closure)',
            '(HCELL n_collector_cell) <- $machine_roots(S)',
            '$heap_owners($heap_graph(S), HOBJECT n_closure) = 2',
            '$lookup(psymboltable_global.ENV, $ptascii("token")) = (n_token_global_cell)',
            'S.STORE[n_token_global_cell] = DEFINED (PARRAY n_array)',
            '$lookup(psymboltable_global.ENV, $ptascii("leaf")) = (n_first_global_cell)',
            'S.STORE[n_first_global_cell] = DEFINED (POBJECT n_first)',
            '$lookup(psymboltable_global.ENV, $ptascii("leaf2")) = (n_second_global_cell)',
            'S.STORE[n_second_global_cell] = DEFINED (POBJECT n_second)',
            '$lookup(S.ENV, $ptascii("token")) = (n_token_local_cell)',
            '$lookup(S.ENV, $ptascii("copy")) = eps',
            '$lookup(S.ENV, $ptascii("leafCopy")) = eps',
            '$lookup(S.ENV, $ptascii("leafCopy2")) = eps',
            'S.STORE[n_token_local_cell] = DEFINED (PARRAY n_array)',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_first) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_second) = 2',
            '(HARRAY n_array) <- $heap_reach([HOBJECT n_closure], eps, H.EDGES)',
            '(HOBJECT n_first) <- $heap_reach([HOBJECT n_closure], eps, H.EDGES)',
            '(HOBJECT n_second) <- $heap_reach([HOBJECT n_closure], eps, H.EDGES)',
            '~((HARRAY n_array) <- $gc_white(H, $gc_eligible_nodes(pgcplan.BUFFER)))',
            '~((HOBJECT n_first) <- $gc_white(H, $gc_eligible_nodes(pgcplan.BUFFER)))',
            '~((HOBJECT n_second) <- $gc_white(H, $gc_eligible_nodes(pgcplan.BUFFER)))',
            '$lookup(S.ENV, $ptascii("held")) = (n_held_cell)',
            'S.STORE[n_held_cell] = DEFINED (POBJECT n_held)',
            '(HCELL n_held_cell) <- $machine_roots(S)',
            '(HOBJECT n_held) <- $heap_reach($environment_nodes(S.ENV), eps, H.EDGES)',
            '$heap_owners($heap_graph(S), HOBJECT n_held) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_drop) = 1',
            '~$gc_materialized_caller_target(S, CLOSURE_TARGET n_closure, (pgccall.CALL.SITE))',
            '~$gc_materialized_caller_target(S[.SOURCES = eps], CLOSURE_TARGET n_closure, (porigin_outer_call))',
            '~$gc_materialized_caller_target(S, CLOSURE_TARGET n_wh, (porigin_outer_call))',
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
