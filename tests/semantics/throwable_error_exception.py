#!/usr/bin/env python3
"""Original-source differentials for the distinct ErrorException constructor."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ('default', '<?php $e=new ErrorException;echo $e->getMessage(),"|",$e->getCode(),"|",$e->getSeverity(),"|",$e->getFile()===__FILE__,"|",$e->getLine(),"|",$e->getPrevious()===null;', 'agreement'),
    ('filename-line', '<?php $a=new ErrorException("m",3,5,"f.php");$b=new ErrorException("m",3,5,null,9);echo $a->getFile(),"|",$a->getLine(),"|",$b->getFile()===__FILE__,"|",$b->getLine();', 'agreement'),
    ('empty-filename', '<?php $e=new ErrorException("m",3,5,filename:"",line:null);echo $e->getFile()==="","|",$e->getLine();', 'agreement'),
    ('negative-line', '<?php $e=new ErrorException("m",3,5,"f.php",-7);echo $e->getFile(),"|",$e->getLine();', 'agreement'),
    ('named-order', '<?php $p=new Exception("p");$e=new ErrorException(previous:$p,line:7,filename:"f.php",severity:8,code:9,message:"m");echo $e->getMessage(),"|",$e->getCode(),"|",$e->getSeverity(),"|",$e->getFile(),"|",$e->getLine(),"|",$e->getPrevious()===$p;', 'agreement'),
    ('reentry-default', '<?php $e=new ErrorException("m",3,4,"f.php",8);$e->__construct();echo $e->getMessage(),"|",$e->getCode(),"|",$e->getSeverity(),"|",$e->getFile(),"|",$e->getLine();', 'agreement'),
    ('reentry-filename', '<?php $e=new ErrorException("m",3,4,"old.php",8);$e->__construct(severity:5,filename:"new.php");echo $e->getMessage(),"|",$e->getCode(),"|",$e->getSeverity(),"|",$e->getFile(),"|",$e->getLine();', 'agreement'),
    ('reentry-trace', '<?php function f(){ $e=new ErrorException("m",3,4);$before=$e->getTrace();$e->__construct("new",5,6,"f.php",7);$after=$e->getTrace();echo $before===$after,"|",$after[0]["function"],"|",$e->getFile(),"|",$e->getLine();}f();', 'agreement'),
    ('validation-atomic', '<?php $e=new ErrorException("old",3,4,"old.php",8);try{$e->__construct("new",9,[],"new.php",7);}catch(TypeError $x){echo "caught|";}echo $e->getMessage(),"|",$e->getCode(),"|",$e->getSeverity(),"|",$e->getFile(),"|",$e->getLine();', 'agreement'),
    ('severity-arity', '<?php $e=new ErrorException("m",0,9);echo $e->getSeverity(),"|",$e->GETSEVERITY(),"|";function tick(){echo "T";return 1;}try{$e->getSeverity(tick());}catch(ArgumentCountError $x){echo "|",$x->getMessage();}', 'agreement'),
    ('constructor-arity', '<?php try{new ErrorException("m",0,1,null,null,null,7);}catch(ArgumentCountError $e){echo $e->getMessage();}', 'agreement'),
    ('getter-arity', '<?php $e=new ErrorException;try{$e->getSeverity(1);}catch(ArgumentCountError $x){echo $x->getMessage();}', 'agreement'),
    ('cast-layout-control', '<?php $e=new ErrorException;foreach((array)$e as $key=>$value){echo bin2hex($key),",";}', 'unsupported'),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    watched = [*modules, 'spec/semantics/modules.json', 'bin/php-semantics',
               'frontend/worker.php', 'frontend/wire.php', '.tools/php-file.so',
               'tests/semantics/profile.json', 'tests/semantics/throwable_error_exception.py',
               '.tools/php/bin/php', '_build/default/adapter/main.exe']
    before = {name: digest(ROOT / name) for name in watched}
    out = Path(tempfile.mkdtemp(prefix='error-exception-probes-', dir=ROOT / '.tools'))
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    env = dict(os.environ, LC_ALL='C', TZ='UTC')
    rows = []
    for case_id, source_text, kind in CASES:
        directory = out / case_id
        directory.mkdir()
        source = directory / 'source.php'
        source.write_bytes(source_text.encode())
        native = subprocess.run([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)],
                                cwd=directory, env=env, capture_output=True, timeout=65)
        model = subprocess.run([str(ROOT / 'bin/php-semantics'), str(source), '--timeout', '60'],
                               cwd=directory, env=env, capture_output=True, timeout=65)
        (directory / 'native.stdout').write_bytes(native.stdout)
        (directory / 'native.stderr').write_bytes(native.stderr)
        (directory / 'model.stdout').write_bytes(model.stdout)
        (directory / 'model.stderr').write_bytes(model.stderr)
        actual = json.loads(model.stdout)
        expected = {'stdout': base64.b64encode(native.stdout).decode(),
                    'stderr': base64.b64encode(native.stderr).decode(), 'exit_status': native.returncode}
        passed = (model.returncode == 0 and not model.stderr and
                  all(actual.get(key) == value for key, value in expected.items())) if kind == 'agreement' else (
                      model.returncode == 1 and not model.stderr and actual.get('status') == 'unsupported')
        rows.append({'id': case_id, 'kind': kind, 'pass': passed,
                     'source_sha256': digest(source), 'actual': actual, 'native': expected})
        print(case_id, passed, actual.get('status'), flush=True)
    assert before == {name: digest(ROOT / name) for name in watched}, 'inputs changed'
    report = {'result': 'pass' if all(row['pass'] for row in rows) else 'fail',
              'agreements': sum(row['kind'] == 'agreement' for row in rows),
              'unsupported_controls': sum(row['kind'] == 'unsupported' for row in rows),
              'inputs': before, 'profile': profile, 'records': rows, 'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    assert report['result'] == 'pass'


if __name__ == '__main__':
    main()
