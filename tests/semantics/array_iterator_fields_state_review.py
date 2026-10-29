#!/usr/bin/env python3
"""Shared physical edges and a retained selected row through field retirement."""
from pathlib import Path

import array_iterator_fields_review_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial
from array_generator_unpack_state_review import finish, owners, public, singleton

HELPERS = shared.HELPERS + r'''
dec $a64_peer_reach(pstate, nat) : pstate
def $a64_peer_reach(S, n_stage) = S_found[.COMPLETION = NORMAL]
  -- if S_found = $list_warning_seek(S, n_stage, 3000)
  -- if S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET
dec $a64_peer_echo(pstate, ptbytes) : bool
def $a64_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a64_peer_echo(S, n_prefix*) = false -- otherwise
dec $a64_peer_storage(pstate, nat) : bool
def $a64_peer_storage(S, n_next) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*
  -- if pinstancestorage.NEXT = n_next
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if $instance_storage_valid(S, pinstancestorage)
def $a64_peer_storage(S, n_next) = false -- otherwise
def $list_warning_frontier(S, 640) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "key-start") :: ptask*
def $list_warning_frontier(S, 641) = $a64_peer_echo(S, $ptascii("B:"))
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 642) = $a64_peer_echo(S, $ptascii("M:"))
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
def $list_warning_frontier(S, 643) = $a64_peer_storage(S, 0)
def $list_warning_frontier(S, 644) = $a64_peer_storage(S, 1)
def $list_warning_frontier(S, 645) = $a64_peer_storage(S, 2)
def $list_warning_frontier(S, 646) = $a64_peer_storage(S, 3)
def $list_warning_frontier(S, 647) = $a64_peer_echo(S, $ptascii("R:"))
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 648) = $a64_peer_echo(S, $ptascii("S:"))
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 649) = $a64_peer_echo(S, $ptascii("T:"))
  -- if S.CURRENT = eps /\ S.FRAMES = eps
'''


def seek(start, stage, state):
    return [f'{state} = $a64_peer_reach({start}, {stage})',
            f'$list_warning_frontier({state}, {stage})']


def fields(state, first, second, row):
    suffix = state.lower()
    return [
        f'$objectprops_record_at({state}.OBJECTPROPS, n_object) = (pobjectprops_{suffix})',
        f'$property_slot_at(pobjectprops_{suffix}.SLOTS, $ptascii("first")) = (ppropertyslot_{suffix}_first)',
        f'ppropertyslot_{suffix}_first.STATE = PROP_VALUE (DIRECT (PARRAY {first}))',
        f'$property_slot_at(pobjectprops_{suffix}.SLOTS, $ptascii("second")) = (ppropertyslot_{suffix}_second)',
        f'ppropertyslot_{suffix}_second.STATE = PROP_VALUE (DIRECT (PARRAY {second}))',
        f'$property_slot_at(pobjectprops_{suffix}.SLOTS, $ptascii("row")) = (ppropertyslot_{suffix}_row)',
        f'ppropertyslot_{suffix}_row.STATE = PROP_VALUE (ALIAS n_outer)',
        f'{state}.STORE[n_outer] = DEFINED (PARRAY {row})',
        f'$node_children({state}, HOBJECT n_object) = [HARRAY {first},HARRAY {second},HCELL n_outer]',
    ]


def pair(state, root, child):
    return f'{state}.ARRAYS[{root}].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY {child})),ENTRY (KINT 1) (DIRECT (PINT 1))]'


def storage(start, stage, state, next_slot):
    return seek(start, stage, state) + [
        f'{state}.TODO = (INSTANCE_STORAGE_STEP pinstancestorage_{next_slot}) :: ptask_storage_{next_slot}*',
        f'pinstancestorage_{next_slot}.OBJECT = n_object',
        f'pinstancestorage_{next_slot}.NEXT = {next_slot}',
    ] + public(state)


def conditions(name, program, path, stdout):
    checks = initial(program, path) + seek('S_initial', 640, 'S_cache') + [
        'S_cache.TODO = (ARRAY_ITERATOR parrayiterator "key-start") :: ptask_tail*',
        'parrayiterator.OBJECT = n_object', 'parrayiterator.ARRAY = n_target',
        'parrayiterator.CURRENT = REFERENCE n_outer',
        '$lookup(S_cache.ENV, $ptascii("it")) = (n_it)',
        'S_cache.STORE[n_it] = DEFINED (POBJECT n_object)',
        '$lookup(S_cache.ENV, $ptascii("saved")) = (n_saved)',
        'S_cache.STORE[n_saved] = DEFINED (PARRAY n_shared)',
        '$lookup(S_cache.ENV, $ptascii("seed")) = (n_seed)',
        '$lookup(S_cache.ENV, $ptascii("leaf")) = (n_leaf)',
        '$lookup(S_cache.ENV, $ptascii("other")) = (n_other)',
        '$lookup(S_cache.ENV, $ptascii("dest")) = (n_dest)',
        '$lookup(S_cache.ENV, $ptascii("tail")) = (n_tail)',
        '$lookup(S_cache.ENV, $ptascii("watch")) = (n_watch)',
        'S_cache.STORE[n_watch] = DEFINED (POBJECT n_observer)',
        '$weakref_get(S_cache, n_observer) = POBJECT n_object',
        '$array_iterator_ready(S_cache, parrayiterator)',
    ] + fields('S_cache', 'n_shared', 'n_shared', 'n_old') + [
        pair('S_cache', 'n_shared', 'n_child'),
        'S_cache.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_child)),ENTRY (KINT 1) (ALIAS n_leaf)]',
        singleton('S_cache', 'n_child', 3),
        '$heap_count(HARRAY n_child, $pools_nodes(S_cache.POOLS)) = 0',
        '$heap_count(HARRAY n_shared, $node_children(S_cache, HOBJECT n_object)) = 2',
        owners('S_cache', 'HOBJECT n_object', 2),
        owners('S_cache', 'HCELL n_outer', 2),
        owners('S_cache', 'HARRAY n_shared', 3),
        owners('S_cache', 'HARRAY n_child', 2),
        'S_scalar = S_cache[.STORE[n_outer] = DEFINED (PINT 17)]',
        '$array_iterator_ready(S_scalar, parrayiterator)',
    ] + public('S_cache')
    checks += seek('S_cache', 641, 'S_before') + fields('S_before', 'n_shared', 'n_second', 'n_row') + [
        pair('S_before', 'n_second', 'n_second_child'),
        singleton('S_before', 'n_second_child', 22),
        'n_second =/= n_shared', 'n_second_child =/= n_child',
        'S_before.ARRAYS[n_row].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_child)),ENTRY (KINT 1) (ALIAS n_other)]',
        'n_row =/= n_old', '~((HARRAY n_old) <- S_before.ALLOCATIONS)',
        'S_before.STORE[n_dest] = DEFINED (PARRAY n_target)',
        'S_before.ARRAYS[n_target].ITEMS = [ENTRY (KSTRING ($ptascii("row"))) (DIRECT (PARRAY n_row)),ENTRY (KINT 0) (DIRECT (PINT 7))]',
        'S_before.STORE[n_tail] = DEFINED (PINT 8)',
        'S_before.ITERATORS = eps',
        owners('S_before', 'HOBJECT n_object', 1),
        owners('S_before', 'HCELL n_outer', 1),
        owners('S_before', 'HARRAY n_shared', 2),
        owners('S_before', 'HARRAY n_child', 2),
        owners('S_before', 'HARRAY n_row', 2),
        '$array_iterator_ready(S_before, parrayiterator)',
        'S_cycle = S_before[.ARRAYS[n_second_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_second))]]',
        '~$array_iterator_ready(S_cycle, parrayiterator)',
        'S_backedge = S_before[.ARRAYS[n_second_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_target))]]',
        '~$array_iterator_ready(S_backedge, parrayiterator)',
    ] + public('S_before')
    checks += seek('S_before', 642, 'S_mutated') + fields('S_mutated', 'n_first_private', 'n_second', 'n_row_private') + [
        pair('S_mutated', 'n_first_private', 'n_first_child'),
        singleton('S_mutated', 'n_first_child', 44),
        'S_mutated.ARRAYS[n_row_private].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_row_child)),ENTRY (KINT 1) (ALIAS n_other)]',
        singleton('S_mutated', 'n_row_child', 55),
        'n_first_private =/= n_shared', 'n_row_private =/= n_row',
        'n_first_child =/= n_child', 'n_row_child =/= n_child',
        'n_first_child =/= n_row_child',
        singleton('S_mutated', 'n_child', 3),
        'S_mutated.STORE[n_saved] = DEFINED (PARRAY n_shared)',
        'S_mutated.ARRAYS[n_shared].ITEMS = S_cache.ARRAYS[n_shared].ITEMS',
        'S_mutated.ARRAYS[n_row].ITEMS = S_before.ARRAYS[n_row].ITEMS',
        'S_mutated.STORE[n_other] = DEFINED (PINT 42)',
        'S_mutated.STORE[n_tail] = DEFINED (PINT 20)',
        '$weakref_get(S_mutated, n_observer) = POBJECT n_object',
        owners('S_mutated', 'HARRAY n_child', 2),
        owners('S_mutated', 'HARRAY n_shared', 1),
        owners('S_mutated', 'HARRAY n_row', 1),
    ] + public('S_mutated')
    checks += storage('S_mutated', 643, 'S_storage', 0) + [
        '$weakref_get(S_storage, n_observer) = PNULL',
        owners('S_storage', 'HOBJECT n_object', 1),
        owners('S_storage', 'HARRAY n_child', 2),
    ]
    checks += storage('S_storage', 644, 'S_first_gone', 1) + [
        '~((HARRAY n_first_private) <- S_first_gone.ALLOCATIONS)',
        '~((HARRAY n_first_child) <- S_first_gone.ALLOCATIONS)',
        '$node_children(S_first_gone, HOBJECT n_object) = [HARRAY n_second,HCELL n_outer]',
        owners('S_first_gone', 'HARRAY n_child', 2),
    ]
    checks += storage('S_first_gone', 645, 'S_second_gone', 2) + [
        '~((HARRAY n_second) <- S_second_gone.ALLOCATIONS)',
        '~((HARRAY n_second_child) <- S_second_gone.ALLOCATIONS)',
        '$node_children(S_second_gone, HOBJECT n_object) = [HCELL n_outer]',
        owners('S_second_gone', 'HARRAY n_child', 2),
    ]
    checks += storage('S_second_gone', 646, 'S_fields_gone', 3) + [
        '~((HCELL n_outer) <- S_fields_gone.ALLOCATIONS)',
        '~((HARRAY n_row_private) <- S_fields_gone.ALLOCATIONS)',
        '~((HARRAY n_row_child) <- S_fields_gone.ALLOCATIONS)',
        '$node_children(S_fields_gone, HOBJECT n_object) = eps',
        owners('S_fields_gone', 'HARRAY n_child', 2),
    ]
    checks += seek('S_fields_gone', 647, 'S_read') + [
        '~((HOBJECT n_object) <- S_read.ALLOCATIONS)',
        '$weakref_get(S_read, n_observer) = PNULL',
        'S_read.STORE[n_saved] = DEFINED (PARRAY n_shared)',
        'S_read.STORE[n_dest] = DEFINED (PARRAY n_target)',
        'S_read.ARRAYS[n_target].ITEMS = S_before.ARRAYS[n_target].ITEMS',
        'S_read.ARRAYS[n_row].ITEMS = S_before.ARRAYS[n_row].ITEMS',
        singleton('S_read', 'n_child', 3),
        owners('S_read', 'HARRAY n_child', 2),
    ] + public('S_read')
    checks += seek('S_read', 648, 'S_saved_write') + [
        pair('S_saved_write', 'n_shared', 'n_saved_child'),
        singleton('S_saved_write', 'n_saved_child', 66),
        'n_saved_child =/= n_child',
        singleton('S_saved_write', 'n_child', 3),
        owners('S_saved_write', 'HARRAY n_child', 1),
    ] + public('S_saved_write')
    checks += seek('S_saved_write', 649, 'S_unique') + [
        '~((HARRAY n_shared) <- S_unique.ALLOCATIONS)',
        '~((HARRAY n_saved_child) <- S_unique.ALLOCATIONS)',
        'S_unique.ARRAYS[n_row].ITEMS = S_before.ARRAYS[n_row].ITEMS',
        singleton('S_unique', 'n_child', 77),
        owners('S_unique', 'HARRAY n_child', 1),
        'S_unique.POOLS = S_cache.POOLS',
    ] + public('S_unique')
    return checks + finish('S_unique', stdout, [
        'HOBJECT n_object', 'HOBJECT n_observer',
        'HCELL n_it', 'HCELL n_outer', 'HCELL n_seed', 'HCELL n_leaf',
        'HCELL n_other', 'HCELL n_dest', 'HCELL n_saved', 'HCELL n_watch', 'HCELL n_tail',
        'HARRAY n_shared', 'HARRAY n_child', 'HARRAY n_old', 'HARRAY n_row',
        'HARRAY n_target', 'HARRAY n_second', 'HARRAY n_second_child',
        'HARRAY n_first_private', 'HARRAY n_first_child',
        'HARRAY n_row_private', 'HARRAY n_row_child', 'HARRAY n_saved_child',
    ]) + ['S_done.POOLS = S_cache.POOLS']


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS, model_timeout=300, extra_inputs=(
        Path(__file__), Path(__file__).with_name('array_aggregate_unpack_state_review.py'),
        Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
