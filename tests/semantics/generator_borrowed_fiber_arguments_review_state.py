#!/usr/bin/env python3
"""Check real saved Fiber VMs during borrowed Generator argument traversal."""
import base64
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import tempfile

from exception_handler_review import recorded
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).with_name('generator_borrowed_fiber_arguments_review_cases.json')
EXPECTED = {
    'i130-borrowed-next-suspend-normal-send': 'bdb696bbd8fef8f71c9893d6272bc41487cd33bddf887aae9ab4b73c3d80793a',
    'i130-borrowed-next-suspend-prefix-cache-source-throw': 'ed3e3eca0f4ff2dc5b5c0f3890d5b100881a9f156ae57f2d3b8c76d41e5d28a3',
}
PREFIX = r'''
dec $test_i130_echo(pstate, ptbytes) : bool
def $test_i130_echo(S, ptbytes) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = ptbytes
def $test_i130_echo(S, ptbytes) = false -- otherwise
dec $test_i130_front(pstate, nat) : bool
def $test_i130_front(S, 0) = $test_i130_echo(S, $ptascii("PARK|"))
def $test_i130_front(S, 1) = $test_i130_echo(S, $ptascii("RESUMED|"))
def $test_i130_front(S, 2) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
def $test_i130_front(S, 3) = true
  -- if S.TODO = (THROW_SEARCH n) :: (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if pgeneratorop.STARTPACK /\ pgeneratorop.BORROWED
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $test_i130_front(S, 4) = $test_i130_echo(S, $ptascii("CACHED|"))
def $test_i130_front(S, 5) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if $generator_api_kind(pconfigcall.KIND)
def $test_i130_front(S, 6) = $test_i130_echo(S, $ptascii("FIN|"))
def $test_i130_front(S, n_stage) = false -- otherwise
dec $test_i130_seek(pstate, nat, nat) : pstate
def $test_i130_seek(S, n_stage, 0) = S
def $test_i130_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_i130_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_i130_seek(S, n_stage, n) = $test_i130_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_i130_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
'''


def lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def reach(state, start, stage, limit=4000):
    return [state + '_found = $test_i130_seek(' + start + ', ' + str(stage) + ', ' + str(limit) + ')',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_i130_front(' + state + ', ' + str(stage) + ')']


def public(state):
    return ['$call_descriptors_valid(' + state + ')', '$heap_valid($heap_graph(' + state + '))']


def budget(state):
    return [state + '_pause = $drive(' + state + ', 0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        *public(state + '_pause'),
        state + '_one = $drive(' + state + ', 1)',
        state + '_one.COMPLETION = BUDGET',
        '$drive(' + state + '_pause[.COMPLETION = NORMAL], 1) = ' + state + '_one',
        *public(state + '_one')]


def parked_checks():
    values = reach('S_park', 'S_initial', 0) + lines(r'''
S_park.ACTIVEFIBER = eps
S_park.CURRENT = eps
S_park.FRAMES = eps
S_park.FIBERCALLERS = eps
$lookup(S_park.ENV, $ptascii("fiber")) = (n_fiber_cv)
S_park.STORE[n_fiber_cv] = DEFINED (POBJECT n_fiber)
S_park.OBJECTS[n_fiber] = FIBER pfiber
pfiber.STATUS = FIBER_SUSPENDED
pfiber.VM = (pfibervm)
pfibervm.CURRENT = (pcallcontext_source)
pfibervm.FRAMES = pframe_source :: pframe_tail*
pframe_source.CONTEXT = (pcallcontext_handler)
pframe_source.TODO = (GENERATOR_RESUME pgeneratorop_source) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*
pconfiggenerator.CALL = pconfigcall
pconfiggenerator.OBJECT = n_source
pconfiggenerator.INPUT = VARIABLE $ptascii("source") z_input
pconfiggenerator.PRODUCER = eps
pconfigcall.OWNER = (n_target)
pconfigcall.SITE = porigin_call
pconfigcall.LINE = z_call
pconfigcall.PACKS = eps
pconfigcall.SELECTION = eps
~pconfigcall.NAMED
pgeneratorop_source = {OBJECT n_source, NAME "next", SITE porigin_input, LINE z_input, LOOP eps, ADVANCE false, ARGUMENTS eps, STARTPACK true, BORROWED true, SELECTION eps}
pframe_source.ORIGIN = (porigin_input)
S_park.OBJECTS[n_source] = GENERATOR pgenerator_source
pgenerator_source.PHASE = GENERATOR_RUNNING
pgenerator_source.FRAME = eps
pgenerator_source.CLOSURE = eps
pgenerator_source.CREATION = eps
pgenerator_source.ACCESS = eps
pgenerator_source.DELEGATE = eps
pgenerator_source.PARKED = eps
pgenerator_source.RETURN = eps
pgenerator_source.REFCELL = eps
pgenerator_source.BORROWED = eps
~pgenerator_source.PENDING_INIT
pcallcontext_source.FUNCTION = pgenerator_source.FUNCTION
pcallcontext_source.TARGET = pgenerator_source.FUNCTION
pcallcontext_source.INSTANCE = eps
pcallcontext_source.RECEIVER = eps
S_park.OBJECTS[n_target] = GENERATOR pgenerator_target
pgenerator_target.PHASE = GENERATOR_PAUSED
n_source =/= n_target
$lookup(S_park.ENV, $ptascii("target")) = (n_target_cv)
$lookup(S_park.ENV, $ptascii("source")) = (n_source_cv)
S_park.STORE[n_target_cv] = DEFINED PNULL
$generator_operation_nodes(pgeneratorop_source) = eps
$generator_operation_trace(S_park, pgeneratorop_source) = eps
$call_context_roots((pcallcontext_source)) = eps
$heap_count(HOBJECT n_source, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_target, $fiber_vm_nodes(pfibervm)) = 1
$heap_owners($heap_graph(S_park), HOBJECT n_target) = 1
S_view = $fiber_vm_restore(S_park, pfibervm)[.COMPLETION = NORMAL]
S_view.ACTIVEFIBER = eps
S_caller = $constant_frame_scope(S_view, pframe_source, pframe_tail*)
$config_traversable_argument(S_caller, pconfigcall) = ((expression_input, true, eps, porigin_input, z_input))
$config_traversable_prefix(S_caller, pconfigcall)
$generator_source_consumer(S_caller, pconfiggenerator)
$config_generator_operation_tasks(S_caller, pgeneratorop_source, pframe_source.TODO)
$fiber_generator_callee_valid(S_view, pgenerator_source, pcallcontext_source)
$fiber_generator_cached_reference_valid(S_view, pgenerator_source, pcallcontext_source)
$generator_saved_ids(pfibervm.FRAMES) = [n_source]
$generator_resume_ids(pfibervm.TODO) = eps
$fiber_generator_body_id(S_view) = (n_source)
S_active = S_view[.ACTIVEFIBER = (n_fiber)]
$fiber_generator_body_id(S_active) = (n_source)
$fiber_transfer_domain(S_active)
$fiber_vm_valid(S_park, pfibervm, (n_fiber), eps)
$foreach_aggregate_close_vm_ids(S_park, pfibervm) = [n_source]
$generator_saved_fiber_ids(S_park) = [n_source]
$generator_owners_valid(S_park)
pframe_missing = pframe_source[.TODO = (GENERATOR_RESUME pgeneratorop_source) :: ptask_tail*]
S_missing = S_view[.FRAMES = pframe_missing :: pframe_tail*]
$fiber_generator_body_id(S_missing) = eps
~$fiber_vm_valid(S_park, pfibervm[.FRAMES = pframe_missing :: pframe_tail*], (n_fiber), eps)
S_duplicate = S_view[.FRAMES = pframe_source :: pframe_source :: pframe_tail*]
$fiber_generator_body_id(S_duplicate) = eps
~$fiber_vm_valid(S_park, pfibervm[.FRAMES = pframe_source :: pframe_source :: pframe_tail*], (n_fiber), eps)
pconfiggenerator_bad = pconfiggenerator[.CALL = pconfigcall[.OWNER = (n_source)]]
pframe_bad = pframe_source[.TODO = (GENERATOR_RESUME pgeneratorop_source) :: (CONFIG_GENERATOR pconfiggenerator_bad "next") :: ptask_tail*]
$fiber_generator_body_id(S_view[.FRAMES = pframe_bad :: pframe_tail*]) = eps
pframe_line = pframe_source[.TODO = (GENERATOR_RESUME pgeneratorop_source[.LINE = $(z_input + 1)]) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*]
$fiber_generator_body_id(S_view[.FRAMES = pframe_line :: pframe_tail*]) = eps
pconfiggenerator_ini = pconfiggenerator[.CALL = pconfigcall[.KIND = INTRINSIC_INI_SET]]
pframe_ini = pframe_source[.TODO = (GENERATOR_RESUME pgeneratorop_source) :: (CONFIG_GENERATOR pconfiggenerator_ini "next") :: ptask_tail*]
$fiber_generator_body_id(S_view[.FRAMES = pframe_ini :: pframe_tail*]) = eps
''')
    values += lines(r'''
pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD "send" eps
pconfigcall.INDEX = 0
pconfigcall.SENT = eps
pconfiggenerator.ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 17))]
pgenerator_source.VALUE = (PINT 17)
S_park.STORE[n_source_cv] = DEFINED PNULL
$config_generator_argument_nodes(pconfiggenerator) = eps
$task_nodes(CONFIG_GENERATOR pconfiggenerator "next") = [HOBJECT n_source, HOBJECT n_target]
$heap_owners($heap_graph(S_park), HOBJECT n_source) = 1
''')
    return values + public('S_park') + budget('S_park')


def resumed_checks():
    return reach('S_resumed', 'S_park_one[.COMPLETION = NORMAL]', 1) + lines(r'''
S_resumed.ACTIVEFIBER = (n_fiber)
S_resumed.CURRENT = (pcallcontext_source)
S_resumed.FRAMES = pframe_source :: pframe_tail*
S_resumed.OBJECTS[n_fiber] = FIBER pfiber_running
pfiber_running.STATUS = FIBER_RUNNING
pfiber_running.VM = eps
S_resumed.OBJECTS[n_source] = GENERATOR pgenerator_source
$lookup(S_resumed.ENV, $ptascii("received")) = (n_received_cv)
S_resumed.STORE[n_received_cv] = DEFINED (PINT 23)
$generator_saved_fiber_ids(S_resumed) = eps
$generator_saved_ids(S_resumed.FRAMES) = [n_source]
$fiber_generator_body_id(S_resumed) = (n_source)
$heap_owners($heap_graph(S_resumed), HOBJECT n_target) = 1
''') + public('S_resumed')


def normal_checks():
    values = parked_checks() + resumed_checks() + lines(r'''
$heap_owners($heap_graph(S_resumed), HOBJECT n_source) = 1
''')
    values += reach('S_invoke', 'S_resumed', 2) + lines(r'''
S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask_tail*
$heap_owners($heap_graph(S_invoke), HOBJECT n_source) = 0
~((HOBJECT n_source) <- S_invoke.ALLOCATIONS)
$heap_owners($heap_graph(S_invoke), HOBJECT n_target) = 1
$config_generator_retired_scope(S_invoke, pconfiggenerator)
$config_generator_argument_nodes(pconfiggenerator) = eps
PhpStep: S_invoke ~> S_call
S_call.TODO = (CONFIG_INVOKE pconfigcall_copied) :: ptask_tail*
pconfigcall_copied = pconfigcall[.INDEX = 1][.SENT = [NAMED_SENT (KNOWN (PINT 17))]]
$config_invoke_valid(S_call, pconfigcall_copied)
PhpStep: S_call ~> S_args
S_args.TODO = (GENERATOR_ARGS pgeneratorop_target eps ([KNOWN (PINT 17)])) :: ptask_tail*
pgeneratorop_target.OBJECT = n_target
pgeneratorop_target.NAME = "send"
~pgeneratorop_target.STARTPACK
~pgeneratorop_target.BORROWED
pgeneratorop_target.ARGUMENTS = eps
$task_nodes(GENERATOR_ARGS pgeneratorop_target eps ([KNOWN (PINT 17)])) = [HOBJECT n_target]
$generator_saved_fiber_ids(S_args) = eps
''')
    return values + public('S_invoke') + public('S_args') + budget('S_args')


def throwing_checks():
    # N retains the shared saved-VM/forgery/resume laws. This owning contrast
    # checks the new computed-prefix cache roots and actual ordered cancellation.
    values = reach('S_park', 'S_initial', 0, 1500) + lines(r'''
S_park.ACTIVEFIBER = eps
S_park.CURRENT = eps
S_park.FRAMES = eps
S_park.FIBERCALLERS = eps
$lookup(S_park.ENV, $ptascii("fiber")) = (n_fiber_cv)
S_park.STORE[n_fiber_cv] = DEFINED (POBJECT n_fiber)
S_park.OBJECTS[n_fiber] = FIBER pfiber
pfiber.STATUS = FIBER_SUSPENDED
pfiber.VM = (pfibervm)
pfibervm.CURRENT = (pcallcontext_source)
pfibervm.FRAMES = pframe_source :: pframe_tail*
pframe_source.CONTEXT = (pcallcontext_handler)
pframe_source.TODO = (GENERATOR_RESUME pgeneratorop_source) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*
pconfiggenerator.CALL = pconfigcall
pconfiggenerator.OBJECT = n_source
pconfiggenerator.INPUT = VARIABLE $ptascii("source") z_input
pconfiggenerator.PRODUCER = eps
pconfiggenerator.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_cache))]
pconfigcall.OWNER = (n_target)
pconfigcall.SITE = porigin_call
pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD "send" (pgeneratormethodselection)
pgeneratormethodselection.NAME = $ptascii("send")
pconfigcall.INDEX = 1
pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_prefix))]
pconfigcall.PACKS = eps
pconfigcall.SELECTION = eps
~pconfigcall.NAMED
pgeneratorop_source = {OBJECT n_source, NAME "next", SITE porigin_input, LINE z_input, LOOP eps, ADVANCE false, ARGUMENTS eps, STARTPACK true, BORROWED true, SELECTION eps}
S_park.OBJECTS[n_source] = GENERATOR pgenerator_source
pgenerator_source.PHASE = GENERATOR_RUNNING
pgenerator_source.FRAME = eps
pgenerator_source.VALUE = (POBJECT n_cache)
pgenerator_source.REFCELL = eps
pgenerator_source.DELEGATE = eps
pgenerator_source.PARKED = eps
S_park.OBJECTS[n_target] = GENERATOR pgenerator_target
pgenerator_target.PHASE = GENERATOR_PAUSED
n_source =/= n_target
$lookup(S_park.ENV, $ptascii("target")) = (n_target_cv)
$lookup(S_park.ENV, $ptascii("source")) = (n_source_cv)
$lookup(S_park.ENV, $ptascii("value")) = (n_value_cv)
$lookup(S_park.ENV, $ptascii("method")) = (n_method_cv)
S_park.STORE[n_target_cv] = DEFINED PNULL
S_park.STORE[n_source_cv] = DEFINED (POBJECT n_source)
S_park.STORE[n_value_cv] = DEFINED PNULL
S_park.STORE[n_method_cv] = DEFINED (PSTRING_CARRIER INTERNED_STRING $ptascii("current"))
$config_generator_argument_nodes(pconfiggenerator) = [HOBJECT n_prefix, HOBJECT n_cache]
$task_nodes(CONFIG_GENERATOR pconfiggenerator "next") = [HOBJECT n_source, HOBJECT n_prefix, HOBJECT n_cache, HOBJECT n_target]
$heap_count(HOBJECT n_source, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_target, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_prefix, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_cache, $fiber_vm_nodes(pfibervm)) = 1
$heap_owners($heap_graph(S_park), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_park), HOBJECT n_source) = 2
$heap_owners($heap_graph(S_park), HOBJECT n_prefix) = 1
$heap_owners($heap_graph(S_park), HOBJECT n_cache) = 2
S_view = $fiber_vm_restore(S_park, pfibervm)[.COMPLETION = NORMAL]
S_view.ACTIVEFIBER = eps
S_caller = $constant_frame_scope(S_view, pframe_source, pframe_tail*)
$generator_source_consumer(S_caller, pconfiggenerator)
$config_generator_operation_tasks(S_caller, pgeneratorop_source, pframe_source.TODO)
$fiber_generator_body_id(S_view) = (n_source)
$generator_saved_fiber_ids(S_park) = [n_source]
$heap_valid($heap_graph(S_park))
''')
    values += reach('S_pending', 'S_park', 5, 1000) + lines(r'''
S_pending.ACTIVEFIBER = (n_fiber)
S_pending.CURRENT = (pcallcontext_handler)
S_pending.OBJECTS[n_fiber] = FIBER pfiber_running
pfiber_running.STATUS = FIBER_RUNNING
pfiber_running.VM = eps
S_pending.OBJECTS[n_source] = GENERATOR pgenerator_closed
pgenerator_closed.PHASE = GENERATOR_CLOSED
pgenerator_closed.FRAME = eps
pgenerator_closed.VALUE = (POBJECT n_cache)
$lookup(S_pending.ENV, $ptascii("source")) = (n_source_live_cv)
S_pending.STORE[n_source_live_cv] = DEFINED (POBJECT n_source)
S_pending.TODO = (THROW_SEARCH n_error) :: (CONFIG_INVOKE pconfigcall_copied) :: ptask_tail*
pconfigcall_copied.KIND = pconfigcall.KIND
pconfigcall_copied.OWNER = (n_target)
pconfigcall_copied.INDEX = 2
pconfigcall_copied.SENT = [NAMED_SENT (KNOWN (POBJECT n_prefix)), NAMED_SENT (KNOWN (POBJECT n_cache))]
$object_name(S_pending, n_error) = $ptascii("Exception")
$string_bytes($throwable_field(S_pending, n_error, "message")) = ($ptascii("source"))
$throwable_field(S_pending, n_error, "previous") = PNULL
$heap_owners($heap_graph(S_pending), HOBJECT n_source) = 1
$heap_owners($heap_graph(S_pending), HOBJECT n_prefix) = 1
$heap_owners($heap_graph(S_pending), HOBJECT n_cache) = 2
$heap_owners($heap_graph(S_pending), HOBJECT n_target) = 1
$destructor_operational(S_pending)
$config_iterator_copied_call(S_pending, pconfigcall_copied)
$call_task_valid(S_pending, CONFIG_INVOKE pconfigcall_copied)
PhpStep: S_pending ~> S_staged
S_staged.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_argv) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_argv) :: ptask_tail*
pdestructionrelease_argv.JOBS = [DESTRUCTION_VALUE (HOBJECT n_prefix), DESTRUCTION_VALUE (HOBJECT n_cache), DESTRUCTION_VALUE (HOBJECT n_target)]
pdestructionoperation_argv.SOURCE = THROW_SEARCH n_error
pdestructionoperation_argv.PENDING = (n_error)
pdestructionoperation_argv.CALLER = S_pending.CURRENT
pdestructionoperation_argv.ORIGIN = S_pending.ORIGIN
pdestructionoperation_argv.CLEANUP = eps
pdestructionoperation_argv.NOGC = eps
pdestructionoperation_argv.NOGCEXTRA = eps
$eager_operation_source_valid(S_staged, pdestructionoperation_argv)
$task_nodes(DESTRUCTOR_RELEASE pdestructionrelease_argv) = [HOBJECT n_prefix, HOBJECT n_cache, HOBJECT n_target]
$heap_owners($heap_graph(S_staged), HOBJECT n_prefix) = 1
$heap_owners($heap_graph(S_staged), HOBJECT n_cache) = 2
$heap_owners($heap_graph(S_staged), HOBJECT n_target) = 1
''')
    values += budget('S_pending')
    values += reach('S_finally', 'S_staged', 6, 600) + lines(r'''
$heap_owners($heap_graph(S_finally), HOBJECT n_prefix) = 0
~((HOBJECT n_prefix) <- S_finally.ALLOCATIONS)
$heap_owners($heap_graph(S_finally), HOBJECT n_cache) = 1
$heap_owners($heap_graph(S_finally), HOBJECT n_source) = 1
$heap_owners($heap_graph(S_finally), HOBJECT n_target) = 1
$throwable_field(S_finally, n_error, "previous") = PNULL
''')
    return values


def reuse_heap_graphs(conditions):
    # States returned by the source driver are immutable. Preserve each
    # predicate while computing its repeated pure graph value once.
    pattern = r'\$heap_graph\((S_[A-Za-z0-9_]+)\)'
    counts = {}
    for state in re.findall(pattern, '\n'.join(conditions)):
        counts[state] = counts.get(state, 0) + 1
    bound = set()
    result = []
    for condition in conditions:
        bindings = []
        def replace(match):
            state = match.group(1)
            if counts[state] == 1:
                return match.group(0)
            graph = 'H_i130_' + state[2:]
            if state not in bound:
                bindings.append(graph + ' = $heap_graph(' + state + ')')
                bound.add(state)
            return graph
        rewritten = re.sub(pattern, replace, condition)
        result.extend(bindings)
        result.append(rewritten)
    return result


def checks(name, program, path):
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    initial = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'i130-borrowed-next-suspend-normal-send':
        return initial + normal_checks()
    assert name == 'i130-borrowed-next-suspend-prefix-cache-source-throw'
    return reuse_heap_graphs(initial + throwing_checks())


def run(out=None, process_seconds=1200):
    catalog = {row['id']: row for row in json.loads(CATALOG.read_bytes())}
    rows = [catalog[name] for name in EXPECTED]
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='generator-borrowed-fiber-arguments-state-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ, LC_ALL='C', TZ='UTC')
    environment.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    records = []
    for row in rows:
        assert row['source_sha256'] == EXPECTED[row['id']]
        assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
        directory = out / row['id']; directory.mkdir()
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
        conditions = checks(row['id'], checked['fixture'], source)
        fixture = directory / 'test.watsup'
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
            '  -- ' + (condition if condition.startswith('PhpStep:') else 'if ' + condition) + '\n'
            for condition in conditions))
        (directory / 'assertions.json').write_text(json.dumps(conditions, indent=2) + '\n')
        process = recorded([ROOT / 'tests/semantics/_build/default/numeric_runner.exe', '--sl', *modules, fixture], directory, 'model', environment, process_seconds)
        passed = not process['timeout'] and process['exit'] == 0 and (directory / 'model.stdout').read_bytes() == b'true\n' and (directory / 'model.stderr').read_bytes() == b''
        records.append({'id': row['id'], 'source_sha256': row['source_sha256'], 'assertions': len(conditions), 'process': process, 'passed': passed})
        print(row['id'], len(conditions), 'PASS' if passed else 'FAIL', flush=True)
        if not passed:
            break
    report = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'selection': list(EXPECTED), 'records': records, 'passed': len(records) == len(rows) and all(row['passed'] for row in records)}
    (out / 'raw-report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    raise SystemExit(0 if run() else 1)
