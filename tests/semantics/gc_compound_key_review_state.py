#!/usr/bin/env python3
"""Independent source-reached compound Map-key owner and notification check."""
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fiber_state_review as review

source = (root / 'tests/semantics/gc_compound_map_key_multi_source.php').read_text()
stage = ('S.TODO = [EXECUTOR_RELEASE pexecutorqueue EXECUTOR_DONE] '
         '-- if S.DESTRUCTION.OPERATIONS = eps /\\ S.DESTRUCTION.CALLS = eps '
         '-- if S.DESTRUCTION.CLEANUPS = eps /\\ S.DESTRUCTION.RELEASES = eps')
checks = [
    '$call_task_valid(S, EXECUTOR_RELEASE pexecutorqueue EXECUTOR_DONE)',
    '$destruction_state_valid(S)',
    'S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.ITERATORS = eps',
    'S_global = $global_table_view(S)',
    '$lookup(S_global.ENV, $ptascii("compoundMultiOuter33")) = (n_outer_cell)',
    '$lookup(S_global.ENV, $ptascii("compoundMultiInner33")) = (n_inner_cell)',
    '$lookup(S_global.ENV, $ptascii("compoundMultiPlain33")) = (n_plain_cell)',
    '$lookup(S_global.ENV, $ptascii("compoundMultiSecond33")) = (n_second_cell)',
    'S.STORE[n_outer_cell] = DEFINED (POBJECT n_outer)',
    'S.STORE[n_inner_cell] = DEFINED (POBJECT n_inner)',
    'S.STORE[n_plain_cell] = DEFINED (POBJECT n_plain)',
    'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
    'S.OBJECTS[n_outer] = WEAKMAP (pweakmapentry_outer)',
    'S.OBJECTS[n_inner] = WEAKMAPENTRIES ([pweakmapentry_plain, pweakmapentry_second])',
    'pweakmapentry_outer.KEY = n_inner',
    'pweakmapentry_outer.VALUE = POBJECT n_value',
    'pweakmapentry_plain.KEY = n_plain /\\ pweakmapentry_plain.VALUE = POBJECT n_value',
    'pweakmapentry_second.KEY = n_second /\\ pweakmapentry_second.VALUE = POBJECT n_value',
    '$object_name(S, n_value) = $ptascii("GcCompoundMultiValue33")',
    'S_endpoint = S[.TODO = eps][.COMPLETION = pexecutorqueue.COMPLETION][.ORIGIN = pexecutorqueue.ORIGIN]',
    '$executor_free_endpoint(S_endpoint)',
    '$executor_allocator_fast(S_endpoint.REQUEST)',
    'H = $heap_graph(S_endpoint)',
    '$heap_valid(H)',
    '$heap_children(HOBJECT n_inner, H.EDGES) = [HOBJECT n_value, HOBJECT n_value]',
    '$heap_children(HOBJECT n_outer, H.EDGES) = [HOBJECT n_value]',
    '$heap_owners(H, HOBJECT n_value) = 3',
    '$executor_free_key_maps(S_endpoint, eps, n_inner) = [n_outer]',
    '$executor_free_kind(S_endpoint, eps, n_inner) = 1',
    'pexecutorfree_start = {HEAP H, MARKED eps, DETACHED eps, FAILED eps, UNKNOWN false}',
    'pexecutorfree_inner = $executor_free_force(S_endpoint, pexecutorfree_start, n_inner)',
    '~pexecutorfree_inner.UNKNOWN /\\ pexecutorfree_inner.FAILED = eps',
    '(HOBJECT n_inner) <- pexecutorfree_inner.MARKED',
    'pexecutorfree_inner.DETACHED = [(n_outer, n_inner)]',
    '$executor_free_live_maps(S_endpoint, pexecutorfree_inner.MARKED, pexecutorfree_inner.DETACHED, n_inner) = eps',
    '$executor_free_key_maps(S_endpoint, pexecutorfree_inner.MARKED, n_plain) = eps',
    '$executor_free_key_maps(S_endpoint, pexecutorfree_inner.MARKED, n_second) = eps',
    '$heap_children(HOBJECT n_inner, pexecutorfree_inner.HEAP.EDGES) = eps',
    '$heap_children(HOBJECT n_outer, pexecutorfree_inner.HEAP.EDGES) = eps',
    '$heap_owners(pexecutorfree_inner.HEAP, HOBJECT n_value) = 0',
    'S_zero = $drive_steps(S, 0)',
    'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
    'S_done = $drive_steps(S, 1)',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.EXITSTATUS = 0',
    'S_done.ALLOCATIONS = S.ALLOCATIONS /\\ S_done.OBJECTS = S.OBJECTS',
]
review.CASES = {'multi-entry-compound-key': {'source': source, 'stage': stage, 'checks': checks}}
if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=240) else 1)
