#!/usr/bin/env python3
"""Pending-Exception A/B retirement with the older allocation on the RIGHT."""
import concat_dual_stringable_lifetime_review_cases as cases
import concat_dual_stringable_lifetime_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = r'''
dec $concat_dual_review_destructor(pstate, nat, nat) : bool
def $concat_dual_review_destructor(S, n_object, n_exception) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n_object
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.PENDING = (n_exception)
  -- if $destructor_call_live(S, pdestructorcall)
def $concat_dual_review_destructor(S, n_object, n_exception) = false -- otherwise
dec $concat_dual_review_task(ptask) : bool
def $concat_dual_review_task(CONCAT_OWNED_LEFT pconcatleft) = true
def $concat_dual_review_task(CONCAT_OWNED_RIGHT pconcatleft pvalue n?) = true
def $concat_dual_review_task(CONCAT_OWNED_RELEASE pconcatleft) = true
def $concat_dual_review_task(CONCAT_OWNED_RIGHT_RELEASE pconcatleft) = true
def $concat_dual_review_task(CONCAT_OWNED_DONE pconcatleft) = true
def $concat_dual_review_task(ptask) = false -- otherwise
dec $concat_dual_review_tasks(ptask*) : bool
def $concat_dual_review_tasks(eps) = false
def $concat_dual_review_tasks(ptask :: ptask_tail*) = ($concat_dual_review_task(ptask) \/ $concat_dual_review_tasks(ptask_tail*))
dec $concat_dual_review_frontier(pstate, nat, nat, nat, nat) : bool
def $concat_dual_review_frontier(S, 0, n_left, n_right, n_exception) = $concat_dual_review_destructor(S, n_left, n_exception)
def $concat_dual_review_frontier(S, 1, n_left, n_right, n_exception) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n_exception) :: (CONCAT_OWNED_RIGHT_RELEASE pconcatleft) :: ptask_tail*
  -- if pconcatleft.OBJECT = n_left /\ pconcatleft.RIGHT = KNOWN (POBJECT n_right)
  -- if S.DESTRUCTION.OPERATIONS = eps
  -- if ~((HOBJECT n_left) <- S.ALLOCATIONS) /\ (HOBJECT n_right) <- S.ALLOCATIONS
def $concat_dual_review_frontier(S, 2, n_left, n_right, n_exception) = $concat_dual_review_destructor(S, n_right, n_exception)
def $concat_dual_review_frontier(S, 3, n_left, n_right, n_exception) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n_exception) :: ptask_tail*
  -- if S.DESTRUCTION.OPERATIONS = eps
  -- if ~$concat_dual_review_tasks(S.TODO)
  -- if ~((HOBJECT n_left) <- S.ALLOCATIONS) /\ ~((HOBJECT n_right) <- S.ALLOCATIONS)
def $concat_dual_review_frontier(S, 4, n_left, n_right, n_exception) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n_exception) :: (CONCAT_OWNED_LEFT pconcatleft) :: ptask_tail*
  -- if pconcatleft.OBJECT = n_left /\ pconcatleft.RIGHT = KNOWN (POBJECT n_right)
def $concat_dual_review_frontier(S, 5, n_left, n_right, n_exception) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n_exception) :: (CONCAT_OWNED_RIGHT pconcatleft pvalue (n_right)) :: ptask_tail*
  -- if pconcatleft.OBJECT = n_left /\ pconcatleft.RIGHT = KNOWN (POBJECT n_right)
def $concat_dual_review_frontier(S, n_stage, n_left, n_right, n_exception) = false -- otherwise
dec $concat_dual_review_seek(pstate, nat, nat, nat, nat, nat) : pstate
def $concat_dual_review_seek(S, n_stage, n_left, n_right, n_exception, n) = S
  -- if $concat_dual_review_frontier(S, n_stage, n_left, n_right, n_exception)
def $concat_dual_review_seek(S, n_stage, n_left, n_right, n_exception, n) = S
  -- if ~$concat_dual_review_frontier(S, n_stage, n_left, n_right, n_exception)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $concat_dual_review_seek(S, n_stage, n_left, n_right, n_exception, n) = S
  -- if ~$concat_dual_review_frontier(S, n_stage, n_left, n_right, n_exception)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $concat_dual_review_seek(S, n_stage, n_left, n_right, n_exception, n) = $concat_dual_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, n_left, n_right, n_exception, $nabs($(n - 1)))
  -- if ~$concat_dual_review_frontier(S, n_stage, n_left, n_right, n_exception)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def seek(checks, label, start, stage):
    checks += [
        f'{label}_found = $concat_dual_review_seek({start}, {stage}, n_object, n_right_object, n_exception, 3000)',
        f'{label}_found.COMPLETION = NORMAL \\/ {label}_found.COMPLETION = BUDGET',
        f'{label} = {label}_found[.COMPLETION = NORMAL]',
        f'$concat_dual_review_frontier({label}, {stage}, n_object, n_right_object, n_exception)',
    ]


def destructor(checks, label, object_id, adrops, bdrops, rightcalls):
    checks += [
        f'{label}.CURRENT = (pcallcontext_{label})',
        f'$destructor_context_call(pcallcontext_{label}, {label}.CURRENT, {label}.FRAMES) = (pdestructorcall_{label})',
        f'pdestructorcall_{label}.OBJECT = {object_id}',
        f'pdestructorcall_{label}.OPERATION = (pdestructionoperation_{label})',
        f'pdestructionoperation_{label}.PENDING = (n_exception)',
        f'pdestructionoperation_{label}.SOURCE = THROW_SEARCH n_exception',
        f'pdestructionoperation_{label}.VALUE = KNOWN PNULL',
        f'pdestructionoperation_{label}.CALLER = eps',
        f'pcallcontext_{label}.TARGET = METHOD_TARGET {object_id} porigin_method_{label}',
        f'pcallcontext_{label}.RECEIVER = ({object_id})',
        f'$destructor_call_live({label}, pdestructorcall_{label})',
        f'$eager_operation_source_valid({label}, pdestructionoperation_{label})',
        f'$lookup($global_table_view({label}).ENV, $ptascii("seed")) = eps',
        f'{label}.STORE[n_v] = DEFINED (PINT 100)',
        f'{label}.STORE[n_leftcalls] = DEFINED (PINT 1)',
        f'{label}.STORE[n_rightcalls] = DEFINED (PINT {rightcalls})',
        f'{label}.STORE[n_adrops] = DEFINED (PINT {adrops})',
        f'{label}.STORE[n_bdrops] = DEFINED (PINT {bdrops})',
        f'(HOBJECT {object_id}) <- {label}.ALLOCATIONS',
        f'$($heap_owners($heap_prune($heap_graph({label})), HOBJECT {object_id}) > 0)',
        f'$throwable_live({label}, n_exception)',
        f'$throwable_previous_id({label}, n_exception) = eps',
        f'$throwable_field({label}, n_exception, "line") = PINT 20',
        f'$call_descriptors_valid({label})', f'$heap_valid($heap_graph({label}))',
    ]


def conditions(name, program, path, stdout):
    assert name in CASES
    right_throws = name == 'concat-two-acquired-right-throw'
    count = '1' if right_throws else '0'
    checks = shared.prefix(program, path)
    checks += [
        '$(n_right_object < n_object)',
        'S_g_globals = $global_table_view(S_factory_g)',
        '$lookup(S_g_globals.ENV, $ptascii("seed")) = (n_seed_cell)',
        'S_factory_g.STORE[n_seed_cell] = DEFINED (POBJECT n_right_object)',
        '$lookup(S_factory_g_return.ENV, $ptascii("seed")) = eps',
        '$lookup(S_entry.ENV, $ptascii("supplied")) = (n_exception_cell)',
        'S_entry.STORE[n_exception_cell] = DEFINED (POBJECT n_exception)',
        'n_exception =/= n_object', 'n_exception =/= n_right_object',
        '$throwable_previous_id(S_entry, n_exception) = eps',
        '$throwable_field(S_entry, n_exception, "line") = PINT 20',
    ]
    if right_throws:
        shared.returned_left(checks)
        shared.seek(checks, 'S_pendingT', 'S_left', 5)
        checks += [
            'S_pendingT.TODO = (CALL_ARGS (METHOD_TARGET n_right_object porigin_method_right) eps 0 eps (porigin_right) 25) :: (STRINGIFY_RESULT n_right_object porigin_right 25) :: (CONCAT_OWNED_RIGHT pconcatleft pvalue_left (n_right_object)) :: ptask_tail*',
            '$task_nodes(CONCAT_OWNED_RIGHT pconcatleft pvalue_left (n_right_object)) = [HOBJECT n_object, HOBJECT n_right_object]',
            '$heap_count(HOBJECT n_object, $tasks_nodes(S_pendingT.TODO)) = 1',
            '$heap_count(HOBJECT n_right_object, $tasks_nodes(S_pendingT.TODO)) = 3',
            '~$stringify_consumer_receiver_valid(S_pendingT, n_object, CONCAT_OWNED_RIGHT pconcatleft pvalue_left (n_right_object))',
            '$call_descriptors_valid(S_pendingT)', '$heap_valid($heap_graph(S_pendingT))',
        ]
        shared.seek(checks, 'S_enteredT', 'S_pendingT', 6)
        checks += [
            'S_enteredT.CURRENT = (pcallcontext_t)',
            'pcallcontext_t.TARGET = METHOD_TARGET n_right_object porigin_method_right',
            'pcallcontext_t.RECEIVER = (n_right_object)',
            'pcallcontext_t.CALLSITE = (porigin_right)',
            'S_enteredT.FRAMES = pframe_t :: pframe_t_tail*',
            'pframe_t.TODO = (STRINGIFY_RESULT n_right_object porigin_right 25) :: (CONCAT_OWNED_RIGHT pconcatleft pvalue_left (n_right_object)) :: ptask_tail*',
            '$heap_count(HOBJECT n_object, $tasks_nodes(pframe_t.TODO)) = 1',
            '$heap_count(HOBJECT n_right_object, $tasks_nodes(pframe_t.TODO)) = 2',
            '$heap_owners($heap_prune($heap_graph(S_enteredT)), HOBJECT n_object) = 1',
            'S_enteredT.STORE[n_v] = DEFINED (PINT 100)',
            'S_enteredT.STORE[n_adrops] = DEFINED (PINT 0)',
            'S_enteredT.STORE[n_bdrops] = DEFINED (PINT 0)',
            '$stringify_chain_valid(S_enteredT, S_enteredT.CURRENT, S_enteredT.FRAMES)',
            '$call_descriptors_valid(S_enteredT)', '$heap_valid($heap_graph(S_enteredT))',
        ]
        start, stage = 'S_enteredT', 5
        consumer = 'CONCAT_OWNED_RIGHT pconcatleft pvalue_left (n_right_object)'
    else:
        start, stage = 'S_enteredS', 4
        consumer = 'CONCAT_OWNED_LEFT pconcatleft'
    seek(checks, 'S_unwind', start, stage)
    checks += [
        'S_unwind.TODO = (THROW_SEARCH n_exception) :: (' + consumer + ') :: ptask_tail*',
        '$call_task_valid(S_unwind, ' + consumer + ')',
        '$heap_owners($heap_prune($heap_graph(S_unwind)), HOBJECT n_object) = 1',
        '$heap_owners($heap_prune($heap_graph(S_unwind)), HOBJECT n_right_object) = 1',
        'S_unwind.STORE[n_adrops] = DEFINED (PINT 0)',
        'S_unwind.STORE[n_bdrops] = DEFINED (PINT 0)',
        '$call_descriptors_valid(S_unwind)', '$heap_valid($heap_graph(S_unwind))',
        'S_raw_hold = S_unwind[.TODO = (THROW_SEARCH n_exception) :: (CONCAT_OWNED_RIGHT_RELEASE pconcatleft) :: ptask_tail*]',
        'PhpStep: S_unwind ~> S_raw_hold',
        '$task_nodes(CONCAT_OWNED_RIGHT_RELEASE pconcatleft) = [HOBJECT n_right_object]',
        '$heap_owners($heap_prune($heap_graph(S_raw_hold)), HOBJECT n_object) = 0',
        '$heap_owners($heap_prune($heap_graph(S_raw_hold)), HOBJECT n_right_object) = 1',
        'S_raw_hold.EVENTS = S_unwind.EVENTS',
    ]
    seek(checks, 'S_da', 'S_unwind', 0)
    destructor(checks, 'S_da', 'n_object', 0, 0, count)
    checks += [
        '(HOBJECT n_right_object) <- S_da.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_da)), HOBJECT n_right_object) = 1',
    ]
    before_d = b'P;Q;S;' + (b'T;' if right_throws else b'')
    checks += ['$integer_outputs(S_da.EVENTS) = ([' + ','.join(map(str, before_d)) + '])']
    seek(checks, 'S_between', 'S_da', 1)
    checks += [
        'S_between.TODO = (THROW_SEARCH n_exception) :: (CONCAT_OWNED_RIGHT_RELEASE pconcatleft) :: ptask_tail*',
        'S_between.STORE[n_v] = DEFINED (PINT 100)',
        'S_between.STORE[n_adrops] = DEFINED (PINT 1)',
        'S_between.STORE[n_bdrops] = DEFINED (PINT 0)',
        '$heap_count(HOBJECT n_right_object, $tasks_nodes(S_between.TODO)) = 1',
        '$heap_owners($heap_prune($heap_graph(S_between)), HOBJECT n_right_object) = 1',
        '$heap_owners($heap_prune($heap_graph(S_between)), HOBJECT n_object) = 0',
        '$concat_owned_right_release_valid(S_between, pconcatleft)',
        '~$concat_owned_live(S_between, pconcatleft)',
        '$throwable_live(S_between, n_exception)',
        '$call_descriptors_valid(S_between)', '$heap_valid($heap_graph(S_between))',
        'pconcatleft_same = pconcatleft[.OBJECT = n_right_object]',
        'S_same_hold = S_between[.TODO = (THROW_SEARCH n_exception) :: (CONCAT_OWNED_RIGHT_RELEASE pconcatleft_same) :: ptask_tail*]',
        '$heap_valid($heap_graph(S_same_hold))',
        '$heap_owners($heap_prune($heap_graph(S_same_hold)), HOBJECT n_right_object) = 1',
        '~$concat_owned_right_release_valid(S_same_hold, pconcatleft_same)',
        '~$call_descriptors_valid(S_same_hold)',
    ]
    after_a = before_d + b'A:1:1:1:' + count.encode() + b';'
    checks += ['$integer_outputs(S_between.EVENTS) = ([' + ','.join(map(str, after_a)) + '])']
    seek(checks, 'S_db', 'S_between', 2)
    destructor(checks, 'S_db', 'n_right_object', 1, 0, count)
    checks += [
        '~((HOBJECT n_object) <- S_db.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_db)), HOBJECT n_object) = 0',
        '$integer_outputs(S_db.EVENTS) = ([' + ','.join(map(str, after_a)) + '])',
    ]
    seek(checks, 'S_throw', 'S_db', 3)
    checks += [
        'S_throw.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        'S_throw.STORE[n_v] = DEFINED (PINT 100)',
        'S_throw.STORE[n_leftcalls] = DEFINED (PINT 1)',
        f'S_throw.STORE[n_rightcalls] = DEFINED (PINT {count})',
        'S_throw.STORE[n_adrops] = DEFINED (PINT 1)',
        'S_throw.STORE[n_bdrops] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_object) = 0',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_right_object) = 0',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_exception) = 2',
        '$throwable_previous_id(S_throw, n_exception) = eps',
        '$throwable_field(S_throw, n_exception, "line") = PINT 20',
        '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
    ]
    after_b = after_a + b'B:1:1:1:' + count.encode() + b';'
    checks += [
        '$integer_outputs(S_throw.EVENTS) = ([' + ','.join(map(str, after_b)) + '])',
        'S_done = $drive_steps(S_throw, 3000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        'S_done.DESTRUCTION.OPERATIONS = eps',
        'S_done.STORE[n_v] = DEFINED (PINT 100)',
        'S_done.STORE[n_leftcalls] = DEFINED (PINT 8)',
        'S_done.STORE[n_rightcalls] = DEFINED (PINT 9)',
        'S_done.STORE[n_adrops] = DEFINED (PINT 1)',
        'S_done.STORE[n_bdrops] = DEFINED (PINT 1)',
        '$lookup(S_done.ENV, $ptascii("seed")) = (n_seed_end)',
        'S_done.STORE[n_seed_end] = DEFINED (PINT 10)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HOBJECT n_object) = 0',
        '$heap_owners($heap_prune($heap_graph(S_done)), HOBJECT n_right_object) = 0',
        '~((HOBJECT n_object) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_right_object) <- S_done.ALLOCATIONS)',
        '~$concat_dual_review_tasks(S_done.TODO)',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_unwind, 0) = S_unwind[.COMPLETION = BUDGET]',
        '$drive_steps(S_da, 0) = S_da[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
