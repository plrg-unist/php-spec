#!/usr/bin/env python3
"""Check finite native Generator prefixes, borrowed resumes and cache roots."""
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
CATALOG = Path(__file__).with_name('generator_finite_prefix_arguments_review_cases.json')
EXPECTED = {
    'i128-scalar-four-count': 'd8b8d229694cc76eae617a6169573ac30e162506f6f8b0155bfbacc828d10508',
    'i128-owning-three-source-throw': 'dec33c47ae959762f04747cac54af7570a12e47195cbcdfe824cc8fc33381a60',
    'i128-distinct-owning-three-count': '413a6bab35bc0538c4a08a0ee9ad936f787c127ba234467420105b0ba3d7833c',
}
PREFIX = r'''
dec $test_i128_echo(pstate, ptbytes) : bool
def $test_i128_echo(S, ptbytes) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = ptbytes
def $test_i128_echo(S, ptbytes) = false -- otherwise
dec $test_i128_front(pstate, nat) : bool
def $test_i128_front(S, 0) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 2
def $test_i128_front(S, 1) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 3
def $test_i128_front(S, 2) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
def $test_i128_front(S, 3) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
def $test_i128_front(S, 4) = $test_i128_echo(S, $ptascii("AFTER-3|"))
def $test_i128_front(S, 5) = true
  -- if S.TODO = (THROW_SEARCH n) :: (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if pgeneratorop.STARTPACK /\ pgeneratorop.BORROWED
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $test_i128_front(S, 6) = $test_i128_echo(S, $ptascii("CACHED|"))
def $test_i128_front(S, n_stage) = false -- otherwise
dec $test_i128_seek(pstate, nat, nat) : pstate
def $test_i128_seek(S, n_stage, 0) = S
def $test_i128_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_i128_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_i128_seek(S, n_stage, n) = $test_i128_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_i128_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
'''


def lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def reach(state, start, stage):
    return [state + '_found = $test_i128_seek(' + start + ', ' + str(stage) + ', 4000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_i128_front(' + state + ', ' + str(stage) + ')']


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


def call_header(state, generator, method):
    return [
        generator + '.CALL = pconfigcall',
        'pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD "' + method + '" eps',
        'pconfigcall.OWNER = (n_target)',
        'pconfigcall.INDEX = 0', 'pconfigcall.SENT = eps',
        'pconfigcall.PACKS = eps', 'pconfigcall.SELECTION = eps', '~pconfigcall.NAMED',
        generator + '.OBJECT = n_source', generator + '.PRODUCER = eps',
        generator + '.INPUT = VARIABLE $ptascii("source") z_input',
        '$intrinsic_argument(' + state + ', pconfigcall.SITE, 0) = ((expression_input, true, eps, porigin_input, z_input))',
        '$lookup(' + state + '.ENV, $ptascii("source")) = (n_source_cv)',
        '$lookup(' + state + '.ENV, $ptascii("target")) = (n_target_cv)',
        state + '.STORE[n_target_cv] = DEFINED PNULL']


def dispatch(state, values):
    sent = '[' + ', '.join('NAMED_SENT (KNOWN (' + v + '))' for v in values) + ']'
    operands = '[' + ', '.join('KNOWN (' + v + ')' for v in values) + ']'
    return [
        'PhpStep: ' + state + ' ~> S_call',
        'S_call.TODO = (CONFIG_INVOKE pconfigcall_copied) :: ptask_tail*',
        'pconfigcall_copied = pconfigcall[.INDEX = 1][.SENT = ' + sent + ']',
        '$config_invoke_valid(S_call, pconfigcall_copied)',
        'PhpStep: S_call ~> S_args',
        'S_args.TODO = (GENERATOR_ARGS pgeneratorop eps (' + operands + ')) :: ptask_tail*',
        'pgeneratorop.OBJECT = n_target', 'pgeneratorop.NAME = "current"',
        'pgeneratorop.ARGUMENTS = eps', 'pgeneratorop.SELECTION = eps',
        '~pgeneratorop.BORROWED', '~pgeneratorop.STARTPACK',
        '$task_nodes(GENERATOR_ARGS pgeneratorop eps (' + operands + ')) = $config_nodes(pconfigcall_copied)',
        '$heap_owners($heap_graph(S_args), HOBJECT n_target) = 1',
        *public('S_args'), *budget('S_args')]


def scalar_checks():
    values = reach('S', 'S_initial', 0) + lines(r'''
S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask_tail*
pconfiggenerator.ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 11)), ENTRY (KINT 1) (DIRECT (PINT 22))]
''') + call_header('S', 'pconfiggenerator', 'current') + lines(r'''
S.STORE[n_source_cv] = DEFINED (POBJECT n_source)
S.OBJECTS[n_source] = GENERATOR pgenerator_source
pgenerator_source.PHASE = GENERATOR_PAUSED
pgenerator_source.VALUE = (PINT 33)
pgenerator_source.KEY = (PINT 2)
pgenerator_source.REFCELL = eps
$config_generator_valid(S, pconfiggenerator, "ready")
$config_generator_prefix_allowed(S, pconfiggenerator, 3)
$config_generator_prefix_allowed(S, pconfiggenerator, 1000)
$config_generator_send_allowed(S, pconfiggenerator)
$heap_owners($heap_graph(S), HOBJECT n_source) = 2
$heap_owners($heap_graph(S), HOBJECT n_target) = 1
pconfiggenerator_ini = pconfiggenerator[.CALL = pconfigcall[.KIND = INTRINSIC_INI_SET]]
$config_generator_prefix_allowed(S, pconfiggenerator_ini, 0)
$config_generator_prefix_allowed(S, pconfiggenerator_ini, 2)
~$config_generator_prefix_allowed(S, pconfiggenerator_ini, 3)
~$config_generator_prefix_allowed(S, pconfiggenerator_ini, 1000)
~$config_generator_prefix_allowed(S, pconfiggenerator[.INPUT = KNOWN (POBJECT n_source)], 3)
~$config_generator_prefix_allowed(S, pconfiggenerator[.CALL = pconfigcall[.OWNER = (n_source)]], 3)
PhpStep: S ~> S_third
S_third.TODO = (CONFIG_GENERATOR pconfiggenerator_third "next") :: ptask_tail*
pconfiggenerator_third = pconfiggenerator[.ITEMS = pconfiggenerator.ITEMS ++ [ENTRY (KINT 2) (DIRECT (PINT 33))]]
$config_generator_history(S_third, pconfiggenerator_third)
$config_generator_argument_nodes(pconfiggenerator_third) = eps
''')
    values += public('S') + budget('S') + reach('S_fourth', 'S_third', 1) + lines(r'''
S_fourth.TODO = (CONFIG_GENERATOR pconfiggenerator_third "ready") :: ptask_tail*
S_fourth.OBJECTS[n_source] = GENERATOR pgenerator_fourth
pgenerator_fourth.VALUE = (PINT 44)
pgenerator_fourth.KEY = (PINT 3)
$config_generator_send_allowed(S_fourth, pconfiggenerator_third)
PhpStep: S_fourth ~> S_copied
S_copied.TODO = (CONFIG_GENERATOR pconfiggenerator_four "next") :: ptask_tail*
pconfiggenerator_four = pconfiggenerator_third[.ITEMS = pconfiggenerator_third.ITEMS ++ [ENTRY (KINT 3) (DIRECT (PINT 44))]]
$config_generator_history(S_copied, pconfiggenerator_four)
$config_generator_argument_nodes(pconfiggenerator_four) = eps
''')
    values += reach('S_finish', 'S_copied', 2) + lines(r'''
S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator_four "finish") :: ptask_tail*
S_finish.STORE[n_source_cv] = DEFINED PNULL
S_finish.OBJECTS[n_source] = GENERATOR pgenerator_closed
pgenerator_closed.PHASE = GENERATOR_CLOSED
pgenerator_closed.FRAME = eps
pgenerator_closed.VALUE = (PINT 44)
$node_children(S_finish, HOBJECT n_source) = eps
$heap_owners($heap_graph(S_finish), HOBJECT n_source) = 1
$heap_owners($heap_graph(S_finish), HOBJECT n_target) = 1
$config_generator_quiet_closed(S_finish, pconfiggenerator_four)
$config_generator_finish_allowed(S_finish, pconfiggenerator_four)
~$config_generator_callee(S_finish, pconfigcall.OWNER, 1)
$generator_source_live_callee(S_finish, pconfiggenerator_four)
~$destructor_operational(S_finish)
''')
    values += public('S_finish') + budget('S_finish') + lines(r'''
S_finish_one.TODO = (CONFIG_GENERATOR pconfiggenerator_four "invoke") :: ptask_tail*
~((HOBJECT n_source) <- S_finish_one.ALLOCATIONS)
$heap_owners($heap_graph(S_finish_one), HOBJECT n_source) = 0
$heap_owners($heap_graph(S_finish_one), HOBJECT n_target) = 1
''')
    values += reach('S_invoke', 'S_finish_one[.COMPLETION = NORMAL]', 3) + lines(r'''
S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator_four "invoke") :: ptask_tail*
$config_generator_retired_scope(S_invoke, pconfiggenerator_four)
''')
    return values + public('S_invoke') + dispatch('S_invoke', ['PINT 11', 'PINT 22', 'PINT 33', 'PINT 44'])


def repeated_checks():
    values = reach('S_body', 'S_initial', 4) + lines(r'''
S_body.CURRENT = (pcallcontext_source)
S_body.FRAMES = pframe_source :: pframe_source_tail*
pframe_source.TODO = (GENERATOR_RESUME pgeneratorop_source) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*
''') + call_header('S_body', 'pconfiggenerator', 'send') + lines(r'''
S_body.STORE[n_source_cv] = DEFINED (POBJECT n_source)
S_body.OBJECTS[n_source] = GENERATOR pgenerator_running
pgenerator_running.PHASE = GENERATOR_RUNNING
pgenerator_running.FRAME = eps
pgenerator_running.VALUE = (POBJECT n_token)
pgenerator_running.REFCELL = eps
pconfiggenerator.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_token)), ENTRY (KINT 1) (DIRECT (POBJECT n_token)), ENTRY (KINT 2) (DIRECT (POBJECT n_token))]
pgeneratorop_source = {OBJECT n_source, NAME "next", SITE porigin_input, LINE z_input, LOOP eps, ADVANCE false, ARGUMENTS eps, STARTPACK true, BORROWED true, SELECTION eps}
$generator_operation_valid(S_body, pgeneratorop_source)
$generator_operation_nodes(pgeneratorop_source) = eps
$generator_operation_trace(S_body, pgeneratorop_source) = eps
$call_context_roots((pcallcontext_source)) = eps
$config_generator_argument_nodes(pconfiggenerator) = [HOBJECT n_token, HOBJECT n_token, HOBJECT n_token]
$heap_owners($heap_graph(S_body), HOBJECT n_token) = 4
$heap_owners($heap_graph(S_body), HOBJECT n_source) = 2
$heap_owners($heap_graph(S_body), HOBJECT n_target) = 1
S_boundary = $constant_frame_scope(S_body, pframe_source, pframe_source_tail*)
$config_generator_valid(S_boundary, pconfiggenerator, "next")
$config_generator_items(S_boundary, pconfiggenerator, pconfiggenerator.ITEMS)
$config_generator_owning_items_live(S_boundary, pconfiggenerator.ITEMS)
''')
    values += public('S_body') + budget('S_body') + reach('S_error', 'S_body', 5) + lines(r'''
S_error.TODO = (THROW_SEARCH n_error) :: (GENERATOR_RESUME pgeneratorop_source) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*
S_error.OBJECTS[n_source] = GENERATOR pgenerator_closed
pgenerator_closed.PHASE = GENERATOR_CLOSED
pgenerator_closed.FRAME = eps
pgenerator_closed.VALUE = (POBJECT n_token)
$object_name(S_error, n_error) = $ptascii("Exception")
$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("source"))
$throwable_field(S_error, n_error, "previous") = PNULL
$throwable_field(S_error, n_error, "trace") = PARRAY n_trace
S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_source_trace)), ENTRY (KINT 1) (DIRECT (PARRAY n_caller_trace))]
$trace_array_field(S_error, n_source_trace, $ptascii("function")) = PSTRING $ptascii("source128S")
$trace_array_field(S_error, n_caller_trace, $ptascii("function")) = PSTRING $ptascii("run128S")
$heap_owners($heap_graph(S_error), HOBJECT n_token) = 4
PhpStep: S_error ~> S_cursor
S_cursor.TODO = (THROW_SEARCH n_error) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*
S_popped = S_cursor[.TODO = (THROW_SEARCH n_error) :: ptask_tail*]
$heap_owners($heap_graph(S_popped), HOBJECT n_target) = 0
$heap_owners($heap_graph(S_popped), HOBJECT n_token) = 1
$generator_source_discard_state(S_popped, pconfiggenerator, "next") = (S_hold)
pconfigcall_copied = pconfigcall[.INDEX = 1][.SENT = [NAMED_SENT (KNOWN (POBJECT n_token)), NAMED_SENT (KNOWN (POBJECT n_token)), NAMED_SENT (KNOWN (POBJECT n_token))]]
S_hold.TODO = (THROW_SEARCH n_error) :: (CONFIG_INVOKE pconfigcall_copied) :: ptask_tail*
$config_nodes(pconfigcall_copied) = [HOBJECT n_target, HOBJECT n_token, HOBJECT n_token, HOBJECT n_token]
$heap_owners($heap_graph(S_hold), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_hold), HOBJECT n_source) = 1
$heap_owners($heap_graph(S_hold), HOBJECT n_token) = 4
~$destructor_operational(S_cursor)
PhpStep: S_cursor ~> S_staged
S_staged = S_hold
S_staged.EVENTS = S_cursor.EVENTS
$throwable_field(S_staged, n_error, "trace") = PARRAY n_trace
''')
    values += public('S_error') + public('S_staged') + budget('S_cursor')
    values += reach('S_cached', 'S_staged', 6) + lines(r'''
$heap_owners($heap_graph(S_cached), HOBJECT n_source) = 1
$heap_owners($heap_graph(S_cached), HOBJECT n_token) = 1
$heap_owners($heap_graph(S_cached), HOBJECT n_target) = 0
~((HOBJECT n_target) <- S_cached.ALLOCATIONS)
S_cached.OBJECTS[n_source] = GENERATOR pgenerator_cached
pgenerator_cached.PHASE = GENERATOR_CLOSED
pgenerator_cached.FRAME = eps
pgenerator_cached.VALUE = (POBJECT n_token)
''')
    return values + public('S_cached')


def distinct_checks():
    values = reach('S_finish', 'S_initial', 2) + lines(r'''
S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask_tail*
''') + call_header('S_finish', 'pconfiggenerator', 'current') + lines(r'''
pconfiggenerator.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_first)), ENTRY (KINT 1) (DIRECT (POBJECT n_middle)), ENTRY (KINT 2) (DIRECT (POBJECT n_last))]
n_first =/= n_middle
n_middle =/= n_last
n_first =/= n_last
S_finish.STORE[n_source_cv] = DEFINED (POBJECT n_source)
S_finish.OBJECTS[n_source] = GENERATOR pgenerator_closed
pgenerator_closed.PHASE = GENERATOR_CLOSED
pgenerator_closed.FRAME = eps
pgenerator_closed.VALUE = (POBJECT n_last)
pgenerator_closed.REFCELL = eps
$config_generator_items(S_finish, pconfiggenerator, pconfiggenerator.ITEMS)
$config_generator_owning_items_live(S_finish, pconfiggenerator.ITEMS)
$config_generator_argument_nodes(pconfiggenerator) = [HOBJECT n_first, HOBJECT n_middle, HOBJECT n_last]
$node_children(S_finish, HOBJECT n_source) = [HOBJECT n_last]
$heap_owners($heap_graph(S_finish), HOBJECT n_source) = 2
$heap_owners($heap_graph(S_finish), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_finish), HOBJECT n_first) = 1
$heap_owners($heap_graph(S_finish), HOBJECT n_middle) = 1
$heap_owners($heap_graph(S_finish), HOBJECT n_last) = 2
$config_generator_finish_allowed(S_finish, pconfiggenerator)
S_lost_cv = S_finish[.STORE[n_source_cv] = DEFINED PNULL]
$heap_owners($heap_graph(S_lost_cv), HOBJECT n_source) = 1
~$config_generator_finish_allowed(S_lost_cv, pconfiggenerator)
''')
    values += public('S_finish') + budget('S_finish') + reach('S_invoke', 'S_finish_one[.COMPLETION = NORMAL]', 3) + lines(r'''
S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask_tail*
$heap_owners($heap_graph(S_invoke), HOBJECT n_source) = 1
$heap_owners($heap_graph(S_invoke), HOBJECT n_first) = 1
$heap_owners($heap_graph(S_invoke), HOBJECT n_middle) = 1
$heap_owners($heap_graph(S_invoke), HOBJECT n_last) = 2
''')
    values += public('S_invoke') + dispatch('S_invoke', ['POBJECT n_first', 'POBJECT n_middle', 'POBJECT n_last'])
    values += reach('S_cached', 'S_args', 6) + lines(r'''
$heap_owners($heap_graph(S_cached), HOBJECT n_source) = 1
$heap_owners($heap_graph(S_cached), HOBJECT n_first) = 0
$heap_owners($heap_graph(S_cached), HOBJECT n_middle) = 0
$heap_owners($heap_graph(S_cached), HOBJECT n_last) = 1
~((HOBJECT n_first) <- S_cached.ALLOCATIONS)
~((HOBJECT n_middle) <- S_cached.ALLOCATIONS)
~((HOBJECT n_target) <- S_cached.ALLOCATIONS)
S_cached.OBJECTS[n_source] = GENERATOR pgenerator_cached
pgenerator_cached.PHASE = GENERATOR_CLOSED
pgenerator_cached.FRAME = eps
pgenerator_cached.VALUE = (POBJECT n_last)
''')
    return values + public('S_cached')


def checks(name, program, path):
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    initial = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'i128-scalar-four-count':
        return initial + scalar_checks()
    if name == 'i128-owning-three-source-throw':
        return initial + repeated_checks()
    assert name == 'i128-distinct-owning-three-count'
    return initial + distinct_checks()

def run(out=None, process_seconds=600):
    catalog = {row['id']: row for row in json.loads(CATALOG.read_bytes())}
    rows = [catalog[name] for name in EXPECTED]
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='generator-finite-prefix-arguments-state-', dir=ROOT / '.tools'))
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
