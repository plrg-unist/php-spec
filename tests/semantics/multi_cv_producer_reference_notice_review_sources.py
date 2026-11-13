"""Compare immutable duplicate-CV originals using their once-only native records."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import error_handler_run as recorder
from multi_cv_producer_reference_notice_review_cases import CASES, HASHES

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--case', action='append', default=[])
    parser.add_argument('--baseline', action='store_true')
    args = parser.parse_args()
    provenance = args.native_report.resolve()
    native = json.loads(provenance.read_bytes())
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    runtime = digest(ROOT / '.tools/php/bin/php')
    assert native['passed'] and native['mode'] == 'native-only'
    assert native['inputs_stable'] and native['head_stable'] and native['profile'] == profile
    assert runtime == native['runtime']['binary_sha256'] == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    rows = {row['id']: row for row in native['records']}
    assert rows.keys() == CASES.keys() and set(args.case) <= CASES.keys()
    selected = args.case or list(CASES)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    paths = modules + [ROOT / name for name in (
        'spec/semantics/modules.json', 'tests/semantics/profile.json', 'bin/php-semantics',
        '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so',
        'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py',
        'tests/semantics/error_handler_run.py',
        'tests/semantics/multi_cv_producer_reference_notice_review_cases.py')]
    paths += [Path(__file__), provenance]
    for name in selected:
        row = rows[name]
        source = Path(row['source'])
        assert row['passed'] and row['cwd'] == str(ROOT)
        assert source.read_bytes() == CASES[name] and digest(source) == row['source_sha256'] == HASHES[name]
        assert row['process']['exit'] == 0 and not row['process']['timeout'] and not row['process']['group_after']
        assert source.with_name('native.stdout').read_bytes() == row['stdout'].encode()
        assert source.with_name('native.stderr').read_bytes() == row['stderr'].encode() == b''
        paths += [source, source.with_name('native.stdout'), source.with_name('native.stderr')]
    fingerprints = lambda: {str(path): digest(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    out = args.output.resolve()
    out.mkdir(parents=True)
    print(out, flush=True)
    records = []
    for name in selected:
        directory = out / name
        directory.mkdir()
        row = rows[name]
        recorder.ROOT = Path(row['cwd'])
        process = recorder.recorded([str(ROOT / 'bin/php-semantics'), row['source'],
            '--steps', '100000', '--timeout', '180'], directory / 'model', 195)
        try:
            outcome = json.loads((directory / 'model.stdout').read_bytes())
        except ValueError:
            outcome = {}
        passed = (not process['timeout'] and not process['group_after']
            and not (directory / 'model.stderr').read_bytes()
            and outcome.get('frontend') == 'accepted' and outcome.get('checked') == 'program')
        if args.baseline:
            passed = (passed and process['exit'] == 1 and outcome.get('status') == 'unsupported'
                and outcome.get('exit_status') is None and outcome.get('diagnostic') is None
                and outcome.get('reason') == 'error-handler ingress requires a producer continuation'
                and base64.b64decode(outcome.get('stdout', '')) == b'J;M:5:13;'
                and base64.b64decode(outcome.get('stderr', '')) == b'')
        else:
            passed = (passed and process['exit'] == 0 and outcome.get('status') == 'normal'
                and outcome.get('exit_status') == 0 and outcome.get('reason') is None
                and outcome.get('diagnostic') is None
                and base64.b64decode(outcome.get('stdout', '')) == row['stdout'].encode()
                and base64.b64decode(outcome.get('stderr', '')) == b'')
        records.append({'id': name, 'process': process, 'outcome': outcome, 'passed': passed,
                        'source_sha256': row['source_sha256'], 'native_reused': True})
        print(name, passed, outcome.get('status'), flush=True)
        if not passed:
            break
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = stable and head_stable and len(records) == len(selected) and all(row['passed'] for row in records)
    report = {'revision': revision, 'inputs': before, 'input_count': len(before),
        'inputs_stable': stable, 'head_stable': head_stable, 'module_count': len(modules),
        'mode': 'SL/cache=false/det=true', 'profile': profile, 'runtime_sha256': runtime,
        'compiler': {'spectec_commit': 'da36ac3c434cd291940293a63da64544307730a3', 'ocaml': '5.1.0'},
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING_removed': True},
        'native_provenance': str(provenance), 'expected_unsupported_control': args.baseline,
        'source_agreements': sum(row['passed'] for row in records) if not args.baseline else 0,
        'records': records, 'passed': passed}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
