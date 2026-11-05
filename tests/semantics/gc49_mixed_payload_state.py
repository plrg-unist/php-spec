#!/usr/bin/env python3
"""Reached scalar replacement owns one new Value edge; old domains stay disjoint."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc49_scalar_to_finite_mixed_free.php').read_text()
STAGE = (
    'S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail* '
    '-- if $lookup(S.ENV, $ptascii("map")) = (n_map_cell) '
    '-- if S.STORE[n_map_cell] = DEFINED (POBJECT n_map) '
    '-- if S.OBJECTS[n_map] = WEAKMAP (pweakmapentry) '
    '-- if $weakmap_scalar_value(S, pweakmapentry.VALUE) '
    '-- if $access_set_plan(S) = (paccess_plan) '
    '-- if paccess_plan.OBJECT = (n_map) '
    '-- if $lookup(S.ENV, $ptascii("incoming")) = (n_value_cell) '
    '-- if S.STORE[n_value_cell] = DEFINED (POBJECT n_value) '
    '-- if $object_name(S, n_value) = $ptascii("GC49Value")')
CHECKS = [
    'S_value = $quiet_operand(S, paccess_plan.RHS)',
    'S_value.RESULT = KNOWN (POBJECT n_value)',
    'S_key = $quiet_operand(S, paccess_plan.INPUT)',
    'S_key.RESULT = KNOWN (POBJECT n_key)',
    'n_key = pweakmapentry.KEY',
    'pweakmapentry.VALUE = PSTRING $ptascii("seed-49")',
    '$weakmap_value_nodes(pweakmapentry.VALUE) = eps',
    'paccess = paccess_plan[.SELECTED = $rcontainer_selected(S, paccess_plan.RHS)][.VALUE = POBJECT n_value][.OFFSET = POBJECT n_key]',
    'paccess.RHS = S.RESULT',
    'S.RESULT = VARIABLE ptbytes_rhs z_rhs',
    'ptbytes_rhs = $ptascii("incoming")',
    '$operand_nodes(paccess.RHS) = eps',
    '~(n_value_cell <- S.REFCELLS)',
    '$objectprops_at(S.OBJECTPROPS, n_value) = ([ppropertyslot])',
    'ppropertyslot.STATE = PROP_VALUE (DIRECT (POBJECT n_child))',
    '$node_children(S, HOBJECT n_value) = [HOBJECT n_child]',
    'H = $heap_graph(S)',
    '$heap_valid(H)',
    '$heap_owners(H, HOBJECT n_map) = 1',
    '$heap_owners(H, HOBJECT n_key) = 1',
    '$heap_owners(H, HOBJECT n_value) = 2',
    '$heap_owners(H, HOBJECT n_child) = 2',
    '$weakmap_entries_child_value_free(S, pweakmapentry.VALUE)',
    '$weakmap_entries_child_value_free(S, POBJECT n_value)',
    '~$weakmap_entries_child_value_free(S, PFLOAT 4607182418800017408)',
    '~$weakmap_entries_child_value_free(S, ALIAS n_value_cell)',
    '$weakmap_entries_child_storage(S, n_map)',
    '~$weakmap_entries_teardown_table(S, n_map)',
    '~$weakmap_replace_allowed(S, paccess)',
    '$weakmap_entries_write_allowed(S, paccess)',
    'S_scalar = S[.STORE[n_value_cell] = DEFINED PNULL]',
    'paccess_scalar = paccess[.VALUE = PNULL]',
    '$heap_valid($heap_graph(S_scalar))',
    '$weakmap_replace_allowed(S_scalar, paccess_scalar)',
    '~$weakmap_entries_write_allowed(S_scalar, paccess_scalar)',
    '$weakmap_map_free_slot_allowed(S_scalar, n_map, PNULL)',
    '$lookup(S.ENV, $ptascii("otherKey")) = (n_other_cell)',
    'S.STORE[n_other_cell] = DEFINED (POBJECT n_other_key)',
    'n_other_key =/= n_key',
    'pweakmapentry_scalar = {KEY n_other_key, VALUE PBOOL false, BEFORE eps, ORDER 1}',
    'S_many_scalar = S_scalar[.OBJECTS[n_map] = WEAKMAPENTRIES ([pweakmapentry, pweakmapentry_scalar])]',
    '$heap_valid($heap_graph(S_many_scalar))',
    '~$weakmap_entries_teardown_table(S_many_scalar, n_map)',
    '~$weakmap_entries_access_storage(S_many_scalar, n_map, false)',
    '$weakmap_entries_child_storage(S_many_scalar, n_map)',
    '$weakmap_entries_write_allowed(S_many_scalar, paccess_scalar)',
    '~$weakmap_entries_notice_storage(S_many_scalar, n_map, eps, false)',
    'S_leaf = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS, n_value, [ppropertyslot[.STATE = PROP_VALUE (DIRECT PNULL)]])]',
    'pweakmapentry_leaf = pweakmapentry[.VALUE = POBJECT n_value]',
    'S_many_leaf = S_leaf[.OBJECTS[n_map] = WEAKMAPENTRIES ([pweakmapentry_leaf, pweakmapentry_scalar[.VALUE = POBJECT n_value]])]',
    '$heap_valid($heap_graph(S_many_leaf))',
    '$heap_owners($heap_graph(S_many_leaf), HOBJECT n_child) = 1',
    '$weakmap_entries_teardown_table(S_many_leaf, n_map)',
    '$weakmap_entries_child_table_free(S_many_leaf, n_map)',
    '$weakmap_entries_access_storage(S_many_leaf, n_map, false)',
    '$weakmap_entries_storage_valid(S_many_leaf, n_map, eps)',
    '$weakmap_entries_notice_storage(S_many_leaf, n_map, eps, false)',
    '$weakmap_entries_write_allowed(S_many_leaf, paccess)',
    'S_zero = $drive_steps(S, 0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_paused = $drive_steps(S, 1)',
    'S_paused.COMPLETION = BUDGET',
    'S_written = S_paused[.COMPLETION = NORMAL]',
    'S_written.TODO = (ACCESS_RESUME paccess_called) :: ptask_tail*',
    'paccess_called = paccess[.PHASE = ACCESS_CALL $ptascii("offsetSet")]',
    '$weakmap_set_resume(S_written, paccess_called)',
    'S_written.OBJECTS[n_map] = WEAKMAP (pweakmapentry[.VALUE = POBJECT n_value])',
    '$weakmap_key_maps(S_written, S_written.ALLOCATIONS, n_key) = [n_map]',
    '$node_children(S_written, HOBJECT n_value) = [HOBJECT n_child]',
    '$heap_owners($heap_graph(S_written), HOBJECT n_map) = 2',
    '$heap_owners($heap_graph(S_written), HOBJECT n_key) = 1',
    '$heap_owners($heap_graph(S_written), HOBJECT n_value) = 3',
    '$heap_owners($heap_graph(S_written), HOBJECT n_child) = 2',
    '$task_nodes(ACCESS_RESUME paccess_called) = [HOBJECT n_map]',
    'S_written.RESULT = KNOWN PNULL',
    'S_written.EVENTS = S.EVENTS',
    '$heap_valid($heap_graph(S_written))',
    'S_done = $drive_steps(S, 4000)',
    '$drive_steps(S_written, 4000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    '~((HOBJECT n_map) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_value) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {'mixed-payload-owner-and-defaults': {'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=300) else 1)
