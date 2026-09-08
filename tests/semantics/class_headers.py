#!/usr/bin/env python3
"""Checked local declaration headers versus pinned lint, without class activation."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import re
import signal
import subprocess
import tempfile

import static_types as types
ROOT, HERE, PHP = types.ROOT, types.HERE, types.PHP
SPECS = types.SPECS + [ROOT/'spec/semantics/18-class-headers.watsup']

PREFIX = '''
dec $pchfixture(program, bool, ptcontext) : pchresult
def $pchfixture(PROGRAM ([statement]), bool, ptcontext) = $pchcompile(statement,bool,ptcontext)
dec $pchaccepted(pchresult) : bool
def $pchaccepted(PCHOK pchheader pchdiagnostic*) = true
def $pchaccepted(PCHERROR pchdiagnostic*) = false
dec $pchevents(pchresult) : (text,ptbytes,ptbytes,nat)*
def $pchevents(PCHOK pchheader pchdiagnostic*) = ($pchevent(pchdiagnostic))*
def $pchevents(PCHERROR pchdiagnostic*) = ($pchevent(pchdiagnostic))*
dec $pchevent(pchdiagnostic) : (text,ptbytes,ptbytes,nat)
def $pchevent(PCHDIAGNOSTIC text_level text_code ptbytes* ptcontext) = (text_level,$pchmessage(PCHDIAGNOSTIC text_level text_code ptbytes* ptcontext),ptcontext.FILE,ptcontext.LINE)
dec $pchdescriptor(pchresult) : (text,ptbytes,bool,bool,bool,ptbytes,ptbytes*)
def $pchdescriptor(PCHOK pchheader pchdiagnostic*) = (pchheader.KIND,pchheader.NAME,pchheader.ABSTRACT,pchheader.FINAL,pchheader.READONLY,$pchparentdisplay(pchheader.PARENT),pchheader.INTERFACES)
dec $pchparentdisplay(ptbytes?) : ptbytes
def $pchparentdisplay(eps) = eps
def $pchparentdisplay(ptbytes) = ptbytes
dec $pchbody(program) : phpType23
def $pchbody(PROGRAM ([(NStmtClass phpType14 phpType24 phpType3 phpType46 phpType44 phpType23 metadata)])) = phpType23
dec $pchkeptbody(pchresult) : phpType23
def $pchkeptbody(PCHOK pchheader pchdiagnostic*) = pchheader.BODY
'''
lines=PREFIX.splitlines()
PREFIX='\n'.join([x for x in lines if x.startswith('dec ')]+[x for x in lines if not x.startswith('dec ')])+'\n'


def target(ast):
    found=[]
    def walk(value):
        if isinstance(value,dict):
            if value.get('node') in ['Stmt_Class','Stmt_Interface','Stmt_Trait','Stmt_Enum']: found.append(value)
            for child in value.values(): walk(child)
        elif isinstance(value,list):
            for child in value: walk(child)
    walk(ast['program'])
    return found[-1]


def main():
    def expired(signum,frame): raise TimeoutError('class header worker exceeded 30 seconds')
    signal.signal(signal.SIGALRM,expired)
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'),'dune','build','--root',str(HERE),'numeric_runner.exe'],cwd=ROOT,check=True,timeout=120)
    runner=HERE/'_build/default/numeric_runner.exe'
    watched=SPECS+[Path(__file__),HERE/'static_types.py',HERE/'numeric_runner.ml',HERE/'dune',HERE/'profile.json',PHP,runner,ROOT/'vendor/php-src/Zend/zend_compile.c',ROOT/'vendor/php-src/Zend/zend_language_parser.y']
    def fingerprint(): return {'closure':types.syntax_validation.implementation_fingerprint(),'direct':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}}
    before=fingerprint()
    probe=subprocess.run([str(PHP),'-n',*types.FLAGS,'-r','echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,ini_get_all(null,false),get_loaded_extensions()]);'],capture_output=True,text=True,env=types.ENV,check=True,timeout=10)
    identity=json.loads(probe.stdout)
    assert identity[:4]==['8.5.10','cli',8,False]
    assert all(identity[4][k]==v for k,v in types.PROFILE.items())
    frontend=types.Worker([str(PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')])
    adapter=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    cases=[]
    for kind in ['class','interface','trait']:
        for name in ['C','c','_','int','INT','float','string','bool','null','false','true','mixed','object','iterable','void','never','integer','self','parent']:
            cases.append({'declaration':kind+' '+name+' {}','namespace':''})
            cases.append({'declaration':kind+' '+name+' {}','namespace':'Ns'})
    references=['A',r'\A',r'namespace\A','int',r'\int',r'namespace\int','_',r'\_',r'namespace\_',r'Alias\Sub',r'alias\Sub','self',r'\self',r'namespace\self','parent',r'\parent',r'namespace\parent',r'\static',r'namespace\static']
    for position in ['class C extends ','class C implements ','interface C extends ']:
        for name in references:
            for namespace in ['', 'Ns']:
                cases.append({'declaration':position+name+' {}','namespace':namespace,'imports':[('Alias',r'Foo\Bar')]})
    for name in ['C','_','c']:
        for namespace in ['', 'Ns']:
            for imported in [r'Foo\Bar', (namespace+'\\' if namespace else '')+name]:
                # Qualify the same-name global import to avoid an unrelated use warning.
                if imported == name: continue
                cases.append({'declaration':'class '+name+' extends A implements I,J {}','namespace':namespace,'imports':[(name,imported)]})
    for flags in ['', 'abstract ', 'final ', 'readonly ', 'abstract readonly ', 'final readonly ']:
        cases.append({'declaration':flags+'class C extends P implements I,J {}','descriptor':('class','C','abstract' in flags,'final' in flags,'readonly' in flags,'P',['I','J'])})
    cases += [
        {'declaration':'class C {}','nested':True},
        {'declaration':'class int {}','nested':True},
        {'declaration':'class _ {}','nested':True},
        {'declaration':'interface I extends A,B {}','descriptor':('interface','I',True,False,False,None,['A','B'])},
        {'declaration':'trait T {}','descriptor':('trait','T',False,False,False,None,[])},
        {'declaration':'class C { function f() {} }','body_check':True},
        {'declaration':'class C extends Alias\\Base implements alias\\I,namespace\\J,\\K {}','namespace':'Ns','imports':[('Alias',r'Foo\Bar')],'descriptor':('class',r'Ns\C',False,False,False,r'Foo\Bar\Base',[r'Foo\Bar\I',r'Ns\J','K'])},
        {'declaration':'final\nclass _\nextends A {}','namespace':'Ns','line':2},
        {'declaration':'class\nC\nextends\nnamespace\\self {}','line':1},
        {'declaration':'#[A] class C {}','unsupported':'class attributes require attribute compilation'},
        {'declaration':'enum E {}','unsupported':'declaration kind is not a named class, interface or trait'},
    ]
    records=[]; declarations=[]; descriptor_checks=0
    try:
        with tempfile.TemporaryDirectory(prefix='class-headers-',dir=ROOT/'.tools') as tmp:
            file=Path(tmp)/'input.php'
            for case in cases:
                ns=case.get('namespace',''); imports=case.get('imports',[])
                source='<?php '+('namespace '+ns+'; ' if ns else '')+''.join('use '+name+' as '+alias+'; ' for alias,name in imports)
                source+=('class Outer { function f() { ' if case.get('nested') else '')+case['declaration']+(' } }' if case.get('nested') else '')
                parsed=frontend.request({'op':'parse','source':base64.b64encode(source.encode()).decode()})
                native=frontend.request({'op':'oracle','source':base64.b64encode(source.encode()).decode()})
                assert native['accepted'],(source,native)
                file.write_text(source)
                oracle=subprocess.run([str(PHP),'-n',*types.FLAGS,'-l',str(file)],capture_output=True,text=True,env=types.ENV,timeout=10)
                assert oracle.returncode in [0,255],(source,oracle.returncode,oracle.stderr)
                record={**case,'source':source,'sha256':hashlib.sha256(source.encode()).hexdigest(),'exit':oracle.returncode,'stdout':oracle.stdout,'stderr':oracle.stderr,'context':{'namespace':ns,'imports':imports,'active_class':case.get('nested',False),'file':str(file),'compiler_line':case.get('line',1)}}
                restriction = not parsed['accepted']
                if restriction:
                    match=re.fullmatch(r'(class\s+C\s+extends|class\s+C\s+implements|interface\s+C\s+extends|class|interface)\s+((?:namespace\\|\\)?(?:self|parent|static))\s+\{\}',case['declaration'])
                    assert match,(source,parsed)
                    position,reference=match.groups()
                    spelling=reference.split('\\')[-1]
                    declaration_name=position in ['class','interface']
                    role='interface name' if 'implements' in position or position.startswith('interface') else 'class name'
                    if declaration_name: role='class name'
                    reference_line=source[:source.index(reference)].count('\n')+1
                    frontend_message="Cannot use '"+spelling+"' as "+role+" as it is reserved on line "+str(reference_line)
                    assert base64.b64decode(parsed['message']).decode()==frontend_message,(source,parsed,frontend_message)
                    message=("'"+reference+"' is an invalid class name") if reference.startswith('\\') else ('Cannot use "'+spelling+'" as '+role+', as it is reserved')
                    if declaration_name: message='Cannot use "'+spelling+'" as '+('a class name' if position=='class' else 'an interface name')+' as it is reserved'
                    assert oracle.returncode==255 and oracle.stderr=='Fatal error: '+message+' in '+str(file)+' on line '+str(case.get('line',1))+'\nStack trace:\n#0 {main}\n',(source,oracle.stderr)
                    record.update(classification='frontend-compile-restriction',frontend=parsed,native=native)
                    records.append(record)
                    donor=frontend.request({'op':'parse','source':base64.b64encode(source.replace(reference,'HeaderReference',1).encode()).decode()})
                    assert donor['accepted'],donor
                    declaration=copy.deepcopy(target(donor['ast']))
                    name={'node':'Name_FullyQualified' if reference.startswith('\\') else 'Name_Relative' if reference.startswith('namespace') else 'Name','fields':[{'bytes':base64.b64encode(spelling.encode()).decode()}],'meta':{}}
                    if declaration_name:
                        name['node']='Identifier'
                        declaration['fields'][2 if position=='class' else 1]=name
                    elif role=='class name': declaration['fields'][3]=name
                    elif declaration['node']=='Stmt_Interface': declaration['fields'][2][0]=name
                    else: declaration['fields'][4][0]=name
                    ast={'version':1,'program':[declaration]}
                    record={**case,'source':source,'classification':'edited-compiler-restriction','ast':ast,'stderr':oracle.stderr}
                else:
                    ast={'version':1,'program':[target(parsed['ast'])]}

                checked=adapter.request({'op':'check','ast':ast,'fixture':True})
                context='{NAMESPACE ('+types.byte_expr(ns)+'),IMPORTS (['+','.join('('+types.byte_expr(alias)+','+types.byte_expr(name)+')' for alias,name in imports)+']),SCOPE PTGLOBAL,POSITION PTRETURN,OWNER eps,MEMBER eps,FILE ('+types.byte_expr(str(file))+'),LINE '+str(case.get('line',1))+'}'
                record['context']={'namespace':ns,'imports':imports,'active_class':case.get('nested',False),'file':str(file),'compiler_line':case.get('line',1)}
                invocation=f'$pchfixture({checked["fixture"]},{str(case.get("nested",False)).lower()},{context})'
                assertion=''
                if 'unsupported' in case:
                    assertion=f'  -- if {invocation} = PCHUNSUPPORTED {json.dumps(case["unsupported"])}\n'
                    record['classification']='unsupported'
                else:
                    events=[]
                    for line in oracle.stderr.splitlines():
                        if not line or line=='Stack trace:' or re.match(r'#\d+ ',line): continue
                        match=re.fullmatch(r'(?:PHP )?(Warning|Deprecated|Fatal error): (.*) in (.*) on line (\d+)',line)
                        assert match,(source,line)
                        level,message,path,lineno=match.groups()
                        events.append(({'Warning':'warning','Deprecated':'deprecated','Fatal error':'fatal'}[level],message,path,int(lineno)))
                    expected='['+','.join('('+json.dumps(level)+','+types.byte_expr(message)+','+types.byte_expr(path)+','+str(line)+')' for level,message,path,line in events)+']'
                    assertion=f'  -- if pchresult = {invocation}\n  -- if $pchaccepted(pchresult) = {str(oracle.returncode==0).lower()}\n  -- if $pchevents(pchresult) = {expected}\n'
                    if 'descriptor' in case:
                        kind,name,abstract,final,readonly,parent,interfaces=case['descriptor']
                        descriptor='('+json.dumps(kind)+','+types.byte_expr(name)+','+str(abstract).lower()+','+str(final).lower()+','+str(readonly).lower()+','+(types.byte_expr(parent) if parent else 'eps')+',['+','.join(types.byte_expr(name) for name in interfaces)+'])'
                        assertion+=f'  -- if $pchdescriptor(pchresult) = {descriptor}\n'
                        descriptor_checks+=1
                    if case.get('body_check'): assertion+=f'  -- if $pchkeptbody(pchresult) = $pchbody({checked["fixture"]})\n'
                    record['classification']='edited-compiler-restriction' if restriction else 'compared'
                ordinal=len(declarations)
                declarations.append(f'dec $case{ordinal}() : bool\ndef $case{ordinal}() = true\n'+assertion)
                records.append(record)
            seed=frontend.request({'op':'parse','source':base64.b64encode(b'<?php class C {}').decode()})['ast']
            negative_context='{NAMESPACE eps,IMPORTS eps,SCOPE PTGLOBAL,POSITION PTRETURN,OWNER eps,MEMBER eps,FILE ([102]),LINE 1}'
            negatives=[('invalid-name','edited invalid declaration name'),('varlike-name','edited invalid declaration name'),('missing-name','anonymous declaration requires generated class identity'),('invalid-flags','edited invalid class modifiers'),('invalid-parent','edited invalid class reference'),('missing-file','missing source file or class compiler line'),('missing-line','missing source file or class compiler line'),('missing-interface-name','edited missing declaration name')]
            for name,reason in negatives:
                ast,context=copy.deepcopy(seed),negative_context
                declaration=ast['program'][0]
                if name=='invalid-name': declaration['fields'][2]['fields'][0]={'bytes':'YmFkXFxuYW1l'}
                if name=='varlike-name': declaration['fields'][2]['node']='VarLikeIdentifier'
                if name=='missing-name': declaration['fields'][2]=None
                if name=='invalid-flags': declaration['fields'][1]={'int':'1'}
                if name=='invalid-parent': declaration['fields'][3]={'node':'Name','fields':[{'bytes':'QQA='}],'meta':{}}
                if name=='missing-file': context=context.replace('FILE ([102])','FILE eps')
                if name=='missing-line': context=context.replace('LINE 1','LINE 0')
                if name=='missing-interface-name': ast['program'][0]={'node':'Stmt_Interface','fields':[[],None,[],[]],'meta':{}}
                checked=adapter.request({'op':'check','ast':ast,'fixture':True})
                ordinal=len(declarations)
                declarations.append(f'dec $case{ordinal}() : bool\ndef $case{ordinal}() = true\n  -- if $pchfixture({checked["fixture"]},false,{context}) = PCHUNSUPPORTED {json.dumps(reason)}\n')
                records.append({'classification':'edited-unsupported','name':name,'reason':reason,'ast':ast,'context':context})
            for start in range(0,len(declarations),40):
                batch=declarations[start:start+40]
                fixture=Path(tmp)/'cases.watsup'
                fixture.write_text(PREFIX+'\n'.join(batch)+'\ndec $main() : bool\ndef $main() = true\n'+'\n'.join('  -- if '+re.search(r'\$case\d+',x).group()+'()' for x in batch)+'\n')
                r=subprocess.run([str(runner),*map(str,SPECS),str(fixture)],capture_output=True,text=True,timeout=120)
                if r.returncode or r.stdout.strip()!='true':
                    (ROOT/'.tools/class-headers-failure.watsup').write_text(fixture.read_text())
                    raise AssertionError((start,r.stdout,r.stderr))
    finally:
        frontend.close();adapter.close()
    for record in records:
        if 'source' in record:
            record['source_sha256']=hashlib.sha256(record['source'].encode()).hexdigest()
        if 'ast' in record:
            record['ast_sha256']=hashlib.sha256(json.dumps(record['ast'],sort_keys=True).encode()).hexdigest()
        identity_payload={key:record[key] for key in ['source_sha256','ast_sha256','name'] if key in record}
        context=record.get('context')
        identity_payload['context']={k:v for k,v in context.items() if k!='file'} if isinstance(context,dict) else context
        record['id']=record['classification']+':'+hashlib.sha256(json.dumps(identity_payload,sort_keys=True).encode()).hexdigest()
    assert len({r['id'] for r in records})==len(records),'duplicate header case identities'
    assert before==fingerprint(),'inputs changed during validation'
    report={'target':'PHP 8.5.10 CLI NTS signed64','result':'pass','compared':sum(r['classification']=='compared' for r in records),'descriptor_checks':descriptor_checks,'explicit_unsupported':sum(r['classification'] in ['unsupported','edited-unsupported'] for r in records),'edited_compiler_restrictions':sum(r['classification']=='edited-compiler-restriction' for r in records),'frontend_compile_restrictions':sum(r['classification']=='frontend-compile-restriction' for r in records),'identity':identity,'profile':types.PROFILE,'environment':{'LC_ALL':'C','TZ':'UTC'},'budgets':{'request_seconds':30,'shutdown_seconds':5,'lint_seconds':10,'batch_seconds':120},'fingerprints':before,'cases':records}
    (ROOT/'coverage/semantics/class-headers.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['cases','identity','profile','fingerprints']}))

if __name__=='__main__': main()
