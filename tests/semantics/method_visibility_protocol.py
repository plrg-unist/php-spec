#!/usr/bin/env python3
"""Authenticate paused nonpublic method targets against their caller scope."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = ROOT / 'tests/semantics/method_visibility_cases.json'
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
MODULES = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
CASES = {
    'effective-protected': ('visibility-protected-family', 'PROPERTY_PROTECTED', [
        '$call_selected_valid(S, METHOD_TARGET n porigin_method, (porigin_site))',
        '~$call_selected_valid(S[.CURRENT = eps], METHOD_TARGET n porigin_method, (porigin_site))',
        '~$call_task_valid(S[.CURRENT = eps], ptask)',
    ]),
    'effective-private': ('visibility-computed-private', 'PROPERTY_PRIVATE', [
        '$call_selected_valid(S, METHOD_TARGET n porigin_method, (porigin_site))',
        '~$call_selected_valid(S[.CURRENT = eps], METHOD_TARGET n porigin_method, (porigin_site))',
        '~$call_task_valid(S[.CURRENT = eps], ptask)',
    ]),
    'ancestor-private': ('visibility-private-parent-public-shadow', 'PROPERTY_PRIVATE', [
        '$class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)',
        '$call_selected_valid(S, METHOD_TARGET n porigin_method, (porigin_site))',
        '~$call_selected_valid(S[.CURRENT = (pcallcontext[.LEXICAL_CLASS = (porigin_b)])], METHOD_TARGET n porigin_method, (porigin_site))',
        '~$call_task_valid(S[.CURRENT = (pcallcontext[.LEXICAL_CLASS = (porigin_b)])], ptask)',
    ]),
    'saved-ancestor-private': ('visibility-private-parent-public-shadow', 'PROPERTY_PRIVATE', [
        '$class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)',
        '$call_current_valid(S)',
        '$call_selected_valid(S, METHOD_TARGET n porigin_method, (porigin_site))',
        '~$call_selected_valid(S[.FRAMES = (pframe[.CONTEXT = (pcallcontext_caller[.LEXICAL_CLASS = (porigin_b)])]) :: pframe_tail*], METHOD_TARGET n porigin_method, (porigin_site))',
        '~$call_current_valid(S[.FRAMES = (pframe[.CONTEXT = (pcallcontext_caller[.LEXICAL_CLASS = (porigin_b)])]) :: pframe_tail*])',
    ]),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    out = Path(tempfile.mkdtemp(prefix='method-visibility-protocol-', dir=ROOT / '.tools'))
    inputs = [*MODULES, ROOT / 'spec/semantics/modules.json', ROOT / 'bin/php-semantics',
              ROOT / 'spec/php.watsup', ROOT / 'spec/schema.json', ROOT / 'frontend/worker.php',
              ROOT / 'frontend/FileLexer.php', ROOT / 'frontend/encoding.php', ROOT / 'frontend/target.php',
              ROOT / '_build/default/adapter/main.exe',
              ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
              ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so', CATALOGUE, Path(__file__)]
    before = {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    records = []
    for name, (source_id, visibility, checks) in CASES.items():
        directory = out / name
        directory.mkdir()
        source = directory / 'source.php'
        source.write_bytes(ROWS[source_id]['source'].encode())
        assert digest(source) == ROWS[source_id]['source_sha256']
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                           'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], directory / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                         directory / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'], name
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], name
        finally:
            frontend.close()
            adapter.close()
        if name == 'saved-ancestor-private':
            stage = ('S.CURRENT = (pcallcontext_callee) -- if pcallcontext_callee.FUNCTION = porigin_method '
                     '-- if pcallcontext_callee.CALLSITE = (porigin_site) '
                     '-- if pcallcontext_callee.RECEIVER = (n) '
                     '-- if S.FRAMES = pframe :: pframe_tail* '
                     '-- if pframe.ORIGIN = (porigin_site) '
                     '-- if pframe.CONTEXT = (pcallcontext_caller) '
                     '-- if $class_method_origin(S.CLASSES, porigin_method) = (pmethoddesc) '
                     f'-- if pmethoddesc.VISIBILITY = {visibility}')
        else:
            stage = ('S.TODO = ptask :: ptask_tail* -- if ptask = CALL_ARGS (METHOD_TARGET n porigin_method) '
                     'phpType7* n_arg poperand* (porigin_site) z -- if S.CURRENT = (pcallcontext) '
                     '-- if $class_method_origin(S.CLASSES, porigin_method) = (pmethoddesc) '
                     f'-- if pmethoddesc.VISIBILITY = {visibility}')
        fixture = directory / 'test.watsup'
        fixture.write_text(
            'dec $stage(pstate) : bool\n'
            f'def $stage(S) = true -- if {stage}\n'
            'def $stage(S) = false -- otherwise\n'
            'dec $seek(pstate, nat) : pstate\n'
            'def $seek(S, n) = S -- if $stage(S)\n'
            'def $seek(S, n) = $seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1))) -- if ~$stage(S) -- if $(n > 0)\n'
            'dec $main() : bool\ndef $main() = true\n'
            '  -- if S_initial = $php_run(' + checked['fixture'] + ', 0, '
            + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')\n'
            '  -- if S = $seek(S_initial[.COMPLETION = NORMAL], 2000)[.COMPLETION = NORMAL]\n'
            f'  -- if {stage}\n'
            + ''.join('  -- if ' + clause + '\n' for clause in checks))
        result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                 *map(str, MODULES), str(fixture)], capture_output=True,
                                text=True, timeout=300)
        (directory / 'stdout').write_text(result.stdout)
        (directory / 'stderr').write_text(result.stderr)
        passed = result.returncode == 0 and result.stdout == 'true\n' and not result.stderr
        records.append({'id': name, 'source_id': source_id,
                        'assertions': len(checks) + 3, 'pass': passed})
        print(name, passed, flush=True)
        if not passed:
            print(result.stderr[-2200:], flush=True)
    stable = before == {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    report = {'result': 'pass' if stable and all(r['pass'] for r in records) else 'fail',
              'stable': stable, 'records': records, 'inputs': before}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    assert report['result'] == 'pass'


if __name__ == '__main__':
    run()
