#!/usr/bin/env python3
"""Capture both natives; compare normal CLI and require the pending state bridge."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import string_offset_nested_unset_bool_cv_empty_array_post_sources as runner
import string_offset_nested_unset_bool_cv_object_array_fields_post_cases as cases

ROOT = runner.ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--native-baseline', type=Path)
    parser.add_argument('--normal-baseline', type=Path)
    args = parser.parse_args()
    assert not args.normal_baseline or args.native_baseline
    args.output.mkdir(parents=True, exist_ok=False)
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    paths = [Path(__file__), Path(cases.__file__), Path(runner.__file__), ROOT / '.tools/php/bin/php',
        ROOT / '_build/default/adapter/main.exe', ROOT / 'bin/php-semantics',
        ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/error_handler_run.py',
        ROOT / 'spec/semantics/modules.json', *[ROOT / path for path in cases.WATCHED]]
    before = {str(path.relative_to(ROOT)): digest(path) for path in paths}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    saved_rows = {}
    if args.native_baseline:
        saved = json.loads((args.native_baseline / 'report.json').read_bytes())
        assert saved['profile'] == profile
        assert saved['inputs']['.tools/php/bin/php'] == before['.tools/php/bin/php']
        saved_rows = {row['id']: row for row in saved['rows']}
        assert set(saved_rows) == set(cases.CASES)
    normal, retained_inputs = None, {}
    if args.normal_baseline:
        retained = json.loads(args.normal_baseline.read_bytes())
        assert retained['profile'] == profile
        own = str(Path(__file__).relative_to(ROOT))
        assert all(value == before[path] for path, value in retained['inputs'].items() if path != own)
        normal = next(row for row in retained['rows'] if not cases.FACTS[row['id']]['throwing'])
        assert normal['passed'] and normal['agreement_credit'] == 1
        assert normal['model']['cap_seconds'] == 150
        raw = args.normal_baseline.parent / normal['id'] / 'model.stdout'
        err = raw.with_name('model.stderr')
        assert json.loads(raw.read_bytes()) == normal['outcome'] and not err.read_bytes()
        retained_inputs = {str(path): digest(path) for path in (args.normal_baseline, raw, err)}
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    rows = []
    for name, source_bytes in cases.CASES.items():
        out = args.output / name
        out.mkdir()
        if saved_rows:
            native = saved_rows[name]['native']
            source = Path(native['argv'][-1])
            assert source.read_bytes() == source_bytes
        else:
            source = out / 'source.php'
            source.write_bytes(source_bytes)
            native = runner.recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)], out / 'native', 30)
        native_stdout, native_stderr = source.with_name('native.stdout'), source.with_name('native.stderr')
        native_inputs = {str(path): digest(path) for path in (source, native_stdout, native_stderr)}
        native_ok = (native['exit'] == 0 and not native['timeout'] and native['interruption'] is None
            and native['group_after'] == [] and native_stdout.read_bytes() == cases.OUTPUTS[name]
            and native_stderr.read_bytes() == cases.stderr(name, source))
        model = outcome = None
        pending = cases.FACTS[name]['throwing']
        argv = [str(ROOT / 'bin/php-semantics'), str(source), '--steps', '100000', '--timeout', '120']
        if not pending:
            if normal is not None:
                model, outcome = normal['model'], normal['outcome']
                assert model['argv'] == argv and model['cwd'] == str(ROOT)
            else:
                model = runner.recorded(argv, out / 'model', 150)
                outcome = json.loads((out / 'model.stdout').read_bytes())
            model_ok = (model['exit'] == 0 and not model['timeout'] and model['interruption'] is None
                and model['group_after'] == [] and outcome.get('frontend') == 'accepted'
                and outcome.get('checked') == 'program' and outcome['status'] == 'normal'
                and outcome['exit_status'] == 0 and outcome['reason'] is None
                and base64.b64decode(outcome['stdout']) == native_stdout.read_bytes()
                and base64.b64decode(outcome['stderr']) == native_stderr.read_bytes())
            if normal is None:
                model_ok = model_ok and not (out / 'model.stderr').read_bytes()
        else:
            model_ok = True  # Native collection only; Make requires both current pending bridges.
        assert native_inputs == {path: digest(Path(path)) for path in native_inputs}
        rows.append({'id': name, 'source': str(source), 'source_sha256': digest(source),
            'native_inputs': native_inputs, 'native': native, 'native_reused': bool(saved_rows),
            'native_stdout': str(native_stdout), 'native_stderr': str(native_stderr),
            'model': model, 'outcome': outcome, 'model_reused': normal is not None and not pending,
            'awaiting_source_bridge': pending, 'passed': native_ok and model_ok,
            'pass_scope': 'native capture only; mandatory pending postfixture bridge' if pending else 'normal public source comparison',
            'agreement_credit': int(native_ok and model_ok and not pending)})
        print(name, native_ok and model_ok, 'native-only' if pending else 'normal', flush=True)
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in paths}
    assert retained_inputs == {path: digest(Path(path)) for path in retained_inputs}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'revision': revision, 'inputs': before, 'profile': profile,
        'environment': {key: runner.ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING')},
        'scope': 'Native2 capture and normal public120/outer150 comparison; pending model UNRUN/source0 until required author and independent core bridges.',
        'native_input_report': str(args.native_baseline / 'report.json') if args.native_baseline else None,
        'normal_reused_from': str(args.normal_baseline) if args.normal_baseline else None,
        'retained_model_inputs': retained_inputs, 'rows': rows}
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return all(row['passed'] for row in rows)


if __name__ == '__main__':
    if '--baseline' in sys.argv:
        runner.cases = cases
        raise SystemExit(0 if runner.main() else 1)
    raise SystemExit(0 if main() else 1)
