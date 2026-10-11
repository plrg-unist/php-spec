"""Simple class-CV CURRENT capture and genuine frozen current-body selection."""
from error_handler_protocol import PREFIX
from closure_current_capture_review import guards, lines, step

EXTRA = r'''
dec $current_class_stage(pstate, nat) : bool
def $current_class_stage(S, 0) = true
  -- if S.TODO = (SCOPED_CLASS phpType19 phpType20 phpType7* z) :: ptask*
  -- if phpType19 = NExprVariable (BYTES text_class) metadata_class
  -- if phpType20 = NIdentifier (BYTES text_method) metadata_method
  -- if $ptlc($base64(text_method)) = $ptascii("getcurrent")
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprStaticCall phpType19 phpType20 (SEQUENCE phpType7*) metadata)
  -- if $ppfirstclass(phpType7*)
def $current_class_stage(S, 1) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("class")
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("stdClass"))
def $current_class_stage(S, 2) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_CLOSURE_CURRENT
def $current_class_stage(S, n) = false -- otherwise
dec $current_class_seek(pstate, nat, nat) : pstate
def $current_class_seek(S, n_stage, n) = S
  -- if $current_class_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $current_class_seek(S, n_stage, n) = $current_class_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$current_class_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $current_class_seek(S, n_stage, 0) = S
  -- if ~$current_class_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $current_class_seek(S, n_stage, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''


def seek(state, previous, stage):
    return [f'{state}_reached = $current_class_seek({previous}, {stage}, 1000)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$current_class_stage({state}, {stage})']


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
$ptlc($base64(text_method)) = $ptascii("getcurrent")
$lookup(S_capture.ENV, n_class_name*) = (n_class_cell)
S_capture.STORE[n_class_cell] = DEFINED pvalue_before
$string_bytes(pvalue_before) = ($ptascii("Closure"))
$call_task_valid(S_capture, SCOPED_CLASS phpType19 phpType20 phpType7* z_capture)
$call_line_valid(S_capture, (porigin_capture), z_capture)
$ppfirstclass(phpType7*)
~$ppscoped_named(phpType19)
S_class = $scoped_class_prepare(S_capture, phpType19, z_capture)
S_class.COMPLETION = NORMAL
S_class.RESULT = KNOWN (PSTRING ($ptascii("Closure")))
S_class.TODO = S_capture.TODO /\ S_class.ORIGIN = S_capture.ORIGIN
S_class.STORE = S_capture.STORE /\ S_class.ENV = S_capture.ENV
$heap_graph(S_class) = $heap_graph(S_capture)
$closure_current_capture_site(S_class, porigin_capture)
$closure_current_capture(S_class, phpType19, $ptascii("getcurrent"), phpType7*, z_capture)
S_capture.CURRENT = eps /\ S_capture.FRAMES = eps
$outputs(S_capture.EVENTS) = $ptascii("Q;")
n_api = |S_capture.OBJECTS|
''') + guards('S_capture') + step('S_minted', 'S_capture') + lines(r'''
S_prepared_mint = $scoped_name_prepare(S_class, phpType19, S_class.RESULT, phpType20, phpType7*, z_capture)
S_minted = $destruction_store_new(S_prepared_mint)
S_minted.TODO = ptask_capture*
S_minted.RESULT = KNOWN (POBJECT n_api)
S_minted.OBJECTS = S_capture.OBJECTS ++ [INTRINSICCLOSURE INTRINSIC_CLOSURE_CURRENT]
S_minted.CURRENT = S_capture.CURRENT /\ S_minted.FRAMES = S_capture.FRAMES
(HOBJECT n_api) <- S_minted.ALLOCATIONS
$node_children(S_minted, HOBJECT n_api) = eps
$heap_owners($heap_graph(S_minted), HOBJECT n_api) = 1
$closure_callable(S_minted, n_api)
$closure_live_object_valid(S_minted, n_api)
''')
    genuine += seek('S_mutate', 'S_minted', 1) + lines(r'''
S_mutate.TODO = (WRITE_NAME n_name* z_mutate) :: ptask_mutate*
n_name* = n_class_name*
S_mutate.RESULT = KNOWN pvalue_after
$string_bytes(pvalue_after) = ($ptascii("stdClass"))
$lookup(S_mutate.ENV, n_name*) = (n_class_cell)
S_mutate.STORE[n_class_cell] = DEFINED pvalue_before
$lookup(S_mutate.ENV, $ptascii("api")) = (n_api_cell)
S_mutate.STORE[n_api_cell] = DEFINED (POBJECT n_api)
$heap_owners($heap_graph(S_mutate), HOBJECT n_api) = 1
$outputs(S_mutate.EVENTS) = $ptascii("Q;")
''') + step('S_changed', 'S_mutate') + lines(r'''
S_changed.TODO = ptask_mutate*
S_changed.STORE[n_class_cell] = DEFINED pvalue_after
S_changed.STORE[n_api_cell] = DEFINED (POBJECT n_api)
S_changed.OBJECTS = S_mutate.OBJECTS
S_changed.ALLOCATIONS = S_mutate.ALLOCATIONS
S_changed.EVENTS = S_mutate.EVENTS
$heap_owners($heap_graph(S_changed), HOBJECT n_api) = 1
$closure_callable(S_changed, n_api)
''')
    genuine += seek('S_config', 'S_changed', 2) + lines(r'''
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
$lookup(psymboltable_global.ENV, n_class_name*) = (n_class_cell)
S_config.STORE[n_class_cell] = DEFINED pvalue_after
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
$outputs(S_config.EVENTS) = $ptascii("Q;K:changed;A;B;C:held;")
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
~(HOBJECT n_api <- S_done.ALLOCATIONS)
~(HOBJECT n_body <- S_done.ALLOCATIONS)
$weakref_get(S_done, n_weak_api) = PNULL
$weakref_get(S_done, n_weak_body) = PNULL
S_done = $drive(S_zero[.COMPLETION = NORMAL], 1500)
S_done = $drive(S_begin[.COMPLETION = NORMAL], 1500)
''') + [f'$outputs(S_done.EVENTS) = $ptascii("{expected}")'] + guards('S_done')
    controls = lines(r'''
~$closure_current_capture(S_capture, phpType19, $ptascii("getcurrent"), phpType7*, z_capture)
~$closure_current_capture_site(S_class[.RESULT = KNOWN PNULL], porigin_capture)
~$closure_current_capture_site(S_class[.RESULT = KNOWN (PSTRING ($ptascii("stdClass")))], porigin_capture)
~$closure_current_capture(S_class[.COMPLETION = BUDGET], phpType19, $ptascii("getcurrent"), phpType7*, z_capture)
~$closure_current_capture(S_class[.ORIGIN = eps], phpType19, $ptascii("getcurrent"), phpType7*, z_capture)
~$closure_current_capture(S_class[.ORIGIN = (porigin_body)], phpType19, $ptascii("getcurrent"), phpType7*, z_capture)
~$closure_current_capture(S_class[.TODO = eps], phpType19, $ptascii("getcurrent"), phpType7*, z_capture)
~$closure_current_capture(S_class, phpType19, $ptascii("bind"), phpType7*, z_capture)
~$closure_current_capture(S_class, phpType19, $ptascii("getcurrent"), eps, z_capture)
~$closure_current_capture(S_class, phpType19, $ptascii("getcurrent"), phpType7*, $(z_capture + 1))
~$closure_current_capture(S_class[.SOURCES = eps], phpType19, $ptascii("getcurrent"), phpType7*, z_capture)
~$closure_current_capture(S_class[.CODE = eps], phpType19, $ptascii("getcurrent"), phpType7*, z_capture)
phpType19_other = NExprVariable (BYTES "cmVjZWl2ZXI=") metadata_class
~$closure_current_capture(S_class[.TODO = (SCOPED_CLASS phpType19_other phpType20 phpType7* z_capture) :: ptask_capture*], phpType19_other, $ptascii("getcurrent"), phpType7*, z_capture)
''')
    checks = genuine + controls
    text = PREFIX[PREFIX.index('dec $outputs'):] + EXTRA + '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks, len(genuine), len(controls)
