#!/usr/bin/env python3
"""Reached leading-string caches survive RHS rebinding, unset and zero errors."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import leading_string_review_cases as cases
import leading_string_protocol as shared

REVIEW_HELPERS = r'''
dec $leading_string_review_diagnostic(pevent, text) : nat
def $leading_string_review_diagnostic(DIAGNOSTIC text n* z, text) = 1
def $leading_string_review_diagnostic(DIAGNOSTIC_SOURCE n_source text n* z, text) = 1
def $leading_string_review_diagnostic(DIAGNOSTIC_STACK text n* z n_trace*, text) = 1
def $leading_string_review_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n* z n_trace*, text) = 1
def $leading_string_review_diagnostic(pevent, text) = 0 -- otherwise
dec $leading_string_review_diagnostics(pevent*, text) : nat
def $leading_string_review_diagnostics(eps, text) = 0
def $leading_string_review_diagnostics(pevent :: pevent_tail*, text) = $($leading_string_review_diagnostic(pevent, text) + $leading_string_review_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    tag, operation, text, number, error_kind, error_message = {
        'leading-string-xor-reference-default': ('BIT_ASSIGN_BOTH_LEFT', 'BITXOR', '-1tail', '(-1)', None, None),
        'leading-string-shift-unset-default': ('SHIFT_ASSIGN_BOTH_LEFT', 'SHIFTRIGHT', '-1tail', '(-1)', 'ArithmeticError', 'Bit shift by negative number'),
        'leading-string-mod-zero-default': ('MOD_ASSIGN_BOTH_LEFT', 'MODULO', '0tail', '0', 'DivisionByZeroError', 'Modulo by zero'),
    }[name]
    xor = error_kind is None
    unset = error_kind == 'ArithmeticError'
    saved = 'PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(text) + '))'
    left = lambda stage: f'{tag} pintegeroperation n_target n_right n_bits_left i_left {stage}'
    marker = lambda stage, value='pvalue_saved', integer='i_right': f'BOTH_ASSIGN_STRING_WARNING pintegeroperation n_target n_right n_bits_left i_left ({value}) {integer} {stage}'
    snapshot = '$bothassign_leading_string_snapshot'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $leading_string_seek(S_initial, 1, 4000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$leading_string_frontier(S, 1)',
        'S.TODO = (' + left(0) + ') :: ptask_tail*',
        'n_bits_left = 4623226492472524800', 'i_left = 12',
        'pintegeroperation.OP = ' + operation, '~pintegeroperation.SWAPPED',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LINE = 25', 'S.ORIGIN = (pintegeroperation.SITE)',
        '$lookup(S.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S.ENV, $ptascii("calls")) = (n_calls)',
        'S.STORE[n_target] = DEFINED (PFLOAT n_bits_left)',
        'S.STORE[n_right] = DEFINED (PFLOAT 4620974692658839552)',
        'S.STORE[n_v] = DEFINED (PINT 100)', 'S.STORE[n_calls] = DEFINED (PINT 0)',
        '~(n_target <- S.REFCELLS)', '~(n_right <- S.REFCELLS)',
        '$call_task_valid(S, ' + left(0) + ')',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'S_first_budget = $drive_steps(S, 1)', 'S_first_budget.COMPLETION = BUDGET',
        'S_first = S_first_budget[.COMPLETION = NORMAL]', '$leading_string_frontier(S_first, 2)',
        'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
        'perrorcall_first.RESUME = ' + left(1), 'perrorcall_first.TARGET = eps',
        'perrorcall_first.LEVEL = 8192', 'perrorcall_first.LINE = 25',
        'perrorcall_first.MESSAGE = $ptascii("Implicit conversion from float 12.5 to int loses precision")',
        '$error_call_valid(S_first, perrorcall_first)',
        'S_first_entered_found = $leading_string_seek(S_first, 3, 4000)',
        r'S_first_entered_found.COMPLETION = NORMAL \/ S_first_entered_found.COMPLETION = BUDGET',
        'S_first_entered = S_first_entered_found[.COMPLETION = NORMAL]',
        '$leading_string_entered(S_first_entered.FRAMES, 0)',
        '$call_descriptors_valid(S_first_entered)', '$heap_valid($heap_graph(S_first_entered))',
        'S_left_found = $leading_string_seek(S_first_entered, 4, 4000)',
        r'S_left_found.COMPLETION = NORMAL \/ S_left_found.COMPLETION = BUDGET',
        'S_left = S_left_found[.COMPLETION = NORMAL]', '$leading_string_frontier(S_left, 4)',
        'S_left.TODO = (' + left(1) + ') :: ptask_tail*',
        'S_left.CURRENT = eps', 'S_left.FRAMES = eps',
        'S_left.STORE[n_target] = DEFINED (PINT 99)',
        'S_left.STORE[n_right] = DEFINED (pvalue_saved)', 'pvalue_saved = ' + saved,
        '$string_carrier_valid(S_left, pvalue_saved)',
        '$string_long($ptascii(' + json.dumps(text) + ')) = STRINT i_right ([LEADINGNUMBER])',
        'i_right = ' + number,
        'S_left.STORE[n_v] = DEFINED (PINT 100)', 'S_left.STORE[n_calls] = DEFINED (PINT 1)',
        '$lookup(S_left.ENV, $ptascii("alias")) = (n_target)',
        'n_target <- S_left.REFCELLS', '~(n_right <- S_left.REFCELLS)',
        '$heap_owners($heap_prune($heap_graph(S_left)), HCELL n_target) = 2',
        snapshot + '(S_left, pintegeroperation, n_target, n_right) = ((pvalue_saved, i_right))',
        '$bothassign_quiet_string_snapshot(S_left, pintegeroperation, n_target, n_right) = eps',
        '$modassign_both_right_snapshot(S_left, pintegeroperation, n_target, n_right) = eps',
        '$call_descriptors_valid(S_left)', '$heap_valid($heap_graph(S_left))',
        'S_marker_budget = $drive_steps(S_left, 1)', 'S_marker_budget.COMPLETION = BUDGET',
        'S_marker = S_marker_budget[.COMPLETION = NORMAL]', '$leading_string_frontier(S_marker, 5)',
        'S_marker.TODO = (' + marker(0) + ') :: ptask_tail*',
        'S_marker.STORE = S_left.STORE', 'S_marker.ENV = S_left.ENV',
        'S_marker.EVENTS = S_left.EVENTS', 'S_marker.STRINGDATA = S_left.STRINGDATA',
        '$call_task_valid(S_marker, ' + marker(0) + ')', '$task_nodes(' + marker(0) + ') = eps',
        '~$call_task_valid(S_marker, ' + marker(2) + ')',
        '$call_descriptors_valid(S_marker)', '$heap_valid($heap_graph(S_marker))',
        'S_second_budget = $drive_steps(S_marker, 1)', 'S_second_budget.COMPLETION = BUDGET',
        'S_second = S_second_budget[.COMPLETION = NORMAL]', '$leading_string_frontier(S_second, 6)',
        'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
        'perrorcall_second.RESUME = ' + marker(1), 'perrorcall_second.TARGET = eps',
        'perrorcall_second.LEVEL = 2', 'perrorcall_second.LINE = 25',
        'perrorcall_second.MESSAGE = $ptascii("A non-numeric value encountered")',
        'perrorcall_second.EVENT = DIAGNOSTIC "Warning" perrorcall_second.MESSAGE 25',
        '$error_call_valid(S_second, perrorcall_second)',
        '$call_descriptors_valid(S_second)', '$heap_valid($heap_graph(S_second))',
        '~$error_call_valid(S_second, perrorcall_second[.LEVEL = 8192])',
        '~$error_call_valid(S_second, perrorcall_second[.LINE = 24])',
        '~$error_call_valid(S_second, perrorcall_second[.MESSAGE = $ptascii("wrong")])',
        '~$error_call_valid(S_second, perrorcall_second[.RESUME = ' + marker(1, integer='2') + '])',
        '$call_task_valid(S_second, ' + marker(1, 'PSTRING_CARRIER INTERNED_STRING ($ptascii("-2tail"))', '(-2)') + ')',
        '~$error_call_valid(S_second, perrorcall_second[.RESUME = ' + marker(1, 'PSTRING_CARRIER INTERNED_STRING ($ptascii("-2tail"))', '(-2)') + '])',
        'S_second_entered_found = $leading_string_seek(S_second, 7, 4000)',
        r'S_second_entered_found.COMPLETION = NORMAL \/ S_second_entered_found.COMPLETION = BUDGET',
        'S_second_entered = S_second_entered_found[.COMPLETION = NORMAL]',
        '$leading_string_entered(S_second_entered.FRAMES, 1)',
        '$call_descriptors_valid(S_second_entered)', '$heap_valid($heap_graph(S_second_entered))',
        'S_return_found = $leading_string_seek(S_second_entered, 8, 4000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', '$leading_string_frontier(S_return, 8)',
        'S_return.TODO = (' + marker(1) + ') :: ptask_tail*',
        'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
        'S_return.STORE[n_target] = DEFINED (PINT 88)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)', 'S_return.STORE[n_calls] = DEFINED (PINT 2)',
        '$lookup(S_return.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S_return.ENV, $ptascii("alias")) = (n_target)', 'n_target <- S_return.REFCELLS',
        'S_return.STRINGDATA[0:|S_left.STRINGDATA|] = S_left.STRINGDATA', '$string_carrier_valid(S_return, pvalue_saved)',
        '$call_task_valid(S_return, ' + marker(1) + ')', '~$call_task_valid(S_return, ' + marker(0) + ')',
        '$task_nodes(' + marker(1) + ') = eps',
        '$powerassign_warning_ready(S_return, pintegeroperation, n_target)',
        snapshot + '(S_return, pintegeroperation, n_target, n_right) = eps',
        '$leading_string_review_diagnostics(S_return.EVENTS, "Deprecated") = 0',
        '$leading_string_review_diagnostics(S_return.EVENTS, "Warning") = 1',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
    ]
    if xor:
        checks += [
            '$lookup(S_return.ENV, $ptascii("right")) = (n_target)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_target) = 3',
        ]
    elif unset:
        checks += [
            '$lookup(S_return.ENV, $ptascii("right")) = eps',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_target) = 2',
        ]
    else:
        checks += [
            '$lookup(S_return.ENV, $ptascii("right")) = (n_right)',
            'S_return.STORE[n_right] = DEFINED (PINT 7)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_target) = 2',
        ]
    checks += [
        '$integer_binary(pintegeroperation.OP, i_left, i_right) = ' + ('IRESULT (-13)' if xor else ('NEGSHIFT' if unset else 'INTZERO')),
        'S_step_budget = $drive_steps(S_return, 1)', 'S_step_budget.COMPLETION = BUDGET',
        'S_step = S_step_budget[.COMPLETION = NORMAL]',
        'S_step.EVENTS = S_return.EVENTS', 'S_step.STRINGDATA = S_return.STRINGDATA',
        '~$leading_string_tasks(S_step.TODO)',
    ]
    if xor:
        checks += [
            '$leading_string_frontier(S_step, 9)', 'S_step.TODO = ptask_tail*',
            'S_step.RESULT = KNOWN (PINT (-13))',
            '$lookup(S_step.ENV, $ptascii("left")) = (n_new)', 'n_new = |S_return.STORE|',
            'S_step.CELL = n_new', 'S_step.LOCATION = ROOT n_new', '~(n_new <- S_step.REFCELLS)',
            '$lookup(S_step.ENV, $ptascii("right")) = (n_target)',
            '$lookup(S_step.ENV, $ptascii("alias")) = (n_target)',
            'S_step.STORE = S_return.STORE ++ [DEFINED (PINT (-13))]',
            'S_step.ALLOCATIONS = S_return.ALLOCATIONS ++ [HCELL n_new]',
            '$heap_owners($heap_prune($heap_graph(S_step)), HCELL n_target) = 2',
            '$heap_owners($heap_prune($heap_graph(S_step)), HCELL n_new) = 1',
            '$call_descriptors_valid(S_step)', '$heap_valid($heap_graph(S_step))',
            'S_done = $drive_steps(S_step, 4000)',
            '$lookup(S_done.ENV, $ptascii("left")) = (n_new)',
            '$lookup(S_done.ENV, $ptascii("right")) = (n_target)',
            'S_done.STORE[n_new] = DEFINED (PINT 7)',
            'S_done.STORE[n_target] = DEFINED (PINT 6)',
            'S_done.STORE[n_v] = DEFINED (PINT (-13))',
        ]
    else:
        checks += [
            '$leading_string_frontier(S_step, 10)',
            'S_step.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
            'S_step.RESULT = KNOWN PNULL', 'S_step.CURRENT = eps', 'S_step.FRAMES = eps',
            'n_error = |S_return.OBJECTS|',
            'S_step.OBJECTS[n_error] = THROWABLE pthrowable',
            'S_step.OBJECTS = S_return.OBJECTS ++ [THROWABLE pthrowable]',
            'pthrowable.KIND = ' + json.dumps(error_kind), 'pthrowable.ORIGIN = (pintegeroperation.SITE)',
            '$throwable_field(S_step, n_error, "line") = PINT 25',
            '$string_bytes($throwable_field(S_step, n_error, "message")) = ($ptascii(' + json.dumps(error_message) + '))',
            '$throwable_previous_id(S_step, n_error) = eps', '$throwable_live(S_step, n_error)',
            '$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]',
            '$heap_owners($heap_prune($heap_graph(S_step)), HOBJECT n_error) = 1',
            'S_step.STORE = S_return.STORE', 'S_step.ENV = S_return.ENV',
            'S_step.REFCELLS = S_return.REFCELLS',
            '$heap_owners($heap_prune($heap_graph(S_step)), HCELL n_target) = 2',
            '$call_descriptors_valid(S_step)', '$heap_valid($heap_graph(S_step))',
            'S_done = $drive_steps(S_step, 4000)',
            '$lookup(S_done.ENV, $ptascii("left")) = (n_target)',
            'S_done.STORE[n_target] = DEFINED (PINT 7)', 'S_done.STORE[n_v] = DEFINED (PINT 100)',
        ]
        if unset:
            checks += ['$lookup(S_done.ENV, $ptascii("right")) = eps']
        else:
            checks += ['S_done.STORE[n_right] = DEFINED (PINT 7)']
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("alias")) = (n_target)',
        'S_done.STORE[n_calls] = DEFINED (PINT 2)',
        '$string_carrier_valid(S_done, pvalue_saved)',
        '$leading_string_review_diagnostics(S_done.EVENTS, "Deprecated") = 0',
        '$leading_string_review_diagnostics(S_done.EVENTS, "Warning") = 1',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]', '$drive_steps(S, 6000) = S_done',
        '$drive_steps(S_marker, 6000) = S_done', '$drive_steps(S_second, 6000) = S_done',
        '$drive_steps(S_return, 6000) = S_done',
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
    report['review_scope'] = 'Actual first LEFT deprecation then leading-string Warning: cached12/-1 XOR detaches target while RHS remains aliased, unset RHS cannot change cached negative-shift Error, cached0 modulo errors despite live7; fresh warning admission, immutable saved string metadata, exact stores/owners/default delivery and whole/budget equality'
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
