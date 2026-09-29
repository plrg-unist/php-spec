#!/usr/bin/env python3
"""Exact static-property source bridges on typed-return and file-context bases."""
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
     b'function f(): string { A::$x=7; return 3; } echo f(),"|",A::$x;', {}),
    ('include-static-file', b'<?php class A { public static string $file="one.php"; } '
     b'include A::$file; echo "|",A::$file;', {'one.php': b'<?php echo "I";'}),
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
    for case_id, source_bytes, files in CASES:
        directory = out / case_id
        directory.mkdir()
        source = directory / 'source.php'
        source.write_bytes(source_bytes)
        for name, content in files.items():
            path = directory / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        model_command = [str(ROOT / 'bin/php-semantics'), str(source), '--timeout', '60']
        if files:
            child = directory / 'one.php'
            snapshot = {'version': 1, 'main': base64.b64encode(os.fsencode(source.resolve())).decode(),
                        'cwd': base64.b64encode(os.fsencode(ROOT.resolve())).decode(),
                        'include_path': base64.b64encode(b'.:').decode(),
                        'entries': [{'caller': base64.b64encode(os.fsencode(source.resolve())).decode(),
                                     'requested': base64.b64encode(b'one.php').decode(),
                                     'status': 'opened',
                                     'resolved': base64.b64encode(os.fsencode(child.resolve())).decode(),
                                     'opened': base64.b64encode(os.fsencode(child.resolve())).decode(),
                                     'source': base64.b64encode(child.read_bytes()).decode()}]}
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
        passed = model.returncode == 0 and not model.stderr and all(
            actual.get(key) == value for key, value in expected.items())
        rows.append({'id': case_id, 'pass': passed, 'source_sha256': digest(source),
                     'files': {name: digest(directory / name) for name in files},
                     'snapshot_sha256': digest(snapshot_path) if files else None,
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
