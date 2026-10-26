#!/usr/bin/env python3
"""Reached normal Iterator spread keeps and retires one declared array field."""
from pathlib import Path
from types import SimpleNamespace

import array_iterator_owned_field_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial, seek
from array_generator_unpack_state_review import budget, finish, owners, public

SELECTED = ('array-iterator-owned-field-last-data',
            'array-iterator-owned-field-retained-owner')
AUTHOR = SimpleNamespace(CASES={name: cases.CASES[name] for name in SELECTED},
                         __file__=cases.__file__)

HELPERS = shared.HELPERS + r'''
dec $a62_echo(pstate, ptbytes) : bool
def $a62_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a62_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 710) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "key-start") :: ptask*
def $list_warning_frontier(S, 711) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "insert") :: ptask*
def $list_warning_frontier(S, 712) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "finish") :: ptask*
def $list_warning_frontier(S, 713) = $a62_echo(S, $ptascii("D:"))
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
def $list_warning_frontier(S, 714) = $a62_echo(S, $ptascii("M:"))
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
def $list_warning_frontier(S, 715) = true
  -- if S.TODO = (ARRAY_ITERATOR_RELEASE parrayiterator "normal") :: ptask*
def $list_warning_frontier(S, 716) = $a62_echo(S, $ptascii("R:"))
def $list_warning_frontier(S, 717) = $a62_echo(S, $ptascii("B:"))
'''


def old_row(state):
    return [
        f'{state}.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_old_child)),ENTRY (KINT 1) (ALIAS n_leaf),ENTRY (KINT 2) (DIRECT (PINT 7))]',
        f'{state}.ARRAYS[n_old_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 3))]',
        f'$node_children({state}, HARRAY n_old) = [HARRAY n_old_child,HCELL n_leaf]',
    ]


def new_row(state, other):
    return [
        f'{state}.ARRAYS[n_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_new_child)),ENTRY (KINT 1) (ALIAS n_other),ENTRY (KINT 2) (DIRECT (PINT 19))]',
        f'{state}.ARRAYS[n_new_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 11))]',
        f'{state}.STORE[n_other] = DEFINED (PINT {other})',
        f'$node_children({state}, HARRAY n_new) = [HARRAY n_new_child,HCELL n_other]',
    ]


def field(state, root, child, value):
    tag = state.lower()
    return [
        f'$objectprops_record_at({state}.OBJECTPROPS, n_object) = (pobjectprops_{tag})',
        f'$property_slot_at(pobjectprops_{tag}.SLOTS, $ptascii("hold")) = (ppropertyslot_{tag})',
        f'ppropertyslot_{tag}.STATE = PROP_VALUE (DIRECT (PARRAY {root}))',
        f'$node_children({state}, HOBJECT n_object) = [HARRAY {root}]',
        f'{state}.ARRAYS[{root}].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY {child})),ENTRY (KINT 1) (ALIAS n_leaf),ENTRY (KINT 2) (DIRECT (PINT 7))]',
        f'{state}.ARRAYS[{child}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT {value}))]',
    ]


def builder(state, tail=None):
    entries = '[ENTRY (KINT 4) (DIRECT (PINT 8)),ENTRY (KSTRING ($ptascii("row"))) (DIRECT (PARRAY n_new))]'
    if tail is not None:
        entries = entries[:-1] + f',ENTRY (KINT 5) (DIRECT (PINT {tail}))]'
    return [f'{state}.ARRAYS[n_target].ITEMS = {entries}']


def common(program, path, object_owners):
    checks = initial(program, path) + seek('S_initial', 710, 'S_cache') + [
        'S_cache.TODO = (ARRAY_ITERATOR parrayiterator_cached "key-start") :: ptask_tail*',
        'parrayiterator_cached.CURRENT = REFERENCE n_outer',
        'parrayiterator_cached.KEY = KNOWN PNULL',
        'parrayiterator_cached.OBJECT = n_object',
        'parrayiterator_cached.ARRAY = n_target',
        '$lookup(S_cache.ENV, $ptascii("row")) = (n_outer)',
        '$lookup(S_cache.ENV, $ptascii("saved")) = (n_saved)',
        '$lookup(S_cache.ENV, $ptascii("leaf")) = (n_leaf)',
        '$lookup(S_cache.ENV, $ptascii("other")) = (n_other)',
        '$lookup(S_cache.ENV, $ptascii("it")) = ' + ('eps' if object_owners == 1 else '(n_it)'),
        '$lookup(S_cache.ENV, $ptascii("dest")) = (n_dest)',
        '$lookup(S_cache.ENV, $ptascii("tail")) = (n_tail)',
        '$lookup(S_cache.ENV, $ptascii("watch")) = (n_watch)',
        'S_cache.STORE[n_outer] = DEFINED (PARRAY n_old)',
        'S_cache.STORE[n_saved] = DEFINED (PARRAY n_old)',
        'S_cache.STORE[n_leaf] = DEFINED (PINT 2)',
        'S_cache.STORE[n_other] = DEFINED (PINT 9)',
        'S_cache.STORE[n_dest] = DEFINED (PINT 99)',
        'S_cache.STORE[n_tail] = DEFINED (PINT 7)',
        'S_cache.STORE[n_watch] = DEFINED (POBJECT n_observer)',
        '$weakref_get(S_cache, n_observer) = POBJECT n_object',
        'S_cache.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8))]',
        '$array_iterator_destructor_byref_current(S_cache, parrayiterator_cached)',
        '$array_iterator_owned_field(S_cache, parrayiterator_cached)',
        '$array_iterator_ready(S_cache, parrayiterator_cached)',
        '$array_iterator_current_value(S_cache, parrayiterator_cached, REFERENCE n_outer) = (PARRAY n_old)',
    ] + old_row('S_cache') + field('S_cache', 'n_old', 'n_old_child', 3) + [
        owners('S_cache', 'HOBJECT n_object', object_owners),
        owners('S_cache', 'HARRAY n_old', 3),
        '$heap_count(HARRAY n_old_child, $pools_nodes(S_cache.POOLS)) = 1',
        owners('S_cache', 'HARRAY n_old_child', 2),
        owners('S_cache', 'HCELL n_leaf', 2),
    ] + public('S_cache')
    checks += seek('S_cache', 711, 'S_key') + [
        'S_key.TODO = (ARRAY_ITERATOR parrayiterator_key "insert") :: ptask_tail*',
        'parrayiterator_key.CURRENT = REFERENCE n_outer',
        'parrayiterator_key.KEY = KNOWN pvalue_key',
        '$string_bytes(pvalue_key) = ($ptascii("row"))',
        'S_key.STORE[n_outer] = DEFINED (PARRAY n_new)',
        'n_new =/= n_old',
        'S_key.STORE[n_saved] = DEFINED (PARRAY n_old)',
        '$array_iterator_current_value(S_key, parrayiterator_key, REFERENCE n_outer) = (PARRAY n_new)',
        '$array_iterator_ready(S_key, parrayiterator_key)',
    ] + old_row('S_key') + new_row('S_key', 9) + field('S_key', 'n_old', 'n_old_child', 3) + [
        owners('S_key', 'HARRAY n_old', 2),
        owners('S_key', 'HARRAY n_old_child', 2),
        owners('S_key', 'HARRAY n_new', 1),
        owners('S_key', 'HCELL n_leaf', 2),
        owners('S_key', 'HCELL n_other', 2),
        'PhpStep: S_key ~> S_insert',
        'S_insert.TODO = (ARRAY_ITERATOR parrayiterator_insert "next-start") :: ptask_tail*',
        'parrayiterator_insert.CURRENT = KNOWN PNULL',
        'parrayiterator_insert.KEY = KNOWN PNULL',
        '$array_iterator_current_builder(S_insert, parrayiterator_insert)',
        owners('S_insert', 'HARRAY n_old', 2),
        owners('S_insert', 'HARRAY n_new', 2),
        '$heap_count(HARRAY n_new_child, $pools_nodes(S_insert.POOLS)) = 1',
        owners('S_insert', 'HARRAY n_new_child', 2),
    ] + builder('S_insert') + public('S_key') + public('S_insert') + budget('S_key', 'S_insert_budget') + [
        'S_materialized = $objectprops_mark(S_cache, n_object)',
        'S_materialized.ALLOCATIONS = S_cache.ALLOCATIONS',
        'S_materialized.ARRAYS = S_cache.ARRAYS',
        'S_materialized.STORE = S_cache.STORE',
        '~$array_iterator_owned_field(S_materialized, parrayiterator_cached)',
        '~$array_iterator_ready(S_materialized, parrayiterator_cached)',
        'S_object_child = S_cache[.ARRAYS[n_old_child].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_observer))]]',
        '$node_children(S_object_child, HARRAY n_old_child) = [HOBJECT n_observer]',
        '~$array_iterator_reference_table(S_object_child, n_old)',
        '~$array_iterator_owned_field(S_object_child, parrayiterator_cached)',
        '~$array_iterator_ready(S_object_child, parrayiterator_cached)',
    ]
    checks += seek('S_insert', 712, 'S_finish') + [
        'S_finish.TODO = (ARRAY_ITERATOR parrayiterator_finish "finish") :: ptask_finish_tail*',
        'parrayiterator_finish = parrayiterator_insert[.CURRENT = KNOWN PNULL][.KEY = KNOWN PNULL]',
        '$array_iterator_ready(S_finish, parrayiterator_finish)',
        '$array_iterator_destructor_byref_current(S_finish, parrayiterator_finish)',
        'S_finish.STORE[n_dest] = DEFINED (PINT 99)',
        'S_finish.STORE[n_tail] = DEFINED (PINT 7)',
        owners('S_finish', 'HOBJECT n_object', object_owners),
        owners('S_finish', 'HARRAY n_old', 2),
        owners('S_finish', 'HARRAY n_old_child', 2),
        owners('S_finish', 'HARRAY n_new', 2),
    ] + builder('S_finish') + old_row('S_finish') + new_row('S_finish', 9) + field('S_finish', 'n_old', 'n_old_child', 3) + public('S_finish')
    return checks


def last_data(program, path, stdout):
    checks = common(program, path, 1) + [
        'PhpStep: S_finish ~> S_raw',
        'S_raw.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (ARRAY_ITERATOR_RELEASE parrayiterator_finish "normal") :: ptask_finish_tail*',
        'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_object)]',
        '$array_iterator_release_valid(S_raw, parrayiterator_finish, "normal")',
        owners('S_raw', 'HOBJECT n_object', 1),
        owners('S_raw', 'HARRAY n_old', 2),
        owners('S_raw', 'HARRAY n_new', 2),
    ] + public('S_raw') + budget('S_finish', 'S_finish_budget') + seek('S_finish', 713, 'S_dtor') + [
        'S_dtor.CURRENT = (pcallcontext_d)',
        '$destructor_context_call(pcallcontext_d, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object',
        '$destructor_call_live(S_dtor, pdestructorcall)',
        '$weakref_get(S_dtor, n_observer) = POBJECT n_object',
        'S_dtor.STORE[n_dest] = DEFINED (PINT 99)',
        'S_dtor.STORE[n_tail] = DEFINED (PINT 7)',
        owners('S_dtor', 'HARRAY n_old', 2),
        owners('S_dtor', 'HARRAY n_old_child', 2),
    ] + field('S_dtor', 'n_old', 'n_old_child', 3) + public('S_dtor')
    checks += seek('S_dtor', 714, 'S_mutated') + [
        'S_mutated.STORE[n_saved] = DEFINED (PARRAY n_old)',
        'S_mutated.STORE[n_leaf] = DEFINED (PINT 2)',
        'S_mutated.STORE[n_other] = DEFINED (PINT 9)',
    ] + old_row('S_mutated') + field('S_mutated', 'n_field', 'n_field_child', 44) + [
        'n_field =/= n_old', 'n_field_child =/= n_old_child',
        owners('S_mutated', 'HARRAY n_old', 1),
        owners('S_mutated', 'HARRAY n_old_child', 2),
        owners('S_mutated', 'HARRAY n_field', 1),
        owners('S_mutated', 'HARRAY n_field_child', 1),
        owners('S_mutated', 'HCELL n_leaf', 3),
    ] + public('S_mutated')
    checks += seek('S_mutated', 715, 'S_released') + [
        'S_released.TODO = (ARRAY_ITERATOR_RELEASE parrayiterator_finish "normal") :: ptask_finish_tail*',
        '~((HOBJECT n_object) <- S_released.ALLOCATIONS)',
        '~((HARRAY n_field) <- S_released.ALLOCATIONS)',
        '~((HARRAY n_field_child) <- S_released.ALLOCATIONS)',
        '$weakref_get(S_released, n_observer) = PNULL',
        'S_released.STORE[n_leaf] = DEFINED (PINT 17)',
        'S_released.STORE[n_other] = DEFINED (PINT 42)',
        'S_released.STORE[n_tail] = DEFINED (PINT 20)',
        '$array_iterator_release_valid(S_released, parrayiterator_finish, "normal")',
        '$array_iterator_release_builder(S_released, parrayiterator_finish)',
        owners('S_released', 'HARRAY n_old', 1),
        owners('S_released', 'HARRAY n_old_child', 2),
        owners('S_released', 'HCELL n_leaf', 2),
        owners('S_released', 'HARRAY n_new', 2),
        'PhpStep: S_released ~> S_next',
        'S_next.TODO = (ARRAY_NEXT n_target parrayiterator_finish.TAIL) :: ptask_finish_tail*',
    ] + old_row('S_released') + new_row('S_released', 42) + builder('S_released') + public('S_released') + public('S_next') + budget('S_released', 'S_release_budget')
    checks += seek('S_released', 716, 'S_read') + [
        'S_read.STORE[n_dest] = DEFINED (PARRAY n_target)',
        'S_read.STORE[n_tail] = DEFINED (PINT 21)',
        '$weakref_get(S_read, n_observer) = PNULL',
        '~((HARRAY n_field) <- S_read.ALLOCATIONS)',
        owners('S_read', 'HARRAY n_old', 1),
        owners('S_read', 'HARRAY n_old_child', 2),
        owners('S_read', 'HARRAY n_new', 2),
        owners('S_read', 'HCELL n_leaf', 2),
    ] + builder('S_read', 20) + old_row('S_read') + new_row('S_read', 42) + public('S_read')
    return checks + finish('S_read', stdout, [
        'HOBJECT n_object', 'HOBJECT n_observer', 'HCELL n_outer',
        'HCELL n_leaf', 'HCELL n_other', 'HARRAY n_old', 'HARRAY n_old_child',
        'HARRAY n_field', 'HARRAY n_field_child', 'HARRAY n_new', 'HARRAY n_new_child',
        'HARRAY n_target',
    ])


def retained(program, path, stdout):
    checks = common(program, path, 2) + seek('S_finish', 717, 'S_before') + [
        '$lookup(S_before.ENV, $ptascii("it")) = (n_it)',
        'S_before.STORE[n_it] = DEFINED (POBJECT n_object)',
        'S_before.STORE[n_dest] = DEFINED (PARRAY n_target)',
        'S_before.STORE[n_tail] = DEFINED (PINT 8)',
        '$weakref_get(S_before, n_observer) = POBJECT n_object',
        owners('S_before', 'HOBJECT n_object', 1),
        owners('S_before', 'HARRAY n_old', 2),
        owners('S_before', 'HARRAY n_new', 2),
    ] + builder('S_before', 7) + field('S_before', 'n_old', 'n_old_child', 3) + public('S_before') + budget('S_finish', 'S_retained_finish_budget')
    checks += seek('S_before', 713, 'S_dtor') + [
        'S_dtor.CURRENT = (pcallcontext_d)',
        '$destructor_context_call(pcallcontext_d, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object',
        '$destructor_call_live(S_dtor, pdestructorcall)',
        'S_dtor_global = $global_table_view(S_dtor)',
        '$lookup(S_dtor_global.ENV, $ptascii("it")) = eps',
        'S_dtor.STORE[n_dest] = DEFINED (PARRAY n_target)',
        'S_dtor.STORE[n_tail] = DEFINED (PINT 8)',
        '$weakref_get(S_dtor, n_observer) = POBJECT n_object',
    ] + field('S_dtor', 'n_old', 'n_old_child', 3) + public('S_dtor')
    checks += seek('S_dtor', 714, 'S_mutated') + [
        'S_mutated.STORE[n_leaf] = DEFINED (PINT 2)',
    ] + old_row('S_mutated') + field('S_mutated', 'n_field', 'n_field_child', 44) + [
        'n_field =/= n_old', 'n_field_child =/= n_old_child',
        owners('S_mutated', 'HARRAY n_old', 1),
        owners('S_mutated', 'HARRAY n_field', 1),
        owners('S_mutated', 'HCELL n_leaf', 3),
    ] + public('S_mutated')
    checks += seek('S_mutated', 716, 'S_read') + [
        '~((HOBJECT n_object) <- S_read.ALLOCATIONS)',
        '~((HARRAY n_field) <- S_read.ALLOCATIONS)',
        '~((HARRAY n_field_child) <- S_read.ALLOCATIONS)',
        '$weakref_get(S_read, n_observer) = PNULL',
        'S_read.STORE[n_dest] = DEFINED (PARRAY n_target)',
        'S_read.STORE[n_leaf] = DEFINED (PINT 17)',
        'S_read.STORE[n_other] = DEFINED (PINT 42)',
        'S_read.STORE[n_tail] = DEFINED (PINT 20)',
        owners('S_read', 'HARRAY n_old', 1),
        owners('S_read', 'HARRAY n_old_child', 2),
        owners('S_read', 'HARRAY n_new', 2),
        owners('S_read', 'HCELL n_leaf', 2),
    ] + builder('S_read', 7) + old_row('S_read') + new_row('S_read', 42) + public('S_read')
    return checks + finish('S_read', stdout, [
        'HOBJECT n_object', 'HOBJECT n_observer', 'HCELL n_outer',
        'HCELL n_leaf', 'HCELL n_other', 'HARRAY n_old', 'HARRAY n_old_child',
        'HARRAY n_field', 'HARRAY n_field_child', 'HARRAY n_new', 'HARRAY n_new_child',
        'HARRAY n_target',
    ])


def conditions(name, program, path, stdout):
    return last_data(program, path, stdout) if name == SELECTED[0] else retained(program, path, stdout)


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(AUTHOR, conditions, HELPERS, extra_inputs=(
        Path(__file__), Path(__file__).with_name('array_aggregate_unpack_state_review.py'),
        Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
