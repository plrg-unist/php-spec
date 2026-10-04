#!/usr/bin/env python3
"""Compile and execute source-driven exception-handler protocol assertions."""
import argparse
import base64
import json
from pathlib import Path
import subprocess
import tempfile

from error_handler_run import ENV, ROOT, recorded
from exception_handlers import digest
from exception_handler_protocol import CASES, PREFIX, SOURCES
from recorded_worker import Worker


def run(selected):
    assert not selected or set(selected) <= {row[0] for row in CASES}, 'unknown case'
    cases = [row for row in CASES if not selected or row[0] in selected]
    assert cases, 'empty selection'
    out = Path(tempfile.mkdtemp(prefix='exception-handler-state-', dir=ROOT / '.tools'))
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    identities = {str(path.relative_to(ROOT)): digest(path) for path in [
        ROOT / '.tools/php/bin/php', ROOT / '.tools/spectec/bin/p4spectec',
        ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
        ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php-file.so',
        ROOT / 'tests/semantics/exception_handler_protocol.py',
        ROOT / 'tests/semantics/exception_handler_cases.json',
        ROOT / 'tests/semantics/exception_handler_state.py']}
    modules = [str(ROOT / path) for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    print(out, flush=True)
    results = []
    failure = None
    try:
        for name, source_id, stage, expected, checks in cases:
            directory = out / name
            directory.mkdir()
            source = directory / 'source.php'
            source.write_text(SOURCES[source_id])
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                               'extension=' + str(ROOT / '.tools/php-file.so'),
                               str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            try:
                adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
                try:
                    parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                    assert parsed['accepted'], parsed
                    checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                    assert checked['ok'], checked
                finally:
                    adapter.close()
            finally:
                frontend.close()
            path = json.dumps(base64.b64encode(str(source).encode()).decode())
            conditions = [
                'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + path + ')',
                'S_reached = $seek(S_initial[.COMPLETION = NORMAL], 1500)',
                r'S_reached.COMPLETION = NORMAL \/ S_reached.COMPLETION = BUDGET',
                'S = S_reached[.COMPLETION = NORMAL]', '$stage(S)', *checks,
                '$outputs(S_done.EVENTS) = [' + ','.join(map(str, expected.encode())) + ']',
            ]
            fixture = directory / 'protocol.watsup'
            fixture.write_text(PREFIX.replace('STAGE', stage)
                               + '\ndec $main() : bool\ndef $main() = true\n'
                               + ''.join('  -- ' + (condition if condition.startswith('PhpStep:') else 'if ' + condition) + '\n'
                                         for condition in conditions))
            compiler = recorded([str(ROOT / '.tools/spectec/bin/p4spectec'), 'algo', *modules, str(fixture)],
                                directory / 'compiler', 120)
            passed = (compiler['exit'] == 0 and not compiler['timeout']
                      and not (directory / 'compiler.stderr').read_bytes())
            result = {'id': name, 'source_id': source_id, 'assertions': len(conditions),
                      'source_sha256': digest(source), 'fixture_sha256': digest(fixture),
                      'compiler': compiler, 'passed': False}
            results.append(result)
            assert passed, 'compile: ' + name
            model = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), *modules, str(fixture)],
                             directory / 'model', 300)
            passed = (model['exit'] == 0 and not model['timeout']
                      and (directory / 'model.stdout').read_bytes().strip() == b'true'
                      and not (directory / 'model.stderr').read_bytes())
            result.update(model=model, passed=passed)
            print(name, passed, len(conditions), flush=True)
            assert passed, name
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error)}
    stable = all(digest(ROOT / name) == sha for name, sha in identities.items())
    passed = failure is None and stable and len(results) == len(cases) and all(row['passed'] for row in results)
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'identities': identities,
        'inputs_stable': stable, 'selection': [row[0] for row in cases],
        'environment': {'LC_ALL': ENV['LC_ALL'], 'TZ': ENV['TZ'],
                        'PHP_SPEC_SCRIPT_ENCODING_removed': 'PHP_SPEC_SCRIPT_ENCODING' not in ENV},
        'records': results, 'failure': failure, 'passed': passed}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.case) else 1)
