#!/usr/bin/env python3
"""Explicit registered startup bytes, Restore, silence and a finite include."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile

from error_handler_run import recorded

R = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('startup_ini')
b64 = lambda value: base64.b64encode(value).decode()
CASES = [
    ('suffix', 'reporting.php', '  +512junk', '  +512junk', '/startup:.'),
    ('scientific', 'reporting.php', '2e3', '2e3', '/startup:.'),
    ('low32', 'reporting.php', '4294967808', '4294967808', '/startup:.'),
    ('empty', 'reporting.php', '', '', '/startup:.'),
    ('absent', 'reporting.php', None, None, '/startup:.'),
    ('expression', 'reporting.php', 'E_ALL & ~E_DEPRECATED', '22527', '/startup:.'),
    ('restore-silence', 'restore-silence.php', '-2147483136tail', '-2147483136tail', '/startup/first::last'),
    ('fatal-restore', 'fatal-restore.php', '1', '1', '/startup/fatal'),
    ('restore-include', 'include/main.php', '  +512junk', '  +512junk', None),
]


def main():
    out = Path(tempfile.mkdtemp(prefix='startup-ini-', dir=R / '.tools'))
    print(out, flush=True)
    profile = json.loads((R / 'tests/semantics/profile.json').read_text())
    profile.pop('error_reporting')
    profile.pop('include_path')
    modules = [R / name for name in json.loads((R / 'spec/semantics/modules.json').read_text())]
    inputs = [*modules, R / 'bin/php-semantics', R / 'adapter/main.ml',
              R / '_build/default/adapter/main.exe', R / '.tools/php/bin/php',
              R / 'tests/semantics/profile.json', Path(__file__),
              R / 'tests/semantics/error_handler_run.py', *sorted(SOURCES.rglob('*.php'))]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path.relative_to(R)): digest(path) for path in inputs}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    rows = []
    for name, source, native_reporting, registered_reporting, include_path in CASES:
        directory = out / name
        directory.mkdir()
        script = directory / 'main.php'
        script.write_bytes((SOURCES / source).read_bytes())
        model_args = []
        if name == 'restore-include':
            library = directory / 'library'
            library.mkdir()
            target = library / 'selected.php'
            target.write_bytes((SOURCES / 'include/library/selected.php').read_bytes())
            include_path = str(library)
            snapshot = {'version': 2, 'main': b64(bytes(script)), 'cwd': b64(bytes(R)),
                        'include_path': b64(bytes(library)), 'chdir_entries': [],
                        'entries': [{'caller': b64(bytes(script)), 'requested': b64(b'selected.php'),
                                     'cwd': b64(bytes(R)), 'include_path': b64(bytes(library)),
                                     'status': 'opened', 'resolved': b64(bytes(target)),
                                     'opened': b64(bytes(target)), 'source': b64(target.read_bytes())}]}
            snapshot_path = directory / 'snapshot.json'
            snapshot_path.write_text(json.dumps(snapshot) + '\n')
            model_args = ['--file-snapshot', str(snapshot_path)]
        startup = {'error_reporting': None if registered_reporting is None else b64(registered_reporting.encode()),
                   'include_path': b64(include_path.encode())}
        startup_path = directory / 'startup.json'
        startup_path.write_text(json.dumps(startup) + '\n')
        native_profile = dict(profile, include_path=include_path)
        if native_reporting is not None:
            native_profile['error_reporting'] = native_reporting
        flags = [part for key, value in native_profile.items() for part in ('-d', key + '=' + value)]
        native = recorded([str(R / '.tools/php/bin/php'), '-n', *flags, str(script)], directory / 'native', 30)
        model = recorded([str(R / 'bin/php-semantics'), str(script), '--startup-ini', str(startup_path),
                          *model_args, '--steps', '100000', '--timeout', '60'], directory / 'model', 90)
        outcome = json.loads((directory / 'model.stdout').read_bytes())
        passed = (native['exit'] == model['exit'] == 0 and not native['timeout'] and not model['timeout']
                  and not (directory / 'model.stderr').read_bytes()
                  and outcome['frontend'] == 'accepted' and outcome['checked'] == 'program'
                  and outcome['status'] == 'normal' and outcome['exit_status'] == 0
                  and base64.b64decode(outcome['stdout']) == (directory / 'native.stdout').read_bytes()
                  and base64.b64decode(outcome['stderr']) == (directory / 'native.stderr').read_bytes())
        rows.append({'id': name, 'pass': passed, 'native': native, 'model': model,
                     'registered_startup': startup, 'native_profile': native_profile})
        print(name, passed, flush=True)
    assert before == {str(path.relative_to(R)): digest(path) for path in inputs}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    report = {'revision': revision, 'inputs': before, 'rows': rows,
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent'}}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return all(row['pass'] for row in rows)


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
