#!/usr/bin/env python3
"""Reached inactive weak chains preserve owner counts through both allocators."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
STAGE = ('S.TODO = [EXECUTOR_RELEASE pexecutorqueue EXECUTOR_DONE] '
         '-- if S.DESTRUCTION.OPERATIONS = eps /\\ S.DESTRUCTION.CALLS = eps '
         '-- if S.DESTRUCTION.CLEANUPS = eps /\\ S.DESTRUCTION.RELEASES = eps')
CHECKS = [
    '$call_task_valid(S, EXECUTOR_RELEASE pexecutorqueue EXECUTOR_DONE)',
    '$call_descriptors_valid(S)',
    '$destruction_state_valid(S)',
    '$output_state_valid(S)',
    '$heap_valid($heap_graph(S))',
    'S_global = $global_table_view(S)',
    '$lookup(S_global.ENV, $ptascii("chainParent30")) = (n_parent_cell)',
    '$lookup(S_global.ENV, $ptascii("chainWeak30")) = (n_weak_cell)',
    '$lookup(S_global.ENV, $ptascii("chainAlias30")) = (n_alias_cell)',
    '$lookup(S_global.ENV, $ptascii("chainObserver30")) = (n_chain_cell)',
    '$lookup(S_global.ENV, $ptascii("chainDead30")) = (n_dead_cell)',
    'S.STORE[n_parent_cell] = DEFINED (POBJECT n_parent)',
    'S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
    'S.STORE[n_alias_cell] = DEFINED (POBJECT n_weak)',
    'n_alias_cell =/= n_weak_cell',
    'S.STORE[n_chain_cell] = DEFINED (POBJECT n_chain)',
    'S.STORE[n_dead_cell] = DEFINED (POBJECT n_dead)',
    'S.OBJECTS[n_parent] = STDINSTANCE',
    'S.OBJECTS[n_weak] = WEAKREFERENCE (n_parent)',
    'S.OBJECTS[n_chain] = WEAKREFERENCE (n_weak)',
    'S.OBJECTS[n_dead] = WEAKREFERENCE (n_retired)',
    '~((HOBJECT n_retired) <- S.ALLOCATIONS)',
    '$weakref_get(S, n_dead) = PNULL',
    '$weakref_find(S, S.ALLOCATIONS, n_parent) = (n_weak)',
    '$weakref_find(S, S.ALLOCATIONS, n_weak) = (n_chain)',
    'H_chain = $heap_graph(S)',
    '$heap_owners(H_chain, HOBJECT n_parent) = 1',
    '$heap_owners(H_chain, HOBJECT n_weak) = 2',
    '$heap_owners(H_chain, HOBJECT n_chain) = 1',
    '$heap_owners(H_chain, HOBJECT n_dead) = 1',
    '$node_children(S, HOBJECT n_parent) = eps',
    '$node_children(S, HOBJECT n_weak) = eps',
    '$node_children(S, HOBJECT n_chain) = eps',
    '$node_children(S, HOBJECT n_dead) = eps',
    '$heap_edge_owners(HOBJECT n_parent, H_chain.EDGES, [HOBJECT n_weak]) = 0',
    '$heap_edge_owners(HOBJECT n_weak, H_chain.EDGES, [HOBJECT n_chain]) = 0',
    'S_endpoint = S[.TODO = eps][.COMPLETION = pexecutorqueue.COMPLETION][.ORIGIN = pexecutorqueue.ORIGIN]',
    '$executor_free_endpoint(S_endpoint)',
    'pexecutorfree_start = {HEAP H_chain, MARKED eps, DETACHED eps, FAILED eps, UNKNOWN false}',
    '$executor_free_weak(S_endpoint, eps, n_parent)',
    '$executor_free_weak(S_endpoint, eps, n_weak)',
    '$executor_free_kind(S_endpoint, eps, n_parent) = 1',
    '$executor_free_kind(S_endpoint, eps, n_weak) = 1',
    '$executor_free_kind(S_endpoint, eps, n_chain) = 1',
    '$executor_free_kind(S_endpoint, eps, n_dead) = 1',
    'pexecutorfree_chain = $executor_free_force(S_endpoint, pexecutorfree_start, n_chain)',
    'pexecutorfree_chain.MARKED = [HOBJECT n_chain]',
    '~pexecutorfree_chain.UNKNOWN /\\ pexecutorfree_chain.FAILED = eps',
    'pexecutorfree_chain.HEAP.EDGES = H_chain.EDGES',
    'pexecutorfree_chain.HEAP.NODES = H_chain.NODES',
    'pexecutorfree_chain.HEAP.ROOTS = H_chain.ROOTS ++ [HOBJECT n_chain]',
    '$heap_owners(pexecutorfree_chain.HEAP, HOBJECT n_weak) = 2',
    '$heap_owners(pexecutorfree_chain.HEAP, HOBJECT n_chain) = 2',
    '~$executor_free_weak(S_endpoint, pexecutorfree_chain.MARKED, n_weak)',
    '$executor_free_weak(S_endpoint, pexecutorfree_chain.MARKED, n_parent)',
    '$executor_free_kind(S_endpoint, pexecutorfree_chain.MARKED, n_weak) = 1',
    '$executor_free_force(S_endpoint, pexecutorfree_chain, n_chain) = pexecutorfree_chain',
    '$executor_free_zero(S_endpoint, pexecutorfree_chain, HOBJECT n_chain) = pexecutorfree_chain',
    'pexecutorfree_weak = $executor_free_force(S_endpoint, pexecutorfree_chain, n_weak)',
    'pexecutorfree_weak.MARKED = [HOBJECT n_weak, HOBJECT n_chain]',
    'pexecutorfree_weak.HEAP.EDGES = H_chain.EDGES',
    '$heap_owners(pexecutorfree_weak.HEAP, HOBJECT n_weak) = 3',
    '$heap_owners(pexecutorfree_weak.HEAP, HOBJECT n_parent) = 1',
    '~$executor_free_weak(S_endpoint, pexecutorfree_weak.MARKED, n_parent)',
    '$executor_free_kind(S_endpoint, pexecutorfree_weak.MARKED, n_parent) = 0',
    'pexecutorfree_parent = $executor_free_force(S_endpoint, pexecutorfree_weak, n_parent)',
    'pexecutorfree_parent.MARKED = [HOBJECT n_parent, HOBJECT n_weak, HOBJECT n_chain]',
    '~pexecutorfree_parent.UNKNOWN /\\ pexecutorfree_parent.FAILED = eps',
    '$heap_owners(pexecutorfree_parent.HEAP, HOBJECT n_parent) = n_parent_owners',
    'S_empty = S_endpoint[.OBJECTS[n_dead] = WEAKREFERENCE eps]',
    '$node_children(S_empty, HOBJECT n_dead) = eps',
    '$executor_free_kind(S_empty, eps, n_dead) = 1',
    '$heap_graph(S_empty) = $heap_graph(S_endpoint)',
    '$executor_free_force(S_empty, pexecutorfree_start, n_dead) = $executor_free_force(S_endpoint, pexecutorfree_start, n_dead)',
    'pexecutorfree_tables = $executor_free_tables(S_endpoint, pexecutorfree_start)',
    '~pexecutorfree_tables.UNKNOWN /\\ pexecutorfree_tables.FAILED = eps',
    'pexecutorfree_done = $executor_free_walk(S_endpoint, pexecutorfree_tables, S.DESTRUCTION.NEXT)',
    '~pexecutorfree_done.UNKNOWN /\\ pexecutorfree_done.FAILED = eps',
    '(HOBJECT n_parent) <- pexecutorfree_done.MARKED',
    '(HOBJECT n_weak) <- pexecutorfree_done.MARKED',
    '(HOBJECT n_chain) <- pexecutorfree_done.MARKED',
    '(HOBJECT n_dead) <- pexecutorfree_done.MARKED',
    '$executor_free_result(S_endpoint, pexecutorfree_done) = S_endpoint',
    '$executor_free_finish(S_endpoint) = S_endpoint',
    'S_zero = $drive_steps(S, 0)',
    'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
    'S_zero.ALLOCATIONS = S.ALLOCATIONS /\\ S_zero.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S, 1)',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = S_done',
    'S_done = S_endpoint',
    'S_done.COMPLETION = NORMAL',
    'S_done.OBJECTS = S.OBJECTS /\\ S_done.ALLOCATIONS = S.ALLOCATIONS',
    'S_done.GC = S.GC',
    '$heap_valid($heap_graph(S_done))',
]

review.ROOT = ROOT
SOURCE = (HERE / 'gc_inactive_weak_chain_source.php').read_text()
review.CASES = {
    'fast-observer-chain': {
        'source': SOURCE, 'stage': STAGE,
        'checks': ['n_parent_owners = 1', '$executor_allocator_fast(S.REQUEST)', *CHECKS],
    },
    'slow-observer-chain': {
        'source': SOURCE, 'stage': STAGE,
        'request_env': [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one'), (b'USE_ZEND_ALLOC', b'0')],
        'checks': ['n_parent_owners = 2', '~$executor_allocator_fast(S.REQUEST)', *CHECKS],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
