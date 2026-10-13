#!/usr/bin/env python3
"""Independent reached exit states for string skip and caller cleanup."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import incdec_exit_protocol as protocol
import incdec_exit_review_cases as cases

CASES = ('review-exit-empty-postdec', 'review-exit-caller-destructor',
         'review-exit-registry-replacement', 'review-exit-parent-throw')
CALLER_HELPERS = r'''
def $update_exit_frontier(S, 3) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = EXIT_UNWIND z
def $update_exit_frontier(S, 4) = true
  -- if S.TODO = (THROW_SEARCH n) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*
  -- if $update_warning_exit_parent_call(pdestructorcall)
def $update_exit_frontier(S, 5) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if $update_warning_exit_parent_call(pdestructorcall)
'''


def parent_throw_conditions(program, path, stdout):
    prefix, _ = stdout.split(b'C:', 1)
    return [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_parent = $update_exit_seek(S_initial, 5, 2500)[.COMPLETION = NORMAL]',
        'S_parent.TODO = (DESTRUCTOR_ENTER pdestructorcall_enter) :: ptask_parent*',
        '$call_descriptors_valid(S_parent)',
        'pdestructorcall_enter.OPERATION = (pdestructionoperation_enter)',
        'pdestructionoperation_enter.SOURCE = UPDATE_WARNING_EXIT perrorcall_enter 0',
        '$update_warning_exit_parent_operation(S_parent, (pdestructionoperation_enter), 0)',
        '$update_warning_exit_parent_prefix(S_parent, DESTRUCTOR_ENTER pdestructorcall_enter, 0)',
        '$exit_unwind_tasks(S_parent, S_parent.TODO, 0)',
        '$lookup($global_table_view(S_parent).ENV, $ptascii("second")) = (n_second_cell)',
        'S_parent.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        '~$update_warning_exit_parent_operation(S_parent, (pdestructionoperation_enter[.SOURCE = UPDATE_WARNING_EXIT perrorcall_enter 1]), 0)',
        '~$update_warning_exit_parent_operation(S_parent, (pdestructionoperation_enter[.PENDING = (n_second)]), 0)',
        '~$update_warning_exit_parent_operation(S_parent, (pdestructionoperation_enter[.VALUE = KNOWN (PINT 41)]), 0)',
        '~$update_warning_exit_parent_operation(S_parent[.CODE = eps], (pdestructionoperation_enter), 0)',
        'S_guard = $update_exit_seek(S_parent, 4, 2500)[.COMPLETION = NORMAL]',
        'S_guard.TODO = (THROW_SEARCH n_second) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*',
        '$call_descriptors_valid(S_guard)', '$heap_valid($heap_graph(S_guard))',
        '$destructor_result_valid(S_guard, pdestructorcall)',
        'pdestructorcall.OPERATION = (pdestructionoperation)',
        'pdestructionoperation.SOURCE = UPDATE_WARNING_EXIT perrorcall 0',
        'perrorcall.RESUME = UPDATE_WARNING_RESTORE pupdatewarning',
        'pupdatewarning.INPUT = PBOOL true',
        'S_global = $global_table_view(S_guard)',
        '$lookup(S_global.ENV, $ptascii("x")) = (n_x)',
        '$lookup(S_global.ENV, $ptascii("v")) = (n_value)',
        '$lookup(S_global.ENV, $ptascii("second")) = (n_second_cell)',
        'S_guard.STORE[n_x] = DEFINED (PBOOL true)',
        'S_guard.STORE[n_value] = DEFINED (PINT 100)',
        'S_guard.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]',
        '$integer_outputs(S_guard.EVENTS) = ([' + ','.join(map(str, prefix)) + '])',
        '$update_warning_exit_parent_call(pdestructorcall)',
        '$throwable_marker(DESTRUCTOR_RESULT pdestructorcall)',
        '~$exception_terminal_tail(S_guard, (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*)',
        '$eager_bailout_source(S_guard) = eps',
        '$eager_operation_source_guard(S_guard, pdestructionoperation)',
        '$update_warning_exit_parent_prefix(S_guard, DESTRUCTOR_RESULT pdestructorcall, 0)',
        '$exit_unwind_tasks(S_guard, S_guard.TODO, 0)',
        '~$eager_operation_source_guard(S_guard, pdestructionoperation[.SOURCE = UPDATE_WARNING_EXIT perrorcall[.MESSAGE = eps] 0])',
        '~$eager_operation_source_guard(S_guard, pdestructionoperation[.SOURCE = UPDATE_WARNING_EXIT perrorcall 2147483648])',
        '~$eager_operation_source_guard(S_guard[.CODE = eps], pdestructionoperation)',
        'PhpStep: S_guard ~> S_failure',
        'S_failure.COMPLETION = UNSUPPORTED "increment/decrement warning exit parent cleanup throw"',
        'S_failure.STORE = S_guard.STORE', 'S_failure.EVENTS = S_guard.EVENTS',
        'S_failure.TODO = S_guard.TODO', 'S_failure.ALLOCATIONS = S_guard.ALLOCATIONS',
        'S_failure.DESTRUCTION = S_guard.DESTRUCTION',
        '$drive_steps(S_guard, 0) = S_guard[.COMPLETION = BUDGET]',
        'S_closed = $drive_steps(S_guard, 1)',
        'S_closed.COMPLETION = UNSUPPORTED "increment/decrement warning exit parent cleanup throw"',
        'S_closed.EVENTS = S_guard.EVENTS',
    ]


def conditions(name, program, path, stdout):
    if name == 'review-exit-parent-throw':
        return parent_throw_conditions(program, path, stdout)
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_begin = $update_seek(S_initial, 0, 2500)[.COMPLETION = NORMAL]',
        '$update_warning_plan(S_begin) = (pupdatewarning)',
        'pupdatewarning.PENDING = eps',
        'S_invoke = $update_exit_seek(S_begin, 0, 2500)[.COMPLETION = NORMAL]',
        '$call_descriptors_valid(S_invoke)',
        'PhpStep: S_invoke ~> S_requested',
        'S_requested.COMPLETION = EXITED 0',
        '$update_warning_exit_unwind(S_requested)',
        'S_boundary = $update_exit_seek(S_requested, 1, 2500)[.COMPLETION = NORMAL]',
        'S_boundary.TODO = (UPDATE_WARNING_EXIT perrorcall 0) :: ptask_tail*',
        'perrorcall.RESUME = UPDATE_WARNING_RESTORE pupdatewarning',
        '$call_descriptors_valid(S_boundary)',
        '$task_nodes(UPDATE_WARNING_EXIT perrorcall 0) = eps',
        '$throwable_marker(UPDATE_WARNING_EXIT perrorcall 0)',
        'S_global = $global_table_view(S_boundary)',
        '$lookup(S_global.ENV, $ptascii("x")) = (n_x)',
        '$lookup(S_global.ENV, $ptascii("v")) = (n_value)',
        'S_boundary.STORE[n_x] = DEFINED (PINT 41)',
        'S_boundary.STORE[n_value] = DEFINED (PINT 100)',
    ]
    if name == 'review-exit-empty-postdec':
        checks += [
            'pupdatewarning.OP = DECREMENT', 'pupdatewarning.POST',
            '$string_bytes(pupdatewarning.INPUT) = (eps)',
            'pupdatewarning.POINTER = UPDATE_CV ($ptascii("x"))',
            '$update_warning_after(DECREMENT, pupdatewarning.INPUT) = (PINT (-1))',
            '~$update_warning_restores_throw(pupdatewarning.INPUT)',
        ]
    else:
        checks += ['pupdatewarning.INPUT = PBOOL true', 'pupdatewarning.OP = INCREMENT',
                   '~pupdatewarning.POST']
    if name == 'review-exit-caller-destructor':
        checks += [
            'pupdatewarning.POINTER = UPDATE_CELL n_x',
            'S_boundary.CURRENT = (pcallcontext)',
            'S_boundary.FRAMES = pframe :: pframe_caller*',
            '$lookup(S_boundary.ENV, $ptascii("outer")) = (n_outer_cell)',
            'S_boundary.STORE[n_outer_cell] = DEFINED (POBJECT n_outer)',
            '(HOBJECT n_outer) <- S_boundary.ALLOCATIONS',
            '~(n_outer <- S_boundary.DESTRUCTION.CALLED)',
            '$heap_owners($heap_prune($heap_graph(S_boundary)), HOBJECT n_outer) = 1',
        ]
    if name == 'review-exit-registry-replacement':
        checks += [
            'S_boundary.ERRORHANDLER.CALLBACK = (pvalue_registered)',
            '$string_bytes(pvalue_registered) = ($ptascii("h2"))',
            'pvalue_registered =/= perrorcall.CALLBACK',
            '$update_warning_exit_named(S_boundary, perrorcall)',
            '~$update_warning_exit_named(S_boundary, perrorcall[.RESUME = UPDATE_WARNING_RESTORE pupdatewarning[.POST = true]])',
            '~$update_warning_exit_named(S_boundary, perrorcall[.RESUME = UPDATE_WARNING_RESTORE pupdatewarning[.NAME = $ptascii("missing")]])',
            '~$update_warning_exit_named(S_boundary, perrorcall[.RESUME = UPDATE_WARNING_RESTORE pupdatewarning[.INPUT = PINT 41]])',
            '~$call_task_valid(S_boundary[.ORIGIN = eps], UPDATE_WARNING_EXIT perrorcall 0)',
            'perrorcall_bad = perrorcall[.RESUME = UPDATE_WARNING_RESTORE pupdatewarning[.LINE = $(pupdatewarning.LINE + 1)]]',
            'S_bad = S_boundary[.TODO = (UPDATE_WARNING_EXIT perrorcall_bad 0) :: ptask_tail*]',
            '$scope_codes_valid(S_bad, S_bad.CODE)', '~$call_descriptors_valid(S_bad)',
            '$drive(S_bad, 1).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
        ]
    else:
        checks += ['S_boundary.ERRORHANDLER.CALLBACK = eps']
    checks += [
        'PhpStep: S_boundary ~> S_continue',
        'S_continue.TODO = [EXIT_UNWIND 0]', 'S_continue.ORIGIN = eps',
        'S_continue.COMPLETION = NORMAL', 'S_continue.EXITSTATUS = 0',
        'S_continue.EVENTS = S_boundary.EVENTS',
        'S_continue.FRAMES = S_boundary.FRAMES',
        'S_continue.STORE[n_value] = DEFINED (PINT 100)',
        '$call_descriptors_valid(S_continue)', '$heap_valid($heap_graph(S_continue))',
    ]
    if name == 'review-exit-empty-postdec':
        checks += ['S_continue.STORE = S_boundary.STORE',
                   'S_continue.STORE[n_x] = DEFINED (PINT 41)']
    else:
        checks += ['S_continue.STORE[n_x] = DEFINED (PBOOL true)']
    if name == 'review-exit-registry-replacement':
        checks += ['S_continue.ERRORHANDLER = S_boundary.ERRORHANDLER']
    else:
        checks += ['S_continue.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)']
    checks += [
        '$drive_steps(S_boundary, 0) = S_boundary[.COMPLETION = BUDGET]',
        'S_budget = $drive_steps(S_boundary, 1)', 'S_budget.COMPLETION = BUDGET',
        'S_budget = ' + protocol.update_runner.transitioned('S_boundary', 'S_continue') + '[.COMPLETION = BUDGET]',
    ]
    if name == 'review-exit-caller-destructor':
        checks += [
            'S_continue.CURRENT = S_boundary.CURRENT',
            '$heap_owners($heap_prune($heap_graph(S_continue)), HOBJECT n_outer) = 1',
            '~(n_outer <- S_continue.DESTRUCTION.CALLED)',
            'S_cleanup = $update_exit_seek(S_continue, 3, 2500)[.COMPLETION = NORMAL]',
            'S_cleanup.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_cleanup*',
            'pdestructorcall.OBJECT = n_outer',
            'pdestructorcall.OPERATION = (pdestructionoperation)',
            'pdestructionoperation.SOURCE = EXIT_UNWIND 0',
            '$call_descriptors_valid(S_cleanup)',
            '~$update_warning_exit_pending(S_cleanup)',
            'S_cleanup.STORE[n_x] = DEFINED (PBOOL true)',
            'S_cleanup.STORE[n_value] = DEFINED (PINT 100)',
            '$integer_outputs(S_cleanup.EVENTS) = ($ptascii("H:2;E;"))',
        ]
    checks += [
        'S_done = $drive_steps(S_continue, 2500)', 'S_done.COMPLETION = EXITED 0',
        'S_done.EXITSTATUS = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        'S_done.FRAMES = eps', 'S_done.TODO = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_budget[.COMPLETION = NORMAL], 2500) = S_done',
    ]
    if name == 'review-exit-caller-destructor':
        checks += ['n_outer <- S_done.DESTRUCTION.CALLED',
                   '$heap_owners($heap_prune($heap_graph(S_done)), HOBJECT n_outer) = 0',
                   '$drive_steps(S_cleanup, 2500) = S_done']
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path)
    args, _ = parser.parse_known_args()
    out = args.output
    if out is None:
        out = Path(tempfile.mkdtemp(prefix='incdec-exit-state-review-', dir=protocol.runner.ROOT / '.tools'))
        sys.argv += ['--output', str(out)]
    wrapper = Path(__file__)
    before = hashlib.sha256(wrapper.read_bytes()).hexdigest()
    protocol.CASES, protocol.conditions, protocol.cases = CASES, conditions, cases
    protocol.HELPERS += CALLER_HELPERS
    passed = protocol.main()
    assert before == hashlib.sha256(wrapper.read_bytes()).hexdigest()
    report = json.loads((out / 'report.json').read_bytes())
    report['helper_inputs'][str(wrapper)] = before
    for row in report['rows']:
        row['boundary_control'] = row['id'] == 'review-exit-parent-throw'
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
