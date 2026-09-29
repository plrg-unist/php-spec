#!/usr/bin/env python3
"""Source-derived pauses for owned weak typed-return string callbacks."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASES = {row['id']: row for row in json.loads(
    (ROOT / 'tests/semantics/user_string_typed_cases.json').read_text())}
MODULES = [ROOT / name for name in json.loads(
    (ROOT / 'spec/semantics/modules.json').read_text())]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


STAGES = [
    ('pending', 'typed-return-direct',
     'S.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_site) z) '
     ':: (STRINGIFY_RESULT n porigin_site z) :: (RETURN_VALUE z) '
     ':: (TYPE_RETURN_THROW n porigin_site z) :: ptask_tail*', [
         '$typed_return_marker_valid(S, n, porigin_site, z)',
         '$stringify_pending(S, METHOD_TARGET n porigin_method, porigin_site)',
         '(HOBJECT n) <- $heap_graph(S).ROOTS',
         '~$call_descriptors_valid(S[.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_site) z) :: (STRINGIFY_RESULT n porigin_site z) :: (RETURN_VALUE z) :: ptask_tail*])',
         '~$call_descriptors_valid(S[.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_site) z) :: (STRINGIFY_RESULT n porigin_site z) :: (TYPE_RETURN_THROW n porigin_site z) :: (RETURN_VALUE z) :: ptask_tail*])',
         '~$call_descriptors_valid(S[.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_site) z) :: (STRINGIFY_RESULT n porigin_site z) :: (RETURN_VALUE z) :: (TYPE_RETURN_THROW $(n + 1) porigin_site z) :: ptask_tail*])',
     ]),
    ('entered', 'typed-return-direct',
     'S.CURRENT = (pcallcontext) -- if S.FRAMES = pframe :: pframe_tail* '
     '-- if pframe.TODO = (STRINGIFY_RESULT n porigin_site z) :: (RETURN_VALUE z) '
     ':: (TYPE_RETURN_THROW n porigin_site z) :: ptask_tail*', [
         '$stringify_context_frame_valid(S, pcallcontext, pframe)',
         '$typed_return_marker_valid(S[.CURRENT = pframe.CONTEXT][.ORIGIN = pframe.ORIGIN][.TODO = pframe.TODO], n, porigin_site, z)',
         '(HOBJECT n) <- $heap_graph(S).ROOTS',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n porigin_site z) :: (RETURN_VALUE z) :: ptask_tail*] :: pframe_tail*])',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n porigin_site z) :: (RETURN_VALUE z) :: (TYPE_RETURN_THROW n porigin_site $(z + 1)) :: ptask_tail*] :: pframe_tail*])',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n porigin_site z) :: (TYPE_RETURN_THROW n porigin_site z) :: (RETURN_VALUE z) :: ptask_tail*] :: pframe_tail*])',
     ]),
    ('restored-result', 'typed-return-direct',
     'S.TODO = (STRINGIFY_RESULT n porigin_site z) :: (RETURN_VALUE z) '
     ':: (TYPE_RETURN_THROW n porigin_site z) :: ptask_tail* '
     '-- if S.RESULT = KNOWN (PSTRING n_text*)', [
         '$typed_return_marker_valid(S, n, porigin_site, z)',
         '$stringify_result_valid(S, n, porigin_site, z)',
         '(HOBJECT n) <- $heap_graph(S).ROOTS',
         '~$call_descriptors_valid(S[.TODO = (STRINGIFY_RESULT n porigin_site z) :: (RETURN_VALUE z) :: ptask_tail*])',
         '~$call_descriptors_valid(S[.TODO = (STRINGIFY_RESULT n porigin_site z) :: (RETURN_VALUE z) :: (TYPE_RETURN_THROW n porigin_site $(z + 1)) :: ptask_tail*])',
     ]),
    ('return-resume', 'typed-return-direct',
     'S.TODO = (RETURN_VALUE z) :: (TYPE_RETURN_THROW n porigin_site z) :: ptask_tail* '
     '-- if S.RESULT = KNOWN (PSTRING n_text*)', [
         '$typed_return_resume_pending(S, z)',
         '$typed_return_marker_valid(S, n, porigin_site, z)',
         '(HOBJECT n) <- $heap_graph(S).ROOTS',
         '~$call_descriptors_valid(S[.TODO = [TYPE_RETURN_THROW n porigin_site z]])',
         '~$call_descriptors_valid(S[.RESULT = KNOWN (POBJECT n)])',
         'S_next = $drive_steps(S[.COMPLETION = NORMAL], 1)',
         'S_next.TODO = (RETURN_UNWIND (KNOWN (PSTRING n_text*)) (porigin_site)) :: ptask_tail*',
     ]),
    ('throw-chain', 'typed-return-local-catch',
     'S.TODO = (THROW_SEARCH n_old) :: (STRINGIFY_RESULT n porigin_site z) '
     ':: (RETURN_VALUE z) :: (TYPE_RETURN_THROW n porigin_site z) :: ptask_tail*', [
         '$typed_return_throw_pending(S)',
         '(HOBJECT n) <- $heap_graph(S).ROOTS',
         '(HOBJECT n_old) <- $heap_graph(S).ROOTS',
         '~$call_descriptors_valid(S[.TODO = (THROW_SEARCH n_old) :: (STRINGIFY_RESULT n porigin_site z) :: (RETURN_VALUE z) :: ptask_tail*])',
         '~$call_descriptors_valid(S[.TODO = (THROW_SEARCH n_old) :: (STRINGIFY_RESULT n porigin_site z) :: (TYPE_RETURN_THROW n porigin_site z) :: (RETURN_VALUE z) :: ptask_tail*])',
         '~$call_descriptors_valid(S[.TODO = (THROW_SEARCH n_old) :: (STRINGIFY_RESULT n porigin_site z) :: (RETURN_VALUE z) :: (TYPE_RETURN_THROW $(n + 1) porigin_site z) :: ptask_tail*])',
         'S_next = $drive_steps(S[.COMPLETION = NORMAL], 1)',
         'S_next.TODO = (THROW_SEARCH n_new) :: ptask_tail*',
         '$throwable_previous_id(S_next, n_new) = (n_old)',
         'S_next.OBJECTS[n_new] = THROWABLE pthrowable',
         'pthrowable.KIND = "TypeError"',
     ]),
]


def main():
    out = Path(tempfile.mkdtemp(prefix='user-string-typed-protocol-', dir=ROOT / '.tools'))
    inputs = [*MODULES, ROOT / 'spec/semantics/modules.json',
              ROOT / 'tests/semantics/user_string_typed_cases.json', Path(__file__),
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
        for source_id in {row[1] for row in STAGES}:
            source = out / (source_id + '.php')
            source.write_bytes(CASES[source_id]['source'].encode())
            assert sha(source) == CASES[source_id]['source_sha256']
            parsed = frontend.request({'op': 'parse',
                                       'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            fixtures[source_id] = ('$php_run(' + checked['fixture'] + ', 0, ' +
                                   json.dumps(base64.b64encode(str(source).encode()).decode()) + ')')
    finally:
        frontend.close()
        adapter.close()
    results = []
    for name, source_id, stage, checks in STAGES:
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
            '  -- if S = $seek(S_initial[.COMPLETION = NORMAL], 500)\n'
            '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
            f'  -- if {stage}\n'
            '  -- if $call_descriptors_valid(S)\n'
            '  -- if $heap_valid($heap_graph(S))\n'
            + ''.join('  -- if ' + check + '\n' for check in checks))
        result = subprocess.run(
            [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
             *map(str, MODULES), str(fixture)], capture_output=True,
            text=True, timeout=300)
        (directory / 'stdout').write_text(result.stdout)
        (directory / 'stderr').write_text(result.stderr)
        passed = result.returncode == 0 and result.stdout == 'true\n' and not result.stderr
        results.append({'id': name, 'source_id': source_id, 'source_sha256': sha(out / (source_id + '.php')),
                        'fixture_sha256': sha(fixture), 'assertions': len(checks) + 4,
                        'pass': passed})
        print(name, passed, flush=True)
        if not passed:
            print(result.stderr[-1500:], flush=True)
    stable = before == {str(path.relative_to(ROOT)): sha(path) for path in inputs}
    report = {'result': 'pass' if stable and all(row['pass'] for row in results) else 'fail',
              'stable': stable, 'inputs': before, 'records': results, 'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
