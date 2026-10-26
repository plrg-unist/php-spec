#!/usr/bin/env python3
"""A reached weak query TypeError keeps its raw object until the last array copy."""
from pathlib import Path

import define_stdclass_array_duplicate_review_protocol as prior
import typed_static_invoke_set_protocol as process_base
import constant_owned_nonstringable_query_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
CASE = sources.CASE
PREFIX = common.PREFIX + r'''
dec $test_owned_nonstring_peer_unset(pstate, preqbytes) : bool
def $test_owned_nonstring_peer_unset(S,preqbytes) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_name) metadata_name) :: expression_tail*
  -- if $base64(text_name) = preqbytes
def $test_owned_nonstring_peer_unset(S,preqbytes) = false -- otherwise
dec $test_owned_nonstring_peer_front(pstate, nat) : bool
def $test_owned_nonstring_peer_front(S,0) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINED /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.INDEX = 0
def $test_owned_nonstring_peer_front(S,1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINED
  -- if $dynamic_owned_query_string_call(pconfigcall)
def $test_owned_nonstring_peer_front(S,2) = $test_owned_nonstring_peer_unset(S,$ptascii("error"))
def $test_owned_nonstring_peer_front(S,3) = $test_owned_nonstring_peer_unset(S,$ptascii("rawArgs"))
def $test_owned_nonstring_peer_front(S,4) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
def $test_owned_nonstring_peer_front(S,5) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue) = ($ptascii("V104_REVIEW_RECOVERY"))
def $test_owned_nonstring_peer_front(S,n_phase) = false -- otherwise
dec $test_owned_nonstring_peer_seek(pstate, nat, nat) : pstate
def $test_owned_nonstring_peer_seek(S,n_phase,0) = S
def $test_owned_nonstring_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_owned_nonstring_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_owned_nonstring_peer_seek(S,n_phase,n) = $test_owned_nonstring_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_owned_nonstring_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $test_owned_nonstring_peer_settled(pstate) : bool
def $test_owned_nonstring_peer_settled(S) = (S.DESTRUCTION.RELEASES = eps /\ S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.CALLS = eps)
dec $test_owned_nonstring_peer_settle(pstate, nat) : pstate
def $test_owned_nonstring_peer_settle(S,0) = S
def $test_owned_nonstring_peer_settle(S,n) = S
  -- if $(n > 0)
  -- if $test_owned_nonstring_peer_settled(S) \/ $test_owned_nonstring_peer_front(S,4) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_owned_nonstring_peer_settle(S,n) = $test_owned_nonstring_peer_settle($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_owned_nonstring_peer_settled(S) /\ ~$test_owned_nonstring_peer_front(S,4)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_owned_nonstring_peer_seek({start},{phase},3000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_owned_nonstring_peer_front({state},{phase})', *common.public(state)]


def budget(state):
    return [f'{state}_pause = $drive_steps({state},0)',
        f'{state}_pause = {state}[.COMPLETION = BUDGET]',
        f'$test_running({state}_pause) = {state}',
        f'$drive_steps({state},1) = $drive_steps($test_running({state}_pause),1)']


def settle(state, start):
    return [f'{state}_found = $test_owned_nonstring_peer_settle({start},80)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_owned_nonstring_peer_settled({state})', *common.public(state)]


def controls():
    # These projections check refusal only and are never driven as source states.
    values = ['~$dynamic_query_string_call(pconfigcall)',
        'S_dead_callee = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_callee)]',
        '~$dynamic_query_nonstring_valid(S_dead_callee,pconfigcall)',
        'S_dead_name = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_name)]',
        '~$dynamic_query_nonstring_valid(S_dead_name,pconfigcall)',
        'S_wrong_callee = S[.OBJECTS[n_callee] = INTRINSICCLOSURE INTRINSIC_CONSTANT]',
        '~$dynamic_query_nonstring_valid(S_wrong_callee,pconfigcall)',
        '~$dynamic_query_nonstring_object(S,n_weak_name)',
        '~$dynamic_query_nonstring_object(S,|S.OBJECTS|)']
    for change in ['.OWNER = eps', '.OWNER = (|S.OBJECTS|)', '.SELECTION = (0)',
            '.KIND = INTRINSIC_DEFINE', '.KIND = INTRINSIC_CONSTANT', '.INDEX = 0',
            '.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall.LINE + 1)', '.NAMED = true']:
        values += [f'~$dynamic_query_nonstring_valid(S,pconfigcall[{change}])']
    for value in ['PNULL', 'PBOOL false', 'PINT 0', 'PFLOAT 0',
            'PSTRING ($ptascii(""))', 'PARRAY 0',
            'POBJECT (|S.OBJECTS|)', 'POBJECT n_weak_name']:
        values += [f'~$dynamic_query_nonstring_valid(S,pconfigcall[.SENT = [NAMED_SENT (KNOWN ({value}))]])']
    values += ['pconfigpack_bad = {INDEX 0,SITE pconfigcall.SITE,LINE pconfigcall.LINE,ARRAY 0,ITEMS eps}',
        '~$dynamic_query_nonstring_valid(S,pconfigcall[.PACKS = [pconfigpack_bad]])',
        '~$dynamic_query_nonstring_valid(S,pconfigcall[.SENT = eps])',
        '~$dynamic_query_nonstring_valid(S,pconfigcall[.SENT = pconfigcall.SENT ++ pconfigcall.SENT])']
    return values


def checks(initial, stdout):
    begin = b'B|A|calleeHeld|'
    message = 'defined(): Argument #1 ($constant_name) must be of type string, V104ReviewName given'
    caught = begin + b'T|' + message.encode() + (b'|38|none|defined|file|38|rawObject|same|end|'
        b'currentNull|97|1|0|0|calleeGone|traceHeld|')
    raw = caught + b'rawHeld|0|'
    released = raw + b'D|calleeGone|gone|1|0|'
    assert stdout == released + b'23|A|'
    values = [*initial, 'S_initial.COMPLETION = BUDGET', *reach('S_capture','S_initial',0),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        'pconfigcall_capture.OWNER = (n_callee)', 'pconfigcall_capture.SELECTION = eps',
        'pconfigcall_capture.PACKS = eps', 'pconfigcall_capture.SENT = eps',
        'S_capture.OBJECTS[n_callee] = INTRINSICCLOSURE INTRINSIC_DEFINED',
        '$config_selected_valid(S_capture,pconfigcall_capture)',
        '$config_nodes(pconfigcall_capture) = [HOBJECT n_callee]',
        *[f'$lookup(S_capture.ENV,{text(name)}) = (n_{label}_cv)' for name,label in [
            ('call','call'),('name','name'),('weakCall','weak_call'),('weakName','weak_name'),
            ('effects','effects'),('methodCalls','methods'),('drops','drops'),('result','result')]],
        'S_capture.STORE[n_call_cv] = DEFINED (POBJECT n_callee)',
        'S_capture.STORE[n_name_cv] = DEFINED (POBJECT n_name)',
        'S_capture.STORE[n_weak_call_cv] = DEFINED (POBJECT n_weak_call)',
        'S_capture.STORE[n_weak_name_cv] = DEFINED (POBJECT n_weak_name)',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_callee) = 2',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_name) = 1',
        'S_capture.SELECTEDCALLS = eps', 'S_capture.SELECTSEQ = 0',
        '$test_outputs(S_capture.EVENTS) = ' + term(b'B|'),
        *reach('S','S_capture',1),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_call*',
        'pconfigcall.KIND = INTRINSIC_DEFINED', 'pconfigcall.OWNER = (n_callee)',
        'pconfigcall.SELECTION = eps', 'pconfigcall.PACKS = eps', '~pconfigcall.NAMED',
        'pconfigcall.INDEX = 1', 'pconfigcall.LINE = 38',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_name))]',
        '$config_invoke_valid(S,pconfigcall)', '$dynamic_owned_query_string_call(pconfigcall)',
        '$dynamic_scalar_define_arguments(S,pconfigcall,0)',
        '$dynamic_query_nonstring_object(S,n_name)', '$dynamic_query_nonstring_valid(S,pconfigcall)',
        '~$dynamic_query_string_valid(S,pconfigcall)', '~$stringable_instance(S,n_name)',
        '~$config_strict(S,pconfigcall)', '~$config_method_receiver(S,pconfigcall)',
        '~$config_string_launch(S,pconfigcall)', '~$pipe_site(S,pconfigcall.SITE)',
        '$dynamic_define_known(S,pconfigcall.SITE,0) = eps',
        'S.OBJECTS[n_name] = INSTANCE porigin_class',
        '$effective_method(S,porigin_class,$ptascii("toString"),|S.CLASSES|) = (pmethoddesc_ordinary)',
        '$effective_method(S,porigin_class,$ptascii("__toString"),|S.CLASSES|) = eps',
        '$config_nodes(pconfigcall) = [HOBJECT n_callee,HOBJECT n_name]',
        '$heap_owners($heap_graph(S),HOBJECT n_callee) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_name) = 1',
        '$weakref_get(S,n_weak_call) = POBJECT n_callee',
        '$weakref_get(S,n_weak_name) = POBJECT n_name',
        'S.STORE[n_call_cv] = DEFINED PNULL', 'S.STORE[n_name_cv] = DEFINED PNULL',
        'S.STORE[n_effects_cv] = DEFINED (PINT 1)', 'S.STORE[n_methods_cv] = DEFINED (PINT 0)',
        'S.STORE[n_drops_cv] = DEFINED (PINT 0)', 'S.STORE[n_result_cv] = DEFINED (PINT 97)',
        'S.USERCONSTANTS = eps', 'S.SELECTEDCALLS = eps', 'S.SELECTSEQ = 0',
        '$test_outputs(S.EVENTS) = ' + term(begin), *controls(), *budget('S'),
        *common.step('S_error_pending','S'), *settle('S_error','S_error_pending'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_call*',
        'S_error.ORIGIN = (pconfigcall.SITE)',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "TypeError"',
        'pthrowable.ORIGIN = (pconfigcall.SITE)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text(message) + ')',
        '$throwable_field(S_error,n_error,"line") = PINT 38',
        '$string_bytes($throwable_field(S_error,n_error,"file")) = ($call_sourcefile(S_error.FILES,pconfigcall.SITE))',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api_frame))]',
        '$trace_array_field(S_error,n_api_frame,$ptascii("function")) = PSTRING ($ptascii("defined"))',
        '$trace_array_field(S_error,n_api_frame,$ptascii("line")) = PINT 38',
        '$trace_array_field(S_error,n_api_frame,$ptascii("args")) = PARRAY n_api_args',
        'S_error.ARRAYS[n_api_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_name))]',
        '$node_children(S_error,HARRAY n_api_args) = [HOBJECT n_name]',
        '~(HOBJECT n_callee <- S_error.ALLOCATIONS)',
        '$weakref_get(S_error,n_weak_call) = PNULL',
        '$weakref_get(S_error,n_weak_name) = POBJECT n_name',
        '$heap_owners($heap_graph(S_error),HOBJECT n_name) = 1',
        'S_error.STORE[n_methods_cv] = DEFINED (PINT 0)',
        'S_error.STORE[n_drops_cv] = DEFINED (PINT 0)',
        'S_error.STORE[n_result_cv] = DEFINED (PINT 97)',
        'S_error.USERCONSTANTS = eps', '$test_outputs(S_error.EVENTS) = ' + term(begin),
        *reach('S_caught','S_error',2),
        '$lookup(S_caught.ENV,$ptascii("rawArgs")) = (n_raw_cv)',
        'S_caught.STORE[n_raw_cv] = DEFINED (PARRAY n_api_args)',
        '$weakref_get(S_caught,n_weak_call) = PNULL',
        '$weakref_get(S_caught,n_weak_name) = POBJECT n_name',
        'S_caught.STORE[n_methods_cv] = DEFINED (PINT 0)',
        '$test_outputs(S_caught.EVENTS) = ' + term(caught),
        *reach('S_raw','S_caught',3),
        '~(HOBJECT n_error <- S_raw.ALLOCATIONS)', '~(HARRAY n_trace <- S_raw.ALLOCATIONS)',
        '~(HARRAY n_api_frame <- S_raw.ALLOCATIONS)',
        'S_raw.STORE[n_raw_cv] = DEFINED (PARRAY n_api_args)',
        '$entry_lookup(S_raw.ARRAYS[n_api_args].ITEMS,KINT 0) = (DIRECT (POBJECT n_name))',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_name) = 1',
        '$weakref_get(S_raw,n_weak_name) = POBJECT n_name',
        '~(n_name <- S_raw.DESTRUCTION.CALLED)',
        'S_raw.STORE[n_methods_cv] = DEFINED (PINT 0)',
        'S_raw.STORE[n_drops_cv] = DEFINED (PINT 0)',
        '$test_outputs(S_raw.EVENTS) = ' + term(raw), *budget('S_raw'),
        *reach('S_drop','S_raw',4),
        'S_drop.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_drop*',
        'pdestructorcall.OBJECT = n_name',
        'pdestructorcall.TARGET = METHOD_TARGET n_name porigin_destructor',
        'pdestructorcall.CALLER = eps', 'pdestructorcall.USER',
        '$destructor_call_valid(S_drop,pdestructorcall)',
        '$call_task_valid(S_drop,DESTRUCTOR_ENTER pdestructorcall)',
        '$weakref_get(S_drop,n_weak_call) = PNULL',
        'S_drop.STORE[n_drops_cv] = DEFINED (PINT 0)',
        '$test_outputs(S_drop.EVENTS) = ' + term(raw), *budget('S_drop'),
        *reach('S_read','S_drop',5),
        'S_read.TODO = (CONFIG_INVOKE pconfigcall_read) :: ptask_read*',
        'pconfigcall_read.OWNER = (n_reader)', 'n_reader =/= n_callee',
        'pconfigcall_read.SELECTION = eps', 'pconfigcall_read.PACKS = eps',
        '$dynamic_owned_global_query_valid(S_read,pconfigcall_read)',
        '~(HOBJECT n_name <- S_read.ALLOCATIONS)', '~(HARRAY n_api_args <- S_read.ALLOCATIONS)',
        '$weakref_get(S_read,n_weak_name) = PNULL',
        'S_read.STORE[n_drops_cv] = DEFINED (PINT 1)',
        'S_read.STORE[n_methods_cv] = DEFINED (PINT 0)',
        'S_read.STORE[n_result_cv] = DEFINED (PINT 97)',
        'S_read.USERCONSTANTS = [puserconstant]',
        'puserconstant.NAME = $ptascii("V104_REVIEW_RECOVERY")',
        'puserconstant.VALUE = PINT 23', 'puserconstant.CLASS = PVSCALAR',
        '$test_outputs(S_read.EVENTS) = ' + term(released),
        *common.step('S_value_pending','S_read'), *settle('S_value','S_value_pending'),
        'S_value.TODO = ptask_read*', 'S_value.RESULT = KNOWN (PINT 23)',
        *define.finish('S_value',stdout),
        'S_final.USERCONSTANTS = S_read.USERCONSTANTS',
        'S_final.SELECTEDCALLS = eps', 'S_final.SELECTSEQ = 0']
    for node in ['HOBJECT n_callee','HOBJECT n_name','HOBJECT n_weak_call','HOBJECT n_weak_name',
            'HOBJECT n_error','HOBJECT n_reader','HARRAY n_trace','HARRAY n_api_frame','HARRAY n_api_args']:
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
