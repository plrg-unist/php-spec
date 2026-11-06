#!/usr/bin/env python3
"""Check borrowed Aggregate reentry, real owners and DATA promotion."""
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
CATALOG = Path(__file__).with_name('generator_aggregate_reentry_review_cases.json')
EXPECTED = {
    'i135-getter-nested-next-return': '27e0fe69916c231dc858325e5d1992b164a98f465a9f134a32ba8ecca18c9a35',
    'i135-getter-nested-send-failure-literal': '1bf24a56c98b925de3953336b519acf009e7ca97ea76af018039adff52489b4c',
}
PREFIX = r'''
dec $test_i135_front(pstate, nat) : bool
def $test_i135_front(S, 0) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = $ptascii("INNER|")
def $test_i135_front(S, 1) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = $ptascii("GET-RESUMED|")
def $test_i135_front(S, 2) = true
  -- if S.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask*
def $test_i135_front(S, 3) = true
  -- if S.TODO = (GENERATOR_ARGS pgeneratorop phpType7* poperand*) :: ptask*
def $test_i135_front(S, 4) = true
  -- if S.TODO = (STMT statement) :: ptask*
  -- if $lookup(S.ENV, $ptascii("error")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (POBJECT n_error)
  -- if $throwable_live(S, n_error)
def $test_i135_front(S, n_stage) = false -- otherwise
dec $test_i135_seek(pstate, nat, nat) : pstate
def $test_i135_seek(S, n_stage, 0) = S
def $test_i135_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_i135_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $test_i135_seek(S, n_stage, n) = $test_i135_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_i135_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
'''


def lines(text):
    return [x.strip() for x in text.splitlines() if x.strip()]


def reach(state, start, stage, limit):
    return [state + '_found = $test_i135_seek(' + start + ', ' + str(stage) + ', ' + str(limit) + ')',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_i135_front(' + state + ', ' + str(stage) + ')']


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
    normal = name == 'i135-getter-nested-next-return'
    assert normal or name == 'i135-getter-nested-send-failure-literal'
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    values = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')', 'S_initial.COMPLETION = BUDGET']
    values += reach('S_inner', 'S_initial', 0, 1200)
    values += lines(r'''
S_inner.CURRENT = (pcallcontext_body)
S_inner.FRAMES = pframe_resume :: pframe_getter :: pframe_tail*
pframe_resume.TODO = (GENERATOR_RESUME pgeneratorop_inner) :: ptask_resume_tail*
pframe_resume.CONTEXT = (pcallcontext_getter)
pframe_getter.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_getter_tail*
pconfigaggregate.CALL = pconfigcall
pconfigaggregate.OBJECT = n_aggregate
pconfigaggregate.INPUT = VARIABLE $ptascii("aggregate") z_input
pconfigcall.OWNER = (n_target)
pconfigcall.INDEX = @INDEX@
pconfigcall.SENT = @SENT@
pconfigcall.NAMED = false
pconfigcall.PACKS = eps
pconfigcall.SELECTION = eps
pgeneratorop_inner.OBJECT = n_target
pgeneratorop_inner.LOOP = eps
~pgeneratorop_inner.ADVANCE
~pgeneratorop_inner.STARTPACK
~pgeneratorop_inner.BORROWED
S_inner.OBJECTS[n_target] = GENERATOR pgenerator_running
pgenerator_running.PHASE = GENERATOR_RUNNING
pgenerator_running.FUNCTION = pcallcontext_body.FUNCTION
pgenerator_running.FRAME = eps
$context_target(pcallcontext_getter) = AGGREGATE_METHOD_TARGET n_aggregate pcallcontext_getter.FUNCTION
pcallcontext_getter.INSTANCE = eps
$call_context_roots((pcallcontext_getter)) = eps
$target_nodes(AGGREGATE_METHOD_TARGET n_aggregate pcallcontext_getter.FUNCTION) = eps
$generator_saved_ids(S_inner.FRAMES) = [n_target]
$fiber_generator_body_id(S_inner) = (n_target)
S_inner.ITERATORS = eps
$task_nodes(GENERATOR_RESUME pgeneratorop_inner) = [HOBJECT n_target]
$heap_count(HOBJECT n_target, $task_nodes(CONFIG_AGGREGATE pconfigaggregate)) = 1
$heap_count(HOBJECT n_aggregate, $task_nodes(CONFIG_AGGREGATE pconfigaggregate)) = 0
H_inner = $heap_graph(S_inner)
$heap_owners(H_inner, HOBJECT n_target) = 2
$heap_owners(H_inner, HOBJECT n_aggregate) = 1
(HOBJECT n_aggregate) <- S_inner.ALLOCATIONS
$heap_valid(H_inner)
'''.replace('@INDEX@','1' if normal else '0').replace('@SENT@','[NAMED_SENT (KNOWN (POBJECT n_prefix))]' if normal else 'eps'))
    if normal:
        values += lines(r'''
pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD "send" (pgeneratormethodselection)
pgeneratormethodselection.NAME = $ptascii("send")
pgeneratorop_inner.NAME = "next"
pgeneratorop_inner.ARGUMENTS = eps
$heap_owners(H_inner, HOBJECT n_prefix) = 1
S_caller = $constant_frame_scope(S_inner, pframe_getter, pframe_tail*)
$lookup(S_caller.ENV, $ptascii("aggregate")) = (n_aggregate_cv)
S_inner.STORE[n_aggregate_cv] = DEFINED (POBJECT n_aggregate)
$lookup(S_caller.ENV, $ptascii("iterator")) = (n_iterator_cv)
S_inner.STORE[n_iterator_cv] = DEFINED (POBJECT n_iterator)
$heap_owners(H_inner, HOBJECT n_iterator) = 1
$heap_count(HOBJECT n_iterator, $task_nodes(CONFIG_AGGREGATE pconfigaggregate)) = 0
S_no_owner = S_inner[.STORE[n_aggregate_cv] = DEFINED PNULL]
$heap_owners($heap_graph(S_no_owner), HOBJECT n_aggregate) = 0
$generator_iterator_reentry_view(S_no_owner) = eps
''')
    else:
        values += lines(r'''
pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD "current" eps
pgeneratorop_inner.NAME = "send"
pgeneratorop_inner.ARGUMENTS = [PINT 17]
$generator_traversable_source_index(S_inner, pconfigcall) = (0)
''')
    values += lines(r'''
$generator_iterator_reentry_view(S_inner) = ((S_view, pframe_resume, pframe_getter, pframe_tail*))
S_view = $generator_set(S_inner, n_target, pgenerator_running[.PHASE = GENERATOR_PAUSED])
$heap_graph(S_view) = H_inner
~$generator_aggregate_site(S_inner, pconfigcall)
$generator_aggregate_site(S_view, pconfigcall)
~$config_aggregate_frame(S_inner, pcallcontext_getter, pframe_getter)
$config_aggregate_frame(S_view, pcallcontext_getter, pframe_getter)
$useriter_frame(S_inner, pcallcontext_getter, pframe_getter)
$call_frame_scope(S_inner, pframe_resume, pframe_getter :: pframe_tail*) = $constant_frame_scope(S_view, pframe_resume, pframe_getter :: pframe_tail*)
$call_frame_scope(S_inner, pframe_getter, pframe_tail*) = $constant_frame_scope(S_view, pframe_getter, pframe_tail*)
$call_frame_scope(S_inner, pframe_resume, pframe_tail*) = $constant_frame_scope(S_inner, pframe_resume, pframe_tail*)
S_missing = S_inner[.FRAMES = pframe_resume :: pframe_tail*]
$fiber_generator_body_id(S_missing) = (n_target)
$generator_iterator_reentry_view(S_missing) = eps
$generator_resume_pairs(S_inner, S_inner.CURRENT, S_inner.FRAMES)
$call_descriptors_valid(S_inner)
''')
    values += budget('S_inner')
    values += ['$heap_owners(H_S_inner_one, HOBJECT n_target) = 2', '$heap_owners(H_S_inner_one, HOBJECT n_aggregate) = 1']
    if normal:
        values += ['$heap_owners(H_S_inner_one, HOBJECT n_prefix) = 1']
        values += reach('S_getter', 'S_inner_one[.COMPLETION = NORMAL]', 1, 650)
        values += lines(r'''
S_getter.CURRENT = (pcallcontext_getter)
S_getter.FRAMES = pframe_getter :: pframe_tail*
S_getter.OBJECTS[n_target] = GENERATOR pgenerator_paused
pgenerator_paused.PHASE = GENERATOR_PAUSED
$generator_iterator_reentry_view(S_getter) = eps
$config_aggregate_frame(S_getter, pcallcontext_getter, pframe_getter)
$call_frame_scope(S_getter, pframe_getter, pframe_tail*) = $constant_frame_scope(S_getter, pframe_getter, pframe_tail*)
''')
        values += reach('S_return', 'S_getter', 2, 500)
        values += lines(r'''
S_return.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_getter_tail*
S_return.RESULT = KNOWN (POBJECT n_iterator)
H_return = $heap_graph(S_return)
$heap_owners(H_return, HOBJECT n_target) = 1
$heap_owners(H_return, HOBJECT n_prefix) = 1
$heap_owners(H_return, HOBJECT n_aggregate) = 1
$heap_owners(H_return, HOBJECT n_iterator) = 2
$heap_count(HOBJECT n_iterator, H_return.ROOTS) = 1
PhpStep: S_return ~> S_promoted
S_promoted.TODO = (CONFIG_ITERATOR pconfigiterator "rewind-start") :: ptask_getter_tail*
pconfigiterator.CALL = pconfigcall
pconfigiterator.INPUT = pconfigaggregate.INPUT
pconfigiterator.OBJECT = n_iterator
pconfigiterator.PRODUCER = (n_aggregate)
S_promoted.RESULT = KNOWN PNULL
H_promoted = $heap_graph(S_promoted)
$heap_owners(H_promoted, HOBJECT n_iterator) = 2
$heap_owners(H_promoted, HOBJECT n_aggregate) = 1
$heap_count(HOBJECT n_iterator, $task_nodes(CONFIG_ITERATOR pconfigiterator "rewind-start")) = 1
$heap_count(HOBJECT n_aggregate, $task_nodes(CONFIG_ITERATOR pconfigiterator "rewind-start")) = 0
''')
        values += reach('S_api', 'S_promoted', 3, 850)
        values += lines(r'''
S_api.TODO = (GENERATOR_ARGS pgeneratorop_outer eps ([KNOWN (POBJECT n_prefix)])) :: ptask_api_tail*
pgeneratorop_outer.OBJECT = n_target
pgeneratorop_outer.NAME = "send"
pgeneratorop_outer.SITE = pconfigcall.SITE
H_api = $heap_graph(S_api)
$heap_owners(H_api, HOBJECT n_target) = 1
$heap_owners(H_api, HOBJECT n_prefix) = 1
$heap_owners(H_api, HOBJECT n_aggregate) = 1
$heap_owners(H_api, HOBJECT n_iterator) = 0
~((HOBJECT n_iterator) <- S_api.ALLOCATIONS)
''')
    else:
        values += reach('S_catch', 'S_inner_one[.COMPLETION = NORMAL]', 4, 1000)
        values += lines(r'''
$lookup(S_catch.ENV, $ptascii("error")) = (n_error_cell)
S_catch.STORE[n_error_cell] = DEFINED (POBJECT n_error)
$throwable_field(S_catch, n_error, "previous") = PNULL
$lookup($global_table_view(S_catch).ENV, $ptascii("iterator")) = (n_iterator_cv)
S_catch.STORE[n_iterator_cv] = DEFINED (POBJECT n_iterator)
H_catch = $heap_graph(S_catch)
$heap_owners(H_catch, HOBJECT n_target) = 0
$heap_owners(H_catch, HOBJECT n_aggregate) = 1
$heap_owners(H_catch, HOBJECT n_iterator) = 1
~((HOBJECT n_target) <- S_catch.ALLOCATIONS)
S_catch.ITERATORS = eps
$generator_saved_ids(S_catch.FRAMES) = eps
''')
    return values


def run(out=None, process_seconds=600):
    catalog = {x['id']: x for x in json.loads(CATALOG.read_bytes())}
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='generator-aggregate-reentry-state-', dir=ROOT / '.tools'))
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
