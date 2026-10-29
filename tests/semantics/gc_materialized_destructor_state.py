#!/usr/bin/env python3
"""Reached callback, retrace, and already-called materialized GC fronts."""
import argparse
import hashlib

import gc_materialized_destructor_sources as sources
import shutdown_state_review as runner


PEER = b'''<?php
gc_disable();
#[AllowDynamicProperties]
class GcCallbackRoot05 {
    public $edge;
    public $payload;
    public function __destruct() {
        global $saved, $wr, $wl;
        echo 'D|', $wr->get() === $this ? 'self|' : 'BAD|';
        echo $wl->get() !== null ? 'child|' : 'BAD|';
        $saved = $this;
    }
}
class GcCallbackLeaf05 { public $back; }
$saved = null;
$root = new GcCallbackRoot05;
$leaf = new GcCallbackLeaf05;
$link = $leaf;
$root->edge =& $link;
$root->payload = [$leaf, $leaf];
$root->extra = 7;
$leaf->back = $root;
$wr = WeakReference::create($root);
$wl = WeakReference::create($leaf);
unset($root, $leaf, $link);
echo 'B|', gc_collect_cycles(), '|';
echo $wr->get() === $saved && $wl->get() !== null ? 'saved|' : 'BAD|';
unset($saved);
echo 'U|', gc_collect_cycles(), '|';
echo $wr->get() === null && $wl->get() === null ? 'dead|' : 'BAD|';
echo gc_collect_cycles(), '|END';
'''
assert hashlib.sha256(PEER).hexdigest() == 'b21221a41606cfd93d4c33e17c46866677c6d75f1de4cfa84ebcc8a7e65da17d'
AUTHOR = sources.family.CASES['materialized-shared-table-dtor'].decode()


CASES = {
    'materialized-first-trace-and-callback': {
        'source': AUTHOR,
        'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* -- if pgccall.PASS = 0 -- if S.GC.NEXT = 1',
        'checks': [
            '$call_task_valid(S, GC_TRACE pgccall)',
            '$object_table_gc_boundary(S)',
            '$gc_materialized_callback_context(S)',
            'pgcplan = $gc_plan(S, pgccall)',
            'pgccall.COUNT_SOURCE = (pgccountsource)',
            'pgcplan.WEAK = (eps)',
            '$lookup(S.ENV, $ptascii("wr")) = (n_wr_cell)',
            'S.STORE[n_wr_cell] = DEFINED (POBJECT n_wr)',
            'S.OBJECTS[n_wr] = WEAKREFERENCE (n_root)',
            'pgcplan.DTORS = [HOBJECT n_root]',
            '$object_table_at(S.OBJECTTABLES, n_root) = (n_root_table)',
            '$gc_materialized_callback_trace(S, pgccall)',
            '$gc_callback_walk_agrees(pgcplan)',
            '$gc_materialized_callback_trace_ok(S, pgccall)',
            '$gc_count_walk(pgcplan.GRAPH, pgcplan.PROXIES, eps, '
            '$gc_root_visits($gc_eligible_nodes(pgcplan.BUFFER)), '
            '$gc_white(pgcplan.GRAPH, $gc_eligible_nodes(pgcplan.BUFFER))) = '
            '$gc_count_walk(pgcplan.GRAPH, pgcplan.PROXIES, (eps), '
            '$gc_root_visits($gc_eligible_nodes(pgcplan.BUFFER)), '
            '$gc_white(pgcplan.GRAPH, $gc_eligible_nodes(pgcplan.BUFFER)))',
            'S_step = $drive_steps(S, 1)',
            'S_step.COMPLETION = BUDGET',
            'S_step.TODO = (GC_DTORS pgcplan) :: ptask_tail*',
            '$call_task_valid(S_step[.COMPLETION = NORMAL], GC_DTORS pgcplan)',
            '$drive_steps(S_step[.COMPLETION = NORMAL], 1) = $drive_steps(S, 2)',
        ], 'timeout': 180,
    },
    'resurrection-retrace': {
        'source': PEER.decode(),
        'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* -- if pgccall.PASS = 1 -- if S.GC.PLAN = (pgcplan_prior)',
        'checks': [
            '$call_task_valid(S, GC_TRACE pgccall)',
            'pgcplan_prior.DTORS = [HOBJECT n_root]',
            'pgcplan_prior.INDEX = |pgcplan_prior.DTORS|',
            'pgcplan_prior.STEPS = [GC_CALLED (HOBJECT n_root)]',
            'pgcplan_prior.DONE = [HOBJECT n_root]',
            'n_root <- S.DESTRUCTION.CALLED',
            '$gc_prior_ordinary_table(S, pgcplan_prior.TABLES, pgcplan_prior.GRAPH.NODES)',
            'S.OBJECTS[n_root] = INSTANCE porigin_root',
            '$lookup(S.ENV, $ptascii("saved")) = (n_saved_cell)',
            'S.STORE[n_saved_cell] = DEFINED (POBJECT n_root)',
            '$lookup(S.ENV, $ptascii("wl")) = (n_wl_cell)',
            'S.STORE[n_wl_cell] = DEFINED (POBJECT n_wl)',
            'S.OBJECTS[n_wl] = WEAKREFERENCE (n_leaf)',
            '$object_table_at(S.OBJECTTABLES, n_root) = (n_root_table)',
            '$gc_trace_children(S, HARRAY n_root_table) = [HCELL n_alias, HARRAY n_payload]',
            'H = $heap_graph(S)',
            '$heap_owners(H, HOBJECT n_root) = 2',
            '$heap_owners(H, HCELL n_alias) = 1',
            '$heap_owners(H, HOBJECT n_leaf) = 3',
            '~((HEDGE (HARRAY n_root_table) (HCELL n_alias)) <- H.EDGES)',
            '$gc_materialized_callback_trace(S, pgccall)',
            '$gc_materialized_callback_context(S)',
            'pgcplan = $gc_plan(S, pgccall)',
            'pgccall.COUNT_SOURCE = (pgccountsource)',
            'pgcplan.WEAK = (eps)',
            'pgcplan.DTORS = eps',
            'pgcplan.FREESET = eps',
            '$gc_callback_walk_agrees(pgcplan)',
            '$gc_materialized_callback_trace_ok(S, pgccall)',
            'S_std = S[.OBJECTS[n_root] = STDINSTANCE]',
            '~$gc_prior_ordinary_table(S_std, pgcplan_prior.TABLES, pgcplan_prior.GRAPH.NODES)',
            '~$gc_materialized_callback_trace(S_std, pgccall)',
            '$gc_materialized_callback_trace_ok(S_std, pgccall)',
            'S_step = $drive_steps(S, 1)',
            'S_step.COMPLETION = BUDGET',
            'S_step.TODO = (GC_DTORS pgcplan) :: ptask_tail*',
            '$drive_steps(S_step[.COMPLETION = NORMAL], 1) = $drive_steps(S, 2)',
        ], 'timeout': 180,
    },
    'already-called-fresh-collection': {
        'source': PEER.decode(),
        'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* -- if pgccall.PASS = 0 -- if S.GC.NEXT = 2',
        'checks': [
            '$call_task_valid(S, GC_TRACE pgccall)',
            'S.GC.PLAN = eps',
            '$gc_materialized_callback_context(S)',
            '$gc_ephemeron_called_current(S, S.DESTRUCTION.CALLED)',
            'pgcplan = $gc_plan(S, pgccall)',
            'pgccall.COUNT_SOURCE = (pgccountsource)',
            'pgcplan.WEAK = (eps)',
            'pgcplan.DTORS = eps',
            '$gc_materialized_callback_trace(S, pgccall)',
            '$gc_callback_walk_agrees(pgcplan)',
            '$gc_materialized_callback_trace_ok(S, pgccall)',
            '|pgcplan.COUNTED| = 3',
            '$gc_pass_count(pgcplan) = 3',
            '$lookup(S.ENV, $ptascii("wr")) = (n_wr_cell)',
            'S.STORE[n_wr_cell] = DEFINED (POBJECT n_wr)',
            'S.OBJECTS[n_wr] = WEAKREFERENCE (n_root)',
            'n_root <- S.DESTRUCTION.CALLED',
            '$lookup(S.ENV, $ptascii("wl")) = (n_wl_cell)',
            'S.STORE[n_wl_cell] = DEFINED (POBJECT n_wl)',
            'S.OBJECTS[n_wl] = WEAKREFERENCE (n_leaf)',
            'S_step = $drive_steps(S, 1)',
            'S_step.COMPLETION = BUDGET',
            'S_step.TODO = (GC_DTORS pgcplan) :: ptask_tail*',
            '$drive_steps(S_step[.COMPLETION = NORMAL], 1) = $drive_steps(S, 2)',
            'S_free = $drive_steps(S, 2)',
            'S_free.COMPLETION = BUDGET',
            'S_free.TODO = (GC_FREE pgcplan) :: ptask_tail*',
            '$call_task_valid(S_free[.COMPLETION = NORMAL], GC_FREE pgcplan)',
            'S_done = $drive_steps(S_free[.COMPLETION = NORMAL], 1)',
            'S_done.COMPLETION = BUDGET',
            'S_done.RESULT = KNOWN (PINT 3)',
            '~((HOBJECT n_root) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_leaf) <- S_done.ALLOCATIONS)',
            'S_done = $drive_steps(S, 3)',
        ], 'timeout': 180,
    },
    'derived-order-mismatch-refusal': {
        'source': AUTHOR,
        'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* -- if pgccall.PASS = 0 -- if S.GC.NEXT = 1',
        'checks': [
            '$lookup(S.ENV, $ptascii("wr")) = (n_wr_cell)',
            'S.STORE[n_wr_cell] = DEFINED (POBJECT n_wr)',
            'S.OBJECTS[n_wr] = WEAKREFERENCE (n_root)',
            '$lookup(S.ENV, $ptascii("wp")) = (n_wp_cell)',
            'S.STORE[n_wp_cell] = DEFINED (POBJECT n_wp)',
            'S.OBJECTS[n_wp] = WEAKREFERENCE (n_proxy)',
            '$object_table_at(S.OBJECTTABLES, n_proxy) = (n_proxy_table)',
            '$objectprops_at(S.OBJECTPROPS, n_root) = (ppropertyslot*)',
            '$property_slot_at(ppropertyslot*, $ptascii("head")) = (ppropertyslot_head)',
            'ppropertyslot_head.STATE = PROP_VALUE (DIRECT (PARRAY n_proxy_table))',
            '$property_slot_at(ppropertyslot*, $ptascii("tail")) = (ppropertyslot_tail)',
            'ppropertyslot_tail.STATE = PROP_VALUE (DIRECT (POBJECT n_proxy))',
            'ppropertyslot_swapped* = $property_slot_set('
            '$property_slot_set(ppropertyslot*, $ptascii("head"), '
            'PROP_VALUE (DIRECT (POBJECT n_proxy))), $ptascii("tail"), '
            'PROP_VALUE (DIRECT (PARRAY n_proxy_table)))',
            'S_swapped = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS, n_root, ppropertyslot_swapped*)]'
            '[.GC.BUFFER = [GC_ROOT (HOBJECT n_root)]][.GC.FREE = eps]',
            '$gc_materialized_callback_context(S_swapped)',
            '$object_tables_valid(S_swapped)',
            'pgccall.COUNT_SOURCE = (pgccountsource)',
            'pgcplan_swapped = $gc_plan(S_swapped, pgccall)',
            'pgcplan_swapped.DTORS = [HOBJECT n_root]',
            'H_swapped = pgcplan_swapped.GRAPH',
            'pnode_roots* = $gc_eligible_nodes(pgcplan_swapped.BUFFER)',
            'pnode_white* = $gc_white(H_swapped, pnode_roots*)',
            '$gc_count_walk(H_swapped, pgcplan_swapped.PROXIES, eps, '
            '$gc_root_visits(pnode_roots*), pnode_white*) = (pnode_old_visit*, pnode_old_counted*)',
            '$gc_count_walk(H_swapped, pgcplan_swapped.PROXIES, (eps), '
            '$gc_root_visits(pnode_roots*), pnode_white*) = (pnode_new_visit*, pnode_new_counted*)',
            '|pnode_old_counted*| = 2',
            '|pnode_new_counted*| = 3',
            '~((HARRAY n_proxy_table) <- pnode_old_counted*)',
            '(HARRAY n_proxy_table) <- pnode_new_counted*',
            '~$gc_callback_walk_agrees(pgcplan_swapped)',
            'pgcplan_swapped.WEAK = (eps)',
            '|pgcplan_swapped.COUNTED| = 3',
            '~$call_task_valid(S_swapped, GC_TRACE pgccall)',
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
