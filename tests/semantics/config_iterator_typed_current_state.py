#!/usr/bin/env python3
"""Typed DATA fields, nullable current, source detach, and copied API arguments."""
from pathlib import Path
from types import SimpleNamespace

import config_iterator_typed_current_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek

NAME = 'config-typed-current-owned-aggregate'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a67_echo(pstate, ptbytes) : bool
def $a67_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a67_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 930) = true
  -- if S.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask*
def $list_warning_frontier(S, 931) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "key-start") :: ptask*
  -- if pconfigiterator.ITEMS = eps
def $list_warning_frontier(S, 932) = $a67_echo(S, $ptascii("R:"))
def $list_warning_frontier(S, 933) = $a67_echo(S, $ptascii("M:"))
def $list_warning_frontier(S, 934) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "ready") :: ptask*
def $list_warning_frontier(S, 935) = $a67_echo(S, $ptascii("F:"))
'''


def string(state, cell, value):
    return [f'{state}.STORE[{cell}] = DEFINED pvalue_{state.lower()}_{cell}',
            f'$string_bytes(pvalue_{state.lower()}_{cell}) = ($ptascii("{value}"))']


def field(state, name, cell):
    label = state.lower() + '_' + name
    return [f'$objectprops_record_at({state}.OBJECTPROPS, n_object) = (pobjectprops_{label})',
            f'$property_slot_at(pobjectprops_{label}.SLOTS, $ptascii("{name}")) = (ppropertyslot_{label})',
            f'ppropertyslot_{label}.STATE = PROP_VALUE (ALIAS {cell})',
            f'ppropertyslot_{label}.DECL = (ppropertyid_{name})',
            f'$propref_at({state}.PROPREFS, {cell}) = (ppropref_{label})',
            f'ppropref_{label}.SOURCES = [OBJECT_PROP_SOURCE n_object ($ptascii("{name}")) ppropertyid_{name}]',
            f'$propref_sources_valid({state}, {cell}, ppropref_{label}.SOURCES)']


def array(state, cell, name, value):
    return [f'{state}.STORE[{cell}] = DEFINED (PARRAY n_{name})',
            f'{state}.ARRAYS[n_{name}].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_{name}_{state.lower()})]',
            f'$string_bytes(pvalue_{name}_{state.lower()}) = ($ptascii("{value}"))']


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 930, 'S_return') + [
        'S_return.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_return*',
        'S_return.RESULT = KNOWN (POBJECT n_object)',
        'pconfigaggregate.OBJECT = n_aggregate',
        '$lookup(S_return.ENV, $ptascii("name")) = (n_name)',
        '$lookup(S_return.ENV, $ptascii("held")) = (n_held)',
        '$lookup(S_return.ENV, $ptascii("fresh")) = (n_fresh)',
        '$lookup(S_return.ENV, $ptascii("watch")) = (n_watch_cell)',
        'S_return.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        'S_return.STORE[n_name] = DEFINED PNULL',
        '$ordinary_reference_value(S_return, n_name) = eps',
        '$ordinary_reference_value(S_return, n_held) = eps',
        '$config_iterator_reference_value(S_return, n_name) = (PNULL)',
        '$config_iterator_reference_value(S_return, n_held) = (pvalue_initial)',
        '$string_bytes(pvalue_initial) = ($ptascii("13"))',
        '$proprefs_valid(S_return)',
        '$config_iterator_owned_fields(S_return, n_object)',
        '$config_iterator_finalizer(S_return, n_object)',
        '$config_aggregate_return_allowed(S_return, pconfigaggregate)',
        '$node_children(S_return, HOBJECT n_object) = [HCELL n_name, HCELL n_held]',
        '$node_children(S_return, HCELL n_name) = eps',
        '$config_iterator_data_node(S_return, HCELL n_name, [HOBJECT n_object])',
        '~$config_iterator_data_node(S_return, HCELL n_name, [HCELL n_name, HOBJECT n_object])',
        owners('S_return', 'HOBJECT n_object', 1),
        owners('S_return', 'HCELL n_name', 2), owners('S_return', 'HCELL n_held', 2),
    ] + field('S_return', 'name', 'n_name') + field('S_return', 'value', 'n_held') + public('S_return')
    checks += seek('S_return', 931, 'S_cache') + [
        'S_cache.TODO = (CONFIG_ITERATOR pconfigiterator_cache "key-start") :: ptask_cache*',
        'pconfigiterator_cache.OBJECT = n_object',
        'pconfigiterator_cache.CURRENT = REFERENCE n_name',
        'S_cache.STORE[n_name] = DEFINED PNULL',
        '$config_iterator_current_value(S_cache, pconfigiterator_cache, REFERENCE n_name) = (PNULL)',
        '~$config_iterator_current_string(S_cache, pconfigiterator_cache)',
        '$config_iterator_valid(S_cache, pconfigiterator_cache, "key-start")',
        owners('S_cache', 'HCELL n_name', 3),
        'S_bad_value = S_cache[.STORE = $set_cell(S_cache.STORE, n_name, DEFINED (PINT 0))]',
        '$config_iterator_reference_value(S_bad_value, n_name) = eps',
        'S_empty_sources = S_cache[.PROPREFS = [ppropref_s_return_name[.SOURCES = eps]]]',
        '$config_iterator_reference_value(S_empty_sources, n_name) = eps',
        '$config_iterator_current_receipt(S_empty_sources, pconfigiterator_cache, REFERENCE n_name)',
    ] + public('S_cache') + budget('S_cache', 'S_cache_budget') + seek('S_cache', 932, 'S_key') + [
        'S_key.CURRENT = (pcallcontext_key)',
        'S_key.FRAMES = pframe_key :: pframe_tail*',
        'pframe_key.TODO = (CONFIG_ITERATOR pconfigiterator_key "key") :: ptask_key*',
        'pconfigiterator_key.CURRENT = REFERENCE n_held',
        'pconfigiterator_key.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_name)]',
        '$string_bytes(pvalue_name) = ($ptascii("precision"))',
        '$config_iterator_frame(S_key, pcallcontext_key, pframe_key)',
        '$propref_at(S_key.PROPREFS, n_held) = eps',
        '$ordinary_reference_value(S_key, n_held) = (pvalue_sent)',
        '$string_bytes(pvalue_sent) = ($ptascii("17"))',
        '$config_iterator_current_value(S_key, pconfigiterator_key, REFERENCE n_held) = (pvalue_sent)',
        '$node_children(S_key, HOBJECT n_object) = [HCELL n_name, HCELL n_fresh]',
        owners('S_key', 'HCELL n_held', 2), owners('S_key', 'HCELL n_fresh', 2),
    ] + field('S_key', 'value', 'n_fresh') + string('S_key', 'n_fresh', '23') + string('S_key', 'n_name', 'serialize_precision') + public('S_key')
    checks += seek('S_key', 933, 'S_dtor') + [
        'S_dtor.CURRENT = (pcallcontext_dtor)',
        '$destructor_context_call(pcallcontext_dtor, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object', 'pdestructorcall.PENDING = eps',
        '$destructor_call_live(S_dtor, pdestructorcall)',
        '$objectprops_record_at(S_dtor.OBJECTPROPS, n_object) = (pobjectprops_dtor)',
        '$property_slot_at(pobjectprops_dtor.SLOTS, $ptascii("name")) = (ppropertyslot_dtor_name)',
        'ppropertyslot_dtor_name.STATE = PROP_UNSET',
        '$propref_at(S_dtor.PROPREFS, n_name) = eps',
        '$propref_at(S_dtor.PROPREFS, n_held) = eps',
        '$weakref_get(S_dtor, n_watch) = POBJECT n_object',
        'S_dtor.PRECISIONINI = $ptascii("14")',
    ] + array('S_dtor', 'n_name', 'name_array', 'free') + array('S_dtor', 'n_held', 'old_array', 'old') + field('S_dtor', 'value', 'n_fresh') + string('S_dtor', 'n_fresh', '29') + public('S_dtor')
    checks += seek('S_dtor', 934, 'S_ready') + [
        'S_ready.TODO = (CONFIG_ITERATOR pconfigiterator_ready "ready") :: ptask_ready*',
        'pconfigiterator_ready.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_name), ENTRY (KINT 1) (DIRECT pvalue_sent)]',
        '$config_iterator_valid(S_ready, pconfigiterator_ready, "ready")',
        '$config_iterator_retired_scope(S_ready, pconfigiterator_ready)',
        '~((HOBJECT n_object) <- S_ready.ALLOCATIONS)',
        '~((HOBJECT n_aggregate) <- S_ready.ALLOCATIONS)',
        '$propref_at(S_ready.PROPREFS, n_fresh) = eps',
        '$weakref_get(S_ready, n_watch) = PNULL',
        'S_ready.PRECISIONINI = $ptascii("14")',
        'PhpStep: S_ready ~> S_api',
        'S_api.PRECISIONINI = $ptascii("17")',
        'S_api.RESULT = KNOWN pvalue_previous', '$string_bytes(pvalue_previous) = ($ptascii("14"))',
    ] + public('S_ready') + public('S_api') + seek('S_api', 935, 'S_outside') + [
        '$propref_at(S_outside.PROPREFS, n_fresh) = eps',
    ] + array('S_outside', 'n_fresh', 'fresh_array', 'detached') + public('S_outside')
    checks += finish('S_outside', stdout, ['HOBJECT n_object', 'HOBJECT n_aggregate',
        'HOBJECT n_watch', 'HCELL n_name', 'HCELL n_held', 'HCELL n_fresh'])
    checks += ['S_done.POOLS = S_return.POOLS']
    for name, state in [('name_array', 'S_dtor'), ('old_array', 'S_dtor'),
                        ('fresh_array', 'S_outside')]:
        checks += [
            f'(HARRAY n_{name}) <- S_done.ALLOCATIONS',
            f'n_{name}_roots = $heap_count(HARRAY n_{name}, $pools_nodes(S_done.POOLS))',
            f'$(n_{name}_roots > 0)',
            owners('S_done', f'HARRAY n_{name}', f'n_{name}_roots'),
            f'S_done.ARRAYS[n_{name}] = {state}.ARRAYS[n_{name}]',
        ]
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
