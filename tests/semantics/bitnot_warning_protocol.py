#!/usr/bin/env python3
"""Production float bitwise-NOT capture, callback frames and supplied throw."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import bitnot_warning_cases as cases
import arithmetic_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $bitnot_task(ptask) : bool
def $bitnot_task(BITNOT_WARNING pbitnotwarning n) = true
def $bitnot_task(ERROR_HANDLER_INVOKE perrorcall) = $bitnot_task(perrorcall.RESUME)
def $bitnot_task(ERROR_HANDLER_RESULT perrorcall) = $bitnot_task(perrorcall.RESUME)
def $bitnot_task(ERROR_HANDLER_CLEAN perrorcall) = $bitnot_task(perrorcall.RESUME)
def $bitnot_task(ptask) = false -- otherwise
dec $bitnot_tasks(ptask*) : bool
def $bitnot_tasks(eps) = false
def $bitnot_tasks(ptask :: ptask_tail*) = ($bitnot_task(ptask) \/ $bitnot_tasks(ptask_tail*))
dec $bitnot_handler_frame(pframe) : bool
def $bitnot_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = BITNOT_WARNING pbitnotwarning 1
  -- if perrorcall.TARGET =/= eps
def $bitnot_handler_frame(pframe) = false -- otherwise
dec $bitnot_entered(pframe*) : bool
def $bitnot_entered(eps) = false
def $bitnot_entered(pframe :: pframe_tail*) = ($bitnot_handler_frame(pframe) \/ $bitnot_entered(pframe_tail*))
dec $bitnot_frontier(pstate, nat) : bool
def $bitnot_frontier(S, 0) = ($bitnot_warning_plan(S) =/= eps)
def $bitnot_frontier(S, 1) = true
  -- if S.TODO = (BITNOT_WARNING pbitnotwarning 0) :: ptask_tail*
def $bitnot_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = BITNOT_WARNING pbitnotwarning 1
  -- if perrorcall.TARGET = eps
def $bitnot_frontier(S, 3) = (S.CURRENT =/= eps /\ $bitnot_entered(S.FRAMES))
def $bitnot_frontier(S, 4) = true
  -- if S.TODO = (BITNOT_WARNING pbitnotwarning 1) :: ptask_tail*
def $bitnot_frontier(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprBitwiseNot expression metadata)
  -- if S.RESULT = KNOWN (PINT i)
  -- if ~$bitnot_tasks(S.TODO)
def $bitnot_frontier(S, 6) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if ~$bitnot_tasks(S.TODO)
def $bitnot_frontier(S, n) = false -- otherwise
dec $bitnot_seek(pstate, nat, nat) : pstate
def $bitnot_seek(S, n_stage, n) = S -- if $bitnot_frontier(S, n_stage)
def $bitnot_seek(S, n_stage, n) = S
  -- if ~$bitnot_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $bitnot_seek(S, n_stage, n) = S
  -- if ~$bitnot_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $bitnot_seek(S, n_stage, n) = $bitnot_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$bitnot_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    thrown = name == 'bitnot-float-handler-throw'
    line = 11 if thrown else 10
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $bitnot_seek(S_initial, 0, 2000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_entry = S_found[.COMPLETION = NORMAL]', '$bitnot_frontier(S_entry, 0)',
        '$bitnot_warning_plan(S_entry) = (pbitnotwarning)',
        'pbitnotwarning.LINE = ' + str(line),
        'pbitnotwarning.INPUT = VARIABLE ($ptascii("x")) ' + str(line),
        'pbitnotwarning.BITS = 4612811918334230528',
        'pbitnotwarning.VALUE = 2',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)',
        'S_entry.STORE[n_x] = DEFINED (PFLOAT pbitnotwarning.BITS)',
        '~(n_x <- S_entry.REFCELLS)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        '$bitnot_snapshot(S_entry, pbitnotwarning)',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$bitnot_warning_plan(S_entry[.RESULT = KNOWN PNULL]) = eps',
        '$bitnot_warning_plan(S_entry[.STORE[n_x] = UNDEFINED]) = eps',
        '~$bitnot_source_valid(S_entry, pbitnotwarning[.BITS = 18446744073709551616])',
        '~$bitnot_source_valid(S_entry, pbitnotwarning[.VALUE = 3])',
        '~$bitnot_source_valid(S_entry, pbitnotwarning[.LINE = $(pbitnotwarning.LINE + 1)])',
        '~$bitnot_source_valid(S_entry, pbitnotwarning[.INPUT = VARIABLE ($ptascii("v")) ' + str(line) + '])',
        '~$bitnot_source_valid(S_entry[.ORIGIN = eps], pbitnotwarning)',
        '~$bitnot_source_valid(S_entry[.CODE = eps], pbitnotwarning)',
        'S_capture_budget = $drive_steps(S_entry, 1)', 'S_capture_budget.COMPLETION = BUDGET',
        'S_capture = S_capture_budget[.COMPLETION = NORMAL]', '$bitnot_frontier(S_capture, 1)',
        'S_capture.TODO = (BITNOT_WARNING pbitnotwarning 0) :: ptask_tail*',
        'S_capture.RESULT = KNOWN PNULL', 'S_capture.STORE = S_entry.STORE',
        'S_capture.ALLOCATIONS = S_entry.ALLOCATIONS', 'S_capture.EVENTS = S_entry.EVENTS',
        '$task_nodes(BITNOT_WARNING pbitnotwarning 0) = eps',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_x) = 1',
        '$bitnot_warning_valid(S_capture, pbitnotwarning, 0)',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
        'pbitnotwarning_bad = pbitnotwarning[.BITS = 4609434218613702656][.VALUE = 1]',
        '$bitnot_source_valid(S_capture, pbitnotwarning_bad)',
        '~$bitnot_snapshot(S_capture, pbitnotwarning_bad)',
        'S_capture_bad = S_capture[.TODO = (BITNOT_WARNING pbitnotwarning_bad 0) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_capture_bad))', '~$call_descriptors_valid(S_capture_bad)',
        '~$call_descriptors_valid(S_capture[.TODO = (BITNOT_WARNING pbitnotwarning 2) :: ptask_tail*])',
        'S_dispatch_budget = $drive_steps(S_capture, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]', '$bitnot_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.TARGET = eps', 'perrorcall.RESUME = BITNOT_WARNING pbitnotwarning 1',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        'perrorcall_bad = perrorcall[.RESUME = BITNOT_WARNING pbitnotwarning_bad 1]',
        '~$error_call_valid(S_dispatch, perrorcall_bad)',
        'S_dispatch_bad = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall_bad) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_dispatch_bad))', '~$call_descriptors_valid(S_dispatch_bad)',
        'perrorcall_empty = perrorcall[.MESSAGE = eps][.EVENT = DIAGNOSTIC "Deprecated" eps perrorcall.LINE]',
        '~$error_call_valid(S_dispatch, perrorcall_empty)',
        'S_message_bad = S_dispatch[.TODO = (ERROR_HANDLER_INVOKE perrorcall_empty) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_message_bad))', '~$call_descriptors_valid(S_message_bad)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        'S_entered_found = $bitnot_seek(S_dispatch, 3, 2000)',
        r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
        'S_entered = S_entered_found[.COMPLETION = NORMAL]', '$bitnot_frontier(S_entered, 3)',
        'S_entered.FRAMES = pframe :: pframe_tail*', '$bitnot_handler_frame(pframe)',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_saved*',
        'perrorcall_entered.TARGET =/= eps',
        'perrorcall_entered.RESUME = BITNOT_WARNING pbitnotwarning 1',
        '$call_descriptors_valid(S_entered)', '$heap_valid($heap_graph(S_entered))',
    ]
    if thrown:
        checks += [
            'S_throw_found = $bitnot_seek(S_entered, 6, 2000)',
            r'S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET',
            'S_throw = S_throw_found[.COMPLETION = NORMAL]', '$bitnot_frontier(S_throw, 6)',
            'S_throw.TODO = (THROW_SEARCH n_exception) :: ptask_throw*',
            'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps', '~$bitnot_tasks(S_throw.TODO)',
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
            'S_return_found = $bitnot_seek(S_entered, 4, 2000)',
            r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
            'S_return = S_return_found[.COMPLETION = NORMAL]', '$bitnot_frontier(S_return, 4)',
            'S_return.TODO = (BITNOT_WARNING pbitnotwarning 1) :: ptask_tail*',
            'S_return.STORE[n_x] = DEFINED (PINT 99)', '~$bitnot_snapshot(S_return, pbitnotwarning)',
            '$bitnot_warning_valid(S_return, pbitnotwarning, 1)',
            '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_x) = 1',
            '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
            'S_delivered_budget = $drive_steps(S_return, 1)', 'S_delivered_budget.COMPLETION = BUDGET',
            'S_delivered = S_delivered_budget[.COMPLETION = NORMAL]', '$bitnot_frontier(S_delivered, 5)',
            'S_delivered.TODO = ptask_tail*', 'S_delivered.RESULT = KNOWN (PINT $(-3))',
            'S_delivered.STORE[n_x] = DEFINED (PINT 99)', 'S_delivered.STORE[n_v] = DEFINED (PINT 100)',
            '~$bitnot_tasks(S_delivered.TODO)',
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
    report['bitnot_inputs'] = before
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
