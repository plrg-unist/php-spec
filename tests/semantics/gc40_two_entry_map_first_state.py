#!/usr/bin/env python3
"""Reached two-entry Map free transfers both Value owners in table order."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc40_first_field_second_leaf.php').read_text()
STAGE = (
    'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail* '
    '-- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_map)) :: pdestructionjob_tail* '
    '-- if S.OBJECTS[n_map] = WEAKMAPENTRIES ([pweakmapentry_field, pweakmapentry_leaf]) '
    '-- if pweakmapentry_field.VALUE = POBJECT n_field '
    '-- if $object_name(S, n_field) = $ptascii("GC40Value") '
    '-- if $weakmap_declared_value_child(S, n_field)')
CHECKS = [
    '$destructor_release_valid(S, pdestructionrelease)',
    'pweakmapentry_leaf.VALUE = POBJECT n_leaf',
    '$object_name(S, n_leaf) = $ptascii("GC40Leaf")',
    'n_field_key = pweakmapentry_field.KEY',
    'n_leaf_key = pweakmapentry_leaf.KEY',
    'n_field_key =/= n_leaf_key',
    '$weakmap_key_maps(S, S.ALLOCATIONS, n_field_key) = [n_map]',
    '$weakmap_key_maps(S, S.ALLOCATIONS, n_leaf_key) = [n_map]',
    '$weakmap_key_maps(S, S.ALLOCATIONS, n_map) = eps',
    '$node_children(S, HOBJECT n_map) = [HOBJECT n_field, HOBJECT n_leaf]',
    '$objectprops_at(S.OBJECTPROPS, n_field) = ([ppropertyslot])',
    'ppropertyslot.DECL =/= eps',
    'ppropertyslot.STATE = PROP_VALUE (DIRECT (POBJECT n_child))',
    '$object_name(S, n_child) = $ptascii("GC40Child")',
    '$node_children(S, HOBJECT n_field) = [HOBJECT n_child]',
    '$node_children(S, HOBJECT n_child) = eps',
    'H = $heap_graph(S)',
    '$heap_valid(H) /\\ $destruction_state_valid(S)',
    '$heap_owners(H, HOBJECT n_field) = 1',
    '$heap_owners(H, HOBJECT n_leaf) = 1',
    '$heap_owners(H, HOBJECT n_child) = 1',
    '~$weakmap_entries_teardown_table(S, n_map)',
    '~$weakmap_entries_callbacks(S, [pweakmapentry_field, pweakmapentry_leaf])',
    '$weakmap_entries_field_leaf_free(S, n_map, pweakmapentry_field, pweakmapentry_leaf)',
    '~$weakmap_entries_field_leaf_free(S, n_map, pweakmapentry_field[.KEY = n_leaf_key], pweakmapentry_leaf)',
    '$weakmap_entries_two_value_child_free(S, n_map)',
    'S_unheld = $destructor_release_replace(S, pdestructionrelease[.JOBS = pdestructionjob_tail*])',
    '$heap_owners($heap_graph(S_unheld), HOBJECT n_map) = 0',
    '$weakmap_entries_free_allowed(S_unheld, n_map, pdestructionrelease[.JOBS = pdestructionjob_tail*])',
    '~$weakmap_entries_free_allowed(S, n_map, pdestructionrelease)',
    'S_missing = S_unheld[.ALLOCATIONS = $destruction_node_delete(S_unheld.ALLOCATIONS, HOBJECT n_child)]',
    '~$weakmap_entries_two_value_child_free(S_missing, n_map)',
    '~$weakmap_entries_free_allowed(S_missing, n_map, pdestructionrelease[.JOBS = pdestructionjob_tail*])',
    'S_global = $global_table_view(S)',
    '$lookup(S_global.ENV, $ptascii("mapWatch")) = (n_map_watch_cell)',
    'S.STORE[n_map_watch_cell] = DEFINED (POBJECT n_map_watch)',
    'S.OBJECTS[n_map_watch] = WEAKREFERENCE (n_map)',
    '$lookup(S_global.ENV, $ptascii("firstWatch")) = (n_field_watch_cell)',
    'S.STORE[n_field_watch_cell] = DEFINED (POBJECT n_field_watch)',
    'S.OBJECTS[n_field_watch] = WEAKREFERENCE (n_field)',
    '$lookup(S_global.ENV, $ptascii("secondWatch")) = (n_leaf_watch_cell)',
    'S.STORE[n_leaf_watch_cell] = DEFINED (POBJECT n_leaf_watch)',
    'S.OBJECTS[n_leaf_watch] = WEAKREFERENCE (n_leaf)',
    'PhpStep: S ~> S_started',
    '$weakmap_key_maps(S_started, S_started.ALLOCATIONS, n_field_key) = eps',
    '$weakmap_key_maps(S_started, S_started.ALLOCATIONS, n_leaf_key) = eps',
    '$node_children(S_started, HOBJECT n_map) = eps',
    '$heap_owners($heap_graph(S_started), HOBJECT n_field) = 1',
    '$heap_owners($heap_graph(S_started), HOBJECT n_leaf) = 1',
    '$weakref_get(S_started, n_map_watch) = POBJECT n_map',
    '$weakref_get(S_started, n_field_watch) = POBJECT n_field',
    '$weakref_get(S_started, n_leaf_watch) = POBJECT n_leaf',
    '$heap_valid($heap_graph(S_started))',
    'S_zero = $drive_steps(S, 0)',
    'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = S_started[.COMPLETION = BUDGET]',
    'S_done = $drive_steps(S, 4000)',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
    '$weakref_get(S_done, n_map_watch) = PNULL',
    '$weakref_get(S_done, n_field_watch) = PNULL',
    '$weakref_get(S_done, n_leaf_watch) = PNULL',
    '~((HOBJECT n_map) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_field) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_leaf) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {'two-entry-map-first': {'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=240) else 1)
