#!/usr/bin/env python3
"""Reject explicit empty SET lists before compiling their bodies."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import recorded
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('property_hook_parameter_list')
b64 = lambda data: base64.b64encode(data).decode()
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--native', type=Path, help='reuse a completed native-only run')
    parser.add_argument('--native-only', action='store_true')
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    assert not (args.native and args.native_only)
    cases = json.loads((SOURCE / 'cases.json').read_text())
    hashes = json.loads((SOURCE / 'hashes.json').read_text())
    assert hashes == {name: sha(SOURCE / name) for name in hashes}
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), SOURCE / 'cases.json', SOURCE / 'hashes.json',
        *(SOURCE / name for name in hashes), *modules, *(ROOT / path for path in (
            'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'adapter/main.ml',
            'frontend/worker.php', 'frontend/SourcePrinter.php', 'frontend/FileLexer.php',
            'bin/php-semantics', '.tools/php/bin/php', '.tools/php-file.so',
            '_build/default/adapter/main.exe', 'tests/semantics/profile.json',
            'tests/semantics/static_types.py', 'tests/semantics/error_handler_run.py'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    profile = {**types.PROFILE, 'include_path': '.:'}
    flags = [flag for key, value in profile.items() for flag in ('-d', key + '=' + value)]
    prior = json.loads((args.native / 'report.json').read_text()) if args.native else None
    if prior:
        assert prior['passed'] and prior['native_only'] and prior['profile'] == profile
        assert prior['inputs']['.tools/php/bin/php'] == sha(types.PHP)
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'profile': profile,
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'native_only': args.native_only,
        'native_replayed': False, 'saved_native': str(args.native) if args.native else None,
        'records': [], 'source_agreements': 0, 'passed': False}
    try:
        for name, case in cases.items():
            path = SOURCE / case['source']; target = out / name; target.mkdir()
            row = {'id': name, 'source_sha256': sha(path)}; report['records'].append(row)
            if prior:
                old = next(row for row in prior['records'] if row['id'] == name)
                assert old['source_sha256'] == row['source_sha256'] and old['passed']
                native = old['native']; native_root = args.native / name
            else:
                native = recorded([str(types.PHP), '-n', *flags, str(path)], target / 'native', 15)
                native_root = target
            row['native'] = native
            stdout = (native_root / 'native.stdout').read_bytes(); stderr = (native_root / 'native.stderr').read_bytes()
            expected = b'Fatal error: ' + case['message'].encode() + b' in ' + bytes(path) + b' on line ' + str(case['line']).encode() + b'\nStack trace:\n#0 {main}\n'
            assert native['exit'] == case['exit_status'] and not native['timeout'] and not native['group_after']
            assert not stdout and stderr == expected, (name, stdout, stderr, expected)
            if args.native_only:
                row['passed'] = True
                continue
            startup = {'error_reporting': b64(b'30719'), 'include_path': b64(b'.:')}
            (target / 'startup.json').write_text(json.dumps(startup) + '\n')
            model = recorded([str(ROOT / 'bin/php-semantics'), str(path), '--startup-ini',
                str(target / 'startup.json'), '--steps', '100000', '--timeout', '120'], target / 'model', 140)
            row['model'] = model
            outcome = json.loads((target / 'model.stdout').read_bytes()); row['status'] = outcome.get('status')
            row['passed'] = (model['exit'] == 0 and not model['timeout'] and not model['group_after']
                and not (target / 'model.stderr').read_bytes() and outcome.get('status') == 'static_rejection'
                and outcome.get('frontend') == 'accepted' and outcome.get('checked') == 'program'
                and outcome.get('reason') is None and outcome.get('exit_status') == native['exit']
                and outcome.get('stdout') == b64(stdout) and outcome.get('stderr') == b64(stderr)
                and outcome.get('diagnostic') == {'class': 'CompileError', 'message': b64(case['message'].encode()), 'line': case['line']})
            report['source_agreements'] += int(row['passed'])
            print(name, 'pass' if row['passed'] else 'fail', flush=True)
            assert row['passed'], outcome
        report['passed'] = len(report['records']) == len(cases) and all(row['passed'] for row in report['records'])
    finally:
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in paths}
        report['passed'] = report['passed'] and report['head_stable'] and report['inputs_stable']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']


if __name__ == '__main__': main()
