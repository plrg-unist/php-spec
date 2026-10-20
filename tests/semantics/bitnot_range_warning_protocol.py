#!/usr/bin/env python3
"""Range-only bitwise NOT keeps original float semantics across supplied throw."""
import base64
import json

import bitnot_range_warning_cases as cases
import bitnot_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
def $bitnot_task(BITNOT_RANGE_WARNING pbitnotwarning n) = true
def $bitnot_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = BITNOT_RANGE_WARNING pbitnotwarning 1
  -- if perrorcall.TARGET =/= eps
dec $bitnot_range_frontier(pstate, nat) : bool
def $bitnot_range_frontier(S, 0) = ($bitnot_range_warning_plan(S) =/= eps)
def $bitnot_range_frontier(S, 1) = true
  -- if S.TODO = (BITNOT_RANGE_WARNING pbitnotwarning 0) :: ptask_tail*
def $bitnot_range_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = BITNOT_RANGE_WARNING pbitnotwarning 1
  -- if perrorcall.TARGET = eps
def $bitnot_range_frontier(S, 4) = true
  -- if S.TODO = (BITNOT_RANGE_WARNING pbitnotwarning 1) :: ptask_tail*
def $bitnot_range_frontier(S, n) = $bitnot_frontier(S, n)
  -- if n = 3 \/ n = 5 \/ n = 6
def $bitnot_range_frontier(S, n) = false -- otherwise
dec $bitnot_range_seek(pstate, nat, nat) : pstate
def $bitnot_range_seek(S, n_stage, n) = S -- if $bitnot_range_frontier(S, n_stage)
def $bitnot_range_seek(S, n_stage, n) = S
  -- if ~$bitnot_range_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $bitnot_range_seek(S, n_stage, n) = S
  -- if ~$bitnot_range_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $bitnot_range_seek(S, n_stage, n) = $bitnot_range_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$bitnot_range_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET']

    def seek(state, before, stage):
        checks.extend([f'{state}_found = $bitnot_range_seek({before}, {stage}, 3000)',
                       f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
                       f'{state} = {state}_found[.COMPLETION = NORMAL]',
                       f'$bitnot_range_frontier({state}, {stage})'])

    def step(state, before):
        checks.extend([f'{state}_budget = $drive_steps({before}, 1)',
                       f'{state}_budget.COMPLETION = BUDGET',
                       f'{state} = {state}_budget[.COMPLETION = NORMAL]'])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$bitnot_range_warning_plan(S_entry) = (pbitnotwarning)',
        '$bitnot_warning_plan(S_entry) = eps', '$bitnot_nan_warning_plan(S_entry) = eps',
        '$bitnot_range_source_valid(S_entry, pbitnotwarning)', '$bitnot_snapshot(S_entry, pbitnotwarning)',
        'pbitnotwarning.LINE = 25', 'pbitnotwarning.INPUT = VARIABLE ($ptascii("x")) 25',
        'pbitnotwarning.BITS = 9218868437227405312', 'pbitnotwarning.VALUE = 0',
        '$float_long(pbitnotwarning.BITS, true) = (0, [RANGEWARNING])',
        '$integer_float_notices([RANGEWARNING], pbitnotwarning.BITS) = [(2, ($ptascii("The float INF is not representable as an int, cast occurred")))]',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)', '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
        'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        'S_entry.STORE[n_x] = DEFINED (PFLOAT pbitnotwarning.BITS)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)', 'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '~(n_x <- S_entry.REFCELLS)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$bitnot_range_warning_plan(S_entry[.ORIGIN = eps]) = eps',
        '$bitnot_range_warning_plan(S_entry[.CODE = eps]) = eps',
        '$bitnot_range_warning_plan(S_entry[.RESULT = KNOWN (PFLOAT pbitnotwarning.BITS)]) = eps',
        '$bitnot_range_warning_plan(S_entry[.STORE[n_x] = UNDEFINED]) = eps',
        '$bitnot_range_warning_plan(S_entry[.REFCELLS = [n_x]]) = eps',
        '$bitnot_range_warning_plan(S_entry[.ERRORHANDLER.CALLBACK = eps]) = eps',
        '$bitnot_range_warning_plan(S_entry[.ERRORHANDLER.LEVELS = 8192]) = eps',
        '~$bitnot_range_source_valid(S_entry, pbitnotwarning[.LINE = 24])',
        '~$bitnot_range_source_valid(S_entry, pbitnotwarning[.INPUT = VARIABLE ($ptascii("v")) 25])',
        '~$bitnot_range_source_valid(S_entry, pbitnotwarning[.BITS = 18446744073709551616])',
        '~$bitnot_range_source_valid(S_entry, pbitnotwarning[.VALUE = 1])',
        'pbitnotwarning_precision = pbitnotwarning[.BITS = 4615063718147915776][.VALUE = 3]',
        '$bitnot_source_valid(S_entry, pbitnotwarning_precision)',
        '~$bitnot_range_source_valid(S_entry, pbitnotwarning_precision)',
        'pbitnotwarning_nan = pbitnotwarning[.BITS = 9221120237041090560]',
        '$bitnot_nan_source_valid(S_entry, pbitnotwarning_nan)',
        '~$bitnot_range_source_valid(S_entry, pbitnotwarning_nan)',
        'S_entry.TODO = ptask_old :: ptask_tail*', 'PhpStep: S_entry ~> S_atomic_begin',
        'S_atomic_begin = S_entry[.TODO = (BITNOT_RANGE_WARNING pbitnotwarning 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_capture', 'S_entry')
    checks += ['S_capture = S_atomic_begin', '$bitnot_range_frontier(S_capture, 1)',
               '$bitnot_range_warning_valid(S_capture, pbitnotwarning, 0)',
               '$task_nodes(BITNOT_RANGE_WARNING pbitnotwarning 0) = eps',
               '~$bitnot_range_warning_valid(S_capture, pbitnotwarning, 2)']
    step('S_dispatch', 'S_capture')
    checks += ['S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
               'perrorcall.RESUME = BITNOT_RANGE_WARNING pbitnotwarning 1', 'perrorcall.TARGET = eps',
               'perrorcall.LINE = 25', 'perrorcall.LEVEL = 2',
               'perrorcall.MESSAGE = $ptascii("The float INF is not representable as an int, cast occurred")',
               'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE 25',
               '$error_call_valid(S_dispatch, perrorcall)', '$call_descriptors_valid(S_dispatch)',
               '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 8192])',
               '~$error_call_valid(S_dispatch, perrorcall[.LINE = 24])']
    seek('S_entered', 'S_dispatch', 3)
    checks += ['$bitnot_entered(S_entered.FRAMES)', '$call_descriptors_valid(S_entered)']
    seek('S_throw', 'S_entered', 6)
    checks += ['S_throw.TODO = (THROW_SEARCH n_second) :: ptask_caller*',
               'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps', '~$bitnot_tasks(S_throw.TODO)',
               '$lookup(S_throw.ENV, $ptascii("x")) = (n_x)',
               'S_throw.STORE[n_x] = DEFINED (PINT 99)',
               'S_throw.STORE[n_v] = DEFINED (PINT 100)', 'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
               '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_x) = 1',
               '~$bitnot_snapshot(S_throw, pbitnotwarning)',
               '$bitnot_range_warning_valid(S_throw, pbitnotwarning, 1)',
               '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]',
               '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
               '$throwable_live(S_throw, n_second)', '$throwable_previous_id(S_throw, n_second) = eps',
               '$throwable_field(S_throw, n_second, "line") = PINT 20',
               'S_throw.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
               '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
               'S_done = $drive_steps(S_throw, 3000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
               'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
               'S_done.STORE[n_v] = DEFINED (PINT 100)', 'S_done.STORE[n_calls] = DEFINED (PINT 1)',
               'S_done.STORE[n_x] = DEFINED (PINT 8)', '$lookup(S_done.ENV, $ptascii("x")) = (n_x)',
               '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_x) = 1',
               '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
               '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
               '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]']
    assert len(checks) == len(set(checks))
    return checks
