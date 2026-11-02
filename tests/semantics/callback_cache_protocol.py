#!/usr/bin/env python3
"""Reached persistent FCC owners, inline release and quiet FINAL retention."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import callback_cache_review_protocol as reviewed
from error_handler_run import recorded
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASES = (
    'tick-bound-closure-cache-and-ordered-unregister',
    'shutdown-bound-closure-cache-and-captured-final-observers',
    *reviewed.CASES,
)
AUTHOR_HELPERS = r'''
dec $cc_test_front(pstate, nat) : bool
def $cc_test_front(S, 0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
  -- if pcallcontext.RECEIVER = (n_receiver)
  -- if $object_name(S, n_receiver) = $ptascii("TickCacheReceiver")
  -- if $lookup(S.ENV, $ptascii("argument")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (POBJECT n_argument)
  -- if $lookup(S.ENV, $ptascii("captured")) = (n_captured)
  -- if S.STORE[n_captured] = DEFINED (POBJECT n_capture)
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV, $ptascii("calls")) = (n_calls)
  -- if S_global.STORE[n_calls] = DEFINED (PINT 0)
def $cc_test_front(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("TickCacheArgument")
  -- if $class_method_origin(S.CLASSES, porigin) = (pmethoddesc)
  -- if pmethoddesc.NAME = $ptascii("__destruct")
def $cc_test_front(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("TickCacheCapture")
  -- if $class_method_origin(S.CLASSES, porigin) = (pmethoddesc)
  -- if pmethoddesc.NAME = $ptascii("__destruct")
def $cc_test_front(S, 3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("TickCacheReceiver")
  -- if $class_method_origin(S.CLASSES, porigin) = (pmethoddesc)
  -- if pmethoddesc.NAME = $ptascii("__destruct")
def $cc_test_front(S, 4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
  -- if pcallcontext.RECEIVER = (n_receiver)
  -- if $object_name(S, n_receiver) = $ptascii("ShutdownCacheReceiver")
  -- if $lookup(S.ENV, $ptascii("snapshot")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (PINT 7)
def $cc_test_front(S, 5) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $shutdown_context_kind(S, pcallcontext)
  -- if $target_function(S, pcallcontext.TARGET) = (pfunction)
  -- if pfunction.NAME = $ptascii("last_callback")
def $cc_test_front(S, 6) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
  -- if $lookup(S.ENV, $ptascii("observe_cb")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (POBJECT n_weak)
  -- if $object_body(S.OBJECTS[n_weak]) = WEAKREFERENCE (n_callback)
  -- if $lookup(S.ENV, $ptascii("observe_recv")) = (n_receiver_cell)
  -- if S.STORE[n_receiver_cell] = DEFINED (POBJECT n_weak_receiver)
  -- if $object_body(S.OBJECTS[n_weak_receiver]) = WEAKREFERENCE (n_receiver)
def $cc_test_front(S, n) = false -- otherwise
dec $cc_test_seek(pstate, nat, nat) : pstate
def $cc_test_seek(S, n_stage, n) = S -- if $cc_test_front(S, n_stage)
def $cc_test_seek(S, n_stage, 0) = S -- if ~$cc_test_front(S, n_stage)
def $cc_test_seek(S, n_stage, n) = $cc_test_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$cc_test_front(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $cc_test_seek(S, n_stage, n) = S
  -- if ~$cc_test_front(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''
HELPERS = AUTHOR_HELPERS + reviewed.HELPERS


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def conditions(name, program, source, expected_stdout):
    if name in reviewed.CASES:
        return reviewed.conditions(name, program, source, expected_stdout)
    encoded_path = base64.b64encode(str(source).encode()).decode()
    checks = [f'S_initial = $php_run({program}, 0, "{encoded_path}")',
              'S_initial.COMPLETION = BUDGET']

    def reach(label, prior, stage):
        checks.extend([f'{label}_found = $cc_test_seek({prior}, {stage}, 4000)',
                       fr'{label}_found.COMPLETION = NORMAL \/ {label}_found.COMPLETION = BUDGET',
                       f'{label} = {label}_found[.COMPLETION = NORMAL]',
                       f'$cc_test_front({label}, {stage})',
                       f'$call_descriptors_valid({label})',
                       f'$heap_valid($heap_graph({label}))'])

    lines = source.read_bytes().splitlines()
    matches = [i for i, line in enumerate(lines, 1) if b'echo "P:"' in line]
    assert len(matches) == 1
    line = matches[0]
    checks += [
        f'S_registered_found = $cc_review_seek(S_initial, 0, {line}, 4000)',
        r'S_registered_found.COMPLETION = NORMAL \/ S_registered_found.COMPLETION = BUDGET',
        'S_registered = S_registered_found[.COMPLETION = NORMAL]',
        f'$cc_review_front(S_registered, 0, {line})',
        '$call_descriptors_valid(S_registered)', '$heap_valid($heap_graph(S_registered))',
    ]
    shutdown = name == CASES[1]
    if shutdown:
        checks += [
            'S_registered.SHUTDOWN.ENTRIES = [pshutdownentry, pshutdownentry_last]',
            'pshutdownentry.TARGET = CLOSURE_TARGET n_closure',
            'pshutdownentry.CACHEOBJECT = (n_receiver)',
            'pshutdownentry.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_closure))]',
            '$object_name(S_registered, n_receiver) = $ptascii("ShutdownCacheReceiver")',
        ]
    else:
        checks += [
            'S_registered.TICKENTRIES = [ptickentry]',
            'ptickentry.ENTRY = pshutdownentry',
            'pshutdownentry.TARGET = CLOSURE_TARGET n_closure',
            'pshutdownentry.CACHEOBJECT = (n_receiver)',
            'pshutdownentry.ARGS = [POBJECT n_argument]',
            '$object_body(S_registered.OBJECTS[n_closure]) = REALCLOSURE porigin_function ([DIRECT (POBJECT n_capture)]) eps',
            '$object_name(S_registered, n_receiver) = $ptascii("TickCacheReceiver")',
            '$object_name(S_registered, n_capture) = $ptascii("TickCacheCapture")',
            '$object_name(S_registered, n_argument) = $ptascii("TickCacheArgument")',
        ]
    checks += [
        '$heap_owners($heap_prune($heap_graph(S_registered)), HOBJECT n_closure) = 1',
        '$heap_owners($heap_prune($heap_graph(S_registered)), HOBJECT n_receiver) = 2',
    ]
    if shutdown:
        reach('S_body', 'S_registered', 4)
        checks += [
            'S_body.CURRENT = (pcallcontext_body)',
            'pcallcontext_body.TARGET = CLOSURE_TARGET n_closure',
            'pcallcontext_body.INSTANCE = (n_closure)',
            '$shutdown_context_valid(S_body, pcallcontext_body)',
            '$heap_owners($heap_prune($heap_graph(S_body)), HOBJECT n_closure) = 2',
            '$heap_owners($heap_prune($heap_graph(S_body)), HOBJECT n_receiver) = 2',
        ]
        reach('S_last', 'S_body', 5)
        checks += [
            'S_last.SHUTDOWN.ENTRIES = [pshutdownentry, pshutdownentry_last]',
            '$heap_owners($heap_prune($heap_graph(S_last)), HOBJECT n_closure) = 1',
            '$heap_owners($heap_prune($heap_graph(S_last)), HOBJECT n_receiver) = 2',
        ]
        reach('S_final', 'S_last', 6)
        checks += [
            'S_final.SHUTDOWN.PHASE = SHUTDOWN_DONE',
            'S_final.SHUTDOWN.ENTRIES = [pshutdownentry, pshutdownentry_last]',
            'S_final.CURRENT = (pcallcontext_final)',
            'pcallcontext_final.TARGET = CLOSURE_TARGET n_finalizer',
            'n_finalizer =/= n_closure',
            '$lookup(S_final.ENV, $ptascii("observe_cb")) = (n_observer_cell)',
            'S_final.STORE[n_observer_cell] = DEFINED (POBJECT n_observer)',
            '$object_body(S_final.OBJECTS[n_observer]) = WEAKREFERENCE (n_closure)',
            '$lookup(S_final.ENV, $ptascii("observe_recv")) = (n_receiver_cell)',
            'S_final.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver_observer)',
            '$object_body(S_final.OBJECTS[n_receiver_observer]) = WEAKREFERENCE (n_receiver)',
            '$heap_owners($heap_prune($heap_graph(S_final)), HOBJECT n_closure) = 1',
            '$heap_owners($heap_prune($heap_graph(S_final)), HOBJECT n_receiver) = 2',
        ]
        last = 'S_final'
    else:
        checks += [
            '$heap_owners($heap_prune($heap_graph(S_registered)), HOBJECT n_capture) = 1',
            '$heap_owners($heap_prune($heap_graph(S_registered)), HOBJECT n_argument) = 1',
        ]
        reach('S_body', 'S_registered', 0)
        checks += [
            'S_body.CURRENT = (pcallcontext_body)',
            'pcallcontext_body.TARGET = CLOSURE_TARGET n_closure',
            'pcallcontext_body.INSTANCE = (n_closure)',
            '$tick_context_valid(S_body, pcallcontext_body)',
            '$heap_owners($heap_prune($heap_graph(S_body)), HOBJECT n_closure) = 2',
            '$heap_owners($heap_prune($heap_graph(S_body)), HOBJECT n_receiver) = 2',
            '$heap_owners($heap_prune($heap_graph(S_body)), HOBJECT n_capture) = 2',
            '$heap_owners($heap_prune($heap_graph(S_body)), HOBJECT n_argument) = 2',
        ]
        reach('S_argument', 'S_body', 1)
        checks += [
            'S_argument.TICKENTRIES = eps',
            'S_argument.CURRENT = (pcallcontext_argument)',
            'pcallcontext_argument.TARGET = METHOD_TARGET n_argument porigin_argument',
            '$heap_owners($heap_prune($heap_graph(S_argument)), HOBJECT n_closure) = 2',
            '$heap_owners($heap_prune($heap_graph(S_argument)), HOBJECT n_receiver) = 2',
            '$heap_owners($heap_prune($heap_graph(S_argument)), HOBJECT n_capture) = 1',
            'S_one = $drive_steps(S_argument, 1)', 'S_one.COMPLETION = BUDGET',
            '$drive_steps(S_one[.COMPLETION = NORMAL], 1) = $drive_steps(S_argument, 2)',
        ]
        reach('S_capture', 'S_argument', 2)
        checks += [
            '~((HOBJECT n_argument) <- S_capture.ALLOCATIONS)',
            '~((HOBJECT n_closure) <- S_capture.ALLOCATIONS)',
            '$heap_owners($heap_prune($heap_graph(S_capture)), HOBJECT n_receiver) = 1',
        ]
        reach('S_receiver', 'S_capture', 3)
        checks += [
            '~((HOBJECT n_argument) <- S_receiver.ALLOCATIONS)',
            '~((HOBJECT n_capture) <- S_receiver.ALLOCATIONS)',
            '~((HOBJECT n_closure) <- S_receiver.ALLOCATIONS)',
            'S_receiver.CURRENT = (pcallcontext_receiver)',
            'pcallcontext_receiver.TARGET = METHOD_TARGET n_receiver porigin_receiver',
        ]
        last = 'S_receiver'
    checks += [
        f'S_done = $drive_steps({last}, 4000)', 'S_done.COMPLETION = NORMAL',
        'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.TICKENTRIES = eps',
        'S_done.DESTRUCTION.FRAMES = eps', 'S_done.DESTRUCTION.RELEASES = eps',
        'S_done.DESTRUCTION.CALLS = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$cc_review_output(S_done.EVENTS) = [' + ','.join(map(str, expected_stdout)) + ']',
    ]
    if shutdown:
        checks += [
            'S_done.SHUTDOWN.ENTRIES = [pshutdownentry, pshutdownentry_last]',
            'S_done.OUTPUTBUFFERS = eps',
            '~((HOBJECT n_observer) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_receiver_observer) <- S_done.ALLOCATIONS)',
        ]
    else:
        checks += [f'~((HOBJECT {node}) <- S_done.ALLOCATIONS)' for node in ('n_argument','n_capture','n_closure','n_receiver')]
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
                   '115-closure-compiler.watsup', '117-arrow-compiler.watsup',
                   '39-ownership.watsup', '231-shutdown-functions.watsup',
                   '247-handler-callable-consumers.watsup', '277-autoload.watsup',
                   '393-ticks.watsup', '395-output-handlers.watsup',
                   '142-method-runtime.watsup', '379-sensitive-parameters.watsup',
                   '301-cycle-collection.watsup',
                   '257-request-destructors.watsup', '270-eager-destructors.watsup',
                   '440-builtin-function-attributes.watsup',
                   '443-deprecated-closure-invoke.watsup')],
               ROOT / 'spec/semantics/442-deprecated-api-callbacks.watsup',
               ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
               ROOT / '_build/default/adapter/main.exe', ROOT / 'frontend/worker.php',
               ROOT / '.tools/php-file.so', php]
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    native = {}
    for report_path in args.native_report:
        report = json.loads(report_path.read_bytes())
        assert report['profile'] == profile
        assert report['passed'] or args.case is not None
        binary_hashes = [value for key, value in report['inputs'].items()
                         if key.endswith('.tools/php/bin/php')]
        assert binary_hashes == [digest(php)]
        watched.append(report_path)
        for row in report['rows']:
            if args.case and row['id'] not in args.case:
                continue
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
                     'derived_guard_assertions': reviewed.DERIVED.get(name, 0),
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
        'scope': 'Reached persistent callback caches and borrowed calls; inline retirement and quiet shutdown through FINAL; no late-free policy or native execution'}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
