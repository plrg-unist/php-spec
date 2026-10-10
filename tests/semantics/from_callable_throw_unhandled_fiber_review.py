"""Reached unhandled bound injection, ordinary finally, callback and capture retirement."""
from from_callable_throw_fiber_review import EXTRA, guards, lines, render as handled_render
from error_handler_protocol import PREFIX


UNHANDLED = r'''
dec $unhandled_throw_stage(pstate, nat) : bool
def $unhandled_throw_stage(S, 0) = true
  -- if S.TODO = (FINALLY_RESUME porigin (n)) :: (FINALLY_PHASE porigin 1) :: ptask*
  -- if S.ACTIVEFIBER =/= eps
def $unhandled_throw_stage(S, 1) = true
  -- if S.TODO = (THROW_SEARCH n) :: (FIBER_FINISH n_fiber) :: eps
  -- if S.ACTIVEFIBER = (n_fiber)
def $unhandled_throw_stage(S, 2) = true
  -- if S.TODO = (FIBER_THROW_FINISH pfiberfinish) :: eps
def $unhandled_throw_stage(S, 3) = true
  -- if S.TODO = (THROW_SEARCH n) :: (FIBER_CAPTURE_RESULT n_capture pconfigcall false) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_FIBER_THROW
  -- if S.ACTIVEFIBER = eps
def $unhandled_throw_stage(S, 4) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
  -- if pdestructionoperation.SOURCE = THROW_SEARCH n
  -- if pdestructionoperation.PENDING = (n)
  -- if S.ACTIVEFIBER = eps
def $unhandled_throw_stage(S, 5) = true
  -- if S.TODO = (CATCH_BIND porigin n_catch n) :: ptask*
  -- if S.ACTIVEFIBER = eps
def $unhandled_throw_stage(S, n) = false -- otherwise
dec $unhandled_throw_seek(pstate, nat, nat) : pstate
def $unhandled_throw_seek(S, n_phase, n) = S
  -- if $unhandled_throw_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $unhandled_throw_seek(S, n_phase, n) = $unhandled_throw_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if ~$unhandled_throw_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $unhandled_throw_seek(S, n_phase, 0) = S
  -- if ~$unhandled_throw_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $unhandled_throw_seek(S, n_phase, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''


def seek(state, previous, phase):
    return [f'{state}_reached = $unhandled_throw_seek({previous}, {phase}, 1000)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$unhandled_throw_stage({state}, {phase})']


def render(program, filename, expected):
    _, prior, genuine_count, _ = handled_render(program, filename, expected)
    cut = next(i for i, check in enumerate(prior) if check.startswith('S_before_catch_reached ='))
    # These factory/invocation checks execute the new original, through injection.
    genuine = prior[:cut]
    prefix = 'Q;A;M:isTerminated;F;B;P:pause;H:held;V;F:C:held;X:held;H:held;'
    genuine += seek('S_finally', 'S_switched', 0) + lines(r'''
S_finally.TODO = (FINALLY_RESUME porigin_finally (n_exception)) :: (FINALLY_PHASE porigin_finally 1) :: ptask_after_finally*
S_finally.ACTIVEFIBER = (n_receiver)
S_finally.FIBERCALLERS = [pfibercaller]
S_finally.CURRENT = S_switched.CURRENT
$finally_resume_valid(S_finally, porigin_finally, (n_exception))
$call_task_valid(S_finally, FINALLY_RESUME porigin_finally (n_exception))
$task_nodes(FINALLY_RESUME porigin_finally (n_exception)) = [HOBJECT n_exception]
$heap_owners($heap_graph(S_finally), HOBJECT n_exception) = 2
$heap_owners($heap_graph(S_finally), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_finally), HOBJECT n_receiver) = 1
$weakref_get(S_finally, n_weak_exception) = POBJECT n_exception
$weakref_get(S_finally, n_weak_capture) = POBJECT n_capture
$weakref_get(S_finally, n_weak_receiver) = POBJECT n_receiver
S_after_finally_step = $drive_steps(S_finally, 1)
S_after_finally_step.COMPLETION = BUDGET
S_after_finally = S_after_finally_step[.COMPLETION = NORMAL]
S_after_finally.TODO = (THROW_SEARCH n_exception) :: ptask_unwind*
''') + [f'$outputs(S_finally.EVENTS) = $ptascii("{prefix}")',
        '$outputs(S_after_finally.EVENTS) = $outputs(S_finally.EVENTS)'] + guards('S_finally') + guards('S_after_finally')
    genuine += seek('S_uncaught', 'S_after_finally', 1) + lines(r'''
S_uncaught.TODO = [THROW_SEARCH n_exception, FIBER_FINISH n_receiver]
S_uncaught.ACTIVEFIBER = (n_receiver)
S_uncaught.CURRENT = eps
S_uncaught.FRAMES = eps
S_uncaught.FIBERCALLERS = [pfibercaller]
$fiber_throw_ready(S_uncaught)
$fiber_ordinary_cleanup(S_uncaught, n_receiver)
~$fiber_close_boundary(S_uncaught)
$heap_owners($heap_graph(S_uncaught), HOBJECT n_exception) = 2
$heap_owners($heap_graph(S_uncaught), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_uncaught), HOBJECT n_receiver) = 1
$outputs(S_uncaught.EVENTS) = $outputs(S_finally.EVENTS)
''') + guards('S_uncaught')
    genuine += seek('S_finish', 'S_uncaught', 2) + lines(r'''
S_finish.TODO = [FIBER_THROW_FINISH pfiberfinish]
pfiberfinish = {OBJECT n_receiver, PENDING (n_exception), SEQUENCE pfiber_running.SEQUENCE, PROTECTED eps}
S_finish.ACTIVEFIBER = (n_receiver)
S_finish.FIBERCALLERS = [pfibercaller]
S_finish.CURRENT = eps
S_finish.FRAMES = eps
$fiber_at(S_finish, n_receiver) = (pfiber_retired)
pfiber_retired.STATUS = FIBER_RUNNING
pfiber_retired.RAW = PNULL
pfiber_retired.CALL = eps
pfiber_retired.TARGET = eps
pfiber_retired.FINISH = (pfiberfinish)
pfiber_retired.VALUE = PNULL
~pfiber_retired.RETURNED
~pfiber_retired.FAILED
~pfiber_retired.GRACEFUL
~$fiber_close_boundary(S_finish)
$fiber_ordinary_finish_live(S_finish, pfiberfinish)
$call_task_valid(S_finish, FIBER_THROW_FINISH pfiberfinish)
$task_nodes(FIBER_THROW_FINISH pfiberfinish) = [HOBJECT n_exception]
~((HOBJECT n_body) <- S_finish.ALLOCATIONS)
$heap_owners($heap_graph(S_finish), HOBJECT n_body) = 0
$heap_owners($heap_graph(S_finish), HOBJECT n_exception) = 2
$heap_owners($heap_graph(S_finish), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_finish), HOBJECT n_receiver) = 1
$outputs(S_finish.EVENTS) = $outputs(S_finally.EVENTS)
''') + guards('S_finish')
    genuine += seek('S_result', 'S_finish', 3) + lines(r'''
S_result.TODO = (THROW_SEARCH n_exception) :: (FIBER_CAPTURE_RESULT n_capture pconfigcall_throw false) :: ptask_after_call*
S_result.RESULT = KNOWN PNULL
S_result.ACTIVEFIBER = eps
S_result.FIBERCALLERS = eps
S_result.CURRENT = S_invoke.CURRENT
S_result.FRAMES = S_invoke.FRAMES
$fiber_at(S_result, n_receiver) = (pfiber_terminated)
pfiber_terminated.STATUS = FIBER_TERMINATED
pfiber_terminated.RAW = PNULL
pfiber_terminated.TARGET = eps
pfiber_terminated.VALUE = PNULL
~pfiber_terminated.RETURNED
pfiber_terminated.FAILED
~pfiber_terminated.GRACEFUL
$fiber_capture_result_valid(S_result, n_capture, pconfigcall_throw, false)
$task_nodes(THROW_SEARCH n_exception) = [HOBJECT n_exception]
$task_nodes(FIBER_CAPTURE_RESULT n_capture pconfigcall_throw false) = [HOBJECT n_capture]
$heap_owners($heap_graph(S_result), HOBJECT n_exception) = 1
$heap_owners($heap_graph(S_result), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_result), HOBJECT n_receiver) = 1
$config_slots_valid(S_result, pconfigcall_throw.SENT)
$throwable_field(S_result, n_exception, "trace") = PARRAY n_exception_trace
S_result.ARRAYS[n_exception_trace].ITEMS = eps
$outputs(S_result.EVENTS) = $outputs(S_finally.EVENTS)
S_release_begin_step = $drive_steps(S_result, 1)
S_release_begin_step.COMPLETION = BUDGET
S_release_begin = S_release_begin_step[.COMPLETION = NORMAL]
S_release_begin.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
pdestructionoperation.SOURCE = THROW_SEARCH n_exception
pdestructionoperation.VALUE = KNOWN PNULL
pdestructionoperation.PENDING = (n_exception)
S_release_begin.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_after_call*
$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_exception]
$destructor_release_valid(S_release_begin, pdestructionrelease)
$destructor_operation_valid(S_release_begin, pdestructionoperation)
$heap_owners($heap_graph(S_release_begin), HOBJECT n_exception) = 1
$heap_owners($heap_graph(S_release_begin), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_release_begin), HOBJECT n_receiver) = 1
$outputs(S_release_begin.EVENTS) = $outputs(S_finally.EVENTS)
''') + guards('S_result') + guards('S_release_begin')
    genuine += seek('S_release_exit', 'S_release_begin', 4) + lines(r'''
S_release_exit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_after_call*
$destructor_operation_valid(S_release_exit, pdestructionoperation)
~((HOBJECT n_capture) <- S_release_exit.ALLOCATIONS)
~((HOBJECT n_receiver) <- S_release_exit.ALLOCATIONS)
$heap_owners($heap_graph(S_release_exit), HOBJECT n_capture) = 0
$heap_owners($heap_graph(S_release_exit), HOBJECT n_receiver) = 0
$heap_owners($heap_graph(S_release_exit), HOBJECT n_exception) = 1
$weakref_get(S_release_exit, n_weak_capture) = PNULL
$weakref_get(S_release_exit, n_weak_receiver) = PNULL
$weakref_get(S_release_exit, n_weak_exception) = POBJECT n_exception
~$fiber_capture_source_valid(S_release_exit, pfibercapture)
S_pending_step = $drive_steps(S_release_exit, 1)
S_pending_step.COMPLETION = BUDGET
S_pending = S_pending_step[.COMPLETION = NORMAL]
S_pending.TODO = (THROW_SEARCH n_exception) :: ptask_after_call*
S_pending.DESTRUCTION.OPERATIONS = pdestructionoperation_tail*
$heap_owners($heap_graph(S_pending), HOBJECT n_exception) = 1
$outputs(S_pending.EVENTS) = $outputs(S_finally.EVENTS)
''') + guards('S_release_exit') + guards('S_pending')
    genuine += seek('S_before_catch', 'S_pending', 5) + lines(r'''
S_before_catch.TODO = (CATCH_BIND porigin_outer_try n_catch n_exception) :: ptask_after_catch*
S_before_catch.ACTIVEFIBER = eps
S_before_catch.FIBERCALLERS = eps
$throwable_binding_valid(S_before_catch, porigin_outer_try, n_catch, n_exception)
$task_nodes(CATCH_BIND porigin_outer_try n_catch n_exception) = [HOBJECT n_exception]
$heap_owners($heap_graph(S_before_catch), HOBJECT n_exception) = 1
$heap_owners($heap_graph(S_before_catch), HOBJECT n_capture) = 0
$heap_owners($heap_graph(S_before_catch), HOBJECT n_receiver) = 0
S_caught_step = $drive_steps(S_before_catch, 1)
S_caught_step.COMPLETION = BUDGET
S_caught = S_caught_step[.COMPLETION = NORMAL]
$lookup(S_caught.ENV, $ptascii("caught")) = (n_caught_cell)
S_caught.STORE[n_caught_cell] = DEFINED (POBJECT n_exception)
$heap_owners($heap_graph(S_caught), HOBJECT n_exception) = 1
$weakref_get(S_caught, n_weak_exception) = POBJECT n_exception
$weakref_get(S_caught, n_weak_capture) = PNULL
$weakref_get(S_caught, n_weak_receiver) = PNULL
$outputs(S_caught.EVENTS) = $outputs(S_finally.EVENTS)
S_zero = $drive_steps(S_invoke, 0)
S_zero = S_invoke[.COMPLETION = BUDGET]
S_done = $drive(S_zero[.COMPLETION = NORMAL], 1000)
S_done = $drive(S_invoke, 1000)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.ACTIVEFIBER = eps
S_done.FIBERCALLERS = eps
S_done.STORE[n_caught_cell] = DEFINED PNULL
~((HOBJECT n_capture) <- S_done.ALLOCATIONS)
~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)
~((HOBJECT n_exception) <- S_done.ALLOCATIONS)
$heap_owners($heap_graph(S_done), HOBJECT n_exception) = 0
$weakref_get(S_done, n_weak_exception) = PNULL
$weakref_get(S_done, n_weak_capture) = PNULL
$weakref_get(S_done, n_weak_receiver) = PNULL
$from_factory_saved(S_done, n_factory)
~$from_factory_live(S_done, n_factory)
~$fiber_capture_source_valid(S_done, pfibercapture)
''') + [f'$outputs(S_done.EVENTS) = $ptascii("{expected}")'] + guards('S_before_catch') + guards('S_caught') + guards('S_done')
    controls = prior[genuine_count:]
    controls += lines(r'''
S_finally_bad_phase = S_finally[.TODO = (FINALLY_RESUME porigin_finally (n_exception)) :: (FINALLY_PHASE porigin_finally 0) :: ptask_after_finally*]
$heap_graph(S_finally_bad_phase) = $heap_graph(S_finally)
~$call_task_valid(S_finally_bad_phase, FINALLY_RESUME porigin_finally (n_exception))
~$call_descriptors_valid(S_finally_bad_phase)
S_finish_bad_mode = S_finish[.TODO = [FIBER_RETURN_FINISH pfiberfinish]]
$heap_graph(S_finish_bad_mode) = $heap_graph(S_finish)
~$call_task_valid(S_finish_bad_mode, FIBER_RETURN_FINISH pfiberfinish)
~$call_descriptors_valid(S_finish_bad_mode)
pfiberfinish_bad = pfiberfinish[.SEQUENCE = 0]
S_finish_bad_sequence = S_finish[.TODO = [FIBER_THROW_FINISH pfiberfinish_bad]]
~$call_task_valid(S_finish_bad_sequence, FIBER_THROW_FINISH pfiberfinish_bad)
~$call_descriptors_valid(S_finish_bad_sequence)
~$throwable_binding_valid(S_before_catch, porigin_outer_try, n_catch, n_receiver)
''')
    checks = genuine + controls
    text = EXTRA + UNHANDLED + PREFIX[PREFIX.index('dec $outputs'):]
    text += '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks, len(genuine), len(controls)
