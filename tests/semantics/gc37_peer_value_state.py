#!/usr/bin/env python3
"""Reached owner transfer when an ordinary WeakMap Value releases its child."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc37_peer_value_preinsert.php').read_text()
STAGE = (
    'S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_tail* '
    '-- if n_value = pinstancestorage.OBJECT '
    '-- if $object_name(S, n_value) = $ptascii("GC37PeerPreValue") '
    '-- if pinstancestorage.NEXT = 0 '
    '-- if pinstancestorage.SLOTS = [ppropertyslot] '
    '-- if ppropertyslot.STATE = PROP_VALUE (DIRECT (POBJECT n_child))')
CHECKS = [
    'S_global = $global_table_view(S)',
    '$lookup(S_global.ENV, $ptascii("valueWatch")) = (n_watch_cell)',
    'S.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
    'S.OBJECTS[n_watch] = WEAKREFERENCE (n_value)',
    '$lookup(S_global.ENV, $ptascii("map")) = (n_map_cell)',
    'S.STORE[n_map_cell] = DEFINED (POBJECT n_map)',
    'S.OBJECTS[n_map] = WEAKMAP eps',
    'S.OBJECTS[n_value] = INSTANCE porigin',
    '$objectprops_at(S.OBJECTPROPS, n_value) = ([ppropertyslot])',
    'ppropertyslot.DECL = (porigin_property)',
    '$object_table_at(S.OBJECTTABLES, n_value) = eps',
    '$object_name(S, n_child) = $ptascii("GC37PeerPreChild")',
    '$node_children(S, HOBJECT n_value) = [HOBJECT n_child]',
    '$node_children(S, HOBJECT n_child) = eps',
    'pinstancestorage.NOTIFY = eps',
    '$instance_storage_valid(S, pinstancestorage)',
    '$weakref_get(S, n_watch) = PNULL',
    'H = $heap_graph(S)',
    '$heap_valid(H) /\\ $destruction_state_valid(S) /\\ $call_descriptors_valid(S)',
    '$heap_owners(H, HOBJECT n_value) = 1',
    '$heap_owners(H, HOBJECT n_child) = 1',
    '~$instance_storage_basic(S, pinstancestorage[.SLOTS = eps])',
    'PhpStep: S ~> S_transfer',
    '$node_children(S_transfer, HOBJECT n_value) = eps',
    '$objectprops_at(S_transfer.OBJECTPROPS, n_value) = ([ppropertyslot_cleared])',
    'ppropertyslot_cleared.STATE = PROP_UNSET',
    '$instance_storage_for(S_transfer, n_value) = (pinstancestorage_after)',
    'pinstancestorage_after.NEXT = 1',
    '$heap_owners($heap_graph(S_transfer), HOBJECT n_child) = 1',
    'S_zero = $drive_steps(S, 0)',
    'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
    'S_done = $drive_steps(S, 4000)',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    'S_done.OBJECTS[n_map] = WEAKMAP eps',
    '~((HOBJECT n_value) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
    '$weakref_get(S_done, n_watch) = PNULL',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {
    'declared-value-child-release': {
        'source': SOURCE,
        'stage': STAGE,
        'checks': CHECKS,
    },
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', default=[])
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=240) else 1)
