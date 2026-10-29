#!/usr/bin/env python3
"""Final temporary INPUT retires before API while distinct copied args stay live."""
from pathlib import Path
from types import SimpleNamespace

import config_iterator_input_finalizer_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek

NAME='config-temporary-input-object-argument-finalizer-trace'
SOURCES=SimpleNamespace(CASES={NAME:cases.CASES[NAME]},__file__=cases.__file__)
HELPERS=shared.HELPERS+r'''
dec $a70_echo(pstate, ptbytes) : bool
def $a70_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a70_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 980) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "send") :: ptask*
  -- if |pconfigiterator.ITEMS| = 1
def $list_warning_frontier(S, 981) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "input-release") :: ptask*
def $list_warning_frontier(S, 982) = $a70_echo(S, $ptascii("I:"))
def $list_warning_frontier(S, 983) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "ready") :: ptask*
def $list_warning_frontier(S, 984) = $a70_echo(S, $ptascii("E:"))
def $list_warning_frontier(S, 985) = $a70_echo(S, $ptascii("T:"))
def $list_warning_frontier(S, 986) = $a70_echo(S, $ptascii("P:"))
def $list_warning_frontier(S, 987) = $a70_echo(S, $ptascii("R:"))
'''


def conditions(name,program,path,stdout):
    assert name==NAME
    checks=initial(program,path)+seek('S_initial',980,'S_send')+[
        'S_send.TODO = (CONFIG_ITERATOR pconfigiterator_send "send") :: ptask_tail*',
        'pconfigiterator_send.OBJECT = n_input',
        'pconfigiterator_send.INPUT = KNOWN (POBJECT n_input)',
        'pconfigiterator_send.PRODUCER = eps',
        'pconfigiterator_send.CURRENT = KNOWN (POBJECT n_payload)',
        '$config_iterator_valid(S_send, pconfigiterator_send, "send")',
        '$config_iterator_owning_input(pconfigiterator_send)',
        '$config_iterator_argument_nodes(pconfigiterator_send) = eps',
        'n_input =/= n_payload',
        '$lookup(S_send.ENV, $ptascii("iteratorWatch")) = (n_iterator_watch_cell)',
        'S_send.STORE[n_iterator_watch_cell] = DEFINED (POBJECT n_iterator_watch)',
        '$lookup(S_send.ENV, $ptascii("payloadWatch")) = (n_payload_watch_cell)',
        'S_send.STORE[n_payload_watch_cell] = DEFINED (POBJECT n_payload_watch)',
        '$lookup(S_send.ENV, $ptascii("inputDtors")) = (n_dtors)',
        '$lookup(S_send.ENV, $ptascii("result")) = (n_result)',
        '$lookup(S_send.ENV, $ptascii("stage")) = (n_stage)',
        owners('S_send','HOBJECT n_input',2),owners('S_send','HOBJECT n_payload',1),
        'PhpStep: S_send ~> S_sent',
        'S_sent.TODO = (CONFIG_ITERATOR pconfigiterator_sent "next-start") :: ptask_tail*',
        '$config_iterator_argument_nodes(pconfigiterator_sent) = [HOBJECT n_payload]',
        '$task_nodes(CONFIG_ITERATOR pconfigiterator_sent "next-start") = [HOBJECT n_input, HOBJECT n_input, HOBJECT n_payload]',
        owners('S_sent','HOBJECT n_input',2),owners('S_sent','HOBJECT n_payload',1),
    ]+public('S_sent')+seek('S_sent',981,'S_input')+[
        'S_input.TODO = (CONFIG_ITERATOR pconfigiterator_input "input-release") :: ptask_input*',
        '$config_iterator_valid(S_input, pconfigiterator_input, "input-release")',
        '$config_iterator_owning_input(pconfigiterator_input)',
        '~$config_iterator_quiet_input(S_input, pconfigiterator_input)',
        '$config_iterator_effectful_input(S_input, pconfigiterator_input)',
        '$config_iterator_finalizer(S_input, n_input)',
        '$node_children(S_input, HOBJECT n_input) = eps',
        '$node_children(S_input, HOBJECT n_payload) = eps',
        '$config_iterator_argument_nodes(pconfigiterator_input) = [HOBJECT n_payload]',
        '~$heap_member(HOBJECT n_input, $heap_reach([HOBJECT n_payload], eps, $heap_graph(S_input).EDGES))',
        '$useriter_cursor_count(S_input.ITERATORS, pconfigiterator_input.ITERATOR) = 0',
        owners('S_input','HOBJECT n_input',1),owners('S_input','HOBJECT n_payload',1),
        'pconfigiterator_empty = pconfigiterator_input[.ITEMS = eps]',
        '~$config_iterator_effectful_input(S_input, pconfigiterator_empty)',
        'S_empty_refused = $config_iterator_release_input(S_input, pconfigiterator_empty, ptask_input*)',
        'S_empty_refused.COMPLETION = UNSUPPORTED "CONFIG Iterator unpack last INPUT owner"',
        'S_dead_arg = S_input[.ALLOCATIONS = $destruction_node_delete(S_input.ALLOCATIONS, HOBJECT n_payload)]',
        '~$config_iterator_effectful_input(S_dead_arg, pconfigiterator_input)',
    ]+public('S_input')+budget('S_input','S_input_budget')+seek('S_input',982,'S_dtor')+[
        'S_dtor.CURRENT = (pcallcontext_input)',
        '$destructor_context_call(pcallcontext_input, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall_input)',
        'pdestructorcall_input.OBJECT = n_input',
        'pdestructorcall_input.PENDING = eps',
        '$destructor_call_live(S_dtor, pdestructorcall_input)',
        '$weakref_get(S_dtor, n_payload_watch) = POBJECT n_payload',
        'S_dtor.PRECISIONINI = $ptascii("14")',
        'S_dtor.STORE[n_dtors] = DEFINED (PINT 0)',
        owners('S_dtor','HOBJECT n_payload',1),
    ]+public('S_dtor')+seek('S_dtor',983,'S_ready')+[
        'S_ready.TODO = (CONFIG_ITERATOR pconfigiterator_ready "ready") :: ptask_ready*',
        '$config_iterator_valid(S_ready, pconfigiterator_ready, "ready")',
        '$config_iterator_retired_scope(S_ready, pconfigiterator_ready)',
        '~$config_iterator_effectful_input(S_ready, pconfigiterator_ready)',
        '~((HOBJECT n_input) <- S_ready.ALLOCATIONS)',
        '$weakref_get(S_ready, n_iterator_watch) = PNULL',
        '$weakref_get(S_ready, n_payload_watch) = POBJECT n_payload',
        'S_ready.PRECISIONINI = $ptascii("7")',
        'S_ready.STORE[n_dtors] = DEFINED (PINT 1)',
        '$config_pack_prefix(pconfigiterator_ready.CALL, pconfigiterator_ready.ITEMS, false) = (pconfigcall_prefix)',
        'pconfigcall = pconfigcall_prefix[.INDEX = 1]',
        '$config_iterator_copied_call(S_ready, pconfigcall)',
        '$config_nodes(pconfigcall) = [HOBJECT n_payload]',
        owners('S_ready','HOBJECT n_payload',1),
        'PhpStep: S_ready ~> S_invoke',
        'S_invoke.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_ready*',
        'PhpStep: S_invoke ~> S_error',
        'S_error.COMPLETION = THROWING n_error',
        '$throwable_field(S_error, n_error, "trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS[0] = ENTRY (KINT 0) (DIRECT (PARRAY n_api))',
        '$trace_array_field(S_error, n_api, $ptascii("args")) = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING ($ptascii("precision")))), ENTRY (KINT 1) (DIRECT (POBJECT n_payload))]',
        owners('S_error','HOBJECT n_payload',2),
    ]+public('S_ready')+seek('S_invoke',984,'S_catch')+[
        '$lookup(S_catch.ENV, $ptascii("e")) = (n_e)',
        'S_catch.STORE[n_e] = DEFINED (POBJECT n_error)',
        'S_catch.STORE[n_result] = DEFINED (PINT 99)',
        'S_catch.STORE[n_dtors] = DEFINED (PINT 1)',
        owners('S_catch','HOBJECT n_payload',1),
    ]+public('S_catch')+seek('S_catch',985,'S_trace')+[
        '$lookup(S_trace.ENV, $ptascii("arg")) = (n_arg)',
        'S_trace.STORE[n_arg] = DEFINED (POBJECT n_payload)',
        owners('S_trace','HOBJECT n_payload',2),
    ]+public('S_trace')+seek('S_trace',986,'S_payload_dtor')+[
        'S_payload_dtor.CURRENT = (pcallcontext_payload)',
        '$destructor_context_call(pcallcontext_payload, S_payload_dtor.CURRENT, S_payload_dtor.FRAMES) = (pdestructorcall_payload)',
        'pdestructorcall_payload.OBJECT = n_payload',
        'pdestructorcall_payload.PENDING = eps',
        '$destructor_call_live(S_payload_dtor, pdestructorcall_payload)',
        '$weakref_get(S_payload_dtor, n_iterator_watch) = PNULL',
        'S_payload_dtor.STORE[n_stage] = DEFINED pvalue_stage',
        '$string_bytes(pvalue_stage) = ($ptascii("release"))',
    ]+public('S_payload_dtor')+seek('S_payload_dtor',987,'S_released')+[
        '$weakref_get(S_released, n_payload_watch) = PNULL',
        'S_released.STORE[n_dtors] = DEFINED (PINT 1)',
        '~((HOBJECT n_payload) <- S_released.ALLOCATIONS)',
        '~((HOBJECT n_error) <- S_released.ALLOCATIONS)',
    ]+public('S_released')
    return checks+finish('S_released',stdout,['HOBJECT n_input','HOBJECT n_payload',
        'HOBJECT n_error','HOBJECT n_iterator_watch','HOBJECT n_payload_watch'])


if __name__=='__main__':
    raise SystemExit(0 if shared.run(SOURCES,conditions,HELPERS,model_timeout=300,
        extra_inputs=(Path(__file__),Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
