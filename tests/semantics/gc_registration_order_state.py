#!/usr/bin/env python3
"""Strict source-reached WeakMap registration and white-worklist checks."""
import argparse
import hashlib

import gc_registration_order_sources as sources
import shutdown_state_review as runner


PEER_CBA = b'''<?php
#[AllowDynamicProperties]
class ReviewBag {}
$mapA = new WeakMap;
$mapB = new WeakMap;
$mapC = new WeakMap;
$key = new stdClass;
$a = new ReviewBag;
$b = new ReviewBag;
$oldC = new ReviewBag;
$c = new ReviewBag;
echo 'P|';
$mapC[$key] = $oldC;
$mapA[$key] = $a;
$mapB[$key] = $b;
$mapC[$key] = $c;
unset($oldC);
unset($mapA[$key]);
$mapA[$key] = $a;
$c->back = $key;
$table = (array) $c;
$a->view = $table;
$b->also = $table;
$b->back = $c;
$key->self = $key;
$weakKey = WeakReference::create($key);
$weakA = WeakReference::create($a);
$weakB = WeakReference::create($b);
$weakC = WeakReference::create($c);
$outside = $table;
$heldKey = $key;
unset($key, $a, $b, $c, $table);
echo gc_collect_cycles(), '|';
echo $weakKey->get() !== null && $weakA->get() !== null
    && $weakB->get() !== null && $weakC->get() !== null ? 'live|' : 'BAD-live|';
unset($outside);
echo gc_collect_cycles(), '|';
unset($heldKey);
echo gc_collect_cycles(), '|';
echo $weakKey->get() === null && $weakA->get() === null
    && $weakB->get() === null && $weakC->get() === null ? 'dead|' : 'BAD-dead|';
unset($mapA, $mapB, $mapC);
echo gc_collect_cycles(), '|END';
'''
PEER_ABC = PEER_CBA.replace(b'unset($mapA[$key]);\n$mapA[$key] = $a;',
                            b'unset($mapC[$key]);\n$mapC[$key] = $c;')
assert hashlib.sha256(PEER_CBA).hexdigest() == '93f404cbfe3f488ce35de5133e0c9b09decc66d47c7f56efa1934aef505e174f'
assert hashlib.sha256(PEER_ABC).hexdigest() == '2cf90765fc896518e0167c4752bb81f0bc58659c0d72b6215aa806b4f6bb4e33'


def peer_case(source, ranks, ordered, first, count, table_counted):
    checks = [
        '$gc_ephemeron_policy(S)', '$call_task_valid(S, GC_FREE pgcplan)',
        'pgcplan.DTORS = eps', 'pgcplan.WEAK = (hedge_weak*)',
        'H = pgcplan.GRAPH', '$heap_valid(H)',
        '$lookup(S.ENV, $ptascii("weakKey")) = (n_weak_key_cell)',
        'S.STORE[n_weak_key_cell] = DEFINED (POBJECT n_weak_key)',
        'S.OBJECTS[n_weak_key] = WEAKREFERENCE (n_key)',
        '$lookup(S.ENV, $ptascii("weakA")) = (n_weak_a_cell)',
        'S.STORE[n_weak_a_cell] = DEFINED (POBJECT n_weak_a)',
        'S.OBJECTS[n_weak_a] = WEAKREFERENCE (n_a)',
        '$lookup(S.ENV, $ptascii("weakB")) = (n_weak_b_cell)',
        'S.STORE[n_weak_b_cell] = DEFINED (POBJECT n_weak_b)',
        'S.OBJECTS[n_weak_b] = WEAKREFERENCE (n_b)',
        '$lookup(S.ENV, $ptascii("weakC")) = (n_weak_c_cell)',
        'S.STORE[n_weak_c_cell] = DEFINED (POBJECT n_weak_c)',
        'S.OBJECTS[n_weak_c] = WEAKREFERENCE (n_c)',
        '$lookup(S.ENV, $ptascii("mapA")) = (n_map_a_cell)',
        'S.STORE[n_map_a_cell] = DEFINED (POBJECT n_map_a)',
        '$lookup(S.ENV, $ptascii("mapB")) = (n_map_b_cell)',
        'S.STORE[n_map_b_cell] = DEFINED (POBJECT n_map_b)',
        '$lookup(S.ENV, $ptascii("mapC")) = (n_map_c_cell)',
        'S.STORE[n_map_c_cell] = DEFINED (POBJECT n_map_c)',
        '$weakmap_entries_find($weakmap_entries_contents(S, n_map_a), n_key) = (pweakmapentry_a)',
        '$weakmap_entries_find($weakmap_entries_contents(S, n_map_b), n_key) = (pweakmapentry_b)',
        '$weakmap_entries_find($weakmap_entries_contents(S, n_map_c), n_key) = (pweakmapentry_c)',
        f'pweakmapentry_a.ORDER = {ranks[0]}', f'pweakmapentry_b.ORDER = {ranks[1]}',
        f'pweakmapentry_c.ORDER = {ranks[2]}',
        '$gc_ephemeron_key_order_safe(S, n_key)',
        '$gc_ephemeron_key_records(S, n_key, S.ALLOCATIONS) = '
        '[' + ', '.join('pweakmapentry_' + letter for letter in ordered) + ']',
        '$heap_children(HOBJECT n_key, hedge_weak*) = '
        '[' + ', '.join('HOBJECT n_' + letter for letter in ordered) + ']',
        '$object_table_at(S.OBJECTTABLES, n_c) = (n_table)',
        '(HARRAY n_table) <- pgcplan.FREESET',
        f'|pgcplan.COUNTED| = {count}', f'$gc_pass_count(pgcplan) = {count}',
        'pnode_roots* = $gc_eligible_nodes(pgcplan.BUFFER)',
        'pnode_white* = $gc_white(H, pnode_roots*)',
        '$gc_count_walk(H, pgcplan.PROXIES, pgcplan.WEAK, '
        '$gc_root_visits(pnode_roots*), pnode_white*) = (pnode_visit*, pnode_counted*)',
        'pnode_visit* = pgcplan.FREESET',
        'pnode_counted* = pgcplan.COUNTED',
        'pnode_visit*[0] = HOBJECT n_key',
        f'pnode_visit*[1] = HOBJECT n_{first}',
        f'|pnode_counted*| = {count}',
    ]
    checks.append(('' if table_counted else '~') + '((HARRAY n_table) <- pgcplan.COUNTED)')
    checks += [
        'S_step = $drive_steps(S, 1)', 'S_step.COMPLETION = BUDGET',
        f'S_step.RESULT = KNOWN (PINT {count})',
        '~((HOBJECT n_key) <- S_step.ALLOCATIONS)',
        '$drive_steps(S_step[.COMPLETION = NORMAL], 1) = $drive_steps(S, 2)',
    ]
    if ordered == 'cba':
        checks += [
            # These alter the matching consumer and installed plan together.
            'pgcplan_missing = pgcplan[.WEAK = eps]',
            'S_missing = S[.GC.PLAN = (pgcplan_missing)][.TODO = (GC_FREE pgcplan_missing) :: ptask_tail*]',
            '~$call_task_valid(S_missing, GC_FREE pgcplan_missing)',
            'pgcplan_wrong = pgcplan[.WEAK = ([HEDGE (HOBJECT n_key) (HOBJECT n_a)])]',
            'S_wrong = S[.GC.PLAN = (pgcplan_wrong)][.TODO = (GC_FREE pgcplan_wrong) :: ptask_tail*]',
            '~$call_task_valid(S_wrong, GC_FREE pgcplan_wrong)',
            'S_tied = S[.OBJECTS[n_map_a] = WEAKMAP (pweakmapentry_a[.ORDER = 1])]',
            '~$gc_ephemeron_key_order_safe(S_tied, n_key)',
            'pgccall_pass1 = pgcplan.CALL[.PASS = 1]',
            'pgcplan_pass1 = pgcplan[.CALL = pgccall_pass1]',
            'S_pass1 = S[.GC.ACTIVE = (pgccall_pass1)][.GC.PLAN = (pgcplan_pass1)][.TODO = (GC_FREE pgcplan_pass1) :: ptask_tail*]',
            '~$gc_ephemeron_phase(S_pass1)',
            'pgcplan_dtor = pgcplan[.DTORS = [HOBJECT n_key]]',
            'S_dtor = S[.GC.PLAN = (pgcplan_dtor)][.TODO = (GC_FREE pgcplan_dtor) :: ptask_tail*]',
            '~$gc_ephemeron_phase(S_dtor)',
        ]
    return {'source': source.decode(),
            'stage': 'S.TODO = (GC_FREE pgcplan) :: ptask_tail* '
                     '-- if pgcplan.CALL.PASS = 0 -- if S.GC.NEXT = 3',
            'checks': checks, 'timeout': 180}


CASES = {
    'discarded-first-insertion': {
        'source': sources.family.CASES['reverse-two-proxy'].decode(),
        'stage': 'S.TODO = (ASSIGN_ARRAY (BASE_DIM (BASE_VALUE poperand_base) '
                 'poperand_key z_key) z false) :: ptask_tail* '
                 '-- if $access_set_plan(S) = (paccess) '
                 '-- if paccess.OBJECT = (n_map) '
                 '-- if S.OBJECTS[n_map] = WEAKMAP eps',
        'checks': [
            '$lookup(S.ENV, $ptascii("right")) = (n_right_cell)',
            'S.STORE[n_right_cell] = DEFINED (POBJECT n_map)',
            '$lookup(S.ENV, $ptascii("key")) = (n_key_cell)',
            'S.STORE[n_key_cell] = DEFINED (POBJECT n_key)',
            '$lookup(S.ENV, $ptascii("proxy")) = (n_proxy_cell)',
            'S.STORE[n_proxy_cell] = DEFINED (POBJECT n_proxy)',
            'paccess.RHS = S.RESULT',
            'paccess_live = paccess[.SELECTED = $rcontainer_selected(S, paccess.RHS)]'
            '[.VALUE = POBJECT n_proxy][.OFFSET = POBJECT n_key]'
            '[.PHASE = ACCESS_CALL $ptascii("offsetSet")]',
            '$weakmap_write_allowed(S, paccess_live)',
            '$destructor_return_discarded(ptask_tail*)',
            '$weakmap_insert_result(S, paccess_live) = (S, PNULL)',
            'PhpStep: S ~> S_written',
            'S_written.OBJECTS[n_map] = WEAKMAP ({KEY n_key, VALUE POBJECT n_proxy, BEFORE eps, ORDER 1})',
            'S_written.RESULT = KNOWN PNULL',
            '~((HOBJECT n_proxy) <- $gc_nodes(S_written.GC.BUFFER))',
            'S_drive = $drive_steps(S, 1)',
            'S_drive.COMPLETION = BUDGET',
            'S_drive.RESULT = KNOWN PNULL',
            '~((HOBJECT n_proxy) <- $gc_nodes(S_drive.GC.BUFFER))',
            # A used result is a derived task-tail control, not a source claim.
            'S_used = S[.TODO = [paccess.TASK]]',
            '~$destructor_return_discarded(eps)',
            '$weakmap_insert_result(S_used, paccess_live) = (S_used_read, POBJECT n_proxy)',
            'S_used_read.COMPLETION = NORMAL',
        ], 'timeout': 180,
    },
    'two-key-independent-ranks': {
        'source': sources.family.CASES['interleaved-two-keys'].decode(),
        'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
                 '-- if pconfigcall.KIND = INTRINSIC_GC_COLLECT -- if S.GC.NEXT = 0',
        'checks': [
            '$gc_ephemeron_policy(S)',
            '$lookup(S.ENV, $ptascii("wone")) = (n_wone_cell)',
            'S.STORE[n_wone_cell] = DEFINED (POBJECT n_wone)',
            'S.OBJECTS[n_wone] = WEAKREFERENCE (n_one)',
            '$lookup(S.ENV, $ptascii("wtwo")) = (n_wtwo_cell)',
            'S.STORE[n_wtwo_cell] = DEFINED (POBJECT n_wtwo)',
            'S.OBJECTS[n_wtwo] = WEAKREFERENCE (n_two)',
            '$lookup(S.ENV, $ptascii("mapA")) = (n_mapa_cell)',
            'S.STORE[n_mapa_cell] = DEFINED (POBJECT n_mapa)',
            '$lookup(S.ENV, $ptascii("mapB")) = (n_mapb_cell)',
            'S.STORE[n_mapb_cell] = DEFINED (POBJECT n_mapb)',
            '$lookup(S.ENV, $ptascii("mapC")) = (n_mapc_cell)',
            'S.STORE[n_mapc_cell] = DEFINED (POBJECT n_mapc)',
            '$weakmap_entries_contents(S, n_mapa) = [pweakmapentry_aone, pweakmapentry_atwo]',
            '$weakmap_entries_contents(S, n_mapb) = [pweakmapentry_btwo, pweakmapentry_bone]',
            '$weakmap_entries_contents(S, n_mapc) = [pweakmapentry_cone, pweakmapentry_ctwo]',
            'pweakmapentry_cone.KEY = n_one', 'pweakmapentry_cone.ORDER = 1',
            'pweakmapentry_aone.KEY = n_one', 'pweakmapentry_aone.ORDER = 2',
            'pweakmapentry_bone.KEY = n_one', 'pweakmapentry_bone.ORDER = 3',
            'pweakmapentry_btwo.KEY = n_two', 'pweakmapentry_btwo.ORDER = 1',
            'pweakmapentry_ctwo.KEY = n_two', 'pweakmapentry_ctwo.ORDER = 2',
            'pweakmapentry_atwo.KEY = n_two', 'pweakmapentry_atwo.ORDER = 3',
            '$gc_ephemeron_key_records(S, n_one, S.ALLOCATIONS) = [pweakmapentry_cone, pweakmapentry_aone, pweakmapentry_bone]',
            '$gc_ephemeron_key_records(S, n_two, S.ALLOCATIONS) = [pweakmapentry_btwo, pweakmapentry_ctwo, pweakmapentry_atwo]',
            '$gc_ephemeron_key_order_safe(S, n_one)',
            '$gc_ephemeron_key_order_safe(S, n_two)',
        ], 'timeout': 180,
    },
    'peer-reinsert-a-count-five': peer_case(PEER_CBA, (4, 3, 1), 'cba', 'a', 5, True),
    'peer-reinsert-c-count-four': peer_case(PEER_ABC, (2, 3, 4), 'abc', 'c', 4, False),
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
