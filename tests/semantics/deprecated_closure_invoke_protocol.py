#!/usr/bin/env python3
"""Check reached raw Closure wrapper phases and ordered preentry cleanup."""
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
    'explicit-wrapper-positional-before-type-reception',
    'explicit-wrapper-outer-throw-releases-raw-owners',
    'explicit-wrapper-required-named-hole-before-error',
)
HELPERS = r'''
dec $ci_test_front(pstate, nat) : bool
def $ci_test_front(S, 0) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CLOSURE_INVOKE_INNER ptask_source
  -- if perrorcall.LEVEL = 8192
def $ci_test_front(S, 1) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CLOSURE_INVOKE_ENTER ptask_source
  -- if perrorcall.LEVEL = 16384
def $ci_test_front(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.WRAPPER =/= eps
  -- if S.TODO = [TYPE_RECEIVE pcallcontext.FUNCTION 0]
def $ci_test_front(S, 3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.WRAPPER =/= eps
  -- if S.TODO = [NAMED_PREFLIGHT pcallcontext.FUNCTION 0]
def $ci_test_front(S, 4) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CLOSURE_INVOKE_INNER ptask_source
def $ci_test_front(S, n) = false -- otherwise
dec $ci_test_seek(pstate, nat, nat) : pstate
def $ci_test_seek(S, n_stage, n) = S -- if $ci_test_front(S, n_stage)
def $ci_test_seek(S, n_stage, 0) = S -- if ~$ci_test_front(S, n_stage)
def $ci_test_seek(S, n_stage, n) = $ci_test_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$ci_test_front(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $ci_test_seek(S, n_stage, n) = S
  -- if ~$ci_test_front(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $ci_test_output(pevent*) : ptbytes
dec $ci_test_is_output(pevent) : bool
def $ci_test_output(eps) = eps
def $ci_test_output((OUTPUT ptbytes) :: pevent_tail*) = ptbytes ++ $ci_test_output(pevent_tail*)
def $ci_test_output(pevent :: pevent_tail*) = $ci_test_output(pevent_tail*) -- if ~$ci_test_is_output(pevent)
def $ci_test_is_output(OUTPUT ptbytes) = true
def $ci_test_is_output(pevent) = false -- otherwise
'''


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def conditions(name, program, source, expected_stdout):
    checks = [f'S_initial = $php_run({program}, 0, "{base64.b64encode(str(source).encode()).decode()}")',
              'S_initial.COMPLETION = BUDGET']

    def reach(label, prior, stage):
        checks.extend([f'{label}_found = $ci_test_seek({prior}, {stage}, 4000)',
                       fr'{label}_found.COMPLETION = NORMAL \/ {label}_found.COMPLETION = BUDGET',
                       f'{label} = {label}_found[.COMPLETION = NORMAL]',
                       f'$ci_test_front({label}, {stage})',
                       f'$call_descriptors_valid({label})',
                       f'$heap_valid($heap_graph({label}))'])

    reach('S_outer', 'S_initial', 0)
    checks += [
        'S_outer.TODO = (ERROR_HANDLER_INVOKE perrorcall_outer) :: ptask_tail*',
        'perrorcall_outer.RESUME = CLOSURE_INVOKE_INNER ptask_source',
        '$closure_invoke_source(ptask_source) = ((CLOSURE_TARGET n_closure, pnamedargs_raw, porigin_site, z_line))',
        '$closure_invoke_valid(S_outer, ptask_source)',
        'S_outer.CURRENT = eps', 'S_outer.FRAMES = eps',
        '$heap_owners($heap_prune($heap_graph(S_outer)), HOBJECT n_closure) = 2',
        '~$call_task_valid(S_outer, CLOSURE_INVOKE_INNER (CLOSURE_INVOKE_ENTER ptask_source))',
    ]
    if name == CASES[0]:
        checks += [
            'ptask_source = CALL_ARGS pcalltarget eps n_sent poperand* (porigin_site) z_line',
            'poperand* = [KNOWN (PSTRING ($ptascii("bad")))]',
            '~$closure_invoke_valid(S_outer, CALL_ARGS pcalltarget eps n_sent poperand* (porigin_site) $(z_line + 1))',
        ]
        reach('S_inner', 'S_outer', 1)
        checks += [
            'S_inner.TODO = (ERROR_HANDLER_INVOKE perrorcall_inner) :: ptask_tail*',
            'perrorcall_inner.RESUME = CLOSURE_INVOKE_ENTER ptask_source',
            'S_inner.CURRENT = eps', 'S_inner.FRAMES = eps',
            '$closure_invoke_valid(S_inner, ptask_source)',
            '$lookup(S_inner.ENV, $ptascii("arg")) = (n_arg)',
            'S_inner.STORE[n_arg] = DEFINED (PINT 8)',
            'poperand* = [KNOWN (PSTRING ($ptascii("bad")))]',
        ]
        reach('S_entered', 'S_inner', 2)
        checks += [
            'S_entered.CURRENT = (pcallcontext)',
            'pcallcontext.TARGET = CLOSURE_TARGET n_closure',
            'pcallcontext.INSTANCE = (n_closure)',
            'pcallcontext.WRAPPER = (pnamedargs_raw)',
            '$heap_owners($heap_prune($heap_graph(S_entered)), HOBJECT n_closure) = 3',
            '$lookup(S_entered.ENV, $ptascii("value")) = (n_value)',
            'S_entered.STORE[n_value] = DEFINED (PSTRING ($ptascii("bad")))',
            '$target_function(S_entered, pcallcontext.TARGET) = (pfunction)',
            '$closure_invoke_received(S_entered, pfunction)',
            '~$closure_invoke_received(S_entered[.CURRENT = (pcallcontext[.WRAPPER = eps])], pfunction)',
        ]
        last = 'S_entered'
    elif name == CASES[1]:
        reach('S_throw', 'S_outer', 4)
        checks += [
            'S_throw.TODO = (THROW_SEARCH n_saved) :: (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_tail*',
            'perrorcall_throw.RESUME = CLOSURE_INVOKE_INNER ptask_source',
            'pnamedargs_raw.SLOTS = [NAMED_SENT (KNOWN (POBJECT n_token))]',
            '$target_receiver(S_throw, CLOSURE_TARGET n_closure) = (n_receiver)',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_closure) = 1',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_receiver) = 1',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_token) = 1',
            '$throwable_live(S_throw, n_saved)',
        ]
        last = 'S_throw'
    else:
        checks += [
            'pnamedargs_raw.SLOTS = [NAMED_HOLE, NAMED_SENT (KNOWN (PINT 2))]',
            '$lookup(S_outer.ENV, $ptascii("first")) = eps',
            '$lookup(S_outer.ENV, $ptascii("second")) = eps',
        ]
        reach('S_inner', 'S_outer', 1)
        checks += [
            'S_inner.TODO = (ERROR_HANDLER_INVOKE perrorcall_inner) :: ptask_tail*',
            'perrorcall_inner.RESUME = CLOSURE_INVOKE_ENTER ptask_source',
            'S_inner.CURRENT = eps', 'S_inner.FRAMES = eps',
            '$closure_invoke_source(ptask_source) = ((CLOSURE_TARGET n_closure, pnamedargs_raw, porigin_site, z_line))',
        ]
        reach('S_entered', 'S_inner', 3)
        checks += [
            'S_entered.CURRENT = (pcallcontext)',
            'pcallcontext.TARGET = CLOSURE_TARGET n_closure',
            'pcallcontext.WRAPPER = (pnamedargs_raw)',
            'pcallcontext.HOLES = [0]',
            '~$named_defined(S_entered, $ptascii("first"))',
            '$named_defined(S_entered, $ptascii("second"))',
            '$heap_owners($heap_prune($heap_graph(S_entered)), HOBJECT n_closure) = 3',
        ]
        last = 'S_entered'
    checks += [f'S_done = $drive_steps({last}, 4000)', 'S_done.COMPLETION = NORMAL',
               'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
               '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
               '$ci_test_output(S_done.EVENTS) = [' + ','.join(map(str, expected_stdout)) + ']']
    if name == CASES[1]:
        checks += ['~((HOBJECT n_closure) <- S_done.ALLOCATIONS)',
                   '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
                   '~((HOBJECT n_token) <- S_done.ALLOCATIONS)']
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
               *[ROOT / ('spec/semantics/' + name) for name in (
                   '79-call-frames.watsup', '80-call-control.watsup', '83-call-traces.watsup',
                   '105-named-arguments.watsup', '108-call-unpack.watsup',
                   '257-request-destructors.watsup', '440-builtin-function-attributes.watsup',
                   '443-deprecated-closure-invoke.watsup')],
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
                     'derived_guard_assertions': {CASES[0]: 3, CASES[1]: 1, CASES[2]: 1}[name],
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
        'scope': 'Three reached explicit-wrapper fronts and derived cursor guards; no native execution'}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
