#!/usr/bin/env python3
"""Reached reverse entry cleanup with nested Child throw under Map and Value pins."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc40_peer_reverse_throw.php').read_text()
STAGE = (
    'S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail* '
    '-- if $object_name(S, pdestructorcall.OBJECT) = $ptascii("GC40PeerChild") '
    '-- if S_global = $global_table_view(S) '
    '-- if $lookup(S_global.ENV, $ptascii("mapWatch")) = (n_map_watch_cell) '
    '-- if S.STORE[n_map_watch_cell] = DEFINED (POBJECT n_map_watch) '
    '-- if S.OBJECTS[n_map_watch] = WEAKREFERENCE (n_map) '
    '-- if $lookup(S_global.ENV, $ptascii("leafWatch")) = (n_leaf_watch_cell) '
    '-- if S.STORE[n_leaf_watch_cell] = DEFINED (POBJECT n_leaf_watch) '
    '-- if $lookup(S_global.ENV, $ptascii("fieldWatch")) = (n_field_watch_cell) '
    '-- if S.STORE[n_field_watch_cell] = DEFINED (POBJECT n_field_watch) '
    '-- if S.OBJECTS[n_field_watch] = WEAKREFERENCE (n_field) '
    '-- if $lookup(S_global.ENV, $ptascii("firstKeyWatch")) = (n_first_watch_cell) '
    '-- if S.STORE[n_first_watch_cell] = DEFINED (POBJECT n_first_watch) '
    '-- if S.OBJECTS[n_first_watch] = WEAKREFERENCE (n_first_key) '
    '-- if $lookup(S_global.ENV, $ptascii("secondKeyWatch")) = (n_second_watch_cell) '
    '-- if S.STORE[n_second_watch_cell] = DEFINED (POBJECT n_second_watch) '
    '-- if S.OBJECTS[n_second_watch] = WEAKREFERENCE (n_second_key) '
    '-- if $instance_storage_for(S, n_map) = (pinstancestorage_map) '
    '-- if $instance_storage_for(S, n_field) = (pinstancestorage_field)')
CHECKS = [
    'n_child = pdestructorcall.OBJECT',
    '$instance_storage_basic(S, pinstancestorage_map)',
    '$instance_storage_basic(S, pinstancestorage_field)',
    'pinstancestorage_map.SLOTS = eps /\\ pinstancestorage_map.NOTIFY = (n_map_watch)',
    'pinstancestorage_field.NEXT = 1 /\\ pinstancestorage_field.NOTIFY = eps',
    'S.OBJECTS[n_map] = WEAKMAP eps',
    '$weakmap_key_maps(S, S.ALLOCATIONS, n_first_key) = eps',
    '$weakmap_key_maps(S, S.ALLOCATIONS, n_second_key) = eps',
    '$weakref_get(S, n_leaf_watch) = PNULL',
    '$weakref_get(S, n_field_watch) = PNULL',
    '$weakref_get(S, n_map_watch) = POBJECT n_map',
    '$weakref_get(S, n_first_watch) = POBJECT n_first_key',
    '$weakref_get(S, n_second_watch) = POBJECT n_second_key',
    '$objectprops_at(S.OBJECTPROPS, n_field) = ([ppropertyslot])',
    'ppropertyslot.STATE = PROP_UNSET',
    'H = $heap_graph(S)',
    '$heap_valid(H) /\\ $destruction_state_valid(S) /\\ $call_descriptors_valid(S)',
    '$heap_owners(H, HOBJECT n_map) = 1',
    '$heap_owners(H, HOBJECT n_field) = 1',
    '$heap_owners(H, HOBJECT n_child) = 2',
    '$heap_owners(H, HOBJECT n_first_key) = 1',
    '$heap_owners(H, HOBJECT n_second_key) = 1',
    'S_zero = $drive_steps(S, 0)',
    'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
    'S_done = $drive_steps(S, 4000)',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 4000) = S_done',
    'S_one = $drive_steps(S, 1)',
    'S_one.COMPLETION = BUDGET /\\ S_one.TODO =/= S.TODO',
    '$drive_steps(S_one[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    '$weakref_get(S_done, n_map_watch) = PNULL',
    '$weakref_get(S_done, n_field_watch) = PNULL',
    '$weakref_get(S_done, n_first_watch) = PNULL',
    '$weakref_get(S_done, n_second_watch) = PNULL',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {'reverse-two-entry-child-throw': {'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=240) else 1)
