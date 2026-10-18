#!/usr/bin/env python3
"""Reached nested empty copy classes, query COW and normal duplicate cleanup."""
import argparse
from pathlib import Path
import sys

import define_stdclass_array_duplicate_protocol as prior
import define_nested_empty_array_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text = prior.ROOT, prior.text
PREFIX = prior.PREFIX + r'''
dec $test_nested_empty_release_front(pstate) : bool
def $test_nested_empty_release_front(S) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata_unset)) :: ptask_tail*
  -- if expression* = expression_head :: expression_tail*
  -- if expression_head = NExprVariable (BYTES text_input) metadata_variable
  -- if $base64(text_input) = $ptascii("input")
  -- if $lookup(S.ENV,$ptascii("copy")) = (n_copy)
def $test_nested_empty_release_front(S) = false -- otherwise
dec $test_nested_empty_release_seek(pstate, nat) : pstate
def $test_nested_empty_release_seek(S,0) = S
def $test_nested_empty_release_seek(S,n) = S
  -- if $(n > 0)
  -- if $test_nested_empty_release_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_nested_empty_release_seek(S,n) = $test_nested_empty_release_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_nested_empty_release_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def checks(initial, name, stdout):
    duplicate = name.startswith('selected-')
    target = 'V70_EVAL_TARGET' if duplicate else 'V70_TREE'
    pooled, head, nested, leaf = [text(k) for k in ('pooled','head','nested','leaf' if duplicate else 'again')]
    fields = [(pooled,'PARRAY n_pooled'), (nested,'PARRAY n_input_nested')]
    if not duplicate:
        fields.insert(1,(head,'ALIAS n_cell'))
    input_items = ','.join(f'ENTRY (KSTRING {key}) (' + (value if value.startswith('ALIAS') else 'DIRECT ('+value+')') + ')' for key,value in fields)
    child = f'$array_insert($array_empty(),KSTRING {leaf},DIRECT (PARRAY n_leaf))'
    root = f'$array_insert($array_empty(),KSTRING {pooled},DIRECT (PARRAY n_pooled))'
    if not duplicate:
        root = f'$array_insert({root},KSTRING {head},DIRECT (PARRAY n_head))'
    root = f'$array_insert({root},KSTRING {nested},DIRECT (PARRAY n_nested))'
    classes = [(pooled,'PVARRAY true eps'),(nested,'pvalueclass_nested')]
    if not duplicate:
        classes.insert(1,(head,'PVARRAY false eps'))
    rootclass = 'PVARRAY false ([' + ','.join(f'(KSTRING {key},{value})' for key,value in classes) + '])'
    values = [*initial,*define.reach('S','S_initial',1 if duplicate else 0,target),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        '$dynamic_array_call_valid(S,pconfigcall)',
        '$dynamic_define_values(pconfigcall) = ((preqbytes,PARRAY n_input))',
        'preqbytes = '+text(target),'n_constants = |S.USERCONSTANTS|',
        'n_constants = '+('1' if duplicate else '0'),
        f'S.ARRAYS[n_input].ITEMS = [{input_items}]',
        f'S.ARRAYS[n_input_nested].ITEMS = [ENTRY (KSTRING {leaf}) (ALIAS n_cell)]',
        'S.STORE[n_cell] = DEFINED (PARRAY n_empty)',
        'S.ARRAYS[n_empty].ITEMS = eps','S.ARRAYS[n_empty].NEXT = 91',
        '~$array_immutable(S,n_empty)','$array_immutable(S,n_pooled)',
        'S.ARRAYS[n_pooled] = $array_empty()','n_pooled =/= n_empty',
        'n_before = |S.ARRAYS|',
        'n_pool_owners = $heap_owners($heap_graph(S),HARRAY n_pooled)']
    if not duplicate:
        values += ['S_pause = $drive_steps(S,0)','S_pause = S[.COMPLETION = BUDGET]',
            'S_resume = $test_running(S_pause)','S_resume = S']
    values += [*common.step('S_after','S' if duplicate else 'S_resume',None if duplicate else 'PBOOL true'),
        *common.public('S_after')]
    if duplicate:
        values += ['S_after.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_root pvalueclass n_constants',
            '$error_call_valid(S_after,perrorcall)',
            'n_leaf = n_before','n_nested = $(n_before + 1)','n_root = $(n_before + 2)',
            'S_after.USERCONSTANTS = S.USERCONSTANTS']
    else:
        values += ['n_head = n_before','n_leaf = $(n_before + 1)',
            'n_nested = $(n_before + 2)','n_root = $(n_before + 3)',
            'n_head =/= n_leaf','n_head =/= n_empty',
            '$user_constant_at(S_after.USERCONSTANTS,preqbytes) = (puserconstant)',
            'S_after.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant]',
            'puserconstant.VALUE = PARRAY n_root','puserconstant.CLASS = pvalueclass']
    values += ['n_leaf =/= n_empty','n_root =/= n_input','n_nested =/= n_input_nested',
        'parray_nested = '+child,'parray_root = '+root,
        'S_after.ARRAYS = S.ARRAYS ++ ['+('$array_empty(),' if not duplicate else '')+'$array_empty(),parray_nested,parray_root]',
        'S_after.STORE = S.STORE','S_after.EVENTS = S.EVENTS',
        f'pvalueclass_nested = PVARRAY false ([(KSTRING {leaf},PVARRAY false eps)])',
        'pvalueclass = '+rootclass,
        '$dynamic_array_value(S_after,PARRAY n_root,eps,false) = ((S_after,PARRAY n_root,pvalueclass))',
        '$dynamic_global_constant_array_tree(S_after,PARRAY n_root,pvalueclass)',
        '$heap_owners($heap_graph(S_after),HARRAY n_leaf) = 1',
        '$heap_owners($heap_graph(S_after),HARRAY n_nested) = 1',
        '$heap_owners($heap_graph(S_after),HARRAY n_pooled) = $(n_pool_owners + 1)',
        '$dynamic_array_value(S_after,PARRAY n_leaf,[n_root,n_nested],false) = ((S_after,PARRAY n_leaf,PVARRAY false eps))',
        '$dynamic_array_value(S_after,PARRAY n_pooled,[n_root],false) = ((S_after,PARRAY n_pooled,PVARRAY true eps))',
        # Pure seen, history, allocation and cycle controls are never driven.
        '$dynamic_array_value(S_after,PARRAY n_leaf,[n_leaf],true) = eps',
        '$dynamic_array_value(S_after,PARRAY n_leaf,[n_leaf],false) = eps',
        '$dynamic_array_value(S_after,PARRAY n_pooled,[n_pooled],true) = eps',
        '$dynamic_array_value(S_after,PARRAY n_pooled,[n_pooled],false) = eps',
        'S_history = S_after[.ARRAYS[n_leaf].NEXT = 91]',
        '$dynamic_array_value(S_history,PARRAY n_root,eps,false) = eps',
        'S_dead = S_after[.ALLOCATIONS = $destruction_node_delete(S_after.ALLOCATIONS,HARRAY n_pooled)]',
        '$dynamic_array_value(S_dead,PARRAY n_root,eps,false) = eps',
        'S_cycle = S_after[.ARRAYS[n_leaf] = $array_insert($array_empty(),KINT 0,DIRECT (PARRAY n_root))]',
        '$dynamic_array_value(S_cycle,PARRAY n_root,eps,true) = eps',
        '$dynamic_array_value(S_cycle,PARRAY n_root,eps,false) = eps',
        f'pvalueclass_wrong = $pvclass_put(pvalueclass,KSTRING {pooled},PVARRAY false eps)']
    if duplicate:
        values += ['~$dynamic_array_duplicate_valid(S_after,pconfigcall,n_root,pvalueclass_wrong,n_constants)',
            'pconfigcall.SITE = PORIGIN 1 pcpath_call','pconfigcall.SELECTION = (n_selection)',
            *prior.reach('S_done','S_after',0,target),
            'S_done.TODO = (ERROR_HANDLER_RESULT perrorcall_done) :: ptask_tail*',
            'perrorcall_done.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_root pvalueclass n_constants',
            'S_done.RESULT = KNOWN (PBOOL true)',
            'S_done.USERCONSTANTS = S.USERCONSTANTS',
            'S_done.STORE[n_cell] = DEFINED (PARRAY n_grown)',
            '$entry_lookup(S_done.ARRAYS[n_grown].ITEMS,KINT 91) = (DIRECT pvalue_source)',
            '$string_bytes(pvalue_source) = ('+text('source')+')',
            'S_done.ARRAYS[n_leaf] = $array_empty()',
            '$dynamic_array_duplicate_valid(S_done,pconfigcall,n_root,pvalueclass,n_constants)',
            *common.step('S_pending','S_done'),*common.public('S_pending'),
            'S_pending.TODO = (DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_root pvalueclass n_constants) :: ptask_tail*',
            'S_pending.EVENTS = S_done.EVENTS',
            'n_pending_pool = $heap_owners($heap_graph(S_pending),HARRAY n_pooled)',
            *common.step('S_false','S_pending','PBOOL false'),
            'S_false.USERCONSTANTS = S.USERCONSTANTS',
            '$heap_owners($heap_graph(S_false),HARRAY n_pooled) = $(n_pending_pool - 1)',
            '~(HARRAY n_root <- S_false.ALLOCATIONS)',
            '~(HARRAY n_nested <- S_false.ALLOCATIONS)',
            '~(HARRAY n_leaf <- S_false.ALLOCATIONS)',
            *define.finish('S_false',stdout),'S_final.USERCONSTANTS = S.USERCONSTANTS',
            '~(HARRAY n_grown <- S_final.ALLOCATIONS)']
    else:
        values += ['~$user_constants_valid(S_after[.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant[.CLASS = pvalueclass_wrong]]],S.USERCONSTANTS ++ [puserconstant[.CLASS = pvalueclass_wrong]])',
            *common.reach('S_query','S_after',0,target),*common.public('S_query'),
            '$dynamic_global_constant_value(S_query,preqbytes) = (PARRAY n_root)',
            'H_query = $heap_graph(S_query)','n_root_owners = $heap_owners(H_query,HARRAY n_root)',
            *common.step('S_value','S_query','PARRAY n_root'),
            'S_value.ARRAYS = S_query.ARRAYS','S_value.ALLOCATIONS = S_query.ALLOCATIONS',
            'S_value.USERCONSTANTS = S_query.USERCONSTANTS',
            '$heap_graph(S_value).EDGES = H_query.EDGES',
            '$heap_owners($heap_graph(S_value),HARRAY n_root) = $(n_root_owners + 1)',
            'S_release_found = $test_nested_empty_release_seek(S_value,5000)',
            r'S_release_found.COMPLETION = NORMAL \/ S_release_found.COMPLETION = BUDGET',
            'S_release = $test_running(S_release_found)',
            '$test_nested_empty_release_front(S_release)',*common.public('S_release'),
            '$lookup(S_release.ENV,$ptascii("copy")) = (n_copy_cell)',
            'S_release.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_root',
            f'$entry_lookup(S_release.ARRAYS[n_copy].ITEMS,KSTRING {nested}) = (DIRECT (PARRAY n_written_nested))',
            'n_written_nested =/= n_nested']
        for label, key, parent, original in [('head',head,'n_copy','n_head'),('again',leaf,'n_written_nested','n_leaf'),('pool',pooled,'n_copy','n_pooled')]:
            values += [f'$entry_lookup(S_release.ARRAYS[{parent}].ITEMS,KSTRING {key}) = (DIRECT (PARRAY n_written_{label}))',
                f'n_written_{label} =/= {original}',
                f'S_release.ARRAYS[n_written_{label}].NEXT = 1',
                f'$entry_lookup(S_release.ARRAYS[n_written_{label}].ITEMS,KINT 0) = (DIRECT pvalue_{label})',
                f'$string_bytes(pvalue_{label}) = ('+text(label)+')']
        values += ['S_release.ARRAYS[n_head] = $array_empty()',
            'S_release.ARRAYS[n_leaf] = $array_empty()',
            'S_release.ARRAYS[n_root] = parray_root',
            'S_release.ARRAYS[n_nested] = parray_nested',
            *define.finish('S_release',stdout),'S_final.USERCONSTANTS = S_after.USERCONSTANTS',
            'S_final.ARRAYS[n_root] = parray_root','S_final.ARRAYS[n_nested] = parray_nested',
            'S_final.ARRAYS[n_head] = $array_empty()','S_final.ARRAYS[n_leaf] = $array_empty()',
            '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1',
            '$heap_owners($heap_graph(S_final),HARRAY n_nested) = 1',
            '$heap_owners($heap_graph(S_final),HARRAY n_head) = 1',
            '$heap_owners($heap_graph(S_final),HARRAY n_leaf) = 1']
        values += [f'~(HARRAY {node} <- S_final.ALLOCATIONS)' for node in
            ['n_copy','n_written_nested','n_written_head','n_written_again','n_written_pool']]
    values += ['~(HARRAY n_input <- S_final.ALLOCATIONS)',
        '~(HARRAY n_input_nested <- S_final.ALLOCATIONS)',
        '~(HARRAY n_empty <- S_final.ALLOCATIONS)', '~(HCELL n_cell <- S_final.ALLOCATIONS)',
        'HARRAY n_pooled <- S_final.ALLOCATIONS','$array_immutable(S_final,n_pooled)']
    return values


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
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
