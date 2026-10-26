#!/usr/bin/env python3
"""Real pending-Exception destruction of acquired CONCAT operands."""
import concat_returned_stringable_warning_review_cases as cases
import concat_returned_stringable_warning_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = r'''
dec $concat_returned_review_destructor(pstate, nat, nat) : bool
def $concat_returned_review_destructor(S, n_object, n_exception) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n_object
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.PENDING = (n_exception)
  -- if $destructor_call_live(S, pdestructorcall)
def $concat_returned_review_destructor(S, n_object, n_exception) = false -- otherwise
dec $concat_returned_review_seek_destructor(pstate, nat, nat, nat) : pstate
def $concat_returned_review_seek_destructor(S, n_object, n_exception, n) = S
  -- if $concat_returned_review_destructor(S, n_object, n_exception)
def $concat_returned_review_seek_destructor(S, n_object, n_exception, n) = S
  -- if ~$concat_returned_review_destructor(S, n_object, n_exception)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $concat_returned_review_seek_destructor(S, n_object, n_exception, n) = S
  -- if ~$concat_returned_review_destructor(S, n_object, n_exception)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $concat_returned_review_seek_destructor(S, n_object, n_exception, n) = $concat_returned_review_seek_destructor($drive_steps(S[.COMPLETION = NORMAL], 1), n_object, n_exception, $nabs($(n - 1)))
  -- if ~$concat_returned_review_destructor(S, n_object, n_exception)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
dec $concat_returned_review_task(ptask) : bool
def $concat_returned_review_task(CONCAT_RETURNED_WARNING pconcatreturned n) = true
def $concat_returned_review_task(CONCAT_RETURNED_LEFT pconcatreturned) = true
def $concat_returned_review_task(CONCAT_RETURNED_RIGHT pconcatreturned) = true
def $concat_returned_review_task(CONCAT_RETURNED_RELEASE pconcatreturned) = true
def $concat_returned_review_task(CONCAT_RETURNED_DONE pconcatreturned) = true
def $concat_returned_review_task(ptask) = false -- otherwise
dec $concat_returned_review_tasks(ptask*) : bool
def $concat_returned_review_tasks(eps) = false
def $concat_returned_review_tasks(ptask :: ptask_tail*) = ($concat_returned_review_task(ptask) \/ $concat_returned_review_tasks(ptask_tail*))
dec $concat_returned_review_throw(pstate, nat, nat) : bool
def $concat_returned_review_throw(S, n_object, n_exception) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n_exception) :: ptask_tail*
  -- if S.DESTRUCTION.OPERATIONS = eps
  -- if ~$concat_returned_review_tasks(S.TODO)
  -- if ~((HOBJECT n_object) <- S.ALLOCATIONS)
def $concat_returned_review_throw(S, n_object, n_exception) = false -- otherwise
dec $concat_returned_review_seek_throw(pstate, nat, nat, nat) : pstate
def $concat_returned_review_seek_throw(S, n_object, n_exception, n) = S
  -- if $concat_returned_review_throw(S, n_object, n_exception)
def $concat_returned_review_seek_throw(S, n_object, n_exception, n) = S
  -- if ~$concat_returned_review_throw(S, n_object, n_exception)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $concat_returned_review_seek_throw(S, n_object, n_exception, n) = S
  -- if ~$concat_returned_review_throw(S, n_object, n_exception)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $concat_returned_review_seek_throw(S, n_object, n_exception, n) = $concat_returned_review_seek_throw($drive_steps(S[.COMPLETION = NORMAL], 1), n_object, n_exception, $nabs($(n - 1)))
  -- if ~$concat_returned_review_throw(S, n_object, n_exception)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
dec $concat_returned_review_warning(pevent) : nat
def $concat_returned_review_warning(DIAGNOSTIC "Warning" n_message* z) = 1
def $concat_returned_review_warning(DIAGNOSTIC_SOURCE n_source "Warning" n_message* z) = 1
def $concat_returned_review_warning(DIAGNOSTIC_STACK "Warning" n_message* z n_trace*) = 1
def $concat_returned_review_warning(DIAGNOSTIC_STACK_SOURCE n_source "Warning" n_message* z n_trace*) = 1
def $concat_returned_review_warning(pevent) = 0 -- otherwise
dec $concat_returned_review_warnings(pevent*) : nat
def $concat_returned_review_warnings(eps) = 0
def $concat_returned_review_warnings(pevent :: pevent_tail*) = $($concat_returned_review_warning(pevent) + $concat_returned_review_warnings(pevent_tail*))
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    in_stringable = name == 'concat-array-left-returned-stringable-throw'
    casts = '1' if in_stringable else '0'
    warnings = '1' if in_stringable else '0'
    checks = shared.prefix(program, path)
    checks += [
        '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
        'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        'n_second =/= n_object',
        '$throwable_previous_id(S_entry, n_second) = eps',
        '$throwable_field(S_entry, n_second, "line") = PINT 20',
    ]
    if in_stringable:
        shared.returned_h(checks)
        checks += [
            '$concat_returned_review_warnings(S_return.EVENTS) = 1',
            '~$concat_returned_review_destructor(S_return, n_object, n_second)',
            '~$concat_returned_review_destructor(S_pending, n_object, n_second)',
            '~$stringify_consumer_receiver_valid(S_pending, n_second, CONCAT_RETURNED_RIGHT pconcatreturned)',
            '~$stringify_source(S_pending, porigin_left, 25, CONCAT_RETURNED_RIGHT pconcatreturned)',
        ]
        shared.seek(checks, 'S_enteredS', 'S_pending', 7)
        checks += [
            'S_enteredS.CURRENT = (pcallcontext_s)',
            'pcallcontext_s.TARGET = METHOD_TARGET n_object porigin_method',
            'pcallcontext_s.RECEIVER = (n_object)',
            'pcallcontext_s.CALLSITE = (porigin_right)',
            'S_enteredS.FRAMES = pframe_s :: pframe_s_tail*',
            'pframe_s.TODO = (STRINGIFY_RESULT n_object porigin_right 25) :: (CONCAT_RETURNED_RIGHT pconcatreturned) :: ptask_tail*',
            '$heap_count(HOBJECT n_object, $tasks_nodes(pframe_s.TODO)) = 2',
            '(HOBJECT n_object) <- S_enteredS.ALLOCATIONS',
            'S_enteredS.STORE[n_v] = DEFINED (PINT 100)',
            'S_enteredS.STORE[n_casts] = DEFINED (PINT 0)',
            'S_enteredS.STORE[n_drops] = DEFINED (PINT 0)',
            '$stringify_chain_valid(S_enteredS, S_enteredS.CURRENT, S_enteredS.FRAMES)',
            '$call_descriptors_valid(S_enteredS)', '$heap_valid($heap_graph(S_enteredS))',
        ]
        start = 'S_enteredS'
    else:
        start = 'S_enteredH'
    checks += [
        f'S_dtor_found = $concat_returned_review_seek_destructor({start}, n_object, n_second, 3000)',
        'S_dtor_found.COMPLETION = NORMAL \\/ S_dtor_found.COMPLETION = BUDGET',
        'S_dtor = S_dtor_found[.COMPLETION = NORMAL]',
        '$concat_returned_review_destructor(S_dtor, n_object, n_second)',
        '~$concat_returned_review_destructor(S_dtor, n_second, n_second)',
        '~$concat_returned_review_destructor(S_dtor, n_object, n_object)',
        'S_dtor.CURRENT = (pcallcontext_dtor)',
        '$destructor_context_call(pcallcontext_dtor, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object',
        'pdestructorcall.OPERATION = (pdestructionoperation)',
        'pdestructionoperation.PENDING = (n_second)',
        'pdestructionoperation.VALUE = KNOWN PNULL',
        'pdestructionoperation.CALLER = eps',
        'pcallcontext_dtor.TARGET = METHOD_TARGET n_object porigin_destructor',
        'pcallcontext_dtor.RECEIVER = (n_object)',
        '$destructor_call_live(S_dtor, pdestructorcall)',
        '$eager_operation_source_valid(S_dtor, pdestructionoperation)',
        '$lookup($global_table_view(S_dtor).ENV, $ptascii("left")) = eps',
        'S_dtor.STORE[n_seed] = DEFINED pvalue_seed_after_h',
        '$string_bytes(pvalue_seed_after_h) = ($ptascii("changed"))',
        'S_dtor.STORE[n_v] = DEFINED (PINT 100)',
        'S_dtor.STORE[n_calls] = DEFINED (PINT 1)',
        f'S_dtor.STORE[n_casts] = DEFINED (PINT {casts})',
        'S_dtor.STORE[n_drops] = DEFINED (PINT 0)',
        '(HOBJECT n_object) <- S_dtor.ALLOCATIONS',
        '$($heap_owners($heap_prune($heap_graph(S_dtor)), HOBJECT n_object) > 0)',
        '$heap_owners($heap_prune($heap_graph(S_dtor)), HARRAY n_array) = 0',
        '$throwable_live(S_dtor, n_second)',
        '$throwable_previous_id(S_dtor, n_second) = eps',
        '$throwable_field(S_dtor, n_second, "line") = PINT 20',
        f'$concat_returned_review_warnings(S_dtor.EVENTS) = {warnings}',
        '$call_descriptors_valid(S_dtor)', '$heap_valid($heap_graph(S_dtor))',
    ]
    before_d = b'P;H:2:1:25;' + (b'S:1;' if in_stringable else b'')
    checks += [
        '$integer_outputs(S_dtor.EVENTS) = ([' + ','.join(map(str, before_d)) + '])',
        'S_throw_found = $concat_returned_review_seek_throw(S_dtor, n_object, n_second, 3000)',
        'S_throw_found.COMPLETION = NORMAL \\/ S_throw_found.COMPLETION = BUDGET',
        'S_throw = S_throw_found[.COMPLETION = NORMAL]',
        '$concat_returned_review_throw(S_throw, n_object, n_second)',
        'S_throw.TODO = (THROW_SEARCH n_second) :: ptask_caller*',
        'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps',
        'S_throw.DESTRUCTION.OPERATIONS = eps',
        '~$concat_returned_review_tasks(S_throw.TODO)',
        '$lookup(S_throw.ENV, $ptascii("left")) = eps',
        '$lookup(S_throw.ENV, $ptascii("seed")) = (n_seed)',
        'S_throw.STORE[n_seed] = DEFINED pvalue_seed_after_h',
        'S_throw.STORE[n_v] = DEFINED (PINT 100)',
        'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
        f'S_throw.STORE[n_casts] = DEFINED (PINT {casts})',
        'S_throw.STORE[n_drops] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_object) = 0',
        '~((HOBJECT n_object) <- S_throw.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HARRAY n_array) = 0',
        '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
        '$throwable_live(S_throw, n_second)',
        '$throwable_previous_id(S_throw, n_second) = eps',
        '$throwable_field(S_throw, n_second, "line") = PINT 20',
        f'$concat_returned_review_warnings(S_throw.EVENTS) = {warnings}',
        '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
    ]
    through_d = before_d + b'D:1:' + casts.encode() + b';'
    checks += [
        '$integer_outputs(S_throw.EVENTS) = ([' + ','.join(map(str, through_d)) + '])',
        'S_done = $drive_steps(S_throw, 3000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        'S_done.DESTRUCTION.OPERATIONS = eps',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_left_end)',
        'S_done.STORE[n_left_end] = DEFINED (PINT 8)',
        '$lookup(S_done.ENV, $ptascii("seed")) = (n_seed)',
        'S_done.STORE[n_seed] = DEFINED pvalue_seed_end',
        '$string_bytes(pvalue_seed_end) = ($ptascii("end"))',
        'S_done.STORE[n_v] = DEFINED (PINT 100)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        f'S_done.STORE[n_casts] = DEFINED (PINT {casts})',
        'S_done.STORE[n_drops] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HOBJECT n_object) = 0',
        '~((HOBJECT n_object) <- S_done.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_array) = 0',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        f'$concat_returned_review_warnings(S_done.EVENTS) = {warnings}',
        '~$concat_returned_review_tasks(S_done.TODO)',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_capture, 0) = S_capture[.COMPLETION = BUDGET]',
        '$drive_steps(S_dtor, 0) = S_dtor[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
