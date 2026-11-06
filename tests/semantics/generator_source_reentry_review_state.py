#!/usr/bin/env python3
"""Check actual dual Generator pairs, scoped history and cache owners."""
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
CATALOG = Path(__file__).with_name('generator_source_reentry_review_cases.json')
EXPECTED = {
    'i134-source-nested-next-normal': '0bc496be03c0399c894c8d93db8a373bc3ceeffb6c9969fc5020adfedf955876',
    'i134-source-nested-send-body-throw': '46c214510062e9affc107b82abcabe013ad29e0382398c90e1248926a1c92612',
}
PREFIX = r'''
dec $test_i134_front(pstate, nat) : bool
def $test_i134_front(S, 0) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = $ptascii("TARGET-INNER|")
def $test_i134_front(S, 1) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = $ptascii("SOURCE-RESUMED|")
def $test_i134_front(S, 2) = true
  -- if S.TODO = (GENERATOR_ARGS pgeneratorop phpType7* poperand*) :: ptask*
def $test_i134_front(S, 3) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = $ptascii("SOURCE-FIN|")
def $test_i134_front(S, 4) = true
  -- if S.TODO = (STMT statement) :: ptask*
  -- if $lookup(S.ENV, $ptascii("error")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (POBJECT n_error)
  -- if $throwable_live(S, n_error)
def $test_i134_front(S, n_stage) = false -- otherwise
dec $test_i134_seek(pstate, nat, nat) : pstate
def $test_i134_seek(S, n_stage, 0) = S
def $test_i134_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_i134_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $test_i134_seek(S, n_stage, n) = $test_i134_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_i134_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
'''


def lines(text):
    return [x.strip() for x in text.splitlines() if x.strip()]


def reach(state, start, stage, limit):
    return [state + '_found = $test_i134_seek(' + start + ', ' + str(stage) + ', ' + str(limit) + ')',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_i134_front(' + state + ', ' + str(stage) + ')']


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
    normal = name == 'i134-source-nested-next-normal'
    assert normal or name == 'i134-source-nested-send-body-throw'
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    values = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')', 'S_initial.COMPLETION = BUDGET']
    values += reach('S_inner', 'S_initial', 0, 1400)
    values += lines(r'''
S_inner.CURRENT = (pcallcontext_target)
S_inner.FRAMES = pframe_target :: pframe_source :: pframe_tail*
pframe_target.TODO = (GENERATOR_RESUME pgeneratorop_target) :: ptask_target_tail*
pframe_target.CONTEXT = (pcallcontext_source)
pframe_source.TODO = (GENERATOR_RESUME pgeneratorop_source) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_outer_tail*
pconfiggenerator.CALL = pconfigcall
pconfiggenerator.OBJECT = n_source
pconfiggenerator.INPUT = VARIABLE $ptascii("source") z_input
pconfiggenerator.PRODUCER = eps
pconfiggenerator.ITEMS = [ENTRY pkey_item (DIRECT (POBJECT n_token))]
$config_generator_key(S_inner, PINT 0) = (pkey_item)
pconfigcall.OWNER = (n_target)
n_source =/= n_target
pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD "send" (pgeneratormethodselection)
pgeneratormethodselection.OBJECT = n_target
pgeneratormethodselection.NAME = $ptascii("send")
pconfigcall.INDEX = @INDEX@
pconfigcall.SENT = @SENT@
pconfigcall.NAMED = false
pconfigcall.PACKS = eps
pconfigcall.SELECTION = eps
pgeneratorop_target.OBJECT = n_target
pgeneratorop_target.LOOP = eps
~pgeneratorop_target.ADVANCE
~pgeneratorop_target.STARTPACK
~pgeneratorop_target.BORROWED
pgeneratorop_source.OBJECT = n_source
pgeneratorop_source.NAME = "next"
pgeneratorop_source.STARTPACK
pgeneratorop_source.BORROWED
pgeneratorop_source.SELECTION = eps
pgeneratorop_source.ARGUMENTS = eps
S_inner.OBJECTS[n_target] = GENERATOR pgenerator_target
S_inner.OBJECTS[n_source] = GENERATOR pgenerator_source
pgenerator_target.PHASE = GENERATOR_RUNNING
pgenerator_source.PHASE = GENERATOR_RUNNING
pgenerator_target.FRAME = eps
pgenerator_source.FRAME = eps
pgenerator_target.FUNCTION = pcallcontext_target.FUNCTION
pgenerator_source.FUNCTION = pcallcontext_source.FUNCTION
$generator_values_nodes(pgenerator_source.VALUE) = [HOBJECT n_token]
pgenerator_source.REFCELL = eps
$generator_saved_ids(S_inner.FRAMES) = [n_target, n_source]
$fiber_generator_body_id(S_inner) = eps
$task_nodes(GENERATOR_RESUME pgeneratorop_target) = [HOBJECT n_target]
$task_nodes(GENERATOR_RESUME pgeneratorop_source) = eps
$heap_count(HOBJECT n_target, $task_nodes(CONFIG_GENERATOR pconfiggenerator "next")) = 1
$heap_count(HOBJECT n_source, $task_nodes(CONFIG_GENERATOR pconfiggenerator "next")) = 1
H_inner = $heap_graph(S_inner)
$heap_owners(H_inner, HOBJECT n_target) = 2
$heap_owners(H_inner, HOBJECT n_source) = 2
$heap_owners(H_inner, HOBJECT n_token) = 2
$heap_count(HOBJECT n_target, H_inner.ROOTS) = 2
$heap_count(HOBJECT n_source, H_inner.ROOTS) = 1
$heap_count(HOBJECT n_token, H_inner.ROOTS) = 1
$node_children(S_inner, HOBJECT n_source) = [HOBJECT n_token]
$heap_valid(H_inner)
'''.replace('@INDEX@','0' if normal else '1').replace('@SENT@','eps' if normal else '[NAMED_SENT (KNOWN (POBJECT n_prefix))]'))
    values += ['pgeneratorop_target.NAME = "' + ('next' if normal else 'send') + '"',
        'pgeneratorop_target.ARGUMENTS = ' + ('eps' if normal else '[PINT 17]')]
    if not normal:
        values += ['$heap_owners(H_inner, HOBJECT n_prefix) = 1']
    values += lines(r'''
$generator_source_reentry_view(S_inner) = ((S_view, pframe_target, pframe_source, pframe_tail*))
S_view = $generator_set(S_inner, n_target, pgenerator_target[.PHASE = GENERATOR_PAUSED])
$heap_graph(S_view) = H_inner
S_default = $constant_frame_scope(S_inner, pframe_source, pframe_tail*)
~$generator_source_consumer(S_default, pconfiggenerator)
~$config_generator_operation_tasks(S_default, pgeneratorop_source, pframe_source.TODO)
S_scope = $config_generator_operation_frame_scope(S_inner, pframe_source, pframe_tail*)
S_scope = $constant_frame_scope(S_view, pframe_source, pframe_tail*)
$generator_source_consumer(S_scope, pconfiggenerator)
$config_generator_operation_tasks(S_scope, pgeneratorop_source, pframe_source.TODO)
$config_generator_operation_valid(S_inner, pgeneratorop_source)
$call_frame_scope(S_inner, pframe_target, pframe_source :: pframe_tail*) = $constant_frame_scope(S_view, pframe_target, pframe_source :: pframe_tail*)
$call_frame_scope(S_inner, pframe_source, pframe_tail*) = $constant_frame_scope(S_view, pframe_source, pframe_tail*)
$config_generator_operation_frame_scope(S_inner, pframe_target, pframe_source :: pframe_tail*) = $constant_frame_scope(S_inner, pframe_target, pframe_source :: pframe_tail*)
$generator_resume_pairs(S_inner, S_inner.CURRENT, S_inner.FRAMES)
$call_descriptors_valid(S_inner)
S_missing = S_inner[.FRAMES = pframe_target :: pframe_source[.TODO = (GENERATOR_RESUME pgeneratorop_source) :: ptask_outer_tail*] :: pframe_tail*]
$generator_saved_ids(S_missing.FRAMES) = [n_target, n_source]
$generator_source_reentry_view(S_missing) = eps
S_alias = S_inner[.FRAMES = pframe_target :: pframe_source[.TODO = (GENERATOR_RESUME pgeneratorop_source) :: (CONFIG_GENERATOR pconfiggenerator[.CALL = pconfigcall[.OWNER = (n_source)]] "next") :: ptask_outer_tail*] :: pframe_tail*]
$generator_saved_ids(S_alias.FRAMES) = [n_target, n_source]
$generator_source_reentry_view(S_alias) = eps
''')
    values += budget('S_inner')
    values += lines(r'''
$heap_owners(H_S_inner_one, HOBJECT n_target) = 2
$heap_owners(H_S_inner_one, HOBJECT n_source) = 2
$heap_owners(H_S_inner_one, HOBJECT n_token) = 2
''')
    if not normal:
        values += ['$heap_owners(H_S_inner_one, HOBJECT n_prefix) = 1']
    values += reach('S_single', 'S_inner_one[.COMPLETION = NORMAL]', 1 if normal else 3, 650)
    values += lines(r'''
S_single.CURRENT = (pcallcontext_source)
S_single.FRAMES = pframe_source :: pframe_tail*
$generator_saved_ids(S_single.FRAMES) = [n_source]
$fiber_generator_body_id(S_single) = (n_source)
$generator_source_reentry_view(S_single) = eps
$config_generator_operation_frame_scope(S_single, pframe_source, pframe_tail*) = $constant_frame_scope(S_single, pframe_source, pframe_tail*)
S_single.OBJECTS[n_target] = GENERATOR pgenerator_returned
pgenerator_returned.PHASE = @PHASE@
H_single = $heap_graph(S_single)
$heap_owners(H_single, HOBJECT n_target) = 1
$heap_owners(H_single, HOBJECT n_source) = 2
$heap_owners(H_single, HOBJECT n_token) = 2
$generator_resume_pairs(S_single, S_single.CURRENT, S_single.FRAMES)
'''.replace('@PHASE@','GENERATOR_PAUSED' if normal else 'GENERATOR_CLOSED'))
    if not normal:
        values += ['$heap_owners(H_single, HOBJECT n_prefix) = 1']
    if normal:
        values += reach('S_api', 'S_single', 2, 800)
        values += lines(r'''
S_api.TODO = (GENERATOR_ARGS pgeneratorop_outer eps ([KNOWN (POBJECT n_token)])) :: ptask_api_tail*
pgeneratorop_outer.OBJECT = n_target
pgeneratorop_outer.NAME = "send"
pgeneratorop_outer.SITE = pconfigcall.SITE
pgeneratorop_outer.SELECTION = (pgeneratormethodselection)
S_api.OBJECTS[n_source] = GENERATOR pgenerator_closed
pgenerator_closed.PHASE = GENERATOR_CLOSED
H_api = $heap_graph(S_api)
$heap_owners(H_api, HOBJECT n_target) = 1
$heap_owners(H_api, HOBJECT n_source) = 1
$heap_owners(H_api, HOBJECT n_token) = 2
$heap_count(HOBJECT n_source, H_api.ROOTS) = 0
$node_children(S_api, HOBJECT n_source) = [HOBJECT n_token]
''')
    else:
        values += reach('S_catch', 'S_single', 4, 1000)
        values += lines(r'''
$lookup(S_catch.ENV, $ptascii("error")) = (n_error_cell)
S_catch.STORE[n_error_cell] = DEFINED (POBJECT n_error)
$throwable_field(S_catch, n_error, "previous") = PNULL
S_catch.OBJECTS[n_source] = GENERATOR pgenerator_closed
pgenerator_closed.PHASE = GENERATOR_CLOSED
H_catch = $heap_graph(S_catch)
$heap_owners(H_catch, HOBJECT n_target) = 0
$heap_owners(H_catch, HOBJECT n_prefix) = 0
$heap_owners(H_catch, HOBJECT n_source) = 1
$heap_owners(H_catch, HOBJECT n_token) = 1
$heap_count(HOBJECT n_token, H_catch.ROOTS) = 0
$node_children(S_catch, HOBJECT n_source) = [HOBJECT n_token]
~((HOBJECT n_target) <- S_catch.ALLOCATIONS)
~((HOBJECT n_prefix) <- S_catch.ALLOCATIONS)
''')
    return values


def run(out=None, process_seconds=600):
    catalog = {x['id']: x for x in json.loads(CATALOG.read_bytes())}
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='generator-source-reentry-state-', dir=ROOT / '.tools'))
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
