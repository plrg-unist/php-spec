#!/usr/bin/env python3
"""Reached failure uses live types and preserves original target/RHS identities."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import delayed_type_failure_review_cases as cases
import delayed_type_failure_protocol as shared

REVIEW_HELPERS = r'''
dec $delayed_failure_review_diagnostic(pevent, text) : nat
def $delayed_failure_review_diagnostic(DIAGNOSTIC text n* z, text) = 1
def $delayed_failure_review_diagnostic(DIAGNOSTIC_SOURCE n_source text n* z, text) = 1
def $delayed_failure_review_diagnostic(DIAGNOSTIC_STACK text n* z n_trace*, text) = 1
def $delayed_failure_review_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n* z n_trace*, text) = 1
def $delayed_failure_review_diagnostic(pevent, text) = 0 -- otherwise
dec $delayed_failure_review_diagnostics(pevent*, text) : nat
def $delayed_failure_review_diagnostics(eps, text) = 0
def $delayed_failure_review_diagnostics(pevent :: pevent_tail*, text) = $($delayed_failure_review_diagnostic(pevent, text) + $delayed_failure_review_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    family, tag, operation, value_left, labels, array = {
        'delayed-type-failure-xor-string-default': ('bitassign', 'BIT_ASSIGN_BOTH_LEFT', 'BITXOR', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))', 'string ^ string', False),
        'delayed-type-failure-mod-array-default': ('modassign', 'MOD_ASSIGN_BOTH_LEFT', 'MODULO', 'PNULL', 'null % array', True),
        'delayed-type-failure-shift-array-default': ('shiftassign', 'SHIFT_ASSIGN_BOTH_LEFT', 'SHIFTRIGHT', 'PBOOL false', 'bool >> array', True),
    }[name]
    task = lambda stage: f'{tag} pintegeroperation n_target n_right n_bits_left i_left {stage}'
    frontier = f'${family}_both_frontier'
    seek = f'${family}_both_seek'
    operands = '$bothassign_type_failure_operands'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        f'S_found = {seek}(S_initial, 1, 4000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', f'{frontier}(S, 1)',
        'S.TODO = (' + task(0) + ') :: ptask_tail*',
        'n_bits_left = 4623226492472524800', 'i_left = 12',
        'pintegeroperation.OP = ' + operation, '~pintegeroperation.SWAPPED',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LINE = 25', 'S.ORIGIN = (pintegeroperation.SITE)',
        '$lookup(S.ENV, $ptascii("left")) = (n_target)', '$lookup(S.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S.ENV, $ptascii("v")) = (n_v)', '$lookup(S.ENV, $ptascii("calls")) = (n_calls)',
        'S.STORE[n_target] = DEFINED (PFLOAT n_bits_left)',
        'S.STORE[n_right] = DEFINED (PFLOAT 4620974692658839552)',
        'S.STORE[n_v] = DEFINED (PINT 100)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        '~(n_target <- S.REFCELLS)', '~(n_right <- S.REFCELLS)',
        '$call_task_valid(S, ' + task(0) + ')',
        operands + '(S, pintegeroperation, n_target, n_right) = eps',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'S_first_budget = $drive_steps(S, 1)', 'S_first_budget.COMPLETION = BUDGET',
        'S_first = S_first_budget[.COMPLETION = NORMAL]', f'{frontier}(S_first, 2)',
        'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + task(1), 'perrorcall.TARGET = eps',
        'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = $ptascii("Implicit conversion from float 12.5 to int loses precision")',
        '$error_call_valid(S_first, perrorcall)',
        f'S_entered_found = {seek}(S_first, 3, 4000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', f'${family}_both_entered(S_entered.FRAMES, 0)',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
        f'S_return_found = {seek}(S_entered, 4, 4000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', f'{frontier}(S_return, 4)',
        'S_return.TODO = (' + task(1) + ') :: ptask_tail*',
        'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
        'S_return.STORE[n_target] = DEFINED pvalue_left', 'pvalue_left = ' + value_left,
        'S_return.STORE[n_right] = DEFINED pvalue_right',
        'S_return.STORE[n_v] = DEFINED (PINT 100)', 'S_return.STORE[n_calls] = DEFINED (PINT 1)',
        '$lookup(S_return.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S_return.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_return.ENV, $ptascii("alias")) = (n_target)',
        'n_target <- S_return.REFCELLS', '~(n_right <- S_return.REFCELLS)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_target) = 2',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 1',
        '$call_task_valid(S_return, ' + task(1) + ')', '~$call_task_valid(S_return, ' + task(0) + ')',
        '$powerassign_warning_ready(S_return, pintegeroperation, n_target)',
        '$delayed_failure_review_diagnostics(S_return.EVENTS, "Deprecated") = 1',
        '$delayed_failure_review_diagnostics(S_return.EVENTS, "Warning") = 0',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
    ]
    if array:
        checks += [
            'pvalue_right = PARRAY n_array', 'parray_right = S_return.ARRAYS[n_array]',
            '(HARRAY n_array) <- S_return.ALLOCATIONS',
            '$entry_lookup(parray_right.ITEMS, KINT 0) = (DIRECT (PINT 3))',
            '$heap_count(HARRAY n_array, $pools_nodes(S_return.POOLS)) = 1',
            '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_array) = 2',
        ]
    else:
        checks += [
            'pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("xyz"))',
            '$string_carrier_valid(S_return, pvalue_left)', '$string_carrier_valid(S_return, pvalue_right)',
            '$string_long($ptascii("xyz")) = STRINTERROR',
        ]
    checks += [
        operands + '(S_return, pintegeroperation, n_target, n_right) = ((pvalue_left, pvalue_right))',
        '$bothassign_rhs_rejected(S_return, pvalue_right)',
        '$modassign_both_right_snapshot(S_return, pintegeroperation, n_target, n_right) = eps',
        '$bothassign_quiet_string_snapshot(S_return, pintegeroperation, n_target, n_right) = eps',
        '$bothassign_leading_string_snapshot(S_return, pintegeroperation, n_target, n_right) = eps',
        operands + '(S_return[.REFCELLS = S_return.REFCELLS ++ [n_right]], pintegeroperation, n_target, n_right) = eps',
        operands + '(S_return, pintegeroperation, n_v, n_right) = eps',
        operands + '(S_return, pintegeroperation, n_target, n_v) = eps',
        operands + '(S_return[.STORE[n_right] = DEFINED PUNDEFINED], pintegeroperation, n_target, n_right) = eps',
        '~$bothassign_rhs_rejected(S_return, PARRAY (|S_return.ARRAYS|))',
        'S_error_budget = $drive_steps(S_return, 1)', 'S_error_budget.COMPLETION = BUDGET',
        'S_error = S_error_budget[.COMPLETION = NORMAL]', f'{frontier}(S_error, 10)',
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*', f'~${family}_both_tasks(S_error.TODO)',
        'S_error.CURRENT = eps', 'S_error.FRAMES = eps', 'S_error.RESULT = KNOWN PNULL',
        'n_error = |S_return.OBJECTS|', 'S_error.OBJECTS[n_error] = THROWABLE pthrowable',
        'S_error.OBJECTS = S_return.OBJECTS ++ [THROWABLE pthrowable]',
        'pthrowable.KIND = "TypeError"', 'pthrowable.ORIGIN = (pintegeroperation.SITE)',
        '$throwable_field(S_error, n_error, "line") = PINT 25',
        '$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii(' + json.dumps('Unsupported operand types: ' + labels) + '))',
        '$throwable_previous_id(S_error, n_error) = eps', '$throwable_live(S_error, n_error)',
        '$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]',
        '$heap_owners($heap_prune($heap_graph(S_error)), HOBJECT n_error) = 1',
        'S_error.STORE = S_return.STORE', 'S_error.ENV = S_return.ENV',
        'S_error.REFCELLS = S_return.REFCELLS', 'S_error.EVENTS = S_return.EVENTS',
        'S_error.STRINGDATA = S_return.STRINGDATA',
        'S_error.ARRAYS[0:|S_return.ARRAYS|] = S_return.ARRAYS',
        '$heap_owners($heap_prune($heap_graph(S_error)), HCELL n_target) = 2',
        '$heap_owners($heap_prune($heap_graph(S_error)), HCELL n_right) = 1',
        '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
    ]
    if array:
        checks += [
            'S_error.STORE[n_right] = DEFINED (PARRAY n_array)',
            'S_error.ARRAYS[n_array] = parray_right',
            '$heap_owners($heap_prune($heap_graph(S_error)), HARRAY n_array) = 2',
        ]
    checks += [
        'S_done = $drive_steps(S_error, 4000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S_done.ENV, $ptascii("alias")) = (n_target)',
        '$lookup(S_done.ENV, $ptascii("right")) = (n_right)',
        'S_done.STORE[n_target] = DEFINED (PINT 7)', 'S_done.STORE[n_right] = DEFINED pvalue_right',
        'S_done.STORE[n_v] = DEFINED (PINT 100)', 'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        '$delayed_failure_review_diagnostics(S_done.EVENTS, "Deprecated") = 1',
        '$delayed_failure_review_diagnostics(S_done.EVENTS, "Warning") = 0',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]', '$drive_steps(S, 6000) = S_done',
        '$drive_steps(S_first, 6000) = S_done', '$drive_steps(S_entered, 6000) = S_done',
        '$drive_steps(S_return, 6000) = S_done',
    ]
    if array:
        checks += [
            'S_done.ARRAYS[n_array] = parray_right',
            '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_array) = 2',
        ]
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path, required=True)
    args, _ = parser.parse_known_args()
    watched = [Path(__file__), Path(shared.__file__), Path(cases.__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    shared.cases, shared.CASES, shared.conditions = cases, tuple(cases.CASES), conditions
    shared.HELPERS += REVIEW_HELPERS
    passed = shared.main()
    assert before == {str(path): digest(path) for path in watched}
    report = json.loads((args.output / 'report.json').read_bytes())
    report['review_inputs'] = before
    report['review_scope'] = 'Actual first default deprecation then direct TypeError25 from live string/string, NULL/array and bool/array; numeric bitwise specialization is not retried, original target/RHS cells and array identities/owners survive without store/detachment, exact atomic metadata and whole/budget equality'
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
