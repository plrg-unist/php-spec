#!/usr/bin/env python3
"""Checked non-class names against original-source lookup diagnostics and controls."""
import base64,hashlib,json,re,signal,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tests/semantics'))
import static_types as types,source_context as context,source_occurrences as occurrences
SPECS=context.SPECS+[ROOT/'spec/semantics/22-name-resolution.watsup']
CASES=[]
def add(kind,prefix,name,resolved,full,fallback=None,output=None):
    as_bytes=lambda x:x if isinstance(x,bytes) else x.encode()
    CASES.append((kind,*map(as_bytes,[prefix,name,resolved]),full,None if fallback is None else as_bytes(fallback),output))
for kind in ['PLCONSTANT','PLFUNCTION']:
    add(kind,'','Missing','Missing',False)
    add(kind,'','\\Missing','Missing',True)
    add(kind,'','namespace\\Missing','Missing',True)
    add(kind,'namespace Ns;','Missing','Ns\\Missing',False,'Missing')
    add(kind,'namespace Ns;','\\Missing','Missing',True)
    add(kind,'namespace Ns;','namespace\\Missing','Ns\\Missing',True)
    add(kind,'namespace Ns;','Sub\\Missing','Ns\\Sub\\Missing',True)
    add(kind,'namespace Ns;use Vendor\\Package as A;','a\\Missing','Vendor\\Package\\Missing',True)
    add(kind,'namespace Ns;use Vendor\\{Package as A};','A\\Missing','Vendor\\Package\\Missing',True)
    add(kind,'namespace Ns;use Vendor\\Package as A;','A','Ns\\A',False,'A')
    add(kind,'namespace Ns;use Vendor\\Package as A;','namespace\\A\\Missing','Ns\\A\\Missing',True)
    add(kind,'namespace Ns;use Vendor\\Package as A;','\\A\\Missing','A\\Missing',True)
    add(kind,'namespace Ns;use function Vendor\\fun as A;use const Other\\VALUE as B;','A\\Missing','Ns\\A\\Missing',True)
    add(kind,b'namespace N\xff;use V\xfe\\Pkg as A;','A\\Missing',b'V\xfe\\Pkg\\Missing',True)
    add(kind,'namespace É;use V\\Pkg as É;','é\\Missing','É\\é\\Missing',True)
    add(kind,'namespace É;use V\\Pkg as É;','É\\Missing','V\\Pkg\\Missing',True)
    add(kind,'namespace Before {use Vendor\\Package as A;} namespace After {','A\\Missing','After\\A\\Missing',True)
for kind,word in [('PLFUNCTION','function'),('PLCONSTANT','const')]:
    add(kind,'namespace Ns;use '+word+' Vendor\\Missing as A;','A','Vendor\\Missing',True)
    add(kind,'namespace Ns;use '+word+' Vendor\\{Missing as A};','A','Vendor\\Missing',True)
    add(kind,'namespace Ns;use '+word+' Vendor\\Missing as A;','a','Vendor\\Missing' if kind=='PLFUNCTION' else 'Ns\\a',kind=='PLFUNCTION',None if kind=='PLFUNCTION' else 'a')
    add(kind,'namespace Ns;use '+word+' Vendor\\Missing as A;','namespace\\A','Ns\\A',True)
for name in ['strlen','STRLEN']:
    add('PLFUNCTION','namespace Ns;',name,'Ns\\'+name,False,name,b'3')
    add('PLFUNCTION','namespace Ns;','\\'+name,name,True,None,b'3')
add('PLFUNCTION','namespace Ns;use function strlen as Measure;','mEaSuRe','strlen',True,None,b'3')
add('PLFUNCTION','namespace Ns;use function strlen as Self;','Self','strlen',True,None,b'3')
add('PLCONSTANT','namespace Ns;','NAN','Ns\\NAN',False,'NAN',b'NAN')
add('PLCONSTANT','namespace Ns;','\\NAN','NAN',True,None,b'NAN')
add('PLCONSTANT','namespace Ns;use const NAN as V;','V','NAN',True,None,b'NAN')
add('PLCONSTANT','namespace Ns;use const NAN as V;','v','Ns\\v',False,'v')
for name,output in [('true',b'1'),('FaLsE',b''),('NULL',b'')]:
    add('PLCONSTANT','namespace Ns;',name,'Ns\\'+name,False,name,output)
    add('PLCONSTANT','namespace Ns;','\\'+name,name,True,None,output)
    add('PLCONSTANT','namespace Ns;','namespace\\'+name,'Ns\\'+name,True)

def bytes_term(value):return "(["+",".join(map(str,value))+"])"

def target(ast,kind):
    wanted='Expr_ConstFetch' if kind=='PLCONSTANT' else 'Expr_FuncCall'
    def walk(x):
        if isinstance(x,dict):
            if x.get('node')==wanted:return x['fields'][0]
            for value in x.values():
                found=walk(value)
                if found is not None:return found
        if isinstance(x,list):
            for value in x:
                found=walk(value)
                if found is not None:return found
    return walk(ast)

def main():
    signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('name worker exceeded30seconds')))
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'),'dune','build','--root',str(types.HERE),'numeric_runner.exe'],cwd=ROOT,check=True,timeout=120)
    runner=ROOT/'tests/semantics/_build/default/numeric_runner.exe'
    watched=SPECS+[Path(__file__),runner,ROOT/'vendor/php-src/Zend/zend_compile.c']
    fingerprint=lambda:{'closure':types.syntax_validation.implementation_fingerprint(),'direct':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}}
    before=fingerprint();records=[];fixtures=[]
    identity=json.loads(subprocess.run([str(types.PHP),'-n',*types.FLAGS,'-r','echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,ini_get_all(null,false)]);'],capture_output=True,text=True,cwd=ROOT,env=types.ENV,timeout=10,check=True).stdout)
    assert identity[:4]==['8.5.10','cli',8,False] and all(identity[4][k]==v for k,v in types.PROFILE.items())
    f=types.Worker([str(types.PHP),'-n','-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')]);a=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    try:
        with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as tmp:
            file=Path(tmp)/'input.php'
            for i,(kind,prefix,name,resolved,full,fallback,output) in enumerate(CASES):
                source=b'<?php '+prefix+b'echo '+name+(b'("abc")' if kind=='PLFUNCTION' else b'')+b';'+(b'}' if b'namespace After {' in prefix else b'')
                parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],(source,parsed)
                checked=a.request({'op':'check','ast':parsed['ast'],'fixture':True});node=target(checked['ast'],kind);assert node,source
                term=occurrences.node_term(node);file.write_bytes(source)
                command=[str(types.PHP),'-n',*types.FLAGS,str(file)];run=subprocess.run(command,capture_output=True,cwd=ROOT,env=types.ENV,timeout=10)
                if output is not None:assert run.returncode==0 and run.stdout==output,(source,run.stdout,run.stderr)
                else:
                    pattern=rb'Undefined constant "([^"]*)"' if kind=='PLCONSTANT' else rb'Call to undefined function ([^\n]*?)\(\)'
                    match=re.search(pattern,run.stderr);assert run.returncode==255 and match and match.group(1)==resolved,(source,resolved,run.stdout,run.stderr)
                fallback_term='eps' if fallback is None else '('+bytes_term(fallback)+')'
                expected='{ ORIGINAL '+term+', KIND '+kind+', RESOLVED '+bytes_term(resolved)+', FULL '+str(full).lower()+', FALLBACK '+fallback_term+' }'
                fixtures.append(f'dec $case{i}() : bool\ndef $case{i}() = true\n  -- if $plstart(1, {checked["fixture"]}, ([120])) = PLWORK pcoccurrence plstate pldiagnostic*\n  -- if $pnresolve(plstate.ENV, {kind}, {term}) = PNRESOLVED '+expected+'\n')
                records.append({'id':i,'source_base64':base64.b64encode(source).decode(),'ast_sha256':hashlib.sha256(json.dumps(checked['ast'],sort_keys=True).encode()).hexdigest(),'kind':kind,'resolved_base64':base64.b64encode(resolved).decode(),'full':full,'fallback_base64':None if fallback is None else base64.b64encode(fallback).decode(),'observation':'undefined-name diagnostic' if output is None else 'successful builtin/special-constant control','oracle':{'command':command,'cwd':str(ROOT),'status':run.returncode,'stdout_base64':base64.b64encode(run.stdout).decode(),'stderr_base64':base64.b64encode(run.stderr).decode()}})
            for name in [b'',b'\\Bad',b'Bad\\',b'A\\\\B',b'1Bad',b'A\0B']:
                i=len(fixtures);term='NName (BYTES '+json.dumps(base64.b64encode(name).decode())+') eps'
                fixtures.append(f'dec $case{i}() : bool\ndef $case{i}() = true\n  -- if $pnresolve($plempty(false), PLCONSTANT, {term}) = PNUNSUPPORTED "invalid or unsupported non-class name resolution"\n')
            i=len(fixtures);fixtures.append(f'dec $case{i}() : bool\ndef $case{i}() = true\n  -- if $pnresolve($plempty(false), PLCLASS, NName (BYTES "QQ==") eps) = PNUNSUPPORTED "invalid or unsupported non-class name resolution"\n')
            helper=Path(tmp)/'names.watsup';helper.write_text('\n'.join(fixtures)+'\ndec $main() : bool\ndef $main() = true\n'+''.join(f'  -- if $case{i}()\n' for i in range(len(fixtures))))
            run=subprocess.run([str(runner),*map(str,SPECS),str(helper)],capture_output=True,text=True,timeout=60)
            if run.returncode or run.stdout.strip()!='true':
                (ROOT/'.tools/name-resolution-failure.watsup').write_text(helper.read_text());raise AssertionError((run.stdout,run.stderr))
    finally:f.close();a.close()
    assert before==fingerprint(),'watched inputs changed'
    (ROOT/'coverage/semantics/name-resolution.json').write_text(json.dumps({'scope':'lexical non-class resolution;no runtime lookup or source activation','fingerprint':before,'profile':types.PROFILE,'oracle_identity':identity,'cases':records,'edited_boundaries':7},indent=2)+'\n')
    print(len(records),'original source name observations;7 edited boundaries passed')
if __name__=='__main__':main()
