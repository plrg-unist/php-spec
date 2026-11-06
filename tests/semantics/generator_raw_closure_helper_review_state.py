#!/usr/bin/env python3
"""Check raw Closure helper INSTANCE ownership and VM movement."""
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
CATALOG = Path(__file__).with_name('generator_raw_closure_helper_review_cases.json')
EXPECTED = {
    'i138-raw-closure-fiber-normal': '0d3d99259a591948a3e0b4c217564a7ff06df5fd85a036192cc6dc569b1393a1',
    'i138-raw-closure-source-failure': '74dd8bc5fe307c3cfe8f36598e0f475632ddf254dfa3f8d8492a7515078fa05d',
}
PREFIX = r'''
dec $test_i138_front(pstate, nat) : bool
def $test_i138_front(S, 0) = true
  -- if S.ACTIVEFIBER = eps /\ S.CURRENT = eps /\ S.FRAMES = eps
  -- if $lookup(S.ENV, $ptascii("fiber138N")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (POBJECT n)
  -- if S.OBJECTS[n] = FIBER pfiber
  -- if pfiber.STATUS = FIBER_SUSPENDED
  -- if pfiber.VM =/= eps
def $test_i138_front(S, 1) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = $ptascii("INNER|")
def $test_i138_front(S, n_stage) = false -- otherwise
dec $test_i138_seek(pstate, nat, nat) : pstate
def $test_i138_seek(S, n_stage, 0) = S
def $test_i138_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_i138_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $test_i138_seek(S, n_stage, n) = $test_i138_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_i138_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
'''


def lines(text):
    return [x.strip() for x in text.splitlines() if x.strip()]


def reach(state, start, stage, limit=1400):
    return [state + '_found = $test_i138_seek(' + start + ', ' + str(stage) + ', ' + str(limit) + ')',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_i138_front(' + state + ', ' + str(stage) + ')']


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


def closure_context(state, context, object_name):
    tag = context.removeprefix('pcallcontext_')
    return [f'{context}.TARGET = CLOSURE_TARGET n_{object_name}',
        f'{context}.INSTANCE = (n_{object_name})',
        f'{context}.RECEIVER = eps /\\ {context}.LEXICAL_CLASS = eps /\\ {context}.CALLED_CLASS = eps',
        f'$call_context_roots(({context})) = [HOBJECT n_{object_name}]',
        f'{state}.OBJECTS[n_{object_name}] = REALCLOSURE {context}.FUNCTION eps eps',
        f'$node_children({state}, HOBJECT n_{object_name}) = eps',
        f'$closure_scope_at({state}.CLOSURESCOPES, n_{object_name}) = eps',
        f'$closure_binding_at({state}.CLOSUREBINDINGS, n_{object_name}) = eps',
        f'$function_at({state}.CLOSURETEMPLATES, {context}.FUNCTION) = (pfunction_{tag})',
        f'$closure_static({state}, pfunction_{tag})',
        f'$closure_lexicals(pfunction_{tag}.CODE.EXPRESSIONS) = eps /\\ $static_code_entries(pfunction_{tag}.CODE.EXPRESSIONS) = eps',
        f'$generator_helper_context({state}, {context})']


def cleared(state, table, variable, tag):
    return [f'$lookup({table}, $ptascii("{variable}")) = (n_{tag}_cv)',
        f'{state}.STORE[n_{tag}_cv] = DEFINED PNULL']


def normal_checks():
    values = reach('S_park', 'S_initial', 0) + lines(r'''
$lookup(S_park.ENV, $ptascii("fiber138N")) = (n_fiber_cv)
S_park.STORE[n_fiber_cv] = DEFINED (POBJECT n_fiber)
S_park.OBJECTS[n_fiber] = FIBER pfiber
pfiber.STATUS = FIBER_SUSPENDED
pfiber.VM = (pfibervm)
pfibervm.CURRENT = (pcallcontext_inside)
pfibervm.FRAMES = pframe_body :: pframe_resume :: pframe_callback :: pframe_cursor :: pframe_tail*
pframe_resume.CONTEXT = (pcallcontext_before)
pframe_resume.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_resume*
pframe_cursor.TODO = (CONFIG_ITERATOR pconfigiterator text_stage) :: ptask_cursor*
pconfigiterator.CALL.OWNER = (n_target)
pconfigiterator.CALL.SENT = [NAMED_SENT (KNOWN (PINT 13))]
pconfigiterator.OBJECT = n_input
pgeneratorop.OBJECT = n_target
pgeneratorop.NAME = "next"
S_restored = $fiber_vm_restore(S_park, pfibervm)[.COMPLETION = NORMAL]
S_restored.ACTIVEFIBER = eps
''')
    values += closure_context('S_restored', 'pcallcontext_inside', 'inside')
    values += closure_context('S_restored', 'pcallcontext_before', 'before')
    values += cleared('S_park', 'S_park.ENV', 'inside138N', 'inside')
    values += cleared('S_park', 'S_park.ENV', 'before138N', 'before')
    values += lines(r'''
n_inside =/= n_before
~$generator_helper_context(S_restored, pcallcontext_inside[.INSTANCE = eps])
~$generator_helper_context(S_restored, pcallcontext_inside[.INSTANCE = (n_before)])
~$generator_helper_context(S_restored, pcallcontext_inside[.RECEIVER = (n_target)])
$generator_saved_ids(pfibervm.FRAMES) = [n_target]
$fiber_generator_body_id(S_restored) = (n_target)
$generator_source_reentry_view(S_restored) = eps
$generator_iterator_reentry_view(S_restored) = ((S_view, pframe_callback, pframe_cursor, pframe_tail*))
S_restored.OBJECTS[n_target] = GENERATOR pgenerator
S_view = $generator_set(S_restored, n_target, pgenerator[.PHASE = GENERATOR_PAUSED])
$heap_graph(S_view) = $heap_graph(S_restored)
$heap_count(HOBJECT n_inside, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_before, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_target, $fiber_vm_nodes(pfibervm)) = 2
$heap_count(HOBJECT n_input, $fiber_vm_nodes(pfibervm)) = 1
H_park = $heap_graph(S_park)
$heap_owners(H_park, HOBJECT n_inside) = 1
$heap_owners(H_park, HOBJECT n_before) = 1
$heap_owners(H_park, HOBJECT n_target) = 2
$heap_owners(H_park, HOBJECT n_input) = 1
$generator_saved_fiber_ids(S_park) = [n_target]
$fiber_vm_valid(S_park, pfibervm, (n_fiber), eps)
''')
    return values + budget('S_park')


def failure_checks():
    values = reach('S_inner', 'S_initial', 1) + lines(r'''
S_inner.CURRENT = (pcallcontext_inside)
S_inner.FRAMES = pframe_body :: pframe_target :: pframe_source_body :: pframe_source :: pframe_tail*
pframe_target.CONTEXT = (pcallcontext_before)
pframe_target.TODO = (GENERATOR_RESUME pgeneratorop_target) :: ptask_target*
pframe_source.TODO = (GENERATOR_RESUME pgeneratorop_source) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_outer*
pconfiggenerator.CALL.OWNER = (n_target)
pconfiggenerator.CALL.SENT = [NAMED_SENT (KNOWN (PINT 13))]
pconfiggenerator.OBJECT = n_source
pconfiggenerator.ITEMS = [ENTRY pkey (DIRECT (PINT 11))]
pgeneratorop_target.OBJECT = n_target
pgeneratorop_target.NAME = "send"
pgeneratorop_target.ARGUMENTS = [PINT 17]
pgeneratorop_source.OBJECT = n_source
pgeneratorop_source.STARTPACK /\ pgeneratorop_source.BORROWED
n_target =/= n_source
S_inner.OBJECTS[n_target] = GENERATOR pgenerator_target
S_inner.OBJECTS[n_source] = GENERATOR pgenerator_source
pgenerator_target.PHASE = GENERATOR_RUNNING
pgenerator_source.PHASE = GENERATOR_RUNNING
S_inner.GLOBALTABLE = (psymboltable_global)
''')
    values += closure_context('S_inner', 'pcallcontext_inside', 'inside')
    values += closure_context('S_inner', 'pcallcontext_before', 'before')
    values += cleared('S_inner', 'psymboltable_global.ENV', 'inside138E', 'inside')
    values += cleared('S_inner', 'psymboltable_global.ENV', 'before138E', 'before')
    values += lines(r'''
n_inside =/= n_before
~$generator_helper_context(S_inner, pcallcontext_inside[.INSTANCE = (n_before)])
$generator_saved_ids(S_inner.FRAMES) = [n_target, n_source]
$fiber_generator_body_id(S_inner) = eps
$generator_iterator_reentry_view(S_inner) = eps
$generator_source_reentry_view(S_inner) = ((S_view, pframe_source_body, pframe_source, pframe_tail*))
S_view = $generator_set(S_inner, n_target, pgenerator_target[.PHASE = GENERATOR_PAUSED])
$heap_graph(S_view) = $heap_graph(S_inner)
$generator_resume_pairs(S_inner, S_inner.CURRENT, S_inner.FRAMES)
H_inner = $heap_graph(S_inner)
$heap_owners(H_inner, HOBJECT n_inside) = 1
$heap_owners(H_inner, HOBJECT n_before) = 1
$heap_owners(H_inner, HOBJECT n_target) = 2
$heap_owners(H_inner, HOBJECT n_source) = 2
$task_nodes(GENERATOR_RESUME pgeneratorop_source) = eps
''')
    return values + budget('S_inner')


def checks(name, program, path):
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    values = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'i138-raw-closure-fiber-normal':
        return values + normal_checks()
    assert name == 'i138-raw-closure-source-failure'
    return values + failure_checks()


def run(out=None, process_seconds=600):
    catalog = {x['id']: x for x in json.loads(CATALOG.read_bytes())}
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='generator-raw-closure-helper-state-', dir=ROOT / '.tools'))
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
