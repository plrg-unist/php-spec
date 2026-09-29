#!/usr/bin/env python3
"""Original-source differentials for structured Throwable traces and strings."""
from pathlib import Path
import base64
import hashlib
import json
import os
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ('empty-trace', '<?php $e=new Exception("x");echo $e->getTraceAsString();', 'agreement'),
    ('function-frame', '<?php function f($x){$e=new Exception;$t=$e->getTrace();echo $t[0]["function"],"|",$t[0]["args"][0];}f(7);', 'agreement'),
    ('frame-key-order', '<?php function f(){ $e=new Exception;$t=$e->getTrace();foreach($t[0] as $key=>$value){echo $key,",";}}f();', 'agreement'),
    ('inherited-frame', '<?php class A{function f($x){$e=new Exception;$t=$e->getTrace();echo $t[0]["class"],"|",$t[0]["type"],"|",$t[0]["function"];}}class B extends A{}(new B)->f(7);', 'agreement'),
    ('nested-method-order', '<?php class A{function f($x){$t=(new Exception)->getTrace();echo $t[0]["function"],"|",$t[0]["class"],"|",$t[0]["type"],"|",$t[1]["function"];}}function outer(){(new A)->f(7);}outer();', 'agreement'),
    ('closure-frame', '<?php $f=function($x){$t=(new Exception)->getTrace();echo $t[0]["function"],"|",$t[0]["args"][0];};$f(7);', 'agreement'),
    ('inherited-bound-closure', '<?php class A{function f(){return function($x){$t=(new Exception)->getTrace();echo $t[0]["class"],$t[0]["type"],"|",$t[0]["args"][0];};}}class B extends A{}(new B)->f()(7);', 'agreement'),
    ('named-extra-string', '<?php function f($a,...$rest){$e=new Exception;echo $e->getTraceAsString();}f(a:1,z:2);', 'agreement'),
    ('named-fixed-order', '<?php function f($a,$b){$e=new Exception;$t=$e->getTrace();echo $t[0]["args"][0],"|",$t[0]["args"][1];}f(b:2,a:1);', 'agreement'),
    ('array-snapshot', '<?php function f($a){$e=new Exception;$t=$e->getTrace();$a[0]=9;echo $t[0]["args"][0][0];}f([1]);', 'agreement'),
    ('reference-snapshot', '<?php function f(&$x){$e=new Exception;$t=$e->getTrace();$x=9;echo $t[0]["args"][0];}$x=1;f($x);', 'agreement'),
    ('object-identity', '<?php function f($o){$e=new Exception;$t=$e->getTrace();$o->x=9;echo $t[0]["args"][0]->x;}$o=new stdClass;$o->x=1;f($o);', 'agreement'),
    ('returned-trace-cow', '<?php function f($x){$e=new Exception;$t=$e->getTrace();$t[0]["function"]="changed";echo $e->getTrace()[0]["function"];}f(1);', 'agreement'),
    ('generated-typeerror', '<?php function f(int $x){}try{f("x");}catch(TypeError $e){$t=$e->getTrace();echo $t[0]["function"],"|",$e->getTraceAsString();}', 'agreement'),
    ('generated-arity', '<?php function f($x){}try{f();}catch(ArgumentCountError $e){$t=$e->getTrace();echo $t[0]["function"],"|",$e->getTraceAsString();}', 'agreement'),
    ('generated-wrapper-trace', '<?php $f=function($x){unset($x);missing();};try{$f->__invoke([1]);}catch(Error $e){$t=$e->getTrace();echo $t[0]["function"],"|",$t[0]["args"][0]===null,"|",$t[1]["function"],"|",$t[1]["class"],$t[1]["type"],"|",$t[1]["args"][0][0];}', 'agreement'),
    ('method-trace-string', '<?php class A{function f($x){$e=new Exception("x");echo $e->getTraceAsString();}}(new A)->f(7);', 'agreement'),
    ('string-basic', '<?php $e=new Exception("M");echo $e->__toString();', 'agreement'),
    ('string-empty-message', '<?php $e=new Exception;echo $e->__toString();', 'agreement'),
    ('string-typeerror-defined', '<?php function f(int $x){}try{f("x");}catch(TypeError $e){echo $e->__toString();}', 'agreement'),
    ('string-typeerror-nul', '<?php $e=new TypeError("x\\0, called in y");echo $e->__toString();', 'agreement'),
    ('string-implicit', '<?php $e=new Exception("M");echo $e;', 'agreement'),
    ('string-cast', '<?php $e=new Error("M");echo (string)$e;', 'agreement'),
    ('string-self-cycle', '<?php $e=new Exception("M");$e->__construct("M",0,$e);echo $e->__toString();', 'agreement'),
    ('string-two-cycle', '<?php $a=new Exception("A");$b=new Error("B");$a->__construct("A",0,$b);$b->__construct("B",0,$a);echo $a->__toString();', 'agreement'),
    ('reentry-trace', '<?php function f(){ $e=new Exception("M");$before=$e->getTraceAsString();$e->__construct("N");echo $e->getTraceAsString()===$before,"|",$e->getMessage();}f();', 'agreement'),
    ('trace-arity-side-effect', '<?php $e=new Exception;function v(){echo "V";return 1;}try{$e->getTrace(v());}catch(ArgumentCountError $x){echo "|",$x->getMessage();}', 'agreement'),
    ('trace-string-arity-side-effect', '<?php $e=new Exception;function v(){echo "V";return 1;}try{$e->getTraceAsString(v());}catch(ArgumentCountError $x){echo "|",$x->getMessage();}', 'agreement'),
    ('to-string-arity-side-effect', '<?php $e=new Exception;function v(){echo "V";return 1;}try{$e->__toString(v());}catch(ArgumentCountError $x){echo "|",$x->getMessage();}', 'agreement'),
    ('uncaught-frame', '<?php function f($x){throw new Exception("M");}f(7);', 'agreement'),
    ('uncaught-float-argument', '<?php function f($x){throw new Exception("M");}f(1.25);', 'agreement'),
    ('uncaught-object-argument', '<?php class A{} function f($x){throw new Exception("M");}f(new A);', 'agreement'),
    ('json-encode-control', '<?php $e=new Exception;echo json_encode($e->getTrace());', 'unsupported'),
    ('reflection-control', '<?php $e=new Exception;$p=new ReflectionProperty(Exception::class,"string");echo $p->getValue($e);', 'unsupported'),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    watched = [*modules, 'spec/semantics/modules.json', 'bin/php-semantics',
               'frontend/worker.php', 'frontend/wire.php', '.tools/php-file.so',
               'tests/semantics/profile.json', 'tests/semantics/throwable_traces.py',
               '.tools/php/bin/php', '_build/default/adapter/main.exe']
    before = {name: digest(ROOT / name) for name in watched}
    out = Path(tempfile.mkdtemp(prefix='trace-probes-', dir=ROOT / '.tools'))
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
