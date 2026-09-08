#!/usr/bin/env python3
"""Checked structural occurrence identities; no compiler or runtime coverage claim."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import signal
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tests/semantics'))
import static_types as types

SPECS = [ROOT/'spec/php.watsup', ROOT/'spec/semantics/11-source-occurrences.watsup']
SCHEMA = json.loads((ROOT/'spec/schema.json').read_text())
NODES = SCHEMA['nodes']


def value_term(value):
    if value is None: return 'ABSENT'
    if isinstance(value,bool): return '(BOOLEAN '+str(value).lower()+')'
    if isinstance(value, list): return '(SEQUENCE ([' + ','.join(map(value_term,value)) + ']))'
    if 'node' in value: return node_term(value)
    kind, value = next(iter(value.items()))
    return '(' + {'bytes':'BYTES','int':'INTEGER','float':'FLOAT','bool':'BOOLEAN'}[kind] + ' ' + (str(value).lower() if kind in ['int','bool'] else json.dumps(value)) + ')'


def node_term(node):
    metadata = []
    for key, value in node.get('meta',{}).items():
        if key == 'comments':
            comments=[]
            for comment in value:
                doc, text, *positions = comment['comment']
                comments.append('(COMMENT '+str(doc).lower()+' '+json.dumps(text)+' '+' '.join(positions)+')')
            payload = '(['+','.join(comments)+'])'
        elif SCHEMA['metadata'][key] == 'text': payload=json.dumps(value['bytes'])
        elif SCHEMA['metadata'][key] == 'int': payload=value['int']
        else: payload=json.dumps(value)
        metadata.append('(M'+key+' '+payload+')')
    return '('+NODES[node['node']]['constructor']+' '+' '.join(map(value_term,node['fields']))+' (['+','.join(metadata)+']))'


def path_term(path):
    return '([' + ','.join(f'(PC{kind} {i})' for kind,i in path) + '])'


def expected(node, path):
    out = [(path,node)]
    def child(value, childpath):
        if isinstance(value,list):
            for i,item in enumerate(value): child(item,childpath+[('INDEX',i)])
        elif isinstance(value,dict) and 'node' in value:
            out.extend(expected(value,childpath))
    for i, field in enumerate(node['fields']): child(field,path+[('FIELD',i)])
    return out


def occurrence_term(occurrences):
    return '(['+','.join('(PCOCCURRENCE '+path_term(path)+' '+node_term(node)+')' for path,node in occurrences)+'])'


def minimal_values():
    domains = SCHEMA['domains']; values={}; costs={}
    # Find finite witnesses through the complete schema, without guessed field defaults.
    while len(values) != len(domains):
        old=len(values)
        for domain, alternatives in domains.items():
            for alt in alternatives:
                kind=alt[0]
                if kind == 'node':
                    fields=NODES[alt[1]]['fields']
                    if any(f['domain'] not in values for f in fields): continue
                    cost=1+sum(costs[f['domain']] for f in fields)
                    value={'node':alt[1],'fields':[copy.deepcopy(values[f['domain']]) for f in fields],'meta':{}}
                elif kind == 'list': cost,value=0,[]
                else: cost,value=0,{'string':{'bytes':'AA=='},'int':{'int':'0'},'float':{'float':'7ff8000000000000'},'bool':{'bool':False},'null':None}[kind]
                if domain not in costs or cost < costs[domain]: costs[domain],values[domain]=cost,value
        if len(values)==old and len(values)!=len(domains): raise AssertionError('no finite schema witness')
    return values


def main():
    def expired(signum,frame): raise TimeoutError('worker request exceeded 30 seconds')
    signal.signal(signal.SIGALRM,expired)
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'),'dune','build','--root',str(types.HERE),'numeric_runner.exe'],cwd=ROOT,check=True,timeout=120)
    subprocess.run([sys.executable,str(ROOT/'scripts/generate-occurrences.py'),'--check'],cwd=ROOT,check=True,timeout=10)
    runner=ROOT/'tests/semantics/_build/default/numeric_runner.exe'
    watched=SPECS+[Path(__file__),ROOT/'spec/schema.json',ROOT/'scripts/generate-occurrences.py',runner,ROOT/'_build/default/adapter/main.exe',types.PHP]
    def fingerprint(): return {'closure':types.syntax_validation.implementation_fingerprint(), 'direct':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}}
    before=fingerprint()
    values=minimal_values(); fixtures=[]; records=[]
    for tag,node in NODES.items():
        value={'node':tag,'fields':[copy.deepcopy(values[f['domain']]) for f in node['fields']],'meta':{'startLine':{'int':'19'},'endLine':{'int':'23'}}}
        path=[('INDEX',3),('FIELD',7),('INDEX',2)]
        occurrences=expected(value,path)
        fixtures.append('  -- if $pcwalk(([(PCOCCURRENCE '+path_term(path)+' '+node_term(value)+')])) = '+occurrence_term(occurrences))
        fixtures.append('  -- if $pcmetadata('+node_term(value)+') = [(MstartLine 19),(MendLine 23)]')
        records.append({'id':'constructor-'+tag,'occurrences':len(occurrences)})
    domain_cases=0
    keys={json.dumps(v,sort_keys=True):k for k,v in SCHEMA['domains'].items()}
    for domain,alternatives in SCHEMA['domains'].items():
        for alt in alternatives:
            kind=alt[0]
            if kind=='node':
                value={'node':alt[1],'fields':[copy.deepcopy(values[f['domain']]) for f in NODES[alt[1]]['fields']],'meta':{}}
                immediate=[([],value)]
            elif kind=='list':
                child=keys[json.dumps(alt[1],sort_keys=True)]
                value=[copy.deepcopy(values[child]),copy.deepcopy(values[child])]
                immediate=[([('INDEX',i)],v) for i,v in enumerate(value) if isinstance(v,dict) and 'node' in v]
            else:
                value={'string':{'bytes':'AA=='},'int':{'int':'0'},'float':{'float':'7ff8000000000000'},'bool':False,'null':None}[kind]
                immediate=[]
            fixtures.append(f'  -- if $pcfield_{domain}({value_term(value)}, eps) = '+occurrence_term(immediate))
            domain_cases+=1
    sources=[
        b'<?php',
        b'<?php $a=[1,1]; $b=[1,1];',
        b'<?php [, $x,, $y] = [1,2,3,4];',
        b'<?php function f($a=null, ...$b) { return [NAN]; } f(); f();',
        b'<?php namespace N; use A\\B as C; function f(?C $x): C|null { return $x; } namespace M; $a=1;',
        b'<?php namespace N { class C { private ?A $p = null; public function f() {} } } namespace { ; }',
        b'<?php interface I { public function f(); } function f() {}',
        b'<?php for ($i=0; $i<2; $i++) { $a=[1]; }',
        b'<?php if ($a) {;} elseif ($b) {;} else {;} try {;} catch (A|B $e) {;} finally {;}',
        b'<?php $a = function() use (&$x, $y) { return fn($a) => $a; };',
        b'<?php $a = "a\\x00\\xff"; $b=1e1000; $c=-0.0;',
        b'<?php /** node-looking data: {"node":"Scalar_Int"} */ function f() {}',
        b'#!/usr/bin/php\n<?php echo "ok"; __halt_compiler();\x00data',
        b'<?php $a = new class { public function f() {} }; match($a) { 1,2=>3, default=>4 };',
    ]
    frontend=types.Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')])
    adapter=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    try:
        for i,source in enumerate(sources):
            parsed=frontend.request({'op':'parse','source':base64.b64encode(source).decode()})
            assert parsed['accepted'],parsed
            checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
            assert checked['ast']==parsed['ast']
            ast=checked['ast']; occurrences=[]
            for j,node in enumerate(ast['program']): occurrences.extend(expected(node,[('INDEX',j)]))
            paths=[path for path,node in occurrences]
            assert len(set(map(repr,paths)))==len(paths)
            fixture=checked['fixture']
            fixtures += [f'  -- if pcunit_{i} = $pcsource(7, {fixture})',
                         f'  -- if pcunit_{i}.ID = 7',
                         f'  -- if pcunit_{i}.AST = {fixture}',
                         f'  -- if pcunit_{i}.OCCURRENCES = '+occurrence_term(occurrences),
                         f'  -- if $pcsource(8, {fixture}) = pcunit_{i}[.ID = 8]']
            records.append({'id':f'source-{i}','source_base64':base64.b64encode(source).decode(),'source_sha256':hashlib.sha256(source).hexdigest(),'ast_sha256':hashlib.sha256(json.dumps(ast,sort_keys=True).encode()).hexdigest(),'occurrences':len(occurrences)})
        # Identical checked trees at different paths must not collapse, even with identical metadata.
        seed=frontend.request({'op':'parse','source':base64.b64encode(b'<?php $a=[1];').decode()})['ast']
        duplicate=copy.deepcopy(seed); duplicate['program']*=2
        checked=adapter.request({'op':'check','ast':duplicate,'fixture':True})
        occurrences=[]
        for i,node in enumerate(checked['ast']['program']): occurrences.extend(expected(node,[('INDEX',i)]))
        fixtures.append('  -- if $pcsource(9, '+checked['fixture']+').OCCURRENCES = '+occurrence_term(occurrences))
        # Removing all optional metadata changes retained syntax, never structural paths.
        def clear_metadata(value):
            if isinstance(value,list):
                for v in value: clear_metadata(v)
            elif isinstance(value,dict) and 'node' in value:
                value['meta']={}
                for field in value['fields']: clear_metadata(field)
        without=copy.deepcopy(duplicate); clear_metadata(without['program'])
        stripped=adapter.request({'op':'check','ast':without,'fixture':True})
        fixtures.append('  -- if $pctestpaths($pcsource(9, '+checked['fixture']+').OCCURRENCES) = $pctestpaths($pcsource(9, '+stripped['fixture']+').OCCURRENCES)')
        fixtures.append('  -- if $pcsource(9, '+checked['fixture']+').AST =/= $pcsource(9, '+stripped['fixture']+').AST')
    finally:
        frontend.close(); adapter.close()
    with tempfile.TemporaryDirectory(prefix='php-occurrences-') as tmp:
        fixture=Path(tmp)/'cases.watsup'
        fixture.write_text('dec $pctestpaths(pcoccurrence*) : pcpath*\ndef $pctestpaths((PCOCCURRENCE pcpath pcnode)*) = pcpath*\ndec $main() : bool\ndef $main() = true\n'+'\n'.join(fixtures)+'\n')
        result=subprocess.run([str(runner),*map(str,SPECS),str(fixture)],capture_output=True,text=True,timeout=120)
        if result.returncode or result.stdout.strip()!='true':
            (ROOT/'.tools/source-occurrences-failure.watsup').write_text(fixture.read_text())
            raise AssertionError((result.returncode,result.stdout,result.stderr))
    assert before==fingerprint(),'changed test inputs'
    report={'scope':'checked structural traversal; no PHP compiler or execution agreement claimed','constructors':len(NODES),'source_cases':len(sources),'domain_alternatives':domain_cases,'metamorphic_assertions':3,'assertions':len(fixtures),'fingerprint':before,'cases':records}
    (ROOT/'coverage/semantics/source-occurrences.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'{len(NODES)} constructors, {len(sources)} checked sources, {domain_cases} domain alternatives, {len(fixtures)} assertions passed')

if __name__=='__main__': main()
