#!/usr/bin/env python3
"""Independent original-source checks for scalar integer conversion callbacks."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from error_handler_run import ENV, recorded

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).with_name('integer_operator_warning_review_cases.json')
CASES = {row['id']: row for row in json.loads(CATALOG.read_bytes())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=tuple(CASES))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = args.case or list(CASES)
    out = args.output or Path(tempfile.mkdtemp(prefix='integer-op-review-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', CATALOG, Path(__file__),
               ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/error_handler_run.py',
               ROOT / 'bin/php-semantics', ROOT / 'frontend/worker.php', ROOT / 'frontend/target.php',
               ROOT / 'spec/schema.json', ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
               ROOT / '_build/default/adapter/main.exe',
               ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path.relative_to(ROOT)): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    rows = []
    print(out, flush=True)
    for name in selected:
        directory = out / name
        directory.mkdir()
        case = CASES[name]
        source = directory / 'source.php'
        source.write_bytes(case['source'].encode())
        assert digest(source) == case['source_sha256']
        native = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)], directory / 'native', 30)
        model = recorded([str(ROOT / 'bin/php-semantics'), str(source), '--steps', '100000', '--timeout', '60'], directory / 'model', 90)
        try:
            outcome = json.loads((directory / 'model.stdout').read_bytes())
        except ValueError:
            outcome = {}
        if not isinstance(outcome, dict):
            outcome = {}
        native_expected = ((directory / 'native.stdout').read_bytes() == case['stdout'].encode()
                           and (directory / 'native.stderr').read_bytes() == case['stderr'].encode())
        passed = (native_expected and native['exit'] == model['exit'] == 0
                  and not native['timeout'] and not model['timeout']
                  and not (directory / 'model.stderr').read_bytes()
                  and outcome.get('frontend') == 'accepted' and outcome.get('checked') == 'program'
                  and outcome.get('status') == 'normal' and outcome.get('exit_status') == 0
                  and outcome.get('reason') is None
                  and base64.b64decode(outcome.get('stdout', '')) == (directory / 'native.stdout').read_bytes()
                  and base64.b64decode(outcome.get('stderr', '')) == (directory / 'native.stderr').read_bytes())
        rows.append({'id': name, 'source_sha256': digest(source), 'native': native, 'model': model,
                     'native_expected': native_expected, 'passed': passed})
        print(name, passed, flush=True)
        if not passed:
            break
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'revision': revision, 'inputs': before, 'profile': profile, 'selection': selected, 'rows': rows,
              'environment': {key: ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING')},
              'scope': 'Independent direct defined-CV originals; copied and reference-result producers remain separate.',
              'passed': len(rows) == len(selected) and all(row['passed'] for row in rows)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
