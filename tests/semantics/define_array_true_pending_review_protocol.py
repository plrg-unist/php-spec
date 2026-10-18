#!/usr/bin/env python3
"""Reached pending-cycle suppression, prior trace owners and ordinary recovery."""
from pathlib import Path

import define_stdclass_array_duplicate_review_protocol as prior
import define_array_true_pending_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text = prior.ROOT, prior.text
TARGET = 'V75_REVIEW_OLD'
RECOVERY = 'V75_REVIEW_RECOVERY'
PREFIX = define.PREFIX + r'''
dec $test_array_pending_peer_front(pstate, nat) : bool
def $test_array_pending_peer_front(S,0) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V75_REVIEW_OLD"),pvalue))
def $test_array_pending_peer_front(S,1) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata_unset)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_bucket) metadata_variable) :: expression_tail*
  -- if $base64(text_bucket) = $ptascii("bucket")
  -- if $lookup(S.ENV,$ptascii("bucket")) = (n_cell)
def $test_array_pending_peer_front(S,2) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata_unset)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_copy) metadata_variable) :: expression_tail*
  -- if $base64(text_copy) = $ptascii("copy")
  -- if $lookup(S.ENV,$ptascii("copy")) = (n_cell)
def $test_array_pending_peer_front(S,n_phase) = false -- otherwise
dec $test_array_pending_peer_seek(pstate, nat, nat) : pstate
def $test_array_pending_peer_seek(S,n_phase,0) = S
def $test_array_pending_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_array_pending_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_array_pending_peer_seek(S,n_phase,n) = $test_array_pending_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_array_pending_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_array_pending_peer_seek({start},{phase},5000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_array_pending_peer_front({state},{phase})', *common.public(state)]


def checks(initial, stdout):
    assert stdout == b'B|H|1|2|E|V75_PENDING|V75_BASE|none|define|true|true|false|17|31|1|kept|41|41|T|53|41|67|41|A|'
    edge, tag = text('edge'), text('tag')
    source_items = f'[ENTRY (KSTRING {edge}) (ALIAS n_cell)]'
    values = [*initial, *define.reach('S', 'S_initial', 1, TARGET),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.NAMED', 'pconfigcall.SELECTION = (n_selection)',
        '$dynamic_define_values(pconfigcall) = ((' + text(TARGET) + ',PARRAY n_input))',
        '$named_slot_at(pconfigcall.SENT,2) = NAMED_SENT (KNOWN (PBOOL true))',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        '$dynamic_array_call_valid(S,pconfigcall)', '$dynamic_constant_case_valid(S,pconfigcall)',
        '$dynamic_array_recursive(S,PARRAY n_input,eps) = (false)',
        '$user_constant_at(S.USERCONSTANTS,' + text(TARGET) + ') = (puserconstant_old)',
        'puserconstant_old.VALUE = PINT 17', 'S.USERCONSTANTS = [puserconstant_old]',
        '$lookup(S.ENV,$ptascii("cell")) = (n_cell)', 'n_cell <- S.REFCELLS',
        '$lookup(S.ENV,$ptascii("input")) = (n_input_cell)',
        'S.STORE[n_input_cell] = DEFINED (PARRAY n_input)',
        'S.ARRAYS[n_input].ITEMS = ' + source_items,
        '$lookup(S.ENV,$ptascii("flag")) = (n_flag)', 'S.STORE[n_flag] = DEFINED (PBOOL true)',
        '$lookup(S.ENV,$ptascii("stage")) = (n_stage)', 'S.STORE[n_stage] = DEFINED (PINT 0)',
        '$lookup(S.ENV,$ptascii("api")) = (n_api)',
        'S.STORE[n_api] = DEFINED pvalue_api',
        '$string_bytes(pvalue_api) = ($ptascii("define"))',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)',
        'S.STORE[n_result] = DEFINED pvalue_sentinel',
        *common.step('S_dispatch', 'S'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_case) :: ptask_tail*',
        'perrorcall_case.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall',
        'perrorcall_case.LEVEL = 2', 'perrorcall_case.MESSAGE = $dynamic_constant_case_message()',
        '$error_call_valid(S_dispatch,perrorcall_case)',
        'S_dispatch.ARRAYS = S.ARRAYS', 'S_dispatch.ALLOCATIONS = S.ALLOCATIONS',
        'S_dispatch.USERCONSTANTS = S.USERCONSTANTS',
        *reach('S_throw', 'S_dispatch', 0),
        'S_throw.TODO = (THROW_SEARCH n_pending) :: (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_after*',
        'perrorcall_throw.RESUME = perrorcall_case.RESUME',
        'S_throw.OBJECTS[n_pending] = THROWABLE pthrowable_pending',
        'pthrowable_pending.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_pending,"message")) = ($ptascii("V75_PENDING"))',
        '$throwable_field(S_throw,n_pending,"previous") = POBJECT n_base', 'n_base =/= n_pending',
        'S_throw.OBJECTS[n_base] = THROWABLE pthrowable_base', 'pthrowable_base.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_base,"message")) = ($ptascii("V75_BASE"))',
        '$throwable_field(S_throw,n_base,"previous") = PNULL',
        '$throwable_chain_valid(S_throw,n_pending)',
        'S_throw.STORE[n_cell] = DEFINED (PARRAY n_input)',
        'S_throw.ARRAYS[n_input] = S.ARRAYS[n_input]',
        '$dynamic_constant_case_valid(S_throw,pconfigcall)',
        '$dynamic_array_recursive(S_throw,PARRAY n_input,eps) = (true)',
        '$dynamic_array_value(S_throw,PARRAY n_input,eps,true) = eps',
        'S_throw.STORE[n_flag] = DEFINED (PBOOL false)',
        'S_throw.STORE[n_stage] = DEFINED (PINT 1)',
        'S_throw.STORE[n_api] = DEFINED pvalue_api_after',
        '$string_bytes(pvalue_api_after) = ($ptascii("defined"))',
        '$user_constant_at(S_throw.USERCONSTANTS,$ptascii("V75_REVIEW_SIDE")) = (puserconstant_side)',
        'puserconstant_side.VALUE = PINT 31',
        'S_throw.USERCONSTANTS = [puserconstant_old,puserconstant_side]',
        '$throwable_field(S_throw,n_pending,"trace") = PARRAY n_trace_pending',
        '$entry_lookup(S_throw.ARRAYS[n_trace_pending].ITEMS,KINT 1) = (DIRECT (PARRAY n_frame_pending))',
        '$trace_array_field(S_throw,n_frame_pending,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_throw,n_frame_pending,$ptascii("args")) = PARRAY n_args_pending',
        '$entry_lookup(S_throw.ARRAYS[n_args_pending].ITEMS,KINT 1) = (DIRECT (PARRAY n_input))',
        '$entry_lookup(S_throw.ARRAYS[n_args_pending].ITEMS,KINT 2) = (DIRECT (PBOOL true))',
        '$throwable_field(S_throw,n_base,"trace") = PARRAY n_trace_base',
        'n_trace_base =/= n_trace_pending',
        '$entry_lookup(S_throw.ARRAYS[n_trace_base].ITEMS,KINT 1) = (DIRECT (PARRAY n_frame_base))',
        '$trace_array_field(S_throw,n_frame_base,$ptascii("args")) = PARRAY n_args_base',
        '$entry_lookup(S_throw.ARRAYS[n_args_base].ITEMS,KINT 1) = (DIRECT (PARRAY n_input))',
        '$entry_lookup(S_throw.ARRAYS[n_args_base].ITEMS,KINT 2) = (DIRECT (PBOOL true))',
        '$heap_owners($heap_graph(S_throw),HARRAY n_input) = 5',
        '$heap_edge_owners(HCELL n_cell,$heap_graph(S_throw).EDGES,[HARRAY n_input]) = 1',
        '~$destructor_operational(S_throw)',
        # Only pure guard projections; none is driven.
        'S_dead = S_throw[.ALLOCATIONS = $destruction_node_delete(S_throw.ALLOCATIONS,HOBJECT n_pending)]',
        'S_dead_pending = $dynamic_constant_case_pending(S_dead,pconfigcall)',
        'S_dead_pending.COMPLETION = UNSUPPORTED "boolean define flag pending-exception registration"',
        'pconfigcall_false = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN (PBOOL false))]',
        '~$dynamic_constant_case_valid(S_throw,pconfigcall_false)',
        'S_false_pending = $dynamic_constant_case_pending(S_throw,pconfigcall_false)',
        'S_false_pending.COMPLETION = UNSUPPORTED "boolean define flag pending-exception registration"',
        'S_no_throw = S_throw[.TODO = ptask_after*]',
        'S_no_throw_pending = $dynamic_constant_case_pending(S_no_throw,pconfigcall)',
        'S_no_throw_pending.COMPLETION = UNSUPPORTED "boolean define flag pending-exception registration"',
        *common.step('S_after', 'S_throw'), *common.public('S_after'),
        'S_after.TODO = (THROW_SEARCH n_pending) :: ptask_after*',
        'S_after.ARRAYS = S_throw.ARRAYS', 'S_after.ALLOCATIONS = S_throw.ALLOCATIONS',
        'S_after.OBJECTS = S_throw.OBJECTS', 'S_after.OBJECTPROPS = S_throw.OBJECTPROPS',
        'S_after.STORE = S_throw.STORE', 'S_after.USERCONSTANTS = S_throw.USERCONSTANTS',
        'S_after.RESULT = S_throw.RESULT', 'S_after.EVENTS = S_throw.EVENTS',
        'S_after.ERRORHANDLER.CALLBACK = (perrorcall_throw.CALLBACK)',
        '$throwable_field(S_after,n_pending,"previous") = POBJECT n_base',
        '$throwable_field(S_after,n_base,"previous") = PNULL',
        '$heap_owners($heap_graph(S_after),HARRAY n_input) = 4',
        '$heap_edge_owners(HCELL n_cell,$heap_graph(S_after).EDGES,[HARRAY n_input]) = 1',
        *reach('S_bucket', 'S_after', 1),
        '$lookup(S_bucket.ENV,$ptascii("bucket")) = (n_cell)',
        '$lookup(S_bucket.ENV,$ptascii("raw")) = (n_raw_cell)',
        'S_bucket.STORE[n_raw_cell] = DEFINED (PARRAY n_raw)', 'n_raw =/= n_input',
        'S_bucket.STORE[n_input_cell] = DEFINED (PARRAY n_input)',
        'S_bucket.ARRAYS[n_input].ITEMS = ' + source_items,
        'S_bucket.ARRAYS[n_raw].ITEMS = ' + source_items,
        'S_bucket.STORE[n_cell] = DEFINED (PARRAY n_leaf41)',
        f'S_bucket.ARRAYS[n_leaf41].ITEMS = [ENTRY (KSTRING {tag}) (DIRECT (PINT 41))]',
        '$dynamic_array_recursive(S_bucket,PARRAY n_input,eps) = (false)',
        '$heap_edge_owners(HCELL n_cell,$heap_graph(S_bucket).EDGES,[HARRAY n_input,HARRAY n_raw]) = 2',
        *define.reach('S_recovery', 'S_bucket', 0, RECOVERY),
        'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
        '$dynamic_define_values(pconfigcall_recovery) = ((' + text(RECOVERY) + ',PARRAY n_input))',
        '$named_slot_at(pconfigcall_recovery.SENT,2) = NAMED_SENT (KNOWN (PBOOL false))',
        '$dynamic_array_call_valid(S_recovery,pconfigcall_recovery)',
        'S_recovery.USERCONSTANTS = S_throw.USERCONSTANTS',
        'n_before = |S_recovery.ARRAYS|',
        *common.step('S_row', 'S_recovery', 'PBOOL true'), *common.public('S_row'),
        'S_row.TODO = ptask_recovery*',
        '$user_constant_at(S_row.USERCONSTANTS,' + text(RECOVERY) + ') = (puserconstant_recovery)',
        'S_row.USERCONSTANTS = [puserconstant_old,puserconstant_side,puserconstant_recovery]',
        'puserconstant_recovery.VALUE = PARRAY n_root', 'n_child = n_before', 'n_root = $(n_before + 1)',
        f'parray_child = $array_insert($array_empty(),KSTRING {tag},DIRECT (PINT 41))',
        f'parray_root = $array_insert($array_empty(),KSTRING {edge},DIRECT (PARRAY n_child))',
        f'pvalueclass_child = PVARRAY false ([(KSTRING {tag},PVSCALAR)])',
        f'puserconstant_recovery.CLASS = PVARRAY false ([(KSTRING {edge},pvalueclass_child)])',
        'puserconstant_recovery.ORIGIN = pconfigcall_recovery.SITE',
        'S_row.ARRAYS = S_recovery.ARRAYS ++ [parray_child,parray_root]',
        'n_child =/= n_leaf41',
        '$heap_owners($heap_graph(S_row),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_row),HARRAY n_child) = 1',
        *common.reach('S_query', 'S_row', 0, RECOVERY), *common.public('S_query'),
        '$dynamic_global_constant_value(S_query,' + text(RECOVERY) + ') = (PARRAY n_root)',
        'n_query_owners = $heap_owners($heap_graph(S_query),HARRAY n_root)',
        *common.step('S_value', 'S_query', 'PARRAY n_root'),
        'S_value.ARRAYS = S_query.ARRAYS', 'S_value.ALLOCATIONS = S_query.ALLOCATIONS',
        '$heap_graph(S_value).EDGES = $heap_graph(S_query).EDGES',
        '$heap_owners($heap_graph(S_value),HARRAY n_root) = $(n_query_owners + 1)',
        *reach('S_cow', 'S_value', 2),
        '$lookup(S_cow.ENV,$ptascii("copy")) = (n_copy_cell)',
        'S_cow.STORE[n_copy_cell] = DEFINED (PARRAY n_copy_root)', 'n_copy_root =/= n_root',
        f'$entry_lookup(S_cow.ARRAYS[n_copy_root].ITEMS,KSTRING {edge}) = (DIRECT (PARRAY n_copy_child))',
        'n_copy_child =/= n_child',
        f'S_cow.ARRAYS[n_copy_child].ITEMS = [ENTRY (KSTRING {tag}) (DIRECT (PINT 53))]',
        'S_cow.STORE[n_cell] = DEFINED (PARRAY n_source67)',
        f'S_cow.ARRAYS[n_source67].ITEMS = [ENTRY (KSTRING {tag}) (DIRECT (PINT 67))]',
        'S_cow.ARRAYS[n_root] = parray_root', 'S_cow.ARRAYS[n_child] = parray_child',
        '$heap_owners($heap_graph(S_cow),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_cow),HARRAY n_child) = 1',
        '$heap_owners($heap_graph(S_cow),HARRAY n_source67) = 1',
        '$throwable_field(S_cow,n_pending,"previous") = POBJECT n_base',
        *define.finish('S_cow', stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_final.ARRAYS[n_root] = parray_root', 'S_final.ARRAYS[n_child] = parray_child',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_child) = 1',
        '~(HOBJECT n_pending <- S_final.ALLOCATIONS)', '~(HOBJECT n_base <- S_final.ALLOCATIONS)',
        '~(HARRAY n_trace_pending <- S_final.ALLOCATIONS)', '~(HARRAY n_trace_base <- S_final.ALLOCATIONS)',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)', '~(HARRAY n_raw <- S_final.ALLOCATIONS)',
        '~(HARRAY n_copy_root <- S_final.ALLOCATIONS)', '~(HARRAY n_copy_child <- S_final.ALLOCATIONS)',
        '~(HARRAY n_source67 <- S_final.ALLOCATIONS)', '~(HCELL n_cell <- S_final.ALLOCATIONS)']
    return values


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = packet.process


def process(command, directory, _timeout, cwd):
    return packet_process(command, directory, 150, cwd)


packet.process = process
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    raise SystemExit(0 if packet.main() else 1)
