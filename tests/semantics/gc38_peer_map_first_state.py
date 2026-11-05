#!/usr/bin/env python3
"""Reached Child callback under nested Map and Value storage pins."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc38_peer_map_first_observers.php').read_text()
STAGE = ('S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail* '
         '-- if $object_name(S, pdestructorcall.OBJECT) = $ptascii("GC38PeerChild") '
         '-- if S_global = $global_table_view(S) '
         '-- if $lookup(S_global.ENV, $ptascii("mapWatch")) = (n_map_watch_cell) '
         '-- if S.STORE[n_map_watch_cell] = DEFINED (POBJECT n_map_watch) '
         '-- if S.OBJECTS[n_map_watch] = WEAKREFERENCE (n_map) '
         '-- if $lookup(S_global.ENV, $ptascii("valueWatch")) = (n_value_watch_cell) '
         '-- if S.STORE[n_value_watch_cell] = DEFINED (POBJECT n_value_watch) '
         '-- if S.OBJECTS[n_value_watch] = WEAKREFERENCE (n_value) '
         '-- if $lookup(S_global.ENV, $ptascii("keyWatch")) = (n_key_watch_cell) '
         '-- if S.STORE[n_key_watch_cell] = DEFINED (POBJECT n_key_watch) '
         '-- if S.OBJECTS[n_key_watch] = WEAKREFERENCE (n_key) '
         '-- if $instance_storage_for(S, n_map) = (pinstancestorage_map) '
         '-- if $instance_storage_for(S, n_value) = (pinstancestorage_value)')
CHECKS = [
    'n_child = pdestructorcall.OBJECT',
    'pinstancestorage_map.NOTIFY = (n_map_watch) /\\ pinstancestorage_map.SLOTS = eps',
    'pinstancestorage_value.NOTIFY = eps /\\ pinstancestorage_value.NEXT = 1',
    '$instance_storage_basic(S, pinstancestorage_map)',
    '$instance_storage_basic(S, pinstancestorage_value)',
    'S.OBJECTS[n_map] = WEAKMAP eps',
    '$weakmap_key_maps(S, S.ALLOCATIONS, n_key) = eps',
    'S.OBJECTS[n_key] = STDINSTANCE',
    '$object_name(S, n_value) = $ptascii("GC38PeerValue")',
    '$node_children(S, HOBJECT n_value) = eps',
    '$objectprops_at(S.OBJECTPROPS, n_value) = ([ppropertyslot_cleared])',
    'ppropertyslot_cleared.STATE = PROP_UNSET',
    '$weakmap_storage_read(S, n_map_watch, n_map)',
    '$weakref_get(S, n_map_watch) = POBJECT n_map',
    '$weakref_get(S, n_value_watch) = PNULL',
    '$weakref_get(S, n_key_watch) = POBJECT n_key',
    'H = $heap_graph(S)',
    '$heap_valid(H) /\\ $destruction_state_valid(S) /\\ $call_descriptors_valid(S)',
    '$heap_owners(H, HOBJECT n_map) = 1',
    '$heap_owners(H, HOBJECT n_value) = 1',
    '$heap_owners(H, HOBJECT n_key) = 1',
    '$heap_owners(H, HOBJECT n_child) = 2',
    'S_zero = $drive_steps(S, 0)',
    'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
    'S_done = $drive_steps(S, 4000)',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    '~((HOBJECT n_map) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_value) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_key) <- S_done.ALLOCATIONS)',
    '$weakref_get(S_done, n_map_watch) = PNULL',
    '$weakref_get(S_done, n_value_watch) = PNULL',
    '$weakref_get(S_done, n_key_watch) = PNULL',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {
    'map-first-child-callback-observers': {
        'source': SOURCE,
        'stage': STAGE,
        'checks': CHECKS,
    },
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', default=[])
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=240) else 1)
