#!/usr/bin/env python3
"""Strict source-reached finite ephemeron closure and partial GC_FREE checks."""
import argparse
import hashlib

import gc_ephemeron_generic_sources as sources
import shutdown_state_review as runner


PEER = b'''<?php
gc_disable();
class ReviewEphemeronPayload {
    public $chain;
    public $back;
    public $number;
}
$left = new WeakMap;
$right = new WeakMap;
$extra = new WeakMap;
$a = new stdClass;
$b = new stdClass;
$drop = new stdClass;
$x = new ReviewEphemeronPayload;
$y = new ReviewEphemeronPayload;
$left[$a] = $x;
$right[$b] = $y;
$extra[$drop] = $x;
$drop->self = $drop;
$link = $b;
$outside = 7;
$x->chain = [&$link, &$link];
$x->number =& $outside;
$y->back = $a;
$wa = WeakReference::create($a);
$wb = WeakReference::create($b);
$wx = WeakReference::create($x);
$wy = WeakReference::create($y);
$wd = WeakReference::create($drop);
$held = $x;
unset($a, $b, $drop, $x, $y, $link);
echo 'P|', gc_collect_cycles(), '|';
echo $wa->get() !== null && $wb->get() !== null && $wx->get() !== null && $wy->get() !== null ? 'live|' : 'BAD|';
echo $wd->get() === null ? 'drop-dead|' : 'BAD|';
echo $outside, '|';
unset($held);
echo 'R|', gc_collect_cycles(), '|';
echo $wa->get() === null && $wb->get() === null && $wx->get() === null && $wy->get() === null ? 'dead|' : 'BAD|';
echo $outside, '|';
$outside = 8;
echo 'A|', $outside, '|', gc_collect_cycles(), '|END';
'''
assert hashlib.sha256(PEER).hexdigest() == 'b1532e60a6f1de82c3389ad44b8ac2aa04e480d9e3fb4404f0de604d09ca5f4e'


CASES = {
    'branching-live-fixpoint': {
        'source': sources.family.CASES['branching-entry-fixpoint'].decode(),
        'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
                 '-- if pconfigcall.KIND = INTRINSIC_GC_COLLECT -- if S.GC.NEXT = 0',
        'checks': [
            '$gc_ephemeron_policy(S)',
            'H = $gc_ephemeron_base(S)',
            'pnode_start* = $heap_intersect(H.NODES, $heap_reach(H.ROOTS, eps, H.EDGES))',
            'pnode_step1* = $gc_ephemeron_live_step(S, H, pnode_start*)',
            'pnode_step2* = $gc_ephemeron_live_step(S, H, pnode_step1*)',
            'pnode_start* =/= pnode_step1*', 'pnode_step1* =/= pnode_step2*',
            '$heap_subset(pnode_start*, pnode_step1*)',
            '$heap_subset(pnode_step1*, pnode_step2*)',
            'pnode_step2* = $gc_ephemeron_live_fix(S, H, pnode_start*)',
            '$gc_ephemeron_live_step(S, H, pnode_step2*) = pnode_step2*',
            # Derived entry-order control over the same reached heap.
            '$lookup(S.ENV, $ptascii("map")) = (n_map_cell)',
            'S.STORE[n_map_cell] = DEFINED (POBJECT n_map)',
            'pweakmapentry_all* = $weakmap_entries_contents(S, n_map)',
            '|pweakmapentry_all*| = 3',
            'pweakmapentry_a = pweakmapentry_all*[0]',
            'pweakmapentry_b = pweakmapentry_all*[1]',
            'pweakmapentry_c = pweakmapentry_all*[2]',
            'S_reversed = S[.OBJECTS[n_map] = $weakmap_entries_pack([pweakmapentry_c] ++ [pweakmapentry_b] ++ [pweakmapentry_a])]',
            '$gc_ephemeron_base(S_reversed) = H',
            '$gc_ephemeron_live_step(S_reversed, H, pnode_start*) = pnode_step1*',
            '$gc_ephemeron_live_step(S_reversed, H, pnode_step1*) = pnode_step2*',
        ],
        'timeout': 180,
    },
    'branching-released-proxy-count': {
        'source': sources.family.CASES['branching-entry-fixpoint'].decode(),
        'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
                 '-- if pconfigcall.KIND = INTRINSIC_GC_COLLECT -- if S.GC.NEXT = 1',
        'checks': [
            '$gc_ephemeron_policy(S)',
            'S_started = $gc_begin(S, pconfigcall)',
            '$gc_ephemeron_policy(S_started)',
            'S_started.TODO = (GC_TRACE pgccall) :: ptask_tail*',
            'pgcplan = $gc_plan(S_started, pgccall)',
            'pgcplan.DTORS = eps', '|pgcplan.COUNTED| = 7',
            '$gc_pass_count(pgcplan) = 7',
            '$lookup(S.ENV, $ptascii("wx")) = (n_watch_cell)',
            'S.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
            'S.OBJECTS[n_watch] = WEAKREFERENCE (n_x)',
            '$object_table_at(S.OBJECTTABLES, n_x) = (n_table)',
            '(HARRAY n_table) <- pgcplan.FREESET',
            '~((HARRAY n_table) <- pgcplan.COUNTED)',
            '$heap_valid(pgcplan.GRAPH)',
        ],
        'timeout': 180,
    },
    'unheld-map-dual-incidence': {
        'source': sources.family.CASES['unheld-map-live-key'].decode(),
        'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
                 '-- if pconfigcall.KIND = INTRINSIC_GC_COLLECT -- if S.GC.NEXT = 0',
        'checks': [
            '$gc_ephemeron_policy(S)',
            '$lookup(S.ENV, $ptascii("wm")) = (n_wm_cell)',
            'S.STORE[n_wm_cell] = DEFINED (POBJECT n_wm)',
            'S.OBJECTS[n_wm] = WEAKREFERENCE (n_map)',
            '$lookup(S.ENV, $ptascii("wv")) = (n_wv_cell)',
            'S.STORE[n_wv_cell] = DEFINED (POBJECT n_wv)',
            'S.OBJECTS[n_wv] = WEAKREFERENCE (n_value)',
            '$lookup(S.ENV, $ptascii("wk")) = (n_wk_cell)',
            'S.STORE[n_wk_cell] = DEFINED (POBJECT n_wk)',
            'S.OBJECTS[n_wk] = WEAKREFERENCE (n_key)',
            'S_started = $gc_begin(S, pconfigcall)',
            'H = $gc_ephemeron_base(S_started)',
            'pnode_start* = $heap_intersect(H.NODES, $heap_reach(H.ROOTS, eps, H.EDGES))',
            'pnode_live* = $gc_ephemeron_live_fix(S_started, H, pnode_start*)',
            '(HOBJECT n_key) <- pnode_live*', '~((HOBJECT n_map) <- pnode_live*)',
            'S_started.TODO = (GC_TRACE pgccall) :: ptask_tail*',
            'pgcplan = $gc_plan(S_started, pgccall)',
            '(HEDGE (HOBJECT n_map) (HOBJECT n_value)) <- pgcplan.GRAPH.EDGES',
            '~((HEDGE (HOBJECT n_key) (HOBJECT n_value)) <- pgcplan.GRAPH.EDGES)',
            'pnode_white_live* = $destruction_nodes_delete(pnode_live*, [HOBJECT n_key])',
            'hedge_both* = $gc_ephemeron_collect_edges(S_started, H, pnode_white_live*, H.NODES)',
            '(HEDGE (HOBJECT n_key) (HOBJECT n_value)) <- hedge_both*',
            '(HEDGE (HOBJECT n_map) (HOBJECT n_value)) <- hedge_both*',
            '(HOBJECT n_map) <- $heap_reach([HOBJECT n_key], eps, hedge_both*)',
            '|pgcplan.COUNTED| = 3', 'pgcplan.DTORS = eps',
        ],
        'timeout': 180,
    },
    'peer-partial-entry-free': {
        'source': PEER.decode(),
        'stage': 'S.TODO = (GC_FREE pgcplan) :: ptask_tail* '
                 '-- if pgcplan.CALL.PASS = 0 -- if S.GC.NEXT = 1',
        'checks': [
            '$gc_ephemeron_policy(S)', '$call_task_valid(S, GC_FREE pgcplan)',
            'pgcplan.DTORS = eps', '|pgcplan.COUNTED| = 1',
            '$lookup(S.ENV, $ptascii("wx")) = (n_wx_cell)',
            'S.STORE[n_wx_cell] = DEFINED (POBJECT n_wx)',
            'S.OBJECTS[n_wx] = WEAKREFERENCE (n_x)',
            '$lookup(S.ENV, $ptascii("wd")) = (n_wd_cell)',
            'S.STORE[n_wd_cell] = DEFINED (POBJECT n_wd)',
            'S.OBJECTS[n_wd] = WEAKREFERENCE (n_drop)',
            'pgcplan.FREESET = [HOBJECT n_drop]',
            'pgccall_pass1 = pgcplan.CALL[.PASS = 1]',
            'pgcplan_pass1 = pgcplan[.CALL = pgccall_pass1]',
            'S_pass1 = S[.GC.ACTIVE = (pgccall_pass1)][.GC.PLAN = (pgcplan_pass1)]',
            '~$gc_ephemeron_phase(S_pass1)', '~$gc_ephemeron_policy(S_pass1)',
            'pgcplan_dtor = pgcplan[.DTORS = [HOBJECT n_drop]]',
            'S_dtor = S[.GC.PLAN = (pgcplan_dtor)]',
            '~$gc_ephemeron_phase(S_dtor)', '~$gc_ephemeron_policy(S_dtor)',
            '$lookup(S.ENV, $ptascii("left")) = (n_left_cell)',
            'S.STORE[n_left_cell] = DEFINED (POBJECT n_left)',
            '$lookup(S.ENV, $ptascii("right")) = (n_right_cell)',
            'S.STORE[n_right_cell] = DEFINED (POBJECT n_right)',
            '$lookup(S.ENV, $ptascii("extra")) = (n_extra_cell)',
            'S.STORE[n_extra_cell] = DEFINED (POBJECT n_extra)',
            '$weakmap_entries_contents(S, n_left) = [pweakmapentry_left]',
            '$weakmap_entries_contents(S, n_right) = [pweakmapentry_right]',
            '$weakmap_entries_contents(S, n_extra) = [pweakmapentry_drop]',
            'pweakmapentry_left.KEY = n_a',
            'pweakmapentry_left.BEFORE = eps',
            'pweakmapentry_right.VALUE = POBJECT n_y',
            'pweakmapentry_drop.KEY = n_drop', 'pweakmapentry_drop.VALUE = POBJECT n_x',
            '$heap_owners($heap_graph(S), HOBJECT n_x) = 3',
            '$gc_free_prepare(S, pgcplan) = (S_prepared)',
            'S_prepared.OBJECTS[n_extra] = WEAKMAP eps',
            '$weakmap_entries_contents(S_prepared, n_left) = [pweakmapentry_left]',
            '$weakmap_entries_contents(S_prepared, n_right) = [pweakmapentry_right]',
            '$heap_owners($heap_graph(S_prepared), HOBJECT n_x) = 2',
            '$lookup(S.ENV, $ptascii("outside")) = (n_outside)',
            'S.STORE[n_outside] = DEFINED (PINT 7)',
            'S_step = $drive_steps(S, 1)', 'S_step.COMPLETION = BUDGET',
            '~((HOBJECT n_drop) <- S_step.ALLOCATIONS)',
            '(HOBJECT n_x) <- S_step.ALLOCATIONS',
            'S_step.STORE[n_outside] = DEFINED (PINT 7)',
            '$heap_owners($heap_graph(S_step), HOBJECT n_x) = 2',
            '$drive_steps(S_step[.COMPLETION = NORMAL], 1) = $drive_steps(S, 2)',
            # Derived rank-order and tied-rank controls; source cuts stay fixed.
            'S_order = S[.OBJECTS[n_right] = WEAKMAP (pweakmapentry_right[.KEY = n_a][.ORDER = 2])]',
            '$gc_ephemeron_before(S_order, n_left, n_right, n_a)',
            '$gc_ephemeron_key_payloads(S_order, HOBJECT n_a, eps, S.ALLOCATIONS) = [HOBJECT n_x, HOBJECT n_y]',
            'S_reverse = S_order[.OBJECTS[n_left] = WEAKMAP (pweakmapentry_left[.ORDER = 2])][.OBJECTS[n_right] = WEAKMAP (pweakmapentry_right[.KEY = n_a][.ORDER = 1])]',
            '$gc_ephemeron_before(S_reverse, n_right, n_left, n_a)',
            '$gc_ephemeron_key_payloads(S_reverse, HOBJECT n_a, eps, S.ALLOCATIONS) = [HOBJECT n_y, HOBJECT n_x]',
            'S_unknown = S_order[.OBJECTS[n_right] = WEAKMAP (pweakmapentry_right[.KEY = n_a][.ORDER = 1])][.OBJECTTABLES = [{OBJECT n_x, TABLE 0}]]',
            '~$gc_ephemeron_key_order_safe(S_unknown, n_a)',
        ],
        'timeout': 180,
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
