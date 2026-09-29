#!/usr/bin/env python3
"""Exact original-source differentials for class static property access."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ('static-to-instance-fatal', '<?php class A { public static $x=1; } class B extends A { public $x=2; }'),
    ('instance-to-static-fatal', '<?php class A { public $x=1; } class B extends A { public static $x=2; }'),
    ('static-before-visibility-fatal', '<?php class A { public static $x=1; } class B extends A { private $x=2; }'),
    ('instance-before-visibility-fatal', '<?php class A { public $x=1; } class B extends A { private static $x=2; }'),
    ('static-type-override-fatal', '<?php class A { protected static int $x=1; } class B extends A { protected static string $x="s"; }'),
    ('static-visibility-override-fatal', '<?php class A { public static $x=1; } class B extends A { protected static $x=2; }'),
    ('shared-cell', '<?php class A { public static $x=1; } class B extends A {} B::$x=7; echo A::$x,"|",B::$x;'),
    ('redeclared-cell', '<?php class A { public static $x=1; } class B extends A { public static $x=2; } B::$x=7; echo A::$x,"|",B::$x;'),
    ('private-shadow', '<?php class A { private static $x=1; public static function f(){return self::$x;} } class B extends A { public static $x=2; } echo B::f(),"|",B::$x;'),
    ('private-static-instance-shadow', '<?php class A { private static $x=1; public static function a(){return self::$x;} } class B extends A { public $x=2; } echo A::a(),"|",(new B)->x;'),
    ('static-excluded-instance-cast', '<?php class A { public static $x=1; } foreach ((array)new A as $k=>$v) { echo $k; } echo "E";'),
    ('forward-early-default', '<?php echo A::$x; class A { public static $x=1; }'),
    ('late-private-public', '<?php class A { private static $x=1; public static function f(){return static::$x;} } class B extends A { public static $x=2; } echo B::f();'),
    ('late-private-denied', '<?php class A { private static $x=1; public static function f(){return static::$x;} } class B extends A { private static $x=2; } try{B::f();}catch(Error $e){echo $e->getMessage();}'),
    ('inherited-private-label', '<?php class A { private static $x=1; } class B extends A {} try{echo B::$x;}catch(Error $e){echo $e->getMessage();}'),
    ('inherited-protected-label', '<?php class A { protected static $x=1; } class B extends A {} try{echo B::$x;}catch(Error $e){echo $e->getMessage();}'),
    ('typed-uninitialized', '<?php class A { public static int $x; } class B extends A {} try{echo B::$x;}catch(Error $e){echo $e->getMessage();}'),
    ('typed-float-default', '<?php class A { public static float $x=1; } echo get_debug_type(A::$x),"|",A::$x;'),
    ('typed-write', '<?php class A { public static int $x; } A::$x=7; echo A::$x;'),
    ('typed-reject-atomic', '<?php class A { public static int $x=1; } try{A::$x=[];}catch(TypeError $e){echo "T|";} echo A::$x;'),
    ('quiet-missing', '<?php class A {} echo isset(A::$x)?"Y":"N", "|", empty(A::$x)?"Y":"N", "|", A::$x ?? "F";'),
    ('unknown-read', '<?php class A {} try{echo A::$x;}catch(Error $e){echo $e->getMessage();}'),
    ('quiet-uninitialized', '<?php class A { public static int $x; } echo isset(A::$x)?"Y":"N", "|", empty(A::$x)?"Y":"N", "|", A::$x ?? "F";'),
    ('quiet-private', '<?php class A { private static $x=1; } echo isset(A::$x)?"Y":"N", "|", empty(A::$x)?"Y":"N";'),
    ('coalesce-assign', '<?php class A { public static ?int $x; } A::$x ??= 7; echo A::$x;'),
    ('dynamic-name', '<?php class A { public static $x=1; } $n="x"; A::${$n}=7; echo A::$x;'),
    ('dynamic-class-lowercase', '<?php class A { public static $x=1; } $c="a"; $n="x"; echo $c::${$n};'),
    ('dynamic-object-class', '<?php class A { public static $x=1; } $a=new A; $a::$x=7; echo A::$x;'),
    ('class-name-order', '<?php class A { public static $x=1; } function cls(){echo "C";return "A";} function nm(){echo "N";return "x";} function val(){echo "V";return 7;} cls()::${nm()}=val(); echo "|",A::$x;'),
    ('private-write-order', '<?php class A { private static $x=1; } function val(){echo "V";return 7;} try{A::$x=val();}catch(Error $e){echo "E";}'),
    ('unset-error', '<?php class A { public static $x=1; } try{unset(A::$x);}catch(Error $e){echo $e->getMessage();} echo "|",A::$x;'),
    ('increment-compound', '<?php class A { public static int $x=1; } echo ++A::$x,"|"; A::$x+=3; echo A::$x;'),
    ('array-dimension-write', '<?php class A { public static array $x=[1]; } A::$x[0]=2; echo A::$x[0];'),
    ('array-cow', '<?php class A { public static array $x=[1]; } $a=A::$x; $a[0]=2; echo A::$x[0],"|",$a[0];'),
    ('typed-array-autoinit', '<?php class A { public static int $x; } try{A::$x[]=1;}catch(TypeError $e){echo $e->getMessage();}'),
    ('interface-static', '<?php interface I {} class A implements I { public static $x=7; } echo A::$x;'),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    watched = [*modules, 'spec/semantics/modules.json', 'bin/php-semantics',
               'frontend/worker.php', 'frontend/wire.php', '.tools/php-file.so',
               'tests/semantics/profile.json', 'tests/semantics/class_static_properties.py',
               '.tools/php/bin/php', '_build/default/adapter/main.exe']
    before = {name: digest(ROOT / name) for name in watched}
    out = Path(tempfile.mkdtemp(prefix='class-static-source-', dir=ROOT / '.tools'))
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    env = dict(os.environ, LC_ALL='C', TZ='UTC')
    rows = []
    for case_id, source_text in CASES:
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
        passed = model.returncode == 0 and not model.stderr and all(actual.get(key) == value for key, value in expected.items())
        rows.append({'id': case_id, 'pass': passed, 'source_sha256': digest(source),
                     'actual': actual, 'native': expected})
        print(case_id, passed, actual.get('status'), flush=True)
    assert before == {name: digest(ROOT / name) for name in watched}, 'inputs changed during run'
    report = {'result': 'pass' if all(row['pass'] for row in rows) else 'fail',
              'exact': sum(row['pass'] for row in rows), 'inputs': before,
              'profile': profile, 'records': rows, 'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    assert report['result'] == 'pass'


if __name__ == '__main__':
    main()
