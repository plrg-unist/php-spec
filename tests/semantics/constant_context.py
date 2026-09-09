#!/usr/bin/env python3
"""Exact constant-expression helper facts; runtime source consumption remains pending."""
import base64, copy, hashlib, json, subprocess, sys, tempfile, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tests/semantics'))
import static_types as types, source_occurrences as occurrences
MODULE=ROOT/'spec/semantics/45-constant-context.watsup'
SPECS=[ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]+[ROOT/'spec/semantics/11-source-occurrences.watsup',ROOT/'spec/semantics/16-static-types.watsup',ROOT/'spec/semantics/21-source-context.watsup',ROOT/'spec/semantics/44-dimension-read.watsup',MODULE]
PREFIX='''
syntax pftestvalue = PFNULL | PFBOOL bool | PFINT int | PFFLOAT nat | PFSTRING nat* | PFARRAYVALUE (pkey, pftestvalue)*
dec $pfobserve(pstate, pvalue) : pftestvalue
dec $pfobserveentry(pstate, pentry) : (pkey, pftestvalue)
def $pfobserve(S, PNULL) = PFNULL
def $pfobserve(S, PBOOL b) = PFBOOL b
def $pfobserve(S, PINT i) = PFINT i
def $pfobserve(S, PFLOAT n) = PFFLOAT n
def $pfobserve(S, PSTRING n*) = PFSTRING n*
def $pfobserve(S, PARRAY n) = PFARRAYVALUE ($pfobserveentry(S, pentry))*
  -- if S.ARRAYS[n].ITEMS = pentry*
def $pfobserveentry(S, ENTRY pkey (DIRECT pvalue)) = (pkey, $pfobserve(S, pvalue))
'''
OBSERVER=b'''\nfunction observe($v) { return match(gettype($v)) { 'NULL'=>['n'], 'boolean'=>['b',$v], 'integer'=>['i',(string)$v], 'double'=>['f',bin2hex(pack('E',$v))], 'string'=>['s',bin2hex($v)], 'array'=>['a',array_map(fn($k)=>[observe($k),observe($v[$k])],array_keys($v))] }; } echo json_encode(observe($result[0]));'''
def obs(x):
    k=x[0]
    if k=='n':return 'PFNULL'
    if k=='b':return 'PFBOOL '+str(x[1]).lower()
    if k=='i':return 'PFINT $('+x[1]+')'
    if k=='f':return 'PFFLOAT '+str(int(x[1],16))
    if k=='s':return 'PFSTRING (['+','.join(map(str,bytes.fromhex(x[1])))+'])'
    if k=='a':return 'PFARRAYVALUE (['+','.join('('+('KINT $('+key[1]+')' if key[0]=='i' else 'KSTRING (['+','.join(map(str,bytes.fromhex(key[1])))+'])')+', '+obs(v)+')' for key,v in x[1])+'])'
    raise AssertionError(x)
CASES = [
    ('17', True),
    ('1.5', True),
    ('"a\\x00b"', True),
    ('null', True),
    ('true', True),
    ('false', True),
    ('NAN', True),
    ('INF', True),
    ('1+2*3', True),
    ('8/2', True),
    ('[]', True),
    ('[1,2]', True),
    ('[true=>7,false=>8,1.0=>9]', True),
    ('["1"=>7,"01"=>8]', True),
    ('[[NAN],[NAN]]', True),
    ('[1,2]+[9,8,7]', True),
    ('[1,2] === [1,2]', True),
    ('"abc"["1x"]', True),
    ('"abc"["1"]', True),
    ('"abc"[1]', True),
    ('"abc"[-1]', False),
    ('"abc"[1.0]', False),
    ('"abc"[true]', False),
    ('"abc"[9]', False),
    ('[7,8][true]', False),
    ('[7,8][1.0]', False),
    ('[7,8][1]', True),
    ('[7,8]["1"]', True),
    ('[7,8]["01"]', False),
    ('[null=>7]', False),
    ('[1.5=>7]', False),
    ('[$u,"abc"["1x"]]', False),
    ('[&$u,"abc"["1x"]]', False),
    ('[($u="abc"["1x"])]', False),
    ('[($u=&$v),"abc"["1x"]]', False),
]

def main():
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'),'dune','build','--root',str(types.HERE),'numeric_runner.exe'],cwd=ROOT,check=True,timeout=120)
    runner=ROOT/'tests/semantics/_build/default/numeric_runner.exe'
    watched=SPECS+[Path(__file__),runner,ROOT/'vendor/php-src/Zend/zend_compile.c']
    def fingerprint():
        return {'closure':types.syntax_validation.implementation_fingerprint(), 'direct':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}}
    before=fingerprint()
    identity=json.loads(subprocess.run([str(types.PHP),'-n',*types.FLAGS,'-r','echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,ini_get_all(null,false)]);'],capture_output=True,text=True,env=types.ENV,timeout=10,check=True).stdout)
    assert identity[:4]==['8.5.10','cli',8,False]
    assert all(identity[4][k]==v for k,v in types.PROFILE.items())
    frontend=types.Worker([str(types.PHP),'-n','-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')]);adapter=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    fixtures=[];records=[]
    try:
        with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as tmp:
            file=Path(tmp)/'input.php'
            for i,(expression,folded) in enumerate(CASES):
                source=('<?php $u=7;$v=9;\n$result=['+expression+'];').encode()
                parsed=frontend.request({'op':'parse','source':base64.b64encode(source+OBSERVER).decode()});assert parsed['accepted'],parsed
                checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True});node=checked['ast']['program'][2]['fields'][0]['fields'][1]['fields'][0][0]['fields'][1]
                path=occurrences.path_term([('INDEX',2),('FIELD',0),('FIELD',1),('FIELD',0),('INDEX',0),('FIELD',1)])
                file.write_bytes(source+OBSERVER)
                command=[str(types.PHP),'-n',*types.FLAGS,str(file)]
                run=subprocess.run(command,capture_output=True,cwd=ROOT,env=types.ENV,timeout=10)
                assert run.returncode==0,(source,run.stdout,run.stderr)
                expected=json.loads(run.stdout)
                body=f'dec $case{i}() : bool\ndef $case{i}() = true\n  -- if F = $pfprepare($pfbegin(41, {checked["fixture"]}), {path}, {occurrences.node_term(node)}, $plempty(false), 2)\n  -- if F.MEMORY.COMPLETION = NORMAL\n'
                if folded:
                    body+='  -- if F.VALUE = (pvalue)\n  -- if $pfobserve(F.MEMORY, pvalue) = '+obs(expected)+'\n'
                    body+=f'  -- if $pfprepare(F, {path}, {occurrences.node_term(node)}, $plempty(false), 2) = F\n'
                else: body+='  -- if F.VALUE = eps\n'
                if expression in ['[$u,"abc"["1x"]]','[&$u,"abc"["1x"]]','[($u=&$v),"abc"["1x"]]']:
                    fact_path=occurrences.path_term([('INDEX',2),('FIELD',0),('FIELD',1),('FIELD',0),('INDEX',0),('FIELD',1),('FIELD',0),('INDEX',1),('FIELD',1)])
                    body+='  -- if $pffact(F.FACTS, '+fact_path+') = (PSTRING ([98]))\n'
                    assert run.stderr==b'',run.stderr
                if expression=='[($u="abc"["1x"])]':
                    fact_path=occurrences.path_term([('INDEX',2),('FIELD',0),('FIELD',1),('FIELD',0),('INDEX',0),('FIELD',1),('FIELD',0),('INDEX',0),('FIELD',1),('FIELD',1)])
                    body+='  -- if $pffact(F.FACTS, '+fact_path+') = eps\n'
                    assert b'Illegal string offset' in run.stderr,run.stderr
                if expression=='[[NAN],[NAN]]':
                    left=occurrences.path_term([('INDEX',2),('FIELD',0),('FIELD',1),('FIELD',0),('INDEX',0),('FIELD',1),('FIELD',0),('INDEX',0),('FIELD',1)])
                    right=occurrences.path_term([('INDEX',2),('FIELD',0),('FIELD',1),('FIELD',0),('INDEX',0),('FIELD',1),('FIELD',0),('INDEX',1),('FIELD',1)])
                    body+='  -- if $pffact(F.FACTS, '+left+') = (PARRAY n_left)\n  -- if $pffact(F.FACTS, '+right+') = (PARRAY n_right)\n  -- if n_left =/= n_right\n'
                body+='  -- if S_pruned = $prune_allocations(F.MEMORY[.RESULT = KNOWN PNULL])\n  -- if S_pruned.ALLOCATIONS = F.MEMORY.ALLOCATIONS\n'
                fixtures.append(body);records.append({'expression':expression,'source_base64':base64.b64encode(source+OBSERVER).decode(),'ast_sha256':hashlib.sha256(json.dumps(checked['ast'],sort_keys=True).encode()).hexdigest(),'context':'selected inner expression of outer array compile prepass','folded':folded,'oracle':{'command':command,'cwd':str(ROOT),'status':run.returncode,'stdout_base64':base64.b64encode(run.stdout).decode(),'stderr_base64':base64.b64encode(run.stderr).decode()},'stderr':run.stderr.decode(),'value':expected})
            for expression in ['[&$u[]]','[$u,&$v[]]','["abc"["1x"]=>$u[]]','[$u[]=>"abc"["1x"]]','[[]=>7]','[\n \"abc\"[\"1x\"],\n &$u[]]','[\n $u[]=>\n \"abc\"[\"1x\"]]']:
                i=len(fixtures);source=('<?php $u=7;$v=9;\n$result=['+expression+'];').encode()
                parsed=frontend.request({'op':'parse','source':base64.b64encode(source+OBSERVER).decode()});assert parsed['accepted'],parsed
                checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True});node=checked['ast']['program'][2]['fields'][0]['fields'][1]['fields'][0][0]['fields'][1]
                path=occurrences.path_term([('INDEX',2),('FIELD',0),('FIELD',1),('FIELD',0),('INDEX',0),('FIELD',1)])
                file.write_bytes(source+OBSERVER)
                command=[str(types.PHP),'-n',*types.FLAGS,'-l',str(file)]
                run=subprocess.run(command,capture_output=True,cwd=ROOT,env=types.ENV,timeout=10)
                assert run.returncode==255,(source,run.stdout,run.stderr)
                match=re.search(rb'Fatal error: (.*) in .* on line (\d+)',run.stderr);assert match,run.stderr
                message,line=match.groups()
                body=f'dec $case{i}() : bool\ndef $case{i}() = true\n  -- if F = $pfprepare($pfbegin(41, {checked["fixture"]}), {path}, {occurrences.node_term(node)}, $plempty(false), $expression_line({occurrences.node_term(node)}))\n  -- if F.MEMORY.COMPLETION = STATICERROR '+json.dumps(message.decode())+' '+line.decode()+'\n'
                if expression=='["abc"["1x"]=>$u[]]':
                    body+='  -- if F.FACTS = eps\n'
                if expression=='[$u[]=>"abc"["1x"]]':
                    fact_path=occurrences.path_term([('INDEX',2),('FIELD',0),('FIELD',1),('FIELD',0),('INDEX',0),('FIELD',1),('FIELD',0),('INDEX',0),('FIELD',1)])
                    body+='  -- if $pffact(F.FACTS, '+fact_path+') = (PSTRING ([98]))\n'
                fixtures.append(body);records.append({'expression':expression,'source_base64':base64.b64encode(source+OBSERVER).decode(),'ast_sha256':hashlib.sha256(json.dumps(checked['ast'],sort_keys=True).encode()).hexdigest(),'compile_error':message.decode(),'line':line.decode(),'oracle':{'command':command,'cwd':str(ROOT),'status':run.returncode,'stdout_base64':base64.b64encode(run.stdout).decode(),'stderr_base64':base64.b64encode(run.stderr).decode()},'stderr':run.stderr.decode()})
            # Internally constructed state accepts only its exact source occurrence/context.
            i=len(fixtures)
            prepare=f'$pfprepare(F_seed, {path}, {occurrences.node_term(node)}, $plempty(false), 2)'
            body=f'dec $case{i}() : bool\ndef $case{i}() = true\n  -- if F_seed = $pfbegin(41, {checked["fixture"]})\n'
            probes=[prepare.replace(path,'eps',1),prepare.replace(', 2)',', 0)'),prepare.replace(', 2)',', $(-1))'),prepare.replace('$plempty(false)','$plempty(false)[.NAMESPACE = [78]]'),prepare.replace('$plempty(false)','$plempty(false)[.CONSTANTS = [([78],[77])]]'),prepare.replace('F_seed,','F_seed[.SOURCE = F_seed.SOURCE[.OCCURRENCES = eps]],',1)]
            changed=copy.deepcopy(node);changed['meta']['startLine']={'int':'99'}
            probes.append(prepare.replace(occurrences.node_term(node),occurrences.node_term(changed)))
            for j,probe in enumerate(probes):
                body+=f'  -- if F_bad{j} = '+probe+'\n  -- if F_bad'+str(j)+'.MEMORY.COMPLETION = UNSUPPORTED "invalid constant-expression occurrence, compiler line, or unsupported namespace/import context"\n'
            body+='  -- if F_other = $pfbegin(42, '+checked['fixture']+')\n  -- if F_seed.SOURCE.ID =/= F_other.SOURCE.ID\n'
            fixtures.append(body)
            f=Path(tmp)/'test.watsup'
            f.write_text(PREFIX+'\n'.join(fixtures)+'\ndec $main() : bool\ndef $main() = true\n'+''.join(f'  -- if $case{i}()\n' for i in range(len(fixtures))))
            run=subprocess.run([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),*map(str,SPECS),str(f)],capture_output=True,text=True,timeout=120)
            if run.returncode or run.stdout.strip()!='true':
                (ROOT/'.tools/constant-failure.watsup').write_text(f.read_text());raise AssertionError((run.returncode,run.stdout,run.stderr))
            print(len(records),'source observations and 7 boundary probes passed')
    finally:frontend.close();adapter.close()
    assert before==fingerprint(),'watched inputs changed'
    report={'scope':'selected checked constant-expression invocations in explicit global context; no source compiler or runtime consumption', 'profile':types.PROFILE, 'oracle_identity':identity, 'fingerprint':before, 'source_cases':len(records), 'boundary_probes':7, 'cases':records}
    (ROOT/'coverage/semantics/constant-context.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__': main()
