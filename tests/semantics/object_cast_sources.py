#!/usr/bin/env python3
"""Non-object casts, table sharing, callback operands and live-owner companions."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile

from error_handler_run import recorded

R = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('object_casts')
CASES = ('scalars', 'keys', 'singletons', 'shared-clone', 'nan-throw',
         'nan-locations', 'typed-alias', 'nul-callback', 'undefined-array',
         'iterator-reference', 'iterator-retained-table', 'nan-live-short', 'two-line-cast')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', choices=CASES)
    args = parser.parse_args()
    selected = (args.case,) if args.case else CASES
    out = Path(tempfile.mkdtemp(prefix='object-cast-sources-', dir=R / '.tools')); print(out, flush=True)
    modules = [R / name for name in json.loads((R / 'spec/semantics/modules.json').read_bytes())]
    watched = [*modules, R / 'spec/semantics/modules.json', R / 'bin/php-semantics',
               R / '_build/default/adapter/main.exe', R / '.tools/php/bin/php',
               R / 'tests/semantics/profile.json', R / 'tests/semantics/error_handler_run.py',
               Path(__file__), *[SOURCES / (name + '.php') for name in selected]]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path.relative_to(R)): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    profile = json.loads((R / 'tests/semantics/profile.json').read_bytes())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    rows = []
    for name in selected:
        directory = out / name; directory.mkdir()
        source = SOURCES / (name + '.php')
        native = recorded([str(R / '.tools/php/bin/php'), '-n', *flags, str(source)], directory / 'native', 30)
        model = recorded([str(R / 'bin/php-semantics'), str(source), '--steps', '100000', '--timeout', '60'],
                         directory / 'model', 90)
        outcome = json.loads((directory / 'model.stdout').read_bytes())
        passed = (native['exit'] == 0 and model['exit'] == 0 and not native['timeout'] and not model['timeout']
                  and not (directory / 'model.stderr').read_bytes() and outcome.get('frontend') == 'accepted'
                  and outcome.get('checked') == 'program' and outcome.get('status') == 'normal'
                  and outcome.get('exit_status') == 0 and outcome.get('reason') is None
                  and base64.b64decode(outcome['stdout']) == (directory / 'native.stdout').read_bytes()
                  and base64.b64decode(outcome['stderr']) == (directory / 'native.stderr').read_bytes())
        rows.append({'id': name, 'passed': passed, 'native': native, 'model': model})
        print(name, passed, flush=True)
    assert before == {str(path.relative_to(R)): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'inputs': before, 'profile': profile,
        'rows': rows, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent'},
        'excluded_originals': 'nan-borrowed/iterator-table expired locations and nan-borrowed-live timeout retain zero full agreement.'}, indent=2) + '\n')
    return all(row['passed'] for row in rows)


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
