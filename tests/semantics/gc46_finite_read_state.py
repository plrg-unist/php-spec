#!/usr/bin/env python3
"""Reached fetched ownership and constructed finite-read protocol counterstates."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = (ROOT / 'tests/semantics/gc46_direct_fetched_retained.php').read_text()
# One held spare Key keeps the absent-input counterstate canonical and finite.
SOURCE = ORIGINAL.replace('$otherKey = new stdClass;',
                          '$otherKey = new stdClass;\n$spareKey = new stdClass;')
STAGE = (
    'S.TODO = (KEY_READ_DIM poperand_key z KEY_R) :: ptask_tail* '
    '-- if S_base = $quiet_operand(S, S.RESULT) '
    '-- if S_base.RESULT = KNOWN (POBJECT n_map) '
    '-- if S.OBJECTS[n_map] = WEAKMAPENTRIES ([pweakmapentry_value, pweakmapentry_leaf]) '
    '-- if pweakmapentry_value.VALUE = POBJECT n_value '
    '-- if $object_name(S, n_value) = $ptascii("GC46Value")')
CHECKS = [
    'S.ORIGIN = (porigin)',
    'S_key = $quiet_operand(S, poperand_key)',
    'S_key.RESULT = KNOWN (POBJECT n_key)',
    'n_key = pweakmapentry_value.KEY',
    'pweakmapentry_leaf.VALUE = POBJECT n_leaf',
    '$objectprops_at(S.OBJECTPROPS, n_value) = ([ppropertyslot_a, ppropertyslot_b, ppropertyslot_c])',
    'ppropertyslot_a.STATE = PROP_VALUE (DIRECT (POBJECT n_x))',
    'ppropertyslot_b.STATE = PROP_VALUE (DIRECT (POBJECT n_y))',
    'ppropertyslot_c.STATE = ppropertyslot_a.STATE',
    'H = $heap_graph(S)',
    '$heap_valid(H)',
    '$heap_owners(H, HOBJECT n_value) = 1',
    '$heap_owners(H, HOBJECT n_x) = 2',
    '$heap_owners(H, HOBJECT n_y) = 1',
    'S.EVENTS = [OUTPUT $ptascii("B|"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), OUTPUT $ptascii("0"), OUTPUT $ptascii("|")]',
    'paccess_initial = $access_record(S, porigin, z, ACCESS_READ KEY_R, BASE_VALUE S.RESULT, poperand_key, KNOWN PNULL, KEY_READ_DIM poperand_key z KEY_R, (n_map), true)',
    'paccess = paccess_initial[.SELECTED = $rcontainer_selected(S, S.RESULT)][.OFFSET = POBJECT n_key]',
    '$weakmap_read_allowed(S, paccess)',
    '~$weakmap_entries_access_storage(S, n_map, false)',
    '$weakmap_entries_child_storage(S, n_map)',
    '$weakmap_entries_access_allowed(S, paccess, $ptascii("offsetGet"))',
    '~$weakmap_entries_access_allowed(S, paccess, $ptascii("offsetUnset"))',
    '~$weakmap_entries_access_allowed(S, paccess[.OBJECT = eps], $ptascii("offsetGet"))',
    'S_missing_child = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_y)]',
    '~$weakmap_entries_access_allowed(S_missing_child, paccess, $ptascii("offsetGet"))',
    '$lookup(S.ENV, $ptascii("spareKey")) = (n_spare_cell)',
    'S.STORE[n_spare_cell] = DEFINED (POBJECT n_spare)',
    'n_spare =/= n_key /\\ n_spare =/= pweakmapentry_leaf.KEY',
    'S_absent = S[.OBJECTS[n_map] = WEAKMAPENTRIES ([pweakmapentry_value[.KEY = n_spare][.BEFORE = eps], pweakmapentry_leaf])]',
    '$weakmap_entries_find($weakmap_entries_contents(S_absent, n_map), n_key) = eps',
    '$weakmap_entries_child_storage(S_absent, n_map)',
    '$weakmap_entries_access_allowed(S_absent, paccess, $ptascii("offsetGet"))',
    '$lookup(S.ENV, $ptascii("keyWatch")) = (n_watch_cell)',
    'S.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
    'pinstancestorage = {OBJECT n_key, HANDLE S.DESTRUCTION.HANDLES[n_key], SLOTS eps, NEXT 0, NOTIFY (n_watch), CALLER S.CURRENT, ORIGIN S.ORIGIN, CONSTCONTEXT S.CONSTCONTEXT, USER $destructor_user_source(S)}',
    'S_active = $instance_storage_called(S_absent[.TODO = (KEY_READ_DIM poperand_key z KEY_R) :: (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_tail*], n_key)',
    '$instance_storage_basic(S_active, pinstancestorage)',
    '$instance_storage_state_valid(S_active)',
    '$weakmap_storage_read(S_active, n_watch, n_key)',
    '$weakmap_read_allowed(S_active, paccess)',
    '$weakmap_entries_child_storage(S_active, n_map)',
    '~$weakmap_entries_access_allowed(S_active, paccess, $ptascii("offsetGet"))',
    'PhpStep: S ~> S_read',
    'S_read.RESULT = KNOWN (POBJECT n_value)',
    'S_read.OBJECTS[n_map] = S.OBJECTS[n_map]',
    '$heap_owners($heap_graph(S_read), HOBJECT n_value) = 2',
    '$heap_owners($heap_graph(S_read), HOBJECT n_x) = 2',
    '$heap_owners($heap_graph(S_read), HOBJECT n_y) = 1',
    'S_read.EVENTS = S.EVENTS',
    '$heap_valid($heap_graph(S_read))',
    'S_zero = $drive_steps(S, 0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_paused = $drive_steps(S, 1)',
    'S_paused.COMPLETION = BUDGET /\\ S_paused.TODO = S_read.TODO',
    'S_paused.RESULT = KNOWN (POBJECT n_value)',
    '$heap_owners($heap_graph(S_paused), HOBJECT n_value) = 2',
    '$heap_owners($heap_graph(S_paused), HOBJECT n_x) = 2',
    '$heap_owners($heap_graph(S_paused), HOBJECT n_y) = 1',
    '$heap_valid($heap_graph(S_paused))',
    'S_done = $drive_steps(S, 4000)',
    '$drive_steps(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    '~((HOBJECT n_value) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_x) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_y) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_leaf) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_map) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {'finite-value-read-owner': {'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=300) else 1)
