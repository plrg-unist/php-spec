#!/usr/bin/env python3
"""Independent source-reached caller roots and materialized callback progress."""
import argparse

import gc_caller_materialized_review_sources as sources
import shutdown_state_review as runner


NESTED = sources.family.CASES['nested-caller-local-protects-sibling'].decode()
RESURRECT = sources.family.CASES['function-caller-mutation-resurrection'].decode()

CASES = {
    'saved-caller-local-root': {
        'source': NESTED,
        'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* '
        '-- if pgccall.PASS = 0 -- if S.GC.NEXT = 1',
        'checks': [
            '$call_task_valid(S, GC_TRACE pgccall)',
            'S.CURRENT = (pcallcontext)',
            'pgccall.CALLER = S.CURRENT',
            'pcallcontext.NAME = $ptascii("collect_saved_inner07")',
            'S.FRAMES = [pframe_relay, pframe_outer, pframe_global]',
            'pframe_relay.CONTEXT = (pcallcontext_relay)',
            'pcallcontext_relay.NAME = $ptascii("collect_saved_relay07")',
            'pframe_outer.CONTEXT = (pcallcontext_outer)',
            'pcallcontext_outer.NAME = $ptascii("collect_saved_outer07")',
            'pframe_outer.LOCALS = (psymboltable_outer)',
            '$lookup(psymboltable_outer.ENV, $ptascii("held")) = (n_held_cell)',
            'S.STORE[n_held_cell] = DEFINED (POBJECT n_held)',
            '$lookup(S.ENV, $ptascii("held")) = eps',
            '(HCELL n_held_cell) <- $table_roots(pframe_outer.LOCALS)',
            '(HOBJECT n_held) <- $heap_reach($machine_roots(S), eps, $heap_graph(S).EDGES)',
            '$gc_materialized_callback_context(S)',
            'pgccall.COUNT_SOURCE = (pgccountsource)',
            'pgcplan = $gc_plan(S, pgccall)',
            'pgcplan.WEAK = (eps)',
            'pgcplan.DTORS = [HOBJECT n_drop]',
            'n_held =/= n_drop',
            '~((HOBJECT n_held) <- $gc_white(pgcplan.GRAPH, $gc_eligible_nodes(pgcplan.BUFFER)))',
            '(HOBJECT n_drop) <- $gc_white(pgcplan.GRAPH, $gc_eligible_nodes(pgcplan.BUFFER))',
            '$gc_materialized_caller(S, (pcallcontext_relay))',
            '~$gc_materialized_caller_site(S, (pcallcontext_relay), pgccall.CALL.SITE)',
            'pgccall_foreign = pgccall[.CALLER = (pcallcontext_relay)]',
            'S_foreign = S[.GC.ACTIVE = (pgccall_foreign)]'
            '[.TODO = (GC_TRACE pgccall_foreign) :: ptask_tail*]',
            '~$gc_callback_caller_valid(S_foreign, pgccall_foreign)',
            '~$gc_call_live(S_foreign, pgccall_foreign)',
            'pgccall_foreign_erased = pgccall_foreign[.COUNT_SOURCE = eps]',
            'S_relay = $constant_frame_scope(S, pframe_relay, [pframe_outer, pframe_global])',
            'S_foreign_erased = S_relay[.ORIGIN = pgccall.ORIGIN]'
            '[.GC.ACTIVE = (pgccall_foreign_erased)]'
            '[.TODO = (GC_TRACE pgccall_foreign_erased) :: S_relay.TODO]',
            '$call_current_valid(S_foreign_erased)',
            '$gc_materialized_caller(S_foreign_erased, S_foreign_erased.CURRENT)',
            '$gc_materialized_caller_frames(S_foreign_erased, S_foreign_erased.FRAMES)',
            '$gc_materialized_quiet(S_foreign_erased)',
            '~$gc_materialized_caller_site(S_foreign_erased, '
            'S_foreign_erased.CURRENT, pgccall_foreign_erased.CALL.SITE)',
            '$gc_trace(S_foreign_erased, pgccall_foreign_erased).COMPLETION = '
            'UNSUPPORTED "materialized callback trace order"',
            'S_fresh = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
            'pgcplan_foreign_erased = pgcplan[.CALL = pgccall_foreign_erased][.WEAK = eps]',
            'S_fresh_erased = S_fresh[.GC.ACTIVE = (pgccall_foreign_erased)]'
            '[.GC.PLAN = (pgcplan_foreign_erased)]'
            '[.TODO = (GC_DTORS pgcplan_foreign_erased) :: ptask_tail*]',
            '$gc_callback_count_required_plan(S_fresh_erased, pgcplan_foreign_erased)',
            '~$gc_plan_live(S_fresh_erased, pgcplan_foreign_erased)',
            '$task_nodes(GC_TRACE pgccall[.COUNT_SOURCE = eps]) = $task_nodes(GC_TRACE pgccall)',
            '~$call_task_valid(S[.CURRENT = eps], GC_TRACE pgccall)',
            '~$gc_materialized_callback_context(S[.FRAMES = '
            '[pframe_relay, pframe_outer[.CONTEXT = eps], pframe_global]])',
            'S_paused = $drive_steps(S, 0)',
            'S_paused.COMPLETION = BUDGET',
            'S_paused.FRAMES = S.FRAMES',
            '$drive_steps(S_paused[.COMPLETION = NORMAL], 1) = $drive_steps(S, 1)',
        ], 'timeout': 240,
    },
    'callback-caller-erasure': {
        'source': RESURRECT,
        'stage': 'S.CURRENT = (pcallcontext) -- if S.GC.NEXT = 1 '
        '-- if S.GC.PLAN = (pgcplan) -- if pgcplan.CALL.PASS = 0 '
        '-- if $destructor_context_kind(S, pcallcontext)',
        'checks': [
            '$gc_plan_live(S, pgcplan)',
            'pgcplan.CALL.COUNT_SOURCE = (pgccountsource)',
            'pgcplan.DTORS = [HOBJECT n_root]',
            'pgcplan.CALL.CALLER = (pcallcontext_caller)',
            'pcallcontext_caller.NAME = $ptascii("collect_resurrect_frame07")',
            'pcallcontext =/= pcallcontext_caller',
            'S.FRAMES = pframe_gc :: pframe_tail*',
            'pframe_gc.CONTEXT = (pcallcontext_caller)',
            'pframe_gc.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: '
            '(GC_DTOR_RETURN pgcplan n_root) :: ptask_tail*',
            'pdestructorcall.CALLER = pgcplan.CALL.CALLER',
            '$gc_consumer_count(S.TODO, pgcplan.CALL) = 0',
            '$gc_consumer_frame_count(S.FRAMES, pgcplan.CALL) = 1',
            '~$gc_snapshot_fresh(S, pgcplan)',
            '$destructor_context_valid(S, pcallcontext)',
            '$machine_roots(S[.GC.PLAN = eps][.GC.ACTIVE = eps]) = $machine_roots(S)',
            'pgccall_erased = pgcplan.CALL[.COUNT_SOURCE = eps]',
            'pgcplan_erased = pgcplan[.CALL = pgccall_erased][.WEAK = eps]',
            'pframe_erased = pframe_gc[.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: '
            '(GC_DTOR_RETURN pgcplan_erased n_root) :: ptask_tail*]',
            'S_erased = S[.GC.ACTIVE = (pgccall_erased)][.GC.PLAN = (pgcplan_erased)]'
            '[.FRAMES = pframe_erased :: pframe_tail*]',
            '$gc_consumer_frame_count(S_erased.FRAMES, pgccall_erased) = 1',
            '$gc_callback_count_required_plan(S_erased, pgcplan_erased)',
            '~$gc_call_live(S_erased, pgccall_erased)',
            '~$gc_plan_live(S_erased, pgcplan_erased)',
            '~$destructor_context_valid(S_erased, pcallcontext)',
            'pgccall_foreign_erased = pgccall_erased[.CALLER = (pcallcontext)]',
            'pgcplan_foreign_erased = pgcplan_erased[.CALL = pgccall_foreign_erased]',
            'pframe_foreign_erased = pframe_gc[.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: '
            '(GC_DTOR_RETURN pgcplan_foreign_erased n_root) :: ptask_tail*]',
            'S_foreign_erased = S[.GC.ACTIVE = (pgccall_foreign_erased)]'
            '[.GC.PLAN = (pgcplan_foreign_erased)]'
            '[.FRAMES = pframe_foreign_erased :: pframe_tail*]',
            '$gc_callback_count_required_plan(S_foreign_erased, pgcplan_foreign_erased)',
            '~$gc_call_live(S_foreign_erased, pgccall_foreign_erased)',
            'S_unconsumed = S[.FRAMES = '
            'pframe_gc[.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*] :: pframe_tail*]',
            '~$gc_call_live(S_unconsumed, pgcplan.CALL)',
            'S_duplicated = S[.FRAMES = pframe_gc[.TODO = pframe_gc.TODO ++ '
            '[GC_DTOR_RETURN pgcplan n_root]] :: pframe_tail*]',
            '~$gc_call_live(S_duplicated, pgcplan.CALL)',
        ], 'timeout': 240,
    },
    'resurrection-signed-pass1': {
        'source': RESURRECT,
        'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* '
        '-- if pgccall.PASS = 1 -- if S.GC.NEXT = 1',
        'checks': [
            '$call_task_valid(S, GC_TRACE pgccall)',
            'S.CURRENT = pgccall.CALLER',
            'pgccall.CALLER = (pcallcontext)',
            'pcallcontext.NAME = $ptascii("collect_resurrect_frame07")',
            'pgccall.COUNT_SOURCE = (pgccountsource)',
            'pgccountsource.DTORS = [HOBJECT n_root]',
            'S.GC.PLAN = (pgcplan_prior)',
            'pgcplan_prior.CALL = pgccall',
            'pgcplan_prior.STEPS = [GC_CALLED (HOBJECT n_root)]',
            'pgcplan_prior.DONE = [HOBJECT n_root]',
            'pgccall.TOTAL = $(-1)',
            '$lookup(S.ENV, $ptascii("saved07")) = (n_saved_cell)',
            'S.GLOBALTABLE = (psymboltable_global)',
            '$lookup(psymboltable_global.ENV, $ptascii("saved07")) = (n_saved_cell)',
            'S.STORE[n_saved_cell] = DEFINED (POBJECT n_root)',
            '$heap_owners($heap_graph(S), HOBJECT n_root) = 2',
            '$gc_graph(S) = H_current',
            'H_current =/= pgccountsource.GRAPH',
            'pgcplan = $gc_plan(S, pgccall)',
            'pgcplan.WEAK = (eps)',
            'pgcplan.DTORS = eps',
            'pgcplan.FREESET = eps',
            'pgccall_erased = pgccall[.COUNT_SOURCE = eps]',
            'pgcplan_erased = pgcplan_prior[.CALL = pgccall_erased][.WEAK = eps]',
            'S_erased = S[.GC.ACTIVE = (pgccall_erased)][.GC.PLAN = (pgcplan_erased)]'
            '[.TODO = (GC_TRACE pgccall_erased) :: ptask_tail*]',
            '$gc_callback_count_required_plan(S_erased, pgcplan_erased)',
            '~$call_task_valid(S_erased, GC_TRACE pgccall_erased)',
            'S_step = $drive_steps(S, 1)',
            'S_step.COMPLETION = BUDGET',
            'S_step.TODO = (GC_DTORS pgcplan) :: ptask_tail*',
            'S_done = $drive_steps(S, 3)',
            'S_done.COMPLETION = BUDGET',
            'S_done.RESULT = KNOWN (PINT $(-1))',
            '$drive_steps(S_step[.COMPLETION = NORMAL], 2) = S_done',
        ], 'timeout': 240,
    },
    'resurrected-caller-later-release': {
        'source': RESURRECT,
        'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* '
        '-- if pgccall.PASS = 0 -- if S.GC.NEXT = 3',
        'checks': [
            '$call_task_valid(S, GC_TRACE pgccall)',
            'S.CURRENT = pgccall.CALLER',
            'pgccall.CALLER = (pcallcontext)',
            'pcallcontext.NAME = $ptascii("collect_resurrect_frame07")',
            'pgccall.COUNT_SOURCE = (pgccountsource)',
            'pgccountsource.DTORS = eps',
            '$lookup(S.ENV, $ptascii("saved07")) = (n_saved_cell)',
            'S.STORE[n_saved_cell] = DEFINED PNULL',
            '$lookup(S.ENV, $ptascii("weakRoot")) = (n_root_weak_cell)',
            'S.STORE[n_root_weak_cell] = DEFINED (POBJECT n_root_weak)',
            'S.OBJECTS[n_root_weak] = WEAKREFERENCE (n_root)',
            '$lookup(S.ENV, $ptascii("weakProxy")) = (n_proxy_weak_cell)',
            'S.STORE[n_proxy_weak_cell] = DEFINED (POBJECT n_proxy_weak)',
            'S.OBJECTS[n_proxy_weak] = WEAKREFERENCE (n_proxy)',
            '$object_table_at(S.OBJECTTABLES, n_proxy) = (n_table)',
            '$objectprops_at(S.OBJECTPROPS, n_root) = (ppropertyslot*)',
            '$property_slot_at(ppropertyslot*, $ptascii("head")) = (ppropertyslot_head)',
            'ppropertyslot_head.STATE = PROP_VALUE (DIRECT (POBJECT n_proxy))',
            '$property_slot_at(ppropertyslot*, $ptascii("tail")) = (ppropertyslot_tail)',
            'ppropertyslot_tail.STATE = PROP_VALUE (DIRECT (PARRAY n_table))',
            'pgcplan = $gc_plan(S, pgccall)',
            'pgcplan.WEAK = (eps)',
            'pgcplan.DTORS = eps',
            '|pgcplan.COUNTED| = 3',
            '$gc_pass_count(pgcplan) = 3',
            'S_done = $drive_steps(S, 3)',
            'S_done.COMPLETION = BUDGET',
            'S_done.RESULT = KNOWN (PINT 3)',
            '~((HOBJECT n_root) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_proxy) <- S_done.ALLOCATIONS)',
            '$drive_steps($drive_steps(S, 1)[.COMPLETION = NORMAL], 2) = S_done',
        ], 'timeout': 240,
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
