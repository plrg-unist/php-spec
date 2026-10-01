#!/usr/bin/env python3
"""Source-derived exit pauses with retired lexical context and live frame cleanup."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASES = {row['id']: row for row in json.loads(
    (ROOT / 'tests/semantics/finally_cases.json').read_text())}
MODULES = [ROOT / name for name in json.loads(
    (ROOT / 'spec/semantics/modules.json').read_text())]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def completed(terminal=False):
    return [
        'S_done = $drive(' + ('S' if terminal else 'S[.COMPLETION = NORMAL]') + ', 1000)',
        'S_whole = $drive_steps(S_initial[.COMPLETION = NORMAL], 1000)',
        'S_done = S_whole', 'S_done.COMPLETION = EXITED 7',
        'S_done.ORIGIN = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
        'S_done.TODO = eps', 'S_done.ITERATORS = eps', 'S_done.SILENCES = eps',
        'S_done.REPORTING = S_initial.REPORTING', 'S_done.TRACE = eps',
        'S_done.ERRORORIGIN = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


STAGES = []
for name, source in [
    ('function-finalizer-unwind', 'exit-origin-function-finalizer'),
    ('function-catch-unwind', 'exit-origin-function-catch'),
    ('method-finalizer-unwind', 'exit-origin-method-finalizer'),
    ('suppressed-foreach-unwind', 'exit-origin-suppressed-foreach'),
    ('outer-foreach-unwind', 'exit-origin-outer-foreach'),
]:
    checks = [
        'S.COMPLETION = BUDGET', 'S.ORIGIN = eps', 'S.CURRENT = (pcallcontext)',
        '$task_nodes(EXIT_UNWIND 7) = eps',
        '~$call_task_valid(S[.ORIGIN = (pcallcontext.FUNCTION)], EXIT_UNWIND 7)',
        '~$call_descriptors_valid(S[.ORIGIN = (pcallcontext.FUNCTION)])',
    ]
    if name == 'suppressed-foreach-unwind':
        checks += ['S.ITERATORS = eps', 'S.SILENCES = eps',
                   'S.REPORTING = $long_and(S_initial.REPORTING, 4437)',
                   'S.FRAMES = pframe :: pframe_tail*', 'pframe.SILENCES =/= eps']
    if name == 'outer-foreach-unwind':
        checks += ['|S.ITERATORS| = 1',
                   'S_next = $drive_steps(S[.COMPLETION = NORMAL], 1)',
                   'S_next.TODO = [EXIT_UNWIND 7]', 'S_next.ORIGIN = eps',
                   'S_next.ITERATORS = eps', '$call_descriptors_valid(S_next)',
                   '$heap_valid($heap_graph(S_next))']
    STAGES.append((name, source, 'S.TODO = [EXIT_UNWIND 7]', checks + completed()))
STAGES.append(('top-level-finalizer-exit', 'exit-origin-top-level-finalizer',
               'S.COMPLETION = EXITED 7', ['S.ORIGIN = eps'] + completed(terminal=True)))


def main(match):
    stages = [row for row in STAGES if match in row[0]]
    assert stages
    out = Path(tempfile.mkdtemp(prefix='exit-origin-protocol-', dir=ROOT / '.tools'))
    inputs = [*MODULES, ROOT / 'spec/semantics/modules.json',
              ROOT / 'tests/semantics/finally_cases.json', Path(__file__),
              ROOT / 'tests/semantics/profile.json', ROOT / 'frontend/worker.php',
              ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
              ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
              ROOT / '_build/default/adapter/main.exe']
    before = {str(path.relative_to(ROOT)): sha(path) for path in inputs}
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [part for key, value in profile.items()
             for part in ('-d', key + '=' + value)]
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        fixtures = {}
        for source_id in {row[1] for row in stages}:
            source = out / (source_id + '.php')
            source.write_bytes(CASES[source_id]['source'].encode())
            parsed = frontend.request({'op': 'parse',
                                       'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            fixtures[source_id] = ('$php_run(' + checked['fixture'] + ', 0, ' +
                                   json.dumps(base64.b64encode(str(source).encode()).decode()) + ')')
    finally:
        frontend.close()
        adapter.close()
    records = []
    for name, source_id, stage, checks in stages:
        directory = out / name
        directory.mkdir()
        fixture = directory / 'protocol.watsup'
        fixture.write_text(
            'dec $stage(pstate) : bool\n'
            f'def $stage(S) = true -- if {stage}\n'
            'def $stage(S) = false -- otherwise\n'
            'dec $seek(pstate, nat) : pstate\n'
            'def $seek(S, n) = S -- if $stage(S)\n'
            'def $seek(S, n) = $seek($drive_steps(S[.COMPLETION = NORMAL], 1), '
            '$nabs($(n - 1))) -- if ~$stage(S) -- if $(n > 0)\n'
            'dec $main() : bool\ndef $main() = true\n'
            f'  -- if S_initial = {fixtures[source_id]}\n'
            '  -- if S = $seek(S_initial[.COMPLETION = NORMAL], 300)\n'
            '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET \\/ S.COMPLETION = EXITED 7\n'
            f'  -- if {stage}\n'
            '  -- if $call_descriptors_valid(S)\n'
            '  -- if $heap_valid($heap_graph(S))\n'
            + ''.join('  -- if ' + check + '\n' for check in checks))
        result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                 *map(str, MODULES), str(fixture)],
                                capture_output=True, text=True, timeout=300)
        (directory / 'stdout').write_text(result.stdout)
        (directory / 'stderr').write_text(result.stderr)
        passed = result.returncode == 0 and result.stdout == 'true\n' and not result.stderr
        records.append({'id': name, 'source_id': source_id,
                        'source_sha256': sha(out / (source_id + '.php')),
                        'fixture_sha256': sha(fixture), 'assertions': len(checks) + 4,
                        'pass': passed})
        print(name, passed, flush=True)
        if not passed:
            print(result.stderr[-1500:], flush=True)
    stable = before == {str(path.relative_to(ROOT)): sha(path) for path in inputs}
    report = {'result': 'pass' if stable and all(row['pass'] for row in records) else 'fail',
              'stable': stable, 'inputs': before, 'records': records, 'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    return report['result'] == 'pass'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    raise SystemExit(0 if main(parser.parse_args().match) else 1)
