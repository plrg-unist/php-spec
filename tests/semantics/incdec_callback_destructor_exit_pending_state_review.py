#!/usr/bin/env python3
"""Reached last-owner lifetime across raw callback exit and request shutdown."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import incdec_callback_destructor_exit_pending_review_cases as cases
import incdec_callback_destructor_exit_protocol as raw_protocol
import incdec_warning_protocol as update_protocol
import integer_operator_warning_protocol as runner

CASES = ('review-callback-dexit-pending-last-owner',)
HELPERS = raw_protocol.HELPERS + r'''
dec $callback_previous_review_frontier(pstate, nat) : bool
def $callback_previous_review_frontier(S, 0) = true
  -- if S.TODO = (UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation z 0) :: ptask_tail*
def $callback_previous_review_frontier(S, 1) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation_original z 0
def $callback_previous_review_frontier(S, 2) = true
  -- if S.TODO = [UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation z 1]
  -- if S.DESTRUCTION.CALLS = eps /\ S.DESTRUCTION.RELEASES = eps /\ S.DESTRUCTION.OPERATIONS = eps
def $callback_previous_review_frontier(S, 3) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation_original z 1
def $callback_previous_review_frontier(S, 4) = true
  -- if S.TODO = [UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation z 2]
  -- if S.DESTRUCTION.CALLS = eps /\ S.DESTRUCTION.RELEASES = eps /\ S.DESTRUCTION.OPERATIONS = eps
def $callback_previous_review_frontier(S, n) = false -- otherwise
dec $callback_previous_review_seek(pstate, nat, nat) : pstate
def $callback_previous_review_seek(S, n_stage, n) = S -- if $callback_previous_review_frontier(S, n_stage)
def $callback_previous_review_seek(S, n_stage, n) = S
  -- if ~$callback_previous_review_frontier(S, n_stage)
  -- if ~$update_exit_resumable(S) \/ n = 0
def $callback_previous_review_seek(S, n_stage, n) = $callback_previous_review_seek($drive_steps($update_exit_resume(S), 1), n_stage, $nabs($(n - 1)))
  -- if ~$callback_previous_review_frontier(S, n_stage)
  -- if $update_exit_resumable(S) /\ $(n > 0)
'''


def conditions(name, program, path, stdout):
    return [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_invoke = $callback_destructor_exit_seek(S_initial, 0, 2500)[.COMPLETION = NORMAL]',
        'S_invoke.TODO = (EXIT_INVOKE pexitcall) :: ptask_current*',
        '$exit_invoke_valid(S_invoke, pexitcall)',
        '$update_callback_destructor_exit_entered(S_invoke)',
        '$update_warning_exit_unwind(S_invoke)',
        '$call_descriptors_valid(S_invoke)', '$heap_valid($heap_graph(S_invoke))',
        'S_invoke.FRAMES = pframe :: pframe_tail*',
        'S_saved = $constant_frame_scope(S_invoke, pframe, pframe_tail*)',
        'S_saved.FRAMES = eps', 'S_saved.CURRENT = eps',
        'S_saved.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup 23 2) :: ptask_tail*',
        'pdestructionoperation.PENDING = (n_pending)', 'pdestructorcall.PENDING = (n_pending)',
        'pdestructorcall.OPERATION = (pdestructionoperation)',
        'pdestructionoperation.SOURCE = ERROR_HANDLER_CLEAN perrorcall',
        'pdestructionoperation.CLEANUP = (pdestructioncleanup)',
        'pdestructioncleanup.RELEASED',
        'perrorcall.CALLBACK = POBJECT n_handler', 'pdestructorcall.OBJECT = n_handler',
        'perrorcall.RESUME = UPDATE_WARNING_RESTORE pupdatewarning',
        'pupdatewarning.INPUT = PBOOL true', 'pupdatewarning.OP = INCREMENT', '~pupdatewarning.POST',
        '$tasks_nodes(ptask_tail*) = [HOBJECT n_parent]',
        'n_pending =/= n_parent', 'n_pending =/= n_handler',
        '$update_callback_previous_return(S_saved)', '~$update_callback_destructor_exit_return(S_saved)',
        '$update_warning_pointer_value(S_saved, pupdatewarning.POINTER) = (DEFINED (PINT 99))',
        'S_global = $global_table_view(S_invoke)',
        '$lookup(S_global.ENV, $ptascii("pending")) = eps',
        '$lookup(S_global.ENV, $ptascii("weak_pending")) = (n_weak_pending_cell)',
        '$lookup(S_global.ENV, $ptascii("weak_handler")) = (n_weak_handler_cell)',
        'S_invoke.STORE[n_weak_pending_cell] = DEFINED (POBJECT n_weak_pending)',
        'S_invoke.STORE[n_weak_handler_cell] = DEFINED (POBJECT n_weak_handler)',
        '$weakref_get(S_invoke, n_weak_pending) = POBJECT n_pending',
        '$weakref_get(S_invoke, n_weak_handler) = POBJECT n_handler',
        '$throwable_previous_id(S_invoke, n_pending) = eps',
        '$heap_owners($heap_prune($heap_graph(S_invoke)), HOBJECT n_pending) = 1',
        '$heap_owners($heap_prune($heap_graph(S_invoke)), HOBJECT n_parent) = 1',
        '~(n_parent <- S_invoke.DESTRUCTION.CALLED)', '~(n_pending <- S_invoke.DESTRUCTION.CALLED)',
        'S_invoke.EXITSTATUS = 23',
        '$integer_outputs(S_invoke.EVENTS) = ($ptascii("H:2;L:1;D:1;"))',
        'PhpStep: S_invoke ~> S_requested',
        'S_requested.COMPLETION = EXITED 17', 'S_requested.EXITSTATUS = 17',
        'S_unwind = $callback_destructor_exit_unwind_input(S_requested, 17)',
        'S_unwind.COMPLETION = NORMAL', 'S_unwind.TODO = [EXIT_UNWIND 17]',
        'S_return = $restore_frame(S_unwind)',
        '$update_callback_previous_return(S_return)',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        '~$update_callback_previous_return(S_return[.CODE = eps])',
        'PhpStep: S_unwind ~> S_handoff',
        'pdestructionoperation_new = pdestructionoperation[.PENDING = eps]',
        'S_handoff.COMPLETION = NORMAL', 'S_handoff.DESTRUCTION.CALLS = eps',
        'S_handoff.DESTRUCTION.OPERATIONS = [pdestructionoperation_new]',
        '(UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation 17 0) <- S_handoff.TODO',
        '$heap_owners($heap_prune($heap_graph(S_handoff)), HOBJECT n_pending) = 1',
        '$heap_owners($heap_prune($heap_graph(S_handoff)), HOBJECT n_parent) = 1',
        '$call_descriptors_valid(S_handoff)', '$heap_valid($heap_graph(S_handoff))',
        'S_handoff.EVENTS = S_requested.EVENTS',
        'S_budget = $drive_steps(S_requested, 1)', 'S_budget.COMPLETION = BUDGET',
        'S_budget = ' + update_protocol.transitioned('S_unwind', 'S_handoff') + '[.COMPLETION = BUDGET]',
        'S_finish = $callback_previous_review_seek(S_budget[.COMPLETION = NORMAL], 0, 2500)[.COMPLETION = NORMAL]',
        'S_finish.TODO = (UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation 17 0) :: ptask_tail*',
        '$call_descriptors_valid(S_finish)', '$heap_valid($heap_graph(S_finish))',
        '$task_nodes(UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation 17 0) = [HOBJECT n_pending]',
        '$task_nodes(UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation 17 1) = [HOBJECT n_pending]',
        '$task_nodes(UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation 17 2) = eps',
        '$heap_owners($heap_prune($heap_graph(S_finish)), HOBJECT n_pending) = 1',
        '$weakref_get(S_finish, n_weak_pending) = POBJECT n_pending',
        '$weakref_get(S_finish, n_weak_handler) = PNULL',
        '~((HOBJECT n_handler) <- S_finish.ALLOCATIONS)',
        '$update_warning_pointer_value(S_finish, pupdatewarning.POINTER) = (DEFINED (PINT 99))',
        '~$update_callback_previous_valid(S_finish, pdestructionoperation, 17, 3)',
        '~$update_callback_previous_valid(S_finish[.CODE = eps], pdestructionoperation, 17, 0)',
        '~$update_callback_previous_valid(S_finish, pdestructionoperation[.PENDING = eps], 17, 0)',
        '~$update_callback_previous_valid(S_finish, pdestructionoperation[.PENDING = (n_handler)], 17, 0)',
        '~$update_callback_previous_valid(S_finish, pdestructionoperation[.VALUE = KNOWN (PINT 99)], 17, 0)',
        '~$update_callback_previous_valid(S_finish, pdestructionoperation[.CLEANUP = (pdestructioncleanup[.RELEASED = false])], 17, 0)',
        '~$update_callback_previous_valid(S_finish, pdestructionoperation, 2147483648, 0)',
        'PhpStep: S_finish ~> S_capture',
        'S_capture.COMPLETION = NORMAL',
        'S_capture.TODO = [UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation 17 1]',
        '$update_warning_pointer_value(S_capture, pupdatewarning.POINTER) = (DEFINED (PBOOL true))',
        'S_capture.ERRORHANDLER = S_finish.ERRORHANDLER', 'S_capture.ERRORHANDLERS = S_finish.ERRORHANDLERS',
        'S_capture.EVENTS = S_finish.EVENTS',
        'S_capture_live = ' + update_protocol.transitioned('S_finish', 'S_capture'),
        'S_capture_live.DESTRUCTION.OPERATIONS = [pdestructionoperation_parent]',
        'pdestructionoperation_parent.SOURCE = UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation 17 0',
        'pdestructionoperation_parent.PENDING = eps',
        '$call_descriptors_valid(S_capture_live)', '$heap_valid($heap_graph(S_capture_live))',
        'S_parent = $callback_previous_review_seek(S_capture_live, 1, 2500)[.COMPLETION = NORMAL]',
        'S_parent.TODO = (DESTRUCTOR_ENTER pdestructorcall_parent) :: ptask_parent*',
        'pdestructorcall_parent.OBJECT = n_parent',
        '$weakref_get(S_parent, n_weak_pending) = POBJECT n_pending',
        '$heap_owners($heap_prune($heap_graph(S_parent)), HOBJECT n_pending) = 1',
        '$update_warning_pointer_value(S_parent, pupdatewarning.POINTER) = (DEFINED (PBOOL true))',
        '$call_descriptors_valid(S_parent)', '$heap_valid($heap_graph(S_parent))',
        'S_hold = $callback_previous_review_seek(S_parent, 2, 2500)[.COMPLETION = NORMAL]',
        'S_hold.TODO = [UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation 17 1]',
        'S_hold.COMPLETION = NORMAL', 'S_hold.SHUTDOWN.PHASE = SHUTDOWN_PENDING',
        '$weakref_get(S_hold, n_weak_pending) = POBJECT n_pending',
        '~(n_pending <- S_hold.DESTRUCTION.CALLED)',
        '$heap_owners($heap_prune($heap_graph(S_hold)), HOBJECT n_pending) = 1',
        '$integer_outputs(S_hold.EVENTS) = ($ptascii("H:2;L:1;D:1;P:1::1::1;"))',
        '$call_descriptors_valid(S_hold)', '$heap_valid($heap_graph(S_hold))',
        'PhpStep: S_hold ~> S_release',
        'S_release.TODO = [UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation 17 2]',
        'S_release.DESTRUCTION.OPERATIONS = eps',
        'S_release_live = ' + update_protocol.transitioned('S_hold', 'S_release'),
        'S_release_live.DESTRUCTION.OPERATIONS = [pdestructionoperation_cause]',
        'pdestructionoperation_cause.SOURCE = UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation 17 1',
        'pdestructionoperation_cause.PENDING = eps',
        'S_release_live.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_cause) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_cause) :: [UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation 17 2]',
        'pdestructionrelease_cause.JOBS = [DESTRUCTION_VALUE (HOBJECT n_pending)]',
        '$call_descriptors_valid(S_release_live)', '$heap_valid($heap_graph(S_release_live))',
        'S_cause = $callback_previous_review_seek(S_release_live, 3, 2500)[.COMPLETION = NORMAL]',
        'S_cause.TODO = (DESTRUCTOR_ENTER pdestructorcall_cause) :: ptask_cause*',
        'pdestructorcall_cause.OBJECT = n_pending',
        '$heap_owners($heap_prune($heap_graph(S_cause)), HOBJECT n_pending) = 2',
        '$weakref_get(S_cause, n_weak_pending) = POBJECT n_pending',
        '$update_warning_pointer_value(S_cause, pupdatewarning.POINTER) = (DEFINED (PBOOL true))',
        '$call_descriptors_valid(S_cause)', '$heap_valid($heap_graph(S_cause))',
        'S_retired = $callback_previous_review_seek(S_cause, 4, 2500)[.COMPLETION = NORMAL]',
        'S_retired.TODO = [UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation 17 2]',
        'S_retired.SHUTDOWN.PHASE = SHUTDOWN_PENDING',
        '$weakref_get(S_retired, n_weak_pending) = PNULL',
        '~((HOBJECT n_pending) <- S_retired.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_retired)), HOBJECT n_pending) = 0',
        '$throwable_member(S_retired, n_pending)',
        '$update_callback_previous_source(S_retired, pdestructionoperation, 17)',
        '$update_callback_previous_valid(S_retired, pdestructionoperation, 17, 2)',
        '~$update_callback_previous_valid(S_retired, pdestructionoperation, 17, 1)',
        '$update_warning_pointer_value(S_retired, pupdatewarning.POINTER) = (DEFINED (PINT 73))',
        '$integer_outputs(S_retired.EVENTS) = ($ptascii("H:2;L:1;D:1;P:1::1::1;Q::1:1;"))',
        '$call_descriptors_valid(S_retired)', '$heap_valid($heap_graph(S_retired))',
        'PhpStep: S_retired ~> S_exit', 'S_exit.TODO = [EXIT_UNWIND 17]',
        '$update_warning_pointer_value(S_exit, pupdatewarning.POINTER) = (DEFINED (PINT 73))',
        'S_exit.EVENTS = S_retired.EVENTS',
        '$drive_steps(S_retired, 0) = S_retired[.COMPLETION = BUDGET]',
        'S_end_budget = $drive_steps(S_retired, 1)',
        'S_end_budget = ' + update_protocol.transitioned('S_retired', 'S_exit') + '[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_end_budget[.COMPLETION = NORMAL], 2500)',
        'S_done.COMPLETION = EXITED 17', 'S_done.EXITSTATUS = 17',
        'S_done.TODO = eps', 'S_done.FRAMES = eps',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path)
    args, _ = parser.parse_known_args()
    out = args.output
    if out is None:
        out = Path(tempfile.mkdtemp(prefix='incdec-callback-previous-review-', dir=runner.ROOT / '.tools'))
        sys.argv += ['--output', str(out)]
    watched = [Path(__file__), Path(cases.__file__), Path(raw_protocol.__file__),
               Path(raw_protocol.callback_protocol.__file__),
               Path(raw_protocol.callback_protocol.exit_protocol.__file__),
               Path(update_protocol.__file__), Path(runner.__file__)]
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    before = {str(p): digest(p) for p in watched}
    runner.CASES, runner.HELPERS, runner.conditions = CASES, HELPERS, conditions
    runner.sources, runner.__file__ = cases, __file__
    passed = runner.main()
    assert before == {str(p): digest(p) for p in watched}
    report = json.loads((out / 'report.json').read_bytes())
    report['helper_inputs'] = before
    for row in report['rows']:
        assert row['native']['interruption'] is None and row['native']['group_after'] == []
        if 'model' in row:
            result = row['model']
            row['passed'] = row['passed'] and result['interruption'] is None and result['group_after'] == []
            row['passed'] = row['passed'] and (out / (row['id'] + '-model.stdout')).read_bytes() == b'true\n'
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed and all(row.get('passed', True) for row in report['rows'])


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
