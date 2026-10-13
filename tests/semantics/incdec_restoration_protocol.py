#!/usr/bin/env python3
"""Source-reached before-commit destruction, roots and budget replay."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import sys
import tempfile

import incdec_restoration_cases as cases
import incdec_restoration_review_cases as review_cases
import incdec_warning_protocol as update_runner
import integer_operator_warning_protocol as runner

ROOT = Path(__file__).resolve().parents[2]
CASES = ('pre-inc-object-string', 'post-inc-object-write-bool',
         'pre-dec-object-null-handler-throw', 'pre-inc-object-both-throw-bool',
         'pre-inc-object-retained-reference', 'pre-inc-unique-wrapper-string',
         'pre-inc-array-ordered-throw', 'review-destructor-resurrection',
         'pre-inc-plain-object-handler-throw',
         'review-destructor-late-property-source', 'review-destructor-exit-bool')
HELPERS = update_runner.HELPERS + r'''
dec $restore_frontier(pstate, nat) : bool
def $restore_frontier(S, 0) = true
  -- if S.TODO = (UPDATE_WARNING_RESTORE pupdatewarning) :: ptask_tail*
  -- if $update_restore_capture(S, pupdatewarning) =/= eps
def $restore_frontier(S, 1) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = UPDATE_WARNING_RELEASE pupdaterestore
def $restore_frontier(S, 2) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = UPDATE_WARNING_RELEASE pupdaterestore
def $restore_frontier(S, 3) = ($update_raw_identity_plan(S) =/= eps)
def $restore_frontier(S, 4) = true
  -- if S.TODO = (EXIT_INVOKE pexitcall) :: ptask_tail*
  -- if $update_warning_exit_pending(S)
def $restore_frontier(S, n) = false -- otherwise
dec $restore_seek(pstate, nat, nat) : pstate
def $restore_seek(S, n_stage, n) = S -- if $restore_frontier(S, n_stage)
def $restore_seek(S, n_stage, n) = S
  -- if ~$restore_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $restore_seek(S, n_stage, 0) = S
  -- if ~$restore_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $restore_seek(S, n_stage, n) = $restore_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$restore_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_restore = $restore_seek(S_initial, 0, 3000)[.COMPLETION = NORMAL]',
        '$restore_frontier(S_restore, 0)', '$call_descriptors_valid(S_restore)',
        'S_restore.TODO = (UPDATE_WARNING_RESTORE pupdatewarning) :: ptask_tail*',
        '$update_restore_capture(S_restore, pupdatewarning) = (pupdaterestore)',
        'pupdaterestore.WARNING = pupdatewarning',
        'pupdaterestore.CALLER = S_restore.CURRENT',
        'pupdaterestore.CONSTCONTEXT = S_restore.CONSTCONTEXT',
        '$update_warning_pointer_value(S_restore, pupdatewarning.POINTER) = (DEFINED pupdaterestore.VALUE)',
        '~$update_warning_release_safe(S_restore, DEFINED pupdaterestore.VALUE)',
        '$task_nodes(UPDATE_WARNING_RELEASE pupdaterestore) = $instance_roots(pupdatewarning.PENDING)',
        '$task_nodes(UPDATE_WARNING_COMMIT pupdaterestore) = eps',
        '$throwable_marker(UPDATE_WARNING_COMMIT pupdaterestore)',
        'PhpStep: S_restore ~> S_record',
        'S_record.TODO = (UPDATE_WARNING_RELEASE pupdaterestore) :: ptask_tail*',
        'S_record.STORE = S_restore.STORE', 'S_record.EVENTS = S_restore.EVENTS',
        'S_record.ALLOCATIONS = S_restore.ALLOCATIONS',
        '$call_task_valid(S_record, UPDATE_WARNING_RELEASE pupdaterestore)',
        '~$call_task_valid(S_record, UPDATE_WARNING_RELEASE pupdaterestore[.WARNING.LINE = $(pupdatewarning.LINE + 1)])',
        '~$call_task_valid(S_record, UPDATE_WARNING_RELEASE pupdaterestore[.WARNING.NAME = $ptascii("missing")])',
        '~$call_task_valid(S_record, UPDATE_WARNING_RELEASE pupdaterestore[.WARNING.POST = ~pupdatewarning.POST])',
        '~$call_task_valid(S_record, UPDATE_WARNING_RELEASE pupdaterestore[.WARNING.INPUT = PINT 41])',
        'PhpStep: S_record ~> S_raw',
        'S_raw = $update_restore_release(S_record, pupdaterestore, ptask_tail*)',
        'S_raw.STORE[pupdaterestore.CELL] = DEFINED pupdaterestore.VALUE',
        '$update_released_cell(S_raw, pupdaterestore.CELL)',
        '$node_children(S_raw, HCELL pupdaterestore.CELL) = eps',
        'S_released = $drive_steps(S_record, 1)[.COMPLETION = NORMAL]',
        '$call_descriptors_valid(S_released)',
        '$heap_valid($heap_graph(S_released))',
        '$update_restore_record_valid(S_released, pupdaterestore)',
        '$update_restore_commit_count(S_released.TODO, pupdaterestore) = 1',
        '$call_task_valid(S_released, UPDATE_WARNING_COMMIT pupdaterestore)',
        'n_invalid = |S_released.STORE|',
        '~$call_task_valid(S_released, UPDATE_WARNING_COMMIT pupdaterestore[.CELL = n_invalid])',
        '~$call_task_valid(S_released[.TODO = eps], UPDATE_WARNING_COMMIT pupdaterestore)',
        '~$update_released_cell(S_released[.TODO = eps][.FRAMES = eps], pupdaterestore.CELL)',
        '$drive_steps(S_record, 0) = S_record[.COMPLETION = BUDGET]',
    ]
    if name == 'review-destructor-late-property-source':
        return checks + [
            'S_finish = $restore_seek(S_released, 2, 3000)[.COMPLETION = NORMAL]',
            'S_finish.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_finish) :: (UPDATE_WARNING_COMMIT pupdaterestore) :: ptask_tail*',
            '$call_descriptors_valid(S_finish)',
            '$update_restore_record_valid(S_finish, pupdaterestore)',
            'pupdatewarning.POINTER = UPDATE_CELL pupdaterestore.CELL',
            '$propref_at(S_finish.PROPREFS, pupdaterestore.CELL) =/= eps',
            'S_finish.STORE[pupdaterestore.CELL] = DEFINED (PINT 7)',
            '~$update_restore_unconstrained(S_finish, pupdaterestore)',
            'PhpStep: S_finish ~> S_failure',
            'S_failure.COMPLETION = UNSUPPORTED "increment/decrement restoration target is expired or constrained"',
            'S_failure.STORE = S_finish.STORE', 'S_failure.EVENTS = S_finish.EVENTS',
            'S_closed = $drive_steps(S_finish, 1)',
            'S_closed.COMPLETION = UNSUPPORTED "increment/decrement restoration target is expired or constrained"',
        ]
    if name == 'review-destructor-exit-bool':
        return checks + [
            'S_pending = $restore_seek(S_released, 4, 3000)[.COMPLETION = NORMAL]',
            '$restore_frontier(S_pending, 4)', '$call_descriptors_valid(S_pending)',
            'PhpStep: S_pending ~> S_exit',
            'S_exit.COMPLETION = EXITED 0',
            '$update_warning_exit_pending(S_exit)',
            '~$update_warning_exit_pending(S_exit[.TODO = eps][.FRAMES = eps])',
            'S_global = $global_table_view(S_exit)',
            '$lookup(S_global.ENV, $ptascii("x")) = (pupdaterestore.CELL)',
            'S_exit.STORE[pupdaterestore.CELL] = DEFINED pupdaterestore.VALUE',
            'S_failure = $exit_start_unwind(S_exit, 0)',
            'S_failure.COMPLETION = UNSUPPORTED "increment/decrement warning exit continuation"',
            'S_failure.STORE = S_exit.STORE', 'S_failure.EVENTS = S_exit.EVENTS',
            'S_closed = $drive_steps(S_exit, 2500)',
            'S_closed.COMPLETION = UNSUPPORTED "increment/decrement warning exit continuation"',
        ]
    if name == 'pre-inc-plain-object-handler-throw':
        checks += [
            '~$destructor_operational(S_released)',
            'pupdatewarning.PENDING = (n_first)',
            'S_released.TODO = (THROW_SEARCH n_first) :: (UPDATE_WARNING_COMMIT pupdaterestore) :: ptask_tail*',
            '$destructor_operation_for(S_released) = eps',
            '$heap_owners($heap_prune($heap_graph(S_released)), HOBJECT n_first) = 2',
            'PhpStep: S_released ~> S_commit',
            'S_commit.TODO = (UPDATE_WARNING_DONE pupdatewarning) :: ptask_tail*',
            'S_commit.STORE[pupdaterestore.CELL] = DEFINED (PBOOL true)',
        ]
    else:
        checks += [
            '$destructor_operation_for(S_released) = (pdestructionoperation)',
            'pdestructionoperation.SOURCE = UPDATE_WARNING_RELEASE pupdaterestore',
            'pdestructionoperation.PENDING = pupdatewarning.PENDING',
            'pdestructionoperation.VALUE = KNOWN PNULL',
            'pdestructionoperation.BASE = BASE_VALUE (KNOWN PNULL)',
            '$eager_operation_source_guard(S_released, pdestructionoperation)',
            '~$eager_operation_source_guard(S_released, pdestructionoperation[.ORIGIN = eps])',
            '~$eager_operation_source_guard(S_released, pdestructionoperation[.SOURCE = UPDATE_WARNING_RELEASE pupdaterestore[.CELL = n_invalid]])',
            '~$call_task_valid(S_released[.TODO = (UPDATE_WARNING_COMMIT pupdaterestore) :: S_released.TODO], UPDATE_WARNING_COMMIT pupdaterestore)',
            'S_enter = $restore_seek(S_released, 1, 3000)[.COMPLETION = NORMAL]',
            '$restore_frontier(S_enter, 1)', '$call_descriptors_valid(S_enter)',
            'S_enter.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_enter*',
            'pdestructorcall.OPERATION = (pdestructionoperation)',
            'S_enter.STORE[pupdaterestore.CELL] = DEFINED pupdaterestore.VALUE',
            '$update_released_cell(S_enter, pupdaterestore.CELL)',
            '$task_nodes(UPDATE_WARNING_COMMIT pupdaterestore) = eps',
            'S_finish = $restore_seek(S_enter, 2, 3000)[.COMPLETION = NORMAL]',
            '$restore_frontier(S_finish, 2)', '$call_descriptors_valid(S_finish)',
            'S_finish.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_finish) :: (UPDATE_WARNING_COMMIT pupdaterestore) :: ptask_tail*',
            'pdestructionoperation_finish.SOURCE = UPDATE_WARNING_RELEASE pupdaterestore',
            '$destructor_operation_valid(S_finish, pdestructionoperation_finish)',
            'PhpStep: S_finish ~> S_commit',
            'S_commit.TODO = (UPDATE_WARNING_DONE pupdatewarning_done) :: ptask_tail*',
            'pupdatewarning_done = pupdatewarning[.PENDING = pdestructionoperation_finish.PENDING]',
            '$update_warning_after(pupdatewarning.OP, pupdatewarning.INPUT) = (pvalue_after)',
            'S_commit.STORE[pupdaterestore.CELL] = DEFINED pvalue_after',
            '$task_nodes(UPDATE_WARNING_DONE pupdatewarning_done) = $instance_roots(pdestructionoperation_finish.PENDING)',
            'S_commit.COMPLETION = NORMAL',
            'S_commit.EVENTS = S_finish.EVENTS',
            '$heap_valid($heap_graph(S_commit))',
            '$drive_steps(S_finish, 1) = ' + update_runner.transitioned('S_finish', 'S_commit') + '[.COMPLETION = BUDGET]',
            'S_budget = $drive_steps(S_finish, 1)', 'S_budget.COMPLETION = BUDGET',
        ]
        if name in ('pre-dec-object-null-handler-throw', 'pre-inc-object-both-throw-bool'):
            checks += [
                'pupdatewarning.PENDING = (n_first)',
                '$heap_owners($heap_prune($heap_graph(S_record)), HOBJECT n_first) = 2',
                '$heap_owners($heap_prune($heap_graph(S_released)), HOBJECT n_first) = 2',
                '$task_nodes(UPDATE_WARNING_COMMIT pupdaterestore) = eps',
            ]
        if name == 'pre-inc-object-both-throw-bool':
            checks += [
                '$lookup(S_finish.ENV, $ptascii("second")) = (n_second_cell)',
                'S_finish.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
                'pdestructionoperation_finish.PENDING = (n_second)',
                'n_second =/= n_first',
                '$throwable_previous_id(S_finish, n_second) = (n_first)',
                '$heap_owners($heap_prune($heap_graph(S_commit)), HOBJECT n_second) = 2',
                '$heap_owners($heap_prune($heap_graph(S_commit)), HOBJECT n_first) = 2',
            ]
        if name == 'post-inc-object-write-bool':
            checks += ['S_finish.STORE[pupdaterestore.CELL] = DEFINED (PINT 99)']
        if name == 'pre-inc-object-retained-reference':
            checks += [
                'pupdatewarning.POINTER = UPDATE_CELL pupdaterestore.CELL',
                'pupdaterestore.WRAPPER = eps',
                '$lookup(S_released.ENV, $ptascii("keep")) = (pupdaterestore.CELL)',
                '$heap_owners($heap_prune($heap_graph(S_released)), HCELL pupdaterestore.CELL) = 2',
            ]
        if name == 'pre-inc-unique-wrapper-string':
            checks += [
                'pupdaterestore.WRAPPER = (n_wrapper)',
                'pupdaterestore.CELL = |S_record.STORE|',
                '$lookup(S_record.ENV, $ptascii("x")) = (n_wrapper)',
                '$lookup(S_released.ENV, $ptascii("x")) = (pupdaterestore.CELL)',
                '~(pupdaterestore.CELL <- S_released.REFCELLS)',
                '$heap_owners($heap_prune($heap_graph(S_record)), HCELL n_wrapper) = 1',
                '~((HCELL n_wrapper) <- S_enter.ALLOCATIONS)',
            ]
        if name == 'pre-inc-array-ordered-throw':
            checks += [
                'pupdaterestore.VALUE = PARRAY n_array',
                '$heap_owners($heap_prune($heap_graph(S_record)), HARRAY n_array) = 1',
                '~((HARRAY n_array) <- S_enter.ALLOCATIONS)',
                'S_compare = $restore_seek(S_enter, 3, 3000)[.COMPLETION = NORMAL]',
                '$update_raw_identity_plan(S_compare) = (false)',
                '$call_descriptors_valid(S_compare)',
                '~((HARRAY n_array) <- $machine_roots(S_compare))',
                'S_compare.ORIGIN = (porigin_compare)',
                '$origin_child((porigin_compare), [PCFIELD 0]) = (porigin_left)',
                '$origin_child((porigin_compare), [PCFIELD 1]) = (porigin_right)',
                '$update_raw_identity_side(S_compare, porigin_left, porigin_right)',
                '~$update_raw_identity_side(S_compare[.CODE = eps], porigin_left, porigin_right)',
                '$update_raw_identity_plan(S_compare[.ORIGIN = eps]) = eps',
                'PhpStep: S_compare ~> S_compared',
                'S_compared.RESULT = KNOWN (PBOOL false)',
                'S_compared.ALLOCATIONS = S_compare.ALLOCATIONS',
                '$heap_valid($heap_graph(S_compared))',
                'S_finish.STORE[pupdaterestore.CELL] = DEFINED (PINT 99)',
                '$lookup(S_finish.ENV, $ptascii("second")) = (n_second_cell)',
                'S_finish.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
                'pdestructionoperation_finish.PENDING = (n_second)',
            ]
        if name == 'review-destructor-resurrection':
            checks += [
                'pupdaterestore.VALUE = POBJECT n_object',
                '$lookup(S_finish.ENV, $ptascii("escaped")) = (n_escaped)',
                'S_finish.STORE[n_escaped] = DEFINED (POBJECT n_object)',
                '(HOBJECT n_object) <- S_finish.ALLOCATIONS',
                'n_object <- S_finish.DESTRUCTION.CALLED',
            ]
    checks += [
        'S_done = $drive_steps(S_commit, 3000)', 'S_done.COMPLETION = NORMAL',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        'S_done.FRAMES = eps', 'S_done.HELD = eps', '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
    ]
    if name != 'pre-inc-plain-object-handler-throw':
        checks += ['$drive_steps(S_budget[.COMPLETION = NORMAL], 3000) = S_done']
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path)
    args, _ = parser.parse_known_args()
    out = args.output
    if out is None:
        out = Path(tempfile.mkdtemp(prefix='incdec-restoration-protocol-', dir=ROOT / '.tools'))
        sys.argv += ['--output', str(out)]
    watched = [Path(__file__), Path(runner.__file__), Path(update_runner.__file__),
               Path(cases.__file__), Path(review_cases.__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    runner.CASES, runner.HELPERS, runner.conditions = CASES, HELPERS, conditions
    runner.sources = cases
    runner.sources.CASES = {**cases.CASES, **review_cases.CASES}
    runner.__file__ = __file__
    passed = runner.main()
    assert before == {str(path): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = json.loads((out / 'report.json').read_bytes())
    report['helper_inputs'], report['revision'] = before, revision
    for row in report['rows']:
        row['boundary_control'] = row['id'] in ('review-destructor-late-property-source', 'review-destructor-exit-bool')
        if 'model' in row:
            result = row['model']
            row['passed'] = (row['passed'] and result['interruption'] is None and result['group_after'] == []
                             and (out / (row['id'] + '-model.stdout')).read_bytes() == b'true\n')
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed and all(row.get('passed', True) for row in report['rows'])


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
