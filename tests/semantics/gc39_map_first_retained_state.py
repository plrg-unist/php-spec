#!/usr/bin/env python3
"""Reached Map free accepts a Value whose Child has one outside owner."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc39_map_first_retained_observers.php').read_text()
STAGE = (
    'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail* '
    '-- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_map)) :: pdestructionjob_tail* '
    '-- if S.OBJECTS[n_map] = WEAKMAP (pweakmapentry) '
    '-- if pweakmapentry.VALUE = POBJECT n_value '
    '-- if $object_name(S, n_value) = $ptascii("GC39Value") '
    '-- if $weakmap_declared_value_child_owners(S, n_value, 2)')
CHECKS = [
    '$destructor_release_valid(S, pdestructionrelease)',
    'n_key = pweakmapentry.KEY',
    'S.OBJECTS[n_key] = STDINSTANCE',
    '$node_children(S, HOBJECT n_key) = eps',
    '$weakmap_key_maps(S, S.ALLOCATIONS, n_key) = [n_map]',
    '$weakmap_key_maps(S, S.ALLOCATIONS, n_map) = eps',
    '$node_children(S, HOBJECT n_map) = [HOBJECT n_value]',
    '$objectprops_at(S.OBJECTPROPS, n_value) = ([ppropertyslot])',
    'ppropertyslot.DECL =/= eps',
    'ppropertyslot.STATE = PROP_VALUE (DIRECT (POBJECT n_child))',
    '$object_name(S, n_child) = $ptascii("GC39Child")',
    '$node_children(S, HOBJECT n_value) = [HOBJECT n_child]',
    '$node_children(S, HOBJECT n_child) = eps',
    'H = $heap_graph(S)',
    '$heap_valid(H) /\\ $destruction_state_valid(S)',
    '$heap_owners(H, HOBJECT n_value) = 1',
    '$heap_owners(H, HOBJECT n_child) = 2',
    '~$weakmap_declared_value_child(S, n_value)',
    '~$weakmap_declared_value_child_owners(S, n_value, 3)',
    '~$weakmap_free_slot_allowed(S, POBJECT n_value)',
    '$weakmap_map_free_slot_allowed(S, n_map, POBJECT n_value)',
    'S_unheld = $destructor_release_replace(S, pdestructionrelease[.JOBS = pdestructionjob_tail*])',
    '$heap_owners($heap_graph(S_unheld), HOBJECT n_map) = 0',
    '$weakmap_free_allowed(S_unheld, n_map, pdestructionrelease[.JOBS = pdestructionjob_tail*])',
    'S_global = $global_table_view(S)',
    '$lookup(S_global.ENV, $ptascii("child")) = (n_child_cell)',
    'S.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
    '$lookup(S_global.ENV, $ptascii("mapWatch")) = (n_map_watch_cell)',
    'S.STORE[n_map_watch_cell] = DEFINED (POBJECT n_map_watch)',
    'S.OBJECTS[n_map_watch] = WEAKREFERENCE (n_map)',
    '$lookup(S_global.ENV, $ptascii("valueWatch")) = (n_value_watch_cell)',
    'S.STORE[n_value_watch_cell] = DEFINED (POBJECT n_value_watch)',
    'S.OBJECTS[n_value_watch] = WEAKREFERENCE (n_value)',
    '$lookup(S_global.ENV, $ptascii("keyWatch")) = (n_key_watch_cell)',
    'S.STORE[n_key_watch_cell] = DEFINED (POBJECT n_key_watch)',
    'S.OBJECTS[n_key_watch] = WEAKREFERENCE (n_key)',
    '$weakref_get(S, n_map_watch) = POBJECT n_map',
    '$weakref_get(S, n_value_watch) = POBJECT n_value',
    '$weakref_get(S, n_key_watch) = POBJECT n_key',
    'PhpStep: S ~> S_started',
    'S_started.OBJECTS[n_map] = WEAKMAP eps',
    '$weakmap_key_maps(S_started, S_started.ALLOCATIONS, n_key) = eps',
    '$heap_owners($heap_graph(S_started), HOBJECT n_child) = 2',
    '$weakref_get(S_started, n_map_watch) = POBJECT n_map',
    '$heap_valid($heap_graph(S_started))',
    'S_zero = $drive_steps(S, 0)',
    'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = $drive_steps(S, 1)',
    'S_done = $drive_steps(S, 4000)',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
    '$weakref_get(S_done, n_map_watch) = PNULL',
    '$weakref_get(S_done, n_value_watch) = PNULL',
    '$weakref_get(S_done, n_key_watch) = PNULL',
    '~((HOBJECT n_map) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_value) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {'map-first-retained-child': {'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=240) else 1)
