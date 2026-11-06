#!/usr/bin/env python3
"""Check real Aggregate acquisition roots, return promotion and cancellation."""
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
CATALOG = Path(__file__).with_name('generator_aggregate_acquisition_review_cases.json')
EXPECTED = {
    'i132-sole-cursor-getter-normal-send': '1d27c0f706b36caa3524451c7186967ef0719e579883a50c4064dd88cdb8104c',
    'i132-sole-cursor-getter-given-fiber': 'bda156cb3712754960fda78d4dc05d3b0d749c75fed9b7bc6b1aece5fe3ff479',
    'i132-sole-cursor-getter-return-type-error': 'd4d8c40fdbdca52686028a6ea1c46a1854394c4365d0322d6b8b7e47e74cb976',
}
PREFIX = r'''
dec $test_i132_front(pstate, nat) : bool
def $test_i132_front(S, 0) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = $ptascii("GET|")
def $test_i132_front(S, 1) = true
  -- if S.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask*
def $test_i132_front(S, 2) = true
  -- if S.TODO = (GENERATOR_ARGS pgeneratorop phpType7* poperand*) :: ptask*
def $test_i132_front(S, 3) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_AGGREGATE pconfigaggregate) :: ptask*
def $test_i132_front(S, 4) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = $ptascii("FIN|")
def $test_i132_front(S, n_stage) = false -- otherwise
dec $test_i132_seek(pstate, nat, nat) : pstate
def $test_i132_seek(S, n_stage, 0) = S
def $test_i132_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_i132_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $test_i132_seek(S, n_stage, n) = $test_i132_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_i132_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
'''


def lines(text):
    return [x.strip() for x in text.splitlines() if x.strip()]


def reach(state, start, stage, limit):
    return [state + '_found = $test_i132_seek(' + start + ', ' + str(stage) + ', ' + str(limit) + ')',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_i132_front(' + state + ', ' + str(stage) + ')']


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


def cursor(state, method, selected):
    kind = 'INTRINSIC_GENERATOR_METHOD "' + method + '" ' + ('(pgeneratormethodselection)' if selected else 'eps')
    result = lines(r'''
pconfigaggregate.CALL = pconfigcall
pconfigaggregate.OBJECT = n_aggregate
pconfigaggregate.INPUT = VARIABLE $ptascii("aggregate") z_input
pconfigcall.OWNER = (n_target)
pconfigcall.INDEX = 1
pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_prefix))]
pconfigcall.NAMED = false
pconfigcall.PACKS = eps
pconfigcall.SELECTION = eps
STATE.OBJECTS[n_target] = GENERATOR pgenerator_target
pgenerator_target.PHASE = GENERATOR_PAUSED
$generator_aggregate_site(STATE, pconfigcall)
$config_aggregate_scope(STATE, pconfigaggregate)
$config_aggregate_valid(STATE, pconfigaggregate)
$task_nodes(CONFIG_AGGREGATE pconfigaggregate) = [HOBJECT n_target, HOBJECT n_prefix]
STATE.ITERATORS = eps
'''.replace('STATE', state))
    result += ['pconfigcall.KIND = ' + kind]
    if selected:
        result += ['pgeneratormethodselection.NAME = $ptascii("' + method + '")']
    return result


def normal():
    values = reach('S_get', 'S_initial', 0, 1000) + lines(r'''
S_get.ACTIVEFIBER = eps
S_get.CURRENT = (pcallcontext_getter)
S_get.FRAMES = pframe_caller :: pframe_tail*
pframe_caller.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_get_tail*
pconfigaggregate.OBJECT = n_aggregate
pcallcontext_getter.INSTANCE = eps
$call_context_roots((pcallcontext_getter)) = eps
$config_aggregate_frame(S_get, pcallcontext_getter, pframe_caller)
$config_aggregate_method(S_get, n_aggregate) = (pmethoddesc_getter)
$target_nodes(AGGREGATE_METHOD_TARGET n_aggregate pmethoddesc_getter.FUNCTION.ORIGIN) = eps
''')
    # Source validation uses the caller scope, while owners below use real S_get.
    values += lines(r'''
pconfigaggregate.CALL = pconfigcall
pconfigaggregate.INPUT = VARIABLE $ptascii("aggregate") z_input
pconfigcall.OWNER = (n_target)
pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD "send" (pgeneratormethodselection)
pgeneratormethodselection.NAME = $ptascii("send")
pconfigcall.INDEX = 1
pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_prefix))]
$task_nodes(CONFIG_AGGREGATE pconfigaggregate) = [HOBJECT n_target, HOBJECT n_prefix]
H_get = $heap_graph(S_get)
$heap_owners(H_get, HOBJECT n_target) = 1
$heap_owners(H_get, HOBJECT n_prefix) = 1
$heap_owners(H_get, HOBJECT n_aggregate) = 1
$heap_count(HOBJECT n_aggregate, $task_nodes(CONFIG_AGGREGATE pconfigaggregate)) = 0
$call_descriptors_valid(S_get)
$heap_valid(H_get)
''')
    values += reach('S_return', 'S_get', 1, 500) + lines(r'''
S_return.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_return_tail*
S_return.RESULT = KNOWN (POBJECT n_data)
S_return.CURRENT = eps
$lookup(S_return.ENV, $ptascii("aggregate")) = (n_aggregate_cv)
S_return.STORE[n_aggregate_cv] = DEFINED (POBJECT n_aggregate)
$lookup(S_return.ENV, $ptascii("iterator")) = (n_data_cv)
S_return.STORE[n_data_cv] = DEFINED (POBJECT n_data)
H_return = $heap_graph(S_return)
$heap_owners(H_return, HOBJECT n_target) = 1
$heap_owners(H_return, HOBJECT n_prefix) = 1
$heap_owners(H_return, HOBJECT n_aggregate) = 1
$heap_owners(H_return, HOBJECT n_data) = 2
$heap_count(HOBJECT n_data, H_return.ROOTS) = 1
~$config_aggregate_owners(S_return, pconfigaggregate, 1)
$config_aggregate_live_callee(S_return, pconfigaggregate)
$config_aggregate_return_allowed(S_return, pconfigaggregate)
S_missing = S_return[.TODO = ptask_return_tail*]
~$config_aggregate_live_callee(S_missing, pconfigaggregate)
S_no_aggregate = S_return[.STORE[n_aggregate_cv] = DEFINED PNULL]
~$generator_aggregate_live_source(S_no_aggregate, pconfigaggregate)
~$config_aggregate_live_callee(S_no_aggregate, pconfigaggregate)
PhpStep: S_return ~> S_promoted
S_promoted.TODO = (CONFIG_ITERATOR pconfigiterator "rewind-start") :: ptask_return_tail*
pconfigiterator.CALL = pconfigcall
pconfigiterator.OBJECT = n_data
pconfigiterator.INPUT = pconfigaggregate.INPUT
pconfigiterator.PRODUCER = (n_aggregate)
pconfigiterator.ITEMS = eps
S_promoted.RESULT = KNOWN PNULL
H_promoted = $heap_graph(S_promoted)
$heap_owners(H_promoted, HOBJECT n_target) = 1
$heap_owners(H_promoted, HOBJECT n_prefix) = 1
$heap_owners(H_promoted, HOBJECT n_aggregate) = 1
$heap_owners(H_promoted, HOBJECT n_data) = 2
$heap_count(HOBJECT n_data, H_promoted.ROOTS) = 1
$heap_count(HOBJECT n_data, $task_nodes(CONFIG_ITERATOR pconfigiterator "rewind-start")) = 1
$heap_count(HOBJECT n_aggregate, $task_nodes(CONFIG_ITERATOR pconfigiterator "rewind-start")) = 0
''')
    values += budget('S_return') + ['S_return_one.TODO = S_promoted.TODO']
    values += reach('S_api', 'S_return_one[.COMPLETION = NORMAL]', 2, 800) + lines(r'''
S_api.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_prefix)])) :: ptask_api_tail*
pgeneratorop.OBJECT = n_target
pgeneratorop.NAME = "send"
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
H_api = $heap_graph(S_api)
$heap_owners(H_api, HOBJECT n_data) = 0
~((HOBJECT n_data) <- S_api.ALLOCATIONS)
$heap_owners(H_api, HOBJECT n_target) = 1
$heap_owners(H_api, HOBJECT n_prefix) = 1
$heap_owners(H_api, HOBJECT n_aggregate) = 1
''')
    return values


def failure(fiber):
    values = reach('S_pending', 'S_initial', 3, 1000)
    values += ['S_pending.TODO = (THROW_SEARCH n_error) :: (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*']
    values += cursor('S_pending', 'send' if fiber else 'current', fiber)
    values += [('$destructor_operational' if fiber else '~$destructor_operational') + '(S_pending)']
    values += lines(r'''
H_pending = $heap_graph(S_pending)
$heap_owners(H_pending, HOBJECT n_target) = 1
$heap_owners(H_pending, HOBJECT n_prefix) = 1
$heap_owners(H_pending, HOBJECT n_aggregate) = 1
~$config_aggregate_owners(S_pending, pconfigaggregate, 1)
S_popped = S_pending[.TODO = (THROW_SEARCH n_error) :: ptask_tail*]
H_popped = $heap_graph(S_popped)
$heap_owners(H_popped, HOBJECT n_target) = 0
$heap_owners(H_popped, HOBJECT n_prefix) = 0
$heap_owners(H_popped, HOBJECT n_aggregate) = 1
~$config_aggregate_owners(S_popped, pconfigaggregate, 0)
$throwable_field(S_pending, n_error, "previous") = PNULL
''')
    if fiber:
        values += lines(r'''
$lookup(S_pending.ENV, $ptascii("given")) = (n_given_cv)
S_pending.STORE[n_given_cv] = DEFINED (POBJECT n_error)
$object_name(S_pending, n_error) = $ptascii("Exception")
''')
    else:
        values += ['$object_name(S_pending, n_error) = $ptascii("TypeError")']
    values += lines(r'''
PhpStep: S_pending ~> S_queued
S_queued.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_prefix), DESTRUCTION_VALUE (HOBJECT n_target)]
pdestructionoperation.SOURCE = THROW_SEARCH n_error
pdestructionoperation.PENDING = (n_error)
pdestructionoperation.CALLER = S_pending.CURRENT
pdestructionoperation.ORIGIN = (pconfigcall.SITE)
pdestructionoperation.CLEANUP = eps
pdestructionoperation.NOGC = eps
pdestructionoperation.NOGCEXTRA = eps
$eager_operation_source_valid(S_queued, pdestructionoperation)
H_queued = $heap_graph(S_queued)
$heap_owners(H_queued, HOBJECT n_target) = 1
$heap_owners(H_queued, HOBJECT n_prefix) = 1
$heap_owners(H_queued, HOBJECT n_aggregate) = 1
''')
    values += budget('S_pending')
    values += lines(r'''
S_pending_one.TODO = S_queued.TODO
$heap_owners(H_S_pending_one, HOBJECT n_target) = 1
$heap_owners(H_S_pending_one, HOBJECT n_prefix) = 1
$heap_owners(H_S_pending_one, HOBJECT n_aggregate) = 1
''')
    values += reach('S_finally', 'S_pending_one[.COMPLETION = NORMAL]', 4, 300)
    values += lines(r'''
H_finally = $heap_graph(S_finally)
$heap_owners(H_finally, HOBJECT n_prefix) = 0
~((HOBJECT n_prefix) <- S_finally.ALLOCATIONS)
$heap_owners(H_finally, HOBJECT n_target) = 1
$heap_owners(H_finally, HOBJECT n_aggregate) = 1
$throwable_field(S_finally, n_error, "previous") = PNULL
''')
    return values


def checks(name, program, path):
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    initial = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'i132-sole-cursor-getter-normal-send':
        return initial + normal()
    assert name in ('i132-sole-cursor-getter-given-fiber', 'i132-sole-cursor-getter-return-type-error')
    return initial + failure(name.endswith('given-fiber'))


def run(out=None, process_seconds=600):
    catalog = {x['id']: x for x in json.loads(CATALOG.read_bytes())}
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='generator-aggregate-acquisition-state-', dir=ROOT / '.tools'))
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
