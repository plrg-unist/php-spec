#!/usr/bin/env python3
"""Independent certified instance edges across snapshot, throw and query COW."""
from pathlib import Path

import define_stdclass_array_duplicate_review_protocol as prior
import define_certified_instance_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
TARGET = 'V73_REVIEW_TREE'
PREFIX = define.PREFIX + r'''
dec $test_certified_instance_peer_front(pstate, nat) : bool
def $test_certified_instance_peer_front(S,0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V73_REVIEW_TREE"),pvalue))
def $test_certified_instance_peer_front(S,1) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V73_REVIEW_TREE"),pvalue))
def $test_certified_instance_peer_front(S,2) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata_unset)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_slot) metadata_variable) :: expression_tail*
  -- if $base64(text_slot) = $ptascii("slot")
  -- if $lookup(S.ENV,$ptascii("slot")) = (n_slot)
def $test_certified_instance_peer_front(S,3) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask_tail*
  -- if ~$test_certified_instance_peer_front(S,1)
def $test_certified_instance_peer_front(S,4) = true
  -- if S.RESULT = KNOWN (PBOOL true)
def $test_certified_instance_peer_front(S,n_phase) = false -- otherwise
dec $test_certified_instance_peer_seek(pstate, nat, nat) : pstate
def $test_certified_instance_peer_seek(S,n_phase,0) = S
def $test_certified_instance_peer_seek(S,n_phase,n) = S
  -- if $(n > 0)
  -- if $test_certified_instance_peer_front(S,n_phase) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_certified_instance_peer_seek(S,n_phase,n) = $test_certified_instance_peer_seek($drive_steps($test_running(S),1),n_phase,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_certified_instance_peer_front(S,n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase):
    return [f'{state}_found = $test_certified_instance_peer_seek({start},{phase},5000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_certified_instance_peer_front({state},{phase})', *common.public(state)]


def checks(initial, stdout):
    assert stdout == b'B|T|R|H|2|E|V73_STOP|define|false|L|17|R|41|17|kept|41|31|kept|A|D|17|D|41|'
    head, nested, leaf = [text(key) for key in ('head', 'nested', 'leaf')]
    child = f'$array_insert($array_empty(),KSTRING {leaf},DIRECT (POBJECT n_right))'
    root = lambda n: f'$array_insert($array_insert($array_empty(),KSTRING {head},DIRECT (POBJECT n_right)),KSTRING {nested},DIRECT (PARRAY {n}))'
    input_items = f'[ENTRY (KSTRING {head}) (ALIAS n_cell),ENTRY (KSTRING {nested}) (DIRECT (PARRAY n_input_child))]'
    values = [*initial, *define.reach('S_fresh', 'S_initial', 0, TARGET),
        'S_fresh.TODO = (CONFIG_INVOKE pconfigcall_fresh) :: ptask_fresh*',
        'pconfigcall_fresh.NAMED',
        '$dynamic_define_values(pconfigcall_fresh) = ((' + text(TARGET) + ',PARRAY n_input))',
        '$dynamic_define_known(S_fresh,pconfigcall_fresh.SITE,1) = eps',
        '$dynamic_array_call_valid(S_fresh,pconfigcall_fresh)',
        '$user_constant_at(S_fresh.USERCONSTANTS,$ptascii("V73_REVIEW_LEFT")) = (puserconstant_left)',
        '$user_constant_at(S_fresh.USERCONSTANTS,$ptascii("V73_REVIEW_RIGHT")) = (puserconstant_right)',
        'S_fresh.USERCONSTANTS = [puserconstant_left,puserconstant_right]',
        'puserconstant_left.VALUE = POBJECT n_left',
        'puserconstant_right.VALUE = POBJECT n_right', 'n_left =/= n_right',
        'puserconstant_left.CLASS = PVINSTANCE n_left porigin_left',
        'puserconstant_right.CLASS = PVINSTANCE n_right porigin_right',
        '$global_new_record(S_fresh.CONSTANTOBJECTS,n_right) = (pconstantobject_right)',
        '$global_new_completed(S_fresh,pconstantobject_right)',
        'pconstantobject_right.SITE = porigin_right',
        '$dynamic_define_value_class(S_fresh,POBJECT n_right) = (PVINSTANCE n_right porigin_right)',
        '~$constant_value_class_valid(S_fresh,POBJECT n_right,PVSTDCLASS n_right porigin_right)',
        '$lookup(S_fresh.ENV,$ptascii("cell")) = (n_cell)',
        'n_cell <- S_fresh.REFCELLS',
        'S_fresh.STORE[n_cell] = DEFINED (POBJECT n_right)',
        'S_fresh.ARRAYS[n_input].ITEMS = ' + input_items,
        f'S_fresh.ARRAYS[n_input_child].ITEMS = [ENTRY (KSTRING {leaf}) (ALIAS n_cell)]',
        *define.property_value('S_fresh', 'n_left', 17, 'left_start'),
        *define.property_value('S_fresh', 'n_right', 23, 'right_start'),
        # Pure receipt controls are never driven.
        'S_missing = S_fresh[.CONSTANTOBJECTS = eps]',
        '$dynamic_define_value_class(S_missing,POBJECT n_right) = eps',
        'S_incomplete = S_fresh[.CONSTANTOBJECTS = $global_new_record_put(S_fresh.CONSTANTOBJECTS,pconstantobject_right[.COMPLETE = false])]',
        '$dynamic_define_value_class(S_incomplete,POBJECT n_right) = eps',
        'S_bad_site = S_fresh[.CONSTANTOBJECTS = $global_new_record_put(S_fresh.CONSTANTOBJECTS,pconstantobject_right[.SITE = pconfigcall_fresh.SITE])]',
        '$dynamic_define_value_class(S_bad_site,POBJECT n_right) = eps',
        'S_dead = S_fresh[.ALLOCATIONS = $destruction_node_delete(S_fresh.ALLOCATIONS,HOBJECT n_right)]',
        '$dynamic_define_value_class(S_dead,POBJECT n_right) = eps',
        'n_fresh_before = |S_fresh.ARRAYS|',
        '$heap_owners($heap_graph(S_fresh),HOBJECT n_right) = 2',
        *common.step('S_registered', 'S_fresh'),
        *reach('S_bound', 'S_registered', 4),
        'S_bound.TODO = ptask_fresh*',
        '$user_constant_at(S_bound.USERCONSTANTS,' + text(TARGET) + ') = (puserconstant_tree)',
        'S_bound.USERCONSTANTS = S_fresh.USERCONSTANTS ++ [puserconstant_tree]',
        'puserconstant_tree.VALUE = PARRAY n_stored',
        'n_stored_child = n_fresh_before', 'n_stored = $(n_fresh_before + 1)',
        'parray_child = ' + child, 'parray_stored = ' + root('n_stored_child'),
        'S_bound.ARRAYS = S_fresh.ARRAYS ++ [parray_child,parray_stored]',
        f'pvalueclass_child = PVARRAY false ([(KSTRING {leaf},PVINSTANCE n_right porigin_right)])',
        f'pvalueclass_tree = PVARRAY false ([(KSTRING {head},PVINSTANCE n_right porigin_right),(KSTRING {nested},pvalueclass_child)])',
        'puserconstant_tree.CLASS = pvalueclass_tree',
        'S_bound.OBJECTS = S_fresh.OBJECTS', 'S_bound.STORE = S_fresh.STORE',
        'S_bound.CONSTANTOBJECTS = S_fresh.CONSTANTOBJECTS',
        '$heap_owners($heap_graph(S_bound),HOBJECT n_right) = 4',
        # Reach the actual later duplicate after the caller retained a query.
        *define.reach('S', 'S_bound', 1, TARGET),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.NAMED', 'pconfigcall.SELECTION = (n_selection)',
        'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        '$dynamic_define_values(pconfigcall) = ((' + text(TARGET) + ',PARRAY n_input))',
        'S.USERCONSTANTS = S_bound.USERCONSTANTS',
        'n_constants = |S.USERCONSTANTS|', 'n_constants = 3',
        '$dynamic_array_duplicate_call_valid(S,pconfigcall,n_constants)',
        'S.STORE[n_cell] = DEFINED (POBJECT n_right)',
        'n_before = |S.ARRAYS|',
        *common.step('S_dispatch', 'S'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass_tree n_constants',
        'n_candidate_child = n_before', 'n_candidate = $(n_before + 1)',
        'parray_candidate = ' + root('n_candidate_child'),
        'S_dispatch.ARRAYS = S.ARRAYS ++ [parray_child,parray_candidate]',
        '$task_nodes(perrorcall.RESUME) = [HARRAY n_candidate,HARRAY n_input]',
        '$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_candidate,pvalueclass_tree,n_constants)',
        '$heap_owners($heap_graph(S_dispatch),HOBJECT n_right) = 6',
        '$heap_edge_owners(HOBJECT n_right,$heap_graph(S_dispatch).EDGES,[HARRAY n_candidate,HARRAY n_candidate_child]) = 2',
        *reach('S_entered', 'S_dispatch', 0), *reach('S_throw', 'S_entered', 1),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_throw*',
        'perrorcall_throw.RESUME = perrorcall.RESUME',
        'S_throw.STORE[n_cell] = DEFINED (POBJECT n_left)',
        'S_throw.CONSTANTOBJECTS = S.CONSTANTOBJECTS',
        '$dynamic_array_duplicate_valid(S_throw,pconfigcall,n_candidate,pvalueclass_tree,n_constants)',
        'S_throw.ARRAYS[n_stored] = parray_stored',
        'S_throw.ARRAYS[n_stored_child] = parray_child',
        'S_throw.ARRAYS[n_candidate] = parray_candidate',
        'S_throw.ARRAYS[n_candidate_child] = parray_child',
        *define.property_value('S_throw', 'n_left', 17, 'left_throw'),
        *define.property_value('S_throw', 'n_right', 41, 'right_throw'),
        '$user_constant_at(S_throw.USERCONSTANTS,$ptascii("V73_REVIEW_SIDE")) = (puserconstant_side)',
        'S_throw.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant_side]',
        'puserconstant_side.VALUE = PINT 31',
        '$throwable_field(S_throw,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_throw.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_trace_api))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_api].ITEMS,KSTRING ($ptascii("args"))) = (DIRECT (PARRAY n_trace_args))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_args].ITEMS,KINT 1) = (DIRECT (PARRAY n_input))',
        '$entry_lookup(S_throw.ARRAYS[n_trace_args].ITEMS,KINT 2) = (DIRECT (PBOOL false))',
        '$heap_owners($heap_graph(S_throw),HARRAY n_input) = 3',
        '$heap_owners($heap_graph(S_throw),HOBJECT n_right) = 5',
        '$heap_owners($heap_graph(S_throw),HOBJECT n_left) = 2',
        '~(n_right <- S_throw.DESTRUCTION.CALLED)',
        '~(n_left <- S_throw.DESTRUCTION.CALLED)',
        *common.step('S_drop', 'S_throw'),
        *reach('S_after', 'S_drop', 3),
        'S_after.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
        '~(HARRAY n_candidate <- S_after.ALLOCATIONS)',
        '~(HARRAY n_candidate_child <- S_after.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_after),HARRAY n_input) = 2',
        '$heap_owners($heap_graph(S_after),HOBJECT n_right) = 3',
        '$heap_owners($heap_graph(S_after),HOBJECT n_left) = 2',
        '$heap_edge_owners(HOBJECT n_right,$heap_graph(S_after).EDGES,[HARRAY n_stored,HARRAY n_stored_child]) = 2',
        '~(n_right <- S_after.DESTRUCTION.CALLED)',
        *reach('S_bucket', 'S_after', 2),
        '$lookup(S_bucket.ENV,$ptascii("row")) = (n_row_cell)',
        'S_bucket.STORE[n_row_cell] = DEFINED (PARRAY n_row_copy)',
        'n_row_copy =/= n_stored',
        f'$entry_lookup(S_bucket.ARRAYS[n_row_copy].ITEMS,KSTRING {nested}) = (DIRECT (PARRAY n_row_child))',
        'n_row_child =/= n_stored_child',
        '$lookup(S_bucket.ENV,$ptascii("slot")) = (n_slot)',
        f'$entry_lookup(S_bucket.ARRAYS[n_row_child].ITEMS,KSTRING {leaf}) = (ALIAS n_slot)',
        'S_bucket.STORE[n_slot] = DEFINED (POBJECT n_left)',
        'S_bucket.ARRAYS[n_stored] = parray_stored',
        'S_bucket.ARRAYS[n_stored_child] = parray_child',
        *define.property_value('S_bucket', 'n_right', 41, 'right_bucket'),
        *define.finish('S_bucket', stdout),
        'S_final.USERCONSTANTS = S_throw.USERCONSTANTS',
        'S_final.CONSTANTOBJECTS = S_fresh.CONSTANTOBJECTS',
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 1',
        '$heap_owners($heap_graph(S_final),HOBJECT n_right) = 3',
        'n_left <- S_final.DESTRUCTION.CALLED',
        'n_right <- S_final.DESTRUCTION.CALLED',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)',
        '~(HARRAY n_input_child <- S_final.ALLOCATIONS)',
        '~(HARRAY n_row_copy <- S_final.ALLOCATIONS)',
        '~(HARRAY n_row_child <- S_final.ALLOCATIONS)',
        '~(HCELL n_cell <- S_final.ALLOCATIONS)',
        '~(HCELL n_slot <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)',
        'S_final.ARRAYS[n_stored] = parray_stored',
        'S_final.ARRAYS[n_stored_child] = parray_child',
        *define.property_value('S_final', 'n_left', 17, 'left_final'),
        *define.property_value('S_final', 'n_right', 41, 'right_final')]
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
