#!/usr/bin/env python3
"""Both the rejected snapshot and changed raw leaf retire before the callee."""
from pathlib import Path

import define_certified_instance_protocol as instance
import define_runtime_closure_protocol as runtime
import define_stdclass_array_duplicate_review_protocol as prior
import define_owned_array_order_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
TARGET = 'V94_ORDER_OLD'
CASE = sources.CASE
PREFIX = define.PREFIX + r'''
dec $test_owned_array_order_front(pstate, nat, nat) : bool
def $test_owned_array_order_front(S,0,n_object) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.OWNER =/= eps
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V94_ORDER_OLD"),PARRAY n_input))
def $test_owned_array_order_front(S,1,n_object) = true
  -- if S.TODO = (DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants) :: ptask_tail*
  -- if $dynamic_define_values(pconfigcall) = (($ptascii("V94_ORDER_OLD"),PARRAY n_input))
def $test_owned_array_order_front(S,2,n_object) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OBJECT = n_object /\ ~pdestructorcall.STORE
def $test_owned_array_order_front(S,n_phase,n_object) = false -- otherwise
dec $test_owned_array_order_seek(pstate, nat, nat, nat) : pstate
def $test_owned_array_order_seek(S,n_phase,n_object,0) = S
def $test_owned_array_order_seek(S,n_phase,n_object,n) = S
  -- if $(n > 0)
  -- if $test_owned_array_order_front(S,n_phase,n_object) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_owned_array_order_seek(S,n_phase,n_object,n) = $test_owned_array_order_seek($drive_steps($test_running(S),1),n_phase,n_object,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_owned_array_order_front(S,n_phase,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase, obj='0'):
    return [f'{state}_found = $test_owned_array_order_seek({start},{phase},{obj},1500)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_owned_array_order_front({state},{phase},{obj})', *common.public(state)]


def checks(initial, stdout):
    assert stdout == b'B|N|H|2|D|41|held|D|53|held|F|gone|17|A|'
    leaf = text('leaf')
    values = [*initial, *reach('S','S_initial',0),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        'pconfigcall.OWNER = (n_callee)', 'pconfigcall.SELECTION = (0)',
        'S.SELECTEDCALLS = [pselectedcall]',
        'pselectedcall.OWNER = (n_callee)', 'pselectedcall.ORIGINAL = eps',
        '$selected_entry_source_valid(S,pselectedcall)',
        '$dynamic_owned_define_header(S,pconfigcall)',
        '$dynamic_array_duplicate_call_valid(S,pconfigcall,1)',
        '$dynamic_define_values(pconfigcall) = ((' + text(TARGET) + ',PARRAY n_input))',
        '$lookup(S.ENV,$ptascii("call")) = (n_call)',
        '$lookup(S.ENV,$ptascii("source")) = (n_source)',
        '$lookup(S.ENV,$ptascii("box")) = (n_box_cv)',
        '$lookup(S.ENV,$ptascii("weak")) = (n_weak_cv)',
        'S.STORE[n_call] = DEFINED PNULL', 'S.STORE[n_source] = DEFINED PNULL',
        'S.STORE[n_box_cv] = DEFINED (POBJECT n_box)',
        'S.STORE[n_weak_cv] = DEFINED (POBJECT n_weak)',
        'S.OBJECTS[n_callee] = INTRINSICCLOSURE INTRINSIC_DEFINE',
        'S.OBJECTS[n_weak] = WEAKREFERENCE (n_callee)',
        '$node_children(S,HOBJECT n_weak) = eps',
        '$objectprops_at(S.OBJECTPROPS,n_box) = (ppropertyslot_box*)',
        '$property_slot_at(ppropertyslot_box*,$ptascii("leaf")) = (ppropertyslot_leaf)',
        'ppropertyslot_leaf.STATE = PROP_VALUE (ALIAS n_cell)',
        f'S.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {leaf}) (ALIAS n_cell)]',
        'S.STORE[n_cell] = DEFINED (POBJECT n_old)',
        '$heap_owners($heap_graph(S),HOBJECT n_old) = 1',
        '$heap_owners($heap_graph(S),HCELL n_cell) = 2',
        '$heap_owners($heap_graph(S),HARRAY n_input) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_callee) = 1',
        '$weakref_get(S,n_weak) = POBJECT n_callee',
        *instance.property_value('S','n_old',41,'old_initial'),
        'S.USERCONSTANTS = [puserconstant_old]',
        'puserconstant_old.NAME = ' + text(TARGET),
        'puserconstant_old.VALUE = PINT 17', 'puserconstant_old.CLASS = PVSCALAR',
        'n_candidate = |S.ARRAYS|',
        '$test_outputs(S.EVENTS) = ($ptascii("B|N|"))',
        *common.step('S_dispatch','S'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_initial*',
        'perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass 1',
        f'parray_candidate = $array_insert($array_empty(),KSTRING {leaf},DIRECT (POBJECT n_old))',
        f'pvalueclass = PVARRAY false ([(KSTRING {leaf},PVOBJECT)])',
        'S_dispatch.ARRAYS = S.ARRAYS ++ [parray_candidate]',
        '$task_nodes(perrorcall.RESUME) = [HARRAY n_candidate,HARRAY n_input,HOBJECT n_callee]',
        '$heap_owners($heap_graph(S_dispatch),HOBJECT n_old) = 2',
        # The returning handler replaces the referenced property, then retires its box.
        *reach('S_marker','S_dispatch',1),
        'S_marker.TODO = (DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass 1) :: ptask_marker*',
        'S_marker.STORE[n_box_cv] = DEFINED PNULL',
        'S_marker.STORE[n_cell] = DEFINED (POBJECT n_new)', 'n_new =/= n_old',
        'S_marker.ARRAYS[n_candidate] = parray_candidate',
        'S_marker.ARRAYS[n_input] = S.ARRAYS[n_input]',
        '~(HOBJECT n_box <- S_marker.ALLOCATIONS)',
        '$dynamic_array_duplicate_valid(S_marker,pconfigcall,n_candidate,pvalueclass,1)',
        '$heap_owners($heap_graph(S_marker),HOBJECT n_old) = 1',
        '$heap_owners($heap_graph(S_marker),HOBJECT n_new) = 1',
        '$heap_owners($heap_graph(S_marker),HCELL n_cell) = 1',
        '$heap_edge_owners(HOBJECT n_old,$heap_graph(S_marker).EDGES,[HARRAY n_candidate]) = 1',
        '$heap_edge_owners(HOBJECT n_new,$heap_graph(S_marker).EDGES,[HCELL n_cell]) = 1',
        '$heap_edge_owners(HCELL n_cell,$heap_graph(S_marker).EDGES,[HARRAY n_input]) = 1',
        '$heap_owners($heap_graph(S_marker),HOBJECT n_callee) = 1',
        *instance.property_value('S_marker','n_old',41,'old_marker'),
        *instance.property_value('S_marker','n_new',53,'new_marker'),
        'S_marker.USERCONSTANTS = S.USERCONSTANTS',
        '$test_outputs(S_marker.EVENTS) = ($ptascii("B|N|H|2|"))',
        'S_pause = $drive_steps(S_marker,0)',
        'S_pause = S_marker[.COMPLETION = BUDGET]', '$test_running(S_pause) = S_marker',
        *common.step('S_drop','S_marker'), *common.public('S_drop'),
        '$drive_steps($test_running(S_pause),1) = S_drop_found',
        'S_drop.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_drop) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_marker*',
        '$destruction_job_nodes(pdestructionrelease_drop.JOBS) = [HARRAY n_candidate,HARRAY n_input,HOBJECT n_callee]',
        'pdestructionoperation.SOURCE = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass 1',
        'pdestructionoperation.VALUE = KNOWN (PBOOL false)',
        'pdestructionoperation.PENDING = eps',
        # Snapshot child A is selected while the changed raw leaf B still exists.
        *reach('S_old','S_drop',2,'n_old'),
        'S_old.TODO = (DESTRUCTOR_ENTER pdestructorcall_old) :: (DESTRUCTOR_RELEASE pdestructionrelease_old) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_marker*',
        'pdestructorcall_old.OBJECT = n_old', '~pdestructorcall_old.STORE',
        'pdestructorcall_old.OPERATION = (pdestructionoperation)',
        'pdestructorcall_old.PENDING = eps',
        '$destructor_enter_valid(S_old,pdestructorcall_old)',
        '$destruction_job_nodes(pdestructionrelease_old.JOBS) = [HARRAY n_input,HOBJECT n_callee]',
        '~(HARRAY n_candidate <- S_old.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_old),HOBJECT n_old) = 2',
        '$heap_owners($heap_graph(S_old),HOBJECT n_new) = 1',
        '$heap_owners($heap_graph(S_old),HOBJECT n_callee) = 1',
        '$weakref_get(S_old,n_weak) = POBJECT n_callee',
        '$test_outputs(S_old.EVENTS) = ($ptascii("B|N|H|2|"))',
        # Raw ARRAY/CELL teardown selects B before consuming the callee job.
        *reach('S_new','S_old',2,'n_new'),
        'S_new.TODO = (DESTRUCTOR_ENTER pdestructorcall_new) :: (DESTRUCTOR_RELEASE pdestructionrelease_new) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_marker*',
        'pdestructorcall_new.OBJECT = n_new', '~pdestructorcall_new.STORE',
        'pdestructorcall_new.OPERATION = (pdestructionoperation)',
        'pdestructorcall_new.PENDING = eps',
        '$destructor_enter_valid(S_new,pdestructorcall_new)',
        '$destruction_job_nodes(pdestructionrelease_new.JOBS) = [HOBJECT n_callee]',
        '~(HARRAY n_input <- S_new.ALLOCATIONS)',
        '~(HCELL n_cell <- S_new.ALLOCATIONS)',
        '~(HOBJECT n_old <- S_new.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_new),HOBJECT n_new) = 2',
        '$heap_owners($heap_graph(S_new),HOBJECT n_callee) = 1',
        '$weakref_get(S_new,n_weak) = POBJECT n_callee',
        'S_new.USERCONSTANTS = S.USERCONSTANTS',
        '$test_outputs(S_new.EVENTS) = ($ptascii("B|N|H|2|D|41|held|"))',
        *common.reach('S_query','S_new',0,TARGET), *common.public('S_query'),
        '$lookup(S_query.ENV,$ptascii("result")) = (n_result)',
        'S_query.STORE[n_result] = DEFINED (PBOOL false)',
        '$weakref_get(S_query,n_weak) = PNULL',
        '~(HOBJECT n_callee <- S_query.ALLOCATIONS)',
        '~(HOBJECT n_new <- S_query.ALLOCATIONS)',
        'S_query.USERCONSTANTS = S.USERCONSTANTS',
        '$selected_entry_source_valid(S_query,pselectedcall)',
        '$test_outputs(S_query.EVENTS) = ($ptascii("B|N|H|2|D|41|held|D|53|held|F|gone|"))',
        *define.finish('S_query',stdout),
        'S_final.USERCONSTANTS = S.USERCONSTANTS',
        'S_final.SELECTEDCALLS = [pselectedcall]',
        '~(HOBJECT n_callee <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_weak <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_box <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_old <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_new <- S_final.ALLOCATIONS)',
        '~(HARRAY n_candidate <- S_final.ALLOCATIONS)',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)',
        '~(HCELL n_cell <- S_final.ALLOCATIONS)']
    return values


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = runtime.packet_process


def process(command, directory, timeout, cwd):
    if directory.parent.name == CASE:
        timeout = 240
    return packet_process(command, directory, timeout, cwd)


packet.process = process
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    raise SystemExit(0 if packet.main() else 1)
