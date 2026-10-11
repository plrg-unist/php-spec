"""Literal bind capture, copied internal scope and distinct object retirements."""
from error_handler_protocol import PREFIX

EXTRA = r'''
dec $bind_capture_stage(pstate, nat) : bool
def $bind_capture_stage(S, 0) = true
  -- if S.TODO = (SCOPED_CLASS phpType19 phpType20 phpType7* z) :: ptask*
  -- if $closure_bind_capture(S[.COMPLETION = NORMAL], phpType19, $ptascii("bind"), phpType7*, z)
def $bind_capture_stage(S, 1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_CLOSURE_BIND
def $bind_capture_stage(S, 2) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("api")
  -- if S.RESULT = KNOWN PNULL
def $bind_capture_stage(S, 3) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("body")
  -- if S.RESULT = KNOWN PNULL
def $bind_capture_stage(S, 4) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("receiver")
  -- if S.RESULT = KNOWN PNULL
def $bind_capture_stage(S, 5) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("bound")
  -- if S.RESULT = KNOWN PNULL
def $bind_capture_stage(S, 6) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("returned")
  -- if S.RESULT = KNOWN PNULL
def $bind_capture_stage(S, n) = false -- otherwise
dec $bind_capture_seek(pstate, nat, nat) : pstate
def $bind_capture_seek(S, n_stage, n) = S
  -- if $bind_capture_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $bind_capture_seek(S, n_stage, n) = $bind_capture_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$bind_capture_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $bind_capture_seek(S, n_stage, 0) = S
  -- if ~$bind_capture_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $bind_capture_seek(S, n_stage, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''


def lines(text):
    return [line for line in text.strip().splitlines() if line]


def guards(state):
    return [f'$call_current_valid({state})', f'$call_frames_valid({state}, {state}.FRAMES)',
            f'$call_descriptors_valid({state})', f'$closure_state_valid({state})',
            f'$heap_valid($heap_graph({state}))']


def seek(state, previous, stage):
    return [f'{state}_reached = $bind_capture_seek({previous}, {stage}, 1000)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$bind_capture_stage({state}, {stage})']


def step(after, before):
    return [f'{after}_step = $drive_steps({before}, 1)',
            f'{after}_step.COMPLETION = BUDGET',
            f'{after} = {after}_step[.COMPLETION = NORMAL]']


def write(state, previous, stage, name, cell, value):
    checks = seek(state, previous, stage) + [
        f'{state}.TODO = (WRITE_NAME $ptascii("{name}") z_{name}) :: ptask_{name}*',
        f'{state}.STORE[{cell}] = DEFINED {value}', f'{state}.RESULT = KNOWN PNULL',
        f'{state}.CURRENT = eps /\\ {state}.FRAMES = eps',
        f'~$destructor_operational({state})']
    return checks


def cleared(after, before, name, cell):
    return step(after, before) + [
        f'{after}.TODO = ptask_{name}*', f'{after}.STORE[{cell}] = DEFINED PNULL',
        f'{after}.RESULT = KNOWN PNULL', f'{after}.EVENTS = {before}.EVENTS',
        f'{after}.DESTRUCTION.OPERATIONS = eps /\\ {after}.DESTRUCTION.RELEASES = eps']


def render(program, filename, expected):
    genuine = [f'S_begin = $php_run({program}, 0, {filename})', 'S_begin.COMPLETION = BUDGET']
    genuine += seek('S_capture', 'S_begin', 0) + lines(r'''
S_capture.TODO = (SCOPED_CLASS phpType19 phpType20 phpType7* z_capture) :: ptask_capture*
S_capture.ORIGIN = (porigin_capture)
S_class = $scoped_class_prepare(S_capture, phpType19, z_capture)
S_class.COMPLETION = NORMAL
S_class.RESULT = KNOWN (PSTRING ptbytes_class)
$ptlc($typed_callable_name(ptbytes_class)) = $ptascii("closure")
$ppscoped_named(phpType19) /\ ~$ppscoped_keyword(phpType19)
$ppfirstclass(phpType7*)
$closure_bind_capture(S_capture, phpType19, $ptascii("bind"), phpType7*, z_capture)
$call_task_valid(S_capture, SCOPED_CLASS phpType19 phpType20 phpType7* z_capture)
$outputs(S_capture.EVENTS) = $ptascii("Q;")
n_api = |S_capture.OBJECTS|
''') + guards('S_capture') + step('S_minted', 'S_capture') + lines(r'''
S_minted.TODO = ptask_capture*
S_minted.RESULT = KNOWN (POBJECT n_api)
S_minted.OBJECTS = S_capture.OBJECTS ++ [INTRINSICCLOSURE INTRINSIC_CLOSURE_BIND]
(HOBJECT n_api) <- S_minted.ALLOCATIONS
$node_children(S_minted, HOBJECT n_api) = eps
$heap_owners($heap_graph(S_minted), HOBJECT n_api) = 1
$closure_callable(S_minted, n_api)
$closure_live_object_valid(S_minted, n_api)
$closure_static_api_owner_valid(S_minted, n_api)
''') + guards('S_minted')
    genuine += seek('S_config', 'S_minted', 1) + lines(r'''
S_config.TODO = (CONFIG_INVOKE pconfigcall_bind) :: ptask_config*
pconfigcall_bind.KIND = INTRINSIC_CLOSURE_BIND
pconfigcall_bind.OWNER = (n_api)
pconfigcall_bind.SELECTION = eps
pconfigcall_bind.INDEX = 3 /\ pconfigcall_bind.PACKS = eps /\ ~pconfigcall_bind.NAMED
$lookup(S_config.ENV, $ptascii("api")) = (n_api_cell)
S_config.STORE[n_api_cell] = DEFINED (POBJECT n_api)
$lookup(S_config.ENV, $ptascii("body")) = (n_body_cell)
S_config.STORE[n_body_cell] = DEFINED (POBJECT n_body)
$lookup(S_config.ENV, $ptascii("receiver")) = (n_receiver_cell)
S_config.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver)
pconfigcall_bind.SENT = [NAMED_SENT (KNOWN (POBJECT n_body)), NAMED_SENT (KNOWN (POBJECT n_receiver)), NAMED_SENT (KNOWN PNULL)]
S_config.OBJECTS[n_api] = INTRINSICCLOSURE INTRINSIC_CLOSURE_BIND
S_config.OBJECTS[n_body] = REALCLOSURE porigin_body eps eps
S_config.OBJECTS[n_receiver] = STDINSTANCE
$lookup(S_config.ENV, $ptascii("weakApi")) = (n_weak_api_cell)
S_config.STORE[n_weak_api_cell] = DEFINED (POBJECT n_weak_api)
$lookup(S_config.ENV, $ptascii("weakBody")) = (n_weak_body_cell)
S_config.STORE[n_weak_body_cell] = DEFINED (POBJECT n_weak_body)
$lookup(S_config.ENV, $ptascii("weakReceiver")) = (n_weak_receiver_cell)
S_config.STORE[n_weak_receiver_cell] = DEFINED (POBJECT n_weak_receiver)
$weakref_get(S_config, n_weak_api) = POBJECT n_api
$weakref_get(S_config, n_weak_body) = POBJECT n_body
$weakref_get(S_config, n_weak_receiver) = POBJECT n_receiver
$config_selected_valid(S_config, pconfigcall_bind)
$config_invoke_valid(S_config, pconfigcall_bind)
$call_task_valid(S_config, CONFIG_INVOKE pconfigcall_bind)
$dynamic_site(S_config, (pconfigcall_bind.SITE))
$closure_binding_api_site(S_config, pconfigcall_bind.SITE)
$task_nodes(CONFIG_INVOKE pconfigcall_bind) = [HOBJECT n_body, HOBJECT n_receiver]
$heap_owners($heap_graph(S_config), HOBJECT n_api) = 1
$heap_owners($heap_graph(S_config), HOBJECT n_body) = 2
$heap_owners($heap_graph(S_config), HOBJECT n_receiver) = 2
S_config.CURRENT = eps /\ S_config.FRAMES = eps
S_config.FIBERSEQ = 1 /\ ~$destructor_operational(S_config)
S_config.DESTRUCTION.OPERATIONS = eps /\ S_config.DESTRUCTION.RELEASES = eps
$outputs(S_config.EVENTS) = $ptascii("Q;C:held;B:held;P:held;A;")
n_bound = |S_config.OBJECTS|
''') + guards('S_config') + step('S_result', 'S_config') + lines(r'''
S_result.RESULT = KNOWN (POBJECT n_bound)
S_result.TODO = ptask_config*
S_result.CURRENT = S_config.CURRENT /\ S_result.FRAMES = S_config.FRAMES
S_result.OBJECTS[n_bound] = INTERNALSCOPECLOSURE pinternalclosurescope (REALCLOSURE porigin_body eps eps)
pinternalclosurescope.SOURCE = n_body
pinternalclosurescope.FUNCTION = porigin_body
pinternalclosurescope.CALLSITE = (pconfigcall_bind.SITE)
pinternalclosurescope.LEXICAL = BIND_INTERNAL ($ptascii("Closure"))
pinternalclosurescope.CALLED = $bind_object_scope(S_result, n_receiver)
pinternalclosurescope.RECEIVER = (n_receiver) /\ pinternalclosurescope.BOUND
$node_children(S_result, HOBJECT n_bound) = [HOBJECT n_receiver]
$internal_closure_history_valid(S_result, n_bound)
$internal_closure_scope_valid(S_result, n_bound)
$closure_callable(S_result, n_bound)
$heap_owners($heap_graph(S_result), HOBJECT n_bound) = 1
$heap_owners($heap_graph(S_result), HOBJECT n_api) = 1
$heap_owners($heap_graph(S_result), HOBJECT n_body) = 1
$heap_owners($heap_graph(S_result), HOBJECT n_receiver) = 2
''') + guards('S_result')
    genuine += write('S_api_write', 'S_result', 2, 'api', 'n_api_cell', '(POBJECT n_api)') + lines(r'''
$lookup(S_api_write.ENV, $ptascii("bound")) = (n_bound_cell)
S_api_write.STORE[n_bound_cell] = DEFINED (POBJECT n_bound)
$lookup(S_api_write.ENV, $ptascii("weakBound")) = (n_weak_bound_cell)
S_api_write.STORE[n_weak_bound_cell] = DEFINED (POBJECT n_weak_bound)
$heap_owners($heap_graph(S_api_write), HOBJECT n_api) = 1
''') + cleared('S_api_gone', 'S_api_write', 'api', 'n_api_cell') + lines(r'''
~(HOBJECT n_api <- S_api_gone.ALLOCATIONS)
$heap_owners($heap_graph(S_api_gone), HOBJECT n_api) = 0
$weakref_get(S_api_gone, n_weak_api) = PNULL
~$closure_callable(S_api_gone, n_api)
~$closure_live_object_valid(S_api_gone, n_api)
$closure_static_api_owner_valid(S_api_gone, n_api)
$internal_closure_scope_valid(S_api_gone, n_bound)
''')
    genuine += write('S_body_write', 'S_api_gone', 3, 'body', 'n_body_cell', '(POBJECT n_body)') + [
        '$heap_owners($heap_graph(S_body_write), HOBJECT n_body) = 1']
    genuine += cleared('S_body_gone', 'S_body_write', 'body', 'n_body_cell') + lines(r'''
~(HOBJECT n_body <- S_body_gone.ALLOCATIONS)
$heap_owners($heap_graph(S_body_gone), HOBJECT n_body) = 0
$weakref_get(S_body_gone, n_weak_body) = PNULL
S_body_gone.OBJECTS[n_bound] = S_result.OBJECTS[n_bound]
$internal_closure_history_valid(S_body_gone, n_bound)
$internal_closure_scope_valid(S_body_gone, n_bound)
''') + guards('S_body_gone')
    genuine += write('S_receiver_write', 'S_body_gone', 4, 'receiver', 'n_receiver_cell', '(POBJECT n_receiver)') + [
        '$heap_owners($heap_graph(S_receiver_write), HOBJECT n_receiver) = 2']
    genuine += cleared('S_receiver_held', 'S_receiver_write', 'receiver', 'n_receiver_cell') + lines(r'''
$heap_owners($heap_graph(S_receiver_held), HOBJECT n_receiver) = 1
$node_children(S_receiver_held, HOBJECT n_bound) = [HOBJECT n_receiver]
$weakref_get(S_receiver_held, n_weak_receiver) = POBJECT n_receiver
$internal_closure_scope_valid(S_receiver_held, n_bound)
''')
    genuine += write('S_bound_write', 'S_receiver_held', 5, 'bound', 'n_bound_cell', '(POBJECT n_bound)') + lines(r'''
$lookup(S_bound_write.ENV, $ptascii("returned")) = (n_returned_cell)
S_bound_write.STORE[n_returned_cell] = DEFINED (POBJECT n_receiver)
$heap_owners($heap_graph(S_bound_write), HOBJECT n_bound) = 1
$heap_owners($heap_graph(S_bound_write), HOBJECT n_receiver) = 2
$outputs(S_bound_write.EVENTS) = $ptascii("Q;C:held;B:held;P:held;A;N:bound;C:gone;B:gone;P:held;I:same;")
''') + cleared('S_bound_gone', 'S_bound_write', 'bound', 'n_bound_cell') + lines(r'''
~(HOBJECT n_bound <- S_bound_gone.ALLOCATIONS)
$heap_owners($heap_graph(S_bound_gone), HOBJECT n_bound) = 0
$weakref_get(S_bound_gone, n_weak_bound) = PNULL
$heap_owners($heap_graph(S_bound_gone), HOBJECT n_receiver) = 1
$weakref_get(S_bound_gone, n_weak_receiver) = POBJECT n_receiver
~$internal_closure_scope_valid(S_bound_gone, n_bound)
''') + guards('S_bound_gone')
    genuine += write('S_returned_write', 'S_bound_gone', 6, 'returned', 'n_returned_cell', '(POBJECT n_receiver)') + [
        '$heap_owners($heap_graph(S_returned_write), HOBJECT n_receiver) = 1']
    genuine += cleared('S_receiver_gone', 'S_returned_write', 'returned', 'n_returned_cell') + lines(r'''
~(HOBJECT n_receiver <- S_receiver_gone.ALLOCATIONS)
$heap_owners($heap_graph(S_receiver_gone), HOBJECT n_receiver) = 0
$weakref_get(S_receiver_gone, n_weak_receiver) = PNULL
$weakref_get(S_receiver_gone, n_weak_body) = PNULL
$weakref_get(S_receiver_gone, n_weak_api) = PNULL
$weakref_get(S_receiver_gone, n_weak_bound) = PNULL
''') + guards('S_receiver_gone') + lines(r'''
S_zero = $drive_steps(S_config, 0)
S_zero = S_config[.COMPLETION = BUDGET]
S_done = $drive(S_receiver_gone, 1500)
S_done.COMPLETION = NORMAL
S_done.CURRENT = eps /\ S_done.FRAMES = eps
S_done.TODO = eps /\ S_done.TRACE = eps
S_done = $drive(S_zero[.COMPLETION = NORMAL], 1500)
S_done = $drive(S_begin[.COMPLETION = NORMAL], 1500)
''') + [f'$outputs(S_done.EVENTS) = $ptascii("{expected}")'] + guards('S_done')
    controls = lines(r'''
~$closure_bind_capture(S_capture[.COMPLETION = BUDGET], phpType19, $ptascii("bind"), phpType7*, z_capture)
~$closure_bind_capture(S_capture[.ORIGIN = eps], phpType19, $ptascii("bind"), phpType7*, z_capture)
~$closure_bind_capture(S_capture[.TODO = eps], phpType19, $ptascii("bind"), phpType7*, z_capture)
~$closure_bind_capture(S_capture, phpType19, $ptascii("bindto"), phpType7*, z_capture)
~$closure_bind_capture(S_capture, phpType19, $ptascii("bind"), eps, z_capture)
~$closure_bind_capture(S_capture, phpType19, $ptascii("bind"), phpType7*, $(z_capture + 1))
~$config_selected_valid(S_config, pconfigcall_bind[.OWNER = eps])
~$config_selected_valid(S_config, pconfigcall_bind[.OWNER = (n_body)])
~$config_selected_valid(S_config, pconfigcall_bind[.KIND = INTRINSIC_GET_CLASS])
~$config_selected_valid(S_config[.OBJECTS[n_api] = INTRINSICCLOSURE INTRINSIC_GET_CLASS], pconfigcall_bind)
~$config_invoke_valid(S_config, pconfigcall_bind[.SITE = porigin_capture])
~$config_invoke_valid(S_config, pconfigcall_bind[.LINE = $(pconfigcall_bind.LINE + 1)])
~$closure_binding_api_site(S_result, porigin_capture)
~$closure_binding_api_site(S_result, porigin_body)
~$internal_closure_history_valid(S_result[.OBJECTS[n_bound] = INTERNALSCOPECLOSURE (pinternalclosurescope[.SOURCE = n_api]) (REALCLOSURE porigin_body eps eps)], n_bound)
~$internal_closure_history_valid(S_result[.OBJECTS[n_bound] = INTERNALSCOPECLOSURE (pinternalclosurescope[.FUNCTION = porigin_capture]) (REALCLOSURE porigin_body eps eps)], n_bound)
~$internal_closure_history_valid(S_result[.OBJECTS[n_bound] = INTERNALSCOPECLOSURE (pinternalclosurescope[.CALLSITE = (porigin_capture)]) (REALCLOSURE porigin_body eps eps)], n_bound)
~$internal_closure_history_valid(S_result[.OBJECTS[n_bound] = INTERNALSCOPECLOSURE (pinternalclosurescope[.CALLSITE = (porigin_body)]) (REALCLOSURE porigin_body eps eps)], n_bound)
~$internal_closure_history_valid(S_result[.OBJECTS[n_bound] = INTERNALSCOPECLOSURE (pinternalclosurescope[.CALLED = BIND_UNSCOPED]) (REALCLOSURE porigin_body eps eps)], n_bound)
~$internal_closure_history_valid(S_result[.OBJECTS[n_bound] = INTERNALSCOPECLOSURE (pinternalclosurescope[.RECEIVER = eps]) (REALCLOSURE porigin_body eps eps)], n_bound)
''')
    checks = genuine + controls
    text = PREFIX[PREFIX.index('dec $outputs'):] + EXTRA + '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks, len(genuine), len(controls)
