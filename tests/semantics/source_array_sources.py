#!/usr/bin/env python3
"""Array eval/include conversion, handler effects and frozen source bytes."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile

from error_handler_run import recorded

R = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('source-arrays')
CASES = ('routing', 'throw', 'eval', 'core-observer')
b64 = lambda value: base64.b64encode(value).decode()


def source_inputs(name, source, out):
    args = []
    if name != 'core-observer':
        path = out / 'startup.json'
        path.write_text(json.dumps({'error_reporting': b64(b'30719'), 'include_path': b64(b'.:')}) + '\n')
        args += ['--startup-ini', str(path)]
    if name not in ('routing', 'core-observer'):
        return args
    early, late = source.parent / 'early/Array', source.parent / 'late/Array'
    snapshot = {'version': 2, 'main': b64(bytes(source)), 'cwd': b64(bytes(R)),
                'include_path': b64(b'.:'), 'entries': [], 'chdir_entries': []}
    for child in ((late,) if name == 'routing' else (late, early)):
        cwd = child.parent if name == 'routing' else R
        path = b'.' if name == 'routing' else bytes(child.parent)
        snapshot['entries'].append({'caller': b64(bytes(source)), 'requested': b64(b'Array'),
            'cwd': b64(bytes(cwd)), 'include_path': b64(path), 'status': 'opened',
            'resolved': b64(bytes(child)), 'opened': b64(bytes(child)), 'source': b64(child.read_bytes())})
    if name == 'routing':
        for cwd in (R, late.parent):
            snapshot['chdir_entries'].append({'cwd': b64(bytes(cwd)), 'requested': b64(bytes(late.parent)),
                                            'status': 'success', 'next_cwd': b64(bytes(late.parent))})
    path = out / 'snapshot.json'
    path.write_text(json.dumps(snapshot) + '\n')
    return args + ['--file-snapshot', str(path)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=CASES)
    args = parser.parse_args()
    selected = (args.case,) if args.case else CASES
    out = Path(tempfile.mkdtemp(prefix='source-array-sources-', dir=R / '.tools')); print(out, flush=True)
    modules = [R / name for name in json.loads((R / 'spec/semantics/modules.json').read_bytes())]
    watched = [*modules, R / 'spec/semantics/modules.json', R / 'spec/schema.json',
               R / 'bin/php-semantics', R / 'frontend/worker.php', R / 'frontend/target.php',
               R / '_build/default/adapter/main.exe', R / '.tools/php/bin/php', R / '.tools/php-file.so',
               R / 'tests/semantics/profile.json', R / 'tests/semantics/error_handler_run.py',
               Path(__file__), *sorted(SOURCES.rglob('*.php')),
               *sorted(SOURCES.rglob('Array'))]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path.relative_to(R)): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    profile = json.loads((R / 'tests/semantics/profile.json').read_bytes())
    rows = []
    for name in selected:
        directory = out / name; directory.mkdir()
        source = (SOURCES / 'core' if name == 'core-observer' else SOURCES) / (name + '.php')
        selected_profile = profile if name == 'core-observer' else dict(profile, include_path='.:')
        flags = [arg for key, value in selected_profile.items() for arg in ('-d', key + '=' + value)]
        model_args = source_inputs(name, source, directory)
        native = recorded([str(R / '.tools/php/bin/php'), '-n', *flags, str(source)], directory / 'native', 30)
        model = recorded([str(R / 'bin/php-semantics'), str(source), *model_args,
                          '--steps', '100000', '--timeout', '60'], directory / 'model', 90)
        outcome = json.loads((directory / 'model.stdout').read_bytes())
        passed = (native['exit'] == model['exit'] == 0 and not native['timeout'] and not model['timeout']
                  and not (directory / 'model.stderr').read_bytes() and outcome.get('frontend') == 'accepted'
                  and outcome.get('checked') == 'program' and outcome.get('status') == 'normal'
                  and outcome.get('exit_status') == 0 and outcome.get('reason') is None
                  and base64.b64decode(outcome['stdout']) == (directory / 'native.stdout').read_bytes()
                  and base64.b64decode(outcome['stderr']) == (directory / 'native.stderr').read_bytes())
        rows.append({'id': name, 'profile': selected_profile, 'passed': passed, 'native': native, 'model': model})
        print(name, passed, flush=True)
        if not passed:
            break
    assert before == {str(path.relative_to(R)): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'inputs': before, 'rows': rows,
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent'},
        'scope': 'Four destructor-free originals. lifetime-pending.php awaits accepted eager release.'}, indent=2) + '\n')
    return len(rows) == len(selected) and all(row['passed'] for row in rows)


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
