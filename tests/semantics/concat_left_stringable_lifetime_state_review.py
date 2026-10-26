#!/usr/bin/env python3
"""Pending-Throwable retirement of CONCAT's acquired LEFT temporary."""
import concat_left_stringable_lifetime_review_cases as cases
import concat_left_stringable_lifetime_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = r'''
dec $concat_owned_review_destructor(pstate, nat, nat) : bool
def $concat_owned_review_destructor(S, n_object, n_exception) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n_object
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.PENDING = (n_exception)
  -- if $destructor_call_live(S, pdestructorcall)
def $concat_owned_review_destructor(S, n_object, n_exception) = false -- otherwise
dec $concat_owned_review_seek_destructor(pstate, nat, nat, nat) : pstate
def $concat_owned_review_seek_destructor(S, n_object, n_exception, n) = S
  -- if $concat_owned_review_destructor(S, n_object, n_exception)
def $concat_owned_review_seek_destructor(S, n_object, n_exception, n) = S
  -- if ~$concat_owned_review_destructor(S, n_object, n_exception)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $concat_owned_review_seek_destructor(S, n_object, n_exception, n) = S
  -- if ~$concat_owned_review_destructor(S, n_object, n_exception)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $concat_owned_review_seek_destructor(S, n_object, n_exception, n) = $concat_owned_review_seek_destructor($drive_steps(S[.COMPLETION = NORMAL], 1), n_object, n_exception, $nabs($(n - 1)))
  -- if ~$concat_owned_review_destructor(S, n_object, n_exception)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
dec $concat_owned_review_task(ptask) : bool
def $concat_owned_review_task(CONCAT_OWNED_LEFT pconcatleft) = true
def $concat_owned_review_task(CONCAT_OWNED_RIGHT pconcatleft pvalue n?) = true
def $concat_owned_review_task(CONCAT_OWNED_RELEASE pconcatleft) = true
def $concat_owned_review_task(CONCAT_OWNED_DONE pconcatleft) = true
def $concat_owned_review_task(ptask) = false -- otherwise
dec $concat_owned_review_tasks(ptask*) : bool
def $concat_owned_review_tasks(eps) = false
def $concat_owned_review_tasks(ptask :: ptask_tail*) = ($concat_owned_review_task(ptask) \/ $concat_owned_review_tasks(ptask_tail*))
dec $concat_owned_review_throw(pstate, nat, nat) : bool
def $concat_owned_review_throw(S, n_object, n_exception) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n_exception) :: ptask_tail*
  -- if S.DESTRUCTION.OPERATIONS = eps
  -- if ~$concat_owned_review_tasks(S.TODO)
  -- if ~((HOBJECT n_object) <- S.ALLOCATIONS)
def $concat_owned_review_throw(S, n_object, n_exception) = false -- otherwise
dec $concat_owned_review_seek_throw(pstate, nat, nat, nat) : pstate
def $concat_owned_review_seek_throw(S, n_object, n_exception, n) = S
  -- if $concat_owned_review_throw(S, n_object, n_exception)
def $concat_owned_review_seek_throw(S, n_object, n_exception, n) = S
  -- if ~$concat_owned_review_throw(S, n_object, n_exception)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $concat_owned_review_seek_throw(S, n_object, n_exception, n) = S
  -- if ~$concat_owned_review_throw(S, n_object, n_exception)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $concat_owned_review_seek_throw(S, n_object, n_exception, n) = $concat_owned_review_seek_throw($drive_steps(S[.COMPLETION = NORMAL], 1), n_object, n_exception, $nabs($(n - 1)))
  -- if ~$concat_owned_review_throw(S, n_object, n_exception)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    right_throws = name == 'concat-acquired-left-right-throw'
    rightcalls = '1' if right_throws else '0'
    checks = shared.prefix(program, path)
    checks += [
        '$lookup(S_entry.ENV, $ptascii("second")) = (n_second_cell)',
        'S_entry.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        'n_second =/= n_object',
        '$throwable_previous_id(S_entry, n_second) = eps',
        '$throwable_field(S_entry, n_second, "line") = PINT 20',
        '~$concat_owned_review_destructor(S_enteredS, n_object, n_second)',
        '$heap_count(HOBJECT n_object, $tasks_nodes(pframe_s.TODO)) = 2',
        '~$stringify_consumer_receiver_valid(S_pendingS, n_second, CONCAT_OWNED_LEFT pconcatleft)',
        '~$stringify_source(S_pendingS, porigin_right, 25, CONCAT_OWNED_LEFT pconcatleft)',
    ]
    if right_throws:
        shared.returned_left(checks)
        checks += [
            '$lookup(S_left.ENV, $ptascii("left")) = eps',
            'S_left.STORE[n_right_cell] = DEFINED (POBJECT n_right_object)',
            '$stringable_instance(S_left, n_right_object)',
            '$heap_owners($heap_prune($heap_graph(S_left)), HOBJECT n_right_object) = 1',
            '$concat_owned_live(S_left, pconcatleft)',
            '$concat_owned_ready(S_left, pconcatleft.RIGHT)',
            '$integer_outputs(S_left.EVENTS) = ($ptascii("P;S;"))',
        ]
        shared.seek(checks, 'S_pendingT', 'S_left', 8)
        checks += [
            'S_pendingT.TODO = (CALL_ARGS (METHOD_TARGET n_right_object porigin_method_right) eps 0 eps (porigin_right) 25) :: (STRINGIFY_RESULT n_right_object porigin_right 25) :: (CONCAT_OWNED_RIGHT pconcatleft pvalue_left (n_right_object)) :: ptask_tail*',
            'S_pendingT.ORIGIN = (porigin_right)',
            'S_pendingT.STORE[n_v] = DEFINED (PINT 100)',
            'S_pendingT.STORE[n_leftcalls] = DEFINED (PINT 1)',
            'S_pendingT.STORE[n_rightcalls] = DEFINED (PINT 0)',
            'S_pendingT.STORE[n_drops] = DEFINED (PINT 0)',
            '$task_nodes(STRINGIFY_RESULT n_right_object porigin_right 25) = [HOBJECT n_right_object]',
            '$task_nodes(CONCAT_OWNED_RIGHT pconcatleft pvalue_left (n_right_object)) = [HOBJECT n_object]',
            '$heap_count(HOBJECT n_object, $tasks_nodes(S_pendingT.TODO)) = 1',
            '$heap_count(HOBJECT n_right_object, $tasks_nodes(S_pendingT.TODO)) = 2',
            '$heap_owners($heap_prune($heap_graph(S_pendingT)), HOBJECT n_object) = 1',
            '~$stringify_consumer_receiver_valid(S_pendingT, n_object, CONCAT_OWNED_RIGHT pconcatleft pvalue_left (n_right_object))',
            '~$stringify_source(S_pendingT, porigin_left, 25, CONCAT_OWNED_RIGHT pconcatleft pvalue_left (n_right_object))',
            '$call_descriptors_valid(S_pendingT)', '$heap_valid($heap_graph(S_pendingT))',
        ]
        shared.seek(checks, 'S_enteredT', 'S_pendingT', 9)
        checks += [
            'S_enteredT.CURRENT = (pcallcontext_t)',
            'pcallcontext_t.TARGET = METHOD_TARGET n_right_object porigin_method_right',
            'pcallcontext_t.RECEIVER = (n_right_object)',
            'pcallcontext_t.CALLSITE = (porigin_right)',
            'S_enteredT.FRAMES = pframe_t :: pframe_t_tail*',
            'pframe_t.TODO = (STRINGIFY_RESULT n_right_object porigin_right 25) :: (CONCAT_OWNED_RIGHT pconcatleft pvalue_left (n_right_object)) :: ptask_tail*',
            'S_enteredT.STORE[n_v] = DEFINED (PINT 100)',
            'S_enteredT.STORE[n_leftcalls] = DEFINED (PINT 1)',
            'S_enteredT.STORE[n_rightcalls] = DEFINED (PINT 0)',
            'S_enteredT.STORE[n_drops] = DEFINED (PINT 0)',
            '$heap_count(HOBJECT n_object, $tasks_nodes(pframe_t.TODO)) = 1',
            '$heap_count(HOBJECT n_right_object, $tasks_nodes(pframe_t.TODO)) = 1',
            '$heap_owners($heap_prune($heap_graph(S_enteredT)), HOBJECT n_object) = 1',
            '~$concat_owned_review_destructor(S_enteredT, n_object, n_second)',
            '$stringify_chain_valid(S_enteredT, S_enteredT.CURRENT, S_enteredT.FRAMES)',
            '$call_descriptors_valid(S_enteredT)', '$heap_valid($heap_graph(S_enteredT))',
        ]
        start = 'S_enteredT'
    else:
        start = 'S_enteredS'
    checks += [
        f'S_dtor_found = $concat_owned_review_seek_destructor({start}, n_object, n_second, 3000)',
        'S_dtor_found.COMPLETION = NORMAL \\/ S_dtor_found.COMPLETION = BUDGET',
        'S_dtor = S_dtor_found[.COMPLETION = NORMAL]',
        '$concat_owned_review_destructor(S_dtor, n_object, n_second)',
        '~$concat_owned_review_destructor(S_dtor, n_second, n_second)',
        '~$concat_owned_review_destructor(S_dtor, n_object, n_object)',
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
        'S_dtor.STORE[n_right_cell] = DEFINED (POBJECT n_right_object)',
        'n_right_object =/= n_object', 'n_right_object =/= n_second',
        '$stringable_instance(S_dtor, n_right_object)',
        'S_dtor.STORE[n_v] = DEFINED (PINT 100)',
        'S_dtor.STORE[n_leftcalls] = DEFINED (PINT 1)',
        f'S_dtor.STORE[n_rightcalls] = DEFINED (PINT {rightcalls})',
        'S_dtor.STORE[n_drops] = DEFINED (PINT 0)',
        '(HOBJECT n_object) <- S_dtor.ALLOCATIONS',
        '$($heap_owners($heap_prune($heap_graph(S_dtor)), HOBJECT n_object) > 0)',
        '$throwable_live(S_dtor, n_second)',
        '$throwable_previous_id(S_dtor, n_second) = eps',
        '$throwable_field(S_dtor, n_second, "line") = PINT 20',
        '$call_descriptors_valid(S_dtor)', '$heap_valid($heap_graph(S_dtor))',
    ]
    before_d = b'P;S;' + (b'T;' if right_throws else b'')
    checks += [
        '$integer_outputs(S_dtor.EVENTS) = ([' + ','.join(map(str, before_d)) + '])',
        'S_throw_found = $concat_owned_review_seek_throw(S_dtor, n_object, n_second, 3000)',
        'S_throw_found.COMPLETION = NORMAL \\/ S_throw_found.COMPLETION = BUDGET',
        'S_throw = S_throw_found[.COMPLETION = NORMAL]',
        '$concat_owned_review_throw(S_throw, n_object, n_second)',
        'S_throw.TODO = (THROW_SEARCH n_second) :: ptask_caller*',
        'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps',
        'S_throw.DESTRUCTION.OPERATIONS = eps',
        '~$concat_owned_review_tasks(S_throw.TODO)',
        '$lookup(S_throw.ENV, $ptascii("left")) = eps',
        '$lookup(S_throw.ENV, $ptascii("right")) = (n_right_cell)',
        'S_throw.STORE[n_right_cell] = DEFINED pvalue_retired',
        '$string_bytes(pvalue_retired) = ($ptascii("retired"))',
        'S_throw.STORE[n_v] = DEFINED (PINT 100)',
        'S_throw.STORE[n_leftcalls] = DEFINED (PINT 1)',
        f'S_throw.STORE[n_rightcalls] = DEFINED (PINT {rightcalls})',
        'S_throw.STORE[n_drops] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_object) = 0',
        '~((HOBJECT n_object) <- S_throw.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_right_object) = 0',
        '~((HOBJECT n_right_object) <- S_throw.ALLOCATIONS)',
        '$task_nodes(THROW_SEARCH n_second) = [HOBJECT n_second]',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_second) = 2',
        '$throwable_live(S_throw, n_second)',
        '$throwable_previous_id(S_throw, n_second) = eps',
        '$throwable_field(S_throw, n_second, "line") = PINT 20',
        '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
    ]
    through_d = before_d + b'D:1:' + rightcalls.encode() + b';'
    checks += [
        '$integer_outputs(S_throw.EVENTS) = ([' + ','.join(map(str, through_d)) + '])',
        'S_done = $drive_steps(S_throw, 3000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        'S_done.DESTRUCTION.OPERATIONS = eps',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_left_end)',
        'S_done.STORE[n_left_end] = DEFINED (PINT 8)',
        '$lookup(S_done.ENV, $ptascii("right")) = (n_right_cell)',
        'S_done.STORE[n_right_cell] = DEFINED (PINT 9)',
        'S_done.STORE[n_v] = DEFINED (PINT 100)',
        'S_done.STORE[n_leftcalls] = DEFINED (PINT 1)',
        f'S_done.STORE[n_rightcalls] = DEFINED (PINT {rightcalls})',
        'S_done.STORE[n_drops] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HOBJECT n_object) = 0',
        '~((HOBJECT n_object) <- S_done.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HOBJECT n_right_object) = 0',
        '~((HOBJECT n_right_object) <- S_done.ALLOCATIONS)',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '~$concat_owned_review_tasks(S_done.TODO)',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_entry, 0) = S_entry[.COMPLETION = BUDGET]',
        '$drive_steps(S_dtor, 0) = S_dtor[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
