#!/usr/bin/env python3
"""Source-derived publication history and completed-prefix regression tests."""
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import static_types as types
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/compiler_publication_protocol_cases.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(match):
    selected = [row for row in json.loads(CATALOGUE.read_text())['cases'] if match in row['id']]
    assert selected, 'empty publication protocol selection'
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    adapter_path = ROOT / '_build/default/adapter/main.exe'
    watched = [*modules, runner, adapter_path, types.PHP, Path(__file__), CATALOGUE,
               ROOT / 'spec/semantics/modules.json', ROOT / 'frontend/worker.php',
               ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/recorded_worker.py']
    fingerprint = types.syntax_validation.implementation_fingerprint()
    before = {str(path.relative_to(ROOT)): sha(path) for path in watched}

    def stable():
        return fingerprint == types.syntax_validation.implementation_fingerprint() and all(
            sha(ROOT / name) == digest for name, digest in before.items())

    out = Path(tempfile.mkdtemp(prefix='compiler-publication-', dir=ROOT / '.tools'))
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(adapter_path), str(ROOT)], out / 'adapter')
    fixtures = []
    try:
        for row in selected:
            source = out / (row['id'] + '.php')
            source.write_bytes(row['source'].encode())
            assert sha(source) == row['source_sha256']
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'], (row['id'], parsed)
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], (row['id'], checked)
            filename = "(" + types.byte_expr(str(source)) + ")"
            conditions = [f'P = $ppstart(0, {checked["fixture"]}, {filename})',
                          f'S = $compile_source($initial_state(NORMAL)[.FILES = [SOURCEFILE 0 {filename}]], P)',
                          *row['checks']]
            fixture = out / (row['id'] + '.watsup')
            fixture.write_text('dec $main() : bool\ndef $main() = true\n' + ''.join(
                '  -- if ' + condition + '\n' for condition in conditions))
            fixtures.append((row, fixture, len(conditions)))
    finally:
        try:
            frontend.close()
        finally:
            adapter.close()
    records = []
    for row, fixture, count in fixtures:
        assert stable(), 'publication inputs changed before case'
        command = [str(runner), *map(str, modules), str(fixture)]
        raw = out / row['id']
        raw.mkdir()
        (raw / 'command.json').write_text(json.dumps(command) + '\n')
        with (raw / 'stdout').open('wb') as stdout_stream, (raw / 'stderr').open('wb') as stderr_stream:
            try:
                result = subprocess.run(command, cwd=ROOT, env=types.ENV,
                                        stdout=stdout_stream, stderr=stderr_stream, timeout=120)
                status = result.returncode
            except subprocess.TimeoutExpired:
                status = None
        stdout, stderr = (raw / 'stdout').read_bytes(), (raw / 'stderr').read_bytes()
        verdict = ('timeout_unknown' if status is None else
                   'pass' if status == 0 and stdout == b'true\n' and not stderr else 'fail')
        (raw / 'status.json').write_text(json.dumps({'exit_status': status, 'result': verdict}) + '\n')
        records.append({'id': row['id'], 'result': verdict, 'conditions': count,
                        'source_sha256': row['source_sha256'], 'fixture_sha256': sha(fixture),
                        'stdout_sha256': sha(raw / 'stdout'), 'stderr_sha256': sha(raw / 'stderr'),
                        'inputs_stable': stable()})
        print(row['id'], verdict, count, flush=True)
        if verdict != 'pass' or not records[-1]['inputs_stable']:
            break
    passed = len(records) == len(selected) and stable() and all(row['result'] == 'pass' for row in records)
    report = {'result': 'pass' if passed else 'fail', 'selected_cases': len(selected),
              'completed_cases': len(records), 'records': records, 'fingerprint': fingerprint,
              'direct_inputs': before, 'scope': 'Source-derived state/history predicates and altered-history rejection; native output, current compatibility and full publication acceptance remain separate.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'], flush=True)
    return passed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--match', default='')
    raise SystemExit(0 if run(parser.parse_args().match) else 1)
