#!/usr/bin/env python3
"""Independent weak-hook order, retained headers and notification fences."""
import argparse

import gc_caller_materialized_state as ordinary
import gc_inactive_weak_free_review_sources as sources
import shutdown_state_review as runner


STAGE = ('S.TODO = [EXECUTOR_RELEASE pexecutorqueue EXECUTOR_DONE] '
         '-- if S.DESTRUCTION.OPERATIONS = eps /\\ S.DESTRUCTION.CALLS = eps '
         '-- if S.DESTRUCTION.CLEANUPS = eps /\\ S.DESTRUCTION.RELEASES = eps')
COMMON = [
    '$call_task_valid(S, EXECUTOR_RELEASE pexecutorqueue EXECUTOR_DONE)',
    '$call_descriptors_valid(S)',
    '$destruction_state_valid(S)',
    '$output_state_valid(S)',
    'S.CURRENT = eps',
    'S.FRAMES = eps',
    'S.OUTPUTBUFFERS = eps',
    'S.SHUTDOWN.ENTRIES = eps',
    'S.DESTRUCTION.PHASE = DESTRUCTION_DONE',
    'S_global = $global_table_view(S)',
    '$lookup(S_global.ENV, $ptascii("savedParent")) = (n_parent_cell)',
    '$lookup(S_global.ENV, $ptascii("savedWeak")) = (n_weak_cell)',
    '$lookup(S_global.ENV, $ptascii("parent")) = (n_original_parent_cell)',
    '$lookup(S_global.ENV, $ptascii("weak")) = (n_original_weak_cell)',
    'n_original_parent_cell =/= n_parent_cell',
    'n_original_weak_cell =/= n_weak_cell',
    'S.STORE[n_parent_cell] = DEFINED (POBJECT n_parent)',
    'S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
    'S.STORE[n_original_parent_cell] = DEFINED (POBJECT n_parent)',
    'S.STORE[n_original_weak_cell] = DEFINED (POBJECT n_weak)',
    'S.OBJECTS[n_weak] = WEAKREFERENCE (n_parent)',
    '$node_children(S, HOBJECT n_parent) = [HOBJECT n_child]',
    '$object_name(S, n_child) = $ptascii("GcWeakOrderChild30")',
    '~(n_child <- S.DESTRUCTION.CALLED)',
    '$node_children(S, HOBJECT n_weak) = eps',
    'S_endpoint = S[.TODO = eps][.COMPLETION = pexecutorqueue.COMPLETION][.ORIGIN = pexecutorqueue.ORIGIN]',
    '$executor_free_endpoint(S_endpoint)',
    '$executor_allocator_fast(S_endpoint.REQUEST)',
    'S_endpoint.COMPLETION = NORMAL',
    'H = $heap_graph(S_endpoint)',
    '$heap_valid(H)',
    '$heap_owners(H, HOBJECT n_parent) = n_parent_owners',
    '$heap_owners(H, HOBJECT n_weak) = 2',
    '$heap_edge_owners(HOBJECT n_parent, H.EDGES, [HCELL n_parent_cell, HCELL n_original_parent_cell]) = 2',
    '$heap_edge_owners(HOBJECT n_weak, H.EDGES, [HCELL n_weak_cell, HCELL n_original_weak_cell]) = 2',
    '$heap_count(HCELL n_parent_cell, H.ROOTS) = 1',
    '$heap_count(HCELL n_original_parent_cell, H.ROOTS) = 1',
    '$heap_count(HCELL n_weak_cell, H.ROOTS) = 1',
    '$heap_count(HCELL n_original_weak_cell, H.ROOTS) = 1',
    '$heap_owners(H, HOBJECT n_child) = 1',
    '$heap_edge_owners(HOBJECT n_child, H.EDGES, [HOBJECT n_parent]) = 1',
    '$heap_edge_owners(HOBJECT n_parent, H.EDGES, [HOBJECT n_weak]) = 0',
    'n_handle_parent = S.DESTRUCTION.HANDLES[n_parent]',
    'n_handle_weak = S.DESTRUCTION.HANDLES[n_weak]',
    'n_handle_child = S.DESTRUCTION.HANDLES[n_child]',
    '$(n_handle_child > n_handle_parent)',
    '$(n_handle_child > n_handle_weak)',
    'pexecutorfree_start = {HEAP H, MARKED eps, DETACHED eps, FAILED eps, UNKNOWN false}',
    '$executor_free_weak(S_endpoint, eps, n_parent)',
    '$executor_free_kind(S_endpoint, eps, n_parent) = 1',
    '$executor_free_kind(S_endpoint, [HOBJECT n_weak], n_parent) = 0',
    '$executor_free_kind(S_endpoint, eps, n_weak) = 1',
    'pexecutorfree_observer = $executor_free_force(S_endpoint, pexecutorfree_start, n_weak)',
    'pexecutorfree_observer.MARKED = [HOBJECT n_weak]',
    'pexecutorfree_observer.HEAP.NODES = H.NODES',
    'pexecutorfree_observer.HEAP.EDGES = H.EDGES',
    'pexecutorfree_observer.HEAP.ROOTS = H.ROOTS ++ [HOBJECT n_weak]',
    '$heap_owners(pexecutorfree_observer.HEAP, HOBJECT n_parent) = n_parent_owners',
    '$heap_owners(pexecutorfree_observer.HEAP, HOBJECT n_weak) = 3',
    '$heap_owners(pexecutorfree_observer.HEAP, HOBJECT n_child) = 1',
    '~$executor_free_weak(S_endpoint, pexecutorfree_observer.MARKED, n_parent)',
    'pexecutorfree_parent = $executor_free_force(S_endpoint, pexecutorfree_observer, n_parent)',
    'pexecutorfree_parent.MARKED = [HOBJECT n_parent, HOBJECT n_weak]',
    'pexecutorfree_parent.HEAP.EDGES = H.EDGES',
    'pexecutorfree_parent.HEAP.ROOTS = pexecutorfree_observer.HEAP.ROOTS',
    '$heap_owners(pexecutorfree_parent.HEAP, HOBJECT n_child) = 1',
    'pexecutorfree_tables = $executor_free_tables(S_endpoint, pexecutorfree_start)',
    'pexecutorfree_tables = pexecutorfree_start',
    'pexecutorfree_done = $executor_free_walk(S_endpoint, pexecutorfree_tables, S.DESTRUCTION.NEXT)',
    '~pexecutorfree_done.UNKNOWN',
    'pexecutorfree_done.HEAP.NODES = H.NODES',
    '(HOBJECT n_parent) <- pexecutorfree_done.MARKED',
    '(HOBJECT n_child) <- pexecutorfree_done.MARKED',
    'S_zero = $drive_steps(S, 0)',
    'S_zero.COMPLETION = BUDGET',
    'S_zero.TODO = S.TODO',
    'S_zero.ALLOCATIONS = S.ALLOCATIONS',
    'S_zero.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S, 1)',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = S_done',
    'S_done.OBJECTS = S.OBJECTS',
    'S_done.ALLOCATIONS = S.ALLOCATIONS',
    'S_done.GC = S.GC',
    '$heap_valid($heap_graph(S_done))',
]

LOWER = ['n_parent_owners = 2', *COMMON,
    '$(n_handle_weak < n_handle_parent)',
    'pexecutorfree_done.FAILED = (n_child)',
    '~((HOBJECT n_weak) <- pexecutorfree_done.MARKED)',
    '$heap_children(HOBJECT n_parent, pexecutorfree_done.HEAP.EDGES) = eps',
    '$heap_owners(pexecutorfree_done.HEAP, HOBJECT n_child) = 0',
    '''ptbytes_fatal = $ptascii("Couldn't execute method GcWeakOrderChild30::__destruct")''',
    'S_done.COMPLETION = REQUESTFATAL ($ptascii("Error")) ptbytes_fatal 0',
    'S_done.EXITSTATUS = 0',
    'preqbytes_fatal = $ptascii("Fatal error: ") ++ ptbytes_fatal ++ $ptascii(" in Unknown on line 0") ++ [10] ++ $ptascii("Stack trace:") ++ [10] ++ $ptascii("#0 {main}") ++ [10]',
    'S_done.EVENTS = S.EVENTS ++ [STDERR preqbytes_fatal]',
    'S_done.DESTRUCTION.CALLED = $destructor_all(0, |S_done.OBJECTS|)',
]


def normal(owners):
    return [f'n_parent_owners = {owners}', *COMMON,
        '$(n_handle_parent < n_handle_weak)',
        'pexecutorfree_done.FAILED = eps',
        '(HOBJECT n_weak) <- pexecutorfree_done.MARKED',
        '$heap_children(HOBJECT n_parent, pexecutorfree_done.HEAP.EDGES) = [HOBJECT n_child]',
        '$heap_owners(pexecutorfree_done.HEAP, HOBJECT n_child) = 1',
        'S_done = S_endpoint',
        'S_done.COMPLETION = NORMAL',
        'S_done.EVENTS = S.EVENTS',
    ]


HIGHER = normal(2)
for label, key, observer_kind, parent_kind, retired_kind in [
        ('map_observer', 'n_weak', 2, 1, 1),
        ('map_referent', 'n_parent', 1, 2, 0)]:
    HIGHER += [
        f'S_{label} = S_endpoint[.OBJECTS[n_child] = WEAKMAP ({{KEY {key}, VALUE (PINT 17), BEFORE eps, ORDER 0}})]',
        f'H_{label} = $heap_graph(S_{label})',
        f'$heap_valid(H_{label})',
        f'$weakmap_key_maps(S_{label}, S_{label}.ALLOCATIONS, {key}) = [n_child]',
        f'$executor_free_kind(S_{label}, eps, n_weak) = {observer_kind}',
        f'$executor_free_kind(S_{label}, eps, n_parent) = {parent_kind}',
        f'$executor_free_key_maps(S_{label}, eps, {key}) = [n_child]',
        f'$executor_free_kind(S_{label}, eps, n_child) = 1',
        f'pexecutorfree_map_{label} = $executor_free_force(S_{label}, {{HEAP H_{label}, MARKED eps, DETACHED eps, FAILED eps, UNKNOWN false}}, n_child)',
        f'~pexecutorfree_map_{label}.UNKNOWN /\\ pexecutorfree_map_{label}.FAILED = eps',
        f'pexecutorfree_map_{label}.MARKED = [HOBJECT n_child]',
        f'pexecutorfree_map_{label}.HEAP.EDGES = H_{label}.EDGES',
        f'$executor_free_key_maps(S_{label}, pexecutorfree_map_{label}.MARKED, {key}) = eps',
        f'$executor_free_kind(S_{label}, [HOBJECT n_weak, HOBJECT n_child], {key}) = {retired_kind}',
        f'pexecutorfree_{label} = $executor_free_force(S_{label}, {{HEAP H_{label}, MARKED eps, DETACHED eps, FAILED eps, UNKNOWN false}}, {key})',
        f'pexecutorfree_{label}.UNKNOWN',
        f'pexecutorfree_{label}.MARKED = eps',
        f'pexecutorfree_{label}.HEAP = H_{label}',
    ]
HIGHER += [
    'S_custom = S_endpoint[.OBJECTS[n_child] = WEAKMAP eps]',
    '$executor_free_kind(S_custom, eps, n_child) = 1',
    '$executor_free_kind(S_custom, [HOBJECT n_weak], n_child) = 1',
]

BOUND = normal(3) + [
    'S.ERRORHANDLER.CALLBACK = (POBJECT n_closure)',
    '$closure_callable(S_endpoint, n_closure)',
    '$node_children(S_endpoint, HOBJECT n_closure) = [HOBJECT n_parent]',
    '$heap_owners(H, HOBJECT n_closure) = 1',
    '$executor_free_kind(S_endpoint, pexecutorfree_parent.MARKED, n_closure) = 1',
    'pexecutorfree_bound = $executor_free_force(S_endpoint, pexecutorfree_parent, n_closure)',
    '~pexecutorfree_bound.UNKNOWN',
    'pexecutorfree_bound.FAILED = eps',
    '$heap_edge_owners(HOBJECT n_parent, pexecutorfree_bound.HEAP.EDGES, [HOBJECT n_closure]) = 0',
    '$heap_owners(pexecutorfree_bound.HEAP, HOBJECT n_parent) = 2',
    '$heap_children(HOBJECT n_parent, pexecutorfree_bound.HEAP.EDGES) = [HOBJECT n_child]',
    '$heap_owners(pexecutorfree_bound.HEAP, HOBJECT n_child) = 1',
    'S_hidden = S_endpoint[.ALLOCATIONS = $destruction_nodes_delete(S_endpoint.ALLOCATIONS, [HOBJECT n_parent])]',
    '~$closure_callable(S_hidden, n_closure)',
    'S_observed = S_endpoint[.OBJECTS[n_weak] = WEAKREFERENCE (n_closure)]',
    '$closure_callable(S_observed, n_closure)',
    '$heap_graph(S_observed) = H',
    '$executor_free_weak(S_observed, eps, n_closure)',
    '$executor_free_kind(S_observed, eps, n_closure) = 2',
    '$executor_free_kind(S_observed, [HOBJECT n_parent], n_closure) = 2',
    '$executor_free_kind(S_observed, [HOBJECT n_weak, HOBJECT n_parent], n_closure) = 1',
    'pexecutorfree_refusal = $executor_free_force(S_observed, pexecutorfree_start, n_closure)',
    'pexecutorfree_refusal.UNKNOWN',
    'pexecutorfree_refusal.MARKED = eps',
    'pexecutorfree_refusal.HEAP = H',
]

CASES = {name: {'source': sources.PATHS[source].read_text(), 'stage': STAGE,
                'checks': checks, 'timeout': 240}
         for name, source, checks in [
             ('observer-before-unregister-fatal', 'observer-lower', LOWER),
             ('unregister-before-parent-skip', 'observer-higher', HIGHER),
             ('bound-receiver-and-weak-closure-fence', 'bound-receiver', BOUND)]}
RECORDED = ordinary.RECORDED


def strict_recorded(command, directory, stem, environment, cap):
    return RECORDED([command[0], '--sl', *command[1:]], directory, stem, environment, cap)


runner.CASES = CASES
runner.recorded = strict_recorded
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if runner.run(args.case) else 1)
