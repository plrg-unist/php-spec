#!/usr/bin/env python3
"""Exact static-property bridges across selected calls and reference returns."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ('typed-return', b'<?php class A { public static int $x=1; } '
     b'function f(): string { A::$x=7; return 3; } echo f(),"|",A::$x;', {}, False),
    ('include-static-file', b'<?php class A { public static string $file="one.php"; } '
     b'include A::$file; echo "|",A::$file;', {'one.php': b'<?php echo "I";'}, True),
    ('selected-static-callee', b'<?php class A { public static $f="set_include_path"; '
     b'public static int $x=1; } function arg() { A::$f="ini_restore"; A::$x=7; '
     b'return "bridge"; } echo (A::$f)(arg()),"|",A::$f,"|",A::$x,"|",'
     b'set_include_path("tail");', {}, True),
    ('selected-name-throw', b'<?php class A { public static int $x=1; } '
     b'function nm() { global $a; $a=null; $f="set_include_path"; $f([]); } '
     b'$a=new A; try { echo $a::${nm()}; } catch (TypeError $e) { echo "T"; } '
     b'finally { echo "F"; } echo "|",A::$x;', {}, True),
    ('unused-reference-finally', b'<?php class A { public static int $x=1; } '
     b'function &f(): int { try { return A::$x; } '
     b'finally { A::$x=3; echo "F"; } } f(); echo A::$x;', {}, False),
    ('object-selector-detach', b'<?php class A { public int $p=1; public static $x=7; } '
     b'function nm(){global $a,$r;$a=null;try{$r="s";echo "W";}catch(TypeError $e)'
     b'{echo "E";}return "x";} $a=new A;$r=&$a->p;echo $a::${nm()},"|",$r;', {}, False),
    ('object-selector-retained', b'<?php class A { public int $p=1; public static $x=7; } '
     b'function nm(){global $a,$r;$a=null;try{$r="s";echo "W";}catch(TypeError $e)'
     b'{echo "E";}return "x";} $a=new A;$keep=$a;$r=&$a->p;echo $a::${nm()},"|",$r;', {}, False),
    ('object-selector-cow', b'<?php class A { public int $p=1; public static $x=7; } '
     b'function nm(){global $a,$copy;$a=null;$other=$copy;try{$other[0]="s";echo "W";}'
     b'catch(TypeError $e){echo "E";}return "x";} $a=new A;$r=&$a->p;$copy=[&$r];'
     b'echo $a::${nm()},"|",$r,"|",$copy[0];', {}, False),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    watched = [*modules, 'spec/semantics/modules.json', 'bin/php-semantics',
               'frontend/worker.php', 'frontend/wire.php', '.tools/php-file.so',
               'tests/semantics/profile.json', 'tests/semantics/class_static_merged_bridge.py',
               '.tools/php/bin/php', '_build/default/adapter/main.exe']
    before = {name: digest(ROOT / name) for name in watched}
    out = Path(tempfile.mkdtemp(prefix='class-static-merged-', dir=ROOT / '.tools'))
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    env = dict(os.environ, LC_ALL='C', TZ='UTC')
    rows = []
    for case_id, source_bytes, files, finite in CASES:
        directory = out / case_id
        directory.mkdir()
        source = directory / 'source.php'
        source.write_bytes(source_bytes)
        for name, content in files.items():
            path = directory / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        model_command = [str(ROOT / 'bin/php-semantics'), str(source), '--timeout', '60']
        if finite:
            snapshot = {'version': 1, 'main': base64.b64encode(os.fsencode(source.resolve())).decode(),
                        'cwd': base64.b64encode(os.fsencode(ROOT.resolve())).decode(),
                        'include_path': base64.b64encode(b'.:').decode(),
                        'entries': [{'caller': base64.b64encode(os.fsencode(source.resolve())).decode(),
                                     'requested': base64.b64encode(os.fsencode(name)).decode(),
                                     'status': 'opened',
                                     'resolved': base64.b64encode(os.fsencode((directory / name).resolve())).decode(),
                                     'opened': base64.b64encode(os.fsencode((directory / name).resolve())).decode(),
                                     'source': base64.b64encode(content).decode()} for name, content in files.items()]}
            snapshot_path = directory / 'snapshot.json'
            snapshot_path.write_text(json.dumps(snapshot, sort_keys=True) + '\n')
            model_command += ['--file-snapshot', str(snapshot_path)]
        native = subprocess.run([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)],
                                cwd=ROOT, env=env, capture_output=True, timeout=65)
        model = subprocess.run(model_command, cwd=ROOT, env=env, capture_output=True, timeout=65)
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
                     'files': {name: digest(directory / name) for name in files},
                     'snapshot_sha256': digest(snapshot_path) if finite else None,
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
