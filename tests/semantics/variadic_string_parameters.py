#!/usr/bin/env python3
"""Stringable variadic elements and genuine deferred parameter defaults."""
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
    'positional-order': b'<?php class S{public string $id;function __construct($id){$this->id=$id;}function __toString(){echo $this->id,func_num_args(),"|";return $this->id;}}function take(string ...$xs){echo "F",func_num_args(),"|",$xs[0],"|",$xs[1],"|",func_get_arg(0),"|",func_get_arg(1);}take(new S("a"),new S("b"));',
    'mixed-named-order': b'<?php class S{public string $id;function __construct($id){$this->id=$id;}function __toString(){echo $this->id,func_num_args(),"|";return $this->id;}}function take(string $fixed,string ...$xs){echo "F",func_num_args(),"|",$fixed,"|",$xs[0],"|",$xs["z"],"|",$xs["a"],"|",func_get_arg(1);}take("f",new S("p"),z:new S("z"),a:new S("a"));',
    'positional-reference-backing': b'<?php class C{public static object $o;}class S{public static int $n=0;function __toString(){echo "T",func_num_args(),"|";global $v;if(self::$n===0){self::$n=1;C::$o=&$v;}return "v\\0raw";}}function take(string &...$xs){echo "F",func_num_args(),"|",$xs[0],"|",$xs[1],"|";try{$xs[0]=[];}catch(TypeError $e){echo "D|";}}$v=new S;$other=$v;take($v,$other);echo $v,"|",$other;unset($v,$other);$replacement=new stdClass;C::$o=&$replacement;unset($replacement);',
    'named-constrained-ordinal': b'<?php class C{public static object $o;}class S{function __toString(){echo "T|";return "s";}}function take(string &$fixed,string &...$xs){echo "BAD";}$fixed="f";$p="p";$z=new S;C::$o=new S;$r=&C::$o;try{take($fixed,$p,z:$z,bad:$r);}catch(TypeError $e){echo $e->getMessage();}echo "|",$z,"|",$r instanceof S?"object":"other";',
    'strict-variadic-and-default': b'<?php declare(strict_types=1);class S{function __toString(){echo "BAD";return "s";}}function take(string ...$xs){echo "BAD";}function omitted(string $s=new S){echo "BAD";}try{take(new S);}catch(TypeError $e){echo "V|";}try{omitted();}catch(TypeError $e){echo "D";}',
    'nominal-callable-priority': b'<?php class S{function __invoke(){echo "I|";}function __toString(){echo "T",func_num_args(),"|";return "s";}}function nominal(Stringable|string ...$xs){echo $xs[0] instanceof S?"N|":"BAD";}function callable_first(callable|string ...$xs){$xs[0]();}function omitted(Stringable|string $s=new S){echo $s instanceof S?"D|":"BAD";}function text(string ...$xs){echo "F",func_num_args(),"|",$xs[0];}$s=new S;nominal($s);callable_first($s);omitted();text($s);',
    'inherited-named-hole-default': b'<?php class S{function __toString(){echo __CLASS__,"/",static::class,"/",func_num_args(),"|";return "v\\0raw";}}class C extends S{public static function take(string &$s=new self,int $n=5){echo __CLASS__,"/",static::class,"/",func_num_args(),"|",$s,"|",func_get_arg(0),"|",$n;}}class D extends C{}D::take(n:7);',
    'default-conversion-throw': b'<?php class C{public static int $n=0;}class S{function __toString(){echo "T",func_num_args(),"|";C::$n=3;throw new Exception("stop");}}function take(string &$s=new S){echo "BAD";}try{take();}catch(Exception $e){echo "E:",$e->getMessage(),"|",$e->getPrevious()===null?"none":"previous","|",C::$n;}',
    'variadic-same-object-reentry': b'<?php class C{public static object $a;public static object $b;}class S{public static int $n=0;function __toString(){echo "T",func_num_args(),"|";global $x,$y;if(self::$n===0){self::$n=1;C::$a=&$x;take($y);}else{C::$b=&$y;}return "s";}}function take(string &...$xs){echo "F",func_num_args(),"|",$xs[0],"|";}$holder=new S;$x=$holder;$y=$holder;take($x);echo $x,"|",$y;',
    'required-hole-before-conversion': b'<?php class S{function __toString(){echo "BAD";return "s";}}function take(string $a,string $b=new S){echo "BAD";}$v=new S;try{take(b:$v);}catch(ArgumentCountError $e){echo "R|";}echo $v instanceof S?"object":"other";',
    'variadic-attach-throw': b'<?php class C{public static object $o;}class S{function __toString(){echo "T",func_num_args(),"|";global $v;C::$o=&$v;$v=new stdClass;throw new Exception("stop");}}function take(string &...$xs){echo "BAD";}$v=new S;try{take($v);}catch(Exception $e){echo "E:",$e->getMessage(),"|",$e->getPrevious()===null?"none":"previous","|";}echo $v instanceof stdClass?"object":"other","|",C::$o instanceof stdClass?"object":"other","|";try{$v=[];}catch(TypeError $e){echo "D";}',
}
CASES['unpacked-hole-default'] = CASES['inherited-named-hole-default'].replace(
    b'D::take(n:7);', b'$args=["n"=>7];D::take(...$args);')
CASES['default-constructor-stop'] = b'<?php class A{function __construct(){echo "C",func_num_args(),"|";}function __toString(){echo "T",func_num_args(),"|";return "s";}}class S extends A{}function take(string $s=new S){echo "F",func_num_args(),"|",$s;}take();'
CASES['default-named-new'] = b'<?php class S{function __toString(){echo "T|";return "s";}}function f(string $s=new S(x:1)){echo "F|",$s;}f();'
CASES['default-object-truth'] = b'<?php class S{function __toString(){echo "T",func_num_args(),"|";return "s";}}class U{function __construct(){echo "BAD";}}function f(string $s=(new S)?:new U){echo "F",func_num_args(),"|",$s,";";}function g(string $s=(new S)??new U){echo "G",func_num_args(),"|",$s;}f();g();'
CASES['inherited-parent-default'] = b'<?php class A{function __toString(){return static::class;}}class B extends A{static function f(string $s=new parent){echo $s;}}class C extends B{}C::f();\n'
CASES['named-trigger-handler-holes'] = b'<?php function handler($a,$b,$c,$d){echo "H",func_num_args(),"|",$b,"|",$a===E_USER_NOTICE?"N":"BAD";return true;}set_error_handler("handler");trigger_error(message:"x");echo "|after";\n'
EXPECTED = {
    'positional-order': b'a0|b0|F2|a|b|a|b',
    'mixed-named-order': b'p0|z0|a0|F2|f|p|z|a|p',
    'positional-reference-backing': b'T0|T0|F2|v\0raw|v\0raw|D|v\0raw|v\0raw',
    'strict-variadic-and-default': b'V|D',
    'nominal-callable-priority': b'N|I|D|T0|F1|s',
    'inherited-named-hole-default': b'S/C/0|C/D/2|v\0raw|v\0raw|7',
    'default-conversion-throw': b'T0|E:stop|none|3',
    'variadic-same-object-reentry': b'T0|T0|F1|s|F1|s|s|s',
    'required-hole-before-conversion': b'R|object',
    'variadic-attach-throw': b'T0|E:stop|none|object|object|D',
}
EXPECTED['unpacked-hole-default'] = EXPECTED['inherited-named-hole-default']
EXPECTED['default-constructor-stop'] = b'C0|T0|F0|s'
EXPECTED['default-named-new'] = b'T|F|s'
EXPECTED['default-object-truth'] = b'T0|F0|s;T0|G0|s'
EXPECTED['inherited-parent-default'] = b'A'
EXPECTED['named-trigger-handler-holes'] = b'H4|x|N|after'


def expected_stdout(name, path):
    if name == 'named-constrained-ordinal':
        return (b'T|take(): Argument #3 must be of type string, S given, called in ' +
                os.fsencode(path) + b' on line 1|s|object')
    return EXPECTED[name]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs(freeze=None):
    return cross.snapshot(freeze)


def constructor_stop(directory, path):
    native = driver.process([str(ROOT / '.tools/php/bin/php'), '-n', *driver.types.FLAGS,
                             str(path)], directory / 'native', 30, directory)
    assert native.returncode == 0 and not native.stderr
    assert native.stdout == EXPECTED['default-constructor-stop']
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
    assert outcome['status'] == 'unsupported' and outcome['reason'] == 'parameter default constructor'
    assert outcome['diagnostic'] is None
    assert not base64.b64decode(outcome['stdout'], validate=True)
    assert not base64.b64decode(outcome['stderr'], validate=True)
    return {'status': outcome['status'], 'reason': outcome['reason'], 'semantic_agreement': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--select', help='Comma-separated exact case IDs')
    parser.add_argument('--freeze', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(selected) == len(set(selected)) and all(n in CASES for n in selected)
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = inputs(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='variadic-string-parameters-', dir=ROOT / '.tools'))
    report = {'result': 'fail', 'selected': selected, 'records': [], 'inputs': before,
              'profile': driver.types.PROFILE, 'semantic_agreements': 0,
              'unsupported_controls': 0, 'scope': 'Variadic elements and deferred parameter defaults; no typed-return producer.'}
    print(out, flush=True)
    try:
        for name in selected:
            directory = out / name; directory.mkdir()
            path = directory / 'source.php'; path.write_bytes(CASES[name])
            row = {'id': name, 'source_sha256': sha(path), 'completed': False, 'passed': False}
            report['records'].append(row)
            if name == 'default-constructor-stop':
                row['observation'] = constructor_stop(directory, path)
                report['unsupported_controls'] += 1
            else:
                expected = expected_stdout(name, path)
                row['observation'] = cross.source({'expected_exit_status': 0,
                    'expected_stdout': expected.decode(), 'abrupt': False}, directory, path)
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
