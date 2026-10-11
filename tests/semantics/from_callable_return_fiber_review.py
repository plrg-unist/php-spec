"""Reached defined object getReturn, result marker and separate result retirement."""
from error_handler_protocol import PREFIX
from from_callable_throw_fiber_review import guards, lines, render as throw_render


EXTRA = r'''
dec $return_peer_stage(pstate, nat) : bool
def $return_peer_stage(S, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_FROM_CALLABLE_FACTORY
def $return_peer_stage(S, 1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_FIBER_RETURN
  -- if pconfigcall.SELECTION =/= eps
def $return_peer_stage(S, 2) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
  -- if pdestructionoperation.SOURCE = FIBER_CAPTURE_RESULT n pconfigcall false
  -- if pconfigcall.KIND = INTRINSIC_FIBER_RETURN
def $return_peer_stage(S, 3) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("selected")
  -- if S.RESULT = KNOWN PNULL
def $return_peer_stage(S, 4) = true
  -- if $lookup(S.ENV, $ptascii("selected")) = (n_selected)
  -- if S.STORE[n_selected] = DEFINED PNULL
  -- if $lookup(S.ENV, $ptascii("returned")) = (n_returned)
  -- if S.STORE[n_returned] = DEFINED (POBJECT n_payload)
  -- if $lookup(S.ENV, $ptascii("weakFiber")) = (n_weak_cell)
  -- if S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
  -- if $weakref_get(S, n_weak) = PNULL
  -- if S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.RELEASES = eps
  -- if S.TODO =/= eps
def $return_peer_stage(S, 5) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("returned")
  -- if S.RESULT = KNOWN PNULL
def $return_peer_stage(S, 6) = true
  -- if $lookup(S.ENV, $ptascii("selected")) = (n_selected)
  -- if S.STORE[n_selected] = DEFINED PNULL
  -- if $lookup(S.ENV, $ptascii("returned")) = (n_returned)
  -- if S.STORE[n_returned] = DEFINED PNULL
  -- if S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.RELEASES = eps
  -- if S.TODO =/= eps
def $return_peer_stage(S, n) = false -- otherwise
dec $return_peer_seek(pstate, nat, nat) : pstate
def $return_peer_seek(S, n_phase, n) = S
  -- if $return_peer_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $return_peer_seek(S, n_phase, n) = $return_peer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if ~$return_peer_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $return_peer_seek(S, n_phase, 0) = S
  -- if ~$return_peer_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $return_peer_seek(S, n_phase, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''


def seek(state, previous, phase):
    return [f'{state}_reached = $return_peer_seek({previous}, {phase}, 1000)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$return_peer_stage({state}, {phase})']


def render(program, filename, expected):
    _, prior, _, _ = throw_render(program, filename, expected)
    cut = next(i for i, check in enumerate(prior) if check.startswith('S_invoke_reached ='))
    genuine = prior[:cut]
    begin = genuine.index('$lookup(S_factory.ENV, $ptascii("exception")) = (n_exception_cell)')
    end = genuine.index('$call_current_valid(S_factory)', begin)
    del genuine[begin:end]
    genuine = [check.replace('$throw_peer_', '$return_peer_')
               .replace('INTRINSIC_FIBER_THROW', 'INTRINSIC_FIBER_RETURN')
               .replace('$ptascii("throw")', '$ptascii("getReturn")')
               .replace('pfiber_initial', 'pfiber_returned')
               .replace('pfiber_returned.STATUS = FIBER_INIT', 'pfiber_returned.STATUS = FIBER_TERMINATED')
               for check in genuine]
    at = genuine.index('$call_current_valid(S_factory)')
    genuine[at:at] = lines(r'''
$fiber_factory_return(S_factory, pconfigcall_factory, PARRAY n_callback)
$lookup(S_factory.ENV, $ptascii("payload")) = (n_payload_cell)
S_factory.STORE[n_payload_cell] = DEFINED PNULL
pfiber_returned.VALUE = POBJECT n_payload
pfiber_returned.RETURNED
~pfiber_returned.FAILED
~pfiber_returned.GRACEFUL
pfiber_returned.READY
pfiber_returned.RAW = PNULL
pfiber_returned.CALL = eps
pfiber_returned.TARGET = eps
pfiber_returned.VM = eps
pfiber_returned.FINISH = eps
pfiber_returned.SEQUENCE = 1
S_factory.FIBERSEQ = 2
S_factory.ACTIVEFIBER = eps
S_factory.FIBERCALLERS = eps
S_factory.FIBERCLOSERS = eps
S_factory.CURRENT = eps
S_factory.FRAMES = eps
$destructor_operational(S_factory)
S_factory.OBJECTS[n_payload] = THROWABLE pthrowable_payload
pthrowable_payload.KIND = "Exception"
$throwable_field(S_factory, n_payload, "trace") = PARRAY n_payload_trace
S_factory.ARRAYS[n_payload_trace].ITEMS = eps
$node_children(S_factory, HOBJECT n_receiver) = [HOBJECT n_payload]
$node_children(S_factory, HOBJECT n_payload) = [HARRAY n_payload_trace]
$heap_owners($heap_graph(S_factory), HOBJECT n_payload) = 1
$heap_owners($heap_graph(S_factory), HARRAY n_payload_trace) = 1
$lookup(S_factory.ENV, $ptascii("weakPayload")) = (n_weak_payload_cell)
S_factory.STORE[n_weak_payload_cell] = DEFINED (POBJECT n_weak_payload)
$weakref_get(S_factory, n_weak_payload) = POBJECT n_payload
$node_children(S_factory, HOBJECT n_weak_payload) = eps
$throwable_live(S_factory, n_payload)
''')
    genuine += seek('S_invoke', 'S_minted', 1) + lines(r'''
S_invoke.TODO = (CONFIG_INVOKE pconfigcall_return) :: ptask_release*
ptask_release* = (FIBER_CAPTURE_RELEASE n_capture pconfigcall_return.SITE) :: ptask_after_call*
pconfigcall_return.KIND = INTRINSIC_FIBER_RETURN
pconfigcall_return.OWNER = (n_receiver)
pconfigcall_return.SELECTION = (n_capture)
pconfigcall_return.SENT = eps
S_invoke.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture
$fiber_at(S_invoke, n_receiver) = (pfiber_returned)
S_invoke.STORE[n_payload_cell] = DEFINED PNULL
$lookup(S_invoke.ENV, $ptascii("selected")) = (n_selected_cell)
S_invoke.STORE[n_selected_cell] = DEFINED (POBJECT n_capture)
$lookup(S_invoke.ENV, $ptascii("fiber")) = (n_fiber_cell)
S_invoke.STORE[n_fiber_cell] = DEFINED PNULL
S_invoke.STORE[n_callback_cell] = DEFINED PNULL
S_invoke.STORE[n_method_cell] = DEFINED pvalue_changed
$string_bytes(pvalue_changed) = ($ptascii("isTerminated"))
~((HOBJECT n_factory) <- S_invoke.ALLOCATIONS)
~((HARRAY n_callback) <- S_invoke.ALLOCATIONS)
~((HARRAY n_original_callback) <- S_invoke.ALLOCATIONS)
$heap_owners($heap_graph(S_invoke), HOBJECT n_factory) = 0
$heap_owners($heap_graph(S_invoke), HARRAY n_callback) = 0
$heap_owners($heap_graph(S_invoke), HOBJECT n_capture) = 2
$heap_owners($heap_graph(S_invoke), HOBJECT n_receiver) = 1
$heap_owners($heap_graph(S_invoke), HOBJECT n_payload) = 1
$heap_owners($heap_graph(S_invoke), HARRAY n_payload_trace) = 1
$node_children(S_invoke, HOBJECT n_capture) = [HOBJECT n_receiver]
$node_children(S_invoke, HOBJECT n_receiver) = [HOBJECT n_payload]
$config_nodes(pconfigcall_return) = eps
$task_nodes(FIBER_CAPTURE_RELEASE n_capture pconfigcall_return.SITE) = [HOBJECT n_capture]
$lookup(S_invoke.ENV, $ptascii("weakSelected")) = (n_weak_capture_cell)
S_invoke.STORE[n_weak_capture_cell] = DEFINED (POBJECT n_weak_capture)
$weakref_get(S_invoke, n_weak_capture) = POBJECT n_capture
$lookup(S_invoke.ENV, $ptascii("weakFiber")) = (n_weak_receiver_cell)
S_invoke.STORE[n_weak_receiver_cell] = DEFINED (POBJECT n_weak_receiver)
$weakref_get(S_invoke, n_weak_receiver) = POBJECT n_receiver
$weakref_get(S_invoke, n_weak_payload) = POBJECT n_payload
$from_factory_saved(S_invoke, n_factory)
~$from_factory_live(S_invoke, n_factory)
$fiber_factory_saved_call(S_invoke, pconfigcall_factory, INTRINSIC_FIBER_RETURN, (n_receiver))
$fiber_capture_source_valid(S_invoke, pfibercapture)
$fiber_capture_config_selected(S_invoke, pconfigcall_return)
$config_invoke_valid(S_invoke, pconfigcall_return)
S_invoke.DESTRUCTION.OPERATIONS = eps
S_invoke.DESTRUCTION.RELEASES = eps
$outputs(S_invoke.EVENTS) = $ptascii("Q;B;P:held;A;M:isTerminated;F;H:held;")
S_received = $config_receive(S_invoke, pconfigcall_return)
S_received.COMPLETION = NORMAL
S_received.RESULT = KNOWN (POBJECT n_payload)
S_received.TODO = (FIBER_CAPTURE_RESULT n_capture pconfigcall_return false) :: ptask_after_call*
$fiber_at(S_received, n_receiver) = (pfiber_returned)
$heap_owners($heap_graph(S_received), HOBJECT n_capture) = 2
$heap_owners($heap_graph(S_received), HOBJECT n_payload) = 2
S_value_step = $drive_steps(S_invoke, 1)
S_value_step.COMPLETION = BUDGET
S_value = S_value_step[.COMPLETION = NORMAL]
S_value.RESULT = KNOWN (POBJECT n_payload)
S_value.TODO = (FIBER_CAPTURE_RESULT n_capture pconfigcall_return false) :: ptask_after_call*
S_value.OBJECTS = S_received.OBJECTS
S_value.ARRAYS = S_received.ARRAYS
S_value.OBJECTPROPS = S_received.OBJECTPROPS
S_value.ALLOCATIONS = S_received.ALLOCATIONS
$fiber_capture_result_valid(S_value, n_capture, pconfigcall_return, false)
~$exit_method_site(S_value, pconfigcall_return.SITE)
$task_nodes(FIBER_CAPTURE_RESULT n_capture pconfigcall_return false) = [HOBJECT n_capture]
$heap_owners($heap_graph(S_value), HOBJECT n_capture) = 2
$heap_owners($heap_graph(S_value), HOBJECT n_receiver) = 1
$heap_owners($heap_graph(S_value), HOBJECT n_payload) = 2
$heap_owners($heap_graph(S_value), HARRAY n_payload_trace) = 1
$outputs(S_value.EVENTS) = $outputs(S_invoke.EVENTS)
S_marker_step = $drive_steps(S_value, 1)
S_marker_step.COMPLETION = BUDGET
S_marker = S_marker_step[.COMPLETION = NORMAL]
S_marker.DESTRUCTION.OPERATIONS = pdestructionoperation_marker :: pdestructionoperation_marker_tail*
pdestructionoperation_marker_tail* = eps
pdestructionoperation_marker.SOURCE = FIBER_CAPTURE_RESULT n_capture pconfigcall_return false
pdestructionoperation_marker.VALUE = KNOWN (POBJECT n_payload)
pdestructionoperation_marker.PENDING = eps
pdestructionoperation_marker.COMPLETION = NORMAL
S_marker.RESULT = KNOWN PNULL
$destructor_operation_live(S_marker, pdestructionoperation_marker)
$fiber_at(S_marker, n_receiver) = (pfiber_returned)
$heap_owners($heap_graph(S_marker), HOBJECT n_payload) = 2
$outputs(S_marker.EVENTS) = $outputs(S_invoke.EVENTS)
''') + guards('S_invoke') + guards('S_value') + guards('S_marker')
    genuine += seek('S_marker_exit', 'S_marker', 2) + lines(r'''
S_marker_exit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_marker) :: ptask_after_call*
S_marker_exit.DESTRUCTION.RELEASES = eps
$destructor_operation_valid(S_marker_exit, pdestructionoperation_marker)
$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_marker) = [HOBJECT n_payload]
$heap_owners($heap_graph(S_marker_exit), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_marker_exit), HOBJECT n_receiver) = 1
$heap_owners($heap_graph(S_marker_exit), HOBJECT n_payload) = 2
S_marker_done_step = $drive_steps(S_marker_exit, 1)
S_marker_done_step.COMPLETION = BUDGET
S_marker_done = S_marker_done_step[.COMPLETION = NORMAL]
S_marker_done.TODO = ptask_after_call*
S_marker_done.RESULT = KNOWN (POBJECT n_payload)
S_marker_done.DESTRUCTION.OPERATIONS = eps
S_marker_done.DESTRUCTION.RELEASES = eps
$heap_owners($heap_graph(S_marker_done), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_marker_done), HOBJECT n_payload) = 2
$weakref_get(S_marker_done, n_weak_capture) = POBJECT n_capture
$weakref_get(S_marker_done, n_weak_receiver) = POBJECT n_receiver
$weakref_get(S_marker_done, n_weak_payload) = POBJECT n_payload
$outputs(S_marker_done.EVENTS) = $outputs(S_invoke.EVENTS)
''') + guards('S_marker_exit') + guards('S_marker_done')
    genuine += seek('S_selected_before', 'S_marker_done', 3) + lines(r'''
S_selected_before.TODO = (WRITE_NAME $ptascii("selected") z_selected) :: ptask_selected_tail*
S_selected_before.RESULT = KNOWN PNULL
S_selected_before.STORE[n_selected_cell] = DEFINED (POBJECT n_capture)
$lookup(S_selected_before.ENV, $ptascii("returned")) = (n_returned_cell)
S_selected_before.STORE[n_returned_cell] = DEFINED (POBJECT n_payload)
$fiber_at(S_selected_before, n_receiver) = (pfiber_returned)
$heap_owners($heap_graph(S_selected_before), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_selected_before), HOBJECT n_payload) = 2
S_selected_step = $drive_steps(S_selected_before, 1)
S_selected_step.COMPLETION = BUDGET
S_selected = S_selected_step[.COMPLETION = NORMAL]
S_selected.STORE[n_selected_cell] = DEFINED PNULL
S_selected.DESTRUCTION.OPERATIONS = pdestructionoperation_selected :: pdestructionoperation_selected_tail*
pdestructionoperation_selected_tail* = eps
pdestructionoperation_selected.SOURCE = $eager_operation_source(S_selected_before, WRITE_NAME $ptascii("selected") z_selected)
pdestructionoperation_selected.VALUE = KNOWN PNULL
pdestructionoperation_selected.PENDING = eps
$destructor_operation_live(S_selected, pdestructionoperation_selected)
''') + guards('S_selected_before') + guards('S_selected')
    genuine += seek('S_selected_clear', 'S_selected', 4) + lines(r'''
S_selected_clear.STORE[n_selected_cell] = DEFINED PNULL
S_selected_clear.STORE[n_returned_cell] = DEFINED (POBJECT n_payload)
~((HOBJECT n_capture) <- S_selected_clear.ALLOCATIONS)
~((HOBJECT n_receiver) <- S_selected_clear.ALLOCATIONS)
$heap_owners($heap_graph(S_selected_clear), HOBJECT n_capture) = 0
$heap_owners($heap_graph(S_selected_clear), HOBJECT n_receiver) = 0
$heap_owners($heap_graph(S_selected_clear), HOBJECT n_payload) = 1
$heap_owners($heap_graph(S_selected_clear), HARRAY n_payload_trace) = 1
$weakref_get(S_selected_clear, n_weak_capture) = PNULL
$weakref_get(S_selected_clear, n_weak_receiver) = PNULL
$weakref_get(S_selected_clear, n_weak_payload) = POBJECT n_payload
$throwable_live(S_selected_clear, n_payload)
~$fiber_capture_source_valid(S_selected_clear, pfibercapture)
$from_factory_saved(S_selected_clear, n_factory)
$fiber_factory_saved_call(S_selected_clear, pconfigcall_factory, INTRINSIC_FIBER_RETURN, (n_receiver))
$outputs(S_selected_clear.EVENTS) = $ptascii("Q;B;P:held;A;M:isTerminated;F;H:held;I:same;C:held;")
''') + guards('S_selected_clear')
    genuine += seek('S_returned_before', 'S_selected_clear', 5) + lines(r'''
S_returned_before.TODO = (WRITE_NAME $ptascii("returned") z_returned) :: ptask_returned_tail*
S_returned_before.RESULT = KNOWN PNULL
S_returned_before.STORE[n_returned_cell] = DEFINED (POBJECT n_payload)
$heap_owners($heap_graph(S_returned_before), HOBJECT n_payload) = 1
S_returned_step = $drive_steps(S_returned_before, 1)
S_returned_step.COMPLETION = BUDGET
S_returned = S_returned_step[.COMPLETION = NORMAL]
S_returned.STORE[n_returned_cell] = DEFINED PNULL
S_returned.DESTRUCTION.OPERATIONS = pdestructionoperation_returned :: pdestructionoperation_returned_tail*
pdestructionoperation_returned_tail* = eps
pdestructionoperation_returned.SOURCE = $eager_operation_source(S_returned_before, WRITE_NAME $ptascii("returned") z_returned)
pdestructionoperation_returned.VALUE = KNOWN PNULL
pdestructionoperation_returned.PENDING = eps
$destructor_operation_live(S_returned, pdestructionoperation_returned)
''') + guards('S_returned_before') + guards('S_returned')
    genuine += seek('S_pruned', 'S_returned', 6) + lines(r'''
S_pruned.STORE[n_returned_cell] = DEFINED PNULL
S_pruned.STORE[n_selected_cell] = DEFINED PNULL
~((HOBJECT n_payload) <- S_pruned.ALLOCATIONS)
~((HARRAY n_payload_trace) <- S_pruned.ALLOCATIONS)
$heap_owners($heap_graph(S_pruned), HOBJECT n_payload) = 0
$heap_owners($heap_graph(S_pruned), HARRAY n_payload_trace) = 0
$weakref_get(S_pruned, n_weak_payload) = PNULL
$weakref_get(S_pruned, n_weak_capture) = PNULL
$weakref_get(S_pruned, n_weak_receiver) = PNULL
~$throwable_live(S_pruned, n_payload)
S_pruned.ACTIVEFIBER = eps
S_pruned.FIBERCALLERS = eps
S_pruned.FIBERCLOSERS = eps
S_pruned.CURRENT = eps
S_pruned.FRAMES = eps
S_pruned.FIBERSEQ = 2
$outputs(S_pruned.EVENTS) = $ptascii("Q;B;P:held;A;M:isTerminated;F;H:held;I:same;C:held;C:gone;H:gone;P:held;")
S_zero = $drive_steps(S_invoke, 0)
S_zero = S_invoke[.COMPLETION = BUDGET]
S_done = $drive(S_zero[.COMPLETION = NORMAL], 1000)
S_done = $drive(S_invoke, 1000)
S_done = $drive(S_pruned, 1000)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
''') + [f'$outputs(S_done.EVENTS) = $ptascii("{expected}")'] + guards('S_pruned') + guards('S_done')
    controls = []
    for label, changed in [
        ('input', 'pfibercapture[.INPUT = eps]'),
        ('kind', 'pfibercapture[.KIND = INTRINSIC_FIBER_TERMINATED]'),
        ('name', 'pfibercapture[.NAME = $ptascii("isTerminated")]'),
        ('line', 'pfibercapture[.FACTORY = (pfiberfactory[.CALL = pconfigcall_factory[.LINE = $(pconfigcall_factory.LINE + 1)]])]'),
        ('owner', 'pfibercapture[.FACTORY = (pfiberfactory[.CALL = pconfigcall_factory[.OWNER = (n_receiver)]])]'),
        ('site', 'pfibercapture[.FACTORY = (pfiberfactory[.CALL = pconfigcall_factory[.SITE = porigin_create]])]'),
    ]:
        controls += [f'pfibercapture_{label} = {changed}',
                     f'~$fiber_capture_source_valid(S_invoke, pfibercapture_{label})',
                     f'S_bad_{label} = S_invoke[.OBJECTS = $object_set(S_invoke.OBJECTS, n_capture, FIBERAPICLOSURE pfibercapture_{label})]',
                     f'~$fiber_capture_live(S_bad_{label}, n_capture)',
                     f'~$call_descriptors_valid(S_bad_{label})']
    controls += lines(r'''
pentry_alias* = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), ENTRY (KINT 1) (ALIAS n_method_cell)]
~$config_pack_items_valid(pentry_alias*)
pfibercapture_alias = pfibercapture[.FACTORY = (pfiberfactory[.ITEMS = pentry_alias*])]
~$fiber_capture_source_valid(S_invoke, pfibercapture_alias)
pfibercapture_receiver = pfibercapture[.INPUT = (n_capture)]
~$fiber_capture_source_valid(S_invoke, pfibercapture_receiver)
pvalue_static = PSTRING $ptascii("Fiber::getReturn")
pconfigcall_static = pconfigcall_factory[.SENT = [NAMED_SENT (KNOWN pvalue_static)]]
S_static = S_factory[.TODO = (CONFIG_INVOKE pconfigcall_static) :: ptask_factory*]
$config_invoke_valid(S_static, pconfigcall_static)
$fiber_factory_candidate(S_static, pvalue_static)
$fiber_factory_selection(S_static, pvalue_static, eps) = eps
~$fiber_factory_return(S_static, pconfigcall_static, pvalue_static)
pconfigcall_wrong_owner = pconfigcall_return[.OWNER = (n_capture)]
~$fiber_capture_result_valid(S_value, n_capture, pconfigcall_wrong_owner, false)
pconfigcall_wrong_line = pconfigcall_return[.LINE = $(pconfigcall_return.LINE + 1)]
~$fiber_capture_result_valid(S_value, n_capture, pconfigcall_wrong_line, false)
~$fiber_capture_result_valid(S_value, n_capture, pconfigcall_return, true)
S_duplicate = S_value[.TODO = (FIBER_CAPTURE_RESULT n_capture pconfigcall_return false) :: S_value.TODO]
~$fiber_capture_result_valid(S_duplicate, n_capture, pconfigcall_return, false)
''')
    checks = genuine + controls
    text = EXTRA + PREFIX.replace('STAGE', '$return_peer_stage(S, 0)')
    text += '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks, len(genuine), len(controls)
