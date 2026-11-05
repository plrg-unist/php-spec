#!/usr/bin/env python3
"""Reached finite write guards and append ownership without copied Child edges."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc44_prebuilt_value_insertion.php').read_text()
STAGE = (
    'S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail* '
    '-- if $lookup(S.ENV, $ptascii("map")) = (n_map_cell) '
    '-- if S.STORE[n_map_cell] = DEFINED (POBJECT n_map) '
    '-- if S.OBJECTS[n_map] = WEAKMAP (pweakmapentry_first) '
    '-- if pweakmapentry_first.VALUE = POBJECT n_value '
    '-- if $object_name(S, n_value) = $ptascii("GC44Value")')
CHECKS = [
    '$access_set_plan(S) = (paccess_plan)',
    'paccess_plan.OBJECT = (n_map)',
    'S_value = $quiet_operand(S, paccess_plan.RHS)',
    'S_value.RESULT = KNOWN (POBJECT n_value)',
    'S_key = $quiet_operand(S, paccess_plan.INPUT)',
    'S_key.RESULT = KNOWN (POBJECT n_key)',
    'paccess = paccess_plan[.SELECTED = $rcontainer_selected(S, paccess_plan.RHS)][.VALUE = POBJECT n_value][.OFFSET = POBJECT n_key]',
    'paccess.RHS = S.RESULT',
    'S.RESULT = VARIABLE ptbytes_rhs z_rhs',
    'ptbytes_rhs = $ptascii("value")',
    '$operand_nodes(paccess.RHS) = eps',
    '$lookup(S.ENV, $ptascii("value")) = (n_value_cell)',
    'S.STORE[n_value_cell] = DEFINED (POBJECT n_value)',
    '~(n_value_cell <- S.REFCELLS)',
    'paccess.SELECTED = paccess.RHS',
    'n_key =/= pweakmapentry_first.KEY',
    '$weakmap_key_maps(S, S.ALLOCATIONS, n_key) = eps',
    '$objectprops_at(S.OBJECTPROPS, n_value) = ([ppropertyslot_a, ppropertyslot_b, ppropertyslot_c])',
    'ppropertyslot_a.STATE = PROP_VALUE (DIRECT (POBJECT n_x))',
    'ppropertyslot_b.STATE = ppropertyslot_a.STATE',
    'ppropertyslot_c.STATE = PROP_VALUE (DIRECT (POBJECT n_y))',
    '$node_children(S, HOBJECT n_value) = [HOBJECT n_x, HOBJECT n_x, HOBJECT n_y]',
    'H = $heap_graph(S)',
    '$heap_valid(H)',
    '$heap_owners(H, HOBJECT n_value) = 2',
    '$heap_owners(H, HOBJECT n_x) = 2',
    '$heap_owners(H, HOBJECT n_y) = 1',
    '$weakmap_entries_child_storage(S, n_map)',
    '~$weakmap_entries_teardown_table(S, n_map)',
    '~$weakmap_table_leaves(S, [pweakmapentry_first])',
    '$weakmap_entries_write_allowed(S, paccess)',
    '~$weakmap_write_allowed(S, paccess)',
    '~$weakmap_replace_allowed(S, paccess)',
    '~$weakmap_entries_write_allowed(S, paccess[.SELECTED = KNOWN PNULL])',
    '~$weakmap_entries_write_allowed(S, paccess[.RHS = KNOWN PNULL])',
    'S_missing = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_y)]',
    '~$weakmap_entries_child_storage(S_missing, n_map)',
    '~$weakmap_entries_write_allowed(S_missing, paccess)',
    '$destructor_return_discarded(ptask_tail*)',
    '$weakmap_insert_result(S, paccess) = (S, PNULL)',
    'PhpStep: S ~> S_written',
    'S_written.OBJECTS[n_map] = WEAKMAPENTRIES ([pweakmapentry_first, pweakmapentry_second])',
    'pweakmapentry_second.KEY = n_key /\\ pweakmapentry_second.VALUE = POBJECT n_value',
    'pweakmapentry_second.BEFORE = $weakref_find(S, S.ALLOCATIONS, n_key)',
    'pweakmapentry_second.ORDER = 1',
    '$node_children(S_written, HOBJECT n_map) = [HOBJECT n_value, HOBJECT n_value]',
    '$node_children(S_written, HOBJECT n_value) = [HOBJECT n_x, HOBJECT n_x, HOBJECT n_y]',
    '$heap_owners($heap_graph(S_written), HOBJECT n_value) = 3',
    '$heap_owners($heap_graph(S_written), HOBJECT n_x) = 2',
    '$heap_owners($heap_graph(S_written), HOBJECT n_y) = 1',
    '$weakmap_key_maps(S_written, S_written.ALLOCATIONS, n_key) = [n_map]',
    'S_written.RESULT = KNOWN PNULL',
    'S_written.EVENTS = S.EVENTS',
    '$heap_valid($heap_graph(S_written))',
    '$weakmap_entries_child_storage(S_written, n_map)',
    '~$weakmap_table_leaves(S_written, [pweakmapentry_first, pweakmapentry_second])',
    '$lookup(S.ENV, $ptascii("mapWatch")) = (n_map_watch_cell)',
    'S.STORE[n_map_watch_cell] = DEFINED (POBJECT n_map_watch)',
    '$lookup(S.ENV, $ptascii("valueWatch")) = (n_value_watch_cell)',
    'S.STORE[n_value_watch_cell] = DEFINED (POBJECT n_value_watch)',
    '$lookup(S.ENV, $ptascii("xWatch")) = (n_x_watch_cell)',
    'S.STORE[n_x_watch_cell] = DEFINED (POBJECT n_x_watch)',
    '$lookup(S.ENV, $ptascii("yWatch")) = (n_y_watch_cell)',
    'S.STORE[n_y_watch_cell] = DEFINED (POBJECT n_y_watch)',
    'S_zero = $drive_steps(S, 0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_paused = $drive_steps(S, 1)',
    'S_paused.COMPLETION = BUDGET /\\ S_paused.TODO = S_written.TODO',
    '$heap_owners($heap_graph(S_paused), HOBJECT n_value) = 3',
    '$heap_owners($heap_graph(S_paused), HOBJECT n_x) = 2',
    '$heap_owners($heap_graph(S_paused), HOBJECT n_y) = 1',
    '$heap_valid($heap_graph(S_paused))',
    'S_done = $drive_steps(S, 4000)',
    '$drive_steps(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    '$weakref_get(S_done, n_map_watch) = PNULL',
    '$weakref_get(S_done, n_value_watch) = PNULL',
    '$weakref_get(S_done, n_x_watch) = PNULL',
    '$weakref_get(S_done, n_y_watch) = PNULL',
    '~((HOBJECT n_value) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_x) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_y) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
FIRST_WRITE_STAGE = (
    'S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail* '
    '-- if $lookup(S.ENV, $ptascii("map")) = (n_map_cell) '
    '-- if S.STORE[n_map_cell] = DEFINED (POBJECT n_map) '
    '-- if S.OBJECTS[n_map] = WEAKMAP eps '
    '-- if $access_set_plan(S) = (paccess_plan) '
    '-- if $lookup(S.ENV, $ptascii("value")) = (n_value_cell) '
    '-- if S.STORE[n_value_cell] = DEFINED (POBJECT n_value) '
    '-- if $object_name(S, n_value) = $ptascii("GC44Value")')
FIRST_WRITE_CHECKS = [
    '$access_set_plan(S) = (paccess_plan)',
    'paccess_plan.OBJECT = (n_map)',
    'S_value = $quiet_operand(S, paccess_plan.RHS)',
    'S_value.RESULT = KNOWN (POBJECT n_value)',
    'S_key = $quiet_operand(S, paccess_plan.INPUT)',
    'S_key.RESULT = KNOWN (POBJECT n_key)',
    'paccess = paccess_plan[.SELECTED = $rcontainer_selected(S, paccess_plan.RHS)][.VALUE = POBJECT n_value][.OFFSET = POBJECT n_key]',
    'paccess.RHS = S.RESULT',
    '$node_children(S, HOBJECT n_value) =/= eps',
    '$weakmap_entries_child_value_free(S, paccess.VALUE)',
    '$weakmap_write_value_allowed(S, paccess)',
    '$weakmap_write_allowed(S, paccess)',
    'n_dangling = |S.OBJECTS|',
    '~$weakmap_write_value_allowed(S, paccess[.VALUE = POBJECT n_dangling])',
    'S_missing = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_value)]',
    '~$weakmap_write_value_allowed(S_missing, paccess)',
    '~$weakmap_write_value_allowed(S, paccess[.SELECTED = KNOWN PNULL])',
    '~$weakmap_write_value_allowed(S, paccess[.RHS = KNOWN PNULL])',
    '~$weakmap_write_value_allowed(S[.TODO = eps], paccess)',
]
review.CASES = {
    'finite-value-append-owner': {'source': SOURCE, 'stage': STAGE, 'checks': CHECKS},
    'finite-value-first-write-guards': {
        'source': SOURCE, 'stage': FIRST_WRITE_STAGE, 'checks': FIRST_WRITE_CHECKS},
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=300) else 1)
