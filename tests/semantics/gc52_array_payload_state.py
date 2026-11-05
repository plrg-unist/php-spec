#!/usr/bin/env python3
"""A genuine COW copy retires one array and transfers its physical Value edges."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc52_peer_array_cow_throw.php').read_text()
STAGE = (
    'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail* '
    '-- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HARRAY n_copy)) :: pdestructionjob_tail* '
    '-- if $lookup(S.ENV, $ptascii("map")) = (n_map_cell) '
    '-- if S.STORE[n_map_cell] = DEFINED (POBJECT n_map) '
    '-- if S.OBJECTS[n_map] = WEAKMAP (pweakmapentry) '
    '-- if pweakmapentry.VALUE = PARRAY n_original '
    '-- if n_copy =/= n_original '
    '-- if S.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 1) (DIRECT (POBJECT n_b)), ENTRY (KINT 2) (DIRECT (POBJECT n_a))]')
CHECKS = [
    'S.CURRENT = eps /\\ S.FRAMES = eps',
    'pdestructionjob_tail* = eps',
    '$destructor_release_valid(S, pdestructionrelease)',
    '$task_nodes(DESTRUCTOR_RELEASE pdestructionrelease) = [HARRAY n_copy]',
    'n_key = pweakmapentry.KEY',
    'S.ARRAYS[n_original].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_a)), ENTRY (KINT 1) (DIRECT (POBJECT n_b)), ENTRY (KINT 2) (DIRECT (POBJECT n_a))]',
    '$node_children(S, HOBJECT n_map) = [HARRAY n_original]',
    '$node_children(S, HARRAY n_original) = [HOBJECT n_a, HOBJECT n_b, HOBJECT n_a]',
    '$node_children(S, HARRAY n_copy) = [HOBJECT n_b, HOBJECT n_a]',
    '$node_children(S, HOBJECT n_a) = [HOBJECT n_x]',
    '$node_children(S, HOBJECT n_b) = [HOBJECT n_y]',
    'n_a =/= n_b /\\ n_x =/= n_y',
    '$heap_valid($heap_graph(S))',
    '$heap_owners($heap_graph(S), HOBJECT n_map) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_key) = 1',
    '$heap_owners($heap_graph(S), HARRAY n_original) = 1',
    '$heap_owners($heap_graph(S), HARRAY n_copy) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_a) = 3',
    '$heap_owners($heap_graph(S), HOBJECT n_b) = 2',
    '$heap_owners($heap_graph(S), HOBJECT n_x) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_y) = 1',
    '$weakmap_entries_child_value_free(S, PARRAY n_original)',
    '$weakmap_entries_child_value_free(S, PARRAY n_copy)',
    '$weakmap_entries_child_storage(S, n_map)',
    '~$weakmap_entries_teardown_table(S, n_map)',
    '~$weakmap_reference_value_allowed(S, PARRAY n_original)',
    '~$weakmap_free_slot_allowed(S, PARRAY n_original)',
    '$weakmap_map_free_slot_allowed(S, n_map, PARRAY n_original)',
    '~$weakmap_entries_property_value_free(S, PARRAY n_original)',
    '~$weakmap_entries_array_item_free(S, DIRECT (PARRAY n_original))',
    '~$weakmap_entries_child_value_free(S, PARRAY (|S.ARRAYS|))',
    'S_unallocated = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HARRAY n_copy)]',
    '~$weakmap_entries_child_value_free(S_unallocated, PARRAY n_copy)',
    'S_nested = S[.ARRAYS[n_copy] = S.ARRAYS[n_copy][.ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_original))]]]',
    '$heap_valid($heap_graph(S_nested))',
    '$weakmap_entries_child_value_free(S_nested, PARRAY n_original)',
    '~$weakmap_entries_child_value_free(S_nested, PARRAY n_copy)',
    'S_duplicate = S[.ARRAYS[n_copy] = S.ARRAYS[n_copy][.ITEMS = [ENTRY (KINT 1) (DIRECT (POBJECT n_b)), ENTRY (KINT 1) (DIRECT (POBJECT n_a))]]]',
    '$heap_valid($heap_graph(S_duplicate))',
    '~$weakmap_entries_child_value_free(S_duplicate, PARRAY n_copy)',
    'n_cell = |S.STORE|',
    'S_reference = S[.STORE = S.STORE ++ [DEFINED (POBJECT n_key)]][.REFCELLS = S.REFCELLS ++ [n_cell]][.ALLOCATIONS = S.ALLOCATIONS ++ [HCELL n_cell]][.ARRAYS[n_copy] = $array_insert($array_empty(), KINT 0, ALIAS n_cell)]',
    '$heap_valid($heap_graph(S_reference))',
    '$weakmap_array_backedge(S_reference, n_copy, n_key)',
    '~$weakmap_entries_array_item_free(S_reference, ALIAS n_cell)',
    '~$weakmap_entries_child_value_free(S_reference, PARRAY n_copy)',
    'S_zero = $drive_steps(S, 0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_paused = $drive_steps(S, 1)',
    'S_paused.COMPLETION = BUDGET',
    'S_transferred = S_paused[.COMPLETION = NORMAL]',
    'S_transferred.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_children) :: ptask_tail*',
    'pdestructionrelease_children = pdestructionrelease[.JOBS = [DESTRUCTION_VALUE (HOBJECT n_b), DESTRUCTION_VALUE (HOBJECT n_a)]]',
    '$destructor_release_valid(S_transferred, pdestructionrelease_children)',
    '$task_nodes(DESTRUCTOR_RELEASE pdestructionrelease_children) = [HOBJECT n_b, HOBJECT n_a]',
    '~((HARRAY n_copy) <- S_transferred.ALLOCATIONS)',
    '(HARRAY n_original) <- S_transferred.ALLOCATIONS',
    'S_transferred.ARRAYS[n_copy] = S.ARRAYS[n_copy]',
    'S_transferred.ARRAYS[n_original] = S.ARRAYS[n_original]',
    'S_transferred.OBJECTS[n_map] = S.OBJECTS[n_map]',
    '$heap_owners($heap_graph(S_transferred), HARRAY n_copy) = 0',
    '$heap_owners($heap_graph(S_transferred), HARRAY n_original) = 1',
    '$heap_owners($heap_graph(S_transferred), HOBJECT n_a) = 3',
    '$heap_owners($heap_graph(S_transferred), HOBJECT n_b) = 2',
    '$heap_owners($heap_graph(S_transferred), HOBJECT n_x) = 1',
    '$heap_owners($heap_graph(S_transferred), HOBJECT n_y) = 1',
    '$weakmap_entries_child_storage(S_transferred, n_map)',
    '$heap_valid($heap_graph(S_transferred))',
    'S_transferred.EVENTS = S.EVENTS',
    'S_transferred.GC = $gc_buffer_drop(S.GC, HARRAY n_copy)',
    'S_b_paused = $drive_steps(S_transferred, 1)',
    'S_b_paused.COMPLETION = BUDGET',
    'S_b = S_b_paused[.COMPLETION = NORMAL]',
    'S_b.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_a) :: ptask_tail*',
    'pdestructionrelease_a = pdestructionrelease[.JOBS = [DESTRUCTION_VALUE (HOBJECT n_a)]]',
    '$heap_owners($heap_graph(S_b), HOBJECT n_b) = 1',
    '$heap_owners($heap_graph(S_b), HOBJECT n_a) = 3',
    '$heap_owners($heap_graph(S_b), HOBJECT n_x) = 1',
    '$heap_owners($heap_graph(S_b), HOBJECT n_y) = 1',
    'S_b.EVENTS = S.EVENTS',
    '$heap_valid($heap_graph(S_b))',
    'S_done = $drive_steps(S, 4000)',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 4000) = S_done',
    '$drive_steps(S_transferred, 4000) = S_done',
    '$drive_steps(S_b, 4000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    '~((HARRAY n_original) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_map) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_a) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_b) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_x) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_y) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_key) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {'cow-array-owner-transfer': {'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=360) else 1)
