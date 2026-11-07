#!/usr/bin/env python3
"""Check current-frame argument count and Switch-only TMP evidence."""
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
CATALOG = Path(__file__).with_name('plain_switch_argc_review_cases.json')
EXPECTED = {
    'ctrl4-switch-argc-default': 'f5d42ba1ba9dccb78208b53aaef9e5c974a4efbeb1fcd796f0b974cc5ae7aad3',
    'ctrl4-switch-argc-surplus': 'eae54b792c5e5097109a3da8c5eff1c1556d8a61feb5ada13e2a0411a4a22b6f',
}
PREFIX = r'''
dec $test_ctrl4_front(pstate, nat) : bool
def $test_ctrl4_front(S, 0) = true
  -- if S.TODO = (STMT (NStmtSwitch expression phpType60 metadata)) :: ptask*
def $test_ctrl4_front(S, 1) = true
  -- if S.TODO = (SWITCH_START statement porigin) :: ptask*
def $test_ctrl4_front(S, n_stage) = false -- otherwise
dec $test_ctrl4_seek(pstate, nat, nat) : pstate
def $test_ctrl4_seek(S, n_stage, 0) = S
def $test_ctrl4_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_ctrl4_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $test_ctrl4_seek(S, n_stage, n) = $test_ctrl4_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ctrl4_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
'''


def lines(text):
    return [x.strip() for x in text.splitlines() if x.strip()]


def reach(state, start, stage):
    return [f'{state}_found = $test_ctrl4_seek({start}, {stage}, 768)',
            rf'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$test_ctrl4_front({state}, {stage})']


def checks(name, program, path):
    argc, formal = (0, 13) if name == 'ctrl4-switch-argc-default' else (2, 99)
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    values = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')', 'S_initial.COMPLETION = BUDGET']
    values += reach('S_entry', 'S_initial', 0)
    values += lines(r'''
S_entry.TODO = (STMT statement_switch) :: ptask_entry_tail*
statement_switch = NStmtSwitch expression_query phpType60 metadata_switch
expression_query = NExprFuncCall name (SEQUENCE eps) metadata_call
S_entry.ORIGIN = (porigin_switch)
porigin_switch = PORIGIN n_unit pcpath_switch
pcpath_query = pcpath_switch ++ [PCFIELD 0]
$source_unit(S_entry.SOURCES, n_unit) = (pcunit)
$code_at(S_entry.CODE, n_unit) = (pcode)
pcode.UNIT = pcunit.ID
$pparginfo_tmp_fields(pcode.EXPRESSIONS, pcode.NAMES, pcunit.OCCURRENCES, pcpath_query)
$pparginfo_tmp(pcode, pcunit, pcpath_query)
~$pparginfo_tmp(pcode[.UNIT = $(n_unit + 1)], pcunit, pcpath_query)
$code_name(pcode.NAMES, pcpath_query) = ((ptbytes, eps))
$ptlc(ptbytes) = $ptascii("func_num_args")
$tick_empty_declare_owner(pcunit.OCCURRENCES, pcpath_query) = (pcpath_owner)
S_entry.CURRENT = (pcallcontext)
$function_at(S_entry.FUNCTIONS, pcallcontext.FUNCTION) = (pfunction)
$origin_source(pfunction.ORIGIN) = PORIGIN n_unit pcpath_owner
|pcallcontext.PARAMS| = 1
|pfunction.SIGNATURE.PARAMETERS| = 1
$goto_plain_control(S_entry)
$tick_switch_numargs_site(S_entry, statement_switch, porigin_switch)
~$tick_switch_empty_family(statement_switch)
$tick_switch_new_site(S_entry, statement_switch, porigin_switch)
$switch_source_admitted(S_entry, statement_switch, porigin_switch)
$lookup(S_entry.ENV, $ptascii("formal")) = (n_formal)
$tick_source_plan(S_entry, n_unit) = (T_plan)
T_plan.DEPENDENCY = eps /\ T_plan.MARKERS = eps
T_seed = T_plan[.FREQUENCY = 0]
$tick_switch_numargs_root(T_seed, pcode.EXPRESSIONS, pcpath_query, expression_query)
$tick_subject_free(T_seed, pcode.EXPRESSIONS, pcpath_query, expression_query) = eps
$tick_switch_subject_free(T_seed, pcode.EXPRESSIONS, pcpath_query, expression_query) = (true)
$tick_switch_finish(T_seed[.LAST = true], true) = T_seed[.LAST = false]
S_denied = S_entry[.CURRENT = (pcallcontext[.CALLSITE = eps])]
~$switch_source_admitted(S_denied, statement_switch, porigin_switch)
PhpStep: S_denied ~> S_denied[.TODO = eps][.COMPLETION = UNSUPPORTED "argument-count switch control context"]
''')
    values += [f'pcallcontext.ARGC = {argc}', f'S_entry.STORE[n_formal] = DEFINED (PINT {formal})']
    values += reach('S_query', 'S_entry', 1)
    values += lines(r'''
S_query.TODO = (SWITCH_START statement_switch porigin_switch) :: ptask_query_tail*
S_query.CURRENT = S_entry.CURRENT /\ S_query.FRAMES = S_entry.FRAMES
$switch_source_admitted(S_query, statement_switch, porigin_switch)
$goto_plain_control(S_query)
$operand_nodes(S_query.RESULT) = eps
''')
    values += [f'S_query.RESULT = KNOWN (PINT {argc})', f'S_query.STORE[n_formal] = DEFINED (PINT {formal})',
               f'S_raw = S_query[.TODO = (SWITCH_SCAN statement_switch porigin_switch (KNOWN (PINT {argc})) 0) :: ptask_query_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]']
    values += lines(r'''
PhpStep: S_query ~> S_raw
$heap_graph(S_raw) = $heap_graph(S_query)
S_raw.CURRENT = S_query.CURRENT /\ S_raw.ENV = S_query.ENV /\ S_raw.STORE = S_query.STORE
S_pause = $drive(S_query, 0)
S_pause = S_query[.COMPLETION = BUDGET]
$call_descriptors_valid(S_pause)
$heap_valid($heap_graph(S_pause))
S_one = $drive(S_query, 1)
S_one = S_raw[.COMPLETION = BUDGET]
$drive(S_pause[.COMPLETION = NORMAL], 1) = S_one
$call_descriptors_valid(S_one)
$heap_valid($heap_graph(S_one))
''')
    return values


def run(out=None, process_seconds=180):
    catalog = {x['id']: x for x in json.loads(CATALOG.read_bytes())}
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='plain-switch-argc-state-', dir=ROOT / '.tools'))
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
