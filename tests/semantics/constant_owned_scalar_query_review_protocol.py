#!/usr/bin/env python3
"""Reached strict/raw and weak/API scalar query traces with independent recovery."""
from pathlib import Path

import define_stdclass_array_duplicate_review_protocol as prior
import typed_static_invoke_set_protocol as process_base
import constant_owned_scalar_query_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
CASE = sources.CASE
PREFIX = common.PREFIX + r'''
dec $test_owned_scalar_peer_front(pstate, nat) : bool
def $test_owned_scalar_peer_front(S,0) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINED /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.INDEX = 0 /\ ~$config_method_receiver(S,pconfigcall)
def $test_owned_scalar_peer_front(S,1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINED /\ pconfigcall.OWNER =/= eps
def $test_owned_scalar_peer_front(S,2) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.INDEX = 0 /\ $config_method_receiver(S,pconfigcall)
def $test_owned_scalar_peer_front(S,3) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.OWNER =/= eps
  -- if $config_method_receiver(S,pconfigcall)
def $test_owned_scalar_peer_front(S,4) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.INDEX = 0 /\ ~$config_method_receiver(S,pconfigcall)
def $test_owned_scalar_peer_front(S,5) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.OWNER =/= eps
  -- if ~$config_method_receiver(S,pconfigcall)
def $test_owned_scalar_peer_front(S,n_phase) = false -- otherwise
dec $test_owned_scalar_peer_seek(pstate, nat, nat) : pstate
def $test_owned_scalar_peer_seek(S,n_phase,0) = S
def $test_owned_scalar_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_owned_scalar_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_owned_scalar_peer_seek(S,n_phase,n) = $test_owned_scalar_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_owned_scalar_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_owned_scalar_peer_seek({start},{phase},2000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_owned_scalar_peer_front({state},{phase})', *common.public(state)]


def controls(state, call, owner, label):
    # These malformed authority/shape projections are never driven.
    values = [
        f'S_dead_{label} = {state}[.ALLOCATIONS = $destruction_node_delete({state}.ALLOCATIONS,HOBJECT {owner})]',
        f'~$dynamic_scalar_constant_valid(S_dead_{label},{call})',
        f'~$dynamic_scalar_constant_call({call})']
    for change in ['.OWNER = eps', f'.OWNER = (|{state}.OBJECTS|)', '.SELECTION = (0)',
            '.KIND = INTRINSIC_DEFINE', '.SITE = PORIGIN 0 eps',
            f'.LINE = $({call}.LINE + 1)', '.INDEX = 0', f'.NAMED = ~{call}.NAMED']:
        values += [f'~$dynamic_scalar_constant_valid({state},{call}[{change}])']
    for value in ['PNULL', 'PSTRING ($ptascii("37.5"))', 'POBJECT 0', 'PARRAY 0',
            'PFLOAT 9221120237041090560', 'PFLOAT 9218868437227405312']:
        values += [f'~$dynamic_scalar_constant_valid({state},{call}[.SENT = [NAMED_SENT (KNOWN ({value}))]])']
    values += [f'~$dynamic_scalar_constant_valid({state},{call}[.SENT = eps])',
        f'~$dynamic_scalar_constant_valid({state},{call}[.SENT = [NAMED_SENT (KNOWN (PINT 1)),NAMED_SENT (KNOWN (PINT 2))]])',
        f'pconfigpack_{label} = {{INDEX 0,SITE {call}.SITE,LINE {call}.LINE,ARRAY 0,ITEMS eps}}',
        f'~$dynamic_scalar_constant_valid({state},{call}[.PACKS = [pconfigpack_{label}]])']
    return values


def error(state, before, call, kind, message, invoke):
    values = [*common.step(state, before), *common.public(state),
        f'{state}.TODO = (THROW_SEARCH n_error_{state}) :: ptask_{before}*',
        f'{state}.OBJECTS[n_error_{state}] = THROWABLE pthrowable_{state}',
        f'pthrowable_{state}.KIND = "{kind}"',
        f'pthrowable_{state}.ORIGIN = ({call}.SITE)',
        f'$throwable_chain_valid({state},n_error_{state})',
        f'$string_bytes($throwable_field({state},n_error_{state},"message")) = ({text(message)})',
        f'$throwable_field({state},n_error_{state},"previous") = PNULL',
        f'$throwable_field({state},n_error_{state},"line") = PINT {call}.LINE',
        f'$throwable_field({state},n_error_{state},"trace") = PARRAY n_trace_{state}',
        f'{state}.ARRAYS[n_trace_{state}].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api_{state}))'
            + (f',ENTRY (KINT 1) (DIRECT (PARRAY n_invoke_{state}))]' if invoke else ']'),
        f'$trace_array_field({state},n_api_{state},$ptascii("function")) = PSTRING ($intrinsic_name({call}.KIND))',
        f'$trace_array_field({state},n_api_{state},$ptascii("line")) = PINT {call}.LINE',
        f'$trace_array_field({state},n_api_{state},$ptascii("args")) = PARRAY n_api_args_{state}',
        f'{state}.USERCONSTANTS = {before}.USERCONSTANTS',
        f'{state}.SELECTEDCALLS = eps', f'{state}.SELECTSEQ = 0',
        f'{state}.EVENTS = {before}.EVENTS',
        f'{state}.DESTRUCTION.OPERATIONS = eps', f'{state}.DESTRUCTION.RELEASES = eps']
    if invoke:
        values += [
            f'$trace_array_field({state},n_invoke_{state},$ptascii("function")) = PSTRING ($ptascii("__invoke"))',
            f'$trace_array_field({state},n_invoke_{state},$ptascii("class")) = PSTRING ($ptascii("Closure"))',
            f'$trace_array_field({state},n_invoke_{state},$ptascii("args")) = PARRAY n_invoke_args_{state}']
    return values


def checks(initial, stdout):
    begin = b'B|'
    strict = begin + b'S|held|'
    float_begin = strict + (b'T|defined(): Argument #1 ($constant_name) must be of type string, true given|37|'
        b'none|defined|rawT|null|currentI|97|1|gone|')
    floating = float_begin + b'F|held|'
    recovery = floating + (b'E|Undefined constant "37.5"|54|none|constant|__invoke|apiS|invokeD|distinct|'
        b'stillT|defined|currentD|97|2|gone|')
    reading = recovery + b'R|held|'
    assert stdout == reading + b'23|null|gone|kept|A|'
    values = [*initial, 'S_initial.COMPLETION = BUDGET', *reach('S_capture','S_initial',0),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        'pconfigcall_capture.OWNER = (n_a)', 'pconfigcall_capture.SELECTION = eps',
        'pconfigcall_capture.SENT = eps', 'pconfigcall_capture.PACKS = eps',
        'S_capture.OBJECTS[n_a] = INTRINSICCLOSURE INTRINSIC_DEFINED',
        '$config_selected_valid(S_capture,pconfigcall_capture)',
        '$config_nodes(pconfigcall_capture) = [HOBJECT n_a]',
        '$lookup(S_capture.ENV,$ptascii("call")) = (n_call)',
        '$lookup(S_capture.ENV,$ptascii("name")) = (n_name)',
        '$lookup(S_capture.ENV,$ptascii("calls")) = (n_calls)',
        '$lookup(S_capture.ENV,$ptascii("result")) = (n_result)',
        '$lookup(S_capture.ENV,$ptascii("weakStrict")) = (n_weak_a_cv)',
        'S_capture.STORE[n_call] = DEFINED (POBJECT n_a)',
        'S_capture.STORE[n_name] = DEFINED (PBOOL true)',
        'S_capture.STORE[n_weak_a_cv] = DEFINED (POBJECT n_weak_a)',
        'S_capture.OBJECTS[n_weak_a] = WEAKREFERENCE (n_a)',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_a) = 2',
        'S_capture.USERCONSTANTS = eps', 'S_capture.SELECTEDCALLS = eps',
        'S_capture.SELECTSEQ = 0', '$test_outputs(S_capture.EVENTS) = ' + term(begin),
        *reach('S','S_capture',1),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_S*',
        'pconfigcall.OWNER = (n_a)', 'pconfigcall.SELECTION = eps',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (PBOOL true))]',
        'pconfigcall.NAMED', 'pconfigcall.PACKS = eps', 'pconfigcall.INDEX = 1',
        'pconfigcall.LINE = 37', '$config_invoke_valid(S,pconfigcall)',
        '$dynamic_scalar_constant_valid(S,pconfigcall)', '$config_strict(S,pconfigcall)',
        '$config_conversion(S,pconfigcall,PBOOL true) = TYPEREJECT',
        'S.STORE[n_call] = DEFINED PNULL', 'S.STORE[n_name] = DEFINED (PINT 911)',
        'S.STORE[n_calls] = DEFINED (PINT 1)', 'S.STORE[n_result] = DEFINED (PINT 97)',
        '$weakref_get(S,n_weak_a) = POBJECT n_a',
        '$heap_owners($heap_graph(S),HOBJECT n_a) = 1',
        'S.USERCONSTANTS = eps', 'S.SELECTEDCALLS = eps', 'S.SELECTSEQ = 0',
        '~$destructor_operational(S)', '$test_outputs(S.EVENTS) = ' + term(strict),
        *controls('S','pconfigcall','n_a','strict'),
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        '$test_running(S_pause) = S',
        *error('S_type','S','pconfigcall','TypeError',
            'defined(): Argument #1 ($constant_name) must be of type string, true given',False),
        '$drive_steps($test_running(S_pause),1) = S_type_found',
        'S_type.ARRAYS[n_api_args_S_type].ITEMS = [ENTRY (KINT 0) (DIRECT (PBOOL true))]',
        '~(HOBJECT n_a <- S_type.ALLOCATIONS)', '$weakref_get(S_type,n_weak_a) = PNULL',
        'S_type.STRINGDATA = S.STRINGDATA',
        'S_type.STORE[n_result] = DEFINED (PINT 97)',
        *reach('S_float_capture','S_type',2),
        'S_float_capture.TODO = (CONFIG_ARGS pconfigcall_float_capture) :: ptask_float_capture*',
        'pconfigcall_float_capture.OWNER = (n_b)', 'n_b =/= n_a',
        'pconfigcall_float_capture.SELECTION = eps', 'pconfigcall_float_capture.SENT = eps',
        'S_float_capture.OBJECTS[n_b] = INTRINSICCLOSURE INTRINSIC_CONSTANT',
        '$lookup(S_float_capture.ENV,$ptascii("weakFloat")) = (n_weak_b_cv)',
        'S_float_capture.STORE[n_weak_b_cv] = DEFINED (POBJECT n_weak_b)',
        'S_float_capture.OBJECTS[n_weak_b] = WEAKREFERENCE (n_b)',
        '$heap_owners($heap_graph(S_float_capture),HOBJECT n_b) = 2',
        '$test_outputs(S_float_capture.EVENTS) = ' + term(float_begin),
        *reach('S_float','S_float_capture',3),
        'S_float.TODO = (CONFIG_INVOKE pconfigcall_float) :: ptask_S_float*',
        'pconfigcall_float.OWNER = (n_b)', 'pconfigcall_float.SELECTION = eps',
        'pconfigcall_float.SENT = [NAMED_SENT (KNOWN (PFLOAT 4630474473122824192))]',
        'pconfigcall_float.NAMED', 'pconfigcall_float.PACKS = eps', 'pconfigcall_float.INDEX = 1',
        'pconfigcall_float.LINE = 54', '$config_invoke_valid(S_float,pconfigcall_float)',
        '$exit_strict(S_float,pconfigcall_float.SITE)', '~$config_strict(S_float,pconfigcall_float)',
        '$dynamic_scalar_constant_valid(S_float,pconfigcall_float)',
        '$config_conversion(S_float,pconfigcall_float,PFLOAT 4630474473122824192) = TYPESTRING (PFLOAT 4630474473122824192)',
        'S_float_received = $typed_apply(S_float,TYPESTRING (PFLOAT 4630474473122824192),pconfigcall_float.LINE)',
        'S_float_received.RESULT = KNOWN pvalue_received',
        '$string_bytes(pvalue_received) = ($ptascii("37.5"))',
        '$string_carrier_valid(S_float_received,pvalue_received)',
        'S_float.STORE[n_call] = DEFINED pvalue_current_call',
        '$string_bytes(pvalue_current_call) = ($ptascii("defined"))',
        'S_float.STORE[n_name] = DEFINED (PFLOAT 0)',
        'S_float.STORE[n_calls] = DEFINED (PINT 2)', 'S_float.STORE[n_result] = DEFINED (PINT 97)',
        '$weakref_get(S_float,n_weak_b) = POBJECT n_b',
        '$heap_owners($heap_graph(S_float),HOBJECT n_b) = 1',
        '$entry_lookup(S_float.ARRAYS[n_api_args_S_type].ITEMS,KINT 0) = (DIRECT (PBOOL true))',
        '$test_outputs(S_float.EVENTS) = ' + term(floating),
        *controls('S_float','pconfigcall_float','n_b','float'),
        'S_float_pause = $drive_steps(S_float,0)',
        'S_float_pause = S_float[.COMPLETION = BUDGET]',
        *error('S_error','S_float','pconfigcall_float','Error','Undefined constant "37.5"',True),
        '$drive_steps($test_running(S_float_pause),1) = S_error_found',
        'S_error.ARRAYS[n_api_args_S_error].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_received)]',
        'S_error.ARRAYS[n_invoke_args_S_error].ITEMS = [ENTRY (KINT 0) (DIRECT (PFLOAT 4630474473122824192))]',
        '$strict_check(S_error,PARRAY n_api_args_S_error,PARRAY n_invoke_args_S_error,eps) = COMPARED false',
        'S_error.STRINGDATA = S_float_received.STRINGDATA',
        '~(HOBJECT n_b <- S_error.ALLOCATIONS)', '$weakref_get(S_error,n_weak_b) = PNULL',
        'S_error.STORE[n_result] = DEFINED (PINT 97)',
        *reach('S_recovery','S_error',4),
        'S_recovery.TODO = (CONFIG_ARGS pconfigcall_recovery) :: ptask_recovery*',
        'pconfigcall_recovery.OWNER = (n_c)', 'n_c =/= n_b', 'n_c =/= n_a',
        'pconfigcall_recovery.SELECTION = eps', 'pconfigcall_recovery.SENT = eps',
        'S_recovery.OBJECTS[n_c] = INTRINSICCLOSURE INTRINSIC_CONSTANT',
        '$lookup(S_recovery.ENV,$ptascii("weakRead")) = (n_weak_c_cv)',
        'S_recovery.STORE[n_weak_c_cv] = DEFINED (POBJECT n_weak_c)',
        'S_recovery.OBJECTS[n_weak_c] = WEAKREFERENCE (n_c)',
        '$heap_owners($heap_graph(S_recovery),HOBJECT n_c) = 2',
        'S_recovery.USERCONSTANTS = [puserconstant]',
        'puserconstant.NAME = $ptascii("2.5")', 'puserconstant.VALUE = PINT 23',
        'puserconstant.CLASS = PVSCALAR', '$test_outputs(S_recovery.EVENTS) = ' + term(recovery),
        *reach('S_read','S_recovery',5),
        'S_read.TODO = (CONFIG_INVOKE pconfigcall_read) :: ptask_read*',
        'pconfigcall_read.OWNER = (n_c)', 'pconfigcall_read.SELECTION = eps',
        'pconfigcall_read.SENT = [NAMED_SENT (KNOWN pvalue_read)]',
        '$string_bytes(pvalue_read) = ($ptascii("2.5"))',
        '$dynamic_owned_global_query_valid(S_read,pconfigcall_read)',
        '~$dynamic_scalar_constant_valid(S_read,pconfigcall_read)',
        'S_read.STORE[n_call] = DEFINED PNULL',
        '$weakref_get(S_read,n_weak_c) = POBJECT n_c',
        '$heap_owners($heap_graph(S_read),HOBJECT n_c) = 1',
        '$entry_lookup(S_read.ARRAYS[n_api_args_S_type].ITEMS,KINT 0) = (DIRECT (PBOOL true))',
        '$entry_lookup(S_read.ARRAYS[n_api_args_S_error].ITEMS,KINT 0) = (DIRECT pvalue_received)',
        '$entry_lookup(S_read.ARRAYS[n_invoke_args_S_error].ITEMS,KINT 0) = (DIRECT (PFLOAT 4630474473122824192))',
        '$test_outputs(S_read.EVENTS) = ' + term(reading),
        *common.step('S_value','S_read','PINT 23'),
        'S_value.TODO = ptask_read*', '~(HOBJECT n_c <- S_value.ALLOCATIONS)',
        '$weakref_get(S_value,n_weak_c) = PNULL',
        *define.finish('S_value',stdout),
        'S_final.USERCONSTANTS = S_recovery.USERCONSTANTS',
        'S_final.SELECTEDCALLS = eps', 'S_final.SELECTSEQ = 0']
    for node in ['HOBJECT n_a','HOBJECT n_b','HOBJECT n_c','HOBJECT n_weak_a',
            'HOBJECT n_weak_b','HOBJECT n_weak_c','HOBJECT n_error_S_type',
            'HOBJECT n_error_S_error','HARRAY n_trace_S_type','HARRAY n_api_args_S_type',
            'HARRAY n_trace_S_error','HARRAY n_api_args_S_error','HARRAY n_invoke_args_S_error']:
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
