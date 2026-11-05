#!/usr/bin/env python3
"""Reached Key notification conserves one transferred Value edge and its Children."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc45_repeated_value_key_death.php').read_text()
STAGE = (
    'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail* '
    '-- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_key)) :: pdestructionjob_tail* '
    '-- if $lookup(S.ENV, $ptascii("map")) = (n_map_cell) '
    '-- if S.STORE[n_map_cell] = DEFINED (POBJECT n_map) '
    '-- if S.OBJECTS[n_map] = WEAKMAPENTRIES ([pweakmapentry_first, pweakmapentry_second, pweakmapentry_tail]) '
    '-- if pweakmapentry_first.KEY = n_key '
    '-- if pweakmapentry_first.VALUE = POBJECT n_value '
    '-- if $object_name(S, n_value) = $ptascii("GC45Value") '
    '-- if $heap_owners($heap_graph(S), HOBJECT n_key) = 1')
CHECKS = [
    '$destructor_release_valid(S, pdestructionrelease)',
    'pweakmapentry_second.VALUE = POBJECT n_value',
    'pweakmapentry_tail.VALUE = POBJECT n_leaf',
    '$object_name(S, n_leaf) = $ptascii("GC45Leaf")',
    '$objectprops_at(S.OBJECTPROPS, n_value) = ([ppropertyslot_a, ppropertyslot_b, ppropertyslot_c])',
    'ppropertyslot_a.STATE = PROP_VALUE (DIRECT (POBJECT n_x))',
    'ppropertyslot_b.STATE = PROP_VALUE (DIRECT (POBJECT n_y))',
    'ppropertyslot_c.STATE = ppropertyslot_a.STATE',
    'pweakmapentry_first.BEFORE = (n_key_watch)',
    '$weakref_get(S, n_key_watch) = POBJECT n_key',
    'H = $heap_graph(S)',
    '$heap_valid(H) /\\ $destruction_state_valid(S)',
    '$heap_owners(H, HOBJECT n_value) = 2',
    '$heap_owners(H, HOBJECT n_x) = 2',
    '$heap_owners(H, HOBJECT n_y) = 1',
    '$heap_owners(H, HOBJECT n_leaf) = 1',
    '$weakmap_entries_child_storage(S, n_map)',
    '~$weakmap_entries_storage_valid(S, n_map, [n_key])',
    '~$weakmap_entries_notice_storage(S, n_map, [n_key], false)',
    'PhpStep: S ~> S_started',
    'S_started.OBJECTS[n_map] = WEAKMAPENTRIES ([pweakmapentry_second, pweakmapentry_tail])',
    '$weakmap_key_maps(S_started, S_started.ALLOCATIONS, n_key) = eps',
    '$weakmap_key_maps(S_started, S_started.ALLOCATIONS, pweakmapentry_second.KEY) = [n_map]',
    '$weakmap_key_maps(S_started, S_started.ALLOCATIONS, pweakmapentry_tail.KEY) = [n_map]',
    'S_started.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_value) :: (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_after_pin*',
    'S_started.DESTRUCTION.RELEASES = pdestructionrelease_value :: pdestructionrelease_outer*',
    'pdestructionrelease_value.JOBS = [DESTRUCTION_VALUE (HOBJECT n_value)]',
    'pinstancestorage.OBJECT = n_key /\\ pinstancestorage.NEXT = 0 /\\ pinstancestorage.SLOTS = eps /\\ pinstancestorage.NOTIFY = eps',
    '$instance_storage_valid(S_started, pinstancestorage)',
    '$destructor_release_valid(S_started, pdestructionrelease_value)',
    '$heap_owners($heap_graph(S_started), HOBJECT n_key) = 1',
    '$heap_owners($heap_graph(S_started), HOBJECT n_value) = 2',
    '$heap_owners($heap_graph(S_started), HOBJECT n_x) = 2',
    '$heap_owners($heap_graph(S_started), HOBJECT n_y) = 1',
    '$weakref_get(S_started, n_key_watch) = PNULL',
    '$heap_valid($heap_graph(S_started)) /\\ $destruction_state_valid(S_started)',
    # Invert only the observed entry-to-job transfer to expose its internal input.
    'S_notice = S_started[.OBJECTS[n_map] = S.OBJECTS[n_map]][.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_after_pin*][.DESTRUCTION.RELEASES = pdestructionrelease_outer*]',
    '$instance_storage_valid(S_notice, pinstancestorage)',
    '$heap_owners($heap_graph(S_notice), HOBJECT n_value) = 2',
    '~$weakmap_entries_child_storage(S_notice, n_map)',
    '$weakmap_entries_child_storage_policy(S_notice, n_map, (n_key))',
    '~$weakmap_entries_child_storage_policy(S_notice, n_map, (pweakmapentry_second.KEY))',
    '$weakmap_entries_notice_storage(S_notice, n_map, [n_key], false)',
    '$weakmap_key_notice(S_notice, n_key) = S_started',
    '~$weakmap_entries_notice_storage(S_notice, n_map, [pweakmapentry_second.KEY], false)',
    '~$weakmap_entries_notice_storage(S_notice, n_map, eps, false)',
    '~$weakmap_entries_notice_storage(S_notice, n_map, [n_key, pweakmapentry_second.KEY], false)',
    'S_missing_pin = S_notice[.TODO = ptask_after_pin*]',
    '~$weakmap_entries_notice_storage(S_missing_pin, n_map, [n_key], false)',
    'S_wrong_pin = S_notice[.TODO = (INSTANCE_STORAGE_STEP pinstancestorage[.OBJECT = pweakmapentry_second.KEY]) :: ptask_after_pin*]',
    '~$weakmap_entries_notice_storage(S_wrong_pin, n_map, [n_key], false)',
    'S_sibling = S_notice[.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: (INSTANCE_STORAGE_STEP pinstancestorage[.OBJECT = pweakmapentry_second.KEY]) :: ptask_after_pin*]',
    '$instance_storage_freeing(S_sibling, pweakmapentry_second.KEY)',
    '~$weakmap_entries_child_entries_policy(S_sibling, n_map, (n_key), [pweakmapentry_first, pweakmapentry_second, pweakmapentry_tail])',
    'S_cursor = S_notice[.ITERATORS = [OBJECTITER 0 n_map 0 false]]',
    '$weakmap_foreach_active(S_cursor.ITERATORS, n_map)',
    '~$weakmap_entries_child_storage_policy(S_cursor, n_map, (n_key))',
    '~$weakmap_entries_notice_storage(S_cursor, n_map, [n_key], false)',
    'S_leaf_cursor = S_cursor[.OBJECTS[n_map] = WEAKMAPENTRIES ([pweakmapentry_first[.VALUE = POBJECT n_leaf], pweakmapentry_second[.VALUE = POBJECT n_leaf], pweakmapentry_tail])]',
    '$weakmap_entries_storage_valid(S_leaf_cursor, n_map, [n_key])',
    '$weakmap_entries_notice_storage(S_leaf_cursor, n_map, [n_key], false)',
    'PhpStep: S_started ~> S_shared',
    '$heap_owners($heap_graph(S_shared), HOBJECT n_value) = 1',
    '$heap_owners($heap_graph(S_shared), HOBJECT n_x) = 2',
    '$heap_owners($heap_graph(S_shared), HOBJECT n_y) = 1',
    '~$instance_storage_freeing(S_shared, n_value)',
    'S_shared.EVENTS = S.EVENTS',
    '$heap_valid($heap_graph(S_shared)) /\\ $destruction_state_valid(S_shared)',
    'S_zero = $drive_steps(S, 0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_paused = $drive_steps(S, 2)',
    'S_paused.COMPLETION = BUDGET /\\ S_paused.TODO = S_shared.TODO',
    '$heap_owners($heap_graph(S_paused), HOBJECT n_value) = 1',
    '$heap_owners($heap_graph(S_paused), HOBJECT n_x) = 2',
    '$heap_owners($heap_graph(S_paused), HOBJECT n_y) = 1',
    '$heap_valid($heap_graph(S_paused))',
    'S_done = $drive_steps(S, 4000)',
    '$drive_steps(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    '~((HOBJECT n_key) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_value) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_x) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_y) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_leaf) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_map) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {'finite-value-key-detach': {'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=300) else 1)
