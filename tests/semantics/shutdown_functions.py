#!/usr/bin/env python3
"""Exact PHP source tuples for cached shutdown registration and ordered callbacks."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from error_handler_run import ENV, ROOT, recorded

CASES = Path(__file__).with_name('shutdown_cases.json')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(selected, native_records):
    if native_records:
        native_records = native_records.resolve()
    rows = json.loads(CASES.read_text())
    assert not selected or set(selected) <= {row['id'] for row in rows}, 'unknown case'
    rows = [row for row in rows if not selected or row['id'] in selected]
    assert rows, 'empty selection'
    out = Path(tempfile.mkdtemp(prefix='shutdown-functions-', dir=ROOT / '.tools'))
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    runtime = ROOT / '.tools/php/bin/php'
    compiler = ROOT / '.tools/spectec/bin/p4spectec'
    identities = {str(path.relative_to(ROOT)): digest(path) for path in [
        runtime, compiler, ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
        ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php-file.so',
        ROOT / 'bin/php-semantics', CASES, Path(__file__).resolve()]}
    print(out, flush=True)
    results = []
    failure = None
    try:
        for row in rows:
            stem = out / row['id']
            source = stem.with_suffix('.php')
            source.write_text(row['source'])
            assert digest(source) == row['source_sha256']
            if native_records:
                native_stem = native_records / row['id']
                native_source = native_stem.with_suffix('.php')
                assert native_source.read_bytes() == source.read_bytes()
                native = json.loads(native_stem.with_suffix('.exit.json').read_text())
                native = dict(native, reused_from=str(native_stem))
            else:
                native_source = source
                native_stem = stem.with_name(stem.name + '-native')
                native = recorded([str(runtime), '-n', *flags, str(source)], native_stem, 30)
            nout = native_stem.with_suffix('.stdout').read_bytes()
            nerr = native_stem.with_suffix('.stderr').read_bytes()
            passed = (not native.get('timeout', False) and native['exit'] == row['exit']
                      and nout == row['stdout'].encode()
                      and nerr == row['stderr'].replace('{file}', str(native_source)).encode())
            result = {'id': row['id'], 'native': native, 'passed': False}
            results.append(result)
            assert passed, 'native expected tuple: ' + row['id']
            model_stem = stem.with_name(stem.name + '-model')
            model = recorded([str(ROOT / 'bin/php-semantics'), str(native_source),
                              '--steps', '100000', '--timeout', '60'], model_stem, 90)
            result['model'] = model
            actual = json.loads(model_stem.with_suffix('.stdout').read_bytes())
            result['observation'] = actual
            passed = (not model['timeout'] and model['exit'] == 0
                      and not model_stem.with_suffix('.stderr').read_bytes()
                      and actual.get('frontend') == 'accepted' and actual.get('checked') == 'program'
                      and actual.get('status') == row['status'] and actual.get('exit_status') == row['exit']
                      and base64.b64decode(actual['stdout']) == nout
                      and base64.b64decode(actual['stderr']) == nerr)
            result['passed'] = passed
            print(row['id'], passed, flush=True)
            assert passed, row['id']
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error)}
    stable = all(digest(ROOT / name) == sha for name, sha in identities.items())
    passed = failure is None and stable and len(results) == len(rows) and all(row['passed'] for row in results)
    report = {'revision': revision, 'identities': identities, 'inputs_stable': stable,
              'environment': {'LC_ALL': ENV['LC_ALL'], 'TZ': ENV['TZ'],
                              'PHP_SPEC_SCRIPT_ENCODING_removed': 'PHP_SPEC_SCRIPT_ENCODING' not in ENV},
              'profile': profile, 'selection': [row['id'] for row in rows],
              'records': results, 'failure': failure, 'passed': passed}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    parser.add_argument('--native-records', type=Path, help='reuse unchanged original-source native preflight')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.case, args.native_records) else 1)
