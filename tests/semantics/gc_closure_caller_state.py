#!/usr/bin/env python3
"""Reached materialized collection in a direct real-Closure call."""
import argparse

import gc_caller_materialized_state as ordinary
import gc_closure_caller_sources as sources
import shutdown_state_review as runner


CASES = {
    'direct-real-closure-caller': {
        'source': sources.family.CASES['real-closure-caller'].decode(),
        'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* '
                 '-- if pgccall.PASS = 0 -- if S.GC.NEXT = 2',
        'checks': [
            *ordinary.COMMON,
            'pcallcontext.TARGET = CLOSURE_TARGET n_closure',
            'pcallcontext.INSTANCE = (n_closure)',
            'pcallcontext.RECEIVER = eps',
            'S.OBJECTS[n_closure] = REALCLOSURE porigin_template pitem* pstaticcell*',
            '(HOBJECT n_closure) <- S.ALLOCATIONS',
            '$target_function(S, CLOSURE_TARGET n_closure) = (pfunction_closure)',
            '$function_at(S.CLOSURETEMPLATES, porigin_template) = (pfunction_closure)',
            'S.GC.ACTIVE = (pgccall)',
            '$gc_ordinary_node(S, HOBJECT n_closure)',
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
            '$lookup(S.ENV, $ptascii("held")) = (n_held_cell)',
            'S.STORE[n_held_cell] = DEFINED (POBJECT n_held)',
            '(HCELL n_held_cell) <- $machine_roots(S)',
            '(HOBJECT n_held) <- $heap_reach($environment_nodes(S.ENV), eps, H.EDGES)',
            '$heap_owners($heap_graph(S), HOBJECT n_held) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_drop) = 1',
            '~$gc_materialized_caller_target(S, CLOSURE_TARGET n_closure, (pgccall.CALL.SITE))',
            '~$gc_materialized_caller_target(S[.OBJECTS[n_closure] = NAMEDCLOSURE porigin_template], CLOSURE_TARGET n_closure, (porigin_outer_call))',
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
