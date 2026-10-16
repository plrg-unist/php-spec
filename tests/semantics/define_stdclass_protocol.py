#!/usr/bin/env python3
"""Reached stdClass define publication, duplicate captures and live row owners."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

import global_constant_stdclass_array_protocol as packet
import global_constant_stdclass_protocol as std
import define_stdclass_sources as sources

common, ROOT, text, term = packet.common, packet.ROOT, packet.text, packet.term
PREFIX = common.PREFIX + std.PREFIX + r'''
dec $test_std_define_front(pstate, nat, preqbytes) : bool
def $test_std_define_front(S,0,preqbytes) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE
  -- if $dynamic_define_values(pconfigcall) = ((preqbytes,pvalue))
def $test_std_define_front(S,1,preqbytes) = true
  -- if $test_std_define_front(S,0,preqbytes)
  -- if $user_constant_at(S.USERCONSTANTS,$user_constant_key(preqbytes)) =/= eps
def $test_std_define_front(S,2,preqbytes) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall n_constants
  -- if $dynamic_define_values(pconfigcall) = ((preqbytes,pvalue))
def $test_std_define_front(S,3,preqbytes) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall n_constants
  -- if $dynamic_define_values(pconfigcall) = ((preqbytes,pvalue))
def $test_std_define_front(S,4,preqbytes) = true
  -- if S.TODO = (DYNAMIC_CONSTANT_DUPLICATE pconfigcall n_constants) :: ptask_tail*
  -- if $dynamic_define_values(pconfigcall) = ((preqbytes,pvalue))
def $test_std_define_front(S,n_phase,preqbytes) = false -- otherwise
dec $test_std_define_seek(pstate, nat, preqbytes, nat) : pstate
def $test_std_define_seek(S,n_phase,preqbytes,0) = S
def $test_std_define_seek(S,n_phase,preqbytes,n) = S
  -- if $(n > 0)
  -- if $test_std_define_front(S,n_phase,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_std_define_seek(S,n_phase,preqbytes,n) = $test_std_define_seek($drive_steps($test_running(S),1),n_phase,preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_std_define_front(S,n_phase,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state,start,phase,name,public=True):
    return [f'{state}_found = $test_std_define_seek({start},{phase},{text(name)},5000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_std_define_front({state},{phase},{text(name)})',
        *(common.public(state) if public else [])]


def property_value(state,obj,value,suffix):
    return [f'$property_slot_at($object_table_slots_at({state},{obj}),$ptascii("value")) = (ppropertyslot_{suffix})',
        f'ppropertyslot_{suffix}.STATE = PROP_VALUE pitem_{suffix}',
        f'$entry_value({state},pitem_{suffix}) = PINT {value}']


def fresh(initial,target,donor,budget=False):
    values=[*initial,*reach('S','S_initial',0,target),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        '$config_invoke_valid(S,pconfigcall)', '$dynamic_define_source(S,pconfigcall.SITE)',
        '$dynamic_define_values(pconfigcall) = ((preqbytes,POBJECT n_object))',
        'preqbytes = '+text(target),
        '$user_constant_at(S.USERCONSTANTS,'+text(donor)+') = (puserconstant_donor)',
        'puserconstant_donor.VALUE = POBJECT n_object',
        'puserconstant_donor.CLASS = PVSTDCLASS n_object porigin_site',
        '$global_std_record(S.CONSTANTSTDOBJECTS,n_object) = (pconstantstdobject)',
        '$global_std_completed(S,pconstantstdobject)', 'pconstantstdobject.SITE = porigin_site',
        'S.OBJECTS[n_object] = STDINSTANCE',
        '$dynamic_define_value_class(S,POBJECT n_object) = (PVSTDCLASS n_object porigin_site)',
        '$dynamic_define_known(S,pconfigcall.SITE,0) = eps',
        '$dynamic_define_known(S,pconfigcall.SITE,1) = eps',
        'n_owners = $heap_owners($heap_graph(S),HOBJECT n_object)',
        '$(n_owners > 1)',
        # Pure helper projections are never driven.
        '$dynamic_define_value_class(S[.CONSTANTSTDOBJECTS = eps],POBJECT n_object) = eps',
        '$dynamic_define_value_class(S[.CONSTANTSTDOBJECTS = $global_std_record_put(S.CONSTANTSTDOBJECTS,pconstantstdobject[.COMPLETE = false])],POBJECT n_object) = eps',
        '$dynamic_define_value_class(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_object)],POBJECT n_object) = eps',
        'n_absent = |S.OBJECTS|', '$dynamic_define_value_class(S,POBJECT n_absent) = eps',
        'pconfigcall.SENT = (NAMED_SENT (KNOWN pvalue_name)) :: pnamedslot_tail*',
        '$string_bytes(pvalue_name) = (preqbytes)',
        'pconfigcall_true = pconfigcall[.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN (POBJECT n_object)),NAMED_SENT (KNOWN (PBOOL true))]]',
        'S_fenced = $dynamic_define_finish(S,pconfigcall_true)',
        'S_fenced.COMPLETION = UNSUPPORTED "dynamic constant call domain"']
    start='S'
    if budget:
        values += ['S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
            'S_resume = $test_running(S_pause)', 'S_resume = S']
        start='S_resume'
    values += [*common.step('S_row',start,'PBOOL true'),
        'S_row.TODO = ptask_tail*', 'S_row.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant]',
        'puserconstant.NAME = preqbytes', 'puserconstant.ORIGIN = pconfigcall.SITE',
        'puserconstant.VALUE = POBJECT n_object',
        'puserconstant.CLASS = PVSTDCLASS n_object porigin_site',
        'puserconstant.READS = eps', 'puserconstant.RECEIVES = eps',
        '$user_constant_roots(S_row.USERCONSTANTS) = $user_constant_roots(S.USERCONSTANTS) ++ [HOBJECT n_object]',
        '$heap_owners($heap_graph(S_row),HOBJECT n_object) = n_owners']
    values += [f'S_row.{f} = S.{f}' for f in ['ALLOCATIONS','OBJECTS','ARRAYS','OBJECTPROPS','OBJECTTABLES','CONSTANTSTDOBJECTS','STORE','EVENTS']]
    for change in ['[.ORIGIN = PORIGIN 0 eps]','[.CLASS = PVOBJECT]',
            '[.CLASS = PVSTDCLASS n_object (PORIGIN 0 eps)]','[.VALUE = POBJECT n_absent]']:
        values += ['~$user_constants_valid(S_row[.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant'+change+']],S.USERCONSTANTS ++ [puserconstant'+change+'])']
    return values


def finish(start,stdout):
    return [f'S_final = $drive_steps({start},5000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.CONSTCONTEXT = eps', 'S_final.EVALCONTEXTS = eps',
        '$test_outputs(S_final.EVENTS) = '+term(stdout),*common.public('S_final')]


def checks(initial,name,stdout,response):
    selected=name.startswith('selected-')
    target,donor=('V65_DUPLICATE','V65_OLD') if selected else ('V65_PUBLISHED','V65_DONOR')
    values=fresh(initial,target,donor,not selected)
    if not selected:
        values += [*common.reach('S_query','S_row',0,target),*common.public('S_query'),
            '$dynamic_global_constant_value(S_query,'+text(target)+') = (POBJECT n_object)',
            'n_query_owners = $heap_owners($heap_graph(S_query),HOBJECT n_object)',
            *common.step('S_value','S_query','POBJECT n_object'),
            '$heap_owners($heap_graph(S_value),HOBJECT n_object) = $(n_query_owners + 1)',
            'S_value.ALLOCATIONS = S_query.ALLOCATIONS', 'S_value.USERCONSTANTS = S_query.USERCONSTANTS',
            *finish('S_value',stdout),
            'S_final.USERCONSTANTS = S_row.USERCONSTANTS',
            '$heap_owners($heap_graph(S_final),HOBJECT n_object) = 2',
            *property_value('S_final','n_object',7,'final')]
        return values
    values += ['pconfigcall.SELECTION = (n_selection)',
        '~$dynamic_define_source(S_row[.SELECTEDCALLS = eps][.SELECTSEQ = 0],puserconstant.ORIGIN)',
        'S_wait = $drive_steps(S_row,5000)', 'S_wait.COMPLETION = SOURCE_PENDING',*common.public('S_wait'),
        '$eval_response_valid(S_wait,'+response+')',
        'S_eval = $test_running($eval_resume(S_wait,'+response+'))',
        *reach('S_dup','S_eval',1,target),
        'S_dup.TODO = (CONFIG_INVOKE pconfigcall_dup) :: ptask_dup*',
        'pconfigcall_dup.SITE = PORIGIN 1 pcpath_dup',
        'pconfigcall_dup.SELECTION = (n_selection_dup)', 'n_selection_dup =/= n_selection',
        '$dynamic_define_values(pconfigcall_dup) = ((preqbytes,POBJECT n_candidate))',
        'n_candidate =/= n_object',
        '$global_std_record(S_dup.CONSTANTSTDOBJECTS,n_candidate) = (pconstantstdobject_candidate)',
        '$global_std_completed(S_dup,pconstantstdobject_candidate)',
        'S_dup.USERCONSTANTS = S_row.USERCONSTANTS', 'n_constants = |S_dup.USERCONSTANTS|',
        '$dynamic_constant_duplicate_valid(S_dup,pconfigcall_dup,n_constants)',
        '$config_nodes(pconfigcall_dup) = [HOBJECT n_candidate]',
        *property_value('S_dup','n_object',11,'old'),*property_value('S_dup','n_candidate',29,'candidate'),
        *common.step('S_dispatch','S_dup'),*common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_dup*',
        'perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup n_constants',
        '$error_call_valid(S_dispatch,perrorcall)', 'perrorcall.LEVEL = 2',
        'perrorcall.MESSAGE = $global_constant_duplicate_message(preqbytes)',
        'S_dispatch.USERCONSTANTS = S_dup.USERCONSTANTS', 'S_dispatch.EVENTS = S_dup.EVENTS',
        *reach('S_true','S_dispatch',2,target),
        'S_true.RESULT = KNOWN (PBOOL true)',
        'S_true.USERCONSTANTS = S_dup.USERCONSTANTS ++ [puserconstant_side]',
        'puserconstant_side.NAME = $ptascii("V65_HANDLER_SIDE")',
        'puserconstant_side.VALUE = PINT 19',
        '$dynamic_constant_duplicate_valid(S_true,pconfigcall_dup,n_constants)',
        *property_value('S_true','n_object',13,'changed_old'),*property_value('S_true','n_candidate',31,'changed_candidate'),
        *common.step('S_pending','S_true'),*common.public('S_pending'),
        'S_pending.TODO = (DYNAMIC_CONSTANT_DUPLICATE pconfigcall_dup n_constants) :: ptask_dup*',
        'S_pending.EVENTS = S_true.EVENTS',
        'n_candidate_owners = $heap_owners($heap_graph(S_pending),HOBJECT n_candidate)',
        '$(n_candidate_owners > 1)',
        *common.step('S_false','S_pending','PBOOL false'),
        'S_false.TODO = ptask_dup*', 'S_false.USERCONSTANTS = S_true.USERCONSTANTS',
        '$heap_owners($heap_graph(S_false),HOBJECT n_candidate) = $(n_candidate_owners - 1)',
        *finish('S_false',stdout),
        'S_final.USERCONSTANTS = S_true.USERCONSTANTS',
        '$heap_owners($heap_graph(S_final),HOBJECT n_object) = 2',
        '$heap_owners($heap_graph(S_final),HOBJECT n_candidate) = 1',
        *property_value('S_final','n_object',13,'final_old'),*property_value('S_final','n_candidate',31,'final_candidate')]
    return values


def prepare(out,originals):
    native=json.loads((originals/'native-report.json').read_text());assert native['passed'] and native['inputs_stable']
    frontend=packet.Worker([str(packet.types.PHP),'-n',*packet.types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],out/'frontend')
    adapter=None
    try:
        adapter=packet.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],out/'adapter')
        for name in sources.family.CASES:
            path=originals/name/'main.php';row,=[r for r in native['records'] if r['id']==name]
            assert hashlib.sha256(path.read_bytes()).hexdigest()==row['source_sha256']
            assert row['process']['exit']==0 and not base64.b64decode(row['stderr'])
            parsed=frontend.request({'op':'parse','source':packet.b64(path.read_bytes())});assert parsed['accepted']
            main=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})['fixture']
            response=None
            if name.startswith('selected-'):
                code,=[base64.b64decode(n['fields'][0]['bytes']) for n in std.nodes(parsed['ast']) if n['node']=='Scalar_String' and base64.b64decode(n['fields'][0]['bytes']).startswith(b'$install = ')]
                unit=frontend.request({'op':'parse-eval','id':'1','mode':'eval','profile':'cli-raw-85','source':packet.b64(code)});assert unit['accepted']
                checked=adapter.request({'op':'check','ast':unit['ast'],'fixture':True})['fixture']
                response='SOURCE_ACCEPT 1 '+term(code)+' '+checked
            initial=['S_initial = $php_run('+main+',0,'+json.dumps(packet.b64(str(path).encode()))+')']
            values=checks(initial,name,base64.b64decode(row['stdout']),response)
            target=out/name;target.mkdir()
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
    parser=argparse.ArgumentParser(add_help=False);parser.add_argument('--case',choices=sources.family.CASES,required=True)
    args,remaining=parser.parse_known_args();sources.family.CASES={args.case:sources.family.CASES[args.case]}
    sys.argv=[sys.argv[0],*remaining]
    raise SystemExit(0 if packet.main() else 1)
