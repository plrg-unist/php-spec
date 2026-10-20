#!/usr/bin/env python3
"""Reached fromCallable publication with saved private USER permission."""
import argparse
from pathlib import Path
import sys

import define_certified_instance_protocol as instance
import define_runtime_closure_protocol as runtime
import define_scoped_runtime_closure_protocol as scoped
import define_stdclass_array_duplicate_protocol as prior
import define_runtime_from_callable_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
DIRECT = sources.DIRECT
PREFIX = scoped.PREFIX + r'''
dec $test_from_value_capture(pstate) : bool
def $test_from_value_capture(S) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_FROM_CALLABLE
def $test_from_value_capture(S) = false -- otherwise
dec $test_from_value_capture_seek(pstate, nat) : pstate
def $test_from_value_capture_seek(S,0) = S
def $test_from_value_capture_seek(S,n) = S
  -- if $(n > 0)
  -- if $test_from_value_capture(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_from_value_capture_seek(S,n) = $test_from_value_capture_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_from_value_capture(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def creation(initial, receiver=False):
    values = [*initial,
        'S_capture_found = $test_from_value_capture_seek(S_initial,1000)',
        r'S_capture_found.COMPLETION = NORMAL \/ S_capture_found.COMPLETION = BUDGET',
        'S_capture = $test_running(S_capture_found)',
        '$test_from_value_capture(S_capture)', *common.public('S_capture'),
        'S_capture.TODO = (CONFIG_INVOKE pconfigcall_capture) :: ptask_capture*',
        'pconfigcall_capture.KIND = INTRINSIC_FROM_CALLABLE',
        'pconfigcall_capture.INDEX = 1', '~pconfigcall_capture.NAMED',
        'pconfigcall_capture.OWNER = eps',
        'pconfigcall_capture.SENT = [NAMED_SENT (KNOWN (PARRAY n_callback))]',
        '$config_invoke_valid(S_capture,pconfigcall_capture)',
        '$lookup(S_capture.ENV,$ptascii("callback")) = (n_callback_cv)',
        '$lookup(S_capture.ENV,$ptascii("method")) = (n_method_local)',
        'S_capture.STORE[n_callback_cv] = DEFINED (PARRAY n_callback)',
        'S_capture.ARRAYS[n_callback].ITEMS = [ENTRY (KINT 0) (ALIAS n_input_local),ENTRY (KINT 1) (ALIAS n_method_local)]',
        'S_capture.STORE[n_method_local] = DEFINED pvalue_method',
        '$string_bytes(pvalue_method) = ($ptascii("read"))',
        '$from_identity(S_capture,PARRAY n_callback) = eps',
        'S_capture.CURRENT = (pcallcontext_creator)',
        'pcallcontext_creator.LEXICAL_CLASS = (porigin_base)',
        'pcallcontext_creator.CALLED_CLASS = (porigin_child)']
    if receiver:
        values += ['$lookup(S_capture.ENV,$ptascii("receiver")) = (n_input_local)',
            'S_capture.STORE[n_input_local] = DEFINED (POBJECT n_receiver_left)',
            'pcallcontext_creator.RECEIVER = (n_receiver_left)']
    else:
        values += ['$lookup(S_capture.ENV,$ptascii("class")) = (n_input_local)',
            'S_capture.STORE[n_input_local] = DEFINED pvalue_class',
            '$string_bytes(pvalue_class) = ($ptascii("V91ArrayChild"))',
            'pcallcontext_creator.RECEIVER = eps']
    return values


def selected(state, obj, label, receiver, static=False):
    method, scope = 'pfrommethod_' + label, 'pclosurescope_' + label
    return [f'{state}.OBJECTS[{obj}] = FROMCALLABLECLOSURE {method}',
        f'{method}.SITE = pconfigcall_capture.SITE', f'{method}.FACTORY = eps',
        f'{method}.SCOPE = (porigin_base)', f'{method}.CALLED = (porigin_child)',
        f'{method}.CLASS.REQUESTED = porigin_child', f'{method}.CLASS.CALLED = porigin_child',
        f'{method}.CLASS.RECEIVER = {receiver}',
        f'{method}.CLASS.STRICT = {str(static).lower()}',
        f'{method}.FUNCTION = porigin_body', f'{method}.NAME = $ptascii("read")',
        f'{method}.METHOD = $ptascii("read")', f'{method}.PREFIX = 0', f'{method}.WIDTH = 0',
        f'{method}.STATIC = {str(static).lower()}', f'{method}.ARRAY', f'~{method}.INVOKE',
        f'{method}.OUTER = eps', f'{method}.CREATION = eps',
        f'$from_valid({state},{method})', f'$from_permission({state},{method})',
        f'$closure_scope_at({state}.CLOSURESCOPES,{obj}) = ({scope})',
        f'{scope}.OBJECT = {obj}', f'{scope}.LEXICAL = porigin_base',
        f'{scope}.CALLED = porigin_child', f'{scope}.RECEIVER = {receiver}',
        f'{scope}.CREATION = eps', f'$closure_scope_row_valid({state},{scope})',
        f'$typed_closure({state},{obj})', f'$closure_live_object_valid({state},{obj})',
        f'$closure_binding_at({state}.CLOSUREBINDINGS,{obj}) = eps',
        f'$constant_callable_record({state}.CONSTANTCLOSURES,{obj}) = eps',
        f'$dynamic_define_value_class({state},POBJECT {obj}) = (PVOBJECT)']


def counter(state, value):
    return [f'{state}.STATICS = [pstaticcell_count]',
        f'$static_at({state}.STATICS,pstaticcell_count.ORIGIN) = (n_count)',
        'pstaticcell_count.CELL = n_count',
        f'n_count <- {state}.REFCELLS', f'HCELL n_count <- {state}.ALLOCATIONS',
        f'{state}.STORE[n_count] = DEFINED (PINT {value})',
        f'$heap_owners($heap_graph({state}),HCELL n_count) = 1']


def controls():
    return ['~$global_constant_class_supported(PVOBJECT)',
        '~$global_constant_class_supported(PVARRAY false ([(KSTRING ($ptascii("edge")),PVOBJECT)]))',
        '~$constant_value_class_valid(S,POBJECT n_left,PVCLOSURE n_left pconfigcall.SITE)',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_left)]',
        '$dynamic_define_value_class(S_dead,POBJECT n_left) = eps',
        '~$dynamic_runtime_object(S,|S.OBJECTS|)',
        'S_no_scope = S[.CLOSURESCOPES = eps]',
        '~$typed_closure(S_no_scope,n_left)', '~$dynamic_runtime_object(S_no_scope,n_left)',
        'S_dead_receiver = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_receiver_left)]',
        '~$typed_closure(S_dead_receiver,n_left)', '~$dynamic_runtime_object(S_dead_receiver,n_left)',
        'S_wrong_scope = S[.CLOSURESCOPES = [pclosurescope_first[.LEXICAL = porigin_child]]]',
        '~$closure_live_object_valid(S_wrong_scope,n_left)', '~$dynamic_runtime_object(S_wrong_scope,n_left)',
        'S_wrong_site = S[.OBJECTS[n_left] = FROMCALLABLECLOSURE pfrommethod_first[.SITE = pconfigcall.SITE]]',
        '~$dynamic_runtime_object(S_wrong_site,n_left)',
        'S_wrong_user = S[.OBJECTS[n_left] = FROMCALLABLECLOSURE pfrommethod_first[.SCOPE = (porigin_child)]]',
        '~$dynamic_runtime_object(S_wrong_user,n_left)',
        'S_wrong_function = S[.OBJECTS[n_left] = FROMCALLABLECLOSURE pfrommethod_first[.FUNCTION = pmethoddesc_child.FUNCTION.ORIGIN]]',
        '~$dynamic_runtime_object(S_wrong_function,n_left)',
        'S_wrong_leaf = S[.OBJECTS[n_left] = FROMCALLABLECLOSURE pfrommethod_first[.METHOD = $ptascii("gone")]]',
        '~$dynamic_runtime_object(S_wrong_leaf,n_left)',
        'pclosurebinding_bad = {OBJECT n_left,SITE pconfigcall.SITE,SOURCE n_left,LEXICAL eps,CALLED eps,RECEIVER eps}',
        'S_binding = S[.CLOSUREBINDINGS = [pclosurebinding_bad]]',
        '$typed_closure(S_binding,n_left)', '~$dynamic_runtime_object(S_binding,n_left)',
        'S_wrapped = S[.OBJECTS[n_left] = CONSTANTCLOSURE pconfigcall.SITE (S.OBJECTS[n_left])]',
        '$dynamic_define_value_class(S_wrapped,POBJECT n_left) = eps',
        'S_internal = S[.OBJECTS[n_left] = INTRINSICCLOSURE INTRINSIC_DEFINE]',
        '~$dynamic_runtime_object(S_internal,n_left)',
        'pconstantclosure_bad = {OBJECT n_left,SITE pconfigcall.SITE,DECL pconfigcall.SITE,PREFIX (|S.DECLARATIONS|)}',
        'S_bad_record = S[.CONSTANTCLOSURES = [pconstantclosure_bad]]',
        '$dynamic_define_value_class(S_bad_record,POBJECT n_left) = eps']


def direct(initial, stdout):
    before = stdout.removesuffix(b'D|41|A|D|23|'); assert before != stdout
    values = [*creation(initial,True),
        *define.reach('S','S_capture',0,'V91_FROM_CLOSURE'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        '$dynamic_define_values(pconfigcall) = (($ptascii("V91_FROM_CLOSURE"),POBJECT n_left))',
        '$config_invoke_valid(S,pconfigcall)', 'pconfigcall.NAMED',
        'S.USERCONSTANTS = eps', 'S.CONSTANTCLOSURES = eps', 'S.STATICS = eps',
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
        'S.CURRENT = eps',
        'S.STORE[n_other_cv] = DEFINED (POBJECT n_receiver_right)',
        'n_left =/= n_right', *scoped.classes('S','V91Base','V91Child'),
        *selected('S','n_left','first','(n_receiver_left)'),
        *selected('S','n_right','right','(n_receiver_right)'),
        'pfrommethod_first.INPUT = POBJECT n_receiver_left',
        'pfrommethod_right.INPUT = POBJECT n_receiver_right',
        '$from_selected(S,pfrommethod_first) = (pmethoddesc_selected)',
        'pmethoddesc_selected.OWNER = porigin_base',
        'pmethoddesc_selected.VISIBILITY = PROPERTY_PRIVATE',
        'pmethoddesc_selected.FUNCTION.ORIGIN = porigin_body',
        '$effective_method(S,porigin_child,$ptascii("read"),|S.CLASSES|) = (pmethoddesc_child)',
        'pmethoddesc_child.OWNER = porigin_child',
        'pmethoddesc_child.VISIBILITY = PROPERTY_PUBLIC',
        'pmethoddesc_child.FUNCTION.ORIGIN =/= porigin_body',
        '~(HARRAY n_callback <- S.ALLOCATIONS)',
        '~(HCELL n_callback_cv <- S.ALLOCATIONS)',
        '~(HCELL n_input_local <- S.ALLOCATIONS)',
        '~(HCELL n_method_local <- S.ALLOCATIONS)',
        '$node_children(S,HOBJECT n_left) = [HOBJECT n_receiver_left]',
        '$heap_owners($heap_graph(S),HOBJECT n_left) = 2',
        '$heap_owners($heap_graph(S),HOBJECT n_right) = 2',
        '$heap_owners($heap_graph(S),HOBJECT n_receiver_left) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_receiver_right) = 2',
        *scoped.private_values('S','n_receiver_left',23,'left_initial'),
        *scoped.private_values('S','n_receiver_right',100,'right_initial'),
        *controls(),
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]', '$test_running(S_pause) = S',
        *common.step('S_row','S','PBOOL true'),
        '$drive_steps($test_running(S_pause),1) = S_row_found',
        'S_row.TODO = ptask_initial*', 'S_row.USERCONSTANTS = [puserconstant_row]',
        'puserconstant_row.ORIGIN = pconfigcall.SITE',
        'puserconstant_row.VALUE = POBJECT n_left', 'puserconstant_row.CLASS = PVOBJECT',
        '$heap_owners($heap_graph(S_row),HOBJECT n_left) = 2']
    values += [f'S_row.{field} = S.{field}' for field in
        ['OBJECTS','ARRAYS','ALLOCATIONS','STORE','STATICS','CLOSURESCOPES','CLOSUREBINDINGS','CONSTANTCLOSURES']]
    values += ['puserconstant_bad = puserconstant_row[.ORIGIN = PORIGIN 0 eps]',
        '$dynamic_global_constant_value(S_row[.USERCONSTANTS = [puserconstant_bad]],$ptascii("V91_FROM_CLOSURE")) = eps',
        *common.reach('S_query','S_row',0,'V91_FROM_CLOSURE'),
        '$dynamic_global_constant_value(S_query,$ptascii("V91_FROM_CLOSURE")) = (POBJECT n_left)',
        *common.step('S_value','S_query','POBJECT n_left'),
        '$heap_owners($heap_graph(S_value),HOBJECT n_left) = 3',
        'S_value.ALLOCATIONS = S_query.ALLOCATIONS', 'S_value.OBJECTS = S_query.OBJECTS',
        *define.reach('S_dup','S_value',1,'V91_FROM_CLOSURE'),
        'S_dup.TODO = (CONFIG_INVOKE pconfigcall_dup) :: ptask_dup*',
        '$dynamic_define_values(pconfigcall_dup) = (($ptascii("V91_FROM_CLOSURE"),POBJECT n_right))',
        '$dynamic_constant_duplicate_valid(S_dup,pconfigcall_dup,1)',
        'S_dup.USERCONSTANTS = S_row.USERCONSTANTS',
        *counter('S_dup',2),
        '$static_function_at($class_method_functions(S_dup.CLASSES),pstaticcell_count.ORIGIN) = (pfunction_count)',
        'pfunction_count.ORIGIN = porigin_body', '$static_cells_valid(S_dup,S_dup.STATICS)',
        '$heap_edge_owners(HCELL n_count,$heap_graph(S_dup).EDGES,[HOBJECT n_left,HOBJECT n_right]) = 0',
        '$heap_owners($heap_graph(S_dup),HOBJECT n_right) = 3',
        *common.step('S_warning','S_dup'),
        'S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warning*',
        'perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup 1',
        *define.reach('S_resume','S_warning',4,'V91_FROM_CLOSURE'),
        'S_resume.TODO = (DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup 1) :: ptask_warning*',
        'S_resume.STORE[n_candidate] = DEFINED PNULL', 'S_resume.STORE[n_calls] = DEFINED (PINT 1)',
        'S_resume.USERCONSTANTS = S_row.USERCONSTANTS',
        *counter('S_resume',3), *scoped.private_values('S_resume','n_receiver_right',41,'right_callback'),
        *common.step('S_release','S_resume'),
        'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_warning*',
        'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_right)]',
        'pdestructionoperation.SOURCE = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup 1',
        'pdestructionoperation.VALUE = KNOWN (PBOOL false)', 'pdestructionoperation.PENDING = eps',
        *common.step('S_released','S_release'), *common.step('S_release_exit','S_released'),
        *common.step('S_false','S_release_exit','PBOOL false'),
        'S_false.TODO = ptask_warning*', 'S_false.USERCONSTANTS = S_row.USERCONSTANTS',
        '$heap_owners($heap_graph(S_false),HOBJECT n_right) = 1',
        *runtime.unset('S_observed','S_false','stored'), *counter('S_observed',4),
        '$test_outputs(S_observed.EVENTS) = ' + term(before),
        'S_free_found = $test_scoped_real_free_seek(S_observed,n_receiver_right,1500)',
        r'S_free_found.COMPLETION = NORMAL \/ S_free_found.COMPLETION = BUDGET',
        'S_free = $test_running(S_free_found)', '$test_scoped_real_free(S_free,n_receiver_right)',
        *common.public('S_free'),
        'S_free.TODO = (DESTRUCTOR_ENTER pdestructorcall_free) :: ptask_free*',
        'pdestructorcall_free.OBJECT = n_receiver_right', '~pdestructorcall_free.STORE',
        '$destructor_enter_valid(S_free,pdestructorcall_free)',
        '~(HOBJECT n_right <- S_free.ALLOCATIONS)',
        'HCELL n_count <- S_free.ALLOCATIONS',
        '$heap_owners($heap_graph(S_free),HOBJECT n_receiver_right) = 2',
        '$test_outputs(S_free.EVENTS) = ' + term(before),
        *instance.store('S_store','S_free','n_receiver_left',1,before+b'D|41|A|'),
        *define.finish('S_store_selected',stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS', *counter('S_final',4),
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 1',
        '$node_children(S_final,HOBJECT n_left) = [HOBJECT n_receiver_left]',
        '$heap_edge_owners(HOBJECT n_receiver_left,$heap_graph(S_final).EDGES,[HOBJECT n_left]) = 1',
        '~(HOBJECT n_receiver_right <- S_final.ALLOCATIONS)',
        'n_receiver_left <- S_final.DESTRUCTION.CALLED', 'n_receiver_right <- S_final.DESTRUCTION.CALLED']
    return values


def array(initial, stdout):
    edge = text('edge')
    before = stdout.removesuffix(b'after|S|41|V91ArrayChild|3|A|'); assert before != stdout
    return [*creation(initial),
        *define.reach('S','S_capture',0,'V91_STATIC_FROM_CLOSURE'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        '$dynamic_define_values(pconfigcall) = (($ptascii("V91_STATIC_FROM_CLOSURE"),PARRAY n_input))',
        '$dynamic_array_call_valid(S,pconfigcall)', 'S.USERCONSTANTS = eps', 'S.STATICS = eps',
        '$lookup(S.ENV,$ptascii("slot")) = (n_slot)',
        '$lookup(S.ENV,$ptascii("input")) = (n_input_cv)',
        'S.STORE[n_slot] = DEFINED (POBJECT n_closure)',
        '~(HARRAY n_callback <- S.ALLOCATIONS)',
        '~(HCELL n_callback_cv <- S.ALLOCATIONS)',
        '~(HCELL n_input_local <- S.ALLOCATIONS)',
        '~(HCELL n_method_local <- S.ALLOCATIONS)',
        'S.STORE[n_input_cv] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        f'S.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {edge}) (ALIAS n_slot)]',
        'S.ARRAYS[n_input].NEXT = 91',
        f'S.ARRAYS[n_caller] = $array_insert(S.ARRAYS[n_input],KINT 90,DIRECT (PINT 31))',
        *scoped.classes('S','V91ArrayBase','V91ArrayChild'),
        *selected('S','n_closure','first','eps',True),
        '$string_bytes(pfrommethod_first.INPUT) = ($ptascii("V91ArrayChild"))',
        '$closure_scope_roots(S.CLOSURESCOPES,n_closure) = eps',
        '$node_children(S,HOBJECT n_closure) = eps', *scoped.static_values('S',23),
        '$heap_owners($heap_graph(S),HOBJECT n_closure) = 1',
        'S_bad_scope = S[.CLOSURESCOPES = [pclosurescope_first[.CALLED = porigin_base]]]',
        '$closure_scope_complete(S_bad_scope,[HOBJECT n_closure])',
        '~$closure_live_object_valid(S_bad_scope,n_closure)', '~$dynamic_runtime_object(S_bad_scope,n_closure)',
        'n_root = |S.ARRAYS|',
        f'parray_root = $array_insert($array_empty(),KSTRING {edge},DIRECT (POBJECT n_closure))',
        f'pvalueclass_tree = PVARRAY false ([(KSTRING {edge},PVOBJECT)])',
        '$dynamic_array_value(S,PARRAY n_input,eps,true) = ((S_validation,PARRAY n_root,pvalueclass_tree))',
        'S_validation.ARRAYS = S.ARRAYS ++ [parray_root]',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]', '$test_running(S_pause) = S',
        *common.step('S_row','S','PBOOL true'), '$drive_steps($test_running(S_pause),1) = S_row_found',
        'S_row.TODO = ptask_initial*', 'S_row.ARRAYS = S_validation.ARRAYS',
        'S_row.OBJECTS = S.OBJECTS', 'S_row.STORE = S.STORE', 'S_row.CLOSURESCOPES = S.CLOSURESCOPES',
        'S_row.USERCONSTANTS = [puserconstant_row]',
        'puserconstant_row.ORIGIN = pconfigcall.SITE',
        'puserconstant_row.VALUE = PARRAY n_root', 'puserconstant_row.CLASS = pvalueclass_tree',
        '$dynamic_global_constant_value(S_row,$ptascii("V91_STATIC_FROM_CLOSURE")) = (PARRAY n_root)',
        '$heap_owners($heap_graph(S_row),HOBJECT n_closure) = 2',
        '$array_append_key(S_row.ARRAYS[n_root]) = KINT 0', '~(HARRAY n_input <- S_row.ALLOCATIONS)',
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
        *counter('S_observed',2),
        '$static_function_at($class_method_functions(S_observed.CLASSES),pstaticcell_count.ORIGIN) = (pfunction_count)',
        'pfunction_count.ORIGIN = porigin_body', '$static_cells_valid(S_observed,S_observed.STATICS)',
        *scoped.static_values('S_observed',41),
        '$closure_scope_at(S_observed.CLOSURESCOPES,n_closure) = (pclosurescope_first)',
        '$node_children(S_observed,HOBJECT n_closure) = eps',
        '$heap_owners($heap_graph(S_observed),HOBJECT n_closure) = 3',
        'S_observed.USERCONSTANTS = S_row.USERCONSTANTS',
        '$test_outputs(S_observed.EVENTS) = ' + term(before),
        *define.finish('S_observed',stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS', 'S_final.ARRAYS[n_root] = parray_root',
        *counter('S_final',3), '$node_children(S_final,HOBJECT n_closure) = eps',
        '$heap_owners($heap_graph(S_final),HOBJECT n_closure) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)',
        '~(HARRAY n_caller <- S_final.ALLOCATIONS)', '~(HARRAY n_copy <- S_final.ALLOCATIONS)',
        '~(HCELL n_slot <- S_final.ALLOCATIONS)', '~(HCELL n_bucket <- S_final.ALLOCATIONS)']


def checks(initial, name, stdout):
    return (direct if name == DIRECT else array)(initial, stdout)


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = runtime.packet_process


def process(command, directory, timeout, cwd):
    if directory.parent.name in sources.family.CASES:
        timeout = 300 if directory.parent.name == DIRECT else 180
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
