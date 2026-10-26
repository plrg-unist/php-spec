#!/usr/bin/env python3
"""A raw Iterator current cell and its scalar alias survive real DATA destruction."""
from pathlib import Path
from types import SimpleNamespace

import array_iterator_byref_destructor_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial, seek
from array_generator_unpack_state_review import budget, finish, owners, public

SELECTED = ('array-iterator-byref-destructor-last-data',
            'array-iterator-byref-destructor-retained-owner')
AUTHOR = SimpleNamespace(CASES={name: cases.CASES[name] for name in SELECTED}, __file__=cases.__file__)

HELPERS = shared.HELPERS + r'''
dec $a61_echo(pstate, ptbytes) : bool
def $a61_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a61_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 510) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "key-start") :: ptask*
def $list_warning_frontier(S, 511) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "insert") :: ptask*
def $list_warning_frontier(S, 512) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "finish") :: ptask*
def $list_warning_frontier(S, 513) = $a61_echo(S, $ptascii("D:"))
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
def $list_warning_frontier(S, 514) = true
  -- if S.TODO = (ARRAY_ITERATOR_RELEASE parrayiterator "normal") :: ptask*
def $list_warning_frontier(S, 515) = $a61_echo(S, $ptascii("R:"))
def $list_warning_frontier(S, 516) = $a61_echo(S, $ptascii("B:"))
'''


def old_row(state):
    return [
        f'{state}.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf),ENTRY (KINT 1) (DIRECT (PINT 7))]',
        f'{state}.STORE[n_leaf] = DEFINED (PINT 2)',
        f'$node_children({state}, HARRAY n_old) = [HCELL n_leaf]',
    ]


def new_row(state, value):
    return [
        f'{state}.ARRAYS[n_new].ITEMS = [ENTRY (KINT 0) (ALIAS n_alias),ENTRY (KINT 1) (DIRECT (PINT 19))]',
        f'{state}.STORE[n_alias] = DEFINED (PINT {value})',
        f'$node_children({state}, HARRAY n_new) = [HCELL n_alias]',
    ]


def builder(state, tail=None):
    entries = '[ENTRY (KINT 4) (DIRECT (PINT 8)),ENTRY (KSTRING ($ptascii("row"))) (DIRECT (PARRAY n_new))]'
    if tail is not None:
        entries = entries[:-1] + f',ENTRY (KINT 5) (DIRECT (PINT {tail}))]'
    return [f'{state}.ARRAYS[n_target].ITEMS = {entries}',
            f'$entry_lookup({state}.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("row"))) = (DIRECT (PARRAY n_new))']


def common(program, path, object_owners):
    checks = initial(program, path) + seek('S_initial', 510, 'S_cache') + [
        'S_cache.TODO = (ARRAY_ITERATOR parrayiterator_cached "key-start") :: ptask_tail*',
        'parrayiterator_cached.CURRENT = REFERENCE n_outer',
        'parrayiterator_cached.KEY = KNOWN PNULL',
        'parrayiterator_cached.OBJECT = n_object',
        'parrayiterator_cached.ARRAY = n_target',
        '$lookup(S_cache.ENV, $ptascii("row")) = (n_outer)',
        '$lookup(S_cache.ENV, $ptascii("leaf")) = (n_leaf)',
        '$lookup(S_cache.ENV, $ptascii("alias")) = (n_alias)',
        '$lookup(S_cache.ENV, $ptascii("saved")) = (n_saved)',
        '$lookup(S_cache.ENV, $ptascii("it")) = ' + ('eps' if object_owners == 1 else '(n_it)'),
        '$lookup(S_cache.ENV, $ptascii("dest")) = (n_dest)',
        '$lookup(S_cache.ENV, $ptascii("tail")) = (n_tail)',
        '$lookup(S_cache.ENV, $ptascii("watch")) = (n_watch)',
        'S_cache.STORE[n_watch] = DEFINED (POBJECT n_observer)',
        'S_cache.STORE[n_outer] = DEFINED (PARRAY n_old)',
        'S_cache.STORE[n_saved] = DEFINED (PARRAY n_old)',
        'S_cache.STORE[n_dest] = DEFINED (PINT 99)',
        'S_cache.STORE[n_tail] = DEFINED (PINT 7)',
        'S_cache.STORE[n_alias] = DEFINED (PINT 9)',
        'n_outer <- S_cache.REFCELLS', 'n_leaf <- S_cache.REFCELLS',
        'S_cache.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8))]',
        '$array_iterator_destructor_byref_current(S_cache, parrayiterator_cached)',
        '$array_iterator_ready(S_cache, parrayiterator_cached)',
        '$array_iterator_reference_cell(S_cache, n_outer) = (PARRAY n_old)',
        '$array_iterator_value(S_cache, REFERENCE n_outer) = eps',
        '$array_iterator_current_value(S_cache, parrayiterator_cached, REFERENCE n_outer) = (PARRAY n_old)',
        '$weakref_get(S_cache, n_observer) = POBJECT n_object',
        owners('S_cache', 'HOBJECT n_object', object_owners),
        owners('S_cache', 'HCELL n_outer', 2),
        owners('S_cache', 'HARRAY n_old', 2),
        owners('S_cache', 'HCELL n_leaf', 2),
    ] + old_row('S_cache') + public('S_cache')
    checks += seek('S_cache', 511, 'S_key') + [
        'S_key.TODO = (ARRAY_ITERATOR parrayiterator_key "insert") :: ptask_tail*',
        'parrayiterator_key.KEY = KNOWN pvalue_key',
        'parrayiterator_key = parrayiterator_cached[.KEY = KNOWN pvalue_key]',
        '$string_bytes(pvalue_key) = ($ptascii("row"))',
        'S_key.STORE[n_outer] = DEFINED (PARRAY n_new)',
        'n_new =/= n_old',
        'S_key.STORE[n_saved] = DEFINED (PARRAY n_old)',
        '$array_iterator_reference_cell(S_key, n_outer) = (PARRAY n_new)',
        '$array_iterator_current_value(S_key, parrayiterator_key, REFERENCE n_outer) = (PARRAY n_new)',
        '$array_iterator_ready(S_key, parrayiterator_key)',
        'S_key.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8))]',
        owners('S_key', 'HOBJECT n_object', object_owners),
        owners('S_key', 'HCELL n_outer', 2),
        owners('S_key', 'HARRAY n_old', 1),
        owners('S_key', 'HARRAY n_new', 1),
        owners('S_key', 'HCELL n_leaf', 2),
        owners('S_key', 'HCELL n_alias', 2),
        'PhpStep: S_key ~> S_insert',
        'S_insert.TODO = (ARRAY_ITERATOR parrayiterator_key[.CURRENT = KNOWN PNULL][.KEY = KNOWN PNULL] "next-start") :: ptask_tail*',
        '$entry_lookup(S_insert.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("row"))) = (DIRECT (PARRAY n_new))',
        '$array_iterator_current_builder(S_insert, parrayiterator_key[.CURRENT = KNOWN PNULL][.KEY = KNOWN PNULL])',
        owners('S_insert', 'HARRAY n_target', 1),
        owners('S_insert', 'HCELL n_outer', 1),
        owners('S_insert', 'HARRAY n_old', 1),
        owners('S_insert', 'HARRAY n_new', 2),
        owners('S_insert', 'HCELL n_alias', 2),
    ] + old_row('S_key') + new_row('S_key', 9) + public('S_key') + public('S_insert') + budget('S_key', 'S_insert_budget')
    checks += seek('S_insert', 512, 'S_finish') + [
        'S_finish.TODO = (ARRAY_ITERATOR parrayiterator_finish "finish") :: ptask_finish_tail*',
        'parrayiterator_finish = parrayiterator_key[.CURRENT = KNOWN PNULL][.KEY = KNOWN PNULL]',
        '$array_iterator_valid(S_finish, parrayiterator_finish, "finish")',
        '$array_iterator_ready(S_finish, parrayiterator_finish)',
        '$array_iterator_destructor_byref_current(S_finish, parrayiterator_finish)',
        '$array_iterator_current_builder(S_finish, parrayiterator_finish)',
        'S_finish.STORE[n_dest] = DEFINED (PINT 99)',
        'S_finish.STORE[n_tail] = DEFINED (PINT 7)',
        owners('S_finish', 'HOBJECT n_object', object_owners),
        owners('S_finish', 'HARRAY n_target', 1),
        owners('S_finish', 'HARRAY n_old', 1),
        owners('S_finish', 'HARRAY n_new', 2),
        owners('S_finish', 'HCELL n_alias', 2),
    ] + builder('S_finish') + old_row('S_finish') + new_row('S_finish', 9) + public('S_finish')
    return checks


def last_data(program, path, stdout):
    checks = common(program, path, 1) + [
        'PhpStep: S_finish ~> S_raw',
        'S_raw.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (ARRAY_ITERATOR_RELEASE parrayiterator_finish "normal") :: ptask_finish_tail*',
        'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_object)]',
        'pdestructionrelease.USER',
        'S_raw.ITERATORS = eps',
        '$array_iterator_release_valid(S_raw, parrayiterator_finish, "normal")',
        '$task_nodes(ARRAY_ITERATOR_RELEASE parrayiterator_finish "normal") = [HARRAY n_target]',
        owners('S_raw', 'HOBJECT n_object', 1),
        owners('S_raw', 'HARRAY n_target', 1),
        owners('S_raw', 'HARRAY n_new', 2),
    ] + public('S_raw') + budget('S_finish', 'S_finish_budget') + seek('S_finish', 513, 'S_dtor') + [
        'S_dtor.CURRENT = (pcallcontext_d)',
        '$destructor_context_call(pcallcontext_d, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object',
        'pdestructorcall.SITE = $origin_child((parrayiterator_finish.SITE), [PCFIELD 1])',
        'pdestructorcall.LINE = parrayiterator_finish.LINE',
        'pdestructorcall.USER',
        '$destructor_call_live(S_dtor, pdestructorcall)',
        '$weakref_get(S_dtor, n_observer) = POBJECT n_object',
        'S_dtor.STORE[n_dest] = DEFINED (PINT 99)',
        'S_dtor.STORE[n_tail] = DEFINED (PINT 7)',
        'S_dtor.STORE[n_alias] = DEFINED (PINT 9)',
        owners('S_dtor', 'HARRAY n_target', 1),
        owners('S_dtor', 'HARRAY n_new', 2),
    ] + builder('S_dtor') + new_row('S_dtor', 9) + public('S_dtor')
    checks += seek('S_dtor', 514, 'S_released') + [
        'S_released.TODO = (ARRAY_ITERATOR_RELEASE parrayiterator_finish "normal") :: ptask_finish_tail*',
        '~((HOBJECT n_object) <- S_released.ALLOCATIONS)',
        '$weakref_get(S_released, n_observer) = PNULL',
        'S_released.STORE[n_dest] = DEFINED (PINT 99)',
        'S_released.STORE[n_tail] = DEFINED (PINT 20)',
        'S_released.STORE[n_alias] = DEFINED (PINT 42)',
        '$array_iterator_release_valid(S_released, parrayiterator_finish, "normal")',
        '$array_iterator_destructor_byref_current(S_released, parrayiterator_finish)',
        '$array_iterator_release_builder(S_released, parrayiterator_finish)',
        '~$array_iterator_source(S_released, parrayiterator_finish)',
        owners('S_released', 'HARRAY n_target', 1),
        owners('S_released', 'HARRAY n_old', 1),
        owners('S_released', 'HARRAY n_new', 2),
        owners('S_released', 'HCELL n_alias', 2),
        'PhpStep: S_released ~> S_next',
        'S_next.TODO = (ARRAY_NEXT n_target parrayiterator_finish.TAIL) :: ptask_finish_tail*',
        'S_next.STORE[n_tail] = DEFINED (PINT 20)',
    ] + builder('S_released') + old_row('S_released') + new_row('S_released', 42) + public('S_released') + public('S_next') + budget('S_released', 'S_release_budget')
    checks += seek('S_released', 515, 'S_read') + [
        'S_read.STORE[n_dest] = DEFINED (PARRAY n_target)',
        'S_read.STORE[n_tail] = DEFINED (PINT 21)',
        '$weakref_get(S_read, n_observer) = PNULL',
        owners('S_read', 'HARRAY n_target', 1),
        owners('S_read', 'HARRAY n_old', 1),
        owners('S_read', 'HARRAY n_new', 2),
        owners('S_read', 'HCELL n_alias', 2),
    ] + builder('S_read', 20) + old_row('S_read') + new_row('S_read', 42) + public('S_read')
    return checks + finish('S_read', stdout, [
        'HOBJECT n_object', 'HOBJECT n_observer', 'HCELL n_outer',
        'HCELL n_leaf', 'HCELL n_alias', 'HARRAY n_old', 'HARRAY n_new', 'HARRAY n_target',
    ])


def retained(program, path, stdout):
    checks = common(program, path, 2) + seek('S_finish', 516, 'S_before') + [
        '$lookup(S_before.ENV, $ptascii("it")) = (n_it)',
        'S_before.STORE[n_it] = DEFINED (POBJECT n_object)',
        'S_before.STORE[n_dest] = DEFINED (PARRAY n_target)',
        'S_before.STORE[n_tail] = DEFINED (PINT 8)',
        'S_before.STORE[n_alias] = DEFINED (PINT 9)',
        '$weakref_get(S_before, n_observer) = POBJECT n_object',
        '$list_warning_outputs(S_before.EVENTS) = $ptascii("P:1;W;V0;C;K;N;V1;")',
        owners('S_before', 'HOBJECT n_object', 1),
        owners('S_before', 'HARRAY n_target', 1),
        owners('S_before', 'HARRAY n_new', 2),
        owners('S_before', 'HCELL n_alias', 2),
    ] + builder('S_before', 7) + old_row('S_before') + new_row('S_before', 9) + public('S_before') + budget('S_finish', 'S_retained_finish_budget')
    checks += seek('S_before', 513, 'S_dtor') + [
        'S_dtor.CURRENT = (pcallcontext_d)',
        '$destructor_context_call(pcallcontext_d, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object',
        '$destructor_call_live(S_dtor, pdestructorcall)',
        'S_dtor_global = $global_table_view(S_dtor)',
        '$lookup(S_dtor_global.ENV, $ptascii("it")) = eps',
        '$weakref_get(S_dtor, n_observer) = POBJECT n_object',
        'S_dtor.STORE[n_dest] = DEFINED (PARRAY n_target)',
        'S_dtor.STORE[n_tail] = DEFINED (PINT 8)',
        'S_dtor.STORE[n_alias] = DEFINED (PINT 9)',
        owners('S_dtor', 'HARRAY n_target', 1),
        owners('S_dtor', 'HARRAY n_new', 2),
    ] + builder('S_dtor', 7) + new_row('S_dtor', 9) + public('S_dtor')
    checks += seek('S_dtor', 515, 'S_read') + [
        '~((HOBJECT n_object) <- S_read.ALLOCATIONS)',
        '$weakref_get(S_read, n_observer) = PNULL',
        'S_read.STORE[n_dest] = DEFINED (PARRAY n_target)',
        'S_read.STORE[n_tail] = DEFINED (PINT 20)',
        'S_read.STORE[n_alias] = DEFINED (PINT 42)',
        owners('S_read', 'HARRAY n_target', 1),
        owners('S_read', 'HARRAY n_old', 1),
        owners('S_read', 'HARRAY n_new', 2),
        owners('S_read', 'HCELL n_alias', 2),
    ] + builder('S_read', 7) + old_row('S_read') + new_row('S_read', 42) + public('S_read')
    return checks + finish('S_read', stdout, [
        'HOBJECT n_object', 'HOBJECT n_observer', 'HCELL n_outer',
        'HCELL n_leaf', 'HCELL n_alias', 'HARRAY n_old', 'HARRAY n_new', 'HARRAY n_target',
    ])


def conditions(name, program, path, stdout):
    return last_data(program, path, stdout) if name == SELECTED[0] else retained(program, path, stdout)


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(AUTHOR, conditions, HELPERS, extra_inputs=(
        Path(__file__), Path(__file__).with_name('array_aggregate_unpack_state_review.py'),
        Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
