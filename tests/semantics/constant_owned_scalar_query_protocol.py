#!/usr/bin/env python3
"""Reached scalar captures, late lookup, converted traces and callee retirement."""
from pathlib import Path

import constant_owned_query_protocol as prior
import typed_static_invoke_set_protocol as process_base
import constant_owned_scalar_query_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
PREFIX = prior.PREFIX


def admission(state, call, value):
    return [f'{call}.SELECTION = eps', f'{call}.PACKS = eps',
        f'{call}.NAMED', f'{call}.INDEX = 1',
        f'{call}.SENT = [NAMED_SENT (KNOWN ({value}))]',
        f'$config_invoke_valid({state},{call})',
        f'~$dynamic_scalar_constant_call({call})',
        f'$dynamic_owned_scalar_query_call({call})',
        f'$dynamic_scalar_constant_valid({state},{call})',
        f'~$config_strict({state},{call})',
        f'$dynamic_global_constant_known({state},{call}.SITE) = eps']


def controls(state, call, owner, label):
    # Invalid authority/shape projections are checked without driving them.
    values = [f'S_dead_{label} = {state}[.ALLOCATIONS = $destruction_node_delete({state}.ALLOCATIONS,HOBJECT {owner})]',
        f'~$dynamic_scalar_constant_valid(S_dead_{label},{call})',
        f'S_wrong_{label} = {state}[.OBJECTS[{owner}] = INTRINSICCLOSURE INTRINSIC_DEFINE]',
        f'~$dynamic_scalar_constant_valid(S_wrong_{label},{call})']
    for change in [f'.OWNER = (|{state}.OBJECTS|)', '.SELECTION = (0)',
            '.KIND = INTRINSIC_DEFINE', '.INDEX = 0', '.SITE = PORIGIN 0 eps',
            f'.LINE = $({call}.LINE + 1)', f'.NAMED = ~{call}.NAMED']:
        values += [f'~$dynamic_scalar_constant_valid({state},{call}[{change}])']
    values += [f'pconfigpack_{label} = {{INDEX 0, SITE {call}.SITE, LINE {call}.LINE, ARRAY 0, ITEMS eps}}',
        f'~$dynamic_owned_scalar_query_call({call}[.PACKS = [pconfigpack_{label}]])']
    for value in ['PNULL', 'PSTRING ($ptascii("37"))', 'PARRAY 0', 'POBJECT 0',
            'PFLOAT 9218868437227405312', 'PFLOAT 18442240474082181120',
            'PFLOAT 9221120237041090560', 'PFLOAT 18446744073709551616']:
        values += [f'~$dynamic_owned_scalar_query_value({value})',
            f'~$dynamic_owned_scalar_query_call({call}[.SENT = [NAMED_SENT (KNOWN ({value}))]])',
            f'~$dynamic_scalar_constant_valid({state},{call}[.SENT = [NAMED_SENT (KNOWN ({value}))]])']
    values += [f'~$dynamic_owned_scalar_query_call({call}[.SENT = eps])',
        f'~$dynamic_owned_scalar_query_call({call}[.SENT = {call}.SENT ++ {call}.SENT])']
    return values


def converted(state, call, value, query):
    after = state + '_converted'
    return [f'$config_conversion({state},{call},{value}) = TYPESTRING ({value})',
        f'{after} = $typed_apply({state},TYPESTRING ({value}),{call}.LINE)',
        f'{after}.COMPLETION = NORMAL', f'{after}.RESULT = KNOWN pvalue_{after}',
        f'$string_bytes(pvalue_{after}) = ({text(query)})',
        f'$string_carrier_valid({after},pvalue_{after})',
        f'{after}.STORE = {state}.STORE', f'{after}.USERCONSTANTS = {state}.USERCONSTANTS']


def late(initial, stdout):
    before = b'B|N|held|'
    before_bool = before + b'137|gone|null|404|'
    assert stdout == before_bool + b'F|held|T|gone|T|101|A|'
    values = [*initial, *prior.reach('S_capture','S_initial','INTRINSIC_CONSTANT',0),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        'pconfigcall_capture.OWNER = (n_reader)', 'pconfigcall_capture.SENT = eps',
        'pconfigcall_capture.SELECTION = eps',
        *prior.intrinsic('S_capture','n_reader','INTRINSIC_CONSTANT'),
        '$lookup(S_capture.ENV,$ptascii("call")) = (n_call)',
        '$lookup(S_capture.ENV,$ptascii("other")) = (n_other)',
        '$lookup(S_capture.ENV,$ptascii("name")) = (n_name)',
        '$lookup(S_capture.ENV,$ptascii("weakRead")) = (n_weak_read_cv)',
        '$lookup(S_capture.ENV,$ptascii("weakHas")) = (n_weak_has_cv)',
        'S_capture.STORE[n_call] = DEFINED (POBJECT n_reader)',
        'S_capture.STORE[n_other] = DEFINED (POBJECT n_has)',
        'S_capture.STORE[n_name] = DEFINED (PINT 37)',
        'S_capture.STORE[n_weak_read_cv] = DEFINED (POBJECT n_weak_read)',
        'S_capture.STORE[n_weak_has_cv] = DEFINED (POBJECT n_weak_has)',
        'S_capture.OBJECTS[n_weak_read] = WEAKREFERENCE (n_reader)',
        'S_capture.OBJECTS[n_weak_has] = WEAKREFERENCE (n_has)',
        *prior.intrinsic('S_capture','n_has','INTRINSIC_DEFINED'),
        'n_reader =/= n_has', 'S_capture.USERCONSTANTS = eps',
        'S_capture.SELECTEDCALLS = eps', 'S_capture.SELECTSEQ = 0',
        '$config_nodes(pconfigcall_capture) = [HOBJECT n_reader]',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_reader) = 2',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_has) = 1',
        '$test_outputs(S_capture.EVENTS) = ' + term(b'B|'),
        *prior.reach('S','S_capture','INTRINSIC_CONSTANT',1),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_read*',
        'pconfigcall.OWNER = (n_reader)', *admission('S','pconfigcall','PINT 37'),
        'S.STORE[n_call] = DEFINED (POBJECT n_has)',
        'S.STORE[n_other] = DEFINED PNULL', 'S.STORE[n_name] = DEFINED (PINT 404)',
        'S.USERCONSTANTS = [puserconstant_int]',
        'puserconstant_int.NAME = $ptascii("37")',
        'puserconstant_int.VALUE = PINT 137', 'puserconstant_int.CLASS = PVSCALAR',
        '$dynamic_define_source(S,puserconstant_int.ORIGIN)',
        '$dynamic_global_constant_value(S,$ptascii("37")) = (PINT 137)',
        '$heap_owners($heap_graph(S),HOBJECT n_reader) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_has) = 1',
        '$weakref_get(S,n_weak_read) = POBJECT n_reader',
        'S.SELECTEDCALLS = eps', 'S.SELECTSEQ = 0',
        '$test_outputs(S.EVENTS) = ' + term(before),
        *controls('S','pconfigcall','n_reader','int'),
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        *converted('S','pconfigcall','PINT 37','37'),
        *common.step('S_value','S','PINT 137'),
        '$drive_steps($test_running(S_pause),1) = S_value_found',
        'S_value.TODO = ptask_read*', 'S_value.STRINGDATA = S_converted.STRINGDATA',
        *prior.unchanged('S','S_value'),
        '~(HOBJECT n_reader <- S_value.ALLOCATIONS)',
        '$weakref_get(S_value,n_weak_read) = PNULL',
        *prior.reach('S_bool_capture','S_value','INTRINSIC_DEFINED',0),
        'S_bool_capture.TODO = (CONFIG_ARGS pconfigcall_bool_capture) :: ptask_bool_capture*',
        'pconfigcall_bool_capture.OWNER = (n_has)',
        'pconfigcall_bool_capture.SENT = eps', 'pconfigcall_bool_capture.SELECTION = eps',
        'S_bool_capture.STORE[n_name] = DEFINED (PBOOL false)',
        '$heap_owners($heap_graph(S_bool_capture),HOBJECT n_has) = 2',
        '$test_outputs(S_bool_capture.EVENTS) = ' + term(before_bool),
        *prior.reach('S_bool','S_bool_capture','INTRINSIC_DEFINED',1),
        'S_bool.TODO = (CONFIG_INVOKE pconfigcall_bool) :: ptask_bool*',
        'pconfigcall_bool.OWNER = (n_has)',
        *admission('S_bool','pconfigcall_bool','PBOOL false'),
        'S_bool.STORE[n_call] = DEFINED pvalue_current_call',
        '$string_bytes(pvalue_current_call) = ($ptascii("constant"))',
        'S_bool.STORE[n_name] = DEFINED (PBOOL true)',
        'S_bool.USERCONSTANTS = [puserconstant_int,puserconstant_empty]',
        'puserconstant_empty.NAME = eps', 'puserconstant_empty.VALUE = PINT 101',
        'puserconstant_empty.CLASS = PVSCALAR',
        '$dynamic_define_source(S_bool,puserconstant_empty.ORIGIN)',
        '$dynamic_global_constant_value(S_bool,eps) = (PINT 101)',
        '$heap_owners($heap_graph(S_bool),HOBJECT n_has) = 1',
        '$weakref_get(S_bool,n_weak_has) = POBJECT n_has',
        'S_bool.SELECTEDCALLS = eps', 'S_bool.SELECTSEQ = 0',
        '$test_outputs(S_bool.EVENTS) = ' + term(before_bool + b'F|held|'),
        *converted('S_bool','pconfigcall_bool','PBOOL false',''),
        *common.step('S_has','S_bool','PBOOL true'),
        'S_has.TODO = ptask_bool*', 'S_has.STRINGDATA = S_bool_converted.STRINGDATA',
        *prior.unchanged('S_bool','S_has'),
        '~(HOBJECT n_has <- S_has.ALLOCATIONS)',
        '$weakref_get(S_has,n_weak_has) = PNULL',
        *define.finish('S_has',stdout),
        'S_final.USERCONSTANTS = S_bool.USERCONSTANTS',
        'S_final.SELECTEDCALLS = eps', 'S_final.SELECTSEQ = 0',
        '~(HOBJECT n_reader <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_has <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_weak_read <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_weak_has <- S_final.ALLOCATIONS)']
    return values


def missing(initial, stdout):
    before = b'B|N|held|'
    assert stdout == before + b'E|Undefined constant ""|19|none|constant|S|97|1|gone|T|null|A|'
    values = [*initial, *prior.reach('S_capture','S_initial','INTRINSIC_CONSTANT',0),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        'pconfigcall_capture.OWNER = (n_reader)', 'pconfigcall_capture.SENT = eps',
        'pconfigcall_capture.SELECTION = eps',
        *prior.intrinsic('S_capture','n_reader','INTRINSIC_CONSTANT'),
        '$lookup(S_capture.ENV,$ptascii("call")) = (n_call)',
        '$lookup(S_capture.ENV,$ptascii("name")) = (n_name)',
        '$lookup(S_capture.ENV,$ptascii("weak")) = (n_weak_cv)',
        '$lookup(S_capture.ENV,$ptascii("calls")) = (n_calls)',
        '$lookup(S_capture.ENV,$ptascii("result")) = (n_result)',
        'S_capture.STORE[n_call] = DEFINED (POBJECT n_reader)',
        'S_capture.STORE[n_name] = DEFINED (PBOOL false)',
        'S_capture.STORE[n_calls] = DEFINED (PINT 0)',
        'S_capture.STORE[n_result] = DEFINED (PINT 97)',
        'S_capture.STORE[n_weak_cv] = DEFINED (POBJECT n_weak)',
        'S_capture.OBJECTS[n_weak] = WEAKREFERENCE (n_reader)',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_reader) = 2',
        *prior.reach('S','S_capture','INTRINSIC_CONSTANT',1),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        'pconfigcall.OWNER = (n_reader)', *admission('S','pconfigcall','PBOOL false'),
        'S.STORE[n_call] = DEFINED PNULL', 'S.STORE[n_name] = DEFINED (PBOOL true)',
        'S.STORE[n_calls] = DEFINED (PINT 1)', 'S.STORE[n_result] = DEFINED (PINT 97)',
        'S.USERCONSTANTS = eps', 'S.SELECTEDCALLS = eps', 'S.SELECTSEQ = 0',
        '$heap_owners($heap_graph(S),HOBJECT n_reader) = 1',
        '$weakref_get(S,n_weak) = POBJECT n_reader',
        '$test_outputs(S.EVENTS) = ' + term(before),
        *controls('S','pconfigcall','n_reader','false'),
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        *converted('S','pconfigcall','PBOOL false',''),
        *common.step('S_error','S'), *common.public('S_error'),
        '$drive_steps($test_running(S_pause),1) = S_error_found',
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_initial*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'pthrowable_error.KIND = "Error"', 'pthrowable_error.ORIGIN = (pconfigcall.SITE)',
        '$throwable_chain_valid(S_error,n_error)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('Undefined constant ""') + ')',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"line") = PINT pconfigcall.LINE',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]',
        '$trace_array_field(S_error,n_frame,$ptascii("function")) = PSTRING ($ptascii("constant"))',
        '$trace_array_field(S_error,n_frame,$ptascii("args")) = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_S_converted)]',
        '$string_carrier_valid(S_error,pvalue_S_converted)',
        '~(HOBJECT n_reader <- S_error.ALLOCATIONS)',
        '$weakref_get(S_error,n_weak) = PNULL',
        '$heap_owners($heap_graph(S_error),HOBJECT n_reader) = 0',
        'S_error.STORE[n_result] = DEFINED (PINT 97)',
        'S_error.STORE[n_name] = DEFINED (PBOOL true)',
        'S_error.USERCONSTANTS = eps', 'S_error.SELECTEDCALLS = eps',
        'S_error.SELECTSEQ = 0', 'S_error.EVENTS = S.EVENTS',
        *define.finish('S_error',stdout),
        'S_final.USERCONSTANTS = eps', 'S_final.SELECTEDCALLS = eps',
        'S_final.SELECTSEQ = 0', '~(HOBJECT n_error <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_reader <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_weak <- S_final.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_final.ALLOCATIONS)',
        '~(HARRAY n_frame <- S_final.ALLOCATIONS)',
        '~(HARRAY n_args <- S_final.ALLOCATIONS)']
    return values


def checks(initial, name, stdout):
    return (late if name == sources.LATE else missing)(initial, stdout)


base = prior.prior
base.sources, base.checks, base.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, base.prepare
packet_process = process_base.process


def process(command, directory, timeout, cwd):
    if directory.parent.name in sources.family.CASES:
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
