#!/usr/bin/env python3
"""Pure return covariance against executed declaration-only oracle fixtures."""
import base64
import hashlib
import json
from pathlib import Path
import re
import signal
import subprocess
import tempfile
import static_types as types
ROOT,HERE,PHP=types.ROOT,types.HERE,types.PHP
SPECS=types.SPECS+[ROOT/'spec/semantics/19-variance.watsup']
PREFIX='''
dec $pvtestname(pvresult,ptbranch*,ptbranch*) : ptbytes
def $pvtestname(PVINCOMPATIBLE,ptbranch*,ptbranch_parent*) = $ptascii("Declaration of C::f(): ") ++ $pttypename(ptbranch*) ++ $ptascii(" must be compatible with P::f(): ") ++ $pttypename(ptbranch_parent*)
def $pvtestname(PVNEEDS (ptbytes :: ptbytes_rest*),ptbranch*,ptbranch_parent*) = $ptascii("Could not check compatibility between C::f(): ") ++ $pttypename(ptbranch*) ++ $ptascii(" and P::f(): ") ++ $pttypename(ptbranch_parent*) ++ $ptascii(", because class ") ++ ptbytes ++ $ptascii(" is not available")
'''
def cls(name,parent='',ancestors=(),final=False):
    return '{NAME ('+types.byte_expr(name)+'),PARENT ('+types.byte_expr(parent)+'),ANCESTORS (['+','.join('('+types.byte_expr(n)+')' for n in ancestors)+']),FINAL '+str(final).lower()+'}'
def context(name,parent,file):
    return '{NAMESPACE eps,IMPORTS eps,SCOPE (PTKNOWN ('+types.byte_expr(name)+') ('+(types.byte_expr(parent) if parent else 'eps')+')),POSITION PTRETURN,OWNER ('+types.byte_expr(name)+'),MEMBER ([102]),FILE ('+types.byte_expr(str(file))+'),LINE 1}'
def main():
    signal.signal(signal.SIGALRM,lambda s,f:(_ for _ in ()).throw(TimeoutError('variance request budget')))
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'),'dune','build','--root',str(HERE),'numeric_runner.exe'],cwd=ROOT,check=True,timeout=120)
    runner=HERE/'_build/default/numeric_runner.exe'
    watched=SPECS+[Path(__file__),HERE/'static_types.py',HERE/'numeric_runner.ml',HERE/'dune',HERE/'profile.json',PHP,runner,ROOT/'vendor/php-src/Zend/zend_inheritance.c',ROOT/'vendor/php-src/Zend/zend_compile.c']
    def fingerprint(): return {'closure':types.syntax_validation.implementation_fingerprint(),'direct':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}}
    before=fingerprint()
    probe=subprocess.run([str(PHP),'-n',*types.FLAGS,'-r','echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,ini_get_all(null,false),get_loaded_extensions()]);'],capture_output=True,text=True,env=types.ENV,check=True,timeout=10)
    identity=json.loads(probe.stdout)
    assert identity[:4]==['8.5.10','cli',8,False]
    assert all(identity[4][k]==v for k,v in types.PROFILE.items())
    frontend=types.Worker([str(PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')])
    adapter=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    atoms=['int','float','string','bool','true','false','null','void','never','mixed','object','array','iterable','callable','A','B','C','I','J','Closure','Traversable','self','static','Missing','I&J','(I&J)|null','A|B','int|A','?A','Missing|A','Missing&J']
    cases=[{'child':child,'parent':parent} for child in atoms for parent in atoms]
    cases += [{'child':'parent','parent':parent} for parent in atoms]
    cases += [{'child':child,'parent':parent,'final':True} for child in ['self','C','A','Missing','C&J','C|int'] for parent in ['static','static|int','callable|static']]
    cases += [{'child':child,'parent':parent,'implements':interfaces} for interfaces in [[],['J'],['I','J']] for child in ['static','self'] for parent in ['I&J','(I&J)|null']]
    cases += [{'child':child,'parent':parent,'needs':needs} for child,parent,needs in [('Z|W','X|Y',['Z','W','X','Y']),('X|Z','X|Y',['X','Z','Y']),('Z&X','Y&X',['Z','X','Y']),('Z|A','Y|A',['Z','Y']),('Missing|A','J',[]),('A','Missing&J',[]),('Missing&A','I',[]),('A','Missing|I',[])]]
    deduplicated={}
    for case in cases:
        key=(case['child'],case['parent'],case.get('final',False),tuple(case.get('implements',['I'])))
        deduplicated[key]=case
    cases=list(deduplicated.values())
    records=[]; declarations=[]
    try:
        with tempfile.TemporaryDirectory(prefix='variance-',dir=ROOT/'.tools') as tmp:
            file=Path(tmp)/'input.php'
            for case in cases:
                interfaces=case.get('implements',['I']);final=case.get('final',False)
                source='<?php interface I{} interface J{} class A implements I{} class B extends A implements J{} class P'+(' implements '+','.join(interfaces) if interfaces else '')+' {function f():'+case['parent']+'{}} '+('final ' if final else '')+'class C extends P {function f():'+case['child']+'{}}'
                parsed=frontend.request({'op':'parse','source':base64.b64encode(source.encode()).decode()})
                assert parsed['accepted'],(case,parsed)
                checked=adapter.request({'op':'check','ast':parsed['ast']})
                parent,child=checked['ast']['program'][-2:]
                childnode=types.find_type(child,'return');parentnode=types.find_type(parent,'return')
                file.write_text(source)
                run=subprocess.run([str(PHP),'-n',*types.FLAGS,str(file)],capture_output=True,text=True,env=types.ENV,timeout=10)
                assert run.returncode in [0,255] and not run.stdout,(case,run)
                childscope=cls('C','P',['P',*interfaces],final);parentscope=cls('P','',interfaces)
                entries=[('C',childscope),('I',cls('I')),('J',cls('J')),('A',cls('A','',['I'])),('B',cls('B','A',['A','I','J'])),('P',parentscope),('Closure',cls('Closure',final=True)),('Traversable',cls('Traversable'))]
                registry='['+','.join('('+types.byte_expr(name)+','+value+')' for name,value in entries)+']'
                assertion=f'  -- if $ptype_normalize({types.type_expr(childnode)},{context("C","P",file)}) = PTOK ptbranch_child* eps\n  -- if $ptype_normalize({types.type_expr(parentnode)},{context("P","",file)}) = PTOK ptbranch_parent* eps\n  -- if pvresult = $pvcovariant(ptbranch_child*,{childscope},ptbranch_parent*,{parentscope},{registry})\n'
                if run.returncode==0:
                    assert not run.stderr,(case,run.stderr)
                    assertion+='  -- if pvresult = PVCOMPATIBLE\n';status='compatible'
                else:
                    match=re.fullmatch(r'Fatal error: (.*) in '+re.escape(str(file))+r' on line 1\nStack trace:\n#0 \{main\}\n',run.stderr)
                    assert match,(case,run.stderr)
                    message=match[1]
                    if message.startswith('Declaration of '):
                        assertion+='  -- if pvresult = PVINCOMPATIBLE\n';status='incompatible'
                    else:
                        match=re.fullmatch(r'(Could not check compatibility between .*), because class (.*?) is not available',message)
                        assert match,(case,message)
                        _,missing=match.groups()
                        assertion+='  -- if pvresult = PVNEEDS ptbytes_missing*\n  -- if '+types.byte_expr(missing)+' <- ptbytes_missing*\n';status='unresolved'
                    assertion+='  -- if $pvtestname(pvresult,ptbranch_child*,ptbranch_parent*) = '+types.byte_expr(message)+'\n'
                if case.get('needs'): assertion+='  -- if pvresult = PVNEEDS (['+','.join('('+types.byte_expr(n)+')' for n in case['needs'])+'])\n'
                declarations.append(f'dec $case{len(declarations)}() : bool\ndef $case{len(declarations)}() = true\n'+assertion)
                records.append({**case,'source':source,'ast':{'checked_child_return':childnode,'checked_parent_return':parentnode},'status':status,'exit':run.returncode,'stdout':run.stdout,'stderr':run.stderr,'context':{'child':childscope,'parent':parentscope,'registry':registry,'namespace':'','imports':[],'file':str(file),'compiler_line':1}})
            def branches(*names):
                def atom(name):
                    if name in ['self','parent']: return 'PT'+name.upper()
                    if name=='static': return 'PTSTATIC'
                    if name in ['object','callable','mixed','int','array','iterable']: return '(PTBUILTIN '+json.dumps(name)+')'
                    return '(PTCLASS ('+types.byte_expr(name)+'))'
                return '['+','.join('(PTBRANCH (['+','.join(atom(a) for a in name.split('&'))+']))' for name in names)+']'
            c=cls('C','P',['P','I'],True);p=cls('P','',['I'])
            registry='[('+types.byte_expr('I')+','+cls('I')+'),('+types.byte_expr('P')+','+p+'),('+types.byte_expr('C')+','+c+'),('+types.byte_expr('Closure')+','+cls('Closure',final=True)+'),('+types.byte_expr('AliasC')+','+c+'),('+types.byte_expr('AliasClosure')+','+cls('Closure',final=True)+'),('+types.byte_expr('AliasP')+','+p+')]'
            symbolic=[
                ('closure-alias',branches('AliasClosure'),c,branches('callable'),p,registry,'PVCOMPATIBLE'),
                ('final-self-alias',branches('AliasC'),c,branches('static'),p,registry,'PVCOMPATIBLE'),
                ('nonfinal-self-alias',branches('AliasC'),c.replace('FINAL true','FINAL false'),branches('static'),p,registry.replace(c,c.replace('FINAL true','FINAL false')),'PVINCOMPATIBLE'),
                ('parent-alias',branches('self'),c,branches('AliasP'),p,registry,'PVCOMPATIBLE'),
                ('deferred-self',branches('self'),c,branches('C'),p,registry,'PVCOMPATIBLE'),
                ('deferred-parent',branches('parent'),c,branches('P'),p,registry,'PVCOMPATIBLE'),
                ('missing-deferred-parent',branches('parent'),cls('T'),branches('object'),p,registry,'PVNEEDS (['+types.byte_expr('parent')+'])'),
                ('equal-undeclared-caseless',branches('Unknown'),c,branches('unknown'),p,registry,'PVCOMPATIBLE'),
                ('case-distinct-obligations',branches('Z','W'),c,branches('z','Y'),p,registry,'PVNEEDS (['+','.join('('+types.byte_expr(n)+')' for n in ['Z','W','z','Y'])+'])'),
            ]
            reason='PVUNSUPPORTED "covariance requires two present normalized types and named class contexts"'
            symbolic += [('missing-child-type','eps',c,branches('int'),p,registry,reason),('missing-parent-type',branches('int'),c,'eps',p,registry,reason),('missing-child-scope',branches('int'),cls(''),branches('int'),p,registry,reason),('missing-parent-scope',branches('int'),c,branches('int'),cls(''),registry,reason)]
            for name,child,c,parent,p,registry,expected in symbolic:
                invocation=f'$pvcovariant({child},{c},{parent},{p},{registry})'
                declarations.append(f'dec $case{len(declarations)}() : bool\ndef $case{len(declarations)}() = true\n  -- if {invocation} = {expected}\n')
                records.append({'name':name,'classification':'symbolic-normalized-input','invocation':invocation,'expected':expected})
            for start in range(0,len(declarations),30):
                batch=declarations[start:start+30];fixture=Path(tmp)/'cases.watsup'
                fixture.write_text(PREFIX+'\n'.join(batch)+'\ndec $main() : bool\ndef $main() = true\n'+'\n'.join('  -- if '+re.search(r'\$case\d+',x).group()+'()' for x in batch)+'\n')
                r=subprocess.run([str(runner),*map(str,SPECS),str(fixture)],capture_output=True,text=True,timeout=120)
                if r.returncode or r.stdout.strip()!='true':
                    (ROOT/'.tools/variance-failure.watsup').write_text(fixture.read_text());(ROOT/'.tools/variance-records.json').write_text(json.dumps(records,indent=2))
                    raise AssertionError((start,r.stdout,r.stderr))
    finally:
        frontend.close();adapter.close()
    for record in records:
        if 'source' in record:
            record['source_sha256']=hashlib.sha256(record['source'].encode()).hexdigest()
            record['ast_sha256']=hashlib.sha256(json.dumps(record['ast'],sort_keys=True).encode()).hexdigest()
            record['classification']='source-oracle-helper'
        payload={k:record[k] for k in ['classification','source_sha256','ast_sha256','name','invocation','expected'] if k in record}
        record['id']=record['classification']+':'+hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
    ids=[record['id'] for record in records]
    assert len(set(ids))==len(ids),'duplicate variance case identities'
    assert before==fingerprint(),'inputs changed during covariance validation'
    report={'target':'PHP 8.5.10 CLI NTS signed64','result':'pass','source_oracle_helper':sum(r['classification']=='source-oracle-helper' for r in records),'symbolic_descriptors':sum(r['classification']=='symbolic-normalized-input' and not r['expected'].startswith('PVUNSUPPORTED') for r in records),'explicit_unsupported':sum(r.get('expected','').startswith('PVUNSUPPORTED') for r in records),'comparison':'declaration-only executed oracle; exact covariance status plus test-rendered fatal message/file/line; explicit visible graph prerequisite, no source activation semantics','identity':identity,'profile':types.PROFILE,'environment':{'LC_ALL':'C','TZ':'UTC'},'budgets':{'request_seconds':30,'shutdown_seconds':5,'oracle_seconds':10,'batch_seconds':120},'fingerprints':before,'cases':records}
    (ROOT/'coverage/semantics/variance.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['cases','identity','profile','fingerprints']}))
if __name__=='__main__':main()
