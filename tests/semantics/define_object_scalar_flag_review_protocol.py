#!/usr/bin/env python3
"""Reached raw flag capture, pending object publication and typed sharing."""
from pathlib import Path

import define_certified_instance_protocol as instance
import define_stdclass_array_duplicate_protocol as prior
import define_object_scalar_flag_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
TARGET = 'V80_REVIEW_TARGET'
PREFIX = instance.PREFIX + r'''
dec $test_object_scalar_peer_front(pstate, nat) : bool
def $test_object_scalar_peer_front(S,0) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.INDEX = 2
  -- if $named_slot_at(pconfigcall.SENT,1) = NAMED_SENT (KNOWN (POBJECT n_object))
  -- if $named_slot_at(pconfigcall.SENT,2) = NAMED_SENT (KNOWN pvalue_flag)
  -- if $string_bytes(pvalue_flag) = ($ptascii("false"))
def $test_object_scalar_peer_front(S,1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_scalar_define_flag_values(pconfigcall) = (($ptascii("V80_REVIEW_TARGET"),POBJECT n_object,pvalue_flag))
def $test_object_scalar_peer_front(S,2) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall
  -- if $dynamic_scalar_define_flag_values(pconfigcall) = (($ptascii("V80_REVIEW_TARGET"),POBJECT n_object,pvalue_flag))
def $test_object_scalar_peer_front(S,3) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask_tail*
def $test_object_scalar_peer_front(S,4) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata_unset)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_slot) metadata_variable) :: expression_tail*
  -- if $base64(text_slot) = $ptascii("slot")
def $test_object_scalar_peer_front(S,n_phase) = false -- otherwise
dec $test_object_scalar_peer_seek(pstate, nat, nat) : pstate
def $test_object_scalar_peer_seek(S,n_phase,0) = S
def $test_object_scalar_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_object_scalar_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_object_scalar_peer_seek(S,n_phase,n) = $test_object_scalar_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_object_scalar_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_object_scalar_peer_seek({start},{phase},500)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_object_scalar_peer_front({state},{phase})']


def checks(initial, name, stdout):
    suffix = b'D|53|D|23|'
    assert stdout == b'B|N|H|2|zero|R|absent|E|V80_PENDING|none|define|raw|left|defined|same|53|kept|1|A|' + suffix
    before = stdout[:-len(suffix)]
    values = [*initial, *reach('S_capture','S_initial',0), *common.public('S_capture'),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        'pconfigcall_capture.INDEX = 2', 'pconfigcall_capture.SELECTION = (n_selection)',
        'S_capture.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        '$named_slot_at(pconfigcall_capture.SENT,0) = NAMED_HOLE',
        '$named_slot_at(pconfigcall_capture.SENT,1) = NAMED_SENT (KNOWN (POBJECT n_object))',
        '$named_slot_at(pconfigcall_capture.SENT,2) = NAMED_SENT (KNOWN pvalue_flag)',
        'pvalue_flag = PSTRING_CARRIER (REQUEST_STRING n_flag_string) ($ptascii("false"))',
        '$string_carrier_valid(S_capture,pvalue_flag)',
        '$dynamic_constant_class(pvalue_flag) = (PVSTRING false)',
        '$value_nodes(pvalue_flag) = eps',
        '$lookup(S_capture.ENV,$ptascii("candidate")) = (n_candidate)',
        '$lookup(S_capture.ENV,$ptascii("flag")) = (n_flag)',
        '$lookup(S_capture.ENV,$ptascii("api")) = (n_api)',
        '$lookup(S_capture.ENV,$ptascii("calls")) = (n_calls)',
        '$lookup(S_capture.ENV,$ptascii("result")) = (n_result)',
        'S_capture.STORE[n_candidate] = DEFINED (POBJECT n_object)',
        'S_capture.STORE[n_flag] = DEFINED pvalue_flag',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_object) = 3',
        *reach('S','S_capture',1), *common.public('S'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.SITE = pconfigcall_capture.SITE',
        'pconfigcall.SELECTION = pconfigcall_capture.SELECTION', 'pconfigcall.NAMED',
        '$config_invoke_valid(S,pconfigcall)',
        '$dynamic_scalar_define_flag_values(pconfigcall) = ((' + text(TARGET) + ',POBJECT n_object,pvalue_flag))',
        '$dynamic_scalar_define_flag_valid(S,pconfigcall)',
        '$dynamic_scalar_define_flag_case_valid(S,pconfigcall)',
        '~$dynamic_constant_case_valid(S,pconfigcall)', '~$config_strict(S,pconfigcall)',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        '$config_nodes(pconfigcall) = [HOBJECT n_object]',
        *instance.certified('S','n_object','V80_REVIEW_LEFT','left'),
        *instance.certified('S','n_right','V80_REVIEW_RIGHT','right'),
        'S.USERCONSTANTS = [puserconstant_left,puserconstant_right]', 'n_object =/= n_right',
        *instance.property_value('S','n_object',17,'left_before'),
        *instance.property_value('S','n_right',23,'right_before'),
        'S.STORE[n_candidate] = DEFINED (POBJECT n_right)',
        'S.STORE[n_flag] = DEFINED pvalue_current_flag',
        '$string_bytes(pvalue_current_flag) = ($ptascii("0"))',
        'S.STORE[n_api] = DEFINED pvalue_current_api',
        '$string_bytes(pvalue_current_api) = ($ptascii("defined"))',
        'S.STORE[n_calls] = DEFINED (PINT 0)',
        'S.STORE[n_result] = DEFINED pvalue_sentinel',
        '$string_bytes(pvalue_sentinel) = ($ptascii("kept"))',
        '$source_constant_lookup(S,' + text(TARGET) + ') = eps',
        '$heap_owners($heap_graph(S),HOBJECT n_object) = 2',
        # Receipt and carrier projections are validator-only controls.
        *instance.controls('n_object','pconstantobject_left'),
        '$dynamic_scalar_define_flag_valid(S_missing,pconfigcall)',
        '~$dynamic_scalar_define_flag_valid(S_incomplete,pconfigcall)',
        '~$dynamic_scalar_define_flag_valid(S_dead,pconfigcall)',
        'n_bad_string = |S.STRINGDATA|',
        'pconfigcall_bad_flag = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN (PSTRING_CARRIER (REQUEST_STRING n_bad_string) ($ptascii("false"))))]',
        '~$dynamic_scalar_define_flag_valid(S,pconfigcall_bad_flag)',
        'pconfigcall_inf = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN (PFLOAT 9218868437227405312))]',
        '~$dynamic_scalar_define_flag_valid(S,pconfigcall_inf)',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        '$test_running(S_pause) = S',
        *common.step('S_dispatch','S'), *common.public('S_dispatch'),
        '$drive_steps($test_running(S_pause),1) = S_dispatch_found',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall',
        'perrorcall.LEVEL = 2', '$error_call_valid(S_dispatch,perrorcall)',
        'S_dispatch.USERCONSTANTS = S.USERCONSTANTS',
        'S_dispatch.ARRAYS = S.ARRAYS', 'S_dispatch.ALLOCATIONS = S.ALLOCATIONS',
        *reach('S_throw','S_dispatch',2), *common.public('S_throw'),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_after*',
        'perrorcall_throw.RESUME = perrorcall.RESUME',
        'S_throw.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'pthrowable_error.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_error,"message")) = ($ptascii("V80_PENDING"))',
        '$throwable_field(S_throw,n_error,"previous") = PNULL',
        '$throwable_chain_valid(S_throw,n_error)',
        '$throwable_field(S_throw,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_throw.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_throw,n_frame,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_throw,n_frame,$ptascii("args")) = PARRAY n_args',
        '$entry_lookup(S_throw.ARRAYS[n_args].ITEMS,KINT 1) = (DIRECT (POBJECT n_object))',
        '$entry_lookup(S_throw.ARRAYS[n_args].ITEMS,KINT 2) = (DIRECT pvalue_flag)',
        '$heap_edge_owners(HOBJECT n_object,$heap_graph(S_throw).EDGES,[HARRAY n_args]) = 1',
        'S_throw.STORE[n_candidate] = DEFINED (POBJECT n_right)',
        'S_throw.STORE[n_flag] = DEFINED pvalue_current_flag',
        'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
        'S_throw.STORE[n_result] = DEFINED pvalue_sentinel',
        *instance.property_value('S_throw','n_object',41,'left_throw'),
        'S_throw.USERCONSTANTS = S.USERCONSTANTS',
        '$dynamic_scalar_define_flag_case_valid(S_throw,pconfigcall)',
        '$heap_owners($heap_graph(S_throw),HOBJECT n_object) = 3',
        # Follow the genuine discard and any eager operation back to the throw.
        *common.step('S_drop','S_throw'), *reach('S_after','S_drop',3), *common.public('S_after'),
        'S_after.TODO = (THROW_SEARCH n_error) :: ptask_after*',
        'S_after.RESULT = S_throw.RESULT', 'S_after.EVENTS = S_throw.EVENTS',
        'S_after.ERRORHANDLER.CALLBACK = (perrorcall_throw.CALLBACK)',
        '$user_constant_at(S_after.USERCONSTANTS,' + text(TARGET) + ') = (puserconstant_row)',
        'S_after.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant_row]',
        'puserconstant_row.VALUE = POBJECT n_object',
        'puserconstant_row.CLASS = PVINSTANCE n_object porigin_left',
        'puserconstant_row.ORIGIN = pconfigcall.SITE',
        'puserconstant_row.READS = eps', 'puserconstant_row.RECEIVES = eps',
        '$heap_graph(S_after).EDGES = $heap_graph(S_throw).EDGES',
        '$heap_owners($heap_graph(S_after),HOBJECT n_object) = 3',
        '~(n_object <- S_after.DESTRUCTION.CALLED)']
    values += [f'S_after.{field} = S_throw.{field}' for field in
        ['OBJECTS','OBJECTPROPS','OBJECTTABLES','PROPREFS','STORE','ARRAYS','ALLOCATIONS','CONSTANTOBJECTS']]
    values += [
        # Existing-key pending composition is pure, with no extra callback credit.
        '$error_handler_eligible(S_after,2)',
        '$dynamic_scalar_define_flag_duplicate_valid(S_after,pconfigcall,|S_after.USERCONSTANTS|)',
        '$dynamic_scalar_define_flag_pending(S_after,pconfigcall) = S_after[.ERRORFATALTRACE = eps]',
        *common.reach('S_query','S_after',0,TARGET), *common.public('S_query'),
        'n_query_owners = $heap_owners($heap_graph(S_query),HOBJECT n_object)',
        *common.step('S_value','S_query','POBJECT n_object'),
        '$heap_owners($heap_graph(S_value),HOBJECT n_object) = $(n_query_owners + 1)',
        'S_value.ALLOCATIONS = S_query.ALLOCATIONS',
        '$heap_graph(S_value).EDGES = $heap_graph(S_query).EDGES',
        *reach('S_reference','S_value',4),
        '$lookup(S_reference.ENV,$ptascii("slot")) = (n_slot)',
        'n_slot <- S_reference.REFCELLS', 'HCELL n_slot <- S_reference.ALLOCATIONS',
        'S_reference.STORE[n_slot] = DEFINED (PINT 53)',
        *instance.property_value('S_reference','n_object',53,'reference'),
        'ppropertyslot_reference.STATE = PROP_VALUE (ALIAS n_slot)',
        *instance.store('S_store_left','S_reference','n_object',2,before),
        *instance.property_value('S_store_left','n_object',53,'store_left'),
        *instance.store('S_store_right','S_store_left_selected','n_right',1,before + b'D|53|'),
        'n_object <- S_store_right.DESTRUCTION.CALLED',
        *define.finish('S_store_right_selected',stdout),
        'S_final.USERCONSTANTS = S_after.USERCONSTANTS',
        'S_final.CONSTANTOBJECTS = S.CONSTANTOBJECTS',
        '$heap_owners($heap_graph(S_final),HOBJECT n_object) = 2',
        '$heap_owners($heap_graph(S_final),HOBJECT n_right) = 1',
        'n_object <- S_final.DESTRUCTION.CALLED', 'n_right <- S_final.DESTRUCTION.CALLED',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_final.ALLOCATIONS)', '~(HARRAY n_frame <- S_final.ALLOCATIONS)',
        '~(HARRAY n_args <- S_final.ALLOCATIONS)']
    return values


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = packet.process


def process(command, directory, timeout, cwd):
    if directory.parent.name == 'captured-string-flag-and-pending-object-publication':
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
