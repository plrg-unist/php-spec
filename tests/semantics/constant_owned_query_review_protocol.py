#!/usr/bin/env python3
"""Captured CONSTANT Error/trace ownership and a later independent reader."""
from pathlib import Path

import define_runtime_closure_protocol as runtime
import define_stdclass_array_duplicate_review_protocol as prior
import typed_static_invoke_set_protocol as process_base
import constant_owned_query_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
CASE = sources.CASE
MISSING, REBOUND, LATE = 'V99_REVIEW_MISSING', 'V99_REVIEW_REBOUND', 'V99_REVIEW_LATE'
PREFIX = runtime.PREFIX + r'''
dec $test_owned_query_peer_front(pstate, nat) : bool
def $test_owned_query_peer_front(S,0) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.INDEX = 0 /\ $config_method_receiver(S,pconfigcall)
def $test_owned_query_peer_front(S,1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.OWNER =/= eps
  -- if $config_method_receiver(S,pconfigcall)
def $test_owned_query_peer_front(S,2) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.INDEX = 0 /\ ~$config_method_receiver(S,pconfigcall)
def $test_owned_query_peer_front(S,3) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT /\ pconfigcall.OWNER =/= eps
  -- if ~$config_method_receiver(S,pconfigcall)
def $test_owned_query_peer_front(S,n_phase) = false -- otherwise
dec $test_owned_query_peer_seek(pstate, nat, nat) : pstate
def $test_owned_query_peer_seek(S,n_phase,0) = S
def $test_owned_query_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_owned_query_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_owned_query_peer_seek(S,n_phase,n) = $test_owned_query_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_owned_query_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_owned_query_peer_seek({start},{phase},1500)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_owned_query_peer_front({state},{phase})', *common.public(state)]


def controls():
    # These source/shape projections are never driven. A live same-kind owner
    # is structural authority here; owned queries deliberately have no nonce.
    values = [
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_a)]',
        '~$config_selected_valid(S_dead,pconfigcall)',
        '~$dynamic_owned_global_query_valid(S_dead,pconfigcall)',
        'S_wrong = S[.OBJECTS[n_a] = INTRINSICCLOSURE INTRINSIC_DEFINED]',
        '~$config_selected_valid(S_wrong,pconfigcall)',
        '~$dynamic_owned_global_query_valid(S_wrong,pconfigcall)']
    for change in ['.OWNER = eps', '.OWNER = (|S.OBJECTS|)', '.SELECTION = (0)',
            '.KIND = INTRINSIC_DEFINED', '.KIND = INTRINSIC_DEFINE',
            '.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall.LINE + 1)', '.INDEX = 0']:
        values += [f'~$dynamic_owned_global_query_valid(S,pconfigcall[{change}])',
            f'~$dynamic_global_constant_valid(S,pconfigcall[{change}])']
    for index, value in enumerate(['PNULL', 'PINT 17', 'PSTRING ($ptascii("Unknown::VALUE"))',
            'PSTRING ($ptascii("__COMPILER_HALT_OFFSET__"))', 'PSTRING ([86,0,57])']):
        call = f'pconfigcall_bad_{index}'
        values += [f'{call} = pconfigcall[.SENT = [NAMED_SENT (KNOWN ({value}))]]']
        values += [f'~$dynamic_global_constant_call({call})',
            f'~$dynamic_owned_global_query_valid(S,{call})']
    values += ['~$dynamic_owned_global_query_valid(S,pconfigcall[.SENT = eps])',
        '~$dynamic_owned_global_query_valid(S,pconfigcall[.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN pvalue_name)]])']
    return values


def checks(initial, stdout):
    begin = b'B|'
    before = begin + b'N|held|'
    caught = before + (b'E|Undefined constant "V99_REVIEW_MISSING"|none|constant|__invoke|'
        b'V99_REVIEW_MISSING|rawsame|V99_REVIEW_REBOUND|defined|97|1|gone|absent|')
    reading = caught + b'R|held|'
    assert stdout == reading + b'23|null|gone|V99_REVIEW_MISSING|A|'
    values = [*initial, *reach('S_capture','S_initial',0),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        'pconfigcall_capture.OWNER = (n_a)', 'pconfigcall_capture.SELECTION = eps',
        'pconfigcall_capture.SENT = eps', 'pconfigcall_capture.PACKS = eps',
        'S_capture.SELECTEDCALLS = eps', 'S_capture.SELECTSEQ = 0',
        'S_capture.USERCONSTANTS = eps',
        'S_capture.OBJECTS[n_a] = INTRINSICCLOSURE INTRINSIC_CONSTANT',
        '$config_selected_valid(S_capture,pconfigcall_capture)',
        '$config_nodes(pconfigcall_capture) = [HOBJECT n_a]',
        '$lookup(S_capture.ENV,$ptascii("call")) = (n_call)',
        '$lookup(S_capture.ENV,$ptascii("name")) = (n_name)',
        '$lookup(S_capture.ENV,$ptascii("weak")) = (n_weak_cv)',
        '$lookup(S_capture.ENV,$ptascii("calls")) = (n_calls)',
        '$lookup(S_capture.ENV,$ptascii("result")) = (n_result)',
        'S_capture.STORE[n_call] = DEFINED (POBJECT n_a)',
        'S_capture.STORE[n_name] = DEFINED pvalue_original_name',
        '$string_bytes(pvalue_original_name) = (' + text(MISSING) + ')',
        'S_capture.STORE[n_weak_cv] = DEFINED (POBJECT n_weak_a)',
        'S_capture.STORE[n_calls] = DEFINED (PINT 0)',
        'S_capture.STORE[n_result] = DEFINED (PINT 97)',
        'S_capture.OBJECTS[n_weak_a] = WEAKREFERENCE (n_a)',
        '$node_children(S_capture,HOBJECT n_weak_a) = eps',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_a) = 2',
        '$test_outputs(S_capture.EVENTS) = ' + term(begin),
        *reach('S','S_capture',1),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        'pconfigcall.OWNER = (n_a)', 'pconfigcall.SELECTION = eps',
        'pconfigcall.PACKS = eps', '~pconfigcall.NAMED', 'pconfigcall.INDEX = 1',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name)]',
        '$string_bytes(pvalue_name) = (' + text(MISSING) + ')',
        '$dynamic_global_constant_known(S,pconfigcall.SITE) = eps',
        '$config_invoke_valid(S,pconfigcall)', '$dynamic_owned_global_query_valid(S,pconfigcall)',
        '$dynamic_global_constant_valid(S,pconfigcall)',
        '$dynamic_global_constant_value(S,' + text(MISSING) + ') = eps',
        'S.STORE[n_call] = DEFINED pvalue_call',
        '$string_bytes(pvalue_call) = ($ptascii("defined"))',
        'S.STORE[n_name] = DEFINED pvalue_rebound_name',
        '$string_bytes(pvalue_rebound_name) = (' + text(REBOUND) + ')',
        'S.STORE[n_calls] = DEFINED (PINT 1)', 'S.STORE[n_result] = DEFINED (PINT 97)',
        'S.SELECTEDCALLS = eps', 'S.SELECTSEQ = 0', 'S.USERCONSTANTS = eps',
        '$config_nodes(pconfigcall) = [HOBJECT n_a]',
        '$heap_owners($heap_graph(S),HOBJECT n_a) = 1',
        '$weakref_get(S,n_weak_a) = POBJECT n_a', '~$destructor_operational(S)',
        '$test_outputs(S.EVENTS) = ' + term(before),
        *controls(),
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        '$test_running(S_pause) = S',
        *common.step('S_error','S'), *common.public('S_error'),
        '$drive_steps($test_running(S_pause),1) = S_error_found',
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_initial*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'pthrowable_error.KIND = "Error"', 'pthrowable_error.ORIGIN = (pconfigcall.SITE)',
        '$throwable_chain_valid(S_error,n_error)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('Undefined constant "' + MISSING + '"') + ')',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"line") = PINT pconfigcall.LINE',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame_api)),ENTRY (KINT 1) (DIRECT (PARRAY n_frame_invoke))]',
        '$trace_array_field(S_error,n_frame_api,$ptascii("function")) = PSTRING ($ptascii("constant"))',
        '$trace_array_field(S_error,n_frame_invoke,$ptascii("function")) = PSTRING ($ptascii("__invoke"))',
        '$trace_array_field(S_error,n_frame_invoke,$ptascii("class")) = PSTRING ($ptascii("Closure"))',
        '$trace_array_field(S_error,n_frame_api,$ptascii("args")) = PARRAY n_args_api',
        '$trace_array_field(S_error,n_frame_invoke,$ptascii("args")) = PARRAY n_args_invoke',
        '$entry_lookup(S_error.ARRAYS[n_args_api].ITEMS,KINT 0) = (DIRECT pvalue_trace_name)',
        '$string_bytes(pvalue_trace_name) = (' + text(MISSING) + ')',
        '$strict_check(S_error,PARRAY n_args_api,PARRAY n_args_invoke,eps) = COMPARED true',
        '~(HOBJECT n_a <- S_error.ALLOCATIONS)', '$weakref_get(S_error,n_weak_a) = PNULL',
        '$heap_owners($heap_graph(S_error),HOBJECT n_a) = 0',
        'S_error.DESTRUCTION.OPERATIONS = eps', 'S_error.DESTRUCTION.RELEASES = eps',
        'S_error.STORE[n_result] = DEFINED (PINT 97)',
        'S_error.USERCONSTANTS = eps', 'S_error.SELECTEDCALLS = eps', 'S_error.SELECTSEQ = 0',
        'S_error.EVENTS = S.EVENTS',
        *reach('S_recovery','S_error',2),
        'S_recovery.TODO = (CONFIG_ARGS pconfigcall_recovery) :: ptask_recovery*',
        'pconfigcall_recovery.OWNER = (n_b)', 'n_b =/= n_a',
        'pconfigcall_recovery.SELECTION = eps', 'pconfigcall_recovery.SENT = eps',
        'S_recovery.OBJECTS[n_b] = INTRINSICCLOSURE INTRINSIC_CONSTANT',
        '$config_selected_valid(S_recovery,pconfigcall_recovery)',
        '$lookup(S_recovery.ENV,$ptascii("weakAgain")) = (n_weak_b_cv)',
        'S_recovery.STORE[n_weak_b_cv] = DEFINED (POBJECT n_weak_b)',
        'S_recovery.OBJECTS[n_weak_b] = WEAKREFERENCE (n_b)',
        'S_recovery.STORE[n_call] = DEFINED (POBJECT n_b)',
        '$weakref_get(S_recovery,n_weak_a) = PNULL',
        '$heap_owners($heap_graph(S_recovery),HOBJECT n_b) = 2',
        '$throwable_field(S_recovery,n_error,"trace") = PARRAY n_trace',
        'S_recovery.USERCONSTANTS = [puserconstant_late]',
        'puserconstant_late.NAME = ' + text(LATE),
        'puserconstant_late.VALUE = PINT 23', 'puserconstant_late.CLASS = PVSCALAR',
        '$dynamic_global_constant_value(S_recovery,' + text(LATE) + ') = (PINT 23)',
        'S_recovery.SELECTEDCALLS = eps', 'S_recovery.SELECTSEQ = 0',
        '$test_outputs(S_recovery.EVENTS) = ' + term(caught),
        *reach('S_read','S_recovery',3),
        'S_read.TODO = (CONFIG_INVOKE pconfigcall_read) :: ptask_read*',
        'pconfigcall_read.OWNER = (n_b)', 'pconfigcall_read.SELECTION = eps',
        'pconfigcall_read.SENT = [NAMED_SENT (KNOWN pvalue_late_name)]',
        '$string_bytes(pvalue_late_name) = (' + text(LATE) + ')',
        '$dynamic_global_constant_known(S_read,pconfigcall_read.SITE) = eps',
        '$dynamic_owned_global_query_valid(S_read,pconfigcall_read)',
        '$dynamic_global_constant_valid(S_read,pconfigcall_read)',
        'S_read.STORE[n_call] = DEFINED PNULL', 'S_read.STORE[n_result] = DEFINED (PINT 97)',
        '$heap_owners($heap_graph(S_read),HOBJECT n_b) = 1',
        '$weakref_get(S_read,n_weak_b) = POBJECT n_b',
        'S_read.USERCONSTANTS = S_recovery.USERCONSTANTS',
        '$throwable_field(S_read,n_error,"trace") = PARRAY n_trace',
        '$strict_check(S_read,PARRAY n_args_api,PARRAY n_args_invoke,eps) = COMPARED true',
        '$test_outputs(S_read.EVENTS) = ' + term(reading),
        *common.step('S_value','S_read','PINT 23'),
        'S_value.TODO = ptask_read*', 'S_value.USERCONSTANTS = S_recovery.USERCONSTANTS',
        '~(HOBJECT n_b <- S_value.ALLOCATIONS)', '$weakref_get(S_value,n_weak_b) = PNULL',
        '$weakref_get(S_value,n_weak_a) = PNULL',
        '$throwable_field(S_value,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_value.ARRAYS[n_args_api].ITEMS,KINT 0) = (DIRECT pvalue_trace_name)',
        'S_value.SELECTEDCALLS = eps', 'S_value.SELECTSEQ = 0',
        *define.finish('S_value',stdout),
        'S_final.USERCONSTANTS = S_recovery.USERCONSTANTS',
        'S_final.SELECTEDCALLS = eps', 'S_final.SELECTSEQ = 0',
        '~(HOBJECT n_a <- S_final.ALLOCATIONS)', '~(HOBJECT n_b <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_weak_a <- S_final.ALLOCATIONS)', '~(HOBJECT n_weak_b <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_final.ALLOCATIONS)',
        '~(HARRAY n_args_api <- S_final.ALLOCATIONS)', '~(HARRAY n_args_invoke <- S_final.ALLOCATIONS)']
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
