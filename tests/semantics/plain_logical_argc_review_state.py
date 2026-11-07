#!/usr/bin/env python3
"""Check argument-count lazy Boolean control and source history."""
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
CATALOG = Path(__file__).with_name('plain_logical_argc_review_cases.json')
EXPECTED = {
    'ctrl6-logical-argc-default': 'b26788a8720afbee27628beabea57b5929be2c9e966b781879e751f45d4f95b3',
    'ctrl6-logical-argc-surplus': '22ed689eaa3ed6065dac37e7830ed3c1ec6c9bb2c37334320f7657ce53b089a4',
}
PREFIX = r'''
dec $test_ctrl6_front(pstate, nat) : bool
def $test_ctrl6_front(S, 0) = true
  -- if S.TODO = (AT porigin (EVAL (NExprBinaryOpBooleanAnd expression_left expression_right metadata))) :: ptask*
def $test_ctrl6_front(S, 1) = true
  -- if S.TODO = (SHORT_RESULT false expression z_left z_right) :: ptask*
def $test_ctrl6_front(S, 2) = true
  -- if S.TODO = (SHORT_RESULT true expression z_left z_right) :: ptask*
def $test_ctrl6_front(S, 3) = true
  -- if S.TODO = (TRUTH_RESULT false z) :: ptask*
def $test_ctrl6_front(S, n_stage) = false -- otherwise
dec $test_ctrl6_seek(pstate, nat, nat) : pstate
def $test_ctrl6_seek(S, n_stage, 0) = S
def $test_ctrl6_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_ctrl6_front(S, n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $test_ctrl6_seek(S, n_stage, n) = $test_ctrl6_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ctrl6_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
'''


def lines(text):
    return [x.strip() for x in text.splitlines() if x.strip()]


def reach(state, start, stage):
    return [f'{state}_found = $test_ctrl6_seek({start}, {stage}, 768)',
            rf'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$test_ctrl6_front({state}, {stage})']


def checks(name, program, path):
    argc = 0 if name == 'ctrl6-logical-argc-default' else 2
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    values = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
              'S_initial.COMPLETION = BUDGET']
    values += reach('S_before', 'S_initial', 0)
    values += lines(r"""
S_before.TODO = (AT porigin_and (EVAL expression_and)) :: ptask_before_tail*
expression_and = NExprBinaryOpBooleanAnd expression_left expression_right metadata_and
$tick_argc_short_operands(expression_and) = ((false, expression_left, expression_right))
porigin_and = PORIGIN n_unit pcpath_and
$source_unit(S_before.SOURCES, n_unit) = (pcunit)
$code_at(S_before.CODE, n_unit) = (pcode)
pcode.UNIT = pcunit.ID
$code_expression(pcode.EXPRESSIONS, pcpath_and) = ((z_root, false))
$pparginfo_tmp(pcode, pcunit, pcpath_and ++ [PCFIELD 0])
$tick_argc_short_fields(pcode.EXPRESSIONS, pcode.NAMES, pcunit.OCCURRENCES, pcpath_and, expression_and)
$tick_empty_declare_owner(pcunit.OCCURRENCES, pcpath_and) = (pcpath_owner)
S_before.CURRENT = (pcallcontext)
$function_at(S_before.FUNCTIONS, pcallcontext.FUNCTION) = (pfunction)
$origin_source(pfunction.ORIGIN) = PORIGIN n_unit pcpath_owner
|pcallcontext.PARAMS| = 1 /\ |pfunction.SIGNATURE.PARAMETERS| = 1
$lookup(S_before.ENV, $ptascii("formal")) = (n_formal)
S_before.STORE[n_formal] = DEFINED (PINT 99)
$tick_source_plan(S_before, n_unit) = (T_plan)
T_plan.DEPENDENCY = eps /\ T_plan.MARKERS = eps
T_seed = T_plan[.FREQUENCY = 0]
$tick_argc_short_root(T_seed, pcode.EXPRESSIONS, pcpath_and, expression_and)
~$tick_argc_short_root(T_seed[.FREQUENCY = 1], pcode.EXPRESSIONS, pcpath_and, expression_and)
$tick_switch_unknown(pcode.NAMES, pcpath_and, expression_and)
$tick_expression_body(T_seed, pcode.EXPRESSIONS, pcpath_and, expression_and) = $tick_expression_raw(T_seed, pcode.EXPRESSIONS, pcpath_and, expression_and)
~$tick_argc_short_rhs(expression_left)
$tick_argc_short_site(S_before, porigin_and)
$tick_argc_short_admitted(S_before, porigin_and)
S_eval = $tick_enter(S_before, porigin_and, EVAL expression_and, ptask_before_tail*)
PhpStep: S_before ~> S_eval
S_eval.ORIGIN = (porigin_and)
$call_task_valid(S_eval, EVAL expression_and)
S_handler = S_before[.ERRORHANDLER = {CALLBACK (PSTRING pfunction.NAME), LEVELS 2}]
$tick_argc_short_site(S_handler, porigin_and)
~$tick_argc_short_admitted(S_handler, porigin_and)
S_handler_entered = $enter_constant_task(S_handler, porigin_and, EVAL expression_and, ptask_before_tail*)
PhpStep: S_handler ~> S_handler_entered[.TODO = eps][.COMPLETION = UNSUPPORTED "argument-count logical control context"]
~$call_task_valid(S_eval[.ERRORHANDLER = S_handler.ERRORHANDLER], EVAL expression_and)
S_denied = S_eval[.CURRENT = (pcallcontext[.CALLSITE = eps])]
~$call_task_valid(S_denied, EVAL expression_and)
""")
    values += [f'pcallcontext.ARGC = {argc}']
    values += reach('S_and', 'S_eval', 1)
    values += lines(r"""
S_and.TODO = (SHORT_RESULT false expression_right z_left z_right) :: ptask_and_tail*
S_and.ORIGIN = (porigin_and)
S_and.CURRENT = S_before.CURRENT /\ S_and.FRAMES = S_before.FRAMES
$call_task_valid(S_and, SHORT_RESULT false expression_right z_left z_right)
~$call_task_valid(S_and, SHORT_RESULT true expression_right z_left z_right)
~$call_task_valid(S_and, SHORT_RESULT false expression_left z_left z_right)
~$call_task_valid(S_and, SHORT_RESULT false expression_right z_left $(z_right + 1))
$lookup(S_and.ENV, $ptascii("andRight")) = (n_and)
S_and.STORE[n_and] = DEFINED (PINT 0)
S_and_raw = $short_result(S_and[.TODO = ptask_and_tail*], false, expression_right, z_left, z_right)
PhpStep: S_and ~> S_and_raw
$heap_graph(S_and_raw) = $heap_graph(S_and)
S_pause = $drive(S_and, 0)
S_pause = S_and[.COMPLETION = BUDGET]
$call_descriptors_valid(S_pause)
$heap_valid($heap_graph(S_pause))
S_one = $drive(S_and, 1)
S_one = S_and_raw[.COMPLETION = BUDGET]
$drive(S_pause[.COMPLETION = NORMAL], 1) = S_one
$call_descriptors_valid(S_one)
$heap_valid($heap_graph(S_one))
""")
    values += [f'S_and.RESULT = KNOWN (PINT {argc})']
    if argc == 0:
        values += ['S_and_raw.TODO = ptask_and_tail*',
                   'S_and_raw.RESULT = KNOWN (PBOOL false)']
    else:
        values += ['S_and_raw.TODO = [$at_task($origin_child((porigin_and), [PCFIELD 1]), EVAL expression_right), TRUTH_RESULT false z_right] ++ ptask_and_tail*',
                   'S_and_raw.RESULT = KNOWN PNULL']
    values += reach('S_or', 'S_and_raw', 2)
    values += lines(r"""
S_or.TODO = (SHORT_RESULT true expression_or_right z_or_left z_or_right) :: ptask_or_tail*
S_or.ORIGIN = (porigin_or)
$origin_node(S_or.SOURCES, porigin_or) = (expression_or)
expression_or = NExprBinaryOpBooleanOr expression_or_left expression_or_right metadata_or
$tick_argc_short_site(S_or, porigin_or)
$call_task_valid(S_or, SHORT_RESULT true expression_or_right z_or_left z_or_right)
~$call_task_valid(S_or, SHORT_RESULT false expression_or_right z_or_left z_or_right)
$lookup(S_or.ENV, $ptascii("andRight")) = (n_and)
$lookup(S_or.ENV, $ptascii("and")) = (n_result)
$lookup(S_or.ENV, $ptascii("orRight")) = (n_or)
S_or.STORE[n_or] = DEFINED (PINT 0)
S_or_raw = $short_result(S_or[.TODO = ptask_or_tail*], true, expression_or_right, z_or_left, z_or_right)
PhpStep: S_or ~> S_or_raw
""")
    values += [f'S_or.RESULT = KNOWN (PINT {argc})',
               f'S_or.STORE[n_and] = DEFINED (PINT {0 if argc == 0 else 1})',
               'S_or.STORE[n_result] = DEFINED (PBOOL ' + ('false' if argc == 0 else 'true') + ')']
    if argc == 0:
        values += ['S_or_raw.TODO = [$at_task($origin_child((porigin_or), [PCFIELD 1]), EVAL expression_or_right), TRUTH_RESULT false z_or_right] ++ ptask_or_tail*',
                   'S_or_raw.RESULT = KNOWN PNULL']
    else:
        values += ['S_or_raw.TODO = ptask_or_tail*',
                   'S_or_raw.RESULT = KNOWN (PBOOL true)']
    values += reach('S_truth', 'S_or_raw' if argc == 0 else 'S_and_raw', 3)
    values += lines(r"""
S_truth.TODO = (TRUTH_RESULT false z_truth) :: ptask_truth_tail*
S_truth.ORIGIN = (porigin_truth)
$tick_argc_short_site(S_truth, porigin_truth)
$call_task_valid(S_truth, TRUTH_RESULT false z_truth)
~$call_task_valid(S_truth, TRUTH_RESULT true z_truth)
~$call_task_valid(S_truth, TRUTH_RESULT false $(z_truth + 1))
S_bool = $boolean_result(S_truth[.TODO = ptask_truth_tail*], false, z_truth)
PhpStep: S_truth ~> S_bool
S_bool.RESULT = KNOWN (PBOOL true)
S_bool.ENV = S_truth.ENV /\ S_bool.STORE = S_truth.STORE
""")
    values += [f'S_truth.RESULT = KNOWN (PINT {2 if argc == 0 else 1})']
    return values


def run(out=None, process_seconds=180):
    catalog = {x['id']: x for x in json.loads(CATALOG.read_bytes())}
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='plain-logical-argc-state-', dir=ROOT / '.tools'))
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
