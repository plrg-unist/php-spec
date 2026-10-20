#!/usr/bin/env python3
"""Reached scoped REAL publication, private scope, statics and query COW."""
import argparse
from pathlib import Path
import sys

import define_certified_instance_protocol as instance
import define_runtime_closure_protocol as runtime
import define_stdclass_array_duplicate_protocol as prior
import define_scoped_runtime_closure_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
DIRECT = 'scoped-real-closure-private-access-and-normal-duplicate'
PREFIX = instance.PREFIX + runtime.PREFIX[len(define.PREFIX):] + r'''
dec $test_scoped_real_free(pstate, nat) : bool
def $test_scoped_real_free(S,n_receiver) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OBJECT = n_receiver /\ ~pdestructorcall.STORE
def $test_scoped_real_free(S,n_receiver) = false -- otherwise
dec $test_scoped_real_free_seek(pstate, nat, nat) : pstate
def $test_scoped_real_free_seek(S,n_receiver,0) = S
def $test_scoped_real_free_seek(S,n_receiver,n) = S
  -- if $(n > 0)
  -- if $test_scoped_real_free(S,n_receiver) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_scoped_real_free_seek(S,n_receiver,n) = $test_scoped_real_free_seek($drive_steps($test_running(S),1),n_receiver,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_scoped_real_free(S,n_receiver)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def scoped(state, obj, label, receiver):
    scope = 'pclosurescope_' + label
    return [f'$closure_scope_at({state}.CLOSURESCOPES,{obj}) = ({scope})',
        f'{scope}.OBJECT = {obj}', f'{scope}.LEXICAL = porigin_base',
        f'{scope}.CALLED = porigin_child', f'{scope}.RECEIVER = {receiver}',
        f'{scope}.CREATION = eps',
        f'$closure_binding_at({state}.CLOSUREBINDINGS,{obj}) = eps',
        f'$closure_scope_row_valid({state},{scope})',
        f'$dynamic_real_scope_valid({state},{obj})',
        f'$closure_scope_complete({state},[HOBJECT {obj}])',
        f'$typed_closure({state},{obj})', f'$closure_live_object_valid({state},{obj})',
        f'$constant_callable_record({state}.CONSTANTCLOSURES,{obj}) = eps',
        f'$dynamic_define_value_class({state},POBJECT {obj}) = (PVOBJECT)']


def private_values(state, obj, value, label):
    return [f'$objectprops_at({state}.OBJECTPROPS,{obj}) = (ppropertyslot_all_{label}*)',
        f'$property_slot_at(ppropertyslot_all_{label}*,ppropertydesc_base.KEY) = (ppropertyslot_base_{label})',
        f'ppropertyslot_base_{label}.STATE = PROP_VALUE (DIRECT (PINT {value}))',
        f'$property_slot_at(ppropertyslot_all_{label}*,ppropertydesc_shadow.KEY) = (ppropertyslot_shadow_{label})',
        f'ppropertyslot_shadow_{label}.STATE = PROP_VALUE (DIRECT (PINT 100))']


def classes(state, base, child):
    return [f'$class_named({state}.CLASSNAMES,$ptlc($ptascii("{base}"))) = (porigin_base)',
        f'$class_named({state}.CLASSNAMES,$ptlc($ptascii("{child}"))) = (porigin_child)',
        'porigin_base =/= porigin_child',
        f'$class_at({state}.CLASSES,porigin_base) = (pclassdesc_base)',
        f'$class_at({state}.CLASSES,porigin_child) = (pclassdesc_child)',
        'pclassdesc_base.PROPERTIES = [ppropertydesc_base]',
        'pclassdesc_child.PROPERTIES = [ppropertydesc_shadow]',
        'ppropertydesc_base.KEY =/= ppropertydesc_shadow.KEY']


def direct(initial, stdout):
    before = stdout.removesuffix(b'D|41|A|D|23|')
    assert before != stdout
    values = [*initial, *define.reach('S','S_initial',0,'V87_SCOPED'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        '$dynamic_define_values(pconfigcall) = (($ptascii("V87_SCOPED"),POBJECT n_left))',
        '$config_invoke_valid(S,pconfigcall)', 'pconfigcall.NAMED',
        'S.USERCONSTANTS = eps', 'S.CONSTANTCLOSURES = eps',
        '$lookup(S.ENV,$ptascii("left")) = (n_left_cv)',
        '$lookup(S.ENV,$ptascii("right")) = (n_right_cv)',
        '$lookup(S.ENV,$ptascii("candidate")) = (n_candidate)',
        '$lookup(S.ENV,$ptascii("owner")) = (n_owner_cv)',
        '$lookup(S.ENV,$ptascii("other")) = (n_other_cv)',
        '$lookup(S.ENV,$ptascii("calls")) = (n_calls)',
        'S.STORE[n_left_cv] = DEFINED (POBJECT n_left)',
        'S.STORE[n_right_cv] = DEFINED (POBJECT n_right)',
        'S.STORE[n_candidate] = DEFINED (POBJECT n_right)',
        'S.STORE[n_owner_cv] = DEFINED PNULL',
        'S.STORE[n_other_cv] = DEFINED (POBJECT n_receiver_right)',
        'n_left =/= n_right', *classes('S','V87Base','V87Child'),
        'S.OBJECTS[n_left] = REALCLOSURE porigin_body eps eps',
        'S.OBJECTS[n_right] = REALCLOSURE porigin_body eps eps',
        *scoped('S','n_left','left','(n_receiver_left)'),
        *scoped('S','n_right','right','(n_receiver_right)'),
        '$closure_source_class(S,porigin_body) = (porigin_base)',
        'S.OBJECTS[n_receiver_left] = INSTANCE porigin_child',
        'S.OBJECTS[n_receiver_right] = INSTANCE porigin_child',
        '$node_children(S,HOBJECT n_left) = [HOBJECT n_receiver_left]',
        '$heap_owners($heap_graph(S),HOBJECT n_left) = 2',
        '$heap_owners($heap_graph(S),HOBJECT n_right) = 2',
        '$heap_owners($heap_graph(S),HOBJECT n_receiver_left) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_receiver_right) = 2',
        *private_values('S','n_receiver_left',23,'left_initial'),
        *private_values('S','n_receiver_right',100,'right_initial'),
        '~$global_constant_class_supported(PVOBJECT)',
        '~$constant_value_class_valid(S,POBJECT n_left,PVCLOSURE n_left pconfigcall.SITE)',
        # Pure projections do not alter the driven states or grant certificates.
        'S_missing = S[.CLOSURESCOPES = eps]',
        '$typed_closure(S_missing,n_left)',
        '~$closure_scope_complete(S_missing,[HOBJECT n_left])',
        '~$dynamic_runtime_object(S_missing,n_left)',
        'S_dead_receiver = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_receiver_left)]',
        '$closure_scope_complete(S_dead_receiver,[HOBJECT n_left])',
        '~$dynamic_real_scope_valid(S_dead_receiver,n_left)',
        '~$dynamic_runtime_object(S_dead_receiver,n_left)',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        '$test_running(S_pause) = S',
        *common.step('S_row','S','PBOOL true'),
        '$drive_steps($test_running(S_pause),1) = S_row_found',
        'S_row.TODO = ptask_initial*', 'S_row.USERCONSTANTS = [puserconstant_row]',
        'puserconstant_row.ORIGIN = pconfigcall.SITE',
        'puserconstant_row.VALUE = POBJECT n_left', 'puserconstant_row.CLASS = PVOBJECT',
        '$heap_owners($heap_graph(S_row),HOBJECT n_left) = 2']
    values += [f'S_row.{field} = S.{field}' for field in
        ['OBJECTS','ARRAYS','ALLOCATIONS','STORE','STATICS','CLOSURESCOPES','CLOSUREBINDINGS','CONSTANTCLOSURES','EVENTS']]
    values += ['puserconstant_bad = puserconstant_row[.ORIGIN = PORIGIN 0 eps]',
        '$dynamic_global_constant_value(S_row[.USERCONSTANTS = [puserconstant_bad]],$ptascii("V87_SCOPED")) = eps',
        *common.reach('S_query','S_row',0,'V87_SCOPED'),
        '$dynamic_global_constant_value(S_query,$ptascii("V87_SCOPED")) = (POBJECT n_left)',
        '$heap_owners($heap_graph(S_query),HOBJECT n_left) = 2',
        *common.step('S_value','S_query','POBJECT n_left'),
        '$heap_owners($heap_graph(S_value),HOBJECT n_left) = 3',
        'S_value.OBJECTS = S_query.OBJECTS', 'S_value.ALLOCATIONS = S_query.ALLOCATIONS',
        'S_value.CLOSURESCOPES = S_query.CLOSURESCOPES',
        *define.reach('S_dup','S_value',1,'V87_SCOPED'),
        'S_dup.TODO = (CONFIG_INVOKE pconfigcall_dup) :: ptask_dup*',
        '$dynamic_define_values(pconfigcall_dup) = (($ptascii("V87_SCOPED"),POBJECT n_right))',
        '$dynamic_constant_duplicate_valid(S_dup,pconfigcall_dup,1)',
        'S_dup.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_dup.STORE[n_candidate] = DEFINED (POBJECT n_right)',
        'S_dup.STORE[n_calls] = DEFINED (PINT 0)',
        *runtime.counter('S_dup','n_left','porigin_body','eps','left',2),
        *runtime.counter('S_dup','n_right','porigin_body','eps','right',1),
        '$heap_owners($heap_graph(S_dup),HOBJECT n_right) = 3',
        '$heap_edge_owners(HOBJECT n_receiver_right,$heap_graph(S_dup).EDGES,[HOBJECT n_right]) = 1',
        *common.step('S_warning','S_dup'),
        'S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warning*',
        'perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup 1',
        *define.reach('S_resume','S_warning',4,'V87_SCOPED'),
        'S_resume.TODO = (DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup 1) :: ptask_warning*',
        'S_resume.STORE[n_candidate] = DEFINED PNULL',
        'S_resume.STORE[n_calls] = DEFINED (PINT 1)',
        'S_resume.USERCONSTANTS = S_row.USERCONSTANTS',
        *runtime.counter('S_resume','n_right','porigin_body','eps','right',2),
        *private_values('S_resume','n_receiver_right',41,'right_callback'),
        '$heap_owners($heap_graph(S_resume),HOBJECT n_right) = 2',
        *common.step('S_release','S_resume'),
        'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_warning*',
        'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_right)]',
        'pdestructionoperation.SOURCE = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup 1',
        'pdestructionoperation.VALUE = KNOWN (PBOOL false)', 'pdestructionoperation.PENDING = eps',
        *common.step('S_released','S_release'),
        *common.step('S_release_exit','S_released'),
        *common.step('S_false','S_release_exit','PBOOL false'),
        'S_false.TODO = ptask_warning*', 'S_false.USERCONSTANTS = S_row.USERCONSTANTS',
        '$heap_owners($heap_graph(S_false),HOBJECT n_right) = 1',
        *runtime.unset('S_observed','S_false','stored'),
        *runtime.counter('S_observed','n_left','porigin_body','eps','left',4),
        *runtime.counter('S_observed','n_right','porigin_body','eps','right',2),
        '$test_outputs(S_observed.EVENTS) = ' + term(before),
        'S_free_found = $test_scoped_real_free_seek(S_observed,n_receiver_right,1500)',
        r'S_free_found.COMPLETION = NORMAL \/ S_free_found.COMPLETION = BUDGET',
        'S_free = $test_running(S_free_found)',
        '$test_scoped_real_free(S_free,n_receiver_right)', *common.public('S_free'),
        'S_free.TODO = (DESTRUCTOR_ENTER pdestructorcall_free) :: ptask_free*',
        'pdestructorcall_free.OBJECT = n_receiver_right', '~pdestructorcall_free.STORE',
        '$destructor_enter_valid(S_free,pdestructorcall_free)',
        '~(HOBJECT n_right <- S_free.ALLOCATIONS)',
        '~(HCELL n_counter_right <- S_free.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_free),HOBJECT n_receiver_right) = 2',
        '$test_outputs(S_free.EVENTS) = ' + term(before),
        *instance.store('S_store','S_free','n_receiver_left',1,before+b'D|41|A|'),
        *define.finish('S_store_selected',stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS',
        *runtime.counter('S_final','n_left','porigin_body','eps','left',4),
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 1',
        '$heap_owners($heap_graph(S_final),HCELL n_counter_left) = 1',
        '$heap_edge_owners(HOBJECT n_receiver_left,$heap_graph(S_final).EDGES,[HOBJECT n_left]) = 1',
        '~(HOBJECT n_receiver_right <- S_final.ALLOCATIONS)',
        'n_receiver_left <- S_final.DESTRUCTION.CALLED',
        'n_receiver_right <- S_final.DESTRUCTION.CALLED']
    return values


def static_values(state, value):
    return [f'$class_static_at({state}.CLASSSTATICS,ppropertydesc_base.ORIGIN) = ({{DECL ppropertydesc_base.ORIGIN,STATE PROP_VALUE (DIRECT (PINT {value}))}})',
        f'$class_static_at({state}.CLASSSTATICS,ppropertydesc_shadow.ORIGIN) = ({{DECL ppropertydesc_shadow.ORIGIN,STATE PROP_VALUE (DIRECT (PINT 900))}})']


def array(initial, stdout):
    edge = text('edge')
    values = [*initial, *define.reach('S','S_initial',0,'V87_SCOPED_ARRAY'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        '$dynamic_define_values(pconfigcall) = (($ptascii("V87_SCOPED_ARRAY"),PARRAY n_input))',
        '$dynamic_array_call_valid(S,pconfigcall)', 'S.USERCONSTANTS = eps',
        '$lookup(S.ENV,$ptascii("slot")) = (n_slot)',
        '$lookup(S.ENV,$ptascii("input")) = (n_input_cv)',
        'S.STORE[n_slot] = DEFINED (POBJECT n_closure)',
        'S.STORE[n_input_cv] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        f'S.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {edge}) (ALIAS n_slot)]',
        'S.ARRAYS[n_input].NEXT = 91',
        f'S.ARRAYS[n_caller] = $array_insert(S.ARRAYS[n_input],KINT 90,DIRECT (PINT 31))',
        *classes('S','V87ArrayBase','V87ArrayChild'),
        'S.OBJECTS[n_closure] = REALCLOSURE porigin_body eps eps',
        *scoped('S','n_closure','array','eps'),
        '$closure_source_class(S,porigin_body) = (porigin_base)',
        '$closure_scope_roots(S.CLOSURESCOPES,n_closure) = eps',
        '$node_children(S,HOBJECT n_closure) = eps',
        *static_values('S',23),
        '$heap_owners($heap_graph(S),HOBJECT n_closure) = 1',
        # Class-source completeness alone does not validate a forged selected row.
        'S_wrong_scope = S[.CLOSURESCOPES = [pclosurescope_array[.LEXICAL = porigin_child]]]',
        '$closure_scope_complete(S_wrong_scope,[HOBJECT n_closure])',
        '~$dynamic_real_scope_valid(S_wrong_scope,n_closure)',
        '~$dynamic_runtime_object(S_wrong_scope,n_closure)',
        'n_root = |S.ARRAYS|',
        f'parray_root = $array_insert($array_empty(),KSTRING {edge},DIRECT (POBJECT n_closure))',
        f'pvalueclass_tree = PVARRAY false ([(KSTRING {edge},PVOBJECT)])',
        '$dynamic_array_value(S,PARRAY n_input,eps,true) = ((S_validation,PARRAY n_root,pvalueclass_tree))',
        'S_validation.ARRAYS = S.ARRAYS ++ [parray_root]',
        *common.step('S_row','S','PBOOL true'), 'S_row.TODO = ptask_initial*',
        'S_row.ARRAYS = S_validation.ARRAYS', 'S_row.OBJECTS = S.OBJECTS', 'S_row.STORE = S.STORE',
        'S_row.CLOSURESCOPES = S.CLOSURESCOPES', 'S_row.CLASSSTATICS = S.CLASSSTATICS',
        'S_row.USERCONSTANTS = [puserconstant_row]',
        'puserconstant_row.ORIGIN = pconfigcall.SITE',
        'puserconstant_row.VALUE = PARRAY n_root', 'puserconstant_row.CLASS = pvalueclass_tree',
        '$dynamic_global_constant_value(S_row,$ptascii("V87_SCOPED_ARRAY")) = (PARRAY n_root)',
        '$heap_owners($heap_graph(S_row),HOBJECT n_closure) = 2',
        '$array_append_key(S_row.ARRAYS[n_root]) = KINT 0',
        '~(HARRAY n_input <- S_row.ALLOCATIONS)',
        *runtime.unset('S_observed','S_row','bucket'),
        '$lookup(S_observed.ENV,$ptascii("copy")) = (n_copy_cv)',
        '$lookup(S_observed.ENV,$ptascii("again")) = (n_again_cv)',
        '$lookup(S_observed.ENV,$ptascii("bucket")) = (n_bucket)',
        'S_observed.STORE[n_copy_cv] = DEFINED (PARRAY n_copy)',
        'S_observed.STORE[n_again_cv] = DEFINED (PARRAY n_root)', 'n_copy =/= n_root',
        f'$entry_lookup(S_observed.ARRAYS[n_copy].ITEMS,KSTRING {edge}) = (ALIAS n_bucket)',
        'S_observed.STORE[n_bucket] = DEFINED PNULL', 'S_observed.STORE[n_slot] = DEFINED PNULL',
        f'$entry_lookup(S_observed.ARRAYS[n_copy].ITEMS,KINT 0) = (DIRECT (PINT 53))',
        'S_observed.ARRAYS[n_copy].NEXT = 1', 'S_observed.ARRAYS[n_root] = parray_root',
        *runtime.counter('S_observed','n_closure','porigin_body','eps','array',2),
        *static_values('S_observed',41),
        '$closure_scope_at(S_observed.CLOSURESCOPES,n_closure) = (pclosurescope_array)',
        '$node_children(S_observed,HOBJECT n_closure) = [HCELL n_counter_array]',
        '$heap_owners($heap_graph(S_observed),HOBJECT n_closure) = 3',
        '$heap_edge_owners(HCELL n_counter_array,$heap_graph(S_observed).EDGES,[HOBJECT n_closure]) = 1',
        'S_observed.USERCONSTANTS = S_row.USERCONSTANTS',
        '$test_outputs(S_observed.EVENTS) = ' + term(stdout[:-2]),
        *define.finish('S_observed',stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS', 'S_final.ARRAYS[n_root] = parray_root',
        *runtime.counter('S_final','n_closure','porigin_body','eps','array',2),
        '$heap_owners($heap_graph(S_final),HOBJECT n_closure) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_final),HCELL n_counter_array) = 1',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)', '~(HARRAY n_caller <- S_final.ALLOCATIONS)',
        '~(HARRAY n_copy <- S_final.ALLOCATIONS)', '~(HCELL n_slot <- S_final.ALLOCATIONS)',
        '~(HCELL n_bucket <- S_final.ALLOCATIONS)']
    return values


def checks(initial, name, stdout):
    return (direct if name == DIRECT else array)(initial, stdout)


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = runtime.packet_process


def process(command, directory, timeout, cwd):
    if directory.parent.name in sources.family.CASES:
        timeout = 240 if directory.parent.name == DIRECT else 150
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
