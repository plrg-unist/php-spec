#!/usr/bin/env python3
"""A genuine direct foreach fetch captures one Key and one outer-array owner."""
import argparse
import json
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc56_peer_finite_foreach_exhaustion.php').read_text()
STAGE = (
    'S.TODO = (FOREACH_NEXT n (HOBJECT n_map) statement (porigin) z) :: ptask_tail* '
    '-- if $iterator_lookup(S.ITERATORS, n) = (WEAKMAPITER n n_map 2 n_keys*)')
CHUNKS = (['L|', 's|', '17', '|', 'o|', '23', '|', 'a|', '1', '|', '9', '|', 'E|']
          + ['1', '|'] * 2 + ['A|'] + ['1', '|'] * 4
          + ['M|'] + ['1', '|'] * 3 + ['K|'] + ['1', '|'] * 2
          + ['k|', '1', '|', 'Z|'] + ['1', '|'] * 4 + ['F|'] + ['1', '|'] * 2)
ENDING = 'S_done.EVENTS = [' + ', '.join(
    'OUTPUT $ptascii(' + json.dumps(chunk) + ')' for chunk in CHUNKS) + ']'
CHECKS = [
    'S.CURRENT = eps /\\ S.FRAMES = eps',
    'statement = NStmtForeach expression_iterable expression_key (BOOLEAN false) expression_value (SEQUENCE statement_body*) (BOOLEAN false) metadata',
    'S.ITERATORS = [WEAKMAPITER n n_map 2 n_keys*]',
    'n_keys* = [n_scalar_key, n_first_key, n_last_key]',
    '$(n_last_key < n_first_key) /\\ $(n_first_key < n_scalar_key)',
    '$lookup(S.ENV, $ptascii("map56Peer")) = (n_map_cell)',
    'S.STORE[n_map_cell] = DEFINED (POBJECT n_map)',
    '$lookup(S.ENV, $ptascii("loopKey56Peer")) = (n_key_cell)',
    'S.STORE[n_key_cell] = DEFINED (POBJECT n_first_key)',
    '$lookup(S.ENV, $ptascii("loopValue56Peer")) = (n_value_cell)',
    'S.STORE[n_value_cell] = DEFINED (POBJECT n_first_value)',
    '$lookup(S.ENV, $ptascii("lastKey56Peer")) = (n_last_key_cell)',
    'pweakmapentry* = $weakmap_entries_contents(S, n_map)',
    'pweakmapentry* = [pweakmapentry_scalar, pweakmapentry_first, pweakmapentry_last]',
    'pweakmapentry_scalar.KEY = n_scalar_key /\\ pweakmapentry_scalar.VALUE = PINT 17',
    'pweakmapentry_first.KEY = n_first_key /\\ pweakmapentry_first.VALUE = POBJECT n_first_value',
    'pweakmapentry_last.KEY = n_last_key',
    'pweakmapentry_last.VALUE = PARRAY n_outer',
    '$weakmap_entries_cursor_next(pweakmapentry*, 2, n_keys*) = (pweakmapentry_last, 3)',
    'S.ARRAYS[n_outer].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_inner)), ENTRY (KINT 1) (DIRECT (PARRAY n_inner))]',
    'S.ARRAYS[n_inner].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_last_value)), ENTRY (KINT 1) (DIRECT (PINT 9)), ENTRY (KINT 2) (DIRECT (POBJECT n_last_value))]',
    '$node_children(S, HOBJECT n_map) = [HOBJECT n_first_value, HARRAY n_outer]',
    '$node_children(S, HARRAY n_outer) = [HARRAY n_inner, HARRAY n_inner]',
    '$node_children(S, HARRAY n_inner) = [HOBJECT n_last_value, HOBJECT n_last_value]',
    '$node_children(S, HOBJECT n_first_value) = [HOBJECT n_first_child]',
    '$node_children(S, HOBJECT n_last_value) = [HOBJECT n_last_child]',
    '$objectprops_at(S.OBJECTPROPS, n_first_value) = ([ppropertyslot_tag, ppropertyslot_child])',
    '$task_nodes(FOREACH_NEXT n (HOBJECT n_map) statement (porigin) z) = [HOBJECT n_map]',
    '$heap_owners($heap_graph(S), HOBJECT n_map) = 2',
    '$heap_owners($heap_graph(S), HOBJECT n_scalar_key) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_first_key) = 2',
    '$heap_owners($heap_graph(S), HOBJECT n_last_key) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_first_value) = 2',
    '$heap_owners($heap_graph(S), HARRAY n_outer) = 1',
    '$heap_owners($heap_graph(S), HARRAY n_inner) = 2',
    '$heap_owners($heap_graph(S), HOBJECT n_last_value) = 2',
    '$heap_owners($heap_graph(S), HOBJECT n_first_child) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_last_child) = 1',
    '$weakmap_finite_foreach_storage(S, n_map)',
    '$weakmap_finite_foreach_source(S, n_map, statement)',
    '~$weakmap_finite_foreach_source(S, n_map, NStmtForeach (NExprUnaryPlus expression_iterable metadata) expression_key (BOOLEAN false) expression_value (SEQUENCE statement_body*) (BOOLEAN false) metadata)',
    '~$weakmap_finite_foreach_source(S[.REFCELLS = n_map_cell :: S.REFCELLS], n_map, statement)',
    'S_rebound = S[.STORE[n_map_cell] = DEFINED PNULL]',
    '~$weakmap_finite_foreach_source(S_rebound, n_map, statement)',
    '$weakmap_finite_foreach_storage(S_rebound, n_map)',
    '$call_task_valid(S_rebound, FOREACH_NEXT n (HOBJECT n_map) statement (porigin) z)',
    '$heap_owners($heap_graph(S_rebound), HOBJECT n_map) = 1',
    '~$weakmap_foreach_storage_valid(S, n_map)',
    '~$weakmap_entries_foreach_storage(S, n_map)',
    '~$weakmap_entries_child_storage(S, n_map)',
    '$weakmap_entries_child_storage(S[.ITERATORS = eps], n_map)',
    '$heap_graph(S[.ITERATORS = eps]) = $heap_graph(S)',
    '~$weakmap_entries_table_valid(S, n_map, eps)',
    '~$weakmap_entries_teardown_table(S, n_map)',
    '~$weakmap_entries_access_storage(S, n_map, true)',
    '~$weakmap_entries_notice_storage(S, n_map, eps, true)',
    '~$weakmap_entries_reference_storage(S, n_map)',
    '~$weakmap_iterator_factory_storage(S, n_map)',
    # Constructed views test held-Key refusal and disjoint old-domain admission.
    'S_unheld = S[.STORE[n_last_key_cell] = DEFINED PNULL]',
    '$heap_owners($heap_graph(S_unheld), HOBJECT n_last_key) = 0',
    '~$weakmap_entries_keys_held(S_unheld, pweakmapentry*)',
    '~$weakmap_finite_foreach_storage(S_unheld, n_map)',
    '~$call_task_valid(S_unheld, FOREACH_NEXT n (HOBJECT n_map) statement (porigin) z)',
    'S_leaf = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS, n_first_value, [ppropertyslot_tag, ppropertyslot_child[.STATE = PROP_VALUE (DIRECT PNULL)]])]',
    'S_legacy = S_leaf[.OBJECTS[n_map] = WEAKMAP (pweakmapentry_first)][.ITERATORS = [OBJECTITER n n_map 0 false]]',
    '$weakmap_foreach_storage_valid(S_legacy, n_map)',
    '$weakmap_foreach_byvalue_storage(S_legacy, n_map)',
    '~$weakmap_finite_foreach_storage(S_legacy, n_map)',
    '$weakmap_foreach_cursor_valid(S_legacy, n, n_map, 0)',
    '$call_task_valid(S, FOREACH_NEXT n (HOBJECT n_map) statement (porigin) z)',
    '~$call_task_valid(S, FOREACH_NEXT n (HOBJECT n_last_key) statement (porigin) z)',
    '~$call_task_valid(S, FOREACH_NEXT n (HOBJECT n_map) statement eps z)',
    '$call_descriptors_valid(S) /\\ $heap_valid($heap_graph(S))',
    'S_missing = S[.ITERATORS = eps]',
    '$heap_graph(S_missing) = $heap_graph(S)',
    '~$call_task_valid(S_missing, FOREACH_NEXT n (HOBJECT n_map) statement (porigin) z)',
    'S_range = S[.ITERATORS = [WEAKMAPITER n n_map 4 n_keys*]]',
    '~$call_task_valid(S_range, FOREACH_NEXT n (HOBJECT n_map) statement (porigin) z)',
    'S_duplicate = S[.ITERATORS = [WEAKMAPITER n n_map 2 ([n_scalar_key, n_scalar_key, n_last_key])]]',
    '~$call_task_valid(S_duplicate, FOREACH_NEXT n (HOBJECT n_map) statement (porigin) z)',
    'S_order = S[.ITERATORS = [WEAKMAPITER n n_map 2 ([n_first_key, n_scalar_key, n_last_key])]]',
    '~$call_task_valid(S_order, FOREACH_NEXT n (HOBJECT n_map) statement (porigin) z)',
    'S_mode = S[.ITERATORS = [WEAKMAPREFITER n n_map 2 n_keys*]]',
    '~$call_task_valid(S_mode, FOREACH_NEXT n (HOBJECT n_map) statement (porigin) z)',
    'S_extra = S[.ITERATORS = S.ITERATORS ++ [WEAKMAPITER S.NEXTITER n_map 0 n_keys*]][.NEXTITER = $(S.NEXTITER + 1)]',
    '~$weakmap_finite_foreach_storage(S_extra, n_map)',
    '~$call_task_valid(S_extra, FOREACH_NEXT n (HOBJECT n_map) statement (porigin) z)',
    '~$weakmap_finite_foreach_storage(S[.GC.WORKER = (n_map)], n_map)',
    'S_zero = $drive_steps(S, 0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_fetch = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
    '$iterator_lookup(S_fetch.ITERATORS, n) = (WEAKMAPITER n n_map 3 n_keys*)',
    '$weakmap_entries_contents(S_fetch, n_map) = pweakmapentry*',
    '$heap_owners($heap_graph(S_fetch), HOBJECT n_map) = 2',
    '$heap_owners($heap_graph(S_fetch), HOBJECT n_last_key) = 2',
    '$heap_owners($heap_graph(S_fetch), HARRAY n_outer) = 2',
    '$heap_owners($heap_graph(S_fetch), HARRAY n_inner) = 2',
    '$heap_owners($heap_graph(S_fetch), HOBJECT n_last_value) = 2',
    '$heap_owners($heap_graph(S_fetch), HOBJECT n_last_child) = 1',
    '$heap_owners($heap_graph(S_fetch), HOBJECT n_first_key) = 2',
    '$heap_owners($heap_graph(S_fetch), HOBJECT n_first_value) = 2',
    '$heap_count(HOBJECT n_map, $tasks_nodes(S_fetch.TODO)) = 1',
    '$heap_count(HOBJECT n_last_key, $tasks_nodes(S_fetch.TODO)) = 1',
    '$heap_count(HARRAY n_outer, $tasks_nodes(S_fetch.TODO)) = 1',
    '$heap_count(HARRAY n_inner, $tasks_nodes(S_fetch.TODO)) = 0',
    'S_fetch.ARRAYS = S.ARRAYS /\\ S_fetch.OBJECTPROPS = S.OBJECTPROPS',
    'S_fetch.EVENTS = S.EVENTS',
    '$call_descriptors_valid(S_fetch) /\\ $heap_valid($heap_graph(S_fetch))',
    'S_paused = $drive_steps(S, 1)',
    'S_paused = S_fetch[.COMPLETION = BUDGET]',
    'S_done = $drive_steps(S, 4000)',
    '$drive_steps(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    'S_done.ITERATORS = eps',
    ENDING,
    '~((HOBJECT n_map) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_scalar_key) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_first_key) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_last_key) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_first_value) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_last_value) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_first_child) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_last_child) <- S_done.ALLOCATIONS)',
    '~((HARRAY n_outer) <- S_done.ALLOCATIONS)',
    '~((HARRAY n_inner) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {'finite-foreach-captured-owner-transfer': {
    'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=360) else 1)
