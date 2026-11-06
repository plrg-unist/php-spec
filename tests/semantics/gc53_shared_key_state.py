#!/usr/bin/env python3
"""Real shared-Key jobs preserve owners and both live/delivered wrapper phases."""
import argparse
import json
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc53_shared_object_key_death.php').read_text()
SOURCE_EARLY = (ROOT / 'tests/semantics/gc53_shared_object_key_death_early.php').read_text()
STAGE = (
    'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail* '
    '-- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_key)) :: pdestructionjob_tail* '
    '-- if $lookup(S.ENV, $ptascii("left")) = (n_left_cell) '
    '-- if S.STORE[n_left_cell] = DEFINED (POBJECT n_left) '
    '-- if $lookup(S.ENV, $ptascii("right")) = (n_right_cell) '
    '-- if S.STORE[n_right_cell] = DEFINED (POBJECT n_right) '
    '-- if S.OBJECTS[n_left] = WEAKMAPENTRIES ([pweakmapentry_left, pweakmapentry_scalar]) '
    '-- if S.OBJECTS[n_right] = WEAKMAP (pweakmapentry_right) '
    '-- if pweakmapentry_left.KEY = n_key '
    '-- if pweakmapentry_left.VALUE = POBJECT n_value '
    '-- if $heap_owners($heap_graph(S), HOBJECT n_key) = 1')
CHUNKS = (['B|', 'S|', '1', '|', '1', '|', 'C|'] + ['1', '|'] * 5
          + ['T|', '1', '|', 'makeSharedObjectFailure53', '|', '0', '|']
          + ['1', '|'] * 4 + ['A|'] + ['1', '|'] * 2)
ENDING = 'S_done.EVENTS = [' + ', '.join(
    'OUTPUT $ptascii(' + json.dumps(chunk) + ')' for chunk in CHUNKS) + ']'
CHECKS = [
    'S.CURRENT = eps /\\ S.FRAMES = eps',
    'pdestructionjob_tail* = eps',
    '$destructor_release_valid(S, pdestructionrelease)',
    'pweakmapentry_right.KEY = n_key /\\ pweakmapentry_right.VALUE = POBJECT n_value',
    'pweakmapentry_scalar.VALUE = PINT 0',
    '$objectprops_at(S.OBJECTPROPS, n_value) = ([ppropertyslot])',
    'ppropertyslot.STATE = PROP_VALUE (DIRECT (POBJECT n_child))',
    '$lookup(S.ENV, $ptascii("keyWatch")) = (n_watch_cell)',
    'S.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
    'pweakmapentry_left.BEFORE = eps /\\ pweakmapentry_right.BEFORE = eps',
    '$(pweakmapentry_left.ORDER < pweakmapentry_right.ORDER)',
    '$weakmap_notice_first(S, n_key, [n_right, n_left]) = (n_left)',
    '$weakmap_key_maps(S, S.ALLOCATIONS, n_key) = [n_left, n_right]',
    '$weakmap_shared_key_order_safe(S, n_key)',
    '~$weakmap_entries_child_private_storage(S, n_left, eps)',
    '$weakmap_entries_child_shared_storage(S, n_left, eps)',
    '$weakmap_entries_child_storage(S, n_right)',
    '$node_children(S, HOBJECT n_left) = [HOBJECT n_value]',
    '$node_children(S, HOBJECT n_right) = [HOBJECT n_value]',
    '$node_children(S, HOBJECT n_value) = [HOBJECT n_child]',
    '$heap_owners($heap_graph(S), HOBJECT n_value) = 2',
    '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_watch) = 1',
    '$heap_valid($heap_graph(S)) /\\ $destruction_state_valid(S)',
    # Constructed association/rank/cursor and old-domain selectors.
    'S_bad_value = S[.OBJECTS[n_right] = WEAKMAP (pweakmapentry_right[.VALUE = POBJECT n_child])]',
    '$heap_valid($heap_graph(S_bad_value))',
    '~$weakmap_entries_child_storage(S_bad_value, n_left)',
    'S_duplicate_rank = S[.OBJECTS[n_right] = WEAKMAP (pweakmapentry_right[.ORDER = pweakmapentry_left.ORDER])]',
    '~$weakmap_shared_key_order_safe(S_duplicate_rank, n_key)',
    'S_bad_prefix = S[.OBJECTS[n_left] = WEAKMAPENTRIES ([pweakmapentry_left[.BEFORE = (n_watch)], pweakmapentry_scalar])]',
    '~$weakmap_shared_key_order_safe(S_bad_prefix, n_key)',
    'S_cursor = S[.ITERATORS = [OBJECTITER 0 n_right 0 false]]',
    '~$weakmap_entries_child_storage(S_cursor, n_left)',
    'S_registration = S[.OBJECTS[n_right] = WEAKMAP eps]',
    '~$weakmap_shared_leaf_registration(S_registration, n_right, n_key, POBJECT n_value)',
    '$weakmap_shared_finite_registration(S_registration, n_right, n_key, POBJECT n_value)',
    '~$weakmap_shared_finite_registration(S_registration, n_right, n_left, POBJECT n_value)',
    'S_leaf = S_registration[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS, n_value, [ppropertyslot[.STATE = PROP_VALUE (DIRECT PNULL)]])][.OBJECTS[n_left] = WEAKMAPENTRIES ([pweakmapentry_left, pweakmapentry_scalar[.VALUE = POBJECT n_value]])]',
    '$heap_valid($heap_graph(S_leaf))',
    '$weakmap_shared_leaf_registration(S_leaf, n_right, n_key, POBJECT n_value)',
    '~$weakmap_shared_finite_registration(S_leaf, n_right, n_key, POBJECT n_value)',
    '$weakmap_shared_registration(S_leaf, n_right, n_key, POBJECT n_value)',
    # Actual Key free atomically starts its first selected Map notification.
    'S_zero = $drive_steps(S, 0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_started = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
    'S_started.OBJECTS[n_left] = WEAKMAP (pweakmapentry_scalar)',
    'S_started.OBJECTS[n_right] = S.OBJECTS[n_right]',
    '$weakmap_key_maps(S_started, S_started.ALLOCATIONS, n_key) = [n_right]',
    'S_started.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_value) :: (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_after_pin*',
    'pdestructionrelease_value.JOBS = [DESTRUCTION_VALUE (HOBJECT n_value)]',
    'pinstancestorage.OBJECT = n_key /\\ pinstancestorage.NEXT = 0 /\\ pinstancestorage.SLOTS = eps /\\ pinstancestorage.NOTIFY = (n_watch)',
    '$task_nodes(INSTANCE_STORAGE_STEP pinstancestorage) = [HOBJECT n_key]',
    '$instance_storage_valid(S_started, pinstancestorage)',
    '$weakmap_storage_read(S_started, n_watch, n_key)',
    '$weakref_get(S_started, n_watch) = POBJECT n_key',
    '$heap_owners($heap_graph(S_started), HOBJECT n_key) = 1',
    '$heap_owners($heap_graph(S_started), HOBJECT n_value) = 2',
    '$heap_owners($heap_graph(S_started), HOBJECT n_child) = 1',
    '$heap_owners($heap_graph(S_started), HOBJECT n_watch) = 1',
    '~$weakmap_shared_wrapper_ready(S_started, pinstancestorage)',
    'S_shared = $drive_steps(S_started, 1)[.COMPLETION = NORMAL]',
    '$heap_owners($heap_graph(S_shared), HOBJECT n_value) = 1',
    '$heap_owners($heap_graph(S_shared), HOBJECT n_child) = 1',
    '~$instance_storage_freeing(S_shared, n_value)',
    'S_shared.EVENTS = S.EVENTS',
    'S_front = $drive_steps(S_shared, 1)[.COMPLETION = NORMAL]',
    'S_front.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_after_pin*',
    '$weakmap_shared_wrapper_ready(S_front, pinstancestorage)',
    '$weakmap_storage_read(S_front, n_watch, n_key)',
    # A delivered EPS cannot be rearmed on the same pre-WR remaining record.
    'S_wrong_phase = S_front[.TODO = (INSTANCE_STORAGE_STEP pinstancestorage[.NOTIFY = eps]) :: ptask_after_pin*]',
    '~$weakmap_key_continue_leaf(S_wrong_phase, n_key)',
    '~$weakmap_key_continue_finite(S_wrong_phase, n_key)',
    'S_last = $drive_steps(S_front, 1)[.COMPLETION = NORMAL]',
    'S_last.OBJECTS[n_right] = WEAKMAP eps',
    '$weakmap_key_maps(S_last, S_last.ALLOCATIONS, n_key) = eps',
    'S_last.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_last) :: (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_after_pin*',
    'pdestructionrelease_last.JOBS = [DESTRUCTION_VALUE (HOBJECT n_value)]',
    '$heap_owners($heap_graph(S_last), HOBJECT n_value) = 1',
    '$heap_owners($heap_graph(S_last), HOBJECT n_child) = 1',
    '$heap_owners($heap_graph(S_last), HOBJECT n_watch) = 1',
    '$weakmap_storage_read(S_last, n_watch, n_key)',
    '$heap_valid($heap_graph(S_last)) /\\ $destruction_state_valid(S_last)',
    'S_last.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S, 4000)',
    '$drive_steps(S_last, 4000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    ENDING,
    '~((HOBJECT n_key) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_value) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_left) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_right) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
STAGE_EARLY = (
    'S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_tail* '
    '-- if pinstancestorage.NOTIFY = eps '
    '-- if n_key = pinstancestorage.OBJECT '
    '-- if $lookup(S.ENV, $ptascii("right")) = (n_right_cell) '
    '-- if S.STORE[n_right_cell] = DEFINED (POBJECT n_right) '
    '-- if S.OBJECTS[n_right] = WEAKMAP (pweakmapentry_right) '
    '-- if pweakmapentry_right.KEY = n_key '
    '-- if pweakmapentry_right.VALUE = POBJECT n_value '
    '-- if $weakmap_key_maps(S, S.ALLOCATIONS, n_key) = [n_right]')
CHECKS_EARLY = [
    'S.CURRENT = eps /\\ S.FRAMES = eps',
    '$instance_storage_valid(S, pinstancestorage)',
    'pinstancestorage.NEXT = 0 /\\ pinstancestorage.SLOTS = eps',
    '$lookup(S.ENV, $ptascii("left")) = (n_left_cell)',
    'S.STORE[n_left_cell] = DEFINED (POBJECT n_left)',
    'S.OBJECTS[n_left] = WEAKMAP (pweakmapentry_scalar)',
    'pweakmapentry_scalar.VALUE = PINT 0',
    '$objectprops_at(S.OBJECTPROPS, n_value) = ([ppropertyslot])',
    'ppropertyslot.STATE = PROP_VALUE (DIRECT (POBJECT n_child))',
    '$lookup(S.ENV, $ptascii("keyWatch")) = (n_watch_cell)',
    'S.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
    'pweakmapentry_right.BEFORE = (n_watch)',
    '$weakref_find(S, S.ALLOCATIONS, n_key) = (n_watch)',
    '$weakref_get(S, n_watch) = PNULL',
    '~$weakmap_storage_read(S, n_watch, n_key)',
    '~$weakmap_key_continue_leaf(S, n_key)',
    '$weakmap_key_continue_finite(S, n_key)',
    '$weakmap_entries_child_storage_policy(S, n_right, (n_key))',
    '$heap_owners($heap_graph(S), HOBJECT n_key) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_value) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
    '$heap_valid($heap_graph(S))',
    'S_next = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
    'S_next.OBJECTS[n_right] = WEAKMAP eps',
    '$weakmap_key_maps(S_next, S_next.ALLOCATIONS, n_key) = eps',
    'S_next.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_tail*',
    'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_value)]',
    '$task_nodes(INSTANCE_STORAGE_STEP pinstancestorage) = [HOBJECT n_key]',
    '$heap_owners($heap_graph(S_next), HOBJECT n_value) = 1',
    '$heap_owners($heap_graph(S_next), HOBJECT n_child) = 1',
    '$weakref_get(S_next, n_watch) = PNULL',
    '~$weakmap_storage_read(S_next, n_watch, n_key)',
    'S_next.EVENTS = S.EVENTS',
    '$heap_valid($heap_graph(S_next)) /\\ $destruction_state_valid(S_next)',
    'S_done = $drive_steps(S_next, 4000)',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    ENDING,
    '~((HOBJECT n_key) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_value) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {
    'shared-value-live-wrapper': {'source': SOURCE, 'stage': STAGE, 'checks': CHECKS},
    'shared-value-delivered-wrapper': {'source': SOURCE_EARLY, 'stage': STAGE_EARLY, 'checks': CHECKS_EARLY},
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=360) else 1)
