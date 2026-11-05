#!/usr/bin/env python3
"""Independent source-reached standard weak-Key field ordering checks."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc36_key_child_postinsert.php').read_text()
COMMON = [
    'S_global = $global_table_view(S)',
    '$lookup(S_global.ENV, $ptascii("keyWatch")) = (n_watch_cell)',
    'S.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
    'S.OBJECTS[n_watch] = WEAKREFERENCE (n_key)',
    '$instance_storage_for(S, n_key) = (pinstancestorage)',
    'pinstancestorage.OBJECT = n_key',
    'S.OBJECTS[n_key] = STDINSTANCE',
    '$instance_storage_basic(S, pinstancestorage)',
    'pinstancestorage.SLOTS = [ppropertyslot]',
    '$object_table_at(S.OBJECTTABLES, n_key) = eps',
    'H = $heap_graph(S)',
    '$heap_valid(H) /\\ $destruction_state_valid(S) /\\ $call_descriptors_valid(S)',
    '$heap_owners(H, HOBJECT n_key) = 1',
]
FINISH = [
    'S_zero = $drive_steps(S, 0)',
    'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
    'S_done = $drive_steps(S, 4000)',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    '~((HOBJECT n_key) <- S_done.ALLOCATIONS)',
    '$weakref_get(S_done, n_watch) = PNULL',
    '$heap_valid($heap_graph(S_done))',
]
VALUE = [
    *COMMON,
    'pdestructorcall.OBJECT = n_value',
    '$object_name(S, n_value) = $ptascii("GC36ValuePost")',
    'pinstancestorage.NEXT = 0 /\\ pinstancestorage.NOTIFY = (n_watch)',
    'ppropertyslot.STATE = PROP_VALUE (DIRECT (POBJECT n_child))',
    '$object_name(S, n_child) = $ptascii("GC36ChildPost")',
    '$weakmap_standard_key_child(S, n_key)',
    '$node_children(S, HOBJECT n_key) = [HOBJECT n_child]',
    '$heap_owners(H, HOBJECT n_child) = 1',
    '$weakref_get(S, n_watch) = POBJECT n_key',
    '~$weakmap_key_waiting(S, n_key)',
    *FINISH,
]
CHILD = [
    *COMMON,
    'pdestructorcall.OBJECT = n_child',
    '$object_name(S, n_child) = $ptascii("GC36ChildPost")',
    'pinstancestorage.NEXT = 1 /\\ pinstancestorage.NOTIFY = eps',
    '$objectprops_at(S.OBJECTPROPS, n_key) = ([ppropertyslot_cleared])',
    'ppropertyslot_cleared.STATE = PROP_UNSET',
    '$node_children(S, HOBJECT n_key) = eps',
    '$heap_owners(H, HOBJECT n_child) = 2',
    '$weakref_get(S, n_watch) = PNULL',
    *FINISH,
]
review.CASES = {
    'field-child-held-through-weak-value-callback': {
        'source': SOURCE,
        'stage': 'S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail* '
                 '-- if $object_name(S, pdestructorcall.OBJECT) = $ptascii("GC36ValuePost")',
        'checks': VALUE,
    },
    'field-child-released-after-wrapper-clear': {
        'source': SOURCE,
        'stage': 'S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail* '
                 '-- if $object_name(S, pdestructorcall.OBJECT) = $ptascii("GC36ChildPost")',
        'checks': CHILD,
    },
}
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', default=[])
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=240) else 1)
