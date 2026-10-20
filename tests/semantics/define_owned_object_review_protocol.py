#!/usr/bin/env python3
"""Direct raw object arguments survive callee cleanup and retire after trace views."""
from pathlib import Path

import define_certified_instance_protocol as instance
import define_runtime_closure_protocol as runtime
import define_stdclass_array_duplicate_review_protocol as prior
import typed_static_invoke_set_protocol as process_base
import define_owned_object_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
TARGET = 'V95_REVIEW_DIRECT'
CASE = sources.CASE
PREFIX = runtime.PREFIX + r'''
dec $test_owned_object_peer_front(pstate, nat, nat) : bool
def $test_owned_object_peer_front(S,0,n_object) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.INDEX = 2
  -- if $named_slot_at(pconfigcall.SENT,0) = NAMED_SENT (KNOWN pvalue_name)
  -- if $string_bytes(pvalue_name) = ($ptascii("V95_REVIEW_DIRECT"))
  -- if $named_slot_at(pconfigcall.SENT,1) = NAMED_SENT (KNOWN (POBJECT n_payload))
def $test_owned_object_peer_front(S,1,n_object) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.OWNER =/= eps
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V95_REVIEW_DIRECT"),POBJECT n_payload))
def $test_owned_object_peer_front(S,2,n_object) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall n_constants
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V95_REVIEW_DIRECT"),POBJECT n_payload))
def $test_owned_object_peer_front(S,3,n_object) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask_tail*
  -- if ~$test_owned_object_peer_front(S,2,n_object)
  -- if S.DESTRUCTION.OPERATIONS = eps
def $test_owned_object_peer_front(S,4,n_object) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OBJECT = n_object /\ ~pdestructorcall.STORE
def $test_owned_object_peer_front(S,n_phase,n_object) = false -- otherwise
dec $test_owned_object_peer_seek(pstate, nat, nat, nat) : pstate
def $test_owned_object_peer_seek(S,n_phase,n_object,0) = S
def $test_owned_object_peer_seek(S,n_phase,n_object,n) = S
  -- if $(n > 0)
  -- if $test_owned_object_peer_front(S,n_phase,n_object) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_owned_object_peer_seek(S,n_phase,n_object,n) = $test_owned_object_peer_seek($drive_steps($test_running(S),1),n_phase,n_object,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_owned_object_peer_front(S,n_phase,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase, obj='0'):
    return [f'{state}_found = $test_owned_object_peer_seek({start},{phase},{obj},1500)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_owned_object_peer_front({state},{phase},{obj})', *common.public(state)]


def checks(initial, stdout):
    captured = b'B|N|held|'
    warning = captured + b'H|2|held|'
    kept = (warning + b'E|same|STOP|none|v95ReviewReport|define|__invoke|'
        b'V95_REVIEW_DIRECT|false|rawsame|41|1|0|gone|defined|null|97|'
        b'shared|53|kept|0|gone|')
    released = kept + b'D|53|gone|released|1|gone|'
    assert stdout == released + b'17|A|'
    values = [*initial, *reach('S_capture','S_initial',0),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        'pconfigcall_capture.OWNER = (n_callee)', 'pconfigcall_capture.SELECTION = (0)',
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
        '$lookup(S_capture.ENV,$ptascii("payload")) = (n_payload_cv)',
        '$lookup(S_capture.ENV,$ptascii("cell")) = (n_cell)',
        '$lookup(S_capture.ENV,$ptascii("calls")) = (n_calls)',
        '$lookup(S_capture.ENV,$ptascii("destroyed")) = (n_destroyed)',
        '$lookup(S_capture.ENV,$ptascii("result")) = (n_result)',
        '$lookup(S_capture.ENV,$ptascii("chosen")) = (n_chosen)',
        '$named_slot_at(pconfigcall_capture.SENT,1) = NAMED_SENT (KNOWN (POBJECT n_object))',
        'S_capture.STORE[n_payload_cv] = DEFINED (POBJECT n_object)',
        'S_capture.STORE[n_cell] = DEFINED (POBJECT n_object)',
        'S_capture.STORE[n_call] = DEFINED (POBJECT n_callee)',
        'S_capture.STORE[n_weak_cv] = DEFINED (POBJECT n_weak)',
        'S_capture.OBJECTS[n_weak] = WEAKREFERENCE (n_callee)',
        '$node_children(S_capture,HOBJECT n_weak) = eps',
        '$node_children(S_capture,HOBJECT n_callee) = eps',
        'S_capture.OBJECTS[n_object] = INSTANCE porigin_class',
        '$global_new_record(S_capture.CONSTANTOBJECTS,n_object) = eps',
        '$dynamic_define_value_class(S_capture,POBJECT n_object) = (PVOBJECT)',
        '$task_nodes(CONFIG_ARGS pconfigcall_capture) = [HOBJECT n_object,HOBJECT n_callee]',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_object) = 3',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_callee) = 2',
        *instance.property_value('S_capture','n_object',7,'capture'),
        '$test_outputs(S_capture.EVENTS) = ' + term(b'B|'),
        *reach('S','S_capture',1),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        'pconfigcall.OWNER = (n_callee)', 'pconfigcall.SELECTION = (0)',
        '~pconfigcall.NAMED', '|pconfigcall.SENT| = 3',
        '$dynamic_define_values(pconfigcall) = ((' + text(TARGET) + ',POBJECT n_object))',
        '$named_slot_at(pconfigcall.SENT,2) = NAMED_SENT (KNOWN (PBOOL false))',
        '$dynamic_owned_define_header(S,pconfigcall)', '$dynamic_owned_define_valid(S,pconfigcall)',
        '~$dynamic_array_call_valid(S,pconfigcall)',
        '$dynamic_define_value_class(S,POBJECT n_object) = (PVOBJECT)',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        'S.USERCONSTANTS = [puserconstant_old]',
        'puserconstant_old.NAME = ' + text(TARGET),
        'puserconstant_old.VALUE = PINT 17', 'puserconstant_old.CLASS = PVSCALAR',
        'S.STORE[n_payload_cv] = DEFINED PNULL',
        'S.STORE[n_cell] = DEFINED (POBJECT n_object)',
        'S.STORE[n_call] = DEFINED pvalue_call',
        '$string_bytes(pvalue_call) = ($ptascii("defined"))',
        '$config_nodes(pconfigcall) = [HOBJECT n_object,HOBJECT n_callee]',
        '$heap_owners($heap_graph(S),HOBJECT n_object) = 2',
        '$heap_owners($heap_graph(S),HOBJECT n_callee) = 1',
        *instance.property_value('S','n_object',31,'invoke'),
        '$dynamic_constant_duplicate_valid(S,pconfigcall,1)',
        '$test_outputs(S.EVENTS) = ' + term(captured),
        # These malformed projections test authority; none is driven.
        '~$dynamic_owned_define_valid(S,pconfigcall[.OWNER = eps])',
        '~$dynamic_owned_define_valid(S,pconfigcall[.SELECTION = eps])',
        'S_missing = S[.SELECTEDCALLS = eps][.SELECTSEQ = 0]',
        '$heap_graph(S_missing) = $heap_graph(S)',
        '~$dynamic_owned_define_valid(S_missing,pconfigcall)',
        '~$dynamic_define_source(S_missing,pconfigcall.SITE)',
        'S_dead_payload = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_object)]',
        '$dynamic_define_value_class(S_dead_payload,POBJECT n_object) = eps',
        '~$dynamic_owned_define_valid(S_dead_payload,pconfigcall)',
        'S_dead_callee = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_callee)]',
        '$selected_entry_source_valid(S_dead_callee,pselectedcall)',
        '~$dynamic_owned_define_valid(S_dead_callee,pconfigcall)',
        'pconfigcall_callee_value = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,1,KNOWN (POBJECT n_callee))]',
        '$dynamic_owned_define_header(S,pconfigcall_callee_value)',
        '$dynamic_define_value_class(S,POBJECT n_callee) = eps',
        '~$dynamic_owned_define_valid(S,pconfigcall_callee_value)']
    for label, value in [('null','PNULL'),('quiet','PINT 0'),('true','PBOOL true')]:
        call = 'pconfigcall_' + label
        negated = '' if label == 'true' else '~'
        values += [f'{call} = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN ({value}))]',
            f'$config_invoke_valid(S,{call})',
            f'{negated}$dynamic_owned_define_header(S,{call})',
            f'{negated}$dynamic_owned_define_valid(S,{call})']
    values += [
        *common.step('S_dispatch','S'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_dispatch*',
        'perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall 1',
        '$error_call_valid(S_dispatch,perrorcall)',
        '$task_nodes(perrorcall.RESUME) = [HOBJECT n_object,HOBJECT n_callee]',
        'S_dispatch.ARRAYS = S.ARRAYS', 'S_dispatch.USERCONSTANTS = S.USERCONSTANTS',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.EVENTS = S.EVENTS',
        *reach('S_throw','S_dispatch',2),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_done) :: ptask_after*',
        'perrorcall_done.RESUME = perrorcall.RESUME',
        'S_throw.STORE[n_cell] = DEFINED PNULL',
        'S_throw.STORE[n_chosen] = DEFINED (POBJECT n_error)',
        'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
        'S_throw.STORE[n_destroyed] = DEFINED (PINT 0)',
        'S_throw.STORE[n_result] = DEFINED (PINT 97)',
        'S_throw.USERCONSTANTS = S.USERCONSTANTS',
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
        '$trace_array_field(S_throw,n_frame_report,$ptascii("function")) = PSTRING ($ptascii("v95ReviewReport"))',
        '$trace_array_field(S_throw,n_frame_api,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_throw,n_frame_invoke,$ptascii("function")) = PSTRING ($ptascii("__invoke"))',
        '$trace_array_field(S_throw,n_frame_api,$ptascii("args")) = PARRAY n_args_api',
        '$trace_array_field(S_throw,n_frame_invoke,$ptascii("args")) = PARRAY n_args_invoke',
        '$entry_lookup(S_throw.ARRAYS[n_args_api].ITEMS,KINT 1) = (DIRECT (POBJECT n_object))',
        '$entry_lookup(S_throw.ARRAYS[n_args_api].ITEMS,KINT 2) = (DIRECT (PBOOL false))',
        '$strict_check(S_throw,PARRAY n_args_api,PARRAY n_args_invoke,eps) = COMPARED true',
        '$heap_edge_owners(HOBJECT n_object,$heap_graph(S_throw).EDGES,[HARRAY n_args_api,HARRAY n_args_invoke]) = 2',
        '$heap_owners($heap_graph(S_throw),HOBJECT n_object) = 3',
        '$heap_owners($heap_graph(S_throw),HOBJECT n_callee) = 1',
        *instance.property_value('S_throw','n_object',41,'throwing'),
        '~(n_object <- S_throw.DESTRUCTION.CALLED)',
        '$test_outputs(S_throw.EVENTS) = ' + term(warning),
        'S_throw_pause = $drive_steps(S_throw,0)',
        'S_throw_pause = S_throw[.COMPLETION = BUDGET]',
        '$test_running(S_throw_pause) = S_throw',
        *common.step('S_drop','S_throw'), *common.public('S_drop'),
        '$drive_steps($test_running(S_throw_pause),1) = S_drop_found',
        'S_drop.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_drop) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_after*',
        'pdestructionoperation.SOURCE = THROW_SEARCH n_error',
        'pdestructionoperation.VALUE = KNOWN PNULL',
        'pdestructionoperation.PENDING = (n_error)',
        '$destruction_job_nodes(pdestructionrelease_drop.JOBS) = [HOBJECT n_object,HOBJECT n_callee]',
        # Raw arg-frame edges keep the payload live while the callee is released.
        *reach('S_after','S_drop',3),
        'S_after.TODO = (THROW_SEARCH n_error) :: ptask_after*',
        'S_after.USERCONSTANTS = S.USERCONSTANTS',
        'S_after.STORE[n_destroyed] = DEFINED (PINT 0)',
        'S_after.STORE[n_calls] = DEFINED (PINT 1)',
        'S_after.STORE[n_result] = DEFINED (PINT 97)',
        'S_after.OBJECTS[n_error] = THROWABLE pthrowable_error',
        '$weakref_get(S_after,n_weak) = PNULL',
        '~(HOBJECT n_callee <- S_after.ALLOCATIONS)',
        'HOBJECT n_object <- S_after.ALLOCATIONS',
        '~(n_object <- S_after.DESTRUCTION.CALLED)',
        '$heap_owners($heap_graph(S_after),HOBJECT n_object) = 2',
        '$heap_edge_owners(HOBJECT n_object,$heap_graph(S_after).EDGES,[HARRAY n_args_api,HARRAY n_args_invoke]) = 2',
        '$selected_entry_source_valid(S_after,pselectedcall)',
        '$test_outputs(S_after.EVENTS) = ' + term(warning),
        *runtime.unset('S_kept','S_after','rawInvoke'),
        '$test_outputs(S_kept.EVENTS) = ' + term(kept),
        'S_kept.STORE[n_destroyed] = DEFINED (PINT 0)',
        'S_kept.STORE[n_result] = DEFINED (PINT 97)',
        '$weakref_get(S_kept,n_weak) = PNULL',
        '~(HOBJECT n_error <- S_kept.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_kept.ALLOCATIONS)',
        'HARRAY n_args_api <- S_kept.ALLOCATIONS',
        'HARRAY n_args_invoke <- S_kept.ALLOCATIONS',
        '$strict_check(S_kept,PARRAY n_args_api,PARRAY n_args_invoke,eps) = COMPARED true',
        '$lookup(S_kept.ENV,$ptascii("raw")) = (n_raw_cv)',
        'S_kept.STORE[n_raw_cv] = DEFINED (POBJECT n_object)',
        '$heap_owners($heap_graph(S_kept),HOBJECT n_object) = 3',
        *instance.property_value('S_kept','n_object',53,'kept'),
        # Seek actual release after the explicit raw-view unsets; no isolated unset claim.
        *reach('S_free','S_kept',4,'n_object'),
        'S_free.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_free*',
        'pdestructorcall.OBJECT = n_object', '~pdestructorcall.STORE',
        'pdestructorcall.FRAME = eps', 'pdestructorcall.PENDING = eps',
        'pdestructorcall.OPERATION = (pdestructionoperation_free)',
        'pdestructionoperation_free.PENDING = eps',
        '$destructor_enter_valid(S_free,pdestructorcall)',
        '$heap_owners($heap_graph(S_free),HOBJECT n_object) = 2',
        '~(HOBJECT n_callee <- S_free.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_free.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_free.ALLOCATIONS)',
        '~(HARRAY n_args_api <- S_free.ALLOCATIONS)',
        '~(HARRAY n_args_invoke <- S_free.ALLOCATIONS)',
        '$weakref_get(S_free,n_weak) = PNULL',
        *instance.property_value('S_free','n_object',53,'free'),
        'S_free.STORE[n_destroyed] = DEFINED (PINT 0)',
        'n_object <- S_free.DESTRUCTION.CALLED',
        '$test_outputs(S_free.EVENTS) = ' + term(kept),
        'S_free_pause = $drive_steps(S_free,0)',
        'S_free_pause = S_free[.COMPLETION = BUDGET]',
        '$test_running(S_free_pause) = S_free',
        'S_start_found = $drive_steps($test_running(S_free_pause),1)',
        '$drive_steps(S_free,1) = S_start_found',
        r'S_start_found.COMPLETION = NORMAL \/ S_start_found.COMPLETION = BUDGET',
        'S_start = $test_running(S_start_found)', *common.public('S_start'),
        *common.reach('S_query','S_start',0,TARGET), *common.public('S_query'),
        '$test_outputs(S_query.EVENTS) = ' + term(released),
        'S_query.STORE[n_destroyed] = DEFINED (PINT 1)',
        'S_query.USERCONSTANTS = S.USERCONSTANTS',
        '~(HOBJECT n_object <- S_query.ALLOCATIONS)',
        '~(HOBJECT n_callee <- S_query.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_query.ALLOCATIONS)',
        '$selected_entry_source_valid(S_query,pselectedcall)',
        '$selected_log_valid(S_query,S_query.SELECTEDCALLS,0)',
        *define.finish('S_query',stdout),
        'S_final.USERCONSTANTS = S.USERCONSTANTS',
        'S_final.SELECTEDCALLS = [pselectedcall]',
        '~(HOBJECT n_object <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_callee <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_weak <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_final.ALLOCATIONS)',
        '~(HARRAY n_args_api <- S_final.ALLOCATIONS)',
        '~(HARRAY n_args_invoke <- S_final.ALLOCATIONS)']
    return values


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = process_base.process


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
