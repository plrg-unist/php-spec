#!/usr/bin/env python3
"""Original-source Throwable comparisons and separate unsupported controls."""
from pathlib import Path
import base64
import hashlib
import json
import os
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    cases = json.loads((ROOT / 'tests/semantics/throwable_cases.json').read_text())
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    watched = [*modules, 'spec/semantics/modules.json', 'bin/php-semantics',
               'tests/semantics/profile.json', 'tests/semantics/throwable_cases.json',
               'tests/semantics/throwable_expressions.py', '.tools/php/bin/php',
               '_build/default/adapter/main.exe']
    before = {name: digest(ROOT / name) for name in watched}
    out = Path(tempfile.mkdtemp(prefix='throwable-expressions-', dir=ROOT / '.tools'))
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    env = dict(os.environ, LC_ALL='C', TZ='UTC')
    rows = []
    for case in cases:
        directory = out / case['id']
        directory.mkdir()
        source = directory / 'source.php'
        source.write_bytes(case['source'].encode())
        native_command = [str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)]
        model_command = [str(ROOT / 'bin/php-semantics'), str(source), '--timeout', '60']
        native = subprocess.run(native_command, cwd=directory, env=env, capture_output=True, timeout=65)
        model = subprocess.run(model_command, cwd=directory, env=env, capture_output=True, timeout=65)
        for name, process in [('native', native), ('model', model)]:
            (directory / (name + '.stdout')).write_bytes(process.stdout)
            (directory / (name + '.stderr')).write_bytes(process.stderr)
            (directory / (name + '.status')).write_text(str(process.returncode) + '\n')
        actual = json.loads(model.stdout)
        expected = {'stdout': base64.b64encode(native.stdout).decode(),
                    'stderr': base64.b64encode(native.stderr).decode(), 'exit_status': native.returncode}
        if case['kind'] == 'agreement':
            passed = model.returncode == 0 and not model.stderr and all(actual.get(k) == v for k, v in expected.items())
        else:
            passed = model.returncode == 1 and not model.stderr and actual.get('status') == 'unsupported'
        rows.append({'id': case['id'], 'kind': case['kind'], 'pass': passed,
                     'source_sha256': digest(source), 'actual': actual, 'native': expected,
                     'native_command': native_command, 'model_command': model_command})
        print(case['id'], passed, actual.get('status'), flush=True)
    assert before == {name: digest(ROOT / name) for name in watched}, 'inputs changed'
    report = {'result': 'pass' if all(row['pass'] for row in rows) else 'fail',
              'agreements': sum(row['kind'] == 'agreement' for row in rows),
              'unsupported_controls': sum(row['kind'] == 'unsupported' for row in rows),
              'inputs': before, 'profile': profile, 'cwd': 'each retained source directory',
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'records': rows, 'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    (ROOT / 'coverage/semantics/throwable-source.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    assert report['result'] == 'pass'


if __name__ == '__main__':
    main()
