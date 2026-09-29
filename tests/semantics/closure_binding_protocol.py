#!/usr/bin/env python3
"""Paused source-authentication checks for ordinary Closure binding."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
MODULES = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
CASES = {
    'bindto-selector': {
        'source': '<?php class A {} $a=function(){return "A";}; $b=function(){return "B";}; '
                  '$c=$a->bindTo(new A); echo $c();',
        'stage': ('S.TODO = (BIND_ARGS pbindcall) :: ptask_tail* '
                  '-- if pbindcall.KIND = INSTANCE_BIND -- if pbindcall.INDEX = 0'),
        'checks': [
            'pbindcall.SOURCE = (n_a)',
            '$lookup(S.ENV, $ptascii("a")) = (n_cell_a)',
            'S.STORE[n_cell_a] = DEFINED (POBJECT n_a)',
            '$lookup(S.ENV, $ptascii("b")) = (n_cell_b)',
            'S.STORE[n_cell_b] = DEFINED (POBJECT n_b)',
            '$call_task_valid(S, BIND_ARGS pbindcall)',
            'HOBJECT n_a <- $task_nodes(BIND_ARGS pbindcall)',
            '~$call_task_valid(S, BIND_ARGS pbindcall[.SOURCE = (n_b)])',
        ],
    },
    'bind-first-argument': {
        'source': '<?php class A {} $a=function(){return "A";}; $b=function(){return "B";}; '
                  '$c=Closure::bind($a,new A,A::class); echo $c();',
        'stage': ('S.TODO = (BIND_ARGS pbindcall) :: ptask_tail* '
                  '-- if pbindcall.KIND = STATIC_BIND -- if pbindcall.INDEX = 1'),
        'checks': [
            'pbindcall.SENT = [KNOWN (POBJECT n_a)]',
            '$lookup(S.ENV, $ptascii("a")) = (n_cell_a)',
            'S.STORE[n_cell_a] = DEFINED (POBJECT n_a)',
            '$lookup(S.ENV, $ptascii("b")) = (n_cell_b)',
            'S.STORE[n_cell_b] = DEFINED (POBJECT n_b)',
            '$call_task_valid(S, BIND_ARGS pbindcall)',
            'HOBJECT n_a <- $task_nodes(BIND_ARGS pbindcall)',
            '~$call_task_valid(S, BIND_ARGS pbindcall[.SENT = [KNOWN (POBJECT n_b)]])',
        ],
    },
    'bound-source-release': {
        'source': '<?php $a=function(){return 7;}; $b=$a->bindTo(null); unset($a); echo $b();',
        'stage': ('S.TODO = (CALL_ARGS (CLOSURE_TARGET n_bound) phpType7* n_arg '
                  'poperand* porigin_site? z) :: ptask_tail* '
                  '-- if $closure_binding_at(S.CLOSUREBINDINGS, n_bound) = (pclosurebinding)'),
        'checks': [
            'pclosurebinding.SOURCE = n_source',
            '(HOBJECT n_bound) <- S.ALLOCATIONS',
            '~((HOBJECT n_source) <- S.ALLOCATIONS)',
            '$node_children(S, HOBJECT n_bound) = eps',
            '$closure_binding_source_valid(S, pclosurebinding)',
            '$call_task_valid(S, CALL_ARGS (CLOSURE_TARGET n_bound) phpType7* n_arg '
            'poperand* porigin_site? z)',
        ],
    },
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    output = Path(tempfile.mkdtemp(prefix='closure-binding-protocol-', dir=ROOT / '.tools'))
    inputs = [*MODULES, ROOT / 'spec/semantics/modules.json', ROOT / 'spec/php.watsup',
              ROOT / 'spec/schema.json', ROOT / 'frontend/worker.php',
              ROOT / '_build/default/adapter/main.exe',
              ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
              ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so', Path(__file__)]
    before = {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    records = []
    for name, case in CASES.items():
        directory = output / name
        directory.mkdir()
        source = directory / 'source.php'
        source.write_text(case['source'])
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                           'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], directory / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'], name
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], name
        finally:
            frontend.close()
            adapter.close()
        fixture = directory / 'test.watsup'
        fixture.write_text(
            'dec $stage(pstate) : bool\n'
            'def $stage(S) = true -- if ' + case['stage'] + '\n'
            'def $stage(S) = false -- otherwise\n'
            'dec $seek(pstate, nat) : pstate\n'
            'def $seek(S, n) = S -- if $stage(S)\n'
            'def $seek(S, n) = $seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1))) '
            '-- if ~$stage(S) -- if $(n > 0)\n'
            'dec $main() : bool\ndef $main() = true\n'
            '  -- if S_initial = $php_run(' + checked['fixture'] + ', 0, '
            + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')\n'
            '  -- if S = $seek(S_initial[.COMPLETION = NORMAL], 2000)[.COMPLETION = NORMAL]\n'
            '  -- if ' + case['stage'] + '\n'
            + ''.join('  -- if ' + clause + '\n' for clause in case['checks']))
        result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                 *map(str, MODULES), str(fixture)], capture_output=True,
                                text=True, timeout=300)
        (directory / 'stdout').write_text(result.stdout)
        (directory / 'stderr').write_text(result.stderr)
        passed = result.returncode == 0 and result.stdout == 'true\n' and not result.stderr
        records.append({'id': name, 'source_sha256': digest(source),
                        'assertions': len(case['checks']) + 3, 'pass': passed})
        print(name, passed, flush=True)
        if not passed:
            print(result.stderr[-2500:], flush=True)
    stable = before == {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    report = {'result': 'pass' if stable and all(row['pass'] for row in records) else 'fail',
              'stable': stable, 'records': records, 'inputs': before}
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(output, report['result'])
    assert report['result'] == 'pass'


if __name__ == '__main__':
    run()
