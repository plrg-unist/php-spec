#!/usr/bin/env python3
"""Quiet ternary-copy power reaches the existing final diagnostic continuation."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import quiet_power_copy_cases as cases
import plain_arithmetic_protocol as prior

shared = prior.shared
CASES = ('quiet-power-copy-throw',)
HELPERS = prior.HELPERS + r'''
dec $quiet_power_copy_frontier(pstate, nat) : bool
def $quiet_power_copy_frontier(S, 0) = ($quiet_power_copy_plan(S) =/= eps)
def $quiet_power_copy_frontier(S, n) = $plain_arithmetic_frontier(S, n) -- if n =/= 0
dec $quiet_power_copy_seek(pstate, nat, nat) : pstate
def $quiet_power_copy_seek(S, n_stage, n) = S -- if $quiet_power_copy_frontier(S, n_stage)
def $quiet_power_copy_seek(S, n_stage, n) = S
  -- if ~$quiet_power_copy_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $quiet_power_copy_seek(S, n_stage, n) = S
  -- if ~$quiet_power_copy_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $quiet_power_copy_seek(S, n_stage, n) = $quiet_power_copy_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$quiet_power_copy_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    marker = lambda stage: f'ARITHMETIC_CV_DEPRECATED pintegeroperation (NFLOAT 0) (NINT (-2)) {stage}'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $quiet_power_copy_seek({before}, {stage}, 5000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$quiet_power_copy_frontier({state}, {stage})',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$quiet_power_copy_plan(S_entry) = ((pintegeroperation, NFLOAT 0, NINT (-2)))',
        '$arithmetic_copy_valid(S_entry, pintegeroperation)', '$arithmetic_cv_valid(S_entry, pintegeroperation)',
        '$arithmetic_copy_plan(S_entry) = eps', '$arithmetic_cv_plan(S_entry) = eps',
        '$power_warning_plan(S_entry) = eps', '$power_conversion_warning_plan(S_entry) = eps',
        '$error_handler_eligible(S_entry, 8192)', '~$error_handler_eligible(S_entry, 2)',
        '$arithmetic_add_named(S_entry)', 'pintegeroperation.OP = POWER', '~pintegeroperation.SWAPPED',
        'pintegeroperation.LINE = 25', 'pintegeroperation.LEFT = KNOWN pvalue_left',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LEFTPOINTER = INTEGER_COPY pvalue_left',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("right"))',
        '$integer_slot_rank(S_entry, pintegeroperation.SITE, [PCFIELD 0], pintegeroperation.LEFT) = (2)',
        '$integer_slot_rank(S_entry, pintegeroperation.SITE, [PCFIELD 1], pintegeroperation.RIGHT) = (8)',
        '$operand_nodes(pintegeroperation.LEFT) = eps', '$operand_nodes(pintegeroperation.RIGHT) = eps',
        'pvalue_left = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("0.0"))',
        'S_entry.STRINGDATA[n_string] = $ptascii("0.0")', '$string_carrier_valid(S_entry, pvalue_left)',
        '$arithmetic_add_conversion(pvalue_left) = ((NFLOAT 0, false))',
        '$arithmetic_add_conversion(PINT (-2)) = ((NINT (-2), false))',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("supplied")) = (n_supplied_cell)',
        'S_entry.STORE[n_supplied_cell] = DEFINED (POBJECT n_supplied)',
        'S_entry.STORE[n_left] = DEFINED pvalue_left', 'S_entry.STORE[n_right] = DEFINED (PINT (-2))',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', 'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '~(n_left <- S_entry.REFCELLS)', '~(n_right <- S_entry.REFCELLS)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 1',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HOBJECT n_supplied) = 1',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$quiet_power_copy_plan(S_entry[.ORIGIN = eps]) = eps',
        '$quiet_power_copy_plan(S_entry[.STRINGDATA = eps]) = eps',
        'S_entry.TODO = ptask_old :: ptask_tail*',
        '$quiet_power_copy_plan(S_entry[.TODO = (BINARY_RIGHT ADD (KNOWN pvalue_left) 25) :: ptask_tail*]) = eps',
        '$quiet_power_copy_plan(S_entry[.TODO = (BINARY_RIGHT POWER (KNOWN pvalue_left) 26) :: ptask_tail*]) = eps',
        '$quiet_power_copy_plan(S_entry[.TODO = (BINARY_RIGHT POWER (VARIABLE ($ptascii("left")) 23) 25) :: ptask_tail*]) = eps',
        '$quiet_power_copy_plan(S_entry[.RESULT = KNOWN (PINT (-2))]) = eps',
        '$quiet_power_copy_plan(S_entry[.STORE[n_right] = UNDEFINED]) = eps',
        '$quiet_power_copy_plan(S_entry[.REFCELLS = [n_right]]) = eps',
        '$quiet_power_copy_plan(S_entry[.ERRORHANDLER.CALLBACK = eps]) = eps',
        '$quiet_power_copy_plan(S_entry[.STORE[n_right] = DEFINED (PINT 2)]) = eps',
        '$quiet_power_copy_plan(S_entry[.STORE[n_right] = DEFINED (PSTRING ($ptascii("bad")))]) = eps',
        '$quiet_power_copy_plan(S_entry[.STORE[n_right] = DEFINED (PSTRING ($ptascii("-2tail")))]) = eps',
        '$quiet_power_copy_plan(S_entry[.TODO = (BINARY_RIGHT POWER (KNOWN (PSTRING ($ptascii("0tail")))) 25) :: ptask_tail*]) = eps',
        'PhpStep: S_entry ~> S_begin',
        'S_begin = S_entry[.TODO = (' + marker(0) + ') :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$arithmetic_cv_deprecated_valid(S_begin, pintegeroperation, NFLOAT 0, NINT (-2), 0)',
        '$task_nodes(' + marker(0) + ') = eps', '$call_task_valid(S_begin, ' + marker(0) + ')',
        '$quiet_power_copy_plan(S_begin) = eps',
        '~$arithmetic_cv_deprecated_valid(S_begin, pintegeroperation[.OP = ADD], NFLOAT 0, NINT (-2), 0)',
        '~$arithmetic_cv_deprecated_valid(S_begin, pintegeroperation[.LINE = 24], NFLOAT 0, NINT (-2), 0)',
        '~$arithmetic_cv_deprecated_valid(S_begin, pintegeroperation[.SWAPPED = true], NFLOAT 0, NINT (-2), 0)',
        '~$arithmetic_cv_deprecated_valid(S_begin, pintegeroperation, NFLOAT 0, NINT (-2), 2)',
        '~$arithmetic_cv_deprecated_valid(S_begin, pintegeroperation, NINT 1, NINT (-2), 0)',
        'S_final_budget = $drive_steps(S_begin, 1)', 'S_final_budget.COMPLETION = BUDGET',
        'S_final = S_final_budget[.COMPLETION = NORMAL]', '$plain_arithmetic_frontier(S_final, 13)',
        'S_final.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(1), 'perrorcall.TARGET = eps',
        'perrorcall.SITE = pintegeroperation.SITE', 'perrorcall.LINE = 25', 'perrorcall.LEVEL = 8192',
        'perrorcall.MESSAGE = $ptascii("Power of base 0 and negative exponent is deprecated")',
        '$error_call_valid(S_final, perrorcall)', '$call_descriptors_valid(S_final)',
        '~$error_call_valid(S_final, perrorcall[.LINE = 24])',
        '~$error_call_valid(S_final, perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S_final, perrorcall[.MESSAGE = eps])',
        '~$error_call_valid(S_final, perrorcall[.RESUME = ARITHMETIC_CV_DEPRECATED pintegeroperation (NFLOAT 0) (NINT (-2)) 2])',
        '~$error_call_valid(S_final, perrorcall[.RESUME = POWER_WARNING pintegeroperation (NFLOAT 0) (NINT (-2)) 1])',
    ]
    seek('S_entered', 'S_final', 14)
    checks += ['$plain_arithmetic_entered(S_entered.FRAMES, 2)', '$call_descriptors_valid(S_entered)',
               '$heap_valid($heap_graph(S_entered))']
    seek('S_throw', 'S_entered', 9)
    checks += [
        'S_throw.TODO = (THROW_SEARCH n_supplied) :: ptask_throw*',
        'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps', '~$plain_arithmetic_tasks(S_throw.TODO)',
        '$throwable_live(S_throw, n_supplied)', '$throwable_previous_id(S_throw, n_supplied) = eps',
        '$throwable_field(S_throw, n_supplied, "line") = PINT 20',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_supplied) = 2',
        'S_throw.STORE[n_left] = DEFINED (PINT 77)', 'S_throw.STORE[n_right] = DEFINED (PINT 9)',
        'S_throw.STORE[n_calls] = DEFINED (PINT 1)', 'S_throw.STORE[n_v] = DEFINED (PINT 100)',
        'S_throw.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        'S_throw.STRINGDATA[n_string] = $ptascii("0.0")', '$string_carrier_valid(S_throw, pvalue_left)',
        'S_throw.ERRORHANDLER = S_entry.ERRORHANDLER',
        '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
        'S_done = $drive_steps(S_throw, 5000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_v] = DEFINED (PINT 100)', 'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        'S_done.STORE[n_left] = DEFINED (PINT 1)', 'S_done.STORE[n_right] = DEFINED (PINT 2)',
        '$throwable_previous_id(S_done, n_supplied) = eps', '$throwable_field(S_done, n_supplied, "line") = PINT 20',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_entry, 6000) = S_done', '$drive_steps(S_final, 0) = S_final[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks


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
