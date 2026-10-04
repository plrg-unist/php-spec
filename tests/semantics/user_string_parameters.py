#!/usr/bin/env python3
"""Weak Stringable parameter reception; new property sources stay explicit."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
import typed_static_invoke_set_protocol as driver

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'value-copy': b'<?php class S{function __toString(){echo "T",func_num_args(),"|";return "v\\0raw";}}function take(string $s){echo "V",func_num_args(),"|",$s,"|",func_get_arg(0);} $v=new S;take($v);echo "|",$v instanceof S?"object":"other";',
    'value-callback-mutation': b'<?php class S{function __toString(){echo "T",func_num_args(),"|";global $v;$v="side";return "converted";}}function take(string $s){echo "V",func_num_args(),"|",$s;} $v=new S;take($v);echo "|",$v;',
    'free-reference-mutation': b'<?php class S{function __toString(){echo "T",func_num_args(),"|";global $v;$v="side";return "converted";}}function take(string &$s){echo "F",func_num_args(),"|",func_get_arg(0);} $v=new S;take($v);echo "|",$v;',
    'receive-order-shared-cell': b'<?php class S{function __toString(){echo "T|";return "v";}}function take(string &$x,string &$y){echo "F",func_num_args(),"|",$x,"|",$y;} $v=new S;take($v,$v);echo "|",$v;',
    'conversion-throw': b'<?php class S{function __toString(){echo "T",func_num_args(),"|";global $v;$v="side";throw new Exception("X");}}function take(string &$s){echo "BAD";} $v=new S;try{take($v);}catch(Exception $e){echo $e->getMessage(),"|",$e->getPrevious()===null?"none":"previous";}echo "|",$v;',
    'strict-rejection': b'<?php declare(strict_types=1);class S{function __toString(){echo "BAD";return "v";}}function take(string $s){echo "BAD";} $v=new S;try{take($v);}catch(TypeError $e){echo "R";}echo "|",$v instanceof S?"object":"other";',
    'constrained-reference-rejection': b'<?php class S{function __toString(){echo "BAD";return "v";}}class C{public static object $o;}function take(string &$s){echo "BAD";}C::$o=new S;$r=&C::$o;try{take($r);}catch(TypeError $e){echo "R";}echo "|",$r instanceof S?"object":"other";',
    'nominal-before-conversion': b'<?php class S{function __toString(){echo "BAD";return "v";}}function take(Stringable|string $s){echo "N",$s instanceof S?"object":"other";}take(new S);',
    'callable-before-conversion': b'<?php class S{function __invoke(){echo "I";}function __toString(){echo "BAD";return "v";}}function take(callable|string $s){echo "C";$s();}take(new S);',
    'inherited-named-default': b'<?php class A{function __toString(){echo __CLASS__,"/",static::class,"/",func_num_args(),"|";return "x";}}class B extends A{}class C{public static function take(string $s,int $n=5){echo __CLASS__,"/",static::class,"/",func_num_args(),"|",$s,"|",$n;}}class D extends C{}D::take(s:new B);',
    'same-site-reentry': b'<?php class S{public static int $n=0;function __toString(){echo "S",func_num_args(),"|";if(self::$n===0){self::$n=1;take($this);}return "s";}}function take(string $s){echo "O",func_num_args(),"|",$s,"|";}take(new S);',
    'new-property-source-stop': b'<?php class C{public static object $o;}class S{function __toString(){echo "T",func_num_args(),"|";global $v;C::$o=&$v;return "s";}}function take(string &$s){echo "F",func_num_args(),"|",$s;} $v=new S;take($v);echo "|",$v;',
    'constant-closure-parameter': b'<?php class A{const F=static function(string $s){echo __CLASS__,"/",static::class,"/",func_num_args(),"|",$s,"|",func_get_arg(0);};}class B extends A{}class S{function __toString(){echo "T",func_num_args(),"|";return "v\\0raw";}}$f=B::F;$f(new S);unset($f);',
    'nonpublic-callable-priority': b'<?php class H{protected function __invoke(){echo "I",func_num_args(),"|";}public function __toString():string{echo "T",func_num_args(),"|";return "v";}}function pick(callable|string $f){$f();}function text(string $s){echo "S",func_num_args(),"|",$s;}$h=new H;pick($h);text($h);',
}
EXPECTED = {
    'value-copy': b'T0|V1|v\0raw|v\0raw|object',
    'value-callback-mutation': b'T0|V1|converted|side',
    'free-reference-mutation': b'T0|F1|converted|converted',
    'receive-order-shared-cell': b'T|F2|v|v|v',
    'conversion-throw': b'T0|X|none|side',
    'strict-rejection': b'R|object',
    'constrained-reference-rejection': b'R|object',
    'nominal-before-conversion': b'Nobject',
    'callable-before-conversion': b'CI',
    'inherited-named-default': b'A/B/0|C/D/1|x|5',
    'same-site-reentry': b'S0|S0|O1|s|O1|s|',
    'new-property-source-stop': b'T0|F1|s|s',
    'constant-closure-parameter': b'T0|A/A/1|v\0raw|v\0raw',
    'nonpublic-callable-priority': b'I0|T0|S1|v',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs(freeze=None):
    return cross.snapshot(freeze)


def unsupported_source(directory, path):
    native = driver.process([str(ROOT / '.tools/php/bin/php'), '-n', *driver.types.FLAGS,
                             str(path)], directory / 'native', 30, directory)
    assert native.returncode == 0 and not native.stderr
    assert native.stdout == EXPECTED['new-property-source-stop']
    facts = {'version': 2, 'main': driver.b64(os.fsencode(path)),
             'cwd': driver.b64(os.fsencode(directory)), 'include_path': driver.b64(b'.:'),
             'entries': [], 'chdir_entries': []}
    facts_path = directory / 'snapshot.json'
    facts_path.write_text(json.dumps(facts, sort_keys=True) + '\n')
    model = driver.process([str(ROOT / 'bin/php-semantics'), str(path), '--file-snapshot',
        str(facts_path), '--steps', '100000', '--timeout', '60'], directory / 'model', 90, directory)
    assert model.returncode == 1 and not model.stderr
    outcome = json.loads(model.stdout)
    assert outcome['frontend'] == 'accepted' and outcome['checked'] == 'program'
    assert outcome['status'] == 'unsupported'
    assert outcome['reason'] == 'parameter string conversion gained property type source'
    assert outcome['diagnostic'] is None
    assert base64.b64decode(outcome['stdout'], validate=True) == b'T0|'
    assert not base64.b64decode(outcome['stderr'], validate=True)
    return {'status': outcome['status'], 'reason': outcome['reason'], 'semantic_agreement': False}


def nonpublic_source(directory, path):
    native = driver.process([str(ROOT / '.tools/php/bin/php'), '-n', *driver.types.FLAGS,
                             str(path)], directory / 'native', 30, directory)
    warning = (b'Warning: The magic method H::__invoke() must have public visibility in ' +
               os.fsencode(path) + b' on line 1\n')
    assert native.returncode == 0 and native.stdout == EXPECTED['nonpublic-callable-priority']
    assert native.stderr == warning
    facts = {'version': 2, 'main': driver.b64(os.fsencode(path)),
             'cwd': driver.b64(os.fsencode(directory)), 'include_path': driver.b64(b'.:'),
             'entries': [], 'chdir_entries': []}
    facts_path = directory / 'snapshot.json'
    facts_path.write_text(json.dumps(facts, sort_keys=True) + '\n')
    model = driver.process([str(ROOT / 'bin/php-semantics'), str(path), '--file-snapshot',
        str(facts_path), '--steps', '100000', '--timeout', '60'], directory / 'model', 90, directory)
    assert model.returncode == 0 and not model.stderr
    outcome = json.loads(model.stdout)
    assert outcome['frontend'] == 'accepted' and outcome['checked'] == 'program'
    assert outcome['status'] == 'normal' and outcome['exit_status'] == 0
    assert outcome['diagnostic'] is None and outcome['reason'] is None
    assert base64.b64decode(outcome['stdout'], validate=True) == native.stdout
    assert base64.b64decode(outcome['stderr'], validate=True) == warning
    return {'status': outcome['status'], 'exit_status': outcome['exit_status']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--select', help='Comma-separated exact case IDs')
    parser.add_argument('--freeze', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(selected) == len(set(selected)) and all(n in CASES for n in selected)
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = inputs(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='string-parameters-', dir=ROOT / '.tools'))
    report = {'result': 'fail', 'selected': selected, 'records': [], 'inputs': before,
              'profile': driver.types.PROFILE, 'semantic_agreements': 0,
              'unsupported_controls': 0, 'scope': 'Supplied weak parameters; no typed-return witness.'}
    print(out, flush=True)
    try:
        for name in selected:
            directory = out / name; directory.mkdir()
            path = directory / 'source.php'; path.write_bytes(CASES[name])
            row = {'id': name, 'source_sha256': sha(path), 'completed': False, 'passed': False}
            report['records'].append(row)
            if name == 'new-property-source-stop':
                row['observation'] = unsupported_source(directory, path)
                report['unsupported_controls'] += 1
            elif name == 'nonpublic-callable-priority':
                row['observation'] = nonpublic_source(directory, path)
                report['semantic_agreements'] += 1
            else:
                row['observation'] = cross.source({'expected_exit_status': 0,
                    'expected_stdout': EXPECTED[name].decode(), 'abrupt': False}, directory, path)
                report['semantic_agreements'] += 1
            row.update(completed=True, passed=True)
            print(name, row['observation']['status'], flush=True)
        report['result'] = 'pass'
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after_inputs'] = inputs(args.freeze)
        if report['after_inputs'] != before:
            report['result'] = 'fail'
        report['raw_files'] = {str(p.relative_to(ROOT)): {'sha256': sha(p), 'bytes': p.stat().st_size,
            'mode': oct(p.stat().st_mode & 0o7777)} for p in sorted(out.rglob('*')) if p.is_file()}
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['result'], flush=True)
    assert report['result'] == 'pass'


if __name__ == '__main__':
    main()
