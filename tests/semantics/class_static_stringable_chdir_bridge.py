#!/usr/bin/env python3
"""A static-name callback preserves live cells across Stringable chdir pauses."""
import base64
import json
import os
from pathlib import Path
import subprocess
import tempfile

from class_static_merged_bridge import ROOT, digest

SOURCE = (b'<?php class A{public int $p=1;public static string $x="3";}'
          b'class D{public function __toString():string{global $a,$r,$s;'
          b'$a=null;$r="s";$s="9";echo "T";return ".tools";}}'
          b'function nm(){echo chdir(new D)?"C":"F";echo chdir("..")?"R":"F";'
          b'return "x";}$a=new A;$r=&$a->p;$s=&A::$x;echo $a::${nm()},"|",$r,"|",$s;')


def b64(value):
    return base64.b64encode(value).decode()


def main():
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    watched = [*modules, 'spec/semantics/modules.json', 'bin/php-semantics',
               'frontend/worker.php', 'frontend/wire.php', '.tools/php-file.so',
               'tests/semantics/profile.json', 'tests/semantics/class_static_merged_bridge.py',
               'tests/semantics/class_static_stringable_chdir_bridge.py',
               '.tools/php/bin/php', '_build/default/adapter/main.exe']
    before = {name: digest(ROOT / name) for name in watched}
    out = Path(tempfile.mkdtemp(prefix='class-static-stringable-chdir-', dir=ROOT / '.tools'))
    source = out / 'source.php'
    source.write_bytes(SOURCE)
    cwd = b64(os.fsencode(ROOT.resolve()))
    sub = b64(os.fsencode((ROOT / '.tools').resolve()))
    snapshot = {'version': 2, 'main': b64(os.fsencode(source.resolve())), 'cwd': cwd,
                'include_path': b64(b'.:'), 'entries': [], 'chdir_entries': [
                    {'cwd': cwd, 'requested': b64(b'.tools'), 'status': 'success', 'next_cwd': sub},
                    {'cwd': sub, 'requested': b64(b'..'), 'status': 'success', 'next_cwd': cwd}]}
    snapshot_path = out / 'snapshot.json'
    snapshot_path.write_text(json.dumps(snapshot, sort_keys=True) + '\n')
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    env = dict(os.environ, LC_ALL='C', TZ='UTC')
    native_command = [str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)]
    model_command = [str(ROOT / 'bin/php-semantics'), str(source), '--timeout', '60',
                     '--file-snapshot', str(snapshot_path)]
    native = subprocess.run(native_command, cwd=ROOT, env=env, capture_output=True, timeout=30)
    expected = {'stdout': b64(native.stdout), 'stderr': b64(native.stderr), 'exit_status': native.returncode}
    (out / 'native.stdout').write_bytes(native.stdout)
    (out / 'native.stderr').write_bytes(native.stderr)
    # Two directory pauses use the installed nested-chdir aggregate cap; each request stays at 60s.
    timed_out = False
    try:
        model = subprocess.run(model_command, cwd=ROOT, env=env, capture_output=True, timeout=180)
        stdout, stderr, exit_status = model.stdout, model.stderr, model.returncode
    except subprocess.TimeoutExpired as error:
        stdout, stderr, exit_status = error.stdout or b'', error.stderr or b'', None
        timed_out = True
    (out / 'model.stdout').write_bytes(stdout)
    (out / 'model.stderr').write_bytes(stderr)
    try:
        actual = json.loads(stdout)
    except (ValueError, UnicodeDecodeError):
        actual = {'status': 'timeout' if timed_out else 'runner_failure'}
    passed = (not timed_out and exit_status == 0 and not stderr
              and actual.get('status') in {'normal', 'php_error', 'static_rejection', 'explicit_exit'}
              and all(actual.get(key) == value for key, value in expected.items()))
    assert before == {name: digest(ROOT / name) for name in watched}, 'inputs changed during run'
    report = {'result': 'pass' if passed else 'timeout' if timed_out else 'fail',
              'exact': int(passed), 'inputs': before, 'source_sha256': digest(source),
              'snapshot_sha256': digest(snapshot_path), 'profile': profile,
              'environment_overrides': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'cwd': str(ROOT.resolve()),
              'model_command': model_command, 'native_command': native_command,
              'model_exit_status': exit_status, 'timeout': timed_out,
              'actual': actual, 'native': expected, 'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'], actual.get('status'), flush=True)
    assert passed, report['result']


if __name__ == '__main__':
    main()
