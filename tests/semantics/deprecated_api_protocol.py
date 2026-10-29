#!/usr/bin/env python3
"""Check reached selected API callback preparation and owner boundaries."""
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
    'assert-closure-entry-retain-outlives-last-outside-alias',
    'assert-early-throw-enters-live-exception-policy',
    'unmarked-assert-active-handler-replacement-and-fresh-refs',
    'error-handler-mask-and-moved-callback-owner',
)
HELPERS = r'''
dec $api_test_front(pstate, nat) : bool
def $api_test_front(S, 0) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = API_CALLBACK_SEND papiargcursor
  -- if papiargcursor.CALL = API_ASSERT passertcall
  -- if perrorcall.LEVEL = 16384
def $api_test_front(S, 1) = true
  -- if S.TODO = (API_CALLBACK_SEND papiargcursor) :: ptask_tail*
  -- if papiargcursor.CALL = API_ASSERT passertcall
  -- if papiargcursor.INDEX = 0
def $api_test_front(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = API_BORROWED_TARGET pshutdownproducer
  -- if pcallcontext.INSTANCE = (n)
def $api_test_front(S, 3) = true
  -- if S.TODO = (THROW_SEARCH n) :: (API_CALLBACK_SEND papiargcursor) :: ptask_tail*
  -- if papiargcursor.CALL = API_ASSERT passertcall
def $api_test_front(S, 4) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = API_CALLBACK_REF papiargcursor
  -- if papiargcursor.CALL = API_ASSERT passertcall
  -- if papiargcursor.INDEX = 0
def $api_test_front(S, 5) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = API_CALLBACK_REF papiargcursor
  -- if papiargcursor.CALL = API_ASSERT passertcall
  -- if papiargcursor.INDEX = 2
def $api_test_front(S, 6) = true
  -- if S.TODO = (API_CALLBACK_SEND papiargcursor) :: ptask_tail*
  -- if papiargcursor.CALL = API_ERROR perrorcall
  -- if papiargcursor.INDEX = 0
def $api_test_front(S, 7) = true
  -- if S.TODO = (API_CALLBACK_REF papiargcursor) :: ptask_tail*
  -- if papiargcursor.CALL = API_ERROR perrorcall
  -- if papiargcursor.INDEX = 0
def $api_test_front(S, 8) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = API_BORROWED_TARGET pshutdownproducer
  -- if pcallcontext.INSTANCE = (n)
  -- if $heap_owners($heap_prune($heap_graph(S)), HOBJECT n) = 1
def $api_test_front(S, n) = false -- otherwise
dec $api_test_seek(pstate, nat, nat) : pstate
def $api_test_seek(S, n_stage, n) = S -- if $api_test_front(S, n_stage)
def $api_test_seek(S, n_stage, 0) = S -- if ~$api_test_front(S, n_stage)
def $api_test_seek(S, n_stage, n) = $api_test_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$api_test_front(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $api_test_seek(S, n_stage, n) = S
  -- if ~$api_test_front(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $api_test_output(pevent*) : ptbytes
dec $api_test_is_output(pevent) : bool
def $api_test_output(eps) = eps
def $api_test_output((OUTPUT ptbytes) :: pevent_tail*) = ptbytes ++ $api_test_output(pevent_tail*)
def $api_test_output(pevent :: pevent_tail*) = $api_test_output(pevent_tail*) -- if ~$api_test_is_output(pevent)
def $api_test_is_output(OUTPUT ptbytes) = true
def $api_test_is_output(pevent) = false -- otherwise
'''


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def conditions(name, program, source, expected_stdout):
    checks = [f'S_initial = $php_run({program}, 0, "{base64.b64encode(str(source).encode()).decode()}")',
              'S_initial.COMPLETION = BUDGET']

    def reach(label, prior, stage):
        checks.extend([f'{label}_found = $api_test_seek({prior}, {stage}, 3000)',
                       f'{label}_found.COMPLETION = NORMAL \\/ {label}_found.COMPLETION = BUDGET',
                       f'{label} = {label}_found[.COMPLETION = NORMAL]',
                       f'$api_test_front({label}, {stage})',
                       f'$call_descriptors_valid({label})',
                       f'$heap_valid($heap_graph({label}))'])

    if name == CASES[0]:
        reach('S_deprecated', 'S_initial', 0)
        checks += [
            'S_deprecated.TODO = (ERROR_HANDLER_INVOKE perrorcall_deprecation) :: ptask_tail*',
            'perrorcall_deprecation.RESUME = API_CALLBACK_SEND papiargcursor',
            'papiargcursor.CALL = API_ASSERT passertcall',
            'papiargcursor.TARGET = CLOSURE_TARGET n_closure',
            'papiargcursor.PRODUCER = pshutdownproducer',
            'papiargcursor.SENT = eps', 'papiargcursor.INDEX = 0',
            '$api_cursor_valid(S_deprecated, papiargcursor)',
            '$heap_owners($heap_prune($heap_graph(S_deprecated)), HOBJECT n_closure) = 3',
            '$target_nodes(API_BORROWED_TARGET pshutdownproducer) = eps',
            '~$api_cursor_valid(S_deprecated, papiargcursor[.LINE = $(papiargcursor.LINE + 1)])',
            '~$api_cursor_valid(S_deprecated, papiargcursor[.PRODUCER = pshutdownproducer[.SITE = eps]])',
        ]
        reach('S_pending', 'S_deprecated', 1)
        checks += [
            'S_pending.TODO = (API_CALLBACK_SEND papiargcursor_pending) :: ptask_tail*',
            'papiargcursor_pending.TARGET = CLOSURE_TARGET n_closure',
            '$api_cursor_valid(S_pending, papiargcursor_pending)',
            '$heap_owners($heap_prune($heap_graph(S_pending)), HOBJECT n_closure) = 1',
            '~$api_cursor_valid(S_pending, papiargcursor_pending[.SENT = [KNOWN PNULL]][.INDEX = 1])',
        ]
        reach('S_entered', 'S_pending', 2)
        checks += [
            'S_entered.CURRENT = (pcallcontext)',
            'pcallcontext.TARGET = API_BORROWED_TARGET pshutdownproducer',
            'pcallcontext.INSTANCE = (n_closure)',
            'pcallcontext.RECEIVER = (n_receiver)',
            '$heap_owners($heap_prune($heap_graph(S_entered)), HOBJECT n_closure) = 2',
            '$heap_owners($heap_prune($heap_graph(S_entered)), HOBJECT n_receiver) = 1',
            '$target_nodes(pcallcontext.TARGET) = eps',
        ]
        reach('S_body', 'S_entered', 8)
        checks += [
            'S_body.CURRENT = (pcallcontext_body)',
            'pcallcontext_body.TARGET = API_BORROWED_TARGET pshutdownproducer',
            'pcallcontext_body.INSTANCE = (n_closure)',
            'pcallcontext_body.RECEIVER = (n_receiver)',
            '$heap_owners($heap_prune($heap_graph(S_body)), HOBJECT n_closure) = 1',
            '$heap_owners($heap_prune($heap_graph(S_body)), HOBJECT n_receiver) = 1',
        ]
        last = 'S_body'
    elif name == CASES[1]:
        reach('S_deprecated', 'S_initial', 0)
        reach('S_throw', 'S_deprecated', 3)
        checks += [
            'S_throw.TODO = (THROW_SEARCH n_saved) :: (API_CALLBACK_SEND papiargcursor) :: ptask_tail*',
            'papiargcursor.CALL = API_ASSERT passertcall',
            'papiargcursor.SENT = eps', 'papiargcursor.INDEX = 0',
            'S_throw.ASSERTEXCEPTION.VALUE',
            '$throwable_live(S_throw, n_saved)',
            '$api_cursor_saved_valid(S_throw, papiargcursor)',
            '~$api_cursor_saved_valid(S_throw, papiargcursor[.LINE = $(papiargcursor.LINE + 1)])',
            '$target_nodes(API_BORROWED_TARGET papiargcursor.PRODUCER) = eps',
            'PhpStep: S_throw ~> S_policy',
            'S_policy.COMPLETION = THROWING n_assert',
            'n_assert =/= n_saved',
            '$throwable_field(S_policy, n_assert, "previous") = POBJECT n_saved',
            'S_policy.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
            'pconfigcall = passertcall.FAILURE.CALL',
        ]
        last = 'S_throw'
    elif name == CASES[2]:
        reach('S_first_warning', 'S_initial', 4)
        checks += [
            'S_first_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
            'perrorcall_first.RESUME = API_CALLBACK_REF papiargcursor_first',
            'papiargcursor_first.TARGET = pcalltarget',
            '$target_function(S_first_warning, pcalltarget) = (pfunction)',
            '$function_deprecated(S_first_warning, pfunction) = NO_DEPRECATED',
            'papiargcursor_first.SENT = eps',
            '$api_cursor_valid(S_first_warning, papiargcursor_first)',
            '$api_cursor_warning_ref_valid(S_first_warning, papiargcursor_first)',
            '~$api_cursor_valid(S_first_warning, papiargcursor_first[.INDEX = 1])',
        ]
        reach('S_third_warning', 'S_first_warning', 5)
        checks += [
            'S_third_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall_third) :: ptask_tail*',
            'perrorcall_third.RESUME = API_CALLBACK_REF papiargcursor_third',
            'papiargcursor_third.SENT = [REFERENCE n_file, KNOWN pvalue_line]',
            'papiargcursor_third.VALUES[0] = pvalue_file',
            'S_third_warning.STORE[n_file] = DEFINED pvalue_file',
            '$heap_owners($heap_prune($heap_graph(S_third_warning)), HCELL n_file) = 1',
            '$api_cursor_valid(S_third_warning, papiargcursor_third)',
            '$api_cursor_warning_ref_valid(S_third_warning, papiargcursor_third)',
            '~$api_cursor_valid(S_third_warning, papiargcursor_third[.SENT = [KNOWN pvalue_file, KNOWN pvalue_line]])',
        ]
        last = 'S_third_warning'
    else:
        reach('S_default_deprecated', 'S_initial', 6)
        checks += [
            'S_default_deprecated.TODO = (API_CALLBACK_SEND papiargcursor) :: ptask_tail*',
            'papiargcursor.CALL = API_ERROR perrorcall',
            'perrorcall.CALLBACK = POBJECT n_handler',
            'S_default_deprecated.ERRORHANDLER.CALLBACK = eps',
            'papiargcursor.SENT = eps',
            '$api_cursor_valid(S_default_deprecated, papiargcursor)',
            '$heap_owners($heap_prune($heap_graph(S_default_deprecated)), HOBJECT n_handler) = 1',
            '$target_nodes(API_BORROWED_TARGET papiargcursor.PRODUCER) = eps',
            '~$api_cursor_valid(S_default_deprecated, papiargcursor[.INDEX = 1])',
        ]
        reach('S_default_warning', 'S_default_deprecated', 7)
        checks += [
            'S_default_warning.TODO = (API_CALLBACK_REF papiargcursor_warning) :: ptask_tail*',
            'papiargcursor_warning.CALL = API_ERROR perrorcall_warning',
            'papiargcursor_warning.SENT = eps', 'papiargcursor_warning.INDEX = 0',
            'S_default_warning.ERRORHANDLER.CALLBACK = eps',
            '$call_task_valid(S_default_warning, API_CALLBACK_REF papiargcursor_warning)',
            '$heap_owners($heap_prune($heap_graph(S_default_warning)), HOBJECT n_handler) = 1',
        ]
        last = 'S_default_warning'
    checks += [f'S_done = $drive_steps({last}, 3000)', 'S_done.COMPLETION = NORMAL',
               'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
               '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
               '$api_test_output(S_done.EVENTS) = [' + ','.join(map(str, expected_stdout)) + ']']
    if name == CASES[0]:
        checks += [
            '~((HOBJECT n_closure) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            '$target_function($api_callback_result_scope(S_done, API_BORROWED_TARGET pshutdownproducer), pshutdownproducer.TARGET) = (pfunction)',
            '$target_receiver($api_callback_result_scope(S_done, API_BORROWED_TARGET pshutdownproducer), pshutdownproducer.TARGET) = (n_receiver)',
        ]
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
    native = {}
    watched = [Path(__file__), ROOT / 'tests/semantics/error_handler_run.py',
               ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/profile.json',
               ROOT / 'spec/semantics/modules.json', ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
               ROOT / '_build/default/adapter/main.exe', ROOT / 'frontend/worker.php',
               ROOT / '.tools/php-file.so', php]
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    watched.extend(modules)
    for report_path in args.native_report:
        report = json.loads(report_path.read_bytes())
        assert report['passed'] and report['profile'] == profile
        binary_hashes = [value for key, value in report['inputs'].items()
                         if key.endswith('.tools/php/bin/php')]
        assert binary_hashes == [digest(php)]
        watched.append(report_path)
        for row in report['rows']:
            source = Path(row['native']['argv'][-1])
            assert row['passed'] and row['native']['exit'] == 0
            assert not row['native']['timeout'] and not row['native']['group_after']
            assert source.is_file() and digest(source) == row['source_sha256']
            assert row['id'] not in native
            native[row['id']] = (source, row)
            watched.append(source)
    selected = args.case or CASES
    assert len(set(selected)) == len(selected) and set(selected) <= native.keys()
    before = {str(p): digest(p) for p in watched}
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
        derived = {CASES[0]: 3, CASES[1]: 1, CASES[2]: 2, CASES[3]: 1}[name]
        rows.append({'id': name, 'source_sha256': digest(source),
                     'fixture_sha256': digest(fixture), 'conditions': len(checks),
                     'derived_guard_assertions': derived,
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
        'rows': rows, 'passed': passed, 'scope': 'Four original reached fronts and derived cursor guards; no native execution'},
        indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
