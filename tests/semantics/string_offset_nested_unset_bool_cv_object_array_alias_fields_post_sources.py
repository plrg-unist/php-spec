#!/usr/bin/env python3
"""Capture native originals; both complete checked-source bridges are mandatory."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import string_offset_nested_unset_bool_cv_empty_array_post_sources as baseline
import string_offset_nested_unset_bool_cv_object_array_alias_fields_post_cases as cases

ROOT = baseline.ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--native-baseline', type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    paths = [Path(__file__), Path(cases.__file__), Path(baseline.__file__),
        ROOT / '.tools/php/bin/php', ROOT / '_build/default/adapter/main.exe',
        ROOT / 'bin/php-semantics', ROOT / 'tests/semantics/profile.json',
        ROOT / 'tests/semantics/error_handler_run.py', ROOT / 'spec/semantics/modules.json',
        *[ROOT / path for path in cases.WATCHED]]
    before = {str(path.relative_to(ROOT)): digest(path) for path in paths}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    saved_rows = {}
    if args.native_baseline:
        saved = json.loads((args.native_baseline / 'report.json').read_bytes())
        assert saved['profile'] == profile
        assert saved['inputs']['.tools/php/bin/php'] == before['.tools/php/bin/php']
        saved_rows = {row['id']: row for row in saved['rows']}
        assert set(saved_rows) == set(cases.CASES)
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    rows = []
    for name, source_bytes in cases.CASES.items():
        out = args.output / name
        out.mkdir()
        if saved_rows:
            native = saved_rows[name]['native']
            source = Path(native['argv'][-1])
            assert source.is_absolute() and source.read_bytes() == source_bytes
        else:
            source = out / 'source.php'
            source.write_bytes(source_bytes)
            native = baseline.recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)], out / 'native', 30)
        assert native['argv'] == [str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)]
        assert native['cwd'] == str(ROOT)
        stdout, stderr = source.with_name('native.stdout'), source.with_name('native.stderr')
        native_inputs = {str(path): digest(path) for path in (source, stdout, stderr)}
        passed = (native['exit'] == 0 and not native['timeout'] and native['interruption'] is None
            and native['group_after'] == [] and stdout.read_bytes() == cases.OUTPUTS[name]
            and stderr.read_bytes() == cases.stderr(name, source))
        assert native_inputs == {path: digest(Path(path)) for path in native_inputs}
        rows.append({'id': name, 'source': str(source), 'source_sha256': digest(source),
            'native_inputs': native_inputs, 'native': native, 'native_reused': bool(saved_rows),
            'native_stdout': str(stdout), 'native_stderr': str(stderr),
            'model': None, 'outcome': None, 'awaiting_bridge': True,
            'passed': passed, 'pass_scope': 'native capture only; both checked-source budget bridges required',
            'agreement_credit': 0})
        print(name, passed, 'native-only/source0', flush=True)
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in paths}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (args.output / 'report.json').write_text(json.dumps({'revision': revision, 'inputs': before,
        'profile': profile, 'environment': {key: baseline.ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING')},
        'scope': 'Native2 capture only; both post public-CLI models UNRUN/source0. Make separately requires both complete checked-source/native budget bridges and all author/reviewer core/guard parts.',
        'native_input_report': str(args.native_baseline / 'report.json') if args.native_baseline else None,
        'rows': rows}, indent=2) + '\n')
    return all(row['passed'] for row in rows)

if __name__ == '__main__':
    if '--baseline' in sys.argv:
        baseline.cases = cases
        main = baseline.main
    raise SystemExit(0 if main() else 1)
