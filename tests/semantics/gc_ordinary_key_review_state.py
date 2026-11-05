#!/usr/bin/env python3
"""Independent source-reached ordinary weak-Key callback phases."""
import argparse

import fiber_state_review as review
import gc_ordinary_key_review_sources as sources


def wr_case(source_name, watch_name, notice, watched):
    stage = ('S_global = $global_table_view(S) '
        '-- if $lookup(S_global.ENV, $ptascii("target")) = (n_target_cell) '
        '-- if S.STORE[n_target_cell] = DEFINED (POBJECT n_target) '
        f'-- if $lookup(S_global.ENV, $ptascii("{watch_name}")) = (n_watch_cell) '
        '-- if S.STORE[n_watch_cell] = DEFINED (POBJECT n_watch) '
        '-- if S.OBJECTS[n_watch] = WEAKREFERENCE (n_old) '
        '-- if S.OBJECTS[n_old] = WEAKREFERENCE (n_target) '
        '-- if $instance_storage_for(S, n_old) = (pinstancestorage) '
        '-- if $lookup(S_global.ENV, $ptascii("newWR34")) = (n_new_cell) '
        '-- if S.STORE[n_new_cell] = DEFINED (POBJECT n_new) '
        '-- if S.OBJECTS[n_new] = WEAKREFERENCE (n_target)')
    checks = [
        '$instance_storage_freeing(S, n_old)',
        '$instance_storage_basic(S, pinstancestorage)',
        f'pinstancestorage.NOTIFY = {notice}',
        ('$weakmap_storage_create(S, n_old)' if notice != 'eps'
         else '~$weakmap_storage_create(S, n_old)'),
        'pinstancestorage.OBJECT = n_old /\\ pinstancestorage.SLOTS = eps',
        'n_old =/= n_new /\\ n_watch =/= n_new',
        '$weakref_find(S, S.ALLOCATIONS, n_target) = (n_new)',
        '$weakref_get(S, n_old) = PNULL',
        f'$weakref_get(S, n_watch) = {watched}',
        '$weakref_get(S, n_new) = POBJECT n_target',
        '$weakref_state_valid(S)',
        '$lookup(S_global.ENV, $ptascii("map")) = (n_map_cell)',
        'S.STORE[n_map_cell] = DEFINED (POBJECT n_map)',
        'S.OBJECTS[n_map] = WEAKMAP eps',
        '$weakmap_key_maps(S, S.ALLOCATIONS, n_old) = eps',
        'H = $heap_graph(S)', '$heap_valid(H)',
        '$($heap_owners(H, HOBJECT n_old) > 0)',
        'S_duplicate = S[.OBJECTS[n_watch] = WEAKREFERENCE (n_target)]',
        '~$weakref_state_valid(S_duplicate)',
        'S_zero = $drive_steps(S, 0)',
        'S_zero.COMPLETION = BUDGET /\\ S_zero.OBJECTS = S.OBJECTS',
        'S_one = $drive_steps(S, 1)',
        '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = S_one',
    ]
    return {'source': sources.PATHS[source_name].read_text(), 'stage': stage, 'checks': checks}


MAP_STAGE = ('S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail* '
    '-- if $object_name(S, pdestructorcall.OBJECT) = $ptascii("GC34OwnViewGlobal") '
    '-- if S_global = $global_table_view(S) '
    '-- if $lookup(S_global.ENV, $ptascii("watch")) = (n_watch_cell) '
    '-- if S.STORE[n_watch_cell] = DEFINED (POBJECT n_watch) '
    '-- if S.OBJECTS[n_watch] = WEAKREFERENCE (n_map) '
    '-- if $instance_storage_for(S, n_map) = (pinstancestorage)')
MAP_CHECKS = [
    '$instance_storage_basic(S, pinstancestorage)',
    'pinstancestorage.OBJECT = n_map /\\ pinstancestorage.NOTIFY = (n_watch)',
    '$weakmap_storage_create(S, n_map)',
    '$weakmap_storage_read(S, n_watch, n_map)',
    '$weakref_get(S, n_watch) = POBJECT n_map',
    'S.OBJECTS[n_map] = WEAKMAP eps',
    '$node_children(S, HOBJECT n_map) = eps',
    '$lookup(S_global.ENV, $ptascii("outer")) = (n_outer_cell)',
    'S.STORE[n_outer_cell] = DEFINED (POBJECT n_outer)',
    'S.OBJECTS[n_outer] = WEAKMAP (pweakmapentry)',
    'pweakmapentry.KEY = n_map',
    'pweakmapentry.VALUE = POBJECT n_incoming',
    '$weakmap_key_maps(S, S.ALLOCATIONS, n_map) = [n_outer]',
    'H = $heap_graph(S)', '$heap_valid(H)',
    '$heap_children(HOBJECT n_outer, H.EDGES) = [HOBJECT n_incoming]',
    '$heap_owners(H, HOBJECT n_map) = 1',
    '$heap_owners(H, HOBJECT n_incoming) = 1',
    '$destruction_state_valid(S)',
    'S_zero = $drive_steps(S, 0)',
    'S_zero.COMPLETION = BUDGET /\\ S_zero.OBJECTS = S.OBJECTS',
    'S_one = $drive_steps(S, 1)',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = S_one',
]
review.CASES = {
    'wrapper-recreation-after-early-observer': wr_case(
        'wr-recreate-global', 'watch', 'eps', 'PNULL'),
    'wrapper-recreation-before-late-observer': wr_case(
        'wr-old-get-before-observer', 'keyWatch', '(n_watch)', 'POBJECT n_old'),
    'map-own-value-before-incoming-notification': {
        'source': sources.PATHS['map-own-phase-global'].read_text(),
        'stage': MAP_STAGE, 'checks': MAP_CHECKS},
}
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', default=[])
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=240) else 1)
