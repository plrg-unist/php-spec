#!/usr/bin/env python3
"""Acquired RHS ownership before Warning and through CONCAT's TMP release."""
import base64
import json

import concat_returned_stringable_warning_cases as cases
import integer_operator_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $concat_returned_handler_frame(pframe) : bool
def $concat_returned_handler_frame(pframe) = true
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CONCAT_RETURNED_WARNING pconcatreturned 1
  -- if perrorcall.TARGET =/= eps
def $concat_returned_handler_frame(pframe) = false -- otherwise
dec $concat_returned_entered(pframe*) : bool
def $concat_returned_entered(eps) = false
def $concat_returned_entered(pframe :: pframe_tail*) = ($concat_returned_handler_frame(pframe) \/ $concat_returned_entered(pframe_tail*))
dec $concat_returned_frontier(pstate, nat) : bool
def $concat_returned_frontier(S, 0) = ($concat_returned_plan(S) =/= eps)
def $concat_returned_frontier(S, 1) = true
  -- if S.TODO = (CONCAT_RETURNED_WARNING pconcatreturned 0) :: ptask_tail*
def $concat_returned_frontier(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CONCAT_RETURNED_WARNING pconcatreturned 1
  -- if perrorcall.TARGET = eps
def $concat_returned_frontier(S, 3) = (S.CURRENT =/= eps /\ $concat_returned_entered(S.FRAMES))
def $concat_returned_frontier(S, 4) = true
  -- if S.TODO = (CONCAT_RETURNED_WARNING pconcatreturned 1) :: ptask_tail*
def $concat_returned_frontier(S, 5) = true
  -- if S.TODO = (CONCAT_RETURNED_LEFT pconcatreturned) :: ptask_tail*
  -- if S.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("Array")))
def $concat_returned_frontier(S, 6) = true
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method) eps 0 eps (porigin_right) z) :: (STRINGIFY_RESULT n_object porigin_right z) :: (CONCAT_RETURNED_RIGHT pconcatreturned) :: ptask_tail*
  -- if n_object = pconcatreturned.OBJECT
def $concat_returned_frontier(S, 7) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_object porigin_method
  -- if pcallcontext.RECEIVER = (n_object)
  -- if pcallcontext.CALLSITE = (porigin_right)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n_object porigin_right z) :: (CONCAT_RETURNED_RIGHT pconcatreturned) :: ptask_tail*
  -- if n_object = pconcatreturned.OBJECT
def $concat_returned_frontier(S, 8) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (CONCAT_RETURNED_RIGHT pconcatreturned) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("B"))
def $concat_returned_frontier(S, 9) = true
  -- if S.TODO = (CONCAT_RETURNED_RELEASE pconcatreturned) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("ArrayB"))
def $concat_returned_frontier(S, 10) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (CONCAT_RETURNED_DONE pconcatreturned) :: ptask_tail*
def $concat_returned_frontier(S, 11) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("f")
def $concat_returned_frontier(S, 12) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (CONCAT_RIGHT poperand_left false false 25) :: ptask_tail*
  -- if S.RESULT = KNOWN (POBJECT n)
def $concat_returned_frontier(S, 13) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = CONCAT_RETURNED_RELEASE pconcatreturned
  -- if pdestructionoperation.PENDING = eps
def $concat_returned_frontier(S, n) = false -- otherwise
dec $concat_returned_seek(pstate, nat, nat) : pstate
def $concat_returned_seek(S, n_stage, n) = S -- if $concat_returned_frontier(S, n_stage)
def $concat_returned_seek(S, n_stage, n) = S
  -- if ~$concat_returned_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $concat_returned_seek(S, n_stage, n) = S
  -- if ~$concat_returned_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $concat_returned_seek(S, n_stage, n) = $concat_returned_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$concat_returned_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
dec $concat_returned_diagnostic(pevent) : nat
def $concat_returned_diagnostic(DIAGNOSTIC "Warning" n_message* z) = 1
def $concat_returned_diagnostic(DIAGNOSTIC_SOURCE n_source "Warning" n_message* z) = 1
def $concat_returned_diagnostic(DIAGNOSTIC_STACK "Warning" n_message* z n_trace*) = 1
def $concat_returned_diagnostic(DIAGNOSTIC_STACK_SOURCE n_source "Warning" n_message* z n_trace*) = 1
def $concat_returned_diagnostic(pevent) = 0 -- otherwise
dec $concat_returned_diagnostics(pevent*) : nat
def $concat_returned_diagnostics(eps) = 0
def $concat_returned_diagnostics(pevent :: pevent_tail*) = $($concat_returned_diagnostic(pevent) + $concat_returned_diagnostics(pevent_tail*))
'''

MARKER = 'CONCAT_RETURNED_WARNING pconcatreturned '
CONSUMER = 'CONCAT_RETURNED_LEFT pconcatreturned'


def seek(checks, label, start, stage):
    checks += [
        f'{label}_found = $concat_returned_seek({start}, {stage}, 3000)',
        f'{label}_found.COMPLETION = NORMAL \\/ {label}_found.COMPLETION = BUDGET',
        f'{label} = {label}_found[.COMPLETION = NORMAL]',
        f'$concat_returned_frontier({label}, {stage})',
    ]


def prefix(program, path):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]
    seek(checks, 'S_factory', 'S_initial', 11)
    checks += [
        'S_factory.CURRENT = (pcallcontext_factory)', 'pcallcontext_factory.CALLSITE = (porigin_right)',
        'S_factory_global = $global_table_view(S_factory)',
        '$lookup(S_factory_global.ENV, $ptascii("seed")) = (n_seed)',
        'S_factory.STORE[n_seed] = DEFINED (POBJECT n_object)', '$stringable_instance(S_factory, n_object)',
        '$heap_owners($heap_prune($heap_graph(S_factory)), HOBJECT n_object) = 1',
        '$call_descriptors_valid(S_factory)', '$heap_valid($heap_graph(S_factory))',
    ]
    seek(checks, 'S_factory_return', 'S_factory', 12)
    checks += [
        'S_factory_return.RESULT = KNOWN (POBJECT n_object)',
        'S_factory_return.TODO = (CONCAT_RIGHT poperand_left false false 25) :: ptask_before*',
        '$heap_owners($heap_prune($heap_graph(S_factory_return)), HOBJECT n_object) = 2',
        '$integer_outputs(S_factory_return.EVENTS) = ([80,59])',
        '$call_descriptors_valid(S_factory_return)', '$heap_valid($heap_graph(S_factory_return))',
    ]
    seek(checks, 'S_entry', 'S_factory_return', 0)
    checks += [
        '$concat_returned_plan(S_entry) = (pconcatreturned)',
        'S_entry.ORIGIN = (porigin_parent)', 'pconcatreturned.SITE = porigin_parent',
        'pconcatreturned.LINE = 25', 'pconcatreturned.OBJECT = n_object',
        'poperand_left = VARIABLE ($ptascii("left")) 24', 'pconcatreturned.LEFT = poperand_left',
        '$origin_child((porigin_parent), [PCFIELD 0]) = (porigin_left)',
        '$origin_child((porigin_parent), [PCFIELD 1]) = (porigin_right)',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_entry.ENV, $ptascii("seed")) = (n_seed)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("calls")) = (n_calls)',
        '$lookup(S_entry.ENV, $ptascii("casts")) = (n_casts)',
        '$lookup(S_entry.ENV, $ptascii("drops")) = (n_drops)',
        'S_entry.STORE[n_left] = DEFINED (PARRAY n_array)',
        'S_entry.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
        'S_entry.STORE[n_seed] = DEFINED (POBJECT n_object)',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)', 'S_entry.STORE[n_calls] = DEFINED (PINT 0)',
        'S_entry.STORE[n_casts] = DEFINED (PINT 0)', 'S_entry.STORE[n_drops] = DEFINED (PINT 0)',
        '$concat_returned_source(S_entry, pconcatreturned)', '$concat_returned_fresh(S_entry, pconcatreturned)',
        '$concat_array_plan(S_entry) = eps',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HOBJECT n_object) = 2',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
        'S_capture_budget = $drive_steps(S_entry, 1)', 'S_capture_budget.COMPLETION = BUDGET',
        'S_capture = S_capture_budget[.COMPLETION = NORMAL]',
        'S_capture.TODO = (' + MARKER + '0) :: (' + CONSUMER + ') :: ptask_tail*',
        'S_capture.ORIGIN = (porigin_left)',
        'S_capture.STORE = S_entry.STORE', 'S_capture.ALLOCATIONS = S_entry.ALLOCATIONS',
        '$task_nodes(' + MARKER + '0) = eps', '$task_nodes(' + CONSUMER + ') = [HOBJECT n_object]',
        '$heap_count(HOBJECT n_object, $tasks_nodes(S_capture.TODO)) = 1',
        '$heap_owners($heap_prune($heap_graph(S_capture)), HOBJECT n_object) = 2',
        '$call_descriptors_valid(S_capture)', '$heap_valid($heap_graph(S_capture))',
        'S_dispatch_budget = $drive_steps(S_capture, 1)', 'S_dispatch_budget.COMPLETION = BUDGET',
        'S_dispatch = S_dispatch_budget[.COMPLETION = NORMAL]',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: (' + CONSUMER + ') :: ptask_tail*',
        'perrorcall.RESUME = ' + MARKER + '1', 'perrorcall.TARGET = eps',
        'perrorcall.SITE = porigin_left', 'perrorcall.LINE = 25', 'perrorcall.LEVEL = 2',
        'perrorcall.MESSAGE = $ptascii("Array to string conversion")', '$error_call_valid(S_dispatch, perrorcall)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
    ]
    seek(checks, 'S_enteredH', 'S_dispatch', 3)
    checks += [
        'S_enteredH.FRAMES = pframe_h :: pframe_h_tail*',
        'pframe_h.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: (' + CONSUMER + ') :: ptask_saved*',
        'perrorcall_entered.RESUME = ' + MARKER + '1', 'perrorcall_entered.TARGET =/= eps',
        '$call_descriptors_valid(S_enteredH)', '$heap_valid($heap_graph(S_enteredH))',
    ]
    return checks


def returned_h(checks):
    seek(checks, 'S_return', 'S_enteredH', 4)
    checks += [
        'S_return.TODO = (' + MARKER + '1) :: (' + CONSUMER + ') :: ptask_tail*',
        '$lookup(S_return.ENV, $ptascii("left")) = eps',
        'S_return.STORE[n_seed] = DEFINED pvalue_seed', '$string_bytes(pvalue_seed) = ($ptascii("changed"))',
        'S_return.STORE[n_v] = DEFINED (PINT 100)', 'S_return.STORE[n_calls] = DEFINED (PINT 1)',
        'S_return.STORE[n_casts] = DEFINED (PINT 0)', 'S_return.STORE[n_drops] = DEFINED (PINT 0)',
        '$concat_returned_live(S_return, pconcatreturned)', '~$concat_returned_fresh(S_return, pconcatreturned)',
        '$heap_owners($heap_prune($heap_graph(S_return)), HARRAY n_array) = 0',
        '$heap_owners($heap_prune($heap_graph(S_return)), HOBJECT n_object) = 1',
        '$heap_count(HOBJECT n_object, $tasks_nodes(S_return.TODO)) = 1',
        '$call_descriptors_valid(S_return)', '$heap_valid($heap_graph(S_return))',
        'S_result_budget = $drive_steps(S_return, 1)', 'S_result_budget.COMPLETION = BUDGET',
        'S_result = S_result_budget[.COMPLETION = NORMAL]',
        'S_result.TODO = (' + CONSUMER + ') :: ptask_tail*',
        'pvalue_array = PSTRING_CARRIER INTERNED_STRING ($ptascii("Array"))',
        'S_result.RESULT = KNOWN pvalue_array', 'S_result.BASE = BASE_VALUE (KNOWN pvalue_array)',
        'S_result.STORE = S_return.STORE', 'S_result.ALLOCATIONS = S_return.ALLOCATIONS',
        'S_result.EVENTS = S_return.EVENTS',
    ]
    seek(checks, 'S_pending', 'S_result', 6)
    checks += [
        'S_pending.ORIGIN = (porigin_right)',
        'S_pending.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method) eps 0 eps (porigin_right) 25) :: (STRINGIFY_RESULT n_object porigin_right 25) :: (CONCAT_RETURNED_RIGHT pconcatreturned) :: ptask_tail*',
        '$task_nodes(STRINGIFY_RESULT n_object porigin_right 25) = [HOBJECT n_object]',
        '$task_nodes(CONCAT_RETURNED_RIGHT pconcatreturned) = [HOBJECT n_object]',
        'S_pending.STORE[n_v] = DEFINED (PINT 100)', 'S_pending.STORE[n_drops] = DEFINED (PINT 0)',
        '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
    ]


def conditions(name, program, path, stdout):
    assert name in CASES
    checks = prefix(program, path)
    returned_h(checks)
    checks += [
        '$concat_returned_diagnostics(S_return.EVENTS) = 1',
        'S_callback = S_return[.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: (CONCAT_RETURNED_LEFT pconcatreturned) :: ptask_tail*][.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_capsule = $error_handler_finish(S_callback, perrorcall_entered)',
        'S_capsule.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_cleanup) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_cleanup) :: (ERROR_HANDLER_CLEAN perrorcall_entered) :: (CONCAT_RETURNED_LEFT pconcatreturned) :: ptask_tail*',
        'pdestructionoperation_cleanup.CLEANUP = (pdestructioncleanup)',
        '$concat_array_consumer(S_capsule.TODO, CONCAT_RETURNED_WARNING pconcatreturned 1) = eps',
        '$concat_returned_consumer(S_capsule, pconcatreturned, 1)',
        '$heap_owners($heap_prune($heap_graph(S_capsule)), HOBJECT n_object) = 1',
        '$heap_valid($heap_graph(S_capsule))',
        'S_capsule_exit = S_capsule[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_cleanup) :: (ERROR_HANDLER_CLEAN perrorcall_entered) :: (CONCAT_RETURNED_LEFT pconcatreturned) :: ptask_tail*]',
        '$concat_returned_consumer(S_capsule_exit, pconcatreturned, 1)',
        '~$concat_returned_consumer(S_capsule_exit, pconcatreturned, 0)',
        '~$concat_returned_consumer(S_capsule_exit[.DESTRUCTION.OPERATIONS = eps], pconcatreturned, 1)',
        '~$concat_returned_consumer(S_capsule_exit[.DESTRUCTION.CLEANUPS = eps], pconcatreturned, 1)',
        'pdestructionoperation_bad = pdestructionoperation_cleanup[.SOURCE = ERROR_HANDLER_CLEAN perrorcall_entered]',
        'S_capsule_bad = S_capsule_exit[.DESTRUCTION.OPERATIONS = [pdestructionoperation_bad]][.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_bad) :: (ERROR_HANDLER_CLEAN perrorcall_entered) :: (CONCAT_RETURNED_LEFT pconcatreturned) :: ptask_tail*]',
        '~$concat_returned_consumer(S_capsule_bad, pconcatreturned, 1)',
        '$heap_owners($heap_prune($heap_graph(S_capsule_bad)), HOBJECT n_object) = 1',
        'perrorcall_bad = perrorcall_entered[.RESUME = CONCAT_RETURNED_WARNING pconcatreturned 0]',
        'pdestructioncleanup_resume = pdestructioncleanup[.SOURCE = ERROR_HANDLER_RESULT perrorcall_bad]',
        'pdestructionoperation_resume = pdestructionoperation_cleanup[.SOURCE = ERROR_HANDLER_RESULT perrorcall_bad][.CLEANUP = (pdestructioncleanup_resume)]',
        'S_resume_bad = S_capsule_exit[.DESTRUCTION.OPERATIONS = [pdestructionoperation_resume]][.DESTRUCTION.CLEANUPS = [pdestructioncleanup_resume]][.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_resume) :: (ERROR_HANDLER_CLEAN perrorcall_bad) :: (CONCAT_RETURNED_LEFT pconcatreturned) :: ptask_tail*]',
        '~$concat_returned_consumer(S_resume_bad, pconcatreturned, 1)',
        '$heap_owners($heap_prune($heap_graph(S_resume_bad)), HOBJECT n_object) = 1',
        'pdestructionrelease_bad = pdestructionrelease_cleanup[.ORIGIN = eps]',
        'S_release_bad = S_capsule[.DESTRUCTION.RELEASES = [pdestructionrelease_bad]][.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_bad) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_cleanup) :: (ERROR_HANDLER_CLEAN perrorcall_entered) :: (CONCAT_RETURNED_LEFT pconcatreturned) :: ptask_tail*]',
        '~$concat_returned_consumer(S_release_bad, pconcatreturned, 1)',
        '$heap_owners($heap_prune($heap_graph(S_release_bad)), HOBJECT n_object) = 1',
        '$concat_returned_plan(S_entry[.ORIGIN = eps]) = eps',
        '$concat_returned_plan(S_entry[.CODE = eps]) = eps',
        '$concat_returned_plan(S_entry[.TODO = [CONCAT_PREP poperand_left (REFERENCE n_seed) false false 25]]) = eps',
        '~$concat_returned_source(S_entry, pconcatreturned[.LINE = 26])',
        '~$concat_returned_source(S_entry, pconcatreturned[.SITE = porigin_right])',
        '~$concat_returned_source(S_entry, pconcatreturned[.OBJECT = |S_entry.OBJECTS|])',
        'S_bad_consumer = S_capture[.TODO = [' + MARKER + '0, CONCAT_RETURNED_RIGHT pconcatreturned]]',
        '$heap_valid($heap_graph(S_bad_consumer))',
        '~$concat_returned_warning_valid(S_bad_consumer, pconcatreturned, 0)',
        '~$call_descriptors_valid(S_bad_consumer)',
        '~$concat_returned_warning_valid(S_capture[.REFCELLS = S_capture.REFCELLS ++ [n_left]], pconcatreturned, 0)',
    ]
    seek(checks, 'S_enteredS', 'S_pending', 7)
    checks += [
        'S_enteredS.CURRENT = (pcallcontext_s)',
        'pcallcontext_s.TARGET = METHOD_TARGET n_object porigin_method',
        'pcallcontext_s.RECEIVER = (n_object)', 'pcallcontext_s.CALLSITE = (porigin_right)',
        'S_enteredS.FRAMES = pframe_s :: pframe_s_tail*',
        'pframe_s.TODO = (STRINGIFY_RESULT n_object porigin_right 25) :: (CONCAT_RETURNED_RIGHT pconcatreturned) :: ptask_tail*',
        'S_enteredS.STORE[n_v] = DEFINED (PINT 100)', 'S_enteredS.STORE[n_casts] = DEFINED (PINT 0)',
        'S_enteredS.STORE[n_drops] = DEFINED (PINT 0)',
        '$stringify_chain_valid(S_enteredS, S_enteredS.CURRENT, S_enteredS.FRAMES)',
        '$call_descriptors_valid(S_enteredS)', '$heap_valid($heap_graph(S_enteredS))',
    ]
    seek(checks, 'S_back', 'S_enteredS', 8)
    checks += [
        'S_back.TODO = (CONCAT_RETURNED_RIGHT pconcatreturned) :: ptask_tail*',
        'S_back.RESULT = KNOWN pvalue_b', '$string_bytes(pvalue_b) = ($ptascii("B"))',
        'S_back.STORE[n_v] = DEFINED (PINT 100)', 'S_back.STORE[n_casts] = DEFINED (PINT 1)',
        'S_back.STORE[n_drops] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_back)), HOBJECT n_object) = 1',
        '$heap_count(HOBJECT n_object, $tasks_nodes(S_back.TODO)) = 1',
        '$call_descriptors_valid(S_back)', '$heap_valid($heap_graph(S_back))',
        'S_concat_budget = $drive_steps(S_back, 1)', 'S_concat_budget.COMPLETION = BUDGET',
        'S_concat = S_concat_budget[.COMPLETION = NORMAL]', '$concat_returned_frontier(S_concat, 9)',
        'S_concat.ORIGIN = (porigin_parent)',
        'S_concat.TODO = (CONCAT_RETURNED_RELEASE pconcatreturned) :: ptask_tail*',
        'S_concat.RESULT = KNOWN pvalue_concat', '$string_bytes(pvalue_concat) = ($ptascii("ArrayB"))',
        'S_concat.STORE[n_v] = DEFINED (PINT 100)', 'S_concat.STORE[n_drops] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_concat)), HOBJECT n_object) = 1',
        '$call_descriptors_valid(S_concat)', '$heap_valid($heap_graph(S_concat))',
    ]
    seek(checks, 'S_destructor', 'S_concat', 13)
    checks += [
        'S_destructor.CURRENT = (pcallcontext_d)',
        '$destructor_context_call(pcallcontext_d, S_destructor.CURRENT, S_destructor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object', 'pdestructorcall.OPERATION = (pdestructionoperation)',
        'pdestructionoperation.SOURCE = CONCAT_RETURNED_RELEASE pconcatreturned',
        'pdestructionoperation.PENDING = eps', 'pdestructionoperation.VALUE = KNOWN pvalue_concat',
        'pdestructionoperation.ORIGIN = (porigin_parent)',
        'S_destructor.STORE[n_v] = DEFINED (PINT 100)', 'S_destructor.STORE[n_casts] = DEFINED (PINT 1)',
        'S_destructor.STORE[n_drops] = DEFINED (PINT 0)',
        '$destructor_call_live(S_destructor, pdestructorcall)',
        '$call_descriptors_valid(S_destructor)', '$heap_valid($heap_graph(S_destructor))',
    ]
    seek(checks, 'S_released', 'S_destructor', 10)
    checks += [
        'S_released.RESULT = KNOWN pvalue_concat',
        'S_released.STORE[n_v] = DEFINED (PINT 100)', 'S_released.STORE[n_drops] = DEFINED (PINT 1)',
        '$task_nodes(CONCAT_RETURNED_DONE pconcatreturned) = eps',
        '$heap_owners($heap_prune($heap_graph(S_released)), HOBJECT n_object) = 0',
        '~((HOBJECT n_object) <- S_released.ALLOCATIONS)', 'S_released.DESTRUCTION.OPERATIONS = eps',
        '$call_descriptors_valid(S_released)', '$heap_valid($heap_graph(S_released))',
        'S_done = $drive_steps(S_released, 3000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        'S_done.STORE[n_v] = DEFINED pvalue_concat', 'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        'S_done.STORE[n_casts] = DEFINED (PINT 1)', 'S_done.STORE[n_drops] = DEFINED (PINT 1)',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_left_end)', 'S_done.STORE[n_left_end] = DEFINED (PINT 8)',
        'S_done.STORE[n_seed] = DEFINED pvalue_end', '$string_bytes(pvalue_end) = ($ptascii("end"))',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$concat_returned_diagnostics(S_done.EVENTS) = 1',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_return, 3000) = S_done',
    ]
    assert len(checks) == len(set(checks))
    return checks
