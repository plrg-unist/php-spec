"""Selected BIND pin during the actual third-argument global null write."""
from error_handler_protocol import PREFIX
from closure_bind_capture_review import guards, lines, step

EXTRA = r'''
dec $bind_argument_stage(pstate, nat) : bool
def $bind_argument_stage(S, 0) = true
  -- if S.TODO = (CALL_DYNAMIC porigin z_init z_call) :: ptask*
  -- if S_value = $resolve_at(S[.COMPLETION = NORMAL], S.RESULT, z_init)
  -- if S_value.RESULT = KNOWN (POBJECT n)
  -- if S_value.OBJECTS[n] = INTRINSICCLOSURE INTRINSIC_CLOSURE_BIND
def $bind_argument_stage(S, 1) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_CLOSURE_BIND
  -- if pconfigcall.INDEX = 0
def $bind_argument_stage(S, 2) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("api")
  -- if S.RESULT = KNOWN PNULL
  -- if S.CURRENT = (pcallcontext)
  -- if $ptlc(pcallcontext.NAME) = $ptascii("bind_scope_arg21")
def $bind_argument_stage(S, 3) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_CLOSURE_BIND
def $bind_argument_stage(S, 4) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("body")
  -- if S.RESULT = KNOWN PNULL
def $bind_argument_stage(S, 5) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("bound")
  -- if S.RESULT = KNOWN PNULL
def $bind_argument_stage(S, 6) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("returned")
  -- if S.RESULT = KNOWN PNULL
def $bind_argument_stage(S, n) = false -- otherwise
dec $bind_argument_seek(pstate, nat, nat) : pstate
def $bind_argument_seek(S, n_stage, n) = S
  -- if $bind_argument_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $bind_argument_seek(S, n_stage, n) = $bind_argument_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$bind_argument_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $bind_argument_seek(S, n_stage, 0) = S
  -- if ~$bind_argument_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $bind_argument_seek(S, n_stage, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $bind_argument_saved(ptask*) : pconfigcall?
dec $bind_argument_saved_head(ptask) : bool
def $bind_argument_saved_head(AT porigin ptask) = true
def $bind_argument_saved_head(CONFIG_SEND pconfigcall) = true
  -- if pconfigcall.KIND = INTRINSIC_CLOSURE_BIND
def $bind_argument_saved_head(ptask) = false -- otherwise
def $bind_argument_saved((AT porigin ptask) :: ptask_tail*) = $bind_argument_saved(ptask :: ptask_tail*)
def $bind_argument_saved((CONFIG_SEND pconfigcall) :: ptask_tail*) = (pconfigcall)
  -- if pconfigcall.KIND = INTRINSIC_CLOSURE_BIND
def $bind_argument_saved(ptask :: ptask_tail*) = $bind_argument_saved(ptask_tail*)
  -- if ~$bind_argument_saved_head(ptask)
def $bind_argument_saved(eps) = eps
'''


def seek(state, previous, stage):
    return [f'{state}_reached = $bind_argument_seek({previous}, {stage}, 1000)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$bind_argument_stage({state}, {stage})']


def function(entry, genuine, controls, shared):
    text = PREFIX[PREFIX.index('dec $outputs'):] + EXTRA if shared else ''
    checks = genuine + controls
    text += '\ndec $' + entry + '() : bool\ndef $' + entry + '() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks, len(genuine), len(controls)


def render(program, filename, expected, captured=True, entry='main', shared=True):
    genuine = [f'S_begin = $php_run({program}, 0, {filename})', 'S_begin.COMPLETION = BUDGET']
    if captured:
        genuine += seek('S_lookup', 'S_begin', 0) + lines(r'''
S_lookup.TODO = (CALL_DYNAMIC porigin_call z_init z_call) :: ptask_lookup*
S_lookup.ORIGIN = (porigin_call)
$dynamic_site(S_lookup, (porigin_call))
$call_task_valid(S_lookup, CALL_DYNAMIC porigin_call z_init z_call)
S_value = $resolve_at(S_lookup[.TODO = ptask_lookup*], S_lookup.RESULT, z_init)
S_value.COMPLETION = NORMAL
S_value.RESULT = KNOWN (POBJECT n_api)
S_value.OBJECTS[n_api] = INTRINSICCLOSURE INTRINSIC_CLOSURE_BIND
$outputs(S_lookup.EVENTS) = $ptascii("Q;C:held;B:held;P:held;A;")
''') + step('S_start', 'S_lookup') + lines(r'''
S_start = $config_prepare(S_value, INTRINSIC_CLOSURE_BIND, z_call, (n_api), porigin_call)
S_start.TODO = (CONFIG_ARGS pconfigcall_start) :: ptask_lookup*
pconfigcall_start.OWNER = (n_api)
pconfigcall_start.SELECTION = (n_api)
pconfigcall_start.SITE = porigin_call /\ pconfigcall_start.LINE = z_call
$closure_current_config_tag(pconfigcall_start)
$task_nodes(CONFIG_ARGS pconfigcall_start) = [HOBJECT n_api]
''')
    else:
        genuine += seek('S_start', 'S_begin', 1) + lines(r'''
S_start.TODO = (CONFIG_ARGS pconfigcall_start) :: ptask_start*
pconfigcall_start.OWNER = eps /\ pconfigcall_start.SELECTION = eps
~$closure_current_config_tag(pconfigcall_start)
$task_nodes(CONFIG_ARGS pconfigcall_start) = eps
''')
    genuine += lines(r'''
pconfigcall_start.KIND = INTRINSIC_CLOSURE_BIND
pconfigcall_start.INDEX = 0 /\ pconfigcall_start.SENT = eps
pconfigcall_start.PACKS = eps /\ ~pconfigcall_start.NAMED
$config_selected_valid(S_start, pconfigcall_start)
$call_task_valid(S_start, CONFIG_ARGS pconfigcall_start)
S_start.CURRENT = eps /\ S_start.FRAMES = eps
S_start.RESULT = KNOWN PNULL
S_start.GLOBALTABLE = eps
''')
    for name, ident in [('api', 'api'), ('body', 'body'), ('receiver', 'receiver'),
                        ('weakApi', 'weak_api'), ('weakBody', 'weak_body'), ('weakReceiver', 'weak_receiver')]:
        genuine += [f'$lookup(S_start.ENV, $ptascii("{name}")) = (n_{ident}_cell)',
                    f'S_start.STORE[n_{ident}_cell] = DEFINED (POBJECT n_{ident})']
    genuine += lines(r'''
S_start.OBJECTS[n_api] = INTRINSICCLOSURE INTRINSIC_CLOSURE_BIND
S_start.OBJECTS[n_body] = REALCLOSURE porigin_body eps eps
S_start.OBJECTS[n_receiver] = STDINSTANCE
$node_children(S_start, HOBJECT n_body) = eps
$weakref_get(S_start, n_weak_api) = POBJECT n_api
$heap_owners($heap_graph(S_start), HOBJECT n_body) = 1
$heap_owners($heap_graph(S_start), HOBJECT n_receiver) = 1
''') + [f'$heap_owners($heap_graph(S_start), HOBJECT n_api) = {2 if captured else 1}']
    genuine += guards('S_start') + seek('S_write', 'S_start', 2) + lines(r'''
S_write.TODO = (WRITE_NAME $ptascii("api") z_write) :: ptask_write*
S_write.RESULT = KNOWN PNULL
S_write.CURRENT = (pcallcontext_helper)
$ptlc(pcallcontext_helper.NAME) = $ptascii("bind_scope_arg21")
pcallcontext_helper.INSTANCE = eps /\ pcallcontext_helper.RECEIVER = eps
S_write.FRAMES = [pframe_main]
pframe_main.CONTEXT = eps /\ pframe_main.LOCALS = eps
$bind_argument_saved(pframe_main.TODO) = (pconfigcall_saved)
pconfigcall_saved = pconfigcall_start[.INDEX = 2][.SENT = [NAMED_SENT (KNOWN (POBJECT n_body)), NAMED_SENT (KNOWN (POBJECT n_receiver))]]
S_write.GLOBALTABLE = (psymboltable_write)
$lookup(psymboltable_write.ENV, $ptascii("api")) = (n_api_cell)
$lookup(S_write.ENV, $ptascii("api")) = (n_api_cell)
S_write.STORE[n_api_cell] = DEFINED (POBJECT n_api)
$heap_owners($heap_graph(S_write), HOBJECT n_body) = 2
$heap_owners($heap_graph(S_write), HOBJECT n_receiver) = 2
S_write.FIBERSEQ = 1 /\ ~$destructor_operational(S_write)
S_write.DESTRUCTION.OPERATIONS = eps /\ S_write.DESTRUCTION.RELEASES = eps
$outputs(S_write.EVENTS) = $ptascii("Q;C:held;B:held;P:held;A;S;")
''') + [f'$heap_owners($heap_graph(S_write), HOBJECT n_api) = {2 if captured else 1}']
    genuine += guards('S_write') + step('S_cleared', 'S_write') + lines(r'''
S_cleared.TODO = ptask_write*
S_cleared.RESULT = KNOWN PNULL
S_cleared.STORE[n_api_cell] = DEFINED PNULL
S_cleared.CURRENT = S_write.CURRENT /\ S_cleared.FRAMES = S_write.FRAMES
S_cleared.EVENTS = S_write.EVENTS
S_cleared.DESTRUCTION.OPERATIONS = eps /\ S_cleared.DESTRUCTION.RELEASES = eps
$heap_owners($heap_graph(S_cleared), HOBJECT n_body) = 2
$heap_owners($heap_graph(S_cleared), HOBJECT n_receiver) = 2
''')
    if captured:
        genuine += lines(r'''
(HOBJECT n_api) <- S_cleared.ALLOCATIONS
$heap_owners($heap_graph(S_cleared), HOBJECT n_api) = 1
$weakref_get(S_cleared, n_weak_api) = POBJECT n_api
$task_nodes(CONFIG_SEND pconfigcall_saved) = [HOBJECT n_api, HOBJECT n_body, HOBJECT n_receiver]
''')
    else:
        genuine += lines(r'''
~(HOBJECT n_api <- S_cleared.ALLOCATIONS)
$heap_owners($heap_graph(S_cleared), HOBJECT n_api) = 0
$weakref_get(S_cleared, n_weak_api) = PNULL
$task_nodes(CONFIG_SEND pconfigcall_saved) = [HOBJECT n_body, HOBJECT n_receiver]
''')
    genuine += guards('S_cleared')
    if not captured:
        controls = lines(r'''
pconfigcall_forged = pconfigcall_start[.OWNER = (n_api)][.SELECTION = (n_api)]
$closure_callable(S_start, n_api)
$closure_current_config_tag(pconfigcall_forged)
~$config_selected_valid(S_start, pconfigcall_forged)
~$call_task_valid(S_start, CONFIG_ARGS pconfigcall_forged)
''')
        return function(entry, genuine, controls, shared)
    genuine += seek('S_config', 'S_cleared', 3) + lines(r'''
S_config.TODO = (CONFIG_INVOKE pconfigcall_bind) :: ptask_config*
pconfigcall_bind = pconfigcall_saved[.INDEX = 3][.SENT = pconfigcall_saved.SENT ++ [NAMED_SENT (KNOWN PNULL)]]
$closure_current_config_tag(pconfigcall_bind)
$config_invoke_valid(S_config, pconfigcall_bind)
$call_task_valid(S_config, CONFIG_INVOKE pconfigcall_bind)
S_config.CURRENT = eps /\ S_config.FRAMES = eps
S_config.STORE[n_api_cell] = DEFINED PNULL
S_config.RESULT = KNOWN PNULL
$task_nodes(CONFIG_INVOKE pconfigcall_bind) = [HOBJECT n_api, HOBJECT n_body, HOBJECT n_receiver]
$heap_owners($heap_graph(S_config), HOBJECT n_api) = 1
$heap_owners($heap_graph(S_config), HOBJECT n_body) = 2
$heap_owners($heap_graph(S_config), HOBJECT n_receiver) = 2
$outputs(S_config.EVENTS) = $ptascii("Q;C:held;B:held;P:held;A;S;C:held;")
n_bound = |S_config.OBJECTS|
''') + guards('S_config') + step('S_result', 'S_config') + lines(r'''
S_result.TODO = ptask_config*
S_result.RESULT = KNOWN (POBJECT n_bound)
S_result.CURRENT = S_config.CURRENT /\ S_result.FRAMES = S_config.FRAMES
S_result.EVENTS = S_config.EVENTS
S_result.OBJECTS[n_bound] = INTERNALSCOPECLOSURE pinternalclosurescope (REALCLOSURE porigin_body eps eps)
pinternalclosurescope.SOURCE = n_body /\ pinternalclosurescope.FUNCTION = porigin_body
pinternalclosurescope.CALLSITE = (pconfigcall_bind.SITE)
pinternalclosurescope.LEXICAL = BIND_INTERNAL ($ptascii("Closure"))
pinternalclosurescope.CALLED = $bind_object_scope(S_result, n_receiver)
pinternalclosurescope.RECEIVER = (n_receiver) /\ pinternalclosurescope.BOUND
$node_children(S_result, HOBJECT n_bound) = [HOBJECT n_receiver]
$internal_closure_history_valid(S_result, n_bound)
$internal_closure_scope_valid(S_result, n_bound)
~(HOBJECT n_api <- S_result.ALLOCATIONS)
$heap_owners($heap_graph(S_result), HOBJECT n_api) = 0
$weakref_get(S_result, n_weak_api) = PNULL
~$closure_callable(S_result, n_api)
$closure_static_api_owner_valid(S_result, n_api)
$heap_owners($heap_graph(S_result), HOBJECT n_body) = 1
$heap_owners($heap_graph(S_result), HOBJECT n_receiver) = 2
$heap_owners($heap_graph(S_result), HOBJECT n_bound) = 1
''') + guards('S_result')
    genuine += seek('S_body_write', 'S_result', 4) + lines(r'''
S_body_write.TODO = (WRITE_NAME $ptascii("body") z_body) :: ptask_body*
S_body_write.STORE[n_body_cell] = DEFINED (POBJECT n_body)
S_body_write.RESULT = KNOWN PNULL
~$destructor_operational(S_body_write)
$lookup(S_body_write.ENV, $ptascii("bound")) = (n_bound_cell)
S_body_write.STORE[n_bound_cell] = DEFINED (POBJECT n_bound)
''') + step('S_body_gone', 'S_body_write') + lines(r'''
S_body_gone.TODO = ptask_body*
S_body_gone.STORE[n_body_cell] = DEFINED PNULL
S_body_gone.EVENTS = S_body_write.EVENTS
~(HOBJECT n_body <- S_body_gone.ALLOCATIONS)
$heap_owners($heap_graph(S_body_gone), HOBJECT n_body) = 0
$weakref_get(S_body_gone, n_weak_body) = PNULL
S_body_gone.OBJECTS[n_bound] = S_result.OBJECTS[n_bound]
$internal_closure_history_valid(S_body_gone, n_bound)
''') + guards('S_body_gone')
    genuine += seek('S_bound_write', 'S_body_gone', 5) + lines(r'''
S_bound_write.TODO = (WRITE_NAME $ptascii("bound") z_bound) :: ptask_bound*
S_bound_write.STORE[n_bound_cell] = DEFINED (POBJECT n_bound)
S_bound_write.STORE[n_receiver_cell] = DEFINED PNULL
S_bound_write.RESULT = KNOWN PNULL
~$destructor_operational(S_bound_write)
$lookup(S_bound_write.ENV, $ptascii("returned")) = (n_returned_cell)
S_bound_write.STORE[n_returned_cell] = DEFINED (POBJECT n_receiver)
$lookup(S_bound_write.ENV, $ptascii("weakBound")) = (n_weak_bound_cell)
S_bound_write.STORE[n_weak_bound_cell] = DEFINED (POBJECT n_weak_bound)
$heap_owners($heap_graph(S_bound_write), HOBJECT n_bound) = 1
$heap_owners($heap_graph(S_bound_write), HOBJECT n_receiver) = 2
$outputs(S_bound_write.EVENTS) = $ptascii("Q;C:held;B:held;P:held;A;S;C:held;N:bound;C:gone;B:gone;P:held;I:same;")
''') + step('S_bound_gone', 'S_bound_write') + lines(r'''
S_bound_gone.TODO = ptask_bound*
S_bound_gone.STORE[n_bound_cell] = DEFINED PNULL
S_bound_gone.EVENTS = S_bound_write.EVENTS
~(HOBJECT n_bound <- S_bound_gone.ALLOCATIONS)
$heap_owners($heap_graph(S_bound_gone), HOBJECT n_bound) = 0
$weakref_get(S_bound_gone, n_weak_bound) = PNULL
$heap_owners($heap_graph(S_bound_gone), HOBJECT n_receiver) = 1
$weakref_get(S_bound_gone, n_weak_receiver) = POBJECT n_receiver
''') + guards('S_bound_gone')
    genuine += seek('S_returned_write', 'S_bound_gone', 6) + lines(r'''
S_returned_write.TODO = (WRITE_NAME $ptascii("returned") z_returned) :: ptask_returned*
S_returned_write.STORE[n_returned_cell] = DEFINED (POBJECT n_receiver)
S_returned_write.RESULT = KNOWN PNULL
~$destructor_operational(S_returned_write)
$heap_owners($heap_graph(S_returned_write), HOBJECT n_receiver) = 1
''') + step('S_receiver_gone', 'S_returned_write') + lines(r'''
S_receiver_gone.TODO = ptask_returned*
S_receiver_gone.STORE[n_returned_cell] = DEFINED PNULL
S_receiver_gone.EVENTS = S_returned_write.EVENTS
~(HOBJECT n_receiver <- S_receiver_gone.ALLOCATIONS)
$heap_owners($heap_graph(S_receiver_gone), HOBJECT n_receiver) = 0
$weakref_get(S_receiver_gone, n_weak_receiver) = PNULL
S_zero = $drive_steps(S_config, 0)
S_zero = S_config[.COMPLETION = BUDGET]
S_done = $drive(S_receiver_gone, 1500)
S_done.COMPLETION = NORMAL
S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps
S_done.TRACE = eps
S_done = $drive(S_zero[.COMPLETION = NORMAL], 1500)
S_done = $drive(S_begin[.COMPLETION = NORMAL], 1500)
''') + [f'$outputs(S_done.EVENTS) = $ptascii("{expected}")'] + guards('S_done')
    controls = lines(r'''
~$closure_current_config_tag(pconfigcall_bind[.SELECTION = eps])
~$config_selected_valid(S_config, pconfigcall_bind[.SELECTION = eps])
~$config_invoke_valid(S_config, pconfigcall_bind[.SELECTION = eps])
~$closure_current_config_tag(pconfigcall_bind[.SELECTION = (n_body)])
~$config_selected_valid(S_config, pconfigcall_bind[.SELECTION = (n_body)])
~$config_selected_valid(S_config, pconfigcall_bind[.OWNER = eps])
~$config_selected_valid(S_config, pconfigcall_bind[.OWNER = (n_body)])
~$config_invoke_valid(S_config, pconfigcall_bind[.SITE = PORIGIN 999 eps])
~$config_invoke_valid(S_config, pconfigcall_bind[.LINE = $(pconfigcall_bind.LINE + 1)])
~$config_selected_valid(S_config, pconfigcall_bind[.KIND = INTRINSIC_CLOSURE_CURRENT])
~$config_selected_valid(S_config[.OBJECTS[n_api] = INTRINSICCLOSURE INTRINSIC_CLOSURE_CURRENT], pconfigcall_bind)
S_wrong = $config_prepare(S_value[.RESULT = KNOWN (POBJECT n_body)], INTRINSIC_CLOSURE_BIND, z_call, (n_api), porigin_call)
S_wrong.TODO = (CONFIG_ARGS pconfigcall_wrong) :: S_value.TODO
pconfigcall_wrong.SELECTION = eps
~$closure_current_config_tag(pconfigcall_wrong)
~$config_selected_valid(S_value, pconfigcall_wrong)
pconfigcall_nonce = pconfigcall_start[.KIND = INTRINSIC_GET_CLASS][.OWNER = eps]
$selected_task_nonce(CONFIG_ARGS pconfigcall_nonce) = (n_api)
$selected_task_count([CONFIG_ARGS pconfigcall_nonce], n_api) = 1
''')
    for task in ['CONFIG_ARGS pconfigcall_start', 'CONFIG_SEND pconfigcall_saved',
                 'CONFIG_UNPACK_PREP pconfigcall_start', 'CONFIG_UNPACK_NEXT pconfigcall_start (KNOWN PNULL) 0',
                 'CONFIG_INVOKE pconfigcall_bind', 'CONFIG_INI_NULL_RESULT pconfigcall_bind',
                 'CONFIG_STRING_RESULT pconfigcall_bind n_body porigin_call 1 1']:
        controls += [f'$selected_task_nonce({task}) = eps', f'$selected_task_count([{task}], n_api) = 0']
    return function(entry, genuine, controls, shared)


def bridge(program, filename, entry='bind_argument_bridge', shared=False):
    genuine = [f'S_begin = $php_run({program}, 0, {filename})', 'S_begin.COMPLETION = BUDGET']
    genuine += seek('S_config', 'S_begin', 3) + lines(r'''
S_config.TODO = (CONFIG_INVOKE pconfigcall_bind) :: ptask_config*
pconfigcall_bind.KIND = INTRINSIC_CLOSURE_BIND
pconfigcall_bind.OWNER = (n_api)
pconfigcall_bind.SELECTION = (n_api)
pconfigcall_bind.SENT = [NAMED_SENT (KNOWN (POBJECT n_body)), NAMED_SENT (KNOWN (POBJECT n_receiver)), NAMED_SENT (KNOWN PNULL)]
$closure_current_config_tag(pconfigcall_bind)
$config_invoke_valid(S_config, pconfigcall_bind)
$task_nodes(CONFIG_INVOKE pconfigcall_bind) = [HOBJECT n_api, HOBJECT n_body, HOBJECT n_receiver]
$heap_owners($heap_graph(S_config), HOBJECT n_api) = 2
$lookup(S_config.ENV, $ptascii("api")) = (n_api_cell)
S_config.STORE[n_api_cell] = DEFINED (POBJECT n_api)
S_config.OBJECTS[n_body] = REALCLOSURE porigin_body eps eps
n_bound = |S_config.OBJECTS|
''') + step('S_result', 'S_config') + lines(r'''
S_result.TODO = ptask_config*
S_result.RESULT = KNOWN (POBJECT n_bound)
S_result.OBJECTS[n_bound] = INTERNALSCOPECLOSURE pinternalclosurescope (REALCLOSURE porigin_body eps eps)
pinternalclosurescope.SOURCE = n_body /\ pinternalclosurescope.FUNCTION = porigin_body
pinternalclosurescope.CALLSITE = (pconfigcall_bind.SITE)
pinternalclosurescope.LEXICAL = BIND_INTERNAL ($ptascii("Closure"))
pinternalclosurescope.CALLED = $bind_object_scope(S_result, n_receiver)
pinternalclosurescope.RECEIVER = (n_receiver) /\ pinternalclosurescope.BOUND
$node_children(S_result, HOBJECT n_bound) = [HOBJECT n_receiver]
$internal_closure_history_valid(S_result, n_bound)
$heap_owners($heap_graph(S_result), HOBJECT n_api) = 1
S_result.STORE[n_api_cell] = S_config.STORE[n_api_cell]
''')
    return function(entry, genuine, [], shared)
