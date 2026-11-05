#!/usr/bin/env python3
"""Ticks: native-first exact original sources and explicit dependency controls."""
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
    'straight': (b'<?php function tick(){echo "T";} register_tick_function("tick"); declare(ticks=1);echo "A";echo "B";', b'TATBT'),
    'frequency2': (b'<?php function tick(){echo "T";} register_tick_function("tick"); declare(ticks=2);echo "A";echo "B";echo "C";', b'ATBCT'),
    'if-false': (b'<?php function tick(){echo "T";} register_tick_function("tick"); declare(ticks=1);if(false){echo "A";}echo "Z";', b'TZT'),
    'if-empty': (b'<?php function tick(){echo "T";} register_tick_function("tick"); declare(ticks=1);if(false){}echo "Z";', b'TTZT'),
    'for-body': (b'<?php function tick(){echo "T";} register_tick_function("tick"); declare(ticks=1);for($i=0;$i<2;$i++){echo "A";}echo "Z";', b'TATATTZT'),
    'break-skips-tick': (b'<?php function tick(){echo "T";} register_tick_function("tick"); declare(ticks=1);while(true){echo "A";break;}echo "Z";', b'TATTZT'),
    'goto-skips-tick': (b'<?php function tick(){echo "T";} register_tick_function("tick"); declare(ticks=1);goto done;echo "X";done:echo "Z";', b'TZT'),
    'return-skips-tick': (b'<?php function tick(){echo "T";} register_tick_function("tick"); declare(ticks=1);function f(){echo "F";return 1;}echo f();echo "Z";', b'TFT1TZT'),
    'nested-scope-dedup': (b'<?php function tick(){echo "T";} register_tick_function("tick"); declare(ticks=1);declare(ticks=2){echo "A";}echo "B";echo "C";', b'TABTCT'),
    'dynamic-not-inherited': (b'<?php function tick(){echo "T";} register_tick_function("tick"); declare(ticks=1);eval(\'echo "E";echo "V";\');echo "Z";', b'TEVTZT'),
    'dynamic-own-count': (b'<?php function tick(){echo "T";} register_tick_function("tick"); declare(ticks=2);eval(\'declare(ticks=2);echo "E";echo "V";\');echo "Z";', b'TEVTZT'),
    'registration-duplicates': (b'<?php function tick($x){echo $x;} register_tick_function("tick","A");register_tick_function("tick","B");declare(ticks=1);echo "X";unregister_tick_function("tick");echo "Z";', b'ABXABBZB'),
    'self-unregister-error': (b'<?php function tick(){try{unregister_tick_function("tick");}catch(Error $e){echo $e->getMessage(),"|";}}register_tick_function("tick");declare(ticks=1){echo "A";}', b'ARegistered tick function cannot be unregistered while it is being executed|'),
    'callback-throws-order': (b'<?php function a(){echo "A";throw new Exception("E");}function b(){echo "B";}register_tick_function("a");register_tick_function("b");try{declare(ticks=1){echo "X";}}catch(Exception $e){echo "C";}', b'XAC'),
    'exit-no-post-tick': (b'<?php function tick(){echo "T";} register_tick_function("tick"); register_shutdown_function(function(){echo "S";});declare(ticks=1);echo "A";exit("E");', b'TATES'),
    'literal-string-float': (b'<?php function tick(){echo "T";} register_tick_function("tick"); declare(ticks="2.5");echo "A";echo "Z";', b'ATZ'),
    'literal-negative': (b'<?php function tick(){echo "T";} register_tick_function("tick"); declare(ticks=-1);echo "A";echo "Z";', b''),
    'append-during-dispatch': (b'<?php $n=0;function a(){global $n;echo "A";if($n===0){$n=1;register_tick_function("b");}}function b(){echo "B";}register_tick_function("a");declare(ticks=1){echo "X";}', b'XAB'),
    'remove-next-during-dispatch': (b'<?php function a(){echo "A";unregister_tick_function("b");}function b(){echo "B";}register_tick_function("a");register_tick_function("b");declare(ticks=1){echo "X";}', b'XA'),
    'exit-running-bit': (b'<?php function tick(){echo "T";exit("E");}register_tick_function("tick");register_shutdown_function(function(){try{unregister_tick_function("tick");echo "U";}catch(Error $e){echo "LOCK";}});declare(ticks=1);echo "A";', b'TEU'),
    'captured-reference-argument': (b'<?php $x=1;$a=&$x;function tick($v){echo $v;}register_tick_function("tick",$a);$x=2;declare(ticks=1){echo "A";}', b'A1'),
    'retained-argument-array': (b'<?php $x=[1];function tick($v){echo $v[0];}register_tick_function("tick",$x);$x[0]=2;declare(ticks=1){echo "A";}', b'A1'),
    'byref-warning': (b'<?php set_error_handler(function($n,$m){echo "H";return true;});function tick(&$v){echo $v;}register_tick_function("tick",7);declare(ticks=1){echo "A";}', b'AH7'),
    'named-extra-reject': (b'<?php function tick($x){echo $x;}try{register_tick_function(callback:"tick",x:"A");}catch(Throwable $e){echo $e->getMessage();}', b'register_tick_function() does not accept unknown named parameters'),
    'fiber-switch-blocked': (b'<?php function tick(){try{Fiber::suspend();}catch(FiberError $e){echo $e->getMessage(),"|";}}register_tick_function("tick");$f=new Fiber(function(){declare(ticks=1){echo "A";}});$f->start();', b'ACannot switch fibers in current execution context|'),
    'empty-statements': (b'<?php function t(){echo "T";} declare(ticks=1); register_tick_function("t"); ; 1+2; $x=1; $x; echo "Z";', b'TTZT'),
    'function-directive-leaks': (b'<?php function t(){echo "T";} function f(){declare(ticks=1);echo "F";} register_tick_function("t"); echo "A"; f(); echo "Z";', b'TATTFTTZT'),
    'balanced-function-directive': (b'<?php function t(){echo "T";} function f(){declare(ticks=1){echo "F";}} register_tick_function("t"); echo "A"; f(); echo "Z";', b'AFTZ'),
    'callback-owned-arg': (b'<?php class C{function __destruct(){echo "D";}} function t($x){echo "T";} $x=new C; register_tick_function("t",$x); unset($x); echo "A"; unregister_tick_function("t"); echo "Z";', b'ADZ'),
}
STATUSES = {
    'straight': 'normal',
    'frequency2': 'normal',
    'if-false': 'normal',
    'if-empty': 'normal',
    'for-body': 'normal',
    'break-skips-tick': 'normal',
    'goto-skips-tick': 'normal',
    'return-skips-tick': 'normal',
    'nested-scope-dedup': 'normal',
    'dynamic-not-inherited': 'normal',
    'dynamic-own-count': 'normal',
    'registration-duplicates': 'normal',
    'self-unregister-error': 'normal',
    'callback-throws-order': 'normal',
    'exit-no-post-tick': 'explicit_exit',
    'literal-string-float': 'normal',
    'literal-negative': 'static_rejection',
    'append-during-dispatch': 'normal',
    'remove-next-during-dispatch': 'normal',
    'exit-running-bit': 'explicit_exit',
    'captured-reference-argument': 'normal',
    'retained-argument-array': 'normal',
    'byref-warning': 'normal',
    'named-extra-reject': 'normal',
    'fiber-switch-blocked': 'normal',
    'empty-statements': 'normal',
    'function-directive-leaks': 'normal',
    'balanced-function-directive': 'normal',
    'callback-owned-arg': 'normal',
}
EXITS = {
    'straight': 0,
    'frequency2': 0,
    'if-false': 0,
    'if-empty': 0,
    'for-body': 0,
    'break-skips-tick': 0,
    'goto-skips-tick': 0,
    'return-skips-tick': 0,
    'nested-scope-dedup': 0,
    'dynamic-not-inherited': 0,
    'dynamic-own-count': 0,
    'registration-duplicates': 0,
    'self-unregister-error': 0,
    'callback-throws-order': 0,
    'exit-no-post-tick': 0,
    'literal-string-float': 0,
    'literal-negative': 255,
    'append-during-dispatch': 0,
    'remove-next-during-dispatch': 0,
    'exit-running-bit': 0,
    'captured-reference-argument': 0,
    'retained-argument-array': 0,
    'byref-warning': 0,
    'named-extra-reject': 0,
    'fiber-switch-blocked': 0,
    'empty-statements': 0,
    'function-directive-leaks': 0,
    'balanced-function-directive': 0,
    'callback-owned-arg': 0,
}
CONTROLS = {
    'class-placement': (b'<?php echo "P"; declare(ticks=1); class C {} echo "A";', b''),
    'typed-variadic': (b'<?php function t(int ...$args){} echo "P"; register_tick_function("t",1); declare(ticks=1); echo "A";', b'P'),
    'builtin-callback': (b'<?php echo "P"; register_tick_function("ob_get_level"); declare(ticks=1); echo "A";', b'P'),
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
             'tests/semantics/profile.json', 'tests/semantics/tick_sources.py']
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
    out = args.output or Path(tempfile.mkdtemp(prefix='tick-sources-', dir=ROOT / '.tools'))
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
                assert outcome['reason']
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
