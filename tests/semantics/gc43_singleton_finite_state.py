#!/usr/bin/env python3
"""Reached singleton free transfers one Value owner and preserves its outside CV."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc43_peer_retained_fields.php').read_text()
STAGE = (
    'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail* '
    '-- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_map)) :: pdestructionjob_tail* '
    '-- if S.OBJECTS[n_map] = WEAKMAP (pweakmapentry) '
    '-- if pweakmapentry.VALUE = POBJECT n_value '
    '-- if $object_name(S, n_value) = $ptascii("GC43PeerRetainedValue") '
    '-- if $heap_owners($heap_graph(S), HOBJECT n_map) = 1')
CHECKS = [
    '$destructor_release_valid(S, pdestructionrelease)',
    'n_key = pweakmapentry.KEY',
    '$weakmap_key_maps(S, S.ALLOCATIONS, n_key) = [n_map]',
    '$weakmap_key_maps(S, S.ALLOCATIONS, n_map) = eps',
    '$node_children(S, HOBJECT n_map) = [HOBJECT n_value]',
    '$objectprops_at(S.OBJECTPROPS, n_value) = ([ppropertyslot_a, ppropertyslot_b, ppropertyslot_c])',
    'ppropertyslot_a.STATE = PROP_VALUE (DIRECT (POBJECT n_x))',
    'ppropertyslot_b.STATE = ppropertyslot_a.STATE',
    'ppropertyslot_c.STATE = PROP_VALUE (DIRECT (POBJECT n_y))',
    '$node_children(S, HOBJECT n_value) = [HOBJECT n_x, HOBJECT n_x, HOBJECT n_y]',
    'H = $heap_graph(S)',
    '$heap_valid(H) /\\ $destruction_state_valid(S)',
    '$heap_owners(H, HOBJECT n_value) = 2',
    '$heap_owners(H, HOBJECT n_x) = 2',
    '$heap_owners(H, HOBJECT n_y) = 1',
    '~$weakmap_declared_value_child(S, n_value)',
    '~$weakmap_declared_value_child_owners(S, n_value, 2)',
    '~$weakmap_free_slot_allowed(S, POBJECT n_value)',
    '$weakmap_entries_child_value_free(S, POBJECT n_value)',
    '$weakmap_map_free_slot_allowed(S, n_map, POBJECT n_value)',
    '$weakmap_free_slot_allowed(S, POBJECT n_x)',
    '~$weakmap_entries_child_value_free(S, POBJECT n_x)',
    '$weakmap_map_free_slot_allowed(S, n_map, POBJECT n_x)',
    'S_unheld = $destructor_release_replace(S, pdestructionrelease[.JOBS = pdestructionjob_tail*])',
    '$heap_owners($heap_graph(S_unheld), HOBJECT n_map) = 0',
    '$weakmap_free_allowed(S_unheld, n_map, pdestructionrelease[.JOBS = pdestructionjob_tail*])',
    '~$weakmap_free_allowed(S, n_map, pdestructionrelease)',
    'S_missing = S_unheld[.ALLOCATIONS = $destruction_node_delete(S_unheld.ALLOCATIONS, HOBJECT n_y)]',
    '~$weakmap_map_free_slot_allowed(S_missing, n_map, POBJECT n_value)',
    '~$weakmap_free_allowed(S_missing, n_map, pdestructionrelease[.JOBS = pdestructionjob_tail*])',
    'S_global = $global_table_view(S)',
    '$lookup(S_global.ENV, $ptascii("value")) = (n_value_cell)',
    'S.STORE[n_value_cell] = DEFINED (POBJECT n_value)',
    '$lookup(S_global.ENV, $ptascii("mapWatch")) = (n_map_watch_cell)',
    'S.STORE[n_map_watch_cell] = DEFINED (POBJECT n_map_watch)',
    '$lookup(S_global.ENV, $ptascii("valueWatch")) = (n_value_watch_cell)',
    'S.STORE[n_value_watch_cell] = DEFINED (POBJECT n_value_watch)',
    '$lookup(S_global.ENV, $ptascii("keyWatch")) = (n_key_watch_cell)',
    'S.STORE[n_key_watch_cell] = DEFINED (POBJECT n_key_watch)',
    '$lookup(S_global.ENV, $ptascii("xWatch")) = (n_x_watch_cell)',
    'S.STORE[n_x_watch_cell] = DEFINED (POBJECT n_x_watch)',
    '$lookup(S_global.ENV, $ptascii("yWatch")) = (n_y_watch_cell)',
    'S.STORE[n_y_watch_cell] = DEFINED (POBJECT n_y_watch)',
    'PhpStep: S ~> S_started',
    'S_started.OBJECTS[n_map] = WEAKMAP eps',
    '$weakmap_key_maps(S_started, S_started.ALLOCATIONS, n_key) = eps',
    '$node_children(S_started, HOBJECT n_map) = eps',
    'S_started.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_value) :: ptask_map*',
    'pdestructionrelease_value.JOBS = [DESTRUCTION_VALUE (HOBJECT n_value)]',
    '$destructor_release_valid(S_started, pdestructionrelease_value)',
    '$heap_owners($heap_graph(S_started), HOBJECT n_value) = 2',
    '$heap_owners($heap_graph(S_started), HOBJECT n_x) = 2',
    '$heap_owners($heap_graph(S_started), HOBJECT n_y) = 1',
    '$weakref_get(S_started, n_map_watch) = POBJECT n_map',
    '$weakref_get(S_started, n_value_watch) = POBJECT n_value',
    'PhpStep: S_started ~> S_shared',
    'S_shared.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_empty) :: ptask_map*',
    'pdestructionrelease_empty.JOBS = eps',
    '$heap_owners($heap_graph(S_shared), HOBJECT n_value) = 1',
    '$heap_owners($heap_graph(S_shared), HOBJECT n_x) = 2',
    '$heap_owners($heap_graph(S_shared), HOBJECT n_y) = 1',
    'S_shared.STORE[n_value_cell] = DEFINED (POBJECT n_value)',
    '$instance_storage_for(S_shared, n_value) = eps',
    '~(n_value <- S_shared.DESTRUCTION.CALLED)',
    'S_shared.EVENTS = S.EVENTS',
    '$weakref_get(S_shared, n_value_watch) = POBJECT n_value',
    '$weakref_get(S_shared, n_x_watch) = POBJECT n_x',
    '$heap_valid($heap_graph(S_shared)) /\\ $destruction_state_valid(S_shared)',
    'S_zero = $drive_steps(S, 0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_paused = $drive_steps(S, 2)',
    'S_paused.COMPLETION = BUDGET /\\ S_paused.TODO = S_shared.TODO',
    'S_paused.ALLOCATIONS = S_shared.ALLOCATIONS',
    '$heap_owners($heap_graph(S_paused), HOBJECT n_value) = 1',
    '$heap_owners($heap_graph(S_paused), HOBJECT n_x) = 2',
    '$heap_owners($heap_graph(S_paused), HOBJECT n_y) = 1',
    '$heap_valid($heap_graph(S_paused)) /\\ $destruction_state_valid(S_paused)',
    'S_done = $drive_steps(S, 4000)',
    '$drive_steps(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    '$weakref_get(S_done, n_map_watch) = PNULL',
    '$weakref_get(S_done, n_value_watch) = PNULL',
    '$weakref_get(S_done, n_key_watch) = PNULL',
    '$weakref_get(S_done, n_x_watch) = PNULL',
    '$weakref_get(S_done, n_y_watch) = PNULL',
    '~((HOBJECT n_map) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_value) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_x) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_y) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {'singleton-retained-finite-value': {'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=300) else 1)
