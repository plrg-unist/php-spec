#!/usr/bin/env python3
"""Source-derived ownership and phase checks for concatenation callbacks."""
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
MODULES = [ROOT / name for name in json.loads(
    (ROOT / 'spec/semantics/modules.json').read_text())]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


STAGES = [
    ('left-pending', 'concat-string-dual-effect',
     'S.TODO = (CALL_ARGS (METHOD_TARGET n_left porigin_method) eps 0 eps (porigin_left) z) '
     ':: (STRINGIFY_RESULT n_left porigin_left z) '
     ':: (CONCAT_AFTER_LEFT porigin_parent (KNOWN (POBJECT n_right)) b_right z) :: ptask_tail*', [
         'S.ORIGIN = (porigin_left)',
         '$concat_left_child_valid(S, porigin_parent, porigin_left, z, b_right)',
         '(HOBJECT n_left) <- $heap_graph(S).ROOTS',
         '(HOBJECT n_right) <- $heap_graph(S).ROOTS',
         '~$call_descriptors_valid(S[.TODO = (CALL_ARGS (METHOD_TARGET n_left porigin_method) eps 0 eps (porigin_left) z) '
         ':: (STRINGIFY_RESULT n_left porigin_left z) '
         ':: (CONCAT_AFTER_RIGHT porigin_parent eps z) :: ptask_tail*])',
         '~$call_descriptors_valid(S[.TODO = (CALL_ARGS (METHOD_TARGET n_left porigin_method) eps 0 eps (porigin_left) $(z + 1)) '
         ':: (STRINGIFY_RESULT n_left porigin_left z) '
         ':: (CONCAT_AFTER_LEFT porigin_parent (KNOWN (POBJECT n_right)) b_right z) :: ptask_tail*])',
     ]),
    ('left-entered', 'concat-string-dual-effect',
     'S.CURRENT = (pcallcontext) -- if pcallcontext.CALLSITE = (porigin_left) '
     '-- if S.FRAMES = pframe :: pframe_tail* '
     '-- if pframe.TODO = (STRINGIFY_RESULT n_left porigin_left z) '
     ':: (CONCAT_AFTER_LEFT porigin_parent (KNOWN (POBJECT n_right)) b_right z) :: ptask_tail*', [
         '$concat_left_child_valid(S, porigin_parent, porigin_left, z, b_right)',
         '$stringify_chain_valid(S, S.CURRENT, S.FRAMES)',
         '(HOBJECT n_right) <- $heap_graph(S).ROOTS',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_left porigin_left z) '
         ':: (CONCAT_AFTER_RIGHT porigin_parent eps z) :: ptask_tail*] :: pframe_tail*])',
     ]),
    ('right-pending', 'concat-string-dual-effect',
     'S.TODO = (CALL_ARGS (METHOD_TARGET n_right porigin_method) eps 0 eps (porigin_right) z) '
     ':: (STRINGIFY_RESULT n_right porigin_right z) '
     ':: (CONCAT_AFTER_RIGHT porigin_parent n_left* z) :: ptask_tail*', [
         'S.ORIGIN = (porigin_right)',
         '$concat_right_child_valid(S, porigin_parent, porigin_right, z)',
         '(HOBJECT n_right) <- $heap_graph(S).ROOTS',
         '~$call_descriptors_valid(S[.TODO = (CALL_ARGS (METHOD_TARGET n_right porigin_method) eps 0 eps (porigin_right) z) '
         ':: (STRINGIFY_RESULT n_right porigin_right z) '
         ':: (CONCAT_AFTER_LEFT porigin_parent (KNOWN PNULL) false z) :: ptask_tail*])',
     ]),
    ('right-entered', 'concat-string-dual-effect',
     'S.CURRENT = (pcallcontext) -- if pcallcontext.CALLSITE = (porigin_right) '
     '-- if S.FRAMES = pframe :: pframe_tail* '
     '-- if pframe.TODO = (STRINGIFY_RESULT n_right porigin_right z) '
     ':: (CONCAT_AFTER_RIGHT porigin_parent n_left* z) :: ptask_tail*', [
         '$concat_right_child_valid(S, porigin_parent, porigin_right, z)',
         '$stringify_chain_valid(S, S.CURRENT, S.FRAMES)',
         '(HOBJECT n_right) <- $heap_graph(S).ROOTS',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_right porigin_right z) '
         ':: (CONCAT_AFTER_LEFT porigin_parent (KNOWN PNULL) false z) :: ptask_tail*] :: pframe_tail*])',
     ]),
    ('same-site-reentry', 'concat-string-same-site-reentrant',
     'S.CURRENT = (pcallcontext) -- if pcallcontext.CALLSITE = (porigin_left) '
     '-- if S.FRAMES = pframe :: pframe_tail* '
     '-- if pframe.TODO = (STRINGIFY_RESULT n porigin_left z) '
     ':: (CONCAT_AFTER_LEFT porigin_parent poperand_right b_right z) :: ptask_tail* '
     '-- if $older_left_marker(pframe_tail*, porigin_left)', [
         '$concat_left_child_valid(S, porigin_parent, porigin_left, z, b_right)',
         '$stringify_chain_valid(S, S.CURRENT, S.FRAMES)',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n porigin_left z) '
         ':: (CONCAT_AFTER_RIGHT porigin_parent eps z) :: ptask_tail*] :: pframe_tail*])',
     ]),
]

OLDER_MARKER = (
    'dec $left_marker_here(pframe, porigin) : bool\n'
    'def $left_marker_here(pframe, porigin_site) = true\n'
    '  -- if pframe.TODO = (STRINGIFY_RESULT n porigin_site z) '
    ':: (CONCAT_AFTER_LEFT porigin_parent poperand_right b_right z) :: ptask_tail*\n'
    'def $left_marker_here(pframe, porigin_site) = false -- otherwise\n'
    'dec $older_left_marker(pframe*, porigin) : bool\n'
    'def $older_left_marker(eps, porigin_site) = false\n'
    'def $older_left_marker(pframe :: pframe_tail*, porigin_site) = '
    '$left_marker_here(pframe, porigin_site) \\/ '
    '$older_left_marker(pframe_tail*, porigin_site)\n'
)


def initial_for(row, out):
    source = out / (row['id'] + '.php')
    source.write_bytes(row['source'].encode())
    assert sha(source) == row['source_sha256']
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [part for key, value in profile.items()
             for part in ('-d', key + '=' + value)]
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / (row['id'] + '-frontend'))
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                     out / (row['id'] + '-adapter'))
    try:
        parsed = frontend.request({'op': 'parse',
                                   'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
    finally:
        frontend.close()
        adapter.close()
    return ('$php_run(' + checked['fixture'] + ', 0, ' +
            json.dumps(base64.b64encode(str(source).encode()).decode()) + ')')


def main():
    out = Path(tempfile.mkdtemp(prefix='user-string-concat-protocol-', dir=ROOT / '.tools'))
    initials = {case_id: initial_for(CASES[case_id], out)
                for case_id in {stage[1] for stage in STAGES}}
    inputs = [*MODULES, ROOT / 'spec/semantics/modules.json',
              ROOT / 'tests/semantics/user_string_cases.json', Path(__file__),
              ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
              ROOT / '_build/default/adapter/main.exe']
    before = {str(path.relative_to(ROOT)): sha(path) for path in inputs}
    results = []
    for name, case_id, stage, checks in STAGES:
        directory = out / name
        directory.mkdir()
        fixture = directory / 'protocol.watsup'
        fixture.write_text(
            OLDER_MARKER +
            'dec $stage(pstate) : bool\n'
            f'def $stage(S) = true -- if {stage}\n'
            'def $stage(S) = false -- otherwise\n'
            'dec $seek(pstate, nat) : pstate\n'
            'def $seek(S, n) = S -- if $stage(S)\n'
            'def $seek(S, n) = $seek($drive_steps(S[.COMPLETION = NORMAL], 1), '
            '$nabs($(n - 1))) -- if ~$stage(S) -- if $(n > 0)\n'
            'dec $main() : bool\ndef $main() = true\n'
            f'  -- if S_initial = {initials[case_id]}\n'
            '  -- if S = $seek(S_initial[.COMPLETION = NORMAL], 600)\n'
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
        results.append({'id': name, 'assertions': len(checks) + 4,
                        'fixture_sha256': sha(fixture), 'pass': passed})
        print(name, passed, flush=True)
        if not passed:
            print(result.stderr[-1200:], flush=True)
    stable = before == {str(path.relative_to(ROOT)): sha(path) for path in inputs}
    report = {'result': 'pass' if stable and all(row['pass'] for row in results) else 'fail',
              'stable': stable, 'source_sha256': {case_id: CASES[case_id]['source_sha256']
                                                for case_id in initials},
              'inputs': before, 'records': results, 'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
