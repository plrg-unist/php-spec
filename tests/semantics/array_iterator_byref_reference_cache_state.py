#!/usr/bin/env python3
"""A key callback retargets a raw current cell before spread copies its row."""
from pathlib import Path
from types import SimpleNamespace

import array_iterator_byref_reference_cache_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial, seek
from array_generator_unpack_state_review import budget, finish, owners, public

SELECTED = ('array-iterator-byref-reference-cache-held',
            'array-iterator-byref-reference-cache-dropped')
AUTHOR = SimpleNamespace(CASES={name: cases.CASES[name] for name in SELECTED}, __file__=cases.__file__)

HELPERS = shared.HELPERS + r'''
dec $iterator_byref_cache_echo(pstate, ptbytes) : bool
def $iterator_byref_cache_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $iterator_byref_cache_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 330) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "key-start") :: ptask*
def $list_warning_frontier(S, 331) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "insert") :: ptask*
def $list_warning_frontier(S, 332) = $iterator_byref_cache_echo(S, $ptascii("B:"))
def $list_warning_frontier(S, 333) = $iterator_byref_cache_echo(S, $ptascii("R:"))
'''


def old_row(state, leaf=2):
    return [
        f'{state}.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf),ENTRY (KINT 1) (DIRECT (PINT 7))]',
        f'{state}.STORE[n_leaf] = DEFINED (PINT {leaf})',
        f'$node_children({state}, HARRAY n_old) = [HCELL n_leaf]',
        f'$node_children({state}, HCELL n_leaf) = eps',
    ]


def new_row(state, other=9):
    return [
        f'{state}.ARRAYS[n_new].ITEMS = [ENTRY (KINT 0) (ALIAS n_other),ENTRY (KINT 1) (DIRECT (PINT 19))]',
        f'{state}.STORE[n_other] = DEFINED (PINT {other})',
        f'$node_children({state}, HARRAY n_new) = [HCELL n_other]',
    ]


def common(program, path):
    checks = initial(program, path) + seek('S_initial', 330, 'S_cache') + [
        'S_cache.TODO = (ARRAY_ITERATOR parrayiterator_cached "key-start") :: ptask_tail*',
        'parrayiterator_cached.CURRENT = REFERENCE n_outer',
        'parrayiterator_cached.KEY = KNOWN PNULL',
        'parrayiterator_cached.OBJECT = n_object',
        'parrayiterator_cached.ARRAY = n_target',
        '$lookup(S_cache.ENV, $ptascii("row")) = (n_outer)',
        '$lookup(S_cache.ENV, $ptascii("leaf")) = (n_leaf)',
        '$lookup(S_cache.ENV, $ptascii("saved")) = (n_saved)',
        '$lookup(S_cache.ENV, $ptascii("it")) = (n_it)',
        'S_cache.STORE[n_outer] = DEFINED (PARRAY n_old)',
        'S_cache.STORE[n_saved] = DEFINED (PARRAY n_old)',
        'S_cache.STORE[n_it] = DEFINED (POBJECT n_object)',
        'n_outer =/= n_leaf',
        'n_outer <- S_cache.REFCELLS', 'n_leaf <- S_cache.REFCELLS',
        'S_cache.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8))]',
        '$array_iterator_source(S_cache, parrayiterator_cached)',
        '$array_iterator_valid(S_cache, parrayiterator_cached, "key-start")',
        '$array_iterator_ready(S_cache, parrayiterator_cached)',
        '$array_iterator_reference_cell(S_cache, n_outer) = (PARRAY n_old)',
        '$array_iterator_value(S_cache, REFERENCE n_outer) = eps',
        '$array_iterator_reference_table(S_cache, n_old)',
        '$array_iterator_current_value(S_cache, parrayiterator_cached, REFERENCE n_outer) = (PARRAY n_old)',
        '$node_children(S_cache, HCELL n_outer) = [HARRAY n_old]',
        '~$array_iterator_reference_away(S_cache, PARRAY n_target, n_target)',
        owners('S_cache', 'HOBJECT n_object', 2),
        owners('S_cache', 'HCELL n_outer', 2),
        owners('S_cache', 'HARRAY n_old', 2),
        owners('S_cache', 'HCELL n_leaf', 2),
    ] + old_row('S_cache') + public('S_cache')
    checks += seek('S_cache', 331, 'S_key') + [
        'S_key.TODO = (ARRAY_ITERATOR parrayiterator_key "insert") :: ptask_tail*',
        'parrayiterator_key.KEY = KNOWN pvalue_key',
        'parrayiterator_key = parrayiterator_cached[.KEY = KNOWN pvalue_key]',
        '$string_bytes(pvalue_key) = ($ptascii("ref"))',
        '$lookup(S_key.ENV, $ptascii("row")) = (n_outer)',
        '$lookup(S_key.ENV, $ptascii("other")) = (n_other)',
        'S_key.STORE[n_outer] = DEFINED (PARRAY n_new)',
        'n_new =/= n_old',
        'S_key.STORE[n_saved] = DEFINED (PARRAY n_old)',
        '$node_children(S_key, HCELL n_outer) = [HARRAY n_new]',
        '$array_iterator_reference_cell(S_key, n_outer) = (PARRAY n_new)',
        '$array_iterator_value(S_key, REFERENCE n_outer) = eps',
        '$array_iterator_reference_table(S_key, n_new)',
        '$array_iterator_current_value(S_key, parrayiterator_key, REFERENCE n_outer) = (PARRAY n_new)',
        '$array_iterator_ready(S_key, parrayiterator_key)',
        'S_key.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8))]',
        owners('S_key', 'HCELL n_outer', 2),
        owners('S_key', 'HARRAY n_old', 1),
        owners('S_key', 'HARRAY n_new', 1),
        owners('S_key', 'HCELL n_leaf', 2),
        owners('S_key', 'HCELL n_other', 2),
        'PhpStep: S_key ~> S_insert',
        'S_insert.TODO = (ARRAY_ITERATOR parrayiterator_key[.CURRENT = KNOWN PNULL][.KEY = KNOWN PNULL] "next-start") :: ptask_tail*',
        '$entry_lookup(S_insert.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("ref"))) = (DIRECT (PARRAY n_new))',
        '$node_children(S_insert, HARRAY n_target) = [HARRAY n_new]',
        'S_insert.STORE[n_outer] = DEFINED (PARRAY n_new)',
        owners('S_insert', 'HCELL n_outer', 1),
        owners('S_insert', 'HARRAY n_old', 1),
        owners('S_insert', 'HARRAY n_new', 2),
        owners('S_insert', 'HCELL n_other', 2),
    ] + old_row('S_key') + new_row('S_key') + public('S_key') + public('S_insert') + budget('S_key', 'S_insert_budget')
    checks += seek('S_insert', 332, 'S_spread') + [
        '$lookup(S_spread.ENV, $ptascii("out")) = (n_out)',
        'S_spread.STORE[n_out] = DEFINED (PARRAY n_target)',
        'S_spread.STORE[n_saved] = DEFINED (PARRAY n_old)',
        'S_spread.STORE[n_outer] = DEFINED (PARRAY n_new)',
        '$entry_lookup(S_spread.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("ref"))) = (DIRECT (PARRAY n_new))',
        'S_spread.ITERATORS = eps',
        owners('S_spread', 'HOBJECT n_object', 1),
        owners('S_spread', 'HARRAY n_old', 1),
        owners('S_spread', 'HARRAY n_new', 2),
        owners('S_spread', 'HCELL n_leaf', 2),
        owners('S_spread', 'HCELL n_other', 2),
    ] + old_row('S_spread') + new_row('S_spread') + public('S_spread')
    return checks


def held(program, path, stdout):
    checks = common(program, path) + seek('S_spread', 333, 'S_read') + [
        'S_read.STORE[n_out] = DEFINED (PARRAY n_target)',
        'S_read.STORE[n_saved] = DEFINED (PARRAY n_old)',
        'S_read.STORE[n_outer] = DEFINED (PARRAY n_new)',
        '$entry_lookup(S_read.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("ref"))) = (DIRECT (PARRAY n_copy))',
        r'n_copy =/= n_new /\ n_copy =/= n_old',
        'S_read.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 0) (ALIAS n_other),ENTRY (KINT 1) (DIRECT (PINT 88))]',
        '$node_children(S_read, HARRAY n_copy) = [HCELL n_other]',
        owners('S_read', 'HARRAY n_old', 1), owners('S_read', 'HARRAY n_new', 1),
        owners('S_read', 'HARRAY n_copy', 1), owners('S_read', 'HCELL n_leaf', 2),
        owners('S_read', 'HCELL n_other', 3),
    ] + old_row('S_read', 44) + new_row('S_read', 66) + public('S_read')
    return checks + finish('S_read', stdout, [
        'HOBJECT n_object', 'HCELL n_outer', 'HCELL n_leaf', 'HCELL n_other',
        'HARRAY n_old', 'HARRAY n_new', 'HARRAY n_copy', 'HARRAY n_target',
    ])


def dropped(program, path, stdout):
    checks = common(program, path) + seek('S_spread', 333, 'S_read') + [
        'S_read.STORE[n_out] = DEFINED (PARRAY n_target)',
        'S_read.STORE[n_saved] = DEFINED (PARRAY n_old)',
        'S_read.STORE[n_outer] = DEFINED (PARRAY n_new)',
        '$lookup(S_read.ENV, $ptascii("other")) = eps',
        '$entry_lookup(S_read.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("ref"))) = (DIRECT (PARRAY n_copy))',
        r'n_copy =/= n_new /\ n_copy =/= n_old',
        'S_read.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9)),ENTRY (KINT 1) (DIRECT (PINT 88))]',
        '$node_children(S_read, HARRAY n_copy) = eps',
        'S_read.STORE[n_other] = DEFINED (PINT 44)',
        owners('S_read', 'HARRAY n_old', 1), owners('S_read', 'HARRAY n_new', 1),
        owners('S_read', 'HARRAY n_copy', 1), owners('S_read', 'HCELL n_leaf', 2),
        owners('S_read', 'HCELL n_other', 1),
    ] + old_row('S_read') + new_row('S_read', 44) + public('S_read')
    return checks + finish('S_read', stdout, [
        'HOBJECT n_object', 'HCELL n_outer', 'HCELL n_leaf', 'HCELL n_other',
        'HARRAY n_old', 'HARRAY n_new', 'HARRAY n_copy', 'HARRAY n_target',
    ])


def conditions(name, program, path, stdout):
    return (held if name == SELECTED[0] else dropped)(program, path, stdout)


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(AUTHOR, conditions, HELPERS, extra_inputs=(
        Path(__file__), Path(__file__).with_name('array_aggregate_unpack_state_review.py'),
        Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
