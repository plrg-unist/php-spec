"""Independent captured static suspension, parked owner and resume checks."""
from error_handler_protocol import PREFIX


EXTRA = r'''
dec $suspend_peer_stage(pstate, nat) : bool
def $suspend_peer_stage(S, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_FROM_CALLABLE_FACTORY
def $suspend_peer_stage(S, 1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_FIBER_SUSPEND
  -- if pconfigcall.SELECTION =/= eps
  -- if S.ACTIVEFIBER =/= eps
def $suspend_peer_stage(S, 2) = true
  -- if S.TODO = (FIBER_CONTINUE pfiberapi) :: ptask*
  -- if pfiberapi.KIND = (INTRINSIC_FIBER_SUSPEND)
def $suspend_peer_stage(S, 3) = true
  -- if S.TODO = (FIBER_CAPTURE_RESULT n pconfigcall false) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_FIBER_SUSPEND
def $suspend_peer_stage(S, 4) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
  -- if pdestructionoperation.SOURCE = FIBER_CAPTURE_RESULT n pconfigcall false
  -- if pconfigcall.KIND = INTRINSIC_FIBER_SUSPEND
def $suspend_peer_stage(S, n) = false -- otherwise
dec $suspend_peer_seek(pstate, nat, nat) : pstate
def $suspend_peer_seek(S, n_phase, n) = S
  -- if $suspend_peer_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $suspend_peer_seek(S, n_phase, n) = $suspend_peer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if ~$suspend_peer_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $suspend_peer_seek(S, n_phase, 0) = S
  -- if ~$suspend_peer_stage(S, n_phase)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $suspend_peer_seek(S, n_phase, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
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
    return [f'{state}_reached = $suspend_peer_seek({previous}, {phase}, 1000)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$suspend_peer_stage({state}, {phase})']


def render(program, filename, expected):
    genuine = [f'S_begin = $php_run({program}, 0, {filename})',
               'S_begin.COMPLETION = BUDGET']
    genuine += seek('S_factory', 'S_begin', 0) + lines(r'''
S_factory.TODO = (CONFIG_INVOKE pconfigcall_factory) :: ptask_factory*
pconfigcall_factory.KIND = INTRINSIC_FROM_CALLABLE_FACTORY
pconfigcall_factory.OWNER = (n_factory)
pconfigcall_factory.SELECTION = eps
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
$string_bytes(pvalue_method) = ($ptascii("suspend"))
n_method_cell <- S_factory.REFCELLS
$entry_lookup(S_factory.ARRAYS[n_callback].ITEMS, KINT 1) = (ALIAS n_method_cell)
pentry* = $fiber_factory_items(S_factory, PARRAY n_callback)
pentry* = [ENTRY (KINT 0) (DIRECT pvalue_class), ENTRY (KINT 1) (DIRECT pvalue_method)]
$string_bytes(pvalue_class) = ($ptascii("Fiber"))
$fiber_factory_selection(S_factory, PARRAY n_callback, pentry*) = ((INTRINSIC_FIBER_SUSPEND, $ptascii("suspend"), eps))
$config_invoke_valid(S_factory, pconfigcall_factory)
$heap_owners($heap_graph(S_factory), HOBJECT n_factory) = 1
''') + guards('S_factory') + lines(r'''
n_capture = |S_factory.OBJECTS|
S_minted_step = $drive_steps(S_factory, 1)
S_minted_step.COMPLETION = BUDGET
S_minted = S_minted_step[.COMPLETION = NORMAL]
S_minted.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture
pfibercapture.FACTORY = (pfiberfactory)
pfibercapture = {SITE pconfigcall_factory.SITE, KIND INTRINSIC_FIBER_SUSPEND, NAME $ptascii("suspend"), INPUT eps, FACTORY (pfiberfactory), ARRAY eps}
pfiberfactory = {CALL pconfigcall_factory, ITEMS pentry*}
$fiber_capture_source_valid(S_minted, pfibercapture)
$fiber_capture_live(S_minted, n_capture)
$node_children(S_minted, HOBJECT n_capture) = eps
''') + guards('S_minted')
    genuine += seek('S_invoke', 'S_minted', 1) + lines(r'''
S_invoke.TODO = (CONFIG_INVOKE pconfigcall_suspend) :: ptask_release*
ptask_release* = (FIBER_CAPTURE_RELEASE n_capture pconfigcall_suspend.SITE) :: ptask_after_call*
pconfigcall_suspend.KIND = INTRINSIC_FIBER_SUSPEND
pconfigcall_suspend.OWNER = (n_capture)
pconfigcall_suspend.SELECTION = (n_capture)
pconfigcall_suspend.SENT = [NAMED_SENT (KNOWN pvalue_pause)]
$string_bytes(pvalue_pause) = ($ptascii("pause"))
~pconfigcall_suspend.NAMED
S_invoke.ACTIVEFIBER = (n_fiber)
n_fiber =/= n_capture
$fiber_at(S_invoke, n_fiber) = (pfiber_running)
pfiber_running.STATUS = FIBER_RUNNING
S_invoke.CURRENT = (pcallcontext_body)
pfiber_running.RAW = POBJECT n_body
pcallcontext_body.TARGET = CLOSURE_TARGET n_body
S_global = $global_table_view(S_invoke)
$lookup(S_global.ENV, $ptascii("selected")) = (n_selected_cell)
S_invoke.STORE[n_selected_cell] = DEFINED PNULL
n_selected_cell <- S_invoke.REFCELLS
S_invoke.STORE[n_callback_cell] = DEFINED PNULL
S_invoke.STORE[n_method_cell] = DEFINED pvalue_changed
$string_bytes(pvalue_changed) = ($ptascii("getCurrent"))
~((HOBJECT n_factory) <- S_invoke.ALLOCATIONS)
~((HARRAY n_callback) <- S_invoke.ALLOCATIONS)
~((HARRAY n_original_callback) <- S_invoke.ALLOCATIONS)
$heap_owners($heap_graph(S_invoke), HOBJECT n_factory) = 0
$heap_owners($heap_graph(S_invoke), HARRAY n_callback) = 0
$heap_owners($heap_graph(S_invoke), HARRAY n_original_callback) = 0
$node_children(S_invoke, HOBJECT n_capture) = eps
$config_nodes(pconfigcall_suspend) = eps
$task_nodes(FIBER_CAPTURE_RELEASE n_capture pconfigcall_suspend.SITE) = [HOBJECT n_capture]
$heap_owners($heap_graph(S_invoke), HOBJECT n_capture) = 1
$from_factory_saved(S_invoke, n_factory)
~$from_factory_live(S_invoke, n_factory)
$fiber_factory_saved_call(S_invoke, pconfigcall_factory, INTRINSIC_FIBER_SUSPEND, eps)
$fiber_capture_source_valid(S_invoke, pfibercapture)
$fiber_capture_config_selected(S_invoke, pconfigcall_suspend)
$config_invoke_valid(S_invoke, pconfigcall_suspend)
$outputs(S_invoke.EVENTS) = $ptascii("Q;A;M:getCurrent;F;B;V;")
''') + guards('S_invoke') + lines(r'''
S_parked_step = $drive_steps(S_invoke, 1)
S_parked_step.COMPLETION = BUDGET
S_parked = S_parked_step[.COMPLETION = NORMAL]
S_parked.ACTIVEFIBER = eps
S_parked.FIBERCALLERS = eps
$fiber_at(S_parked, n_fiber) = (pfiber_parked)
pfiber_parked.STATUS = FIBER_SUSPENDED
pfiber_parked.VM = (pfibervm_parked)
pfibervm_parked.CURRENT = S_invoke.CURRENT
pfibervm_parked.FRAMES = S_invoke.FRAMES
pfibervm_parked.TODO = (FIBER_CONTINUE pfiberapi_suspend) :: (FIBER_CAPTURE_RESULT n_capture pconfigcall_suspend false) :: ptask_after_call*
pfiberapi_suspend.OBJECT = n_fiber
pfiberapi_suspend.KIND = (INTRINSIC_FIBER_SUSPEND)
pfiberapi_suspend.START = eps
pfiberapi_suspend.SENT = (pvalue_pause)
pfiberapi_suspend.PACKS = eps
pfiberapi_suspend.SITE = pconfigcall_suspend.SITE
pfiberapi_suspend.LINE = pconfigcall_suspend.LINE
pfiberapi_suspend.SEQUENCE = pfiber_parked.SEQUENCE
$task_nodes(FIBER_CONTINUE pfiberapi_suspend) = eps
$task_nodes(FIBER_CAPTURE_RESULT n_capture pconfigcall_suspend false) = [HOBJECT n_capture]
$heap_owners($heap_graph(S_parked), HOBJECT n_capture) = 1
$fiber_capture_live(S_parked, n_capture)
$fiber_record_valid(S_parked, n_fiber, pfiber_parked)
$fiber_vm_valid(S_parked, pfibervm_parked, (n_fiber), eps)
S_parked_view = $fiber_vm_restore(S_parked, pfibervm_parked)[.ACTIVEFIBER = (n_fiber)][.FIBERCALLERS = eps]
$fiber_api_valid(S_parked_view, pfiberapi_suspend)
$fiber_capture_result_valid(S_parked_view, n_capture, pconfigcall_suspend, false)
''') + guards('S_parked')
    genuine += seek('S_continue', 'S_parked', 2) + lines(r'''
S_continue.TODO = (FIBER_CONTINUE pfiberapi_suspend) :: (FIBER_CAPTURE_RESULT n_capture pconfigcall_suspend false) :: ptask_after_call*
S_continue.ACTIVEFIBER = (n_fiber)
S_continue.RESULT = KNOWN pvalue_done
$string_bytes(pvalue_done) = ($ptascii("done"))
$fiber_at(S_continue, n_fiber) = (pfiber_resumed)
pfiber_resumed.STATUS = FIBER_RUNNING
pfiber_resumed.VM = eps
$(pfiber_resumed.SEQUENCE > pfiberapi_suspend.SEQUENCE)
S_continue.STORE[n_selected_cell] = DEFINED PNULL
$heap_owners($heap_graph(S_continue), HOBJECT n_capture) = 1
$fiber_continue_valid(S_continue, pfiberapi_suspend)
$fiber_api_valid(S_continue, pfiberapi_suspend)
$fiber_capture_result_valid(S_continue, n_capture, pconfigcall_suspend, false)
''') + guards('S_continue')
    genuine += seek('S_result', 'S_continue', 3) + lines(r'''
S_result.TODO = (FIBER_CAPTURE_RESULT n_capture pconfigcall_suspend false) :: ptask_after_call*
S_result.RESULT = KNOWN pvalue_done
$fiber_capture_result_valid(S_result, n_capture, pconfigcall_suspend, false)
$heap_owners($heap_graph(S_result), HOBJECT n_capture) = 1
S_release_begin_step = $drive_steps(S_result, 1)
S_release_begin_step.COMPLETION = BUDGET
S_release_begin = S_release_begin_step[.COMPLETION = NORMAL]
S_release_begin.RESULT = KNOWN PNULL
S_release_begin.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
pdestructionoperation.SOURCE = FIBER_CAPTURE_RESULT n_capture pconfigcall_suspend false
pdestructionoperation.VALUE = KNOWN pvalue_done
pdestructionoperation.PENDING = eps
S_release_begin.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_after_call*
$destructor_release_valid(S_release_begin, pdestructionrelease)
$destructor_operation_valid(S_release_begin, pdestructionoperation)
$heap_owners($heap_graph(S_release_begin), HOBJECT n_capture) = 1
$fiber_capture_live(S_release_begin, n_capture)
$outputs(S_release_begin.EVENTS) = $outputs(S_result.EVENTS)
''') + guards('S_result') + guards('S_release_begin')
    genuine += seek('S_release_exit', 'S_release_begin', 4) + lines(r'''
S_release_exit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_after_call*
S_release_exit.RESULT = KNOWN PNULL
$destructor_operation_valid(S_release_exit, pdestructionoperation)
~((HOBJECT n_capture) <- S_release_exit.ALLOCATIONS)
$heap_owners($heap_graph(S_release_exit), HOBJECT n_capture) = 0
$fiber_capture_source_valid(S_release_exit, pfibercapture)
~$fiber_capture_live(S_release_exit, n_capture)
S_value_step = $drive_steps(S_release_exit, 1)
S_value_step.COMPLETION = BUDGET
S_value = S_value_step[.COMPLETION = NORMAL]
S_value.RESULT = KNOWN pvalue_done
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
~((HOBJECT n_fiber) <- S_done.ALLOCATIONS)
$heap_owners($heap_graph(S_done), HOBJECT n_capture) = 0
$from_factory_saved(S_done, n_factory)
$fiber_factory_saved_call(S_done, pconfigcall_factory, INTRINSIC_FIBER_SUSPEND, eps)
$fiber_capture_source_valid(S_done, pfibercapture)
~$fiber_capture_live(S_done, n_capture)
''') + [f'$outputs(S_done.EVENTS) = $ptascii("{expected}")'] + guards('S_done')
    controls = []
    for name, change in [('kind', '.KIND = INTRINSIC_FIBER_CURRENT'),
                         ('name', '.NAME = $ptascii("getCurrent")'),
                         ('input', '.INPUT = (n_fiber)')]:
        controls += [f'S_bad_{name} = S_invoke[.OBJECTS = $object_set(S_invoke.OBJECTS, n_capture, FIBERAPICLOSURE pfibercapture[{change}])]',
                     f'$heap_graph(S_bad_{name}) = $heap_graph(S_invoke)',
                     f'~$fiber_capture_live(S_bad_{name}, n_capture)',
                     f'~$call_descriptors_valid(S_bad_{name})']
    for name, change in [('line', '.LINE = 999'), ('owner', '.OWNER = (n_fiber)')]:
        controls += [f'pfiberfactory_bad_{name} = pfiberfactory[.CALL = pconfigcall_factory[{change}]]',
                     f'S_bad_{name} = S_invoke[.OBJECTS = $object_set(S_invoke.OBJECTS, n_capture, FIBERAPICLOSURE pfibercapture[.FACTORY = (pfiberfactory_bad_{name})])]',
                     f'$heap_graph(S_bad_{name}) = $heap_graph(S_invoke)',
                     f'~$fiber_capture_live(S_bad_{name}, n_capture)',
                     f'~$call_descriptors_valid(S_bad_{name})']
    controls += lines(r'''
pfiberfactory_alias = pfiberfactory[.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_class), ENTRY (KINT 1) (ALIAS n_method_cell)]]
S_alias = S_invoke[.OBJECTS = $object_set(S_invoke.OBJECTS, n_capture, FIBERAPICLOSURE pfibercapture[.FACTORY = (pfiberfactory_alias)])]
$heap_graph(S_alias) = $heap_graph(S_invoke)
~$fiber_capture_live(S_alias, n_capture)
~$call_descriptors_valid(S_alias)
''')
    for name, change in [('site', '.SITE = pconfigcall_factory.SITE'),
                         ('line', '.LINE = 999'),
                         ('sent', '.SENT = (PSTRING $ptascii("forged"))'),
                         ('sequence', '.SEQUENCE = 0')]:
        controls += [f'pfiberapi_bad_{name} = pfiberapi_suspend[{change}]',
                     f'S_continue_bad_{name} = S_continue[.TODO = (FIBER_CONTINUE pfiberapi_bad_{name}) :: (FIBER_CAPTURE_RESULT n_capture pconfigcall_suspend false) :: ptask_after_call*]',
                     f'$heap_graph(S_continue_bad_{name}) = $heap_graph(S_continue)',
                     f'~$fiber_continue_valid(S_continue_bad_{name}, pfiberapi_bad_{name})',
                     f'~$call_descriptors_valid(S_continue_bad_{name})']
    controls += lines(r'''
S_missing_result = S_continue[.TODO = (FIBER_CONTINUE pfiberapi_suspend) :: ptask_after_call*]
$heap_owners($heap_graph(S_missing_result), HOBJECT n_capture) = 0
$heap_valid($heap_graph(S_missing_result))
~$fiber_continue_valid(S_missing_result, pfiberapi_suspend)
~$call_descriptors_valid(S_missing_result)
''')
    checks = genuine + controls
    text = EXTRA + PREFIX[PREFIX.index('dec $outputs'):]
    text += '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks, len(genuine), len(controls)
