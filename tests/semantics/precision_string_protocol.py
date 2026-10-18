#!/usr/bin/env python3
"""Reached complete/leading precision diagnostics, protected caches and cancellation."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import precision_string_cases as cases
import arithmetic_warning_protocol as shared
import quiet_scalar_protocol as prior

CASES = ('precision-string-mod-carrier', 'precision-string-left-complete',
         'precision-string-leading-warning-throw')
HELPERS = prior.HELPERS + r'''
dec $precision_string_task(ptask) : bool
def $precision_string_task(BOTH_ASSIGN_PRECISION_STRING pintegeroperation n_target n_right n_bits_left i_left pintegerconversion n_cursor) = true
def $precision_string_task(ERROR_HANDLER_INVOKE perrorcall) = $precision_string_task(perrorcall.RESUME)
def $precision_string_task(ERROR_HANDLER_RESULT perrorcall) = $precision_string_task(perrorcall.RESUME)
def $precision_string_task(ERROR_HANDLER_CLEAN perrorcall) = $precision_string_task(perrorcall.RESUME)
def $precision_string_task(ptask) = ($modassign_both_task(ptask) \/ $shiftassign_both_task(ptask) \/ $bitassign_both_task(ptask)) -- otherwise
dec $precision_string_tasks(ptask*) : bool
def $precision_string_tasks(eps) = false
def $precision_string_tasks(ptask :: ptask_tail*) = ($precision_string_task(ptask) \/ $precision_string_tasks(ptask_tail*))
dec $precision_string_frame(pframe, nat) : bool
def $precision_string_frame(pframe, n_cursor) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = BOTH_ASSIGN_PRECISION_STRING pintegeroperation n_target n_right n_bits_left i_left pintegerconversion n_cursor
  -- if perrorcall.TARGET =/= eps
def $precision_string_frame(pframe, n_cursor) = false -- otherwise
dec $precision_string_entered(pframe*, nat) : bool
def $precision_string_entered(pframe*, 0) = ($modassign_both_entered(pframe*, 0) \/ $shiftassign_both_entered(pframe*, 0) \/ $bitassign_both_entered(pframe*, 0))
def $precision_string_entered(eps, n_phase) = false -- if $(n_phase >= 1 /\ n_phase <= 2)
def $precision_string_entered(pframe :: pframe_tail*, n_phase) = ($precision_string_frame(pframe, n_phase) \/ $precision_string_entered(pframe_tail*, n_phase))
  -- if $(n_phase >= 1 /\ n_phase <= 2)
def $precision_string_entered(pframe*, n_phase) = false -- otherwise
dec $precision_string_source(expression) : bool
def $precision_string_source(NExprAssignOpMod expression_left expression_right metadata) = true
def $precision_string_source(expression) = ($shiftassign_warning_operator(expression) =/= eps \/ $bitassign_warning_operator(expression) =/= eps) -- otherwise
dec $precision_string_frontier(pstate, nat) : bool
def $precision_string_frontier(S, n_stage) = ($modassign_both_frontier(S, n_stage) \/ $shiftassign_both_frontier(S, n_stage) \/ $bitassign_both_frontier(S, n_stage))
  -- if $(n_stage >= 1 /\ n_stage <= 4)
def $precision_string_frontier(S, 5) = true
  -- if S.TODO = (BOTH_ASSIGN_PRECISION_STRING pintegeroperation n_target n_right n_bits_left i_left pintegerconversion 0) :: ptask_tail*
def $precision_string_frontier(S, 6) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = BOTH_ASSIGN_PRECISION_STRING pintegeroperation n_target n_right n_bits_left i_left pintegerconversion 1
  -- if perrorcall.TARGET = eps
def $precision_string_frontier(S, 7) = (S.CURRENT =/= eps /\ $precision_string_entered(S.FRAMES, 1))
def $precision_string_frontier(S, 8) = true
  -- if S.TODO = (BOTH_ASSIGN_PRECISION_STRING pintegeroperation n_target n_right n_bits_left i_left pintegerconversion 1) :: ptask_tail*
def $precision_string_frontier(S, 9) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (expression)
  -- if $precision_string_source(expression)
  -- if S.RESULT = KNOWN (PINT i)
  -- if ~$precision_string_tasks(S.TODO)
def $precision_string_frontier(S, 10) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if ~$precision_string_tasks(S.TODO)
def $precision_string_frontier(S, 11) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = BOTH_ASSIGN_PRECISION_STRING pintegeroperation n_target n_right n_bits_left i_left pintegerconversion 2
  -- if perrorcall.TARGET = eps
def $precision_string_frontier(S, 12) = (S.CURRENT =/= eps /\ $precision_string_entered(S.FRAMES, 2))
def $precision_string_frontier(S, 13) = true
  -- if S.TODO = (BOTH_ASSIGN_PRECISION_STRING pintegeroperation n_target n_right n_bits_left i_left pintegerconversion 2) :: ptask_tail*
def $precision_string_frontier(S, n_stage) = false -- otherwise
dec $precision_string_seek(pstate, nat, nat) : pstate
def $precision_string_seek(S, n_stage, n) = S -- if $precision_string_frontier(S, n_stage)
def $precision_string_seek(S, n_stage, n) = S
  -- if ~$precision_string_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $precision_string_seek(S, n_stage, n) = S
  -- if ~$precision_string_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $precision_string_seek(S, n_stage, n) = $precision_string_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$precision_string_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    leading = name != CASES[1]
    thrown = name == CASES[2]
    tag, operation, text, result = ('MOD_ASSIGN_BOTH_LEFT', 'MODULO', '05.5tail', '2') if leading else ('SHIFT_ASSIGN_BOTH_LEFT', 'SHIFTLEFT', '5.5', '384')
    ascii_value = lambda value: '$ptascii(' + json.dumps(value) + ')'
    string = lambda value: 'PSTRING_CARRIER INTERNED_STRING (' + ascii_value(value) + ')'
    precision = lambda value: ascii_value('Implicit conversion from float-string "' + value + '" to int loses precision')
    warning = '$ptascii("A non-numeric value encountered")'
    notices = lambda value: ('[(2, ' + warning + '), (8192, ' + precision(value) + ')]' if leading else '[(8192, ' + precision(value) + ')]')
    left = lambda stage: f'{tag} pintegeroperation n_target n_right n_bits_left i_left {stage}'
    marker = lambda cursor, conversion='pintegerconversion': f'BOTH_ASSIGN_PRECISION_STRING pintegeroperation n_target n_right n_bits_left i_left {conversion} {cursor}'
    snapshot = '$bothassign_precision_string_snapshot'
    rhs = ('PSTRING_CARRIER (REQUEST_STRING n_string) (' + ascii_value(text) + ')') if leading else string(text)
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_left_found = $precision_string_seek(S_initial, 4, 4000)',
        r'S_left_found.COMPLETION = NORMAL \/ S_left_found.COMPLETION = BUDGET',
        'S_left = S_left_found[.COMPLETION = NORMAL]', '$precision_string_frontier(S_left, 4)',
        'S_left.TODO = (' + left(1) + ') :: ptask_tail*', 'n_bits_left = 4623226492472524800', 'i_left = 12',
        'pintegeroperation.OP = ' + operation, '~pintegeroperation.SWAPPED',
        'pintegeroperation.LEFT = VARIABLE ($ptascii("left")) 23',
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("right")) 25',
        'pintegeroperation.LINE = 25', 'S_left.ORIGIN = (pintegeroperation.SITE)',
        'S_left.CURRENT = eps', 'S_left.FRAMES = eps',
        '$lookup(S_left.ENV, $ptascii("left")) = (n_target)', '$lookup(S_left.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_left.ENV, $ptascii("alias")) = (n_target)', '$lookup(S_left.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_left.ENV, $ptascii("calls")) = (n_calls)', '$lookup(S_left.ENV, $ptascii("second")) = (n_second_cell)',
        'S_left.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        'S_left.STORE[n_target] = DEFINED (PINT 99)', 'S_left.STORE[n_right] = DEFINED pvalue_saved',
        'pvalue_saved = ' + rhs, 'S_left.STORE[n_v] = DEFINED (PINT 100)',
        'S_left.STORE[n_calls] = DEFINED (PINT 1)', 'n_target <- S_left.REFCELLS', '~(n_right <- S_left.REFCELLS)',
        '$heap_owners($heap_prune($heap_graph(S_left)), HCELL n_target) = 2',
        '$string_carrier_valid(S_left, pvalue_saved)', '$string_bytes(pvalue_saved) = (' + ascii_value(text) + ')',
        '$string_long(' + ascii_value(text) + ') = STRINT 5 (' + ('[LEADINGNUMBER, STRINGPRECISIONLOSS]' if leading else '[STRINGPRECISIONLOSS]') + ')',
        snapshot + '(S_left, pintegeroperation, n_target, n_right) = (pintegerconversion)',
        'pintegerconversion.INPUT = pvalue_saved', 'pintegerconversion.VALUE = 5',
        'pintegerconversion.NOTICES = ' + notices(text), '$integer_conversion(pvalue_saved) = (pintegerconversion)',
        '$bothassign_leading_string_snapshot(S_left, pintegeroperation, n_target, n_right) = eps',
        '$bothassign_quiet_string_snapshot(S_left, pintegeroperation, n_target, n_right) = eps',
        '$modassign_both_right_snapshot(S_left, pintegeroperation, n_target, n_right) = eps',
        '$call_task_valid(S_left, ' + left(1) + ')', '$modassign_both_deprecations(S_left.EVENTS) = 0',
        '$call_descriptors_valid(S_left)', '$heap_valid($heap_graph(S_left))',
    ]
    if name == CASES[0]:
        checks += ['S_left.STRINGDATA[n_string] = ' + ascii_value(text)]
        for value in ['PINT 5', 'PFLOAT 4617878467915022336', 'PBOOL true', 'PNULL', 'PSTRING ($ptascii("5"))', 'PSTRING ($ptascii("5tail"))', 'PSTRING ($ptascii("wat"))', 'PUNDEFINED']:
            checks += [snapshot + f'(S_left[.STORE[n_right] = DEFINED ({value})], pintegeroperation, n_target, n_right) = eps']
        for state in ['S_left[.REFCELLS = S_left.REFCELLS ++ [n_right]]', 'S_left[.ALLOCATIONS = eps]', 'S_left[.ENV = eps][.GLOBALTABLE = eps]', 'S_left[.PROPREFS = [{CELL n_target, SOURCES eps}]]', 'S_left[.STORE[n_target] = DEFINED (POBJECT n_second)]', 'S_left[.STRINGDATA[n_string] = $ptascii("bad")]']:
            checks += [snapshot + f'({state}, pintegeroperation, n_target, n_right) = eps']
    checks += [
        'S_marker_budget = $drive_steps(S_left, 1)', 'S_marker_budget.COMPLETION = BUDGET',
        'S_marker = S_marker_budget[.COMPLETION = NORMAL]', '$precision_string_frontier(S_marker, 5)',
        'S_marker.TODO = (' + marker(0) + ') :: ptask_tail*',
        'S_marker.STORE = S_left.STORE', 'S_marker.ENV = S_left.ENV',
        'S_marker.EVENTS = S_left.EVENTS', 'S_marker.STRINGDATA = S_left.STRINGDATA',
        '$call_task_valid(S_marker, ' + marker(0) + ')', '$task_nodes(' + marker(0) + ') = eps',
        '~$call_task_valid(S_marker, ' + marker(3) + ')',
        '~$call_task_valid(S_marker, ' + marker(1, 'pintegerconversion[.VALUE = 6]') + ')',
        '~$call_task_valid(S_marker, ' + marker(1, 'pintegerconversion[.INPUT = PINT 5]') + ')',
        '~$call_task_valid(S_marker, ' + marker(1, 'pintegerconversion[.NOTICES = eps]') + ')',
        '~$call_task_valid(S_marker, BOTH_ASSIGN_STRING_WARNING pintegeroperation n_target n_right n_bits_left i_left pvalue_saved 5 1)',
        'S_notice_budget = $drive_steps(S_marker, 1)', 'S_notice_budget.COMPLETION = BUDGET',
        'S_notice = S_notice_budget[.COMPLETION = NORMAL]', '$precision_string_frontier(S_notice, 6)',
        'S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
        'perrorcall_first.RESUME = ' + marker(1), 'perrorcall_first.TARGET = eps',
        'perrorcall_first.LEVEL = ' + ('2' if leading else '8192'), 'perrorcall_first.LINE = 25',
        'perrorcall_first.MESSAGE = ' + (warning if leading else precision(text)),
        'perrorcall_first.EVENT = DIAGNOSTIC ' + ('"Warning"' if leading else '"Deprecated"') + ' perrorcall_first.MESSAGE 25',
        '$error_call_valid(S_notice, perrorcall_first)',
        '~$error_call_valid(S_notice, perrorcall_first[.LINE = 24])',
        '~$error_call_valid(S_notice, perrorcall_first[.MESSAGE = $ptascii("wrong")])',
        '~$error_call_valid(S_notice, perrorcall_first[.RESUME = ' + marker(0) + '])',
        'pintegerconversion_alt = pintegerconversion[.INPUT = ' + string('6.5tail' if leading else '6.5') + '][.VALUE = 6][.NOTICES = ' + notices('6.5tail' if leading else '6.5') + ']',
        '$call_task_valid(S_notice, ' + marker(1, 'pintegerconversion_alt') + ')',
        '~$error_call_valid(S_notice, perrorcall_first[.RESUME = ' + marker(1, 'pintegerconversion_alt') + '][.MESSAGE = ' + (warning if leading else precision('6.5')) + '][.EVENT = DIAGNOSTIC ' + ('"Warning"' if leading else '"Deprecated"') + ' ' + (warning if leading else precision('6.5')) + ' 25])',
        '$call_descriptors_valid(S_notice)', '$heap_valid($heap_graph(S_notice))',
        'S_entered_found = $precision_string_seek(S_notice, 7, 4000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', '$precision_string_entered(S_entered.FRAMES, 1)',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if thrown:
        checks += [
            'S_throw_found = $precision_string_seek(S_entered, 10, 4000)',
            r'S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET',
            'S_throw = S_throw_found[.COMPLETION = NORMAL]', '$precision_string_frontier(S_throw, 10)',
            'S_throw.TODO = (THROW_SEARCH n_second) :: ptask_throw*', '~$precision_string_tasks(S_throw.TODO)',
            'S_throw.STORE[n_target] = DEFINED (PINT 88)',
            'S_throw.STORE[n_right] = DEFINED (' + string('7.5replaced') + ')',
            'S_throw.STORE[n_v] = DEFINED (PINT 100)', 'S_throw.STORE[n_calls] = DEFINED (PINT 2)',
            '$lookup(S_throw.ENV, $ptascii("left")) = (n_target)', '$lookup(S_throw.ENV, $ptascii("alias")) = (n_target)',
            '$throwable_live(S_throw, n_second)', '$throwable_previous_id(S_throw, n_second) = eps',
            '$throwable_field(S_throw, n_second, "line") = PINT 20',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_target) = 2',
            'S_throw.ERRORHANDLER = S_left.ERRORHANDLER', '$modassign_both_deprecations(S_throw.EVENTS) = 0',
            '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
            'S_done = $drive_steps(S_throw, 4000)', 'S_done.STORE[n_target] = DEFINED (PINT 7)',
            'S_done.STORE[n_v] = DEFINED (PINT 100)',
        ]
    else:
        checks += [
            'S_after_found = $precision_string_seek(S_entered, 8, 4000)',
            r'S_after_found.COMPLETION = NORMAL \/ S_after_found.COMPLETION = BUDGET',
            'S_after = S_after_found[.COMPLETION = NORMAL]', '$precision_string_frontier(S_after, 8)',
            'S_after.TODO = (' + marker(1) + ') :: ptask_tail*',
            'S_after.CURRENT = eps', 'S_after.FRAMES = eps',
            'S_after.STORE[n_target] = DEFINED (PINT ' + ('88' if leading else '101') + ')',
            'S_after.STORE[n_v] = DEFINED (PINT 100)', 'S_after.STORE[n_calls] = DEFINED (PINT 2)',
            '$call_task_valid(S_after, ' + marker(1) + ')', '~$call_task_valid(S_after, ' + marker(0) + ')',
            '$powerassign_warning_ready(S_after, pintegeroperation, n_target)',
            '$heap_owners($heap_prune($heap_graph(S_after)), HCELL n_target) = 2',
            'S_after.STRINGDATA[0:|S_left.STRINGDATA|] = S_left.STRINGDATA',
            '$string_carrier_valid(S_after, pvalue_saved)', '$modassign_both_deprecations(S_after.EVENTS) = 0',
            '$call_descriptors_valid(S_after)', '$heap_valid($heap_graph(S_after))',
        ]
        if leading:
            checks += [
                'S_after.STORE[n_right] = DEFINED (' + string('7.5replaced') + ')',
                snapshot + '(S_after, pintegeroperation, n_target, n_right) =/= (pintegerconversion)',
                'S_precision_budget = $drive_steps(S_after, 1)', 'S_precision_budget.COMPLETION = BUDGET',
                'S_precision = S_precision_budget[.COMPLETION = NORMAL]', '$precision_string_frontier(S_precision, 11)',
                'S_precision.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_tail*',
                'perrorcall_second.RESUME = ' + marker(2), 'perrorcall_second.TARGET = eps',
                'perrorcall_second.LEVEL = 8192', 'perrorcall_second.LINE = 25',
                'perrorcall_second.MESSAGE = ' + precision(text),
                'perrorcall_second.EVENT = DIAGNOSTIC "Deprecated" perrorcall_second.MESSAGE 25',
                '$error_call_valid(S_precision, perrorcall_second)',
                '~$error_call_valid(S_precision, perrorcall_second[.RESUME = ' + marker(3) + '])',
                '~$error_call_valid(S_precision, perrorcall_second[.MESSAGE = $ptascii("wrong")])',
                '~$error_call_valid(S_precision, perrorcall_second[.RESUME = ' + marker(2, 'pintegerconversion[.VALUE = 6]') + '])',
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
            ]
        else:
            checks += ['S_return = S_after']
        live_right = '7' if leading else '10'
        checks += [
            'S_return.STORE[n_target] = DEFINED (PINT 101)', 'S_return.STORE[n_right] = DEFINED (PINT ' + live_right + ')',
            'S_return.STORE[n_calls] = DEFINED (PINT ' + ('3' if leading else '2') + ')',
            '$lookup(S_return.ENV, $ptascii("alias")) = (n_target)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_target) = 2',
            '$integer_binary(pintegeroperation.OP, i_left, pintegerconversion.VALUE) = IRESULT ' + result,
            'S_step_budget = $drive_steps(S_return, 1)', 'S_step_budget.COMPLETION = BUDGET',
            'S_step = S_step_budget[.COMPLETION = NORMAL]', '$precision_string_frontier(S_step, 9)',
            'S_step.TODO = ptask_tail*', 'S_step.RESULT = KNOWN (PINT ' + result + ')',
            '~$precision_string_tasks(S_step.TODO)',
            '$lookup(S_step.ENV, $ptascii("left")) = (n_new)', 'n_new = |S_return.STORE|',
            'S_step.CELL = n_new', 'S_step.LOCATION = ROOT n_new', '~(n_new <- S_step.REFCELLS)',
            '$lookup(S_step.ENV, $ptascii("alias")) = (n_target)',
            'S_step.STORE = S_return.STORE ++ [DEFINED (PINT ' + result + ')]',
            'S_step.ALLOCATIONS = S_return.ALLOCATIONS ++ [HCELL n_new]',
            'S_step.STRINGDATA = S_return.STRINGDATA', 'S_step.EVENTS = S_return.EVENTS',
            '$string_carrier_valid(S_step, pvalue_saved)',
            '$heap_owners($heap_prune($heap_graph(S_step)), HCELL n_target) = 1',
            '$heap_owners($heap_prune($heap_graph(S_step)), HCELL n_new) = 1',
            '$call_descriptors_valid(S_step)', '$heap_valid($heap_graph(S_step))',
            'S_done = $drive_steps(S_step, 4000)',
            'S_done.STORE[n_target] = DEFINED (PINT 101)', 'S_done.STORE[n_new] = DEFINED (PINT 7)',
            'S_done.STORE[n_v] = DEFINED (PINT ' + result + ')',
            'S_done.STORE[n_right] = DEFINED (PINT ' + live_right + ')',
            '$drive_steps(S_return, 6000) = S_done',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("alias")) = (n_target)',
        'S_done.STORE[n_calls] = DEFINED (PINT ' + ('2' if thrown or not leading else '3') + ')',
        '$string_carrier_valid(S_done, pvalue_saved)', '$modassign_both_deprecations(S_done.EVENTS) = 0',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_left, 0) = S_left[.COMPLETION = BUDGET]',
        '$drive_steps(S_left, 6000) = S_done', '$drive_steps(S_marker, 6000) = S_done',
        '$drive_steps(S_notice, 6000) = S_done', '$drive_steps(S_entered, 6000) = S_done',
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
    report['precision_string_inputs'] = before
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
