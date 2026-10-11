"""Computed class bind capture, genuine concat normalization and frozen API identity."""
from error_handler_protocol import PREFIX
from closure_bind_capture_review import guards, lines, step

EXTRA = r'''
dec $bind_class_expression_stage(pstate, nat) : bool
def $bind_class_expression_stage(S, 0) = true
  -- if S.TODO = (CONCAT_AFTER_RIGHT porigin_concat pvalue_left z) :: ptask*
  -- if $origin_node(S.SOURCES, porigin_concat) = (NExprBinaryOpConcat expression_left expression_right metadata)
def $bind_class_expression_stage(S, 1) = true
  -- if S.TODO = (SCOPED_CLASS phpType19 phpType20 phpType7* z) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprStaticCall (NExprBinaryOpConcat expression_left expression_right metadata_class) phpType20 (SEQUENCE phpType7*) metadata)
def $bind_class_expression_stage(S, 2) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("prefix")
  -- if S.RESULT = KNOWN pvalue_left
  -- if $string_bytes(pvalue_left) = ($ptascii("std"))
def $bind_class_expression_stage(S, 3) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("suffix")
  -- if S.RESULT = KNOWN pvalue_right
  -- if $string_bytes(pvalue_right) = ($ptascii("Class"))
def $bind_class_expression_stage(S, 4) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_CLOSURE_BIND
def $bind_class_expression_stage(S, n) = false -- otherwise
dec $bind_class_expression_seek(pstate, nat, nat) : pstate
def $bind_class_expression_seek(S, n_stage, n) = S
  -- if $bind_class_expression_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $bind_class_expression_seek(S, n_stage, n) = $bind_class_expression_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$bind_class_expression_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $bind_class_expression_seek(S, n_stage, 0) = S
  -- if ~$bind_class_expression_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $bind_class_expression_seek(S, n_stage, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''


def seek(state, previous, stage):
    return [f'{state}_reached = $bind_class_expression_seek({previous}, {stage}, 1000)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$bind_class_expression_stage({state}, {stage})']


def render(program, filename, expected):
    genuine = [f'S_begin = $php_run({program}, 0, {filename})', 'S_begin.COMPLETION = BUDGET']
    genuine += seek('S_finish', 'S_begin', 0) + lines(r'''
S_finish.TODO = (CONCAT_AFTER_RIGHT porigin_concat pvalue_left z_concat) :: ptask_concat*
ptask_concat* = (ORIGIN_RETURN (porigin_capture)) :: (SCOPED_CLASS phpType19 phpType20 phpType7* z_capture) :: ptask_capture*
S_finish.ORIGIN = (porigin_right)
$origin_child((porigin_concat), [PCFIELD 1]) = (porigin_right)
$origin_child((porigin_capture), [PCFIELD 0]) = (porigin_concat)
$origin_node(S_finish.SOURCES, porigin_capture) = (NExprStaticCall phpType19 phpType20 (SEQUENCE phpType7*) metadata_capture)
phpType19 = NExprBinaryOpConcat expression_left expression_right metadata_class
phpType20 = NIdentifier (BYTES text_method) metadata_method
$ptlc($base64(text_method)) = $ptascii("bind")
expression_left = NExprVariable (BYTES text_left) metadata_left
expression_right = NExprVariable (BYTES text_right) metadata_right
$base64(text_left) = $ptascii("prefix")
$base64(text_right) = $ptascii("suffix")
$origin_node(S_finish.SOURCES, porigin_concat) = (phpType19)
~$ppscoped_named(phpType19)
$lookup(S_finish.ENV, $ptascii("prefix")) = (n_left_cell)
$lookup(S_finish.ENV, $ptascii("suffix")) = (n_right_cell)
pvalue_left = PSTRING_CARRIER INTERNED_STRING ($ptascii("Clo"))
S_finish.STORE[n_left_cell] = DEFINED pvalue_left
S_finish.RESULT = KNOWN pvalue_right
pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("sure"))
S_finish.STORE[n_right_cell] = DEFINED pvalue_right
$concat_right_child_valid(S_finish, porigin_concat, porigin_right, z_concat)
~$concat_constant(S_finish, $origin_child((porigin_concat), [PCFIELD 0]))
~$concat_constant(S_finish, $origin_child((porigin_concat), [PCFIELD 1]))
$outputs(S_finish.EVENTS) = $ptascii("Q;")
n_string = |S_finish.STRINGDATA|
S_derived_concat = $string_concat(S_finish, pvalue_left, pvalue_right, false, false)
S_derived_concat.RESULT = KNOWN (PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("Closure")))
S_derived_concat.STRINGDATA = S_finish.STRINGDATA ++ [$ptascii("Closure")]
''') + guards('S_finish') + step('S_concatenated', 'S_finish') + lines(r'''
S_raw_concat = S_derived_concat[.ORIGIN = (porigin_concat)][.TODO = ptask_concat*][.BASE = BASE_VALUE S_derived_concat.RESULT]
S_concatenated = $destruction_store_new(S_raw_concat)
S_concatenated.RESULT = S_derived_concat.RESULT
S_concatenated.OBJECTS = S_finish.OBJECTS
S_concatenated.STORE = S_finish.STORE /\ S_concatenated.ENV = S_finish.ENV
S_concatenated.EVENTS = S_finish.EVENTS
''')
    genuine += seek('S_capture', 'S_concatenated', 1) + lines(r'''
S_capture.TODO = (SCOPED_CLASS phpType19 phpType20 phpType7* z_capture) :: ptask_capture*
S_capture.ORIGIN = (porigin_capture)
S_capture.RESULT = S_concatenated.RESULT
S_capture.STRINGDATA = S_concatenated.STRINGDATA
S_capture.STORE = S_concatenated.STORE /\ S_capture.ENV = S_concatenated.ENV
$call_task_valid(S_capture, SCOPED_CLASS phpType19 phpType20 phpType7* z_capture)
$ppfirstclass(phpType7*)
S_class = $scoped_class_prepare(S_capture, phpType19, z_capture)
S_class.COMPLETION = NORMAL
S_class.RESULT = KNOWN (PSTRING ptbytes_class)
ptbytes_class = $ptascii("Closure")
S_class.TODO = S_capture.TODO
S_class.ORIGIN = S_capture.ORIGIN
S_class.STORE = S_capture.STORE /\ S_class.ENV = S_capture.ENV
S_class.OBJECTS = S_capture.OBJECTS /\ S_class.ALLOCATIONS = S_capture.ALLOCATIONS
S_class.STRINGDATA = S_capture.STRINGDATA
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
    for label, previous, stage, name, cell, before, after in [
        ('S_left', 'S_minted', 2, 'prefix', 'n_left_cell', 'pvalue_left', 'std'),
        ('S_right', 'S_left_changed', 3, 'suffix', 'n_right_cell', 'pvalue_right', 'Class')]:
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
S_config.STORE[n_left_cell] = DEFINED pvalue_after_prefix
S_config.STORE[n_right_cell] = DEFINED pvalue_after_suffix
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
~$closure_bind_capture(S_class[.TODO = (SCOPED_NAME phpType19 S_class.RESULT phpType7* z_capture) :: ptask_capture*], phpType19, $ptascii("bind"), phpType7*, z_capture)
~$closure_bind_capture(S_class, phpType19, $ptascii("getCurrent"), phpType7*, z_capture)
~$closure_bind_capture(S_class, phpType19, $ptascii("bind"), eps, z_capture)
~$closure_bind_capture(S_class, phpType19, $ptascii("bind"), phpType7*, $(z_capture + 1))
~$closure_bind_capture(S_class[.SOURCES = eps], phpType19, $ptascii("bind"), phpType7*, z_capture)
~$closure_bind_capture(S_class[.CODE = eps], phpType19, $ptascii("bind"), phpType7*, z_capture)
phpType19_other = NExprVariable (BYTES text_left) metadata_left
~$closure_bind_capture(S_class[.TODO = (SCOPED_CLASS phpType19_other phpType20 phpType7* z_capture) :: ptask_capture*], phpType19_other, $ptascii("bind"), phpType7*, z_capture)
S_class.ORIGIN = (PORIGIN n_unit pcpath)
S_class.SOURCES = pcunit :: pcunit_tail*
pcunit.ID = n_unit
S_other_source = S_class[.SOURCES = pcunit[.OCCURRENCES = [PCOCCURRENCE pcpath (NExprStaticCall phpType19 (NIdentifier (BYTES "Z2V0Q3VycmVudA==") metadata_method) (SEQUENCE phpType7*) metadata_capture)]] :: pcunit_tail*]
~$closure_bind_capture(S_other_source, phpType19, $ptascii("bind"), phpType7*, z_capture)
''')
    checks = genuine + controls
    text = PREFIX[PREFIX.index('dec $outputs'):] + EXTRA + '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks, len(genuine), len(controls)
