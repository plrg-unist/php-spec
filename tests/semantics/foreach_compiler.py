#!/usr/bin/env python3
"""Foreach key prechecks precede iterable compilation and retain source context."""
import base64,hashlib,json,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

CASES = {
    'key-ref': b'<?php foreach([] as &$k=>$v){}',
    'key-ref-both': b'<?php foreach([] as &$k=>&$v){}',
    'key-ref-before-iterable': b'<?php foreach([[]=>1] as &$k=>$v){}',
    'key-ref-before-list-spread': b'<?php foreach([] as &$k=>[...$v]){}',
    'key-ref-dim': b'<?php foreach([] as &$k[0]=>$v){}',
    'key-list': b'<?php foreach([] as list($k)=>$v){}',
    'key-list-empty': b'<?php foreach([] as list()=>$v){}',
    'key-list-holes': b'<?php foreach([] as list(,$k,)=>$v){}',
    'key-short-list': b'<?php foreach([] as [$k]=>$v){}',
    'key-short-holes': b'<?php foreach([] as [,$k,]=>$v){}',
    'key-list-ref': b'<?php foreach([] as [&$k]=>$v){}',
    'key-list-unpack': b'<?php foreach([] as [...$k]=>$v){}',
    'key-list-before-iterable': b'<?php foreach([[]=>1] as list($k)=>$v){}',
    'key-ref-multiline': b'<?php foreach(\n[[]=>1]\nas\n&$k\n=>\n$v\n){}',
    'vendor/php-src/Zend/tests/errmsg/errmsg_042.phpt': b'<?php\n\n$a = array(1,2,3);\nforeach ($a as &$k=>$v) {\n}\n\necho "Done\\n";\n?>\n',
    'vendor/php-src/Zend/tests/foreach/foreach_list_003.phpt': b"<?php\n\n$array = [['a', 'b'], 'c', 'd'];\n\nforeach($array as list($key) => list(list(), $a)) {\n}\n\n?>\n",
    'vendor/php-src/tests/lang/foreachLoop.006.phpt': b'<?php\n$a = array("a","b","c");\nforeach ($a as &$k=>$v) {\n  var_dump($v);\n}\n?>\n',
}


def fingerprint():
    paths=[*compiler.SPECS,Path(__file__),Path(compiler.__file__),ROOT/'tests/semantics/_build/default/numeric_runner.exe']
    return {'closure':types.syntax_validation.implementation_fingerprint(),'direct':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}


def main():
    global compiler,types,context
    import source_compiler as compiler
    from source_compiler import types,context
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
    def boundary(source,target,key,value,expected):
        ast=parse(source);node=ast['program'][0]
        if target=='foreach':node['meta']={}
        elif target=='keyref':node['fields'][5]=value
        elif target=='absent-key':node['fields'][1]=None
        else:
            node=node['fields'][0] if target=='iterable' else node['fields'][1]
            if value is None:node['meta'].pop(key,None)
            else:node['meta'][key]={'int':str(value)}
        add(ast,['P.COMPLETION = '+expected]);boundaries.append({'source_base64':base64.b64encode(source).decode(),'target':target,'field':key,'value':value,'expected':expected})
    try:
        with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as tmp:
            file=(Path(tmp)/'input.php').resolve()
            for name,source in CASES.items():
                file.write_bytes(source);command=[str(types.PHP),'-n',*types.FLAGS,'-l',str(file)];lint=subprocess.run(command,capture_output=True,cwd=ROOT,env=types.ENV,timeout=10)
                checked=add(parse(source),['$pptrace(P) = '+context.expected_events(context.events(lint),file)]);records.append({'id':name,**compiler.oracle_record(source,checked,command,lint)})
            for source,message in [(b'<?php foreach(1 as &$k=>$v){}','Key element cannot be a reference'),(b'<?php foreach(1 as list($k)=>$v){}','Cannot use list as key element')]:
                for value in [None,0,-1,91]:boundary(source,'iterable','startLine',value,'PPCABRUPT (UNSUPPORTED "missing ordinary compiler line")' if value!=91 else 'PPCABRUPT (STATICERROR "'+message+'" 91)')
                boundary(source,'foreach','all',None,'PPCABRUPT (STATICERROR "'+message+'" 1)')
            for value in [None,0,-1,91]:boundary(b'<?php foreach([] as &$k=>$v){}','iterable','endLine',value,'PPCABRUPT (UNSUPPORTED "missing ordinary compiler line")' if value!=91 else 'PPCABRUPT (STATICERROR "Key element cannot be a reference" 91)')
            for field in ['kind','destructuringArrayKind','listFirstHoleLine']:
                for value in [None,0,91]:boundary(b'<?php foreach(1 as [, $k]=>$v){}','key',field,value,'PPCABRUPT (STATICERROR "Cannot use list as key element" 1)')
            boundary(b'<?php foreach(1 as [$k]=>$v){}','keyref','bool',True,'PPCABRUPT (STATICERROR "Key element cannot be a reference" 1)')
            boundary(b'<?php foreach(1 as &$k=>$v){}','keyref','bool',False,'PPCNORMAL')
            boundary(b'<?php foreach(1 as &$k=>$v){}','absent-key','key',None,'PPCABRUPT (UNSUPPORTED "reference foreach key without target")')
            script=Path(tmp)/'compiler.watsup';script.write_text(compiler.PREFIX+'\n'.join(fixtures)+'\ndec $main() : bool\ndef $main() = true\n'+''.join(f'  -- if $case{i}()\n' for i in range(len(fixtures))))
            run=subprocess.run([str(runner),*map(str,compiler.SPECS),str(script)],capture_output=True,text=True,cwd=ROOT,timeout=120)
            if run.returncode or run.stdout.strip()!='true':
                failure=Path(tempfile.mkdtemp(prefix='foreach-compiler-failure-',dir=ROOT/'.tools'))
                (failure/'compiler.watsup').write_text(script.read_text());(failure/'result.json').write_text(json.dumps({'status':run.returncode,'stdout':run.stdout,'stderr':run.stderr,'records':records,'boundaries':boundaries},indent=2)+'\n')
                raise AssertionError((str(failure),run.stdout,run.stderr))
    finally:frontend.close();adapter.close()
    assert before==fingerprint(),'foreach compiler inputs changed'
    report={'scope':'foreach key-reference/list-key source prechecks; full foreach compilation; scalar/array runtime admission gated separately','fingerprint':before,'profile':types.PROFILE,'source_cases':len(records),'boundaries':boundaries,'records':records}
    (ROOT/'coverage/semantics/foreach-compiler.json').write_text(json.dumps(report,indent=2)+'\n');print(len(records),'native key-precheck lints;',len(boundaries),'semantic metadata boundaries passed')

if __name__=='__main__':main()
