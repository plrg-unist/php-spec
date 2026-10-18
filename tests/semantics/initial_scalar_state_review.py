#!/usr/bin/env python3
"""New scalar entry defers invalid text and captures a repaired negative mask."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import initial_scalar_review_cases as cases
import initial_scalar_protocol as shared

CASES = ('initial-scalar-bad-xor-default', 'initial-scalar-null-negative-reference-default')
REVIEW_HELPERS = r'''
dec $initial_scalar_review_diagnostic(pevent, text) : nat
def $initial_scalar_review_diagnostic(DIAGNOSTIC text n* z, text) = 1
def $initial_scalar_review_diagnostic(DIAGNOSTIC_SOURCE n_source text n* z, text) = 1
def $initial_scalar_review_diagnostic(DIAGNOSTIC_STACK text n* z n_trace*, text) = 1
def $initial_scalar_review_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n* z n_trace*, text) = 1
def $initial_scalar_review_diagnostic(pevent, text) = 0 -- otherwise
dec $initial_scalar_review_diagnostics(pevent*, text) : nat
def $initial_scalar_review_diagnostics(eps, text) = 0
def $initial_scalar_review_diagnostics(pevent :: pevent_tail*, text) = $($initial_scalar_review_diagnostic(pevent, text) + $initial_scalar_review_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    bad_text = name == CASES[0]
    left = lambda stage: f'BIT_ASSIGN_BOTH_LEFT pintegeroperation n_target n_right n_bits_left i_left {stage}'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_plan_found = $bitassign_both_seek(S_initial, 0, 4000)',
        r'S_plan_found.COMPLETION = NORMAL \/ S_plan_found.COMPLETION = BUDGET',
        'S_plan = S_plan_found[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_plan, 0)',
        '$bitassign_both_warning_plan(S_plan) = (' + left(0) + ')',
        '$bitassign_warning_plan(S_plan) = eps',
        'S_marker_budget = $drive_steps(S_plan, 1)', 'S_marker_budget.COMPLETION = BUDGET',
        'S = S_marker_budget[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S, 1)',
        'S.TODO = (' + left(0) + ') :: ptask_tail*',
        'n_bits_left = 4623226492472524800', 'i_left = 12',
        'pintegeroperation.OP = BITXOR', '~pintegeroperation.SWAPPED',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LINE = 25', 'S.ORIGIN = (pintegeroperation.SITE)',
        '$lookup(S.ENV, $ptascii("left")) = (n_target)', '$lookup(S.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S.ENV, $ptascii("v")) = (n_v)', '$lookup(S.ENV, $ptascii("calls")) = (n_calls)',
        'S.STORE[n_target] = DEFINED (PFLOAT n_bits_left)', 'S.STORE[n_right] = DEFINED pvalue_initial',
        'S.STORE[n_v] = DEFINED (PINT 100)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        '~(n_target <- S.REFCELLS)', '~(n_right <- S.REFCELLS)',
        '$bothassign_initial_right_valid(S, pvalue_initial)',
        '$modassign_both_snapshot(S, pintegeroperation, n_target, n_right, n_bits_left)',
        '~$modassign_warning_snapshot(S, pintegeroperation, n_target, n_right, n_bits_left)',
        '$call_task_valid(S, ' + left(0) + ')',
        '~$call_task_valid(S, BIT_ASSIGN_WARNING pintegeroperation n_target n_right n_bits_left i_left 0)',
        '$task_nodes(' + left(0) + ') = eps',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_right) = 1',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
    ]
    if bad_text:
        checks += [
            'pvalue_initial = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("bad5"))',
            'S.STRINGDATA[n_string] = $ptascii("bad5")', '$string_carrier_valid(S, pvalue_initial)',
            '$string_long($ptascii("bad5")) = STRINTERROR', '$integer_conversion(pvalue_initial) = eps',
        ]
    else:
        checks += ['pvalue_initial = PNULL']
    checks += [
        'S_first_budget = $drive_steps(S, 1)', 'S_first_budget.COMPLETION = BUDGET',
        'S_first = S_first_budget[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_first, 2)',
        'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
        'perrorcall_first.RESUME = ' + left(1), 'perrorcall_first.TARGET = eps',
        'perrorcall_first.LEVEL = 8192', 'perrorcall_first.LINE = 25',
        'perrorcall_first.MESSAGE = $ptascii("Implicit conversion from float 12.5 to int loses precision")',
        '$error_call_valid(S_first, perrorcall_first)',
        'S_entered_found = $bitassign_both_seek(S_first, 3, 4000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', '$bitassign_both_entered(S_entered.FRAMES, 0)',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
        'S_return_found = $bitassign_both_seek(S_entered, 4, 4000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_return, 4)',
        'S_return.TODO = (' + left(1) + ') :: ptask_tail*',
        'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
        '$lookup(S_return.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S_return.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_return.ENV, $ptascii("alias")) = (n_target)',
        'n_target <- S_return.REFCELLS', '~(n_right <- S_return.REFCELLS)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)', 'S_return.STORE[n_calls] = DEFINED (PINT 1)',
        '$call_task_valid(S_return, ' + left(1) + ')', '~$call_task_valid(S_return, ' + left(0) + ')',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_target) = 2',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 1',
        'S_return.STRINGDATA[0:|S.STRINGDATA|] = S.STRINGDATA',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
    ]
    if bad_text:
        checks += [
            'pvalue_left = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))',
            'S_return.STORE[n_target] = DEFINED pvalue_left', 'S_return.STORE[n_right] = DEFINED pvalue_initial',
            '$string_carrier_valid(S_return, pvalue_initial)', 'S_return.STRINGDATA[n_string] = $ptascii("bad5")',
            '$bothassign_type_failure_operands(S_return, pintegeroperation, n_target, n_right) = ((pvalue_left, pvalue_initial))',
            '$initial_scalar_review_diagnostics(S_return.EVENTS, "Deprecated") = 1',
            'S_error_budget = $drive_steps(S_return, 1)', 'S_error_budget.COMPLETION = BUDGET',
            'S_error = S_error_budget[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_error, 10)',
            'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*', 'S_error.RESULT = KNOWN PNULL',
            'n_error = |S_return.OBJECTS|', 'S_error.OBJECTS[n_error] = THROWABLE pthrowable',
            'S_error.OBJECTS = S_return.OBJECTS ++ [THROWABLE pthrowable]',
            'pthrowable.KIND = "TypeError"', 'pthrowable.ORIGIN = (pintegeroperation.SITE)',
            '$throwable_field(S_error, n_error, "line") = PINT 25',
            '$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("Unsupported operand types: string ^ string"))',
            '$throwable_previous_id(S_error, n_error) = eps', '$throwable_live(S_error, n_error)',
            '$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]',
            '$heap_owners($heap_prune($heap_graph(S_error)), HOBJECT n_error) = 1',
            'S_error.STORE = S_return.STORE', 'S_error.ENV = S_return.ENV',
            'S_error.REFCELLS = S_return.REFCELLS', 'S_error.EVENTS = S_return.EVENTS',
            'S_error.STRINGDATA = S_return.STRINGDATA', 'S_error.ARRAYS[0:|S_return.ARRAYS|] = S_return.ARRAYS',
            '$heap_owners($heap_prune($heap_graph(S_error)), HCELL n_target) = 2',
            '$heap_owners($heap_prune($heap_graph(S_error)), HCELL n_right) = 1',
            '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
            'S_done = $drive_steps(S_error, 4000)',
            '$lookup(S_done.ENV, $ptascii("left")) = (n_target)', '$lookup(S_done.ENV, $ptascii("right")) = (n_right)',
            'S_done.STORE[n_target] = DEFINED (PINT 7)', 'S_done.STORE[n_right] = DEFINED pvalue_initial',
            'S_done.STORE[n_v] = DEFINED (PINT 100)', 'S_done.STORE[n_calls] = DEFINED (PINT 1)',
            '$string_carrier_valid(S_done, pvalue_initial)', 'S_done.STRINGDATA[n_string] = $ptascii("bad5")',
        ]
    else:
        right = lambda stage: f'BIT_ASSIGN_BOTH_RIGHT pintegeroperation n_target n_right n_bits_left i_left n_bits_right i_right {stage}'
        checks += [
            'S_return.STORE[n_target] = DEFINED (PINT 99)',
            'S_return.STORE[n_right] = DEFINED (PFLOAT 13832806255468478464)',
            '$initial_scalar_review_diagnostics(S_return.EVENTS, "Deprecated") = 0',
            '$modassign_both_right_snapshot(S_return, pintegeroperation, n_target, n_right) = ((13832806255468478464, (-1)))',
            'S_right_budget = $drive_steps(S_return, 1)', 'S_right_budget.COMPLETION = BUDGET',
            'S_right = S_right_budget[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_right, 5)',
            'S_right.TODO = (' + right(0) + ') :: ptask_tail*',
            'n_bits_right = 13832806255468478464', 'i_right = (-1)',
            '$call_task_valid(S_right, ' + right(0) + ')', '$task_nodes(' + right(0) + ') = eps',
            'S_second_budget = $drive_steps(S_right, 1)', 'S_second_budget.COMPLETION = BUDGET',
            'S_second = S_second_budget[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_second, 6)',
            'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
            'perrorcall_second.RESUME = ' + right(1), 'perrorcall_second.TARGET = eps',
            'perrorcall_second.LEVEL = 8192', 'perrorcall_second.LINE = 25',
            'perrorcall_second.MESSAGE = $ptascii("Implicit conversion from float -1.5 to int loses precision")',
            '$error_call_valid(S_second, perrorcall_second)',
            'S_second_entered_found = $bitassign_both_seek(S_second, 7, 4000)',
            r'S_second_entered_found.COMPLETION = NORMAL \/ S_second_entered_found.COMPLETION = BUDGET',
            'S_second_entered = S_second_entered_found[.COMPLETION = NORMAL]', '$bitassign_both_entered(S_second_entered.FRAMES, 1)',
            'S_late_found = $bitassign_both_seek(S_second_entered, 8, 4000)',
            r'S_late_found.COMPLETION = NORMAL \/ S_late_found.COMPLETION = BUDGET',
            'S_late = S_late_found[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_late, 8)',
            'S_late.TODO = (' + right(1) + ') :: ptask_tail*',
            '$lookup(S_late.ENV, $ptascii("left")) = (n_target)',
            '$lookup(S_late.ENV, $ptascii("alias")) = (n_target)',
            '$lookup(S_late.ENV, $ptascii("right")) = (n_target)',
            'S_late.STORE[n_target] = DEFINED (PINT 88)', 'S_late.STORE[n_calls] = DEFINED (PINT 2)',
            '$call_task_valid(S_late, ' + right(1) + ')', '~$call_task_valid(S_late, ' + right(0) + ')',
            '$heap_owners($heap_prune($heap_graph(S_late)), HCELL n_target) = 3',
            '$powerassign_warning_ready(S_late, pintegeroperation, n_target)',
            '$integer_binary(pintegeroperation.OP, i_left, i_right) = IRESULT (-13)',
            'S_commit_budget = $drive_steps(S_late, 1)', 'S_commit_budget.COMPLETION = BUDGET',
            'S_commit = S_commit_budget[.COMPLETION = NORMAL]', '$bitassign_both_frontier(S_commit, 9)',
            'S_commit.TODO = ptask_tail*', 'S_commit.RESULT = KNOWN (PINT (-13))',
            '$lookup(S_commit.ENV, $ptascii("left")) = (n_new)', 'n_new = |S_late.STORE|',
            'S_commit.CELL = n_new', 'S_commit.LOCATION = ROOT n_new', '~(n_new <- S_commit.REFCELLS)',
            '$lookup(S_commit.ENV, $ptascii("alias")) = (n_target)', '$lookup(S_commit.ENV, $ptascii("right")) = (n_target)',
            'S_commit.STORE = S_late.STORE ++ [DEFINED (PINT (-13))]',
            'S_commit.ALLOCATIONS = S_late.ALLOCATIONS ++ [HCELL n_new]',
            'S_commit.REFCELLS = S_late.REFCELLS', 'S_commit.EVENTS = S_late.EVENTS',
            'S_commit.STRINGDATA = S_late.STRINGDATA', 'S_commit.ARRAYS = S_late.ARRAYS',
            '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_target) = 2',
            '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_new) = 1',
            '$call_descriptors_valid(S_commit)', '$heap_valid($heap_graph(S_commit))',
            'S_done = $drive_steps(S_commit, 4000)',
            '$lookup(S_done.ENV, $ptascii("left")) = (n_new)', '$lookup(S_done.ENV, $ptascii("right")) = (n_target)',
            'S_done.STORE[n_new] = DEFINED (PINT 7)', 'S_done.STORE[n_target] = DEFINED (PINT 6)',
            'S_done.STORE[n_v] = DEFINED (PINT (-13))', 'S_done.STORE[n_calls] = DEFINED (PINT 2)',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("alias")) = (n_target)',
        '$initial_scalar_review_diagnostics(S_done.EVENTS, "Deprecated") = 1',
        '$initial_scalar_review_diagnostics(S_done.EVENTS, "Warning") = 0',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]', '$drive_steps(S_plan, 5000) = S_done',
        '$drive_steps(S, 5000) = S_done', '$drive_steps(S_first, 5000) = S_done',
        '$drive_steps(S_return, 5000) = S_done',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path, required=True)
    args, _ = parser.parse_known_args()
    watched = [Path(__file__), Path(shared.__file__), Path(cases.__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    shared.cases, shared.CASES, shared.conditions = cases, CASES, conditions
    shared.HELPERS += REVIEW_HELPERS
    passed = shared.main()
    assert before == {str(path): digest(path) for path in watched}
    report = json.loads((args.output / 'report.json').read_bytes())
    report['review_inputs'] = before
    report['review_scope'] = 'Actual new non-PINT scalar entry selects BOTH0 while single0 refuses: invalid request text reaches LEFT handler before live string^string TypeError/no-store, or initial NULL is repaired to a negative float whose cached XOR survives RHS reference rebinding and detaches owners3 to2; source-only first supplied throw is not repeated; exact atomic storage/metadata, original bindings/owners and whole/resumed budgets'
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
