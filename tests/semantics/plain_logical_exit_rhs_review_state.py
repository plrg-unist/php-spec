#!/usr/bin/env python3
"""Check lazy scalar exit selection, frame unwind and budget continuations."""
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
CATALOG = Path(__file__).with_name('plain_logical_exit_rhs_review_cases.json')
EXPECTED = {
    'ctrl8-logical-exit-skip': '79711d84d8e76b1cb99cac6ad2242f38c9db93f31da8cab03b8e230a85037afe',
    'ctrl8-logical-exit-take': '96dcdaafc4c3ae4661591519986e6fadb7409383576515f17035b3768cb24ffe',
}
PREFIX = r'''
dec $test_ctrl8_front(pstate, nat) : bool
def $test_ctrl8_front(S, 0) = true
  -- if S.TODO = (AT porigin (EVAL (NExprBinaryOpBooleanAnd expression_left expression_right metadata))) :: ptask*
def $test_ctrl8_front(S, 1) = true
  -- if S.TODO = (SHORT_RESULT false expression z_left z_right) :: ptask*
def $test_ctrl8_front(S, 2) = true
  -- if S.TODO = (EXIT_INVOKE pexitcall) :: ptask*
def $test_ctrl8_front(S, n_stage) = false -- otherwise
dec $test_ctrl8_seek(pstate, nat, nat) : pstate
def $test_ctrl8_seek(S, n_stage, 0) = S
def $test_ctrl8_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_ctrl8_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $test_ctrl8_seek(S, n_stage, n) = $test_ctrl8_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ctrl8_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
'''


def lines(text):
    return [x.strip() for x in text.splitlines() if x.strip()]


def reach(state, start, stage):
    return [f'{state}_found = $test_ctrl8_seek({start}, {stage}, 768)',
            rf'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$test_ctrl8_front({state}, {stage})']


def checks(name, program, path):
    argc = 0 if name == 'ctrl8-logical-exit-skip' else 2
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    values = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
              'S_initial.COMPLETION = BUDGET']
    values += reach('S_before', 'S_initial', 0)
    values += lines(r'''
S_before.TODO = (AT porigin_root (EVAL expression_root)) :: ptask_before_tail*
expression_root = NExprBinaryOpBooleanAnd expression_left expression_right metadata_root
expression_right = NExprExit (NScalarInt (INTEGER 13) metadata_value) metadata_exit
porigin_root = PORIGIN n_unit pcpath_root
porigin_exit = PORIGIN n_unit (pcpath_root ++ [PCFIELD 1])
$source_unit(S_before.SOURCES, n_unit) = (pcunit)
$code_at(S_before.CODE, n_unit) = (pcode)
pcode.UNIT = pcunit.ID
$pparginfo_tmp(pcode, pcunit, pcpath_root ++ [PCFIELD 0])
$exit_root(pcunit.OCCURRENCES, pcode.NAMES, pcpath_root ++ [PCFIELD 1])
$code_name(pcode.NAMES, pcpath_root ++ [PCFIELD 1]) = (($ptascii("exit"), eps))
$code_expression(pcode.EXPRESSIONS, pcpath_root ++ [PCFIELD 1, PCFIELD 0]) = ((z_value, b_value))
$code_call_init(pcode.EXPRESSIONS, pcpath_root ++ [PCFIELD 1]) = eps
$tick_argc_short_exit_rhs(pcode.EXPRESSIONS, pcode.NAMES, pcunit.OCCURRENCES, pcpath_root ++ [PCFIELD 1], expression_right)
~$tick_argc_short_exit_rhs((CODECALL_INIT (pcpath_root ++ [PCFIELD 1]) 7) :: pcode.EXPRESSIONS, pcode.NAMES, pcunit.OCCURRENCES, pcpath_root ++ [PCFIELD 1], expression_right)
$tick_argc_short_fields(pcode.EXPRESSIONS, pcode.NAMES, pcunit.OCCURRENCES, pcpath_root, expression_root)
S_before.CURRENT = (pcallcontext)
pcallcontext.NAME = $ptascii("exit_ctrl8")
|pcallcontext.PARAMS| = 1
$lookup(S_before.ENV, $ptascii("formal")) = (n_formal)
$lookup(S_before.ENV, $ptascii("answer")) = (n_answer)
S_before.STORE[n_formal] = DEFINED (PINT 99)
S_before.STORE[n_answer] = DEFINED (PINT 41)
$tick_argc_short_site(S_before, porigin_root)
$tick_argc_exit_context(S_before)
$tick_argc_short_admitted(S_before, porigin_root)
S_future = S_before[.EXITSTATUS = 13][.ORIGIN = (porigin_root)]
$tick_argc_short_admitted(S_future, porigin_root)
$call_task_valid(S_future, EVAL expression_root)
$call_task_valid(S_future, AT porigin_root (EVAL expression_root))
S_blocked = S_before[.OUTPUTBLOCKED = true]
$tick_argc_short_site(S_blocked, porigin_root)
~$tick_argc_short_admitted(S_blocked, porigin_root)
S_blocked_entered = $enter_constant_task(S_blocked, porigin_root, EVAL expression_root, ptask_before_tail*)
PhpStep: S_blocked ~> S_blocked_entered[.TODO = eps][.COMPLETION = UNSUPPORTED "argument-count logical control context"]
S_shutdown = S_before[.SHUTDOWN.PHASE = SHUTDOWN_DONE]
$tick_argc_short_site(S_shutdown, porigin_root)
~$tick_argc_exit_context(S_shutdown)
~$tick_argc_short_admitted(S_shutdown, porigin_root)
S_handler = S_before[.ERRORHANDLER = {CALLBACK (PSTRING pcallcontext.NAME), LEVELS 2}]
$tick_argc_short_site(S_handler, porigin_root)
~$tick_argc_short_admitted(S_handler, porigin_root)
S_eval = $tick_enter(S_before, porigin_root, EVAL expression_root, ptask_before_tail*)
PhpStep: S_before ~> S_eval
S_eval.ORIGIN = (porigin_root)
''')
    values += [f'pcallcontext.ARGC = {argc}']
    values += reach('S_short', 'S_eval', 1)
    values += lines(r'''
S_short.TODO = (SHORT_RESULT false expression_right z_left z_right) :: ptask_short_tail*
S_short.ORIGIN = (porigin_root)
S_short.CURRENT = S_before.CURRENT /\ S_short.FRAMES = S_before.FRAMES
S_short.STORE[n_formal] = DEFINED (PINT 99)
S_short.STORE[n_answer] = DEFINED (PINT 41)
$call_task_valid(S_short, SHORT_RESULT false expression_right z_left z_right)
~$call_task_valid(S_short, SHORT_RESULT true expression_right z_left z_right)
~$call_task_valid(S_short, SHORT_RESULT false expression_right z_left $(z_right + 1))
S_branch = $short_result(S_short[.TODO = ptask_short_tail*], false, expression_right, z_left, z_right)
PhpStep: S_short ~> S_branch
S_branch.EXITSTATUS = 0
S_branch.STORE = S_short.STORE /\ S_branch.ENV = S_short.ENV
''')
    values += [f'S_short.RESULT = KNOWN (PINT {argc})']
    if argc == 0:
        values += lines(r'''
S_branch.TODO = ptask_short_tail*
S_branch.RESULT = KNOWN (PBOOL false)
S_pause = $drive(S_short, 0)
S_pause = S_short[.COMPLETION = BUDGET]
$call_descriptors_valid(S_pause)
$heap_valid($heap_graph(S_pause))
S_one = $drive(S_short, 1)
S_one = S_branch[.COMPLETION = BUDGET]
$drive(S_pause[.COMPLETION = NORMAL], 1) = S_one
S_one.EXITSTATUS = 0 /\ S_one.STORE[n_answer] = DEFINED (PINT 41)
''')
    else:
        values += lines(r'''
S_branch.TODO = [$at_task((porigin_exit), EVAL expression_right), TRUTH_RESULT false z_right] ++ ptask_short_tail*
S_branch.RESULT = KNOWN PNULL
''')
        values += reach('S_invoke', 'S_branch', 2)
        values += lines(r'''
S_invoke.TODO = (EXIT_INVOKE pexitcall) :: ptask_invoke_tail*
pexitcall.SITE = porigin_exit /\ pexitcall.KIND = INTRINSIC_EXIT
pexitcall.INDEX = 1 /\ ~pexitcall.NAMED /\ pexitcall.OWNER = eps
pexitcall.SENT = [KNOWN (PINT 13)]
$exit_selected_valid(S_invoke, pexitcall)
$exit_invoke_valid(S_invoke, pexitcall)
$task_nodes(EXIT_INVOKE pexitcall) = eps
S_invoke.EXITSTATUS = 0 /\ S_invoke.STORE[n_answer] = DEFINED (PINT 41)
S_invoke.FRAMES = pframe_main :: eps
pframe_main.CONTEXT = eps
S_raw = $exit_receive(S_invoke[.TODO = ptask_invoke_tail*], pexitcall)
PhpStep: S_invoke ~> S_raw
S_raw.COMPLETION = EXITED 13 /\ S_raw.EXITSTATUS = 13
S_raw.TODO = eps /\ S_raw.ORIGIN = eps
S_raw.RESULT = KNOWN PNULL /\ S_raw.BASE = BASE_VALUE (KNOWN PNULL)
S_raw.TRACE = eps /\ S_raw.ERRORORIGIN = eps
S_raw.CURRENT = S_invoke.CURRENT /\ S_raw.FRAMES = S_invoke.FRAMES
S_raw.STORE[n_answer] = DEFINED (PINT 41)
S_raw.EVENTS = S_invoke.EVENTS
S_unwind = $exit_start_unwind(S_raw, 13)
S_unwind.TODO = [EXIT_UNWIND 13] /\ S_unwind.COMPLETION = NORMAL
S_unwind.CURRENT = S_invoke.CURRENT /\ S_unwind.FRAMES = S_invoke.FRAMES
$exit_unwind_valid(S_unwind, 13)
S_pause = $drive(S_invoke, 0)
S_pause = S_invoke[.COMPLETION = BUDGET]
$call_descriptors_valid(S_pause)
$heap_valid($heap_graph(S_pause))
S_one = $drive(S_invoke, 1)
S_one = S_unwind[.COMPLETION = BUDGET]
$drive(S_pause[.COMPLETION = NORMAL], 1) = S_one
$call_descriptors_valid(S_one)
$heap_valid($heap_graph(S_one))
S_done = $drive(S_one[.COMPLETION = NORMAL], 16)
S_done.COMPLETION = EXITED 13 /\ S_done.EXITSTATUS = 13
S_done.TODO = eps /\ S_done.FRAMES = eps /\ S_done.CURRENT = eps
S_done.ORIGIN = eps /\ S_done.TRACE = eps /\ S_done.ERRORORIGIN = eps
S_done.EVENTS = S_invoke.EVENTS
$heap_owners($heap_graph(S_done), HCELL n_formal) = 0
$heap_owners($heap_graph(S_done), HCELL n_answer) = 0
''')
    return values


def run(out=None, process_seconds=180):
    catalog = {x['id']: x for x in json.loads(CATALOG.read_bytes())}
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='plain-logical-exit-rhs-state-', dir=ROOT / '.tools'))
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
