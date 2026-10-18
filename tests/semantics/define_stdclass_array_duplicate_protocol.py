#!/usr/bin/env python3
"""Reached copied candidates, original call arguments and duplicate disposal."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

import define_stdclass_protocol as define
import define_stdclass_array_duplicate_sources as sources

packet, common, std = define.packet, define.common, define.std
ROOT, text, term = define.ROOT, define.text, define.term
PREFIX = define.PREFIX + r'''
dec $test_array_duplicate_front(pstate, nat, preqbytes) : bool
def $test_array_duplicate_front(S,0,preqbytes) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants
  -- if $dynamic_define_values(pconfigcall) = ((preqbytes,PARRAY n_input))
def $test_array_duplicate_front(S,1,preqbytes) = true
  -- if S.TODO = (DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants) :: ptask_tail*
  -- if $dynamic_define_values(pconfigcall) = ((preqbytes,PARRAY n_input))
def $test_array_duplicate_front(S,n_phase,preqbytes) = false -- otherwise
dec $test_array_duplicate_seek(pstate, nat, preqbytes, nat) : pstate
def $test_array_duplicate_seek(S,n_phase,preqbytes,0) = S
def $test_array_duplicate_seek(S,n_phase,preqbytes,n) = S
  -- if $(n > 0)
  -- if $test_array_duplicate_front(S,n_phase,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_array_duplicate_seek(S,n_phase,preqbytes,n) = $test_array_duplicate_seek($drive_steps($test_running(S),1),n_phase,preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_array_duplicate_front(S,n_phase,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state,start,phase,name):
    return [f'{state}_found = $test_array_duplicate_seek({start},{phase},{text(name)},5000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_array_duplicate_front({state},{phase},{text(name)})',*common.public(state)]


def capture(initial,target,donor,keys,alias=False,budget=False):
    first,nested,leaf=keys
    item='ALIAS n_cell' if alias else 'DIRECT (POBJECT n_object)'
    marker='DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants'
    values=[*initial,*define.reach('S','S_initial',1,target),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'n_constants = |S.USERCONSTANTS|',
        '$dynamic_array_duplicate_call_valid(S,pconfigcall,n_constants)',
        '~$dynamic_constant_duplicate_valid(S,pconfigcall,n_constants)',
        '$dynamic_define_values(pconfigcall) = ((preqbytes,PARRAY n_input))',
        'preqbytes = '+text(target),
        '$user_constant_at(S.USERCONSTANTS,preqbytes) = (puserconstant_old)',
        '$user_constant_at(S.USERCONSTANTS,'+text(donor)+') = (puserconstant_donor)',
        'puserconstant_donor.VALUE = POBJECT n_object',
        'puserconstant_donor.CLASS = PVSTDCLASS n_object porigin_site',
        '$global_std_record(S.CONSTANTSTDOBJECTS,n_object) = (pconstantstdobject)',
        '$global_std_completed(S,pconstantstdobject)',
        f'S.ARRAYS[n_input].ITEMS = [ENTRY ({first}) ({item}),ENTRY ({nested}) (DIRECT (PARRAY n_input_child))]',
        f'S.ARRAYS[n_input_child].ITEMS = [ENTRY ({leaf}) ({item})]',
        'n_before = |S.ARRAYS|','H_before = $heap_graph(S)',
        'n_input_owners = $heap_owners(H_before,HARRAY n_input)',
        'n_leaf_owners = $heap_owners(H_before,HOBJECT n_object)']
    if alias:values += ['S.STORE[n_cell] = DEFINED (POBJECT n_object)','HCELL n_cell <- S.ALLOCATIONS']
    if budget:
        values += ['S_pause = $drive_steps(S,0)','S_pause = S[.COMPLETION = BUDGET]',
            'S_resume = $test_running(S_pause)','S_resume = S']
    values += [*common.step('S_dispatch','S_resume' if budget else 'S'),*common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = '+marker,
        '$error_call_valid(S_dispatch,perrorcall)',
        'perrorcall.LEVEL = 2','perrorcall.SITE = pconfigcall.SITE',
        'perrorcall.LINE = pconfigcall.LINE','perrorcall.MESSAGE = $global_constant_duplicate_message(preqbytes)',
        'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE pconfigcall.LINE',
        'S_dispatch.RESULT = KNOWN PNULL','S_dispatch.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_dispatch.USERCONSTANTS = S.USERCONSTANTS','S_dispatch.EVENTS = S.EVENTS',
        'n_candidate = $(n_before + 1)','n_candidate_child = n_before',
        'n_candidate =/= n_input','n_candidate_child =/= n_input_child',
        f'parray_child = $array_insert($array_empty(),{leaf},DIRECT (POBJECT n_object))',
        f'parray_candidate = $array_insert($array_insert($array_empty(),{first},DIRECT (POBJECT n_object)),{nested},DIRECT (PARRAY n_candidate_child))',
        'S_dispatch.ARRAYS = S.ARRAYS ++ [parray_child,parray_candidate]',
        f'pvalueclass_child = PVARRAY false ([({leaf},PVSTDCLASS n_object porigin_site)])',
        f'pvalueclass = PVARRAY false ([({first},PVSTDCLASS n_object porigin_site),({nested},pvalueclass_child)])',
        '$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_candidate,pvalueclass,n_constants)',
        '$task_nodes('+marker+') = [HARRAY n_candidate] ++ $config_nodes(pconfigcall)',
        '$selected_task_nonce('+marker+') = pconfigcall.SELECTION',
        'H_dispatch = $heap_graph(S_dispatch)',
        '$heap_owners(H_dispatch,HARRAY n_candidate) = 1',
        '$heap_owners(H_dispatch,HARRAY n_candidate_child) = 1',
        '$heap_owners(H_dispatch,HARRAY n_input) = n_input_owners',
        '$heap_owners(H_dispatch,HOBJECT n_object) = $(n_leaf_owners + 2)',
        '$heap_edge_owners(HOBJECT n_object,H_dispatch.EDGES,[HARRAY n_candidate,HARRAY n_candidate_child]) = 2']
    values += [f'S_dispatch.{field} = S.{field}' for field in ['OBJECTS','OBJECTPROPS','OBJECTTABLES','CONSTANTSTDOBJECTS','STORE','REFCELLS']]
    # These projections test only validators; no altered state is driven.
    values += ['~$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_input,pvalueclass,n_constants)',
        '~$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_candidate,pvalueclass,0)',
        '~$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_candidate,pvalueclass,$(n_constants + 1))',
        '~$dynamic_array_duplicate_valid(S_dispatch,pconfigcall,n_candidate,PVARRAY true eps,n_constants)']
    for suffix,change in [
        ('missing','[.CONSTANTSTDOBJECTS = eps]'),
        ('incomplete','[.CONSTANTSTDOBJECTS = $global_std_record_put(S_dispatch.CONSTANTSTDOBJECTS,pconstantstdobject[.COMPLETE = false])]'),
        ('dead','[.ALLOCATIONS = $destruction_node_delete(S_dispatch.ALLOCATIONS,HOBJECT n_object)]'),
        ('history','[.ARRAYS[n_candidate].NEXT = $(parray_candidate.NEXT + 1)]')]:
        values += ['S_'+suffix+' = S_dispatch'+change,
            '~$dynamic_array_duplicate_valid(S_'+suffix+',pconfigcall,n_candidate,pvalueclass,n_constants)']
    return values


def checks(initial,name,stdout):
    selected=name.startswith('selected-')
    target,donor,old=('V67_EVAL_TREE','V67_EVAL_NEXT','V67_EVAL_OLD') if selected else ('V67_TREE','V67_LEFT','V67_OLD')
    keys=('KINT 4','KINT 7','KSTRING '+text('leaf')) if selected else ('KINT 2','KINT 5','KSTRING '+text('leaf'))
    values=capture(initial,target,donor,keys,not selected,not selected)
    values += ['$user_constant_at(S.USERCONSTANTS,'+text(old)+') = (puserconstant_old_donor)',
        'puserconstant_old_donor.VALUE = POBJECT n_old',
        'puserconstant_old.VALUE = PARRAY n_old_root',
        *reach('S_done','S_dispatch',0,target),
        'S_done.TODO = (ERROR_HANDLER_RESULT perrorcall_done) :: ptask_tail*',
        'perrorcall_done.RESUME = DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants',
        'S_done.RESULT = KNOWN (PBOOL '+('false' if selected else 'true')+')',
        'S_done.USERCONSTANTS = S.USERCONSTANTS',
        'S_done.ARRAYS[n_candidate] = parray_candidate','S_done.ARRAYS[n_candidate_child] = parray_child',
        '$dynamic_array_duplicate_valid(S_done,pconfigcall,n_candidate,pvalueclass,n_constants)',
        *define.property_value('S_done','n_old',19 if selected else 17,'changed_old'),
        *define.property_value('S_done','n_object',29 if selected else 13,'candidate'),
        *common.step('S_pending','S_done'),*common.public('S_pending'),
        'S_pending.TODO = (DYNAMIC_ARRAY_CONSTANT_DUPLICATE pconfigcall n_candidate pvalueclass n_constants) :: ptask_tail*',
        'S_pending.EVENTS = S_done.EVENTS'+(' ++ [DIAGNOSTIC_SOURCE 1 "Warning" perrorcall_done.MESSAGE pconfigcall.LINE]' if selected else ''),
        'H_pending = $heap_graph(S_pending)',
        '$heap_owners(H_pending,HARRAY n_candidate) = 1',
        'n_pending_leaf = $heap_owners(H_pending,HOBJECT n_object)',
        *common.step('S_false','S_pending','PBOOL false'),
        'S_false.TODO = ptask_tail*','S_false.USERCONSTANTS = S.USERCONSTANTS',
        '~(HARRAY n_candidate <- S_false.ALLOCATIONS)',
        '~(HARRAY n_candidate_child <- S_false.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_false),HOBJECT n_object) = $(n_pending_leaf - '+('4' if selected else '2')+')']
    if selected:
        values += ['pconfigcall.SITE = PORIGIN 1 pcpath_call','pconfigcall.SELECTION = (n_selection)',
            'S_done.ERRORFATALTRACE = eps','$display_state_mode(S_done) = 2',
            '~$dynamic_array_duplicate_valid(S_dispatch[.SELECTEDCALLS = eps][.SELECTSEQ = 0],pconfigcall,n_candidate,pvalueclass,n_constants)',
            '~(HARRAY n_input <- S_false.ALLOCATIONS)','~(HARRAY n_input_child <- S_false.ALLOCATIONS)']
    else:
        values += ['S.ARRAYS[n_input].NEXT = 91','parray_candidate.NEXT = 6',
            '$user_constant_at(S.USERCONSTANTS,$ptascii("V67_RIGHT")) = (puserconstant_right)',
            'puserconstant_right.VALUE = POBJECT n_right',
            'S_pending.STORE[n_cell] = DEFINED (POBJECT n_right)',
            '$heap_owners($heap_graph(S_false),HARRAY n_input) = 1',
            '$heap_owners($heap_graph(S_false),HOBJECT n_right) = 2']
    values += [*define.finish('S_false',stdout),'S_final.USERCONSTANTS = S.USERCONSTANTS',
        '$heap_owners($heap_graph(S_final),HOBJECT n_object) = 1',
        '$heap_owners($heap_graph(S_final),HOBJECT n_old) = 3',
        '$heap_owners($heap_graph(S_final),HARRAY n_old_root) = 1',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)','~(HARRAY n_input_child <- S_final.ALLOCATIONS)',
        *define.property_value('S_final','n_old',19 if selected else 17,'final_old'),
        *define.property_value('S_final','n_object',29 if selected else 13,'final_candidate')]
    if not selected:values += ['$heap_owners($heap_graph(S_final),HOBJECT n_right) = 1','~(HCELL n_cell <- S_final.ALLOCATIONS)']
    return values


def prepare(out,originals):
    native=json.loads((originals/'native-report.json').read_text());assert native['passed'] and native['inputs_stable']
    frontend=packet.Worker([str(packet.types.PHP),'-n',*packet.types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],out/'frontend')
    adapter=None
    try:
        adapter=packet.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],out/'adapter')
        for name in sources.family.CASES:
            path=originals/name/'main.php';row,=[r for r in native['records'] if r['id']==name]
            assert hashlib.sha256(path.read_bytes()).hexdigest()==row['source_sha256'] and row['process']['exit']==0
            parsed=frontend.request({'op':'parse','source':packet.b64(path.read_bytes())});assert parsed['accepted']
            main=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})['fixture']
            initial=['S_initial = $php_run('+main+',0,'+json.dumps(packet.b64(str(path).encode()))+')','S_initial.COMPLETION = BUDGET']
            if any(n['node']=='Expr_Eval' for n in std.nodes(parsed['ast'])):
                code,=[base64.b64decode(n['fields'][0]['bytes']) for n in std.nodes(parsed['ast']) if n['node']=='Scalar_String' and base64.b64decode(n['fields'][0]['bytes']).startswith(b'$api = "define";')]
                unit=frontend.request({'op':'parse-eval','id':'1','mode':'eval','profile':'cli-raw-85','source':packet.b64(code)});assert unit['accepted']
                checked=adapter.request({'op':'check','ast':unit['ast'],'fixture':True})['fixture'];response='SOURCE_ACCEPT 1 '+term(code)+' '+checked
                initial=['S_wait = $php_run('+main+',5000,'+json.dumps(packet.b64(str(path).encode()))+')','S_wait.COMPLETION = SOURCE_PENDING',*common.public('S_wait'),'$eval_response_valid(S_wait,'+response+')','S_initial = $test_running($eval_resume(S_wait,'+response+'))']
            values=checks(initial,name,base64.b64decode(row['stdout']));target=out/name;target.mkdir()
            (target/'assertions.json').write_text(json.dumps(values,indent=2)+'\n')
            (target/'protocol.watsup').write_text(PREFIX+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+v+'\n' for v in values))
    finally:
        try:
            if adapter:adapter.close()
        finally:frontend.close()


packet.sources,packet.prepare=sources,prepare
family_fingerprint=sources.family.fingerprint
def fingerprint():
    return dict(family_fingerprint(),**{str(Path(__file__).relative_to(ROOT)):sources.family.sha(__file__)})
sources.family.fingerprint=fingerprint

if __name__=='__main__':
    parser=argparse.ArgumentParser(add_help=False);parser.add_argument('--case',choices=sources.family.CASES)
    args,remaining=parser.parse_known_args()
    if args.case:sources.family.CASES={args.case:sources.family.CASES[args.case]}
    sys.argv=[sys.argv[0],*remaining]
    raise SystemExit(0 if packet.main() else 1)
