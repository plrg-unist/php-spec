#!/usr/bin/env python3
"""Captured NULL query roots through callbacks, default delivery and reception."""
from pathlib import Path

import constant_owned_query_protocol as captured
import global_constant_null_name_protocol as nulls
import typed_static_invoke_set_protocol as process_base
import constant_owned_null_query_sources as sources

define, packet, common = captured.define, captured.packet, captured.common
ROOT, text, term = captured.ROOT, captured.text, captured.term
PREFIX = captured.PREFIX + nulls.PREFIX + r'''
dec $test_owned_null_deprecated_item(pevent) : nat
def $test_owned_null_deprecated_item(DIAGNOSTIC "Deprecated" preqbytes z) = 1
def $test_owned_null_deprecated_item(pevent) = 0 -- otherwise
dec $test_owned_null_deprecated(pevent*) : nat
def $test_owned_null_deprecated(eps) = 0
def $test_owned_null_deprecated(pevent :: pevent_tail*) = $($test_owned_null_deprecated_item(pevent) + $test_owned_null_deprecated(pevent_tail*))
'''
READ_MESSAGE = 'constant(): Passing null to parameter #1 ($name) of type string is deprecated'
HAS_MESSAGE = 'defined(): Passing null to parameter #1 ($constant_name) of type string is deprecated'


def front(state, start, kind, owner):
    call = 'pconfigcall_' + state
    return [*nulls.reach(state,start,0,kind),
        f'{state}.TODO = (CONFIG_INVOKE {call}) :: ptask_{state}*',
        f'{call}.OWNER = ({owner})', f'{call}.SELECTION = eps',
        f'{call}.PACKS = eps', f'{call}.NAMED', f'{call}.INDEX = 1',
        f'{call}.SENT = [NAMED_SENT (KNOWN PNULL)]',
        f'$config_invoke_valid({state},{call})',
        f'~$dynamic_null_constant_call({call})',
        f'$dynamic_owned_null_query_call({call})',
        f'$dynamic_null_constant_valid({state},{call})',
        *captured.intrinsic(state,owner,kind),
        f'$config_nodes({call}) = [HOBJECT {owner}]',
        f'$heap_owners($heap_graph({state}),HOBJECT {owner}) = 1']


def weak(state, owner, variable, label):
    return [f'$lookup({state}.ENV,{text(variable)}) = (n_weak_cv_{label})',
        f'{state}.STORE[n_weak_cv_{label}] = DEFINED (POBJECT n_weak_{label})',
        f'{state}.OBJECTS[n_weak_{label}] = WEAKREFERENCE ({owner})',
        f'$weakref_get({state},n_weak_{label}) = POBJECT {owner}']


def controls(state, owner):
    call = 'pconfigcall_' + state
    values = [f'S_dead_{state} = {state}[.ALLOCATIONS = $destruction_node_delete({state}.ALLOCATIONS,HOBJECT {owner})]',
        f'~$dynamic_null_constant_valid(S_dead_{state},{call})']
    for change in ['.OWNER = eps', f'.OWNER = (|{state}.OBJECTS|)', '.SELECTION = (0)',
            '.KIND = INTRINSIC_DEFINE', '.INDEX = 0', '.SITE = PORIGIN 0 eps',
            f'.LINE = $({call}.LINE + 1)', f'.NAMED = ~{call}.NAMED']:
        values += [f'~$dynamic_null_constant_valid({state},{call}[{change}])']
    for value in ['PINT 0', 'PBOOL false', 'PSTRING ($ptascii(""))', 'PARRAY 0', 'POBJECT 0']:
        values += [f'~$dynamic_owned_null_query_call({call}[.SENT = [NAMED_SENT (KNOWN ({value}))]])']
    values += [f'pconfigpack_{state} = {{INDEX 0,SITE {call}.SITE,LINE {call}.LINE,ARRAY 0,ITEMS eps}}',
        f'~$dynamic_owned_null_query_call({call}[.PACKS = [pconfigpack_{state}]])']
    return values


def handler(state, start, original, kind, owner, weak_name):
    call = 'pconfigcall_' + original
    return [*nulls.reach(state,start,1,kind),
        f'{state}.CURRENT = (pcallcontext_{state})',
        f'$error_context_call({state},pcallcontext_{state}) = (perrorcall_{state})',
        f'perrorcall_{state}.RESUME = DYNAMIC_NULL_CONSTANT_RESULT {call}',
        f'$error_context_valid({state},pcallcontext_{state})',
        f'$error_context_trigger({state},pcallcontext_{state}) = ({call})',
        f'$error_handler_trace_values({state},pcallcontext_{state},{call}) = [PNULL]',
        f'$heap_owners($heap_graph({state}),HOBJECT {owner}) = 1',
        f'$weakref_get({state},{weak_name}) = POBJECT {owner}']


def budget(state):
    return [f'{state}_pause = $drive_steps({state},0)',
        f'{state}_pause = {state}[.COMPLETION = BUDGET]',
        f'$drive_steps($test_running({state}_pause),1) = $drive_steps({state},1)']


def error(state, before, original, kind, message, invoke):
    call = 'pconfigcall_' + original
    values = [*common.step(state,before), *common.public(state),
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
        f'$trace_array_field({state},n_api_{state},$ptascii("function")) = PSTRING ($ptascii("constant"))',
        f'$trace_array_field({state},n_api_{state},$ptascii("args")) = PARRAY n_api_args_{state}',
        f'{state}.EVENTS = {before}.EVENTS']
    if invoke:
        values += [f'$trace_array_field({state},n_invoke_{state},$ptascii("function")) = PSTRING ($ptascii("__invoke"))',
            f'$trace_array_field({state},n_invoke_{state},$ptascii("class")) = PSTRING ($ptascii("Closure"))',
            f'$trace_array_field({state},n_invoke_{state},$ptascii("args")) = PARRAY n_invoke_args_{state}']
    return values


def returning(initial, stdout):
    before = b'B|N|held|'
    first = before + b'H|8192|' + READ_MESSAGE.encode() + b'|27|held|'
    second = first + b'101|gone|handler|constant|1|N|held|'
    resumed = second + b'H|8192|' + HAS_MESSAGE.encode() + b'|35|held|'
    assert stdout == resumed + b'T|gone|handler|constant|2|101|A|'
    values = [*initial, *front('S','S_initial','INTRINSIC_CONSTANT','n_reader'),
        'pconfigcall_S.LINE = 27', '~$config_strict(S,pconfigcall_S)',
        *weak('S','n_reader','weakRead','read'),
        '$lookup(S.ENV,$ptascii("call")) = (n_call)',
        '$lookup(S.ENV,$ptascii("name")) = (n_name)',
        '$lookup(S.ENV,$ptascii("hits")) = (n_hits)',
        'S.STORE[n_call] = DEFINED PNULL',
        'S.STORE[n_name] = DEFINED pvalue_argument',
        '$string_bytes(pvalue_argument) = ($ptascii("argument"))',
        'S.STORE[n_hits] = DEFINED (PINT 0)',
        'S.USERCONSTANTS = eps', 'S.SELECTEDCALLS = eps', 'S.SELECTSEQ = 0',
        '$test_outputs(S.EVENTS) = ' + term(before), *controls('S','n_reader'),
        *nulls.warning('S_warning','S'), *budget('S_warning'),
        *handler('S_handler','S_warning','S','INTRINSIC_CONSTANT','n_reader','n_weak_read'),
        *nulls.resume('S_resume','S_handler','S','INTRINSIC_CONSTANT'),
        'S_resume.USERCONSTANTS = [puserconstant_empty]',
        'puserconstant_empty.NAME = eps', 'puserconstant_empty.VALUE = PINT 101',
        'puserconstant_empty.CLASS = PVSCALAR',
        '$dynamic_define_source(S_resume,puserconstant_empty.ORIGIN)',
        'S_resume.STORE[n_call] = DEFINED pvalue_current_call',
        '$string_bytes(pvalue_current_call) = ($ptascii("constant"))',
        'S_resume.STORE[n_name] = DEFINED pvalue_current_name',
        '$string_bytes(pvalue_current_name) = ($ptascii("handler"))',
        'S_resume.STORE[n_hits] = DEFINED (PINT 1)',
        '$weakref_get(S_resume,n_weak_read) = POBJECT n_reader',
        '$heap_owners($heap_graph(S_resume),HOBJECT n_reader) = 1',
        '$test_outputs(S_resume.EVENTS) = ' + term(first),
        '$test_owned_null_deprecated(S_resume.EVENTS) = 0', *budget('S_resume'),
        *common.step('S_value','S_resume','PINT 101'),
        'S_value.TODO = ptask_S_resume*',
        'S_value.USERCONSTANTS = S_resume.USERCONSTANTS',
        '~(HOBJECT n_reader <- S_value.ALLOCATIONS)',
        '$weakref_get(S_value,n_weak_read) = PNULL',
        *front('S_has','S_value','INTRINSIC_DEFINED','n_has'),
        'pconfigcall_S_has.LINE = 35', '~$config_strict(S_has,pconfigcall_S_has)',
        *weak('S_has','n_has','weakHas','has'),
        'S_has.USERCONSTANTS = S_resume.USERCONSTANTS',
        'S_has.STORE[n_call] = DEFINED PNULL',
        'S_has.STORE[n_name] = DEFINED pvalue_argument',
        'S_has.STORE[n_hits] = DEFINED (PINT 1)',
        '$test_outputs(S_has.EVENTS) = ' + term(second),
        *nulls.warning('S_has_warning','S_has'),
        *handler('S_has_handler','S_has_warning','S_has','INTRINSIC_DEFINED','n_has','n_weak_has'),
        *nulls.resume('S_has_resume','S_has_handler','S_has','INTRINSIC_DEFINED'),
        'S_has_resume.USERCONSTANTS = S_resume.USERCONSTANTS',
        'S_has_resume.STORE[n_hits] = DEFINED (PINT 2)',
        '$weakref_get(S_has_resume,n_weak_has) = POBJECT n_has',
        '$heap_owners($heap_graph(S_has_resume),HOBJECT n_has) = 1',
        '$test_outputs(S_has_resume.EVENTS) = ' + term(resumed),
        '$test_owned_null_deprecated(S_has_resume.EVENTS) = 0',
        *common.step('S_done','S_has_resume','PBOOL true'),
        'S_done.TODO = ptask_S_has_resume*',
        '~(HOBJECT n_has <- S_done.ALLOCATIONS)',
        '$weakref_get(S_done,n_weak_has) = PNULL',
        *define.finish('S_done',stdout),
        'S_final.USERCONSTANTS = S_resume.USERCONSTANTS',
        'S_final.SELECTEDCALLS = eps', 'S_final.SELECTSEQ = 0',
        '$test_owned_null_deprecated(S_final.EVENTS) = 0',
        '~(HOBJECT n_reader <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_has <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_weak_read <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_weak_has <- S_final.ALLOCATIONS)']
    return values


def strict(initial, stdout):
    before = b'B|N|held|'
    explicit = before + (b'T|constant(): Argument #1 ($name) must be of type string, null given|32|'
        b'constant|rawN|null|argument|97|1|0|gone|N|held|')
    resumed = explicit + b'H|8192|' + READ_MESSAGE.encode() + b'|48|held|'
    assert stdout == resumed + (b'E|Undefined constant ""|48|none|constant|__invoke|apiS|invokeN|distinct|'
        b'keptN|handler|defined|97|2|1|gone|A|')
    values = [*initial, *front('S','S_initial','INTRINSIC_CONSTANT','n_a'),
        'pconfigcall_S.LINE = 32', '$config_strict(S,pconfigcall_S)',
        '~$call_task_valid(S,DYNAMIC_NULL_CONSTANT_RESULT pconfigcall_S)',
        *weak('S','n_a','weakStrict','a'),
        '$lookup(S.ENV,$ptascii("call")) = (n_call)',
        '$lookup(S.ENV,$ptascii("name")) = (n_name)',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)',
        '$lookup(S.ENV,$ptascii("calls")) = (n_calls)',
        '$lookup(S.ENV,$ptascii("hits")) = (n_hits)',
        'S.STORE[n_call] = DEFINED PNULL', 'S.STORE[n_result] = DEFINED (PINT 97)',
        'S.STORE[n_calls] = DEFINED (PINT 1)', 'S.STORE[n_hits] = DEFINED (PINT 0)',
        '$test_outputs(S.EVENTS) = ' + term(before), *controls('S','n_a'), *budget('S'),
        *error('S_type','S','S','TypeError','constant(): Argument #1 ($name) must be of type string, null given',False),
        'S_type.ARRAYS[n_api_args_S_type].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL)]',
        'S_type.STORE[n_result] = DEFINED (PINT 97)',
        'S_type.STORE[n_hits] = DEFINED (PINT 0)',
        '~(HOBJECT n_a <- S_type.ALLOCATIONS)', '$weakref_get(S_type,n_weak_a) = PNULL',
        '$test_owned_null_deprecated(S_type.EVENTS) = 0',
        *front('S_explicit','S_type','INTRINSIC_CONSTANT','n_b'),
        'pconfigcall_S_explicit.LINE = 48', '$exit_strict(S_explicit,pconfigcall_S_explicit.SITE)',
        '$config_method_receiver(S_explicit,pconfigcall_S_explicit)',
        '~$config_strict(S_explicit,pconfigcall_S_explicit)',
        *weak('S_explicit','n_b','weakExplicit','b'),
        'S_explicit.STORE[n_call] = DEFINED PNULL',
        'S_explicit.STORE[n_result] = DEFINED (PINT 97)',
        'S_explicit.STORE[n_calls] = DEFINED (PINT 2)',
        'S_explicit.STORE[n_hits] = DEFINED (PINT 0)',
        '$test_outputs(S_explicit.EVENTS) = ' + term(explicit),
        *nulls.warning('S_warning','S_explicit'),
        *handler('S_handler','S_warning','S_explicit','INTRINSIC_CONSTANT','n_b','n_weak_b'),
        *nulls.resume('S_resume','S_handler','S_explicit','INTRINSIC_CONSTANT'),
        'S_resume.USERCONSTANTS = eps',
        'S_resume.STORE[n_call] = DEFINED pvalue_current_call',
        '$string_bytes(pvalue_current_call) = ($ptascii("defined"))',
        'S_resume.STORE[n_name] = DEFINED pvalue_current_name',
        '$string_bytes(pvalue_current_name) = ($ptascii("handler"))',
        'S_resume.STORE[n_hits] = DEFINED (PINT 1)',
        '$weakref_get(S_resume,n_weak_b) = POBJECT n_b',
        '$heap_owners($heap_graph(S_resume),HOBJECT n_b) = 1',
        '$test_outputs(S_resume.EVENTS) = ' + term(resumed),
        '$test_owned_null_deprecated(S_resume.EVENTS) = 1',
        'S_resume.EVENTS[$nabs($(|S_resume.EVENTS| - 1))] = DIAGNOSTIC "Deprecated" $dynamic_null_constant_message(pconfigcall_S_explicit) 48',
        *budget('S_resume'),
        'S_received = $typed_apply(S_resume[.TODO = (CONFIG_INVOKE pconfigcall_S_explicit) :: ptask_S_resume*],TYPESTRING PNULL,48)',
        'S_received.RESULT = KNOWN pvalue_received', '$string_bytes(pvalue_received) = (eps)',
        '$string_carrier_valid(S_received,pvalue_received)',
        *error('S_error','S_resume','S_explicit','Error','Undefined constant ""',True),
        'S_error.ARRAYS[n_api_args_S_error].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_received)]',
        'S_error.ARRAYS[n_invoke_args_S_error].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL)]',
        '$strict_check(S_error,PARRAY n_api_args_S_error,PARRAY n_invoke_args_S_error,eps) = COMPARED false',
        'S_error.STORE[n_result] = DEFINED (PINT 97)',
        '$entry_lookup(S_error.ARRAYS[n_api_args_S_type].ITEMS,KINT 0) = (DIRECT PNULL)',
        '~(HOBJECT n_b <- S_error.ALLOCATIONS)', '$weakref_get(S_error,n_weak_b) = PNULL',
        *define.finish('S_error',stdout),
        'S_final.USERCONSTANTS = eps', 'S_final.SELECTEDCALLS = eps', 'S_final.SELECTSEQ = 0',
        '$test_owned_null_deprecated(S_final.EVENTS) = 1']
    for node in ['HOBJECT n_a','HOBJECT n_b','HOBJECT n_weak_a','HOBJECT n_weak_b',
            'HOBJECT n_error_S_type','HOBJECT n_error_S_error','HARRAY n_trace_S_type',
            'HARRAY n_api_args_S_type','HARRAY n_trace_S_error','HARRAY n_api_args_S_error',
            'HARRAY n_invoke_args_S_error']:
        values += [f'~({node} <- S_final.ALLOCATIONS)']
    return values


def checks(initial, name, stdout):
    return (returning if name == sources.RETURN else strict)(initial,stdout)


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
