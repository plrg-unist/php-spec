#!/usr/bin/env python3
"""Reached capture cells, selected scope and warning-time Closure owners."""
import argparse
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess

import deprecated_closure_expression_review_protocol as reviewed
from error_handler_run import recorded
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASES = (
    'closure-expression-reference-capture-through-both-vm-warnings',
    'arrow-expression-multiline-static-name-and-used-result',
    'closure-expression-owned-assert-api-selection',
    *reviewed.CASES,
)
AUTHOR_HELPERS = r'''
dec $ce_test_front(pstate, nat) : bool
def $ce_test_front(S, 0) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = NODISCARD_RESUME pframe
  -- if perrorcall.LEVEL = 16384
def $ce_test_front(S, 1) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = NODISCARD_RESUME pframe
  -- if perrorcall.LEVEL = 512
def $ce_test_front(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
  -- if $lookup(S.ENV, $ptascii("value")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (PINT 7)
def $ce_test_front(S, 3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
  -- if $lookup(S.ENV, $ptascii("initial")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (PINT 3)
def $ce_test_front(S, 4) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = API_CALLBACK_SEND papiargcursor
  -- if papiargcursor.CALL = API_ASSERT passertcall
  -- if perrorcall.LEVEL = 16384
def $ce_test_front(S, 5) = true
  -- if S.TODO = (API_CALLBACK_SEND papiargcursor) :: ptask_tail*
  -- if papiargcursor.CALL = API_ASSERT passertcall
  -- if papiargcursor.INDEX = 0
def $ce_test_front(S, 6) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = API_BORROWED_TARGET pshutdownproducer
  -- if $lookup(S.ENV, $ptascii("phase")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (PINT 9)
def $ce_test_front(S, n) = false -- otherwise
dec $ce_test_seek(pstate, nat, nat) : pstate
def $ce_test_seek(S, n_stage, n) = S -- if $ce_test_front(S, n_stage)
def $ce_test_seek(S, n_stage, 0) = S -- if ~$ce_test_front(S, n_stage)
def $ce_test_seek(S, n_stage, n) = $ce_test_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$ce_test_front(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $ce_test_seek(S, n_stage, n) = S
  -- if ~$ce_test_front(S, n_stage) /\ $(n > 0)
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
        checks.extend([f'{label}_found = $ce_test_seek({prior}, {stage}, 4000)',
                       fr'{label}_found.COMPLETION = NORMAL \/ {label}_found.COMPLETION = BUDGET',
                       f'{label} = {label}_found[.COMPLETION = NORMAL]',
                       f'$ce_test_front({label}, {stage})',
                       f'$call_descriptors_valid({label})',
                       f'$heap_valid($heap_graph({label}))'])

    def parked(label, level):
        checks.extend([
            f'{label}.TODO = (ERROR_HANDLER_INVOKE perrorcall_{label}) :: ptask_{label}_tail*',
            f'perrorcall_{label}.RESUME = NODISCARD_RESUME pframe_{label}',
            f'perrorcall_{label}.LEVEL = {level}',
            f'{label}.CURRENT = eps', f'{label}.FRAMES = eps',
            f'pframe_{label}.CONTEXT = (pcallcontext_{label})',
            f'pcallcontext_{label}.TARGET = CLOSURE_TARGET n_closure',
            f'pcallcontext_{label}.INSTANCE = (n_closure)',
            f'$error_call_valid({label}, perrorcall_{label})',
        ])

    if name == CASES[0]:
        reach('S_deprecated', 'S_initial', 0)
        parked('S_deprecated', 16384)
        checks += [
            '$object_body(S_deprecated.OBJECTS[n_closure]) = REALCLOSURE porigin_function [ALIAS n_cell] eps',
            '$target_function(S_deprecated, CLOSURE_TARGET n_closure) = (pfunction)',
            'pfunction.LINE = 8',
            f'pfunction.NAME = $ptascii("{{closure:") ++ $base64("{encoded_path}") ++ $ptascii(":8}}")',
            '$lookup(S_deprecated.ENV, $ptascii("value")) = (n_cell)',
            'S_deprecated.STORE[n_cell] = DEFINED (PINT 1)',
            'n_cell <- S_deprecated.REFCELLS',
            '$heap_owners($heap_prune($heap_graph(S_deprecated)), HOBJECT n_closure) = 2',
            '$heap_owners($heap_prune($heap_graph(S_deprecated)), HCELL n_cell) = 2',
            '$ce_review_output(S_deprecated.EVENTS) = eps',
        ]
        reach('S_nodiscard', 'S_deprecated', 1)
        parked('S_nodiscard', 512)
        checks += [
            'pframe_S_nodiscard.CONTEXT = pframe_S_deprecated.CONTEXT',
            '$object_body(S_nodiscard.OBJECTS[n_closure]) = REALCLOSURE porigin_function [ALIAS n_cell] eps',
            'S_nodiscard.STORE[n_cell] = DEFINED (PINT 4)',
            '$heap_owners($heap_prune($heap_graph(S_nodiscard)), HOBJECT n_closure) = 1',
            '$heap_owners($heap_prune($heap_graph(S_nodiscard)), HCELL n_cell) = 2',
            '$ce_review_output(S_nodiscard.EVENTS) = $ptascii("D:1:1:1:1;")',
            'S_one = $drive_steps(S_nodiscard, 1)',
            'S_one.COMPLETION = BUDGET',
            '$drive_steps(S_one[.COMPLETION = NORMAL], 1) = $drive_steps(S_nodiscard, 2)',
        ]
        reach('S_body', 'S_nodiscard', 2)
        checks += [
            'S_body.CURRENT = (pcallcontext_body)',
            'pcallcontext_body.TARGET = CLOSURE_TARGET n_closure',
            '$lookup(S_body.ENV, $ptascii("value")) = (n_cell)',
            'S_body.STORE[n_cell] = DEFINED (PINT 7)',
            '$heap_owners($heap_prune($heap_graph(S_body)), HOBJECT n_closure) = 1',
            '$heap_owners($heap_prune($heap_graph(S_body)), HCELL n_cell) = 3',
            '$ce_review_output(S_body.EVENTS) = $ptascii("D:1:1:1:1;N:1:1:1:1;")',
        ]
        last = 'S_body'
    elif name == CASES[1]:
        reach('S_first_warning', 'S_initial', 0)
        parked('S_first_warning', 16384)
        checks += [
            '$object_body(S_first_warning.OBJECTS[n_closure]) = REALCLOSURE porigin_function [DIRECT (PINT 3)] eps',
            '$target_function(S_first_warning, CLOSURE_TARGET n_closure) = (pfunction)',
            'pfunction.LINE = 7',
            f'pfunction.NAME = $ptascii("{{closure:") ++ $base64("{encoded_path}") ++ $ptascii(":7}}")',
            '$lookup(S_first_warning.ENV, $ptascii("initial")) = (n_outside)',
            'S_first_warning.STORE[n_outside] = DEFINED (PINT 3)',
            '$heap_owners($heap_prune($heap_graph(S_first_warning)), HOBJECT n_closure) = 2',
            '$ce_review_output(S_first_warning.EVENTS) = eps',
        ]
        reach('S_first_body', 'S_first_warning', 3)
        checks += [
            'S_first_body.CURRENT = (pcallcontext_first_body)',
            'pcallcontext_first_body.TARGET = CLOSURE_TARGET n_closure',
            'S_first_body.GLOBALTABLE = (psymboltable_globals)',
            '$lookup(psymboltable_globals.ENV, $ptascii("initial")) = (n_outside)',
            'S_first_body.STORE[n_outside] = DEFINED (PINT 99)',
            '$lookup(S_first_body.ENV, $ptascii("initial")) = (n_inside)',
            'n_inside =/= n_outside',
            'S_first_body.STORE[n_inside] = DEFINED (PINT 3)',
            '$ce_review_output(S_first_body.EVENTS) = $ptascii("D:1:1:1;")',
        ]
        reach('S_second_warning', 'S_first_body', 0)
        parked('S_second_warning', 16384)
        checks += [
            '$object_body(S_second_warning.OBJECTS[n_closure]) = REALCLOSURE porigin_function [DIRECT (PINT 3)] eps',
            '$ce_review_output(S_second_warning.EVENTS) = $ptascii("D:1:1:1;B:1;U:1;")',
        ]
        reach('S_nodiscard', 'S_second_warning', 1)
        parked('S_nodiscard', 512)
        checks += [
            '$ce_review_output(S_nodiscard.EVENTS) = $ptascii("D:1:1:1;B:1;U:1;D:1:1:1;")',
        ]
        reach('S_body', 'S_nodiscard', 3)
        checks += [
            'S_body.CURRENT = (pcallcontext_body)',
            'pcallcontext_body.TARGET = CLOSURE_TARGET n_closure',
            '$object_body(S_body.OBJECTS[n_closure]) = REALCLOSURE porigin_function [DIRECT (PINT 3)] eps',
            '$ce_review_output(S_body.EVENTS) = $ptascii("D:1:1:1;B:1;U:1;D:1:1:1;N:1:1:1;")',
        ]
        last = 'S_body'
    else:
        reach('S_warning', 'S_initial', 4)
        checks += [
            'S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall_warning) :: ptask_tail*',
            'perrorcall_warning.RESUME = API_CALLBACK_SEND papiargcursor',
            'papiargcursor.CALL = API_ASSERT passertcall',
            'papiargcursor.TARGET = CLOSURE_TARGET n_closure',
            'papiargcursor.SENT = eps', 'papiargcursor.INDEX = 0',
            'S_warning.CURRENT = eps', 'S_warning.FRAMES = eps',
            '$error_call_valid(S_warning, perrorcall_warning)',
            '$api_cursor_valid(S_warning, papiargcursor)',
            '$object_body(S_warning.OBJECTS[n_closure]) = REALCLOSURE porigin_function [ALIAS n_phase] eps',
            'S_warning.STORE[n_phase] = DEFINED (PINT 1)',
            '$target_function(S_warning, CLOSURE_TARGET n_closure) = (pfunction)',
            'pfunction.NAME = $ptascii("{closure:ApiOwner::make():6}")', 'pfunction.LINE = 6',
            '$target_receiver(S_warning, CLOSURE_TARGET n_closure) = (n_receiver)',
            '$object_name(S_warning, n_receiver) = $ptascii("ApiOwner")',
            '$heap_owners($heap_prune($heap_graph(S_warning)), HOBJECT n_closure) = 3',
            '$heap_owners($heap_prune($heap_graph(S_warning)), HOBJECT n_receiver) = 1',
        ]
        reach('S_pending', 'S_warning', 5)
        checks += [
            'S_pending.TODO = (API_CALLBACK_SEND papiargcursor_pending) :: ptask_tail*',
            'papiargcursor_pending.TARGET = CLOSURE_TARGET n_closure',
            'papiargcursor_pending.SENT = eps', 'papiargcursor_pending.INDEX = 0',
            '$api_cursor_valid(S_pending, papiargcursor_pending)',
            'S_pending.STORE[n_phase] = DEFINED (PINT 9)',
            '$heap_owners($heap_prune($heap_graph(S_pending)), HOBJECT n_closure) = 1',
            '$heap_owners($heap_prune($heap_graph(S_pending)), HOBJECT n_receiver) = 1',
            '$ce_review_output(S_pending.EVENTS) = $ptascii("D:1:1:1:1;")',
            # Derived expired-node projection, not a physically valid reached state.
            'S_expired = S_pending[.ALLOCATIONS = $destruction_node_delete(S_pending.ALLOCATIONS, HOBJECT n_closure)]',
            '~$call_task_valid(S_expired, API_CALLBACK_SEND papiargcursor_pending)',
            'PhpStep: S_expired ~> S_refused',
            'S_refused = S_expired[.COMPLETION = UNSUPPORTED "expired selected API callback before argument copy"]',
        ]
        reach('S_body', 'S_pending', 6)
        checks += [
            'S_body.CURRENT = (pcallcontext_body)',
            'pcallcontext_body.TARGET = API_BORROWED_TARGET pshutdownproducer',
            'pcallcontext_body.INSTANCE = (n_closure)',
            'pcallcontext_body.RECEIVER = (n_receiver)',
            'pcallcontext_body.ARGC = 4',
            '$lookup(S_body.ENV, $ptascii("phase")) = (n_phase)',
            'S_body.STORE[n_phase] = DEFINED (PINT 9)',
            '$heap_owners($heap_prune($heap_graph(S_body)), HOBJECT n_closure) = 2',
            '$heap_owners($heap_prune($heap_graph(S_body)), HOBJECT n_receiver) = 1',
            '$ce_review_output(S_body.EVENTS) = $ptascii("D:1:1:1:1;")',
        ]
        last = 'S_body'
    checks += [
        f'S_done = $drive_steps({last}, 4000)', 'S_done.COMPLETION = NORMAL',
        'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
        'S_done.DESTRUCTION.FRAMES = eps', 'S_done.DESTRUCTION.RELEASES = eps',
        'S_done.DESTRUCTION.CALLS = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$ce_review_output(S_done.EVENTS) = [' + ','.join(map(str, expected_stdout)) + ']',
    ]
    if name != CASES[1]:
        checks += ['~((HOBJECT n_closure) <- S_done.ALLOCATIONS)']
    if name == CASES[2]:
        checks += ['~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)']
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
                   '141-method-compiler.watsup', '194-compiler-preflight.watsup',
                   '253-closure-current-binding.watsup',
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
    keyword_programs = []
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        programs = {name: adapter.request({'op': 'check', 'ast': parsed[name]['ast'], 'fixture': True})['fixture']
                    for name in selected}
        if CASES[0] in selected:
            for invalid in ('missing', 'out_of_span'):
                ast = copy.deepcopy(parsed[CASES[0]]['ast'])
                pending, closures = [ast], []
                while pending:
                    value = pending.pop()
                    if isinstance(value, dict):
                        if value.get('node') == 'Expr_Closure':
                            closures.append(value)
                        pending.extend(value.values())
                    elif isinstance(value, list):
                        pending.extend(value)
                assert len(closures) == 1
                metadata = closures[0]['meta']
                assert metadata['methodKeywordLine'] == {'int': '8'}
                if invalid == 'missing':
                    del metadata['methodKeywordLine']
                else:
                    metadata['methodKeywordLine'] = {'int': str(int(metadata['endLine']['int']) + 1)}
                keyword_programs.append(adapter.request({'op': 'check', 'ast': ast, 'fixture': True})['fixture'])
    finally:
        adapter.close()
    rows = []
    for name in selected:
        source, native_row = native[name]
        checks = conditions(name, programs[name], source, base64.b64decode(native_row['stdout_b64']))
        if name == CASES[0]:
            encoded_path = base64.b64encode(str(source).encode()).decode()
            # Two derived checked-AST receipt refusals, never source agreements.
            checks += [f'$php_run({program}, 0, "{encoded_path}").COMPLETION = UNSUPPORTED "ordinary expression or writable operand compilation"'
                       for program in keyword_programs]
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
                     'derived_guard_assertions': 2 if name == CASES[0] else (4 if name == CASES[2] else 0),
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
        'scope': 'Reached real Closure/arrow captures, selected scopes and borrowed receivers; labeled expired-target derived guard; no native execution'}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
