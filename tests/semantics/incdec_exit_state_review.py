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
import incdec_parent_exit_cancellation_protocol as parent_protocol

CASES = ('review-exit-empty-postdec', 'review-exit-caller-destructor',
         'review-exit-registry-replacement', 'review-exit-parent-throw')
CALLER_HELPERS = r'''
def $update_exit_frontier(S, 3) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = EXIT_UNWIND z
'''


def parent_throw_conditions(program, path, stdout):
    return parent_protocol.conditions('parent-exit-original', program, path, stdout) + [
        '$lookup(S_global.ENV, $ptascii("x")) = (n_x)',
        'S_enter.STORE[n_x] = DEFINED (PBOOL true)',
        'S_throw.STORE[n_x] = DEFINED (PBOOL true)',
        'S_restore.STORE[n_x] = DEFINED (PBOOL true)',
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
    watched = [Path(__file__), Path(parent_protocol.__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    protocol.CASES, protocol.conditions, protocol.cases = CASES, conditions, cases
    protocol.HELPERS = parent_protocol.HELPERS + CALLER_HELPERS
    passed = protocol.main()
    assert before == {str(path): digest(path) for path in watched}
    report = json.loads((out / 'report.json').read_bytes())
    report['helper_inputs'].update(before)
    for row in report['rows']:
        row['boundary_control'] = False
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
