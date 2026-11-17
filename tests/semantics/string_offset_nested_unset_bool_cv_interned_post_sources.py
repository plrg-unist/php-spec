#!/usr/bin/env python3
"""Quiet INTERNED poststring originals; native bytes execute once."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import ENV, recorded
import string_offset_nested_unset_bool_cv_interned_post_cases as cases

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--native-baseline', type=Path)
    parser.add_argument('--baseline', action='store_true')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    paths = [Path(__file__), Path(cases.__file__), ROOT / '.tools/php/bin/php',
             ROOT / '_build/default/adapter/main.exe', ROOT / 'bin/php-semantics',
             ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/error_handler_run.py',
             ROOT / 'spec/semantics/modules.json', *[ROOT / name for name in cases.WATCHED]]
    before = {str(path.relative_to(ROOT)): digest(path) for path in paths}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    saved_rows = {}
    if args.native_baseline:
        saved = json.loads((args.native_baseline / 'report.json').read_bytes())
        assert saved['profile'] == profile
        assert saved['inputs']['.tools/php/bin/php'] == before['.tools/php/bin/php']
        saved_rows = {row['id']: row for row in saved['rows']}
        assert set(saved_rows) == set(cases.CASES)
    rows = []
    for name, source_bytes in cases.CASES.items():
        out = args.output / name
        out.mkdir()
        reused = name in saved_rows
        if reused:
            native = saved_rows[name]['native']
            source = Path(native['argv'][-1])
            assert source.read_bytes() == source_bytes
        else:
            source = out / 'source.php'
            source.write_bytes(source_bytes)
            native = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)], out / 'native', 30)
        native_stdout = source.with_name('native.stdout').read_bytes()
        native_stderr = source.with_name('native.stderr').read_bytes()
        native_ok = (native['exit'] == 0 and not native['timeout'] and native['interruption'] is None
                     and not native['group_after'] and native_stdout == cases.OUTPUTS[name]
                     and not native_stderr)
        native_paths = [source, source.with_name('native.stdout'), source.with_name('native.stderr')]
        if args.native_baseline:
            native_paths.append(args.native_baseline / 'report.json')
        native_before = {str(path): digest(path) for path in native_paths}
        model = recorded([str(ROOT / 'bin/php-semantics'), str(source), '--steps', '100000',
                          '--timeout', '90'], out / 'model', 120)
        outcome = json.loads((out / 'model.stdout').read_bytes())
        common = (native_ok and not model['timeout'] and model['interruption'] is None
                  and not model['group_after'] and not (out / 'model.stderr').read_bytes()
                  and outcome.get('frontend') == 'accepted' and outcome.get('checked') == 'program')
        if args.baseline:
            passed = (common and model['exit'] == 1 and outcome['status'] == 'unsupported'
                      and outcome['reason'] == 'post-warning Boolean CV conversion'
                      and base64.b64decode(outcome['stdout']) == b'H:2:String offset cast occurred;'
                      and not base64.b64decode(outcome['stderr']))
        else:
            passed = (common and model['exit'] == 0 and outcome['status'] == 'normal'
                      and outcome['exit_status'] == 0 and outcome['reason'] is None
                      and base64.b64decode(outcome['stdout']) == native_stdout
                      and base64.b64decode(outcome['stderr']) == native_stderr)
        assert native_before == {str(path): digest(path) for path in native_paths}
        rows.append({'id': name, 'native_inputs': native_before, 'source': str(source), 'source_sha256': digest(source),
                     'native': native, 'native_reused': reused,
                     'native_stdout': str(source.with_name('native.stdout')),
                     'native_stderr': str(source.with_name('native.stderr')),
                     'model': model, 'outcome': outcome, 'passed': passed,
                     'agreement_credit': int(passed and not args.baseline)})
        print(name, passed, outcome['status'], outcome.get('reason'), flush=True)
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in paths}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (args.output / 'report.json').write_text(json.dumps({
        'revision': revision, 'inputs': before, 'profile': profile,
        'environment': {key: ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING')},
        'scope': 'fresh quiet-INTERNED baseline Unsupported4/source0' if args.baseline else 'production-SL quiet INTERNED poststring originals',
        'native_input_report': str(args.native_baseline / 'report.json') if args.native_baseline else None,
        'rows': rows}, indent=2) + '\n')
    return all(row['passed'] for row in rows)


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
