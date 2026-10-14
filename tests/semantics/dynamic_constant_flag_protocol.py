#!/usr/bin/env python3
"""Reached ignored-flag warning, publication and handler-created collision."""
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
STAGES = {'plain': ('static-native-v41', 'plain-ignored', 'V41_PLAIN', 41, 41),
    'selected': ('static-native-v41', 'selected-reentry', 'V41_KEEP', 17, 29)}
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
  -- if $dynamic_constant_case_flag(pconfigcall)
def $test_front(S, 1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE /\ pconfigcall.SELECTION =/= eps
  -- if $dynamic_constant_case_flag(pconfigcall)
def $test_front(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall
def $test_front(S, 3) = true
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


def negatives(state, selected):
    variants = ['pconfigcall[.KIND = INTRINSIC_DEFINED]',
        'pconfigcall[.SITE = PORIGIN 0 eps]',
        'pconfigcall[.LINE = $(pconfigcall.LINE + 1)]',
        'pconfigcall[.SENT = [NAMED_SENT (KNOWN pvalue_name), NAMED_SENT (KNOWN pvalue_candidate), NAMED_SENT (KNOWN (PBOOL false))]]',
        'pconfigcall[.SENT = [NAMED_SENT (KNOWN pvalue_name), NAMED_SENT (KNOWN pvalue_candidate)]]',
        'pconfigcall[.SENT = [NAMED_SENT (KNOWN pvalue_name), NAMED_SENT (KNOWN (PINT 99)), NAMED_SENT (KNOWN (PBOOL true))]]',
        'pconfigcall[.SENT = [NAMED_SENT (KNOWN (PSTRING ($ptascii("V41_FORGED")))), NAMED_SENT (KNOWN pvalue_candidate), NAMED_SENT (KNOWN (PBOOL true))]]']
    if selected:
        variants.append('pconfigcall[.SELECTION = eps]')
    checks = []
    for call in variants:
        resume = 'DYNAMIC_CONSTANT_CASE_WARNING (' + call + ')'
        task = 'ERROR_HANDLER_INVOKE (perrorcall[.RESUME = ' + resume + '])' if selected else resume
        checks += ['~$dynamic_constant_case_valid(' + state + ',' + call + ')',
            '~$call_descriptors_valid(' + state + '[.TODO = (' + task + ') :: ptask_tail*])']
    return checks


def assertions(main, case, name, constant, old, candidate, stdout):
    selected = name == 'selected'
    mode = '1' if selected else '0'
    checks = ['S_initial = $php_run(' + main + ',0,' + json.dumps(b64(os.fsencode(case / 'main.php'))) + ')',
        *reached('S', '$test_seek(S_initial,' + mode + ',1200)'), '$test_front(S,' + mode + ')',
        'S.FILEINCLUDEPATH = eps', 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'S.USERCONSTANTS = eps', '$dynamic_define_values(pconfigcall) = ((preqbytes,pvalue_candidate))',
        'preqbytes = $ptascii(' + json.dumps(constant) + ')', 'pvalue_candidate = PINT ' + str(candidate),
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name), NAMED_SENT (KNOWN pvalue_candidate), NAMED_SENT (KNOWN (PBOOL true))]',
        '$dynamic_constant_case_flag(pconfigcall)', '$dynamic_constant_case_valid(S,pconfigcall)',
        '$call_task_valid(S,CONFIG_INVOKE pconfigcall)', '|$test_warnings(S.EVENTS)| = 0', *public('S'),
        *reached('S_dispatch', '$drive_steps(S,1)'), 'S_dispatch.USERCONSTANTS = eps', *public('S_dispatch')]
    if not selected:
        checks += ['S_dispatch.TODO = (DYNAMIC_CONSTANT_CASE_WARNING pconfigcall) :: ptask_tail*',
            '$call_task_valid(S_dispatch,DYNAMIC_CONSTANT_CASE_WARNING pconfigcall)',
            '|$test_warnings(S_dispatch.EVENTS)| = 1',
            '$test_outputs(S_dispatch.EVENTS) = $test_outputs(S.EVENTS)',
            *negatives('S_dispatch', False), *reached('S_return', '$drive_steps(S_dispatch,1)'),
            'S_return.RESULT = KNOWN (PBOOL true)', 'S_return.USERCONSTANTS = [puserconstant]',
            'puserconstant.NAME = preqbytes', 'puserconstant.VALUE = pvalue_candidate',
            'puserconstant.ORIGIN = pconfigcall.SITE', 'puserconstant.CLASS = PVSCALAR',
            'puserconstant.READS = eps /\\ puserconstant.RECEIVES = eps']
    else:
        checks += ['pconfigcall.SELECTION = (n_selection)',
            '$selected_task_nonce(DYNAMIC_CONSTANT_CASE_WARNING pconfigcall) = (n_selection)',
            'S.SELECTEDCALLS[n_selection] = pselectedcall', 'pselectedcall.KIND = INTRINSIC_DEFINE',
            'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall',
            'perrorcall.LEVEL = 2', 'perrorcall.MESSAGE = $dynamic_constant_case_message()',
            'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE pconfigcall.LINE',
            '$error_call_valid(S_dispatch,perrorcall)', '|$test_warnings(S_dispatch.EVENTS)| = 0',
            *negatives('S_dispatch', True)]
        for change in ['[.LEVEL = 512]', '[.SITE = PORIGIN 0 eps]',
                '[.EVENT = DIAGNOSTIC "Notice" perrorcall.MESSAGE pconfigcall.LINE]',
                '[.LINE = $(pconfigcall.LINE + 1)][.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE ($(pconfigcall.LINE + 1))]',
                '[.MESSAGE = $ptascii("forged")][.EVENT = DIAGNOSTIC "Warning" ($ptascii("forged")) pconfigcall.LINE]']:
            checks += ['~$error_call_valid(S_dispatch,perrorcall' + change + ')',
                '~$call_descriptors_valid(S_dispatch[.TODO = (ERROR_HANDLER_INVOKE (perrorcall' + change + ')) :: ptask_tail*])']
        checks += [*reached('S_entered', '$drive_steps(S_dispatch,1)'),
            'S_entered.CURRENT = (pcallcontext)', '$error_context_trigger(S_entered,pcallcontext) = (pconfigcall)',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name), NAMED_SENT (KNOWN pvalue_candidate), NAMED_SENT (KNOWN (PBOOL true))]',
            'S_entered.USERCONSTANTS = eps', *public('S_entered'),
            *reached('S_seed', '$test_seek(S_entered,2,1200)'),
            'S_seed.TODO = (ERROR_HANDLER_RESULT perrorcall_case) :: ptask_tail*',
            'perrorcall_case.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall',
            'S_seed.RESULT = KNOWN (PBOOL true)', 'S_seed.USERCONSTANTS = [puserconstant]',
            'puserconstant.NAME = preqbytes', 'puserconstant.VALUE = PINT ' + str(old),
            'puserconstant.ORIGIN =/= pconfigcall.SITE', '$dynamic_define_source(S_seed,puserconstant.ORIGIN)',
            '$dynamic_constant_case_valid(S_seed,pconfigcall)', '|$test_warnings(S_seed.EVENTS)| = 0',
            *public('S_seed'), *reached('S_pending', '$drive_steps(S_seed,1)'),
            'S_pending.TODO = (DYNAMIC_CONSTANT_CASE_WARNING pconfigcall) :: ptask_tail*',
            'S_pending.USERCONSTANTS = [puserconstant]', *public('S_pending'),
            *reached('S_duplicate', '$drive_steps(S_pending,1)'),
            'S_duplicate.TODO = (ERROR_HANDLER_INVOKE perrorcall_duplicate) :: ptask_tail*',
            'perrorcall_duplicate.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall 1',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name), NAMED_SENT (KNOWN pvalue_candidate), NAMED_SENT (KNOWN (PBOOL true))]',
            '$selected_task_nonce(DYNAMIC_CONSTANT_DUPLICATE pconfigcall 1) = (n_selection)',
            '$dynamic_constant_duplicate_valid(S_duplicate,pconfigcall,1)',
            'perrorcall_duplicate.LEVEL = 2',
            'perrorcall_duplicate.MESSAGE = $global_constant_duplicate_message(preqbytes)',
            '$error_call_valid(S_duplicate,perrorcall_duplicate)',
            'S_duplicate.USERCONSTANTS = [puserconstant]', '|$test_warnings(S_duplicate.EVENTS)| = 0', *public('S_duplicate')]
        for prefix in ['0', '2']:
            checks += ['~$dynamic_constant_duplicate_valid(S_duplicate,pconfigcall,' + prefix + ')',
                '~$call_descriptors_valid(S_duplicate[.TODO = (ERROR_HANDLER_INVOKE (perrorcall_duplicate[.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall ' + prefix + '])) :: ptask_tail*])']
        checks += [*reached('S_handled', '$test_seek(S_duplicate,3,1200)'),
            'S_handled.TODO = (ERROR_HANDLER_RESULT perrorcall_handled) :: ptask_tail*',
            'perrorcall_handled.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall 1',
            'S_handled.RESULT = KNOWN (PBOOL true)', 'S_handled.USERCONSTANTS = [puserconstant]',
            '|$test_warnings(S_handled.EVENTS)| = 0', *public('S_handled'),
            *reached('S_rejected', '$drive_steps(S_handled,1)'),
            'S_rejected.TODO = (DYNAMIC_CONSTANT_DUPLICATE pconfigcall 1) :: ptask_tail*',
            'S_rejected.USERCONSTANTS = [puserconstant]', *public('S_rejected'),
            *reached('S_return', '$drive_steps(S_rejected,1)'), 'S_return.RESULT = KNOWN (PBOOL false)',
            'S_return.USERCONSTANTS = [puserconstant]']
    checks += ['S_return.TODO = ptask_tail*', *public('S_return'),
        'S_final = $drive_steps(S_return,2000)', 'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps',
        '$test_outputs(S_final.EVENTS) = $ptascii(' + json.dumps(stdout) + ')',
        '|$test_warnings(S_final.EVENTS)| = ' + ('0' if selected else '1'), *public('S_final'),
        'S_final.USERCONSTANTS = [puserconstant]']
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
