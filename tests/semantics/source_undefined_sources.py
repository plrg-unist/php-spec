#!/usr/bin/env python3
"""Undefined eval/include operands, frozen null and handler-throw priority."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile

from error_handler_run import recorded

R = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('source-undefined')
CASES = ('eval-mutation', 'file-empty', 'eval-throw', 'eval-nohandler', 'private-state')
b64 = lambda value: base64.b64encode(value).decode()


def source_inputs(name, source, out):
    header = out / 'startup.json'
    header.write_text(json.dumps({'error_reporting': b64(b'30719'), 'include_path': b64(b'.:')}) + '\n')
    args = ['--startup-ini', str(header)]
    if name != 'file-empty':
        return args
    snapshot = {'version': 2, 'main': b64(bytes(source)), 'cwd': b64(bytes(R)),
                'include_path': b64(b'.:'), 'chdir_entries': [], 'entries': [
                    {'caller': b64(bytes(source)), 'requested': '', 'cwd': b64(bytes(R)),
                     'include_path': b64(b'callback-path'), 'status': 'open_failure',
                     'resolved': b64(bytes(source.parent)), 'warning_path': b64(bytes(source.parent)),
                     'stream_error': b64(b'No such file or directory')}]}
    path = out / 'snapshot.json'
    path.write_text(json.dumps(snapshot) + '\n')
    return args + ['--file-snapshot', str(path)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=CASES + ('private-source',))
    args = parser.parse_args()
    selected = (args.case,) if args.case else CASES
    out = Path(tempfile.mkdtemp(prefix='source-undefined-sources-', dir=R / '.tools'))
    print(out, flush=True)
    modules = [R / name for name in json.loads((R / 'spec/semantics/modules.json').read_bytes())]
    watched = [*modules, R / 'spec/semantics/modules.json', R / 'spec/schema.json',
               R / 'bin/php-semantics', R / 'frontend/worker.php', R / 'frontend/target.php',
               R / '_build/default/adapter/main.exe', R / '.tools/php/bin/php', R / '.tools/php-file.so',
               R / 'tests/semantics/profile.json', R / 'tests/semantics/error_handler_run.py',
               Path(__file__), *sorted(SOURCES.glob('*.php'))]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path.relative_to(R)): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    profile = dict(json.loads((R / 'tests/semantics/profile.json').read_bytes()), include_path='.:')
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    rows = []
    for name in selected:
        directory = out / name
        directory.mkdir()
        source = SOURCES / (name + '.php')
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
        rows.append({'id': name, 'profile': profile, 'passed': passed, 'native': native, 'model': model})
        print(name, passed, flush=True)
        if not passed:
            break
    assert before == {str(path.relative_to(R)): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'inputs': before, 'rows': rows,
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent'},
        'selected': selected,
        'scope': 'Four original comparisons and one separately compared line-preserving private-state derivative. Only empty once operations demand file facts. The optional private-source trace original retains its 60s timeout.'}, indent=2) + '\n')
    return len(rows) == len(selected) and all(row['passed'] for row in rows)


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
