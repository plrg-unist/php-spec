#!/usr/bin/env python3
"""Original-source eval outcomes through the checked parser continuation."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

import static_types as types

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(match):
    catalogue = ROOT / 'tests/semantics/eval_cases.json'
    cases = [row for row in json.loads(catalogue.read_text()) if match in row['id']]
    assert cases, 'no eval cases selected'
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    inputs = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'bin/php-semantics',
              ROOT / 'frontend/worker.php', ROOT / 'frontend/EvalLexer.php',
              ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
              ROOT / '_build/default/adapter/main.exe', ROOT / 'tests/semantics/profile.json',
              Path(__file__), catalogue]
    before = {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    out = Path(tempfile.mkdtemp(prefix='eval-execution-', dir=ROOT / '.tools'))
    print(out, flush=True)
    records = []
    for row in cases:
        directory = out / row['id']
        directory.mkdir()
        source = directory / 'source.php'
        source.write_bytes(row['source'].encode())
        commands = {
            'native': [str(types.PHP), '-n', *types.FLAGS, str(source)],
            'model': [str(ROOT / 'bin/php-semantics'), str(source),
                      '--steps', '100000', '--timeout', '180'],
        }
        processes = {}
        for kind, command in commands.items():
            (directory / (kind + '.command.json')).write_text(json.dumps(command) + '\n')
            result = subprocess.run(command, cwd=directory, env=types.ENV,
                                    capture_output=True, timeout=190)
            (directory / (kind + '.stdout')).write_bytes(result.stdout)
            (directory / (kind + '.stderr')).write_bytes(result.stderr)
            (directory / (kind + '.status.json')).write_text(
                json.dumps({'exit_status': result.returncode}) + '\n')
            processes[kind] = result
        native, model = processes['native'], processes['model']
        try:
            actual = json.loads(model.stdout)
        except json.JSONDecodeError:
            actual = {'status': 'runner_failure'}
        native_shape = ((native.returncode == 0 and not native.stderr) if row['kind'] == 'normal'
                        else ((native.returncode == 0 and bool(native.stderr)) if row['kind'] == 'normal_warning'
                              else (native.returncode != 0 and bool(native.stderr))))
        if row.get('expected_model') == 'unsupported':
            passed = (native_shape and model.returncode == 1 and not model.stderr
                      and actual.get('status') == 'unsupported')
        else:
            passed = (native_shape and model.returncode == 0 and not model.stderr
                      and actual.get('status') == ('normal' if row['kind'] == 'normal_warning' else row['kind'])
                      and actual.get('exit_status') == native.returncode
                      and actual.get('stdout') == base64.b64encode(native.stdout).decode()
                      and actual.get('stderr') == base64.b64encode(native.stderr).decode())
        records.append({'id': row['id'], 'native_kind': row['kind'],
                        'expected_model': row.get('expected_model', 'native_agreement'), 'pass': passed,
                        'actual': actual, 'source_sha256': digest(source),
                        'native_stdout': base64.b64encode(native.stdout).decode(),
                        'native_stderr': base64.b64encode(native.stderr).decode(),
                        'native_exit_status': native.returncode,
                        'model_exit_status': model.returncode})
        (out / 'records.json').write_text(json.dumps(records, indent=2) + '\n')
        print(row['id'], passed, actual.get('status'), flush=True)
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    report = {'result': 'pass' if all(row['pass'] for row in records) else 'fail',
              'selection': match, 'inputs': before, 'records': records,
              'native_agreements': sum(row['pass'] and row['expected_model'] == 'native_agreement'
                                       for row in records),
              'unsupported_controls': sum(row['pass'] and row['expected_model'] == 'unsupported'
                                          for row in records),
              'failures': sum(not row['pass'] for row in records),
              'profile': types.PROFILE, 'env_overrides': {'LC_ALL': 'C', 'TZ': 'UTC'},
              'scope': 'Exact original-source tuples; Unsupported controls are separate.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    raise SystemExit(0 if run(parser.parse_args().match) else 1)
