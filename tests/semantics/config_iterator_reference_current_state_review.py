#!/usr/bin/env python3
"""Selected-cell snapshots and last-cache-owner CONFIG exception cleanup."""
from pathlib import Path
from types import SimpleNamespace

import config_iterator_reference_current_review_cases as snapshot
import config_iterator_reference_current_cleanup_cases as cleanup
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial, seek
from array_generator_unpack_state_review import budget, finish, owners, public

NORMAL = 'config-iterator-reference-current-review-selected-cell-snapshot'
CACHE = 'config-reference-current-cache-only-throw'
CASES = SimpleNamespace(CASES={NORMAL: snapshot.CASES[NORMAL], CACHE: cleanup.CASES[CACHE]},
                        __file__=snapshot.__file__)

HELPERS = shared.HELPERS + r'''
dec $a66_peer_echo(pstate, ptbytes) : bool
def $a66_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a66_peer_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 900) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "key-start") :: ptask*
  -- if |pconfigiterator.ITEMS| = 1
def $list_warning_frontier(S, 901) = $a66_peer_echo(S, $ptascii("Q:"))
def $list_warning_frontier(S, 902) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "send") :: ptask*
  -- if |pconfigiterator.ITEMS| = 1
def $list_warning_frontier(S, 903) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "next-start") :: ptask*
  -- if |pconfigiterator.ITEMS| = 2
def $list_warning_frontier(S, 904) = $a66_peer_echo(S, $ptascii("D:"))
def $list_warning_frontier(S, 905) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "ready") :: ptask*
def $list_warning_frontier(S, 906) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "key-start") :: ptask*
  -- if pconfigiterator.ITEMS = eps
def $list_warning_frontier(S, 907) = $a66_peer_echo(S, $ptascii("X:"))
def $list_warning_frontier(S, 908) = $a66_peer_echo(S, $ptascii("E:"))
'''


def string(state, cell, value):
    return [f'{state}.STORE[{cell}] = DEFINED pvalue_{state.lower()}_{cell}',
            f'$string_bytes(pvalue_{state.lower()}_{cell}) = ($ptascii("{value}"))']


def fields(state, value_cell):
    tag = state.lower()
    return [f'$objectprops_record_at({state}.OBJECTPROPS, n_object) = (pobjectprops_{tag})',
            f'$property_slot_at(pobjectprops_{tag}.SLOTS, $ptascii("name")) = (ppropertyslot_name_{tag})',
            f'ppropertyslot_name_{tag}.STATE = PROP_VALUE (ALIAS n_name)',
            f'$property_slot_at(pobjectprops_{tag}.SLOTS, $ptascii("value")) = (ppropertyslot_value_{tag})',
            f'ppropertyslot_value_{tag}.STATE = PROP_VALUE (ALIAS {value_cell})',
            f'$node_children({state}, HOBJECT n_object) = [HCELL n_name,HCELL {value_cell}]']


def normal(program, path, stdout):
    checks = initial(program, path) + seek('S_initial', 900, 'S_cache') + [
        'S_cache.TODO = (CONFIG_ITERATOR pconfigiterator_cache "key-start") :: ptask_cache*',
        'pconfigiterator_cache.OBJECT = n_object',
        'pconfigiterator_cache.CURRENT = REFERENCE n_old',
        'pconfigiterator_cache.PRODUCER = (n_aggregate)',
        'pconfigiterator_cache.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_name)]',
        '$string_bytes(pvalue_name) = ($ptascii("precision"))',
        '$lookup(S_cache.ENV, $ptascii("held")) = (n_old)',
        '$lookup(S_cache.ENV, $ptascii("fresh")) = (n_fresh)',
        '$lookup(S_cache.ENV, $ptascii("nameRef")) = (n_name)',
        '$lookup(S_cache.ENV, $ptascii("watch")) = (n_watch)',
        'S_cache.STORE[n_watch] = DEFINED (POBJECT n_observer)',
        '~((HOBJECT n_aggregate) <- S_cache.ALLOCATIONS)',
        '$config_iterator_byref_current(S_cache, pconfigiterator_cache)',
        '$config_iterator_valid(S_cache, pconfigiterator_cache, "key-start")',
        owners('S_cache', 'HCELL n_old', 3), owners('S_cache', 'HCELL n_fresh', 1),
    ] + fields('S_cache', 'n_old') + string('S_cache', 'n_old', '3') + public('S_cache')
    checks += seek('S_cache', 901, 'S_key') + [
        'S_key.CURRENT = (pcallcontext_key)',
        'S_key.FRAMES = pframe_key :: pframe_key_tail*',
        'pframe_key.TODO = (CONFIG_ITERATOR pconfigiterator_key "key") :: ptask_key*',
        'pconfigiterator_key.OBJECT = n_object',
        'pconfigiterator_key.CURRENT = REFERENCE n_old',
        'pconfigiterator_key.ITEMS = pconfigiterator_cache.ITEMS',
        '$config_iterator_frame(S_key, pcallcontext_key, pframe_key)',
        owners('S_key', 'HCELL n_old', 2), owners('S_key', 'HCELL n_fresh', 2),
    ] + fields('S_key', 'n_fresh') + string('S_key', 'n_old', '17') + string('S_key', 'n_fresh', '23') + string('S_key', 'n_name', 'serialize_precision') + public('S_key')
    checks += seek('S_key', 902, 'S_send') + [
        'S_send.TODO = (CONFIG_ITERATOR pconfigiterator_send "send") :: ptask_send*',
        'pconfigiterator_send.OBJECT = n_object',
        'pconfigiterator_send.CURRENT = REFERENCE n_old',
        'pconfigiterator_send.KEY = KNOWN (PINT 1)',
        '$config_iterator_current_value(S_send, pconfigiterator_send, REFERENCE n_old) = (pvalue_sent)',
        '$string_bytes(pvalue_sent) = ($ptascii("17"))',
    ] + public('S_send') + budget('S_send', 'S_send_budget') + seek('S_send', 903, 'S_sent') + [
        'S_sent.TODO = (CONFIG_ITERATOR pconfigiterator_sent "next-start") :: ptask_sent*',
        'pconfigiterator_sent.CURRENT = KNOWN PNULL',
        'pconfigiterator_sent.KEY = KNOWN PNULL',
        'pconfigiterator_sent.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_name),ENTRY (KINT 1) (DIRECT pvalue_sent)]',
        owners('S_sent', 'HCELL n_old', 1),
    ] + public('S_sent') + seek('S_sent', 904, 'S_dtor') + [
        'S_dtor.CURRENT = (pcallcontext_dtor)',
        '$destructor_context_call(pcallcontext_dtor, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object', 'pdestructorcall.PENDING = eps',
        '$destructor_call_live(S_dtor, pdestructorcall)',
        '$weakref_get(S_dtor, n_observer) = POBJECT n_object',
        'S_dtor.ITERATORS = eps', owners('S_dtor', 'HCELL n_old', 1),
    ] + fields('S_dtor', 'n_fresh') + public('S_dtor') + seek('S_dtor', 905, 'S_ready') + [
        'S_ready.TODO = (CONFIG_ITERATOR pconfigiterator_ready "ready") :: ptask_ready*',
        'pconfigiterator_ready.ITEMS = pconfigiterator_sent.ITEMS',
        '$config_iterator_valid(S_ready, pconfigiterator_ready, "ready")',
        '$config_iterator_retired_scope(S_ready, pconfigiterator_ready)',
        '~((HOBJECT n_object) <- S_ready.ALLOCATIONS)',
        '$weakref_get(S_ready, n_observer) = PNULL',
        owners('S_ready', 'HCELL n_old', 1), owners('S_ready', 'HCELL n_fresh', 1),
        owners('S_ready', 'HCELL n_name', 1),
    ] + string('S_ready', 'n_old', '19') + string('S_ready', 'n_fresh', '29') + public('S_ready')
    return checks + finish('S_ready', stdout, ['HOBJECT n_object', 'HOBJECT n_aggregate',
        'HOBJECT n_observer', 'HCELL n_old', 'HCELL n_fresh', 'HCELL n_name'])


def cache_only(program, path, stdout):
    checks = initial(program, path) + seek('S_initial', 906, 'S_cache') + [
        'S_cache.TODO = (CONFIG_ITERATOR pconfigiterator_cache "key-start") :: ptask_cache*',
        'pconfigiterator_cache.OBJECT = n_object',
        'pconfigiterator_cache.INPUT = KNOWN (POBJECT n_object)',
        'pconfigiterator_cache.CURRENT = REFERENCE n_cache',
        '$lookup(S_cache.ENV, $ptascii("saved")) = (n_saved_cell)',
        'S_cache.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)',
        '$lookup(S_cache.ENV, $ptascii("stamp")) = (n_stamp)',
        '$lookup(S_cache.ENV, $ptascii("watch")) = (n_watch)',
        'S_cache.STORE[n_watch] = DEFINED (POBJECT n_observer)',
        '$ordinary_reference_value(S_cache, n_cache) = (POBJECT n_payload)',
        '$config_iterator_current_value(S_cache, pconfigiterator_cache, REFERENCE n_cache) = (POBJECT n_payload)',
        owners('S_cache', 'HCELL n_cache', 2), owners('S_cache', 'HOBJECT n_payload', 1),
        owners('S_cache', 'HOBJECT n_object', 2),
    ] + public('S_cache') + seek('S_cache', 901, 'S_key') + [
        'S_key_globals = $global_table_view(S_key)',
        '$lookup(S_key_globals.ENV, $ptascii("slot")) = eps',
        'S_key.STORE[n_stamp] = DEFINED (PINT 0)',
        '(HCELL n_cache) <- S_key.ALLOCATIONS',
        owners('S_key', 'HCELL n_cache', 1),
        owners('S_key', 'HOBJECT n_payload', 1),
        '$weakref_get(S_key, n_observer) = POBJECT n_object',
    ] + public('S_key') + seek('S_key', 907, 'S_payload') + [
        'S_payload.CURRENT = (pcallcontext_payload)',
        '$destructor_context_call(pcallcontext_payload, S_payload.CURRENT, S_payload.FRAMES) = (pdestructorcall_payload)',
        'pdestructorcall_payload.OBJECT = n_payload',
        'pdestructorcall_payload.PENDING = (n_saved)',
        '$destructor_call_live(S_payload, pdestructorcall_payload)',
        'S_payload.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
        'pdestructionoperation.SOURCE = CONFIG_ITERATOR pconfigiterator_history "key"',
        'pconfigiterator_history.OBJECT = n_object',
        'pconfigiterator_history.INPUT = KNOWN (POBJECT n_object)',
        'pconfigiterator_history.CURRENT = REFERENCE n_cache',
        '$eager_operation_source_valid(S_payload, pdestructionoperation)',
        '~((HCELL n_cache) <- S_payload.ALLOCATIONS)',
        '$ordinary_reference_value(S_payload, n_cache) = eps',
        '$config_iterator_current_receipt(S_payload, pconfigiterator_history, REFERENCE n_cache)',
        '$config_iterator_stage(S_payload, pconfigiterator_history, "key")',
        '$weakref_get(S_payload, n_observer) = POBJECT n_object',
        'S_payload.STORE[n_stamp] = DEFINED (PINT 1)',
        owners('S_payload', 'HOBJECT n_object', 2),
    ] + public('S_payload') + seek('S_payload', 908, 'S_caught') + [
        '$lookup(S_caught.ENV, $ptascii("e")) = (n_error_cell)',
        'S_caught.STORE[n_error_cell] = DEFINED (POBJECT n_saved)',
        '$throwable_field(S_caught, n_saved, "previous") = PNULL',
        '$weakref_get(S_caught, n_observer) = PNULL',
        '~((HCELL n_cache) <- S_caught.ALLOCATIONS)',
        '~((HOBJECT n_payload) <- S_caught.ALLOCATIONS)',
        '~((HOBJECT n_object) <- S_caught.ALLOCATIONS)',
        'S_caught.STORE[n_stamp] = DEFINED (PINT 1)',
    ] + public('S_caught')
    return checks + finish('S_caught', stdout, ['HCELL n_cache', 'HOBJECT n_payload',
        'HOBJECT n_object', 'HOBJECT n_observer', 'HOBJECT n_saved'])


def conditions(name, program, path, stdout):
    return normal(program, path, stdout) if name == NORMAL else cache_only(program, path, stdout)


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(CASES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__), Path(cleanup.__file__),
                      Path(__file__).with_name('array_aggregate_unpack_state_review.py'),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
