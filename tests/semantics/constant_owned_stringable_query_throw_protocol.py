#!/usr/bin/env python3
"""Pending ordinary lookup and completed explicit cleanup keep distinct traces."""
from pathlib import Path

import constant_owned_stringable_query_protocol as prior
import typed_static_invoke_set_protocol as process_base
import constant_owned_stringable_query_throw_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
PREFIX = prior.PREFIX + r'''
dec $test_query_throw_front(pstate, nat) : bool
def $test_query_throw_front(S,0) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
def $test_query_throw_front(S,1) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call
  -- if $dynamic_owned_query_string_call(pconfigcall)
  -- if pdestructionoperation.PENDING =/= eps
def $test_query_throw_front(S,2) = true
  -- if S.TODO = (THROW_SEARCH n_exception) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.DESTRUCTION.RELEASES = eps /\ S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.CALLS = eps
def $test_query_throw_front(S,3) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_name) metadata_name) :: expression_tail*
  -- if $base64(text_name) = $ptascii("provided")
def $test_query_throw_front(S,4) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.OWNER =/= eps
  -- if $dynamic_owned_global_query_valid(S,pconfigcall)
def $test_query_throw_front(S,n_phase) = false -- otherwise
dec $test_query_throw_seek(pstate, nat, nat) : pstate
def $test_query_throw_seek(S,n_phase,0) = S
def $test_query_throw_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_query_throw_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_query_throw_seek(S,n_phase,n) = $test_query_throw_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_query_throw_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_query_throw_seek({start},{phase},3500)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_query_throw_front({state},{phase})', *common.public(state)]


def trace(state, explicit, class_name, call_line):
    values = [f'$throwable_field({state},n_exception,"trace") = PARRAY n_trace',
        f'{state}.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_destructor_frame))'
            + (']' if explicit else ',ENTRY (KINT 1) (DIRECT (PARRAY n_api_frame))]'),
        f'$trace_array_field({state},n_destructor_frame,$ptascii("function")) = PSTRING ($ptascii("__destruct"))',
        f'$trace_array_field({state},n_destructor_frame,$ptascii("class")) = PSTRING ({text(class_name)})',
        f'$trace_array_field({state},n_destructor_frame,$ptascii("args")) = PARRAY n_destructor_args',
        f'{state}.ARRAYS[n_destructor_args].ITEMS = eps']
    if explicit:
        values += [f'$trace_array_field({state},n_destructor_frame,$ptascii("file")) = PSTRING ($call_sourcefile({state}.FILES,pconfigcall_S.SITE))',
            f'$trace_array_field({state},n_destructor_frame,$ptascii("line")) = PINT {call_line}']
    else:
        values += [f'$entry_lookup({state}.ARRAYS[n_destructor_frame].ITEMS,KSTRING ($ptascii("file"))) = eps',
            f'$entry_lookup({state}.ARRAYS[n_destructor_frame].ITEMS,KSTRING ($ptascii("line"))) = eps',
            f'$trace_array_field({state},n_api_frame,$ptascii("function")) = PSTRING ($ptascii("constant"))',
            f'$trace_array_field({state},n_api_frame,$ptascii("file")) = PSTRING ($call_sourcefile({state}.FILES,pconfigcall_S.SITE))',
            f'$trace_array_field({state},n_api_frame,$ptascii("line")) = PINT {call_line}',
            f'$trace_array_field({state},n_api_frame,$ptascii("args")) = PARRAY n_raw_args',
            f'{state}.ARRAYS[n_raw_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_name))]']
    return values


def checks(initial, name, stdout):
    explicit = name == sources.EXPLICIT
    key = 'V103_EXPLICIT' if explicit else 'V103_RETURN'
    class_name = 'V103ExplicitName' if explicit else 'V103ReturnName'
    kind = 'INTRINSIC_DEFINED' if explicit else 'INTRINSIC_CONSTANT'
    call_line, made_line, value = (33,19,23) if explicit else (32,18,17)
    current_call = 'constant' if explicit else 'defined'
    converted, destructed = b'B|S|held|', b'B|S|held|D|held|'
    caught = destructed + (b'Exception|same|V103_EXPLICIT_D|19|none|__destruct|noCaller|noArg|end|'
        b'file0|33|internal1|-1|calleeGone|nameGone|null|constant|97|1|1|' if explicit else
        b'Exception|same|V103_RETURN_D|18|none|__destruct|constant|rawO|end|'
        b'internal0|-1|file1|32|calleeGone|nameHeld|null|defined|97|1|1|')
    released = caught + b'released|1|'
    assert stdout == released + str(value).encode() + b'|A|'
    values = [*initial, *prior.front('S','S_initial',kind,'n_callee','n_name',call_line,explicit),
        f'{"" if explicit else "~"}$exit_strict(S,pconfigcall_S.SITE)',
        '~$config_strict(S,pconfigcall_S)',
        *prior.weak('S','weakCall','n_callee','call'),
        *prior.weak('S','weakName','n_name','name'),
        *[f'$lookup(S.ENV,{text(var)}) = (n_{var}_cv)' for var in [
            'call','name','provided','casts','drops','result']],
        'S.STORE[n_provided_cv] = DEFINED PNULL',
        'S.STORE[n_casts_cv] = DEFINED (PINT 0)',
        'S.STORE[n_drops_cv] = DEFINED (PINT 0)',
        'S.STORE[n_result_cv] = DEFINED (PINT 97)',
        'S.USERCONSTANTS = eps', 'S.SELECTEDCALLS = eps', 'S.SELECTSEQ = 0',
        '$test_outputs(S.EVENTS) = ' + term(b'B|'),
        *prior.converted('S_returned','S',kind,'n_name',key),
        'S_returned.STORE[n_call_cv] = DEFINED pvalue_current_call',
        f'$string_bytes(pvalue_current_call) = ({text(current_call)})',
        'S_returned.STORE[n_name_cv] = DEFINED PNULL',
        'S_returned.STORE[n_casts_cv] = DEFINED (PINT 1)',
        'S_returned.STORE[n_drops_cv] = DEFINED (PINT 0)',
        'S_returned.STORE[n_result_cv] = DEFINED (PINT 97)',
        'S_returned.USERCONSTANTS = eps',
        '$test_outputs(S_returned.EVENTS) = ' + term(converted),
        *prior.reach('S_enter','S_returned',kind,5),
        'S_enter.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_enter*',
        'pdestructorcall.OBJECT = n_name', 'pdestructorcall.CALLER = eps',
        'pdestructorcall.OPERATION = (pdestructionoperation_before)',
        'pdestructionoperation_before.SOURCE = CONFIG_STRING_RESULT pconfigcall_S n_name porigin_child_S_returned z_child_S_returned pconfigcall_S.LINE',
        'pdestructionoperation_before.PENDING = eps',
        'pdestructorcall.USER', '$destructor_call_valid(S_enter,pdestructorcall)',
        '$weakref_get(S_enter,n_weak_call) = POBJECT n_callee',
        '$weakref_get(S_enter,n_weak_name) = POBJECT n_name',
        'S_enter.STORE[n_drops_cv] = DEFINED (PINT 0)',
        'S_enter.STORE[n_provided_cv] = DEFINED PNULL',
        '$test_outputs(S_enter.EVENTS) = ' + term(converted)]
    if explicit:
        values += ['pdestructionoperation_before.VALUE = KNOWN (PBOOL false)',
            'pdestructorcall.SITE = (pconfigcall_S.SITE)',
            '$destructor_callsite(pdestructorcall) = (pconfigcall_S.SITE)',
            f'$destructor_line(pdestructorcall) = {call_line}',
            '$dynamic_query_string_release_invoke(S_enter.TODO,pdestructionoperation_before) = eps',
            '~$dynamic_query_string_release_valid(S_enter,pdestructionoperation_before,pconfigcall_received_S_returned)']
    else:
        values += ['pdestructionoperation_before.VALUE = KNOWN PNULL',
            'pdestructorcall.SITE = eps', '$destructor_callsite(pdestructorcall) = eps',
            '$destructor_line(pdestructorcall) = $(-1)',
            '$dynamic_query_string_release_invoke(S_enter.TODO,pdestructionoperation_before) = (pconfigcall_received_S_returned)',
            '$dynamic_query_string_release_valid(S_enter,pdestructionoperation_before,pconfigcall_received_S_returned)']
    values += [*reach('S_throw','S_enter',0),
        'S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_throw*',
        'S_throw.CURRENT = (pcallcontext_destructor)',
        '$destructor_context_valid(S_throw,pcallcontext_destructor)',
        'S_throw.STORE[n_provided_cv] = DEFINED (POBJECT n_exception)',
        'S_throw.OBJECTS[n_exception] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        f'$string_bytes($throwable_field(S_throw,n_exception,"message")) = ({text(key + "_D")})',
        f'$throwable_field(S_throw,n_exception,"line") = PINT {made_line}',
        '$throwable_field(S_throw,n_exception,"previous") = PNULL',
        '$throwable_chain_valid(S_throw,n_exception)', *trace('S_throw',explicit,class_name,call_line),
        'S_throw.USERCONSTANTS = [puserconstant]',
        f'puserconstant.NAME = {text(key)}', f'puserconstant.VALUE = PINT {value}',
        'puserconstant.CLASS = PVSCALAR', '$dynamic_define_source(S_throw,puserconstant.ORIGIN)',
        'S_throw.STORE[n_drops_cv] = DEFINED (PINT 1)',
        'S_throw.STORE[n_casts_cv] = DEFINED (PINT 1)',
        'S_throw.STORE[n_result_cv] = DEFINED (PINT 97)',
        'n_name <- S_throw.DESTRUCTION.CALLED',
        '$weakref_get(S_throw,n_weak_call) = POBJECT n_callee',
        '$test_outputs(S_throw.EVENTS) = ' + term(destructed), *prior.budget('S_throw'),
        *reach('S_pending','S_throw',1),
        'S_pending.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_pending*',
        'pdestructionoperation.PENDING = (n_exception)',
        'pdestructionoperation.SOURCE = pdestructionoperation_before.SOURCE',
        'pdestructionoperation.COMPLETION = NORMAL',
        'S_pending.CURRENT = eps', 'S_pending.FRAMES = eps',
        'S_pending.DESTRUCTION.RELEASES = eps', 'S_pending.DESTRUCTION.CALLS = eps',
        '$call_task_valid(S_pending,DESTRUCTOR_OPERATION_EXIT pdestructionoperation)',
        'S_pending.USERCONSTANTS = S_throw.USERCONSTANTS',
        'S_pending.STORE[n_result_cv] = DEFINED (PINT 97)',
        '$test_outputs(S_pending.EVENTS) = ' + term(destructed), *prior.budget('S_pending')]
    if explicit:
        values += ['S_pending.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_S*',
            'pdestructionoperation.VALUE = KNOWN (PBOOL false)',
            '$dynamic_query_string_release_invoke(S_pending.TODO,pdestructionoperation) = eps',
            '~$dynamic_query_string_release_valid(S_pending,pdestructionoperation,pconfigcall_received_S_returned)',
            '~(HOBJECT n_callee <- S_pending.ALLOCATIONS)',
            '~(HOBJECT n_name <- S_pending.ALLOCATIONS)',
            '$weakref_get(S_pending,n_weak_call) = PNULL',
            '$weakref_get(S_pending,n_weak_name) = PNULL',
            '$destructor_trace_suffix(S_throw,pcallcontext_destructor) = eps']
    else:
        values += ['S_pending.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (CONFIG_INVOKE pconfigcall_received_S_returned) :: ptask_S*',
            'pdestructionoperation.VALUE = KNOWN PNULL',
            '$dynamic_query_string_release_invoke(S_pending.TODO,pdestructionoperation) = (pconfigcall_received_S_returned)',
            '$dynamic_query_string_release_valid(S_pending,pdestructionoperation,pconfigcall_received_S_returned)',
            '$dynamic_owned_global_query_valid(S_pending,pconfigcall_received_S_returned)',
            '$weakref_get(S_pending,n_weak_call) = POBJECT n_callee',
            '$weakref_get(S_pending,n_weak_name) = POBJECT n_name',
            '$heap_owners($heap_graph(S_pending),HOBJECT n_name) = 1']
    values += [*reach('S_error','S_pending',2),
        'S_error.TODO = (THROW_SEARCH n_exception) :: ptask_S*',
        '$throwable_field(S_error,n_exception,"previous") = PNULL',
        *trace('S_error',explicit,class_name,call_line),
        '~(HOBJECT n_callee <- S_error.ALLOCATIONS)',
        '$weakref_get(S_error,n_weak_call) = PNULL',
        'S_error.STORE[n_result_cv] = DEFINED (PINT 97)',
        'S_error.STORE[n_drops_cv] = DEFINED (PINT 1)',
        'S_error.USERCONSTANTS = S_throw.USERCONSTANTS',
        '$test_outputs(S_error.EVENTS) = ' + term(destructed),
        *reach('S_caught','S_error',3),
        '$lookup(S_caught.ENV,$ptascii("error")) = (n_error_cv)',
        '$lookup(S_caught.ENV,$ptascii("trace")) = (n_trace_cv)',
        'S_caught.STORE[n_error_cv] = DEFINED (POBJECT n_exception)',
        'S_caught.STORE[n_provided_cv] = DEFINED (POBJECT n_exception)',
        'S_caught.STORE[n_trace_cv] = DEFINED (PARRAY n_trace)',
        '$test_outputs(S_caught.EVENTS) = ' + term(caught),
        *reach('S_read','S_caught',4),
        'S_read.TODO = (CONFIG_INVOKE pconfigcall_read) :: ptask_read*',
        'pconfigcall_read.OWNER = (n_reader)', 'n_reader =/= n_callee',
        'pconfigcall_read.SENT = [NAMED_SENT (KNOWN pvalue_read)]',
        f'$string_bytes(pvalue_read) = ({text(key)})',
        '$dynamic_owned_global_query_valid(S_read,pconfigcall_read)',
        '~(HOBJECT n_name <- S_read.ALLOCATIONS)', '~(HOBJECT n_exception <- S_read.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_read.ALLOCATIONS)',
        '$weakref_get(S_read,n_weak_name) = PNULL',
        'S_read.STORE[n_drops_cv] = DEFINED (PINT 1)',
        'S_read.STORE[n_casts_cv] = DEFINED (PINT 1)',
        'S_read.STORE[n_result_cv] = DEFINED (PINT 97)',
        'S_read.USERCONSTANTS = S_throw.USERCONSTANTS',
        '$test_outputs(S_read.EVENTS) = ' + term(released),
        *common.step('S_value_pending','S_read'),
        *prior.settle('S_value','S_value_pending',f'PINT {value}'),
        'S_value.TODO = ptask_read*', *define.finish('S_value',stdout),
        'S_final.USERCONSTANTS = S_throw.USERCONSTANTS',
        'S_final.SELECTEDCALLS = eps', 'S_final.SELECTSEQ = 0']
    for node in ['HOBJECT n_callee','HOBJECT n_name','HOBJECT n_reader','HOBJECT n_exception',
            'HOBJECT n_weak_call','HOBJECT n_weak_name','HARRAY n_trace','HARRAY n_destructor_args']:
        values += [f'~({node} <- S_final.ALLOCATIONS)']
    if not explicit:
        values += ['~(HARRAY n_raw_args <- S_final.ALLOCATIONS)']
    return values


base = prior.base
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
