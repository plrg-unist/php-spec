#!/usr/bin/env python3
"""A rejected intrinsic VALUE survives its callee and becomes a selected writer."""
from pathlib import Path

import define_runtime_closure_protocol as runtime
import define_stdclass_array_duplicate_review_protocol as prior
import typed_static_invoke_set_protocol as process_base
import define_runtime_intrinsic_closure_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
CASE = sources.CASE
OLD, NEW = 'V98_REVIEW_OLD', 'V98_REVIEW_NEW'
PREFIX = runtime.PREFIX + r'''
dec $test_intrinsic_peer_front(pstate, nat) : bool
def $test_intrinsic_peer_front(S,0) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.SELECTION = (0) /\ pconfigcall.INDEX = 2
def $test_intrinsic_peer_front(S,1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.SELECTION = (0)
def $test_intrinsic_peer_front(S,2) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall n_constants
  -- if pconfigcall.SELECTION = (0)
def $test_intrinsic_peer_front(S,3) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.SELECTION = (1) /\ pconfigcall.INDEX = 0
def $test_intrinsic_peer_front(S,4) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.SELECTION = (1)
def $test_intrinsic_peer_front(S,n_phase) = false -- otherwise
dec $test_intrinsic_peer_seek(pstate, nat, nat) : pstate
def $test_intrinsic_peer_seek(S,n_phase,0) = S
def $test_intrinsic_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_intrinsic_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_intrinsic_peer_seek(S,n_phase,n) = $test_intrinsic_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_intrinsic_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_intrinsic_peer_seek({start},{phase},1500)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_intrinsic_peer_front({state},{phase})', *common.public(state)]


def intrinsic(state, obj):
    return [f'{state}.OBJECTS[{obj}] = INTRINSICCLOSURE INTRINSIC_DEFINE',
        f'$typed_closure({state},{obj})', f'$closure_live_object_valid({state},{obj})',
        f'$closure_scope_at({state}.CLOSURESCOPES,{obj}) = eps',
        f'$closure_binding_at({state}.CLOSUREBINDINGS,{obj}) = eps',
        f'$constant_callable_record({state}.CONSTANTCLOSURES,{obj}) = eps',
        f'$node_children({state},HOBJECT {obj}) = eps',
        f'$dynamic_runtime_object({state},{obj})',
        f'$dynamic_define_value_class({state},POBJECT {obj}) = (PVOBJECT)']


def receipt(state, call, label, nonce):
    return [f'{call}.OWNER = (n_{label})', f'{call}.SELECTION = ({nonce})',
        f'{state}.SELECTEDCALLS[{nonce}] = pselectedcall_{label}',
        f'pselectedcall_{label}.NONCE = {nonce}', f'pselectedcall_{label}.OWNER = (n_{label})',
        f'pselectedcall_{label}.KIND = INTRINSIC_DEFINE',
        f'pselectedcall_{label}.SITE = {call}.SITE', f'pselectedcall_{label}.LINE = {call}.LINE',
        f'pselectedcall_{label}.DEPTH = 0', f'pselectedcall_{label}.ORIGINAL = eps',
        f'pselectedcall_{label}.LOOKUP = $ptascii("define")',
        f'$selected_entry_source_valid({state},pselectedcall_{label})',
        f'$selected_entry_active_valid({state},pselectedcall_{label})',
        f'$config_selected_valid({state},{call})']


def controls():
    return [
        '~$global_constant_class_supported(PVOBJECT)',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_b)]',
        '$dynamic_define_value_class(S_dead,POBJECT n_b) = eps',
        '~$dynamic_runtime_object(S,|S.OBJECTS|)',
        'pclosurescope_bad = {OBJECT n_b,LEXICAL pconfigcall.SITE,CALLED pconfigcall.SITE,RECEIVER eps,CREATION eps}',
        'S_scope = S[.CLOSURESCOPES = [pclosurescope_bad]]',
        '$typed_closure(S_scope,n_b)', '~$dynamic_runtime_object(S_scope,n_b)',
        'pclosurebinding_bad = {OBJECT n_b,SITE pconfigcall.SITE,SOURCE n_b,LEXICAL eps,CALLED eps,RECEIVER eps}',
        'S_binding = S[.CLOSUREBINDINGS = [pclosurebinding_bad]]',
        '$typed_closure(S_binding,n_b)', '~$dynamic_runtime_object(S_binding,n_b)',
        'pconstantclosure_bad = {OBJECT n_b,SITE pconfigcall.SITE,DECL pconfigcall.SITE,PREFIX (|S.DECLARATIONS|)}',
        'S_record = S[.CONSTANTCLOSURES = [pconstantclosure_bad]]',
        '~$dynamic_runtime_object(S_record,n_b)',
        '$dynamic_define_value_class(S_record,POBJECT n_b) = eps',
        'S_wrapped = S[.OBJECTS[n_b] = CONSTANTCLOSURE pconfigcall.SITE (INTRINSICCLOSURE INTRINSIC_DEFINE)]',
        '~$dynamic_runtime_object(S_wrapped,n_b)',
        '$dynamic_define_value_class(S_wrapped,POBJECT n_b) = eps',
        'S_current = S[.OBJECTS[n_b] = INTRINSICCLOSURE INTRINSIC_CLOSURE_CURRENT]',
        '~$typed_closure(S_current,n_b)', '~$dynamic_runtime_object(S_current,n_b)',
        '~$config_selected_valid(S,pconfigcall_capture[.OWNER = (n_b)])',
        'S_other = S[.SELECTEDCALLS[0] = pselectedcall_a[.OWNER = (n_b)]]',
        '$selected_entry_source_valid(S_other,S_other.SELECTEDCALLS[0])',
        '~$config_selected_valid(S_other,pconfigcall_capture)',
        '~$config_selected_valid(S,pconfigcall_capture[.OWNER = eps])',
        '~$config_selected_valid(S,pconfigcall_capture[.SELECTION = eps])',
        'S_clear = S[.SELECTEDCALLS[0] = pselectedcall_a[.OWNER = eps]]',
        '~$selected_entry_source_valid(S_clear,S_clear.SELECTEDCALLS[0])',
        'S_missing = S[.SELECTEDCALLS = eps][.SELECTSEQ = 0]',
        '$heap_graph(S_missing) = $heap_graph(S)',
        '~$config_selected_valid(S_missing,pconfigcall_capture)',
        '~$dynamic_owned_define_valid(S_missing,pconfigcall)']


def checks(initial, stdout):
    begin = b'B|distinct|'
    before = begin + b'N|held|held|'
    thrown = before + b'H|2|held|held|17|'
    recovered = thrown + (b'E|same|STOP|none|v98ReviewReport|define|__invoke|'
        b'V98_REVIEW_OLD|false|rawsame|gone|held|same-value|defined|null|97|17|')
    writing = recovered + b'R|held|'
    kept = writing + b'T|held|constant|23|'
    assert stdout == kept + b'gone|gone|Q|17|23|1|97|A|'
    values = [*initial, *reach('S_capture','S_initial',0),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        *receipt('S_capture','pconfigcall_capture','a',0),
        'S_capture.SELECTEDCALLS = [pselectedcall_a]', 'S_capture.SELECTSEQ = 1',
        'pconfigcall_capture.SENT = [NAMED_SENT (KNOWN pvalue_old_name),NAMED_SENT (KNOWN (POBJECT n_b))]',
        '$string_bytes(pvalue_old_name) = (' + text(OLD) + ')',
        'n_a =/= n_b', *intrinsic('S_capture','n_a'), *intrinsic('S_capture','n_b'),
        'S_capture.CONSTANTCLOSURES = eps',
        '$lookup(S_capture.ENV,$ptascii("call")) = (n_call)',
        '$lookup(S_capture.ENV,$ptascii("value")) = (n_value)',
        '$lookup(S_capture.ENV,$ptascii("weakA")) = (n_weak_a_cv)',
        '$lookup(S_capture.ENV,$ptascii("weakB")) = (n_weak_b_cv)',
        '$lookup(S_capture.ENV,$ptascii("chosen")) = (n_chosen)',
        '$lookup(S_capture.ENV,$ptascii("calls")) = (n_calls)',
        '$lookup(S_capture.ENV,$ptascii("result")) = (n_result)',
        'S_capture.STORE[n_call] = DEFINED (POBJECT n_a)',
        'S_capture.STORE[n_value] = DEFINED (POBJECT n_b)',
        'S_capture.STORE[n_weak_a_cv] = DEFINED (POBJECT n_weak_a)',
        'S_capture.STORE[n_weak_b_cv] = DEFINED (POBJECT n_weak_b)',
        'S_capture.OBJECTS[n_weak_a] = WEAKREFERENCE (n_a)',
        'S_capture.OBJECTS[n_weak_b] = WEAKREFERENCE (n_b)',
        '$node_children(S_capture,HOBJECT n_weak_a) = eps',
        '$node_children(S_capture,HOBJECT n_weak_b) = eps',
        '$config_nodes(pconfigcall_capture) = [HOBJECT n_b,HOBJECT n_a]',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_a) = 2',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_b) = 2',
        'S_capture.USERCONSTANTS = [puserconstant_old]',
        'puserconstant_old.NAME = ' + text(OLD),
        'puserconstant_old.VALUE = PINT 17', 'puserconstant_old.CLASS = PVSCALAR',
        '$test_outputs(S_capture.EVENTS) = ' + term(begin),
        *reach('S','S_capture',1),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        'pconfigcall.OWNER = (n_a)', 'pconfigcall.SELECTION = (0)',
        '$dynamic_define_values(pconfigcall) = ((' + text(OLD) + ',POBJECT n_b))',
        '$config_method_receiver(S,pconfigcall)', '$config_invoke_valid(S,pconfigcall)',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        '$dynamic_owned_define_header(S,pconfigcall)', '$dynamic_owned_define_valid(S,pconfigcall)',
        '$dynamic_constant_duplicate_valid(S,pconfigcall,1)',
        'S.STORE[n_call] = DEFINED pvalue_call', '$string_bytes(pvalue_call) = ($ptascii("defined"))',
        'S.STORE[n_value] = DEFINED PNULL', 'S.STORE[n_chosen] = DEFINED PNULL',
        'S.STORE[n_calls] = DEFINED (PINT 0)', 'S.STORE[n_result] = DEFINED (PINT 97)',
        '$config_nodes(pconfigcall) = [HOBJECT n_b,HOBJECT n_a]',
        '$heap_owners($heap_graph(S),HOBJECT n_a) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_b) = 1',
        '~$destructor_operational(S)', '$test_outputs(S.EVENTS) = ' + term(before),
        *controls(),
        *common.step('S_dispatch','S'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_initial*',
        'perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall 1',
        '$error_call_valid(S_dispatch,perrorcall)', 'perrorcall.LEVEL = 2',
        'S_dispatch.USERCONSTANTS = S_capture.USERCONSTANTS',
        *reach('S_throw','S_dispatch',2),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_done) :: ptask_throw*',
        'perrorcall_done.RESUME = perrorcall.RESUME',
        'S_throw.STORE[n_chosen] = DEFINED (POBJECT n_error)',
        'S_throw.STORE[n_calls] = DEFINED (PINT 1)', 'S_throw.STORE[n_result] = DEFINED (PINT 97)',
        'S_throw.OBJECTS[n_error] = THROWABLE pthrowable_error', 'pthrowable_error.KIND = "Exception"',
        '$throwable_chain_valid(S_throw,n_error)',
        '$throwable_field(S_throw,n_error,"previous") = PNULL',
        '$string_bytes($throwable_field(S_throw,n_error,"message")) = ($ptascii("STOP"))',
        '$throwable_field(S_throw,n_error,"trace") = PARRAY n_trace',
        '|S_throw.ARRAYS[n_trace].ITEMS| = 3',
        '$entry_lookup(S_throw.ARRAYS[n_trace].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_report))',
        '$entry_lookup(S_throw.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_frame_api))',
        '$entry_lookup(S_throw.ARRAYS[n_trace].ITEMS,KINT 2) = (DIRECT (PARRAY n_frame_invoke))',
        '$trace_array_field(S_throw,n_frame_report,$ptascii("function")) = PSTRING ($ptascii("v98ReviewReport"))',
        '$trace_array_field(S_throw,n_frame_api,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_throw,n_frame_invoke,$ptascii("function")) = PSTRING ($ptascii("__invoke"))',
        '$trace_array_field(S_throw,n_frame_api,$ptascii("args")) = PARRAY n_args_api',
        '$trace_array_field(S_throw,n_frame_invoke,$ptascii("args")) = PARRAY n_args_invoke',
        '$entry_lookup(S_throw.ARRAYS[n_args_api].ITEMS,KINT 0) = (DIRECT pvalue_trace_name)',
        '$string_bytes(pvalue_trace_name) = (' + text(OLD) + ')',
        '$entry_lookup(S_throw.ARRAYS[n_args_api].ITEMS,KINT 1) = (DIRECT (POBJECT n_b))',
        '$entry_lookup(S_throw.ARRAYS[n_args_api].ITEMS,KINT 2) = (DIRECT (PBOOL false))',
        '$strict_check(S_throw,PARRAY n_args_api,PARRAY n_args_invoke,eps) = COMPARED true',
        '$heap_edge_owners(HOBJECT n_b,$heap_graph(S_throw).EDGES,[HARRAY n_args_api,HARRAY n_args_invoke]) = 2',
        '$heap_owners($heap_graph(S_throw),HOBJECT n_b) = 3',
        '$heap_owners($heap_graph(S_throw),HOBJECT n_a) = 1',
        '$test_outputs(S_throw.EVENTS) = ' + term(thrown),
        'S_pause = $drive_steps(S_throw,0)', 'S_pause = S_throw[.COMPLETION = BUDGET]',
        '$test_running(S_pause) = S_throw',
        *common.step('S_drop','S_throw'), *common.public('S_drop'),
        '$drive_steps($test_running(S_pause),1) = S_drop_found',
        'S_drop.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
        'S_drop.DESTRUCTION.OPERATIONS = eps', 'S_drop.DESTRUCTION.RELEASES = eps',
        'S_drop.USERCONSTANTS = S_capture.USERCONSTANTS',
        'S_drop.OBJECTS[n_error] = THROWABLE pthrowable_error',
        '~(HOBJECT n_a <- S_drop.ALLOCATIONS)', 'HOBJECT n_b <- S_drop.ALLOCATIONS',
        '$weakref_get(S_drop,n_weak_a) = PNULL', '$weakref_get(S_drop,n_weak_b) = POBJECT n_b',
        '$heap_owners($heap_graph(S_drop),HOBJECT n_b) = 2',
        '$selected_entry_source_valid(S_drop,pselectedcall_a)',
        '$test_outputs(S_drop.EVENTS) = ' + term(thrown),
        *reach('S_recovery','S_drop',3),
        'S_recovery.TODO = (CONFIG_ARGS pconfigcall_recovery) :: ptask_recovery*',
        *receipt('S_recovery','pconfigcall_recovery','b',1),
        'S_recovery.SELECTEDCALLS = [pselectedcall_a,pselectedcall_b]',
        'S_recovery.SELECTSEQ = 2', 'pconfigcall_recovery.SENT = eps',
        '$lookup(S_recovery.ENV,$ptascii("raw")) = (n_raw)',
        'S_recovery.STORE[n_raw] = DEFINED (POBJECT n_b)',
        'S_recovery.STORE[n_call] = DEFINED (POBJECT n_b)',
        '$throwable_field(S_recovery,n_error,"trace") = PARRAY n_trace',
        '$weakref_get(S_recovery,n_weak_a) = PNULL',
        'S_recovery.USERCONSTANTS = S_capture.USERCONSTANTS',
        '$test_outputs(S_recovery.EVENTS) = ' + term(recovered),
        *reach('S_write','S_recovery',4),
        'S_write.TODO = (CONFIG_INVOKE pconfigcall_write) :: ptask_write*',
        'pconfigcall_write.OWNER = (n_b)', 'pconfigcall_write.SELECTION = (1)',
        '$dynamic_define_values(pconfigcall_write) = ((' + text(NEW) + ',PINT 23))',
        '~$config_method_receiver(S_write,pconfigcall_write)',
        '$dynamic_owned_define_valid(S_write,pconfigcall_write)',
        'S_write.STORE[n_call] = DEFINED pvalue_replaced', '$string_bytes(pvalue_replaced) = ($ptascii("constant"))',
        '$heap_owners($heap_graph(S_write),HOBJECT n_b) = 4',
        '$test_outputs(S_write.EVENTS) = ' + term(writing),
        *common.step('S_row','S_write','PBOOL true'),
        'S_row.TODO = ptask_write*',
        'S_row.USERCONSTANTS = [puserconstant_old,puserconstant_new]',
        'puserconstant_new.NAME = ' + text(NEW), 'puserconstant_new.ORIGIN = pconfigcall_write.SITE',
        'puserconstant_new.VALUE = PINT 23', 'puserconstant_new.CLASS = PVSCALAR',
        'puserconstant_new.READS = eps', 'puserconstant_new.RECEIVES = eps',
        '$heap_owners($heap_graph(S_row),HOBJECT n_b) = 3',
        *runtime.unset('S_kept','S_row','raw'),
        '$test_outputs(S_kept.EVENTS) = ' + term(kept),
        '$throwable_field(S_kept,n_error,"trace") = PARRAY n_trace',
        'S_kept.STORE[n_raw] = DEFINED (POBJECT n_b)',
        *common.reach('S_query','S_kept',0,NEW), *common.public('S_query'),
        '$test_outputs(S_query.EVENTS) = ' + term(kept + b'gone|gone|Q|17|'),
        'S_query.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_query.SELECTEDCALLS = [pselectedcall_a,pselectedcall_b]',
        '$selected_entry_source_valid(S_query,pselectedcall_a)',
        '$selected_entry_source_valid(S_query,pselectedcall_b)',
        '$dynamic_define_source(S_query,pconfigcall_write.SITE)',
        '$dynamic_global_constant_value(S_query,' + text(NEW) + ') = (PINT 23)',
        '~(HOBJECT n_a <- S_query.ALLOCATIONS)', '~(HOBJECT n_b <- S_query.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_query.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_query.ALLOCATIONS)',
        '~(HARRAY n_args_api <- S_query.ALLOCATIONS)', '~(HARRAY n_args_invoke <- S_query.ALLOCATIONS)',
        '$weakref_get(S_query,n_weak_a) = PNULL', '$weakref_get(S_query,n_weak_b) = PNULL',
        'S_query_missing = S_query[.SELECTEDCALLS = eps][.SELECTSEQ = 0]',
        '~$user_constants_valid(S_query_missing,S_query_missing.USERCONSTANTS)',
        '$heap_graph(S_query_missing) = $heap_graph(S_query)',
        *common.step('S_value','S_query','PINT 23'),
        *define.finish('S_value',stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_final.SELECTEDCALLS = [pselectedcall_a,pselectedcall_b]',
        '$selected_log_valid(S_final,S_final.SELECTEDCALLS,0)',
        '~(HOBJECT n_a <- S_final.ALLOCATIONS)', '~(HOBJECT n_b <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_weak_a <- S_final.ALLOCATIONS)', '~(HOBJECT n_weak_b <- S_final.ALLOCATIONS)']
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
