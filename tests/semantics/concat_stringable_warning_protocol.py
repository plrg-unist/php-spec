#!/usr/bin/env python3
"""A completed array Warning admits the live selected Stringable RHS."""
import base64
import json

import concat_stringable_warning_cases as cases
import concat_array_warning_protocol as previous

CASES = tuple(cases.CASES)
HELPERS = previous.HELPERS + r'''
dec $concat_stringable_frontier(pstate, nat) : bool
def $concat_stringable_frontier(S, n) = $concat_array_frontier(S, n) -- if $(n <= 6)
def $concat_stringable_frontier(S, 7) = true
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_right) z) :: (STRINGIFY_RESULT n porigin_right z) :: (CONCAT_AFTER_RIGHT porigin_parent pvalue_left z) :: ptask_tail*
def $concat_stringable_frontier(S, 8) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin_method
  -- if pcallcontext.RECEIVER = (n)
  -- if pcallcontext.CALLSITE = (porigin_right)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n porigin_right z) :: (CONCAT_AFTER_RIGHT porigin_parent pvalue_left z) :: ptask_tail*
def $concat_stringable_frontier(S, 9) = true
  -- if $concat_stringable_frontier(S, 8)
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV, $ptascii("left")) = (n_left)
  -- if S.STORE[n_left] = DEFINED (PINT 9)
  -- if $lookup(S_global.ENV, $ptascii("right")) = (n_right)
  -- if S.STORE[n_right] = DEFINED pvalue
  -- if $string_bytes(pvalue) = ($ptascii("method"))
def $concat_stringable_frontier(S, 10) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (CONCAT_AFTER_RIGHT porigin_parent pvalue_left z) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("B"))
def $concat_stringable_frontier(S, 11) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("ArrayB"))
  -- if ~$concat_array_tasks(S.TODO) /\ ~$concat_array_legacy(S.TODO)
def $concat_stringable_frontier(S, n) = false -- otherwise
dec $concat_stringable_seek(pstate, nat, nat) : pstate
def $concat_stringable_seek(S, n_stage, n) = S -- if $concat_stringable_frontier(S, n_stage)
def $concat_stringable_seek(S, n_stage, n) = S
  -- if ~$concat_stringable_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $concat_stringable_seek(S, n_stage, n) = S
  -- if ~$concat_stringable_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $concat_stringable_seek(S, n_stage, n) = $concat_stringable_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$concat_stringable_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
dec $concat_stringable_diagnostic(pevent) : nat
def $concat_stringable_diagnostic(DIAGNOSTIC "Warning" n_message* z) = 1
def $concat_stringable_diagnostic(DIAGNOSTIC_SOURCE n_source "Warning" n_message* z) = 1
def $concat_stringable_diagnostic(DIAGNOSTIC_STACK "Warning" n_message* z n_trace*) = 1
def $concat_stringable_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source "Warning" n_message* z n_trace*) = 1
def $concat_stringable_diagnostic(pevent) = 0 -- otherwise
dec $concat_stringable_diagnostics(pevent*) : nat
def $concat_stringable_diagnostics(eps) = 0
def $concat_stringable_diagnostics(pevent :: pevent_tail*) = $($concat_stringable_diagnostic(pevent) + $concat_stringable_diagnostics(pevent_tail*))
'''

MARKER = 'CONCAT_ARRAY_LEFT_WARNING porigin_parent poperand_left poperand_right n_right 25 '
CONSUMER = 'CONCAT_AFTER_LEFT porigin_parent poperand_right false 25'


def seek(checks, label, start, stage):
    checks += [
        f'{label}_found = $concat_stringable_seek({start}, {stage}, 3000)',
        f'{label}_found.COMPLETION = NORMAL \\/ {label}_found.COMPLETION = BUDGET',
        f'{label} = {label}_found[.COMPLETION = NORMAL]',
        f'$concat_stringable_frontier({label}, {stage})',
    ]


def prefix(program, path):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]
    seek(checks, 'S_entry', 'S_initial', 0)
    checks += [
        'S_entry.ORIGIN = (porigin_parent)',
        'poperand_left = VARIABLE ($ptascii("left")) 24',
        'poperand_right = VARIABLE ($ptascii("right")) 25',
        '$origin_child((porigin_parent), [PCFIELD 0]) = (porigin_left)',
        '$origin_child((porigin_parent), [PCFIELD 1]) = (porigin_right)',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("casts")) = (n_casts)',
        'S_entry.STORE[n_left] = DEFINED (PARRAY n_array)',
        'S_entry.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_calls] = DEFINED (PINT 0)', 'S_entry.STORE[n_casts] = DEFINED (PINT 0)',
        '$concat_array_string(S_entry, poperand_right) = (n_right, pvalue_before)',
        '$string_bytes(pvalue_before) = ($ptascii("before"))',
        '~$concat_array_right_stringable(S_entry, poperand_right, n_right)',
        '$concat_array_plan(S_entry) = ((porigin_left, ' + MARKER + '0, ' + CONSUMER + '))',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HARRAY n_array) = 1',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_right) = 1',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'S_capture_budget = $drive_steps(S_entry, 1)', 'S_capture_budget.COMPLETION = BUDGET',
        'S_capture = S_capture_budget[.COMPLETION = NORMAL]',
        'S_capture.TODO = (' + MARKER + '0) :: (' + CONSUMER + ') :: ptask_tail*',
        'S_capture.STORE = S_entry.STORE', 'S_capture.ARRAYS = S_entry.ARRAYS',
        'S_capture.ALLOCATIONS = S_entry.ALLOCATIONS',
        '$task_nodes(' + MARKER + '0) = eps',
        '$concat_array_left_fresh(S_capture, poperand_left, poperand_right, n_right)',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
        'S_dispatch_budget = $drive_steps(S_capture, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: (' + CONSUMER + ') :: ptask_tail*',
        'perrorcall.RESUME = ' + MARKER + '1', 'perrorcall.TARGET = eps',
        'perrorcall.SITE = porigin_left', 'perrorcall.LINE = 25', 'perrorcall.LEVEL = 2',
        'perrorcall.MESSAGE = $ptascii("Array to string conversion")',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
    ]
    seek(checks, 'S_enteredH', 'S_dispatch', 3)
    checks += [
        'S_enteredH.FRAMES = pframe_h :: pframe_h_tail*',
        'pframe_h.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: (' + CONSUMER + ') :: ptask_saved*',
        'perrorcall_entered.RESUME = ' + MARKER + '1', 'perrorcall_entered.TARGET =/= eps',
        '$heap_owners($heap_prune($heap_graph(S_enteredH)), HARRAY n_array) = 1',
        '$call_descriptors_valid(S_enteredH)', '$heap_valid($heap_graph(S_enteredH))',
    ]
    return checks


def returned_h(checks):
    seek(checks, 'S_return', 'S_enteredH', 4)
    checks += [
        'S_return.TODO = (' + MARKER + '1) :: (' + CONSUMER + ') :: ptask_tail*',
        '$lookup(S_return.ENV, $ptascii("left")) = eps',
        '$lookup(S_return.ENV, $ptascii("right")) = (n_right)',
        'S_return.STORE[n_right] = DEFINED (POBJECT n_object)',
        '$stringable_instance(S_return, n_object)',
        'S_return.STORE[n_v] = DEFINED (PINT 100)',
        'S_return.STORE[n_calls] = DEFINED (PINT 1)', 'S_return.STORE[n_casts] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_array) = 0',
        '$heap_owners($heap_prune($heap_graph(S_return)), HOBJECT n_object) = 1',
        '$concat_array_right_stringable(S_return, poperand_right, n_right)',
        '~$concat_array_right_cell(S_return, poperand_right, n_right)',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'S_result_budget = $drive_steps(S_return, 1)', 'S_result_budget.COMPLETION = BUDGET',
        'S_result = S_result_budget[.COMPLETION = NORMAL]',
        'S_result.TODO = (' + CONSUMER + ') :: ptask_tail*',
        'pvalue_array = PSTRING_CARRIER INTERNED_STRING ($ptascii("Array"))',
        'S_result.RESULT = KNOWN pvalue_array', 'S_result.BASE = BASE_VALUE (KNOWN pvalue_array)',
        'S_result.STORE = S_return.STORE', 'S_result.ALLOCATIONS = S_return.ALLOCATIONS',
        'S_result.EVENTS = S_return.EVENTS', 'S_result.STORE[n_v] = DEFINED (PINT 100)',
        '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
    ]
    seek(checks, 'S_pending', 'S_result', 7)
    checks += [
        'S_pending.ORIGIN = (porigin_right)',
        'S_pending.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method) eps 0 eps (porigin_right) 25) :: (STRINGIFY_RESULT n_object porigin_right 25) :: (CONCAT_AFTER_RIGHT porigin_parent pvalue_array 25) :: ptask_tail*',
        'S_pending.STORE[n_right] = DEFINED (POBJECT n_object)',
        'S_pending.STORE[n_v] = DEFINED (PINT 100)', 'S_pending.STORE[n_casts] = DEFINED (PINT 0)',
        '(HOBJECT n_object) <- $heap_graph(S_pending).ROOTS',
        '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
    ]


def conditions(name, program, path, stdout):
    assert name in CASES
    checks = prefix(program, path)
    returned_h(checks)
    checks += [
        'S_fresh_object = S_capture[.OBJECTS = S_return.OBJECTS][.ALLOCATIONS = S_capture.ALLOCATIONS ++ [HOBJECT n_object]][.STORE[n_right] = DEFINED (POBJECT n_object)]',
        '$heap_valid($heap_graph(S_fresh_object))',
        '$concat_array_right_stringable(S_fresh_object, poperand_right, n_right)',
        '~$concat_array_left_fresh(S_fresh_object, poperand_left, poperand_right, n_right)',
        '~$call_descriptors_valid(S_fresh_object)',
        '~$concat_array_right_stringable(S_return[.REFCELLS = S_return.REFCELLS ++ [n_right]], poperand_right, n_right)',
        '~$concat_array_right_stringable(S_return[.ALLOCATIONS = eps], poperand_right, n_right)',
        'S_rebound = S_return[.ENV = [BIND ($ptascii("right")) n_v]][.STORE[n_v] = DEFINED (POBJECT n_object)]',
        '~$concat_array_right_stringable(S_rebound, poperand_right, n_right)',
        'S_retyped = S_return[.STORE[n_right] = DEFINED (PINT 9)]',
        'PhpStep: S_retyped ~> S_boundary',
        'S_boundary = S_retyped[.COMPLETION = UNSUPPORTED "concatenation selected right operand"]',
    ]
    seek(checks, 'S_enteredS', 'S_pending', 8)
    checks += [
        'S_enteredS.CURRENT = (pcallcontext_s)', 'pcallcontext_s.RECEIVER = (n_object)',
        'pcallcontext_s.CALLSITE = (porigin_right)',
        '$stringify_chain_valid(S_enteredS, S_enteredS.CURRENT, S_enteredS.FRAMES)',
        'S_enteredS.STORE[n_right] = DEFINED (POBJECT n_object)',
        'S_enteredS.STORE[n_v] = DEFINED (PINT 100)',
        '$call_descriptors_valid(S_enteredS)', '$heap_valid($heap_graph(S_enteredS))',
    ]
    seek(checks, 'S_changed', 'S_enteredS', 9)
    checks += [
        'S_changed.CURRENT = (pcallcontext_changed)', 'pcallcontext_changed.RECEIVER = (n_object)',
        'S_changed.STORE[n_right] = DEFINED pvalue_method', '$string_bytes(pvalue_method) = ($ptascii("method"))',
        'S_changed.STORE[n_casts] = DEFINED (PINT 1)', 'S_changed.STORE[n_v] = DEFINED (PINT 100)',
        '$($heap_owners($heap_prune($heap_graph(S_changed)), HOBJECT n_object) > 0)',
        '$stringify_chain_valid(S_changed, S_changed.CURRENT, S_changed.FRAMES)',
        '$call_descriptors_valid(S_changed)', '$heap_valid($heap_graph(S_changed))',
    ]
    seek(checks, 'S_back', 'S_changed', 10)
    checks += [
        'S_back.TODO = (CONCAT_AFTER_RIGHT porigin_parent pvalue_array 25) :: ptask_tail*',
        'S_back.RESULT = KNOWN pvalue_b', '$string_bytes(pvalue_b) = ($ptascii("B"))',
        'S_back.STORE[n_right] = DEFINED pvalue_method', 'S_back.STORE[n_v] = DEFINED (PINT 100)',
        '$heap_owners($heap_prune($heap_graph(S_back)), HOBJECT n_object) = 0',
        '$call_descriptors_valid(S_back)', '$heap_valid($heap_graph(S_back))',
    ]
    seek(checks, 'S_concat', 'S_back', 11)
    checks += [
        'S_concat.RESULT = KNOWN pvalue_concat', '$string_bytes(pvalue_concat) = ($ptascii("ArrayB"))',
        'S_concat.STORE[n_v] = DEFINED (PINT 100)',
        '$call_descriptors_valid(S_concat)', '$heap_valid($heap_graph(S_concat))',
        'S_done = $drive_steps(S_concat, 3000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_left_end)', 'S_done.STORE[n_left_end] = DEFINED (PINT 8)',
        'S_done.STORE[n_right] = DEFINED pvalue_end', '$string_bytes(pvalue_end) = ($ptascii("end"))',
        'S_done.STORE[n_v] = DEFINED pvalue_concat',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)', 'S_done.STORE[n_casts] = DEFINED (PINT 1)',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$concat_stringable_diagnostics(S_done.EVENTS) = 1',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_return, 3000) = S_done',
    ]
    assert len(checks) == len(set(checks))
    return checks
