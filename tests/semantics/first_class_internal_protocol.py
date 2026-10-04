#!/usr/bin/env python3
"""Paused ownership and provenance controls for finite internal captures."""
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
    'getter-capture-edge': {
        'source': '<?php $e=new Exception("X"); $c=$e->getMessage(...); $e=null; echo $c();',
        'stage': ('S.RESULT = KNOWN (POBJECT n) '
                  '-- if S.OBJECTS[n] = GETTERCLOSURE n_receiver GET_MESSAGE text_base porigin_site'),
        'checks': [
            '$getter_capture_live(S, n)',
            '$closure_live_object_valid(S, n)',
            '$closure_callable(S, n)',
            '$node_children(S, HOBJECT n) = [HOBJECT n_receiver]',
            '~$closure_scope_complete(S[.CLOSURESCOPES = [{OBJECT n, LEXICAL PORIGIN 0 eps, CALLED PORIGIN 0 eps, RECEIVER eps, CREATION eps}]], S.ALLOCATIONS)',
            '~$getter_capture_live(S[.OBJECTS = $object_set(S.OBJECTS, n, GETTERCLOSURE n_receiver GET_CODE text_base porigin_site)], n)',
            '~$getter_capture_live(S[.OBJECTS = $object_set(S.OBJECTS, n, GETTERCLOSURE 9999 GET_MESSAGE text_base porigin_site)], n)',
        ],
    },
    'invoke-capture-edge': {'source': '<?php $f=fn()=>"X"; $c=$f->__invoke(...); unset($f); echo $c();',
                            'stage': 'S.RESULT = KNOWN (POBJECT n) -- if S.OBJECTS[n] = REALCLOSURE porigin_template pitem* '
                                     'pstaticcell* -- if S.ORIGIN = (porigin_site) -- if $invoke_capture_source(S, '
                                     'porigin_site)',
                            'checks': ['$closure_callable(S, n)',
                                       '$closure_live_object_valid(S, n)',
                                       '$node_children(S, HOBJECT n) = eps',
                                       '~$closure_scope_complete(S[.CLOSURESCOPES = [{OBJECT n, LEXICAL PORIGIN 0 eps, '
                                       'CALLED PORIGIN 0 eps, RECEIVER eps, CREATION eps}]], S.ALLOCATIONS)',
                                       '~$closure_callable(S[.OBJECTS = $object_set(S.OBJECTS, n, INVOKECLOSURE n '
                                       'porigin_site)], n)',
                                       '~$closure_callable(S[.OBJECTS = $object_set(S.OBJECTS, n, INVOKECLOSURE 9999 '
                                       'porigin_site)], n)',
                                       'S_global = $global_table_view(S)',
                                       '$lookup(S_global.ENV, $ptascii("f")) = (n_f)',
                                       'S.STORE[n_f] = DEFINED (POBJECT n)']},
    'getter-invoke-wrapper': {'source': '<?php $e=new Exception("X"); $c=$e->getMessage(...); $w=$c->__invoke(...); $e=null; '
                                        'unset($c); echo $w();',
                              'stage': 'S.RESULT = KNOWN (POBJECT n) -- if S.OBJECTS[n] = GETTERCLOSURE n_receiver '
                                       'GET_MESSAGE text_base porigin_getter -- if S.ORIGIN = (porigin_site) -- if '
                                       '$invoke_capture_source(S, porigin_site)',
                              'checks': ['$closure_callable(S, n)',
                                         '$closure_live_object_valid(S, n)',
                                         '$getter_capture_live(S, n)',
                                         '$node_children(S, HOBJECT n) = [HOBJECT n_receiver]',
                                         'S_global = $global_table_view(S)',
                                         '$lookup(S_global.ENV, $ptascii("c")) = (n_c)',
                                         'S.STORE[n_c] = DEFINED (POBJECT n)',
                                         '~$closure_live_object_valid(S[.OBJECTS = $object_set(S.OBJECTS, n, INVOKECLOSURE '
                                         '9999 porigin_site)], n)']},
    'getter-wrapper-after-release': {'source': '<?php $e=new Exception("X"); $c=$e->getMessage(...); $w=$c->__invoke(...); $e=null; '
                                               'unset($c); echo $w();',
                                     'stage': 'S.TODO = (GETTER_ARGS pgettercall) :: ptask_tail* -- if pgettercall.CAPTURE = '
                                              '(n_source) -- if S.OBJECTS[n_source] = GETTERCLOSURE n_receiver GET_MESSAGE text_base '
                                              'porigin_getter -- if S_global = $global_table_view(S) -- if $lookup(S_global.ENV, '
                                              '$ptascii("w")) = (n_cell) -- if S.STORE[n_cell] = DEFINED (POBJECT n) -- if n = '
                                              'n_source -- if $lookup(S_global.ENV, $ptascii("c")) = eps -- if $lookup(S_global.ENV, '
                                              '$ptascii("e")) = (n_ecell) -- if S.STORE[n_ecell] = DEFINED PNULL',
                                     'checks': ['$call_task_valid(S, GETTER_ARGS pgettercall)',
                                                '$closure_callable(S, n)',
                                                '$getter_capture_live(S, n_source)',
                                                '(HOBJECT n) <- S.ALLOCATIONS',
                                                '(HOBJECT n_source) <- S.ALLOCATIONS',
                                                '(HOBJECT n_receiver) <- S.ALLOCATIONS',
                                                '$node_children(S, HOBJECT n) = [HOBJECT n_receiver]',
                                                '$node_children(S, HOBJECT n_source) = [HOBJECT n_receiver]']},
    'invoke-after-unset': {
        'source': '<?php $f=fn()=>"X"; $c=$f->__invoke(...); unset($f); echo $c();',
        'stage': ('S.TODO = (CALL_ARGS (CLOSURE_TARGET n_source) phpType7* n_arg '
                  'poperand* (porigin_call) z) :: ptask_tail* '
                  '-- if S.OBJECTS[n_source] = REALCLOSURE porigin_template pitem* pstaticcell*'),
        'checks': [
            '$call_task_valid(S, CALL_ARGS (CLOSURE_TARGET n_source) phpType7* n_arg poperand* (porigin_call) z)',
            '(HOBJECT n_source) <- S.ALLOCATIONS',
            'HOBJECT n_source <- $task_nodes(CALL_ARGS (CLOSURE_TARGET n_source) phpType7* n_arg poperand* (porigin_call) z)',
        ],
    },
    'getter-pending': {
        'source': '<?php $e=new Exception("X"); $c=$e->getMessage(...); $e=null; echo $c();',
        'stage': ('S.TODO = (GETTER_ARGS pgettercall) :: ptask_tail* '
                  '-- if pgettercall.CAPTURE = (n) '
                  '-- if pgettercall.METHOD = GET_MESSAGE'),
        'checks': [
            '$getter_call_valid(S, pgettercall)',
            '$call_task_valid(S, GETTER_ARGS pgettercall)',
            'HOBJECT n <- $task_nodes(GETTER_ARGS pgettercall)',
            'HOBJECT pgettercall.RECEIVER <- $node_children(S, HOBJECT n)',
            '(HOBJECT pgettercall.RECEIVER) <- S.ALLOCATIONS',
            '~$call_task_valid(S, GETTER_ARGS pgettercall[.CAPTURE = eps])',
            '~$call_task_valid(S, GETTER_ARGS pgettercall[.RECEIVER = 9999])',
            '~$call_task_valid(S, GETTER_ARGS pgettercall[.METHOD = GET_CODE])',
        ],
    },
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    output = Path(tempfile.mkdtemp(prefix='first-class-internal-protocol-', dir=ROOT / '.tools'))
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
            '  -- if $closure_state_valid(S)\n'
            + ''.join('  -- if ' + clause + '\n' for clause in case['checks']))
        result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                 *map(str, MODULES), str(fixture)], capture_output=True,
                                text=True, timeout=300)
        (directory / 'stdout').write_text(result.stdout)
        (directory / 'stderr').write_text(result.stderr)
        passed = result.returncode == 0 and result.stdout == 'true\n' and not result.stderr
        records.append({'id': name, 'source_sha256': digest(source),
                        'assertions': len(case['checks']) + 4, 'pass': passed})
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
