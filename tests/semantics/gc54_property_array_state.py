#!/usr/bin/env python3
"""An actual declared slot transfers one shared HARRAY owner without Child copies."""
import argparse
import json
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc54_peer_shared_array_property_order.php').read_text()
STAGE = (
    'S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_tail* '
    '-- if pinstancestorage.NEXT = 0 '
    '-- if n_value = pinstancestorage.OBJECT '
    '-- if $object_name(S, n_value) = $ptascii("ArrayPropertyValue54") '
    '-- if pinstancestorage.SLOTS = [ppropertyslot_first, ppropertyslot_middle, ppropertyslot_last] '
    '-- if ppropertyslot_first.STATE = PROP_VALUE (DIRECT (PARRAY n_array))')
CHUNKS = (['B|', 'S|', 'Y|'] + ['1', '|'] * 5 + ['Z|'] + ['1', '|'] * 5
          + ['X|'] + ['1', '|'] * 5
          + ['T|', '1', '|', 'makeArrayPropertyFailure54', '|', '0', '|']
          + ['1', '|'] * 6 + ['A|', '1', '|'])
ENDING = 'S_done.EVENTS = [' + ', '.join(
    'OUTPUT $ptascii(' + json.dumps(chunk) + ')' for chunk in CHUNKS) + ']'
CHECKS = [
    'S.CURRENT = eps /\\ S.FRAMES = eps',
    '$instance_storage_valid(S, pinstancestorage)',
    '$objectprops_at(S.OBJECTPROPS, n_value) = (pinstancestorage.SLOTS)',
    'ppropertyslot_first.NAME = $ptascii("first")',
    'ppropertyslot_middle.NAME = $ptascii("middle")',
    'ppropertyslot_last.NAME = $ptascii("last")',
    'ppropertyslot_last.STATE = ppropertyslot_first.STATE',
    'ppropertyslot_middle.STATE = PROP_VALUE (DIRECT (POBJECT n_y))',
    'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_x)), ENTRY (KINT 1) (DIRECT (PINT 0)), ENTRY (KINT 2) (DIRECT (POBJECT n_z)), ENTRY (KINT 3) (DIRECT (POBJECT n_x))]',
    '$node_children(S, HOBJECT n_value) = [HARRAY n_array, HOBJECT n_y, HARRAY n_array]',
    '$node_children(S, HARRAY n_array) = [HOBJECT n_x, HOBJECT n_z, HOBJECT n_x]',
    '$task_nodes(INSTANCE_STORAGE_STEP pinstancestorage) = [HOBJECT n_value]',
    '$heap_owners($heap_graph(S), HOBJECT n_value) = 1',
    '$heap_owners($heap_graph(S), HARRAY n_array) = 2',
    '$heap_owners($heap_graph(S), HOBJECT n_x) = 2',
    '$heap_owners($heap_graph(S), HOBJECT n_y) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_z) = 1',
    '$lookup(S.ENV, $ptascii("mapWatch54")) = (n_map_watch_cell)',
    'S.STORE[n_map_watch_cell] = DEFINED (POBJECT n_map_watch)',
    '$weakref_get(S, n_map_watch) = POBJECT n_map',
    '$instance_storage_freeing(S, n_map)',
    '$heap_owners($heap_graph(S), HOBJECT n_map) = 1',
    '$lookup(S.ENV, $ptascii("key")) = (n_key_cell)',
    'S.STORE[n_key_cell] = DEFINED (POBJECT n_key)',
    '$weakmap_key_maps(S, S.ALLOCATIONS, n_key) = eps',
    '$heap_owners($heap_graph(S), HOBJECT n_key) = 1',
    '$heap_valid($heap_graph(S)) /\\ $destruction_state_valid(S)',
    '$weakmap_entries_property_value_free(S, PARRAY n_array)',
    '~$weakmap_entries_property_leaf_free(S, PARRAY n_array)',
    '$weakmap_entries_property_leaf_free(S, POBJECT n_x)',
    '~$weakmap_entries_child_value_free(S, PARRAY n_array)',
    '~$weakmap_entries_child_value_free(S, POBJECT n_x)',
    # Bounded property-array controls use constructed helper inputs only.
    '$weakmap_entries_property_array_entries_free(S, eps)',
    '$weakmap_entries_property_array_entries_free(S, [ENTRY (KINT 4) (DIRECT (PINT 0))])',
    '~$weakmap_entries_property_array_entries_free(S, [ENTRY (KINT 0) (DIRECT (PARRAY n_array))])',
    '~$weakmap_entries_property_array_entries_free(S, [ENTRY (KINT 0) (ALIAS n_key_cell)])',
    '~$weakmap_entries_callback_class(S, n_value)',
    '~$weakmap_entries_property_array_entries_free(S, [ENTRY (KINT 0) (DIRECT (POBJECT n_value))])',
    '~$weakmap_entries_property_array_entries_free(S, [ENTRY (KINT 0) (DIRECT (PINT 0)), ENTRY (KINT 0) (DIRECT (POBJECT n_x))])',
    '~$weakmap_entries_property_value_free(S, PARRAY (|S.ARRAYS|))',
    'S_unallocated = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HARRAY n_array)]',
    '~$weakmap_entries_property_value_free(S_unallocated, PARRAY n_array)',
    'S_zero = $drive_steps(S, 0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_transferred = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
    'S_transferred.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (INSTANCE_STORAGE_STEP pinstancestorage_next) :: ptask_tail*',
    'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_array)]',
    'pinstancestorage_next = pinstancestorage[.NEXT = 1]',
    '$objectprops_at(S_transferred.OBJECTPROPS, n_value) = ([ppropertyslot_first[.STATE = PROP_UNSET], ppropertyslot_middle, ppropertyslot_last])',
    '$task_nodes(DESTRUCTOR_RELEASE pdestructionrelease) = [HARRAY n_array]',
    '$task_nodes(INSTANCE_STORAGE_STEP pinstancestorage_next) = [HOBJECT n_value]',
    '$instance_storage_valid(S_transferred, pinstancestorage_next)',
    '$destructor_release_valid(S_transferred, pdestructionrelease)',
    '$heap_owners($heap_graph(S_transferred), HOBJECT n_value) = 1',
    '$heap_owners($heap_graph(S_transferred), HARRAY n_array) = 2',
    '$heap_owners($heap_graph(S_transferred), HOBJECT n_x) = 2',
    '$heap_owners($heap_graph(S_transferred), HOBJECT n_y) = 1',
    '$heap_owners($heap_graph(S_transferred), HOBJECT n_z) = 1',
    'S_transferred.ARRAYS[n_array] = S.ARRAYS[n_array]',
    'S_transferred.EVENTS = S.EVENTS',
    '$heap_valid($heap_graph(S_transferred)) /\\ $destruction_state_valid(S_transferred)',
    'S_shared = $drive_steps(S_transferred, 1)[.COMPLETION = NORMAL]',
    '$heap_owners($heap_graph(S_shared), HARRAY n_array) = 1',
    '$heap_owners($heap_graph(S_shared), HOBJECT n_x) = 2',
    '$heap_owners($heap_graph(S_shared), HOBJECT n_y) = 1',
    '$heap_owners($heap_graph(S_shared), HOBJECT n_z) = 1',
    '(HARRAY n_array) <- S_shared.ALLOCATIONS',
    'S_shared.ARRAYS[n_array] = S.ARRAYS[n_array]',
    'S_shared.EVENTS = S.EVENTS',
    '$heap_valid($heap_graph(S_shared))',
    'S_paused = $drive_steps(S, 2)',
    'S_paused.COMPLETION = BUDGET /\\ S_paused.TODO = S_shared.TODO',
    '$heap_owners($heap_graph(S_paused), HARRAY n_array) = 1',
    '$heap_owners($heap_graph(S_paused), HOBJECT n_x) = 2',
    'S_done = $drive_steps(S, 4000)',
    '$drive_steps(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    ENDING,
    '~((HARRAY n_array) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_value) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_x) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_y) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_z) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_key) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_map) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {'property-array-owner-transfer': {'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=360) else 1)
