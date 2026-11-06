#!/usr/bin/env python3
"""Check source-bound method helpers, real VM roots and dual reentry."""
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
CATALOG = Path(__file__).with_name('generator_method_helper_reentry_review_cases.json')
EXPECTED = {
    'i136-iterator-method-fiber-normal': '1086ea93956565257dad2502546650abafdbe1671aa670566abac5dc9dfc30fc',
    'i136-source-method-helper-failure': 'd9dada9755ae7e59bbdaa3941b41e4d4248bb2d2f262029b3937bd01ac17cee3',
}
PREFIX = r'''
dec $test_i136_echo(pstate, preqbytes) : bool
def $test_i136_echo(S, preqbytes) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = preqbytes
def $test_i136_echo(S, preqbytes) = false -- otherwise
dec $test_i136_front(pstate, nat) : bool
def $test_i136_front(S, 1) = $test_i136_echo(S, $ptascii("PARK|"))
def $test_i136_front(S, 3) = $test_i136_echo(S, $ptascii("STATIC|"))
def $test_i136_front(S, n_stage) = false -- otherwise
dec $test_i136_seek(pstate, nat, nat) : pstate
def $test_i136_seek(S, n_stage, 0) = S
def $test_i136_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_i136_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $test_i136_seek(S, n_stage, n) = $test_i136_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_i136_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
'''


def lines(text):
    return [x.strip() for x in text.splitlines() if x.strip()]


def reach(state, start, stage, limit=1400):
    return [state + '_found = $test_i136_seek(' + start + ', ' + str(stage) + ', ' + str(limit) + ')',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_i136_front(' + state + ', ' + str(stage) + ')']


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


def normal_checks():
    values = reach('S_park', 'S_initial', 1, 1700) + lines(r'''
S_park.ACTIVEFIBER = eps
S_park.CURRENT = eps
S_park.FRAMES = eps
$lookup(S_park.ENV, $ptascii("fiber")) = (n_fiber_cv)
S_park.STORE[n_fiber_cv] = DEFINED (POBJECT n_fiber)
S_park.OBJECTS[n_fiber] = FIBER pfiber
pfiber.STATUS = FIBER_SUSPENDED
pfiber.VM = (pfibervm)
pfibervm.CURRENT = (pcallcontext_helper)
pfibervm.FRAMES = pframe_body :: pframe_resume :: pframe_callback :: pframe_cursor :: pframe_tail*
pframe_resume.CONTEXT = (pcallcontext_bridge)
pframe_resume.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_resume*
pframe_callback.CONTEXT = (pcallcontext_callback)
pframe_cursor.TODO = (CONFIG_ITERATOR pconfigiterator text_stage) :: ptask_cursor*
pconfigiterator.CALL = pconfigcall
pconfigiterator.PRODUCER = eps
pconfigiterator.OBJECT = n_input
pconfigcall.OWNER = (n_target)
pconfigcall.INDEX = 1
pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_prefix))]
pgeneratorop.OBJECT = n_target
pgeneratorop.NAME = "next"
~pgeneratorop.ADVANCE /\ ~pgeneratorop.STARTPACK /\ ~pgeneratorop.BORROWED
S_park.OBJECTS[n_target] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
pcallcontext_helper.TARGET = METHOD_TARGET n_helper pcallcontext_helper.FUNCTION
pcallcontext_helper.RECEIVER = (n_helper)
$call_context_roots((pcallcontext_helper)) = [HOBJECT n_helper]
$call_context_roots((pcallcontext_bridge)) = eps
$call_context_roots((pcallcontext_callback)) = eps
$heap_count(HOBJECT n_helper, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_target, $fiber_vm_nodes(pfibervm)) = 2
$heap_count(HOBJECT n_prefix, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_input, $fiber_vm_nodes(pfibervm)) = 1
H_park = $heap_graph(S_park)
$heap_owners(H_park, HOBJECT n_helper) = 1
$heap_owners(H_park, HOBJECT n_target) = 2
$heap_owners(H_park, HOBJECT n_prefix) = 1
$heap_owners(H_park, HOBJECT n_input) = 1
S_restored = $fiber_vm_restore(S_park, pfibervm)[.COMPLETION = NORMAL]
S_restored.ACTIVEFIBER = eps
$lookup(S_restored.ENV, $ptascii("helper")) = (n_helper_cv)
S_restored.STORE[n_helper_cv] = DEFINED PNULL
$generator_helper_context(S_restored, pcallcontext_helper)
$generator_helper_context(S_restored, pcallcontext_bridge)
$generator_helper_method_source(S_restored, pcallcontext_helper) = (pmethoddesc_helper)
$generator_helper_method_source(S_restored, pcallcontext_bridge) = (pmethoddesc_bridge)
~pmethoddesc_helper.STATIC /\ pmethoddesc_bridge.STATIC
pcallcontext_helper.CALLSITE = (porigin_helper)
$origin_node(S_restored.SOURCES, porigin_helper) = (NExprMethodCall (NExprVariable (BYTES text_receiver) metadata_receiver) phpType20 phpType6 metadata_call)
~$generator_helper_instance_source((NExprMethodCall (NExprVariable (BYTES "dGhpcw==") metadata_receiver) phpType20 phpType6 metadata_call))
~$generator_helper_context(S_restored, pcallcontext_helper[.CALLSITE = eps])
~$generator_helper_context(S_restored, pcallcontext_helper[.TARGET = AGGREGATE_METHOD_TARGET n_helper pcallcontext_helper.FUNCTION])
~$generator_helper_context(S_restored, pcallcontext_bridge[.TARGET = METHOD_TARGET n_helper pcallcontext_bridge.FUNCTION])
pcallcontext_bridge.TARGET = SCOPED_TARGET porigin_requested pcallcontext_bridge.FUNCTION porigin_called eps poperand_selector
~$generator_helper_context(S_restored, pcallcontext_bridge[.TARGET = SCOPED_TARGET porigin_requested pcallcontext_bridge.FUNCTION porigin_called (n_helper) poperand_selector])
~$generator_helper_context(S_restored, pcallcontext_bridge[.TARGET = SCOPED_TARGET porigin_requested pcallcontext_bridge.FUNCTION porigin_called eps (KNOWN (POBJECT n_helper))])
$generator_saved_ids(pfibervm.FRAMES) = [n_target]
$fiber_generator_body_id(S_restored) = (n_target)
$generator_source_reentry_view(S_restored) = eps
~$useriter_frame(S_restored, pcallcontext_helper, pframe_body)
$generator_iterator_reentry_view(S_restored) = ((S_view, pframe_callback, pframe_cursor, pframe_tail*))
S_view = $generator_set(S_restored, n_target, pgenerator[.PHASE = GENERATOR_PAUSED])
$heap_graph(S_view) = $heap_graph(S_restored)
S_bad_receiver = S_restored[.CURRENT = (pcallcontext_helper[.RECEIVER = eps])]
$fiber_generator_body_id(S_bad_receiver) = eps
$foreach_aggregate_close_vm_ids(S_park, pfibervm) = [n_target]
$generator_saved_fiber_ids(S_park) = [n_target]
$fiber_vm_valid(S_park, pfibervm, (n_fiber), eps)
''')
    values += budget('S_park')
    return values


def failure_checks():
    values = reach('S_static', 'S_initial', 3, 1700) + lines(r'''
S_static.CURRENT = (pcallcontext_static)
S_static.FRAMES = pframe_body :: pframe_target :: pframe_source_body :: pframe_source :: pframe_tail*
pframe_body.CONTEXT = (pcallcontext_target)
pframe_target.CONTEXT = (pcallcontext_before)
pframe_target.TODO = (GENERATOR_RESUME pgeneratorop_target) :: ptask_target*
pframe_source_body.CONTEXT = (pcallcontext_source)
pframe_source.TODO = (GENERATOR_RESUME pgeneratorop_source) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_outer*
pconfiggenerator.CALL = pconfigcall
pconfiggenerator.OBJECT = n_source
pconfiggenerator.ITEMS = [ENTRY pkey (DIRECT (PINT 11))]
pconfigcall.OWNER = (n_target)
pconfigcall.INDEX = 1
pconfigcall.SENT = [NAMED_SENT (KNOWN (PINT 13))]
pgeneratorop_target.OBJECT = n_target
pgeneratorop_target.NAME = "send"
pgeneratorop_target.ARGUMENTS = [PINT 17]
~pgeneratorop_target.STARTPACK /\ ~pgeneratorop_target.BORROWED
pgeneratorop_source.OBJECT = n_source
pgeneratorop_source.NAME = "next"
pgeneratorop_source.STARTPACK /\ pgeneratorop_source.BORROWED
S_static.OBJECTS[n_target] = GENERATOR pgenerator_target
S_static.OBJECTS[n_source] = GENERATOR pgenerator_source
pgenerator_target.PHASE = GENERATOR_RUNNING
pgenerator_source.PHASE = GENERATOR_RUNNING
n_target =/= n_source
pgenerator_source.VALUE = (PINT 11)
pcallcontext_before.TARGET = METHOD_TARGET n_before pcallcontext_before.FUNCTION
pcallcontext_before.RECEIVER = (n_before)
$call_context_roots((pcallcontext_before)) = [HOBJECT n_before]
$call_context_roots((pcallcontext_static)) = eps
$generator_helper_context(S_static, pcallcontext_before)
$generator_helper_context(S_static, pcallcontext_static)
$generator_helper_method_source(S_static, pcallcontext_before) = (pmethoddesc_before)
$generator_helper_method_source(S_static, pcallcontext_static) = (pmethoddesc_static)
~pmethoddesc_before.STATIC /\ pmethoddesc_static.STATIC
$generator_saved_ids(S_static.FRAMES) = [n_target, n_source]
$fiber_generator_body_id(S_static) = eps
$generator_iterator_reentry_view(S_static) = eps
$generator_source_reentry_view(S_static) = ((S_view, pframe_source_body, pframe_source, pframe_tail*))
S_view = $generator_set(S_static, n_target, pgenerator_target[.PHASE = GENERATOR_PAUSED])
H_static = $heap_graph(S_static)
$heap_graph(S_view) = H_static
$heap_owners(H_static, HOBJECT n_before) = 1
$heap_owners(H_static, HOBJECT n_target) = 2
$heap_owners(H_static, HOBJECT n_source) = 2
$generator_values_nodes(pgenerator_source.VALUE) = eps
$task_nodes(GENERATOR_RESUME pgeneratorop_source) = eps
$heap_count(HOBJECT n_source, $task_nodes(CONFIG_GENERATOR pconfiggenerator "next")) = 1
$heap_count(HOBJECT n_target, $task_nodes(CONFIG_GENERATOR pconfiggenerator "next")) = 1
S_source_scope = $config_generator_operation_frame_scope(S_static, pframe_source, pframe_tail*)
S_source_scope = $constant_frame_scope(S_view, pframe_source, pframe_tail*)
$generator_source_consumer(S_source_scope, pconfiggenerator)
$config_generator_operation_tasks(S_source_scope, pgeneratorop_source, pframe_source.TODO)
$generator_resume_pairs(S_static, S_static.CURRENT, S_static.FRAMES)
pframe_bad_before = pframe_target[.CONTEXT = (pcallcontext_before[.RECEIVER = eps])]
S_bad_before = S_static[.FRAMES = pframe_body :: pframe_bad_before :: pframe_source_body :: pframe_source :: pframe_tail*]
$generator_saved_ids(S_bad_before.FRAMES) = [n_target, n_source]
$generator_source_reentry_view(S_bad_before) = eps
''')
    values += budget('S_static')

    return values


def checks(name, program, path):
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    values = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'i136-iterator-method-fiber-normal':
        return values + normal_checks()
    assert name == 'i136-source-method-helper-failure'
    return values + failure_checks()


def run(out=None, process_seconds=600):
    catalog = {x['id']: x for x in json.loads(CATALOG.read_bytes())}
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='generator-method-helper-reentry-state-', dir=ROOT / '.tools'))
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
