#!/usr/bin/env python3
"""Anonymous keyword defaults use the live receiving Closure lexical scope."""
import argparse
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'rebound-self-parent': b'<?php class ParentOne{function __toString(){return static::class;}}class ParentTwo{function __toString(){return static::class;}}class A extends ParentOne{static function maker(){return static function(string $a=new self,string $b=new parent){echo $a,"/",$b,";";};}}class B extends ParentTwo{}$f=A::maker();$g=$f->bindTo(null,B::class);$g();$f();$g();\n',
    'global-bound-self': b'<?php class A{function __toString(){return "A";}}$f=static function(string $s=new self){echo $s;};$g=$f->bindTo(null,A::class);$g();try{$f();}catch(Error $e){echo "|E|",$e->getMessage();}\n',
    'closure-call-self': b'<?php class A{function __toString(){return static::class;}static function maker(){return function(string $s=new self){echo $s,"|";};}}class B extends A{}$f=A::maker();$f->call(new B);$f();\n',
    'anonymous-default-unrelated-called-scope-instanceof': b'<?php\nclass A{\n    private function __construct(){echo "A|";}\n    static function make(){return function($a=new self){echo get_called_class(),"/",($a instanceof A ? "A" : "B");};}\n}\nclass B{}\n$f=A::make();\n$g=$f->bindTo(new B,A::class);\nunset($f);\n$g();\n',
    'anonymous-default-parent-no-scope': b'<?php\nclass P{}\nclass A extends P{static function make(){return function($a=new parent(E_STRICT)){echo "BAD";};}}\nfunction h($level,$message,$file,$line){echo "D",func_num_args(),"|";return true;}\nset_error_handler("h");\n$f=A::make();$g=$f->bindTo(null,null);\ntry{$g();}catch(Error $e){echo "E|",$e->getMessage();}\n',
    'anonymous-default-parent-missing': b'<?php\nclass P{}\nclass A extends P{static function make(){return function($a=new parent(E_STRICT)){echo "BAD";};}}\nclass Bare{}\nfunction h($level,$message,$file,$line){echo "D",func_num_args(),"|";return true;}\nset_error_handler("h");\n$f=A::make();$g=$f->bindTo(null,Bare::class);\ntry{$g();}catch(Error $e){echo "E|",$e->getMessage();}\n',
    'anonymous-default-target-class-name-argument-instanceof': b'<?php\nclass A{function __construct($name){echo "A(",$name,")|";}static function make(){return function($a=new self(self::class)){echo get_called_class(),"/",($a instanceof B ? "B" : "A"),";";};}}\nclass B{function __construct($name){echo "B(",$name,")|";}}\n$f=A::make();$g=$f->bindTo(null,B::class);\n$f();$g();$f();\n',
    'anonymous-default-bound-arrow-instanceof': b"<?php\nclass A {\n    public static function make() {\n        return fn($a = new self) => $a instanceof B ? 'B' : 'A';\n    }\n}\nclass B {}\n$f = A::make();\n$g = $f->bindTo(null, B::class);\nunset($f);\necho $g(), '|';\n$r = $g->bindTo(null, A::class);\nunset($g);\necho $r();\n",
    'anonymous-default-trait-maker-rebound-instanceof': b"<?php\ntrait Maker {\n    public static function make() {\n        return function($a = new self, $b = new parent) {\n            echo ($a instanceof B ? 'B' : 'A'), '/', ($b instanceof ParentTwo ? 'ParentTwo' : 'ParentOne'), ';';\n        };\n    }\n}\nclass ParentOne {}\nclass A extends ParentOne { use Maker; }\nclass ParentTwo {}\nclass B extends ParentTwo {}\n$f = A::make();\n$g = $f->bindTo(null, B::class);\nunset($f);\n$g();\n$r = $g->bindTo(null, A::class);\nunset($g);\n$r();\n",
    'anonymous-default-callback-owner-retirement': b"<?php\nfunction h($level, $message, $file, $line) {\n    echo 'H|';\n    unset($GLOBALS['bound']);\n    return true;\n}\nclass A {\n    private function __construct($flag) { echo 'C', $flag, '|'; }\n    public function __toString() { echo 'T|'; return 'a'; }\n    public static function make() {\n        return function(string $s = new self(E_STRICT)) {\n            echo get_called_class(), '/', $s;\n        };\n    }\n}\nclass B {}\nset_error_handler('h');\n$maker = A::make();\n$bound = $maker->bindTo(new B, A::class);\nunset($maker);\n$bound();\n",
    'anonymous-default-recursive-template-scopes': b"<?php\nclass A {\n    private function __construct() {\n        global $inner;\n        $inner();\n        echo 'A|';\n    }\n    public function __toString() { echo 'TA|'; return 'a'; }\n    public static function make() {\n        return function(string $s = new self) { echo 'F', $s, '|'; };\n    }\n}\nclass B {\n    public function __construct() { echo 'B|'; }\n    public function __toString() { echo 'TB|'; return 'b'; }\n}\n$maker = A::make();\n$inner = $maker->bindTo(null, B::class);\n$outer = $maker->bindTo(null, A::class);\nunset($maker);\n$outer();\n",
}
EXPECTED = {
    'rebound-self-parent': b'B/ParentTwo;A/ParentOne;B/ParentTwo;',
    'global-bound-self': b'A|E|Cannot access "self" when no class scope is active',
    'closure-call-self': b'B|A|',
    'anonymous-default-unrelated-called-scope-instanceof': b'A|B/A',
    'anonymous-default-parent-no-scope': b'E|Cannot access "parent" when no class scope is active',
    'anonymous-default-parent-missing': b'E|Cannot access "parent" when current class scope has no parent',
    'anonymous-default-target-class-name-argument-instanceof': b'A(A)|A/A;B(B)|B/B;A(A)|A/A;',
    'anonymous-default-bound-arrow-instanceof': b'B|A',
    'anonymous-default-trait-maker-rebound-instanceof': b'B/ParentTwo;A/ParentOne;',
    'anonymous-default-callback-owner-retirement': b'H|C2048|T|B/a',
    'anonymous-default-recursive-template-scopes': b'B|TB|Fb|A|TA|Fa|',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='Comma-separated exact case IDs')
    parser.add_argument('--freeze', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(selected) == len(set(selected)) and all(name in CASES for name in selected)
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='anonymous-default-new-', dir=ROOT / '.tools'))
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
                'expected_stdout': EXPECTED[name].decode()}, directory, source)
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
