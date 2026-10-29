#!/usr/bin/env python3
"""Reached pooled field snapshots separate from raw current and runtime COW."""
from pathlib import Path
from types import SimpleNamespace

import array_iterator_pooled_field_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial, seek
from array_generator_unpack_state_review import budget, finish, owners, public

SELECTED = ('array-iterator-pooled-field-last-data',
            'array-iterator-pooled-field-key-throw')
AUTHOR = SimpleNamespace(CASES={name: cases.CASES[name] for name in SELECTED},
                         __file__=cases.__file__)

HELPERS = shared.HELPERS + r'''
dec $a63_echo(pstate, ptbytes) : bool
def $a63_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a63_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 810) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "key-start") :: ptask*
def $list_warning_frontier(S, 811) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "insert") :: ptask*
def $list_warning_frontier(S, 812) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "finish") :: ptask*
def $list_warning_frontier(S, 813) = $a63_echo(S, $ptascii("D:"))
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
def $list_warning_frontier(S, 814) = $a63_echo(S, $ptascii("M:"))
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
def $list_warning_frontier(S, 815) = $a63_echo(S, $ptascii("Q:"))
def $list_warning_frontier(S, 816) = $a63_echo(S, $ptascii("E:"))
def $list_warning_frontier(S, 817) = $a63_echo(S, $ptascii("R:"))
'''


def field(state, root, child, value):
    tag = state.lower()
    return [
        f'$objectprops_record_at({state}.OBJECTPROPS, n_object) = (pobjectprops_{tag})',
        f'$property_slot_at(pobjectprops_{tag}.SLOTS, $ptascii("hold")) = (ppropertyslot_{tag})',
        f'ppropertyslot_{tag}.STATE = PROP_VALUE (DIRECT (PARRAY {root}))',
        f'$node_children({state}, HOBJECT n_object) = [HARRAY {root}]',
        f'{state}.ARRAYS[{root}].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY {child})),ENTRY (KINT 1) (DIRECT (PINT 7))]',
        f'{state}.ARRAYS[{child}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT {value}))]',
    ]


def pool(state, extra):
    return [
        f'{state}.POOLS = S_cache.POOLS',
        f'(HARRAY n_pool) <- {state}.ALLOCATIONS',
        f'(HARRAY n_pool_child) <- {state}.ALLOCATIONS',
        f'{state}.ARRAYS[n_pool].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_pool_child)),ENTRY (KINT 1) (DIRECT (PINT 7))]',
        f'{state}.ARRAYS[n_pool_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 3))]',
        f'$heap_count(HARRAY n_pool, $pools_nodes({state}.POOLS)) = n_pool_roots',
        f'$heap_count(HARRAY n_pool_child, $pools_nodes({state}.POOLS)) = n_pool_child_roots',
        owners(state, 'HARRAY n_pool', f'$(n_pool_roots + {extra})'),
        owners(state, 'HARRAY n_pool_child', '$(n_pool_child_roots + 1)'),
    ]


def common(program, path):
    return initial(program, path) + seek('S_initial', 810, 'S_cache') + [
        'S_cache.TODO = (ARRAY_ITERATOR parrayiterator_cached "key-start") :: ptask_cache_tail*',
        'parrayiterator_cached.CURRENT = REFERENCE n_outer',
        'parrayiterator_cached.OBJECT = n_object',
        'parrayiterator_cached.ARRAY = n_target',
        '$lookup(S_cache.ENV, $ptascii("it")) = eps',
        '$lookup(S_cache.ENV, $ptascii("row")) = (n_outer)',
        '$lookup(S_cache.ENV, $ptascii("saved")) = (n_saved)',
        '$lookup(S_cache.ENV, $ptascii("leaf")) = (n_leaf)',
        '$lookup(S_cache.ENV, $ptascii("other")) = (n_other)',
        '$lookup(S_cache.ENV, $ptascii("dest")) = (n_dest)',
        '$lookup(S_cache.ENV, $ptascii("tail")) = (n_tail)',
        '$lookup(S_cache.ENV, $ptascii("watch")) = (n_watch)',
        'S_cache.STORE[n_outer] = DEFINED (PARRAY n_old)',
        'S_cache.STORE[n_saved] = DEFINED (PARRAY n_pool)',
        'S_cache.STORE[n_watch] = DEFINED (POBJECT n_observer)',
        'S_cache.STORE[n_dest] = DEFINED (PINT 99)',
        'S_cache.STORE[n_tail] = DEFINED (PINT 7)',
        'S_cache.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_old_child)),ENTRY (KINT 1) (ALIAS n_leaf),ENTRY (KINT 2) (DIRECT (PINT 8))]',
        'S_cache.ARRAYS[n_old_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 5))]',
        'n_old =/= n_pool',
        'n_pool_roots = $heap_count(HARRAY n_pool, $pools_nodes(S_cache.POOLS))',
        '$(n_pool_roots > 0)',
        '$weakref_get(S_cache, n_observer) = POBJECT n_object',
        '$array_iterator_table(S_cache, n_pool)',
        '~$array_iterator_reference_table(S_cache, n_pool)',
        '$array_iterator_owned_field(S_cache, parrayiterator_cached)',
        '$array_iterator_ready(S_cache, parrayiterator_cached)',
        owners('S_cache', 'HOBJECT n_object', 1),
        owners('S_cache', 'HARRAY n_old', 1),
        owners('S_cache', 'HCELL n_outer', 2),
    ] + field('S_cache', 'n_pool', 'n_pool_child', 3) + [
        'n_pool_child_roots = $heap_count(HARRAY n_pool_child, $pools_nodes(S_cache.POOLS))',
    ] + pool('S_cache', 2) + public('S_cache')


def last_data(program, path, stdout):
    checks = common(program, path) + [
        'S_cache.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8))]',
        'S_pool_alias = S_cache[.ARRAYS[n_pool].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf)]]',
        '~$array_iterator_owned_field(S_pool_alias, parrayiterator_cached)',
        'S_builder_edge = S_cache[.ARRAYS[n_pool_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_target))]]',
        '$array_iterator_table(S_builder_edge, n_pool)',
        '~$array_iterator_owned_field(S_builder_edge, parrayiterator_cached)',
    ] + seek('S_cache', 811, 'S_key') + [
        'S_key.TODO = (ARRAY_ITERATOR parrayiterator_key "insert") :: ptask_cache_tail*',
        'parrayiterator_key.CURRENT = REFERENCE n_outer',
        'S_key.STORE[n_outer] = DEFINED (PARRAY n_new)',
        '~((HARRAY n_old) <- S_key.ALLOCATIONS)',
        'S_key.ARRAYS[n_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_new_child)),ENTRY (KINT 1) (ALIAS n_other),ENTRY (KINT 2) (DIRECT (PINT 19))]',
        '$array_iterator_current_value(S_key, parrayiterator_key, REFERENCE n_outer) = (PARRAY n_new)',
        'PhpStep: S_key ~> S_insert',
        'S_insert.TODO = (ARRAY_ITERATOR parrayiterator_insert "next-start") :: ptask_cache_tail*',
        'parrayiterator_insert.CURRENT = KNOWN PNULL',
        'S_insert.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8)),ENTRY (KSTRING ($ptascii("row"))) (DIRECT (PARRAY n_new))]',
        '$node_children(S_insert, HARRAY n_target) = [HARRAY n_new]',
        owners('S_insert', 'HARRAY n_new', 2),
    ] + pool('S_insert', 2) + public('S_insert') + budget('S_key', 'S_insert_budget')
    checks += seek('S_insert', 812, 'S_finish') + [
        'S_finish.TODO = (ARRAY_ITERATOR parrayiterator_finish "finish") :: ptask_finish_tail*',
        '$array_iterator_ready(S_finish, parrayiterator_finish)',
        'PhpStep: S_finish ~> S_release',
        'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_start) :: (ARRAY_ITERATOR_RELEASE parrayiterator_finish "normal") :: ptask_finish_tail*',
        'pdestructionrelease_start.JOBS = [DESTRUCTION_VALUE (HOBJECT n_object)]',
    ] + seek('S_release', 813, 'S_dtor') + field('S_dtor', 'n_pool', 'n_pool_child', 3) + pool('S_dtor', 2) + [
        '$weakref_get(S_dtor, n_observer) = POBJECT n_object',
        'S_dtor.STORE[n_dest] = DEFINED (PINT 99)',
        'S_dtor.STORE[n_tail] = DEFINED (PINT 7)',
    ] + public('S_dtor')
    checks += seek('S_dtor', 814, 'S_mutated') + field('S_mutated', 'n_field', 'n_field_child', 44) + pool('S_mutated', 1) + [
        'n_field =/= n_pool', 'n_field_child =/= n_pool_child',
        '$heap_count(HARRAY n_field, $pools_nodes(S_mutated.POOLS)) = 0',
        owners('S_mutated', 'HARRAY n_field', 1),
        owners('S_mutated', 'HARRAY n_field_child', 1),
        '$array_iterator_reference_table(S_mutated, n_field)',
    ] + public('S_mutated')
    checks += seek('S_mutated', 817, 'S_read') + [
        '~((HOBJECT n_object) <- S_read.ALLOCATIONS)',
        '~((HARRAY n_field) <- S_read.ALLOCATIONS)',
        '~((HARRAY n_field_child) <- S_read.ALLOCATIONS)',
        '$weakref_get(S_read, n_observer) = PNULL',
        'S_read.STORE[n_dest] = DEFINED (PARRAY n_target)',
        'S_read.STORE[n_tail] = DEFINED (PINT 21)',
        'S_read.STORE[n_other] = DEFINED (PINT 42)',
        'S_read.STORE[n_leaf] = DEFINED (PINT 17)',
        'S_read.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8)),ENTRY (KSTRING ($ptascii("row"))) (DIRECT (PARRAY n_new)),ENTRY (KINT 5) (DIRECT (PINT 20))]',
    ] + pool('S_read', 1) + public('S_read')
    return checks + finish('S_read', stdout, [
        'HOBJECT n_object', 'HOBJECT n_observer', 'HCELL n_outer', 'HCELL n_leaf',
        'HCELL n_other', 'HARRAY n_old', 'HARRAY n_new', 'HARRAY n_target',
        'HARRAY n_field', 'HARRAY n_field_child',
    ]) + pool('S_done', 0)


def key_throw(program, path, stdout):
    checks = common(program, path) + [
        '$lookup(S_cache.ENV, $ptascii("first")) = (n_first)',
        'S_cache.STORE[n_first] = DEFINED (POBJECT n_original)',
        'S_cache.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8)),ENTRY (KINT 5) (ALIAS n_other)]',
    ] + seek('S_cache', 815, 'S_key') + field('S_key', 'n_field', 'n_field_child', 22) + pool('S_key', 1) + [
        'n_field =/= n_pool', 'n_field_child =/= n_pool_child',
        'S_key.STORE[n_outer] = DEFINED (PARRAY n_new)',
        'S_key_global = $global_table_view(S_key)',
        '$lookup(S_key_global.ENV, $ptascii("row")) = eps',
        '$array_iterator_reference_table(S_key, n_field)',
        owners('S_key', 'HARRAY n_field', 1),
        owners('S_key', 'HARRAY n_field_child', 1),
        '$weakref_get(S_key, n_observer) = POBJECT n_object',
    ] + public('S_key')
    checks += seek('S_key', 813, 'S_dtor') + field('S_dtor', 'n_field', 'n_field_child', 22) + pool('S_dtor', 1) + [
        '~((HCELL n_outer) <- S_dtor.ALLOCATIONS)',
        '~((HARRAY n_new) <- S_dtor.ALLOCATIONS)',
        '(HARRAY n_target) <- S_dtor.ALLOCATIONS',
        'S_dtor.STORE[n_dest] = DEFINED (PINT 99)',
        '$weakref_get(S_dtor, n_observer) = POBJECT n_object',
    ] + public('S_dtor')
    checks += seek('S_dtor', 814, 'S_mutated') + field('S_mutated', 'n_field', 'n_field_child', 44) + pool('S_mutated', 1) + [
        owners('S_mutated', 'HARRAY n_field', 1),
        owners('S_mutated', 'HARRAY n_field_child', 1),
    ] + public('S_mutated')
    checks += seek('S_mutated', 816, 'S_caught') + [
        '$lookup(S_caught.ENV, $ptascii("e")) = (n_caught)',
        'S_caught.STORE[n_caught] = DEFINED (POBJECT n_original)',
        '$throwable_field(S_caught, n_original, "previous") = PNULL',
        '~((HOBJECT n_object) <- S_caught.ALLOCATIONS)',
        '~((HARRAY n_field) <- S_caught.ALLOCATIONS)',
        '~((HARRAY n_field_child) <- S_caught.ALLOCATIONS)',
        '~((HARRAY n_target) <- S_caught.ALLOCATIONS)',
        '$weakref_get(S_caught, n_observer) = PNULL',
        'S_caught.STORE[n_dest] = DEFINED (PINT 99)',
        'S_caught.STORE[n_leaf] = DEFINED (PINT 17)',
        'S_caught.STORE[n_other] = DEFINED (PINT 42)',
        'S_caught.STORE[n_tail] = DEFINED (PINT 20)',
    ] + pool('S_caught', 1) + public('S_caught')
    return checks + finish('S_caught', stdout, [
        'HOBJECT n_object', 'HOBJECT n_observer', 'HOBJECT n_original',
        'HCELL n_outer', 'HCELL n_leaf', 'HCELL n_other', 'HARRAY n_old',
        'HARRAY n_new', 'HARRAY n_target', 'HARRAY n_field', 'HARRAY n_field_child',
    ]) + pool('S_done', 0)


def conditions(name, program, path, stdout):
    return (last_data if name == SELECTED[0] else key_throw)(program, path, stdout)


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(AUTHOR, conditions, HELPERS, extra_inputs=(
        Path(__file__), Path(__file__).with_name('array_aggregate_unpack_state_review.py'),
        Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
