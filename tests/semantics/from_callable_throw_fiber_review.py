"""Independent captured-factory throw, injection, saved caller and owned-buffer release checks."""
from error_handler_protocol import PREFIX


EXTRA = r'''
dec $throw_peer_stage(pstate, nat) : bool
def $throw_peer_stage(S, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_FROM_CALLABLE_FACTORY
def $throw_peer_stage(S, 1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_FIBER_THROW
  -- if pconfigcall.SELECTION =/= eps
def $throw_peer_stage(S, 2) = true
  -- if S.TODO = (FIBER_CAPTURE_RESULT n pconfigcall false) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_FIBER_THROW
def $throw_peer_stage(S, 3) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
  -- if pdestructionoperation.SOURCE = FIBER_CAPTURE_RESULT n pconfigcall false
  -- if pconfigcall.KIND = INTRINSIC_FIBER_THROW
def $throw_peer_stage(S, 4) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n_object) :: ptask*
def $throw_peer_stage(S, n) = false -- otherwise
dec $throw_peer_seek(pstate, nat, nat) : pstate
def $throw_peer_seek(S, n_phase, n) = S
  -- if $throw_peer_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $throw_peer_seek(S, n_phase, n) = $throw_peer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if ~$throw_peer_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $throw_peer_seek(S, n_phase, 0) = S
  -- if ~$throw_peer_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $throw_peer_seek(S, n_phase, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $throw_peer_without(pnode*, pnode) : pnode*
def $throw_peer_without(eps, pnode) = eps
def $throw_peer_without(pnode :: pnode_tail*, pnode) = pnode_tail*
def $throw_peer_without(pnode_other :: pnode_tail*, pnode) = pnode_other :: $throw_peer_without(pnode_tail*, pnode)
  -- if pnode_other =/= pnode
'''


def lines(text):
    return text.strip().splitlines()


def guards(state):
    return [f'$call_current_valid({state})',
            f'$call_frames_valid({state}, {state}.FRAMES)',
            f'$call_descriptors_valid({state})',
            f'$class_constant_history_valid({state})',
            f'$fiber_state_valid({state})', f'$heap_valid($heap_graph({state}))']


def seek(state, previous, phase):
    return [f'{state}_reached = $throw_peer_seek({previous}, {phase}, 1000)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$throw_peer_stage({state}, {phase})']


def render(program, filename, expected):
    genuine = [f'S_begin = $php_run({program}, 0, {filename})',
               'S_begin.COMPLETION = BUDGET']
    genuine += seek('S_factory', 'S_begin', 0) + lines(r'''
S_factory.TODO = (CONFIG_INVOKE pconfigcall_factory) :: ptask_factory*
pconfigcall_factory.KIND = INTRINSIC_FROM_CALLABLE_FACTORY
pconfigcall_factory.OWNER = (n_factory)
pconfigcall_factory.SELECTION = eps
pconfigcall_factory.NAMED
pconfigcall_factory.SENT = [NAMED_SENT (KNOWN (PARRAY n_callback))]
S_factory.OBJECTS[n_factory] = FROMCALLABLEFACTORY porigin_create
porigin_create =/= pconfigcall_factory.SITE
$from_factory_site(S_factory, porigin_create)
$from_factory_call_site(S_factory, pconfigcall_factory.SITE)
$node_children(S_factory, HOBJECT n_factory) = eps
$task_nodes(CONFIG_INVOKE pconfigcall_factory) = [HOBJECT n_factory, HARRAY n_callback]
$lookup(S_factory.ENV, $ptascii("factory")) = (n_factory_cell)
S_factory.STORE[n_factory_cell] = DEFINED PNULL
$lookup(S_factory.ENV, $ptascii("callback")) = (n_callback_cell)
S_factory.STORE[n_callback_cell] = DEFINED (PARRAY n_original_callback)
$lookup(S_factory.ENV, $ptascii("method")) = (n_method_cell)
S_factory.STORE[n_method_cell] = DEFINED pvalue_method
$string_bytes(pvalue_method) = ($ptascii("throw"))
n_method_cell <- S_factory.REFCELLS
$entry_lookup(S_factory.ARRAYS[n_callback].ITEMS, KINT 1) = (ALIAS n_method_cell)
pentry* = $fiber_factory_items(S_factory, PARRAY n_callback)
pentry* = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), ENTRY (KINT 1) (DIRECT pvalue_method)]
$fiber_factory_selection(S_factory, PARRAY n_callback, pentry*) = ((INTRINSIC_FIBER_THROW, $ptascii("throw"), (n_receiver)))
$fiber_at(S_factory, n_receiver) = (pfiber_initial)
pfiber_initial.STATUS = FIBER_INIT
$config_invoke_valid(S_factory, pconfigcall_factory)
$heap_owners($heap_graph(S_factory), HOBJECT n_factory) = 1
$lookup(S_factory.ENV, $ptascii("exception")) = (n_exception_cell)
S_factory.STORE[n_exception_cell] = DEFINED (POBJECT n_exception)
S_factory.OBJECTS[n_exception] = THROWABLE pthrowable
pthrowable.KIND = "Exception"
$throwable_field(S_factory, n_exception, "trace") = PARRAY n_exception_trace
S_factory.ARRAYS[n_exception_trace].ITEMS = eps
$node_children(S_factory, HOBJECT n_exception) = [HARRAY n_exception_trace]
''') + guards('S_factory') + lines(r'''
n_capture = |S_factory.OBJECTS|
S_minted_step = $drive_steps(S_factory, 1)
S_minted_step.COMPLETION = BUDGET
S_minted = S_minted_step[.COMPLETION = NORMAL]
S_minted.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture
pfibercapture.FACTORY = (pfiberfactory)
pfibercapture = {SITE pconfigcall_factory.SITE, KIND INTRINSIC_FIBER_THROW, NAME $ptascii("throw"), INPUT (n_receiver), FACTORY (pfiberfactory), ARRAY eps}
pfiberfactory = {CALL pconfigcall_factory, ITEMS pentry*}
$fiber_capture_source_valid(S_minted, pfibercapture)
$fiber_capture_live(S_minted, n_capture)
$node_children(S_minted, HOBJECT n_capture) = [HOBJECT n_receiver]
''') + guards('S_minted')
    genuine += seek('S_invoke', 'S_minted', 1) + lines(r'''
S_invoke.TODO = (CONFIG_INVOKE pconfigcall_throw) :: ptask_release*
ptask_release* = (FIBER_CAPTURE_RELEASE n_capture pconfigcall_throw.SITE) :: ptask_after_call*
pconfigcall_throw.KIND = INTRINSIC_FIBER_THROW
pconfigcall_throw.OWNER = (n_receiver)
pconfigcall_throw.SELECTION = (n_capture)
pconfigcall_throw.NAMED
pconfigcall_throw.SENT = [NAMED_SENT (KNOWN (POBJECT n_exception))]
$class_instanceof(S_invoke, POBJECT n_exception, $ptascii("Throwable"))
$throwable_live(S_invoke, n_exception)
S_invoke.STORE[n_exception_cell] = DEFINED PNULL
n_exception_cell <- S_invoke.REFCELLS
S_invoke.ACTIVEFIBER = eps
S_invoke.FIBERCALLERS = eps
$fiber_at(S_invoke, n_receiver) = (pfiber_suspended)
pfiber_suspended.STATUS = FIBER_SUSPENDED
pfiber_suspended.RAW = POBJECT n_body
pfiber_suspended.VM = (pfibervm_suspended)
pfibervm_suspended.TODO = (FIBER_CONTINUE pfiberapi_suspend) :: ptask_body*
pfiberapi_suspend.KIND = (INTRINSIC_FIBER_SUSPEND)
pfiberapi_suspend.OBJECT = n_receiver
pfiberapi_suspend.SENT = (pvalue_pause)
$string_bytes(pvalue_pause) = ($ptascii("pause"))
pfiberapi_suspend.SEQUENCE = pfiber_suspended.SEQUENCE
$lookup(S_invoke.ENV, $ptascii("selected")) = (n_selected_cell)
S_invoke.STORE[n_selected_cell] = DEFINED PNULL
n_selected_cell <- S_invoke.REFCELLS
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
$heap_owners($heap_graph(S_invoke), HARRAY n_original_callback) = 0
$heap_owners($heap_graph(S_invoke), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_invoke), HOBJECT n_receiver) = 1
$node_children(S_invoke, HOBJECT n_capture) = [HOBJECT n_receiver]
$config_nodes(pconfigcall_throw) = [HOBJECT n_exception]
$heap_owners($heap_graph(S_invoke), HOBJECT n_exception) = 1
$lookup(S_invoke.ENV, $ptascii("weakException")) = (n_weak_exception_cell)
S_invoke.STORE[n_weak_exception_cell] = DEFINED (POBJECT n_weak_exception)
$weakref_get(S_invoke, n_weak_exception) = POBJECT n_exception
$node_children(S_invoke, HOBJECT n_weak_exception) = eps
$lookup(S_invoke.ENV, $ptascii("weakSelected")) = (n_weak_capture_cell)
S_invoke.STORE[n_weak_capture_cell] = DEFINED (POBJECT n_weak_capture)
$weakref_get(S_invoke, n_weak_capture) = POBJECT n_capture
$lookup(S_invoke.ENV, $ptascii("weakFiber")) = (n_weak_receiver_cell)
S_invoke.STORE[n_weak_receiver_cell] = DEFINED (POBJECT n_weak_receiver)
$weakref_get(S_invoke, n_weak_receiver) = POBJECT n_receiver
$task_nodes(FIBER_CAPTURE_RELEASE n_capture pconfigcall_throw.SITE) = [HOBJECT n_capture]
$from_factory_saved(S_invoke, n_factory)
~$from_factory_live(S_invoke, n_factory)
$fiber_factory_saved_call(S_invoke, pconfigcall_factory, INTRINSIC_FIBER_THROW, (n_receiver))
$fiber_capture_source_valid(S_invoke, pfibercapture)
$fiber_capture_config_selected(S_invoke, pconfigcall_throw)
$config_invoke_valid(S_invoke, pconfigcall_throw)
$fiber_vm_valid(S_invoke, pfibervm_suspended, (n_receiver), eps)
$outputs(S_invoke.EVENTS) = $ptascii("Q;A;M:isTerminated;F;B;P:pause;H:held;V;")
''') + guards('S_invoke') + lines(r'''
S_switched_step = $drive_steps(S_invoke, 1)
S_switched_step.COMPLETION = BUDGET
S_switched = S_switched_step[.COMPLETION = NORMAL]
S_switched.ACTIVEFIBER = (n_receiver)
S_switched.TODO = (THROW_SEARCH n_exception) :: ptask_body*
S_switched.RESULT = KNOWN PNULL
S_switched.BASE = BASE_VALUE (KNOWN PNULL)
S_switched.HELD = eps
S_switched.CONSTCONTEXT = eps
$task_nodes(THROW_SEARCH n_exception) = [HOBJECT n_exception]
S_switched.CURRENT = pfibervm_suspended.CURRENT
S_switched.FRAMES = pfibervm_suspended.FRAMES
S_switched.CURRENT = (pcallcontext_body)
pcallcontext_body.TARGET = CLOSURE_TARGET n_body
$fiber_at(S_switched, n_receiver) = (pfiber_running)
pfiber_running.STATUS = FIBER_RUNNING
pfiber_running.VM = eps
$(pfiber_running.SEQUENCE > pfiberapi_suspend.SEQUENCE)
S_switched.FIBERCALLERS = [pfibercaller]
pfibercaller.OBJECT = n_receiver
pfibercaller.PREVIOUS = eps
pfibercaller.VM = pfibervm_caller
pfibercaller.API = pfiberapi_throw
pfibervm_caller.TODO = (FIBER_WAIT pfiberapi_throw) :: (FIBER_CAPTURE_RESULT n_capture pconfigcall_throw false) :: ptask_after_call*
pfibervm_caller.CURRENT = S_invoke.CURRENT
pfibervm_caller.FRAMES = S_invoke.FRAMES
pfiberapi_throw = {SITE pconfigcall_throw.SITE, OBJECT n_receiver, KIND (INTRINSIC_FIBER_THROW), START eps, SENT (POBJECT n_exception), LINE pconfigcall_throw.LINE, SEQUENCE S_invoke.FIBERSEQ, PACKS eps}
pfiber_running.SEQUENCE = pfiberapi_throw.SEQUENCE
S_switched.FIBERSEQ = $(S_invoke.FIBERSEQ + 1)
$task_nodes(FIBER_WAIT pfiberapi_throw) = eps
$task_nodes(FIBER_CAPTURE_RESULT n_capture pconfigcall_throw false) = [HOBJECT n_capture]
$fiber_caller_api_nodes(pfibercaller) = [HOBJECT n_exception]
$heap_owners($heap_graph(S_switched), HOBJECT n_exception) = 2
$throwable_field(S_switched, n_exception, "trace") = PARRAY n_exception_trace
S_switched.ARRAYS[n_exception_trace].ITEMS = eps
S_switched.STORE[n_exception_cell] = DEFINED PNULL
$heap_owners($heap_graph(S_switched), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_switched), HOBJECT n_receiver) = 1
S_switched.STORE[n_selected_cell] = DEFINED PNULL
S_switched.STORE[n_fiber_cell] = DEFINED PNULL
$fiber_capture_live(S_switched, n_capture)
$call_task_valid(S_switched, THROW_SEARCH n_exception)
$fiber_vm_valid(S_switched, pfibervm_caller, eps, eps)
S_caller_view = $fiber_vm_restore(S_switched, pfibervm_caller)[.ACTIVEFIBER = eps][.FIBERCALLERS = eps]
$fiber_api_valid(S_caller_view, pfiberapi_throw)
$fiber_wait_valid(S_caller_view, pfiberapi_throw)
$fiber_capture_result_valid(S_caller_view, n_capture, pconfigcall_throw, false)
$outputs(S_switched.EVENTS) = $outputs(S_invoke.EVENTS)
''') + guards('S_switched')
    genuine += seek('S_before_catch', 'S_switched', 4) + lines(r'''
S_before_catch.TODO = (CATCH_BIND porigin_try n_catch n_exception) :: ptask_after_catch*
S_before_catch.RESULT = KNOWN PNULL
S_before_catch.ACTIVEFIBER = (n_receiver)
S_before_catch.FIBERCALLERS = [pfibercaller]
$throwable_binding_valid(S_before_catch, porigin_try, n_catch, n_exception)
$heap_owners($heap_graph(S_before_catch), HOBJECT n_exception) = 2
$task_nodes(CATCH_BIND porigin_try n_catch n_exception) = [HOBJECT n_exception]
$outputs(S_before_catch.EVENTS) = $outputs(S_switched.EVENTS)
S_caught_step = $drive_steps(S_before_catch, 1)
S_caught_step.COMPLETION = BUDGET
S_caught = S_caught_step[.COMPLETION = NORMAL]
S_caught.ACTIVEFIBER = (n_receiver)
S_caught.FIBERCALLERS = [pfibercaller]
S_caught.RESULT = KNOWN PNULL
S_caught.CURRENT = S_switched.CURRENT
S_caught.FRAMES = S_switched.FRAMES
$lookup(S_caught.ENV, $ptascii("caught")) = (n_caught_cell)
S_caught.STORE[n_caught_cell] = DEFINED (POBJECT n_exception)
$heap_owners($heap_graph(S_caught), HOBJECT n_exception) = 2
$heap_owners($heap_graph(S_caught), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_caught), HOBJECT n_receiver) = 1
$weakref_get(S_caught, n_weak_exception) = POBJECT n_exception
$weakref_get(S_caught, n_weak_capture) = POBJECT n_capture
$outputs(S_caught.EVENTS) = $outputs(S_switched.EVENTS)
''') + guards('S_before_catch') + guards('S_caught')
    genuine += seek('S_result', 'S_caught', 2) + lines(r'''
S_result.TODO = (FIBER_CAPTURE_RESULT n_capture pconfigcall_throw false) :: ptask_after_call*
S_result.RESULT = KNOWN PNULL
S_result.ACTIVEFIBER = eps
S_result.FIBERCALLERS = eps
S_result.CURRENT = S_invoke.CURRENT
S_result.FRAMES = S_invoke.FRAMES
$fiber_at(S_result, n_receiver) = (pfiber_terminated)
pfiber_terminated.STATUS = FIBER_TERMINATED
pfiber_terminated.RAW = PNULL
pfiber_terminated.TARGET = eps
pfiber_terminated.RETURNED
pfiber_terminated.VALUE = pvalue_finished
$string_bytes(pvalue_finished) = ($ptascii("finished"))
$fiber_capture_result_valid(S_result, n_capture, pconfigcall_throw, false)
$heap_owners($heap_graph(S_result), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_result), HOBJECT n_receiver) = 1
~((HOBJECT n_exception) <- S_result.ALLOCATIONS)
$heap_owners($heap_graph(S_result), HOBJECT n_exception) = 0
$weakref_get(S_result, n_weak_exception) = PNULL
~$config_slots_valid(S_result, pconfigcall_throw.SENT)
$task_nodes(FIBER_CAPTURE_RESULT n_capture pconfigcall_throw false) = [HOBJECT n_capture]
$outputs(S_result.EVENTS) = $ptascii("Q;A;M:isTerminated;F;B;P:pause;H:held;V;I:same;C:held;")
S_release_begin_step = $drive_steps(S_result, 1)
S_release_begin_step.COMPLETION = BUDGET
S_release_begin = S_release_begin_step[.COMPLETION = NORMAL]
S_release_begin.RESULT = KNOWN PNULL
S_release_begin.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
pdestructionoperation.SOURCE = FIBER_CAPTURE_RESULT n_capture pconfigcall_throw false
pdestructionoperation.VALUE = KNOWN PNULL
pdestructionoperation.PENDING = eps
S_release_begin.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_after_call*
$destructor_release_valid(S_release_begin, pdestructionrelease)
$destructor_operation_valid(S_release_begin, pdestructionoperation)
$heap_owners($heap_graph(S_release_begin), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_release_begin), HOBJECT n_receiver) = 1
$fiber_capture_live(S_release_begin, n_capture)
$outputs(S_release_begin.EVENTS) = $outputs(S_result.EVENTS)
''') + guards('S_result') + guards('S_release_begin')
    genuine += seek('S_release_exit', 'S_release_begin', 3) + lines(r'''
S_release_exit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_after_call*
S_release_exit.RESULT = KNOWN PNULL
$destructor_operation_valid(S_release_exit, pdestructionoperation)
~((HOBJECT n_capture) <- S_release_exit.ALLOCATIONS)
~((HOBJECT n_receiver) <- S_release_exit.ALLOCATIONS)
$heap_owners($heap_graph(S_release_exit), HOBJECT n_capture) = 0
$heap_owners($heap_graph(S_release_exit), HOBJECT n_receiver) = 0
~$fiber_capture_source_valid(S_release_exit, pfibercapture)
~$fiber_capture_live(S_release_exit, n_capture)
S_value_step = $drive_steps(S_release_exit, 1)
S_value_step.COMPLETION = BUDGET
S_value = S_value_step[.COMPLETION = NORMAL]
S_value.RESULT = KNOWN PNULL
S_value.TODO = ptask_after_call*
S_value.DESTRUCTION.OPERATIONS = pdestructionoperation_tail*
$outputs(S_value.EVENTS) = $outputs(S_result.EVENTS)
''') + guards('S_release_exit') + guards('S_value') + lines(r'''
S_zero = $drive_steps(S_invoke, 0)
S_zero = S_invoke[.COMPLETION = BUDGET]
S_done = $drive(S_zero[.COMPLETION = NORMAL], 1000)
S_done = $drive(S_invoke, 1000)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
~((HOBJECT n_capture) <- S_done.ALLOCATIONS)
~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)
$heap_owners($heap_graph(S_done), HOBJECT n_capture) = 0
$heap_owners($heap_graph(S_done), HOBJECT n_receiver) = 0
~((HOBJECT n_exception) <- S_done.ALLOCATIONS)
$heap_owners($heap_graph(S_done), HOBJECT n_exception) = 0
$weakref_get(S_done, n_weak_exception) = PNULL
$weakref_get(S_done, n_weak_capture) = PNULL
$weakref_get(S_done, n_weak_receiver) = PNULL
$from_factory_saved(S_done, n_factory)
~$from_factory_live(S_done, n_factory)
$fiber_factory_saved_call(S_done, pconfigcall_factory, INTRINSIC_FIBER_THROW, (n_receiver))
~$fiber_capture_source_valid(S_done, pfibercapture)
~$fiber_capture_live(S_done, n_capture)
''') + [f'$outputs(S_done.EVENTS) = $ptascii("{expected}")'] + guards('S_done')
    controls = []
    for name, change in [('input', '.INPUT = eps'),
                         ('kind', '.KIND = INTRINSIC_FIBER_RESUME'),
                         ('name', '.NAME = $ptascii("resume")')]:
        controls += [f'pfibercapture_bad_{name} = pfibercapture[{change}]',
                     f'~$fiber_capture_source_valid(S_invoke, pfibercapture_bad_{name})',
                     f'S_bad_{name} = S_invoke[.OBJECTS = $object_set(S_invoke.OBJECTS, n_capture, FIBERAPICLOSURE pfibercapture_bad_{name})]',
                     f'~$fiber_capture_live(S_bad_{name}, n_capture)',
                     f'~$call_descriptors_valid(S_bad_{name})']
        if name != 'input':
            controls += [f'$heap_graph(S_bad_{name}) = $heap_graph(S_invoke)']
    for name, change in [('line', '.LINE = 999'), ('owner', '.OWNER = (n_receiver)')]:
        controls += [f'pfiberfactory_bad_{name} = pfiberfactory[.CALL = pconfigcall_factory[{change}]]',
                     f'S_bad_{name} = S_invoke[.OBJECTS = $object_set(S_invoke.OBJECTS, n_capture, FIBERAPICLOSURE pfibercapture[.FACTORY = (pfiberfactory_bad_{name})])]',
                     f'$heap_graph(S_bad_{name}) = $heap_graph(S_invoke)',
                     f'~$fiber_capture_live(S_bad_{name}, n_capture)',
                     f'~$call_descriptors_valid(S_bad_{name})']
    controls += lines(r'''
n_substitute = |S_invoke.OBJECTS|
S_other = S_invoke[.OBJECTS = S_invoke.OBJECTS ++ [FIBER $fiber_empty()]][.ALLOCATIONS = S_invoke.ALLOCATIONS ++ [HOBJECT n_substitute]]
$fiber_at(S_other, n_substitute) =/= eps
$heap_valid($heap_graph(S_other))
$fiber_factory_selection(S_other, PARRAY n_callback, pentry*) = ((INTRINSIC_FIBER_THROW, $ptascii("throw"), (n_receiver)))
~$fiber_capture_source_valid(S_other, pfibercapture[.INPUT = (n_substitute)])
S_missing_receiver = S_invoke[.ALLOCATIONS = $throw_peer_without(S_invoke.ALLOCATIONS, HOBJECT n_receiver)]
~$fiber_capture_source_valid(S_missing_receiver, pfibercapture)
~$fiber_capture_live(S_missing_receiver, n_capture)
pfiberfactory_alias = pfiberfactory[.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), ENTRY (KINT 1) (ALIAS n_method_cell)]]
S_alias = S_invoke[.OBJECTS = $object_set(S_invoke.OBJECTS, n_capture, FIBERAPICLOSURE pfibercapture[.FACTORY = (pfiberfactory_alias)])]
$heap_graph(S_alias) = $heap_graph(S_invoke)
~$fiber_capture_live(S_alias, n_capture)
~$call_descriptors_valid(S_alias)
''')
    for name, change in [('site', '.SITE = pconfigcall_factory.SITE'),
                         ('line', '.LINE = 999'),
                         ('sent', '.SENT = (PSTRING $ptascii("forged"))'),
                         ('sequence', '.SEQUENCE = 0'),
                         ('kind', '.KIND = (INTRINSIC_FIBER_RESUME)')]:
        controls += [f'pfiberapi_bad_{name} = pfiberapi_throw[{change}]',
                     f'pfibervm_bad_{name} = pfibervm_caller[.TODO = (FIBER_WAIT pfiberapi_bad_{name}) :: (FIBER_CAPTURE_RESULT n_capture pconfigcall_throw false) :: ptask_after_call*]',
                     f'pfibercaller_bad_{name} = pfibercaller[.API = pfiberapi_bad_{name}][.VM = pfibervm_bad_{name}]',
                     f'S_switched_bad_{name} = S_switched[.FIBERCALLERS = [pfibercaller_bad_{name}]]',
                     f'S_caller_bad_{name} = $fiber_vm_restore(S_switched_bad_{name}, pfibervm_bad_{name})[.ACTIVEFIBER = eps][.FIBERCALLERS = eps]',
                     f'~$fiber_api_valid(S_caller_bad_{name}, pfiberapi_bad_{name})',
                     f'~$fiber_wait_valid(S_caller_bad_{name}, pfiberapi_bad_{name})',
                     f'~$call_descriptors_valid(S_switched_bad_{name})']
    controls += lines(r'''
pfibervm_missing_result = pfibervm_caller[.TODO = (FIBER_WAIT pfiberapi_throw) :: ptask_after_call*]
S_missing_result = S_switched[.FIBERCALLERS = [pfibercaller[.VM = pfibervm_missing_result]]]
$heap_owners($heap_graph(S_missing_result), HOBJECT n_capture) = 0
S_missing_result_view = $fiber_vm_restore(S_missing_result, pfibervm_missing_result)[.ACTIVEFIBER = eps][.FIBERCALLERS = eps]
~$fiber_api_valid(S_missing_result_view, pfiberapi_throw)
~$call_descriptors_valid(S_missing_result)
''')
    controls += lines(r'''
pconfigcall_bad_type = pconfigcall_throw[.SENT = [NAMED_SENT (KNOWN (PINT 7))]]
pfiberapi_bad_type = pfiberapi_throw[.SENT = (PINT 7)]
pfibervm_bad_type = pfibervm_caller[.TODO = (FIBER_WAIT pfiberapi_bad_type) :: (FIBER_CAPTURE_RESULT n_capture pconfigcall_bad_type false) :: ptask_after_call*]
S_bad_type_view = $fiber_vm_restore(S_switched, pfibervm_bad_type)[.ACTIVEFIBER = eps][.FIBERCALLERS = eps]
$config_slots_valid(S_bad_type_view, pconfigcall_bad_type.SENT)
$fiber_capture_result_valid(S_bad_type_view, n_capture, pconfigcall_bad_type, false)
~$class_instanceof(S_bad_type_view, PINT 7, $ptascii("Throwable"))
~$fiber_api_valid(S_bad_type_view, pfiberapi_bad_type)
~$fiber_wait_valid(S_bad_type_view, pfiberapi_bad_type)
''')
    checks = genuine + controls
    text = EXTRA + PREFIX[PREFIX.index('dec $outputs'):]
    text += '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks, len(genuine), len(controls)
