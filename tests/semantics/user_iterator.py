#!/usr/bin/env python3
"""Original-source Iterator foreach observations against the pinned CLI profile."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

import typed_static_invoke_set_protocol as driver

ROOT = Path(__file__).resolve().parents[2]
METHODS = {
    'current': 'function current():mixed {echo "C";return 10+$this->i;}',
    'next': 'function next():void {echo "N";$this->i++;}',
    'key': 'function key():mixed {echo "K";return 20+$this->i;}',
    'valid': 'function valid():bool {echo "V";return $this->i<2;}',
    'rewind': 'function rewind():void {echo "R";$this->i=0;}',
}


def source(loop='foreach(new It as $k=>$v){echo "[",$k,":",$v,"]";}',
           overrides=None, fields='public $i=0;', prefix='', parent='', declaration=''):
    methods = dict(METHODS)
    methods.update(overrides or {})
    body = fields + '\n' + '\n'.join(methods.values())
    return ('<?php\n' + prefix + '\n' + declaration + '\nclass It ' + parent +
            ' implements Iterator {\n' + body + '\n}\n' + loop).encode()


CASES = {
    'keyed-order': (source(), b'RVCK[20:10]NVCK[21:11]NV'),
    'values-omit-key': (source('foreach(new It as $v){echo $v;}'), b'RVC10NVC11NV'),
    'break-omits-next': (source('foreach(new It as $k=>$v){echo "[",$k,":",$v,"]";break;}'), b'RVCK[20:10]'),
    'continue-next': (source('foreach(new It as $k=>$v){echo "A";if($v==10)continue;echo "B";}'), b'RVCKANVCKABNV'),
    'raw-array-key': (source('foreach(new It as $k=>$v){echo $k[0],":",$v,";";}',
        {'key': 'function key():mixed {echo "K";return [$this->i];}'}), b'RVCK0:10;NVCK1:11;NV'),
    'raw-object-key': (source('$it=new It;foreach($it as $k=>$v){echo $k===$it?"T":"F";}',
        {'key': 'function key():mixed {echo "K";return $this;}'}), b'RVCKTNVCKTNV'),
    'raw-float-key': (source('foreach(new It as $k=>$v){echo $k,";";}',
        {'key': 'function key():mixed {echo "K";return 1.5;}'}), b'RVCK1.5;NVCK1.5;NV'),
    'optional-current-zero-argc': (source(overrides={'current':
        'function current($p=9):mixed {echo "C",func_num_args(),":",$p;return $this->i;}'}),
        b'RVC0:9K[20:0]NVC0:9K[21:1]NV'),
    'byref-rejected-before-callback': (source('try{foreach(new It as &$v){echo "BAD";}}catch(Error $e){echo $e->getMessage();}'),
        b'An iterator cannot be used with foreach by reference'),
    'current-cell-write': (source('foreach(new It as $k=>$v){echo $v,":",$k;}', {
        'current': 'function &current():mixed {echo "C";return $this->v;}',
        'key': 'function key():mixed {echo "K";$this->v=9;return 9;}',
        'valid': 'function valid():bool {echo "V";return $this->i<1;}'}, 'public $i=0;public $v=7;'), b'RVCK9:9NV'),
    'current-cell-rebind': (source('foreach(new It as $k=>$v){echo $v,":",$k;}', {
        'current': 'function &current():mixed {echo "C";return $this->v;}',
        'key': 'function key():mixed {echo "K";$GLOBALS["replacement"]=8;$this->v=&$GLOBALS["replacement"];return $this->v;}',
        'valid': 'function valid():bool {echo "V";return $this->i<1;}'}, 'public $i=0;public $v=7;'), b'RVCK7:8NV'),
    'value-target-before-key-target': (source('$a=1;try{foreach(new It as $k=>$a[0]){echo "BAD";}}catch(Error $e){echo isset($k)?"K":"U";}'), b'RVCKU'),
    'return-finally-cleanup': (source('function f(){try{foreach(new It as $v){echo $v;return;}}finally{echo "F";}}f();echo "D";'), b'RVC10FD'),
    'goto-cleanup': (source('foreach(new It as $v){echo $v;goto done;}done:echo "D";'), b'RVC10D'),
    'covariant-current': (source(overrides={'current': 'function current():int {echo "C";return 10+$this->i;}'}), b'RVCK[20:10]NVCK[21:11]NV'),
    'source-interface-nominal': (source('$it=new It;echo $it instanceof Iterator?"1":"0";echo $it instanceof Traversable?"1":"0";echo $it instanceof Seq?"1":"0";function f(Traversable $x){echo "T";}f($it);', prefix='interface Seq extends Iterator {}').replace(b'implements Iterator', b'implements Seq'), b'111T'),
    'traversable-parent-adds-iterator': (source(prefix='abstract class ParentIt implements Traversable {}', parent='extends ParentIt'), b'RVCK[20:10]NVCK[21:11]NV'),
}
for stage, expected in {'rewind': b'RE', 'valid': b'RVE', 'current': b'RVCE',
                        'key': b'RVCKE', 'next': b'RVCK[20:10]NE'}.items():
    typ = {'rewind': 'void', 'next': 'void', 'valid': 'bool'}.get(stage, 'mixed')
    method = f'function {stage}():{typ} {{echo "{METHODS[stage].split(chr(34))[1]}";throw new Exception("x");}}'
    loop = 'try{foreach(new It as $k=>$v){echo "[",$k,":",$v,"]";}}catch(Exception $e){echo "E";}'
    CASES['throw-' + stage] = (source(loop, {stage: method}), expected)

UNSUPPORTED = {
    'tentative-omitted': source(overrides={'current': 'function current(){return 1;}'}),
    'tentative-incompatible': source(overrides={'valid': 'function valid():int {return 0;}'}),
    'traversable-only': b'<?php class It implements Traversable {}',
    'aggregate-required-followup': source('').replace(b'class It ', b'class Inner ') + b'\nclass It implements IteratorAggregate {function getIterator():Traversable{echo "G";return new Inner;}} foreach(new It as $v){echo $v;break;}',
    'arrayaccess-required-followup': b'<?php class It implements ArrayAccess {function offsetExists(mixed $o):bool{return false;} function offsetGet(mixed $o):mixed{return 1;} function offsetSet(mixed $o,mixed $v):void{} function offsetUnset(mixed $o):void{}} echo (new It)[0];',
}
CONTROL_NATIVE = {
    'tentative-omitted': (0, b'RVK[20:1]NVK[21:1]NV', b'Deprecated: Return type of It::current() should either be compatible with Iterator::current(): mixed,'),
    'tentative-incompatible': (0, b'R', b'Deprecated: Return type of It::valid(): int should either be compatible with Iterator::valid(): bool,'),
    'traversable-only': (255, b'', b'Fatal error: Class It must implement interface Traversable as part of either Iterator or IteratorAggregate in Unknown on line 0'),
    'aggregate-required-followup': (0, b'GRVC10', b''),
    'arrayaccess-required-followup': (0, b'1', b''),
}
DECLARATIONS = {}
for name, current, message in [
    ('inherited-required-current', 'function current($x):mixed{return 1;}', 'Declaration of It::current($x): mixed must be compatible with Iterator::current(): mixed'),
    ('inherited-private-current', 'private function current():mixed{return 1;}', 'Access level to It::current() must be public (as in class Iterator)'),
]:
    methods = dict(METHODS, current=current)
    text = '<?php\nabstract class ParentIt implements Iterator {}\nclass It extends ParentIt {' + ''.join(methods.values()) + '}echo "BAD";'
    DECLARATIONS[name] = (text.encode(), message, 3)
DECLARATIONS['inherited-missing'] = (b'<?php\nabstract class ParentIt implements Iterator {}\nclass It extends ParentIt {}',
    'Class It contains 5 abstract methods and must therefore be declared abstract or implement the remaining methods (Iterator::current, Iterator::next, Iterator::key, ...)', 3)
DECLARATIONS['inherited-before-own-interface'] = (b'<?php\ninterface B {function g();}\nabstract class ParentIt implements Iterator {}\nclass It extends ParentIt implements B {static function g(){} function current($x):mixed{return 1;} function next():void{} function key():mixed{return 0;} function valid():bool{return false;} function rewind():void{}}',
    'Declaration of It::current($x): mixed must be compatible with Iterator::current(): mixed', 4)


def process(command, stem, timeout=90, cwd=ROOT):
    return driver.process(command, stem, timeout, cwd)


def runtime(out):
    probe = process([str(driver.types.PHP), '-n', *driver.types.FLAGS, '-r',
                     'echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,ini_get_all(null,false)]);'],
                    out / 'runtime', 10)
    assert probe.returncode == 0 and not probe.stderr
    identity = json.loads(probe.stdout)
    assert identity[:4] == ['8.5.10', 'cli', 8, False], identity[:4]
    assert all(identity[4][key] == value for key, value in driver.types.PROFILE.items())
    return identity


def provenance(out):
    (out / 'candidate.diff').write_bytes(subprocess.check_output(
        ['git', 'diff', 'HEAD', '--', 'spec/semantics'], cwd=ROOT))
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in [Path(__file__), ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
                         ROOT / '_build/default/adapter/main.exe']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['native', 'full'], default='full')
    parser.add_argument('--select', help='Comma-separated exact case IDs')
    args = parser.parse_args()
    names = args.select.split(',') if args.select else list(CASES) + list(DECLARATIONS) + list(UNSUPPORTED)
    assert names and len(names) == len(set(names)) and all(n in CASES or n in DECLARATIONS or n in UNSUPPORTED for n in names)
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    out = Path(tempfile.mkdtemp(prefix='user-iterator-', dir=ROOT / '.tools'))
    report = {'result': 'fail', 'mode': args.mode, 'records': [], 'profile': driver.types.PROFILE,
              'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'agreements': 0, 'unsupported': 0}
    print(out, flush=True)
    try:
        report['tools'] = provenance(out)
        report['runtime'] = runtime(out)
        for name in names:
            directory = out / name
            directory.mkdir()
            path = directory / 'source.php'
            path.write_bytes(CASES[name][0] if name in CASES else DECLARATIONS[name][0] if name in DECLARATIONS else UNSUPPORTED[name])
            row = {'id': name, 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
            report['records'].append(row)
            native = process([str(driver.types.PHP), '-n', *driver.types.FLAGS, str(path)], directory / 'native', 10, directory)
            row['native_exit'] = native.returncode
            if name in CASES:
                assert native.returncode == 0 and native.stdout == CASES[name][1] and not native.stderr, (name, native.stdout, native.stderr)
            elif name in DECLARATIONS:
                _, message, line = DECLARATIONS[name]
                expected = f'Fatal error: {message} in {path} on line {line}\nStack trace:\n#0 {{main}}\n'.encode()
                assert native.returncode == 255 and not native.stdout and native.stderr == expected, (name, native.stderr)
            else:
                exit_status, stdout, stderr_prefix = CONTROL_NATIVE[name]
                assert native.returncode == exit_status and native.stdout == stdout
                assert native.stderr.startswith(stderr_prefix) if stderr_prefix else not native.stderr
            if args.mode == 'full':
                model = process([str(ROOT / 'bin/php-semantics'), str(path), '--steps', '100000', '--timeout', '60'], directory / 'model', 90, directory)
                assert model.returncode == 0 and not model.stderr, (name, model.stderr)
                observation = json.loads(model.stdout)
                assert observation['frontend'] == 'accepted' and observation['checked'] == 'program', observation
                if name in UNSUPPORTED:
                    assert observation['status'] == 'unsupported', observation
                    report['unsupported'] += 1
                else:
                    assert observation['status'] == ('php_error' if name in DECLARATIONS else 'normal'), observation
                    assert observation['exit_status'] == native.returncode and observation['reason'] is None
                    if name in CASES:
                        assert observation['diagnostic'] is None
                    assert base64.b64decode(observation['stdout'], validate=True) == native.stdout, observation
                    assert base64.b64decode(observation['stderr'], validate=True) == native.stderr, observation
                    report['agreements'] += 1
                row['model_status'] = observation['status']
            row['passed'] = True
            print(name, 'pass', flush=True)
        report['result'] = 'pass'
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['result'], flush=True)


if __name__ == '__main__':
    main()
