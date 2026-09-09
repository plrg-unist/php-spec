#!/usr/bin/env python3
"""Original string token lines through checked compilation and source execution."""
import base64, copy, hashlib, json, signal, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tests/semantics'))
import source_compiler as compiler, static_types as types
LITERALS=[b'"a\nb"',b'<<<TXT\na\nb\nTXT',b"<<<'TXT'\na\nb\nTXT",b'<<<TXT\nTXT',b"<<<'TXT'\nTXT",b'<<<TXT\n  a\n  b\n  TXT',b'<<<TXT\n\nTXT',b'<<<TXT\r\na\r\nb\r\nTXT',b'b<<<TXT\na\nTXT',b"'a\nb'",b"<<<'TXT'\n    a\n    TXT",b"<<<'TXT'\r\nTXT"]
CASES=[(b'<?php $u=1;\necho [\n$u,\n'+literal+b'\n];',{}) for literal in LITERALS]
TEXT='<?php $u=1;\necho [\n$u,\n<<<TXT\na\nb\nTXT\n];'
CASES += [(b'\xff\xfe'+TEXT.encode('utf-16le'),{'zend.multibyte':'1','internal_encoding':'UTF-8'}),(TEXT.replace('a\nb','\xff\nb').encode('latin1'),{'zend.multibyte':'1','internal_encoding':'UTF-8','zend.script_encoding':'ISO-8859-1'})]

def main():
    def expired(signum,frame):raise TimeoutError('string line worker exceeded30seconds')
    signal.signal(signal.SIGALRM,expired)
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'),'dune','build','--root',str(types.HERE),'numeric_runner.exe'],cwd=ROOT,check=True,timeout=120)
    runner=ROOT/'tests/semantics/_build/default/numeric_runner.exe'
    def fingerprint():return {'closure':types.syntax_validation.implementation_fingerprint(),'direct':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in compiler.SPECS+[Path(__file__),runner,ROOT/'vendor/php-src/Zend/zend_language_parser.y',ROOT/'vendor/php-src/Zend/zend_language_scanner.l']}}
    identity=json.loads(subprocess.run([str(types.PHP),'-n',*types.FLAGS,'-r','echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,ini_get_all(null,false)]);'],capture_output=True,text=True,cwd=ROOT,env=types.ENV,timeout=10,check=True).stdout)
    assert identity[:4]==['8.5.10','cli',8,False] and all(identity[4][k]==v for k,v in types.PROFILE.items())
    before=fingerprint();records=[];fixtures=[];adapter=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    try:
        with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as tmp:
            file=Path(tmp)/'source.php'
            for i,(source,ini) in enumerate(CASES):
                flags=[v for k,value in ini.items() for v in ['-d',k+'='+value]]
                frontend=types.Worker([str(types.PHP),'-n',*flags,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')])
                try:
                    parsed=frontend.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                    checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
                finally:frontend.close()
                file.write_bytes(source);command=[str(types.PHP),'-n',*types.FLAGS,*flags,str(file)]
                run=subprocess.run(command,capture_output=True,cwd=ROOT,env=types.ENV,timeout=10);assert run.returncode==0
                events=compiler.context.events(run);assert len(events)==1,(source,run.stderr)
                line=events[0][2]
                fixtures.append(f'dec $case{i}() : bool\ndef $case{i}() = true\n  -- if P = $ppstart(1, {checked["fixture"]}, ([120]))\n  -- if P.COMPLETION = PPCNORMAL\n  -- if P.LOCATION.LINE = {line}\n')
                record={'id':i,'ini':ini,'oracle':compiler.oracle_record(source,checked,command,run),'expected_line':line}
                if not ini:
                    command=[str(ROOT/'bin/php-semantics'),str(file)]
                    result=subprocess.run(command,capture_output=True,cwd=ROOT,env=types.ENV,timeout=30);assert result.returncode==0,(result.stdout,result.stderr)
                    obs=json.loads(result.stdout);assert obs['status']=='normal',obs
                    assert base64.b64decode(obs['stdout'])==run.stdout and base64.b64decode(obs['stderr'])==run.stderr and obs['exit_status']==run.returncode,(source,obs,run.stderr)
                    record['runtime']={'command':command,'cwd':str(ROOT),'status':result.returncode,'stdout_base64':base64.b64encode(result.stdout).decode(),'stderr_base64':base64.b64encode(result.stderr).decode()}
                records.append(record)
            # Kind absence is distinguishable from an explicitly invalid kind.
            meta=copy.deepcopy(checked['ast']['program'][1]['fields'][0][0]['fields'][0][1]['fields'][1]['meta'])
            mutations=[('missing-kind',{'kind':None},0),('invalid-kind',{'kind':{'int':'9'}},0),('zero-kind',{'kind':{'int':'0'}},0),('negative-kind',{'kind':{'int':'-1'}},0),('missing-start',{'startLine':None},0),('zero-start',{'startLine':{'int':'0'}},0),('absent-single-line',{'kind':None,'endLine':{'int':'4'}},4)]
            for label,patch,expected in mutations:
                edited=copy.deepcopy(meta)
                for key,value in patch.items():
                    if value is None:edited.pop(key,None)
                    else:edited[key]=value
                node={'node':'Scalar_String','fields':[{'bytes':'YQ=='}],'meta':edited}
                edited_ast=copy.deepcopy(checked['ast']);edited_ast['program'][1]['fields'][0][0]['fields'][0][1]['fields'][1]=node
                edited_checked=adapter.request({'op':'check','ast':edited_ast,'fixture':True});i=len(fixtures)
                expectation='  -- if P.COMPLETION = PPCABRUPT (UNSUPPORTED "missing ordinary compiler line")\n' if expected==0 else f'  -- if P.COMPLETION = PPCNORMAL\n  -- if P.LOCATION.LINE = {expected}\n'
                fixtures.append(f'dec $case{i}() : bool\ndef $case{i}() = true\n  -- if P = $ppstart(1, {edited_checked["fixture"]}, ([120]))\n'+expectation)
            helper=Path(tmp)/'lines.watsup';helper.write_text('\n'.join(fixtures)+'\ndec $main() : bool\ndef $main() = true\n'+''.join(f'  -- if $case{i}()\n' for i in range(len(fixtures))))
            command=[str(runner),*map(str,compiler.SPECS),str(helper)];result=subprocess.run(command,capture_output=True,cwd=ROOT,timeout=60)
            if result.returncode or result.stdout.strip()!=b'true':
                (ROOT/'.tools/string-lines-failure.watsup').write_text(helper.read_text());raise AssertionError((result.stdout,result.stderr))
            assert before==fingerprint(),'watched inputs changed'
            report={'scope':'original string compiler lines;12 full source comparisons and2 encoding-profile compiler comparisons','fingerprint':before,'profile':types.PROFILE,'oracle_identity':identity,'cases':records,'edited_metadata':mutations,'helper':{'command':command,'cwd':str(ROOT),'status':result.returncode,'stdout_base64':base64.b64encode(result.stdout).decode(),'stderr_base64':base64.b64encode(result.stderr).decode()}}
            (ROOT/'coverage/semantics/string-lines.json').write_text(json.dumps(report,indent=2)+'\n')
            print('12 source comparisons;2 encoding compiler comparisons;7 metadata boundaries passed')
    finally:adapter.close()
if __name__=='__main__':main()
