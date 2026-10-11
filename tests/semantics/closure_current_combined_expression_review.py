"""Evaluated class/member CURRENT capture, genuine concat producers and frozen current-body selection."""
from error_handler_protocol import PREFIX
from closure_current_capture_review import guards, lines, step

EXTRA = r'''
dec $current_combined_expression_stage(pstate, nat) : bool
def $current_combined_expression_stage(S, 0) = true
  -- if S.TODO = (CONCAT_AFTER_RIGHT porigin_concat pvalue_left z) :: ptask*
  -- if S.ORIGIN = (porigin_right)
  -- if ptask* = (ORIGIN_RETURN (porigin_capture)) :: (SCOPED_CLASS phpType19 phpType20 phpType7* z_capture) :: ptask_tail*
  -- if $origin_child((porigin_capture), [PCFIELD 0]) = (porigin_concat)
def $current_combined_expression_stage(S, 1) = true
  -- if S.TODO = (SCOPED_CLASS phpType19 phpType20 phpType7* z) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprStaticCall (NExprBinaryOpConcat expression_left expression_right metadata_class) (NExprBinaryOpConcat expression_name_left expression_name_right metadata_method) (SEQUENCE phpType7*) metadata)
def $current_combined_expression_stage(S, 2) = true
  -- if S.TODO = (CONCAT_AFTER_RIGHT porigin_concat pvalue_left z) :: ptask*
  -- if ptask* = (ORIGIN_RETURN (porigin_capture)) :: (SCOPED_NAME phpType19 poperand_selector phpType7* z_capture) :: ptask_tail*
  -- if $origin_child((porigin_capture), [PCFIELD 1]) = (porigin_concat)
def $current_combined_expression_stage(S, 3) = true
  -- if S.TODO = (SCOPED_NAME phpType19 poperand_selector phpType7* z) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprStaticCall (NExprBinaryOpConcat expression_left expression_right metadata_class) (NExprBinaryOpConcat expression_name_left expression_name_right metadata_method) (SEQUENCE phpType7*) metadata)
def $current_combined_expression_stage(S, 4) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("prefix")
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("std"))
def $current_combined_expression_stage(S, 5) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("suffix")
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("Class"))
def $current_combined_expression_stage(S, 6) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("left")
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("bi"))
def $current_combined_expression_stage(S, 7) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask*
  -- if n_name* = $ptascii("right")
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("nd"))
def $current_combined_expression_stage(S, 8) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_CLOSURE_CURRENT
def $current_combined_expression_stage(S, n) = false -- otherwise
dec $current_combined_expression_seek(pstate, nat, nat) : pstate
def $current_combined_expression_seek(S, n_stage, n) = S
  -- if $current_combined_expression_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $current_combined_expression_seek(S, n_stage, n) = $current_combined_expression_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$current_combined_expression_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $current_combined_expression_seek(S, n_stage, 0) = S
  -- if ~$current_combined_expression_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $current_combined_expression_seek(S, n_stage, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''


def seek(state, previous, stage):
    return [f'{state}_reached = $current_combined_expression_seek({previous}, {stage}, 1000)',
            f'{state}_reached.COMPLETION = NORMAL \\/ {state}_reached.COMPLETION = BUDGET',
            f'{state} = {state}_reached[.COMPLETION = NORMAL]',
            f'$current_combined_expression_stage({state}, {stage})']


def render(program, filename, expected):
    genuine = [f'S_begin = $php_run({program}, 0, {filename})', 'S_begin.COMPLETION = BUDGET']
    genuine += seek('S_class_finish', 'S_begin', 0) + lines(r'''
S_class_finish.TODO = (CONCAT_AFTER_RIGHT porigin_class_concat pvalue_class_left z_class_concat) :: ptask_class_concat*
ptask_class_concat* = (ORIGIN_RETURN (porigin_capture)) :: (SCOPED_CLASS phpType19 phpType20 phpType7* z_capture) :: ptask_tail*
S_class_finish.ORIGIN = (porigin_class_right)
$origin_child((porigin_class_concat), [PCFIELD 1]) = (porigin_class_right)
$origin_child((porigin_capture), [PCFIELD 0]) = (porigin_class_concat)
$origin_node(S_class_finish.SOURCES, porigin_capture) = (NExprStaticCall phpType19 phpType20 (SEQUENCE phpType7*) metadata_capture)
phpType19 = NExprBinaryOpConcat expression_class_left expression_class_right metadata_class
phpType20 = NExprBinaryOpConcat expression_method_left expression_method_right metadata_method
expression_class_left = NExprVariable (BYTES text_class_left) metadata_class_left
expression_class_right = NExprVariable (BYTES text_class_right) metadata_class_right
$base64(text_class_left) = $ptascii("prefix")
$base64(text_class_right) = $ptascii("suffix")
expression_method_left = NExprVariable (BYTES text_method_left) metadata_method_left
expression_method_right = NExprVariable (BYTES text_method_right) metadata_method_right
$base64(text_method_left) = $ptascii("left")
$base64(text_method_right) = $ptascii("right")
$origin_node(S_class_finish.SOURCES, porigin_class_concat) = (phpType19)
~$ppscoped_named(phpType19)
$property_computed_name(phpType20)
$lookup(S_class_finish.ENV, $ptascii("prefix")) = (n_prefix_cell)
$lookup(S_class_finish.ENV, $ptascii("suffix")) = (n_suffix_cell)
pvalue_class_left = PSTRING_CARRIER INTERNED_STRING ($ptascii("Clo"))
pvalue_class_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("sure"))
S_class_finish.STORE[n_prefix_cell] = DEFINED pvalue_class_left
S_class_finish.STORE[n_suffix_cell] = DEFINED pvalue_class_right
S_class_finish.RESULT = KNOWN pvalue_class_right
$concat_right_child_valid(S_class_finish, porigin_class_concat, porigin_class_right, z_class_concat)
$outputs(S_class_finish.EVENTS) = $ptascii("Q;")
n_class_string = |S_class_finish.STRINGDATA|
S_class_concat_query = $string_concat(S_class_finish, pvalue_class_left, pvalue_class_right, false, false)
S_class_concat_query.RESULT = KNOWN (PSTRING_CARRIER (REQUEST_STRING n_class_string) ($ptascii("Closure")))
S_class_concat_query.STRINGDATA = S_class_finish.STRINGDATA ++ [$ptascii("Closure")]
''') + step('S_class_concatenated', 'S_class_finish') + lines(r'''
S_class_concat_raw = S_class_concat_query[.ORIGIN = (porigin_class_concat)][.TODO = ptask_class_concat*][.BASE = BASE_VALUE S_class_concat_query.RESULT]
S_class_concatenated = $destruction_store_new(S_class_concat_raw)
S_class_concatenated.OBJECTS = S_class_finish.OBJECTS
S_class_concatenated.STORE = S_class_finish.STORE /\ S_class_concatenated.ENV = S_class_finish.ENV
S_class_concatenated.EVENTS = S_class_finish.EVENTS
''')
    genuine += seek('S_class_raw', 'S_class_concatenated', 1) + lines(r'''
S_class_raw.TODO = (SCOPED_CLASS phpType19 phpType20 phpType7* z_capture) :: ptask_tail*
S_class_raw.ORIGIN = (porigin_capture)
S_class_raw.RESULT = S_class_concat_query.RESULT
S_class_raw.STRINGDATA = S_class_concat_query.STRINGDATA
$call_task_valid(S_class_raw, SCOPED_CLASS phpType19 phpType20 phpType7* z_capture)
$ppfirstclass(phpType7*)
S_class = $scoped_class_prepare(S_class_raw, phpType19, z_capture)
S_class.COMPLETION = NORMAL
S_class.RESULT = KNOWN (PSTRING ptbytes_class)
ptbytes_class = $ptascii("Closure")
S_class.TODO = S_class_raw.TODO
S_class.ORIGIN = S_class_raw.ORIGIN
S_class.STRINGDATA = S_class_raw.STRINGDATA
$heap_graph(S_class) = $heap_graph(S_class_raw)
S_prepared_name = $scoped_name_prepare(S_class, phpType19, S_class.RESULT, phpType20, phpType7*, z_capture)
S_prepared_name.TODO = [$at_task($origin_child(S_class.ORIGIN, [PCFIELD 1]), EVAL (NExprBinaryOpConcat expression_method_left expression_method_right metadata_method)), SCOPED_NAME phpType19 (KNOWN (PSTRING ptbytes_class)) phpType7* z_capture] ++ ptask_tail*
''') + step('S_enqueued', 'S_class_raw') + lines(r'''
S_enqueued = $destruction_store_new(S_prepared_name)
S_enqueued.RESULT = KNOWN PNULL /\ S_enqueued.BASE = BASE_VALUE (KNOWN PNULL)
S_enqueued.OBJECTS = S_class_raw.OBJECTS
S_enqueued.ALLOCATIONS = S_class_raw.ALLOCATIONS
S_enqueued.EVENTS = S_class_raw.EVENTS
''')
    genuine += seek('S_method_finish', 'S_enqueued', 2) + lines(r'''
S_method_finish.TODO = (CONCAT_AFTER_RIGHT porigin_method_concat pvalue_method_left z_method_concat) :: ptask_method_concat*
ptask_method_concat* = (ORIGIN_RETURN (porigin_capture)) :: (SCOPED_NAME phpType19 poperand_selector phpType7* z_capture) :: ptask_tail*
poperand_selector = KNOWN (PSTRING ptbytes_class)
$origin_child((porigin_capture), [PCFIELD 1]) = (porigin_method_concat)
S_method_finish.ORIGIN = (porigin_method_right)
$origin_child((porigin_method_concat), [PCFIELD 1]) = (porigin_method_right)
$origin_node(S_method_finish.SOURCES, porigin_method_concat) = (phpType20)
$lookup(S_method_finish.ENV, $ptascii("left")) = (n_left_cell)
$lookup(S_method_finish.ENV, $ptascii("right")) = (n_right_cell)
pvalue_method_left = PSTRING_CARRIER INTERNED_STRING ($ptascii("get"))
pvalue_method_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("Current"))
S_method_finish.STORE[n_left_cell] = DEFINED pvalue_method_left
S_method_finish.STORE[n_right_cell] = DEFINED pvalue_method_right
S_method_finish.RESULT = KNOWN pvalue_method_right
$concat_right_child_valid(S_method_finish, porigin_method_concat, porigin_method_right, z_method_concat)
S_method_finish.STRINGDATA = S_enqueued.STRINGDATA
n_method_string = |S_method_finish.STRINGDATA|
n_method_string = $(n_class_string + 1)
$scoped_name_task(S_method_finish[.ORIGIN = (porigin_capture)], phpType19, poperand_selector, phpType7*, z_capture)
$outputs(S_method_finish.EVENTS) = $ptascii("Q;")
S_method_concat_query = $string_concat(S_method_finish, pvalue_method_left, pvalue_method_right, false, false)
S_method_concat_query.RESULT = KNOWN (PSTRING_CARRIER (REQUEST_STRING n_method_string) ($ptascii("getCurrent")))
S_method_concat_query.STRINGDATA = S_method_finish.STRINGDATA ++ [$ptascii("getCurrent")]
''') + step('S_method_concatenated', 'S_method_finish') + lines(r'''
S_method_concat_raw = S_method_concat_query[.ORIGIN = (porigin_method_concat)][.TODO = ptask_method_concat*][.BASE = BASE_VALUE S_method_concat_query.RESULT]
S_method_concatenated = $destruction_store_new(S_method_concat_raw)
S_method_concatenated.OBJECTS = S_method_finish.OBJECTS
S_method_concatenated.STORE = S_method_finish.STORE /\ S_method_concatenated.ENV = S_method_finish.ENV
S_method_concatenated.EVENTS = S_method_finish.EVENTS
''')
    genuine += seek('S_capture', 'S_method_concatenated', 3) + lines(r'''
S_capture.TODO = (SCOPED_NAME phpType19 poperand_selector phpType7* z_capture) :: ptask_tail*
S_capture.ORIGIN = (porigin_capture)
S_capture.RESULT = S_method_concat_query.RESULT
S_capture.STRINGDATA = S_method_concat_query.STRINGDATA
S_capture.CLASSES = eps /\ S_capture.CLASSNAMES = eps
$scoped_name_task(S_capture, phpType19, poperand_selector, phpType7*, z_capture)
$call_task_valid(S_capture, SCOPED_NAME phpType19 poperand_selector phpType7* z_capture)
S_name = $resolve_at(S_capture, S_capture.RESULT, z_capture)
S_name = S_capture
S_name.RESULT = KNOWN pvalue_selected
$string_bytes(pvalue_selected) = (ptbytes_method)
ptbytes_method = $ptascii("getCurrent")
$string_carrier_valid(S_name, pvalue_selected)
$closure_current_capture(S_name, phpType19, ptbytes_method, phpType7*, z_capture)
n_api = |S_capture.OBJECTS|
''') + guards('S_capture') + step('S_minted', 'S_capture') + lines(r'''
S_prepared_mint = $scoped_select(S_name, phpType19, poperand_selector, ptbytes_method, phpType7*, z_capture)
S_minted = $destruction_store_new(S_prepared_mint)
S_minted.TODO = ptask_tail*
S_minted.RESULT = KNOWN (POBJECT n_api)
S_minted.OBJECTS = S_capture.OBJECTS ++ [INTRINSICCLOSURE INTRINSIC_CLOSURE_CURRENT]
(HOBJECT n_api) <- S_minted.ALLOCATIONS
$node_children(S_minted, HOBJECT n_api) = eps
$heap_owners($heap_graph(S_minted), HOBJECT n_api) = 1
$closure_callable(S_minted, n_api)
$closure_live_object_valid(S_minted, n_api)
''')
    for label, previous, stage, name, cell, before, after in [
        ('S_prefix', 'S_minted', 4, 'prefix', 'n_prefix_cell', 'pvalue_class_left', 'std'),
        ('S_suffix', 'S_prefix_changed', 5, 'suffix', 'n_suffix_cell', 'pvalue_class_right', 'Class'),
        ('S_left', 'S_suffix_changed', 6, 'left', 'n_left_cell', 'pvalue_method_left', 'bi'),
        ('S_right', 'S_left_changed', 7, 'right', 'n_right_cell', 'pvalue_method_right', 'nd')]:
        changed = label + '_changed'
        event_prefix = 'Q;' if name in ('prefix', 'suffix') else 'Q;K:changed;'
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
            f'$outputs({label}.EVENTS) = $ptascii("{event_prefix}")']
        genuine += step(changed, label) + [
            f'{changed}.TODO = ptask_{name}*',
            f'{changed}.STORE[{cell}] = DEFINED pvalue_after_{name}',
            f'{changed}.STORE[n_api_cell] = DEFINED (POBJECT n_api)',
            f'{changed}.OBJECTS = {label}.OBJECTS',
            f'{changed}.ALLOCATIONS = {label}.ALLOCATIONS',
            f'{changed}.EVENTS = {label}.EVENTS',
            f'$heap_owners($heap_graph({changed}), HOBJECT n_api) = 1',
            f'$closure_callable({changed}, n_api)']
    genuine += seek('S_config', 'S_right_changed', 8) + lines(r'''
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
$lookup(psymboltable_global.ENV, $ptascii("prefix")) = (n_prefix_cell)
S_config.STORE[n_prefix_cell] = DEFINED pvalue_after_prefix
$lookup(psymboltable_global.ENV, $ptascii("suffix")) = (n_suffix_cell)
S_config.STORE[n_suffix_cell] = DEFINED pvalue_after_suffix
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
$dynamic_site(S_config, (pconfigcall_current.SITE))
$task_nodes(CONFIG_INVOKE pconfigcall_current) = [HOBJECT n_api]
$heap_owners($heap_graph(S_config), HOBJECT n_api) = 2
$heap_owners($heap_graph(S_config), HOBJECT n_body) = 1
$outputs(S_config.EVENTS) = $ptascii("Q;K:changed;M:changed;A;B;C:held;")
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
~$closure_current_capture(S_class, phpType19, $ptascii("getCurrent"), phpType7*, z_capture)
~$scoped_name_task(S_capture, phpType19, KNOWN (PSTRING ($ptascii("stdClass"))), phpType7*, z_capture)
~$scoped_name_task(S_capture, phpType19, poperand_selector, eps, z_capture)
~$scoped_name_task(S_capture, phpType19, poperand_selector, phpType7*, $(z_capture + 1))
~$scoped_name_task(S_capture[.ORIGIN = eps], phpType19, poperand_selector, phpType7*, z_capture)
~$scoped_name_task(S_capture[.SOURCES = eps], phpType19, poperand_selector, phpType7*, z_capture)
~$scoped_name_task(S_capture[.CODE = eps], phpType19, poperand_selector, phpType7*, z_capture)
phpType19_other = NExprVariable (BYTES text_class_left) metadata_class_left
~$scoped_name_task(S_capture, phpType19_other, poperand_selector, phpType7*, z_capture)
$closure_current_capture(S_name[.RESULT = KNOWN (PSTRING ptbytes_method)], phpType19, ptbytes_method, phpType7*, z_capture)
~$closure_current_capture(S_name[.RESULT = KNOWN (PSTRING ($ptascii("bind")))], phpType19, ptbytes_method, phpType7*, z_capture)
~$closure_current_capture(S_name[.RESULT = KNOWN PNULL], phpType19, ptbytes_method, phpType7*, z_capture)
~$closure_current_capture(S_name[.COMPLETION = BUDGET], phpType19, ptbytes_method, phpType7*, z_capture)
~$closure_current_capture(S_name[.ORIGIN = eps], phpType19, ptbytes_method, phpType7*, z_capture)
~$closure_current_capture(S_name[.TODO = eps], phpType19, ptbytes_method, phpType7*, z_capture)
~$closure_current_capture(S_name[.TODO = (SCOPED_NAME phpType19 (KNOWN (PSTRING ($ptascii("stdClass")))) phpType7* z_capture) :: ptask_tail*], phpType19, ptbytes_method, phpType7*, z_capture)
~$closure_current_capture(S_name, phpType19, $ptascii("bind"), phpType7*, z_capture)
~$closure_current_capture(S_name, phpType19, ptbytes_method, eps, z_capture)
~$closure_current_capture(S_name, phpType19, ptbytes_method, phpType7*, $(z_capture + 1))
S_name.ORIGIN = (PORIGIN n_unit pcpath)
S_name.SOURCES = pcunit :: pcunit_tail*
pcunit.ID = n_unit
S_other_source = S_name[.SOURCES = pcunit[.OCCURRENCES = [PCOCCURRENCE pcpath (NExprStaticCall phpType19 (NIdentifier (BYTES "Z2V0Q3VycmVudA==") metadata_method) (SEQUENCE phpType7*) metadata_capture)]] :: pcunit_tail*]
~$closure_current_capture(S_other_source, phpType19, ptbytes_method, phpType7*, z_capture)
~$scoped_name_task(S_other_source, phpType19, poperand_selector, phpType7*, z_capture)
''')
    checks = genuine + controls
    text = PREFIX[PREFIX.index('dec $outputs'):] + EXTRA + '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks, len(genuine), len(controls)
