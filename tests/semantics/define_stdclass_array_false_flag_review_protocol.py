#!/usr/bin/env python3
"""Independent captured false flag survives caller mutation and abrupt discard."""
from pathlib import Path

import define_stdclass_array_duplicate_review_protocol as prior
import define_stdclass_array_false_flag_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
TARGET = 'V68_REVIEW_TARGET'
PREFIX = define.PREFIX + r'''
dec $test_array_false_peer_front(pstate, nat) : bool
def $test_array_false_peer_front(S,0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V68_REVIEW_TARGET"),pvalue))
def $test_array_false_peer_front(S,1) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V68_REVIEW_TARGET"),pvalue))
def $test_array_false_peer_front(S,n_phase) = false -- otherwise
dec $test_array_false_peer_seek(pstate, nat, nat) : pstate
def $test_array_false_peer_seek(S,n_phase,0) = S
def $test_array_false_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_array_false_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_array_false_peer_seek(S,n_phase,n) = $test_array_false_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_array_false_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_array_false_peer_seek({start},{phase},5000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_array_false_peer_front({state},{phase})', *common.public(state)]


def checks(initial, stdout):
    assert stdout == b'B|H|2|17|E|V68_STOP|define|R|F|T|17|41|19|31|kept|A|'
    head, nested, leaf = [text(key) for key in ('head', 'nested', 'leaf')]
    values = [*initial, *define.reach('S', 'S_initial', 1, TARGET),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        '$dynamic_array_call_valid(S,pconfigcall)',
        'pconfigcall.NAMED', 'pconfigcall.INDEX = 3',
        'pconfigcall.SELECTION = (n_selection)',
        'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN (PARRAY n_input)),NAMED_SENT (KNOWN (PBOOL false))]',
        '$string_bytes(pvalue_name) = (' + text(TARGET) + ')',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        '~$dynamic_constant_case_flag(pconfigcall)',
        '$config_nodes(pconfigcall) = [HARRAY n_input]',
        '$lookup(S.ENV,$ptascii("flag")) = (n_flag)',
        'S.STORE[n_flag] = DEFINED (PBOOL false)',
        '$lookup(S.ENV,$ptascii("cell")) = (n_cell)',
        '$user_constant_at(S.USERCONSTANTS,$ptascii("V68_REVIEW_LEFT")) = (puserconstant_left)',
        'puserconstant_left.VALUE = POBJECT n_left',
        'puserconstant_left.CLASS = PVSTDCLASS n_left porigin_left',
        '$user_constant_at(S.USERCONSTANTS,$ptascii("V68_REVIEW_RIGHT")) = (puserconstant_right)',
        'puserconstant_right.VALUE = POBJECT n_right', 'n_left =/= n_right',
        '$user_constant_at(S.USERCONSTANTS,' + text(TARGET) + ') = (puserconstant_old)',
        'puserconstant_old.VALUE = PINT 17', 'n_constants = |S.USERCONSTANTS|',
        'n_constants = 3',
        'S.STORE[n_cell] = DEFINED (POBJECT n_left)',
        f'S.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {head}) (ALIAS n_cell),ENTRY (KSTRING {nested}) (DIRECT (PARRAY n_input_child))]',
        f'S.ARRAYS[n_input_child].ITEMS = [ENTRY (KSTRING {leaf}) (ALIAS n_cell)]',
        # Pure flag/domain controls are never driven.
        'pconfigcall_true = pconfigcall[.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN (PARRAY n_input)),NAMED_SENT (KNOWN (PBOOL true))]]',
        '$dynamic_constant_case_flag(pconfigcall_true)',
        '~$dynamic_array_call_valid(S,pconfigcall_true)',
        'pconfigcall_nonbool = pconfigcall[.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN (PARRAY n_input)),NAMED_SENT (KNOWN (PINT 0))]]',
        '$dynamic_define_values(pconfigcall_nonbool) = eps',
        '~$dynamic_array_call_valid(S,pconfigcall_nonbool)',
        'n_before = |S.ARRAYS|', '$test_outputs(S.EVENTS) = ' + term(b'B|'),
        *common.step('S_dispatch', 'S'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_copy pvalueclass_copy n_constants',
        '$error_call_valid(S_dispatch,perrorcall)',
        '$task_nodes(perrorcall.RESUME) = [HARRAY n_copy,HARRAY n_input]',
        'n_copy = $(n_before + 1)', 'n_child = n_before',
        'n_copy =/= n_input', 'n_child =/= n_input_child',
        f'parray_child = $array_insert($array_empty(),KSTRING {leaf},DIRECT (POBJECT n_left))',
        f'parray_root = $array_insert($array_insert($array_empty(),KSTRING {head},DIRECT (POBJECT n_left)),KSTRING {nested},DIRECT (PARRAY n_child))',
        'S_dispatch.ARRAYS = S.ARRAYS ++ [parray_child,parray_root]',
        'S_dispatch.STORE = S.STORE', 'S_dispatch.USERCONSTANTS = S.USERCONSTANTS',
        '$heap_owners($heap_graph(S_dispatch),HOBJECT n_left) = 4',
        '$heap_owners($heap_graph(S_dispatch),HARRAY n_input) = 2',
        *reach('S_entered', 'S_dispatch', 0),
        *reach('S_throw', 'S_entered', 1),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_throw*',
        'perrorcall_throw.RESUME = perrorcall.RESUME',
        # The caller cell now holds true; the exact continuation still owns false.
        'S_throw.STORE[n_flag] = DEFINED (PBOOL true)',
        'n_flag <- S_throw.REFCELLS',
        'S_throw.STORE[n_cell] = DEFINED (POBJECT n_right)',
        '$dynamic_array_call_valid(S_throw,pconfigcall)',
        '$dynamic_array_duplicate_valid(S_throw,pconfigcall,n_copy,pvalueclass_copy,n_constants)',
        '~$dynamic_array_duplicate_valid(S_throw,pconfigcall_true,n_copy,pvalueclass_copy,n_constants)',
        '$user_constant_at(S_throw.USERCONSTANTS,$ptascii("V68_REVIEW_SIDE")) = (puserconstant_side)',
        'S_throw.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant_side]',
        'puserconstant_side.VALUE = PINT 31',
        'S_throw.ARRAYS[n_copy] = parray_root', 'S_throw.ARRAYS[n_child] = parray_child',
        '$throwable_field(S_throw,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_throw.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_trace_api))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_api].ITEMS,KSTRING ($ptascii("args"))) = (DIRECT (PARRAY n_trace_args))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_args].ITEMS,KINT 1) = (DIRECT (PARRAY n_input))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_args].ITEMS,KINT 2) = (DIRECT (PBOOL false))',
        '|S_throw.ARRAYS[n_trace_args].ITEMS| = 3',
        'H_throw = $heap_graph(S_throw)',
        '$heap_edge_owners(HARRAY n_input,H_throw.EDGES,[HARRAY n_trace_args]) = 1',
        '$heap_edge_owners(HARRAY n_copy,H_throw.EDGES,[HARRAY n_trace_args]) = 0',
        '$heap_edge_owners(HOBJECT n_left,H_throw.EDGES,[HARRAY n_copy,HARRAY n_child]) = 2',
        '$heap_owners(H_throw,HARRAY n_copy) = 1',
        '$heap_owners(H_throw,HARRAY n_input) = 3',
        '$heap_owners(H_throw,HOBJECT n_left) = 3',
        '$heap_owners(H_throw,HOBJECT n_right) = 2',
        *define.property_value('S_throw','n_left',41,'changed_left'),
        # One real discard drops the private snapshot and its two leaf edges.
        *common.step('S_after','S_throw'), *common.public('S_after'),
        'S_after.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
        'S_after.USERCONSTANTS = S_throw.USERCONSTANTS',
        'S_after.STORE[n_flag] = DEFINED (PBOOL true)',
        '~(HARRAY n_copy <- S_after.ALLOCATIONS)', '~(HARRAY n_child <- S_after.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_after),HARRAY n_input) = 2',
        '$heap_owners($heap_graph(S_after),HOBJECT n_left) = 1',
        '$heap_owners($heap_graph(S_after),HOBJECT n_right) = 2',
        *define.finish('S_after',stdout),
        'S_final.USERCONSTANTS = S_throw.USERCONSTANTS',
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 1',
        '$heap_owners($heap_graph(S_final),HOBJECT n_right) = 1',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)', '~(HARRAY n_input_child <- S_final.ALLOCATIONS)',
        '~(HCELL n_flag <- S_final.ALLOCATIONS)', '~(HCELL n_cell <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)',
        *define.property_value('S_final','n_left',41,'final_left'),
        *define.property_value('S_final','n_right',19,'final_right')]
    return values


# Reuse the main-only preparation, preserving the exact native file and bytes.
prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    raise SystemExit(0 if packet.main() else 1)
