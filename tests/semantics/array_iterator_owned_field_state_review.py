#!/usr/bin/env python3
"""Abrupt Iterator spread keeps the field graph through Dtor and releases it afterward."""
from pathlib import Path
from types import SimpleNamespace

import array_iterator_owned_field_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial
from array_generator_unpack_state_review import finish, owners, public

SELECTED = ('array-iterator-owned-field-key-throw',
            'array-iterator-owned-field-invalid-key')
PEER = SimpleNamespace(CASES={name: cases.CASES[name] for name in SELECTED},
                       __file__=cases.__file__)

HELPERS = shared.HELPERS + r'''
dec $a62_peer_reach(pstate, nat) : pstate
def $a62_peer_reach(S, n_stage) = S_found[.COMPLETION = NORMAL]
  -- if S_found = $list_warning_seek(S, n_stage, 3000)
  -- if S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET
dec $a62_peer_echo(pstate, ptbytes) : bool
def $a62_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a62_peer_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 620) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "key-start") :: ptask*
def $list_warning_frontier(S, 621) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_ITERATOR parrayiterator "key") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 622) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "insert") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 623) = $a62_peer_echo(S, $ptascii("D:"))
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
def $list_warning_frontier(S, 624) = $a62_peer_echo(S, $ptascii("M:"))
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
def $list_warning_frontier(S, 625) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n)) :: pdestructionjob*
  -- if n <- S.DESTRUCTION.CALLED
  -- if $heap_owners($heap_graph(S), HOBJECT n) = 1
  -- if $objectprops_record_at(S.OBJECTPROPS, n) = (pobjectprops)
  -- if $property_slot_at(pobjectprops.SLOTS, $ptascii("hold")) = (ppropertyslot)
  -- if ppropertyslot.STATE = PROP_VALUE (DIRECT (PARRAY n_field))
def $list_warning_frontier(S, 626) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_ITERATOR_RELEASE parrayiterator "abrupt") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 627) = $a62_peer_echo(S, $ptascii("E:"))
'''


def seek(start, stage, state):
    return [f'{state} = $a62_peer_reach({start}, {stage})',
            f'$list_warning_frontier({state}, {stage})']


def old_graph(state):
    return [
        f'{state}.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_old_child)),ENTRY (KINT 1) (ALIAS n_leaf),ENTRY (KINT 2) (DIRECT (PINT 7))]',
        f'{state}.ARRAYS[n_old_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 3))]',
        f'$node_children({state}, HARRAY n_old) = [HARRAY n_old_child,HCELL n_leaf]',
    ]


def field(state, root, child, value):
    suffix = state.lower()
    return [
        f'$objectprops_record_at({state}.OBJECTPROPS, n_object) = (pobjectprops_{suffix})',
        f'$property_slot_at(pobjectprops_{suffix}.SLOTS, $ptascii("hold")) = (ppropertyslot_{suffix})',
        f'ppropertyslot_{suffix}.STATE = PROP_VALUE (DIRECT (PARRAY {root}))',
        f'$node_children({state}, HOBJECT n_object) = [HARRAY {root}]',
        f'{state}.ARRAYS[{root}].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY {child})),ENTRY (KINT 1) (ALIAS n_leaf),ENTRY (KINT 2) (DIRECT (PINT 7))]',
        f'{state}.ARRAYS[{child}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT {value}))]',
        f'$node_children({state}, HARRAY {root}) = [HARRAY {child},HCELL n_leaf]',
    ]


def common(program, path):
    checks = initial(program, path) + seek('S_initial', 620, 'S_cache') + [
        'S_cache.TODO = (ARRAY_ITERATOR parrayiterator "key-start") :: ptask_tail*',
        'parrayiterator.CURRENT = REFERENCE n_outer',
        'parrayiterator.KEY = KNOWN PNULL',
        'parrayiterator.OBJECT = n_object',
        'parrayiterator.ARRAY = n_target',
        '$lookup(S_cache.ENV, $ptascii("it")) = eps',
        '$lookup(S_cache.ENV, $ptascii("row")) = (n_outer)',
        '$lookup(S_cache.ENV, $ptascii("saved")) = (n_saved)',
        'S_cache.STORE[n_saved] = DEFINED (PARRAY n_old)',
        'S_cache.STORE[n_outer] = DEFINED (PARRAY n_old)',
        '$lookup(S_cache.ENV, $ptascii("leaf")) = (n_leaf)',
        '$lookup(S_cache.ENV, $ptascii("other")) = (n_other)',
        'S_cache.STORE[n_leaf] = DEFINED (PINT 2)',
        'S_cache.STORE[n_other] = DEFINED (PINT 9)',
        '$lookup(S_cache.ENV, $ptascii("dest")) = (n_dest)',
        '$lookup(S_cache.ENV, $ptascii("tail")) = (n_tail)',
        'S_cache.STORE[n_dest] = DEFINED (PINT 99)',
        'S_cache.STORE[n_tail] = DEFINED (PINT 7)',
        '$lookup(S_cache.ENV, $ptascii("watch")) = (n_watch)',
        'S_cache.STORE[n_watch] = DEFINED (POBJECT n_observer)',
        '$weakref_get(S_cache, n_observer) = POBJECT n_object',
        '$array_iterator_destructor_byref_current(S_cache, parrayiterator)',
        '$array_iterator_owned_field(S_cache, parrayiterator)',
        '$array_iterator_ready(S_cache, parrayiterator)',
        'S_cache.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8)),ENTRY (KINT 5) (ALIAS n_other)]',
    ] + old_graph('S_cache') + field('S_cache', 'n_old', 'n_old_child', 3) + [
        owners('S_cache', 'HOBJECT n_object', 1),
        owners('S_cache', 'HARRAY n_old', 3),
        owners('S_cache', 'HARRAY n_old_child', 2),
        '$heap_count(HARRAY n_old_child, $pools_nodes(S_cache.POOLS)) = 1',
        owners('S_cache', 'HCELL n_leaf', 2),
    ] + public('S_cache')
    return checks


def after_destructor(start, stdout, pending):
    checks = seek(start, 623, 'S_dtor') + [
        'S_dtor.CURRENT = (pcallcontext_d)',
        '$destructor_context_call(pcallcontext_d, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object',
        'pdestructorcall.PENDING = (n_original)',
        '$destructor_call_live(S_dtor, pdestructorcall)',
        '$weakref_get(S_dtor, n_observer) = POBJECT n_object',
        'S_dtor.STORE[n_dest] = DEFINED (PINT 99)',
        'S_dtor.STORE[n_other] = DEFINED (PINT 9)',
        owners('S_dtor', 'HARRAY n_old', 2),
        owners('S_dtor', 'HARRAY n_old_child', 2),
    ] + field('S_dtor', 'n_old', 'n_old_child', 3) + public('S_dtor')
    checks += seek('S_dtor', 624, 'S_mutated') + old_graph('S_mutated') + field('S_mutated', 'n_field', 'n_field_child', 44) + [
        'n_field =/= n_old', 'n_field_child =/= n_old_child',
        'S_mutated.STORE[n_saved] = DEFINED (PARRAY n_old)',
        'S_mutated.STORE[n_leaf] = DEFINED (PINT 2)',
        'S_mutated.STORE[n_other] = DEFINED (PINT 9)',
        owners('S_mutated', 'HARRAY n_old', 1),
        owners('S_mutated', 'HARRAY n_old_child', 2),
        owners('S_mutated', 'HARRAY n_field', 1),
        owners('S_mutated', 'HARRAY n_field_child', 1),
        owners('S_mutated', 'HCELL n_leaf', 3),
    ] + public('S_mutated')
    checks += seek('S_mutated', 625, 'S_release_field') + [
        'S_release_field.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_field) :: ptask_storage_tail*',
        'pdestructionrelease_field.JOBS = (DESTRUCTION_VALUE (HOBJECT n_object)) :: pdestructionjob_tail*',
        '$destructor_release_valid(S_release_field, pdestructionrelease_field)',
        'S_release_field.STORE[n_leaf] = DEFINED (PINT 17)',
        'S_release_field.STORE[n_other] = DEFINED (PINT 42)',
        'S_release_field.STORE[n_tail] = DEFINED (PINT 20)',
        '$weakref_get(S_release_field, n_observer) = POBJECT n_object',
        owners('S_release_field', 'HOBJECT n_object', 1),
        'PhpStep: S_release_field ~> S_storage',
        'S_storage.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: (DESTRUCTOR_RELEASE pdestructionrelease_after) :: ptask_storage_tail*',
        'pdestructionrelease_after = pdestructionrelease_field[.JOBS = pdestructionjob_tail*]',
        'pinstancestorage.OBJECT = n_object',
        'pinstancestorage.NEXT = 0',
        '$instance_storage_valid(S_storage, pinstancestorage)',
        '$weakref_get(S_storage, n_observer) = PNULL',
        'S_storage.STORE[n_leaf] = DEFINED (PINT 17)',
        'S_storage.STORE[n_other] = DEFINED (PINT 42)',
        'S_storage.STORE[n_tail] = DEFINED (PINT 20)',
        owners('S_storage', 'HARRAY n_field', 1),
        owners('S_storage', 'HARRAY n_field_child', 1),
        'PhpStep: S_storage ~> S_slot',
        'S_slot.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (INSTANCE_STORAGE_STEP pinstancestorage_next) :: (DESTRUCTOR_RELEASE pdestructionrelease_after) :: ptask_storage_tail*',
        'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_field)]',
        'pinstancestorage_next.NEXT = 1',
        '$instance_storage_valid(S_slot, pinstancestorage_next)',
        '(HOBJECT n_object) <- S_slot.ALLOCATIONS',
        '$node_children(S_slot, HOBJECT n_object) = eps',
        owners('S_slot', 'HARRAY n_field', 1),
    ] + field('S_release_field', 'n_field', 'n_field_child', 44) + public('S_release_field') + field('S_storage', 'n_field', 'n_field_child', 44) + public('S_storage') + public('S_slot')
    if pending:
        checks += seek('S_storage', 626, 'S_released') + [
            'S_released.TODO = (THROW_SEARCH n_original) :: (ARRAY_ITERATOR_RELEASE parrayiterator_release "abrupt") :: ptask_tail*',
            '~((HOBJECT n_object) <- S_released.ALLOCATIONS)',
            '~((HARRAY n_field) <- S_released.ALLOCATIONS)',
            '~((HARRAY n_field_child) <- S_released.ALLOCATIONS)',
            '$array_iterator_release_builder(S_released, parrayiterator_release)',
            owners('S_released', 'HARRAY n_target', 1),
        ] + old_graph('S_released') + public('S_released')
        start = 'S_released'
    else:
        start = 'S_storage'
    checks += seek(start, 627, 'S_caught') + [
        '$lookup(S_caught.ENV, $ptascii("e")) = (n_caught)',
        'S_caught.STORE[n_caught] = DEFINED (POBJECT n_original)',
        'S_caught.STORE[n_saved] = DEFINED (PARRAY n_old)',
        'S_caught.STORE[n_leaf] = DEFINED (PINT 17)',
        'S_caught.STORE[n_other] = DEFINED (PINT 42)',
        'S_caught.STORE[n_dest] = DEFINED (PINT 99)',
        'S_caught.STORE[n_tail] = DEFINED (PINT 20)',
        '$weakref_get(S_caught, n_observer) = PNULL',
        '~((HOBJECT n_object) <- S_caught.ALLOCATIONS)',
        '~((HARRAY n_field) <- S_caught.ALLOCATIONS)',
        '~((HARRAY n_field_child) <- S_caught.ALLOCATIONS)',
        '~((HARRAY n_target) <- S_caught.ALLOCATIONS)',
        owners('S_caught', 'HARRAY n_old', 1),
        owners('S_caught', 'HARRAY n_old_child', 2),
        '$heap_count(HARRAY n_old_child, $pools_nodes(S_caught.POOLS)) = 1',
    ] + old_graph('S_caught') + public('S_caught')
    return checks + finish('S_caught', stdout, [
        'HOBJECT n_object', 'HOBJECT n_observer', 'HOBJECT n_original',
        'HCELL n_outer', 'HCELL n_leaf', 'HCELL n_other',
        'HARRAY n_target', 'HARRAY n_old',
        'HARRAY n_field', 'HARRAY n_field_child',
    ]) + [
        # Folded literal descendants retain their permanent compiled-pool owner.
        '(HARRAY n_old_child) <- S_done.ALLOCATIONS',
        '$heap_count(HARRAY n_old_child, $pools_nodes(S_done.POOLS)) = 1',
        owners('S_done', 'HARRAY n_old_child', 1),
    ]


def supplied(program, path, stdout):
    checks = common(program, path) + [
        '$lookup(S_cache.ENV, $ptascii("first")) = (n_first)',
        'S_cache.STORE[n_first] = DEFINED (POBJECT n_original)',
    ] + seek('S_cache', 621, 'S_pending') + [
        'S_pending.TODO = (THROW_SEARCH n_original) :: (ARRAY_ITERATOR parrayiterator "key") :: ptask_tail*',
        'S_pending.STORE[n_saved] = DEFINED (PARRAY n_old)',
        'S_pending.STORE[n_outer] = DEFINED (PARRAY n_new)',
        '$lookup(S_pending.ENV, $ptascii("row")) = eps',
        'S_pending.STORE[n_dest] = DEFINED (PINT 99)',
        '$array_iterator_ready(S_pending, parrayiterator)',
        owners('S_pending', 'HARRAY n_target', 1),
        owners('S_pending', 'HARRAY n_old', 2),
        owners('S_pending', 'HARRAY n_new', 1),
        'S_popped = S_pending[.TODO = (THROW_SEARCH n_original) :: ptask_tail*]',
        'PhpStep: S_pending ~> S_release',
        'S_release = $array_iterator_discard(S_popped, parrayiterator, "key")',
        'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_outer) :: (THROW_SEARCH n_original) :: (ARRAY_ITERATOR_RELEASE parrayiterator_release "abrupt") :: ptask_tail*',
        'pdestructionrelease_outer.JOBS = [DESTRUCTION_VALUE (HCELL n_outer),DESTRUCTION_VALUE (HOBJECT n_object)]',
        '$task_nodes(ARRAY_ITERATOR_RELEASE parrayiterator_release "abrupt") = [HARRAY n_target]',
        '$array_iterator_release_valid(S_release, parrayiterator_release, "abrupt")',
    ] + field('S_pending', 'n_old', 'n_old_child', 3) + public('S_pending') + public('S_release')
    return checks + after_destructor('S_pending', stdout, True)


def invalid(program, path, stdout):
    checks = common(program, path) + seek('S_cache', 622, 'S_insert') + [
        'S_insert.TODO = (ARRAY_ITERATOR parrayiterator_insert "insert") :: ptask_tail*',
        'parrayiterator_insert.CURRENT = REFERENCE n_outer',
        'parrayiterator_insert.KEY = KNOWN (PBOOL false)',
        'S_insert.STORE[n_saved] = DEFINED (PARRAY n_old)',
        'S_insert.STORE[n_outer] = DEFINED (PARRAY n_new)',
        '$lookup(S_insert.ENV, $ptascii("row")) = eps',
        '$array_iterator_ready(S_insert, parrayiterator_insert)',
        'PhpStep: S_insert ~> S_raw',
        'S_raw.TODO = S_insert.TODO',
        'S_raw.COMPLETION = THROWN "Error" ($ptascii("Keys must be of type int|string during array unpacking")) parrayiterator_insert.LINE',
        'S_queued = $drive_steps(S_insert, 1)',
        'S_queued.COMPLETION = BUDGET',
        'S_queued.TODO = (THROW_SEARCH n_original) :: (ARRAY_ITERATOR parrayiterator_insert "insert") :: ptask_tail*',
        'S_queued.DESTRUCTION.RELEASES = S_insert.DESTRUCTION.RELEASES',
        'S_queued.DESTRUCTION.OPERATIONS = S_insert.DESTRUCTION.OPERATIONS',
        '$throwable_field(S_queued, n_original, "previous") = PNULL',
        'parrayiterator_release = parrayiterator_insert[.CURRENT = KNOWN PNULL][.KEY = KNOWN PNULL]',
        owners('S_queued', 'HARRAY n_target', 1),
        owners('S_queued', 'HARRAY n_old', 2),
    ] + field('S_insert', 'n_old', 'n_old_child', 3) + public('S_insert') + public('S_queued')
    return checks + after_destructor('S_queued', stdout, True)


def conditions(name, program, path, stdout):
    return supplied(program, path, stdout) if name == SELECTED[0] else invalid(program, path, stdout)


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(PEER, conditions, HELPERS, extra_inputs=(
        Path(__file__), Path(__file__).with_name('array_aggregate_unpack_state_review.py'),
        Path(__file__).with_name('array_generator_unpack_state_review.py'),
    )) else 1)
