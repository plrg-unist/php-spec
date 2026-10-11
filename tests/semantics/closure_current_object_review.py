"""Object-form static CURRENT capture without retaining its selector Closure."""
from error_handler_protocol import PREFIX
from closure_current_capture_review import guards, lines, step

EXTRA = r'''
dec $current_object_stage(pstate, nat) : bool
def $current_object_stage(S, 0) = true
  -- if S.TODO = (METHOD_PREP phpType20 phpType7* false false z) :: ptask*
  -- if phpType20 = NIdentifier (BYTES text_method) metadata_method
  -- if $ptlc($base64(text_method)) = $ptascii("getcurrent")
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprMethodCall expression phpType20 (SEQUENCE phpType7*) metadata)
  -- if $ppfirstclass(phpType7*)
def $current_object_stage(S, 1) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("selector")
  -- if S.RESULT = KNOWN PNULL
def $current_object_stage(S, 2) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_CLOSURE_CURRENT
def $current_object_stage(S, n) = false -- otherwise
dec $current_object_seek(pstate, nat, nat) : pstate
def $current_object_seek(S, n_stage, n) = S
  -- if $current_object_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $current_object_seek(S, n_stage, n) = $current_object_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$current_object_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $current_object_seek(S, n_stage, 0) = S
  -- if ~$current_object_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $current_object_seek(S, n_stage, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''


def seek(state, previous, stage):
    return [f'{state}_reached = $current_object_seek({previous}, {stage}, 1000)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$current_object_stage({state}, {stage})']


def render(program, filename, expected):
    genuine = [f'S_begin = $php_run({program}, 0, {filename})', 'S_begin.COMPLETION = BUDGET']
    genuine += seek('S_capture', 'S_begin', 0) + lines(r'''
S_capture.TODO = (METHOD_PREP phpType20 phpType7* false false z_capture) :: ptask_capture*
S_capture.ORIGIN = (porigin_capture)
$origin_node(S_capture.SOURCES, porigin_capture) = (NExprMethodCall expression_receiver phpType20 (SEQUENCE phpType7*) metadata_capture)
expression_receiver = NExprVariable (BYTES text_receiver) metadata_receiver
$base64(text_receiver) = $ptascii("selector")
phpType20 = NIdentifier (BYTES text_method) metadata_method
$ptlc($base64(text_method)) = $ptascii("getcurrent")
S_capture.RESULT = VARIABLE n_selector_name* z_selector
n_selector_name* = $base64(text_receiver)
z_selector = $variable_line(BYTES text_receiver, metadata_receiver)
$lookup(S_capture.ENV, n_selector_name*) = (n_selector_cell)
S_capture.STORE[n_selector_cell] = DEFINED (POBJECT n_selector)
$object_body(S_capture.OBJECTS[n_selector]) = REALCLOSURE porigin_selector eps eps
$closure_callable(S_capture, n_selector)
$heap_owners($heap_graph(S_capture), HOBJECT n_selector) = 1
$lookup(S_capture.ENV, $ptascii("weakSelector")) = (n_weak_selector_cell)
S_capture.STORE[n_weak_selector_cell] = DEFINED (POBJECT n_weak_selector)
$weakref_get(S_capture, n_weak_selector) = POBJECT n_selector
$call_task_valid(S_capture, METHOD_PREP phpType20 phpType7* false false z_capture)
$method_receiver_operand_valid(S_capture, expression_receiver, S_capture.RESULT)
$ppfirstclass(phpType7*)
S_receiver = $resolve_at(S_capture, S_capture.RESULT, z_capture)
S_receiver.COMPLETION = NORMAL
S_receiver.RESULT = KNOWN (POBJECT n_selector)
S_receiver.TODO = S_capture.TODO /\ S_receiver.ORIGIN = S_capture.ORIGIN
S_receiver.STORE = S_capture.STORE /\ S_receiver.ENV = S_capture.ENV
S_receiver.OBJECTS = S_capture.OBJECTS /\ S_receiver.ALLOCATIONS = S_capture.ALLOCATIONS
$heap_owners($heap_graph(S_receiver), HOBJECT n_selector) = 2
$closure_current_method_capture(S_receiver, S_capture.RESULT, $ptascii("getcurrent"), phpType7*, z_capture)
S_capture.CURRENT = eps /\ S_capture.FRAMES = eps
$outputs(S_capture.EVENTS) = $ptascii("Q;")
n_api = |S_capture.OBJECTS|
''') + guards('S_capture') + step('S_minted', 'S_capture') + lines(r'''
S_raw_mint = $method_prepare(S_capture, phpType20, phpType7*, false, false, z_capture)
S_minted = $destruction_store_new(S_raw_mint)
S_minted.TODO = ptask_capture*
S_minted.RESULT = KNOWN (POBJECT n_api)
S_minted.OBJECTS = S_capture.OBJECTS ++ [INTRINSICCLOSURE INTRINSIC_CLOSURE_CURRENT]
S_minted.CURRENT = S_capture.CURRENT /\ S_minted.FRAMES = S_capture.FRAMES
(HOBJECT n_api) <- S_minted.ALLOCATIONS
$node_children(S_minted, HOBJECT n_api) = eps
$heap_owners($heap_graph(S_minted), HOBJECT n_api) = 1
$heap_owners($heap_graph(S_minted), HOBJECT n_selector) = 1
$closure_callable(S_minted, n_api)
$closure_live_object_valid(S_minted, n_api)
''') + guards('S_minted')
    genuine += seek('S_clear', 'S_minted', 1) + lines(r'''
S_clear.TODO = (WRITE_NAME n_selector_name* z_clear) :: ptask_clear*
S_clear.RESULT = KNOWN PNULL
$lookup(S_clear.ENV, n_selector_name*) = (n_selector_cell)
S_clear.STORE[n_selector_cell] = DEFINED (POBJECT n_selector)
$lookup(S_clear.ENV, $ptascii("api")) = (n_api_cell)
S_clear.STORE[n_api_cell] = DEFINED (POBJECT n_api)
S_clear.STORE[n_weak_selector_cell] = DEFINED (POBJECT n_weak_selector)
$weakref_get(S_clear, n_weak_selector) = POBJECT n_selector
$node_children(S_clear, HOBJECT n_api) = eps
$heap_owners($heap_graph(S_clear), HOBJECT n_selector) = 1
$heap_owners($heap_graph(S_clear), HOBJECT n_api) = 1
S_clear.CURRENT = eps /\ S_clear.FRAMES = eps
~$destructor_operational(S_clear)
S_clear.DESTRUCTION.OPERATIONS = eps /\ S_clear.DESTRUCTION.RELEASES = eps
$outputs(S_clear.EVENTS) = $ptascii("Q;")
''') + guards('S_clear') + step('S_gone', 'S_clear') + lines(r'''
S_gone.TODO = ptask_clear*
S_gone.RESULT = KNOWN PNULL
S_gone.STORE[n_selector_cell] = DEFINED PNULL
S_gone.STORE[n_api_cell] = DEFINED (POBJECT n_api)
S_gone.OBJECTS = S_clear.OBJECTS
S_gone.CURRENT = S_clear.CURRENT /\ S_gone.FRAMES = S_clear.FRAMES
S_gone.EVENTS = S_clear.EVENTS
~(HOBJECT n_selector <- S_gone.ALLOCATIONS)
$heap_owners($heap_graph(S_gone), HOBJECT n_selector) = 0
$weakref_get(S_gone, n_weak_selector) = PNULL
(HOBJECT n_api) <- S_gone.ALLOCATIONS
$heap_owners($heap_graph(S_gone), HOBJECT n_api) = 1
$node_children(S_gone, HOBJECT n_api) = eps
S_gone.DESTRUCTION.OPERATIONS = eps /\ S_gone.DESTRUCTION.RELEASES = eps
''') + guards('S_gone')
    genuine += seek('S_config', 'S_gone', 2) + lines(r'''
S_config.TODO = (CONFIG_INVOKE pconfigcall_current) :: ptask_config*
pconfigcall_current.KIND = INTRINSIC_CLOSURE_CURRENT
pconfigcall_current.OWNER = (n_api)
pconfigcall_current.SELECTION = (n_api)
pconfigcall_current.SENT = eps /\ pconfigcall_current.INDEX = 0
pconfigcall_current.PACKS = eps /\ ~pconfigcall_current.NAMED
S_config.OBJECTS[n_api] = INTRINSICCLOSURE INTRINSIC_CLOSURE_CURRENT
$lookup(S_config.ENV, $ptascii("picked")) = (n_picked_cell)
S_config.STORE[n_picked_cell] = DEFINED (POBJECT n_api)
S_config.GLOBALTABLE = (psymboltable_global)
$lookup(psymboltable_global.ENV, n_selector_name*) = (n_selector_cell)
S_config.STORE[n_selector_cell] = DEFINED PNULL
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
n_api =/= n_body /\ n_body =/= n_selector
$object_body(S_config.OBJECTS[n_body]) = REALCLOSURE porigin_body eps eps
S_config.CURRENT = (pcallcontext_body)
pcallcontext_body.TARGET = CLOSURE_TARGET n_body
pcallcontext_body.INSTANCE = (n_body)
S_config.FRAMES = [pframe_main]
pframe_main.CONTEXT = eps /\ pframe_main.LOCALS = eps
$closure_current_object(S_config) = (n_body)
$config_selected_valid(S_config, pconfigcall_current)
$config_invoke_valid(S_config, pconfigcall_current)
$call_task_valid(S_config, CONFIG_INVOKE pconfigcall_current)
$task_nodes(CONFIG_INVOKE pconfigcall_current) = [HOBJECT n_api]
$heap_owners($heap_graph(S_config), HOBJECT n_api) = 2
$heap_owners($heap_graph(S_config), HOBJECT n_body) = 1
$outputs(S_config.EVENTS) = $ptascii("Q;S:gone;A;B;C:held;")
''') + guards('S_config') + step('S_result', 'S_config') + lines(r'''
S_result.RESULT = KNOWN (POBJECT n_body)
S_result.TODO = ptask_config*
S_result.CURRENT = S_config.CURRENT /\ S_result.FRAMES = S_config.FRAMES
S_result.OBJECTS = S_config.OBJECTS /\ S_result.ARRAYS = S_config.ARRAYS
S_result.STORE = S_config.STORE /\ S_result.ALLOCATIONS = S_config.ALLOCATIONS
$closure_current_object(S_result) = (n_body)
$heap_owners($heap_graph(S_result), HOBJECT n_api) = 1
$heap_owners($heap_graph(S_result), HOBJECT n_body) = 2
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
~$closure_current_method_capture(S_capture, S_capture.RESULT, $ptascii("getcurrent"), phpType7*, z_capture)
~$closure_current_method_capture(S_receiver, VARIABLE ($ptascii("api")) z_selector, $ptascii("getcurrent"), phpType7*, z_capture)
~$closure_current_method_capture(S_receiver, VARIABLE n_selector_name* $(z_selector + 1), $ptascii("getcurrent"), phpType7*, z_capture)
~$closure_current_method_capture(S_receiver, KNOWN (POBJECT n_selector), $ptascii("getcurrent"), phpType7*, z_capture)
~$closure_current_method_capture(S_receiver[.RESULT = KNOWN PNULL], S_capture.RESULT, $ptascii("getcurrent"), phpType7*, z_capture)
~$closure_current_method_capture(S_receiver[.RESULT = KNOWN (POBJECT n_weak_selector)], S_capture.RESULT, $ptascii("getcurrent"), phpType7*, z_capture)
~$closure_current_method_capture(S_receiver[.ALLOCATIONS = eps], S_capture.RESULT, $ptascii("getcurrent"), phpType7*, z_capture)
~$closure_current_method_capture(S_receiver[.COMPLETION = BUDGET], S_capture.RESULT, $ptascii("getcurrent"), phpType7*, z_capture)
~$closure_current_method_capture(S_receiver[.ORIGIN = eps], S_capture.RESULT, $ptascii("getcurrent"), phpType7*, z_capture)
~$closure_current_method_capture(S_receiver[.ORIGIN = (porigin_body)], S_capture.RESULT, $ptascii("getcurrent"), phpType7*, z_capture)
~$closure_current_method_capture(S_receiver[.TODO = eps], S_capture.RESULT, $ptascii("getcurrent"), phpType7*, z_capture)
~$closure_current_method_capture(S_receiver, S_capture.RESULT, $ptascii("bind"), phpType7*, z_capture)
~$closure_current_method_capture(S_receiver, S_capture.RESULT, $ptascii("getcurrent"), eps, z_capture)
~$closure_current_method_capture(S_receiver, S_capture.RESULT, $ptascii("getcurrent"), phpType7*, $(z_capture + 1))
~$closure_current_method_capture(S_receiver[.SOURCES = eps], S_capture.RESULT, $ptascii("getcurrent"), phpType7*, z_capture)
~$closure_current_method_capture(S_receiver[.CODE = eps], S_capture.RESULT, $ptascii("getcurrent"), phpType7*, z_capture)
~$closure_current_method_capture(S_receiver[.TODO = (METHOD_PREP phpType20 phpType7* true false z_capture) :: ptask_capture*], S_capture.RESULT, $ptascii("getcurrent"), phpType7*, z_capture)
~$closure_current_method_capture(S_receiver[.TODO = (METHOD_PREP phpType20 phpType7* false true z_capture) :: ptask_capture*], S_capture.RESULT, $ptascii("getcurrent"), phpType7*, z_capture)
phpType20_other = NIdentifier (BYTES "YmluZA==") metadata_method
~$closure_current_method_capture(S_receiver[.TODO = (METHOD_PREP phpType20_other phpType7* false false z_capture) :: ptask_capture*], S_capture.RESULT, $ptascii("getcurrent"), phpType7*, z_capture)
''')
    checks = genuine + controls
    text = PREFIX[PREFIX.index('dec $outputs'):] + EXTRA + '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks, len(genuine), len(controls)
