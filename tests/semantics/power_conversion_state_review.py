#!/usr/bin/env python3
"""Reached power holders, live failure types, and historical signed zero."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import power_conversion_review_cases as cases
import power_conversion_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = r'''
dec $power_conversion_review_diagnostic(pevent, text) : nat
def $power_conversion_review_diagnostic(DIAGNOSTIC text n* z, text) = 1
def $power_conversion_review_diagnostic(DIAGNOSTIC_SOURCE n_source text n* z, text) = 1
def $power_conversion_review_diagnostic(DIAGNOSTIC_STACK text n* z n_trace*, text) = 1
def $power_conversion_review_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n* z n_trace*, text) = 1
def $power_conversion_review_diagnostic(pevent, text) = 0 -- otherwise
dec $power_conversion_review_diagnostics(pevent*, text) : nat
def $power_conversion_review_diagnostics(eps, text) = 0
def $power_conversion_review_diagnostics(pevent :: pevent_tail*, text) = $($power_conversion_review_diagnostic(pevent, text) + $power_conversion_review_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    fractional = name == CASES[0]
    failure = name == CASES[1]
    rebound = name == CASES[2]
    operator = 'POWER'
    initial_text = '4.0tail' if fractional else ('-0.0tail' if rebound else '2tail')
    right_text = '0.5tail' if fractional else '-3tail'
    left_number = 'NFLOAT 4616189618054758400' if fractional else ('NFLOAT 9223372036854775808' if rebound else 'NINT 2')
    right_number = 'NFLOAT 4602678819172646912' if fractional else 'NINT (-3)'
    result_value = 'PFLOAT 4611686018427387904' if fractional else 'PFLOAT 18442240474082181120'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_plan_found = $power_conversion_seek(S_initial, 0, 5000)',
        r'S_plan_found.COMPLETION = NORMAL \/ S_plan_found.COMPLETION = BUDGET',
        'S_plan = S_plan_found[.COMPLETION = NORMAL]', '$power_conversion_frontier(S_plan, 0)',
        '$power_conversion_warning_plan(S_plan) = (pintegeroperation)',
        '$power_conversion_valid(S_plan, pintegeroperation)', '$arithmetic_add_selected(S_plan, pintegeroperation)',
        '$power_warning_plan(S_plan) = eps',
        'pintegeroperation.OP = ' + operator, '~pintegeroperation.SWAPPED',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LINE = 25', 'S_plan.ORIGIN = (pintegeroperation.SITE)',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_left',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_right', 'n_left =/= n_right',
        '$lookup(S_plan.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_plan.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_plan.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_plan.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_plan.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_plan.ENV, $ptascii("calls")) = (n_calls)',
        'n_left <- S_plan.REFCELLS', 'n_right <- S_plan.REFCELLS',
        'S_plan.STORE[n_left] = DEFINED pvalue_left',
        '$string_bytes(pvalue_left) = ($ptascii("' + initial_text + '"))',
        'S_plan.STORE[n_right] = DEFINED pvalue_initial_right',
        '$string_bytes(pvalue_initial_right) = ($ptascii("bad"))',
        '$arithmetic_add_conversion(pvalue_initial_right) = eps',
        'pnumber_left = ' + left_number,
        '$arithmetic_add_conversion(pvalue_left) = ((pnumber_left, true))',
        'S_plan.STORE[n_v] = DEFINED (PINT 100)', 'S_plan.STORE[n_calls] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_plan)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_plan)), HCELL n_right) = 2',
        '$call_descriptors_valid(S_plan)', '$heap_valid($heap_graph(S_plan))',
        'S_capture_found = $power_conversion_seek(S_plan, 2, 100)',
        r'S_capture_found.COMPLETION = NORMAL \/ S_capture_found.COMPLETION = BUDGET',
        'S_capture = S_capture_found[.COMPLETION = NORMAL]', '$power_conversion_frontier(S_capture, 2)',
        'S_capture.TODO = (POWER_CONVERSION_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_left pnumber_left 0) :: ptask_tail*',
        '$power_conversion_warning_valid(S_capture, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, pnumber_left, 0)',
        '$task_nodes(POWER_CONVERSION_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_left pnumber_left 0) = eps',
        'S_capture.STORE = S_plan.STORE', 'S_capture.ALLOCATIONS = S_plan.ALLOCATIONS',
        'S_first_budget = $drive_steps(S_capture, 1)', 'S_first_budget.COMPLETION = BUDGET',
        'S_first = S_first_budget[.COMPLETION = NORMAL]', '$power_conversion_frontier(S_first, 3)',
        'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
        'perrorcall_first.RESUME = POWER_CONVERSION_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_left pnumber_left 1',
        'perrorcall_first.TARGET = eps', 'perrorcall_first.LEVEL = 2', 'perrorcall_first.LINE = 25',
        'perrorcall_first.MESSAGE = $ptascii("A non-numeric value encountered")',
        '$error_call_valid(S_first, perrorcall_first)', '$call_descriptors_valid(S_first)',
        'S_entered_found = $power_conversion_seek(S_first, 10, 4000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', '$power_conversion_entered(S_entered.FRAMES, 0)',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
        'S_left_found = $power_conversion_seek(S_entered, 4, 4000)',
        r'S_left_found.COMPLETION = NORMAL \/ S_left_found.COMPLETION = BUDGET',
        'S_left = S_left_found[.COMPLETION = NORMAL]', '$power_conversion_frontier(S_left, 4)',
        'S_left.TODO = (POWER_CONVERSION_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_left pnumber_left 1) :: ptask_tail*',
        '$power_conversion_warning_valid(S_left, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, pnumber_left, 1)',
        '~$power_conversion_warning_valid(S_left, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, pnumber_left, 0)',
        'S_left.STORE[n_calls] = DEFINED (PINT 1)', 'S_left.STORE[n_v] = DEFINED (PINT 100)',
        'S_left.STRINGDATA[0:|S_capture.STRINGDATA|] = S_capture.STRINGDATA',
        '$call_descriptors_valid(S_left)', '$heap_valid($heap_graph(S_left))',
        'S_right_budget = $drive_steps(S_left, 1)', 'S_right_budget.COMPLETION = BUDGET',
        'S_right = S_right_budget[.COMPLETION = NORMAL]', '$power_conversion_frontier(S_right, 5)',
        'S_right.TODO = (POWER_CONVERT pintegeroperation (ARITHMETIC_RIGHT pnumber_left)) :: ptask_tail*',
        '$task_nodes(POWER_CONVERT pintegeroperation (ARITHMETIC_RIGHT pnumber_left)) = eps',
        'S_right.STORE = S_left.STORE', 'S_right.ENV = S_left.ENV',
        '$call_descriptors_valid(S_right)', '$heap_valid($heap_graph(S_right))',
    ]
    if fractional:
        checks += [
            '~$power_conversion_valid(S_plan, pintegeroperation[.OP = SUBTRACT])',
            '~$power_conversion_valid(S_plan, pintegeroperation[.SWAPPED = true])',
            '~$power_conversion_valid(S_plan, pintegeroperation[.LINE = 26])',
            '~$power_conversion_valid(S_plan, pintegeroperation[.LEFTPOINTER = INTEGER_CV ($ptascii("left"))])',
            '~$power_conversion_valid(S_plan[.ORIGIN = eps], pintegeroperation)',
            '~$power_conversion_valid(S_plan[.CODE = eps], pintegeroperation)',
            '~$power_conversion_warning_valid(S_capture, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NINT 12, 0)',
            '~$power_conversion_warning_valid(S_capture, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, pnumber_left, 2)',
            '~$error_call_valid(S_first, perrorcall_first[.LEVEL = 8192])',
            '~$error_call_valid(S_first, perrorcall_first[.RESUME = POWER_CONVERSION_WARNING pintegeroperation ARITHMETIC_LEFT (PSTRING ($ptascii("13.5tail"))) (NFLOAT 4623789442425946112) 1])',
        ]
    if failure:
        checks += [
            'S_left.STORE[n_left] = DEFINED (PBOOL false)',
            'S_left.STORE[n_right] = DEFINED pvalue_initial_right',
            '$power_conversion_review_diagnostics(S_left.EVENTS, "Warning") = 1',
            '$power_conversion_failure_operands(S_right, pintegeroperation, ARITHMETIC_RIGHT pnumber_left) = ((PBOOL false, pvalue_initial_right))',
            '$power_conversion_failure_operands(S_right, pintegeroperation, ARITHMETIC_LEFT) = eps',
            'S_result_budget = $drive_steps(S_right, 1)', 'S_result_budget.COMPLETION = BUDGET',
            'S_result = S_result_budget[.COMPLETION = NORMAL]', '$power_conversion_frontier(S_result, 9)',
            'S_result.TODO = (THROW_SEARCH n_error) :: ptask_tail*', 'S_result.RESULT = KNOWN PNULL',
            'S_result.CURRENT = eps', 'n_error = |S_right.OBJECTS|',
            'S_result.OBJECTS[n_error] = THROWABLE pthrowable',
            'S_result.OBJECTS = S_right.OBJECTS ++ [THROWABLE pthrowable]',
            'pthrowable.KIND = "TypeError"', 'pthrowable.ORIGIN = (pintegeroperation.SITE)',
            '$throwable_field(S_result, n_error, "line") = PINT 25',
            '$string_bytes($throwable_field(S_result, n_error, "message")) = ($ptascii("Unsupported operand types: bool ** string"))',
            '$throwable_previous_id(S_result, n_error) = eps', '$throwable_live(S_result, n_error)',
            '$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]',
            '$heap_owners($heap_prune($heap_graph(S_result)), HOBJECT n_error) = 1',
            'S_result.STORE = S_right.STORE', 'S_result.ENV = S_right.ENV',
            'S_result.REFCELLS = S_right.REFCELLS', 'S_result.EVENTS = S_right.EVENTS',
            'S_result.STRINGDATA = S_right.STRINGDATA',
            'S_result.ARRAYS[0:|S_right.ARRAYS|] = S_right.ARRAYS',
            '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_left) = 2',
            '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_right) = 2',
        ]
    else:
        checks += [
            'S_left.STORE[n_left] = DEFINED (PINT 99)',
            'S_left.STORE[n_right] = DEFINED pvalue_right',
            '$string_bytes(pvalue_right) = ($ptascii("' + right_text + '"))',
            'pnumber_right = ' + right_number,
            '$arithmetic_add_conversion(pvalue_right) = ((pnumber_right, true))',
            '$power_conversion_review_diagnostics(S_left.EVENTS, "Warning") = 0',
            'S_second_capture_budget = $drive_steps(S_right, 1)', 'S_second_capture_budget.COMPLETION = BUDGET',
            'S_second_capture = S_second_capture_budget[.COMPLETION = NORMAL]', '$power_conversion_frontier(S_second_capture, 6)',
            'S_second_capture.TODO = (POWER_CONVERSION_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue_right pnumber_right 0) :: ptask_tail*',
            '$power_conversion_warning_valid(S_second_capture, pintegeroperation, ARITHMETIC_RIGHT pnumber_left, pvalue_right, pnumber_right, 0)',
            'S_second_budget = $drive_steps(S_second_capture, 1)', 'S_second_budget.COMPLETION = BUDGET',
            'S_second = S_second_budget[.COMPLETION = NORMAL]', '$power_conversion_frontier(S_second, 7)',
            'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
            'perrorcall_second.TARGET = eps', 'perrorcall_second.LEVEL = 2', 'perrorcall_second.LINE = 25',
            'perrorcall_second.RESUME = POWER_CONVERSION_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue_right pnumber_right 1',
            '$error_call_valid(S_second, perrorcall_second)', '$call_descriptors_valid(S_second)',
            '~$error_call_valid(S_second, perrorcall_second[.RESUME = POWER_CONVERSION_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) (PSTRING ($ptascii("6tail"))) (NINT 6) 1])',
            'S_second_entered_found = $power_conversion_seek(S_second, 11, 4000)',
            r'S_second_entered_found.COMPLETION = NORMAL \/ S_second_entered_found.COMPLETION = BUDGET',
            'S_second_entered = S_second_entered_found[.COMPLETION = NORMAL]', '$power_conversion_entered(S_second_entered.FRAMES, 1)',
            '$call_descriptors_valid(S_second_entered)', '$heap_valid($heap_graph(S_second_entered))',
            'S_return_found = $power_conversion_seek(S_second_entered, 8, 4000)',
            r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
            'S_return = S_return_found[.COMPLETION = NORMAL]', '$power_conversion_frontier(S_return, 8)',
            'S_return.TODO = (POWER_CONVERSION_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue_right pnumber_right 1) :: ptask_tail*',
            '$power_conversion_warning_valid(S_return, pintegeroperation, ARITHMETIC_RIGHT pnumber_left, pvalue_right, pnumber_right, 1)',
            '~$power_conversion_warning_valid(S_return, pintegeroperation, ARITHMETIC_RIGHT pnumber_left, pvalue_right, pnumber_right, 0)',
            'S_return.STORE[n_calls] = DEFINED (PINT 2)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
            '$power_conversion_review_diagnostics(S_return.EVENTS, "Warning") = ' + ('0' if rebound else '1'),
            'S_return.STRINGDATA[0:|S_left.STRINGDATA|] = S_left.STRINGDATA',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        ]
        if fractional:
            checks += [
                'S_result_budget = $drive_steps(S_return, 1)', 'S_result_budget.COMPLETION = BUDGET',
                'S_result = S_result_budget[.COMPLETION = NORMAL]',
                'S_result.RESULT = KNOWN (' + result_value + ')', 'S_result.TODO = ptask_tail*',
                'S_result = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (' + result_value + ')]',
                'S_return.STORE[n_left] = DEFINED (PBOOL false)',
                'S_return.STORE[n_right] = DEFINED pvalue_bad', '$string_bytes(pvalue_bad) = ($ptascii("bad"))',
                '$power_conversion_failure_operands(S_return, pintegeroperation, ARITHMETIC_RIGHT pnumber_left) = ((PBOOL false, pvalue_bad))',
                '$num_pow(pnumber_left, pnumber_right) = (NFLOAT 4611686018427387904, false)',
                '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_left) = 2',
                '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_right) = 2',
            ]
        if rebound:
            checks += [
                '$lookup(S_left.ENV, $ptascii("right")) = (n_replacement)', 'n_replacement =/= n_right',
                '$lookup(S_left.ENV, $ptascii("replacement")) = (n_replacement)',
                '$lookup(S_left.ENV, $ptascii("rightAlias")) = (n_right)',
                '$integer_pointer_select(S_left, pintegeroperation.RIGHT) = (INTEGER_CELL n_replacement)',
                '~$arithmetic_add_selected(S_left, pintegeroperation)',
                '$heap_owners($heap_prune($heap_graph(S_left)), HCELL n_right) = 1',
                '$heap_owners($heap_prune($heap_graph(S_left)), HCELL n_replacement) = 2',
                '$lookup(S_return.ENV, $ptascii("right")) = (n_replacement)',
                'S_return.STORE[n_replacement] = DEFINED pvalue_replacement',
                '$string_bytes(pvalue_replacement) = ($ptascii("2tail"))',
                'S_return.STORE[n_left] = DEFINED (PINT 88)', 'S_return.STORE[n_right] = DEFINED (PINT 7)',
                '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_left) = 2',
                '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 1',
                '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_replacement) = 2',
            ]
            checks += [
                '$num_pow(pnumber_left, pnumber_right) = (NFLOAT 18442240474082181120, true)',
                'S_final_capture_budget = $drive_steps(S_return, 1)', 'S_final_capture_budget.COMPLETION = BUDGET',
                'S_final_capture = S_final_capture_budget[.COMPLETION = NORMAL]', '$power_conversion_frontier(S_final_capture, 12)',
                'S_final_capture = S_return[.TODO = (POWER_CONVERSION_DEPRECATED pintegeroperation pnumber_left pnumber_right 0) :: ptask_tail*][.RESULT = KNOWN PNULL]',
                '$power_conversion_deprecated_valid(S_final_capture, pintegeroperation, pnumber_left, pnumber_right, 0)',
                '$task_nodes(POWER_CONVERSION_DEPRECATED pintegeroperation pnumber_left pnumber_right 0) = eps',
                '~$power_conversion_deprecated_valid(S_final_capture, pintegeroperation, pnumber_left, NINT 3, 0)',
                '~$power_conversion_deprecated_valid(S_final_capture, pintegeroperation, pnumber_left, pnumber_right, 2)',
                '~$power_conversion_deprecated_valid(S_final_capture, pintegeroperation, NFLOAT 18446744073709551616, pnumber_right, 0)',
                'S_final_budget = $drive_steps(S_final_capture, 1)', 'S_final_budget.COMPLETION = BUDGET',
                'S_final = S_final_budget[.COMPLETION = NORMAL]', '$power_conversion_frontier(S_final, 13)',
                'S_final.TODO = (ERROR_HANDLER_INVOKE perrorcall_final) :: ptask_tail*',
                'perrorcall_final.TARGET = eps', 'perrorcall_final.LINE = 25', 'perrorcall_final.LEVEL = 8192',
                'perrorcall_final.MESSAGE = $ptascii("Power of base 0 and negative exponent is deprecated")',
                'perrorcall_final.RESUME = POWER_CONVERSION_DEPRECATED pintegeroperation pnumber_left pnumber_right 1',
                '$error_call_valid(S_final, perrorcall_final)', '$call_descriptors_valid(S_final)',
                'S_final.STORE[n_left] = DEFINED (PINT 88)', 'S_final.STORE[n_right] = DEFINED (PINT 7)',
                '$lookup(S_final.ENV, $ptascii("right")) = (n_replacement)',
                '~$arithmetic_add_selected(S_final, pintegeroperation)',
                '~$error_call_valid(S_final, perrorcall_final[.LEVEL = 2])',
                '~$error_call_valid(S_final, perrorcall_final[.LINE = 24])',
                '~$error_call_valid(S_final, perrorcall_final[.RESUME = POWER_CONVERSION_DEPRECATED pintegeroperation pnumber_left (NINT 3) 1])',
                'S_final_entered_found = $power_conversion_seek(S_final, 14, 4000)',
                r'S_final_entered_found.COMPLETION = NORMAL \/ S_final_entered_found.COMPLETION = BUDGET',
                'S_final_entered = S_final_entered_found[.COMPLETION = NORMAL]', '$power_conversion_entered(S_final_entered.FRAMES, 2)',
                '$call_descriptors_valid(S_final_entered)', '$heap_valid($heap_graph(S_final_entered))',
                'S_final_return_found = $power_conversion_seek(S_final_entered, 15, 4000)',
                r'S_final_return_found.COMPLETION = NORMAL \/ S_final_return_found.COMPLETION = BUDGET',
                'S_final_return = S_final_return_found[.COMPLETION = NORMAL]', '$power_conversion_frontier(S_final_return, 15)',
                'S_final_return.TODO = (POWER_CONVERSION_DEPRECATED pintegeroperation pnumber_left pnumber_right 1) :: ptask_tail*',
                '$power_conversion_deprecated_valid(S_final_return, pintegeroperation, pnumber_left, pnumber_right, 1)',
                'S_final_return.STORE[n_left] = DEFINED (PINT 4)', 'S_final_return.STORE[n_right] = DEFINED (PINT 9)',
                'S_final_return.STORE[n_calls] = DEFINED (PINT 3)', 'S_final_return.STORE[n_v] = DEFINED (PINT 100)',
                'S_final_return.STORE[n_replacement] = DEFINED pvalue_replacement',
                '$power_conversion_review_diagnostics(S_final_return.EVENTS, "Warning") = 0',
                '$power_conversion_review_diagnostics(S_final_return.EVENTS, "Deprecated") = 1',
                'S_final_return.STRINGDATA[0:|S_return.STRINGDATA|] = S_return.STRINGDATA',
                '$call_descriptors_valid(S_final_return)', '$heap_valid($heap_graph(S_final_return))',
                'S_result_budget = $drive_steps(S_final_return, 1)', 'S_result_budget.COMPLETION = BUDGET',
                'S_result = S_result_budget[.COMPLETION = NORMAL]',
                'S_result = S_final_return[.TODO = ptask_tail*][.RESULT = KNOWN (' + result_value + ')]',
                '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_left) = 2',
                '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_right) = 1',
                '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_replacement) = 2',
            ]
    checks += [
        '~$power_conversion_tasks(S_result.TODO)', '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 5000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_done.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_done.ENV, $ptascii("rightAlias")) = (n_right)',
        'S_done.STORE[n_left] = DEFINED (PINT 7)',
        'S_done.STORE[n_right] = DEFINED (PINT ' + ('6' if rebound else '8') + ')',
        '$lookup(S_done.ENV, $ptascii("v")) = (n_done_v)',
        'S_done.STORE[n_done_v] = DEFINED (' + ('PINT 100' if failure else result_value) + ')',
        'S_done.STORE[n_calls] = DEFINED (PINT ' + ('1' if failure else ('3' if rebound else '2')) + ')',
        '$power_conversion_review_diagnostics(S_done.EVENTS, "Warning") = ' + ('0' if rebound else '1'),
        '$power_conversion_review_diagnostics(S_done.EVENTS, "Deprecated") = ' + ('1' if rebound else '0'),
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_plan, 0) = S_plan[.COMPLETION = BUDGET]',
        '$drive_steps(S_plan, 8000) = S_done',
    ]
    if rebound:
        checks += [
            '$lookup(S_done.ENV, $ptascii("right")) = (n_replacement)',
            '$lookup(S_done.ENV, $ptascii("replacement")) = (n_replacement)',
            'S_done.STORE[n_replacement] = DEFINED (PINT 8)',
            '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_right) = 1',
            '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_replacement) = 2',
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
    report['review_scope'] = 'Reached power holders produce strict float2.0 after poisoning; live bool/string failure; negative-zero and selected old RIGHT survive rebinding and a final default Deprecated with historical holders, exact atomic results or TypeError, owners and one whole/split budget equality'
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
