#!/usr/bin/env python3
"""Independent cancellation, late aliases, nested caller and parent-owner checks."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import incdec_exit_cancellation_protocol as protocol
import incdec_exit_cancellation_review_cases as cases

CASES = ('review-exit-cancel-null-late-peer', 'review-exit-cancel-nested-catch',
         'review-exit-cancel-parent-owner')
PARENT_HELPERS = r'''
def $update_exit_frontier(S, 7) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if $class_named(S.CLASSNAMES, $ptascii("parentt")) = (porigin_parent)
  -- if S.OBJECTS[pdestructorcall.OBJECT] = INSTANCE porigin_parent
'''


def conditions(name, program, path, stdout):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_begin = $update_seek(S_initial, 0, 2500)[.COMPLETION = NORMAL]',
        '$update_warning_plan(S_begin) = (pupdatewarning_first)',
        'S_guard = $update_exit_seek(S_begin, 6, 2500)[.COMPLETION = NORMAL]',
        'S_guard.TODO = (THROW_SEARCH n_second) :: (UPDATE_WARNING_EXIT perrorcall 0) :: ptask_tail*',
        'perrorcall.RESUME = UPDATE_WARNING_RESTORE pupdatewarning',
        '$call_descriptors_valid(S_guard)', '$heap_valid($heap_graph(S_guard))',
        'S_guard.EXITSTATUS = 0', 'S_guard.RESULT = KNOWN PNULL',
        'S_guard.BASE = BASE_VALUE (KNOWN PNULL)', 'pupdatewarning.PENDING = eps',
        '$update_warning_exit_named(S_guard, perrorcall)',
        '$update_warning_exit_cancel_safe(S_guard, perrorcall)',
        '$throwable_live(S_guard, n_second)',
        '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]',
        '$task_nodes(UPDATE_WARNING_EXIT perrorcall 0) = eps',
        'S_global = $global_table_view(S_guard)',
        '$lookup(S_global.ENV, $ptascii("second")) = (n_second_cell)',
        'S_guard.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        '$lookup(S_global.ENV, $ptascii("v")) = (n_value)',
        'S_guard.STORE[n_value] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_guard)), HOBJECT n_second) = 2',
        '$throwable_previous_id(S_guard, n_second) = eps',
        'PhpStep: S_guard ~> S_pending',
        'S_pending.TODO = (UPDATE_WARNING_DONE pupdatewarning_pending) :: ptask_tail*',
        'pupdatewarning_pending = pupdatewarning[.PENDING = (n_second)]',
        '$task_nodes(UPDATE_WARNING_DONE pupdatewarning_pending) = [HOBJECT n_second]',
        'S_pending.COMPLETION = NORMAL', 'S_pending.EXITSTATUS = 0',
        'S_pending.RESULT = KNOWN PNULL', 'S_pending.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_pending.CURRENT = S_guard.CURRENT', 'S_pending.FRAMES = S_guard.FRAMES',
        'S_pending.ORIGIN = S_guard.ORIGIN', 'S_pending.EVENTS = S_guard.EVENTS',
        '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
        '$heap_owners($heap_prune($heap_graph(S_pending)), HOBJECT n_second) = 2',
        '$throwable_previous_id(S_pending, n_second) = eps',
        'S_pending.STORE[n_value] = DEFINED (PINT 100)',
    ]
    if name == 'review-exit-cancel-nested-catch':
        checks += [
            'pupdatewarning_first.INPUT = PBOOL true',
            'pupdatewarning_first.NAME = $ptascii("x")',
            'pupdatewarning.INPUT = PBOOL false', 'pupdatewarning.OP = INCREMENT',
            '~pupdatewarning.POST', 'pupdatewarning.NAME = $ptascii("y")',
            'S_guard.CURRENT = (pcallcontext)',
            'S_guard.FRAMES = pframe_outer :: pframe_tail*',
            'pframe_outer.TODO = (ERROR_HANDLER_RESULT perrorcall_outer) :: ptask_outer*',
            'perrorcall_outer.RESUME = UPDATE_WARNING_RESTORE pupdatewarning_first',
            '$lookup(S_global.ENV, $ptascii("x")) = (n_x)',
            '$lookup(S_global.ENV, $ptascii("y")) = (n_y)',
            '$lookup(S_global.ENV, $ptascii("w")) = (n_w)',
            '$lookup(S_guard.ENV, $ptascii("y")) = (n_y)',
            'pupdatewarning.POINTER = UPDATE_CELL n_y',
            'S_guard.STORE[n_x] = DEFINED (PINT 41)',
            'S_guard.STORE[n_y] = DEFINED (PINT 73)',
            'S_guard.STORE[n_w] = DEFINED (PINT 200)',
            'S_pending.STORE[n_x] = DEFINED (PINT 41)',
            'S_pending.STORE[n_y] = DEFINED (PBOOL false)',
            'S_pending.STORE[n_w] = DEFINED (PINT 200)',
            'S_guard.ERRORHANDLER.CALLBACK = (pvalue_registered)',
            '$string_bytes(pvalue_registered) = ($ptascii("h3"))',
            'pvalue_registered =/= perrorcall.CALLBACK',
            'S_pending.ERRORHANDLER = S_guard.ERRORHANDLER',
            'S_pending.ERRORHANDLERS = S_guard.ERRORHANDLERS',
        ]
    else:
        checks += [
            'pupdatewarning_first = pupdatewarning',
            'pupdatewarning.POINTER = UPDATE_CV ($ptascii("x"))',
            '$lookup(S_global.ENV, $ptascii("x")) = (n_x_old)',
            'S_guard.STORE[n_x_old] = DEFINED (PINT 41)',
            'S_pending.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)',
        ]
        if name == 'review-exit-cancel-null-late-peer':
            checks += [
                'pupdatewarning.INPUT = PNULL', 'pupdatewarning.OP = DECREMENT',
                'pupdatewarning.POST',
                '$lookup(S_global.ENV, $ptascii("peer")) = (n_x_old)',
                'n_x_old <- S_guard.REFCELLS',
                '$heap_owners($heap_prune($heap_graph(S_guard)), HCELL n_x_old) = 2',
                '$lookup($global_table_view(S_pending).ENV, $ptascii("x")) = (n_x_new)',
                'n_x_old =/= n_x_new', '~(n_x_new <- S_pending.REFCELLS)',
                '$lookup($global_table_view(S_pending).ENV, $ptascii("peer")) = (n_x_old)',
                'S_pending.STORE[n_x_old] = DEFINED (PINT 41)',
                'S_pending.STORE[n_x_new] = DEFINED PNULL',
                '$heap_owners($heap_prune($heap_graph(S_pending)), HCELL n_x_old) = 1',
                '$heap_owners($heap_prune($heap_graph(S_pending)), HCELL n_x_new) = 1',
            ]
        else:
            checks += ['pupdatewarning.INPUT = PBOOL true', 'pupdatewarning.OP = INCREMENT',
                       '~pupdatewarning.POST', 'S_pending.STORE[n_x_old] = DEFINED (PBOOL true)']
    checks += [
        'PhpStep: S_pending ~> S_search',
        'S_search.TODO = (THROW_SEARCH n_second) :: ptask_tail*',
        'S_search.STORE = S_pending.STORE', 'S_search.EVENTS = S_pending.EVENTS',
        'S_search.EXITSTATUS = 0', '$call_descriptors_valid(S_search)',
        '$heap_owners($heap_prune($heap_graph(S_search)), HOBJECT n_second) = 2',
        '$drive_steps(S_guard, 0) = S_guard[.COMPLETION = BUDGET]',
        'S_budget = $drive_steps(S_guard, 1)', 'S_budget.COMPLETION = BUDGET',
        'S_budget = ' + protocol.update_protocol.transitioned('S_guard', 'S_pending') + '[.COMPLETION = BUDGET]',
    ]
    if name == 'review-exit-cancel-parent-owner':
        checks += [
            'S_cleanup = $update_exit_seek(S_search, 7, 2500)[.COMPLETION = NORMAL]',
            'S_cleanup.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_cleanup*',
            '$class_named(S_cleanup.CLASSNAMES, $ptascii("parentt")) = (porigin_parent)',
            'pdestructorcall.OBJECT = n_parent',
            'S_guard.OBJECTS[n_parent] = INSTANCE porigin_parent',
            '$call_descriptors_valid(S_cleanup)', '$heap_valid($heap_graph(S_cleanup))',
            '$destructor_enter_valid(S_cleanup, pdestructorcall)',
            '~$update_warning_exit_parent_call(pdestructorcall)',
            '$heap_owners($heap_prune($heap_graph(S_guard)), HOBJECT n_parent) = 1',
            '$heap_owners($heap_prune($heap_graph(S_pending)), HOBJECT n_parent) = 1',
            '$heap_owners($heap_prune($heap_graph(S_search)), HOBJECT n_parent) = 1',
            '~(n_parent <- S_guard.DESTRUCTION.CALLED)',
            '~(n_parent <- S_pending.DESTRUCTION.CALLED)',
            'S_cleanup.STORE[n_x_old] = DEFINED (PBOOL true)',
            'S_cleanup.STORE[n_value] = DEFINED (PINT 100)',
            '$integer_outputs(S_cleanup.EVENTS) = ($ptascii("H:2;E;L:1;"))',
        ]
    checks += [
        'S_done = $drive_steps(S_search, 2500)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        'S_done.TODO = eps', 'S_done.FRAMES = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_budget[.COMPLETION = NORMAL], 2500) = S_done',
    ]
    if name == 'review-exit-cancel-parent-owner':
        checks += ['n_parent <- S_done.DESTRUCTION.CALLED',
                   '$drive_steps(S_cleanup, 2500) = S_done']
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path)
    args, _ = parser.parse_known_args()
    out = args.output
    if out is None:
        out = Path(tempfile.mkdtemp(prefix='incdec-exit-cancel-review-', dir=protocol.runner.ROOT / '.tools'))
        sys.argv += ['--output', str(out)]
    wrapper = Path(__file__)
    before = hashlib.sha256(wrapper.read_bytes()).hexdigest()
    protocol.CASES, protocol.conditions, protocol.cases = CASES, conditions, cases
    protocol.HELPERS += PARENT_HELPERS
    passed = protocol.main()
    assert before == hashlib.sha256(wrapper.read_bytes()).hexdigest()
    report = json.loads((out / 'report.json').read_bytes())
    report['helper_inputs'][str(wrapper)] = before
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
