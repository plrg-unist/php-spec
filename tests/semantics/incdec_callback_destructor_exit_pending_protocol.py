#!/usr/bin/env python3
"""Source-reached internal-exit previous ownership through helper and cleanup."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import incdec_callback_destructor_exit_pending_cases as cases
import incdec_callback_destructor_exit_protocol as previous_protocol
import incdec_warning_protocol as update_protocol
import integer_operator_warning_protocol as runner

CASES = tuple(cases.CASES)
HELPERS = previous_protocol.HELPERS + r'''
dec $callback_previous_frontier(pstate, nat) : bool
def $callback_previous_frontier(S, 0) = true
  -- if S.TODO = (EXIT_INVOKE pexitcall) :: ptask_tail*
  -- if $update_callback_destructor_exit_entered(S)
def $callback_previous_frontier(S, 1) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation_original z 0) :: ptask_tail*
def $callback_previous_frontier(S, 2) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation_original z 0
def $callback_previous_frontier(S, 3) = true
  -- if S.TODO = [UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation z 1]
def $callback_previous_frontier(S, 4) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation_original z 2) :: ptask_tail*
def $callback_previous_frontier(S, n) = false -- otherwise
dec $callback_previous_seek(pstate, nat, nat) : pstate
def $callback_previous_seek(S, n_stage, n) = S -- if $callback_previous_frontier(S, n_stage)
def $callback_previous_seek(S, n_stage, n) = S
  -- if ~$callback_previous_frontier(S, n_stage)
  -- if ~$update_exit_resumable(S) \/ n = 0
def $callback_previous_seek(S, n_stage, n) = $callback_previous_seek($drive_steps($update_exit_resume(S), 1), n_stage, $nabs($(n - 1)))
  -- if ~$callback_previous_frontier(S, n_stage)
  -- if $update_exit_resumable(S) /\ $(n > 0)
'''


def conditions(name, program, path, stdout):
    empty = name == CASES[1]
    null = name == CASES[2]
    status = cases.EXIT_CODES[name]
    stored = 73 if empty else 99
    prefix = 'H:8192;L:1;D:1;D-E;' if empty else ('H:2;L:1:1;D:1:1;' if null else 'H:2;L:1;D:1;')
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_invoke = $callback_previous_seek(S_initial, 0, 2500)[.COMPLETION = NORMAL]',
        'S_invoke.TODO = (EXIT_INVOKE pexitcall) :: ptask_dtail*',
        '$exit_invoke_valid(S_invoke, pexitcall)',
        '$update_callback_destructor_exit_entered(S_invoke)', '$update_warning_exit_unwind(S_invoke)',
        '$call_descriptors_valid(S_invoke)', '$heap_valid($heap_graph(S_invoke))',
        'S_invoke.FRAMES = pframe :: pframe_tail*',
        'S_saved = $constant_frame_scope(S_invoke, pframe, pframe_tail*)',
        'S_saved.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup 23 2) :: ptask_tail*',
        '$update_callback_previous_return(S_saved)', '~$update_callback_destructor_exit_return(S_saved)',
        'pdestructorcall.OPERATION = (pdestructionoperation)',
        'pdestructorcall.PENDING = (n_pending)', 'pdestructionoperation.PENDING = (n_pending)',
        '$throwable_live(S_saved, n_pending)',
        '$heap_owners($heap_prune($heap_graph(S_saved)), HOBJECT n_pending) = 2',
        'pdestructionoperation.SOURCE = ERROR_HANDLER_CLEAN perrorcall',
        'pdestructionoperation.CLEANUP = (pdestructioncleanup)',
        'pdestructioncleanup.RELEASED', 'pdestructioncleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall',
        'perrorcall.RESUME = UPDATE_WARNING_RESTORE pupdatewarning',
        'perrorcall.CALLBACK = POBJECT n_handler', 'pdestructorcall.OBJECT = n_handler',
        'pdestructorcall.RELEASE = (pdestructionrelease_source)',
        'pdestructionrelease_source.JOBS = pdestructionjob :: pdestructionjob_tail*',
        '$destruction_job_node(pdestructionjob) = (HOBJECT n_handler)',
        'pdestructionrelease = pdestructionrelease_source[.JOBS = pdestructionjob_tail*]',
        '$destructor_local_cells(S_invoke.ENV, S_invoke.SYMBOLS) = eps',
        'S_invoke.HELD = eps', '$tasks_nodes(S_invoke.TODO) = eps',
        '$heap_owners($heap_prune($heap_graph(S_invoke)), HOBJECT n_handler) = 2',
        '$update_warning_pointer_value(S_saved, pupdatewarning.POINTER) = (DEFINED (PINT ' + str(stored) + '))',
        'S_invoke.EXITSTATUS = 23',
        'PhpStep: S_invoke ~> S_requested',
        'S_requested.EXITSTATUS = ' + str(status),
        '$integer_outputs(S_requested.EVENTS) = ($ptascii(' + json.dumps(prefix) + '))',
        'S_unwind = $callback_destructor_exit_unwind_input(S_requested, ' + str(status) + ')',
        '$call_descriptors_valid(S_unwind)', '$heap_valid($heap_graph(S_unwind))',
        'S_return = $restore_frame(S_unwind)',
        '$update_callback_previous_return(S_return)', '$call_descriptors_valid(S_return)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HOBJECT n_handler) = 1',
        '~$update_callback_previous_return(S_return[.CODE = eps])',
        '~$update_callback_previous_return(S_return[.FRAMES = [pframe]])',
        '~$update_callback_previous_source(S_return, pdestructionoperation[.PENDING = eps], ' + str(status) + ')',
        '~$update_callback_previous_source(S_return, pdestructionoperation[.CLEANUP = (pdestructioncleanup[.RELEASED = false])], ' + str(status) + ')',
        '~$update_callback_previous_source(S_return, pdestructionoperation[.VALUE = KNOWN (PBOOL true)], ' + str(status) + ')',
        '~$update_callback_previous_source(S_return, pdestructionoperation[.CALLER = S_invoke.CURRENT], ' + str(status) + ')',
        '~$update_callback_previous_source(S_return, pdestructionoperation, 2147483648)',
        'PhpStep: S_unwind ~> S_resumed',
        '$call_descriptors_valid(S_resumed)', '$heap_valid($heap_graph(S_resumed))',
        'S_resumed.DESTRUCTION.OPERATIONS = [pdestructionoperation_rebased]',
        'pdestructionoperation_rebased = pdestructionoperation[.PENDING = eps]',
        '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_rebased) = eps',
        '$heap_owners($heap_prune($heap_graph(S_resumed)), HOBJECT n_pending) = 2',
        'S_raw = $callback_previous_seek(' + update_protocol.transitioned('S_unwind', 'S_resumed') + ', 1, 2500)[.COMPLETION = NORMAL]',
        'S_raw.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_rebased) :: (UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation ' + str(status) + ' 0) :: ptask_tail*',
        '$call_descriptors_valid(S_raw)', '$heap_valid($heap_graph(S_raw))',
        '~((HOBJECT n_handler) <- S_raw.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_raw)), HOBJECT n_handler) = 0',
        '$heap_owners($heap_prune($heap_graph(S_raw)), HOBJECT n_pending) = 2',
        'S_raw.EVENTS = S_requested.EVENTS',
        'PhpStep: S_raw ~> S_finish',
        'S_finish.TODO = (UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation ' + str(status) + ' 0) :: ptask_tail*',
        '$call_descriptors_valid(S_finish)', '$heap_valid($heap_graph(S_finish))',
        '$task_nodes(UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation ' + str(status) + ' 0) = [HOBJECT n_pending]',
        '~$call_task_valid(S_finish, UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation ' + str(status) + ' 3)',
        '$source_static_exit_tail(S_finish, ptask_tail*) = eps',
        'PhpStep: S_finish ~> S_capture',
        'S_capture.TODO = [UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation ' + str(status) + ' 1]',
        'S_capture.COMPLETION = NORMAL',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
        'S_capture.ERRORHANDLER = S_finish.ERRORHANDLER', 'S_capture.ERRORHANDLERS = S_finish.ERRORHANDLERS',
        'S_capture.EVENTS = S_finish.EVENTS',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HOBJECT n_pending) = 2',
        '$lookup(S_finish.ENV, $ptascii("v")) = (n_result)', 'S_capture.STORE[n_result] = DEFINED (PINT 100)',
        'S_parent = $callback_previous_seek(' + update_protocol.transitioned('S_finish', 'S_capture') + ', 2, 2500)[.COMPLETION = NORMAL]',
        'S_parent.TODO = (DESTRUCTOR_ENTER pdestructorcall_parent) :: ptask_parent*',
        'n_parent = pdestructorcall_parent.OBJECT', 'n_parent =/= n_handler', 'n_parent =/= n_pending',
        '$heap_owners($heap_prune($heap_graph(S_finish)), HOBJECT n_parent) = 1',
        '$heap_owners($heap_prune($heap_graph(S_parent)), HOBJECT n_parent) = 2',
        '$heap_owners($heap_prune($heap_graph(S_parent)), HOBJECT n_pending) = 2',
        '$call_descriptors_valid(S_parent)', '$heap_valid($heap_graph(S_parent))',
        'S_previous = $callback_previous_seek(S_parent, 3, 2500)[.COMPLETION = NORMAL]',
        '$call_descriptors_valid(S_previous)', '$heap_valid($heap_graph(S_previous))',
        'S_previous.DESTRUCTION.OPERATIONS = eps',
        '$heap_owners($heap_prune($heap_graph(S_previous)), HOBJECT n_pending) = 2',
        'PhpStep: S_previous ~> S_released',
        'S_released.TODO = [UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation ' + str(status) + ' 2]',
        'S_released.DESTRUCTION.OPERATIONS = eps',
        '$task_nodes(UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation ' + str(status) + ' 2) = eps',
        '$heap_owners($heap_prune($heap_graph(S_released)), HOBJECT n_pending) = 1',
        'S_cause = ' + update_protocol.transitioned('S_previous', 'S_released'),
        'S_cause.DESTRUCTION.OPERATIONS = [pdestructionoperation_cause]',
        'pdestructionoperation_cause.SOURCE = UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation ' + str(status) + ' 1',
        'pdestructionoperation_cause.PENDING = eps',
        'S_cause.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_cause) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_cause) :: (UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation ' + str(status) + ' 2) :: ptask_cause*',
        'ptask_cause* = eps',
        'pdestructionrelease_cause.JOBS = [DESTRUCTION_VALUE (HOBJECT n_pending)]',
        '$task_nodes(DESTRUCTOR_RELEASE pdestructionrelease_cause) = [HOBJECT n_pending]',
        '$heap_owners($heap_prune($heap_graph(S_cause)), HOBJECT n_pending) = 2',
        '$call_descriptors_valid(S_cause)', '$heap_valid($heap_graph(S_cause))',
        'S_cause_finish = $callback_previous_seek(S_cause, 4, 2500)[.COMPLETION = NORMAL]',
        '$call_descriptors_valid(S_cause_finish)', '$heap_valid($heap_graph(S_cause_finish))',
        '$heap_owners($heap_prune($heap_graph(S_cause_finish)), HOBJECT n_pending) = 1',
        'PhpStep: S_cause_finish ~> S_final',
        'S_final.TODO = [UPDATE_WARNING_CALLBACK_PREVIOUS pdestructionoperation ' + str(status) + ' 2]',
        'S_final.COMPLETION = NORMAL', '$call_descriptors_valid(S_final)',
        'PhpStep: S_final ~> S_exit', 'S_exit.TODO = [EXIT_UNWIND ' + str(status) + ']',
        '$call_descriptors_valid(S_exit)',
        '$drive_steps(S_unwind, 0) = S_unwind[.COMPLETION = BUDGET]',
        'S_budget = $drive_steps(S_requested, 1)', 'S_budget.COMPLETION = BUDGET',
        'S_budget = ' + update_protocol.transitioned('S_unwind', 'S_resumed') + '[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_budget[.COMPLETION = NORMAL], 2500)',
        'S_done.COMPLETION = EXITED ' + str(status), 'S_done.EXITSTATUS = ' + str(status),
        'S_done.TODO = eps', 'S_done.FRAMES = eps',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    if empty:
        checks += ['pupdatewarning.POST', 'pupdatewarning.OP = DECREMENT',
                   '$string_bytes(pupdatewarning.INPUT) = ($ptascii(""))',
                   'S_capture.STORE = S_finish.STORE',
                   '$update_warning_pointer_value(S_parent, pupdatewarning.POINTER) = (DEFINED (PINT 73))']
    else:
        captured = 'PNULL' if null else 'PBOOL true'
        checks += ['~pupdatewarning.POST', 'pupdatewarning.OP = ' + ('DECREMENT' if null else 'INCREMENT'),
                   'pupdatewarning.INPUT = ' + captured,
                   '$update_warning_pointer_value(S_capture, pupdatewarning.POINTER) = (DEFINED (' + captured + '))',
                   '$update_warning_pointer_value(S_parent, pupdatewarning.POINTER) = (DEFINED (' + captured + '))']
    if null:
        checks += ['pupdatewarning.POINTER = UPDATE_CELL n_keep',
                   '$lookup(S_finish.ENV, $ptascii("x")) = (n_peer)', 'n_peer =/= n_keep',
                   'S_capture.STORE[n_peer] = DEFINED (PINT 73)',
                   '$heap_owners($heap_prune($heap_graph(S_finish)), HCELL n_keep) = 1']
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path)
    args, _ = parser.parse_known_args()
    out = args.output
    if out is None:
        out = Path(tempfile.mkdtemp(prefix='incdec-callback-dexit-pending-', dir=runner.ROOT / '.tools'))
        sys.argv += ['--output', str(out)]
    watched = [Path(__file__), Path(cases.__file__), Path(previous_protocol.__file__),
               Path(previous_protocol.callback_protocol.__file__),
               Path(previous_protocol.callback_protocol.exit_protocol.__file__), Path(update_protocol.__file__), Path(runner.__file__)]
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
