#!/usr/bin/env python3
"""Precision changes during genuine suspended eval compilation."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile

from error_handler_run import recorded

R = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('suspended_precision')
b64 = lambda value: base64.b64encode(value).decode()
CASES = [
    ('folds', 'folds.php', 'normal'),
    ('throw', 'throw.php', 'normal'),
    ('exit', 'exit.php', 'explicit_exit'),
    ('nested', 'nested.php', 'normal'),
    ('arrays', 'arrays.php', 'normal'),
    ('child-warning', 'child-warning.php', 'normal'),
    ('chronology', 'main.php', 'normal'),
    ('compiled-names', 'names.php', 'normal'),
    ('bound-trait', 'trait-bound.php', 'normal'),
    ('trait-key', 'trait-key.php', 'normal'),
]


def main(selected=None):
    out = Path(tempfile.mkdtemp(prefix='suspended-precision-sources-', dir=R / '.tools'))
    print(out, flush=True)
    modules = [R / name for name in json.loads((R / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, R / 'spec/semantics/modules.json', R / 'bin/php-semantics',
               R / 'adapter/main.ml', R / '_build/default/adapter/main.exe', R / '.tools/php/bin/php',
               R / '.tools/php-file.so', R / 'tests/semantics/profile.json',
               R / 'tests/semantics/error_handler_run.py', Path(__file__), *sorted(SOURCES.rglob('*.php'))]
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    inputs = {str(path.relative_to(R)): sha(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    profile = json.loads((R / 'tests/semantics/profile.json').read_text())
    rows = []
    for name, filename, status in CASES:
        if selected and name not in selected:
            continue
        directory = out / name
        directory.mkdir()
        source = SOURCES / filename
        startup = {'precision': b64(b'5junk')}
        startup_path = directory / 'startup.json'
        startup_path.write_text(json.dumps(startup) + '\n')
        model_args = ['--startup-ini', str(startup_path)]
        native_profile = dict(profile, precision='5junk')
        flags = [arg for key, value in native_profile.items() for arg in ('-d', key + '=' + value)]
        native = recorded([str(R / '.tools/php/bin/php'), '-n', *flags, str(source)], directory / 'native', 30)
        model = recorded([str(R / 'bin/php-semantics'), str(source), *model_args,
                          '--steps', '100000', '--timeout', '60'], directory / 'model', 90)
        outcome = json.loads((directory / 'model.stdout').read_bytes())
        passed = (native['exit'] == 0 and model['exit'] == 0 and not native['timeout'] and not model['timeout']
                  and not (directory / 'model.stderr').read_bytes() and outcome.get('frontend') == 'accepted'
                  and outcome.get('checked') == 'program' and outcome.get('status') == status
                  and outcome.get('exit_status') == 0 and outcome.get('reason') is None
                  and base64.b64decode(outcome['stdout']) == (directory / 'native.stdout').read_bytes()
                  and base64.b64decode(outcome['stderr']) == (directory / 'native.stderr').read_bytes())
        rows.append({'id': name, 'source': filename, 'passed': passed, 'profile': native_profile,
                     'registered_startup': startup, 'native': native, 'model': model})
        print(name, passed, flush=True)
    assert inputs == {str(path.relative_to(R)): sha(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'inputs': inputs, 'rows': rows,
        'scope': 'Ten source comparisons for later eval compiler precision, parser capture, pending abrupt callbacks, nested eval and retained array/class data; wider configuration remains open.',
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent'}}, indent=2) + '\n')
    return all(row['passed'] for row in rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=[case[0] for case in CASES])
    args = parser.parse_args()
    raise SystemExit(0 if main(args.case) else 1)
