#!/usr/bin/env python3
"""Reached define snapshots, certified leaves and allocation-free array queries."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

import define_stdclass_protocol as define
import define_stdclass_array_sources as sources

packet, common, std = define.packet, define.common, define.std
ROOT, text, term, PREFIX = define.ROOT, define.text, define.term, define.PREFIX


def fresh(initial,target,donor,keys,alias=False,budget=False):
    first,nested,leaf=keys
    valueclass='PVSTDCLASS n_object porigin_site'
    childclass=f'PVARRAY false ([({leaf},{valueclass})])'
    treeclass=f'PVARRAY false ([({first},{valueclass}),({nested},pvalueclass_child)])'
    item='ALIAS n_cell' if alias else 'DIRECT (POBJECT n_object)'
    values=[*initial,*define.reach('S','S_initial',0,target),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        '$config_invoke_valid(S,pconfigcall)','$dynamic_array_call_valid(S,pconfigcall)',
        '$dynamic_define_values(pconfigcall) = ((preqbytes,PARRAY n_input))',
        'preqbytes = '+text(target),'$source_constant_lookup(S,preqbytes) = eps',
        '$user_constant_at(S.USERCONSTANTS,'+text(donor)+') = (puserconstant_donor)',
        'puserconstant_donor.VALUE = POBJECT n_object',
        'puserconstant_donor.CLASS = '+valueclass,
        '$global_std_record(S.CONSTANTSTDOBJECTS,n_object) = (pconstantstdobject)',
        '$global_std_completed(S,pconstantstdobject)',
        '$dynamic_define_value_class(S,POBJECT n_object) = ('+valueclass+')',
        'parray_input = S.ARRAYS[n_input]',
        f'parray_input.ITEMS = [ENTRY ({first}) ({item}),ENTRY ({nested}) (DIRECT (PARRAY n_child_input))]',
        f'S.ARRAYS[n_child_input].ITEMS = [ENTRY ({leaf}) ({item})]',
        'n_before = |S.ARRAYS|',
        'n_leaf_before = $heap_owners($heap_graph(S),HOBJECT n_object)']
    if alias:
        values += ['S.STORE[n_cell] = DEFINED (POBJECT n_object)',
            'HCELL n_cell <- S.ALLOCATIONS',
            '$dynamic_array_value(S,PARRAY n_input,eps,false) = eps']
    if budget:
        values += ['S_pause = $drive_steps(S,0)','S_pause = S[.COMPLETION = BUDGET]',
            'S_resume = $test_running(S_pause)','S_resume = S']
    values += [*common.step('S_row','S_resume' if budget else 'S','PBOOL true'),
        'S_row.TODO = ptask_tail*',
        '$user_constant_at(S_row.USERCONSTANTS,preqbytes) = (puserconstant)',
        'S_row.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant]',
        'puserconstant.ORIGIN = pconfigcall.SITE','puserconstant.NAME = preqbytes',
        'puserconstant.VALUE = PARRAY n_root',
        'n_root =/= n_input','$(n_root >= n_before)',
        'parray_root = S_row.ARRAYS[n_root]',
        f'parray_root.ITEMS = [ENTRY ({first}) (DIRECT (POBJECT n_object)),ENTRY ({nested}) (DIRECT (PARRAY n_child))]',
        'n_child =/= n_child_input','n_child =/= n_root','$(n_child >= n_before)',
        '|S_row.ARRAYS| = $(n_before + 2)',
        'parray_child = S_row.ARRAYS[n_child]',
        f'parray_child = $array_insert($array_empty(),{leaf},DIRECT (POBJECT n_object))',
        f'parray_root = $array_insert($array_insert($array_empty(),{first},DIRECT (POBJECT n_object)),{nested},DIRECT (PARRAY n_child))',
        'pvalueclass_child = '+childclass,
        'puserconstant.CLASS = '+treeclass,
        'puserconstant.READS = eps','puserconstant.RECEIVES = eps',
        '$dynamic_array_value(S_row,PARRAY n_root,eps,false) = ((S_row,PARRAY n_root,puserconstant.CLASS))',
        '$dynamic_global_constant_array_tree(S_row,PARRAY n_root,puserconstant.CLASS)',
        '$user_constant_roots(S_row.USERCONSTANTS) = $user_constant_roots(S.USERCONSTANTS) ++ [HARRAY n_root]',
        'H_row = $heap_graph(S_row)',
        '$heap_owners(H_row,HARRAY n_root) = 1',
        '$heap_owners(H_row,HARRAY n_child) = 1',
        '$heap_edge_owners(HOBJECT n_object,H_row.EDGES,[HARRAY n_root,HARRAY n_child]) = 2']
    values += [f'S_row.{field} = S.{field}' for field in
        ['OBJECTS','OBJECTPROPS','OBJECTTABLES','CONSTANTSTDOBJECTS','EVENTS']]
    if alias:
        values += ['$heap_owners(H_row,HOBJECT n_object) = $(n_leaf_before + 2)',
            'S_row.ARRAYS[n_input] = parray_input',
            'S_row.ARRAYS[n_child_input] = S.ARRAYS[n_child_input]',
            'S_row.STORE = S.STORE']
    # Pure projections test validation only; no projected state is driven.
    projections=[
        ('missing','[.CONSTANTSTDOBJECTS = eps]'),
        ('incomplete','[.CONSTANTSTDOBJECTS = $global_std_record_put(S_row.CONSTANTSTDOBJECTS,pconstantstdobject[.COMPLETE = false])]'),
        ('dead','[.ALLOCATIONS = $destruction_node_delete(S_row.ALLOCATIONS,HOBJECT n_object)]'),
        ('history','[.ARRAYS = $array_replace(S_row.ARRAYS,n_root,parray_root[.NEXT = $(parray_root.NEXT + 1)])]')]
    for suffix,change in projections:
        values += ['S_'+suffix+' = S_row'+change,
            '$dynamic_array_value(S_'+suffix+',PARRAY n_root,eps,false) = eps',
            '~$user_constants_valid(S_'+suffix+',S_'+suffix+'.USERCONSTANTS)']
    wrong='PVARRAY false ([('+first+',PVOBJECT),('+nested+',pvalueclass_child)])'
    values += ['puserconstant_bad = puserconstant[.CLASS = '+wrong+']',
        '~$user_constants_valid(S_row[.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant_bad]],S.USERCONSTANTS ++ [puserconstant_bad])']
    return values


def receive(start,target):
    values=[*common.reach('S_query',start,0,target),*common.public('S_query'),
        '$dynamic_global_constant_value(S_query,'+text(target)+') = (PARRAY n_root)',
        'H_query = $heap_graph(S_query)',
        'n_query_owners = $heap_owners(H_query,HARRAY n_root)',
        'n_query_leafowners = $heap_owners(H_query,HOBJECT n_object)',
        *common.step('S_value','S_query','PARRAY n_root'),
        'H_value = $heap_graph(S_value)','H_value.EDGES = H_query.EDGES',
        '$heap_owners(H_value,HARRAY n_root) = $(n_query_owners + 1)',
        '$heap_owners(H_value,HOBJECT n_object) = n_query_leafowners']
    values += [f'S_value.{field} = S_query.{field}' for field in
        ['ARRAYS','ALLOCATIONS','OBJECTS','OBJECTPROPS','OBJECTTABLES','STORE','USERCONSTANTS','CONSTANTSTDOBJECTS']]
    return values


def checks(initial,name,stdout):
    selected=name.startswith('selected-')
    target,donor=('V66_EVAL_TREE','V66_EVAL_LEAF') if selected else ('V66_SNAPSHOT','V66_LEAF')
    keys=('KINT 4','KINT 7','KSTRING '+text('leaf')) if selected else ('KINT 2','KINT 5','KSTRING '+text('leaf'))
    values=fresh(initial,target,donor,keys,not selected,not selected)
    if selected:
        values += ['pconfigcall.SITE = PORIGIN 1 pcpath_define',
            'pconfigcall.SELECTION = (n_selection)',
            '~$dynamic_array_source(S_row[.SELECTEDCALLS = eps][.SELECTSEQ = 0],puserconstant.ORIGIN)']
    else:
        values += ['parray_input.NEXT = 91','parray_input.SERIAL = 3','parray_root.NEXT = 6']
    values += [*receive('S_row',target),*define.finish('S_value',stdout),
        'S_final.USERCONSTANTS = S_row.USERCONSTANTS',
        'S_final.ARRAYS[n_root] = parray_root','S_final.ARRAYS[n_child] = parray_child',
        '~(HARRAY n_input <- S_final.ALLOCATIONS)',
        '~(HARRAY n_child_input <- S_final.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 1',
        '$heap_owners($heap_graph(S_final),HARRAY n_child) = 1',
        '$heap_owners($heap_graph(S_final),HOBJECT n_object) = 3',
        *define.property_value('S_final','n_object',19 if selected else 7,'final')]
    if not selected:
        values += ['~(HCELL n_cell <- S_final.ALLOCATIONS)']
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
            initial=['S_initial = $php_run('+main+',0,'+json.dumps(packet.b64(str(path).encode()))+')','S_initial.COMPLETION = BUDGET']
            if any(n['node']=='Expr_Eval' for n in std.nodes(parsed['ast'])):
                code,=[base64.b64decode(n['fields'][0]['bytes']) for n in std.nodes(parsed['ast']) if n['node']=='Scalar_String' and base64.b64decode(n['fields'][0]['bytes']).startswith(b'$ok = $install(')]
                unit=frontend.request({'op':'parse-eval','id':'1','mode':'eval','profile':'cli-raw-85','source':packet.b64(code)});assert unit['accepted']
                checked=adapter.request({'op':'check','ast':unit['ast'],'fixture':True})['fixture']
                response='SOURCE_ACCEPT 1 '+term(code)+' '+checked
                initial=['S_wait = $php_run('+main+',5000,'+json.dumps(packet.b64(str(path).encode()))+')','S_wait.COMPLETION = SOURCE_PENDING',*common.public('S_wait'),'$eval_response_valid(S_wait,'+response+')','S_initial = $test_running($eval_resume(S_wait,'+response+'))']
            values=checks(initial,name,base64.b64decode(row['stdout']))
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
