#!/usr/bin/env python3
"""Explicit integer-cast range Warning preserves the original double."""
import base64
import json

import int_cast_range_warning_cases as cases
import bitnot_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
def $bitnot_task(INT_CAST_RANGE_WARNING pbitnotwarning n) = true
def $bitnot_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = INT_CAST_RANGE_WARNING pbitnotwarning 1
  -- if perrorcall.TARGET =/= eps
dec $int_cast_range_frontier(pstate, nat) : bool
def $int_cast_range_frontier(S, 0) = ($int_cast_range_plan(S) =/= eps)
def $int_cast_range_frontier(S, 1) = true
  -- if S.TODO = (INT_CAST_RANGE_WARNING pbitnotwarning 0) :: ptask_tail*
def $int_cast_range_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = INT_CAST_RANGE_WARNING pbitnotwarning 1
  -- if perrorcall.TARGET = eps
def $int_cast_range_frontier(S, 4) = true
  -- if S.TODO = (INT_CAST_RANGE_WARNING pbitnotwarning 1) :: ptask_tail*
def $int_cast_range_frontier(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprCastInt expression metadata)
  -- if S.RESULT = KNOWN (PINT i)
  -- if ~$bitnot_tasks(S.TODO)
def $int_cast_range_frontier(S, n) = $bitnot_frontier(S, n)
  -- if n = 3 \/ n = 6
def $int_cast_range_frontier(S, n) = false -- otherwise
dec $int_cast_range_seek(pstate, nat, nat) : pstate
def $int_cast_range_seek(S, n_stage, n) = S -- if $int_cast_range_frontier(S, n_stage)
def $int_cast_range_seek(S, n_stage, n) = S
  -- if ~$int_cast_range_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $int_cast_range_seek(S, n_stage, n) = S
  -- if ~$int_cast_range_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $int_cast_range_seek(S, n_stage, n) = $int_cast_range_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$int_cast_range_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
dec $int_cast_range_diagnostic(pevent, text) : nat
def $int_cast_range_diagnostic(DIAGNOSTIC text n_message* z, text) = 1
def $int_cast_range_diagnostic(DIAGNOSTIC_SOURCE n_source text n_message* z, text) = 1
def $int_cast_range_diagnostic(DIAGNOSTIC_STACK text n_message* z n_trace*, text) = 1
def $int_cast_range_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n_message* z n_trace*, text) = 1
def $int_cast_range_diagnostic(pevent, text) = 0 -- otherwise
dec $int_cast_range_diagnostics(pevent*, text) : nat
def $int_cast_range_diagnostics(eps, text) = 0
def $int_cast_range_diagnostics(pevent :: pevent_tail*, text) = $($int_cast_range_diagnostic(pevent, text) + $int_cast_range_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $int_cast_range_seek({before}, {stage}, 3000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$int_cast_range_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$int_cast_range_plan(S_entry) = (pbitnotwarning)',
        '$bitnot_warning_plan(S_entry) = eps',
        '$bitnot_nan_warning_plan(S_entry) = eps',
        '$bitnot_range_warning_plan(S_entry) = eps',
        '$object_numeric_cast_plan(S_entry) = eps',
        'pbitnotwarning.LINE = 25',
        'pbitnotwarning.INPUT = VARIABLE ($ptascii("x")) 25',
        'pbitnotwarning.BITS = 4890909195324358656',
        'pbitnotwarning.VALUE = $(-9223372036854775808)',
        '$float_long(pbitnotwarning.BITS, false) = ($(-9223372036854775808), [RANGEWARNING])',
        '$string_cast_integer($ptascii("9223372036854775808")) = 9223372036854775807',
        'n_message* = $ptascii("The float 9.223372036854776E+18 is not representable as an int, cast occurred")',
        '$integer_float_notices([RANGEWARNING], pbitnotwarning.BITS) = [(2, n_message*)]',
        '$int_cast_range_source_valid(S_entry, pbitnotwarning)',
        '$bitnot_snapshot(S_entry, pbitnotwarning)',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        'S_entry.STORE[n_x] = DEFINED (PFLOAT pbitnotwarning.BITS)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '~(n_x <- S_entry.REFCELLS)',
        '$integer_pointer_select(S_entry, pbitnotwarning.INPUT) = (INTEGER_CV ($ptascii("x")))',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        'S_entry.EVENTS = eps',
        '$call_descriptors_valid(S_entry)',
        '$heap_valid($heap_graph(S_entry))',
        '$int_cast_range_plan(S_entry[.ORIGIN = eps]) = eps',
        '$int_cast_range_plan(S_entry[.CODE = eps]) = eps',
        '$int_cast_range_plan(S_entry[.RESULT = KNOWN (PFLOAT pbitnotwarning.BITS)]) = eps',
        '$int_cast_range_plan(S_entry[.STORE[n_x] = UNDEFINED]) = eps',
        '$int_cast_range_plan(S_entry[.REFCELLS = [n_x]]) = eps',
        '$int_cast_range_plan(S_entry[.ERRORHANDLER.CALLBACK = eps]) = eps',
        '$int_cast_range_plan(S_entry[.ERRORHANDLER.LEVELS = 8192]) = eps',
        '~$int_cast_range_source_valid(S_entry, pbitnotwarning[.LINE = 24])',
        '~$int_cast_range_source_valid(S_entry, pbitnotwarning[.INPUT = VARIABLE ($ptascii("v")) 25])',
        '~$int_cast_range_source_valid(S_entry, pbitnotwarning[.BITS = 18446744073709551616])',
        '~$int_cast_range_source_valid(S_entry, pbitnotwarning[.VALUE = 0])',
        'pbitnotwarning_inrange = pbitnotwarning[.BITS = 4615063718147915776][.VALUE = 3]',
        '$float_long(pbitnotwarning_inrange.BITS, false) = (3, eps)',
        '$float_long(pbitnotwarning_inrange.BITS, true) = (3, [PRECISIONLOSS])',
        '~$int_cast_range_source_valid(S_entry, pbitnotwarning_inrange)',
        'S_entry.TODO = ptask_old :: ptask_tail*',
        'PhpStep: S_entry ~> S_capture_atomic',
        'S_capture_atomic = S_entry[.TODO = (INT_CAST_RANGE_WARNING pbitnotwarning 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture = S_capture_atomic',
        '$int_cast_range_frontier(S_capture, 1)',
        '$int_cast_range_warning_valid(S_capture, pbitnotwarning, 0)',
        '~$int_cast_range_warning_valid(S_capture, pbitnotwarning, 2)',
        '$task_nodes(INT_CAST_RANGE_WARNING pbitnotwarning 0) = eps',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HCELL n_x) = 1',
        '$call_descriptors_valid(S_capture)',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        '$int_cast_range_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = INT_CAST_RANGE_WARNING pbitnotwarning 1',
        'perrorcall.TARGET = eps',
        'perrorcall.SITE = pbitnotwarning.SITE',
        'perrorcall.LINE = 25',
        'perrorcall.LEVEL = 2',
        'perrorcall.MESSAGE = n_message*',
        'perrorcall.EVENT = DIAGNOSTIC "Warning" n_message* 25',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 8192])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = 24])',
        'S_dispatch.EVENTS = S_entry.EVENTS',
        '$call_descriptors_valid(S_dispatch)',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += [
        '$bitnot_entered(S_entered.FRAMES)',
        'S_entered.CURRENT =/= eps',
        '$call_descriptors_valid(S_entered)',
    ]
    seek('S_return', 'S_entered', 4)
    checks += [
        'S_return.TODO = (INT_CAST_RANGE_WARNING pbitnotwarning 1) :: ptask_tail*',
        'S_return.CURRENT = eps',
        'S_return.FRAMES = eps',
        '$lookup(S_return.ENV, $ptascii("x")) = (n_x)',
        'S_return.STORE[n_x] = DEFINED pvalue_text',
        '$string_bytes(pvalue_text) = (n_text*)',
        'n_text* = $ptascii("9223372036854775808")',
        '$string_cast_integer(n_text*) = 9223372036854775807',
        'S_return.STORE[n_v] = DEFINED (PINT 100)',
        'S_return.STORE[n_calls] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HCELL n_x) = 1',
        '$int_cast_range_source_valid(S_return, pbitnotwarning)',
        '~$bitnot_snapshot(S_return, pbitnotwarning)',
        '~$int_cast_range_warning_valid(S_return, pbitnotwarning, 0)',
        '$int_cast_range_warning_valid(S_return, pbitnotwarning, 1)',
        '$task_nodes(INT_CAST_RANGE_WARNING pbitnotwarning 1) = eps',
        '$int_cast_range_diagnostics(S_return.EVENTS, "Warning") = 1',
        '$int_cast_range_diagnostics(S_return.EVENTS, "Deprecated") = 0',
        'S_return.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_return)',
        '$heap_valid($heap_graph(S_return))',
        'PhpStep: S_return ~> S_result_atomic',
        'S_result_atomic = S_return[.TODO = ptask_tail*][.RESULT = KNOWN (PINT $(-9223372036854775808))][.BASE = BASE_VALUE (KNOWN (PINT $(-9223372036854775808)))]',
    ]
    step('S_result', 'S_return')
    checks += [
        'S_result = S_result_atomic',
        '$int_cast_range_frontier(S_result, 5)',
        '~$bitnot_tasks(S_result.TODO)',
        'S_result.STORE[n_x] = DEFINED pvalue_text',
        'S_result.STORE[n_v] = DEFINED (PINT 100)',
        'S_result.STORE = S_return.STORE',
        'S_result.ENV = S_return.ENV',
        'S_result.ALLOCATIONS = S_return.ALLOCATIONS',
        'S_result.EVENTS = S_return.EVENTS',
        '$call_descriptors_valid(S_result)',
        '$heap_valid($heap_graph(S_result))',
        'S_done = $drive_steps(S_result, 3000)',
        'S_done.COMPLETION = NORMAL',
        'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps',
        'S_done.FRAMES = eps',
        'S_done.CURRENT = eps',
        'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("x")) = (n_x)',
        'S_done.STORE[n_x] = DEFINED (PINT 8)',
        'S_done.STORE[n_v] = DEFINED (PINT $(-9223372036854775808))',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_x) = 1',
        '$int_cast_range_diagnostics(S_done.EVENTS, "Warning") = 1',
        '$int_cast_range_diagnostics(S_done.EVENTS, "Deprecated") = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_return, 0) = S_return[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
