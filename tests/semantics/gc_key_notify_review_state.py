#!/usr/bin/env python3
"""Source-reached selective Key notification and duplicate Map-edge checks."""
import argparse

import fiber_state_review as review
import gc_key_notify_review_sources as sources


STAGE = ('S.TODO = [EXECUTOR_RELEASE pexecutorqueue EXECUTOR_DONE] '
         '-- if S.DESTRUCTION.OPERATIONS = eps /\\ S.DESTRUCTION.CALLS = eps '
         '-- if S.DESTRUCTION.CLEANUPS = eps /\\ S.DESTRUCTION.RELEASES = eps')
COMMON = [
    '$call_task_valid(S, EXECUTOR_RELEASE pexecutorqueue EXECUTOR_DONE)',
    '$call_descriptors_valid(S)', '$destruction_state_valid(S)',
    '$output_state_valid(S)', '$class_state_valid(S)',
    'S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.ITERATORS = eps',
    'S_global = $global_table_view(S)',
    'S_endpoint = S[.TODO = eps][.COMPLETION = pexecutorqueue.COMPLETION][.ORIGIN = pexecutorqueue.ORIGIN]',
    '$executor_free_endpoint(S_endpoint)',
    '$executor_allocator_fast(S_endpoint.REQUEST)',
    'H = $heap_graph(S_endpoint)', '$heap_valid(H)',
    'pexecutorfree_start = {HEAP H, MARKED eps, DETACHED eps, FAILED eps, UNKNOWN false}',
    'S_zero = $drive_steps(S, 0)',
    'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
    'S_zero.ALLOCATIONS = S.ALLOCATIONS /\\ S_zero.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S, 1)',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = S_done',
    'S_done.OBJECTS = S.OBJECTS /\\ S_done.ALLOCATIONS = S.ALLOCATIONS',
    '$heap_valid($heap_graph(S_done))',
    'S_done.EXITSTATUS = 0',
]
SELECTIVE = [*COMMON,
    '$lookup(S_global.ENV, $ptascii("gcNotifyMap32")) = (n_map_cell)',
    '$lookup(S_global.ENV, $ptascii("gcNotifyKeyB32")) = (n_keyB_cell)',
    '$lookup(S_global.ENV, $ptascii("gcNotifyKeyA32")) = (n_keyA_cell)',
    '$lookup(S_global.ENV, $ptascii("gcNotifyHeldA32")) = (n_a_cell)',
    'S.STORE[n_map_cell] = DEFINED (POBJECT n_map)',
    'S.STORE[n_keyB_cell] = DEFINED (POBJECT n_keyB)',
    'S.STORE[n_keyA_cell] = DEFINED (POBJECT n_keyA)',
    'S.STORE[n_a_cell] = DEFINED (POBJECT n_a)',
    'S.OBJECTS[n_map] = WEAKMAPENTRIES ([pentry_a, pentry_b])',
    'pentry_a.KEY = n_keyA /\\ pentry_a.VALUE = POBJECT n_a',
    'pentry_b.KEY = n_keyB /\\ pentry_b.VALUE = POBJECT n_b',
    'pentry_a.BEFORE = eps /\\ pentry_b.BEFORE = eps',
    'pentry_a.ORDER = 1 /\\ pentry_b.ORDER = 1',
    'S.OBJECTS[n_keyA] = STDINSTANCE /\\ S.OBJECTS[n_keyB] = STDINSTANCE',
    '$object_name(S, n_a) = $ptascii("GcNotifyHeldA32")',
    '$object_name(S, n_b) = $ptascii("GcNotifySpareB32")',
    '$object_name(S, n_c) = $ptascii("GcNotifyFieldC32")',
    '$node_children(S, HOBJECT n_map) = [HOBJECT n_a, HOBJECT n_b]',
    '$node_children(S, HOBJECT n_keyA) = [HOBJECT n_c]',
    '$node_children(S, HOBJECT n_keyB) = eps',
    '$heap_owners(H, HOBJECT n_map) = 1',
    '$heap_owners(H, HOBJECT n_keyA) = 1 /\\ $heap_owners(H, HOBJECT n_keyB) = 1',
    '$heap_owners(H, HOBJECT n_a) = 2',
    '$heap_owners(H, HOBJECT n_b) = 1 /\\ $heap_owners(H, HOBJECT n_c) = 1',
    '$executor_free_key_maps(S_endpoint, eps, n_keyA) = [n_map]',
    '$executor_free_kind(S_endpoint, eps, n_keyA) = 1',
    '$executor_free_kind(S_endpoint, [HOBJECT n_map], n_keyA) = 0',
    '$(S.DESTRUCTION.HANDLES[n_keyB] < S.DESTRUCTION.HANDLES[n_keyA])',
    'pexecutorfree_key = $executor_free_force(S_endpoint, pexecutorfree_start, n_keyA)',
    '~pexecutorfree_key.UNKNOWN /\\ pexecutorfree_key.FAILED = (n_c)',
    '(HOBJECT n_keyA) <- pexecutorfree_key.MARKED',
    '$heap_children(HOBJECT n_map, pexecutorfree_key.HEAP.EDGES) = [HOBJECT n_b]',
    '$heap_children(HOBJECT n_keyA, pexecutorfree_key.HEAP.EDGES) = eps',
    '$heap_owners(pexecutorfree_key.HEAP, HOBJECT n_a) = 1',
    '$heap_owners(pexecutorfree_key.HEAP, HOBJECT n_b) = 1',
    '$heap_owners(pexecutorfree_key.HEAP, HOBJECT n_c) = 0',
    '$heap_owners(pexecutorfree_key.HEAP, HOBJECT n_keyA) = 2',
    '$executor_free_key_maps(S_endpoint, pexecutorfree_key.MARKED, n_keyB) = [n_map]',
    'pexecutorfree_done = $executor_free_walk(S_endpoint, pexecutorfree_start, S.DESTRUCTION.NEXT)',
    'pexecutorfree_done.FAILED = (n_c) /\\ ~pexecutorfree_done.UNKNOWN',
    'S_done.COMPLETION = REQUESTFATAL ($ptascii("Error")) $ptascii("Couldn\'t execute method GcNotifyFieldC32::__destruct") 0',
]
SHARED = [*COMMON,
    '$lookup(S_global.ENV, $ptascii("gcNotifySharedMap32")) = (n_map_cell)',
    '$lookup(S_global.ENV, $ptascii("gcNotifySharedKeyB32")) = (n_keyB_cell)',
    '$lookup(S_global.ENV, $ptascii("gcNotifySharedKeyA32")) = (n_keyA_cell)',
    'S.STORE[n_map_cell] = DEFINED (POBJECT n_map)',
    'S.STORE[n_keyB_cell] = DEFINED (POBJECT n_keyB)',
    'S.STORE[n_keyA_cell] = DEFINED (POBJECT n_keyA)',
    'S.OBJECTS[n_map] = WEAKMAPENTRIES ([pentry_a, pentry_b])',
    'pentry_a.KEY = n_keyA /\\ pentry_b.KEY = n_keyB',
    'pentry_a.VALUE = POBJECT n_shared /\\ pentry_b.VALUE = POBJECT n_shared',
    '$object_name(S, n_shared) = $ptascii("GcNotifySharedA32")',
    '$object_name(S, n_c) = $ptascii("GcNotifySharedField32")',
    '$node_children(S, HOBJECT n_map) = [HOBJECT n_shared, HOBJECT n_shared]',
    '$node_children(S, HOBJECT n_keyA) = [HOBJECT n_c]',
    '$heap_owners(H, HOBJECT n_shared) = 2',
    '$heap_owners(H, HOBJECT n_c) = 1',
    '$executor_free_kind(S_endpoint, eps, n_keyA) = 1',
    'pexecutorfree_key = $executor_free_force(S_endpoint, pexecutorfree_start, n_keyA)',
    '~pexecutorfree_key.UNKNOWN /\\ pexecutorfree_key.FAILED = (n_c)',
    '$heap_children(HOBJECT n_map, pexecutorfree_key.HEAP.EDGES) = [HOBJECT n_shared]',
    '$heap_owners(pexecutorfree_key.HEAP, HOBJECT n_shared) = 1',
    '$heap_owners(pexecutorfree_key.HEAP, HOBJECT n_c) = 0',
    'pexecutorfree_done = $executor_free_walk(S_endpoint, pexecutorfree_start, S.DESTRUCTION.NEXT)',
    'pexecutorfree_done.FAILED = (n_c) /\\ ~pexecutorfree_done.UNKNOWN',
    'S_done.COMPLETION = REQUESTFATAL ($ptascii("Error")) $ptascii("Couldn\'t execute method GcNotifySharedField32::__destruct") 0',
]

review.ROOT = sources.ROOT
review.CASES = {
    'selective': {'source': sources.PATHS['selective'].read_text(), 'stage': STAGE, 'checks': SELECTIVE},
    'shared-value': {'source': sources.PATHS['shared-value'].read_text(), 'stage': STAGE, 'checks': SHARED},
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
