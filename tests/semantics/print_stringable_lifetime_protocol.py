#!/usr/bin/env python3
"""Acquired print operands survive conversion and emission before retirement."""
import base64
import json

import print_stringable_lifetime_cases as cases
import integer_operator_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $print_lifetime_frontier(pstate, nat) : bool
def $print_lifetime_frontier(S, 0) = ($print_owned_plan(S) =/= eps)
def $print_lifetime_frontier(S, 1) = true
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_print) z) :: (STRINGIFY_RESULT n porigin_print z) :: (PRINT_EMIT porigin_print z) :: (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask*
  -- if n = pobstringrelease.OBJECT
def $print_lifetime_frontier(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin_method
  -- if pcallcontext.RECEIVER = (n)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n porigin_print z) :: (PRINT_EMIT porigin_print z) :: (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask*
  -- if n = pobstringrelease.OBJECT
def $print_lifetime_frontier(S, 3) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (STRINGIFY_RESULT n porigin_print z) :: (PRINT_EMIT porigin_print z) :: (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask*
  -- if n = pobstringrelease.OBJECT
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("X;"))
def $print_lifetime_frontier(S, 4) = true
  -- if S.TODO = (PRINT_EMIT porigin_print z) :: (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("X;"))
def $print_lifetime_frontier(S, 5) = true
  -- if S.TODO = (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask*
  -- if S.RESULT = KNOWN (PINT 1)
def $print_lifetime_frontier(S, 6) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = OUTPUT_STRING_RELEASE pobstringrelease
  -- if pdestructorcall.OBJECT = pobstringrelease.OBJECT
  -- if pdestructionoperation.PENDING = eps
def $print_lifetime_frontier(S, 7) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps /\ S.DESTRUCTION.OPERATIONS = eps
  -- if S.RESULT = KNOWN (PINT 1)
  -- if $integer_outputs(S.EVENTS) = ($ptascii("P;S;X;D:1:1;"))
def $print_lifetime_frontier(S, 8) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("f")
def $print_lifetime_frontier(S, n) = false -- otherwise
dec $print_lifetime_seek(pstate, nat, nat) : pstate
def $print_lifetime_seek(S, n_stage, n) = S -- if $print_lifetime_frontier(S, n_stage)
def $print_lifetime_seek(S, n_stage, n) = S
  -- if ~$print_lifetime_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $print_lifetime_seek(S, n_stage, n) = S
  -- if ~$print_lifetime_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $print_lifetime_seek(S, n_stage, n) = $print_lifetime_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$print_lifetime_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def seek(checks, label, start, stage):
    checks += [f'{label}_found = $print_lifetime_seek({start}, {stage}, 3000)',
               f'{label}_found.COMPLETION = NORMAL \\/ {label}_found.COMPLETION = BUDGET',
               f'{label} = {label}_found[.COMPLETION = NORMAL]',
               f'$print_lifetime_frontier({label}, {stage})']


def acquired_prefix(program, path):
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET']
    seek(checks, 'S_factory', 'S_initial', 8)
    checks += ['S_factory.CURRENT = (pcallcontext_f)', 'pcallcontext_f.TARGET = porigin_function',
               'pcallcontext_f.RECEIVER = eps',
               '$call_descriptors_valid(S_factory)', '$heap_valid($heap_graph(S_factory))']
    seek(checks, 'S_entry', 'S_factory', 0)
    checks += [
        'S_entry.TODO = (PRINT_EMIT porigin_print 25) :: ptask_tail*',
        'S_entry.RESULT = KNOWN (POBJECT n_object)',
        'S_entry.ORIGIN = (porigin_print)',
        '$origin_child((porigin_print), [PCFIELD 0]) = (porigin_operand)',
        'pcallcontext_f.CALLSITE = (porigin_operand)',
        'S_entry.OUTPUTBUFFERS = eps',
        '$print_task_valid(S_entry, porigin_print, 25)',
        '$print_owned_source(S_entry, porigin_print, 25)',
        '$print_owned_plan(S_entry) = (pobstringrelease)',
        'pobstringrelease = {OBJECT n_object, CALLER (OUTPUT_VM porigin_print (PRINT_EMIT porigin_print 25) 25), CONTEXT eps, TAIL ptask_tail*}',
        '$task_nodes(OUTPUT_STRING_RELEASE pobstringrelease) = [HOBJECT n_object]',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HOBJECT n_object) = 1',
        '$stringable_instance(S_entry, n_object)',
        '$integer_outputs(S_entry.EVENTS) = ($ptascii("P;"))',
        '$lookup(S_entry.ENV, $ptascii("left")) = eps',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
    ]
    for name in ('v', 'casts', 'drops'):
        checks += [f'$lookup(S_entry.ENV, $ptascii("{name}")) = (n_{name})',
                   f'S_entry.STORE[n_{name}] = DEFINED (PINT {100 if name == "v" else 0})']
    seek(checks, 'S_pendingS', 'S_entry', 1)
    checks += [
        'S_pendingS.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method) eps 0 eps (porigin_print) 25) :: (STRINGIFY_RESULT n_object porigin_print 25) :: (PRINT_EMIT porigin_print 25) :: (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask_tail*',
        '$heap_count(HOBJECT n_object, $tasks_nodes(S_pendingS.TODO)) = 3',
        '$task_nodes(STRINGIFY_RESULT n_object porigin_print 25) = [HOBJECT n_object]',
        '$output_string_release_valid(S_pendingS, pobstringrelease)',
        '$stringify_source(S_pendingS, porigin_print, 25, PRINT_EMIT porigin_print 25)',
        '$stringify_consumer_receiver_valid(S_pendingS, n_object, PRINT_EMIT porigin_print 25)',
        '$output_string_held(S_pendingS, pobstringrelease.CALLER, n_object, (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask_tail*)',
        '$integer_outputs(S_pendingS.EVENTS) = ($ptascii("P;"))',
        'S_pendingS.STORE[n_v] = DEFINED (PINT 100)',
        'S_pendingS.STORE[n_casts] = DEFINED (PINT 0)', 'S_pendingS.STORE[n_drops] = DEFINED (PINT 0)',
        '$call_descriptors_valid(S_pendingS)', '$heap_valid($heap_graph(S_pendingS))',
    ]
    seek(checks, 'S_enteredS', 'S_pendingS', 2)
    checks += [
        'S_enteredS.CURRENT = (pcallcontext_s)',
        'pcallcontext_s.TARGET = METHOD_TARGET n_object porigin_method',
        'pcallcontext_s.RECEIVER = (n_object)', 'pcallcontext_s.CALLSITE = (porigin_print)',
        'S_enteredS.FRAMES = pframe_s :: pframe_tail*',
        'pframe_s.TODO = (STRINGIFY_RESULT n_object porigin_print 25) :: (PRINT_EMIT porigin_print 25) :: (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask_tail*',
        '$heap_count(HOBJECT n_object, $tasks_nodes(pframe_s.TODO)) = 2',
        '$stringify_chain_valid(S_enteredS, S_enteredS.CURRENT, S_enteredS.FRAMES)',
        'S_enteredS.STORE[n_v] = DEFINED (PINT 100)',
        'S_enteredS.STORE[n_casts] = DEFINED (PINT 0)', 'S_enteredS.STORE[n_drops] = DEFINED (PINT 0)',
        '$call_descriptors_valid(S_enteredS)', '$heap_valid($heap_graph(S_enteredS))',
    ]
    return checks


def conditions(name, program, path, stdout):
    assert name in CASES
    checks = acquired_prefix(program, path)
    checks += [
        '~$print_owned_source(S_entry, porigin_operand, 25)',
        '~$print_owned_source(S_entry, porigin_print, 24)',
    ]
    seek(checks, 'S_returnS', 'S_enteredS', 3)
    checks += [
        'S_returnS.TODO = (STRINGIFY_RESULT n_object porigin_print 25) :: (PRINT_EMIT porigin_print 25) :: (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask_tail*',
        'S_returnS.RESULT = KNOWN pvalue_text', '$string_bytes(pvalue_text) = ($ptascii("X;"))',
        'S_returnS.STORE[n_v] = DEFINED (PINT 100)',
        'S_returnS.STORE[n_casts] = DEFINED (PINT 1)', 'S_returnS.STORE[n_drops] = DEFINED (PINT 0)',
        '$lookup(S_returnS.ENV, $ptascii("left")) = eps',
        '$heap_count(HOBJECT n_object, $tasks_nodes(S_returnS.TODO)) = 2',
        '$heap_owners($heap_prune($heap_graph(S_returnS)), HOBJECT n_object) = 2',
        '$integer_outputs(S_returnS.EVENTS) = ($ptascii("P;S;"))',
        '$call_descriptors_valid(S_returnS)', '$heap_valid($heap_graph(S_returnS))',
        # Same reached roots; each tuple component is necessary to recognize a hold.
        '~$output_string_held(S_returnS, OUTPUT_VM porigin_operand (PRINT_EMIT porigin_operand 25) 25, n_object, (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask_tail*)',
        '~$output_string_held(S_returnS, pobstringrelease.CALLER, $(n_object + 1), (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask_tail*)',
        '~$output_string_held(S_returnS[.CURRENT = (pcallcontext_f)], pobstringrelease.CALLER, n_object, (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask_tail*)',
        '~$output_string_held(S_returnS, pobstringrelease.CALLER, n_object, (OUTPUT_STRING_RELEASE pobstringrelease) :: (TRUTH_RESULT false 25) :: ptask_tail*)',
        # Derived nonempty default-buffer view: historical ownership survives it.
        'S_buffer = S_returnS[.OUTPUTBUFFERS = [{ID S_returnS.OUTPUTSEQ, HANDLER eps, CHUNK 0, FLAGS 112, SIZE 16384, BYTES eps}]][.OUTPUTSEQ = $(S_returnS.OUTPUTSEQ + 1)]',
        '$output_state_valid(S_buffer)', '$call_descriptors_valid(S_buffer)', '$heap_valid($heap_graph(S_buffer))',
        '$heap_owners($heap_prune($heap_graph(S_buffer)), HOBJECT n_object) = 2',
        '~$output_positive(S_buffer.OUTPUTBUFFERS)',
        '$output_string_held(S_buffer, pobstringrelease.CALLER, n_object, (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask_tail*)',
        'S_buffer_next = $stringify_return_state(S_buffer, PRINT_EMIT porigin_print 25, pvalue_text, (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask_tail*)',
        'S_buffer_next.TODO = (PRINT_EMIT porigin_print 25) :: (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask_tail*',
        'S_buffer_next.COMPLETION = NORMAL',
        '$heap_count(HOBJECT n_object, $tasks_nodes(S_buffer_next.TODO)) = 1',
        'PhpStep: S_buffer ~> S_buffer_next',
        '$call_descriptors_valid(S_buffer_next)', '$heap_valid($heap_graph(S_buffer_next))',
    ]
    seek(checks, 'S_text', 'S_returnS', 4)
    checks += [
        'S_text.TODO = (PRINT_EMIT porigin_print 25) :: (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask_tail*',
        'S_text.RESULT = KNOWN pvalue_text',
        'S_text.STORE[n_v] = DEFINED (PINT 100)', 'S_text.STORE[n_drops] = DEFINED (PINT 0)',
        '$heap_count(HOBJECT n_object, $tasks_nodes(S_text.TODO)) = 1',
        '$heap_owners($heap_prune($heap_graph(S_text)), HOBJECT n_object) = 1',
        '$integer_outputs(S_text.EVENTS) = ($ptascii("P;S;"))',
        '$call_descriptors_valid(S_text)', '$heap_valid($heap_graph(S_text))',
    ]
    seek(checks, 'S_printed', 'S_text', 5)
    checks += [
        'S_printed.TODO = (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask_tail*',
        'S_printed.RESULT = KNOWN (PINT 1)', 'S_printed.BASE = BASE_VALUE (KNOWN (PINT 1))',
        'S_printed.STORE[n_v] = DEFINED (PINT 100)', 'S_printed.STORE[n_drops] = DEFINED (PINT 0)',
        '$integer_outputs(S_printed.EVENTS) = ($ptascii("P;S;X;"))',
        '$heap_owners($heap_prune($heap_graph(S_printed)), HOBJECT n_object) = 1',
        '$call_descriptors_valid(S_printed)', '$heap_valid($heap_graph(S_printed))',
        # Inspect root loss while retaining print1; drive the genuine eager path below.
        'S_raw = S_printed[.TODO = ptask_tail*]', 'PhpStep: S_printed ~> S_raw',
        'S_raw.RESULT = KNOWN (PINT 1)', 'S_raw.BASE = BASE_VALUE (KNOWN (PINT 1))',
        'S_raw.EVENTS = S_printed.EVENTS',
        '$heap_count(HOBJECT n_object, $tasks_nodes(S_raw.TODO)) = 0',
        '$heap_owners($heap_prune($heap_graph(S_raw)), HOBJECT n_object) = 0',
    ]
    seek(checks, 'S_dtor', 'S_printed', 6)
    checks += [
        'S_dtor.CURRENT = (pcallcontext_dtor)',
        '$destructor_context_call(pcallcontext_dtor, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object', 'pdestructorcall.OPERATION = (pdestructionoperation)',
        'pdestructionoperation.SOURCE = OUTPUT_STRING_RELEASE pobstringrelease',
        'pdestructionoperation.PENDING = eps',
        'pdestructionoperation.VALUE = KNOWN (PINT 1)', 'pdestructionoperation.BASE = BASE_VALUE (KNOWN (PINT 1))',
        'S_dtor.STORE[n_v] = DEFINED (PINT 100)',
        'S_dtor.STORE[n_casts] = DEFINED (PINT 1)', 'S_dtor.STORE[n_drops] = DEFINED (PINT 0)',
        '$integer_outputs(S_dtor.EVENTS) = ($ptascii("P;S;X;"))',
        '$destructor_call_live(S_dtor, pdestructorcall)',
        '$call_descriptors_valid(S_dtor)', '$heap_valid($heap_graph(S_dtor))',
    ]
    seek(checks, 'S_released', 'S_dtor', 7)
    checks += [
        'S_released.TODO = ptask_tail*',
        'S_released.RESULT = KNOWN (PINT 1)', 'S_released.BASE = BASE_VALUE (KNOWN (PINT 1))',
        'S_released.STORE[n_v] = DEFINED (PINT 100)',
        'S_released.STORE[n_casts] = DEFINED (PINT 1)', 'S_released.STORE[n_drops] = DEFINED (PINT 1)',
        '~((HOBJECT n_object) <- S_released.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_released)), HOBJECT n_object) = 0',
        '$output_string_certificate(S_released, pobstringrelease)',
        '$call_descriptors_valid(S_released)', '$heap_valid($heap_graph(S_released))',
        'S_done = $drive_steps(S_released, 3000)', 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.DESTRUCTION.OPERATIONS = eps',
        'S_done.STORE[n_v] = DEFINED (PINT 1)',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_left_end)', 'S_done.STORE[n_left_end] = DEFINED (PINT 8)',
        'S_done.STORE[n_casts] = DEFINED (PINT 1)', 'S_done.STORE[n_drops] = DEFINED (PINT 1)',
        '~((HOBJECT n_object) <- S_done.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HOBJECT n_object) = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_printed, 3000) = S_done',
        '$drive_steps(S_entry, 0) = S_entry[.COMPLETION = BUDGET]',
        '$drive_steps(S_text, 0) = S_text[.COMPLETION = BUDGET]',
        '$drive_steps(S_dtor, 0) = S_dtor[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
