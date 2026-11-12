#!/usr/bin/env python3
"""Check typed CV verification before an ignored Set result."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from arrayaccess_scalar_reference_callbacks_review import render
from arrayaccess_scalar_reference_callbacks_review_cases import CASES
from error_handler_run import recorded
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    source = out / 'original.php'
    source.write_text(CASES[0]['source'])
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = modules + [Path(__file__), source]
    watched += [ROOT / name for name in (
        'spec/semantics/modules.json', 'tests/semantics/arrayaccess_scalar_reference_callbacks_review.py',
        'tests/semantics/arrayaccess_reference_discard_review.py',
        'tests/semantics/arrayaccess_scalar_reference_callbacks_review_cases.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/error_handler_run.py', 'tests/semantics/numeric_runner.ml',
        'tests/semantics/_build/default/numeric_runner.exe', 'frontend/worker.php', '.tools/php/bin/php',
        '.tools/php-file.so', '_build/default/adapter/main.exe', '.tools/spectec/bin/p4spectec')]
    before = {str(path): digest(path) for path in watched}
    report = {'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'inputs': before, 'mode': 'AL fixture', 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
        'passed': False}
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted']
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        finally:
            adapter.close()
        program = out / 'original.program'
        program.write_text(checked['fixture'])
        fixture = out / 'continuation.watsup'
        text, report['premises'] = render(checked['fixture'], base64.b64encode(bytes(source)).decode())
        fixture.write_text(text)
        report['generated'] = {str(path): digest(path) for path in (program, fixture)}
        report['compiler'] = recorded([str(ROOT / '.tools/spectec/bin/p4spectec'), 'algo',
            *map(str, modules), str(fixture)], out / 'compiler', 120)
        assert report['compiler']['exit'] == 0 and not report['compiler']['timeout']
        assert not (out / 'compiler.stderr').read_bytes()
        assert b'def $main' in (out / 'compiler.stdout').read_bytes()
        report['execution'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
            *map(str, modules), str(fixture)], out / 'state', 180)
        report['passed'] = (report['execution']['exit'] == 0 and not report['execution']['timeout']
            and (out / 'state.stdout').read_bytes().strip() == b'true'
            and not (out / 'state.stderr').read_bytes())
        report['generated_stable'] = report['generated'] == {str(path): digest(path) for path in (program, fixture)}
        report['passed'] = report['passed'] and report['generated_stable']
    finally:
        frontend.close()
        report['inputs_stable'] = before == {str(path): digest(path) for path in watched}
        report['passed'] = report['passed'] and report['inputs_stable']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['premises'], 'pass' if report['passed'] else 'fail')
    assert report['passed']


if __name__ == '__main__':
    main()
