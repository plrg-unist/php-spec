#!/usr/bin/env python3
"""Copied NULL/scalar sends outlive DATA through handler return or supplied throw."""
from pathlib import Path
from types import SimpleNamespace

import config_iterator_scalar_review_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial, seek
from array_generator_unpack_state_review import budget, finish, owners, public

RETURN = 'config-scalar-review-null-option-handler-return'
THROW = 'config-scalar-review-null-option-handler-throw'
SOURCES = SimpleNamespace(CASES={n: cases.CASES[n] for n in (RETURN, THROW)},
                          __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a68_peer_echo(pstate, ptbytes) : bool
def $a68_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a68_peer_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 960) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "key-start") :: ptask*
  -- if |pconfigiterator.ITEMS| = 1
def $list_warning_frontier(S, 961) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "send") :: ptask*
  -- if |pconfigiterator.ITEMS| = 1
def $list_warning_frontier(S, 962) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "ready") :: ptask*
def $list_warning_frontier(S, 963) = $a68_peer_echo(S, $ptascii("H:"))
def $list_warning_frontier(S, 964) = true
  -- if S.TODO = (CONFIG_INI_NULL_RESULT pconfigcall) :: ptask*
def $list_warning_frontier(S, 965) = $a68_peer_echo(S, $ptascii("E:"))
'''


def dead_data(state):
    return [f'~((HOBJECT n_iterator) <- {state}.ALLOCATIONS)',
            f'~((HOBJECT n_aggregate) <- {state}.ALLOCATIONS)',
            f'$weakref_get({state}, n_watch) = PNULL',
            f'{state}.ITERATORS = eps',
            f'{state}.PRECISIONINI = $ptascii("19")',
            f'{state}.STORE[n_result] = DEFINED (PINT 99)',
            f'{state}.STORE[n_value] = DEFINED (PINT 31)',
            f'{state}.STORE[n_name] = DEFINED pvalue_name_{state.lower()}',
            f'$string_bytes(pvalue_name_{state.lower()}) = ($ptascii("precision"))',
            owners(state, 'HCELL n_name', 1), owners(state, 'HCELL n_value', 1)]


def conditions(name, program, path, stdout):
    checks = initial(program, path) + seek('S_initial', 960, 'S_cache') + [
        'S_cache.TODO = (CONFIG_ITERATOR pconfigiterator_cache "key-start") :: ptask_cache*',
        'pconfigiterator_cache.OBJECT = n_iterator',
        'pconfigiterator_cache.PRODUCER = (n_aggregate)',
        'pconfigiterator_cache.CURRENT = REFERENCE n_value',
        'pconfigiterator_cache.ITEMS = [ENTRY (KINT 0) (DIRECT PNULL)]',
        '$lookup(S_cache.ENV, $ptascii("name")) = (n_name)',
        '$lookup(S_cache.ENV, $ptascii("value")) = (n_value)',
        '$lookup(S_cache.ENV, $ptascii("result")) = (n_result)',
        '$lookup(S_cache.ENV, $ptascii("saved")) = (n_saved_cell)',
        'S_cache.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)',
        '$lookup(S_cache.ENV, $ptascii("watch")) = (n_watch_cell)',
        'S_cache.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        'S_cache.STORE[n_value] = DEFINED (PINT 13)',
        'S_cache.STORE[n_name] = DEFINED pvalue_name',
        '$string_bytes(pvalue_name) = ($ptascii("precision"))',
        '$config_iterator_valid(S_cache, pconfigiterator_cache, "key-start")',
        owners('S_cache', 'HCELL n_value', 2),
        owners('S_cache', 'HOBJECT n_iterator', 1),
        '~((HOBJECT n_aggregate) <- S_cache.ALLOCATIONS)',
    ] + public('S_cache') + seek('S_cache', 961, 'S_send') + [
        'S_send.TODO = (CONFIG_ITERATOR pconfigiterator_send "send") :: ptask_send*',
        'pconfigiterator_send.CURRENT = REFERENCE n_value',
        'pconfigiterator_send.KEY = KNOWN (PINT 1)',
        'pconfigiterator_send.ITEMS = pconfigiterator_cache.ITEMS',
        '$config_iterator_current_value(S_send, pconfigiterator_send, REFERENCE n_value) = (PINT 17)',
        owners('S_send', 'HCELL n_value', 2),
    ] + public('S_send') + budget('S_send', 'S_send_budget') + seek('S_send', 962, 'S_ready') + [
        'S_ready.TODO = (CONFIG_ITERATOR pconfigiterator_ready "ready") :: ptask_ready*',
        'pconfigiterator_ready.ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT (PINT 17))]',
        'pconfigiterator_ready.CURRENT = KNOWN PNULL',
        'pconfigiterator_ready.KEY = KNOWN PNULL',
        '$config_iterator_valid(S_ready, pconfigiterator_ready, "ready")',
        '$config_iterator_retired_scope(S_ready, pconfigiterator_ready)',
        '$config_pack_prefix(pconfigiterator_ready.CALL, pconfigiterator_ready.ITEMS, false) = (pconfigcall_prefix)',
        'pconfigcall = pconfigcall_prefix[.INDEX = 1]',
        'pconfigcall.PACKS = eps',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PINT 17))]',
        'S_ready.ORIGIN = (pconfigcall.SITE)',
        '$config_call_valid(S_ready, pconfigcall)',
        '~$config_invoke_valid(S_ready, pconfigcall)',
        '$config_ini_null_valid(S_ready, pconfigcall)',
        '~$config_ini_null_valid(S_ready, pconfigcall[.LINE = $(pconfigcall.LINE + 1)])',
        '~$config_ini_null_valid(S_ready, pconfigcall[.OWNER = (n_watch)])',
        '~$config_ini_null_valid(S_ready, pconfigcall[.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (POBJECT n_watch))]])',
    ] + dead_data('S_ready') + public('S_ready') + seek('S_ready', 963, 'S_handler') + [
        'S_handler.CURRENT = (pcallcontext_handler)',
        '$error_context_call(S_handler, pcallcontext_handler) = (perrorcall)',
        'perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall',
        'perrorcall.SITE = pconfigcall.SITE',
        'perrorcall.LINE = pconfigcall.LINE',
        'perrorcall.LEVEL = 8192',
        'perrorcall.MESSAGE = $config_ini_null_message(pconfigcall)',
        'S_handler.FRAMES = pframe_handler :: pframe_handler_tail*',
        'pframe_handler.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_handler*',
        'S_receipt = $api_saved_frame_scope($constant_frame_scope(S_handler, pframe_handler, pframe_handler_tail*), pframe_handler, pframe_handler_tail*)',
        '$error_entered_call_valid(S_receipt, perrorcall)',
        '$config_ini_null_valid(S_receipt, pconfigcall)',
        '~$config_invoke_valid(S_receipt, pconfigcall)',
    ] + dead_data('S_handler') + public('S_handler')
    if name == RETURN:
        checks += seek('S_handler', 964, 'S_resume') + [
            'S_resume.TODO = (CONFIG_INI_NULL_RESULT pconfigcall) :: ptask_resume*',
            '$config_ini_null_valid(S_resume, pconfigcall)',
            '~$config_invoke_valid(S_resume, pconfigcall)',
            'PhpStep: S_resume ~> S_after',
            'S_after.RESULT = KNOWN (PBOOL false)',
            'S_after.PRECISIONINI = $ptascii("19")',
        ] + public('S_resume') + public('S_after')
    else:
        checks += seek('S_handler', 965, 'S_after') + [
            '$lookup(S_after.ENV, $ptascii("e")) = (n_caught_cell)',
            'S_after.STORE[n_caught_cell] = DEFINED (POBJECT n_saved)',
            '$throwable_field(S_after, n_saved, "previous") = PNULL',
        ] + dead_data('S_after') + public('S_after')
    return checks + finish('S_after', stdout, ['HOBJECT n_iterator', 'HOBJECT n_aggregate',
        'HOBJECT n_watch', 'HOBJECT n_saved', 'HCELL n_name', 'HCELL n_value'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_aggregate_unpack_state_review.py'),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
