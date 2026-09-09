#!/usr/bin/env python3
"""Ordered source compiler checks, independently of source runtime execution."""
import base64,copy,hashlib,importlib.util,json,signal,subprocess,sys,tempfile,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tests/semantics'))
import static_types as types,source_context as context,source_occurrences as occurrences
SPECS=list(dict.fromkeys([ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]+[ROOT/'spec/semantics/16-static-types.watsup',ROOT/'spec/semantics/21-source-context.watsup',ROOT/'spec/semantics/44-dimension-read.watsup',ROOT/'spec/semantics/45-constant-context.watsup',ROOT/'spec/semantics/46-source-compiler.watsup']))
PREFIX=context.PREFIX+'''
dec $pptrace(ppstate) : (text,ptbytes,ptbytes,nat)*
def $pptrace(P) = ($pltestevent(pldiagnostic))*
  -- if P.DIAGNOSTICS = pldiagnostic*
  -- if P.COMPLETION = PPCNORMAL
def $pptrace(P) = ($pltestevent(pldiagnostic))*
  -- if P.DIAGNOSTICS = pldiagnostic*
  -- if P.COMPLETION = PPCNAMESPACE
def $pptrace(P) = ($pltestevent(pldiagnostic))* ++ [("fatal",$ptascii(text),P.LOCATION.FILE,n)]
  -- if P.DIAGNOSTICS = pldiagnostic*
  -- if P.COMPLETION = PPCABRUPT (STATICERROR text z)
  -- if z = n
'''
PREFIX+='''
dec $access_paths((pcpath, ppmode)*) : pcpath*
def $access_paths(eps) = eps
def $access_paths((pcpath, ppmode) :: (pcpath_tail, ppmode_tail)*) = pcpath :: $access_paths((pcpath_tail, ppmode_tail)*)
dec $expression_paths(ppexprdone*) : pcpath*
def $expression_paths(eps) = eps
def $expression_paths((PPCEXPR pcpath n pvalue?) :: ppexprdone*) = pcpath :: $expression_paths(ppexprdone*)
'''
LINES=[b'<?php $u=7;\necho [$u, \"abc\"[\n\"1x\"]];',b'<?php $u=7;\necho \"abc\"[\n\"1x\"];',b'<?php $u=7;\necho [\"abc\"[\n\"-1x\"]];',b'<?php $u=7;\necho [$u=[\"abc\"[\n\"1x\"]]];',b'<?php $u=[NAN];\necho ($u[\n0]=$u);']
# Rewritten values inherit the prepass compiler line; original scalar leaves do not.
LINES += [b'<?php $u=1;\necho [\n $u,\n "abc"[\n "1x"\n ],\n];', b'<?php $u=1;\necho [\n 1,\n $u,\n "abc"["1x"]\n];', b'<?php $u=1;\necho [\n $u,\n NAN\n];', b'<?php $u=1;\necho [\n $u,\n true\n];', b'<?php $u=1;\necho [\n $u,\n 1+\n 2\n];', b'<?php $u=1;\necho [\n $u,\n -\n 2\n];', b'<?php $u=1;\necho [\n "abc"[\n "1x"\n]\n];', b'<?php $u=1;\necho [\n $u,\n "last"\n];', b'<?php $u=1;\necho [\n $u,\n $u+\n 2\n];', b'<?php $u=1;\necho [\n $u,\n ($v="abc"[\n "1x"\n ])\n];']
CASES=[b'<?php use A; echo ${[[]=>1]}; use B;',b'<?php use A; $x=[($u=[&$v[]])]; use B;',b'<?php use A; echo ${[$u=[&$v[]]]}; use B;',b'<?php $u=7; echo ${[$u=["abc"["1x"]]]};',b'<?php $a=[[1]]; $a[0][0] = 2;',b'<?php $a=[[1]]; unset($a[0][]);',b'<?php namespace N; use function A as Self; echo 1;',b'<?php echo 1;',b'<?php $a=[NAN]+[];',b'<?php echo [NAN] === [NAN];',b'<?php $a=[1/0]; use A;',b'<?php $a=[1,2]; echo $a[0];',b'<?php $u=7; $a=[$u,"abc"["1x"]];',b'<?php $u=7; $a=[&$u,"abc"["1x"]];',b'<?php $a=[($u=["abc"["1x"]])];',b'<?php $a=[($u=&$v),["abc"["1x"]]];',b'<?php $a=[&$u[]];',b'<?php $a=[$u,&$v[]];',b'<?php $a=["abc"["1x"]=>$u[]];',b'<?php $a=[$u[]=>"abc"["1x"]];',b'<?php $a=[[]=>1];',b'<?php echo 1; $a=[&$u[]];',b'<?php use A; $a=[&$u[]]; use B;',b'<?php use A; echo 1; use A;',b'<?php use A; {break;} use B;',b'<?php $a=[1]; $a[0]=$a;',b'<?php $a=[1]; $a[0]=&$a;',b'<?php $a=[1]; unset($a[0]);',b'<?php $a=[1]; unset($a[]);',b'<?php $x=&$a[];',b'<?php namespace N; echo 1; use A; echo 2;',b'<?php namespace N {echo 1; use A;} namespace M {echo 2;}',b'<?php use A; {$x=[1,2];echo $x[0];} use B;',b'<?php {echo 1;} {echo 2;}',b'<?php $a=[[NAN],[NAN]]; $x=$a[0] === $a[1];']
CASES.append(b'<?php use V\\A as X\xff\xc2\x85\xe2\x80\xa8; use V\\B as X\xff\xc2\x85\xe2\x80\xa8;')
loader=importlib.util.spec_from_file_location('runtime_cases',ROOT/'tests/semantics/validate.py')
runtime_cases=importlib.util.module_from_spec(loader);loader.loader.exec_module(runtime_cases)
SOURCE_CASES=[('baseline/'+name,source) for name,source in runtime_cases.CASES.items()]+[('targeted/'+str(i),source) for i,source in enumerate(CASES)]

I=lambda n:('INDEX',n)
F=lambda n:('FIELD',n)
ACCESS_CASES=[
 (b'<?php echo $a[0];', [([I(0),F(0),I(0)],'PPR'),([I(0),F(0),I(0),F(0)],'PPR'),([I(0),F(0),I(0),F(1)],'PPR')]),
 (b'<?php $a[0]=1;', [([I(0),F(0)],'PPR'),([I(0),F(0),F(0)],'PPW'),([I(0),F(0),F(0),F(0)],'PPW'),([I(0),F(0),F(0),F(1)],'PPR'),([I(0),F(0),F(1)],'PPR')]),
 (b'<?php $x=&$a[0];', [([I(0),F(0),F(0)],'PPW'),([I(0),F(0),F(1)],'PPW'),([I(0),F(0),F(1),F(0)],'PPW'),([I(0),F(0),F(1),F(1)],'PPR')]),
 (b'<?php unset($a[0]);', [([I(0),F(0),I(0)],'PPUNSET'),([I(0),F(0),I(0),F(0)],'PPUNSET'),([I(0),F(0),I(0),F(1)],'PPR')]),
 (b'<?php $a=[&$x,$k=>$v];', [([I(0),F(0),F(1)],'PPR'),([I(0),F(0),F(1),F(0),I(0),F(1)],'PPW'),([I(0),F(0),F(1),F(0),I(1),F(0)],'PPR'),([I(0),F(0),F(1),F(0),I(1),F(1)],'PPR')]),
 (b'<?php ${$name}=1;', [([I(0),F(0),F(0)],'PPW'),([I(0),F(0),F(0),F(0)],'PPR')]),
 (b'<?php $u=0;echo [$u,"abc"["1x"]];', [([I(1),F(0),I(0),F(0),I(1),F(1)],'PPR'),([I(1),F(0),I(0),F(0),I(1),F(1),F(0)],None)]),
 (b'<?php $a[0]=$a;', [([I(0),F(0),F(1)],'PPR')]),
]

def oracle_record(source, checked, command, run):
    return {'source_base64':base64.b64encode(source).decode(), 'ast_sha256':hashlib.sha256(json.dumps(checked['ast'],sort_keys=True).encode()).hexdigest(), 'command':command, 'cwd':str(ROOT), 'status':run.returncode, 'stdout_base64':base64.b64encode(run.stdout).decode(), 'stderr_base64':base64.b64encode(run.stderr).decode()}

def main():
    # Oracle diagnostics are PHP bytes, including invalid UTF-8 and Unicode
    # separator sequences that must not be mistaken for physical output lines.
    raw_message=b'Cannot use X\xff\xc2\x85\xe2\x80\xa8 as Y'
    probe=subprocess.CompletedProcess([],255,b'',b'Fatal error: '+raw_message+b' in input.php on line 1\n')
    parsed_message=context.events(probe)[0][1]
    assert parsed_message.encode('utf-8','surrogateescape')==raw_message
    assert types.byte_expr(parsed_message)=='['+','.join(map(str,raw_message))+']'
    def expired(signum,frame): raise TimeoutError('compiler worker request exceeded30seconds')
    signal.signal(signal.SIGALRM,expired)
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'),'dune','build','--root',str(types.HERE),'numeric_runner.exe'],cwd=ROOT,check=True,timeout=120)
    runner=ROOT/'tests/semantics/_build/default/numeric_runner.exe'
    watched=SPECS+[Path(__file__),ROOT/'tests/semantics/validate.py',runner,ROOT/'vendor/php-src/Zend/zend_compile.c']
    def fingerprint(): return {'closure':types.syntax_validation.implementation_fingerprint(), 'direct':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}}
    before=fingerprint()
    identity=json.loads(subprocess.run([str(types.PHP),'-n',*types.FLAGS,'-r','echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,ini_get_all(null,false)]);'],capture_output=True,text=True,env=types.ENV,timeout=10,check=True).stdout)
    assert identity[:4]==['8.5.10','cli',8,False]
    assert all(identity[4][k]==v for k,v in types.PROFILE.items())
    f=types.Worker([str(types.PHP),'-n','-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')]);a=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    prefix=PREFIX+'''
    dec $pprecord(ppexprdone*, pcpath) : ppexprdone?
    def $pprecord(eps, pcpath) = eps
    def $pprecord((PPCEXPR pcpath n pvalue?) :: ppexprdone*, pcpath) = (PPCEXPR pcpath n pvalue?)
    def $pprecord((PPCEXPR pcpath_other n pvalue?) :: ppexprdone*, pcpath) = $pprecord(ppexprdone*, pcpath)
            -- if pcpath_other =/= pcpath
    '''
    fixtures=[];records=[]
    try:
        with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as tmp:
            file=Path(tmp)/'input.php'
            for i,(case_id,source) in enumerate(SOURCE_CASES):
                parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                checked=a.request({'op':'check','ast':parsed['ast'],'fixture':True})
                file.write_bytes(source);command=[str(types.PHP),'-n',*types.FLAGS,'-l',str(file)]
                run=subprocess.run(command,capture_output=True,cwd=ROOT,env=types.ENV,timeout=10)
                events=context.events(run)
                fixtures.append(f'dec $case{i}() : bool\ndef $case{i}() = true\n  -- if P = $ppstart(91, {checked["fixture"]}, {types.byte_expr(str(file))})\n  -- if $pptrace(P) = '+context.expected_events(events,file)+'\n'+('  -- if P.COMPLETION = PPCNORMAL\n' if run.returncode==0 else ''))
                if source==b'<?php $a=[NAN]+[];':
                    path=occurrences.path_term([('INDEX',0),('FIELD',0),('FIELD',1)])
                    fixtures[-1]+='  -- if $pffact(P.FOLD.FACTS, '+path+') = eps\n  -- if $pprecord(P.EXPRESSIONS, '+path+') = (PPCEXPR '+path+' 1 (PARRAY n_result))\n  -- if $entry_lookup(P.FOLD.MEMORY.ARRAYS[n_result].ITEMS, KINT 0) = (DIRECT (PFLOAT 9221120237041090560))\n  -- if S_pruned = $prune_allocations(P.FOLD.MEMORY[.RESULT = KNOWN PNULL])\n  -- if S_pruned.ALLOCATIONS = P.FOLD.MEMORY.ALLOCATIONS\n'
                if source==b'<?php echo [NAN] === [NAN];':
                    path=occurrences.path_term([('INDEX',0),('FIELD',0),('INDEX',0)])
                    fixtures[-1]+='  -- if $pprecord(P.EXPRESSIONS, '+path+') = (PPCEXPR '+path+' 1 (PBOOL false))\n'
                records.append({'id':case_id, 'kind':'compiler-lint', 'oracle':oracle_record(source,checked,command,run), 'events':events})
            for source in LINES:
                i=len(fixtures);parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                checked=a.request({'op':'check','ast':parsed['ast'],'fixture':True})
                file.write_bytes(source);command=[str(types.PHP),'-n',*types.FLAGS,str(file)]
                run=subprocess.run(command,capture_output=True,cwd=ROOT,env=types.ENV,timeout=10)
                assert run.returncode==0,(source,run.stdout,run.stderr)
                events=context.events(run);assert events,source
                line=events[-1][2];path=occurrences.path_term([('INDEX',1),('FIELD',0),('INDEX',0)])
                fixtures.append(f'dec $case{i}() : bool\ndef $case{i}() = true\n  -- if P = $ppstart(91, {checked["fixture"]}, {types.byte_expr(str(file))})\n  -- if P.COMPLETION = PPCNORMAL\n  -- if $pprecord(P.EXPRESSIONS, {path}) = (PPCEXPR {path} {line} pvalue?)\n')
                records.append({'id':'emission-line-'+str(i),'kind':'emission-line','oracle':oracle_record(source,checked,command,run),'events':events,'path':path,'expected_line':line})
            for source,message in [(b'<?php use A; function f(){} use B;','ordinary statement compilation'),(b'<?php namespace N; $a=[1];','invalid constant-expression occurrence, compiler line, or unsupported namespace/import context'),(b'<?php use const PHP_INT_MAX as B;echo B;','ordinary expression or writable operand compilation'),(b'<?php echo ${[1]};','compile-time array name diagnostic'),(b'<?php echo ${NAN};','compile-time NaN name diagnostic'),(b'<?php namespace N {echo 1;} namespace {echo 2;} __halt_compiler();','ordinary statement compilation')]:
                i=len(fixtures);parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                checked=a.request({'op':'check','ast':parsed['ast'],'fixture':True})
                fixtures.append(f'dec $case{i}() : bool\ndef $case{i}() = true\n  -- if P = $ppstart(91, {checked["fixture"]}, {types.byte_expr(str(file))})\n  -- if P.COMPLETION = PPCABRUPT (UNSUPPORTED '+json.dumps(message)+')\n')
                file.write_bytes(source);command=[str(types.PHP),'-n',*types.FLAGS,'-l',str(file)]
                run=subprocess.run(command,capture_output=True,cwd=ROOT,env=types.ENV,timeout=10)
                records.append({'id':'unsupported-'+str(i),'kind':'unsupported-context','oracle':oracle_record(source,checked,command,run),'reason':message})
            parsed=f.request({'op':'parse','source':base64.b64encode(b'<?php echo 1;').decode()})
            for line in [None,'0','-1']:
                ast=copy.deepcopy(parsed['ast']);node=ast['program'][0]['fields'][0][0]
                if line is None:node['meta'].pop('startLine')
                else:node['meta']['startLine']={'int':line}
                checked=a.request({'op':'check','ast':ast,'fixture':True});i=len(fixtures)
                fixtures.append(f'dec $case{i}() : bool\ndef $case{i}() = true\n  -- if P = $ppstart(91, {checked["fixture"]}, {types.byte_expr(str(file))})\n  -- if P.COMPLETION = PPCABRUPT (UNSUPPORTED "missing ordinary compiler line")\n')
            source=b'<?php echo [[NAN],[NAN]];'
            parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()})
            checked=a.request({'op':'check','ast':parsed['ast'],'fixture':True})
            path=occurrences.path_term([('INDEX',0),('FIELD',0),('INDEX',0)])
            child=occurrences.path_term([('INDEX',0),('FIELD',0),('INDEX',0),('FIELD',0),('INDEX',0),('FIELD',1)])
            i=len(fixtures)
            fixtures.append(f'dec $case{i}() : bool\ndef $case{i}() = true\n  -- if P = $ppstart(91, {checked["fixture"]}, ([120]))\n  -- if P.COMPLETION = PPCNORMAL\n  -- if $pffact(P.FOLD.FACTS, {path}) = (PARRAY n_root)\n  -- if $pffact(P.FOLD.FACTS, {child}) = (PARRAY n_child)\n  -- if n_root =/= n_child\n  -- if $ppconstants(P) = PPCCONSTANTS (pcpath_constants, pvalue_constants)*\n  -- if $ppconstant_at((pcpath_constants, pvalue_constants)*, {path}) = (PARRAY n_root)\n  -- if $ppconstants(P[.EXPRESSIONS = P.EXPRESSIONS ++ [PPCEXPR {path} 1 (PARRAY n_root)]]) = $ppconstants(P)\n  -- if $ppconstants(P[.EXPRESSIONS = P.EXPRESSIONS ++ [PPCEXPR {path} 1 (PINT 9)]]) = PPCINVALID "conflicting constant values for one source occurrence"\n  -- if $ppconstants(P[.EXPRESSIONS = P.EXPRESSIONS ++ [PPCEXPR {path} 1 (PARRAY n_child)]]) = PPCINVALID "conflicting constant values for one source occurrence"\n  -- if $ppconstants(P[.EXPRESSIONS = P.EXPRESSIONS ++ [PPCEXPR {path} 0 eps]]) = PPCINVALID "missing compiled operand line"\n  -- if $ppconstants(P[.FOLD = P.FOLD[.FACTS = [PFFACT {path} (PARRAY n_root) 0]]]) = PPCINVALID "missing constant rewrite line"\n  -- if $ppconstants(P[.COMPLETION = PPCNAMESPACE]) = PPCINVALID "incomplete source compilation"\n')
            for source, probes in ACCESS_CASES:
                i=len(fixtures);parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                checked=a.request({'op':'check','ast':parsed['ast'],'fixture':True})
                body=f'dec $case{i}() : bool\ndef $case{i}() = true\n  -- if P = $ppstart(91, {checked["fixture"]}, ([120]))\n  -- if P.COMPLETION = PPCNORMAL\n'
                for steps,mode in probes:
                    path=occurrences.path_term(steps)
                    body+='  -- if $ppaccess(P, '+path+') = '+('eps' if mode is None else '('+mode+')')+'\n'
                present=occurrences.path_term(next(steps for steps,mode in probes if mode is not None))
                body+='  -- if $ppaccess(P[.COMPLETION = PPCNAMESPACE], '+present+') = eps\n  -- if $ppaccess(P[.COMPLETION = PPCABRUPT (UNSUPPORTED "probe")], '+present+') = eps\n  -- if $access_paths(P.ACCESS) = $expression_paths(P.EXPRESSIONS)\n'
                file.write_bytes(source);command=[str(types.PHP),'-n',*types.FLAGS,'-l',str(file)]
                run=subprocess.run(command,capture_output=True,cwd=ROOT,env=types.ENV,timeout=10)
                assert run.returncode==0,(source,run.stdout,run.stderr)
                records.append({'id':'access-'+str(i),'kind':'compiler-access','oracle':oracle_record(source,checked,command,run),'expected_access':[{'path':occurrences.path_term(steps),'mode':mode} for steps,mode in probes]})
                fixtures.append(body)
            file=Path(tmp)/'cases.watsup' ;file.write_text(prefix+'\n'.join(fixtures)+'\ndec $main() : bool\ndef $main() = true\n'+''.join(f'  -- if $case{i}()\n' for i in range(len(fixtures))))
            run=subprocess.run([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),*map(str,SPECS),str(file)],capture_output=True,text=True,timeout=120)
            if run.returncode or run.stdout.strip()!='true':
                (ROOT/'.tools/source-compiler-failure.watsup').write_text(file.read_text());raise AssertionError((run.returncode,run.stdout,run.stderr))
            print(len(ACCESS_CASES),'access sources;',sum(len(probes) for source,probes in ACCESS_CASES),'access paths;',len(SOURCE_CASES),'compiler lint comparisons;',len(LINES),'emission-line observations; 6 Unsupported contexts; 3 metadata boundaries; constant export merge checks passed')
    finally:f.close();a.close()
    assert before==fingerprint(),'watched inputs changed'
    report={'scope':'ordered compiler work, access and operand descriptors; no source runtime integration', 'profile':types.PROFILE,'oracle_identity':identity,'fingerprint':before,'baseline_cases':len(runtime_cases.CASES),'targeted_lint_cases':len(CASES),'byte_diagnostic_checks':['invalid UTF-8 roundtrip','Unicode separators are not output line breaks'],'access_sources':len(ACCESS_CASES),'access_paths':sum(len(probes) for source,probes in ACCESS_CASES),'emission_line_cases':len(LINES),'unsupported_contexts':6,'constant_export_checks':['matching duplicate','conflicting scalar','conflicting array ID','missing operand line','missing fact line','incomplete compilation'],'metadata_boundaries':[None,'0','-1'],'cases':records}
    (ROOT/'coverage/semantics/source-compiler.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__': main()
