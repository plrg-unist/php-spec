#!/usr/bin/env python3
"""Real copied argument roots, embedded aliases, API traces, and final owners."""
from pathlib import Path
from types import SimpleNamespace

import config_iterator_argument_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek

ARRAY = 'config-owning-argument-byref-array-api-trace'
SELF = 'config-owning-argument-self-object-api-trace'
SOURCES = SimpleNamespace(CASES={name: cases.CASES[name] for name in (ARRAY, SELF)},
                          __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a69_echo(pstate, ptbytes) : bool
def $a69_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a69_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 930) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "key-start") :: ptask*
  -- if |pconfigiterator.ITEMS| = 1
def $list_warning_frontier(S, 931) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "send") :: ptask*
  -- if |pconfigiterator.ITEMS| = 1
def $list_warning_frontier(S, 932) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "ready") :: ptask*
def $list_warning_frontier(S, 933) = $a69_echo(S, $ptascii("D:"))
def $list_warning_frontier(S, 934) = $a69_echo(S, $ptascii("E:"))
def $list_warning_frontier(S, 935) = $a69_echo(S, $ptascii("T:"))
def $list_warning_frontier(S, 936) = $a69_echo(S, $ptascii("V:"))
def $list_warning_frontier(S, 937) = $a69_echo(S, $ptascii("R:"))
'''


def bound(state, names):
    return [f'$lookup({state}.ENV, $ptascii("{name}")) = (n_{name})' for name in names]


def row(state, array, value, leaf='n_leaf'):
    return [f'{state}.ARRAYS[{array}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT {value})), ENTRY (KINT 1) (ALIAS {leaf})]']


def trace(state, error, value):
    return [f'$throwable_field({state}, {error}, "previous") = PNULL',
            f'$throwable_field({state}, {error}, "trace") = PARRAY n_trace',
            f'{state}.ARRAYS[n_trace].ITEMS[0] = ENTRY (KINT 0) (DIRECT (PARRAY n_trace_frame))',
            f'(ENTRY (KSTRING ($ptascii("args"))) (DIRECT (PARRAY n_args))) <- {state}.ARRAYS[n_trace_frame].ITEMS',
            f'{state}.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option), ENTRY (KINT 1) (DIRECT ({value}))]',
            '$string_bytes(pvalue_option) = ($ptascii("precision"))']


def array(program, path, stdout):
    checks = initial(program, path) + seek('S_initial', 930, 'S_cache') + [
        'S_cache.TODO = (CONFIG_ITERATOR pconfigiterator_cache "key-start") :: ptask_tail*',
        'pconfigiterator_cache.OBJECT = n_object',
        'pconfigiterator_cache.PRODUCER = (n_aggregate)',
        'pconfigiterator_cache.CURRENT = REFERENCE n_row',
        '$config_iterator_current_value(S_cache, pconfigiterator_cache, REFERENCE n_row) = (PARRAY n_initial)',
        '$config_iterator_current_receipt(S_cache, pconfigiterator_cache, KNOWN (PARRAY n_initial))',
        '$config_iterator_current_value(S_cache, pconfigiterator_cache, KNOWN (PARRAY n_initial)) = (PARRAY n_initial)',
        '$config_iterator_current_argument(S_cache, pconfigiterator_cache)',
        '$config_iterator_valid(S_cache, pconfigiterator_cache, "key-start")',
        '~((HOBJECT n_aggregate) <- S_cache.ALLOCATIONS)',
    ] + bound('S_cache', ['row', 'leaf', 'saved', 'watch', 'result']) + [
        'S_cache.STORE[n_row] = DEFINED (PARRAY n_initial)',
        'S_cache.STORE[n_saved] = DEFINED (PARRAY n_initial)',
        'S_cache.STORE[n_leaf] = DEFINED (PINT 7)',
        'S_cache.STORE[n_watch] = DEFINED (POBJECT n_weak)',
        owners('S_cache', 'HCELL n_row', 2), owners('S_cache', 'HARRAY n_initial', 2),
        owners('S_cache', 'HCELL n_leaf', 2),
    ] + row('S_cache', 'n_initial', 3) + public('S_cache')
    checks += seek('S_cache', 931, 'S_send') + [
        'S_send.TODO = (CONFIG_ITERATOR pconfigiterator_send "send") :: ptask_tail*',
        'pconfigiterator_send.CURRENT = REFERENCE n_row',
        'pconfigiterator_send.KEY = KNOWN (PINT 1)',
        'S_send.STORE[n_row] = DEFINED (PARRAY n_argument)',
        'n_argument =/= n_initial',
        '~((HARRAY n_initial) <- S_send.ALLOCATIONS)',
        'S_send.STORE[n_leaf] = DEFINED (PINT 17)',
        '$lookup(S_send.ENV, $ptascii("saved")) = eps',
        '$config_iterator_current_value(S_send, pconfigiterator_send, REFERENCE n_row) = (PARRAY n_argument)',
        '$config_iterator_argument(S_send, PARRAY n_argument)',
        owners('S_send', 'HCELL n_row', 2), owners('S_send', 'HARRAY n_argument', 1),
        owners('S_send', 'HCELL n_leaf', 2),
    ] + row('S_send', 'n_argument', 22) + public('S_send') + [
        'PhpStep: S_send ~> S_sent',
        'S_sent.TODO = (CONFIG_ITERATOR pconfigiterator_sent "next-start") :: ptask_tail*',
        'pconfigiterator_sent = pconfigiterator_send[.ITEMS = pconfigiterator_send.ITEMS ++ [ENTRY (KINT 1) (DIRECT (PARRAY n_argument))]][.CURRENT = KNOWN PNULL][.KEY = KNOWN PNULL]',
        '$config_iterator_argument_nodes(pconfigiterator_sent) = [HARRAY n_argument]',
        '$task_nodes(CONFIG_ITERATOR pconfigiterator_sent "next-start") = [HOBJECT n_object, HARRAY n_argument]',
        owners('S_sent', 'HCELL n_row', 1), owners('S_sent', 'HARRAY n_argument', 2),
    ] + public('S_sent') + budget('S_sent', 'S_sent_budget')
    checks += seek('S_sent', 933, 'S_dtor') + [
        'S_dtor.CURRENT = (pcallcontext_dtor)',
        '$destructor_context_call(pcallcontext_dtor, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object', 'pdestructorcall.PENDING = eps',
        '$destructor_call_live(S_dtor, pdestructorcall)',
        'S_dtor.STORE[n_row] = DEFINED (PARRAY n_live)',
        'n_live =/= n_argument',
        'S_dtor.STORE[n_leaf] = DEFINED (PINT 29)',
        '$lookup($global_table_view(S_dtor).ENV, $ptascii("leaf")) = eps',
        'S_dtor.PRECISIONINI = $ptascii("14")',
        owners('S_dtor', 'HARRAY n_argument', 1), owners('S_dtor', 'HARRAY n_live', 1),
        owners('S_dtor', 'HCELL n_leaf', 2),
    ] + row('S_dtor', 'n_live', 33) + row('S_dtor', 'n_argument', 22) + public('S_dtor')
    checks += seek('S_dtor', 932, 'S_ready') + [
        'S_ready.TODO = (CONFIG_ITERATOR pconfigiterator_ready "ready") :: ptask_ready*',
        '$config_iterator_valid(S_ready, pconfigiterator_ready, "ready")',
        '$config_iterator_retired_scope(S_ready, pconfigiterator_ready)',
        '~((HOBJECT n_object) <- S_ready.ALLOCATIONS)',
        '$weakref_get(S_ready, n_weak) = PNULL',
        'S_ready.STORE[n_leaf] = DEFINED (PINT 31)',
        '$config_pack_prefix(pconfigiterator_ready.CALL, pconfigiterator_ready.ITEMS, false) = (pconfigcall_prefix)',
        'pconfigcall = pconfigcall_prefix[.INDEX = 1]',
        '$config_iterator_copied_call(S_ready, pconfigcall)',
        '$config_invoke_valid(S_ready, pconfigcall)',
        '~$config_iterator_copied_call(S_ready, pconfigcall[.INDEX = 0])',
        '~$config_iterator_copied_call(S_ready, pconfigcall[.LINE = $(pconfigcall.LINE + 1)])',
        '$config_nodes(pconfigcall) = [HARRAY n_argument]',
        owners('S_ready', 'HARRAY n_argument', 1),
        'PhpStep: S_ready ~> S_invoke',
        'S_invoke.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_ready*',
        '$task_nodes(CONFIG_INVOKE pconfigcall) = [HARRAY n_argument]',
        'pconfigcall_null = pconfigcall[.SENT = [NAMED_SENT (KNOWN PNULL), NAMED_SENT (KNOWN (PARRAY n_argument))]]',
        'S_null = S_invoke[.TODO = (CONFIG_INVOKE pconfigcall_null) :: ptask_ready*]',
        '$config_iterator_copied_call(S_null, pconfigcall_null)',
        '$config_ini_null_valid(S_null, pconfigcall_null)',
        '~$config_ini_rejected_array(S_null, n_argument)',
        '~$config_ini_rejected_alias_array(S_null, n_argument)',
        'S_null_error = $config_ini_null_finish(S_null, pconfigcall_null)',
        'S_null_error.COMPLETION = THROWING n_null_error',
        '$throwable_field(S_null_error, n_null_error, "trace") = PARRAY n_null_trace',
        'S_null_error.ARRAYS[n_null_trace].ITEMS[0] = ENTRY (KINT 0) (DIRECT (PARRAY n_null_frame))',
        '(ENTRY (KSTRING ($ptascii("args"))) (DIRECT (PARRAY n_null_args))) <- S_null_error.ARRAYS[n_null_frame].ITEMS',
        'S_null_error.ARRAYS[n_null_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING eps)), ENTRY (KINT 1) (DIRECT (PARRAY n_argument))]',
        owners('S_null_error', 'HARRAY n_argument', 2),
        'S_null_flat = S_null[.ARRAYS[n_argument].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 17))]]',
        '$config_ini_rejected_array(S_null_flat, n_argument)',
        '$config_ini_null_valid(S_null_flat, pconfigcall_null)',
        'S_null_flat_error = $config_ini_null_finish(S_null_flat, pconfigcall_null)',
        'S_null_flat_error.COMPLETION = THROWING n_null_flat_error',
        'S_null_alias = S_null[.ARRAYS[n_argument].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf)]]',
        '$config_ini_rejected_alias_array(S_null_alias, n_argument)',
        '$config_ini_null_valid(S_null_alias, pconfigcall_null)',
        'S_null_alias_error = $config_ini_null_finish(S_null_alias, pconfigcall_null)',
        'S_null_alias_error.COMPLETION = THROWING n_null_alias_error',
        'PhpStep: S_invoke ~> S_error',
        'S_error.COMPLETION = THROWING n_error',
        '$throwable_field(S_error, n_error, "message") = pvalue_message',
        '$string_bytes(pvalue_message) = ($ptascii("ini_set(): Argument #2 ($value) must be of type string|int|float|bool|null"))',
        owners('S_error', 'HARRAY n_argument', 2),
    ] + row('S_ready', 'n_live', 44) + trace('S_error', 'n_error', 'PARRAY n_argument') + public('S_ready')
    checks += seek('S_invoke', 934, 'S_catch') + [
        'S_catch.STORE[n_result] = DEFINED (PINT 99)',
        'S_catch.PRECISIONINI = $ptascii("14")',
        '$lookup(S_catch.ENV, $ptascii("e")) = (n_e)',
        'S_catch.STORE[n_e] = DEFINED (POBJECT n_error)',
        owners('S_catch', 'HARRAY n_argument', 1), owners('S_catch', 'HOBJECT n_error', 1),
        owners('S_catch', 'HCELL n_leaf', 2),
    ] + public('S_catch')
    checks += seek('S_catch', 936, 'S_cow') + bound('S_cow', ['captured']) + [
        'S_cow.STORE[n_captured] = DEFINED (PARRAY n_copy)',
        'n_copy =/= n_argument', 'n_copy =/= n_live',
        'S_cow.STORE[n_leaf] = DEFINED (PINT 88)',
        owners('S_cow', 'HARRAY n_argument', 1), owners('S_cow', 'HARRAY n_copy', 1),
        owners('S_cow', 'HARRAY n_live', 1), owners('S_cow', 'HCELL n_leaf', 3),
    ] + row('S_cow', 'n_argument', 22) + row('S_cow', 'n_copy', 77) + row('S_cow', 'n_live', 55) + public('S_cow')
    return checks + finish('S_cow', stdout, ['HOBJECT n_object', 'HOBJECT n_aggregate',
        'HOBJECT n_weak', 'HOBJECT n_error', 'HARRAY n_argument', 'HARRAY n_copy',
        'HARRAY n_live', 'HCELL n_row', 'HCELL n_leaf'])


def self_object(program, path, stdout):
    checks = initial(program, path) + seek('S_initial', 931, 'S_send') + [
        'S_send.TODO = (CONFIG_ITERATOR pconfigiterator_send "send") :: ptask_tail*',
        'pconfigiterator_send.OBJECT = n_object',
        'pconfigiterator_send.PRODUCER = (n_aggregate)',
        'pconfigiterator_send.CURRENT = KNOWN (POBJECT n_object)',
        '$config_iterator_current_receipt(S_send, pconfigiterator_send, KNOWN (POBJECT n_object))',
        '$config_iterator_current_argument(S_send, pconfigiterator_send)',
        '$config_iterator_valid(S_send, pconfigiterator_send, "send")',
        owners('S_send', 'HOBJECT n_object', 2),
        'PhpStep: S_send ~> S_sent',
        'S_sent.TODO = (CONFIG_ITERATOR pconfigiterator_sent "next-start") :: ptask_tail*',
        '$config_iterator_argument_nodes(pconfigiterator_sent) = [HOBJECT n_object]',
        '$task_nodes(CONFIG_ITERATOR pconfigiterator_sent "next-start") = [HOBJECT n_object, HOBJECT n_object]',
        owners('S_sent', 'HOBJECT n_object', 2),
    ] + bound('S_send', ['watch', 'result', 'dtors', 'stage']) + [
        'S_send.STORE[n_watch] = DEFINED (POBJECT n_weak)',
        'S_send.STORE[n_dtors] = DEFINED (PINT 0)',
    ] + public('S_sent')
    checks += seek('S_sent', 932, 'S_ready') + [
        'S_ready.TODO = (CONFIG_ITERATOR pconfigiterator_ready "ready") :: ptask_ready*',
        '$config_iterator_valid(S_ready, pconfigiterator_ready, "ready")',
        '~$config_iterator_retired_scope(S_ready, pconfigiterator_ready)',
        '$weakref_get(S_ready, n_weak) = POBJECT n_object',
        'S_ready.STORE[n_dtors] = DEFINED (PINT 0)',
        '$config_pack_prefix(pconfigiterator_ready.CALL, pconfigiterator_ready.ITEMS, false) = (pconfigcall_prefix)',
        'pconfigcall = pconfigcall_prefix[.INDEX = 1]',
        '$config_iterator_copied_call(S_ready, pconfigcall)',
        owners('S_ready', 'HOBJECT n_object', 1),
        'PhpStep: S_ready ~> S_invoke',
        'S_invoke.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_ready*',
        '$config_invoke_valid(S_invoke, pconfigcall)',
        'PhpStep: S_invoke ~> S_error',
        'S_error.COMPLETION = THROWING n_error',
        owners('S_error', 'HOBJECT n_object', 2),
    ] + trace('S_error', 'n_error', 'POBJECT n_object') + public('S_ready')
    checks += seek('S_invoke', 934, 'S_catch') + [
        '$lookup(S_catch.ENV, $ptascii("e")) = (n_e)',
        'S_catch.STORE[n_e] = DEFINED (POBJECT n_error)',
        '$weakref_get(S_catch, n_weak) = POBJECT n_object',
        'S_catch.STORE[n_result] = DEFINED (PINT 99)',
        'S_catch.STORE[n_dtors] = DEFINED (PINT 0)',
        owners('S_catch', 'HOBJECT n_object', 1),
    ] + public('S_catch')
    checks += seek('S_catch', 935, 'S_trace') + bound('S_trace', ['arg']) + [
        'S_trace.STORE[n_arg] = DEFINED (POBJECT n_object)',
        owners('S_trace', 'HOBJECT n_object', 2),
        'S_trace.STORE[n_dtors] = DEFINED (PINT 0)',
    ] + public('S_trace')
    checks += seek('S_trace', 933, 'S_dtor') + [
        'S_dtor.CURRENT = (pcallcontext_dtor)',
        '$destructor_context_call(pcallcontext_dtor, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object', 'pdestructorcall.PENDING = eps',
        '$destructor_call_live(S_dtor, pdestructorcall)',
        'S_dtor.STORE[n_stage] = DEFINED pvalue_stage',
        '$string_bytes(pvalue_stage) = ($ptascii("release"))',
        'S_dtor.STORE[n_dtors] = DEFINED (PINT 0)',
    ] + public('S_dtor')
    checks += seek('S_dtor', 937, 'S_released') + [
        '$weakref_get(S_released, n_weak) = PNULL',
        '~((HOBJECT n_object) <- S_released.ALLOCATIONS)',
        '~((HOBJECT n_error) <- S_released.ALLOCATIONS)',
        'S_released.STORE[n_dtors] = DEFINED (PINT 1)',
    ] + public('S_released')
    return checks + finish('S_released', stdout, ['HOBJECT n_object',
        'HOBJECT n_aggregate', 'HOBJECT n_weak', 'HOBJECT n_error'])


def conditions(name, program, path, stdout):
    return (array if name == ARRAY else self_object)(program, path, stdout)


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
