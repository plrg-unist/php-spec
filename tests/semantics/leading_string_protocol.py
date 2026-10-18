#!/usr/bin/env python3
"""Reached leading-string parse, warning callback, store and throw frontiers."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import leading_string_cases as cases
import arithmetic_warning_protocol as shared
import quiet_scalar_protocol as prior

CASES = ('leading-string-mod-carrier', 'leading-string-left-literal',
         'leading-string-or-exponent', 'leading-string-second-throw')
HELPERS = prior.HELPERS + r'''
dec $leading_string_task(ptask) : bool
def $leading_string_task(BOTH_ASSIGN_STRING_WARNING pintegeroperation n_target n_right n_bits_left i_left pvalue_right i_right n_stage) = true
def $leading_string_task(ERROR_HANDLER_INVOKE perrorcall) = $leading_string_task(perrorcall.RESUME)
def $leading_string_task(ERROR_HANDLER_RESULT perrorcall) = $leading_string_task(perrorcall.RESUME)
def $leading_string_task(ERROR_HANDLER_CLEAN perrorcall) = $leading_string_task(perrorcall.RESUME)
def $leading_string_task(ptask) = ($modassign_both_task(ptask) \/ $shiftassign_both_task(ptask) \/ $bitassign_both_task(ptask)) -- otherwise
dec $leading_string_tasks(ptask*) : bool
def $leading_string_tasks(eps) = false
def $leading_string_tasks(ptask :: ptask_tail*) = ($leading_string_task(ptask) \/ $leading_string_tasks(ptask_tail*))
dec $leading_string_frame(pframe) : bool
def $leading_string_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = BOTH_ASSIGN_STRING_WARNING pintegeroperation n_target n_right n_bits_left i_left pvalue_right i_right 1
  -- if perrorcall.TARGET =/= eps
def $leading_string_frame(pframe) = false -- otherwise
dec $leading_string_entered(pframe*, nat) : bool
def $leading_string_entered(pframe*, 0) = ($modassign_both_entered(pframe*, 0) \/ $shiftassign_both_entered(pframe*, 0) \/ $bitassign_both_entered(pframe*, 0))
def $leading_string_entered(eps, 1) = false
def $leading_string_entered(pframe :: pframe_tail*, 1) = ($leading_string_frame(pframe) \/ $leading_string_entered(pframe_tail*, 1))
def $leading_string_entered(pframe*, n) = false -- otherwise
dec $leading_string_source(expression) : bool
def $leading_string_source(NExprAssignOpMod expression_left expression_right metadata) = true
def $leading_string_source(expression) = ($shiftassign_warning_operator(expression) =/= eps \/ $bitassign_warning_operator(expression) =/= eps) -- otherwise
dec $leading_string_frontier(pstate, nat) : bool
def $leading_string_frontier(S, n_stage) = ($modassign_both_frontier(S, n_stage) \/ $shiftassign_both_frontier(S, n_stage) \/ $bitassign_both_frontier(S, n_stage))
  -- if $(n_stage >= 1 /\ n_stage <= 4)
def $leading_string_frontier(S, 5) = true
  -- if S.TODO = (BOTH_ASSIGN_STRING_WARNING pintegeroperation n_target n_right n_bits_left i_left pvalue_right i_right 0) :: ptask_tail*
def $leading_string_frontier(S, 6) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = BOTH_ASSIGN_STRING_WARNING pintegeroperation n_target n_right n_bits_left i_left pvalue_right i_right 1
  -- if perrorcall.TARGET = eps
def $leading_string_frontier(S, 7) = (S.CURRENT =/= eps /\ $leading_string_entered(S.FRAMES, 1))
def $leading_string_frontier(S, 8) = true
  -- if S.TODO = (BOTH_ASSIGN_STRING_WARNING pintegeroperation n_target n_right n_bits_left i_left pvalue_right i_right 1) :: ptask_tail*
def $leading_string_frontier(S, 9) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (expression)
  -- if $leading_string_source(expression)
  -- if S.RESULT = KNOWN (PINT i)
  -- if ~$leading_string_tasks(S.TODO)
def $leading_string_frontier(S, 10) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if ~$leading_string_tasks(S.TODO)
def $leading_string_frontier(S, n) = false -- otherwise
dec $leading_string_seek(pstate, nat, nat) : pstate
def $leading_string_seek(S, n_stage, n) = S -- if $leading_string_frontier(S, n_stage)
def $leading_string_seek(S, n_stage, n) = S
  -- if ~$leading_string_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $leading_string_seek(S, n_stage, n) = S
  -- if ~$leading_string_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $leading_string_seek(S, n_stage, n) = $leading_string_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$leading_string_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    family, tag, op, text, result = {
        CASES[0]: ('modassign', 'MOD_ASSIGN_BOTH_LEFT', 'MODULO', '05tail', '2'),
        CASES[1]: ('shiftassign', 'SHIFT_ASSIGN_BOTH_LEFT', 'SHIFTLEFT', '5tail', '384'),
        CASES[2]: ('bitassign', 'BIT_ASSIGN_BOTH_LEFT', 'BITOR', ' +5e0 tail', '13'),
        CASES[3]: ('modassign', 'MOD_ASSIGN_BOTH_LEFT', 'MODULO', '05tail', '2'),
    }[name]
    thrown = name == CASES[3]
    carrier = family == 'modassign'
    live_right = '7' if carrier else '10'
    left = lambda stage: f'{tag} pintegeroperation n_target n_right n_bits_left i_left {stage}'
    marker = lambda stage, value='pvalue_right', integer='5', operation='pintegeroperation', bits='n_bits_left', integer_left='i_left': f'BOTH_ASSIGN_STRING_WARNING {operation} n_target n_right {bits} {integer_left} ({value}) {integer} {stage}'
    snapshot = '$bothassign_leading_string_snapshot'
    valid = lambda state, stage, value='pvalue_right', integer='5', operation='pintegeroperation', bits='n_bits_left', integer_left='i_left': f'$bothassign_leading_string_valid({state}, {operation}, n_target, n_right, {bits}, {integer_left}, ({value}), {integer}, {stage})'
    bytes_ = '$ptascii(' + json.dumps(text) + ')'
    rhs = 'PSTRING_CARRIER ' + ('(REQUEST_STRING n_string)' if carrier else 'INTERNED_STRING') + ' (' + bytes_ + ')'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $leading_string_seek(S_initial, 1, 4000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$leading_string_frontier(S, 1)',
        'S.TODO = (' + left(0) + ') :: ptask_tail*', 'n_bits_left = 4623226492472524800', 'i_left = 12',
        'pintegeroperation.OP = ' + op, 'pintegeroperation.LINE = 25', '~pintegeroperation.SWAPPED',
        'S.ORIGIN = (pintegeroperation.SITE)',
        '$lookup(S.ENV, $ptascii("left")) = (n_target)', '$lookup(S.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S.ENV, $ptascii("v")) = (n_v)', '$lookup(S.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)',
        'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        'S.STORE[n_target] = DEFINED (PFLOAT n_bits_left)',
        'S.STORE[n_right] = DEFINED (PFLOAT 4620974692658839552)',
        '$call_task_valid(S, ' + left(0) + ')', snapshot + '(S, pintegeroperation, n_target, n_right) = eps',
        'S_first_budget = $drive_steps(S, 1)', 'S_first_budget.COMPLETION = BUDGET',
        'S_first = S_first_budget[.COMPLETION = NORMAL]', '$leading_string_frontier(S_first, 2)',
        'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
        'perrorcall_first.RESUME = ' + left(1), 'perrorcall_first.TARGET = eps',
        'perrorcall_first.LEVEL = 8192', 'perrorcall_first.LINE = 25', '$error_call_valid(S_first, perrorcall_first)',
        'S_first_entered_found = $leading_string_seek(S_first, 3, 4000)',
        r'S_first_entered_found.COMPLETION = NORMAL \/ S_first_entered_found.COMPLETION = BUDGET',
        'S_first_entered = S_first_entered_found[.COMPLETION = NORMAL]', '$leading_string_entered(S_first_entered.FRAMES, 0)',
        'S_left_found = $leading_string_seek(S_first_entered, 4, 4000)',
        r'S_left_found.COMPLETION = NORMAL \/ S_left_found.COMPLETION = BUDGET',
        'S_left = S_left_found[.COMPLETION = NORMAL]', '$leading_string_frontier(S_left, 4)',
        'S_left.TODO = (' + left(1) + ') :: ptask_tail*', 'S_left.CURRENT = eps', 'S_left.FRAMES = eps',
        'S_left.STORE[n_target] = DEFINED (PINT 99)', 'S_left.STORE[n_right] = DEFINED pvalue_right',
        'pvalue_right = ' + rhs, '$string_carrier_valid(S_left, pvalue_right)',
        '$string_bytes(pvalue_right) = (' + bytes_ + ')', '$string_long(' + bytes_ + ') = STRINT 5 ([LEADINGNUMBER])',
        'S_left.STORE[n_v] = DEFINED (PINT 100)', 'S_left.STORE[n_calls] = DEFINED (PINT 1)',
        '$lookup(S_left.ENV, $ptascii("alias")) = (n_target)', 'n_target <- S_left.REFCELLS',
        '$heap_owners($heap_prune($heap_graph(S_left)), HCELL n_target) = 2',
        snapshot + '(S_left, pintegeroperation, n_target, n_right) = ((pvalue_right, 5))',
        '$bothassign_quiet_string_snapshot(S_left, pintegeroperation, n_target, n_right) = eps',
        '$modassign_both_right_snapshot(S_left, pintegeroperation, n_target, n_right) = eps',
        '$modassign_both_integral_snapshot(S_left, pintegeroperation, n_target, n_right) = eps',
        '$bothassign_quiet_scalar_snapshot(S_left, pintegeroperation, n_target, n_right) = eps',
        '$call_descriptors_valid(S_left)', '$heap_valid($heap_graph(S_left))',
    ]
    if name == CASES[0]:
        checks += [
            'S_left.STRINGDATA[n_string] = ' + bytes_,
            snapshot + '(S_left[.STORE[n_right] = DEFINED (PSTRING ($ptascii("05tail")))], pintegeroperation, n_target, n_right) = (((PSTRING ($ptascii("05tail"))), 5))',
            snapshot + '(S_left[.STRINGDATA = S_left.STRINGDATA ++ [($ptascii("other39"))]], pintegeroperation, n_target, n_right) = ((pvalue_right, 5))',
            snapshot + '(S_left[.STRINGDATA[n_string] = $ptascii("bad")], pintegeroperation, n_target, n_right) = eps',
        ]
        for value in ['PINT 5', 'PFLOAT 4617315517961601024', 'PBOOL true', 'PNULL', 'PSTRING ($ptascii("5"))', 'PSTRING ($ptascii("5.5tail"))', 'PSTRING ($ptascii("wat"))', 'PUNDEFINED']:
            checks += [snapshot + f'(S_left[.STORE[n_right] = DEFINED ({value})], pintegeroperation, n_target, n_right) = eps']
        for state in ['S_left[.REFCELLS = S_left.REFCELLS ++ [n_right]]', 'S_left[.ALLOCATIONS = eps]', 'S_left[.ENV = eps][.GLOBALTABLE = eps]', 'S_left[.PROPREFS = [{CELL n_target, SOURCES eps}]]', 'S_left[.STORE[n_target] = DEFINED (POBJECT n_second)]']:
            checks += [snapshot + f'({state}, pintegeroperation, n_target, n_right) = eps']
    checks += [
        'S_marker_budget = $drive_steps(S_left, 1)', 'S_marker_budget.COMPLETION = BUDGET',
        'S_marker = S_marker_budget[.COMPLETION = NORMAL]', '$leading_string_frontier(S_marker, 5)',
        'S_marker.TODO = (' + marker(0) + ') :: ptask_tail*',
        'S_marker.STORE = S_left.STORE', 'S_marker.ENV = S_left.ENV',
        'S_marker.EVENTS = S_left.EVENTS', 'S_marker.STRINGDATA = S_left.STRINGDATA',
        '$call_task_valid(S_marker, ' + marker(0) + ')', '$task_nodes(' + marker(0) + ') = eps',
        '~' + valid('S_marker', 2), '~' + valid('S_marker', 0, integer='6'),
        '~' + valid('S_marker', 0, integer_left='13'),
        '~' + valid('S_marker', 0, operation='pintegeroperation[.OP = POWER]'),
        '~' + valid('S_marker', 0, bits='18446744073709551616'),
        'S_second_budget = $drive_steps(S_marker, 1)', 'S_second_budget.COMPLETION = BUDGET',
        'S_second = S_second_budget[.COMPLETION = NORMAL]', '$leading_string_frontier(S_second, 6)',
        'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
        'perrorcall_second.RESUME = ' + marker(1), 'perrorcall_second.TARGET = eps',
        'perrorcall_second.LEVEL = 2', 'perrorcall_second.LINE = 25',
        'perrorcall_second.MESSAGE = $ptascii("A non-numeric value encountered")',
        'perrorcall_second.EVENT = DIAGNOSTIC "Warning" perrorcall_second.MESSAGE 25',
        '$error_call_valid(S_second, perrorcall_second)',
        '~$error_call_valid(S_second, perrorcall_second[.LEVEL = 8192])',
        '~$error_call_valid(S_second, perrorcall_second[.LINE = 24])',
        '~$error_call_valid(S_second, perrorcall_second[.MESSAGE = $ptascii("wrong")])',
        '~$error_call_valid(S_second, perrorcall_second[.EVENT = DIAGNOSTIC "Deprecated" perrorcall_second.MESSAGE 25])',
        '$call_task_valid(S_second, ' + marker(1, value='PSTRING ($ptascii("6tail"))', integer='6') + ')',
        '~$error_call_valid(S_second, perrorcall_second[.RESUME = ' + marker(1, value='PSTRING ($ptascii("6tail"))', integer='6') + '])',
        '$call_descriptors_valid(S_second)', '$heap_valid($heap_graph(S_second))',
        'S_second_entered_found = $leading_string_seek(S_second, 7, 4000)',
        r'S_second_entered_found.COMPLETION = NORMAL \/ S_second_entered_found.COMPLETION = BUDGET',
        'S_second_entered = S_second_entered_found[.COMPLETION = NORMAL]', '$leading_string_entered(S_second_entered.FRAMES, 1)',
        '$call_descriptors_valid(S_second_entered)', '$heap_valid($heap_graph(S_second_entered))',
    ]
    if thrown:
        checks += [
            'S_throw_found = $leading_string_seek(S_second_entered, 10, 4000)',
            r'S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET',
            'S_throw = S_throw_found[.COMPLETION = NORMAL]', '$leading_string_frontier(S_throw, 10)',
            'S_throw.TODO = (THROW_SEARCH n_second) :: ptask_throw*', '~$leading_string_tasks(S_throw.TODO)',
            '$lookup(S_throw.ENV, $ptascii("left")) = (n_target)', '$lookup(S_throw.ENV, $ptascii("alias")) = (n_target)',
            'S_throw.STORE[n_target] = DEFINED (PINT 88)', 'S_throw.STORE[n_right] = DEFINED (PINT 7)',
            'S_throw.STORE[n_v] = DEFINED (PINT 100)', 'S_throw.STORE[n_calls] = DEFINED (PINT 2)',
            '$throwable_live(S_throw, n_second)', '$throwable_previous_id(S_throw, n_second) = eps',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_target) = 2',
            'S_throw.ERRORHANDLER = S.ERRORHANDLER', '$modassign_both_deprecations(S_throw.EVENTS) = 0',
            '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
            'S_done = $drive_steps(S_throw, 4000)',
            '$lookup(S_done.ENV, $ptascii("left")) = (n_target)',
            'S_done.STORE[n_target] = DEFINED (PINT 7)', 'S_done.STORE[n_v] = DEFINED (PINT 100)',
        ]
    else:
        checks += [
            'S_return_found = $leading_string_seek(S_second_entered, 8, 4000)',
            r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
            'S_return = S_return_found[.COMPLETION = NORMAL]', '$leading_string_frontier(S_return, 8)',
            'S_return.TODO = (' + marker(1) + ') :: ptask_tail*',
            'S_return.STORE[n_target] = DEFINED (PINT 88)', 'S_return.STORE[n_right] = DEFINED (PINT ' + live_right + ')',
            'S_return.STORE[n_v] = DEFINED (PINT 100)', 'S_return.STORE[n_calls] = DEFINED (PINT 2)',
            '$lookup(S_return.ENV, $ptascii("alias")) = (n_target)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_target) = 2',
            '$call_task_valid(S_return, ' + marker(1) + ')', '~$call_task_valid(S_return, ' + marker(0) + ')',
            snapshot + '(S_return, pintegeroperation, n_target, n_right) = eps',
            '$powerassign_warning_ready(S_return, pintegeroperation, n_target)',
            '$integer_binary(pintegeroperation.OP, i_left, 5) = IRESULT ' + result,
            'S_step_budget = $drive_steps(S_return, 1)', 'S_step_budget.COMPLETION = BUDGET',
            'S_step = S_step_budget[.COMPLETION = NORMAL]', '$leading_string_frontier(S_step, 9)',
            'S_step.TODO = ptask_tail*', 'S_step.RESULT = KNOWN (PINT ' + result + ')',
            '$lookup(S_step.ENV, $ptascii("left")) = (n_new)', 'n_new = |S_return.STORE|',
            'S_step.CELL = n_new', 'S_step.LOCATION = ROOT n_new', '~(n_new <- S_step.REFCELLS)',
            '$lookup(S_step.ENV, $ptascii("alias")) = (n_target)',
            'S_step.STORE = S_return.STORE ++ [DEFINED (PINT ' + result + ')]',
            'S_step.ALLOCATIONS = S_return.ALLOCATIONS ++ [HCELL n_new]',
            'S_step.STRINGDATA = S_return.STRINGDATA', 'S_step.EVENTS = S_return.EVENTS',
            '$heap_owners($heap_prune($heap_graph(S_step)), HCELL n_target) = 1',
            '$heap_owners($heap_prune($heap_graph(S_step)), HCELL n_new) = 1',
            '$heap_owners($heap_prune($heap_graph(S_step)), HCELL n_right) = 1',
            '$string_carrier_valid(S_step, pvalue_right)',
            '$call_descriptors_valid(S_step)', '$heap_valid($heap_graph(S_step))',
            'S_done = $drive_steps(S_step, 4000)',
            '$drive_steps(S_return, 5000) = S_done',
            'S_done.STORE[n_target] = DEFINED (PINT 88)', 'S_done.STORE[n_new] = DEFINED (PINT 7)',
            'S_done.STORE[n_v] = DEFINED (PINT ' + result + ')',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_right] = DEFINED (PINT ' + live_right + ')',
        'S_done.STORE[n_calls] = DEFINED (PINT 2)', '$string_carrier_valid(S_done, pvalue_right)',
        '$modassign_both_deprecations(S_done.EVENTS) = 0',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]', '$drive_steps(S, 6000) = S_done',
        '$drive_steps(S_marker, 6000) = S_done', '$drive_steps(S_first_entered, 6000) = S_done',
        '$drive_steps(S_second_entered, 6000) = S_done',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path, required=True)
    args, _ = parser.parse_known_args()
    watched = [Path(__file__), Path(cases.__file__), Path(prior.__file__), Path(shared.__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    shared.cases, shared.CASES, shared.HELPERS, shared.conditions = cases, CASES, HELPERS, conditions
    passed = shared.main()
    assert before == {str(path): digest(path) for path in watched}
    report = json.loads((args.output / 'report.json').read_bytes())
    report['leading_string_inputs'] = before
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
