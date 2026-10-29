#!/usr/bin/env python3
"""Check reached raw-argument, unused-return and outer-Closure retirement."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import deprecated_closure_return_review_protocol as reviewed
from error_handler_run import recorded
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASES = (
    'invoke-unused-owning-result-retires-between-raw-argument-and-receiver',
    'invoke-unused-result-destructor-throw-keeps-outer-owner-and-caller-trace',
    *reviewed.CASES,
)
AUTHOR_HELPERS = r'''
dec $cr_test_front(pstate, ptbytes) : bool
def $cr_test_front(S, ptbytes) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = ptbytes
  -- if $class_method_origin(S.CLASSES, porigin) = (pmethoddesc)
  -- if pmethoddesc.NAME = $ptascii("__destruct")
def $cr_test_front(S, ptbytes) = false -- otherwise
dec $cr_test_seek(pstate, ptbytes, nat) : pstate
def $cr_test_seek(S, ptbytes, n) = S -- if $cr_test_front(S, ptbytes)
def $cr_test_seek(S, ptbytes, 0) = S -- if ~$cr_test_front(S, ptbytes)
def $cr_test_seek(S, ptbytes, n) = $cr_test_seek($drive_steps(S[.COMPLETION = NORMAL], 1), ptbytes, $nabs($(n - 1)))
  -- if ~$cr_test_front(S, ptbytes) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $cr_test_seek(S, ptbytes, n) = S
  -- if ~$cr_test_front(S, ptbytes) /\ $(n > 0)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''
HELPERS = AUTHOR_HELPERS + reviewed.HELPERS


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def conditions(name, program, source, expected_stdout):
    if name in reviewed.CASES:
        return reviewed.conditions(name, program, source, expected_stdout)
    throwing = name == CASES[1]
    token_class, value_class, receiver_class = (
        ('ThrowToken', 'ThrowValue', 'ThrowCarrier') if throwing else
        ('ResultToken', 'ResultValue', 'ResultCarrier'))
    encoded_path = base64.b64encode(str(source).encode()).decode()
    checks = [f'S_initial = $php_run({program}, 0, "{encoded_path}")',
              'S_initial.COMPLETION = BUDGET']

    def reach(label, prior, class_name):
        stage = f'$ptascii("{class_name}")'
        checks.extend([f'{label}_found = $cr_test_seek({prior}, {stage}, 4000)',
                       fr'{label}_found.COMPLETION = NORMAL \/ {label}_found.COMPLETION = BUDGET',
                       f'{label} = {label}_found[.COMPLETION = NORMAL]',
                       f'$cr_test_front({label}, {stage})',
                       f'$call_descriptors_valid({label})',
                       f'$heap_valid($heap_graph({label}))'])

    reach('S_token', 'S_initial', token_class)
    checks += [
        'S_token.CURRENT = (pcallcontext_token)',
        'pcallcontext_token.TARGET = METHOD_TARGET n_token porigin_token',
        'S_token.DESTRUCTION.RELEASES = [pdestructionrelease_token]',
        'pdestructionrelease_token.JOBS = [DESTRUCTION_VALUE (HOBJECT n_value), DESTRUCTION_VALUE (HOBJECT n_closure)]',
        f'$object_name(S_token, n_value) = $ptascii("{value_class}")',
        '$target_receiver(S_token, CLOSURE_TARGET n_closure) = (n_receiver)',
        f'$object_name(S_token, n_receiver) = $ptascii("{receiver_class}")',
        'S_token.DESTRUCTION.FRAMES = [pdestructionframe_return]',
        'pdestructionframe_return.VALUE = KNOWN PNULL',
        'pdestructionframe_return.PENDING = eps',
        'pdestructionframe_return.CALLER = eps',
        '$heap_owners($heap_prune($heap_graph(S_token)), HOBJECT n_value) = 1',
        '$heap_owners($heap_prune($heap_graph(S_token)), HOBJECT n_closure) = 1',
        '$heap_owners($heap_prune($heap_graph(S_token)), HOBJECT n_receiver) = 1',
        'S_one = $drive_steps(S_token, 1)',
        'S_one.COMPLETION = BUDGET',
        '$drive_steps(S_one[.COMPLETION = NORMAL], 1) = $drive_steps(S_token, 2)',
    ]
    reach('S_value', 'S_token', value_class)
    checks += [
        'S_value.CURRENT = (pcallcontext_value)',
        'pcallcontext_value.TARGET = METHOD_TARGET n_value porigin_value',
        '~((HOBJECT n_token) <- S_value.ALLOCATIONS)',
        'S_value.DESTRUCTION.RELEASES = [pdestructionrelease_value]',
        'pdestructionrelease_value.JOBS = [DESTRUCTION_VALUE (HOBJECT n_closure)]',
        'S_value.DESTRUCTION.FRAMES = [pdestructionframe_return]',
        '$heap_owners($heap_prune($heap_graph(S_value)), HOBJECT n_closure) = 1',
        '$heap_owners($heap_prune($heap_graph(S_value)), HOBJECT n_receiver) = 1',
    ]
    if throwing:
        checks += [
            'S_value.GLOBALTABLE = (psymboltable_globals)',
            '$lookup(psymboltable_globals.ENV, $ptascii("saved")) = (n_saved_cell)',
            'S_value.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)',
        ]
    reach('S_receiver', 'S_value', receiver_class)
    checks += [
        'S_receiver.CURRENT = (pcallcontext_receiver)',
        'pcallcontext_receiver.TARGET = METHOD_TARGET n_receiver porigin_receiver',
        '~((HOBJECT n_token) <- S_receiver.ALLOCATIONS)',
        '~((HOBJECT n_value) <- S_receiver.ALLOCATIONS)',
        '~((HOBJECT n_closure) <- S_receiver.ALLOCATIONS)',
    ]
    if throwing:
        checks += [
            'S_receiver.DESTRUCTION.FRAMES = [pdestructionframe_pending]',
            'pdestructionframe_pending.VALUE = KNOWN PNULL',
            'pdestructionframe_pending.PENDING = (n_saved)',
            'pdestructionframe_pending.FUNCTION = pdestructionframe_return.FUNCTION',
            '$throwable_live(S_receiver, n_saved)',
        ]
    else:
        checks += ['S_receiver.DESTRUCTION.FRAMES = [pdestructionframe_return]']
    checks += [
        'S_done = $drive_steps(S_receiver, 4000)',
        'S_done.COMPLETION = NORMAL',
        'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
        'S_done.DESTRUCTION.FRAMES = eps',
        'S_done.DESTRUCTION.RELEASES = eps',
        'S_done.DESTRUCTION.CALLS = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$cr_review_output(S_done.EVENTS) = [' + ','.join(map(str, expected_stdout)) + ']',
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
    watched = [Path(__file__), ROOT / 'tests/semantics/error_handler_run.py',
               ROOT / 'tests/semantics/recorded_worker.py', Path(reviewed.__file__), ROOT / 'tests/semantics/profile.json',
               ROOT / 'spec/semantics/modules.json', ROOT / 'spec/semantics/30-storage.watsup',
               *[ROOT / ('spec/semantics/' + name) for name in (
                   '79-call-frames.watsup', '80-call-control.watsup', '83-call-traces.watsup',
                   '105-named-arguments.watsup', '108-call-unpack.watsup',
                   '142-method-runtime.watsup', '379-sensitive-parameters.watsup',
                   '301-cycle-collection.watsup',
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
                     'derived_guard_assertions': 0,
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
        'scope': 'Reached explicit-wrapper return retirement and supplied-throw/alias owners; no native execution'}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
