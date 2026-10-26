#!/usr/bin/env python3
"""Saved ARRAY delivery, named default holes and raw Closure::call Error roots."""
from pathlib import Path

import define_stdclass_array_duplicate_protocol as prior
import typed_static_invoke_set_protocol as process_base
import closure_call_array_pack_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
PREFIX = common.PREFIX + r'''
dec $test_closure_pack_front(pstate,nat) : bool
def $test_closure_pack_front(S,0) = true
  -- if S.TODO = (CLOSURE_CALL_ARGS pclosurecall) :: ptask_tail*
  -- if pclosurecall.INDEX = 0
def $test_closure_pack_front(S,1) = true
  -- if S.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall (KNOWN (PARRAY n_array)) 0) :: ptask_tail*
def $test_closure_pack_front(S,2) = true
  -- if S.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall (KNOWN (PARRAY n_array)) n_cursor) :: ptask_tail*
  -- if pclosurecall.PACKS = [pconfigpack]
  -- if n_cursor = |pconfigpack.ITEMS|
def $test_closure_pack_front(S,3) = true
  -- if S.TODO = (CLOSURE_CALL_INVOKE pclosurecall) :: ptask_tail*
def $test_closure_pack_front(S,4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_CALL_TARGET n_source n_receiver
  -- if $lookup(S.ENV,$ptascii("first")) = (n_first)
  -- if S.STORE[n_first] = DEFINED (PINT 7)
  -- if $lookup(S.ENV,$ptascii("second")) = (n_second)
  -- if S.STORE[n_second] = DEFINED pvalue_second
  -- if $string_plain(pvalue_second) = PSTRING $ptascii("5")
def $test_closure_pack_front(S,5) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_CALL_TARGET n_source n_receiver
  -- if $lookup(S.ENV,$ptascii("first")) = (n_first)
  -- if S.STORE[n_first] = DEFINED (PINT 17)
  -- if $lookup(S.ENV,$ptascii("second")) = (n_second)
  -- if S.STORE[n_second] = DEFINED (PINT 29)
def $test_closure_pack_front(S,6) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask_tail*
def $test_closure_pack_front(S,7) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_name) metadata_name) :: expression_tail*
  -- if $base64(text_name) = $ptascii("error")
def $test_closure_pack_front(S,8) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_name) metadata_name) :: expression_tail*
  -- if $base64(text_name) = $ptascii("raw")
def $test_closure_pack_front(S,n_phase) = false -- otherwise
dec $test_closure_pack_seek(pstate,nat,nat) : pstate
def $test_closure_pack_seek(S,n_phase,0) = S
def $test_closure_pack_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_closure_pack_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_closure_pack_seek(S,n_phase,n) = $test_closure_pack_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_closure_pack_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $test_closure_pack_settled(pstate) : bool
def $test_closure_pack_settled(S) = (S.DESTRUCTION.RELEASES = eps /\ S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.CALLS = eps)
dec $test_closure_pack_user_entry(pstate) : bool
def $test_closure_pack_user_entry(S) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
def $test_closure_pack_user_entry(S) = false -- otherwise
dec $test_closure_pack_settle(pstate,nat) : pstate
def $test_closure_pack_settle(S,0) = S
def $test_closure_pack_settle(S,n) = S
  -- if $(n > 0)
  -- if $test_closure_pack_settled(S) \/ $test_closure_pack_user_entry(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_closure_pack_settle(S,n) = $test_closure_pack_settle($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_closure_pack_settled(S) /\ ~$test_closure_pack_user_entry(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_closure_pack_seek({start},{phase},3000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_closure_pack_front({state},{phase})', *common.public(state)]


def settle(state, start):
    return [f'{state}_found = $test_closure_pack_settle({start},80)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_closure_pack_settled({state})', *common.public(state)]


def budget(state):
    return [f'{state}_pause = $drive_steps({state},0)',
        f'{state}_pause = {state}[.COMPLETION = BUDGET]',
        f'$test_running({state}_pause) = {state}',
        f'$drive_steps({state},1) = $drive_steps($test_running({state}_pause),1)']


def capture(initial):
    return [*initial, *reach('S_capture','S_initial',0),
        'S_capture.TODO = (CLOSURE_CALL_ARGS pclosurecall_capture) :: ptask_capture*',
        'n_source = pclosurecall_capture.SOURCE',
        'pclosurecall_capture.PACKS = eps', 'pclosurecall_capture.INDEX = 0',
        '$closure_call_array_pack_site(S_capture,pclosurecall_capture.SITE)',
        *[f'$lookup(S_capture.ENV,{text(name)}) = (n_{name}_cv)' for name in
            ['call','receiver','pack','effects','bodies','result','weakCall','weakReceiver']],
        'S_capture.STORE[n_call_cv] = DEFINED (POBJECT n_source)',
        'S_capture.STORE[n_receiver_cv] = DEFINED (POBJECT n_receiver)',
        'S_capture.STORE[n_pack_cv] = DEFINED (PARRAY n_pack)',
        'S_capture.STORE[n_weakCall_cv] = DEFINED (POBJECT n_weak_call)',
        'S_capture.STORE[n_weakReceiver_cv] = DEFINED (POBJECT n_weak_receiver)',
        'S_capture.STORE[n_effects_cv] = DEFINED (PINT 0)',
        'S_capture.STORE[n_bodies_cv] = DEFINED (PINT 0)',
        'S_capture.STORE[n_result_cv] = DEFINED (PINT 97)',
        '$test_outputs(S_capture.EVENTS) = ' + term(b'B|'),
        *reach('S_unpack','S_capture',1),
        'S_unpack.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_unpack (KNOWN (PARRAY n_pack)) 0) :: ptask_unpack*',
        'pclosurecall_unpack.SOURCE = n_source',
        'pclosurecall_unpack.FIRST = (POBJECT n_receiver)',
        'pclosurecall_unpack.RECEIVER = (n_receiver)',
        'pclosurecall_unpack.PACKS = [pconfigpack]',
        'pconfigpack.ARRAY = n_pack', 'pconfigpack.INDEX = 1',
        'pconfigpack.LINE = pclosurecall_unpack.LINE',
        'pclosurecall_unpack.RAW = eps',
        'pclosurecall_unpack.SENT = {SLOTS eps, NAMED eps}',
        '$closure_call_pack_source_valid(S_unpack,pclosurecall_unpack,pconfigpack)',
        '$closure_call_unpack_valid(S_unpack,pclosurecall_unpack,KNOWN (PARRAY n_pack),0)',
        '(HARRAY n_pack) <- S_unpack.ALLOCATIONS',
        '(HARRAY n_pack) <- $task_nodes(CLOSURE_CALL_UNPACK_NEXT pclosurecall_unpack (KNOWN (PARRAY n_pack)) 0)',
        'S_unpack.STORE[n_effects_cv] = DEFINED (PINT 1)',
        'S_unpack.STORE[n_bodies_cv] = DEFINED (PINT 0)',
        'S_unpack.STORE[n_result_cv] = DEFINED (PINT 97)',
        '$test_outputs(S_unpack.EVENTS) = ' + term(b'B|P|callHeld|receiverHeld|'),
        *budget('S_unpack')]


def refusals(state, record, pack, count):
    values = []
    for change in ['.PACKS = eps','.INDEX = 1','.SOURCE = |' + state + '.OBJECTS|',
            '.LINE = $(' + record + '.LINE + 1)','.FIRST = eps','.RECEIVER = eps',
            '.ERROR = ($ptascii("forged"))']:
        values += [f'~$call_task_valid({state},CLOSURE_CALL_INVOKE {record}[{change}])']
    for change in ['.INDEX = 0','.ARRAY = |' + state + '.ARRAYS|',
            '.LINE = $(' + pack + '.LINE + 1)','.SITE = PORIGIN 0 eps']:
        values += [f'~$call_task_valid({state},CLOSURE_CALL_INVOKE {record}[.PACKS = [{pack}[{change}]]])']
    values += [f'~$closure_call_pack_replay({state},{record},{count + 1})']
    return values


def positional(initial, stdout):
    assert stdout == b'B|P|callHeld|receiverHeld|F|17|int|string|callHeld|receiverHeld|R|17|1|1|99|currentNull|callGone|receiverGone|A|'
    values = [*capture(initial),
        'pconfigpack.ITEMS = [ENTRY (KINT 4) (DIRECT pvalue_first),ENTRY (KINT 9) (DIRECT (PINT 5))]',
        '$string_plain(pvalue_first) = PSTRING $ptascii("7")',
        'S_unpack.ARRAYS[n_pack].ITEMS = pconfigpack.ITEMS',
        'S_unpack.STORE[n_pack_cv] = DEFINED (PARRAY n_current)', 'n_current =/= n_pack',
        '$entry_lookup(S_unpack.ARRAYS[n_current].ITEMS,KINT 4) = (DIRECT pvalue_current)',
        '$string_plain(pvalue_current) = PSTRING $ptascii("99")',
        'S_unpack.STORE[n_call_cv] = DEFINED PNULL',
        'S_unpack.STORE[n_receiver_cv] = DEFINED PNULL',
        *reach('S_sent','S_unpack',2),
        'S_sent.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_sent (KNOWN (PARRAY n_pack)) 2) :: ptask_sent*',
        'pclosurecall_sent.RAW = [(KINT 1,KNOWN pvalue_first),(KINT 2,KNOWN (PINT 5))]',
        'pclosurecall_sent.SENT = {SLOTS [NAMED_SENT (KNOWN pvalue_first),NAMED_SENT (KNOWN (PINT 5))],NAMED eps}',
        'pclosurecall_sent.ERROR = eps',
        *reach('S_invoke_pending','S_sent',3), *settle('S_invoke','S_invoke_pending'),
        'S_invoke.TODO = (CLOSURE_CALL_INVOKE pclosurecall) :: ptask_invoke*',
        'pclosurecall.INDEX = 2', 'pclosurecall.PACKS = [pconfigpack]',
        'pclosurecall.RAW = pclosurecall_sent.RAW', 'pclosurecall.SENT = pclosurecall_sent.SENT',
        '~(HARRAY n_pack <- S_invoke.ALLOCATIONS)',
        '~(HARRAY n_pack <- $task_nodes(CLOSURE_CALL_INVOKE pclosurecall))',
        '(HOBJECT n_source) <- S_invoke.ALLOCATIONS',
        '(HOBJECT n_receiver) <- S_invoke.ALLOCATIONS',
        '$closure_call_pack_replay(S_invoke,pclosurecall,2)',
        *refusals('S_invoke','pclosurecall','pconfigpack',2),
        'S_history = S_invoke[.ARRAYS[n_pack].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 99)),ENTRY (KINT 9) (DIRECT (PINT 5))]]',
        '$call_task_valid(S_history,CLOSURE_CALL_INVOKE pclosurecall)',
        *budget('S_invoke'),
        *reach('S_body','S_invoke',4),
        'S_body.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = CLOSURE_CALL_TARGET n_source n_receiver',
        'pcallcontext.ARGC = 2', 'pcallcontext.HOLES = eps', 'pcallcontext.NAMED = eps',
        'pcallcontext.WRAPPER = (pnamedargs_wrapper)',
        'pnamedargs_wrapper = {SLOTS [NAMED_SENT (KNOWN pvalue_first),NAMED_SENT (KNOWN (PINT 5))],NAMED eps}',
        '$wrapper_context_valid(S_body,pcallcontext)',
        '~$wrapper_context_valid(S_body,pcallcontext[.ARGC = 1])',
        '~$wrapper_context_valid(S_body,pcallcontext[.WRAPPER = eps])',
        '$lookup(S_body.ENV,$ptascii("first")) = (n_first)',
        '$lookup(S_body.ENV,$ptascii("second")) = (n_second)',
        'S_body.STORE[n_first] = DEFINED (PINT 7)',
        'S_body.STORE[n_second] = DEFINED pvalue_second',
        '$string_plain(pvalue_second) = PSTRING $ptascii("5")',
        'S_body.STORE[n_bodies_cv] = DEFINED (PINT 0)',
        '$test_outputs(S_body.EVENTS) = ' + term(b'B|P|callHeld|receiverHeld|'),
        *reach('S_cleanup_pending','S_body',7), *settle('S_cleanup','S_cleanup_pending'),
        'S_cleanup.STORE[n_result_cv] = DEFINED (PINT 17)',
        'S_cleanup.STORE[n_effects_cv] = DEFINED (PINT 1)',
        'S_cleanup.STORE[n_bodies_cv] = DEFINED (PINT 1)',
        '~(HOBJECT n_source <- S_cleanup.ALLOCATIONS)',
        '~(HOBJECT n_receiver <- S_cleanup.ALLOCATIONS)',
        '~(HARRAY n_pack <- S_cleanup.ALLOCATIONS)',
        '(HARRAY n_current) <- S_cleanup.ALLOCATIONS',
        '$test_outputs(S_cleanup.EVENTS) = ' + term(stdout[:-2]),
        *define.finish('S_cleanup',stdout)]
    for node in ['HOBJECT n_source','HOBJECT n_receiver','HARRAY n_pack','HARRAY n_current',
            'HOBJECT n_weak_call','HOBJECT n_weak_receiver']:
        values += [f'~({node} <- S_final.ALLOCATIONS)']
    return values


def named(initial, stdout):
    first_output = b'B|P|callHeld|receiverHeld|F|23|17|29|R|46|1|1|99|'
    second_output = first_output + b'P|callHeld|receiverHeld|'
    caught_output = second_output + b'E|Unknown named parameter $unknown|38|none|call|Closure|->|file|38|rawReceiver|named31|end|currentNull|callGone|receiverHeld|97|2|1|'
    assert stdout == caught_output + b'rawHeld|released|23|A|'
    values = [*capture(initial),
        'pconfigpack.ITEMS = [ENTRY (KSTRING $ptascii("second")) (DIRECT (PINT 29))]',
        'S_unpack.ARRAYS[n_pack].ITEMS = pconfigpack.ITEMS',
        'S_unpack.STORE[n_pack_cv] = DEFINED (PARRAY n_current)', 'n_current =/= n_pack',
        'S_unpack.ARRAYS[n_current].ITEMS = [ENTRY (KSTRING $ptascii("second")) (DIRECT (PINT 99))]',
        *reach('S_sent','S_unpack',2),
        'S_sent.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_sent (KNOWN (PARRAY n_pack)) 1) :: ptask_sent*',
        'pclosurecall_sent.RAW = [(KSTRING $ptascii("second"),KNOWN (PINT 29))]',
        'pclosurecall_sent.SENT = {SLOTS [NAMED_HOLE,NAMED_SENT (KNOWN (PINT 29))],NAMED eps}',
        'pclosurecall_sent.ERROR = eps',
        *reach('S_invoke_pending','S_sent',3), *settle('S_invoke','S_invoke_pending'),
        'S_invoke.TODO = (CLOSURE_CALL_INVOKE pclosurecall) :: ptask_invoke*',
        'pclosurecall.PACKS = [pconfigpack]',
        '$closure_call_pack_named(pclosurecall.RAW)',
        '~(HARRAY n_pack <- S_invoke.ALLOCATIONS)',
        *refusals('S_invoke','pclosurecall','pconfigpack',1),
        *budget('S_invoke'),
        *reach('S_body','S_invoke',5),
        'S_body.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = CLOSURE_CALL_TARGET n_source n_receiver',
        'pcallcontext.ARGC = 2', 'pcallcontext.HOLES = [0]', 'pcallcontext.NAMED = eps',
        'pcallcontext.WRAPPER = (pnamedargs_wrapper)',
        'pnamedargs_wrapper = {SLOTS eps,NAMED [($ptascii("second"),KNOWN (PINT 29))]}',
        '$wrapper_context_valid(S_body,pcallcontext)',
        '~$wrapper_context_valid(S_body,pcallcontext[.HOLES = eps])',
        '~$wrapper_context_valid(S_body,pcallcontext[.WRAPPER = (pnamedargs_wrapper[.NAMED = [($ptascii("first"),KNOWN (PINT 29))]])])',
        'S_body.STORE[n_bodies_cv] = DEFINED (PINT 0)',
        *reach('S_second_capture','S_body',0),
        'S_second_capture.TODO = (CLOSURE_CALL_ARGS pclosurecall_second) :: ptask_second*',
        'pclosurecall_second.SOURCE = n_source', 'pclosurecall_second.LINE = 38',
        'S_second_capture.STORE[n_effects_cv] = DEFINED (PINT 1)',
        'S_second_capture.STORE[n_bodies_cv] = DEFINED (PINT 1)',
        'S_second_capture.STORE[n_result_cv] = DEFINED (PINT 97)',
        '$test_outputs(S_second_capture.EVENTS) = ' + term(first_output),
        *reach('S_second_unpack','S_second_capture',1),
        'S_second_unpack.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_unknown (KNOWN (PARRAY n_unknown)) 0) :: ptask_unknown*',
        'pclosurecall_unknown.PACKS = [pconfigpack_unknown]',
        'pconfigpack_unknown.ITEMS = [ENTRY (KSTRING $ptascii("unknown")) (DIRECT (PINT 31))]',
        'S_second_unpack.STORE[n_call_cv] = DEFINED PNULL',
        'S_second_unpack.STORE[n_receiver_cv] = DEFINED PNULL',
        'S_second_unpack.STORE[n_pack_cv] = DEFINED PNULL',
        '$test_outputs(S_second_unpack.EVENTS) = ' + term(second_output),
        *reach('S_error_invoke_pending','S_second_unpack',3), *settle('S_error_invoke','S_error_invoke_pending'),
        'S_error_invoke.TODO = (CLOSURE_CALL_INVOKE pclosurecall_error) :: ptask_error*',
        'pclosurecall_error.SOURCE = n_source', 'pclosurecall_error.RECEIVER = (n_receiver)',
        'pclosurecall_error.RAW = [(KSTRING $ptascii("unknown"),KNOWN (PINT 31))]',
        'pclosurecall_error.SENT = {SLOTS eps,NAMED eps}',
        'pclosurecall_error.ERROR = ($ptascii("Unknown named parameter $unknown"))',
        '~(HARRAY n_unknown <- S_error_invoke.ALLOCATIONS)',
        '(HOBJECT n_source) <- S_error_invoke.ALLOCATIONS',
        '(HOBJECT n_receiver) <- S_error_invoke.ALLOCATIONS',
        *budget('S_error_invoke'),
        *reach('S_error_pending','S_error_invoke',6), *settle('S_error','S_error_pending'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Error"',
        '$throwable_field(S_error,n_error,"line") = PINT 38',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = ($ptascii("Unknown named parameter $unknown"))',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]',
        '$entry_lookup(S_error.ARRAYS[n_frame].ITEMS,KSTRING $ptascii("function")) = (DIRECT pvalue_function)',
        '$string_bytes(pvalue_function) = ($ptascii("call"))',
        '$entry_lookup(S_error.ARRAYS[n_frame].ITEMS,KSTRING $ptascii("line")) = (DIRECT (PINT 38))',
        '$entry_lookup(S_error.ARRAYS[n_frame].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args))',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)),ENTRY (KSTRING $ptascii("unknown")) (DIRECT (PINT 31))]',
        '~(HOBJECT n_source <- S_error.ALLOCATIONS)',
        '(HOBJECT n_receiver) <- S_error.ALLOCATIONS',
        'S_error.STORE[n_result_cv] = DEFINED (PINT 97)',
        'S_error.STORE[n_effects_cv] = DEFINED (PINT 2)',
        'S_error.STORE[n_bodies_cv] = DEFINED (PINT 1)',
        *reach('S_caught_pending','S_error',7), *settle('S_caught','S_caught_pending'),
        '$lookup(S_caught.ENV,$ptascii("raw")) = (n_raw_cv)',
        'S_caught.STORE[n_raw_cv] = DEFINED (PARRAY n_args)',
        '$test_outputs(S_caught.EVENTS) = ' + term(caught_output),
        *reach('S_raw_pending','S_caught',8), *settle('S_raw','S_raw_pending'),
        'S_raw.STORE[n_raw_cv] = DEFINED (PARRAY n_args)',
        '~(HOBJECT n_error <- S_raw.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_raw.ALLOCATIONS)',
        '~(HARRAY n_frame <- S_raw.ALLOCATIONS)',
        '(HARRAY n_args) <- S_raw.ALLOCATIONS',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_receiver) = 1',
        '$test_outputs(S_raw.EVENTS) = ' + term(caught_output + b'rawHeld|'),
        *define.finish('S_raw',stdout)]
    for node in ['HOBJECT n_source','HOBJECT n_receiver','HARRAY n_pack','HARRAY n_current',
            'HARRAY n_unknown','HOBJECT n_error','HARRAY n_trace','HARRAY n_frame','HARRAY n_args',
            'HOBJECT n_weak_call','HOBJECT n_weak_receiver']:
        values += [f'~({node} <- S_final.ALLOCATIONS)']
    return values


def checks(initial, name, stdout):
    return (positional if name == sources.POSITIONAL else named)(initial,stdout)


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = process_base.process


def process(command, directory, timeout, cwd):
    if directory.parent.name in sources.family.CASES:
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
