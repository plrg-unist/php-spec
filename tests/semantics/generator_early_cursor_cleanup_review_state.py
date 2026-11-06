#!/usr/bin/env python3
"""Check real early native Generator cursor roots and ordered cancellation."""
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
CATALOG = Path(__file__).with_name('generator_early_cursor_cleanup_review_cases.json')
EXPECTED = {
    'i131-current-prefix-scalar-pack-type-error': 'b36244d910fd2690e3c68c54ed7160a465ffdafbbaddcb1fd3ecaedc8475b616',
    'i131-send-prefix-argument-throw-skips-pack': 'bf87a348c555307c4cd49cb2b2fbafb5f7f078e347540f3abb82794c8c88ed9a',
}
PREFIX = r'''
dec $test_i131_front(pstate, nat) : bool
def $test_i131_front(S, 0) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_UNPACK_PREP pconfigcall) :: ptask*
def $test_i131_front(S, 1) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_SEND pconfigcall) :: ptask*
def $test_i131_front(S, 2) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = $ptascii("FIN|")
def $test_i131_front(S, n_stage) = false -- otherwise
dec $test_i131_seek(pstate, nat, nat) : pstate
def $test_i131_seek(S, n_stage, 0) = S
def $test_i131_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_i131_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $test_i131_seek(S, n_stage, n) = $test_i131_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_i131_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
'''


def lines(text):
    return [x.strip() for x in text.splitlines() if x.strip()]


def reach(state, start, stage, limit):
    return [state + '_found = $test_i131_seek(' + start + ', ' + str(stage) + ', ' + str(limit) + ')',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_i131_front(' + state + ', ' + str(stage) + ')']


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


def checks(name, program, path):
    prep = name == 'i131-current-prefix-scalar-pack-type-error'
    assert prep or name == 'i131-send-prefix-argument-throw-skips-pack'
    tag, other = ('CONFIG_UNPACK_PREP', 'CONFIG_SEND') if prep else ('CONFIG_SEND', 'CONFIG_UNPACK_PREP')
    method, rebound = ('current', 'send') if prep else ('send', 'current')
    state = 'S_pre' if prep else 'S_pending'
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    values = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')', 'S_initial.COMPLETION = BUDGET']
    if prep:
        # The source-backed diagnostic reached this unchanged pre-error prefix
        # at324 steps. The repair first acts on the following PREP transition.
        values += lines(r'''
S_fixed = $drive_steps(S_initial[.COMPLETION = NORMAL], 324)
S_fixed.COMPLETION = BUDGET
S_pre = S_fixed[.COMPLETION = NORMAL]
S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_pre_tail*
''')
    else:
        values += reach('S_pending', 'S_initial', 1, 1000)
        values += ['S_pending.TODO = (THROW_SEARCH n_error) :: (CONFIG_SEND pconfigcall) :: ptask_tail*']
    values += lines(r'''
STATE.CURRENT = (pcallcontext_handler)
STATE.ACTIVEFIBER = (n_fiber)
pconfigcall.OWNER = (n_target)
pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD "METHOD" (pgeneratormethodselection)
pgeneratormethodselection.NAME = $ptascii("METHOD")
pconfigcall.INDEX = 1
pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_prefix))]
pconfigcall.PACKS = eps
pconfigcall.SELECTION = eps
~pconfigcall.NAMED
STATE.OBJECTS[n_target] = GENERATOR pgenerator_target
pgenerator_target.PHASE = GENERATOR_PAUSED
STATE.ITERATORS = eps
$lookup(STATE.ENV, $ptascii("target")) = (n_target_cv)
$lookup(STATE.ENV, $ptascii("method")) = (n_method_cv)
STATE.STORE[n_target_cv] = DEFINED PNULL
STATE.STORE[n_method_cv] = DEFINED pvalue_method
$string_bytes(pvalue_method) = ($ptascii("REBOUND"))
$generator_traversable_source_index(STATE, pconfigcall) = (TERMINAL)
$generator_early_config_valid(STATE, TAG pconfigcall)
~$generator_early_config_valid(STATE, OTHER pconfigcall)
$task_nodes(TAG pconfigcall) = [HOBJECT n_target, HOBJECT n_prefix]
H_before = $heap_graph(STATE)
$heap_owners(H_before, HOBJECT n_prefix) = 1
$heap_owners(H_before, HOBJECT n_target) = 1
$heap_count(HOBJECT n_prefix, H_before.ROOTS) = 1
$heap_edge_owners(HOBJECT n_prefix, H_before.EDGES, H_before.NODES) = 0
$destructor_operational(STATE)
'''.replace('STATE', state).replace('"METHOD"', '"' + method + '"').replace('REBOUND', rebound).replace('TERMINAL', '1' if prep else '2').replace('OTHER', other).replace('TAG', tag))
    if prep:
        values += lines(r'''
$lookup(S_pre.ENV, $ptascii("pack")) = (n_pack_cv)
S_pre.STORE[n_pack_cv] = DEFINED (PINT 17)
PhpStep: S_pre ~> S_throw
S_throw.TODO = S_pre.TODO
S_throw.COMPLETION = THROWN "TypeError" ($ptascii("Only arrays and Traversables can be unpacked, int given")) z_error
$throwable_same_frame_continuation(S_pre, S_throw, ptask_pre_tail*) = S_throw
''')
        values += budget('S_pre')
        values += ['$heap_owners(H_S_pre_one, HOBJECT n_prefix) = 1', '$heap_owners(H_S_pre_one, HOBJECT n_target) = 1']
        values += reach('S_pending', 'S_pre_one[.COMPLETION = NORMAL]', 0, 100)
        values += ['S_pending.TODO = (THROW_SEARCH n_error) :: (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*']
    else:
        values += lines(r'''
$lookup(S_pending.ENV, $ptascii("value")) = (n_value_cv)
S_pending.STORE[n_value_cv] = DEFINED PNULL
$lookup(S_pending.ENV, $ptascii("given")) = (n_given_cv)
S_pending.STORE[n_given_cv] = DEFINED (POBJECT n_error)
~$config_traversable_prefix(S_pending, pconfigcall)
''')
    values += ['$object_name(S_pending, n_error) = $ptascii("' + ('TypeError' if prep else 'Exception') + '")']
    values += ['$throwable_field(S_pending, n_error, "previous") = PNULL']
    if prep:
        values += lines(r'''
S_pending.OBJECTS[n_target] = GENERATOR pgenerator_pending
pgenerator_pending.PHASE = GENERATOR_PAUSED
H_pending = $heap_graph(S_pending)
$heap_owners(H_pending, HOBJECT n_prefix) = 1
$heap_owners(H_pending, HOBJECT n_target) = 1
''')
    values += lines(r'''
PhpStep: S_pending ~> S_queued
S_queued.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_prefix), DESTRUCTION_VALUE (HOBJECT n_target)]
pdestructionoperation.SOURCE = THROW_SEARCH n_error
pdestructionoperation.PENDING = (n_error)
pdestructionoperation.CALLER = S_pending.CURRENT
pdestructionoperation.ORIGIN = S_pending.ORIGIN
pdestructionoperation.CLEANUP = eps
pdestructionoperation.NOGC = eps
pdestructionoperation.NOGCEXTRA = eps
$eager_operation_source_valid(S_queued, pdestructionoperation)
$task_nodes(DESTRUCTOR_RELEASE pdestructionrelease) = [HOBJECT n_prefix, HOBJECT n_target]
H_queued = $heap_graph(S_queued)
$heap_owners(H_queued, HOBJECT n_prefix) = 1
$heap_owners(H_queued, HOBJECT n_target) = 1
''')
    if prep:
        values += ['S_pending_one = $drive(S_pending, 1)', 'S_pending_one.COMPLETION = BUDGET'] + public('S_pending_one')
    else:
        values += budget('S_pending')
    values += lines(r'''
S_pending_one.TODO = S_queued.TODO
$heap_owners(H_S_pending_one, HOBJECT n_prefix) = 1
$heap_owners(H_S_pending_one, HOBJECT n_target) = 1
''')
    values += reach('S_finally', 'S_pending_one[.COMPLETION = NORMAL]', 2, 300)
    values += lines(r'''
H_finally = $heap_graph(S_finally)
$heap_owners(H_finally, HOBJECT n_prefix) = 0
~((HOBJECT n_prefix) <- S_finally.ALLOCATIONS)
$heap_owners(H_finally, HOBJECT n_target) = 1
$throwable_field(S_finally, n_error, "previous") = PNULL
''')
    return values


def run(out=None, process_seconds=600):
    catalog = {x['id']: x for x in json.loads(CATALOG.read_bytes())}
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='generator-early-cursor-cleanup-state-', dir=ROOT / '.tools'))
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
