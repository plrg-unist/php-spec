#!/usr/bin/env python3
"""Check silenced CV snapshots, reporting masks and Switch history."""
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
CATALOG = Path(__file__).with_name('plain_switch_silenced_cv_review_cases.json')
EXPECTED = {
    'ctrl5-switch-silenced-defined': 'd322faf96a1b39cb77b21589bb64e3f1d17d6a42ed2de06d345ddcccd3399a2c',
    'ctrl5-switch-silenced-missing': '870f7d4eebd1beb3c9c5913130b7aae207563f2f574560915bde9d93d03095c5',
}
PREFIX = r'''
dec $test_ctrl5_front(pstate, nat) : bool
def $test_ctrl5_front(S, 0) = true
  -- if S.TODO = (STMT (NStmtSwitch expression phpType60 metadata)) :: ptask*
def $test_ctrl5_front(S, 1) = true
  -- if S.TODO = (SILENCE_END porigin) :: ptask*
def $test_ctrl5_front(S, 2) = true
  -- if S.TODO = (SWITCH_COMPARE statement porigin poperand 0 z) :: ptask*
def $test_ctrl5_front(S, n_stage) = false -- otherwise
dec $test_ctrl5_seek(pstate, nat, nat) : pstate
def $test_ctrl5_seek(S, n_stage, 0) = S
def $test_ctrl5_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_ctrl5_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $test_ctrl5_seek(S, n_stage, n) = $test_ctrl5_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ctrl5_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
'''


def lines(text):
    return [x.strip() for x in text.splitlines() if x.strip()]


def reach(state, start, stage):
    return [f'{state}_found = $test_ctrl5_seek({start}, {stage}, 768)',
            rf'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$test_ctrl5_front({state}, {stage})']


def checks(name, program, path):
    defined = name == 'ctrl5-switch-silenced-defined'
    snapshot, current = ('(PINT 0)', 2) if defined else ('PNULL', 1)
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    values = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
              'S_initial.COMPLETION = BUDGET']
    values += reach('S_entry', 'S_initial', 0)
    values += lines(r'''
S_entry.TODO = (STMT statement_switch) :: ptask_entry_tail*
statement_switch = NStmtSwitch expression_silenced phpType60 metadata_switch
expression_silenced = NExprErrorSuppress (NExprVariable (BYTES text_var) metadata_var) metadata_silenced
S_entry.ORIGIN = (porigin_switch)
porigin_switch = PORIGIN n_unit pcpath_switch
pcpath_silenced = pcpath_switch ++ [PCFIELD 0]
pcpath_var = pcpath_silenced ++ [PCFIELD 0]
porigin_silenced = PORIGIN n_unit pcpath_silenced
n_name* = $base64(text_var)
$source_unit(S_entry.SOURCES, n_unit) = (pcunit)
$code_at(S_entry.CODE, n_unit) = (pcode)
pcode.UNIT = pcunit.ID
$code_expression(pcode.EXPRESSIONS, pcpath_silenced) = ((z_outer, false))
$code_expression(pcode.EXPRESSIONS, pcpath_var) = ((z_var, false))
$tick_switch_silenced_fields(pcode.EXPRESSIONS, pcunit.OCCURRENCES, pcpath_silenced, expression_silenced)
$tick_empty_declare_owner(pcunit.OCCURRENCES, pcpath_silenced) = (pcpath_owner)
S_entry.CURRENT = (pcallcontext)
$function_at(S_entry.FUNCTIONS, pcallcontext.FUNCTION) = (pfunction)
$origin_source(pfunction.ORIGIN) = PORIGIN n_unit pcpath_owner
$goto_plain_control(S_entry)
$tick_switch_silenced_site(S_entry, statement_switch, porigin_switch)
$tick_switch_new_site(S_entry, statement_switch, porigin_switch)
$switch_source_admitted(S_entry, statement_switch, porigin_switch)
S_entry.REPORTING = 30719 /\ S_entry.SILENCES = eps
S_entry.ERRORHANDLER.CALLBACK = eps
$tick_source_plan(S_entry, n_unit) = (T_plan)
T_plan.DEPENDENCY = eps /\ T_plan.MARKERS = eps
T_seed = T_plan[.FREQUENCY = 0]
$tick_switch_silenced_root(T_seed, pcode.EXPRESSIONS, pcpath_silenced, expression_silenced)
~$tick_switch_silenced_root(T_seed[.FREQUENCY = 1], pcode.EXPRESSIONS, pcpath_silenced, expression_silenced)
$tick_subject_free(T_seed, pcode.EXPRESSIONS, pcpath_silenced, expression_silenced) = eps
$tick_switch_subject_free(T_seed, pcode.EXPRESSIONS, pcpath_silenced, expression_silenced) = (true)
$tick_switch_finish(T_seed[.LAST = true], true) = T_seed[.LAST = false]
S_handler = S_entry[.ERRORHANDLER = {CALLBACK (PSTRING pfunction.NAME), LEVELS 2}]
$error_handler_eligible(S_handler, 2)
$tick_switch_silenced_site(S_handler, statement_switch, porigin_switch)
$tick_switch_new_site(S_handler, statement_switch, porigin_switch)
~$switch_source_admitted(S_handler, statement_switch, porigin_switch)
PhpStep: S_handler ~> S_handler[.TODO = eps][.COMPLETION = UNSUPPORTED "silenced-variable switch control context"]
S_denied = S_entry[.CURRENT = (pcallcontext[.CALLSITE = eps])]
~$switch_source_admitted(S_denied, statement_switch, porigin_switch)
PhpStep: S_denied ~> S_denied[.TODO = eps][.COMPLETION = UNSUPPORTED "silenced-variable switch control context"]
''')
    values += reach('S_end', 'S_entry', 1)
    values += lines(r'''
S_end.TODO = (SILENCE_END porigin_silenced) :: ptask_end_tail*
S_end.ORIGIN = (porigin_silenced)
S_end.RESULT = VARIABLE n_name* z_var
S_end.CURRENT = S_entry.CURRENT /\ S_end.FRAMES = S_entry.FRAMES
S_end.REPORTING = 4437
S_end.SILENCES = (SILENCE porigin_silenced 30719) :: eps
S_end.EVENTS = S_entry.EVENTS
$silence_origin_valid(S_end, porigin_silenced)
$call_task_valid(S_end, SILENCE_END porigin_silenced)
S_read = $silence_read(S_end, porigin_silenced)
S_read.COMPLETION = NORMAL
S_read.REPORTING = 4437 /\ S_read.SILENCES = S_end.SILENCES
S_read.ENV = S_end.ENV /\ S_read.STORE = S_end.STORE
S_read.EVENTS = S_end.EVENTS
S_restored = $silence_finish(S_read[.TODO = ptask_end_tail*], porigin_silenced)
PhpStep: S_end ~> S_restored
S_restored.REPORTING = 30719 /\ S_restored.SILENCES = eps
$operand_nodes(S_restored.RESULT) = eps
$heap_graph(S_restored) = $heap_graph(S_end)
S_pause = $drive(S_end, 0)
S_pause = S_end[.COMPLETION = BUDGET]
$call_descriptors_valid(S_pause)
$heap_valid($heap_graph(S_pause))
S_one = $drive(S_end, 1)
S_one = S_restored[.COMPLETION = BUDGET]
$drive(S_pause[.COMPLETION = NORMAL], 1) = S_one
$call_descriptors_valid(S_one)
$heap_valid($heap_graph(S_one))
''')
    values += [f'S_read.RESULT = KNOWN {snapshot}', f'S_restored.RESULT = KNOWN {snapshot}']
    if defined:
        values += ['$lookup(S_end.ENV, n_name*) = (n_before)',
                   'S_end.STORE[n_before] = DEFINED (PINT 0)']
    else:
        values += ['$lookup(S_end.ENV, n_name*) = eps']
    values += reach('S_compare', 'S_restored', 2)
    values += [f'S_compare.TODO = (SWITCH_COMPARE statement_switch porigin_switch (KNOWN {snapshot}) 0 z_compare) :: ptask_compare_tail*',
               f'S_compare.RESULT = KNOWN (PINT {current})']
    values += lines(r'''
S_compare.REPORTING = 30719 /\ S_compare.SILENCES = eps
S_compare.CURRENT = S_entry.CURRENT /\ S_compare.FRAMES = S_entry.FRAMES
$lookup(S_compare.ENV, n_name*) = (n_current)
$switch_compare_valid(S_compare, statement_switch, porigin_switch, 0, z_compare)
$switch_source_admitted(S_compare, statement_switch, porigin_switch)
$tick_switch_silenced_site(S_compare, statement_switch, porigin_switch)
$operand_nodes(S_compare.RESULT) = eps
''')
    values += [f'S_compare.STORE[n_current] = DEFINED (PINT {current})']
    return values


def run(out=None, process_seconds=180):
    catalog = {x['id']: x for x in json.loads(CATALOG.read_bytes())}
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='plain-switch-silenced-cv-state-', dir=ROOT / '.tools'))
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
