#!/usr/bin/env python3
"""Reached named Closure identity with independent request static roots."""
import argparse
from pathlib import Path
import sys

import define_runtime_closure_protocol as runtime
import define_stdclass_array_duplicate_protocol as prior
import define_runtime_named_closure_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
DIRECT = 'named-closure-shared-function-statics-and-normal-duplicate'
PREFIX = runtime.PREFIX


def named(state, obj, origin):
    return [f'{state}.OBJECTS[{obj}] = NAMEDCLOSURE {origin}',
        f'$typed_closure({state},{obj})', f'$closure_live_object_valid({state},{obj})',
        f'$closure_scope_at({state}.CLOSURESCOPES,{obj}) = eps',
        f'$closure_binding_at({state}.CLOSUREBINDINGS,{obj}) = eps',
        f'$constant_callable_record({state}.CONSTANTCLOSURES,{obj}) = eps',
        f'$node_children({state},HOBJECT {obj}) = eps',
        f'$dynamic_define_value_class({state},POBJECT {obj}) = (PVOBJECT)']


def counter(state, label, value):
    row = 'pstaticcell_' + label
    cell = 'n_counter_' + label
    return [f'$static_function_at({state}.FUNCTIONS,{row}.ORIGIN) = (pfunction_{label})',
        f'$static_at({state}.STATICS,{row}.ORIGIN) = ({cell})',
        f'{row}.CELL = {cell}', f'{cell} <- {state}.REFCELLS',
        f'HCELL {cell} <- {state}.ALLOCATIONS',
        f'{state}.STORE[{cell}] = DEFINED (PINT {value})',
        f'$heap_owners($heap_graph({state}),HCELL {cell}) = 1']


def controls():
    return ['~$global_constant_class_supported(PVOBJECT)',
        '~$constant_value_class_valid(S,POBJECT n_left,PVCLOSURE n_left pconfigcall.SITE)',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_left)]',
        '~$dynamic_runtime_object(S_dead,n_left)',
        '~$dynamic_runtime_object(S,|S.OBJECTS|)',
        'S_no_functions = S[.FUNCTIONS = eps]',
        '~$dynamic_runtime_object(S_no_functions,n_left)',
        'S_no_names = S[.CALLABLES = eps]',
        '~$dynamic_runtime_object(S_no_names,n_left)',
        'pclosurescope_bad = {OBJECT n_left,LEXICAL pconfigcall.SITE,CALLED pconfigcall.SITE,RECEIVER eps,CREATION eps}',
        'S_scope = S[.CLOSURESCOPES = [pclosurescope_bad]]',
        '$typed_closure(S_scope,n_left)', '$closure_live_object_valid(S_scope,n_left)',
        '~$dynamic_runtime_object(S_scope,n_left)',
        'pclosurebinding_bad = {OBJECT n_left,SITE pconfigcall.SITE,SOURCE n_left,LEXICAL eps,CALLED eps,RECEIVER eps}',
        'S_binding = S[.CLOSUREBINDINGS = [pclosurebinding_bad]]',
        '~$dynamic_runtime_object(S_binding,n_left)',
        'S_wrapped = S[.OBJECTS[n_left] = CONSTANTCLOSURE pconfigcall.SITE (S.OBJECTS[n_left])]',
        '$typed_closure(S_wrapped,n_left)',
        '$dynamic_define_value_class(S_wrapped,POBJECT n_left) = eps',
        'pconstantclosure_bad = {OBJECT n_left,SITE pconfigcall.SITE,DECL pconfigcall.SITE,PREFIX (|S.DECLARATIONS|)}',
        'S_bad_record = S[.CONSTANTCLOSURES = [pconstantclosure_bad]]',
        '$dynamic_define_value_class(S_bad_record,POBJECT n_left) = eps']


def direct(initial, stdout):
    before = stdout.removesuffix(b'after|103|A|'); assert before != stdout
    values = [*initial, *define.reach('S','S_initial',0,'V88_NAMED'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        '$dynamic_define_values(pconfigcall) = (($ptascii("V88_NAMED"),POBJECT n_left))',
        '$config_invoke_valid(S,pconfigcall)', 'pconfigcall.NAMED',
        'S.USERCONSTANTS = eps', 'S.STATICS = eps',
        '$lookup(S.ENV,$ptascii("left")) = (n_left_cv)',
        '$lookup(S.ENV,$ptascii("twin")) = (n_twin_cv)',
        '$lookup(S.ENV,$ptascii("right")) = (n_right_cv)',
        '$lookup(S.ENV,$ptascii("candidate")) = (n_candidate)',
        '$lookup(S.ENV,$ptascii("calls")) = (n_calls)',
        'S.STORE[n_left_cv] = DEFINED (POBJECT n_left)',
        'S.STORE[n_twin_cv] = DEFINED (POBJECT n_twin)',
        'S.STORE[n_right_cv] = DEFINED (POBJECT n_right)',
        'S.STORE[n_candidate] = DEFINED (POBJECT n_right)',
        'n_left =/= n_twin', 'n_left =/= n_right',
        *named('S','n_left','porigin_shared'), *named('S','n_twin','porigin_shared'),
        *named('S','n_right','porigin_other'),
        '$function_at(S.FUNCTIONS,porigin_shared) = (pfunction_shared)',
        '$function_at(S.FUNCTIONS,porigin_other) = (pfunction_other)',
        'pfunction_shared.NAME = ($ptascii("v88Counter"))',
        'pfunction_other.NAME = ($ptascii("v88Other"))',
        '$heap_owners($heap_graph(S),HOBJECT n_left) = 2',
        '$heap_owners($heap_graph(S),HOBJECT n_twin) = 1',
        '$heap_owners($heap_graph(S),HOBJECT n_right) = 2',
        # Pure projections never become the state passed to drive_steps.
        *controls(),
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
        '$dynamic_global_constant_value(S_row[.USERCONSTANTS = [puserconstant_bad]],$ptascii("V88_NAMED")) = eps',
        *common.reach('S_query','S_row',0,'V88_NAMED'),
        '$dynamic_global_constant_value(S_query,$ptascii("V88_NAMED")) = (POBJECT n_left)',
        *common.step('S_value','S_query','POBJECT n_left'),
        '$heap_owners($heap_graph(S_value),HOBJECT n_left) = 3',
        'S_value.ALLOCATIONS = S_query.ALLOCATIONS', 'S_value.OBJECTS = S_query.OBJECTS',
        *define.reach('S_dup','S_value',1,'V88_NAMED'),
        'S_dup.TODO = (CONFIG_INVOKE pconfigcall_dup) :: ptask_dup*',
        '$dynamic_define_values(pconfigcall_dup) = (($ptascii("V88_NAMED"),POBJECT n_right))',
        '$dynamic_constant_duplicate_valid(S_dup,pconfigcall_dup,1)',
        'S_dup.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_dup.STATICS = [pstaticcell_shared,pstaticcell_other]',
        *counter('S_dup','shared',3), *counter('S_dup','other',101),
        '$heap_edge_owners(HCELL n_counter_shared,$heap_graph(S_dup).EDGES,[HOBJECT n_left,HOBJECT n_twin]) = 0',
        '$heap_owners($heap_graph(S_dup),HOBJECT n_right) = 3',
        # NAMED type authority is separate from the request static invariant.
        'S_static_dead = S_dup[.ALLOCATIONS = $destruction_node_delete(S_dup.ALLOCATIONS,HCELL n_counter_shared)]',
        '$dynamic_runtime_object(S_static_dead,n_left)',
        '~$static_cells_valid(S_static_dead,S_static_dead.STATICS)',
        *common.step('S_warning','S_dup'),
        'S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warning*',
        'perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup 1',
        *define.reach('S_resume','S_warning',4,'V88_NAMED'),
        'S_resume.TODO = (DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup 1) :: ptask_warning*',
        'S_resume.STORE[n_candidate] = DEFINED PNULL',
        'S_resume.STORE[n_calls] = DEFINED (PINT 1)',
        'S_resume.STATICS = S_dup.STATICS',
        *counter('S_resume','other',102),
        *common.step('S_false','S_resume','PBOOL false'),
        'S_false.USERCONSTANTS = S_row.USERCONSTANTS',
        '$heap_owners($heap_graph(S_false),HOBJECT n_right) = 1',
        *runtime.unset('S_observed','S_false','stored'),
        *counter('S_observed','shared',5), *counter('S_observed','other',102),
        '$test_outputs(S_observed.EVENTS) = ' + term(before),
        *define.finish('S_observed',stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS', 'S_final.STATICS = S_dup.STATICS',
        *counter('S_final','shared',5), *counter('S_final','other',103),
        '$node_children(S_final,HOBJECT n_left) = eps',
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 1',
        '~(HOBJECT n_twin <- S_final.ALLOCATIONS)', '~(HOBJECT n_right <- S_final.ALLOCATIONS)']
    return values


def array(initial, stdout):
    edge = text('edge'); before = stdout.removesuffix(b'after|5|A|'); assert before != stdout
    return [*initial, *define.reach('S','S_initial',0,'V88_NAMED_ARRAY'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        '$dynamic_define_values(pconfigcall) = (($ptascii("V88_NAMED_ARRAY"),PARRAY n_input))',
        '$dynamic_array_call_valid(S,pconfigcall)', 'S.USERCONSTANTS = eps', 'S.STATICS = eps',
        '$lookup(S.ENV,$ptascii("slot")) = (n_slot)',
        '$lookup(S.ENV,$ptascii("twin")) = (n_twin_cv)',
        '$lookup(S.ENV,$ptascii("input")) = (n_input_cv)',
        'S.STORE[n_slot] = DEFINED (POBJECT n_closure)',
        'S.STORE[n_twin_cv] = DEFINED (POBJECT n_twin)',
        'S.STORE[n_input_cv] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        f'S.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {edge}) (ALIAS n_slot)]',
        'S.ARRAYS[n_input].NEXT = 91',
        f'S.ARRAYS[n_caller] = $array_insert(S.ARRAYS[n_input],KINT 90,DIRECT (PINT 31))',
        *named('S','n_closure','porigin_shared'), *named('S','n_twin','porigin_shared'),
        '$function_at(S.FUNCTIONS,porigin_shared) = (pfunction_shared)',
        'pfunction_shared.NAME = ($ptascii("v88ArrayCounter"))',
        'n_closure =/= n_twin', 'n_root = |S.ARRAYS|',
        f'parray_root = $array_insert($array_empty(),KSTRING {edge},DIRECT (POBJECT n_closure))',
        f'pvalueclass_tree = PVARRAY false ([(KSTRING {edge},PVOBJECT)])',
        '$dynamic_array_value(S,PARRAY n_input,eps,true) = ((S_validation,PARRAY n_root,pvalueclass_tree))',
        'S_validation.ARRAYS = S.ARRAYS ++ [parray_root]',
        *common.step('S_row','S','PBOOL true'), 'S_row.TODO = ptask_initial*',
        'S_row.ARRAYS = S_validation.ARRAYS', 'S_row.OBJECTS = S.OBJECTS', 'S_row.STORE = S.STORE',
        'S_row.USERCONSTANTS = [puserconstant_row]',
        'puserconstant_row.ORIGIN = pconfigcall.SITE',
        'puserconstant_row.VALUE = PARRAY n_root', 'puserconstant_row.CLASS = pvalueclass_tree',
        '$dynamic_global_constant_value(S_row,$ptascii("V88_NAMED_ARRAY")) = (PARRAY n_root)',
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
        'S_observed.STATICS = [pstaticcell_shared]', *counter('S_observed','shared',4),
        '$heap_edge_owners(HCELL n_counter_shared,$heap_graph(S_observed).EDGES,[HOBJECT n_closure,HOBJECT n_twin]) = 0',
        '$heap_owners($heap_graph(S_observed),HOBJECT n_closure) = 3',
        'S_observed.USERCONSTANTS = S_row.USERCONSTANTS',
        '$test_outputs(S_observed.EVENTS) = ' + term(before),
        *define.finish('S_observed',stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS', 'S_final.ARRAYS[n_root] = parray_root',
        'S_final.STATICS = S_observed.STATICS', *counter('S_final','shared',5),
        '$node_children(S_final,HOBJECT n_closure) = eps',
        '$heap_owners($heap_graph(S_final),HOBJECT n_closure) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1',
        '~(HOBJECT n_twin <- S_final.ALLOCATIONS)',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)', '~(HARRAY n_caller <- S_final.ALLOCATIONS)',
        '~(HARRAY n_copy <- S_final.ALLOCATIONS)', '~(HCELL n_slot <- S_final.ALLOCATIONS)',
        '~(HCELL n_bucket <- S_final.ALLOCATIONS)']


def checks(initial, name, stdout):
    return (direct if name == DIRECT else array)(initial, stdout)


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = runtime.packet_process


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
