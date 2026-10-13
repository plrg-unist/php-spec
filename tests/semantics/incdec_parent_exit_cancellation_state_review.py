#!/usr/bin/env python3
"""Independent source-reached retired operand and finally-outcome checks."""
import base64
import hashlib
import json
from pathlib import Path

import incdec_parent_exit_cancellation_review_cases as cases
import incdec_parent_exit_cancellation_protocol as protocol
import incdec_warning_protocol as update_protocol

CASES = ('review-parent-exit-two-retired', 'review-parent-exit-alias-retirement',
         'review-parent-exit-finally-pending')
HELPERS = protocol.HELPERS + r'''
dec $review_parent_pending_head(ptask, nat) : bool
def $review_parent_pending_head(FINALLY_RESUME porigin (n), n) = true
def $review_parent_pending_head(ptask, n) = false -- otherwise
dec $review_parent_pending_finally(ptask*, nat) : bool
def $review_parent_pending_finally(eps, n) = false
def $review_parent_pending_finally(ptask :: ptask_tail*, n) = true -- if $review_parent_pending_head(ptask, n)
def $review_parent_pending_finally(ptask :: ptask_tail*, n) = $review_parent_pending_finally(ptask_tail*, n) -- if ~$review_parent_pending_head(ptask, n)
dec $review_parent_finally_head(ptask*) : bool
def $review_parent_finally_head((FINALLY_RESUME porigin eps) :: (FINALLY_PHASE porigin 0) :: ptask*) = true
def $review_parent_finally_head(ptask*) = false -- otherwise
dec $review_parent_first_finally(ptask*) : porigin?
def $review_parent_first_finally(eps) = eps
def $review_parent_first_finally((FINALLY_RESUME porigin eps) :: (FINALLY_PHASE porigin 0) :: ptask*) = (porigin)
def $review_parent_first_finally(ptask :: ptask_tail*) = $review_parent_first_finally(ptask_tail*) -- if ~$review_parent_finally_head(ptask :: ptask_tail*)
dec $review_parent_try_head(ptask) : bool
def $review_parent_try_head(TRY_END porigin) = true
def $review_parent_try_head(ptask) = false -- otherwise
dec $review_parent_replace_try(ptask*, porigin) : ptask*
def $review_parent_replace_try(eps, porigin) = eps
def $review_parent_replace_try((TRY_END porigin_old) :: ptask*, porigin) = (TRY_END porigin) :: ptask*
def $review_parent_replace_try(ptask :: ptask_tail*, porigin) = ptask :: $review_parent_replace_try(ptask_tail*, porigin) -- if ~$review_parent_try_head(ptask)
'''


def conditions(name, program, path, stdout):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_begin = $update_seek(S_initial, 0, 2500)[.COMPLETION = NORMAL]',
        '$update_warning_plan(S_begin) = (pupdatewarning)',
        'pupdatewarning.INPUT = PBOOL true',
        'S_boundary = $update_exit_seek(S_begin, 1, 2500)[.COMPLETION = NORMAL]',
        'S_boundary.TODO = (UPDATE_WARNING_EXIT perrorcall 0) :: ptask_caller*',
        'perrorcall.RESUME = UPDATE_WARNING_RESTORE pupdatewarning',
        '$call_descriptors_valid(S_boundary)',
        'S_entry = $parent_exit_seek(S_boundary, 0, 2500)[.COMPLETION = NORMAL]',
        'S_entry.TODO = (DESTRUCTOR_ENTER pdestructorcall_entry) :: ptask_entry*',
        'pdestructorcall_entry.OPERATION = (pdestructionoperation)',
        'pdestructionoperation.SOURCE = UPDATE_WARNING_EXIT_HISTORY perrorcall 0 ptask_history*',
        '$tasks_nodes(ptask_history*) = eps',
        '$task_nodes(pdestructionoperation.SOURCE) = eps',
        '$update_exit_history(S_boundary, perrorcall.SITE) = GOTOTASKS ptask_history*',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
    ]
    if name == 'review-parent-exit-two-retired':
        checks += [
            'n_first = pdestructorcall_entry.OBJECT',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HOBJECT n_first) = 2',
            'S_after_enter = $drive_steps(S_entry, 1)[.COMPLETION = NORMAL]',
            'S_enter = $parent_exit_seek(S_after_enter, 0, 2500)[.COMPLETION = NORMAL]',
            'S_enter.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_release*',
            'n_parent = pdestructorcall.OBJECT', 'n_parent =/= n_first',
            'pdestructorcall.OPERATION = (pdestructionoperation)',
            '$heap_owners($heap_prune($heap_graph(S_enter)), HOBJECT n_first) = 0',
            '~((HOBJECT n_first) <- S_enter.ALLOCATIONS)',
            '$lookup(S_enter.ENV, $ptascii("wa")) = (n_wa_cell)',
            'S_enter.STORE[n_wa_cell] = DEFINED (POBJECT n_wa)',
            '$weakref_get(S_enter, n_wa) = PNULL',
            '$lookup(S_enter.ENV, $ptascii("x")) = (n_x)',
            'S_enter.STORE[n_x] = DEFINED (PINT 99)',
        ]
    else:
        checks += [
            'S_enter = S_entry', 'pdestructorcall = pdestructorcall_entry',
            'S_enter.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_release*',
            'n_parent = pdestructorcall.OBJECT',
        ]
    checks += [
        'pdestructionoperation.PENDING = eps',
        '$heap_owners($heap_prune($heap_graph(S_enter)), HOBJECT n_parent) = 2',
        '$eager_operation_source_guard(S_enter, pdestructionoperation)',
        '$destructor_enter_valid(S_enter, pdestructorcall)',
        '$call_descriptors_valid(S_enter)',
        'S_throw = $parent_exit_seek(S_enter, 1, 2500)[.COMPLETION = NORMAL]',
        'S_throw.TODO = (THROW_SEARCH n_second) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_release*',
        '$destructor_result_valid(S_throw, pdestructorcall)',
        '$throwable_marker(DESTRUCTOR_RESULT pdestructorcall)',
        '$eager_bailout_source(S_throw) = eps',
        '~$exception_terminal_tail(S_throw, (DESTRUCTOR_RESULT pdestructorcall) :: ptask_release*)',
        '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
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
        '~$eager_operation_source_guard(S_throw, pdestructionoperation[.SOURCE = UPDATE_WARNING_EXIT_HISTORY perrorcall 0 ptask_swapped*])',
        '~$eager_operation_source_guard(S_throw, pdestructionoperation[.SOURCE = UPDATE_WARNING_EXIT_HISTORY perrorcall 0 eps])',
        '~$eager_operation_source_guard(S_throw, pdestructionoperation[.SOURCE = UPDATE_WARNING_EXIT_HISTORY perrorcall[.LINE = $(perrorcall.LINE + 1)] 0 ptask_history*])',
        '~$eager_operation_source_guard(S_throw[.CODE = eps], pdestructionoperation)',
        'PhpStep: S_throw ~> S_pending',
        'pdestructionoperation_pending = pdestructionoperation[.PENDING = (n_second)]',
        'S_pending.DESTRUCTION.OPERATIONS = pdestructionoperation_pending :: pdestructionoperation_tail*',
        'S_pending.TODO = $destructor_operation_tasks(ptask_release*, pdestructionoperation, pdestructionoperation_pending)',
        'S_pending.DESTRUCTION.CALLS = eps',
        'S_pending.STORE = S_throw.STORE', 'S_pending.EVENTS = S_throw.EVENTS',
        '$heap_owners($heap_prune($heap_graph(S_pending)), HOBJECT n_second) = 2',
        '$call_descriptors_valid(S_pending)',
        'S_finish = $parent_exit_seek(S_pending, 2, 2500)[.COMPLETION = NORMAL]',
        'S_finish.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending) :: ptask_exit*',
        '$destructor_operation_valid(S_finish, pdestructionoperation_pending)',
        '$call_descriptors_valid(S_finish)', '$heap_valid($heap_graph(S_finish))',
        '$heap_owners($heap_prune($heap_graph(S_finish)), HOBJECT n_parent) = 0',
        '~((HOBJECT n_parent) <- S_finish.ALLOCATIONS)',
        'PhpStep: S_finish ~> S_restore',
        'S_restore.TODO = (THROW_SEARCH n_second) :: ptask_history*',
        'S_restore.ORIGIN = eps', 'S_restore.RESULT = KNOWN PNULL',
        'S_restore.BASE = BASE_VALUE (KNOWN PNULL)', 'S_restore.COMPLETION = NORMAL',
        'S_restore.DESTRUCTION.OPERATIONS = eps',
        'S_restore.DESTRUCTION.CALLS = eps', 'S_restore.DESTRUCTION.RELEASES = eps',
        'S_restore.CURRENT = S_finish.CURRENT', 'S_restore.FRAMES = S_finish.FRAMES',
        'S_restore.STORE = S_finish.STORE', 'S_restore.EVENTS = S_finish.EVENTS',
        'S_restore.ALLOCATIONS = S_finish.ALLOCATIONS',
        'S_restore.EXITSTATUS = S_finish.EXITSTATUS',
        '$heap_owners($heap_prune($heap_graph(S_restore)), HOBJECT n_second) = 2',
        '$throwable_previous_id(S_restore, n_second) = eps',
        '$call_descriptors_valid(S_restore)', '$heap_valid($heap_graph(S_restore))',
        '$drive_steps(S_finish, 0) = S_finish[.COMPLETION = BUDGET]',
        'S_budget = $drive_steps(S_finish, 1)',
        'S_budget = ' + update_protocol.transitioned('S_finish', 'S_restore') + '[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_restore, 2500)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_budget[.COMPLETION = NORMAL], 2500) = S_done',
    ]
    if name == 'review-parent-exit-two-retired':
        checks += [
            'ptask_caller* = (ORIGIN_RETURN (porigin_inner)) :: (BINARY_RIGHT IDENTICAL poperand_inner z_inner) :: ptask_inner*',
            'ptask_inner* = (ORIGIN_RETURN (porigin_outer)) :: (BINARY_RIGHT IDENTICAL poperand_outer z_outer) :: ptask_outer*',
            'ptask_outer* = (ORIGIN_RETURN (porigin_assign)) :: (WRITE_NAME n_target* z_target) :: ptask_assign*',
            'poperand_inner = KNOWN (POBJECT n_parent)',
            'poperand_outer = KNOWN (POBJECT n_first)',
            '$tasks_nodes(ptask_caller*) = [HOBJECT n_parent, HOBJECT n_first]',
            '$update_exit_order(S_boundary) = UPDATE_EXIT_ORDER ([HOBJECT n_first, HOBJECT n_parent])',
            '$update_exit_order_supported(S_boundary)',
            '$update_exit_owner_reordered(S_boundary)',
            '~$update_exit_order_supported(S_boundary[.ORIGIN = (porigin_inner)])',
            '~$update_exit_order_supported(S_boundary[.CODE = eps])',
            '$update_exit_inputs(S_boundary, perrorcall.SITE, (ORIGIN_RETURN (porigin_inner)) :: (BINARY_RIGHT NOTIDENTICAL poperand_inner z_inner) :: ptask_inner*, ptask_history*) = UPDATE_EXIT_UNORDERED',
            '$update_exit_inputs(S_boundary, perrorcall.SITE, (ORIGIN_RETURN (porigin_inner)) :: (BINARY_RIGHT IDENTICAL poperand_inner $(z_inner + 1)) :: ptask_inner*, ptask_history*) = UPDATE_EXIT_UNORDERED',
            '$update_exit_inputs(S_boundary, perrorcall.SITE, (ORIGIN_RETURN (porigin_inner)) :: (BINARY_RIGHT IDENTICAL (VARIABLE ($ptascii("x")) z_inner) z_inner) :: ptask_inner*, ptask_history*) = UPDATE_EXIT_UNORDERED',
            '$update_exit_inputs(S_boundary, perrorcall.SITE, (BINARY_RIGHT IDENTICAL poperand_inner z_inner) :: ptask_inner*, ptask_history*) = UPDATE_EXIT_UNORDERED',
            '$update_exit_inputs(S_boundary, porigin_outer, (ORIGIN_RETURN (porigin_assign)) :: (WRITE_NAME ($ptascii("not_v")) z_target) :: ptask_assign*, ptask_history*) = UPDATE_EXIT_UNORDERED',
            '$lookup(S_global.ENV, $ptascii("wb")) = (n_wb_cell)',
            'S_throw.STORE[n_wb_cell] = DEFINED (POBJECT n_wb)',
            '$weakref_get(S_throw, n_wb) = POBJECT n_parent',
            '$weakref_get(S_restore, n_wa) = PNULL',
            '$weakref_get(S_restore, n_wb) = PNULL',
            'S_restore.STORE[n_x] = DEFINED (PINT 99)',
            '$heap_owners($heap_prune($heap_graph(S_restore)), HOBJECT n_first) = 0',
            '~((HOBJECT n_first) <- S_restore.ALLOCATIONS)',
        ]
    elif name == 'review-parent-exit-alias-retirement':
        checks += [
            '$lookup(S_enter.ENV, $ptascii("keep")) = (n_keep_cell)',
            'S_enter.STORE[n_keep_cell] = DEFINED (POBJECT n_kept)',
            '$lookup(S_enter.ENV, $ptascii("wk")) = (n_wk_cell)',
            'S_enter.STORE[n_wk_cell] = DEFINED (POBJECT n_wk)',
            '$weakref_get(S_enter, n_wk) = POBJECT n_kept',
            '$heap_owners($heap_prune($heap_graph(S_enter)), HOBJECT n_kept) = 1',
            '$weakref_get(S_throw, n_wk) = PNULL',
            '$weakref_get(S_restore, n_wk) = PNULL',
            '$heap_owners($heap_prune($heap_graph(S_restore)), HOBJECT n_kept) = 0',
            '~((HOBJECT n_kept) <- S_restore.ALLOCATIONS)',
        ]
    else:
        checks += [
            '$lookup(S_global.ENV, $ptascii("first")) = (n_first_cell)',
            'S_boundary.STORE[n_first_cell] = DEFINED (POBJECT n_first)',
            '$review_parent_pending_finally(ptask_caller*, n_first)',
            '$heap_owners($heap_prune($heap_graph(S_boundary)), HOBJECT n_first) = 2',
            '$heap_owners($heap_prune($heap_graph(S_enter)), HOBJECT n_first) = 1',
            '$heap_owners($heap_prune($heap_graph(S_restore)), HOBJECT n_first) = 1',
            '$review_parent_first_finally(ptask_history*) = (porigin_inner)',
            '$update_exit_control(S_boundary, [FINALLY_RESUME porigin_inner (n_first), FINALLY_PHASE porigin_inner 1], [FINALLY_RESUME porigin_inner eps, FINALLY_PHASE porigin_inner 0])',
            '~$update_exit_control(S_boundary, [FINALLY_RESUME porigin_inner (n_first), FINALLY_PHASE porigin_inner 0], [FINALLY_RESUME porigin_inner eps, FINALLY_PHASE porigin_inner 0])',
            '$throwable_try_valid(S_throw, porigin_inner)',
            'ptask_wrong_try* = $review_parent_replace_try(ptask_history*, porigin_inner)',
            'ptask_wrong_try* =/= ptask_history*',
            '$tasks_nodes(ptask_wrong_try*) = eps',
            '~$eager_operation_source_guard(S_throw, pdestructionoperation[.SOURCE = UPDATE_WARNING_EXIT_HISTORY perrorcall 0 ptask_wrong_try*])',
        ]
    return checks


def main():
    own = Path(__file__)
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    protocol.CASES, protocol.HELPERS, protocol.conditions, protocol.cases = CASES, HELPERS, conditions, cases
    passed = protocol.main()
    assert before == hashlib.sha256(own.read_bytes()).hexdigest()
    parser = protocol.argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path)
    args, _ = parser.parse_known_args()
    if args.output is not None:
        report_path = args.output / 'report.json'
        report = json.loads(report_path.read_bytes())
        report['helper_inputs'][str(own)] = before
        report_path.write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
