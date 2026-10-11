#!/usr/bin/env python3
"""Independent reached checks for borrowed left cells and later diagnostics."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from error_handler_run import ENV, recorded
from recorded_worker import Worker
import integer_operator_warning_protocol as protocol
import integer_operator_warning_review as originals

ROOT = originals.ROOT
CASES = ('mod-left-ref-diagnostic', 'and-eager-ref-live-write', 'leading-handler-replace')
HELPERS = protocol.HELPERS.replace('def $integer_frontier(S, n) = false -- otherwise', r'''
def $integer_frontier(S, 6) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 2
def $integer_frontier(S, 7) = true
  -- if S.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 2) :: ptask_tail*
def $integer_frontier(S, n) = false -- otherwise
''')


def conditions(name, program, path, stdout):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_entry = $integer_seek(S_initial, 0, 1500)[.COMPLETION = NORMAL]',
        '$integer_frontier(S_entry, 0)', '$integer_operator_plan(S_entry) = (pintegeroperation)',
        'S_capture = $integer_seek(S_entry, 1, 1500)[.COMPLETION = NORMAL]',
        '$integer_frontier(S_capture, 1)',
        'S_capture.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 0) :: ptask_tail*',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
        '$task_nodes(INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 0) = eps',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S_capture, 1)', 'S_one.COMPLETION = BUDGET',
        '$integer_frontier(S_one, 2)', '$call_descriptors_valid(S_one)',
        'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
        '$error_call_valid(S_one, perrorcall_first)',
        '~$error_call_valid(S_one, perrorcall_first[.EVENT = OUTPUT eps])',
        '~$integer_warning_valid(S_capture, pintegeroperation, INTEGER_LEFT, pintegerconversion[.INPUT = PINT 12], 0)',
        'S_return = $integer_seek(S_one, 3, 1500)[.COMPLETION = NORMAL]',
        '$integer_frontier(S_return, 3)', '$call_descriptors_valid(S_return)',
        'S_right = $integer_seek(S_return, 4, 1500)[.COMPLETION = NORMAL]',
        '$integer_frontier(S_right, 4)', '$call_descriptors_valid(S_right)',
        'S_done = $drive_steps(S_right, 1500)', 'S_done.COMPLETION = NORMAL',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_entry, 1500) = S_done', '$drive_steps(S_capture, 1500) = S_done',
        '$drive_steps(S_one[.COMPLETION = NORMAL], 1500) = S_done',
    ]
    if name == 'mod-left-ref-diagnostic':
        checks += [
            '$lookup(S_entry.ENV, $ptascii("x")) = (n_old)',
            'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_old',
            '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_old) = 2',
            '$lookup(S_return.ENV, $ptascii("x")) = (n_new)', 'n_new =/= n_old',
            '$lookup(S_return.ENV, $ptascii("keep")) = (n_old)',
            'S_return.STORE[n_new] = DEFINED (PBOOL true)',
            '$integer_pointer_value(S_return, pintegeroperation.LEFTPOINTER) = (pintegerconversion.INPUT)',
            'pintegerconversion.VALUE = 5',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_old) = 1',
            '~$integer_operation_valid(S_return, pintegeroperation[.RIGHTPOINTER = INTEGER_CELL n_old])',
            '~$integer_operation_valid(S_return, pintegeroperation[.LEFTPOINTER = INTEGER_CV ($ptascii("keep"))])',
        ]
    else:
        checks += [
            '$string_bytes(pintegerconversion.INPUT) = ($ptascii("12.5tail"))',
            'pintegerconversion.VALUE = 12', '|pintegerconversion.NOTICES| = 2',
            'S_second = $integer_seek(S_return, 6, 1500)[.COMPLETION = NORMAL]',
            '$integer_frontier(S_second, 6)',
            'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
            '$error_call_valid(S_second, perrorcall_second)', 'perrorcall_second.LEVEL = 8192',
            'perrorcall_second.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion 2',
            'S_twice = $integer_seek(S_second, 7, 1500)[.COMPLETION = NORMAL]',
            '$integer_frontier(S_twice, 7)', '$call_descriptors_valid(S_twice)',
            '$drive_steps(S_second, 1500) = S_done', '$drive_steps(S_twice, 1500) = S_done',
        ]
        if name == 'and-eager-ref-live-write':
            checks += [
                '$lookup(S_entry.ENV, $ptascii("y")) = (n_old)',
                'pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_old',
                '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_old) = 2',
                '$lookup(S_return.ENV, $ptascii("y")) = (n_new)', 'n_new =/= n_old',
                '$lookup(S_twice.ENV, $ptascii("old")) = (n_old)',
                'S_return.STORE[n_old] = DEFINED (PINT 1)',
                'S_twice.STORE[n_old] = DEFINED (PINT 7)',
                '$integer_pointer_value(S_right, pintegeroperation.RIGHTPOINTER) = (PINT 7)',
                '$heap_owners($heap_prune($heap_graph(S_twice)), HCELL n_old) = 1',
                'S_right_capture = $integer_seek(S_right, 5, 1500)[.COMPLETION = NORMAL]',
                'S_right_capture.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT 12) pintegerconversion_right 0) :: ptask_tail*',
                'pintegerconversion_right.INPUT = PINT 7', 'pintegerconversion_right.VALUE = 7',
                'pintegerconversion_right.NOTICES = eps',
            ]
        else:
            checks += [
                '$string_bytes(perrorcall_first.CALLBACK) = ($ptascii("h1"))',
                'S_return.ERRORHANDLER.CALLBACK = (pvalue_h2)',
                '$string_bytes(pvalue_h2) = ($ptascii("h2"))',
                'perrorcall_second.CALLBACK = pvalue_h2',
                'perrorcall_first.CALLBACK =/= perrorcall_second.CALLBACK',
            ]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=CASES)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = (args.case,) if args.case else CASES
    out = args.output or Path(tempfile.mkdtemp(prefix='integer-op-review-state-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    print(out, flush=True)
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = {name: frontend.request({'op': 'parse', 'source': base64.b64encode(originals.CASES[name]['source'].encode()).decode()}) for name in selected}
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
        case = originals.CASES[name]
        path = out / (name + '.php')
        path.write_text(case['source'])
        native = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(path)], out / (name + '-native'), 30)
        assert native['exit'] == 0 and not native['timeout']
        assert (out / (name + '-native.stdout')).read_bytes() == case['stdout'].encode()
        assert (out / (name + '-native.stderr')).read_bytes() == case['stderr'].encode()
        checks = conditions(name, programs[name], path, case['stdout'].encode())
        fixture = out / (name + '.watsup')
        fixture.write_text(HELPERS + '\ndec $main() : bool\ndef $main() = true\n'
            + ''.join('  -- if ' + check + '\n' for check in checks) + 'def $main() = false -- otherwise\n')
        rows.append({'id': name, 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                     'conditions': len(checks), 'native': native})
    report = {'selection': selected, 'rows': rows, 'profile': profile,
              'semantic_mode': 'SL',
              'environment': {key: ENV.get(key) for key in ('LC_ALL', 'TZ', 'PHP_SPEC_SCRIPT_ENCODING')}}
    if args.prepare_only:
        report['execution'] = 'checked source/native preparation; zero model agreement'
    else:
        modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
        runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
        watched = [*modules, ROOT / 'spec/semantics/modules.json', runner, Path(__file__),
                   Path(protocol.__file__), Path(originals.__file__), originals.CATALOG,
                   ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/error_handler_run.py',
                   ROOT / 'tests/semantics/recorded_worker.py', ROOT / '.tools/php/bin/php',
                   ROOT / '.tools/php-file.so', ROOT / '_build/default/adapter/main.exe',
                   *[out / (name + '.watsup') for name in selected]]
        digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        before = {str(path): digest(path) for path in watched}
        report['revision'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        for row in rows:
            result = recorded([str(runner), '--sl', *map(str, modules), str(out / (row['id'] + '.watsup'))], out / (row['id'] + '-model'), 120)
            row['model'] = result
            row['passed'] = (result['exit'] == 0 and not result['timeout']
                             and (out / (row['id'] + '-model.stdout')).read_text().strip() == 'true'
                             and not (out / (row['id'] + '-model.stderr')).read_bytes())
            print(row['id'], row['passed'], flush=True)
            if not row['passed']:
                break
        assert before == {str(path): digest(path) for path in watched}
        assert report['revision'] == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs'] = before
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return args.prepare_only or (len(rows) == len(selected) and all(row.get('passed', False) for row in rows))


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
