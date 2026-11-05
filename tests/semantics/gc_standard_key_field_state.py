#!/usr/bin/env python3
"""Reached standard Key pin preserves its field across weak notification."""
import argparse

import fiber_state_review as review
import gc_standard_key_field_sources as sources


STAGE = (
    'S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_tail* '
    '-- if n_key = pinstancestorage.OBJECT '
    '-- if pinstancestorage.NOTIFY = (n_watch) '
    '-- if pinstancestorage.SLOTS = [ppropertyslot] '
    '-- if ppropertyslot.STATE = PROP_VALUE (DIRECT (POBJECT n_child)) '
    '-- if S.OBJECTS[n_key] = STDINSTANCE '
    '-- if S.OBJECTS[n_watch] = WEAKREFERENCE (n_key)')
CHECKS = [
    'S_global = $global_table_view(S)',
    '$lookup(S_global.ENV, $ptascii("gc36Watch")) = (n_watch_cell)',
    'S.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
    '$lookup(S_global.ENV, $ptascii("map")) = (n_map_cell)',
    'S.STORE[n_map_cell] = DEFINED (POBJECT n_map)',
    'S.OBJECTS[n_map] = WEAKMAP eps',
    'pinstancestorage.NEXT = 0',
    'ppropertyslot.DECL = eps',
    '$objectprops_at(S.OBJECTPROPS, n_key) = ([ppropertyslot])',
    '$object_table_at(S.OBJECTTABLES, n_key) = eps',
    '$node_children(S, HOBJECT n_key) = [HOBJECT n_child]',
    '$node_children(S, HOBJECT n_child) = eps',
    '$weakmap_standard_key_child(S, n_key)',
    '$instance_storage_valid(S, pinstancestorage)',
    '$weakmap_storage_notice_valid(S, pinstancestorage)',
    '$weakmap_storage_read(S, n_watch, n_key)',
    '$weakref_get(S, n_watch) = POBJECT n_key',
    'H = $heap_graph(S)', '$heap_valid(H)',
    '$heap_owners(H, HOBJECT n_key) = 1',
    '$heap_owners(H, HOBJECT n_child) = 1',
    '~$instance_storage_basic(S, pinstancestorage[.SLOTS = eps])',
    '~$weakmap_storage_notice_valid(S, pinstancestorage[.NEXT = 1])',
    'S_missing = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_child)]',
    '~$weakmap_standard_key_child(S_missing, n_key)',
    '~$weakmap_insert_key(S, n_key)',
    'PhpStep: S ~> S_notified',
    'S_notified.TODO = (INSTANCE_STORAGE_STEP pinstancestorage[.NOTIFY = eps]) :: ptask_tail*',
    'S_notified.OBJECTPROPS = S.OBJECTPROPS',
    '$weakref_get(S_notified, n_watch) = PNULL',
    '$heap_owners($heap_graph(S_notified), HOBJECT n_child) = 1',
    'PhpStep: S_notified ~> S_transferred',
    '$node_children(S_transferred, HOBJECT n_key) = eps',
    '$heap_owners($heap_graph(S_transferred), HOBJECT n_child) = 1',
    '$instance_storage_for(S_transferred, n_key) = (pinstancestorage_after)',
    'pinstancestorage_after.NEXT = 1 /\\ pinstancestorage_after.NOTIFY = eps',
    '$instance_storage_basic(S_transferred, pinstancestorage_after)',
    'S_zero = $drive_steps(S, 0)',
    'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = $drive_steps(S, 1)',
    'S_done = $drive_steps(S, 4000)',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
    'S_done.OBJECTS[n_map] = WEAKMAP eps',
    '~((HOBJECT n_key) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {
    name: {'source': path.read_text(), 'stage': STAGE, 'checks': CHECKS}
    for name, path in sources.PATHS.items() if name != 'two-fields-unsupported'
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=240) else 1)
