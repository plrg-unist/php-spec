#!/usr/bin/env python3
"""Reached bare METHOD Closure snapshot and sole receiver retirement."""
from pathlib import Path

import define_certified_instance_protocol as instance
import define_stdclass_array_duplicate_review_protocol as prior
import define_runtime_closure_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
TARGET = 'V85_REVIEW_OLD'
CASE = 'method-closure-private-array-owner-retires-before-catch'
PREFIX = define.PREFIX + r'''
dec $test_runtime_closure_peer_front(pstate, nat, nat) : bool
def $test_runtime_closure_peer_front(S,0,n_closure) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.INDEX = 2
  -- if $named_slot_at(pconfigcall.SENT,0) = NAMED_HOLE
  -- if $named_slot_at(pconfigcall.SENT,1) = NAMED_SENT (KNOWN (PARRAY n_input))
  -- if $named_slot_at(pconfigcall.SENT,2) = NAMED_SENT (KNOWN (PBOOL false))
def $test_runtime_closure_peer_front(S,1,n_closure) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V85_REVIEW_OLD"),PARRAY n_input))
def $test_runtime_closure_peer_front(S,2,n_closure) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V85_REVIEW_OLD"),PARRAY n_input))
def $test_runtime_closure_peer_front(S,3,n_closure) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OBJECT = n_closure /\ ~pdestructorcall.STORE
def $test_runtime_closure_peer_front(S,4,n_closure) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask_tail*
  -- if ~$test_runtime_closure_peer_front(S,2,n_closure)
  -- if S.DESTRUCTION.OPERATIONS = eps
def $test_runtime_closure_peer_front(S,n_phase,n_closure) = false -- otherwise
dec $test_runtime_closure_peer_seek(pstate, nat, nat, nat) : pstate
def $test_runtime_closure_peer_seek(S,n_phase,n_closure,0) = S
def $test_runtime_closure_peer_seek(S,n_phase,n_closure,n) = S
  -- if $(n > 0)
  -- if $test_runtime_closure_peer_front(S,n_phase,n_closure) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_runtime_closure_peer_seek(S,n_phase,n_closure,n) = $test_runtime_closure_peer_seek($drive_steps($test_running(S),1),n_phase,n_closure,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_runtime_closure_peer_front(S,n_phase,n_closure)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase, obj='0'):
    return [f'{state}_found = $test_runtime_closure_peer_seek({start},{phase},{obj},1500)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_runtime_closure_peer_front({state},{phase},{obj})']


def checks(initial, stdout):
    warning = b'B|N|H|2|41|17|'
    assert stdout == (warning + b'D|41|E|V85_STOP|none|define|false|null|dropped|defined|'
        b'17|1|1|1|kept|31|split|history|A|')
    edge = text('edge')
    values = [*initial, *reach('S_capture','S_initial',0), *common.public('S_capture'),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        '$named_slot_at(pconfigcall_capture.SENT,1) = NAMED_SENT (KNOWN (PARRAY n_input))',
        'pconfigcall_capture.SELECTION = (n_selection)',
        'S_capture.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        '$lookup(S_capture.ENV,$ptascii("closure")) = (n_closure_cv)',
        '$lookup(S_capture.ENV,$ptascii("owner")) = (n_owner_cv)',
        '$lookup(S_capture.ENV,$ptascii("cell")) = (n_cell)',
        '$lookup(S_capture.ENV,$ptascii("input")) = (n_input_cv)',
        '$lookup(S_capture.ENV,$ptascii("api")) = (n_api)',
        '$lookup(S_capture.ENV,$ptascii("calls")) = (n_calls)',
        '$lookup(S_capture.ENV,$ptascii("reads")) = (n_reads)',
        '$lookup(S_capture.ENV,$ptascii("destroyed")) = (n_destroyed)',
        '$lookup(S_capture.ENV,$ptascii("result")) = (n_result)',
        'S_capture.STORE[n_closure_cv] = DEFINED (POBJECT n_closure)',
        'S_capture.STORE[n_owner_cv] = DEFINED (POBJECT n_receiver)',
        'S_capture.OBJECTS[n_closure] = METHODCLOSURE porigin_method porigin_site porigin_requested pmethodcapture?',
        'pobject_closure = S_capture.OBJECTS[n_closure]',
        '$closure_scope_at(S_capture.CLOSURESCOPES,n_closure) = (pclosurescope)',
        'pclosurescope.OBJECT = n_closure',
        'pclosurescope.RECEIVER = (n_receiver)',
        '$method_closure_scope_valid(S_capture,pclosurescope)',
        '$typed_closure(S_capture,n_closure)',
        '$closure_live_object_valid(S_capture,n_closure)',
        'S_capture.STORE[n_cell] = DEFINED (POBJECT n_closure)',
        'n_cell <- S_capture.REFCELLS',
        'S_capture.STORE[n_input_cv] = DEFINED (PARRAY n_input)',
        f'S_capture.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {edge}) (ALIAS n_cell)]',
        'S_capture.ARRAYS[n_input].NEXT = 91',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_closure) = 2',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_receiver) = 2',
        '$heap_edge_owners(HOBJECT n_receiver,$heap_graph(S_capture).EDGES,[HOBJECT n_closure]) = 1',
        '$heap_owners($heap_graph(S_capture),HARRAY n_input) = 2',
        '$heap_edge_owners(HOBJECT n_closure,$heap_graph(S_capture).EDGES,[HCELL n_cell]) = 1',
        *instance.property_value('S_capture','n_receiver',7,'capture'),
        *reach('S','S_capture',1), *common.public('S'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.NAMED', 'pconfigcall.SITE = pconfigcall_capture.SITE',
        'pconfigcall.SELECTION = pconfigcall_capture.SELECTION',
        '$dynamic_define_values(pconfigcall) = ((' + text(TARGET) + ',PARRAY n_input))',
        '$named_slot_at(pconfigcall.SENT,2) = NAMED_SENT (KNOWN (PBOOL false))',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        '$config_invoke_valid(S,pconfigcall)', '$dynamic_array_call_valid(S,pconfigcall)',
        'S.USERCONSTANTS = [puserconstant_old]',
        'puserconstant_old.NAME = ' + text(TARGET),
        'puserconstant_old.VALUE = PINT 17', 'puserconstant_old.CLASS = PVSCALAR',
        'S.CONSTANTOBJECTS = eps', 'S.CONSTANTCLOSURES = eps',
        'S.OBJECTS[n_closure] = pobject_closure',
        '$closure_scope_at(S.CLOSURESCOPES,n_closure) = (pclosurescope)',
        '$typed_closure(S,n_closure)', '$closure_live_object_valid(S,n_closure)',
        '$method_closure_scope_valid(S,pclosurescope)',
        '$constant_callable_record(S.CONSTANTCLOSURES,n_closure) = eps',
        '$dynamic_runtime_object(S,n_closure)',
        '$dynamic_define_value_class(S,POBJECT n_closure) = (PVOBJECT)',
        '~$constant_value_class_valid(S,POBJECT n_closure,PVCLOSURE n_closure pconfigcall.SITE)',
        '~$global_constant_class_supported(PVOBJECT)',
        f'~$global_constant_class_supported(PVARRAY false ([(KSTRING {edge},PVOBJECT)]))',
        'S.STORE[n_closure_cv] = DEFINED PNULL', 'S.STORE[n_owner_cv] = DEFINED PNULL',
        'S.STORE[n_cell] = DEFINED (POBJECT n_closure)',
        'S.STORE[n_input_cv] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        f'S.ARRAYS[n_caller].ITEMS = [ENTRY (KSTRING {edge}) (ALIAS n_cell),ENTRY (KINT 90) (DIRECT (PINT 31))]',
        'S.ARRAYS[n_input] = S_capture.ARRAYS[n_input]',
        'S.STORE[n_api] = DEFINED pvalue_api', '$string_bytes(pvalue_api) = ($ptascii("defined"))',
        'S.STORE[n_calls] = DEFINED (PINT 0)', 'S.STORE[n_reads] = DEFINED (PINT 0)', 'S.STORE[n_destroyed] = DEFINED (PINT 0)',
        'S.STORE[n_result] = DEFINED pvalue_sentinel', '$string_bytes(pvalue_sentinel) = ($ptascii("kept"))',
        '$heap_owners($heap_graph(S),HOBJECT n_closure) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
        '$heap_edge_owners(HOBJECT n_receiver,$heap_graph(S).EDGES,[HOBJECT n_closure]) = 1',
        '$heap_owners($heap_graph(S),HARRAY n_input) = 1',
        '$heap_edge_owners(HOBJECT n_closure,$heap_graph(S).EDGES,[HCELL n_cell]) = 1',
        '$dynamic_array_value(S,PARRAY n_input,eps,false) = eps',
        'n_constants = |S.USERCONSTANTS|', 'n_constants = 1',
        '$dynamic_array_duplicate_call_valid(S,pconfigcall,n_constants)',
        '~$dynamic_constant_duplicate_valid(S,pconfigcall,n_constants)',
        'n_candidate = |S.ARRAYS|',
        '$test_outputs(S.EVENTS) = ($ptascii("B|N|"))',
        # Pure type/receipt controls never enter the machine driver.
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_closure)]',
        '~$dynamic_runtime_object(S_dead,n_closure)',
        '$dynamic_define_value_class(S_dead,POBJECT n_closure) = eps',
        '~$dynamic_runtime_object(S,|S.OBJECTS|)',
        'S_internal = S[.OBJECTS[n_closure] = INTRINSICCLOSURE INTRINSIC_DEFINE]',
        '~$dynamic_runtime_object(S_internal,n_closure)',
        'S_no_scope = S[.CLOSURESCOPES = eps]',
        '~$typed_closure(S_no_scope,n_closure)',
        '~$dynamic_runtime_object(S_no_scope,n_closure)',
        'S_receiver_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_receiver)]',
        '~$dynamic_runtime_object(S_receiver_dead,n_closure)',
        'S_wrapped = S[.OBJECTS[n_closure] = CONSTANTCLOSURE pconfigcall.SITE pobject_closure]',
        '~$dynamic_runtime_object(S_wrapped,n_closure)',
        '$dynamic_define_value_class(S_wrapped,POBJECT n_closure) = eps',
        'S_named = S[.OBJECTS[n_closure] = NAMEDCLOSURE porigin_method]',
        '~$dynamic_runtime_object(S_named,n_closure)',
        'pconstantclosure_bad = {OBJECT n_closure,SITE pconfigcall.SITE,DECL pconfigcall.SITE,PREFIX (|S.DECLARATIONS|)}',
        'S_bad_record = S[.CONSTANTCLOSURES = [pconstantclosure_bad]]',
        '~$dynamic_runtime_object(S_bad_record,n_closure)',
        '$dynamic_define_value_class(S_bad_record,POBJECT n_closure) = eps',
        # The genuine copying dispatch creates a DIRECT private owner.
        *common.step('S_dispatch','S'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants',
        'perrorcall.LEVEL = 2', '$error_call_valid(S_dispatch,perrorcall)',
        'perrorcall.MESSAGE = $global_constant_duplicate_message(' + text(TARGET) + ')',
        f'parray_candidate = $array_insert($array_empty(),KSTRING {edge},DIRECT (POBJECT n_closure))',
        f'pvalueclass = PVARRAY false ([(KSTRING {edge},PVOBJECT)])',
        'S_dispatch.ARRAYS = S.ARRAYS ++ [parray_candidate]',
        'S_dispatch.OBJECTS = S.OBJECTS', 'S_dispatch.OBJECTPROPS = S.OBJECTPROPS',
        'S_dispatch.ALLOCATIONS = S.ALLOCATIONS ++ [HARRAY n_candidate]',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.USERCONSTANTS = S.USERCONSTANTS',
        'S_dispatch.EVENTS = S.EVENTS',
        '$dynamic_array_value(S_dispatch,PARRAY n_candidate,eps,false) = ((S_dispatch,PARRAY n_candidate,pvalueclass))',
        '$dynamic_global_constant_array_tree(S_dispatch,PARRAY n_candidate,pvalueclass)',
        '$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_candidate,pvalueclass,n_constants)',
        '$task_nodes(perrorcall.RESUME) = [HARRAY n_candidate,HARRAY n_input]',
        '$heap_owners($heap_graph(S_dispatch),HARRAY n_candidate) = 1',
        '$heap_owners($heap_graph(S_dispatch),HOBJECT n_closure) = 2',
        '$heap_owners($heap_graph(S_dispatch),HOBJECT n_receiver) = 1',
        '$heap_edge_owners(HOBJECT n_receiver,$heap_graph(S_dispatch).EDGES,[HOBJECT n_closure]) = 1',
        '$heap_edge_owners(HOBJECT n_closure,$heap_graph(S_dispatch).EDGES,[HARRAY n_candidate]) = 1',
        f'pvalueclass_bad = PVARRAY false ([(KSTRING {edge},PVCLOSURE n_closure pconfigcall.SITE)])',
        '~$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_candidate,pvalueclass_bad,n_constants)',
        '~$dynamic_global_constant_array_tree(S_dispatch,PARRAY n_candidate,pvalueclass_bad)',
        # The throwing handler clears the shared source cell, not the snapshot.
        *reach('S_throw','S_dispatch',2), *common.public('S_throw'),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_done) :: ptask_after*',
        'perrorcall_done.RESUME = perrorcall.RESUME',
        '$dynamic_array_duplicate_valid(S_throw,pconfigcall,n_candidate,pvalueclass,n_constants)',
        'S_throw.STORE[n_cell] = DEFINED PNULL', 'S_throw.STORE[n_closure_cv] = DEFINED PNULL',
        'S_throw.STORE[n_owner_cv] = DEFINED PNULL',
        'S_throw.STORE[n_calls] = DEFINED (PINT 1)', 'S_throw.STORE[n_reads] = DEFINED (PINT 1)', 'S_throw.STORE[n_destroyed] = DEFINED (PINT 0)',
        'S_throw.STORE[n_result] = DEFINED pvalue_sentinel',
        'S_throw.USERCONSTANTS = S.USERCONSTANTS',
        'S_throw.ARRAYS[n_candidate] = parray_candidate',
        'S_throw.ARRAYS[n_input] = S.ARRAYS[n_input]',
        'S_throw.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'pthrowable_error.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_error,"message")) = ($ptascii("V85_STOP"))',
        '$throwable_field(S_throw,n_error,"previous") = PNULL',
        '$throwable_chain_valid(S_throw,n_error)',
        '$throwable_field(S_throw,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_throw.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_throw,n_frame,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_throw,n_frame,$ptascii("args")) = PARRAY n_args',
        '$entry_lookup(S_throw.ARRAYS[n_args].ITEMS,KINT 1) = (DIRECT (PARRAY n_input))',
        '$entry_lookup(S_throw.ARRAYS[n_args].ITEMS,KINT 2) = (DIRECT (PBOOL false))',
        '$heap_owners($heap_graph(S_throw),HOBJECT n_closure) = 1',
        '$heap_owners($heap_graph(S_throw),HOBJECT n_receiver) = 1',
        '$heap_edge_owners(HOBJECT n_receiver,$heap_graph(S_throw).EDGES,[HOBJECT n_closure]) = 1',
        '$heap_owners($heap_graph(S_throw),HARRAY n_candidate) = 1',
        '$heap_owners($heap_graph(S_throw),HARRAY n_input) = 2',
        '$heap_edge_owners(HOBJECT n_closure,$heap_graph(S_throw).EDGES,[HARRAY n_candidate]) = 1',
        '$heap_edge_owners(HOBJECT n_closure,$heap_graph(S_throw).EDGES,[HCELL n_cell,HARRAY n_args]) = 0',
        '$heap_edge_owners(HARRAY n_input,$heap_graph(S_throw).EDGES,[HARRAY n_args]) = 1',
        *instance.property_value('S_throw','n_receiver',41,'throw'),
        '~(n_receiver <- S_throw.DESTRUCTION.CALLED)',
        '$test_outputs(S_throw.EVENTS) = ' + term(warning),
        # Real marker removal releases the sole Closure owner, then its receiver.
        'S_pause = $drive_steps(S_throw,0)', 'S_pause = S_throw[.COMPLETION = BUDGET]',
        'S_resume = $test_running(S_pause)', 'S_resume = S_throw',
        *common.step('S_drop','S_resume'),
        *reach('S_free','S_drop',3,'n_receiver'), *common.public('S_free'),
        'S_free.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_free*',
        'pdestructorcall.OBJECT = n_receiver', '~pdestructorcall.STORE',
        'pdestructorcall.RELEASE = (pdestructionrelease)',
        'pdestructorcall.FRAME = eps',
        'pdestructorcall.OPERATION = (pdestructionoperation)',
        'pdestructorcall.PENDING = (n_error)',
        'pdestructionoperation.PENDING = (n_error)',
        'pdestructionoperation.SOURCE = THROW_SEARCH n_error',
        '$destructor_enter_valid(S_free,pdestructorcall)',
        '~(HARRAY n_candidate <- S_free.ALLOCATIONS)',
        '~(HOBJECT n_closure <- S_free.ALLOCATIONS)',
        '$heap_edge_owners(HOBJECT n_receiver,$heap_graph(S_free).EDGES,[HOBJECT n_closure]) = 0',
        '$heap_owners($heap_graph(S_free),HOBJECT n_receiver) = 2',
        'n_receiver <- S_free.DESTRUCTION.CALLED',
        'S_free.STORE[n_destroyed] = DEFINED (PINT 0)',
        'S_free.USERCONSTANTS = S.USERCONSTANTS',
        '$test_outputs(S_free.EVENTS) = ' + term(warning),
        *instance.property_value('S_free','n_receiver',41,'free'),
        *reach('S_after','S_free',4,'n_receiver'), *common.public('S_after'),
        'S_after.TODO = (THROW_SEARCH n_error) :: ptask_after*',
        'S_after.USERCONSTANTS = S.USERCONSTANTS',
        'S_after.ERRORHANDLER.CALLBACK = (perrorcall_done.CALLBACK)',
        'S_after.STORE[n_result] = DEFINED pvalue_sentinel',
        'S_after.STORE[n_destroyed] = DEFINED (PINT 1)',
        'S_after.STORE[n_calls] = DEFINED (PINT 1)', 'S_after.STORE[n_reads] = DEFINED (PINT 1)',
        'S_after.STORE[n_cell] = DEFINED PNULL',
        'S_after.OBJECTS[n_error] = THROWABLE pthrowable_error',
        '$throwable_field(S_after,n_error,"previous") = PNULL',
        '$heap_owners($heap_graph(S_after),HARRAY n_input) = 1',
        '$heap_edge_owners(HARRAY n_input,$heap_graph(S_after).EDGES,[HARRAY n_args]) = 1',
        '~(HOBJECT n_closure <- S_after.ALLOCATIONS)',
        '~(HOBJECT n_receiver <- S_after.ALLOCATIONS)',
        '~(HARRAY n_candidate <- S_after.ALLOCATIONS)',
        '$test_outputs(S_after.EVENTS) = ' + term(warning + b'D|41|'),
        *define.finish('S_after',stdout),
        'S_final.USERCONSTANTS = S.USERCONSTANTS',
        'S_final.CONSTANTOBJECTS = eps',
        'n_receiver <- S_final.DESTRUCTION.CALLED',
        '~(HOBJECT n_closure <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_receiver <- S_final.ALLOCATIONS)',
        '~(HARRAY n_candidate <- S_final.ALLOCATIONS)',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)',
        '~(HARRAY n_caller <- S_final.ALLOCATIONS)',
        '~(HCELL n_cell <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_final.ALLOCATIONS)',
        '~(HARRAY n_frame <- S_final.ALLOCATIONS)',
        '~(HARRAY n_args <- S_final.ALLOCATIONS)']
    return values


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = packet.process


def process(command, directory, timeout, cwd):
    if directory.parent.name == CASE:
        timeout = 180
    return packet_process(command, directory, timeout, cwd)


packet.process = process
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    raise SystemExit(0 if packet.main() else 1)
