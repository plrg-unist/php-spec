#!/usr/bin/env python3
"""Production power-number capture, deprecation dispatch and cancellation fronts."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import power_warning_cases as cases
import arithmetic_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $power_task(ptask) : bool
def $power_task(POWER_WARNING pintegeroperation pnumber_left pnumber_right n) = true
def $power_task(ERROR_HANDLER_INVOKE perrorcall) = $power_task(perrorcall.RESUME)
def $power_task(ERROR_HANDLER_RESULT perrorcall) = $power_task(perrorcall.RESUME)
def $power_task(ERROR_HANDLER_CLEAN perrorcall) = $power_task(perrorcall.RESUME)
def $power_task(ptask) = false -- otherwise
dec $power_tasks(ptask*) : bool
def $power_tasks(eps) = false
def $power_tasks(ptask :: ptask_tail*) = ($power_task(ptask) \/ $power_tasks(ptask_tail*))
dec $power_handler_frame(pframe) : bool
def $power_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = POWER_WARNING pintegeroperation pnumber_left pnumber_right 1
  -- if perrorcall.TARGET =/= eps
def $power_handler_frame(pframe) = false -- otherwise
dec $power_entered(pframe*) : bool
def $power_entered(eps) = false
def $power_entered(pframe :: pframe_tail*) = ($power_handler_frame(pframe) \/ $power_entered(pframe_tail*))
dec $power_frontier(pstate, nat) : bool
def $power_frontier(S, 0) = ($power_warning_plan(S) =/= eps)
def $power_frontier(S, 1) = true
  -- if S.TODO = (POWER_WARNING pintegeroperation pnumber_left pnumber_right 0) :: ptask_tail*
def $power_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = POWER_WARNING pintegeroperation pnumber_left pnumber_right 1
  -- if perrorcall.TARGET = eps
def $power_frontier(S, 3) = (S.CURRENT =/= eps /\ $power_entered(S.FRAMES))
def $power_frontier(S, 4) = true
  -- if S.TODO = (POWER_WARNING pintegeroperation pnumber_left pnumber_right 1) :: ptask_tail*
def $power_frontier(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprBinaryOpPow expression_left expression_right metadata)
  -- if S.RESULT = KNOWN (PFLOAT n)
  -- if ~$power_tasks(S.TODO)
def $power_frontier(S, 6) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if ~$power_tasks(S.TODO)
def $power_frontier(S, n) = false -- otherwise
dec $power_seek(pstate, nat, nat) : pstate
def $power_seek(S, n_stage, n) = S -- if $power_frontier(S, n_stage)
def $power_seek(S, n_stage, n) = S
  -- if ~$power_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $power_seek(S, n_stage, n) = S
  -- if ~$power_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $power_seek(S, n_stage, n) = $power_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$power_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    thrown = name.endswith('-throw')
    line = 13 if thrown else 12
    def marker(stage, op='pintegeroperation', base='(NINT 0)', exponent='(NINT (-2))'):
        return f'POWER_WARNING {op} {base} {exponent} {stage}'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $power_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]', '$power_frontier(S_entry, 0)',
        '$power_warning_plan(S_entry) = ((pintegeroperation, NINT 0, NINT (-2)))',
        'pintegeroperation.OP = POWER', '~pintegeroperation.SWAPPED', 'pintegeroperation.LINE = ' + str(line),
        'pintegeroperation.LEFT = VARIABLE ($ptascii("base")) ' + str(line - 1),
        'pintegeroperation.RIGHT = VARIABLE ($ptascii("exponent")) ' + str(line),
        'pintegeroperation.LEFTPOINTER = INTEGER_CV ($ptascii("base"))',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CV ($ptascii("exponent"))',
        '$lookup(S_entry.ENV, $ptascii("base")) = (n_base)',
        '$lookup(S_entry.ENV, $ptascii("exponent")) = (n_exponent)', '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'S_entry.STORE[n_base] = DEFINED (PINT 0)', 'S_entry.STORE[n_exponent] = DEFINED (PINT (-2))',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '~(n_base <- S_entry.REFCELLS)', '~(n_exponent <- S_entry.REFCELLS)',
        '$num_pow(NINT 0, NINT (-2)) = (NFLOAT 9218868437227405312, true)',
        '$power_warning_source(S_entry, pintegeroperation)', '$power_warning_snapshot(S_entry, pintegeroperation, NINT 0, NINT (-2))',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$power_warning_plan(S_entry[.RESULT = KNOWN (PINT (-2))]) = eps',
        '$power_warning_plan(S_entry[.REFCELLS = S_entry.REFCELLS ++ [n_base]]) = eps',
        '$power_warning_plan(S_entry[.STORE[n_exponent] = UNDEFINED]) = eps',
        'S_capture_budget = $drive_steps(S_entry, 1)', 'S_capture_budget.COMPLETION = BUDGET',
        'S_capture = S_capture_budget[.COMPLETION = NORMAL]', '$power_frontier(S_capture, 1)',
        'S_capture.TODO = (' + marker(0) + ') :: ptask_tail*',
        'S_capture.RESULT = KNOWN PNULL', 'S_capture.BASE = BASE_VALUE (KNOWN PNULL)',
        '$task_nodes(' + marker(0) + ') = eps',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_base) = 1',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_exponent) = 1',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
        'pintegeroperation_line = pintegeroperation[.LINE = ' + str(line - 1) + ']',
        'S_line_bad = S_capture[.TODO = (' + marker(0, op='pintegeroperation_line') + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_line_bad))', '~$call_descriptors_valid(S_line_bad)',
        'pintegeroperation_op = pintegeroperation[.OP = MULTIPLY]',
        'S_op_bad = S_capture[.TODO = (' + marker(0, op='pintegeroperation_op') + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_op_bad))', '~$call_descriptors_valid(S_op_bad)',
        'S_base_bad = S_capture[.TODO = (' + marker(0, base='(NFLOAT 0)') + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_base_bad))', '~$call_descriptors_valid(S_base_bad)',
        'S_exponent_bad = S_capture[.TODO = (' + marker(0, exponent='(NINT (-3))') + ') :: ptask_tail*]',
        '$heap_valid($heap_graph(S_exponent_bad))', '~$call_descriptors_valid(S_exponent_bad)',
        '~$power_warning_valid(S_capture, pintegeroperation, NINT 1, NINT (-2), 1)',
        '~$power_warning_valid(S_capture, pintegeroperation, NINT 0, NINT 2, 1)',
        '~$power_warning_valid(S_capture, pintegeroperation, NINT 0, NINT (-2), 2)',
        'S_range_bad = S_capture[.TODO = (POWER_WARNING pintegeroperation (NINT 0) (NINT (-9223372036854775809)) 1) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_range_bad))', '~$call_descriptors_valid(S_range_bad)',
        'S_dispatch_budget = $drive_steps(S_capture, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]', '$power_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ' + marker(1), 'perrorcall.TARGET = eps',
        'perrorcall.SITE = pintegeroperation.SITE', 'perrorcall.LINE = ' + str(line), 'perrorcall.LEVEL = 8192',
        '$error_call_valid(S_dispatch, perrorcall)', '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'perrorcall_cache_bad = perrorcall[.RESUME = ' + marker(1, exponent='(NINT (-3))') + ']',
        'S_dispatch_bad = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall_cache_bad) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_dispatch_bad))', '~$error_call_valid(S_dispatch_bad, perrorcall_cache_bad)', '~$call_descriptors_valid(S_dispatch_bad)',
        'perrorcall_message_bad = perrorcall[.MESSAGE = eps][.EVENT = DIAGNOSTIC "Deprecated" eps ' + str(line) + ']',
        'S_message_bad = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall_message_bad) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_message_bad))', '~$error_call_valid(S_message_bad, perrorcall_message_bad)', '~$call_descriptors_valid(S_message_bad)',
        'S_entered_found = $power_seek(S_dispatch, 3, 2000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', '$power_frontier(S_entered, 3)',
        'S_entered.FRAMES = pframe :: pframe_tail*', '$power_handler_frame(pframe)',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_saved*',
        'perrorcall_entered.RESUME = ' + marker(1), 'perrorcall_entered.TARGET =/= eps',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if thrown:
        checks += [
            '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)', 'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            'S_throw_found = $power_seek(S_entered, 6, 2000)',
            r'S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET',
            'S_throw = S_throw_found[.COMPLETION = NORMAL]', '$power_frontier(S_throw, 6)',
            'S_throw.TODO = (THROW_SEARCH n_second) :: ptask_throw*',
            'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps', '~$power_tasks(S_throw.TODO)',
            'S_throw.STORE[n_base] = DEFINED (PINT 2)', 'S_throw.STORE[n_exponent] = DEFINED (PINT 3)',
            'S_throw.STORE[n_v] = DEFINED (PINT 100)',
            '$throwable_live(S_throw, n_second)', '$throwable_previous_id(S_throw, n_second) = eps',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
            'S_throw.ERRORHANDLER = S_entry.ERRORHANDLER',
            '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
            'S_done = $drive_steps(S_throw, 2000)', '$drive_steps(S_dispatch, 2000) = S_done',
            'S_done.STORE[n_v] = DEFINED (PINT 100)',
        ]
    else:
        checks += [
            'S_return_found = $power_seek(S_entered, 4, 2000)',
            r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
            'S_return = S_return_found[.COMPLETION = NORMAL]', '$power_frontier(S_return, 4)',
            'S_return.TODO = (' + marker(1) + ') :: ptask_tail*',
            'S_return.STORE[n_base] = DEFINED (PINT 2)', 'S_return.STORE[n_exponent] = DEFINED (PINT 3)',
            'S_return.STORE[n_v] = DEFINED (PINT 100)',
            '$power_warning_valid(S_return, pintegeroperation, NINT 0, NINT (-2), 1)',
            '~$power_warning_valid(S_return, pintegeroperation, NINT 0, NINT (-2), 0)',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
            'S_result_budget = $drive_steps(S_return, 1)', 'S_result_budget.COMPLETION = BUDGET',
            'S_result = S_result_budget[.COMPLETION = NORMAL]', '$power_frontier(S_result, 5)',
            'S_result.TODO = ptask_tail*', 'S_result.RESULT = KNOWN (PFLOAT 9218868437227405312)',
            'S_result.STORE = S_return.STORE', 'S_result.ALLOCATIONS = S_return.ALLOCATIONS',
            'S_result.EVENTS = S_return.EVENTS', 'S_result.STORE[n_v] = DEFINED (PINT 100)',
            '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
            'S_done = $drive_steps(S_result, 2000)', '$drive_steps(S_return, 2000) = S_done',
            'S_done.STORE[n_v] = DEFINED (PFLOAT 9218868437227405312)',
        ]
    checks += [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_base] = DEFINED (PINT 2)', 'S_done.STORE[n_exponent] = DEFINED (PINT 3)',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]', '$drive_steps(S_capture, 2000) = S_done',
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
    report['power_inputs'] = before
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
