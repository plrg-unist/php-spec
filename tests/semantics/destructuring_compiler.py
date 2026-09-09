#!/usr/bin/env python3
"""Destructuring compiler order, effectful results and checked list metadata."""
import base64, hashlib, json, subprocess, tempfile
from pathlib import Path
import source_compiler as compiler
from source_compiler import ROOT, types, context

ARCHIVES={
    'list-compiler-line-originals.json':set(),
    'list-rhs-line-originals.json':set(),
    'list-effectful-result-originals.json':set(),
    'list-spread-originals.json':set(),
    'list-static-sweep-originals.json':{'target-dim-call','ref-call','ref-whole-list'},
    'coalesce-source-originals.json':{'quiet-property','quiet-nullsafe','quiet-static-property'},
}
# The retained call and object-access boundaries remain assigned in QUIET-CV-HANDOFF.
CASES={}
for archive,excluded in ARCHIVES.items():
    data=json.loads((ROOT/'coverage/semantics'/archive).read_text())
    for row in data if isinstance(data,list) else data['records']:
        if row['id'] not in excluded:
            CASES[archive+'/'+row['id']]=base64.b64decode(row['source_base64'])


def fingerprint():
    paths=[*compiler.SPECS,Path(__file__),Path(compiler.__file__),ROOT/'tests/semantics/_build/default/numeric_runner.exe']+[ROOT/'coverage/semantics'/name for name in ARCHIVES]
    return {'closure':types.syntax_validation.implementation_fingerprint(),
            'direct':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}


def lists(value):
    if isinstance(value,list):
        for child in value:yield from lists(child)
    elif isinstance(value,dict):
        if value.get('node')=='Expr_List':yield value
        for child in value.get('fields',[]):yield from lists(child)


def main():
    before=fingerprint();runner=ROOT/'tests/semantics/_build/default/numeric_runner.exe'
    frontend=types.Worker([str(types.PHP),'-n','-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')])
    adapter=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    fixtures=[];records=[];boundaries=[]
    def parse(source):
        result=frontend.request({'op':'parse','source':base64.b64encode(source).decode()});assert result['accepted'],result
        return result['ast']
    def add(ast,checks):
        checked=adapter.request({'op':'check','ast':ast,'fixture':True});assert checked['ok'],checked
        index=len(fixtures);fixtures.append(f'dec $case{index}() : bool\ndef $case{index}() = true\n  -- if P = $ppstart(91, '+checked['fixture']+', '+types.byte_expr(str(file))+')\n'+''.join('  -- if '+check+'\n' for check in checks));return checked
    def boundary(source,index,key,value,expected):
        ast=parse(source);target=list(lists(ast['program']))[index]
        if value is None:target['meta'].pop(key,None)
        else:target['meta'][key]={'int':str(value)}
        add(ast,['P.COMPLETION = '+expected]);boundaries.append({'source_base64':base64.b64encode(source).decode(),'list_index':index,'field':key,'value':value,'expected':expected})
    try:
        with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as tmp:
            file=(Path(tmp)/'input.php').resolve()
            for name,source in CASES.items():
                file.write_bytes(source);command=[str(types.PHP),'-n',*types.FLAGS,'-l',str(file)]
                lint=subprocess.run(command,capture_output=True,cwd=ROOT,env=types.ENV,timeout=10)
                checks=['$pptrace(P) = '+context.expected_events(context.events(lint),file)]
                if lint.returncode==0:checks.extend(['P.COMPLETION = PPCNORMAL','$access_paths(P.ACCESS) = $expression_paths(P.EXPRESSIONS)'])
                checked=add(parse(source),checks);records.append({'id':name,**compiler.oracle_record(source,checked,command,lint)})
            for source in [b'<?php [,&$x]=[];',b'<?php list(,&$x)=[];']:
                for value in [None,0,-1,91]:boundary(source,0,'listFirstHoleLine',value,'PPCABRUPT (UNSUPPORTED "missing ordinary compiler line")' if value!=91 else 'PPCABRUPT (STATICERROR "Cannot assign reference to non referenceable value" 91)')
            for value in [None,0,-1,91]:
                boundary(b'<?php list()=[];',0,'listFirstHoleLine',value,'PPCABRUPT (STATICERROR "Cannot use empty list" 1)')
                boundary(b'<?php list()=[];',0,'endLine',value,'PPCABRUPT (UNSUPPORTED "missing ordinary compiler line")' if value!=91 else 'PPCABRUPT (STATICERROR "Cannot use empty list" 1)')
            for field in ['kind','destructuringArrayKind']:
                for value in [None,0,-1,91]:boundary(b'<?php [$x]=[];',0,field,value,'PPCABRUPT (UNSUPPORTED "missing list syntax context")')
            for value in [None,0,-1,91]:boundary(b'<?php [[$x]]=[];',1,'destructuringArrayKind',value,'PPCABRUPT (UNSUPPORTED "missing list syntax context")')
            boundary(b'<?php [[$x]]=[];',1,'destructuringArrayKind',1,'PPCABRUPT (STATICERROR "Cannot assign to array(), use [] instead" 1)')
            boundary(b'<?php [[$x]]=[];',1,'kind',1,'PPCABRUPT (STATICERROR "Cannot mix [] and list()" 1)')
            for value in [None,91]:boundary(b'<?php [$x]=[[]=>1];',0,'destructuringArrayKind',value,'PPCABRUPT (STATICERROR "Illegal offset type" 1)')
            script=Path(tmp)/'compiler.watsup';script.write_text(compiler.PREFIX+'\n'.join(fixtures)+'\ndec $main() : bool\ndef $main() = true\n'+''.join(f'  -- if $case{i}()\n' for i in range(len(fixtures))))
            run=subprocess.run([str(runner),*map(str,compiler.SPECS),str(script)],capture_output=True,text=True,cwd=ROOT,timeout=180)
            if run.returncode or run.stdout.strip()!='true':
                failure=Path(tempfile.mkdtemp(prefix='destructuring-compiler-failure-',dir=ROOT/'.tools'))
                (failure/'compiler.watsup').write_text(script.read_text());(failure/'result.json').write_text(json.dumps({'status':run.returncode,'stdout':run.stdout,'stderr':run.stderr,'records':records,'boundaries':boundaries},indent=2)+'\n')
                raise AssertionError((str(failure),run.stdout,run.stderr))
    finally:
        frontend.close();adapter.close()
    assert before==fingerprint(),'destructuring compiler inputs changed'
    report={'scope':'destructuring/list and variable/coalesce compiler checks; pending calls and object access tracked separately','fingerprint':before,'profile':types.PROFILE,'source_cases':len(records),'boundaries':boundaries,'records':records}
    (ROOT/'coverage/semantics/destructuring-compiler.json').write_text(json.dumps(report,indent=2)+'\n')
    print(len(records),'native lint comparisons;',len(boundaries),'list metadata controls passed')

if __name__=='__main__':main()
