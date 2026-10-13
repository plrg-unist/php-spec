#!/usr/bin/env python3
"""Reached raw-destructor exit, borrowed restoration and pending exclusion."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import incdec_callback_destructor_exit_review_cases as cases
import incdec_callback_exit_protocol as protocol
import incdec_warning_protocol as update_protocol

CASES = ('review-callback-dexit-null-rebind',
         'review-callback-dexit-cleared-registry',
         'review-callback-dexit-pending-local-throw')
HELPERS = protocol.HELPERS + r'''
dec $callback_dexit_review_frontier(pstate, nat) : bool
def $callback_dexit_review_frontier(S, 0) = true
  -- if S.TODO = (EXIT_INVOKE pexitcall) :: ptask_current*
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup z 2) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = ERROR_HANDLER_CLEAN perrorcall
  -- if perrorcall.RESUME = UPDATE_WARNING_RESTORE pupdatewarning
def $callback_dexit_review_frontier(S, 1) = true
  -- if S.TODO = (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup z 2) :: ptask_tail*
def $callback_dexit_review_frontier(S, n) = false -- otherwise
dec $callback_dexit_review_seek(pstate, nat, nat) : pstate
def $callback_dexit_review_seek(S, n_stage, n) = S -- if $callback_dexit_review_frontier(S, n_stage)
def $callback_dexit_review_seek(S, n_stage, n) = S
  -- if ~$callback_dexit_review_frontier(S, n_stage)
  -- if ~$update_exit_resumable(S) \/ n = 0
def $callback_dexit_review_seek(S, n_stage, n) = $callback_dexit_review_seek($drive_steps($update_exit_resume(S), 1), n_stage, $nabs($(n - 1)))
  -- if ~$callback_dexit_review_frontier(S, n_stage)
  -- if $update_exit_resumable(S) /\ $(n > 0)
'''


def conditions(name, program, path, stdout):
    pending = name == 'review-callback-dexit-pending-local-throw'
    status = cases.EXIT_CODES[name]
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_invoke = $callback_dexit_review_seek(S_initial, 0, 2500)[.COMPLETION = NORMAL]',
        'S_invoke.TODO = (EXIT_INVOKE pexitcall) :: ptask_current*',
        'S_invoke.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup 23 2) :: ptask_tail*',
        'pdestructionoperation.SOURCE = ERROR_HANDLER_CLEAN perrorcall',
        'pdestructionoperation.CLEANUP = (pdestructioncleanup)',
        'pdestructorcall.OPERATION = (pdestructionoperation)',
        'pdestructioncleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall',
        'pdestructioncleanup.RELEASED',
        'perrorcall.CALLBACK = POBJECT n_handler',
        'pdestructorcall.OBJECT = n_handler',
        'perrorcall.RESUME = UPDATE_WARNING_RESTORE pupdatewarning',
        '$tasks_nodes(ptask_tail*) = [HOBJECT n_parent]',
        'n_parent =/= n_handler',
        '~(n_parent <- S_invoke.DESTRUCTION.CALLED)',
        '$heap_owners($heap_prune($heap_graph(S_invoke)), HOBJECT n_parent) = 1',
        '$call_descriptors_valid(S_invoke)', '$heap_valid($heap_graph(S_invoke))',
        '$update_callback_destructor_exit_pending(S_invoke)',
        '$update_warning_exit_pending(S_invoke)',
        '$destructor_local_cells(S_invoke.ENV, S_invoke.SYMBOLS) = eps',
        'S_invoke.HELD = eps', '$tasks_nodes(S_invoke.TODO) = eps',
        'S_invoke.EXITSTATUS = 23',
        'S_global = $global_table_view(S_invoke)',
        '$lookup(S_global.ENV, $ptascii("v")) = (n_value)',
        '$lookup(S_global.ENV, $ptascii("weak")) = (n_weak_cell)',
        'S_invoke.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
        '$weakref_get(S_invoke, n_weak) = POBJECT n_handler',
        'S_invoke.STORE[n_value] = DEFINED (PINT 100)',
        '$update_warning_pointer_value($constant_frame_scope(S_invoke, pframe, pframe_tail*), pupdatewarning.POINTER) = (DEFINED (PINT 99))',
        'pdestructorcall.RELEASE = (pdestructionrelease_source)',
        'pdestructionrelease_source.JOBS = pdestructionjob :: pdestructionjob_tail*',
        '$destruction_job_node(pdestructionjob) = (HOBJECT n_handler)',
        'pdestructionrelease = pdestructionrelease_source[.JOBS = pdestructionjob_tail*]',
        'PhpStep: S_invoke ~> S_requested',
        'S_requested.COMPLETION = EXITED ' + str(status),
        'S_requested.EXITSTATUS = ' + str(status),
        'S_requested.STORE = S_invoke.STORE',
        '$heap_owners($heap_prune($heap_graph(S_requested)), HOBJECT n_parent) = 1',
        '~(n_parent <- S_requested.DESTRUCTION.CALLED)',
        # These are the two internal inputs used by148, not extra public steps.
        'S_view = $constant_frame_scope(S_requested, pframe, pframe_tail*)',
        '$update_callback_destructor_exit_call(S_view) = (pdestructorcall)',
        '~$update_callback_destructor_exit_pending(S_requested[.CODE = eps])',
    ]
    if pending:
        return checks + [
            'pdestructionoperation.PENDING = (n_second)',
            'pdestructorcall.PENDING = (n_second)',
            '$lookup(S_global.ENV, $ptascii("second")) = (n_second_cell)',
            'S_requested.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            '$throwable_live(S_requested, n_second)',
            '$throwable_previous_id(S_requested, n_second) = eps',
            '$heap_owners($heap_prune($heap_graph(S_requested)), HOBJECT n_second) = 2',
            '~$update_callback_destructor_exit_return(S_view)',
            '~$update_callback_destructor_exit_entered(S_requested)',
            '~$update_warning_exit_unwind(S_requested)',
            'S_guard = $exit_start_unwind(S_requested, ' + str(status) + ')',
            'S_guard = S_requested[.COMPLETION = UNSUPPORTED "increment/decrement warning exit continuation"]',
            '$call_descriptors_valid(S_guard)', '$heap_valid($heap_graph(S_guard))',
            '$heap_owners($heap_prune($heap_graph(S_guard)), HOBJECT n_parent) = 1',
            '$heap_owners($heap_prune($heap_graph(S_guard)), HOBJECT n_second) = 2',
            '~(n_parent <- S_guard.DESTRUCTION.CALLED)',
            '$update_warning_pointer_value($constant_frame_scope(S_guard, pframe, pframe_tail*), pupdatewarning.POINTER) = (DEFINED (PINT 99))',
            '$integer_outputs(S_guard.EVENTS) = ($ptascii("H:2;L:1;D:1;"))',
            '$drive_steps(S_requested, 2500) = S_guard',
        ]
    checks += [
        'pdestructionoperation.PENDING = eps', 'pdestructorcall.PENDING = eps',
        '$update_callback_destructor_exit_return(S_view)',
        '$update_callback_destructor_exit_entered(S_requested)',
        '$update_warning_exit_unwind(S_requested)',
        '~$update_callback_destructor_exit_entered(S_requested[.HELD = [HOBJECT n_parent]])',
        '~$update_callback_destructor_exit_entered(S_requested[.FRAMES = eps])',
        'S_unwind = $exit_start_unwind(S_requested, ' + str(status) + ')',
        'S_unwind.TODO = [EXIT_UNWIND ' + str(status) + ']',
        'S_unwind.FRAMES = S_requested.FRAMES',
        'S_return = $restore_frame(S_unwind)',
        'S_return.TODO = pframe.TODO',
        '$update_callback_destructor_exit_return(S_return)',
        '$update_warning_exit_pending(S_return)', '~$update_warning_exit_unwind(S_return)',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        '~$update_callback_destructor_exit_return(S_return[.CODE = eps])',
        '~$update_callback_destructor_exit_return(S_return[.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup 23 1) :: ptask_tail*])',
        '~$update_callback_destructor_exit_return(S_return[.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease[.JOBS = (DESTRUCTION_VALUE (HOBJECT n_parent)) :: pdestructionrelease.JOBS]) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup 23 2) :: ptask_tail*])',
        '~$update_callback_destructor_exit_return(S_return[.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup[.RELEASED = false] 23 2) :: ptask_tail*])',
        '~$update_callback_destructor_exit_return(S_return[.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup 2147483648 2) :: ptask_tail*])',
        'PhpStep: S_unwind ~> S_handoff',
        'S_handoff.COMPLETION = NORMAL',
        'S_handoff.FRAMES = S_return.FRAMES', 'S_handoff.CURRENT = S_return.CURRENT',
        'S_handoff.EVENTS = S_requested.EVENTS',
        'S_handoff.EXITSTATUS = ' + str(status),
        'S_handoff.ERRORHANDLER = S_requested.ERRORHANDLER',
        '(UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup ' + str(status) + ' 2) <- S_handoff.TODO',
        '$heap_owners($heap_prune($heap_graph(S_handoff)), HOBJECT n_parent) = 1',
        '~(n_parent <- S_handoff.DESTRUCTION.CALLED)',
        '$update_warning_pointer_value(S_handoff, pupdatewarning.POINTER) = (DEFINED (PINT 99))',
        '$call_descriptors_valid(S_handoff)', '$heap_valid($heap_graph(S_handoff))',
        'S_handoff_budget = $drive_steps(S_requested, 1)',
        'S_handoff_budget.COMPLETION = BUDGET',
        'S_handoff_budget = ' + update_protocol.transitioned('S_unwind', 'S_handoff') + '[.COMPLETION = BUDGET]',
        'S_finish = $callback_dexit_review_seek(S_handoff_budget[.COMPLETION = NORMAL], 1, 2500)[.COMPLETION = NORMAL]',
        'S_finish.TODO = (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup ' + str(status) + ' 2) :: ptask_tail*',
        '$update_callback_exit_valid(S_finish, pdestructioncleanup, ' + str(status) + ', 2)',
        '$call_descriptors_valid(S_finish)', '$heap_valid($heap_graph(S_finish))',
        '~((HOBJECT n_handler) <- S_finish.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_finish), HOBJECT n_handler) = 0',
        '$weakref_get(S_finish, n_weak) = PNULL',
        '$heap_owners($heap_prune($heap_graph(S_finish)), HOBJECT n_parent) = 1',
        '~(n_parent <- S_finish.DESTRUCTION.CALLED)',
        '$update_warning_pointer_value(S_finish, pupdatewarning.POINTER) = (DEFINED (PINT 99))',
        'S_finish.STORE[n_value] = DEFINED (PINT 100)',
        'S_finish.ERRORHANDLER = S_requested.ERRORHANDLER',
        'PhpStep: S_finish ~> S_drop',
        'S_drop.TODO = [EXIT_UNWIND ' + str(status) + ']',
        'S_drop.ERRORHANDLER = S_finish.ERRORHANDLER',
        'S_drop.STORE[n_value] = DEFINED (PINT 100)',
        'S_drop.EXITSTATUS = ' + str(status),
        '$call_descriptors_valid(S_drop)',
        '$drive_steps(S_finish, 0) = S_finish[.COMPLETION = BUDGET]',
        'S_budget = $drive_steps(S_finish, 1)', 'S_budget.COMPLETION = BUDGET',
        'S_budget = ' + update_protocol.transitioned('S_finish', 'S_drop') + '[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_budget[.COMPLETION = NORMAL], 2500)',
        'S_done.COMPLETION = EXITED ' + str(status),
        'S_done.EXITSTATUS = ' + str(status), 'S_done.TODO = eps', 'S_done.FRAMES = eps',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    if name == 'review-callback-dexit-null-rebind':
        checks += [
            'pupdatewarning.INPUT = PNULL', 'pupdatewarning.OP = DECREMENT',
            'pupdatewarning.POINTER = UPDATE_CELL n_old',
            '$lookup(S_global.ENV, $ptascii("keep")) = (n_old)',
            '$lookup(S_global.ENV, $ptascii("x")) = (n_new)',
            '$lookup(S_global.ENV, $ptascii("peer")) = (n_new)',
            'n_old =/= n_new',
            '$heap_owners($heap_prune($heap_graph(S_finish)), HCELL n_old) = 1',
            '$heap_owners($heap_prune($heap_graph(S_finish)), HCELL n_new) = 2',
            'S_finish.STORE[n_new] = DEFINED (PINT 73)',
            'S_drop.STORE[n_old] = DEFINED PNULL',
            'S_drop.STORE[n_new] = DEFINED (PINT 73)',
        ]
    else:
        checks += [
            'pupdatewarning.INPUT = PBOOL true',
            'S_requested.ERRORHANDLER.CALLBACK = eps',
            'S_finish.ERRORHANDLER.CALLBACK = eps',
            'S_drop.ERRORHANDLER.CALLBACK = eps',
            '$update_warning_pointer_value(S_drop, pupdatewarning.POINTER) = (DEFINED (PBOOL true))',
        ]
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path)
    args, _ = parser.parse_known_args()
    out = args.output
    if out is None:
        out = Path(tempfile.mkdtemp(prefix='callback-dexit-review-', dir=protocol.runner.ROOT / '.tools'))
        sys.argv += ['--output', str(out)]
    wrapper = Path(__file__)
    before = hashlib.sha256(wrapper.read_bytes()).hexdigest()
    protocol.CASES, protocol.HELPERS = CASES, HELPERS
    protocol.conditions, protocol.cases = conditions, cases
    passed = protocol.main()
    assert before == hashlib.sha256(wrapper.read_bytes()).hexdigest()
    report = json.loads((out / 'report.json').read_bytes())
    report['helper_inputs'][str(wrapper)] = before
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
