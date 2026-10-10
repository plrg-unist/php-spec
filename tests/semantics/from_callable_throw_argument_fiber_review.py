"""Reached wrong-Throwable reception, scalar trace and INITIAL callback retirement."""
from from_callable_throw_fiber_review import EXTRA, guards, lines, render as handled_render
from error_handler_protocol import PREFIX


ARGUMENT = r'''
dec $throw_argument_stage(pstate, nat) : bool
def $throw_argument_stage(S, 0) = true
  -- if S.TODO = (THROW_SEARCH n) :: (FIBER_CAPTURE_RELEASE n_capture porigin) :: ptask*
  -- if S.ACTIVEFIBER = eps
def $throw_argument_stage(S, 1) = true
  -- if S.TODO = (CATCH_BIND porigin n_catch n) :: ptask*
  -- if S.ACTIVEFIBER = eps
def $throw_argument_stage(S, n) = false -- otherwise
dec $throw_argument_seek(pstate, nat, nat) : pstate
def $throw_argument_seek(S, n_phase, n) = S
  -- if $throw_argument_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $throw_argument_seek(S, n_phase, n) = $throw_argument_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if ~$throw_argument_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $throw_argument_seek(S, n_phase, 0) = S
  -- if ~$throw_argument_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $throw_argument_seek(S, n_phase, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''


def seek(state, previous, phase):
    return [f'{state}_reached = $throw_argument_seek({previous}, {phase}, 1000)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$throw_argument_stage({state}, {phase})']


def render(program, filename, expected):
    _, prior, genuine_count, _ = handled_render(program, filename, expected)
    cut = next(i for i, check in enumerate(prior) if check.startswith('S_invoke_reached ='))
    genuine = prior[:cut]
    # The new original has no pre-created Exception; reuse only factory/mint checks.
    begin = genuine.index('$lookup(S_factory.ENV, $ptascii("exception")) = (n_exception_cell)')
    end = genuine.index('$call_current_valid(S_factory)', begin)
    del genuine[begin:end]
    genuine += lines(r'''
S_invoke_reached = $throw_peer_seek(S_minted, 1, 1000)
S_invoke_reached.COMPLETION = NORMAL \/ S_invoke_reached.COMPLETION = BUDGET
S_invoke = S_invoke_reached[.COMPLETION = NORMAL]
$throw_peer_stage(S_invoke, 1)
S_invoke.TODO = (CONFIG_INVOKE pconfigcall_throw) :: ptask_release*
ptask_release* = (FIBER_CAPTURE_RELEASE n_capture pconfigcall_throw.SITE) :: ptask_after_call*
pconfigcall_throw.KIND = INTRINSIC_FIBER_THROW
pconfigcall_throw.OWNER = (n_receiver)
pconfigcall_throw.SELECTION = (n_capture)
pconfigcall_throw.NAMED
pconfigcall_throw.SENT = [NAMED_SENT (KNOWN (PINT 7))]
~$class_instanceof(S_invoke, PINT 7, $ptascii("Throwable"))
$config_nodes(pconfigcall_throw) = eps
$task_nodes(FIBER_CAPTURE_RELEASE n_capture pconfigcall_throw.SITE) = [HOBJECT n_capture]
$lookup(S_invoke.ENV, $ptascii("selected")) = (n_selected_cell)
S_invoke.STORE[n_selected_cell] = DEFINED PNULL
n_selected_cell <- S_invoke.REFCELLS
$lookup(S_invoke.ENV, $ptascii("fiber")) = (n_fiber_cell)
S_invoke.STORE[n_fiber_cell] = DEFINED PNULL
S_invoke.STORE[n_callback_cell] = DEFINED PNULL
S_invoke.STORE[n_method_cell] = DEFINED pvalue_changed
$string_bytes(pvalue_changed) = ($ptascii("isStarted"))
~((HOBJECT n_factory) <- S_invoke.ALLOCATIONS)
~((HARRAY n_callback) <- S_invoke.ALLOCATIONS)
~((HARRAY n_original_callback) <- S_invoke.ALLOCATIONS)
$heap_owners($heap_graph(S_invoke), HOBJECT n_factory) = 0
$heap_owners($heap_graph(S_invoke), HARRAY n_callback) = 0
$heap_owners($heap_graph(S_invoke), HARRAY n_original_callback) = 0
$heap_owners($heap_graph(S_invoke), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_invoke), HOBJECT n_receiver) = 1
$node_children(S_invoke, HOBJECT n_capture) = [HOBJECT n_receiver]
$fiber_at(S_invoke, n_receiver) = (pfiber_initial)
pfiber_initial.STATUS = FIBER_INIT
pfiber_initial.READY
pfiber_initial.RAW = POBJECT n_body
pfiber_initial.VM = eps
pfiber_initial.FINISH = eps
pfiber_initial.SEQUENCE = 0
~pfiber_initial.RETURNED
~pfiber_initial.FAILED
~pfiber_initial.GRACEFUL
S_invoke.ACTIVEFIBER = eps
S_invoke.FIBERCALLERS = eps
S_invoke.FIBERCLOSERS = eps
S_invoke.FIBERSEQ = 1
~$destructor_operational(S_invoke)
S_invoke.CURRENT = eps
S_invoke.FRAMES = eps
$node_children(S_invoke, HOBJECT n_receiver) = [HOBJECT n_body]
$heap_owners($heap_graph(S_invoke), HOBJECT n_body) = 1
$lookup(S_invoke.ENV, $ptascii("weakSelected")) = (n_weak_capture_cell)
S_invoke.STORE[n_weak_capture_cell] = DEFINED (POBJECT n_weak_capture)
$weakref_get(S_invoke, n_weak_capture) = POBJECT n_capture
$lookup(S_invoke.ENV, $ptascii("weakFiber")) = (n_weak_receiver_cell)
S_invoke.STORE[n_weak_receiver_cell] = DEFINED (POBJECT n_weak_receiver)
$weakref_get(S_invoke, n_weak_receiver) = POBJECT n_receiver
$node_children(S_invoke, HOBJECT n_weak_capture) = eps
$node_children(S_invoke, HOBJECT n_weak_receiver) = eps
$from_factory_saved(S_invoke, n_factory)
~$from_factory_live(S_invoke, n_factory)
$fiber_factory_saved_call(S_invoke, pconfigcall_factory, INTRINSIC_FIBER_THROW, (n_receiver))
$fiber_capture_source_valid(S_invoke, pfibercapture)
$fiber_capture_config_selected(S_invoke, pconfigcall_throw)
$config_invoke_valid(S_invoke, pconfigcall_throw)
$outputs(S_invoke.EVENTS) = $ptascii("Q;A;M:isStarted;F;H:held;V;")
''') + guards('S_invoke')
    # Reception is a derived query on this reached producer, not a second source run.
    genuine += lines(r'''
S_received = $config_receive(S_invoke, pconfigcall_throw)
S_received.COMPLETION = THROWING n_error
n_error = |S_invoke.OBJECTS|
S_received.OBJECTS[n_error] = THROWABLE pthrowable_error
pthrowable_error = {KIND "TypeError", ORIGIN (pconfigcall_throw.SITE), FILEORIGIN (pconfigcall_throw.SITE)}
S_received.CURRENT = S_invoke.CURRENT
S_received.FRAMES = S_invoke.FRAMES
S_received.ACTIVEFIBER = eps
S_received.FIBERCALLERS = eps
S_received.FIBERCLOSERS = eps
S_received.FIBERSEQ = S_invoke.FIBERSEQ
$fiber_at(S_received, n_receiver) = (pfiber_initial)
$heap_owners($heap_graph(S_received), HOBJECT n_error) = 1
$heap_owners($heap_graph(S_received), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_received), HOBJECT n_receiver) = 1
$throwable_field(S_received, n_error, "trace") = PARRAY n_trace
S_received.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]
S_received.ARRAYS[n_frame].ITEMS = [ENTRY (KSTRING $ptascii("file")) (DIRECT (PSTRING $call_sourcefile(S_invoke.FILES, pconfigcall_throw.SITE))), ENTRY (KSTRING $ptascii("line")) (DIRECT (PINT pconfigcall_throw.LINE)), ENTRY (KSTRING $ptascii("function")) (DIRECT (PSTRING $ptascii("throw"))), ENTRY (KSTRING $ptascii("class")) (DIRECT (PSTRING $ptascii("Fiber"))), ENTRY (KSTRING $ptascii("type")) (DIRECT (PSTRING $ptascii("->"))), ENTRY (KSTRING $ptascii("args")) (DIRECT (PARRAY n_args))]
S_received.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]
$node_children(S_received, HOBJECT n_error) = [HARRAY n_trace]
$node_children(S_received, HARRAY n_trace) = [HARRAY n_frame]
$node_children(S_received, HARRAY n_frame) = [HARRAY n_args]
$node_children(S_received, HARRAY n_args) = eps
$trace_argument_array_valid(S_received, n_args)
$trace_graph_valid(S_received, n_trace)
$throwable_object_image_valid(S_received, n_error)
$throwable_live(S_received, n_error)
S_rejected_step = $drive_steps(S_invoke, 1)
S_rejected_step.COMPLETION = BUDGET
S_rejected = S_rejected_step[.COMPLETION = NORMAL]
$throw_argument_stage(S_rejected, 0)
S_rejected.TODO = (THROW_SEARCH n_error) :: (FIBER_CAPTURE_RELEASE n_capture pconfigcall_throw.SITE) :: ptask_after_call*
S_rejected.OBJECTS = S_received.OBJECTS
S_rejected.ARRAYS = S_received.ARRAYS
S_rejected.OBJECTPROPS = S_received.OBJECTPROPS
S_rejected.ALLOCATIONS = S_received.ALLOCATIONS
S_rejected.RESULT = KNOWN PNULL
S_rejected.BASE = BASE_VALUE (KNOWN PNULL)
S_rejected.HELD = eps
S_rejected.CURRENT = S_invoke.CURRENT
S_rejected.FRAMES = S_invoke.FRAMES
S_rejected.ACTIVEFIBER = eps
S_rejected.FIBERCALLERS = eps
S_rejected.FIBERCLOSERS = eps
S_rejected.FIBERSEQ = S_invoke.FIBERSEQ
$fiber_at(S_rejected, n_receiver) = (pfiber_initial)
$task_nodes(THROW_SEARCH n_error) = [HOBJECT n_error]
$fiber_capture_release_valid(S_rejected, n_capture, pconfigcall_throw.SITE)
$heap_owners($heap_graph(S_rejected), HOBJECT n_error) = 1
$heap_owners($heap_graph(S_rejected), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_rejected), HOBJECT n_receiver) = 1
$heap_owners($heap_graph(S_rejected), HOBJECT n_body) = 1
$outputs(S_rejected.EVENTS) = $outputs(S_invoke.EVENTS)
S_retired_step = $drive_steps(S_rejected, 1)
S_retired_step.COMPLETION = BUDGET
S_retired = S_retired_step[.COMPLETION = NORMAL]
S_retired.TODO = (THROW_SEARCH n_error) :: ptask_after_call*
S_retired.DESTRUCTION.OPERATIONS = eps
S_retired.DESTRUCTION.RELEASES = eps
~$destructor_operational(S_retired)
~((HOBJECT n_capture) <- S_retired.ALLOCATIONS)
~((HOBJECT n_receiver) <- S_retired.ALLOCATIONS)
~((HOBJECT n_body) <- S_retired.ALLOCATIONS)
$heap_owners($heap_graph(S_retired), HOBJECT n_capture) = 0
$heap_owners($heap_graph(S_retired), HOBJECT n_receiver) = 0
$heap_owners($heap_graph(S_retired), HOBJECT n_body) = 0
$heap_owners($heap_graph(S_retired), HOBJECT n_error) = 1
$weakref_get(S_retired, n_weak_capture) = PNULL
$weakref_get(S_retired, n_weak_receiver) = PNULL
$throwable_live(S_retired, n_error)
$trace_graph_valid(S_retired, n_trace)
S_retired.ACTIVEFIBER = eps
S_retired.FIBERCALLERS = eps
S_retired.FIBERCLOSERS = eps
S_retired.FIBERSEQ = S_invoke.FIBERSEQ
~$fiber_capture_source_valid(S_retired, pfibercapture)
$outputs(S_retired.EVENTS) = $outputs(S_invoke.EVENTS)
''') + guards('S_rejected') + guards('S_retired')
    genuine += seek('S_before_catch', 'S_retired', 1) + lines(r'''
S_before_catch.TODO = (CATCH_BIND porigin_outer_try n_catch n_error) :: ptask_after_catch*
S_before_catch.ACTIVEFIBER = eps
S_before_catch.FIBERCALLERS = eps
S_before_catch.FIBERCLOSERS = eps
S_before_catch.FIBERSEQ = S_invoke.FIBERSEQ
$throwable_binding_valid(S_before_catch, porigin_outer_try, n_catch, n_error)
$task_nodes(CATCH_BIND porigin_outer_try n_catch n_error) = [HOBJECT n_error]
$heap_owners($heap_graph(S_before_catch), HOBJECT n_error) = 1
$heap_owners($heap_graph(S_before_catch), HOBJECT n_capture) = 0
$heap_owners($heap_graph(S_before_catch), HOBJECT n_receiver) = 0
S_caught_step = $drive_steps(S_before_catch, 1)
S_caught_step.COMPLETION = BUDGET
S_caught = S_caught_step[.COMPLETION = NORMAL]
$lookup(S_caught.ENV, $ptascii("caught")) = (n_caught_cell)
S_caught.STORE[n_caught_cell] = DEFINED (POBJECT n_error)
$heap_owners($heap_graph(S_caught), HOBJECT n_error) = 1
$weakref_get(S_caught, n_weak_capture) = PNULL
$weakref_get(S_caught, n_weak_receiver) = PNULL
$outputs(S_caught.EVENTS) = $outputs(S_invoke.EVENTS)
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
S_done.FIBERCLOSERS = eps
S_done.FIBERSEQ = S_invoke.FIBERSEQ
S_done.STORE[n_caught_cell] = DEFINED PNULL
~((HOBJECT n_capture) <- S_done.ALLOCATIONS)
~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)
~((HOBJECT n_body) <- S_done.ALLOCATIONS)
~((HOBJECT n_error) <- S_done.ALLOCATIONS)
~((HARRAY n_trace) <- S_done.ALLOCATIONS)
~((HARRAY n_frame) <- S_done.ALLOCATIONS)
~((HARRAY n_args) <- S_done.ALLOCATIONS)
$heap_owners($heap_graph(S_done), HOBJECT n_error) = 0
$weakref_get(S_done, n_weak_capture) = PNULL
$weakref_get(S_done, n_weak_receiver) = PNULL
$lookup(S_done.ENV, $ptascii("weakError")) = (n_weak_error_cell)
S_done.STORE[n_weak_error_cell] = DEFINED (POBJECT n_weak_error)
$weakref_get(S_done, n_weak_error) = PNULL
$from_factory_saved(S_done, n_factory)
~$from_factory_live(S_done, n_factory)
~$fiber_capture_source_valid(S_done, pfibercapture)
''') + [f'$outputs(S_done.EVENTS) = $ptascii("{expected}")'] + guards('S_before_catch') + guards('S_caught') + guards('S_done')
    # Only the prior factory certificate controls apply to this new INITIAL source.
    controls = prior[genuine_count:]
    cut = controls.index('pfiberapi_bad_site = pfiberapi_throw[.SITE = pconfigcall_factory.SITE]')
    controls = controls[:cut]
    controls += lines(r'''
S_bad_release_site = S_rejected[.TODO = (THROW_SEARCH n_error) :: (FIBER_CAPTURE_RELEASE n_capture pconfigcall_factory.SITE) :: ptask_after_call*]
$heap_graph(S_bad_release_site) = $heap_graph(S_rejected)
~$fiber_capture_release_valid(S_bad_release_site, n_capture, pconfigcall_factory.SITE)
~$call_descriptors_valid(S_bad_release_site)
S_bad_trace_alias = S_rejected[.ARRAYS = $array_replace(S_rejected.ARRAYS, n_args, S_rejected.ARRAYS[n_args][.ITEMS = [ENTRY (KINT 0) (ALIAS n_method_cell)]])]
~$trace_argument_array_valid(S_bad_trace_alias, n_args)
~$trace_graph_valid(S_bad_trace_alias, n_trace)
~$throwable_object_image_valid(S_bad_trace_alias, n_error)
~$throwable_live(S_bad_trace_alias, n_error)
~$call_descriptors_valid(S_bad_trace_alias)
~$throwable_binding_valid(S_before_catch, porigin_outer_try, n_catch, n_receiver)
''')
    checks = genuine + controls
    text = EXTRA + ARGUMENT + PREFIX[PREFIX.index('dec $outputs'):]
    text += '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks, len(genuine), len(controls)
