#!/usr/bin/env python3
"""Reached callee-only wrappers, sealed normal returns and unsealed body throws."""
import argparse
import json
import os
from pathlib import Path
import tempfile
from recorded_worker import Worker
import output_result_cleanup_sources as sources
import output_result_cleanup_review_sources as review

ROOT = sources.ROOT
CASES = {
    'callee-wrapper': sources.CASES['unset-wrapper-during-body'],
    'normal-return-cleanup': sources.CASES['api-normal-result-argv-throw'],
    'body-throw-unsealed': sources.CASES['body-throw-null-result'],
    'borrowed-receiver': review.CASES['normal-wrapper-before-alias-receiver-release'],
}
PREFIX = r"""
dec $rc_output(pevent*) : preqbytes
dec $rc_is_output(pevent) : bool
def $rc_output(eps) = eps
def $rc_output((OUTPUT n*) :: pevent_tail*) = n* ++ $rc_output(pevent_tail*)
def $rc_output(pevent :: pevent_tail*) = $rc_output(pevent_tail*) -- if ~$rc_is_output(pevent)
def $rc_is_output(OUTPUT n*) = true
def $rc_is_output(pevent) = false -- otherwise
dec $rc_success(ptask*) : ptask?
dec $rc_is_success(ptask) : bool
def $rc_success((OB_USER_NORMAL_RESULT pobinvoke pdestructionframe) :: ptask_tail*) = (OB_USER_NORMAL_RESULT pobinvoke pdestructionframe)
def $rc_success(ptask :: ptask_tail*) = $rc_success(ptask_tail*) -- if ~$rc_is_success(ptask)
def $rc_success(eps) = eps
def $rc_is_success(OB_USER_NORMAL_RESULT pobinvoke pdestructionframe) = true
def $rc_is_success(ptask) = false -- otherwise
dec $rc_frame_exit(ptask*) : pdestructionframe?
def $rc_frame_exit((DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*) = $rc_frame_exit(ptask_tail*)
def $rc_frame_exit((DESTRUCTOR_FRAME_EXIT pdestructionframe) :: ptask_tail*) = (pdestructionframe)
def $rc_frame_exit(ptask*) = eps -- otherwise
dec $rc_phase(pstate, nat) : bool
def $rc_phase(S, 0) = true
  -- if S.TODO = (AT porigin (STMT (NStmtUnset phpType25 metadata))) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if $ob_user_context_valid(S, pcallcontext)
def $rc_phase(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION =/= eps
def $rc_phase(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.FRAME = (pdestructionframe)
  -- if pdestructionframe.PENDING = eps
def $rc_phase(S, 3) = true -- if S.TODO = (OB_USER_NORMAL_PENDING pobinvoke pdestructionframe) :: ptask_tail*
def $rc_phase(S, 4) = true
  -- if S.TODO = (THROW_SEARCH n) :: eps
  -- if S.CURRENT = (pcallcontext)
  -- if $ob_user_context_valid(S, pcallcontext)
def $rc_phase(S, 5) = true
  -- if S.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (OB_USER_RESULT pobinvoke) :: ptask_tail*
  -- if pdestructionframe.PENDING =/= eps
def $rc_phase(S, 6) = true -- if S.TODO = (OB_USER_FAIL_ARGS pobinvoke n) :: ptask_tail*
def $rc_phase(S, 7) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = OUTPUT_BORROWED_TARGET pcalltarget
  -- if S.TODO = (AT porigin (STMT (NStmtReturn phpType5 metadata))) :: ptask_tail*
def $rc_phase(S, 8) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.FRAME = (pdestructionframe)
  -- if pdestructionframe.PENDING =/= eps
def $rc_phase(S, 9) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.FRAME = (pdestructionframe)
  -- if pdestructionframe.PENDING = eps
def $rc_phase(S, n) = false -- otherwise
dec $rc_seek(pstate, nat, nat) : pstate
def $rc_seek(S, n_phase, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $rc_seek(S, n_phase, n) = S -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if $rc_phase(S, n_phase)
def $rc_seek(S, n_phase, 0) = S -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if ~$rc_phase(S, n_phase)
def $rc_seek(S, n_phase, n) = $rc_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$rc_phase(S, n_phase) /\ $(n > 0)
"""


def bytes_expr(value):
    return '$base64(' + json.dumps(sources.base64.b64encode(value).decode()) + ')'


def valid(state):
    return ['$call_descriptors_valid(' + state + ')', '$heap_valid($heap_graph(' + state + '))',
            '$output_state_valid(' + state + ')']


def budget(state, target):
    return [target + ' = $drive_steps(' + state + ', 0)', target + '.COMPLETION = BUDGET',
            target + '.TODO = ' + state + '.TODO', target + '.OUTPUTBUFFERS = ' + state + '.OUTPUTBUFFERS',
            target + '.DESTRUCTION = ' + state + '.DESTRUCTION', *valid(target)]


def seek(state, phase, target):
    return [target + '_found = $rc_seek(' + state + ', ' + str(phase) + ', 512)',
            target + r'_found.COMPLETION = NORMAL \/ ' + target + '_found.COMPLETION = BUDGET',
            target + ' = ' + target + '_found[.COMPLETION = NORMAL]',
            '$rc_phase(' + target + ', ' + str(phase) + ')', *valid(target)]


def fingerprint():
    inputs = sources.fingerprint()
    for name in ('tests/semantics/output_result_cleanup_state.py', 'tests/semantics/output_result_cleanup_review_sources.py',
                 'tests/semantics/_build/default/numeric_runner.exe'):
        inputs[name] = sources.common.sha(ROOT / name)
    return inputs


def assertions(name, fixture, directory, path):
    phase = {'callee-wrapper': 0, 'normal-return-cleanup': 2, 'body-throw-unsealed': 4, 'borrowed-receiver': 7}[name]
    checks = ['S_initial = $php_file_run(' + fixture + ', 0, ' + bytes_expr(os.fsencode(path)) + ', ' + bytes_expr(os.fsencode(directory)) + ')',
              'S_initial.COMPLETION = BUDGET', *valid('S_initial'), *seek('S_initial', phase, 'S_reached'),
              *budget('S_reached', 'S_budget')]
    if name == 'callee-wrapper':
        checks += ['S_reached.CURRENT = (pcallcontext_callback)',
                   '$ob_user_context(pcallcontext_callback, S_reached.CURRENT, S_reached.FRAMES) = (pobinvoke)',
                   'S_reached.FRAMES = pframe :: pframe_tail*',
                   'pframe.TODO = (OB_USER_RESULT pobinvoke) :: ptask_native*',
                   '$ob_user_fci_arguments(pobinvoke)',
                   '$lookup(S_reached.ENV, ([98])) = (n_argument)',
                   'S_reached.STORE[n_argument] = DEFINED (POBJECT n_object)',
                   '$heap_owners($heap_graph(S_reached), HCELL n_argument) = 1',
                   '$heap_owners($heap_graph(S_reached), HOBJECT n_object) = 1',
                   '$ob_user_running(S_reached)',
                   '$output_selected(S_reached, pobinvoke) = (poutputbuffer)',
                   r'poutputbuffer.FLAGS = 113 /\ poutputbuffer.BYTES = ([65])',
                   'S_forged = S_reached[.FRAMES = pframe[.TODO = (OB_USER_RESULT pobinvoke[.SENT = [REFERENCE n_argument, KNOWN (PINT pobinvoke.PHASE)]]) :: ptask_native*] :: pframe_tail*]',
                   '~$ob_user_context_valid(S_forged, pcallcontext_callback)',
                   'S_caller = $constant_frame_scope(S_reached, pframe, pframe_tail*)',
                   '~$call_task_valid(S_caller, OB_USER_RESULT pobinvoke[.SENT = [REFERENCE n_argument, KNOWN (PINT pobinvoke.PHASE)]])',
                   *seek('S_reached', 1, 'S_child'),
                   'S_child.CURRENT = (pcallcontext_destructor)',
                   '$destructor_context_call(pcallcontext_destructor, S_child.CURRENT, S_child.FRAMES) = (pdestructorcall)',
                   'pdestructorcall.OPERATION = (pdestructionoperation)',
                   'pdestructorcall.CALLER = (pcallcontext_callback)',
                   'pdestructorcall.OBJECT = n_object',
                   '$ob_user_running(S_child)', *budget('S_child', 'S_child_budget')]
    elif name == 'normal-return-cleanup':
        checks += ['S_reached.CURRENT = (pcallcontext_destructor)',
                   '$destructor_context_call(pcallcontext_destructor, S_reached.CURRENT, S_reached.FRAMES) = (pdestructorcall)',
                   'pdestructorcall.FRAME = (pdestructionframe_success)',
                   'pdestructorcall.OPERATION = eps',
                   'pdestructionframe_success.PENDING = eps',
                   'pdestructionframe_success.VALUE = KNOWN pvalue_return',
                   '$string_bytes(pvalue_return) = ([88])',
                   'S_reached.FRAMES = pframe :: pframe_tail*',
                   '$rc_success(pframe.TODO) = (OB_USER_NORMAL_RESULT pobinvoke pdestructionframe_success)',
                   'pobinvoke.CALL = OB_API pconfigcall',
                   '$ob_user_fci_arguments(pobinvoke)', '$ob_user_running(S_reached)',
                   'pdestructorcall.USER',
                   r'pcallcontext_destructor.CALLSITE = eps /\ pcallcontext_destructor.LINE = $(-1)',
                   'S_caller = $destructor_boundary_scope(S_reached, pdestructorcall, S_reached.FRAMES)',
                   '$ob_callee_cleanup_call(S_caller, pdestructionframe_success, S_caller.TODO) = (pconfigcall)',
                   '$ob_callee_cleanup_call(S_caller, pdestructionframe_success, eps) = eps',
                   '$ob_callee_cleanup_call(S_caller, pdestructionframe_success[.FUNCTION = pcallcontext_destructor.FUNCTION], S_caller.TODO) = eps',
                   *seek('S_initial', 9, 'S_enter'),
                   'S_enter.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_enter_tail*',
                   '$destructor_enter_valid(S_enter, pdestructorcall)',
                   'pdestructorcall.SITE = eps',
                   '$ob_callee_cleanup_call(S_enter, pdestructionframe_success, S_enter.TODO) = (pconfigcall)',
                   '~$destructor_context_valid(S_reached[.CURRENT = (pcallcontext_destructor[.CALLSITE = (pconfigcall.SITE)])], pcallcontext_destructor[.CALLSITE = (pconfigcall.SITE)])',
                   '$eval_exception_trace_raw(S_reached) = [ptraceframe_destructor, ptraceframe_api]',
                   r'ptraceframe_destructor.FILE = eps /\ ptraceframe_destructor.LINE = $(-1)',
                   r'ptraceframe_api.FILE = $call_sourcefile(S_reached.FILES, pconfigcall.SITE) /\ ptraceframe_api.LINE = pconfigcall.LINE /\ ptraceframe_api.FUNCTION = $intrinsic_name(pconfigcall.KIND)',
                   '$output_selected(S_reached, pobinvoke) = (poutputbuffer)',
                   r'poutputbuffer.FLAGS = 113 /\ poutputbuffer.BYTES = ([65])',
                   *seek('S_reached', 3, 'S_pending'),
                   'S_pending.TODO = (OB_USER_NORMAL_PENDING pobinvoke pdestructionframe_pending) :: ptask_native*',
                   'pdestructionframe_pending.PENDING = (n_pending)',
                   'pdestructionframe_pending = pdestructionframe_success[.PENDING = (n_pending)]',
                   '$throwable_live(S_pending, n_pending)',
                   'S_pending.DESTRUCTION.FRAMES = eps',
                   '$ob_user_running(S_pending)',
                   '~$call_task_valid(S_pending, OB_USER_NORMAL_PENDING pobinvoke pdestructionframe_success)',
                   '~$call_task_valid(S_pending, OB_USER_NORMAL_PENDING pobinvoke pdestructionframe_pending[.FUNCTION = pcallcontext_destructor.FUNCTION])',
                   '~$call_task_valid(S_pending, OB_USER_NORMAL_PENDING pobinvoke pdestructionframe_pending[.CALLER = (pcallcontext_destructor)])',
                   '~$call_task_valid(S_pending[.ORIGIN = eps], OB_USER_NORMAL_PENDING pobinvoke pdestructionframe_pending)',
                   '~$call_task_valid(S_pending, OB_USER_NORMAL_PENDING pobinvoke[.SENT = eps] pdestructionframe_pending)',
                   '~$call_task_valid(S_pending, OB_USER_NORMAL_PENDING pobinvoke[.CALL = OB_API pconfigcall_forged] pdestructionframe_pending)',
                   *budget('S_pending', 'S_pending_budget'),
                   'S_commit_found = $drive_steps(S_pending, 1)',
                   'S_commit = S_commit_found[.COMPLETION = NORMAL]', *valid('S_commit'),
                   'S_commit.TODO = (OB_USER_NORMAL_COMMIT pobinvoke_commit pdestructionframe_pending poboutput) :: ptask_native*',
                   'pobinvoke_commit = pobinvoke[.SENT = eps]',
                   'poboutput.VALUE = pvalue_return', 'poboutput.BYTES = ([88])',
                   '~$call_task_valid(S_commit, OB_USER_NORMAL_COMMIT pobinvoke_commit pdestructionframe_pending[.PENDING = eps] poboutput)',
                   '$output_selected(S_commit, pobinvoke_commit) = (poutputbuffer_commit)',
                   r'poutputbuffer_commit.FLAGS = 113 /\ poutputbuffer_commit.BYTES = ([65,68,49])',
                   '$ob_user_running(S_commit)']
        # A real alternate API site is not needed: the same call with another kind
        # must fail its source certificate before it can change the finish mode.
        insertion = checks.index('~$call_task_valid(S_pending, OB_USER_NORMAL_PENDING pobinvoke[.CALL = OB_API pconfigcall_forged] pdestructionframe_pending)')
        checks[insertion:insertion] = ['pconfigcall_forged = pconfigcall[.KIND = INTRINSIC_OB_END_CLEAN]']
    elif name == 'body-throw-unsealed':
        checks += ['S_reached.TODO = [THROW_SEARCH n_pending]',
                   'S_reached.RESULT = KNOWN PNULL',
                   'S_reached.CURRENT = (pcallcontext_callback)',
                   '$ob_user_context(pcallcontext_callback, S_reached.CURRENT, S_reached.FRAMES) = (pobinvoke)',
                   '$ob_user_fci_arguments(pobinvoke)',
                   'S_raw = $restore_frame_raw(S_reached)',
                   'S_release = $frame_release(S_reached, S_raw)',
                   '$generator_frame_release(S_reached, S_release) = S_release',
                   '$rc_success(S_release.TODO) = eps',
                   '$rc_frame_exit(S_release.TODO) = (pdestructionframe_initial)',
                   'pdestructionframe_initial.VALUE = KNOWN PNULL',
                   'pdestructionframe_initial.PENDING = (n_pending)',
                   *seek('S_reached', 8, 'S_child'),
                   'S_child.CURRENT = (pcallcontext_destructor)',
                   '$destructor_context_call(pcallcontext_destructor, S_child.CURRENT, S_child.FRAMES) = (pdestructorcall)',
                   'pdestructorcall.FRAME = (pdestructionframe_initial)',
                   'pdestructorcall.USER',
                   r'pcallcontext_destructor.CALLSITE = eps /\ pcallcontext_destructor.LINE = $(-1)',
                   'S_caller = $destructor_boundary_scope(S_child, pdestructorcall, S_child.FRAMES)',
                   '$rc_success(S_caller.TODO) = eps',
                   '$ob_callee_cleanup_call(S_caller, pdestructionframe_initial, S_caller.TODO) = (pconfigcall)',
                   '$ob_callee_cleanup_call(S_caller, pdestructionframe_initial[.PENDING = eps], S_caller.TODO) = eps',
                   '$eval_exception_trace_raw(S_child) = [ptraceframe_destructor, ptraceframe_api]',
                   r'ptraceframe_destructor.FILE = eps /\ ptraceframe_destructor.LINE = $(-1)',
                   r'ptraceframe_api.FILE = $call_sourcefile(S_child.FILES, pconfigcall.SITE) /\ ptraceframe_api.LINE = pconfigcall.LINE /\ ptraceframe_api.FUNCTION = $intrinsic_name(pconfigcall.KIND)',
                   *seek('S_reached', 5, 'S_exit'),
                   'S_exit.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe_pending) :: (OB_USER_RESULT pobinvoke) :: ptask_native*',
                   'pdestructionframe_pending.VALUE = KNOWN PNULL',
                   'pdestructionframe_pending.PENDING = (n_pending)',
                   '$rc_success(S_exit.TODO) = eps',
                   'S_next_found = $drive_steps(S_exit, 1)',
                   'S_next = S_next_found[.COMPLETION = NORMAL]', *valid('S_next'),
                   'S_next.TODO = (THROW_SEARCH n_pending) :: (OB_USER_RESULT pobinvoke) :: ptask_native*',
                   *seek('S_next', 6, 'S_args'),
                   'S_args.TODO = (OB_USER_FAIL_ARGS pobinvoke_failed n_pending) :: ptask_native*',
                   '$ob_user_fci_arguments(pobinvoke_failed)',
                   '~$call_task_valid(S_args, OB_USER_FAIL_ARGS pobinvoke_failed[.SENT = eps] n_pending)',
                   '$ob_user_running(S_args)', *budget('S_args', 'S_args_budget')]
    else:
        checks += ['S_reached.CURRENT = (pcallcontext_callback)',
                   'pcallcontext_callback.TARGET = OUTPUT_BORROWED_TARGET pcalltarget',
                   'pcallcontext_callback.RECEIVER = (n_receiver)',
                   '~((HOBJECT n_receiver) <- S_reached.ALLOCATIONS)',
                   '$call_receiver_roots(pcallcontext_callback) = eps',
                   '~((HOBJECT n_receiver) <- $call_context_roots(S_reached.CURRENT))',
                   '$ob_user_context_valid(S_reached, pcallcontext_callback)',
                   '~$ob_user_context_valid(S_reached[.CURRENT = (pcallcontext_callback[.TARGET = pcalltarget])], pcallcontext_callback[.TARGET = pcalltarget])',
                   '$lookup(S_reached.ENV, ([98])) = (n_argument)',
                   'S_reached.STORE[n_argument] = DEFINED (POBJECT n_object)',
                   '$heap_owners($heap_graph(S_reached), HCELL n_argument) = 1',
                   '$heap_owners($heap_graph(S_reached), HOBJECT n_object) = 1',
                   '$ob_user_context(pcallcontext_callback, S_reached.CURRENT, S_reached.FRAMES) = (pobinvoke)',
                   'pobinvoke.BUFFER.HANDLER = (poutputhandler)',
                   'pcalltarget = poutputhandler.ENTRY.TARGET',
                   '$ob_user_running(S_reached)', '~$ob_user_access_pending(S_reached)',
                   'S_reached.TODO = (AT porigin_return (STMT (NStmtReturn phpType5_return metadata_return))) :: ptask_native*',
                   'S_read = S_reached[.TODO = [EVAL (NExprVariable (BYTES "dGhpcw==") metadata_return)]]',
                   '$ob_user_access_pending(S_read)',
                   'S_refused = $output_guard(S_read)',
                   'S_refused.COMPLETION = UNSUPPORTED "access through a retired output-handler receiver"',
                   'S_refused.ALLOCATIONS = S_read.ALLOCATIONS',
                   'S_refused.RESULT = S_read.RESULT', 'S_refused.BASE = S_read.BASE',
                   'S_prior = S_read[.COMPLETION = UNSUPPORTED "prior refusal"]',
                   '$output_guard(S_prior) = S_prior',
                   'S_host = S_read[.COMPLETION = SOURCE_PENDING]',
                   '$output_guard(S_host) = S_host']
    checks += ['S_done = $drive_steps(S_reached, 1024)',
               r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
               'S_done.OUTPUTBUFFERS = eps', '$rc_output(S_done.EVENTS) = ' + bytes_expr(CASES[name][1]), *valid('S_done')]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact group IDs')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare', action='store_true', help='write checked fixtures without numeric execution')
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(set(selected)) == len(selected) and all(name in CASES for name in selected)
    out = args.output or Path(tempfile.mkdtemp(prefix='output-result-cleanup-state-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': sources.subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'before': fingerprint(), 'profile': sources.common.PROFILE, 'selected': selected,
              'groups': [], 'passed': False, 'completed': False, 'prepared': args.prepare}
    bodies = []
    print(out, flush=True)
    try:
        for index, name in enumerate(selected):
            directory = out / name; directory.mkdir()
            source, expected = CASES[name]; path = directory / 'source.php'; path.write_bytes(source)
            if not args.prepare:
                native = sources.common.run([str(ROOT / '.tools/php/bin/php'), '-n', *sources.common.FLAGS, str(path)], directory, 'native', 10)
                assert native.returncode == 0 and native.stdout == expected and not native.stderr, (name, native.stdout, native.stderr)
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
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
            bodies.append('dec $rc_case_' + str(index) + '() : bool\ndef $rc_case_' + str(index) + '() = true\n' +
                          ''.join('  -- if ' + check + '\n' for check in checks))
            report['groups'].append({'id': name, 'premises': len(checks), 'source_sha256': sources.common.sha(path)})
        fixture = out / 'state.watsup'
        fixture.write_text(PREFIX + '\n'.join(bodies) + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if $rc_case_' + str(index) + '()\n' for index in range(len(bodies))))
        report['fixture_sha256'] = sources.common.sha(fixture)
        if not args.prepare:
            modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
            result = sources.common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                         *[str(ROOT / name) for name in modules], str(fixture)], out, 'state', 120)
            assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, (result.returncode, result.stdout, result.stderr)
            report.update(passed=True, completed=True)
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = fingerprint()
        report['passed'] = report['passed'] and report['before'] == report['after']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert args.prepare or report['passed'] and report['completed']


if __name__ == '__main__':
    main()
