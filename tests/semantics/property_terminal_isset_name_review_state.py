#!/usr/bin/env python3
"""Check terminal isset after deferred computed property-name evaluation."""
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
CATALOG = Path(__file__).with_name('property_terminal_isset_name_review_cases.json')
EXPECTED = {
    'property-terminal-isset-name-rebind': '59e75a02f97115345ca7fcab0d286d26dcba81b4e00f845ac047f5c3a2bfd990',
}
PREFIX = r'''
dec $test_property_isset_front(pstate, nat) : bool
def $test_property_isset_front(S, 0) = true
  -- if S.TODO = (PROPERTY_PREP (NExprFuncCall name (SEQUENCE eps) metadata) z) :: (ORIGIN_RETURN porigin?) :: (ISSET_RESULT false z) :: ptask*
def $test_property_isset_front(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("choose_dynamic_name")
  -- if S.TODO = (AT porigin (STMT (NStmtReturn expression metadata))) :: ptask*
def $test_property_isset_front(S, 2) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_BASE_NAME (BASE_VALUE (VARIABLE n_name* z_base)) z) :: (ORIGIN_RETURN porigin?) :: (ISSET_RESULT false z) :: ptask*
def $test_property_isset_front(S, n_stage) = false -- otherwise
dec $test_property_isset_seek(pstate, nat, nat) : pstate
def $test_property_isset_seek(S, n_stage, 0) = S
def $test_property_isset_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_property_isset_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $test_property_isset_seek(S, n_stage, n) = $test_property_isset_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_property_isset_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
'''


def lines(text):
    return [x.strip() for x in text.splitlines() if x.strip()]


def reach(state, start, stage):
    return [f'{state}_found = $test_property_isset_seek({start}, {stage}, 768)',
            rf'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$test_property_isset_front({state}, {stage})']


def checks(name, program, path):
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    values = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
              'S_initial.COMPLETION = BUDGET']
    values += reach('S_before', 'S_initial', 0)
    values += lines(r'''
S_before.TODO = (PROPERTY_PREP expression_name z) :: (ORIGIN_RETURN (porigin_property)) :: (ISSET_RESULT false z) :: (ORIGIN_RETURN (porigin_isset)) :: (ISSET_NEXT eps 1) :: ptask_tail*
S_before.ORIGIN = (porigin_property)
porigin_property = PORIGIN n_unit pcpath_property
porigin_isset = PORIGIN n_unit pcpath_isset
pcpath_property = pcpath_isset ++ [PCFIELD 0, PCINDEX 0]
$origin_node(S_before.SOURCES, porigin_property) = (NExprPropertyFetch expression_base expression_name metadata_property)
expression_property = NExprPropertyFetch expression_base expression_name metadata_property
$origin_node(S_before.SOURCES, porigin_isset) = (NExprIsset (SEQUENCE ([expression_property])) metadata_isset)
S_before.RESULT = VARIABLE ptbytes_base z_base
pbase_cv = BASE_VALUE (VARIABLE ptbytes_base z_base)
$property_cv_name_source(S_before) = ((ptbytes_base, ptbytes_replacement, ptbytes_key))
ptbytes_base = $ptascii("base") /\ ptbytes_replacement = $ptascii("replacement") /\ ptbytes_key = $ptascii("slot")
z = $runtime_line(S_before, eps, expression_property)
ptask_consumer* = [ORIGIN_RETURN (porigin_property), ISSET_RESULT false z, ORIGIN_RETURN (porigin_isset), ISSET_NEXT eps 1] ++ ptask_tail*
$property_cv_name_isset_tail(S_before, ptask_consumer*, z)
$property_cv_name_tail(S_before, ptask_consumer*, z)
~$property_cv_name_pair([PROPERTY_BASE_NAME pbase_cv z] ++ ptask_consumer*, pbase_cv, z)
$property_cv_name_isset_pair(S_before, [PROPERTY_BASE_NAME pbase_cv z] ++ ptask_consumer*, pbase_cv, z)
~$property_cv_name_isset_tail(S_before, ptask_consumer*, $(z + 1))
~$property_cv_name_isset_tail(S_before[.ORIGIN = (porigin_isset)], ptask_consumer*, z)
ptask_empty* = [ORIGIN_RETURN (porigin_property), ISSET_RESULT true z, ORIGIN_RETURN (porigin_isset), ISSET_NEXT eps 1] ++ ptask_tail*
~$property_cv_name_isset_tail(S_before, ptask_empty*, z)
~$property_cv_name_tail(S_before, ptask_empty*, z)
ptask_bad_parent* = [ORIGIN_RETURN (porigin_property), ISSET_RESULT false z, ORIGIN_RETURN (porigin_property), ISSET_NEXT eps 1] ++ ptask_tail*
~$property_cv_name_isset_tail(S_before, ptask_bad_parent*, z)
ptask_bad_next* = [ORIGIN_RETURN (porigin_property), ISSET_RESULT false z, ORIGIN_RETURN (porigin_isset), ISSET_NEXT eps 2] ++ ptask_tail*
~$property_cv_name_isset_tail(S_before, ptask_bad_next*, z)
$lookup(S_before.ENV, ptbytes_base) = (n_base)
$lookup(S_before.ENV, $ptascii("old")) = (n_alias)
$lookup(S_before.ENV, ptbytes_replacement) = (n_replacement)
S_before.STORE[n_base] = DEFINED (POBJECT n_old)
S_before.STORE[n_alias] = DEFINED (POBJECT n_old)
S_before.STORE[n_replacement] = DEFINED (POBJECT n_new)
n_old =/= n_new /\ n_base =/= n_alias
S_before.CURRENT = eps /\ S_before.FRAMES = eps /\ S_before.GLOBALTABLE = eps
$property_cv_name_entry(S_before)
$heap_owners($heap_graph(S_before), HOBJECT n_old) = 2
$heap_owners($heap_graph(S_before), HOBJECT n_new) = 1
S_carrier = S_before[.TODO = [$at_task($origin_child(S_before.ORIGIN, [PCFIELD 1]), EVAL expression_name), PROPERTY_BASE_NAME pbase_cv z] ++ ptask_consumer*][.BASE = BASE_VALUE (KNOWN PNULL)][.RESULT = KNOWN PNULL]
PhpStep: S_before ~> S_carrier
$task_nodes(PROPERTY_BASE_NAME pbase_cv z) = eps
$heap_graph(S_carrier) = $heap_graph(S_before)
S_carrier.ENV = S_before.ENV /\ S_carrier.STORE = S_before.STORE
S_pause = $drive(S_before, 0)
S_pause = S_before[.COMPLETION = BUDGET]
S_one = $drive(S_before, 1)
S_one = S_carrier[.COMPLETION = BUDGET]
$drive(S_pause[.COMPLETION = NORMAL], 1) = S_one
$call_descriptors_valid(S_one)
''')
    values += reach('S_helper', 'S_carrier', 1)
    values += lines(r'''
S_helper.CURRENT = (pcallcontext_helper)
pcallcontext_helper.ARGC = 0 /\ pcallcontext_helper.PARAMS = eps
pcallcontext_helper.CALLSITE = (PORIGIN n_unit (pcpath_property ++ [PCFIELD 1]))
S_helper.TODO = (AT porigin_return (STMT (NStmtReturn expression_key metadata_return))) :: ptask_return_tail*
S_helper.STORE[n_base] = DEFINED (POBJECT n_new)
S_helper.STORE[n_alias] = DEFINED (POBJECT n_old)
(n_base <- S_helper.REFCELLS) /\ (n_replacement <- S_helper.REFCELLS)
S_helper.FRAMES = pframe_main :: eps
pframe_main.CONTEXT = eps /\ pframe_main.LOCALS = eps
S_helper.EVENTS = S_before.EVENTS
$heap_owners($heap_graph(S_helper), HOBJECT n_old) = 1
$heap_owners($heap_graph(S_helper), HOBJECT n_new) = 2
S_main = $constant_frame_scope(S_helper, pframe_main, eps)
S_main.CURRENT = eps /\ S_main.FRAMES = eps
S_main.TODO = pframe_main.TODO
$call_tasks_valid(S_main, S_main.TODO)
S_marker_view = S_main[.ORIGIN = (porigin_property)]
$property_cv_name_count(S_marker_view.TODO, pbase_cv, z) = 1
~$property_cv_name_pair(S_marker_view.TODO, pbase_cv, z)
$property_cv_name_isset_pair(S_marker_view, S_marker_view.TODO, pbase_cv, z)
$property_cv_name_task_valid(S_marker_view, pbase_cv, z)
$call_task_valid(S_marker_view, PROPERTY_BASE_NAME pbase_cv z)
$call_descriptors_valid(S_helper)
''')
    values += reach('S_name', 'S_helper', 2)
    values += lines(r'''
S_name.TODO = (PROPERTY_BASE_NAME pbase_cv z) :: ptask_consumer*
S_name.ORIGIN = (porigin_property)
S_name.CURRENT = eps /\ S_name.FRAMES = eps /\ S_name.GLOBALTABLE = eps
S_name.RESULT = KNOWN pvalue_name
$string_bytes(pvalue_name) = (ptbytes_key)
S_name.STORE[n_base] = DEFINED (POBJECT n_new)
S_name.STORE[n_alias] = DEFINED (POBJECT n_old)
S_name.EVENTS = S_before.EVENTS
$property_cv_name_task_valid(S_name, pbase_cv, z)
$property_cv_name_read(S_name, pbase_cv, z)
S_duplicate = S_name[.TODO = S_name.TODO ++ S_name.TODO]
$property_cv_name_count(S_duplicate.TODO, pbase_cv, z) = 2
~$property_cv_name_task_valid(S_duplicate, pbase_cv, z)
S_empty = S_name[.TODO = (PROPERTY_BASE_NAME pbase_cv z) :: ptask_empty*]
~$property_cv_name_task_valid(S_empty, pbase_cv, z) /\ ~$property_cv_name_read(S_empty, pbase_cv, z)
S_bad_next = S_name[.TODO = (PROPERTY_BASE_NAME pbase_cv z) :: ptask_bad_next*]
~$property_cv_name_task_valid(S_bad_next, pbase_cv, z) /\ ~$property_cv_name_read(S_bad_next, pbase_cv, z)
S_ready = $property_cv_name_finish(S_name, pbase_cv, z)
PhpStep: S_name ~> S_ready
S_ready.TODO = ptask_consumer*
S_ready.BASE = BASE_PROPERTY (POBJECT n_new) ptbytes_key
S_ready.RESULT = KNOWN PNULL
S_ready.ENV = S_name.ENV /\ S_ready.STORE = S_name.STORE
$objectprops_record_at(S_ready.OBJECTPROPS, n_old) = (pobjectprops_old)
$objectprops_record_at(S_ready.OBJECTPROPS, n_new) = (pobjectprops_new)
$property_slot_at(pobjectprops_old.SLOTS, ptbytes_key) = (ppropertyslot_old)
$property_slot_at(pobjectprops_new.SLOTS, ptbytes_key) = (ppropertyslot_new)
ppropertyslot_old.STATE = PROP_VALUE (DIRECT (PINT 11))
ppropertyslot_new.STATE = PROP_VALUE (DIRECT PNULL)
$heap_owners($heap_graph(S_ready), HOBJECT n_old) = 1
$heap_owners($heap_graph(S_ready), HOBJECT n_new) = 3
S_terminal = S_ready[.TODO = [ISSET_RESULT false z, ORIGIN_RETURN (porigin_isset), ISSET_NEXT eps 1] ++ ptask_tail*][.ORIGIN = (porigin_property)]
PhpStep: S_ready ~> S_terminal
~$property_isset_pending(S_terminal)
S_false = $isset_base(S_terminal, S_terminal.BASE, false, z)[.TODO = [ORIGIN_RETURN (porigin_isset), ISSET_NEXT eps 1] ++ ptask_tail*][.BASE = BASE_VALUE (KNOWN PNULL)]
PhpStep: S_terminal ~> S_false
S_false.COMPLETION = NORMAL /\ S_false.RESULT = KNOWN (PBOOL false)
S_false.EVENTS = S_before.EVENTS
S_false.ENV = S_name.ENV /\ S_false.STORE = S_name.STORE
$heap_owners($heap_graph(S_false), HOBJECT n_old) = 1
$heap_owners($heap_graph(S_false), HOBJECT n_new) = 2
S_parent = S_false[.TODO = (ISSET_NEXT eps 1) :: ptask_tail*][.ORIGIN = (porigin_isset)]
PhpStep: S_false ~> S_parent
S_done = S_parent[.TODO = ptask_tail*]
PhpStep: S_parent ~> S_done
S_done.RESULT = KNOWN (PBOOL false)
S_done.EVENTS = S_before.EVENTS
''')
    return values


def run(out=None, process_seconds=180):
    catalog = {x['id']: x for x in json.loads(CATALOG.read_bytes())}
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='property-terminal-isset-name-state-', dir=ROOT / '.tools'))
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
