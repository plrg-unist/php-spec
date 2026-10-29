#!/usr/bin/env python3
"""BYVAL cached table, sole-leaf COW, and invalid-key DATA cleanup."""
from pathlib import Path
from types import SimpleNamespace

import array_iterator_byval_fields_review_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial
from array_generator_unpack_state_review import finish, owners, public, singleton

SELECTED = 'array-iterator-byval-fields-invalid-sole-leaf'
PEER = SimpleNamespace(CASES={SELECTED: cases.CASES[SELECTED]}, __file__=cases.__file__)

HELPERS = shared.HELPERS + r'''
dec $a65_peer_reach(pstate, nat) : pstate
def $a65_peer_reach(S, n_stage) = S_found[.COMPLETION = NORMAL]
  -- if S_found = $list_warning_seek(S, n_stage, 3000)
  -- if S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET
dec $a65_peer_echo(pstate, ptbytes) : bool
def $a65_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a65_peer_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 650) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "key-start") :: ptask*
def $list_warning_frontier(S, 651) = $a65_peer_echo(S, $ptascii("K:"))
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ARRAY_ITERATOR parrayiterator "key") :: ptask*
def $list_warning_frontier(S, 652) = $a65_peer_echo(S, $ptascii("D:"))
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
def $list_warning_frontier(S, 653) = $a65_peer_echo(S, $ptascii("M:"))
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
def $list_warning_frontier(S, 654) = $a65_peer_echo(S, $ptascii("E:"))
  -- if S.CURRENT = eps /\ S.FRAMES = eps
'''


def seek(start, stage, state):
    return [f'{state} = $a65_peer_reach({start}, {stage})',
            f'$list_warning_frontier({state}, {stage})']


def fields(state, hold, row):
    tag = state.lower()
    return [
        f'$objectprops_record_at({state}.OBJECTPROPS, n_object) = (pobjectprops_{tag})',
        f'$property_slot_at(pobjectprops_{tag}.SLOTS, $ptascii("hold")) = (ppropertyslot_{tag}_hold)',
        f'ppropertyslot_{tag}_hold.STATE = PROP_VALUE (DIRECT (PARRAY {hold}))',
        f'$property_slot_at(pobjectprops_{tag}.SLOTS, $ptascii("row")) = (ppropertyslot_{tag}_row)',
        f'ppropertyslot_{tag}_row.STATE = PROP_VALUE (DIRECT (PARRAY {row}))',
        f'$node_children({state}, HOBJECT n_object) = [HARRAY {hold},HARRAY {row}]',
    ]


def row_items(state, root, child, leaf):
    return f'{state}.ARRAYS[{root}].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY {child})),ENTRY (KINT 1) ({leaf})]'


def conditions(name, program, path, stdout):
    checks = initial(program, path) + seek('S_initial', 650, 'S_cache') + [
        'S_cache.TODO = (ARRAY_ITERATOR parrayiterator "key-start") :: ptask_tail*',
        'parrayiterator.OBJECT = n_object', 'parrayiterator.ARRAY = n_target',
        'parrayiterator.CURRENT = KNOWN (PARRAY n_old)',
        '$lookup(S_cache.ENV, $ptascii("it")) = eps',
        '$lookup(S_cache.ENV, $ptascii("leaf")) = eps',
        '$lookup(S_cache.ENV, $ptascii("saved")) = (n_saved)',
        'S_cache.STORE[n_saved] = DEFINED (PARRAY n_old)',
        '$lookup(S_cache.ENV, $ptascii("other")) = (n_other)',
        '$lookup(S_cache.ENV, $ptascii("dest")) = (n_dest)',
        '$lookup(S_cache.ENV, $ptascii("tail")) = (n_tail)',
        '$lookup(S_cache.ENV, $ptascii("seed")) = (n_seed)',
        '$lookup(S_cache.ENV, $ptascii("watch")) = (n_watch)',
        'S_cache.STORE[n_watch] = DEFINED (POBJECT n_observer)',
        '$weakref_get(S_cache, n_observer) = POBJECT n_object',
        '$array_iterator_destructor(S_cache, n_object)',
        '~$array_iterator_byref_current(S_cache, parrayiterator)',
        '~$array_iterator_destructor_byref_current(S_cache, parrayiterator)',
        '$array_iterator_owned_field(S_cache, parrayiterator)',
        '$array_iterator_current_value(S_cache, parrayiterator, KNOWN (PARRAY n_old)) = (PARRAY n_old)',
        '$array_iterator_ready(S_cache, parrayiterator)',
    ] + fields('S_cache', 'n_old', 'n_old') + [
        row_items('S_cache', 'n_old', 'n_child', 'ALIAS n_leaf'),
        singleton('S_cache', 'n_child', 3),
        'S_cache.STORE[n_leaf] = DEFINED (PINT 2)',
        '$array_iterator_reference_cell(S_cache, n_leaf) = (PINT 2)',
        '$array_iterator_current_value(S_cache, parrayiterator, REFERENCE n_leaf) = eps',
        'S_cache.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8)),ENTRY (KINT 5) (ALIAS n_other)]',
        '$heap_count(HARRAY n_old, $pools_nodes(S_cache.POOLS)) = 0',
        '$heap_count(HARRAY n_child, $pools_nodes(S_cache.POOLS)) = 0',
        owners('S_cache', 'HOBJECT n_object', 1),
        owners('S_cache', 'HARRAY n_old', 4),
        owners('S_cache', 'HARRAY n_child', 1),
        owners('S_cache', 'HCELL n_leaf', 1),
    ] + public('S_cache')
    checks += seek('S_cache', 651, 'S_key') + fields('S_key', 'n_old', 'n_new') + [
        'S_key.CURRENT = (pcallcontext_key)',
        'S_key.FRAMES = pframe_key :: pframe_key_tail*',
        'pframe_key.TODO = (ARRAY_ITERATOR parrayiterator_key "key") :: ptask_key_tail*',
        'parrayiterator_key.CURRENT = KNOWN (PARRAY n_old)',
        'parrayiterator_key.OBJECT = n_object', 'parrayiterator_key.ARRAY = n_target',
        '$array_iterator_frame(S_key, pcallcontext_key, pframe_key)',
        row_items('S_key', 'n_new', 'n_new_child', 'DIRECT (PINT 17)'),
        singleton('S_key', 'n_new_child', 22),
        'n_new =/= n_old', 'n_new_child =/= n_child',
        row_items('S_key', 'n_old', 'n_child', 'ALIAS n_leaf'),
        'S_key.STORE[n_leaf] = DEFINED (PINT 2)',
        owners('S_key', 'HARRAY n_old', 3),
        owners('S_key', 'HARRAY n_child', 1),
        owners('S_key', 'HCELL n_leaf', 1),
    ] + public('S_key')
    checks += seek('S_key', 652, 'S_dtor') + [
        'S_dtor.CURRENT = (pcallcontext_dtor)',
        '$destructor_context_call(pcallcontext_dtor, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object', 'pdestructorcall.PENDING = (n_pending)',
        '$destructor_call_live(S_dtor, pdestructorcall)',
        '$throwable_live(S_dtor, n_pending)',
        '$throwable_field(S_dtor, n_pending, "previous") = PNULL',
        '$weakref_get(S_dtor, n_observer) = POBJECT n_object',
        'S_dtor.ITERATORS = eps', 'S_dtor.STORE[n_dest] = DEFINED (PINT 99)',
        'S_dtor.STORE[n_tail] = DEFINED (PINT 7)',
        'S_dtor.ARRAYS[n_target].ITEMS = S_cache.ARRAYS[n_target].ITEMS',
        owners('S_dtor', 'HARRAY n_old', 2),
        owners('S_dtor', 'HARRAY n_child', 1),
        owners('S_dtor', 'HCELL n_leaf', 1),
    ] + fields('S_dtor', 'n_old', 'n_new') + public('S_dtor')
    checks += seek('S_dtor', 653, 'S_mutated') + fields('S_mutated', 'n_private', 'n_new') + [
        row_items('S_mutated', 'n_private', 'n_private_child', 'DIRECT (PINT 31)'),
        singleton('S_mutated', 'n_private_child', 44),
        row_items('S_mutated', 'n_new', 'n_new_child', 'DIRECT (PINT 66)'),
        singleton('S_mutated', 'n_new_child', 55),
        'n_private =/= n_old', 'n_private_child =/= n_child',
        row_items('S_mutated', 'n_old', 'n_child', 'ALIAS n_leaf'),
        singleton('S_mutated', 'n_child', 3),
        'S_mutated.STORE[n_leaf] = DEFINED (PINT 2)',
        'S_mutated.STORE[n_other] = DEFINED (PINT 42)',
        'S_mutated.STORE[n_tail] = DEFINED (PINT 20)',
        'S_mutated.STORE[n_dest] = DEFINED (PINT 99)',
        owners('S_mutated', 'HARRAY n_old', 1),
        owners('S_mutated', 'HCELL n_leaf', 1),
    ] + public('S_mutated')
    checks += seek('S_mutated', 654, 'S_caught') + [
        '$lookup(S_caught.ENV, $ptascii("e")) = (n_error)',
        'S_caught.STORE[n_error] = DEFINED (POBJECT n_pending)',
        '$throwable_field(S_caught, n_pending, "previous") = PNULL',
        'S_caught.STORE[n_dest] = DEFINED (PINT 99)',
        'S_caught.STORE[n_saved] = DEFINED (PARRAY n_old)',
        'S_caught.STORE[n_other] = DEFINED (PINT 42)',
        'S_caught.STORE[n_tail] = DEFINED (PINT 20)',
        '~((HOBJECT n_object) <- S_caught.ALLOCATIONS)',
        '~((HARRAY n_target) <- S_caught.ALLOCATIONS)',
        '~((HARRAY n_private) <- S_caught.ALLOCATIONS)',
        '~((HARRAY n_private_child) <- S_caught.ALLOCATIONS)',
        '~((HARRAY n_new) <- S_caught.ALLOCATIONS)',
        '~((HARRAY n_new_child) <- S_caught.ALLOCATIONS)',
        '$weakref_get(S_caught, n_observer) = PNULL',
        row_items('S_caught', 'n_old', 'n_child', 'ALIAS n_leaf'),
        'S_caught.STORE[n_leaf] = DEFINED (PINT 2)',
        owners('S_caught', 'HARRAY n_old', 1),
        owners('S_caught', 'HARRAY n_child', 1),
        owners('S_caught', 'HCELL n_leaf', 1),
        owners('S_caught', 'HCELL n_other', 1),
        'S_caught.POOLS = S_cache.POOLS',
    ] + public('S_caught')
    return checks + finish('S_caught', stdout, [
        'HOBJECT n_object', 'HOBJECT n_observer', 'HOBJECT n_pending',
        'HCELL n_leaf', 'HCELL n_other', 'HCELL n_saved', 'HCELL n_dest',
        'HCELL n_tail', 'HCELL n_seed', 'HCELL n_watch', 'HCELL n_error',
        'HARRAY n_old', 'HARRAY n_child', 'HARRAY n_new', 'HARRAY n_new_child',
        'HARRAY n_private', 'HARRAY n_private_child', 'HARRAY n_target',
    ])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(PEER, conditions, HELPERS, model_timeout=300, extra_inputs=(
        Path(__file__), Path(__file__).with_name('array_aggregate_unpack_state_review.py'),
        Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
