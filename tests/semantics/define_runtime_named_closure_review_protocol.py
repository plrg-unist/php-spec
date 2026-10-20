#!/usr/bin/env python3
"""Rejected named Closure disposal preserves request-owned function statics."""
from pathlib import Path

import define_stdclass_array_duplicate_review_protocol as prior
import define_runtime_named_closure_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
TARGET = 'V88_REVIEW_OLD'
CASE = 'named-closure-array-discard-keeps-function-static-child'
PREFIX = define.PREFIX + r'''
dec $test_named_peer_front(pstate, nat, nat) : bool
def $test_named_peer_front(S,0,n_child) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.INDEX = 2
  -- if $named_slot_at(pconfigcall.SENT,0) = NAMED_HOLE
  -- if $named_slot_at(pconfigcall.SENT,1) = NAMED_SENT (KNOWN (PARRAY n_input))
  -- if $named_slot_at(pconfigcall.SENT,2) = NAMED_SENT (KNOWN (PBOOL false))
def $test_named_peer_front(S,1,n_child) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V88_REVIEW_OLD"),PARRAY n_input))
def $test_named_peer_front(S,2,n_child) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V88_REVIEW_OLD"),PARRAY n_input))
def $test_named_peer_front(S,3,n_child) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask_tail*
  -- if ~$test_named_peer_front(S,2,n_child)
  -- if S.DESTRUCTION.OPERATIONS = eps
def $test_named_peer_front(S,4,n_child) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OBJECT = n_child /\ ~pdestructorcall.STORE
def $test_named_peer_front(S,n_phase,n_child) = false -- otherwise
dec $test_named_peer_seek(pstate, nat, nat, nat) : pstate
def $test_named_peer_seek(S,n_phase,n_child,0) = S
def $test_named_peer_seek(S,n_phase,n_child,n) = S
  -- if $(n > 0)
  -- if $test_named_peer_front(S,n_phase,n_child) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_named_peer_seek(S,n_phase,n_child,n) = $test_named_peer_seek($drive_steps($test_running(S),1),n_phase,n_child,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_named_peer_front(S,n_phase,n_child)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase, child='0'):
    return [f'{state}_found = $test_named_peer_seek({start},{phase},{child},1500)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_named_peer_front({state},{phase},{child})']


def statics(state, count, held='POBJECT n_child'):
    return [f'{state}.STATICS = [pstaticcell_held,pstaticcell_count]',
        f'{state}.STORE[n_held] = DEFINED ({held})',
        f'{state}.STORE[n_count] = DEFINED (PINT {count})',
        f'$static_cells_valid({state},{state}.STATICS)']


def controls():
    return ['S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_closure)]',
        '$dynamic_define_value_class(S_dead,POBJECT n_closure) = eps',
        '~$dynamic_runtime_object(S,|S.OBJECTS|)',
        'S_no_function = S[.FUNCTIONS = eps]',
        '~$typed_closure(S_no_function,n_closure)',
        '~$dynamic_runtime_object(S_no_function,n_closure)',
        'S_no_map = S[.CALLABLES = eps]',
        '~$closure_live_object_valid(S_no_map,n_closure)',
        '~$dynamic_runtime_object(S_no_map,n_closure)',
        'S_unknown = S[.OBJECTS[n_closure] = NAMEDCLOSURE (PORIGIN (|S.SOURCES|) eps)]',
        '~$dynamic_runtime_object(S_unknown,n_closure)',
        'pclosurescope_bad = {OBJECT n_closure,LEXICAL porigin_function,CALLED porigin_function,RECEIVER eps,CREATION eps}',
        'S_scope = S[.CLOSURESCOPES = [pclosurescope_bad]]',
        '$typed_closure(S_scope,n_closure)',
        '~$dynamic_runtime_object(S_scope,n_closure)',
        'pclosurebinding_bad = {OBJECT n_closure,SITE pconfigcall.SITE,SOURCE n_closure,LEXICAL eps,CALLED eps,RECEIVER eps}',
        'S_binding = S[.CLOSUREBINDINGS = [pclosurebinding_bad]]',
        '$typed_closure(S_binding,n_closure)',
        '~$dynamic_runtime_object(S_binding,n_closure)',
        'S_internal = S[.OBJECTS[n_closure] = INTRINSICCLOSURE INTRINSIC_DEFINE]',
        '~$dynamic_runtime_object(S_internal,n_closure)',
        'S_wrapped = S[.OBJECTS[n_closure] = CONSTANTCLOSURE pconfigcall.SITE (NAMEDCLOSURE porigin_function)]',
        '~$dynamic_runtime_object(S_wrapped,n_closure)',
        '$dynamic_define_value_class(S_wrapped,POBJECT n_closure) = eps',
        'pconstantclosure_bad = {OBJECT n_closure,SITE pconfigcall.SITE,DECL pconfigcall.SITE,PREFIX (|S.DECLARATIONS|)}',
        'S_record = S[.CONSTANTCLOSURES = [pconstantclosure_bad]]',
        '~$dynamic_runtime_object(S_record,n_closure)',
        '$dynamic_define_value_class(S_record,POBJECT n_closure) = eps']


def checks(initial, stdout):
    warning = b'B|N|H|2|2|0|'
    before_clear = (warning + b'E|V88_STOP|none|define|false|null|dropped|defined|'
        b'17|1|0|kept|31|split|history|3|0|')
    assert stdout == before_clear + b'D|41|4|1|A|'
    edge = text('edge')
    values = [*initial, *reach('S_capture','S_initial',0), *common.public('S_capture'),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        '$named_slot_at(pconfigcall_capture.SENT,1) = NAMED_SENT (KNOWN (PARRAY n_input))',
        'pconfigcall_capture.SELECTION = (n_selection)',
        'S_capture.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        '$lookup(S_capture.ENV,$ptascii("child")) = (n_child_cv)',
        '$lookup(S_capture.ENV,$ptascii("cell")) = (n_cell)',
        '$lookup(S_capture.ENV,$ptascii("input")) = (n_input_cv)',
        '$lookup(S_capture.ENV,$ptascii("api")) = (n_api)',
        '$lookup(S_capture.ENV,$ptascii("calls")) = (n_calls)',
        '$lookup(S_capture.ENV,$ptascii("destroyed")) = (n_destroyed)',
        '$lookup(S_capture.ENV,$ptascii("result")) = (n_result)',
        'S_capture.STORE[n_child_cv] = DEFINED (POBJECT n_child)',
        'S_capture.STORE[n_cell] = DEFINED (POBJECT n_closure)',
        'S_capture.OBJECTS[n_closure] = NAMEDCLOSURE porigin_function',
        '$function_at(S_capture.FUNCTIONS,porigin_function) = (pfunction_keep)',
        'pfunction_keep.NAME = $ptascii("v88ReviewKeep")',
        '$callable_at(S_capture.CALLABLES,$ptlc(pfunction_keep.NAME)) = (porigin_function)',
        '$typed_closure(S_capture,n_closure)', '$closure_live_object_valid(S_capture,n_closure)',
        '$node_children(S_capture,HOBJECT n_closure) = eps',
        'S_capture.STATICS = [pstaticcell_held,pstaticcell_count]',
        'n_held = pstaticcell_held.CELL', 'n_count = pstaticcell_count.CELL',
        'n_held =/= n_count',
        '$static_function_entry(pfunction_keep,pstaticcell_held.ORIGIN)',
        '$static_function_entry(pfunction_keep,pstaticcell_count.ORIGIN)',
        '$static_descriptor(S_capture,pstaticcell_held.ORIGIN) = (($ptascii("held"),z_held_begin,z_held_bind,true))',
        '$static_descriptor(S_capture,pstaticcell_count.ORIGIN) = (($ptascii("count"),z_count_begin,z_count_bind,true))',
        *statics('S_capture',1),
        '$heap_owners($heap_graph(S_capture),HCELL n_held) = 1',
        '$heap_owners($heap_graph(S_capture),HCELL n_count) = 1',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_child) = 2',
        '$heap_edge_owners(HOBJECT n_child,$heap_graph(S_capture).EDGES,[HCELL n_held]) = 1',
        '$heap_edge_owners(HOBJECT n_child,$heap_graph(S_capture).EDGES,[HOBJECT n_closure]) = 0',
        'n_cell <- S_capture.REFCELLS',
        'S_capture.STORE[n_input_cv] = DEFINED (PARRAY n_input)',
        f'S_capture.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {edge}) (ALIAS n_cell)]',
        'S_capture.ARRAYS[n_input].NEXT = 91',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_closure) = 1',
        '$heap_owners($heap_graph(S_capture),HARRAY n_input) = 2',
        *define.property_value('S_capture','n_child',41,'capture'),
        *reach('S','S_capture',1), *common.public('S'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.NAMED', 'pconfigcall.SITE = pconfigcall_capture.SITE',
        'pconfigcall.SELECTION = pconfigcall_capture.SELECTION',
        '$dynamic_define_values(pconfigcall) = ((' + text(TARGET) + ',PARRAY n_input))',
        '$named_slot_at(pconfigcall.SENT,2) = NAMED_SENT (KNOWN (PBOOL false))',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        '$config_invoke_valid(S,pconfigcall)', '$dynamic_array_call_valid(S,pconfigcall)',
        'S.USERCONSTANTS = [puserconstant_old]', 'puserconstant_old.NAME = ' + text(TARGET),
        'puserconstant_old.VALUE = PINT 17', 'puserconstant_old.CLASS = PVSCALAR',
        'S.CONSTANTOBJECTS = eps', 'S.CONSTANTCLOSURES = eps',
        'S.OBJECTS[n_closure] = NAMEDCLOSURE porigin_function',
        '$typed_closure(S,n_closure)', '$closure_live_object_valid(S,n_closure)',
        '$closure_scope_at(S.CLOSURESCOPES,n_closure) = eps',
        '$closure_binding_at(S.CLOSUREBINDINGS,n_closure) = eps',
        '$dynamic_runtime_object(S,n_closure)',
        '$dynamic_define_value_class(S,POBJECT n_closure) = (PVOBJECT)',
        '~$constant_value_class_valid(S,POBJECT n_closure,PVCLOSURE n_closure pconfigcall.SITE)',
        '~$global_constant_class_supported(PVOBJECT)',
        f'~$global_constant_class_supported(PVARRAY false ([(KSTRING {edge},PVOBJECT)]))',
        *statics('S',1),
        'S.STORE[n_child_cv] = DEFINED PNULL',
        'S.STORE[n_cell] = DEFINED (POBJECT n_closure)',
        'S.STORE[n_input_cv] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        f'S.ARRAYS[n_caller].ITEMS = [ENTRY (KSTRING {edge}) (ALIAS n_cell),ENTRY (KINT 90) (DIRECT (PINT 31))]',
        'S.ARRAYS[n_input] = S_capture.ARRAYS[n_input]',
        'S.STORE[n_api] = DEFINED pvalue_api', '$string_bytes(pvalue_api) = ($ptascii("defined"))',
        'S.STORE[n_calls] = DEFINED (PINT 0)', 'S.STORE[n_destroyed] = DEFINED (PINT 0)',
        'S.STORE[n_result] = DEFINED pvalue_sentinel', '$string_bytes(pvalue_sentinel) = ($ptascii("kept"))',
        '$heap_owners($heap_graph(S),HOBJECT n_closure) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_child) = 1',
        '$heap_edge_owners(HOBJECT n_child,$heap_graph(S).EDGES,[HCELL n_held]) = 1',
        '$heap_edge_owners(HOBJECT n_child,$heap_graph(S).EDGES,[HOBJECT n_closure]) = 0',
        '$heap_owners($heap_graph(S),HARRAY n_input) = 1',
        '$dynamic_array_value(S,PARRAY n_input,eps,false) = eps',
        'n_constants = |S.USERCONSTANTS|', 'n_constants = 1',
        '$dynamic_array_duplicate_call_valid(S,pconfigcall,n_constants)',
        '~$dynamic_constant_duplicate_valid(S,pconfigcall,n_constants)',
        'n_candidate = |S.ARRAYS|', '$test_outputs(S.EVENTS) = ($ptascii("B|N|"))',
        # These malformed authority projections are pure and never driven.
        *controls(),
        *common.step('S_dispatch','S'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_dispatch*',
        'perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants',
        'perrorcall.LEVEL = 2', '$error_call_valid(S_dispatch,perrorcall)',
        'perrorcall.MESSAGE = $global_constant_duplicate_message(' + text(TARGET) + ')',
        f'parray_candidate = $array_insert($array_empty(),KSTRING {edge},DIRECT (POBJECT n_closure))',
        f'pvalueclass = PVARRAY false ([(KSTRING {edge},PVOBJECT)])',
        'S_dispatch.ARRAYS = S.ARRAYS ++ [parray_candidate]',
        'S_dispatch.OBJECTS = S.OBJECTS', 'S_dispatch.OBJECTPROPS = S.OBJECTPROPS',
        'S_dispatch.ALLOCATIONS = S.ALLOCATIONS ++ [HARRAY n_candidate]',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.STATICS = S.STATICS',
        'S_dispatch.USERCONSTANTS = S.USERCONSTANTS', 'S_dispatch.EVENTS = S.EVENTS',
        '$dynamic_array_value(S_dispatch,PARRAY n_candidate,eps,false) = ((S_dispatch,PARRAY n_candidate,pvalueclass))',
        '$dynamic_global_constant_array_tree(S_dispatch,PARRAY n_candidate,pvalueclass)',
        '$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_candidate,pvalueclass,n_constants)',
        '$task_nodes(perrorcall.RESUME) = [HARRAY n_candidate,HARRAY n_input]',
        '$heap_owners($heap_graph(S_dispatch),HARRAY n_candidate) = 1',
        '$heap_owners($heap_graph(S_dispatch),HOBJECT n_closure) = 2',
        '$heap_owners($heap_graph(S_dispatch),HOBJECT n_child) = 1',
        '$heap_edge_owners(HOBJECT n_closure,$heap_graph(S_dispatch).EDGES,[HARRAY n_candidate]) = 1',
        '$heap_edge_owners(HOBJECT n_child,$heap_graph(S_dispatch).EDGES,[HOBJECT n_closure,HARRAY n_candidate]) = 0',
        *reach('S_throw','S_dispatch',2), *common.public('S_throw'),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_done) :: ptask_after*',
        'perrorcall_done.RESUME = perrorcall.RESUME',
        '$dynamic_array_duplicate_valid(S_throw,pconfigcall,n_candidate,pvalueclass,n_constants)',
        'S_throw.STORE[n_cell] = DEFINED PNULL', 'S_throw.STORE[n_child_cv] = DEFINED PNULL',
        'S_throw.STORE[n_calls] = DEFINED (PINT 1)', 'S_throw.STORE[n_destroyed] = DEFINED (PINT 0)',
        'S_throw.STORE[n_result] = DEFINED pvalue_sentinel',
        *statics('S_throw',2),
        'S_throw.USERCONSTANTS = S.USERCONSTANTS',
        'S_throw.ARRAYS[n_candidate] = parray_candidate',
        'S_throw.ARRAYS[n_input] = S.ARRAYS[n_input]',
        'S_throw.OBJECTS[n_closure] = NAMEDCLOSURE porigin_function',
        '$node_children(S_throw,HOBJECT n_closure) = eps',
        'S_throw.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'pthrowable_error.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_error,"message")) = ($ptascii("V88_STOP"))',
        '$throwable_field(S_throw,n_error,"previous") = PNULL',
        '$throwable_chain_valid(S_throw,n_error)',
        '$throwable_field(S_throw,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_throw.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_throw,n_frame,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_throw,n_frame,$ptascii("args")) = PARRAY n_args',
        '$entry_lookup(S_throw.ARRAYS[n_args].ITEMS,KINT 1) = (DIRECT (PARRAY n_input))',
        '$entry_lookup(S_throw.ARRAYS[n_args].ITEMS,KINT 2) = (DIRECT (PBOOL false))',
        '$heap_owners($heap_graph(S_throw),HOBJECT n_closure) = 1',
        '$heap_owners($heap_graph(S_throw),HOBJECT n_child) = 1',
        '$heap_edge_owners(HOBJECT n_child,$heap_graph(S_throw).EDGES,[HCELL n_held]) = 1',
        '$heap_edge_owners(HOBJECT n_child,$heap_graph(S_throw).EDGES,[HOBJECT n_closure]) = 0',
        '$heap_owners($heap_graph(S_throw),HARRAY n_candidate) = 1',
        '$heap_owners($heap_graph(S_throw),HARRAY n_input) = 2',
        '$heap_edge_owners(HOBJECT n_closure,$heap_graph(S_throw).EDGES,[HARRAY n_candidate]) = 1',
        '$heap_edge_owners(HARRAY n_input,$heap_graph(S_throw).EDGES,[HARRAY n_args]) = 1',
        '~(n_child <- S_throw.DESTRUCTION.CALLED)',
        '$test_outputs(S_throw.EVENTS) = ' + term(warning),
        # Genuine marker disposal frees the private array and bare fake Closure.
        'S_pause = $drive_steps(S_throw,0)', 'S_pause = S_throw[.COMPLETION = BUDGET]',
        'S_resume = $test_running(S_pause)', 'S_resume = S_throw',
        *common.step('S_drop','S_resume'),
        *reach('S_after','S_drop',3), *common.public('S_after'),
        'S_after.TODO = (THROW_SEARCH n_error) :: ptask_after*',
        'S_after.USERCONSTANTS = S.USERCONSTANTS',
        'S_after.ERRORHANDLER.CALLBACK = (perrorcall_done.CALLBACK)',
        'S_after.STORE[n_result] = DEFINED pvalue_sentinel',
        'S_after.STORE[n_destroyed] = DEFINED (PINT 0)',
        'S_after.OBJECTS[n_error] = THROWABLE pthrowable_error',
        '$throwable_field(S_after,n_error,"previous") = PNULL',
        *statics('S_after',2),
        '$heap_owners($heap_graph(S_after),HARRAY n_input) = 1',
        '$heap_edge_owners(HARRAY n_input,$heap_graph(S_after).EDGES,[HARRAY n_args]) = 1',
        '~(HOBJECT n_closure <- S_after.ALLOCATIONS)', '~(HARRAY n_candidate <- S_after.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_after),HOBJECT n_child) = 1',
        '$heap_edge_owners(HOBJECT n_child,$heap_graph(S_after).EDGES,[HCELL n_held]) = 1',
        '$heap_owners($heap_graph(S_after),HCELL n_held) = 1',
        '$heap_owners($heap_graph(S_after),HCELL n_count) = 1',
        '~(n_child <- S_after.DESTRUCTION.CALLED)',
        '$test_outputs(S_after.EVENTS) = ' + term(warning),
        # Only the later direct function clear removes the request-static edge.
        *reach('S_free','S_after',4,'n_child'), *common.public('S_free'),
        'S_free.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_free*',
        'pdestructorcall.OBJECT = n_child', '~pdestructorcall.STORE',
        'pdestructorcall.PENDING = eps', '$destructor_enter_valid(S_free,pdestructorcall)',
        'S_free.CURRENT = (pcallcontext_keep)',
        'pcallcontext_keep.FUNCTION = porigin_function', 'pcallcontext_keep.INSTANCE = eps',
        'S_free.STORE[n_destroyed] = DEFINED (PINT 0)',
        *statics('S_free',4,'PNULL'),
        '~(HOBJECT n_closure <- S_free.ALLOCATIONS)', '~(HARRAY n_candidate <- S_free.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_free.ALLOCATIONS)',
        '$heap_edge_owners(HOBJECT n_child,$heap_graph(S_free).EDGES,[HCELL n_held]) = 0',
        '$heap_owners($heap_graph(S_free),HOBJECT n_child) = 2',
        'n_child <- S_free.DESTRUCTION.CALLED',
        *define.property_value('S_free','n_child',41,'free'),
        '$test_outputs(S_free.EVENTS) = ' + term(before_clear),
        *define.finish('S_free',stdout),
        'S_final.USERCONSTANTS = S.USERCONSTANTS',
        *statics('S_final',4,'PNULL'),
        '$heap_owners($heap_graph(S_final),HCELL n_held) = 1',
        '$heap_owners($heap_graph(S_final),HCELL n_count) = 1',
        'n_child <- S_final.DESTRUCTION.CALLED',
        '~(HOBJECT n_child <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_closure <- S_final.ALLOCATIONS)', '~(HARRAY n_candidate <- S_final.ALLOCATIONS)',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)', '~(HARRAY n_caller <- S_final.ALLOCATIONS)',
        '~(HCELL n_cell <- S_final.ALLOCATIONS)', '~(HOBJECT n_error <- S_final.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_final.ALLOCATIONS)', '~(HARRAY n_frame <- S_final.ALLOCATIONS)',
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
