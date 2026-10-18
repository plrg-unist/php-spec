#!/usr/bin/env python3
"""Copied arithmetic Warning holders and source-authenticated MUL conversion order."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import copied_arithmetic_cases as cases
import plain_arithmetic_protocol as prior

shared = prior.shared
CASES = ('copied-arithmetic-mul-swapped', 'copied-arithmetic-power-deprecated-throw')
HELPERS = prior.HELPERS + r'''
dec $copied_arithmetic_frontier(pstate, nat) : bool
def $copied_arithmetic_frontier(S, 0) = ($arithmetic_copy_plan(S) =/= eps)
def $copied_arithmetic_frontier(S, n) = $plain_arithmetic_frontier(S, n) -- if n =/= 0
dec $copied_arithmetic_seek(pstate, nat, nat) : pstate
def $copied_arithmetic_seek(S, n_stage, n) = S -- if $copied_arithmetic_frontier(S, n_stage)
def $copied_arithmetic_seek(S, n_stage, n) = S
  -- if ~$copied_arithmetic_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $copied_arithmetic_seek(S, n_stage, n) = S
  -- if ~$copied_arithmetic_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $copied_arithmetic_seek(S, n_stage, n) = $copied_arithmetic_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$copied_arithmetic_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def power_conditions(program, path, stdout):
    checks = prior.power_conditions(prior.CASES[2], program, path, stdout)
    result = []
    for check in checks:
        result.append(check.replace('$plain_arithmetic_seek(', '$copied_arithmetic_seek(')
                      .replace('$plain_arithmetic_frontier(', '$copied_arithmetic_frontier(')
                      .replace('$arithmetic_cv_plan(', '$arithmetic_copy_plan(')
                      .replace('pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23', 'pintegeroperation.LEFT = KNOWN pvalue_left')
                      .replace('pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("left"))', 'pintegeroperation.LEFTPOINTER = INTEGER_COPY pvalue_left')
                      .replace('~$arithmetic_cv_warning_valid(S_return, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NINT 0, 0)',
                               '$arithmetic_cv_warning_valid(S_return, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NINT 0, 0)'))
    result += [
        '$arithmetic_copy_valid(S_entry, pintegeroperation)', '$arithmetic_cv_plan(S_entry) = eps', '$arithmetic_mixed_plan(S_entry) = eps',
        '$power_conversion_warning_plan(S_entry) = eps',
        '$integer_slot_rank(S_entry, pintegeroperation.SITE, [PCFIELD 0], pintegeroperation.LEFT) = (2)',
        '$integer_slot_rank(S_entry, pintegeroperation.SITE, [PCFIELD 1], pintegeroperation.RIGHT) = (8)',
        '$arithmetic_cv_pointer(pintegeroperation, ARITHMETIC_LEFT) = pintegeroperation.LEFTPOINTER',
        '$arithmetic_cv_pointer(pintegeroperation, ARITHMETIC_RIGHT (NINT 0)) = pintegeroperation.RIGHTPOINTER',
        '$arithmetic_cv_value(S_return, pintegeroperation.LEFTPOINTER) = (pvalue_left)',
        '$integer_pointer_value(S_return, INTEGER_CV ($ptascii("left"))) = (PINT 99)',
        '$operand_nodes(pintegeroperation.LEFT) = eps', '$operand_nodes(pintegeroperation.RIGHT) = eps',
    ]
    return result


def multiply_conditions(program, path, stdout):
    left = lambda stage: f'ARITHMETIC_CV_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_right (NINT 5) {stage}'
    right = lambda stage: f'ARITHMETIC_CV_WARNING pintegeroperation (ARITHMETIC_RIGHT (NINT 5)) pvalue_copy (NINT 12) {stage}'
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET']

    def seek(state, before, stage):
        checks.extend([f'{state}_found = $copied_arithmetic_seek({before}, {stage}, 5000)',
                       f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
                       f'{state} = {state}_found[.COMPLETION = NORMAL]', f'$copied_arithmetic_frontier({state}, {stage})'])

    def step(state, before):
        checks.extend([f'{state}_budget = $drive_steps({before}, 1)', f'{state}_budget.COMPLETION = BUDGET',
                       f'{state} = {state}_budget[.COMPLETION = NORMAL]'])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$arithmetic_copy_operation(S_entry) = (pintegeroperation)', '$arithmetic_copy_plan(S_entry) = (pintegeroperation)',
        '$arithmetic_copy_valid(S_entry, pintegeroperation)', '$arithmetic_cv_valid(S_entry, pintegeroperation)',
        '$arithmetic_cv_plan(S_entry) = eps', '$arithmetic_mixed_plan(S_entry) = eps', '$submul_warning_plan(S_entry) = eps',
        'pintegeroperation.OP = MULTIPLY', 'pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = KNOWN pvalue_copy', 'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_COPY pvalue_copy', 'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))',
        '$integer_slot_rank(S_entry, pintegeroperation.SITE, [PCFIELD 0], pintegeroperation.LEFT) = (1)',
        '$integer_slot_rank(S_entry, pintegeroperation.SITE, [PCFIELD 1], pintegeroperation.RIGHT) = (8)',
        '$arithmetic_copy_swap(S_entry, pintegeroperation.SITE, MULTIPLY, pintegeroperation.LEFT, pintegeroperation.RIGHT) = (true)',
        '$arithmetic_cv_pointer(pintegeroperation, ARITHMETIC_LEFT) = pintegeroperation.RIGHTPOINTER',
        '$arithmetic_cv_pointer(pintegeroperation, ARITHMETIC_RIGHT (NINT 5)) = pintegeroperation.LEFTPOINTER',
        '$arithmetic_add_pointer(pintegeroperation, ARITHMETIC_LEFT) = pintegeroperation.LEFTPOINTER',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)', '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)', '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'S_entry.STORE[n_left] = DEFINED pvalue_origin', '$string_bytes(pvalue_origin) = ($ptascii("12tail"))',
        '$string_bytes(pvalue_copy) = ($ptascii("12tail"))', 'S_entry.STORE[n_right] = DEFINED pvalue_right',
        '$string_bytes(pvalue_right) = ($ptascii("5tail"))', '$arithmetic_add_conversion(pvalue_right) = ((NINT 5, true))',
        '$arithmetic_add_conversion(pvalue_copy) = ((NINT 12, true))',
        '$operand_nodes(pintegeroperation.LEFT) = eps', '$operand_nodes(pintegeroperation.RIGHT) = eps',
        '$value_nodes(pvalue_copy) = eps', 'S_entry.STORE[n_v] = DEFINED (PINT 100)', 'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '~$arithmetic_copy_valid(S_entry, pintegeroperation[.SWAPPED = false])',
        '~$arithmetic_copy_valid(S_entry, pintegeroperation[.OP = ADD])',
        '~$arithmetic_copy_valid(S_entry, pintegeroperation[.LINE = 24])',
        '~$arithmetic_copy_valid(S_entry[.ORIGIN = eps], pintegeroperation)',
        '~$arithmetic_copy_valid(S_entry, pintegeroperation[.LEFT = KNOWN (PSTRING ($ptascii("13tail")))])',
        '~$arithmetic_copy_pointers(INTEGER_CV ($ptascii("left")), INTEGER_CV ($ptascii("right")))',
        '~$arithmetic_copy_pointers(INTEGER_CELL n_left, INTEGER_CELL n_right)',
        '$arithmetic_cv_value(S_entry, INTEGER_COPY PUNDEFINED) = eps',
        '$arithmetic_cv_value(S_entry, INTEGER_COPY (PARRAY 0)) = eps', '$arithmetic_cv_value(S_entry, INTEGER_COPY (POBJECT 0)) = eps',
        '$arithmetic_cv_value(S_entry, INTEGER_COPY (PINT 9223372036854775808)) = eps',
        '$arithmetic_cv_value(S_entry, INTEGER_COPY (PFLOAT 18446744073709551616)) = eps',
        '$arithmetic_cv_value(S_entry, INTEGER_COPY (PSTRING_CARRIER (REQUEST_STRING (|S_entry.STRINGDATA|)) ($ptascii("bad")))) = eps',
        '$arithmetic_copy_operation(S_entry[.RESULT = REFERENCE n_right]) = eps',
    ]
    step('S_begin', 'S_entry')
    checks += ['S_entry.TODO = ptask_old :: ptask_tail*',
               'S_begin = S_entry[.TODO = (ARITHMETIC_CV_CONVERT pintegeroperation ARITHMETIC_LEFT) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
               '$call_task_valid(S_begin, ARITHMETIC_CV_CONVERT pintegeroperation ARITHMETIC_LEFT)',
               '$task_nodes(ARITHMETIC_CV_CONVERT pintegeroperation ARITHMETIC_LEFT) = eps']
    step('S_capture', 'S_begin')
    checks += ['S_capture = S_begin[.TODO = (' + left(0) + ') :: ptask_tail*]',
               '$arithmetic_cv_warning_valid(S_capture, pintegeroperation, ARITHMETIC_LEFT, pvalue_right, NINT 5, 0)']
    step('S_first', 'S_capture')
    checks += ['$copied_arithmetic_frontier(S_first, 3)', 'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
               'perrorcall_first.RESUME = ' + left(1), 'perrorcall_first.TARGET = eps', 'perrorcall_first.LEVEL = 2', 'perrorcall_first.LINE = 25',
               '$error_call_valid(S_first, perrorcall_first)',
               '~$error_call_valid(S_first, perrorcall_first[.RESUME = ARITHMETIC_CV_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_copy (NINT 12) 1])']
    seek('S_entered', 'S_first', 10)
    checks += ['$plain_arithmetic_entered(S_entered.FRAMES, 0)', '$call_descriptors_valid(S_entered)']
    seek('S_return', 'S_entered', 4)
    checks += ['S_return.TODO = (' + left(1) + ') :: ptask_tail*', 'S_return.STORE[n_left] = DEFINED (PINT 99)',
               'S_return.STORE[n_right] = DEFINED (PINT 7)', 'S_return.STORE[n_calls] = DEFINED (PINT 1)',
               '$arithmetic_cv_warning_valid(S_return, pintegeroperation, ARITHMETIC_LEFT, pvalue_right, NINT 5, 1)',
               '~$arithmetic_cv_warning_valid(S_return, pintegeroperation, ARITHMETIC_LEFT, pvalue_right, NINT 5, 0)',
               '$arithmetic_cv_value(S_return, pintegeroperation.LEFTPOINTER) = (pvalue_copy)',
               'S_return.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA']
    step('S_pending', 'S_return')
    checks += ['S_pending = S_return[.TODO = (ARITHMETIC_CV_CONVERT pintegeroperation (ARITHMETIC_RIGHT (NINT 5))) :: ptask_tail*][.RESULT = KNOWN PNULL]']
    step('S_second_capture', 'S_pending')
    checks += ['S_second_capture = S_pending[.TODO = (' + right(0) + ') :: ptask_tail*]',
               '$arithmetic_cv_fresh(S_second_capture, pintegeroperation, ARITHMETIC_RIGHT (NINT 5), pvalue_copy)']
    step('S_second', 'S_second_capture')
    checks += ['$copied_arithmetic_frontier(S_second, 7)', 'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
               'perrorcall_second.RESUME = ' + right(1), 'perrorcall_second.TARGET = eps', '$error_call_valid(S_second, perrorcall_second)']
    seek('S_second_entered', 'S_second', 11)
    checks += ['$plain_arithmetic_entered(S_second_entered.FRAMES, 1)', '$call_descriptors_valid(S_second_entered)']
    seek('S_late', 'S_second_entered', 8)
    checks += ['S_late.TODO = (' + right(1) + ') :: ptask_tail*', 'S_late.STORE[n_left] = DEFINED (PINT 88)',
               'S_late.STORE[n_right] = DEFINED (PINT 8)', 'S_late.STORE[n_calls] = DEFINED (PINT 2)',
               '$arithmetic_cv_warning_valid(S_late, pintegeroperation, ARITHMETIC_RIGHT (NINT 5), pvalue_copy, NINT 12, 1)',
               '$arithmetic_cv_warning_valid(S_late, pintegeroperation, ARITHMETIC_RIGHT (NINT 5), pvalue_copy, NINT 12, 0)',
               '$arithmetic_cv_value(S_late, pintegeroperation.LEFTPOINTER) = (pvalue_copy)',
               '$arithmetic_cv_value(S_late, pintegeroperation.RIGHTPOINTER) = (PINT 8)']
    step('S_result', 'S_late')
    checks += ['S_result = S_late[.TODO = ptask_tail*][.RESULT = KNOWN (PINT 60)]',
               '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_left) = 1',
               '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_right) = 1',
               '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
               'S_done = $drive_steps(S_result, 5000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
               'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
               'S_done.STORE[n_v] = DEFINED (PINT 60)', 'S_done.STORE[n_calls] = DEFINED (PINT 2)',
               'S_done.STORE[n_left] = DEFINED (PINT 1)', 'S_done.STORE[n_right] = DEFINED (PINT 2)',
               '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
               '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
               '$drive_steps(S_entry, 7000) = S_done', '$drive_steps(S_second, 0) = S_second[.COMPLETION = BUDGET]']
    return checks


def conditions(name, program, path, stdout):
    result = multiply_conditions(program, path, stdout) if name == CASES[0] else power_conditions(program, path, stdout)
    assert len(result) == len(set(result))
    return result


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path, required=True)
    parser.parse_known_args()
    watched = [Path(__file__), Path(cases.__file__), Path(prior.__file__), Path(prior.prior.__file__), Path(shared.__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    shared.cases, shared.CASES, shared.HELPERS, shared.conditions = cases, CASES, HELPERS, conditions
    passed = shared.main()
    assert before == {str(path): digest(path) for path in watched}
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
