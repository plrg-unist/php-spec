#!/usr/bin/env python3
"""Reached cycle repair, late duplicate snapshot and throwing-handler cleanup."""
from pathlib import Path

import define_stdclass_array_duplicate_review_protocol as prior
import define_array_true_flag_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
TARGET = 'V74_REVIEW_ROW'
PREFIX = define.PREFIX + r'''
dec $test_array_true_peer_case(ptask) : bool
def $test_array_true_peer_case(DYNAMIC_CONSTANT_CASE_WARNING pconfigcall) = true
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V74_REVIEW_ROW"),pvalue))
def $test_array_true_peer_case(ptask) = false -- otherwise
dec $test_array_true_peer_front(pstate, nat) : bool
def $test_array_true_peer_front(S,0) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if $test_array_true_peer_case(perrorcall.RESUME)
def $test_array_true_peer_front(S,1) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V74_REVIEW_ROW"),pvalue))
def $test_array_true_peer_front(S,2) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata_unset)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_bucket) metadata_variable) :: expression_tail*
  -- if $base64(text_bucket) = $ptascii("bucket")
  -- if $lookup(S.ENV,$ptascii("bucket")) = (n_cell)
def $test_array_true_peer_front(S,3) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask_tail*
  -- if ~$test_array_true_peer_front(S,1)
def $test_array_true_peer_front(S,n_phase) = false -- otherwise
dec $test_array_true_peer_seek(pstate, nat, nat) : pstate
def $test_array_true_peer_seek(S,n_phase,0) = S
def $test_array_true_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_array_true_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_array_true_peer_seek(S,n_phase,n) = $test_array_true_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_array_true_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_array_true_peer_seek({start},{phase},5000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_array_true_peer_front({state},{phase})', *common.public(state)]


def checks(initial, stdout):
    assert stdout == b'B|H|1|2|T|H|2|2|E|V74_STOP|define|true|false|31|17|2|kept|41|A|'
    edge, leaf = text('edge'), text('leaf')
    source_items = f'[ENTRY (KSTRING {edge}) (ALIAS n_cell)]'
    copied_child = f'$array_insert($array_empty(),KSTRING {leaf},DIRECT (PINT 23))'
    copied_root = f'$array_insert($array_empty(),KSTRING {edge},DIRECT (PARRAY n_candidate_child))'
    values = [*initial, *define.reach('S','S_initial',0,TARGET),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.NAMED', 'pconfigcall.SELECTION = (n_selection)',
        '$dynamic_define_values(pconfigcall) = ((' + text(TARGET) + ',PARRAY n_input))',
        '$named_slot_at(pconfigcall.SENT,0) = NAMED_SENT (KNOWN pvalue_name)',
        '$named_slot_at(pconfigcall.SENT,2) = NAMED_SENT (KNOWN (PBOOL true))',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        '$dynamic_array_call_valid(S,pconfigcall)', '$dynamic_constant_case_valid(S,pconfigcall)',
        '$lookup(S.ENV,$ptascii("cell")) = (n_cell)',
        '$lookup(S.ENV,$ptascii("flag")) = (n_flag)',
        '$lookup(S.ENV,$ptascii("stage")) = (n_stage)',
        'n_cell <- S.REFCELLS', 'S.STORE[n_flag] = DEFINED (PBOOL true)',
        'S.STORE[n_stage] = DEFINED (PINT 0)',
        'S.ARRAYS[n_input].ITEMS = ' + source_items,
        'S.STORE[n_cell] = DEFINED (PARRAY n_input)',
        '$dynamic_array_recursive(S,PARRAY n_input,eps) = (true)',
        '$dynamic_array_value(S,PARRAY n_input,eps,true) = eps',
        'S.USERCONSTANTS = eps',
        # Pure captures/header controls are never driven.
        '$dynamic_array_known_matches(S,PARRAY n_input,eps)',
        '~$dynamic_array_known_matches(S,PARRAY n_input,(PINT 17))',
        'pconfigcall_false = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN (PBOOL false))]',
        '$dynamic_array_call_valid(S,pconfigcall_false)',
        '~$dynamic_constant_case_valid(S,pconfigcall_false)',
        'pconfigcall_nonbool = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN (PINT 1))]',
        '$dynamic_define_values(pconfigcall_nonbool) = eps',
        '~$dynamic_array_call_valid(S,pconfigcall_nonbool)',
        'n_bad_string = |S.STRINGDATA|',
        'pvalue_bad_name = PSTRING_CARRIER (REQUEST_STRING n_bad_string) ' + text(TARGET),
        '~$string_carrier_valid(S,pvalue_bad_name)',
        'pconfigcall_bad_name = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,0,KNOWN pvalue_bad_name)]',
        '$dynamic_array_call_valid(S,pconfigcall_bad_name)',
        '~$dynamic_constant_case_valid(S,pconfigcall_bad_name)',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_input)]',
        '~$dynamic_constant_case_valid(S_dead,pconfigcall)',
        *common.step('S_dispatch','S'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_case) :: ptask_tail*',
        'perrorcall_case.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall',
        'perrorcall_case.MESSAGE = $dynamic_constant_case_message()',
        'S_dispatch.ARRAYS = S.ARRAYS', 'S_dispatch.ALLOCATIONS = S.ALLOCATIONS',
        'S_dispatch.USERCONSTANTS = eps',
        '$task_nodes(perrorcall_case.RESUME) = [HARRAY n_input]',
        *reach('S_done','S_dispatch',0),
        'S_done.TODO = (ERROR_HANDLER_RESULT perrorcall_done) :: ptask_done*',
        'perrorcall_done.RESUME = perrorcall_case.RESUME',
        'S_done.RESULT = KNOWN (PBOOL true)',
        'S_done.STORE[n_flag] = DEFINED (PBOOL false)',
        'S_done.STORE[n_stage] = DEFINED (PINT 1)',
        'S_done.STORE[n_cell] = DEFINED (PARRAY n_leaf23)',
        f'S_done.ARRAYS[n_leaf23].ITEMS = [ENTRY (KSTRING {leaf}) (DIRECT (PINT 23))]',
        'S_done.ARRAYS[n_input].ITEMS = ' + source_items,
        '$dynamic_array_recursive(S_done,PARRAY n_input,eps) = (false)',
        '$user_constant_at(S_done.USERCONSTANTS,' + text(TARGET) + ') = (puserconstant_old)',
        'S_done.USERCONSTANTS = [puserconstant_old]',
        'puserconstant_old.VALUE = PINT 17', 'puserconstant_old.CLASS = PVSCALAR',
        '$dynamic_constant_case_valid(S_done,pconfigcall)',
        '$heap_owners($heap_graph(S_done),HARRAY n_input) = 2',
        '~$destructor_operational(S_done)',
        *common.step('S_case','S_done'), *common.public('S_case'),
        'S_case.TODO = (DYNAMIC_CONSTANT_CASE_WARNING pconfigcall) :: ptask_done*',
        'S_case.ARRAYS = S_done.ARRAYS', 'S_case.USERCONSTANTS = S_done.USERCONSTANTS',
        'n_before = |S_case.ARRAYS|', 'n_constants = |S_case.USERCONSTANTS|', 'n_constants = 1',
        *common.step('S_duplicate','S_case'), *common.public('S_duplicate'),
        'S_duplicate.TODO = (ERROR_HANDLER_INVOKE perrorcall_duplicate) :: ptask_done*',
        'pvalueclass_leaf = PVARRAY false ([(KSTRING ' + leaf + ',PVSCALAR)])',
        'pvalueclass_copy = PVARRAY false ([(KSTRING ' + edge + ',pvalueclass_leaf)])',
        'perrorcall_duplicate.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass_copy n_constants',
        'n_candidate_child = n_before', 'n_candidate = $(n_before + 1)',
        'parray_child = ' + copied_child, 'parray_copy = ' + copied_root,
        'S_duplicate.ARRAYS = S_case.ARRAYS ++ [parray_child,parray_copy]',
        'S_duplicate.USERCONSTANTS = S_done.USERCONSTANTS',
        '$task_nodes(perrorcall_duplicate.RESUME) = [HARRAY n_candidate,HARRAY n_input]',
        '$dynamic_array_duplicate_valid(S_duplicate,pconfigcall,n_candidate,pvalueclass_copy,n_constants)',
        '~$dynamic_array_duplicate_valid(S_duplicate,pconfigcall,n_candidate,pvalueclass_copy,0)',
        '$heap_owners($heap_graph(S_duplicate),HARRAY n_candidate) = 1',
        *reach('S_throw','S_duplicate',1),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_throw*',
        'perrorcall_throw.RESUME = perrorcall_duplicate.RESUME',
        'S_throw.STORE[n_flag] = DEFINED (PBOOL false)',
        'S_throw.STORE[n_stage] = DEFINED (PINT 2)',
        'S_throw.STORE[n_cell] = DEFINED (PARRAY n_leaf31)',
        f'S_throw.ARRAYS[n_leaf31].ITEMS = [ENTRY (KSTRING {leaf}) (DIRECT (PINT 31))]',
        'S_throw.ARRAYS[n_input].ITEMS = ' + source_items,
        'S_throw.ARRAYS[n_candidate_child] = parray_child',
        'S_throw.ARRAYS[n_candidate] = parray_copy',
        'S_throw.USERCONSTANTS = S_done.USERCONSTANTS',
        '$dynamic_array_duplicate_valid(S_throw,pconfigcall,n_candidate,pvalueclass_copy,n_constants)',
        '$throwable_field(S_throw,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_throw.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_trace_api))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_api].ITEMS,KSTRING ($ptascii("args"))) = (DIRECT (PARRAY n_trace_args))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_args].ITEMS,KINT 1) = (DIRECT (PARRAY n_input))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_args].ITEMS,KINT 2) = (DIRECT (PBOOL true))',
        '$heap_owners($heap_graph(S_throw),HARRAY n_input) = 3',
        *common.step('S_drop','S_throw'), *reach('S_after','S_drop',3),
        'S_after.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
        '~(HARRAY n_candidate <- S_after.ALLOCATIONS)',
        '~(HARRAY n_candidate_child <- S_after.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_after),HARRAY n_input) = 2',
        'S_after.USERCONSTANTS = S_done.USERCONSTANTS',
        *reach('S_bucket','S_after',2),
        '$lookup(S_bucket.ENV,$ptascii("bucket")) = (n_cell)',
        '$lookup(S_bucket.ENV,$ptascii("raw")) = (n_raw_cell)',
        '$lookup(S_bucket.ENV,$ptascii("input")) = (n_input_cell)',
        'S_bucket.STORE[n_raw_cell] = DEFINED (PARRAY n_raw)', 'n_raw =/= n_input',
        'S_bucket.STORE[n_input_cell] = DEFINED (PARRAY n_input)',
        'S_bucket.ARRAYS[n_raw].ITEMS = ' + source_items,
        'S_bucket.ARRAYS[n_input].ITEMS = ' + source_items,
        'S_bucket.STORE[n_cell] = DEFINED (PARRAY n_leaf41)',
        f'S_bucket.ARRAYS[n_leaf41].ITEMS = [ENTRY (KSTRING {leaf}) (DIRECT (PINT 41))]',
        *define.finish('S_bucket',stdout),
        'S_final.USERCONSTANTS = [puserconstant_old]',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)',
        '~(HARRAY n_raw <- S_final.ALLOCATIONS)',
        '~(HARRAY n_candidate <- S_final.ALLOCATIONS)',
        '~(HARRAY n_candidate_child <- S_final.ALLOCATIONS)',
        '~(HCELL n_cell <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)']
    return values


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    raise SystemExit(0 if packet.main() else 1)
