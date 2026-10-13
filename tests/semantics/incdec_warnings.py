#!/usr/bin/env python3
"""Native preparation and checked original-source update agreements."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile

from error_handler_run import ENV, recorded
import incdec_warning_cases as cases

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=tuple(cases.CASES))
    parser.add_argument('--exclude', choices=tuple(cases.CASES), action='append', default=[])
    parser.add_argument('--native-only', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    names = (args.case,) if args.case else tuple(cases.CASES)
    names = tuple(name for name in names if name not in args.exclude)
    if not names:
        parser.error('the selection contains no cases')
    out = args.output or Path(tempfile.mkdtemp(prefix='incdec-warnings-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    print(out, flush=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'bin/php-semantics',
               ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php/bin/php',
               ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/error_handler_run.py',
               Path(__file__), Path(cases.__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path.relative_to(ROOT)): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    rows = []
    for name in names:
        directory = out / name
        directory.mkdir()
        source = directory / 'source.php'
        source.write_bytes(cases.CASES[name])
        native = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)], directory / 'native', 30)
        row = {'id': name, 'source_sha256': digest(source), 'native': native, 'agreement_credit': 0}
        boundary = getattr(cases, 'BOUNDARIES', {}).get(name)
        exit_code = getattr(cases, 'EXIT_CODES', {}).get(name, 0)
        status = getattr(cases, 'STATUSES', {}).get(name, getattr(cases, 'STATUS', 'normal'))
        if boundary is not None:
            row['expected_boundary'] = boundary
        if args.native_only:
            row['passed'] = native['exit'] == exit_code and not native['timeout'] and native['interruption'] is None
        else:
            model = recorded([str(ROOT / 'bin/php-semantics'), str(source), '--steps', '100000', '--timeout', '60'], directory / 'model', 90)
            try:
                outcome = json.loads((directory / 'model.stdout').read_bytes())
            except ValueError:
                outcome = {}
            row['model'] = model
            row['outcome'] = outcome
            ordinary = (native['exit'] == exit_code and model['exit'] == 0 and not native['timeout'] and not model['timeout']
                and native['interruption'] is None and model['interruption'] is None
                and not (directory / 'model.stderr').read_bytes() and outcome.get('frontend') == 'accepted'
                and outcome.get('checked') == 'program' and outcome.get('status') == status
                and outcome.get('exit_status') == native['exit'] and outcome.get('reason') is None
                and base64.b64decode(outcome.get('stdout', '')) == (directory / 'native.stdout').read_bytes()
                and base64.b64decode(outcome.get('stderr', '')) == (directory / 'native.stderr').read_bytes())
            explicit_boundary = (boundary is not None and native['exit'] == exit_code and model['exit'] == 1
                and not native['timeout'] and not model['timeout']
                and native['interruption'] is None and model['interruption'] is None
                and not (directory / 'model.stderr').read_bytes() and outcome.get('frontend') == 'accepted'
                and outcome.get('checked') == 'program' and outcome.get('status') == 'unsupported'
                and outcome.get('reason') == boundary)
            row['passed'] = ordinary if boundary is None else explicit_boundary
            row['agreement_credit'] = int(row['passed'] and boundary is None)
        rows.append(row)
        print(name, row['passed'], flush=True)
        if not row['passed']:
            break
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'inputs': before, 'profile': profile,
        'rows': rows, 'environment': {key: ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING')},
        'selection': names, 'scope': 'native-only preparation' if args.native_only else 'checked original-source agreement'}, indent=2) + '\n')
    return all(row['passed'] for row in rows)


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
