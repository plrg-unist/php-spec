#!/usr/bin/env python3
"""Reached false-flag capture and array copying after argument effects."""
import argparse
from pathlib import Path
import sys

import define_stdclass_array_protocol as array
import define_stdclass_array_duplicate_protocol as duplicate
import define_stdclass_array_false_flag_sources as sources

define = array.define
packet, common, std = define.packet, define.common, define.std
ROOT, text = define.ROOT, define.text
PREFIX = duplicate.PREFIX + r'''
dec $test_array_flag_front(pstate, preqbytes) : bool
def $test_array_flag_front(S,preqbytes) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.INDEX = 2
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN (PARRAY n_input))]
  -- if $string_bytes(pvalue_name) = (preqbytes)
def $test_array_flag_front(S,preqbytes) = false -- otherwise
dec $test_array_flag_seek(pstate, preqbytes, nat) : pstate
def $test_array_flag_seek(S,preqbytes,0) = S
def $test_array_flag_seek(S,preqbytes,n) = S
  -- if $(n > 0)
  -- if $test_array_flag_front(S,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_array_flag_seek(S,preqbytes,n) = $test_array_flag_seek($drive_steps($test_running(S),1),preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_array_flag_front(S,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def before(initial,target,prior):
    return [*initial,
        'S_before_found = $test_array_flag_seek(S_initial,'+text(target)+',5000)',
        r'S_before_found.COMPLETION = NORMAL \/ S_before_found.COMPLETION = BUDGET',
        'S_before = $test_running(S_before_found)',
        '$test_array_flag_front(S_before,'+text(target)+')',*common.public('S_before'),
        'S_before.TODO = (CONFIG_ARGS pconfigcall_before) :: ptask_before*',
        'pconfigcall_before.INDEX = 2',
        'pconfigcall_before.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN (PARRAY n_input_before))]',
        '$user_constant_at(S_before.USERCONSTANTS,'+text(prior)+') = (puserconstant_prior)',
        'puserconstant_prior.VALUE = POBJECT n_prior',
        'S_before.ARRAYS[n_input_before].ITEMS = (ENTRY pkey_first (ALIAS n_cell_before)) :: pentry_before*',
        'S_before.STORE[n_cell_before] = DEFINED (POBJECT n_prior)']


def flag_checks():
    return ['pconfigcall.SITE = pconfigcall_before.SITE',
        'pconfigcall.INDEX = 3',
        'pconfigcall.SENT = pconfigcall_before.SENT ++ [NAMED_SENT (KNOWN (PBOOL false))]',
        'n_input = n_input_before','n_cell = n_cell_before','n_object =/= n_prior',
        'S.ARRAYS = S_before.ARRAYS',
        'S.CONSTANTSTDOBJECTS = S_before.CONSTANTSTDOBJECTS',
        '~$dynamic_constant_case_flag(pconfigcall)',
        'pconfigcall_true = pconfigcall[.SENT = pconfigcall_before.SENT ++ [NAMED_SENT (KNOWN (PBOOL true))]]',
        '$dynamic_constant_case_flag(pconfigcall_true)',
        '~$dynamic_array_call_valid(S,pconfigcall_true)',
        'pconfigcall_nonbool = pconfigcall[.SENT = pconfigcall_before.SENT ++ [NAMED_SENT (KNOWN (PINT 0))]]',
        '$dynamic_define_values(pconfigcall_nonbool) = eps',
        '~$dynamic_array_call_valid(S,pconfigcall_nonbool)']


def checks(initial,name,stdout):
    selected = name.startswith('selected-')
    target,donor,prior = ('V68_EVAL_TREE','V68_EVAL_NEXT','V68_EVAL_OLD') if selected else ('V68_TREE','V68_RIGHT','V68_LEFT')
    keys = ('KINT 4','KINT 7','KSTRING '+text('leaf')) if selected else ('KINT 2','KINT 5','KSTRING '+text('leaf'))
    values = before(initial,target,prior)
    body = duplicate.capture([],target,donor,keys,True) if selected else array.fresh([],target,donor,keys,True,True)
    values += [v.replace('S_initial','S_before') for v in body]
    values += flag_checks()
    if not selected:
        values += ['parray_input.NEXT = 91','parray_root.NEXT = 6',
            *array.receive('S_row',target),*define.finish('S_value',stdout),
            'S_final.USERCONSTANTS = S_row.USERCONSTANTS',
            'S_final.ARRAYS[n_root] = parray_root','S_final.ARRAYS[n_child] = parray_child',
            '$heap_owners($heap_graph(S_final),HOBJECT n_object) = 3',
            '$heap_owners($heap_graph(S_final),HOBJECT n_prior) = 1',
            '~(HARRAY n_input <- S_final.ALLOCATIONS)',
            '~(HARRAY n_child_input <- S_final.ALLOCATIONS)',
            '~(HCELL n_cell <- S_final.ALLOCATIONS)',
            *define.property_value('S_final','n_object',11,'final_right'),
            *define.property_value('S_final','n_prior',3,'final_left')]
        return values
    values += ['pconfigcall.SITE = PORIGIN 1 pcpath_call',
        'pconfigcall.SELECTION = (n_selection)',
        '~$dynamic_array_duplicate_valid(S_dispatch,pconfigcall_true,n_candidate,pvalueclass,n_constants)',
        '~$dynamic_array_duplicate_valid(S_dispatch[.SELECTEDCALLS = eps][.SELECTSEQ = 0],pconfigcall,n_candidate,pvalueclass,n_constants)',
        'puserconstant_old.VALUE = PARRAY n_old_root',
        *duplicate.reach('S_done','S_dispatch',0,target),
        'S_done.TODO = (ERROR_HANDLER_RESULT perrorcall_done) :: ptask_tail*',
        'perrorcall_done.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants',
        'S_done.RESULT = KNOWN (PBOOL true)',
        'S_done.USERCONSTANTS = S.USERCONSTANTS',
        '$test_outputs(S_done.EVENTS) = $test_outputs(S_dispatch.EVENTS) ++ '+define.term(b'H|D|old|false|'),
        'S_done.STORE[n_cell] = DEFINED (POBJECT n_prior)',
        'S_done.ARRAYS[n_candidate] = parray_candidate',
        'S_done.ARRAYS[n_candidate_child] = parray_child',
        '$dynamic_array_duplicate_valid(S_done,pconfigcall,n_candidate,pvalueclass,n_constants)',
        *define.property_value('S_done','n_prior',19,'changed_old'),
        *define.property_value('S_done','n_object',23,'candidate'),
        *common.step('S_pending','S_done'),*common.public('S_pending'),
        'S_pending.TODO = (DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants) :: ptask_tail*',
        'S_pending.EVENTS = S_done.EVENTS',
        'H_pending = $heap_graph(S_pending)',
        '$heap_owners(H_pending,HOBJECT n_object) = 3',
        *common.step('S_false','S_pending','PBOOL false'),
        'S_false.TODO = ptask_tail*','S_false.USERCONSTANTS = S.USERCONSTANTS',
        '~(HARRAY n_candidate <- S_false.ALLOCATIONS)',
        '~(HARRAY n_candidate_child <- S_false.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_false),HOBJECT n_object) = 1',
        '$heap_owners($heap_graph(S_false),HARRAY n_input) = 1',
        *define.finish('S_false',stdout),'S_final.USERCONSTANTS = S.USERCONSTANTS',
        '$heap_owners($heap_graph(S_final),HOBJECT n_object) = 1',
        '$heap_owners($heap_graph(S_final),HOBJECT n_prior) = 3',
        '$heap_owners($heap_graph(S_final),HARRAY n_old_root) = 1',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)',
        '~(HARRAY n_input_child <- S_final.ALLOCATIONS)',
        '~(HCELL n_cell <- S_final.ALLOCATIONS)',
        *define.property_value('S_final','n_prior',19,'final_old'),
        *define.property_value('S_final','n_object',23,'final_candidate')]
    return values


# Reuse the exact-source/eval preparation and existing checked state runner.
duplicate.sources, duplicate.checks, duplicate.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, duplicate.prepare
family_fingerprint = sources.family.fingerprint

def fingerprint():
    return dict(family_fingerprint(), **{str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})
sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    parser=argparse.ArgumentParser(add_help=False);parser.add_argument('--case',choices=sources.family.CASES)
    args,remaining=parser.parse_known_args()
    if args.case:sources.family.CASES={args.case:sources.family.CASES[args.case]}
    sys.argv=[sys.argv[0],*remaining]
    raise SystemExit(0 if packet.main() else 1)
