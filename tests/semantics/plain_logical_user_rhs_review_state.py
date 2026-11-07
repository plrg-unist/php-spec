#!/usr/bin/env python3
"""Check lazy function-RHS frames, scalar defaults and caller restoration."""
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
CATALOG = Path(__file__).with_name('plain_logical_user_rhs_review_cases.json')
EXPECTED = {
    'ctrl7-logical-user-rhs-default': '0c5b7d398931c1c536ba6bf652e67b692a6d6cf02c6b4ce49268b6b225263ecd',
    'ctrl7-logical-user-rhs-surplus': 'bb8f756e99cb9be0b65c2aacb2eaa471ced21e01135aaaa6f2d2a7142fcab08d',
}
PREFIX = r'''
dec $test_ctrl7_front(pstate, nat, bool) : bool
def $test_ctrl7_front(S, 0, b_taken) = true
  -- if S.TODO = (AT porigin (EVAL expression)) :: ptask*
  -- if $tick_argc_short_operands(expression) = ((b_taken, expression_left, expression_right))
def $test_ctrl7_front(S, 1, b_taken) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("right_ctrl7")
  -- if S.TODO = (AT porigin (EVAL (NExprFuncCall name (SEQUENCE eps) metadata))) :: ptask*
def $test_ctrl7_front(S, 2, b_taken) = true
  -- if S.TODO = (TRUTH_RESULT false z) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (expression)
  -- if $tick_argc_short_operands(expression) = ((b_taken, expression_left, expression_right))
def $test_ctrl7_front(S, n_stage, b_taken) = false -- otherwise
dec $test_ctrl7_seek(pstate, nat, bool, nat) : pstate
def $test_ctrl7_seek(S, n_stage, b_taken, 0) = S
def $test_ctrl7_seek(S, n_stage, b_taken, n) = S
  -- if $(n > 0)
  -- if $test_ctrl7_front(S, n_stage, b_taken) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $test_ctrl7_seek(S, n_stage, b_taken, n) = $test_ctrl7_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, b_taken, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ctrl7_front(S, n_stage, b_taken)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
'''


def lines(text):
    return [x.strip() for x in text.splitlines() if x.strip()]


def reach(state, start, stage, taken):
    return [f'{state}_found = $test_ctrl7_seek({start}, {stage}, {taken}, 768)',
            rf'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$test_ctrl7_front({state}, {stage}, {taken})']


def checks(name, program, path):
    argc = 0 if name == 'ctrl7-logical-user-rhs-default' else 2
    taken = 'true' if argc == 0 else 'false'
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    values = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
              'S_initial.COMPLETION = BUDGET']
    values += reach('S_before', 'S_initial', 0, taken)
    values += lines(r"""
S_before.TODO = (AT porigin_root (EVAL expression_root)) :: ptask_before_tail*
$tick_argc_short_operands(expression_root) = ((b_taken, expression_left, expression_right))
porigin_root = PORIGIN n_unit pcpath_root
$source_unit(S_before.SOURCES, n_unit) = (pcunit)
$code_at(S_before.CODE, n_unit) = (pcode)
$tick_argc_short_user_rhs(pcode.EXPRESSIONS, pcode.NAMES, pcunit.OCCURRENCES, pcpath_root ++ [PCFIELD 1], expression_right) = ((pcpath_helper, pcpath_query))
$function_at(S_before.FUNCTIONS, PORIGIN n_unit pcpath_helper) = (pfunction_helper)
S_before.FUNCTIONS = pfunction_helper :: pfunction_tail*
pfunction_helper.BODY = pcpath_helper ++ [PCFIELD 5]
pfunction_helper.CODE.UNIT = pcunit.ID
~pfunction_helper.SIGNATURE.BYREF /\ pfunction_helper.SIGNATURE.RETURNS = eps
$pparginfo_tmp(pfunction_helper.CODE, pcunit, pcpath_query)
$callable_at(S_before.CALLABLES, $ptlc(pfunction_helper.NAME)) = (pfunction_helper.ORIGIN)
$call_selected_valid(S_before, pfunction_helper.ORIGIN, (PORIGIN n_unit (pcpath_root ++ [PCFIELD 1])))
S_before.CURRENT = (pcallcontext_outer)
pcallcontext_outer.NAME = $ptascii("outer_ctrl7")
$lookup(S_before.ENV, $ptascii("formal")) = (n_outer)
S_before.STORE[n_outer] = DEFINED (PINT 99)
$tick_argc_short_site(S_before, porigin_root)
$tick_argc_user_binding(S_before, porigin_root, pcpath_helper, pcpath_query)
$tick_argc_short_admitted(S_before, porigin_root)
S_body_bad = S_before[.FUNCTIONS = pfunction_helper[.BODY = eps] :: pfunction_tail*]
$tick_argc_short_site(S_body_bad, porigin_root)
~$tick_argc_user_binding(S_body_bad, porigin_root, pcpath_helper, pcpath_query)
~$tick_argc_short_admitted(S_body_bad, porigin_root)
S_code_bad = S_before[.FUNCTIONS = pfunction_helper[.CODE.UNIT = $(n_unit + 1)] :: pfunction_tail*]
$tick_argc_short_site(S_code_bad, porigin_root)
~$tick_argc_user_binding(S_code_bad, porigin_root, pcpath_helper, pcpath_query)
S_unbound = S_before[.CALLABLES = eps]
$tick_argc_short_site(S_unbound, porigin_root)
~$tick_argc_user_binding(S_unbound, porigin_root, pcpath_helper, pcpath_query)
S_blocked = S_before[.OUTPUTBLOCKED = true]
$tick_argc_short_site(S_blocked, porigin_root)
~$tick_argc_short_admitted(S_blocked, porigin_root)
S_blocked_entered = $enter_constant_task(S_blocked, porigin_root, EVAL expression_root, ptask_before_tail*)
PhpStep: S_blocked ~> S_blocked_entered[.TODO = eps][.COMPLETION = UNSUPPORTED "argument-count logical control context"]
S_eval = $tick_enter(S_before, porigin_root, EVAL expression_root, ptask_before_tail*)
S_eval.ORIGIN = (porigin_root)
z_right = $runtime_line(S_eval, [PCFIELD 1], expression_right)
""")
    values += [f'pcallcontext_outer.ARGC = {argc}', f'b_taken = {taken}']
    values += reach('S_helper', 'S_eval', 1, taken)
    values += lines(r"""
S_helper.TODO = (AT porigin_query (EVAL expression_query)) :: ptask_helper_tail*
porigin_query = PORIGIN n_unit pcpath_query
S_helper.CURRENT = (pcallcontext_helper)
pcallcontext_helper.FUNCTION = pfunction_helper.ORIGIN
pcallcontext_helper.TARGET = pfunction_helper.ORIGIN
pcallcontext_helper.ARGC = 0 /\ |pcallcontext_helper.PARAMS| = 1
pcallcontext_helper.CALLSITE = (PORIGIN n_unit (pcpath_root ++ [PCFIELD 1]))
pcallcontext_helper.INSTANCE = eps /\ pcallcontext_helper.RECEIVER = eps
$lookup(S_helper.ENV, $ptascii("formal")) = (n_helper)
S_helper.STORE[n_helper] = DEFINED (PINT 13)
n_helper =/= n_outer
S_helper.FRAMES = pframe_outer :: pframe_tail*
pframe_outer.CONTEXT = (pcallcontext_outer)
pframe_outer.LOCALS = (psymboltable_outer)
$lookup(psymboltable_outer.ENV, $ptascii("formal")) = (n_outer)
S_helper.STORE[n_outer] = DEFINED (PINT 99)
(TRUTH_RESULT false z_right) <- pframe_outer.TODO
$heap_owners($heap_graph(S_helper), HCELL n_helper) = 1
$heap_owners($heap_graph(S_helper), HCELL n_outer) = 1
S_outer_view = $constant_frame_scope(S_helper, pframe_outer, pframe_tail*)
S_outer_view.CURRENT = (pcallcontext_outer)
S_outer_view.ENV = psymboltable_outer.ENV
$call_tasks_valid(S_outer_view, pframe_outer.TODO)
$call_task_valid(S_outer_view[.ORIGIN = (porigin_root)], TRUTH_RESULT false z_right)
S_inside = $tick_enter(S_helper, porigin_query, EVAL expression_query, ptask_helper_tail*)
PhpStep: S_helper ~> S_inside
$heap_graph(S_inside) = $heap_graph(S_helper)
S_inside.CURRENT = S_helper.CURRENT /\ S_inside.FRAMES = S_helper.FRAMES
S_pause = $drive(S_helper, 0)
S_pause = S_helper[.COMPLETION = BUDGET]
$call_descriptors_valid(S_pause)
$heap_valid($heap_graph(S_pause))
S_one = $drive(S_helper, 1)
S_one = S_inside[.COMPLETION = BUDGET]
$drive(S_pause[.COMPLETION = NORMAL], 1) = S_one
$call_descriptors_valid(S_one)
$heap_valid($heap_graph(S_one))
""")
    values += reach('S_truth', 'S_inside', 2, taken)
    values += lines(r"""
S_truth.TODO = (TRUTH_RESULT false z_right) :: ptask_truth_tail*
S_truth.ORIGIN = (porigin_root)
S_truth.CURRENT = (pcallcontext_outer)
S_truth.FRAMES = S_before.FRAMES
S_truth.RESULT = KNOWN (PINT 0)
$lookup(S_truth.ENV, $ptascii("formal")) = (n_outer)
S_truth.STORE[n_outer] = DEFINED (PINT 99)
$heap_owners($heap_graph(S_truth), HCELL n_helper) = 0
$heap_owners($heap_graph(S_truth), HCELL n_outer) = 1
$call_task_valid(S_truth, TRUTH_RESULT false z_right)
$tick_argc_short_rhs_admitted(S_truth, porigin_root)
S_bool = $boolean_result(S_truth[.TODO = ptask_truth_tail*], false, z_right)
PhpStep: S_truth ~> S_bool
S_bool.RESULT = KNOWN (PBOOL false)
S_bool.ENV = S_truth.ENV /\ S_bool.STORE = S_truth.STORE
""")
    return values


def run(out=None, process_seconds=180):
    catalog = {x['id']: x for x in json.loads(CATALOG.read_bytes())}
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='plain-logical-user-rhs-state-', dir=ROOT / '.tools'))
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
