#!/usr/bin/env python3
"""Execute-only source filename transport, including byte-preserving paths."""
import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tests/semantics'))
import static_types as types


def main():
    def fingerprint(): return types.syntax_validation.implementation_fingerprint()
    before = fingerprint()
    source = b'<?php echo $missing;'
    frontend = types.Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension='+str(ROOT/'.tools/php-file.so'), str(ROOT/'frontend/worker.php')])
    adapter = types.Worker([str(ROOT/'_build/default/adapter/main.exe'), str(ROOT)])
    records = []
    try:
        parsed = frontend.request({'op':'parse','source':base64.b64encode(source).decode()})
        assert parsed['accepted'], parsed
        checked = adapter.request({'op':'check','ast':parsed['ast']})
        assert checked.get('ok') and checked['ast'] == parsed['ast'], checked
        for filename in (b'/tmp/source.php', b'/tmp/space and \xff\x80.php', b'input.php'):
            for budget in (0,100):
                request = {'op':'execute','ast':parsed['ast'],'steps':budget,'filename':base64.b64encode(filename).decode()}
                response = adapter.request(request)
                assert response.get('ok'), response
                state = response['state']
                assert state['FILES'] == [{'tag':'SOURCEFILE','args':['0',list(map(str,filename))]}], state['FILES']
                assert state['COMPLETION']['tag'] == ('BUDGET' if budget == 0 else 'NORMAL'), response
                assert state['SOURCES'][0]['ID'] == '0'
                records.append({'input':request,'response':response})
        for filename in (b'',b'/tmp/a\0b.php'):
            request = {'op':'execute','ast':parsed['ast'],'steps':100,'filename':base64.b64encode(filename).decode()}
            response = adapter.request(request)
            assert response.get('ok') and response['state']['COMPLETION'] == {'tag':'UNSUPPORTED','args':['invalid source filename']}, response
            records.append({'input':request,'response':response})
        for filename in (None, 42, '!', 'AA', 'AB==', 'A===', 'é==='):
            request = {'op':'execute','ast':parsed['ast'],'steps':100}
            if filename is not None: request['filename'] = filename
            run = subprocess.run([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],
                input=types.wire.dumps(request)+'\n',capture_output=True,text=True,timeout=30)
            assert run.returncode == 0, run.stderr
            response = types.wire.loads(run.stdout)
            assert not response.get('ok') and response['category'] == 'runner_failure', response
            records.append({'input':request,'response':response})
    finally: frontend.close(); adapter.close()
    # A real non-UTF8 path passes through the CLI, adapter, and diagnostic formatter.
    with tempfile.TemporaryDirectory(prefix='execute-context-',dir=ROOT/'.tools') as tmp:
        file = Path(tmp)/os.fsdecode(b'byte \xff.php')
        file.write_bytes(source)
        native = subprocess.run([str(types.PHP),'-n',*types.FLAGS,str(file)],capture_output=True,timeout=30,env=types.ENV,cwd=tmp)
        run = subprocess.run([str(ROOT/'bin/php-semantics'),str(file)],capture_output=True,timeout=35,env=types.ENV,cwd=tmp)
        response = json.loads(run.stdout)
        assert run.returncode == 0 and response['status'] == 'normal', response
        assert base64.b64decode(response['stdout']) == native.stdout
        assert base64.b64decode(response['stderr']) == native.stderr
        assert response['exit_status'] == native.returncode
        records.append({'filename_base64':base64.b64encode(os.fsencode(file)).decode(),
            'native_command':native.args,'semantic_command':run.args,'cwd':tmp,
            'profile':types.PROFILE,'environment':{'LC_ALL':'C','TZ':'UTC','PHP_SPEC_SCRIPT_ENCODING':None},
            'semantic_stdout_base64':base64.b64encode(run.stdout).decode(),
            'semantic_stderr_base64':base64.b64encode(run.stderr).decode(),
            'semantic_exit_status':run.returncode,
            'native_stdout_base64':base64.b64encode(native.stdout).decode(),
            'native_stderr_base64':base64.b64encode(native.stderr).decode(),
            'native_exit_status':native.returncode,'response':response})
    assert before == fingerprint(), 'implementation changed during execute context validation'
    report = {'result':'pass','classification':'source filename transport; file-sensitive PHP constructs remain pending',
        'cases':len(records),'source_base64':base64.b64encode(source).decode(),'records':records,'fingerprint':before}
    (ROOT/'coverage/semantics/execute-context.json').write_text(json.dumps(report,indent=2)+'\n')
    print({'result':'pass','cases':len(records)})


if __name__ == '__main__': main()
