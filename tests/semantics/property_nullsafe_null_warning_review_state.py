#!/usr/bin/env python3
"""Check final nullsafe fetch Warning after an ordinary-CV rebind to NULL."""
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
CATALOG = Path(__file__).with_name('property_nullsafe_null_warning_review_cases.json')
EXPECTED = {
    'property-nullsafe-null-warning': '347a4c8565ecde37f5d4e0adc823a13776cb74e161c18bdbc16540db7ce90e4d',
}
PREFIX = r'''
dec $test_property_null_warning_front(pstate, nat) : bool
def $test_property_null_warning_front(S, 0) = true
  -- if S.TODO = (NULLSAFE_CHECK (NExprFuncCall name (SEQUENCE eps) metadata) z false) :: (DIM_FETCH z) :: ptask*
def $test_property_null_warning_front(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("choose_dynamic_name")
  -- if S.TODO = (AT porigin (STMT (NStmtReturn expression metadata))) :: ptask*
def $test_property_null_warning_front(S, 2) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_BASE_NAME (BASE_VALUE (VARIABLE n_name* z_base)) z) :: (DIM_FETCH z) :: ptask*
def $test_property_null_warning_front(S, n_stage) = false -- otherwise
dec $test_property_null_warning_seek(pstate, nat, nat) : pstate
def $test_property_null_warning_seek(S, n_stage, 0) = S
def $test_property_null_warning_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_property_null_warning_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $test_property_null_warning_seek(S, n_stage, n) = $test_property_null_warning_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_property_null_warning_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
'''


def lines(text):
    return [x.strip() for x in text.splitlines() if x.strip()]


def reach(state, start, stage):
    return [f'{state}_found = $test_property_null_warning_seek({start}, {stage}, 768)',
            rf'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$test_property_null_warning_front({state}, {stage})']


def checks(name, program, path):
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    values = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
              'S_initial.COMPLETION = BUDGET']
    values += reach('S_before', 'S_initial', 0)
    values += [f'S_before.FILES = [SOURCEFILE 0 ($base64({encoded}))]']
    values += lines(r'''
S_before.TODO = (NULLSAFE_CHECK expression_name z false) :: (DIM_FETCH z) :: ptask_tail*
S_before.ORIGIN = (porigin_property)
porigin_property = PORIGIN n_unit pcpath_property
n_unit = 0
$origin_node(S_before.SOURCES, porigin_property) = (NExprNullsafePropertyFetch expression_base expression_name metadata_property)
S_before.BASE = BASE_VALUE (VARIABLE ptbytes_base z_base)
pbase_cv = BASE_VALUE (VARIABLE ptbytes_base z_base)
$property_cv_name_source(S_before) = ((ptbytes_base, ptbytes_replacement, ptbytes_key))
ptbytes_base = $ptascii("base") /\ ptbytes_replacement = $ptascii("replacement") /\ ptbytes_key = $ptascii("slot")
$nullsafe_property_task(S_before, expression_name, z, false, true)
z = 14
$lookup(S_before.ENV, ptbytes_base) = (n_base)
$lookup(S_before.ENV, $ptascii("old")) = (n_alias)
$lookup(S_before.ENV, ptbytes_replacement) = (n_replacement)
S_before.STORE[n_base] = DEFINED (POBJECT n_old)
S_before.STORE[n_alias] = DEFINED (POBJECT n_old)
S_before.STORE[n_replacement] = DEFINED PNULL
n_base =/= n_alias
S_before.CURRENT = eps /\ S_before.FRAMES = eps /\ S_before.GLOBALTABLE = eps
$property_cv_name_values(S_before, ptbytes_base, ptbytes_replacement, ptbytes_key) = ((n_old, PNULL))
~$property_cv_name_targets(S_before, ptbytes_base, ptbytes_replacement, ptbytes_key)
$property_cv_name_null_target(S_before, ptbytes_base, ptbytes_replacement, ptbytes_key)
$property_cv_nullsafe_entry(S_before)
S_before.ERRORHANDLER.CALLBACK = eps /\ S_before.OUTPUTBUFFERS = eps /\ ~S_before.OUTPUTBLOCKED
$long_and(S_before.REPORTING, 2) = 2
$display_state_mode(S_before) = 2
S_before.EVENTS = [OUTPUT ($ptascii("BEFORE|"))]
$heap_owners($heap_graph(S_before), HOBJECT n_old) = 2
S_read = $nullsafe_receiver(S_before, false, z)
S_read.COMPLETION = NORMAL /\ S_read.RESULT = KNOWN (POBJECT n_old)
S_read.EVENTS = S_before.EVENTS
S_carrier = S_read[.TODO = [$at_task($origin_child(S_before.ORIGIN, [PCFIELD 1]), EVAL expression_name), PROPERTY_BASE_NAME pbase_cv z, DIM_FETCH z] ++ ptask_tail*][.BASE = BASE_VALUE (KNOWN PNULL)][.RESULT = KNOWN PNULL]
PhpStep: S_before ~> S_carrier
$task_nodes(PROPERTY_BASE_NAME pbase_cv z) = eps
$heap_graph(S_carrier) = $heap_graph(S_before)
S_carrier.ENV = S_before.ENV /\ S_carrier.STORE = S_before.STORE
S_carrier.EVENTS = S_before.EVENTS
''')
    values += reach('S_helper', 'S_carrier', 1)
    values += lines(r'''
S_helper.CURRENT = (pcallcontext_helper)
pcallcontext_helper.ARGC = 0 /\ pcallcontext_helper.PARAMS = eps
pcallcontext_helper.CALLSITE = (PORIGIN n_unit (pcpath_property ++ [PCFIELD 1]))
S_helper.TODO = (AT porigin_return (STMT (NStmtReturn expression_key metadata_return))) :: ptask_return_tail*
S_helper.STORE[n_base] = DEFINED PNULL
S_helper.STORE[n_replacement] = DEFINED PNULL
S_helper.STORE[n_alias] = DEFINED (POBJECT n_old)
(n_base <- S_helper.REFCELLS) /\ (n_replacement <- S_helper.REFCELLS)
S_helper.FRAMES = pframe_main :: eps
pframe_main.CONTEXT = eps /\ pframe_main.LOCALS = eps
S_helper.EVENTS = S_before.EVENTS
$heap_owners($heap_graph(S_helper), HOBJECT n_old) = 1
S_main = $constant_frame_scope(S_helper, pframe_main, eps)
S_main.CURRENT = eps /\ S_main.FRAMES = eps
$call_tasks_valid(S_main, S_main.TODO)
S_marker_view = S_main[.ORIGIN = (porigin_property)]
$property_cv_name_count(S_marker_view.TODO, pbase_cv, z) = 1
$property_cv_name_pair(S_marker_view.TODO, pbase_cv, z)
$property_cv_name_task_valid(S_marker_view, pbase_cv, z)
$call_task_valid(S_marker_view, PROPERTY_BASE_NAME pbase_cv z)
$call_descriptors_valid(S_helper)
''')
    values += reach('S_name', 'S_helper', 2)
    values += lines(r'''
S_name.TODO = (PROPERTY_BASE_NAME pbase_cv z) :: (DIM_FETCH z) :: ptask_tail*
S_name.ORIGIN = (porigin_property)
S_name.CURRENT = eps /\ S_name.FRAMES = eps /\ S_name.GLOBALTABLE = eps
S_name.RESULT = KNOWN pvalue_name
$string_bytes(pvalue_name) = (ptbytes_key)
S_name.STORE[n_base] = DEFINED PNULL
S_name.STORE[n_alias] = DEFINED (POBJECT n_old)
S_name.EVENTS = S_before.EVENTS
$property_cv_name_task_valid(S_name, pbase_cv, z)
$property_cv_name_read(S_name, pbase_cv, z)
S_handler = S_name[.ERRORHANDLER.CALLBACK = (PSTRING ($ptascii("choose_dynamic_name")))][.ERRORHANDLER.LEVELS = 2]
$property_cv_name_task_valid(S_handler, pbase_cv, z)
~$property_cv_name_null_fetch(S_handler[.TODO = (DIM_FETCH z) :: ptask_tail*], z)
S_handler_out = $property_cv_name_finish(S_handler, pbase_cv, z)
S_handler_out.COMPLETION = UNSUPPORTED "deferred ordinary property receiver target"
S_handler_out.EVENTS = S_name.EVENTS
S_fetch = $property_cv_name_finish(S_name, pbase_cv, z)
PhpStep: S_name ~> S_fetch
S_fetch.COMPLETION = NORMAL /\ S_fetch.RESULT = KNOWN PNULL
S_fetch.TODO = (DIM_FETCH z) :: ptask_tail*
S_fetch.BASE = BASE_PROPERTY PNULL ptbytes_key
S_fetch.BASE =/= BASE_SHORT
$property_cv_name_null_fetch(S_fetch, z)
~$property_cv_name_null_fetch(S_fetch[.TODO = (ISSET_RESULT false z) :: ptask_tail*], z)
S_fetch.ENV = S_name.ENV /\ S_fetch.STORE = S_name.STORE
S_fetch.EVENTS = S_before.EVENTS
$base_nodes(S_fetch.BASE) = eps
$heap_owners($heap_graph(S_fetch), HOBJECT n_old) = 1
S_warning = $base_read(S_fetch, S_fetch.BASE, z)[.TODO = ptask_tail*][.BASE = BASE_VALUE (KNOWN PNULL)]
PhpStep: S_fetch ~> S_warning
S_warning.COMPLETION = NORMAL /\ S_warning.RESULT = KNOWN PNULL
S_warning.EVENTS = S_before.EVENTS ++ [DIAGNOSTIC "Warning" ($ptascii("Attempt to read property \"slot\" on null")) 14]
S_warning.FILES = S_before.FILES /\ S_warning.ORIGIN = (porigin_property)
$display_state_mode(S_warning) = 2
S_warning.ERRORHANDLER.CALLBACK = eps
S_warning.ENV = S_name.ENV /\ S_warning.STORE = S_name.STORE
$heap_owners($heap_graph(S_warning), HOBJECT n_old) = 1
S_pause = $drive(S_fetch, 0)
S_pause = S_fetch[.COMPLETION = BUDGET]
S_one = $drive(S_fetch, 1)
S_one = S_warning[.COMPLETION = BUDGET]
$drive(S_pause[.COMPLETION = NORMAL], 1) = S_one
$call_descriptors_valid(S_one)
S_masked = S_fetch[.REPORTING = 0]
S_suppressed = $base_read(S_masked, S_masked.BASE, z)[.TODO = ptask_tail*][.BASE = BASE_VALUE (KNOWN PNULL)]
PhpStep: S_masked ~> S_suppressed
S_suppressed.COMPLETION = NORMAL /\ S_suppressed.RESULT = KNOWN PNULL
S_suppressed.EVENTS = S_before.EVENTS
''')
    return values


def run(out=None, process_seconds=180):
    catalog = {x['id']: x for x in json.loads(CATALOG.read_bytes())}
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='property-nullsafe-null-warning-state-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    modules = [ROOT / x for x in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    environment = dict(os.environ, LC_ALL='C', TZ='UTC')
    environment.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    records = []
    for name, digest in EXPECTED.items():
        row = catalog[name]
        assert row['source_sha256'] == digest == hashlib.sha256(row['source'].encode()).hexdigest()
        directory = out / name
        directory.mkdir()
        source = directory / 'source.php'
        source.write_text(row['source'])
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
