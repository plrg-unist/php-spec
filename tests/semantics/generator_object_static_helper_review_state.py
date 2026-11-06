#!/usr/bin/env python3
"""Check receiver-free object-static helpers and real selector retirement."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from exception_handler_review import recorded
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).with_name('generator_object_static_helper_review_cases.json')
EXPECTED = {
    'i137-object-static-fiber-normal': 'fbe7aaa515128f614621abd8cc607c195ac86d2d43f4218fd30c8746da57d9fd',
    'i137-object-static-source-failure': '88d37c29936ac60e4bf1b7aedefe29127be56e0c135d8c092c5b45477dc51a88',
}
PREFIX = r'''
dec $test_i137_bound(pstate, preqbytes, preqbytes) : bool
def $test_i137_bound(S, preqbytes_function, preqbytes_variable) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $lookup(S.ENV, preqbytes_variable) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (POBJECT n)
  -- if $function_at(S.FUNCTIONS, pcallcontext.FUNCTION) = (pfunction)
  -- if pfunction.NAME = preqbytes_function
def $test_i137_bound(S, preqbytes_function, preqbytes_variable) = false -- otherwise
dec $test_i137_front(pstate, nat) : bool
def $test_i137_front(S, 0) = $test_i137_bound(S, $ptascii("argA137N"), $ptascii("selector137N"))
def $test_i137_front(S, 1) = $test_i137_bound(S, $ptascii("argB137N"), $ptascii("selector137N"))
def $test_i137_front(S, 2) = true
  -- if S.ACTIVEFIBER = eps /\ S.CURRENT = eps /\ S.FRAMES = eps
  -- if $lookup(S.ENV, $ptascii("fiber137N")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (POBJECT n)
  -- if S.OBJECTS[n] = FIBER pfiber
  -- if pfiber.STATUS = FIBER_SUSPENDED
  -- if pfiber.VM =/= eps
def $test_i137_front(S, 3) = $test_i137_bound(S, $ptascii("beforeArg137E"), $ptascii("before137E"))
def $test_i137_front(S, 4) = $test_i137_bound(S, $ptascii("bodyArg137E"), $ptascii("inside137E"))
def $test_i137_front(S, 5) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = $ptascii("STATIC|")
def $test_i137_front(S, n_stage) = false -- otherwise
dec $test_i137_seek(pstate, nat, nat) : pstate
def $test_i137_seek(S, n_stage, 0) = S
def $test_i137_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_i137_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $test_i137_seek(S, n_stage, n) = $test_i137_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_i137_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
'''


def lines(text):
    return [x.strip() for x in text.splitlines() if x.strip()]


def reach(state, start, stage, limit=1400):
    return [state + '_found = $test_i137_seek(' + start + ', ' + str(stage) + ', ' + str(limit) + ')',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_i137_front(' + state + ', ' + str(stage) + ')']


def public(state):
    return ['H_' + state + ' = $heap_graph(' + state + ')',
        '$call_descriptors_valid(' + state + ')', '$heap_valid(H_' + state + ')']


def budget(state):
    return [state + '_pause = $drive(' + state + ', 0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        *public(state + '_pause'), state + '_one = $drive(' + state + ', 1)',
        state + '_one.COMPLETION = BUDGET',
        '$drive(' + state + '_pause[.COMPLETION = NORMAL], 1) = ' + state + '_one',
        *public(state + '_one')]


def selector(state, variable, object_name, class_origin):
    return [f'$lookup({state}.ENV, $ptascii("{variable}")) = (n_{object_name}_cv)',
        f'{state}.STORE[n_{object_name}_cv] = DEFINED (POBJECT n_{object_name})',
        f'$object_class_origin({state}, n_{object_name}) = ({class_origin})',
        f'H_{state} = $heap_graph({state})',
        f'$heap_owners(H_{state}, HOBJECT n_{object_name}) = 1']


def static_context(state, context, called, owner, method):
    tag = context.removeprefix('pcallcontext_')
    return [f'{context}.TARGET = STATIC_METHOD_TARGET {called} {context}.FUNCTION',
        f'{context}.RECEIVER = eps /\\ {context}.INSTANCE = eps',
        f'$call_context_roots(({context})) = eps',
        f'$target_nodes({context}.TARGET) = eps',
        f'$generator_helper_context({state}, {context})',
        f'$generator_helper_method_source({state}, {context}) = (pmethoddesc_{tag})',
        f'pmethoddesc_{tag}.STATIC',
        f'pmethoddesc_{tag}.NAME = $ptascii("{method}")',
        f'$class_named({state}.CLASSNAMES, $ptlc($ptascii("{owner}"))) = (pmethoddesc_{tag}.OWNER)']


def normal_checks():
    values = reach('S_arg_a', 'S_initial', 0) + selector('S_arg_a', 'selector137N', 'selector_a', 'porigin_a')
    values += reach('S_arg_b', 'S_arg_a', 1, 700) + selector('S_arg_b', 'selector137N', 'selector_b', 'porigin_b')
    values += reach('S_park', 'S_arg_b', 2, 350) + lines(r'''
$lookup(S_park.ENV, $ptascii("fiber137N")) = (n_fiber_cv)
S_park.STORE[n_fiber_cv] = DEFINED (POBJECT n_fiber)
S_park.OBJECTS[n_fiber] = FIBER pfiber
pfiber.STATUS = FIBER_SUSPENDED
pfiber.VM = (pfibervm)
pfibervm.CURRENT = (pcallcontext_pause)
pfibervm.FRAMES = pframe_body :: pframe_resume :: pframe_callback :: pframe_cursor :: pframe_tail*
pframe_resume.CONTEXT = (pcallcontext_advance)
pframe_resume.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_resume*
pframe_cursor.TODO = (CONFIG_ITERATOR pconfigiterator text_stage) :: ptask_cursor*
pconfigiterator.CALL.OWNER = (n_target)
pconfigiterator.OBJECT = n_input
pgeneratorop.OBJECT = n_target
pgeneratorop.NAME = "next"
S_restored = $fiber_vm_restore(S_park, pfibervm)[.COMPLETION = NORMAL]
S_restored.ACTIVEFIBER = eps
''')
    values += static_context('S_restored', 'pcallcontext_pause', 'porigin_b', 'Base137N', 'pause')
    values += static_context('S_restored', 'pcallcontext_advance', 'porigin_a', 'Base137N', 'advance')
    values += lines(r'''
~$generator_helper_context(S_restored, pcallcontext_pause[.RECEIVER = (n_target)])
~$generator_helper_context(S_restored, pcallcontext_pause[.INSTANCE = (n_target)])
~$generator_helper_context(S_restored, pcallcontext_pause[.CALLSITE = eps])
$generator_saved_ids(pfibervm.FRAMES) = [n_target]
$fiber_generator_body_id(S_restored) = (n_target)
$generator_source_reentry_view(S_restored) = eps
$generator_iterator_reentry_view(S_restored) = ((S_view, pframe_callback, pframe_cursor, pframe_tail*))
S_restored.OBJECTS[n_target] = GENERATOR pgenerator
S_view = $generator_set(S_restored, n_target, pgenerator[.PHASE = GENERATOR_PAUSED])
$heap_graph(S_view) = $heap_graph(S_restored)
$heap_count(HOBJECT n_selector_a, $fiber_vm_nodes(pfibervm)) = 0
$heap_count(HOBJECT n_selector_b, $fiber_vm_nodes(pfibervm)) = 0
$heap_count(HOBJECT n_target, $fiber_vm_nodes(pfibervm)) = 2
$heap_count(HOBJECT n_input, $fiber_vm_nodes(pfibervm)) = 1
H_park = $heap_graph(S_park)
$heap_owners(H_park, HOBJECT n_selector_a) = 0
$heap_owners(H_park, HOBJECT n_selector_b) = 0
~((HOBJECT n_selector_a) <- S_park.ALLOCATIONS)
~((HOBJECT n_selector_b) <- S_park.ALLOCATIONS)
$heap_owners(H_park, HOBJECT n_target) = 2
$heap_owners(H_park, HOBJECT n_input) = 1
$generator_saved_fiber_ids(S_park) = [n_target]
$fiber_vm_valid(S_park, pfibervm, (n_fiber), eps)
''')
    return values + budget('S_park')


def failure_checks():
    values = reach('S_before', 'S_initial', 3) + selector('S_before', 'before137E', 'before', 'porigin_before')
    values += reach('S_inside', 'S_before', 4, 600) + selector('S_inside', 'inside137E', 'inside', 'porigin_inside')
    values += reach('S_static', 'S_inside', 5, 250) + lines(r'''
S_static.CURRENT = (pcallcontext_fail)
S_static.FRAMES = pframe_body :: pframe_target :: pframe_source_body :: pframe_source :: pframe_tail*
pframe_target.CONTEXT = (pcallcontext_advance)
pframe_target.TODO = (GENERATOR_RESUME pgeneratorop_target) :: ptask_target*
pframe_source.TODO = (GENERATOR_RESUME pgeneratorop_source) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_outer*
pconfiggenerator.CALL.OWNER = (n_target)
pconfiggenerator.OBJECT = n_source
pconfiggenerator.CALL.SENT = [NAMED_SENT (KNOWN (PINT 13))]
pconfiggenerator.ITEMS = [ENTRY pkey (DIRECT (PINT 11))]
pgeneratorop_target.OBJECT = n_target
pgeneratorop_target.NAME = "send"
pgeneratorop_target.ARGUMENTS = [PINT 17]
pgeneratorop_source.OBJECT = n_source
pgeneratorop_source.STARTPACK /\ pgeneratorop_source.BORROWED
n_target =/= n_source
S_static.OBJECTS[n_target] = GENERATOR pgenerator_target
S_static.OBJECTS[n_source] = GENERATOR pgenerator_source
pgenerator_target.PHASE = GENERATOR_RUNNING
pgenerator_source.PHASE = GENERATOR_RUNNING
''')
    values += static_context('S_static', 'pcallcontext_fail', 'porigin_inside', 'BodyBase137E', 'fail')
    values += static_context('S_static', 'pcallcontext_advance', 'porigin_before', 'BeforeBase137E', 'advance')
    values += lines(r'''
~$generator_helper_context(S_static, pcallcontext_fail[.RECEIVER = (n_target)])
$generator_saved_ids(S_static.FRAMES) = [n_target, n_source]
$fiber_generator_body_id(S_static) = eps
$generator_iterator_reentry_view(S_static) = eps
$generator_source_reentry_view(S_static) = ((S_view, pframe_source_body, pframe_source, pframe_tail*))
S_view = $generator_set(S_static, n_target, pgenerator_target[.PHASE = GENERATOR_PAUSED])
$heap_graph(S_view) = $heap_graph(S_static)
$generator_resume_pairs(S_static, S_static.CURRENT, S_static.FRAMES)
H_static = $heap_graph(S_static)
$heap_owners(H_static, HOBJECT n_before) = 0
$heap_owners(H_static, HOBJECT n_inside) = 0
~((HOBJECT n_before) <- S_static.ALLOCATIONS)
~((HOBJECT n_inside) <- S_static.ALLOCATIONS)
$heap_owners(H_static, HOBJECT n_target) = 2
$heap_owners(H_static, HOBJECT n_source) = 2
$task_nodes(GENERATOR_RESUME pgeneratorop_source) = eps
''')
    return values + budget('S_static')


def checks(name, program, path):
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    values = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'i137-object-static-fiber-normal':
        return values + normal_checks()
    assert name == 'i137-object-static-source-failure'
    return values + failure_checks()


def run(out=None, process_seconds=600):
    catalog = {x['id']: x for x in json.loads(CATALOG.read_bytes())}
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='generator-object-static-helper-state-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    modules = [ROOT / x for x in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    environment = dict(os.environ, LC_ALL='C', TZ='UTC')
    environment.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    records = []
    for name, digest in EXPECTED.items():
        row = catalog[name]
        assert row['source_sha256'] == digest == hashlib.sha256(row['source'].encode()).hexdigest()
        directory = out / name; directory.mkdir()
        source = directory / 'source.php'; source.write_text(row['source'])
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
        finally:
            frontend.close()
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        try:
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok']
        finally:
            adapter.close()
        conditions = checks(name, checked['fixture'], source)
        fixture = directory / 'test.watsup'
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- ' + (x if x.startswith('PhpStep:') else 'if ' + x) + '\n' for x in conditions))
        (directory / 'assertions.json').write_text(json.dumps(conditions, indent=2) + '\n')
        process = recorded([ROOT / 'tests/semantics/_build/default/numeric_runner.exe', '--sl', *modules, fixture], directory, 'model', environment, process_seconds)
        passed = process['exit'] == 0 and not process['timeout'] and (directory / 'model.stdout').read_bytes() == b'true\n' and (directory / 'model.stderr').read_bytes() == b''
        records.append({'id': name, 'source_sha256': digest, 'assertions': len(conditions), 'process': process, 'passed': passed})
        print(name, len(conditions), 'PASS' if passed else 'FAIL', flush=True)
        if not passed:
            break
    report = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'selection': list(EXPECTED), 'records': records, 'passed': len(records) == len(EXPECTED) and all(x['passed'] for x in records)}
    (out / 'raw-report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    raise SystemExit(0 if run() else 1)
