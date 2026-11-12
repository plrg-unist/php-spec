#!/usr/bin/env python3
"""Checked source agreements, optionally retaining exact prior native originals."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
import string_offset_reference_alias_keeper_cases as cases

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', type=Path, action='append', default=[])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    prior, originals = {}, []
    for report_path in args.native_report:
        report_path = report_path.resolve()
        report = json.loads(report_path.read_bytes())
        assert report['profile'] == profile
        assert [value for path, value in report['inputs'].items()
                if path.endswith('.tools/php/bin/php')] == [digest(ROOT / '.tools/php/bin/php')]
        originals.append(report_path)
        for row in report['rows']:
            assert row['id'] in cases.CASES and row['id'] not in prior
            native = row['native']
            source = Path(native['argv'][-1])
            assert source.is_absolute() and source.read_bytes() == cases.CASES[row['id']]
            assert digest(source) == row['source_sha256']
            assert native['cwd'] == str(ROOT) and native['exit'] == 0
            assert not native['timeout'] and native['interruption'] is None and native['group_after'] == []
            prior[row['id']] = (source, dict(native, reused_from=str(report_path)))
            originals += [source, source.with_name('native.stdout'), source.with_name('native.stderr')]
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    watched = [*modules, *originals, Path(__file__), Path(cases.__file__),
               *[ROOT / name for name in ('spec/semantics/modules.json', 'spec/schema.json',
                   'bin/php-semantics', '_build/default/adapter/main.exe', '.tools/php/bin/php',
                   '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php',
                   'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/profile.json',
                   'tests/semantics/error_handler_run.py', 'semantics-reference-inputs.json')]]
    before = {str(path): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    assert not ENV.get('LD_PRELOAD') and not ENV.get('PHP_SPEC_REQUEST_CLOCK')
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    rows = []
    for index, (name, source_bytes) in enumerate(cases.CASES.items()):
        directory = out / name
        directory.mkdir()
        if name in prior:
            source, native = prior[name]
        else:
            source = directory / 'source.php'
            source.write_bytes(source_bytes)
            native = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)], directory / 'native', 30)
            watched += [source, directory / 'native.stdout', directory / 'native.stderr']
            before.update({str(path): digest(path) for path in watched if str(path) not in before})
        native_stem = source.parent
        native_ok = (native['exit'] == 0 and not native['timeout'] and native['interruption'] is None
                     and native['group_after'] == [] and (native_stem / 'native.stdout').read_bytes() == cases.OUTPUTS[index]
                     and not (native_stem / 'native.stderr').read_bytes())
        model = recorded([str(ROOT / 'bin/php-semantics'), str(source), '--steps', '100000', '--timeout', '90'], directory / 'model', 120)
        try:
            outcome = json.loads((directory / 'model.stdout').read_bytes())
        except ValueError:
            outcome = {}
        passed = (native_ok and model['exit'] == 0 and not model['timeout'] and model['interruption'] is None
                  and model['group_after'] == [] and not (directory / 'model.stderr').read_bytes()
                  and outcome.get('frontend') == 'accepted' and outcome.get('checked') == 'program'
                  and outcome.get('status') == 'normal' and outcome.get('exit_status') == 0
                  and outcome.get('reason') is None and base64.b64decode(outcome.get('stdout', '')) == cases.OUTPUTS[index]
                  and base64.b64decode(outcome.get('stderr', '')) == b'')
        rows.append({'id': name, 'source_sha256': digest(source), 'native': native, 'model': model,
                     'outcome': outcome, 'passed': passed, 'agreement_credit': int(passed)})
        print(name, passed, flush=True)
        if not passed:
            break
    assert before == {str(path): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = len(rows) == len(cases.CASES) and all(row['passed'] for row in rows)
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'mode': 'production SL',
        'module_entries': len(modules), 'selection': list(cases.CASES), 'rows': rows, 'inputs': before,
        'profile': profile, 'environment': {key: ENV.get(key) for key in ('LC_ALL', 'TZ',
            'PHP_SPEC_SCRIPT_ENCODING', 'LD_PRELOAD', 'PHP_SPEC_REQUEST_CLOCK')},
        'source_credit': sum(row['agreement_credit'] for row in rows), 'passed': passed}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
