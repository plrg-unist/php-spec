#!/usr/bin/env python3
"""Production unary capture, callback frames, delivery and supplied throw."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import unary_warning_cases as cases
import arithmetic_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $unary_task(ptask) : bool
def $unary_task(ARITHMETIC_UNARY_WARNING punarywarning n) = true
def $unary_task(ERROR_HANDLER_INVOKE perrorcall) = $unary_task(perrorcall.RESUME)
def $unary_task(ERROR_HANDLER_RESULT perrorcall) = $unary_task(perrorcall.RESUME)
def $unary_task(ERROR_HANDLER_CLEAN perrorcall) = $unary_task(perrorcall.RESUME)
def $unary_task(ptask) = false -- otherwise
dec $unary_tasks(ptask*) : bool
def $unary_tasks(eps) = false
def $unary_tasks(ptask :: ptask_tail*) = ($unary_task(ptask) \/ $unary_tasks(ptask_tail*))
dec $unary_handler_frame(pframe) : bool
def $unary_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_UNARY_WARNING punarywarning 1
  -- if perrorcall.TARGET =/= eps
def $unary_handler_frame(pframe) = false -- otherwise
dec $unary_entered(pframe*) : bool
def $unary_entered(eps) = false
def $unary_entered(pframe :: pframe_tail*) = ($unary_handler_frame(pframe) \/ $unary_entered(pframe_tail*))
dec $unary_numeric_operand(poperand) : bool
def $unary_numeric_operand(KNOWN (PINT i)) = true
def $unary_numeric_operand(KNOWN (PFLOAT n)) = true
def $unary_numeric_operand(poperand) = false -- otherwise
dec $unary_frontier(pstate, nat) : bool
def $unary_frontier(S, 0) = ($arithmetic_unary_plan(S) =/= eps)
def $unary_frontier(S, 1) = true
  -- if S.TODO = (ARITHMETIC_UNARY_WARNING punarywarning 0) :: ptask_tail*
def $unary_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ARITHMETIC_UNARY_WARNING punarywarning 1
  -- if perrorcall.TARGET = eps
def $unary_frontier(S, 3) = (S.CURRENT =/= eps /\ $unary_entered(S.FRAMES))
def $unary_frontier(S, 4) = true
  -- if S.TODO = (ARITHMETIC_UNARY_WARNING punarywarning 1) :: ptask_tail*
def $unary_frontier(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (pcnode)
  -- if $arithmetic_unary_kind(pcnode) =/= eps
  -- if $unary_numeric_operand(S.RESULT)
  -- if ~$unary_tasks(S.TODO)
def $unary_frontier(S, 6) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if ~$unary_tasks(S.TODO)
def $unary_frontier(S, n) = false -- otherwise
dec $unary_seek(pstate, nat, nat) : pstate
def $unary_seek(S, n_stage, n) = S -- if $unary_frontier(S, n_stage)
def $unary_seek(S, n_stage, n) = S
  -- if ~$unary_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $unary_seek(S, n_stage, n) = S
  -- if ~$unary_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $unary_seek(S, n_stage, n) = $unary_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$unary_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    thrown = name == 'unary-minus-leading-handler-throw'
    op, other, line = ('NEGATIVE', 'POSITIVE', 11) if thrown else ('POSITIVE', 'NEGATIVE', 10)
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $unary_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]', '$unary_frontier(S_entry, 0)',
        '$arithmetic_unary_plan(S_entry) = (punarywarning)',
        'punarywarning.OP = ' + op, 'punarywarning.LINE = ' + str(line),
        'punarywarning.INPUT = VARIABLE ($ptascii("x")) ' + str(line),
        '$string_bytes(punarywarning.VALUE) = ($ptascii("12tail"))',
        'punarywarning.NUMBER = NINT 12',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)',
        'S_entry.STORE[n_x] = DEFINED punarywarning.VALUE',
        '~(n_x <- S_entry.REFCELLS)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        '$arithmetic_unary_snapshot(S_entry, punarywarning)',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$arithmetic_unary_plan(S_entry[.RESULT = KNOWN PNULL]) = eps',
        '$arithmetic_unary_plan(S_entry[.STORE[n_x] = UNDEFINED]) = eps',
        '~$arithmetic_unary_valid(S_entry, punarywarning[.OP = ' + other + '])',
        '~$arithmetic_unary_valid(S_entry, punarywarning[.LINE = $(punarywarning.LINE + 1)])',
        '~$arithmetic_unary_valid(S_entry, punarywarning[.INPUT = VARIABLE ($ptascii("v")) ' + str(line) + '])',
        '~$arithmetic_unary_valid(S_entry[.ORIGIN = eps], punarywarning)',
        '~$arithmetic_unary_valid(S_entry[.CODE = eps], punarywarning)',
        'S_capture_budget = $drive_steps(S_entry, 1)', 'S_capture_budget.COMPLETION = BUDGET',
        'S_capture = S_capture_budget[.COMPLETION = NORMAL]', '$unary_frontier(S_capture, 1)',
        'S_capture.TODO = (ARITHMETIC_UNARY_WARNING punarywarning 0) :: ptask_tail*',
        'S_capture.RESULT = KNOWN PNULL', 'S_capture.STORE = S_entry.STORE',
        'S_capture.ALLOCATIONS = S_entry.ALLOCATIONS', 'S_capture.EVENTS = S_entry.EVENTS',
        '$task_nodes(ARITHMETIC_UNARY_WARNING punarywarning 0) = eps',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_x) = 1',
        '$arithmetic_unary_warning_valid(S_capture, punarywarning, 0)',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
        'punarywarning_bad = punarywarning[.VALUE = PSTRING ($ptascii("99tail"))][.NUMBER = NINT 99]',
        '$arithmetic_unary_valid(S_capture, punarywarning_bad)',
        '~$arithmetic_unary_snapshot(S_capture, punarywarning_bad)',
        'S_capture_bad = S_capture[.TODO = (ARITHMETIC_UNARY_WARNING punarywarning_bad 0) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_capture_bad))', '~$call_descriptors_valid(S_capture_bad)',
        '~$call_descriptors_valid(S_capture[.TODO = (ARITHMETIC_UNARY_WARNING punarywarning 2) :: ptask_tail*])',
        'S_dispatch_budget = $drive_steps(S_capture, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]', '$unary_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.TARGET = eps', 'perrorcall.RESUME = ARITHMETIC_UNARY_WARNING punarywarning 1',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 8192])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        'perrorcall_bad = perrorcall[.RESUME = ARITHMETIC_UNARY_WARNING punarywarning_bad 1]',
        '~$error_call_valid(S_dispatch, perrorcall_bad)',
        'S_dispatch_bad = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall_bad) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_dispatch_bad))', '~$call_descriptors_valid(S_dispatch_bad)',
        'perrorcall_empty = perrorcall[.MESSAGE = eps][.EVENT = DIAGNOSTIC "Warning" eps perrorcall.LINE]',
        '~$error_call_valid(S_dispatch, perrorcall_empty)',
        'S_message_bad = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall_empty) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_message_bad))', '~$call_descriptors_valid(S_message_bad)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'S_entered_found = $unary_seek(S_dispatch, 3, 2000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', '$unary_frontier(S_entered, 3)',
        'S_entered.FRAMES = pframe :: pframe_tail*', '$unary_handler_frame(pframe)',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_saved*',
        'perrorcall_entered.TARGET =/= eps',
        'perrorcall_entered.RESUME = ARITHMETIC_UNARY_WARNING punarywarning 1',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if thrown:
        checks += [
            'S_throw_found = $unary_seek(S_entered, 6, 2000)',
            r'S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET',
            'S_throw = S_throw_found[.COMPLETION = NORMAL]', '$unary_frontier(S_throw, 6)',
            'S_throw.TODO = (THROW_SEARCH n_exception) :: ptask_throw*',
            'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps', '~$unary_tasks(S_throw.TODO)',
            '$lookup(S_throw.ENV, $ptascii("second")) = (n_second)',
            'S_throw.STORE[n_second] = DEFINED (POBJECT n_exception)',
            '$throwable_previous_id(S_throw, n_exception) = eps',
            '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_exception) = 2',
            '$task_nodes(THROW_SEARCH n_exception) = [HOBJECT n_exception]',
            'S_throw.STORE[n_x] = DEFINED (PINT 99)', 'S_throw.STORE[n_v] = DEFINED (PINT 100)',
            '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
            'S_done = $drive_steps(S_throw, 2000)',
        ]
    else:
        checks += [
            'S_return_found = $unary_seek(S_entered, 4, 2000)',
            r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
            'S_return = S_return_found[.COMPLETION = NORMAL]', '$unary_frontier(S_return, 4)',
            'S_return.TODO = (ARITHMETIC_UNARY_WARNING punarywarning 1) :: ptask_tail*',
            'S_return.STORE[n_x] = DEFINED (PINT 99)', '~$arithmetic_unary_snapshot(S_return, punarywarning)',
            '$arithmetic_unary_warning_valid(S_return, punarywarning, 1)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_x) = 1',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
            'S_delivered_budget = $drive_steps(S_return, 1)', 'S_delivered_budget.COMPLETION = BUDGET',
            'S_delivered = S_delivered_budget[.COMPLETION = NORMAL]', '$unary_frontier(S_delivered, 5)',
            'S_delivered.TODO = ptask_tail*', 'S_delivered.RESULT = KNOWN (PINT 12)',
            'S_delivered.STORE[n_x] = DEFINED (PINT 99)', 'S_delivered.STORE[n_v] = DEFINED (PINT 100)',
            '~$unary_tasks(S_delivered.TODO)',
            '$call_descriptors_valid(S_delivered)', '$heap_valid($heap_graph(S_delivered))',
            'S_done = $drive_steps(S_delivered, 2000)',
        ]
    return checks + [
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_capture, 2000) = S_done', '$drive_steps(S_dispatch, 2000) = S_done',
    ]


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path, required=True)
    args, _ = parser.parse_known_args()
    watched = [Path(__file__), Path(cases.__file__), Path(shared.__file__)]
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    before = {str(p): digest(p) for p in watched}
    shared.cases, shared.CASES, shared.HELPERS, shared.conditions = cases, CASES, HELPERS, conditions
    passed = shared.main()
    assert before == {str(p): digest(p) for p in watched}
    report = json.loads((args.output / 'report.json').read_bytes())
    report['unary_inputs'] = before
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
