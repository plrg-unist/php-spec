#!/usr/bin/env python3
"""Reached materialized collection from explicit real Closure::__invoke."""
import argparse

import gc_caller_materialized_state as ordinary
import gc_closure_invoke_sources as sources
import shutdown_state_review as runner


CASES = {
    'explicit-real-closure-invoke-caller': {
        'source': sources.family.CASES['explicit-real-closure-invoke'].decode(),
        'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* '
                 '-- if pgccall.PASS = 0 -- if S.GC.NEXT = 2',
        'checks': [
            *ordinary.COMMON,
            'pcallcontext.TARGET = CLOSURE_TARGET n_closure',
            'pcallcontext.INSTANCE = (n_closure)',
            'pcallcontext.RECEIVER = eps',
            'pcallcontext.WRAPPER = (pnamedargs)',
            'pcallcontext.HOLES = eps',
            'pnamedargs.SLOTS = eps',
            'pnamedargs.NAMED = eps',
            'S.OBJECTS[n_closure] = REALCLOSURE porigin_template eps eps',
            '(HOBJECT n_closure) <- S.ALLOCATIONS',
            '$target_function(S, CLOSURE_TARGET n_closure) = (pfunction_closure)',
            '$function_at(S.CLOSURETEMPLATES, porigin_template) = (pfunction_closure)',
            '$function_deprecated(S, pfunction_closure) = NO_DEPRECATED',
            '$node_children(S, HOBJECT n_closure) = eps',
            '$wrapper_site(S, CLOSURE_TARGET n_closure, pcallcontext.CALLSITE)',
            '$wrapper_receiver_roots(pcallcontext) = [HOBJECT n_closure]',
            '$call_receiver_roots(pcallcontext) = eps',
            '$call_context_roots(S.CURRENT) = [HOBJECT n_closure, HOBJECT n_closure]',
            '$gc_materialized_caller_target(S, CLOSURE_TARGET n_closure, (porigin_outer_call))',
            '$gc_ordinary_node(S, HOBJECT n_closure)',
            '$gc_ordinary_nodes(S, S.ALLOCATIONS)',
            '~$gc_ordinary_node(S[.GC.ACTIVE = eps], HOBJECT n_closure)',
            '~$gc_ordinary_node(S[.GC.ACTIVE = (pgccall[.CALLER = eps])], HOBJECT n_closure)',
            '~$gc_ordinary_node(S[.OBJECTS[n_wh] = REALCLOSURE porigin_template eps eps], HOBJECT n_wh)',
            'S.GLOBALTABLE = (psymboltable_global)',
            '$lookup(psymboltable_global.ENV, $ptascii("collector")) = (n_collector_cell)',
            'S.STORE[n_collector_cell] = DEFINED (POBJECT n_closure)',
            '(HCELL n_collector_cell) <- $machine_roots(S)',
            '$heap_owners($heap_graph(S), HOBJECT n_closure) = 3',
            '$lookup(S.ENV, $ptascii("held")) = (n_held_cell)',
            'S.STORE[n_held_cell] = DEFINED (POBJECT n_held)',
            '(HCELL n_held_cell) <- $machine_roots(S)',
            '(HOBJECT n_held) <- $heap_reach($environment_nodes(S.ENV), eps, H.EDGES)',
            '$heap_owners($heap_graph(S), HOBJECT n_held) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_drop) = 1',
            '~$gc_materialized_caller_target(S, CLOSURE_TARGET n_closure, (pgccall.CALL.SITE))',
            '~$gc_materialized_caller_target(S[.SOURCES = eps], CLOSURE_TARGET n_closure, (porigin_outer_call))',
            '~$gc_materialized_caller_target(S[.OBJECTS[n_closure] = NAMEDCLOSURE porigin_template], CLOSURE_TARGET n_closure, (porigin_outer_call))',
            '~$gc_materialized_caller_target(S, CLOSURE_TARGET n_wh, (porigin_outer_call))',
            '~$gc_materialized_caller(S, (pcallcontext[.WRAPPER = eps]))',
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
