#!/usr/bin/env python3
"""A key throw retains the raw outer reference until actual spread cleanup."""
from pathlib import Path
from types import SimpleNamespace

import array_iterator_byref_reference_cache_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial, seek
from array_generator_unpack_state_review import budget, finish, owners, public

CASE = 'array-iterator-byref-reference-cache-key-throw'
PEER = SimpleNamespace(CASES={CASE: cases.CASES[CASE]}, __file__=cases.__file__)

HELPERS = shared.HELPERS + r'''
dec $iterator_byref_reference_echo(pstate, ptbytes) : bool
def $iterator_byref_reference_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $iterator_byref_reference_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 340) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "current") :: ptask*
  -- if S.RESULT = REFERENCE n
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 341) = $iterator_byref_reference_echo(S, $ptascii("Q:"))
def $list_warning_frontier(S, 342) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_ITERATOR parrayiterator "key") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 343) = $iterator_byref_reference_echo(S, $ptascii("T:"))
'''


def graph(state):
    return [
        f'{state}.STORE[n_outer] = DEFINED (PARRAY n_row)',
        f'{state}.ARRAYS[n_row].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf),ENTRY (KINT 1) (DIRECT (PINT 7))]',
        f'{state}.STORE[n_leaf] = DEFINED (PINT 2)',
        f'$node_children({state}, HCELL n_outer) = [HARRAY n_row]',
        f'$node_children({state}, HARRAY n_row) = [HCELL n_leaf]',
        f'$node_children({state}, HCELL n_leaf) = eps',
    ]


def conditions(name, program, path, stdout):
    assert name == CASE
    checks = initial(program, path) + seek('S_initial', 340, 'S_current') + [
        'S_current.TODO = (ARRAY_ITERATOR parrayiterator "current") :: ptask_tail*',
        'S_current.RESULT = REFERENCE n_outer',
        'parrayiterator.OBJECT = n_object', 'parrayiterator.ARRAY = n_target',
        'parrayiterator.CURRENT = KNOWN PNULL', 'parrayiterator.KEY = KNOWN PNULL',
        'parrayiterator.ITERATOR = n_iterator',
        'S_current.ITERATORS = [OBJECTITER n_iterator n_object 0 false]',
        '$lookup(S_current.ENV, $ptascii("row")) = (n_outer)',
        '$lookup(S_current.ENV, $ptascii("leaf")) = (n_leaf)',
        'n_outer =/= n_leaf',
        'n_outer <- S_current.REFCELLS', 'n_leaf <- S_current.REFCELLS',
        '$lookup(S_current.ENV, $ptascii("it")) = (n_it)',
        'S_current.STORE[n_it] = DEFINED (POBJECT n_object)',
        '$lookup(S_current.ENV, $ptascii("watch")) = (n_watch)',
        'S_current.STORE[n_watch] = DEFINED (POBJECT n_observer)',
        '$lookup(S_current.ENV, $ptascii("second")) = (n_second)',
        'S_current.STORE[n_second] = DEFINED (POBJECT n_exception)',
        '$lookup(S_current.ENV, $ptascii("dest")) = (n_dest)',
        '$lookup(S_current.ENV, $ptascii("later")) = (n_later)',
        'S_current.STORE[n_dest] = DEFINED (PINT 99)',
        'S_current.STORE[n_later] = DEFINED (PINT 7)',
        'S_current.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8))]',
        '$array_iterator_source(S_current, parrayiterator)',
        '$array_iterator_valid(S_current, parrayiterator, "current")',
        '$array_iterator_ready(S_current, parrayiterator)',
        '$array_iterator_value(S_current, REFERENCE n_outer) = eps',
        '$array_iterator_reference_cell(S_current, n_outer) = (PARRAY n_row)',
        '$array_iterator_current_value(S_current, parrayiterator, REFERENCE n_outer) = (PARRAY n_row)',
        '$task_nodes(ARRAY_ITERATOR parrayiterator "current") = [HARRAY n_target, HOBJECT n_object]',
        '$operand_nodes(S_current.RESULT) = [HCELL n_outer]',
        '$node_children(S_current, HOBJECT n_object) = eps',
        '$list_warning_outputs(S_current.EVENTS) = $ptascii("P:1;W;V0;C;")',
        owners('S_current', 'HOBJECT n_object', 2), owners('S_current', 'HCELL n_outer', 2),
        owners('S_current', 'HARRAY n_row', 1), owners('S_current', 'HCELL n_leaf', 2),
        owners('S_current', 'HARRAY n_target', 1),
        'PhpStep: S_current ~> S_cached',
        'parrayiterator_cached = parrayiterator[.CURRENT = REFERENCE n_outer]',
        'S_cached.TODO = (ARRAY_ITERATOR parrayiterator_cached "key-start") :: ptask_tail*',
        'S_cached.RESULT = KNOWN PNULL', 'S_cached.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_cached.STORE = S_current.STORE', 'S_cached.ARRAYS = S_current.ARRAYS',
        'S_cached.ALLOCATIONS = S_current.ALLOCATIONS',
        '$task_nodes(ARRAY_ITERATOR parrayiterator_cached "key-start") = [HARRAY n_target, HOBJECT n_object, HCELL n_outer]',
        '$array_iterator_ready(S_cached, parrayiterator_cached)',
        owners('S_cached', 'HCELL n_outer', 2), owners('S_cached', 'HARRAY n_row', 1),
        owners('S_cached', 'HCELL n_leaf', 2),
    ] + graph('S_current') + public('S_current') + public('S_cached') + budget('S_current', 'S_capture_budget')
    # This metadata-only helper control leaves the inner scalar reference and
    # physical graph intact; it supplies no additional PHP-source agreement.
    checks += [
        'S_unmarked = S_cached[.REFCELLS = [n_leaf]]',
        '$heap_graph(S_unmarked) = $heap_graph(S_cached)',
        '$array_iterator_reference_table(S_unmarked, n_row)',
        '$array_iterator_current_value(S_unmarked, parrayiterator_cached, REFERENCE n_outer) = eps',
    ]
    checks += seek('S_cached', 341, 'S_key') + [
        'S_key.CURRENT = (pcallcontext_key)',
        'S_key.FRAMES = pframe_key :: pframe_caller*',
        'pframe_key.TODO = (ARRAY_ITERATOR parrayiterator_cached "key") :: ptask_tail*',
        '$array_iterator_target(S_key, parrayiterator_cached, pcallcontext_key.TARGET, "key")',
        'S_key_global = $global_table_view(S_key)',
        '$lookup(S_key_global.ENV, $ptascii("it")) = eps',
        '$lookup(S_key_global.ENV, $ptascii("row")) = eps',
        '$lookup(S_key_global.ENV, $ptascii("leaf")) = eps',
        '$weakref_get(S_key, n_observer) = POBJECT n_object',
        'S_key.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8))]',
        '$list_warning_outputs(S_key.EVENTS) = $ptascii("P:1;W;V0;C;K;")',
        owners('S_key', 'HOBJECT n_object', 1), owners('S_key', 'HCELL n_outer', 1),
        owners('S_key', 'HARRAY n_row', 1), owners('S_key', 'HCELL n_leaf', 1),
        owners('S_key', 'HARRAY n_target', 1),
    ] + graph('S_key') + public('S_key')
    checks += seek('S_key', 342, 'S_pending') + [
        'S_pending.TODO = (THROW_SEARCH n_exception) :: (ARRAY_ITERATOR parrayiterator_cached "key") :: ptask_tail*',
        '$array_iterator_source(S_pending, parrayiterator_cached)',
        '$array_iterator_valid(S_pending, parrayiterator_cached, "key")',
        '$array_iterator_ready(S_pending, parrayiterator_cached)',
        '$array_iterator_current_value(S_pending, parrayiterator_cached, REFERENCE n_outer) = (PARRAY n_row)',
        'S_pending.STORE[n_dest] = DEFINED (PINT 99)',
        'S_pending.STORE[n_later] = DEFINED (PINT 7)',
        'S_pending.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8))]',
        '$lookup(S_pending.ENV, $ptascii("it")) = eps',
        '$lookup(S_pending.ENV, $ptascii("row")) = eps',
        '$lookup(S_pending.ENV, $ptascii("leaf")) = eps',
        '$throwable_field(S_pending, n_exception, "previous") = PNULL',
        '$throwable_field(S_pending, n_exception, "trace") = PARRAY n_trace',
        'S_pending.ARRAYS[n_trace].ITEMS = eps',
        '$list_warning_outputs(S_pending.EVENTS) = $ptascii("P:1;W;V0;C;K;Q:1::;")',
        owners('S_pending', 'HOBJECT n_object', 1), owners('S_pending', 'HCELL n_outer', 1),
        owners('S_pending', 'HARRAY n_row', 1), owners('S_pending', 'HCELL n_leaf', 1),
        owners('S_pending', 'HARRAY n_target', 1),
        'S_popped = S_pending[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
        'S_direct = $return_discard(S_popped, ARRAY_ITERATOR parrayiterator_cached "key")',
        'PhpStep: S_pending ~> S_raw',
        'S_raw = S_direct',
        'S_raw.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        'S_raw.ITERATORS = $iterator_remove(S_pending.ITERATORS, n_iterator)',
        'S_raw.ALLOCATIONS = S_pending.ALLOCATIONS',
        'S_raw.ARRAYS = S_pending.ARRAYS', 'S_raw.STORE = S_pending.STORE',
        'S_raw.EVENTS = S_pending.EVENTS', 'S_raw.DESTRUCTION = S_pending.DESTRUCTION',
        owners('S_raw', 'HOBJECT n_object', 0), owners('S_raw', 'HCELL n_outer', 0),
        owners('S_raw', 'HARRAY n_target', 0), owners('S_raw', 'HARRAY n_row', 1),
        owners('S_raw', 'HCELL n_leaf', 1),
    ] + graph('S_pending') + public('S_pending') + public('S_raw') + budget('S_pending', 'S_discard_budget')
    # Scalar cache cleanup is atomic in the methodless driver domain. Observe
    # the actual one-step public result, without inventing a storage-pin task.
    checks += [
        'S_retired = S_discard_budget_one[.COMPLETION = NORMAL]',
        'S_retired.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        '$weakref_get(S_retired, n_observer) = PNULL',
        *[f'~(({node}) <- S_retired.ALLOCATIONS)' for node in [
            'HOBJECT n_object', 'HCELL n_outer', 'HARRAY n_row', 'HCELL n_leaf', 'HARRAY n_target',
        ]],
        owners('S_retired', 'HCELL n_outer', 0), owners('S_retired', 'HARRAY n_row', 0),
        owners('S_retired', 'HCELL n_leaf', 0),
    ] + public('S_retired')
    checks += seek('S_retired', 343, 'S_caught') + [
        '$lookup(S_caught.ENV, $ptascii("e")) = (n_caught)',
        'S_caught.STORE[n_caught] = DEFINED (POBJECT n_exception)',
        'S_caught.STORE[n_second] = DEFINED (POBJECT n_exception)',
        'S_caught.STORE[n_dest] = DEFINED (PINT 99)',
        'S_caught.STORE[n_later] = DEFINED (PINT 7)',
        '$weakref_get(S_caught, n_observer) = PNULL',
    ] + public('S_caught')
    return checks + finish('S_caught', stdout, [
        'HOBJECT n_object', 'HOBJECT n_exception', 'HOBJECT n_observer',
        'HCELL n_outer', 'HARRAY n_row', 'HCELL n_leaf', 'HARRAY n_target',
    ])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(PEER, conditions, HELPERS, extra_inputs=(
        Path(__file__),
        Path(__file__).with_name('array_aggregate_unpack_state_review.py'),
        Path(__file__).with_name('array_generator_unpack_state_review.py'),
    )) else 1)
