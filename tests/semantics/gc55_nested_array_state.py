#!/usr/bin/env python3
"""A real outer-array release transfers two edges to one shared inner table."""
import argparse
import json
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc55_peer_shared_inner_array_throw.php').read_text()
STAGE = (
    'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail* '
    '-- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HARRAY n_outer)) :: pdestructionjob_tail* '
    '-- if S.ARRAYS[n_outer].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_inner)), ENTRY (KINT 1) (DIRECT (PARRAY n_inner)), ENTRY (KINT 2) (DIRECT (PINT 0))] '
    '-- if $lookup(S.ENV, $ptascii("mapWatch55")) = (n_map_watch_cell) '
    '-- if S.STORE[n_map_watch_cell] = DEFINED (POBJECT n_map_watch) '
    '-- if $weakref_get(S, n_map_watch) = POBJECT n_map '
    '-- if $instance_storage_freeing(S, n_map)')
CHUNKS = (['B|', 'S|'] + ['1', '|'] * 2 + ['Y|'] + ['1', '|'] * 4
          + ['X|'] + ['1', '|'] * 4
          + ['T|', '1', '|', 'makeNestedArrayFailure55', '|', '0', '|']
          + ['1', '|'] * 4 + ['A|', '1', '|'])
ENDING = 'S_done.EVENTS = [' + ', '.join(
    'OUTPUT $ptascii(' + json.dumps(chunk) + ')' for chunk in CHUNKS) + ']'
CHECKS = [
    'S.CURRENT = eps /\\ S.FRAMES = eps',
    'pdestructionjob_tail* = eps',
    '$destructor_release_valid(S, pdestructionrelease)',
    'n_outer =/= n_inner',
    'S.ARRAYS[n_inner].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_a)), ENTRY (KINT 1) (DIRECT (POBJECT n_b)), ENTRY (KINT 2) (DIRECT (POBJECT n_a))]',
    '$node_children(S, HARRAY n_outer) = [HARRAY n_inner, HARRAY n_inner]',
    '$node_children(S, HARRAY n_inner) = [HOBJECT n_a, HOBJECT n_b, HOBJECT n_a]',
    '$node_children(S, HOBJECT n_a) = [HOBJECT n_x]',
    '$node_children(S, HOBJECT n_b) = [HOBJECT n_y]',
    '$heap_owners($heap_graph(S), HARRAY n_outer) = 1',
    '$heap_owners($heap_graph(S), HARRAY n_inner) = 2',
    '$heap_owners($heap_graph(S), HOBJECT n_a) = 2',
    '$heap_owners($heap_graph(S), HOBJECT n_b) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_x) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_y) = 1',
    'S.OBJECTS[n_map] = WEAKMAP eps',
    '$heap_owners($heap_graph(S), HOBJECT n_map) = 1',
    '$lookup(S.ENV, $ptascii("key")) = (n_key_cell)',
    'S.STORE[n_key_cell] = DEFINED (POBJECT n_key)',
    '$heap_owners($heap_graph(S), HOBJECT n_key) = 1',
    '$weakmap_key_maps(S, S.ALLOCATIONS, n_key) = eps',
    '$heap_valid($heap_graph(S)) /\\ $destruction_state_valid(S)',
    '$weakmap_entries_child_value_free(S, PARRAY n_outer)',
    '$weakmap_entries_array_value_free(S, n_inner, [n_outer])',
    '$weakmap_entries_array_graph_item_free(S, DIRECT (PARRAY n_inner), [n_outer])',
    '~$weakmap_entries_array_value_free(S, n_inner, [n_inner])',
    '~$weakmap_entries_array_item_free(S, DIRECT (PARRAY n_inner))',
    '~$weakmap_entries_property_value_free(S, PARRAY n_outer)',
    '~$weakmap_entries_property_array_entries_free(S, [ENTRY (KINT 0) (DIRECT (PARRAY n_inner))])',
    # Constructed ancestor-cycle/reference controls carry no PHP agreement.
    'S_cycle = S[.ARRAYS[n_inner] = S.ARRAYS[n_inner][.ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_outer))]]]',
    '$heap_valid($heap_graph(S_cycle))',
    '~$weakmap_entries_array_value_free(S_cycle, n_inner, [n_outer])',
    '~$weakmap_entries_child_value_free(S_cycle, PARRAY n_outer)',
    'n_cell = |S.STORE|',
    'S_reference = S[.STORE = S.STORE ++ [DEFINED (POBJECT n_key)]][.REFCELLS = S.REFCELLS ++ [n_cell]][.ALLOCATIONS = S.ALLOCATIONS ++ [HCELL n_cell]][.ARRAYS[n_inner] = $array_insert($array_empty(), KINT 0, ALIAS n_cell)]',
    '$heap_valid($heap_graph(S_reference))',
    '$weakmap_array_backedge(S_reference, n_inner, n_key)',
    '~$weakmap_entries_array_graph_item_free(S_reference, ALIAS n_cell, [n_outer, n_inner])',
    '~$weakmap_entries_child_value_free(S_reference, PARRAY n_outer)',
    'S_duplicate = S[.ARRAYS[n_outer] = S.ARRAYS[n_outer][.ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_inner)), ENTRY (KINT 0) (DIRECT (PARRAY n_inner))]]]',
    '$heap_valid($heap_graph(S_duplicate))',
    '~$weakmap_entries_child_value_free(S_duplicate, PARRAY n_outer)',
    '~$weakmap_entries_array_value_free(S, |S.ARRAYS|, eps)',
    'S_unallocated = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HARRAY n_inner)]',
    '~$weakmap_entries_array_value_free(S_unallocated, n_inner, eps)',
    'S_zero = $drive_steps(S, 0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_transferred = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
    'S_transferred.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_inner) :: ptask_tail*',
    'pdestructionrelease_inner = pdestructionrelease[.JOBS = [DESTRUCTION_VALUE (HARRAY n_inner), DESTRUCTION_VALUE (HARRAY n_inner)]]',
    '$task_nodes(DESTRUCTOR_RELEASE pdestructionrelease_inner) = [HARRAY n_inner, HARRAY n_inner]',
    '~((HARRAY n_outer) <- S_transferred.ALLOCATIONS)',
    '(HARRAY n_inner) <- S_transferred.ALLOCATIONS',
    'S_transferred.ARRAYS[n_outer] = S.ARRAYS[n_outer]',
    'S_transferred.ARRAYS[n_inner] = S.ARRAYS[n_inner]',
    '$heap_owners($heap_graph(S_transferred), HARRAY n_outer) = 0',
    '$heap_owners($heap_graph(S_transferred), HARRAY n_inner) = 2',
    '$heap_owners($heap_graph(S_transferred), HOBJECT n_a) = 2',
    '$heap_owners($heap_graph(S_transferred), HOBJECT n_b) = 1',
    '$heap_owners($heap_graph(S_transferred), HOBJECT n_x) = 1',
    '$heap_owners($heap_graph(S_transferred), HOBJECT n_y) = 1',
    'S_transferred.EVENTS = S.EVENTS',
    '$heap_valid($heap_graph(S_transferred)) /\\ $destruction_state_valid(S_transferred)',
    'S_shared = $drive_steps(S_transferred, 1)[.COMPLETION = NORMAL]',
    'S_shared.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_inner[.JOBS = [DESTRUCTION_VALUE (HARRAY n_inner)]]) :: ptask_tail*',
    '$heap_owners($heap_graph(S_shared), HARRAY n_inner) = 1',
    '$heap_owners($heap_graph(S_shared), HOBJECT n_a) = 2',
    '$heap_owners($heap_graph(S_shared), HOBJECT n_b) = 1',
    '$heap_owners($heap_graph(S_shared), HOBJECT n_x) = 1',
    '$heap_owners($heap_graph(S_shared), HOBJECT n_y) = 1',
    'S_shared.EVENTS = S.EVENTS',
    '$heap_valid($heap_graph(S_shared))',
    'S_paused = $drive_steps(S, 2)',
    'S_paused.COMPLETION = BUDGET /\\ S_paused.TODO = S_shared.TODO',
    '$heap_owners($heap_graph(S_paused), HARRAY n_inner) = 1',
    'S_done = $drive_steps(S, 4000)',
    '$drive_steps(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    ENDING,
    '~((HARRAY n_outer) <- S_done.ALLOCATIONS)',
    '~((HARRAY n_inner) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_map) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_key) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_a) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_b) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_x) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_y) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {'nested-array-inner-owner-transfer': {'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=360) else 1)
