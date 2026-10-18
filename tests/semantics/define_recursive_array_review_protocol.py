#!/usr/bin/env python3
"""Reached late cycle creation, original Error trace and late-cut DAG copies."""
from pathlib import Path

import define_stdclass_array_duplicate_review_protocol as prior
import define_recursive_array_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text = prior.ROOT, prior.text
TARGET, RECOVER = 'V71_REVIEW_TARGET', 'V71_REVIEW_RECOVER'
MESSAGE = 'define(): Argument #2 ($value) cannot be a recursive array'
PREFIX = define.PREFIX + r'''
dec $test_recursive_peer_front(pstate, nat) : bool
def $test_recursive_peer_front(S,0) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.INDEX = 1
  -- if pconfigcall.NAMED
  -- if pconfigcall.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (PARRAY n_input))]
def $test_recursive_peer_front(S,1) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata_unset)) :: ptask_tail*
  -- if expression* = expression_head :: expression_tail*
  -- if expression_head = NExprVariable (BYTES text_trace) metadata_variable
  -- if $base64(text_trace) = $ptascii("trace")
  -- if $lookup(S.ENV,$ptascii("copy")) = (n_copy)
def $test_recursive_peer_front(S,n_phase) = false -- otherwise
dec $test_recursive_peer_seek(pstate, nat, nat) : pstate
def $test_recursive_peer_seek(S,n_phase,0) = S
def $test_recursive_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_recursive_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_recursive_peer_seek(S,n_phase,n) = $test_recursive_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_recursive_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_recursive_peer_seek({start},{phase},5000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_recursive_peer_front({state},{phase})', *common.public(state)]


def checks(initial, stdout):
    assert stdout == (b'B|E|' + MESSAGE.encode() + b'|define|false|cycle|17|0|kept|broken|T|31|23|23|stored|A|')
    edge, again, tag = [text(key) for key in ('edge','again','tag')]
    return [*initial, *reach('S_pre','S_initial',0),
        'S_pre.TODO = (CONFIG_ARGS pconfigcall_pre) :: ptask_pre*',
        'pconfigcall_pre.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (PARRAY n_input))]',
        '$lookup(S_pre.ENV,$ptascii("cell")) = (n_cell)',
        'n_cell <- S_pre.REFCELLS',
        'S_pre.STORE[n_cell] = DEFINED (PARRAY n_empty)',
        'S_pre.ARRAYS[n_empty] = $array_empty()',
        f'parray_input = $array_insert($array_insert($array_empty(),KSTRING {edge},ALIAS n_cell),KSTRING {again},ALIAS n_cell)',
        'S_pre.ARRAYS[n_input] = parray_input',
        '$dynamic_array_recursive(S_pre,PARRAY n_input,eps) = (false)',
        *define.reach('S','S_pre',1,TARGET),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.SITE = pconfigcall_pre.SITE',
        'pconfigcall.NAMED', 'pconfigcall.SELECTION = (n_selection)',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN (PARRAY n_input)),NAMED_SENT (KNOWN (PBOOL false))]',
        '$string_bytes(pvalue_name) = ('+text(TARGET)+')',
        '$dynamic_array_call_valid(S,pconfigcall)',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        'S.STORE[n_cell] = DEFINED (PARRAY n_input)',
        'S.ARRAYS = S_pre.ARRAYS',
        '$dynamic_array_recursive(S,PARRAY n_input,eps) = (true)',
        '$dynamic_array_value(S,PARRAY n_input,eps,true) = eps',
        '$heap_owners($heap_graph(S),HARRAY n_input) = 3',
        '$user_constant_at(S.USERCONSTANTS,'+text(TARGET)+') = (puserconstant_old)',
        'puserconstant_old.VALUE = PINT 17',
        '$lookup(S.ENV,$ptascii("warnings")) = (n_warnings_cell)',
        'S.STORE[n_warnings_cell] = DEFINED (PINT 0)',
        '$lookup(S.ENV,$ptascii("ok")) = (n_result_cell)',
        'S.STORE[n_result_cell] = DEFINED pvalue_kept',
        '$string_bytes(pvalue_kept) = ($ptascii("kept"))',
        # Malformed helper inputs are projections, never resumed.
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HCELL n_cell)]',
        '$dynamic_array_recursive(S_dead,PARRAY n_input,eps) = eps',
        'S_dead_root = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_input)]',
        '$dynamic_array_recursive(S_dead_root,PARRAY n_input,eps) = eps',
        '$dynamic_array_recursive(S,PARRAY (|S.ARRAYS|),eps) = eps',
        'S_malformed = S[.STORE[n_cell] = UNDEFINED]',
        '$dynamic_array_recursive(S_malformed,PARRAY n_input,eps) = eps',
        *common.step('S_error','S'), *common.public('S_error'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'pthrowable_error.KIND = "ValueError"',
        'pthrowable_error.ORIGIN = (pconfigcall.SITE)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = ('+text(MESSAGE)+')',
        '$throwable_field(S_error,n_error,"line") = PINT pconfigcall.LINE',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]',
        '$trace_array_field(S_error,n_frame,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_error,n_frame,$ptascii("args")) = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_name),ENTRY (KINT 1) (DIRECT (PARRAY n_input)),ENTRY (KINT 2) (DIRECT (PBOOL false))]',
        'S_error.ARRAYS = S.ARRAYS ++ [S_error.ARRAYS[n_trace],S_error.ARRAYS[n_args],S_error.ARRAYS[n_frame]]',
        'S_error.STORE = S.STORE', 'S_error.ENV = S.ENV',
        'S_error.USERCONSTANTS = S.USERCONSTANTS',
        'S_error.EVENTS = S.EVENTS', 'S_error.ERRORHANDLER = S.ERRORHANDLER',
        '$heap_owners($heap_graph(S_error),HARRAY n_input) = 3',
        *reach('S_repre','S_error',0),
        'S_repre.TODO = (CONFIG_ARGS pconfigcall_repre) :: ptask_repre*',
        'pconfigcall_repre.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (PARRAY n_input))]',
        'S_repre.STORE[n_cell] = DEFINED (PARRAY n_input)',
        '$dynamic_array_recursive(S_repre,PARRAY n_input,eps) = (true)',
        'S_repre.STORE[n_warnings_cell] = DEFINED (PINT 0)',
        'S_repre.STORE[n_result_cell] = DEFINED pvalue_kept',
        *define.reach('S_retry','S_repre',0,RECOVER),
        'S_retry.TODO = (CONFIG_INVOKE pconfigcall_retry) :: ptask_retry*',
        'pconfigcall_retry.SITE = pconfigcall_repre.SITE',
        'pconfigcall_retry.SENT = [NAMED_SENT (KNOWN pvalue_recover),NAMED_SENT (KNOWN (PARRAY n_input)),NAMED_SENT (KNOWN (PBOOL false))]',
        '$dynamic_array_call_valid(S_retry,pconfigcall_retry)',
        'S_retry.STORE[n_cell] = DEFINED (PARRAY n_dag)',
        'HARRAY n_dag <- $pools_nodes(S_retry.POOLS)',
        f'parray_dag = $array_insert($array_empty(),KSTRING {tag},DIRECT (PINT 23))',
        'S_retry.ARRAYS[n_dag] = parray_dag',
        'S_retry.ARRAYS[n_input] = parray_input',
        '$dynamic_array_recursive(S_retry,PARRAY n_input,eps) = (false)',
        '$dynamic_array_recursive(S_retry,PARRAY n_dag,[n_input]) = (false)',
        'S_retry.USERCONSTANTS = S.USERCONSTANTS',
        'n_before = |S_retry.ARRAYS|',
        *common.step('S_row','S_retry','PBOOL true'), *common.public('S_row'),
        'n_edge_copy = n_before', 'n_again_copy = $(n_before + 1)',
        'n_root = $(n_before + 2)', 'n_edge_copy =/= n_again_copy',
        f'parray_copy = $array_insert($array_insert($array_empty(),KSTRING {edge},DIRECT (PARRAY n_edge_copy)),KSTRING {again},DIRECT (PARRAY n_again_copy))',
        'S_row.ARRAYS = S_retry.ARRAYS ++ [parray_dag,parray_dag,parray_copy]',
        '$user_constant_at(S_row.USERCONSTANTS,'+text(RECOVER)+') = (puserconstant_row)',
        'S_row.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant_row]',
        'puserconstant_row.VALUE = PARRAY n_root',
        f'pvalueclass_child = PVARRAY false ([(KSTRING {tag},PVSCALAR)])',
        f'puserconstant_row.CLASS = PVARRAY false ([(KSTRING {edge},pvalueclass_child),(KSTRING {again},pvalueclass_child)])',
        'S_row.STORE = S_retry.STORE', 'S_row.EVENTS = S_retry.EVENTS',
        *reach('S_end','S_row',1),
        '$lookup(S_end.ENV,$ptascii("copy")) = (n_copy_cell)',
        'S_end.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_root',
        f'$entry_lookup(S_end.ARRAYS[n_copy].ITEMS,KSTRING {edge}) = (DIRECT (PARRAY n_written))',
        f'$entry_lookup(S_end.ARRAYS[n_written].ITEMS,KSTRING {tag}) = (DIRECT (PINT 31))',
        f'$entry_lookup(S_end.ARRAYS[n_copy].ITEMS,KSTRING {again}) = (DIRECT (PARRAY n_again_copy))',
        'S_end.ARRAYS[n_root] = parray_copy',
        'S_end.ARRAYS[n_edge_copy] = parray_dag',
        'S_end.ARRAYS[n_again_copy] = parray_dag',
        'S_end.ARRAYS[n_dag] = parray_dag',
        *define.finish('S_end',stdout), 'S_final.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_final.ARRAYS[n_root] = parray_copy',
        'S_final.ARRAYS[n_edge_copy] = parray_dag',
        'S_final.ARRAYS[n_again_copy] = parray_dag',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_edge_copy) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_again_copy) = 1',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)',
        'HARRAY n_dag <- S_final.ALLOCATIONS',
        'HARRAY n_dag <- $pools_nodes(S_final.POOLS)',
        'S_final.ARRAYS[n_dag] = parray_dag',
        '~(HARRAY n_copy <- S_final.ALLOCATIONS)',
        '~(HARRAY n_written <- S_final.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_final.ALLOCATIONS)',
        '~(HARRAY n_frame <- S_final.ALLOCATIONS)',
        '~(HARRAY n_args <- S_final.ALLOCATIONS)',
        '~(HCELL n_cell <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)']


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    raise SystemExit(0 if packet.main() else 1)
