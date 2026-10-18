#!/usr/bin/env python3
"""Reached quiet bool/null conversion: one fixture per new commit/error rule."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import quiet_scalar_cases as cases
import arithmetic_warning_protocol as shared
import modassign_both_warning_protocol as modulo
import shiftassign_both_warning_protocol as shift
import bitassign_both_warning_protocol as bitwise

CASES = ('quiet-scalar-mod-true', 'quiet-scalar-left-true', 'quiet-scalar-xor-true', 'quiet-scalar-mod-false')
HELPERS = shared.HELPERS
for protocol in (modulo, shift, bitwise):
    assert protocol.HELPERS.startswith(shared.HELPERS)
    HELPERS += protocol.HELPERS[len(shared.HELPERS):]


def conditions(name, program, path, stdout):
    family, tag, operation, result = {
        'quiet-scalar-mod-true': ('modassign', 'MOD_ASSIGN_BOTH_LEFT', 'MODULO', '0'),
        'quiet-scalar-left-true': ('shiftassign', 'SHIFT_ASSIGN_BOTH_LEFT', 'SHIFTLEFT', '24'),
        'quiet-scalar-xor-true': ('bitassign', 'BIT_ASSIGN_BOTH_LEFT', 'BITXOR', '13'),
        'quiet-scalar-mod-false': ('modassign', 'MOD_ASSIGN_BOTH_LEFT', 'MODULO', None),
    }[name]
    zero = result is None
    value = 'PBOOL false' if zero else 'PBOOL true'
    number = '0' if zero else '1'
    left = lambda stage: f'{tag} pintegeroperation n_target n_right n_bits_left i_left {stage}'
    frontier = f'${family}_both_frontier'
    seek = f'${family}_both_seek'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        f'S_found = {seek}(S_initial, 1, 3000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', f'{frontier}(S, 1)',
        'S.TODO = (' + left(0) + ') :: ptask_tail*',
        'n_bits_left = 4623226492472524800', 'i_left = 12',
        'pintegeroperation.OP = ' + operation, 'pintegeroperation.LINE = 25', '~pintegeroperation.SWAPPED',
        '$lookup(S.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S.ENV, $ptascii("v")) = (n_v)', '$lookup(S.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)',
        'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        'S.STORE[n_target] = DEFINED (PFLOAT n_bits_left)',
        'S.STORE[n_right] = DEFINED (PFLOAT 4620974692658839552)',
        '$bothassign_quiet_scalar_snapshot(S, pintegeroperation, n_target, n_right) = eps',
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
        'S_entered = S_entered_found[.COMPLETION = NORMAL]',
        f'${family}_both_entered(S_entered.FRAMES, 0)',
        f'S_return_found = {seek}(S_entered, 4, 3000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', f'{frontier}(S_return, 4)',
        'S_return.TODO = (' + left(1) + ') :: ptask_tail*',
        'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
        'S_return.STORE[n_target] = DEFINED (PINT 99)',
        'S_return.STORE[n_right] = DEFINED (' + value + ')',
        'S_return.STORE[n_v] = DEFINED (PINT 100)', 'S_return.STORE[n_calls] = DEFINED (PINT 1)',
        '$lookup(S_return.ENV, $ptascii("alias")) = (n_target)', 'n_target <- S_return.REFCELLS',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_target) = 2',
        '$bothassign_quiet_scalar_snapshot(S_return, pintegeroperation, n_target, n_right) = (' + number + ')',
        '$modassign_warning_ready(S_return, pintegeroperation, n_target, n_right) = eps',
        '$modassign_both_right_snapshot(S_return, pintegeroperation, n_target, n_right) = eps',
        '$modassign_both_integral_snapshot(S_return, pintegeroperation, n_target, n_right) = eps',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
    ]
    if name == CASES[0]:
        for scalar, integer in [('PNULL', '0'), ('PBOOL false', '0'), ('PBOOL true', '1')]:
            checks += [f'$bothassign_quiet_scalar_snapshot(S_return[.STORE[n_right] = DEFINED ({scalar})], pintegeroperation, n_target, n_right) = ({integer})']
        for scalar in ['PINT 1', 'PFLOAT 4607182418800017408', 'PFLOAT 4609434218613702656', 'PSTRING ($ptascii("1"))', 'POBJECT n_second', 'PUNDEFINED']:
            checks += [f'$bothassign_quiet_scalar_snapshot(S_return[.STORE[n_right] = DEFINED ({scalar})], pintegeroperation, n_target, n_right) = eps']
        for state in ['S_return[.REFCELLS = S_return.REFCELLS ++ [n_right]]', 'S_return[.ALLOCATIONS = eps]', 'S_return[.ENV = eps][.GLOBALTABLE = eps]', 'S_return[.PROPREFS = [{CELL n_target, SOURCES eps}]]', 'S_return[.STORE[n_target] = DEFINED (POBJECT n_second)]']:
            checks += [f'$bothassign_quiet_scalar_snapshot({state}, pintegeroperation, n_target, n_right) = eps']
        checks += [
            '$bothassign_quiet_scalar_snapshot(S_return, pintegeroperation, n_v, n_right) = eps',
            '$bothassign_quiet_scalar_snapshot(S_return, pintegeroperation, n_target, n_v) = eps',
        ]
    checks += [
        '$integer_binary(pintegeroperation.OP, i_left, ' + number + ') = ' + ('INTZERO' if zero else 'IRESULT ' + result),
        'S_step_budget = $drive_steps(S_return, 1)', 'S_step_budget.COMPLETION = BUDGET',
        'S_step = S_step_budget[.COMPLETION = NORMAL]',
        'S_step.TODO = ' + ('(THROW_SEARCH n_error) :: ptask_tail*' if zero else 'ptask_tail*'),
        f'{frontier}(S_step, ' + ('10)' if zero else '9)'),
        f'~{frontier}(S_step, 5)', f'~{frontier}(S_step, 11)',
        'S_step.EVENTS = S_return.EVENTS',
    ]
    if zero:
        checks += [
            'S_step.RESULT = KNOWN PNULL', 'n_error = |S_return.OBJECTS|',
            'S_step.OBJECTS[n_error] = THROWABLE pthrowable',
            'S_step.OBJECTS = S_return.OBJECTS ++ [THROWABLE pthrowable]',
            'pthrowable.KIND = "DivisionByZeroError"', 'pthrowable.ORIGIN = (pintegeroperation.SITE)',
            '$throwable_field(S_step, n_error, "line") = PINT 25',
            '$string_bytes($throwable_field(S_step, n_error, "message")) = ($ptascii("Modulo by zero"))',
            '$throwable_previous_id(S_step, n_error) = eps',
            '$heap_owners($heap_prune($heap_graph(S_step)), HOBJECT n_error) = 1',
            'S_step.STORE = S_return.STORE', 'S_step.ENV = S_return.ENV',
            'S_step.REFCELLS = S_return.REFCELLS',
            '$heap_owners($heap_prune($heap_graph(S_step)), HCELL n_target) = 2',
        ]
    else:
        checks += [
            'S_step.RESULT = KNOWN (PINT ' + result + ')',
            '$lookup(S_step.ENV, $ptascii("left")) = (n_new)', 'n_new = |S_return.STORE|',
            'S_step.CELL = n_new', 'S_step.LOCATION = ROOT n_new', '~(n_new <- S_step.REFCELLS)',
            '$lookup(S_step.ENV, $ptascii("alias")) = (n_target)',
            'S_step.STORE = S_return.STORE ++ [DEFINED (PINT ' + result + ')]',
            'S_step.ALLOCATIONS = S_return.ALLOCATIONS ++ [HCELL n_new]',
            '$heap_owners($heap_prune($heap_graph(S_step)), HCELL n_target) = 1',
            '$heap_owners($heap_prune($heap_graph(S_step)), HCELL n_new) = 1',
        ]
    checks += [
        '$call_descriptors_valid(S_step)', '$heap_valid($heap_graph(S_step))',
        'S_done = $drive_steps(S_step, 3000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_target] = DEFINED (PINT ' + ('7)' if zero else '99)'),
        'S_done.STORE[n_right] = DEFINED (' + value + ')', 'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        'S_done.STORE[n_v] = DEFINED (PINT ' + ('100)' if zero else result + ')'),
        '$bitassign_both_deprecations(S_done.EVENTS) = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]', '$drive_steps(S, 3000) = S_done',
        '$drive_steps(S_return, 3000) = S_done',
    ]
    if not zero:
        checks += ['S_done.STORE[n_new] = DEFINED (PINT 7)']
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path, required=True)
    args, _ = parser.parse_known_args()
    watched = [Path(__file__), Path(cases.__file__), *(Path(protocol.__file__) for protocol in (shared, modulo, shift, bitwise))]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    shared.cases, shared.CASES, shared.HELPERS, shared.conditions = cases, CASES, HELPERS, conditions
    passed = shared.main()
    assert before == {str(path): digest(path) for path in watched}
    report = json.loads((args.output / 'report.json').read_bytes())
    report['quiet_scalar_inputs'] = before
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
