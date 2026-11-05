#!/usr/bin/env python3
"""Peer reached check for retained Child's shared release under Map/Value pins."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc39_peer_retained_throw.php').read_text()
STAGE = (
    'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail* '
    '-- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_child)) :: pdestructionjob_tail* '
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
    '-- if $object_name(S, n_value) = $ptascii("GC39PeerValue") '
    '-- if $instance_storage_for(S, n_value) = (pinstancestorage_value) '
    '-- if $instance_storage_for(S, n_map) = (pinstancestorage_map)')
CHECKS = [
    '$destructor_release_valid(S, pdestructionrelease)',
    'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_child)]',
    'pinstancestorage_value.OBJECT = n_value /\\ pinstancestorage_map.OBJECT = n_map',
    '$instance_storage_valid(S, pinstancestorage_value)',
    '$instance_storage_valid(S, pinstancestorage_map)',
    'pinstancestorage_value.NEXT = 1 /\\ pinstancestorage_value.NOTIFY = eps',
    'pinstancestorage_map.SLOTS = eps /\\ pinstancestorage_map.NOTIFY = (n_map_watch)',
    'S.OBJECTS[n_map] = WEAKMAP eps',
    '$objectprops_at(S.OBJECTPROPS, n_value) = ([ppropertyslot])',
    'ppropertyslot.STATE = PROP_UNSET',
    '$object_name(S, n_child) = $ptascii("GC39PeerChild")',
    '(HOBJECT n_child) <- S.ALLOCATIONS',
    '~(n_child <- S.DESTRUCTION.CALLED)',
    '$weakref_get(S, n_map_watch) = POBJECT n_map',
    '$weakref_get(S, n_value_watch) = PNULL',
    '$weakref_get(S, n_key_watch) = POBJECT n_key',
    'H = $heap_graph(S)',
    '$heap_valid(H) /\\ $destruction_state_valid(S)',
    '$heap_owners(H, HOBJECT n_map) = 1',
    '$heap_owners(H, HOBJECT n_value) = 1',
    '$heap_owners(H, HOBJECT n_child) = 2',
    'PhpStep: S ~> S_shared',
    '$instance_storage_for(S_shared, n_value) = (pinstancestorage_value)',
    '$heap_owners($heap_graph(S_shared), HOBJECT n_child) = 1',
    '(HOBJECT n_child) <- S_shared.ALLOCATIONS',
    '~(n_child <- S_shared.DESTRUCTION.CALLED)',
    '$weakref_get(S_shared, n_map_watch) = POBJECT n_map',
    '$weakref_get(S_shared, n_value_watch) = PNULL',
    '$heap_valid($heap_graph(S_shared))',
]
review.CASES = {'retained-child-shared-release': {'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=240) else 1)
