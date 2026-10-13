#!/usr/bin/env python3
"""Reached pending ownership, retained registry and late-reference cancellation."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import incdec_callback_exit_cancellation_review_cases as cases
import incdec_exit_protocol as exit_protocol
import incdec_warning_protocol as update_protocol
import integer_operator_warning_protocol as runner

CASES = ('review-callback-cancel-retained-registry', 'review-callback-cancel-late-peer')
HELPERS = exit_protocol.HELPERS + r'''
dec $callback_cancel_review_frontier(pstate, nat) : bool
def $callback_cancel_review_frontier(S, 0) = true
  -- if S.TODO = (THROW_SEARCH n) :: (UPDATE_WARNING_EXIT perrorcall z) :: ptask_tail*
def $callback_cancel_review_frontier(S, n_phase) = true
  -- if $(n_phase > 0) /\ $(n_phase <= 2)
  -- if S.TODO = (THROW_SEARCH n) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup z n_phase) :: ptask_tail*
def $callback_cancel_review_frontier(S, n_phase) = false -- otherwise
dec $callback_cancel_review_seek(pstate, nat, nat) : pstate
def $callback_cancel_review_seek(S, n_phase, n) = S -- if $callback_cancel_review_frontier(S, n_phase)
def $callback_cancel_review_seek(S, n_phase, n) = S
  -- if ~$callback_cancel_review_frontier(S, n_phase)
  -- if ~$update_exit_resumable(S) \/ n = 0
def $callback_cancel_review_seek(S, n_phase, n) = $callback_cancel_review_seek($drive_steps($update_exit_resume(S), 1), n_phase, $nabs($(n - 1)))
  -- if ~$callback_cancel_review_frontier(S, n_phase)
  -- if $update_exit_resumable(S) /\ $(n > 0)
'''


def conditions(name, program, path, stdout):
    retained = name == CASES[0]
    prefix = 'H:2;E;L:1;' if retained else 'H:2;E;L:1:1;'
    before_commit = prefix if retained else prefix + 'D:1:1;'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_boundary = $callback_cancel_review_seek(S_initial, 0, 2500)[.COMPLETION = NORMAL]',
        'S_boundary.TODO = (THROW_SEARCH n_pending) :: (UPDATE_WARNING_EXIT perrorcall 0) :: ptask_tail*',
        'perrorcall.RESUME = UPDATE_WARNING_RESTORE pupdatewarning',
        'perrorcall.CALLBACK = POBJECT n_handler',
        'pupdatewarning.INPUT = PBOOL true', 'pupdatewarning.OP = INCREMENT', '~pupdatewarning.POST',
        'pupdatewarning.POINTER = UPDATE_CV ($ptascii("x"))',
        'pupdatewarning.PENDING = eps',
        '$update_warning_exit_owning(S_boundary, perrorcall)',
        '~$update_warning_exit_named(S_boundary, perrorcall)',
        '$call_descriptors_valid(S_boundary)', '$heap_valid($heap_graph(S_boundary))',
        '$throwable_live(S_boundary, n_pending)',
        '$throwable_previous_id(S_boundary, n_pending) = eps',
        '$task_nodes(THROW_SEARCH n_pending) = [HOBJECT n_pending]',
        '$heap_owners($heap_prune($heap_graph(S_boundary)), HOBJECT n_pending) = 2',
        '$heap_owners($heap_prune($heap_graph(S_boundary)), HOBJECT n_handler) = 2',
        '$integer_outputs(S_boundary.EVENTS) = ($ptascii(' + json.dumps(prefix) + '))',
        'S_global = $global_table_view(S_boundary)',
        '$lookup(S_global.ENV, $ptascii("second")) = (n_pending_cell)',
        'S_boundary.STORE[n_pending_cell] = DEFINED (POBJECT n_pending)',
        '$lookup(S_global.ENV, $ptascii("v")) = (n_value)',
        'S_boundary.STORE[n_value] = DEFINED (PINT 100)',
        '$lookup(S_global.ENV, $ptascii("weak")) = (n_weak_cell)',
        'S_boundary.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
        'PhpStep: S_boundary ~> S_phase0',
        'S_phase0.TODO = (THROW_SEARCH n_pending) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup 0 0) :: ptask_tail*',
        'pdestructioncleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall',
        '~pdestructioncleanup.RELEASED',
        '$call_descriptors_valid(S_phase0)', '$heap_valid($heap_graph(S_phase0))',
        'S_phase0.STORE = S_boundary.STORE', 'S_phase0.EVENTS = S_boundary.EVENTS',
        '$task_nodes(UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup 0 0) = [HOBJECT n_handler, HOBJECT n_handler]',
        'PhpStep: S_phase0 ~> S_selected_operation',
        'S_selected_operation.DESTRUCTION.OPERATIONS = pdestructionoperation_selected :: pdestructionoperation_tail*',
        'pdestructionoperation_selected.SOURCE = ERROR_HANDLER_RESULT perrorcall',
        'pdestructionoperation_selected.PENDING = (n_pending)',
        'pdestructionoperation_selected.CLEANUP = (pdestructioncleanup)',
        '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_selected) = [HOBJECT n_pending]',
        '$eager_operation_source_valid(S_selected_operation, pdestructionoperation_selected)',
        '$call_descriptors_valid(S_selected_operation)', '$heap_valid($heap_graph(S_selected_operation))',
        '$heap_owners($heap_prune($heap_graph(S_selected_operation)), HOBJECT n_pending) = 2',
        'S_selected = $callback_cancel_review_seek(S_selected_operation, 1, 2500)[.COMPLETION = NORMAL]',
        'S_selected.TODO = (THROW_SEARCH n_pending) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup 0 1) :: ptask_tail*',
        '$call_descriptors_valid(S_selected)', '$heap_valid($heap_graph(S_selected))',
        '$heap_owners($heap_prune($heap_graph(S_selected)), HOBJECT n_handler) = 1',
        '$heap_owners($heap_prune($heap_graph(S_selected)), HOBJECT n_pending) = 2',
        '$integer_outputs(S_selected.EVENTS) = ($ptascii(' + json.dumps(prefix) + '))',
        '$update_warning_pointer_value(S_selected, pupdatewarning.POINTER) = (DEFINED (PINT 41))',
        'PhpStep: S_selected ~> S_raw_operation',
        'pdestructioncleanup_done = pdestructioncleanup[.RELEASED = true]',
        'S_raw_operation.DESTRUCTION.OPERATIONS = pdestructionoperation_raw :: pdestructionoperation_tail*',
        'pdestructionoperation_raw.SOURCE = ERROR_HANDLER_CLEAN perrorcall',
        'pdestructionoperation_raw.PENDING = (n_pending)',
        'pdestructionoperation_raw.CLEANUP = (pdestructioncleanup_done)',
        '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_raw) = [HOBJECT n_pending]',
        '$eager_operation_source_valid(S_raw_operation, pdestructionoperation_raw)',
        '$call_descriptors_valid(S_raw_operation)', '$heap_valid($heap_graph(S_raw_operation))',
        '$heap_owners($heap_prune($heap_graph(S_raw_operation)), HOBJECT n_pending) = 2',
        'S_phase2 = $callback_cancel_review_seek(S_raw_operation, 2, 2500)[.COMPLETION = NORMAL]',
        'S_phase2.TODO = (THROW_SEARCH n_pending) :: (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup_done 0 2) :: ptask_tail*',
        '$call_descriptors_valid(S_phase2)', '$heap_valid($heap_graph(S_phase2))',
        '$task_nodes(UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup_done 0 2) = eps',
        '$eager_cleanup_find(S_phase2.DESTRUCTION.CLEANUPS, pdestructioncleanup.SOURCE) = eps',
        '$update_callback_exit_source_valid(S_phase2, pdestructioncleanup_done)',
        '$heap_owners($heap_prune($heap_graph(S_phase2)), HOBJECT n_pending) = 2',
        '$throwable_previous_id(S_phase2, n_pending) = eps',
        '$integer_outputs(S_phase2.EVENTS) = ($ptascii(' + json.dumps(before_commit) + '))',
        'S_phase2.STORE[n_value] = DEFINED (PINT 100)',
        'S_phase2.EXITSTATUS = 0',
        '~$call_task_valid(S_phase0, UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup 0 1)',
        '~$call_task_valid(S_phase2, UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup_done 0 3)',
        '~$call_task_valid(S_phase2, UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup_done 2147483648 2)',
        '~$update_callback_exit_valid(S_phase2, pdestructioncleanup_done[.RELEASED = false], 0, 2)',
        '~$update_callback_exit_source_valid(S_phase2[.CODE = eps], pdestructioncleanup_done)',
        '~$update_callback_exit_source_valid(S_phase2, pdestructioncleanup_done[.SOURCE = ERROR_HANDLER_RESULT perrorcall[.MESSAGE = eps]])',
        '~$update_callback_exit_source_valid(S_phase2, pdestructioncleanup_done[.SOURCE = ERROR_HANDLER_RESULT perrorcall[.RESUME = UPDATE_WARNING_RESTORE pupdatewarning[.PENDING = (n_pending)]]])',
        'PhpStep: S_phase2 ~> S_pending',
        'S_pending.TODO = (UPDATE_WARNING_DONE pupdatewarning[.PENDING = (n_pending)]) :: ptask_tail*',
        '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
        '$task_nodes(UPDATE_WARNING_DONE pupdatewarning[.PENDING = (n_pending)]) = [HOBJECT n_pending]',
        '$heap_owners($heap_prune($heap_graph(S_pending)), HOBJECT n_pending) = 2',
        '$throwable_previous_id(S_pending, n_pending) = eps',
        'S_pending.EVENTS = S_phase2.EVENTS', 'S_pending.ERRORHANDLER = S_phase2.ERRORHANDLER',
        'S_pending.ERRORHANDLERS = S_phase2.ERRORHANDLERS',
        'S_pending.STORE[n_value] = DEFINED (PINT 100)',
        '$update_warning_pointer_value(S_pending, pupdatewarning.POINTER) = (DEFINED (PBOOL true))',
        'PhpStep: S_pending ~> S_search',
        'S_search.TODO = (THROW_SEARCH n_pending) :: ptask_tail*',
        '$call_descriptors_valid(S_search)', '$heap_valid($heap_graph(S_search))',
        '$heap_owners($heap_prune($heap_graph(S_search)), HOBJECT n_pending) = 2',
        'S_search.STORE = S_pending.STORE', 'S_search.EVENTS = S_pending.EVENTS',
        'S_search.EXITSTATUS = 0',
        '$drive_steps(S_phase2, 0) = S_phase2[.COMPLETION = BUDGET]',
        'S_budget = $drive_steps(S_phase2, 1)', 'S_budget.COMPLETION = BUDGET',
        'S_budget = ' + update_protocol.transitioned('S_phase2', 'S_pending') + '[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_search, 2500)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_budget[.COMPLETION = NORMAL], 2500) = S_done',
    ]
    if retained:
        checks += [
            'S_selected.ERRORHANDLER.CALLBACK = eps',
            'S_raw_operation.ERRORHANDLER.CALLBACK = (POBJECT n_handler)',
            'S_phase2.ERRORHANDLER.CALLBACK = (POBJECT n_handler)',
            '(HOBJECT n_handler) <- S_phase2.ALLOCATIONS',
            '$heap_owners($heap_prune($heap_graph(S_phase2)), HOBJECT n_handler) = 1',
            '~(n_handler <- S_phase2.DESTRUCTION.CALLED)',
            '$weakref_get(S_phase2, n_weak) = POBJECT n_handler',
            '$update_warning_pointer_value(S_phase2, pupdatewarning.POINTER) = (DEFINED (PINT 41))',
            '~(n_handler <- S_pending.DESTRUCTION.CALLED)',
        ]
    else:
        checks += [
            'n_handler <- S_phase2.DESTRUCTION.CALLED',
            '~((HOBJECT n_handler) <- S_phase2.ALLOCATIONS)',
            '$weakref_get(S_phase2, n_weak) = PNULL',
            'S_phase2.ERRORHANDLER.CALLBACK = (pvalue_registered)',
            '$string_bytes(pvalue_registered) = ($ptascii("h3"))',
            '$lookup($global_table_view(S_phase2).ENV, $ptascii("x")) = (n_old)',
            '$lookup($global_table_view(S_phase2).ENV, $ptascii("peer")) = (n_old)',
            'n_old <- S_phase2.REFCELLS', 'S_phase2.STORE[n_old] = DEFINED (PINT 99)',
            '$heap_owners($heap_prune($heap_graph(S_phase2)), HCELL n_old) = 2',
            '$lookup($global_table_view(S_pending).ENV, $ptascii("x")) = (n_new)',
            'n_old =/= n_new', '~(n_new <- S_pending.REFCELLS)',
            '$lookup($global_table_view(S_pending).ENV, $ptascii("peer")) = (n_old)',
            'S_pending.STORE[n_old] = DEFINED (PINT 99)',
            'S_pending.STORE[n_new] = DEFINED (PBOOL true)',
            '$heap_owners($heap_prune($heap_graph(S_pending)), HCELL n_old) = 1',
            '$heap_owners($heap_prune($heap_graph(S_pending)), HCELL n_new) = 1',
            'S_done.STORE[n_old] = DEFINED (PINT 99)',
        ]
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path)
    args, _ = parser.parse_known_args()
    out = args.output
    if out is None:
        out = Path(tempfile.mkdtemp(prefix='incdec-callback-cancel-review-', dir=runner.ROOT / '.tools'))
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
