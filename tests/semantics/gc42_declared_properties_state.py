#!/usr/bin/env python3
"""Reached declared-slot cleanup retains later Children and consumes one shared edge."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc42_peer_declared_shared_throw.php').read_text()
STAGE = (
    'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (INSTANCE_STORAGE_STEP pinstancestorage_value) :: ptask_tail* '
    '-- if pinstancestorage_value.NEXT = 1 '
    '-- if n_value = pinstancestorage_value.OBJECT '
    '-- if $object_name(S, n_value) = $ptascii("GC42PeerValue") '
    '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_x)] '
    '-- if $object_name(S, n_x) = $ptascii("GC42PeerX")')
CHECKS = [
    '$destructor_release_valid(S, pdestructionrelease)',
    '$instance_storage_basic(S, pinstancestorage_value)',
    'pinstancestorage_value.SLOTS = [ppropertyslot_a, ppropertyslot_b, ppropertyslot_c, ppropertyslot_d]',
    'ppropertyslot_a.NAME = $ptascii("a")',
    'ppropertyslot_b.NAME = $ptascii("b")',
    'ppropertyslot_c.NAME = $ptascii("c")',
    'ppropertyslot_d.NAME = $ptascii("d")',
    'ppropertyslot_a.STATE = PROP_VALUE (DIRECT (POBJECT n_x))',
    'ppropertyslot_b.STATE = PROP_VALUE (DIRECT (POBJECT n_y))',
    'ppropertyslot_c.STATE = ppropertyslot_a.STATE',
    'ppropertyslot_d.STATE = PROP_VALUE (DIRECT (POBJECT n_z))',
    '$object_name(S, n_y) = $ptascii("GC42PeerY")',
    '$object_name(S, n_z) = $ptascii("GC42PeerZ")',
    '$objectprops_at(S.OBJECTPROPS, n_value) = (ppropertyslot_live*)',
    'ppropertyslot_live* = [ppropertyslot_a[.STATE = PROP_UNSET], ppropertyslot_b, ppropertyslot_c, ppropertyslot_d]',
    '$property_slot_nodes(pinstancestorage_value.SLOTS) = [HOBJECT n_x, HOBJECT n_y, HOBJECT n_x, HOBJECT n_z]',
    '$node_children(S, HOBJECT n_value) = [HOBJECT n_y, HOBJECT n_x, HOBJECT n_z]',
    '$task_nodes(INSTANCE_STORAGE_STEP pinstancestorage_value) = [HOBJECT n_value]',
    'S.OBJECTS[n_value] = INSTANCE porigin_value',
    '$class_at(S.CLASSES, porigin_value) = (pclassdesc)',
    'pclassdesc.PROPERTIES = [ppropertydesc_a, ppropertydesc_b, ppropertydesc_c, ppropertydesc_d]',
    '$weakmap_entries_declared_properties_free(S, n_value, pclassdesc.PROPERTIES, pinstancestorage_value.SLOTS)',
    '$weakmap_entries_declared_properties_free(S, n_value, pclassdesc.PROPERTIES, ppropertyslot_live*)',
    '~$weakmap_entries_declared_properties_free(S, n_value, [ppropertydesc_a[.ORIGIN = ppropertydesc_b.ORIGIN], ppropertydesc_b, ppropertydesc_c, ppropertydesc_d], ppropertyslot_live*)',
    '~$weakmap_entries_property_state_free(S, PROP_VALUE (ALIAS 0))',
    '~$weakmap_entries_property_value_free(S, PUNDEFINED)',
    '~$weakmap_entries_property_value_free(S, PFLOAT 18446744073709551616)',
    '~$weakmap_entries_child_value_free(S, POBJECT n_value)',
    'S_global = $global_table_view(S)',
    '$lookup(S_global.ENV, $ptascii("mapWatch")) = (n_map_watch_cell)',
    'S.STORE[n_map_watch_cell] = DEFINED (POBJECT n_map_watch)',
    'S.OBJECTS[n_map_watch] = WEAKREFERENCE (n_map)',
    '$lookup(S_global.ENV, $ptascii("valueWatch")) = (n_value_watch_cell)',
    'S.STORE[n_value_watch_cell] = DEFINED (POBJECT n_value_watch)',
    '$lookup(S_global.ENV, $ptascii("leafWatch")) = (n_leaf_watch_cell)',
    'S.STORE[n_leaf_watch_cell] = DEFINED (POBJECT n_leaf_watch)',
    'S.OBJECTS[n_leaf_watch] = WEAKREFERENCE (n_leaf)',
    '$lookup(S_global.ENV, $ptascii("xWatch")) = (n_x_watch_cell)',
    'S.STORE[n_x_watch_cell] = DEFINED (POBJECT n_x_watch)',
    '$lookup(S_global.ENV, $ptascii("yWatch")) = (n_y_watch_cell)',
    'S.STORE[n_y_watch_cell] = DEFINED (POBJECT n_y_watch)',
    '$lookup(S_global.ENV, $ptascii("zWatch")) = (n_z_watch_cell)',
    'S.STORE[n_z_watch_cell] = DEFINED (POBJECT n_z_watch)',
    '$instance_storage_for(S, n_map) = (pinstancestorage_map)',
    '$instance_storage_basic(S, pinstancestorage_map)',
    'pinstancestorage_map.NOTIFY = (n_map_watch)',
    'pinstancestorage_value.NOTIFY = eps',
    '$weakref_get(S, n_map_watch) = POBJECT n_map',
    '$weakref_get(S, n_value_watch) = PNULL',
    '$weakref_get(S, n_leaf_watch) = POBJECT n_leaf',
    'H = $heap_graph(S)',
    '$heap_valid(H) /\\ $destruction_state_valid(S) /\\ $call_descriptors_valid(S)',
    '$heap_owners(H, HOBJECT n_map) = 1',
    '$heap_owners(H, HOBJECT n_value) = 1',
    '$heap_owners(H, HOBJECT n_leaf) = 1',
    '$heap_owners(H, HOBJECT n_x) = 2',
    '$heap_owners(H, HOBJECT n_y) = 1',
    '$heap_owners(H, HOBJECT n_z) = 1',
    'PhpStep: S ~> S_shared',
    'S_shared.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_empty) :: (INSTANCE_STORAGE_STEP pinstancestorage_value) :: ptask_tail*',
    'pdestructionrelease_empty.JOBS = eps',
    '$heap_owners($heap_graph(S_shared), HOBJECT n_x) = 1',
    '$heap_owners($heap_graph(S_shared), HOBJECT n_y) = 1',
    '$heap_owners($heap_graph(S_shared), HOBJECT n_z) = 1',
    'S_shared.EVENTS = S.EVENTS /\\ S_shared.CURRENT = S.CURRENT',
    '~(n_x <- S_shared.DESTRUCTION.CALLED)',
    '$weakref_get(S_shared, n_x_watch) = POBJECT n_x',
    '$heap_valid($heap_graph(S_shared)) /\\ $destruction_state_valid(S_shared)',
    'S_zero = $drive_steps(S, 0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_paused = $drive_steps(S, 1)',
    'S_paused.COMPLETION = BUDGET /\\ S_paused.TODO = S_shared.TODO',
    'S_paused.ALLOCATIONS = S_shared.ALLOCATIONS',
    '$heap_owners($heap_graph(S_paused), HOBJECT n_x) = 1',
    '$heap_owners($heap_graph(S_paused), HOBJECT n_y) = 1',
    '$heap_owners($heap_graph(S_paused), HOBJECT n_z) = 1',
    '$heap_valid($heap_graph(S_paused)) /\\ $destruction_state_valid(S_paused)',
    'S_done = $drive_steps(S, 4000)',
    '$drive_steps(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    '$weakref_get(S_done, n_map_watch) = PNULL',
    '$weakref_get(S_done, n_value_watch) = PNULL',
    '$weakref_get(S_done, n_leaf_watch) = PNULL',
    '$weakref_get(S_done, n_x_watch) = PNULL',
    '$weakref_get(S_done, n_y_watch) = PNULL',
    '$weakref_get(S_done, n_z_watch) = PNULL',
    '~((HOBJECT n_value) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_x) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_y) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_z) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {'declared-first-shared-child': {'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=300) else 1)
