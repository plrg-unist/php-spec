#!/usr/bin/env python3
"""Nested cached values preserve physical child edges across roots and COW."""
import array_traversable_nested_cache_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial, seek
from array_generator_unpack_state_review import budget, finish, owners, public
from array_traversable_nested_cache_state_review import HELPERS

HELPERS += r'''
def $list_warning_frontier(S, 160) = true
  -- if S.TODO = (ARRAY_UNPACK n phpType13* z) :: ptask*
def $list_warning_frontier(S, 161) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "key-start") :: ptask*
def $list_warning_frontier(S, 162) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "insert") :: ptask*
def $list_warning_frontier(S, 163) = $nested_cache_echo(S, $ptascii("R:"))
def $list_warning_frontier(S, 164) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask*
  -- if S.OBJECTS[parraygenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_PAUSED
def $list_warning_frontier(S, 165) = $nested_cache_echo(S, $ptascii("N;"))
  -- if S.CURRENT = (pcallcontext)
def $list_warning_frontier(S, 166) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask*
  -- if S.OBJECTS[parraygenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $list_warning_frontier(S, 167) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "data-released") :: ptask*
def $list_warning_frontier(S, 168) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "input-released") :: ptask*
'''


def pair(state, array, first, second=7):
    return f'{state}.ARRAYS[{array}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT {first})),ENTRY (KINT 1) (DIRECT (PINT {second}))]'


def graph(state, root, left, right):
    return f'{state}.ARRAYS[{root}].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY {left})),ENTRY (KINT 1) (DIRECT (PARRAY {right})),ENTRY (KINT 2) (DIRECT (PARRAY n_fixed)),ENTRY (KINT 3) (DIRECT (PARRAY n_empty))]'


def entry(program, path):
    return initial(program, path) + seek('S_initial', 160, 'S_pre') + [
        'S_pre.TODO = (ARRAY_UNPACK n_target phpType13* z) :: ptask_tail*',
        'S_pre.RESULT = VARIABLE ($ptascii("it")) z',
        '$lookup(S_pre.ENV, $ptascii("it")) = (n_it)',
        'S_pre.STORE[n_it] = DEFINED (POBJECT n_object)',
        '$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf_cell)',
        'S_pre.STORE[n_leaf_cell] = DEFINED (PARRAY n_leaf)',
        '$lookup(S_pre.ENV, $ptascii("row")) = (n_row)',
        'S_pre.STORE[n_row] = DEFINED (PARRAY n_old)',
        'S_pre.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf)),ENTRY (KINT 1) (DIRECT (PARRAY n_leaf)),ENTRY (KINT 2) (DIRECT (PARRAY n_fixed)),ENTRY (KINT 3) (DIRECT (PARRAY n_empty))]',
        'S_pre.ARRAYS[n_fixed].ITEMS = [ENTRY (KSTRING ($ptascii("fixed"))) (DIRECT (PARRAY n_pool_leaf))]',
        pair('S_pre', 'n_leaf', 2), pair('S_pre', 'n_pool_leaf', 5, 9),
        'S_pre.ARRAYS[n_empty].ITEMS = eps', '$array_immutable(S_pre, n_empty)',
        'S_pre.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8))]',
        *[f'$heap_count(HARRAY {node}, $pools_nodes(S_pre.POOLS)) = 0' for node in ['n_target', 'n_old', 'n_leaf']],
        *[f'$heap_count(HARRAY {node}, $pools_nodes(S_pre.POOLS)) = 1' for node in ['n_fixed', 'n_pool_leaf', 'n_empty']],
        owners('S_pre', 'HARRAY n_old', 2), owners('S_pre', 'HARRAY n_leaf', 3),
        owners('S_pre', 'HARRAY n_fixed', 2), owners('S_pre', 'HARRAY n_pool_leaf', 2),
        owners('S_pre', 'HARRAY n_empty', 2), owners('S_pre', 'HARRAY n_target', 1),
        owners('S_pre', 'HOBJECT n_object', 1),
        '$array_iterator_table(S_pre, n_old)', '$array_iterator_table(S_pre, n_leaf)',
        '$array_iterator_value(S_pre, KNOWN (PARRAY n_old)) = (PARRAY n_old)',
        '$array_iterator_value_away(S_pre, PARRAY n_old, n_target)',
        '~$array_iterator_value_away(S_pre, PARRAY n_target, n_target)',
        '$array_iterator_value_away(S_pre, PINT 8, n_target)',
    ] + public('S_pre')


def pool_finish(state, stdout, retired):
    return finish(state, stdout, retired) + [
        *[f'(HARRAY {node}) <- S_done.ALLOCATIONS' for node in ['n_fixed', 'n_pool_leaf', 'n_empty']],
        owners('S_done', 'HARRAY n_fixed', 1), owners('S_done', 'HARRAY n_pool_leaf', 2),
        owners('S_done', 'HARRAY n_empty', 1),
        'S_done.ARRAYS[n_fixed].ITEMS = S_pre.ARRAYS[n_fixed].ITEMS',
        'S_done.ARRAYS[n_pool_leaf].ITEMS = S_pre.ARRAYS[n_pool_leaf].ITEMS',
        'S_done.ARRAYS[n_empty].ITEMS = eps',
    ]


def iterator_checks(program, path, stdout):
    checks = entry(program, path) + [
        '$lookup(S_pre.ENV, $ptascii("outside")) = (n_row)',
        '$lookup(S_pre.ENV, $ptascii("before")) = (n_before)',
        'S_pre.STORE[n_before] = DEFINED (PARRAY n_old)', 'n_row <- S_pre.REFCELLS',
        owners('S_pre', 'HCELL n_row', 2),
        '$array_iterator_plan(S_pre) = (parrayiterator)',
        'parrayiterator.ARRAY = n_target', 'parrayiterator.OBJECT = n_object',
        'PhpStep: S_pre ~> S_active',
        'S_active.TODO = (ARRAY_ITERATOR parrayiterator "rewind-start") :: ptask_tail*',
        owners('S_active', 'HOBJECT n_object', 2),
    ] + budget('S_pre', 'S_entry_budget') + seek('S_active', 161, 'S_cache') + [
        'S_cache.TODO = (ARRAY_ITERATOR parrayiterator_cached "key-start") :: ptask_tail*',
        'parrayiterator_cached = parrayiterator[.CURRENT = REFERENCE n_row]',
        '$array_iterator_ready(S_cache, parrayiterator_cached)',
        '$array_iterator_value(S_cache, parrayiterator_cached.CURRENT) = (PARRAY n_old)',
        owners('S_cache', 'HCELL n_row', 3), owners('S_cache', 'HARRAY n_old', 2),
        owners('S_cache', 'HARRAY n_leaf', 3), owners('S_cache', 'HARRAY n_fixed', 2),
    ] + public('S_cache') + seek('S_cache', 162, 'S_key') + [
        'S_key.TODO = (ARRAY_ITERATOR parrayiterator_key "insert") :: ptask_tail*',
        'parrayiterator_key.CURRENT = REFERENCE n_row',
        'parrayiterator_key.KEY = KNOWN pvalue_key', '$string_bytes(pvalue_key) = ($ptascii("tree"))',
        'S_key.STORE[n_row] = DEFINED (PARRAY n_live)', 'n_live =/= n_old',
        'S_key.ARRAYS[n_live].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_key_leaf)),ENTRY (KINT 1) (DIRECT (PARRAY n_leaf)),ENTRY (KINT 2) (DIRECT (PARRAY n_fixed)),ENTRY (KINT 3) (DIRECT (PARRAY n_empty))]',
        'n_key_leaf =/= n_leaf', pair('S_key', 'n_key_leaf', 44), pair('S_key', 'n_leaf', 2),
        graph('S_key', 'n_old', 'n_leaf', 'n_leaf'),
        '$array_iterator_value(S_key, parrayiterator_key.CURRENT) = (PARRAY n_live)',
        '$array_iterator_ready(S_key, parrayiterator_key)',
        owners('S_key', 'HCELL n_row', 3), owners('S_key', 'HARRAY n_old', 1),
        owners('S_key', 'HARRAY n_live', 1), owners('S_key', 'HARRAY n_key_leaf', 1),
        owners('S_key', 'HARRAY n_leaf', 4), owners('S_key', 'HARRAY n_fixed', 3),
        owners('S_key', 'HARRAY n_pool_leaf', 2), owners('S_key', 'HARRAY n_empty', 3),
        'PhpStep: S_key ~> S_insert',
        'S_insert.TODO = (ARRAY_ITERATOR parrayiterator_key[.CURRENT = KNOWN PNULL][.KEY = KNOWN PNULL] "next-start") :: ptask_tail*',
        '$entry_lookup(S_insert.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("tree"))) = (DIRECT (PARRAY n_live))',
        owners('S_insert', 'HCELL n_row', 2), owners('S_insert', 'HARRAY n_live', 2),
        owners('S_insert', 'HARRAY n_leaf', 4), owners('S_insert', 'HARRAY n_fixed', 3),
    ] + public('S_insert') + budget('S_key', 'S_insert_budget') + seek('S_insert', 163, 'S_read') + [
        '$lookup(S_read.ENV, $ptascii("saved")) = (n_saved)',
        'S_read.STORE[n_saved] = DEFINED (PARRAY n_target)',
        '$lookup(S_read.ENV, $ptascii("out")) = (n_out)',
        'S_read.STORE[n_out] = DEFINED (PARRAY n_out_array)', 'n_out_array =/= n_target',
        '$entry_lookup(S_read.ARRAYS[n_out_array].ITEMS, KSTRING ($ptascii("tree"))) = (DIRECT (PARRAY n_out_tree))',
        'n_out_tree =/= n_live',
        'S_read.ARRAYS[n_out_tree].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_out_leaf)),ENTRY (KINT 1) (DIRECT (PARRAY n_leaf)),ENTRY (KINT 2) (DIRECT (PARRAY n_fixed)),ENTRY (KINT 3) (DIRECT (PARRAY n_empty))]',
        'n_out_leaf =/= n_key_leaf', pair('S_read', 'n_out_leaf', 44, 88), pair('S_read', 'n_key_leaf', 44),
        'S_read.STORE[n_row] = DEFINED (PARRAY n_current)', 'n_current =/= n_live',
        'S_read.ARRAYS[n_current].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_key_leaf)),ENTRY (KINT 1) (DIRECT (PARRAY n_outside_leaf)),ENTRY (KINT 2) (DIRECT (PARRAY n_fixed)),ENTRY (KINT 3) (DIRECT (PARRAY n_empty))]',
        'n_outside_leaf =/= n_leaf', pair('S_read', 'n_outside_leaf', 66),
        graph('S_read', 'n_old', 'n_leaf', 'n_leaf'), graph('S_read', 'n_live', 'n_key_leaf', 'n_leaf'),
        owners('S_read', 'HARRAY n_leaf', 5), owners('S_read', 'HARRAY n_key_leaf', 2),
        owners('S_read', 'HARRAY n_fixed', 5), owners('S_read', 'HARRAY n_pool_leaf', 2),
        owners('S_read', 'HARRAY n_empty', 5), owners('S_read', 'HCELL n_row', 2),
        'S_read.ITERATORS = eps', owners('S_read', 'HOBJECT n_object', 1),
    ] + public('S_read')
    return checks + pool_finish('S_read', stdout, ['HOBJECT n_object', 'HCELL n_row', 'HARRAY n_target',
        'HARRAY n_old', 'HARRAY n_leaf', 'HARRAY n_live', 'HARRAY n_key_leaf', 'HARRAY n_current',
        'HARRAY n_outside_leaf', 'HARRAY n_out_array', 'HARRAY n_out_tree', 'HARRAY n_out_leaf'])


def generator_checks(program, path, stdout):
    checks = entry(program, path) + [
        'S_pre.OBJECTS[n_object] = GENERATOR pgenerator_initial',
        'pgenerator_initial.FRAME = (pframe_generator)', 'pframe_generator.LOCALS = (psymboltable_generator)',
        '$lookup(psymboltable_generator.ENV, $ptascii("local")) = (n_local)',
        'S_pre.STORE[n_local] = DEFINED (PARRAY n_old)',
        '$array_generator_plan(S_pre) = (parraygenerator)',
        'parraygenerator.ARRAY = n_target', 'parraygenerator.OBJECT = n_object',
        'PhpStep: S_pre ~> S_active',
        'S_active.TODO = (ARRAY_GENERATOR parraygenerator "rewind") :: ptask_tail*',
        owners('S_active', 'HOBJECT n_object', 2),
    ] + budget('S_pre', 'S_entry_budget') + seek('S_active', 164, 'S_first') + [
        'S_first.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask_tail*',
        'S_first.OBJECTS[n_object] = GENERATOR pgenerator_first',
        'pgenerator_first.VALUE = (PARRAY n_old)', 'pgenerator_first.REFCELL = eps',
        '$string_bytes($generator_cached_value(S_first, n_object, true)) = ($ptascii("first"))',
        '$array_generator_ready(S_first, parraygenerator)',
        '$lookup(S_first.ENV, $ptascii("it")) = eps', '~((HCELL n_it) <- S_first.ALLOCATIONS)',
        owners('S_first', 'HOBJECT n_object', 1), owners('S_first', 'HARRAY n_old', 3),
        owners('S_first', 'HARRAY n_leaf', 3), owners('S_first', 'HARRAY n_fixed', 2),
        'PhpStep: S_first ~> S_insert',
        'S_insert.TODO = (ARRAY_GENERATOR parraygenerator "next") :: ptask_tail*',
        '$entry_lookup(S_insert.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("first"))) = (DIRECT (PARRAY n_old))',
        owners('S_insert', 'HARRAY n_old', 4), owners('S_insert', 'HARRAY n_leaf', 3),
    ] + public('S_insert') + budget('S_first', 'S_insert_budget') + seek('S_insert', 165, 'S_body') + [
        'S_body.OBJECTS[n_object] = GENERATOR pgenerator_running',
        'pgenerator_running.PHASE = GENERATOR_RUNNING', 'pgenerator_running.VALUE = (PARRAY n_old)',
        'S_body.STORE[n_local] = DEFINED (PARRAY n_old)',
        owners('S_body', 'HARRAY n_old', 4), owners('S_body', 'HARRAY n_leaf', 3),
    ] + public('S_body') + seek('S_body', 166, 'S_closed') + [
        'S_closed.OBJECTS[n_object] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED', 'pgenerator_closed.VALUE = (PARRAY n_last)',
        'pgenerator_closed.FRAME = eps', 'pgenerator_closed.REFCELL = eps',
        'n_last =/= n_old',
        'S_closed.ARRAYS[n_last].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_last_leaf)),ENTRY (KINT 1) (DIRECT (PARRAY n_leaf)),ENTRY (KINT 2) (DIRECT (PARRAY n_fixed)),ENTRY (KINT 3) (DIRECT (PARRAY n_empty))]',
        'n_last_leaf =/= n_leaf', pair('S_closed', 'n_last_leaf', 44),
        graph('S_closed', 'n_old', 'n_leaf', 'n_leaf'), pair('S_closed', 'n_leaf', 2),
        '$entry_lookup(S_closed.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("second"))) = (DIRECT (PARRAY n_last))',
        '~((HCELL n_local) <- S_closed.ALLOCATIONS)',
        owners('S_closed', 'HARRAY n_old', 2), owners('S_closed', 'HARRAY n_last', 2),
        owners('S_closed', 'HARRAY n_leaf', 4), owners('S_closed', 'HARRAY n_last_leaf', 1),
        owners('S_closed', 'HARRAY n_fixed', 3), owners('S_closed', 'HARRAY n_pool_leaf', 2),
        '$array_generator_ready(S_closed, parraygenerator)',
    ] + public('S_closed') + seek('S_closed', 167, 'S_data') + [
        '~((HOBJECT n_object) <- S_data.ALLOCATIONS)',
        '$array_generator_history(S_data, parraygenerator)', '~$array_generator_source(S_data, parraygenerator)',
        owners('S_data', 'HARRAY n_last', 1), owners('S_data', 'HARRAY n_old', 2),
        owners('S_data', 'HARRAY n_leaf', 4), owners('S_data', 'HARRAY n_fixed', 3),
    ] + public('S_data') + seek('S_data', 168, 'S_input') + [
        '$array_generator_nodes(parraygenerator, "input-released") = [HARRAY n_target]',
    ] + seek('S_input', 163, 'S_read') + [
        '$lookup(S_read.ENV, $ptascii("saved")) = (n_saved)',
        'S_read.STORE[n_saved] = DEFINED (PARRAY n_target)',
        '$lookup(S_read.ENV, $ptascii("out")) = (n_out)',
        'S_read.STORE[n_out] = DEFINED (PARRAY n_out_array)', 'n_out_array =/= n_target',
        '$entry_lookup(S_read.ARRAYS[n_out_array].ITEMS, KSTRING ($ptascii("first"))) = (DIRECT (PARRAY n_first_out))',
        '$entry_lookup(S_read.ARRAYS[n_out_array].ITEMS, KSTRING ($ptascii("second"))) = (DIRECT (PARRAY n_second_out))',
        'n_first_out =/= n_old', 'n_second_out =/= n_last',
        'S_read.ARRAYS[n_first_out].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf)),ENTRY (KINT 1) (DIRECT (PARRAY n_first_leaf)),ENTRY (KINT 2) (DIRECT (PARRAY n_fixed)),ENTRY (KINT 3) (DIRECT (PARRAY n_empty))]',
        'S_read.ARRAYS[n_second_out].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_second_leaf)),ENTRY (KINT 1) (DIRECT (PARRAY n_leaf)),ENTRY (KINT 2) (DIRECT (PARRAY n_fixed)),ENTRY (KINT 3) (DIRECT (PARRAY n_empty))]',
        'n_first_leaf =/= n_leaf', 'n_second_leaf =/= n_last_leaf',
        pair('S_read', 'n_first_leaf', 2, 66), pair('S_read', 'n_second_leaf', 44, 88),
        pair('S_read', 'n_leaf', 2), pair('S_read', 'n_last_leaf', 44),
        owners('S_read', 'HARRAY n_leaf', 6), owners('S_read', 'HARRAY n_fixed', 5),
        owners('S_read', 'HARRAY n_pool_leaf', 2), owners('S_read', 'HARRAY n_empty', 5),
        owners('S_read', 'HARRAY n_old', 2), owners('S_read', 'HARRAY n_last', 1),
    ] + public('S_read')
    return checks + pool_finish('S_read', stdout, ['HOBJECT n_object', 'HCELL n_local', 'HARRAY n_target',
        'HARRAY n_old', 'HARRAY n_leaf', 'HARRAY n_last', 'HARRAY n_last_leaf', 'HARRAY n_out_array',
        'HARRAY n_first_out', 'HARRAY n_first_leaf', 'HARRAY n_second_out', 'HARRAY n_second_leaf'])


def conditions(name, program, path, stdout):
    return iterator_checks(program, path, stdout) if name.endswith('iterator-reference') else generator_checks(program, path, stdout)


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
