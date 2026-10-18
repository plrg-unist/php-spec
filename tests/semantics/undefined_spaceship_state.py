#!/usr/bin/env python3
"""Run focused source-reached spaceship continuations through strict SL."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(cases, checks, prefix, output, extra_inputs=()):
    recorder.ROOT = ROOT
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', ROOT / 'spec/schema.json',
        ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so', ROOT / '_build/default/adapter/main.exe',
        ROOT / 'tests/semantics/_build/default/numeric_runner.exe', ROOT / 'tests/semantics/profile.json',
        ROOT / 'tests/semantics/error_handler_run.py', ROOT / 'tests/semantics/recorded_worker.py',
        *sorted((ROOT / 'tests/semantics').glob('undefined_spaceship*.py')), *extra_inputs]
    before = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'revision': revision, 'inputs': before, 'profile': profile, 'mode': 'SL',
        'cache': False, 'det': True, 'module_count': len(modules), 'records': [], 'passed': False}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d',
            'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], output / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], output / 'adapter')
        for name, source in cases.items():
            directory = output / name
            directory.mkdir()
            source_path = directory / 'main.php'
            source_path.write_bytes(source)
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            assert parsed['accepted'], parsed
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ast'] == parsed['ast']
            conditions = checks(checked['fixture'], source_path, name)
            fixture = directory / 'state.watsup'
            fixture.write_text(prefix + '\ndec $main() : bool\ndef $main() = true\n'
                + ''.join('  -- ' + (condition if condition.startswith('PhpStep:') else 'if ' + condition)
                          + '\n' for condition in conditions))
            process = recorder.recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                '--sl', *map(str, modules), str(fixture)], directory / 'state', 120)
            passed = (process['exit'] == 0 and not process['timeout']
                and (directory / 'state.stdout').read_bytes() == b'true\n'
                and not (directory / 'state.stderr').read_bytes())
            report['records'].append({'id': name, 'source_sha256': sha(source_path),
                'fixture': str(fixture), 'fixture_sha256': sha(fixture),
                'premises': len(conditions), 'process': process, 'passed': passed})
            print(name, passed, len(conditions), flush=True)
            assert passed, name
        report['passed'] = True
    finally:
        try:
            if adapter:
                adapter.close()
        finally:
            if frontend:
                frontend.close()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in watched}
        report['head_stable'] = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['passed'] = report['passed'] and report['inputs_stable'] and report['head_stable']
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']
    return report


if __name__ == '__main__':
    from undefined_spaceship_cases import CASES
    from undefined_spaceship_protocol import PREFIX, checks
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = {name: CASES[name] for name in ('missing-left-constant', 'missing-right-constant', 'missing-left-cv')}
    run(selected, checks, PREFIX, args.output)
