#!/usr/bin/env python3
"""Reached owned array snapshots, private child retirement and query COW."""
import argparse
from pathlib import Path
import sys

import define_runtime_closure_protocol as real
import define_runtime_object_protocol as runtime
import define_owned_closure_protocol as owned
import define_owned_array_sources as sources

define, packet, common = owned.define, owned.packet, owned.common
prior, instance = owned.prior, runtime.instance
ROOT, text, term = owned.ROOT, owned.text, owned.term
DIRECT = sources.DIRECT
assert runtime.PREFIX.startswith(define.PREFIX)
assert real.PREFIX.startswith(define.PREFIX)
PREFIX = runtime.PREFIX + real.PREFIX[len(define.PREFIX):] + r'''
dec $test_owned_array_front(pstate, nat, preqbytes) : bool
def $test_owned_array_front(S,0,preqbytes) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.INDEX = 0
def $test_owned_array_front(S,1,preqbytes) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.INDEX = 1 /\ pconfigcall.NAMED
  -- if pconfigcall.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (PARRAY n_input))]
def $test_owned_array_front(S,2,preqbytes) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.OWNER =/= eps
  -- if $dynamic_define_values(pconfigcall) = ((preqbytes,PARRAY n_input))
def $test_owned_array_front(S,3,preqbytes) = true
  -- if S.TODO = (DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants) :: ptask_tail*
  -- if $dynamic_define_values(pconfigcall) = ((preqbytes,PARRAY n_input))
def $test_owned_array_front(S,4,preqbytes) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if ~pdestructorcall.STORE
def $test_owned_array_front(S,n_phase,preqbytes) = false -- otherwise
dec $test_owned_array_seek(pstate, nat, preqbytes, nat) : pstate
def $test_owned_array_seek(S,n_phase,preqbytes,0) = S
def $test_owned_array_seek(S,n_phase,preqbytes,n) = S
  -- if $(n > 0)
  -- if $test_owned_array_front(S,n_phase,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_owned_array_seek(S,n_phase,preqbytes,n) = $test_owned_array_seek($drive_steps($test_running(S),1),n_phase,preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_owned_array_front(S,n_phase,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase, target):
    return [f'{state}_found = $test_owned_array_seek({start},{phase},{text(target)},1500)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_owned_array_front({state},{phase},{text(target)})', *common.public(state)]


def direct(initial, stdout):
    target, edge = 'V94_ARRAY_OWNED', text('edge')
    values = [*initial, *reach('S_capture','S_initial',0,target),
        'S_capture.TODO = (CONFIG_ARGS pconfigcall_capture) :: ptask_capture*',
        *owned.receipt('S_capture','pconfigcall_capture','first',0,0),
        'S_capture.SELECTEDCALLS = [pselectedcall_first]',
        'S_capture.USERCONSTANTS = eps', 'pconfigcall_capture.SENT = eps',
        '$lookup(S_capture.ENV,$ptascii("call")) = (n_call)',
        '$lookup(S_capture.ENV,$ptascii("weak")) = (n_weak_cv)',
        '$lookup(S_capture.ENV,$ptascii("payload")) = (n_payload)',
        '$lookup(S_capture.ENV,$ptascii("cell")) = (n_cell)',
        '$lookup(S_capture.ENV,$ptascii("raw")) = (n_raw)',
        '$lookup(S_capture.ENV,$ptascii("calls")) = (n_calls)',
        '$lookup(S_capture.ENV,$ptascii("destroyed")) = (n_destroyed)',
        'S_capture.STORE[n_call] = DEFINED (POBJECT n_first)',
        'S_capture.STORE[n_weak_cv] = DEFINED (POBJECT n_weak_first)',
        'S_capture.OBJECTS[n_weak_first] = WEAKREFERENCE (n_first)',
        'S_capture.STORE[n_payload] = DEFINED (PARRAY n_input)',
        'S_capture.STORE[n_raw] = DEFINED (PARRAY n_input)',
        'S_capture.STORE[n_cell] = DEFINED (POBJECT n_left)',
        f'S_capture.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {edge}) (ALIAS n_cell)]',
        'S_capture.ARRAYS[n_input].NEXT = 91',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_first) = 2',
        *reach('S_args','S_capture',1,target),
        'S_args.TODO = (CONFIG_ARGS pconfigcall_args) :: ptask_capture*',
        'pconfigcall_args.OWNER = (n_first)', 'pconfigcall_args.SELECTION = (0)',
        'pconfigcall_args.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (PARRAY n_input))]',
        'S_args.STORE[n_cell] = DEFINED (POBJECT n_left)',
        *instance.property_value('S_args','n_left',7,'before_name'),
        *reach('S','S_args',2,target),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        'pconfigcall.OWNER = (n_first)', 'pconfigcall.SELECTION = (0)',
        '|pconfigcall.SENT| = 2', 'pconfigcall.NAMED',
        '$dynamic_owned_define_header(S,pconfigcall)',
        '~$dynamic_owned_define_valid(S,pconfigcall)',
        '$dynamic_array_call_valid(S,pconfigcall)',
        '$dynamic_define_values(pconfigcall) = (($ptascii("V94_ARRAY_OWNED"),PARRAY n_input))',
        'S.STORE[n_call] = DEFINED pvalue_call', '$string_bytes(pvalue_call) = ($ptascii("constant"))',
        'S.STORE[n_payload] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        'S.ARRAYS[n_caller].ITEMS = [ENTRY (KINT 90) (DIRECT (PINT 31))]',
        'S.STORE[n_raw] = DEFINED (PARRAY n_input)',
        'S.STORE[n_cell] = DEFINED (POBJECT n_left)',
        *runtime.ordinary('S','n_left','left'),
        *instance.property_value('S','n_left',19,'after_name'),
        '$heap_owners($heap_graph(S),HOBJECT n_first) = 1',
        '$weakref_get(S,n_weak_first) = POBJECT n_first',
        'pconfigcall_object = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,1,KNOWN (POBJECT n_left))]',
        '$dynamic_owned_define_header(S,pconfigcall_object)',
        '$dynamic_owned_define_valid(S,pconfigcall_object)',
        '~$dynamic_array_call_valid(S,pconfigcall_object)',
        '~$dynamic_owned_define_header(S,pconfigcall[.OWNER = eps])',
        '~$dynamic_owned_define_header(S,pconfigcall[.SELECTION = eps])',
        'n_root = |S.ARRAYS|',
        f'parray_root = $array_insert($array_empty(),KSTRING {edge},DIRECT (POBJECT n_left))',
        f'pvalueclass_tree = PVARRAY false ([(KSTRING {edge},PVOBJECT)])',
        '$dynamic_array_value(S,PARRAY n_input,eps,true) = ((S_copy,PARRAY n_root,pvalueclass_tree))',
        'S_copy.ARRAYS = S.ARRAYS ++ [parray_root]',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        '$test_running(S_pause) = S',
        '$destructor_operational(S)',
        *common.step('S_registered','S'), *common.public('S_registered'),
        '$drive_steps($test_running(S_pause),1) = S_registered_found',
        'S_registered.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_first) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_first) :: ptask_initial*',
        'pdestructionrelease_first.JOBS = [DESTRUCTION_VALUE (HARRAY n_input),DESTRUCTION_VALUE (HOBJECT n_first)]',
        'pdestructionoperation_first.SOURCE = CONFIG_INVOKE pconfigcall',
        'pdestructionoperation_first.VALUE = KNOWN (PBOOL true)',
        'pdestructionoperation_first.PENDING = eps',
        'S_registered.RESULT = KNOWN PNULL',
        'S_registered.USERCONSTANTS = [puserconstant_row]',
        'puserconstant_row.NAME = $ptascii("V94_ARRAY_OWNED")',
        'puserconstant_row.ORIGIN = pconfigcall.SITE',
        'puserconstant_row.VALUE = PARRAY n_root', 'puserconstant_row.CLASS = pvalueclass_tree',
        'S_registered.ARRAYS = S_copy.ARRAYS',
        '$heap_owners($heap_graph(S_registered),HOBJECT n_first) = 1',
        'S_row_found = $test_runtime_object_delivery_seek(S_registered,100)',
        r'S_row_found.COMPLETION = NORMAL \/ S_row_found.COMPLETION = BUDGET',
        'S_row = $test_running(S_row_found)', *common.public('S_row'),
        'S_row.TODO = ptask_initial*', 'S_row.RESULT = KNOWN (PBOOL true)',
        '~(HOBJECT n_first <- S_row.ALLOCATIONS)',
        '$weakref_get(S_row,n_weak_first) = PNULL',
        'S_row.USERCONSTANTS = S_registered.USERCONSTANTS',
        'S_row.SELECTEDCALLS = [pselectedcall_first]',
        '$selected_entry_source_valid(S_row,pselectedcall_first)',
        *common.reach('S_query','S_row',0,target), *common.public('S_query'),
        'S_query.STORE[n_cell] = DEFINED PNULL',
        'S_query.USERCONSTANTS = S_row.USERCONSTANTS',
        '$dynamic_global_constant_value(S_query,$ptascii("V94_ARRAY_OWNED")) = (PARRAY n_root)',
        *real.unset('S_observed','S_query','stored'),
        '$lookup(S_observed.ENV,$ptascii("stored")) = (n_stored_cv)',
        '$lookup(S_observed.ENV,$ptascii("again")) = (n_again_cv)',
        '$lookup(S_observed.ENV,$ptascii("object")) = (n_object_cv)',
        'S_observed.STORE[n_stored_cv] = DEFINED (PARRAY n_query_copy)',
        'S_observed.STORE[n_again_cv] = DEFINED (PARRAY n_root)',
        'S_observed.STORE[n_object_cv] = DEFINED (POBJECT n_left)',
        'n_query_copy =/= n_root',
        f'$entry_lookup(S_observed.ARRAYS[n_query_copy].ITEMS,KSTRING {edge}) = (pitem_query_edge)',
        '$entry_value(S_observed,pitem_query_edge) = PNULL',
        '$array_append_key(S_observed.ARRAYS[n_query_copy]) = KINT 1',
        '$array_append_key(S_observed.ARRAYS[n_input]) = KINT 92',
        'S_observed.ARRAYS[n_root] = parray_root',
        *instance.property_value('S_observed','n_left',23,'shared'),
        '$heap_owners($heap_graph(S_observed),HOBJECT n_left) = 2',
        '$test_outputs(S_observed.EVENTS) = '+term(b'B|N|1|held|T|gone|constant|31|19|same|23|history|'),
        *reach('S_dup','S_observed',2,target),
        'S_dup.TODO = (CONFIG_INVOKE pconfigcall_dup) :: ptask_dup*',
        'pconfigcall_dup.OWNER = (n_second)', 'pconfigcall_dup.SELECTION = (1)',
        'n_first =/= n_second',
        'S_dup.SELECTEDCALLS = [pselectedcall_first,pselectedcall_second]',
        'pselectedcall_second.OWNER = (n_second)',
        '$selected_entry_source_valid(S_dup,pselectedcall_second)',
        '$dynamic_array_duplicate_call_valid(S_dup,pconfigcall_dup,1)',
        '$lookup(S_dup.ENV,$ptascii("cell")) = (n_cell_dup)',
        '$lookup(S_dup.ENV,$ptascii("payload")) = (n_payload_dup)',
        '$lookup(S_dup.ENV,$ptascii("candidate")) = (n_candidate_cv)',
        'n_cell_dup =/= n_cell', 'n_payload_dup =/= n_payload',
        'S_dup.STORE[n_cell_dup] = DEFINED (POBJECT n_right)',
        'S_dup.STORE[n_candidate_cv] = DEFINED PNULL',
        'S_dup.STORE[n_weak_cv] = DEFINED (POBJECT n_weak_second)',
        'S_dup.OBJECTS[n_weak_second] = WEAKREFERENCE (n_second)',
        '$dynamic_define_values(pconfigcall_dup) = (($ptascii("V94_ARRAY_OWNED"),PARRAY n_dup_input))',
        f'S_dup.ARRAYS[n_dup_input].ITEMS = [ENTRY (KSTRING {edge}) (ALIAS n_cell_dup)]',
        *instance.property_value('S_dup','n_right',41,'right'),
        'n_private = |S_dup.ARRAYS|',
        *reach('S_marker','S_dup',3,target),
        'S_marker.TODO = (DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall_dup n_private pvalueclass_tree 1) :: ptask_marker*',
        f'S_marker.ARRAYS[n_private].ITEMS = [ENTRY (KSTRING {edge}) (DIRECT (POBJECT n_right))]',
        'S_marker.STORE[n_cell_dup] = DEFINED PNULL',
        'S_marker.STORE[n_calls] = DEFINED (PINT 1)',
        'S_marker.STORE[n_destroyed] = DEFINED (PINT 0)',
        '$heap_owners($heap_graph(S_marker),HOBJECT n_right) = 1',
        '$heap_owners($heap_graph(S_marker),HOBJECT n_second) = 1',
        '$weakref_get(S_marker,n_weak_second) = POBJECT n_second',
        'S_marker.USERCONSTANTS = S_row.USERCONSTANTS',
        '$test_outputs(S_marker.EVENTS) = '+term(b'B|N|1|held|T|gone|constant|31|19|same|23|history|N|2|held|H|2|23|0|held|'),
        *reach('S_free','S_marker',4,target),
        'S_free.TODO = (DESTRUCTOR_ENTER pdestructorcall_free) :: ptask_free*',
        'pdestructorcall_free.OBJECT = n_right', '~pdestructorcall_free.STORE',
        'pdestructorcall_free.OPERATION = (pdestructionoperation_dup)',
        'pdestructionoperation_dup.SOURCE = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall_dup n_private pvalueclass_tree 1',
        'pdestructionoperation_dup.VALUE = KNOWN (PBOOL false)',
        'pdestructionoperation_dup.PENDING = eps',
        '$destructor_enter_valid(S_free,pdestructorcall_free)',
        '~(HARRAY n_private <- S_free.ALLOCATIONS)',
        'HOBJECT n_second <- S_free.ALLOCATIONS',
        '$heap_owners($heap_graph(S_free),HOBJECT n_second) = 1',
        '$weakref_get(S_free,n_weak_second) = POBJECT n_second',
        '$heap_owners($heap_graph(S_free),HOBJECT n_right) = 2',
        '$test_outputs(S_free.EVENTS) = $test_outputs(S_marker.EVENTS)',
        *common.reach('S_last_query','S_free',0,target), *common.public('S_last_query'),
        '~(HOBJECT n_second <- S_last_query.ALLOCATIONS)',
        '~(HOBJECT n_right <- S_last_query.ALLOCATIONS)',
        '$weakref_get(S_last_query,n_weak_second) = PNULL',
        'S_last_query.STORE[n_calls] = DEFINED (PINT 1)',
        'S_last_query.STORE[n_destroyed] = DEFINED (PINT 1)',
        'S_last_query.USERCONSTANTS = S_row.USERCONSTANTS',
        '$test_outputs(S_last_query.EVENTS) = '+term(b'B|N|1|held|T|gone|constant|31|19|same|23|history|N|2|held|H|2|23|0|held|D|41|held|F|gone|'),
        *instance.store('S_store','S_last_query','n_left',1,stdout[:-5]),
        *define.finish('S_store_selected',stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_final.SELECTEDCALLS = [pselectedcall_first,pselectedcall_second]',
        '$selected_log_valid(S_final,S_final.SELECTEDCALLS,0)',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 1',
        '~(HOBJECT n_first <- S_final.ALLOCATIONS)', '~(HOBJECT n_second <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_right <- S_final.ALLOCATIONS)',
        *instance.property_value('S_final','n_left',23,'final')]
    return values


def flags():
    values=[]
    for label,value in [('null','PNULL'),('quiet','PINT 0'),('true','PBOOL true')]:
        call='pconfigcall_'+label
        negated = '' if label == 'true' else '~'
        values += [f'{call} = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN ({value}))]',
            f'$config_invoke_valid(S,{call})',
            f'$dynamic_define_values({call}) = (($ptascii("V94_NESTED_OWNED"),PARRAY n_input))',
            f'{negated}$dynamic_owned_define_header(S,{call})',
            f'{negated}$dynamic_array_call_valid(S,{call})']
    return values


def nested(initial, stdout):
    target,edge,key,leaf='V94_NESTED_OWNED',text('edge'),text('nested'),text('leaf')
    return [*initial, *reach('S','S_initial',2,target),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        *owned.receipt('S','pconfigcall','first',0,0),
        '$dynamic_owned_define_header(S,pconfigcall)', '~$dynamic_owned_define_valid(S,pconfigcall)',
        '$dynamic_array_call_valid(S,pconfigcall)',
        '$dynamic_define_values(pconfigcall) = (($ptascii("V94_NESTED_OWNED"),PARRAY n_input))',
        '$lookup(S.ENV,$ptascii("cell")) = (n_cell)',
        '$lookup(S.ENV,$ptascii("input")) = (n_input_cv)',
        '$lookup(S.ENV,$ptascii("raw")) = (n_raw_cv)',
        '$lookup(S.ENV,$ptascii("weak")) = (n_weak_cv)',
        'S.STORE[n_cell] = DEFINED (PINT 23)',
        'S.STORE[n_raw_cv] = DEFINED (PARRAY n_input)',
        'S.STORE[n_input_cv] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        'S.STORE[n_weak_cv] = DEFINED (POBJECT n_weak)',
        'S.OBJECTS[n_weak] = WEAKREFERENCE (n_first)',
        f'S.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {edge}) (ALIAS n_cell),ENTRY (KSTRING {key}) (DIRECT (PARRAY n_source_child))]',
        f'S.ARRAYS[n_source_child].ITEMS = [ENTRY (KSTRING {leaf}) (ALIAS n_cell)]',
        'S.ARRAYS[n_input].NEXT = 91',
        'S.ARRAYS[n_caller] = $array_insert(S.ARRAYS[n_input],KINT 90,DIRECT (PINT 31))',
        '$weakref_get(S,n_weak) = POBJECT n_first',
        *flags(),
        'n_child = |S.ARRAYS|', 'n_root = $(n_child + 1)',
        f'parray_child = $array_insert($array_empty(),KSTRING {leaf},DIRECT (PINT 23))',
        f'parray_root = $array_insert($array_insert($array_empty(),KSTRING {edge},DIRECT (PINT 23)),KSTRING {key},DIRECT (PARRAY n_child))',
        f'pvalueclass_tree = PVARRAY false ([(KSTRING {edge},PVSCALAR),(KSTRING {key},PVARRAY false ([(KSTRING {leaf},PVSCALAR)]))])',
        '$dynamic_array_value(S,PARRAY n_input,eps,true) = ((S_copy,PARRAY n_root,pvalueclass_tree))',
        'S_copy.ARRAYS = S.ARRAYS ++ [parray_child,parray_root]',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]', '$test_running(S_pause) = S',
        '~$destructor_operational(S)',
        *common.step('S_row','S','PBOOL true'),
        '$drive_steps($test_running(S_pause),1) = S_row_found',
        'S_row.TODO = ptask_initial*', '~(HOBJECT n_first <- S_row.ALLOCATIONS)',
        '$weakref_get(S_row,n_weak) = PNULL',
        'S_row.USERCONSTANTS = [puserconstant_row]',
        'puserconstant_row.ORIGIN = pconfigcall.SITE',
        'puserconstant_row.VALUE = PARRAY n_root', 'puserconstant_row.CLASS = pvalueclass_tree',
        'S_row.ARRAYS = S_copy.ARRAYS',
        '$selected_entry_source_valid(S_row,pselectedcall_first)',
        *real.unset('S_observed','S_row','call'),
        '$test_outputs(S_observed.EVENTS) = '+term(stdout),
        '$lookup(S_observed.ENV,$ptascii("stored")) = (n_stored_cv)',
        '$lookup(S_observed.ENV,$ptascii("again")) = (n_again_cv)',
        'S_observed.STORE[n_stored_cv] = DEFINED (PARRAY n_copy_root)',
        'S_observed.STORE[n_again_cv] = DEFINED (PARRAY n_root)',
        'n_copy_root =/= n_root',
        f'$entry_lookup(S_observed.ARRAYS[n_copy_root].ITEMS,KSTRING {key}) = (pitem_copy_nested)',
        '$entry_value(S_observed,pitem_copy_nested) = PARRAY n_copy_child',
        'n_copy_child =/= n_child',
        f'$entry_lookup(S_observed.ARRAYS[n_copy_child].ITEMS,KSTRING {leaf}) = (pitem_copy_leaf)',
        '$entry_value(S_observed,pitem_copy_leaf) = PNULL',
        f'$entry_lookup(S_observed.ARRAYS[n_copy_root].ITEMS,KSTRING {edge}) = (pitem_copy_edge)',
        '$entry_value(S_observed,pitem_copy_edge) = PNULL',
        'S_observed.STORE[n_cell] = DEFINED (PINT 41)',
        'S_observed.ARRAYS[n_root] = parray_root', 'S_observed.ARRAYS[n_child] = parray_child',
        '$array_append_key(S_observed.ARRAYS[n_copy_root]) = KINT 1',
        '$array_append_key(S_observed.ARRAYS[n_input]) = KINT 92',
        '$dynamic_global_constant_value(S_observed,$ptascii("V94_NESTED_OWNED")) = (PARRAY n_root)',
        *define.finish('S_observed',stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_final.ARRAYS[n_root] = parray_root', 'S_final.ARRAYS[n_child] = parray_child',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_child) = 1',
        '~(HCELL n_cell <- S_final.ALLOCATIONS)',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)', '~(HARRAY n_source_child <- S_final.ALLOCATIONS)',
        '~(HARRAY n_caller <- S_final.ALLOCATIONS)', '~(HARRAY n_copy_root <- S_final.ALLOCATIONS)',
        '~(HARRAY n_copy_child <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_first <- S_final.ALLOCATIONS)',
        '$selected_entry_source_valid(S_final,pselectedcall_first)']


def checks(initial, name, stdout):
    return (direct if name == DIRECT else nested)(initial, stdout)


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = real.packet_process


def process(command, directory, timeout, cwd):
    if directory.parent.name in sources.family.CASES:
        timeout = 480 if directory.parent.name == DIRECT else 180
    return packet_process(command, directory, timeout, cwd)


packet.process = process
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--case', choices=sources.family.CASES)
    args, remaining = parser.parse_known_args()
    if args.case:
        sources.family.CASES = {args.case: sources.family.CASES[args.case]}
    sys.argv = [sys.argv[0], *remaining]
    raise SystemExit(0 if packet.main() else 1)
