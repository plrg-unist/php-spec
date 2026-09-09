#!/usr/bin/env python3
"""User-method implementation checks and exact deferred diagnostic rendering."""
import base64
import hashlib
import json
from pathlib import Path
import re
import signal
import subprocess
import tempfile
import static_types as types
import variance
ROOT,HERE,PHP=types.ROOT,types.HERE,types.PHP
SPECS=[ROOT/'spec/php.watsup']+[ROOT/('spec/semantics/'+name+'.watsup') for name in ['00-numeric','01-integer','02-numeric-text','03-numeric-format','10-bytes','16-static-types','17-signatures','19-variance','19-method-signatures']]
PREFIX='''
dec $pmfixture(program,ptcontext) : pmmethod
def $pmfixture(PROGRAM ([(NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 (SEQUENCE ([(NStmtClassMethod phpType14_method phpType24_method (BOOLEAN bool) (NIdentifier (BYTES text) metadata_name) phpType16 phpType18 phpType47 metadata_method)])) metadata)]),ptcontext) = {OWNER ptcontext.OWNER,NAME ($base64(text)),SIGNATURE pssignature,CONTEXT ptcontext}
  -- if $pscompile(phpType16,phpType18,bool,ptcontext) = PSOK pssignature psdiagnostic*
dec $pmcompileevents(program,ptcontext) : (text,ptbytes,ptbytes,nat)*
def $pmcompileevents(PROGRAM ([(NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 (SEQUENCE ([(NStmtClassMethod phpType14_method phpType24_method (BOOLEAN bool) (NIdentifier (BYTES text) metadata_name) phpType16 phpType18 phpType47 metadata_method)])) metadata)]),ptcontext) = ($pmcompileevent(psdiagnostic))*
  -- if $pscompile(phpType16,phpType18,bool,ptcontext) = PSOK pssignature psdiagnostic*
dec $pmcompileevent(psdiagnostic) : (text,ptbytes,ptbytes,nat)
def $pmcompileevent(PSTYPEDIAGNOSTIC (PTDIAGNOSTIC text_level text_code ptbranch* ptcontext)) = (text_level,$ptmessage(PTDIAGNOSTIC text_level text_code ptbranch* ptcontext),ptcontext.FILE,ptcontext.LINE)
def $pmcompileevent(PSDIAGNOSTIC text_level text_code ptbytes* ptcontext) = (text_level,$psmessage(PSDIAGNOSTIC text_level text_code ptbytes* ptcontext),ptcontext.FILE,ptcontext.LINE)
dec $pmlocalfixture(program,ptcontext) : psresult
def $pmlocalfixture(PROGRAM ([(NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 (SEQUENCE ([(NStmtClassMethod phpType14_method phpType24_method (BOOLEAN bool) (NIdentifier (BYTES text) metadata_name) phpType16 phpType18 phpType47 metadata_method)])) metadata)]),ptcontext) = $pscompile(phpType16,phpType18,bool,ptcontext)
dec $pmtestevent(pmdiagresult) : (text,ptbytes,ptbytes,nat)
def $pmtestevent(PMDIAGNOSTIC pmdiagnostic) = (pmdiagnostic.LEVEL,pmdiagnostic.MESSAGE,pmdiagnostic.FILE,pmdiagnostic.LINE)
'''
lines=PREFIX.splitlines()
PREFIX='\n'.join([line for line in lines if line.startswith('dec ')]+[line for line in lines if not line.startswith('dec ')])+'\n'
def byte_expr(value):
    return '['+','.join(map(str,value if isinstance(value,bytes) else value.encode()))+']'
def main():
    signal.signal(signal.SIGALRM,lambda s,f:(_ for _ in ()).throw(TimeoutError('method request budget')))
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'),'dune','build','--root',str(HERE),'numeric_runner.exe'],cwd=ROOT,check=True,timeout=120)
    runner=HERE/'_build/default/numeric_runner.exe'
    watched=SPECS+[Path(__file__),HERE/'static_types.py',HERE/'variance.py',HERE/'numeric_runner.ml',HERE/'dune',HERE/'profile.json',PHP,runner,ROOT/'vendor/php-src/Zend/zend_inheritance.c',ROOT/'vendor/php-src/Zend/zend_compile.c']
    def fingerprint(): return {'closure':types.syntax_validation.implementation_fingerprint(),'direct':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}}
    before=fingerprint()
    probe=subprocess.run([str(PHP),'-n',*types.FLAGS,'-r','echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,ini_get_all(null,false),get_loaded_extensions()]);'],capture_output=True,text=True,env=types.ENV,check=True,timeout=10)
    identity=json.loads(probe.stdout)
    assert identity[:4]==['8.5.10','cli',8,False]
    assert all(identity[4][k]==v for k,v in types.PROFILE.items())
    frontend=types.Worker([str(PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')])
    adapter=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    params=['','$x','$renamed','&$x','...$x','&...$x','$x=1','int $x','mixed $x','A $x','B $x','I|J $x','I&J $x','$x,$y','$x,$y=1','$x,...$rest','int ...$x','int $x=1','float $x=1','$x=null','$x=UNKNOWN','Missing $x','Other $x','iterable $x','callable $x','array $x','Traversable $x','Closure $x']
    cases=[{'child':child,'parent':parent} for child in params for parent in params]
    cases += [{'child':child,'parent':parent,'child_ref':cr,'parent_ref':pr,'child_return':'int','parent_return':'int'} for child,parent in [('$x','$x'),('int $x','string $x'),('...$x','$x'),('$x=1','$x=2')] for cr in [False,True] for pr in [False,True]]
    cases += [{'child':'','parent':'','child_return':child,'parent_return':parent} for child in ['','int','void','never','mixed','A','B','self','static','Missing'] for parent in ['','int','void','mixed','A','self','static','Other']]
    cases += [{'child':'int $x='+default,'parent':'string $x','child_return':'','parent_return':''} for default in ['1','-1','+1','-(-1)']]
    cases += [{'child':'$x='+default,'parent':'&$x','child_return':'','parent_return':''} for default in ['null','true','false','[]','"a"','"abcdefghijklm"','"ab\\x00c"','"\\xffabcdefghijk"','1.5','-0.0','1e1000','-9223372036854775808','-(-9223372036854775808)','UNKNOWN',r'\UNKNOWN']]
    cases += [{'child':child,'parent':parent,'child_return':cr,'parent_return':pr} for child,parent,cr,pr in [('X $x,Z $y','Y $x,W $y','A','I'),('X $x,int $y','Y $x,string $y','Other','Missing'),('X &$x','Y $x','A','I'),('X $x','Y $x','Other','Missing')]]
    cases += [{'child':child,'parent':parent,'child_ref':cr,'parent_ref':pr,'child_return':'void','parent_return':'void'} for child,parent in [('$x','$x'),('$x=1,$y','$x,$y'),('int $x=null,$y','int $x,$y')] for cr in [False,True] for pr in [False,True]]
    cases += [{'child':child,'parent':parent,'namespace':'Ns','imports':[('Alias',r'Ns\A')],'child_return':'','parent_return':''} for child,parent in [('Alias $x','A $x'),('$x=UNKNOWN','&$x'),('$x=Alias','&$x'),(r'$x=Alias\CONST','&$x'),(r'$x=namespace\null','&$x'),(r'$x=\UNKNOWN','&$x'),('callable $x',r'\Closure $x'),('iterable $x',r'\Traversable $x')]]
    cases += [{'child':child,'parent':parent,'multiline':True,'child_name':'F','child_ref':cr,'parent_ref':pr} for child,parent,cr,pr in [('int $x','$x',False,False),('int $x=null,$y','int $x,$y',True,True),('$x=1,$y','$x,$y',False,True)]]
    cases += [{'child':'&$x','parent':'$x="ab\\x00c"','child_return':'','parent_return':''},{'child':'$x="cd\\x00e"','parent':'&$x="ab\\x00c"','child_return':'','parent_return':''}]
    dedup={}
    for case in cases:
        key=(case['child'],case['parent'],case.get('child_ref',False),case.get('parent_ref',False),case.get('child_return','void'),case.get('parent_return','void'),case.get('namespace',''),case.get('multiline',False))
        dedup[key]=case
    records=[];declarations=[]
    try:
        with tempfile.TemporaryDirectory(prefix='method-signatures-',dir=ROOT/'.tools') as tmp:
            file=Path(tmp)/'input.php'
            for case in dedup.values():
                cr=case.get('child_return','void');pr=case.get('parent_return','void')
                ns=case.get('namespace','');prefix=ns+'\\' if ns else '';imports=case.get('imports',[])
                parentname=case.get('parent_name','f');childname=case.get('child_name','f')
                declaration='function '+('&' if case.get('parent_ref') else '')+parentname+'('+case['parent']+')'+(':'+pr if pr else '')+'{}'
                childdeclaration='function '+('&' if case.get('child_ref') else '')+childname+'('+case['child']+')'+(':'+cr if cr else '')+'{}'
                setup='interface I{} interface J{} class A implements I{} class B extends A implements J{}'
                source='<?php '+('namespace '+ns+'; ' if ns else '')+''.join('use '+name+' as '+alias+'; ' for alias,name in imports)+setup+' class P {'+declaration+'} class C extends P {'+childdeclaration+'}'
                pline=cline=1
                if case.get('multiline'):
                    source='<?php\n'+setup+'\nclass P {'+declaration+'}\nclass C extends P {\n'+childdeclaration+'\n}'
                    pline,cline=3,5
                def context(name,parent,line,member):
                    ctx=variance.context(prefix+name,prefix+parent if parent else '',file).replace('NAMESPACE eps','NAMESPACE ('+byte_expr(ns)+')').replace('IMPORTS eps','IMPORTS (['+','.join('('+byte_expr(alias)+','+byte_expr(target)+')' for alias,target in imports)+'])' if imports else 'IMPORTS eps')
                    return ctx.replace('LINE 1','LINE '+str(line)).replace('MEMBER ([102])','MEMBER ('+byte_expr(member)+')')
                pctx=context('P','',pline,parentname);cctx=context('C','P',cline,childname)
                parsed=frontend.request({'op':'parse','source':base64.b64encode(source.encode()).decode()});assert parsed['accepted'],(case,parsed)
                checked=adapter.request({'op':'check','ast':parsed['ast']})
                pc,cc=(checked['ast']['program'][0]['fields'][1] if ns else checked['ast']['program'])[-2:]
                pfixture=adapter.request({'op':'check','ast':{'version':1,'program':[pc]},'fixture':True})['fixture']
                cfixture=adapter.request({'op':'check','ast':{'version':1,'program':[cc]},'fixture':True})['fixture']
                file.write_text(source)
                run=subprocess.run([str(PHP),'-n',*types.FLAGS,str(file)],capture_output=True,env=types.ENV,timeout=10)
                assert run.returncode in [0,255] and not run.stdout,(case,run)
                cscope=variance.cls(prefix+'C',prefix+'P',[prefix+'P']);pscope=variance.cls(prefix+'P')
                entries=[('C',cscope),('P',pscope),('I',variance.cls(prefix+'I')),('J',variance.cls(prefix+'J')),('A',variance.cls(prefix+'A','',[prefix+'I'])),('B',variance.cls(prefix+'B',prefix+'A',[prefix+'A',prefix+'I',prefix+'J']))]
                entries=[(prefix+n,v) for n,v in entries]+[('Traversable',variance.cls('Traversable')),('Closure',variance.cls('Closure',final=True))]
                registry='['+','.join('('+byte_expr(n)+','+v+')' for n,v in entries)+']'
                assertion=f'  -- if pmmethod_child = $pmfixture({cfixture},{cctx})\n  -- if pmmethod_parent = $pmfixture({pfixture},{pctx})\n  -- if pmcheck = $pmcompare(PMUSER pmmethod_child,{cscope},PMUSER pmmethod_parent,{pscope},{registry})\n'
                remainder=run.stderr;events=[]
                while remainder.startswith((b'Deprecated:',b'Warning:')):
                    event=re.match(rb'(Deprecated|Warning): (.*?) in '+re.escape(str(file).encode())+rb' on line (\d+)\n',remainder,re.DOTALL)
                    assert event,(case,remainder)
                    events.append((b'deprecated' if event[1]==b'Deprecated' else b'warning',event[2],int(event[3])))
                    remainder=remainder[event.end():]
                expected='['+','.join('('+json.dumps(level.decode())+','+byte_expr(message)+','+byte_expr(str(file))+','+str(line)+')' for level,message,line in events)+']'
                assertion+=f'  -- if $pmcompileevents({pfixture},{pctx}) ++ $pmcompileevents({cfixture},{cctx}) = {expected}\n'
                if not run.returncode:
                    assert not remainder,(case,remainder)
                    assertion+='  -- if pmcheck = PMCHECK PVYES eps\n';status='compatible'
                else:
                    match=re.fullmatch(b'Fatal error: (.*) in '+re.escape(str(file).encode())+rb' on line '+str(cline).encode()+rb'\nStack trace:\n#0 \{main\}\n',remainder,re.DOTALL)
                    assert match,(case,run.stderr)
                    message=match[1]
                    if message.startswith(b'Declaration of '):
                        assertion+='  -- if pmcheck = PMCHECK PVNO ptbytes_pending*\n';status='incompatible'
                        diagnostic=f'$pmmismatch(pmmethod_child,{cscope},pmmethod_parent,{pscope},14)'
                    else:
                        assert message.startswith(b'Could not check compatibility between '),(case,message)
                        assertion+='  -- if pmcheck = PMCHECK PVUNRESOLVED ptbytes_pending*\n';status='unresolved'
                        diagnostic=f'$pmunavailable(pmmethod_child,{cscope},pmmethod_parent,{pscope},ptbytes_pending*,14)'
                    assertion+='  -- if $pmtestevent('+diagnostic+') = ("fatal",'+byte_expr(message)+','+byte_expr(str(file))+','+str(cline)+')\n'
                pending={('X $x,Z $y','Y $x,W $y'):['Y','X','W','Z'],('X $x,int $y','Y $x,string $y'):['Y','X'],('X &$x','Y $x'):['Y','X'],('X $x','Y $x'):['Y','X','Other','Missing']}.get((case['child'],case['parent']))
                if pending is not None:
                    assertion+='  -- if ptbytes_pending* = (['+','.join('('+byte_expr(name)+')' for name in pending)+'])\n'
                declarations.append(f'dec $case{len(declarations)}() : bool\ndef $case{len(declarations)}() = true\n'+assertion)
                records.append({**case,'source':source,'ast':{'parent':pc,'child':cc},'classification':status,'pending_descriptor':pending,'exit':run.returncode,'stdout_base64':base64.b64encode(run.stdout).decode(),'stderr_base64':base64.b64encode(run.stderr).decode(),'context':{'child':cscope,'parent':pscope,'registry':registry,'file':str(file),'child_line':cline,'parent_line':pline,'namespace':ns,'imports':imports}})
            seed=f'  -- if pmmethod_child = $pmfixture({cfixture},{cctx})\n  -- if pmmethod_parent = $pmfixture({pfixture},{pctx})\n'
            call=f'$pmcompare(PMUSER pmmethod_child,{cscope},PMUSER pmmethod_parent,{pscope},{registry})'
            reason='PMUNSUPPORTED "user method requires named descriptors and source context"'
            negatives=[('missing-method-name',call.replace('PMUSER pmmethod_child','PMUSER (pmmethod_child[.NAME = eps])'),reason),('missing-owner',call.replace('PMUSER pmmethod_child','PMUSER (pmmethod_child[.OWNER = eps])'),reason),('missing-scope',call.replace(cscope,cscope.replace('NAME ([67])','NAME eps')),reason),('missing-compiler-line',call.replace('PMUSER pmmethod_child','PMUSER (pmmethod_child[.CONTEXT = pmmethod_child.CONTEXT[.LINE = 0]])'),reason),('missing-file',call.replace('PMUSER pmmethod_child','PMUSER (pmmethod_child[.CONTEXT = pmmethod_child.CONTEXT[.FILE = eps]])'),reason)]
            internal='PMUNSUPPORTED "internal method requires a pinned signature and tentative-return catalog"'
            negatives += [('internal-prototype',call.replace('PMUSER pmmethod_parent','PMINTERNAL ('+byte_expr('Countable')+') ('+byte_expr('count')+')'),internal),('internal-child',call.replace('PMUSER pmmethod_child','PMINTERNAL ('+byte_expr('Countable')+') ('+byte_expr('count')+')'),internal)]
            negatives += [('missing-diagnostic-file',f'$pmmismatch(pmmethod_child[.CONTEXT = pmmethod_child.CONTEXT[.FILE = eps]],{cscope},pmmethod_parent,{pscope},14)','PMDIAGUNSUPPORTED "method diagnostic requires source file and compiler line"'),('empty-availability-collection',f'$pmunavailable(pmmethod_child,{cscope},pmmethod_parent,{pscope},eps,14)','PMDIAGUNSUPPORTED "availability diagnostic requires an unresolved class collection"'),('anonymous-display-context',f'$pmdeclaration(pmmethod_child[.OWNER = ([65,0,66])],{cscope},14)','PMDISPLAYUNSUPPORTED "method declaration display requires a named nonanonymous owner"'),('uncompiled-default-display',f'$pmdefaulttext(PSNONE,{cctx},14)','PMDISPLAYUNSUPPORTED "method default display requires a compiled supported default"')]
            negatives.append(('nan-default-warning-context',f'$pmdefaulttext(PSDEFAULT (NScalarFloat (FLOAT "7ff8000000000000") eps) "float",{cctx},14)','PMDISPLAYUNSUPPORTED "NaN default rendering requires activation warning context"'))
            for name,invocation,expected in negatives:
                declarations.append(f'dec $case{len(declarations)}() : bool\ndef $case{len(declarations)}() = true\n'+seed+f'  -- if {invocation} = {expected}\n')
                records.append({'name':name,'classification':'explicit-unsupported','invocation':invocation,'expected':expected,'seed':{'parent':pc,'child':cc}})
            source='<?php\nclass P { function f(&$x) {} }\nclass C extends P {\n    function f($x=1e1000-1e1000) {}\n}\n'
            parsed=frontend.request({'op':'parse','source':base64.b64encode(source.encode()).decode()});assert parsed['accepted'],parsed
            ast={'version':1,'program':[parsed['ast']['program'][-1]]}
            checked=adapter.request({'op':'check','ast':ast,'fixture':True})
            file.write_text(source)
            run=subprocess.run([str(PHP),'-n',*types.FLAGS,str(file)],capture_output=True,env=types.ENV,timeout=10)
            expected=b'Warning: unexpected NAN value was coerced to string in '+str(file).encode()+b' on line 3\nFatal error: Declaration of C::f($x = NAN) must be compatible with P::f(&$x) in '+str(file).encode()+b' on line 4\nStack trace:\n#0 {main}\n'
            assert run.returncode==255 and run.stdout==b'' and run.stderr==expected,(run.returncode,run.stdout,run.stderr)
            ctx=variance.context('C','P',file).replace('LINE 1','LINE 4')
            declarations.append(f'dec $case{len(declarations)}() : bool\ndef $case{len(declarations)}() = true\n  -- if $pmlocalfixture({checked["fixture"]},{ctx}) = PSUNSUPPORTED "nonliteral parameter default requires constant-expression compilation"\n')
            records.append({'classification':'source-constant-expression-pending','source':source,'ast':checked['ast'],'exit':run.returncode,'stdout_base64':base64.b64encode(run.stdout).decode(),'stderr_base64':base64.b64encode(run.stderr).decode(),'context':{'file':str(file),'class_activation_line':3,'method_compiler_line':4},'pending':'constant-expression default compilation and activation warning context'})
            for start in range(0,len(declarations),25):
                batch=declarations[start:start+25];fixture=Path(tmp)/'cases.watsup'
                fixture.write_text(PREFIX+'\n'.join(batch)+'\ndec $main() : bool\ndef $main() = true\n'+'\n'.join('  -- if '+re.search(r'\$case\d+',x).group()+'()' for x in batch)+'\n')
                r=subprocess.run([str(runner),*map(str,SPECS),str(fixture)],capture_output=True,text=True,timeout=120)
                if r.returncode or r.stdout.strip()!='true':
                    (ROOT/'.tools/method-signatures-failure.watsup').write_text(fixture.read_text());(ROOT/'.tools/method-signatures-records.json').write_text(json.dumps(records,indent=2))
                    raise AssertionError((start,r.stdout,r.stderr))
    finally:frontend.close();adapter.close()
    assert before==fingerprint(),'inputs changed during method validation'
    for record in records:
        if 'source' in record:
            record['source_sha256']=hashlib.sha256(record['source'].encode()).hexdigest()
            record['ast_sha256']=hashlib.sha256(json.dumps(record['ast'],sort_keys=True).encode()).hexdigest()
        else:
            record['ast_sha256']=hashlib.sha256(json.dumps(record['seed'],sort_keys=True).encode()).hexdigest()
        payload={k:record[k] for k in ['classification','source_sha256','ast_sha256','name','expected'] if k in record}
        record['id']=record['classification']+':'+hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
    assert len({record['id'] for record in records})==len(records),'duplicate method case identities'
    report={'target':'PHP 8.5.10 CLI NTS signed64','result':'pass','source_oracle_helper':sum(r['classification'] in ['compatible','incompatible','unresolved'] for r in records),'source_phase_pending':sum(r['classification']=='source-constant-expression-pending' for r in records),'ordered_pending_descriptors':sum(r.get('pending_descriptor') is not None for r in records),'explicit_unsupported':sum(r['classification']=='explicit-unsupported' for r in records),'comparison':'ordered compilation diagnostics, method compatibility status, exact production-rendered declaration/availability fatal bytes and source contexts; no source activation or autoload execution semantics','identity':identity,'profile':types.PROFILE,'environment':{'LC_ALL':'C','TZ':'UTC'},'budgets':{'request_seconds':30,'shutdown_seconds':5,'oracle_seconds':10,'batch_seconds':120},'fingerprints':before,'cases':records}
    (ROOT/'coverage/semantics/method-signatures.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['cases','identity','profile','fingerprints']}))
if __name__=='__main__':main()
