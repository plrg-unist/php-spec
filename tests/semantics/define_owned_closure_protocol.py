#!/usr/bin/env python3
"""Reached owned DEFINE selection, nonowning history and same-site replay."""
import argparse
from pathlib import Path
import sys

import define_runtime_object_protocol as runtime
import define_stdclass_array_duplicate_protocol as prior
import define_owned_closure_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
DIRECT = sources.DIRECT
PREFIX = define.PREFIX + r'''
dec $test_owned_define_front(pstate, nat) : bool
def $test_owned_define_front(S,0) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.INDEX = 0
def $test_owned_define_front(S,1) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.INDEX = 2
  -- if $named_slot_at(pconfigcall.SENT,0) = NAMED_HOLE
def $test_owned_define_front(S,n_phase) = false -- otherwise
dec $test_owned_define_seek(pstate, nat, nat) : pstate
def $test_owned_define_seek(S,n_phase,0) = S
def $test_owned_define_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_owned_define_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_owned_define_seek(S,n_phase,n) = $test_owned_define_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_owned_define_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def capture(state, start, phase=0):
    return [f'{state}_found = $test_owned_define_seek({start},{phase},1000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_owned_define_front({state},{phase})', *common.public(state)]


def receipt(state, call, label, nonce, depth):
    return [f'{call}.OWNER = (n_{label})', f'{call}.SELECTION = ({nonce})',
        f'{state}.SELECTEDCALLS[{nonce}] = pselectedcall_{label}',
        f'pselectedcall_{label}.NONCE = {nonce}',
        f'pselectedcall_{label}.OWNER = (n_{label})',
        f'pselectedcall_{label}.KIND = INTRINSIC_DEFINE',
        f'pselectedcall_{label}.SITE = {call}.SITE',
        f'pselectedcall_{label}.LINE = {call}.LINE',
        f'pselectedcall_{label}.DEPTH = {depth}',
        f'pselectedcall_{label}.ORIGINAL = eps',
        f'pselectedcall_{label}.LOOKUP = $ptascii("define")',
        f'{state}.OBJECTS[n_{label}] = INTRINSICCLOSURE INTRINSIC_DEFINE',
        f'HOBJECT n_{label} <- {state}.ALLOCATIONS',
        f'$node_children({state},HOBJECT n_{label}) = eps',
        f'$selected_entry_source_valid({state},pselectedcall_{label})',
        f'$selected_entry_active_valid({state},pselectedcall_{label})',
        f'$config_selected_valid({state},{call})']


def controls():
    return [
        '~$config_selected_valid(S,pconfigcall[.OWNER = eps])',
        '~$config_selected_valid(S,pconfigcall[.SELECTION = eps])',
        '~$config_selected_valid(S,pconfigcall[.SELECTION = (|S.SELECTEDCALLS|)])',
        '~$config_selected_valid(S,pconfigcall[.LINE = $(pconfigcall.LINE + 1)])',
        'S_no_history = S[.SELECTEDCALLS = eps][.SELECTSEQ = 0]',
        '$heap_graph(S_no_history) = $heap_graph(S)',
        '~$config_selected_valid(S_no_history,pconfigcall)',
        '~$dynamic_define_source(S_no_history,pconfigcall.SITE)',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_first)]',
        '$selected_entry_source_valid(S_dead,pselectedcall_first)',
        '~$config_selected_valid(S_dead,pconfigcall)',
        'S_clear = S[.SELECTEDCALLS[0] = pselectedcall_first[.OWNER = eps]]',
        '~$selected_entry_source_valid(S_clear,S_clear.SELECTEDCALLS[0])',
        '~$config_selected_valid(S_clear,pconfigcall)',
        'S_string = S[.SELECTEDCALLS[0] = pselectedcall_first[.ORIGINAL = $ptascii("define")]]',
        '~$selected_entry_source_valid(S_string,S_string.SELECTEDCALLS[0])',
        'S_depth = S[.SELECTEDCALLS[0] = pselectedcall_first[.DEPTH = 1]]',
        '$selected_entry_source_valid(S_depth,S_depth.SELECTEDCALLS[0])',
        '~$selected_entry_active_valid(S_depth,S_depth.SELECTEDCALLS[0])',
        'S_twice = S[.TODO = (CONFIG_INVOKE pconfigcall) :: S.TODO]',
        '~$selected_entry_active_valid(S_twice,pselectedcall_first)',
        'pselectedcall_newer = pselectedcall_first[.NONCE = 1]',
        'S_stale = S[.SELECTEDCALLS = [pselectedcall_first,pselectedcall_newer]][.SELECTSEQ = 2]',
        '$selected_newer_same_owner(S_stale.SELECTEDCALLS,pselectedcall_first)',
        '~$config_selected_valid(S_stale,pconfigcall)',
        '$dynamic_owned_define_valid(S,pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,1,KNOWN (POBJECT n_first))])',
        '~$dynamic_owned_define_valid(S,pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN (PBOOL true))])',
        '~$dynamic_owned_define_valid(S,pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN PNULL)])',
        '~$dynamic_owned_define_valid(S,pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN (PINT 0))])',
        'pvalue_bad_name = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("V93_OWNED"))',
        'pconfigcall_bad_name = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,0,KNOWN pvalue_bad_name)]',
        '$config_invoke_valid(S,pconfigcall_bad_name)',
        '~$dynamic_owned_define_valid(S,pconfigcall_bad_name)']


def transfer(state, start, owner, value, tail):
    return [*common.step(state, start), *common.public(state),
        f'{state}.TODO = {tail}',
        f'{state}.RESULT = KNOWN (PBOOL {value})',
        f'~(HOBJECT {owner} <- {state}.ALLOCATIONS)',
        f'{state}.SELECTEDCALLS = {start}.SELECTEDCALLS',
        f'{state}.OBJECTS = {start}.OBJECTS', f'{state}.STORE = {start}.STORE',
        f'{state}.EVENTS = {start}.EVENTS']


def direct(initial, stdout):
    values = [*initial, *capture('S_capture','S_initial'),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        *receipt('S_capture','pconfigcall_capture','first',0,0),
        'S_capture.SELECTEDCALLS = [pselectedcall_first]', 'S_capture.SELECTSEQ = 1',
        'S_capture.USERCONSTANTS = eps', 'pconfigcall_capture.SENT = eps',
        '$lookup(S_capture.ENV,$ptascii("call")) = (n_call)',
        '$lookup(S_capture.ENV,$ptascii("value")) = (n_value)',
        '$lookup(S_capture.ENV,$ptascii("calls")) = (n_calls)',
        'S_capture.STORE[n_call] = DEFINED (POBJECT n_first)',
        'S_capture.STORE[n_value] = DEFINED (PINT 17)',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_first) = 2',
        *capture('S_args','S_capture',1),
        'S_args.TODO = (CONFIG_ARGS pconfigcall_args) :: ptask_capture*',
        'pconfigcall_args.OWNER = (n_first)', 'pconfigcall_args.SELECTION = (0)',
        'pconfigcall_args.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (PINT 17)),NAMED_SENT (KNOWN (PBOOL false))]',
        'pconfigcall_args.NAMED', 'S_args.SELECTEDCALLS = S_capture.SELECTEDCALLS',
        'S_args.STORE[n_call] = DEFINED (POBJECT n_first)',
        'S_args.STORE[n_value] = DEFINED (PINT 17)',
        *define.reach('S','S_args',0,'V93_OWNED'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        'pconfigcall.OWNER = (n_first)', 'pconfigcall.SELECTION = (0)',
        '$dynamic_define_values(pconfigcall) = (($ptascii("V93_OWNED"),PINT 17))',
        '$dynamic_owned_define_valid(S,pconfigcall)',
        '$task_nodes(CONFIG_INVOKE pconfigcall) = [HOBJECT n_first]',
        'S.STORE[n_call] = DEFINED pvalue_call', '$string_bytes(pvalue_call) = ($ptascii("defined"))',
        'S.STORE[n_value] = DEFINED (PINT 31)', 'S.USERCONSTANTS = eps',
        'S.SELECTEDCALLS = S_capture.SELECTEDCALLS',
        '$heap_owners($heap_graph(S),HOBJECT n_first) = 1', *controls(),
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        '$test_running(S_pause) = S',
        *transfer('S_transfer','S','n_first','true','ptask_initial*'),
        '$drive_steps($test_running(S_pause),1) = S_transfer_found',
        'S_transfer.USERCONSTANTS = [puserconstant_row]',
        'puserconstant_row.NAME = $ptascii("V93_OWNED")',
        'puserconstant_row.ORIGIN = pconfigcall.SITE',
        'puserconstant_row.VALUE = PINT 17', 'puserconstant_row.CLASS = PVSCALAR',
        'puserconstant_row.READS = eps', 'puserconstant_row.RECEIVES = eps',
        *common.reach('S_query','S_transfer',0,'V93_OWNED'), *common.public('S_query'),
        'S_query.USERCONSTANTS = S_transfer.USERCONSTANTS',
        'S_query.SELECTEDCALLS = S_capture.SELECTEDCALLS',
        '~(HOBJECT n_first <- S_query.ALLOCATIONS)',
        'S_query.OBJECTS[n_first] = INTRINSICCLOSURE INTRINSIC_DEFINE',
        '$selected_entry_source_valid(S_query,pselectedcall_first)',
        '$selected_entry_active_valid(S_query,pselectedcall_first)',
        '$dynamic_define_source(S_query,pconfigcall.SITE)',
        '$dynamic_global_constant_value(S_query,$ptascii("V93_OWNED")) = (PINT 17)',
        'S_query_missing = S_query[.SELECTEDCALLS = eps][.SELECTSEQ = 0]',
        '$heap_graph(S_query_missing) = $heap_graph(S_query)',
        '~$user_constants_valid(S_query_missing,S_query_missing.USERCONSTANTS)',
        *common.step('S_value','S_query','PINT 17'),
        *capture('S_capture_second','S_value'),
        'S_capture_second.TODO = (CONFIG_ARGS pconfigcall_second) :: ptask_second*',
        *receipt('S_capture_second','pconfigcall_second','second',1,0),
        'n_first =/= n_second',
        'S_capture_second.SELECTEDCALLS = [pselectedcall_first,pselectedcall_second]',
        '~(HOBJECT n_first <- S_capture_second.ALLOCATIONS)',
        *define.reach('S_dup','S_capture_second',1,'V93_OWNED'),
        'S_dup.TODO = (CONFIG_INVOKE pconfigcall_dup) :: ptask_dup*',
        'pconfigcall_dup.OWNER = (n_second)', 'pconfigcall_dup.SELECTION = (1)',
        '$dynamic_define_values(pconfigcall_dup) = (($ptascii("V93_OWNED"),PINT 41))',
        '$dynamic_constant_duplicate_valid(S_dup,pconfigcall_dup,1)',
        'S_dup.STORE[n_call] = DEFINED pvalue_call_dup', '$string_bytes(pvalue_call_dup) = ($ptascii("constant"))',
        'S_dup.STORE[n_value] = DEFINED (PINT 53)',
        'S_dup.STORE[n_calls] = DEFINED (PINT 0)',
        '$heap_owners($heap_graph(S_dup),HOBJECT n_second) = 1',
        *common.step('S_dispatch','S_dup'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_dispatch*',
        'perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup 1',
        '$error_call_valid(S_dispatch,perrorcall)', 'perrorcall.LEVEL = 2',
        *define.reach('S_marker','S_dispatch',4,'V93_OWNED'),
        'S_marker.TODO = (DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup 1) :: ptask_dispatch*',
        'S_marker.STORE[n_calls] = DEFINED (PINT 1)',
        'S_marker.USERCONSTANTS = S_transfer.USERCONSTANTS',
        '$heap_owners($heap_graph(S_marker),HOBJECT n_second) = 1',
        '$test_outputs(S_marker.EVENTS) = '+term(b'B|N|1|T|17|defined|31|N|2|H|2|17|53|'),
        *transfer('S_false','S_marker','n_second','false','ptask_dispatch*'),
        'S_false.USERCONSTANTS = S_transfer.USERCONSTANTS',
        *common.reach('S_last_query','S_false',0,'V93_OWNED'), *common.public('S_last_query'),
        '~(HOBJECT n_second <- S_last_query.ALLOCATIONS)',
        '$selected_entry_source_valid(S_last_query,pselectedcall_second)',
        '$dynamic_global_constant_value(S_last_query,$ptascii("V93_OWNED")) = (PINT 17)',
        *define.finish('S_last_query',stdout),
        'S_final.USERCONSTANTS = S_transfer.USERCONSTANTS',
        'S_final.SELECTEDCALLS = [pselectedcall_first,pselectedcall_second]',
        'S_final.SELECTSEQ = 2',
        '~(HOBJECT n_first <- S_final.ALLOCATIONS)', '~(HOBJECT n_second <- S_final.ALLOCATIONS)',
        '$selected_log_valid(S_final,S_final.SELECTEDCALLS,0)']
    return values


def repeated(initial, stdout):
    return [*initial, *capture('S_capture','S_initial'),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        'S_capture.CURRENT = (pcallcontext_first)', 'S_capture.FRAMES = [pframe_first]',
        *receipt('S_capture','pconfigcall_capture','first',0,1),
        *define.reach('S','S_capture',0,'V93_REPEAT'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        'pconfigcall.OWNER = (n_first)', 'pconfigcall.SELECTION = (0)',
        '~pconfigcall.NAMED', '|pconfigcall.SENT| = 2',
        '$dynamic_define_values(pconfigcall) = (($ptascii("V93_REPEAT"),PINT 23))',
        '$dynamic_owned_define_valid(S,pconfigcall)',
        '$heap_owners($heap_graph(S),HOBJECT n_first) = 2',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]', '$test_running(S_pause) = S',
        *common.step('S_row','S','PBOOL true'),
        '$drive_steps($test_running(S_pause),1) = S_row_found',
        'S_row.USERCONSTANTS = [puserconstant_row]',
        'puserconstant_row.ORIGIN = pconfigcall.SITE',
        'puserconstant_row.VALUE = PINT 23', 'puserconstant_row.CLASS = PVSCALAR',
        '$heap_owners($heap_graph(S_row),HOBJECT n_first) = 1',
        *common.reach('S_query','S_row',0,'V93_REPEAT'), *common.public('S_query'),
        'S_query.CURRENT = eps', 'S_query.FRAMES = eps',
        '~(HOBJECT n_first <- S_query.ALLOCATIONS)',
        '$selected_entry_source_valid(S_query,pselectedcall_first)',
        '$selected_entry_active_valid(S_query,pselectedcall_first)',
        '$dynamic_global_constant_value(S_query,$ptascii("V93_REPEAT")) = (PINT 23)',
        *common.step('S_value','S_query','PINT 23'),
        *capture('S_capture_second','S_value'),
        'S_capture_second.TODO = (CONFIG_ARGS pconfigcall_second) :: ptask_second*',
        *receipt('S_capture_second','pconfigcall_second','second',1,1),
        'n_first =/= n_second',
        'pselectedcall_second.SITE = pselectedcall_first.SITE',
        'S_capture_second.SELECTEDCALLS = [pselectedcall_first,pselectedcall_second]',
        '$selected_newer_same_owner(S_capture_second.SELECTEDCALLS,pselectedcall_first)',
        '$selected_entry_source_valid(S_capture_second,pselectedcall_first)',
        '$selected_entry_active_valid(S_capture_second,pselectedcall_first)',
        '~$config_selected_valid(S_capture_second,pconfigcall)',
        *define.reach('S_dup','S_capture_second',1,'V93_REPEAT'),
        'S_dup.TODO = (CONFIG_INVOKE pconfigcall_dup) :: ptask_dup*',
        'pconfigcall_dup.OWNER = (n_second)', 'pconfigcall_dup.SELECTION = (1)',
        '$dynamic_define_values(pconfigcall_dup) = (($ptascii("V93_REPEAT"),PINT 31))',
        '$dynamic_constant_duplicate_valid(S_dup,pconfigcall_dup,1)',
        '$heap_owners($heap_graph(S_dup),HOBJECT n_second) = 2',
        *define.reach('S_marker','S_dup',4,'V93_REPEAT'),
        'S_marker.TODO = (DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup 1) :: ptask_tail*',
        '$heap_owners($heap_graph(S_marker),HOBJECT n_second) = 2',
        *common.step('S_false','S_marker','PBOOL false'),
        '$heap_owners($heap_graph(S_false),HOBJECT n_second) = 1',
        *common.reach('S_last_query','S_false',0,'V93_REPEAT'), *common.public('S_last_query'),
        'S_last_query.CURRENT = eps', 'S_last_query.FRAMES = eps',
        '~(HOBJECT n_first <- S_last_query.ALLOCATIONS)', '~(HOBJECT n_second <- S_last_query.ALLOCATIONS)',
        '$dynamic_global_constant_value(S_last_query,$ptascii("V93_REPEAT")) = (PINT 23)',
        *define.finish('S_last_query',stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_final.SELECTEDCALLS = [pselectedcall_first,pselectedcall_second]',
        'S_final.SELECTSEQ = 2', '$selected_log_valid(S_final,S_final.SELECTEDCALLS,0)']


def checks(initial, name, stdout):
    return (direct if name == DIRECT else repeated)(initial, stdout)


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = runtime.packet_process


def process(command, directory, timeout, cwd):
    if directory.parent.name in sources.family.CASES:
        timeout = 240 if directory.parent.name == DIRECT else 180
    return packet_process(command, directory, timeout, cwd)


packet.process = process
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--case', choices=sources.family.CASES)
    args, remaining = parser.parse_known_args()
    if args.case:
        sources.family.CASES = {args.case: sources.family.CASES[args.case]}
    sys.argv = [sys.argv[0], *remaining]
    raise SystemExit(0 if packet.main() else 1)
