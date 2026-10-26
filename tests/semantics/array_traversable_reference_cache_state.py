#!/usr/bin/env python3
"""A retained outside alias survives Iterator spread and selected array COW."""
from pathlib import Path
from types import SimpleNamespace

import array_traversable_reference_cache_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial, seek
from array_generator_unpack_state_review import budget, finish, owners, public

CASE = 'array-traversable-reference-cache-alias-retained'
AUTHOR = SimpleNamespace(CASES={CASE: cases.CASES[CASE]}, __file__=cases.__file__)

HELPERS = shared.HELPERS + r'''
dec $reference_cache_echo(pstate, ptbytes) : bool
def $reference_cache_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $reference_cache_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 190) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "key-start") :: ptask*
def $list_warning_frontier(S, 191) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "insert") :: ptask*
def $list_warning_frontier(S, 192) = $reference_cache_echo(S, $ptascii("B:"))
def $list_warning_frontier(S, 193) = $reference_cache_echo(S, $ptascii("R:"))
'''


def pair(state, value, second=7):
    return [
        f'{state}.ARRAYS[n_row].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf),ENTRY (KINT 1) (DIRECT (PINT {second}))]',
        f'{state}.STORE[n_leaf] = DEFINED (PINT {value})',
        f'$node_children({state}, HARRAY n_row) = [HCELL n_leaf]',
        f'$node_children({state}, HCELL n_leaf) = eps',
    ]


def conditions(name, program, path, stdout):
    assert name == CASE
    checks = initial(program, path) + seek('S_initial', 190, 'S_cache') + [
        'S_cache.TODO = (ARRAY_ITERATOR parrayiterator_cached "key-start") :: ptask_tail*',
        '$lookup(S_cache.ENV, $ptascii("leaf")) = (n_leaf)',
        '$lookup(S_cache.ENV, $ptascii("row")) = (n_row_cell)',
        'S_cache.STORE[n_row_cell] = DEFINED (PARRAY n_row)',
        '$lookup(S_cache.ENV, $ptascii("it")) = (n_it)',
        'S_cache.STORE[n_it] = DEFINED (POBJECT n_object)',
        'parrayiterator_cached.OBJECT = n_object',
        'parrayiterator_cached.ARRAY = n_target',
        'parrayiterator_cached.CURRENT = KNOWN (PARRAY n_row)',
        'parrayiterator_cached.KEY = KNOWN PNULL',
        'S_cache.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8))]',
        '(HCELL n_leaf) <- S_cache.ALLOCATIONS',
        'n_leaf <- S_cache.REFCELLS',
        '$array_iterator_source(S_cache, parrayiterator_cached)',
        '$array_iterator_ready(S_cache, parrayiterator_cached)',
        '$array_iterator_reference_table(S_cache, n_row)',
        '$array_iterator_current_value(S_cache, parrayiterator_cached, KNOWN (PARRAY n_row)) = (PARRAY n_row)',
        '$array_iterator_value(S_cache, KNOWN (PARRAY n_row)) = eps',
        '~$array_iterator_reference_table(S_cache[.REFCELLS = eps], n_row)',
        '~$array_iterator_reference_away(S_cache, PARRAY n_target, n_target)',
        owners('S_cache', 'HARRAY n_row', 2),
        owners('S_cache', 'HCELL n_leaf', 2),
        owners('S_cache', 'HOBJECT n_object', 2),
    ] + pair('S_cache', 2) + public('S_cache')
    checks += seek('S_cache', 191, 'S_key') + [
        'S_key.TODO = (ARRAY_ITERATOR parrayiterator_key "insert") :: ptask_tail*',
        'parrayiterator_key = parrayiterator_cached[.KEY = KNOWN pvalue_key]',
        '$string_bytes(pvalue_key) = ($ptascii("ref"))',
        '$array_iterator_ready(S_key, parrayiterator_key)',
        'S_key.ARRAYS[n_row].ITEMS = S_cache.ARRAYS[n_row].ITEMS',
        owners('S_key', 'HARRAY n_row', 2), owners('S_key', 'HCELL n_leaf', 2),
        'PhpStep: S_key ~> S_insert',
        'S_insert.TODO = (ARRAY_ITERATOR parrayiterator_key[.CURRENT = KNOWN PNULL][.KEY = KNOWN PNULL] "next-start") :: ptask_tail*',
        '$entry_lookup(S_insert.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("ref"))) = (DIRECT (PARRAY n_row))',
        '$node_children(S_insert, HARRAY n_target) = [HARRAY n_row]',
        'S_insert.ARRAYS[n_row] = S_key.ARRAYS[n_row]',
        owners('S_insert', 'HARRAY n_row', 2), owners('S_insert', 'HCELL n_leaf', 2),
    ] + pair('S_key', 3) + public('S_key') + public('S_insert') + budget('S_key', 'S_insert_budget')
    checks += seek('S_insert', 192, 'S_spread') + [
        '$lookup(S_spread.ENV, $ptascii("out")) = (n_out)',
        'S_spread.STORE[n_out] = DEFINED (PARRAY n_target)',
        '$entry_lookup(S_spread.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("ref"))) = (DIRECT (PARRAY n_row))',
        'S_spread.ITERATORS = eps',
        '$duplicate_item(S_spread, n_row, ALIAS n_leaf) = ALIAS n_leaf',
        owners('S_spread', 'HARRAY n_row', 2), owners('S_spread', 'HCELL n_leaf', 2),
        owners('S_spread', 'HOBJECT n_object', 1),
    ] + pair('S_spread', 3) + public('S_spread')
    checks += seek('S_spread', 193, 'S_read') + [
        'S_read.STORE[n_row_cell] = DEFINED (PARRAY n_row)',
        'S_read.STORE[n_out] = DEFINED (PARRAY n_target)',
        '$lookup(S_read.ENV, $ptascii("leaf")) = (n_leaf)',
        '$entry_lookup(S_read.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("ref"))) = (DIRECT (PARRAY n_copy))',
        'n_copy =/= n_row',
        'S_read.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf),ENTRY (KINT 1) (DIRECT (PINT 88))]',
        '$node_children(S_read, HARRAY n_copy) = [HCELL n_leaf]',
        owners('S_read', 'HARRAY n_row', 1), owners('S_read', 'HARRAY n_copy', 1),
        owners('S_read', 'HARRAY n_target', 1), owners('S_read', 'HCELL n_leaf', 3),
    ] + pair('S_read', 44) + public('S_read')
    return checks + finish('S_read', stdout, [
        'HOBJECT n_object', 'HCELL n_leaf', 'HARRAY n_row', 'HARRAY n_copy', 'HARRAY n_target',
    ])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(AUTHOR, conditions, HELPERS, extra_inputs=(
        Path(__file__), Path(__file__).with_name('array_aggregate_unpack_state_review.py'),
        Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
