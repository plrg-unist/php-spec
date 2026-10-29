#!/usr/bin/env python3
"""Check reached explicit-wrapper reference cells and separate call owners."""
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
    'invoke-reference-slot-live-through-both-warnings',
    'invoke-body-return-retires-raw-argument-before-outer-receiver',
)
HELPERS = r'''
dec $ci_review_front(pstate, nat) : bool
def $ci_review_front(S, 0) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CLOSURE_INVOKE_INNER ptask
  -- if perrorcall.LEVEL = 8192
def $ci_review_front(S, 1) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CLOSURE_INVOKE_ENTER ptask
  -- if perrorcall.LEVEL = 16384
def $ci_review_front(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
  -- if pcallcontext.WRAPPER =/= eps
def $ci_review_front(S, 3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("ReturnToken")
def $ci_review_front(S, 4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("ReturnCarrier")
def $ci_review_front(S, n) = false -- otherwise
dec $ci_review_seek(pstate, nat, nat) : pstate
def $ci_review_seek(S, n_stage, n) = S -- if $ci_review_front(S, n_stage)
def $ci_review_seek(S, n_stage, 0) = S -- if ~$ci_review_front(S, n_stage)
def $ci_review_seek(S, n_stage, n) = $ci_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$ci_review_front(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $ci_review_seek(S, n_stage, n) = S
  -- if ~$ci_review_front(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $ci_review_output(pevent*) : ptbytes
dec $ci_review_is_output(pevent) : bool
def $ci_review_output(eps) = eps
def $ci_review_output((OUTPUT ptbytes) :: pevent_tail*) = ptbytes ++ $ci_review_output(pevent_tail*)
def $ci_review_output(pevent :: pevent_tail*) = $ci_review_output(pevent_tail*) -- if ~$ci_review_is_output(pevent)
def $ci_review_is_output(OUTPUT ptbytes) = true
def $ci_review_is_output(pevent) = false -- otherwise
'''


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def conditions(name, program, source, expected_stdout):
    checks = [f'S_initial = $php_run({program}, 0, "{base64.b64encode(str(source).encode()).decode()}")',
              'S_initial.COMPLETION = BUDGET']

    def reach(label, prior, stage):
        checks.extend([f'{label}_found = $ci_review_seek({prior}, {stage}, 3000)',
                       fr'{label}_found.COMPLETION = NORMAL \/ {label}_found.COMPLETION = BUDGET',
                       f'{label} = {label}_found[.COMPLETION = NORMAL]',
                       f'$ci_review_front({label}, {stage})',
                       f'$call_descriptors_valid({label})',
                       f'$heap_valid($heap_graph({label}))'])

    reach('S_outer', 'S_initial', 0)
    checks += [
        'S_outer.TODO = (ERROR_HANDLER_INVOKE perrorcall_outer) :: ptask_tail*',
        'perrorcall_outer.RESUME = CLOSURE_INVOKE_INNER ptask_source',
        '$closure_invoke_source(ptask_source) = ((CLOSURE_TARGET n_closure, pnamedargs, porigin, z))',
        'ptask_source = CALL_ARGS pcalltarget eps n_count poperand* (porigin) z',
        '$closure_invoke_valid(S_outer, ptask_source)',
        'S_outer.CURRENT = eps', 'S_outer.FRAMES = eps',
    ]
    if name == CASES[0]:
        checks += [
            'pnamedargs.SLOTS = (NAMED_SENT (REFERENCE n_cell)) :: pnamedslot_tail*',
            'S_outer.STORE[n_cell] = DEFINED (PINT 7)',
        ]
        reach('S_inner', 'S_outer', 1)
        checks += [
            'S_inner.TODO = (ERROR_HANDLER_INVOKE perrorcall_inner) :: ptask_inner_tail*',
            'perrorcall_inner.RESUME = CLOSURE_INVOKE_ENTER ptask_source',
            '$closure_invoke_valid(S_inner, ptask_source)',
            'S_inner.CURRENT = eps', 'S_inner.FRAMES = eps',
            'S_inner.STORE[n_cell] = DEFINED (PINT 17)',
            '$heap_owners($heap_prune($heap_graph(S_inner)), HOBJECT n_closure) = 1',
            '~$closure_invoke_valid(S_inner, CALL_ARGS pcalltarget eps n_count poperand* (porigin) $(z + 1))',
        ]
        reach('S_body', 'S_inner', 2)
        checks += [
            'S_body.CURRENT = (pcallcontext)',
            'pcallcontext.TARGET = CLOSURE_TARGET n_closure',
            'pcallcontext.INSTANCE = (n_closure)',
            'pcallcontext.WRAPPER = (pnamedargs)',
            '$lookup(S_body.ENV, $ptascii("value")) = (n_cell)',
            'S_body.STORE[n_cell] = DEFINED (PINT 23)',
            '$heap_owners($heap_prune($heap_graph(S_body)), HOBJECT n_closure) = 2',
        ]
        last = 'S_body'
    else:
        checks += [
            'pnamedargs.SLOTS = [NAMED_SENT (KNOWN (POBJECT n_token))]',
            '$target_receiver(S_outer, CLOSURE_TARGET n_closure) = (n_receiver)',
            '$heap_owners($heap_prune($heap_graph(S_outer)), HOBJECT n_closure) = 2',
            '$heap_owners($heap_prune($heap_graph(S_outer)), HOBJECT n_token) = 2',
        ]
        reach('S_inner', 'S_outer', 1)
        checks += [
            'S_inner.TODO = (ERROR_HANDLER_INVOKE perrorcall_inner) :: ptask_inner_tail*',
            'perrorcall_inner.RESUME = CLOSURE_INVOKE_ENTER ptask_source',
            '$closure_invoke_valid(S_inner, ptask_source)',
            'S_inner.CURRENT = eps', 'S_inner.FRAMES = eps',
            '$heap_owners($heap_prune($heap_graph(S_inner)), HOBJECT n_closure) = 1',
            '$heap_owners($heap_prune($heap_graph(S_inner)), HOBJECT n_token) = 1',
            '$heap_owners($heap_prune($heap_graph(S_inner)), HOBJECT n_receiver) = 1',
            '~$closure_invoke_valid(S_inner, CALL_ARGS pcalltarget eps n_count poperand* (porigin) $(z + 1))',
        ]
        reach('S_body', 'S_inner', 2)
        checks += [
            'S_body.CURRENT = (pcallcontext)',
            'pcallcontext.TARGET = CLOSURE_TARGET n_closure',
            'pcallcontext.INSTANCE = (n_closure)',
            'pcallcontext.WRAPPER = (pnamedargs)',
            '$heap_owners($heap_prune($heap_graph(S_body)), HOBJECT n_closure) = 2',
            '$heap_owners($heap_prune($heap_graph(S_body)), HOBJECT n_token) = 2',
            '$heap_owners($heap_prune($heap_graph(S_body)), HOBJECT n_receiver) = 1',
        ]
        reach('S_token', 'S_body', 3)
        checks += [
            'S_token.CURRENT = (pcallcontext_token)',
            'pcallcontext_token.TARGET = METHOD_TARGET n_token porigin_token',
            '$heap_owners($heap_prune($heap_graph(S_token)), HOBJECT n_closure) = 1',
            '$heap_owners($heap_prune($heap_graph(S_token)), HOBJECT n_receiver) = 1',
        ]
        reach('S_receiver', 'S_token', 4)
        checks += [
            'S_receiver.CURRENT = (pcallcontext_receiver)',
            'pcallcontext_receiver.TARGET = METHOD_TARGET n_receiver porigin_receiver',
            '~((HOBJECT n_closure) <- S_receiver.ALLOCATIONS)',
            '~((HOBJECT n_token) <- S_receiver.ALLOCATIONS)',
        ]
        last = 'S_receiver'
    checks += [f'S_done = $drive_steps({last}, 3000)',
               'S_done.COMPLETION = NORMAL',
               '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
               '$ci_review_output(S_done.EVENTS) = [' + ','.join(map(str, expected_stdout)) + ']']
    if name == CASES[0]:
        checks += ['S_chunk = $drive_steps(S_body, 1)',
                   'S_chunk.COMPLETION = BUDGET',
                   'S_resumed = $drive_steps(S_chunk[.COMPLETION = NORMAL], 3000)',
                   'S_resumed = S_done']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', action='append', required=True, type=Path)
    parser.add_argument('--case', choices=CASES, action='append')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    affinity = sorted(os.sched_getaffinity(0))
    assert len(affinity) == 1 and affinity[0] in range(1, 6)
    assert not subprocess.check_output(['git', 'status', '--porcelain=v1'], cwd=ROOT)
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    php = ROOT / '.tools/php/bin/php'
    watched = [Path(__file__), ROOT / 'tests/semantics/error_handler_run.py',
               ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/profile.json',
               ROOT / 'spec/semantics/modules.json', ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
               ROOT / '_build/default/adapter/main.exe', ROOT / 'frontend/worker.php',
               ROOT / '.tools/php-file.so', php]
    watched += [ROOT / 'spec/semantics' / name for name in (
        '30-storage.watsup', '79-call-frames.watsup', '80-call-control.watsup',
        '83-call-traces.watsup', '105-named-arguments.watsup', '108-call-unpack.watsup',
        '257-request-destructors.watsup', '440-builtin-function-attributes.watsup',
        '443-deprecated-closure-invoke.watsup')]
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    native = {}
    for report_path in args.native_report:
        report = json.loads(report_path.read_bytes())
        assert report['passed'] and report['profile'] == profile
        assert [value for key, value in report['inputs'].items()
                if key.endswith('.tools/php/bin/php')] == [digest(php)]
        watched.append(report_path)
        for row in report['rows']:
            assert row['passed'] and row['native']['exit'] == 0
            assert not row['native']['timeout'] and not row['native']['group_after']
            assert row['native']['interruption'] is None
            if row['id'] not in CASES:
                continue
            source = Path(row['native']['argv'][-1])
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
            '  -- if ' + condition + '\n' for condition in checks))
        before[str(fixture)] = digest(fixture)
        process = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                            '--sl', *map(str, modules), str(fixture)], out / (name + '-model'), 300)
        passed = (process['exit'] == 0 and not process['timeout'] and process['interruption'] is None
                  and not process['group_after']
                  and (out / (name + '-model.stdout')).read_bytes() == b'true\n'
                  and not (out / (name + '-model.stderr')).read_bytes())
        rows.append({'id': name, 'source_sha256': digest(source),
                     'fixture_sha256': digest(fixture), 'conditions': len(checks),
                     'derived_guard_assertions': 1, 'model': process, 'passed': passed})
        print(name, passed, flush=True)
        if not passed:
            break
    assert before == {path: digest(path) for path in before}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    assert not subprocess.check_output(['git', 'status', '--porcelain=v1'], cwd=ROOT)
    passed = len(rows) == len(selected) and all(row['passed'] for row in rows)
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'profile': profile,
        'inputs': before, 'selection': selected, 'affinity': affinity,
        'rows': rows, 'passed': passed,
        'scope': 'Two independent source groups with reached owner/cell checks and derived line guards; no native execution'}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
