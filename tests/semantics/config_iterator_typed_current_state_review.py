#!/usr/bin/env python3
"""Instance/static type-source detach with a retained selected CONFIG cell."""
from pathlib import Path

import config_iterator_values_review_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial, seek
from array_generator_unpack_state_review import budget, finish, owners, public

NORMAL = 'config-typed-current-review-instance-static-detach-snapshot'
THROW = 'config-typed-current-review-instance-static-detach-throw'

HELPERS = shared.HELPERS + r'''
dec $a67_peer_echo(pstate, ptbytes) : bool
def $a67_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a67_peer_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 910) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "key-start") :: ptask*
  -- if |pconfigiterator.ITEMS| = 1
def $list_warning_frontier(S, 911) = $a67_peer_echo(S, $ptascii("Q:"))
def $list_warning_frontier(S, 912) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "send") :: ptask*
  -- if |pconfigiterator.ITEMS| = 1
def $list_warning_frontier(S, 913) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "next-start") :: ptask*
  -- if |pconfigiterator.ITEMS| = 2
def $list_warning_frontier(S, 914) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "ready") :: ptask*
def $list_warning_frontier(S, 915) = $a67_peer_echo(S, $ptascii("E:"))
def $list_warning_frontier(S, 916) = $a67_peer_echo(S, $ptascii("D:"))
'''


def string(state, cell, value):
    return [f'{state}.STORE[{cell}] = DEFINED pvalue_{state.lower()}_{cell}',
            f'$string_bytes(pvalue_{state.lower()}_{cell}) = ($ptascii("{value}"))']


def static(state, cell):
    return [f'$class_static_at({state}.CLASSSTATICS, ppropertyid_static) = (pclassstatic_{state.lower()})',
            f'pclassstatic_{state.lower()}.STATE = PROP_VALUE (ALIAS {cell})']


def detached(state, cell):
    return [f'$objectprops_record_at({state}.OBJECTPROPS, n_first) = (pobjectprops_{state.lower()})',
            f'$property_slot_at(pobjectprops_{state.lower()}.SLOTS, $ptascii("value")) = (ppropertyslot_{state.lower()})',
            f'ppropertyslot_{state.lower()}.STATE = PROP_UNSET',
            f'$propref_at({state}.PROPREFS, {cell}) = (ppropref_{state.lower()})',
            f'ppropref_{state.lower()}.SOURCES = [CLASS_PROP_SOURCE ppropertyid_static]',
            f'$propref_sources_valid({state}, {cell}, ppropref_{state.lower()}.SOURCES)']


def entry(program, path):
    checks = initial(program, path) + seek('S_initial', 910, 'S_cache') + [
        'S_cache.TODO = (CONFIG_ITERATOR pconfigiterator_cache "key-start") :: ptask_cache*',
        'pconfigiterator_cache.OBJECT = n_iterator',
        'pconfigiterator_cache.CURRENT = REFERENCE n_old',
        'pconfigiterator_cache.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_name)]',
        '$string_bytes(pvalue_name) = ($ptascii("precision"))',
        '$lookup(S_cache.ENV, $ptascii("old")) = (n_old)',
        '$lookup(S_cache.ENV, $ptascii("held")) = (n_old)',
        '$lookup(S_cache.ENV, $ptascii("fresh")) = (n_fresh)',
        '$lookup(S_cache.ENV, $ptascii("name")) = (n_name)',
        '$lookup(S_cache.ENV, $ptascii("first")) = (n_first_cell)',
        'S_cache.STORE[n_first_cell] = DEFINED (POBJECT n_first)',
        '$objectprops_record_at(S_cache.OBJECTPROPS, n_first) = (pobjectprops_first)',
        '$property_slot_at(pobjectprops_first.SLOTS, $ptascii("value")) = (ppropertyslot_first)',
        'ppropertyslot_first.STATE = PROP_VALUE (ALIAS n_old)',
        'ppropertyslot_first.DECL = (ppropertyid_first)',
        '$propref_at(S_cache.PROPREFS, n_old) = (ppropref_cache)',
        'ppropref_cache.SOURCES = [OBJECT_PROP_SOURCE n_first ($ptascii("value")) ppropertyid_first,CLASS_PROP_SOURCE ppropertyid_static]',
        '$propref_unique_sources(ppropref_cache.SOURCES)',
        '$propref_sources_valid(S_cache, n_old, ppropref_cache.SOURCES)',
        '$ordinary_reference_value(S_cache, n_old) = eps',
        '$config_iterator_current_value(S_cache, pconfigiterator_cache, REFERENCE n_old) = (pvalue_old)',
        '$string_bytes(pvalue_old) = ($ptascii("13"))',
        '$config_iterator_valid(S_cache, pconfigiterator_cache, "key-start")',
        owners('S_cache', 'HCELL n_old', 5), owners('S_cache', 'HCELL n_fresh', 1),
        owners('S_cache', 'HOBJECT n_iterator', 2), owners('S_cache', 'HOBJECT n_first', 1),
        'S_bad_value = S_cache[.STORE = $set_cell(S_cache.STORE, n_old, DEFINED PNULL)]',
        '$config_iterator_current_value(S_bad_value, pconfigiterator_cache, REFERENCE n_old) = eps',
        'S_bad_source = S_cache[.PROPREFS = [ppropref_cache[.SOURCES = [OBJECT_PROP_SOURCE n_iterator ($ptascii("value")) ppropertyid_first]]]]',
        '$config_iterator_current_value(S_bad_source, pconfigiterator_cache, REFERENCE n_old) = eps',
        'S_duplicate = S_cache[.PROPREFS = [ppropref_cache[.SOURCES = ppropref_cache.SOURCES ++ [CLASS_PROP_SOURCE ppropertyid_static]]]]',
        '$config_iterator_current_value(S_duplicate, pconfigiterator_cache, REFERENCE n_old) = eps',
        '$config_iterator_current_receipt(S_bad_source, pconfigiterator_cache, REFERENCE n_old)',
    ] + static('S_cache', 'n_old') + public('S_cache')
    return checks + seek('S_cache', 911, 'S_key') + [
        'S_key.CURRENT = (pcallcontext_key)',
        'S_key.FRAMES = pframe_key :: pframe_key_tail*',
        'pframe_key.TODO = (CONFIG_ITERATOR pconfigiterator_key "key") :: ptask_key*',
        'pconfigiterator_key.OBJECT = n_iterator',
        'pconfigiterator_key.CURRENT = REFERENCE n_old',
        '$config_iterator_frame(S_key, pcallcontext_key, pframe_key)',
        'S_key_globals = $global_table_view(S_key)',
        '$lookup(S_key_globals.ENV, $ptascii("held")) = (n_fresh)',
        '$lookup(S_key_globals.ENV, $ptascii("old")) = (n_old)',
        owners('S_key', 'HCELL n_old', 3), owners('S_key', 'HCELL n_fresh', 2),
        '$config_iterator_current_value(S_key, pconfigiterator_key, REFERENCE n_old) = (pvalue_sent)',
        '$string_bytes(pvalue_sent) = ($ptascii("17"))',
    ] + string('S_key', 'n_fresh', '23') + detached('S_key', 'n_old') + static('S_key', 'n_old') + public('S_key')


def moved(state):
    return [f'$propref_at({state}.PROPREFS, n_old) = eps',
            f'$ordinary_reference_value({state}, n_old) = (PARRAY n_array)',
            f'$node_children({state}, HCELL n_old) = [HARRAY n_array]',
            owners(state, 'HCELL n_old', 1), owners(state, 'HARRAY n_array', 1),
            owners(state, 'HCELL n_fresh', 3),
            f'$propref_at({state}.PROPREFS, n_fresh) = (ppropref_moved)',
            'ppropref_moved.SOURCES = [CLASS_PROP_SOURCE ppropertyid_static]',
            f'$propref_sources_valid({state}, n_fresh, ppropref_moved.SOURCES)',
            owners(state, 'HOBJECT n_iterator', 1),
            *static(state, 'n_fresh'), *public(state)]


def conditions(name, program, path, stdout):
    checks = entry(program, path)
    if name == NORMAL:
        checks += seek('S_key', 912, 'S_send') + [
            'S_send.TODO = (CONFIG_ITERATOR pconfigiterator_send "send") :: ptask_send*',
            'pconfigiterator_send.CURRENT = REFERENCE n_old',
            'pconfigiterator_send.KEY = KNOWN (PINT 1)',
            '$config_iterator_current_value(S_send, pconfigiterator_send, REFERENCE n_old) = (pvalue_sent)',
        ] + budget('S_send', 'S_send_budget') + seek('S_send', 913, 'S_sent') + [
            'S_sent.TODO = (CONFIG_ITERATOR pconfigiterator_sent "next-start") :: ptask_sent*',
            'pconfigiterator_sent.CURRENT = KNOWN PNULL',
            'pconfigiterator_sent.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_name),ENTRY (KINT 1) (DIRECT pvalue_sent)]',
            owners('S_sent', 'HCELL n_old', 2),
        ] + public('S_sent') + seek('S_sent', 914, 'S_after') + [
            'S_after.TODO = (CONFIG_ITERATOR pconfigiterator_after "ready") :: ptask_after*',
            'pconfigiterator_after.ITEMS = pconfigiterator_sent.ITEMS',
            '$config_iterator_valid(S_after, pconfigiterator_after, "ready")',
        ] + moved('S_after')
    else:
        checks += seek('S_key', 915, 'S_caught') + [
            '$lookup(S_caught.ENV, $ptascii("saved")) = (n_saved_cell)',
            'S_caught.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)',
            '$lookup(S_caught.ENV, $ptascii("e")) = (n_error_cell)',
            'S_caught.STORE[n_error_cell] = DEFINED (POBJECT n_saved)',
            '$throwable_field(S_caught, n_saved, "previous") = PNULL',
            '$lookup(S_caught.ENV, $ptascii("result")) = (n_result)',
            'S_caught.STORE[n_result] = DEFINED (PINT 99)',
            owners('S_caught', 'HCELL n_old', 2), owners('S_caught', 'HCELL n_fresh', 2),
            owners('S_caught', 'HOBJECT n_iterator', 1),
        ] + detached('S_caught', 'n_old') + static('S_caught', 'n_old') + public('S_caught')
        checks += seek('S_caught', 916, 'S_after') + moved('S_after')
    return checks + finish('S_after', stdout, ['HCELL n_old', 'HCELL n_fresh',
        'HCELL n_name', 'HARRAY n_array', 'HOBJECT n_first', 'HOBJECT n_iterator'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_aggregate_unpack_state_review.py'),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
