#!/usr/bin/env python3
"""Original-source interpolation cardinality, callbacks and ownership."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile

from error_handler_run import recorded

R = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('interpolation')
CASES = ('scalars', 'cv-mutation', 'warning', 'fast-throw', 'multiline',
         'undefined-cardinality', 'two-line-core', 'owner-cardinality', 'undefined-array-owner')
b64 = lambda value: base64.b64encode(value).decode()


def main():
    out = Path(tempfile.mkdtemp(prefix='interpolation-sources-', dir=R / '.tools')); print(out, flush=True)
    modules = [R / name for name in json.loads((R / 'spec/semantics/modules.json').read_bytes())]
    watched = [*modules, R / 'spec/semantics/modules.json', R / 'bin/php-semantics', R / 'adapter/main.ml',
               R / '_build/default/adapter/main.exe', R / '.tools/php/bin/php', R / 'tests/semantics/profile.json',
               R / 'tests/semantics/error_handler_run.py', Path(__file__), *sorted(SOURCES.glob('*.php'))]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path.relative_to(R)): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    profile = json.loads((R / 'tests/semantics/profile.json').read_bytes())
    rows = []
    for name in CASES:
        directory = out / name; directory.mkdir()
        source = SOURCES / (name + '.php')
        selected = dict(profile); model_args = []
        if name in {'owner-cardinality', 'undefined-array-owner'}:
            selected['include_path'] = '.:'
            startup = {key: b64(value.encode()) for key, value in
                       (('error_reporting', '30719'), ('include_path', '.:'), ('display_errors', 'stderr'))}
            path = directory / 'startup.json'; path.write_text(json.dumps(startup) + '\n')
            model_args = ['--startup-ini', str(path)]
        flags = [arg for key, value in selected.items() for arg in ('-d', key + '=' + value)]
        native = recorded([str(R / '.tools/php/bin/php'), '-n', *flags, str(source)], directory / 'native', 30)
        model = recorded([str(R / 'bin/php-semantics'), str(source), *model_args,
                          '--steps', '100000', '--timeout', '60'], directory / 'model', 90)
        outcome = json.loads((directory / 'model.stdout').read_bytes())
        passed = (native['exit'] == 0 and model['exit'] == 0 and not native['timeout'] and not model['timeout']
                  and not (directory / 'model.stderr').read_bytes() and outcome['frontend'] == 'accepted'
                  and outcome['checked'] == 'program' and outcome['status'] == 'normal' and outcome['exit_status'] == 0
                  and outcome.get('reason') is None
                  and base64.b64decode(outcome['stdout']) == (directory / 'native.stdout').read_bytes()
                  and base64.b64decode(outcome['stderr']) == (directory / 'native.stderr').read_bytes())
        rows.append({'id': name, 'pass': passed, 'profile': selected, 'native': native, 'model': model})
        print(name, passed, flush=True)
    assert before == {str(path.relative_to(R)): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'inputs': before, 'rows': rows,
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent'},
        'scope': 'Nine distinct interpolation sources; non-object cast line pin stays native-only in the ledger.'}, indent=2) + '\n')
    return all(row['pass'] for row in rows)


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
