#!/usr/bin/env python3
"""Reached duplicate define warnings, captured prefixes and false results."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import file_compile_notice_sources as inputs
import static_types as types
from recorded_worker import Worker
from typed_static_invoke_set_protocol import process

ROOT = Path(__file__).resolve().parents[2]
STAGES = {'plain': ('static-native-v40', 'plain-duplicate', 'V40_DUP', 41, 42),
    'selected': ('static-native-v40-selected', 'selected-append', 'V40_KEEP', 17, 18)}
b64 = lambda data: base64.b64encode(data).decode()
PREFIX = r'''
dec $test_output_item(pevent) : nat*
def $test_output_item(OUTPUT n*) = n*
def $test_output_item(pevent) = eps -- otherwise
dec $test_outputs(pevent*) : nat*
def $test_outputs(eps) = eps
def $test_outputs(pevent :: pevent_tail*) = $test_output_item(pevent) ++ $test_outputs(pevent_tail*)
dec $test_warning_item(pevent) : nat*
def $test_warning_item(DIAGNOSTIC "Warning" n_message* z) = [0]
def $test_warning_item(pevent) = eps -- otherwise
dec $test_warnings(pevent*) : nat*
def $test_warnings(eps) = eps
def $test_warnings(pevent :: pevent_tail*) = $test_warning_item(pevent) ++ $test_warnings(pevent_tail*)
dec $test_running(pstate) : pstate
def $test_running(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $test_running(S) = S -- otherwise
dec $test_front(pstate, nat) : bool
def $test_front(S, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.SELECTION = eps
  -- if S.USERCONSTANTS =/= eps
def $test_front(S, 1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.SELECTION =/= eps
def $test_front(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall n_constants
def $test_front(S, n_mode) = false -- otherwise
dec $test_seek(pstate, nat, nat) : pstate
def $test_seek(S, n_mode, 0) = S
def $test_seek(S, n_mode, n_steps) = S
  -- if $(n_steps > 0)
  -- if $test_front(S,n_mode) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_seek(S, n_mode, n_steps) = $test_seek($drive_steps($test_running(S),1),n_mode,$nabs($(n_steps - 1)))
  -- if $(n_steps > 0)
  -- if ~$test_front(S,n_mode)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def public(state):
    return ['$call_descriptors_valid(' + state + ')', '$declaration_entry_check(' + state + ') = ' + state,
        '$heap_valid($heap_graph(' + state + '))']


def reached(state, expression):
    return [state + '_budget = ' + expression,
        state + '_budget.COMPLETION = NORMAL \\/ ' + state + '_budget.COMPLETION = BUDGET',
        state + ' = ' + state + '_budget[.COMPLETION = NORMAL]']


def negatives(state, tail, selected):
    variants = [('pconfigcall', '0'), ('pconfigcall', '2'),
        ('pconfigcall[.KIND = INTRINSIC_DEFINED]', '1'),
        ('pconfigcall[.SITE = PORIGIN 0 eps]', '1'),
        ('pconfigcall[.LINE = $(pconfigcall.LINE + 1)]', '1'),
        ('pconfigcall[.SENT = [NAMED_SENT (KNOWN pvalue_name), NAMED_SENT (KNOWN (PINT 99))]]', '1'),
        ('pconfigcall[.SENT = [NAMED_SENT (KNOWN (PSTRING ($ptascii("V40_FORGED")))), NAMED_SENT (KNOWN pvalue_candidate)]]', '1')]
    if selected:
        variants.append(('pconfigcall[.SELECTION = eps]', '1'))
    checks = []
    for call, prefix in variants:
        resume = 'DYNAMIC_CONSTANT_DUPLICATE (' + call + ') ' + prefix
        task = 'ERROR_HANDLER_INVOKE (perrorcall[.RESUME = ' + resume + '])' if selected else resume
        checks += ['~$dynamic_constant_duplicate_valid(' + state + ',' + call + ',' + prefix + ')',
            '~$call_descriptors_valid(' + state + '[.TODO = (' + task + ') :: ' + tail + '])']
    return checks


def assertions(main, case, name, constant, old, candidate, stdout):
    mode = '1' if name == 'selected' else '0'
    checks = ['S_initial = $php_run(' + main + ',0,' + json.dumps(b64(os.fsencode(case / 'main.php'))) + ')',
        *reached('S', '$test_seek(S_initial,' + mode + ',1200)'), '$test_front(S,' + mode + ')',
        'S.FILEINCLUDEPATH = eps', 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'S.USERCONSTANTS = [puserconstant]', 'puserconstant.VALUE = PINT ' + str(old),
        'puserconstant.NAME = $ptascii(' + json.dumps(constant) + ')',
        '$dynamic_define_values(pconfigcall) = ((preqbytes,pvalue_candidate))',
        'preqbytes = puserconstant.NAME', 'pvalue_candidate = PINT ' + str(candidate),
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name), NAMED_SENT (KNOWN pvalue_candidate)]',
        '$dynamic_constant_duplicate_valid(S,pconfigcall,1)', *public('S'),
        *reached('S_dispatch', '$drive_steps(S,1)'),
        'S_dispatch.USERCONSTANTS = [puserconstant]', *public('S_dispatch')]
    if name == 'plain':
        checks += ['S_dispatch.TODO = (DYNAMIC_CONSTANT_DUPLICATE pconfigcall 1) :: ptask_tail*',
            '|$test_warnings(S_dispatch.EVENTS)| = 1',
            '$test_outputs(S_dispatch.EVENTS) = $test_outputs(S.EVENTS)',
            *negatives('S_dispatch', 'ptask_tail*', False),
            *reached('S_return', '$drive_steps(S_dispatch,1)')]
    else:
        checks += ['pconfigcall.SELECTION = (n_selection)',
            '$selected_task_nonce(DYNAMIC_CONSTANT_DUPLICATE pconfigcall 1) = (n_selection)',
            'S.SELECTEDCALLS[n_selection] = pselectedcall', 'pselectedcall.KIND = INTRINSIC_DEFINE',
            'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall 1',
            'perrorcall.LEVEL = 2', 'perrorcall.MESSAGE = $global_constant_duplicate_message(preqbytes)',
            '$error_call_valid(S_dispatch,perrorcall)', '|$test_warnings(S_dispatch.EVENTS)| = 0',
            *negatives('S_dispatch', 'ptask_tail*', True)]
        for change in ['[.LEVEL = 512]', '[.SITE = PORIGIN 0 eps]',
                '[.EVENT = DIAGNOSTIC "Notice" perrorcall.MESSAGE pconfigcall.LINE]',
                '[.LINE = $(pconfigcall.LINE + 1)][.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE ($(pconfigcall.LINE + 1))]',
                '[.MESSAGE = $ptascii("forged")][.EVENT = DIAGNOSTIC "Warning" ($ptascii("forged")) pconfigcall.LINE]']:
            checks += ['~$error_call_valid(S_dispatch,perrorcall' + change + ')',
                '~$call_descriptors_valid(S_dispatch[.TODO = (ERROR_HANDLER_INVOKE (perrorcall' + change + ')) :: ptask_tail*])']
        checks += [*reached('S_false', '$test_seek(S_dispatch,2,1200)'),
            'S_false.TODO = (ERROR_HANDLER_RESULT perrorcall_false) :: ptask_tail*',
            'perrorcall_false.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall 1',
            'S_false.RESULT = KNOWN (PBOOL false)', 'S_false.USERCONSTANTS = [puserconstant,puserconstant_side]',
            'puserconstant_side.NAME = $ptascii("V40_SIDE")', 'puserconstant_side.VALUE = PINT 5',
            '$dynamic_constant_duplicate_valid(S_false,pconfigcall,1)',
            '|$test_warnings(S_false.EVENTS)| = 0', *public('S_false'),
            '~$dynamic_constant_duplicate_valid(S_false[.USERCONSTANTS = [puserconstant_side]],pconfigcall,1)',
            '~$call_descriptors_valid(S_false[.USERCONSTANTS = [puserconstant_side]])',
            '~$dynamic_constant_duplicate_valid(S_false[.USERCONSTANTS = [puserconstant_side,puserconstant]],pconfigcall,1)',
            '~$call_descriptors_valid(S_false[.USERCONSTANTS = [puserconstant_side,puserconstant]])',
            *reached('S_pending', '$drive_steps(S_false,1)'),
            'S_pending.TODO = (DYNAMIC_CONSTANT_DUPLICATE pconfigcall 1) :: ptask_tail*',
            '|S_pending.USERCONSTANTS| = 2', '|$test_warnings(S_pending.EVENTS)| = 1', *public('S_pending'),
            *reached('S_return', '$drive_steps(S_pending,1)')]
    checks += ['S_return.RESULT = KNOWN (PBOOL false)', 'S_return.TODO = ptask_tail*', *public('S_return')]
    if name == 'selected':
        checks += [*reached('S_second', '$test_seek(S_return,1,1200)'),
            'S_second.TODO = (CONFIG_INVOKE pconfigcall_second) :: ptask_second*',
            'S_second.USERCONSTANTS = [puserconstant,puserconstant_side]',
            'pconfigcall_second.SELECTION = (n_second)', 'n_second =/= n_selection',
            '$dynamic_constant_duplicate_valid(S_second,pconfigcall_second,2)', *public('S_second'),
            *reached('S_true_dispatch', '$drive_steps(S_second,1)'), *public('S_true_dispatch'),
            *reached('S_true', '$test_seek(S_true_dispatch,2,1200)'),
            'S_true.TODO = (ERROR_HANDLER_RESULT perrorcall_true) :: ptask_second*',
            'perrorcall_true.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_second 2',
            'S_true.RESULT = KNOWN (PBOOL true)', 'S_true.USERCONSTANTS = [puserconstant,puserconstant_side]',
            '|$test_warnings(S_true.EVENTS)| = 1', *public('S_true'),
            *reached('S_true_pending', '$drive_steps(S_true,1)'),
            'S_true_pending.TODO = (DYNAMIC_CONSTANT_DUPLICATE pconfigcall_second 2) :: ptask_second*',
            '|$test_warnings(S_true_pending.EVENTS)| = 1', *public('S_true_pending'),
            *reached('S_true_return', '$drive_steps(S_true_pending,1)'),
            'S_true_return.RESULT = KNOWN (PBOOL false)', *public('S_true_return')]
    final_start = 'S_true_return' if name == 'selected' else 'S_return'
    checks += ['S_final = $drive_steps(' + final_start + ',2000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', '$test_outputs(S_final.EVENTS) = $ptascii(' + json.dumps(stdout) + ')',
        '|$test_warnings(S_final.EVENTS)| = 1', *public('S_final'),
        'S_final.USERCONSTANTS = ' + ('[puserconstant,puserconstant_side]' if name == 'selected' else '[puserconstant]')]
    return checks


def prepare(out, sources, names):
    out.mkdir()
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for name in names:
            suite, case_name, constant, old, candidate = STAGES[name]
            case = sources / suite / case_name
            native = json.loads((case.parent / 'report.json').read_text())
            row, = [item for item in native['records'] if item['id'] == case_name]
            assert native['result'] == 'native_observation' and native['stable_inputs']
            assert native['target'] == types.PROFILE and row['exit'] == 0
            assert hashlib.sha256((case / 'main.php').read_bytes()).hexdigest() == row['originals']['main.php']
            parsed = frontend.request({'op': 'parse', 'source': b64((case / 'main.php').read_bytes())})
            assert parsed['accepted'], parsed
            main = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            checks = assertions(main, case, name, constant, old, candidate, row['stdout'])
            target = out / name
            target.mkdir()
            (target / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
            (target / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                ''.join('  -- if ' + item + '\n' for item in checks))
    finally:
        if adapter:
            adapter.close()
        frontend.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['fixtures', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stage', action='append', default=[])
    parser.add_argument('--attempt', type=int, default=1)
    args = parser.parse_args()
    names, out, sources = args.stage or list(STAGES), args.output.resolve(), args.sources.resolve()
    assert args.attempt > 0 and names and len(set(names)) == len(names) and set(names) <= STAGES.keys()
    paths = [Path(__file__), ROOT / 'tests/semantics/recorded_worker.py',
        ROOT / 'tests/semantics/_build/default/numeric_runner.exe', ROOT / 'frontend/target.php', ROOT / 'adapter/wire.ml']
    for name in names:
        suite, case, _, _, _ = STAGES[name]
        paths += [sources / suite / 'report.json', sources / suite / 'run.py', sources / suite / case / 'main.php']
        paths += [sources / suite / case / 'native' / item for item in ['stdout', 'stderr', 'process.json', 'command.json']]
        if args.phase == 'check':
            paths += [out / name / 'protocol.watsup', out / name / 'assertions.json']
    pins = lambda: dict(inputs.inputs(), **{str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    before = pins()
    label = args.phase if args.attempt == 1 else args.phase + '-' + str(args.attempt)
    assert not (out / (label + '-report.json')).exists()
    report = {'phase': args.phase, 'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'module_count': len(json.loads((ROOT / 'spec/semantics/modules.json').read_text())), 'inputs': before,
        'implementation_diff_sha256': hashlib.sha256(subprocess.check_output(['git', 'diff', 'HEAD', '--', 'spec/semantics'], cwd=ROOT)).hexdigest(),
        'records': [], 'agreement_credit': 0, 'result': 'fail'}
    try:
        if args.phase == 'fixtures':
            prepare(out, sources, names)
        else:
            mods = [str(ROOT / item) for item in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
            for name in names:
                target = out / name
                runner = process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *mods,
                    str(target / 'protocol.watsup')], target / label, 90, ROOT)
                passed = runner.returncode == 0 and runner.stdout.strip() == b'true' and not runner.stderr
                report['records'].append({'id': name, 'pass': passed, 'runner_exit': runner.returncode,
                    'premises': len(json.loads((target / 'assertions.json').read_text())) if passed else 0})
                print(json.dumps(report['records'][-1]), flush=True)
                if not passed:
                    break
        report['result'] = 'pass' if args.phase == 'fixtures' or len(report['records']) == len(names) and all(row['pass'] for row in report['records']) else 'fail'
    finally:
        report['stable_inputs'] = before == pins()
        if not report['stable_inputs']:
            report['result'] = 'fail'
            for record in report['records']:
                record['pass'], record['premises'] = False, 0
        (out / (label + '-report.json')).write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if report['result'] == 'pass' else 1)


if __name__ == '__main__':
    main()
