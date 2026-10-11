#!/usr/bin/env python3
"""Source-reached copied operands and owning reference results in integer ops."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile

from error_handler_run import ENV, recorded
from recorded_worker import Worker
from integer_operator_warning_protocol import HELPERS
import integer_operator_warnings as sources

ROOT = sources.ROOT
CASES = ('copy-right-0', 'copy-left-0', 'both-copy-leading', 'literal-string-left',
         'refcall-right-0', 'refcall-left-failure', 'refcall-right-throw',
         'refassign-live-0', 'copy-array-right', 'copy-left-3', 'literal-left-3')
HELPERS += r'''
def $integer_frontier(S, 6) = true
  -- if S.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i) pintegerconversion 1) :: ptask_tail*
'''


def swapped_conditions(name, program, path, stdout):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_entry = $integer_seek(S_initial, 0, 2000)[.COMPLETION = NORMAL]',
        '$integer_operator_plan(S_entry) = (pintegeroperation)',
        '$integer_operation_valid(S_entry, pintegeroperation)',
        'pintegeroperation.OP = BITAND', 'pintegeroperation.SWAPPED',
        '~$integer_operation_valid(S_entry, pintegeroperation[.SWAPPED = false])',
        '~$integer_operation_valid(S_entry[.CODE = eps], pintegeroperation)',
        'pintegeroperation.LEFT = KNOWN pvalue_float',
        'pvalue_float = PFLOAT n_float',
        'pintegeroperation.LEFTPOINTER = INTEGER_COPY pvalue_float',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("b"))',
        '$integer_slot_rank(S_entry, pintegeroperation.SITE, [PCFIELD 0], pintegeroperation.LEFT) = (' + ('2' if name == 'copy-left-3' else '1') + ')',
        '$integer_slot_rank(S_entry, pintegeroperation.SITE, [PCFIELD 1], pintegeroperation.RIGHT) = (8)',
        '$integer_phase_pointer(pintegeroperation, INTEGER_LEFT) = pintegeroperation.RIGHTPOINTER',
        '$integer_phase_pointer(pintegeroperation, INTEGER_RIGHT 2) = pintegeroperation.LEFTPOINTER',
        'PhpStep: S_entry ~> S_begin',
        'S_begin.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation INTEGER_LEFT) :: ptask_tail*',
        'S_begin.ALLOCATIONS = S_entry.ALLOCATIONS', 'S_begin.STORE = S_entry.STORE',
        '$task_nodes(INTEGER_OPERATOR_CONVERT pintegeroperation INTEGER_LEFT) = eps',
        '$call_descriptors_valid(S_begin)',
    ]
    if name == 'copy-left-3':
        checks += [
            '$integer_pointer_value(S_begin, pintegeroperation.RIGHTPOINTER) = (PARRAY n_array)',
            '$integer_conversion(PARRAY n_array) = eps',
            'PhpStep: S_begin ~> S_failure',
            'S_failure.COMPLETION = THROWN "TypeError" ($ptascii("Unsupported operand types: array & float")) pintegeroperation.LINE',
            'S_failure.EVENTS = S_begin.EVENTS', 'S_failure.STORE = S_begin.STORE',
            '$lookup(S_failure.ENV, $ptascii("a")) = (n_live)',
            'S_failure.STORE[n_live] = DEFINED pvalue_float',
            'S_done = $drive_steps(S_begin, 2500)',
            '$drive_steps(S_begin, 1) = $drive_steps($gc_transition_owners(S_begin, $destruction_transition_owners(S_begin, $sensitive_trace_freeze($source_exception_transition(S_begin, $throwable_transition(S_begin, S_failure))))), 0)',
        ]
    else:
        checks += [
            'PhpStep: S_begin ~> S_first',
            'S_first.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion_first 0) :: ptask_tail*',
            'pintegerconversion_first.INPUT = PINT 2',
            'pintegerconversion_first.VALUE = 2', 'pintegerconversion_first.NOTICES = eps',
            '$integer_warning_valid(S_first, pintegeroperation, INTEGER_LEFT, pintegerconversion_first, 0)',
            'PhpStep: S_first ~> S_second',
            'S_second.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT 2)) :: ptask_tail*',
            'PhpStep: S_second ~> S_capture',
            'S_capture.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT 2) pintegerconversion 0) :: ptask_tail*',
            'pintegerconversion.INPUT = pvalue_float', 'pintegerconversion.VALUE = 5',
            '|pintegerconversion.NOTICES| = 1',
            '$integer_warning_valid(S_capture, pintegeroperation, INTEGER_RIGHT 2, pintegerconversion, 0)',
            '~$integer_warning_valid(S_capture, pintegeroperation[.SWAPPED = false], INTEGER_RIGHT 2, pintegerconversion, 0)',
            'PhpStep: S_capture ~> S_dispatch',
            'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT 2) pintegerconversion 1',
            '$error_call_valid(S_dispatch, perrorcall)',
            '~$error_call_valid(S_dispatch, perrorcall[.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation[.SWAPPED = false] (INTEGER_RIGHT 2) pintegerconversion 1])',
            'S_return = $integer_seek(S_dispatch, 6, 2000)[.COMPLETION = NORMAL]',
            '$integer_frontier(S_return, 6)',
            'S_return.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT 2) pintegerconversion 1) :: ptask_tail*',
            '$integer_pointer_value(S_return, pintegeroperation.RIGHTPOINTER) = (PINT 3)',
            '$integer_pointer_value(S_return, pintegeroperation.LEFTPOINTER) = (pvalue_float)',
            '$integer_warning_valid(S_return, pintegeroperation, INTEGER_RIGHT 2, pintegerconversion, 1)',
            '$task_nodes(INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT 2) pintegerconversion 1) = eps',
            '$call_descriptors_valid(S_return)',
            'S_done = $drive_steps(S_return, 2500)',
            '$lookup(S_done.ENV, $ptascii("v")) = (n_result)',
            'S_done.STORE[n_result] = DEFINED (PINT 0)',
            '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
            '$drive_steps(S_capture, 1) = $gc_transition_owners(S_capture, $destruction_transition_owners(S_capture, $sensitive_trace_freeze($source_exception_transition(S_capture, $throwable_transition(S_capture, S_dispatch)))))[.COMPLETION = BUDGET]',
            '$drive_steps(S_capture, 2500) = S_done',
        ]
    return checks + [
        'S_done.COMPLETION = NORMAL',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        'S_done.FRAMES = eps', 'S_done.HELD = eps', '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_begin, 0) = S_begin[.COMPLETION = BUDGET]',
    ]


def conditions(name, program, path, stdout):
    if name in ('copy-left-3', 'literal-left-3'):
        return swapped_conditions(name, program, path, stdout)
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_entry = $integer_seek(S_initial, 0, 2000)[.COMPLETION = NORMAL]',
        '$integer_frontier(S_entry, 0)', '$call_descriptors_valid(S_entry)',
        '$integer_operator_plan(S_entry) = (pintegeroperation)',
        '$integer_operation_valid(S_entry, pintegeroperation)',
        '~pintegeroperation.SWAPPED',
        '~$integer_operation_valid(S_entry, pintegeroperation[.SWAPPED = true])',
        '~$integer_operation_valid(S_entry, pintegeroperation[.OP = ADD])',
        '~$integer_operation_valid(S_entry, pintegeroperation[.LINE = $(pintegeroperation.LINE + 1)])',
        '~$integer_operation_valid(S_entry[.ORIGIN = eps], pintegeroperation)',
        'n_invalid = |S_entry.STORE|',
        '~$integer_operation_valid(S_entry, pintegeroperation[.LEFTPOINTER = INTEGER_CELL n_invalid])',
        'PhpStep: S_entry ~> S_begin',
        'S_begin.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation INTEGER_LEFT) :: ptask_tail*',
        'S_begin.STORE = S_entry.STORE', 'S_begin.ALLOCATIONS = S_entry.ALLOCATIONS',
        '$task_nodes(INTEGER_OPERATOR_CONVERT pintegeroperation INTEGER_LEFT) = $operand_nodes(pintegeroperation.LEFT) ++ $operand_nodes(pintegeroperation.RIGHT)',
        '$call_descriptors_valid(S_begin)',
        'S_capture = $integer_seek(S_begin, 1, 2000)[.COMPLETION = NORMAL]',
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
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        '~$error_call_valid(S_dispatch, perrorcall[.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 0])',
    ]
    if name == 'refcall-right-throw':
        checks += ['S_done = $drive_steps(S_dispatch, 2500)']
    else:
        checks += [
            'S_return = $integer_seek(S_dispatch, 3, 2000)[.COMPLETION = NORMAL]',
            '$integer_frontier(S_return, 3)', '$call_descriptors_valid(S_return)',
            'S_right = $integer_seek(S_return, 4, 2000)[.COMPLETION = NORMAL]',
            '$integer_frontier(S_right, 4)',
            'S_right.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT pintegerconversion.VALUE)) :: ptask_tail*',
            '$call_descriptors_valid(S_right)', 'S_done = $drive_steps(S_right, 2500)',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        'S_done.FRAMES = eps', 'S_done.HELD = eps', '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_capture, 1) = $gc_transition_owners(S_capture, $destruction_transition_owners(S_capture, $sensitive_trace_freeze($source_exception_transition(S_capture, $throwable_transition(S_capture, S_dispatch)))))[.COMPLETION = BUDGET]',
        '$drive_steps(S_begin, 2500) = S_done', '$drive_steps(S_capture, 2500) = S_done',
    ]
    if name in ('copy-right-0', 'both-copy-leading'):
        value = 2 if name == 'copy-right-0' else 7
        checks += [
            'pintegeroperation.RIGHT = KNOWN (PINT ' + str(value) + ')',
            'pintegeroperation.RIGHTPOINTER = INTEGER_COPY (PINT ' + str(value) + ')',
            '$integer_pointer_value(S_right, pintegeroperation.RIGHTPOINTER) = (PINT ' + str(value) + ')',
            '~$integer_operation_valid(S_capture, pintegeroperation[.RIGHTPOINTER = INTEGER_CV ($ptascii("b"))])',
            '$lookup(S_right.ENV, $ptascii("b")) = (n_live)',
            'S_right.STORE[n_live] = DEFINED (PINT ' + ('3' if name == 'copy-right-0' else '5') + ')',
            '$task_nodes(INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 0) = eps',
        ]
    if name in ('copy-left-0', 'both-copy-leading', 'literal-string-left'):
        checks += [
            'pintegeroperation.LEFT = KNOWN pintegerconversion.INPUT',
            'pintegeroperation.LEFTPOINTER = INTEGER_COPY pintegerconversion.INPUT',
            '$integer_pointer_value(S_right, pintegeroperation.LEFTPOINTER) = (pintegerconversion.INPUT)',
            '~$integer_operation_valid(S_capture, pintegeroperation[.LEFTPOINTER = INTEGER_CV ($ptascii("a"))])',
        ]
    if name == 'literal-string-left':
        checks += [
            '$string_bytes(pintegerconversion.INPUT) = ($ptascii("12.5tail"))',
            '|pintegerconversion.NOTICES| = 2',
            '~$integer_operation_source(S_capture, pintegeroperation[.LEFT = KNOWN PNULL])',
            'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("b"))',
            '$integer_pointer_value(S_right, pintegeroperation.RIGHTPOINTER) = (PINT 5)',
        ]
    if name.startswith('refcall') or name == 'refassign-live-0':
        side = 'LEFT' if name == 'refcall-left-failure' else 'RIGHT'
        checks += [
            'pintegeroperation.' + side + ' = REFERENCE n_old',
            'pintegeroperation.' + side + 'POINTER = INTEGER_CELL n_old',
            '$task_nodes(INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 0) = [HCELL n_old]',
            '$task_nodes(ERROR_HANDLER_INVOKE perrorcall) = [HCELL n_old]',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_old) = ' + ('3' if name == 'refassign-live-0' else '2'),
            '~$integer_operation_valid(S_capture, pintegeroperation[.' + side + 'POINTER = INTEGER_COPY (PINT 2)])',
            '~$integer_operation_valid(S_capture, pintegeroperation[.' + side + ' = REFERENCE n_invalid])',
            '$integer_pointer_value(S_capture, pintegeroperation.' + side + 'POINTER) = (pvalue_owned)',
            '~$integer_operation_valid(S_capture, pintegeroperation[.' + side + ' = KNOWN pvalue_owned][.' + side + 'POINTER = INTEGER_COPY pvalue_owned])',
            '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_old) = ' + ('1' if name == 'refassign-live-0' else '0'),
        ]
        if name != 'refcall-right-throw':
            checks += [
                '$heap_owners($heap_prune($heap_graph(S_right)), HCELL n_old) = ' + ('2' if name == 'refassign-live-0' else '1'),
                '$integer_pointer_value(S_right, pintegeroperation.' + side + 'POINTER) = (' + ('pintegerconversion.INPUT' if side == 'LEFT' else 'PINT 7' if name == 'refassign-live-0' else 'PINT 2') + ')',
            ]
    if name == 'copy-array-right':
        checks += [
            'pintegeroperation.RIGHT = KNOWN (PARRAY n_array)',
            'pintegeroperation.RIGHTPOINTER = INTEGER_COPY (PARRAY n_array)',
            '$task_nodes(INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 0) = [HARRAY n_array]',
            '$integer_pointer_value(S_right, pintegeroperation.RIGHTPOINTER) = (PARRAY n_array)',
            '$heap_owners($heap_prune($heap_graph(S_right)), HARRAY n_array) = $($heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_array) + 1)',
            '~$integer_operation_valid(S_capture, pintegeroperation[.RIGHTPOINTER = INTEGER_CV ($ptascii("b"))])',
        ]
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', choices=CASES)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = (args.case,) if args.case else CASES
    out = args.output or Path(tempfile.mkdtemp(prefix='integer-copy-protocol-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    print(out, flush=True)
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
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
        rows.append({'id': name, 'conditions': len(checks), 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'native': native})
    report = {'revision': revision, 'selection': selected, 'rows': rows,
        'environment': {key: ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING')}}
    if args.prepare_only:
        report['execution'] = 'checked syntax and native preparation only; zero semantic agreement'
    else:
        modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
        runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
        watched = [*modules, ROOT / 'spec/semantics/modules.json', runner, Path(__file__), Path(sources.__file__),
                   ROOT / 'tests/semantics/integer_operator_copy_cases.py', ROOT / 'tests/semantics/integer_operator_warning_protocol.py',
                   ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/error_handler_run.py',
                   ROOT / 'tests/semantics/recorded_worker.py', *[out / (name + '.watsup') for name in selected]]
        digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        before = {str(path): digest(path) for path in watched}
        for row in rows:
            result = recorded([str(runner), '--sl', *map(str, modules), str(out / (row['id'] + '.watsup'))], out / (row['id'] + '-model'), 120)
            row['model'] = result
            row['passed'] = result['exit'] == 0 and not result['timeout'] and (out / (row['id'] + '-model.stdout')).read_text().strip() == 'true' and not (out / (row['id'] + '-model.stderr')).read_bytes()
            print(row['id'], row['passed'], flush=True)
            if not row['passed']:
                break
        assert before == {str(path): digest(path) for path in watched}
        report['inputs'] = before
    assert report['revision'] == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return args.prepare_only or all(row.get('passed', False) for row in rows)


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
