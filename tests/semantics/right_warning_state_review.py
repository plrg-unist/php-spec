#!/usr/bin/env python3
"""Reached quiet LEFT, cached right Warning, zero division and power history."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import right_warning_review_cases as cases
import right_warning_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = r'''
dec $right_warning_review_diagnostic(pevent, text) : nat
def $right_warning_review_diagnostic(DIAGNOSTIC text n* z, text) = 1
def $right_warning_review_diagnostic(DIAGNOSTIC_SOURCE n_source text n* z, text) = 1
def $right_warning_review_diagnostic(DIAGNOSTIC_STACK text n* z n_trace*, text) = 1
def $right_warning_review_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n* z n_trace*, text) = 1
def $right_warning_review_diagnostic(pevent, text) = 0 -- otherwise
dec $right_warning_review_diagnostics(pevent*, text) : nat
def $right_warning_review_diagnostics(eps, text) = 0
def $right_warning_review_diagnostics(pevent :: pevent_tail*, text) = $($right_warning_review_diagnostic(pevent, text) + $right_warning_review_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    multiply = name == CASES[0]
    zero = name == CASES[1]
    power = name == CASES[2]
    family, conversion, warning, plan, valid, warning_valid, operation = {
        CASES[0]: ('submul', 'SUBMUL_CONVERT', 'SUBMUL_WARNING', 'submul_warning_plan', 'submul_valid', 'submul_warning_valid', 'MULTIPLY'),
        CASES[1]: ('division', 'ARITHMETIC_DIV_CONVERT', 'ARITHMETIC_DIV_WARNING', 'arithmetic_div_plan', 'arithmetic_div_valid', 'arithmetic_div_warning_valid', 'DIVIDE'),
        CASES[2]: ('power_conversion', 'POWER_CONVERT', 'POWER_CONVERSION_WARNING', 'power_conversion_warning_plan', 'power_conversion_valid', 'power_conversion_warning_valid', 'POWER'),
    }[name]
    left_number = 'NFLOAT 4623226492472524800' if multiply else ('NINT 12' if zero else 'NFLOAT 9223372036854775808')
    right_number = 'NFLOAT 4617878467915022336' if multiply else ('NINT 0' if zero else 'NINT (-3)')
    right_text = '5.5tail' if multiply else ('0tail' if zero else '-3tail')
    result_value = 'PFLOAT 4634538268099084288' if multiply else ('PINT 100' if zero else 'PFLOAT 18442240474082181120')
    right_phase = 'ARITHMETIC_RIGHT pnumber_left'
    convert = lambda phase: f'{conversion} pintegeroperation ({phase})'
    warn = lambda stage: f'{warning} pintegeroperation ({right_phase}) pvalue_right pnumber_right {stage}'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = ${family}_seek({before}, {stage}, 5000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]', f'${family}_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)', f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_plan', 'S_initial', 0)
    checks += [
        '$arithmetic_right_warning_operation(S_plan) = (pintegeroperation)',
        f'${plan}(S_plan) = (pintegeroperation)', f'${valid}(S_plan, pintegeroperation)',
        'pintegeroperation.OP = ' + operation, '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23', 'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_left', 'pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_right', 'n_left =/= n_right',
        '$lookup(S_plan.ENV, $ptascii("left")) = (n_left)', '$lookup(S_plan.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_plan.ENV, $ptascii("right")) = (n_right)', '$lookup(S_plan.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_plan.ENV, $ptascii("v")) = (n_v)', '$lookup(S_plan.ENV, $ptascii("calls")) = (n_calls)',
        'n_left <- S_plan.REFCELLS', 'n_right <- S_plan.REFCELLS',
        'S_plan.STORE[n_left] = DEFINED pvalue_left', 'S_plan.STORE[n_right] = DEFINED pvalue_right',
        'pnumber_left = ' + left_number, 'pnumber_right = ' + right_number,
        '$arithmetic_add_conversion(pvalue_left) = ((pnumber_left, false))',
        '$arithmetic_add_conversion(pvalue_right) = ((pnumber_right, true))',
        '$string_bytes(pvalue_right) = ($ptascii("' + right_text + '"))',
        'S_plan.STORE[n_calls] = DEFINED (PINT 0)', 'S_plan.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_plan)), HCELL n_left) = 2', '$heap_owners($heap_prune($heap_graph(S_plan)), HCELL n_right) = 2',
        '$call_descriptors_valid(S_plan)', '$heap_valid($heap_graph(S_plan))',
    ]
    checks += ['$string_bytes(pvalue_left) = ($ptascii("12.5"))'] if multiply else [
        'pvalue_left = ' + ('PINT 12' if zero else 'PFLOAT 9223372036854775808')]
    step('S_begin', 'S_plan')
    checks += [
        'S_plan.TODO = ptask_old :: ptask_tail*',
        'S_begin = S_plan[.TODO = (' + convert('ARITHMETIC_LEFT') + ') :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$call_task_valid(S_begin, ' + convert('ARITHMETIC_LEFT') + ')', '$task_nodes(' + convert('ARITHMETIC_LEFT') + ') = eps',
    ]
    step('S_right', 'S_begin')
    checks += [
        'S_right = S_begin[.TODO = (' + convert(right_phase) + ') :: ptask_tail*][.RESULT = KNOWN PNULL]',
        f'${family}_frontier(S_right, 5)', f'~${family}_frontier(S_right, 2)', f'~${family}_frontier(S_right, 3)',
        '$call_task_valid(S_right, ' + convert(right_phase) + ')', '$task_nodes(' + convert(right_phase) + ') = eps',
        'S_right.STORE[n_calls] = DEFINED (PINT 0)',
    ]
    step('S_capture', 'S_right')
    checks += [
        'S_capture = S_right[.TODO = (' + warn(0) + ') :: ptask_tail*]',
        f'${family}_frontier(S_capture, 6)', f'${warning_valid}(S_capture, pintegeroperation, {right_phase}, pvalue_right, pnumber_right, 0)',
        '$task_nodes(' + warn(0) + ') = eps',
    ]
    step('S_first', 'S_capture')
    checks += [
        'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
        'perrorcall_first.RESUME = ' + warn(1), 'perrorcall_first.TARGET = eps',
        'perrorcall_first.LEVEL = 2', 'perrorcall_first.LINE = 25',
        'perrorcall_first.MESSAGE = $ptascii("A non-numeric value encountered")',
        'S_first.STORE[n_calls] = DEFINED (PINT 0)', '$error_call_valid(S_first, perrorcall_first)',
        '$call_descriptors_valid(S_first)',
        '~$error_call_valid(S_first, perrorcall_first[.RESUME = ' + warning + ' pintegeroperation (' + right_phase + ') (PSTRING ($ptascii("6tail"))) (NINT 6) 1])',
    ]
    if not zero:
        seek('S_entered', 'S_first', 11)
        checks += [f'${family}_entered(S_entered.FRAMES, 1)', f'~${family}_entered(S_entered.FRAMES, 0)',
                   '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))']
    seek('S_return', 'S_first' if zero else 'S_entered', 8)
    checks += [
        'S_return.TODO = (' + warn(1) + ') :: ptask_tail*',
        f'${warning_valid}(S_return, pintegeroperation, {right_phase}, pvalue_right, pnumber_right, 1)',
        f'~${warning_valid}(S_return, pintegeroperation, {right_phase}, pvalue_right, pnumber_right, 0)',
        'S_return.STORE[n_calls] = DEFINED (PINT 1)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
        'S_return.STRINGDATA[0:|S_plan.STRINGDATA|] = S_plan.STRINGDATA',
        '$right_warning_review_diagnostics(S_return.EVENTS, "Warning") = ' + ('0' if power else '1'),
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
    ]
    if multiply:
        checks += [
            'S_return.STORE[n_left] = DEFINED (PBOOL false)',
            'S_return.STORE[n_right] = DEFINED pvalue_bad', '$string_bytes(pvalue_bad) = ($ptascii("bad"))',
            '$num_mul(pnumber_left, pnumber_right) = NFLOAT 4634538268099084288',
        ]
        step('S_result', 'S_return')
        checks += ['S_result = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (' + result_value + ')]']
    elif zero:
        checks += ['S_return.STORE[n_left] = DEFINED (PBOOL false)', 'S_return.STORE[n_right] = DEFINED (PINT 7)',
                   '$num_div(pnumber_left, pnumber_right) = DIVZERO']
        step('S_result', 'S_return')
        checks += [
            '$division_frontier(S_result, 9)', 'S_result.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
            'S_result.CURRENT = eps', 'n_error = |S_return.OBJECTS|',
            'S_result.OBJECTS[n_error] = THROWABLE pthrowable', 'S_result.OBJECTS = S_return.OBJECTS ++ [THROWABLE pthrowable]',
            'pthrowable.KIND = "DivisionByZeroError"', 'pthrowable.ORIGIN = (pintegeroperation.SITE)',
            '$throwable_field(S_result, n_error, "line") = PINT 25',
            '$string_bytes($throwable_field(S_result, n_error, "message")) = ($ptascii("Division by zero"))',
            '$throwable_previous_id(S_result, n_error) = eps', '$throwable_live(S_result, n_error)',
            '$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]', '$heap_owners($heap_prune($heap_graph(S_result)), HOBJECT n_error) = 1',
            'S_result.STORE = S_return.STORE', 'S_result.ENV = S_return.ENV', 'S_result.REFCELLS = S_return.REFCELLS',
            'S_result.EVENTS = S_return.EVENTS', 'S_result.STRINGDATA = S_return.STRINGDATA',
            'S_result.ARRAYS[0:|S_return.ARRAYS|] = S_return.ARRAYS',
        ]
    else:
        checks += [
            '$lookup(S_return.ENV, $ptascii("right")) = (n_replacement)', 'n_replacement =/= n_right',
            '$lookup(S_return.ENV, $ptascii("replacement")) = (n_replacement)',
            '$integer_pointer_select(S_return, pintegeroperation.RIGHT) = (INTEGER_CELL n_replacement)',
            '~$arithmetic_add_selected(S_return, pintegeroperation)',
            'S_return.STORE[n_left] = DEFINED (PINT 99)', 'S_return.STORE[n_right] = DEFINED (PINT 7)',
            'S_return.STORE[n_replacement] = DEFINED pvalue_replacement', '$string_bytes(pvalue_replacement) = ($ptascii("2tail"))',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 1',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_replacement) = 2',
            '$num_pow(pnumber_left, pnumber_right) = (NFLOAT 18442240474082181120, true)',
        ]
        step('S_final_capture', 'S_return')
        checks += [
            '$power_conversion_frontier(S_final_capture, 12)',
            'S_final_capture = S_return[.TODO = (POWER_CONVERSION_DEPRECATED pintegeroperation pnumber_left pnumber_right 0) :: ptask_tail*][.RESULT = KNOWN PNULL]',
            '$power_conversion_deprecated_valid(S_final_capture, pintegeroperation, pnumber_left, pnumber_right, 0)',
            '$task_nodes(POWER_CONVERSION_DEPRECATED pintegeroperation pnumber_left pnumber_right 0) = eps',
        ]
        step('S_final', 'S_final_capture')
        checks += [
            '$power_conversion_frontier(S_final, 13)', 'S_final.TODO = (ERROR_HANDLER_INVOKE perrorcall_final) :: ptask_tail*',
            'perrorcall_final.TARGET = eps', 'perrorcall_final.LEVEL = 8192', 'perrorcall_final.LINE = 25',
            'perrorcall_final.MESSAGE = $ptascii("Power of base 0 and negative exponent is deprecated")',
            'perrorcall_final.RESUME = POWER_CONVERSION_DEPRECATED pintegeroperation pnumber_left pnumber_right 1',
            '$error_call_valid(S_final, perrorcall_final)', '~$arithmetic_add_selected(S_final, pintegeroperation)',
        ]
        seek('S_final_entered', 'S_final', 14)
        checks += ['$power_conversion_entered(S_final_entered.FRAMES, 2)', '$call_descriptors_valid(S_final_entered)', '$heap_valid($heap_graph(S_final_entered))']
        seek('S_final_return', 'S_final_entered', 15)
        checks += [
            'S_final_return.STORE[n_left] = DEFINED (PINT 4)', 'S_final_return.STORE[n_right] = DEFINED (PINT 9)',
            'S_final_return.STORE[n_replacement] = DEFINED pvalue_replacement', 'S_final_return.STORE[n_calls] = DEFINED (PINT 2)',
            'S_final_return.STORE[n_v] = DEFINED (PINT 100)',
            '$power_conversion_deprecated_valid(S_final_return, pintegeroperation, pnumber_left, pnumber_right, 1)',
            '$right_warning_review_diagnostics(S_final_return.EVENTS, "Deprecated") = 1',
            'S_final_return.STRINGDATA[0:|S_return.STRINGDATA|] = S_return.STRINGDATA',
        ]
        step('S_result', 'S_final_return')
        checks += ['S_result = S_final_return[.TODO = ptask_tail*][.RESULT = KNOWN (' + result_value + ')]',
                   '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_replacement) = 2']
    checks += [
        f'~${family}_tasks(S_result.TODO)', '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_right) = ' + ('1' if power else '2'),
        'S_done = $drive_steps(S_result, 5000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_left)', '$lookup(S_done.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_done.ENV, $ptascii("rightAlias")) = (n_right)', 'S_done.STORE[n_left] = DEFINED (PINT 7)',
        'S_done.STORE[n_right] = DEFINED (PINT ' + ('6' if power else '8') + ')',
        '$lookup(S_done.ENV, $ptascii("v")) = (n_done_v)', 'S_done.STORE[n_done_v] = DEFINED (' + result_value + ')',
        'S_done.STORE[n_calls] = DEFINED (PINT ' + ('2' if power else '1') + ')',
        '$right_warning_review_diagnostics(S_done.EVENTS, "Warning") = ' + ('0' if power else '1'),
        '$right_warning_review_diagnostics(S_done.EVENTS, "Deprecated") = ' + ('1' if power else '0'),
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_plan, 0) = S_plan[.COMPLETION = BUDGET]', '$drive_steps(S_plan, 7000) = S_done',
    ]
    if power:
        checks += ['$lookup(S_done.ENV, $ptascii("right")) = (n_replacement)', '$lookup(S_done.ENV, $ptascii("replacement")) = (n_replacement)',
                   'S_done.STORE[n_replacement] = DEFINED (PINT 8)',
                   '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_right) = 1',
                   '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement) = 2']
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
    report['review_scope'] = 'Actual quiet LEFT-to-RIGHT capture without a LEFT Warning; strict cached float68.75, cached-zero DivisionByZeroError and historical signed-zero power Deprecated after RHS-name rebinding; exact atomic effects, alias owners/defaults and one whole/split budget equality'
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
