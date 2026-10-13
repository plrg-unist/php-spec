#!/usr/bin/env python3
"""Source-reached callback release, captured restore and pending-owner checks."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import incdec_callback_exit_cases as cases
import incdec_exit_protocol as exit_protocol
import incdec_warning_protocol as update_protocol
import integer_operator_warning_protocol as runner

CASES = ('callback-exit-bool-owner-write', 'callback-exit-empty-owner-write',
         'callback-exit-int23-owner-throw')
HELPERS = exit_protocol.HELPERS + r'''
dec $callback_exit_frontier(pstate, nat) : bool
def $callback_exit_frontier(S, n_phase) = true
  -- if $(n_phase <= 2)
  -- if S.TODO = (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup z n_phase) :: ptask_tail*
def $callback_exit_frontier(S, 3) = true
  -- if S.TODO = (THROW_SEARCH n) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup z 2) :: ptask_tail*
def $callback_exit_frontier(S, 4) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = ERROR_HANDLER_CLEAN perrorcall
  -- if perrorcall.RESUME = UPDATE_WARNING_RESTORE pupdatewarning
  -- if pdestructionoperation.PENDING = (n)
def $callback_exit_frontier(S, n) = false -- otherwise
dec $callback_exit_seek(pstate, nat, nat) : pstate
def $callback_exit_seek(S, n_stage, n) = S -- if $callback_exit_frontier(S, n_stage)
def $callback_exit_seek(S, n_stage, n) = S
  -- if ~$callback_exit_frontier(S, n_stage)
  -- if ~$update_exit_resumable(S) \/ n = 0
def $callback_exit_seek(S, n_stage, n) = $callback_exit_seek($drive_steps($update_exit_resume(S), 1), n_stage, $nabs($(n - 1)))
  -- if ~$callback_exit_frontier(S, n_stage)
  -- if $update_exit_resumable(S) /\ $(n > 0)
'''


def conditions(name, program, path, stdout):
    pending = name == 'callback-exit-int23-owner-throw'
    status = cases.EXIT_CODES.get(name, 0)
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_exit = $update_exit_seek(S_initial, 1, 2500)[.COMPLETION = NORMAL]',
        'S_exit.TODO = (UPDATE_WARNING_EXIT perrorcall z) :: ptask_tail*',
        'z = ' + str(status), 'S_exit.EXITSTATUS = ' + str(status),
        'perrorcall.CALLBACK = POBJECT n_handler',
        'perrorcall.RESUME = UPDATE_WARNING_RESTORE pupdatewarning',
        '$update_warning_exit_owning(S_exit, perrorcall)',
        '~$update_warning_exit_named(S_exit, perrorcall)',
        '$call_descriptors_valid(S_exit)', '$heap_valid($heap_graph(S_exit))',
        '$task_nodes(UPDATE_WARNING_EXIT perrorcall z) = [HOBJECT n_handler, HOBJECT n_handler]',
        '$heap_owners($heap_prune($heap_graph(S_exit)), HOBJECT n_handler) = 2',
        '$update_warning_pointer_value(S_exit, pupdatewarning.POINTER) = (DEFINED (PINT 41))',
        'S_global = $global_table_view(S_exit)',
        '$lookup(S_global.ENV, $ptascii("v")) = (n_value)',
        'S_exit.STORE[n_value] = DEFINED (PINT 100)',
        'PhpStep: S_exit ~> S_capture',
        'S_capture.TODO = (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup z 0) :: ptask_tail*',
        'pdestructioncleanup = $eager_cleanup_record(S_exit, ERROR_HANDLER_RESULT perrorcall)',
        '~pdestructioncleanup.RELEASED',
        '$eager_cleanup_find(S_capture.DESTRUCTION.CLEANUPS, pdestructioncleanup.SOURCE) = eps',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
        'S_capture.STORE = S_exit.STORE', 'S_capture.ALLOCATIONS = S_exit.ALLOCATIONS',
        'S_capture.ERRORHANDLER = S_exit.ERRORHANDLER', 'S_capture.EVENTS = S_exit.EVENTS',
        '$task_nodes(UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup z 0) = [HOBJECT n_handler, HOBJECT n_handler]',
        '~$call_task_valid(S_capture, UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup z 1)',
        '~$call_task_valid(S_capture, UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup z 3)',
        '~$call_task_valid(S_capture, UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup 2147483648 0)',
        '~$call_task_valid(S_capture[.CODE = eps], UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup z 0)',
        '~$call_task_valid(S_capture[.ORIGIN = eps], UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup z 0)',
        '~$update_callback_exit_source_valid(S_capture, pdestructioncleanup[.SOURCE = ERROR_HANDLER_RESULT perrorcall[.MESSAGE = eps]])',
        '~$update_callback_exit_source_valid(S_capture, pdestructioncleanup[.SOURCE = ERROR_HANDLER_RESULT perrorcall[.LINE = $(perrorcall.LINE + 1)]])',
        '~$update_callback_exit_source_valid(S_capture, pdestructioncleanup[.SOURCE = ERROR_HANDLER_RESULT perrorcall[.TARGET = eps]])',
        'S_selected = $callback_exit_seek(S_capture, 1, 2500)[.COMPLETION = NORMAL]',
        'S_selected.TODO = (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup z 1) :: ptask_tail*',
        'S_selected.DESTRUCTION.CLEANUPS = pdestructioncleanup :: pdestructioncleanup_tail*',
        '$task_nodes(UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup z 1) = [HOBJECT n_handler]',
        '$heap_owners($heap_prune($heap_graph(S_selected)), HOBJECT n_handler) = 1',
        '$call_descriptors_valid(S_selected)', '$heap_valid($heap_graph(S_selected))',
        'S_selected.EVENTS = S_capture.EVENTS',
        '$update_warning_pointer_value(S_selected, pupdatewarning.POINTER) = (DEFINED (PINT 41))',
        'PhpStep: S_selected ~> S_raw',
        'pdestructioncleanup_done = pdestructioncleanup[.RELEASED = true]',
        'S_raw.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup_done z 2) :: ptask_tail*',
        'pdestructionoperation.SOURCE = ERROR_HANDLER_CLEAN perrorcall',
        'pdestructionoperation.CLEANUP = (pdestructioncleanup_done)',
        'pdestructionoperation.PENDING = eps',
        'S_raw.ERRORHANDLER = S_selected.ERRORHANDLER',
        '$call_descriptors_valid(S_raw)', '$heap_valid($heap_graph(S_raw))',
    ]
    if pending:
        checks += [
            'S_operation = $callback_exit_seek(S_raw, 4, 2500)[.COMPLETION = NORMAL]',
            'S_operation.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup_done z 2) :: ptask_tail*',
            'pdestructionoperation_pending.SOURCE = ERROR_HANDLER_CLEAN perrorcall',
            'pdestructionoperation_pending.PENDING = (n_second)',
            '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending) = [HOBJECT n_second]',
            '$heap_owners($heap_prune($heap_graph(S_operation)), HOBJECT n_second) = 2',
            '~((HOBJECT n_handler) <- S_operation.ALLOCATIONS)',
            '$call_descriptors_valid(S_operation)', '$heap_valid($heap_graph(S_operation))',
            'PhpStep: S_operation ~> S_finish',
            'S_finish.EVENTS = S_operation.EVENTS',
            'S_finish.EXITSTATUS = S_operation.EXITSTATUS',
        ]
    else:
        checks += ['S_finish = $callback_exit_seek(S_raw, 2, 2500)[.COMPLETION = NORMAL]']
    checks += [
        '$update_callback_exit_valid(S_finish, pdestructioncleanup_done, z, 2)',
        '$eager_cleanup_find(S_finish.DESTRUCTION.CLEANUPS, pdestructioncleanup.SOURCE) = eps',
        '$update_callback_exit_source_valid(S_finish, pdestructioncleanup_done)',
        '$call_descriptors_valid(S_finish)', '$heap_valid($heap_graph(S_finish))',
        '$task_nodes(UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup_done z 2) = eps',
        '~((HOBJECT n_handler) <- S_finish.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_finish), HOBJECT n_handler) = 0',
        'n_handler <- S_finish.DESTRUCTION.CALLED',
        'S_finish.STORE[n_value] = DEFINED (PINT 100)',
        '~$call_task_valid(S_finish, UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup_done z 0)',
        'PhpStep: S_finish ~> S_continue',
        'S_continue.ERRORHANDLER = S_finish.ERRORHANDLER',
        'S_continue.STORE[n_value] = DEFINED (PINT 100)',
        'S_continue.EXITSTATUS = ' + str(status),
        '$call_descriptors_valid(S_continue)',
        '$drive_steps(S_finish, 0) = S_finish[.COMPLETION = BUDGET]',
        'S_budget = $drive_steps(S_finish, 1)', 'S_budget.COMPLETION = BUDGET',
        'S_budget = ' + update_protocol.transitioned('S_finish', 'S_continue') + '[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_budget[.COMPLETION = NORMAL], 2500)',
        'S_done.EXITSTATUS = ' + str(status), 'S_done.TODO = eps', 'S_done.FRAMES = eps',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    if pending:
        checks += [
            'S_finish.TODO = (THROW_SEARCH n_second) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup_done z 2) :: ptask_tail*',
            '$lookup($global_table_view(S_finish).ENV, $ptascii("second")) = (n_second_cell)',
            'S_finish.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            '$throwable_previous_id(S_finish, n_second) = eps',
            '$heap_owners($heap_prune($heap_graph(S_finish)), HOBJECT n_second) = 2',
            'S_continue.TODO = (UPDATE_WARNING_DONE pupdatewarning[.PENDING = (n_second)]) :: ptask_tail*',
            '$heap_owners($heap_prune($heap_graph(S_continue)), HOBJECT n_second) = 2',
            'S_continue.RESULT = KNOWN PNULL', 'S_continue.BASE = BASE_VALUE (KNOWN PNULL)',
            '$update_warning_pointer_value(S_finish, pupdatewarning.POINTER) = (DEFINED (PINT 99))',
            '$update_warning_pointer_value(S_continue, pupdatewarning.POINTER) = (DEFINED (PBOOL true))',
            'PhpStep: S_continue ~> S_search',
            'S_search.TODO = (THROW_SEARCH n_second) :: ptask_tail*',
            '$heap_owners($heap_prune($heap_graph(S_search)), HOBJECT n_second) = 2',
            '$throwable_previous_id(S_search, n_second) = eps',
            'S_done.COMPLETION = NORMAL',
        ]
    else:
        checks += [
            'S_finish.TODO = (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup_done z 2) :: ptask_tail*',
            '$update_exit_control_call(S_finish) = ((perrorcall, z, ptask_tail*))',
            '$update_exit_order_supported(S_finish)',
            'S_continue.TODO = [EXIT_UNWIND 0]', 'S_continue.ORIGIN = eps',
            'S_done.COMPLETION = EXITED 0',
        ]
        if name == 'callback-exit-empty-owner-write':
            checks += [
                'pupdatewarning.POST', '$string_bytes(pupdatewarning.INPUT) = ($ptascii(""))',
                '~$update_warning_restores_throw(pupdatewarning.INPUT)',
                '$update_warning_pointer_value(S_finish, pupdatewarning.POINTER) = (DEFINED (PINT 73))',
                'S_continue.STORE = S_finish.STORE',
            ]
        else:
            checks += [
                'pupdatewarning.INPUT = PBOOL true',
                '$update_warning_pointer_value(S_finish, pupdatewarning.POINTER) = (DEFINED (PINT 99))',
                '$update_warning_pointer_value(S_continue, pupdatewarning.POINTER) = (DEFINED (PBOOL true))',
            ]
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path)
    args, _ = parser.parse_known_args()
    out = args.output
    if out is None:
        out = Path(tempfile.mkdtemp(prefix='incdec-callback-exit-', dir=runner.ROOT / '.tools'))
        sys.argv += ['--output', str(out)]
    watched = [Path(__file__), Path(cases.__file__), Path(exit_protocol.__file__),
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
