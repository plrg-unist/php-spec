#!/usr/bin/env python3
"""Paused finalizer phase, previous-chain and suspended-frame ownership checks."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker
from finally_protocol_cases import CASES, PREFIX

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(match):
    out = Path(tempfile.mkdtemp(prefix='finally-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    files = [*modules, runner, ROOT / 'spec/semantics/modules.json',
             ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
             ROOT / '_build/default/adapter/main.exe', ROOT / 'frontend/worker.php',
             ROOT / 'tests/semantics/finally_protocol_cases.py', Path(__file__)]
    before = {str(path.relative_to(ROOT)): digest(path) for path in files}
    results = []
    selected = [case for case in CASES if match in case[0]]
    assert selected
    for name, source, stage, checks in selected:
        directory = out / name
        directory.mkdir()
        source_path = directory / 'source.php'
        source_path.write_bytes(source)
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                           'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], directory / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            assert parsed['accepted'], parsed
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], checked
        finally:
            frontend.close()
            adapter.close()
        initial = '$php_run(' + checked['fixture'] + ', 0, ' + json.dumps(
            base64.b64encode(str(source_path).encode()).decode()) + ')'
        conditions = ['S_initial = ' + initial,
                      'S = $seek(S_initial[.COMPLETION = NORMAL], 1000)[.COMPLETION = NORMAL]', *checks]
        fixture = directory / 'protocol.watsup'
        fixture.write_text(PREFIX.replace('STAGE', stage) + '\ndec $main() : bool\ndef $main() = true\n'
                           + ''.join('  -- if ' + condition + '\n' for condition in conditions))
        command = [str(runner), *map(str, modules), str(fixture)]
        (directory / 'command.json').write_text(json.dumps(command) + '\n')
        try:
            result = subprocess.run(command, capture_output=True, timeout=300)
        except subprocess.TimeoutExpired as error:
            (directory / 'stdout').write_bytes(error.stdout or b'')
            (directory / 'stderr').write_bytes(error.stderr or b'')
            (directory / 'status.json').write_text('{"status":"timeout"}\n')
            raise
        (directory / 'stdout').write_bytes(result.stdout)
        (directory / 'stderr').write_bytes(result.stderr)
        (directory / 'status.json').write_text(json.dumps({'exit_status': result.returncode}) + '\n')
        passed = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
        results.append({'name': name, 'pass': passed, 'assertions': len(conditions),
                        'source_sha256': digest(source_path), 'fixture_sha256': digest(fixture)})
        (out / 'records.json').write_text(json.dumps(results, indent=2) + '\n')
        print(name, passed, len(conditions), flush=True)
    assert before == {str(path.relative_to(ROOT)): digest(path) for path in files}
    report = {'result': 'pass' if all(row['pass'] for row in results) else 'fail',
              'inputs': before, 'selection': match, 'records': results,
              'assertions': sum(row['assertions'] for row in results)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    raise SystemExit(0 if main(parser.parse_args().match) else 1)
