#!/usr/bin/env python3
"""Canonical mixed-pack forwarding preserves snapshots through a deferred duplicate."""
from pathlib import Path

import define_stdclass_array_duplicate_review_protocol as prior
import typed_static_invoke_set_protocol as process_base
import closure_call_argument_list_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
CASE = sources.CASE
PREFIX = common.PREFIX + r'''
dec $test_closure_list_peer_front(pstate,nat) : bool
def $test_closure_list_peer_front(S,0) = true
  -- if S.TODO = (CLOSURE_CALL_ARGS pclosurecall) :: ptask_tail*
  -- if pclosurecall.INDEX = 0
def $test_closure_list_peer_front(S,1) = true
  -- if S.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall (KNOWN (PARRAY n)) 0) :: ptask_tail*
  -- if pclosurecall.INDEX = 1
def $test_closure_list_peer_front(S,2) = true
  -- if S.TODO = (CLOSURE_CALL_ARGS pclosurecall) :: ptask_tail*
  -- if pclosurecall.INDEX = 2
def $test_closure_list_peer_front(S,3) = true
  -- if S.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall (KNOWN (PARRAY n)) 0) :: ptask_tail*
  -- if pclosurecall.INDEX = 2
def $test_closure_list_peer_front(S,4) = true
  -- if S.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall (KNOWN (PARRAY n)) 1) :: ptask_tail*
  -- if pclosurecall.INDEX = 2
def $test_closure_list_peer_front(S,5) = true
  -- if S.TODO = (CLOSURE_CALL_FORWARD pclosurecall 0 pnamedargs n_base) :: ptask_tail*
def $test_closure_list_peer_front(S,6) = true
  -- if S.TODO = (CLOSURE_CALL_FORWARD pclosurecall 1 pnamedargs n_base) :: ptask_tail*
def $test_closure_list_peer_front(S,7) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
def $test_closure_list_peer_front(S,8) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_name) metadata_name) :: expression_tail*
  -- if $base64(text_name) = $ptascii("error")
def $test_closure_list_peer_front(S,9) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_name) metadata_name) :: expression_tail*
  -- if $base64(text_name) = $ptascii("raw")
def $test_closure_list_peer_front(S,n_phase) = false -- otherwise
dec $test_closure_list_peer_seek(pstate,nat,nat) : pstate
def $test_closure_list_peer_seek(S,n_phase,0) = S
def $test_closure_list_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_closure_list_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_closure_list_peer_seek(S,n_phase,n) = $test_closure_list_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_closure_list_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $test_closure_list_peer_settled(pstate) : bool
def $test_closure_list_peer_settled(S) = (S.DESTRUCTION.RELEASES = eps /\ S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.CALLS = eps)
dec $test_closure_list_peer_user_entry(pstate) : bool
def $test_closure_list_peer_user_entry(S) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
def $test_closure_list_peer_user_entry(S) = false -- otherwise
dec $test_closure_list_peer_settle(pstate,nat) : pstate
def $test_closure_list_peer_settle(S,0) = S
def $test_closure_list_peer_settle(S,n) = S
  -- if $(n > 0)
  -- if $test_closure_list_peer_settled(S) \/ $test_closure_list_peer_user_entry(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_closure_list_peer_settle(S,n) = $test_closure_list_peer_settle($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_closure_list_peer_settled(S) /\ ~$test_closure_list_peer_user_entry(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_closure_list_peer_seek({start},{phase},3000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_closure_list_peer_front({state},{phase})', *common.public(state)]


def settle(state, start):
    return [f'{state}_found = $test_closure_list_peer_settle({start},80)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_closure_list_peer_settled({state})', *common.public(state)]


def budget(state):
    return [f'{state}_pause = $drive_steps({state},0)',
        f'{state}_pause = {state}[.COMPLETION = BUDGET]',
        f'$test_running({state}_pause) = {state}',
        f'$drive_steps({state},1) = $drive_steps($test_running({state}_pause),1)']


def checks(initial, stdout):
    first = b'B|N|calleeHeld|receiverHeld|'
    before_warning = first + b'P|calleeHeld|receiverHeld|'
    marker = b'|warningFile|56|29|31|calleeHeld|receiverHeld|'
    assert stdout.startswith(before_warning + b'W|2|')
    message, _ = stdout[len(before_warning + b'W|2|'):].split(marker,1)
    assert message.startswith(b'V108ReviewReceiver::{closure:')
    assert message.endswith(b':46}(): Argument #1 ($x) must be passed by reference, value given')
    after_warning = before_warning + b'W|2|' + message + marker
    duplicate = b'Named parameter $x overwrites previous argument'
    caught = after_warning + b'E|' + duplicate + (b'|56|none|call|Closure|->|file|56|rawReceiver|pos31|named17|end|'
        b'47|53|97|2|1|0|currentNull|calleeGone|receiverHeld|')
    assert stdout == caught + b'posKept|namedKept|rawHeld|released|23|A|'
    values = [*initial,'S_initial.COMPLETION = BUDGET',
        *reach('S_capture','S_initial',0),
        'S_capture.TODO = (CLOSURE_CALL_ARGS pclosurecall_capture) :: ptask_capture*',
        'n_source = pclosurecall_capture.SOURCE','pclosurecall_capture.PACKS = eps',
        *[f'$lookup(S_capture.ENV,{text(name)}) = (n_{name}_cv)' for name in
            ['call','receiver','namedPack','positionalPack','namedCell','positionalCell','weakCall','weakReceiver','effects','warnings','bodies','result']],
        'S_capture.STORE[n_call_cv] = DEFINED (POBJECT n_source)',
        'S_capture.STORE[n_receiver_cv] = DEFINED (POBJECT n_receiver)',
        'S_capture.STORE[n_namedPack_cv] = DEFINED (PARRAY n_named_pack)',
        'S_capture.STORE[n_positionalPack_cv] = DEFINED (PARRAY n_positional_pack)',
        'S_capture.STORE[n_namedCell_cv] = DEFINED (PINT 17)',
        'S_capture.STORE[n_positionalCell_cv] = DEFINED (PINT 23)',
        'S_capture.STORE[n_weakCall_cv] = DEFINED (POBJECT n_weak_call)',
        'S_capture.STORE[n_weakReceiver_cv] = DEFINED (POBJECT n_weak_receiver)',
        'S_capture.ARRAYS[n_named_pack].ITEMS = [ENTRY (KSTRING $ptascii("x")) (ALIAS n_namedCell_cv)]',
        'S_capture.ARRAYS[n_positional_pack].ITEMS = [ENTRY (KINT 9) (ALIAS n_positionalCell_cv)]',
        *reach('S_first','S_capture',1),
        'S_first.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_first (KNOWN (PARRAY n_named_pack)) 0) :: ptask_first*',
        'pclosurecall_first.PACKS = [pconfigpack_first]',
        'pconfigpack_first.INDEX = 1','pconfigpack_first.ARRAY = n_named_pack',
        'pconfigpack_first.ITEMS = [ENTRY (KSTRING $ptascii("x")) (DIRECT (PINT 17))]',
        'pclosurecall_first.RAW = eps','pclosurecall_first.ERROR = eps',
        *reach('S_between_pending','S_first',2),*settle('S_between','S_between_pending'),
        'S_between.TODO = (CLOSURE_CALL_ARGS pclosurecall_between) :: ptask_between*',
        'pclosurecall_between.PACKS = [pconfigpack_first]',
        'pclosurecall_between.RAW = [(KSTRING $ptascii("x"),KNOWN (PINT 17))]',
        'pclosurecall_between.SENT = {SLOTS ([(NAMED_SENT (KNOWN (PINT 17)))]),NAMED eps}',
        'pclosurecall_between.ERROR = eps',
        '~(HARRAY n_named_pack <- S_between.ALLOCATIONS)',
        'S_between.STORE[n_namedCell_cv] = DEFINED (PINT 17)',
        'S_between.STORE[n_positionalCell_cv] = DEFINED (PINT 23)',
        '$test_outputs(S_between.EVENTS) = ' + term(first),*budget('S_between'),
        *reach('S_second','S_between',3),
        'S_second.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_second (KNOWN (PARRAY n_positional_pack)) 0) :: ptask_second*',
        'pclosurecall_second.PACKS = [pconfigpack_first,pconfigpack_second]',
        'pconfigpack_second.INDEX = 2','pconfigpack_second.ARRAY = n_positional_pack',
        'pconfigpack_second.ITEMS = [ENTRY (KINT 9) (DIRECT (PINT 31))]',
        'pclosurecall_second.RAW = pclosurecall_between.RAW',
        'pclosurecall_second.SENT = pclosurecall_between.SENT','pclosurecall_second.ERROR = eps',
        '$closure_call_pack_named(pclosurecall_second.RAW)',
        'S_second.STORE[n_namedCell_cv] = DEFINED (PINT 29)',
        'S_second.STORE[n_positionalCell_cv] = DEFINED (PINT 31)',
        'S_second.STORE[n_call_cv] = DEFINED PNULL','S_second.STORE[n_receiver_cv] = DEFINED PNULL',
        'S_second.STORE[n_namedPack_cv] = DEFINED PNULL','S_second.STORE[n_positionalPack_cv] = DEFINED PNULL',
        '~(HARRAY n_named_pack <- S_second.ALLOCATIONS)',
        '(HARRAY n_positional_pack) <- S_second.ALLOCATIONS',
        'S_second.ARRAYS[n_named_pack].ITEMS = [ENTRY (KSTRING $ptascii("x")) (ALIAS n_namedCell_cv)]',
        '$test_outputs(S_second.EVENTS) = ' + term(before_warning),*budget('S_second'),
        *reach('S_sent','S_second',4),
        'S_sent.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_sent (KNOWN (PARRAY n_positional_pack)) 1) :: ptask_sent*',
        'pclosurecall_sent.RAW = [(KINT 1,KNOWN (PINT 31)),(KSTRING $ptascii("x"),KNOWN (PINT 17))]',
        'pclosurecall_sent.SENT = {SLOTS eps,NAMED eps}',
        'pclosurecall_sent.ERROR = (' + text(duplicate.decode()) + ')',
        *reach('S_forward_pending','S_sent',5),*settle('S_forward','S_forward_pending'),
        'S_forward.TODO = (CLOSURE_CALL_FORWARD pclosurecall 0 pnamedargs_empty n_base) :: ptask_forward*',
        'pclosurecall.SOURCE = n_source','pclosurecall.RECEIVER = (n_receiver)',
        'pclosurecall.INDEX = 3','pclosurecall.PACKS = [pconfigpack_first,pconfigpack_second]',
        'pclosurecall.RAW = pclosurecall_sent.RAW','pclosurecall.SENT = pclosurecall_sent.SENT',
        'pclosurecall.ERROR = pclosurecall_sent.ERROR','pnamedargs_empty = {SLOTS eps,NAMED eps}',
        'n_base = |S_forward.STORE|',
        '~(HARRAY n_named_pack <- S_forward.ALLOCATIONS)',
        '~(HARRAY n_positional_pack <- S_forward.ALLOCATIONS)',
        'S_forward.STORE[n_warnings_cv] = DEFINED (PINT 0)',
        'S_forward.STORE[n_bodies_cv] = DEFINED (PINT 0)',
        'S_forward.STORE[n_result_cv] = DEFINED (PINT 97)',*budget('S_forward')]
    # History/shape projections are checked, never driven as source states.
    for change in ['.PACKS = eps','.PACKS = [pconfigpack_first]',
            '.PACKS = [pconfigpack_second,pconfigpack_first]',
            '.PACKS = [pconfigpack_first,pconfigpack_second,pconfigpack_second]',
            '.INDEX = 2','.LINE = $(pclosurecall.LINE + 1)',
            '.RAW = [(KSTRING $ptascii("x"),KNOWN (PINT 17)),(KINT 1,KNOWN (PINT 31))]',
            '.RAW = [(KINT 9,KNOWN (PINT 31)),(KSTRING $ptascii("x"),KNOWN (PINT 17))]',
            '.ERROR = eps','.FIRST = eps','.RECEIVER = eps']:
        values += [f'~$call_task_valid(S_forward,CLOSURE_CALL_FORWARD pclosurecall[{change}] 0 pnamedargs_empty n_base)']
    for change in ['.INDEX = 1','.ARRAY = |S_forward.ARRAYS|','.SITE = PORIGIN 0 eps',
            '.LINE = $(pconfigpack_second.LINE + 1)',
            '.ITEMS = [ENTRY (KINT 9) (ALIAS n_positionalCell_cv)]']:
        values += [f'~$call_task_valid(S_forward,CLOSURE_CALL_FORWARD pclosurecall[.PACKS = [pconfigpack_first,pconfigpack_second[{change}]]] 0 pnamedargs_empty n_base)']
    values += [
        'S_history = S_forward[.ARRAYS[n_named_pack].ITEMS = [ENTRY (KSTRING $ptascii("x")) (DIRECT (PINT 88))]][.ARRAYS[n_positional_pack].ITEMS = [ENTRY (KINT 9) (DIRECT (PINT 99))]]',
        '$call_task_valid(S_history,CLOSURE_CALL_FORWARD pclosurecall 0 pnamedargs_empty n_base)',
        *reach('S_prepared','S_forward',6),
        'S_prepared.TODO = (CLOSURE_CALL_FORWARD pclosurecall 1 pnamedargs_prepared n_base) :: ptask_prepared*',
        'pnamedargs_prepared.SLOTS = [NAMED_SENT (REFERENCE n_temp)]','pnamedargs_prepared.NAMED = eps',
        'S_prepared.STORE[n_temp] = DEFINED (PINT 31)',
        'S_prepared.STORE[n_namedCell_cv] = DEFINED (PINT 47)',
        'S_prepared.STORE[n_positionalCell_cv] = DEFINED (PINT 53)',
        '$(n_temp >= n_base)','n_temp =/= n_namedCell_cv','n_temp =/= n_positionalCell_cv',
        '$call_reference_operand_valid(S_prepared,REFERENCE n_temp)',
        'S_prepared.STORE[n_warnings_cv] = DEFINED (PINT 1)',
        'S_prepared.STORE[n_bodies_cv] = DEFINED (PINT 0)',
        'S_prepared.STORE[n_result_cv] = DEFINED (PINT 97)',
        '$test_outputs(S_prepared.EVENTS) = ' + term(after_warning),
        'S_same_value = S_prepared[.STORE[n_positionalCell_cv] = DEFINED (PINT 31)]',
        'pnamedargs_bad = pnamedargs_prepared[.SLOTS = [NAMED_SENT (REFERENCE n_positionalCell_cv)]]',
        '~$call_task_valid(S_same_value,CLOSURE_CALL_FORWARD pclosurecall 1 pnamedargs_bad n_base)',
        *budget('S_prepared'),
        *reach('S_error_pending','S_prepared',7),*settle('S_error','S_error_pending'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_error*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable','pthrowable.KIND = "Error"',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text(duplicate.decode()) + ')',
        '$throwable_field(S_error,n_error,"line") = PINT 56',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]',
        '$entry_lookup(S_error.ARRAYS[n_frame].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args))',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)),ENTRY (KINT 1) (DIRECT (PINT 31)),ENTRY (KSTRING $ptascii("x")) (DIRECT (PINT 17))]',
        '~(HOBJECT n_source <- S_error.ALLOCATIONS)','~(HCELL n_temp <- S_error.ALLOCATIONS)',
        '(HOBJECT n_receiver) <- S_error.ALLOCATIONS',
        'S_error.STORE[n_bodies_cv] = DEFINED (PINT 0)',
        'S_error.STORE[n_result_cv] = DEFINED (PINT 97)',
        *reach('S_caught','S_error',8),
        '$lookup(S_caught.ENV,$ptascii("raw")) = (n_raw_cv)',
        'S_caught.STORE[n_raw_cv] = DEFINED (PARRAY n_args)',
        '$test_outputs(S_caught.EVENTS) = ' + term(caught),
        *reach('S_raw_pending','S_caught',9),*settle('S_raw','S_raw_pending'),
        'S_raw.STORE[n_raw_cv] = DEFINED (PARRAY n_args)',
        '~(HCELL n_namedCell_cv <- S_raw.ALLOCATIONS)',
        '~(HCELL n_positionalCell_cv <- S_raw.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_raw.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_raw.ALLOCATIONS)','~(HARRAY n_frame <- S_raw.ALLOCATIONS)',
        '(HARRAY n_args) <- S_raw.ALLOCATIONS',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_receiver) = 1',
        '$test_outputs(S_raw.EVENTS) = ' + term(caught + b'posKept|namedKept|rawHeld|'),
        *define.finish('S_raw',stdout)]
    for node in ['HOBJECT n_source','HOBJECT n_receiver','HOBJECT n_weak_call','HOBJECT n_weak_receiver',
            'HARRAY n_named_pack','HARRAY n_positional_pack','HCELL n_namedCell_cv','HCELL n_positionalCell_cv',
            'HCELL n_temp','HOBJECT n_error','HARRAY n_trace','HARRAY n_frame','HARRAY n_args']:
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
