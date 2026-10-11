"""Computed object-member CURRENT capture with its genuine request carrier and receiver-free mint."""
from error_handler_protocol import PREFIX
from closure_current_capture_review import guards, lines, step

EXTRA = r'''
dec $current_object_member_stage(pstate, nat) : bool
def $current_object_member_stage(S, 0) = true
  -- if S.TODO = (CONCAT_AFTER_RIGHT porigin_concat pvalue_left z) :: ptask*
  -- if $origin_node(S.SOURCES, porigin_concat) = (NExprBinaryOpConcat expression_left expression_right metadata)
def $current_object_member_stage(S, 1) = true
  -- if S.TODO = (METHOD_NAME poperand_selector phpType7* z) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprMethodCall expression_receiver (NExprBinaryOpConcat expression_left expression_right metadata_member) (SEQUENCE phpType7*) metadata)
def $current_object_member_stage(S, 2) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("left")
  -- if S.RESULT = KNOWN pvalue_left
  -- if $string_bytes(pvalue_left) = ($ptascii("bi"))
def $current_object_member_stage(S, 3) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("right")
  -- if S.RESULT = KNOWN pvalue_right
  -- if $string_bytes(pvalue_right) = ($ptascii("nd"))
def $current_object_member_stage(S, 4) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("selector")
  -- if S.RESULT = KNOWN PNULL
def $current_object_member_stage(S, 5) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_CLOSURE_CURRENT
def $current_object_member_stage(S, n) = false -- otherwise
dec $current_object_member_seek(pstate, nat, nat) : pstate
def $current_object_member_seek(S, n_stage, n) = S
  -- if $current_object_member_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $current_object_member_seek(S, n_stage, n) = $current_object_member_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$current_object_member_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $current_object_member_seek(S, n_stage, 0) = S
  -- if ~$current_object_member_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $current_object_member_seek(S, n_stage, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''


def seek(state, previous, stage):
    return [f'{state}_reached = $current_object_member_seek({previous}, {stage}, 1000)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$current_object_member_stage({state}, {stage})']


def render(program, filename, expected):
    genuine = [f'S_begin = $php_run({program}, 0, {filename})', 'S_begin.COMPLETION = BUDGET']
    genuine += seek('S_finish', 'S_begin', 0) + lines(r'''
S_finish.TODO = (CONCAT_AFTER_RIGHT porigin_concat pvalue_left z_concat) :: ptask_concat*
ptask_concat* = (ORIGIN_RETURN (porigin_capture)) :: (METHOD_NAME poperand_selector phpType7* z_capture) :: ptask_capture*
poperand_selector = VARIABLE n_selector_name* z_selector
S_finish.ORIGIN = (porigin_right)
$origin_child((porigin_concat), [PCFIELD 1]) = (porigin_right)
$origin_child((porigin_capture), [PCFIELD 1]) = (porigin_concat)
$origin_node(S_finish.SOURCES, porigin_capture) = (NExprMethodCall expression_receiver phpType20 (SEQUENCE phpType7*) metadata_capture)
phpType20 = NExprBinaryOpConcat expression_left expression_right metadata_method
expression_left = NExprVariable (BYTES text_left) metadata_left
expression_right = NExprVariable (BYTES text_right) metadata_right
$base64(text_left) = $ptascii("left")
$base64(text_right) = $ptascii("right")
$origin_node(S_finish.SOURCES, porigin_concat) = (phpType20)
expression_receiver = NExprVariable (BYTES text_receiver) metadata_receiver
n_selector_name* = $base64(text_receiver)
n_selector_name* = $ptascii("selector")
z_selector = $variable_line(BYTES text_receiver, metadata_receiver)
$lookup(S_finish.ENV, n_selector_name*) = (n_selector_cell)
S_finish.STORE[n_selector_cell] = DEFINED (POBJECT n_selector)
$object_body(S_finish.OBJECTS[n_selector]) = REALCLOSURE porigin_selector eps eps
$closure_callable(S_finish, n_selector)
$method_receiver_operand_valid(S_finish, expression_receiver, poperand_selector)
$heap_owners($heap_graph(S_finish), HOBJECT n_selector) = 1
$lookup(S_finish.ENV, $ptascii("weakSelector")) = (n_weak_selector_cell)
S_finish.STORE[n_weak_selector_cell] = DEFINED (POBJECT n_weak_selector)
$weakref_get(S_finish, n_weak_selector) = POBJECT n_selector
$lookup(S_finish.ENV, $ptascii("left")) = (n_left_cell)
$lookup(S_finish.ENV, $ptascii("right")) = (n_right_cell)
pvalue_left = PSTRING_CARRIER INTERNED_STRING ($ptascii("get"))
S_finish.STORE[n_left_cell] = DEFINED pvalue_left
S_finish.RESULT = KNOWN pvalue_right
pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("Current"))
S_finish.STORE[n_right_cell] = DEFINED pvalue_right
$concat_right_child_valid(S_finish, porigin_concat, porigin_right, z_concat)
~$concat_constant(S_finish, $origin_child((porigin_concat), [PCFIELD 0]))
~$concat_constant(S_finish, $origin_child((porigin_concat), [PCFIELD 1]))
$outputs(S_finish.EVENTS) = $ptascii("Q;")
n_string = |S_finish.STRINGDATA|
S_derived_concat = $string_concat(S_finish, pvalue_left, pvalue_right, false, false)
S_derived_concat.RESULT = KNOWN (PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("getCurrent")))
S_derived_concat.STRINGDATA = S_finish.STRINGDATA ++ [$ptascii("getCurrent")]
''') + guards('S_finish') + step('S_concatenated', 'S_finish') + lines(r'''
S_raw_concat = S_derived_concat[.ORIGIN = (porigin_concat)][.TODO = ptask_concat*][.BASE = BASE_VALUE S_derived_concat.RESULT]
S_concatenated = $destruction_store_new(S_raw_concat)
S_concatenated.RESULT = S_derived_concat.RESULT
S_concatenated.OBJECTS = S_finish.OBJECTS
S_concatenated.STORE = S_finish.STORE /\ S_concatenated.ENV = S_finish.ENV
S_concatenated.EVENTS = S_finish.EVENTS
''')
    genuine += seek('S_capture', 'S_concatenated', 1) + lines(r'''
S_capture.TODO = (METHOD_NAME poperand_selector phpType7* z_capture) :: ptask_capture*
S_capture.ORIGIN = (porigin_capture)
S_capture.RESULT = S_concatenated.RESULT
S_capture.STRINGDATA = S_concatenated.STRINGDATA
S_capture.STORE = S_concatenated.STORE /\ S_capture.ENV = S_concatenated.ENV
$property_computed_name(phpType20)
$call_task_valid(S_capture, METHOD_NAME poperand_selector phpType7* z_capture)
$method_name_task(S_capture, poperand_selector, phpType7*, z_capture)
$ppfirstclass(phpType7*)
$call_line_valid(S_capture, (porigin_capture), z_capture)
$method_receiver_operand_valid(S_capture, expression_receiver, poperand_selector)
porigin_concat = PORIGIN n_member_unit pcpath_member
$code_at(S_capture.CODE, n_member_unit) = (pcode_member)
$code_expression(pcode_member.EXPRESSIONS, pcpath_member) = ((z_member, b_member))
S_name = $resolve_at(S_capture, S_capture.RESULT, z_capture)
S_name = S_capture
S_name.RESULT = KNOWN pvalue_selected
$string_bytes(pvalue_selected) = (ptbytes_method)
ptbytes_method = $ptascii("getCurrent")
$string_carrier_valid(S_name, pvalue_selected)
$heap_owners($heap_graph(S_name), HOBJECT n_selector) = 1
S_receiver = $resolve_at(S_name, poperand_selector, z_capture)
S_receiver.COMPLETION = NORMAL
S_receiver.RESULT = KNOWN (POBJECT n_selector)
S_receiver.TODO = S_name.TODO /\ S_receiver.ORIGIN = S_name.ORIGIN
S_receiver.STORE = S_name.STORE /\ S_receiver.ENV = S_name.ENV
S_receiver.OBJECTS = S_name.OBJECTS /\ S_receiver.ALLOCATIONS = S_name.ALLOCATIONS
$heap_owners($heap_graph(S_receiver), HOBJECT n_selector) = 2
$call_task_valid(S_receiver, METHOD_NAME poperand_selector phpType7* z_capture)
$closure_current_method_capture(S_receiver, poperand_selector, ptbytes_method, phpType7*, z_capture)
$outputs(S_capture.EVENTS) = $ptascii("Q;")
n_api = |S_capture.OBJECTS|
''') + guards('S_capture') + step('S_minted', 'S_capture') + lines(r'''
S_prepared_mint = $method_select(S_name, poperand_selector, ptbytes_method, phpType7*, z_capture)
S_minted = $destruction_store_new(S_prepared_mint)
S_minted.TODO = ptask_capture*
S_minted.RESULT = KNOWN (POBJECT n_api)
S_minted.OBJECTS = S_capture.OBJECTS ++ [INTRINSICCLOSURE INTRINSIC_CLOSURE_CURRENT]
(HOBJECT n_api) <- S_minted.ALLOCATIONS
$node_children(S_minted, HOBJECT n_api) = eps
$heap_owners($heap_graph(S_minted), HOBJECT n_selector) = 1
$heap_owners($heap_graph(S_minted), HOBJECT n_api) = 1
$closure_callable(S_minted, n_api)
$closure_live_object_valid(S_minted, n_api)
''')
    for label, previous, stage, name, cell, before, after in [
        ('S_left', 'S_minted', 2, 'left', 'n_left_cell', 'pvalue_left', 'bi'),
        ('S_right', 'S_left_changed', 3, 'right', 'n_right_cell', 'pvalue_right', 'nd')]:
        changed = label + '_changed'
        genuine += seek(label, previous, stage) + [
            f'{label}.TODO = (WRITE_NAME n_name_{name}* z_{name}) :: ptask_{name}*',
            f'n_name_{name}* = $ptascii("{name}")',
            f'{label}.RESULT = KNOWN pvalue_after_{name}',
            f'$string_bytes(pvalue_after_{name}) = ($ptascii("{after}"))',
            f'$lookup({label}.ENV, n_name_{name}*) = ({cell})',
            f'{label}.STORE[{cell}] = DEFINED {before}',
            f'$lookup({label}.ENV, $ptascii("api")) = (n_api_cell)',
            f'{label}.STORE[n_api_cell] = DEFINED (POBJECT n_api)',
            f'$heap_owners($heap_graph({label}), HOBJECT n_api) = 1',
            f'$outputs({label}.EVENTS) = $ptascii("Q;")']
        genuine += step(changed, label) + [
            f'{changed}.TODO = ptask_{name}*',
            f'{changed}.STORE[{cell}] = DEFINED pvalue_after_{name}',
            f'{changed}.STORE[n_api_cell] = DEFINED (POBJECT n_api)',
            f'{changed}.OBJECTS = {label}.OBJECTS',
            f'{changed}.ALLOCATIONS = {label}.ALLOCATIONS',
            f'{changed}.EVENTS = {label}.EVENTS',
            f'$heap_owners($heap_graph({changed}), HOBJECT n_api) = 1',
            f'$closure_callable({changed}, n_api)']
    genuine += seek('S_clear', 'S_right_changed', 4) + lines(r'''
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
$outputs(S_clear.EVENTS) = $ptascii("Q;M:changed;")
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
    genuine += seek('S_config', 'S_gone', 5) + lines(r'''
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
$weakref_get(S_config, n_weak_selector) = PNULL
$lookup(psymboltable_global.ENV, $ptascii("left")) = (n_left_cell)
S_config.STORE[n_left_cell] = DEFINED pvalue_after_left
$lookup(psymboltable_global.ENV, $ptascii("right")) = (n_right_cell)
S_config.STORE[n_right_cell] = DEFINED pvalue_after_right
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
$dynamic_site(S_config, (pconfigcall_current.SITE))
$task_nodes(CONFIG_INVOKE pconfigcall_current) = [HOBJECT n_api]
$heap_owners($heap_graph(S_config), HOBJECT n_api) = 2
$heap_owners($heap_graph(S_config), HOBJECT n_body) = 1
$outputs(S_config.EVENTS) = $ptascii("Q;M:changed;S:gone;A;B;C:held;")
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
    controls = lines(r"""
~$closure_current_method_capture(S_capture, poperand_selector, ptbytes_method, phpType7*, z_capture)
~$closure_current_method_capture(S_receiver[.TODO = (METHOD_NAME (VARIABLE ($ptascii("api")) z_selector) phpType7* z_capture) :: ptask_capture*], VARIABLE ($ptascii("api")) z_selector, ptbytes_method, phpType7*, z_capture)
~$closure_current_method_capture(S_receiver[.TODO = (METHOD_NAME (VARIABLE n_selector_name* $(z_selector + 1)) phpType7* z_capture) :: ptask_capture*], VARIABLE n_selector_name* $(z_selector + 1), ptbytes_method, phpType7*, z_capture)
~$closure_current_method_capture(S_receiver[.TODO = (METHOD_NAME (KNOWN (POBJECT n_selector)) phpType7* z_capture) :: ptask_capture*], KNOWN (POBJECT n_selector), ptbytes_method, phpType7*, z_capture)
~$closure_current_method_capture(S_receiver[.RESULT = KNOWN PNULL], poperand_selector, ptbytes_method, phpType7*, z_capture)
~$closure_current_method_capture(S_receiver[.RESULT = KNOWN (POBJECT n_weak_selector)], poperand_selector, ptbytes_method, phpType7*, z_capture)
~$closure_current_method_capture(S_receiver[.ALLOCATIONS = eps], poperand_selector, ptbytes_method, phpType7*, z_capture)
~$closure_current_method_capture(S_receiver[.COMPLETION = BUDGET], poperand_selector, ptbytes_method, phpType7*, z_capture)
~$closure_current_method_capture(S_receiver[.ORIGIN = eps], poperand_selector, ptbytes_method, phpType7*, z_capture)
~$closure_current_method_capture(S_receiver[.ORIGIN = (porigin_body)], poperand_selector, ptbytes_method, phpType7*, z_capture)
~$closure_current_method_capture(S_receiver[.TODO = eps], poperand_selector, ptbytes_method, phpType7*, z_capture)
~$closure_current_method_capture(S_receiver[.TODO = (METHOD_PREP phpType20 phpType7* false false z_capture) :: ptask_capture*], poperand_selector, ptbytes_method, phpType7*, z_capture)
~$closure_current_method_capture(S_receiver, poperand_selector, $ptascii("bind"), phpType7*, z_capture)
~$closure_current_method_capture(S_receiver, poperand_selector, ptbytes_method, eps, z_capture)
~$closure_current_method_capture(S_receiver, poperand_selector, ptbytes_method, phpType7*, $(z_capture + 1))
~$closure_current_method_capture(S_receiver[.SOURCES = eps], poperand_selector, ptbytes_method, phpType7*, z_capture)
~$closure_current_method_capture(S_receiver[.CODE = eps], poperand_selector, ptbytes_method, phpType7*, z_capture)
S_receiver.ORIGIN = (PORIGIN n_unit pcpath)
S_receiver.SOURCES = pcunit :: pcunit_tail*
pcunit.ID = n_unit
S_other_source = S_receiver[.SOURCES = pcunit[.OCCURRENCES = [PCOCCURRENCE pcpath (NExprMethodCall expression_receiver (NIdentifier (BYTES "Z2V0Q3VycmVudA==") metadata_method) (SEQUENCE phpType7*) metadata_capture)]] :: pcunit_tail*]
~$closure_current_method_capture(S_other_source, poperand_selector, ptbytes_method, phpType7*, z_capture)
""")
    checks = genuine + controls
    text = PREFIX[PREFIX.index('dec $outputs'):] + EXTRA + '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks, len(genuine), len(controls)
