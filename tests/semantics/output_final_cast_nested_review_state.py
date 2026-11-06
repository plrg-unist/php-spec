#!/usr/bin/env python3
"""Nested null-C destructor fatal retains real C owners and aborts later CVs."""
import argparse
import json
import os
import re
from pathlib import Path
import tempfile

from recorded_worker import Worker

import output_deprecation_warning_review_state as runner
import output_final_cast_nested_sources as sources
import output_object_conversion_review_sources as support

ROOT = support.ROOT
SOURCE = sources.CASES['fresh-local-destructor-throw']
CAUGHT_SOURCE = sources.CASES['caught-local-destructor-throw']
FINALLY_SOURCE = SOURCE.replace(b"throw new Exception('F');",
                               b"try { throw new Exception('F'); } finally { return; }")
PREFIX = runner.PREFIX.split('dec $dp_phase', 1)[0] + r'''
dec $dp_phase(pstate, nat) : bool
def $dp_phase(S, 0) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = [pframe]
  -- if pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (OUTPUT_FINAL_OBJECT_CV pobobjectreturn) :: ptask_native*
def $dp_phase(S, 2) = true
  -- if S.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (DESTRUCTOR_C_RETURN pdestructorcall) :: (DESTRUCTOR_RESULT pdestructorcall) :: (OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall porigin n eps) :: ptask_native*
  -- if pdestructionframe.PENDING = (n)
def $dp_phase(S, 3) = true
  -- if S.TODO = [OUTPUT_FINAL_DEACTIVATE pobdeactivate]
  -- if pobdeactivate.INDEX = 0
def $dp_phase(S, 7) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = [pframe]
  -- if pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_native*
def $dp_phase(S, 8) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.FRAME = (pdestructionframe)
  -- if $object_name(S, pdestructorcall.OBJECT) = $ptascii("T")
def $dp_phase(S, 9) = true
  -- if S.TODO = [RETURN_UNWIND poperand porigin?]
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = [pframe]
  -- if pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_native*
def $dp_phase(S, n) = false -- otherwise
''' + 'dec $dp_seek' + runner.PREFIX.split('dec $dp_seek', 1)[1]


def expected_fatal(path, message='F', line=4, method='D->__destruct'):
    return (f'Fatal error: Uncaught Exception: {message} in {path}:{line}\nStack trace:\n'
            f'#0 [internal function]: {method}()\n#1 {{main}}\n'
            f'  thrown in {path} on line {line}\n').encode()


def fingerprint():
    result = support.fingerprint()
    for name in ('tests/semantics/output_final_cast_nested_sources.py',
                 'tests/semantics/output_final_cast_nested_review_state.py',
                 'tests/semantics/output_deprecation_warning_review_state.py',
                 'tests/semantics/_build/default/numeric_runner.exe'):
        result[name] = support.common.sha(ROOT / name)
    return result


def reach(fixture, directory, path):
    return [
        'S_initial = $php_file_run(' + fixture + ', 0, ' + runner.bytes_expr(os.fsencode(path)) + ', ' + runner.bytes_expr(os.fsencode(directory)) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $dp_seek(S_initial, 0, 1024)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]',
        'S.TODO = (THROW_VALUE porigin z) :: ptask_tail*',
        'S.CURRENT = (pcallcontext)', 'S.FRAMES = [pframe]',
        'pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_native*',
        'pdestructorcall.FRAME = (pdestructionframe_outer)',
        'pdestructionframe_outer.PENDING = (n_old)',
        'S.RESULT = KNOWN (POBJECT n_new)',
        'ptask_native* = [DESTRUCTOR_RELEASE pdestructionrelease, DESTRUCTOR_FRAME_EXIT pdestructionframe_outer, OUTPUT_FINAL_OBJECT_CV pobobjectreturn, OUTPUT_DRAIN pobdrain]',
        'pobobjectreturn.SOURCE = ((porigin_old, n_old))',
        'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_later_cell)]',
        'S.STORE[n_later_cell] = DEFINED (POBJECT n_later)',
        'ptask_marker = OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall porigin n_new eps',
        'S_capture_found = $drive_steps(S, 1)', 'S_capture_found.COMPLETION = BUDGET',
        'S_capture = S_capture_found[.COMPLETION = NORMAL]',
        'S_capture.TODO = (THROW_SEARCH n_new) :: ptask_unwind*',
        '$ob_object_final_local_pending(S_capture)',
        'S_capture.FRAMES = [pframe_capture]',
        'pframe_capture.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_marker :: ptask_native*',
    ]


def owners(state, new_count=1):
    return (f'$heap_count(HOBJECT pobobjectreturn.OBJECT, $machine_roots({state})) = 2 /\\ '
            f'$heap_count(HOBJECT pdestructorcall.OBJECT, $machine_roots({state})) = 2 /\\ '
            f'$heap_count(HOBJECT n_old, $machine_roots({state})) = 1 /\\ '
            f'$heap_owners($heap_graph({state}), HOBJECT n_later) = 1 /\\ '
            f'$heap_count(HOBJECT n_new, $machine_roots({state})) = {new_count}')


def primary_assertions(fixture, directory, path):
    bindings = reach(fixture, directory, path) + [
        'S_exit_found = $dp_seek(S_capture, 2, 256)',
        r'S_exit_found.COMPLETION = NORMAL \/ S_exit_found.COMPLETION = BUDGET',
        'S_exit = S_exit_found[.COMPLETION = NORMAL]',
        'S_exit.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: ptask_return*',
        'ptask_return* = [DESTRUCTOR_C_RETURN pdestructorcall, DESTRUCTOR_RESULT pdestructorcall, ptask_marker] ++ ptask_native*',
        'S_stale = S_exit[.ALLOCATIONS = $destruction_node_delete(S_exit.ALLOCATIONS, HOBJECT n_new)]',
        'S_wrong_source = S_exit[.TODO = [DESTRUCTOR_FRAME_EXIT pdestructionframe, DESTRUCTOR_C_RETURN pdestructorcall, DESTRUCTOR_RESULT pdestructorcall, OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall porigin_old n_new eps] ++ ptask_native*]',
        'ptask_wrong_source* = [DESTRUCTOR_C_RETURN pdestructorcall, DESTRUCTOR_RESULT pdestructorcall, OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall porigin_old n_new eps] ++ ptask_native*',
        'S_budget = $drive_steps(S_exit, 0)',
        'S_report_found = $drive_steps(S_budget[.COMPLETION = NORMAL], 1)',
        'S_report_found.COMPLETION = BUDGET', 'S_report = S_report_found[.COMPLETION = NORMAL]',
        'S_report.TODO = [OUTPUT_FINAL_PENDING pobdeactivate n_new true]',
        'S_report.DESTRUCTION.ABANDONED = [pdestructioncleanup_local, pdestructioncleanup_outer]',
        'pdestructioncleanup_bad = pdestructioncleanup_outer[.SOURCE = OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall porigin_old n_new (pobdeactivate)]',
        'S_bad_receipt = S_report[.DESTRUCTION.ABANDONED = [pdestructioncleanup_local, pdestructioncleanup_bad]]',
        'S_release_found = $drive_steps(S_report, 1)', 'S_release_found.COMPLETION = BUDGET',
        'S_release = S_release_found[.COMPLETION = NORMAL]',
        'S_deactivate_found = $dp_seek(S_release, 3, 256)',
        r'S_deactivate_found.COMPLETION = NORMAL \/ S_deactivate_found.COMPLETION = BUDGET',
        'S_deactivate = S_deactivate_found[.COMPLETION = NORMAL]',
        'S_done = $drive_steps(S_deactivate, 2048)',
    ]
    events = '[OUTPUT ([80]), STDERR ' + runner.bytes_expr(expected_fatal(path)) + ']'
    components = [
        ('actual D throw preserves distinct native C owners', r'n_old =/= n_new /\ pobobjectreturn.OBJECT =/= n_later /\ $object_name(S, n_later) = $ptascii("T") /\ pdestructorcall.PENDING = (n_old) /\ ~pdestructorcall.USER /\ pdestructorcall.SITE = eps /\ pcallcontext.CALLSITE = eps /\ pcallcontext.LINE = $(-1) /\ $throwable_field(S, n_new, "previous") = PNULL /\ ' + owners('S')),
        ('borrowed F capture changes no existing owner', r'$task_nodes(ptask_marker) = eps /\ pobobjectreturn.SOURCE = ((porigin_old, n_old)) /\ S_capture.EVENTS = [OUTPUT ([80])] /\ ' + owners('S_capture')),
        ('public captured native frame', r'$call_descriptors_valid(S_capture) /\ $heap_valid($heap_graph(S_capture)) /\ $output_state_valid(S_capture) /\ $destruction_state_valid(S_capture)'),
        ('actual inner D frame exits before C guards and later CVs', r'S_exit.CURRENT = eps /\ S_exit.FRAMES = eps /\ S_exit.ORIGIN = eps /\ S_exit.DESTRUCTION.FRAMES = [pdestructionframe, pdestructionframe_outer] /\ pdestructionframe.PENDING = (n_new) /\ pdestructionframe_outer.PENDING = (n_old) /\ ~(n_later <- S_exit.DESTRUCTION.CALLED) /\ ~(pobobjectreturn.OBJECT <- S_exit.DESTRUCTION.CALLED) /\ ' + owners('S_exit')),
        ('full actual native return and public admission', r'$ob_object_final_local_ready(S_exit, pobobjectreturn, pdestructorcall, porigin, n_new, pdestructionframe, ptask_return*) /\ $call_descriptors_valid(S_exit) /\ $heap_valid($heap_graph(S_exit)) /\ $output_state_valid(S_exit) /\ $destruction_state_valid(S_exit)'),
        ('stale source pending frame and class refusals', r'~$call_task_valid(S_stale, ptask_marker) /\ ~$ob_object_final_local_ready(S_wrong_source, pobobjectreturn, pdestructorcall, porigin_old, n_new, pdestructionframe, ptask_wrong_source*) /\ ~$ob_object_final_local_ready(S_exit, pobobjectreturn, pdestructorcall, porigin, n_old, pdestructionframe, ptask_return*) /\ ~$ob_object_final_local_ready(S_exit[.FRAMES = [pframe]], pobobjectreturn, pdestructorcall, porigin, n_new, pdestructionframe, ptask_return*) /\ ~$ob_object_final_local_ready(S_exit[.DECLARATIONS = eps], pobobjectreturn, pdestructorcall, porigin, n_new, pdestructionframe, ptask_return*)'),
        ('zero budget preserves all actual C and CV owners', r'S_budget.COMPLETION = BUDGET /\ S_budget.TODO = S_exit.TODO /\ S_budget.DESTRUCTION = S_exit.DESTRUCTION /\ S_budget.ALLOCATIONS = S_exit.ALLOCATIONS /\ S_budget.GC = S_exit.GC /\ S_budget.EVENTS = S_exit.EVENTS'),
        ('nested F fatal precedes old E restoration and later CV execution', 'S_report.EVENTS = ' + events + r' /\ pobdeactivate.COMPLETION = REQUESTFATAL ($ptascii("Exception")) ($ptascii("F")) 4 /\ S_report.EXITSTATUS = 255 /\ $throwable_field(S_report, n_new, "previous") = PNULL /\ S_report.DESTRUCTION.CALLS = eps /\ S_report.DESTRUCTION.FRAMES = eps /\ S_report.DESTRUCTION.RELEASES = eps /\ ~(n_later <- S_report.DESTRUCTION.CALLED) /\ ' + owners('S_report')),
        ('genuine generic D receipt and separate outer T pair', r'pdestructioncleanup_local.SOURCE = DESTRUCTOR_RESULT pdestructorcall /\ pdestructioncleanup_outer.SOURCE = OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall porigin n_new (pobdeactivate) /\ $eager_cleanup_valid(S_report, pdestructioncleanup_local) /\ $eager_cleanup_valid(S_report, pdestructioncleanup_outer) /\ ~$eager_cleanup_valid(S_bad_receipt, pdestructioncleanup_bad) /\ ~$eager_cleanup_valid(S_report[.DESTRUCTION.ABANDONED = [pdestructioncleanup_local]], pdestructioncleanup_outer) /\ $eager_abandoned_owner(pdestructioncleanup_outer.SOURCE) = [HOBJECT pobobjectreturn.OBJECT, HOBJECT pobobjectreturn.OBJECT] /\ $task_nodes(pdestructioncleanup_outer.SOURCE) = eps /\ ~$call_task_valid(S_report, pdestructioncleanup_outer.SOURCE) /\ $call_descriptors_valid(S_report) /\ $heap_valid($heap_graph(S_report)) /\ $output_state_valid(S_report) /\ $destruction_state_valid(S_report)'),
        ('reported F retires without releasing saved old E or C guards', r'~((HOBJECT n_new) <- S_deactivate.ALLOCATIONS) /\ $eager_cleanup_valid(S_deactivate, pdestructioncleanup_local) /\ $eager_cleanup_valid(S_deactivate, pdestructioncleanup_outer) /\ S_deactivate.EVENTS = S_report.EVENTS /\ ' + owners('S_deactivate', 0)),
        ('actual fatal deactivation keeps skipped CV and abandoned C roots', r'S_done.COMPLETION = pobdeactivate.COMPLETION /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.OUTPUTBUFFERS = eps /\ S_done.EXITSTATUS = 255 /\ S_done.EVENTS = S_report.EVENTS /\ S_done.DESTRUCTION.ABANDONED = S_report.DESTRUCTION.ABANDONED /\ ~(n_later <- S_done.DESTRUCTION.CALLED) /\ ~(pobobjectreturn.OBJECT <- S_done.DESTRUCTION.CALLED) /\ $eager_cleanup_valid(S_done, pdestructioncleanup_local) /\ $eager_cleanup_valid(S_done, pdestructioncleanup_outer) /\ ' + owners('S_done', 0)),
    ]
    return bindings, components


def caught_assertions(fixture, directory, path):
    bindings = reach(fixture, directory, path) + [
        'S_catch_found = $dp_seek(S_capture, 7, 256)',
        r'S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET',
        'S_catch = S_catch_found[.COMPLETION = NORMAL]',
        'S_catch.TODO = (CATCH_BIND porigin_try n_index n_new) :: ptask_catch*',
        'S_catch.FRAMES = [pframe_catch]',
        'pframe_catch.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_native*',
        'S_later_found = $dp_seek(S_catch, 8, 512)',
        r'S_later_found.COMPLETION = NORMAL \/ S_later_found.COMPLETION = BUDGET',
        'S_later = S_later_found[.COMPLETION = NORMAL]',
        'S_later.TODO = (DESTRUCTOR_ENTER pdestructorcall_later) :: ptask_later*',
    ]
    components = [
        ('actual catch consumes F marker while F is still owned', r'$task_nodes(ptask_marker) = eps /\ $task_nodes(CATCH_BIND porigin_try n_index n_new) = [HOBJECT n_new] /\ (HOBJECT n_new) <- S_catch.ALLOCATIONS /\ $call_task_valid(S_catch, CATCH_BIND porigin_try n_index n_new) /\ ' + owners('S_catch')),
        ('normal destructor resumes the genuine later CV', r'pdestructorcall_later.OBJECT = n_later /\ pdestructorcall_later.PENDING = (n_old) /\ pdestructorcall_later.FRAME = (pdestructionframe_outer) /\ ~pdestructorcall_later.USER /\ pdestructorcall_later.SITE = eps /\ ~((HOBJECT n_new) <- S_later.ALLOCATIONS) /\ ~((HOBJECT pdestructorcall.OBJECT) <- S_later.ALLOCATIONS) /\ $heap_count(HOBJECT pobobjectreturn.OBJECT, $machine_roots(S_later)) = 2 /\ $heap_count(HOBJECT n_old, $machine_roots(S_later)) = 1 /\ $heap_count(HOBJECT n_later, $machine_roots(S_later)) = 2 /\ S_later.EVENTS = [OUTPUT ([80])]'),
    ]
    return bindings, components


def finally_assertions(fixture, directory, path):
    bindings = reach(fixture, directory, path) + [
        'S_return_found = $dp_seek(S_capture, 9, 512)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]',
        'S_return.TODO = [RETURN_UNWIND (KNOWN PNULL) porigin_return?]',
        'S_return.FRAMES = [pframe_return]',
        'pframe_return.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_native*',
        'S_normal_found = $drive_steps(S_return, 1)', 'S_normal_found.COMPLETION = BUDGET',
        'S_normal = S_normal_found[.COMPLETION = NORMAL]',
        'S_normal.DESTRUCTION.FRAMES = [pdestructionframe_normal, pdestructionframe_outer]',
        'S_normal.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_normal) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe_normal) :: (DESTRUCTOR_C_RETURN pdestructorcall) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_normal*',
        'ptask_normal* = ptask_native*',
    ]
    components = [
        ('actual finally consumption preserves a valid normal-return budget state', r'~((HOBJECT n_new) <- S_return.ALLOCATIONS) /\ $call_descriptors_valid(S_return) /\ $heap_valid($heap_graph(S_return)) /\ $output_state_valid(S_return) /\ $destruction_state_valid(S_return) /\ ' + owners('S_return', 0)),
        ('normal restore preserves consumed F metadata and real C owners', r'S_normal.CURRENT = eps /\ S_normal.FRAMES = eps /\ S_normal.ORIGIN = eps /\ pdestructionframe_normal.PENDING = eps /\ pdestructionframe_normal.VALUE = KNOWN PNULL /\ pdestructionframe_outer.PENDING = (n_old) /\ pdestructionrelease_normal.JOBS = eps /\ pobobjectreturn.SOURCE = ((porigin_old, n_old)) /\ $call_descriptors_valid(S_normal) /\ $heap_valid($heap_graph(S_normal)) /\ ' + owners('S_normal', 0)),
    ]
    return bindings, components


def render(bindings, components):
    return (PREFIX + '\ndec $main() : bool*\ndef $main() = [' +
            ', '.join('(' + check + ')' for _, check in components) + ']\n' +
            ''.join('  -- if ' + binding + '\n' for binding in bindings))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='output-final-cast-nested-review-'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': support.subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'before': fingerprint(), 'profile': support.common.PROFILE,
              'model_only_controls': ['caught', 'finally'], 'native_agreement_credit': 0,
              'records': [], 'passed': False, 'completed': False}
    stage = 'native'
    directory = out
    try:
        cases = [('primary', SOURCE, primary_assertions), ('caught', CAUGHT_SOURCE, caught_assertions),
                 ('finally', FINALLY_SOURCE, finally_assertions)]
        paths = {}
        for name, source, _ in cases:
            paths[name] = out / (name + '.php')
            paths[name].write_bytes(source)
        native = support.common.run([str(ROOT / '.tools/php/bin/php'), '-n', *support.common.FLAGS,
                                     str(paths['primary'])], out, 'native', 10)
        assert native.returncode == 255 and native.stdout == b'P'
        assert native.stderr == expected_fatal(paths['primary'])
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], out / 'frontend')
        try:
            parsed = {name: frontend.request({'op': 'parse', 'source': support.base64.b64encode(source).decode()})
                      for name, source, _ in cases}
        finally:
            frontend.close()
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            checked = {name: adapter.request({'op': 'check', 'ast': parsed[name]['ast'], 'fixture': True})
                       for name, _, _ in cases}
        finally:
            adapter.close()
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
        for name, _, assertions in cases:
            directory = out / name
            directory.mkdir()
            bindings, components = assertions(checked[name]['fixture'], out, paths[name])
            fixture = directory / 'state.watsup'
            fixture.write_text(render(bindings, components))
            record = {'case': name, 'source_sha256': support.common.sha(paths[name]),
                      'fixture_sha256': support.common.sha(fixture), 'components': [label for label, _ in components],
                      'passed': False}
            report['records'].append(record)
            stage = 'state'
            result = support.common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                         *[str(ROOT / module) for module in modules], str(fixture)], directory, 'state', 300)
            rendered = result.stdout.decode('ascii')
            values = re.findall(r'\b(?:true|false)\b', rendered)
            record['component_results'] = dict(zip(record['components'], [value == 'true' for value in values]))
            assert not re.sub(r'true|false|[\[\](),;\s]', '', rendered), rendered
            assert result.returncode == 0 and not result.stderr and values == ['true'] * len(components), (result.returncode, result.stdout, result.stderr)
            record['passed'] = True
            print(name, True, flush=True)
        report.update(passed=True, completed=True)
    except BaseException as error:
        if isinstance(error, support.subprocess.TimeoutExpired):
            (directory / (stage + '.stdout')).write_bytes(error.stdout or b'')
            (directory / (stage + '.stderr')).write_bytes(error.stderr or b'')
            (directory / (stage + '.timeout')).write_text(str(error.timeout) + '\n')
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = fingerprint()
        report['stable'] = report['before'] == report['after']
        report['passed'] = report['passed'] and report['stable']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed'] and report['completed']


if __name__ == '__main__':
    main()
