#!/usr/bin/env python3
"""Array unpack compiler phases, source paths and required operand metadata."""
import base64, copy, hashlib, json, subprocess, tempfile
from pathlib import Path
import array_unpack, source_compiler as compiler
from source_compiler import ROOT, types, context

CASES={name:source for name,source in array_unpack.CASES.items() if name.startswith('unpack-compiler-')}
PREFIX=compiler.PREFIX+'''
dec $unpack_record(ppexprdone*, pcpath) : ppexprdone?
def $unpack_record(eps, pcpath) = eps
def $unpack_record((PPCEXPR pcpath n pvalue?) :: ppexprdone*, pcpath) = (PPCEXPR pcpath n pvalue?)
def $unpack_record((PPCEXPR pcpath_other n pvalue?) :: ppexprdone*, pcpath) = $unpack_record(ppexprdone*, pcpath)
  -- if pcpath_other =/= pcpath
'''


def fingerprint():
    paths=[*compiler.SPECS,Path(__file__),Path(array_unpack.__file__),Path(compiler.__file__),ROOT/'tests/semantics/_build/default/numeric_runner.exe']
    return {'closure':types.syntax_validation.implementation_fingerprint(),
            'direct':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}


def main():
    before=fingerprint();runner=ROOT/'tests/semantics/_build/default/numeric_runner.exe'
    frontend=types.Worker([str(types.PHP),'-n','-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')])
    adapter=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    fixtures=[];records=[];boundaries=[]
    def parse(source):
        result=frontend.request({'op':'parse','source':base64.b64encode(source).decode()});assert result['accepted'],result
        return result['ast']
    def add(name,ast,checks):
        checked=adapter.request({'op':'check','ast':ast,'fixture':True});assert checked['ok'],checked
        index=len(fixtures);fixtures.append(f'dec $case{index}() : bool\ndef $case{index}() = true\n  -- if P = $ppstart(91, '+checked['fixture']+', '+types.byte_expr(str(file))+')\n'+''.join('  -- if '+check+'\n' for check in checks))
        return checked
    try:
        with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as tmp:
            file=(Path(tmp)/'input.php').resolve()
            for name,source in CASES.items():
                file.write_bytes(source);command=[str(types.PHP),'-n',*types.FLAGS,'-l',str(file)]
                lint=subprocess.run(command,capture_output=True,cwd=ROOT,env=types.ENV,timeout=10)
                checks=['$pptrace(P) = '+context.expected_events(context.events(lint),file)]
                if lint.returncode==0:checks.append('P.COMPLETION = PPCNORMAL')
                checked=add(name,parse(source),checks)
                records.append({'id':name,**compiler.oracle_record(source,checked,command,lint)})
            def boundary(name,ast,checks):
                add(name,ast,checks);boundaries.append({'id':name,'checks':checks,'ast_sha256':hashlib.sha256(json.dumps(ast,sort_keys=True).encode()).hexdigest()})
            path='([PCINDEX 0, PCFIELD 0, PCFIELD 1, PCFIELD 0, PCINDEX 1, PCFIELD 1])'
            sibling='([PCINDEX 0, PCFIELD 0, PCFIELD 1, PCFIELD 0, PCINDEX 2, PCFIELD 1])'
            original=parse(b'<?php $a=[1,...$x,$y];')
            boundary('original-item-indices',original,['P.COMPLETION = PPCNORMAL','$ppaccess(P, '+path+') = (PPR)','$ppaccess(P, '+sibling+') = (PPR)','$unpack_record(P.EXPRESSIONS, '+path+') = (PPCEXPR '+path+' 1 eps)'])
            for value in [None,0,-1,91]:
                ast=copy.deepcopy(original);operand=ast['program'][0]['fields'][0]['fields'][1]['fields'][0][1]['fields'][1]
                if value is None:operand['meta'].pop('startLine')
                else:operand['meta']['startLine']={'int':str(value)}
                checks=['P.COMPLETION = PPCABRUPT (UNSUPPORTED "missing ordinary compiler line")'] if value!=91 else ['P.COMPLETION = PPCNORMAL','$unpack_record(P.EXPRESSIONS, '+path+') = (PPCEXPR '+path+' 91 eps)']
                boundary('operand-line-'+str(value),ast,checks)
            for kind in ['key','reference']:
                ast=parse(b'<?php $a=[...$x];');item=ast['program'][0]['fields'][0]['fields'][1]['fields'][0][0]
                if kind=='reference':item['fields'][2]=True
                else:item['fields'][0]=parse(b'<?php 1;')['program'][0]['fields'][0]
                boundary('edited-spread-'+kind,ast,['P.COMPLETION = PPCABRUPT (UNSUPPORTED "constant array unpack or edited item")'])
            root='([PCINDEX 0, PCFIELD 0, PCFIELD 1])';child='([PCINDEX 0, PCFIELD 0, PCFIELD 1, PCFIELD 0, PCINDEX 0, PCFIELD 1])'
            boundary('constant-pool-occurrences',parse(b'<?php $a=[...[7,8]];'),['P.COMPLETION = PPCNORMAL','$pffact(P.FOLD.FACTS, '+root+') = (PARRAY n_root)','$pffact(P.FOLD.FACTS, '+child+') = (PARRAY n_child)','n_root =/= n_child'])
            for name,source in [('overflow',b'<?php $a=[9223372036854775807=>1,...[2]];'),('dynamic-scalar',b'<?php $a=[...1,$x];')]:
                boundary('defer-'+name,parse(source),['P.COMPLETION = PPCNORMAL','$pffact(P.FOLD.FACTS, '+root+') = eps'])
            script=Path(tmp)/'compiler.watsup';script.write_text(PREFIX+'\n'.join(fixtures)+'\ndec $main() : bool\ndef $main() = true\n'+''.join(f'  -- if $case{i}()\n' for i in range(len(fixtures))))
            run=subprocess.run([str(runner),*map(str,compiler.SPECS),str(script)],capture_output=True,text=True,cwd=ROOT,timeout=120)
            if run.returncode or run.stdout.strip()!='true':
                failure=Path(tempfile.mkdtemp(prefix='array-unpack-compiler-failure-',dir=ROOT/'.tools'))
                (failure/'compiler.watsup').write_text(script.read_text());(failure/'result.json').write_text(json.dumps({'status':run.returncode,'stdout':run.stdout,'stderr':run.stderr,'records':records,'boundaries':boundaries},indent=2)+'\n')
                raise AssertionError((str(failure),run.stdout,run.stderr))
    finally:
        frontend.close();adapter.close()
    assert before==fingerprint(),'unpack compiler inputs changed'
    report={'scope':'array unpack native compiler phases and checked operand descriptors; runtime evidence separate','fingerprint':before,'profile':types.PROFILE,'source_cases':len(records),'boundaries':boundaries,'records':records}
    (ROOT/'coverage/semantics/array-unpack-compiler.json').write_text(json.dumps(report,indent=2)+'\n')
    print(len(records),'native lint comparisons;',len(boundaries),'descriptor and metadata controls passed')

if __name__=='__main__':main()
