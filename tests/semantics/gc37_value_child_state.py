#!/usr/bin/env python3
"""Reached first WeakMap insertion transfers a field-bearing Value owner."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc37_value_child_preinsert.php').read_text()
STAGE = (
    'S.TODO = (ASSIGN_ARRAY pbase z b) :: ptask_tail* '
    '-- if $lookup(S.ENV, $ptascii("value")) = (n_value_cell) '
    '-- if S.STORE[n_value_cell] = DEFINED (POBJECT n_value) '
    '-- if $lookup(S.ENV, $ptascii("map")) = (n_map_cell) '
    '-- if S.STORE[n_map_cell] = DEFINED (POBJECT n_map) '
    '-- if S.OBJECTS[n_map] = WEAKMAP eps '
    '-- if $object_name(S, n_value) = $ptascii("GC37ValuePre") '
    '-- if $weakmap_declared_value_child(S, n_value)')
CHECKS = [
    '$access_set_plan(S) = (paccess_plan)',
    'paccess_plan.OBJECT = (n_map)',
    'S_value = $quiet_operand(S, paccess_plan.RHS)',
    'S_value.RESULT = KNOWN (POBJECT n_value)',
    'S_key = $quiet_operand(S, paccess_plan.INPUT)',
    'S_key.RESULT = KNOWN (POBJECT n_key)',
    'paccess = paccess_plan[.SELECTED = $rcontainer_selected(S, paccess_plan.RHS)][.VALUE = POBJECT n_value][.OFFSET = POBJECT n_key]',
    'S.TODO = paccess.TASK :: ptask_tail*',
    'S.OBJECTS[n_key] = STDINSTANCE',
    '$node_children(S, HOBJECT n_key) = eps',
    '$objectprops_at(S.OBJECTPROPS, n_value) = ([ppropertyslot])',
    'ppropertyslot.DECL =/= eps',
    'ppropertyslot.STATE = PROP_VALUE (DIRECT (POBJECT n_child))',
    '$object_name(S, n_child) = $ptascii("GC37ChildPre")',
    '$node_children(S, HOBJECT n_value) = [HOBJECT n_child]',
    '$node_children(S, HOBJECT n_child) = eps',
    'H = $heap_graph(S)',
    '$heap_valid(H)',
    '$heap_owners(H, HOBJECT n_child) = 1',
    '$weakmap_write_value_allowed(S, paccess)',
    '$weakmap_write_allowed(S, paccess)',
    '~$weakmap_declared_value_child(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_child)], n_value)',
    '~$weakmap_declared_value_child(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS, n_value, eps)], n_value)',
    '~$weakmap_write_value_allowed(S, paccess[.OBJECT = (n_key)])',
    'PhpStep: S ~> S_inserted',
    'S_inserted.OBJECTS[n_map] = WEAKMAP (pweakmapentry)',
    'pweakmapentry.KEY = n_key /\\ pweakmapentry.VALUE = POBJECT n_value',
    '~$weakmap_write_value_allowed(S_inserted, paccess)',
    '$node_children(S_inserted, HOBJECT n_map) = [HOBJECT n_value]',
    '$node_children(S_inserted, HOBJECT n_value) = [HOBJECT n_child]',
    '$heap_valid($heap_graph(S_inserted))',
    'S_zero = $drive_steps(S, 0)',
    'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = $drive_steps(S, 1)',
    'S_done = $drive_steps(S, 4000)',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
    'S_done.OBJECTS[n_map] = WEAKMAP eps',
    '~((HOBJECT n_key) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_value) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {'first-insertion-declared-child': {'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=240) else 1)
