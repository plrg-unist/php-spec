#!/usr/bin/env python3
"""Source-derived ownership checks for eval operand string callbacks."""
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


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


STAGES = [
    ('scalar-request', 'eval-string-multiline-scalar-throw',
     'S.TODO = (EVAL_REQUEST porigin_parent z) :: (ORIGIN_RETURN (porigin_parent)) :: ptask_tail* '
     '-- if S.ORIGIN = (porigin_child)', [
         '$eval_operand_site_valid(S, porigin_parent, porigin_child, z)',
         '$(z = 2)',
         '$eval_requests_owned(S.TODO)',
         '~$call_descriptors_valid(S[.ORIGIN = (porigin_parent)])',
         '~$call_descriptors_valid(S[.TODO = (EVAL_REQUEST porigin_parent z) :: ptask_tail*])',
         '~$call_descriptors_valid(S[.TODO = (EVAL_REQUEST porigin_parent z) :: (ORIGIN_RETURN (porigin_child)) :: ptask_tail*])',
     ]),
    ('pending-callback', 'eval-string-code',
     'S.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_child) z) '
     ':: (STRINGIFY_RESULT n porigin_child z) :: (EVAL_REQUEST porigin_parent z) '
     ':: (ORIGIN_RETURN (porigin_parent)) :: ptask_tail*', [
         '$stringify_pending(S, METHOD_TARGET n porigin_method, porigin_child)',
         '$eval_operand_site_valid(S, porigin_parent, porigin_child, z)',
         '~$call_descriptors_valid(S[.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_child) z) :: (STRINGIFY_RESULT n porigin_child z) :: (EVAL_REQUEST porigin_parent z) :: ptask_tail*])',
         '~$call_descriptors_valid(S[.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_child) z) :: (STRINGIFY_RESULT n porigin_child z) :: (EVAL_REQUEST porigin_parent z) :: (ORIGIN_RETURN (porigin_child)) :: ptask_tail*])',
         '~$call_descriptors_valid(S[.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_child) z) :: (STRINGIFY_RESULT n porigin_child z) :: (EVAL_REQUEST porigin_parent $(z + 1)) :: (ORIGIN_RETURN (porigin_parent)) :: ptask_tail*])',
     ]),
    ('entered-callback', 'eval-string-multiline-callback-throw',
     'S.CURRENT = (pcallcontext) -- if pcallcontext.CALLSITE = (porigin_child) '
     '-- if S.FRAMES = pframe :: pframe_tail* '
     '-- if pframe.TODO = (STRINGIFY_RESULT n porigin_child z) '
     ':: (EVAL_REQUEST porigin_parent z) :: (ORIGIN_RETURN (porigin_parent)) :: ptask_tail*', [
         '$(z = 2)',
         '$stringify_context_frame_valid(S, pcallcontext, pframe)',
         '$eval_trace_preparser(S, S.CURRENT, pframe) = [ptraceframe]',
         'ptraceframe.LINE = z',
         'ptraceframe.FILE = $call_sourcefile(S.FILES, porigin_parent)',
         '$eval_trace_preparser(S, (pcallcontext[.CALLSITE = eps]), pframe) = eps',
         '~$call_descriptors_valid(S[.CURRENT = (pcallcontext[.LINE = $(z + 1)])])',
         '~$call_descriptors_valid(S[.CURRENT = (pcallcontext[.RECEIVER = ($(n + 1))])])',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n porigin_child z) :: (EVAL_REQUEST porigin_parent z) :: ptask_tail*] :: pframe_tail*])',
         '~$call_descriptors_valid(S[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n porigin_child z) :: (EVAL_REQUEST porigin_parent z) :: (ORIGIN_RETURN (porigin_child)) :: ptask_tail*] :: pframe_tail*])',
     ]),
    ('restored-result', 'eval-string-code',
     'S.CURRENT = eps -- if S.TODO = (STRINGIFY_RESULT n porigin_child z) '
     ':: (EVAL_REQUEST porigin_parent z) :: (ORIGIN_RETURN (porigin_parent)) :: ptask_tail*', [
         '$stringify_result_valid(S, n, porigin_child, z)',
         '(HOBJECT n) <- $heap_graph(S).ROOTS',
         '~$call_descriptors_valid(S[.TODO = (STRINGIFY_RESULT n porigin_child z) :: (EVAL_REQUEST porigin_parent z) :: ptask_tail*])',
         '~$call_descriptors_valid(S[.TODO = (STRINGIFY_RESULT n porigin_parent z) :: (EVAL_REQUEST porigin_parent z) :: (ORIGIN_RETURN (porigin_parent)) :: ptask_tail*])',
         '~$call_descriptors_valid(S[.TODO = (STRINGIFY_RESULT $(n + 1) porigin_child z) :: (EVAL_REQUEST porigin_parent z) :: (ORIGIN_RETURN (porigin_parent)) :: ptask_tail*])',
     ]),
    ('parser-wait', 'eval-string-multiline-generated-throw',
     'S.COMPLETION = SOURCE_PENDING -- if S.EVALCONTEXTS = pevalcontext :: pevalcontext_tail* '
     '-- if pevalcontext.SITE = porigin_parent -- if S.TODO = (EVAL_AWAIT n) '
     ':: (ORIGIN_RETURN (porigin_parent)) :: ptask_tail*', [
         'pevalcontext.UNIT = n',
         'S.ORIGIN = (porigin_parent)',
         '$($eval_site_line(S, porigin_parent) = 2)',
         '~$call_descriptors_valid(S[.ORIGIN = $origin_child((porigin_parent), [PCFIELD 0])])',
         '~$call_descriptors_valid(S[.TODO = (EVAL_AWAIT n) :: ptask_tail*])',
     ]),
]


def fixture(source, directory):
    path = directory / 'source.php'
    path.write_bytes(source['source'].encode())
    assert digest(path) == source['source_sha256']
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [part for key, value in profile.items()
             for part in ('-d', key + '=' + value)]
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], directory / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                     directory / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse',
                                   'source': base64.b64encode(path.read_bytes()).decode()})
        assert parsed['accepted']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
    finally:
        frontend.close()
        adapter.close()
    return ('$php_run(' + checked['fixture'] + ', 0, ' +
            json.dumps(base64.b64encode(str(path).encode()).decode()) + ')')


def main():
    out = Path(tempfile.mkdtemp(prefix='user-string-eval-protocol-', dir=ROOT / '.tools'))
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    inputs = [*MODULES, ROOT / 'spec/semantics/modules.json',
              ROOT / 'tests/semantics/user_string_cases.json', Path(__file__), runner,
              ROOT / '_build/default/adapter/main.exe']
    before = {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    records = []
    for name, case_id, stage, checks in STAGES:
        directory = out / name
        directory.mkdir()
        initial = fixture(CASES[case_id], directory)
        protocol = directory / 'protocol.watsup'
        protocol.write_text(
            'dec $stage(pstate) : bool\n'
            f'def $stage(S) = true -- if {stage}\n'
            'def $stage(S) = false -- otherwise\n'
            'dec $seek(pstate, nat) : pstate\n'
            'def $seek(S, n) = S -- if $stage(S)\n'
            'def $seek(S, n) = $seek($drive_steps(S[.COMPLETION = NORMAL], 1), '
            '$nabs($(n - 1))) -- if ~$stage(S) -- if $(n > 0)\n'
            'dec $main() : bool\ndef $main() = true\n'
            f'  -- if S_initial = {initial}\n'
            '  -- if S = $seek(S_initial[.COMPLETION = NORMAL], 700)\n'
            f'  -- if {stage}\n'
            '  -- if $call_descriptors_valid(S)\n'
            '  -- if $heap_valid($heap_graph(S))\n'
            + ''.join('  -- if ' + check + '\n' for check in checks))
        result = subprocess.run([str(runner), *map(str, MODULES), str(protocol)],
                                capture_output=True, text=True, timeout=300)
        (directory / 'stdout').write_text(result.stdout)
        (directory / 'stderr').write_text(result.stderr)
        passed = result.returncode == 0 and result.stdout == 'true\n' and not result.stderr
        records.append({'id': name, 'source_sha256': digest(directory / 'source.php'),
                        'fixture_sha256': digest(protocol), 'assertions': len(checks) + 4,
                        'pass': passed})
        print(name, passed, flush=True)
        if not passed:
            print(result.stderr[-1500:], flush=True)
    stable = before == {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    report = {'result': 'pass' if stable and all(row['pass'] for row in records) else 'fail',
              'stable': stable, 'inputs': before, 'records': records,
              'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
