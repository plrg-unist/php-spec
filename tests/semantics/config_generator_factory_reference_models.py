#!/usr/bin/env python3
"""Compare A76 models with the frozen PHP originals without rerunning PHP."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import config_generator_factory_reference_cases as author
import config_generator_factory_reference_review_cases as peer
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
CASES = author.CASES | peer.CASES
EXPECTED = author.EXPECTED | peer.EXPECTED


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', type=Path, action='append', required=True)
    parser.add_argument('--case', action='append', choices=tuple(CASES))
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    affinity = sorted(os.sched_getaffinity(0))
    assert len(affinity) == 1 and affinity[0] in range(1, 6)
    git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, text=True).strip()
    revision = git('rev-parse', 'HEAD')
    assert not git('status', '--porcelain=v1')
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    watched = [Path(__file__), Path(author.__file__), Path(peer.__file__),
               ROOT / 'tests/semantics/error_handler_run.py', ROOT / 'tests/semantics/profile.json',
               ROOT / 'bin/php-semantics', ROOT / '.tools/php/bin/php',
               ROOT / '.tools/php-file.so', ROOT / '_build/default/adapter/main.exe',
               ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
               ROOT / 'spec/semantics/modules.json']
    watched += [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    frozen = {}
    for report_path in args.native_report:
        report_path = report_path.resolve()
        report = json.loads(report_path.read_bytes())
        assert report['scope'] == 'native-only preparation' and report['profile'] == profile
        assert report['revision'] == 'ddc24c3609ad4af88cbc7daf12736010831a4a9d'
        watched.append(report_path)
        for row in report['rows']:
            name = row['id']
            assert name in CASES and name not in frozen and row['passed']
            source = report_path.parent / name / 'source.php'
            stdout = report_path.parent / name / 'native.stdout'
            stderr = report_path.parent / name / 'native.stderr'
            assert source.read_bytes() == CASES[name] and digest(source) == row['source_sha256']
            assert stdout.read_bytes() == EXPECTED[name] and stderr.read_bytes() == b''
            assert row['native']['exit'] == 0 and not row['native']['timeout']
            assert row['native']['interruption'] is None and not row['native']['group_after']
            watched += [source, stdout, stderr]
            frozen[name] = (source, stdout, stderr, report_path)
    assert set(frozen) == set(CASES)
    selection = args.case or list(CASES)
    assert len(selection) == len(set(selection))
    before = {str(path): digest(path) for path in watched}
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    for name in selection:
        source, stdout, stderr, report_path = frozen[name]
        directory = output / name
        directory.mkdir()
        model = recorded([str(ROOT / 'bin/php-semantics'), str(source), '--steps', '100000',
                          '--timeout', '240'], directory / 'model', 270)
        try:
            outcome = json.loads((directory / 'model.stdout').read_bytes())
        except ValueError:
            outcome = {}
        passed = (model['exit'] == 0 and not model['timeout'] and model['interruption'] is None
                  and not model['group_after'] and (directory / 'model.stderr').read_bytes() == b''
                  and outcome.get('frontend') == 'accepted' and outcome.get('checked') == 'program'
                  and outcome.get('status') == 'normal' and outcome.get('exit_status') == 0
                  and outcome.get('reason') is None
                  and base64.b64decode(outcome.get('stdout', '')) == stdout.read_bytes()
                  and base64.b64decode(outcome.get('stderr', '')) == stderr.read_bytes())
        rows.append({'id': name, 'source_sha256': digest(source), 'native_report': str(report_path),
                     'model': model, 'outcome': outcome, 'passed': passed})
        print(name, passed, flush=True)
        if not passed:
            break
    report = {'revision': revision, 'inputs': before, 'inputs_stable': before ==
              {str(path): digest(path) for path in watched}, 'head_stable': revision == git('rev-parse', 'HEAD'),
              'profile': profile, 'affinity': affinity, 'selection': selection, 'rows': rows,
              'agreements': sum(row['passed'] for row in rows)}
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert not git('status', '--porcelain=v1')
    return len(rows) == len(selection) and all(row['passed'] for row in rows) and report['inputs_stable'] and report['head_stable']


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
