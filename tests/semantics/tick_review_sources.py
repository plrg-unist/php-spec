#!/usr/bin/env python3
"""Independent tick placement, callback lifetime and source-frame comparisons."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PROFILE = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
FLAGS = [arg for key, value in PROFILE.items() for arg in ('-d', key + '=' + value)]
CASES = {
    'uint32-frequency-zero': (b'<?php function tick(){echo "T";} register_tick_function("tick");declare(ticks=1);declare(ticks=4294967296);echo "A";echo "Z";', b'TATZT'),
    'literal-dim-adjacency': (b'<?php function t(){echo "T";} register_tick_function("t"); declare(ticks=1); [1][0]; echo "Z";', b'TTZT'),
    'callback-eval-counter': (b'<?php $n=0;function tick(){global $n;$n++;echo "T";if($n===1){eval(\'declare(ticks=1);echo "E";\');}}register_tick_function("tick");declare(ticks=2);echo "A";echo "B";echo "Z";', b'ATEBZT'),
    'closure-first-unregister': (b'<?php $t=function($x){echo $x;};register_tick_function($t,"A");register_tick_function($t,"B");declare(ticks=1){echo "X";}unregister_tick_function($t);declare(ticks=1){echo "Z";}', b'XABZB'),
    'return-destructor-unregister': (b'<?php class C{function __destruct(){try{unregister_tick_function("t");echo "U";}catch(Error $e){echo "H";}}}function t(){return new C;}register_tick_function("t");declare(ticks=1){echo "A";}', b'AH'),
    'return-destructor-fiber': (b'<?php class C{function __destruct(){try{Fiber::suspend();echo "U";}catch(FiberError $e){echo "H";}}}function t(){return new C;}register_tick_function("t");$f=new Fiber(function(){declare(ticks=1){echo "A";}});$f->start();', b'AH'),
    'strict-source-entry': (b'<?php declare(strict_types=1);\nfunction t(int $x){echo $x;}\nregister_tick_function("t","7");\ntry {\n declare(ticks=1) {\n  echo "A";\n }\n} catch (TypeError $e) {echo "C",$e->getFile()===__FILE__?"F":"X",$e->getLine(),"|",$e->getTrace()[0]["file"]===__FILE__?"F":"X",$e->getTrace()[0]["line"];}\n', b'ACF2|F6'),
    'empty-if-source-trace': (b'<?php\nfunction t(){throw new Exception("E");}\nregister_tick_function("t");\ntry {\n declare(ticks=1) {\n  if(false) {\n  }\n }\n} catch (Exception $e) {echo "C",$e->getTrace()[0]["file"]===__FILE__?"F":"X",$e->getTrace()[0]["line"];}\n', b'CF6'),
    'return-destructor-caller-scope': (b'<?php class C{function __destruct(){$e=new Exception("E");$a=$e->getTrace();echo $a[0]["function"],"|",isset($a[1])?$a[1]["function"]:"-";}}function t(){return new C;}register_tick_function("t");declare(ticks=1){echo "A";}', b'A__destruct|-'),
    'byref-source-warning': (b'<?php\nfunction t(&$x){echo $x;}\nregister_tick_function("t",7);\ndeclare(ticks=1){\n echo "A";\n}\n', b'A7'),
    'calling-scope-identity': (b'<?php class A{function m($x){echo $x;}}class B extends A{function run(){register_tick_function("A::m","A");register_tick_function([$this,"m"],"B");unregister_tick_function([$this,"m"]);}}$b=new B;$b->run();declare(ticks=1){echo "X";}', b'XA'),
    'active-match-removes-later-duplicate': (b'<?php function t($x){echo $x;if($x==="A"){try{unregister_tick_function("t");}catch(Error $e){echo "H";}}}register_tick_function("t","A");register_tick_function("t","B");declare(ticks=1){echo "X";}echo "Z";', b'XAHZ'),
    'two-active-error-chain': (b'<?php $n=0;function t($x){global $n;echo $x;if($x==="A"&&$n===0){$n=1;eval(\'declare(ticks=1);echo "E";\');}if($x==="B"&&$n===1){$n=2;try{unregister_tick_function("t");}catch(Error $e){echo "H",$e->getPrevious()===null?"N":"P";}}}register_tick_function("t","A");register_tick_function("t","B");register_tick_function("t","C");declare(ticks=1){echo "X";}echo "Z";', b'XABHPEBBZ'),
    'unregister-argument-before-receiver': (b'<?php class A{function m($v){}function __destruct(){echo "A";}}class B{function __destruct(){global $r;echo "1";$r=null;echo "2";}}$x=new A;$r=&$x;$cb=[&$r,"m"];register_tick_function($cb,new B);unset($x);unregister_tick_function($cb);echo "Z";', b'12AZ'),
    'unregister-throw-before-receiver': (b'<?php class A{function m($v){}function __destruct(){echo "A";}}class B{function __destruct(){global $r;echo "1";$r=null;echo "2";throw new Exception("E");}}$x=new A;$r=&$x;$cb=[&$r,"m"];register_tick_function($cb,new B);unset($x);try{unregister_tick_function($cb);}catch(Exception $e){echo "C";}echo "Z";', b'12ACZ'),
    'unregister-exit-before-shutdown': (b'<?php class A{function m($v){}function __destruct(){echo "A";}}class B{function __destruct(){global $r;echo "1";$r=null;exit("E");}}$x=new A;$r=&$x;$cb=[&$r,"m"];register_tick_function($cb,new B);unset($x);register_shutdown_function(function(){echo "S";});unregister_tick_function($cb);echo "Z";', b'1EAS'),
    'joined-eval-static-return-cleanup': (b'<?php class R{function __destruct(){echo "D";}}class C{function __destruct(){try{unregister_tick_function("t");echo "U";}catch(Error $e){echo "H";}}}function t(){return new C;}register_tick_function("t");eval(\'static $owner;$owner=new R;unset($owner);declare(ticks=1){echo "A";}\');echo "Z";', b'AHDZ'),
}
STATUSES = {
    'uint32-frequency-zero': 'normal',
    'literal-dim-adjacency': 'normal',
    'callback-eval-counter': 'normal',
    'closure-first-unregister': 'normal',
    'return-destructor-unregister': 'normal',
    'return-destructor-fiber': 'normal',
    'strict-source-entry': 'normal',
    'empty-if-source-trace': 'normal',
    'return-destructor-caller-scope': 'normal',
    'byref-source-warning': 'normal',
    'calling-scope-identity': 'normal',
    'active-match-removes-later-duplicate': 'normal',
    'two-active-error-chain': 'normal',
    'unregister-argument-before-receiver': 'normal',
    'unregister-throw-before-receiver': 'normal',
    'unregister-exit-before-shutdown': 'explicit_exit',
    'joined-eval-static-return-cleanup': 'normal',
}
EXITS = {
    'uint32-frequency-zero': 0,
    'literal-dim-adjacency': 0,
    'callback-eval-counter': 0,
    'closure-first-unregister': 0,
    'return-destructor-unregister': 0,
    'return-destructor-fiber': 0,
    'strict-source-entry': 0,
    'empty-if-source-trace': 0,
    'return-destructor-caller-scope': 0,
    'byref-source-warning': 0,
    'calling-scope-identity': 0,
    'active-match-removes-later-duplicate': 0,
    'two-active-error-chain': 0,
    'unregister-argument-before-receiver': 0,
    'unregister-throw-before-receiver': 0,
    'unregister-exit-before-shutdown': 0,
    'joined-eval-static-return-cleanup': 0,
}
CONTROLS = {
    'parameter-default-closure': (b'<?php function tick(){echo "T";}register_tick_function("tick");function f($x=static function(){declare(ticks=1);echo "C";}){return $x;}$c=f();$c();echo "Z";', b''),
    'foreach-value-key-closure': (b'<?php function tick(){echo "T";}register_tick_function("tick");$a=[];foreach([1] as $a[(function(){declare(ticks=1);return 0;})()]){}echo "Z";', b''),
    'abstract-parameter-default-closure': (b'<?php function tick(){echo "T";}register_tick_function("tick");abstract class A{abstract public function f($x=static function(){declare(ticks=1);echo "C";});}echo "Z";', b''),
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint():
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    names = ['spec/php.watsup', 'spec/semantics/modules.json', *modules,
             'adapter/main.ml', 'bin/php-semantics', '.tools/php/bin/php',
             '.tools/php-file.so', '_build/default/adapter/main.exe',
             'vendor/php-src/Zend/zend_compile.c', 'vendor/php-src/Zend/zend_vm_def.h',
             'vendor/php-src/ext/standard/basic_functions.c', 'vendor/php-src/main/php_ticks.c',
             'tests/semantics/profile.json', 'tests/semantics/tick_sources.py', 'tests/semantics/tick_review_sources.py']
    return {name: sha(ROOT / name) for name in names}


def run(argv, directory, name, timeout):
    environment = {'LC_ALL': 'C', 'TZ': 'UTC', 'PATH': '/usr/bin:/bin'}
    (directory / (name + '.command.json')).write_text(json.dumps(
        {'argv': argv, 'cwd': str(directory), 'env': environment}) + '\n')
    result = subprocess.run(argv, cwd=directory, env=environment,
                            capture_output=True, timeout=timeout)
    for channel, raw in [('stdout', result.stdout), ('stderr', result.stderr)]:
        (directory / (name + '.' + channel)).write_bytes(raw)
    (directory / (name + '.exit')).write_text(str(result.returncode) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact IDs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES) + list(CONTROLS)
    assert selected and len(set(selected)) == len(selected)
    assert all(name in CASES or name in CONTROLS for name in selected)
    out = args.output or Path(tempfile.mkdtemp(prefix='tick-review-sources-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'before': fingerprint(), 'profile': PROFILE, 'selected': selected, 'records': [],
              'completed': False, 'passed': False}
    print(out, flush=True)
    try:
        for name in selected:
            source = CASES[name][0] if name in CASES else CONTROLS[name][0]
            directory = out / name; directory.mkdir()
            path = directory / 'source.php'; path.write_bytes(source)
            native = run([str(ROOT / '.tools/php/bin/php'), '-n', *FLAGS, str(path)], directory, 'native', 10)
            if name in CASES:
                assert native.stdout == CASES[name][1], (name, native.stdout, CASES[name][1])
                assert native.returncode == EXITS[name], (name, native.returncode, native.stderr)
            modeled = run([str(ROOT / 'bin/php-semantics'), str(path), '--timeout', '60'], directory, 'model', 90)
            assert not modeled.stderr, (name, modeled.stdout, modeled.stderr)
            outcome = json.loads(modeled.stdout)
            if name in CASES:
                status = STATUSES[name]
                assert modeled.returncode == 0 and outcome['status'] == status, (name, outcome)
                assert outcome['reason'] is None
                assert base64.b64decode(outcome['stdout'], validate=True) == native.stdout, (name, outcome, native.stdout)
                assert base64.b64decode(outcome['stderr'], validate=True) == native.stderr, (name, outcome, native.stderr)
                assert outcome['exit_status'] == native.returncode
            else:
                assert modeled.returncode == 1 and outcome['status'] == 'unsupported', (name, outcome)
                assert base64.b64decode(outcome['stdout'], validate=True) == CONTROLS[name][1], (name, outcome)
                assert base64.b64decode(outcome['stderr'], validate=True) == b'', (name, outcome)
                assert outcome['reason'] == 'tick opcode placement for this statement', (name, outcome)
            report['records'].append({'case': name, 'source_sha256': sha(path), 'status': outcome['status'],
                                      'native_credit': name in CASES, 'native_exit': native.returncode,
                                      'stdout_sha256': hashlib.sha256(native.stdout).hexdigest(),
                                      'stderr_sha256': hashlib.sha256(native.stderr).hexdigest()})
            print(name, outcome['status'], flush=True)
        report.update(completed=True, passed=True)
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = fingerprint()
        report['passed'] = report['passed'] and report['before'] == report['after']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed'] and report['completed']


if __name__ == '__main__':
    main()
