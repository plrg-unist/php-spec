"""Reached named START buffer, callback-local release and ordinary buffer retirement."""
from error_handler_protocol import PREFIX
from from_callable_throw_fiber_review import guards, lines, render as throw_render


EXTRA = r'''
dec $start_peer_stage(pstate, nat) : bool
def $start_peer_stage(S, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_FROM_CALLABLE_FACTORY
def $start_peer_stage(S, 1) = true
  -- if S.TODO = (FIBER_START_CAPTURE_ARGS n pfiberstart) :: ptask*
  -- if pfiberstart.INDEX = 1
def $start_peer_stage(S, 2) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("value")
  -- if S.RESULT = KNOWN PNULL
  -- if S.ACTIVEFIBER =/= eps
def $start_peer_stage(S, 3) = true
  -- if S.ACTIVEFIBER =/= eps
  -- if S.CURRENT =/= eps
  -- if $lookup(S.ENV, $ptascii("value")) = (n_value)
  -- if S.STORE[n_value] = DEFINED PNULL
  -- if S.RESULT = KNOWN PNULL
  -- if S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.RELEASES = eps
  -- if S.TODO =/= eps
def $start_peer_stage(S, 4) = true
  -- if S.TODO = [FIBER_FINISH n]
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $start_peer_stage(S, 5) = true
  -- if S.TODO = [FIBER_RETURN_FINISH pfiberfinish]
def $start_peer_stage(S, 6) = true
  -- if S.TODO = (FIBER_START_CAPTURE_RESULT n pfiberstart false) :: ptask*
  -- if S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.RELEASES = eps
def $start_peer_stage(S, 7) = true
  -- if S.ACTIVEFIBER = eps
  -- if S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.RELEASES = eps
  -- if $lookup(S.ENV, $ptascii("weakFiber")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (POBJECT n_weak)
  -- if $weakref_get(S, n_weak) = PNULL
  -- if S.TODO =/= eps
def $start_peer_stage(S, n) = false -- otherwise
dec $start_peer_seek(pstate, nat, nat) : pstate
def $start_peer_seek(S, n_phase, n) = S
  -- if $start_peer_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $start_peer_seek(S, n_phase, n) = $start_peer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if ~$start_peer_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $start_peer_seek(S, n_phase, 0) = S
  -- if ~$start_peer_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $start_peer_seek(S, n_phase, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''


def seek(state, previous, phase):
    return [f'{state}_reached = $start_peer_seek({previous}, {phase}, 1000)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$start_peer_stage({state}, {phase})']


def render(program, filename, expected):
    _, prior, _, _ = throw_render(program, filename, expected)
    cut = next(i for i, check in enumerate(prior) if check.startswith('S_invoke_reached ='))
    genuine = prior[:cut]
    begin = genuine.index('$lookup(S_factory.ENV, $ptascii("exception")) = (n_exception_cell)')
    end = genuine.index('$call_current_valid(S_factory)', begin)
    del genuine[begin:end]
    genuine = [check.replace('$throw_peer_', '$start_peer_')
               .replace('INTRINSIC_FIBER_THROW', 'INTRINSIC_FIBER_START')
               .replace('$ptascii("throw")', '$ptascii("start")')
               for check in genuine]
    at = genuine.index('$call_current_valid(S_factory)')
    genuine[at:at] = lines(r'''
$fiber_factory_start(S_factory, pconfigcall_factory, PARRAY n_callback)
$lookup(S_factory.ENV, $ptascii("payload")) = (n_payload_cell)
S_factory.STORE[n_payload_cell] = DEFINED (POBJECT n_payload)
S_factory.OBJECTS[n_payload] = THROWABLE pthrowable_payload
pthrowable_payload.KIND = "Exception"
$throwable_field(S_factory, n_payload, "trace") = PARRAY n_payload_trace
S_factory.ARRAYS[n_payload_trace].ITEMS = eps
$node_children(S_factory, HOBJECT n_payload) = [HARRAY n_payload_trace]
$heap_owners($heap_graph(S_factory), HOBJECT n_payload) = 1
$heap_owners($heap_graph(S_factory), HARRAY n_payload_trace) = 1
pfiber_initial.RAW = POBJECT n_body
$node_children(S_factory, HOBJECT n_receiver) = [HOBJECT n_body]
$node_children(S_factory, HOBJECT n_body) = eps
$lookup(S_factory.ENV, $ptascii("weakPayload")) = (n_weak_payload_cell)
S_factory.STORE[n_weak_payload_cell] = DEFINED (POBJECT n_weak_payload)
$weakref_get(S_factory, n_weak_payload) = POBJECT n_payload
$node_children(S_factory, HOBJECT n_weak_payload) = eps
S_factory.FIBERSEQ = 1
S_factory.ACTIVEFIBER = eps
S_factory.FIBERCALLERS = eps
S_factory.FIBERCLOSERS = eps
''')
    genuine += seek('S_args', 'S_minted', 1) + lines(r'''
S_args.TODO = (FIBER_START_CAPTURE_ARGS n_capture pfiberstart) :: ptask_release*
ptask_release* = (FIBER_CAPTURE_RELEASE n_capture pfiberstart.SITE) :: ptask_after_call*
pfiberstart.OBJECT = n_receiver
pfiberstart.INDEX = 1
pfiberstart.SENT.SLOTS = eps
pfiberstart.SENT.NAMED = [($ptascii("value"), KNOWN (POBJECT n_payload))]
pfiberstart.PACKS = eps
$intrinsic_count(S_args, pfiberstart.SITE) = (1)
S_args.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture
$fiber_at(S_args, n_receiver) = (pfiber_initial)
S_args.STORE[n_payload_cell] = DEFINED PNULL
$lookup(S_args.ENV, $ptascii("selected")) = (n_selected_cell)
S_args.STORE[n_selected_cell] = DEFINED PNULL
$lookup(S_args.ENV, $ptascii("fiber")) = (n_fiber_cell)
S_args.STORE[n_fiber_cell] = DEFINED PNULL
S_args.STORE[n_callback_cell] = DEFINED PNULL
S_args.STORE[n_method_cell] = DEFINED pvalue_changed
$string_bytes(pvalue_changed) = ($ptascii("isStarted"))
~((HOBJECT n_factory) <- S_args.ALLOCATIONS)
~((HARRAY n_callback) <- S_args.ALLOCATIONS)
~((HARRAY n_original_callback) <- S_args.ALLOCATIONS)
$heap_owners($heap_graph(S_args), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_args), HOBJECT n_receiver) = 1
$heap_owners($heap_graph(S_args), HOBJECT n_body) = 1
$heap_owners($heap_graph(S_args), HOBJECT n_payload) = 1
$heap_owners($heap_graph(S_args), HARRAY n_payload_trace) = 1
$task_nodes(FIBER_START_CAPTURE_ARGS n_capture pfiberstart) = [HOBJECT n_payload]
$task_nodes(FIBER_CAPTURE_RELEASE n_capture pfiberstart.SITE) = [HOBJECT n_capture]
$lookup(S_args.ENV, $ptascii("weakSelected")) = (n_weak_capture_cell)
S_args.STORE[n_weak_capture_cell] = DEFINED (POBJECT n_weak_capture)
$weakref_get(S_args, n_weak_capture) = POBJECT n_capture
$lookup(S_args.ENV, $ptascii("weakFiber")) = (n_weak_receiver_cell)
S_args.STORE[n_weak_receiver_cell] = DEFINED (POBJECT n_weak_receiver)
$weakref_get(S_args, n_weak_receiver) = POBJECT n_receiver
$weakref_get(S_args, n_weak_payload) = POBJECT n_payload
$from_factory_saved(S_args, n_factory)
~$from_factory_live(S_args, n_factory)
$fiber_factory_saved_call(S_args, pconfigcall_factory, INTRINSIC_FIBER_START, (n_receiver))
$fiber_capture_source_valid(S_args, pfibercapture)
$fiber_start_capture_valid(S_args, n_capture, pfiberstart, false)
S_args.ACTIVEFIBER = eps
S_args.FIBERCALLERS = eps
S_args.FIBERSEQ = 1
S_args.DESTRUCTION.OPERATIONS = eps
S_args.DESTRUCTION.RELEASES = eps
$outputs(S_args.EVENTS) = $ptascii("Q;A;M:isStarted;F;H:held;V;")
S_enter_step = $drive_steps(S_args, 1)
S_enter_step.COMPLETION = BUDGET
S_enter = S_enter_step[.COMPLETION = NORMAL]
S_enter.TODO = (FIBER_START_CAPTURE_ARGS n_capture pfiberstart) :: (FIBER_START_CAPTURE_RESULT n_capture pfiberstart false) :: ptask_after_call*
$fiber_start_capture_result_valid(S_enter, n_capture, pfiberstart, false)
~$exit_method_site(S_enter, pfiberstart.SITE)
$task_nodes(FIBER_START_CAPTURE_RESULT n_capture pfiberstart false) = [HOBJECT n_capture]
$heap_owners($heap_graph(S_enter), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_enter), HOBJECT n_payload) = 1
S_switched_step = $drive_steps(S_enter, 1)
S_switched_step.COMPLETION = BUDGET
S_switched = S_switched_step[.COMPLETION = NORMAL]
S_switched.ACTIVEFIBER = (n_receiver)
S_switched.TODO = [FIBER_ENTER n_receiver pfiberstart.SENT, FIBER_FINISH n_receiver]
S_switched.FIBERCALLERS = [pfibercaller]
pfibercaller.OBJECT = n_receiver
pfibercaller.PREVIOUS = eps
pfibercaller.API = pfiberapi
pfibercaller.VM = pfibervm_caller
pfibervm_caller.TODO = (FIBER_WAIT pfiberapi) :: (FIBER_START_CAPTURE_RESULT n_capture pfiberstart false) :: ptask_after_call*
pfibervm_caller.CURRENT = S_enter.CURRENT
pfibervm_caller.FRAMES = S_enter.FRAMES
pfiberapi = {SITE pfiberstart.SITE, OBJECT n_receiver, KIND eps, START (pfiberstart.SENT), SENT eps, LINE pfiberstart.LINE, SEQUENCE 1, PACKS eps}
$fiber_at(S_switched, n_receiver) = (pfiber_running)
pfiber_running.STATUS = FIBER_RUNNING
pfiber_running.ENTRY = (pfiberstart.SENT)
pfiber_running.SEQUENCE = 1
pfiber_running.VM = eps
S_switched.FIBERSEQ = 2
$fiber_caller_api_nodes(pfibercaller) = [HOBJECT n_payload]
$task_nodes(FIBER_ENTER n_receiver pfiberstart.SENT) = eps
$task_nodes(FIBER_WAIT pfiberapi) = eps
$heap_owners($heap_graph(S_switched), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_switched), HOBJECT n_receiver) = 1
$heap_owners($heap_graph(S_switched), HOBJECT n_payload) = 1
$heap_owners($heap_graph(S_switched), HARRAY n_payload_trace) = 1
$outputs(S_switched.EVENTS) = $outputs(S_args.EVENTS)
''') + guards('S_args') + guards('S_enter') + guards('S_switched')
    genuine += seek('S_local_before', 'S_switched', 2) + lines(r'''
S_local_before.TODO = (WRITE_NAME $ptascii("value") z_value) :: ptask_local_tail*
S_local_before.CURRENT = (pcallcontext_body)
pcallcontext_body.TARGET = CLOSURE_TARGET n_body
$fiber_context_valid(S_local_before, pcallcontext_body)
$lookup(S_local_before.ENV, $ptascii("value")) = (n_value_cell)
S_local_before.STORE[n_value_cell] = DEFINED (POBJECT n_payload)
S_local_before.FIBERCALLERS = [pfibercaller]
$fiber_caller_api_nodes(pfibercaller) = [HOBJECT n_payload]
$heap_owners($heap_graph(S_local_before), HOBJECT n_payload) = 2
$heap_owners($heap_graph(S_local_before), HARRAY n_payload_trace) = 1
$outputs(S_local_before.EVENTS) = $ptascii("Q;A;M:isStarted;F;H:held;V;B;I:same;P:held;")
S_local_step = $drive_steps(S_local_before, 1)
S_local_step.COMPLETION = BUDGET
S_local = S_local_step[.COMPLETION = NORMAL]
S_local.STORE[n_value_cell] = DEFINED PNULL
S_local.DESTRUCTION.OPERATIONS = pdestructionoperation_local :: pdestructionoperation_local_tail*
pdestructionoperation_local_tail* = eps
pdestructionoperation_local.SOURCE = $eager_operation_source(S_local_before, WRITE_NAME $ptascii("value") z_value)
pdestructionoperation_local.VALUE = KNOWN PNULL
pdestructionoperation_local.PENDING = eps
$destructor_operation_live(S_local, pdestructionoperation_local)
''') + guards('S_local_before') + guards('S_local')
    genuine += seek('S_local_done', 'S_local', 3) + lines(r'''
S_local_done.TODO = ptask_local_tail*
S_local_done.ACTIVEFIBER = (n_receiver)
S_local_done.CURRENT = (pcallcontext_body)
S_local_done.STORE[n_value_cell] = DEFINED PNULL
S_local_done.FIBERCALLERS = [pfibercaller]
$fiber_caller_api_nodes(pfibercaller) = [HOBJECT n_payload]
$heap_owners($heap_graph(S_local_done), HOBJECT n_payload) = 1
$heap_owners($heap_graph(S_local_done), HARRAY n_payload_trace) = 1
$weakref_get(S_local_done, n_weak_payload) = POBJECT n_payload
$throwable_live(S_local_done, n_payload)
$outputs(S_local_done.EVENTS) = $outputs(S_local_before.EVENTS)
''') + guards('S_local_done')
    genuine += seek('S_body_done', 'S_local_done', 4) + lines(r'''
S_body_done.TODO = [FIBER_FINISH n_receiver]
S_body_done.RESULT = KNOWN (PINT 7)
S_body_done.FIBERCALLERS = [pfibercaller]
$fiber_caller_api_nodes(pfibercaller) = [HOBJECT n_payload]
$heap_owners($heap_graph(S_body_done), HOBJECT n_payload) = 1
$heap_owners($heap_graph(S_body_done), HARRAY n_payload_trace) = 1
$heap_owners($heap_graph(S_body_done), HOBJECT n_body) = 1
$fiber_ordinary_cleanup(S_body_done, n_receiver)
$outputs(S_body_done.EVENTS) = $ptascii("Q;A;M:isStarted;F;H:held;V;B;I:same;P:held;L:held;")
''') + guards('S_body_done')
    genuine += seek('S_finish', 'S_body_done', 5) + lines(r'''
S_finish.TODO = [FIBER_RETURN_FINISH pfiberfinish]
pfiberfinish.OBJECT = n_receiver
pfiberfinish.PENDING = eps
pfiberfinish.SEQUENCE = 1
$fiber_at(S_finish, n_receiver) = (pfiber_finishing)
pfiber_finishing.STATUS = FIBER_RUNNING
pfiber_finishing.VALUE = PINT 7
pfiber_finishing.RETURNED
pfiber_finishing.RAW = PNULL
pfiber_finishing.CALL = eps
pfiber_finishing.TARGET = eps
pfiber_finishing.FINISH = (pfiberfinish)
S_finish.FIBERCALLERS = [pfibercaller]
S_finish.DESTRUCTION.OPERATIONS = eps
S_finish.DESTRUCTION.RELEASES = eps
~((HOBJECT n_body) <- S_finish.ALLOCATIONS)
$heap_owners($heap_graph(S_finish), HOBJECT n_body) = 0
$heap_owners($heap_graph(S_finish), HOBJECT n_payload) = 1
$heap_owners($heap_graph(S_finish), HARRAY n_payload_trace) = 1
$fiber_ordinary_finish_live(S_finish, pfiberfinish)
$call_task_valid(S_finish, FIBER_RETURN_FINISH pfiberfinish)
$outputs(S_finish.EVENTS) = $outputs(S_body_done.EVENTS)
S_raw_back = $fiber_ordinary_finish(S_finish, pfiberfinish)
S_raw_back.COMPLETION = NORMAL
S_raw_back.ACTIVEFIBER = eps
S_raw_back.FIBERCALLERS = eps
S_raw_back.TODO = (FIBER_START_CAPTURE_RESULT n_capture pfiberstart false) :: ptask_after_call*
S_raw_back.RESULT = KNOWN PNULL
S_raw_back.ALLOCATIONS = S_finish.ALLOCATIONS
$heap_owners($heap_graph(S_raw_back), HOBJECT n_payload) = 0
$task_nodes(FIBER_START_CAPTURE_RESULT n_capture pfiberstart false) = [HOBJECT n_capture]
S_back_step = $drive_steps(S_finish, 1)
S_back_step.COMPLETION = BUDGET
S_back = S_back_step[.COMPLETION = NORMAL]
S_back.ACTIVEFIBER = eps
S_back.FIBERCALLERS = eps
S_back.DESTRUCTION.OPERATIONS = pdestructionoperation_buffer :: pdestructionoperation_buffer_tail*
pdestructionoperation_buffer_tail* = eps
pdestructionoperation_buffer.SOURCE = FIBER_RETURN_FINISH pfiberfinish
pdestructionoperation_buffer.VALUE = KNOWN PNULL
pdestructionoperation_buffer.PENDING = eps
$destructor_operation_live(S_back, pdestructionoperation_buffer)
$outputs(S_back.EVENTS) = $outputs(S_finish.EVENTS)
''') + guards('S_finish') + guards('S_back')
    genuine += seek('S_marker', 'S_back', 6) + lines(r'''
S_marker.TODO = (FIBER_START_CAPTURE_RESULT n_capture pfiberstart false) :: ptask_after_call*
S_marker.RESULT = KNOWN PNULL
S_marker.ACTIVEFIBER = eps
S_marker.FIBERCALLERS = eps
$fiber_at(S_marker, n_receiver) = (pfiber_returned)
pfiber_returned.STATUS = FIBER_TERMINATED
pfiber_returned.VALUE = PINT 7
pfiber_returned.RETURNED
pfiber_returned.FINISH = eps
pfiber_returned.ENTRY = eps
$fiber_start_capture_result_valid(S_marker, n_capture, pfiberstart, false)
~((HOBJECT n_payload) <- S_marker.ALLOCATIONS)
~((HARRAY n_payload_trace) <- S_marker.ALLOCATIONS)
$heap_owners($heap_graph(S_marker), HOBJECT n_payload) = 0
$heap_owners($heap_graph(S_marker), HARRAY n_payload_trace) = 0
$heap_owners($heap_graph(S_marker), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_marker), HOBJECT n_receiver) = 1
$weakref_get(S_marker, n_weak_payload) = PNULL
$weakref_get(S_marker, n_weak_capture) = POBJECT n_capture
$weakref_get(S_marker, n_weak_receiver) = POBJECT n_receiver
$outputs(S_marker.EVENTS) = $outputs(S_finish.EVENTS)
S_release_step = $drive_steps(S_marker, 1)
S_release_step.COMPLETION = BUDGET
S_release = S_release_step[.COMPLETION = NORMAL]
S_release.DESTRUCTION.OPERATIONS = pdestructionoperation_marker :: pdestructionoperation_marker_tail*
pdestructionoperation_marker_tail* = eps
pdestructionoperation_marker.SOURCE = FIBER_START_CAPTURE_RESULT n_capture pfiberstart false
pdestructionoperation_marker.VALUE = KNOWN PNULL
pdestructionoperation_marker.PENDING = eps
$destructor_operation_live(S_release, pdestructionoperation_marker)
$outputs(S_release.EVENTS) = $outputs(S_marker.EVENTS)
''') + guards('S_marker') + guards('S_release')
    genuine += seek('S_pruned', 'S_release', 7) + lines(r'''
S_pruned.TODO = ptask_after_call*
S_pruned.RESULT = KNOWN PNULL
S_pruned.STORE[n_selected_cell] = DEFINED PNULL
S_pruned.STORE[n_payload_cell] = DEFINED PNULL
~((HOBJECT n_capture) <- S_pruned.ALLOCATIONS)
~((HOBJECT n_receiver) <- S_pruned.ALLOCATIONS)
~((HOBJECT n_body) <- S_pruned.ALLOCATIONS)
~((HOBJECT n_payload) <- S_pruned.ALLOCATIONS)
~((HARRAY n_payload_trace) <- S_pruned.ALLOCATIONS)
$heap_owners($heap_graph(S_pruned), HOBJECT n_capture) = 0
$heap_owners($heap_graph(S_pruned), HOBJECT n_receiver) = 0
$heap_owners($heap_graph(S_pruned), HOBJECT n_payload) = 0
$heap_owners($heap_graph(S_pruned), HARRAY n_payload_trace) = 0
$weakref_get(S_pruned, n_weak_capture) = PNULL
$weakref_get(S_pruned, n_weak_receiver) = PNULL
$weakref_get(S_pruned, n_weak_payload) = PNULL
~$fiber_capture_source_valid(S_pruned, pfibercapture)
$from_factory_saved(S_pruned, n_factory)
$fiber_factory_saved_call(S_pruned, pconfigcall_factory, INTRINSIC_FIBER_START, (n_receiver))
S_pruned.FIBERSEQ = 2
S_pruned.FIBERCALLERS = eps
S_pruned.FIBERCLOSERS = eps
$outputs(S_pruned.EVENTS) = $outputs(S_finish.EVENTS)
S_zero = $drive_steps(S_args, 0)
S_zero = S_args[.COMPLETION = BUDGET]
S_done = $drive(S_zero[.COMPLETION = NORMAL], 1000)
S_done = $drive(S_args, 1000)
S_done = $drive(S_pruned, 1000)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
$lookup(S_done.ENV, $ptascii("returned")) = (n_returned_cell)
S_done.STORE[n_returned_cell] = DEFINED PNULL
''') + [f'$outputs(S_done.EVENTS) = $ptascii("{expected}")'] + guards('S_pruned') + guards('S_done')
    controls = []
    for label, changed in [
        ('input', 'pfibercapture[.INPUT = eps]'),
        ('kind', 'pfibercapture[.KIND = INTRINSIC_FIBER_STARTED]'),
        ('name', 'pfibercapture[.NAME = $ptascii("isStarted")]'),
        ('line', 'pfibercapture[.FACTORY = (pfiberfactory[.CALL = pconfigcall_factory[.LINE = $(pconfigcall_factory.LINE + 1)]])]'),
        ('owner', 'pfibercapture[.FACTORY = (pfiberfactory[.CALL = pconfigcall_factory[.OWNER = (n_receiver)]])]'),
        ('site', 'pfibercapture[.FACTORY = (pfiberfactory[.CALL = pconfigcall_factory[.SITE = porigin_create]])]'),
    ]:
        controls += [f'pfibercapture_{label} = {changed}',
                     f'~$fiber_capture_source_valid(S_args, pfibercapture_{label})',
                     f'S_bad_{label} = S_args[.OBJECTS = $object_set(S_args.OBJECTS, n_capture, FIBERAPICLOSURE pfibercapture_{label})]',
                     f'~$fiber_capture_live(S_bad_{label}, n_capture)',
                     f'~$call_descriptors_valid(S_bad_{label})']
    controls += lines(r'''
pentry_alias* = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), ENTRY (KINT 1) (ALIAS n_method_cell)]
~$config_pack_items_valid(pentry_alias*)
pfibercapture_alias = pfibercapture[.FACTORY = (pfiberfactory[.ITEMS = pentry_alias*])]
~$fiber_capture_source_valid(S_args, pfibercapture_alias)
pfibercapture_receiver = pfibercapture[.INPUT = (n_capture)]
~$fiber_capture_source_valid(S_args, pfibercapture_receiver)
pvalue_static = PSTRING $ptascii("Fiber::start")
pconfigcall_static = pconfigcall_factory[.SENT = [NAMED_SENT (KNOWN pvalue_static)]]
S_static = S_factory[.TODO = (CONFIG_INVOKE pconfigcall_static) :: ptask_factory*]
$config_invoke_valid(S_static, pconfigcall_static)
$fiber_factory_candidate(S_static, pvalue_static)
$fiber_factory_selection(S_static, pvalue_static, eps) = eps
~$fiber_factory_start(S_static, pconfigcall_static, pvalue_static)
pnamedargs_other = pfiberstart.SENT[.NAMED = [($ptascii("value"), KNOWN (POBJECT n_weak_payload))]]
$fiber_start_shape(S_args, pfiberstart.SITE, 1, pnamedargs_other, eps)
pnamedargs_other =/= pfiberstart.SENT
pfiberstart_reference = pfiberstart[.SENT.NAMED = [($ptascii("value"), REFERENCE n_payload_cell)]]
~$fiber_start_capture_valid(S_args, n_capture, pfiberstart_reference, false)
pfiberstart_wrong_object = pfiberstart[.OBJECT = n_capture]
~$fiber_start_capture_result_valid(S_marker, n_capture, pfiberstart_wrong_object, false)
pfiberstart_wrong_line = pfiberstart[.LINE = $(pfiberstart.LINE + 1)]
~$fiber_start_capture_result_valid(S_marker, n_capture, pfiberstart_wrong_line, false)
pfiberstart_wrong_name = pfiberstart[.SENT.NAMED = [($ptascii("other"), KNOWN (POBJECT n_payload))]]
~$fiber_start_capture_result_valid(S_marker, n_capture, pfiberstart_wrong_name, false)
~$fiber_start_capture_result_valid(S_marker, n_capture, pfiberstart, true)
S_duplicate = S_marker[.TODO = (FIBER_START_CAPTURE_RESULT n_capture pfiberstart false) :: S_marker.TODO]
~$fiber_start_capture_result_valid(S_duplicate, n_capture, pfiberstart, false)
''')
    checks = genuine + controls
    text = EXTRA + PREFIX.replace('STAGE', '$start_peer_stage(S, 0)')
    text += '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks, len(genuine), len(controls)
