"""Computed class-CV bind capture, frozen API and authentic binding result."""
from error_handler_protocol import PREFIX
from closure_bind_capture_review import guards, lines, step

EXTRA = r'''
dec $bind_computed_stage(pstate, nat) : bool
def $bind_computed_stage(S, 0) = true
  -- if S.TODO = (SCOPED_CLASS phpType19 phpType20 phpType7* z) :: ptask*
  -- if phpType19 = NExprVariable (BYTES text_class) metadata_class
  -- if S_class = $scoped_class_prepare(S[.COMPLETION = NORMAL], phpType19, z)
  -- if $closure_bind_capture(S_class, phpType19, $ptascii("bind"), phpType7*, z)
def $bind_computed_stage(S, 1) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("class")
  -- if S.RESULT = KNOWN (PSTRING ptbytes_class)
  -- if $ptlc(ptbytes_class) = $ptascii("stdclass")
def $bind_computed_stage(S, 2) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_CLOSURE_BIND
def $bind_computed_stage(S, n) = false -- otherwise
dec $bind_computed_seek(pstate, nat, nat) : pstate
def $bind_computed_seek(S, n_stage, n) = S
  -- if $bind_computed_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $bind_computed_seek(S, n_stage, n) = $bind_computed_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$bind_computed_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $bind_computed_seek(S, n_stage, 0) = S
  -- if ~$bind_computed_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $bind_computed_seek(S, n_stage, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''


def seek(state, previous, stage):
    return [f'{state}_reached = $bind_computed_seek({previous}, {stage}, 1000)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$bind_computed_stage({state}, {stage})']


def render(program, filename, expected):
    genuine = [f'S_begin = $php_run({program}, 0, {filename})', 'S_begin.COMPLETION = BUDGET']
    genuine += seek('S_capture', 'S_begin', 0) + lines(r'''
S_capture.TODO = (SCOPED_CLASS phpType19 phpType20 phpType7* z_capture) :: ptask_capture*
phpType19 = NExprVariable (BYTES text_class) metadata_class
$base64(text_class) = $ptascii("class")
S_capture.RESULT = VARIABLE n_class_name* z_class
n_class_name* = $base64(text_class)
S_capture.ORIGIN = (porigin_capture)
$origin_node(S_capture.SOURCES, porigin_capture) = (NExprStaticCall phpType19 phpType20 (SEQUENCE phpType7*) metadata_capture)
phpType20 = NIdentifier (BYTES text_method) metadata_method
$ptlc($base64(text_method)) = $ptascii("bind")
$lookup(S_capture.ENV, $ptascii("class")) = (n_class_cell)
S_capture.STORE[n_class_cell] = DEFINED (PSTRING ptbytes_before)
$ptlc(ptbytes_before) = $ptascii("closure")
$call_task_valid(S_capture, SCOPED_CLASS phpType19 phpType20 phpType7* z_capture)
$ppfirstclass(phpType7*)
~$ppscoped_named(phpType19)
S_class = $scoped_class_prepare(S_capture, phpType19, z_capture)
S_class.COMPLETION = NORMAL
S_class.RESULT = KNOWN (PSTRING ptbytes_prepared)
$ptlc($typed_callable_name(ptbytes_prepared)) = $ptascii("closure")
S_class.TODO = S_capture.TODO
S_class.ORIGIN = S_capture.ORIGIN
S_class.STORE = S_capture.STORE /\ S_class.ENV = S_capture.ENV
$heap_graph(S_class) = $heap_graph(S_capture)
$closure_bind_capture(S_class, phpType19, $ptascii("bind"), phpType7*, z_capture)
$outputs(S_capture.EVENTS) = $ptascii("Q;")
n_api = |S_capture.OBJECTS|
''') + guards('S_capture') + step('S_minted', 'S_capture') + lines(r'''
S_prepared_mint = $scoped_name_prepare(S_class, phpType19, S_class.RESULT, phpType20, phpType7*, z_capture)
S_minted = $destruction_store_new(S_prepared_mint)
S_minted.TODO = ptask_capture*
S_minted.RESULT = KNOWN (POBJECT n_api)
S_minted.OBJECTS = S_capture.OBJECTS ++ [INTRINSICCLOSURE INTRINSIC_CLOSURE_BIND]
(HOBJECT n_api) <- S_minted.ALLOCATIONS
$node_children(S_minted, HOBJECT n_api) = eps
$heap_owners($heap_graph(S_minted), HOBJECT n_api) = 1
$closure_callable(S_minted, n_api)
$closure_live_object_valid(S_minted, n_api)
''')
    genuine += seek('S_mutate', 'S_minted', 1) + lines(r'''
S_mutate.TODO = (WRITE_NAME n_name* z_mutate) :: ptask_mutate*
n_name* = $ptascii("class")
S_mutate.RESULT = KNOWN (PSTRING ptbytes_after)
$ptlc(ptbytes_after) = $ptascii("stdclass")
$lookup(S_mutate.ENV, n_name*) = (n_class_cell)
S_mutate.STORE[n_class_cell] = DEFINED (PSTRING ptbytes_before)
$lookup(S_mutate.ENV, $ptascii("api")) = (n_api_cell)
S_mutate.STORE[n_api_cell] = DEFINED (POBJECT n_api)
$heap_owners($heap_graph(S_mutate), HOBJECT n_api) = 1
$outputs(S_mutate.EVENTS) = $ptascii("Q;")
''') + step('S_changed', 'S_mutate') + lines(r'''
S_changed.TODO = ptask_mutate*
S_changed.STORE[n_class_cell] = DEFINED (PSTRING ptbytes_after)
S_changed.STORE[n_api_cell] = DEFINED (POBJECT n_api)
S_changed.OBJECTS = S_mutate.OBJECTS
S_changed.ALLOCATIONS = S_mutate.ALLOCATIONS
S_changed.EVENTS = S_mutate.EVENTS
$heap_owners($heap_graph(S_changed), HOBJECT n_api) = 1
$closure_callable(S_changed, n_api)
''')
    genuine += seek('S_config', 'S_changed', 2) + lines(r'''
S_config.TODO = (CONFIG_INVOKE pconfigcall_bind) :: ptask_config*
pconfigcall_bind.KIND = INTRINSIC_CLOSURE_BIND
pconfigcall_bind.OWNER = (n_api)
pconfigcall_bind.SELECTION = (n_api)
pconfigcall_bind.INDEX = 3 /\ pconfigcall_bind.PACKS = eps /\ ~pconfigcall_bind.NAMED
S_config.STORE[n_class_cell] = DEFINED (PSTRING ptbytes_after)
S_config.STORE[n_api_cell] = DEFINED (POBJECT n_api)
$lookup(S_config.ENV, $ptascii("body")) = (n_body_cell)
S_config.STORE[n_body_cell] = DEFINED (POBJECT n_body)
$lookup(S_config.ENV, $ptascii("receiver")) = (n_receiver_cell)
S_config.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver)
pconfigcall_bind.SENT = [NAMED_SENT (KNOWN (POBJECT n_body)), NAMED_SENT (KNOWN (POBJECT n_receiver)), NAMED_SENT (KNOWN PNULL)]
S_config.OBJECTS[n_api] = INTRINSICCLOSURE INTRINSIC_CLOSURE_BIND
S_config.OBJECTS[n_body] = REALCLOSURE porigin_body eps eps
S_config.OBJECTS[n_receiver] = STDINSTANCE
$config_selected_valid(S_config, pconfigcall_bind)
$config_invoke_valid(S_config, pconfigcall_bind)
$call_task_valid(S_config, CONFIG_INVOKE pconfigcall_bind)
$dynamic_site(S_config, (pconfigcall_bind.SITE))
$closure_binding_api_site(S_config, pconfigcall_bind.SITE)
$task_nodes(CONFIG_INVOKE pconfigcall_bind) = [HOBJECT n_api, HOBJECT n_body, HOBJECT n_receiver]
$heap_owners($heap_graph(S_config), HOBJECT n_api) = 2
$heap_owners($heap_graph(S_config), HOBJECT n_body) = 2
$heap_owners($heap_graph(S_config), HOBJECT n_receiver) = 2
S_config.CURRENT = eps /\ S_config.FRAMES = eps
S_config.FIBERSEQ = 1 /\ ~$destructor_operational(S_config)
S_config.DESTRUCTION.OPERATIONS = eps /\ S_config.DESTRUCTION.RELEASES = eps
$outputs(S_config.EVENTS) = $ptascii("Q;K:changed;C:held;B:held;P:held;A;")
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
S_zero = $drive_steps(S_config, 0)
S_zero = S_config[.COMPLETION = BUDGET]
S_done = $drive(S_result, 1500)
S_done.COMPLETION = NORMAL
S_done.CURRENT = eps /\ S_done.FRAMES = eps
S_done.TODO = eps /\ S_done.TRACE = eps
S_done = $drive(S_zero[.COMPLETION = NORMAL], 1500)
S_done = $drive(S_begin[.COMPLETION = NORMAL], 1500)
''') + [f'$outputs(S_done.EVENTS) = $ptascii("{expected}")'] + guards('S_done')
    controls = lines(r'''
~$closure_bind_capture(S_capture, phpType19, $ptascii("bind"), phpType7*, z_capture)
~$closure_bind_capture(S_class[.RESULT = KNOWN (PSTRING ($ptascii("stdClass")))], phpType19, $ptascii("bind"), phpType7*, z_capture)
~$closure_bind_capture(S_class[.RESULT = KNOWN PNULL], phpType19, $ptascii("bind"), phpType7*, z_capture)
~$closure_bind_capture(S_class[.COMPLETION = BUDGET], phpType19, $ptascii("bind"), phpType7*, z_capture)
~$closure_bind_capture(S_class[.ORIGIN = eps], phpType19, $ptascii("bind"), phpType7*, z_capture)
~$closure_bind_capture(S_class[.ORIGIN = (porigin_body)], phpType19, $ptascii("bind"), phpType7*, z_capture)
~$closure_bind_capture(S_class[.TODO = eps], phpType19, $ptascii("bind"), phpType7*, z_capture)
~$closure_bind_capture(S_class, phpType19, $ptascii("bindto"), phpType7*, z_capture)
~$closure_bind_capture(S_class, phpType19, $ptascii("bind"), eps, z_capture)
~$closure_bind_capture(S_class, phpType19, $ptascii("bind"), phpType7*, $(z_capture + 1))
~$closure_bind_capture(S_class[.SOURCES = eps], phpType19, $ptascii("bind"), phpType7*, z_capture)
phpType19_other = NExprVariable (BYTES "cmVjZWl2ZXI=") metadata_class
~$closure_bind_capture(S_class[.TODO = (SCOPED_CLASS phpType19_other phpType20 phpType7* z_capture) :: ptask_capture*], phpType19_other, $ptascii("bind"), phpType7*, z_capture)
''')
    checks = genuine + controls
    text = PREFIX[PREFIX.index('dec $outputs'):] + EXTRA + '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks, len(genuine), len(controls)
