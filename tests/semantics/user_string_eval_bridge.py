#!/usr/bin/env python3
"""Exact file-to-eval user-string source controls on the installed file provider."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'include-return7': (b"<?php echo include 'one.php';",
                        b'<?php return 7;', 'normal'),
    'file-eval-code': (b"<?php include 'one.php';",
                       b'''<?php class O{function __toString(){return 'echo "E;";';}} eval(new O);''',
                       'normal'),
    'file-eval-callback-throw': (b"<?php include 'one.php';",
                                 b'''<?php class O{function __toString(){throw new Exception("x");}} eval(new O);''',
                                 'php_error'),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def b64(data):
    return base64.b64encode(data).decode()


def main():
    out = Path(tempfile.mkdtemp(prefix='user-string-eval-bridge-', dir=ROOT / '.tools'))
    modules = [ROOT / name for name in json.loads(
        (ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json',
               ROOT / 'bin/php-semantics', ROOT / 'frontend/worker.php',
               ROOT / 'frontend/FileLexer.php', ROOT / 'frontend/EvalLexer.php',
               ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php/bin/php',
               ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/profile.json',
               Path(__file__)]
    before = {str(path.relative_to(ROOT)): digest(path) for path in watched}
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [part for key, value in profile.items()
             for part in ('-d', key + '=' + value)]
    env = dict(os.environ, LC_ALL='C', TZ='UTC')
    records = []
    for case_id, (main_source, child_source, status) in CASES.items():
        directory = out / case_id
        directory.mkdir()
        main_path = directory / 'main.php'
        child_path = directory / 'one.php'
        main_path.write_bytes(main_source)
        child_path.write_bytes(child_source)
        entry = {'caller': b64(os.fsencode(main_path.resolve())),
                 'requested': b64(b'one.php'), 'status': 'opened',
                 'resolved': b64(os.fsencode(child_path.resolve())),
                 'opened': b64(os.fsencode(child_path.resolve())),
                 'source': b64(child_source)}
        snapshot = {'version': 1, 'main': b64(os.fsencode(main_path.resolve())),
                    'cwd': b64(os.fsencode(ROOT.resolve())),
                    'include_path': b64(b'.:'), 'entries': [entry]}
        snapshot_path = directory / 'snapshot.json'
        snapshot_path.write_text(json.dumps(snapshot, sort_keys=True) + '\n')
        native = subprocess.run([ROOT / '.tools/php/bin/php', '-n', *flags, main_path],
                                cwd=ROOT, env=env, capture_output=True, timeout=45)
        model = subprocess.run([ROOT / 'bin/php-semantics', main_path,
                                '--file-snapshot', snapshot_path,
                                '--steps', '100000', '--timeout', '60'],
                               cwd=ROOT, env=env, capture_output=True, timeout=90)
        for name, result in [('native', native), ('model', model)]:
            (directory / (name + '.stdout')).write_bytes(result.stdout)
            (directory / (name + '.stderr')).write_bytes(result.stderr)
        actual = json.loads(model.stdout)
        passed = (model.returncode == 0 and not model.stderr
                  and actual.get('status') == status
                  and actual.get('exit_status') == native.returncode
                  and base64.b64decode(actual['stdout']) == native.stdout
                  and base64.b64decode(actual['stderr']) == native.stderr)
        records.append({'id': case_id, 'pass': passed,
                        'main_sha256': digest(main_path),
                        'child_sha256': digest(child_path),
                        'snapshot_sha256': digest(snapshot_path),
                        'model_status': actual.get('status')})
        print(case_id, passed, actual.get('status'), flush=True)
    stable = before == {str(path.relative_to(ROOT)): digest(path)
                        for path in watched}
    report = {'result': 'pass' if stable and all(row['pass'] for row in records)
              else 'fail', 'stable': stable, 'inputs': before,
              'records': records, 'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
