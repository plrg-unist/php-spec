#!/usr/bin/env python3
"""Check reached exception-handler API cursor, ownership, and terminal states."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

from error_handler_run import recorded
from recorded_worker import Worker


ROOT = Path(__file__).resolve().parents[2]
CASES = (
    'deprecated-warning-throw-reenters-replacement-then-original',
    'deprecated-byref-selected-target-and-fresh-throwable-slot',
    'exception-closure-body-drop-preserves-call-retain',
    'exception-early-warning-throw-fatal',
)
HELPERS = r'''
dec $eh_test_front(pstate, nat) : bool
def $eh_test_front(S, 0) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = API_CALLBACK_SEND papiargcursor
  -- if papiargcursor.CALL = API_EXCEPTION pexceptioncall
  -- if perrorcall.LEVEL = 16384
def $eh_test_front(S, 1) = true
  -- if S.TODO = (API_CALLBACK_SEND papiargcursor) :: ptask_tail*
  -- if papiargcursor.CALL = API_EXCEPTION pexceptioncall
  -- if papiargcursor.INDEX = 0
  -- if $target_function(S, papiargcursor.TARGET) = (pfunction)
  -- if $function_deprecated(S, pfunction) = DEPRECATED_ATTRIBUTE ptbytes_message ptbytes_since
def $eh_test_front(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = API_CALLBACK_REF papiargcursor
  -- if papiargcursor.CALL = API_EXCEPTION pexceptioncall
  -- if perrorcall.LEVEL = 2
def $eh_test_front(S, 3) = true
  -- if S.TODO = (API_CALLBACK_SEND papiargcursor) :: ptask_tail*
  -- if papiargcursor.CALL = API_EXCEPTION pexceptioncall
  -- if papiargcursor.INDEX = 1
  -- if papiargcursor.SENT = (REFERENCE n) :: eps
def $eh_test_front(S, 4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = API_BORROWED_TARGET pshutdownproducer
  -- if pcallcontext.INSTANCE = (n)
  -- if $heap_owners($heap_prune($heap_graph(S)), HOBJECT n) = 2
def $eh_test_front(S, 5) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = API_BORROWED_TARGET pshutdownproducer
  -- if pcallcontext.INSTANCE = (n)
  -- if $heap_owners($heap_prune($heap_graph(S)), HOBJECT n) = 1
def $eh_test_front(S, 6) = true
  -- if S.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall) :: ptask_tail*
  -- if pexceptioncall.TARGET = (API_BORROWED_TARGET pshutdownproducer)
  -- if pshutdownproducer.TARGET = CLOSURE_TARGET n
  -- if ~((HOBJECT n) <- S.ALLOCATIONS)
  -- if $target_receiver($api_callback_result_scope(S, API_BORROWED_TARGET pshutdownproducer), pshutdownproducer.TARGET) = (n_receiver)
  -- if ~((HOBJECT n_receiver) <- S.ALLOCATIONS)
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $eh_test_front(S, 7) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = API_CALLBACK_SEND papiargcursor
  -- if papiargcursor.CALL = API_EXCEPTION pexceptioncall
  -- if perrorcall.LEVEL = 16384
def $eh_test_front(S, n) = false -- otherwise
dec $eh_test_seek(pstate, nat, nat) : pstate
def $eh_test_seek(S, n_stage, n) = S -- if $eh_test_front(S, n_stage)
def $eh_test_seek(S, n_stage, 0) = S -- if ~$eh_test_front(S, n_stage)
def $eh_test_seek(S, n_stage, n) = $eh_test_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$eh_test_front(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $eh_test_seek(S, n_stage, n) = S
  -- if ~$eh_test_front(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $eh_test_output(pevent*) : ptbytes
dec $eh_test_is_output(pevent) : bool
def $eh_test_output(eps) = eps
def $eh_test_output((OUTPUT ptbytes) :: pevent_tail*) = ptbytes ++ $eh_test_output(pevent_tail*)
def $eh_test_output(pevent :: pevent_tail*) = $eh_test_output(pevent_tail*) -- if ~$eh_test_is_output(pevent)
def $eh_test_is_output(OUTPUT ptbytes) = true
def $eh_test_is_output(pevent) = false -- otherwise
'''


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def conditions(name, program, source, expected_stdout):
    checks = [f'S_initial = $php_run({program}, 0, "{base64.b64encode(str(source).encode()).decode()}")',
              'S_initial.COMPLETION = BUDGET']

    def reach(label, prior, stage):
        checks.extend([f'{label}_found = $eh_test_seek({prior}, {stage}, 3000)',
                       fr'{label}_found.COMPLETION = NORMAL \/ {label}_found.COMPLETION = BUDGET',
                       f'{label} = {label}_found[.COMPLETION = NORMAL]',
                       f'$eh_test_front({label}, {stage})',
                       f'$call_descriptors_valid({label})',
                       f'$heap_valid($heap_graph({label}))'])

    if name == CASES[0]:
        reach('S_deprecated', 'S_initial', 0)
        checks += [
            'S_deprecated.TODO = (ERROR_HANDLER_INVOKE perrorcall_deprecated) :: ptask_tail*',
            'perrorcall_deprecated.RESUME = API_CALLBACK_SEND papiargcursor_deprecated',
            'papiargcursor_deprecated.CALL = API_EXCEPTION pexceptioncall',
            'pexceptioncall.OBJECT = n_original',
            'papiargcursor_deprecated.SENT = eps', 'papiargcursor_deprecated.INDEX = 0',
            '$api_cursor_warning_valid(S_deprecated, papiargcursor_deprecated)',
            '$api_callback_roots(papiargcursor_deprecated.CALL) = [HOBJECT n_original]',
            '~$api_cursor_warning_valid(S_deprecated, papiargcursor_deprecated[.LINE = $(papiargcursor_deprecated.LINE + 1)])',
        ]
        reach('S_resumed', 'S_deprecated', 1)
        checks += [
            'S_resumed.TODO = (API_CALLBACK_SEND papiargcursor_resumed) :: ptask_tail*',
            'papiargcursor_resumed.CALL = API_EXCEPTION pexceptioncall_resumed',
            'pexceptioncall_resumed.OBJECT = n_original',
            'papiargcursor_resumed.TARGET = papiargcursor_deprecated.TARGET',
            'papiargcursor_resumed.PRODUCER = papiargcursor_deprecated.PRODUCER',
            'papiargcursor_resumed.SENT = eps', 'papiargcursor_resumed.INDEX = 0',
            '$api_cursor_valid(S_resumed, papiargcursor_resumed)',
            'S_resumed.EXCEPTIONHANDLER =/= eps',
            '~$api_cursor_valid(S_resumed, papiargcursor_resumed[.PRODUCER = papiargcursor_resumed.PRODUCER[.SITE = eps]])',
        ]
        last = 'S_resumed'
    elif name == CASES[1]:
        reach('S_warning', 'S_initial', 2)
        checks += [
            'S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall_warning) :: ptask_tail*',
            'perrorcall_warning.RESUME = API_CALLBACK_REF papiargcursor_warning',
            'papiargcursor_warning.CALL = API_EXCEPTION pexceptioncall_warning',
            'pexceptioncall_warning.OBJECT = n_original',
            'papiargcursor_warning.SENT = eps', 'papiargcursor_warning.INDEX = 0',
            '$api_cursor_warning_ref_valid(S_warning, papiargcursor_warning)',
            'perrorcall_warning.EVENT = DIAGNOSTIC_INTERNAL "Warning" perrorcall_warning.MESSAGE 0',
        ]
        reach('S_fresh', 'S_warning', 3)
        checks += [
            'S_fresh.TODO = (API_CALLBACK_SEND papiargcursor_fresh) :: ptask_tail*',
            'papiargcursor_fresh.CALL = API_EXCEPTION pexceptioncall_fresh',
            'pexceptioncall_fresh.OBJECT = n_original',
            'papiargcursor_fresh.SENT = (REFERENCE n_cell) :: eps',
            'papiargcursor_fresh.VALUES = [POBJECT n_original]',
            'S_fresh.STORE[n_cell] = DEFINED (POBJECT n_original)',
            '$heap_owners($heap_prune($heap_graph(S_fresh)), HCELL n_cell) = 1',
            '$api_cursor_valid(S_fresh, papiargcursor_fresh)',
            'S_fresh.EXCEPTIONHANDLER =/= eps',
            '~$api_cursor_valid(S_fresh, papiargcursor_fresh[.SENT = [KNOWN (POBJECT n_original)]])',
            '~$api_cursor_valid(S_fresh, papiargcursor_fresh[.INDEX = 0])',
        ]
        last = 'S_fresh'
    elif name == CASES[2]:
        reach('S_deprecated', 'S_initial', 0)
        checks += [
            'S_deprecated.TODO = (ERROR_HANDLER_INVOKE perrorcall_deprecated) :: ptask_tail*',
            'perrorcall_deprecated.RESUME = API_CALLBACK_SEND papiargcursor_deprecated',
            'papiargcursor_deprecated.CALL = API_EXCEPTION pexceptioncall',
            'papiargcursor_deprecated.TARGET = CLOSURE_TARGET n_closure',
            'papiargcursor_deprecated.PRODUCER = pshutdownproducer',
            'papiargcursor_deprecated.SENT = eps', 'papiargcursor_deprecated.INDEX = 0',
            '$heap_owners($heap_prune($heap_graph(S_deprecated)), HOBJECT n_closure) = 1',
            '$target_nodes(API_BORROWED_TARGET pshutdownproducer) = eps',
        ]
        reach('S_pending', 'S_deprecated', 1)
        checks += [
            'S_pending.TODO = (API_CALLBACK_SEND papiargcursor_pending) :: ptask_tail*',
            'papiargcursor_pending.TARGET = CLOSURE_TARGET n_closure',
            '$api_cursor_valid(S_pending, papiargcursor_pending)',
            '$heap_owners($heap_prune($heap_graph(S_pending)), HOBJECT n_closure) = 1',
        ]
        reach('S_entered', 'S_pending', 4)
        checks += [
            'S_entered.CURRENT = (pcallcontext)',
            'pcallcontext.TARGET = API_BORROWED_TARGET pshutdownproducer',
            'pcallcontext.INSTANCE = (n_closure)',
            'pcallcontext.RECEIVER = (n_receiver)',
            '$heap_owners($heap_prune($heap_graph(S_entered)), HOBJECT n_closure) = 2',
            '$heap_owners($heap_prune($heap_graph(S_entered)), HOBJECT n_receiver) = 1',
        ]
        reach('S_body', 'S_entered', 5)
        checks += [
            'S_body.CURRENT = (pcallcontext_body)',
            'pcallcontext_body.TARGET = API_BORROWED_TARGET pshutdownproducer',
            'pcallcontext_body.INSTANCE = (n_closure)',
            'pcallcontext_body.RECEIVER = (n_receiver)',
            '$heap_owners($heap_prune($heap_graph(S_body)), HOBJECT n_closure) = 1',
            '$heap_owners($heap_prune($heap_graph(S_body)), HOBJECT n_receiver) = 1',
        ]
        reach('S_result', 'S_body', 6)
        checks += [
            'S_result.TODO = (EXCEPTION_HANDLER_RESULT pexceptioncall_result) :: ptask_tail*',
            'pexceptioncall_result.TARGET = (API_BORROWED_TARGET pshutdownproducer)',
            '~((HOBJECT n_closure) <- S_result.ALLOCATIONS)',
            '~((HOBJECT n_receiver) <- S_result.ALLOCATIONS)',
            '$exception_result_valid(S_result, pexceptioncall_result)',
            '$target_function($api_callback_result_scope(S_result, API_BORROWED_TARGET pshutdownproducer), pshutdownproducer.TARGET) = (pfunction)',
            '$target_receiver($api_callback_result_scope(S_result, API_BORROWED_TARGET pshutdownproducer), pshutdownproducer.TARGET) = (n_receiver)',
            '~$exception_selected_valid(S_result, pexceptioncall_result[.TARGET = (API_BORROWED_TARGET pshutdownproducer[.SITE = eps])])',
        ]
        last = 'S_result'
    else:
        reach('S_deprecated', 'S_initial', 0)
        reach('S_throw', 'S_deprecated', 7)
        checks += [
            'S_throw.TODO = (THROW_SEARCH n_saved) :: (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_tail*',
            'perrorcall_throw.RESUME = API_CALLBACK_SEND papiargcursor_throw',
            'papiargcursor_throw.CALL = API_EXCEPTION pexceptioncall_throw',
            'papiargcursor_throw.SENT = eps', 'papiargcursor_throw.INDEX = 0',
            'S_throw.EXCEPTIONHANDLER = eps',
            '$throwable_live(S_throw, n_saved)',
            '$throwable_marker(ERROR_HANDLER_RESULT perrorcall_throw)',
            '$exception_terminal_tail(S_throw, (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_tail*)',
            '~$exception_dispatch_ready(S_throw)',
            'PhpStep: S_throw ~> S_uncaught',
            'S_uncaught.COMPLETION = UNCAUGHT n_saved',
            'S_uncaught.TODO = eps',
        ]
        last = 'S_throw'
    checks += [f'S_done = $drive_steps({last}, 3000)',
               'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
               '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
               '$eh_test_output(S_done.EVENTS) = [' + ','.join(map(str, expected_stdout)) + ']']
    if name == CASES[3]:
        checks += ['S_done.COMPLETION = REQUESTFATAL ptbytes_class ptbytes_message 12',
                   'ptbytes_class = $ptascii("Exception")',
                   'ptbytes_message = $ptascii("preentry")',
                   'S_done.EXITSTATUS = 255']
    else:
        checks += ['S_done.COMPLETION = NORMAL']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', action='append', required=True, type=Path)
    parser.add_argument('--case', choices=CASES, action='append')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    assert len(os.sched_getaffinity(0)) == 1 and next(iter(os.sched_getaffinity(0))) in range(1, 6)
    assert not subprocess.check_output(['git', 'status', '--porcelain=v1'], cwd=ROOT)
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    php = ROOT / '.tools/php/bin/php'
    watched = [Path(__file__), ROOT / 'tests/semantics/error_handler_run.py',
               ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/profile.json',
               ROOT / 'spec/semantics/modules.json', ROOT / 'spec/semantics/30-storage.watsup',
               ROOT / 'spec/semantics/222-exception-handlers.watsup',
               ROOT / 'spec/semantics/442-deprecated-api-callbacks.watsup',
               ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
               ROOT / '_build/default/adapter/main.exe', ROOT / 'frontend/worker.php',
               ROOT / '.tools/php-file.so', php]
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    native = {}
    for report_path in args.native_report:
        report = json.loads(report_path.read_bytes())
        assert report['passed'] and report['profile'] == profile
        binary_hashes = [value for key, value in report['inputs'].items()
                         if key.endswith('.tools/php/bin/php')]
        assert binary_hashes == [digest(php)]
        watched.append(report_path)
        for row in report['rows']:
            source = Path(row['native']['argv'][-1])
            assert row['passed'] and row['native']['exit'] in (0, 255)
            assert not row['native']['timeout'] and not row['native']['group_after']
            assert source.is_file() and digest(source) == row['source_sha256']
            assert row['id'] not in native
            native[row['id']] = (source, row)
            watched.append(source)
    selected = args.case or CASES
    assert len(set(selected)) == len(selected) and set(selected) <= native.keys()
    before = {str(path): digest(path) for path in watched}
    out = args.output.resolve()
    out.mkdir(parents=True)
    flags = [flag for key, value in profile.items() for flag in ('-d', key + '=' + value)]
    frontend = Worker([str(php), '-n', *flags, '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = {name: frontend.request({'op': 'parse', 'source': base64.b64encode(native[name][0].read_bytes()).decode()})
                  for name in selected}
        assert all(row['accepted'] for row in parsed.values())
    finally:
        frontend.close()
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        programs = {name: adapter.request({'op': 'check', 'ast': parsed[name]['ast'], 'fixture': True})['fixture']
                    for name in selected}
    finally:
        adapter.close()
    rows = []
    for name in selected:
        source, native_row = native[name]
        checks = conditions(name, programs[name], source, base64.b64decode(native_row['stdout_b64']))
        fixture = out / (name + '.watsup')
        fixture.write_text(HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
            '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            for condition in checks))
        before[str(fixture)] = digest(fixture)
        process = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                            '--sl', *map(str, modules), str(fixture)], out / (name + '-model'), 300)
        passed = (process['exit'] == 0 and not process['timeout'] and process['interruption'] is None
                  and not process['group_after']
                  and (out / (name + '-model.stdout')).read_bytes() == b'true\n'
                  and not (out / (name + '-model.stderr')).read_bytes())
        rows.append({'id': name, 'source_sha256': digest(source),
                     'fixture_sha256': digest(fixture), 'conditions': len(checks),
                     'derived_guard_assertions': {CASES[0]: 2, CASES[1]: 2, CASES[2]: 1, CASES[3]: 0}[name],
                     'model': process, 'passed': passed})
        print(name, passed, flush=True)
        if not passed:
            break
    assert before == {path: digest(path) for path in before}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    assert not subprocess.check_output(['git', 'status', '--porcelain=v1'], cwd=ROOT)
    passed = len(rows) == len(selected) and all(row['passed'] for row in rows)
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'profile': profile,
        'inputs': before, 'selection': selected, 'affinity': sorted(os.sched_getaffinity(0)),
        'rows': rows, 'passed': passed,
        'scope': 'Four reached source fronts and derived cursor guards; no native execution'}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
