#!/usr/bin/env python3
"""Stringable file operands, failed-open callbacks and compiler-stop shutdown."""
from pathlib import Path
import base64
import hashlib
import json
import shutil
import subprocess
import tempfile

from error_handler_run import recorded

R = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('file_operands')
b64 = lambda value: base64.b64encode(value).decode()
CASES = [(name, 'convert/' + name + '.php') for name in ('kinds', 'mutation', 'owner', 'throw', 'bad', 'multiline')]
CASES += [('live', 'warning/live.php'), ('warning-throw', 'warning/throw.php'),
          ('required', 'warning/required.php'), ('exit', 'warning/exit.php'), ('fatal', 'warning/fatal.php')]
CASES += [('late-once', 'once/core-observer.php'), ('throw-require', 'throw-require.php'), ('shutdown', 'shutdown/main.php')]


def snapshot(name, source):
    if name in {'throw', 'bad', 'throw-require'}:
        return None
    directory = source.parent
    cwd = bytes(R)
    entries, changes = [], []

    def opened(requested, target, path=b'.:', current=cwd):
        entries.append({'caller': b64(bytes(source)), 'requested': b64(requested), 'cwd': b64(current),
                        'include_path': b64(path), 'status': 'opened', 'resolved': b64(bytes(target)),
                        'opened': b64(bytes(target)), 'source': b64(target.read_bytes())})

    def missing(requested, path=b'.:'):
        entries.append({'caller': b64(bytes(source)), 'requested': b64(requested), 'cwd': b64(cwd),
                        'include_path': b64(path), 'status': 'missing', 'stream_error': b64(b'No such file or directory')})

    def changed(current, target):
        changes.append({'cwd': b64(current), 'requested': b64(bytes(target)), 'status': 'success', 'next_cwd': b64(bytes(target))})

    if name == 'kinds':
        opened(b'shared.php', directory / 'shared.php')
    elif name == 'mutation':
        changed(cwd, directory / 'cwd')
        opened(b'target.php', directory / 'late/target.php', bytes(directory / 'late'), bytes(directory / 'cwd'))
    elif name == 'owner':
        opened(b'owned.php', directory / 'owned.php')
    elif name == 'multiline':
        missing(b'missing-multiline.php')
    elif name == 'live':
        missing(b'warning-missing.php', b'provider-path')
        opened(b'nested-target.php', directory / 'nested-target.php', b'after-first')
    elif name == 'warning-throw':
        missing(b'throw-missing.php')
        missing(b'throw-again.php', b'thrown-path')
    elif name in {'required', 'exit', 'fatal'}:
        missing((name + '-missing.php').encode())
    elif name == 'late-once':
        opened(b'piece.php', directory / 'first/piece.php', bytes(directory / 'first'))
        changed(cwd, directory / 'second')
        changed(bytes(directory / 'second'), directory / 'second')
        opened(b'piece.php', directory / 'second/piece.php', b'.', bytes(directory / 'second'))
    elif name == 'shutdown':
        missing(b'shutdown-missing.php')
        opened(bytes(directory / 'compile-bad.php'), directory / 'compile-bad.php', b'callback-path')
    else:
        raise AssertionError(name)
    return {'version': 2, 'main': b64(bytes(source)), 'cwd': b64(cwd), 'include_path': b64(b'.:'),
            'entries': entries, 'chdir_entries': changes}


def main():
    out = Path(tempfile.mkdtemp(prefix='file-operands-', dir=R / '.tools')); print(out, flush=True)
    modules = [R / name for name in json.loads((R / 'spec/semantics/modules.json').read_bytes())]
    watched = [*modules, R / 'spec/semantics/modules.json', R / 'bin/php-semantics', R / 'adapter/main.ml',
               R / '_build/default/adapter/main.exe', R / '.tools/php/bin/php', R / 'tests/semantics/profile.json',
               R / 'tests/semantics/error_handler_run.py', Path(__file__), *sorted(SOURCES.rglob('*.php'))]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path.relative_to(R)): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    profile = dict(json.loads((R / 'tests/semantics/profile.json').read_bytes()), include_path='.:')
    rows = []
    for name, relative in CASES:
        directory = out / name; directory.mkdir()
        shutil.copytree(SOURCES, directory / 'sources')
        source = directory / 'sources' / relative
        selected = dict(profile)
        startup = {'error_reporting': b64(b'30719'), 'include_path': b64(b'.:')}
        if name in {'late-once', 'throw-require'}:
            selected['display_errors'] = 'StDeRr'; startup['display_errors'] = b64(b'StDeRr')
        (directory / 'startup.json').write_text(json.dumps(startup) + '\n')
        facts = snapshot(name, source)
        model_args = []
        if facts is not None:
            (directory / 'snapshot.json').write_text(json.dumps(facts) + '\n')
            model_args = ['--file-snapshot', str(directory / 'snapshot.json')]
        flags = [arg for key, value in selected.items() for arg in ('-d', key + '=' + value)]
        native = recorded([str(R / '.tools/php/bin/php'), '-n', *flags, str(source)], directory / 'native', 30)
        model = recorded([str(R / 'bin/php-semantics'), str(source), '--startup-ini', str(directory / 'startup.json'),
                          *model_args, '--steps', '100000', '--timeout', '60'], directory / 'model', 90)
        outcome = json.loads((directory / 'model.stdout').read_bytes())
        expected = 'explicit_exit' if name == 'exit' else 'php_error' if name in {'fatal', 'shutdown'} else 'normal'
        expected_exit = 255 if expected == 'php_error' else 0
        passed = (native['exit'] == expected_exit and model['exit'] == 0 and not native['timeout'] and not model['timeout']
                  and not (directory / 'model.stderr').read_bytes() and outcome['frontend'] == 'accepted'
                  and outcome['checked'] == 'program' and outcome['status'] == expected and outcome['exit_status'] == expected_exit
                  and base64.b64decode(outcome['stdout']) == (directory / 'native.stdout').read_bytes()
                  and base64.b64decode(outcome['stderr']) == (directory / 'native.stderr').read_bytes())
        rows.append({'id': name, 'pass': passed, 'native': native, 'model': model, 'startup': startup, 'profile': selected})
        print(name, passed, flush=True)
    assert before == {str(path.relative_to(R)): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'inputs': before, 'rows': rows,
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent'},
        'scope': 'Fourteen distinct maintained sources; original count/interpolation observers retain zero agreement in the ledger.'}, indent=2) + '\n')
    return all(row['pass'] for row in rows)


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
