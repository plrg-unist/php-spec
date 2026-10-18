#!/usr/bin/env python3
"""Reached quiet literal/exponent strings and dynamic carrier compound stores."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import quiet_string_cases as cases
import arithmetic_warning_protocol as shared
import quiet_scalar_protocol as prior

CASES = ('quiet-string-mod-carrier', 'quiet-string-left-literal', 'quiet-string-or-exponent')
HELPERS = prior.HELPERS


def conditions(name, program, path, stdout):
    family, tag, op, text, result = {
        'quiet-string-mod-carrier': ('modassign', 'MOD_ASSIGN_BOTH_LEFT', 'MODULO', '05', '2'),
        'quiet-string-left-literal': ('shiftassign', 'SHIFT_ASSIGN_BOTH_LEFT', 'SHIFTLEFT', '5', '384'),
        'quiet-string-or-exponent': ('bitassign', 'BIT_ASSIGN_BOTH_LEFT', 'BITOR', ' +5e0 ', '13'),
    }[name]
    carrier = name == CASES[0]
    left = lambda stage: f'{tag} pintegeroperation n_target n_right n_bits_left i_left {stage}'
    frontier, seek = f'${family}_both_frontier', f'${family}_both_seek'
    snapshot = '$bothassign_quiet_string_snapshot'
    bytes_ = '$ptascii(' + json.dumps(text) + ')'
    identity = '(REQUEST_STRING n_string)' if carrier else 'INTERNED_STRING'
    rhs = f'PSTRING_CARRIER {identity} ({bytes_})'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        f'S_found = {seek}(S_initial, 1, 3000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', f'{frontier}(S, 1)',
        'S.TODO = (' + left(0) + ') :: ptask_tail*',
        'n_bits_left = 4623226492472524800', 'i_left = 12',
        'pintegeroperation.OP = ' + op, 'pintegeroperation.LINE = 25', '~pintegeroperation.SWAPPED',
        'S.ORIGIN = (pintegeroperation.SITE)',
        '$lookup(S.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S.ENV, $ptascii("v")) = (n_v)', '$lookup(S.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)',
        'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        'S.STORE[n_target] = DEFINED (PFLOAT n_bits_left)',
        'S.STORE[n_right] = DEFINED (PFLOAT 4620974692658839552)',
        snapshot + '(S, pintegeroperation, n_target, n_right) = eps',
        '$call_task_valid(S, ' + left(0) + ')', '$task_nodes(' + left(0) + ') = eps',
        'S_dispatch_budget = $drive_steps(S, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]', f'{frontier}(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + left(1), 'perrorcall.TARGET = eps',
        'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = $ptascii("Implicit conversion from float 12.5 to int loses precision")',
        '$error_call_valid(S_dispatch, perrorcall)',
        f'S_entered_found = {seek}(S_dispatch, 3, 3000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', f'${family}_both_entered(S_entered.FRAMES, 0)',
        f'S_return_found = {seek}(S_entered, 4, 3000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', f'{frontier}(S_return, 4)',
        'S_return.TODO = (' + left(1) + ') :: ptask_tail*',
        'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
        'S_return.STORE[n_target] = DEFINED (PINT 99)',
        'S_return.STORE[n_right] = DEFINED pvalue_right', 'pvalue_right = ' + rhs,
        '$string_bytes(pvalue_right) = (' + bytes_ + ')', '$string_carrier_valid(S_return, pvalue_right)',
        '$string_long(' + bytes_ + ') = STRINT 5 eps',
        'S_return.STORE[n_v] = DEFINED (PINT 100)', 'S_return.STORE[n_calls] = DEFINED (PINT 1)',
        '$lookup(S_return.ENV, $ptascii("alias")) = (n_target)', 'n_target <- S_return.REFCELLS',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_target) = 2',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 1',
        snapshot + '(S_return, pintegeroperation, n_target, n_right) = (5)',
        '$modassign_warning_ready(S_return, pintegeroperation, n_target, n_right) = eps',
        '$modassign_both_right_snapshot(S_return, pintegeroperation, n_target, n_right) = eps',
        '$modassign_both_integral_snapshot(S_return, pintegeroperation, n_target, n_right) = eps',
        '$bothassign_quiet_scalar_snapshot(S_return, pintegeroperation, n_target, n_right) = eps',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
    ]
    if carrier:
        checks += [
            'S_return.STRINGDATA[n_string] = ' + bytes_,
            snapshot + '(S_return[.STORE[n_right] = DEFINED (PSTRING ($ptascii("05")))], pintegeroperation, n_target, n_right) = (5)',
            snapshot + '(S_return[.STRINGDATA = S_return.STRINGDATA ++ [($ptascii("other38"))]], pintegeroperation, n_target, n_right) = (5)',
            snapshot + '(S_return[.STRINGDATA[n_string] = $ptascii("bad")], pintegeroperation, n_target, n_right) = eps',
            snapshot + '(S_return[.STORE[n_right] = DEFINED (PSTRING_CARRIER (REQUEST_STRING (|S_return.STRINGDATA|)) ($ptascii("05")))], pintegeroperation, n_target, n_right) = eps',
        ]
        for value in ['PINT 5', 'PFLOAT 4617315517961601024', 'PBOOL true', 'PNULL', 'PSTRING ($ptascii("5x"))', 'PSTRING ($ptascii("5.5"))', 'PSTRING ($ptascii("wat"))', 'PSTRING eps', 'PUNDEFINED']:
            checks += [snapshot + f'(S_return[.STORE[n_right] = DEFINED ({value})], pintegeroperation, n_target, n_right) = eps']
        for state in ['S_return[.REFCELLS = S_return.REFCELLS ++ [n_right]]', 'S_return[.ALLOCATIONS = eps]', 'S_return[.ENV = eps][.GLOBALTABLE = eps]', 'S_return[.PROPREFS = [{CELL n_target, SOURCES eps}]]', 'S_return[.STORE[n_target] = DEFINED (POBJECT n_second)]']:
            checks += [snapshot + f'({state}, pintegeroperation, n_target, n_right) = eps']
        checks += [snapshot + '(S_return, pintegeroperation, n_v, n_right) = eps', snapshot + '(S_return, pintegeroperation, n_target, n_v) = eps']
    checks += [
        '$integer_binary(pintegeroperation.OP, i_left, 5) = IRESULT ' + result,
        'S_step_budget = $drive_steps(S_return, 1)', 'S_step_budget.COMPLETION = BUDGET',
        'S_step = S_step_budget[.COMPLETION = NORMAL]', f'{frontier}(S_step, 9)',
        'S_step.TODO = ptask_tail*', f'~{frontier}(S_step, 5)', f'~{frontier}(S_step, 11)',
        'S_step.RESULT = KNOWN (PINT ' + result + ')',
        '$lookup(S_step.ENV, $ptascii("left")) = (n_new)', 'n_new = |S_return.STORE|',
        'S_step.CELL = n_new', 'S_step.LOCATION = ROOT n_new', '~(n_new <- S_step.REFCELLS)',
        '$lookup(S_step.ENV, $ptascii("alias")) = (n_target)',
        'S_step.STORE = S_return.STORE ++ [DEFINED (PINT ' + result + ')]',
        'S_step.ALLOCATIONS = S_return.ALLOCATIONS ++ [HCELL n_new]',
        'S_step.STORE[n_right] = DEFINED pvalue_right', 'S_step.STRINGDATA = S_return.STRINGDATA',
        '$string_carrier_valid(S_step, pvalue_right)',
        '$heap_owners($heap_prune($heap_graph(S_step)), HCELL n_target) = 1',
        '$heap_owners($heap_prune($heap_graph(S_step)), HCELL n_new) = 1',
        '$heap_owners($heap_prune($heap_graph(S_step)), HCELL n_right) = 1',
        'S_step.EVENTS = S_return.EVENTS', '$call_descriptors_valid(S_step)', '$heap_valid($heap_graph(S_step))',
        'S_done = $drive_steps(S_step, 3000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_target] = DEFINED (PINT 99)', 'S_done.STORE[n_new] = DEFINED (PINT 7)',
        'S_done.STORE[n_right] = DEFINED pvalue_right', 'S_done.STORE[n_v] = DEFINED (PINT ' + result + ')',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)', '$string_carrier_valid(S_done, pvalue_right)',
        '$bitassign_both_deprecations(S_done.EVENTS) = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]', '$drive_steps(S, 3000) = S_done',
        '$drive_steps(S_return, 3000) = S_done', '$drive_steps(S_entered, 3000) = S_done',
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
    report['quiet_string_inputs'] = before
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
