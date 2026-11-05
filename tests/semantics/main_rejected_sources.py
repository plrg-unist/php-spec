#!/usr/bin/env python3
"""Original main-source parser failures, warning prefixes and startup masks."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('main_rejections')
ORACLE = 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
MESSAGE = b'declare(encoding=...) ignored because Zend multibyte feature is turned off by settings'
b64 = lambda data: base64.b64encode(data).decode()
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def expected(case, source=SOURCE):
    path = source / case['source']; records = []
    reporting = int(case['reporting'])
    if reporting & 128:
        records += [b'Warning: ' + MESSAGE + b' in ' + bytes(path) + b' on line '
                    + str(line).encode() + b'\n' for line in case['warning_lines']]
    if reporting & (4 if case['kind'] == 'ParseError' else 64):
        records.append((b'Parse error: ' if case['kind'] == 'ParseError' else b'Fatal error: ')
                       + case['message'].encode() + b' in ' + bytes(path) + b' on line '
                       + str(case['line']).encode() + b'\n')
    if case['display'] == 'stderr':
        return b'', b''.join(records)
    if case['display'] == '1':
        return b''.join(b'\n' + record for record in records), b''
    assert case['display'] == '0'
    return b'', b''


def main(source=SOURCE, extra_inputs=()):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--select', help='comma-separated profile IDs')
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    cases = json.loads((source / 'cases.json').read_text())
    if args.select:
        names = args.select.split(',')
        assert len(names) == len(set(names)) and set(names) <= {case['id'] for case in cases}
        cases = [case for case in cases if case['id'] in names]
    assert cases and sha(ROOT / '.tools/php/bin/php') == ORACLE
    hashes = json.loads((source / 'hashes.json').read_text())
    assert hashes == {name: sha(source / name) for name in hashes}
    watched = [Path(__file__), *extra_inputs, *(ROOT / name for name in (
        'adapter/main.ml', 'bin/php-semantics', 'spec/php.watsup', 'spec/schema.json',
        'spec/semantics/modules.json', 'spec/semantics/446-rejected-main-source.watsup',
        'spec/semantics/445-rejected-source-headers.watsup', 'spec/semantics/101-error-suppression.watsup',
        'spec/semantics/225-startup-ini.watsup', 'spec/semantics/237-display-errors.watsup',
        'spec/semantics/272-live-precision.watsup', 'spec/semantics/368-assertions.watsup',
        'frontend/worker.php', 'frontend/RejectedHeaderParser.php', 'frontend/FileLexer.php',
        '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
        'tests/semantics/profile.json', 'tests/semantics/error_handler_run.py')),
        source / 'hashes.json', *(source / name for name in hashes)]
    inputs = {str(path): sha(path) for path in watched}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text()); profile['include_path'] = '.:'
    report = {'head': head, 'inputs': inputs, 'profile': profile, 'oracle_sha256': ORACLE,
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'selected': [case['id'] for case in cases],
              'records': [], 'agreements': 0, 'passed': False}
    try:
        for case in cases:
            dest = out / case['id']; dest.mkdir(); path = source / case['source']
            flags = {**profile, 'error_reporting': case['reporting'], 'display_errors': case['display']}
            argv = [flag for key, value in flags.items() for flag in ('-d', key + '=' + value)]
            stdout, stderr = expected(case, source)
            row = {'id': case['id'], 'profile': flags, 'source_sha256': sha(path)}
            report['records'].append(row)
            native = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *argv, str(path)], dest / 'native', 10)
            row['native'] = native
            assert native['exit'] == 255 and not native['timeout'] and not native['group_after']
            assert (dest / 'native.stdout').read_bytes() == stdout and (dest / 'native.stderr').read_bytes() == stderr
            startup = {'error_reporting': b64(case['reporting'].encode()), 'include_path': b64(b'.:'),
                       'display_errors': b64(case['display'].encode())}
            (dest / 'startup.json').write_text(json.dumps(startup) + '\n')
            model = recorded([str(ROOT / 'bin/php-semantics'), str(path), '--startup-ini',
                str(dest / 'startup.json'), '--steps', '0', '--timeout', '120'], dest / 'model', 140)
            row['model'] = model
            outcome = json.loads((dest / 'model.stdout').read_bytes())
            row['status'] = outcome.get('status'); row['reason'] = outcome.get('reason')
            row['passed'] = (model['exit'] == 0 and not model['timeout'] and not model['group_after']
                and not (dest / 'model.stderr').read_bytes() and outcome.get('status') == 'php_error'
                and outcome.get('frontend') == 'rejected' and outcome.get('checked') == 'source_rejection'
                and outcome.get('reason') is None and outcome.get('exit_status') == 255
                and outcome.get('stdout') == b64(stdout) and outcome.get('stderr') == b64(stderr)
                and outcome.get('diagnostic') == {'class': case['kind'], 'message': b64(case['message'].encode()), 'line': case['line']})
            report['agreements'] += int(row['passed'])
            print(case['id'], 'pass' if row['passed'] else 'fail', flush=True)
            assert row['passed'], row
        report['passed'] = report['agreements'] == len(cases)
    finally:
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = inputs == {str(path): sha(path) for path in watched}
        report['passed'] = report['passed'] and report['head_stable'] and report['inputs_stable']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']


if __name__ == '__main__': main()
