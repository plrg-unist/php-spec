#!/usr/bin/env python3
"""Genuine automatic failure argv, pending lower-write and source operand fronts."""
import argparse
import json
import os
from pathlib import Path
import tempfile
from recorded_worker import Worker
import output_abrupt_sources as sources
ROOT = sources.ROOT
CASES = {
    'argv-cleanup': sources.CASES['reference-argument-cleanup'],
    'pending-lower': sources.CASES['lower-pending'],
    'producer-finish': (b'<?php $e=new Exception;$x=99;function h($b,$p){global $e;throw $e;}class C{function __toString(){return "A";}function __destruct(){echo "D".ob_get_level();}}ob_start("h",1);try{$x=print new C;}catch(Exception $c){echo ($c===$e?"C":"N");}ob_end_clean();echo ":".$x."Z";', b'AD1C:99Z'),
}
PREFIX = r"""
dec $of_output(pevent*) : preqbytes
dec $of_is_output(pevent) : bool
def $of_output(eps) = eps
def $of_output((OUTPUT n*) :: pevent_tail*) = n* ++ $of_output(pevent_tail*)
def $of_output(pevent :: pevent_tail*) = $of_output(pevent_tail*) -- if ~$of_is_output(pevent)
def $of_is_output(OUTPUT n*) = true
def $of_is_output(pevent) = false -- otherwise
dec $of_phase(pstate, nat) : bool
def $of_phase(S, 0) = true -- if S.TODO = (OB_USER_FAIL_ARGS pobinvoke n) :: ptask_tail*
def $of_phase(S, 1) = true
  -- if S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
  -- if pdestructionoperation.SOURCE = OB_USER_FAIL_ARGS pobinvoke n
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
def $of_phase(S, 2) = true
  -- if S.TODO = (OUTPUT_FAIL_WRITE pobwrite n) :: ptask_tail*
  -- if pobwrite.INDEX = 1 /\ |pobwrite.IDS| = 2
def $of_phase(S, 3) = true
  -- if S.TODO = (OUTPUT_FAIL_FINISH pobwrite n) :: ptask_tail*
  -- if pobwrite.TAIL = (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask_tail*
def $of_phase(S, 4) = true
  -- if S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
  -- if pdestructionoperation.SOURCE = OUTPUT_STRING_RELEASE pobstringrelease
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
def $of_phase(S, n) = false -- otherwise
dec $of_seek(pstate, nat, nat) : pstate
def $of_seek(S, n_phase, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $of_seek(S, n_phase, n) = S -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if $of_phase(S, n_phase)
def $of_seek(S, n_phase, 0) = S -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if ~$of_phase(S, n_phase)
def $of_seek(S, n_phase, n) = $of_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$of_phase(S, n_phase) /\ $(n > 0)
"""


def bytes_expr(value):
    return '$base64(' + json.dumps(sources.base64.b64encode(value).decode()) + ')'


def valid(state):
    return ['$call_descriptors_valid(' + state + ')', '$heap_valid($heap_graph(' + state + '))', '$output_state_valid(' + state + ')']


def fingerprint():
    inputs = sources.fingerprint()
    for name in ('tests/semantics/output_abrupt_state.py', 'tests/semantics/_build/default/numeric_runner.exe'):
        inputs[name] = sources.sha(ROOT / name)
    return inputs


def assertions(name, fixture, directory, path):
    phase = {'argv-cleanup': 0, 'pending-lower': 2, 'producer-finish': 3}[name]
    checks = ['S_initial = $php_file_run(' + fixture + ', 0, ' + bytes_expr(os.fsencode(path)) + ', ' + bytes_expr(os.fsencode(directory)) + ')',
              'S_initial.COMPLETION = BUDGET', *valid('S_initial'),
              'S_found = $of_seek(S_initial, ' + str(phase) + ', 512)',
              r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
              'S_reached = S_found[.COMPLETION = NORMAL]', '$of_phase(S_reached, ' + str(phase) + ')', *valid('S_reached'),
              'S_budget = $drive_steps(S_reached, 0)', 'S_budget.COMPLETION = BUDGET',
              r'S_budget.TODO = S_reached.TODO /\ S_budget.OUTPUTBUFFERS = S_reached.OUTPUTBUFFERS', *valid('S_budget')]
    if name == 'argv-cleanup':
        checks += ['S_reached.TODO = (OB_USER_FAIL_ARGS pobinvoke n_pending) :: ptask_tail*',
                   'pobinvoke.CALL = OB_WRITE pobwrite', 'pobwrite.TAIL = ptask_tail*',
                   'pobinvoke.SENT = [REFERENCE n_argument, KNOWN (PINT 1)]',
                   'S_reached.STORE[n_argument] = DEFINED (POBJECT n_argument_object)',
                   '$throwable_live(S_reached, n_pending)', '$ob_user_running(S_reached)',
                   '$output_selected(S_reached, pobinvoke) = (poutputbuffer)',
                   r'poutputbuffer.FLAGS = 113 /\ poutputbuffer.BYTES = ([65])',
                   '~$ob_user_failure_live(S_reached, pobinvoke[.CALL = OB_WRITE pobwrite[.TAIL = eps]])',
                   '~$call_task_valid(S_reached, OB_USER_FAIL_ARGS pobinvoke n_argument_object)',
                   '~$call_task_valid(S_reached, OB_USER_FAIL_ARGS pobinvoke[.SENT = eps] n_pending)',
                   'S_child_found = $of_seek(S_reached, 1, 512)',
                   r'S_child_found.COMPLETION = NORMAL \/ S_child_found.COMPLETION = BUDGET',
                   'S_child = S_child_found[.COMPLETION = NORMAL]', '$of_phase(S_child, 1)', *valid('S_child'),
                   'S_child.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
                   'pdestructionoperation.SOURCE = OB_USER_FAIL_ARGS pobinvoke n_pending',
                   r'pdestructionoperation.COMPLETION = THROWING n_pending /\ pdestructionoperation.PENDING = (n_pending)',
                   '$eager_operation_source_guard(S_child, pdestructionoperation)', '$ob_user_running(S_child)',
                   '$output_at(S_child.OUTPUTBUFFERS, pobinvoke.BUFFER.ID) = (poutputbuffer_child)',
                   r'poutputbuffer_child.FLAGS = 113 /\ poutputbuffer_child.BYTES = ([65])',
                   '~$call_task_valid(S_child, OB_USER_FAIL_ARGS pobinvoke n_pending)',
                   '~$eager_operation_source_guard(S_child, pdestructionoperation[.COMPLETION = NORMAL])',
                   'S_child.FRAMES = pframe :: pframe_tail*',
                   'pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall_replay) :: (DESTRUCTOR_RELEASE pdestructionrelease_replay) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (OB_USER_FAIL_DONE pobinvoke[.SENT = eps]) :: pobwrite.TAIL',
                   'S_frame = $constant_frame_scope(S_child, pframe, pframe_tail*)',
                   'S_tasks = $destructor_saved_frame_scope($api_saved_frame_scope($parameter_string_frame_scope(S_frame, pframe, pframe_tail*), pframe, pframe_tail*), pframe)',
                   'S_replay = $call_after_origin($call_after_origin($call_after_origin(S_tasks, DESTRUCTOR_RESULT pdestructorcall_replay), DESTRUCTOR_RELEASE pdestructionrelease_replay), DESTRUCTOR_OPERATION_EXIT pdestructionoperation)',
                   'S_replay.DESTRUCTION.OPERATIONS = eps',
                   '$ob_user_failure_replay_pending(S_replay, S_replay.TODO, pobinvoke[.SENT = eps]) = (n_pending)',
                   '$ob_user_failure_replay_pending(S_replay, (DESTRUCTOR_OPERATION_EXIT pdestructionoperation[.ORIGIN = eps]) :: (OB_USER_FAIL_DONE pobinvoke[.SENT = eps]) :: pobwrite.TAIL, pobinvoke[.SENT = eps]) = eps',
                   '$ob_user_failure_replay_pending(S_replay, (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (OB_USER_FAIL_DONE pobinvoke[.SENT = eps]) :: eps, pobinvoke[.SENT = eps]) = eps',
                   '$ob_user_failure_replay_pending(S_replay, (DESTRUCTOR_OPERATION_EXIT pdestructionoperation[.COMPLETION = NORMAL]) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (OB_USER_FAIL_DONE pobinvoke[.SENT = eps]) :: pobwrite.TAIL, pobinvoke[.SENT = eps]) = eps']
    else:
        task = 'OUTPUT_FAIL_WRITE' if name == 'pending-lower' else 'OUTPUT_FAIL_FINISH'
        checks += ['S_reached.TODO = (' + task + ' pobwrite n_pending) :: ptask_tail*',
                   'pobwrite.TAIL = ptask_tail*', '$throwable_live(S_reached, n_pending)',
                   '~$ob_user_running(S_reached)',
                   '~$call_task_valid(S_reached, ' + task + ' pobwrite[.TAIL = eps] n_pending)',
                   '~$call_task_valid(S_reached, ' + task + ' pobwrite[.IDS = ([999])] n_pending)',
                   '~$call_task_valid(S_reached, ' + task + ' pobwrite[.CALLER = OUTPUT_VM (PORIGIN 999 eps) (EMIT 1) 1] n_pending)']
    if name == 'pending-lower':
        checks += [r'pobwrite.IDS = ([1,0]) /\ pobwrite.INDEX = 1 /\ pobwrite.BYTES = ([65])',
                   'S_reached.OUTPUTBUFFERS = [poutputbuffer_upper,poutputbuffer_lower]',
                   r'poutputbuffer_upper.FLAGS = 12401 /\ poutputbuffer_upper.SIZE = 0 /\ poutputbuffer_lower.FLAGS = 113',
                   'S_next_found = $drive_steps(S_reached, 1)', 'S_next = S_next_found[.COMPLETION = NORMAL]', *valid('S_next'),
                   'S_next.TODO = (OUTPUT_FAIL_WRITE pobwrite_next n_pending) :: ptask_tail*',
                   r'pobwrite_next.INDEX = 2 /\ pobwrite_next.BYTES = ([65])',
                   'S_next.OUTPUTBUFFERS = [poutputbuffer_upper,poutputbuffer_lower_failed]',
                   r'poutputbuffer_lower_failed.FLAGS = 12401 /\ poutputbuffer_lower_failed.SIZE = 0 /\ poutputbuffer_lower_failed.BYTES = eps']
    if name == 'producer-finish':
        checks += ['pobwrite.CALLER = OUTPUT_VM porigin (PRINT_EMIT porigin z) z',
                   'pobwrite.TAIL = (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask_native_tail*',
                   'pobstringrelease.OBJECT = n_operand',
                   'pobstringrelease.CALLER = pobwrite.CALLER',
                   'pobstringrelease.CONTEXT = pobwrite.CONTEXT',
                   'pobstringrelease.TAIL = ptask_native_tail*',
                   '$call_task_valid(S_reached, OUTPUT_STRING_RELEASE pobstringrelease)',
                   '~$call_task_valid(S_reached, OUTPUT_STRING_RELEASE pobstringrelease[.OBJECT = n_pending])',
                   '~$call_task_valid(S_reached, OUTPUT_STRING_RELEASE pobstringrelease[.TAIL = eps])',
                   '$heap_owners($heap_graph(S_reached), HOBJECT n_operand) = 1',
                   '$of_output(S_reached.EVENTS) = ([65])',
                   'S_child_found = $of_seek(S_reached, 4, 512)',
                   r'S_child_found.COMPLETION = NORMAL \/ S_child_found.COMPLETION = BUDGET',
                   'S_child = S_child_found[.COMPLETION = NORMAL]', '$of_phase(S_child, 4)', *valid('S_child'),
                   'S_child.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
                   'pdestructionoperation.SOURCE = OUTPUT_STRING_RELEASE pobstringrelease',
                   'pdestructionoperation.PENDING = (n_pending)',
                   '$output_string_exit(S_child, pdestructionoperation, pobstringrelease)',
                   '$eager_operation_source_guard(S_child, pdestructionoperation)',
                   '~$eager_operation_source_guard(S_child, pdestructionoperation[.SOURCE = OUTPUT_STRING_RELEASE pobstringrelease[.TAIL = eps]])',
                   '~$ob_user_running(S_child)',
                   'S_child.OUTPUTBUFFERS = [poutputbuffer_disabled]',
                   r'poutputbuffer_disabled.FLAGS = 12401 /\ poutputbuffer_disabled.SIZE = 0 /\ poutputbuffer_disabled.BYTES = eps']
    checks += ['S_done = $drive_steps(S_reached, 1024)',
               r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
               'S_done.OUTPUTBUFFERS = eps', '$of_output(S_done.EVENTS) = ' + bytes_expr(CASES[name][1]), *valid('S_done')]
    return checks

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact group IDs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(set(selected)) == len(selected) and all(name in CASES for name in selected)
    out = args.output or Path(tempfile.mkdtemp(prefix='output-abrupt-state-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': sources.subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'before': fingerprint(), 'profile': sources.PROFILE,
              'selected': selected, 'groups': [], 'passed': False, 'completed': False}
    bodies = []
    print(out, flush=True)
    try:
        for index, name in enumerate(selected):
            directory = out / name; directory.mkdir()
            source, expected = CASES[name]; path = directory / 'source.php'; path.write_bytes(source)
            native = sources.run([str(ROOT / '.tools/php/bin/php'), '-n', *sources.FLAGS, str(path)], directory, 'native', 10)
            if expected is not None:
                assert native.returncode == 0 and native.stdout == expected and not native.stderr, (name, native.stdout, expected, native.stderr)
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                               'extension=' + str(ROOT / '.tools/php-file.so'),
                               str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            try:
                parsed = frontend.request({'op': 'parse', 'source': sources.base64.b64encode(source).decode()})
            finally:
                frontend.close()
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
            try:
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            finally:
                adapter.close()
            checks = assertions(name, checked['fixture'], directory, path)
            bodies.append('dec $of_case_' + str(index) + '() : bool\ndef $of_case_' + str(index) + '() = true\n' +
                          ''.join('  -- if ' + check + '\n' for check in checks))
            report['groups'].append({'id': name, 'premises': len(checks), 'source_sha256': sources.sha(path)})
        fixture = out / 'state.watsup'
        fixture.write_text(PREFIX + '\n'.join(bodies) + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if $of_case_' + str(index) + '()\n' for index in range(len(bodies))))
        report['fixture_sha256'] = sources.sha(fixture)
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
        result = sources.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                              *[str(ROOT / name) for name in modules], str(fixture)], out, 'state', 120)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, (
            result.returncode, result.stdout, result.stderr)
        report.update(passed=True, completed=True)
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = fingerprint()
        report['passed'] = report['passed'] and report['before'] == report['after']
        report['runner_sha256'] = sources.sha(ROOT / 'tests/semantics/_build/default/numeric_runner.exe')
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed'] and report['completed']


if __name__ == '__main__':
    main()
