#!/usr/bin/env python3
"""Raw TypeError traces outlive captured nonStringable query callees."""
from pathlib import Path

import constant_owned_stringable_query_protocol as prior
import typed_static_invoke_set_protocol as process_base
import constant_owned_nonstringable_query_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
PREFIX = prior.PREFIX + r'''
dec $test_nonstring_unset(pstate, preqbytes) : bool
def $test_nonstring_unset(S,preqbytes) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_name) metadata_name) :: expression_tail*
  -- if $base64(text_name) = preqbytes
def $test_nonstring_unset(S,preqbytes) = false -- otherwise
dec $test_nonstring_unset_seek(pstate, preqbytes, nat) : pstate
def $test_nonstring_unset_seek(S,preqbytes,0) = S
def $test_nonstring_unset_seek(S,preqbytes,n) = S
  -- if $(n > 0)
  -- if $test_nonstring_unset(S,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_nonstring_unset_seek(S,preqbytes,n) = $test_nonstring_unset_seek($drive_steps($test_running(S),1),preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_nonstring_unset(S,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def unset(state, start, variable):
    return [f'{state}_found = $test_nonstring_unset_seek({start},{text(variable)},3000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_nonstring_unset({state},{text(variable)})', *common.public(state)]


def controls():
    values = ['S_dead_callee = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_callee)]',
        '~$dynamic_query_nonstring_valid(S_dead_callee,pconfigcall_S)',
        'S_dead_name = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_name)]',
        '~$dynamic_query_nonstring_valid(S_dead_name,pconfigcall_S)']
    for change in ['.OWNER = eps', '.OWNER = (|S.OBJECTS|)', '.SELECTION = (0)',
            '.KIND = INTRINSIC_DEFINE', '.INDEX = 0', '.SITE = PORIGIN 0 eps',
            '.LINE = $(pconfigcall_S.LINE + 1)', '.NAMED = true',
            '.SENT = eps', '.SENT = pconfigcall_S.SENT ++ pconfigcall_S.SENT']:
        values += [f'~$dynamic_query_nonstring_valid(S,pconfigcall_S[{change}])']
    values += ['pconfigpack_forged = {INDEX 0,SITE pconfigcall_S.SITE,LINE pconfigcall_S.LINE,ARRAY 0,ITEMS eps}',
        '~$dynamic_query_nonstring_valid(S,pconfigcall_S[.PACKS = [pconfigpack_forged]])']
    for value in ['PNULL','PBOOL true','PINT 17','PFLOAT 0','PSTRING ($ptascii("TRUE"))',
            'PSTRING ([65,0,66])','PARRAY 0','POBJECT (|S.OBJECTS|)']:
        values += [f'~$dynamic_query_nonstring_valid(S,pconfigcall_S[.SENT = [NAMED_SENT (KNOWN ({value}))]])']
    for label, value in [('weak','WEAKREFERENCE eps'),
            ('closure','INTRINSICCLOSURE INTRINSIC_DEFINED'),
            ('class','INSTANCE (PORIGIN 0 eps)')]:
        values += [f'S_forged_{label} = S[.OBJECTS[n_name] = {value}]',
            f'~$dynamic_query_nonstring_object(S_forged_{label},n_name)',
            f'~$dynamic_query_nonstring_valid(S_forged_{label},pconfigcall_S)']
    return values


def trace(explicit, api, classname, line):
    frames = '[ENTRY (KINT 0) (DIRECT (PARRAY n_api))'
    frames += ',ENTRY (KINT 1) (DIRECT (PARRAY n_invoke))]' if explicit else ']'
    values = ['S_error.TODO = (THROW_SEARCH n_error) :: ptask_error*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable',
        'pthrowable.KIND = "TypeError"', 'pthrowable.ORIGIN = (pconfigcall_S.SITE)',
        '$throwable_chain_valid(S_error,n_error)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = ('
            + text(api+'(): Argument #1 ($'+('constant_name' if explicit else 'name')
                +') must be of type string, '+classname+' given') + ')',
        f'$throwable_field(S_error,n_error,"line") = PINT {line}',
        '$string_bytes($throwable_field(S_error,n_error,"file")) = ($call_sourcefile(S.FILES,pconfigcall_S.SITE))',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS = ' + frames,
        '$trace_array_field(S_error,n_api,$ptascii("function")) = PSTRING (' + text(api) + ')',
        '$trace_array_field(S_error,n_api,$ptascii("file")) = PSTRING ($call_sourcefile(S.FILES,pconfigcall_S.SITE))',
        f'$trace_array_field(S_error,n_api,$ptascii("line")) = PINT {line}',
        '$trace_array_field(S_error,n_api,$ptascii("args")) = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_name))]',
        '$node_children(S_error,HARRAY n_args) = [HOBJECT n_name]']
    if explicit:
        values += ['$trace_array_field(S_error,n_invoke,$ptascii("function")) = PSTRING ($ptascii("__invoke"))',
            '$trace_array_field(S_error,n_invoke,$ptascii("class")) = PSTRING ($ptascii("Closure"))',
            '$trace_array_field(S_error,n_invoke,$ptascii("type")) = PSTRING ($ptascii("->"))',
            '$trace_array_field(S_error,n_invoke,$ptascii("file")) = PSTRING ($call_sourcefile(S.FILES,pconfigcall_S.SITE))',
            f'$trace_array_field(S_error,n_invoke,$ptascii("line")) = PINT {line}',
            '$trace_array_field(S_error,n_invoke,$ptascii("args")) = PARRAY n_invoke_args',
            'S_error.ARRAYS[n_invoke_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_name))]',
            'n_args =/= n_invoke_args',
            '$node_children(S_error,HARRAY n_invoke_args) = [HOBJECT n_name]']
    return values


def checks(initial, name, stdout):
    explicit = name == sources.EXPLICIT
    kind = 'INTRINSIC_DEFINED' if explicit else 'INTRINSIC_CONSTANT'
    api, classname, line = ('defined','V104ExplicitName',31) if explicit else ('constant','stdClass',22)
    key, number = ('V104_EXPLICIT_RECOVERY',23) if explicit else ('V104_STRICT_RECOVERY',17)
    before = b'B|N|held|'
    caught = before + (b'E|defined(): Argument #1 ($constant_name) must be of type string, '
        b'V104ExplicitName given|31|none|defined|apiO|apiFile|31|__invoke|Closure|->|'
        b'invokeO|invokeFile|31|end|calleeGone|nameHeld|null|constant|97|1|0|' if explicit else
        b'E|constant(): Argument #1 ($name) must be of type string, stdClass given|22|'
        b'none|constant|rawO|file|22|end|calleeGone|nameHeld|null|defined|97|1|')
    raw_only = caught + (b'wrapperHeld|0|' if explicit else b'rawHeld|')
    released = raw_only + (b'D|gone|released|1|' if explicit else b'released|')
    assert stdout == released + str(number).encode() + b'|A|'
    values = [*initial, *prior.reach('S_capture','S_initial',kind,0),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        'pconfigcall_capture.OWNER = (n_callee)', 'pconfigcall_capture.SELECTION = eps',
        'pconfigcall_capture.SENT = eps', '$config_selected_valid(S_capture,pconfigcall_capture)',
        '$config_nodes(pconfigcall_capture) = [HOBJECT n_callee]',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_callee) = 2',
        *[f'$lookup(S_capture.ENV,{text(var)}) = (n_{var}_cv)' for var in ['call','name','effects','result']],
        'S_capture.STORE[n_call_cv] = DEFINED (POBJECT n_callee)',
        'S_capture.STORE[n_name_cv] = DEFINED (POBJECT n_name)',
        'S_capture.STORE[n_effects_cv] = DEFINED (PINT 0)',
        'S_capture.STORE[n_result_cv] = DEFINED (PINT 97)',
        '$test_outputs(S_capture.EVENTS) = ' + term(b'B|'),
        *prior.budget('S_capture'), *prior.reach('S','S_capture',kind,1),
        'S.TODO = (CONFIG_INVOKE pconfigcall_S) :: ptask_S*',
        'pconfigcall_S.OWNER = (n_callee)', 'pconfigcall_S.SELECTION = eps',
        'pconfigcall_S.PACKS = eps', '~pconfigcall_S.NAMED', 'pconfigcall_S.INDEX = 1',
        f'pconfigcall_S.LINE = {line}',
        'pconfigcall_S.SENT = [NAMED_SENT (KNOWN (POBJECT n_name))]',
        '$config_invoke_valid(S,pconfigcall_S)', '$dynamic_owned_query_string_call(pconfigcall_S)',
        '$dynamic_scalar_define_arguments(S,pconfigcall_S,0)', '~$pipe_site(S,pconfigcall_S.SITE)',
        '~$dynamic_query_string_call(pconfigcall_S)',
        '$dynamic_query_nonstring_valid(S,pconfigcall_S)',
        '$dynamic_query_nonstring_object(S,n_name)', '~$stringable_instance(S,n_name)',
        '~$dynamic_query_string_valid(S,pconfigcall_S)', '~$config_string_launch(S,pconfigcall_S)',
        '$exit_strict(S,pconfigcall_S.SITE)',
        f'{"~" if explicit else ""}$config_strict(S,pconfigcall_S)',
        f'{"" if explicit else "~"}$config_method_receiver(S,pconfigcall_S)',
        '$config_nodes(pconfigcall_S) = [HOBJECT n_callee,HOBJECT n_name]',
        '$heap_owners($heap_graph(S),HOBJECT n_callee) = 1',
        *prior.captured.intrinsic('S','n_callee',kind),
        *prior.weak('S','weakCall','n_callee','call'), *prior.weak('S','weakName','n_name','name'),
        'S.STORE[n_call_cv] = DEFINED pvalue_current_call',
        '$string_bytes(pvalue_current_call) = (' + text('constant' if explicit else 'defined') + ')',
        'S.STORE[n_name_cv] = DEFINED PNULL', 'S.STORE[n_effects_cv] = DEFINED (PINT 1)',
        'S.STORE[n_result_cv] = DEFINED (PINT 97)',
        'S.SELECTEDCALLS = eps', 'S.SELECTSEQ = 0', '$test_outputs(S.EVENTS) = ' + term(before)]
    if explicit:
        values += ['S.OBJECTS[n_name] = INSTANCE porigin_class',
            '$lookup(S.ENV,$ptascii("drops")) = (n_drops_cv)',
            'S.STORE[n_drops_cv] = DEFINED (PINT 0)', 'S.USERCONSTANTS = eps',
            '$effective_method(S,porigin_class,$ptascii("__toString"),|S.CLASSES|) = eps']
    else:
        values += ['S.OBJECTS[n_name] = STDINSTANCE',
            'S.USERCONSTANTS = [puserconstant]',
            'puserconstant.NAME = ' + text(key), 'puserconstant.VALUE = PINT 17',
            'puserconstant.CLASS = PVSCALAR']
    values += [*controls(), *prior.budget('S'), *common.step('S_pending','S'),
        *prior.settle('S_error','S_pending'), *trace(explicit,api,classname,line),
        '$weakref_get(S_error,n_weak_call) = PNULL',
        '~(HOBJECT n_callee <- S_error.ALLOCATIONS)',
        '$weakref_get(S_error,n_weak_name) = POBJECT n_name',
        'S_error.OBJECTS[n_name] = S.OBJECTS[n_name]',
        '$objectprops_at(S_error.OBJECTPROPS,n_name) = $objectprops_at(S.OBJECTPROPS,n_name)',
        'S_error.STORE[n_result_cv] = DEFINED (PINT 97)',
        'S_error.STORE[n_effects_cv] = DEFINED (PINT 1)',
        'S_error.USERCONSTANTS = S.USERCONSTANTS', 'S_error.EVENTS = S.EVENTS',
        *unset('S_raw','S_error','rawInvoke' if explicit else 'raw'),
        '$weakref_get(S_raw,n_weak_name) = POBJECT n_name',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_name) = 1',
        '~(HOBJECT n_error <- S_raw.ALLOCATIONS)', '~(HARRAY n_trace <- S_raw.ALLOCATIONS)',
        '~(HARRAY n_api <- S_raw.ALLOCATIONS)',
        '$lookup(S_raw.ENV,' + text('rawInvoke' if explicit else 'raw') + ') = (n_raw_cv)',
        'S_raw.STORE[n_raw_cv] = DEFINED (PARRAY ' + ('n_invoke_args' if explicit else 'n_args') + ')',
        'S_raw.STORE[n_result_cv] = DEFINED (PINT 97)',
        '$test_outputs(S_raw.EVENTS) = ' + term(raw_only), *prior.budget('S_raw')]
    if explicit:
        values += ['~(HARRAY n_args <- S_raw.ALLOCATIONS)',
            '~(HARRAY n_invoke <- S_raw.ALLOCATIONS)',
            'S_raw.STORE[n_drops_cv] = DEFINED (PINT 0)', 'S_raw.USERCONSTANTS = eps',
            *prior.reach('S_drop','S_raw',kind,5),
            'S_drop.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_drop*',
            'pdestructorcall.OBJECT = n_name', '$destructor_call_valid(S_drop,pdestructorcall)',
            '$weakref_get(S_drop,n_weak_call) = PNULL',
            'S_drop.STORE[n_drops_cv] = DEFINED (PINT 0)', 'S_drop.USERCONSTANTS = eps',
            '$test_outputs(S_drop.EVENTS) = ' + term(raw_only)]
    values += [*prior.reach('S_recover','S_drop' if explicit else 'S_raw','INTRINSIC_CONSTANT',4),
        'S_recover.TODO = (CONFIG_INVOKE pconfigcall_recover) :: ptask_recover*',
        'pconfigcall_recover.OWNER = (n_reader)',
        'pconfigcall_recover.SENT = [NAMED_SENT (KNOWN pvalue_key)]',
        '$string_bytes(pvalue_key) = (' + text(key) + ')',
        '$weakref_get(S_recover,n_weak_name) = PNULL',
        '~(HOBJECT n_name <- S_recover.ALLOCATIONS)',
        'S_recover.STORE[n_result_cv] = DEFINED (PINT 97)',
        'S_recover.USERCONSTANTS = [puserconstant_recovery]',
        'puserconstant_recovery.NAME = ' + text(key),
        f'puserconstant_recovery.VALUE = PINT {number}', 'puserconstant_recovery.CLASS = PVSCALAR',
        '$test_outputs(S_recover.EVENTS) = ' + term(released),
        *common.step('S_value_pending','S_recover'),
        *prior.settle('S_value','S_value_pending',f'PINT {number}'),
        *define.finish('S_value',stdout),
        'S_final.USERCONSTANTS = S_recover.USERCONSTANTS',
        'S_final.SELECTEDCALLS = eps', 'S_final.SELECTSEQ = 0']
    for node in ['HOBJECT n_callee','HOBJECT n_name','HOBJECT n_reader',
            'HOBJECT n_weak_call','HOBJECT n_weak_name','HOBJECT n_error',
            'HARRAY n_trace','HARRAY n_api','HARRAY n_args'] + (
                ['HARRAY n_invoke','HARRAY n_invoke_args'] if explicit else []):
        values += [f'~({node} <- S_final.ALLOCATIONS)']
    return values


base = prior.captured.prior
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
