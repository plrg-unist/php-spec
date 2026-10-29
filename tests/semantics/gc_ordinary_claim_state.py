#!/usr/bin/env python3
"""Source-reached quiet ordinary GC worklist and plan-authentication checks."""
import argparse
import hashlib

import gc_ordinary_claim_sources as sources
import shutdown_state_review as runner


PEER = b'''<?php
gc_disable();
#[AllowDynamicProperties]
class ReviewRoot04 { public $head; public $tail; }
#[AllowDynamicProperties]
class ReviewProxy04 {}
$root = new ReviewRoot04;
$proxy = new ReviewProxy04;
$proxy->back = $root;
$table = (array) $proxy;
$root->head =& $proxy;
$root->tail = $table;
$root->extra = 7;
$rootWeak = WeakReference::create($root);
$proxyWeak = WeakReference::create($proxy);
$heldRoot = $root;
$outside = $table;
unset($root, $proxy, $table);
echo 'P|', gc_collect_cycles(), '|';
echo $rootWeak->get() !== null && $proxyWeak->get() !== null ? 'live|' : 'BAD-live|';
unset($outside);
echo gc_collect_cycles(), '|';
unset($heldRoot);
echo gc_collect_cycles(), '|';
echo $rootWeak->get() === null && $proxyWeak->get() === null ? 'dead|' : 'BAD-dead|';
echo gc_collect_cycles(), '|END';
'''
assert hashlib.sha256(PEER).hexdigest() == 'c8192e22ac171d9da29bf1bd22bb9b37373c1f911bb8d2bff62876152ef10e69'


AUTHOR = sources.family.CASES['inline-sibling-shared-table'].decode()
FRONT = 'S.TODO = (GC_FREE pgcplan) :: ptask_tail* -- if pgcplan.CALL.PASS = 0 '


def common_white(count):
    return [
        '$gc_quiet_claim_policy(S)', '$call_task_valid(S, GC_FREE pgcplan)',
        'pgcplan.DTORS = eps', 'pgcplan.WEAK = (eps)',
        'H = pgcplan.GRAPH', '$heap_valid(H)',
        'pnode_roots* = $gc_eligible_nodes(pgcplan.BUFFER)',
        'pnode_white* = $gc_white(H, pnode_roots*)',
        '$gc_count_walk(H, pgcplan.PROXIES, pgcplan.WEAK, '
        '$gc_root_visits(pnode_roots*), pnode_white*) = (pnode_visit*, pnode_counted*)',
        'pnode_visit* = pgcplan.FREESET', 'pnode_counted* = pgcplan.COUNTED',
        f'|pnode_counted*| = {count}', f'$gc_pass_count(pgcplan) = {count}',
        'S_step = $drive_steps(S, 1)', 'S_step.COMPLETION = BUDGET',
        f'S_step.RESULT = KNOWN (PINT {count})',
        '$drive_steps(S_step[.COMPLETION = NORMAL], 1) = $drive_steps(S, 2)',
    ]


CASES = {
    'protected-empty-plan-marker': {
        'source': AUTHOR,
        'stage': FRONT + '-- if S.GC.NEXT = 1',
        'checks': [
            '$gc_quiet_claim_policy(S)', '$call_task_valid(S, GC_FREE pgcplan)',
            'pgcplan.WEAK = (eps)', 'pgcplan.DTORS = eps',
            'pgcplan.FREESET = eps', 'pgcplan.COUNTED = eps',
            '$gc_pass_count(pgcplan) = 0',
            'pgcplan_legacy = pgcplan[.WEAK = eps]',
            'S_legacy = S[.GC.PLAN = (pgcplan_legacy)][.TODO = (GC_FREE pgcplan_legacy) :: ptask_tail*]',
            '~$call_task_valid(S_legacy, GC_FREE pgcplan_legacy)',
            'S_step = $drive_steps(S, 1)', 'S_step.COMPLETION = BUDGET',
            'S_step.RESULT = KNOWN (PINT 0)',
        ], 'timeout': 180,
    },
    'inline-sibling-real-table': {
        'source': AUTHOR,
        'stage': FRONT + '-- if S.GC.NEXT = 3',
        'checks': [
            *common_white(3),
            '$lookup(S.ENV, $ptascii("wr")) = (n_wr_cell)',
            'S.STORE[n_wr_cell] = DEFINED (POBJECT n_wr)',
            'S.OBJECTS[n_wr] = WEAKREFERENCE (n_root)',
            '$lookup(S.ENV, $ptascii("wp")) = (n_wp_cell)',
            'S.STORE[n_wp_cell] = DEFINED (POBJECT n_wp)',
            'S.OBJECTS[n_wp] = WEAKREFERENCE (n_proxy)',
            '$lookup(S.ENV, $ptascii("held")) = (n_held_cell)',
            'S.STORE[n_held_cell] = DEFINED (POBJECT n_held)',
            '(HOBJECT n_held) <- $gc_uncalled(S, S.ALLOCATIONS)',
            '~((HOBJECT n_held) <- pnode_white*)',
            '$gc_uncalled(S, pnode_white*) = eps',
            '$object_table_at(S.OBJECTTABLES, n_root) = eps',
            '$object_table_at(S.OBJECTTABLES, n_proxy) = (n_table)',
            '$gc_trace_children(S, HOBJECT n_root) = [HOBJECT n_proxy, HARRAY n_table]',
            '(HEDGE (HOBJECT n_proxy) (HARRAY n_table)) <- pgcplan.PROXIES',
            '$heap_owners($heap_graph(S), HARRAY n_table) = 2',
            'pnode_roots*[0] = HOBJECT n_root',
            '(HARRAY n_table) <- pgcplan.COUNTED',
            '$gc_walk(H, pgcplan.PROXIES, $gc_root_visits(pnode_roots*), '
            'pnode_white*, eps, eps) = (pnode_old_visit*, pnode_old_counted*)',
            '|pnode_old_counted*| = 2',
            '~((HARRAY n_table) <- pnode_old_counted*)',
            '~((HOBJECT n_root) <- S_step.ALLOCATIONS)',
            '~((HOBJECT n_proxy) <- S_step.ALLOCATIONS)',
            '(HOBJECT n_held) <- S_step.ALLOCATIONS',
            '(HOBJECT n_held) <- $gc_uncalled(S_step, S_step.ALLOCATIONS)',
        ], 'timeout': 180,
    },
    'materialized-cell-sibling-real-table': {
        'source': PEER.decode(),
        'stage': FRONT + '-- if S.GC.NEXT = 3',
        'checks': [
            *common_white(3),
            '$lookup(S.ENV, $ptascii("rootWeak")) = (n_wr_cell)',
            'S.STORE[n_wr_cell] = DEFINED (POBJECT n_wr)',
            'S.OBJECTS[n_wr] = WEAKREFERENCE (n_root)',
            '$lookup(S.ENV, $ptascii("proxyWeak")) = (n_wp_cell)',
            'S.STORE[n_wp_cell] = DEFINED (POBJECT n_wp)',
            'S.OBJECTS[n_wp] = WEAKREFERENCE (n_proxy)',
            '$object_table_at(S.OBJECTTABLES, n_root) = (n_root_table)',
            '$object_table_at(S.OBJECTTABLES, n_proxy) = (n_proxy_table)',
            '$gc_trace_children(S, HOBJECT n_root) = [HARRAY n_root_table]',
            '$gc_trace_children(S, HARRAY n_root_table) = [HCELL n_alias, HARRAY n_proxy_table]',
            '$gc_trace_children(S, HCELL n_alias) = [HOBJECT n_proxy]',
            'H_physical = $heap_graph(S)',
            '$heap_owners(H_physical, HCELL n_alias) = 1',
            '$heap_owners(H_physical, HARRAY n_proxy_table) = 2',
            '~((HEDGE (HARRAY n_root_table) (HCELL n_alias)) <- H_physical.EDGES)',
            '(HEDGE (HOBJECT n_root) (HARRAY n_root_table)) <- pgcplan.PROXIES',
            '(HEDGE (HOBJECT n_proxy) (HARRAY n_proxy_table)) <- pgcplan.PROXIES',
            'pnode_roots*[0] = HOBJECT n_root',
            '(HARRAY n_proxy_table) <- pgcplan.COUNTED',
            '~((HARRAY n_root_table) <- pgcplan.COUNTED)',
            '$gc_walk(H, pgcplan.PROXIES, $gc_root_visits(pnode_roots*), '
            'pnode_white*, eps, eps) = (pnode_old_visit*, pnode_old_counted*)',
            '|pnode_old_counted*| = 2',
            '~((HARRAY n_proxy_table) <- pnode_old_counted*)',
            '~((HOBJECT n_root) <- S_step.ALLOCATIONS)',
            '~((HOBJECT n_proxy) <- S_step.ALLOCATIONS)',
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
