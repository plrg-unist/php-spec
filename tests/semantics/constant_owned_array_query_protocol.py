#!/usr/bin/env python3
"""Captured ARRAY TypeErrors preserve runtime payloads through trace COW."""
from pathlib import Path

import constant_owned_nonstringable_query_protocol as prior
import typed_static_invoke_set_protocol as process_base
import constant_owned_array_query_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
lifetime = prior.prior
PREFIX = prior.PREFIX + r'''
dec $test_owned_array_front(pstate, pintrinsic) : bool
def $test_owned_array_front(S,pintrinsic) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = pintrinsic /\ $dynamic_owned_query_array_call(pconfigcall)
def $test_owned_array_front(S,pintrinsic) = false -- otherwise
dec $test_owned_array_seek(pstate, pintrinsic, nat) : pstate
def $test_owned_array_seek(S,pintrinsic,0) = S
def $test_owned_array_seek(S,pintrinsic,n) = S
  -- if $(n > 0)
  -- if $test_owned_array_front(S,pintrinsic) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_owned_array_seek(S,pintrinsic,n) = $test_owned_array_seek($drive_steps($test_running(S),1),pintrinsic,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_owned_array_front(S,pintrinsic)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, kind):
    return [f'{state}_found = $test_owned_array_seek({start},{kind},3000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_owned_array_front({state},{kind})', *common.public(state)]


def variable(state, name, value):
    return [f'$lookup({state}.ENV,{text(name)}) = (n_cv_{name}_{state})',
        f'{state}.STORE[n_cv_{name}_{state}] = DEFINED ({value})']


def payload(state, array, plain, number, value, label):
    return [f'{state}.ARRAYS[{array}].ITEMS = [ENTRY (KSTRING ($ptascii("plain"))) (DIRECT pvalue_{label}),ENTRY (KINT {number}) (DIRECT ({value}))]',
        f'$string_bytes(pvalue_{label}) = ({text(plain)})']


def controls():
    values = ['~$dynamic_query_array_call(pconfigcall_S)',
        'S_dead_callee = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_callee)]',
        '~$dynamic_query_array_valid(S_dead_callee,pconfigcall_S)',
        'S_dead_array = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_input)]',
        '~$dynamic_query_array_valid(S_dead_array,pconfigcall_S)']
    for change in ['.OWNER = eps', '.OWNER = (|S.OBJECTS|)', '.SELECTION = (0)',
            '.KIND = INTRINSIC_DEFINE', '.INDEX = 0', '.SITE = PORIGIN 0 eps',
            '.LINE = $(pconfigcall_S.LINE + 1)', '.NAMED = true', '.SENT = eps',
            '.SENT = pconfigcall_S.SENT ++ pconfigcall_S.SENT']:
        values += [f'~$dynamic_query_array_valid(S,pconfigcall_S[{change}])']
    values += ['pconfigpack_bad = {INDEX 0,SITE pconfigcall_S.SITE,LINE pconfigcall_S.LINE,ARRAY 0,ITEMS eps}',
        '~$dynamic_query_array_valid(S,pconfigcall_S[.PACKS = [pconfigpack_bad]])']
    for value in ['PNULL','PBOOL false','PINT 0','PFLOAT 0','PSTRING ($ptascii(""))',
            'POBJECT n_callee','PARRAY (|S.ARRAYS|)']:
        values += [f'~$dynamic_query_array_valid(S,pconfigcall_S[.SENT = [NAMED_SENT (KNOWN ({value}))]])']
    for item in ['DIRECT (PARRAY n_input)','DIRECT (POBJECT n_callee)',
            'UNINITIALIZED','ALIAS (|S.STORE|)',
            'DIRECT (PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("bad")))']:
        values += [f'~$dynamic_query_array_entries(S,[ENTRY (KINT 0) ({item})])']
    return values


def error_trace(explicit, api, line):
    values = ['S_error.TODO = (THROW_SEARCH n_error) :: ptask_error*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "TypeError"',
        'pthrowable.ORIGIN = (pconfigcall_S.SITE)', '$throwable_chain_valid(S_error,n_error)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = ('
            + text(api+'(): Argument #1 ($'+('constant_name' if explicit else 'name')+') must be of type string, array given') + ')',
        f'$throwable_field(S_error,n_error,"line") = PINT {line}',
        '$string_bytes($throwable_field(S_error,n_error,"file")) = ($call_sourcefile(S.FILES,pconfigcall_S.SITE))',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api))'
            + (',ENTRY (KINT 1) (DIRECT (PARRAY n_invoke))]' if explicit else ']')]
    for frame, function, args in [('n_api',api,'n_args')] + (
            [('n_invoke','__invoke','n_invoke_args')] if explicit else []):
        values += [f'$trace_array_field(S_error,{frame},$ptascii("function")) = PSTRING ({text(function)})',
            f'$trace_array_field(S_error,{frame},$ptascii("file")) = PSTRING ($call_sourcefile(S.FILES,pconfigcall_S.SITE))',
            f'$trace_array_field(S_error,{frame},$ptascii("line")) = PINT {line}',
            f'$trace_array_field(S_error,{frame},$ptascii("args")) = PARRAY {args}',
            f'S_error.ARRAYS[{args}].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_input))]',
            f'$node_children(S_error,HARRAY {args}) = [HARRAY n_input]']
    if explicit:
        values += ['$trace_array_field(S_error,n_invoke,$ptascii("class")) = PSTRING ($ptascii("Closure"))',
            '$trace_array_field(S_error,n_invoke,$ptascii("type")) = PSTRING ($ptascii("->"))',
            'n_args =/= n_invoke_args']
    return values


def checks(initial, name, stdout):
    explicit = name == sources.EXPLICIT
    kind, api, line = ('INTRINSIC_DEFINED','defined',23) if explicit else ('INTRINSIC_CONSTANT','constant',24)
    stem = 'explicit' if explicit else 'strict'
    key, number, slot, value = ('V105_EXPLICIT_RECOVERY',23,5,'PBOOL false') if explicit else ('V105_STRICT_RECOVERY',17,3,'PINT 17')
    before = b'B|N|held|'
    caught = before + (b'E|defined(): Argument #1 ($constant_name) must be of type string, array given|23|'
        b'none|defined|23|apiFile|__invoke|Closure|->|23|invokeFile|explicit-old|end|explicit-old|F|'
        b'calleeGone|currentNull|97|1|explicit-api|explicit-old|FT|explicit-old|traceF|' if explicit else
        b'E|constant(): Argument #1 ($name) must be of type string, array given|24|none|constant|24|file|end|'
        b'strict-old|17|strict-live|strict-old|calleeGone|defined|97|1|strict-raw|strict-live|strict-old|strict-old|')
    raw = caught + (b'R|explicit-api|explicit-old|' if explicit else b'R|strict-raw|17|')
    last = raw + (b'I|explicit-old|' if explicit else b'')
    assert stdout == last + str(number).encode() + b'|A|'
    values = [*initial, *lifetime.reach('S_capture','S_initial',kind,0),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        'pconfigcall_capture.OWNER = (n_callee)', 'pconfigcall_capture.SENT = eps',
        '$config_selected_valid(S_capture,pconfigcall_capture)',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_callee) = 2',
        *variable('S_capture','call','POBJECT n_callee'),
        *variable('S_capture','name','PARRAY n_input'),
        'S_capture.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING ($ptascii("plain"))) (DIRECT pvalue_old),ENTRY (KINT ' + str(slot) + ') (DIRECT (' + value + '))]',
        'pvalue_old = PSTRING_CARRIER (REQUEST_STRING n_old) preqbytes_old',
        'preqbytes_old = ' + text(stem+'-old'), '$string_carrier_valid(S_capture,pvalue_old)',
        '(HARRAY n_input) <- S_capture.ALLOCATIONS', '~(HARRAY n_input <- $pools_nodes(S_capture.POOLS))',
        '$test_outputs(S_capture.EVENTS) = ' + term(b'B|'), *lifetime.budget('S_capture'),
        *reach('S','S_capture',kind),
        'S.TODO = (CONFIG_INVOKE pconfigcall_S) :: ptask_S*',
        'pconfigcall_S.OWNER = (n_callee)', 'pconfigcall_S.SELECTION = eps',
        'pconfigcall_S.PACKS = eps', '~pconfigcall_S.NAMED', 'pconfigcall_S.INDEX = 1',
        f'pconfigcall_S.LINE = {line}', 'pconfigcall_S.SENT = [NAMED_SENT (KNOWN (PARRAY n_input))]',
        '$config_invoke_valid(S,pconfigcall_S)', '$dynamic_owned_query_array_call(pconfigcall_S)',
        '$dynamic_query_array_valid(S,pconfigcall_S)',
        '$dynamic_query_array_entries(S,S.ARRAYS[n_input].ITEMS)',
        '$dynamic_define_known(S,pconfigcall_S.SITE,0) = eps', '~$pipe_site(S,pconfigcall_S.SITE)',
        '$config_nodes(pconfigcall_S) = [HOBJECT n_callee,HARRAY n_input]',
        '$heap_owners($heap_graph(S),HOBJECT n_callee) = 1',
        '$exit_strict(S,pconfigcall_S.SITE)',
        f'{"~" if explicit else ""}$config_strict(S,pconfigcall_S)',
        f'{"" if explicit else "~"}$config_method_receiver(S,pconfigcall_S)',
        *lifetime.weak('S','weakCall','n_callee','call'),
        *variable('S','result','PINT 97'), *variable('S','effects','PINT 1'),
        'S.ARRAYS[n_input] = S_capture.ARRAYS[n_input]',
        'S.USERCONSTANTS = [puserconstant]', 'puserconstant.NAME = ' + text(key),
        f'puserconstant.VALUE = PINT {number}', 'puserconstant.CLASS = PVSCALAR',
        'S.SELECTEDCALLS = eps', 'S.SELECTSEQ = 0', '$test_outputs(S.EVENTS) = ' + term(before)]
    if explicit: values += [*variable('S','call','PNULL'),*variable('S','name','PNULL')]
    else:
        values += [*variable('S','snapshot','PARRAY n_input'),
            *variable('S','name','PARRAY n_live'), 'n_live =/= n_input',
            *payload('S','n_live','strict-live',3,'PINT 17','live'),
            *variable('S','call','pvalue_current_call'), '$string_bytes(pvalue_current_call) = ($ptascii("defined"))']
    values += [*controls(), *lifetime.budget('S'), *common.step('S_pending','S'),
        *lifetime.settle('S_error','S_pending'), *error_trace(explicit,api,line),
        'S_error.ARRAYS[n_input] = S.ARRAYS[n_input]',
        '$weakref_get(S_error,n_weak_call) = PNULL', '~(HOBJECT n_callee <- S_error.ALLOCATIONS)',
        'S_error.USERCONSTANTS = S.USERCONSTANTS', 'S_error.EVENTS = S.EVENTS',
        *variable('S_error','result','PINT 97'),
        *prior.unset('S_caught','S_error','error'),
        '$test_outputs(S_caught.EVENTS) = ' + term(caught),
        'S_caught.ARRAYS[n_input] = S.ARRAYS[n_input]']
    if explicit:
        values += [*variable('S_caught','api','PARRAY n_copy'),
            *variable('S_caught','invoke','PARRAY n_invoke_copy'),
            'n_copy =/= n_input', 'n_invoke_copy =/= n_input', 'n_copy =/= n_invoke_copy',
            *payload('S_caught','n_copy','explicit-api',5,'PBOOL false','copy'),
            *payload('S_caught','n_invoke_copy','explicit-old',5,'PBOOL true','invoke_copy'),
            'pvalue_invoke_copy = pvalue_old',
            *variable('S_caught','rawApiArgs','PARRAY n_args'),
            *variable('S_caught','rawInvokeArgs','PARRAY n_invoke_args')]
    else:
        values += [*variable('S_caught','raw','PARRAY n_copy'), 'n_copy =/= n_input', 'n_copy =/= n_live',
            *payload('S_caught','n_copy','strict-raw',3,'PINT 17','copy'),
            'S_caught.ARRAYS[n_live] = S.ARRAYS[n_live]',
            *variable('S_caught','snapshot','PARRAY n_input')]
    values += [*prior.unset('S_raw','S_caught','api' if explicit else 'raw'),
        '$test_outputs(S_raw.EVENTS) = ' + term(raw),
        '~(HOBJECT n_error <- S_raw.ALLOCATIONS)',
        *[f'~(HARRAY {node} <- S_raw.ALLOCATIONS)' for node in ['n_input','n_trace','n_api','n_args']],
        '$heap_owners($heap_graph(S_raw),HARRAY n_copy) = 1',
        '$node_children(S_raw,HARRAY n_copy) = eps',
        'S_raw.ARRAYS[n_copy] = S_caught.ARRAYS[n_copy]', *lifetime.budget('S_raw')]
    if explicit:
        values += ['~(HARRAY n_invoke <- S_raw.ALLOCATIONS)', '~(HARRAY n_invoke_args <- S_raw.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_raw),HARRAY n_invoke_copy) = 1',
            'S_raw.ARRAYS[n_invoke_copy] = S_caught.ARRAYS[n_invoke_copy]',
            *prior.unset('S_last','S_raw','invoke'),
            '~(HARRAY n_copy <- S_last.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_last),HARRAY n_invoke_copy) = 1',
            'S_last.ARRAYS[n_invoke_copy] = S_caught.ARRAYS[n_invoke_copy]',
            '$test_outputs(S_last.EVENTS) = ' + term(last), *lifetime.budget('S_last')]
    else: values += ['~(HARRAY n_live <- S_raw.ALLOCATIONS)']
    values += [*lifetime.reach('S_read','S_last' if explicit else 'S_raw','INTRINSIC_CONSTANT',4),
        'S_read.TODO = (CONFIG_INVOKE pconfigcall_read) :: ptask_read*',
        'pconfigcall_read.OWNER = (n_reader)', 'n_reader =/= n_callee',
        'pconfigcall_read.SENT = [NAMED_SENT (KNOWN pvalue_key)]',
        '$string_bytes(pvalue_key) = (' + text(key) + ')',
        '~(HARRAY n_copy <- S_read.ALLOCATIONS)',
        *variable('S_read','result','PINT 97'),
        '$test_outputs(S_read.EVENTS) = ' + term(last),
        *common.step('S_value_pending','S_read'),
        *lifetime.settle('S_value','S_value_pending',f'PINT {number}'),
        *define.finish('S_value',stdout), 'S_final.USERCONSTANTS = S.USERCONSTANTS',
        'S_final.SELECTEDCALLS = eps', 'S_final.SELECTSEQ = 0',
        'S_final.STRINGDATA[n_old] = preqbytes_old', '$string_carrier_valid(S_final,pvalue_old)']
    for node in ['HOBJECT n_callee','HOBJECT n_weak_call','HOBJECT n_reader','HOBJECT n_error',
            'HARRAY n_input','HARRAY n_trace','HARRAY n_api','HARRAY n_args','HARRAY n_copy'] + (
                ['HARRAY n_invoke','HARRAY n_invoke_args','HARRAY n_invoke_copy'] if explicit else ['HARRAY n_live']):
        values += [f'~({node} <- S_final.ALLOCATIONS)']
    return values


base = lifetime.captured.prior
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
