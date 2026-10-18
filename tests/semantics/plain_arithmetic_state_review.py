#!/usr/bin/env python3
"""Reached plain-CV holders survive late references/unsetting; failures use live types."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import plain_arithmetic_review_cases as cases
import plain_arithmetic_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = r'''
dec $plain_arithmetic_review_diagnostic(pevent, text) : nat
def $plain_arithmetic_review_diagnostic(DIAGNOSTIC text n* z, text) = 1
def $plain_arithmetic_review_diagnostic(DIAGNOSTIC_SOURCE n_source text n* z, text) = 1
def $plain_arithmetic_review_diagnostic(DIAGNOSTIC_STACK text n* z n_trace*, text) = 1
def $plain_arithmetic_review_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n* z n_trace*, text) = 1
def $plain_arithmetic_review_diagnostic(pevent, text) = 0 -- otherwise
dec $plain_arithmetic_review_diagnostics(pevent*, text) : nat
def $plain_arithmetic_review_diagnostics(eps, text) = 0
def $plain_arithmetic_review_diagnostics(pevent :: pevent_tail*, text) = $($plain_arithmetic_review_diagnostic(pevent, text) + $plain_arithmetic_review_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    multiply, failure, unset = name == CASES[0], name == CASES[1], name == CASES[2]
    operation = 'MULTIPLY' if multiply else ('SUBTRACT' if failure else 'DIVIDE')
    left_number = 'NFLOAT 4623226492472524800' if multiply else ('NINT 2' if failure else 'NINT 12')
    right_number = 'NFLOAT 4617878467915022336' if multiply else 'NINT 2'
    value = 'PFLOAT 4634538268099084288' if multiply else ('PINT 100' if failure else 'PINT 6')
    phase = 'ARITHMETIC_RIGHT pnumber_left'
    convert = lambda p: f'ARITHMETIC_CV_CONVERT pintegeroperation ({p})'
    warning = lambda p, raw, number, stage: f'ARITHMETIC_CV_WARNING pintegeroperation ({p}) {raw} {number} {stage}'
    left = lambda stage: warning('ARITHMETIC_LEFT', 'pvalue_left', 'pnumber_left', stage)
    right = lambda stage: warning(phase, 'pvalue_right', 'pnumber_right', stage)
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $plain_arithmetic_seek({before}, {stage}, 5000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]', f'$plain_arithmetic_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)', f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_plan', 'S_initial', 0)
    checks += [
        '$arithmetic_cv_plan(S_plan) = (pintegeroperation)', '$arithmetic_cv_valid(S_plan, pintegeroperation)',
        '$arithmetic_add_plan(S_plan) = eps', '$arithmetic_div_plan(S_plan) = eps', '$submul_warning_plan(S_plan) = eps',
        '$power_conversion_warning_plan(S_plan) = eps',
        'pintegeroperation.OP = ' + operation, '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23', 'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("left"))', 'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))',
        '$lookup(S_plan.ENV, $ptascii("left")) = (n_left)', '$lookup(S_plan.ENV, $ptascii("right")) = (n_right)', 'n_left =/= n_right',
        '$lookup(S_plan.ENV, $ptascii("calls")) = (n_calls)', '$lookup(S_plan.ENV, $ptascii("v")) = (n_v)',
        '~(n_left <- S_plan.REFCELLS)', '~(n_right <- S_plan.REFCELLS)',
        'S_plan.STORE[n_left] = DEFINED pvalue_left', 'S_plan.STORE[n_right] = DEFINED pvalue_initial_right',
        '$arithmetic_cv_value(S_plan, pintegeroperation.LEFTPOINTER) = (pvalue_left)',
        '$arithmetic_cv_value(S_plan, pintegeroperation.RIGHTPOINTER) = (pvalue_initial_right)',
        'pnumber_left = ' + left_number,
        '$arithmetic_add_conversion(pvalue_left) = ((pnumber_left, ' + ('false' if unset else 'true') + '))',
        'S_plan.STORE[n_calls] = DEFINED (PINT 0)', 'S_plan.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_plan)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_plan)), HCELL n_right) = 1',
        '$call_descriptors_valid(S_plan)', '$heap_valid($heap_graph(S_plan))',
    ]
    checks += [
        'pvalue_left = PINT 12', '$string_bytes(pvalue_initial_right) = ($ptascii("2tail"))',
    ] if unset else [
        '$string_bytes(pvalue_left) = ($ptascii("' + ('12.5tail' if multiply else '2tail') + '"))',
        '$string_bytes(pvalue_initial_right) = ($ptascii("bad"))', '$arithmetic_add_conversion(pvalue_initial_right) = eps',
    ]
    step('S_begin', 'S_plan')
    checks += [
        'S_plan.TODO = ptask_old :: ptask_tail*',
        'S_begin = S_plan[.TODO = (' + convert('ARITHMETIC_LEFT') + ') :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$call_task_valid(S_begin, ' + convert('ARITHMETIC_LEFT') + ')', '$task_nodes(' + convert('ARITHMETIC_LEFT') + ') = eps',
    ]
    if not unset:
        step('S_capture', 'S_begin')
        checks += [
            'S_capture = S_begin[.TODO = (' + left(0) + ') :: ptask_tail*]',
            '$arithmetic_cv_warning_valid(S_capture, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, pnumber_left, 0)',
            '$task_nodes(' + left(0) + ') = eps',
        ]
        step('S_first', 'S_capture')
        checks += [
            '$plain_arithmetic_frontier(S_first, 3)', 'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
            'perrorcall_first.RESUME = ' + left(1), 'perrorcall_first.TARGET = eps',
            'perrorcall_first.LINE = 25', 'perrorcall_first.LEVEL = 2', '$error_call_valid(S_first, perrorcall_first)',
        ]
        if multiply:
            checks += [
                '~$error_call_valid(S_first, perrorcall_first[.RESUME = ARITHMETIC_CV_WARNING pintegeroperation ARITHMETIC_LEFT (PSTRING ($ptascii("13.5tail"))) (NFLOAT 4623789442425946112) 1])',
            ]
        seek('S_left_entered', 'S_first', 10)
        checks += ['$plain_arithmetic_entered(S_left_entered.FRAMES, 0)', '$call_descriptors_valid(S_left_entered)', '$heap_valid($heap_graph(S_left_entered))']
        seek('S_left', 'S_left_entered', 4)
        checks += [
            'S_left.TODO = (' + left(1) + ') :: ptask_tail*',
            '$arithmetic_cv_warning_valid(S_left, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, pnumber_left, 1)',
            '~$arithmetic_cv_warning_valid(S_left, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, pnumber_left, 0)',
            'S_left.STORE[n_calls] = DEFINED (PINT 1)', 'S_left.STORE[n_v] = DEFINED (PINT 100)',
            'S_left.STRINGDATA[0:|S_capture.STRINGDATA|] = S_capture.STRINGDATA',
            '$call_descriptors_valid(S_left)', '$heap_valid($heap_graph(S_left))',
        ]
        step('S_right', 'S_left')
        checks += ['S_right = S_left[.TODO = (' + convert(phase) + ') :: ptask_tail*][.RESULT = KNOWN PNULL]']
    else:
        step('S_right', 'S_begin')
        checks += [
            'S_right = S_begin[.TODO = (' + convert(phase) + ') :: ptask_tail*][.RESULT = KNOWN PNULL]',
            '~$plain_arithmetic_frontier(S_right, 2)', 'S_right.STORE[n_calls] = DEFINED (PINT 0)',
        ]
    checks += [
        '$plain_arithmetic_frontier(S_right, 5)', '$call_task_valid(S_right, ' + convert(phase) + ')',
        '$task_nodes(' + convert(phase) + ') = eps',
    ]
    if failure:
        checks += [
            'S_left.STORE[n_left] = DEFINED (PBOOL false)', 'S_left.STORE[n_right] = DEFINED pvalue_initial_right',
            '$arithmetic_cv_failure_operands(S_right, pintegeroperation, ' + phase + ') = ((PBOOL false, pvalue_initial_right))',
            '$arithmetic_cv_failure_operands(S_right, pintegeroperation, ARITHMETIC_LEFT) = eps',
            '$plain_arithmetic_review_diagnostics(S_right.EVENTS, "Warning") = 1',
        ]
        step('S_result', 'S_right')
        checks += [
            '$plain_arithmetic_frontier(S_result, 9)', 'S_result.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
            'S_result.RESULT = KNOWN PNULL', 'S_result.CURRENT = eps', 'n_error = |S_right.OBJECTS|',
            'S_result.OBJECTS[n_error] = THROWABLE pthrowable', 'S_result.OBJECTS = S_right.OBJECTS ++ [THROWABLE pthrowable]',
            'pthrowable.KIND = "TypeError"', 'pthrowable.ORIGIN = (pintegeroperation.SITE)',
            '$throwable_field(S_result, n_error, "line") = PINT 25',
            '$string_bytes($throwable_field(S_result, n_error, "message")) = ($ptascii("Unsupported operand types: bool - string"))',
            '$throwable_previous_id(S_result, n_error) = eps', '$throwable_live(S_result, n_error)',
            '$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]', '$heap_owners($heap_prune($heap_graph(S_result)), HOBJECT n_error) = 1',
            'S_result.STORE = S_right.STORE', 'S_result.ENV = S_right.ENV', 'S_result.REFCELLS = S_right.REFCELLS',
            'S_result.EVENTS = S_right.EVENTS', 'S_result.STRINGDATA = S_right.STRINGDATA',
            'S_result.ARRAYS[0:|S_right.ARRAYS|] = S_right.ARRAYS',
        ]
    else:
        if multiply:
            checks += [
                'S_left.STORE[n_left] = DEFINED (PINT 99)', 'S_left.STORE[n_right] = DEFINED pvalue_right',
                '$string_bytes(pvalue_right) = ($ptascii("5.5tail"))',
            ]
        else:
            checks += ['pvalue_right = pvalue_initial_right']
        checks += [
            'pnumber_right = ' + right_number, '$arithmetic_add_conversion(pvalue_right) = ((pnumber_right, true))',
        ]
        step('S_right_capture', 'S_right')
        checks += [
            'S_right_capture = S_right[.TODO = (' + right(0) + ') :: ptask_tail*]',
            '$arithmetic_cv_warning_valid(S_right_capture, pintegeroperation, ' + phase + ', pvalue_right, pnumber_right, 0)',
            '$task_nodes(' + right(0) + ') = eps',
        ]
        step('S_second', 'S_right_capture')
        checks += [
            '$plain_arithmetic_frontier(S_second, 7)', 'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
            'perrorcall_second.RESUME = ' + right(1), 'perrorcall_second.TARGET = eps',
            'perrorcall_second.LINE = 25', 'perrorcall_second.LEVEL = 2', '$error_call_valid(S_second, perrorcall_second)',
        ]
        if multiply:
            checks += [
                '~$error_call_valid(S_second, perrorcall_second[.RESUME = ARITHMETIC_CV_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) (PSTRING ($ptascii("6.5tail"))) (NFLOAT 4619004367821864960) 1])',
            ]
        seek('S_right_entered', 'S_second', 11)
        checks += ['$plain_arithmetic_entered(S_right_entered.FRAMES, 1)', '$call_descriptors_valid(S_right_entered)', '$heap_valid($heap_graph(S_right_entered))']
        seek('S_return', 'S_right_entered', 8)
        checks += [
            'S_return.TODO = (' + right(1) + ') :: ptask_tail*',
            '$arithmetic_cv_warning_valid(S_return, pintegeroperation, ' + phase + ', pvalue_right, pnumber_right, 1)',
            '~$arithmetic_cv_warning_valid(S_return, pintegeroperation, ' + phase + ', pvalue_right, pnumber_right, 0)',
            '$arithmetic_cv_value(S_return, pintegeroperation.RIGHTPOINTER) = eps',
            '~$arithmetic_cv_fresh(S_return, pintegeroperation, ' + phase + ', pvalue_right)',
            'S_return.STORE[n_v] = DEFINED (PINT 100)',
            'S_return.STORE[n_calls] = DEFINED (PINT ' + ('2' if multiply else '1') + ')',
            '$plain_arithmetic_review_diagnostics(S_return.EVENTS, "Warning") = 1',
            'S_return.STRINGDATA[0:|S_plan.STRINGDATA|] = S_plan.STRINGDATA',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        ]
        if multiply:
            checks += [
                '$lookup(S_return.ENV, $ptascii("right")) = (n_right)', '$lookup(S_return.ENV, $ptascii("rightAlias")) = (n_right)',
                'n_right <- S_return.REFCELLS', '~(n_left <- S_return.REFCELLS)',
                'S_return.STORE[n_left] = DEFINED (PBOOL false)', 'S_return.STORE[n_right] = DEFINED pvalue_bad',
                '$string_bytes(pvalue_bad) = ($ptascii("bad"))',
                '$integer_pointer_value(S_return, pintegeroperation.RIGHTPOINTER) = (pvalue_bad)',
                '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 2',
                '$num_mul(pnumber_left, pnumber_right) = NFLOAT 4634538268099084288',
            ]
        else:
            checks += [
                '$lookup(S_return.ENV, $ptascii("right")) = eps',
                '$integer_pointer_value(S_return, pintegeroperation.RIGHTPOINTER) = eps',
                'S_return.STORE[n_left] = DEFINED (PINT 99)',
                '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 0',
                '$num_div(pnumber_left, pnumber_right) = NUM (NINT 6)',
            ]
        step('S_result', 'S_return')
        checks += ['S_result = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (' + value + ')]']
    checks += [
        '~$plain_arithmetic_tasks(S_result.TODO)', '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_right) = ' + ('2' if multiply else ('0' if unset else '1')),
        'S_done = $drive_steps(S_result, 5000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_left)', '$lookup(S_done.ENV, $ptascii("right")) = (n_done_right)',
        'S_done.STORE[n_left] = DEFINED (PINT 7)', 'S_done.STORE[n_done_right] = DEFINED (PINT 8)',
        '$lookup(S_done.ENV, $ptascii("v")) = (n_done_v)', 'S_done.STORE[n_done_v] = DEFINED (' + value + ')',
        'S_done.STORE[n_calls] = DEFINED (PINT ' + ('2' if multiply else '1') + ')',
        '$plain_arithmetic_review_diagnostics(S_done.EVENTS, "Warning") = 1',
        '$plain_arithmetic_review_diagnostics(S_done.EVENTS, "Deprecated") = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_plan, 0) = S_plan[.COMPLETION = BUDGET]', '$drive_steps(S_plan, 7000) = S_done',
    ]
    if multiply:
        checks += [
            'n_done_right = n_right', '$lookup(S_done.ENV, $ptascii("rightAlias")) = (n_right)',
            '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_right) = 2',
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
    report['review_scope'] = 'Actual initially plain CV plans and phase-specific fresh inputs; late RHS reference or unsetting after capture retains cached float68.75/int6 while strict plain reads fail; live bool/string TypeError, original/late owner counts and exact atomic effects, default Warning and compact whole/split budgets'
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
