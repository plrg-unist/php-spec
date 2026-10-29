#!/usr/bin/env python3
"""Check selected API callbacks against frozen pinned-PHP native reports."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded


ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', action='append', required=True, type=Path)
    parser.add_argument('--case', action='append')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--timeout', type=int, default=150)
    args = parser.parse_args()
    affinity = sorted(os.sched_getaffinity(0))
    assert len(affinity) == 1 and affinity[0] in range(1, 6)
    assert not subprocess.check_output(['git', 'status', '--porcelain=v1'], cwd=ROOT)
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    php = ROOT / '.tools/php/bin/php'
    php_sha256 = digest(php)
    watched = [Path(__file__), ROOT / 'tests/semantics/error_handler_run.py',
               ROOT / 'tests/semantics/profile.json', ROOT / 'spec/semantics/modules.json',
               ROOT / 'spec/semantics/30-storage.watsup',
               ROOT / 'spec/semantics/152-throwable-runtime.watsup',
               ROOT / 'spec/semantics/207-error-handler-runtime.watsup',
               ROOT / 'spec/semantics/222-exception-handlers.watsup',
               ROOT / 'spec/semantics/247-handler-callable-consumers.watsup',
               ROOT / 'spec/semantics/270-eager-destructors.watsup',
               ROOT / 'spec/semantics/368-assertions.watsup',
               ROOT / 'spec/semantics/391-output-buffers.watsup',
               ROOT / 'spec/semantics/442-deprecated-api-callbacks.watsup',
               ROOT / 'bin/php-semantics', ROOT / 'frontend/worker.php',
               php, ROOT / '.tools/php-file.so', ROOT / '_build/default/adapter/main.exe']
    watched.extend(args.native_report)
    native_rows = []
    for path in args.native_report:
        report = json.loads(path.read_bytes())
        assert report['passed'] and report['profile'] == profile
        binary_hashes = [value for key, value in report['inputs'].items()
                         if key.endswith('.tools/php/bin/php')]
        assert binary_hashes == [php_sha256]
        for row in report['rows']:
            assert row['passed'] and row['native']['exit'] in (0, 255)
            assert not row['native']['timeout'] and not row['native']['group_after']
            source = Path(row['native']['argv'][-1])
            assert source.is_file() and digest(source) == row['source_sha256']
            watched.append(source)
            native_rows.append((row, source, path))
    assert len({row['id'] for row, _, _ in native_rows}) == len(native_rows)
    if args.case:
        assert len(set(args.case)) == len(args.case)
        assert set(args.case) <= {row['id'] for row, _, _ in native_rows}
        native_rows = [item for item in native_rows if item[0]['id'] in args.case]
    before = {str(path): digest(path) for path in watched}
    output = args.output.resolve()
    output.mkdir(parents=True)
    rows = []
    for native_row, source, report_path in native_rows:
        directory = output / native_row['id']
        directory.mkdir()
        model = recorded([str(ROOT / 'bin/php-semantics'), str(source), '--steps', '100000',
                          '--timeout', str(args.timeout)], directory / 'model', args.timeout + 30)
        try:
            outcome = json.loads((directory / 'model.stdout').read_bytes())
        except ValueError:
            outcome = {}
        passed = (model['exit'] == 0 and not model['timeout'] and model['interruption'] is None
                  and not model['group_after'] and not (directory / 'model.stderr').read_bytes()
                  and outcome.get('frontend') == 'accepted' and outcome.get('checked') == 'program'
                  and outcome.get('status') == ('php_error' if native_row['native']['exit'] == 255 else 'normal')
                  and outcome.get('reason') is None
                  and outcome.get('exit_status') == native_row['native']['exit']
                  and outcome.get('stdout') == native_row['stdout_b64']
                  and outcome.get('stderr') == native_row['stderr_b64'])
        rows.append({'id': native_row['id'], 'native_report': str(report_path),
                     'source_sha256': native_row['source_sha256'], 'model': model,
                     'outcome': outcome, 'passed': passed, 'agreement_credit': int(passed)})
        print(native_row['id'], passed, flush=True)
        if not passed:
            break
    assert before == {str(path): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    assert not subprocess.check_output(['git', 'status', '--porcelain=v1'], cwd=ROOT)
    result = {'phase': 'source-model', 'revision': revision, 'inputs': before, 'profile': profile,
              'environment': {key: ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING')},
              'affinity': affinity, 'selection': [row['id'] for row, _, _ in native_rows],
              'rows': rows, 'passed': len(rows) == len(native_rows) and all(row['passed'] for row in rows)}
    (output / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
    return result['passed']


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
