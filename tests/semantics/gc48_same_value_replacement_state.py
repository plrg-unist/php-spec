#!/usr/bin/env python3
"""A real identical occupied write visits the old zval without changing owners."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc48_same_value_replacement.php').read_text()
STAGE = (
    'S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail* '
    '-- if $lookup(S.ENV, $ptascii("map")) = (n_map_cell) '
    '-- if S.STORE[n_map_cell] = DEFINED (POBJECT n_map) '
    '-- if S.OBJECTS[n_map] = WEAKMAP (pweakmapentry) '
    '-- if $access_set_plan(S) = (paccess_plan) '
    '-- if paccess_plan.OBJECT = (n_map) '
    '-- if pweakmapentry.VALUE = POBJECT n_value '
    '-- if $object_name(S, n_value) = $ptascii("GC48SameValue")')
CHECKS = [
    'S_value = $quiet_operand(S, paccess_plan.RHS)',
    'S_value.RESULT = KNOWN (POBJECT n_value)',
    'S_key = $quiet_operand(S, paccess_plan.INPUT)',
    'S_key.RESULT = KNOWN (POBJECT n_key)',
    'n_key = pweakmapentry.KEY',
    'paccess = paccess_plan[.SELECTED = $rcontainer_selected(S, paccess_plan.RHS)][.VALUE = POBJECT n_value][.OFFSET = POBJECT n_key]',
    'paccess.RHS = S.RESULT',
    'S.RESULT = VARIABLE ptbytes_rhs z_rhs',
    'ptbytes_rhs = $ptascii("value")',
    '$operand_nodes(paccess.RHS) = eps',
    '$lookup(S.ENV, $ptascii("value")) = (n_value_cell)',
    'S.STORE[n_value_cell] = DEFINED (POBJECT n_value)',
    '~(n_value_cell <- S.REFCELLS)',
    '$objectprops_at(S.OBJECTPROPS, n_value) = ([ppropertyslot])',
    'ppropertyslot.STATE = PROP_VALUE (DIRECT (POBJECT n_child))',
    '$node_children(S, HOBJECT n_value) = [HOBJECT n_child]',
    'H = $heap_graph(S)',
    '$heap_valid(H)',
    '$heap_owners(H, HOBJECT n_map) = 1',
    '$heap_owners(H, HOBJECT n_key) = 1',
    '$heap_owners(H, HOBJECT n_value) = 2',
    '$heap_owners(H, HOBJECT n_child) = 1',
    '$weakmap_entries_child_storage(S, n_map)',
    '~$weakmap_entries_teardown_table(S, n_map)',
    '~$weakmap_replace_allowed(S, paccess)',
    '$weakmap_entries_write_allowed(S, paccess)',
    '~$weakmap_entries_write_allowed(S, paccess[.SELECTED = KNOWN PNULL])',
    '~$weakmap_entries_write_allowed(S, paccess[.RHS = KNOWN PNULL])',
    '~$weakmap_entries_write_allowed(S[.TODO = eps], paccess)',
    'S_missing = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_child)]',
    '~$weakmap_entries_write_allowed(S_missing, paccess)',
    'S_cursor = S[.ITERATORS = [OBJECTITER 0 n_map 0 false]]',
    '~$weakmap_entries_write_allowed(S_cursor, paccess)',
    '~((HOBJECT n_value) <- $gc_nodes(S.GC.BUFFER))',
    'pnode_before* = $gc_nodes(S.GC.BUFFER)',
    'S_zero = $drive_steps(S, 0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_paused = $drive_steps(S, 1)',
    'S_paused.COMPLETION = BUDGET',
    'S_written = S_paused[.COMPLETION = NORMAL]',
    'S_written.TODO = (ACCESS_RESUME paccess_called) :: ptask_tail*',
    'paccess_called = paccess[.PHASE = ACCESS_CALL $ptascii("offsetSet")]',
    '$weakmap_set_resume(S_written, paccess_called)',
    'S_written.OBJECTS[n_map] = WEAKMAP (pweakmapentry)',
    '$weakmap_key_maps(S_written, S_written.ALLOCATIONS, n_key) = [n_map]',
    '$node_children(S_written, HOBJECT n_value) = [HOBJECT n_child]',
    '$heap_owners($heap_graph(S_written), HOBJECT n_map) = 2',
    '$heap_owners($heap_graph(S_written), HOBJECT n_key) = 1',
    '$heap_owners($heap_graph(S_written), HOBJECT n_value) = 2',
    '$heap_owners($heap_graph(S_written), HOBJECT n_child) = 1',
    '$task_nodes(ACCESS_RESUME paccess_called) = [HOBJECT n_map]',
    'S_written.GC = $gc_buffer_add(S.GC, HOBJECT n_value)',
    '$gc_nodes(S_written.GC.BUFFER) = pnode_before* ++ [HOBJECT n_value]',
    '$(|$gc_nodes(S_written.GC.BUFFER)| = |pnode_before*| + 1)',
    '$weakmap_replaced_value(S_written, POBJECT n_value, POBJECT n_value) = S_written',
    '$weakmap_replaced_value(S, POBJECT n_value, PNULL) = S',
    'S_written.EVENTS = S.EVENTS',
    '$heap_valid($heap_graph(S_written)) /\\ $gc_buffer_valid(S_written, S_written.GC)',
    'S_done = $drive_steps(S, 4000)',
    '$drive_steps(S_written, 4000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    'S_done.EVENTS = [OUTPUT $ptascii("B|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("C|")]',
    '~((HOBJECT n_map) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_value) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {'same-value-occupied-replacement': {'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=300) else 1)
