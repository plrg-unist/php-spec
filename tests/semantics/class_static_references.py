#!/usr/bin/env python3
"""Exact original-source differentials for class static references."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ('reference-alias', '<?php class A { public static $x=1; } $r=&A::$x; $r=9; echo A::$x;'),
    ('typed-reference-atomic', '<?php class A { public static int $x=1; } $r=&A::$x; try{$r=[];}catch(TypeError $e){echo "T|";} echo A::$x;'),
    ('typed-reference-conflict', '<?php class A { public static int $x=1; public static string $y="1"; } $r=&A::$x; try{A::$y=&$r;}catch(TypeError $e){echo "T|";} echo A::$x,"|",A::$y;'),
    ('byref-argument', '<?php class A { public static int $x=1; } function f(&$v){$v=7;} f(A::$x); echo A::$x;'),
    ('cross-object-static', '<?php class A { public static int $x=1; public int $y=2; } $a=new A; $a->y =& A::$x; $a->y=7; echo A::$x,"|",$a->y;'),
    ('rebind-static', '<?php class A { public static int $x=1; } $r=&A::$x; $s=7; A::$x=&$s; $r=9; echo A::$x,"|",$r;'),
    ('typed-reference-uninitialized', '<?php class A { public static int $x; } try{$r=&A::$x;}catch(Error $e){echo $e->getMessage();}'),
    ('direct-overflow', '<?php class A { public static int $x=9223372036854775807; } try{++A::$x;}catch(TypeError $e){echo $e->getMessage();} echo "|",A::$x;'),
    ('alias-overflow', '<?php class A { public static int $x=9223372036854775807; } $r=&A::$x; try{++$r;}catch(TypeError $e){echo $e->getMessage();} echo "|",A::$x;'),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    watched = [*modules, 'spec/semantics/modules.json', 'bin/php-semantics',
               'frontend/worker.php', 'frontend/wire.php', '.tools/php-file.so',
               'tests/semantics/profile.json', 'tests/semantics/class_static_references.py',
               '.tools/php/bin/php', '_build/default/adapter/main.exe']
    before = {name: digest(ROOT / name) for name in watched}
    out = Path(tempfile.mkdtemp(prefix='class-static-references-', dir=ROOT / '.tools'))
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
        passed = (model.returncode == 0 and not model.stderr
                  and actual.get('status') in {'normal', 'php_error', 'static_rejection', 'explicit_exit'}
                  and all(actual.get(key) == value for key, value in expected.items()))
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
