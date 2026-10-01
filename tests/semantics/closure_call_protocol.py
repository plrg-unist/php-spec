#!/usr/bin/env python3
"""Paused source-authentication checks for Closure::call."""
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
    'call-selector': {
        'source': '<?php class A {} $a=function(){return "A";}; $b=function(){return "B";}; '
                  '$r=new A; echo $a->call($r);',
        'stage': ('S.TODO = (CLOSURE_CALL_ARGS pclosurecall) :: ptask_tail* '
                  '-- if pclosurecall.INDEX = 0'),
        'checks': [
            'pclosurecall.SOURCE = n_a',
            '$lookup(S.ENV, $ptascii("a")) = (n_cell_a)',
            'S.STORE[n_cell_a] = DEFINED (POBJECT n_a)',
            '$lookup(S.ENV, $ptascii("b")) = (n_cell_b)',
            'S.STORE[n_cell_b] = DEFINED (POBJECT n_b)',
            '$call_task_valid(S, CLOSURE_CALL_ARGS pclosurecall)',
            '$call_descriptors_valid(S)',
            '$closure_state_valid(S)',
            '$heap_valid($heap_graph(S))',
            'HOBJECT n_a <- $task_nodes(CLOSURE_CALL_ARGS pclosurecall)',
            '~$call_task_valid(S, CLOSURE_CALL_ARGS pclosurecall[.SOURCE = n_b])',
            '~$call_task_valid(S, CLOSURE_CALL_ARGS pclosurecall[.LINE = $(pclosurecall.LINE + 100)])',
        ],
    },
    'call-receiver': {
        'source': '<?php class A {} $a=new A; $b=new A; $c=function(){return "A";}; '
                  'echo $c->call($a);',
        'stage': ('S.TODO = (CLOSURE_CALL_ARGS pclosurecall) :: ptask_tail* '
                  '-- if pclosurecall.INDEX = 1'),
        'checks': [
            'pclosurecall.RECEIVER = (n_a)',
            '$lookup(S.ENV, $ptascii("a")) = (n_cell_a)',
            'S.STORE[n_cell_a] = DEFINED (POBJECT n_a)',
            '$lookup(S.ENV, $ptascii("b")) = (n_cell_b)',
            'S.STORE[n_cell_b] = DEFINED (POBJECT n_b)',
            '$call_task_valid(S, CLOSURE_CALL_ARGS pclosurecall)',
            '$call_descriptors_valid(S)',
            '$closure_state_valid(S)',
            '$heap_valid($heap_graph(S))',
            'HOBJECT n_a <- $task_nodes(CLOSURE_CALL_ARGS pclosurecall)',
            '~$call_task_valid(S, CLOSURE_CALL_ARGS pclosurecall[.RECEIVER = (n_b)])',
        ],
    },
    'call-stdclass-pending': {
        'source': '<?php $c=function($x){}; $c->call(new stdClass,1);',
        'stage': ('S.TODO = (CLOSURE_CALL_INVOKE pclosurecall) :: ptask_tail* '
                  '-- if pclosurecall.RECEIVER = (n_receiver) '
                  '-- if S.OBJECTS[n_receiver] = STDINSTANCE'),
        'checks': [
            'pclosurecall.SOURCE = n_source',
            '(HOBJECT n_source) <- S.ALLOCATIONS',
            '(HOBJECT n_receiver) <- S.ALLOCATIONS',
            'HOBJECT n_receiver <- $task_nodes(CLOSURE_CALL_INVOKE pclosurecall)',
            '$call_task_valid(S, CLOSURE_CALL_INVOKE pclosurecall)',
            '~$call_selected_valid(S, CLOSURE_CALL_TARGET n_source n_receiver, (pclosurecall.SITE))',
            '$call_descriptors_valid(S)',
            '$closure_state_valid(S)',
            '$heap_valid($heap_graph(S))',
        ],
    },
    'call-rebound-source': {
        'source': '<?php class A {} $c=function(){return get_class($this);}; '
                  'echo $c->call((function() use (&$c){$c=null;return new A;})());',
        'stage': ('S.TODO = (CLOSURE_CALL_INVOKE pclosurecall) :: ptask_tail* '
                  '-- if pclosurecall.RECEIVER = (n_receiver)'),
        'checks': [
            'pclosurecall.SOURCE = n_source',
            '$lookup(S.ENV, $ptascii("c")) = (n_cell_c)',
            'S.STORE[n_cell_c] = DEFINED PNULL',
            '(HOBJECT n_source) <- S.ALLOCATIONS',
            'HOBJECT n_source <- $task_nodes(CLOSURE_CALL_INVOKE pclosurecall)',
            'HOBJECT n_receiver <- $task_nodes(CLOSURE_CALL_INVOKE pclosurecall)',
            '$call_task_valid(S, CLOSURE_CALL_INVOKE pclosurecall)',
            '$call_descriptors_valid(S)',
            '$closure_state_valid(S)',
            '$heap_valid($heap_graph(S))',
            '$call_selected_valid(S, CLOSURE_CALL_TARGET n_source n_receiver, (pclosurecall.SITE))',
        ],
    },
    'call-invalid-first': {
        'source': '<?php $c=function($x){}; try {$c->call(null,z:1,x:2);} catch (TypeError $e) {}',
        'stage': ('S.TODO = (CLOSURE_CALL_ARGS pclosurecall) :: ptask_tail* '
                  '-- if pclosurecall.INDEX = 1'),
        'checks': [
            'pclosurecall.FIRST = (PNULL)',
            'pclosurecall.RECEIVER = eps',
            'pclosurecall.ERROR = eps',
            'pclosurecall.SENT = pnamedargs',
            '$call_task_valid(S, CLOSURE_CALL_ARGS pclosurecall)',
            '$call_descriptors_valid(S)',
            '$closure_state_valid(S)',
            '$heap_valid($heap_graph(S))',
            'HOBJECT pclosurecall.SOURCE <- $task_nodes(CLOSURE_CALL_ARGS pclosurecall)',
            '~$call_task_valid(S, CLOSURE_CALL_ARGS pclosurecall[.ERROR = ($ptascii("forged"))])',
            '~$call_task_valid(S, CLOSURE_CALL_ARGS pclosurecall[.SENT = pnamedargs[.NAMED = [($ptascii("x"), KNOWN PNULL)]]])',
        ],
    },
    'call-invalid-raw-root': {
        'source': '<?php class A {} $c=function($x){}; try {$c->call(null,z:new A,x:2);} catch (TypeError $e) {}',
        'stage': ('S.TODO = (CLOSURE_CALL_INVOKE pclosurecall) :: ptask_tail* '
                  '-- if pclosurecall.FIRST = (PNULL)'),
        'checks': [
            'pclosurecall.ERROR = (preqbytes)',
            'pclosurecall.SENT = pnamedargs',
            'pclosurecall.RAW[0] = (KSTRING n_name*, KNOWN (POBJECT n_raw))',
            'HOBJECT n_raw <- $task_nodes(CLOSURE_CALL_INVOKE pclosurecall)',
            '$call_task_valid(S, CLOSURE_CALL_INVOKE pclosurecall)',
            '$call_descriptors_valid(S)',
            '$closure_state_valid(S)',
            '$heap_valid($heap_graph(S))',
            '~$call_task_valid(S, CLOSURE_CALL_INVOKE pclosurecall[.ERROR = ($ptascii("forged"))])',
            '~$call_task_valid(S, CLOSURE_CALL_INVOKE pclosurecall[.SENT = pnamedargs[.NAMED = [($ptascii("x"), KNOWN PNULL)]]])',
            '~$call_task_valid(S, CLOSURE_CALL_INVOKE pclosurecall[.RAW = [(KSTRING n_name*, VARIABLE $ptascii("x") 1), pclosurecall.RAW[1]]])',
            '~$call_task_valid(S, CLOSURE_CALL_INVOKE pclosurecall[.RAW = [(KSTRING n_name*, REFERENCE n_raw), pclosurecall.RAW[1]]])',
            '~$call_task_valid(S, CLOSURE_CALL_INVOKE pclosurecall[.LINE = $(pclosurecall.LINE + 100)])',
        ],
    },
    'call-raw-sent': {
        'source': '<?php class A {} $c=function($x){}; $c->call(new A,1);',
        'stage': ('S.TODO = (CLOSURE_CALL_INVOKE pclosurecall) :: ptask_tail* '
                  '-- if pclosurecall.RAW = [(KINT 1, KNOWN (PINT 1))]'),
        'checks': [
            'pclosurecall.SENT.SLOTS = [NAMED_SENT (KNOWN (PINT 1))]',
            '$call_task_valid(S, CLOSURE_CALL_INVOKE pclosurecall)',
            '$call_descriptors_valid(S)',
            '$closure_state_valid(S)',
            '$heap_valid($heap_graph(S))',
            '~$call_task_valid(S, CLOSURE_CALL_INVOKE pclosurecall[.RAW = [(KINT 1, KNOWN (PINT 9))]])',
            '~$call_task_valid(S, CLOSURE_CALL_INVOKE pclosurecall[.LINE = $(pclosurecall.LINE + 100)])',
        ],
    },
    'call-undefined-first-variable': {
        'source': '<?php $c=function($x){}; try {$c->call($missing,1);} catch (TypeError $e) {echo "C";}',
        'stage': ('S.TODO = (CLOSURE_CALL_ARGS pclosurecall) :: ptask_tail* '
                  '-- if pclosurecall.INDEX = 1'),
        'checks': [
            'pclosurecall.FIRST = (PNULL)',
            'pclosurecall.RECEIVER = eps',
            '$call_task_valid(S, CLOSURE_CALL_ARGS pclosurecall)',
            '$call_descriptors_valid(S)',
            '$closure_state_valid(S)',
            '$heap_valid($heap_graph(S))',
            '~$call_task_valid(S, CLOSURE_CALL_ARGS pclosurecall[.FIRST = (PINT 1)])',
        ],
    },
    'call-named-body-wrapper': {
        'source': '<?php class A {} $c=function($x,$y){throw new Exception("x");}; $c->call(new A,y:2,x:1);',
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.TARGET = CLOSURE_CALL_TARGET n_source n_receiver '
                  '-- if pcallcontext.WRAPPER = (pnamedargs)'),
        'checks': [
            'pnamedargs.SLOTS = eps',
            'pnamedargs.NAMED = [($ptascii("y"), KNOWN (PINT 2)), ($ptascii("x"), KNOWN (PINT 1))]',
            'pcallcontext.ARGC = 2',
            'pcallcontext.NAMED = eps',
            '$wrapper_context_valid(S, pcallcontext)',
            '$call_descriptors_valid(S)',
            '$closure_state_valid(S)',
            '$heap_valid($heap_graph(S))',
            '~$wrapper_context_valid(S, pcallcontext[.WRAPPER = (pnamedargs[.NAMED = [($ptascii("x"), KNOWN (PINT 1)), ($ptascii("y"), KNOWN (PINT 2))]])])',
            '~$wrapper_context_valid(S, pcallcontext[.WRAPPER = (pnamedargs[.NAMED = [($ptascii("y"), VARIABLE $ptascii("x") 1), ($ptascii("x"), KNOWN (PINT 1))]])])',
        ],
    },
    'call-reference-return-used': {
        'source': '<?php class A {} $c=function &(){$x=1;return $x;}; $c->call(new A);',
        'stage': ('S.TODO = (RETURN_REF_FETCH z) :: ptask_tail* '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.TARGET = CLOSURE_CALL_TARGET n_source n_receiver'),
        'checks': [
            '$reference_return_used(S)',
            '$call_task_valid(S, RETURN_REF_FETCH z)',
            '$call_descriptors_valid(S)',
            '$closure_state_valid(S)',
            '$heap_valid($heap_graph(S))',
        ],
    },
    'call-reference-result-unwrapped': {
        'source': '<?php class A {} $x=1; $c=function &() use (&$x){return $x;}; $v =& $c->call(new A); $v=2; echo $x;',
        'stage': ('S.TODO = (CLOSURE_CALL_RESULT porigin z) :: ptask_tail* '
                  '-- if S.RESULT = REFERENCE n_cell'),
        'checks': [
            '$call_task_valid(S, CLOSURE_CALL_RESULT porigin z)',
            '$call_descriptors_valid(S)',
            '$closure_state_valid(S)',
            '$heap_valid($heap_graph(S))',
            '~$call_task_valid(S, CLOSURE_CALL_RESULT porigin $(z + 100))',
            'S_after = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
            'S_after.RESULT = KNOWN (PINT 1)',
            'S_after.BASE = BASE_VALUE (KNOWN (PINT 1))',
            'S_after.STORE[n_cell] = DEFINED (PINT 1)',
            '$call_descriptors_valid(S_after)',
            '$closure_state_valid(S_after)',
            '$heap_valid($heap_graph(S_after))',
        ],
    },
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    output = Path(tempfile.mkdtemp(prefix='closure-call-protocol-', dir=ROOT / '.tools'))
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
