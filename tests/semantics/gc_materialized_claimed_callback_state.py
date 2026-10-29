#!/usr/bin/env python3
"""Reached claimed callback counts, nested buffer removal, and carried origin."""
import argparse
import hashlib

import gc_materialized_claimed_callback_sources as sources
import shutdown_state_review as runner


AUTHOR = sources.family.CASES['materialized-proxy-first-destructor'].decode()
PEER = b'''<?php
gc_disable();
#[AllowDynamicProperties]
class GcMutatingRoot06 {
    public $first;
    public $second;
    public function __destruct() {
        global $saved, $wr, $wp;
        echo 'D|', $wr->get() === $this ? 'self|' : 'BAD|';
        echo $wp->get() !== null ? 'proxy|' : 'BAD|';
        $before = $this->first;
        $this->first = $this->second;
        $this->second = $before;
        $saved = $this;
    }
}
#[AllowDynamicProperties]
class GcMutatingProxy06 {}
$saved = null;
$root = new GcMutatingRoot06;
$proxy = new GcMutatingProxy06;
$proxy->back = $root;
$table = (array) $proxy;
$root->first = $table;
$root->second = $proxy;
$root->extra = 7;
$wr = WeakReference::create($root);
$wp = WeakReference::create($proxy);
unset($proxy);
echo 'P|', gc_collect_cycles(), '|';
echo $wr->get() !== null && $wp->get() !== null ? 'live|' : 'BAD|';
unset($table);
echo gc_collect_cycles(), '|';
unset($root);
echo gc_collect_cycles(), '|';
echo $wr->get() === $saved && $wp->get() !== null ? 'saved|' : 'BAD|';
unset($saved);
echo 'U|', gc_collect_cycles(), '|';
echo $wr->get() === null && $wp->get() === null ? 'dead|' : 'BAD|';
echo gc_collect_cycles(), '|END';
'''
assert hashlib.sha256(PEER).hexdigest() == 'd9a603dcecfe480ec32d659ade719c0544f10ada4bfffd3316861f86cee6e45e'
TWO_CALLS = PEER.replace(
    b"echo $wr->get() === $saved && $wp->get() !== null ? 'saved|' : 'BAD|';",
    b"echo $wp->get() !== $wr->get() && $wr->get() !== $wp->get() && "
    b"$wr->get() === $saved ? 'saved|' : 'BAD|';",
)
assert hashlib.sha256(TWO_CALLS).hexdigest() == 'a6c37e3b363aeb001f68bc99475fcf6d94b4b69f774532c2c4afebd2f8907606'
PRUNED = b'''<?php
gc_disable();
#[AllowDynamicProperties]
class GcPrunedRoot06 {
    public $first;
    public $second;
    public function __destruct() {
        global $saved, $wr, $wp;
        echo 'D|', $wr->get() === $this ? 'self|' : 'BAD|';
        echo $wp->get() !== null ? 'proxy|' : 'BAD|';
        $before = $this->first;
        $this->first = null;
        $this->second = $this;
        echo $wp->get() === null ? 'pruned|' : 'BAD|';
        $saved = $this;
    }
}
#[AllowDynamicProperties]
class GcPrunedProxy06 {}
$saved = null;
$root = new GcPrunedRoot06;
$proxy = new GcPrunedProxy06;
$proxy->back = $root;
$table = (array) $proxy;
$root->first = $table;
$root->second = $proxy;
$root->extra = 7;
$wr = WeakReference::create($root);
$wp = WeakReference::create($proxy);
unset($proxy);
echo 'P|', gc_collect_cycles(), '|';
echo $wr->get() !== null && $wp->get() !== null ? 'live|' : 'BAD|';
unset($table);
echo gc_collect_cycles(), '|';
unset($root);
echo gc_collect_cycles(), '|';
echo $wr->get() === $saved && $wp->get() === null ? 'saved|' : 'BAD|';
unset($saved);
echo 'U|', gc_collect_cycles(), '|';
echo $wr->get() === null && $wp->get() === null ? 'dead|' : 'BAD|';
echo gc_collect_cycles(), '|END';
'''
assert hashlib.sha256(PRUNED).hexdigest() == 'f36e841d67da2be1c8b78acc300984c24f5acbf1d92f544bd03ff0cca83024f7'


CASES = {
    'identity-method-result-borrowed-base': {
        'source': PEER.decode(),
        'stage': 'S.TODO = METHOD_RESULT :: ptask_tail* -- if S.GC.NEXT = 3 '
        '-- if S.CURRENT = eps -- if S.RESULT = KNOWN (POBJECT n_root)',
        'checks': [
            'S.BASE = BASE_VALUE (KNOWN PNULL)',
            'S_step = $drive_steps(S, 1)',
            'S_step.COMPLETION = BUDGET',
            'S_step.RESULT = KNOWN (POBJECT n_root)',
            'S_step.BASE = BASE_VALUE (KNOWN (POBJECT n_root))',
            '$gc_binary_left_cache_prefix(S_step, S_step.TODO, S_step.ORIGIN)',
            '$machine_base_roots(S_step) = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_root) = '
            '$heap_owners($heap_graph(S_step), HOBJECT n_root)',
            'S_step.GC.BUFFER = S.GC.BUFFER',
            '$lookup(S.ENV, $ptascii("wp")) = (n_wp_cell)',
            'S.STORE[n_wp_cell] = DEFINED (POBJECT n_wp)',
            '$machine_base_roots(S_step[.SOURCES = eps]) = [HOBJECT n_root]',
            '$machine_base_roots(S_step[.BASE = BASE_VALUE (KNOWN (POBJECT n_wp))]) = '
            '[HOBJECT n_wp]',
            '$machine_base_roots(S_step[.BASE = BASE_NAME (KNOWN (POBJECT n_root)) 0]) = '
            '[HOBJECT n_root]',
        ], 'timeout': 180,
    },
    'identity-two-call-right-method-result': {
        'source': TWO_CALLS.decode(),
        'stage': 'S.TODO = METHOD_RESULT :: ptask_tail* -- if S.GC.NEXT = 3 '
        '-- if S.CURRENT = eps -- if S.RESULT = KNOWN (POBJECT n_root) '
        '-- if $lookup(S.ENV, $ptascii("wr")) = (n_wr_cell) '
        '-- if S.STORE[n_wr_cell] = DEFINED (POBJECT n_wr) '
        '-- if S.OBJECTS[n_wr] = WEAKREFERENCE (n_root)',
        'checks': [
            '$lookup(S.ENV, $ptascii("wp")) = (n_wp_cell)',
            'S.STORE[n_wp_cell] = DEFINED (POBJECT n_wp)',
            'S.OBJECTS[n_wp] = WEAKREFERENCE (n_proxy)',
            '$gc_binary_right_cache_scan(S, S.TODO, S.ORIGIN, KNOWN (POBJECT n_proxy))',
            'S.BASE = BASE_VALUE (KNOWN PNULL)',
            'n_root =/= n_proxy',
            'S_step = $drive_steps(S, 1)',
            'S_step.COMPLETION = BUDGET',
            'S_step.RESULT = KNOWN (POBJECT n_root)',
            'S_step.BASE = BASE_VALUE (KNOWN (POBJECT n_root))',
            '$gc_binary_right_cache_scan(S_step, S_step.TODO, S_step.ORIGIN, '
            'KNOWN (POBJECT n_root))',
            '$machine_base_roots(S_step) = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_root) = '
            '$heap_owners($heap_graph(S_step), HOBJECT n_root)',
            '$heap_owners($heap_graph(S), HOBJECT n_proxy) = '
            '$heap_owners($heap_graph(S_step), HOBJECT n_proxy)',
            'S_step.GC.BUFFER = S.GC.BUFFER',
        ], 'timeout': 180,
    },
    'identity-two-call-two-temps': {
        'source': TWO_CALLS.decode(),
        'stage': 'S.TODO = (BINARY_RIGHT NOTIDENTICAL poperand_left z) :: ptask_tail* '
        '-- if S.GC.NEXT = 3 -- if S.CURRENT = eps '
        '-- if poperand_left = KNOWN (POBJECT n_proxy) '
        '-- if S.RESULT = KNOWN (POBJECT n_root)',
        'checks': [
            'n_root =/= n_proxy',
            'S.BASE = BASE_VALUE (KNOWN (POBJECT n_root))',
            '$machine_base_roots(S) = eps',
            'PhpStep: S ~> S_raw',
            'S_raw.COMPLETION = NORMAL',
            'S_raw.TODO = ptask_tail*',
            'S_raw.RESULT = KNOWN (PBOOL true)',
            'S_step = $drive_steps(S, 1)',
            'S_step.COMPLETION = BUDGET',
            'S_step.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionoperation.NOGC = eps',
            'pdestructionoperation.NOGCEXTRA = [pgctemporary_left, pgctemporary_right]',
            'pgctemporary_left.OPERAND = KNOWN (POBJECT n_proxy)',
            'pgctemporary_right.OPERAND = KNOWN (POBJECT n_root)',
            'pdestructionrelease.JOBS = [DESTRUCTION_TEMP (HOBJECT n_proxy), '
            'DESTRUCTION_TEMP (HOBJECT n_root)]',
            '$gc_operation_metadata_valid(S_step[.COMPLETION = NORMAL], pdestructionoperation)',
        ], 'timeout': 180,
    },
    'identity-two-produced-same-root': {
        'source': PEER.decode(),
        'stage': 'S.TODO = (BINARY_RIGHT IDENTICAL poperand_left z) :: ptask_tail* '
        '-- if S.GC.NEXT = 3 -- if S.CURRENT = (pcallcontext) '
        '-- if poperand_left = KNOWN (POBJECT n_root) -- if S.RESULT = KNOWN (POBJECT n_root)',
        'checks': [
            'S.ORIGIN = (porigin)',
            '$origin_node(S.SOURCES, porigin) = (pcnode)',
            '$error_binary_source(pcnode) = (IDENTICAL)',
            'PhpStep: S ~> S_raw',
            'S_raw.COMPLETION = NORMAL',
            'S_raw.TODO = ptask_tail*',
            'S_raw.RESULT = KNOWN (PBOOL true)',
            'S.BASE = BASE_VALUE poperand_left',
            '$machine_base_roots(S) = eps',
            'S_step = $drive_steps(S, 1)',
            'S_step.COMPLETION = BUDGET',
            'S_step.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionoperation.NOGC = eps',
            'pdestructionoperation.NOGCEXTRA = [pgctemporary_left, pgctemporary_right]',
            'pgctemporary_left.OPERAND = KNOWN (POBJECT n_root)',
            'pgctemporary_right.OPERAND = KNOWN (POBJECT n_root)',
            'pgctemporary_left.PENDING',
            'pgctemporary_right.PENDING',
            'pdestructionrelease.JOBS = [DESTRUCTION_TEMP (HOBJECT n_root), '
            'DESTRUCTION_TEMP (HOBJECT n_root)]',
            '$gc_operation_metadata_valid(S_step[.COMPLETION = NORMAL], pdestructionoperation)',
            'S_one = $drive_steps(S_step[.COMPLETION = NORMAL], 1)',
            'S_one.COMPLETION = BUDGET',
            'pdestructionoperation[.NOGCEXTRA = [pgctemporary_left[.PENDING = false], '
            'pgctemporary_right]] <- S_one.DESTRUCTION.OPERATIONS',
            'S_two = $drive_steps(S_one[.COMPLETION = NORMAL], 1)',
            'S_two.COMPLETION = BUDGET',
            'pdestructionoperation_done = pdestructionoperation[.NOGCEXTRA = '
            '[pgctemporary_left[.PENDING = false], pgctemporary_right[.PENDING = false]]]',
            'pdestructionoperation_done <- S_two.DESTRUCTION.OPERATIONS',
            '$gc_operation_metadata_valid(S_two[.COMPLETION = NORMAL], pdestructionoperation_done)',
            '$drive_steps(S_step[.COMPLETION = NORMAL], 2) = S_two',
        ], 'timeout': 180,
    },
    'identity-produced-operand-no-gc-root': {
        'source': PEER.decode(),
        'stage': 'S.TODO = (BINARY_RIGHT NOTIDENTICAL poperand_left z) :: ptask_tail* '
        '-- if S.GC.NEXT = 3 -- if S.CURRENT = eps -- if S.RESULT = KNOWN PNULL '
        '-- if poperand_left = KNOWN (POBJECT n_proxy)',
        'checks': [
            'S.ORIGIN = (porigin)',
            '$origin_node(S.SOURCES, porigin) = (pcnode)',
            '$error_binary_source(pcnode) = (NOTIDENTICAL)',
            '$lookup(S.ENV, $ptascii("wp")) = (n_wp_cell)',
            'S.STORE[n_wp_cell] = DEFINED (POBJECT n_wp)',
            'S.OBJECTS[n_wp] = WEAKREFERENCE (n_proxy)',
            '(HOBJECT n_wp) <- $gc_physical_nodes(S.GC.BUFFER)',
            '~((HOBJECT n_proxy) <- $gc_physical_nodes(S.GC.BUFFER))',
            'PhpStep: S ~> S_raw',
            'S_raw.COMPLETION = NORMAL',
            'S_raw.TODO = ptask_tail*',
            'S_raw.RESULT = KNOWN (PBOOL true)',
            'S.BASE = BASE_VALUE poperand_left',
            '$machine_base_roots(S) = eps',
            '$gc_binary_temp_receipt(poperand_left) = [{OPERAND KNOWN (POBJECT n_proxy), PENDING true}]',
            'n_name* = $ptascii("saved")',
            '$gc_binary_temp_receipt(VARIABLE n_name* z) = eps',
            '$gc_binary_temp_receipt(REFERENCE n_wp_cell) = eps',
            '$gc_multi_temporary_jobs([HOBJECT n_proxy, HOBJECT n_proxy], [HOBJECT n_proxy]) = '
            '[DESTRUCTION_TEMP (HOBJECT n_proxy), DESTRUCTION_VALUE (HOBJECT n_proxy)]',
            'S_step = $drive_steps(S, 1)',
            'S_step.COMPLETION = BUDGET',
            'S_step.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
            'pdestructionoperation.VALUE = KNOWN (PBOOL true)',
            'pdestructionoperation.NOGC = eps',
            'pdestructionoperation.NOGCEXTRA = [pgctemporary]',
            'pgctemporary.OPERAND = KNOWN (POBJECT n_proxy)',
            'pgctemporary.PENDING',
            'pdestructionrelease.JOBS = [DESTRUCTION_TEMP (HOBJECT n_proxy)]',
            '$gc_operation_metadata_valid(S_step[.COMPLETION = NORMAL], pdestructionoperation)',
            '(HOBJECT n_wp) <- $gc_physical_nodes(S_step.GC.BUFFER)',
            '~((HOBJECT n_proxy) <- $gc_physical_nodes(S_step.GC.BUFFER))',
            'S_release = $drive_steps(S_step[.COMPLETION = NORMAL], 1)',
            'S_release.COMPLETION = BUDGET',
            'pdestructionoperation[.NOGCEXTRA = [pgctemporary[.PENDING = false]]] <- '
            'S_release.DESTRUCTION.OPERATIONS',
            '(HOBJECT n_wp) <- $gc_physical_nodes(S_release.GC.BUFFER)',
            '~((HOBJECT n_proxy) <- $gc_physical_nodes(S_release.GC.BUFFER))',
        ], 'timeout': 180,
    },
    'proxy-first-nested-debit': {
        'source': AUTHOR,
        'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* -- if pgccall.PASS = 0 -- if S.GC.NEXT = 3',
        'checks': [
            '$call_task_valid(S, GC_TRACE pgccall)',
            'pgccall.COUNT_SOURCE = (pgccountsource)',
            'pgccountsource.DTORS = [HOBJECT n_root]',
            'S.GC.BUFFER = [GC_ROOT (HOBJECT n_root)]',
            'S.GC.FREE = eps',
            '$gc_callback_count_image(pgccountsource)',
            'pgcplan = $gc_plan(S, pgccall)',
            'pgcplan.WEAK = (eps)',
            '$gc_callback_count_plan_image(pgcplan, pgccountsource)',
            'pgcplan.DTORS = [HOBJECT n_root]',
            '|pgcplan.COUNTED| = 3',
            '$lookup(S.ENV, $ptascii("wp")) = (n_wp_cell)',
            'S.STORE[n_wp_cell] = DEFINED (POBJECT n_wp)',
            'S.OBJECTS[n_wp] = WEAKREFERENCE (n_proxy)',
            '$object_table_at(S.OBJECTTABLES, n_proxy) = (n_shared_table)',
            'H_physical = $heap_graph(S)',
            '$heap_owners(H_physical, HOBJECT n_root) = 1',
            '$heap_owners(H_physical, HARRAY n_shared_table) = 2',
            'H = pgcplan.GRAPH',
            'pnode_roots* = $gc_eligible_nodes(pgcplan.BUFFER)',
            'pnode_white* = $gc_white(H, pnode_roots*)',
            '$gc_count_walk(H, pgcplan.PROXIES, eps, $gc_root_visits(pnode_roots*), pnode_white*) = '
            '(pnode_old_visit*, pnode_old_counted*)',
            '|pnode_old_counted*| = 2',
            '~$gc_callback_walk_agrees(pgcplan)',
            '$gc_callback_nested_plan(pgcplan)',
            '(pgcslot_nested*, nat_free*, n_debit) = $gc_callback_nested_image(pgcplan)',
            'n_debit = 2',
            'pgcslot_nested* = [GC_DTOR_ROOT n_root, GC_EMPTY, GC_EMPTY]',
            'nat_free* = [2, 1]',
            '$gc_pass_count(pgcplan) = 1',
            'S_step = $drive_steps(S, 1)',
            'S_step.COMPLETION = BUDGET',
            'S_step.TODO = (GC_DTORS pgcplan) :: ptask_tail*',
            'S_step.GC.BUFFER = pgcslot_nested*',
            'S_step.GC.FREE = nat_free*',
            '$gc_callback_nested_state(S_step[.COMPLETION = NORMAL], pgcplan)',
            '$call_task_valid(S_step[.COMPLETION = NORMAL], GC_DTORS pgcplan)',
            '$drive_steps(S_step[.COMPLETION = NORMAL], 1) = $drive_steps(S, 2)',
        ], 'timeout': 180,
    },
    'author-pass1-total-four': {
        'source': AUTHOR,
        'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* -- if pgccall.PASS = 1 -- if S.GC.NEXT = 3',
        'checks': [
            '$call_task_valid(S, GC_TRACE pgccall)',
            'pgccall.COUNT_SOURCE = (pgccountsource)',
            'pgccountsource.DTORS = [HOBJECT n_root]',
            'S.GC.PLAN = (pgcplan_prior)',
            'pgcplan_prior.CALL = pgccall',
            'pgcplan_prior.INDEX = |pgcplan_prior.DTORS|',
            'pgcplan_prior.STEPS = [GC_CALLED (HOBJECT n_root)]',
            'pgcplan_prior.DONE = [HOBJECT n_root]',
            '$gc_callback_count_plan_image(pgcplan_prior, pgccountsource)',
            'pgccall.TOTAL = 1',
            'pgcplan = $gc_plan(S, pgccall)',
            'pgcplan.WEAK = (eps)',
            'pgcplan.DTORS = eps',
            '|pgcplan.COUNTED| = 3',
            '$gc_pass_count(pgcplan) = 3',
            'S_step = $drive_steps(S, 1)',
            'S_step.COMPLETION = BUDGET',
            'S_step.TODO = (GC_DTORS pgcplan) :: ptask_tail*',
            'S_free = $drive_steps(S, 2)',
            'S_free.COMPLETION = BUDGET',
            'S_free.TODO = (GC_FREE pgcplan) :: ptask_tail*',
            '$call_task_valid(S_free[.COMPLETION = NORMAL], GC_FREE pgcplan)',
            'S_done = $drive_steps(S_free[.COMPLETION = NORMAL], 1)',
            'S_done.COMPLETION = BUDGET',
            'S_done.RESULT = KNOWN (PINT 4)',
            '$lookup(S.ENV, $ptascii("wr")) = (n_wr_cell)',
            'S.STORE[n_wr_cell] = DEFINED (POBJECT n_wr)',
            'S.OBJECTS[n_wr] = WEAKREFERENCE (n_root)',
            '$lookup(S.ENV, $ptascii("wp")) = (n_wp_cell)',
            'S.STORE[n_wp_cell] = DEFINED (POBJECT n_wp)',
            'S.OBJECTS[n_wp] = WEAKREFERENCE (n_proxy)',
            '~((HOBJECT n_root) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_proxy) <- S_done.ALLOCATIONS)',
            'S_done = $drive_steps(S, 3)',
        ], 'timeout': 180,
    },
    'peer-equal-image-source-forgery': {
        'source': PEER.decode(),
        'stage': 'S.TODO = (GC_DTORS pgcplan) :: ptask_tail* -- if pgcplan.CALL.PASS = 0 -- if S.GC.NEXT = 3 -- if pgcplan.INDEX = 0',
        'checks': [
            '$call_task_valid(S, GC_DTORS pgcplan)',
            '$gc_snapshot_fresh(S, pgcplan)',
            'pgcplan.CALL.COUNT_SOURCE = (pgccountsource)',
            'pgcplan.DTORS = [HOBJECT n_root]',
            'pgcplan.WEAK = (eps)',
            '$gc_callback_walk_agrees(pgcplan)',
            '$gc_callback_nested_plan(pgcplan)',
            '(pgcslot_nested*, nat_free*, n_debit) = $gc_callback_nested_image(pgcplan)',
            'n_debit = 3',
            'S.GC.BUFFER = pgcslot_nested*',
            'S.GC.FREE = nat_free*',
            'pgccall_erased = pgcplan.CALL[.COUNT_SOURCE = eps]',
            'pgcplan_erased = pgcplan[.CALL = pgccall_erased][.WEAK = eps]',
            'S_erased = S[.GC.ACTIVE = (pgccall_erased)][.GC.PLAN = (pgcplan_erased)]'
            '[.TODO = (GC_DTORS pgcplan_erased) :: ptask_tail*]',
            '$gc_callback_count_required_plan(S_erased, pgcplan_erased)',
            'S_snapshot = S_erased[.GC.PLAN = eps][.GC.BUFFER = pgcplan.BUFFER][.GC.FREE = eps]',
            '$gc_callback_count_origin(S_snapshot) = (pgccountsource)',
            '~$gc_snapshot_count_source(S_snapshot, pgccall_erased)',
            '~$gc_plan_valid(S_erased, pgcplan_erased)',
        ], 'timeout': 180,
    },
    'peer-mutation-resurrection-and-erasure': {
        'source': PEER.decode(),
        'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* -- if pgccall.PASS = 1 -- if S.GC.NEXT = 3',
        'checks': [
            '$call_task_valid(S, GC_TRACE pgccall)',
            'pgccall.COUNT_SOURCE = (pgccountsource)',
            'pgccountsource.DTORS = [HOBJECT n_root]',
            'S.GC.PLAN = (pgcplan_prior)',
            'pgcplan_prior.CALL = pgccall',
            'pgcplan_prior.STEPS = [GC_CALLED (HOBJECT n_root)]',
            'pgcplan_prior.DONE = [HOBJECT n_root]',
            '$gc_callback_count_plan_image(pgcplan_prior, pgccountsource)',
            'pgccall.TOTAL = 0',
            '$lookup(S.ENV, $ptascii("saved")) = (n_saved_cell)',
            'S.STORE[n_saved_cell] = DEFINED (POBJECT n_root)',
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
            '$drive_steps(S_step[.COMPLETION = NORMAL], 1) = $drive_steps(S, 2)',
            'S_done = $drive_steps(S, 3)',
            'S_done.COMPLETION = BUDGET',
            'S_done.RESULT = KNOWN (PINT 0)',
        ], 'timeout': 180,
    },
    'peer-first-plan-origin-and-later-called': {
        'source': PEER.decode(),
        'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* -- if pgccall.PASS = 0 -- if S.GC.NEXT = 4',
        'checks': [
            '$call_task_valid(S, GC_TRACE pgccall)',
            'pgccall.COUNT_SOURCE = (pgccountsource)',
            'pgccountsource.DTORS = eps',
            '$gc_callback_count_image(pgccountsource)',
            'pgcplan = $gc_plan(S, pgccall)',
            'pgcplan.WEAK = (eps)',
            'pgcplan.DTORS = eps',
            '|pgcplan.COUNTED| = 3',
            '$gc_pass_count(pgcplan) = 3',
            'S_step = $drive_steps(S, 1)',
            'S_step.COMPLETION = BUDGET',
            'S_step.TODO = (GC_DTORS pgcplan) :: ptask_tail*',
            'S_free = $drive_steps(S, 2)',
            'S_free.COMPLETION = BUDGET',
            'S_free.TODO = (GC_FREE pgcplan) :: ptask_tail*',
            '$call_task_valid(S_free[.COMPLETION = NORMAL], GC_FREE pgcplan)',
            'S_done = $drive_steps(S, 3)',
            'S_done.COMPLETION = BUDGET',
            'S_done.RESULT = KNOWN (PINT 3)',
            '$lookup(S.ENV, $ptascii("wr")) = (n_wr_cell)',
            'S.STORE[n_wr_cell] = DEFINED (POBJECT n_wr)',
            'S.OBJECTS[n_wr] = WEAKREFERENCE (n_root)',
            '$lookup(S.ENV, $ptascii("wp")) = (n_wp_cell)',
            'S.STORE[n_wp_cell] = DEFINED (POBJECT n_wp)',
            'S.OBJECTS[n_wp] = WEAKREFERENCE (n_proxy)',
            '$object_table_at(S.OBJECTTABLES, n_proxy) = (n_shared_table)',
            '$objectprops_at(S.OBJECTPROPS, n_root) = (ppropertyslot*)',
            '$property_slot_at(ppropertyslot*, $ptascii("first")) = (ppropertyslot_first)',
            'ppropertyslot_first.STATE = PROP_VALUE (DIRECT (POBJECT n_proxy))',
            '$property_slot_at(ppropertyslot*, $ptascii("second")) = (ppropertyslot_second)',
            'ppropertyslot_second.STATE = PROP_VALUE (DIRECT (PARRAY n_shared_table))',
            '~((HOBJECT n_root) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_proxy) <- S_done.ALLOCATIONS)',
        ], 'timeout': 180,
    },
    'pruned-origin-pass1': {
        'source': PRUNED.decode(),
        'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* -- if pgccall.PASS = 1 -- if S.GC.NEXT = 3',
        'checks': [
            '$call_task_valid(S, GC_TRACE pgccall)',
            'pgccall.COUNT_SOURCE = (pgccountsource)',
            'pgccountsource.DTORS = [HOBJECT n_root]',
            '$lookup(S.ENV, $ptascii("wp")) = (n_wp_cell)',
            'S.STORE[n_wp_cell] = DEFINED (POBJECT n_wp)',
            'S.OBJECTS[n_wp] = WEAKREFERENCE (n_proxy)',
            'pgccountsource.TABLE.OBJECT = n_proxy',
            'n_shared_table = pgccountsource.TABLE.TABLE',
            '(HOBJECT n_proxy) <- pgccountsource.GRAPH.NODES',
            '(HARRAY n_shared_table) <- pgccountsource.GRAPH.NODES',
            '~((HOBJECT n_proxy) <- S.ALLOCATIONS)',
            '~((HARRAY n_shared_table) <- S.ALLOCATIONS)',
            '~(pgccountsource.TABLE <- S.OBJECTTABLES)',
            '$lookup(S.ENV, $ptascii("saved")) = (n_saved_cell)',
            'S.STORE[n_saved_cell] = DEFINED (POBJECT n_root)',
            '$heap_owners($heap_graph(S), HOBJECT n_root) = 2',
            'S.GC.PLAN = (pgcplan_prior)',
            'pgcplan_prior.CALL = pgccall',
            'pgcplan_prior.INDEX = |pgcplan_prior.DTORS|',
            'pgcplan_prior.STEPS = [GC_CALLED (HOBJECT n_root)]',
            'pgcplan_prior.DONE = [HOBJECT n_root]',
            '$gc_callback_count_image(pgccountsource)',
            '$gc_callback_count_kind(S, pgccountsource)',
            '$gc_callback_count_plan_image(pgcplan_prior, pgccountsource)',
            'pgcplan = $gc_plan(S, pgccall)',
            'pgcplan.WEAK = (eps)',
            'pgcplan.DTORS = eps',
            'pgcplan.FREESET = eps',
            'S_step = $drive_steps(S, 1)',
            'S_step.COMPLETION = BUDGET',
            'S_step.TODO = (GC_DTORS pgcplan) :: ptask_tail*',
            'S_done = $drive_steps(S, 3)',
            'S_done.COMPLETION = BUDGET',
            'S_done.RESULT = KNOWN (PINT 0)',
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
