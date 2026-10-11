"""Literal current capture, immediate caller identity and distinct retirements."""
from error_handler_protocol import PREFIX


EXTRA = r'''
dec $current_capture_peer_stage(pstate, nat) : bool
def $current_capture_peer_stage(S, 0) = true
  -- if S.TODO = (SCOPED_CLASS phpType19 phpType20 phpType7* z) :: ptask*
  -- if $closure_current_capture(S[.COMPLETION = NORMAL], phpType19, $ptascii("getcurrent"), phpType7*, z)
def $current_capture_peer_stage(S, 1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_CLOSURE_CURRENT
def $current_capture_peer_stage(S, 2) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("picked")
  -- if S.RESULT = KNOWN PNULL
def $current_capture_peer_stage(S, 3) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("returned")
  -- if S.RESULT = KNOWN PNULL
def $current_capture_peer_stage(S, 4) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n) :: ptask*
def $current_capture_peer_stage(S, 5) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("caught")
  -- if S.RESULT = KNOWN PNULL
def $current_capture_peer_stage(S, n) = false -- otherwise
dec $current_capture_peer_seek(pstate, nat, nat) : pstate
def $current_capture_peer_seek(S, n_stage, n) = S
  -- if $current_capture_peer_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $current_capture_peer_seek(S, n_stage, n) = $current_capture_peer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$current_capture_peer_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $current_capture_peer_seek(S, n_stage, 0) = S
  -- if ~$current_capture_peer_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $current_capture_peer_seek(S, n_stage, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $current_capture_peer_without(pnode*, pnode) : pnode*
def $current_capture_peer_without(eps, pnode) = eps
def $current_capture_peer_without(pnode :: pnode_tail*, pnode) = $current_capture_peer_without(pnode_tail*, pnode)
def $current_capture_peer_without(pnode_head :: pnode_tail*, pnode) = pnode_head :: $current_capture_peer_without(pnode_tail*, pnode)
  -- if pnode_head =/= pnode
'''


def lines(text):
    return [line for line in text.strip().splitlines() if line]


def guards(state):
    return [f'$call_current_valid({state})', f'$call_frames_valid({state}, {state}.FRAMES)',
            f'$call_descriptors_valid({state})', f'$closure_state_valid({state})',
            f'$heap_valid($heap_graph({state}))']


def seek(state, previous, stage):
    return [f'{state}_reached = $current_capture_peer_seek({previous}, {stage}, 1000)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$current_capture_peer_stage({state}, {stage})']


def step(after, before):
    return [f'{after}_step = $drive_steps({before}, 1)',
            f'{after}_step.COMPLETION = BUDGET',
            f'{after} = {after}_step[.COMPLETION = NORMAL]']


def render(program, filename, expected, named=False, entry='main', shared=True):
    genuine = [f'S_begin = $php_run({program}, 0, {filename})', 'S_begin.COMPLETION = BUDGET']
    genuine += seek('S_capture', 'S_begin', 0)
    genuine += lines(r'''
S_capture.TODO = (SCOPED_CLASS phpType19 phpType20 phpType7* z_capture) :: ptask_capture*
S_capture.ORIGIN = (porigin_capture)
S_class = $scoped_class_prepare(S_capture, phpType19, z_capture)
S_class.COMPLETION = NORMAL
S_class.RESULT = KNOWN (PSTRING ptbytes_class)
$ptlc($typed_callable_name(ptbytes_class)) = $ptascii("closure")
$ppscoped_named(phpType19) /\ ~$ppscoped_keyword(phpType19)
$ppfirstclass(phpType7*)
$closure_current_capture_site(S_capture, porigin_capture)
$closure_current_capture(S_capture, phpType19, $ptascii("getcurrent"), phpType7*, z_capture)
$call_task_valid(S_capture, SCOPED_CLASS phpType19 phpType20 phpType7* z_capture)
S_capture.CURRENT = eps /\ S_capture.FRAMES = eps
$outputs(S_capture.EVENTS) = $ptascii("Q;")
n_api = |S_capture.OBJECTS|
''') + guards('S_capture') + step('S_minted', 'S_capture') + lines(r'''
S_minted.TODO = ptask_capture*
S_minted.RESULT = KNOWN (POBJECT n_api)
S_minted.OBJECTS = S_capture.OBJECTS ++ [INTRINSICCLOSURE INTRINSIC_CLOSURE_CURRENT]
S_minted.CURRENT = S_capture.CURRENT /\ S_minted.FRAMES = S_capture.FRAMES
(HOBJECT n_api) <- S_minted.ALLOCATIONS
$node_children(S_minted, HOBJECT n_api) = eps
$heap_owners($heap_graph(S_minted), HOBJECT n_api) = 1
$closure_callable(S_minted, n_api)
$closure_live_object_valid(S_minted, n_api)
$closure_static_api_owner_valid(S_minted, n_api)
''') + guards('S_minted')
    genuine += seek('S_config', 'S_minted', 1)
    genuine += lines(r'''
S_config.TODO = (CONFIG_INVOKE pconfigcall_current) :: ptask_config*
pconfigcall_current.KIND = INTRINSIC_CLOSURE_CURRENT
pconfigcall_current.OWNER = (n_api)
pconfigcall_current.SENT = eps /\ pconfigcall_current.INDEX = 0
pconfigcall_current.PACKS = eps /\ ~pconfigcall_current.NAMED
pconfigcall_current.SELECTION = (n_api)
S_config.OBJECTS[n_api] = INTRINSICCLOSURE INTRINSIC_CLOSURE_CURRENT
$config_invoke_valid(S_config, pconfigcall_current)
$call_task_valid(S_config, CONFIG_INVOKE pconfigcall_current)
$task_nodes(CONFIG_INVOKE pconfigcall_current) = [HOBJECT n_api]
$lookup(S_config.ENV, $ptascii("picked")) = (n_picked_cell)
S_config.STORE[n_picked_cell] = DEFINED (POBJECT n_api)
S_config.GLOBALTABLE = (psymboltable_global)
$lookup(psymboltable_global.ENV, $ptascii("api")) = (n_api_cell)
S_config.STORE[n_api_cell] = DEFINED PNULL
$lookup(psymboltable_global.ENV, $ptascii("body")) = (n_body_cell)
S_config.STORE[n_body_cell] = DEFINED PNULL
$lookup(psymboltable_global.ENV, $ptascii("weakApi")) = (n_weak_api_cell)
S_config.STORE[n_weak_api_cell] = DEFINED (POBJECT n_weak_api)
$weakref_get(S_config, n_weak_api) = POBJECT n_api
$lookup(psymboltable_global.ENV, $ptascii("weakBody")) = (n_weak_body_cell)
S_config.STORE[n_weak_body_cell] = DEFINED (POBJECT n_weak_body)
$weakref_get(S_config, n_weak_body) = POBJECT n_body
n_api =/= n_body
$object_body(S_config.OBJECTS[n_body]) = REALCLOSURE porigin_body eps eps
$node_children(S_config, HOBJECT n_body) = eps
$heap_owners($heap_graph(S_config), HOBJECT n_api) = 2
$heap_owners($heap_graph(S_config), HOBJECT n_body) = 1
S_config.FIBERSEQ = 1
~$destructor_operational(S_config)
S_config.DESTRUCTION.OPERATIONS = eps /\ S_config.DESTRUCTION.RELEASES = eps
''') + guards('S_config')
    if not named:
        genuine += positive()
    else:
        genuine += negative()
    genuine += lines(r'''
S_zero = $drive_steps(S_config, 0)
S_zero = S_config[.COMPLETION = BUDGET]
S_done = $drive(S_zero[.COMPLETION = NORMAL], 1500)
S_done.COMPLETION = NORMAL
S_done.CURRENT = eps /\ S_done.FRAMES = eps
S_done.TODO = eps
S_done.TRACE = eps
~(HOBJECT n_api <- S_done.ALLOCATIONS)
~(HOBJECT n_body <- S_done.ALLOCATIONS)
$weakref_get(S_done, n_weak_api) = PNULL
$weakref_get(S_done, n_weak_body) = PNULL
S_done = $drive(S_begin[.COMPLETION = NORMAL], 1500)
''') + [f'$outputs(S_done.EVENTS) = $ptascii("{expected}")'] + guards('S_done')
    controls = [] if named else lines(r'''
~$closure_current_capture_site(S_capture, PORIGIN 999 eps)
~$closure_current_capture(S_capture[.COMPLETION = BUDGET], phpType19, $ptascii("getcurrent"), phpType7*, z_capture)
~$closure_current_capture(S_capture[.ORIGIN = eps], phpType19, $ptascii("getcurrent"), phpType7*, z_capture)
~$closure_current_capture(S_capture, phpType19, $ptascii("fromcallable"), phpType7*, z_capture)
~$closure_current_capture(S_capture, phpType19, $ptascii("getcurrent"), eps, z_capture)
~$closure_current_capture(S_capture, phpType19, $ptascii("getcurrent"), phpType7*, $(z_capture + 1))
~$closure_callable(S_config[.ALLOCATIONS = $current_capture_peer_without(S_config.ALLOCATIONS, HOBJECT n_api)], n_api)
~$closure_live_object_valid(S_config[.ALLOCATIONS = $current_capture_peer_without(S_config.ALLOCATIONS, HOBJECT n_api)], n_api)
~$config_invoke_valid(S_config[.ORIGIN = eps], pconfigcall_current)
~$config_invoke_valid(S_config, pconfigcall_current[.SITE = PORIGIN 999 eps])
~$config_invoke_valid(S_config, pconfigcall_current[.LINE = $(pconfigcall_current.LINE + 1)])
~$config_invoke_valid(S_config, pconfigcall_current[.INDEX = 1])
~$config_invoke_valid(S_config, pconfigcall_current[.SENT = [NAMED_SENT (KNOWN (PINT 7))]])
~$config_invoke_valid(S_config, pconfigcall_current[.OWNER = eps])
~$config_invoke_valid(S_config, pconfigcall_current[.OWNER = (n_body)])
~$config_invoke_valid(S_config, pconfigcall_current[.KIND = INTRINSIC_GET_CLASS])
~$config_invoke_valid(S_config[.OBJECTS[n_api] = INTRINSICCLOSURE INTRINSIC_GET_CLASS], pconfigcall_current)
$closure_current_object(S_config[.CURRENT = eps]) = eps
$closure_current_object(S_config[.CURRENT = (pcallcontext_body[.TARGET = CLOSURE_TARGET n_api][.INSTANCE = (n_api)])]) = eps
~$call_current_valid(S_config[.CURRENT = (pcallcontext_body[.INSTANCE = (n_api)])])
S_bad_config = S_config[.TODO = (CONFIG_INVOKE pconfigcall_current[.OWNER = (n_body)]) :: ptask_config*]
~$call_descriptors_valid(S_bad_config)
''')
    checks = genuine + controls
    prefix = PREFIX[PREFIX.index('dec $outputs'):]
    text = (prefix + EXTRA if shared else '') + f'\ndec ${entry}() : bool\ndef ${entry}() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks, len(genuine), len(controls)


def positive():
    return lines(r'''
$outputs(S_config.EVENTS) = $ptascii("Q;A;B;C:held;")
S_config.CURRENT = (pcallcontext_body)
pcallcontext_body.TARGET = CLOSURE_TARGET n_body
pcallcontext_body.INSTANCE = (n_body)
S_config.FRAMES = [pframe_main]
pframe_main.CONTEXT = eps /\ pframe_main.LOCALS = eps
$closure_current_object(S_config) = (n_body)
''') + step('S_result', 'S_config') + lines(r'''
S_result.RESULT = KNOWN (POBJECT n_body)
S_result.TODO = ptask_config*
S_result.CURRENT = S_config.CURRENT /\ S_result.FRAMES = S_config.FRAMES
S_result.OBJECTS = S_config.OBJECTS /\ S_result.ARRAYS = S_config.ARRAYS
S_result.STORE = S_config.STORE /\ S_result.ALLOCATIONS = S_config.ALLOCATIONS
$heap_owners($heap_graph(S_result), HOBJECT n_api) = 1
$heap_owners($heap_graph(S_result), HOBJECT n_body) = 2
$closure_current_object(S_result) = (n_body)
''') + guards('S_result') + seek('S_picked', 'S_result', 2) + lines(r'''
S_picked.TODO = (WRITE_NAME $ptascii("picked") z_picked) :: ptask_picked*
S_picked.STORE[n_picked_cell] = DEFINED (POBJECT n_api)
S_picked.CURRENT = (pcallcontext_body)
$lookup(S_picked.ENV, $ptascii("current")) = (n_current_cell)
S_picked.STORE[n_current_cell] = DEFINED (POBJECT n_body)
$outputs(S_picked.EVENTS) = $ptascii("Q;A;B;C:held;I:same;")
$heap_owners($heap_graph(S_picked), HOBJECT n_api) = 1
$heap_owners($heap_graph(S_picked), HOBJECT n_body) = 2
~$destructor_operational(S_picked)
''') + step('S_api_gone', 'S_picked') + lines(r'''
S_api_gone.TODO = ptask_picked*
S_api_gone.STORE[n_picked_cell] = DEFINED PNULL
S_api_gone.RESULT = KNOWN PNULL
S_api_gone.CURRENT = S_picked.CURRENT /\ S_api_gone.FRAMES = S_picked.FRAMES
S_api_gone.EVENTS = S_picked.EVENTS
S_api_gone.DESTRUCTION.OPERATIONS = eps /\ S_api_gone.DESTRUCTION.RELEASES = eps
~(HOBJECT n_api <- S_api_gone.ALLOCATIONS)
$heap_owners($heap_graph(S_api_gone), HOBJECT n_api) = 0
$heap_owners($heap_graph(S_api_gone), HOBJECT n_body) = 2
$weakref_get(S_api_gone, n_weak_api) = PNULL
$weakref_get(S_api_gone, n_weak_body) = POBJECT n_body
''') + guards('S_api_gone') + seek('S_returned', 'S_api_gone', 3) + lines(r'''
S_returned.TODO = (WRITE_NAME $ptascii("returned") z_returned) :: ptask_returned*
S_returned.CURRENT = eps /\ S_returned.FRAMES = eps
$lookup(S_returned.ENV, $ptascii("returned")) = (n_returned_cell)
S_returned.STORE[n_returned_cell] = DEFINED (POBJECT n_body)
$outputs(S_returned.EVENTS) = $ptascii("Q;A;B;C:held;I:same;C:gone;P:held;R:same;H:held;")
$heap_owners($heap_graph(S_returned), HOBJECT n_body) = 1
~(HOBJECT n_api <- S_returned.ALLOCATIONS)
~$destructor_operational(S_returned)
''') + step('S_body_gone', 'S_returned') + lines(r'''
S_body_gone.TODO = ptask_returned*
S_body_gone.STORE[n_returned_cell] = DEFINED PNULL
S_body_gone.RESULT = KNOWN PNULL
S_body_gone.EVENTS = S_returned.EVENTS
S_body_gone.DESTRUCTION.OPERATIONS = eps /\ S_body_gone.DESTRUCTION.RELEASES = eps
~(HOBJECT n_body <- S_body_gone.ALLOCATIONS)
$heap_owners($heap_graph(S_body_gone), HOBJECT n_body) = 0
$weakref_get(S_body_gone, n_weak_body) = PNULL
''') + guards('S_body_gone')


def negative():
    checks = lines(r'''
$outputs(S_config.EVENTS) = $ptascii("Q;A;B;N;C:held;")
S_config.CURRENT = (pcallcontext_named)
pcallcontext_named.TARGET = porigin_named
pcallcontext_named.INSTANCE = eps /\ pcallcontext_named.RECEIVER = eps
pcallcontext_named.ARGC = 0
S_config.FRAMES = [pframe_body, pframe_main]
pframe_body.CONTEXT = (pcallcontext_body)
pcallcontext_body.TARGET = CLOSURE_TARGET n_body
pcallcontext_body.INSTANCE = (n_body)
pframe_main.CONTEXT = eps /\ pframe_main.LOCALS = eps
$closure_current_object(S_config) = eps
ptraceframe* = $source_trace_prefixed(S_config, $config_trace_frames(S_config, pconfigcall_current, eps))
ptraceframe* = [ptraceframe_api, ptraceframe_named, ptraceframe_body]
ptraceframe_api.FUNCTION = $ptascii("getCurrent")
ptraceframe_api.CLASS = ($ptascii("Closure"))
ptraceframe_api.TYPE = ($ptascii("::"))
ptraceframe_api.ARGS = eps /\ ptraceframe_api.HASARGS
ptraceframe_named.FUNCTION = pcallcontext_named.NAME
ptraceframe_named.ARGS = eps /\ ptraceframe_named.HASARGS
ptraceframe_body.FUNCTION = pcallcontext_body.NAME
ptraceframe_body.ARGS = [(KINT 0, PINT 7)] /\ ptraceframe_body.HASARGS
S_received = $config_receive(S_config, pconfigcall_current)
S_received.COMPLETION = THROWING n_error
S_received.TODO = S_config.TODO
S_received.CURRENT = S_config.CURRENT /\ S_received.FRAMES = S_config.FRAMES
S_received.OBJECTS[n_error] = THROWABLE pthrowable
pthrowable.KIND = "Error"
$throwable_field(S_received, n_error, "message") = PSTRING $ptascii("Current function is not a closure")
$throwable_field(S_received, n_error, "trace") = PARRAY n_trace
S_received.RESULT = KNOWN (PARRAY n_trace)
S_received.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame_api)), ENTRY (KINT 1) (DIRECT (PARRAY n_frame_named)), ENTRY (KINT 2) (DIRECT (PARRAY n_frame_body))]
$node_children(S_received, HOBJECT n_error) = [HARRAY n_trace]
$node_children(S_received, HARRAY n_trace) = [HARRAY n_frame_api, HARRAY n_frame_named, HARRAY n_frame_body]
$heap_owners($heap_graph(S_received), HOBJECT n_error) = 1
$heap_owners($heap_graph(S_received), HARRAY n_trace) = 2
$trace_graph_valid(S_received, n_trace)
''')
    for label, args in [('api', 'eps'), ('named', 'eps'), ('body', '[ENTRY (KINT 0) (DIRECT (PINT 7))]')]:
        checks += [f'$entry_lookup(S_received.ARRAYS[n_frame_{label}].ITEMS, KSTRING $ptascii("function")) = (DIRECT (PSTRING ptraceframe_{label}.FUNCTION))',
                   f'$entry_lookup(S_received.ARRAYS[n_frame_{label}].ITEMS, KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args_{label}))',
                   f'S_received.ARRAYS[n_args_{label}].ITEMS = {args}',
                   f'$node_children(S_received, HARRAY n_frame_{label}) = [HARRAY n_args_{label}]',
                   f'$node_children(S_received, HARRAY n_args_{label}) = eps',
                   f'$heap_owners($heap_graph(S_received), HARRAY n_frame_{label}) = 1',
                   f'$heap_owners($heap_graph(S_received), HARRAY n_args_{label}) = 1']
    checks += step('S_rejected', 'S_config') + lines(r'''
S_rejected.TODO = (THROW_SEARCH n_error) :: ptask_config*
S_rejected.CURRENT = S_config.CURRENT /\ S_rejected.FRAMES = S_config.FRAMES
S_rejected.RESULT = KNOWN PNULL
S_rejected.OBJECTS = S_received.OBJECTS /\ S_rejected.ARRAYS = S_received.ARRAYS
S_rejected.OBJECTPROPS = S_received.OBJECTPROPS
S_rejected.EVENTS = S_config.EVENTS
S_rejected.DESTRUCTION.OPERATIONS = eps /\ S_rejected.DESTRUCTION.RELEASES = eps
$heap_owners($heap_graph(S_rejected), HOBJECT n_api) = 1
$heap_owners($heap_graph(S_rejected), HOBJECT n_body) = 1
$heap_owners($heap_graph(S_rejected), HOBJECT n_error) = 1
$heap_owners($heap_graph(S_rejected), HARRAY n_trace) = 1
$node_children(S_rejected, HOBJECT n_error) = [HARRAY n_trace]
''') + guards('S_rejected') + seek('S_catch', 'S_rejected', 4) + lines(r'''
S_catch.TODO = (CATCH_BIND porigin_try n_index n_error) :: ptask_catch*
S_catch.CURRENT = eps /\ S_catch.FRAMES = eps
$outputs(S_catch.EVENTS) = $ptascii("Q;A;B;N;C:held;")
~(HOBJECT n_api <- S_catch.ALLOCATIONS)
~(HOBJECT n_body <- S_catch.ALLOCATIONS)
$heap_owners($heap_graph(S_catch), HOBJECT n_api) = 0
$heap_owners($heap_graph(S_catch), HOBJECT n_body) = 0
$heap_owners($heap_graph(S_catch), HOBJECT n_error) = 1
$heap_owners($heap_graph(S_catch), HARRAY n_trace) = 1
$trace_graph_valid(S_catch, n_trace)
$weakref_get(S_catch, n_weak_api) = PNULL
$weakref_get(S_catch, n_weak_body) = PNULL
''') + step('S_caught', 'S_catch') + lines(r'''
$lookup(S_caught.ENV, $ptascii("caught")) = (n_caught_cell)
S_caught.STORE[n_caught_cell] = DEFINED (POBJECT n_error)
$heap_owners($heap_graph(S_caught), HOBJECT n_error) = 1
$heap_owners($heap_graph(S_caught), HARRAY n_trace) = 1
''') + guards('S_caught') + seek('S_clear', 'S_caught', 5) + lines(r'''
S_clear.TODO = (WRITE_NAME $ptascii("caught") z_clear) :: ptask_clear*
S_clear.STORE[n_caught_cell] = DEFINED (POBJECT n_error)
$lookup(S_clear.ENV, $ptascii("weakError")) = (n_weak_error_cell)
S_clear.STORE[n_weak_error_cell] = DEFINED (POBJECT n_weak_error)
$weakref_get(S_clear, n_weak_error) = POBJECT n_error
$outputs(S_clear.EVENTS) = $ptascii("Q;A;B;N;C:held;E:Error:Current function is not a closure;C:gone;B:gone;E:held;")
$heap_owners($heap_graph(S_clear), HOBJECT n_error) = 1
~$destructor_operational(S_clear)
''') + step('S_error_gone', 'S_clear') + lines(r'''
S_error_gone.TODO = ptask_clear*
S_error_gone.STORE[n_caught_cell] = DEFINED PNULL
S_error_gone.RESULT = KNOWN PNULL
S_error_gone.EVENTS = S_clear.EVENTS
S_error_gone.DESTRUCTION.OPERATIONS = eps /\ S_error_gone.DESTRUCTION.RELEASES = eps
~(HOBJECT n_error <- S_error_gone.ALLOCATIONS)
~(HARRAY n_trace <- S_error_gone.ALLOCATIONS)
$heap_owners($heap_graph(S_error_gone), HOBJECT n_error) = 0
$weakref_get(S_error_gone, n_weak_error) = PNULL
''')
    for label in ['api', 'named', 'body']:
        checks += [f'~(HARRAY n_frame_{label} <- S_error_gone.ALLOCATIONS)',
                   f'~(HARRAY n_args_{label} <- S_error_gone.ALLOCATIONS)']
    return checks + guards('S_error_gone')
