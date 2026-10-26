#!/usr/bin/env python3
"""Independent pending-Exception cleanup after CONCAT's undefined RIGHT fetch."""
import concat_undefined_right_review_cases as cases
import concat_undefined_right_protocol as shared

CASES = tuple(cases.CASES)
REVIEW_HELPERS = r'''
dec $concat_missing_peer_task(ptask) : bool
def $concat_missing_peer_task(ERROR_READ_RESULT perrorread) = true
def $concat_missing_peer_task(ERROR_HANDLER_INVOKE perrorcall) = true
def $concat_missing_peer_task(ERROR_HANDLER_RESULT perrorcall) = true
def $concat_missing_peer_task(CONCAT_OWNED_LEFT pconcatleft) = true
def $concat_missing_peer_task(CONCAT_OWNED_RIGHT pconcatleft pvalue n?) = true
def $concat_missing_peer_task(CONCAT_OWNED_RELEASE pconcatleft) = true
def $concat_missing_peer_task(CONCAT_OWNED_RIGHT_RELEASE pconcatleft) = true
def $concat_missing_peer_task(CONCAT_OWNED_DONE pconcatleft) = true
def $concat_missing_peer_task(ptask) = false -- otherwise
dec $concat_missing_peer_tasks(ptask*) : bool
def $concat_missing_peer_tasks(eps) = false
def $concat_missing_peer_tasks(ptask :: ptask_tail*) = ($concat_missing_peer_task(ptask) \/ $concat_missing_peer_tasks(ptask_tail*))
dec $concat_missing_peer_frontier(pstate, nat, nat, nat) : bool
def $concat_missing_peer_frontier(S, n_object, n_exception, 0) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.ORIGINAL = CONCAT_PREP (KNOWN (POBJECT n_object)) (VARIABLE ptbytes z_input) false false z
def $concat_missing_peer_frontier(S, n_object, n_exception, 1) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n_exception) :: (CONCAT_OWNED_LEFT pconcatleft) :: ptask*
  -- if pconcatleft.OBJECT = n_object /\ pconcatleft.RIGHT = KNOWN PNULL
def $concat_missing_peer_frontier(S, n_object, n_exception, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n_object
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.PENDING = (n_exception)
  -- if $destructor_call_live(S, pdestructorcall)
def $concat_missing_peer_frontier(S, n_object, n_exception, 3) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n_exception) :: ptask*
  -- if S.DESTRUCTION.OPERATIONS = eps
  -- if ~$concat_missing_peer_tasks(S.TODO)
  -- if ~((HOBJECT n_object) <- S.ALLOCATIONS)
def $concat_missing_peer_frontier(S, n_object, n_exception, n) = false -- otherwise
dec $concat_missing_peer_seek(pstate, nat, nat, nat, nat) : pstate
def $concat_missing_peer_seek(S, n_object, n_exception, n_stage, n) = S
  -- if $concat_missing_peer_frontier(S, n_object, n_exception, n_stage)
def $concat_missing_peer_seek(S, n_object, n_exception, n_stage, n) = S
  -- if ~$concat_missing_peer_frontier(S, n_object, n_exception, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $concat_missing_peer_seek(S, n_object, n_exception, n_stage, n) = S
  -- if ~$concat_missing_peer_frontier(S, n_object, n_exception, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $concat_missing_peer_seek(S, n_object, n_exception, n_stage, n) = $concat_missing_peer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_object, n_exception, n_stage, $nabs($(n - 1)))
  -- if ~$concat_missing_peer_frontier(S, n_object, n_exception, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def seek(checks, label, start, stage):
    checks += [f'{label}_found = $concat_missing_peer_seek({start}, n_object, n_exception, {stage}, 3000)',
               f'{label}_found.COMPLETION = NORMAL \\/ {label}_found.COMPLETION = BUDGET',
               f'{label} = {label}_found[.COMPLETION = NORMAL]',
               f'$concat_missing_peer_frontier({label}, n_object, n_exception, {stage})']


def conditions(name, program, path, stdout):
    assert name in CASES
    stringable_throws = name == 'concat-undefined-right-stringable-throw'
    casts = '1' if stringable_throws else '0'
    value = 'method' if stringable_throws else 'handler'
    warnings = '1' if stringable_throws else '0'
    checks = shared.prefix(program, path)
    checks += [
        '$lookup(S_entry.ENV, $ptascii("supplied")) = (n_exception_cell)',
        'S_entry.STORE[n_exception_cell] = DEFINED (POBJECT n_exception)',
        'n_exception =/= n_object',
        '$throwable_previous_id(S_entry, n_exception) = eps',
        '$throwable_field(S_entry, n_exception, "line") = PINT 20',
        '~$concat_missing_peer_frontier(S_enteredH, n_object, n_exception, 2)',
    ]
    if stringable_throws:
        shared.returned_h(checks)
        checks += [
            # Same owning task root, but a live-CV restoration violates the shape.
            'perrorread_live = perrorread[.TASK = perrorread.ORIGINAL]',
            '$task_nodes(ERROR_READ_RESULT perrorread_live) = [HOBJECT n_object]',
            '~$error_read_valid(S_ready, perrorread_live)',
            '$integer_outputs(S_fixed.EVENTS) = ($ptascii("P;H:2:25:Undefined variable $right;"))',
        ]
        shared.seek(checks, 'S_pendingS', 'S_fixed', 6)
        checks += [
            'S_pendingS.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method) eps 0 eps (porigin_left) 25) :: (STRINGIFY_RESULT n_object porigin_left 25) :: (CONCAT_OWNED_LEFT pconcatleft_fixed) :: ptask_tail*',
            '$task_nodes(CONCAT_OWNED_LEFT pconcatleft_fixed) = [HOBJECT n_object]',
            '$task_nodes(STRINGIFY_RESULT n_object porigin_left 25) = [HOBJECT n_object]',
            '$heap_count(HOBJECT n_object, $tasks_nodes(S_pendingS.TODO)) = 3',
            '$stringify_consumer_receiver_valid(S_pendingS, n_object, CONCAT_OWNED_LEFT pconcatleft_fixed)',
            '$stringify_source(S_pendingS, porigin_left, 25, CONCAT_OWNED_LEFT pconcatleft_fixed)',
            '$concat_missing_warnings(S_pendingS.EVENTS) = 1',
            'S_pendingS.STORE[n_v] = DEFINED (PINT 100)',
            'S_pendingS.STORE[n_casts] = DEFINED (PINT 0)',
            'S_pendingS.STORE[n_drops] = DEFINED (PINT 0)',
            '$call_descriptors_valid(S_pendingS)', '$heap_valid($heap_graph(S_pendingS))',
        ]
        shared.seek(checks, 'S_enteredS', 'S_pendingS', 7)
        checks += [
            'S_enteredS.CURRENT = (pcallcontext_s)',
            'pcallcontext_s.TARGET = METHOD_TARGET n_object porigin_method',
            'pcallcontext_s.RECEIVER = (n_object)',
            'pcallcontext_s.CALLSITE = (porigin_left)',
            'S_enteredS.FRAMES = pframe_s :: pframe_s_tail*',
            'pframe_s.TODO = (STRINGIFY_RESULT n_object porigin_left 25) :: (CONCAT_OWNED_LEFT pconcatleft_fixed) :: ptask_tail*',
            '$heap_count(HOBJECT n_object, $tasks_nodes(pframe_s.TODO)) = 2',
            'S_enteredS.STORE[n_calls] = DEFINED (PINT 1)',
            'S_enteredS.STORE[n_casts] = DEFINED (PINT 0)',
            'S_enteredS.STORE[n_drops] = DEFINED (PINT 0)',
            'S_enteredS.STORE[n_v] = DEFINED (PINT 100)',
            'S_enteredS.STORE[n_right_cell] = DEFINED pvalue_handler',
            '$concat_missing_warnings(S_enteredS.EVENTS) = 1',
            '$stringify_chain_valid(S_enteredS, S_enteredS.CURRENT, S_enteredS.FRAMES)',
            '~$concat_missing_peer_frontier(S_enteredS, n_object, n_exception, 2)',
            '$call_descriptors_valid(S_enteredS)', '$heap_valid($heap_graph(S_enteredS))',
        ]
        start, stage, consumer = 'S_enteredS', 1, 'CONCAT_OWNED_LEFT pconcatleft_fixed'
    else:
        start, stage, consumer = 'S_enteredH', 0, 'ERROR_HANDLER_RESULT perrorcall'
    seek(checks, 'S_unwind', start, stage)
    checks += [
        'S_unwind.TODO = (THROW_SEARCH n_exception) :: (' + consumer + ') :: ptask_tail*',
        '$call_task_valid(S_unwind, ' + consumer + ')',
        '$heap_count(HOBJECT n_object, $tasks_nodes(S_unwind.TODO)) = 1',
        '$heap_owners($heap_prune($heap_graph(S_unwind)), HOBJECT n_object) = 1',
        'S_unwind.STORE[n_v] = DEFINED (PINT 100)',
        'S_unwind.STORE[n_calls] = DEFINED (PINT 1)',
        f'S_unwind.STORE[n_casts] = DEFINED (PINT {casts})',
        'S_unwind.STORE[n_drops] = DEFINED (PINT 0)',
        '$lookup(S_unwind.ENV, $ptascii("right")) = (n_right_cell)',
        'S_unwind.STORE[n_right_cell] = DEFINED pvalue_right',
        '$string_bytes(pvalue_right) = ($ptascii("' + value + '"))',
        f'$concat_missing_warnings(S_unwind.EVENTS) = {warnings}',
        '$throwable_live(S_unwind, n_exception)',
        '$call_descriptors_valid(S_unwind)', '$heap_valid($heap_graph(S_unwind))',
    ]
    if not stringable_throws:
        checks += [
            'S_unwind.ERRORHANDLER.CALLBACK = eps',
            '$task_nodes(ERROR_HANDLER_RESULT perrorcall) = [HOBJECT n_object]',
            '$identity_read_discard(S_unwind, perrorcall.RESUME) = S_unwind',
            '$error_read_discard(S_unwind, perrorcall.RESUME) = S_unwind',
        ]
    # Inspect the raw root loss; continue the genuine eager path below.
    raw = 'S_unwind[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]'
    if not stringable_throws:
        raw = '$error_handler_restore(' + raw + ', perrorcall.CALLBACK)'
    checks += [
        'S_raw = ' + raw,
        'PhpStep: S_unwind ~> S_raw',
        'S_raw.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)',
        '$heap_count(HOBJECT n_object, $tasks_nodes(S_raw.TODO)) = 0',
        '$heap_owners($heap_prune($heap_graph(S_raw)), HOBJECT n_object) = 0',
        'S_raw.EVENTS = S_unwind.EVENTS',
    ]
    seek(checks, 'S_dtor', 'S_unwind', 2)
    checks += [
        'S_dtor.CURRENT = (pcallcontext_dtor)',
        '$destructor_context_call(pcallcontext_dtor, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object',
        'pdestructorcall.OPERATION = (pdestructionoperation)',
        'pdestructionoperation.SOURCE = THROW_SEARCH n_exception',
        'pdestructionoperation.PENDING = (n_exception)',
        'pdestructionoperation.VALUE = KNOWN PNULL',
        'pdestructionoperation.CALLER = eps',
        'pcallcontext_dtor.TARGET = METHOD_TARGET n_object porigin_destructor',
        'pcallcontext_dtor.RECEIVER = (n_object)',
        '$eager_operation_source_valid(S_dtor, pdestructionoperation)',
        '$lookup($global_table_view(S_dtor).ENV, $ptascii("right")) = (n_right_cell)',
        'S_dtor.STORE[n_right_cell] = DEFINED pvalue_right',
        'S_dtor.STORE[n_v] = DEFINED (PINT 100)',
        'S_dtor.STORE[n_calls] = DEFINED (PINT 1)',
        f'S_dtor.STORE[n_casts] = DEFINED (PINT {casts})',
        'S_dtor.STORE[n_drops] = DEFINED (PINT 0)',
        '(HOBJECT n_object) <- S_dtor.ALLOCATIONS',
        '$($heap_owners($heap_prune($heap_graph(S_dtor)), HOBJECT n_object) > 0)',
        '$throwable_live(S_dtor, n_exception)',
        '$throwable_previous_id(S_dtor, n_exception) = eps',
        '$throwable_field(S_dtor, n_exception, "line") = PINT 20',
        f'$concat_missing_warnings(S_dtor.EVENTS) = {warnings}',
        '$call_descriptors_valid(S_dtor)', '$heap_valid($heap_graph(S_dtor))',
    ]
    before_d = b'P;H:2:25:Undefined variable $right;' + (b'S;' if stringable_throws else b'')
    checks += ['$integer_outputs(S_dtor.EVENTS) = ([' + ','.join(map(str, before_d)) + '])']
    seek(checks, 'S_throw', 'S_dtor', 3)
    checks += [
        'S_throw.TODO = (THROW_SEARCH n_exception) :: ptask_caller*',
        'S_throw.CURRENT = eps', 'S_throw.FRAMES = eps',
        'S_throw.DESTRUCTION.OPERATIONS = eps',
        '~$concat_missing_peer_tasks(S_throw.TODO)',
        'S_throw.STORE[n_right_cell] = DEFINED pvalue_right',
        'S_throw.STORE[n_v] = DEFINED (PINT 100)',
        'S_throw.STORE[n_calls] = DEFINED (PINT 1)',
        f'S_throw.STORE[n_casts] = DEFINED (PINT {casts})',
        'S_throw.STORE[n_drops] = DEFINED (PINT 1)',
        '~((HOBJECT n_object) <- S_throw.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_object) = 0',
        '$task_nodes(THROW_SEARCH n_exception) = [HOBJECT n_exception]',
        '$heap_owners($heap_prune($heap_graph(S_throw)), HOBJECT n_exception) = 2',
        '$throwable_live(S_throw, n_exception)',
        '$throwable_previous_id(S_throw, n_exception) = eps',
        '$throwable_field(S_throw, n_exception, "line") = PINT 20',
        f'$concat_missing_warnings(S_throw.EVENTS) = {warnings}',
        # The original source certificate remains valid after its A retires.
        '$error_read_valid(S_throw[.ORIGIN = (porigin_parent)], perrorread)',
        '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
        '$integer_outputs(S_throw.EVENTS) = ([' + ','.join(map(str, before_d + b'D:1:' + casts.encode() + b';')) + '])',
        'S_done = $drive_steps(S_throw, 3000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        'S_done.DESTRUCTION.OPERATIONS = eps',
        'S_done.STORE[n_right_cell] = DEFINED (PINT 8)',
        'S_done.STORE[n_v] = DEFINED (PINT 100)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        f'S_done.STORE[n_casts] = DEFINED (PINT {casts})',
        'S_done.STORE[n_drops] = DEFINED (PINT 1)',
        '~((HOBJECT n_object) <- S_done.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HOBJECT n_object) = 0',
        f'$concat_missing_warnings(S_done.EVENTS) = {warnings}',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '~$concat_missing_peer_tasks(S_done.TODO)',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_entry, 0) = S_entry[.COMPLETION = BUDGET]',
        '$drive_steps(S_unwind, 0) = S_unwind[.COMPLETION = BUDGET]',
        '$drive_steps(S_dtor, 0) = S_dtor[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
