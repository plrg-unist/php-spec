#!/usr/bin/env python3
"""Paused scoped-call source and selected-target provenance controls."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import sys
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
MODULES = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
CASES = {
    'missing-literal-name': {
        'source': '<?php function name(){echo "name";return "f";} Missing::{name()}();',
        'stage': ('S.TODO = (SCOPED_NAME phpType19 poperand phpType7* z) :: ptask_tail* '
                  '-- if poperand = KNOWN (PSTRING n_class*)'),
        'checks': [
            '$call_task_valid(S, SCOPED_NAME phpType19 poperand phpType7* z)',
            'n_class* = $ptascii("Missing")',
            '~$call_task_valid(S, SCOPED_NAME phpType19 (KNOWN (PSTRING $ptascii("Other"))) phpType7* z)',
        ],
    },
    'dynamic-selected': {
        'source': ('<?php function cls(){return "A";} class A {public static function f(){echo "A";}} '
                   'class B extends A {} cls()::f();'),
        'stage': ('S.TODO = ptask :: ptask_tail* '
                  '-- if ptask = CALL_ARGS (SCOPED_TARGET porigin_requested porigin_method '
                  'porigin_called n_receiver? poperand_selector) phpType7* n_arg '
                  'poperand* (porigin_site) z '
                  '-- if poperand_selector = KNOWN (PSTRING n_class*)'),
        'checks': [
            '$call_task_valid(S, ptask)',
            '$call_selected_valid(S, SCOPED_TARGET porigin_requested porigin_method porigin_called n_receiver? poperand_selector, (porigin_site))',
            '$class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)',
            '~$call_selected_valid(S, SCOPED_TARGET porigin_b porigin_method porigin_called n_receiver? poperand_selector, (porigin_site))',
            '~$call_selected_valid(S, SCOPED_TARGET porigin_requested porigin_method porigin_called n_receiver? (KNOWN (PSTRING $ptascii("B"))), (porigin_site))',
            '~$call_selected_valid(S, SCOPED_TARGET porigin_requested porigin_method porigin_b n_receiver? poperand_selector, (porigin_site))',
            # Known provenance limit: the completed dynamic class expression's value
            # cannot be recovered when all three stored class fields are forged.
            '$call_selected_valid(S, SCOPED_TARGET porigin_b porigin_method porigin_b n_receiver? (KNOWN (PSTRING $ptascii("B"))), (porigin_site))',
        ],
        'known_limit': 'paired dynamic selector/requested/called swap remains accepted',
    },
    'saved-forwarded-self': {
        'source': ('<?php class A {public static function go(){self::f();} '
                   'public static function f(){echo static::class;}} class B extends A {} B::go();'),
        'stage': ('S.CURRENT = (pcallcontext_callee) '
                  '-- if pcallcontext_callee.TARGET = SCOPED_TARGET porigin_requested '
                  'porigin_method porigin_called n_receiver? poperand_selector '
                  '-- if pcallcontext_callee.CALLSITE = (porigin_site) '
                  '-- if S.FRAMES = pframe :: pframe_tail* '
                  '-- if pframe.CONTEXT = (pcallcontext_caller) '
                  '-- if $class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b) '
                  '-- if pcallcontext_callee.CALLED_CLASS = (porigin_b)'),
        'checks': [
            '$call_current_valid(S)',
            '$call_selected_valid(S, SCOPED_TARGET porigin_requested porigin_method porigin_called n_receiver? poperand_selector, (porigin_site))',
            '~$call_current_valid(S[.CURRENT = (pcallcontext_callee[.TARGET = SCOPED_TARGET porigin_requested porigin_method porigin_requested n_receiver? poperand_selector])])',
            '~$call_selected_valid(S[.FRAMES = (pframe[.CONTEXT = (pcallcontext_caller[.LEXICAL_CLASS = (porigin_b)])]) :: pframe_tail*], SCOPED_TARGET porigin_requested porigin_method porigin_called n_receiver? poperand_selector, (porigin_site))',
            '~$call_current_valid(S[.FRAMES = (pframe[.CONTEXT = (pcallcontext_caller[.LEXICAL_CLASS = (porigin_b)])]) :: pframe_tail*])',
        ],
    },
    'object-selector-roots': {
        'source': ('<?php class A { public static function f(){echo "A";} } '
                   'class B { public static function f(){echo "B";} } '
                   '$a = new A; $b = new B; $a::{"f"}();'),
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.TARGET = SCOPED_TARGET porigin_requested '
                  'porigin_method porigin_called n_receiver? (KNOWN (POBJECT n_selector)) '
                  '-- if pcallcontext.CALLSITE = (porigin_site)'),
        'checks': [
            '$call_current_valid(S)',
            'HOBJECT n_selector <- $call_context_roots(S.CURRENT)',
            '$call_selected_valid(S, pcallcontext.TARGET, (porigin_site))',
            '~$call_selected_valid(S, SCOPED_TARGET porigin_requested porigin_method '
            'porigin_called n_receiver? (KNOWN (PSTRING $ptascii("B"))), (porigin_site))',
            '~$call_selected_valid(S, SCOPED_TARGET porigin_requested porigin_method '
            'porigin_called n_receiver? (KNOWN (POBJECT 9999)), (porigin_site))',
            '~$call_current_valid(S[.CURRENT = (pcallcontext[.TARGET = SCOPED_TARGET '
            'porigin_requested porigin_method porigin_called n_receiver? '
            '(KNOWN (PSTRING $ptascii("B")))])])',
        ],
    },
    'object-selector-name-root': {
        'source': ('<?php function name(){return "f";} class A {public static function f(){echo "A";}} '
                   '$a = new A; $a::{name()}();'),
        'stage': ('S.TODO = ptask_head :: (SCOPED_NAME phpType19 '
                  '(KNOWN (POBJECT n_selector)) phpType7* z) :: ptask_tail*'),
        'checks': [
            'HOBJECT n_selector <- $tasks_nodes(S.TODO)',
            '$call_task_valid(S, SCOPED_NAME phpType19 (KNOWN (POBJECT n_selector)) phpType7* z)',
            '~$call_task_valid(S, SCOPED_NAME phpType19 '
            '(KNOWN (PSTRING $ptascii("Missing"))) phpType7* z)',
        ],
    },
    'nonstatic-explicit-called': {
        'source': ('<?php class A {public function f(){echo static::class;}} '
                   'class B extends A {public function run(){A::f();}} (new B)->run();'),
        'stage': ('S.CURRENT = (pcallcontext_callee) '
                  '-- if pcallcontext_callee.TARGET = SCOPED_TARGET porigin_requested '
                  'porigin_method porigin_called (n_receiver) poperand_selector '
                  '-- if porigin_requested =/= porigin_called'),
        'checks': [
            '$call_current_valid(S)',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_called',
            '~$call_current_valid(S[.CURRENT = (pcallcontext_callee[.TARGET = '
            'SCOPED_TARGET porigin_requested porigin_method porigin_requested '
            '(n_receiver) poperand_selector])])',
        ],
    },
    'first-literal-called': {
        'source': ('<?php class A {public static function f(){echo static::class;}} '
                   'class B extends A {} $c=A::f(...); $c();'),
        'stage': ('S.RESULT = KNOWN (POBJECT n) '
                  '-- if S.OBJECTS[n] = METHODCLOSURE porigin_method porigin_site porigin_requested '
                  '-- if $closure_scope_at(S.CLOSURESCOPES, n) = (pclosurescope)'),
        'checks': [
            '$closure_scope_row_valid(S, pclosurescope)',
            '$class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)',
            '~$closure_scope_row_valid(S, pclosurescope[.CALLED = porigin_b])',
        ],
    },
    'first-private-origin': {
        'source': ('<?php class A {private function f(){echo "A";}} '
                   'class B extends A {public function f(){echo "B";}} '
                   '$c=(new B)->f(...); $c();'),
        'stage': ('S.RESULT = KNOWN (POBJECT n) '
                  '-- if S.OBJECTS[n] = METHODCLOSURE porigin_method porigin_site porigin_requested '
                  '-- if $closure_scope_at(S.CLOSURESCOPES, n) = (pclosurescope)'),
        'checks': [
            '$closure_scope_row_valid(S, pclosurescope)',
            '$class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)',
            '$class_at(S.CLASSES, porigin_a) = (pclassdesc_a)',
            '$method_named(pclassdesc_a.METHODS, $ptascii("f")) = (pmethoddesc_a)',
            '~$closure_scope_row_valid(S[.OBJECTS = $object_set(S.OBJECTS, n, '
            'METHODCLOSURE pmethoddesc_a.FUNCTION.ORIGIN porigin_site porigin_requested)], '
            'pclosurescope[.LEXICAL = pmethoddesc_a.OWNER])',
        ],
    },
    'first-convert-name': {
        'source': ('<?php class A {public static function f(){echo "F";} '
                   'public static function g(){echo "G";}} $c=A::f(...); $c();'),
        'stage': ('S.TODO = (METHOD_CONVERT (SCOPED_TARGET porigin_requested porigin_method '
                  'porigin_called n_receiver? poperand_selector) porigin_site z) :: ptask_tail*'),
        'checks': [
            '$call_task_valid(S, METHOD_CONVERT (SCOPED_TARGET porigin_requested '
            'porigin_method porigin_called n_receiver? poperand_selector) porigin_site z)',
            '$class_at(S.CLASSES, porigin_requested) = (pclassdesc_a)',
            '$method_named(pclassdesc_a.METHODS, $ptascii("g")) = (pmethoddesc_g)',
            '~$call_task_valid(S, METHOD_CONVERT (SCOPED_TARGET porigin_requested '
            'pmethoddesc_g.FUNCTION.ORIGIN porigin_called n_receiver? poperand_selector) '
            'porigin_site z)',
        ],
    },
    'first-object-selector-live': {
        'source': ('<?php class A {public static function f(){echo "F";}} '
                   '$c=(new A)::f(...); $c();'),
        'stage': ('S.TODO = (METHOD_CONVERT (SCOPED_TARGET porigin_requested porigin_method '
                  'porigin_called n_receiver? (KNOWN (POBJECT n_selector))) porigin_site z) :: ptask_tail*'),
        'checks': [
            '$call_task_valid(S, METHOD_CONVERT (SCOPED_TARGET porigin_requested '
            'porigin_method porigin_called n_receiver? (KNOWN (POBJECT n_selector))) porigin_site z)',
            'HOBJECT n_selector <- $tasks_nodes(S.TODO)',
        ],
    },
    'first-object-selector-released': {
        'source': ('<?php class A {public static function f(){echo "F";}} '
                   '$c=(new A)::f(...); $c();'),
        'stage': ('S.RESULT = KNOWN (POBJECT n_closure) '
                  '-- if S.OBJECTS[n_closure] = METHODCLOSURE porigin_method porigin_site porigin_requested '
                  '-- if $closure_scope_at(S.CLOSURESCOPES, n_closure) = (pclosurescope)'),
        'checks': [
            '$closure_scope_row_valid(S, pclosurescope)',
            'pclosurescope.RECEIVER = eps',
            '$node_children(S, HOBJECT n_closure) = eps',
        ],
    },
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    output = Path(tempfile.mkdtemp(prefix='static-method-protocol-', dir=ROOT / '.tools'))
    inputs = [*MODULES, ROOT / 'spec/semantics/modules.json', ROOT / 'spec/php.watsup',
              ROOT / 'spec/schema.json', ROOT / 'frontend/worker.php', ROOT / 'frontend/encoding.php',
              ROOT / 'frontend/FileLexer.php', ROOT / '_build/default/adapter/main.exe',
              ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
              ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so', Path(__file__)]
    before = {str(path.relative_to(ROOT)): digest(path) for path in inputs}
    records = []
    selected = set(sys.argv[1:])
    for name, case in CASES.items():
        if selected and name not in selected:
            continue
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
        checks = case['checks']
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
            + ''.join('  -- if ' + clause + '\n' for clause in checks))
        result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                 *map(str, MODULES), str(fixture)], capture_output=True,
                                text=True, timeout=300)
        (directory / 'stdout').write_text(result.stdout)
        (directory / 'stderr').write_text(result.stderr)
        passed = result.returncode == 0 and result.stdout == 'true\n' and not result.stderr
        records.append({'id': name, 'source_sha256': digest(source),
                        'assertions': len(checks) + 3, 'pass': passed,
                        'known_limit': case.get('known_limit')})
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
