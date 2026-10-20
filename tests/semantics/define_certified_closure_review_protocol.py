#!/usr/bin/env python3
"""Reached pending certified-Closure publication and shared static storage."""
from pathlib import Path

import define_stdclass_array_duplicate_protocol as prior
import define_certified_closure_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text = prior.ROOT, prior.text
TARGET = 'V83_REVIEW_TARGET'
CASE = 'pending-certified-closure-retains-captured-pointer-and-statics'
PREFIX = prior.PREFIX + r'''
dec $test_closure_value_peer_front(pstate, nat) : bool
def $test_closure_value_peer_front(S,0) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.INDEX = 2
  -- if $named_slot_at(pconfigcall.SENT,1) = NAMED_SENT (KNOWN (POBJECT n_object))
  -- if $named_slot_at(pconfigcall.SENT,2) = NAMED_SENT (KNOWN (PBOOL true))
def $test_closure_value_peer_front(S,1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V83_REVIEW_TARGET"),POBJECT n_object))
def $test_closure_value_peer_front(S,2) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V83_REVIEW_TARGET"),POBJECT n_object))
def $test_closure_value_peer_front(S,3) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask_tail*
def $test_closure_value_peer_front(S,n_phase) = false -- otherwise
dec $test_closure_value_peer_seek(pstate, nat, nat) : pstate
def $test_closure_value_peer_seek(S,n_phase,0) = S
def $test_closure_value_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_closure_value_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_closure_value_peer_seek(S,n_phase,n) = $test_closure_value_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_closure_value_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_closure_value_peer_seek({start},{phase},1000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_closure_value_peer_front({state},{phase})']


def certified(state, obj, label, donor):
    return [f'$user_constant_at({state}.USERCONSTANTS,{text(donor)}) = (puserconstant_{label})',
        f'puserconstant_{label}.VALUE = POBJECT {obj}',
        f'puserconstant_{label}.CLASS = PVCLOSURE {obj} porigin_{label}',
        f'$constant_callable_record({state}.CONSTANTCLOSURES,{obj}) = (pconstantclosure_{label})',
        f'pconstantclosure_{label}.SITE = porigin_{label}',
        f'pconstantclosure_{label}.DECL = puserconstant_{label}.ORIGIN',
        f'$constant_callable_record_valid({state},pconstantclosure_{label})',
        f'$global_constant_callable_header({state},pconstantclosure_{label})',
        f'$constant_value_class_valid({state},POBJECT {obj},PVCLOSURE {obj} porigin_{label})',
        f'$dynamic_define_value_class({state},POBJECT {obj}) = (PVCLOSURE {obj} porigin_{label})']


def counter(state, obj, label, value):
    return [f'{state}.OBJECTS[{obj}] = CONSTANTCLOSURE porigin_{label} (REALCLOSURE porigin_{label} eps ([pstaticcell_{label}]))',
        f'n_counter_{label} = pstaticcell_{label}.CELL',
        f'HCELL n_counter_{label} <- {state}.ALLOCATIONS',
        f'n_counter_{label} <- {state}.REFCELLS',
        f'{state}.STORE[n_counter_{label}] = DEFINED (PINT {value})']


def query(state, start, suffix):
    after = state + '_value'
    return [*common.reach(state, start, 0, TARGET),
        f'{state}.TODO = (CONFIG_INVOKE pconfigcall_{suffix}) :: ptask_{suffix}*',
        f'$dynamic_global_constant_valid({state},pconfigcall_{suffix})',
        f'$dynamic_global_constant_value({state},{text(TARGET)}) = (POBJECT n_left)',
        f'n_owners_{suffix} = $heap_owners($heap_graph({state}),HOBJECT n_left)',
        *common.step(after, state, 'POBJECT n_left'),
        f'{after}.TODO = ptask_{suffix}*',
        f'$heap_owners($heap_graph({after}),HOBJECT n_left) = $(n_owners_{suffix} + 1)',
        f'$heap_graph({after}).EDGES = $heap_graph({state}).EDGES',
        *[f'{after}.{field} = {state}.{field}' for field in (
            'OBJECTS','STATICS','STORE','ARRAYS','ALLOCATIONS','USERCONSTANTS',
            'CONSTANTCLOSURES','CLOSURESCOPES','CLOSUREBINDINGS')]]


def checks(initial, name, stdout):
    assert name == CASE
    assert stdout == (b'B|N|H|2|1|absent|E|V83_PENDING|none|define|true|left|right|'
        b'false|defined|1|kept|same|2|3|101|4|same|A|')
    values = [*initial, *reach('S_capture','S_initial',0), *common.public('S_capture'),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        'pconfigcall_capture.INDEX = 2', 'pconfigcall_capture.SELECTION = (n_selection)',
        'S_capture.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        '$named_slot_at(pconfigcall_capture.SENT,0) = NAMED_HOLE',
        '$named_slot_at(pconfigcall_capture.SENT,1) = NAMED_SENT (KNOWN (POBJECT n_left))',
        '$named_slot_at(pconfigcall_capture.SENT,2) = NAMED_SENT (KNOWN (PBOOL true))',
        '$lookup(S_capture.ENV,$ptascii("candidate")) = (n_candidate)',
        '$lookup(S_capture.ENV,$ptascii("flag")) = (n_flag)',
        '$lookup(S_capture.ENV,$ptascii("api")) = (n_api)',
        '$lookup(S_capture.ENV,$ptascii("calls")) = (n_calls)',
        '$lookup(S_capture.ENV,$ptascii("result")) = (n_result)',
        'S_capture.STORE[n_candidate] = DEFINED (POBJECT n_left)',
        'S_capture.STORE[n_flag] = DEFINED (PBOOL true)',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_left) = 3',
        *reach('S','S_capture',1), *common.public('S'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.SITE = pconfigcall_capture.SITE',
        'pconfigcall.SELECTION = pconfigcall_capture.SELECTION', 'pconfigcall.NAMED',
        '$config_invoke_valid(S,pconfigcall)', '$dynamic_constant_case_valid(S,pconfigcall)',
        '$dynamic_define_values(pconfigcall) = ((' + text(TARGET) + ',POBJECT n_left))',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        '$config_nodes(pconfigcall) = [HOBJECT n_left]',
        *certified('S','n_left','left','V83_REVIEW_LEFT'),
        *certified('S','n_right','right','V83_REVIEW_RIGHT'),
        'n_left =/= n_right',
        'S.USERCONSTANTS = [puserconstant_left,puserconstant_right]',
        'S.CONSTANTCLOSURES = [pconstantclosure_left,pconstantclosure_right]',
        'S.OBJECTS[n_left] = CONSTANTCLOSURE porigin_left (REALCLOSURE porigin_left eps eps)',
        'S.OBJECTS[n_right] = CONSTANTCLOSURE porigin_right (REALCLOSURE porigin_right eps eps)',
        'S.STORE[n_candidate] = DEFINED (POBJECT n_left)',
        'S.STORE[n_flag] = DEFINED (PBOOL false)',
        'S.STORE[n_api] = DEFINED pvalue_api', '$string_bytes(pvalue_api) = ($ptascii("defined"))',
        'S.STORE[n_calls] = DEFINED (PINT 0)',
        'S.STORE[n_result] = DEFINED pvalue_sentinel',
        '$string_bytes(pvalue_sentinel) = ($ptascii("kept"))',
        '$source_constant_lookup(S,' + text(TARGET) + ') = eps',
        '$heap_owners($heap_graph(S),HOBJECT n_left) = 3',
        '$heap_owners($heap_graph(S),HOBJECT n_right) = 1',
        # Validator-only controls never become execution roots.
        'S_missing = S[.CONSTANTCLOSURES = [pconstantclosure_right]]',
        'S_plain = S_missing[.OBJECTS[n_left] = REALCLOSURE porigin_left eps eps]',
        '$dynamic_define_value_class(S_plain,POBJECT n_left) = (PVOBJECT)',
        '$dynamic_constant_case_valid(S_plain,pconfigcall)',
        '~$constant_value_class_valid(S_plain,POBJECT n_left,PVCLOSURE n_left porigin_left)',
        '~$user_constants_valid(S_plain,S_plain.USERCONSTANTS)',
        'S_bad_site = S[.CONSTANTCLOSURES[0].SITE = pconfigcall.SITE]',
        'S_bad_prefix = S[.CONSTANTCLOSURES[0].PREFIX = $(|S.DECLARATIONS| + 1)]',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_left)]']
    for state in ('S_missing','S_bad_site','S_bad_prefix','S_dead'):
        values += [f'$dynamic_define_value_class({state},POBJECT n_left) = eps',
            f'~$dynamic_constant_case_valid({state},pconfigcall)']
    values += [
        *common.step('S_warning','S'),
        'S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall',
        'perrorcall.LEVEL = 2', '$error_call_valid(S_warning,perrorcall)',
        'S_warning.OBJECTS = S.OBJECTS', 'S_warning.STORE = S.STORE',
        'S_warning.ALLOCATIONS = S.ALLOCATIONS', 'S_warning.ARRAYS = S.ARRAYS',
        'S_warning.USERCONSTANTS = S.USERCONSTANTS', 'S_warning.EVENTS = S.EVENTS',
        *reach('S_throw','S_warning',2), *common.public('S_throw'),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_done) :: ptask_after*',
        'perrorcall_done.RESUME = perrorcall.RESUME',
        'S_throw.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'pthrowable_error.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_error,"message")) = ($ptascii("V83_PENDING"))',
        '$throwable_field(S_throw,n_error,"previous") = PNULL',
        '$throwable_chain_valid(S_throw,n_error)',
        '$throwable_field(S_throw,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_throw.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_throw,n_frame,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_throw,n_frame,$ptascii("args")) = PARRAY n_args',
        '$entry_lookup(S_throw.ARRAYS[n_args].ITEMS,KINT 1) = (DIRECT (POBJECT n_left))',
        '$entry_lookup(S_throw.ARRAYS[n_args].ITEMS,KINT 2) = (DIRECT (PBOOL true))',
        '$heap_edge_owners(HOBJECT n_left,$heap_graph(S_throw).EDGES,[HARRAY n_args]) = 1',
        'S_throw.STORE[n_candidate] = DEFINED (POBJECT n_right)',
        'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
        'S_throw.STORE[n_result] = DEFINED pvalue_sentinel',
        *counter('S_throw','n_left','left',1),
        'S_throw.USERCONSTANTS = S.USERCONSTANTS',
        '$heap_owners($heap_graph(S_throw),HOBJECT n_left) = 3',
        '$test_outputs(S_throw.EVENTS) = ($ptascii("B|N|H|2|1|absent|"))',
        # Consume the actual discard and any cleanup, preserving its original tail.
        *common.step('S_drop','S_throw'), *reach('S_after','S_drop',3),
        *common.public('S_after'),
        'S_after.TODO = (THROW_SEARCH n_error) :: ptask_after*',
        'S_after.RESULT = S_throw.RESULT', 'S_after.EVENTS = S_throw.EVENTS',
        'S_after.ERRORHANDLER.CALLBACK = (perrorcall_done.CALLBACK)',
        '$user_constant_at(S_after.USERCONSTANTS,' + text(TARGET) + ') = (puserconstant_row)',
        'S_after.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant_row]',
        'puserconstant_row.ORIGIN = pconfigcall.SITE',
        'puserconstant_row.VALUE = POBJECT n_left',
        'puserconstant_row.CLASS = PVCLOSURE n_left porigin_left',
        'puserconstant_row.READS = eps', 'puserconstant_row.RECEIVES = eps',
        '$heap_graph(S_after).EDGES = $heap_graph(S_throw).EDGES',
        '$heap_owners($heap_graph(S_after),HOBJECT n_left) = 3']
    values += [f'S_after.{field} = S_throw.{field}' for field in (
        'OBJECTS','OBJECTPROPS','OBJECTTABLES','PROPREFS','STORE','STATICS','REFCELLS',
        'ARRAYS','ALLOCATIONS','CONSTANTCLOSURES','CLOSURESCOPES','CLOSUREBINDINGS')]
    values += [
        *query('S_query','S_after','first'),
        *counter('S_query','n_left','left',1),
        'n_owners_first = 4',
        *query('S_again','S_query_value','again'),
        *counter('S_again','n_left','left',3),
        *counter('S_again','n_right','right',101),
        'n_owners_again = 4',
        'S_again.USERCONSTANTS = S_after.USERCONSTANTS',
        'S_again.CONSTANTCLOSURES = S.CONSTANTCLOSURES',
        *define.finish('S_again_value',stdout),
        *counter('S_final','n_left','left',4),
        *counter('S_final','n_right','right',101),
        'S_final.USERCONSTANTS = S_after.USERCONSTANTS',
        'S_final.CONSTANTCLOSURES = S.CONSTANTCLOSURES',
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 2',
        '$heap_owners($heap_graph(S_final),HOBJECT n_right) = 1',
        '$heap_owners($heap_graph(S_final),HCELL n_counter_left) = 1',
        '$heap_owners($heap_graph(S_final),HCELL n_counter_right) = 1',
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
