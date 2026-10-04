#!/usr/bin/env python3
"""Constant-AST source constructor reception, ordering and declaration context."""
import argparse
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'direct-default-constructor': b'<?php class A{function __construct(){echo "C",func_num_args(),"|";}function __toString(){echo "T",func_num_args(),"|";return "s";}}class S extends A{}function take(string $s=new A){echo "F",func_num_args(),"|",$s;}take();',
    'inherited-owner-called': b'<?php class A{function __construct(){echo __CLASS__,"/",static::class,"|";}function __toString(){return __CLASS__."/".static::class;}}class B extends A{static function take(string $s=new self){echo __CLASS__,"/",static::class,"|",$s;}}class C extends B{}C::take();\n',
    'arguments-before-access': b'<?php function h($a,$b,$c,$d){echo $a===E_DEPRECATED?"D|":"W|";return true;}set_error_handler("h");class C{private function __construct($x){echo "BAD";}}function take(C $x=new C(E_STRICT)){echo "BAD";}try{take();}catch(Error $e){echo "E|",$e->getMessage();}\n',
    'all-values-before-unknown-name': b'<?php function h($a,$b,$c,$d){echo $a===E_DEPRECATED?"D|":"W|";return true;}set_error_handler("h");class C{function __construct($x){echo "BAD";}}function take(C $x=new C(missing:1,x:E_STRICT)){echo "BAD";}try{take();}catch(Error $e){echo "E|",$e->getMessage();}\n',
    'duplicate-after-current-value': b'<?php function h($a,$b,$c,$d){echo $a===E_DEPRECATED?"D|":"W|";return true;}set_error_handler("h");class C{private function __construct($a){echo "BAD";}}function take(C $x=new C(a:E_STRICT,a:E_STRICT)){echo "BAD";}try{take();}catch(Error $e){echo "E|",$e->getMessage();}\n',
    'all-values-before-type-error': b'<?php function h($a,$b,$c,$d){echo $a===E_DEPRECATED?"D|":"W|";return true;}set_error_handler("h");class C{function __construct(int $x,int $y){echo "BAD";}}function take(C $x=new C("bad",E_STRICT)){echo "BAD";}try{take();}catch(TypeError $e){echo "E";}\n',
    'constructor-byref-warning': b'<?php function h($a,$b,$c,$d){echo "W|",$b,"|";return true;}set_error_handler("h");class C{function __construct(string &$x){echo "C",$x,"|";$x="r";}}function take(C $x=new C("q")){echo "F";}take();\n',
    'constructor-strict-definition': b'<?php declare(strict_types=1);class C{function __construct(int $x){echo "C",$x,"|";}}function take(C $x=new C("1")){echo "F";}try{take();}catch(TypeError $e){echo "E";}\n',
    'byref-warning-handler-throw': b'<?php function h($a,$b,$c,$d){echo "W|";throw new Exception("stop");}set_error_handler("h");class C{function __construct(string &$x){echo "BAD";}}function take(C $x=new C("q")){echo "BAD";}try{take();}catch(Exception $e){echo "E:",$e->getMessage(),"|",$e->getPrevious()===null?"none":"previous";}\n',
    'constructor-throw-trace': b'<?php\nclass C {\n    function __construct($x) {\n        throw new Exception("ctor");\n    }\n}\nfunction take(\n    C $c =\n        new C(\n            1\n        )\n) {}\ntry { take(); }\ncatch (Exception $e) {\n    $t = $e->getTrace();\n    echo "E", $e->getLine(), "|", $e->getFile() === __FILE__ ? "same" : "other", "|";\n    echo $t[0]["function"], "|", $t[0]["file"] ?? "internal", "|", $t[0]["line"] ?? 0, "|";\n    echo $t[1]["function"], "|", $t[1]["line"] ?? 0, "|", isset($t[1]["args"][0]) ? "arg" : "none";\n}\n',
    'constructor-type-error-trace': b'<?php\nclass C {\n    function __construct(int $x) {}\n}\nfunction take(\n    C $c =\n        new C(\n            "bad"\n        )\n) {}\ntry { take(); }\ncatch (TypeError $e) {\n    $t = $e->getTrace();\n    echo "E", $e->getLine(), "|", $e->getFile() === __FILE__ ? "same" : "other", "|", $e->getMessage(), "|";\n    echo $t[0]["function"], "|", $t[0]["file"] ?? "internal", "|", $t[0]["line"] ?? 0, "|";\n    echo $t[1]["function"], "|", $t[1]["line"] ?? 0, "|", isset($t[1]["args"][0]) ? "arg" : "none";\n}\n',
    'strict-caller-weak-default': b'<?php declare(strict_types=1);class C{function __construct(int $x){echo "C",$x,"|";}}eval(\'declare(strict_types=0);function take(C $x=new C("1")){echo "F";}\');take();\n',
    'weak-caller-strict-default': b'<?php class C{function __construct(int $x){echo "BAD";}}eval(\'declare(strict_types=1);function take(C $x=new C("1")){echo "BAD";}\');try{take();}catch(TypeError $e){echo "E";}\n',
    'allocation-before-arguments': b'<?php function h($a,$b,$c,$d){echo "BAD";return true;}set_error_handler("h");abstract class C{function __construct($x){echo "BAD";}}function take(C $x=new C(E_STRICT)){echo "BAD";}try{take();}catch(Error $e){echo "E|",$e->getMessage();}\n',
    'private-declaring-scope': b'<?php class A{private function __construct(){echo "C",__CLASS__,"|";}function __toString(){return static::class;}static function take(string $s=new self){echo "F",static::class,"|",$s;}}class B extends A{}B::take();\n',
    'constructor-default-freshness': b'<?php class C{public static int $n=0;public int $id;function __construct(){self::$n+=1;$this->id=self::$n;echo "C",$this->id,"|";}function __toString(){echo "T",$this->id,"|";return "s".$this->id;}}function take(string $s=new C,$label="L"){echo "F",func_num_args(),"|",$s,"|",$label,";";}take();take(label:"x");take();\n',
    'warning-before-later-name': b'<?php function h($a,$b,$c,$d){echo $a===E_DEPRECATED?"D|":"W|";return true;}set_error_handler("h");class C{function __construct(string &$a){echo "BAD";}}function take(C $x=new C(a:"q",missing:E_STRICT)){echo "BAD";}try{take();}catch(Error $e){echo "E|",$e->getMessage();}\n',
    'cold-class-before-arguments': b'<?php\nfunction h($level,$message,$file,$line){echo "D",func_num_args(),"|";return true;}\nset_error_handler("h");\nclass C {\n    const X=E_STRICT;\n    public int $p=7;\n    function __construct($x){echo "C",self::X,"/",$x,"/",$this->p,"|";}\n}\nfunction take(C $x=new C(E_STRICT)){echo "F";}\ntake();\n',
    'cold-class-aborts-before-arguments': b'<?php\nfunction h($level,$message,$file,$line){echo "BAD";return true;}\nset_error_handler("h");\nclass C {\n    const X=MISSING;\n    function __construct($x){echo "BAD";}\n}\nfunction take(C $x=new C(E_STRICT)){echo "BAD";}\ntry{take();}catch(Error $e){echo "E|",$e->getMessage();}\n',
    'nested-constructor-stringable': b'<?php class V{function __toString(){echo "T|";return "v";}}class C{function __construct(string $v){echo "C",$v,"|";}function __toString(){return "s";}}function f(string $s=new C(new V)){echo "F|",$s;}f();\n',
    'owned-phases': b'<?php\nfunction h($level,$message,$file,$line){echo $level===E_WARNING?"W|":"D|";return true;}\nset_error_handler("h");\nclass V{function __toString(){echo "T|";return "v";}}\nclass C{\n    const X=E_STRICT;\n    public string $p="";\n    function __construct(string &$v,int $n){$this->p=$v;echo "C",$n,"|";}\n    function __toString(){echo "S|";return $this->p;}\n}\nfunction f(\n    string $s =\n        new C(new V,1)\n){echo "F|",$s;}\nf();\n',
    'ordinary-positional-control': b'<?php function g(int $x,int $y){echo "G|",$x+$y;} g(1,2);\n',
    'direct-class-fetch': b'<?php function h($l,$m,$f,$n){echo "D|";return true;} set_error_handler("h"); class K{const X=[E_STRICT];} function f(array $x=K::X){echo $x[0];} f();\n',
}
EXPECTED = {
    'direct-default-constructor': b'C0|T0|F0|s',
    'inherited-owner-called': b'A/B|B/C|A/B',
    'arguments-before-access': b'D|E|Call to private C::__construct() from global scope',
    'all-values-before-unknown-name': b'D|E|Unknown named parameter $missing',
    'duplicate-after-current-value': b'D|D|E|Named parameter $a overwrites previous argument',
    'all-values-before-type-error': b'D|E',
    'constructor-byref-warning': b'W|C::__construct(): Argument #1 ($x) must be passed by reference, value given|Cq|F',
    'constructor-strict-definition': b'E',
    'byref-warning-handler-throw': b'W|E:stop|none',
    'strict-caller-weak-default': b'C1|F',
    'weak-caller-strict-default': b'E',
    'allocation-before-arguments': b'E|Cannot instantiate abstract class C',
    'private-declaring-scope': b'CA|FB|A',
    'constructor-default-freshness': b'C1|T1|F0|s1|L;C2|T2|F2|s2|x;C3|T3|F0|s3|L;',
    'warning-before-later-name': b'D|W|E|Unknown named parameter $missing',
    'cold-class-before-arguments': b'D4|D4|C2048/2048/7|F',
    'cold-class-aborts-before-arguments': b'E|Undefined constant "MISSING"',
    'nested-constructor-stringable': b'T|Cv|F|s',
    'owned-phases': b'D|W|T|C1|S|F|v',
    'ordinary-positional-control': b'G|3',
    'direct-class-fetch': b'D|2048',
}


def expected_stdout(name, path):
    if name == 'constructor-throw-trace':
        return b'E4|same|__construct|' + os.fsencode(path) + b'|8|take|13|none'
    if name == 'constructor-type-error-trace':
        file = os.fsencode(path)
        return (b'E3|same|C::__construct(): Argument #1 ($x) must be of type int, string given, called in ' +
                file + b' on line 6|__construct|' + file + b'|6|take|11|none')
    return EXPECTED[name]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='Comma-separated exact case IDs')
    parser.add_argument('--freeze', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(selected) == len(set(selected)) and all(name in CASES for name in selected)
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='default-constructors-', dir=ROOT / '.tools'))
    report = {'passed': False, 'completed': False, 'before': before,
              'profile': cross.invoke.types.PROFILE, 'selected': selected, 'records': []}
    print(out, flush=True)
    try:
        for name in selected:
            directory = out / name; directory.mkdir()
            source = directory / 'source.php'; source.write_bytes(CASES[name])
            row = {'case': name, 'source_sha256': cross.invoke.sha(source), 'completed': False}
            report['records'].append(row)
            row['outcome'] = cross.source({'abrupt': False, 'expected_exit_status': 0,
                'expected_stdout': expected_stdout(name, source).decode()}, directory, source)
            row['completed'] = True
            print(name, row['outcome']['status'], flush=True)
        report.update(passed=True, completed=True)
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = cross.snapshot(args.freeze)
        report['passed'] = report['passed'] and report['before'] == report['after']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed'] and report['completed']


if __name__ == '__main__':
    main()
