#!/usr/bin/env python3
"""Private duplicate child cleanup precedes the captured DEFINE callee."""
from pathlib import Path

import define_certified_instance_protocol as instance
import define_runtime_closure_protocol as runtime
import define_stdclass_array_duplicate_review_protocol as prior
import define_owned_array_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
TARGET = 'V94_REVIEW_ARRAY'
CASE = sources.CASE
PREFIX = runtime.PREFIX + r'''
dec $test_owned_array_peer_front(pstate, nat, nat) : bool
def $test_owned_array_peer_front(S,0,n_object) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.INDEX = 2
  -- if $named_slot_at(pconfigcall.SENT,0) = NAMED_SENT (KNOWN pvalue_name)
  -- if $string_bytes(pvalue_name) = ($ptascii("V94_REVIEW_ARRAY"))
  -- if $named_slot_at(pconfigcall.SENT,1) = NAMED_SENT (KNOWN (PARRAY n_input))
def $test_owned_array_peer_front(S,1,n_object) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.OWNER =/= eps
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V94_REVIEW_ARRAY"),PARRAY n_input))
def $test_owned_array_peer_front(S,2,n_object) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V94_REVIEW_ARRAY"),PARRAY n_input))
def $test_owned_array_peer_front(S,3,n_object) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OBJECT = n_object /\ ~pdestructorcall.STORE
def $test_owned_array_peer_front(S,4,n_object) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask_tail*
  -- if ~$test_owned_array_peer_front(S,2,n_object)
  -- if S.DESTRUCTION.OPERATIONS = eps
def $test_owned_array_peer_front(S,n_phase,n_object) = false -- otherwise
dec $test_owned_array_peer_seek(pstate, nat, nat, nat) : pstate
def $test_owned_array_peer_seek(S,n_phase,n_object,0) = S
def $test_owned_array_peer_seek(S,n_phase,n_object,n) = S
  -- if $(n > 0)
  -- if $test_owned_array_peer_front(S,n_phase,n_object) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_owned_array_peer_seek(S,n_phase,n_object,n) = $test_owned_array_peer_seek($drive_steps($test_running(S),1),n_phase,n_object,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_owned_array_peer_front(S,n_phase,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase, obj='0'):
    return [f'{state}_found = $test_owned_array_peer_seek({start},{phase},{obj},1500)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_owned_array_peer_front({state},{phase},{obj})', *common.public(state)]


def flags():
    values = []
    for label, value in [('null','PNULL'),('quiet','PINT 0'),('true','PBOOL true')]:
        call = 'pconfigcall_' + label
        values += [f'{call} = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN ({value}))]',
            f'$config_invoke_valid(S,{call})',
            f'~$dynamic_owned_define_header(S,{call})',
            f'~$dynamic_array_call_valid(S,{call})']
    return values


def checks(initial, stdout):
    captured = b'B|N|held|'
    warning = captured + b'H|2|held|'
    released = warning + b'D|41|held|'
    kept = (released + b'E|same|STOP|none|v94ReviewReport|define|__invoke|'
        b'V94_REVIEW_ARRAY|null|false|rawsame|defined|90|97|1|1|gone|')
    assert stdout == kept + b'17|A|'
    leaf = text('leaf')
    values = [*initial, *reach('S_capture','S_initial',0),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        'pconfigcall_capture.OWNER = (n_callee)',
        'pconfigcall_capture.SELECTION = (0)',
        'S_capture.SELECTEDCALLS = [pselectedcall]', 'S_capture.SELECTSEQ = 1',
        'pselectedcall.NONCE = 0', 'pselectedcall.OWNER = (n_callee)',
        'pselectedcall.KIND = INTRINSIC_DEFINE',
        'pselectedcall.SITE = pconfigcall_capture.SITE',
        'pselectedcall.LINE = pconfigcall_capture.LINE',
        'pselectedcall.DEPTH = 0', 'pselectedcall.ORIGINAL = eps',
        'pselectedcall.LOOKUP = $ptascii("define")',
        '$selected_entry_source_valid(S_capture,pselectedcall)',
        '$config_selected_valid(S_capture,pconfigcall_capture)',
        'S_capture.OBJECTS[n_callee] = INTRINSICCLOSURE INTRINSIC_DEFINE',
        '$lookup(S_capture.ENV,$ptascii("call")) = (n_call)',
        '$lookup(S_capture.ENV,$ptascii("weak")) = (n_weak_cv)',
        '$lookup(S_capture.ENV,$ptascii("source")) = (n_source)',
        '$lookup(S_capture.ENV,$ptascii("slot")) = (n_slot)',
        '$lookup(S_capture.ENV,$ptascii("calls")) = (n_calls)',
        '$lookup(S_capture.ENV,$ptascii("destroyed")) = (n_destroyed)',
        '$lookup(S_capture.ENV,$ptascii("result")) = (n_result)',
        '$lookup(S_capture.ENV,$ptascii("chosen")) = (n_chosen)',
        'S_capture.STORE[n_call] = DEFINED (POBJECT n_callee)',
        'S_capture.STORE[n_weak_cv] = DEFINED (POBJECT n_weak)',
        'S_capture.OBJECTS[n_weak] = WEAKREFERENCE (n_callee)',
        '$node_children(S_capture,HOBJECT n_weak) = eps',
        '$node_children(S_capture,HOBJECT n_callee) = eps',
        'S_capture.STORE[n_source] = DEFINED (PARRAY n_input)',
        'S_capture.STORE[n_slot] = DEFINED (POBJECT n_object)',
        'n_slot <- S_capture.REFCELLS',
        '$named_slot_at(pconfigcall_capture.SENT,1) = NAMED_SENT (KNOWN (PARRAY n_input))',
        f'S_capture.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {leaf}) (ALIAS n_slot)]',
        '$array_append_key(S_capture.ARRAYS[n_input]) = KINT 0',
        '$task_nodes(CONFIG_ARGS pconfigcall_capture) = [HARRAY n_input,HOBJECT n_callee]',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_callee) = 2',
        '$heap_owners($heap_graph(S_capture),HARRAY n_input) = 2',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_object) = 1',
        *instance.property_value('S_capture','n_object',7,'captured'),
        *reach('S','S_capture',1),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.OWNER = (n_callee)', 'pconfigcall.SELECTION = (0)',
        'pconfigcall.SITE = pconfigcall_capture.SITE', '~pconfigcall.NAMED',
        '$dynamic_define_values(pconfigcall) = ((' + text(TARGET) + ',PARRAY n_input))',
        '$named_slot_at(pconfigcall.SENT,2) = NAMED_SENT (KNOWN (PBOOL false))',
        '$dynamic_owned_define_header(S,pconfigcall)',
        '~$dynamic_owned_define_valid(S,pconfigcall)',
        '$dynamic_array_call_valid(S,pconfigcall)',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        'S.USERCONSTANTS = [puserconstant_old]',
        'puserconstant_old.NAME = ' + text(TARGET),
        'puserconstant_old.VALUE = PINT 17', 'puserconstant_old.CLASS = PVSCALAR',
        'S.STORE[n_call] = DEFINED pvalue_call',
        '$string_bytes(pvalue_call) = ($ptascii("defined"))',
        'S.STORE[n_source] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        'S.ARRAYS[n_caller].ITEMS = [ENTRY (KINT 90) (DIRECT (PINT 90))]',
        'S.ARRAYS[n_caller].NEXT = 91',
        'S.ARRAYS[n_input] = S_capture.ARRAYS[n_input]',
        'S.STORE[n_slot] = DEFINED (POBJECT n_object)',
        'S.STORE[n_calls] = DEFINED (PINT 0)',
        'S.STORE[n_destroyed] = DEFINED (PINT 0)',
        'S.STORE[n_result] = DEFINED (PINT 97)',
        'S.STORE[n_chosen] = DEFINED PNULL',
        '$weakref_get(S,n_weak) = POBJECT n_callee',
        '$heap_owners($heap_graph(S),HOBJECT n_callee) = 1',
        '$heap_owners($heap_graph(S),HARRAY n_input) = 1',
        '$config_nodes(pconfigcall) = [HARRAY n_input,HOBJECT n_callee]',
        '$dynamic_array_value(S,PARRAY n_input,eps,false) = eps',
        '$dynamic_array_duplicate_call_valid(S,pconfigcall,1)',
        'n_candidate = |S.ARRAYS|',
        '$test_outputs(S.EVENTS) = ' + term(captured),
        # These projections authenticate only the newly admitted owned header.
        '~$dynamic_owned_define_header(S,pconfigcall[.OWNER = eps])',
        '~$dynamic_owned_define_header(S,pconfigcall[.SELECTION = eps])',
        'S_missing = S[.SELECTEDCALLS = eps][.SELECTSEQ = 0]',
        '~$dynamic_array_call_valid(S_missing,pconfigcall)',
        '$heap_graph(S_missing) = $heap_graph(S)',
        'pconfigcall_object = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,1,KNOWN (POBJECT n_object))]',
        '$dynamic_owned_define_header(S,pconfigcall_object)',
        '$dynamic_owned_define_valid(S,pconfigcall_object)',
        '~$dynamic_array_call_valid(S,pconfigcall_object)',
        *flags(),
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        '$test_running(S_pause) = S',
        # A genuine private DIRECT copy precedes the raw input and callee.
        *common.step('S_dispatch','S'), *common.public('S_dispatch'),
        '$drive_steps($test_running(S_pause),1) = S_dispatch_found',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass 1',
        'perrorcall.LEVEL = 2', '$error_call_valid(S_dispatch,perrorcall)',
        'perrorcall.MESSAGE = $global_constant_duplicate_message(' + text(TARGET) + ')',
        f'parray_candidate = $array_insert($array_empty(),KSTRING {leaf},DIRECT (POBJECT n_object))',
        f'pvalueclass = PVARRAY false ([(KSTRING {leaf},PVOBJECT)])',
        'S_dispatch.ARRAYS = S.ARRAYS ++ [parray_candidate]',
        'S_dispatch.OBJECTS = S.OBJECTS',
        'S_dispatch.OBJECTPROPS = S.OBJECTPROPS',
        'S_dispatch.ALLOCATIONS = S.ALLOCATIONS ++ [HARRAY n_candidate]',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.USERCONSTANTS = S.USERCONSTANTS',
        'S_dispatch.EVENTS = S.EVENTS',
        '$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_candidate,pvalueclass,1)',
        '$task_nodes(perrorcall.RESUME) = [HARRAY n_candidate,HARRAY n_input,HOBJECT n_callee]',
        '$heap_owners($heap_graph(S_dispatch),HARRAY n_candidate) = 1',
        '$heap_owners($heap_graph(S_dispatch),HOBJECT n_callee) = 1',
        '$heap_owners($heap_graph(S_dispatch),HOBJECT n_object) = 2',
        '$heap_edge_owners(HOBJECT n_object,$heap_graph(S_dispatch).EDGES,[HARRAY n_candidate]) = 1',
        # The handler clears the sole source alias; only the private copy owns the child.
        *reach('S_throw','S_dispatch',2),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_done) :: ptask_after*',
        'perrorcall_done.RESUME = perrorcall.RESUME',
        'S_throw.STORE[n_slot] = DEFINED PNULL',
        'S_throw.STORE[n_chosen] = DEFINED (POBJECT n_error)',
        'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
        'S_throw.STORE[n_destroyed] = DEFINED (PINT 0)',
        'S_throw.STORE[n_result] = DEFINED (PINT 97)',
        'S_throw.USERCONSTANTS = S.USERCONSTANTS',
        'S_throw.ARRAYS[n_candidate] = parray_candidate',
        'S_throw.ARRAYS[n_input] = S.ARRAYS[n_input]',
        'S_throw.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'pthrowable_error.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_error,"message")) = ($ptascii("STOP"))',
        '$throwable_field(S_throw,n_error,"previous") = PNULL',
        '$throwable_chain_valid(S_throw,n_error)',
        '$throwable_field(S_throw,n_error,"trace") = PARRAY n_trace',
        '|S_throw.ARRAYS[n_trace].ITEMS| = 3',
        '$entry_lookup(S_throw.ARRAYS[n_trace].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_report))',
        '$entry_lookup(S_throw.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_frame_api))',
        '$entry_lookup(S_throw.ARRAYS[n_trace].ITEMS,KINT 2) = (DIRECT (PARRAY n_frame_invoke))',
        '$trace_array_field(S_throw,n_frame_report,$ptascii("function")) = PSTRING ($ptascii("v94ReviewReport"))',
        '$trace_array_field(S_throw,n_frame_api,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_throw,n_frame_invoke,$ptascii("function")) = PSTRING ($ptascii("__invoke"))',
        '$trace_array_field(S_throw,n_frame_api,$ptascii("args")) = PARRAY n_args_api',
        '$trace_array_field(S_throw,n_frame_invoke,$ptascii("args")) = PARRAY n_args_invoke',
        '$entry_lookup(S_throw.ARRAYS[n_args_api].ITEMS,KINT 1) = (DIRECT (PARRAY n_input))',
        '$entry_lookup(S_throw.ARRAYS[n_args_api].ITEMS,KINT 2) = (DIRECT (PBOOL false))',
        '$strict_check(S_throw,PARRAY n_args_api,PARRAY n_args_invoke,eps) = COMPARED true',
        '$heap_owners($heap_graph(S_throw),HOBJECT n_object) = 1',
        '$heap_owners($heap_graph(S_throw),HOBJECT n_callee) = 1',
        '$heap_owners($heap_graph(S_throw),HARRAY n_candidate) = 1',
        '$heap_owners($heap_graph(S_throw),HARRAY n_input) = 3',
        '$heap_edge_owners(HOBJECT n_object,$heap_graph(S_throw).EDGES,[HARRAY n_candidate]) = 1',
        '$heap_edge_owners(HOBJECT n_object,$heap_graph(S_throw).EDGES,[HCELL n_slot,HARRAY n_input]) = 0',
        *instance.property_value('S_throw','n_object',41,'throwing'),
        '~(n_object <- S_throw.DESTRUCTION.CALLED)',
        '$test_outputs(S_throw.EVENTS) = ' + term(warning),
        'S_throw_pause = $drive_steps(S_throw,0)',
        'S_throw_pause = S_throw[.COMPLETION = BUDGET]',
        '$test_running(S_throw_pause) = S_throw',
        # Marker removal uses the real pending Throwable and the original task tail.
        *common.step('S_drop','S_throw'), *common.public('S_drop'),
        '$drive_steps($test_running(S_throw_pause),1) = S_drop_found',
        'S_drop.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_drop) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_after*',
        'pdestructionoperation.SOURCE = THROW_SEARCH n_error',
        'pdestructionoperation.VALUE = KNOWN PNULL',
        'pdestructionoperation.PENDING = (n_error)',
        '$destruction_job_nodes(pdestructionrelease_drop.JOBS) = [HARRAY n_candidate,HARRAY n_input,HOBJECT n_callee]',
        *reach('S_free','S_drop',3,'n_object'),
        'S_free.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease_pending) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_after*',
        'pdestructorcall.OBJECT = n_object', '~pdestructorcall.STORE',
        'pdestructorcall.FRAME = eps',
        'pdestructorcall.OPERATION = (pdestructionoperation)',
        'pdestructorcall.PENDING = (n_error)',
        '$destructor_enter_valid(S_free,pdestructorcall)',
        '$destruction_job_nodes(pdestructionrelease_pending.JOBS) = [HARRAY n_input,HOBJECT n_callee]',
        '~(HARRAY n_candidate <- S_free.ALLOCATIONS)',
        'HOBJECT n_callee <- S_free.ALLOCATIONS',
        '$heap_owners($heap_graph(S_free),HOBJECT n_callee) = 1',
        '$weakref_get(S_free,n_weak) = POBJECT n_callee',
        '$heap_owners($heap_graph(S_free),HOBJECT n_object) = 2',
        'n_object <- S_free.DESTRUCTION.CALLED',
        'S_free.STORE[n_destroyed] = DEFINED (PINT 0)',
        'S_free.USERCONSTANTS = S.USERCONSTANTS',
        '$test_outputs(S_free.EVENTS) = ' + term(warning),
        *reach('S_after','S_free',4,'n_object'),
        'S_after.TODO = (THROW_SEARCH n_error) :: ptask_after*',
        'S_after.USERCONSTANTS = S.USERCONSTANTS',
        'S_after.ERRORHANDLER.CALLBACK = (perrorcall_done.CALLBACK)',
        'S_after.STORE[n_result] = DEFINED (PINT 97)',
        'S_after.STORE[n_destroyed] = DEFINED (PINT 1)',
        'S_after.STORE[n_calls] = DEFINED (PINT 1)',
        'S_after.OBJECTS[n_error] = THROWABLE pthrowable_error',
        '$weakref_get(S_after,n_weak) = PNULL',
        '~(HOBJECT n_callee <- S_after.ALLOCATIONS)',
        '~(HOBJECT n_object <- S_after.ALLOCATIONS)',
        '~(HARRAY n_candidate <- S_after.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_after),HARRAY n_input) = 2',
        '$heap_edge_owners(HARRAY n_input,$heap_graph(S_after).EDGES,[HARRAY n_args_api,HARRAY n_args_invoke]) = 2',
        '$selected_entry_source_valid(S_after,pselectedcall)',
        '$test_outputs(S_after.EVENTS) = ' + term(released),
        *runtime.unset('S_kept','S_after','rawInvoke'),
        '$test_outputs(S_kept.EVENTS) = ' + term(kept),
        'S_kept.STORE[n_result] = DEFINED (PINT 97)',
        '$weakref_get(S_kept,n_weak) = PNULL',
        '$strict_check(S_kept,PARRAY n_args_api,PARRAY n_args_invoke,eps) = COMPARED true',
        *common.reach('S_query','S_kept',0,TARGET), *common.public('S_query'),
        '~(HOBJECT n_error <- S_query.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_query.ALLOCATIONS)',
        '~(HARRAY n_input <- S_query.ALLOCATIONS)',
        'S_query.USERCONSTANTS = S.USERCONSTANTS',
        '$selected_entry_source_valid(S_query,pselectedcall)',
        '$selected_log_valid(S_query,S_query.SELECTEDCALLS,0)',
        '$test_outputs(S_query.EVENTS) = ' + term(kept),
        *define.finish('S_query',stdout),
        'S_final.USERCONSTANTS = S.USERCONSTANTS',
        'S_final.SELECTEDCALLS = [pselectedcall]',
        '~(HOBJECT n_callee <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_object <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_weak <- S_final.ALLOCATIONS)',
        '~(HARRAY n_candidate <- S_final.ALLOCATIONS)',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)',
        '~(HARRAY n_caller <- S_final.ALLOCATIONS)',
        '~(HCELL n_slot <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_final.ALLOCATIONS)']
    return values


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = runtime.packet_process


def process(command, directory, timeout, cwd):
    if directory.parent.name == CASE:
        timeout = 360
    return packet_process(command, directory, timeout, cwd)


packet.process = process
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    raise SystemExit(0 if packet.main() else 1)
