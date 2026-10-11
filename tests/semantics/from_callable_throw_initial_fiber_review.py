"""Reached INITIAL rejection and the fresh FiberError's owning Throwable argument."""
from from_callable_throw_argument_fiber_review import render as argument_render
from from_callable_throw_fiber_review import lines


def render(program, filename, expected):
    text, prior, genuine_count, _ = argument_render(program, filename, expected)
    replacements = {
        'pconfigcall_throw.SENT = [NAMED_SENT (KNOWN (PINT 7))]':
            'pconfigcall_throw.SENT = [NAMED_SENT (KNOWN (POBJECT n_argument))]',
        '~$class_instanceof(S_invoke, PINT 7, $ptascii("Throwable"))':
            '$class_instanceof(S_invoke, POBJECT n_argument, $ptascii("Throwable"))',
        '$config_nodes(pconfigcall_throw) = eps':
            '$config_nodes(pconfigcall_throw) = [HOBJECT n_argument]',
        'pthrowable_error = {KIND "TypeError", ORIGIN (pconfigcall_throw.SITE), FILEORIGIN (pconfigcall_throw.SITE)}':
            'pthrowable_error = {KIND "FiberError", ORIGIN (pconfigcall_throw.SITE), FILEORIGIN (pconfigcall_throw.SITE)}',
        'S_received.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]':
            'S_received.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_argument))]',
        '$node_children(S_received, HARRAY n_args) = eps':
            '$node_children(S_received, HARRAY n_args) = [HOBJECT n_argument]',
    }
    assert all(prior.count(check) == 1 for check in replacements)
    additions = {
        '$call_current_valid(S_factory)': lines(r'''
$lookup(S_factory.ENV, $ptascii("argument")) = (n_argument_cell)
S_factory.STORE[n_argument_cell] = DEFINED (POBJECT n_argument)
S_factory.OBJECTS[n_argument] = THROWABLE pthrowable_argument
pthrowable_argument.KIND = "Exception"
$throwable_field(S_factory, n_argument, "trace") = PARRAY n_argument_trace
S_factory.ARRAYS[n_argument_trace].ITEMS = eps
$node_children(S_factory, HOBJECT n_argument) = [HARRAY n_argument_trace]
$heap_owners($heap_graph(S_factory), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S_factory), HARRAY n_argument_trace) = 1
$lookup(S_factory.ENV, $ptascii("weakArgument")) = (n_weak_argument_cell)
S_factory.STORE[n_weak_argument_cell] = DEFINED (POBJECT n_weak_argument)
$weakref_get(S_factory, n_weak_argument) = POBJECT n_argument
$node_children(S_factory, HOBJECT n_weak_argument) = eps
$throwable_live(S_factory, n_argument)
'''),
        '$call_current_valid(S_invoke)': lines(r'''
S_invoke.STORE[n_argument_cell] = DEFINED PNULL
n_argument_cell <- S_invoke.REFCELLS
S_invoke.OBJECTS[n_argument] = S_factory.OBJECTS[n_argument]
$throwable_field(S_invoke, n_argument, "trace") = PARRAY n_argument_trace
S_invoke.ARRAYS[n_argument_trace].ITEMS = eps
$heap_owners($heap_graph(S_invoke), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S_invoke), HARRAY n_argument_trace) = 1
$weakref_get(S_invoke, n_weak_argument) = POBJECT n_argument
$throwable_live(S_invoke, n_argument)
'''),
        'S_rejected_step = $drive_steps(S_invoke, 1)': lines(r'''
n_error =/= n_argument
n_trace =/= n_argument_trace
$string_bytes($throwable_field(S_received, n_error, "message")) = ($ptascii("Cannot resume a fiber that is not suspended"))
$throwable_field(S_received, n_error, "previous") = PNULL
S_received.OBJECTS[n_argument] = S_invoke.OBJECTS[n_argument]
S_received.ARRAYS[n_argument_trace] = S_invoke.ARRAYS[n_argument_trace]
$node_children(S_received, HOBJECT n_argument) = [HARRAY n_argument_trace]
$heap_owners($heap_graph(S_received), HOBJECT n_argument) = 2
$heap_owners($heap_graph(S_received), HARRAY n_argument_trace) = 1
S_received.RESULT = KNOWN (PARRAY n_trace)
$heap_owners($heap_graph(S_received), HARRAY n_trace) = 2
$heap_owners($heap_graph(S_received), HARRAY n_frame) = 1
$heap_owners($heap_graph(S_received), HARRAY n_args) = 1
$weakref_get(S_received, n_weak_argument) = POBJECT n_argument
$throwable_live(S_received, n_argument)
'''),
        'S_retired_step = $drive_steps(S_rejected, 1)': lines(r'''
S_rejected.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_argument))]
$node_children(S_rejected, HARRAY n_args) = [HOBJECT n_argument]
$node_children(S_rejected, HOBJECT n_argument) = [HARRAY n_argument_trace]
$heap_owners($heap_graph(S_rejected), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S_rejected), HARRAY n_argument_trace) = 1
$heap_owners($heap_graph(S_rejected), HARRAY n_trace) = 1
$heap_owners($heap_graph(S_rejected), HARRAY n_frame) = 1
$heap_owners($heap_graph(S_rejected), HARRAY n_args) = 1
$weakref_get(S_rejected, n_weak_argument) = POBJECT n_argument
$throwable_live(S_rejected, n_argument)
'''),
        'S_before_catch_reached = $throw_argument_seek(S_retired, 1, 1000)': lines(r'''
S_retired.OBJECTS[n_argument] = S_rejected.OBJECTS[n_argument]
S_retired.OBJECTS[n_error] = S_rejected.OBJECTS[n_error]
S_retired.ARRAYS = S_rejected.ARRAYS
S_retired.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_argument))]
$node_children(S_retired, HOBJECT n_error) = [HARRAY n_trace]
$node_children(S_retired, HARRAY n_trace) = [HARRAY n_frame]
$node_children(S_retired, HARRAY n_frame) = [HARRAY n_args]
$node_children(S_retired, HARRAY n_args) = [HOBJECT n_argument]
$node_children(S_retired, HOBJECT n_argument) = [HARRAY n_argument_trace]
$heap_owners($heap_graph(S_retired), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S_retired), HARRAY n_argument_trace) = 1
$heap_owners($heap_graph(S_retired), HARRAY n_trace) = 1
$heap_owners($heap_graph(S_retired), HARRAY n_frame) = 1
$heap_owners($heap_graph(S_retired), HARRAY n_args) = 1
$weakref_get(S_retired, n_weak_argument) = POBJECT n_argument
$throwable_live(S_retired, n_argument)
'''),
        'S_caught_step = $drive_steps(S_before_catch, 1)': lines(r'''
$heap_owners($heap_graph(S_before_catch), HOBJECT n_argument) = 1
$weakref_get(S_before_catch, n_weak_argument) = POBJECT n_argument
S_before_catch.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_argument))]
'''),
        'S_zero = $drive_steps(S_invoke, 0)': lines(r'''
$heap_owners($heap_graph(S_caught), HOBJECT n_argument) = 1
$weakref_get(S_caught, n_weak_argument) = POBJECT n_argument
S_caught.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_argument))]
$throwable_live(S_caught, n_argument)
'''),
        f'$outputs(S_done.EVENTS) = $ptascii("{expected}")': lines(r'''
~((HOBJECT n_argument) <- S_done.ALLOCATIONS)
~((HARRAY n_argument_trace) <- S_done.ALLOCATIONS)
$heap_owners($heap_graph(S_done), HOBJECT n_argument) = 0
$heap_owners($heap_graph(S_done), HARRAY n_argument_trace) = 0
$weakref_get(S_done, n_weak_argument) = PNULL
'''),
    }
    assert all(prior[:genuine_count].count(check) == 1 for check in additions)
    genuine = []
    for check in prior[:genuine_count]:
        genuine += additions.get(check, [])
        genuine.append(replacements.get(check, check))
    cleared = lines(r'''
S_cleared_reached = $throw_initial_seek(S_caught, 2, 1000)
S_cleared_reached.COMPLETION = NORMAL \/ S_cleared_reached.COMPLETION = BUDGET
S_cleared = S_cleared_reached[.COMPLETION = NORMAL]
$throw_initial_stage(S_cleared, 2)
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
~((HOBJECT n_argument) <- S_cleared.ALLOCATIONS)
~((HARRAY n_trace) <- S_cleared.ALLOCATIONS)
~((HARRAY n_frame) <- S_cleared.ALLOCATIONS)
~((HARRAY n_args) <- S_cleared.ALLOCATIONS)
~((HARRAY n_argument_trace) <- S_cleared.ALLOCATIONS)
$heap_owners($heap_graph(S_cleared), HOBJECT n_error) = 0
$heap_owners($heap_graph(S_cleared), HOBJECT n_argument) = 0
$weakref_get(S_cleared, n_weak_argument) = PNULL
$weakref_get(S_cleared, n_weak_capture) = PNULL
$weakref_get(S_cleared, n_weak_receiver) = PNULL
$lookup(S_cleared.ENV, $ptascii("weakError")) = (n_weak_error_cell)
S_cleared.STORE[n_weak_error_cell] = DEFINED (POBJECT n_weak_error)
$weakref_get(S_cleared, n_weak_error) = PNULL
$outputs(S_cleared.EVENTS) = $ptascii("Q;A;M:isStarted;F;H:held;V;T:FiberError;D:Cannot resume a fiber that is not suspended;X:held;C:gone;H:gone;E:held;")
$call_current_valid(S_cleared)
$call_frames_valid(S_cleared, S_cleared.FRAMES)
$call_descriptors_valid(S_cleared)
$class_constant_history_valid(S_cleared)
$fiber_state_valid(S_cleared)
$heap_valid($heap_graph(S_cleared))
''')
    genuine[genuine.index('S_zero = $drive_steps(S_invoke, 0)'):genuine.index('S_zero = $drive_steps(S_invoke, 0)')] = cleared
    genuine.insert(genuine.index('S_done.COMPLETION = NORMAL'), 'S_done = $drive(S_cleared, 1000)')
    controls = prior[genuine_count:] + lines(r'''
S_other_trace_argument = S_rejected[.ARRAYS = $array_replace(S_rejected.ARRAYS, n_args, S_rejected.ARRAYS[n_args][.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver))]])]
S_other_trace_argument.ARRAYS[n_args].ITEMS =/= [ENTRY (KINT 0) (DIRECT (POBJECT n_argument))]
$node_children(S_other_trace_argument, HARRAY n_args) = [HOBJECT n_receiver]
$heap_graph(S_other_trace_argument) =/= $heap_graph(S_rejected)
''')
    checks = [check.replace('$throw_argument_', '$throw_initial_') for check in genuine + controls]
    prefix = text[:text.index('\ndec $main()')].replace('$throw_argument_', '$throw_initial_')
    prefix = prefix.replace('def $throw_initial_stage(S, n) = false -- otherwise', r'''def $throw_initial_stage(S, 2) = true
  -- if $lookup(S.ENV, $ptascii("caught")) = (n_caught)
  -- if S.STORE[n_caught] = DEFINED PNULL
  -- if S.TODO =/= eps
def $throw_initial_stage(S, n) = false -- otherwise''')
    prefix += '\ndec $main() : bool\ndef $main() = true\n'
    prefix += ''.join('  -- if ' + check + '\n' for check in checks)
    return prefix, checks, len(genuine), len(controls)
