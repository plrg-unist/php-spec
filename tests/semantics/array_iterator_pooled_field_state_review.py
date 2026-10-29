#!/usr/bin/env python3
"""Retained Iterator DATA leaves an empty pooled field for late destructor COW."""
from pathlib import Path

import array_iterator_pooled_field_review_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial
from array_generator_unpack_state_review import budget, finish, owners, public

HELPERS = shared.HELPERS + r'''
dec $a63_peer_reach(pstate, nat) : pstate
def $a63_peer_reach(S, n_stage) = S_found[.COMPLETION = NORMAL]
  -- if S_found = $list_warning_seek(S, n_stage, 3000)
  -- if S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET
dec $a63_peer_echo(pstate, ptbytes) : bool
def $a63_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a63_peer_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 630) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "key-start") :: ptask*
def $list_warning_frontier(S, 631) = $a63_peer_echo(S, $ptascii("B:"))
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 632) = $a63_peer_echo(S, $ptascii("D:"))
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
def $list_warning_frontier(S, 633) = $a63_peer_echo(S, $ptascii("M:"))
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
def $list_warning_frontier(S, 634) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n)) :: pdestructionjob*
  -- if n <- S.DESTRUCTION.CALLED
  -- if $heap_owners($heap_graph(S), HOBJECT n) = 1
  -- if $objectprops_record_at(S.OBJECTPROPS, n) = (pobjectprops)
  -- if $property_slot_at(pobjectprops.SLOTS, $ptascii("hold")) = (ppropertyslot)
  -- if ppropertyslot.STATE = PROP_VALUE (DIRECT (PARRAY n_field))
def $list_warning_frontier(S, 635) = $a63_peer_echo(S, $ptascii("R:"))
  -- if S.CURRENT = eps /\ S.FRAMES = eps
'''


def seek(start, stage, state):
    return [f'{state} = $a63_peer_reach({start}, {stage})',
            f'$list_warning_frontier({state}, {stage})']


def field(state, root, items):
    suffix = state.lower()
    return [
        f'$objectprops_record_at({state}.OBJECTPROPS, n_object) = (pobjectprops_{suffix})',
        f'$property_slot_at(pobjectprops_{suffix}.SLOTS, $ptascii("hold")) = (ppropertyslot_{suffix})',
        f'ppropertyslot_{suffix}.STATE = PROP_VALUE (DIRECT (PARRAY {root}))',
        f'$node_children({state}, HOBJECT n_object) = [HARRAY {root}]',
        f'{state}.ARRAYS[{root}].ITEMS = {items}',
    ]


def conditions(name, program, path, stdout):
    checks = initial(program, path) + seek('S_initial', 630, 'S_cache') + [
        'S_cache.TODO = (ARRAY_ITERATOR parrayiterator "key-start") :: ptask_tail*',
        'parrayiterator.OBJECT = n_object', 'parrayiterator.ARRAY = n_target',
        'parrayiterator.CURRENT = REFERENCE n_outer',
        '$lookup(S_cache.ENV, $ptascii("it")) = (n_it)',
        'S_cache.STORE[n_it] = DEFINED (POBJECT n_object)',
        '$lookup(S_cache.ENV, $ptascii("saved")) = (n_saved)',
        'S_cache.STORE[n_saved] = DEFINED (PARRAY n_pool)',
        '$lookup(S_cache.ENV, $ptascii("row")) = (n_outer)',
        'S_cache.STORE[n_outer] = DEFINED (PARRAY n_old)',
        '$lookup(S_cache.ENV, $ptascii("leaf")) = (n_leaf)',
        '$lookup(S_cache.ENV, $ptascii("other")) = (n_other)',
        'S_cache.STORE[n_other] = DEFINED (PINT 9)',
        '$lookup(S_cache.ENV, $ptascii("dest")) = (n_dest)',
        'S_cache.STORE[n_dest] = DEFINED (PINT 99)',
        '$lookup(S_cache.ENV, $ptascii("tail")) = (n_tail)',
        'S_cache.STORE[n_tail] = DEFINED (PINT 7)',
        '$lookup(S_cache.ENV, $ptascii("watch")) = (n_watch)',
        'S_cache.STORE[n_watch] = DEFINED (POBJECT n_observer)',
        '$weakref_get(S_cache, n_observer) = POBJECT n_object',
        'n_pool_roots = $heap_count(HARRAY n_pool, $pools_nodes(S_cache.POOLS))',
        '$(n_pool_roots > 0)', '$array_immutable(S_cache, n_pool)',
        '$array_iterator_table(S_cache, n_pool)',
        '~$array_iterator_reference_table(S_cache, n_pool)',
        '$array_iterator_owned_field(S_cache, parrayiterator)',
        '$array_iterator_ready(S_cache, parrayiterator)',
        'S_cache.ARRAYS[n_target].ITEMS = eps',
        owners('S_cache', 'HOBJECT n_object', 2),
        owners('S_cache', 'HARRAY n_pool', '$(n_pool_roots + 2)'),
    ] + field('S_cache', 'n_pool', 'eps') + public('S_cache')
    checks += seek('S_cache', 631, 'S_before') + [
        'S_before.ITERATORS = eps', 'S_before.POOLS = S_cache.POOLS',
        'S_before.STORE[n_dest] = DEFINED (PARRAY n_target)',
        'S_before.STORE[n_tail] = DEFINED (PINT 8)',
        'S_before.STORE[n_other] = DEFINED (PINT 9)',
        'S_before.STORE[n_saved] = DEFINED (PARRAY n_pool)',
        '$weakref_get(S_before, n_observer) = POBJECT n_object',
        'S_before.ARRAYS[n_target].ITEMS = [ENTRY (KSTRING ($ptascii("row"))) (DIRECT (PARRAY n_new)),ENTRY (KINT 0) (DIRECT (PINT 7))]',
        'S_before.ARRAYS[n_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_new_child)),ENTRY (KINT 1) (ALIAS n_other)]',
        owners('S_before', 'HOBJECT n_object', 1),
        owners('S_before', 'HARRAY n_target', 1),
        owners('S_before', 'HARRAY n_pool', '$(n_pool_roots + 2)'),
    ] + field('S_before', 'n_pool', 'eps') + public('S_before')
    checks += seek('S_before', 632, 'S_dtor') + [
        'S_dtor.CURRENT = (pcallcontext_d)',
        '$destructor_context_call(pcallcontext_d, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object', 'pdestructorcall.PENDING = eps',
        '$destructor_call_live(S_dtor, pdestructorcall)',
        'S_dtor_global = $global_table_view(S_dtor)',
        '$lookup(S_dtor_global.ENV, $ptascii("it")) = eps',
        '$weakref_get(S_dtor, n_observer) = POBJECT n_object',
        'S_dtor.STORE[n_dest] = DEFINED (PARRAY n_target)',
        'S_dtor.STORE[n_tail] = DEFINED (PINT 8)',
        owners('S_dtor', 'HARRAY n_pool', '$(n_pool_roots + 2)'),
    ] + field('S_dtor', 'n_pool', 'eps') + public('S_dtor')
    checks += seek('S_dtor', 633, 'S_mutated') + field(
        'S_mutated', 'n_field', '[ENTRY (KINT 0) (DIRECT (PINT 44))]') + [
        'n_field =/= n_pool', 'n_field =/= n_target',
        'S_mutated.ARRAYS[n_pool].ITEMS = eps',
        'S_mutated.STORE[n_saved] = DEFINED (PARRAY n_pool)',
        'S_mutated.POOLS = S_cache.POOLS',
        '$heap_count(HARRAY n_field, $pools_nodes(S_mutated.POOLS)) = 0',
        '~$array_immutable(S_mutated, n_field)',
        owners('S_mutated', 'HARRAY n_field', 1),
        owners('S_mutated', 'HARRAY n_pool', '$(n_pool_roots + 1)'),
    ] + public('S_mutated')
    checks += seek('S_mutated', 634, 'S_release') + [
        'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_field) :: ptask_storage_tail*',
        'pdestructionrelease_field.JOBS = (DESTRUCTION_VALUE (HOBJECT n_object)) :: pdestructionjob_tail*',
        '$destructor_release_valid(S_release, pdestructionrelease_field)',
        'S_release.STORE[n_other] = DEFINED (PINT 42)',
        'S_release.STORE[n_tail] = DEFINED (PINT 20)',
        '$weakref_get(S_release, n_observer) = POBJECT n_object',
        'PhpStep: S_release ~> S_storage',
        'S_storage.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: (DESTRUCTOR_RELEASE pdestructionrelease_after) :: ptask_storage_tail*',
        'pdestructionrelease_after = pdestructionrelease_field[.JOBS = pdestructionjob_tail*]',
        'pinstancestorage.OBJECT = n_object', 'pinstancestorage.NEXT = 0',
        '$instance_storage_valid(S_storage, pinstancestorage)',
        '$weakref_get(S_storage, n_observer) = PNULL',
        owners('S_storage', 'HARRAY n_field', 1),
        'PhpStep: S_storage ~> S_slot',
        'S_slot.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_slot) :: (INSTANCE_STORAGE_STEP pinstancestorage_next) :: (DESTRUCTOR_RELEASE pdestructionrelease_after) :: ptask_storage_tail*',
        'pdestructionrelease_slot.JOBS = [DESTRUCTION_VALUE (HARRAY n_field)]',
        'pinstancestorage_next.NEXT = 1',
        '$instance_storage_valid(S_slot, pinstancestorage_next)',
        '(HOBJECT n_object) <- S_slot.ALLOCATIONS',
        '$node_children(S_slot, HOBJECT n_object) = eps',
        owners('S_slot', 'HARRAY n_field', 1),
        owners('S_slot', 'HARRAY n_pool', '$(n_pool_roots + 1)'),
    ] + public('S_release') + public('S_storage') + public('S_slot') + budget('S_release', 'S_release_budget')
    checks += seek('S_slot', 635, 'S_read') + [
        '~((HOBJECT n_object) <- S_read.ALLOCATIONS)',
        '~((HARRAY n_field) <- S_read.ALLOCATIONS)',
        '$weakref_get(S_read, n_observer) = PNULL',
        'S_read.STORE[n_dest] = DEFINED (PARRAY n_target)',
        'S_read.STORE[n_tail] = DEFINED (PINT 20)',
        'S_read.STORE[n_other] = DEFINED (PINT 42)',
        'S_read.STORE[n_saved] = DEFINED (PARRAY n_pool)',
        'S_read.ARRAYS[n_pool].ITEMS = eps', 'S_read.POOLS = S_cache.POOLS',
        'S_read.ARRAYS[n_target].ITEMS = S_before.ARRAYS[n_target].ITEMS',
        'S_read.ARRAYS[n_new].ITEMS = S_before.ARRAYS[n_new].ITEMS',
        'S_read.ARRAYS[n_new_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 11))]',
        owners('S_read', 'HARRAY n_pool', '$(n_pool_roots + 1)'),
    ] + public('S_read')
    return checks + finish('S_read', stdout, [
        'HOBJECT n_object', 'HOBJECT n_observer',
        'HCELL n_it', 'HCELL n_outer', 'HCELL n_leaf', 'HCELL n_other',
        'HCELL n_dest', 'HCELL n_saved', 'HCELL n_watch', 'HCELL n_tail',
        'HARRAY n_old', 'HARRAY n_new', 'HARRAY n_target', 'HARRAY n_field',
    ]) + [
        'S_done.POOLS = S_cache.POOLS', '(HARRAY n_pool) <- S_done.ALLOCATIONS',
        'S_done.ARRAYS[n_pool].ITEMS = eps',
        '$heap_count(HARRAY n_pool, $pools_nodes(S_done.POOLS)) = n_pool_roots',
        owners('S_done', 'HARRAY n_pool', 'n_pool_roots'),
    ]


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS, extra_inputs=(
        Path(__file__), Path(__file__).with_name('array_aggregate_unpack_state_review.py'),
        Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
