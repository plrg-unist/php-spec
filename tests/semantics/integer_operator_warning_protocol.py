#!/usr/bin/env python3
"""Genuine source frontiers for integer conversion warnings and borrowed cells."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import integer_operator_warnings as sources

ROOT = sources.ROOT
CASES = ('live-right-0', 'reference-rebind-0', 'reference-rebind-3', 'leading-frozen', 'nan')
HELPERS = r'''
dec $integer_frontier(pstate, nat) : bool
def $integer_frontier(S, 0) = ($integer_operator_plan(S) =/= eps)
def $integer_frontier(S, 1) = true
  -- if S.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 0) :: ptask_tail*
def $integer_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 1
def $integer_frontier(S, 3) = true
  -- if S.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 1) :: ptask_tail*
def $integer_frontier(S, 4) = true
  -- if S.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT i)) :: ptask_tail*
def $integer_frontier(S, 5) = true
  -- if S.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i) pintegerconversion 0) :: ptask_tail*
def $integer_frontier(S, n) = false -- otherwise
dec $integer_seek(pstate, nat, nat) : pstate
def $integer_seek(S, n_stage, n) = S -- if $integer_frontier(S, n_stage)
def $integer_seek(S, n_stage, n) = S
  -- if ~$integer_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $integer_seek(S, n_stage, 0) = S
  -- if ~$integer_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $integer_seek(S, n_stage, n) = $integer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$integer_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
dec $integer_outputs(pevent*) : ptbytes
dec $integer_is_output(pevent) : bool
def $integer_outputs(eps) = eps
def $integer_outputs((OUTPUT n*) :: pevent_tail*) = n* ++ $integer_outputs(pevent_tail*)
def $integer_outputs(pevent :: pevent_tail*) = $integer_outputs(pevent_tail*) -- if ~$integer_is_output(pevent)
def $integer_is_output(OUTPUT ptbytes) = true
def $integer_is_output(pevent) = false -- otherwise
'''


def conditions(name, program, path, stdout):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_entry = $integer_seek(S_initial, 0, 1500)[.COMPLETION = NORMAL]',
        '$integer_frontier(S_entry, 0)', '$call_descriptors_valid(S_entry)',
        '$integer_operator_plan(S_entry) = (pintegeroperation)',
        '$integer_operation_valid(S_entry, pintegeroperation)',
        '~$integer_operation_valid(S_entry, pintegeroperation[.LINE = $(pintegeroperation.LINE + 1)])',
        '~$integer_operation_valid(S_entry, pintegeroperation[.OP = ADD])',
        '~$integer_operation_valid(S_entry, pintegeroperation[.LEFT = $ptascii("missing")])',
        '~$integer_operation_valid(S_entry[.ORIGIN = eps], pintegeroperation)',
        'n_invalid = |S_entry.STORE|',
        '~$integer_operation_valid(S_entry, pintegeroperation[.LEFTPOINTER = INTEGER_CELL n_invalid])',
        'PhpStep: S_entry ~> S_begin',
        'S_begin.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation INTEGER_LEFT) :: ptask_tail*',
        'S_begin.STORE = S_entry.STORE', 'S_begin.ALLOCATIONS = S_entry.ALLOCATIONS',
        '$task_nodes(INTEGER_OPERATOR_CONVERT pintegeroperation INTEGER_LEFT) = eps',
        '$call_descriptors_valid(S_begin)',
        'S_capture = $integer_seek(S_begin, 1, 1500)[.COMPLETION = NORMAL]',
        '$integer_frontier(S_capture, 1)',
        'S_capture.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 0) :: ptask_tail*',
        '$integer_conversion(pintegerconversion.INPUT) = (pintegerconversion)',
        '$integer_warning_valid(S_capture, pintegeroperation, INTEGER_LEFT, pintegerconversion, 0)',
        '~$integer_warning_valid(S_capture, pintegeroperation, INTEGER_LEFT, pintegerconversion[.VALUE = $(pintegerconversion.VALUE + 1)], 0)',
        '~$integer_warning_valid(S_capture, pintegeroperation, INTEGER_LEFT, pintegerconversion, $(|pintegerconversion.NOTICES| + 1))',
        'PhpStep: S_capture ~> S_dispatch',
        '$integer_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 1',
        '$error_call_valid(S_dispatch, perrorcall)', '$call_descriptors_valid(S_dispatch)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 512])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 0])',
        'S_return = $integer_seek(S_dispatch, 3, 1500)[.COMPLETION = NORMAL]',
        '$integer_frontier(S_return, 3)', '$call_descriptors_valid(S_return)',
        '$integer_warning_valid(S_return, pintegeroperation, INTEGER_LEFT, pintegerconversion, 1)',
        'S_right = $integer_seek(S_return, 4, 1500)[.COMPLETION = NORMAL]',
        '$integer_frontier(S_right, 4)',
        'S_right.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT pintegerconversion.VALUE)) :: ptask_tail*',
        '$call_descriptors_valid(S_right)',
        'S_done = $drive_steps(S_right, 1500)', 'S_done.COMPLETION = NORMAL',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        'S_done.FRAMES = eps', 'S_done.HELD = eps', '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_capture, 1) = $gc_transition_owners(S_capture, $destruction_transition_owners(S_capture, $sensitive_trace_freeze($source_exception_transition(S_capture, $throwable_transition(S_capture, S_dispatch)))))[.COMPLETION = BUDGET]',
        '$drive_steps(S_begin, 1500) = S_done',
        '$drive_steps(S_capture, 1500) = S_done',
    ]
    if name.startswith('reference-rebind'):
        checks += [
            '$lookup(S_entry.ENV, $ptascii("b")) = (n_old)',
            '$lookup(S_return.ENV, $ptascii("b")) = (n_new)', 'n_old =/= n_new',
            '$lookup(S_return.ENV, $ptascii("old")) = (n_old)',
            'S_return.STORE[n_old] = DEFINED (PINT 1)', 'S_return.STORE[n_new] = DEFINED (PINT 3)',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_old) = 2',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_old) = 1',
            '$task_nodes(INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 1) = eps',
        ]
        if name.endswith('-0'):
            checks += ['pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("b"))',
                       '$integer_pointer_value(S_return, pintegeroperation.RIGHTPOINTER) = (PINT 3)']
        else:
            checks += ['pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_old',
                       '$integer_pointer_value(S_return, pintegeroperation.RIGHTPOINTER) = (PINT 1)',
                       '$integer_pointer_value(S_return[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)], pintegeroperation.RIGHTPOINTER) = eps']
    if name == 'leading-frozen':
        checks += ['$string_bytes(pintegerconversion.INPUT) = ($ptascii("12.5tail"))',
                   'pintegerconversion.VALUE = 12', '|pintegerconversion.NOTICES| = 2',
                   '$integer_pointer_value(S_return, pintegeroperation.LEFTPOINTER) = (pvalue_changed)',
                   '$string_bytes(pvalue_changed) = ($ptascii("99.75tail"))',
                   'pintegerconversion.NOTICES[1] = (8192, $ptascii("Implicit conversion from float-string ") ++ [34] ++ $ptascii("12.5tail") ++ [34] ++ $ptascii(" to int loses precision"))']
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', choices=CASES)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = (args.case,) if args.case else CASES
    out = args.output or Path(tempfile.mkdtemp(prefix='integer-operator-protocol-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    print(out, flush=True)
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = {name: frontend.request({'op': 'parse', 'source': base64.b64encode(sources.CASES[name]).decode()}) for name in selected}
        assert all(row['accepted'] for row in parsed.values())
    finally:
        frontend.close()
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        programs = {name: adapter.request({'op': 'check', 'ast': row['ast'], 'fixture': True})['fixture'] for name, row in parsed.items()}
    finally:
        adapter.close()
    rows = []
    for name in selected:
        path = out / (name + '.php')
        path.write_bytes(sources.CASES[name])
        native = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(path)], out / (name + '-native'), 30)
        assert native['exit'] == 0 and not native['timeout']
        checks = conditions(name, programs[name], path, (out / (name + '-native.stdout')).read_bytes())
        fixture = out / (name + '.watsup')
        fixture.write_text(HELPERS + '\ndec $main() : bool\ndef $main() = true\n'
            + ''.join('  -- ' + ('' if check.startswith('PhpStep:') else 'if ') + check + '\n' for check in checks))
        rows.append({'id': name, 'conditions': len(checks), 'native': native})
    report = {'selection': selected, 'rows': rows, 'environment': {key: ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING')}}
    if args.prepare_only:
        report['execution'] = 'checked syntax and native preparation only; zero semantic agreement'
    else:
        modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
        runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
        watched = [*modules, ROOT / 'spec/semantics/modules.json', runner, Path(__file__), Path(sources.__file__),
                   ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/error_handler_run.py',
                   ROOT / 'tests/semantics/recorded_worker.py', *[out / (name + '.watsup') for name in selected]]
        digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        before = {str(path): digest(path) for path in watched}
        report['revision'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        for row in rows:
            result = recorded([str(runner), '--sl', *map(str, modules), str(out / (row['id'] + '.watsup'))], out / (row['id'] + '-model'), 120)
            row['model'] = result
            row['passed'] = result['exit'] == 0 and not result['timeout'] and (out / (row['id'] + '-model.stdout')).read_text().strip() == 'true' and not (out / (row['id'] + '-model.stderr')).read_bytes()
            print(row['id'], row['passed'], flush=True)
            if not row['passed']:
                break
        assert before == {str(path): digest(path) for path in watched}
        assert report['revision'] == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs'] = before
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return args.prepare_only or all(row.get('passed', False) for row in rows)


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
