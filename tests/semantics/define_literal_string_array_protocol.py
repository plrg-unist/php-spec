#!/usr/bin/env python3
"""Reached byte-only array snapshots, literal guards and duplicate retirement."""
import argparse
from pathlib import Path
import sys

import define_stdclass_array_duplicate_protocol as prior
import define_literal_string_array_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
PREFIX = prior.PREFIX + r'''
dec $test_literal_string_bucket(pstate) : bool
def $test_literal_string_bucket(S) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE ([NExprVariable (BYTES text_slot) metadata_variable])) metadata_unset)) :: ptask_tail*
  -- if $base64(text_slot) = $ptascii("slot")
def $test_literal_string_bucket(S) = false -- otherwise
dec $test_literal_string_bucket_seek(pstate, nat) : pstate
def $test_literal_string_bucket_seek(S,0) = S
def $test_literal_string_bucket_seek(S,n) = S
  -- if $(n > 0)
  -- if $test_literal_string_bucket(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_literal_string_bucket_seek(S,n) = $test_literal_string_bucket_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_literal_string_bucket(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def table(entries):
    value = '$array_empty()'
    for key, item in entries:
        value = '$array_insert(' + value + ',KSTRING ' + text(key) + ',DIRECT (' + item + '))'
    return value


def valueclass(entries):
    return 'PVARRAY false ([' + ','.join('(KSTRING ' + text(key) + ',' + cls + ')' for key, cls in entries) + '])'


def checks(initial, name, stdout):
    selected = name.startswith('selected-')
    target = 'V72_OLD' if selected else 'V72_TREE'
    first, nested = ('label' if selected else 'plain'), 'nested'
    child_entries = [('word', 'PSTRING ' + text('first')), ('binary', 'PSTRING ' + term(b'B\0\xfe'))] if selected else [
        ('empty', 'PSTRING eps'), ('one', 'PSTRING ' + text('x')), ('binary', 'PSTRING ' + term(b'A\0\xffB'))]
    child_class = valueclass([(key, 'PVSTRING false') for key, _ in child_entries])
    tree_class = valueclass([(first, 'PVSTRING false'), (nested, 'pvalueclass_child')])
    values = [*initial, *define.reach('S', 'S_initial', 1 if selected else 0, target),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        '$dynamic_array_call_valid(S,pconfigcall)',
        '$dynamic_define_values(pconfigcall) = ((preqbytes,PARRAY n_input))',
        'preqbytes = ' + text(target),
        f'S.ARRAYS[n_input].ITEMS = [ENTRY (KSTRING {text(first)}) (DIRECT (PSTRING {text("before" if selected else "alpha")})),ENTRY (KSTRING {text(nested)}) (DIRECT (PARRAY n_input_child))]',
        'parray_child = ' + table(child_entries),
        'S.ARRAYS[n_input_child] = parray_child',
        'n_before = |S.ARRAYS|',
        'n_input_owners = $heap_owners($heap_graph(S),HARRAY n_input)',
        # Pure leaf checks preserve bytes and unknown identity in both modes.
        '$dynamic_array_value(S,PSTRING ' + term(b'A\0\xffB') + ',eps,true) = ((S,PSTRING ' + term(b'A\0\xffB') + ',PVSTRING false))',
        '$dynamic_array_value(S,PSTRING eps,eps,false) = ((S,PSTRING eps,PVSTRING false))',
        '$dynamic_array_value(S,PSTRING [256],eps,true) = eps',
        '$dynamic_constant_class(PSTRING ' + text('alpha') + ') = eps',
        '$dynamic_define_value_class(S,PSTRING ' + text('alpha') + ') = eps',
        '~$default_cacheable(PVSTRING false)',
        'pvalueclass_child = ' + child_class]
    if selected:
        values += ['pconfigcall.NAMED', 'pconfigcall.SITE = PORIGIN 1 pcpath_define',
            'pconfigcall.SELECTION = (n_selection)',
            '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
            'n_constants = |S.USERCONSTANTS|', 'n_constants = 1',
            '$user_constant_at(S.USERCONSTANTS,preqbytes) = (puserconstant_old)',
            'puserconstant_old.VALUE = PINT 17',
            '$dynamic_array_duplicate_call_valid(S,pconfigcall,n_constants)',
            *common.step('S_copy','S'), *common.public('S_copy'),
            'S_copy.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_copy*',
            'perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_root pvalueclass_tree n_constants',
            'S_copy.USERCONSTANTS = S.USERCONSTANTS', 'S_copy.EVENTS = S.EVENTS']
    else:
        values += ['$dynamic_define_known(S,pconfigcall.SITE,1) = (PARRAY n_input)',
            'HARRAY n_input <- $pools_nodes(S.POOLS)',
            'HARRAY n_input_child <- $pools_nodes(S.POOLS)',
            '$source_constant_lookup(S,preqbytes) = eps',
            'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
            'S_resume = $test_running(S_pause)', 'S_resume = S',
            *common.step('S_copy','S_resume','PBOOL true'),
            '$user_constant_at(S_copy.USERCONSTANTS,preqbytes) = (puserconstant)',
            'S_copy.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant]',
            'puserconstant.VALUE = PARRAY n_root',
            'puserconstant.ORIGIN = pconfigcall.SITE',
            'puserconstant.READS = eps', 'puserconstant.RECEIVES = eps',
            'pvalueclass_tree = puserconstant.CLASS']
    values += ['n_child = n_before', 'n_root = $(n_before + 1)',
        'n_root =/= n_input', 'n_child =/= n_input_child',
        'parray_root = ' + table([(first, 'PSTRING ' + text('before' if selected else 'alpha')), (nested, 'PARRAY n_child')]),
        'S_copy.ARRAYS = S.ARRAYS ++ [parray_child,parray_root]',
        'pvalueclass_tree = ' + tree_class,
        '$dynamic_array_value(S_copy,PARRAY n_root,eps,false) = ((S_copy,PARRAY n_root,pvalueclass_tree))',
        '$heap_owners($heap_graph(S_copy),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_copy),HARRAY n_child) = 1',
        'S_copy.STRINGDATA = S.STRINGDATA', 'S_copy.STORE = S.STORE',
        'S_copy.OBJECTS = S.OBJECTS', 'S_copy.CONSTANTSTDOBJECTS = S.CONSTANTSTDOBJECTS',
        # Pure malformed-table/class controls are never driven.
        'S_history = S_copy[.ARRAYS[n_root].NEXT = 1]',
        '$dynamic_array_value(S_history,PARRAY n_root,eps,false) = eps',
        'S_dead = S_copy[.ALLOCATIONS = $destruction_node_delete(S_copy.ALLOCATIONS,HARRAY n_child)]',
        '$dynamic_array_value(S_dead,PARRAY n_root,eps,false) = eps']
    if selected:
        values += ['$dynamic_array_duplicate_valid(S_copy,pconfigcall,n_root,pvalueclass_tree,n_constants)',
            '~$dynamic_array_duplicate_valid(S_copy,pconfigcall,n_input,pvalueclass_tree,n_constants)',
            '~$dynamic_array_duplicate_valid(S_copy,pconfigcall,n_root,PVARRAY true eps,n_constants)',
            *prior.reach('S_done','S_copy',0,target),
            'S_done.TODO = (ERROR_HANDLER_RESULT perrorcall_done) :: ptask_done*',
            'perrorcall_done.RESUME = perrorcall.RESUME',
            'S_done.RESULT = KNOWN (PBOOL true)',
            'S_done.ARRAYS[n_root] = parray_root', 'S_done.ARRAYS[n_child] = parray_child',
            'S_done.ARRAYS[n_input] = S.ARRAYS[n_input]',
            'S_done.ARRAYS[n_input_child] = parray_child',
            '$lookup(S_done.ENV,$ptascii("input")) = (n_caller)',
            'S_done.STORE[n_caller] = DEFINED (PARRAY n_caller_root)',
            'n_caller_root =/= n_input',
            '$entry_lookup(S_done.ARRAYS[n_caller_root].ITEMS,KSTRING ' + text('label') + ') = (DIRECT pvalue_after)',
            '$string_bytes(pvalue_after) = (' + text('after') + ')',
            '$entry_lookup(S_done.ARRAYS[n_caller_root].ITEMS,KSTRING ' + text('nested') + ') = (DIRECT (PARRAY n_caller_child))',
            'n_caller_child =/= n_input_child',
            '$entry_lookup(S_done.ARRAYS[n_caller_child].ITEMS,KSTRING ' + text('word') + ') = (DIRECT pvalue_second)',
            '$string_bytes(pvalue_second) = (' + text('second') + ')',
            '$dynamic_array_duplicate_valid(S_done,pconfigcall,n_root,pvalueclass_tree,n_constants)',
            *common.step('S_pending','S_done'), *common.public('S_pending'),
            'S_pending.EVENTS = S_done.EVENTS',
            'n_pending_owners = $heap_owners($heap_graph(S_pending),HARRAY n_input)',
            *common.step('S_false','S_pending','PBOOL false'),
            '~(HARRAY n_root <- S_false.ALLOCATIONS)', '~(HARRAY n_child <- S_false.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_false),HARRAY n_input) = $(n_pending_owners - 1)',
            *define.finish('S_false',stdout),
            'S_final.USERCONSTANTS = S.USERCONSTANTS',
            '~(HARRAY n_caller_root <- S_final.ALLOCATIONS)',
            '~(HARRAY n_caller_child <- S_final.ALLOCATIONS)']
        return values
    values += ['S_wrong_bytes = S_copy[.ARRAYS[n_child].ITEMS[2] = ENTRY (KSTRING ' + text('binary') + ') (DIRECT (PSTRING ' + text('wrong') + '))]',
        '$dynamic_array_value(S_wrong_bytes,PARRAY n_root,eps,false) = ((S_wrong_bytes,PARRAY n_root,pvalueclass_tree))',
        '~$dynamic_array_known_matches(S_wrong_bytes,PARRAY n_root,(PARRAY n_input))',
        '~$user_constants_valid(S_wrong_bytes,S_wrong_bytes.USERCONSTANTS)',
        'pvalueclass_bad = $pvclass_put(pvalueclass_tree,KSTRING ' + text(first) + ',PVSCALAR)',
        '~$user_constants_valid(S_copy[.USERCONSTANTS = [puserconstant[.CLASS = pvalueclass_bad]]],[puserconstant[.CLASS = pvalueclass_bad]])',
        *common.reach('S_query','S_copy',0,target), *common.public('S_query'),
        'H_query = $heap_graph(S_query)',
        'n_query_owners = $heap_owners(H_query,HARRAY n_root)',
        *common.step('S_value','S_query','PARRAY n_root'),
        '$heap_graph(S_value).EDGES = H_query.EDGES',
        '$heap_owners($heap_graph(S_value),HARRAY n_root) = $(n_query_owners + 1)']
    values += [f'S_value.{field} = S_query.{field}' for field in ['ARRAYS','ALLOCATIONS','STRINGDATA','STORE','USERCONSTANTS']]
    values += ['S_bucket_found = $test_literal_string_bucket_seek(S_value,5000)',
        r'S_bucket_found.COMPLETION = NORMAL \/ S_bucket_found.COMPLETION = BUDGET',
        'S_bucket = $test_running(S_bucket_found)', '$test_literal_string_bucket(S_bucket)', *common.public('S_bucket'),
        '$lookup(S_bucket.ENV,$ptascii("copy")) = (n_copy_cell)',
        'S_bucket.STORE[n_copy_cell] = DEFINED (PARRAY n_copy_root)', 'n_copy_root =/= n_root',
        '$entry_lookup(S_bucket.ARRAYS[n_copy_root].ITEMS,KSTRING ' + text('nested') + ') = (DIRECT (PARRAY n_copy_child))',
        'n_copy_child =/= n_child',
        '$lookup(S_bucket.ENV,$ptascii("slot")) = (n_slot)', 'n_slot <- S_bucket.REFCELLS',
        '$entry_lookup(S_bucket.ARRAYS[n_copy_child].ITEMS,KSTRING ' + text('binary') + ') = (ALIAS n_slot)',
        '$string_bytes($entry_value(S_bucket,ALIAS n_slot)) = (' + text('local') + ')',
        '$heap_owners($heap_graph(S_bucket),HCELL n_slot) = 2',
        'S_bucket.ARRAYS[n_root] = parray_root', 'S_bucket.ARRAYS[n_child] = parray_child',
        *define.finish('S_bucket',stdout),
        'S_final.USERCONSTANTS = S_copy.USERCONSTANTS',
        'S_final.ARRAYS[n_root] = parray_root', 'S_final.ARRAYS[n_child] = parray_child',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_child) = 1',
        '~(HARRAY n_copy_root <- S_final.ALLOCATIONS)',
        '~(HARRAY n_copy_child <- S_final.ALLOCATIONS)', '~(HCELL n_slot <- S_final.ALLOCATIONS)',
        'S_final.ARRAYS[n_input] = S.ARRAYS[n_input]',
        'S_final.ARRAYS[n_input_child] = parray_child',
        'HARRAY n_input <- $pools_nodes(S_final.POOLS)',
        'HARRAY n_input_child <- $pools_nodes(S_final.POOLS)']
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
