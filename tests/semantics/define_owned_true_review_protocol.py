#!/usr/bin/env python3
"""Pending ignored-flag registration transfers a direct argument into its row."""
from pathlib import Path

import define_certified_instance_protocol as instance
import define_runtime_closure_protocol as runtime
import define_stdclass_array_duplicate_review_protocol as prior
import typed_static_invoke_set_protocol as process_base
import define_owned_true_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
TARGET = 'V96_REVIEW_TRUE'
CASE = sources.CASE
PREFIX = instance.PREFIX + runtime.PREFIX[len(define.PREFIX):] + r'''
dec $test_owned_true_peer_front(pstate, nat) : bool
def $test_owned_true_peer_front(S,0) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.INDEX = 2
  -- if $named_slot_at(pconfigcall.SENT,0) = NAMED_SENT (KNOWN pvalue_name)
  -- if $string_bytes(pvalue_name) = ($ptascii("V96_REVIEW_TRUE"))
def $test_owned_true_peer_front(S,1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.OWNER =/= eps
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V96_REVIEW_TRUE"),POBJECT n_payload))
def $test_owned_true_peer_front(S,2) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V96_REVIEW_TRUE"),POBJECT n_payload))
def $test_owned_true_peer_front(S,3) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask_tail*
  -- if ~$test_owned_true_peer_front(S,2)
  -- if S.DESTRUCTION.OPERATIONS = eps
def $test_owned_true_peer_front(S,n_phase) = false -- otherwise
dec $test_owned_true_peer_seek(pstate, nat, nat) : pstate
def $test_owned_true_peer_seek(S,n_phase,0) = S
def $test_owned_true_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_owned_true_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_owned_true_peer_seek(S,n_phase,n) = $test_owned_true_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_owned_true_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_owned_true_peer_seek({start},{phase},1500)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_owned_true_peer_front({state},{phase})', *common.public(state)]


def checks(initial, stdout):
    captured = b'B|N|held|'
    warning = captured + b'H|2|absent|held|'
    kept = (warning + b'E|same|STOP|none|v96ReviewReport|define|__invoke|'
        b'V96_REVIEW_TRUE|true|rawsame|41|1|97|gone|defined|null|defined|same|53|')
    queried = kept + b'kept|alive|gone|'
    before_shutdown = queried + b'Q|53|same|1|97|A|'
    assert stdout == before_shutdown + b'D|53|'
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
        '$lookup(S_capture.ENV,$ptascii("pointerWeak")) = (n_pointer_cv)',
        '$lookup(S_capture.ENV,$ptascii("payload")) = (n_payload_cv)',
        '$lookup(S_capture.ENV,$ptascii("cell")) = (n_cell)',
        '$lookup(S_capture.ENV,$ptascii("calls")) = (n_calls)',
        '$lookup(S_capture.ENV,$ptascii("result")) = (n_result)',
        '$lookup(S_capture.ENV,$ptascii("chosen")) = (n_chosen)',
        '$named_slot_at(pconfigcall_capture.SENT,1) = NAMED_SENT (KNOWN (POBJECT n_object))',
        'S_capture.STORE[n_payload_cv] = DEFINED (POBJECT n_object)',
        'S_capture.STORE[n_cell] = DEFINED (POBJECT n_object)',
        'S_capture.STORE[n_call] = DEFINED (POBJECT n_callee)',
        'S_capture.STORE[n_weak_cv] = DEFINED (POBJECT n_weak)',
        'S_capture.STORE[n_pointer_cv] = DEFINED (POBJECT n_pointer_weak)',
        'S_capture.OBJECTS[n_weak] = WEAKREFERENCE (n_callee)',
        'S_capture.OBJECTS[n_pointer_weak] = WEAKREFERENCE (n_object)',
        '$node_children(S_capture,HOBJECT n_weak) = eps',
        '$node_children(S_capture,HOBJECT n_pointer_weak) = eps',
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
        '$named_slot_at(pconfigcall.SENT,2) = NAMED_SENT (KNOWN (PBOOL true))',
        '$config_invoke_valid(S,pconfigcall)',
        '$dynamic_owned_define_header(S,pconfigcall)', '$dynamic_owned_define_valid(S,pconfigcall)',
        '$dynamic_constant_case_valid(S,pconfigcall)',
        '~$dynamic_array_call_valid(S,pconfigcall)',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        'S.USERCONSTANTS = eps', '$source_constant_lookup(S,' + text(TARGET) + ') = eps',
        'S.STORE[n_payload_cv] = DEFINED PNULL',
        'S.STORE[n_cell] = DEFINED (POBJECT n_object)',
        'S.STORE[n_call] = DEFINED pvalue_call',
        '$string_bytes(pvalue_call) = ($ptascii("defined"))',
        '$config_nodes(pconfigcall) = [HOBJECT n_object,HOBJECT n_callee]',
        '$heap_owners($heap_graph(S),HOBJECT n_object) = 2',
        '$heap_owners($heap_graph(S),HOBJECT n_callee) = 1',
        *instance.property_value('S','n_object',31,'invoke'),
        '$test_outputs(S.EVENTS) = ' + term(captured),
        # Malformed source/owner projections are never driven.
        '~$dynamic_constant_case_valid(S,pconfigcall[.OWNER = eps])',
        '~$dynamic_constant_case_valid(S,pconfigcall[.SELECTION = eps])',
        'S_missing = S[.SELECTEDCALLS = eps][.SELECTSEQ = 0]',
        '~$dynamic_constant_case_valid(S_missing,pconfigcall)',
        '~$dynamic_define_source(S_missing,pconfigcall.SITE)',
        'S_dead_payload = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_object)]',
        '~$dynamic_constant_case_valid(S_dead_payload,pconfigcall)',
        'S_dead_callee = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_callee)]',
        '$selected_entry_source_valid(S_dead_callee,pselectedcall)',
        '~$dynamic_constant_case_valid(S_dead_callee,pconfigcall)']
    for label, value in [('null','PNULL'),('quiet','PINT 0')]:
        call = 'pconfigcall_' + label
        values += [f'{call} = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN ({value}))]',
            f'$config_invoke_valid(S,{call})',
            f'~$dynamic_owned_define_header(S,{call})',
            f'~$dynamic_constant_case_valid(S,{call})']
    values += [
        'pconfigcall_false = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN (PBOOL false))]',
        '$dynamic_owned_define_valid(S,pconfigcall_false)',
        '~$dynamic_constant_case_valid(S,pconfigcall_false)',
        *common.step('S_dispatch','S'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_dispatch*',
        'perrorcall.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall',
        'perrorcall.LEVEL = 2', 'perrorcall.MESSAGE = $dynamic_constant_case_message()',
        '$error_call_valid(S_dispatch,perrorcall)',
        '$task_nodes(perrorcall.RESUME) = [HOBJECT n_object,HOBJECT n_callee]',
        'S_dispatch.USERCONSTANTS = eps', 'S_dispatch.STORE = S.STORE',
        'S_dispatch.EVENTS = S.EVENTS',
        *reach('S_throw','S_dispatch',2),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_done) :: ptask_after*',
        'perrorcall_done.RESUME = perrorcall.RESUME',
        'S_throw.STORE[n_cell] = DEFINED PNULL',
        'S_throw.STORE[n_chosen] = DEFINED (POBJECT n_error)',
        'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
        'S_throw.STORE[n_result] = DEFINED (PINT 97)',
        'S_throw.USERCONSTANTS = eps',
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
        '$trace_array_field(S_throw,n_frame_report,$ptascii("function")) = PSTRING ($ptascii("v96ReviewReport"))',
        '$trace_array_field(S_throw,n_frame_api,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_throw,n_frame_invoke,$ptascii("function")) = PSTRING ($ptascii("__invoke"))',
        '$trace_array_field(S_throw,n_frame_api,$ptascii("args")) = PARRAY n_args_api',
        '$trace_array_field(S_throw,n_frame_invoke,$ptascii("args")) = PARRAY n_args_invoke',
        '$entry_lookup(S_throw.ARRAYS[n_args_api].ITEMS,KINT 1) = (DIRECT (POBJECT n_object))',
        '$entry_lookup(S_throw.ARRAYS[n_args_api].ITEMS,KINT 2) = (DIRECT (PBOOL true))',
        '$strict_check(S_throw,PARRAY n_args_api,PARRAY n_args_invoke,eps) = COMPARED true',
        '$heap_edge_owners(HOBJECT n_object,$heap_graph(S_throw).EDGES,[HARRAY n_args_api,HARRAY n_args_invoke]) = 2',
        '$heap_owners($heap_graph(S_throw),HOBJECT n_object) = 3',
        '$heap_owners($heap_graph(S_throw),HOBJECT n_callee) = 1',
        *instance.property_value('S_throw','n_object',41,'throwing'),
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
        # The same pointer gains a row root as its argument root is removed.
        'pdestructionrelease_drop.JOBS = [DESTRUCTION_VALUE (HOBJECT n_callee)]',
        'S_drop.USERCONSTANTS = [puserconstant]',
        'puserconstant.NAME = ' + text(TARGET),
        'puserconstant.ORIGIN = pconfigcall.SITE',
        'puserconstant.VALUE = POBJECT n_object', 'puserconstant.CLASS = PVOBJECT',
        'puserconstant.READS = eps', 'puserconstant.RECEIVES = eps',
        '$user_constants_valid(S_drop,S_drop.USERCONSTANTS)',
        '$heap_owners($heap_graph(S_drop),HOBJECT n_object) = 3',
        '$test_outputs(S_drop.EVENTS) = ' + term(warning),
        *reach('S_after','S_drop',3),
        'S_after.TODO = (THROW_SEARCH n_error) :: ptask_after*',
        'S_after.USERCONSTANTS = [puserconstant]',
        'S_after.STORE[n_calls] = DEFINED (PINT 1)',
        'S_after.STORE[n_result] = DEFINED (PINT 97)',
        'S_after.OBJECTS[n_error] = THROWABLE pthrowable_error',
        '$weakref_get(S_after,n_weak) = PNULL',
        '~(HOBJECT n_callee <- S_after.ALLOCATIONS)',
        'HOBJECT n_object <- S_after.ALLOCATIONS',
        '~(n_object <- S_after.DESTRUCTION.CALLED)',
        '$heap_owners($heap_graph(S_after),HOBJECT n_object) = 3',
        '$heap_edge_owners(HOBJECT n_object,$heap_graph(S_after).EDGES,[HARRAY n_args_api,HARRAY n_args_invoke]) = 2',
        '$selected_entry_source_valid(S_after,pselectedcall)',
        '$dynamic_define_source(S_after,pconfigcall.SITE)',
        '$test_outputs(S_after.EVENTS) = ' + term(warning),
        *common.reach('S_first_query','S_after',0,TARGET), *common.public('S_first_query'),
        '$dynamic_global_constant_value(S_first_query,' + text(TARGET) + ') = (POBJECT n_object)',
        *common.step('S_first_value','S_first_query','POBJECT n_object'),
        *runtime.unset('S_kept','S_first_value','published'),
        '$test_outputs(S_kept.EVENTS) = ' + term(kept),
        'S_kept.USERCONSTANTS = [puserconstant]',
        *instance.property_value('S_kept','n_object',53,'kept'),
        *common.reach('S_query','S_kept',0,TARGET), *common.public('S_query'),
        '$test_outputs(S_query.EVENTS) = ' + term(queried),
        'S_query.USERCONSTANTS = [puserconstant]',
        '$heap_owners($heap_graph(S_query),HOBJECT n_object) = 1',
        '$weakref_get(S_query,n_pointer_weak) = POBJECT n_object',
        '$weakref_get(S_query,n_weak) = PNULL',
        '~(HOBJECT n_callee <- S_query.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_query.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_query.ALLOCATIONS)',
        '~(HARRAY n_args_api <- S_query.ALLOCATIONS)',
        '~(HARRAY n_args_invoke <- S_query.ALLOCATIONS)',
        '~(n_object <- S_query.DESTRUCTION.CALLED)',
        '$dynamic_global_constant_value(S_query,' + text(TARGET) + ') = (POBJECT n_object)',
        'S_query.STORE[n_result] = DEFINED (PINT 97)',
        'S_query.STORE[n_calls] = DEFINED (PINT 1)',
        *instance.store('S_store','S_query','n_object',1,before_shutdown),
        *define.finish('S_store_selected',stdout),
        'S_final.USERCONSTANTS = [puserconstant]',
        'S_final.SELECTEDCALLS = [pselectedcall]',
        '$selected_entry_source_valid(S_final,pselectedcall)',
        '$heap_owners($heap_graph(S_final),HOBJECT n_object) = 1',
        'n_object <- S_final.DESTRUCTION.CALLED',
        '~(HOBJECT n_callee <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_weak <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_pointer_weak <- S_final.ALLOCATIONS)',
        *instance.property_value('S_final','n_object',53,'final')]
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
