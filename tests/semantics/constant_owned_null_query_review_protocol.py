#!/usr/bin/env python3
"""Real NULL warning callback cancellation, raw traces and owner retirement."""
from pathlib import Path

import define_stdclass_array_duplicate_review_protocol as prior
import typed_static_invoke_set_protocol as process_base
import constant_owned_null_query_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
CASE = sources.CASE
PREFIX = common.PREFIX + r'''
dec $test_owned_null_peer_front(pstate, nat) : bool
def $test_owned_null_peer_front(S,0) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.INDEX = 0 /\ $config_method_receiver(S,pconfigcall)
def $test_owned_null_peer_front(S,1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL)]
def $test_owned_null_peer_front(S,2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_NULL_CONSTANT_RESULT pconfigcall
  -- if pconfigcall.OWNER =/= eps
def $test_owned_null_peer_front(S,3) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_NULL_CONSTANT_RESULT pconfigcall
  -- if pconfigcall.OWNER =/= eps
def $test_owned_null_peer_front(S,4) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.INDEX = 0 /\ ~$config_method_receiver(S,pconfigcall)
def $test_owned_null_peer_front(S,5) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.OWNER =/= eps
  -- if ~$config_method_receiver(S,pconfigcall)
def $test_owned_null_peer_front(S,n_phase) = false -- otherwise
dec $test_owned_null_peer_seek(pstate, nat, nat) : pstate
def $test_owned_null_peer_seek(S,n_phase,0) = S
def $test_owned_null_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_owned_null_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_owned_null_peer_seek(S,n_phase,n) = $test_owned_null_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_owned_null_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_owned_null_peer_seek({start},{phase},2500)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_owned_null_peer_front({state},{phase})', *common.public(state)]


def controls():
    # Invalid authority/shape projections are never driven.
    values = ['S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_a)]',
        '~$dynamic_null_constant_valid(S_dead,pconfigcall)',
        'S_wrong = S[.OBJECTS[n_a] = INTRINSICCLOSURE INTRINSIC_DEFINED]',
        '~$dynamic_null_constant_valid(S_wrong,pconfigcall)',
        '~$dynamic_null_constant_call(pconfigcall)']
    for change in ['.OWNER = eps', '.OWNER = (|S.OBJECTS|)', '.SELECTION = (0)',
            '.KIND = INTRINSIC_DEFINE', '.KIND = INTRINSIC_DEFINED', '.INDEX = 0',
            '.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall.LINE + 1)', '.NAMED = false']:
        values += [f'~$dynamic_null_constant_valid(S,pconfigcall[{change}])']
    for value in ['PBOOL false','PINT 0','PFLOAT 0','PSTRING ($ptascii(""))','PARRAY 0','POBJECT 0']:
        values += [f'~$dynamic_owned_null_query_call(pconfigcall[.SENT = [NAMED_SENT (KNOWN ({value}))]])',
            f'~$dynamic_null_constant_valid(S,pconfigcall[.SENT = [NAMED_SENT (KNOWN ({value}))]])']
    values += ['pconfigpack_bad = {INDEX 0,SITE pconfigcall.SITE,LINE pconfigcall.LINE,ARRAY 0,ITEMS eps}',
        '~$dynamic_owned_null_query_call(pconfigcall[.PACKS = [pconfigpack_bad]])',
        '~$dynamic_owned_null_query_call(pconfigcall[.SENT = eps])',
        '~$dynamic_owned_null_query_call(pconfigcall[.SENT = pconfigcall.SENT ++ pconfigcall.SENT])']
    return values


def checks(initial, stdout):
    begin = b'B|'
    before = begin + b'N|held|'
    callback = before + (b'H|8192|constant(): Passing null to parameter #1 ($name) of type string is deprecated|42|file|held|')
    caught = callback + (b'E|same|none|V101_STOP|22|v101ReviewStop|constant|__invoke|level|rawN|rawsame|'
        b'97|1|1|V101_HANDLER|null|gone|')
    reading = caught + b'R|held|'
    assert stdout == reading + b'23|null|gone|keptN|A|'
    values = [*initial, 'S_initial.COMPLETION = BUDGET', *reach('S_capture','S_initial',0),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        'pconfigcall_capture.OWNER = (n_a)', 'pconfigcall_capture.SELECTION = eps',
        'pconfigcall_capture.PACKS = eps', 'pconfigcall_capture.SENT = eps',
        'S_capture.OBJECTS[n_a] = INTRINSICCLOSURE INTRINSIC_CONSTANT',
        '$config_selected_valid(S_capture,pconfigcall_capture)',
        '$config_nodes(pconfigcall_capture) = [HOBJECT n_a]',
        '$lookup(S_capture.ENV,$ptascii("call")) = (n_call)',
        '$lookup(S_capture.ENV,$ptascii("name")) = (n_name)',
        '$lookup(S_capture.ENV,$ptascii("arguments")) = (n_arguments)',
        '$lookup(S_capture.ENV,$ptascii("calls")) = (n_calls)',
        '$lookup(S_capture.ENV,$ptascii("held")) = (n_held)',
        '$lookup(S_capture.ENV,$ptascii("result")) = (n_result)',
        '$lookup(S_capture.ENV,$ptascii("weak")) = (n_weak_a_cv)',
        'S_capture.STORE[n_call] = DEFINED (POBJECT n_a)',
        'S_capture.STORE[n_name] = DEFINED PNULL',
        'S_capture.STORE[n_weak_a_cv] = DEFINED (POBJECT n_weak_a)',
        'S_capture.OBJECTS[n_weak_a] = WEAKREFERENCE (n_a)',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_a) = 2',
        'S_capture.USERCONSTANTS = eps', 'S_capture.SELECTEDCALLS = eps',
        'S_capture.SELECTSEQ = 0', '$test_outputs(S_capture.EVENTS) = ' + term(begin),
        *reach('S','S_capture',1),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_call*',
        'pconfigcall.OWNER = (n_a)', 'pconfigcall.SELECTION = eps',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL)]',
        'pconfigcall.NAMED', 'pconfigcall.PACKS = eps', 'pconfigcall.INDEX = 1',
        'pconfigcall.LINE = 42', '$config_invoke_valid(S,pconfigcall)',
        '$dynamic_owned_null_query_call(pconfigcall)', '$dynamic_null_constant_valid(S,pconfigcall)',
        '$exit_strict(S,pconfigcall.SITE)', '~$config_strict(S,pconfigcall)',
        '$call_task_valid(S,DYNAMIC_NULL_CONSTANT_RESULT pconfigcall)',
        '$task_nodes(DYNAMIC_NULL_CONSTANT_RESULT pconfigcall) = [HOBJECT n_a]',
        'S.STORE[n_call] = DEFINED pvalue_current_call',
        '$string_bytes(pvalue_current_call) = ($ptascii("defined"))',
        'S.STORE[n_name] = DEFINED pvalue_argument_name',
        '$string_bytes(pvalue_argument_name) = ($ptascii("V101_ARGUMENT"))',
        'S.STORE[n_arguments] = DEFINED (PINT 1)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        'S.STORE[n_result] = DEFINED (PINT 97)', 'S.STORE[n_held] = DEFINED PNULL',
        '$weakref_get(S,n_weak_a) = POBJECT n_a',
        '$heap_owners($heap_graph(S),HOBJECT n_a) = 1',
        'S.USERCONSTANTS = eps', 'S.SELECTEDCALLS = eps', 'S.SELECTSEQ = 0',
        '~$destructor_operational(S)', '$test_outputs(S.EVENTS) = ' + term(before),
        *controls(),
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        '$test_running(S_pause) = S',
        *common.step('S_warning','S'), *common.public('S_warning'),
        '$drive_steps($test_running(S_pause),1) = S_warning_found',
        'S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_call*',
        'perrorcall.RESUME = DYNAMIC_NULL_CONSTANT_RESULT pconfigcall',
        'perrorcall.SITE = pconfigcall.SITE', 'perrorcall.LINE = pconfigcall.LINE',
        'perrorcall.LEVEL = 8192', 'perrorcall.MESSAGE = $dynamic_null_constant_message(pconfigcall)',
        'perrorcall.EVENT = DIAGNOSTIC "Deprecated" perrorcall.MESSAGE pconfigcall.LINE',
        '$error_call_valid(S_warning,perrorcall)',
        '$task_nodes(ERROR_HANDLER_INVOKE perrorcall) = [HOBJECT n_a]',
        '$heap_owners($heap_graph(S_warning),HOBJECT n_a) = 1',
        'S_warning.USERCONSTANTS = S.USERCONSTANTS', 'S_warning.EVENTS = S.EVENTS',
        'S_warning.STORE = S.STORE', 'S_warning.STRINGDATA = S.STRINGDATA',
        *reach('S_handler','S_warning',2),
        'S_handler.CURRENT = (pcallcontext_handler)',
        '$error_context_call(S_handler,pcallcontext_handler) = (perrorcall_handler)',
        'perrorcall_handler.RESUME = DYNAMIC_NULL_CONSTANT_RESULT pconfigcall',
        '$error_context_valid(S_handler,pcallcontext_handler)',
        '$error_context_trigger(S_handler,pcallcontext_handler) = (pconfigcall)',
        '$error_handler_trace_values(S_handler,pcallcontext_handler,pconfigcall) = [PNULL]',
        '$heap_owners($heap_graph(S_handler),HOBJECT n_a) = 1',
        *reach('S_throw','S_handler',3),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_throw*',
        'perrorcall_throw.RESUME = DYNAMIC_NULL_CONSTANT_RESULT pconfigcall',
        '$call_task_valid(S_throw,DYNAMIC_NULL_CONSTANT_RESULT pconfigcall)',
        'S_throw.STORE[n_held] = DEFINED (POBJECT n_error)',
        'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
        'S_throw.STORE[n_arguments] = DEFINED (PINT 1)',
        'S_throw.STORE[n_call] = DEFINED PNULL',
        'S_throw.STORE[n_name] = DEFINED pvalue_handler_name',
        '$string_bytes(pvalue_handler_name) = ($ptascii("V101_HANDLER"))',
        'S_throw.STORE[n_result] = DEFINED (PINT 97)',
        'S_throw.OBJECTS[n_error] = THROWABLE pthrowable',
        'pthrowable.KIND = "Exception"', '$throwable_chain_valid(S_throw,n_error)',
        '$string_bytes($throwable_field(S_throw,n_error,"message")) = ($ptascii("V101_STOP"))',
        '$throwable_field(S_throw,n_error,"previous") = PNULL',
        '$throwable_field(S_throw,n_error,"line") = PINT 22',
        '$throwable_field(S_throw,n_error,"trace") = PARRAY n_trace',
        'S_throw.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_handler_frame)),ENTRY (KINT 1) (DIRECT (PARRAY n_api_frame)),ENTRY (KINT 2) (DIRECT (PARRAY n_invoke_frame))]',
        '$trace_array_field(S_throw,n_handler_frame,$ptascii("function")) = PSTRING ($ptascii("v101ReviewStop"))',
        '$trace_array_field(S_throw,n_api_frame,$ptascii("function")) = PSTRING ($ptascii("constant"))',
        '$trace_array_field(S_throw,n_invoke_frame,$ptascii("function")) = PSTRING ($ptascii("__invoke"))',
        '$trace_array_field(S_throw,n_handler_frame,$ptascii("args")) = PARRAY n_handler_args',
        '$entry_lookup(S_throw.ARRAYS[n_handler_args].ITEMS,KINT 0) = (DIRECT (PINT 8192))',
        '$trace_array_field(S_throw,n_api_frame,$ptascii("args")) = PARRAY n_api_args',
        '$trace_array_field(S_throw,n_invoke_frame,$ptascii("args")) = PARRAY n_invoke_args',
        'S_throw.ARRAYS[n_api_args].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL)]',
        'S_throw.ARRAYS[n_invoke_args].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL)]',
        '$strict_check(S_throw,PARRAY n_api_args,PARRAY n_invoke_args,eps) = COMPARED true',
        'S_throw.USERCONSTANTS = [puserconstant]',
        'puserconstant.NAME = eps', 'puserconstant.VALUE = PINT 23', 'puserconstant.CLASS = PVSCALAR',
        '$dynamic_define_source(S_throw,puserconstant.ORIGIN)',
        '$weakref_get(S_throw,n_weak_a) = POBJECT n_a',
        '$heap_owners($heap_graph(S_throw),HOBJECT n_a) = 1',
        '$test_outputs(S_throw.EVENTS) = ' + term(callback),
        'S_throw_pause = $drive_steps(S_throw,0)',
        'S_throw_pause = S_throw[.COMPLETION = BUDGET]',
        '$test_running(S_throw_pause) = S_throw',
        *common.step('S_cancel','S_throw'), *common.public('S_cancel'),
        '$drive_steps($test_running(S_throw_pause),1) = S_cancel_found',
        'S_cancel.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
        'S_cancel.RESULT = KNOWN PNULL', 'S_cancel.USERCONSTANTS = S_throw.USERCONSTANTS',
        'S_cancel.EVENTS = S_throw.EVENTS', 'S_cancel.STORE = S_throw.STORE',
        '~(HOBJECT n_a <- S_cancel.ALLOCATIONS)', '$weakref_get(S_cancel,n_weak_a) = PNULL',
        '$heap_owners($heap_graph(S_cancel),HOBJECT n_a) = 0',
        '$throwable_field(S_cancel,n_error,"trace") = PARRAY n_trace',
        'S_cancel.ARRAYS[n_api_args] = S_throw.ARRAYS[n_api_args]',
        'S_cancel.ARRAYS[n_invoke_args] = S_throw.ARRAYS[n_invoke_args]',
        *reach('S_recovery','S_cancel',4),
        'S_recovery.TODO = (CONFIG_ARGS pconfigcall_recovery) :: ptask_recovery*',
        'pconfigcall_recovery.OWNER = (n_b)', 'n_b =/= n_a',
        'pconfigcall_recovery.SELECTION = eps', 'pconfigcall_recovery.SENT = eps',
        'S_recovery.OBJECTS[n_b] = INTRINSICCLOSURE INTRINSIC_CONSTANT',
        '$lookup(S_recovery.ENV,$ptascii("weakRead")) = (n_weak_b_cv)',
        'S_recovery.STORE[n_weak_b_cv] = DEFINED (POBJECT n_weak_b)',
        'S_recovery.OBJECTS[n_weak_b] = WEAKREFERENCE (n_b)',
        '$heap_owners($heap_graph(S_recovery),HOBJECT n_b) = 2',
        'S_recovery.USERCONSTANTS = S_throw.USERCONSTANTS',
        '$test_outputs(S_recovery.EVENTS) = ' + term(caught),
        *reach('S_read','S_recovery',5),
        'S_read.TODO = (CONFIG_INVOKE pconfigcall_read) :: ptask_read*',
        'pconfigcall_read.OWNER = (n_b)', 'pconfigcall_read.SELECTION = eps',
        'pconfigcall_read.SENT = [NAMED_SENT (KNOWN pvalue_read)]',
        '$string_bytes(pvalue_read) = (eps)',
        '$dynamic_owned_global_query_valid(S_read,pconfigcall_read)',
        '~$dynamic_null_constant_valid(S_read,pconfigcall_read)',
        'S_read.STORE[n_call] = DEFINED PNULL',
        '$weakref_get(S_read,n_weak_b) = POBJECT n_b',
        '$heap_owners($heap_graph(S_read),HOBJECT n_b) = 1',
        '$entry_lookup(S_read.ARRAYS[n_api_args].ITEMS,KINT 0) = (DIRECT PNULL)',
        '$entry_lookup(S_read.ARRAYS[n_invoke_args].ITEMS,KINT 0) = (DIRECT PNULL)',
        '$test_outputs(S_read.EVENTS) = ' + term(reading),
        *common.step('S_value','S_read','PINT 23'),
        'S_value.TODO = ptask_read*', '~(HOBJECT n_b <- S_value.ALLOCATIONS)',
        '$weakref_get(S_value,n_weak_b) = PNULL',
        *define.finish('S_value',stdout),
        'S_final.USERCONSTANTS = S_throw.USERCONSTANTS',
        'S_final.SELECTEDCALLS = eps', 'S_final.SELECTSEQ = 0']
    for node in ['HOBJECT n_a','HOBJECT n_b','HOBJECT n_weak_a','HOBJECT n_weak_b',
            'HOBJECT n_error','HARRAY n_trace','HARRAY n_api_args','HARRAY n_invoke_args']:
        values += [f'~({node} <- S_final.ALLOCATIONS)']
    return values


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = process_base.process


def process(command, directory, timeout, cwd):
    if directory.parent.name == CASE:
        timeout = 420
    return packet_process(command, directory, timeout, cwd)


packet.process = process
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    raise SystemExit(0 if packet.main() else 1)
