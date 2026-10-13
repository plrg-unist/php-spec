#!/usr/bin/env python3
"""Source-reached raw callback destructor exit and helper return order."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import incdec_callback_destructor_exit_cases as cases
import incdec_callback_exit_protocol as callback_protocol
import incdec_warning_protocol as update_protocol
import integer_operator_warning_protocol as runner

CASES = ('callback-destructor-exit-bool-int17', 'callback-destructor-exit-empty-string')
HELPERS = callback_protocol.HELPERS + r'''
dec $callback_destructor_exit_frontier(pstate, nat) : bool
def $callback_destructor_exit_frontier(S, 0) = true
  -- if S.TODO = (EXIT_INVOKE pexitcall) :: ptask_tail*
  -- if $update_callback_destructor_exit_entered(S)
def $callback_destructor_exit_frontier(S, 1) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = ERROR_HANDLER_CLEAN perrorcall
  -- if perrorcall.RESUME = UPDATE_WARNING_RESTORE pupdatewarning
def $callback_destructor_exit_frontier(S, 2) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = UPDATE_WARNING_CALLBACK_HISTORY pdestructioncleanup z ptask_history*
def $callback_destructor_exit_frontier(S, n) = false -- otherwise
dec $callback_destructor_exit_seek(pstate, nat, nat) : pstate
def $callback_destructor_exit_seek(S, n_stage, n) = S -- if $callback_destructor_exit_frontier(S, n_stage)
def $callback_destructor_exit_seek(S, n_stage, n) = S
  -- if ~$callback_destructor_exit_frontier(S, n_stage)
  -- if ~$update_exit_resumable(S) \/ n = 0
def $callback_destructor_exit_seek(S, n_stage, n) = $callback_destructor_exit_seek($drive_steps($update_exit_resume(S), 1), n_stage, $nabs($(n - 1)))
  -- if ~$callback_destructor_exit_frontier(S, n_stage)
  -- if $update_exit_resumable(S) /\ $(n > 0)
dec $callback_destructor_exit_unwind_input(pstate, int) : pstate
def $callback_destructor_exit_unwind_input(S, z) = $exit_start_unwind(S, z)
  -- if S.COMPLETION = EXITED z
def $callback_destructor_exit_unwind_input(S, z) = S
  -- if S.COMPLETION = NORMAL /\ S.TODO = [EXIT_UNWIND z]
'''


def conditions(name, program, path, stdout):
    empty = name == CASES[1]
    status = cases.EXIT_CODES[name]
    value = 73 if empty else 99
    prefix = 'H:8192;L:1;D:1;' if empty else 'H:2;L:1;D:1:;'
    requested_prefix = prefix + ('Z;' if empty else '')
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_exit = $callback_destructor_exit_seek(S_initial, 0, 2500)[.COMPLETION = NORMAL]',
        'S_exit.TODO = (EXIT_INVOKE pexitcall) :: ptask_dtail*',
        '$exit_invoke_valid(S_exit, pexitcall)',
        '$update_callback_destructor_exit_pending(S_exit)',
        '$update_callback_destructor_exit_entered(S_exit)', '$update_warning_exit_unwind(S_exit)',
        '$call_descriptors_valid(S_exit)', '$heap_valid($heap_graph(S_exit))',
        'S_exit.FRAMES = pframe :: pframe_tail*',
        'S_saved = $constant_frame_scope(S_exit, pframe, pframe_tail*)',
        'S_saved.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup 23 2) :: ptask_tail*',
        '$update_callback_destructor_exit_call(S_saved) = (pdestructorcall)',
        '$update_callback_destructor_exit_return(S_saved)',
        'pdestructorcall.OPERATION = (pdestructionoperation)',
        'pdestructorcall.PENDING = eps', 'pdestructionoperation.PENDING = eps',
        'pdestructionoperation.SOURCE = ERROR_HANDLER_CLEAN perrorcall',
        'pdestructionoperation.CLEANUP = (pdestructioncleanup)',
        'pdestructioncleanup.RELEASED', 'pdestructioncleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall',
        'perrorcall.CALLBACK = POBJECT n_handler', 'pdestructorcall.OBJECT = n_handler',
        'perrorcall.RESUME = UPDATE_WARNING_RESTORE pupdatewarning',
        'pdestructorcall.RELEASE = (pdestructionrelease_source)',
        'pdestructionrelease_source.JOBS = pdestructionjob :: pdestructionjob_tail*',
        '$destruction_job_node(pdestructionjob) = (HOBJECT n_handler)',
        'pdestructionrelease = pdestructionrelease_source[.JOBS = pdestructionjob_tail*]',
        '$heap_owners($heap_prune($heap_graph(S_exit)), HOBJECT n_handler) = 2',
        '$destructor_local_cells(S_exit.ENV, S_exit.SYMBOLS) = eps',
        'S_exit.HELD = eps', '$tasks_nodes(S_exit.TODO) = eps',
        'S_exit.EXITSTATUS = 23',
        '$integer_outputs(S_exit.EVENTS) = ($ptascii(' + json.dumps(prefix) + '))',
        '$update_warning_pointer_value(S_saved, pupdatewarning.POINTER) = (DEFINED (PINT ' + str(value) + '))',
        'PhpStep: S_exit ~> S_requested',
        'S_requested.EXITSTATUS = ' + str(status),
        '$integer_outputs(S_requested.EVENTS) = ($ptascii(' + json.dumps(requested_prefix) + '))',
        'S_unwind = $callback_destructor_exit_unwind_input(S_requested, ' + str(status) + ')',
        'S_unwind.COMPLETION = NORMAL', 'S_unwind.TODO = [EXIT_UNWIND ' + str(status) + ']',
        'S_unwind.CURRENT = S_exit.CURRENT', 'S_unwind.FRAMES = S_exit.FRAMES',
        'S_unwind.RESULT = KNOWN PNULL', 'S_unwind.BASE = BASE_VALUE (KNOWN PNULL)',
        '$call_descriptors_valid(S_unwind)', '$heap_valid($heap_graph(S_unwind))',
        # This is the actual internal projection in148 exit-unwind-frame, not a public step.
        'S_return = $restore_frame(S_unwind)',
        'S_return.TODO = S_saved.TODO',
        '$update_callback_destructor_exit_return(S_return)',
        '$update_callback_destructor_exit_pending(S_return)',
        '~$update_warning_exit_unwind(S_return)',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        '$heap_owners($heap_prune($heap_graph(S_return)), HOBJECT n_handler) = 1',
        '$task_nodes(DESTRUCTOR_RESULT pdestructorcall) = [HOBJECT n_handler]',
        '~$update_callback_destructor_exit_return(S_return[.CODE = eps])',
        '~$update_callback_destructor_exit_return(S_return[.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup 23 1) :: ptask_tail*])',
        '~$update_callback_destructor_exit_return(S_return[.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup[.RELEASED = false] 23 2) :: ptask_tail*])',
        'S_owned = S_unwind[.HELD = [HOBJECT n_handler]]',
        '$update_callback_destructor_exit_pending(S_owned)',
        '~$update_callback_destructor_exit_entered(S_owned)', '~$update_warning_exit_unwind(S_owned)',
        '$exit_start_unwind(S_owned, ' + str(status) + ').COMPLETION = UNSUPPORTED "increment/decrement warning exit continuation"',
        'PhpStep: S_unwind ~> S_resumed',
        '$call_descriptors_valid(S_resumed)', '$heap_valid($heap_graph(S_resumed))',
        'S_resumed.EVENTS = S_requested.EVENTS',
        'S_resumed_live = ' + update_protocol.transitioned('S_unwind', 'S_resumed'),
        'S_operation = $callback_destructor_exit_seek(S_resumed_live, 1, 2500)[.COMPLETION = NORMAL]',
        'S_operation.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup ' + str(status) + ' 2) :: ptask_tail*',
        '$call_descriptors_valid(S_operation)', '$heap_valid($heap_graph(S_operation))',
        '~((HOBJECT n_handler) <- S_operation.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_operation)), HOBJECT n_handler) = 0',
        '$update_warning_pointer_value(S_operation, pupdatewarning.POINTER) = (DEFINED (PINT ' + str(value) + '))',
        'S_operation.ERRORHANDLER = S_exit.ERRORHANDLER', 'S_operation.ERRORHANDLERS = S_exit.ERRORHANDLERS',
        'S_operation.EVENTS = S_requested.EVENTS',
        'PhpStep: S_operation ~> S_finish',
        'S_finish.TODO = (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup ' + str(status) + ' 2) :: ptask_tail*',
        '$call_descriptors_valid(S_finish)', '$heap_valid($heap_graph(S_finish))',
        '$task_nodes(UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup ' + str(status) + ' 2) = eps',
        'S_finish.EXITSTATUS = ' + str(status),
        'PhpStep: S_finish ~> S_capture',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
        'S_capture.ERRORHANDLER = S_finish.ERRORHANDLER', 'S_capture.ERRORHANDLERS = S_finish.ERRORHANDLERS',
        'S_capture.EVENTS = S_finish.EVENTS',
        'S_capture_live = ' + update_protocol.transitioned('S_finish', 'S_capture'),
        'S_parent = $callback_destructor_exit_seek(S_capture_live, 2, 2500)[.COMPLETION = NORMAL]',
        'S_parent.TODO = (DESTRUCTOR_ENTER pdestructorcall_parent) :: ptask_parent*',
        'n_parent = pdestructorcall_parent.OBJECT', 'n_parent =/= n_handler',
        '$heap_owners($heap_prune($heap_graph(S_exit)), HOBJECT n_parent) = 1',
        '$heap_owners($heap_prune($heap_graph(S_return)), HOBJECT n_parent) = 1',
        '$heap_owners($heap_prune($heap_graph(S_operation)), HOBJECT n_parent) = 1',
        '$heap_owners($heap_prune($heap_graph(S_parent)), HOBJECT n_parent) = 2',
        '$call_descriptors_valid(S_parent)', '$heap_valid($heap_graph(S_parent))',
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
        checks += [
            'pupdatewarning.POST', 'pupdatewarning.OP = DECREMENT',
            '$string_bytes(pupdatewarning.INPUT) = ($ptascii(""))',
            'S_capture.STORE = S_finish.STORE',
            '$update_warning_pointer_value(S_parent, pupdatewarning.POINTER) = (DEFINED (PINT 73))',
        ]
    else:
        checks += [
            '~pupdatewarning.POST', 'pupdatewarning.OP = INCREMENT', 'pupdatewarning.INPUT = PBOOL true',
            '$update_warning_pointer_value(S_capture, pupdatewarning.POINTER) = (DEFINED (PBOOL true))',
            '$update_warning_pointer_value(S_parent, pupdatewarning.POINTER) = (DEFINED (PBOOL true))',
        ]
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path)
    args, _ = parser.parse_known_args()
    out = args.output
    if out is None:
        out = Path(tempfile.mkdtemp(prefix='incdec-callback-dexit-', dir=runner.ROOT / '.tools'))
        sys.argv += ['--output', str(out)]
    watched = [Path(__file__), Path(cases.__file__), Path(callback_protocol.__file__),
               Path(callback_protocol.exit_protocol.__file__), Path(update_protocol.__file__), Path(runner.__file__)]
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
