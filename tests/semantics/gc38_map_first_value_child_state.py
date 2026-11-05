#!/usr/bin/env python3
"""Reached Map free transfers one declared-child Value owner before weak notice."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc38_map_first_value_child.php').read_text()
STAGE = (
    'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail* '
    '-- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_map)) :: pdestructionjob_tail* '
    '-- if S.OBJECTS[n_map] = WEAKMAP (pweakmapentry) '
    '-- if pweakmapentry.VALUE = POBJECT n_value '
    '-- if $object_name(S, n_value) = $ptascii("GC38Value") '
    '-- if $weakmap_declared_value_child(S, n_value)')
CHECKS = [
    '$destructor_release_valid(S, pdestructionrelease)',
    'n_key = pweakmapentry.KEY',
    'S.OBJECTS[n_key] = STDINSTANCE',
    '$node_children(S, HOBJECT n_key) = eps',
    '$weakmap_key_maps(S, S.ALLOCATIONS, n_key) = [n_map]',
    '$node_children(S, HOBJECT n_map) = [HOBJECT n_value]',
    '$objectprops_at(S.OBJECTPROPS, n_value) = ([ppropertyslot])',
    'ppropertyslot.DECL =/= eps',
    'ppropertyslot.STATE = PROP_VALUE (DIRECT (POBJECT n_child))',
    '$object_name(S, n_child) = $ptascii("GC38Child")',
    '$node_children(S, HOBJECT n_value) = [HOBJECT n_child]',
    '$node_children(S, HOBJECT n_child) = eps',
    'H = $heap_graph(S)',
    '$heap_valid(H) /\\ $destruction_state_valid(S)',
    '$heap_owners(H, HOBJECT n_child) = 1',
    '~$weakmap_free_slot_allowed(S, POBJECT n_value)',
    '~$weakmap_free_value_allowed(S, POBJECT n_value)',
    '$weakmap_map_free_slot_allowed(S, POBJECT n_value)',
    'S_unheld = $destructor_release_replace(S, pdestructionrelease[.JOBS = pdestructionjob_tail*])',
    '$heap_owners($heap_graph(S_unheld), HOBJECT n_map) = 0',
    '$weakmap_free_allowed(S_unheld, n_map, pdestructionrelease[.JOBS = pdestructionjob_tail*])',
    'S_missing = S_unheld[.ALLOCATIONS = $destruction_node_delete(S_unheld.ALLOCATIONS, HOBJECT n_child)]',
    '~$weakmap_map_free_slot_allowed(S_missing, POBJECT n_value)',
    '~$weakmap_free_allowed(S_missing, n_map, pdestructionrelease[.JOBS = pdestructionjob_tail*])',
    'S_global = $global_table_view(S)',
    '$lookup(S_global.ENV, $ptascii("gc38MapWatch")) = (n_map_watch_cell)',
    'S.STORE[n_map_watch_cell] = DEFINED (POBJECT n_map_watch)',
    'S.OBJECTS[n_map_watch] = WEAKREFERENCE (n_map)',
    '$lookup(S_global.ENV, $ptascii("gc38ValueWatch")) = (n_value_watch_cell)',
    'S.STORE[n_value_watch_cell] = DEFINED (POBJECT n_value_watch)',
    'S.OBJECTS[n_value_watch] = WEAKREFERENCE (n_value)',
    '$weakref_get(S, n_map_watch) = POBJECT n_map',
    '$weakref_get(S, n_value_watch) = POBJECT n_value',
    'PhpStep: S ~> S_started',
    'S_started.OBJECTS[n_map] = WEAKMAP eps',
    '$weakmap_key_maps(S_started, S_started.ALLOCATIONS, n_key) = eps',
    '(HOBJECT n_key) <- S_started.ALLOCATIONS',
    '$node_children(S_started, HOBJECT n_map) = eps',
    '$weakref_get(S_started, n_map_watch) = POBJECT n_map',
    '$heap_valid($heap_graph(S_started))',
    'S_zero = $drive_steps(S, 0)',
    'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = $drive_steps(S, 1)',
    'S_done = $drive_steps(S, 4000)',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
    '$weakref_get(S_done, n_map_watch) = PNULL',
    '$weakref_get(S_done, n_value_watch) = PNULL',
    '~((HOBJECT n_map) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_value) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {'map-first-declared-child': {'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=240) else 1)
