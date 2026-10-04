#!/usr/bin/env python3
"""Live display decoding, raw Restore, ordered events and finite include output."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile

from error_handler_run import recorded

R = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('display_errors')
b64 = lambda value: base64.b64encode(value).decode()
CASES = [
    ('mixed', 'main.php', 'StDeRr', 0),
    ('stdout', 'main.php', 'stdout', 0),
    ('wrap-stderr', 'main.php', '258tail', 0),
    ('wrap-off', 'main.php', '256', 0),
    ('scientific-prefix', 'main.php', '2e3', 0),
    ('fallback', 'main.php', '3', 0),
    ('empty', 'main.php', '', 0),
    ('fatal-stdout', 'fatal.php', 'stdout', 255),
    ('fatal-off', 'fatal.php', '0', 255),
    ('callback-routing', 'routing.php', 'StDeRr', 0),
    ('included-routing', 'include/main.php', 'StDeRr', 0),
]


def main():
    out = Path(tempfile.mkdtemp(prefix='display-errors-', dir=R / '.tools'))
    print(out, flush=True)
    profile = json.loads((R / 'tests/semantics/profile.json').read_text())
    modules = [R / name for name in json.loads((R / 'spec/semantics/modules.json').read_text())]
    inputs = [*modules, R / 'adapter/main.ml', R / 'bin/php-semantics',
              R / '_build/default/adapter/main.exe', R / '.tools/php/bin/php',
              R / 'tests/semantics/profile.json', R / 'tests/semantics/error_handler_run.py',
              Path(__file__), *sorted(SOURCES.rglob('*.php'))]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path.relative_to(R)): digest(path) for path in inputs}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    rows = []
    for name, source, display, expected_exit in CASES:
        directory = out / name
        directory.mkdir()
        script = directory / 'main.php'
        script.write_bytes((SOURCES / source).read_bytes())
        startup = {'display_errors': b64(display.encode())}
        if name == 'callback-routing':
            startup.update(error_reporting=b64(b'30719'), include_path=b64(b'.:'))
        startup_path = directory / 'startup.json'
        startup_path.write_text(json.dumps(startup) + '\n')
        model_args = []
        if name == 'included-routing':
            child = directory / 'child.php'
            child.write_bytes((SOURCES / 'include/child.php').read_bytes())
            snapshot = {'version': 2, 'main': b64(bytes(script)), 'cwd': b64(bytes(R)),
                        'include_path': b64(b'.:'), 'chdir_entries': [], 'entries': [
                            {'caller': b64(bytes(script)), 'requested': b64(b'child.php'),
                             'cwd': b64(bytes(R)), 'include_path': b64(b'.:'), 'status': 'opened',
                             'resolved': b64(bytes(child)), 'opened': b64(bytes(child)), 'source': b64(child.read_bytes())}]}
            snapshot_path = directory / 'snapshot.json'
            snapshot_path.write_text(json.dumps(snapshot) + '\n')
            model_args = ['--file-snapshot', str(snapshot_path)]
        selected = dict(profile, display_errors=display)
        flags = [part for key, value in selected.items() for part in ('-d', key + '=' + value)]
        native = recorded([str(R / '.tools/php/bin/php'), '-n', *flags, str(script)], directory / 'native', 30)
        model = recorded([str(R / 'bin/php-semantics'), str(script), '--startup-ini', str(startup_path),
                          *model_args, '--steps', '100000', '--timeout', '60'], directory / 'model', 90)
        outcome = json.loads((directory / 'model.stdout').read_bytes())
        passed = (native['exit'] == expected_exit and model['exit'] == 0 and not native['timeout'] and not model['timeout']
                  and not (directory / 'model.stderr').read_bytes()
                  and outcome['frontend'] == 'accepted' and outcome['checked'] == 'program'
                  and outcome['status'] == ('normal' if expected_exit == 0 else 'php_error')
                  and outcome['exit_status'] == expected_exit
                  and base64.b64decode(outcome['stdout']) == (directory / 'native.stdout').read_bytes()
                  and base64.b64decode(outcome['stderr']) == (directory / 'native.stderr').read_bytes())
        rows.append({'id': name, 'pass': passed, 'native': native, 'model': model,
                     'registered_startup': startup, 'profile': selected})
        print(name, passed, flush=True)
    assert before == {str(path.relative_to(R)): digest(path) for path in inputs}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    report = {'revision': revision, 'inputs': before, 'rows': rows,
              'scope': 'Ordinary diagnostic routing; shutdown/fatal freeze waits for accepted lifecycle composition.',
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent'}}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return all(row['pass'] for row in rows)


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
