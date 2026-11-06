#!/usr/bin/env python3
"""A genuine current-Key dimension read adds only its copied outer-table owner."""
import argparse
import json
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc57_peer_current_key_dag_read.php').read_text()
STAGE = (
    'S.TODO = (KEY_READ_DIM poperand_key z KEY_R) :: ptask_tail* '
    '-- if S_base = $quiet_operand(S, S.RESULT) '
    '-- if S_base.RESULT = KNOWN (POBJECT n_map) '
    '-- if S.OBJECTS[n_map] = WEAKMAPENTRIES ([pweakmapentry_scalar, pweakmapentry_array]) '
    '-- if pweakmapentry_array.VALUE = PARRAY n_outer '
    '-- if S.ITERATORS = [WEAKMAPITER n n_map 2 n_keys*]')
CHUNKS = (['B|', 's|', '17', '|', 'R|', '1', '|', 'L|'] + ['1', '|'] * 2
          + ['D|', '1', '|', '1', '|', '0', '|', 'K|', '1', '|', 'k|', '1', '|', 'C|']
          + ['1', '|'] * 3 + ['F|', '1', '|'])
ENDING = 'S_done.EVENTS = [' + ', '.join(
    'OUTPUT $ptascii(' + json.dumps(chunk) + ')' for chunk in CHUNKS) + ']'
CHECKS = [
    'S.CURRENT = eps /\\ S.FRAMES = eps',
    'S.ORIGIN = (porigin)',
    'porigin = PORIGIN n_source pcpath_read',
    'pcpath_loop = pcpath_read[0:$nabs($(|pcpath_read| - 4))]',
    'pcpath_read = pcpath_loop ++ [PCFIELD 4, PCINDEX 0, PCFIELD 0, PCFIELD 1]',
    'porigin_loop = PORIGIN n_source pcpath_loop',
    '$origin_node(S.SOURCES, porigin_loop) = (statement)',
    'statement = NStmtForeach expression_iterable expression_key (BOOLEAN false) expression_value (SEQUENCE statement_body*) (BOOLEAN false) metadata',
    'z_loop = $runtime_line(S[.ORIGIN = (porigin_loop)], [PCFIELD 0], expression_iterable)',
    'ptask_loop = FOREACH_NEXT n (HOBJECT n_map) statement (porigin_loop) z_loop',
    '$goto_saved(S.TODO, porigin_loop) = GOTOTASKS (ptask_loop :: ptask_loop_tail*)',
    '$call_task_valid(S, ptask_loop)',
    'n_keys* = [n_scalar_key, n_key]',
    'pweakmapentry_scalar.KEY = n_scalar_key /\\ pweakmapentry_scalar.VALUE = PINT 17',
    'pweakmapentry_array.KEY = n_key',
    'S_key = $quiet_operand(S, poperand_key)',
    'S_key.RESULT = KNOWN (POBJECT n_key)',
    '$lookup(S.ENV, $ptascii("map57Peer")) = (n_map_cell)',
    'S.STORE[n_map_cell] = DEFINED (POBJECT n_map)',
    '$lookup(S.ENV, $ptascii("loopKey57Peer")) = (n_key_cell)',
    'S.STORE[n_key_cell] = DEFINED (POBJECT n_key)',
    '$lookup(S.ENV, $ptascii("loopValue57Peer")) = (n_loop_value_cell)',
    'S.STORE[n_loop_value_cell] = DEFINED (PARRAY n_outer)',
    '$lookup(S.ENV, $ptascii("held57Peer")) = (n_held_cell)',
    'S.STORE[n_held_cell] = DEFINED (PINT 17)',
    '$value_nodes(PINT 17) = eps',
    'S.ARRAYS[n_outer].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_inner)), ENTRY (KINT 1) (DIRECT (PARRAY n_inner))]',
    'S.ARRAYS[n_inner].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_value)), ENTRY (KINT 1) (DIRECT (PINT 0)), ENTRY (KINT 2) (DIRECT (POBJECT n_value))]',
    '$node_children(S, HOBJECT n_value) = [HOBJECT n_child]',
    '$objectprops_at(S.OBJECTPROPS, n_value) = ([ppropertyslot_child])',
    '$heap_owners($heap_graph(S), HOBJECT n_map) = 2',
    '$heap_owners($heap_graph(S), HOBJECT n_key) = 2',
    '$heap_owners($heap_graph(S), HARRAY n_outer) = 2',
    '$heap_owners($heap_graph(S), HARRAY n_inner) = 2',
    '$heap_owners($heap_graph(S), HOBJECT n_value) = 2',
    '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
    '$heap_count(HOBJECT n_map, $tasks_nodes(S.TODO)) = 1',
    '$heap_count(HARRAY n_outer, $tasks_nodes(S.TODO)) = 0',
    'paccess_initial = $access_record(S, porigin, z, ACCESS_READ KEY_R, BASE_VALUE S.RESULT, poperand_key, KNOWN PNULL, KEY_READ_DIM poperand_key z KEY_R, (n_map), true)',
    'paccess = paccess_initial[.SELECTED = $rcontainer_selected(S, S.RESULT)][.OFFSET = POBJECT n_key]',
    'paccess.SELECTED = S.RESULT',
    '$weakmap_read_allowed(S, paccess)',
    '$weakmap_foreach_current_read(S, paccess, S.TODO)',
    '$weakmap_entries_access_allowed(S, paccess, $ptascii("offsetGet"))',
    '~$weakmap_entries_access_storage(S, n_map, false)',
    '~$weakmap_entries_access_storage(S, n_map, true)',
    '~$weakmap_entries_child_storage(S, n_map)',
    '~$weakmap_entries_access_allowed(S, paccess, $ptascii("offsetExists"))',
    '~$weakmap_entries_access_allowed(S, paccess, $ptascii("offsetUnset"))',
    '~$weakmap_entries_access_allowed(S, paccess[.MODE = ACCESS_READ KEY_IS], $ptascii("offsetGet"))',
    '~$weakmap_entries_access_allowed(S, paccess[.MODE = ACCESS_READ (KEY_TEST false)], $ptascii("offsetGet"))',
    '~$weakmap_entries_access_allowed(S, paccess[.OFFSET = POBJECT n_scalar_key], $ptascii("offsetGet"))',
    '~$weakmap_entries_access_allowed(S, paccess[.SELECTED = KNOWN (POBJECT n_map)], $ptascii("offsetGet"))',
    '~$weakmap_entries_access_allowed(S, paccess[.TARGET = porigin_loop], $ptascii("offsetGet"))',
    '~$weakmap_entries_access_allowed(S, paccess[.OBJECT = (n_key)], $ptascii("offsetGet"))',
    'S_no_cursor = S[.ITERATORS = eps]',
    '~$weakmap_foreach_current_read(S_no_cursor, paccess, S_no_cursor.TODO)',
    'S_old_row = S[.ITERATORS = [WEAKMAPITER n n_map 1 n_keys*]]',
    '~$weakmap_entries_access_allowed(S_old_row, paccess, $ptascii("offsetGet"))',
    'S_unref = S[.REFCELLS = n_key_cell :: S.REFCELLS]',
    '~$weakmap_entries_access_allowed(S_unref, paccess, $ptascii("offsetGet"))',
    '~$weakmap_entries_access_allowed(S[.GC.WORKER = (n_map)], paccess, $ptascii("offsetGet"))',
    'S_no_marker = S[.TODO = $generator_foreach_drop(S.TODO, ptask_loop)]',
    '$weakmap_read_allowed(S_no_marker, paccess)',
    '~$weakmap_foreach_current_read(S_no_marker, paccess, S_no_marker.TODO)',
    '~$weakmap_entries_access_allowed(S_no_marker, paccess, $ptascii("offsetGet"))',
    'S_nearer = S[.TODO = (KEY_READ_DIM poperand_key z KEY_R) :: (FOREACH_NEXT S.NEXTITER (HOBJECT n_map) statement (porigin_loop) z_loop) :: ptask_tail*]',
    '~$weakmap_foreach_current_read(S_nearer, paccess, S_nearer.TODO)',
    # A constructed old leaf-only table must use its existing storage domain.
    'S_leaf = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS, n_value, [ppropertyslot_child[.STATE = PROP_VALUE (DIRECT PNULL)]])][.OBJECTS[n_map] = WEAKMAPENTRIES ([pweakmapentry_scalar[.VALUE = POBJECT n_value], pweakmapentry_array[.VALUE = POBJECT n_value]])]',
    '$weakmap_entries_foreach_storage(S_leaf, n_map)',
    '~$weakmap_finite_foreach_storage(S_leaf, n_map)',
    '$weakmap_entries_access_allowed(S_leaf, paccess, $ptascii("offsetGet"))',
    '$call_descriptors_valid(S) /\\ $heap_valid($heap_graph(S))',
    'S_zero = $drive_steps(S, 0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_read = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
    'S_read.TODO = ptask_tail*',
    'S_read.RESULT = KNOWN (PARRAY n_outer)',
    'S_read.STORE[n_held_cell] = DEFINED (PINT 17)',
    '$heap_count(HARRAY n_outer, $operand_nodes(S_read.RESULT)) = 1',
    '$heap_owners($heap_graph(S_read), HARRAY n_outer) = 3',
    '$heap_owners($heap_graph(S_read), HARRAY n_inner) = 2',
    '$heap_owners($heap_graph(S_read), HOBJECT n_value) = 2',
    '$heap_owners($heap_graph(S_read), HOBJECT n_child) = 1',
    '$heap_owners($heap_graph(S_read), HOBJECT n_map) = 2',
    '$heap_owners($heap_graph(S_read), HOBJECT n_key) = 2',
    '$heap_count(HOBJECT n_map, $tasks_nodes(S_read.TODO)) = 1',
    'S_read.ARRAYS = S.ARRAYS /\\ S_read.OBJECTS = S.OBJECTS',
    'S_read.OBJECTPROPS = S.OBJECTPROPS /\\ S_read.EVENTS = S.EVENTS',
    '$call_descriptors_valid(S_read) /\\ $heap_valid($heap_graph(S_read))',
    'S_paused = $drive_steps(S, 1)',
    'S_paused = S_read[.COMPLETION = BUDGET]',
    'S_done = $drive_steps(S, 4000)',
    '$drive_steps(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    'S_done.ITERATORS = eps',
    ENDING,
    '~((HOBJECT n_map) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_key) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_scalar_key) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_value) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
    '~((HARRAY n_outer) <- S_done.ALLOCATIONS)',
    '~((HARRAY n_inner) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {'current-key-read-result-owner': {
    'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=360) else 1)
