"""Independent captured-factory resume, saved caller and receiver release checks."""
from error_handler_protocol import PREFIX


EXTRA = r'''
dec $resume_peer_stage(pstate, nat) : bool
def $resume_peer_stage(S, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_FROM_CALLABLE_FACTORY
def $resume_peer_stage(S, 1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME
  -- if pconfigcall.SELECTION =/= eps
def $resume_peer_stage(S, 2) = true
  -- if S.TODO = (FIBER_CAPTURE_RESULT n pconfigcall false) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME
def $resume_peer_stage(S, 3) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
  -- if pdestructionoperation.SOURCE = FIBER_CAPTURE_RESULT n pconfigcall false
  -- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME
def $resume_peer_stage(S, n) = false -- otherwise
dec $resume_peer_seek(pstate, nat, nat) : pstate
def $resume_peer_seek(S, n_phase, n) = S
  -- if $resume_peer_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $resume_peer_seek(S, n_phase, n) = $resume_peer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if ~$resume_peer_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $resume_peer_seek(S, n_phase, 0) = S
  -- if ~$resume_peer_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $resume_peer_seek(S, n_phase, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $resume_peer_without(pnode*, pnode) : pnode*
def $resume_peer_without(eps, pnode) = eps
def $resume_peer_without(pnode :: pnode_tail*, pnode) = pnode_tail*
def $resume_peer_without(pnode_other :: pnode_tail*, pnode) = pnode_other :: $resume_peer_without(pnode_tail*, pnode)
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
    return [f'{state}_reached = $resume_peer_seek({previous}, {phase}, 1000)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$resume_peer_stage({state}, {phase})']


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
$string_bytes(pvalue_method) = ($ptascii("resume"))
n_method_cell <- S_factory.REFCELLS
$entry_lookup(S_factory.ARRAYS[n_callback].ITEMS, KINT 1) = (ALIAS n_method_cell)
pentry* = $fiber_factory_items(S_factory, PARRAY n_callback)
pentry* = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), ENTRY (KINT 1) (DIRECT pvalue_method)]
$fiber_factory_selection(S_factory, PARRAY n_callback, pentry*) = ((INTRINSIC_FIBER_RESUME, $ptascii("resume"), (n_receiver)))
$fiber_at(S_factory, n_receiver) = (pfiber_initial)
pfiber_initial.STATUS = FIBER_INIT
$config_invoke_valid(S_factory, pconfigcall_factory)
$heap_owners($heap_graph(S_factory), HOBJECT n_factory) = 1
''') + guards('S_factory') + lines(r'''
n_capture = |S_factory.OBJECTS|
S_minted_step = $drive_steps(S_factory, 1)
S_minted_step.COMPLETION = BUDGET
S_minted = S_minted_step[.COMPLETION = NORMAL]
S_minted.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture
pfibercapture.FACTORY = (pfiberfactory)
pfibercapture = {SITE pconfigcall_factory.SITE, KIND INTRINSIC_FIBER_RESUME, NAME $ptascii("resume"), INPUT (n_receiver), FACTORY (pfiberfactory), ARRAY eps}
pfiberfactory = {CALL pconfigcall_factory, ITEMS pentry*}
$fiber_capture_source_valid(S_minted, pfibercapture)
$fiber_capture_live(S_minted, n_capture)
$node_children(S_minted, HOBJECT n_capture) = [HOBJECT n_receiver]
''') + guards('S_minted')
    genuine += seek('S_invoke', 'S_minted', 1) + lines(r'''
S_invoke.TODO = (CONFIG_INVOKE pconfigcall_resume) :: ptask_release*
ptask_release* = (FIBER_CAPTURE_RELEASE n_capture pconfigcall_resume.SITE) :: ptask_after_call*
pconfigcall_resume.KIND = INTRINSIC_FIBER_RESUME
pconfigcall_resume.OWNER = (n_receiver)
pconfigcall_resume.SELECTION = (n_capture)
pconfigcall_resume.NAMED
pconfigcall_resume.SENT = [NAMED_SENT (KNOWN pvalue_done)]
$string_bytes(pvalue_done) = ($ptascii("done"))
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
$config_nodes(pconfigcall_resume) = eps
$task_nodes(FIBER_CAPTURE_RELEASE n_capture pconfigcall_resume.SITE) = [HOBJECT n_capture]
$from_factory_saved(S_invoke, n_factory)
~$from_factory_live(S_invoke, n_factory)
$fiber_factory_saved_call(S_invoke, pconfigcall_factory, INTRINSIC_FIBER_RESUME, (n_receiver))
$fiber_capture_source_valid(S_invoke, pfibercapture)
$fiber_capture_config_selected(S_invoke, pconfigcall_resume)
$config_invoke_valid(S_invoke, pconfigcall_resume)
$fiber_vm_valid(S_invoke, pfibervm_suspended, (n_receiver), eps)
$outputs(S_invoke.EVENTS) = $ptascii("Q;A;M:isTerminated;F;B;P:pause;H:held;V;")
''') + guards('S_invoke') + lines(r'''
S_switched_step = $drive_steps(S_invoke, 1)
S_switched_step.COMPLETION = BUDGET
S_switched = S_switched_step[.COMPLETION = NORMAL]
S_switched.ACTIVEFIBER = (n_receiver)
S_switched.TODO = (FIBER_CONTINUE pfiberapi_suspend) :: ptask_body*
S_switched.RESULT = KNOWN pvalue_done
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
pfibercaller.API = pfiberapi_resume
pfibervm_caller.TODO = (FIBER_WAIT pfiberapi_resume) :: (FIBER_CAPTURE_RESULT n_capture pconfigcall_resume false) :: ptask_after_call*
pfibervm_caller.CURRENT = S_invoke.CURRENT
pfibervm_caller.FRAMES = S_invoke.FRAMES
pfiberapi_resume = {SITE pconfigcall_resume.SITE, OBJECT n_receiver, KIND (INTRINSIC_FIBER_RESUME), START eps, SENT (pvalue_done), LINE pconfigcall_resume.LINE, SEQUENCE S_invoke.FIBERSEQ, PACKS eps}
pfiber_running.SEQUENCE = pfiberapi_resume.SEQUENCE
S_switched.FIBERSEQ = $(S_invoke.FIBERSEQ + 1)
$task_nodes(FIBER_WAIT pfiberapi_resume) = eps
$task_nodes(FIBER_CAPTURE_RESULT n_capture pconfigcall_resume false) = [HOBJECT n_capture]
$fiber_caller_api_nodes(pfibercaller) = eps
$heap_owners($heap_graph(S_switched), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_switched), HOBJECT n_receiver) = 1
S_switched.STORE[n_selected_cell] = DEFINED PNULL
S_switched.STORE[n_fiber_cell] = DEFINED PNULL
$fiber_capture_live(S_switched, n_capture)
$fiber_continue_valid(S_switched, pfiberapi_suspend)
$fiber_vm_valid(S_switched, pfibervm_caller, eps, eps)
S_caller_view = $fiber_vm_restore(S_switched, pfibervm_caller)[.ACTIVEFIBER = eps][.FIBERCALLERS = eps]
$fiber_api_valid(S_caller_view, pfiberapi_resume)
$fiber_wait_valid(S_caller_view, pfiberapi_resume)
$fiber_capture_result_valid(S_caller_view, n_capture, pconfigcall_resume, false)
$outputs(S_switched.EVENTS) = $outputs(S_invoke.EVENTS)
''') + guards('S_switched')
    genuine += seek('S_result', 'S_switched', 2) + lines(r'''
S_result.TODO = (FIBER_CAPTURE_RESULT n_capture pconfigcall_resume false) :: ptask_after_call*
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
$fiber_capture_result_valid(S_result, n_capture, pconfigcall_resume, false)
$heap_owners($heap_graph(S_result), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_result), HOBJECT n_receiver) = 1
$outputs(S_result.EVENTS) = $ptascii("Q;A;M:isTerminated;F;B;P:pause;H:held;V;R:done;C:held;")
S_release_begin_step = $drive_steps(S_result, 1)
S_release_begin_step.COMPLETION = BUDGET
S_release_begin = S_release_begin_step[.COMPLETION = NORMAL]
S_release_begin.RESULT = KNOWN PNULL
S_release_begin.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
pdestructionoperation.SOURCE = FIBER_CAPTURE_RESULT n_capture pconfigcall_resume false
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
$from_factory_saved(S_done, n_factory)
~$from_factory_live(S_done, n_factory)
$fiber_factory_saved_call(S_done, pconfigcall_factory, INTRINSIC_FIBER_RESUME, (n_receiver))
~$fiber_capture_source_valid(S_done, pfibercapture)
~$fiber_capture_live(S_done, n_capture)
''') + [f'$outputs(S_done.EVENTS) = $ptascii("{expected}")'] + guards('S_done')
    controls = []
    for name, change in [('input', '.INPUT = eps'),
                         ('kind', '.KIND = INTRINSIC_FIBER_TERMINATED'),
                         ('name', '.NAME = $ptascii("isTerminated")')]:
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
$fiber_factory_selection(S_other, PARRAY n_callback, pentry*) = ((INTRINSIC_FIBER_RESUME, $ptascii("resume"), (n_receiver)))
~$fiber_capture_source_valid(S_other, pfibercapture[.INPUT = (n_substitute)])
S_missing_receiver = S_invoke[.ALLOCATIONS = $resume_peer_without(S_invoke.ALLOCATIONS, HOBJECT n_receiver)]
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
                         ('sequence', '.SEQUENCE = 0')]:
        controls += [f'pfiberapi_bad_{name} = pfiberapi_resume[{change}]',
                     f'pfibervm_bad_{name} = pfibervm_caller[.TODO = (FIBER_WAIT pfiberapi_bad_{name}) :: (FIBER_CAPTURE_RESULT n_capture pconfigcall_resume false) :: ptask_after_call*]',
                     f'pfibercaller_bad_{name} = pfibercaller[.API = pfiberapi_bad_{name}][.VM = pfibervm_bad_{name}]',
                     f'S_switched_bad_{name} = S_switched[.FIBERCALLERS = [pfibercaller_bad_{name}]]',
                     f'S_caller_bad_{name} = $fiber_vm_restore(S_switched_bad_{name}, pfibervm_bad_{name})[.ACTIVEFIBER = eps][.FIBERCALLERS = eps]',
                     f'~$fiber_api_valid(S_caller_bad_{name}, pfiberapi_bad_{name})',
                     f'~$fiber_wait_valid(S_caller_bad_{name}, pfiberapi_bad_{name})',
                     f'~$call_descriptors_valid(S_switched_bad_{name})']
    controls += lines(r'''
pfibervm_missing_result = pfibervm_caller[.TODO = (FIBER_WAIT pfiberapi_resume) :: ptask_after_call*]
S_missing_result = S_switched[.FIBERCALLERS = [pfibercaller[.VM = pfibervm_missing_result]]]
$heap_owners($heap_graph(S_missing_result), HOBJECT n_capture) = 0
S_missing_result_view = $fiber_vm_restore(S_missing_result, pfibervm_missing_result)[.ACTIVEFIBER = eps][.FIBERCALLERS = eps]
~$fiber_api_valid(S_missing_result_view, pfiberapi_resume)
~$call_descriptors_valid(S_missing_result)
''')
    checks = genuine + controls
    text = EXTRA + PREFIX[PREFIX.index('dec $outputs'):]
    text += '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks, len(genuine), len(controls)
