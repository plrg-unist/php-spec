#!/usr/bin/env python3
"""Reached callback retirement, registry and borrowed-target counterexamples."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import incdec_callback_exit_review_cases as cases
import incdec_exit_protocol as protocol
import incdec_warning_protocol as update_protocol

CASES = ('review-callback-exit-retained-registry',
         'review-callback-exit-null-borrowed-rebind',
         'review-callback-exit-owner-clears-registry')
HELPERS = protocol.HELPERS + r'''
dec $callback_review_frontier(pstate, nat) : bool
def $callback_review_frontier(S, n_phase) = true
  -- if S.TODO = (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup z n_phase) :: ptask_tail*
def $callback_review_frontier(S, n_phase) = false -- otherwise
dec $callback_review_seek(pstate, nat, nat) : pstate
def $callback_review_seek(S, n_phase, n) = S -- if $callback_review_frontier(S, n_phase)
def $callback_review_seek(S, n_phase, n) = S
  -- if ~$callback_review_frontier(S, n_phase)
  -- if ~$update_exit_resumable(S) \/ n = 0
def $callback_review_seek(S, n_phase, n) = $callback_review_seek($drive_steps($update_exit_resume(S), 1), n_phase, $nabs($(n - 1)))
  -- if ~$callback_review_frontier(S, n_phase)
  -- if $update_exit_resumable(S) /\ $(n > 0)
'''


def conditions(name, program, path, stdout):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_begin = $update_seek(S_initial, 0, 2500)[.COMPLETION = NORMAL]',
        '$update_warning_plan(S_begin) = (pupdatewarning)',
        'S_boundary = $update_exit_seek(S_begin, 1, 2500)[.COMPLETION = NORMAL]',
        'S_boundary.TODO = (UPDATE_WARNING_EXIT perrorcall 0) :: ptask_tail*',
        'perrorcall.RESUME = UPDATE_WARNING_RESTORE pupdatewarning',
        'perrorcall.CALLBACK = POBJECT n_handler',
        '$update_warning_exit_owning(S_boundary, perrorcall)',
        '~$update_warning_exit_named(S_boundary, perrorcall)',
        '$call_descriptors_valid(S_boundary)',
        '$task_nodes(UPDATE_WARNING_EXIT perrorcall 0) = [HOBJECT n_handler, HOBJECT n_handler]',
        'PhpStep: S_boundary ~> S_phase0',
        'S_phase0.TODO = (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup 0 0) :: ptask_tail*',
        'pdestructioncleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall',
        '~pdestructioncleanup.RELEASED',
        '$call_descriptors_valid(S_phase0)',
        'S_phase1 = $callback_review_seek(S_phase0, 1, 2500)[.COMPLETION = NORMAL]',
        'S_phase1.TODO = (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup 0 1) :: ptask_tail*',
        '$call_descriptors_valid(S_phase1)', '$heap_valid($heap_graph(S_phase1))',
        '$task_nodes(UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup 0 1) = [HOBJECT n_handler]',
        '$heap_owners($heap_prune($heap_graph(S_phase1)), HOBJECT n_handler) = 1',
        '~(n_handler <- S_phase1.DESTRUCTION.CALLED)',
        '$update_warning_pointer_value(S_phase1, pupdatewarning.POINTER) = (DEFINED (PINT 41))',
        '$integer_outputs(S_phase1.EVENTS) = ($ptascii("H:2;E;"))',
        'S_global = $global_table_view(S_phase1)',
        '$lookup(S_global.ENV, $ptascii("weak")) = (n_weak_cell)',
        'S_phase1.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
        '$weakref_get(S_phase1, n_weak) = POBJECT n_handler',
        '$lookup(S_global.ENV, $ptascii("v")) = (n_value)',
        'S_phase1.STORE[n_value] = DEFINED (PINT 100)',
        'PhpStep: S_phase1 ~> S_releasing',
        'S_releasing.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
        'pdestructionoperation.SOURCE = ERROR_HANDLER_CLEAN perrorcall',
        'pdestructionoperation.PENDING = eps',
        'pdestructionoperation.CLEANUP = (pdestructioncleanup_done)',
        'pdestructioncleanup_done = pdestructioncleanup[.RELEASED = true]',
        '$eager_operation_source_valid(S_releasing, pdestructionoperation)',
        '$call_descriptors_valid(S_releasing)',
        'S_phase2 = $callback_review_seek(S_releasing, 2, 2500)[.COMPLETION = NORMAL]',
        'S_phase2.TODO = (UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup_done 0 2) :: ptask_tail*',
        '$call_descriptors_valid(S_phase2)', '$heap_valid($heap_graph(S_phase2))',
        '$task_nodes(UPDATE_WARNING_CALLBACK_EXIT pdestructioncleanup_done 0 2) = eps',
        '$eager_cleanup_find(S_phase2.DESTRUCTION.CLEANUPS, pdestructioncleanup.SOURCE) = eps',
        '$update_callback_exit_source_valid(S_phase2, pdestructioncleanup_done)',
        '~$update_callback_exit_valid(S_phase2, pdestructioncleanup_done, 0, 3)',
        '~$update_callback_exit_valid(S_phase2, pdestructioncleanup_done, 2147483648, 2)',
        '~$update_callback_exit_valid(S_phase2, pdestructioncleanup_done[.RELEASED = false], 0, 2)',
        '~$update_callback_exit_source_valid(S_phase2[.CODE = eps], pdestructioncleanup_done)',
        '~$update_callback_exit_source_valid(S_phase2, pdestructioncleanup_done[.SOURCE = ERROR_HANDLER_RESULT perrorcall[.MESSAGE = eps]])',
        '~$update_callback_exit_source_valid(S_phase2, pdestructioncleanup_done[.SOURCE = ERROR_HANDLER_RESULT perrorcall[.TARGET = eps]])',
        'S_phase2.STORE[n_value] = DEFINED (PINT 100)',
        'S_phase2.EXITSTATUS = 0',
        'PhpStep: S_phase2 ~> S_exit',
        'S_exit.COMPLETION = NORMAL', 'S_exit.EXITSTATUS = 0',
        '$call_descriptors_valid(S_exit)', '$heap_valid($heap_graph(S_exit))',
        'S_exit.STORE[n_value] = DEFINED (PINT 100)',
        '$drive_steps(S_phase2, 0) = S_phase2[.COMPLETION = BUDGET]',
        'S_budget = $drive_steps(S_phase2, 1)', 'S_budget.COMPLETION = BUDGET',
        'S_budget = ' + update_protocol.transitioned('S_phase2', 'S_exit') + '[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_exit, 2500)',
        'S_done.COMPLETION = EXITED 0', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_budget[.COMPLETION = NORMAL], 2500) = S_done',
    ]
    if name == 'review-callback-exit-retained-registry':
        checks += [
            'pupdatewarning.INPUT = PBOOL true',
            'S_phase1.ERRORHANDLER.CALLBACK = eps',
            'S_releasing.ERRORHANDLER.CALLBACK = (POBJECT n_handler)',
            'S_phase2.ERRORHANDLER.CALLBACK = (POBJECT n_handler)',
            '(HOBJECT n_handler) <- S_phase2.ALLOCATIONS',
            '$heap_owners($heap_prune($heap_graph(S_phase2)), HOBJECT n_handler) = 1',
            '~(n_handler <- S_phase2.DESTRUCTION.CALLED)',
            '$weakref_get(S_phase2, n_weak) = POBJECT n_handler',
            '$integer_outputs(S_phase2.EVENTS) = ($ptascii("H:2;E;"))',
            '$update_warning_pointer_value(S_phase2, pupdatewarning.POINTER) = (DEFINED (PINT 41))',
            '$update_warning_pointer_value(S_exit, pupdatewarning.POINTER) = (DEFINED (PBOOL true))',
            'S_exit.ERRORHANDLER.CALLBACK = S_phase2.ERRORHANDLER.CALLBACK',
            '~(n_handler <- S_exit.DESTRUCTION.CALLED)',
        ]
    else:
        checks += [
            'n_handler <- S_phase2.DESTRUCTION.CALLED',
            '~((HOBJECT n_handler) <- S_phase2.ALLOCATIONS)',
            '$heap_owners($heap_prune($heap_graph(S_phase2)), HOBJECT n_handler) = 0',
            '$weakref_get(S_phase2, n_weak) = PNULL',
            '$integer_outputs(S_phase2.EVENTS) = ($ptascii("H:2;E;D:1;"))',
            '$update_warning_pointer_value(S_phase2, pupdatewarning.POINTER) = (DEFINED (PINT 99))',
            'S_exit.ERRORHANDLER.CALLBACK = S_phase2.ERRORHANDLER.CALLBACK',
        ]
        if name == 'review-callback-exit-owner-clears-registry':
            checks += [
                'pupdatewarning.INPUT = PBOOL true',
                'S_phase2.ERRORHANDLER.CALLBACK = eps',
                'S_exit.ERRORHANDLER.CALLBACK = eps',
                '$update_warning_pointer_value(S_exit, pupdatewarning.POINTER) = (DEFINED (PBOOL true))',
            ]
        else:
            checks += [
                'pupdatewarning.INPUT = PNULL', 'pupdatewarning.OP = DECREMENT',
                'pupdatewarning.POINTER = UPDATE_CELL n_old',
                'S_global2 = $global_table_view(S_phase2)',
                '$lookup(S_global2.ENV, $ptascii("keep")) = (n_old)',
                '$lookup(S_global2.ENV, $ptascii("x")) = (n_new)',
                '$lookup(S_global2.ENV, $ptascii("peer")) = (n_new)',
                'n_old =/= n_new',
                'S_phase2.STORE[n_new] = DEFINED (PINT 73)',
                '$heap_owners($heap_prune($heap_graph(S_phase2)), HCELL n_old) = 1',
                '$heap_owners($heap_prune($heap_graph(S_phase2)), HCELL n_new) = 2',
                'S_phase2.ERRORHANDLER.CALLBACK = (pvalue_registry)',
                '$string_bytes(pvalue_registry) = ($ptascii("h3"))',
                'S_exit.STORE[n_old] = DEFINED PNULL',
                'S_exit.STORE[n_new] = DEFINED (PINT 73)',
                '$heap_owners($heap_prune($heap_graph(S_exit)), HCELL n_old) = 1',
            ]
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path)
    args, _ = parser.parse_known_args()
    out = args.output
    if out is None:
        out = Path(tempfile.mkdtemp(prefix='callback-exit-review-', dir=protocol.runner.ROOT / '.tools'))
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
