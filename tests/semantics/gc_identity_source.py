#!/usr/bin/env python3
"""Check produced-right identity receipt authority in AL and strict SL."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'tests/semantics/gc_identity_source.watsup'
MODULES = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
RUNNER = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'


def fingerprint():
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in [*MODULES, ROOT / 'spec/semantics/modules.json',
                         RUNNER, FIXTURE, Path(__file__),
                         ROOT / 'tests/semantics/error_handler_run.py']}


def main():
    out = Path(tempfile.mkdtemp(prefix='gc-identity-source-', dir=ROOT / '.tools'))
    inputs = fingerprint()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'revision': revision, 'inputs': inputs, 'records': [], 'passed': False}
    print(out, flush=True)
    try:
        for mode in ['AL', 'SL']:
            command = [str(RUNNER), *(['--sl'] if mode == 'SL' else []),
                       *map(str, MODULES), str(FIXTURE)]
            stem = out / mode.lower()
            process = recorded(command, stem, 120)
            passed = (process['exit'] == 0 and not process['timeout']
                      and not process['group_after']
                      and stem.with_suffix('.stdout').read_bytes() == b'true\n'
                      and not stem.with_suffix('.stderr').read_bytes())
            report['records'].append({'mode': mode, 'checks': 14,
                                      'process': process, 'passed': passed})
            print(mode, passed, flush=True)
            if not passed:
                break
    finally:
        report['inputs_stable'] = inputs == fingerprint()
        report['head_stable'] = revision == subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['passed'] = (len(report['records']) == 2
                            and all(row['passed'] for row in report['records'])
                            and report['inputs_stable'] and report['head_stable'])
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed'], out


if __name__ == '__main__':
    main()
