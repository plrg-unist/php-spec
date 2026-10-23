#!/usr/bin/env python3
"""A completed float-copy producer precedes a canceling BITNOT Deprecated."""
import base64
import json

import bitnot_copy_warning_cases as cases
import bitnot_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $bitnot_copy_frontier(pstate, nat) : bool
def $bitnot_copy_frontier(S, 0) = ($bitnot_copy_plan(S) =/= eps)
def $bitnot_copy_frontier(S, n) = $bitnot_frontier(S, n) -- if n =/= 0
dec $bitnot_copy_seek(pstate, nat, nat) : pstate
def $bitnot_copy_seek(S, n_stage, n) = S -- if $bitnot_copy_frontier(S, n_stage)
def $bitnot_copy_seek(S, n_stage, n) = S
  -- if ~$bitnot_copy_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $bitnot_copy_seek(S, n_stage, n) = S
  -- if ~$bitnot_copy_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $bitnot_copy_seek(S, n_stage, n) = $bitnot_copy_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$bitnot_copy_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
dec $bitnot_copy_diagnostic(pevent, text) : nat
def $bitnot_copy_diagnostic(DIAGNOSTIC text n_message* z, text) = 1
def $bitnot_copy_diagnostic(DIAGNOSTIC_SOURCE n_source text n_message* z, text) = 1
def $bitnot_copy_diagnostic(DIAGNOSTIC_STACK text n_message* z n_trace*, text) = 1
def $bitnot_copy_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source text n_message* z n_trace*, text) = 1
def $bitnot_copy_diagnostic(pevent, text) = 0 -- otherwise
dec $bitnot_copy_diagnostics(pevent*, text) : nat
def $bitnot_copy_diagnostics(eps, text) = 0
def $bitnot_copy_diagnostics(pevent :: pevent_tail*, text) = $($bitnot_copy_diagnostic(pevent, text) + $bitnot_copy_diagnostics(pevent_tail*, text))
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, before, stage):
        checks.extend([
            f'{state}_found = $bitnot_copy_seek({before}, {stage}, 3000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$bitnot_copy_frontier({state}, {stage})',
        ])

    def step(state, before):
        checks.extend([
            f'{state}_budget = $drive_steps({before}, 1)',
            f'{state}_budget.COMPLETION = BUDGET',
            f'{state} = {state}_budget[.COMPLETION = NORMAL]',
        ])

    seek('S_entry', 'S_initial', 0)
    checks += [
        '$bitnot_copy_plan(S_entry) = (pbitnotwarning)',
        '$bitnot_warning_plan(S_entry) = eps', '$bitnot_range_warning_plan(S_entry) = eps',
        '$bitnot_nan_warning_plan(S_entry) = eps',
        'pbitnotwarning.LINE = 25',
        'pbitnotwarning.INPUT = KNOWN (PFLOAT pbitnotwarning.BITS)',
        'S_entry.RESULT = pbitnotwarning.INPUT',
        'pbitnotwarning.BITS = 4623226492472524800', 'pbitnotwarning.VALUE = 12',
        '$float_long(pbitnotwarning.BITS, true) = (12, [PRECISIONLOSS])',
        '$long_not(pbitnotwarning.VALUE) = $(-13)',
        '$integer_operand_source(S_entry, pbitnotwarning.SITE, [PCFIELD 0], pbitnotwarning.INPUT)',
        '$integer_pointer_select(S_entry, pbitnotwarning.INPUT) = (INTEGER_COPY (PFLOAT pbitnotwarning.BITS))',
        '$bitnot_source_valid(S_entry, pbitnotwarning)', '$bitnot_snapshot(S_entry, pbitnotwarning)',
        '$lookup(S_entry.ENV, $ptascii("x")) = (n_x)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
        'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        'S_entry.STORE[n_x] = DEFINED (PFLOAT pbitnotwarning.BITS)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)', 'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        '~(n_x <- S_entry.REFCELLS)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_x) = 1',
        '$integer_outputs(S_entry.EVENTS) = ([80,59])',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        '$bitnot_copy_plan(S_entry[.ORIGIN = eps]) = eps',
        '$bitnot_copy_plan(S_entry[.CODE = eps]) = eps',
        '$bitnot_copy_plan(S_entry[.RESULT = KNOWN PNULL]) = eps',
        '$bitnot_copy_plan(S_entry[.RESULT = KNOWN (PINT 12)]) = eps',
        '$bitnot_copy_plan(S_entry[.RESULT = VARIABLE ($ptascii("x")) 25]) = eps',
        '$bitnot_copy_plan(S_entry[.RESULT = KNOWN (PFLOAT 4607182418800017408)]) = eps',
        '$bitnot_copy_plan(S_entry[.RESULT = KNOWN (PFLOAT 18446744073709551616)]) = eps',
        '$bitnot_copy_plan(S_entry[.ERRORHANDLER.CALLBACK = eps]) = eps',
        '$bitnot_copy_plan(S_entry[.ERRORHANDLER.LEVELS = 2]) = eps',
        '~$bitnot_source_valid(S_entry, pbitnotwarning[.LINE = 24])',
        '~$bitnot_source_valid(S_entry, pbitnotwarning[.VALUE = 13])',
        '~$bitnot_source_valid(S_entry, pbitnotwarning[.BITS = 18446744073709551616])',
        '~$bitnot_source_valid(S_entry, pbitnotwarning[.INPUT = VARIABLE ($ptascii("x")) 25])',
        '~$bitnot_source_valid(S_entry, pbitnotwarning[.INPUT = KNOWN PNULL])',
        '~$bitnot_snapshot(S_entry, pbitnotwarning[.INPUT = KNOWN (PFLOAT 4607182418800017408)])',
        'S_entry.TODO = ptask_old :: ptask_tail*', 'PhpStep: S_entry ~> S_capture_atomic',
        'S_capture_atomic = S_entry[.TODO = (BITNOT_WARNING pbitnotwarning 0) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    step('S_capture', 'S_entry')
    checks += [
        'S_capture = S_capture_atomic', '$bitnot_copy_frontier(S_capture, 1)',
        '$bitnot_warning_valid(S_capture, pbitnotwarning, 0)',
        '$bitnot_warning_valid(S_capture, pbitnotwarning, 1)',
        '~$bitnot_warning_valid(S_capture, pbitnotwarning, 2)',
        '$task_nodes(BITNOT_WARNING pbitnotwarning 0) = eps',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
    ]
    step('S_dispatch', 'S_capture')
    checks += [
        '$bitnot_copy_frontier(S_dispatch, 2)',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = BITNOT_WARNING pbitnotwarning 1',
        'perrorcall.TARGET = eps', 'perrorcall.SITE = pbitnotwarning.SITE',
        'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 25',
        'perrorcall.MESSAGE = $ptascii("Implicit conversion from float 12.5 to int loses precision")',
        'perrorcall.EVENT = DIAGNOSTIC "Deprecated" perrorcall.MESSAGE 25',
        '$error_call_valid(S_dispatch, perrorcall)',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S_dispatch, perrorcall[.LINE = 24])',
        'S_dispatch.EVENTS = S_entry.EVENTS', '$call_descriptors_valid(S_dispatch)',
    ]
    seek('S_entered', 'S_dispatch', 3)
    checks += ['$bitnot_entered(S_entered.FRAMES)', 'S_entered.CURRENT =/= eps',
               '$call_descriptors_valid(S_entered)']
    seek('S_throw', 'S_entered', 6)
    checks += [
        'S_throw.TODO = (THROW_SEARCH n_second) :: ptask_caller*',
        'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps', '~$bitnot_tasks(S_throw.TODO)',
        '$lookup(S_throw.ENV, $ptascii("x")) = eps',
        'S_throw.STORE[n_x] = DEFINED (PINT 99)',
        'S_throw.STORE[n_v] = DEFINED (PINT 100)', 'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HCELL n_x) = 0',
        '~((HCELL n_x) <- S_throw.ALLOCATIONS)',
        '$integer_pointer_value(S_throw, INTEGER_CV ($ptascii("x"))) = eps',
        '$integer_pointer_value(S_throw, INTEGER_COPY (PFLOAT pbitnotwarning.BITS)) = (PFLOAT pbitnotwarning.BITS)',
        '$bitnot_source_valid(S_throw, pbitnotwarning)', '$bitnot_snapshot(S_throw, pbitnotwarning)',
        '$bitnot_warning_valid(S_throw, pbitnotwarning, 0)',
        '$bitnot_warning_valid(S_throw, pbitnotwarning, 1)',
        '$error_call_valid(S_throw, perrorcall)',
        '$task_nodes(BITNOT_WARNING pbitnotwarning 1) = eps',
        '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
        '$throwable_live(S_throw, n_second)', '$throwable_previous_id(S_throw, n_second) = eps',
        '$throwable_field(S_throw, n_second, "line") = PINT 20',
        '$bitnot_copy_diagnostics(S_throw.EVENTS, "Deprecated") = 0',
        '$bitnot_copy_diagnostics(S_throw.EVENTS, "Warning") = 0',
        'S_throw.STRINGDATA[0:|S_entry.STRINGDATA|] = S_entry.STRINGDATA',
        '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
        'S_done = $drive_steps(S_throw, 3000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_v] = DEFINED (PINT 100)', 'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        'S_done.STORE[n_x] = DEFINED (PINT 99)',
        '$lookup(S_done.ENV, $ptascii("x")) = (n_x_new)',
        'n_x_new =/= n_x', 'S_done.STORE[n_x_new] = DEFINED (PINT 8)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_x) = 0',
        '~((HCELL n_x) <- S_done.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_x_new) = 1',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_throw, 0) = S_throw[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
