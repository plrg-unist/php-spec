#!/usr/bin/env python3
"""Outer receiver snapshots precede inner reference preparation and errors."""
from pathlib import Path

import closure_call_argument_list_review_protocol as reuse
import closure_call_outer_binding_review_sources as sources

prior, process_base = reuse.prior, reuse.process_base
define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
CASE = sources.CASE
PREFIX = reuse.PREFIX + r'''
dec $test_closure_outer_peer_front(pstate,nat) : bool
def $test_closure_outer_peer_front(S,0) = true
  -- if S.TODO = (CLOSURE_CALL_ARGS pclosurecall) :: ptask_tail*
  -- if pclosurecall.INDEX = 0
def $test_closure_outer_peer_front(S,1) = true
  -- if S.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall (KNOWN (PARRAY n)) 0) :: ptask_tail*
  -- if pclosurecall.INDEX = 0
def $test_closure_outer_peer_front(S,2) = true
  -- if S.TODO = (CLOSURE_CALL_ARGS pclosurecall) :: ptask_tail*
  -- if pclosurecall.INDEX = 1
def $test_closure_outer_peer_front(S,3) = true
  -- if S.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall (KNOWN (PARRAY n)) 0) :: ptask_tail*
  -- if pclosurecall.INDEX = 1
def $test_closure_outer_peer_front(S,4) = true
  -- if S.TODO = (CLOSURE_CALL_ARGS pclosurecall) :: ptask_tail*
  -- if pclosurecall.INDEX = 2
def $test_closure_outer_peer_front(S,5) = true
  -- if S.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall (KNOWN (PARRAY n)) 0) :: ptask_tail*
  -- if pclosurecall.INDEX = 2
def $test_closure_outer_peer_front(S,6) = true
  -- if S.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall (KNOWN (PARRAY n)) 1) :: ptask_tail*
  -- if pclosurecall.INDEX = 2
def $test_closure_outer_peer_front(S,7) = true
  -- if S.TODO = (CLOSURE_CALL_INVOKE pclosurecall) :: ptask_tail*
def $test_closure_outer_peer_front(S,8) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
def $test_closure_outer_peer_front(S,9) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_name) metadata_name) :: expression_tail*
  -- if $base64(text_name) = $ptascii("error")
def $test_closure_outer_peer_front(S,10) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_name) metadata_name) :: expression_tail*
  -- if $base64(text_name) = $ptascii("raw")
def $test_closure_outer_peer_front(S,n_phase) = false -- otherwise
dec $test_closure_outer_peer_seek(pstate,nat,nat) : pstate
def $test_closure_outer_peer_seek(S,n_phase,0) = S
def $test_closure_outer_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_closure_outer_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_closure_outer_peer_seek(S,n_phase,n) = $test_closure_outer_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_closure_outer_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_closure_outer_peer_seek({start},{phase},3000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_closure_outer_peer_front({state},{phase})', *common.public(state)]


settle, budget = reuse.settle, reuse.budget


def checks(initial, stdout):
    first = b'B|N|calleeHeld|payloadHeld|'
    received = first + b'I|17|'
    collected = received + b'L|currentObject|calleeHeld|payloadHeld|'
    message = 'Closure::call(): Argument #1 ($newThis) must be of type object, int given'
    duplicate = 'Named parameter $x overwrites previous argument'
    caught = collected + b'TYPE|' + message.encode() + (
        b'|62|none|call|Closure|->|file|62|saved17|pos31|rawPayload|end|'
        b'liveObject|53|97|3|0|0|currentNull|calleeGone|payloadHeld|')
    assert stdout == caught + b'rawKept|rawHeld|released|23|A|'
    values = [*initial, 'S_initial.COMPLETION = BUDGET',
        *reach('S_capture','S_initial',0),
        'S_capture.TODO = (CLOSURE_CALL_ARGS pclosurecall_capture) :: ptask_capture*',
        'n_source = pclosurecall_capture.SOURCE',
        'pclosurecall_capture.FIRST = eps','pclosurecall_capture.RECEIVER = eps',
        'pclosurecall_capture.PACKS = eps','pclosurecall_capture.RAW = eps',
        *[f'$lookup(S_capture.ENV,{text(name)}) = (n_{name}_cv)' for name in
            ['call','payload','namedCell','receiverCell','namedPack','receiverPack','values',
             'weakCall','weakPayload','effects','warnings','bodies','result']],
        'S_capture.STORE[n_call_cv] = DEFINED (POBJECT n_source)',
        'S_capture.STORE[n_payload_cv] = DEFINED (POBJECT n_payload)',
        'S_capture.STORE[n_namedCell_cv] = DEFINED (POBJECT n_payload)',
        'S_capture.STORE[n_receiverCell_cv] = DEFINED (PINT 17)',
        'S_capture.STORE[n_namedPack_cv] = DEFINED (PARRAY n_named_pack)',
        'S_capture.STORE[n_receiverPack_cv] = DEFINED (PARRAY n_receiver_pack)',
        'S_capture.STORE[n_values_cv] = DEFINED (PARRAY n_values_pack)',
        'S_capture.STORE[n_weakCall_cv] = DEFINED (POBJECT n_weak_call)',
        'S_capture.STORE[n_weakPayload_cv] = DEFINED (POBJECT n_weak_payload)',
        'S_capture.ARRAYS[n_named_pack].ITEMS = [ENTRY (KSTRING $ptascii("x")) (ALIAS n_namedCell_cv)]',
        'S_capture.ARRAYS[n_receiver_pack].ITEMS = [ENTRY (KSTRING $ptascii("newThis")) (ALIAS n_receiverCell_cv)]',
        *reach('S_named','S_capture',1),
        'S_named.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_named (KNOWN (PARRAY n_named_pack)) 0) :: ptask_named*',
        'pclosurecall_named.PACKS = [pconfigpack_named]',
        'pconfigpack_named.INDEX = 0','pconfigpack_named.ARRAY = n_named_pack',
        'pconfigpack_named.ITEMS = [ENTRY (KSTRING $ptascii("x")) (DIRECT (POBJECT n_payload))]',
        'pclosurecall_named.FIRST = eps','pclosurecall_named.RAW = eps',
        *reach('S_before_receiver_pending','S_named',2),
        *settle('S_before_receiver','S_before_receiver_pending'),
        'S_before_receiver.TODO = (CLOSURE_CALL_ARGS pclosurecall_before_receiver) :: ptask_before_receiver*',
        'pclosurecall_before_receiver.FIRST = eps','pclosurecall_before_receiver.RECEIVER = eps',
        'pclosurecall_before_receiver.RAW = [(KSTRING $ptascii("x"),KNOWN (POBJECT n_payload))]',
        'pclosurecall_before_receiver.SENT = {SLOTS ([(NAMED_SENT (KNOWN (POBJECT n_payload)))]),NAMED eps}',
        'pclosurecall_before_receiver.ERROR = eps',
        '~(HARRAY n_named_pack <- S_before_receiver.ALLOCATIONS)',
        '$test_outputs(S_before_receiver.EVENTS) = ' + term(first),
        *budget('S_before_receiver'),
        *reach('S_receiver','S_before_receiver',3),
        'S_receiver.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_receiver (KNOWN (PARRAY n_receiver_pack)) 0) :: ptask_receiver*',
        'pclosurecall_receiver.PACKS = [pconfigpack_named,pconfigpack_receiver]',
        'pconfigpack_receiver.INDEX = 1','pconfigpack_receiver.ARRAY = n_receiver_pack',
        'pconfigpack_receiver.ITEMS = [ENTRY (KSTRING $ptascii("newThis")) (DIRECT (PINT 17))]',
        'pclosurecall_receiver.FIRST = eps','pclosurecall_receiver.RECEIVER = eps',
        'pclosurecall_receiver.RAW = pclosurecall_before_receiver.RAW',
        *reach('S_after_receiver_pending','S_receiver',4),
        *settle('S_after_receiver','S_after_receiver_pending'),
        'S_after_receiver.TODO = (CLOSURE_CALL_ARGS pclosurecall_after_receiver) :: ptask_after_receiver*',
        'pclosurecall_after_receiver.FIRST = (PINT 17)',
        'pclosurecall_after_receiver.RECEIVER = eps',
        'pclosurecall_after_receiver.RAW = pclosurecall_before_receiver.RAW',
        'pclosurecall_after_receiver.SENT = pclosurecall_before_receiver.SENT',
        'pclosurecall_after_receiver.ERROR = eps',
        '~(HARRAY n_receiver_pack <- S_after_receiver.ALLOCATIONS)',
        'S_after_receiver.STORE[n_receiverCell_cv] = DEFINED (PINT 17)',
        '$test_outputs(S_after_receiver.EVENTS) = ' + term(received),
        *budget('S_after_receiver'),
        *reach('S_later','S_after_receiver',5),
        'S_later.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_later (KNOWN (PARRAY n_values_pack)) 0) :: ptask_later*',
        'pclosurecall_later.PACKS = [pconfigpack_named,pconfigpack_receiver,pconfigpack_later]',
        'pconfigpack_later.INDEX = 2','pconfigpack_later.ARRAY = n_values_pack',
        'pconfigpack_later.ITEMS = [ENTRY (KINT 9) (DIRECT (PINT 31))]',
        'pclosurecall_later.FIRST = (PINT 17)','pclosurecall_later.RECEIVER = eps',
        'pclosurecall_later.RAW = pclosurecall_after_receiver.RAW',
        'S_later.STORE[n_receiverCell_cv] = DEFINED (POBJECT n_live)',
        'S_later.STORE[n_namedCell_cv] = DEFINED (POBJECT n_live)',
        '$objectprops_at(S_later.OBJECTPROPS,n_live) = (ppropertyslot_all*)',
        '$property_slot_at(ppropertyslot_all*,$ptascii("tag")) = (ppropertyslot_tag)',
        'ppropertyslot_tag.STATE = PROP_VALUE (DIRECT (PINT 53))',
        'S_later.STORE[n_call_cv] = DEFINED PNULL','S_later.STORE[n_payload_cv] = DEFINED PNULL',
        'S_later.STORE[n_namedPack_cv] = DEFINED PNULL',
        'S_later.STORE[n_receiverPack_cv] = DEFINED PNULL','S_later.STORE[n_values_cv] = DEFINED PNULL',
        '(HOBJECT n_source) <- S_later.ALLOCATIONS','(HOBJECT n_payload) <- S_later.ALLOCATIONS',
        '~(HARRAY n_named_pack <- S_later.ALLOCATIONS)',
        '~(HARRAY n_receiver_pack <- S_later.ALLOCATIONS)',
        '$test_outputs(S_later.EVENTS) = ' + term(collected),
        *reach('S_sent','S_later',6),
        'S_sent.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_sent (KNOWN (PARRAY n_values_pack)) 1) :: ptask_sent*',
        'pclosurecall_sent.FIRST = (PINT 17)','pclosurecall_sent.RECEIVER = eps',
        'pclosurecall_sent.RAW = [(KINT 1,KNOWN (PINT 31)),(KSTRING $ptascii("x"),KNOWN (POBJECT n_payload))]',
        'pclosurecall_sent.SENT = {SLOTS eps,NAMED eps}',
        'pclosurecall_sent.ERROR = (' + text(duplicate) + ')',
        *reach('S_invoke_pending','S_sent',7),*settle('S_invoke','S_invoke_pending'),
        'S_invoke.TODO = (CLOSURE_CALL_INVOKE pclosurecall) :: ptask_invoke*',
        'pclosurecall.SOURCE = n_source','pclosurecall.INDEX = 3',
        'pclosurecall.FIRST = (PINT 17)','pclosurecall.RECEIVER = eps',
        'pclosurecall.PACKS = [pconfigpack_named,pconfigpack_receiver,pconfigpack_later]',
        'pclosurecall.RAW = pclosurecall_sent.RAW','pclosurecall.SENT = pclosurecall_sent.SENT',
        'pclosurecall.ERROR = pclosurecall_sent.ERROR',
        '~(HARRAY n_named_pack <- S_invoke.ALLOCATIONS)',
        '~(HARRAY n_receiver_pack <- S_invoke.ALLOCATIONS)',
        '~(HARRAY n_values_pack <- S_invoke.ALLOCATIONS)',
        'S_invoke.STORE[n_receiverCell_cv] = DEFINED (POBJECT n_live)',
        'S_invoke.STORE[n_namedCell_cv] = DEFINED (POBJECT n_live)',
        'S_invoke.STORE[n_warnings_cv] = DEFINED (PINT 0)',
        'S_invoke.STORE[n_bodies_cv] = DEFINED (PINT 0)',
        'S_invoke.STORE[n_result_cv] = DEFINED (PINT 97)',*budget('S_invoke')]
    # These are undriven projections of a genuine collected call.
    for change in ['.PACKS = eps',
            '.PACKS = [pconfigpack_named,pconfigpack_later]',
            '.PACKS = [pconfigpack_receiver,pconfigpack_named,pconfigpack_later]',
            '.PACKS = [pconfigpack_named,pconfigpack_receiver,pconfigpack_later,pconfigpack_later]',
            '.INDEX = 2','.LINE = $(pclosurecall.LINE + 1)',
            '.FIRST = eps','.FIRST = (POBJECT n_live)','.RECEIVER = (n_live)',
            '.RAW = [(KSTRING $ptascii("x"),KNOWN (POBJECT n_payload)),(KINT 1,KNOWN (PINT 31))]',
            '.RAW = [(KINT 9,KNOWN (PINT 31)),(KSTRING $ptascii("x"),KNOWN (POBJECT n_payload))]',
            '.ERROR = eps']:
        values += [f'~$call_task_valid(S_invoke,CLOSURE_CALL_INVOKE pclosurecall[{change}])']
    for change in ['.INDEX = 0','.ARRAY = |S_invoke.ARRAYS|','.SITE = PORIGIN 0 eps',
            '.LINE = $(pconfigpack_receiver.LINE + 1)',
            '.ITEMS = [ENTRY (KSTRING $ptascii("newThis")) (ALIAS n_receiverCell_cv)]']:
        values += [f'~$call_task_valid(S_invoke,CLOSURE_CALL_INVOKE pclosurecall[.PACKS = [pconfigpack_named,pconfigpack_receiver[{change}],pconfigpack_later]])']
    values += [
        'S_history = S_invoke[.ARRAYS[n_named_pack].ITEMS = [ENTRY (KSTRING $ptascii("x")) (DIRECT (PINT 88))]][.ARRAYS[n_receiver_pack].ITEMS = [ENTRY (KSTRING $ptascii("newThis")) (DIRECT (PINT 99))]]',
        '$call_task_valid(S_history,CLOSURE_CALL_INVOKE pclosurecall)',
        *reach('S_error_pending','S_invoke',8),*settle('S_error','S_error_pending'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_error*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable','pthrowable.KIND = "TypeError"',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text(message) + ')',
        '$throwable_field(S_error,n_error,"line") = PINT 62',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]',
        '$entry_lookup(S_error.ARRAYS[n_frame].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args))',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 17)),ENTRY (KINT 1) (DIRECT (PINT 31)),ENTRY (KSTRING $ptascii("x")) (DIRECT (POBJECT n_payload))]',
        '~(HOBJECT n_source <- S_error.ALLOCATIONS)',
        '(HOBJECT n_payload) <- S_error.ALLOCATIONS',
        'S_error.STORE[n_warnings_cv] = DEFINED (PINT 0)',
        'S_error.STORE[n_bodies_cv] = DEFINED (PINT 0)',
        'S_error.STORE[n_result_cv] = DEFINED (PINT 97)',
        *reach('S_caught','S_error',9),
        '$lookup(S_caught.ENV,$ptascii("raw")) = (n_raw_cv)',
        'S_caught.STORE[n_raw_cv] = DEFINED (PARRAY n_args)',
        '$test_outputs(S_caught.EVENTS) = ' + term(caught),
        *reach('S_raw_pending','S_caught',10),*settle('S_raw','S_raw_pending'),
        'S_raw.STORE[n_raw_cv] = DEFINED (PARRAY n_args)',
        '~(HCELL n_namedCell_cv <- S_raw.ALLOCATIONS)',
        '~(HCELL n_receiverCell_cv <- S_raw.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_raw.ALLOCATIONS)','~(HOBJECT n_live <- S_raw.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_raw.ALLOCATIONS)','~(HARRAY n_frame <- S_raw.ALLOCATIONS)',
        '(HARRAY n_args) <- S_raw.ALLOCATIONS',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_payload) = 1',
        '$test_outputs(S_raw.EVENTS) = ' + term(caught + b'rawKept|rawHeld|'),
        *define.finish('S_raw',stdout)]
    for node in ['HOBJECT n_source','HOBJECT n_payload','HOBJECT n_live',
            'HOBJECT n_weak_call','HOBJECT n_weak_payload',
            'HARRAY n_named_pack','HARRAY n_receiver_pack','HARRAY n_values_pack',
            'HCELL n_namedCell_cv','HCELL n_receiverCell_cv',
            'HOBJECT n_error','HARRAY n_trace','HARRAY n_frame','HARRAY n_args']:
        values += [f'~({node} <- S_final.ALLOCATIONS)']
    return values


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = process_base.process


def process(command, directory, timeout, cwd):
    if directory.parent.name == CASE:
        timeout = 420
    return packet_process(command,directory,timeout,cwd)


packet.process = process
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    raise SystemExit(0 if packet.main() else 1)
