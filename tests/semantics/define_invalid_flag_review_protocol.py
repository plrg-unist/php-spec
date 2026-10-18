#!/usr/bin/env python3
"""Rejected ordinary object flag, trace-only lifetime and genuine free callback."""
from pathlib import Path

import define_certified_instance_protocol as instance
import define_stdclass_array_duplicate_protocol as prior
import define_invalid_flag_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
TARGET = 'V81_REVIEW_TARGET'
PREFIX = instance.PREFIX + r'''
dec $test_invalid_flag_peer_front(pstate, nat, nat) : bool
def $test_invalid_flag_peer_front(S,0,n_object) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.INDEX = 2
  -- if $named_slot_at(pconfigcall.SENT,1) = NAMED_SENT (KNOWN (POBJECT n_value))
  -- if $named_slot_at(pconfigcall.SENT,2) = NAMED_SENT (KNOWN (POBJECT n_flag))
def $test_invalid_flag_peer_front(S,1,n_object) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_define_invalid_flag_values(pconfigcall) = (($ptascii("V81_REVIEW_TARGET"),POBJECT n_value,POBJECT n_flag))
def $test_invalid_flag_peer_front(S,2,n_object) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_slot) metadata_slot) :: expression_tail*
  -- if $base64(text_slot) = $ptascii("slot")
def $test_invalid_flag_peer_front(S,3,n_object) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_error) metadata_error) :: expression_tail*
  -- if $base64(text_error) = $ptascii("error")
def $test_invalid_flag_peer_front(S,4,n_object) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OBJECT = n_object /\ ~pdestructorcall.STORE
def $test_invalid_flag_peer_front(S,5,n_object) = true
  -- if S.TODO = (THROW_SEARCH n_object) :: ptask_tail*
  -- if S.OBJECTS[n_object] = THROWABLE pthrowable
  -- if pthrowable.KIND = "TypeError"
def $test_invalid_flag_peer_front(S,n_phase,n_object) = false -- otherwise
dec $test_invalid_flag_peer_seek(pstate, nat, nat, nat) : pstate
def $test_invalid_flag_peer_seek(S,n_phase,n_object,0) = S
def $test_invalid_flag_peer_seek(S,n_phase,n_object,n) = S
  -- if $(n > 0)
  -- if $test_invalid_flag_peer_front(S,n_phase,n_object) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_invalid_flag_peer_seek(S,n_phase,n_object,n) = $test_invalid_flag_peer_seek($drive_steps($test_running(S),1),n_phase,n_object,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_invalid_flag_peer_front(S,n_phase,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase, obj='0'):
    return [f'{state}_found = $test_invalid_flag_peer_seek({start},{phase},{obj},500)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_invalid_flag_peer_front({state},{phase},{obj})']


def checks(initial, name, stdout):
    kept = (b'B|N|E|define(): Argument #3 ($case_insensitive) must be of type bool, '
        b'V81ReviewFlag given|define|none|left|right|false|41|53|31|0|kept|absent|kept-trace|')
    before = kept + b'F|53|released|A|'
    assert stdout == before + b'D|31|D|23|'
    values = [*initial, *reach('S_capture','S_initial',0),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        '$named_slot_at(pconfigcall_capture.SENT,0) = NAMED_HOLE',
        '$named_slot_at(pconfigcall_capture.SENT,1) = NAMED_SENT (KNOWN (POBJECT n_left))',
        '$named_slot_at(pconfigcall_capture.SENT,2) = NAMED_SENT (KNOWN (POBJECT n_flag))',
        'pconfigcall_capture.SELECTION = (n_selection)',
        'S_capture.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        '$lookup(S_capture.ENV,$ptascii("candidate")) = (n_candidate)',
        '$lookup(S_capture.ENV,$ptascii("flag")) = (n_flag_cv)',
        '$lookup(S_capture.ENV,$ptascii("api")) = (n_api)',
        '$lookup(S_capture.ENV,$ptascii("calls")) = (n_calls)',
        '$lookup(S_capture.ENV,$ptascii("result")) = (n_result)',
        'S_capture.STORE[n_candidate] = DEFINED (POBJECT n_left)',
        'S_capture.STORE[n_flag_cv] = DEFINED (POBJECT n_flag)',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_left) = 3',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_flag) = 2',
        *instance.property_value('S_capture','n_flag',7,'flag_capture'),
        *reach('S','S_capture',1), *common.public('S'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.SITE = pconfigcall_capture.SITE', 'pconfigcall.NAMED',
        'pconfigcall.SELECTION = pconfigcall_capture.SELECTION',
        '$dynamic_define_invalid_flag_values(pconfigcall) = ((' + text(TARGET) + ',POBJECT n_left,POBJECT n_flag))',
        '$dynamic_define_invalid_flag_valid(S,pconfigcall)', '~$config_strict(S,pconfigcall)',
        '$task_nodes(CONFIG_INVOKE pconfigcall) = [HOBJECT n_left,HOBJECT n_flag]',
        *instance.certified('S','n_left','V81_REVIEW_LEFT','left'),
        *instance.certified('S','n_right','V81_REVIEW_RIGHT','right'),
        'S.USERCONSTANTS = [puserconstant_left,puserconstant_right]',
        'n_flag =/= n_left', 'n_flag =/= n_right',
        'S.OBJECTS[n_flag] = INSTANCE porigin_flag',
        '$class_at(S.CLASSES,porigin_flag) = (pclassdesc_flag)',
        'pclassdesc_flag.NAME = ($ptascii("V81ReviewFlag"))',
        '$global_new_record(S.CONSTANTOBJECTS,n_flag) = eps',
        '$dynamic_define_value_class(S,POBJECT n_flag) = eps',
        '$dynamic_define_invalid_flag_kind(S,POBJECT n_flag)',
        *instance.property_value('S','n_flag',41,'flag_rebound'),
        'S.STORE[n_candidate] = DEFINED (POBJECT n_right)',
        'S.STORE[n_flag_cv] = DEFINED (PBOOL false)',
        'S.STORE[n_api] = DEFINED pvalue_api',
        '$string_bytes(pvalue_api) = ($ptascii("defined"))',
        'S.STORE[n_calls] = DEFINED (PINT 0)',
        'S.STORE[n_result] = DEFINED pvalue_sentinel',
        '$string_bytes(pvalue_sentinel) = ($ptascii("kept"))',
        '$source_constant_lookup(S,' + text(TARGET) + ') = eps',
        '$heap_owners($heap_graph(S),HOBJECT n_left) = 2',
        '$heap_owners($heap_graph(S),HOBJECT n_flag) = 1',
        # Pure controls authenticate rejection without granting a publication class.
        'pconfigcall_unpublished_value = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,1,KNOWN (POBJECT n_flag))]',
        '$dynamic_define_invalid_flag_valid(S,pconfigcall_unpublished_value)',
        '~$dynamic_define_invalid_flag_valid(S,pconfigcall[.SELECTION = eps])',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_flag)]',
        '~$dynamic_define_invalid_flag_valid(S_dead,pconfigcall)',
        'S_internal = S[.OBJECTS[n_flag] = INTRINSICCLOSURE INTRINSIC_DEFINE]',
        '$dynamic_define_invalid_flag_kind(S_internal,POBJECT n_flag)',
        '$dynamic_define_invalid_flag_valid(S_internal,pconfigcall)',
        'n_arrays = |S.ARRAYS|', 'n_error = |S.OBJECTS|',
        *common.step('S_dispatch','S'),
        *reach('S_error','S_dispatch',5,'n_error'), *common.public('S_error'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'S_error.OBJECTS = S.OBJECTS ++ [THROWABLE pthrowable_error]',
        'pthrowable_error.KIND = "TypeError"',
        'pthrowable_error.ORIGIN = (pconfigcall.SITE)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = ($ptascii("define(): Argument #3 ($case_insensitive) must be of type bool, V81ReviewFlag given"))',
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
        '$heap_owners($heap_graph(S_error),HOBJECT n_left) = 2',
        '$heap_owners($heap_graph(S_error),HOBJECT n_flag) = 1',
        '$heap_edge_owners(HOBJECT n_flag,$heap_graph(S_error).EDGES,[HARRAY n_args]) = 1',
        '~(n_flag <- S_error.DESTRUCTION.CALLED)']
    values += [f'S_error.{field} = S.{field}' for field in
        ['STORE','ENV','USERCONSTANTS','CONSTANTOBJECTS','CONSTANTSTDOBJECTS','EVENTS','ERRORHANDLER']]
    values += [
        'S_error.OBJECTPROPS = S.OBJECTPROPS ++ [{OBJECT n_error,SLOTS $throwable_slots("TypeError",$ptascii("define(): Argument #3 ($case_insensitive) must be of type bool, V81ReviewFlag given"),$call_sourcefile(S.FILES,pconfigcall.SITE),pconfigcall.LINE,n_trace,PNULL),MATERIALIZED false}]',
        'S_error.OBJECTTABLES = S.OBJECTTABLES', 'S_error.PROPREFS = S.PROPREFS',
        *reach('S_reference','S_error',2),
        '$lookup(S_reference.ENV,$ptascii("slot")) = (n_slot)',
        'n_slot <- S_reference.REFCELLS', 'HCELL n_slot <- S_reference.ALLOCATIONS',
        'S_reference.STORE[n_slot] = DEFINED (PINT 53)',
        *instance.property_value('S_reference','n_flag',53,'flag_reference'),
        'ppropertyslot_flag_reference.STATE = PROP_VALUE (ALIAS n_slot)',
        *reach('S_kept','S_reference',3),
        '$test_outputs(S_kept.EVENTS) = ' + term(kept),
        '$lookup(S_kept.ENV,$ptascii("error")) = (n_error_cv)',
        'S_kept.STORE[n_error_cv] = DEFINED (POBJECT n_error)',
        '$heap_owners($heap_graph(S_kept),HOBJECT n_error) = 1',
        '$heap_owners($heap_graph(S_kept),HOBJECT n_flag) = 1',
        '$heap_edge_owners(HOBJECT n_flag,$heap_graph(S_kept).EDGES,[HARRAY n_args]) = 1',
        '$heap_owners($heap_graph(S_kept),HOBJECT n_left) = 2',
        *instance.property_value('S_kept','n_left',31,'left_kept'),
        *instance.property_value('S_kept','n_flag',53,'flag_kept'),
        'S_kept.USERCONSTANTS = S.USERCONSTANTS', '~(n_flag <- S_kept.DESTRUCTION.CALLED)',
        *reach('S_free','S_kept',4,'n_flag'), *common.public('S_free'),
        'S_free.TODO = (DESTRUCTOR_ENTER pdestructorcall_flag) :: ptask_free*',
        'pdestructorcall_flag.OBJECT = n_flag', '~pdestructorcall_flag.STORE',
        'pdestructorcall_flag.RELEASE = (pdestructionrelease_flag)',
        'pdestructorcall_flag.PENDING = eps', '$destructor_enter_valid(S_free,pdestructorcall_flag)',
        '$task_nodes(DESTRUCTOR_ENTER pdestructorcall_flag) = [HOBJECT n_flag,HOBJECT n_flag]',
        '$heap_owners($heap_graph(S_free),HOBJECT n_flag) = 2',
        '$heap_edge_owners(HOBJECT n_flag,$heap_graph(S_free).EDGES,[HARRAY n_args]) = 0',
        '$test_outputs(S_free.EVENTS) = ' + term(kept),
        *instance.property_value('S_free','n_flag',53,'flag_free'),
        *instance.store('S_store_left','S_free','n_left',1,before),
        '~(HOBJECT n_flag <- S_store_left.ALLOCATIONS)',
        '~(HCELL n_slot <- S_store_left.ALLOCATIONS)', 'n_flag <- S_store_left.DESTRUCTION.CALLED',
        '~(HOBJECT n_error <- S_store_left.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_store_left.ALLOCATIONS)', '~(HARRAY n_args <- S_store_left.ALLOCATIONS)',
        '~(HARRAY n_frame <- S_store_left.ALLOCATIONS)',
        'S_store_left.USERCONSTANTS = S.USERCONSTANTS',
        *instance.store('S_store_right','S_store_left_selected','n_right',1,before + b'D|31|'),
        *define.finish('S_store_right_selected',stdout),
        'S_final.USERCONSTANTS = S.USERCONSTANTS',
        'S_final.CONSTANTOBJECTS = S.CONSTANTOBJECTS',
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 1',
        '$heap_owners($heap_graph(S_final),HOBJECT n_right) = 1',
        'n_left <- S_final.DESTRUCTION.CALLED', 'n_right <- S_final.DESTRUCTION.CALLED',
        '~(HOBJECT n_flag <- S_final.ALLOCATIONS)']
    return values


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = packet.process


def process(command, directory, timeout, cwd):
    if directory.parent.name == 'object-flag-trace-retains-unpinned-instance':
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
