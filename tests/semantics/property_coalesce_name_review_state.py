#!/usr/bin/env python3
"""Check quiet coalesce after deferred computed property-name evaluation."""
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
CATALOG = Path(__file__).with_name('property_coalesce_name_review_cases.json')
EXPECTED = {
    'property-coalesce-name-rebind': '605e1034573f6a3ba2aa8d3acbca74480de390ef039aebddcea5522ab243a281',
}
PREFIX = r'''
dec $test_property_coalesce_front(pstate, nat) : bool
def $test_property_coalesce_front(S, 0) = true
  -- if S.TODO = (PROPERTY_PREP (NExprFuncCall name (SEQUENCE eps) metadata) z) :: (ORIGIN_RETURN porigin?) :: (COALESCE_QUIET expression z z_right) :: ptask*
def $test_property_coalesce_front(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("choose_dynamic_name")
  -- if S.TODO = (AT porigin (STMT (NStmtReturn expression metadata))) :: ptask*
def $test_property_coalesce_front(S, 2) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_BASE_NAME (BASE_VALUE (VARIABLE n_name* z_base)) z) :: (ORIGIN_RETURN porigin?) :: (COALESCE_QUIET expression z z_right) :: ptask*
def $test_property_coalesce_front(S, 3) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (VALUE_COPY z) :: ptask*
  -- if S.RESULT = KNOWN (PINT 7)
def $test_property_coalesce_front(S, n_stage) = false -- otherwise
dec $test_property_coalesce_seek(pstate, nat, nat) : pstate
def $test_property_coalesce_seek(S, n_stage, 0) = S
def $test_property_coalesce_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_property_coalesce_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $test_property_coalesce_seek(S, n_stage, n) = $test_property_coalesce_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_property_coalesce_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
'''


def lines(text):
    return [x.strip() for x in text.splitlines() if x.strip()]


def reach(state, start, stage, fuel=768):
    return [f'{state}_found = $test_property_coalesce_seek({start}, {stage}, {fuel})',
            rf'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$test_property_coalesce_front({state}, {stage})']


def checks(name, program, path):
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    values = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
              'S_initial.COMPLETION = BUDGET']
    values += reach('S_before', 'S_initial', 0)
    values += lines(r'''
S_before.TODO = (PROPERTY_PREP expression_name z) :: (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_QUIET expression_right z z_right) :: ptask_tail*
S_before.ORIGIN = (porigin_property)
porigin_property = PORIGIN n_unit pcpath_property
porigin_parent = PORIGIN n_unit pcpath_parent
pcpath_property = pcpath_parent ++ [PCFIELD 0]
$origin_node(S_before.SOURCES, porigin_property) = (NExprPropertyFetch expression_base expression_name metadata_property)
expression_property = NExprPropertyFetch expression_base expression_name metadata_property
$origin_node(S_before.SOURCES, porigin_parent) = (NExprBinaryOpCoalesce expression_property expression_right metadata_parent)
expression_right = NScalarInt (INTEGER i) metadata_right
i = 7
$code_at(S_before.CODE, n_unit) = (pcode)
$code_expression(pcode.EXPRESSIONS, pcpath_parent) = ((z_parent, b_parent))
$code_expression(pcode.EXPRESSIONS, pcpath_parent ++ [PCFIELD 1]) = ((z_code_right, b_right))
z = $runtime_line(S_before[.ORIGIN = (porigin_parent)], [PCFIELD 0], expression_property)
z_right = $runtime_line(S_before[.ORIGIN = (porigin_parent)], [PCFIELD 1], expression_right)
S_before.RESULT = VARIABLE ptbytes_base z_base
pbase_cv = BASE_VALUE (VARIABLE ptbytes_base z_base)
$property_cv_name_source(S_before) = ((ptbytes_base, ptbytes_replacement, ptbytes_key))
ptbytes_base = $ptascii("base") /\ ptbytes_replacement = $ptascii("replacement") /\ ptbytes_key = $ptascii("slot")
ptask_consumer* = [ORIGIN_RETURN (porigin_parent), COALESCE_QUIET expression_right z z_right] ++ ptask_tail*
$property_cv_name_coalesce_tail(S_before, ptask_consumer*, z)
$property_cv_name_tail(S_before, ptask_consumer*, z)
~$property_cv_name_isset_tail(S_before, ptask_consumer*, z)
~$property_cv_name_pair([PROPERTY_BASE_NAME pbase_cv z] ++ ptask_consumer*, pbase_cv, z)
$property_cv_name_coalesce_pair(S_before, [PROPERTY_BASE_NAME pbase_cv z] ++ ptask_consumer*, pbase_cv, z)
~$property_cv_name_coalesce_tail(S_before, ptask_consumer*, $(z + 1))
ptask_bad_right_line* = [ORIGIN_RETURN (porigin_parent), COALESCE_QUIET expression_right z $(z_right + 1)] ++ ptask_tail*
~$property_cv_name_coalesce_tail(S_before, ptask_bad_right_line*, z)
ptask_bad_right* = [ORIGIN_RETURN (porigin_parent), COALESCE_QUIET (NScalarInt (INTEGER 8) metadata_right) z z_right] ++ ptask_tail*
~$property_cv_name_coalesce_tail(S_before, ptask_bad_right*, z)
ptask_bad_parent* = [ORIGIN_RETURN (porigin_property), COALESCE_QUIET expression_right z z_right] ++ ptask_tail*
~$property_cv_name_coalesce_tail(S_before, ptask_bad_parent*, z)
~$property_cv_name_coalesce_tail(S_before[.ORIGIN = (porigin_parent)], ptask_consumer*, z)
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
$call_tasks_valid(S_main, S_main.TODO)
S_marker_view = S_main[.ORIGIN = (porigin_property)]
$property_cv_name_count(S_marker_view.TODO, pbase_cv, z) = 1
$property_cv_name_coalesce_pair(S_marker_view, S_marker_view.TODO, pbase_cv, z)
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
S_name.EVENTS = S_before.EVENTS
$property_cv_name_task_valid(S_name, pbase_cv, z)
$property_cv_name_read(S_name, pbase_cv, z)
S_duplicate = S_name[.TODO = S_name.TODO ++ S_name.TODO]
$property_cv_name_count(S_duplicate.TODO, pbase_cv, z) = 2
~$property_cv_name_task_valid(S_duplicate, pbase_cv, z)
S_bad_right = S_name[.TODO = (PROPERTY_BASE_NAME pbase_cv z) :: ptask_bad_right*]
~$property_cv_name_task_valid(S_bad_right, pbase_cv, z) /\ ~$property_cv_name_read(S_bad_right, pbase_cv, z)
S_ready = $property_cv_name_finish(S_name, pbase_cv, z)
PhpStep: S_name ~> S_ready
S_ready.TODO = ptask_consumer*
S_ready.BASE = BASE_PROPERTY (POBJECT n_new) ptbytes_key
S_ready.RESULT = KNOWN PNULL
$objectprops_record_at(S_ready.OBJECTPROPS, n_old) = (pobjectprops_old)
$objectprops_record_at(S_ready.OBJECTPROPS, n_new) = (pobjectprops_new)
$property_slot_at(pobjectprops_old.SLOTS, ptbytes_key) = (ppropertyslot_old)
$property_slot_at(pobjectprops_new.SLOTS, ptbytes_key) = (ppropertyslot_new)
ppropertyslot_old.STATE = PROP_VALUE (DIRECT (PINT 11))
ppropertyslot_new.STATE = PROP_VALUE (DIRECT PNULL)
$heap_owners($heap_graph(S_ready), HOBJECT n_old) = 1
$heap_owners($heap_graph(S_ready), HOBJECT n_new) = 3
S_quiet = S_ready[.TODO = (COALESCE_QUIET expression_right z z_right) :: ptask_tail*][.ORIGIN = (porigin_parent)]
PhpStep: S_ready ~> S_quiet
S_null = $quiet_base(S_quiet, S_quiet.BASE, z)
S_null.COMPLETION = NORMAL /\ S_null.RESULT = KNOWN PNULL
S_null.EVENTS = S_before.EVENTS
S_rhs = $coalesce_result($constant_quiet_capture(S_null)[.TODO = ptask_tail*][.BASE = BASE_VALUE (KNOWN PNULL)], expression_right, z, z_right)
PhpStep: S_quiet ~> S_rhs
S_rhs.TODO = [$at_task((PORIGIN n_unit (pcpath_parent ++ [PCFIELD 1])), EVAL expression_right), VALUE_COPY z_right] ++ ptask_tail*
S_rhs.RESULT = KNOWN PNULL /\ S_rhs.BASE = BASE_VALUE (KNOWN PNULL)
S_rhs.ENV = S_name.ENV /\ S_rhs.STORE = S_name.STORE
S_rhs.EVENTS = S_before.EVENTS
$heap_owners($heap_graph(S_rhs), HOBJECT n_old) = 1
$heap_owners($heap_graph(S_rhs), HOBJECT n_new) = 2
S_pause = $drive(S_quiet, 0)
S_pause = S_quiet[.COMPLETION = BUDGET]
S_one = $drive(S_quiet, 1)
S_one = S_rhs[.COMPLETION = BUDGET]
$drive(S_pause[.COMPLETION = NORMAL], 1) = S_one
$call_descriptors_valid(S_one)
''')
    values += reach('S_literal', 'S_rhs', 3, 16)
    values += lines(r'''
S_literal.TODO = (VALUE_COPY z_right) :: ptask_tail*
S_literal.RESULT = KNOWN (PINT 7)
S_literal.EVENTS = S_before.EVENTS
$heap_owners($heap_graph(S_literal), HOBJECT n_new) = 2
''')
    return values


def run(out=None, process_seconds=180):
    catalog = {x['id']: x for x in json.loads(CATALOG.read_bytes())}
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='property-coalesce-name-state-', dir=ROOT / '.tools'))
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
