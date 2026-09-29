#!/usr/bin/env python3
"""Source-derived pauses for the implicit __toString call and its saved owner."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASES = {row['id']: row for row in json.loads(
    (ROOT / 'tests/semantics/user_string_cases.json').read_text())}
SOURCE = CASES['echo-reentrant-same-site']
MODULES = [ROOT / name for name in json.loads(
    (ROOT / 'spec/semantics/modules.json').read_text())]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


STAGES = [
    ('pending',
     'S.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_site) z) '
     ':: (STRINGIFY_RESULT n porigin_site z) :: (EMIT z) :: ptask_tail*', [
         'S.ORIGIN = (porigin_site)',
         '$stringify_pending(S, METHOD_TARGET n porigin_method, porigin_site)',
         '$call_task_valid(S, CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_site) z)',
         '~$call_descriptors_valid(S[.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_site) $(z + 1)) :: (STRINGIFY_RESULT n porigin_site z) :: (EMIT z) :: ptask_tail*])',
         '~$call_descriptors_valid(S[.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_site) z) :: (EMIT z) :: ptask_tail*])',
     ]),
    ('entered',
     'S.CURRENT = (pcallcontext) -- if pcallcontext.RECEIVER = (n) '
     '-- if pcallcontext.CALLSITE = (porigin_site) '
     '-- if S.FRAMES = pframe :: pframe_tail* '
     '-- if pframe.TODO = (STRINGIFY_RESULT n porigin_site z) :: (EMIT z) :: ptask_tail*', [
         '$stringify_context(S, pcallcontext)',
         '$stringify_chain_valid(S, S.CURRENT, S.FRAMES)',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT $(n + 1) porigin_site z) :: (EMIT z) :: ptask_tail*] :: pframe_tail*])',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (EMIT z) :: ptask_tail*] :: pframe_tail*])',
         '~$call_descriptors_valid(S[.CURRENT = (pcallcontext[.LINE = $(z + 1)])])',
     ]),
    ('reentrant-same-site',
     'S.CURRENT = (pcallcontext_inner) '
     '-- if pcallcontext_inner.CALLSITE = (porigin_site) '
     '-- if S.FRAMES = pframe_inner :: pframe_outer :: pframe_root :: eps '
     '-- if pframe_inner.CONTEXT = (pcallcontext_outer) '
     '-- if pcallcontext_outer.CALLSITE = (porigin_site) '
     '-- if pframe_inner.TODO = (STRINGIFY_RESULT n porigin_site z) :: ptask_inner* '
     '-- if pframe_outer.TODO = (STRINGIFY_RESULT n porigin_site z) :: ptask_outer*', [
         '$stringify_chain_valid(S, S.CURRENT, S.FRAMES)',
         '~$stringify_chain_valid(S[.FRAMES = [pframe_inner,pframe_outer]], S.CURRENT, [pframe_inner,pframe_outer])',
         '~$call_descriptors_valid(S[.FRAMES = [pframe_inner,pframe_outer]])',
         '~$call_descriptors_valid(S[.FRAMES = pframe_inner :: pframe_outer[.TODO = ptask_outer*] :: [pframe_root]])',
         '~$stringify_chain_valid(S, eps, S.FRAMES)',
         '~$stringify_context_frame_valid(S, pcallcontext_inner[.CALLSITE = eps], pframe_inner)',
     ]),
    ('restored-result',
     'S.CURRENT = eps -- if S.TODO = (STRINGIFY_RESULT n porigin_site z) '
     ':: (EMIT z) :: ptask_tail*', [
         '$stringify_result_valid(S, n, porigin_site, z)',
         '(HOBJECT n) <- $heap_graph(S).ROOTS',
         '(HOBJECT n) <- S.ALLOCATIONS',
         '~$call_descriptors_valid(S[.TODO = (STRINGIFY_RESULT $(n + 1) porigin_site z) :: (EMIT z) :: ptask_tail*])',
         '$origin_child((porigin_site), [PCFIELD 0]) = (porigin_wrong)',
         '~$call_descriptors_valid(S[.TODO = (STRINGIFY_RESULT n porigin_wrong z) :: (EMIT z) :: ptask_tail*])',
     ]),
]


def main():
    out = Path(tempfile.mkdtemp(prefix='user-string-protocol-', dir=ROOT / '.tools'))
    source = out / 'source.php'
    source.write_bytes(SOURCE['source'].encode())
    assert sha(source) == SOURCE['source_sha256']
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [part for key, value in profile.items()
             for part in ('-d', key + '=' + value)]
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                     out / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse',
                                   'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
    finally:
        frontend.close()
        adapter.close()
    inputs = [*MODULES, ROOT / 'spec/semantics/modules.json',
              ROOT / 'tests/semantics/user_string_cases.json', Path(__file__),
              ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
              ROOT / '_build/default/adapter/main.exe']
    before = {str(path.relative_to(ROOT)): sha(path) for path in inputs}
    initial = ('$php_run(' + checked['fixture'] + ', 0, ' +
               json.dumps(base64.b64encode(str(source).encode()).decode()) + ')')
    results = []
    for name, stage, checks in STAGES:
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
            f'  -- if S_initial = {initial}\n'
            '  -- if S = $seek(S_initial[.COMPLETION = NORMAL], 400)\n'
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
        results.append({'id': name, 'assertions': len(checks) + 4, 'pass': passed})
        print(name, passed, flush=True)
        if not passed:
            print(result.stderr[-1500:], flush=True)
    stable = before == {str(path.relative_to(ROOT)): sha(path) for path in inputs}
    report = {'result': 'pass' if stable and all(row['pass'] for row in results) else 'fail',
              'stable': stable, 'source_sha256': sha(source), 'inputs': before,
              'records': results, 'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
