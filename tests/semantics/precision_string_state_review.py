#!/usr/bin/env python3
"""Reached precision notices retain protected text and converted integer history."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import precision_string_review_cases as cases
import precision_string_protocol as shared

REVIEW_HELPERS = r'''
dec $precision_string_review_diagnostic(pevent, text) : nat
def $precision_string_review_diagnostic(DIAGNOSTIC text n* z, text) = 1
def $precision_string_review_diagnostic(DIAGNOSTIC_SOURCE n_source text n* z, text) = 1
def $precision_string_review_diagnostic(DIAGNOSTIC_STACK text n* z n_trace*, text) = 1
def $precision_string_review_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n* z n_trace*, text) = 1
def $precision_string_review_diagnostic(pevent, text) = 0 -- otherwise
dec $precision_string_review_diagnostics(pevent*, text) : nat
def $precision_string_review_diagnostics(eps, text) = 0
def $precision_string_review_diagnostics(pevent :: pevent_tail*, text) = $($precision_string_review_diagnostic(pevent, text) + $precision_string_review_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    tag, operation, text, number, error_kind, error_message = {
        'precision-string-xor-complete-reference-default': ('BIT_ASSIGN_BOTH_LEFT', 'BITXOR', '-1.5', '(-1)', None, None),
        'precision-string-shift-leading-unset-default': ('SHIFT_ASSIGN_BOTH_LEFT', 'SHIFTRIGHT', '-1.5tail', '(-1)', 'ArithmeticError', 'Bit shift by negative number'),
        'precision-string-mod-leading-zero-default': ('MOD_ASSIGN_BOTH_LEFT', 'MODULO', '0.5tail', '0', 'DivisionByZeroError', 'Modulo by zero'),
    }[name]
    complete = error_kind is None
    unset = error_kind == 'ArithmeticError'
    leading = not complete
    warning_default = leading and not unset
    ascii_value = lambda value: '$ptascii(' + json.dumps(value) + ')'
    string = lambda value: 'PSTRING_CARRIER INTERNED_STRING (' + ascii_value(value) + ')'
    precision = lambda value: ascii_value('Implicit conversion from float-string "' + value + '" to int loses precision')
    warning = '$ptascii("A non-numeric value encountered")'
    notices = lambda value: ('[(2, ' + warning + '), (8192, ' + precision(value) + ')]' if leading else '[(8192, ' + precision(value) + ')]')
    cast_notices = '[LEADINGNUMBER, STRINGPRECISIONLOSS]' if leading else '[STRINGPRECISIONLOSS]'
    left = lambda stage: f'{tag} pintegeroperation n_target n_right n_bits_left i_left {stage}'
    marker = lambda cursor, conversion='pintegerconversion': f'BOTH_ASSIGN_PRECISION_STRING pintegeroperation n_target n_right n_bits_left i_left {conversion} {cursor}'
    snapshot = '$bothassign_precision_string_snapshot'
    alt_text, alt_number = ('1.5tail', '1') if warning_default else (('-2.5tail', '(-2)') if leading else ('-2.5', '(-2)'))
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_left_found = $precision_string_seek(S_initial, 4, 4000)',
        r'S_left_found.COMPLETION = NORMAL \/ S_left_found.COMPLETION = BUDGET',
        'S_left = S_left_found[.COMPLETION = NORMAL]', '$precision_string_frontier(S_left, 4)',
        'S_left.TODO = (' + left(1) + ') :: ptask_tail*',
        'n_bits_left = 4623226492472524800', 'i_left = 12',
        'pintegeroperation.OP = ' + operation, '~pintegeroperation.SWAPPED',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LINE = 25', 'S_left.ORIGIN = (pintegeroperation.SITE)',
        'S_left.CURRENT = eps', 'S_left.FRAMES = eps',
        '$lookup(S_left.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S_left.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_left.ENV, $ptascii("alias")) = (n_target)',
        '$lookup(S_left.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_left.ENV, $ptascii("calls")) = (n_calls)',
        'S_left.STORE[n_target] = DEFINED (PINT 99)',
        'S_left.STORE[n_right] = DEFINED pvalue_saved', 'pvalue_saved = ' + string(text),
        'S_left.STORE[n_v] = DEFINED (PINT 100)', 'S_left.STORE[n_calls] = DEFINED (PINT 1)',
        'n_target <- S_left.REFCELLS', '~(n_right <- S_left.REFCELLS)',
        '$heap_owners($heap_prune($heap_graph(S_left)), HCELL n_target) = 2',
        '$string_carrier_valid(S_left, pvalue_saved)',
        '$string_long(' + ascii_value(text) + ') = STRINT i_right (' + cast_notices + ')',
        'i_right = ' + number,
        snapshot + '(S_left, pintegeroperation, n_target, n_right) = (pintegerconversion)',
        'pintegerconversion.INPUT = pvalue_saved', 'pintegerconversion.VALUE = i_right',
        'pintegerconversion.NOTICES = ' + notices(text),
        '$integer_conversion(pvalue_saved) = (pintegerconversion)',
        '$bothassign_leading_string_snapshot(S_left, pintegeroperation, n_target, n_right) = eps',
        '$bothassign_quiet_string_snapshot(S_left, pintegeroperation, n_target, n_right) = eps',
        '$call_task_valid(S_left, ' + left(1) + ')',
        '$precision_string_review_diagnostics(S_left.EVENTS, "Deprecated") = 0',
        '$precision_string_review_diagnostics(S_left.EVENTS, "Warning") = 0',
        '$call_descriptors_valid(S_left)', '$heap_valid($heap_graph(S_left))',
        'S_marker_budget = $drive_steps(S_left, 1)', 'S_marker_budget.COMPLETION = BUDGET',
        'S_marker = S_marker_budget[.COMPLETION = NORMAL]', '$precision_string_frontier(S_marker, 5)',
        'S_marker.TODO = (' + marker(0) + ') :: ptask_tail*',
        'S_marker.STORE = S_left.STORE', 'S_marker.ENV = S_left.ENV',
        'S_marker.EVENTS = S_left.EVENTS', 'S_marker.STRINGDATA = S_left.STRINGDATA',
        '$call_task_valid(S_marker, ' + marker(0) + ')', '$task_nodes(' + marker(0) + ') = eps',
        '~$call_task_valid(S_marker, ' + marker(3) + ')',
        '~$call_task_valid(S_marker, ' + marker(1, 'pintegerconversion[.VALUE = 7]') + ')',
        '$call_descriptors_valid(S_marker)', '$heap_valid($heap_graph(S_marker))',
        'S_notice_budget = $drive_steps(S_marker, 1)', 'S_notice_budget.COMPLETION = BUDGET',
        'S_notice = S_notice_budget[.COMPLETION = NORMAL]', '$precision_string_frontier(S_notice, 6)',
        'S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
        'perrorcall_first.RESUME = ' + marker(1), 'perrorcall_first.TARGET = eps',
        'perrorcall_first.LEVEL = ' + ('8192' if complete else '2'),
        'perrorcall_first.LINE = 25',
        'perrorcall_first.MESSAGE = ' + (precision(text) if complete else warning),
        'perrorcall_first.EVENT = DIAGNOSTIC ' + ('"Deprecated"' if complete else '"Warning"') + ' perrorcall_first.MESSAGE 25',
        '$error_call_valid(S_notice, perrorcall_first)',
        '~$error_call_valid(S_notice, perrorcall_first[.LINE = 24])',
        '~$error_call_valid(S_notice, perrorcall_first[.LEVEL = ' + ('2' if complete else '8192') + '])',
        '~$error_call_valid(S_notice, perrorcall_first[.RESUME = ' + marker(0) + '])',
        'pintegerconversion_alt = pintegerconversion[.INPUT = ' + string(alt_text) + '][.VALUE = ' + alt_number + '][.NOTICES = ' + notices(alt_text) + ']',
        '$call_task_valid(S_notice, ' + marker(1, 'pintegerconversion_alt') + ')',
        '~$error_call_valid(S_notice, perrorcall_first[.RESUME = ' + marker(1, 'pintegerconversion_alt') + '][.MESSAGE = ' + (precision(alt_text) if complete else warning) + '][.EVENT = DIAGNOSTIC ' + ('"Deprecated"' if complete else '"Warning"') + ' ' + (precision(alt_text) if complete else warning) + ' 25])',
        '$call_descriptors_valid(S_notice)', '$heap_valid($heap_graph(S_notice))',
        'S_entered_found = $precision_string_seek(S_notice, 7, 4000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', '$precision_string_entered(S_entered.FRAMES, 1)',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
        'S_after_found = $precision_string_seek(S_entered, 8, 4000)',
        r'S_after_found.COMPLETION = NORMAL \/ S_after_found.COMPLETION = BUDGET',
        'S_after = S_after_found[.COMPLETION = NORMAL]', '$precision_string_frontier(S_after, 8)',
        'S_after.TODO = (' + marker(1) + ') :: ptask_tail*',
        'S_after.CURRENT = eps', 'S_after.FRAMES = eps',
        'S_after.STORE[n_target] = DEFINED (PINT 88)',
        'S_after.STORE[n_v] = DEFINED (PINT 100)', 'S_after.STORE[n_calls] = DEFINED (PINT 2)',
        '$lookup(S_after.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S_after.ENV, $ptascii("alias")) = (n_target)', 'n_target <- S_after.REFCELLS',
        '$lookup(S_after.ENV, $ptascii("right")) = ' + ('(n_target)' if complete else ('eps' if unset else '(n_right)')),
        '$heap_owners($heap_prune($heap_graph(S_after)), HCELL n_target) = ' + ('3' if complete else '2'),
        '$call_task_valid(S_after, ' + marker(1) + ')', '~$call_task_valid(S_after, ' + marker(0) + ')',
        '$task_nodes(' + marker(1) + ') = eps',
        '$powerassign_warning_ready(S_after, pintegeroperation, n_target)',
        snapshot + '(S_after, pintegeroperation, n_target, n_right) = eps',
        'S_after.STRINGDATA[0:|S_left.STRINGDATA|] = S_left.STRINGDATA',
        '$string_carrier_valid(S_after, pvalue_saved)',
        '$precision_string_review_diagnostics(S_after.EVENTS, "Deprecated") = ' + ('1' if complete else '0'),
        '$precision_string_review_diagnostics(S_after.EVENTS, "Warning") = ' + ('1' if warning_default else '0'),
        '$call_descriptors_valid(S_after)', '$heap_valid($heap_graph(S_after))',
    ]
    if warning_default:
        checks += ['S_after.STORE[n_right] = DEFINED (PINT 7)']
    if leading:
        checks += [
            'S_precision_budget = $drive_steps(S_after, 1)', 'S_precision_budget.COMPLETION = BUDGET',
            'S_precision = S_precision_budget[.COMPLETION = NORMAL]', '$precision_string_frontier(S_precision, 11)',
            'S_precision.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
            'perrorcall_second.RESUME = ' + marker(2), 'perrorcall_second.TARGET = eps',
            'perrorcall_second.LEVEL = 8192', 'perrorcall_second.LINE = 25',
            'perrorcall_second.MESSAGE = ' + precision(text),
            'perrorcall_second.EVENT = DIAGNOSTIC "Deprecated" perrorcall_second.MESSAGE 25',
            '$error_call_valid(S_precision, perrorcall_second)',
            '~$error_call_valid(S_precision, perrorcall_second[.MESSAGE = $ptascii("wrong")])',
            '~$error_call_valid(S_precision, perrorcall_second[.RESUME = ' + marker(3) + '])',
            '~$error_call_valid(S_precision, perrorcall_second[.RESUME = ' + marker(2, 'pintegerconversion[.VALUE = 7]') + '])',
            '$lookup(S_precision.ENV, $ptascii("right")) = ' + ('eps' if unset else '(n_right)'),
            '$call_descriptors_valid(S_precision)', '$heap_valid($heap_graph(S_precision))',
            'S_precision_entered_found = $precision_string_seek(S_precision, 12, 4000)',
            r'S_precision_entered_found.COMPLETION = NORMAL \/ S_precision_entered_found.COMPLETION = BUDGET',
            'S_precision_entered = S_precision_entered_found[.COMPLETION = NORMAL]',
            '$precision_string_entered(S_precision_entered.FRAMES, 2)',
            '$call_descriptors_valid(S_precision_entered)', '$heap_valid($heap_graph(S_precision_entered))',
            'S_return_found = $precision_string_seek(S_precision_entered, 13, 4000)',
            r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
            'S_return = S_return_found[.COMPLETION = NORMAL]', '$precision_string_frontier(S_return, 13)',
            'S_return.TODO = (' + marker(2) + ') :: ptask_tail*',
            'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
            'S_return.STORE[n_target] = DEFINED (PINT 77)',
            'S_return.STORE[n_v] = DEFINED (PINT 100)', 'S_return.STORE[n_calls] = DEFINED (PINT 3)',
            '$lookup(S_return.ENV, $ptascii("left")) = (n_target)',
            '$lookup(S_return.ENV, $ptascii("alias")) = (n_target)',
            '$lookup(S_return.ENV, $ptascii("right")) = ' + ('eps' if unset else '(n_right)'),
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_target) = 2',
            '$call_task_valid(S_return, ' + marker(2) + ')', '~$call_task_valid(S_return, ' + marker(0) + ')',
            '$task_nodes(' + marker(2) + ') = eps',
            '$powerassign_warning_ready(S_return, pintegeroperation, n_target)',
            snapshot + '(S_return, pintegeroperation, n_target, n_right) = eps',
            'S_return.STRINGDATA[0:|S_after.STRINGDATA|] = S_after.STRINGDATA',
            '$string_carrier_valid(S_return, pvalue_saved)',
            '$precision_string_review_diagnostics(S_return.EVENTS, "Deprecated") = 1',
            '$precision_string_review_diagnostics(S_return.EVENTS, "Warning") = ' + ('1' if warning_default else '0'),
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        ]
        if warning_default:
            checks += ['S_return.STORE[n_right] = DEFINED (PINT 7)']
    else:
        checks += ['S_return = S_after']
    checks += [
        '$integer_binary(pintegeroperation.OP, i_left, i_right) = ' + ('IRESULT (-13)' if complete else ('NEGSHIFT' if unset else 'INTZERO')),
        'S_step_budget = $drive_steps(S_return, 1)', 'S_step_budget.COMPLETION = BUDGET',
        'S_step = S_step_budget[.COMPLETION = NORMAL]',
        '~$precision_string_tasks(S_step.TODO)',
        'S_step.EVENTS = S_return.EVENTS', 'S_step.STRINGDATA = S_return.STRINGDATA',
    ]
    if complete:
        checks += [
            '$precision_string_frontier(S_step, 9)', 'S_step.TODO = ptask_tail*',
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
            '$precision_string_frontier(S_step, 10)',
            'S_step.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
            'S_step.RESULT = KNOWN PNULL', 'S_step.CURRENT = eps', 'S_step.FRAMES = eps',
            'n_error = |S_return.OBJECTS|', 'S_step.OBJECTS[n_error] = THROWABLE pthrowable',
            'S_step.OBJECTS = S_return.OBJECTS ++ [THROWABLE pthrowable]',
            'pthrowable.KIND = ' + json.dumps(error_kind), 'pthrowable.ORIGIN = (pintegeroperation.SITE)',
            '$throwable_field(S_step, n_error, "line") = PINT 25',
            '$string_bytes($throwable_field(S_step, n_error, "message")) = (' + ascii_value(error_message) + ')',
            '$throwable_previous_id(S_step, n_error) = eps', '$throwable_live(S_step, n_error)',
            '$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]',
            '$heap_owners($heap_prune($heap_graph(S_step)), HOBJECT n_error) = 1',
            'S_step.STORE = S_return.STORE', 'S_step.ENV = S_return.ENV',
            'S_step.REFCELLS = S_return.REFCELLS',
            'S_step.ARRAYS[0:|S_return.ARRAYS|] = S_return.ARRAYS',
            '$heap_owners($heap_prune($heap_graph(S_step)), HCELL n_target) = 2',
            '$call_descriptors_valid(S_step)', '$heap_valid($heap_graph(S_step))',
            'S_done = $drive_steps(S_step, 4000)',
            '$lookup(S_done.ENV, $ptascii("left")) = (n_target)',
            '$lookup(S_done.ENV, $ptascii("right")) = ' + ('eps' if unset else '(n_right)'),
            'S_done.STORE[n_target] = DEFINED (PINT 7)', 'S_done.STORE[n_v] = DEFINED (PINT 100)',
        ]
        if warning_default:
            checks += ['S_done.STORE[n_right] = DEFINED (PINT 7)']
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("alias")) = (n_target)',
        'S_done.STORE[n_calls] = DEFINED (PINT ' + ('2' if complete else '3') + ')',
        '$string_carrier_valid(S_done, pvalue_saved)',
        '$precision_string_review_diagnostics(S_done.EVENTS, "Deprecated") = 1',
        '$precision_string_review_diagnostics(S_done.EVENTS, "Warning") = ' + ('1' if warning_default else '0'),
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_left, 0) = S_left[.COMPLETION = BUDGET]',
        '$drive_steps(S_left, 6000) = S_done', '$drive_steps(S_marker, 6000) = S_done',
        '$drive_steps(S_notice, 6000) = S_done',
        '$drive_steps(S_return, 6000) = S_done',
    ]
    if leading:
        checks += ['$drive_steps(S_after, 6000) = S_done', '$drive_steps(S_precision, 6000) = S_done']
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
    report['review_scope'] = 'Actual protected complete precision and leading Warning/precision frames: fresh cursor0 authenticates RHS, later cursor history survives RHS reference/unset/live7; cached negative mask detaches target, negative shift/zero modulo preserve aliases and destination, exact default order/atomic metadata and full-budget equality'
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
