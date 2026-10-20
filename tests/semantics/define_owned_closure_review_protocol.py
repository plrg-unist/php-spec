#!/usr/bin/env python3
"""Owned DEFINE identity, weak lifetime, raw throw frames and legacy selection."""
from pathlib import Path

import define_runtime_closure_protocol as runtime
import define_stdclass_array_duplicate_review_protocol as prior
import define_owned_closure_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
TARGET = 'V93_REVIEW_OWNED'
CASE = 'owned-define-explicit-capture-receipts-and-weak-owner-retirement'
PREFIX = runtime.PREFIX + r'''
dec $test_owned_peer_front(pstate, nat) : bool
def $test_owned_peer_front(S,0) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.INDEX = 0
  -- if pconfigcall.SELECTION = (0) /\ pconfigcall.OWNER =/= eps
def $test_owned_peer_front(S,1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.SELECTION = (0)
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V93_REVIEW_OWNED"),PINT 23))
def $test_owned_peer_front(S,2) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.INDEX = 0
  -- if pconfigcall.SELECTION = (1) /\ pconfigcall.OWNER =/= eps
def $test_owned_peer_front(S,3) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.SELECTION = (1)
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V93_REVIEW_OWNED"),PINT 31))
def $test_owned_peer_front(S,4) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask_tail*
  -- if S.OBJECTS[n_error] = THROWABLE pthrowable
  -- if pthrowable.KIND = "Exception"
def $test_owned_peer_front(S,5) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINED /\ pconfigcall.OWNER = eps
  -- if pconfigcall.SELECTION = (2)
def $test_owned_peer_front(S,n_phase) = false -- otherwise
dec $test_owned_peer_seek(pstate, nat, nat) : pstate
def $test_owned_peer_seek(S,n_phase,0) = S
def $test_owned_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_owned_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_owned_peer_seek(S,n_phase,n) = $test_owned_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_owned_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_owned_peer_seek({start},{phase},1500)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_owned_peer_front({state},{phase})', *common.public(state)]


def receipt(state, call, label, nonce):
    return [f'{call}.OWNER = (n_{label})', f'{call}.SELECTION = ({nonce})',
        f'{state}.SELECTEDCALLS[{nonce}] = pselectedcall_{label}',
        f'pselectedcall_{label}.NONCE = {nonce}',
        f'pselectedcall_{label}.OWNER = (n_{label})',
        f'pselectedcall_{label}.KIND = INTRINSIC_DEFINE',
        f'pselectedcall_{label}.SITE = {call}.SITE',
        f'pselectedcall_{label}.LINE = {call}.LINE',
        f'pselectedcall_{label}.DEPTH = 0',
        f'pselectedcall_{label}.ORIGINAL = eps',
        f'pselectedcall_{label}.LOOKUP = $ptascii("define")',
        f'{state}.OBJECTS[n_{label}] = INTRINSICCLOSURE INTRINSIC_DEFINE',
        f'$selected_entry_source_valid({state},pselectedcall_{label})',
        f'$selected_entry_active_valid({state},pselectedcall_{label})',
        f'$config_selected_valid({state},{call})']


def controls():
    return [
        '~$config_selected_valid(S,pconfigcall_capture[.OWNER = (n_b)])',
        'S_other = S[.SELECTEDCALLS[0] = pselectedcall_a[.OWNER = (n_b)]]',
        '$selected_entry_source_valid(S_other,S_other.SELECTEDCALLS[0])',
        '~$config_selected_valid(S_other,pconfigcall_capture)',
        '~$config_selected_valid(S,pconfigcall_capture[.OWNER = eps])',
        '~$config_selected_valid(S,pconfigcall_capture[.SELECTION = eps])',
        'S_clear = S[.SELECTEDCALLS[0] = pselectedcall_a[.OWNER = eps]]',
        '~$selected_entry_source_valid(S_clear,S_clear.SELECTEDCALLS[0])',
        '~$config_selected_valid(S_clear,pconfigcall_capture)',
        'S_lookup = S[.SELECTEDCALLS[0] = pselectedcall_a[.LOOKUP = $ptascii("defined")]]',
        '~$selected_entry_source_valid(S_lookup,S_lookup.SELECTEDCALLS[0])',
        'S_original = S[.SELECTEDCALLS[0] = pselectedcall_a[.ORIGINAL = $ptascii("define")]]',
        '~$selected_entry_source_valid(S_original,S_original.SELECTEDCALLS[0])',
        'S_missing = S[.SELECTEDCALLS = eps][.SELECTSEQ = 0]',
        '~$config_selected_valid(S_missing,pconfigcall_capture)',
        '$heap_graph(S_missing) = $heap_graph(S)',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_a)]',
        '$selected_entry_source_valid(S_dead,pselectedcall_a)',
        '~$config_selected_valid(S_dead,pconfigcall_capture)',
        'S_bound = S[.SELECTEDCALLS[0] = pselectedcall_a[.OWNER = (|S.OBJECTS|)]]',
        '~$selected_entry_source_valid(S_bound,S_bound.SELECTEDCALLS[0])',
        '$dynamic_define_value_class(S,POBJECT n_a) = eps',
        '$node_children(S,HOBJECT n_weak_a) = eps',
        '$node_children(S,HOBJECT n_weak_b) = eps']


def checks(initial, stdout):
    first = b'B|N|1|held|'
    query_first = first + b'T|same|gone|'
    duplicate = query_first + b'23|47|N|2|held|'
    thrown = duplicate + b'H|2|23|held|'
    kept = thrown + b'E|same|STOP|none|v93ReviewReport|define|__invoke|V93_REVIEW_OWNED|31|false|rawsame|defined|53|97|1|'
    after = kept + b'gone|gone|'
    assert stdout == after + b'23|legacy|A|'
    values = [*initial, *reach('S','S_initial',0),
        'S.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        *receipt('S','pconfigcall_capture','a',0),
        'S.SELECTEDCALLS = [pselectedcall_a]', 'S.SELECTSEQ = 1',
        'pconfigcall_capture.SENT = eps', 'S.USERCONSTANTS = eps',
        '$lookup(S.ENV,$ptascii("call")) = (n_call)',
        '$lookup(S.ENV,$ptascii("replacement")) = (n_replacement)',
        '$lookup(S.ENV,$ptascii("weakA")) = (n_weak_a_cv)',
        '$lookup(S.ENV,$ptascii("weakB")) = (n_weak_b_cv)',
        '$lookup(S.ENV,$ptascii("value")) = (n_value)',
        '$lookup(S.ENV,$ptascii("phase")) = (n_phase)',
        '$lookup(S.ENV,$ptascii("calls")) = (n_calls)',
        'S.STORE[n_call] = DEFINED (POBJECT n_a)',
        'S.STORE[n_replacement] = DEFINED (POBJECT n_b)', 'n_a =/= n_b',
        'S.OBJECTS[n_b] = INTRINSICCLOSURE INTRINSIC_DEFINE',
        'S.STORE[n_weak_a_cv] = DEFINED (POBJECT n_weak_a)',
        'S.STORE[n_weak_b_cv] = DEFINED (POBJECT n_weak_b)',
        'S.OBJECTS[n_weak_a] = WEAKREFERENCE (n_a)',
        'S.OBJECTS[n_weak_b] = WEAKREFERENCE (n_b)',
        '$weakref_get(S,n_weak_a) = POBJECT n_a',
        '$weakref_get(S,n_weak_b) = POBJECT n_b',
        '$task_nodes(CONFIG_ARGS pconfigcall_capture) = [HOBJECT n_a]',
        *controls(),
        *reach('S_inv','S',1),
        'S_inv.TODO = (CONFIG_INVOKE pconfigcall_first) :: ptask_first*',
        'pconfigcall_first.OWNER = (n_a)', 'pconfigcall_first.SELECTION = (0)',
        '$dynamic_owned_define_valid(S_inv,pconfigcall_first)',
        '$dynamic_define_values(pconfigcall_first) = (($ptascii("V93_REVIEW_OWNED"),PINT 23))',
        'S_inv.STORE[n_call] = DEFINED (POBJECT n_b)',
        'S_inv.STORE[n_replacement] = DEFINED (POBJECT n_b)',
        'S_inv.STORE[n_value] = DEFINED (PINT 47)',
        'S_inv.STORE[n_phase] = DEFINED (PINT 1)',
        '$weakref_get(S_inv,n_weak_a) = POBJECT n_a',
        '$task_nodes(CONFIG_INVOKE pconfigcall_first) = [HOBJECT n_a]',
        '$heap_owners($heap_graph(S_inv),HOBJECT n_a) = 1',
        '$test_outputs(S_inv.EVENTS) = ' + term(first),
        'pconfigcall_name = pconfigcall_first[.SENT = $named_slot_set(pconfigcall_first.SENT,0,KNOWN (PSTRING ($ptascii("OTHER"))))]',
        '$config_invoke_valid(S_inv,pconfigcall_name)',
        '~$dynamic_owned_define_valid(S_inv,pconfigcall_name)',
        'pconfigcall_value = pconfigcall_first[.SENT = $named_slot_set(pconfigcall_first.SENT,1,KNOWN (POBJECT n_a))]',
        '~$dynamic_owned_define_valid(S_inv,pconfigcall_value)',
        'pconfigcall_flag = pconfigcall_first[.SENT = $named_slot_set(pconfigcall_first.SENT,2,KNOWN (PBOOL true))]',
        '~$dynamic_owned_define_valid(S_inv,pconfigcall_flag)',
        'S_pause = $drive_steps(S_inv,0)', 'S_pause = S_inv[.COMPLETION = BUDGET]',
        '$test_running(S_pause) = S_inv',
        *common.step('S_row','S_inv'), *common.public('S_row'),
        '$drive_steps($test_running(S_pause),1) = S_row_found',
        'S_row.TODO = ptask_first*',
        'S_row.RESULT = KNOWN (PBOOL true)',
        'S_row.USERCONSTANTS = [puserconstant_row]',
        'puserconstant_row.NAME = $ptascii("V93_REVIEW_OWNED")',
        'puserconstant_row.ORIGIN = pconfigcall_first.SITE',
        'puserconstant_row.VALUE = PINT 23', 'puserconstant_row.CLASS = PVSCALAR',
        'puserconstant_row.READS = eps', 'puserconstant_row.RECEIVES = eps',
        'S_row.SELECTEDCALLS = [pselectedcall_a]',
        '~(HOBJECT n_a <- S_row.ALLOCATIONS)',
        *common.reach('S_query','S_row',0,TARGET), *common.public('S_query'),
        '$test_outputs(S_query.EVENTS) = ' + term(query_first),
        '~(HOBJECT n_a <- S_query.ALLOCATIONS)',
        '$weakref_get(S_query,n_weak_a) = PNULL',
        '$selected_entry_source_valid(S_query,pselectedcall_a)',
        '$selected_entry_active_valid(S_query,pselectedcall_a)',
        '$dynamic_define_source(S_query,pconfigcall_first.SITE)',
        'S_query.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_query_missing = S_query[.SELECTEDCALLS = eps][.SELECTSEQ = 0]',
        '~$user_constants_valid(S_query_missing,S_query_missing.USERCONSTANTS)',
        '$heap_graph(S_query_missing) = $heap_graph(S_query)',
        *common.step('S_value','S_query','PINT 23'),
        *reach('S_second','S_value',2),
        'S_second.TODO = (CONFIG_ARGS pconfigcall_second_capture) :: ptask_second*',
        *receipt('S_second','pconfigcall_second_capture','b',1),
        'S_second.SELECTEDCALLS = [pselectedcall_a,pselectedcall_b]',
        'S_second.SELECTSEQ = 2',
        '$lookup(S_second.ENV,$ptascii("result")) = (n_result)',
        '$lookup(S_second.ENV,$ptascii("chosen")) = (n_chosen)',
        'S_second.STORE[n_result] = DEFINED (PINT 97)',
        'S_second.STORE[n_chosen] = DEFINED PNULL',
        *reach('S_dup','S_second',3),
        'S_dup.TODO = (CONFIG_INVOKE pconfigcall_dup) :: ptask_dup*',
        'pconfigcall_dup.OWNER = (n_b)', 'pconfigcall_dup.SELECTION = (1)',
        '$dynamic_owned_define_valid(S_dup,pconfigcall_dup)',
        '$dynamic_constant_duplicate_valid(S_dup,pconfigcall_dup,1)',
        'S_dup.STORE[n_call] = DEFINED pvalue_call',
        '$string_bytes(pvalue_call) = ($ptascii("defined"))',
        'S_dup.STORE[n_replacement] = DEFINED PNULL',
        'S_dup.STORE[n_value] = DEFINED (PINT 53)',
        'S_dup.STORE[n_phase] = DEFINED (PINT 2)',
        'S_dup.STORE[n_calls] = DEFINED (PINT 0)',
        '$weakref_get(S_dup,n_weak_b) = POBJECT n_b',
        '$heap_owners($heap_graph(S_dup),HOBJECT n_b) = 1',
        '$test_outputs(S_dup.EVENTS) = ' + term(duplicate),
        *reach('S_throw','S_dup',4),
        'S_throw.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
        'S_throw.STORE[n_chosen] = DEFINED (POBJECT n_error)',
        'S_throw.STORE[n_result] = DEFINED (PINT 97)',
        'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
        '$weakref_get(S_throw,n_weak_b) = POBJECT n_b',
        'S_throw.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_throw.SELECTEDCALLS = [pselectedcall_a,pselectedcall_b]',
        '$test_outputs(S_throw.EVENTS) = ' + term(thrown),
        'S_throw_pause = $drive_steps(S_throw,0)',
        'S_throw_pause = S_throw[.COMPLETION = BUDGET]',
        '$test_running(S_throw_pause) = S_throw',
        '$drive_steps($test_running(S_throw_pause),1) = $drive_steps(S_throw,1)',
        *runtime.unset('S_kept','S_throw','rawInvoke'),
        '$test_outputs(S_kept.EVENTS) = ' + term(kept),
        '$lookup(S_kept.ENV,$ptascii("error")) = (n_error_cv)',
        '$lookup(S_kept.ENV,$ptascii("trace")) = (n_trace_cv)',
        '$lookup(S_kept.ENV,$ptascii("rawApi")) = (n_api_cv)',
        '$lookup(S_kept.ENV,$ptascii("rawInvoke")) = (n_invoke_cv)',
        'S_kept.STORE[n_error_cv] = DEFINED (POBJECT n_error)',
        'S_kept.STORE[n_chosen] = DEFINED (POBJECT n_error)',
        'S_kept.STORE[n_trace_cv] = DEFINED (PARRAY n_trace)',
        'S_kept.STORE[n_api_cv] = DEFINED (PARRAY n_args_api)',
        'S_kept.STORE[n_invoke_cv] = DEFINED (PARRAY n_args_invoke)',
        '$throwable_field(S_kept,n_error,"previous") = PNULL',
        '$string_bytes($throwable_field(S_kept,n_error,"message")) = ($ptascii("STOP"))',
        '$throwable_field(S_kept,n_error,"trace") = PARRAY n_trace',
        '|S_kept.ARRAYS[n_trace].ITEMS| = 3',
        '$entry_lookup(S_kept.ARRAYS[n_trace].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_report))',
        '$entry_lookup(S_kept.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_frame_api))',
        '$entry_lookup(S_kept.ARRAYS[n_trace].ITEMS,KINT 2) = (DIRECT (PARRAY n_frame_invoke))',
        '$trace_array_field(S_kept,n_frame_report,$ptascii("function")) = PSTRING ($ptascii("v93ReviewReport"))',
        '$trace_array_field(S_kept,n_frame_api,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_kept,n_frame_invoke,$ptascii("function")) = PSTRING ($ptascii("__invoke"))',
        '$trace_array_field(S_kept,n_frame_api,$ptascii("args")) = PARRAY n_args_api',
        '$trace_array_field(S_kept,n_frame_invoke,$ptascii("args")) = PARRAY n_args_invoke',
        '$entry_lookup(S_kept.ARRAYS[n_args_api].ITEMS,KINT 0) = (DIRECT pvalue_name)',
        '$string_bytes(pvalue_name) = ($ptascii("V93_REVIEW_OWNED"))',
        '$entry_lookup(S_kept.ARRAYS[n_args_api].ITEMS,KINT 1) = (DIRECT (PINT 31))',
        '$entry_lookup(S_kept.ARRAYS[n_args_api].ITEMS,KINT 2) = (DIRECT (PBOOL false))',
        '$strict_check(S_kept,PARRAY n_args_api,PARRAY n_args_invoke,eps) = COMPARED true',
        'S_kept.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_kept.STORE[n_result] = DEFINED (PINT 97)',
        *common.reach('S_again','S_kept',0,TARGET), *common.public('S_again'),
        '$test_outputs(S_again.EVENTS) = ' + term(after),
        '$weakref_get(S_again,n_weak_a) = PNULL',
        '$weakref_get(S_again,n_weak_b) = PNULL',
        '~(HOBJECT n_a <- S_again.ALLOCATIONS)', '~(HOBJECT n_b <- S_again.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_again.ALLOCATIONS)',
        '$selected_entry_source_valid(S_again,pselectedcall_a)',
        '$selected_entry_source_valid(S_again,pselectedcall_b)',
        'S_again.USERCONSTANTS = S_row.USERCONSTANTS',
        *common.step('S_again_value','S_again','PINT 23'),
        *reach('S_legacy','S_again_value',5),
        'S_legacy.TODO = (CONFIG_INVOKE pconfigcall_legacy) :: ptask_legacy*',
        'S_legacy.SELECTEDCALLS = [pselectedcall_a,pselectedcall_b,pselectedcall_legacy]',
        'S_legacy.SELECTSEQ = 3',
        'pselectedcall_legacy.NONCE = 2', 'pselectedcall_legacy.OWNER = eps',
        'pselectedcall_legacy.KIND = INTRINSIC_DEFINED',
        'pselectedcall_legacy.ORIGINAL = $ptascii("defined")',
        'pselectedcall_legacy.LOOKUP = $ptascii("defined")',
        'pselectedcall_legacy.SITE = pconfigcall_legacy.SITE',
        'pselectedcall_legacy.LINE = pconfigcall_legacy.LINE',
        '$config_selected_valid(S_legacy,pconfigcall_legacy)',
        '$selected_entry_source_valid(S_legacy,pselectedcall_legacy)',
        '$selected_log_valid(S_legacy,S_legacy.SELECTEDCALLS,0)',
        *common.step('S_legacy_value','S_legacy','PBOOL true'),
        *define.finish('S_legacy_value',stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_final.SELECTEDCALLS = [pselectedcall_a,pselectedcall_b,pselectedcall_legacy]',
        '$selected_log_valid(S_final,S_final.SELECTEDCALLS,0)',
        '~(HOBJECT n_a <- S_final.ALLOCATIONS)', '~(HOBJECT n_b <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_weak_a <- S_final.ALLOCATIONS)', '~(HOBJECT n_weak_b <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)']
    return values


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = runtime.packet_process


def process(command, directory, timeout, cwd):
    if directory.parent.name == CASE:
        timeout = 300
    return packet_process(command, directory, timeout, cwd)


packet.process = process
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    raise SystemExit(0 if packet.main() else 1)
