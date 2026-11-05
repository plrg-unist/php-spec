#!/usr/bin/env python3
"""Reached unlink orders the removed Value before the real selected-Key owner."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc47_unset_selected_key_throw.php').read_text()
STAGE = (
    'S.TODO = UNSET_ARRAY :: ptask_tail* '
    '-- if S.BASE = BASE_DIM (BASE_VALUE poperand_base) poperand_key z '
    '-- if S_base = $quiet_operand(S, poperand_base) '
    '-- if S_base.RESULT = KNOWN (POBJECT n_map) '
    '-- if S.OBJECTS[n_map] = WEAKMAPENTRIES ([pweakmapentry_value, pweakmapentry_left, pweakmapentry_right]) '
    '-- if pweakmapentry_value.VALUE = POBJECT n_value '
    '-- if $object_name(S, n_value) = $ptascii("GC47Value")')
CHECKS = [
    'S.ORIGIN = (porigin)',
    'S_key = $quiet_operand(S, poperand_key)',
    'S_key.RESULT = KNOWN (POBJECT n_key)',
    'n_key = pweakmapentry_value.KEY',
    '$lookup(S.ENV, $ptascii("key")) = (n_key_cell)',
    'S.STORE[n_key_cell] = DEFINED PNULL',
    '$operand_nodes(poperand_key) = [HOBJECT n_key]',
    '$operand_nodes(poperand_base) = eps',
    '$operand_nodes(S.RESULT) = eps',
    '$base_nodes(S.BASE) = [HOBJECT n_key]',
    'pweakmapentry_left.VALUE = POBJECT n_left',
    'pweakmapentry_right.VALUE = POBJECT n_right',
    '$objectprops_at(S.OBJECTPROPS, n_value) = ([ppropertyslot_a, ppropertyslot_b, ppropertyslot_c])',
    'ppropertyslot_a.STATE = PROP_VALUE (DIRECT (POBJECT n_x))',
    'ppropertyslot_b.STATE = PROP_VALUE (DIRECT (POBJECT n_y))',
    'ppropertyslot_c.STATE = ppropertyslot_a.STATE',
    '$lookup(S.ENV, $ptascii("mapWatch")) = (n_map_watch_cell)',
    'S.STORE[n_map_watch_cell] = DEFINED (POBJECT n_map_watch)',
    '$lookup(S.ENV, $ptascii("valueWatch")) = (n_value_watch_cell)',
    'S.STORE[n_value_watch_cell] = DEFINED (POBJECT n_value_watch)',
    '$lookup(S.ENV, $ptascii("keyWatch")) = (n_key_watch_cell)',
    'S.STORE[n_key_watch_cell] = DEFINED (POBJECT n_key_watch)',
    'H = $heap_graph(S)',
    '$heap_valid(H)',
    '$heap_owners(H, HOBJECT n_key) = 1',
    '$heap_owners(H, HOBJECT n_value) = 1',
    '$heap_owners(H, HOBJECT n_x) = 2',
    '$heap_owners(H, HOBJECT n_y) = 1',
    '$weakmap_entries_child_storage(S, n_map)',
    '~$weakmap_entries_access_storage(S, n_map, false)',
    'paccess_initial = $access_record(S, porigin, z, ACCESS_UNSET, BASE_VALUE poperand_base, poperand_key, KNOWN PNULL, UNSET_ARRAY, eps, false)',
    'paccess = paccess_initial[.SELECTED = $rcontainer_selected(S, poperand_base)][.OFFSET = POBJECT n_key][.OBJECT = (n_map)]',
    '$weakmap_unset_allowed(S, paccess)',
    '$weakmap_entries_access_allowed(S, paccess, $ptascii("offsetUnset"))',
    '~$weakmap_entries_access_allowed(S, paccess, $ptascii("offsetGet"))',
    '~$weakmap_entries_access_allowed(S, paccess, $ptascii("offsetExists"))',
    '~$weakmap_entries_access_allowed(S, paccess[.SELECTED = KNOWN PNULL], $ptascii("offsetUnset"))',
    'S_missing = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_y)]',
    '~$weakmap_entries_access_allowed(S_missing, paccess, $ptascii("offsetUnset"))',
    'S_cursor = S[.ITERATORS = [OBJECTITER 0 n_map 0 false]]',
    '~$weakmap_entries_access_allowed(S_cursor, paccess, $ptascii("offsetUnset"))',
    'S_zero = $drive_steps(S, 0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_paused = $drive_steps(S, 1)',
    'S_paused.COMPLETION = BUDGET',
    'S_jobs = S_paused[.COMPLETION = NORMAL]',
    'S_jobs.OBJECTS[n_map] = WEAKMAPENTRIES ([pweakmapentry_left, pweakmapentry_right])',
    '$weakmap_entries_find($weakmap_entries_contents(S_jobs, n_map), n_key) = eps',
    '$weakmap_key_maps(S_jobs, S_jobs.ALLOCATIONS, n_key) = eps',
    '$weakmap_key_maps(S_jobs, S_jobs.ALLOCATIONS, pweakmapentry_left.KEY) = [n_map]',
    '$weakmap_key_maps(S_jobs, S_jobs.ALLOCATIONS, pweakmapentry_right.KEY) = [n_map]',
    'S_jobs.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_after*',
    'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_value), pdestructionjob_key]',
    '$destruction_plain_job(pdestructionjob_key)',
    '$destruction_job_node(pdestructionjob_key) = (HOBJECT n_key)',
    '$destructor_release_valid(S_jobs, pdestructionrelease)',
    'pdestructionoperation.SOURCE = UNSET_ARRAY',
    '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
    '$task_nodes(DESTRUCTOR_RELEASE pdestructionrelease) = [HOBJECT n_value, HOBJECT n_key]',
    '$heap_owners($heap_graph(S_jobs), HOBJECT n_key) = 1',
    '$heap_owners($heap_graph(S_jobs), HOBJECT n_value) = 1',
    '$heap_owners($heap_graph(S_jobs), HOBJECT n_x) = 2',
    '$heap_owners($heap_graph(S_jobs), HOBJECT n_y) = 1',
    '$weakref_get(S_jobs, n_key_watch) = POBJECT n_key',
    '$weakref_get(S_jobs, n_map_watch) = POBJECT n_map',
    '$weakref_get(S_jobs, n_value_watch) = POBJECT n_value',
    'S_jobs.EVENTS = S.EVENTS',
    '$heap_valid($heap_graph(S_jobs)) /\\ $destruction_state_valid(S_jobs)',
    'S_pin_budget = $drive_steps(S_jobs, 1)',
    'S_pin_budget.COMPLETION = BUDGET',
    'S_pin = S_pin_budget[.COMPLETION = NORMAL]',
    '$instance_storage_for(S_pin, n_value) = (pinstancestorage)',
    'pinstancestorage.NEXT = 0',
    'pinstancestorage.SLOTS = [ppropertyslot_a, ppropertyslot_b, ppropertyslot_c]',
    '$instance_storage_valid(S_pin, pinstancestorage)',
    '$task_nodes(INSTANCE_STORAGE_STEP pinstancestorage) = [HOBJECT n_value]',
    '$weakref_get(S_pin, n_value_watch) = PNULL',
    '$weakref_get(S_pin, n_key_watch) = POBJECT n_key',
    '$weakref_get(S_pin, n_map_watch) = POBJECT n_map',
    '$heap_owners($heap_graph(S_pin), HOBJECT n_key) = 1',
    '$heap_owners($heap_graph(S_pin), HOBJECT n_value) = 1',
    '$heap_owners($heap_graph(S_pin), HOBJECT n_x) = 2',
    '$heap_owners($heap_graph(S_pin), HOBJECT n_y) = 1',
    '~$instance_storage_freeing(S_pin, n_key)',
    '~$instance_storage_freeing(S_pin, n_map)',
    '$heap_valid($heap_graph(S_pin)) /\\ $destruction_state_valid(S_pin)',
    'S_done = $drive_steps(S, 4000)',
    '$drive_steps(S_jobs, 4000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    '$weakref_get(S_done, n_key_watch) = PNULL',
    '$weakref_get(S_done, n_value_watch) = PNULL',
    '$weakref_get(S_done, n_map_watch) = PNULL',
    '~((HOBJECT n_key) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_value) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_x) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_y) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {'finite-value-unset-selected-key': {'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=360) else 1)
