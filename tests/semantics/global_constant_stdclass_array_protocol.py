#!/usr/bin/env python3
"""Reached stdClass array alias publication, query ownership and physical COW."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import class_constant_call_protocol as common
import global_constant_stdclass_array_sources as sources
from global_constant_stdclass_protocol import nodes
from recorded_worker import Worker
import static_types as types
from typed_static_invoke_set_protocol import process

ROOT = Path(__file__).resolve().parents[2]
b64 = lambda data: base64.b64encode(data).decode()
term = lambda data: '$base64(' + json.dumps(b64(data)) + ')'
text = lambda value: '$ptascii(' + json.dumps(value) + ')'
PREFIX = common.PREFIX + r'''
dec $test_array_bind(pstate, preqbytes) : bool
def $test_array_bind(S, preqbytes) = true
  -- if S.TODO = (CONSTANT_BIND porigin) :: ptask_tail*
  -- if $constant_declaration(S, porigin) = ((preqbytes,z))
def $test_array_bind(S, preqbytes) = false -- otherwise
dec $test_array_bind_seek(pstate, preqbytes, nat) : pstate
def $test_array_bind_seek(S, preqbytes, 0) = S
def $test_array_bind_seek(S, preqbytes, n) = S
  -- if $(n > 0)
  -- if $test_array_bind(S,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_array_bind_seek(S, preqbytes, n) = $test_array_bind_seek($drive_steps($test_running(S),1),preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_array_bind(S,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def receive(state, start, query):
    after = state + '_value'
    values = [*common.reach(state,start,0,query), *common.public(state),
        f'{state}.TODO = (CONFIG_INVOKE pconfigcall_{state}) :: ptask_{state}*',
        f'$dynamic_global_constant_valid({state},pconfigcall_{state})',
        f'$user_constant_at({state}.USERCONSTANTS,{text(query)}) = (puserconstant)',
        'puserconstant.VALUE = PARRAY n_root',
        f'{state}.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PFLOAT 9221120237041090560)),ENTRY (KINT 1) (DIRECT (PARRAY n_child))]',
        f'{state}.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object)),ENTRY (KINT 1) (DIRECT (PARRAY n_empty))]',
        '$pvclass_get(puserconstant.CLASS,KINT 1) = (pvalueclass_child)',
        '$pvclass_get(pvalueclass_child,KINT 0) = (PVSTDCLASS n_object porigin_site)',
        f'$constant_value_class_valid({state},PARRAY n_root,puserconstant.CLASS)',
        f'$dynamic_global_constant_value({state},{text(query)}) = (PARRAY n_root)',
        f'H_{state} = $heap_graph({state})',
        f'n_rootowners_{state} = $heap_owners(H_{state},HARRAY n_root)',
        f'n_objectowners_{state} = $heap_owners(H_{state},HOBJECT n_object)',
        *common.step(after,state,'PARRAY n_root'),
        f'{after}.TODO = ptask_{state}*',
        f'H_{after} = $heap_graph({after})',
        f'H_{after}.EDGES = H_{state}.EDGES',
        f'$heap_owners(H_{after},HARRAY n_root) = $(n_rootowners_{state} + 1)',
        f'$heap_owners(H_{after},HOBJECT n_object) = n_objectowners_{state}']
    values += [f'{after}.{field} = {state}.{field}' for field in
               ['ARRAYS','OBJECTS','OBJECTTABLES','OBJECTPROPS','ALLOCATIONS','STORE','USERCONSTANTS','CONSTANTSTDOBJECTS']]
    return values


def checks(initial, query, leaf, stdout, selected):
    values = [*initial,
        f'S_bind_found = $test_array_bind_seek(S_initial,{text(query)},3000)',
        'S_bind = $test_running(S_bind_found)', f'$test_array_bind(S_bind,{text(query)})',
        'S_bind.TODO = (CONSTANT_BIND porigin_decl) :: ptask_bind*',
        'S_bind.CONSTCONTEXT = (pconstantcontext)',
        '$constant_received_class(S_bind,porigin_decl) = pvalueclass_tree',
        '$constant_class_tree_valid(pvalueclass_tree)',
        '$constant_facts_valid(S_bind,porigin_decl,pconstantcontext.FACTS)',
        '$global_constant_transfer_valid(S_bind,porigin_decl,pvalueclass_tree,S_bind.USERCONSTANTS)',
        *common.public('S_bind'), *common.step('S_bound','S_bind','PNULL'),
        *receive('S_first','S_bound',query),
        f'$user_constant_at(S_first.USERCONSTANTS,{text(leaf)}) = (puserconstant_leaf)',
        'puserconstant_leaf.VALUE = POBJECT n_object',
        'puserconstant_leaf.CLASS = PVSTDCLASS n_object porigin_site',
        '$global_std_record(S_first.CONSTANTSTDOBJECTS,n_object) = (pconstantstdobject)',
        '$global_std_completed(S_first,pconstantstdobject)',
        'n_rootowners_S_first = 1', 'n_objectowners_S_first = 3',
        '~$default_cacheable(PVSTDCLASS n_object porigin_site)',
        '~$constant_callable_foldable(PVSTDCLASS n_object porigin_site)',
        '~$dynamic_global_constant_array_tree(S_first,POBJECT n_object,PVOBJECT)',
        'S_pause = $drive_steps(S_first,0)', 'S_pause = S_first[.COMPLETION = BUDGET]',
        'S_resume = $test_running(S_pause)', 'S_resume = S_first']
    if selected:
        values += ['pconfigcall_S_first.SELECTION = (n_selection)',
                   'S_first.SELECTEDCALLS[n_selection].KIND = INTRINSIC_CONSTANT',
                   'pconstantstdobject.SITE = PORIGIN 1 pcpath_site']
    else:
        values += ['pconfigcall_S_first.SELECTION = eps',
                   'pconstantstdobject.SITE = PORIGIN 0 pcpath_site']
    for label, change in [('birth','[.CONSTANTSTDOBJECTS[0].COMPLETE = false]'),
                          ('dead','[.ALLOCATIONS = $destruction_node_delete(S_first.ALLOCATIONS,HOBJECT n_object)]')]:
        values += [f'S_bad_{label} = S_first{change}',
                   f'$dynamic_global_constant_value(S_bad_{label},{text(query)}) = eps']
    values += [*receive('S_during','S_first_value',query),
        '$lookup(S_during.ENV,$ptascii("first")) = (n_first)',
        'S_during.STORE[n_first] = DEFINED (PARRAY n_copy_root)', 'n_copy_root =/= n_root',
        'S_during.ARRAYS[n_copy_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PFLOAT 9221120237041090560)),ENTRY (KINT 1) (DIRECT (PARRAY n_copy_child))]',
        'n_copy_child =/= n_child',
        'S_during.ARRAYS[n_copy_child].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object)),ENTRY (KINT 1) (DIRECT (PARRAY n_empty)),ENTRY (KINT 2) (DIRECT pvalue_tail)]',
        '$string_bytes(pvalue_tail) = ($ptascii("tail"))',
        '$heap_edge_owners(HOBJECT n_object,H_S_during.EDGES,[HARRAY n_child,HARRAY n_copy_child]) = 2',
        'n_objectowners_S_during = 5',
        *receive('S_again','S_during_value',query),
        'n_rootowners_S_again = 1', 'n_objectowners_S_again = 3',
        'S_final = $drive_steps(S_again_value,5000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.FRAMES = eps', 'S_final.CURRENT = eps',
        '$test_outputs(S_final.EVENTS) = ' + term(stdout), *common.public('S_final')]
    return values


def prepare(out, originals):
    native = json.loads((originals/'native-report.json').read_text())
    assert native['passed'] and native['inputs_stable']
    frontend = Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],out/'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],out/'adapter')
        for name in sources.family.CASES:
            path = originals/name/'main.php'; row, = [r for r in native['records'] if r['id']==name]
            assert hashlib.sha256(path.read_bytes()).hexdigest()==row['source_sha256']
            assert row['process']['exit']==0 and not base64.b64decode(row['stderr'])
            parsed = frontend.request({'op':'parse','source':b64(path.read_bytes())}); assert parsed['accepted']
            main = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})['fixture']
            initial = ['S_initial = $php_run('+main+',0,'+json.dumps(b64(str(path).encode()))+')','S_initial.COMPLETION = BUDGET']
            selected = name.startswith('eval-')
            if selected:
                code, = [base64.b64decode(n['fields'][0]['bytes']) for n in nodes(parsed['ast']) if n['node']=='Scalar_String' and base64.b64decode(n['fields'][0]['bytes']).startswith(b'const V60_EVAL_LEAF')]
                unit = frontend.request({'op':'parse-eval','id':'1','mode':'eval','profile':'cli-raw-85','source':b64(code)}); assert unit['accepted']
                checked = adapter.request({'op':'check','ast':unit['ast'],'fixture':True})['fixture']
                response = 'SOURCE_ACCEPT 1 '+term(code)+' '+checked
                initial = ['S_wait = $php_run('+main+',5000,'+json.dumps(b64(str(path).encode()))+')','S_wait.COMPLETION = SOURCE_PENDING',*common.public('S_wait'),'$eval_response_valid(S_wait,'+response+')','S_initial = $test_running($eval_resume(S_wait,'+response+'))']
            query, leaf = ('V60_EVAL_TREE','V60_EVAL_LEAF') if selected else ('V60_TREE','V60_LEAF')
            values = checks(initial,query,leaf,base64.b64decode(row['stdout']),selected)
            target=out/name;target.mkdir()
            (target/'assertions.json').write_text(json.dumps(values,indent=2)+'\n')
            (target/'protocol.watsup').write_text(PREFIX+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+v+'\n' for v in values))
    finally:
        try:
            if adapter: adapter.close()
        finally: frontend.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase',choices=['fixtures','check'],required=True)
    parser.add_argument('--sources',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();originals=args.sources.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    watched=[Path(__file__),Path(common.__file__),ROOT/'tests/semantics/global_constant_stdclass_protocol.py',ROOT/'tests/semantics/recorded_worker.py',ROOT/'tests/semantics/_build/default/numeric_runner.exe',originals/'native-report.json']
    watched += [originals/name/'main.php' for name in sources.family.CASES]
    if args.phase=='check':watched += [out/name/item for name in sources.family.CASES for item in ['protocol.watsup','assertions.json']]
    pins=lambda:dict(sources.family.fingerprint(),**{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched})
    before=pins();report={'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'module_count':len(json.loads((ROOT/'spec/semantics/modules.json').read_text())),'runtime_diff_sha256':hashlib.sha256(subprocess.check_output(['git','diff','HEAD','--','spec/semantics'],cwd=ROOT)).hexdigest(),'inputs':before,'result':'fail','agreement_credit':0,'profile':types.PROFILE,'environment':{'LC_ALL':'C','TZ':'UTC'},'records':[]}
    assert not (out/(args.phase+'-report.json')).exists()
    try:
        if args.phase=='fixtures':prepare(out,originals);report['result']='pass'
        else:
            modules=[str(ROOT/p) for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
            for name in sources.family.CASES:
                target=out/name;runner=process([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),'--sl',*modules,str(target/'protocol.watsup')],target/'check',90,ROOT)
                passed=runner.returncode==0 and runner.stdout==b'true\n' and not runner.stderr
                report['records'].append({'id':name,'pass':passed,'runner_exit':runner.returncode,'premises':len(json.loads((target/'assertions.json').read_text())) if passed else 0})
                print(json.dumps(report['records'][-1]),flush=True)
                if not passed:break
            report['result']='pass' if len(report['records'])==len(sources.family.CASES) and all(r['pass'] for r in report['records']) else 'fail'
    finally:
        report['stable_inputs']=before==pins()
        if not report['stable_inputs']:report['result']='fail'
        (out/(args.phase+'-report.json')).write_text(json.dumps(report,indent=2)+'\n')
    return report['result']=='pass'


if __name__=='__main__':
    raise SystemExit(0 if main() else 1)
