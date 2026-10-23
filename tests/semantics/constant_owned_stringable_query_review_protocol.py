#!/usr/bin/env python3
"""Explicit received-name errors retain raw wrapper objects through array roots."""
from pathlib import Path

import define_stdclass_array_duplicate_review_protocol as prior
import typed_static_invoke_set_protocol as process_base
import constant_owned_stringable_query_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
CASE = sources.CASE
PREFIX = common.PREFIX + r'''
dec $test_owned_string_peer_unset(pstate, preqbytes) : bool
def $test_owned_string_peer_unset(S,preqbytes) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_name) metadata_name) :: expression_tail*
  -- if $base64(text_name) = preqbytes
def $test_owned_string_peer_unset(S,preqbytes) = false -- otherwise
dec $test_owned_string_peer_front(pstate, nat) : bool
def $test_owned_string_peer_front(S,0) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.INDEX = 0 /\ $config_method_receiver(S,pconfigcall)
def $test_owned_string_peer_front(S,1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_owned_query_string_call(pconfigcall)
def $test_owned_string_peer_front(S,2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $context_target(pcallcontext) = METHOD_TARGET n_object porigin_method
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*
  -- if $dynamic_owned_query_string_call(pconfigcall)
def $test_owned_string_peer_front(S,3) = true
  -- if S.TODO = (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*
  -- if $dynamic_owned_query_string_call(pconfigcall)
def $test_owned_string_peer_front(S,4) = $test_owned_string_peer_unset(S,$ptascii("error"))
def $test_owned_string_peer_front(S,5) = $test_owned_string_peer_unset(S,$ptascii("rawInvoke"))
def $test_owned_string_peer_front(S,6) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
def $test_owned_string_peer_front(S,7) = $test_owned_string_peer_unset(S,$ptascii("rawApi"))
def $test_owned_string_peer_front(S,n_phase) = false -- otherwise
dec $test_owned_string_peer_seek(pstate, nat, nat) : pstate
def $test_owned_string_peer_seek(S,n_phase,0) = S
def $test_owned_string_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_owned_string_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_owned_string_peer_seek(S,n_phase,n) = $test_owned_string_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_owned_string_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $test_owned_string_peer_settled(pstate) : bool
def $test_owned_string_peer_settled(S) = (S.DESTRUCTION.RELEASES = eps /\ S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.CALLS = eps)
dec $test_owned_string_peer_settle(pstate, nat) : pstate
def $test_owned_string_peer_settle(S,0) = S
def $test_owned_string_peer_settle(S,n) = S
  -- if $(n > 0)
  -- if $test_owned_string_peer_settled(S) \/ $test_owned_string_peer_front(S,6) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_owned_string_peer_settle(S,n) = $test_owned_string_peer_settle($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_owned_string_peer_settled(S) /\ ~$test_owned_string_peer_front(S,6)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_owned_string_peer_seek({start},{phase},3000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_owned_string_peer_front({state},{phase})', *common.public(state)]


def budget(state):
    return [f'{state}_pause = $drive_steps({state},0)',
        f'{state}_pause = {state}[.COMPLETION = BUDGET]',
        f'$test_running({state}_pause) = {state}',
        f'$drive_steps({state},1) = $drive_steps($test_running({state}_pause),1)']


def settle(state, start):
    return [f'{state}_found = $test_owned_string_peer_settle({start},80)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_owned_string_peer_settled({state})', *common.public(state)]


def controls():
    # These projections test refusal only; none is driven as a source state.
    values = ['S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_callee)]',
        '~$dynamic_query_string_valid(S_dead,pconfigcall)',
        'S_wrong = S[.OBJECTS[n_callee] = INTRINSICCLOSURE INTRINSIC_DEFINED]',
        '~$dynamic_query_string_valid(S_wrong,pconfigcall)',
        '~$dynamic_query_string_call(pconfigcall)']
    for change in ['.OWNER = eps', '.OWNER = (|S.OBJECTS|)', '.SELECTION = (0)',
            '.KIND = INTRINSIC_DEFINE', '.KIND = INTRINSIC_DEFINED', '.INDEX = 0',
            '.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall.LINE + 1)', '.NAMED = true']:
        values += [f'~$dynamic_query_string_valid(S,pconfigcall[{change}])']
    for value in ['PNULL','PBOOL false','PINT 0','PFLOAT 0',
            'PSTRING ($ptascii(""))','PARRAY 0']:
        values += [f'~$dynamic_owned_query_string_call(pconfigcall[.SENT = [NAMED_SENT (KNOWN ({value}))]])']
    values += ['pconfigpack_bad = {INDEX 0,SITE pconfigcall.SITE,LINE pconfigcall.LINE,ARRAY 0,ITEMS eps}',
        '~$dynamic_owned_query_string_call(pconfigcall[.PACKS = [pconfigpack_bad]])',
        '~$dynamic_owned_query_string_call(pconfigcall[.SENT = eps])',
        '~$dynamic_owned_query_string_call(pconfigcall[.SENT = pconfigcall.SENT ++ pconfigcall.SENT])',
        '~$dynamic_query_string_valid(S,pconfigcall[.SENT = [NAMED_SENT (KNOWN (POBJECT (|S.OBJECTS|)))]] )',
        '~$dynamic_query_string_valid(S,pconfigcall[.SENT = [NAMED_SENT (KNOWN (POBJECT n_weak_name))]])',
        '~$config_string_site_valid(S,pconfigcall,n_name,PORIGIN 0 eps,z_child,pconfigcall.LINE)',
        '~$config_string_site_valid(S,pconfigcall,n_name,porigin_child,$(z_child + 1),pconfigcall.LINE)',
        '~$config_string_site_valid(S,pconfigcall,n_name,porigin_child,z_child,$(pconfigcall.LINE + 1))']
    return values


def checks(initial, stdout):
    begin = b'B|'
    converted = begin + b'S|calleeHeld|'
    caught = converted + (b'E|Undefined constant "V102_REVIEW_MISSING"|29|none|constant|__invoke|'
        b'apiS|invokeObject|same|currentNull|97|1|0|calleeGone|traceHeld|')
    raw = caught + b'rawHeld|0|'
    released = raw + b'D|calleeGone|gone|1|V102_REVIEW_MISSING|'
    assert stdout == released + b'A|'
    values = [*initial, 'S_initial.COMPLETION = BUDGET', *reach('S_capture','S_initial',0),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        'pconfigcall_capture.OWNER = (n_callee)', 'pconfigcall_capture.SELECTION = eps',
        'pconfigcall_capture.PACKS = eps', 'pconfigcall_capture.SENT = eps',
        'S_capture.OBJECTS[n_callee] = INTRINSICCLOSURE INTRINSIC_CONSTANT',
        '$config_selected_valid(S_capture,pconfigcall_capture)',
        '$config_nodes(pconfigcall_capture) = [HOBJECT n_callee]',
        *[f'$lookup(S_capture.ENV,{text(name)}) = (n_{label}_cv)' for name,label in [
            ('call','call'),('name','name'),('weakCall','weak_call'),('weakName','weak_name'),
            ('casts','casts'),('drops','drops'),('result','result')]],
        'S_capture.STORE[n_call_cv] = DEFINED (POBJECT n_callee)',
        'S_capture.STORE[n_name_cv] = DEFINED (POBJECT n_name)',
        'S_capture.STORE[n_weak_call_cv] = DEFINED (POBJECT n_weak_call)',
        'S_capture.STORE[n_weak_name_cv] = DEFINED (POBJECT n_weak_name)',
        '$weakref_get(S_capture,n_weak_call) = POBJECT n_callee',
        '$weakref_get(S_capture,n_weak_name) = POBJECT n_name',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_callee) = 2',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_name) = 1',
        'S_capture.STORE[n_casts_cv] = DEFINED (PINT 0)',
        'S_capture.STORE[n_drops_cv] = DEFINED (PINT 0)',
        'S_capture.STORE[n_result_cv] = DEFINED (PINT 97)',
        'S_capture.USERCONSTANTS = eps', 'S_capture.SELECTEDCALLS = eps',
        'S_capture.SELECTSEQ = 0', '$test_outputs(S_capture.EVENTS) = ' + term(begin),
        *reach('S','S_capture',1),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_call*',
        'pconfigcall.OWNER = (n_callee)', 'pconfigcall.SELECTION = eps',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_name))]',
        '~pconfigcall.NAMED', 'pconfigcall.PACKS = eps', 'pconfigcall.INDEX = 1',
        'pconfigcall.LINE = 29', '$config_invoke_valid(S,pconfigcall)',
        '$dynamic_owned_query_string_call(pconfigcall)', '$dynamic_query_string_valid(S,pconfigcall)',
        '$dynamic_define_known(S,pconfigcall.SITE,0) = eps',
        '$exit_strict(S,pconfigcall.SITE)', '~$config_strict(S,pconfigcall)',
        '$config_method_receiver(S,pconfigcall)', '$stringable_instance(S,n_name)',
        '$config_nodes(pconfigcall) = [HOBJECT n_callee,HOBJECT n_name]',
        '$config_string_object(pconfigcall) = (n_name)',
        '$config_string_source(S,pconfigcall) = ((porigin_child,z_child))',
        '$config_string_site_valid(S,pconfigcall,n_name,porigin_child,z_child,pconfigcall.LINE)',
        '$config_string_launch(S,pconfigcall)',
        'S.USERCONSTANTS = eps', 'S.SELECTEDCALLS = eps', 'S.SELECTSEQ = 0',
        '$test_outputs(S.EVENTS) = ' + term(begin), *controls(),
        *common.step('S_launch','S'), *common.public('S_launch'),
        'S_launch.TODO = (CALL_ARGS (METHOD_TARGET n_name porigin_method) eps 0 eps (porigin_child) pconfigcall.LINE) :: (STRINGIFY_RESULT n_name porigin_child pconfigcall.LINE) :: (CONFIG_STRING_RESULT pconfigcall n_name porigin_child z_child pconfigcall.LINE) :: ptask_call*',
        *reach('S_entered','S_launch',2),
        'S_entered.CURRENT = (pcallcontext)',
        '$config_string_trace_context(S_entered,pcallcontext)',
        '$config_string_site_valid(S_entered,pconfigcall,n_name,porigin_child,z_child,pconfigcall.LINE)',
        '$weakref_get(S_entered,n_weak_call) = POBJECT n_callee',
        '$weakref_get(S_entered,n_weak_name) = POBJECT n_name',
        *reach('S_returned','S_entered',3),
        'S_returned.TODO = (CONFIG_STRING_RESULT pconfigcall n_name porigin_child z_child pconfigcall.LINE) :: ptask_call*',
        'S_returned.CURRENT = eps', 'S_returned.FRAMES = eps',
        'S_returned.ORIGIN = (porigin_child)', 'porigin_child =/= pconfigcall.SITE',
        'S_returned.RESULT = KNOWN pvalue_received',
        '$string_bytes(pvalue_received) = (' + text('V102_REVIEW_MISSING') + ')',
        '$string_carrier_valid(S_returned,pvalue_received)',
        '$config_string_site_valid(S_returned,pconfigcall,n_name,porigin_child,z_child,pconfigcall.LINE)',
        '$call_task_valid(S_returned,CONFIG_STRING_RESULT pconfigcall n_name porigin_child z_child pconfigcall.LINE)',
        '$task_nodes(CONFIG_STRING_RESULT pconfigcall n_name porigin_child z_child pconfigcall.LINE) = [HOBJECT n_name,HOBJECT n_callee,HOBJECT n_name]',
        'pconfigcall_received = pconfigcall[.SENT = [NAMED_SENT (KNOWN pvalue_received)]]',
        '~$dynamic_owned_global_query_valid(S_returned,pconfigcall_received)',
        '$dynamic_owned_global_query_valid(S_returned[.ORIGIN = (pconfigcall.SITE)],pconfigcall_received)',
        'S_returned.STORE[n_call_cv] = DEFINED PNULL',
        'S_returned.STORE[n_name_cv] = DEFINED PNULL',
        'S_returned.STORE[n_casts_cv] = DEFINED (PINT 1)',
        'S_returned.STORE[n_drops_cv] = DEFINED (PINT 0)',
        'S_returned.STORE[n_result_cv] = DEFINED (PINT 97)',
        '$weakref_get(S_returned,n_weak_call) = POBJECT n_callee',
        '$weakref_get(S_returned,n_weak_name) = POBJECT n_name',
        '$heap_owners($heap_graph(S_returned),HOBJECT n_callee) = 1',
        '$test_outputs(S_returned.EVENTS) = ' + term(converted), *budget('S_returned'),
        *common.step('S_error_pending','S_returned'), *common.public('S_error_pending'),
        'S_error_pending.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_call*',
        'pdestructionoperation.PENDING = (n_error)',
        '$weakref_get(S_error_pending,n_weak_call) = POBJECT n_callee',
        *settle('S_error','S_error_pending'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_call*',
        'S_error.ORIGIN = (pconfigcall.SITE)',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Error"',
        'pthrowable.ORIGIN = (pconfigcall.SITE)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('Undefined constant "V102_REVIEW_MISSING"') + ')',
        '$throwable_field(S_error,n_error,"line") = PINT 29',
        '$string_bytes($throwable_field(S_error,n_error,"file")) = ($call_sourcefile(S_error.FILES,pconfigcall.SITE))',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api_frame)),ENTRY (KINT 1) (DIRECT (PARRAY n_invoke_frame))]',
        '$trace_array_field(S_error,n_api_frame,$ptascii("function")) = PSTRING ($ptascii("constant"))',
        '$trace_array_field(S_error,n_invoke_frame,$ptascii("function")) = PSTRING ($ptascii("__invoke"))',
        '$trace_array_field(S_error,n_api_frame,$ptascii("args")) = PARRAY n_api_args',
        '$trace_array_field(S_error,n_invoke_frame,$ptascii("args")) = PARRAY n_invoke_args',
        'S_error.ARRAYS[n_api_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_received)]',
        'S_error.ARRAYS[n_invoke_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_name))]',
        '~(HOBJECT n_callee <- S_error.ALLOCATIONS)',
        '$weakref_get(S_error,n_weak_call) = PNULL',
        '$weakref_get(S_error,n_weak_name) = POBJECT n_name',
        'S_error.STORE[n_result_cv] = DEFINED (PINT 97)',
        'S_error.STORE[n_casts_cv] = DEFINED (PINT 1)',
        'S_error.STORE[n_drops_cv] = DEFINED (PINT 0)',
        'S_error.USERCONSTANTS = eps', 'S_error.SELECTEDCALLS = eps', 'S_error.SELECTSEQ = 0',
        '$test_outputs(S_error.EVENTS) = ' + term(converted),
        *reach('S_caught','S_error',4),
        '$lookup(S_caught.ENV,$ptascii("rawApi")) = (n_api_cv)',
        '$lookup(S_caught.ENV,$ptascii("rawInvoke")) = (n_invoke_cv)',
        'S_caught.STORE[n_api_cv] = DEFINED (PARRAY n_api_args)',
        'S_caught.STORE[n_invoke_cv] = DEFINED (PARRAY n_invoke_args)',
        '$weakref_get(S_caught,n_weak_call) = PNULL',
        '$weakref_get(S_caught,n_weak_name) = POBJECT n_name',
        'S_caught.STORE[n_drops_cv] = DEFINED (PINT 0)',
        '$test_outputs(S_caught.EVENTS) = ' + term(caught),
        *reach('S_raw','S_caught',5),
        '~(HOBJECT n_error <- S_raw.ALLOCATIONS)', '~(HARRAY n_trace <- S_raw.ALLOCATIONS)',
        'HARRAY n_invoke_args <- S_raw.ALLOCATIONS',
        '$entry_lookup(S_raw.ARRAYS[n_invoke_args].ITEMS,KINT 0) = (DIRECT (POBJECT n_name))',
        '$entry_lookup(S_raw.ARRAYS[n_api_args].ITEMS,KINT 0) = (DIRECT pvalue_received)',
        '$weakref_get(S_raw,n_weak_name) = POBJECT n_name',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_name) = 1',
        'S_raw.STORE[n_casts_cv] = DEFINED (PINT 1)',
        'S_raw.STORE[n_drops_cv] = DEFINED (PINT 0)',
        '$test_outputs(S_raw.EVENTS) = ' + term(raw),
        *reach('S_drop','S_raw',6),
        'S_drop.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_drop*',
        'pdestructorcall.OBJECT = n_name', 'pdestructorcall.TARGET = METHOD_TARGET n_name porigin_destructor',
        'pdestructorcall.CALLER = eps', 'pdestructorcall.USER',
        '$destructor_call_valid(S_drop,pdestructorcall)',
        '$call_task_valid(S_drop,DESTRUCTOR_ENTER pdestructorcall)',
        '$weakref_get(S_drop,n_weak_call) = PNULL',
        'S_drop.STORE[n_drops_cv] = DEFINED (PINT 0)',
        '$test_outputs(S_drop.EVENTS) = ' + term(raw), *budget('S_drop'),
        *reach('S_released','S_drop',7),
        '~(HOBJECT n_name <- S_released.ALLOCATIONS)',
        '~(HARRAY n_invoke_args <- S_released.ALLOCATIONS)',
        '$weakref_get(S_released,n_weak_name) = PNULL',
        '$weakref_get(S_released,n_weak_call) = PNULL',
        'S_released.STORE[n_casts_cv] = DEFINED (PINT 1)',
        'S_released.STORE[n_drops_cv] = DEFINED (PINT 1)',
        'S_released.STORE[n_result_cv] = DEFINED (PINT 97)',
        '$entry_lookup(S_released.ARRAYS[n_api_args].ITEMS,KINT 0) = (DIRECT pvalue_received)',
        '$test_outputs(S_released.EVENTS) = ' + term(released),
        *define.finish('S_released',stdout),
        'S_final.USERCONSTANTS = eps', 'S_final.SELECTEDCALLS = eps', 'S_final.SELECTSEQ = 0']
    for index, value in enumerate(['PSTRING ' + text('A::B'),
            'PSTRING ' + text('__COMPILER_HALT_OFFSET__'), 'PSTRING [65,0,66]', 'PINT 0']):
        bad = f'S_refused_{index}'
        values += [f'{bad} = $dynamic_query_string_finish(S_returned,pconfigcall,{value})',
            f'{bad}.COMPLETION = UNSUPPORTED "Stringable query global name"',
            f'{bad}.EVENTS = S_returned.EVENTS',
            f'{bad}.ALLOCATIONS = S_returned.ALLOCATIONS']
    for node in ['HOBJECT n_callee','HOBJECT n_name','HOBJECT n_weak_call','HOBJECT n_weak_name',
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
