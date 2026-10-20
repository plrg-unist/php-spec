#!/usr/bin/env python3
"""Reached ordinary object publication, unpinned retirement and array COW."""
import argparse
from pathlib import Path
import sys

import define_certified_instance_protocol as instance
import define_stdclass_array_duplicate_protocol as prior
import define_runtime_object_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
DIRECT = 'runtime-object-publication-and-unpinned-duplicate'
PREFIX = instance.PREFIX + r'''
dec $test_runtime_object_delivery(pstate) : bool
def $test_runtime_object_delivery(S) = (S.RESULT = KNOWN (PBOOL true))
dec $test_runtime_object_delivery_seek(pstate, nat) : pstate
def $test_runtime_object_delivery_seek(S,0) = S
def $test_runtime_object_delivery_seek(S,n) = S
  -- if $(n > 0)
  -- if $test_runtime_object_delivery(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_runtime_object_delivery_seek(S,n) = $test_runtime_object_delivery_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_runtime_object_delivery(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $test_runtime_object_unset(pstate) : bool
def $test_runtime_object_unset(S) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_slot) metadata_slot) :: expression_tail*
  -- if $base64(text_slot) = $ptascii("slot")
  -- if $lookup(S.ENV,$ptascii("again")) =/= eps
def $test_runtime_object_unset(S) = false -- otherwise
dec $test_runtime_object_unset_seek(pstate, nat) : pstate
def $test_runtime_object_unset_seek(S,0) = S
def $test_runtime_object_unset_seek(S,n) = S
  -- if $(n > 0)
  -- if $test_runtime_object_unset(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_runtime_object_unset_seek(S,n) = $test_runtime_object_unset_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_runtime_object_unset(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def ordinary(state, obj, suffix):
    return [f'{state}.OBJECTS[{obj}] = INSTANCE porigin_{suffix}',
        f'$class_at({state}.CLASSES,porigin_{suffix}) = (pclassdesc_{suffix})',
        f'pclassdesc_{suffix}.KIND = "class"', f'~pclassdesc_{suffix}.ABSTRACT',
        f'$class_named({state}.CLASSNAMES,$ptlc(pclassdesc_{suffix}.NAME)) = (porigin_{suffix})',
        f'$global_new_record({state}.CONSTANTOBJECTS,{obj}) = eps',
        f'$dynamic_runtime_object({state},{obj})',
        f'$dynamic_define_value_class({state},POBJECT {obj}) = (PVOBJECT)']


def controls():
    return ['~$global_constant_class_supported(PVOBJECT)',
        '~$global_constant_class_supported(PVARRAY false ([(KSTRING ($ptascii("edge")),PVOBJECT)]))',
        '~$constant_value_class_valid(S,POBJECT n_left,PVINSTANCE n_left pconfigcall.SITE)',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_left)]',
        '$dynamic_define_value_class(S_dead,POBJECT n_left) = eps',
        '~$dynamic_runtime_object(S,|S.OBJECTS|)',
        'S_unresolved = S[.CLASSNAMES = eps]',
        '~$dynamic_runtime_object(S_unresolved,n_left)',
        'S_std = S[.OBJECTS[n_left] = STDINSTANCE]',
        '$dynamic_define_value_class(S_std,POBJECT n_left) = eps',
        'S_closure = S[.OBJECTS[n_left] = INTRINSICCLOSURE INTRINSIC_DEFINE]',
        '$dynamic_define_value_class(S_closure,POBJECT n_left) = eps',
        # An intentionally invalid present receipt cannot become ordinary authority.
        'pconstantobject_bad = {OBJECT n_left,SITE pconfigcall.SITE,DECL pconfigcall.SITE,CLASS porigin_left,PREFIX (|S.DECLARATIONS|),COMPLETE false}',
        'S_incomplete = S[.CONSTANTOBJECTS = [pconstantobject_bad]]',
        '~$dynamic_runtime_object(S_incomplete,n_left)',
        '$dynamic_define_value_class(S_incomplete,POBJECT n_left) = eps']


def direct(initial, stdout):
    values = [*initial, *define.reach('S','S_initial',0,'V84_DIRECT'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        '$dynamic_define_values(pconfigcall) = (($ptascii("V84_DIRECT"),POBJECT n_left))',
        '$config_invoke_valid(S,pconfigcall)', '$dynamic_define_source(S,pconfigcall.SITE)',
        'S.CONSTANTOBJECTS = eps', 'S.CONSTANTSTDOBJECTS = eps', 'S.CONSTANTCLOSURES = eps',
        'S.USERCONSTANTS = eps', *ordinary('S','n_left','left'),
        '$lookup(S.ENV,$ptascii("candidate")) = (n_candidate)',
        '$lookup(S.ENV,$ptascii("api")) = (n_api)',
        '$lookup(S.ENV,$ptascii("calls")) = (n_calls)',
        'S.STORE[n_candidate] = DEFINED (POBJECT n_left)',
        '$heap_owners($heap_graph(S),HOBJECT n_left) = 2',
        *instance.property_value('S','n_left',7,'left_initial'), *controls(),
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        '$test_running(S_pause) = S',
        *common.step('S_row','S','PBOOL true'),
        '$drive_steps($test_running(S_pause),1) = S_row_found',
        'S_row.TODO = ptask_initial*',
        'S_row.USERCONSTANTS = [puserconstant_row]',
        'puserconstant_row.NAME = ($ptascii("V84_DIRECT"))',
        'puserconstant_row.ORIGIN = pconfigcall.SITE',
        'puserconstant_row.VALUE = POBJECT n_left', 'puserconstant_row.CLASS = PVOBJECT',
        'puserconstant_row.READS = eps', 'puserconstant_row.RECEIVES = eps',
        '$heap_owners($heap_graph(S_row),HOBJECT n_left) = 2']
    values += [f'S_row.{f} = S.{f}' for f in
        ['ALLOCATIONS','OBJECTS','OBJECTPROPS','ARRAYS','STORE','CONSTANTOBJECTS','EVENTS']]
    values += ['puserconstant_bad = puserconstant_row[.ORIGIN = PORIGIN 0 eps]',
        '$dynamic_global_constant_value(S_row[.USERCONSTANTS = [puserconstant_bad]],$ptascii("V84_DIRECT")) = eps',
        'puserconstant_bad_class = puserconstant_row[.CLASS = PVINSTANCE n_left pconfigcall.SITE]',
        '~$user_constants_valid(S_row[.USERCONSTANTS = [puserconstant_bad_class]],[puserconstant_bad_class])',
        *define.reach('S_dup','S_row',1,'V84_DIRECT'),
        'S_dup.TODO = (CONFIG_INVOKE pconfigcall_dup) :: ptask_dup*',
        '$dynamic_define_values(pconfigcall_dup) = (($ptascii("V84_DIRECT"),POBJECT n_right))',
        '$named_slot_at(pconfigcall_dup.SENT,2) = NAMED_SENT (KNOWN (PBOOL false))',
        *ordinary('S_dup','n_right','right'), 'n_right =/= n_left',
        'S_dup.USERCONSTANTS = S_row.USERCONSTANTS',
        '$dynamic_constant_duplicate_valid(S_dup,pconfigcall_dup,1)',
        'S_dup.STORE[n_candidate] = DEFINED (POBJECT n_right)',
        'S_dup.STORE[n_calls] = DEFINED (PINT 0)',
        '$lookup(S_dup.ENV,$ptascii("result")) = (n_result)',
        '$heap_owners($heap_graph(S_dup),HOBJECT n_left) = 1',
        '$heap_owners($heap_graph(S_dup),HOBJECT n_right) = 2',
        *instance.property_value('S_dup','n_left',19,'left_duplicate'),
        *instance.property_value('S_dup','n_right',23,'right_duplicate'),
        *common.step('S_dispatch','S_dup'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_dispatch*',
        'perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup 1',
        *define.reach('S_marker','S_dispatch',4,'V84_DIRECT'),
        'S_marker.TODO = (DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup 1) :: ptask_dispatch*',
        'S_marker.STORE[n_candidate] = DEFINED PNULL',
        'S_marker.STORE[n_calls] = DEFINED (PINT 1)',
        'S_marker.STORE[n_api] = DEFINED pvalue_api',
        '$string_bytes(pvalue_api) = ($ptascii("constant"))',
        'S_marker.USERCONSTANTS = S_row.USERCONSTANTS',
        '$heap_owners($heap_graph(S_marker),HOBJECT n_right) = 1',
        *instance.property_value('S_marker','n_right',41,'right_pending'),
        '$test_outputs(S_marker.EVENTS) = ' + term(b'B|T|same|7|19|H|2|'),
        '~(n_right <- S_marker.DESTRUCTION.CALLED)',
        *common.step('S_release','S_marker'),
        'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_dispatch*',
        'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_right)]',
        'pdestructionoperation.SOURCE = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup 1',
        'pdestructionoperation.VALUE = KNOWN (PBOOL false)',
        'pdestructionoperation.PENDING = eps',
        *common.step('S_free','S_release'), *common.public('S_free'),
        'S_free.TODO = (DESTRUCTOR_ENTER pdestructorcall_free) :: ptask_free*',
        'pdestructorcall_free.OBJECT = n_right', '~pdestructorcall_free.STORE',
        'pdestructorcall_free.OPERATION = (pdestructionoperation)',
        'pdestructorcall_free.PENDING = eps',
        '$destructor_enter_valid(S_free,pdestructorcall_free)',
        '$heap_owners($heap_graph(S_free),HOBJECT n_right) = 2',
        'n_right <- S_free.DESTRUCTION.CALLED',
        '$test_outputs(S_free.EVENTS) = $test_outputs(S_marker.EVENTS)',
        *common.reach('S_query','S_free',0,'V84_DIRECT'),
        'S_query.STORE[n_result] = DEFINED (PBOOL false)',
        'S_query.USERCONSTANTS = S_row.USERCONSTANTS',
        '~(HOBJECT n_right <- S_query.ALLOCATIONS)',
        '$dynamic_global_constant_value(S_query,$ptascii("V84_DIRECT")) = (POBJECT n_left)',
        '$heap_owners($heap_graph(S_query),HOBJECT n_left) = 1',
        '$test_outputs(S_query.EVENTS) = ' + term(b'B|T|same|7|19|H|2|D|41|F|null|constant|'),
        *common.step('S_value','S_query','POBJECT n_left'),
        '$heap_owners($heap_graph(S_value),HOBJECT n_left) = 2',
        'S_value.ALLOCATIONS = S_query.ALLOCATIONS', 'S_value.OBJECTS = S_query.OBJECTS',
        'S_value.ARRAYS = S_query.ARRAYS', 'S_value.USERCONSTANTS = S_query.USERCONSTANTS',
        *instance.store('S_store','S_value','n_left',1,stdout[:-5]),
        *define.finish('S_store_selected',stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_final.CONSTANTOBJECTS = eps',
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 1',
        '~(HOBJECT n_right <- S_final.ALLOCATIONS)',
        'n_left <- S_final.DESTRUCTION.CALLED', 'n_right <- S_final.DESTRUCTION.CALLED',
        *instance.property_value('S_final','n_left',19,'left_final')]
    return values


def array(initial, stdout):
    edge, key = text('edge'), text('object')
    values = [*initial, *define.reach('S','S_initial',0,'V84_ARRAY'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        '$dynamic_define_values(pconfigcall) = (($ptascii("V84_ARRAY"),PARRAY n_input))',
        '$dynamic_array_call_valid(S,pconfigcall)',
        'S.CONSTANTOBJECTS = eps', 'S.USERCONSTANTS = eps',
        '$lookup(S.ENV,$ptascii("object")) = (n_object_cv)',
        '$lookup(S.ENV,$ptascii("cell")) = (n_cell)',
        '$lookup(S.ENV,$ptascii("input")) = (n_input_cv)',
        'S.STORE[n_object_cv] = DEFINED PNULL',
        'S.STORE[n_cell] = DEFINED (PARRAY n_source_child)',
        'S.STORE[n_input_cv] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        f'S.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {edge}) (ALIAS n_cell)]',
        'S.ARRAYS[n_input].NEXT = 91',
        f'S.ARRAYS[n_source_child].ITEMS = [ENTRY (KSTRING {key}) (DIRECT (POBJECT n_object))]',
        'S.ARRAYS[n_source_child].NEXT = 91',
        f'S.ARRAYS[n_caller] = $array_insert(S.ARRAYS[n_input],KINT 90,DIRECT (PINT 31))',
        *ordinary('S','n_object','array_object'),
        '$heap_owners($heap_graph(S),HOBJECT n_object) = 1',
        *instance.property_value('S','n_object',23,'array_initial'),
        'n_child = |S.ARRAYS|', 'n_root = $(n_child + 1)',
        f'parray_child = $array_insert($array_empty(),KSTRING {key},DIRECT (POBJECT n_object))',
        f'parray_root = $array_insert($array_empty(),KSTRING {edge},DIRECT (PARRAY n_child))',
        f'pvalueclass_tree = PVARRAY false ([(KSTRING {edge},PVARRAY false ([(KSTRING {key},PVOBJECT)]))])',
        # A checking projection is not a resumable public machine state.
        '$dynamic_array_value(S,PARRAY n_input,eps,true) = ((S_validation,PARRAY n_root,pvalueclass_tree))',
        'S_validation.ARRAYS = S.ARRAYS ++ [parray_child,parray_root]',
        *common.step('S_registered','S'),
        'S_row_found = $test_runtime_object_delivery_seek(S_registered,100)',
        r'S_row_found.COMPLETION = NORMAL \/ S_row_found.COMPLETION = BUDGET',
        'S_row = $test_running(S_row_found)',
        '$test_runtime_object_delivery(S_row)', 'S_row.TODO = ptask_initial*', *common.public('S_row'),
        'S_row.ARRAYS = S_validation.ARRAYS', 'S_row.OBJECTS = S.OBJECTS',
        'S_row.STORE = S.STORE', 'S_row.USERCONSTANTS = [puserconstant_row]',
        'puserconstant_row.ORIGIN = pconfigcall.SITE',
        'puserconstant_row.VALUE = PARRAY n_root', 'puserconstant_row.CLASS = pvalueclass_tree',
        '$dynamic_global_constant_value(S_row,$ptascii("V84_ARRAY")) = (PARRAY n_root)',
        '$heap_owners($heap_graph(S_row),HOBJECT n_object) = 2',
        '$array_append_key(S_row.ARRAYS[n_root]) = KINT 0',
        '~(HARRAY n_input <- S_row.ALLOCATIONS)',
        'S_recovered_found = $test_runtime_object_unset_seek(S_row,1500)',
        r'S_recovered_found.COMPLETION = NORMAL \/ S_recovered_found.COMPLETION = BUDGET',
        'S_recovered = $test_running(S_recovered_found)',
        '$test_runtime_object_unset(S_recovered)', *common.public('S_recovered'),
        '$lookup(S_recovered.ENV,$ptascii("copy")) = (n_copy_cv)',
        '$lookup(S_recovered.ENV,$ptascii("again")) = (n_again_cv)',
        '$lookup(S_recovered.ENV,$ptascii("slot")) = (n_slot)',
        '$lookup(S_recovered.ENV,$ptascii("property")) = (n_property)',
        'S_recovered.STORE[n_copy_cv] = DEFINED (PARRAY n_copy_root)',
        'S_recovered.STORE[n_again_cv] = DEFINED (PARRAY n_root)',
        'n_copy_root =/= n_root',
        f'$entry_lookup(S_recovered.ARRAYS[n_copy_root].ITEMS,KSTRING {edge}) = (DIRECT (PARRAY n_copy_child))',
        'n_copy_child =/= n_child',
        f'S_recovered.ARRAYS[n_copy_child].ITEMS = [ENTRY (KSTRING {key}) (ALIAS n_slot)]',
        'S_recovered.STORE[n_slot] = DEFINED PNULL',
        'S_recovered.STORE[n_cell] = DEFINED PNULL',
        'S_recovered.STORE[n_property] = DEFINED (PINT 41)',
        f'$entry_lookup(S_recovered.ARRAYS[n_copy_root].ITEMS,KINT 0) = (DIRECT (PINT 53))',
        'S_recovered.ARRAYS[n_copy_root].NEXT = 1',
        'S_recovered.ARRAYS[n_root] = parray_root', 'S_recovered.ARRAYS[n_child] = parray_child',
        *instance.property_value('S_recovered','n_object',41,'array_shared'),
        '$heap_owners($heap_graph(S_recovered),HOBJECT n_object) = 3',
        'S_recovered.USERCONSTANTS = S_row.USERCONSTANTS',
        *instance.store('S_store','S_recovered','n_object',1,stdout[:-5]),
        *define.finish('S_store_selected',stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS', 'S_final.CONSTANTOBJECTS = eps',
        '$heap_owners($heap_graph(S_final),HOBJECT n_object) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_child) = 1',
        '$heap_owners($heap_graph(S_final),HCELL n_property) = 1',
        'S_final.ARRAYS[n_root] = parray_root', 'S_final.ARRAYS[n_child] = parray_child',
        '~(HARRAY n_source_child <- S_final.ALLOCATIONS)',
        '~(HARRAY n_caller <- S_final.ALLOCATIONS)',
        '~(HARRAY n_copy_root <- S_final.ALLOCATIONS)', '~(HARRAY n_copy_child <- S_final.ALLOCATIONS)',
        '~(HCELL n_cell <- S_final.ALLOCATIONS)', '~(HCELL n_slot <- S_final.ALLOCATIONS)',
        'n_object <- S_final.DESTRUCTION.CALLED',
        *instance.property_value('S_final','n_object',41,'array_final')]
    return values


def checks(initial, name, stdout):
    return (direct if name == DIRECT else array)(initial, stdout)


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = packet.process


def process(command, directory, timeout, cwd):
    if directory.parent.name in sources.family.CASES:
        timeout = 180 if directory.parent.name == DIRECT else 150
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
