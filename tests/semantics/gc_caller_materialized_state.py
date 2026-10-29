#!/usr/bin/env python3
"""Reached ordinary caller roots and fresh materialized callback authority."""
import argparse

import gc_caller_materialized_sources as sources
import shutdown_state_review as runner


FUNCTION = sources.family.CASES['function-local-protects-sibling'].decode()
METHOD = sources.family.CASES['method-receiver-protects-sibling'].decode()

COMMON = [
    'S.CURRENT = (pcallcontext)',
    'pgccall.CALLER = (pcallcontext)',
    'S.FRAMES = [pframe_global]',
    'pframe_global.CONTEXT = eps',
    'pframe_global.LOCALS = eps',
    '$call_current_valid(S)',
    '$gc_materialized_callback_context(S)',
    '$gc_materialized_caller(S, (pcallcontext))',
    '$gc_materialized_caller_frames(S, S.FRAMES)',
    '$gc_materialized_caller_site(S, S.CURRENT, pgccall.CALL.SITE)',
    '$gc_callback_caller_valid(S, pgccall)',
    'pgccall.COUNT_SOURCE = (pgccountsource)',
    '$gc_callback_count_image(pgccountsource)',
    '$gc_scope_valid(S, pgccall)',
    '$lookup(S.ENV, $ptascii("wh")) = (n_wh_cell)',
    'S.STORE[n_wh_cell] = DEFINED (POBJECT n_wh)',
    'S.OBJECTS[n_wh] = WEAKREFERENCE (n_held)',
    '$lookup(S.ENV, $ptascii("wd")) = (n_wd_cell)',
    'S.STORE[n_wd_cell] = DEFINED (POBJECT n_wd)',
    'S.OBJECTS[n_wd] = WEAKREFERENCE (n_drop)',
    'pgcplan = $gc_plan(S, pgccall)',
    'pgcplan.WEAK = (eps)',
    'pgcplan.DTORS = [HOBJECT n_drop]',
    '$gc_callback_count_plan_image(pgcplan, pgccountsource)',
    'H = pgcplan.GRAPH',
    '(HOBJECT n_held) <- $heap_reach(H.ROOTS, eps, H.EDGES)',
    '~((HOBJECT n_drop) <- $heap_reach(H.ROOTS, eps, H.EDGES))',
    '~((HOBJECT n_held) <- $gc_white(H, $gc_eligible_nodes(pgcplan.BUFFER)))',
    '(HOBJECT n_drop) <- $gc_white(H, $gc_eligible_nodes(pgcplan.BUFFER))',
    '~$gc_materialized_callback_context(S[.CURRENT = eps])',
    '~$gc_materialized_callback_context(S[.FRAMES = eps])',
    '~$gc_materialized_callback_context(S[.SOURCES = eps])',
    'S.ORIGIN = (porigin_gc)',
    'pcallcontext.CALLSITE = (porigin_outer_call)',
    '~$gc_materialized_caller_site(S, S.CURRENT, porigin_outer_call)',
    '~$gc_materialized_callback_context(S[.ORIGIN = (porigin_outer_call)])',
    '~$gc_materialized_callback_context(S[.ACTIVEFIBER = (n_held)])',
    '~$gc_materialized_callback_context(S[.GC.WORKER = (n_held)])',
    'pcallcontext_bad = pcallcontext[.CALLSITE = (pgccall.CALL.SITE)]',
    '~$gc_materialized_caller(S, (pcallcontext_bad))',
    '~$gc_materialized_caller(S, (pcallcontext[.LINE = 0]))',
    'S_step = $drive_steps(S, 1)',
    'S_step.COMPLETION = BUDGET',
    'S_step.TODO = (GC_DTORS pgcplan) :: ptask_tail*',
    '$call_task_valid(S_step[.COMPLETION = NORMAL], GC_DTORS pgcplan)',
    'pgccall_erased = pgccall[.COUNT_SOURCE = eps]',
    'pgcplan_erased = pgcplan[.CALL = pgccall_erased][.WEAK = eps]',
    'S_erased = S_step[.COMPLETION = NORMAL][.GC.ACTIVE = (pgccall_erased)]'
    '[.GC.PLAN = (pgcplan_erased)][.TODO = (GC_DTORS pgcplan_erased) :: ptask_tail*]',
    '$gc_callback_count_required_plan(S_erased, pgcplan_erased)',
    '~$gc_plan_valid(S_erased, pgcplan_erased)',
    'S_twice = S_step[.COMPLETION = NORMAL]'
    '[.TODO = (GC_DTORS pgcplan) :: (GC_DTORS pgcplan) :: ptask_tail*]',
    '~$gc_plan_valid(S_twice, pgcplan)',
    '$drive_steps(S_step[.COMPLETION = NORMAL], 1) = $drive_steps(S, 2)',
]

CASES = {
    'function-local-roots-and-fresh-erasure': {
        'source': FUNCTION,
        'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* '
        '-- if pgccall.PASS = 0 -- if S.GC.NEXT = 2',
        'checks': [
            *COMMON,
            'pcallcontext.TARGET = pcallcontext.FUNCTION',
            '$lookup(S.ENV, $ptascii("held")) = (n_held_cell)',
            'S.STORE[n_held_cell] = DEFINED (POBJECT n_held)',
            '(HCELL n_held_cell) <- $machine_roots(S)',
            '(HOBJECT n_held) <- $heap_reach($environment_nodes(S.ENV), eps, H.EDGES)',
            '$call_context_roots(S.CURRENT) = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_held) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_drop) = 1',
        ], 'timeout': 180,
    },
    'method-receiver-root-and-fresh-erasure': {
        'source': METHOD,
        'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* '
        '-- if pgccall.PASS = 0 -- if S.GC.NEXT = 2',
        'checks': [
            *COMMON,
            'pcallcontext.TARGET = METHOD_TARGET n_owner porigin_method',
            'pcallcontext.RECEIVER = (n_owner)',
            '$call_context_roots(S.CURRENT) = [HOBJECT n_owner]',
            '$objectprops_at(S.OBJECTPROPS, n_owner) = (ppropertyslot*)',
            '$property_slot_at(ppropertyslot*, $ptascii("kept")) = (ppropertyslot)',
            'ppropertyslot.STATE = PROP_VALUE (DIRECT (POBJECT n_held))',
            '(HOBJECT n_held) <- $heap_reach($call_context_roots(S.CURRENT), eps, H.EDGES)',
            '~((HOBJECT n_held) <- $heap_reach($environment_nodes(S.ENV), eps, H.EDGES))',
            '~((HOBJECT n_held) <- $heap_reach($machine_roots(S[.CURRENT = eps]), eps, H.EDGES))',
            '$heap_owners($heap_graph(S), HOBJECT n_owner) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_held) = 2',
            '$task_nodes(GC_TRACE pgccall) = eps',
            '~$gc_materialized_caller(S, (pcallcontext[.RECEIVER = eps]))',
        ], 'timeout': 180,
    },
}


RECORDED = runner.recorded


def strict_recorded(command, directory, stem, environment, cap):
    return RECORDED([command[0], '--sl', *command[1:]], directory, stem, environment, cap)


runner.CASES = CASES
runner.recorded = strict_recorded
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if runner.run(args.case) else 1)
