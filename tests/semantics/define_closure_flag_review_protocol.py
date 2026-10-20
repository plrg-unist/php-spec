#!/usr/bin/env python3
"""Rejected method Closure retains its receiver through the original Error trace."""
from pathlib import Path

import define_certified_instance_protocol as instance
import define_stdclass_array_duplicate_protocol as prior
import define_closure_flag_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
TARGET = 'V82_REVIEW_TARGET'
PREFIX = define.PREFIX + r'''
dec $test_closure_flag_peer_front(pstate, nat, nat) : bool
def $test_closure_flag_peer_front(S,0,n_object) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.INDEX = 2
  -- if $named_slot_at(pconfigcall.SENT,1) = NAMED_SENT (KNOWN (POBJECT n_value))
  -- if $named_slot_at(pconfigcall.SENT,2) = NAMED_SENT (KNOWN (POBJECT n_flag))
def $test_closure_flag_peer_front(S,1,n_object) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_define_invalid_flag_values(pconfigcall) = (($ptascii("V82_REVIEW_TARGET"),POBJECT n_value,POBJECT n_flag))
def $test_closure_flag_peer_front(S,2,n_object) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_raw) metadata_raw) :: expression_tail*
  -- if $base64(text_raw) = $ptascii("raw")
def $test_closure_flag_peer_front(S,3,n_object) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_error) metadata_error) :: expression_tail*
  -- if $base64(text_error) = $ptascii("error")
def $test_closure_flag_peer_front(S,4,n_object) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OBJECT = n_object /\ ~pdestructorcall.STORE
def $test_closure_flag_peer_front(S,5,n_object) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NScalarString (BYTES text_released) metadata_released) :: expression_tail*
  -- if $base64(text_released) = $ptascii("released|")
def $test_closure_flag_peer_front(S,6,n_object) = true
  -- if S.TODO = (THROW_SEARCH n_object) :: ptask_tail*
  -- if S.OBJECTS[n_object] = THROWABLE pthrowable
  -- if pthrowable.KIND = "TypeError"
def $test_closure_flag_peer_front(S,n_phase,n_object) = false -- otherwise
dec $test_closure_flag_peer_seek(pstate, nat, nat, nat) : pstate
def $test_closure_flag_peer_seek(S,n_phase,n_object,0) = S
def $test_closure_flag_peer_seek(S,n_phase,n_object,n) = S
  -- if $(n > 0)
  -- if $test_closure_flag_peer_front(S,n_phase,n_object) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_closure_flag_peer_seek(S,n_phase,n_object,n) = $test_closure_flag_peer_seek($drive_steps($test_running(S),1),n_phase,n_object,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_closure_flag_peer_front(S,n_phase,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase, obj='0'):
    return [f'{state}_found = $test_closure_flag_peer_seek({start},{phase},{obj},1000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_closure_flag_peer_front({state},{phase},{obj})']


def checks(initial, name, stdout):
    recovered = (b'B|N|E|define(): Argument #3 ($case_insensitive) must be of type bool, '
        b'Closure given|define|none|left|right|false|null|defined|0|0|kept|absent|C|41|1|')
    kept = recovered + b'kept-trace|'
    assert stdout == kept + b'D|41|released|A|'
    values = [*initial, *reach('S_capture','S_initial',0),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        '$named_slot_at(pconfigcall_capture.SENT,0) = NAMED_HOLE',
        '$named_slot_at(pconfigcall_capture.SENT,1) = NAMED_SENT (KNOWN (POBJECT n_left))',
        '$named_slot_at(pconfigcall_capture.SENT,2) = NAMED_SENT (KNOWN (POBJECT n_flag))',
        'pconfigcall_capture.SELECTION = (n_selection)',
        'S_capture.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        '$closure_scope_at(S_capture.CLOSURESCOPES,n_flag) = (pclosurescope_flag)',
        'pclosurescope_flag.RECEIVER = (n_owner)',
        '$lookup(S_capture.ENV,$ptascii("candidate")) = (n_candidate)',
        '$lookup(S_capture.ENV,$ptascii("owner")) = (n_owner_cv)',
        '$lookup(S_capture.ENV,$ptascii("flag")) = (n_flag_cv)',
        '$lookup(S_capture.ENV,$ptascii("api")) = (n_api)',
        '$lookup(S_capture.ENV,$ptascii("reads")) = (n_reads)',
        '$lookup(S_capture.ENV,$ptascii("warnings")) = (n_warnings)',
        '$lookup(S_capture.ENV,$ptascii("result")) = (n_result)',
        'S_capture.STORE[n_candidate] = DEFINED (POBJECT n_left)',
        'S_capture.STORE[n_flag_cv] = DEFINED (POBJECT n_flag)',
        'S_capture.STORE[n_owner_cv] = DEFINED (POBJECT n_owner)',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_flag) = 2',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_owner) = 2',
        '$heap_edge_owners(HOBJECT n_owner,$heap_graph(S_capture).EDGES,[HOBJECT n_flag]) = 1',
        *reach('S','S_capture',1), *common.public('S'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.SITE = pconfigcall_capture.SITE', 'pconfigcall.NAMED',
        'pconfigcall.SELECTION = pconfigcall_capture.SELECTION',
        '$dynamic_define_invalid_flag_values(pconfigcall) = ((' + text(TARGET) + ',POBJECT n_left,POBJECT n_flag))',
        '$dynamic_define_invalid_flag_valid(S,pconfigcall)', '~$config_strict(S,pconfigcall)',
        '$typed_closure(S,n_flag)', '$typed_given(S,POBJECT n_flag) = ($ptascii("Closure"))',
        '$dynamic_define_invalid_flag_kind(S,POBJECT n_flag)',
        '$object_body(S.OBJECTS[n_flag]) = METHODCLOSURE porigin_method porigin_site porigin_requested pmethodcapture?',
        '$closure_scope_at(S.CLOSURESCOPES,n_flag) = (pclosurescope_flag)',
        '$closure_scope_roots(S.CLOSURESCOPES,n_flag) = [HOBJECT n_owner]',
        '$global_new_record(S.CONSTANTOBJECTS,n_owner) = eps',
        '$dynamic_define_value_class(S,POBJECT n_owner) = (PVOBJECT)',
        '$dynamic_define_value_class(S,POBJECT n_flag) = (PVOBJECT)',
        '$user_constant_at(S.USERCONSTANTS,$ptascii("V82_REVIEW_LEFT")) = (puserconstant_left)',
        '$user_constant_at(S.USERCONSTANTS,$ptascii("V82_REVIEW_RIGHT")) = (puserconstant_right)',
        'puserconstant_left.VALUE = POBJECT n_left', 'puserconstant_right.VALUE = POBJECT n_right',
        'S.USERCONSTANTS = [puserconstant_left,puserconstant_right]',
        'S.STORE[n_candidate] = DEFINED (POBJECT n_right)',
        'S.STORE[n_flag_cv] = DEFINED (PBOOL false)', 'S.STORE[n_owner_cv] = DEFINED PNULL',
        'S.STORE[n_api] = DEFINED pvalue_api', '$string_bytes(pvalue_api) = ($ptascii("defined"))',
        'S.STORE[n_reads] = DEFINED (PINT 0)', 'S.STORE[n_warnings] = DEFINED (PINT 0)',
        'S.STORE[n_result] = DEFINED pvalue_sentinel', '$string_bytes(pvalue_sentinel) = ($ptascii("kept"))',
        *instance.property_value('S','n_owner',41,'owner_before'),
        '$source_constant_lookup(S,' + text(TARGET) + ') = eps',
        '$heap_owners($heap_graph(S),HOBJECT n_flag) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_owner) = 1',
        '$heap_edge_owners(HOBJECT n_owner,$heap_graph(S).EDGES,[HOBJECT n_flag]) = 1',
        # Pure lifetime/source controls are never driven.
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_flag)]',
        '~$typed_closure(S_dead,n_flag)', '~$dynamic_define_invalid_flag_valid(S_dead,pconfigcall)',
        'S_without_scope = S[.CLOSURESCOPES = eps]',
        '~$typed_closure(S_without_scope,n_flag)',
        '~$dynamic_define_invalid_flag_valid(S_without_scope,pconfigcall)',
        '~$dynamic_define_invalid_flag_valid(S,pconfigcall[.SELECTION = eps])',
        'pconfigcall_unpublished_value = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,1,KNOWN (POBJECT n_owner))]',
        '$dynamic_define_invalid_flag_valid(S,pconfigcall_unpublished_value)',
        'n_arrays = |S.ARRAYS|', 'n_error = |S.OBJECTS|',
        *common.step('S_dispatch','S'), *reach('S_error','S_dispatch',6,'n_error'), *common.public('S_error'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'S_error.OBJECTS = S.OBJECTS ++ [THROWABLE pthrowable_error]',
        'pthrowable_error.KIND = "TypeError"', 'pthrowable_error.ORIGIN = (pconfigcall.SITE)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = ($ptascii("define(): Argument #3 ($case_insensitive) must be of type bool, Closure given"))',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"line") = PINT pconfigcall.LINE',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_error.ARRAYS[n_trace].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_error,n_frame,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_error,n_frame,$ptascii("args")) = PARRAY n_args',
        '$entry_lookup(S_error.ARRAYS[n_args].ITEMS,KINT 1) = (DIRECT (POBJECT n_left))',
        '$entry_lookup(S_error.ARRAYS[n_args].ITEMS,KINT 2) = (DIRECT (POBJECT n_flag))',
        'n_trace = n_arrays', 'n_args = $(n_arrays + 1)', 'n_frame = $(n_arrays + 2)',
        'S_error.ARRAYS = S.ARRAYS ++ [S_error.ARRAYS[n_trace],S_error.ARRAYS[n_args],S_error.ARRAYS[n_frame]]',
        'S_error.OBJECTPROPS = S.OBJECTPROPS ++ [{OBJECT n_error,SLOTS $throwable_slots("TypeError",$ptascii("define(): Argument #3 ($case_insensitive) must be of type bool, Closure given"),$call_sourcefile(S.FILES,pconfigcall.SITE),pconfigcall.LINE,n_trace,PNULL),MATERIALIZED false}]',
        '$heap_owners($heap_graph(S_error),HOBJECT n_flag) = 1',
        '$heap_owners($heap_graph(S_error),HOBJECT n_owner) = 1',
        '$heap_edge_owners(HOBJECT n_flag,$heap_graph(S_error).EDGES,[HARRAY n_args]) = 1',
        '$heap_edge_owners(HOBJECT n_owner,$heap_graph(S_error).EDGES,[HOBJECT n_flag]) = 1',
        '~(n_owner <- S_error.DESTRUCTION.CALLED)']
    values += [f'S_error.{field} = S.{field}' for field in
        ['STORE','ENV','USERCONSTANTS','CONSTANTOBJECTS','CONSTANTSTDOBJECTS','EVENTS','ERRORHANDLER','OBJECTTABLES','PROPREFS','CLOSURESCOPES']]
    values += [*reach('S_recovered','S_error',2),
        '$test_outputs(S_recovered.EVENTS) = ' + term(recovered),
        'S_recovered.STORE[n_reads] = DEFINED (PINT 1)',
        'S_recovered.STORE[n_warnings] = DEFINED (PINT 0)',
        '$closure_scope_at(S_recovered.CLOSURESCOPES,n_flag) = (pclosurescope_flag)',
        'S_recovered.OBJECTS[n_flag] = S.OBJECTS[n_flag]',
        '$heap_owners($heap_graph(S_recovered),HOBJECT n_flag) = 2',
        '$heap_owners($heap_graph(S_recovered),HOBJECT n_owner) = 1',
        *reach('S_kept','S_recovered',3), *common.public('S_kept'),
        '$test_outputs(S_kept.EVENTS) = ' + term(kept),
        '$lookup(S_kept.ENV,$ptascii("error")) = (n_error_cv)',
        'S_kept.STORE[n_error_cv] = DEFINED (POBJECT n_error)',
        '$heap_owners($heap_graph(S_kept),HOBJECT n_error) = 1',
        '$heap_owners($heap_graph(S_kept),HOBJECT n_flag) = 1',
        '$heap_owners($heap_graph(S_kept),HOBJECT n_owner) = 1',
        '$heap_edge_owners(HOBJECT n_flag,$heap_graph(S_kept).EDGES,[HARRAY n_args]) = 1',
        '$heap_edge_owners(HOBJECT n_owner,$heap_graph(S_kept).EDGES,[HOBJECT n_flag]) = 1',
        '~(n_owner <- S_kept.DESTRUCTION.CALLED)',
        *reach('S_free','S_kept',4,'n_owner'), *common.public('S_free'),
        'S_free.TODO = (DESTRUCTOR_ENTER pdestructorcall_owner) :: ptask_free*',
        'pdestructorcall_owner.OBJECT = n_owner', '~pdestructorcall_owner.STORE',
        'pdestructorcall_owner.RELEASE = (pdestructionrelease_owner)',
        'pdestructorcall_owner.PENDING = eps', '$destructor_enter_valid(S_free,pdestructorcall_owner)',
        '$heap_owners($heap_graph(S_free),HOBJECT n_owner) = 2',
        '~(HOBJECT n_flag <- S_free.ALLOCATIONS)',
        '$heap_edge_owners(HOBJECT n_owner,$heap_graph(S_free).EDGES,[HOBJECT n_flag]) = 0',
        '$test_outputs(S_free.EVENTS) = ' + term(kept),
        *instance.property_value('S_free','n_owner',41,'owner_free'),
        *reach('S_released','S_free',5),
        '$test_outputs(S_released.EVENTS) = ' + term(kept + b'D|41|'),
        '~(HOBJECT n_owner <- S_released.ALLOCATIONS)', 'n_owner <- S_released.DESTRUCTION.CALLED',
        '~(HOBJECT n_flag <- S_released.ALLOCATIONS)', '~(HOBJECT n_error <- S_released.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_released.ALLOCATIONS)', '~(HARRAY n_args <- S_released.ALLOCATIONS)',
        '~(HARRAY n_frame <- S_released.ALLOCATIONS)',
        'S_released.USERCONSTANTS = S.USERCONSTANTS',
        'S_released.STORE[n_reads] = DEFINED (PINT 1)',
        'S_released.STORE[n_warnings] = DEFINED (PINT 0)',
        *define.finish('S_released',stdout),
        'S_final.USERCONSTANTS = S.USERCONSTANTS',
        'S_final.CONSTANTSTDOBJECTS = S.CONSTANTSTDOBJECTS',
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 1',
        '$heap_owners($heap_graph(S_final),HOBJECT n_right) = 1',
        '~(HOBJECT n_flag <- S_final.ALLOCATIONS)', '~(HOBJECT n_owner <- S_final.ALLOCATIONS)']
    return values


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = packet.process


def process(command, directory, timeout, cwd):
    if directory.parent.name == 'method-closure-flag-retains-unpinned-receiver':
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
