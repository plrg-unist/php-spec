"""Computed member bind capture, genuine concat carrier and frozen API identity."""
from error_handler_protocol import PREFIX
from closure_bind_capture_review import guards, lines, step

EXTRA = r'''
dec $bind_member_expression_stage(pstate, nat) : bool
def $bind_member_expression_stage(S, 0) = true
  -- if S.TODO = (CONCAT_AFTER_RIGHT porigin_concat pvalue_left z) :: ptask*
  -- if $origin_node(S.SOURCES, porigin_concat) = (NExprBinaryOpConcat expression_left expression_right metadata)
def $bind_member_expression_stage(S, 1) = true
  -- if S.TODO = (SCOPED_NAME phpType19 poperand_selector phpType7* z) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprStaticCall phpType19 (NExprBinaryOpConcat expression_left expression_right metadata_member) (SEQUENCE phpType7*) metadata)
def $bind_member_expression_stage(S, 2) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("left")
  -- if S.RESULT = KNOWN pvalue_left
  -- if $string_bytes(pvalue_left) = ($ptascii("get"))
def $bind_member_expression_stage(S, 3) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("right")
  -- if S.RESULT = KNOWN pvalue_right
  -- if $string_bytes(pvalue_right) = ($ptascii("Current"))
def $bind_member_expression_stage(S, 4) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_CLOSURE_BIND
def $bind_member_expression_stage(S, n) = false -- otherwise
dec $bind_member_expression_seek(pstate, nat, nat) : pstate
def $bind_member_expression_seek(S, n_stage, n) = S
  -- if $bind_member_expression_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $bind_member_expression_seek(S, n_stage, n) = $bind_member_expression_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$bind_member_expression_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $bind_member_expression_seek(S, n_stage, 0) = S
  -- if ~$bind_member_expression_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $bind_member_expression_seek(S, n_stage, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''


def seek(state, previous, stage):
    return [f'{state}_reached = $bind_member_expression_seek({previous}, {stage}, 1000)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$bind_member_expression_stage({state}, {stage})']


def render(program, filename, expected):
    genuine = [f'S_begin = $php_run({program}, 0, {filename})', 'S_begin.COMPLETION = BUDGET']
    genuine += seek('S_finish', 'S_begin', 0) + lines(r'''
S_finish.TODO = (CONCAT_AFTER_RIGHT porigin_concat pvalue_left z_concat) :: ptask_concat*
ptask_concat* = (ORIGIN_RETURN (porigin_capture)) :: (SCOPED_NAME phpType19 poperand_selector phpType7* z_capture) :: ptask_capture*
poperand_selector = KNOWN (PSTRING ptbytes_class)
$ptlc($typed_callable_name(ptbytes_class)) = $ptascii("closure")
S_finish.ORIGIN = (porigin_right)
$origin_child((porigin_concat), [PCFIELD 1]) = (porigin_right)
$origin_child((porigin_capture), [PCFIELD 1]) = (porigin_concat)
$origin_node(S_finish.SOURCES, porigin_capture) = (NExprStaticCall phpType19 phpType20 (SEQUENCE phpType7*) metadata_capture)
phpType20 = NExprBinaryOpConcat expression_left expression_right metadata_method
expression_left = NExprVariable (BYTES text_left) metadata_left
expression_right = NExprVariable (BYTES text_right) metadata_right
$base64(text_left) = $ptascii("left")
$base64(text_right) = $ptascii("right")
$origin_node(S_finish.SOURCES, porigin_concat) = (phpType20)
$ppscoped_named(phpType19) /\ ~$ppscoped_keyword(phpType19)
$scoped_source_name(S_finish[.ORIGIN = (porigin_capture)], phpType19) = (ptbytes_class)
$lookup(S_finish.ENV, $ptascii("left")) = (n_left_cell)
$lookup(S_finish.ENV, $ptascii("right")) = (n_right_cell)
pvalue_left = PSTRING_CARRIER INTERNED_STRING ($ptascii("bi"))
S_finish.STORE[n_left_cell] = DEFINED pvalue_left
S_finish.RESULT = KNOWN pvalue_right
pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("nd"))
S_finish.STORE[n_right_cell] = DEFINED pvalue_right
$concat_right_child_valid(S_finish, porigin_concat, porigin_right, z_concat)
~$concat_constant(S_finish, $origin_child((porigin_concat), [PCFIELD 0]))
~$concat_constant(S_finish, $origin_child((porigin_concat), [PCFIELD 1]))
$outputs(S_finish.EVENTS) = $ptascii("Q;")
n_string = |S_finish.STRINGDATA|
S_derived_concat = $string_concat(S_finish, pvalue_left, pvalue_right, false, false)
S_derived_concat.RESULT = KNOWN (PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("bind")))
S_derived_concat.STRINGDATA = S_finish.STRINGDATA ++ [$ptascii("bind")]
''') + guards('S_finish') + step('S_concatenated', 'S_finish') + lines(r'''
S_raw_concat = S_derived_concat[.ORIGIN = (porigin_concat)][.TODO = ptask_concat*][.BASE = BASE_VALUE S_derived_concat.RESULT]
S_concatenated = $destruction_store_new(S_raw_concat)
S_concatenated.RESULT = S_derived_concat.RESULT
S_concatenated.OBJECTS = S_finish.OBJECTS
S_concatenated.STORE = S_finish.STORE /\ S_concatenated.ENV = S_finish.ENV
S_concatenated.EVENTS = S_finish.EVENTS
''')
    genuine += seek('S_capture', 'S_concatenated', 1) + lines(r'''
S_capture.TODO = (SCOPED_NAME phpType19 poperand_selector phpType7* z_capture) :: ptask_capture*
S_capture.ORIGIN = (porigin_capture)
S_capture.RESULT = S_concatenated.RESULT
S_capture.STRINGDATA = S_concatenated.STRINGDATA
S_capture.STORE = S_concatenated.STORE /\ S_capture.ENV = S_concatenated.ENV
$property_computed_name(phpType20)
$call_task_valid(S_capture, SCOPED_NAME phpType19 poperand_selector phpType7* z_capture)
$ppfirstclass(phpType7*)
S_name = $resolve_at(S_capture, S_capture.RESULT, z_capture)
S_name = S_capture
S_name.RESULT = KNOWN pvalue_selected
$string_bytes(pvalue_selected) = (ptbytes_method)
ptbytes_method = $ptascii("bind")
$string_carrier_valid(S_name, pvalue_selected)
$closure_bind_capture(S_name, phpType19, ptbytes_method, phpType7*, z_capture)
$outputs(S_capture.EVENTS) = $ptascii("Q;")
n_api = |S_capture.OBJECTS|
''') + guards('S_capture') + step('S_minted', 'S_capture') + lines(r'''
S_prepared_mint = $scoped_select(S_name, phpType19, poperand_selector, ptbytes_method, phpType7*, z_capture)
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
    for label, previous, stage, name, cell, before, after in [
        ('S_left', 'S_minted', 2, 'left', 'n_left_cell', 'pvalue_left', 'get'),
        ('S_right', 'S_left_changed', 3, 'right', 'n_right_cell', 'pvalue_right', 'Current')]:
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
    genuine += seek('S_config', 'S_right_changed', 4) + lines(r'''
S_config.TODO = (CONFIG_INVOKE pconfigcall_bind) :: ptask_config*
pconfigcall_bind.KIND = INTRINSIC_CLOSURE_BIND
pconfigcall_bind.OWNER = (n_api)
pconfigcall_bind.SELECTION = (n_api)
pconfigcall_bind.INDEX = 3 /\ pconfigcall_bind.PACKS = eps /\ ~pconfigcall_bind.NAMED
S_config.STORE[n_left_cell] = DEFINED pvalue_after_left
S_config.STORE[n_right_cell] = DEFINED pvalue_after_right
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
$outputs(S_config.EVENTS) = $ptascii("Q;M:changed;C:held;B:held;P:held;A;")
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
$closure_bind_capture(S_name[.RESULT = KNOWN (PSTRING ptbytes_method)], phpType19, ptbytes_method, phpType7*, z_capture)
~$closure_bind_capture(S_name[.RESULT = KNOWN (PSTRING ($ptascii("getCurrent")))], phpType19, ptbytes_method, phpType7*, z_capture)
~$closure_bind_capture(S_name[.RESULT = KNOWN PNULL], phpType19, ptbytes_method, phpType7*, z_capture)
~$closure_bind_capture(S_name[.COMPLETION = BUDGET], phpType19, ptbytes_method, phpType7*, z_capture)
~$closure_bind_capture(S_name[.ORIGIN = eps], phpType19, ptbytes_method, phpType7*, z_capture)
~$closure_bind_capture(S_name[.ORIGIN = (porigin_body)], phpType19, ptbytes_method, phpType7*, z_capture)
~$closure_bind_capture(S_name[.TODO = eps], phpType19, ptbytes_method, phpType7*, z_capture)
~$closure_bind_capture(S_name[.TODO = (SCOPED_CLASS phpType19 phpType20 phpType7* z_capture) :: ptask_capture*], phpType19, ptbytes_method, phpType7*, z_capture)
~$closure_bind_capture(S_name[.TODO = (SCOPED_NAME phpType19 (KNOWN (PSTRING ($ptascii("stdClass")))) phpType7* z_capture) :: ptask_capture*], phpType19, ptbytes_method, phpType7*, z_capture)
~$closure_bind_capture(S_name, phpType19, $ptascii("getCurrent"), phpType7*, z_capture)
~$closure_bind_capture(S_name, phpType19, ptbytes_method, eps, z_capture)
~$closure_bind_capture(S_name, phpType19, ptbytes_method, phpType7*, $(z_capture + 1))
~$closure_bind_capture(S_name[.SOURCES = eps], phpType19, ptbytes_method, phpType7*, z_capture)
~$closure_bind_capture(S_name[.CODE = eps], phpType19, ptbytes_method, phpType7*, z_capture)
S_name.ORIGIN = (PORIGIN n_unit pcpath)
S_name.SOURCES = pcunit :: pcunit_tail*
pcunit.ID = n_unit
S_other_source = S_name[.SOURCES = pcunit[.OCCURRENCES = [PCOCCURRENCE pcpath (NExprStaticCall phpType19 (NIdentifier (BYTES "YmluZA==") metadata_method) (SEQUENCE phpType7*) metadata_capture)]] :: pcunit_tail*]
~$closure_bind_capture(S_other_source, phpType19, ptbytes_method, phpType7*, z_capture)
''')
    checks = genuine + controls
    text = PREFIX[PREFIX.index('dec $outputs'):] + EXTRA + '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks, len(genuine), len(controls)
