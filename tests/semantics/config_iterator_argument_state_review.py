#!/usr/bin/env python3
"""Owning prefixes survive cache/DATA cleanup on key and send failures."""
from pathlib import Path
from types import SimpleNamespace

import config_iterator_argument_review_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek

KEY = 'config-argument-review-prefix-cow-key-throw'
NAMED = 'config-argument-review-prefix-cow-unknown-name'
SOURCES = SimpleNamespace(CASES={name: cases.CASES[name] for name in (KEY, NAMED)},
                          __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a69_peer_echo(pstate, ptbytes) : bool
def $a69_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a69_peer_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 940) = $a69_peer_echo(S, $ptascii("Q0:"))
def $list_warning_frontier(S, 941) = $a69_peer_echo(S, $ptascii("Q1:"))
def $list_warning_frontier(S, 942) = $a69_peer_echo(S, $ptascii("C:"))
def $list_warning_frontier(S, 943) = $a69_peer_echo(S, $ptascii("D:"))
def $list_warning_frontier(S, 944) = $a69_peer_echo(S, $ptascii("P:"))
def $list_warning_frontier(S, 945) = $a69_peer_echo(S, $ptascii("E:"))
def $list_warning_frontier(S, 946) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_ITERATOR pconfigiterator "ready") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 947) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "send") :: ptask*
  -- if |pconfigiterator.ITEMS| = 1
def $list_warning_frontier(S, 948) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "send") :: ptask*
  -- if pconfigiterator.ITEMS = eps
'''


def global_cell(state, name, cell):
    return f'$lookup($global_table_view({state}).ENV, $ptascii("{name}")) = ({cell})'


def destructor(state, label, target):
    return [f'{state}.CURRENT = (pcallcontext_{label})',
            f'$destructor_context_call(pcallcontext_{label}, {state}.CURRENT, {state}.FRAMES) = (pdestructorcall_{label})',
            f'pdestructorcall_{label}.OBJECT = {target}',
            f'pdestructorcall_{label}.PENDING = (n_pending)',
            f'$destructor_call_live({state}, pdestructorcall_{label})']


def conditions(name, program, path, stdout):
    named = name == NAMED
    stage = 'send' if named else 'key'
    checks = initial(program, path)
    if named:
        checks += seek('S_initial', 948, 'S_first') + [
            'S_first.TODO = (CONFIG_ITERATOR pconfigiterator_first "send") :: ptask_first*',
            'pconfigiterator_first.ITEMS = eps',
            'pconfigiterator_first.CURRENT = REFERENCE n_prefix_cache',
            '$config_iterator_current_value(S_first, pconfigiterator_first, REFERENCE n_prefix_cache) = (PARRAY n_argument)',
            '$config_iterator_argument_nodes(pconfigiterator_first) = eps',
            '$config_iterator_owning_release(S_first, pconfigiterator_first)',
            '$intrinsic_argument(S_first, pconfigiterator_first.CALL.SITE, 0) = ((expression_first, true, eps, porigin_first, z_first))',
            'pconfigiterator_first_error = pconfigiterator_first[.KEY = KNOWN (PSTRING ($ptascii("unknown69")))]',
            'S_first_error_input = S_first[.TODO = (CONFIG_ITERATOR pconfigiterator_first_error "send") :: ptask_first*]',
            '$config_iterator_valid(S_first_error_input, pconfigiterator_first_error, "send")',
            'PhpStep: S_first_error_input ~> S_first_error',
            'S_first_error.COMPLETION = THROWN "Error" ($ptascii("Unknown named parameter $unknown69")) z_first',
            '$throwable_same_frame_continuation(S_first_error_input, S_first_error, ptask_first*) = S_first_error',
            'S_forged_error = S_first_error[.COMPLETION = THROWN "Error" ($ptascii("forged")) z_first]',
            '$throwable_same_frame_continuation(S_first_error_input, S_forged_error, ptask_first*) = S_forged_error[.TODO = ptask_first*]',
            'pconfigiterator_first_known = pconfigiterator_first_error[.CURRENT = KNOWN (PARRAY n_argument)]',
            'S_first_known = S_first[.TODO = (CONFIG_ITERATOR pconfigiterator_first_known "send") :: ptask_first*]',
            '$config_iterator_valid(S_first_known, pconfigiterator_first_known, "send")',
            '$config_iterator_owning_release(S_first_known, pconfigiterator_first_known)',
            'PhpStep: S_first_known ~> S_first_known_error',
            '$throwable_same_frame_continuation(S_first_known, S_first_known_error, ptask_first*) = S_first_known_error',
            'S_first_dead = S_first_known[.ALLOCATIONS = eps]',
            '~$config_iterator_owning_release(S_first_dead, pconfigiterator_first_known)',
            'pconfigiterator_first_scalar = pconfigiterator_first_error[.CURRENT = KNOWN (PINT 17)]',
            'S_first_scalar = S_first[.TODO = (CONFIG_ITERATOR pconfigiterator_first_scalar "send") :: ptask_first*]',
            '$config_iterator_valid(S_first_scalar, pconfigiterator_first_scalar, "send")',
            '~$config_iterator_owning_release(S_first_scalar, pconfigiterator_first_scalar)',
            'PhpStep: S_first_scalar ~> S_first_scalar_error',
            '$throwable_same_frame_continuation(S_first_scalar, S_first_scalar_error, ptask_first*) = S_first_scalar_error[.TODO = ptask_first*]',
            'S_first_cycle = S_first_error_input[.ARRAYS[n_argument].ITEMS = [ENTRY (KINT 0) (ALIAS n_prefix_cache)]]',
            '$config_iterator_valid(S_first_cycle, pconfigiterator_first_error, "send")',
            '$config_iterator_current_value(S_first_cycle, pconfigiterator_first_error, REFERENCE n_prefix_cache) = eps',
            '$config_iterator_owning_release(S_first_cycle, pconfigiterator_first_error)',
            'PhpStep: S_first_cycle ~> S_first_cycle_error',
            '$throwable_same_frame_continuation(S_first_cycle, S_first_cycle_error, ptask_first*) = S_first_cycle_error',
            'pconfigiterator_first_key = pconfigiterator_first[.KEY = KNOWN PNULL]',
            'S_first_key = S_first[.TODO = (CONFIG_ITERATOR pconfigiterator_first_key "key") :: ptask_first*][.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
            '$config_iterator_valid(S_first_key, pconfigiterator_first_key, "key")',
            '$config_iterator_owning_release(S_first_key, pconfigiterator_first_key)',
            'PhpStep: S_first_key ~> S_first_key_error',
            'S_first_key_error.COMPLETION = THROWN "Error" ($ptascii("Keys must be of type int|string during argument unpacking")) z_first',
            '$throwable_same_frame_continuation(S_first_key, S_first_key_error, ptask_first*) = S_first_key_error',
            'S_forged_key_error = S_first_key_error[.COMPLETION = THROWN "Error" ($ptascii("Keys must be of type int|string during argument unpacking")) $(z_first + 1)]',
            '$throwable_same_frame_continuation(S_first_key, S_forged_key_error, ptask_first*) = S_forged_key_error[.TODO = ptask_first*]',
        ]
        first = 'S_first'
    else:
        first = 'S_initial'
    checks += seek(first, 940, 'S_prefix') + [
        'S_prefix.CURRENT = (pcallcontext_next)',
        'S_prefix.FRAMES = pframe_next :: pframe_next_tail*',
        'pframe_next.TODO = (CONFIG_ITERATOR pconfigiterator_next "next") :: ptask_next*',
        '$config_iterator_frame(S_prefix, pcallcontext_next, pframe_next)',
        'pconfigiterator_next.OBJECT = n_object',
        'pconfigiterator_next.PRODUCER = (n_aggregate)',
        'pconfigiterator_next.ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_argument))]',
        '$config_iterator_argument_nodes(pconfigiterator_next) = [HARRAY n_argument]',
        '$config_iterator_call_nodes(pconfigiterator_next) = [HARRAY n_argument]',
        global_cell('S_prefix', 'prefix', 'n_prefix_cell'),
        'S_prefix.STORE[n_prefix_cell] = DEFINED (PARRAY n_clone)',
        'n_clone =/= n_argument',
        'S_prefix.ARRAYS[n_clone].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
        'S_prefix.ARRAYS[n_argument].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_prefix_payload))]',
        global_cell('S_prefix', 'iteratorWatch', 'n_iterator_watch_cell'),
        'S_prefix.STORE[n_iterator_watch_cell] = DEFINED (POBJECT n_iterator_watch)',
        global_cell('S_prefix', 'prefixWatch', 'n_prefix_watch_cell'),
        'S_prefix.STORE[n_prefix_watch_cell] = DEFINED (POBJECT n_prefix_watch)',
        global_cell('S_prefix', 'cacheWatch', 'n_cache_watch_cell'),
        'S_prefix.STORE[n_cache_watch_cell] = DEFINED (POBJECT n_cache_watch)',
        global_cell('S_prefix', 'saved', 'n_saved_cell'),
        'S_prefix.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)',
        global_cell('S_prefix', 'result', 'n_result_cell'),
        '~((HOBJECT n_aggregate) <- S_prefix.ALLOCATIONS)',
        owners('S_prefix', 'HARRAY n_argument', 1),
        owners('S_prefix', 'HARRAY n_clone', 1),
        owners('S_prefix', 'HOBJECT n_prefix_payload', 1),
        owners('S_prefix', 'HOBJECT n_object', 1),
    ] + public('S_prefix') + seek('S_prefix', 941, 'S_key') + [
        'S_key.CURRENT = (pcallcontext_key)',
        'S_key.FRAMES = pframe_key :: pframe_key_tail*',
        'pframe_key.TODO = (CONFIG_ITERATOR pconfigiterator_key "key") :: ptask_key*',
        '$config_iterator_frame(S_key, pcallcontext_key, pframe_key)',
        'pconfigiterator_key.OBJECT = n_object',
        'pconfigiterator_key.ITEMS = pconfigiterator_next.ITEMS',
        'pconfigiterator_key.CURRENT = REFERENCE n_cache',
        '$ordinary_reference_value(S_key, n_cache) = (POBJECT n_cache_payload)',
        '$config_iterator_current_argument(S_key, pconfigiterator_key)',
        '$lookup($global_table_view(S_key).ENV, $ptascii("prefix")) = eps',
        '$lookup($global_table_view(S_key).ENV, $ptascii("cache")) = eps',
        '~((HARRAY n_clone) <- S_key.ALLOCATIONS)',
        '$weakref_get(S_key, n_prefix_watch) = POBJECT n_prefix_payload',
        '$weakref_get(S_key, n_cache_watch) = POBJECT n_cache_payload',
        '$weakref_get(S_key, n_iterator_watch) = POBJECT n_object',
        owners('S_key', 'HCELL n_cache', 1),
        owners('S_key', 'HOBJECT n_cache_payload', 1),
        owners('S_key', 'HARRAY n_argument', 1),
        owners('S_key', 'HOBJECT n_prefix_payload', 1),
        owners('S_key', 'HOBJECT n_object', 1),
    ] + public('S_key') + budget('S_key', 'S_key_budget')
    if named:
        checks += seek('S_key', 947, 'S_send') + [
            'S_send.TODO = (CONFIG_ITERATOR pconfigiterator_send "send") :: ptask_send*',
            'pconfigiterator_send = pconfigiterator_key[.KEY = KNOWN pvalue_unknown]',
            '$string_bytes(pvalue_unknown) = ($ptascii("unknown69"))',
            '$config_iterator_valid(S_send, pconfigiterator_send, "send")',
            '$intrinsic_argument(S_send, pconfigiterator_send.CALL.SITE, 0) = ((expression, true, eps, porigin_argument, z_argument))',
            'PhpStep: S_send ~> S_error',
            'S_error.COMPLETION = THROWN "Error" ($ptascii("Unknown named parameter $unknown69")) z_argument',
        ]
        start = 'S_send'
    else:
        checks += ['n_pending = n_saved']
        start = 'S_key'
    checks += seek(start, 942, 'S_cache_dtor') + destructor('S_cache_dtor', 'cache', 'n_cache_payload')
    if named:
        checks += ['n_pending =/= n_saved',
            '$throwable_field(S_cache_dtor, n_pending, "message") = pvalue_message',
            '$string_bytes(pvalue_message) = ($ptascii("Unknown named parameter $unknown69"))',
            '$throwable_field(S_cache_dtor, n_pending, "previous") = PNULL']
    checks += [
        'S_cache_dtor.DESTRUCTION.OPERATIONS = pdestructionoperation_cache :: pdestructionoperation_cache_tail*',
        f'pdestructionoperation_cache.SOURCE = CONFIG_ITERATOR pconfigiterator_history "{stage}"',
        f'pconfigiterator_history = {"pconfigiterator_send" if named else "pconfigiterator_key"}',
        'pdestructionoperation_cache.PENDING = (n_pending)',
        '$eager_operation_source_valid(S_cache_dtor, pdestructionoperation_cache)',
        '~((HCELL n_cache) <- S_cache_dtor.ALLOCATIONS)',
        '(n_cache) <- S_cache_dtor.REFCELLS',
        '$ordinary_reference_value(S_cache_dtor, n_cache) = eps',
        '$config_iterator_current_receipt(S_cache_dtor, pconfigiterator_history, REFERENCE n_cache)',
        f'$config_iterator_stage(S_cache_dtor, pconfigiterator_history, "{stage}")',
        '$weakref_get(S_cache_dtor, n_iterator_watch) = POBJECT n_object',
        '$weakref_get(S_cache_dtor, n_prefix_watch) = POBJECT n_prefix_payload',
        owners('S_cache_dtor', 'HARRAY n_argument', 1),
        owners('S_cache_dtor', 'HOBJECT n_prefix_payload', 1),
        owners('S_cache_dtor', 'HOBJECT n_object', 1),
    ] + public('S_cache_dtor') + seek('S_cache_dtor', 943, 'S_data_dtor') + destructor('S_data_dtor', 'data', 'n_object') + [
        '$weakref_get(S_data_dtor, n_cache_watch) = PNULL',
        '~((HOBJECT n_cache_payload) <- S_data_dtor.ALLOCATIONS)',
        '~((HCELL n_cache) <- S_data_dtor.ALLOCATIONS)',
        '$weakref_get(S_data_dtor, n_prefix_watch) = POBJECT n_prefix_payload',
        owners('S_data_dtor', 'HARRAY n_argument', 1),
        owners('S_data_dtor', 'HOBJECT n_prefix_payload', 1),
    ] + public('S_data_dtor') + seek('S_data_dtor', 946, 'S_buffer') + [
        'S_buffer.TODO = (THROW_SEARCH n_pending) :: (CONFIG_ITERATOR pconfigiterator_buffer "ready") :: ptask_buffer*',
        'pconfigiterator_buffer = pconfigiterator_history[.CURRENT = KNOWN PNULL][.KEY = KNOWN PNULL]',
        '$config_iterator_valid(S_buffer, pconfigiterator_buffer, "ready")',
        '$config_iterator_retired_scope(S_buffer, pconfigiterator_buffer)',
        '~((HOBJECT n_object) <- S_buffer.ALLOCATIONS)',
        '$weakref_get(S_buffer, n_iterator_watch) = PNULL',
        '$config_pack_prefix(pconfigiterator_buffer.CALL, pconfigiterator_buffer.ITEMS, false) = (pconfigcall_prefix)',
        'pconfigcall = pconfigcall_prefix[.INDEX = 1]',
        '$config_iterator_copied_call(S_buffer, pconfigcall)',
        owners('S_buffer', 'HARRAY n_argument', 1),
        'pdestructionoperation_next = pdestructionoperation_cache[.SOURCE = CONFIG_ITERATOR pconfigiterator_buffer "next"]',
        '$eager_operation_source_valid(S_buffer, pdestructionoperation_next)',
        'pconfigiterator_empty = pconfigiterator_buffer[.ITEMS = eps]',
        '$config_iterator_retired_scope(S_buffer, pconfigiterator_empty)',
        '~$eager_operation_source_valid(S_buffer, pdestructionoperation_next[.SOURCE = CONFIG_ITERATOR pconfigiterator_empty "next"])',
        'PhpStep: S_buffer ~> S_handoff',
        'S_handoff.TODO = (THROW_SEARCH n_pending) :: (CONFIG_INVOKE pconfigcall) :: ptask_buffer*',
        'S_handoff.COMPLETION = NORMAL',
        owners('S_handoff', 'HARRAY n_argument', 1),
    ] + public('S_handoff') + seek('S_handoff', 944, 'S_prefix_dtor') + destructor('S_prefix_dtor', 'prefix', 'n_prefix_payload') + [
        'S_prefix_dtor.DESTRUCTION.OPERATIONS = pdestructionoperation_prefix :: pdestructionoperation_prefix_tail*',
        'pdestructionoperation_prefix.SOURCE = THROW_SEARCH n_pending',
        '$eager_operation_source_valid(S_prefix_dtor, pdestructionoperation_prefix)',
        '~((HARRAY n_argument) <- S_prefix_dtor.ALLOCATIONS)',
        '$config_iterator_value_receipt(S_prefix_dtor, PARRAY n_argument)',
        '~$config_iterator_argument(S_prefix_dtor, PARRAY n_argument)',
        '$weakref_get(S_prefix_dtor, n_iterator_watch) = PNULL',
        '$weakref_get(S_prefix_dtor, n_cache_watch) = PNULL',
    ] + public('S_prefix_dtor') + seek('S_prefix_dtor', 945, 'S_catch') + [
        '$lookup(S_catch.ENV, $ptascii("e")) = (n_e)',
        'S_catch.STORE[n_e] = DEFINED (POBJECT n_pending)',
        '$throwable_field(S_catch, n_pending, "previous") = PNULL',
        'S_catch.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_catch.PRECISIONINI = $ptascii("14")',
        '$weakref_get(S_catch, n_prefix_watch) = PNULL',
        '~((HOBJECT n_prefix_payload) <- S_catch.ALLOCATIONS)',
        '~((HOBJECT n_cache_payload) <- S_catch.ALLOCATIONS)',
        '~((HOBJECT n_object) <- S_catch.ALLOCATIONS)',
        '~((HARRAY n_argument) <- S_catch.ALLOCATIONS)',
    ] + public('S_catch')
    return checks + finish('S_catch', stdout, ['HOBJECT n_object', 'HOBJECT n_aggregate',
        'HOBJECT n_prefix_payload', 'HOBJECT n_cache_payload', 'HARRAY n_argument',
        'HARRAY n_clone', 'HCELL n_cache', 'HOBJECT n_iterator_watch',
        'HOBJECT n_prefix_watch', 'HOBJECT n_cache_watch', 'HOBJECT n_saved',
        'HOBJECT n_pending'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
