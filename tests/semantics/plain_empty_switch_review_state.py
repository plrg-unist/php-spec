#!/usr/bin/env python3
"""Check empty-case switch continuation and delayed scalar CV reads."""
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
CATALOG = Path(__file__).with_name('plain_empty_switch_review_cases.json')
EXPECTED = {
    'ctrl3-empty-case-delayed-cv': '9358194f3a0a7ecbbeb8274285f6ae00e00dc4c152ecc3b76f5775b2c7d1a4a6',
    'ctrl3-empty-default-continue': 'd0733915248f3ceccb1accdffcc624d3ddc1e5740c6ad1726a05d5870af59e5b',
}
PREFIX = r'''
dec $test_ctrl3_front(pstate, nat) : bool
def $test_ctrl3_front(S, 0) = true
  -- if S.TODO = (STMT (NStmtSwitch expression phpType60 metadata)) :: ptask*
def $test_ctrl3_front(S, 1) = true
  -- if S.TODO = (SWITCH_COMPARE statement porigin poperand 0 z) :: ptask*
def $test_ctrl3_front(S, 2) = true
  -- if S.TODO = (STMT (NStmtContinue phpType5 metadata)) :: ptask*
def $test_ctrl3_front(S, n_stage) = false -- otherwise
dec $test_ctrl3_seek(pstate, nat, nat) : pstate
def $test_ctrl3_seek(S, n_stage, 0) = S
def $test_ctrl3_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_ctrl3_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $test_ctrl3_seek(S, n_stage, n) = $test_ctrl3_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ctrl3_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
'''


def lines(text):
    return [x.strip() for x in text.splitlines() if x.strip()]


def reach(state, start, stage):
    return [f'{state}_found = $test_ctrl3_seek({start}, {stage}, 1024)',
            rf'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$test_ctrl3_front({state}, {stage})']


def source(state, opener):
    return [f'$tick_switch_new_site({state}, statement_switch, porigin_switch)',
            f'$switch_source_admitted({state}, statement_switch, porigin_switch)',
            f'$switch_site({state}, statement_switch, porigin_switch)',
            f'$goto_plain_control({state})',
            f'{state}.CURRENT = (pcallcontext)',
            f'$function_at({state}.FUNCTIONS, pcallcontext.FUNCTION) = (pfunction)',
            f'$source_unit({state}.SOURCES, n_unit) = (pcunit)',
            '$tick_empty_declare_owner(pcunit.OCCURRENCES, pcpath_switch) = (pcpath_owner)',
            '$origin_source(pfunction.ORIGIN) = PORIGIN n_unit pcpath_owner',
            '$tick_contains_nodes($pcfield_phpType23(SEQUENCE $pcprogram(pcunit.AST), eps))',
            '$switch_case_at($switch_cases(statement_switch), 0) = (NStmtCase phpType5_empty (SEQUENCE eps) metadata_case)',
            '$ppcase_semicolon(metadata_case) = (false)',
            f'$ppbodyline(metadata_case) = ({opener})',
            '$source_line(metadata_case) =/= $source_end_line(metadata_case)',
            f'$tick_source_plan({state}, n_unit) = (T_plan)',
            'T_plan.DEPENDENCY = eps /\\ T_plan.MARKERS = eps',
            'pcpath_body = pcpath_switch ++ [PCFIELD 1, PCINDEX 0, PCFIELD 1]',
            'T_seed = T_plan[.FREQUENCY = 0][.LAST = false]',
            f'$tick_switch_body(T_seed, pfunction.CODE.EXPRESSIONS, pcpath_body, eps, metadata_case) = T_seed[.LINE = {opener}]',
            f'$tick_switch_body(T_seed[.LAST = true], pfunction.CODE.EXPRESSIONS, pcpath_body, eps, metadata_case) = T_seed[.LAST = true][.LINE = {opener}]']


def budget(state, raw):
    return [f'{state}_pause = $drive({state}, 0)',
            f'{state}_pause = {state}[.COMPLETION = BUDGET]',
            f'$call_descriptors_valid({state}_pause)',
            f'$heap_valid($heap_graph({state}_pause))',
            f'{state}_one = $drive({state}, 1)',
            f'{state}_one = {raw}[.COMPLETION = BUDGET]',
            f'$drive({state}_pause[.COMPLETION = NORMAL], 1) = {state}_one',
            f'$call_descriptors_valid({state}_one)',
            f'$heap_valid($heap_graph({state}_one))']


def cv_checks():
    values = reach('S_entry', 'S_initial', 0) + lines(r'''
S_entry.TODO = (STMT statement_switch) :: ptask_entry_tail*
S_entry.ORIGIN = (porigin_switch)
porigin_switch = PORIGIN n_unit pcpath_switch
$lookup(S_entry.ENV, $ptascii("subject")) = (n_subject)
S_entry.STORE[n_subject] = DEFINED (PINT 0)
$lookup(S_entry.ENV, $ptascii("side")) = (n_side)
S_entry.STORE[n_side] = DEFINED (PINT 0)
''')
    values += source('S_entry', 9)
    values += lines(r'''
S_denied = S_entry[.CURRENT = (pcallcontext[.CALLSITE = eps])]
~$switch_source_admitted(S_denied, statement_switch, porigin_switch)
PhpStep: S_denied ~> S_denied[.TODO = eps][.COMPLETION = UNSUPPORTED "empty multiline switch control context"]
''')
    values += reach('S_compare', 'S_entry', 1) + lines(r'''
S_compare.TODO = (SWITCH_COMPARE statement_switch porigin_switch (VARIABLE n_subject_name* z_subject) 0 z_compare) :: ptask_compare_tail*
S_compare.CURRENT = S_entry.CURRENT /\ S_compare.FRAMES = S_entry.FRAMES
n_subject_name* = $ptascii("subject")
$origin_node(S_compare.SOURCES, PORIGIN n_unit (pcpath_switch ++ [PCFIELD 0])) = (NExprVariable phpType32_subject metadata_subject)
$cv_name(phpType32_subject) = (n_subject_name*)
$variable_line(phpType32_subject, metadata_subject) = z_subject
$lookup(S_compare.ENV, $ptascii("subject")) = (n_subject)
S_compare.STORE[n_subject] = DEFINED (PINT 2)
S_compare.STORE[n_side] = DEFINED (PINT 0)
S_compare.RESULT = KNOWN (PINT 2)
$task_nodes(SWITCH_COMPARE statement_switch porigin_switch (VARIABLE n_subject_name* z_subject) 0 z_compare) = eps
$goto_plain_control(S_compare)
$switch_site(S_compare, statement_switch, porigin_switch)
~$goto_plain_control(S_compare[.REFCELLS = S_compare.REFCELLS ++ [n_subject]])
H_compare = $heap_graph(S_compare)
$heap_owners(H_compare, HCELL n_subject) = 1
S_subject = $resolve_at($hold_task_inputs(S_compare), VARIABLE n_subject_name* z_subject, z_compare)
S_case = $resolve_at(S_subject, S_compare.RESULT, z_compare)
S_raw = $switch_compare_result(S_compare, S_case, statement_switch, porigin_switch, VARIABLE n_subject_name* z_subject, 0, z_compare, PINT 2, PINT 2)
S_raw.COMPLETION = NORMAL
PhpStep: S_compare ~> S_raw
S_raw.STORE = S_compare.STORE /\ S_raw.ENV = S_compare.ENV /\ S_raw.FRAMES = S_compare.FRAMES
S_raw.TODO = (AT (PORIGIN n_unit (pcpath_switch ++ [PCFIELD 1, PCINDEX 1, PCFIELD 1, PCINDEX 0])) (STMT statement_echo)) :: ptask_raw*
statement_echo = NStmtEcho phpType25 metadata_echo
$goto_saved(S_raw.TODO, porigin_switch) = GOTOTASKS ((SWITCH_NEXT statement_switch porigin_switch (VARIABLE n_subject_name* z_subject)) :: ptask_after_switch*)
$heap_owners($heap_graph(S_raw), HCELL n_subject) = 1
S_raw.STORE[n_side] = DEFINED (PINT 0)
''')
    return values + budget('S_compare', 'S_raw')


def default_checks():
    values = reach('S_continue', 'S_initial', 2) + lines(r'''
S_continue.TODO = (STMT (NStmtContinue phpType5_depth metadata_continue)) :: ptask_continue_tail*
$jump_depth(phpType5_depth) = 2
S_continue.ORIGIN = (porigin_continue)
porigin_continue = PORIGIN n_unit pcpath_continue
$(|pcpath_continue| >= 4)
n_switch = $(|pcpath_continue| - 4)
pcpath_switch = pcpath_continue[0:n_switch]
porigin_switch = PORIGIN n_unit pcpath_switch
$origin_node(S_continue.SOURCES, porigin_switch) = (statement_switch)
$goto_saved(S_continue.TODO, porigin_switch) = GOTOTASKS ((SWITCH_NEXT statement_switch porigin_switch (KNOWN (PINT 7))) :: ptask_switch_tail*)
$lookup(S_continue.ENV, $ptascii("count")) = (n_count)
S_continue.STORE[n_count] = DEFINED (PINT 1)
$lookup(S_continue.ENV, $ptascii("tests")) = (n_tests)
S_continue.STORE[n_tests] = DEFINED (PINT 1)
''')
    values += source('S_continue', 10)
    values += lines(r'''
$(|pcpath_switch| >= 2)
n_loop = $(|pcpath_switch| - 2)
pcpath_loop = pcpath_switch[0:n_loop]
$origin_node(S_continue.SOURCES, PORIGIN n_unit pcpath_loop) = (statement_loop)
$goto_loop_statement(statement_loop)
$goto_saved(S_continue.TODO, PORIGIN n_unit pcpath_loop) = GOTOTASKS ptask_loop*
ptask_loop* = (LOOP_NEXT statement_loop (PORIGIN n_unit pcpath_loop)) :: ptask_loop_tail*
S_raw = $jump_loop(S_continue[.TODO = ptask_continue_tail*], porigin_continue, 2, 2, true)
S_raw.COMPLETION = NORMAL
PhpStep: S_continue ~> S_raw
S_raw.TODO = ptask_loop*
$goto_saved(S_raw.TODO, porigin_switch) = GOTOMISSING
S_raw.STORE = S_continue.STORE /\ S_raw.ENV = S_continue.ENV /\ S_raw.FRAMES = S_continue.FRAMES
''')
    return values + budget('S_continue', 'S_raw')


def checks(name, program, path):
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    values = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'ctrl3-empty-case-delayed-cv':
        return values + cv_checks()
    assert name == 'ctrl3-empty-default-continue'
    return values + default_checks()


def run(out=None, process_seconds=180):
    catalog = {x['id']: x for x in json.loads(CATALOG.read_bytes())}
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='plain-empty-switch-state-', dir=ROOT / '.tools'))
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
