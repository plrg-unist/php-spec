#!/usr/bin/env python3
"""Live precision, source-time capture, deferred AST conversion and raw Restore."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile

from error_handler_run import recorded

R = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('precision')
b64 = lambda value: base64.b64encode(value).decode()
CASES = [
    ('settings-default', 'settings.php', '14', '14', None),
    ('settings-prefix', 'settings.php', '3junk', '3junk', None),
    ('settings-zero', 'settings.php', '0', '0', None),
    ('settings-shortest', 'settings.php', '-1', '-1', None),
    ('settings-wide', 'settings.php', '4294967296', '4294967296', None),
    ('settings-rejected-startup', 'settings.php', '-2', '14', None),
    ('runtime-consumers', 'consumers.php', '14', '14', None),
    ('included-parser-point', 'include-point.php', '14', '14', 'included.php'),
    ('option-callback', 'main.php', '5junk', '5junk', None),
    ('parser-point', 'parser-point.php', '5junk', '5junk', None),
    ('comparison-trace', 'comparison-trace.php', '5junk', '5junk', None),
    ('literal-callback', 'literal-callback.php', '5junk', '5junk', None),
    ('included-compiler-point', 'compiler-point.php', '5junk', '5junk', 'compiled-child.php'),
    ('compiled-names', 'compiled-names.php', '5junk', '5junk', None),
    ('global-deferred-concat', 'global-constant.php', '5junk', '5junk', None),
    ('class-deferred-concat', 'deferred-concat.php', '5junk', '5junk', None),
]


def main(selected=None):
    out = Path(tempfile.mkdtemp(prefix='precision-sources-', dir=R / '.tools'))
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
    for name, filename, precision, registered, child_name in CASES:
        if selected and name not in selected:
            continue
        directory = out / name
        directory.mkdir()
        source = SOURCES / filename
        startup = {'precision': b64(registered.encode())}
        startup_path = directory / 'startup.json'
        startup_path.write_text(json.dumps(startup) + '\n')
        model_args = ['--startup-ini', str(startup_path)]
        if child_name:
            child = SOURCES / child_name
            snapshot = {'version': 2, 'main': b64(bytes(source)), 'cwd': b64(bytes(R)),
                        'include_path': b64(b'.:'), 'chdir_entries': [], 'entries': [
                            {'caller': b64(bytes(source)), 'requested': b64(bytes(child)),
                             'cwd': b64(bytes(R)), 'include_path': b64(b'.:'), 'status': 'opened',
                             'resolved': b64(bytes(child)), 'opened': b64(bytes(child)), 'source': b64(child.read_bytes())}]}
            snapshot_path = directory / 'snapshot.json'
            snapshot_path.write_text(json.dumps(snapshot) + '\n')
            model_args += ['--file-snapshot', str(snapshot_path)]
        native_profile = dict(profile, precision=precision)
        flags = [arg for key, value in native_profile.items() for arg in ('-d', key + '=' + value)]
        native = recorded([str(R / '.tools/php/bin/php'), '-n', *flags, str(source)], directory / 'native', 30)
        model = recorded([str(R / 'bin/php-semantics'), str(source), *model_args,
                          '--steps', '100000', '--timeout', '60'], directory / 'model', 90)
        outcome = json.loads((directory / 'model.stdout').read_bytes())
        passed = (native['exit'] == 0 and model['exit'] == 0 and not native['timeout'] and not model['timeout']
                  and not (directory / 'model.stderr').read_bytes() and outcome.get('frontend') == 'accepted'
                  and outcome.get('checked') == 'program' and outcome.get('status') == 'normal'
                  and outcome.get('exit_status') == 0 and outcome.get('reason') is None
                  and base64.b64decode(outcome['stdout']) == (directory / 'native.stdout').read_bytes()
                  and base64.b64decode(outcome['stderr']) == (directory / 'native.stderr').read_bytes())
        rows.append({'id': name, 'source': filename, 'passed': passed, 'profile': native_profile,
                     'registered_startup': startup, 'native': native, 'model': model})
        print(name, passed, flush=True)
    assert inputs == {str(path.relative_to(R)): sha(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'inputs': inputs, 'rows': rows,
        'scope': 'Sixteen source/profile comparisons across eleven main programs; complete precision/configuration remains open.',
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent'}}, indent=2) + '\n')
    return all(row['passed'] for row in rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=[case[0] for case in CASES])
    args = parser.parse_args()
    raise SystemExit(0 if main(args.case) else 1)
