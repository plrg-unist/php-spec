#!/usr/bin/env python3
"""Selected ADD repairs retain fractional holders through the old continuations."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import add_repair_cases as cases
import arithmetic_warning_protocol as prior

shared = prior
CASES = ('add-repair-cached-float',)
HELPERS = prior.HELPERS + r'''
dec $add_repair_frame(pframe, nat) : bool
def $add_repair_frame(pframe, 0) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_ADD_WARNING pintegeroperation ARITHMETIC_LEFT pvalue pnumber 1
  -- if perrorcall.TARGET =/= eps
def $add_repair_frame(pframe, 1) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_ADD_WARNING pintegeroperation (ARITHMETIC_RIGHT pnumber_left) pvalue pnumber_right 1
  -- if perrorcall.TARGET =/= eps
def $add_repair_frame(pframe, n) = false -- otherwise
dec $add_repair_entered(pframe*, nat) : bool
def $add_repair_entered(eps, n) = false
def $add_repair_entered(pframe :: pframe_tail*, n) = ($add_repair_frame(pframe, n) \/ $add_repair_entered(pframe_tail*, n))
dec $add_repair_frontier(pstate, nat) : bool
def $add_repair_frontier(S, 0) = ($arithmetic_add_repair_plan(S) =/= eps)
def $add_repair_frontier(S, 10) = (S.CURRENT =/= eps /\ $add_repair_entered(S.FRAMES, 0))
def $add_repair_frontier(S, 11) = (S.CURRENT =/= eps /\ $add_repair_entered(S.FRAMES, 1))
def $add_repair_frontier(S, n) = $arithmetic_frontier(S, n) -- if n =/= 0 /\ n =/= 10 /\ n =/= 11
dec $add_repair_seek(pstate, nat, nat) : pstate
def $add_repair_seek(S, n_stage, n) = S -- if $add_repair_frontier(S, n_stage)
def $add_repair_seek(S, n_stage, n) = S
  -- if ~$add_repair_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $add_repair_seek(S, n_stage, n) = S
  -- if ~$add_repair_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $add_repair_seek(S, n_stage, n) = $add_repair_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$add_repair_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    first = lambda stage: f'ARITHMETIC_ADD_WARNING pintegeroperation ARITHMETIC_LEFT pvalue_left (NFLOAT 4623226492472524800) {stage}'
    second = lambda stage: f'ARITHMETIC_ADD_WARNING pintegeroperation (ARITHMETIC_RIGHT (NFLOAT 4623226492472524800)) pvalue_right (NFLOAT 4617878467915022336) {stage}'
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET']

    def seek(state, before, stage):
        checks.extend([f'{state}_found = $add_repair_seek({before}, {stage}, 5000)',
                       f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
                       f'{state} = {state}_found[.COMPLETION = NORMAL]', f'$add_repair_frontier({state}, {stage})'])

    def step(state, before):
        checks.extend([f'{state}_budget = $drive_steps({before}, 1)', f'{state}_budget.COMPLETION = BUDGET',
                       f'{state} = {state}_budget[.COMPLETION = NORMAL]'])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$arithmetic_add_repair_plan(S_entry) = (pintegeroperation)', '$arithmetic_add_plan(S_entry) = eps',
        '$arithmetic_add_valid(S_entry, pintegeroperation)', '$arithmetic_add_selected(S_entry, pintegeroperation)',
        'pintegeroperation.OP = ADD', '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = 25',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23', 'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_left', 'pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_right',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)', '$lookup(S_entry.ENV, $ptascii("leftAlias")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)', '$lookup(S_entry.ENV, $ptascii("rightAlias")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)', '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'S_entry.STORE[n_left] = DEFINED pvalue_left',
        'pvalue_left = PSTRING_CARRIER (REQUEST_STRING n_left_string) ($ptascii("12.5tail"))',
        'S_entry.STORE[n_right] = DEFINED pvalue_bad',
        'pvalue_bad = PSTRING_CARRIER (REQUEST_STRING n_right_string) ($ptascii("bad5"))',
        '$arithmetic_add_conversion(pvalue_left) = ((NFLOAT 4623226492472524800, true))', '$arithmetic_add_conversion(pvalue_bad) = eps',
        '$arithmetic_owned_cell_valid(S_entry, n_left)', '$arithmetic_owned_cell_valid(S_entry, n_right)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 2',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', 'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$arithmetic_add_repair_plan(S_entry[.ORIGIN = eps]) = eps',
        '$arithmetic_add_repair_plan(S_entry[.STRINGDATA = eps]) = eps',
        '$arithmetic_add_repair_plan(S_entry[.ERRORHANDLER.CALLBACK = eps]) = eps',
        '$arithmetic_add_repair_plan(S_entry[.REFCELLS = eps]) = eps',
        '$arithmetic_add_repair_plan(S_entry[.STORE[n_right] = UNDEFINED]) = eps',
        '$arithmetic_add_repair_plan(S_entry[.STORE[n_right] = DEFINED (PINT 5)]) = eps',
        '$arithmetic_add_plan(S_entry[.STORE[n_right] = DEFINED (PINT 5)]) =/= eps',
        '~$submul_initial_value(S_entry, PUNDEFINED)', '~$submul_initial_value(S_entry, PARRAY 0)',
        '~$submul_initial_value(S_entry, POBJECT 0)',
        '$arithmetic_add_failure_operands(S_entry, pintegeroperation, ARITHMETIC_LEFT) = eps',
        'S_entry.TODO = ptask_old :: ptask_tail*',
        '$arithmetic_add_repair_plan(S_entry[.TODO = (BINARY_RIGHT DIVIDE pintegeroperation.LEFT 25) :: ptask_tail*]) = eps',
        '$arithmetic_add_repair_plan(S_entry[.TODO = (BINARY_RIGHT ADD pintegeroperation.LEFT 26) :: ptask_tail*]) = eps',
        'PhpStep: S_entry ~> S_begin',
        'S_begin = S_entry[.TODO = (ARITHMETIC_ADD_CONVERT pintegeroperation ARITHMETIC_LEFT) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$call_task_valid(S_begin, ARITHMETIC_ADD_CONVERT pintegeroperation ARITHMETIC_LEFT)',
        '$task_nodes(ARITHMETIC_ADD_CONVERT pintegeroperation ARITHMETIC_LEFT) = eps',
    ]
    step('S_capture', 'S_begin')
    checks += ['S_capture = S_begin[.TODO = (' + first(0) + ') :: ptask_tail*]',
               '$arithmetic_add_warning_valid(S_capture, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NFLOAT 4623226492472524800, 0)',
               '~$arithmetic_add_warning_valid(S_capture, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NINT 13, 0)',
               '~$arithmetic_add_valid(S_capture, pintegeroperation[.LINE = 24])']
    step('S_first', 'S_capture')
    checks += ['$arithmetic_frontier(S_first, 3)', 'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
               'perrorcall_first.RESUME = ' + first(1), 'perrorcall_first.TARGET = eps',
               'perrorcall_first.LEVEL = 2', 'perrorcall_first.LINE = 25', '$error_call_valid(S_first, perrorcall_first)',
               '~$error_call_valid(S_first, perrorcall_first[.RESUME = ARITHMETIC_ADD_WARNING pintegeroperation ARITHMETIC_LEFT (PSTRING ($ptascii("99tail"))) (NINT 99) 1])']
    seek('S_entered', 'S_first', 10)
    checks += ['$add_repair_entered(S_entered.FRAMES, 0)', '$call_descriptors_valid(S_entered)']
    seek('S_return', 'S_entered', 4)
    checks += ['S_return.TODO = (' + first(1) + ') :: ptask_tail*',
               'S_return.STORE[n_left] = DEFINED (PINT 99)', 'S_return.STORE[n_right] = DEFINED pvalue_right',
               '$string_bytes(pvalue_right) = ($ptascii("5.5tail"))',
               'S_return.STORE[n_calls] = DEFINED (PINT 1)', 'S_return.STORE[n_v] = DEFINED (PINT 100)',
               '$arithmetic_add_warning_valid(S_return, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NFLOAT 4623226492472524800, 1)',
               '~$arithmetic_add_warning_valid(S_return, pintegeroperation, ARITHMETIC_LEFT, pvalue_left, NFLOAT 4623226492472524800, 0)',
               'S_return.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA']
    step('S_pending', 'S_return')
    checks += ['S_pending = S_return[.TODO = (ARITHMETIC_ADD_CONVERT pintegeroperation (ARITHMETIC_RIGHT (NFLOAT 4623226492472524800))) :: ptask_tail*][.RESULT = KNOWN PNULL]',
               '$arithmetic_add_failure_operands(S_pending, pintegeroperation, ARITHMETIC_RIGHT (NFLOAT 4623226492472524800)) = eps']
    step('S_second_capture', 'S_pending')
    checks += ['S_second_capture = S_pending[.TODO = (' + second(0) + ') :: ptask_tail*]']
    step('S_second', 'S_second_capture')
    checks += ['$arithmetic_frontier(S_second, 7)', 'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
               'perrorcall_second.RESUME = ' + second(1), 'perrorcall_second.TARGET = eps',
               'perrorcall_second.LEVEL = 2', 'perrorcall_second.LINE = 25', '$error_call_valid(S_second, perrorcall_second)']
    seek('S_second_entered', 'S_second', 11)
    checks += ['$add_repair_entered(S_second_entered.FRAMES, 1)', '$call_descriptors_valid(S_second_entered)']
    seek('S_late', 'S_second_entered', 8)
    checks += ['S_late.TODO = (' + second(1) + ') :: ptask_tail*',
               'S_late.STORE[n_left] = DEFINED (PBOOL false)', 'S_late.STORE[n_right] = DEFINED (PINT 7)',
               'S_late.STORE[n_calls] = DEFINED (PINT 2)', 'S_late.STORE[n_v] = DEFINED (PINT 100)',
               '$arithmetic_add_warning_valid(S_late, pintegeroperation, ARITHMETIC_RIGHT (NFLOAT 4623226492472524800), pvalue_right, NFLOAT 4617878467915022336, 1)',
               '~$arithmetic_add_warning_valid(S_late, pintegeroperation, ARITHMETIC_RIGHT (NFLOAT 4623226492472524800), pvalue_right, NFLOAT 4617878467915022336, 0)',
               'S_late.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
               'PhpStep: S_late ~> S_atomic',
               'S_atomic = S_late[.TODO = ptask_tail*][.RESULT = KNOWN (PFLOAT 4625759767262920704)]']
    step('S_result', 'S_late')
    checks += ['S_result.RESULT = KNOWN (PFLOAT 4625759767262920704)', 'S_result.TODO = ptask_tail*',
               'S_result.STORE = S_late.STORE', 'S_result.ENV = S_late.ENV', 'S_result.REFCELLS = S_late.REFCELLS',
               'S_result.EVENTS = S_late.EVENTS', 'S_result.STRINGDATA = S_late.STRINGDATA',
               '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_left) = 2',
               '$heap_owners($heap_prune($heap_graph(S_result)), HCELL n_right) = 2',
               'S_done = $drive_steps(S_result, 5000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
               'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
               'S_done.STORE[n_v] = DEFINED (PFLOAT 4625759767262920704)', 'S_done.STORE[n_calls] = DEFINED (PINT 2)',
               'S_done.STORE[n_left] = DEFINED (PINT 1)', 'S_done.STORE[n_right] = DEFINED (PINT 2)',
               '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
               '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
               '$drive_steps(S_entry, 6000) = S_done', '$drive_steps(S_first, 0) = S_first[.COMPLETION = BUDGET]']
    assert len(checks) == len(set(checks))
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path, required=True)
    parser.parse_known_args()
    watched = [Path(__file__), Path(cases.__file__), Path(prior.__file__), Path(prior.runner.__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    shared.cases, shared.CASES, shared.HELPERS, shared.conditions = cases, CASES, HELPERS, conditions
    passed = shared.main()
    assert before == {str(path): digest(path) for path in watched}
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
