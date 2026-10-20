#!/usr/bin/env python3
"""Reached bare REAL Closure publication, lexical/statics and query COW."""
import argparse
from pathlib import Path
import sys

import define_stdclass_array_duplicate_protocol as prior
import define_runtime_closure_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
DIRECT = 'runtime-real-closure-publication-and-normal-duplicate'
PREFIX = define.PREFIX + r'''
dec $test_runtime_real_unset(pstate, preqbytes) : bool
def $test_runtime_real_unset(S,preqbytes) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_name) metadata_name) :: expression_tail*
  -- if $base64(text_name) = preqbytes
def $test_runtime_real_unset(S,preqbytes) = false -- otherwise
dec $test_runtime_real_unset_seek(pstate, preqbytes, nat) : pstate
def $test_runtime_real_unset_seek(S,preqbytes,0) = S
def $test_runtime_real_unset_seek(S,preqbytes,n) = S
  -- if $(n > 0)
  -- if $test_runtime_real_unset(S,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_runtime_real_unset_seek(S,preqbytes,n) = $test_runtime_real_unset_seek($drive_steps($test_running(S),1),preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_runtime_real_unset(S,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def real(state, obj):
    return [f'$typed_closure({state},{obj})',
        f'$closure_live_object_valid({state},{obj})',
        f'$closure_scope_at({state}.CLOSURESCOPES,{obj}) = eps',
        f'$closure_scope_complete({state},[HOBJECT {obj}])',
        f'$constant_callable_record({state}.CONSTANTCLOSURES,{obj}) = eps',
        f'$dynamic_runtime_object({state},{obj})',
        f'$dynamic_define_value_class({state},POBJECT {obj}) = (PVOBJECT)']


def counter(state, obj, origin, captures, label, value):
    return [f'{state}.OBJECTS[{obj}] = REALCLOSURE {origin} {captures} ([pstaticcell_{label}])',
        f'n_counter_{label} = pstaticcell_{label}.CELL',
        f'n_counter_{label} <- {state}.REFCELLS',
        f'HCELL n_counter_{label} <- {state}.ALLOCATIONS',
        f'{state}.STORE[n_counter_{label}] = DEFINED (PINT {value})']


def unset(state, start, name):
    return [f'{state}_found = $test_runtime_real_unset_seek({start},{text(name)},1500)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_runtime_real_unset({state},{text(name)})', *common.public(state)]


def controls():
    return ['~$global_constant_class_supported(PVOBJECT)',
        '~$global_constant_class_supported(PVARRAY false ([(KSTRING ($ptascii("edge")),PVOBJECT)]))',
        '$constant_value_class_valid(S,POBJECT n_left,PVOBJECT)',
        '~$constant_value_class_valid(S,POBJECT n_left,PVCLOSURE n_left pconfigcall.SITE)',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_left)]',
        '$dynamic_define_value_class(S_dead,POBJECT n_left) = eps',
        '~$dynamic_runtime_object(S,|S.OBJECTS|)',
        'S_incomplete = S[.OBJECTS[n_left] = REALCLOSURE porigin_left ([UNINITIALIZED]) eps]',
        '~$typed_closure(S_incomplete,n_left)',
        '~$dynamic_runtime_object(S_incomplete,n_left)',
        'S_busy = S[.TODO = (CLOSURE_CAPTURE n_left 1) :: S.TODO]',
        '~$typed_closure(S_busy,n_left)', '~$dynamic_runtime_object(S_busy,n_left)',
        'S_internal = S[.OBJECTS[n_left] = INTRINSICCLOSURE INTRINSIC_DEFINE]',
        '~$dynamic_runtime_object(S_internal,n_left)',
        'S_named = S[.OBJECTS[n_left] = NAMEDCLOSURE porigin_left]',
        '~$dynamic_runtime_object(S_named,n_left)',
        'S_wrapped = S[.OBJECTS[n_left] = CONSTANTCLOSURE pconfigcall.SITE (S.OBJECTS[n_left])]',
        '$typed_closure(S_wrapped,n_left)',
        '$dynamic_define_value_class(S_wrapped,POBJECT n_left) = eps',
        'pconstantclosure_bad = {OBJECT n_left,SITE pconfigcall.SITE,DECL pconfigcall.SITE,PREFIX (|S.DECLARATIONS|)}',
        'S_bad_record = S[.CONSTANTCLOSURES = [pconstantclosure_bad]]',
        '$dynamic_define_value_class(S_bad_record,POBJECT n_left) = eps']


def direct(initial, stdout):
    values = [*initial, *define.reach('S','S_initial',0,'V85_REAL'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        '$dynamic_define_values(pconfigcall) = (($ptascii("V85_REAL"),POBJECT n_left))',
        '$config_invoke_valid(S,pconfigcall)', 'pconfigcall.NAMED',
        'S.USERCONSTANTS = eps', 'S.CONSTANTCLOSURES = eps',
        '$lookup(S.ENV,$ptascii("left")) = (n_left_cv)',
        '$lookup(S.ENV,$ptascii("right")) = (n_right_cv)',
        '$lookup(S.ENV,$ptascii("candidate")) = (n_candidate)',
        '$lookup(S.ENV,$ptascii("api")) = (n_api)',
        '$lookup(S.ENV,$ptascii("cell")) = (n_cell)',
        '$lookup(S.ENV,$ptascii("calls")) = (n_calls)',
        'S.STORE[n_left_cv] = DEFINED (POBJECT n_left)',
        'S.STORE[n_right_cv] = DEFINED (POBJECT n_right)',
        'S.STORE[n_candidate] = DEFINED (POBJECT n_right)', 'n_left =/= n_right',
        'S.STORE[n_api] = DEFINED pvalue_api', '$string_bytes(pvalue_api) = ($ptascii("constant"))',
        'S.STORE[n_cell] = DEFINED (PINT 23)', 'n_cell <- S.REFCELLS',
        'S.OBJECTS[n_left] = REALCLOSURE porigin_left ([ALIAS n_cell]) eps',
        'S.OBJECTS[n_right] = REALCLOSURE porigin_right eps eps',
        *real('S','n_left'), *real('S','n_right'),
        '$node_children(S,HOBJECT n_left) = [HCELL n_cell]',
        '$heap_owners($heap_graph(S),HOBJECT n_left) = 2',
        '$heap_owners($heap_graph(S),HOBJECT n_right) = 2',
        '$heap_owners($heap_graph(S),HCELL n_cell) = 2',
        '$heap_edge_owners(HCELL n_cell,$heap_graph(S).EDGES,[HOBJECT n_left]) = 1',
        *controls(),
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]', '$test_running(S_pause) = S',
        *common.step('S_row','S','PBOOL true'),
        '$drive_steps($test_running(S_pause),1) = S_row_found',
        'S_row.TODO = ptask_initial*', 'S_row.USERCONSTANTS = [puserconstant_row]',
        'puserconstant_row.ORIGIN = pconfigcall.SITE',
        'puserconstant_row.VALUE = POBJECT n_left', 'puserconstant_row.CLASS = PVOBJECT',
        '$heap_owners($heap_graph(S_row),HOBJECT n_left) = 2']
    values += [f'S_row.{field} = S.{field}' for field in
        ['OBJECTS','ARRAYS','ALLOCATIONS','STORE','STATICS','CLOSURESCOPES','CONSTANTCLOSURES','EVENTS']]
    values += ['puserconstant_bad = puserconstant_row[.ORIGIN = PORIGIN 0 eps]',
        '$dynamic_global_constant_value(S_row[.USERCONSTANTS = [puserconstant_bad]],$ptascii("V85_REAL")) = eps',
        *common.reach('S_query','S_row',0,'V85_REAL'),
        'S_query.TODO = (CONFIG_INVOKE pconfigcall_query) :: ptask_query*',
        '$dynamic_global_constant_valid(S_query,pconfigcall_query)',
        '$dynamic_global_constant_value(S_query,$ptascii("V85_REAL")) = (POBJECT n_left)',
        '$heap_owners($heap_graph(S_query),HOBJECT n_left) = 2',
        *common.step('S_value','S_query','POBJECT n_left'),
        '$heap_owners($heap_graph(S_value),HOBJECT n_left) = 3']
    values += [f'S_value.{field} = S_query.{field}' for field in
        ['OBJECTS','ARRAYS','ALLOCATIONS','STORE','STATICS','USERCONSTANTS']]
    values += [*define.reach('S_dup','S_value',1,'V85_REAL'),
        'S_dup.TODO = (CONFIG_INVOKE pconfigcall_dup) :: ptask_dup*',
        '$dynamic_define_values(pconfigcall_dup) = (($ptascii("V85_REAL"),POBJECT n_right))',
        '$dynamic_constant_duplicate_valid(S_dup,pconfigcall_dup,1)',
        'S_dup.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_dup.STORE[n_candidate] = DEFINED (POBJECT n_right)',
        'S_dup.STORE[n_calls] = DEFINED (PINT 0)', 'S_dup.STORE[n_cell] = DEFINED (PINT 23)',
        *counter('S_dup','n_left','porigin_left','([ALIAS n_cell])','left',2),
        *counter('S_dup','n_right','porigin_right','eps','right',101),
        '$heap_owners($heap_graph(S_dup),HOBJECT n_left) = 3',
        '$heap_owners($heap_graph(S_dup),HOBJECT n_right) = 3',
        # Callable type alone does not certify a malformed static-cell edge.
        'S_static_dead = S_dup[.ALLOCATIONS = $destruction_node_delete(S_dup.ALLOCATIONS,HCELL n_counter_left)]',
        '$typed_closure(S_static_dead,n_left)', '~$closure_live_object_valid(S_static_dead,n_left)',
        '~$dynamic_runtime_object(S_static_dead,n_left)',
        *common.step('S_warning','S_dup'),
        'S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warning*',
        'perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup 1',
        'perrorcall.LEVEL = 2', '$error_call_valid(S_warning,perrorcall)',
        *define.reach('S_resume','S_warning',4,'V85_REAL'),
        'S_resume.TODO = (DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup 1) :: ptask_warning*',
        'S_resume.STORE[n_candidate] = DEFINED PNULL',
        'S_resume.STORE[n_calls] = DEFINED (PINT 1)', 'S_resume.STORE[n_cell] = DEFINED (PINT 41)',
        'S_resume.USERCONSTANTS = S_row.USERCONSTANTS',
        *counter('S_resume','n_left','porigin_left','([ALIAS n_cell])','left',2),
        *counter('S_resume','n_right','porigin_right','eps','right',102),
        '$heap_owners($heap_graph(S_resume),HOBJECT n_right) = 2',
        '$heap_edge_owners(HCELL n_cell,$heap_graph(S_resume).EDGES,[HOBJECT n_left]) = 1',
        *common.step('S_false','S_resume','PBOOL false'),
        'S_false.TODO = ptask_warning*', 'S_false.USERCONSTANTS = S_row.USERCONSTANTS',
        '$heap_owners($heap_graph(S_false),HOBJECT n_right) = 1',
        *unset('S_observed','S_false','stored'),
        *counter('S_observed','n_left','porigin_left','([ALIAS n_cell])','left',4),
        *counter('S_observed','n_right','porigin_right','eps','right',102),
        'S_observed.STORE[n_cell] = DEFINED (PINT 41)',
        '$test_outputs(S_observed.EVENTS) = ' + term(stdout[:-2]),
        *define.finish('S_observed',stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS', 'S_final.CONSTANTCLOSURES = eps',
        *counter('S_final','n_left','porigin_left','([ALIAS n_cell])','left',4),
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 1',
        '$heap_owners($heap_graph(S_final),HCELL n_cell) = 1',
        '$heap_owners($heap_graph(S_final),HCELL n_counter_left) = 1',
        '~(HOBJECT n_right <- S_final.ALLOCATIONS)',
        '~(HCELL n_counter_right <- S_final.ALLOCATIONS)']
    return values


def array(initial, stdout):
    edge = text('edge')
    values = [*initial, *define.reach('S','S_initial',0,'V85_REAL_ARRAY'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        '$dynamic_define_values(pconfigcall) = (($ptascii("V85_REAL_ARRAY"),PARRAY n_input))',
        '$dynamic_array_call_valid(S,pconfigcall)', 'S.USERCONSTANTS = eps', 'S.CONSTANTCLOSURES = eps',
        '$lookup(S.ENV,$ptascii("cell")) = (n_cell)',
        '$lookup(S.ENV,$ptascii("slot")) = (n_slot)',
        '$lookup(S.ENV,$ptascii("input")) = (n_input_cv)',
        'S.STORE[n_cell] = DEFINED (PINT 23)',
        'S.STORE[n_slot] = DEFINED (POBJECT n_closure)',
        'S.STORE[n_input_cv] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        f'S.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {edge}) (ALIAS n_slot)]',
        'S.ARRAYS[n_input].NEXT = 91',
        f'S.ARRAYS[n_caller] = $array_insert(S.ARRAYS[n_input],KINT 90,DIRECT (PINT 31))',
        'S.OBJECTS[n_closure] = REALCLOSURE porigin_closure ([ALIAS n_cell]) eps',
        *real('S','n_closure'),
        '$heap_owners($heap_graph(S),HOBJECT n_closure) = 1',
        '$heap_edge_owners(HCELL n_cell,$heap_graph(S).EDGES,[HOBJECT n_closure]) = 1',
        'n_root = |S.ARRAYS|',
        f'parray_root = $array_insert($array_empty(),KSTRING {edge},DIRECT (POBJECT n_closure))',
        f'pvalueclass_tree = PVARRAY false ([(KSTRING {edge},PVOBJECT)])',
        '$dynamic_array_value(S,PARRAY n_input,eps,true) = ((S_validation,PARRAY n_root,pvalueclass_tree))',
        'S_validation.ARRAYS = S.ARRAYS ++ [parray_root]',
        *common.step('S_row','S','PBOOL true'), 'S_row.TODO = ptask_initial*',
        'S_row.ARRAYS = S_validation.ARRAYS', 'S_row.OBJECTS = S.OBJECTS', 'S_row.STORE = S.STORE',
        'S_row.USERCONSTANTS = [puserconstant_row]',
        'puserconstant_row.ORIGIN = pconfigcall.SITE',
        'puserconstant_row.VALUE = PARRAY n_root', 'puserconstant_row.CLASS = pvalueclass_tree',
        '$dynamic_global_constant_value(S_row,$ptascii("V85_REAL_ARRAY")) = (PARRAY n_root)',
        '$heap_owners($heap_graph(S_row),HOBJECT n_closure) = 2',
        '$array_append_key(S_row.ARRAYS[n_root]) = KINT 0',
        '~(HARRAY n_input <- S_row.ALLOCATIONS)',
        *unset('S_observed','S_row','bucket'),
        '$lookup(S_observed.ENV,$ptascii("copy")) = (n_copy_cv)',
        '$lookup(S_observed.ENV,$ptascii("again")) = (n_again_cv)',
        '$lookup(S_observed.ENV,$ptascii("bucket")) = (n_bucket)',
        'S_observed.STORE[n_copy_cv] = DEFINED (PARRAY n_copy)',
        'S_observed.STORE[n_again_cv] = DEFINED (PARRAY n_root)', 'n_copy =/= n_root',
        f'$entry_lookup(S_observed.ARRAYS[n_copy].ITEMS,KSTRING {edge}) = (ALIAS n_bucket)',
        'S_observed.STORE[n_bucket] = DEFINED PNULL', 'S_observed.STORE[n_slot] = DEFINED PNULL',
        'S_observed.STORE[n_cell] = DEFINED (PINT 41)',
        f'$entry_lookup(S_observed.ARRAYS[n_copy].ITEMS,KINT 0) = (DIRECT (PINT 53))',
        'S_observed.ARRAYS[n_copy].NEXT = 1', 'S_observed.ARRAYS[n_root] = parray_root',
        *counter('S_observed','n_closure','porigin_closure','([ALIAS n_cell])','array',2),
        '$heap_owners($heap_graph(S_observed),HOBJECT n_closure) = 3',
        '$heap_edge_owners(HCELL n_cell,$heap_graph(S_observed).EDGES,[HOBJECT n_closure]) = 1',
        'S_observed.USERCONSTANTS = S_row.USERCONSTANTS',
        '$test_outputs(S_observed.EVENTS) = ' + term(stdout[:-2]),
        *define.finish('S_observed',stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS', 'S_final.CONSTANTCLOSURES = eps',
        'S_final.ARRAYS[n_root] = parray_root',
        *counter('S_final','n_closure','porigin_closure','([ALIAS n_cell])','array',2),
        '$heap_owners($heap_graph(S_final),HOBJECT n_closure) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_final),HCELL n_cell) = 1',
        '$heap_owners($heap_graph(S_final),HCELL n_counter_array) = 1',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)', '~(HARRAY n_caller <- S_final.ALLOCATIONS)',
        '~(HARRAY n_copy <- S_final.ALLOCATIONS)',
        '~(HCELL n_slot <- S_final.ALLOCATIONS)', '~(HCELL n_bucket <- S_final.ALLOCATIONS)']
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
