"""Selected current API pin across a genuine argument-side global write."""
from error_handler_protocol import PREFIX

EXTRA = r'''
dec $current_argument_stage(pstate, nat) : bool
def $current_argument_stage(S, 0) = true
  -- if S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask*
  -- if S_value = $resolve_at(S[.COMPLETION = NORMAL], S.RESULT, z_init)
  -- if S_value.RESULT = KNOWN (POBJECT n)
  -- if S_value.OBJECTS[n] = INTRINSICCLOSURE INTRINSIC_CLOSURE_CURRENT
def $current_argument_stage(S, 1) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_CLOSURE_CURRENT
  -- if pconfigcall.INDEX = 0
def $current_argument_stage(S, 2) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("api")
  -- if S.RESULT = KNOWN PNULL
  -- if S.CURRENT = (pcallcontext)
  -- if $ptlc(pcallcontext.NAME) = $ptascii("retireselectedcurrentargument")
def $current_argument_stage(S, 3) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_CLOSURE_CURRENT
def $current_argument_stage(S, 4) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n) :: ptask*
def $current_argument_stage(S, 5) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("caught")
  -- if S.RESULT = KNOWN PNULL
def $current_argument_stage(S, n) = false -- otherwise
dec $current_argument_seek(pstate, nat, nat) : pstate
def $current_argument_seek(S, n_stage, n) = S
  -- if $current_argument_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $current_argument_seek(S, n_stage, n) = $current_argument_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$current_argument_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $current_argument_seek(S, n_stage, 0) = S
  -- if ~$current_argument_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $current_argument_seek(S, n_stage, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $current_argument_saved(ptask*) : pconfigcall?
dec $current_argument_saved_head(ptask) : bool
def $current_argument_saved_head(AT porigin ptask) = true
def $current_argument_saved_head(CONFIG_SEND pconfigcall) = true
  -- if pconfigcall.KIND = INTRINSIC_CLOSURE_CURRENT
def $current_argument_saved_head(ptask) = false -- otherwise
def $current_argument_saved((AT porigin ptask) :: ptask_tail*) = $current_argument_saved(ptask :: ptask_tail*)
def $current_argument_saved((CONFIG_SEND pconfigcall) :: ptask_tail*) = (pconfigcall)
  -- if pconfigcall.KIND = INTRINSIC_CLOSURE_CURRENT
def $current_argument_saved(ptask :: ptask_tail*) = $current_argument_saved(ptask_tail*)
  -- if ~$current_argument_saved_head(ptask)
def $current_argument_saved(eps) = eps
'''


def lines(text):
    return [line for line in text.strip().splitlines() if line]


def guards(state):
    return [f'$call_current_valid({state})', f'$call_frames_valid({state}, {state}.FRAMES)',
            f'$call_descriptors_valid({state})', f'$closure_state_valid({state})',
            f'$heap_valid($heap_graph({state}))']


def seek(state, previous, stage):
    return [f'{state}_reached = $current_argument_seek({previous}, {stage}, 1000)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$current_argument_stage({state}, {stage})']


def step(after, before):
    return [f'{after}_step = $drive_steps({before}, 1)', f'{after}_step.COMPLETION = BUDGET',
            f'{after} = {after}_step[.COMPLETION = NORMAL]']


def function(entry, genuine, controls, shared):
    text = (PREFIX[PREFIX.index('dec $outputs'):] + EXTRA if shared else '')
    text += '\ndec $' + entry + '() : bool\ndef $' + entry + '() = true\n'
    checks = genuine + controls
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks, len(genuine), len(controls)


def render(program, filename, expected, captured=True, entry='main', shared=True):
    genuine = [f'S_begin = $php_run({program}, 0, {filename})', 'S_begin.COMPLETION = BUDGET']
    if captured:
        genuine += seek('S_lookup', 'S_begin', 0) + lines(r'''
S_lookup.TODO = (CALL_DYNAMIC porigin_call z_init z_call) :: ptask_lookup*
S_lookup.ORIGIN = (porigin_call)
$dynamic_site(S_lookup, (porigin_call))
$dynamic_fixed_name(S_lookup, porigin_call) = eps
$call_task_valid(S_lookup, CALL_DYNAMIC porigin_call z_init z_call)
S_value = $resolve_at(S_lookup[.TODO = ptask_lookup*], S_lookup.RESULT, z_init)
S_value.COMPLETION = NORMAL
S_value.RESULT = KNOWN (POBJECT n_api)
S_value.OBJECTS[n_api] = INTRINSICCLOSURE INTRINSIC_CLOSURE_CURRENT
$closure_callable(S_value, n_api)
$outputs(S_lookup.EVENTS) = $ptascii("Q;A;B;")
''') + step('S_minted', 'S_lookup') + lines(r'''
S_minted = $config_prepare(S_value, INTRINSIC_CLOSURE_CURRENT, z_call, (n_api), porigin_call)
S_minted.TODO = (CONFIG_ARGS pconfigcall_start) :: ptask_lookup*
S_minted.RESULT = KNOWN PNULL
S_minted.CURRENT = S_lookup.CURRENT /\ S_minted.FRAMES = S_lookup.FRAMES
S_minted.OBJECTS = S_lookup.OBJECTS /\ S_minted.ARRAYS = S_lookup.ARRAYS
S_minted.STORE = S_lookup.STORE /\ S_minted.ALLOCATIONS = S_lookup.ALLOCATIONS
''')
    else:
        genuine += seek('S_minted', 'S_begin', 1) + lines(r'''
S_minted.TODO = (CONFIG_ARGS pconfigcall_start) :: ptask_minted*
S_minted.GLOBALTABLE = (psymboltable_minted)
$lookup(psymboltable_minted.ENV, $ptascii("api")) = (n_api_cell)
S_minted.STORE[n_api_cell] = DEFINED (POBJECT n_api)
pconfigcall_start.OWNER = eps /\ pconfigcall_start.SELECTION = eps
~$closure_current_config_tag(pconfigcall_start)
$task_nodes(CONFIG_ARGS pconfigcall_start) = eps
$closure_current_site(S_minted, pconfigcall_start.SITE) /\ ~$closure_current_method_site(S_minted, pconfigcall_start.SITE)
''')
    genuine += lines(r'''
pconfigcall_start.KIND = INTRINSIC_CLOSURE_CURRENT
pconfigcall_start.INDEX = 0 /\ pconfigcall_start.SENT = eps
pconfigcall_start.PACKS = eps /\ ~pconfigcall_start.NAMED
$call_task_valid(S_minted, CONFIG_ARGS pconfigcall_start)
S_minted.OBJECTS[n_api] = INTRINSICCLOSURE INTRINSIC_CLOSURE_CURRENT
S_minted.CURRENT = (pcallcontext_body)
pcallcontext_body.TARGET = CLOSURE_TARGET n_body
pcallcontext_body.INSTANCE = (n_body)
pcallcontext_body.ARGC = 1
S_minted.FRAMES = [pframe_main]
pframe_main.CONTEXT = eps /\ pframe_main.LOCALS = eps
S_minted.GLOBALTABLE = (psymboltable_global)
$lookup(psymboltable_global.ENV, $ptascii("api")) = (n_api_cell)
S_minted.STORE[n_api_cell] = DEFINED (POBJECT n_api)
$lookup(psymboltable_global.ENV, $ptascii("body")) = (n_body_cell)
S_minted.STORE[n_body_cell] = DEFINED PNULL
$lookup(psymboltable_global.ENV, $ptascii("weakApi")) = (n_weak_api_cell)
S_minted.STORE[n_weak_api_cell] = DEFINED (POBJECT n_weak_api)
$lookup(psymboltable_global.ENV, $ptascii("weakBody")) = (n_weak_body_cell)
S_minted.STORE[n_weak_body_cell] = DEFINED (POBJECT n_weak_body)
$weakref_get(S_minted, n_weak_api) = POBJECT n_api
$weakref_get(S_minted, n_weak_body) = POBJECT n_body
$object_body(S_minted.OBJECTS[n_body]) = REALCLOSURE porigin_body eps eps
$node_children(S_minted, HOBJECT n_body) = eps
$heap_owners($heap_graph(S_minted), HOBJECT n_body) = 1
$outputs(S_minted.EVENTS) = $ptascii("Q;A;B;")
''')
    if captured:
        genuine += lines(r'''
pconfigcall_start.OWNER = (n_api) /\ pconfigcall_start.SELECTION = (n_api)
pconfigcall_start.SITE = porigin_call /\ pconfigcall_start.LINE = z_call
$closure_current_config_tag(pconfigcall_start)
$task_nodes(CONFIG_ARGS pconfigcall_start) = [HOBJECT n_api]
$selected_task_nonce(CONFIG_ARGS pconfigcall_start) = eps
$heap_owners($heap_graph(S_minted), HOBJECT n_api) = 2
''')
    else:
        genuine += ['$heap_owners($heap_graph(S_minted), HOBJECT n_api) = 1']
    genuine += guards('S_minted') + seek('S_write', 'S_minted', 2) + lines(r'''
S_write.TODO = (WRITE_NAME $ptascii("api") z_write) :: ptask_write*
S_write.RESULT = KNOWN PNULL
S_write.CURRENT = (pcallcontext_helper)
pcallcontext_helper.INSTANCE = eps /\ pcallcontext_helper.RECEIVER = eps
$ptlc(pcallcontext_helper.NAME) = $ptascii("retireselectedcurrentargument")
S_write.FRAMES = [pframe_body, pframe_main]
pframe_body.CONTEXT = (pcallcontext_body)
$current_argument_saved(pframe_body.TODO) = (pconfigcall_saved)
pconfigcall_saved = pconfigcall_start
S_write.STORE[n_api_cell] = DEFINED (POBJECT n_api)
S_write.STORE[n_body_cell] = DEFINED PNULL
$outputs(S_write.EVENTS) = $ptascii("Q;A;B;S;")
S_write.FIBERSEQ = 1
~$destructor_operational(S_write)
S_write.DESTRUCTION.OPERATIONS = eps /\ S_write.DESTRUCTION.RELEASES = eps
$heap_owners($heap_graph(S_write), HOBJECT n_body) = 1
''') + [f'$heap_owners($heap_graph(S_write), HOBJECT n_api) = {2 if captured else 1}']
    genuine += guards('S_write') + step('S_cleared', 'S_write') + lines(r'''
S_cleared.TODO = ptask_write*
S_cleared.RESULT = KNOWN PNULL
S_cleared.STORE[n_api_cell] = DEFINED PNULL
S_cleared.CURRENT = S_write.CURRENT /\ S_cleared.FRAMES = S_write.FRAMES
S_cleared.EVENTS = S_write.EVENTS
S_cleared.DESTRUCTION.OPERATIONS = eps /\ S_cleared.DESTRUCTION.RELEASES = eps
$heap_owners($heap_graph(S_cleared), HOBJECT n_body) = 1
''')
    if captured:
        genuine += lines(r'''
(HOBJECT n_api) <- S_cleared.ALLOCATIONS
$heap_owners($heap_graph(S_cleared), HOBJECT n_api) = 1
$weakref_get(S_cleared, n_weak_api) = POBJECT n_api
$task_nodes(CONFIG_SEND pconfigcall_saved) = [HOBJECT n_api]
''')
    else:
        genuine += lines(r'''
~(HOBJECT n_api <- S_cleared.ALLOCATIONS)
$heap_owners($heap_graph(S_cleared), HOBJECT n_api) = 0
$weakref_get(S_cleared, n_weak_api) = PNULL
$task_nodes(CONFIG_SEND pconfigcall_saved) = eps
''')
    genuine += guards('S_cleared') + seek('S_config', 'S_cleared', 3) + lines(r'''
S_config.TODO = (CONFIG_INVOKE pconfigcall_current) :: ptask_config*
pconfigcall_current = pconfigcall_start[.INDEX = 1][.SENT = [NAMED_SENT (KNOWN (PINT 7))]]
$config_invoke_valid(S_config, pconfigcall_current)
$call_task_valid(S_config, CONFIG_INVOKE pconfigcall_current)
S_config.CURRENT = (pcallcontext_body) /\ S_config.FRAMES = [pframe_main]
S_config.STORE[n_api_cell] = DEFINED PNULL
$heap_owners($heap_graph(S_config), HOBJECT n_body) = 1
S_config.RESULT = KNOWN PNULL
S_config.DESTRUCTION.OPERATIONS = eps /\ S_config.DESTRUCTION.RELEASES = eps
''') + [f'$outputs(S_config.EVENTS) = $ptascii("Q;A;B;S;C:{"held" if captured else "gone"};")',
       f'$heap_owners($heap_graph(S_config), HOBJECT n_api) = {1 if captured else 0}']
    genuine += guards('S_config')
    if captured:
        genuine += error_lifetime()
    genuine += lines(r'''
S_zero = $drive_steps(S_config, 0)
S_zero = S_config[.COMPLETION = BUDGET]
S_done = $drive(S_zero[.COMPLETION = NORMAL], 1500)
S_done.COMPLETION = NORMAL
S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps
S_done.TRACE = eps
~(HOBJECT n_api <- S_done.ALLOCATIONS)
~(HOBJECT n_body <- S_done.ALLOCATIONS)
$weakref_get(S_done, n_weak_api) = PNULL
$weakref_get(S_done, n_weak_body) = PNULL
S_done = $drive(S_begin[.COMPLETION = NORMAL], 1500)
''') + [f'$outputs(S_done.EVENTS) = $ptascii("{expected}")'] + guards('S_done')
    controls = malformed() if captured else lines(r'''
pconfigcall_forged = pconfigcall_start[.OWNER = (n_api)][.SELECTION = (n_api)]
$closure_callable(S_minted, n_api)
$closure_current_config_tag(pconfigcall_forged)
~$config_selected_valid(S_minted, pconfigcall_forged)
~$call_task_valid(S_minted, CONFIG_ARGS pconfigcall_forged)
S_forged = $config_prepare(S_minted[.RESULT = KNOWN (POBJECT n_api)], INTRINSIC_CLOSURE_CURRENT, pconfigcall_start.LINE, (n_api), pconfigcall_start.SITE)
S_forged.TODO = (CONFIG_ARGS pconfigcall_untagged) :: S_minted.TODO
pconfigcall_untagged.SELECTION = eps
~$closure_current_config_tag(pconfigcall_untagged)
''')
    return function(entry, genuine, controls, shared)


def error_lifetime():
    checks = lines(r'''
ptraceframe* = $source_trace_prefixed(S_config, $config_trace_frames(S_config, pconfigcall_current, [PINT 7]))
ptraceframe* = [ptraceframe_api, ptraceframe_body]
ptraceframe_api.FUNCTION = $ptascii("getCurrent")
ptraceframe_api.CLASS = ($ptascii("Closure")) /\ ptraceframe_api.TYPE = ($ptascii("::"))
ptraceframe_api.ARGS = [(KINT 0, PINT 7)] /\ ptraceframe_api.HASARGS
ptraceframe_body.FUNCTION = pcallcontext_body.NAME
ptraceframe_body.ARGS = [(KINT 0, PINT 7)] /\ ptraceframe_body.HASARGS
S_received = $config_receive(S_config, pconfigcall_current)
S_received.COMPLETION = THROWING n_error
S_received.TODO = S_config.TODO
S_received.OBJECTS[n_error] = THROWABLE pthrowable
pthrowable.KIND = "ArgumentCountError"
$throwable_field(S_received, n_error, "message") = PSTRING $ptascii("Closure::getCurrent() expects exactly 0 arguments, 1 given")
$throwable_field(S_received, n_error, "trace") = PARRAY n_trace
S_received.RESULT = KNOWN (PARRAY n_trace)
S_received.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame_api)), ENTRY (KINT 1) (DIRECT (PARRAY n_frame_body))]
$node_children(S_received, HOBJECT n_error) = [HARRAY n_trace]
$node_children(S_received, HARRAY n_trace) = [HARRAY n_frame_api, HARRAY n_frame_body]
$heap_owners($heap_graph(S_received), HOBJECT n_api) = 1
$heap_owners($heap_graph(S_received), HOBJECT n_error) = 1
$heap_owners($heap_graph(S_received), HARRAY n_trace) = 2
$trace_graph_valid(S_received, n_trace)
''')
    for label in ['api', 'body']:
        checks += [f'$entry_lookup(S_received.ARRAYS[n_frame_{label}].ITEMS, KSTRING $ptascii("function")) = (DIRECT (PSTRING ptraceframe_{label}.FUNCTION))',
                   f'$entry_lookup(S_received.ARRAYS[n_frame_{label}].ITEMS, KSTRING $ptascii("args")) = (DIRECT (PARRAY n_args_{label}))',
                   f'S_received.ARRAYS[n_args_{label}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
                   f'$node_children(S_received, HARRAY n_frame_{label}) = [HARRAY n_args_{label}]',
                   f'$node_children(S_received, HARRAY n_args_{label}) = eps']
    checks += step('S_rejected', 'S_config') + lines(r'''
S_rejected.TODO = (THROW_SEARCH n_error) :: ptask_config*
S_rejected.RESULT = KNOWN PNULL
S_rejected.CURRENT = S_config.CURRENT /\ S_rejected.FRAMES = S_config.FRAMES
S_rejected.OBJECTS = S_received.OBJECTS /\ S_rejected.ARRAYS = S_received.ARRAYS
S_rejected.OBJECTPROPS = S_received.OBJECTPROPS
S_rejected.EVENTS = S_config.EVENTS
S_rejected.DESTRUCTION.OPERATIONS = eps /\ S_rejected.DESTRUCTION.RELEASES = eps
~(HOBJECT n_api <- S_rejected.ALLOCATIONS)
$heap_owners($heap_graph(S_rejected), HOBJECT n_api) = 0
$weakref_get(S_rejected, n_weak_api) = PNULL
$heap_owners($heap_graph(S_rejected), HOBJECT n_body) = 1
$heap_owners($heap_graph(S_rejected), HOBJECT n_error) = 1
$heap_owners($heap_graph(S_rejected), HARRAY n_trace) = 1
''') + guards('S_rejected') + seek('S_catch', 'S_rejected', 4) + lines(r'''
S_catch.TODO = (CATCH_BIND porigin_try n_index n_error) :: ptask_catch*
S_catch.CURRENT = eps /\ S_catch.FRAMES = eps
S_catch.EVENTS = S_config.EVENTS
~(HOBJECT n_api <- S_catch.ALLOCATIONS)
~(HOBJECT n_body <- S_catch.ALLOCATIONS)
$heap_owners($heap_graph(S_catch), HOBJECT n_body) = 0
$heap_owners($heap_graph(S_catch), HOBJECT n_error) = 1
$heap_owners($heap_graph(S_catch), HARRAY n_trace) = 1
$trace_graph_valid(S_catch, n_trace)
''') + step('S_caught', 'S_catch') + lines(r'''
$lookup(S_caught.ENV, $ptascii("caught")) = (n_caught_cell)
S_caught.STORE[n_caught_cell] = DEFINED (POBJECT n_error)
$heap_owners($heap_graph(S_caught), HOBJECT n_error) = 1
''') + seek('S_clear', 'S_caught', 5) + lines(r'''
S_clear.TODO = (WRITE_NAME $ptascii("caught") z_clear) :: ptask_clear*
S_clear.STORE[n_caught_cell] = DEFINED (POBJECT n_error)
$lookup(S_clear.ENV, $ptascii("weakError")) = (n_weak_error_cell)
S_clear.STORE[n_weak_error_cell] = DEFINED (POBJECT n_weak_error)
$weakref_get(S_clear, n_weak_error) = POBJECT n_error
$outputs(S_clear.EVENTS) = $ptascii("Q;A;B;S;C:held;E:ArgumentCountError:Closure::getCurrent() expects exactly 0 arguments, 1 given;C:gone;B:gone;E:held;")
~$destructor_operational(S_clear)
''') + step('S_error_gone', 'S_clear') + lines(r'''
S_error_gone.TODO = ptask_clear*
S_error_gone.RESULT = KNOWN PNULL
S_error_gone.STORE[n_caught_cell] = DEFINED PNULL
S_error_gone.EVENTS = S_clear.EVENTS
S_error_gone.DESTRUCTION.OPERATIONS = eps /\ S_error_gone.DESTRUCTION.RELEASES = eps
~(HOBJECT n_error <- S_error_gone.ALLOCATIONS)
~(HARRAY n_trace <- S_error_gone.ALLOCATIONS)
$heap_owners($heap_graph(S_error_gone), HOBJECT n_error) = 0
$weakref_get(S_error_gone, n_weak_error) = PNULL
''')
    for label in ['api', 'body']:
        checks += [f'~(HARRAY n_frame_{label} <- S_error_gone.ALLOCATIONS)',
                   f'~(HARRAY n_args_{label} <- S_error_gone.ALLOCATIONS)']
    return checks + guards('S_error_gone')


def malformed():
    checks = lines(r'''
~$closure_current_config_tag(pconfigcall_current[.SELECTION = eps])
~$config_selected_valid(S_config, pconfigcall_current[.SELECTION = eps])
~$config_invoke_valid(S_config, pconfigcall_current[.SELECTION = eps])
~$closure_current_config_tag(pconfigcall_current[.SELECTION = ($(n_api + 1))])
~$config_selected_valid(S_config, pconfigcall_current[.SELECTION = ($(n_api + 1))])
~$config_selected_valid(S_config, pconfigcall_current[.OWNER = eps])
~$config_selected_valid(S_config, pconfigcall_current[.OWNER = (n_body)])
~$config_invoke_valid(S_config[.ORIGIN = eps], pconfigcall_current)
~$config_invoke_valid(S_config, pconfigcall_current[.SITE = PORIGIN 999 eps])
~$config_invoke_valid(S_config, pconfigcall_current[.LINE = $(pconfigcall_current.LINE + 1)])
~$config_invoke_valid(S_config, pconfigcall_current[.KIND = INTRINSIC_GET_CLASS])
~$config_selected_valid(S_config[.OBJECTS[n_api] = INTRINSICCLOSURE INTRINSIC_GET_CLASS], pconfigcall_current)
S_wrong = $config_prepare(S_value[.RESULT = KNOWN (POBJECT n_body)], INTRINSIC_CLOSURE_CURRENT, z_call, (n_api), porigin_call)
S_wrong.TODO = (CONFIG_ARGS pconfigcall_wrong) :: S_value.TODO
pconfigcall_wrong.SELECTION = eps
~$closure_current_config_tag(pconfigcall_wrong)
''')
    for task in ['CONFIG_ARGS pconfigcall_start', 'CONFIG_SEND pconfigcall_start',
                 'CONFIG_UNPACK_PREP pconfigcall_start', 'CONFIG_UNPACK_NEXT pconfigcall_start (KNOWN PNULL) 0',
                 'CONFIG_INVOKE pconfigcall_current', 'CONFIG_INI_NULL_RESULT pconfigcall_current',
                 'CONFIG_STRING_RESULT pconfigcall_current n_body porigin_call 1 1']:
        checks += [f'$selected_task_nonce({task}) = eps', f'$selected_task_count([{task}], n_api) = 0']
    return checks


def bridge(program, filename, expected, named=False, entry='main', shared=True):
    genuine = [f'S_begin = $php_run({program}, 0, {filename})', 'S_begin.COMPLETION = BUDGET']
    genuine += seek('S_config', 'S_begin', 3) + lines(r'''
S_config.TODO = (CONFIG_INVOKE pconfigcall_current) :: ptask_config*
pconfigcall_current.KIND = INTRINSIC_CLOSURE_CURRENT
pconfigcall_current.OWNER = (n_api)
pconfigcall_current.SELECTION = (n_api)
pconfigcall_current.INDEX = 0 /\ pconfigcall_current.SENT = eps
$closure_current_config_tag(pconfigcall_current)
$config_invoke_valid(S_config, pconfigcall_current)
$task_nodes(CONFIG_INVOKE pconfigcall_current) = [HOBJECT n_api]
$selected_task_nonce(CONFIG_INVOKE pconfigcall_current) = eps
S_config.OBJECTS[n_api] = INTRINSICCLOSURE INTRINSIC_CLOSURE_CURRENT
$lookup(S_config.ENV, $ptascii("picked")) = (n_picked_cell)
S_config.STORE[n_picked_cell] = DEFINED (POBJECT n_api)
$heap_owners($heap_graph(S_config), HOBJECT n_api) = 2
''') + guards('S_config')
    if named:
        genuine += lines(r'''
S_config.CURRENT = (pcallcontext_named)
pcallcontext_named.INSTANCE = eps
S_config.FRAMES = [pframe_body, pframe_main]
pframe_body.CONTEXT = (pcallcontext_body)
pcallcontext_body.TARGET = CLOSURE_TARGET n_body
pcallcontext_body.INSTANCE = (n_body)
$closure_current_object(S_config) = eps
''') + step('S_after', 'S_config') + lines(r'''
S_after.TODO = (THROW_SEARCH n_error) :: ptask_config*
S_after.OBJECTS[n_error] = THROWABLE pthrowable
pthrowable.KIND = "Error"
$throwable_field(S_after, n_error, "message") = PSTRING $ptascii("Current function is not a closure")
$heap_owners($heap_graph(S_after), HOBJECT n_api) = 1
''')
    else:
        genuine += lines(r'''
S_config.CURRENT = (pcallcontext_body)
pcallcontext_body.TARGET = CLOSURE_TARGET n_body
pcallcontext_body.INSTANCE = (n_body)
$closure_current_object(S_config) = (n_body)
''') + step('S_after', 'S_config') + lines(r'''
S_after.TODO = ptask_config*
S_after.RESULT = KNOWN (POBJECT n_body)
$closure_current_object(S_after) = (n_body)
$heap_owners($heap_graph(S_after), HOBJECT n_api) = 1
$heap_owners($heap_graph(S_after), HOBJECT n_body) = 2
''')
    genuine += ['S_after.CURRENT = S_config.CURRENT /\\ S_after.FRAMES = S_config.FRAMES']
    genuine += guards('S_after') + lines(r'''
S_zero = $drive_steps(S_config, 0)
S_zero = S_config[.COMPLETION = BUDGET]
S_done = $drive(S_zero[.COMPLETION = NORMAL], 1500)
S_done.COMPLETION = NORMAL
S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps
S_done = $drive(S_begin[.COMPLETION = NORMAL], 1500)
''') + [f'$outputs(S_done.EVENTS) = $ptascii("{expected}")'] + guards('S_done')
    return function(entry, genuine, [], shared)
