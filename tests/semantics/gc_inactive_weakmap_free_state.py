#!/usr/bin/env python3
"""Reached Map cleanup keeps leased value edges and reference-cell ownership."""
import argparse

import fiber_state_review as review
import gc_inactive_weakmap_free_sources as sources


ROOT = sources.ROOT
STAGE = ('S.TODO = [EXECUTOR_RELEASE pexecutorqueue EXECUTOR_DONE] '
         '-- if S.DESTRUCTION.OPERATIONS = eps /\\ S.DESTRUCTION.CALLS = eps '
         '-- if S.DESTRUCTION.CLEANUPS = eps /\\ S.DESTRUCTION.RELEASES = eps')
COMMON = [
    '$call_task_valid(S, EXECUTOR_RELEASE pexecutorqueue EXECUTOR_DONE)',
    '$call_descriptors_valid(S)', '$destruction_state_valid(S)',
    '$output_state_valid(S)', '$class_state_valid(S)',
    'S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.ITERATORS = eps',
    'S_global = $global_table_view(S)',
    'H = $heap_graph(S)', '$heap_valid(H)',
    'S_endpoint = S[.TODO = eps][.COMPLETION = pexecutorqueue.COMPLETION][.ORIGIN = pexecutorqueue.ORIGIN]',
    '$executor_free_endpoint(S_endpoint)',
    'pexecutorfree_start = {HEAP H, MARKED eps, DETACHED eps, FAILED eps, UNKNOWN false}',
]
MAP_COMMON = [
    '$executor_free_kind(S_endpoint, eps, n_map) = 1',
    '~$instance_storage_freeing(S_endpoint, n_map)',
    '$executor_free_key_maps(S_endpoint, eps, n_map) = eps',
    '$heap_owners(H, HOBJECT n_map) = 1',
]
FINISH = [
    'S_zero = $drive_steps(S, 0)',
    'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
    'S_zero.ALLOCATIONS = S.ALLOCATIONS /\\ S_zero.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S, 1)',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = S_done',
    'S_done.OBJECTS = S.OBJECTS /\\ S_done.ALLOCATIONS = S.ALLOCATIONS',
    'S_done.GC = S.GC', '$heap_valid($heap_graph(S_done))',
]


def binding(name, cell, value):
    return [f'$lookup(S_global.ENV, $ptascii("{name}")) = ({cell})',
            f'S.STORE[{cell}] = DEFINED (POBJECT {value})']


HELD = [*COMMON,
    '$executor_allocator_fast(S.REQUEST)',
    *binding('studyMap', 'n_map_cell', 'n_map'),
    *binding('studyKey', 'n_key_cell', 'n_key'),
    *binding('studyValue', 'n_value_cell', 'n_a'), *MAP_COMMON,
    'S.OBJECTS[n_map] = WEAKMAP ({KEY n_key, VALUE (POBJECT n_a), BEFORE eps, ORDER 1})',
    '$node_children(S, HOBJECT n_key) = [HOBJECT n_b]',
    '$node_children(S, HOBJECT n_map) = [HOBJECT n_a]',
    '$object_name(S, n_a) = $ptascii("StudyMapValueA")',
    '$object_name(S, n_b) = $ptascii("StudyMapValueB")',
    '$heap_owners(H, HOBJECT n_a) = 2 /\\ $heap_owners(H, HOBJECT n_b) = 1',
    '$heap_owners(H, HOBJECT n_key) = 1',
    '$heap_edge_owners(HOBJECT n_key, H.EDGES, [HOBJECT n_map]) = 0',
    '$executor_free_key_maps(S_endpoint, eps, n_key) = [n_map]',
    '$executor_free_kind(S_endpoint, eps, n_key) = 1',
    '$(S.DESTRUCTION.HANDLES[n_key] < S.DESTRUCTION.HANDLES[n_map])',
    '$(S.DESTRUCTION.HANDLES[n_map] < S.DESTRUCTION.HANDLES[n_a])',
    '$(S.DESTRUCTION.HANDLES[n_a] < S.DESTRUCTION.HANDLES[n_b])',
    '~(n_a <- S.DESTRUCTION.CALLED) /\\ ~(n_b <- S.DESTRUCTION.CALLED)',
    'pexecutorfree_values = $executor_free_force(S_endpoint, $executor_free_force(S_endpoint, pexecutorfree_start, n_b), n_a)',
    'pexecutorfree_values.MARKED = [HOBJECT n_a, HOBJECT n_b]',
    'pexecutorfree_values.HEAP = H',
    'pexecutorfree_map = $executor_free_force(S_endpoint, pexecutorfree_values, n_map)',
    '~pexecutorfree_map.UNKNOWN /\\ pexecutorfree_map.FAILED = eps',
    'pexecutorfree_map.MARKED = [HOBJECT n_map, HOBJECT n_a, HOBJECT n_b]',
    '$heap_children(HOBJECT n_map, pexecutorfree_map.HEAP.EDGES) = eps',
    '$heap_children(HOBJECT n_key, pexecutorfree_map.HEAP.EDGES) = [HOBJECT n_b]',
    '$heap_owners(pexecutorfree_map.HEAP, HOBJECT n_a) = 1',
    '$heap_owners(pexecutorfree_map.HEAP, HOBJECT n_b) = 1',
    '$heap_owners(pexecutorfree_map.HEAP, HOBJECT n_map) = 2',
    '$executor_free_key_maps(S_endpoint, pexecutorfree_map.MARKED, n_key) = eps',
    '$executor_free_kind(S_endpoint, pexecutorfree_map.MARKED, n_key) = 0',
    'pexecutorfree_key = $executor_free_force(S_endpoint, pexecutorfree_map, n_key)',
    'pexecutorfree_key.HEAP = pexecutorfree_map.HEAP',
    'pexecutorfree_done = $executor_free_walk(S_endpoint, pexecutorfree_start, S.DESTRUCTION.NEXT)',
    '~pexecutorfree_done.UNKNOWN /\\ pexecutorfree_done.FAILED = eps',
    '$heap_children(HOBJECT n_key, pexecutorfree_done.HEAP.EDGES) = [HOBJECT n_b]',
    '$heap_owners(pexecutorfree_done.HEAP, HOBJECT n_b) = 1',
    *FINISH, 'S_done = S_endpoint', 'S_done.COMPLETION = NORMAL',
]

ORDER = [*COMMON,
    '$executor_allocator_fast(S.REQUEST)',
    *binding('studyMap', 'n_map_cell', 'n_map'),
    *binding('studyKeyA', 'n_keya_cell', 'n_keya'),
    *binding('studyKeyB', 'n_keyb_cell', 'n_keyb'), *MAP_COMMON,
    'S.OBJECTS[n_map] = WEAKMAPENTRIES ([{KEY n_keya, VALUE (POBJECT n_a), BEFORE eps, ORDER 1}, {KEY n_keyb, VALUE (POBJECT n_b), BEFORE eps, ORDER 1}])',
    '$node_children(S, HOBJECT n_map) = [HOBJECT n_a, HOBJECT n_b]',
    '$heap_owners(H, HOBJECT n_a) = 1 /\\ $heap_owners(H, HOBJECT n_b) = 1',
    '$heap_owners(H, HOBJECT n_keya) = 1 /\\ $heap_owners(H, HOBJECT n_keyb) = 1',
    '$object_name(S, n_a) = $ptascii("StudyMapValueA")',
    '$object_name(S, n_b) = $ptascii("StudyMapValueB")',
    '$(S.DESTRUCTION.HANDLES[n_map] < S.DESTRUCTION.HANDLES[n_a])',
    '$(S.DESTRUCTION.HANDLES[n_a] < S.DESTRUCTION.HANDLES[n_b])',
    '~(n_a <- S.DESTRUCTION.CALLED) /\\ ~(n_b <- S.DESTRUCTION.CALLED)',
    '$executor_free_key_maps(S_endpoint, eps, n_keya) = [n_map]',
    '$executor_free_key_maps(S_endpoint, eps, n_keyb) = [n_map]',
    'pexecutorfree_values = $executor_free_force(S_endpoint, $executor_free_force(S_endpoint, pexecutorfree_start, n_b), n_a)',
    'pexecutorfree_values.MARKED = [HOBJECT n_a, HOBJECT n_b]',
    'pexecutorfree_values.HEAP = H',
    'pexecutorfree_map = $executor_free_force(S_endpoint, pexecutorfree_values, n_map)',
    '~pexecutorfree_map.UNKNOWN /\\ pexecutorfree_map.FAILED = (n_a)',
    'pexecutorfree_map.MARKED = [HOBJECT n_map, HOBJECT n_a, HOBJECT n_b]',
    '$heap_children(HOBJECT n_map, pexecutorfree_map.HEAP.EDGES) = eps',
    '$heap_owners(pexecutorfree_map.HEAP, HOBJECT n_a) = 0',
    '$heap_owners(pexecutorfree_map.HEAP, HOBJECT n_b) = 1',
    '$heap_count(HOBJECT n_b, pexecutorfree_map.HEAP.ROOTS) = 1',
    '$heap_owners(pexecutorfree_map.HEAP, HOBJECT n_map) = 2',
    '$executor_free_key_maps(S_endpoint, pexecutorfree_map.MARKED, n_keya) = eps',
    '$executor_free_key_maps(S_endpoint, pexecutorfree_map.MARKED, n_keyb) = eps',
    'pexecutorfree_done = $executor_free_walk(S_endpoint, pexecutorfree_start, S.DESTRUCTION.NEXT)',
    'pexecutorfree_done = pexecutorfree_map',
    *FINISH,
    '''ptbytes_fatal = $ptascii("Couldn't execute method StudyMapValueA::__destruct")''',
    'S_done.COMPLETION = REQUESTFATAL ($ptascii("Error")) ptbytes_fatal 0',
    'S_done.EXITSTATUS = 0',
    'preqbytes_fatal = $ptascii("Fatal error: ") ++ ptbytes_fatal ++ $ptascii(" in Unknown on line 0") ++ [10] ++ $ptascii("Stack trace:") ++ [10] ++ $ptascii("#0 {main}") ++ [10]',
    'S_done.EVENTS = S.EVENTS ++ [STDERR preqbytes_fatal]',
]

ALIAS = [*COMMON,
    *binding('map31', 'n_map_cell', 'n_map'), *MAP_COMMON,
    *binding('emptyMap31', 'n_empty_cell', 'n_empty'),
    *binding('mapKey31', 'n_key_cell', 'n_key'),
    '$lookup(S_global.ENV, $ptascii("mapAlias31")) = (n_alias)',
    'S.STORE[n_alias] = DEFINED (POBJECT n_value)',
    'n_alias <- S.REFCELLS /\\ (HCELL n_alias) <- S.ALLOCATIONS',
    '$weakmap_reference_cell_valid(S, n_alias)',
    'S.OBJECTS[n_map] = WEAKMAP ({KEY n_key, VALUE (ALIAS n_alias), BEFORE eps, ORDER 1})',
    'S.OBJECTS[n_empty] = WEAKMAP eps',
    '$node_children(S, HOBJECT n_empty) = eps',
    '$node_children(S, HOBJECT n_map) = [HCELL n_alias]',
    '$node_children(S, HCELL n_alias) = [HOBJECT n_value]',
    '$heap_owners(H, HCELL n_alias) = 2',
    '$heap_owners(H, HOBJECT n_value) = 1',
    '$heap_owners(H, HOBJECT n_key) = 1',
    '$heap_owners(H, HOBJECT n_empty) = 1',
    '$heap_edge_owners(HOBJECT n_value, H.EDGES, [HOBJECT n_map]) = 0',
    '$heap_edge_owners(HCELL n_alias, H.EDGES, [HOBJECT n_map]) = 1',
    '$heap_edge_owners(HOBJECT n_value, H.EDGES, [HCELL n_alias]) = 1',
    '$executor_free_kind(S_endpoint, eps, n_empty) = 1',
    'pexecutorfree_empty = $executor_free_force(S_endpoint, pexecutorfree_start, n_empty)',
    'pexecutorfree_empty.MARKED = [HOBJECT n_empty]',
    'pexecutorfree_empty.HEAP.EDGES = H.EDGES',
    '$heap_owners(pexecutorfree_empty.HEAP, HOBJECT n_empty) = 2',
    'pexecutorfree_map = $executor_free_force(S_endpoint, pexecutorfree_empty, n_map)',
    '~pexecutorfree_map.UNKNOWN /\\ pexecutorfree_map.FAILED = eps',
    '$heap_children(HOBJECT n_map, pexecutorfree_map.HEAP.EDGES) = eps',
    '$heap_owners(pexecutorfree_map.HEAP, HCELL n_alias) = 1',
    '$heap_owners(pexecutorfree_map.HEAP, HOBJECT n_value) = 1',
    '$executor_free_key_maps(S_endpoint, pexecutorfree_map.MARKED, n_key) = eps',
    'pexecutorfree_cell = $executor_free_release(S_endpoint, pexecutorfree_map, [HCELL n_alias])',
    '~pexecutorfree_cell.UNKNOWN /\\ pexecutorfree_cell.FAILED = eps',
    '$heap_owners(pexecutorfree_cell.HEAP, HCELL n_alias) = 0',
    '$heap_owners(pexecutorfree_cell.HEAP, HOBJECT n_value) = 0',
    'pexecutorfree_tables = $executor_free_tables(S_endpoint, pexecutorfree_start)',
    '~pexecutorfree_tables.UNKNOWN /\\ pexecutorfree_tables.FAILED = eps',
    'pexecutorfree_done = $executor_free_walk(S_endpoint, pexecutorfree_tables, S.DESTRUCTION.NEXT)',
    '~pexecutorfree_done.UNKNOWN /\\ pexecutorfree_done.FAILED = eps',
    *FINISH, 'S_done = S_endpoint', 'S_done.COMPLETION = NORMAL',
]

review.ROOT = ROOT
review.CASES = {
    'map-unregister-keeps-key-field-shielded': {
        'source': sources.PATHS['map-held-value'].read_text(), 'stage': STAGE, 'checks': HELD},
    'map-value-order-keeps-later-lease': {
        'source': sources.PATHS['map-values-ab'].read_text(), 'stage': STAGE, 'checks': ORDER},
    'map-alias-and-empty-fast': {
        'source': sources.PATHS['map-alias-empty'].read_text(), 'stage': STAGE,
        'checks': ['$executor_allocator_fast(S.REQUEST)', *ALIAS]},
    'map-alias-and-empty-slow': {
        'source': sources.PATHS['map-alias-empty'].read_text(), 'stage': STAGE,
        'request_env': [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one'), (b'USE_ZEND_ALLOC', b'0')],
        'checks': ['~$executor_allocator_fast(S.REQUEST)', *ALIAS,
                   '(HOBJECT n_map) <- pexecutorfree_tables.MARKED',
                   '(HOBJECT n_empty) <- pexecutorfree_tables.MARKED',
                   '$heap_owners(pexecutorfree_tables.HEAP, HCELL n_alias) = 0',
                   '$heap_owners(pexecutorfree_tables.HEAP, HOBJECT n_value) = 0']},
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
