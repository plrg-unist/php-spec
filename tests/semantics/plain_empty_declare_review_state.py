#!/usr/bin/env python3
"""Check empty zero-tick body lines and scoped plain-function execution."""
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
CATALOG = Path(__file__).with_name('plain_empty_declare_review_cases.json')
EXPECTED = {
    'ctrl2-empty-declare-brace': '3856feb73ada32192284c5a7b674dcd45608dff245c57055fd11f4095f48e1d5',
    'ctrl2-empty-declare-colon-loop': '241162f3343140db6f7eb6b93455a8deb5d89ac174c19397feb1fd8fa90e9aef',
}
PREFIX = r'''
dec $test_ctrl2_front(pstate) : bool
def $test_ctrl2_front(S) = true
  -- if S.TODO = (STMT (NStmtDeclare phpType48 (SEQUENCE eps) metadata)) :: ptask*
def $test_ctrl2_front(S) = false -- otherwise
dec $test_ctrl2_seek(pstate, nat) : pstate
def $test_ctrl2_seek(S, 0) = S
def $test_ctrl2_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_ctrl2_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $test_ctrl2_seek(S, n) = $test_ctrl2_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ctrl2_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
'''


def lines(text):
    return [x.strip() for x in text.splitlines() if x.strip()]


def checks(name, program, path):
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    header_line, opener = (4, 5) if name == 'ctrl2-empty-declare-brace' else (7, 8)
    values = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
              'S_initial.COMPLETION = BUDGET']
    values += lines(r'''
S_found = $test_ctrl2_seek(S_initial, 768)
S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET
S = S_found[.COMPLETION = NORMAL]
$test_ctrl2_front(S)
S.TODO = (STMT statement_declare) :: ptask_tail*
statement_declare = NStmtDeclare phpType48 (SEQUENCE eps) metadata
S.ORIGIN = (PORIGIN n_unit pcpath)
$origin_accepts(S.SOURCES, PORIGIN n_unit pcpath, STMT statement_declare)
$tick_empty_zero_declare(statement_declare)
$source_unit(S.SOURCES, n_unit) = (pcunit)
$tick_empty_declare_owner(pcunit.OCCURRENCES, pcpath) = (pcpath_owner)
S.CURRENT = (pcallcontext)
$function_at(S.FUNCTIONS, pcallcontext.FUNCTION) = (pfunction)
$origin_source(pfunction.ORIGIN) = PORIGIN n_unit pcpath_owner
~pfunction.SIGNATURE.BYREF /\ ~$function_generator(S, pfunction)
$goto_plain_control(S)
$tick_empty_declare_runtime(S, statement_declare)
$declare_body_admitted(S, statement_declare)
$unknown_declare_valid(S, statement_declare)
S.TICKENTRIES = eps /\ S.ACTIVEFIBER = eps
$tick_empty_declare_owner(eps, pcpath) = eps
$tick_empty_declare_line(eps) = eps
$tick_source_plan(S, n_unit) = (T_plan)
T_plan.DEPENDENCY = eps /\ T_plan.MARKERS = eps
''')
    values += [f'$source_line(metadata) = {header_line}',
               f'$ppbodyline(metadata) = ({opener})',
               f'$tick_empty_declare_line(metadata) = ({opener})',
               f'T_seed = T_plan[.FREQUENCY = 0][.LINE = {header_line}][.LAST = false]',
               '$tick_empty_declare_owner(T_seed.NODES, pcpath) = (pcpath_owner)',
               f'$tick_statement_body(T_seed, pfunction.CODE.EXPRESSIONS, pcpath, statement_declare, false) = T_seed[.LINE = {opener}]',
               f'$tick_statement_body(T_seed[.LAST = true], pfunction.CODE.EXPRESSIONS, pcpath, statement_declare, false) = T_seed[.LAST = true][.LINE = {opener}]']
    values += lines(r'''
S_raw = S[.TODO = ptask_tail*]
PhpStep: S ~> S_raw
S_raw.STORE = S.STORE /\ S_raw.ENV = S.ENV /\ S_raw.FRAMES = S.FRAMES
S_raw.EVENTS = S.EVENTS /\ S_raw.RESULT = S.RESULT /\ S_raw.BASE = S.BASE
S_denied = S[.CURRENT = (pcallcontext[.CALLSITE = eps])]
~$declare_body_admitted(S_denied, statement_declare)
~$unknown_declare_valid(S_denied, statement_declare)
PhpStep: S_denied ~> S_denied[.TODO = eps][.COMPLETION = UNSUPPORTED "empty zero-tick declare control context"]
S_pause = $drive(S, 0)
S_pause = S[.COMPLETION = BUDGET]
$call_descriptors_valid(S_pause)
$heap_valid($heap_graph(S_pause))
S_one = $drive(S, 1)
S_one = S_raw[.COMPLETION = BUDGET]
$drive(S_pause[.COMPLETION = NORMAL], 1) = S_one
$call_descriptors_valid(S_one)
$heap_valid($heap_graph(S_one))
''')
    if name == 'ctrl2-empty-declare-colon-loop':
        values += lines(r'''
$lookup(S.ENV, $ptascii("count")) = (n_count)
S.STORE[n_count] = DEFINED (PINT 1)
$lookup(S.ENV, $ptascii("total")) = (n_total)
S.STORE[n_total] = DEFINED (PINT 0)
$(|pcpath| >= 2)
n_parent = $(|pcpath| - 2)
pcpath_loop = pcpath[0:n_parent]
$origin_node(S.SOURCES, PORIGIN n_unit pcpath_loop) = (statement_loop)
$goto_loop_statement(statement_loop)
$goto_saved(S.TODO, PORIGIN n_unit pcpath_loop) = GOTOTASKS ptask_saved*
ptask_saved* = (LOOP_NEXT statement_loop (PORIGIN n_unit pcpath_loop)) :: ptask_outer*
$goto_saved(S_one.TODO, PORIGIN n_unit pcpath_loop) = GOTOTASKS ptask_saved*
''')
    else:
        assert name == 'ctrl2-empty-declare-brace'
    return values


def run(out=None, process_seconds=180):
    catalog = {x['id']: x for x in json.loads(CATALOG.read_bytes())}
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='plain-empty-declare-state-', dir=ROOT / '.tools'))
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
