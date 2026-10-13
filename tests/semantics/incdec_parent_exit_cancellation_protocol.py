#!/usr/bin/env python3
"""Source-reached parent cleanup, retired owners and ordered caller history."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import incdec_parent_exit_cancellation_cases as cases
import incdec_exit_protocol as exit_protocol
import incdec_warning_protocol as update_protocol
import integer_operator_warning_protocol as runner

CASES = ('parent-exit-int23-write', 'parent-exit-kept-cell-write',
         'parent-exit-function-catch')
HELPERS = exit_protocol.HELPERS + r'''
dec $parent_exit_frontier(pstate, nat) : bool
def $parent_exit_frontier(S, 0) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = UPDATE_WARNING_EXIT_HISTORY perrorcall z ptask_history*
def $parent_exit_frontier(S, 1) = true
  -- if S.TODO = (THROW_SEARCH n) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = UPDATE_WARNING_EXIT_HISTORY perrorcall z ptask_history*
def $parent_exit_frontier(S, 2) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = UPDATE_WARNING_EXIT_HISTORY perrorcall z ptask_history*
  -- if pdestructionoperation.PENDING = (n)
def $parent_exit_frontier(S, n) = false -- otherwise
dec $parent_exit_seek(pstate, nat, nat) : pstate
def $parent_exit_seek(S, n_stage, n) = S -- if $parent_exit_frontier(S, n_stage)
def $parent_exit_seek(S, n_stage, n) = S
  -- if ~$parent_exit_frontier(S, n_stage)
  -- if ~$update_exit_resumable(S) \/ n = 0
def $parent_exit_seek(S, n_stage, n) = $parent_exit_seek($drive_steps($update_exit_resume(S), 1), n_stage, $nabs($(n - 1)))
  -- if ~$parent_exit_frontier(S, n_stage)
  -- if $update_exit_resumable(S)
  -- if $(n > 0)
dec $parent_exit_statement(ptask) : bool
def $parent_exit_statement(AT porigin (STMT statement)) = true
def $parent_exit_statement(ptask) = false -- otherwise
dec $parent_exit_first_statement(ptask*) : ptask?
def $parent_exit_first_statement(eps) = eps
def $parent_exit_first_statement(ptask :: ptask_tail*) = (ptask) -- if $parent_exit_statement(ptask)
def $parent_exit_first_statement(ptask :: ptask_tail*) = $parent_exit_first_statement(ptask_tail*) -- if ~$parent_exit_statement(ptask)
dec $parent_exit_replace_statement(ptask*, ptask) : ptask*
def $parent_exit_replace_statement(eps, ptask) = eps
def $parent_exit_replace_statement(ptask :: ptask_tail*, ptask_new) = ptask_new :: ptask_tail* -- if $parent_exit_statement(ptask)
def $parent_exit_replace_statement(ptask :: ptask_tail*, ptask_new) = ptask :: $parent_exit_replace_statement(ptask_tail*, ptask_new) -- if ~$parent_exit_statement(ptask)
dec $parent_exit_swap_statements(ptask*) : ptask*
def $parent_exit_swap_statements(ptask :: ptask_tail*) = ptask_next :: $parent_exit_replace_statement(ptask_tail*, ptask)
  -- if $parent_exit_statement(ptask)
  -- if $parent_exit_first_statement(ptask_tail*) = (ptask_next)
def $parent_exit_swap_statements(ptask :: ptask_tail*) = ptask :: $parent_exit_swap_statements(ptask_tail*) -- if ~$parent_exit_statement(ptask)
def $parent_exit_swap_statements(ptask*) = ptask* -- otherwise
'''


def conditions(name, program, path, stdout):
    status = cases.EXIT_CODES.get(name, 0)
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_begin = $update_seek(S_initial, 0, 2500)[.COMPLETION = NORMAL]',
        '$update_warning_plan(S_begin) = (pupdatewarning)',
        'pupdatewarning.INPUT = PBOOL true',
        'S_boundary = $update_exit_seek(S_begin, 1, 2500)[.COMPLETION = NORMAL]',
        'S_boundary.TODO = (UPDATE_WARNING_EXIT perrorcall z) :: ptask_caller*',
        'perrorcall.RESUME = UPDATE_WARNING_RESTORE pupdatewarning',
        '$call_descriptors_valid(S_boundary)',
        'z = ' + str(status),
        'S_enter = $parent_exit_seek(S_boundary, 0, 2500)[.COMPLETION = NORMAL]',
        'S_enter.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_release*',
        'pdestructorcall.OPERATION = (pdestructionoperation)',
        'pdestructionoperation.SOURCE = UPDATE_WARNING_EXIT_HISTORY perrorcall z ptask_history*',
        'pdestructionoperation.PENDING = eps',
        '$task_nodes(pdestructionoperation.SOURCE) = eps',
        '$tasks_nodes(ptask_history*) = eps',
        '$update_exit_history(S_boundary, perrorcall.SITE) = GOTOTASKS ptask_history*',
        '$eager_operation_source_guard(S_enter, pdestructionoperation)',
        '$update_warning_exit_parent_call(pdestructorcall)',
        '$destructor_enter_valid(S_enter, pdestructorcall)',
        '$call_descriptors_valid(S_enter)', '$heap_valid($heap_graph(S_enter))',
        'n_parent = pdestructorcall.OBJECT',
        '$heap_owners($heap_prune($heap_graph(S_enter)), HOBJECT n_parent) = 2',
        'S_enter.EXITSTATUS = ' + str(status),
        'S_enter.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)',
        'S_throw = $parent_exit_seek(S_enter, 1, 2500)[.COMPLETION = NORMAL]',
        'S_throw.TODO = (THROW_SEARCH n_second) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_release*',
        '$destructor_result_valid(S_throw, pdestructorcall)',
        '$throwable_marker(DESTRUCTOR_RESULT pdestructorcall)',
        '~$exception_terminal_tail(S_throw, (DESTRUCTOR_RESULT pdestructorcall) :: ptask_release*)',
        '$eager_bailout_source(S_throw) = eps',
        '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
        'S_throw.ORIGIN = eps',
        'S_throw.EXITSTATUS = ' + str(status),
        'S_global = $global_table_view(S_throw)',
        '$lookup(S_global.ENV, $ptascii("second")) = (n_second_cell)',
        'S_throw.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        '$lookup(S_global.ENV, $ptascii("v")) = (n_value)',
        'S_throw.STORE[n_value] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
        '$throwable_previous_id(S_throw, n_second) = eps',
        'ptask_swapped* = $parent_exit_swap_statements(ptask_history*)',
        'ptask_swapped* =/= ptask_history*',
        '$tasks_nodes(ptask_swapped*) = eps',
        '~$eager_operation_source_guard(S_throw, pdestructionoperation[.SOURCE = UPDATE_WARNING_EXIT_HISTORY perrorcall z ptask_swapped*])',
        '~$eager_operation_source_guard(S_throw, pdestructionoperation[.SOURCE = UPDATE_WARNING_EXIT_HISTORY perrorcall[.MESSAGE = eps] z ptask_history*])',
        '~$eager_operation_source_guard(S_throw, pdestructionoperation[.SOURCE = UPDATE_WARNING_EXIT_HISTORY perrorcall 2147483648 ptask_history*])',
        '~$eager_operation_source_guard(S_throw[.CODE = eps], pdestructionoperation)',
        'PhpStep: S_throw ~> S_pending',
        'pdestructionoperation_pending = pdestructionoperation[.PENDING = (n_second)]',
        'S_pending.DESTRUCTION.OPERATIONS = pdestructionoperation_pending :: pdestructionoperation_tail*',
        'S_pending.TODO = $destructor_operation_tasks(ptask_release*, pdestructionoperation, pdestructionoperation_pending)',
        'S_pending.DESTRUCTION.CALLS = eps',
        'S_pending.EXITSTATUS = S_throw.EXITSTATUS',
        'S_pending.STORE = S_throw.STORE', 'S_pending.EVENTS = S_throw.EVENTS',
        '$heap_owners($heap_prune($heap_graph(S_pending)), HOBJECT n_second) = 2',
        '$call_descriptors_valid(S_pending)',
        'S_finish = $parent_exit_seek(S_pending, 2, 2500)[.COMPLETION = NORMAL]',
        'S_finish.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending) :: ptask_exit*',
        '(EXIT_UNWIND z) <- ptask_exit*',
        '$destructor_operation_valid(S_finish, pdestructionoperation_pending)',
        '$call_descriptors_valid(S_finish)', '$heap_valid($heap_graph(S_finish))',
        '$heap_owners($heap_prune($heap_graph(S_finish)), HOBJECT n_parent) = 0',
        '~((HOBJECT n_parent) <- S_finish.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_finish)), HOBJECT n_second) = 2',
        'PhpStep: S_finish ~> S_restore',
        'S_restore.TODO = (THROW_SEARCH n_second) :: ptask_history*',
        'S_restore.ORIGIN = eps', 'S_restore.RESULT = KNOWN PNULL',
        'S_restore.BASE = BASE_VALUE (KNOWN PNULL)', 'S_restore.COMPLETION = NORMAL',
        'S_restore.DESTRUCTION.OPERATIONS = eps',
        'S_restore.DESTRUCTION.CALLS = eps', 'S_restore.DESTRUCTION.RELEASES = eps',
        'S_restore.CURRENT = S_finish.CURRENT', 'S_restore.FRAMES = S_finish.FRAMES',
        'S_restore.EXITSTATUS = S_finish.EXITSTATUS',
        'S_restore.STORE = S_finish.STORE', 'S_restore.EVENTS = S_finish.EVENTS',
        'S_restore.ALLOCATIONS = S_finish.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_restore)), HOBJECT n_parent) = 0',
        '$heap_owners($heap_prune($heap_graph(S_restore)), HOBJECT n_second) = 2',
        '$throwable_previous_id(S_restore, n_second) = eps',
        '$call_descriptors_valid(S_restore)', '$heap_valid($heap_graph(S_restore))',
        '$drive_steps(S_finish, 0) = S_finish[.COMPLETION = BUDGET]',
        'S_budget = $drive_steps(S_finish, 1)', 'S_budget.COMPLETION = BUDGET',
        'S_budget = ' + update_protocol.transitioned('S_finish', 'S_restore') + '[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_restore, 2500)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = ' + str(status),
        'S_done.TODO = eps', 'S_done.FRAMES = eps',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_budget[.COMPLETION = NORMAL], 2500) = S_done',
    ]
    if name == 'parent-exit-function-catch':
        checks += [
            'S_throw.CURRENT = (pcallcontext)', 'S_throw.FRAMES = pframe :: eps',
            'pdestructionoperation.CALLER = (pcallcontext)',
            '$target_function(S_throw, $context_target(pcallcontext)) = (pfunction)',
            'pcallcontext.NAME = $ptascii("run_case")',
            '~$eager_operation_source_guard(S_throw, pdestructionoperation[.CALLER = eps])',
            'pupdatewarning.POINTER = UPDATE_CELL n_x',
            '$lookup(S_global.ENV, $ptascii("x")) = (n_x)',
            '$lookup(S_throw.ENV, $ptascii("x")) = (n_x)',
            'S_enter.STORE[n_x] = DEFINED (PBOOL true)',
            'S_restore.STORE[n_x] = DEFINED (PINT 99)',
            '$heap_owners($heap_prune($heap_graph(S_restore)), HCELL n_x) = 2',
        ]
    else:
        checks += ['S_throw.CURRENT = eps', 'S_throw.FRAMES = eps']
    if name == 'parent-exit-int23-write':
        checks += [
            'pupdatewarning.POINTER = UPDATE_CV ($ptascii("x"))',
            '$lookup(S_global.ENV, $ptascii("x")) = (n_x)',
            'S_enter.STORE[n_x] = DEFINED (PBOOL true)',
            'S_throw.STORE[n_x] = DEFINED (PINT 99)',
            'S_restore.STORE[n_x] = DEFINED (PINT 99)',
        ]
    elif name == 'parent-exit-kept-cell-write':
        checks += [
            'pupdatewarning.POINTER = UPDATE_CELL n_old',
            '$lookup(S_global.ENV, $ptascii("keep")) = (n_old)',
            '$lookup(S_global.ENV, $ptascii("x")) = (n_new)',
            '$lookup(S_global.ENV, $ptascii("peer")) = (n_new)',
            'n_old =/= n_new',
            'S_enter.STORE[n_old] = DEFINED (PBOOL true)',
            'S_throw.STORE[n_old] = DEFINED (PINT 99)',
            'S_restore.STORE[n_old] = DEFINED (PINT 99)',
            'S_enter.STORE[n_new] = DEFINED (PINT 73)',
            'S_restore.STORE[n_new] = DEFINED (PINT 73)',
            '$heap_owners($heap_prune($heap_graph(S_enter)), HCELL n_old) = 1',
            '$heap_owners($heap_prune($heap_graph(S_restore)), HCELL n_old) = 1',
        ]
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path)
    args, _ = parser.parse_known_args()
    out = args.output
    if out is None:
        out = Path(tempfile.mkdtemp(prefix='incdec-parent-exit-', dir=runner.ROOT / '.tools'))
        sys.argv += ['--output', str(out)]
    watched = [Path(__file__), Path(cases.__file__), Path(exit_protocol.__file__),
               Path(update_protocol.__file__), Path(runner.__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    runner.CASES, runner.HELPERS, runner.conditions = CASES, HELPERS, conditions
    runner.sources, runner.__file__ = cases, __file__
    passed = runner.main()
    assert before == {str(path): digest(path) for path in watched}
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
