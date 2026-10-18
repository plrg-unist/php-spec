#!/usr/bin/env python3
"""Real first callback, live TypeError labels, and no compound store."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import delayed_integer_failure_cases as cases
import quiet_scalar_protocol as shared

CASES = ('delayed-failure-mod-carrier',)
HELPERS = shared.HELPERS


def conditions(name, program, path, stdout):
    assert name == CASES[0]
    marker = lambda stage: 'MOD_ASSIGN_BOTH_LEFT pintegeroperation n_target n_right n_bits_left i_left ' + str(stage)
    snapshot = '$bothassign_type_failure_operands'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $modassign_both_seek(S_initial, 1, 4000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$modassign_both_frontier(S, 1)',
        'S.TODO = (' + marker(0) + ') :: ptask_tail*',
        'n_bits_left = 4623226492472524800', 'i_left = 12',
        'pintegeroperation.OP = MODULO', 'pintegeroperation.LINE = 25', '~pintegeroperation.SWAPPED',
        '$lookup(S.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S.ENV, $ptascii("second")) = (n_second_cell)',
        'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        'S.STORE[n_target] = DEFINED (PFLOAT n_bits_left)',
        'S.STORE[n_right] = DEFINED (PFLOAT 4620974692658839552)',
        snapshot + '(S, pintegeroperation, n_target, n_right) = eps',
        '$call_task_valid(S, ' + marker(0) + ')', '$task_nodes(' + marker(0) + ') = eps',
        'S_first_budget = $drive_steps(S, 1)', 'S_first_budget.COMPLETION = BUDGET',
        'S_first = S_first_budget[.COMPLETION = NORMAL]', '$modassign_both_frontier(S_first, 2)',
        'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(1), 'perrorcall.TARGET = eps',
        'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = $ptascii("Implicit conversion from float 12.5 to int loses precision")',
        '$error_call_valid(S_first, perrorcall)',
        'S_entered_found = $modassign_both_seek(S_first, 3, 4000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', '$modassign_both_entered(S_entered.FRAMES, 0)',
        'S_return_found = $modassign_both_seek(S_entered, 4, 4000)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]', '$modassign_both_frontier(S_return, 4)',
        'S_return.TODO = (' + marker(1) + ') :: ptask_tail*',
        'S_return.CURRENT = eps', 'S_return.FRAMES = eps',
        'S_return.STORE[n_target] = DEFINED (PBOOL true)',
        'S_return.STORE[n_right] = DEFINED pvalue_right',
        'pvalue_right = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("bad5"))',
        'S_return.STRINGDATA[n_string] = $ptascii("bad5")',
        '$string_carrier_valid(S_return, pvalue_right)',
        '$string_long($ptascii("bad5")) = STRINTERROR', '$integer_conversion(pvalue_right) = eps',
        'S_return.STORE[n_v] = DEFINED (PINT 100)', 'S_return.STORE[n_calls] = DEFINED (PINT 1)',
        '$lookup(S_return.ENV, $ptascii("alias")) = (n_target)',
        'n_target <- S_return.REFCELLS', '~(n_right <- S_return.REFCELLS)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_target) = 2',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_right) = 1',
        snapshot + '(S_return, pintegeroperation, n_target, n_right) = ((PBOOL true, pvalue_right))',
        '$modassign_warning_ready(S_return, pintegeroperation, n_target, n_right) = eps',
        '$modassign_both_right_snapshot(S_return, pintegeroperation, n_target, n_right) = eps',
        '$modassign_both_integral_snapshot(S_return, pintegeroperation, n_target, n_right) = eps',
        '$bothassign_quiet_scalar_snapshot(S_return, pintegeroperation, n_target, n_right) = eps',
        '$bothassign_quiet_string_snapshot(S_return, pintegeroperation, n_target, n_right) = eps',
        '$bothassign_leading_string_snapshot(S_return, pintegeroperation, n_target, n_right) = eps',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
    ]
    for value in ['PNULL', 'PBOOL true', 'PINT 5', 'PFLOAT 9221120237041090560', 'PSTRING ($ptascii("5"))', 'PSTRING ($ptascii("5tail"))', 'PSTRING ($ptascii("5.5"))', 'POBJECT n_second', 'PARRAY (|S_return.ARRAYS|)', 'PUNDEFINED']:
        checks += [snapshot + f'(S_return[.STORE[n_right] = DEFINED ({value})], pintegeroperation, n_target, n_right) = eps']
    checks += [
        snapshot + '(S_return[.STRINGDATA[n_string] = $ptascii("other")], pintegeroperation, n_target, n_right) = eps',
        snapshot + '(S_return[.STORE[n_right] = DEFINED (PSTRING_CARRIER (REQUEST_STRING (|S_return.STRINGDATA|)) ($ptascii("bad5")))], pintegeroperation, n_target, n_right) = eps',
        snapshot + '(S_return[.STORE[n_right] = DEFINED (PSTRING ($ptascii("bad5")))], pintegeroperation, n_target, n_right) = ((PBOOL true, PSTRING ($ptascii("bad5"))))',
    ]
    for state in ['S_return[.REFCELLS = S_return.REFCELLS ++ [n_right]]', 'S_return[.ALLOCATIONS = eps]', 'S_return[.ENV = eps][.GLOBALTABLE = eps]', 'S_return[.PROPREFS = [{CELL n_target, SOURCES eps}]]', 'S_return[.STORE[n_target] = DEFINED (POBJECT n_second)]']:
        checks += [snapshot + f'({state}, pintegeroperation, n_target, n_right) = eps']
    checks += [
        snapshot + '(S_return, pintegeroperation, n_v, n_right) = eps',
        snapshot + '(S_return, pintegeroperation, n_target, n_v) = eps',
        'S_step_budget = $drive_steps(S_return, 1)', 'S_step_budget.COMPLETION = BUDGET',
        'S_step = S_step_budget[.COMPLETION = NORMAL]', '$modassign_both_frontier(S_step, 10)',
        'S_step.TODO = (THROW_SEARCH n_error) :: ptask_tail*', '~$modassign_both_tasks(S_step.TODO)',
        'S_step.RESULT = KNOWN PNULL', 'n_error = |S_return.OBJECTS|',
        'S_step.OBJECTS[n_error] = THROWABLE pthrowable',
        'S_step.OBJECTS = S_return.OBJECTS ++ [THROWABLE pthrowable]',
        'pthrowable.KIND = "TypeError"', 'pthrowable.ORIGIN = (pintegeroperation.SITE)',
        '$throwable_field(S_step, n_error, "line") = PINT 25',
        '$string_bytes($throwable_field(S_step, n_error, "message")) = ($ptascii("Unsupported operand types: bool % string"))',
        '$throwable_previous_id(S_step, n_error) = eps',
        '$heap_owners($heap_prune($heap_graph(S_step)), HOBJECT n_error) = 1',
        'S_step.STORE = S_return.STORE', 'S_step.ENV = S_return.ENV',
        'S_step.REFCELLS = S_return.REFCELLS', 'S_step.EVENTS = S_return.EVENTS',
        'S_step.STRINGDATA = S_return.STRINGDATA',
        'S_step.ARRAYS[0:|S_return.ARRAYS|] = S_return.ARRAYS',
        '$string_carrier_valid(S_step, pvalue_right)',
        '$heap_owners($heap_prune($heap_graph(S_step)), HCELL n_target) = 2',
        '$heap_owners($heap_prune($heap_graph(S_step)), HCELL n_right) = 1',
        '$call_descriptors_valid(S_step)', '$heap_valid($heap_graph(S_step))',
        'S_done = $drive_steps(S_step, 4000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_target)',
        '$lookup(S_done.ENV, $ptascii("alias")) = (n_target)',
        'S_done.STORE[n_target] = DEFINED (PINT 7)',
        'S_done.STORE[n_right] = DEFINED pvalue_right', 'S_done.STORE[n_v] = DEFINED (PINT 100)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)', '$string_carrier_valid(S_done, pvalue_right)',
        '$bitassign_both_deprecations(S_done.EVENTS) = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]', '$drive_steps(S, 4000) = S_done',
        '$drive_steps(S_first, 4000) = S_done', '$drive_steps(S_entered, 4000) = S_done',
        '$drive_steps(S_return, 4000) = S_done',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path, required=True)
    args, _ = parser.parse_known_args()
    watched = [Path(__file__), Path(cases.__file__), Path(shared.__file__)]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    shared.cases, shared.CASES, shared.HELPERS, shared.conditions = cases, CASES, HELPERS, conditions
    passed = shared.main()
    assert before == {str(path): digest(path) for path in watched}
    report = json.loads((args.output / 'report.json').read_bytes())
    report['delayed_failure_inputs'] = before
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
