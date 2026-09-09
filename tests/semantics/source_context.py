#!/usr/bin/env python3
"""Ordered namespace/import compiler prefix checks and explicit body-work barriers."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/semantics'))
import static_types as types
import source_occurrences as occurrences
SPECS=occurrences.SPECS+[ROOT/'spec/semantics/10-bytes.watsup',ROOT/'spec/semantics/16-static-types.watsup',ROOT/'spec/semantics/21-source-context.watsup']
PREFIX='''
dec $pltestok(plresult) : bool
def $pltestok(PLDONE plstate pldiagnostic*) = true
def $pltestok(PLERROR pldiagnostic*) = false
dec $pltestevents(plresult) : (text,ptbytes,ptbytes,nat)*
def $pltestevents(PLDONE plstate pldiagnostic*) = ($pltestevent(pldiagnostic))*
def $pltestevents(PLERROR pldiagnostic*) = ($pltestevent(pldiagnostic))*
def $pltestevents(PLWORK pcoccurrence plstate pldiagnostic*) = ($pltestevent(pldiagnostic))*
dec $pltestevent(pldiagnostic) : (text,ptbytes,ptbytes,nat)
def $pltestevent(PLDIAGNOSTIC text_level text_code ptbytes* pllocation) = (text_level,$plmessage(PLDIAGNOSTIC text_level text_code ptbytes* pllocation),pllocation.FILE,pllocation.LINE)
dec $pltestimportok(plimports) : bool
def $pltestimportok(PLIMPORTED plenv pldiagnostic*) = true
def $pltestimportok(PLIMPORTERROR pldiagnostic*) = false
dec $pltestimportevents(plimports) : (text,ptbytes,ptbytes,nat)*
def $pltestimportevents(PLIMPORTED plenv pldiagnostic*) = ($pltestevent(pldiagnostic))*
def $pltestimportevents(PLIMPORTERROR pldiagnostic*) = ($pltestevent(pldiagnostic))*
dec $pltestenv(plresult) : plenv
def $pltestenv(PLDONE plstate pldiagnostic*) = plstate.ENV
def $pltestenv(PLWORK pcoccurrence plstate pldiagnostic*) = plstate.ENV
dec $pltestwork(plresult) : pcoccurrence
def $pltestwork(PLWORK pcoccurrence plstate pldiagnostic*) = pcoccurrence
dec $pltestlocation(plstate) : pllocation
def $pltestlocation(plstate) = pllocation
  -- if plstate.TASKS = (PLVERIFY bool pllocation) :: pltask*
dec $plteststate(plresult) : plstate
def $plteststate(PLWORK pcoccurrence plstate pldiagnostic*) = plstate
def $plteststate(PLDONE plstate pldiagnostic*) = plstate
'''
PREFIX='\n'.join([x for x in PREFIX.splitlines() if x.startswith('dec ')]+[x for x in PREFIX.splitlines() if not x.startswith('dec ')])+'\n'


def events(run):
    out=[]
    for line in run.stderr.decode('utf-8','surrogateescape').split('\n'):
        if not line.strip() or line=='Stack trace:' or re.match(r'#\d+ ',line): continue
        m=re.fullmatch(r'(?:PHP )?(Warning|Deprecated|Fatal error): (.*) in .* on line (\d+)',line)
        assert m,(run.returncode,run.stdout,run.stderr,line)
        level,message,number=m.groups()
        out.append(({'Warning':'warning','Deprecated':'deprecated','Fatal error':'fatal'}[level],message,int(number)))
    return out


def expected_events(diagnostics,file):
    return '['+','.join('('+json.dumps(level)+','+types.byte_expr(message)+','+types.byte_expr(str(file))+','+str(line)+')' for level,message,line in diagnostics)+']'


def main():
    def expired(signum,frame): raise TimeoutError('context worker exceeded30seconds')
    signal.signal(signal.SIGALRM,expired)
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'),'dune','build','--root',str(types.HERE),'numeric_runner.exe'],cwd=ROOT,check=True,timeout=120)
    runner=types.HERE/'_build/default/numeric_runner.exe'
    watched=SPECS+[Path(__file__),runner,types.PHP,ROOT/'vendor/php-src/Zend/zend_compile.c',ROOT/'vendor/php-src/Zend/zend_ast.c',ROOT/'vendor/php-src/Zend/zend_language_parser.y']
    def fingerprint(): return {'closure':types.syntax_validation.implementation_fingerprint(),'direct':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}}
    before=fingerprint()
    identity=json.loads(subprocess.run([str(types.PHP),'-n',*types.FLAGS,'-r','echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,ini_get_all(null,false)]);'],capture_output=True,text=True,env=types.ENV,timeout=10,check=True).stdout)
    assert identity[:4]==['8.5.10','cli',8,False]
    assert all(identity[4][k]==v for k,v in types.PROFILE.items())
    source_cases=[]
    for namespace in ['', 'Ns', 'ns']:
        for kind in ['', 'function ', 'const ']:
            for imports in ['A;',r'\A;',r'A\B;',r'A as X;',r'A\B as X;',r'A\B as X; use KINDC\D as x;',r'A\B as X; use KINDC\D as X;',r'A\B as X; use KINDA\B as X;',r'A,B,A;',r'A\{B,C};',r'A\{B as X,C as x};',r'A\{B as X,C as X};',*[f'A as {alias};' for alias in ['Self','Parent','Static','INT','Integer','true','false','null','void','never','callable','array','_','é']]]:
                body='use '+kind+imports.replace('KIND',kind)
                source=('<?php '+('namespace '+namespace+'; ' if namespace else '')+body).encode()
                source_cases.append(source)
    source_cases += [
        b'<?php use A\\{B as X,function f as X,const C as X};',
        b'<?php use A\\{B as X,function f as X,const C as X}; use function D\\f as x;',
        b'<?php use A\\{B as X,function f as X,const C as X}; use const D\\C as x;',
        b'<?php namespace N; use A\\B as X; namespace N; use C\\D as X;',
        b'<?php namespace N { use A\\B as X; } namespace N { use C\\D as X; }',
        b'<?php namespace { use A; } namespace N { use B; } namespace { use C; }',
        b'<?php use A,\nB,\nA;',
        b'<?php namespace N; use A\\{B as X,\nC as X};',
        b'<?php /* comment */ ; namespace N { ; }',
    ]
    for kind in ['', 'function ', 'const ']:
        source_cases.extend([
            ('<?php use '+kind+'\nA,\nA;').encode(),
            ('<?php use '+kind+'\nA as X,\nB as X;').encode(),
            ('<?php use '+kind+'\nA\\{B as X,\nC as X};').encode(),
            ('<?php use '+kind+'\nA\\\n{B as X,\nC as X};').encode(),
        ])
    source_cases.append(b'<?php namespace\nN\n{ use\nA\\{B as X,\nC as X}; }')
    source_cases += [b'<?php namespace\n{ use A; }', b'<?php namespace\n/* {\n } */\n{ use A; }', b'<?php namespace\r\n{ use A; }', b'<?php namespace { use A; } namespace\n{ use A; }']
    barriers=[
        b'<?php use A; function f($a,$a) {} use B;',
        b'<?php namespace N; use A\\B as Alias; function f(): Alias {} use C;',
        b'<?php namespace N { use A\\B as Alias; class C {} use C\\D as Alias; }',
        b'<?php declare(strict_types=1); namespace N; use A\\B;',
        b'<?php namespace N; use A\\B; if(false) { function f(){} } use C;',
        b'<?php namespace N; use A\\B; $a=[&$x[]]; use C;',
    ]
    frontend=types.Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')])
    adapter=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    fixtures=[]; records=[]; rejected=[]; barrier_records=[]; descriptor_records=[]; seen_records=[]; resume_records=[]; negatives=[]
    try:
        with tempfile.TemporaryDirectory(prefix='php-source-context-') as tmp:
            file=Path(tmp)/'input.php'
            for i,source in enumerate(source_cases):
                file.write_bytes(source)
                run=subprocess.run([str(types.PHP),'-n',*types.FLAGS,'-l',str(file)],capture_output=True,env=types.ENV,timeout=10)
                assert run.returncode in [0,255],(source,run)
                parsed=frontend.request({'op':'parse','source':base64.b64encode(source).decode()})
                if not parsed['accepted']:
                    match=re.fullmatch(rb'<\?php (?:namespace (?:Ns|ns); )?use (function |const )?A as (Static|callable|array);',source)
                    assert match,(source,parsed)
                    kind,alias=match.groups();alias=alias.decode()
                    native=frontend.request({'op':'oracle','source':base64.b64encode(source).decode()})
                    message=f'Syntax error, unexpected T_{alias.upper()}, expecting T_STRING on line 1'
                    assert not native['accepted'] and run.returncode==255
                    classification='parser-rejection'
                    assert base64.b64decode(parsed['message']).decode()==message,(source,parsed)
                    rejected.append({'source_base64':base64.b64encode(source).decode(),'classification':classification,'frontend':parsed,'native_parser':native,'oracle_exit':run.returncode,'oracle_stderr':run.stderr.decode('utf-8','surrogateescape').replace(str(file),'input.php')})
                    continue
                checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
                diagnostics=events(run)
                fixtures.append(f'dec $case{i}() : bool\ndef $case{i}() = true\n  -- if plresult = $plstart({i}, {checked["fixture"]}, {types.byte_expr(str(file))})\n  -- if $pltestok(plresult) = '+str(run.returncode==0).lower()+'\n  -- if $pltestevents(plresult) = '+expected_events(diagnostics,file)+'\n')
                records.append({'id':'source-'+str(i),'source_base64':base64.b64encode(source).decode(),'source_sha256':hashlib.sha256(source).hexdigest(),'ast_sha256':hashlib.sha256(json.dumps(checked['ast'],sort_keys=True).encode()).hexdigest(),'diagnostics':diagnostics,'oracle_exit':run.returncode,'oracle_stdout':run.stdout.decode('utf-8','surrogateescape').replace(str(file),'input.php'),'oracle_stderr':run.stderr.decode('utf-8','surrogateescape').replace(str(file),'input.php')})
            for i,source in enumerate(barriers):
                parsed=frontend.request({'op':'parse','source':base64.b64encode(source).decode()})
                assert parsed['accepted'],parsed
                checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
                def target(nodes,path=[]):
                    for j,node in enumerate(nodes):
                        p=path+[('INDEX',j)]
                        if node['node']=='Stmt_Namespace':
                            found=target(node['fields'][1],p+[('FIELD',1)])
                            if found:return found
                        elif node['node'] not in ['Stmt_Use','Stmt_GroupUse','Stmt_Nop']:
                            return p,node
                path,node=target(checked['ast']['program'])
                file.write_bytes(source)
                run=subprocess.run([str(types.PHP),'-n',*types.FLAGS,'-l',str(file)],capture_output=True,env=types.ENV,timeout=10)
                barrier_records.append({'id':'barrier-'+str(i),'source_base64':base64.b64encode(source).decode(),'path':path,'oracle_exit':run.returncode,'oracle_stderr':run.stderr.decode('utf-8','surrogateescape').replace(str(file),'input.php')})
                expected='(PCOCCURRENCE '+occurrences.path_term(path)+' '+occurrences.node_term(node)+')'
                fixtures.append(f'dec $barrier{i}() : bool\ndef $barrier{i}() = true\n  -- if plresult = $plstart(1000, {checked["fixture"]}, {types.byte_expr(str(file))})\n  -- if $pltestwork(plresult) = '+expected+'\n  -- if $pladvance($plteststate(plresult)) = PLUNSUPPORTED "pending statement compilation must supply its final compiler line"\n')
            descriptor_cases=[
                (b'<?php namespace Ns; use A\\{B as Alias,function f as FUN,const X as CoNs}; function g(): Alias {}', r'Ns', [('alias',r'A\B')], [('fun',r'A\f')], [('CoNs',r'A\X')]),
                (b'<?php namespace Ns; use A\\B as X; namespace Ns; use C\\D as X;', 'Ns', [('x',r'C\D')], [], []),
                (b'<?php namespace Ns { use A\\B as X; } namespace { use C\\D as X; }', '', [], [], []),
            ]
            for i,(source,namespace,classes,functions,constants) in enumerate(descriptor_cases):
                parsed=frontend.request({'op':'parse','source':base64.b64encode(source).decode()})
                assert parsed['accepted'],parsed
                checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
                table=lambda entries:'['+','.join('('+types.byte_expr(k)+','+types.byte_expr(v)+')' for k,v in entries)+']'
                assertions=f'  -- if plresult = $plstart(3000, {checked["fixture"]}, {types.byte_expr(str(file))})\n  -- if plenv = $pltestenv(plresult)\n'
                assertions+='  -- if plenv = { NAMESPACE ('+types.byte_expr(namespace)+'), CLASSES ('+table(classes)+'), FUNCTIONS ('+table(functions)+'), CONSTANTS ('+table(constants)+'), SEEN eps, STRICT false }\n'
                if i==0:
                    function=checked['ast']['program'][0]['fields'][1][-1]
                    return_type=occurrences.value_term(function['fields'][4])
                    location='{ UNIT 3000, PATH ([(PCINDEX 0),(PCFIELD 1),(PCINDEX 1)]), FILE ('+types.byte_expr(str(file))+'), LINE 1 }'
                    assertions+='  -- if $ptype_normalize('+return_type+', $pltypecontext(plenv, PTGLOBAL, PTRETURN, eps, ([103]), '+location+')) = PTOK ([(PTBRANCH ([(PTCLASS ('+types.byte_expr(r'A\B')+'))]))]) eps\n'
                fixtures.append(f'dec $descriptor{i}() : bool\ndef $descriptor{i}() = true\n'+assertions)
                descriptor_records.append({'id':'descriptor-'+str(i),'source_base64':base64.b64encode(source).decode(),'namespace':namespace,'classes':classes,'functions':functions,'constants':constants})
            for namespace in ['', 'Ns','ns','NS']:
                for kind,word,decl in [('PLCLASS','','class X {}'),('PLFUNCTION','function ','function X() {}'),('PLCONSTANT','const ','const X=1;')]:
                    for imported in [r'Other\Y', (namespace+'\\' if namespace else '')+'X']:
                        source=('<?php '+('namespace '+namespace+'; ' if namespace else '')+decl+' use '+word+imported+' as X;').encode()
                        parsed=frontend.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                        checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
                        nodes=checked['ast']['program'][0]['fields'][1] if namespace else checked['ast']['program']
                        use=nodes[-1]
                        key=(namespace+'\\' if namespace else '')+'X'
                        if kind!='PLCONSTANT': key=key.lower()
                        env='($plempty(false))[.NAMESPACE = '+types.byte_expr(namespace)+'][.SEEN = [('+kind+','+types.byte_expr(key)+')]]'
                        path=[('INDEX',0),('FIELD',1),('INDEX',1)] if namespace else [('INDEX',1)]
                        location='{ UNIT 4000, PATH '+occurrences.path_term(path)+', FILE ('+types.byte_expr(str(file))+'), LINE 1 }'
                        file.write_bytes(source)
                        run=subprocess.run([str(types.PHP),'-n',*types.FLAGS,'-l',str(file)],capture_output=True,env=types.ENV,timeout=10)
                        assert run.returncode in [0,255],run
                        inputs='['+','.join(occurrences.node_term(n) for n in use['fields'][1])+']'
                        i=len(seen_records)
                        fixtures.append(f'dec $seen{i}() : bool\ndef $seen{i}() = true\n  -- if plimports = $pluses('+env+', '+location+', '+inputs+', '+use['fields'][0]['int']+', eps)\n  -- if $pltestimportok(plimports) = '+str(run.returncode==0).lower()+'\n  -- if $pltestimportevents(plimports) = '+expected_events(events(run),file)+'\n')
                        seen_records.append({'id':'seen-'+str(i),'scope':'import helper with explicitly supplied earlier declaration key','source_base64':base64.b64encode(source).decode(),'seen':[[kind,key]],'oracle_exit':run.returncode,'oracle_stderr':run.stderr.decode('utf-8','surrogateescape').replace(str(file),'input.php')})
            def parse_ast(source):
                parsed=frontend.request({'op':'parse','source':base64.b64encode(source).decode()})
                assert parsed['accepted'],parsed
                return parsed['ast']
            echo=parse_ast(b'<?php echo 1;')['program'][0]
            semi=parse_ast(b'<?php namespace N;')['program'][0]
            braced=parse_ast(b'<?php namespace N {}')['program'][0]
            nested=copy.deepcopy(braced); nested['fields'][1]=[copy.deepcopy(braced)]
            reserved=copy.deepcopy(semi); reserved['fields'][0]['fields'][0]={'bytes':base64.b64encode(b'namespace').decode()}
            edited_cases=[
                (b'<?php echo 1; namespace N;', [echo,semi],True),
                (b'<?php namespace N {} echo 1;', [braced,echo],True),
                (b'<?php namespace N; namespace N {}', [semi,braced],False),
                (b'<?php namespace N {} namespace N;', [braced,semi],False),
                (b'<?php namespace N { namespace N {} }', [nested],False),
                (b'<?php namespace namespace;', [reserved],False),
                (b'<?php use\nA; namespace\nN;', [parse_ast(b'<?php use\nA;')['program'][0],parse_ast(b'<?php\nnamespace\nN;')['program'][0]],False),
                (b'<?php namespace N {} namespace\nM;', [braced,parse_ast(b'<?php namespace\nM;')['program'][0]],False),
                (b'<?php use A; namespace N;', [parse_ast(b'<?php use A;')['program'][0],semi],False),
                (b'<?php namespace N {} use A;', [braced,parse_ast(b'<?php use A;')['program'][0]],False),
            ]
            for source in [b'<?php namespace N {} __halt_compiler();data',b'<?php declare(ticks=1) { echo 1; } namespace N;']:
                edited_cases.append((source,parse_ast(source)['program'],True))
            for i,(source,nodes,resume) in enumerate(edited_cases):
                ast=parse_ast(b'<?php');ast['program']=copy.deepcopy(nodes)
                checked=adapter.request({'op':'check','ast':ast,'fixture':True})
                file.write_bytes(source)
                run=subprocess.run([str(types.PHP),'-n',*types.FLAGS,'-l',str(file)],capture_output=True,env=types.ENV,timeout=10)
                assert run.returncode in [0,255],run
                assertions=f'  -- if plresult = $plstart(5000, {checked["fixture"]}, {types.byte_expr(str(file))})\n'
                if resume:
                    assertions+='  -- if plstate = $plteststate(plresult)\n  -- if pllocation = $pltestlocation(plstate)\n  -- if plresult_final = $plresume(plstate, PLCOMPILED (pllocation[.LINE = 1]) plstate.ENV)\n'
                    assertions+='  -- if $plresume(plstate, PLCOMPILED pllocation plstate.ENV) = PLUNSUPPORTED "invalid compiler-work resumption"\n'
                    assertions+='  -- if $plresume(plstate, PLCOMPILED (pllocation[.LINE = 1][.UNIT = 6000]) plstate.ENV) = PLUNSUPPORTED "invalid compiler-work resumption"\n'
                else: assertions+='  -- if plresult_final = plresult\n'
                assertions+='  -- if $pltestok(plresult_final) = '+str(run.returncode==0).lower()+'\n  -- if $pltestevents(plresult_final) = '+expected_events(events(run),file)+'\n'
                fixtures.append(f'dec $resume{i}() : bool\ndef $resume{i}() = true\n'+assertions)
                resume_records.append({'id':'resume-'+str(i),'scope':'checked edited namespace shape and/or explicitly supplied successful ordinary compiler result; no body compilation claimed','source_base64':base64.b64encode(source).decode(),'frontend':frontend.request({'op':'parse','source':base64.b64encode(source).decode()}),'native_parser':frontend.request({'op':'oracle','source':base64.b64encode(source).decode()}),'supplied_compiled':resume,'oracle_exit':run.returncode,'oracle_stderr':run.stderr.decode('utf-8','surrogateescape').replace(str(file),'input.php')})
            # Source-derived anonymous brace metadata supplies the compiler line.
            source=b'<?php namespace N; namespace\n{\n}'
            ast=parse_ast(b'<?php namespace N;')
            anonymous=parse_ast(b'<?php namespace\n{\n}')['program'][0]
            ast['program'].append(anonymous)
            checked=adapter.request({'op':'check','ast':ast,'fixture':True})
            file.write_bytes(source)
            run=subprocess.run([str(types.PHP),'-n',*types.FLAGS,'-l',str(file)],capture_output=True,env=types.ENV,timeout=10)
            assert run.returncode==255
            assertions='  -- if plresult = $plstart(8000, '+checked['fixture']+', '+types.byte_expr(str(file))+')\n'
            assertions+='  -- if $pltestevents(plresult) = '+expected_events(events(run),file)+'\n'
            # The brace metadata is retained through checking and actively controls diagnostics.
            assert anonymous['meta']['namespaceBraceLine']=={'int':'2'}
            assertions+='  -- if $plcompileline('+occurrences.node_term(anonymous)+') = 2\n'
            changed=copy.deepcopy(ast);changed['program'][1]['meta']['namespaceBraceLine']={'int':'3'}
            checked_changed=adapter.request({'op':'check','ast':changed,'fixture':True})
            assertions+='  -- if $pltestevents($plstart(8000, '+checked_changed['fixture']+', '+types.byte_expr(str(file))+')) = '+expected_events([(level,message,3) for level,message,line in events(run)],file)+'\n'
            missing=copy.deepcopy(ast);del missing['program'][1]['meta']['namespaceBraceLine']
            checked_missing=adapter.request({'op':'check','ast':missing,'fixture':True})
            assertions+='  -- if $plstart(8000, '+checked_missing['fixture']+', '+types.byte_expr(str(file))+') = PLUNSUPPORTED "missing namespace compiler line (anonymous opening brace requires source context)"\n'
            # An absent one-line brace can be inferred; explicit invalid metadata cannot.
            one_line=copy.deepcopy(ast)
            one_line['program'][1]=parse_ast(b'<?php namespace {}')['program'][0]
            for value,expected in [(None,'PLERROR'),('0','PLUNSUPPORTED'),('-1','PLUNSUPPORTED')]:
                probe=copy.deepcopy(one_line)
                if value is None: del probe['program'][1]['meta']['namespaceBraceLine']
                else: probe['program'][1]['meta']['namespaceBraceLine']={'int':value}
                checked_probe=adapter.request({'op':'check','ast':probe,'fixture':True})
                outcome='$plstart(8000, '+checked_probe['fixture']+', '+types.byte_expr(str(file))+')'
                if expected=='PLUNSUPPORTED':
                    assertions+='  -- if '+outcome+' = PLUNSUPPORTED "missing namespace compiler line (anonymous opening brace requires source context)"\n'
                else:
                    assertions+='  -- if '+outcome+' = PLERROR pldiagnostic_one*\n'
            fixtures.append('dec $anonymousline() : bool\ndef $anonymousline() = true\n'+assertions)
            resume_records.append({'id':'anonymous-opening-brace-line','scope':'source-derived checked brace metadata consumed in edited namespace sequence; mutation changes compiler event line; missing edited metadata is Unsupported','source_base64':base64.b64encode(source).decode(),'brace_line':2,'mutated_line':3,'one_line_missing_field':'diagnostic line inferred','one_line_explicit_nonpositive':['0','-1'],'oracle_exit':run.returncode,'oracle_stderr':run.stderr.decode('utf-8','surrogateescape').replace(str(file),'input.php')})
            seed=parse_ast(b'<?php use A;')
            negative_asts=[]
            missing=copy.deepcopy(seed);missing['program'][0]['meta']={};missing['program'][0]['fields'][1][0]['fields'][1]['meta']={};negative_asts.append((missing,'missing context metadata or edited namespace/import shape'))
            badkind=copy.deepcopy(seed);badkind['program'][0]['fields'][0]={'int':'0'};negative_asts.append((badkind,'missing context metadata or edited namespace/import shape'))
            empty=copy.deepcopy(seed);empty['program'][0]['fields'][1]=[];negative_asts.append((empty,'missing context metadata or edited namespace/import shape'))
            invalid=copy.deepcopy(seed);invalid['program'][0]['fields'][1][0]['fields'][1]['fields'][0]={'bytes':''};negative_asts.append((invalid,'edited invalid import name'))
            for i,(ast,message) in enumerate(negative_asts):
                checked=adapter.request({'op':'check','ast':ast,'fixture':True})
                fixtures.append(f'dec $negative{i}() : bool\ndef $negative{i}() = true\n  -- if $plstart(7000, {checked["fixture"]}, ([120])) = PLUNSUPPORTED '+json.dumps(message)+'\n')
                negatives.append({'id':'negative-'+str(i),'message':message,'ast_sha256':hashlib.sha256(json.dumps(checked['ast'],sort_keys=True).encode()).hexdigest()})
            fixture=Path(tmp)/'cases.watsup'
            names=re.findall(r'^dec \$(\w+)\(\)', '\n'.join(fixtures), re.M)
            fixture.write_text(PREFIX+'\n'.join(fixtures)+'\ndec $main() : bool\ndef $main() = true\n'+'\n'.join('  -- if $'+name+'()' for name in names)+'\n')
            result=subprocess.run([str(runner),*map(str,SPECS),str(fixture)],capture_output=True,text=True,timeout=120)
            if result.returncode or result.stdout.strip()!='true':
                (ROOT/'.tools/source-context-failure.watsup').write_text(fixture.read_text())
                raise AssertionError((result.returncode,result.stdout,result.stderr))
    finally: frontend.close(); adapter.close()
    assert before==fingerprint(),'watchedinputs changed'
    report={'scope':'namespace/import compiler prefixes and explicit pending work; no declaration or runtime activation','profile':types.PROFILE,'oracle_identity':identity,'fingerprint':before,'prefix_comparisons':len(records),'barrier_cases':barrier_records,'frontend_rejections':rejected,'descriptor_cases':descriptor_records,'seen_symbol_cases':seen_records,'resumption_cases':resume_records,'negative_cases':negatives,'cases':records}
    (ROOT/'coverage/semantics/source-context.json').write_text(json.dumps(report,indent=2)+'\n')
    print(len(records),'prefix comparisons;',len(rejected),'frontend rejections;',len(barrier_records),'barriers;',len(descriptor_records),'descriptors;',len(seen_records),'seen-symbol inputs;',len(resume_records),'resumptions;',len(negatives),'negatives')

if __name__=='__main__':main()
