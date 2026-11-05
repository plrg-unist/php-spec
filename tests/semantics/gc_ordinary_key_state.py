#!/usr/bin/env python3
"""Source-reached ordinary internal-Key pins, value leases and throw suffixes."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
VALID = ['$destructor_operational(S)', '$destruction_state_valid(S)', '$call_descriptors_valid(S)',
         'H = $heap_graph(S)', '$heap_valid(H)',
         'S_global = $global_table_view(S)']
DONE = ['S_zero = $drive_steps(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero.TODO = S.TODO /\\ S_zero.OBJECTS = S.OBJECTS',
        'S_done = $drive_steps(S, 4000)',
        '$drive_steps(S_zero[.COMPLETION = NORMAL], 4000) = S_done',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
        '$call_descriptors_valid(S_done) /\\ $heap_valid($heap_graph(S_done))']


def source(name):
    return (ROOT / 'tests/semantics' / name).read_text()


def binding(name, cell, obj):
    return [f'$lookup(S_global.ENV, $ptascii("{name}")) = ({cell})',
            f'S.STORE[{cell}] = DEFINED (POBJECT {obj})']


RELEASE = ('S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail* '
    '-- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_key)) :: pdestructionjob* '
    '-- if $weakmap_internal_key(S, n_key) '
    '-- if S_unheld = $destructor_release_replace(S, pdestructionrelease[.JOBS = pdestructionjob*]) '
    '-- if $heap_owners($heap_graph(S_unheld), HOBJECT n_key) = 0')
START = [
    '$destructor_release_valid(S, pdestructionrelease)',
    'S_start = $destructor_free(S_unheld, HOBJECT n_key, pdestructionrelease[.JOBS = pdestructionjob*])',
    'S_start.COMPLETION = NORMAL /\\ S_start.EVENTS = S.EVENTS',
    '$instance_storage_for(S_start, n_key) = (pinstancestorage)',
    '$instance_storage_basic(S_start, pinstancestorage)',
    'pinstancestorage.OBJECT = n_key /\\ pinstancestorage.NOTIFY = eps',
    '$heap_owners($heap_graph(S_start), HOBJECT n_key) = 1',
    '$heap_valid($heap_graph(S_start))',
    'PhpStep: S ~> S_started', 'S_started = S_start',
]
RANKED = [
    *VALID, *binding('first', 'n_first_cell', 'n_first'),
    *binding('second', 'n_second_cell', 'n_second'),
    'S.OBJECTS[n_key] = WEAKREFERENCE (n_target)',
    'S.OBJECTS[n_first] = WEAKMAP (pweakmapentry_first)',
    'S.OBJECTS[n_second] = WEAKMAP (pweakmapentry_second)',
    'pweakmapentry_first.VALUE = POBJECT n_value_first',
    'pweakmapentry_second.VALUE = POBJECT n_value_second',
    'pweakmapentry_first.KEY = n_key /\\ pweakmapentry_second.KEY = n_key',
    'pweakmapentry_first.ORDER = 2 /\\ pweakmapentry_second.ORDER = 1',
    'pweakmapentry_first.BEFORE = eps /\\ pweakmapentry_second.BEFORE = eps',
    '$(S.DESTRUCTION.HANDLES[n_first] < S.DESTRUCTION.HANDLES[n_second])',
    '$weakmap_key_maps(S, S.ALLOCATIONS, n_key) = [n_first, n_second]',
    '$gc_ephemeron_key_order_safe(S, n_key)',
    '$weakmap_notice_first(S, n_key, [n_first, n_second]) = (n_second)',
    '$weakmap_notice_first(S, n_key, [n_second, n_first]) = (n_second)',
    '$weakmap_notice_first(S, n_key, eps) = eps',
    *START,
    'S_start.OBJECTS[n_first] = S.OBJECTS[n_first]',
    'S_start.OBJECTS[n_second] = WEAKMAP eps',
    '$weakmap_key_maps(S_start, S_start.ALLOCATIONS, n_key) = [n_first]',
    '$heap_children(HOBJECT n_first, $heap_graph(S_start).EDGES) = [HOBJECT n_value_first]',
    '$heap_children(HOBJECT n_second, $heap_graph(S_start).EDGES) = eps',
    '$heap_owners($heap_graph(S_start), HOBJECT n_value_first) = 1',
    '$heap_owners($heap_graph(S_start), HOBJECT n_value_second) = 1',
    'S_start.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_value) :: ptask_value_tail*',
    'pdestructionrelease_value.JOBS = [DESTRUCTION_VALUE (HOBJECT n_value_second)]',
    '$weakref_find(S_start, S_start.ALLOCATIONS, n_target) = eps',
    '$weakref_get(S_start, n_key) = PNULL',
    'S_duplicate = S[.OBJECTS[n_second] = WEAKMAP (pweakmapentry_second[.ORDER = 2])]',
    '~$gc_ephemeron_key_order_safe(S_duplicate, n_key)',
    '~$weakmap_internal_key(S, n_target)', '~$weakmap_internal_key(S, |S.OBJECTS|)',
    *DONE, 'S_done.OBJECTS[n_first] = WEAKMAP eps /\\ S_done.OBJECTS[n_second] = WEAKMAP eps',
    '~((HOBJECT n_key) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_value_first) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_value_second) <- S_done.ALLOCATIONS)',
]
CROSS = [
    *VALID, *binding('outer', 'n_outer_cell', 'n_outer'),
    *binding('other', 'n_other_cell', 'n_other'),
    *binding('watch', 'n_watch_cell', 'n_watch'),
    'S.OBJECTS[n_key] = WEAKMAPENTRIES ([pweakmapentry_a, pweakmapentry_b])',
    'pweakmapentry_a.VALUE = POBJECT n_value', 'pweakmapentry_b.VALUE = POBJECT n_value',
    'S.OBJECTS[n_outer] = WEAKMAP (pweakmapentry_outer)',
    'S.OBJECTS[n_other] = WEAKMAP (pweakmapentry_other)',
    'pweakmapentry_outer.KEY = n_key /\\ pweakmapentry_other.KEY = n_key',
    'pweakmapentry_outer.VALUE = POBJECT n_value /\\ pweakmapentry_other.VALUE = POBJECT n_value',
    'pweakmapentry_outer.ORDER = 2 /\\ pweakmapentry_other.ORDER = 1',
    '$heap_owners(H, HOBJECT n_value) = 4',
    '$heap_children(HOBJECT n_key, H.EDGES) = [HOBJECT n_value, HOBJECT n_value]',
    '$weakref_get(S, n_watch) = POBJECT n_value',
    *START, 'S_start.OBJECTS[n_key] = WEAKMAP eps',
    'S_start.OBJECTS[n_outer] = S.OBJECTS[n_outer] /\\ S_start.OBJECTS[n_other] = S.OBJECTS[n_other]',
    '$weakmap_key_maps(S_start, S_start.ALLOCATIONS, pweakmapentry_a.KEY) = eps',
    '$weakmap_key_maps(S_start, S_start.ALLOCATIONS, pweakmapentry_b.KEY) = eps',
    '$heap_children(HOBJECT n_key, $heap_graph(S_start).EDGES) = eps',
    '$heap_owners($heap_graph(S_start), HOBJECT n_value) = 4',
    'S_start.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_own) :: ptask_own_tail*',
    'pdestructionrelease_own.JOBS = [DESTRUCTION_VALUE (HOBJECT n_value), DESTRUCTION_VALUE (HOBJECT n_value)]',
    '$weakmap_notice_first(S_start, n_key, [n_outer, n_other]) = (n_other)',
    *DONE, 'S_done.OBJECTS[n_outer] = WEAKMAP eps /\\ S_done.OBJECTS[n_other] = WEAKMAP eps',
    '~((HOBJECT n_key) <- S_done.ALLOCATIONS)', '~((HOBJECT n_value) <- S_done.ALLOCATIONS)',
    '$weakref_get(S_done, n_watch) = PNULL',
]
THROW = [
    *VALID, *binding('outer', 'n_outer_cell', 'n_outer'),
    'S.TODO = (DESTRUCTOR_ENTER pdestructorcall_first) :: ptask_first_tail*',
    '$object_name(S, pdestructorcall_first.OBJECT) = $ptascii("GC34OwnThrow")',
    'pdestructorcall_first.PENDING = eps',
    'S.OBJECTS[n_outer] = WEAKMAP (pweakmapentry_outer)',
    'n_key = pweakmapentry_outer.KEY', 'pweakmapentry_outer.VALUE = POBJECT n_incoming',
    'S.OBJECTS[n_key] = WEAKMAPENTRIES ([pweakmapentry_first, pweakmapentry_second])',
    'pweakmapentry_first.VALUE = POBJECT n_first', 'pweakmapentry_second.VALUE = POBJECT n_second',
    'pdestructorcall_first.OBJECT = n_first',
    '$instance_storage_for(S, n_key) = (pinstancestorage)',
    '$instance_storage_basic(S, pinstancestorage)',
    '$heap_owners(H, HOBJECT n_key) = 1 /\\ $heap_owners(H, HOBJECT n_incoming) = 1',
    '$heap_owners(H, HOBJECT n_second) = 1',
    '$heap_children(HOBJECT n_key, H.EDGES) = eps',
    '$weakmap_key_maps(S, S.ALLOCATIONS, pweakmapentry_first.KEY) = eps',
    '$weakmap_key_maps(S, S.ALLOCATIONS, pweakmapentry_second.KEY) = eps',
    'S_middle = $seek($drive_steps(S, 1), 2000)',
    'S_middle.TODO = (DESTRUCTOR_ENTER pdestructorcall_second) :: ptask_second_tail*',
    'pdestructorcall_second.OBJECT = n_second',
    '$object_name(S_middle, n_second) = $ptascii("GC34OwnLater")',
    'pdestructorcall_second.PENDING = (n_error)',
    '$destructor_call_pending_valid(S_middle, pdestructorcall_second)',
    'S_middle.OBJECTS[n_outer] = S.OBJECTS[n_outer]',
    '$heap_owners($heap_graph(S_middle), HOBJECT n_key) = 1',
    '$heap_owners($heap_graph(S_middle), HOBJECT n_incoming) = 1',
    'S_incoming = $seek($drive_steps(S_middle, 1), 2000)',
    'S_incoming.TODO = (DESTRUCTOR_ENTER pdestructorcall_incoming) :: ptask_incoming_tail*',
    'pdestructorcall_incoming.OBJECT = n_incoming',
    'pdestructorcall_incoming.PENDING = (n_error)',
    '$destructor_call_pending_valid(S_incoming, pdestructorcall_incoming)',
    'S_incoming.OBJECTS[n_outer] = WEAKMAP eps',
    '$heap_owners($heap_graph(S_incoming), HOBJECT n_key) = 1',
    *DONE, '~((HOBJECT n_key) <- S_done.ALLOCATIONS)',
    'S_done.OBJECTS[n_outer] = WEAKMAP eps',
]
CHILD = [
    *VALID, *binding('first', 'n_first_cell', 'n_first'),
    *binding('second', 'n_second_cell', 'n_second'),
    'S.TODO = (DESTRUCTOR_ENTER pdestructorcall_first) :: ptask_first_tail*',
    '$object_name(S, pdestructorcall_first.OBJECT) = $ptascii("GcOrdinaryIncomingThrow34")',
    'S.OBJECTS[n_second] = WEAKMAP eps',
    'S.OBJECTS[n_first] = WEAKMAP (pweakmapentry_first)',
    'n_key = pweakmapentry_first.KEY', 'pweakmapentry_first.VALUE = POBJECT n_later',
    'S.OBJECTS[n_key] = WEAKREFERENCE (n_target)',
    '$instance_storage_all(S) = [pinstancestorage_holder, pinstancestorage_key]',
    'pinstancestorage_key.OBJECT = n_key',
    'n_holder = pinstancestorage_holder.OBJECT',
    '$object_name(S, n_holder) = $ptascii("GcOrdinaryIncomingHolder34")',
    '$instance_storage_basic(S, pinstancestorage_holder)',
    '$instance_storage_basic(S, pinstancestorage_key)',
    '$node_children(S, HOBJECT n_holder) = eps',
    '$node_children(S, HOBJECT n_later) = [HOBJECT n_child_later]',
    '$object_name(S, n_child_later) = $ptascii("GcOrdinaryIncomingLater34")',
    '$heap_owners(H, HOBJECT n_key) = 1 /\\ $heap_owners(H, HOBJECT n_holder) = 1',
    '$heap_owners(H, HOBJECT n_later) = 1 /\\ $heap_owners(H, HOBJECT n_child_later) = 1',
    '$weakmap_key_maps(S, S.ALLOCATIONS, n_key) = [n_first]',
    '$weakref_find(S, S.ALLOCATIONS, n_target) = eps',
    'S_later = $seek($drive_steps(S, 1), 2000)',
    'S_later.TODO = (DESTRUCTOR_ENTER pdestructorcall_later) :: ptask_later_tail*',
    'pdestructorcall_later.OBJECT = n_child_later',
    'pdestructorcall_later.PENDING = (n_error)',
    '$destructor_call_pending_valid(S_later, pdestructorcall_later)',
    'S_later.OBJECTS[n_first] = WEAKMAP eps',
    '$instance_storage_all(S_later) = [pinstancestorage_later_holder, pinstancestorage_key]',
    'pinstancestorage_later_holder.OBJECT = n_later',
    '~((HOBJECT n_holder) <- S_later.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_later), HOBJECT n_key) = 1',
    *DONE, 'S_done.OBJECTS[n_first] = WEAKMAP eps /\\ S_done.OBJECTS[n_second] = WEAKMAP eps',
    '~((HOBJECT n_key) <- S_done.ALLOCATIONS)', '~((HOBJECT n_later) <- S_done.ALLOCATIONS)',
]
review.CASES = {
    'ranked-incoming-wrapper-pins': {
        'source': source('gc_ordinary_review_wr_two_incoming_leaves.php'),
        'stage': RELEASE, 'checks': RANKED},
    'own-and-incoming-four-value-owners': {
        'source': source('gc_ordinary_map_cross_shared_source.php'),
        'stage': RELEASE, 'checks': CROSS},
    'own-throw-drains-value-and-incoming-suffix': {
        'source': source('gc_ordinary_review_map_own_throw_suffix.php'),
        'stage': 'S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*',
        'checks': THROW},
    'incoming-child-throw-keeps-later-entry': {
        'source': source('gc_ordinary_incoming_child_throw_source.php'),
        'stage': 'S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*',
        'checks': CHILD},
}
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', default=[])
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=240) else 1)
