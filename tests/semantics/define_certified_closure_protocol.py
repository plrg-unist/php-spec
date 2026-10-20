#!/usr/bin/env python3
"""Reached certified Closure publication, duplicate roots and array COW."""
import argparse
from pathlib import Path
import sys

import define_stdclass_array_duplicate_protocol as prior
import define_certified_closure_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text = prior.ROOT, prior.text
DIRECT = 'direct-closure-publication-and-normal-duplicate'
PREFIX = define.PREFIX + r'''
dec $test_closure_value_unset(pstate) : bool
def $test_closure_value_unset(S) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_slot) metadata_slot) :: expression_tail*
  -- if $base64(text_slot) = $ptascii("slot")
def $test_closure_value_unset(S) = false -- otherwise
dec $test_closure_value_unset_seek(pstate, nat) : pstate
def $test_closure_value_unset_seek(S,0) = S
def $test_closure_value_unset_seek(S,n) = S
  -- if $(n > 0)
  -- if $test_closure_value_unset(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_closure_value_unset_seek(S,n) = $test_closure_value_unset_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_closure_value_unset(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def certified(state, obj, label, donor):
    return [f'$user_constant_at({state}.USERCONSTANTS,{text(donor)}) = (puserconstant_{label})',
        f'puserconstant_{label}.VALUE = POBJECT {obj}',
        f'puserconstant_{label}.CLASS = PVCLOSURE {obj} porigin_{label}',
        f'$constant_callable_record({state}.CONSTANTCLOSURES,{obj}) = (pconstantclosure_{label})',
        f'pconstantclosure_{label}.SITE = porigin_{label}',
        f'pconstantclosure_{label}.DECL = puserconstant_{label}.ORIGIN',
        f'$global_constant_callable_header({state},pconstantclosure_{label})',
        f'$constant_value_class_valid({state},POBJECT {obj},PVCLOSURE {obj} porigin_{label})',
        f'$dynamic_define_value_class({state},POBJECT {obj}) = (PVCLOSURE {obj} porigin_{label})']


def counter(state, obj, label, value):
    return [f'{state}.OBJECTS[{obj}] = CONSTANTCLOSURE porigin_{label} (REALCLOSURE porigin_{label} eps ([pstaticcell_{label}]))',
        f'n_counter_{label} = pstaticcell_{label}.CELL',
        f'n_counter_{label} <- {state}.REFCELLS',
        f'HCELL n_counter_{label} <- {state}.ALLOCATIONS',
        f'{state}.STORE[n_counter_{label}] = DEFINED (PINT {value})']


def controls():
    values = ['S_missing = S[.CONSTANTCLOSURES = [pconstantclosure_right]]',
        'S_plain = S_missing[.OBJECTS[n_left] = REALCLOSURE porigin_left eps eps]',
        '$typed_closure(S_plain,n_left)',
        '$dynamic_define_value_class(S_plain,POBJECT n_left) = (PVOBJECT)',
        '~$constant_value_class_valid(S_plain,POBJECT n_left,PVCLOSURE n_left porigin_left)',
        '~$user_constants_valid(S_plain,S_plain.USERCONSTANTS)',
        'S_bad_site = S[.CONSTANTCLOSURES[0].SITE = pconfigcall.SITE]',
        'S_bad_prefix = S[.CONSTANTCLOSURES[0].PREFIX = $(|S.DECLARATIONS| + 1)]',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_left)]']
    values += [f'$dynamic_define_value_class({state},POBJECT n_left) = eps'
        for state in ('S_missing','S_bad_site','S_bad_prefix','S_dead')]
    values += ['~$constant_value_class_valid(S,POBJECT n_left,PVCLOSURE n_right porigin_right)',
        '$dynamic_define_value_class(S,POBJECT (|S.OBJECTS|)) = eps']
    return values


def direct(initial, stdout):
    values = [*initial, *define.reach('S','S_initial',0,'V83_DIRECT'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        '$dynamic_define_values(pconfigcall) = (($ptascii("V83_DIRECT"),POBJECT n_left))',
        '$config_invoke_valid(S,pconfigcall)',
        *certified('S','n_left','left','V83_LEFT'),
        *certified('S','n_right','right','V83_RIGHT'),
        'n_left =/= n_right',
        'S.USERCONSTANTS = [puserconstant_left,puserconstant_right]',
        'S.CONSTANTCLOSURES = [pconstantclosure_left,pconstantclosure_right]',
        'S.OBJECTS[n_left] = CONSTANTCLOSURE porigin_left (REALCLOSURE porigin_left eps eps)',
        'S.OBJECTS[n_right] = CONSTANTCLOSURE porigin_right (REALCLOSURE porigin_right eps eps)',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        '$lookup(S.ENV,$ptascii("candidate")) = (n_candidate)',
        '$lookup(S.ENV,$ptascii("api")) = (n_api)',
        '$lookup(S.ENV,$ptascii("calls")) = (n_calls)',
        'S.STORE[n_candidate] = DEFINED (POBJECT n_left)',
        '$heap_owners($heap_graph(S),HOBJECT n_left) = 3',
        *controls(),
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        '$test_running(S_pause) = S',
        *common.step('S_row','S','PBOOL true'),
        '$drive_steps($test_running(S_pause),1) = S_row_found',
        'S_row.TODO = ptask_tail*',
        '$user_constant_at(S_row.USERCONSTANTS,$ptascii("V83_DIRECT")) = (puserconstant_row)',
        'S_row.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant_row]',
        'puserconstant_row.ORIGIN = pconfigcall.SITE',
        'puserconstant_row.VALUE = POBJECT n_left',
        'puserconstant_row.CLASS = PVCLOSURE n_left porigin_left',
        'puserconstant_row.READS = eps', 'puserconstant_row.RECEIVES = eps',
        '$heap_owners($heap_graph(S_row),HOBJECT n_left) = 3']
    values += [f'S_row.{field} = S.{field}' for field in
        ['OBJECTS','ARRAYS','ALLOCATIONS','STORE','STATICS','CONSTANTCLOSURES','CLOSURESCOPES','EVENTS']]
    values += [*define.reach('S_dup','S_row',1,'V83_DIRECT'),
        'S_dup.TODO = (CONFIG_INVOKE pconfigcall_dup) :: ptask_dup*',
        '$dynamic_define_values(pconfigcall_dup) = (($ptascii("V83_DIRECT"),POBJECT n_right))',
        'n_constants = |S_dup.USERCONSTANTS|', 'n_constants = 3',
        'S_dup.USERCONSTANTS = S_row.USERCONSTANTS',
        '$dynamic_constant_duplicate_valid(S_dup,pconfigcall_dup,n_constants)',
        'S_dup.STORE[n_candidate] = DEFINED (POBJECT n_right)',
        'S_dup.STORE[n_calls] = DEFINED (PINT 0)',
        *counter('S_dup','n_left','left',8),
        'S_dup.OBJECTS[n_right] = S.OBJECTS[n_right]',
        '$heap_owners($heap_graph(S_dup),HOBJECT n_right) = 3',
        *common.step('S_warning','S_dup'),
        'S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warning*',
        'perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup n_constants',
        'perrorcall.LEVEL = 2', 'S_warning.USERCONSTANTS = S_dup.USERCONSTANTS',
        *define.reach('S_resume','S_warning',4,'V83_DIRECT'),
        'S_resume.TODO = (DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup n_constants) :: ptask_warning*',
        'S_resume.STORE[n_candidate] = DEFINED (POBJECT n_left)',
        'S_resume.STORE[n_calls] = DEFINED (PINT 1)',
        'S_resume.STORE[n_api] = DEFINED pvalue_api',
        '$string_bytes(pvalue_api) = ($ptascii("constant"))',
        *counter('S_resume','n_left','left',8), *counter('S_resume','n_right','right',18),
        '$dynamic_constant_duplicate_valid(S_resume,pconfigcall_dup,n_constants)',
        '$heap_owners($heap_graph(S_resume),HOBJECT n_right) = 2',
        *common.step('S_false','S_resume','PBOOL false'),
        'S_false.TODO = ptask_warning*', 'S_false.USERCONSTANTS = S_dup.USERCONSTANTS',
        'S_false.OBJECTS = S_resume.OBJECTS', 'S_false.STORE = S_resume.STORE',
        '$heap_owners($heap_graph(S_false),HOBJECT n_right) = 1',
        *define.finish('S_false',stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_final.CONSTANTCLOSURES = S.CONSTANTCLOSURES',
        *counter('S_final','n_left','left',9), *counter('S_final','n_right','right',19),
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 2',
        '$heap_owners($heap_graph(S_final),HOBJECT n_right) = 1',
        '$heap_owners($heap_graph(S_final),HCELL n_counter_left) = 1',
        '$heap_owners($heap_graph(S_final),HCELL n_counter_right) = 1']
    return values


def array(initial, stdout):
    edge, call = text('edge'), text('call')
    values = [*initial, *define.reach('S','S_initial',0,'V83_ARRAY'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        '$dynamic_define_values(pconfigcall) = (($ptascii("V83_ARRAY"),PARRAY n_input))',
        'pconfigcall.NAMED', '$dynamic_array_call_valid(S,pconfigcall)',
        *certified('S','n_left','left','V83_ARRAY_LEFT'),
        *certified('S','n_right','right','V83_ARRAY_RIGHT'),
        'n_left =/= n_right',
        'S.USERCONSTANTS = [puserconstant_left,puserconstant_right]',
        'S.CONSTANTCLOSURES = [pconstantclosure_left,pconstantclosure_right]',
        '$lookup(S.ENV,$ptascii("cell")) = (n_cell)',
        '$lookup(S.ENV,$ptascii("input")) = (n_input_cv)',
        'n_cell <- S.REFCELLS',
        'S.STORE[n_cell] = DEFINED (PARRAY n_source_child)',
        'S.STORE[n_input_cv] = DEFINED (PARRAY n_caller)', 'n_caller =/= n_input',
        f'S.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {edge}) (ALIAS n_cell)]',
        'S.ARRAYS[n_input].NEXT = 91',
        f'S.ARRAYS[n_caller] = $array_insert(S.ARRAYS[n_input],KINT 90,DIRECT (PINT 31))',
        f'S.ARRAYS[n_source_child].ITEMS = [ENTRY (KSTRING {call}) (DIRECT (POBJECT n_right))]',
        'S.OBJECTS[n_left] = CONSTANTCLOSURE porigin_left (REALCLOSURE porigin_left eps eps)',
        'S.OBJECTS[n_right] = CONSTANTCLOSURE porigin_right (REALCLOSURE porigin_right eps eps)',
        '$heap_owners($heap_graph(S),HOBJECT n_right) = 2',
        '$heap_owners($heap_graph(S),HARRAY n_input) = 1',
        # Fold projections remain undriven; the actual CFG makes the row below.
        'n_child = |S.ARRAYS|', 'n_root = $(n_child + 1)',
        f'parray_child = $array_insert($array_empty(),KSTRING {call},DIRECT (POBJECT n_right))',
        f'parray_root = $array_insert($array_empty(),KSTRING {edge},DIRECT (PARRAY n_child))',
        f'pvalueclass_tree = PVARRAY false ([(KSTRING {edge},PVARRAY false ([(KSTRING {call},PVCLOSURE n_right porigin_right)]))])',
        '$dynamic_array_value(S,PARRAY n_input,eps,true) = ((S_validation,PARRAY n_root,pvalueclass_tree))',
        'S_validation.ARRAYS = S.ARRAYS ++ [parray_child,parray_root]',
        'S_validation.OBJECTS = S.OBJECTS', 'S_validation.STORE = S.STORE',
        *common.step('S_row','S','PBOOL true'),
        'S_row.TODO = ptask_tail*',
        'S_row.ARRAYS = S_validation.ARRAYS',
        'S_row.OBJECTS = S.OBJECTS', 'S_row.STORE = S.STORE',
        '$user_constant_at(S_row.USERCONSTANTS,$ptascii("V83_ARRAY")) = (puserconstant_row)',
        'S_row.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant_row]',
        'puserconstant_row.VALUE = PARRAY n_root',
        'puserconstant_row.CLASS = pvalueclass_tree',
        'puserconstant_row.ORIGIN = pconfigcall.SITE',
        '$heap_owners($heap_graph(S_row),HOBJECT n_right) = 3',
        '$heap_owners($heap_graph(S_row),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_row),HARRAY n_child) = 1',
        '~(HARRAY n_input <- S_row.ALLOCATIONS)',
        '$array_append_key(S_row.ARRAYS[n_root]) = KINT 0',
        '$dynamic_global_constant_array_tree(S_row,PARRAY n_root,pvalueclass_tree)',
        'S_recovered_found = $test_closure_value_unset_seek(S_row,1500)',
        r'S_recovered_found.COMPLETION = NORMAL \/ S_recovered_found.COMPLETION = BUDGET',
        'S_recovered = $test_running(S_recovered_found)',
        '$test_closure_value_unset(S_recovered)', *common.public('S_recovered'),
        '$lookup(S_recovered.ENV,$ptascii("copy")) = (n_copy_cv)',
        '$lookup(S_recovered.ENV,$ptascii("again")) = (n_again_cv)',
        '$lookup(S_recovered.ENV,$ptascii("slot")) = (n_slot)',
        'S_recovered.STORE[n_copy_cv] = DEFINED (PARRAY n_copy_root)',
        'S_recovered.STORE[n_again_cv] = DEFINED (PARRAY n_root)',
        'n_copy_root =/= n_root',
        f'$entry_lookup(S_recovered.ARRAYS[n_copy_root].ITEMS,KSTRING {edge}) = (DIRECT (PARRAY n_copy_child))',
        'n_copy_child =/= n_child',
        f'S_recovered.ARRAYS[n_copy_child].ITEMS = [ENTRY (KSTRING {call}) (ALIAS n_slot)]',
        'n_slot <- S_recovered.REFCELLS', 'HCELL n_slot <- S_recovered.ALLOCATIONS',
        'S_recovered.STORE[n_slot] = DEFINED (POBJECT n_left)',
        f'$entry_lookup(S_recovered.ARRAYS[n_copy_root].ITEMS,KINT 0) = (DIRECT (PINT 53))',
        'S_recovered.ARRAYS[n_copy_root].NEXT = 1',
        'S_recovered.ARRAYS[n_root] = parray_root',
        'S_recovered.ARRAYS[n_child] = parray_child',
        'S_recovered.STORE[n_cell] = DEFINED (PARRAY n_source_left)',
        f'S_recovered.ARRAYS[n_source_left].ITEMS = [ENTRY (KSTRING {call}) (DIRECT (POBJECT n_left))]',
        *counter('S_recovered','n_left','left',8), *counter('S_recovered','n_right','right',19),
        'S_recovered.USERCONSTANTS = S_row.USERCONSTANTS',
        *define.finish('S_recovered',stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_final.CONSTANTCLOSURES = S.CONSTANTCLOSURES',
        *counter('S_final','n_left','left',8), *counter('S_final','n_right','right',19),
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 1',
        '$heap_owners($heap_graph(S_final),HOBJECT n_right) = 2',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_child) = 1',
        'S_final.ARRAYS[n_root] = parray_root', 'S_final.ARRAYS[n_child] = parray_child',
        '~(HARRAY n_caller <- S_final.ALLOCATIONS)', '~(HARRAY n_copy_root <- S_final.ALLOCATIONS)',
        '~(HARRAY n_copy_child <- S_final.ALLOCATIONS)', '~(HCELL n_cell <- S_final.ALLOCATIONS)',
        '~(HCELL n_slot <- S_final.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_final),HCELL n_counter_left) = 1',
        '$heap_owners($heap_graph(S_final),HCELL n_counter_right) = 1']
    return values


def checks(initial, name, stdout):
    return (direct if name == DIRECT else array)(initial, stdout)


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = packet.process


def process(command, directory, timeout, cwd):
    if directory.parent.name in sources.family.CASES:
        timeout = 150
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
