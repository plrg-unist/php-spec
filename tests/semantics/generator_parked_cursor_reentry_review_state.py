#!/usr/bin/env python3
"""Check real external resumers against parked and reactivated Iterator cursors."""
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
CATALOG = Path(__file__).with_name('generator_parked_cursor_reentry_review_cases.json')
EXPECTED = {
    'i139-parked-cursor-external-next': '9860988b713643084a115375e284c501b091a99bed28bef07ac843ddf7af5b5c',
    'i139-reactivated-cursor-running-error': '396f4edaa9286426810b403d83765eb3d4f563bedc20b29b436adacbf0c14ba2',
}
PREFIX = r'''
dec $test_i139_front(pstate, nat) : bool
def $test_i139_front(S, n_stage) = true
  -- if n_stage <- [0, 1]
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if (n_stage = 0 /\ $base64(text) = $ptascii("EXTERNAL|")) \/ (n_stage = 1 /\ $base64(text) = $ptascii("ITER-BACK|"))
def $test_i139_front(S, 2) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD "send" pgeneratormethodselection?
def $test_i139_front(S, n_stage) = false -- otherwise
dec $test_i139_seek(pstate, nat, nat) : pstate
def $test_i139_seek(S, n_stage, 0) = S
def $test_i139_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_i139_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $test_i139_seek(S, n_stage, n) = $test_i139_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_i139_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
'''


def lines(text):
    return [x.strip() for x in text.splitlines() if x.strip()]


def reach(state, start, stage, limit=1400):
    return [state + '_found = $test_i139_seek(' + start + ', ' + str(stage) + ', ' + str(limit) + ')',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_i139_front(' + state + ', ' + str(stage) + ')']


def budget(state):
    return [state + '_pause = $drive(' + state + ', 0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        '$call_descriptors_valid(' + state + '_pause)',
        '$heap_valid($heap_graph(' + state + '_pause))',
        state + '_one = $drive(' + state + ', 1)',
        state + '_one.COMPLETION = BUDGET',
        '$drive(' + state + '_pause[.COMPLETION = NORMAL], 1) = ' + state + '_one',
        '$call_descriptors_valid(' + state + '_one)',
        '$heap_valid($heap_graph(' + state + '_one))']


def frozen_cursor(state, suffix):
    return lines(rf'''
psymboltable_global = $fiber_globals({state})
$lookup(psymboltable_global.ENV, $ptascii("target139{suffix}")) = (n_target_cv)
{state}.STORE[n_target_cv] = DEFINED PNULL
$lookup(psymboltable_global.ENV, $ptascii("input139{suffix}")) = (n_input_cv)
{state}.STORE[n_input_cv] = DEFINED PNULL
$lookup(psymboltable_global.ENV, $ptascii("outside139{suffix}")) = (n_outside_cv)
{state}.STORE[n_outside_cv] = DEFINED PNULL
$lookup(psymboltable_global.ENV, $ptascii("method139{suffix}")) = (n_method_cv)
{state}.STORE[n_method_cv] = DEFINED (PSTRING_CARRIER INTERNED_STRING $ptascii("current"))
pconfigiterator.CALL.KIND = INTRINSIC_GENERATOR_METHOD "send" pgeneratormethodselection?
pconfigiterator.CALL.OWNER = (n_target)
pconfigiterator.CALL.INDEX = 1
pconfigiterator.CALL.SENT = [NAMED_SENT (KNOWN (PINT 13))]
~pconfigiterator.CALL.NAMED /\ pconfigiterator.CALL.PACKS = eps
pconfigiterator.PRODUCER = eps
pconfigiterator.OBJECT = n_input
pconfigiterator.ITEMS = eps
text_stage = "rewind"
{state}.OBJECTS[n_target] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
H_real = $heap_graph({state})
$heap_owners(H_real, HOBJECT n_target) = 2
$heap_owners(H_real, HOBJECT n_input) = 1
''')


def normal_checks():
    return reach('S_external', 'S_initial', 0) + lines(r'''
S_external.ACTIVEFIBER = eps
S_external.CURRENT = (pcallcontext_actor)
S_external.FRAMES = pframe_actor :: pframe_actor_tail*
pframe_actor.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_actor*
$generator_saved_ids(S_external.FRAMES) = [pgeneratorop.OBJECT]
$lookup($fiber_globals(S_external).ENV, $ptascii("fiber139N")) = (n_fiber_cv)
S_external.STORE[n_fiber_cv] = DEFINED (POBJECT n_fiber)
S_external.OBJECTS[n_fiber] = FIBER pfiber
pfiber.STATUS = FIBER_SUSPENDED
pfiber.VM = (pfibervm)
pfibervm.CURRENT = (pcallcontext_callback)
pfibervm.FRAMES = pframe_cursor :: pframe_tail*
pframe_cursor.TODO = (CONFIG_ITERATOR pconfigiterator text_stage) :: ptask_cursor*
''') + frozen_cursor('S_external', 'N') + lines(r'''
pgeneratorop.OBJECT = n_target
pgeneratorop.NAME = "next"
~pgeneratorop.ADVANCE /\ ~pgeneratorop.STARTPACK /\ ~pgeneratorop.BORROWED
$generator_resume_pairs(S_external, S_external.CURRENT, S_external.FRAMES)
$generator_external_actor_scope(S_external, n_target)
$generator_saved_fiber_ids(S_external) = eps
S_consumer = $fiber_vm_restore(S_external, pfibervm)[.COMPLETION = NORMAL]
$generator_saved_ids(S_consumer.FRAMES) = eps
$generator_resume_ids(S_consumer.TODO) = eps
~$generator_external_actor_scope(S_consumer, n_target)
$heap_count(HOBJECT n_target, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_input, $fiber_vm_nodes(pfibervm)) = 1
$generator_external_scope_real(S_external, S_consumer)
$generator_external_phase_scope(S_external, S_external, pconfigiterator.CALL) = eps
$generator_external_cursor_view(S_external, S_consumer, pconfigiterator.CALL) = ((S_view, pconfigiterator, text_stage))
S_view = $generator_set(S_consumer, n_target, pgenerator[.PHASE = GENERATOR_PAUSED])
$heap_graph(S_view) = $heap_graph(S_consumer)
$call_descriptors_input_scope(S_external, S_consumer) = S_view
$generator_external_cursor(S_external, pconfigiterator.CALL) = ((S_view, pconfigiterator, text_stage))
$config_iterator_history(S_external, pconfigiterator)
$config_iterator_frame(S_view, pcallcontext_callback, pframe_cursor)
~$generator_iterator_entry_site(S_external, pconfigiterator.CALL)
pconfigiterator_fresh = pconfigiterator[.ITERATOR = S_external.NEXTITER]
~$config_iterator_history(S_external, pconfigiterator_fresh)
$generator_external_cursor_view(S_external, S_consumer[.FRAMES = eps], pconfigiterator.CALL) = eps
''') + budget('S_external')


def failure_checks():
    return reach('S_back', 'S_initial', 1) + lines(r'''
S_back.ACTIVEFIBER = (n_fiber)
S_back.CURRENT = (pcallcontext_callback)
S_back.FRAMES = pframe_cursor :: pframe_tail*
pframe_cursor.TODO = (CONFIG_ITERATOR pconfigiterator text_stage) :: ptask_cursor*
S_back.FIBERCALLERS = pfibercaller :: pfibercaller_tail*
pfibercaller.OBJECT = n_fiber
pfibervm_actor = pfibercaller.VM
pfibervm_actor.CURRENT = (pcallcontext_actor)
pfibervm_actor.FRAMES = pframe_actor :: pframe_actor_tail*
pframe_actor.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_actor*
''') + frozen_cursor('S_back', 'E') + lines(r'''
pgeneratorop.OBJECT = n_target
pgeneratorop.NAME = "next"
$generator_saved_ids(S_back.FRAMES) = eps
$generator_resume_ids(S_back.TODO) = eps
$generator_saved_fiber_ids(S_back) = [n_target]
~$generator_external_actor_scope(S_back, n_target)
$generator_external_actor_vm(S_back, pfibervm_actor, n_target)
$heap_count(HOBJECT n_target, $fiber_vm_nodes(pfibervm_actor)) = 1
$heap_count(HOBJECT n_input, $fiber_vm_nodes(pfibervm_actor)) = 0
$generator_external_cursor_view(S_back, S_back, pconfigiterator.CALL) = ((S_view, pconfigiterator, text_stage))
S_view = $generator_set(S_back, n_target, pgenerator[.PHASE = GENERATOR_PAUSED])
$heap_graph(S_view) = H_real
$call_descriptors_input_scope(S_back, S_back) = S_view
$config_iterator_frame(S_view, pcallcontext_callback, pframe_cursor)
~$generator_iterator_entry_site(S_back, pconfigiterator.CALL)
''') + reach('S_invoke', 'S_back', 2, 250) + lines(r'''
S_invoke.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
pconfigcall.OWNER = (n_target)
pconfigcall.KIND = pconfigiterator.CALL.KIND
pconfigcall.SITE = pconfigiterator.CALL.SITE
pconfigcall.INDEX = 2
pconfigcall.SENT = [NAMED_SENT (KNOWN (PINT 13))]
pconfigcall.PACKS = eps
~((HOBJECT n_input) <- S_invoke.ALLOCATIONS)
$generator_external_invoke_view(S_invoke, S_invoke, pconfigcall) = (S_invoke_view)
$config_iterator_copied_header(S_invoke, pconfigcall)
$config_invoke_valid(S_invoke, pconfigcall)
S_args_found = $drive_steps(S_invoke, 1)
S_args_found.COMPLETION = BUDGET
S_args = S_args_found[.COMPLETION = NORMAL]
S_args.TODO = (GENERATOR_ARGS pgeneratorop_outer eps poperand_outer*) :: ptask_tail*
poperand_outer* = [KNOWN (PINT 13)]
pgeneratorop_outer.OBJECT = n_target
pgeneratorop_outer.NAME = "send"
$generator_saved_ids(S_args.FRAMES) = eps
$generator_saved_fiber_ids(S_args) = [n_target]
PhpStep: S_args ~> S_error
S_error.COMPLETION = THROWING n_error
S_error.TODO = ptask_tail*
S_error.OBJECTS[n_error] = THROWABLE pthrowable
pthrowable.KIND = "Error"
S_error.OBJECTS[n_target] = GENERATOR pgenerator
$generator_saved_ids(S_error.FRAMES) = eps
$generator_resume_ids(S_error.TODO) = eps
$generator_saved_fiber_ids(S_error) = [n_target]
$heap_owners($heap_graph(S_error), HOBJECT n_target) = 1
''') + budget('S_back')


def checks(name, program, path):
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    values = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')', 'S_initial.COMPLETION = BUDGET']
    return values + (normal_checks() if name == 'i139-parked-cursor-external-next' else failure_checks())


def run(out=None, process_seconds=600):
    catalog = {x['id']: x for x in json.loads(CATALOG.read_bytes())}
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='generator-parked-cursor-reentry-state-', dir=ROOT / '.tools'))
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
