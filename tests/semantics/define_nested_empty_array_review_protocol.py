#!/usr/bin/env python3
"""Independent nested mutable-empty copies, alias trace and real bucket write."""
from pathlib import Path

import define_stdclass_array_duplicate_review_protocol as prior
import define_nested_empty_array_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text = prior.ROOT, prior.text
TARGET = 'V70_REVIEW_TARGET'
PREFIX = define.PREFIX + r'''
dec $test_nested_empty_peer_front(pstate, nat) : bool
def $test_nested_empty_peer_front(S,0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V70_REVIEW_TARGET"),pvalue))
def $test_nested_empty_peer_front(S,1) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V70_REVIEW_TARGET"),pvalue))
def $test_nested_empty_peer_front(S,2) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata_unset)) :: ptask_tail*
  -- if expression* = expression_head :: expression_tail*
  -- if expression_head = NExprVariable (BYTES text_bucket) metadata_variable
  -- if $base64(text_bucket) = $ptascii("bucket")
  -- if $lookup(S.ENV,$ptascii("bucket")) = (n_bucket)
def $test_nested_empty_peer_front(S,n_phase) = false -- otherwise
dec $test_nested_empty_peer_seek(pstate, nat, nat) : pstate
def $test_nested_empty_peer_seek(S,n_phase,0) = S
def $test_nested_empty_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_nested_empty_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_nested_empty_peer_seek(S,n_phase,n) = $test_nested_empty_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_nested_empty_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_nested_empty_peer_seek({start},{phase},5000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_nested_empty_peer_front({state},{phase})', *common.public(state)]


def checks(initial, stdout):
    assert stdout == b'B|H|2|next|E|V70_STOP|define|false|empty|history|aliases|empty-cvs|17|31|kept|A|'
    head, nested, leaf = [text(key) for key in ('head','nested','leaf')]
    values = [*initial, *define.reach('S','S_initial',1,TARGET),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.NAMED', 'pconfigcall.SELECTION = (n_selection)',
        '$dynamic_define_values(pconfigcall) = ((' + text(TARGET) + ',PARRAY n_input))',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN (PARRAY n_input)),NAMED_SENT (KNOWN (PBOOL false))]',
        'n_constants = |S.USERCONSTANTS|', 'n_constants = 1',
        '$dynamic_array_duplicate_call_valid(S,pconfigcall,n_constants)',
        '$lookup(S.ENV,$ptascii("old")) = (n_old_cell)',
        'S.STORE[n_old_cell] = DEFINED (PARRAY n_old)',
        '$lookup(S.ENV,$ptascii("next")) = (n_next_cell)',
        'S.STORE[n_next_cell] = DEFINED (PARRAY n_next)',
        'S.ARRAYS[n_old].ITEMS = eps', 'S.ARRAYS[n_old].NEXT = 91',
        'S.ARRAYS[n_next].ITEMS = eps', 'S.ARRAYS[n_next].NEXT = 41',
        'n_old =/= n_next', '~$array_immutable(S,n_next)',
        '$lookup(S.ENV,$ptascii("cell")) = (n_cell)',
        'n_cell <- S.REFCELLS', 'S.STORE[n_cell] = DEFINED (PARRAY n_next)',
        f'S.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {head}) (ALIAS n_cell),ENTRY (KSTRING {nested}) (DIRECT (PARRAY n_input_child))]',
        f'S.ARRAYS[n_input_child].ITEMS = [ENTRY (KSTRING {leaf}) (ALIAS n_cell)]',
        'n_before = |S.ARRAYS|',
        *common.step('S_dispatch','S'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants',
        'n_head_copy = n_before', 'n_leaf_copy = $(n_before + 1)',
        'n_nested_copy = $(n_before + 2)', 'n_candidate = $(n_before + 3)',
        'n_head_copy =/= n_leaf_copy',
        f'parray_nested = $array_insert($array_empty(),KSTRING {leaf},DIRECT (PARRAY n_leaf_copy))',
        f'parray_root = $array_insert($array_insert($array_empty(),KSTRING {head},DIRECT (PARRAY n_head_copy)),KSTRING {nested},DIRECT (PARRAY n_nested_copy))',
        'S_dispatch.ARRAYS = S.ARRAYS ++ [$array_empty(),$array_empty(),parray_nested,parray_root]',
        f'pvalueclass_nested = PVARRAY false ([(KSTRING {leaf},PVARRAY false eps)])',
        f'pvalueclass = PVARRAY false ([(KSTRING {head},PVARRAY false eps),(KSTRING {nested},pvalueclass_nested)])',
        '$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_candidate,pvalueclass,n_constants)',
        '$task_nodes(perrorcall.RESUME) = [HARRAY n_candidate,HARRAY n_input]',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.USERCONSTANTS = S.USERCONSTANTS',
        'H_dispatch = $heap_graph(S_dispatch)',
        '$heap_edge_owners(HARRAY n_next,H_dispatch.EDGES,[HARRAY n_head_copy,HARRAY n_leaf_copy,HARRAY n_nested_copy,HARRAY n_candidate]) = 0',
        '$heap_owners(H_dispatch,HARRAY n_head_copy) = 1',
        '$heap_owners(H_dispatch,HARRAY n_leaf_copy) = 1',
        # Pure nested class/history and seen guards are never driven.
        '$dynamic_array_value(S_dispatch,PARRAY n_head_copy,[n_head_copy],true) = eps',
        '$dynamic_array_value(S_dispatch,PARRAY n_head_copy,[n_head_copy],false) = eps',
        f'pvalueclass_wrong = $pvclass_put(pvalueclass,KSTRING {head},PVARRAY true eps)',
        '~$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_candidate,pvalueclass_wrong,n_constants)',
        'S_history = S_dispatch[.ARRAYS[n_head_copy].NEXT = 41]',
        '~$dynamic_array_duplicate_valid(S_history,pconfigcall,n_candidate,pvalueclass,n_constants)',
        *reach('S_entered','S_dispatch',0), *reach('S_throw','S_entered',1),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_throw*',
        'perrorcall_throw.RESUME = perrorcall.RESUME',
        'S_throw.STORE[n_cell] = DEFINED (PARRAY n_old)',
        '$dynamic_array_duplicate_valid(S_throw,pconfigcall,n_candidate,pvalueclass,n_constants)',
        'S_throw.ARRAYS[n_head_copy] = $array_empty()',
        'S_throw.ARRAYS[n_leaf_copy] = $array_empty()',
        '$throwable_field(S_throw,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_throw.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_trace_api))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_api].ITEMS,KSTRING ($ptascii("args"))) = (DIRECT (PARRAY n_trace_args))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_args].ITEMS,KINT 1) = (DIRECT (PARRAY n_input))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_args].ITEMS,KINT 2) = (DIRECT (PBOOL false))',
        '$user_constant_at(S_throw.USERCONSTANTS,$ptascii("V70_REVIEW_SIDE")) = (puserconstant_side)',
        'S_throw.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant_side]',
        'puserconstant_side.VALUE = PINT 31',
        '$heap_owners($heap_graph(S_throw),HARRAY n_input) = 3',
        *common.step('S_after','S_throw'), *common.public('S_after'),
        'S_after.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
        '$heap_owners($heap_graph(S_after),HARRAY n_input) = 2',
        '~(HARRAY n_candidate <- S_after.ALLOCATIONS)',
        '~(HARRAY n_nested_copy <- S_after.ALLOCATIONS)',
        '~(HARRAY n_head_copy <- S_after.ALLOCATIONS)',
        '~(HARRAY n_leaf_copy <- S_after.ALLOCATIONS)',
        *reach('S_bucket','S_after',2),
        '$lookup(S_bucket.ENV,$ptascii("bucket")) = (n_cell)',
        'S_bucket.STORE[n_cell] = DEFINED (PARRAY n_written)',
        'n_written =/= n_old', 'n_written =/= n_next',
        'S_bucket.ARRAYS[n_written].NEXT = 92',
        '$entry_lookup(S_bucket.ARRAYS[n_written].ITEMS,KINT 91) = (DIRECT pvalue_trace)',
        '$string_bytes(pvalue_trace) = ($ptascii("trace"))',
        'S_bucket.STORE[n_old_cell] = DEFINED (PARRAY n_old)',
        'S_bucket.STORE[n_next_cell] = DEFINED (PARRAY n_next)',
        'S_bucket.ARRAYS[n_old].ITEMS = eps', 'S_bucket.ARRAYS[n_old].NEXT = 91',
        'S_bucket.ARRAYS[n_next].ITEMS = eps', 'S_bucket.ARRAYS[n_next].NEXT = 41',
        f'S_bucket.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {head}) (ALIAS n_cell),ENTRY (KSTRING {nested}) (DIRECT (PARRAY n_input_child))]',
        f'S_bucket.ARRAYS[n_input_child].ITEMS = [ENTRY (KSTRING {leaf}) (ALIAS n_cell)]',
        *define.finish('S_bucket',stdout), 'S_final.USERCONSTANTS = S_throw.USERCONSTANTS',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)', '~(HARRAY n_input_child <- S_final.ALLOCATIONS)',
        '~(HARRAY n_old <- S_final.ALLOCATIONS)', '~(HARRAY n_next <- S_final.ALLOCATIONS)',
        '~(HARRAY n_written <- S_final.ALLOCATIONS)', '~(HCELL n_cell <- S_final.ALLOCATIONS)',
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
