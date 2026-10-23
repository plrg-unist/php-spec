#!/usr/bin/env python3
"""Captured Stringable lookup ordering and strict raw-object retirement."""
from pathlib import Path

import constant_owned_query_protocol as captured
import typed_static_invoke_set_protocol as process_base
import constant_owned_stringable_query_sources as sources

define, packet, common = captured.define, captured.packet, captured.common
ROOT, text, term = captured.ROOT, captured.text, captured.term
PREFIX = common.PREFIX + r'''
dec $test_owned_string_front(pstate, pintrinsic, nat) : bool
def $test_owned_string_front(S,pintrinsic,0) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = pintrinsic /\ pconfigcall.OWNER =/= eps /\ pconfigcall.INDEX = 0
def $test_owned_string_front(S,pintrinsic,1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = pintrinsic /\ $dynamic_owned_query_string_call(pconfigcall)
def $test_owned_string_front(S,pintrinsic,2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $context_target(pcallcontext) = METHOD_TARGET n_object porigin_method
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*
  -- if pconfigcall.KIND = pintrinsic /\ $dynamic_owned_query_string_call(pconfigcall)
def $test_owned_string_front(S,pintrinsic,3) = true
  -- if S.TODO = (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*
  -- if pconfigcall.KIND = pintrinsic /\ $dynamic_owned_query_string_call(pconfigcall)
def $test_owned_string_front(S,pintrinsic,4) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = pintrinsic /\ pconfigcall.OWNER =/= eps
  -- if $dynamic_owned_global_query_valid(S,pconfigcall)
def $test_owned_string_front(S,pintrinsic,5) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
def $test_owned_string_front(S,pintrinsic,6) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_name) metadata_name) :: expression_tail*
  -- if $base64(text_name) = $ptascii("error")
def $test_owned_string_front(S,pintrinsic,n_phase) = false -- otherwise
dec $test_owned_string_seek(pstate, pintrinsic, nat, nat) : pstate
def $test_owned_string_seek(S,pintrinsic,n_phase,0) = S
def $test_owned_string_seek(S,pintrinsic,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_owned_string_front(S,pintrinsic,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_owned_string_seek(S,pintrinsic,n_phase,n) = $test_owned_string_seek($drive_steps($test_running(S),1),pintrinsic,n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_owned_string_front(S,pintrinsic,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $test_owned_string_settled(pstate) : bool
def $test_owned_string_settled(S) = (S.DESTRUCTION.RELEASES = eps /\ S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.CALLS = eps)
dec $test_owned_string_settle(pstate, nat) : pstate
def $test_owned_string_settle(S,0) = S
def $test_owned_string_settle(S,n) = S
  -- if $(n > 0)
  -- if $test_owned_string_settled(S) \/ $test_owned_string_front(S,INTRINSIC_CONSTANT,5) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_owned_string_settle(S,n) = $test_owned_string_settle($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_owned_string_settled(S) /\ ~$test_owned_string_front(S,INTRINSIC_CONSTANT,5)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, kind, phase):
    return [f'{state}_found = $test_owned_string_seek({start},{kind},{phase},3000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_owned_string_front({state},{kind},{phase})', *common.public(state)]


def budget(state):
    return [f'{state}_pause = $drive_steps({state},0)',
        f'{state}_pause = {state}[.COMPLETION = BUDGET]',
        f'$test_running({state}_pause) = {state}',
        f'$drive_steps({state},1) = $drive_steps($test_running({state}_pause),1)']


def settle(state, start, result=None):
    values = [f'{state}_found = $test_owned_string_settle({start},80)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_owned_string_settled({state})', *common.public(state)]
    if result is not None:
        values += [f'{state}.RESULT = KNOWN ({result})',
            f'{state}.EVENTS = {start}.EVENTS']
    return values


def front(state, start, kind, owner, obj, line, invoke=False):
    call = 'pconfigcall_' + state
    return [*reach(state,start,kind,1),
        f'{state}.TODO = (CONFIG_INVOKE {call}) :: ptask_{state}*',
        f'{call}.OWNER = ({owner})', f'{call}.SELECTION = eps',
        f'{call}.PACKS = eps', f'~{call}.NAMED', f'{call}.INDEX = 1',
        f'{call}.LINE = {line}',
        f'{call}.SENT = [NAMED_SENT (KNOWN (POBJECT {obj}))]',
        f'$config_invoke_valid({state},{call})',
        f'$dynamic_owned_query_string_call({call})',
        f'~$dynamic_query_string_call({call})',
        f'$dynamic_query_string_valid({state},{call})',
        f'$dynamic_define_known({state},{call}.SITE,0) = eps',
        f'{"" if invoke else "~"}$config_method_receiver({state},{call})',
        f'$config_nodes({call}) = [HOBJECT {owner},HOBJECT {obj}]',
        f'$stringable_instance({state},{obj})',
        *captured.intrinsic(state,owner,kind)]


def weak(state, variable, obj, label):
    return [f'$lookup({state}.ENV,{text(variable)}) = (n_weak_cv_{label})',
        f'{state}.STORE[n_weak_cv_{label}] = DEFINED (POBJECT n_weak_{label})',
        f'$weakref_get({state},n_weak_{label}) = POBJECT {obj}']


def controls(state, owner):
    call = 'pconfigcall_' + state
    values = [f'S_dead_{state} = {state}[.ALLOCATIONS = $destruction_node_delete({state}.ALLOCATIONS,HOBJECT {owner})]',
        f'~$dynamic_query_string_valid(S_dead_{state},{call})']
    for change in ['.OWNER = eps', f'.OWNER = (|{state}.OBJECTS|)', '.SELECTION = (0)',
            '.KIND = INTRINSIC_DEFINE', '.INDEX = 0', '.SITE = PORIGIN 0 eps',
            f'.LINE = $({call}.LINE + 1)', '.NAMED = true']:
        values += [f'~$dynamic_query_string_valid({state},{call}[{change}])']
    for value in ['PNULL','PBOOL false','PINT 0','PFLOAT 0','PSTRING ($ptascii(""))','PARRAY 0']:
        values += [f'~$dynamic_owned_query_string_call({call}[.SENT = [NAMED_SENT (KNOWN ({value}))]])']
    values += [f'pconfigpack_{state} = {{INDEX 0,SITE {call}.SITE,LINE {call}.LINE,ARRAY 0,ITEMS eps}}',
        f'~$dynamic_owned_query_string_call({call}[.PACKS = [pconfigpack_{state}]])',
        f'~$dynamic_owned_query_string_call({call}[.SENT = eps])',
        f'~$dynamic_owned_query_string_call({call}[.SENT = {call}.SENT ++ {call}.SENT])',
        f'~$dynamic_query_string_valid({state},{call}[.SENT = [NAMED_SENT (KNOWN (POBJECT (|{state}.OBJECTS|)))]] )']
    return values


def converted(state, start, kind, obj, key):
    call = 'pconfigcall_' + start
    return [f'$config_string_launch({start},{call})',
        f'$config_string_source({start},{call}) = ((porigin_child_{state},z_child_{state}))',
        *reach(state + '_entered',start,kind,2),
        f'{state}_entered.CURRENT = (pcallcontext_{state})',
        f'$config_string_trace_context({state}_entered,pcallcontext_{state})',
        *reach(state,state + '_entered',kind,3),
        f'{state}.TODO = (CONFIG_STRING_RESULT {call} {obj} porigin_child_{state} z_child_{state} {call}.LINE) :: ptask_{start}*',
        f'{state}.CURRENT = eps', f'{state}.FRAMES = eps',
        f'{state}.ORIGIN = (porigin_child_{state})',
        f'porigin_child_{state} =/= {call}.SITE',
        f'{state}.RESULT = KNOWN pvalue_{state}',
        f'$string_bytes(pvalue_{state}) = ({text(key)})',
        f'$string_carrier_valid({state},pvalue_{state})',
        f'$config_string_site_valid({state},{call},{obj},porigin_child_{state},z_child_{state},{call}.LINE)',
        f'$call_task_valid({state},CONFIG_STRING_RESULT {call} {obj} porigin_child_{state} z_child_{state} {call}.LINE)',
        f'pconfigcall_received_{state} = {call}[.SENT = [NAMED_SENT (KNOWN pvalue_{state})]]',
        f'~$dynamic_owned_global_query_valid({state},pconfigcall_received_{state})',
        f'$dynamic_owned_global_query_valid({state}[.ORIGIN = ({call}.SITE)],pconfigcall_received_{state})',
        *budget(state)]


def order(initial, stdout):
    first = b'B|S|held|'
    destructed = first + b'D|held|'
    second = destructed + b'17|calleeGone|nameGone|null|afterD|1|1|'
    returned = second + b'S|held|'
    assert stdout == returned + b'D|held|F|calleeGone|nameGone|null|afterD|2|2|lateT|17|A|'
    values = [*initial, *reach('S_capture','S_initial','INTRINSIC_CONSTANT',0),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        'pconfigcall_capture.OWNER = (n_reader)',
        '$config_selected_valid(S_capture,pconfigcall_capture)',
        '$config_nodes(pconfigcall_capture) = [HOBJECT n_reader]',
        *[f'$lookup(S_capture.ENV,{text(name)}) = (n_{name}_cv)' for name in [
            'call','name','key','strings','deaths','result']],
        'S_capture.STORE[n_call_cv] = DEFINED (POBJECT n_reader)',
        'S_capture.STORE[n_name_cv] = DEFINED (POBJECT n_name)',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_reader) = 2',
        'S_capture.USERCONSTANTS = eps',
        *front('S','S_capture','INTRINSIC_CONSTANT','n_reader','n_name',31),
        '~$config_strict(S,pconfigcall_S)',
        *weak('S','weak','n_reader','read'), *weak('S','weakName','n_name','name'),
        '$test_outputs(S.EVENTS) = ' + term(b'B|'),
        *controls('S','n_reader'),
        *converted('S_returned','S','INTRINSIC_CONSTANT','n_name','V102_ORDINARY'),
        'S_returned.STORE[n_call_cv] = DEFINED pvalue_current_call',
        '$string_bytes(pvalue_current_call) = ($ptascii("constant"))',
        'S_returned.STORE[n_name_cv] = DEFINED PNULL',
        'S_returned.STORE[n_strings_cv] = DEFINED (PINT 1)',
        'S_returned.STORE[n_deaths_cv] = DEFINED (PINT 0)',
        'S_returned.STORE[n_result_cv] = DEFINED (PINT 97)',
        'S_returned.USERCONSTANTS = eps',
        '$weakref_get(S_returned,n_weak_read) = POBJECT n_reader',
        '$weakref_get(S_returned,n_weak_name) = POBJECT n_name',
        '$test_outputs(S_returned.EVENTS) = ' + term(first),
        'S_handoff = $dynamic_query_string_finish(S_returned,pconfigcall_S,pvalue_S_returned)',
        'S_handoff.TODO = (CONFIG_INVOKE pconfigcall_received_S_returned) :: ptask_S*',
        'S_handoff.RESULT = KNOWN PNULL', 'S_handoff.BASE = BASE_VALUE (KNOWN PNULL)',
        '$config_nodes(pconfigcall_received_S_returned) = [HOBJECT n_reader]',
        '$heap_owners($heap_graph(S_handoff),HOBJECT n_name) = 0',
        *reach('S_drop','S_returned','INTRINSIC_CONSTANT',5),
        'S_drop.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_drop*',
        'pdestructorcall.OBJECT = n_name', '$destructor_call_valid(S_drop,pdestructorcall)',
        '$weakref_get(S_drop,n_weak_read) = POBJECT n_reader',
        'S_drop.STORE[n_deaths_cv] = DEFINED (PINT 0)',
        '$test_outputs(S_drop.EVENTS) = ' + term(first),
        *reach('S_ready','S_drop','INTRINSIC_CONSTANT',4),
        'S_ready.TODO = (CONFIG_INVOKE pconfigcall_received_S_returned) :: ptask_S*',
        '~(HOBJECT n_name <- S_ready.ALLOCATIONS)',
        '$weakref_get(S_ready,n_weak_name) = PNULL',
        '$weakref_get(S_ready,n_weak_read) = POBJECT n_reader',
        'S_ready.STORE[n_deaths_cv] = DEFINED (PINT 1)',
        'S_ready.STORE[n_key_cv] = DEFINED pvalue_after_key',
        '$string_bytes(pvalue_after_key) = ($ptascii("afterD"))',
        'S_ready.USERCONSTANTS = [puserconstant_first]',
        'puserconstant_first.NAME = $ptascii("V102_ORDINARY")',
        'puserconstant_first.VALUE = PINT 17', 'puserconstant_first.CLASS = PVSCALAR',
        '$dynamic_define_source(S_ready,puserconstant_first.ORIGIN)',
        '$test_outputs(S_ready.EVENTS) = ' + term(destructed),
        *common.step('S_value_pending','S_ready'),
        'S_value_pending.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_value) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_value) :: ptask_S*',
        'pdestructionoperation_value.VALUE = KNOWN (PINT 17)',
        'pdestructionoperation_value.PENDING = eps',
        '$weakref_get(S_value_pending,n_weak_read) = POBJECT n_reader',
        *settle('S_value','S_value_pending','PINT 17'),
        'S_value.TODO = ptask_S*', 'S_value.USERCONSTANTS = S_ready.USERCONSTANTS',
        '~(HOBJECT n_reader <- S_value.ALLOCATIONS)',
        '$weakref_get(S_value,n_weak_read) = PNULL',
        *front('S_explicit','S_value','INTRINSIC_DEFINED','n_has','n_explicit_name',42,True),
        '~$config_strict(S_explicit,pconfigcall_S_explicit)',
        *weak('S_explicit','weak','n_has','has'),
        *weak('S_explicit','weakName','n_explicit_name','explicit_name'),
        'S_explicit.USERCONSTANTS = S_ready.USERCONSTANTS',
        '$test_outputs(S_explicit.EVENTS) = ' + term(second),
        *converted('S_explicit_returned','S_explicit','INTRINSIC_DEFINED','n_explicit_name','V102_EXPLICIT'),
        'S_explicit_returned.STORE[n_name_cv] = DEFINED PNULL',
        'S_explicit_returned.STORE[n_call_cv] = DEFINED pvalue_current_call',
        'S_explicit_returned.STORE[n_strings_cv] = DEFINED (PINT 2)',
        'S_explicit_returned.STORE[n_deaths_cv] = DEFINED (PINT 1)',
        'S_explicit_returned.USERCONSTANTS = S_ready.USERCONSTANTS',
        '~$dynamic_constant_exists(S_explicit_returned,$ptascii("V102_EXPLICIT"))',
        '$test_outputs(S_explicit_returned.EVENTS) = ' + term(returned),
        'S_explicit_finish = $dynamic_query_string_finish(S_explicit_returned,pconfigcall_S_explicit,pvalue_S_explicit_returned)',
        'S_explicit_finish.TODO = ptask_S_explicit*',
        'S_explicit_finish.RESULT = KNOWN (PBOOL false)',
        'S_explicit_finish.USERCONSTANTS = S_ready.USERCONSTANTS',
        '$task_nodes(CONFIG_STRING_RESULT pconfigcall_S_explicit n_explicit_name porigin_child_S_explicit_returned z_child_S_explicit_returned pconfigcall_S_explicit.LINE) = [HOBJECT n_explicit_name,HOBJECT n_has,HOBJECT n_explicit_name]',
        '$eager_task_inputs(S_explicit_returned,CONFIG_STRING_RESULT pconfigcall_S_explicit n_explicit_name porigin_child_S_explicit_returned z_child_S_explicit_returned pconfigcall_S_explicit.LINE) = [HOBJECT n_explicit_name,HOBJECT n_explicit_name,HOBJECT n_has]',
        *reach('S_explicit_drop','S_explicit_returned','INTRINSIC_DEFINED',5),
        'S_explicit_drop.TODO = (DESTRUCTOR_ENTER pdestructorcall_explicit) :: ptask_explicit_drop*',
        'pdestructorcall_explicit.OBJECT = n_explicit_name',
        '$destructor_call_valid(S_explicit_drop,pdestructorcall_explicit)',
        '$weakref_get(S_explicit_drop,n_weak_has) = POBJECT n_has',
        'S_explicit_drop.STORE[n_deaths_cv] = DEFINED (PINT 1)',
        'S_explicit_drop.USERCONSTANTS = S_ready.USERCONSTANTS',
        '$test_outputs(S_explicit_drop.EVENTS) = ' + term(returned),
        *define.finish('S_explicit_drop',stdout),
        'S_final.USERCONSTANTS = [puserconstant_first,puserconstant_second]',
        'puserconstant_second.NAME = $ptascii("V102_EXPLICIT")',
        'puserconstant_second.VALUE = PINT 17', 'puserconstant_second.CLASS = PVSCALAR',
        'S_final.SELECTEDCALLS = eps', 'S_final.SELECTSEQ = 0']
    for node in ['n_reader','n_name','n_weak_read','n_weak_name',
            'n_has','n_explicit_name','n_weak_has','n_weak_explicit_name']:
        values += [f'~(HOBJECT {node} <- S_final.ALLOCATIONS)']
    # Result-domain projections are not driven as source states.
    for index,value in enumerate(['PSTRING ' + text('A::B'),
            'PSTRING ' + text('__COMPILER_HALT_OFFSET__'),'PSTRING [65,0,66]','PINT 0']):
        values += [f'S_refused_{index} = $dynamic_query_string_finish(S_returned,pconfigcall_S,{value})',
            f'S_refused_{index}.COMPLETION = UNSUPPORTED "Stringable query global name"',
            f'S_refused_{index}.EVENTS = S_returned.EVENTS',
            f'S_refused_{index}.ALLOCATIONS = S_returned.ALLOCATIONS']
    return values


def strict(initial, stdout):
    before = b'B|N|held|'
    caught = before + (b'E|defined(): Argument #1 ($constant_name) must be of type string, '
        b'V102StrictName given|35|none|defined|rawO|calleeGone|nameHeld|null|constant|97|1|0|X|')
    assert stdout == caught + b'D|gone|nameGone|23|A|'
    values = [*initial, *front('S','S_initial','INTRINSIC_DEFINED','n_has','n_name',35),
        '$config_strict(S,pconfigcall_S)', '~$config_string_launch(S,pconfigcall_S)',
        *weak('S','weak','n_has','has'), *weak('S','weakName','n_name','name'),
        *[f'$lookup(S.ENV,{text(name)}) = (n_{name}_cv)' for name in [
            'call','name','effects','deaths','result']],
        'S.STORE[n_call_cv] = DEFINED pvalue_current_call',
        '$string_bytes(pvalue_current_call) = ($ptascii("constant"))',
        'S.STORE[n_name_cv] = DEFINED PNULL',
        'S.STORE[n_effects_cv] = DEFINED (PINT 1)',
        'S.STORE[n_deaths_cv] = DEFINED (PINT 0)',
        'S.STORE[n_result_cv] = DEFINED (PINT 97)',
        'S.USERCONSTANTS = eps', '$test_outputs(S.EVENTS) = ' + term(before),
        *controls('S','n_has'), *budget('S'),
        *common.step('S_error_pending','S'), *common.public('S_error_pending'),
        'S_error_pending.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_error) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_error) :: ptask_S*',
        'pdestructionoperation_error.PENDING = (n_error)',
        '$weakref_get(S_error_pending,n_weak_has) = POBJECT n_has',
        *settle('S_error','S_error_pending'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_S*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "TypeError"',
        'pthrowable.ORIGIN = (pconfigcall_S.SITE)',
        '$throwable_chain_valid(S_error,n_error)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('defined(): Argument #1 ($constant_name) must be of type string, V102StrictName given') + ')',
        '$throwable_field(S_error,n_error,"line") = PINT 35',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api))]',
        '$trace_array_field(S_error,n_api,$ptascii("function")) = PSTRING ($ptascii("defined"))',
        '$trace_array_field(S_error,n_api,$ptascii("args")) = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_name))]',
        '~(HOBJECT n_has <- S_error.ALLOCATIONS)',
        '$weakref_get(S_error,n_weak_has) = PNULL',
        '$weakref_get(S_error,n_weak_name) = POBJECT n_name',
        'S_error.STORE[n_result_cv] = DEFINED (PINT 97)',
        'S_error.STORE[n_deaths_cv] = DEFINED (PINT 0)',
        'S_error.USERCONSTANTS = eps', 'S_error.EVENTS = S.EVENTS',
        *reach('S_caught','S_error','INTRINSIC_DEFINED',6),
        '$weakref_get(S_caught,n_weak_name) = POBJECT n_name',
        'S_caught.STORE[n_deaths_cv] = DEFINED (PINT 0)',
        'S_caught.USERCONSTANTS = eps', '$test_outputs(S_caught.EVENTS) = ' + term(caught),
        *reach('S_drop','S_caught','INTRINSIC_DEFINED',5),
        'S_drop.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_drop*',
        'pdestructorcall.OBJECT = n_name', '$destructor_call_valid(S_drop,pdestructorcall)',
        '$weakref_get(S_drop,n_weak_has) = PNULL',
        '~(HOBJECT n_error <- S_drop.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_drop.ALLOCATIONS)',
        'S_drop.STORE[n_deaths_cv] = DEFINED (PINT 0)',
        '$test_outputs(S_drop.EVENTS) = ' + term(caught), *budget('S_drop'),
        *reach('S_recover','S_drop','INTRINSIC_CONSTANT',4),
        'S_recover.TODO = (CONFIG_INVOKE pconfigcall_recover) :: ptask_recover*',
        'pconfigcall_recover.OWNER = (n_reader)',
        'pconfigcall_recover.SENT = [NAMED_SENT (KNOWN pvalue_name)]',
        '$string_bytes(pvalue_name) = ($ptascii("V102_STRICT"))',
        'S_recover.USERCONSTANTS = [puserconstant]',
        'puserconstant.NAME = $ptascii("V102_STRICT")',
        'puserconstant.VALUE = PINT 23', 'puserconstant.CLASS = PVSCALAR',
        'S_recover.STORE[n_deaths_cv] = DEFINED (PINT 1)',
        'S_recover.STORE[n_result_cv] = DEFINED (PINT 97)',
        '$weakref_get(S_recover,n_weak_name) = PNULL',
        '~(HOBJECT n_name <- S_recover.ALLOCATIONS)',
        '$test_outputs(S_recover.EVENTS) = ' + term(caught + b'D|gone|nameGone|'),
        *common.step('S_value_pending','S_recover'),
        *settle('S_value','S_value_pending','PINT 23'),
        'S_value.USERCONSTANTS = S_recover.USERCONSTANTS',
        *define.finish('S_value',stdout),
        'S_final.USERCONSTANTS = S_recover.USERCONSTANTS',
        'S_final.SELECTEDCALLS = eps', 'S_final.SELECTSEQ = 0']
    for node in ['HOBJECT n_has','HOBJECT n_name','HOBJECT n_reader','HOBJECT n_weak_has',
            'HOBJECT n_weak_name','HOBJECT n_error','HARRAY n_trace','HARRAY n_api','HARRAY n_args']:
        values += [f'~({node} <- S_final.ALLOCATIONS)']
    return values


def checks(initial, name, stdout):
    return (order if name == sources.ORDER else strict)(initial,stdout)


base = captured.prior
base.sources, base.checks, base.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, base.prepare
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
