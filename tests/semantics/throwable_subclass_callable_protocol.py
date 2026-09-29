#!/usr/bin/env python3
"""Paused inherited getter capture on a source ErrorException descendant."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
MODULES = [ROOT / name for name in json.loads(
    (ROOT / 'spec/semantics/modules.json').read_text())]
SOURCE = b'<?php class C extends ErrorException {} $e=new C("m",0,13); $c=$e->getSeverity(...); $e=null; echo $c();'
STAGES = [
    ('capture',
     'S.RESULT = KNOWN (POBJECT n) '
     '-- if S.OBJECTS[n] = GETTERCLOSURE n_receiver GET_SEVERITY text_base porigin_site', [
         'text_base = "ErrorException"',
         'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
         '$class_throwable_kind(S,porigin_class,|S.CLASSES|) = ("ErrorException")',
         '$getter_capture_live(S,n)',
         '$closure_live_object_valid(S,n)',
         '$closure_callable(S,n)',
         '$node_children(S,HOBJECT n) = [HOBJECT n_receiver]',
         '~$closure_scope_complete(S[.CLOSURESCOPES = [{OBJECT n, LEXICAL PORIGIN 0 eps, CALLED PORIGIN 0 eps, RECEIVER eps}]], S.ALLOCATIONS)',
         '~$getter_capture_live(S[.OBJECTS = $object_set(S.OBJECTS,n,GETTERCLOSURE n_receiver GET_MESSAGE text_base porigin_site)],n)',
         '~$getter_capture_live(S[.OBJECTS = $object_set(S.OBJECTS,n,GETTERCLOSURE 9999 GET_SEVERITY text_base porigin_site)],n)',
         '~$getter_capture_live(S[.OBJECTS = $object_set(S.OBJECTS,n,GETTERCLOSURE n_receiver GET_SEVERITY text_base porigin_class)],n)',
     ]),
    ('invocation',
     'S.TODO = (GETTER_ARGS pgettercall) :: ptask_tail* '
     '-- if pgettercall.CAPTURE = (n) '
     '-- if pgettercall.METHOD = GET_SEVERITY', [
         'pgettercall.BASE = "ErrorException"',
         '$getter_call_valid(S,pgettercall)',
         '$call_task_valid(S,GETTER_ARGS pgettercall)',
         'HOBJECT n <- $task_nodes(GETTER_ARGS pgettercall)',
         'HOBJECT pgettercall.RECEIVER <- $node_children(S,HOBJECT n)',
         '(HOBJECT pgettercall.RECEIVER) <- S.ALLOCATIONS',
         '~$call_task_valid(S,GETTER_ARGS pgettercall[.CAPTURE = eps])',
         '~$call_task_valid(S,GETTER_ARGS pgettercall[.RECEIVER = 9999])',
         '~$call_task_valid(S,GETTER_ARGS pgettercall[.METHOD = GET_MESSAGE])',
     ]),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = Path(tempfile.mkdtemp(prefix='throwable-subclass-callable-', dir=ROOT / '.tools'))
    source = output / 'source.php'
    source.write_bytes(SOURCE)
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], output / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], output / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(SOURCE).decode()})
        assert parsed['accepted'], parsed
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'], checked
    finally:
        frontend.close()
        adapter.close()
    inputs = [*MODULES, ROOT / 'spec/semantics/modules.json', Path(__file__),
              ROOT / 'frontend/worker.php', ROOT / 'frontend/wire.php',
              ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
              ROOT / '_build/default/adapter/main.exe',
              ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    before = {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    initial = ('$php_run(' + checked['fixture'] + ', 0, ' +
               json.dumps(base64.b64encode(str(source).encode()).decode()) + ')')
    records = []
    for name, stage, checks in STAGES:
        directory = output / name
        directory.mkdir()
        fixture = directory / 'protocol.watsup'
        fixture.write_text(
            'dec $stage(pstate) : bool\n'
            f'def $stage(S) = true -- if {stage}\n'
            'def $stage(S) = false -- otherwise\n'
            'dec $seek(pstate, nat) : pstate\n'
            'def $seek(S, n) = S -- if $stage(S)\n'
            'def $seek(S, n) = $seek($drive_steps(S[.COMPLETION = NORMAL],1),'
            '$nabs($(n - 1))) -- if ~$stage(S) -- if $(n > 0)\n'
            'dec $main() : bool\ndef $main() = true\n'
            f'  -- if S_initial = {initial}\n'
            '  -- if S = $seek(S_initial[.COMPLETION = NORMAL],400)[.COMPLETION = NORMAL]\n'
            f'  -- if {stage}\n'
            '  -- if $closure_state_valid(S)\n'
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
        records.append({'id': name, 'assertions': len(checks) + 5,
                        'fixture_sha256': digest(fixture), 'pass': passed})
        print(name, passed, flush=True)
        if not passed:
            print(result.stderr[-1600:], flush=True)
    stable = before == {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    report = {'result': 'pass' if stable and all(row['pass'] for row in records) else 'fail',
              'stable': stable, 'source_sha256': digest(source),
              'inputs': before, 'records': records, 'raw': str(output)}
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(output, report['result'])
    assert report['result'] == 'pass'


if __name__ == '__main__':
    main()
