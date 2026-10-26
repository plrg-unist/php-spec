#!/usr/bin/env python3
"""A key throw releases its raw cache before Dtor, preserving an ALIAS builder."""
from pathlib import Path
from types import SimpleNamespace

import array_iterator_byref_destructor_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial, seek
from array_generator_unpack_state_review import budget, finish, owners, public

CASE = 'array-iterator-byref-destructor-key-throw'
PEER = SimpleNamespace(CASES={CASE: cases.CASES[CASE]}, __file__=cases.__file__)

HELPERS = shared.HELPERS + r'''
dec $a61_review_echo(pstate, ptbytes) : bool
def $a61_review_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a61_review_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 520) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "key-start") :: ptask*
def $list_warning_frontier(S, 521) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_ITERATOR parrayiterator "key") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 522) = $a61_review_echo(S, $ptascii("D:"))
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
def $list_warning_frontier(S, 523) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_ITERATOR_RELEASE parrayiterator "abrupt") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 524) = $a61_review_echo(S, $ptascii("E:"))
'''


def prefix(state):
    return [
        f'{state}.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8)),ENTRY (KINT 5) (ALIAS n_alias)]',
        f'$node_children({state}, HARRAY n_target) = [HCELL n_alias]',
    ]


def current_row(state):
    return [
        f'{state}.ARRAYS[n_new].ITEMS = [ENTRY (KINT 0) (ALIAS n_alias),ENTRY (KINT 1) (DIRECT (PINT 19))]',
        f'$node_children({state}, HCELL n_outer) = [HARRAY n_new]',
        f'$node_children({state}, HARRAY n_new) = [HCELL n_alias]',
    ]


def conditions(name, program, path, stdout):
    assert name == CASE
    checks = initial(program, path) + seek('S_initial', 520, 'S_cache') + [
        'S_cache.TODO = (ARRAY_ITERATOR parrayiterator_cached "key-start") :: ptask_tail*',
        'parrayiterator_cached.CURRENT = REFERENCE n_outer',
        'parrayiterator_cached.KEY = KNOWN PNULL',
        'parrayiterator_cached.OBJECT = n_object', 'parrayiterator_cached.ARRAY = n_target',
        'parrayiterator_cached.ITERATOR = n_iterator',
        '$lookup(S_cache.ENV, $ptascii("it")) = eps',
        '$lookup(S_cache.ENV, $ptascii("row")) = (n_outer)',
        '$lookup(S_cache.ENV, $ptascii("leaf")) = (n_leaf)',
        '$lookup(S_cache.ENV, $ptascii("alias")) = (n_alias)',
        '$lookup(S_cache.ENV, $ptascii("dest")) = (n_dest)',
        '$lookup(S_cache.ENV, $ptascii("tail")) = (n_tail)',
        '$lookup(S_cache.ENV, $ptascii("watch")) = (n_watch)',
        'S_cache.STORE[n_watch] = DEFINED (POBJECT n_observer)',
        '$lookup(S_cache.ENV, $ptascii("first")) = (n_first)',
        'S_cache.STORE[n_first] = DEFINED (POBJECT n_original)',
        'S_cache.STORE[n_outer] = DEFINED (PARRAY n_old)',
        'S_cache.STORE[n_leaf] = DEFINED (PINT 2)',
        'S_cache.STORE[n_alias] = DEFINED (PINT 9)',
        'S_cache.STORE[n_dest] = DEFINED (PINT 99)',
        'S_cache.STORE[n_tail] = DEFINED (PINT 7)',
        'S_cache.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf),ENTRY (KINT 1) (DIRECT (PINT 7))]',
        'n_outer <- S_cache.REFCELLS', 'n_leaf <- S_cache.REFCELLS', 'n_alias <- S_cache.REFCELLS',
        '$array_iterator_source(S_cache, parrayiterator_cached)',
        '$array_iterator_valid(S_cache, parrayiterator_cached, "key-start")',
        '$array_iterator_destructor_byref_current(S_cache, parrayiterator_cached)',
        '$array_iterator_ready(S_cache, parrayiterator_cached)',
        '$array_iterator_value(S_cache, REFERENCE n_outer) = eps',
        '$array_iterator_current_value(S_cache, parrayiterator_cached, REFERENCE n_outer) = (PARRAY n_old)',
        '~$array_null_const_items(S_cache, S_cache.ARRAYS[n_target].ITEMS, [n_target])',
        '$weakref_get(S_cache, n_observer) = POBJECT n_object',
        owners('S_cache', 'HOBJECT n_object', 1), owners('S_cache', 'HCELL n_outer', 2),
        owners('S_cache', 'HARRAY n_old', 1), owners('S_cache', 'HCELL n_leaf', 2),
        owners('S_cache', 'HCELL n_alias', 2), owners('S_cache', 'HARRAY n_target', 1),
    ] + prefix('S_cache') + public('S_cache')
    # A constructed KEY refusal moves the raw reference from cache to RESULT,
    # preserving physical edges and owners. This is a helper-only control,
    # not a PHP history in which key() returned by reference.
    checks += [
        'parrayiterator_refused = parrayiterator_cached[.CURRENT = KNOWN PNULL]',
        'S_key_refused = S_cache[.TODO = (ARRAY_ITERATOR parrayiterator_refused "key") :: ptask_tail*][.RESULT = REFERENCE n_outer][.COMPLETION = UNSUPPORTED "array Iterator unpack callback result outside quiet payload domain"]',
        '$heap_graph(S_key_refused).EDGES = $heap_graph(S_cache).EDGES',
        '$heap_valid($heap_graph(S_key_refused))',
        owners('S_key_refused', 'HCELL n_outer', 2),
        '$array_iterator_ready(S_key_refused, parrayiterator_refused)',
        '$array_iterator_current_value(S_key_refused, parrayiterator_refused, REFERENCE n_outer) = (PARRAY n_old)',
        '$array_iterator_value(S_key_refused, REFERENCE n_outer) = eps',
        '$array_iterator_blocked(S_key_refused)',
        '$drive_steps(S_key_refused, 1) = S_key_refused',
    ]
    checks += seek('S_cache', 521, 'S_pending') + [
        'S_pending.TODO = (THROW_SEARCH n_original) :: (ARRAY_ITERATOR parrayiterator_cached "key") :: ptask_tail*',
        '$lookup(S_pending.ENV, $ptascii("it")) = eps',
        '$lookup(S_pending.ENV, $ptascii("row")) = eps',
        '$array_iterator_ready(S_pending, parrayiterator_cached)',
        'S_pending.STORE[n_outer] = DEFINED (PARRAY n_new)',
        'n_new =/= n_old',
        '~((HARRAY n_old) <- S_pending.ALLOCATIONS)',
        'S_pending.STORE[n_leaf] = DEFINED (PINT 2)',
        'S_pending.STORE[n_alias] = DEFINED (PINT 9)',
        'S_pending.STORE[n_dest] = DEFINED (PINT 99)', 'S_pending.STORE[n_tail] = DEFINED (PINT 7)',
        '$throwable_field(S_pending, n_original, "previous") = PNULL',
        '$throwable_field(S_pending, n_original, "trace") = PARRAY n_trace',
        'S_pending.ARRAYS[n_trace].ITEMS = eps',
        owners('S_pending', 'HOBJECT n_object', 1), owners('S_pending', 'HCELL n_outer', 1),
        owners('S_pending', 'HARRAY n_new', 1), owners('S_pending', 'HCELL n_alias', 3),
        owners('S_pending', 'HCELL n_leaf', 1), owners('S_pending', 'HARRAY n_target', 1),
        'S_popped = S_pending[.TODO = (THROW_SEARCH n_original) :: ptask_tail*]',
        'parrayiterator_release = parrayiterator_cached[.CURRENT = KNOWN PNULL][.KEY = KNOWN PNULL]',
        'PhpStep: S_pending ~> S_release',
        'S_release = $array_iterator_discard(S_popped, parrayiterator_cached, "key")',
        'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (THROW_SEARCH n_original) :: (ARRAY_ITERATOR_RELEASE parrayiterator_release "abrupt") :: ptask_tail*',
        'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_outer),DESTRUCTION_VALUE (HOBJECT n_object)]',
        'pdestructionrelease.USER',
        'pdestructionrelease.ORIGIN = $origin_child((parrayiterator_cached.SITE), [PCFIELD 1])',
        'S_release.ITERATORS = $iterator_remove(S_pending.ITERATORS, n_iterator)',
        '$task_nodes(ARRAY_ITERATOR_RELEASE parrayiterator_release "abrupt") = [HARRAY n_target]',
        '$array_iterator_release_valid(S_release, parrayiterator_release, "abrupt")',
        '$array_iterator_release_builder(S_release, parrayiterator_release)',
        owners('S_release', 'HOBJECT n_object', 1), owners('S_release', 'HCELL n_outer', 1),
        owners('S_release', 'HARRAY n_target', 1), owners('S_release', 'HCELL n_alias', 3),
    ] + current_row('S_pending') + prefix('S_pending') + prefix('S_release') + public('S_pending') + public('S_release') + budget('S_pending', 'S_release_budget')
    checks += seek('S_pending', 522, 'S_dtor') + [
        'S_dtor.CURRENT = (pcallcontext_d)',
        '$destructor_context_call(pcallcontext_d, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object', 'pdestructorcall.USER',
        'pdestructorcall.SITE = $origin_child((parrayiterator_cached.SITE), [PCFIELD 1])',
        'pdestructorcall.LINE = parrayiterator_cached.LINE',
        'pdestructorcall.PENDING = (n_original)',
        '$destructor_call_live(S_dtor, pdestructorcall)',
        'n_object <- S_dtor.DESTRUCTION.CALLED',
        '$weakref_get(S_dtor, n_observer) = POBJECT n_object',
        '~((HCELL n_outer) <- S_dtor.ALLOCATIONS)',
        '~((HARRAY n_new) <- S_dtor.ALLOCATIONS)',
        'S_dtor_global = $global_table_view(S_dtor)',
        '$lookup(S_dtor_global.ENV, $ptascii("row")) = eps',
        'S_dtor.STORE[n_dest] = DEFINED (PINT 99)', 'S_dtor.STORE[n_tail] = DEFINED (PINT 7)',
        'S_dtor.STORE[n_alias] = DEFINED (PINT 9)',
        '$array_iterator_release_builder(S_dtor, parrayiterator_release)',
        owners('S_dtor', 'HARRAY n_target', 1), owners('S_dtor', 'HCELL n_alias', 2),
        owners('S_dtor', 'HCELL n_leaf', 1),
    ] + prefix('S_dtor') + public('S_dtor')
    checks += seek('S_dtor', 523, 'S_released') + [
        'S_released.TODO = (THROW_SEARCH n_original) :: (ARRAY_ITERATOR_RELEASE parrayiterator_release "abrupt") :: ptask_tail*',
        '~((HOBJECT n_object) <- S_released.ALLOCATIONS)',
        '~((HCELL n_outer) <- S_released.ALLOCATIONS)',
        '~((HARRAY n_new) <- S_released.ALLOCATIONS)',
        '$weakref_get(S_released, n_observer) = PNULL',
        'S_released.STORE[n_dest] = DEFINED (PINT 99)',
        'S_released.STORE[n_tail] = DEFINED (PINT 20)',
        'S_released.STORE[n_alias] = DEFINED (PINT 42)',
        '$throwable_field(S_released, n_original, "previous") = PNULL',
        '$array_iterator_release_valid(S_released, parrayiterator_release, "abrupt")',
        '$array_iterator_destructor_byref_current(S_released, parrayiterator_release)',
        '$array_iterator_reference_cell(S_released, n_outer) = eps',
        '$array_iterator_release_builder(S_released, parrayiterator_release)',
        '~$array_iterator_source(S_released, parrayiterator_release)',
        owners('S_released', 'HARRAY n_target', 1), owners('S_released', 'HCELL n_alias', 2),
        'PhpStep: S_released ~> S_cancel',
        'S_cancel.TODO = (THROW_SEARCH n_original) :: ptask_tail*',
        owners('S_cancel', 'HARRAY n_target', 0), owners('S_cancel', 'HCELL n_alias', 2),
    ] + prefix('S_released') + public('S_released') + budget('S_released', 'S_cancel_budget')
    checks += seek('S_released', 524, 'S_caught') + [
        '$lookup(S_caught.ENV, $ptascii("e")) = (n_caught)',
        'S_caught.STORE[n_caught] = DEFINED (POBJECT n_original)',
        'S_caught.STORE[n_first] = DEFINED (POBJECT n_original)',
        'S_caught.STORE[n_dest] = DEFINED (PINT 99)',
        'S_caught.STORE[n_tail] = DEFINED (PINT 20)',
        'S_caught.STORE[n_alias] = DEFINED (PINT 42)',
        '~((HARRAY n_target) <- S_caught.ALLOCATIONS)',
        '$weakref_get(S_caught, n_observer) = PNULL',
        '$throwable_field(S_caught, n_original, "previous") = PNULL',
        owners('S_caught', 'HCELL n_alias', 1), owners('S_caught', 'HCELL n_leaf', 1),
    ] + public('S_caught')
    return checks + finish('S_caught', stdout, [
        'HOBJECT n_object', 'HOBJECT n_observer', 'HOBJECT n_original', 'HARRAY n_trace',
        'HCELL n_outer', 'HCELL n_alias', 'HCELL n_leaf',
        'HARRAY n_target', 'HARRAY n_old', 'HARRAY n_new',
    ])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(PEER, conditions, HELPERS, extra_inputs=(
        Path(__file__),
        Path(__file__).with_name('array_aggregate_unpack_state_review.py'),
        Path(__file__).with_name('array_generator_unpack_state_review.py'),
    )) else 1)
