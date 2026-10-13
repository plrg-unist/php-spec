#!/usr/bin/env python3
"""Source-reached warning exit, cleanup and borrowed-target checks."""
import base64
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import incdec_exit_cases as cases
import incdec_warning_protocol as update_runner
import integer_operator_warning_protocol as runner

CASES = ('handler-exit-bool', 'handler-exit-bool-local-destructor',
         'handler-exit-bool-kept-cell-rebind')
HELPERS = update_runner.HELPERS + r'''
dec $update_exit_frontier(pstate, nat) : bool
def $update_exit_frontier(S, 0) = true
  -- if S.TODO = (EXIT_INVOKE pexitcall) :: ptask_tail*
  -- if $update_warning_exit_pending(S)
def $update_exit_frontier(S, 1) = true
  -- if S.TODO = (UPDATE_WARNING_EXIT perrorcall z) :: ptask_tail*
def $update_exit_frontier(S, 2) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if $update_warning_exit_pending(S)
def $update_exit_frontier(S, n) = false -- otherwise
dec $update_exit_resumable(pstate) : bool
def $update_exit_resumable(S) = (S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET \/ $exit_completion(S.COMPLETION))
dec $update_exit_resume(pstate) : pstate
def $update_exit_resume(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $update_exit_resume(S) = S -- otherwise
dec $update_exit_seek(pstate, nat, nat) : pstate
def $update_exit_seek(S, n_stage, n) = S -- if $update_exit_frontier(S, n_stage)
def $update_exit_seek(S, n_stage, n) = S
  -- if ~$update_exit_frontier(S, n_stage)
  -- if ~$update_exit_resumable(S) \/ n = 0
def $update_exit_seek(S, n_stage, n) = $update_exit_seek($drive_steps($update_exit_resume(S), 1), n_stage, $nabs($(n - 1)))
  -- if ~$update_exit_frontier(S, n_stage)
  -- if $update_exit_resumable(S)
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_begin = $update_seek(S_initial, 0, 2500)[.COMPLETION = NORMAL]',
        '$update_warning_plan(S_begin) = (pupdatewarning)',
        'pupdatewarning.INPUT = PBOOL true', 'pupdatewarning.PENDING = eps',
        'S_invoke = $update_exit_seek(S_begin, 0, 2500)[.COMPLETION = NORMAL]',
        '$update_exit_frontier(S_invoke, 0)', '$call_descriptors_valid(S_invoke)',
        'S_invoke.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_handler*',
        'perrorcall.RESUME = UPDATE_WARNING_RESTORE pupdatewarning',
        'S_invoke.ERRORHANDLER.CALLBACK = eps',
        'PhpStep: S_invoke ~> S_requested', 'S_requested.COMPLETION = EXITED 0',
        '$update_warning_exit_unwind(S_requested)',
        '~$update_warning_exit_unwind(S_requested[.FRAMES = eps])',
        '~$update_warning_exit_unwind(S_requested[.CODE = eps])',
        'S_requested.EXITSTATUS = 0', 'S_requested.STORE = S_invoke.STORE',
    ]
    if name == 'handler-exit-bool-local-destructor':
        checks += [
            'S_cleanup = $update_exit_seek(S_requested, 2, 2500)[.COMPLETION = NORMAL]',
            'S_cleanup.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_cleanup*',
            'S_cleanup.FRAMES = eps', '$call_descriptors_valid(S_cleanup)',
            'S_cleanup.ERRORHANDLER.CALLBACK = eps',
            '$lookup(S_cleanup.ENV, $ptascii("x")) = (n_before)',
            'S_cleanup.STORE[n_before] = DEFINED (PINT 41)',
            'pdestructorcall.OBJECT <- S_cleanup.DESTRUCTION.CALLED',
            '$integer_outputs(S_cleanup.EVENTS) = ($ptascii("H:2;E;"))',
        ]
    checks += [
        'S_boundary = $update_exit_seek(S_requested, 1, 2500)[.COMPLETION = NORMAL]',
        'S_boundary.TODO = (UPDATE_WARNING_EXIT perrorcall 0) :: ptask_tail*',
        '$call_descriptors_valid(S_boundary)',
        '$call_task_valid(S_boundary, UPDATE_WARNING_EXIT perrorcall 0)',
        '$task_nodes(UPDATE_WARNING_EXIT perrorcall 0) = eps',
        '$update_warning_exit_named(S_boundary, perrorcall)',
        '~$update_warning_exit_named(S_boundary, perrorcall[.TARGET = eps])',
        '~$update_warning_exit_named(S_boundary, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '~$update_warning_exit_named(S_boundary, perrorcall[.MESSAGE = eps])',
        '~$update_warning_exit_named(S_boundary, perrorcall[.RESUME = UPDATE_WARNING_NOTICE pupdatewarning])',
        '~$update_warning_exit_named(S_boundary, perrorcall[.CALLBACK = PSTRING ($ptascii("missing"))])',
        '~$call_task_valid(S_boundary[.ORIGIN = eps], UPDATE_WARNING_EXIT perrorcall 0)',
        '~$call_task_valid(S_boundary[.CODE = eps], UPDATE_WARNING_EXIT perrorcall 0)',
        '~$call_task_valid(S_boundary, UPDATE_WARNING_EXIT perrorcall 2147483648)',
        'S_boundary.ERRORHANDLER.CALLBACK = eps',
        '$update_warning_pointer_value(S_boundary, pupdatewarning.POINTER) = (DEFINED (PINT 41))',
        '$lookup(S_boundary.ENV, $ptascii("v")) = (n_value)',
        'S_boundary.STORE[n_value] = DEFINED (PINT 100)',
        'PhpStep: S_boundary ~> S_continue',
        'S_continue.TODO = [EXIT_UNWIND 0]', 'S_continue.ORIGIN = eps',
        'S_continue.COMPLETION = NORMAL', 'S_continue.EXITSTATUS = 0',
        'S_continue.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)',
        '$call_descriptors_valid(S_continue)',
        '$update_warning_pointer_value(S_continue, pupdatewarning.POINTER) = (DEFINED (PBOOL true))',
        'S_continue.STORE[n_value] = DEFINED (PINT 100)',
        '$drive_steps(S_boundary, 0) = S_boundary[.COMPLETION = BUDGET]',
        'S_budget = $drive_steps(S_boundary, 1)', 'S_budget.COMPLETION = BUDGET',
        'S_budget = ' + update_runner.transitioned('S_boundary', 'S_continue') + '[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_budget[.COMPLETION = NORMAL], 2500)',
        'S_done.COMPLETION = EXITED 0', 'S_done.EXITSTATUS = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        'S_done.FRAMES = eps', 'S_done.TODO = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_boundary, 2500) = S_done',
    ]
    if name == 'handler-exit-bool-local-destructor':
        checks += [
            'pdestructorcall.OBJECT <- S_boundary.DESTRUCTION.CALLED',
            '$integer_outputs(S_boundary.EVENTS) = ($ptascii("H:2;E;L:1:;"))',
            '$heap_owners($heap_prune($heap_graph(S_boundary)), HOBJECT pdestructorcall.OBJECT) = 0',
        ]
    if name == 'handler-exit-bool-kept-cell-rebind':
        checks += [
            'pupdatewarning.POINTER = UPDATE_CELL n_old',
            '$lookup(S_boundary.ENV, $ptascii("keep")) = (n_old)',
            '$lookup(S_boundary.ENV, $ptascii("x")) = (n_new)', 'n_old =/= n_new',
            '$lookup(S_boundary.ENV, $ptascii("peer")) = (n_new)',
            'S_boundary.STORE[n_new] = DEFINED (PINT 73)',
            '$heap_owners($heap_prune($heap_graph(S_boundary)), HCELL n_old) = 1',
            '$heap_owners($heap_prune($heap_graph(S_boundary)), HCELL n_new) = 2',
            'S_continue.STORE[n_old] = DEFINED (PBOOL true)',
            'S_continue.STORE[n_new] = DEFINED (PINT 73)',
            '$heap_owners($heap_prune($heap_graph(S_continue)), HCELL n_old) = 1',
        ]
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path)
    args, _ = parser.parse_known_args()
    out = args.output
    if out is None:
        out = Path(tempfile.mkdtemp(prefix='incdec-exit-protocol-', dir=runner.ROOT / '.tools'))
        sys.argv += ['--output', str(out)]
    watched = [Path(__file__), Path(cases.__file__), Path(update_runner.__file__), Path(runner.__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    runner.CASES, runner.HELPERS, runner.conditions = CASES, HELPERS, conditions
    runner.sources = cases
    runner.__file__ = __file__
    passed = runner.main()
    assert before == {str(path): digest(path) for path in watched}
    report = json.loads((out / 'report.json').read_bytes())
    report['helper_inputs'] = before
    for row in report['rows']:
        assert row['native']['interruption'] is None and row['native']['group_after'] == []
        if 'model' in row:
            result = row['model']
            row['passed'] = (row['passed'] and result['interruption'] is None and result['group_after'] == []
                and (out / (row['id'] + '-model.stdout')).read_bytes() == b'true\n')
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed and all(row.get('passed', True) for row in report['rows'])


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
