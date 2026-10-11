"""Reached constructor rejection, fresh Closure trace ownership and quiet cleanup."""
from from_callable_throw_argument_fiber_review import render as argument_render
from from_callable_throw_fiber_review import lines


def render(program, filename, expected):
    text, prior, genuine_count, _ = argument_render(program, filename, expected)
    replacements = {
        'pconfigcall_throw.SENT = [NAMED_SENT (KNOWN (PINT 7))]':
            'pconfigcall_throw.SENT = [NAMED_SENT (KNOWN (POBJECT n_fresh))]',
        '~$class_instanceof(S_invoke, PINT 7, $ptascii("Throwable"))':
            '~$api_special(S_invoke, POBJECT n_fresh)',
        '$config_nodes(pconfigcall_throw) = eps':
            '$config_nodes(pconfigcall_throw) = [HOBJECT n_fresh]',
        'pthrowable_error = {KIND "TypeError", ORIGIN (pconfigcall_throw.SITE), FILEORIGIN (pconfigcall_throw.SITE)}':
            'pthrowable_error = {KIND "FiberError", ORIGIN (pconfigcall_throw.SITE), FILEORIGIN (pconfigcall_throw.SITE)}',
        'S_received.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]':
            'S_received.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_fresh))]',
        '$node_children(S_received, HARRAY n_args) = eps':
            '$node_children(S_received, HARRAY n_args) = [HOBJECT n_fresh]',
    }
    assert all(prior.count(check) == 1 for check in replacements)
    additions = {
        '$call_current_valid(S_factory)': lines(r'''
$fiber_factory_construct(S_factory, pconfigcall_factory, PARRAY n_callback)
pfiber_initial.READY
pfiber_initial.RAW = POBJECT n_body
$lookup(S_factory.ENV, $ptascii("old")) = (n_old_cell)
S_factory.STORE[n_old_cell] = DEFINED PNULL
$lookup(S_factory.ENV, $ptascii("weakOld")) = (n_weak_body_cell)
S_factory.STORE[n_weak_body_cell] = DEFINED (POBJECT n_weak_body)
$weakref_get(S_factory, n_weak_body) = POBJECT n_body
$node_children(S_factory, HOBJECT n_weak_body) = eps
$node_children(S_factory, HOBJECT n_body) = eps
$node_children(S_factory, HOBJECT n_receiver) = [HOBJECT n_body]
$heap_owners($heap_graph(S_factory), HOBJECT n_body) = 1
'''),
        '$call_current_valid(S_invoke)': lines(r'''
$lookup(S_invoke.ENV, $ptascii("fresh")) = (n_fresh_cell)
S_invoke.STORE[n_fresh_cell] = DEFINED PNULL
n_fresh_cell <- S_invoke.REFCELLS
S_invoke.STORE[n_old_cell] = DEFINED PNULL
$(n_fresh >= |S_minted.OBJECTS|)
n_fresh =/= n_body
n_fresh =/= n_capture
n_fresh =/= n_receiver
$class_instanceof(S_invoke, POBJECT n_fresh, $ptascii("Closure"))
$closure_callable(S_invoke, n_fresh)
$closure_live_object_valid(S_invoke, n_fresh)
$fiber_callback_resolution(S_invoke, POBJECT n_fresh) = HANDLERRESOLVED pcalltarget_fresh
$error_handler_callable(S_invoke, POBJECT n_fresh) = (true)
$error_handler_selected(S_invoke, POBJECT n_fresh, pcalltarget_fresh)
$target_function(S_invoke, pcalltarget_fresh) = (pfunction_fresh)
$node_children(S_invoke, HOBJECT n_fresh) = eps
$heap_owners($heap_graph(S_invoke), HOBJECT n_fresh) = 1
$lookup(S_invoke.ENV, $ptascii("weakFresh")) = (n_weak_fresh_cell)
S_invoke.STORE[n_weak_fresh_cell] = DEFINED (POBJECT n_weak_fresh)
$weakref_get(S_invoke, n_weak_fresh) = POBJECT n_fresh
$node_children(S_invoke, HOBJECT n_weak_fresh) = eps
$weakref_get(S_invoke, n_weak_body) = POBJECT n_body
'''),
        'S_rejected_step = $drive_steps(S_invoke, 1)': lines(r'''
n_error =/= n_fresh
$string_bytes($throwable_field(S_received, n_error, "message")) = ($ptascii("Cannot call constructor twice"))
$throwable_field(S_received, n_error, "previous") = PNULL
S_received.OBJECTS[n_fresh] = S_invoke.OBJECTS[n_fresh]
$node_children(S_received, HOBJECT n_fresh) = eps
$heap_owners($heap_graph(S_received), HOBJECT n_fresh) = 2
S_received.RESULT = KNOWN (PARRAY n_trace)
$heap_owners($heap_graph(S_received), HARRAY n_trace) = 2
$heap_owners($heap_graph(S_received), HARRAY n_frame) = 1
$heap_owners($heap_graph(S_received), HARRAY n_args) = 1
$weakref_get(S_received, n_weak_fresh) = POBJECT n_fresh
$closure_live_object_valid(S_received, n_fresh)
'''),
        'S_retired_step = $drive_steps(S_rejected, 1)': lines(r'''
S_rejected.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_fresh))]
$node_children(S_rejected, HARRAY n_args) = [HOBJECT n_fresh]
$node_children(S_rejected, HOBJECT n_fresh) = eps
$heap_owners($heap_graph(S_rejected), HOBJECT n_fresh) = 1
$heap_owners($heap_graph(S_rejected), HARRAY n_trace) = 1
$heap_owners($heap_graph(S_rejected), HARRAY n_frame) = 1
$heap_owners($heap_graph(S_rejected), HARRAY n_args) = 1
$weakref_get(S_rejected, n_weak_fresh) = POBJECT n_fresh
$weakref_get(S_rejected, n_weak_body) = POBJECT n_body
$closure_live_object_valid(S_rejected, n_fresh)
'''),
        'S_before_catch_reached = $throw_argument_seek(S_retired, 1, 1000)': lines(r'''
S_retired.OBJECTS[n_fresh] = S_rejected.OBJECTS[n_fresh]
S_retired.OBJECTS[n_error] = S_rejected.OBJECTS[n_error]
S_retired.ARRAYS = S_rejected.ARRAYS
S_retired.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_fresh))]
$node_children(S_retired, HOBJECT n_error) = [HARRAY n_trace]
$node_children(S_retired, HARRAY n_trace) = [HARRAY n_frame]
$node_children(S_retired, HARRAY n_frame) = [HARRAY n_args]
$node_children(S_retired, HARRAY n_args) = [HOBJECT n_fresh]
$node_children(S_retired, HOBJECT n_fresh) = eps
$heap_owners($heap_graph(S_retired), HOBJECT n_fresh) = 1
$heap_owners($heap_graph(S_retired), HARRAY n_trace) = 1
$heap_owners($heap_graph(S_retired), HARRAY n_frame) = 1
$heap_owners($heap_graph(S_retired), HARRAY n_args) = 1
$weakref_get(S_retired, n_weak_fresh) = POBJECT n_fresh
$weakref_get(S_retired, n_weak_body) = PNULL
$closure_live_object_valid(S_retired, n_fresh)
'''),
        'S_caught_step = $drive_steps(S_before_catch, 1)': lines(r'''
$heap_owners($heap_graph(S_before_catch), HOBJECT n_fresh) = 1
$weakref_get(S_before_catch, n_weak_fresh) = POBJECT n_fresh
$weakref_get(S_before_catch, n_weak_body) = PNULL
S_before_catch.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_fresh))]
'''),
        'S_zero = $drive_steps(S_invoke, 0)': lines(r'''
$heap_owners($heap_graph(S_caught), HOBJECT n_fresh) = 1
$weakref_get(S_caught, n_weak_fresh) = POBJECT n_fresh
$weakref_get(S_caught, n_weak_body) = PNULL
S_caught.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_fresh))]
$closure_live_object_valid(S_caught, n_fresh)
'''),
        f'$outputs(S_done.EVENTS) = $ptascii("{expected}")': lines(r'''
~((HOBJECT n_fresh) <- S_done.ALLOCATIONS)
$heap_owners($heap_graph(S_done), HOBJECT n_fresh) = 0
$weakref_get(S_done, n_weak_fresh) = PNULL
$weakref_get(S_done, n_weak_body) = PNULL
'''),
    }
    assert all(prior[:genuine_count].count(check) == 1 for check in additions)
    genuine = []
    for check in prior[:genuine_count]:
        genuine += additions.get(check, [])
        genuine.append(replacements.get(check, check))
    cleared = lines(r'''
S_clear_before_reached = $construct_error_seek(S_caught, 3, 1000)
S_clear_before_reached.COMPLETION = NORMAL \/ S_clear_before_reached.COMPLETION = BUDGET
S_clear_before = S_clear_before_reached[.COMPLETION = NORMAL]
$construct_error_stage(S_clear_before, 3)
S_clear_before.TODO = (WRITE_NAME $ptascii("caught") z_clear) :: ptask_clear_tail*
S_clear_before.RESULT = KNOWN PNULL
S_clear_before.STORE[n_caught_cell] = DEFINED (POBJECT n_error)
S_clear_before.DESTRUCTION.OPERATIONS = eps
S_clear_before.DESTRUCTION.RELEASES = eps
$heap_owners($heap_graph(S_clear_before), HOBJECT n_error) = 1
$heap_owners($heap_graph(S_clear_before), HOBJECT n_fresh) = 1
S_clear_before.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_fresh))]
$weakref_get(S_clear_before, n_weak_fresh) = POBJECT n_fresh
$outputs(S_clear_before.EVENTS) = $ptascii("Q;A;M:isStarted;F;H:held;V;E:FiberError:Cannot call constructor twice;O:gone;C:gone;H:gone;N:held;E:held;")
S_clear_step = $drive_steps(S_clear_before, 1)
S_clear_step.COMPLETION = BUDGET
S_clear_written = S_clear_step[.COMPLETION = NORMAL]
S_clear_written.STORE[n_caught_cell] = DEFINED PNULL
S_clear_written.TODO = ptask_clear_tail*
S_clear_written.RESULT = KNOWN PNULL
S_clear_written.EVENTS = S_clear_before.EVENTS
S_cleared_reached = $construct_error_seek(S_clear_written, 2, 1000)
S_cleared_reached.COMPLETION = NORMAL \/ S_cleared_reached.COMPLETION = BUDGET
S_cleared = S_cleared_reached[.COMPLETION = NORMAL]
$construct_error_stage(S_cleared, 2)
S_cleared.STORE[n_caught_cell] = DEFINED PNULL
S_cleared.TODO =/= eps
S_cleared.CURRENT = eps
S_cleared.FRAMES = eps
S_cleared.ACTIVEFIBER = eps
S_cleared.FIBERCALLERS = eps
S_cleared.FIBERCLOSERS = eps
S_cleared.FIBERSEQ = S_invoke.FIBERSEQ
S_cleared.DESTRUCTION.OPERATIONS = eps
S_cleared.DESTRUCTION.RELEASES = eps
~((HOBJECT n_error) <- S_cleared.ALLOCATIONS)
~((HOBJECT n_fresh) <- S_cleared.ALLOCATIONS)
~((HOBJECT n_body) <- S_cleared.ALLOCATIONS)
~((HOBJECT n_capture) <- S_cleared.ALLOCATIONS)
~((HOBJECT n_receiver) <- S_cleared.ALLOCATIONS)
~((HARRAY n_trace) <- S_cleared.ALLOCATIONS)
~((HARRAY n_frame) <- S_cleared.ALLOCATIONS)
~((HARRAY n_args) <- S_cleared.ALLOCATIONS)
$heap_owners($heap_graph(S_cleared), HOBJECT n_error) = 0
$heap_owners($heap_graph(S_cleared), HOBJECT n_fresh) = 0
$weakref_get(S_cleared, n_weak_fresh) = PNULL
$weakref_get(S_cleared, n_weak_body) = PNULL
$weakref_get(S_cleared, n_weak_capture) = PNULL
$weakref_get(S_cleared, n_weak_receiver) = PNULL
$lookup(S_cleared.ENV, $ptascii("weakError")) = (n_weak_error_cell)
S_cleared.STORE[n_weak_error_cell] = DEFINED (POBJECT n_weak_error)
$weakref_get(S_cleared, n_weak_error) = PNULL
$outputs(S_cleared.EVENTS) = $ptascii("Q;A;M:isStarted;F;H:held;V;E:FiberError:Cannot call constructor twice;O:gone;C:gone;H:gone;N:held;E:held;")
$call_current_valid(S_cleared)
$call_frames_valid(S_cleared, S_cleared.FRAMES)
$call_descriptors_valid(S_cleared)
$class_constant_history_valid(S_cleared)
$fiber_state_valid(S_cleared)
$heap_valid($heap_graph(S_cleared))
''')
    index = genuine.index('S_zero = $drive_steps(S_invoke, 0)')
    genuine[index:index] = cleared
    genuine.insert(genuine.index('S_done.COMPLETION = NORMAL'),
                   'S_done = $drive(S_cleared, 1000)')
    controls = prior[genuine_count:] + lines(r'''
S_other_trace_argument = S_rejected[.ARRAYS = $array_replace(S_rejected.ARRAYS, n_args, S_rejected.ARRAYS[n_args][.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_body))]])]
S_other_trace_argument.ARRAYS[n_args].ITEMS =/= [ENTRY (KINT 0) (DIRECT (POBJECT n_fresh))]
$node_children(S_other_trace_argument, HARRAY n_args) = [HOBJECT n_body]
$heap_graph(S_other_trace_argument) =/= $heap_graph(S_rejected)
''')
    changes = {
        '$throw_peer_': '$construct_peer_',
        '$throw_argument_': '$construct_error_',
        'pconfigcall_throw': 'pconfigcall_construct',
        'INTRINSIC_FIBER_THROW': 'INTRINSIC_FIBER_CONSTRUCT',
        '$ptascii("throw")': '$ptascii("__construct")',
    }
    def renamed(check):
        for old, new in changes.items():
            check = check.replace(old, new)
        return check
    checks = [renamed(check) for check in genuine + controls]
    prefix = renamed(text[:text.index('\ndec $main()')])
    # Only the genuine factory and constructor producers use this seek family.
    start = prefix.index('def $construct_peer_stage(S, 2) = true')
    end = prefix.index('def $construct_peer_stage(S, n) = false -- otherwise', start)
    prefix = prefix[:start] + prefix[end:]
    prefix = prefix.replace('def $construct_error_stage(S, n) = false -- otherwise', r'''
def $construct_error_stage(S, 2) = true
  -- if $lookup(S.ENV, $ptascii("caught")) = (n_caught)
  -- if S.STORE[n_caught] = DEFINED PNULL
  -- if S.TODO =/= eps
def $construct_error_stage(S, 3) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("caught")
  -- if S.RESULT = KNOWN PNULL
def $construct_error_stage(S, n) = false -- otherwise''')
    prefix += '\ndec $main() : bool\ndef $main() = true\n'
    prefix += ''.join('  -- if ' + check + '\n' for check in checks)
    return prefix, checks, len(genuine), len(controls)
