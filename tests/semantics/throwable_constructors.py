#!/usr/bin/env python3
"""Pinned-PHP source differentials for finite Throwable constructors."""
from pathlib import Path
import base64
import hashlib
import json
import os
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]

CASES = [
    ('default-exception', '<?php $e=new Exception;echo "[",$e->getMessage(),"]|",$e->getCode(),"|",$e->getLine(),"|",$e->getPrevious()===null;', 'agreement'),
    ('default-error', '<?php $e=new Error;echo "[",$e->getMessage(),"]|",$e->getCode(),"|",$e->getLine(),"|",$e->getPrevious()===null;', 'agreement'),
    ('positional', '<?php $e=new Exception("M",7);echo $e->getMessage(),"|",$e->getCode(),"|",$e->getLine();', 'agreement'),
    ('explicit-chain', '<?php $p=new Error("P",9);$e=new Exception("M",7,$p);echo $e->getMessage(),"|",$e->getCode(),"|",$e->getPrevious()===$p;', 'agreement'),
    ('named-unpack', '<?php $p=new Error("P");$a=["previous"=>$p,"code"=>7,"message"=>"M"];$e=new Exception(...$a);echo $e->getMessage(),"|",$e->getCode(),"|",$e->getPrevious()===$p;', 'agreement'),
    ('reentry-omitted', '<?php $p=new Error("P",9);$e=new Exception("old",7,$p);$f=$e->getFile();$l=$e->getLine();$e->__construct();echo $e->getMessage(),"|",$e->getCode(),"|",$e->getPrevious()===$p,"|",$e->getFile()===$f,"|",$e->getLine()===$l;', 'agreement'),
    ('reentry-zero-null', '<?php $p=new Error("P",9);$e=new Exception("old",7,$p);$e->__construct("",0,null);echo "[",$e->getMessage(),"]|",$e->getCode(),"|",$e->getPrevious()===$p;', 'agreement'),
    ('reentry-named-code', '<?php $e=new Exception("old",7);$e->__construct(code:8);echo "[",$e->getMessage(),"]|",$e->getCode();', 'agreement'),
    ('reentry-named-previous-null', '<?php $p=new Error("P");$e=new Exception("old",7,$p);$e->__construct(previous:null);echo "[",$e->getMessage(),"]|",$e->getCode(),"|",$e->getPrevious()===$p;', 'agreement'),
    ('reentry-message-null', '<?php $e=new Exception("old",7);$e->__construct(null);echo "[",$e->getMessage(),"]|",$e->getCode();', 'agreement'),
    ('reentry-code-null', '<?php $e=new Error("old",9);$e->__construct(code:null);echo "[",$e->getMessage(),"]|",$e->getCode();', 'agreement'),
    ('generated-reentry', '<?php try{1/0;}catch(Error $e){$f=$e->getFile();$l=$e->getLine();$e->__construct("changed",4);echo $e->getMessage(),"|",$e->getCode(),"|",$e->getFile()===$f,"|",$e->getLine()===$l;}', 'agreement'),
    ('self-previous', '<?php $e=new Exception("self");$e->__construct("self",0,$e);echo $e->getPrevious()===$e,"|",$e->getMessage();', 'agreement'),
    ('cycle-two', '<?php $a=new Error("a");$b=new Exception("b");$a->__construct(previous:$b);$b->__construct(previous:$a);echo $a->getPrevious()===$b,"|",$b->getPrevious()===$a;', 'agreement'),
    ('uncaught-self-cycle', '<?php $e=new Exception("self");$e->__construct(previous:$e);throw $e;', 'agreement'),
    ('uncaught-two-cycle', '<?php $a=new Error("a");$b=new Exception("b");$a->__construct(previous:$b);$b->__construct(previous:$a);throw $a;', 'agreement'),
    ('rethrow-constructed', '<?php $e=new Exception("x",7);try{throw $e;}catch(Exception $x){echo $x===$e,"|",$x->getFile()===$e->getFile(),"|",$x->getLine()===$e->getLine();}', 'agreement'),
    ('uncaught-constructed', '<?php throw new Exception("E");', 'agreement'),
    ('uncaught-parseerror', '<?php throw new ParseError("M");', 'agreement'),
    ('uncaught-compileerror', '<?php throw new CompileError("M");', 'agreement'),
    ('uncaught-exception-control', '<?php throw new Exception("M");', 'agreement'),
    ('typeerror-inherited', '<?php $e=new TypeError("T",5);echo $e->getMessage(),"|",$e->getCode(),"|",$e instanceof Error;', 'agreement'),
    ('parseerror-inherited', '<?php $e=new ParseError("P",8);echo $e->getMessage(),"|",$e->getCode(),"|",$e instanceof CompileError;', 'agreement'),
    ('inherited-owner-error', '<?php try{new ParseError([]);}catch(TypeError $e){echo $e->getMessage();}', 'agreement'),
    ('weak-message-int', '<?php $e=new Exception(message:42);echo $e->getMessage();', 'agreement'),
    ('strict-message-int', '<?php declare(strict_types=1);try{new Exception(message:42);}catch(TypeError $e){echo $e->getMessage();}', 'agreement'),
    ('bad-message-type', '<?php try{new Exception([],1);}catch(TypeError $e){echo $e->getMessage();}', 'agreement'),
    ('bad-previous-type', '<?php try{new Error("x",1,new stdClass);}catch(TypeError $e){echo $e->getMessage();}', 'agreement'),
    ('invalid-previous-atomic', '<?php $p=new Error("P");$e=new Exception("old",7,$p);try{$e->__construct("new",8,new stdClass);}catch(TypeError $x){echo $e->getMessage(),"|",$e->getCode(),"|",$e->getPrevious()===$p,"|",$x->getMessage();}', 'agreement'),
    ('arity-side-effects', '<?php function v($x){echo $x;return $x;}try{new Exception(v("A"),v("B"),v("C"),v("D"));}catch(ArgumentCountError $e){echo "|",$e->getMessage();}', 'agreement'),
    ('type-side-effects', '<?php function v($x){echo "V";return $x;}try{new Exception(v([]),v(1));}catch(TypeError $e){echo "|",$e->getMessage();}', 'agreement'),
    ('named-unknown-side-effect', '<?php function v(){echo "V";return 1;}try{new Exception(bad:v());}catch(Error $e){echo "|",$e->getMessage();}', 'agreement'),
    ('receiver-rebind', '<?php try{1/0;}catch(Error $e){}echo $e->__construct($e=5)===null;', 'agreement'),
    ('sent-object-rebind', '<?php $p=new Error("P");function kill(&$x){$x=null;return 0;}$e=new Exception(previous:$p,code:kill($p));echo $e->getPrevious()->getMessage(),"|",$p===null;', 'agreement'),
    ('method-null-return', '<?php $e=new Exception("old");$r=$e->__construct("new");echo $r===null,"|",$e->getMessage();', 'agreement'),
    ('trace-allocated', '<?php $e=new Exception("x");$e->getTrace();', 'agreement'),
    ('string-render', '<?php $e=new Exception("x");$e->__toString();', 'agreement'),
    ('errorexception-override', '<?php new ErrorException("x",1,2,"f",3);', 'unsupported'),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    watched = [*modules, 'spec/semantics/modules.json', 'bin/php-semantics',
               'frontend/worker.php', 'frontend/wire.php', '.tools/php-file.so',
               'tests/semantics/profile.json', 'tests/semantics/throwable_constructors.py',
               '.tools/php/bin/php', '_build/default/adapter/main.exe']
    before = {name: digest(ROOT / name) for name in watched}
    out = Path(tempfile.mkdtemp(prefix='ctor-probes-', dir=ROOT / '.tools'))
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    env = dict(os.environ, LC_ALL='C', TZ='UTC')
    rows = []
    for case_id, source_text, kind in CASES:
        directory = out / case_id
        directory.mkdir()
        source = directory / 'source.php'
        source.write_bytes(source_text.encode())
        native_command = [str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)]
        model_command = [str(ROOT / 'bin/php-semantics'), str(source), '--timeout', '60']
        native = subprocess.run(native_command, cwd=directory, env=env, capture_output=True, timeout=65)
        model = subprocess.run(model_command, cwd=directory, env=env, capture_output=True, timeout=65)
        for name, process in [('native', native), ('model', model)]:
            (directory / (name + '.stdout')).write_bytes(process.stdout)
            (directory / (name + '.stderr')).write_bytes(process.stderr)
            (directory / (name + '.status')).write_text(str(process.returncode) + '\n')
        actual = json.loads(model.stdout)
        expected = {'stdout': base64.b64encode(native.stdout).decode(),
                    'stderr': base64.b64encode(native.stderr).decode(), 'exit_status': native.returncode}
        if kind == 'agreement':
            passed = model.returncode == 0 and not model.stderr and all(actual.get(k) == v for k, v in expected.items())
        else:
            passed = model.returncode == 1 and not model.stderr and actual.get('status') == 'unsupported'
        rows.append({'id': case_id, 'kind': kind, 'pass': passed,
                     'source_sha256': digest(source), 'actual': actual, 'native': expected,
                     'native_command': native_command, 'model_command': model_command})
        print(case_id, passed, actual.get('status'), flush=True)
    assert before == {name: digest(ROOT / name) for name in watched}, 'inputs changed'
    report = {'result': 'pass' if all(row['pass'] for row in rows) else 'fail',
              'agreements': sum(row['kind'] == 'agreement' for row in rows),
              'unsupported_controls': sum(row['kind'] == 'unsupported' for row in rows),
              'inputs': before, 'profile': profile, 'cwd': 'each retained source directory',
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'records': rows, 'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    assert report['result'] == 'pass'


if __name__ == '__main__':
    main()
