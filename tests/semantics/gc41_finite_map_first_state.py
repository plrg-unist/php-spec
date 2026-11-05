#!/usr/bin/env python3
"""Reached finite Map retirement preserves repeated Value and shared Child owners."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc41_peer_shared_retained_value.php').read_text()
STAGE = (
    'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail* '
    '-- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_map)) :: pdestructionjob_tail* '
    '-- if S.OBJECTS[n_map] = WEAKMAPENTRIES ([pweakmapentry_first, pweakmapentry_leaf, pweakmapentry_other, pweakmapentry_last]) '
    '-- if pweakmapentry_first.VALUE = POBJECT n_a '
    '-- if $object_name(S, n_a) = $ptascii("GC41PeerSharedValue") '
    '-- if $heap_owners($heap_graph(S), HOBJECT n_map) = 1')
CHECKS = [
    '$destructor_release_valid(S, pdestructionrelease)',
    'pweakmapentry_leaf.VALUE = POBJECT n_leaf',
    'pweakmapentry_other.VALUE = POBJECT n_b',
    'pweakmapentry_last.VALUE = POBJECT n_a',
    'n_a =/= n_b',
    '$object_name(S, n_leaf) = $ptascii("GC41PeerSharedLeaf")',
    '$objectprops_at(S.OBJECTPROPS, n_a) = ([ppropertyslot_a])',
    '$objectprops_at(S.OBJECTPROPS, n_b) = ([ppropertyslot_b])',
    'ppropertyslot_a.STATE = PROP_VALUE (DIRECT (POBJECT n_child))',
    'ppropertyslot_b.STATE = ppropertyslot_a.STATE',
    '$object_name(S, n_child) = $ptascii("GC41PeerSharedChild")',
    'H = $heap_graph(S)',
    '$heap_valid(H) /\\ $destruction_state_valid(S)',
    '$heap_owners(H, HOBJECT n_a) = 3',
    '$heap_owners(H, HOBJECT n_b) = 1',
    '$heap_owners(H, HOBJECT n_leaf) = 1',
    '$heap_owners(H, HOBJECT n_child) = 2',
    '$node_children(S, HOBJECT n_map) = [HOBJECT n_a, HOBJECT n_leaf, HOBJECT n_b, HOBJECT n_a]',
    '$weakmap_declared_value_child_owners(S, n_a, 2)',
    '$weakmap_declared_value_child_owners(S, n_b, 2)',
    '~$weakmap_entries_teardown_table(S, n_map)',
    '$weakmap_entries_child_value_free(S, POBJECT n_a)',
    '$weakmap_entries_child_value_free(S, POBJECT n_b)',
    '$weakmap_entries_child_value_free(S, POBJECT n_leaf)',
    '~$weakmap_entries_child_value_free(S, ALIAS 0)',
    '$weakmap_entries_child_entries_free(S, n_map, [pweakmapentry_first, pweakmapentry_leaf, pweakmapentry_other, pweakmapentry_last])',
    '~$weakmap_entries_child_entries_free(S, n_map, [pweakmapentry_first[.KEY = pweakmapentry_leaf.KEY], pweakmapentry_leaf, pweakmapentry_other, pweakmapentry_last])',
    '$weakmap_entries_child_table_free(S, n_map)',
    'S_unheld = $destructor_release_replace(S, pdestructionrelease[.JOBS = pdestructionjob_tail*])',
    '$weakmap_entries_free_allowed(S_unheld, n_map, pdestructionrelease[.JOBS = pdestructionjob_tail*])',
    '~$weakmap_entries_free_allowed(S, n_map, pdestructionrelease)',
    'S_missing = S_unheld[.ALLOCATIONS = $destruction_node_delete(S_unheld.ALLOCATIONS, HOBJECT n_child)]',
    '~$weakmap_entries_child_value_free(S_missing, POBJECT n_a)',
    '~$weakmap_entries_child_table_free(S_missing, n_map)',
    'S_global = $global_table_view(S)',
    '$lookup(S_global.ENV, $ptascii("mapWatch")) = (n_map_watch_cell)',
    'S.STORE[n_map_watch_cell] = DEFINED (POBJECT n_map_watch)',
    '$lookup(S_global.ENV, $ptascii("aWatch")) = (n_a_watch_cell)',
    'S.STORE[n_a_watch_cell] = DEFINED (POBJECT n_a_watch)',
    '$lookup(S_global.ENV, $ptascii("childWatch")) = (n_child_watch_cell)',
    'S.STORE[n_child_watch_cell] = DEFINED (POBJECT n_child_watch)',
    'PhpStep: S ~> S_started',
    'S_started.OBJECTS[n_map] = WEAKMAP eps',
    '$weakmap_key_maps(S_started, S_started.ALLOCATIONS, pweakmapentry_first.KEY) = eps',
    '$weakmap_key_maps(S_started, S_started.ALLOCATIONS, pweakmapentry_leaf.KEY) = eps',
    '$weakmap_key_maps(S_started, S_started.ALLOCATIONS, pweakmapentry_other.KEY) = eps',
    '$weakmap_key_maps(S_started, S_started.ALLOCATIONS, pweakmapentry_last.KEY) = eps',
    'S_started.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_slots) :: ptask_slots*',
    'pdestructionrelease_slots.JOBS = [DESTRUCTION_VALUE (HOBJECT n_a), DESTRUCTION_VALUE (HOBJECT n_leaf), DESTRUCTION_VALUE (HOBJECT n_b), DESTRUCTION_VALUE (HOBJECT n_a)]',
    '$destructor_release_valid(S_started, pdestructionrelease_slots)',
    '$heap_owners($heap_graph(S_started), HOBJECT n_a) = 3',
    '$heap_owners($heap_graph(S_started), HOBJECT n_child) = 2',
    '$weakref_get(S_started, n_map_watch) = POBJECT n_map',
    'PhpStep: S_started ~> S_first',
    'S_first.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_after_first) :: ptask_slots*',
    'pdestructionrelease_after_first.JOBS = [DESTRUCTION_VALUE (HOBJECT n_leaf), DESTRUCTION_VALUE (HOBJECT n_b), DESTRUCTION_VALUE (HOBJECT n_a)]',
    '$heap_owners($heap_graph(S_first), HOBJECT n_a) = 2',
    '$heap_owners($heap_graph(S_first), HOBJECT n_b) = 1',
    '$heap_owners($heap_graph(S_first), HOBJECT n_child) = 2',
    '$weakref_get(S_first, n_a_watch) = POBJECT n_a',
    '$heap_valid($heap_graph(S_first)) /\\ $destruction_state_valid(S_first)',
    'S_zero = $drive_steps(S, 0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_paused = $drive_steps(S, 2)',
    'S_paused.COMPLETION = BUDGET /\\ S_paused.TODO = S_first.TODO',
    'S_paused.ALLOCATIONS = S_first.ALLOCATIONS',
    '$heap_owners($heap_graph(S_paused), HOBJECT n_a) = 2',
    '$heap_owners($heap_graph(S_paused), HOBJECT n_child) = 2',
    '$heap_valid($heap_graph(S_paused)) /\\ $destruction_state_valid(S_paused)',
    'S_done = $drive_steps(S, 4000)',
    '$drive_steps(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    '$weakref_get(S_done, n_map_watch) = PNULL',
    '$weakref_get(S_done, n_a_watch) = PNULL',
    '$weakref_get(S_done, n_child_watch) = PNULL',
    '~((HOBJECT n_map) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_a) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_b) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {'finite-map-repeated-value': {'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=240) else 1)
