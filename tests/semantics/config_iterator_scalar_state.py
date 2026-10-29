#!/usr/bin/env python3
"""Typed raw float snapshots convert only after sole DATA retirement."""
from pathlib import Path
from types import SimpleNamespace

import config_iterator_scalar_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek

NAME = 'config-scalar-current-float-api-after-data-destructor'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a68_echo(pstate, ptbytes) : bool
def $a68_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a68_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 930) = true
  -- if S.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask*
def $list_warning_frontier(S, 931) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "key-start") :: ptask*
  -- if |pconfigiterator.ITEMS| = 1
def $list_warning_frontier(S, 932) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "send") :: ptask*
  -- if |pconfigiterator.ITEMS| = 1
def $list_warning_frontier(S, 933) = $a68_echo(S, $ptascii("M:"))
def $list_warning_frontier(S, 934) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "ready") :: ptask*
def $list_warning_frontier(S, 935) = $a68_echo(S, $ptascii("F:"))
'''


def source(state, cell):
    label = state.lower()
    return [f'$objectprops_record_at({state}.OBJECTPROPS, n_object) = (pobjectprops_{label})',
            f'$property_slot_at(pobjectprops_{label}.SLOTS, $ptascii("value")) = (ppropertyslot_{label})',
            f'ppropertyslot_{label}.STATE = PROP_VALUE (ALIAS {cell})',
            f'ppropertyslot_{label}.DECL = (ppropertyid_value)',
            f'$propref_at({state}.PROPREFS, {cell}) = (ppropref_{label})',
            f'ppropref_{label}.SOURCES = [OBJECT_PROP_SOURCE n_object ($ptascii("value")) ppropertyid_value]',
            f'$propref_sources_valid({state}, {cell}, ppropref_{label}.SOURCES)']


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
        'S_return.STORE[n_held] = DEFINED (PFLOAT 4609434218613702656)',
        '$ordinary_reference_value(S_return, n_held) = eps',
        '$config_iterator_reference_value(S_return, n_held) = (PFLOAT 4609434218613702656)',
        '$config_aggregate_return_allowed(S_return, pconfigaggregate)',
        '$node_children(S_return, HOBJECT n_object) = [HCELL n_held]',
        owners('S_return', 'HOBJECT n_object', 1), owners('S_return', 'HCELL n_held', 2),
        owners('S_return', 'HCELL n_fresh', 1),
    ] + source('S_return', 'n_held') + public('S_return')
    checks += seek('S_return', 931, 'S_cache') + [
        'S_cache.TODO = (CONFIG_ITERATOR pconfigiterator_cache "key-start") :: ptask_cache*',
        'pconfigiterator_cache.OBJECT = n_object',
        'pconfigiterator_cache.CURRENT = REFERENCE n_held',
        'pconfigiterator_cache.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_name)]',
        '$string_bytes(pvalue_name) = ($ptascii("precision"))',
        '$config_iterator_current_value(S_cache, pconfigiterator_cache, REFERENCE n_held) = (PFLOAT 4609434218613702656)',
        '$config_iterator_valid(S_cache, pconfigiterator_cache, "key-start")',
        owners('S_cache', 'HCELL n_held', 3), owners('S_cache', 'HCELL n_fresh', 1),
        '~((HOBJECT n_aggregate) <- S_cache.ALLOCATIONS)',
    ] + source('S_cache', 'n_held') + public('S_cache')
    checks += seek('S_cache', 932, 'S_send') + [
        'S_send.TODO = (CONFIG_ITERATOR pconfigiterator_send "send") :: ptask_send*',
        'pconfigiterator_send.CURRENT = REFERENCE n_held',
        'pconfigiterator_send.KEY = KNOWN (PINT 1)',
        'pconfigiterator_send.ITEMS = pconfigiterator_cache.ITEMS',
        '$propref_at(S_send.PROPREFS, n_held) = eps',
        'S_send.STORE[n_held] = DEFINED (PFLOAT 4608238818662570491)',
        '$config_iterator_current_value(S_send, pconfigiterator_send, REFERENCE n_held) = (PFLOAT 4608238818662570491)',
        '$config_iterator_current_scalar(S_send, pconfigiterator_send)',
        '~$config_iterator_current_string(S_send, pconfigiterator_send)',
        '$node_children(S_send, HOBJECT n_object) = [HCELL n_fresh]',
        owners('S_send', 'HCELL n_held', 2), owners('S_send', 'HCELL n_fresh', 2),
        '$config_iterator_scalar(S_send, PNULL)',
        '$config_iterator_scalar(S_send, PBOOL false)',
        '$config_iterator_scalar(S_send, PBOOL true)',
        '$config_iterator_scalar(S_send, PINT 17)',
        '$config_iterator_scalar(S_send, PFLOAT 4608238818662570491)',
        '~$config_iterator_scalar(S_send, PINT 9223372036854775808)',
        '~$config_iterator_scalar(S_send, PFLOAT 18446744073709551616)',
        '~$config_iterator_scalar(S_send, POBJECT n_object)',
        'S_object = S_send[.STORE[n_held] = DEFINED (POBJECT n_object)]',
        '$config_iterator_current_value(S_object, pconfigiterator_send, REFERENCE n_held) = (POBJECT n_object)',
        '$config_iterator_valid(S_object, pconfigiterator_send, "send")',
        '~$config_iterator_current_scalar(S_object, pconfigiterator_send)',
        'PhpStep: S_object ~> S_refused',
        'S_refused.COMPLETION = UNSUPPORTED "CONFIG Iterator unpack current outside ordinary scalar send domain"',
        'pconfigiterator_unknown = pconfigiterator_send[.KEY = KNOWN (PSTRING ($ptascii("unknown68")))]',
        'S_unknown = S_object[.TODO = (CONFIG_ITERATOR pconfigiterator_unknown "send") :: ptask_send*]',
        '$config_iterator_valid(S_unknown, pconfigiterator_unknown, "send")',
        '$intrinsic_argument(S_unknown, pconfigiterator_send.CALL.SITE, 0) = ((expression, true, eps, porigin_argument, z_argument))',
        'PhpStep: S_unknown ~> S_error',
        'S_error.COMPLETION = THROWN "Error" ($ptascii("Unknown named parameter $unknown68")) z_argument',
    ] + source('S_send', 'n_fresh') + public('S_send') + budget('S_send', 'S_send_budget') + [
        'PhpStep: S_send ~> S_sent',
        'S_sent.TODO = (CONFIG_ITERATOR pconfigiterator_sent "next-start") :: ptask_send*',
        'pconfigiterator_sent = pconfigiterator_send[.ITEMS = pconfigiterator_send.ITEMS ++ [ENTRY (KINT 1) (DIRECT (PFLOAT 4608238818662570491))]][.CURRENT = KNOWN PNULL][.KEY = KNOWN PNULL]',
        owners('S_sent', 'HCELL n_held', 1),
    ] + public('S_sent')
    checks += seek('S_sent', 933, 'S_dtor') + [
        'S_dtor.CURRENT = (pcallcontext_dtor)',
        '$destructor_context_call(pcallcontext_dtor, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object',
        'pdestructorcall.PENDING = eps',
        '$destructor_call_live(S_dtor, pdestructorcall)',
        'S_dtor.PRECISIONINI = $ptascii("3")',
        'S_dtor.STORE[n_held] = DEFINED (PFLOAT 4616752568008179712)',
        'S_dtor.STORE[n_fresh] = DEFINED (PFLOAT 4619004367821864960)',
        '$propref_at(S_dtor.PROPREFS, n_held) = eps',
        owners('S_dtor', 'HCELL n_held', 1), owners('S_dtor', 'HCELL n_fresh', 2),
        '$weakref_get(S_dtor, n_watch) = POBJECT n_object',
    ] + source('S_dtor', 'n_fresh') + public('S_dtor')
    checks += seek('S_dtor', 934, 'S_ready') + [
        'S_ready.TODO = (CONFIG_ITERATOR pconfigiterator_ready "ready") :: ptask_ready*',
        'pconfigiterator_ready.ITEMS = pconfigiterator_sent.ITEMS',
        '$config_iterator_valid(S_ready, pconfigiterator_ready, "ready")',
        '$config_iterator_retired_scope(S_ready, pconfigiterator_ready)',
        '$weakref_get(S_ready, n_watch) = PNULL',
        '~((HOBJECT n_object) <- S_ready.ALLOCATIONS)',
        '~((HOBJECT n_aggregate) <- S_ready.ALLOCATIONS)',
        '$propref_at(S_ready.PROPREFS, n_fresh) = eps',
        'S_ready.PRECISIONINI = $ptascii("3")',
        'S_ready.STORE[n_held] = S_dtor.STORE[n_held]',
        'S_ready.STORE[n_fresh] = S_dtor.STORE[n_fresh]',
        owners('S_ready', 'HCELL n_held', 1), owners('S_ready', 'HCELL n_fresh', 1),
        'PhpStep: S_ready ~> S_api',
        'S_api.PRECISIONINI = $ptascii("1.23")',
        'S_api.RESULT = KNOWN pvalue_previous',
        '$string_bytes(pvalue_previous) = ($ptascii("3"))',
    ] + public('S_ready') + public('S_api')
    checks += seek('S_api', 935, 'S_outside') + [
        '$propref_at(S_outside.PROPREFS, n_fresh) = eps',
        'S_outside.STORE[n_fresh] = DEFINED (PBOOL false)',
    ] + public('S_outside')
    return checks + finish('S_outside', stdout, ['HOBJECT n_object', 'HOBJECT n_aggregate',
        'HOBJECT n_watch', 'HCELL n_name', 'HCELL n_held', 'HCELL n_fresh'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
