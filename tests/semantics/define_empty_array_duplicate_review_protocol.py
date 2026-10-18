#!/usr/bin/env python3
"""Independent mutable empty snapshot, flag COW and trace-only abrupt owner."""
from pathlib import Path

import define_stdclass_array_duplicate_review_protocol as prior
import define_empty_array_duplicate_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
TARGET = 'V69_REVIEW_TARGET'
PREFIX = define.PREFIX + r'''
dec $test_empty_peer_front(pstate, nat) : bool
def $test_empty_peer_front(S,0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V69_REVIEW_TARGET"),pvalue))
def $test_empty_peer_front(S,1) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V69_REVIEW_TARGET"),pvalue))
def $test_empty_peer_front(S,n_phase) = false -- otherwise
dec $test_empty_peer_seek(pstate, nat, nat) : pstate
def $test_empty_peer_seek(S,n_phase,0) = S
def $test_empty_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_empty_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_empty_peer_seek(S,n_phase,n) = $test_empty_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_empty_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_empty_peer_seek({start},{phase},5000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_empty_peer_front({state},{phase})', *common.public(state)]


def checks(initial, stdout):
    assert stdout == b'B|H|2|17|flag|E|V69_STOP|define|empty|history|caller|kept-empty|false|17|31|kept|A|'
    values = [*initial, *define.reach('S','S_initial',1,TARGET),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.NAMED', 'pconfigcall.SELECTION = (n_selection)',
        '$dynamic_define_values(pconfigcall) = ((' + text(TARGET) + ',PARRAY n_input))',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN (PARRAY n_input)),NAMED_SENT (KNOWN (PBOOL false))]',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        'n_constants = |S.USERCONSTANTS|', 'n_constants = 1',
        '$dynamic_array_duplicate_call_valid(S,pconfigcall,n_constants)',
        'parray_input = S.ARRAYS[n_input]', 'parray_input.ITEMS = eps',
        'parray_input.NEXT = 91', '~$array_immutable(S,n_input)',
        '$lookup(S.ENV,$ptascii("input")) = (n_cell)',
        'S.STORE[n_cell] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        'S.ARRAYS[n_caller].NEXT = 92',
        '$entry_lookup(S.ARRAYS[n_caller].ITEMS,KINT 91) = (DIRECT pvalue_flag)',
        '$string_bytes(pvalue_flag) = ($ptascii("flag"))',
        '$heap_owners($heap_graph(S),HARRAY n_input) = 1',
        'n_before = |S.ARRAYS|',
        *common.step('S_dispatch','S'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate (PVARRAY false eps) n_constants',
        'n_candidate = n_before', 'n_candidate =/= n_input', 'n_candidate =/= n_caller',
        'S_dispatch.ARRAYS = S.ARRAYS ++ [$array_empty()]',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.USERCONSTANTS = S.USERCONSTANTS',
        '$error_call_valid(S_dispatch,perrorcall)',
        '$task_nodes(perrorcall.RESUME) = [HARRAY n_candidate,HARRAY n_input]',
        '$heap_owners($heap_graph(S_dispatch),HARRAY n_candidate) = 1',
        '$heap_owners($heap_graph(S_dispatch),HARRAY n_input) = 1',
        # Pure canonical/class/identity controls are never driven.
        '~$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_candidate,PVARRAY true eps,n_constants)',
        'S_self = S_dispatch[.ARRAYS[n_input] = $array_empty()]',
        '~$array_immutable(S_self,n_input)',
        '$dynamic_array_value(S_self,PARRAY n_input,eps,false) = ((S_self,PARRAY n_input,PVARRAY false eps))',
        '~$dynamic_array_duplicate_valid(S_self,pconfigcall,n_input,PVARRAY false eps,n_constants)',
        'S_history = S_dispatch[.ARRAYS[n_candidate] = parray_input]',
        '~$dynamic_array_duplicate_valid(S_history,pconfigcall,n_candidate,PVARRAY false eps,n_constants)',
        'S_dead = S_dispatch[.ALLOCATIONS = $destruction_node_delete(S_dispatch.ALLOCATIONS,HARRAY n_candidate)]',
        '~$dynamic_array_duplicate_valid(S_dead,pconfigcall,n_candidate,PVARRAY false eps,n_constants)',
        *reach('S_entered','S_dispatch',0),
        *reach('S_throw','S_entered',1),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_throw*',
        'perrorcall_throw.RESUME = perrorcall.RESUME',
        '$user_constant_at(S_throw.USERCONSTANTS,$ptascii("V69_REVIEW_SIDE")) = (puserconstant_side)',
        'S_throw.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant_side]',
        'puserconstant_side.VALUE = PINT 31',
        '$dynamic_array_duplicate_valid(S_throw,pconfigcall,n_candidate,PVARRAY false eps,n_constants)',
        'S_throw.ARRAYS[n_candidate] = $array_empty()',
        'S_throw.ARRAYS[n_input] = parray_input',
        'S_throw.STORE[n_cell] = DEFINED (PARRAY n_caller)',
        'S_throw.ARRAYS[n_caller].NEXT = 93',
        '$entry_lookup(S_throw.ARRAYS[n_caller].ITEMS,KINT 92) = (DIRECT pvalue_handler)',
        '$string_bytes(pvalue_handler) = ($ptascii("handler"))',
        '$throwable_field(S_throw,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_throw.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_trace_api))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_api].ITEMS,KSTRING ($ptascii("args"))) = (DIRECT (PARRAY n_trace_args))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_args].ITEMS,KINT 1) = (DIRECT (PARRAY n_input))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_args].ITEMS,KINT 2) = (DIRECT (PBOOL false))',
        'H_throw = $heap_graph(S_throw)',
        '$heap_edge_owners(HARRAY n_input,H_throw.EDGES,[HARRAY n_trace_args]) = 1',
        '$heap_edge_owners(HARRAY n_candidate,H_throw.EDGES,[HARRAY n_trace_args]) = 0',
        '$heap_owners(H_throw,HARRAY n_input) = 2',
        '$heap_owners(H_throw,HARRAY n_candidate) = 1',
        *common.step('S_after','S_throw'), *common.public('S_after'),
        'S_after.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
        'S_after.USERCONSTANTS = S_throw.USERCONSTANTS',
        '~(HARRAY n_candidate <- S_after.ALLOCATIONS)',
        '(HARRAY n_input) <- S_after.ALLOCATIONS',
        '(HARRAY n_caller) <- S_after.ALLOCATIONS',
        '$heap_owners($heap_graph(S_after),HARRAY n_input) = 1',
        'S_after.ARRAYS[n_input] = parray_input',
        *define.finish('S_after',stdout),
        'S_final.USERCONSTANTS = S_throw.USERCONSTANTS',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)',
        '~(HARRAY n_caller <- S_final.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_final.ALLOCATIONS)',
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
