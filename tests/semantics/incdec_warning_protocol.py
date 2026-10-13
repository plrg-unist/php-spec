#!/usr/bin/env python3
"""Genuine update-warning frontiers, restoration and supplied-throw replay."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import sys
import tempfile

import incdec_warning_cases as cases
import incdec_warning_review_cases as review_cases
import integer_operator_warning_protocol as runner

ROOT = Path(__file__).resolve().parents[2]
CASES = ('pre-inc-bool-true-return', 'post-dec-string-return',
         'pre-dec-null-throw', 'post-dec-string-throw',
         'pre-inc-reference-rebind', 'pre-inc-new-reference',
         'pre-inc-array-replacement', 'destructor-bool-return',
         'review-handler-exit-bool')
HELPERS = runner.HELPERS + r'''
dec $update_frontier(pstate, nat) : bool
def $update_frontier(S, 0) = ($update_warning_plan(S) =/= eps)
def $update_frontier(S, 1) = true
  -- if S.TODO = (UPDATE_WARNING_NOTICE pupdatewarning) :: ptask_tail*
def $update_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = UPDATE_WARNING_RESTORE pupdatewarning
def $update_frontier(S, 3) = true
  -- if S.TODO = (UPDATE_WARNING_RESTORE pupdatewarning) :: ptask_tail*
def $update_frontier(S, 4) = true
  -- if S.TODO = (EXIT_INVOKE pexitcall) :: ptask_tail*
  -- if $update_warning_exit_pending(S)
def $update_frontier(S, 5) = true
  -- if S.TODO = (UPDATE_WARNING_EXIT perrorcall z) :: ptask_tail*
def $update_frontier(S, n) = false -- otherwise
dec $update_seek(pstate, nat, nat) : pstate
def $update_seek(S, n_stage, n) = S -- if $update_frontier(S, n_stage)
def $update_seek(S, n_stage, n) = S
  -- if ~$update_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $update_seek(S, n_stage, n) = S
  -- if ~$update_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $update_seek(S, n_stage, n) = $update_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$update_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def transitioned(before, after):
    return ('$gc_transition_owners(' + before + ', $destruction_transition_owners('
            + before + ', $sensitive_trace_freeze($source_exception_transition('
            + before + ', $throwable_transition(' + before + ', ' + after + ')))))')


def conditions(name, program, path, stdout):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_entry = $update_seek(S_initial, 0, 2000)[.COMPLETION = NORMAL]',
        '$update_frontier(S_entry, 0)', '$call_descriptors_valid(S_entry)',
        '$update_warning_plan(S_entry) = (pupdatewarning)',
        '$update_warning_valid(S_entry, pupdatewarning)',
        '~$update_warning_valid(S_entry, pupdatewarning[.LINE = $(pupdatewarning.LINE + 1)])',
        '~$update_warning_valid(S_entry, pupdatewarning[.POST = ~pupdatewarning.POST])',
        '~$update_warning_valid(S_entry, pupdatewarning[.NAME = $ptascii("missing")])',
        '~$update_warning_valid(S_entry, pupdatewarning[.INPUT = PINT 41])',
        '~$update_warning_valid(S_entry[.ORIGIN = eps], pupdatewarning)',
        'n_invalid = |S_entry.STORE|',
        '~$update_warning_valid(S_entry, pupdatewarning[.POINTER = UPDATE_CELL n_invalid])',
        'PhpStep: S_entry ~> S_capture',
        'S_capture.TODO = (UPDATE_WARNING_NOTICE pupdatewarning) :: ptask_tail*',
        'S_capture.STORE = S_entry.STORE', 'S_capture.ALLOCATIONS = S_entry.ALLOCATIONS',
        '$task_nodes(UPDATE_WARNING_NOTICE pupdatewarning) = eps',
        '$call_task_valid(S_capture, UPDATE_WARNING_NOTICE pupdatewarning)',
        '$call_descriptors_valid(S_capture)',
        'PhpStep: S_capture ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = UPDATE_WARNING_RESTORE pupdatewarning',
        '$update_warning_notice(pupdatewarning.OP, pupdatewarning.INPUT) = ((perrorcall.LEVEL, perrorcall.MESSAGE))',
        '$error_call_valid(S_dispatch, perrorcall)', '$call_descriptors_valid(S_dispatch)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 512])',
        '~$error_call_valid(S_dispatch, perrorcall[.MESSAGE = eps])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '~$error_call_valid(S_dispatch, perrorcall[.RESUME = UPDATE_WARNING_NOTICE pupdatewarning])',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_capture, 1) = ' + transitioned('S_capture', 'S_dispatch') + '[.COMPLETION = BUDGET]',
    ]
    if name == 'review-handler-exit-bool':
        return checks + [
            'S_pending = $update_seek(S_dispatch, 4, 2000)[.COMPLETION = NORMAL]',
            '$update_frontier(S_pending, 4)', '$call_descriptors_valid(S_pending)',
            'PhpStep: S_pending ~> S_exit',
            '$update_warning_exit_pending(S_exit)',
            '~$update_warning_exit_pending(S_exit[.FRAMES = eps][.TODO = eps])',
            'S_exit.COMPLETION = EXITED 0',
            'S_global = $global_table_view(S_exit)',
            '$lookup(S_global.ENV, $ptascii("x")) = (n_live)',
            'S_exit.STORE[n_live] = DEFINED (PINT 41)',
            'S_unwind = $exit_start_unwind(S_exit, 0)',
            'S_unwind.COMPLETION = NORMAL', 'S_unwind.TODO = [EXIT_UNWIND 0]',
            'S_restore = $update_seek(S_unwind, 5, 2500)[.COMPLETION = NORMAL]',
            'S_restore.TODO = (UPDATE_WARNING_EXIT perrorcall_exit 0) :: ptask_exit*',
            'perrorcall_exit.RESUME = UPDATE_WARNING_RESTORE pupdatewarning',
            '$call_descriptors_valid(S_restore)',
            '$update_warning_pointer_value(S_restore, pupdatewarning.POINTER) = (DEFINED (PINT 41))',
            'S_closed = $drive_steps(S_exit, 2500)',
            'S_closed.COMPLETION = EXITED 0', 'S_closed.EXITSTATUS = 0',
            '$integer_outputs(S_closed.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        ]
    if name == 'post-dec-string-throw':
        return checks + [
            '~$update_warning_restores_throw(pupdatewarning.INPUT)',
            'S_done = $drive_steps(S_dispatch, 2500)',
            'S_done.COMPLETION = NORMAL',
            '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
            '$lookup(S_done.ENV, $ptascii("x")) = (n_live)',
            'S_done.STORE[n_live] = DEFINED (PINT 41)',
            '$lookup(S_done.ENV, $ptascii("v")) = (n_value)',
            'S_done.STORE[n_value] = DEFINED (PINT 100)',
            'S_done.FRAMES = eps', '$call_descriptors_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
        ]
    checks += [
        'S_return = $update_seek(S_dispatch, 3, 2000)[.COMPLETION = NORMAL]',
        'S_return.TODO = (UPDATE_WARNING_RESTORE pupdatewarning_return) :: ptask_return*',
        'pupdatewarning_return[.PENDING = eps] = pupdatewarning',
        '$update_warning_valid(S_return, pupdatewarning_return)',
        '$call_descriptors_valid(S_return)',
        '$update_warning_pointer_value(S_return, pupdatewarning.POINTER) = (pslot_changed)',
    ]
    if name == 'destructor-bool-return':
        return checks + [
            'pslot_changed = DEFINED (POBJECT n_object)',
            '~$update_warning_release_safe(S_return, pslot_changed)',
            'PhpStep: S_return ~> S_prepare',
            'S_prepare.TODO = (UPDATE_WARNING_RELEASE pupdaterestore) :: ptask_return*',
            'pupdaterestore.WARNING = pupdatewarning_return',
            'S_prepare.STORE = S_return.STORE', 'S_prepare.EVENTS = S_return.EVENTS',
            '~(n_object <- S_prepare.DESTRUCTION.CALLED)',
            '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
            'S_done = $drive_steps(S_prepare, 2500)', 'S_done.COMPLETION = NORMAL',
            '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
            'n_object <- S_done.DESTRUCTION.CALLED',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        ]
    checks += ['$update_warning_release_safe(S_return, pslot_changed)']
    if name == 'pre-dec-null-throw':
        checks += [
            'pupdatewarning_return.PENDING = (n_failure)',
            '$lookup(S_return.ENV, $ptascii("failure")) = (n_failure_cell)',
            'S_return.STORE[n_failure_cell] = DEFINED (POBJECT n_failure)',
            '$task_nodes(UPDATE_WARNING_RESTORE pupdatewarning_return) = [HOBJECT n_failure]',
            '$update_warning_restores_throw(pupdatewarning.INPUT)',
        ]
    else:
        checks += ['pupdatewarning_return.PENDING = eps',
                   '$task_nodes(UPDATE_WARNING_RESTORE pupdatewarning_return) = eps']
    if name == 'pre-inc-reference-rebind':
        checks += [
            'pupdatewarning.POINTER = UPDATE_CELL n_old',
            '$lookup(S_entry.ENV, $ptascii("x")) = (n_old)',
            '$lookup(S_return.ENV, $ptascii("keep")) = (n_old)',
            '$lookup(S_return.ENV, $ptascii("x")) = (n_peer)', 'n_old =/= n_peer',
            '$lookup(S_return.ENV, $ptascii("peer")) = (n_peer)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_old) = 1',
            'pslot_changed = DEFINED (PINT 41)',
            '~$error_call_valid(S_dispatch, perrorcall[.RESUME = UPDATE_WARNING_RESTORE pupdatewarning[.POINTER = UPDATE_CV pupdatewarning.NAME]])',
        ]
    elif name == 'pre-inc-new-reference':
        checks += [
            'pupdatewarning.POINTER = UPDATE_CV pupdatewarning.NAME',
            '$lookup(S_return.ENV, $ptascii("x")) = (n_peer)',
            '$lookup(S_return.ENV, $ptascii("peer")) = (n_peer)',
            'n_peer <- S_return.REFCELLS',
            '~$error_call_valid(S_dispatch, perrorcall[.RESUME = UPDATE_WARNING_RESTORE pupdatewarning[.POINTER = UPDATE_CELL n_peer]])',
        ]
    elif name == 'pre-inc-array-replacement':
        checks += ['pslot_changed = DEFINED (PARRAY n_array)',
                   '$heap_count(HARRAY n_array, $pools_nodes(S_return.POOLS)) = 1',
                   '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_array) = 2']
    else:
        checks += ['pslot_changed = DEFINED (PINT 41)']
    checks += [
        'PhpStep: S_return ~> S_commit',
        'S_commit.TODO = (UPDATE_WARNING_DONE pupdatewarning_return) :: ptask_return*',
        '$update_warning_after(pupdatewarning.OP, pupdatewarning.INPUT) = (pvalue_after)',
        '$update_warning_pointer_value(S_commit, pupdatewarning.POINTER) = (DEFINED pvalue_after)',
        '$call_descriptors_valid(S_commit)',
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
        '$drive_steps(S_return, 1) = ' + transitioned('S_return', 'S_commit') + '[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_commit, 2500)', 'S_done.COMPLETION = NORMAL',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        'S_done.FRAMES = eps', 'S_done.HELD = eps', '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
        'S_budget = $drive_steps(S_return, 1)',
        '$drive_steps(S_budget[.COMPLETION = NORMAL], 2500) = S_done',
    ]
    if name == 'pre-inc-reference-rebind':
        checks += ['$string_bytes(pvalue_after) = ($ptascii("Ba0"))',
                   'S_commit.STORE[n_peer] = S_return.STORE[n_peer]',
                   '$lookup(S_commit.ENV, $ptascii("x")) = (n_peer)',
                   '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_old) = 1']
    if name == 'pre-inc-new-reference':
        checks += ['$lookup(S_commit.ENV, $ptascii("x")) = (n_new)', 'n_new =/= n_peer',
                   '~(n_new <- S_commit.REFCELLS)',
                   'S_commit.STORE[n_peer] = S_return.STORE[n_peer]']
    if name == 'pre-inc-array-replacement':
        checks += ['S_commit.POOLS = S_return.POOLS',
                   '$heap_owners($heap_prune($heap_graph(S_commit)), HARRAY n_array) = 1']
    if name == 'pre-dec-null-throw':
        checks += ['PhpStep: S_commit ~> S_resume',
                   'S_resume.TODO = (THROW_SEARCH n_failure) :: ptask_return*',
                   'S_resume.RESULT = KNOWN PNULL']
    else:
        checks += ['PhpStep: S_commit ~> S_result',
                   'S_result.TODO = ptask_return*',
                   'S_result.RESULT = KNOWN ' + ('pupdatewarning.INPUT' if name.startswith('post') else 'pvalue_after')]
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path)
    args, _ = parser.parse_known_args()
    out = args.output
    if out is None:
        out = Path(tempfile.mkdtemp(prefix='incdec-warning-protocol-', dir=ROOT / '.tools'))
        sys.argv += ['--output', str(out)]
    watched = [Path(__file__), Path(runner.__file__), Path(cases.__file__), Path(review_cases.__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    runner.CASES, runner.HELPERS, runner.conditions = CASES, HELPERS, conditions
    runner.sources = cases
    runner.sources.CASES = {**cases.CASES, **review_cases.CASES}
    runner.__file__ = __file__
    passed = runner.main()
    assert before == {str(path): digest(path) for path in watched}
    report = json.loads((out / 'report.json').read_bytes())
    report['helper_inputs'] = before
    for row in report['rows']:
        if 'model' in row:
            result = row['model']
            row['passed'] = (row['passed'] and result['interruption'] is None and result['group_after'] == []
                             and (out / (row['id'] + '-model.stdout')).read_bytes() == b'true\n')
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    passed = passed and all(row.get('passed', True) for row in report['rows'])
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
