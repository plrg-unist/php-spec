#!/usr/bin/env python3
"""Factory VALUE permission boundary and raw private-denial receiver lifetime."""
from pathlib import Path

import define_runtime_closure_protocol as runtime
import define_stdclass_array_duplicate_review_protocol as prior
import define_runtime_from_factory_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
TARGET = 'V92_REVIEW_FACTORY'
CASE = 'published-factory-global-denial-retains-raw-receiver-trace'
PREFIX = runtime.PREFIX + r'''
dec $test_factory_value_peer_front(pstate, nat, nat) : bool
def $test_factory_value_peer_front(S,0,n_object) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V92_REVIEW_FACTORY"),POBJECT n_factory))
def $test_factory_value_peer_front(S,1,n_object) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_FROM_CALLABLE_FACTORY /\ pconfigcall.INDEX = 0
  -- if pconfigcall.OWNER = (n_object)
def $test_factory_value_peer_front(S,2,n_object) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_FROM_CALLABLE_FACTORY
  -- if pconfigcall.OWNER = (n_object)
def $test_factory_value_peer_front(S,3,n_object) = true
  -- if S.TODO = (THROW_SEARCH n_object) :: ptask_tail*
  -- if S.OBJECTS[n_object] = THROWABLE pthrowable
  -- if pthrowable.KIND = "TypeError"
def $test_factory_value_peer_front(S,4,n_object) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OBJECT = n_object /\ ~pdestructorcall.STORE
def $test_factory_value_peer_front(S,n_phase,n_object) = false -- otherwise
dec $test_factory_value_peer_seek(pstate, nat, nat, nat) : pstate
def $test_factory_value_peer_seek(S,n_phase,n_object,0) = S
def $test_factory_value_peer_seek(S,n_phase,n_object,n) = S
  -- if $(n > 0)
  -- if $test_factory_value_peer_front(S,n_phase,n_object) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_factory_value_peer_seek(S,n_phase,n_object,n) = $test_factory_value_peer_seek($drive_steps($test_running(S),1),n_phase,n_object,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_factory_value_peer_front(S,n_phase,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase, obj='0'):
    return [f'{state}_found = $test_factory_value_peer_seek({start},{phase},{obj},1500)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_factory_value_peer_front({state},{phase},{obj})']


def private_value(state, value, label):
    return [f'$objectprops_at({state}.OBJECTPROPS,n_receiver) = (ppropertyslot_all_{label}*)',
        f'$property_slot_at(ppropertyslot_all_{label}*,ppropertydesc_value.KEY) = (ppropertyslot_{label})',
        f'ppropertyslot_{label}.DECL = (ppropertydesc_value.ORIGIN)',
        f'ppropertyslot_{label}.STATE = PROP_VALUE (DIRECT (PINT {value}))']


def controls():
    return ['~$global_constant_class_supported(PVOBJECT)',
        '~$constant_value_class_valid(S,POBJECT n_factory,PVCLOSURE n_factory porigin_create)',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_factory)]',
        '$from_factory_saved(S_dead,n_factory)', '~$from_factory_live(S_dead,n_factory)',
        '~$typed_closure(S_dead,n_factory)', '$dynamic_define_value_class(S_dead,POBJECT n_factory) = eps',
        '~$dynamic_runtime_object(S,|S.OBJECTS|)',
        'S_wrong_site = S[.OBJECTS[n_factory] = FROMCALLABLEFACTORY pconfigcall.SITE]',
        '~$from_factory_saved(S_wrong_site,n_factory)', '~$dynamic_runtime_object(S_wrong_site,n_factory)',
        'S_no_source = S[.SOURCES = eps]', '~$from_factory_saved(S_no_source,n_factory)',
        '~$dynamic_runtime_object(S_no_source,n_factory)',
        'pclosurescope_bad = {OBJECT n_factory,LEXICAL porigin_class,CALLED porigin_class,RECEIVER eps,CREATION eps}',
        'S_scope = S[.CLOSURESCOPES = [pclosurescope_bad]]',
        '$typed_closure(S_scope,n_factory)', '~$closure_scope_complete(S_scope,[HOBJECT n_factory])',
        '~$dynamic_runtime_object(S_scope,n_factory)',
        'pclosurebinding_bad = {OBJECT n_factory,SITE pconfigcall.SITE,SOURCE n_factory,LEXICAL (porigin_class),CALLED (porigin_class),RECEIVER eps}',
        'S_binding = S[.CLOSUREBINDINGS = [pclosurebinding_bad]]',
        '$typed_closure(S_binding,n_factory)', '~$dynamic_runtime_object(S_binding,n_factory)',
        'S_internal = S[.OBJECTS[n_factory] = INTRINSICCLOSURE INTRINSIC_DEFINE]',
        '$typed_closure(S_internal,n_factory)', '~$dynamic_runtime_object(S_internal,n_factory)',
        'S_wrapped = S[.OBJECTS[n_factory] = CONSTANTCLOSURE pconfigcall.SITE (S.OBJECTS[n_factory])]',
        '$dynamic_define_value_class(S_wrapped,POBJECT n_factory) = eps',
        'pconstantclosure_bad = {OBJECT n_factory,SITE pconfigcall.SITE,DECL pconfigcall.SITE,PREFIX (|S.DECLARATIONS|)}',
        'S_record = S[.CONSTANTCLOSURES = [pconstantclosure_bad]]',
        '~$dynamic_runtime_object(S_record,n_factory)',
        '$dynamic_define_value_class(S_record,POBJECT n_factory) = eps']


def checks(initial, stdout):
    kept = b'B|T|same|N|E|fromCallable|__invoke|none|read|dropped|defined|kept|0|0|0|shared|41|kept-trace|'
    after = kept + b'D|41|released|1|'
    assert stdout == after + b'factory|A|'
    message = text('Failed to create closure from callable: cannot access private method V92ReviewReceiver::read()')
    values = [*initial, *reach('S','S_initial',0), *common.public('S'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        '$dynamic_define_values(pconfigcall) = ((' + text(TARGET) + ',POBJECT n_factory))',
        '$config_invoke_valid(S,pconfigcall)',
        '$lookup(S.ENV,$ptascii("factory")) = (n_factory_cv)',
        'S.STORE[n_factory_cv] = DEFINED (POBJECT n_factory)',
        'S.OBJECTS[n_factory] = FROMCALLABLEFACTORY porigin_create',
        '$from_factory_site(S,porigin_create)', '$from_factory_live(S,n_factory)',
        '$closure_source_class(S,porigin_create) = (porigin_class)',
        '$class_at(S.CLASSES,porigin_class) = (pclassdesc)',
        'pclassdesc.NAME = ($ptascii("V92ReviewReceiver"))',
        'pclassdesc.PROPERTIES = [ppropertydesc_value]',
        'ppropertydesc_value.NAME = ($ptascii("value"))',
        'ppropertydesc_value.VISIBILITY = PROPERTY_PRIVATE',
        '$effective_method(S,porigin_class,$ptascii("read"),|S.CLASSES|) = (pmethoddesc_read)',
        'pmethoddesc_read.VISIBILITY = PROPERTY_PRIVATE', '~pmethoddesc_read.STATIC',
        '$typed_closure(S,n_factory)', '$closure_live_object_valid(S,n_factory)',
        '$closure_scope_at(S.CLOSURESCOPES,n_factory) = eps',
        '$closure_binding_at(S.CLOSUREBINDINGS,n_factory) = eps',
        '$constant_callable_record(S.CONSTANTCLOSURES,n_factory) = eps',
        '$closure_scope_complete(S,[HOBJECT n_factory])',
        '$dynamic_define_value_class(S,POBJECT n_factory) = (PVOBJECT)',
        '$node_children(S,HOBJECT n_factory) = eps',
        'S.USERCONSTANTS = eps', 'S.STATICS = eps',
        '$heap_owners($heap_graph(S),HOBJECT n_factory) = 2',
        '$test_outputs(S.EVENTS) = ($ptascii("B|"))',
        # Structural projections are not driven and never supply USER permission.
        *controls(),
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        '$test_running(S_pause) = S',
        *common.step('S_row','S','PBOOL true'),
        '$drive_steps($test_running(S_pause),1) = S_row_found',
        'S_row.TODO = ptask_initial*', 'S_row.USERCONSTANTS = [puserconstant]',
        'puserconstant.ORIGIN = pconfigcall.SITE', 'puserconstant.VALUE = POBJECT n_factory',
        'puserconstant.CLASS = PVOBJECT',
        '$heap_owners($heap_graph(S_row),HOBJECT n_factory) = 2']
    values += [f'S_row.{field} = S.{field}' for field in
        ['OBJECTS','ARRAYS','ALLOCATIONS','STORE','CLOSURESCOPES','CLOSUREBINDINGS','CONSTANTCLOSURES']]
    values += ['puserconstant_bad = puserconstant[.ORIGIN = PORIGIN 0 eps]',
        '$dynamic_global_constant_value(S_row[.USERCONSTANTS = [puserconstant_bad]],' + text(TARGET) + ') = eps',
        *common.reach('S_query','S_row',0,TARGET),
        '$dynamic_global_constant_value(S_query,' + text(TARGET) + ') = (POBJECT n_factory)',
        *common.step('S_value','S_query','POBJECT n_factory'),
        '$heap_owners($heap_graph(S_value),HOBJECT n_factory) = 3',
        'S_value.ALLOCATIONS = S_query.ALLOCATIONS',
        *reach('S_capture','S_value',1,'n_factory'), *common.public('S_capture'),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        '$from_factory_invoke_site(S_capture,pconfigcall_capture.SITE)',
        'pconfigcall_capture.OWNER = (n_factory)',
        '$lookup(S_capture.ENV,$ptascii("factory")) = eps',
        '$lookup(S_capture.ENV,$ptascii("call")) = (n_call)',
        '$lookup(S_capture.ENV,$ptascii("owner")) = (n_owner)',
        '$lookup(S_capture.ENV,$ptascii("result")) = (n_result)',
        '$lookup(S_capture.ENV,$ptascii("reads")) = (n_reads)',
        '$lookup(S_capture.ENV,$ptascii("calls")) = (n_calls)',
        '$lookup(S_capture.ENV,$ptascii("destroyed")) = (n_destroyed)',
        'S_capture.STORE[n_call] = DEFINED (POBJECT n_factory)',
        'S_capture.STORE[n_owner] = DEFINED (POBJECT n_receiver)',
        'S_capture.OBJECTS[n_receiver] = INSTANCE porigin_class',
        '$node_children(S_capture,HOBJECT n_factory) = eps',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_factory) = 3',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_receiver) = 1',
        *reach('S_inv','S_capture',2,'n_factory'), *common.public('S_inv'),
        'S_inv.TODO = (CONFIG_INVOKE pconfigcall_invoke) :: ptask_invoke*',
        'pconfigcall_invoke.SITE = pconfigcall_capture.SITE',
        'pconfigcall_invoke.OWNER = (n_factory)', 'pconfigcall_invoke.NAMED',
        'pconfigcall_invoke.SENT = [NAMED_SENT (KNOWN (PARRAY n_callback))]',
        '$config_invoke_valid(S_inv,pconfigcall_invoke)',
        '$from_factory_owner(S_inv,pconfigcall_invoke) = (n_factory)',
        '$task_nodes(CONFIG_INVOKE pconfigcall_invoke) = [HOBJECT n_factory,HARRAY n_callback]',
        '$closure_source_class(S_inv,pconfigcall_invoke.SITE) = eps',
        'S_inv.CURRENT = eps', '$api_frame_scope(S_inv) = eps',
        'S_inv.STORE[n_owner] = DEFINED PNULL',
        'S_inv.STORE[n_call] = DEFINED pvalue_call',
        '$string_bytes(pvalue_call) = ($ptascii("defined"))',
        'S_inv.STORE[n_result] = DEFINED pvalue_sentinel',
        '$string_bytes(pvalue_sentinel) = ($ptascii("kept"))',
        'S_inv.STORE[n_reads] = DEFINED (PINT 0)',
        'S_inv.STORE[n_calls] = DEFINED (PINT 0)',
        'S_inv.STORE[n_destroyed] = DEFINED (PINT 0)',
        'S_inv.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_inv.ARRAYS[n_callback].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)),ENTRY (KINT 1) (DIRECT pvalue_method)]',
        '$string_bytes(pvalue_method) = ($ptascii("read"))',
        '~$method_accessible(S_inv,pmethoddesc_read,eps)',
        '$method_accessible(S_inv,pmethoddesc_read,(porigin_class))',
        '$api_pure(S_inv,PARRAY n_callback) = HANDLERINVALID ($ptascii("cannot access private method V92ReviewReceiver::read()"))',
        '$heap_owners($heap_graph(S_inv),HOBJECT n_factory) = 2',
        '$heap_owners($heap_graph(S_inv),HOBJECT n_receiver) = 1',
        '$heap_edge_owners(HOBJECT n_receiver,$heap_graph(S_inv).EDGES,[HARRAY n_callback]) = 1',
        '$heap_edge_owners(HOBJECT n_receiver,$heap_graph(S_inv).EDGES,[HOBJECT n_factory]) = 0',
        *private_value('S_inv',7,'receiver_before'),
        '$test_outputs(S_inv.EVENTS) = ($ptascii("B|T|same|N|"))',
        'n_error = |S_inv.OBJECTS|', 'n_arrays = |S_inv.ARRAYS|',
        *reach('S_error','S_inv',3,'n_error'), *common.public('S_error'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_error*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'pthrowable_error.KIND = "TypeError"', 'pthrowable_error.ORIGIN = (pconfigcall_invoke.SITE)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + message + ')',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_error.ARRAYS[n_trace].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame_api))',
        '$entry_lookup(S_error.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_frame_invoke))',
        '$trace_array_field(S_error,n_frame_api,$ptascii("function")) = PSTRING ($ptascii("fromCallable"))',
        '$trace_array_field(S_error,n_frame_invoke,$ptascii("function")) = PSTRING ($ptascii("__invoke"))',
        '$trace_array_field(S_error,n_frame_api,$ptascii("args")) = PARRAY n_args_api',
        '$trace_array_field(S_error,n_frame_invoke,$ptascii("args")) = PARRAY n_args_invoke',
        '$entry_lookup(S_error.ARRAYS[n_args_api].ITEMS,KINT 0) = (DIRECT (PARRAY n_callback))',
        '$entry_lookup(S_error.ARRAYS[n_args_invoke].ITEMS,KINT 0) = (DIRECT (PARRAY n_callback))',
        'n_trace = n_arrays', 'n_args_api = $(n_arrays + 1)', 'n_frame_api = $(n_arrays + 2)',
        'n_args_invoke = $(n_arrays + 3)', 'n_frame_invoke = $(n_arrays + 4)',
        '$heap_edge_owners(HARRAY n_callback,$heap_graph(S_error).EDGES,[HARRAY n_args_api,HARRAY n_args_invoke]) = 2',
        '$heap_edge_owners(HOBJECT n_receiver,$heap_graph(S_error).EDGES,[HARRAY n_callback]) = 1',
        '~(n_receiver <- S_error.DESTRUCTION.CALLED)',
        *runtime.unset('S_kept','S_error','receiver'),
        '$test_outputs(S_kept.EVENTS) = ' + term(kept),
        '$lookup(S_kept.ENV,$ptascii("error")) = (n_error_cv)',
        '$lookup(S_kept.ENV,$ptascii("raw")) = (n_raw_cv)',
        '$lookup(S_kept.ENV,$ptascii("receiver")) = (n_receiver_cv)',
        'S_kept.STORE[n_error_cv] = DEFINED (POBJECT n_error)',
        'S_kept.STORE[n_raw_cv] = DEFINED (PARRAY n_callback)',
        'S_kept.STORE[n_receiver_cv] = DEFINED (POBJECT n_receiver)',
        'S_kept.STORE[n_destroyed] = DEFINED (PINT 0)',
        'S_kept.STORE[n_reads] = DEFINED (PINT 0)', 'S_kept.STORE[n_calls] = DEFINED (PINT 0)',
        'S_kept.STORE[n_result] = DEFINED pvalue_sentinel',
        '$heap_owners($heap_graph(S_kept),HOBJECT n_factory) = 1',
        '$heap_owners($heap_graph(S_kept),HOBJECT n_receiver) = 2',
        '$heap_owners($heap_graph(S_kept),HARRAY n_callback) = 3',
        '$heap_edge_owners(HARRAY n_callback,$heap_graph(S_kept).EDGES,[HARRAY n_args_api,HARRAY n_args_invoke]) = 2',
        '$heap_edge_owners(HOBJECT n_receiver,$heap_graph(S_kept).EDGES,[HARRAY n_callback]) = 1',
        '$node_children(S_kept,HOBJECT n_factory) = eps',
        *private_value('S_kept',41,'receiver_kept'),
        'S_kept.USERCONSTANTS = S_row.USERCONSTANTS',
        *reach('S_free','S_kept',4,'n_receiver'), *common.public('S_free'),
        'S_free.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_free*',
        'pdestructorcall.OBJECT = n_receiver', '~pdestructorcall.STORE',
        'pdestructorcall.PENDING = eps', '$destructor_enter_valid(S_free,pdestructorcall)',
        '$task_nodes(DESTRUCTOR_ENTER pdestructorcall) = [HOBJECT n_receiver,HOBJECT n_receiver]',
        '$heap_owners($heap_graph(S_free),HOBJECT n_receiver) = 2',
        '$heap_edge_owners(HOBJECT n_receiver,$heap_graph(S_free).EDGES,[HARRAY n_callback]) = 0',
        '~(HARRAY n_callback <- S_free.ALLOCATIONS)',
        'S_free.STORE[n_destroyed] = DEFINED (PINT 0)',
        '$test_outputs(S_free.EVENTS) = ' + term(kept),
        *private_value('S_free',41,'receiver_free'),
        *common.reach('S_again','S_free',0,TARGET),
        '$test_outputs(S_again.EVENTS) = ' + term(after),
        'S_again.STORE[n_destroyed] = DEFINED (PINT 1)',
        'S_again.USERCONSTANTS = S_row.USERCONSTANTS',
        '~(HOBJECT n_receiver <- S_again.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_again.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_again.ALLOCATIONS)',
        '~(HARRAY n_frame_api <- S_again.ALLOCATIONS)',
        '~(HARRAY n_frame_invoke <- S_again.ALLOCATIONS)',
        '~(HARRAY n_args_api <- S_again.ALLOCATIONS)',
        '~(HARRAY n_args_invoke <- S_again.ALLOCATIONS)',
        '~(HARRAY n_callback <- S_again.ALLOCATIONS)',
        '$dynamic_global_constant_value(S_again,' + text(TARGET) + ') = (POBJECT n_factory)',
        *common.step('S_again_value','S_again','POBJECT n_factory'),
        '$heap_owners($heap_graph(S_again_value),HOBJECT n_factory) = 2',
        *define.finish('S_again_value',stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS',
        '$heap_owners($heap_graph(S_final),HOBJECT n_factory) = 1',
        '$from_factory_live(S_final,n_factory)', '$node_children(S_final,HOBJECT n_factory) = eps',
        'S_final.STATICS = eps', 'n_receiver <- S_final.DESTRUCTION.CALLED',
        '~(HOBJECT n_receiver <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)',
        '~(HARRAY n_callback <- S_final.ALLOCATIONS)']
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
