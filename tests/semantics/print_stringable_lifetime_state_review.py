#!/usr/bin/env python3
"""Borrowed print's early retirement and acquired print's pending throw."""
import base64
import json

import print_stringable_lifetime_review_cases as cases
import print_stringable_lifetime_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = r'''
dec $print_peer_marker(ptask) : bool
def $print_peer_marker(PRINT_EMIT porigin z) = true
def $print_peer_marker(STRINGIFY_RESULT n porigin z) = true
def $print_peer_marker(OUTPUT_STRING_RELEASE pobstringrelease) = true
def $print_peer_marker(ptask) = false -- otherwise
dec $print_peer_markers(ptask*) : bool
def $print_peer_markers(eps) = false
def $print_peer_markers(ptask :: ptask_tail*) = ($print_peer_marker(ptask) \/ $print_peer_markers(ptask_tail*))
dec $print_peer_frontier(pstate, nat) : bool
def $print_peer_frontier(S, 0) = true
  -- if S.TODO = (PRINT_EMIT porigin z) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if S.RESULT = VARIABLE ptbytes z_input
def $print_peer_frontier(S, 1) = true
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_print) z) :: (STRINGIFY_RESULT n porigin_print z) :: (PRINT_EMIT porigin_print z) :: ptask*
def $print_peer_frontier(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin_method
  -- if pcallcontext.RECEIVER = (n)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n porigin_print z) :: (PRINT_EMIT porigin_print z) :: ptask*
def $print_peer_frontier(S, 3) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (STRINGIFY_RESULT n porigin_print z) :: (PRINT_EMIT porigin_print z) :: ptask*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("X;"))
def $print_peer_frontier(S, 4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = STRINGIFY_RESULT pdestructorcall.OBJECT porigin z
  -- if pdestructionoperation.PENDING = eps
def $print_peer_frontier(S, 5) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps /\ S.DESTRUCTION.OPERATIONS = eps
  -- if S.TODO = (PRINT_EMIT porigin z) :: ptask*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("X;"))
  -- if $integer_outputs(S.EVENTS) = ($ptascii("S;D:1:1;"))
def $print_peer_frontier(S, 6) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps /\ S.DESTRUCTION.OPERATIONS = eps
  -- if S.RESULT = KNOWN (PINT 1)
  -- if $integer_outputs(S.EVENTS) = ($ptascii("S;D:1:1;X;"))
def $print_peer_frontier(S, 7) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n_exception) :: (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask*
def $print_peer_frontier(S, 8) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = OUTPUT_STRING_RELEASE pobstringrelease
  -- if pdestructorcall.OBJECT = pobstringrelease.OBJECT
  -- if pdestructionoperation.PENDING = (n_exception)
def $print_peer_frontier(S, 9) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps /\ S.DESTRUCTION.OPERATIONS = eps
  -- if S.TODO = (THROW_SEARCH n_exception) :: ptask*
  -- if ~$print_peer_markers(S.TODO)
def $print_peer_frontier(S, n) = false -- otherwise
dec $print_peer_seek(pstate, nat, nat) : pstate
def $print_peer_seek(S, n_stage, n) = S -- if $print_peer_frontier(S, n_stage)
def $print_peer_seek(S, n_stage, n) = S
  -- if ~$print_peer_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $print_peer_seek(S, n_stage, n) = S
  -- if ~$print_peer_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $print_peer_seek(S, n_stage, n) = $print_peer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$print_peer_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def seek(checks, label, start, stage):
    checks += [f'{label}_found = $print_peer_seek({start}, {stage}, 3000)',
               f'{label}_found.COMPLETION = NORMAL \\/ {label}_found.COMPLETION = BUDGET',
               f'{label} = {label}_found[.COMPLETION = NORMAL]',
               f'$print_peer_frontier({label}, {stage})']


def borrowed_prefix(program, path):
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET']
    seek(checks, 'S_entry', 'S_initial', 0)
    checks += [
        'S_entry.TODO = (PRINT_EMIT porigin_print 25) :: ptask_tail*',
        'S_entry.RESULT = VARIABLE ($ptascii("left")) 25',
        '$origin_child((porigin_print), [PCFIELD 0]) = (porigin_operand)',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left)',
        'S_entry.STORE[n_left] = DEFINED (POBJECT n_object)',
        'S_entry.OUTPUTBUFFERS = eps',
        '$print_task_valid(S_entry, porigin_print, 25)',
        '~$print_owned_source(S_entry, porigin_print, 25)',
        '$print_owned_plan(S_entry) = eps',
        '$stringable_instance(S_entry, n_object)',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HOBJECT n_object) = 1',
        '$integer_outputs(S_entry.EVENTS) = eps',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
    ]
    for name in ('v', 'casts', 'drops'):
        checks += [f'$lookup(S_entry.ENV, $ptascii("{name}")) = (n_{name})',
                   f'S_entry.STORE[n_{name}] = DEFINED (PINT {100 if name == "v" else 0})']
    seek(checks, 'S_pendingS', 'S_entry', 1)
    checks += [
        'S_pendingS.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method) eps 0 eps (porigin_print) 25) :: (STRINGIFY_RESULT n_object porigin_print 25) :: (PRINT_EMIT porigin_print 25) :: ptask_tail*',
        '$heap_count(HOBJECT n_object, $tasks_nodes(S_pendingS.TODO)) = 2',
        '$task_nodes(STRINGIFY_RESULT n_object porigin_print 25) = [HOBJECT n_object]',
        '$stringify_source(S_pendingS, porigin_print, 25, PRINT_EMIT porigin_print 25)',
        '$stringify_consumer_receiver_valid(S_pendingS, n_object, PRINT_EMIT porigin_print 25)',
        '$call_descriptors_valid(S_pendingS)', '$heap_valid($heap_graph(S_pendingS))',
    ]
    seek(checks, 'S_enteredS', 'S_pendingS', 2)
    checks += [
        'S_enteredS.CURRENT = (pcallcontext_s)',
        'pcallcontext_s.TARGET = METHOD_TARGET n_object porigin_method',
        'pcallcontext_s.RECEIVER = (n_object)', 'pcallcontext_s.CALLSITE = (porigin_print)',
        'S_enteredS.FRAMES = pframe_s :: pframe_s_tail*',
        'pframe_s.TODO = (STRINGIFY_RESULT n_object porigin_print 25) :: (PRINT_EMIT porigin_print 25) :: ptask_tail*',
        '$heap_count(HOBJECT n_object, $tasks_nodes(pframe_s.TODO)) = 1',
        'S_enteredS.STORE[n_v] = DEFINED (PINT 100)',
        'S_enteredS.STORE[n_casts] = DEFINED (PINT 0)',
        'S_enteredS.STORE[n_drops] = DEFINED (PINT 0)',
        '$stringify_chain_valid(S_enteredS, S_enteredS.CURRENT, S_enteredS.FRAMES)',
        '$call_descriptors_valid(S_enteredS)', '$heap_valid($heap_graph(S_enteredS))',
    ]
    return checks


def destructor(checks, source, pending, value):
    checks += [
        'S_dtor.CURRENT = (pcallcontext_d)',
        '$destructor_context_call(pcallcontext_d, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object',
        'pdestructorcall.OPERATION = (pdestructionoperation)',
        'pdestructionoperation.SOURCE = ' + source,
        'pdestructionoperation.PENDING = ' + pending,
        'pdestructionoperation.VALUE = KNOWN ' + value,
        'pdestructionoperation.CALLER = eps',
        'pcallcontext_d.TARGET = METHOD_TARGET n_object porigin_destructor',
        'pcallcontext_d.RECEIVER = (n_object)',
        '$destructor_call_live(S_dtor, pdestructorcall)',
        '$eager_operation_source_valid(S_dtor, pdestructionoperation)',
        'S_dtor.STORE[n_v] = DEFINED (PINT 100)',
        'S_dtor.STORE[n_casts] = DEFINED (PINT 1)',
        'S_dtor.STORE[n_drops] = DEFINED (PINT 0)',
        '$lookup($global_table_view(S_dtor).ENV, $ptascii("left")) = eps',
        '(HOBJECT n_object) <- S_dtor.ALLOCATIONS',
        '$($heap_owners($heap_prune($heap_graph(S_dtor)), HOBJECT n_object) > 0)',
        '$call_descriptors_valid(S_dtor)', '$heap_valid($heap_graph(S_dtor))',
    ]


def conditions(name, program, path, stdout):
    assert name in CASES
    borrowed = name == 'print-borrowed-stringable-unset-control'
    if borrowed:
        checks = borrowed_prefix(program, path)
        seek(checks, 'S_returnS', 'S_enteredS', 3)
        checks += [
            'S_returnS.TODO = (STRINGIFY_RESULT n_object porigin_print 25) :: (PRINT_EMIT porigin_print 25) :: ptask_tail*',
            'S_returnS.RESULT = KNOWN pvalue_text', '$string_bytes(pvalue_text) = ($ptascii("X;"))',
            '$lookup(S_returnS.ENV, $ptascii("left")) = eps',
            'S_returnS.STORE[n_v] = DEFINED (PINT 100)',
            'S_returnS.STORE[n_casts] = DEFINED (PINT 1)',
            'S_returnS.STORE[n_drops] = DEFINED (PINT 0)',
            '$heap_count(HOBJECT n_object, $tasks_nodes(S_returnS.TODO)) = 1',
            '$heap_owners($heap_prune($heap_graph(S_returnS)), HOBJECT n_object) = 1',
            '$integer_outputs(S_returnS.EVENTS) = ($ptascii("S;"))',
            '$call_descriptors_valid(S_returnS)', '$heap_valid($heap_graph(S_returnS))',
            # Inspect the raw loss; resume the reached return state for real D.
            'S_raw = $stringify_return_state(S_returnS, PRINT_EMIT porigin_print 25, pvalue_text, ptask_tail*)',
            'PhpStep: S_returnS ~> S_raw',
            'S_raw.TODO = (PRINT_EMIT porigin_print 25) :: ptask_tail*',
            '$heap_owners($heap_prune($heap_graph(S_raw)), HOBJECT n_object) = 0',
            'S_raw.EVENTS = S_returnS.EVENTS',
        ]
        seek(checks, 'S_dtor', 'S_returnS', 4)
        destructor(checks, 'STRINGIFY_RESULT n_object porigin_print 25', 'eps', 'pvalue_text')
        checks += ['$integer_outputs(S_dtor.EVENTS) = ($ptascii("S;"))']
        seek(checks, 'S_emit', 'S_dtor', 5)
        checks += [
            'S_emit.TODO = (PRINT_EMIT porigin_print 25) :: ptask_tail*',
            'S_emit.RESULT = KNOWN pvalue_text',
            'S_emit.STORE[n_v] = DEFINED (PINT 100)',
            'S_emit.STORE[n_drops] = DEFINED (PINT 1)',
            '~((HOBJECT n_object) <- S_emit.ALLOCATIONS)',
            '$heap_owners($heap_prune($heap_graph(S_emit)), HOBJECT n_object) = 0',
            '$call_descriptors_valid(S_emit)', '$heap_valid($heap_graph(S_emit))',
        ]
        seek(checks, 'S_after', 'S_emit', 6)
        checks += ['S_after.RESULT = KNOWN (PINT 1)',
                   'S_after.STORE[n_v] = DEFINED (PINT 100)',
                   'S_after.STORE[n_drops] = DEFINED (PINT 1)',
                   '$call_descriptors_valid(S_after)', '$heap_valid($heap_graph(S_after))']
    else:
        checks = shared.acquired_prefix(program, path)
        checks += [
            '$lookup(S_entry.ENV, $ptascii("supplied")) = (n_exception_cell)',
            'S_entry.STORE[n_exception_cell] = DEFINED (POBJECT n_exception)',
            'n_exception =/= n_object',
            '$throwable_previous_id(S_entry, n_exception) = eps',
            '$throwable_field(S_entry, n_exception, "line") = PINT 20',
        ]
        seek(checks, 'S_unwind', 'S_enteredS', 7)
        checks += [
            'S_unwind.TODO = (THROW_SEARCH n_exception) :: (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask_tail*',
            '$output_string_release_valid(S_unwind, pobstringrelease)',
            '$heap_count(HOBJECT n_object, $tasks_nodes(S_unwind.TODO)) = 1',
            '$heap_owners($heap_prune($heap_graph(S_unwind)), HOBJECT n_object) = 1',
            'S_unwind.RESULT = KNOWN PNULL',
            'S_unwind.STORE[n_v] = DEFINED (PINT 100)',
            'S_unwind.STORE[n_casts] = DEFINED (PINT 1)',
            'S_unwind.STORE[n_drops] = DEFINED (PINT 0)',
            '$lookup(S_unwind.ENV, $ptascii("left")) = eps',
            '$integer_outputs(S_unwind.EVENTS) = ($ptascii("P;S;"))',
            '$call_descriptors_valid(S_unwind)', '$heap_valid($heap_graph(S_unwind))',
            # Drop only the held TMP; drive the original state through real D.
            'S_raw = S_unwind[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
            'PhpStep: S_unwind ~> S_raw',
            '$heap_owners($heap_prune($heap_graph(S_raw)), HOBJECT n_object) = 0',
            'S_raw.EVENTS = S_unwind.EVENTS',
        ]
        seek(checks, 'S_dtor', 'S_unwind', 8)
        destructor(checks, 'OUTPUT_STRING_RELEASE pobstringrelease', '(n_exception)', 'PNULL')
        checks += [
            '$output_string_certificate(S_dtor, pobstringrelease)',
            '$eager_operation_source_guard(S_dtor, pdestructionoperation)',
            '$throwable_live(S_dtor, n_exception)',
            '$throwable_previous_id(S_dtor, n_exception) = eps',
            '$throwable_field(S_dtor, n_exception, "line") = PINT 20',
            '$integer_outputs(S_dtor.EVENTS) = ($ptascii("P;S;"))',
        ]
        seek(checks, 'S_after', 'S_dtor', 9)
        checks += [
            'S_after.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
            'S_after.STORE[n_v] = DEFINED (PINT 100)',
            'S_after.STORE[n_casts] = DEFINED (PINT 1)',
            'S_after.STORE[n_drops] = DEFINED (PINT 1)',
            '~((HOBJECT n_object) <- S_after.ALLOCATIONS)',
            '$heap_owners($heap_prune($heap_graph(S_after)), HOBJECT n_object) = 0',
            '$heap_owners($heap_prune($heap_graph(S_after)), HOBJECT n_exception) = 2',
            '$throwable_previous_id(S_after, n_exception) = eps',
            '$throwable_field(S_after, n_exception, "line") = PINT 20',
            '$output_string_certificate(S_after, pobstringrelease)',
            '~$print_peer_markers(S_after.TODO)',
            '$integer_outputs(S_after.EVENTS) = ($ptascii("P;S;D:1:1;"))',
            '$call_descriptors_valid(S_after)', '$heap_valid($heap_graph(S_after))',
        ]
    value = '1' if borrowed else '100'
    checks += [
        'S_done = $drive_steps(S_after, 3000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        'S_done.DESTRUCTION.OPERATIONS = eps',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_left_end)',
        'S_done.STORE[n_left_end] = DEFINED (PINT 8)',
        f'S_done.STORE[n_v] = DEFINED (PINT {value})',
        'S_done.STORE[n_casts] = DEFINED (PINT 1)',
        'S_done.STORE[n_drops] = DEFINED (PINT 1)',
        '~((HOBJECT n_object) <- S_done.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HOBJECT n_object) = 0',
        '~$print_peer_markers(S_done.TODO)',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_entry, 0) = S_entry[.COMPLETION = BUDGET]',
        '$drive_steps(S_dtor, 0) = S_dtor[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
