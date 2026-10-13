#!/usr/bin/env python3
"""Reached local Throwable transfer through selected and raw callback release."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import incdec_callback_exit_cancellation_cases as cases
import incdec_callback_exit_protocol as callback_protocol
import incdec_warning_protocol as update_protocol
import integer_operator_warning_protocol as runner

CASES = ('callback-cancel-bool-int23', 'callback-cancel-empty-postdec',
         'callback-cancel-null-both-throw-rebind')
HELPERS = callback_protocol.HELPERS + r'''
dec $callback_cancel_frontier(pstate, nat) : bool
def $callback_cancel_frontier(S, 0) = true
  -- if S.TODO = (THROW_SEARCH n) :: (UPDATE_WARNING_EXIT perrorcall z) :: ptask_tail*
def $callback_cancel_frontier(S, 1) = true
  -- if S.TODO = (THROW_SEARCH n) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup z 1) :: ptask_tail*
def $callback_cancel_frontier(S, 2) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = ERROR_HANDLER_RESULT perrorcall
  -- if perrorcall.RESUME = UPDATE_WARNING_RESTORE pupdatewarning
  -- if pdestructionoperation.PENDING = (n)
def $callback_cancel_frontier(S, n_phase) = false -- otherwise
dec $callback_cancel_seek(pstate, nat, nat) : pstate
def $callback_cancel_seek(S, n_stage, n) = S -- if $callback_cancel_frontier(S, n_stage)
def $callback_cancel_seek(S, n_stage, n) = S
  -- if ~$callback_cancel_frontier(S, n_stage)
  -- if ~$update_exit_resumable(S) \/ n = 0
def $callback_cancel_seek(S, n_stage, n) = $callback_cancel_seek($drive_steps($update_exit_resume(S), 1), n_stage, $nabs($(n - 1)))
  -- if ~$callback_cancel_frontier(S, n_stage)
  -- if $update_exit_resumable(S) /\ $(n > 0)
'''


def conditions(name, program, path, stdout):
    secondary = name == CASES[2]
    empty = name == CASES[1]
    status = cases.EXIT_CODES.get(name, 0)
    prefix = 'H:2;L:1;' if name == CASES[0] else ('H:8192;E;L:1;' if empty else 'H:2;E;L:1:1;')
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_boundary = $callback_cancel_seek(S_initial, 0, 2500)[.COMPLETION = NORMAL]',
        'S_boundary.TODO = (THROW_SEARCH n_first) :: (UPDATE_WARNING_EXIT perrorcall z) :: ptask_tail*',
        'z = ' + str(status), 'S_boundary.EXITSTATUS = ' + str(status),
        'S_boundary.RESULT = KNOWN PNULL', 'S_boundary.BASE = BASE_VALUE (KNOWN PNULL)',
        'perrorcall.RESUME = UPDATE_WARNING_RESTORE pupdatewarning',
        'perrorcall.CALLBACK = POBJECT n_handler', 'pupdatewarning.PENDING = eps',
        '$update_warning_exit_owning(S_boundary, perrorcall)',
        '$call_descriptors_valid(S_boundary)', '$heap_valid($heap_graph(S_boundary))',
        '$throwable_live(S_boundary, n_first)', '~$throwable_live(S_boundary, n_handler)',
        '$task_nodes(THROW_SEARCH n_first) = [HOBJECT n_first]',
        '$heap_owners($heap_prune($heap_graph(S_boundary)), HOBJECT n_first) = 2',
        '$heap_owners($heap_prune($heap_graph(S_boundary)), HOBJECT n_handler) = 2',
        '$throwable_previous_id(S_boundary, n_first) = eps',
        '$integer_outputs(S_boundary.EVENTS) = ($ptascii(' + json.dumps(prefix) + '))',
        '$update_warning_pointer_value(S_boundary, pupdatewarning.POINTER) = (DEFINED (PINT 41))',
        '$lookup($global_table_view(S_boundary).ENV, $ptascii("first")) = (n_first_cell)',
        'S_boundary.STORE[n_first_cell] = DEFINED (POBJECT n_first)',
        '$lookup($global_table_view(S_boundary).ENV, $ptascii("v")) = (n_value)',
        'S_boundary.STORE[n_value] = DEFINED (PINT 100)',
        'PhpStep: S_boundary ~> S_capture',
        'S_capture.TODO = (THROW_SEARCH n_first) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup z 0) :: ptask_tail*',
        'pdestructioncleanup = $eager_cleanup_record(S_boundary, ERROR_HANDLER_RESULT perrorcall)',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
        '$task_nodes(UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup z 0) = [HOBJECT n_handler, HOBJECT n_handler]',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HOBJECT n_first) = 2',
        'S_capture.STORE = S_boundary.STORE', 'S_capture.EVENTS = S_boundary.EVENTS',
        'S_capture.ALLOCATIONS = S_boundary.ALLOCATIONS',
        '~$call_task_valid(S_capture, UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup z 1)',
        '~$call_task_valid(S_capture, UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup 2147483648 0)',
        '~$update_callback_exit_source_valid(S_capture[.CODE = eps], pdestructioncleanup)',
        '~$update_callback_exit_source_valid(S_capture, pdestructioncleanup[.SOURCE = ERROR_HANDLER_RESULT perrorcall[.MESSAGE = eps]])',
        '~$update_callback_exit_source_valid(S_capture, pdestructioncleanup[.SOURCE = ERROR_HANDLER_RESULT perrorcall[.RESUME = UPDATE_WARNING_RESTORE pupdatewarning[.PENDING = (n_first)]]])',
        'PhpStep: S_capture ~> S_selected_begin',
        'S_selected_begin.DESTRUCTION.OPERATIONS = pdestructionoperation_selected :: pdestructionoperation_tail*',
        'pdestructionoperation_selected.SOURCE = ERROR_HANDLER_RESULT perrorcall',
        'pdestructionoperation_selected.PENDING = (n_first)',
        '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_selected) = [HOBJECT n_first]',
        '$eager_operation_source_valid(S_selected_begin, pdestructionoperation_selected)',
        '$call_descriptors_valid(S_selected_begin)', '$heap_valid($heap_graph(S_selected_begin))',
        '$heap_owners($heap_prune($heap_graph(S_selected_begin)), HOBJECT n_first) = 2',
        'S_selected_operation = $callback_cancel_seek(S_selected_begin, 2, 2500)[.COMPLETION = NORMAL]',
        'S_selected_operation.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_selected) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup z 1) :: ptask_tail*',
        '$call_descriptors_valid(S_selected_operation)', '$heap_valid($heap_graph(S_selected_operation))',
        '$heap_owners($heap_prune($heap_graph(S_selected_operation)), HOBJECT n_handler) = 1',
        '$heap_owners($heap_prune($heap_graph(S_selected_operation)), HOBJECT n_first) = 2',
        'S_selected_operation.EVENTS = S_capture.EVENTS',
        'PhpStep: S_selected_operation ~> S_selected',
        'S_selected.TODO = (THROW_SEARCH n_first) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup z 1) :: ptask_tail*',
        '$call_descriptors_valid(S_selected)', '$heap_valid($heap_graph(S_selected))',
        '$heap_owners($heap_prune($heap_graph(S_selected)), HOBJECT n_first) = 2',
        'PhpStep: S_selected ~> S_raw',
        'pdestructioncleanup_done = pdestructioncleanup[.RELEASED = true]',
        'S_raw.DESTRUCTION.OPERATIONS = pdestructionoperation_raw :: pdestructionoperation_tail*',
        'pdestructionoperation_raw.SOURCE = ERROR_HANDLER_CLEAN perrorcall',
        'pdestructionoperation_raw.PENDING = (n_first)',
        'pdestructionoperation_raw.CLEANUP = (pdestructioncleanup_done)',
        '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_raw) = [HOBJECT n_first]',
        '$eager_operation_source_valid(S_raw, pdestructionoperation_raw)',
        '$call_descriptors_valid(S_raw)', '$heap_valid($heap_graph(S_raw))',
        '$heap_owners($heap_prune($heap_graph(S_raw)), HOBJECT n_first) = 2',
        'S_operation = $callback_exit_seek(S_raw, 4, 2500)[.COMPLETION = NORMAL]',
        'S_operation.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup_done z 2) :: ptask_tail*',
        'pdestructionoperation_pending.SOURCE = ERROR_HANDLER_CLEAN perrorcall',
        'pdestructionoperation_pending.PENDING = (n_pending)',
        '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending) = [HOBJECT n_pending]',
        '$call_descriptors_valid(S_operation)', '$heap_valid($heap_graph(S_operation))',
        '$heap_owners($heap_prune($heap_graph(S_operation)), HOBJECT n_pending) = 2',
        '~((HOBJECT n_handler) <- S_operation.ALLOCATIONS)',
        'PhpStep: S_operation ~> S_finish',
        'S_finish.TODO = (THROW_SEARCH n_pending) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup_done z 2) :: ptask_tail*',
        '$update_callback_exit_valid(S_finish, pdestructioncleanup_done, z, 2)',
        '$call_descriptors_valid(S_finish)', '$heap_valid($heap_graph(S_finish))',
        '$task_nodes(UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup_done z 2) = eps',
        '$heap_owners($heap_graph(S_finish), HOBJECT n_handler) = 0',
        '$heap_owners($heap_prune($heap_graph(S_finish)), HOBJECT n_pending) = 2',
        'S_finish.STORE[n_value] = DEFINED (PINT 100)',
        'S_finish.EXITSTATUS = ' + str(status),
        'PhpStep: S_finish ~> S_pending',
        'S_pending.TODO = (UPDATE_WARNING_DONE pupdatewarning[.PENDING = (n_pending)]) :: ptask_tail*',
        '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
        '$heap_owners($heap_prune($heap_graph(S_pending)), HOBJECT n_pending) = 2',
        'S_pending.ERRORHANDLER = S_finish.ERRORHANDLER',
        'S_pending.ERRORHANDLERS = S_finish.ERRORHANDLERS',
        'S_pending.EVENTS = S_finish.EVENTS',
        'PhpStep: S_pending ~> S_search',
        'S_search.TODO = (THROW_SEARCH n_pending) :: ptask_tail*',
        '$call_descriptors_valid(S_search)', '$heap_valid($heap_graph(S_search))',
        '$heap_owners($heap_prune($heap_graph(S_search)), HOBJECT n_pending) = 2',
        '$drive_steps(S_finish, 0) = S_finish[.COMPLETION = BUDGET]',
        'S_budget = $drive_steps(S_finish, 1)', 'S_budget.COMPLETION = BUDGET',
        'S_budget = ' + update_protocol.transitioned('S_finish', 'S_pending') + '[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_budget[.COMPLETION = NORMAL], 2500)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = ' + str(status),
        'S_done.TODO = eps', 'S_done.FRAMES = eps',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    if secondary:
        checks += [
            'pupdatewarning.INPUT = PNULL', 'pupdatewarning.OP = DECREMENT', '~pupdatewarning.POST',
            '$lookup($global_table_view(S_finish).ENV, $ptascii("second")) = (n_second_cell)',
            'S_finish.STORE[n_second_cell] = DEFINED (POBJECT n_pending)',
            'n_pending =/= n_first',
            '$throwable_previous_id(S_finish, n_pending) = (n_first)',
            '$heap_owners($heap_prune($heap_graph(S_operation)), HOBJECT n_first) = 2',
            '$heap_owners($heap_prune($heap_graph(S_search)), HOBJECT n_first) = 2',
            'pupdatewarning.POINTER = UPDATE_CELL n_old',
            '$lookup($global_table_view(S_finish).ENV, $ptascii("keep")) = (n_old)',
            '$lookup($global_table_view(S_finish).ENV, $ptascii("x")) = (n_peer)',
            '$lookup($global_table_view(S_finish).ENV, $ptascii("peer")) = (n_peer)',
            'n_old =/= n_peer',
            '$heap_owners($heap_prune($heap_graph(S_finish)), HCELL n_old) = 1',
            '$heap_owners($heap_prune($heap_graph(S_pending)), HCELL n_old) = 1',
            '$heap_owners($heap_prune($heap_graph(S_pending)), HCELL n_peer) = 2',
            'S_pending.STORE[n_peer] = DEFINED (PINT 73)',
            '$update_warning_pointer_value(S_finish, pupdatewarning.POINTER) = (DEFINED (PINT 99))',
            '$update_warning_pointer_value(S_pending, pupdatewarning.POINTER) = (DEFINED PNULL)',
        ]
    else:
        checks += ['n_pending = n_first', '$throwable_previous_id(S_search, n_pending) = eps']
        if empty:
            checks += [
                'pupdatewarning.POST', '~$update_warning_restores_throw(pupdatewarning.INPUT)',
                '$string_bytes(pupdatewarning.INPUT) = ($ptascii(""))',
                '$update_warning_pointer_value(S_finish, pupdatewarning.POINTER) = (DEFINED (PINT 73))',
                'S_pending.STORE = S_finish.STORE',
            ]
        else:
            checks += [
                'pupdatewarning.INPUT = PBOOL true',
                '$update_warning_pointer_value(S_finish, pupdatewarning.POINTER) = (DEFINED (PINT 99))',
                '$update_warning_pointer_value(S_pending, pupdatewarning.POINTER) = (DEFINED (PBOOL true))',
            ]
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path)
    args, _ = parser.parse_known_args()
    out = args.output
    if out is None:
        out = Path(tempfile.mkdtemp(prefix='incdec-callback-cancel-', dir=runner.ROOT / '.tools'))
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
