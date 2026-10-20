#!/usr/bin/env python3
"""Reached fixed parent-string selection despite a Child override."""
from pathlib import Path

import define_stdclass_array_duplicate_review_protocol as prior
import define_runtime_string_closure_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
TARGET = 'V90_REVIEW_OLD'
CASE = 'fixed-parent-string-closure-private-copy-retires-receiver-before-catch'
PREFIX = define.PREFIX + r'''
dec $test_string_method_peer_front(pstate, nat, nat) : bool
def $test_string_method_peer_front(S,0,n_closure) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.INDEX = 2
  -- if $named_slot_at(pconfigcall.SENT,0) = NAMED_HOLE
  -- if $named_slot_at(pconfigcall.SENT,1) = NAMED_SENT (KNOWN (PARRAY n_input))
  -- if $named_slot_at(pconfigcall.SENT,2) = NAMED_SENT (KNOWN (PBOOL false))
def $test_string_method_peer_front(S,1,n_closure) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V90_REVIEW_OLD"),PARRAY n_input))
def $test_string_method_peer_front(S,2,n_closure) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V90_REVIEW_OLD"),PARRAY n_input))
def $test_string_method_peer_front(S,3,n_closure) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OBJECT = n_closure /\ ~pdestructorcall.STORE
def $test_string_method_peer_front(S,4,n_closure) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask_tail*
  -- if ~$test_string_method_peer_front(S,2,n_closure)
  -- if S.DESTRUCTION.OPERATIONS = eps
def $test_string_method_peer_front(S,n_phase,n_closure) = false -- otherwise
dec $test_string_method_peer_seek(pstate, nat, nat, nat) : pstate
def $test_string_method_peer_seek(S,n_phase,n_closure,0) = S
def $test_string_method_peer_seek(S,n_phase,n_closure,n) = S
  -- if $(n > 0)
  -- if $test_string_method_peer_front(S,n_phase,n_closure) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_string_method_peer_seek(S,n_phase,n_closure,n) = $test_string_method_peer_seek($drive_steps($test_running(S),1),n_phase,n_closure,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_string_method_peer_front(S,n_phase,n_closure)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase, obj='0'):
    return [f'{state}_found = $test_string_method_peer_seek({start},{phase},{obj},1500)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_string_method_peer_front({state},{phase},{obj})']


def private_values(state, value, label):
    return [f'$objectprops_at({state}.OBJECTPROPS,n_receiver) = (ppropertyslot_all_{label}*)',
        f'$property_slot_at(ppropertyslot_all_{label}*,ppropertydesc_base.KEY) = (ppropertyslot_base_{label})',
        f'ppropertyslot_base_{label}.DECL = (ppropertydesc_base.ORIGIN)',
        f'ppropertyslot_base_{label}.STATE = PROP_VALUE (DIRECT (PINT {value}))',
        f'$property_slot_at(ppropertyslot_all_{label}*,ppropertydesc_shadow.KEY) = (ppropertyslot_shadow_{label})',
        f'ppropertyslot_shadow_{label}.DECL = (ppropertydesc_shadow.ORIGIN)',
        f'ppropertyslot_shadow_{label}.STATE = PROP_VALUE (DIRECT (PINT 97))']


def controls():
    return ['S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_closure)]',
        '$dynamic_define_value_class(S_dead,POBJECT n_closure) = eps',
        '~$dynamic_runtime_object(S,|S.OBJECTS|)',
        'S_no_scope = S[.CLOSURESCOPES = eps]',
        '~$typed_closure(S_no_scope,n_closure)',
        '~$closure_scope_complete(S_no_scope,[HOBJECT n_closure])',
        '~$dynamic_runtime_object(S_no_scope,n_closure)',
        'S_receiver_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_receiver)]',
        '~$typed_closure(S_receiver_dead,n_closure)',
        '~$closure_live_object_valid(S_receiver_dead,n_closure)',
        '$closure_scope_complete(S_receiver_dead,[HOBJECT n_closure])',
        '~$closure_scope_row_valid(S_receiver_dead,pclosurescope)',
        '~$dynamic_runtime_object(S_receiver_dead,n_closure)',
        'S_wrong_lexical = S[.CLOSURESCOPES = [pclosurescope[.LEXICAL = pclosurescope.CALLED]]]',
        '~$dynamic_runtime_object(S_wrong_lexical,n_closure)',
        'S_wrong_called = S[.CLOSURESCOPES = [pclosurescope[.CALLED = pclosurescope.LEXICAL]]]',
        '~$dynamic_runtime_object(S_wrong_called,n_closure)',
        'S_wrong_site = S[.OBJECTS[n_closure] = STRINGMETHODCLOSURE pcalltarget pstringselection[.SITE = pconfigcall.SITE]]',
        '~$dynamic_runtime_object(S_wrong_site,n_closure)',
        'S_wrong_requested = S[.OBJECTS[n_closure] = STRINGMETHODCLOSURE pcalltarget pstringselection[.REQUESTED = pclosurescope.CALLED]]',
        '~$dynamic_runtime_object(S_wrong_requested,n_closure)',
        'S_wrong_method = S[.OBJECTS[n_closure] = STRINGMETHODCLOSURE pcalltarget pstringselection[.ORIGINAL = $ptascii("V90ReviewBase::absent")]]',
        '~$dynamic_runtime_object(S_wrong_method,n_closure)',
        'S_no_classes = S[.CLASSES = eps]',
        '~$dynamic_runtime_object(S_no_classes,n_closure)',
        'pclosurebinding_bad = {OBJECT n_closure,SITE pconfigcall.SITE,SOURCE n_closure,LEXICAL (pclosurescope.LEXICAL),CALLED (pclosurescope.CALLED),RECEIVER (n_receiver)}',
        'S_binding = S[.CLOSUREBINDINGS = [pclosurebinding_bad]]',
        '$typed_closure(S_binding,n_closure)',
        '$closure_live_object_valid(S_binding,n_closure)',
        '~$dynamic_runtime_object(S_binding,n_closure)',
        'S_internal = S[.OBJECTS[n_closure] = INTRINSICCLOSURE INTRINSIC_DEFINE]',
        '~$dynamic_runtime_object(S_internal,n_closure)',
        'S_wrapped = S[.OBJECTS[n_closure] = CONSTANTCLOSURE pconfigcall.SITE pobject_closure]',
        '~$dynamic_runtime_object(S_wrapped,n_closure)',
        '$dynamic_define_value_class(S_wrapped,POBJECT n_closure) = eps',
        'pconstantclosure_bad = {OBJECT n_closure,SITE pconfigcall.SITE,DECL pconfigcall.SITE,PREFIX (|S.DECLARATIONS|)}',
        'S_record = S[.CONSTANTCLOSURES = [pconstantclosure_bad]]',
        '~$dynamic_runtime_object(S_record,n_closure)',
        '$dynamic_define_value_class(S_record,POBJECT n_closure) = eps']


def checks(initial, stdout):
    warning = b'B|N|C|41|97|V90ReviewReceiver|H|2|41|17|'
    assert stdout == (warning + b'D|41|E|V90_STOP|none|define|false|null|dropped|defined|'
        b'17|1|1|1|kept|31|split|history|A|')
    edge = text('edge')
    values = [*initial, *reach('S_capture','S_initial',0), *common.public('S_capture'),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        '$named_slot_at(pconfigcall_capture.SENT,1) = NAMED_SENT (KNOWN (PARRAY n_input))',
        'pconfigcall_capture.SELECTION = (n_selection)',
        'S_capture.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        '$lookup(S_capture.ENV,$ptascii("owner")) = (n_owner_cv)',
        '$lookup(S_capture.ENV,$ptascii("cell")) = (n_cell)',
        '$lookup(S_capture.ENV,$ptascii("input")) = (n_input_cv)',
        '$lookup(S_capture.ENV,$ptascii("api")) = (n_api)',
        '$lookup(S_capture.ENV,$ptascii("calls")) = (n_calls)',
        '$lookup(S_capture.ENV,$ptascii("reads")) = (n_reads)',
        '$lookup(S_capture.ENV,$ptascii("destroyed")) = (n_destroyed)',
        '$lookup(S_capture.ENV,$ptascii("result")) = (n_result)',
        'S_capture.STORE[n_owner_cv] = DEFINED (POBJECT n_receiver)',
        'S_capture.STORE[n_cell] = DEFINED (POBJECT n_closure)',
        'S_capture.OBJECTS[n_closure] = STRINGMETHODCLOSURE pcalltarget pstringselection',
        '$string_target_identity(S_capture,pcalltarget,pstringselection)',
        '$string_site_valid(S_capture,pstringselection,true)',
        'pstringselection.ORIGINAL = $ptascii("V90ReviewBase::read")',
        '$target_function(S_capture,pcalltarget) = (pfunction_read)',
        '$class_method_origin(S_capture.CLASSES,pfunction_read.ORIGIN) = (pmethoddesc_read)',
        'pobject_closure = S_capture.OBJECTS[n_closure]',
        '$closure_scope_at(S_capture.CLOSURESCOPES,n_closure) = (pclosurescope)',
        'pclosurescope.OBJECT = n_closure',
        'pclosurescope.RECEIVER = (n_receiver)',
        'pclosurescope.LEXICAL =/= pclosurescope.CALLED',
        'pclosurescope.CREATION = eps',
        '$closure_binding_at(S_capture.CLOSUREBINDINGS,n_closure) = eps',
        '$closure_scope_row_valid(S_capture,pclosurescope)',
        '$closure_scope_complete(S_capture,[HOBJECT n_closure])',
        'pmethoddesc_read.OWNER = pclosurescope.LEXICAL',
        'pmethoddesc_read.VISIBILITY = PROPERTY_PUBLIC',
        '~pmethoddesc_read.STATIC',
        'pstringselection.REQUESTED = pclosurescope.LEXICAL',
        '$class_at(S_capture.CLASSES,pclosurescope.LEXICAL) = (pclassdesc_base)',
        'pclassdesc_base.NAME = ($ptascii("V90ReviewBase"))',
        'pclassdesc_base.PROPERTIES = [ppropertydesc_base]',
        '$class_at(S_capture.CLASSES,pclosurescope.CALLED) = (pclassdesc_receiver)',
        'pclassdesc_receiver.NAME = ($ptascii("V90ReviewReceiver"))',
        'pclassdesc_receiver.PROPERTIES = [ppropertydesc_shadow]',
        'pcalltarget = SCOPED_TARGET pclosurescope.LEXICAL pfunction_read.ORIGIN pclosurescope.CALLED (n_receiver) (KNOWN (PSTRING ($ptascii("V90ReviewBase"))))',
        '$dynamic_fixed_name(S_capture,pstringselection.SITE) = ($ptascii("V90ReviewBase::read"))',
        '$effective_method(S_capture,pclosurescope.LEXICAL,$ptascii("read"),|S_capture.CLASSES|) = (pmethoddesc_read)',
        '$effective_method(S_capture,pclosurescope.CALLED,$ptascii("read"),|S_capture.CLASSES|) = (pmethoddesc_override)',
        'pmethoddesc_override.FUNCTION.ORIGIN =/= pfunction_read.ORIGIN',
        'pmethoddesc_override.OWNER = pclosurescope.CALLED',
        'S_capture.OBJECTS[n_receiver] = INSTANCE pclosurescope.CALLED',
        '$typed_closure(S_capture,n_closure)',
        '$closure_live_object_valid(S_capture,n_closure)',
        'n_cell <- S_capture.REFCELLS',
        'S_capture.STORE[n_input_cv] = DEFINED (PARRAY n_input)',
        f'S_capture.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {edge}) (ALIAS n_cell)]',
        'S_capture.ARRAYS[n_input].NEXT = 91',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_closure) = 1',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_receiver) = 2',
        '$heap_edge_owners(HOBJECT n_receiver,$heap_graph(S_capture).EDGES,[HOBJECT n_closure]) = 1',
        '$heap_owners($heap_graph(S_capture),HARRAY n_input) = 2',
        '$heap_edge_owners(HOBJECT n_closure,$heap_graph(S_capture).EDGES,[HCELL n_cell]) = 1',
        *private_values('S_capture',7,'capture'),
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
        '$closure_scope_row_valid(S,pclosurescope)',
        '$closure_scope_complete(S,[HOBJECT n_closure])',
        '$closure_binding_at(S.CLOSUREBINDINGS,n_closure) = eps',
        '$constant_callable_record(S.CONSTANTCLOSURES,n_closure) = eps',
        '$dynamic_runtime_object(S,n_closure)',
        '$dynamic_define_value_class(S,POBJECT n_closure) = (PVOBJECT)',
        '~$constant_value_class_valid(S,POBJECT n_closure,PVCLOSURE n_closure pconfigcall.SITE)',
        '~$global_constant_class_supported(PVOBJECT)',
        f'~$global_constant_class_supported(PVARRAY false ([(KSTRING {edge},PVOBJECT)]))',
        'S.STORE[n_owner_cv] = DEFINED PNULL',
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
        # Selection, scope, binding and certificate projections are pure and never driven.
        *controls(),
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
        'S_throw.STORE[n_cell] = DEFINED PNULL',
        'S_throw.STORE[n_owner_cv] = DEFINED PNULL',
        'S_throw.STORE[n_calls] = DEFINED (PINT 1)', 'S_throw.STORE[n_reads] = DEFINED (PINT 1)', 'S_throw.STORE[n_destroyed] = DEFINED (PINT 0)',
        'S_throw.STORE[n_result] = DEFINED pvalue_sentinel',
        'S_throw.USERCONSTANTS = S.USERCONSTANTS',
        'S_throw.ARRAYS[n_candidate] = parray_candidate',
        'S_throw.ARRAYS[n_input] = S.ARRAYS[n_input]',
        'S_throw.OBJECTS[n_closure] = pobject_closure',
        '$closure_scope_at(S_throw.CLOSURESCOPES,n_closure) = (pclosurescope)',
        '$closure_scope_row_valid(S_throw,pclosurescope)',
        'S_throw.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'pthrowable_error.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_error,"message")) = ($ptascii("V90_STOP"))',
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
        *private_values('S_throw',41,'throw'),
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
        *private_values('S_free',41,'free'),
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
        timeout = 240
    return packet_process(command, directory, timeout, cwd)


packet.process = process
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    raise SystemExit(0 if packet.main() else 1)
