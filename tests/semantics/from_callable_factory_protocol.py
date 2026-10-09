"""Real core-factory creation, receive, retired producer and inherited callback."""
from scoped_static_compound_protocol import computed_start, guards, lines, seek
from static_name_callable_protocol import render_instance_wrapper

PHASE = r'''
def $scoped_phase(S, 24) = true
  -- if S.TODO = (SCOPED_CLASS phpType19 phpType20 phpType7* z) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if $from_static_class(S, porigin, phpType19)
  -- if $origin_child(S.ORIGIN, [PCFIELD 1]) = (porigin_method_name)
  -- if $origin_node(S.SOURCES, porigin_method_name) = (NIdentifier (BYTES text_method) metadata_name)
  -- if $ptlc($base64(text_method)) = $ptascii("fromcallable")
  -- if $ppscoped_named(phpType19)
  -- if $ppfirstclass(phpType7*)
'''


def creation_checks(fixture, filename):
    checks = computed_start('S_create', {'fixture': fixture, 'filename': filename}, 24)
    checks += lines(r'''
S_create.TODO = (SCOPED_CLASS phpType19 phpType20 phpType7* z_create) :: ptask_create*
S_create.ORIGIN = (porigin_create)
porigin_create = PORIGIN n_unit pcpath_create
$origin_node(S_create.SOURCES, porigin_create) = (NExprStaticCall phpType19 phpType20 (SEQUENCE phpType7*) metadata_create)
$ppscoped_named(phpType19)
~$ppscoped_keyword(phpType19)
$origin_child((porigin_create), [PCFIELD 1]) = (porigin_method_name)
$origin_node(S_create.SOURCES, porigin_method_name) = (NIdentifier (BYTES text_method) metadata_name)
$ptlc($base64(text_method)) = $ptascii("fromcallable")
phpType7* = [(NVariadicPlaceholder metadata_placeholder)]
$ppfirstclass(phpType7*)
$code_at(S_create.CODE, n_unit) = (pcode)
$code_name(pcode.NAMES, pcpath_create) = (($ptascii("Closure"), eps))
$from_static_class(S_create, porigin_create, phpType19)
~$from_site(S_create, porigin_create)
S_create.CURRENT = eps
$method_current_scope(S_create) = eps
$call_line_valid(S_create, (porigin_create), z_create)
$call_task_valid(S_create, SCOPED_CLASS phpType19 phpType20 phpType7* z_create)
$outputs(S_create.EVENTS) = $ptascii("Q;")
$lookup(S_create.ENV, $ptascii("callback")) = (n_callback_cell)
S_create.STORE[n_callback_cell] = DEFINED (PARRAY n_callback)
$typed_callback_array(S_create, n_callback)
$entry_lookup(S_create.ARRAYS[n_callback].ITEMS, KINT 0) = (pitem_receiver)
$entry_lookup(S_create.ARRAYS[n_callback].ITEMS, KINT 1) = (pitem_method)
$entry_value(S_create, pitem_receiver) = POBJECT n_receiver
pvalue_method = $entry_value(S_create, pitem_method)
$string_bytes(pvalue_method) = ($ptascii("append"))
$class_named(S_create.CLASSNAMES, $ptlc($ptascii("FromFactoryNameBaseReview20"))) = (porigin_base)
$class_named(S_create.CLASSNAMES, $ptlc($ptascii("FromFactoryNameChildReview20"))) = (porigin_child)
porigin_base =/= porigin_child
S_create.OBJECTS[n_receiver] = INSTANCE porigin_child
(HOBJECT n_receiver) <- S_create.ALLOCATIONS
(HARRAY n_callback) <- S_create.ALLOCATIONS
$effective_method(S_create, porigin_child, $ptascii("append"), |S_create.CLASSES|) = (pmethoddesc)
pmethoddesc.OWNER = porigin_base
~pmethoddesc.STATIC /\ ~pmethoddesc.ABSTRACT
$method_accessible(S_create, pmethoddesc, eps)
pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS[0].BYREF
pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS[1].BYREF
n_receiver_owners = $heap_owners($heap_graph(S_create), HOBJECT n_receiver)
''') + guards('S_create')
    checks += lines(r'''
S_class = $scoped_class_prepare(S_create, phpType19, z_create)
S_class.COMPLETION = NORMAL
S_class.ORIGIN = (porigin_create)
S_class.TODO = S_create.TODO
S_class.CURRENT = S_create.CURRENT
S_class.OBJECTS = S_create.OBJECTS
S_class.ALLOCATIONS = S_create.ALLOCATIONS
S_class.RESULT = KNOWN pvalue_selector
$string_bytes(pvalue_selector) = ($ptascii("Closure"))
''')
    return checks

FACTORY_PHASE = r'''
def $scoped_phase(S, 25) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_FROM_CALLABLE_FACTORY
  -- if pconfigcall.OWNER =/= eps
def $scoped_phase(S, 26) = true
  -- if S.RESULT = KNOWN (POBJECT n)
  -- if S.OBJECTS[n] = FROMCALLABLECLOSURE pfrommethod
  -- if pfrommethod.FACTORY =/= eps
'''


def render_factory(fixture, filename, expected):
    genuine = creation_checks(fixture, filename)
    genuine += lines(r'''
$from_factory_site(S_class, porigin_create)
$from_factory_capture(S_class, phpType19, $base64(text_method), phpType7*, z_create)
n_factory = |S_create.OBJECTS|
S_factory_budget = $drive_steps(S_create, 1)
S_factory_budget.COMPLETION = BUDGET
S_factory = S_factory_budget[.COMPLETION = NORMAL]
S_factory.ORIGIN = (porigin_create)
S_factory.CURRENT = eps
S_factory.OBJECTS = S_create.OBJECTS ++ [FROMCALLABLEFACTORY porigin_create]
S_factory.ALLOCATIONS = S_create.ALLOCATIONS ++ [HOBJECT n_factory]
S_factory.TODO = ptask_create*
S_factory.RESULT = KNOWN (POBJECT n_factory)
S_factory.BASE = BASE_VALUE (KNOWN PNULL)
$from_factory_saved(S_factory, n_factory)
$from_factory_live(S_factory, n_factory)
$closure_callable(S_factory, n_factory)
$closure_live_object_valid(S_factory, n_factory)
$getclass_live_object(S_factory, n_factory)
$class_instanceof(S_factory, POBJECT n_factory, $ptascii("Closure"))
$node_children(S_factory, HOBJECT n_factory) = eps
$closure_scope_at(S_factory.CLOSURESCOPES, n_factory) = eps
$closure_binding_at(S_factory.CLOSUREBINDINGS, n_factory) = eps
$heap_owners($heap_graph(S_factory), HOBJECT n_factory) = 1
$heap_owners($heap_graph(S_factory), HOBJECT n_receiver) = 1
$outputs(S_factory.EVENTS) = $ptascii("Q;")
''') + guards('S_factory')
    genuine += seek('S_config', 'S_factory', 25) + lines(r'''
S_config.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_config*
pconfigcall.KIND = INTRINSIC_FROM_CALLABLE_FACTORY
pconfigcall.OWNER = (n_factory)
pconfigcall.SELECTION = eps
porigin_invoke = pconfigcall.SITE
porigin_invoke =/= porigin_create
pconfigcall.INDEX = 1
pconfigcall.SENT = [NAMED_SENT (KNOWN (PARRAY n_callback))]
pconfigcall.NAMED
pconfigcall.PACKS = eps
S_config.ORIGIN = (porigin_invoke)
S_config.CURRENT = eps
$api_frame_scope(S_config) = eps
$method_current_scope(S_config) = eps
$from_factory_call_site(S_config, porigin_invoke)
~$from_factory_site(S_config, porigin_invoke)
~$from_site(S_config, porigin_invoke)
$origin_node(S_config.SOURCES, porigin_invoke) = (NExprFuncCall expression_factory (SEQUENCE phpType7_invoke*) metadata_invoke)
$ppcall_dynamic(expression_factory)
~$ppfirstclass(phpType7_invoke*)
|phpType7_invoke*| = 1
$lookup(S_config.ENV, $ptascii("factory")) = (n_factory_cell)
S_config.STORE[n_factory_cell] = DEFINED (POBJECT n_factory)
S_config.OBJECTS[n_factory] = FROMCALLABLEFACTORY porigin_create
$from_factory_live(S_config, n_factory)
$from_factory_owner(S_config, pconfigcall) = (n_factory)
$config_selected_valid(S_config, pconfigcall)
$config_call_valid(S_config, pconfigcall)
$config_sent_shape(S_config, pconfigcall)
$config_invoke_valid(S_config, pconfigcall)
$call_task_valid(S_config, CONFIG_INVOKE pconfigcall)
$task_nodes(CONFIG_INVOKE pconfigcall) = [HOBJECT n_factory, HARRAY n_callback]
$node_children(S_config, HOBJECT n_factory) = eps
$heap_owners($heap_graph(S_config), HOBJECT n_factory) = 2
$heap_owners($heap_graph(S_config), HOBJECT n_receiver) = 1
$outputs(S_config.EVENTS) = $ptascii("Q;")
''') + guards('S_config')
    genuine += seek('S_return', 'S_config', 26) + lines(r'''
S_return.RESULT = KNOWN (POBJECT n_produced)
S_return.OBJECTS[n_produced] = FROMCALLABLECLOSURE pfrommethod_return
n_produced =/= n_factory /\ n_produced =/= n_receiver
pfrommethod_return.SITE = porigin_invoke
pfrommethod_return.FACTORY = (n_factory)
pfrommethod_return.SCOPE = eps
pfrommethod_return.CALLED = eps
pfrommethod_return.THIS = eps
pfrommethod_return.CREATION = eps
pfrommethod_return.CLASS.REQUESTED = porigin_child
pfrommethod_return.CLASS.CALLED = porigin_child
pfrommethod_return.CLASS.RECEIVER = (n_receiver)
pfrommethod_return.FUNCTION = pmethoddesc.FUNCTION.ORIGIN
pfrommethod_return.ARRAY /\ ~pfrommethod_return.INVOKE
~pfrommethod_return.STATIC
$from_source_valid(S_return, pfrommethod_return)
$from_permission(S_return, pfrommethod_return)
$from_valid(S_return, pfrommethod_return)
$from_factory_saved(S_return, n_factory)
$from_factory_live(S_return, n_factory)
$node_children(S_return, HOBJECT n_factory) = eps
$node_children(S_return, HOBJECT n_produced) = [HOBJECT n_receiver]
$heap_owners($heap_graph(S_return), HOBJECT n_receiver) = 2
$outputs(S_return.EVENTS) = $ptascii("Q;")
''') + guards('S_return')

    old_text, inherited, reached, _ = render_instance_wrapper(fixture, filename, expected)
    prefix = old_text.split('\ndec $main()')[0].replace('FromInstance', 'FromFactory')
    inherited = inherited[:reached]
    inherited = inherited[len(computed_start('S_name', {'fixture': fixture, 'filename': filename}, 8)):]
    inherited = [check.replace('FromInstance', 'FromFactory').replace('$ptascii("H;', '$ptascii("Q;F;H;')
                 for check in inherited]
    inherited = seek('S_name', 'S_return', 8) + inherited
    index = inherited.index('S_name.OBJECTS[n_closure] = FROMCALLABLECLOSURE pfrommethod')
    inherited[index + 1:index + 1] = lines(r'''
n_closure = n_produced
pfrommethod = pfrommethod_return
pfrommethod.FACTORY = (n_factory)
S_name.OBJECTS[n_factory] = FROMCALLABLEFACTORY porigin_create
~((HOBJECT n_factory) <- S_name.ALLOCATIONS)
$heap_owners($heap_graph(S_name), HOBJECT n_factory) = 0
$from_factory_saved(S_name, n_factory)
~$from_factory_live(S_name, n_factory)
$from_source_valid(S_name, pfrommethod)
$node_children(S_name, HOBJECT n_factory) = eps
''')
    index = inherited.index('~$from_current(S_callback)')
    inherited[index + 1:index + 1] = lines(r'''
~((HOBJECT n_factory) <- S_callback.ALLOCATIONS)
$from_factory_saved(S_callback, n_factory)
$from_source_valid(S_callback, pfrommethod)
$from_valid(S_callback, pfrommethod)
''')
    index = inherited.index('~((HOBJECT n_closure) <- S_done.ALLOCATIONS)')
    inherited[index + 1:index + 1] = lines(r'''
~((HOBJECT n_factory) <- S_done.ALLOCATIONS)
$heap_owners($heap_graph(S_done), HOBJECT n_factory) = 0
$from_factory_saved(S_done, n_factory)
$from_source_valid(S_done, pfrommethod)
''')
    genuine += inherited

    # Constructed controls target only the new factory and returned provenance.
    controls = lines(r'''
$from_kind(INTRINSIC_FROM_CALLABLE)
$from_kind(INTRINSIC_FROM_CALLABLE_FACTORY)
~$closure_static_api_kind(INTRINSIC_FROM_CALLABLE_FACTORY)
$closure_static_api_kind(INTRINSIC_FROM_CALLABLE)
$intrinsic_name(INTRINSIC_FROM_CALLABLE_FACTORY) = $intrinsic_name(INTRINSIC_FROM_CALLABLE)
$config_required(INTRINSIC_FROM_CALLABLE_FACTORY) = 1
$config_parameter(INTRINSIC_FROM_CALLABLE_FACTORY, $ptascii("callback")) = (0)
$config_parameter_name(INTRINSIC_FROM_CALLABLE_FACTORY, 0) = $ptascii("callback")
$config_nodes(pconfigcall[.KIND = INTRINSIC_FROM_CALLABLE]) = [HARRAY n_callback]
$from_factory_owner(S_config, pconfigcall[.KIND = INTRINSIC_FROM_CALLABLE]) = eps
~$config_selected_valid(S_config, pconfigcall[.KIND = INTRINSIC_FROM_CALLABLE])
~$from_factory_capture(S_class[.ORIGIN = eps], phpType19, $base64(text_method), phpType7*, z_create)
~$from_factory_capture(S_class[.TODO = (SCOPED_CLASS phpType19 phpType20 phpType7* $(z_create + 1)) :: ptask_create*], phpType19, $base64(text_method), phpType7*, z_create)
~$from_factory_capture(S_class, phpType19, $ptascii("other"), phpType7*, z_create)
~$from_factory_capture(S_class, phpType19, $base64(text_method), eps, z_create)
S_no_class_name = S_class[.CODE[n_unit] = pcode[.NAMES = eps]]
~$from_factory_site(S_no_class_name, porigin_create)
~$from_factory_capture(S_no_class_name, phpType19, $base64(text_method), phpType7*, z_create)
~$from_factory_site(S_class, porigin_method_name)
n_absent_unit = |S_class.SOURCES|
~$from_factory_site(S_class, PORIGIN n_absent_unit eps)
S_wrong_factory_kind = S_factory[.OBJECTS[n_factory] = INTRINSICCLOSURE INTRINSIC_FROM_CALLABLE]
~$from_factory_saved(S_wrong_factory_kind, n_factory)
~$closure_callable(S_wrong_factory_kind, n_factory)
~$closure_live_object_valid(S_wrong_factory_kind, n_factory)
S_wrong_protocol_kind = S_factory[.OBJECTS[n_factory] = INTRINSICCLOSURE INTRINSIC_FROM_CALLABLE_FACTORY]
~$closure_callable(S_wrong_protocol_kind, n_factory)
~$closure_live_object_valid(S_wrong_protocol_kind, n_factory)
S_wrong_creation = S_config[.OBJECTS[n_factory] = FROMCALLABLEFACTORY porigin_invoke]
~$from_factory_saved(S_wrong_creation, n_factory)
~$from_factory_live(S_wrong_creation, n_factory)
~$config_selected_valid(S_wrong_creation, pconfigcall)
~$from_factory_saved(S_config, |S_config.OBJECTS|)
~$config_selected_valid(S_config, pconfigcall[.OWNER = eps])
~$config_selected_valid(S_config, pconfigcall[.OWNER = (n_receiver)])
~$config_selected_valid(S_config, pconfigcall[.OWNER = (|S_config.OBJECTS|)])
~$config_selected_valid(S_config, pconfigcall[.SITE = porigin_create])
~$config_selected_valid(S_config, pconfigcall[.SELECTION = (0)])
~$config_selected_valid(S_config, pconfigcall[.KIND = INTRINSIC_INI_GET])
~$config_invoke_valid(S_config, pconfigcall[.LINE = $(pconfigcall.LINE + 1)])
~$config_invoke_valid(S_config, pconfigcall[.SENT = eps])
~$config_invoke_valid(S_config, pconfigcall[.NAMED = false])
S_retired_owner = S_config[.ALLOCATIONS = eps]
$from_factory_saved(S_retired_owner, n_factory)
~$from_factory_live(S_retired_owner, n_factory)
~$config_selected_valid(S_retired_owner, pconfigcall)
~$from_source_valid(S_callback, pfrommethod[.FACTORY = eps])
~$from_valid(S_callback, pfrommethod[.FACTORY = eps])
~$from_source_valid(S_callback, pfrommethod[.FACTORY = (n_receiver)])
~$from_valid(S_callback, pfrommethod[.FACTORY = (n_receiver)])
~$from_source_valid(S_callback, pfrommethod[.FACTORY = (|S_callback.OBJECTS|)])
~$from_valid(S_callback, pfrommethod[.FACTORY = (|S_callback.OBJECTS|)])
~$from_source_valid(S_callback, pfrommethod[.SITE = porigin_create])
~$from_valid(S_callback, pfrommethod[.SITE = porigin_create])
S_saved_wrong_creation = S_callback[.OBJECTS[n_factory] = FROMCALLABLEFACTORY porigin_invoke]
~$from_source_valid(S_saved_wrong_creation, pfrommethod)
~$from_valid(S_saved_wrong_creation, pfrommethod)
$from_source_valid(S_callback[.CURRENT = eps], pfrommethod)
$from_valid(S_callback[.CURRENT = eps], pfrommethod)
''')
    checks = genuine + controls
    text = prefix + PHASE + FACTORY_PHASE + '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join(('  -- ' if check.startswith('PhpStep:') else '  -- if ') + check + '\n'
                    for check in checks)
    return text, checks, len(genuine), len(controls)


INVOKE_PHASE = r'''
def $scoped_phase(S, 27) = true
  -- if S.TODO = (METHOD_PREP phpType20 phpType7* false false z) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if $origin_child(S.ORIGIN, [PCFIELD 1]) = (porigin_method_name)
  -- if $origin_node(S.SOURCES, porigin_method_name) = (NIdentifier (BYTES text_method) metadata_name)
  -- if $ptlc($base64(text_method)) = $ptascii("__invoke")
'''


def invoke_entry_checks(fixture, filename):
    checks = computed_start('S_entry', {'fixture': fixture, 'filename': filename}, 27)
    checks += lines(r'''
S_entry.TODO = (METHOD_PREP phpType20 phpType7* false false z_entry) :: ptask_entry*
S_entry.ORIGIN = (porigin_invoke)
porigin_invoke = PORIGIN n_unit pcpath_invoke
$origin_node(S_entry.SOURCES, porigin_invoke) = (NExprMethodCall expression_receiver phpType20 (SEQUENCE phpType7*) metadata_invoke)
$origin_child((porigin_invoke), [PCFIELD 1]) = (porigin_method_name)
$origin_node(S_entry.SOURCES, porigin_method_name) = (NIdentifier (BYTES text_method) metadata_name)
$ptlc($base64(text_method)) = $ptascii("__invoke")
~$ppfirstclass(phpType7*)
$call_line_valid(S_entry, (porigin_invoke), z_entry)
$call_task_valid(S_entry, METHOD_PREP phpType20 phpType7* false false z_entry)
$method_source_task(S_entry, NExprMethodCall expression_receiver phpType20 (SEQUENCE phpType7*) metadata_invoke)
$code_at(S_entry.CODE, n_unit) = (pcode)
$code_expression(pcode.EXPRESSIONS, pcpath_invoke) = ((z_entry, b_expression))
(S_capture, poperand_factory) = $method_capture(S_entry, false, z_entry)
S_capture = S_entry
poperand_factory = S_entry.RESULT
S_read = $resolve_at(S_capture, poperand_factory, z_entry)
S_read.COMPLETION = NORMAL
S_read.RESULT = KNOWN (POBJECT n_factory)
S_read.OBJECTS[n_factory] = FROMCALLABLEFACTORY porigin_create
porigin_create =/= porigin_invoke
$from_factory_saved(S_read, n_factory)
$from_factory_live(S_read, n_factory)
$closure_callable(S_read, n_factory)
$closure_live_object_valid(S_read, n_factory)
$node_children(S_read, HOBJECT n_factory) = eps
$closure_scope_at(S_read.CLOSURESCOPES, n_factory) = eps
$closure_binding_at(S_read.CLOSUREBINDINGS, n_factory) = eps
S_read.CURRENT = eps
S_read.FRAMES = eps
$method_current_scope(S_read) = eps
$api_frame_scope(S_read) = eps
$lookup(S_read.ENV, $ptascii("factory")) = (n_factory_cell)
S_read.STORE[n_factory_cell] = DEFINED (POBJECT n_factory)
(HOBJECT n_factory) <- S_read.ALLOCATIONS
~$from_factory_call_site(S_read, porigin_invoke)
~$from_site(S_read, porigin_invoke)
$from_factory_site(S_read, porigin_create)
$origin_node(S_read.SOURCES, porigin_create) = (NExprStaticCall phpType19 phpType20_create (SEQUENCE phpType7_create*) metadata_create)
$ppscoped_named(phpType19)
~$ppscoped_keyword(phpType19)
$ppfirstclass(phpType7_create*)
$from_static_class(S_read, porigin_create, phpType19)
$class_named(S_read.CLASSNAMES, $ptlc($ptascii("InvokeFactoryNameBaseReview20"))) = (porigin_base)
$class_named(S_read.CLASSNAMES, $ptlc($ptascii("InvokeFactoryNameChildReview20"))) = (porigin_child)
porigin_base =/= porigin_child
$effective_method(S_read, porigin_child, $ptascii("append"), |S_read.CLASSES|) = (pmethoddesc)
pmethoddesc.OWNER = porigin_base
~pmethoddesc.STATIC /\ ~pmethoddesc.ABSTRACT
pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS[0].BYREF
pmethoddesc.FUNCTION.SIGNATURE.PARAMETERS[1].BYREF
$lookup(S_read.ENV, $ptascii("property")) = (n_name_cell)
S_read.STORE[n_name_cell] = DEFINED (POBJECT n_name)
(HOBJECT n_name) <- S_read.ALLOCATIONS
$lookup(S_read.ENV, $ptascii("rhs")) = (n_rhs_cell)
S_read.STORE[n_rhs_cell] = DEFINED pvalue_rhs
$string_bytes(pvalue_rhs) = ($ptascii("before"))
$outputs(S_read.EVENTS) = $ptascii("Q;")
n_factory_owners = $heap_owners($heap_graph(S_read), HOBJECT n_factory)
''') + guards('S_entry') + guards('S_read')
    return checks

INVOKE_ARGUMENT_PHASE = r'''
def $scoped_phase(S, 28) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $ptlc(pcallcontext.NAME) = $ptlc($ptascii("clearFactoryInvokeArgumentReview20"))
  -- if $lookup(S.ENV, $ptascii("factory")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED PNULL
  -- if $outputs(S.EVENTS) = $ptascii("Q;A;")
def $scoped_phase(S, 25) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_FROM_CALLABLE_FACTORY
  -- if pconfigcall.OWNER =/= eps
def $scoped_phase(S, 26) = true
  -- if S.RESULT = KNOWN (POBJECT n)
  -- if S.OBJECTS[n] = FROMCALLABLECLOSURE pfrommethod
  -- if pfrommethod.FACTORY =/= eps
'''


def render_factory_invoke(fixture, filename, expected):
    genuine = invoke_entry_checks(fixture, filename)
    genuine = [check.replace('S_capture', 'S_entry_capture').replace('S_read', 'S_entry_read')
               for check in genuine]
    genuine[genuine.index('~$from_factory_call_site(S_entry_read, porigin_invoke)')] = '$from_factory_call_site(S_entry_read, porigin_invoke)'
    genuine += lines(r'''
$from_factory_invoke_site(S_entry_read, porigin_invoke)
S_start_budget = $drive_steps(S_entry, 1)
S_start_budget.COMPLETION = BUDGET
S_start = S_start_budget[.COMPLETION = NORMAL]
S_start.TODO = (CONFIG_ARGS pconfigcall_start) :: METHOD_RESULT :: ptask_entry*
S_start.ORIGIN = (porigin_invoke)
pconfigcall_start = {SITE porigin_invoke, KIND INTRINSIC_FROM_CALLABLE_FACTORY, INDEX 0, SENT eps, NAMED false, OWNER (n_factory), SELECTION eps, LINE z_entry, PACKS eps}
S_start.CURRENT = S_entry.CURRENT
S_start.FRAMES = S_entry.FRAMES
S_start.RESULT = KNOWN PNULL
S_start.BASE = BASE_VALUE (KNOWN PNULL)
$from_factory_live(S_start, n_factory)
$config_selected_valid(S_start, pconfigcall_start)
$config_call_valid(S_start, pconfigcall_start)
$call_task_valid(S_start, CONFIG_ARGS pconfigcall_start)
$call_task_valid(S_start, METHOD_RESULT)
$task_nodes(CONFIG_ARGS pconfigcall_start) = [HOBJECT n_factory]
$node_children(S_start, HOBJECT n_factory) = eps
$heap_owners($heap_graph(S_start), HOBJECT n_factory) = 2
$outputs(S_start.EVENTS) = $ptascii("Q;")
''') + guards('S_start')
    genuine += seek('S_argument', 'S_start', 28) + lines(r'''
S_argument.CURRENT = (pcallcontext_argument)
$ptlc(pcallcontext_argument.NAME) = $ptlc($ptascii("clearFactoryInvokeArgumentReview20"))
pcallcontext_argument.LEXICAL_CLASS = eps
pcallcontext_argument.CALLED_CLASS = eps
pcallcontext_argument.INSTANCE = eps
pcallcontext_argument.RECEIVER = eps
S_argument.STORE[n_factory_cell] = DEFINED PNULL
S_argument_global = $global_table_view(S_argument)
$lookup(S_argument_global.ENV, $ptascii("factory")) = (n_factory_cell)
$from_factory_live(S_argument, n_factory)
$from_factory_saved(S_argument, n_factory)
$node_children(S_argument, HOBJECT n_factory) = eps
$heap_owners($heap_graph(S_argument), HOBJECT n_factory) = 1
pframe_argument = S_argument.FRAMES[0]
$call_saved_context_valid(S_argument, pframe_argument)
$tasks_nodes(pframe_argument.TODO) = [HOBJECT n_factory]
$outputs(S_argument.EVENTS) = $ptascii("Q;A;")
''') + guards('S_argument')
    genuine += seek('S_config', 'S_argument', 25) + lines(r'''
S_config.TODO = (CONFIG_INVOKE pconfigcall) :: METHOD_RESULT :: ptask_entry*
pconfigcall.SENT = [NAMED_SENT (KNOWN (PARRAY n_callback))]
pconfigcall = pconfigcall_start[.INDEX = 1][.SENT = [NAMED_SENT (KNOWN (PARRAY n_callback))]][.NAMED = true]
S_config.ORIGIN = (porigin_invoke)
S_config.CURRENT = eps
S_config.FRAMES = eps
$api_frame_scope(S_config) = eps
S_config.STORE[n_factory_cell] = DEFINED PNULL
S_config.OBJECTS[n_factory] = FROMCALLABLEFACTORY porigin_create
$typed_callback_array(S_config, n_callback)
$entry_lookup(S_config.ARRAYS[n_callback].ITEMS, KINT 0) = (pitem_receiver)
$entry_lookup(S_config.ARRAYS[n_callback].ITEMS, KINT 1) = (pitem_method)
$entry_value(S_config, pitem_receiver) = POBJECT n_receiver
pvalue_method = $entry_value(S_config, pitem_method)
$string_bytes(pvalue_method) = ($ptascii("append"))
S_config.OBJECTS[n_receiver] = INSTANCE porigin_child
(HOBJECT n_receiver) <- S_config.ALLOCATIONS
(HARRAY n_callback) <- S_config.ALLOCATIONS
$from_factory_live(S_config, n_factory)
$from_factory_owner(S_config, pconfigcall) = (n_factory)
$config_selected_valid(S_config, pconfigcall)
$config_call_valid(S_config, pconfigcall)
$config_sent_shape(S_config, pconfigcall)
$config_invoke_valid(S_config, pconfigcall)
$call_task_valid(S_config, CONFIG_INVOKE pconfigcall)
$task_nodes(CONFIG_INVOKE pconfigcall) = [HOBJECT n_factory, HARRAY n_callback]
$node_children(S_config, HOBJECT n_factory) = eps
$heap_owners($heap_graph(S_config), HOBJECT n_factory) = 1
$heap_owners($heap_graph(S_config), HOBJECT n_receiver) = 1
$outputs(S_config.EVENTS) = $ptascii("Q;A;")
$config_trace_frames(S_config, pconfigcall, [PARRAY n_callback]) = [ptraceframe_api, ptraceframe_invoke]
ptraceframe_api.FILE = $call_sourcefile(S_config.FILES, porigin_invoke)
ptraceframe_api.LINE = z_entry
ptraceframe_api.FUNCTION = $ptascii("fromCallable")
ptraceframe_api.CLASS = ($ptascii("Closure"))
ptraceframe_api.TYPE = ($ptascii("::"))
ptraceframe_api.ARGS = [(KINT 0, PARRAY n_callback)]
ptraceframe_api.HASARGS
ptraceframe_invoke.FILE = ptraceframe_api.FILE
ptraceframe_invoke.LINE = z_entry
ptraceframe_invoke.FUNCTION = $ptascii("__invoke")
ptraceframe_invoke.CLASS = ($ptascii("Closure"))
ptraceframe_invoke.TYPE = ($ptascii("->"))
ptraceframe_invoke.ARGS = ptraceframe_api.ARGS
ptraceframe_invoke.HASARGS
''') + guards('S_config')
    genuine += seek('S_return', 'S_config', 26) + lines(r'''
S_return.RESULT = KNOWN (POBJECT n_produced)
S_return.OBJECTS[n_produced] = FROMCALLABLECLOSURE pfrommethod_return
n_produced =/= n_factory /\ n_produced =/= n_receiver
pfrommethod_return.SITE = porigin_invoke
pfrommethod_return.FACTORY = (n_factory)
pfrommethod_return.SCOPE = eps
pfrommethod_return.CALLED = eps
pfrommethod_return.THIS = eps
pfrommethod_return.CREATION = eps
pfrommethod_return.CLASS.REQUESTED = porigin_child
pfrommethod_return.CLASS.CALLED = porigin_child
pfrommethod_return.CLASS.RECEIVER = (n_receiver)
pfrommethod_return.FUNCTION = pmethoddesc.FUNCTION.ORIGIN
pfrommethod_return.ARRAY /\ ~pfrommethod_return.INVOKE
~pfrommethod_return.STATIC
$from_source_valid(S_return, pfrommethod_return)
$from_permission(S_return, pfrommethod_return)
$from_valid(S_return, pfrommethod_return)
$from_factory_saved(S_return, n_factory)
~$from_factory_live(S_return, n_factory)
~((HOBJECT n_factory) <- S_return.ALLOCATIONS)
~((HARRAY n_callback) <- S_return.ALLOCATIONS)
$heap_owners($heap_graph(S_return), HOBJECT n_factory) = 0
$node_children(S_return, HOBJECT n_factory) = eps
$node_children(S_return, HOBJECT n_produced) = [HOBJECT n_receiver]
$heap_owners($heap_graph(S_return), HOBJECT n_receiver) = 1
$outputs(S_return.EVENTS) = $ptascii("Q;A;")
''') + guards('S_return')

    old_text, inherited, reached, _ = render_instance_wrapper(fixture, filename, expected)
    prefix = old_text.split('\ndec $main()')[0].replace('FromInstance', 'InvokeFactory')
    inherited = inherited[len(computed_start('S_name', {'fixture': fixture, 'filename': filename}, 8)):reached]
    inherited = [check.replace('FromInstance', 'InvokeFactory').replace('$ptascii("H;', '$ptascii("Q;A;F;H;')
                 for check in inherited]
    inherited = seek('S_name', 'S_return', 8) + inherited
    index = inherited.index('S_name.OBJECTS[n_closure] = FROMCALLABLECLOSURE pfrommethod')
    inherited[index + 1:index + 1] = lines(r'''
n_closure = n_produced
pfrommethod = pfrommethod_return
pfrommethod.FACTORY = (n_factory)
S_name.OBJECTS[n_factory] = FROMCALLABLEFACTORY porigin_create
~((HOBJECT n_factory) <- S_name.ALLOCATIONS)
$heap_owners($heap_graph(S_name), HOBJECT n_factory) = 0
$from_factory_saved(S_name, n_factory)
$from_source_valid(S_name, pfrommethod)
''')
    index = inherited.index('~$from_current(S_callback)')
    inherited[index + 1:index + 1] = lines(r'''
~((HOBJECT n_factory) <- S_callback.ALLOCATIONS)
$from_factory_saved(S_callback, n_factory)
$from_source_valid(S_callback, pfrommethod)
$from_valid(S_callback, pfrommethod)
''')
    index = inherited.index('~((HOBJECT n_closure) <- S_done.ALLOCATIONS)')
    inherited[index + 1:index + 1] = lines(r'''
~((HOBJECT n_factory) <- S_done.ALLOCATIONS)
$heap_owners($heap_graph(S_done), HOBJECT n_factory) = 0
$from_factory_saved(S_done, n_factory)
$from_source_valid(S_done, pfrommethod)
''')
    genuine += inherited

    controls = lines(r'''
~$from_factory_invoke_site(S_entry_read, porigin_create)
~$from_factory_call_site(S_entry_read, porigin_create)
~$from_factory_invoke_site(S_entry_read, porigin_method_name)
~$from_factory_call_site(S_entry_read, porigin_method_name)
~$from_factory_invoke_site(S_entry_read[.SOURCES = eps], porigin_invoke)
~$from_factory_call_site(S_entry_read[.SOURCES = eps], porigin_invoke)
~$call_task_valid(S_entry, METHOD_PREP phpType20 eps false false z_entry)
~$call_task_valid(S_entry, METHOD_PREP phpType20 phpType7* true true z_entry)
~$call_task_valid(S_entry, METHOD_PREP phpType20 phpType7* false false $(z_entry + 1))
~$config_selected_valid(S_config, pconfigcall[.OWNER = eps])
~$config_selected_valid(S_config, pconfigcall[.OWNER = (n_name)])
~$config_selected_valid(S_config, pconfigcall[.OWNER = (n_receiver)])
~$config_selected_valid(S_config, pconfigcall[.OWNER = (|S_config.OBJECTS|)])
~$config_selected_valid(S_config, pconfigcall[.SITE = porigin_create])
~$config_selected_valid(S_config, pconfigcall[.SITE = porigin_method_name])
~$config_selected_valid(S_config, pconfigcall[.SELECTION = (0)])
~$config_selected_valid(S_config, pconfigcall[.KIND = INTRINSIC_FROM_CALLABLE])
~$config_call_valid(S_config, pconfigcall[.LINE = $(z_entry + 1)])
~$config_invoke_valid(S_config, pconfigcall[.SENT = eps])
S_wrong_creation = S_config[.OBJECTS[n_factory] = FROMCALLABLEFACTORY porigin_invoke]
~$from_factory_saved(S_wrong_creation, n_factory)
~$config_selected_valid(S_wrong_creation, pconfigcall)
S_wrong_factory_kind = S_config[.OBJECTS[n_factory] = INTRINSICCLOSURE INTRINSIC_FROM_CALLABLE_FACTORY]
~$from_factory_saved(S_wrong_factory_kind, n_factory)
~$config_selected_valid(S_wrong_factory_kind, pconfigcall)
S_retired_factory = S_config[.ALLOCATIONS = eps]
$from_factory_saved(S_retired_factory, n_factory)
~$from_factory_live(S_retired_factory, n_factory)
~$config_selected_valid(S_retired_factory, pconfigcall)
~$from_source_valid(S_name, pfrommethod[.FACTORY = eps])
~$from_source_valid(S_name, pfrommethod[.FACTORY = (n_receiver)])
~$from_source_valid(S_name, pfrommethod[.FACTORY = (|S_name.OBJECTS|)])
~$from_source_valid(S_name, pfrommethod[.SITE = porigin_create])
~$from_source_valid(S_name, pfrommethod[.SITE = porigin_method_name])
~$from_valid(S_name, pfrommethod[.FACTORY = eps])
~$from_valid(S_name, pfrommethod[.CLASS = pfrommethod.CLASS[.RECEIVER = (n_name)]])
~$from_valid(S_name, pfrommethod[.CLASS = pfrommethod.CLASS[.CALLED = porigin_base]])
~$from_valid(S_name, pfrommethod[.FUNCTION = porigin_create])
$config_trace_frames(S_config, pconfigcall[.KIND = INTRINSIC_FROM_CALLABLE], [PARRAY n_callback]) = [ptraceframe_api]
$config_trace_frames(S_config, pconfigcall, [PNULL]) = [ptraceframe_api[.ARGS = [(KINT 0, PNULL)]], ptraceframe_invoke]
''')
    checks = genuine + controls
    text = prefix + INVOKE_PHASE + INVOKE_ARGUMENT_PHASE + '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks, len(genuine), len(controls)


def alias_entry_checks(fixture, filename):
    checks = [check.replace('InvokeFactory', 'AliasFactory')
              for check in invoke_entry_checks(fixture, filename)]
    index = checks.index('~$ppfirstclass(phpType7*)')
    checks[index:index + 1] = ['$ppfirstclass(phpType7*)',
                               'phpType7* = [(NVariadicPlaceholder metadata_placeholder)]']
    index = checks.index('~$from_factory_call_site(S_read, porigin_invoke)')
    checks[index + 1:index + 1] = ['~$from_factory_invoke_site(S_read, porigin_invoke)',
                                 '$invoke_capture_source(S_read, porigin_invoke)']
    return checks


ALIAS_PHASE = r'''
def $scoped_phase(S, 29) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_FROM_CALLABLE_FACTORY
  -- if pconfigcall.INDEX = 0
  -- if pconfigcall.OWNER =/= eps
def $scoped_phase(S, 28) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $ptlc(pcallcontext.NAME) = $ptlc($ptascii("clearAliasFactoryArgumentReview20"))
  -- if $lookup(S.ENV, $ptascii("alias")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED PNULL
  -- if $outputs(S.EVENTS) = $ptascii("Q;S:same;I;A;")
def $scoped_phase(S, 25) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_FROM_CALLABLE_FACTORY
  -- if pconfigcall.OWNER =/= eps
def $scoped_phase(S, 26) = true
  -- if S.RESULT = KNOWN (POBJECT n)
  -- if S.OBJECTS[n] = FROMCALLABLECLOSURE pfrommethod
  -- if pfrommethod.FACTORY =/= eps
'''


def render_factory_alias(fixture, filename, expected):
    genuine = alias_entry_checks(fixture, filename)
    genuine = [check.replace('S_capture', 'S_entry_capture').replace('S_read', 'S_entry_read').replace('porigin_invoke', 'porigin_alias') for check in genuine]
    genuine += lines(r'''
$method_receiver_operand_valid(S_entry, expression_receiver, poperand_factory)
S_alias_budget = $drive_steps(S_entry, 1)
S_alias_budget.COMPLETION = BUDGET
S_alias = S_alias_budget[.COMPLETION = NORMAL]
S_alias = $invoke_capture(S_entry_read, n_factory, (porigin_alias))
S_alias = $method_select(S_entry, poperand_factory, $base64(text_method), phpType7*, z_entry)
S_alias.TODO = ptask_entry*
S_alias.ORIGIN = (porigin_alias)
S_alias.CURRENT = S_entry.CURRENT
S_alias.FRAMES = S_entry.FRAMES
S_alias.RESULT = KNOWN (POBJECT n_factory)
S_alias.BASE = BASE_VALUE (KNOWN PNULL)
S_alias.OBJECTS = S_entry.OBJECTS
S_alias.ALLOCATIONS = S_entry.ALLOCATIONS
S_alias.CLOSURESCOPES = S_entry.CLOSURESCOPES
S_alias.CLOSUREBINDINGS = S_entry.CLOSUREBINDINGS
S_alias.CLASSCONSTANTHISTORY = S_entry.CLASSCONSTANTHISTORY
$from_factory_live(S_alias, n_factory)
$from_factory_saved(S_alias, n_factory)
$node_children(S_alias, HOBJECT n_factory) = eps
$heap_owners($heap_graph(S_alias), HOBJECT n_factory) = 2
$outputs(S_alias.EVENTS) = $ptascii("Q;")
''') + guards('S_alias')
    genuine += seek('S_start', 'S_alias', 29) + lines(r'''
S_start.TODO = (CONFIG_ARGS pconfigcall_start) :: ptask_start*
pconfigcall_start.KIND = INTRINSIC_FROM_CALLABLE_FACTORY
pconfigcall_start.INDEX = 0
pconfigcall_start.SENT = eps
~pconfigcall_start.NAMED
pconfigcall_start.OWNER = (n_factory)
pconfigcall_start.SELECTION = eps
pconfigcall_start.PACKS = eps
porigin_invoke = pconfigcall_start.SITE
porigin_invoke =/= porigin_create /\ porigin_invoke =/= porigin_alias
S_start.ORIGIN = (porigin_invoke)
S_start.CURRENT = eps
S_start.FRAMES = eps
$api_frame_scope(S_start) = eps
$method_current_scope(S_start) = eps
$from_factory_call_site(S_start, porigin_invoke)
~$from_factory_invoke_site(S_start, porigin_invoke)
~$invoke_capture_source(S_start, porigin_invoke)
$origin_node(S_start.SOURCES, porigin_invoke) = (NExprFuncCall expression_alias (SEQUENCE phpType7_invoke*) metadata_invoke_call)
$origin_child((porigin_invoke), [PCFIELD 0]) = (porigin_alias_variable)
$origin_node(S_start.SOURCES, porigin_alias_variable) = (NExprVariable (BYTES text_alias) metadata_alias)
$base64(text_alias) = $ptascii("alias")
~$ppfirstclass(phpType7_invoke*)
S_start.STORE[n_factory_cell] = DEFINED PNULL
$lookup(S_start.ENV, $ptascii("alias")) = (n_alias_cell)
S_start.STORE[n_alias_cell] = DEFINED (POBJECT n_factory)
S_start.OBJECTS[n_factory] = FROMCALLABLEFACTORY porigin_create
$from_factory_live(S_start, n_factory)
$config_selected_valid(S_start, pconfigcall_start)
$config_call_valid(S_start, pconfigcall_start)
$call_task_valid(S_start, CONFIG_ARGS pconfigcall_start)
$task_nodes(CONFIG_ARGS pconfigcall_start) = [HOBJECT n_factory]
$node_children(S_start, HOBJECT n_factory) = eps
$heap_owners($heap_graph(S_start), HOBJECT n_factory) = 2
$outputs(S_start.EVENTS) = $ptascii("Q;S:same;I;")
''') + guards('S_start')
    genuine += seek('S_argument', 'S_start', 28) + lines(r'''
S_argument.CURRENT = (pcallcontext_argument)
$ptlc(pcallcontext_argument.NAME) = $ptlc($ptascii("clearAliasFactoryArgumentReview20"))
pcallcontext_argument.LEXICAL_CLASS = eps
pcallcontext_argument.CALLED_CLASS = eps
pcallcontext_argument.INSTANCE = eps
pcallcontext_argument.RECEIVER = eps
S_argument.STORE[n_factory_cell] = DEFINED PNULL
S_argument.STORE[n_alias_cell] = DEFINED PNULL
S_argument_global = $global_table_view(S_argument)
$lookup(S_argument_global.ENV, $ptascii("alias")) = (n_alias_cell)
$from_factory_live(S_argument, n_factory)
$from_factory_saved(S_argument, n_factory)
$node_children(S_argument, HOBJECT n_factory) = eps
$heap_owners($heap_graph(S_argument), HOBJECT n_factory) = 1
pframe_argument = S_argument.FRAMES[0]
$call_saved_context_valid(S_argument, pframe_argument)
$tasks_nodes(pframe_argument.TODO) = [HOBJECT n_factory]
$outputs(S_argument.EVENTS) = $ptascii("Q;S:same;I;A;")
''') + guards('S_argument')
    genuine += seek('S_config', 'S_argument', 25) + lines(r'''
S_config.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_start*
pconfigcall.SENT = [NAMED_SENT (KNOWN (PARRAY n_callback))]
pconfigcall = pconfigcall_start[.INDEX = 1][.SENT = [NAMED_SENT (KNOWN (PARRAY n_callback))]][.NAMED = true]
S_config.ORIGIN = (porigin_invoke)
S_config.CURRENT = eps
S_config.FRAMES = eps
$api_frame_scope(S_config) = eps
S_config.STORE[n_factory_cell] = DEFINED PNULL
S_config.STORE[n_alias_cell] = DEFINED PNULL
S_config.OBJECTS[n_factory] = FROMCALLABLEFACTORY porigin_create
$typed_callback_array(S_config, n_callback)
$entry_lookup(S_config.ARRAYS[n_callback].ITEMS, KINT 0) = (pitem_receiver)
$entry_lookup(S_config.ARRAYS[n_callback].ITEMS, KINT 1) = (pitem_method)
$entry_value(S_config, pitem_receiver) = POBJECT n_receiver
pvalue_method = $entry_value(S_config, pitem_method)
$string_bytes(pvalue_method) = ($ptascii("append"))
S_config.OBJECTS[n_receiver] = INSTANCE porigin_child
(HOBJECT n_receiver) <- S_config.ALLOCATIONS
(HARRAY n_callback) <- S_config.ALLOCATIONS
$from_factory_live(S_config, n_factory)
$from_factory_owner(S_config, pconfigcall) = (n_factory)
$config_selected_valid(S_config, pconfigcall)
$config_call_valid(S_config, pconfigcall)
$config_sent_shape(S_config, pconfigcall)
$config_invoke_valid(S_config, pconfigcall)
$call_task_valid(S_config, CONFIG_INVOKE pconfigcall)
$task_nodes(CONFIG_INVOKE pconfigcall) = [HOBJECT n_factory, HARRAY n_callback]
$node_children(S_config, HOBJECT n_factory) = eps
$heap_owners($heap_graph(S_config), HOBJECT n_factory) = 1
$heap_owners($heap_graph(S_config), HOBJECT n_receiver) = 1
$outputs(S_config.EVENTS) = $ptascii("Q;S:same;I;A;")
''') + guards('S_config')
    genuine += seek('S_return', 'S_config', 26) + lines(r'''
S_return.RESULT = KNOWN (POBJECT n_produced)
S_return.OBJECTS[n_produced] = FROMCALLABLECLOSURE pfrommethod_return
n_produced =/= n_factory /\ n_produced =/= n_receiver
pfrommethod_return.SITE = porigin_invoke
pfrommethod_return.FACTORY = (n_factory)
pfrommethod_return.SCOPE = eps
pfrommethod_return.CALLED = eps
pfrommethod_return.THIS = eps
pfrommethod_return.CREATION = eps
pfrommethod_return.CLASS.REQUESTED = porigin_child
pfrommethod_return.CLASS.CALLED = porigin_child
pfrommethod_return.CLASS.RECEIVER = (n_receiver)
pfrommethod_return.FUNCTION = pmethoddesc.FUNCTION.ORIGIN
pfrommethod_return.ARRAY /\ ~pfrommethod_return.INVOKE
~pfrommethod_return.STATIC
$from_source_valid(S_return, pfrommethod_return)
$from_permission(S_return, pfrommethod_return)
$from_valid(S_return, pfrommethod_return)
$from_factory_saved(S_return, n_factory)
~$from_factory_live(S_return, n_factory)
~((HOBJECT n_factory) <- S_return.ALLOCATIONS)
~((HARRAY n_callback) <- S_return.ALLOCATIONS)
$heap_owners($heap_graph(S_return), HOBJECT n_factory) = 0
$node_children(S_return, HOBJECT n_factory) = eps
$node_children(S_return, HOBJECT n_produced) = [HOBJECT n_receiver]
$heap_owners($heap_graph(S_return), HOBJECT n_receiver) = 1
$outputs(S_return.EVENTS) = $ptascii("Q;S:same;I;A;")
''') + guards('S_return')

    old_text, inherited, reached, _ = render_instance_wrapper(fixture, filename, expected)
    prefix = old_text.split('\ndec $main()')[0].replace('FromInstance', 'AliasFactory')
    inherited = inherited[:reached]
    inherited = inherited[len(computed_start('S_name', {'fixture': fixture, 'filename': filename}, 8)):]
    inherited = [check.replace('FromInstance', 'AliasFactory').replace('$ptascii("H;', '$ptascii("Q;S:same;I;A;F;H;')
                 for check in inherited]
    inherited = seek('S_name', 'S_return', 8) + inherited
    index = inherited.index('S_name.OBJECTS[n_closure] = FROMCALLABLECLOSURE pfrommethod')
    inherited[index + 1:index + 1] = lines(r'''
n_closure = n_produced
pfrommethod = pfrommethod_return
pfrommethod.FACTORY = (n_factory)
S_name.OBJECTS[n_factory] = FROMCALLABLEFACTORY porigin_create
~((HOBJECT n_factory) <- S_name.ALLOCATIONS)
$heap_owners($heap_graph(S_name), HOBJECT n_factory) = 0
$from_factory_saved(S_name, n_factory)
~$from_factory_live(S_name, n_factory)
$from_source_valid(S_name, pfrommethod)
$node_children(S_name, HOBJECT n_factory) = eps
''')
    index = inherited.index('~$from_current(S_callback)')
    inherited[index + 1:index + 1] = lines(r'''
~((HOBJECT n_factory) <- S_callback.ALLOCATIONS)
$from_factory_saved(S_callback, n_factory)
$from_source_valid(S_callback, pfrommethod)
$from_valid(S_callback, pfrommethod)
''')
    index = inherited.index('~((HOBJECT n_closure) <- S_done.ALLOCATIONS)')
    inherited[index + 1:index + 1] = lines(r'''
~((HOBJECT n_factory) <- S_done.ALLOCATIONS)
$heap_owners($heap_graph(S_done), HOBJECT n_factory) = 0
$from_factory_saved(S_done, n_factory)
$from_source_valid(S_done, pfrommethod)
''')
    genuine += inherited

    # Constructed source/task/liveness controls do not evaluate absent dispatch.
    controls = lines(r'''
~$invoke_capture_source(S_entry_read, porigin_create)
~$invoke_capture_source(S_entry_read, porigin_method_name)
~$invoke_capture_source(S_entry_read, porigin_invoke)
~$invoke_capture_source(S_entry_read[.SOURCES = eps], porigin_alias)
~$call_task_valid(S_entry[.ORIGIN = eps], METHOD_PREP phpType20 phpType7* false false z_entry)
~$call_task_valid(S_entry[.ORIGIN = (porigin_create)], METHOD_PREP phpType20 phpType7* false false z_entry)
~$method_receiver_operand_valid(S_entry, expression_receiver, KNOWN (POBJECT n_factory))
~$method_receiver_operand_valid(S_entry, expression_receiver, VARIABLE $ptascii("alias") z_entry)
~$call_task_valid(S_entry, METHOD_PREP (NIdentifier (BYTES "b3RoZXI=") metadata_name) phpType7* false false z_entry)
~$call_task_valid(S_entry, METHOD_PREP phpType20 eps false false z_entry)
~$call_task_valid(S_entry, METHOD_PREP phpType20 phpType7* true false z_entry)
~$call_task_valid(S_entry, METHOD_PREP phpType20 phpType7* false true z_entry)
~$call_task_valid(S_entry, METHOD_PREP phpType20 phpType7* false false $(z_entry + 1))
S_retired_alias_source = S_entry_read[.ALLOCATIONS = eps]
$from_factory_saved(S_retired_alias_source, n_factory)
~$from_factory_live(S_retired_alias_source, n_factory)
~$closure_callable(S_retired_alias_source, n_factory)
~$closure_live_object_valid(S_retired_alias_source, n_factory)
S_wrong_creation = S_entry_read[.OBJECTS[n_factory] = FROMCALLABLEFACTORY porigin_alias]
~$from_factory_saved(S_wrong_creation, n_factory)
~$from_factory_live(S_wrong_creation, n_factory)
~$closure_callable(S_wrong_creation, n_factory)
S_wrong_factory_kind = S_entry_read[.OBJECTS[n_factory] = INTRINSICCLOSURE INTRINSIC_FROM_CALLABLE_FACTORY]
~$from_factory_saved(S_wrong_factory_kind, n_factory)
~$from_factory_live(S_wrong_factory_kind, n_factory)
~$closure_callable(S_wrong_factory_kind, n_factory)
~$closure_live_object_valid(S_wrong_factory_kind, n_factory)
S_no_creation_name = S_entry_read[.CODE[n_unit] = pcode[.NAMES = eps]]
~$from_factory_saved(S_no_creation_name, n_factory)
~$from_factory_live(S_no_creation_name, n_factory)
~$config_selected_valid(S_config, pconfigcall[.OWNER = eps])
~$config_selected_valid(S_config, pconfigcall[.OWNER = (n_name)])
~$config_selected_valid(S_config, pconfigcall[.OWNER = (n_receiver)])
~$config_selected_valid(S_config, pconfigcall[.OWNER = (|S_config.OBJECTS|)])
~$config_selected_valid(S_config, pconfigcall[.SITE = porigin_create])
~$config_selected_valid(S_config, pconfigcall[.SITE = porigin_alias])
~$config_selected_valid(S_config, pconfigcall[.SELECTION = (0)])
~$config_selected_valid(S_config, pconfigcall[.KIND = INTRINSIC_FROM_CALLABLE])
~$config_invoke_valid(S_config, pconfigcall[.SENT = eps])
S_retired_config_owner = S_config[.ALLOCATIONS = eps]
$from_factory_saved(S_retired_config_owner, n_factory)
~$from_factory_live(S_retired_config_owner, n_factory)
~$config_selected_valid(S_retired_config_owner, pconfigcall)
S_wrong_protocol_object = S_config[.OBJECTS[n_factory] = INTRINSICCLOSURE INTRINSIC_FROM_CALLABLE_FACTORY]
~$config_selected_valid(S_wrong_protocol_object, pconfigcall)
~$from_source_valid(S_callback, pfrommethod[.FACTORY = eps])
~$from_valid(S_callback, pfrommethod[.FACTORY = eps])
~$from_source_valid(S_callback, pfrommethod[.FACTORY = (n_receiver)])
~$from_valid(S_callback, pfrommethod[.FACTORY = (n_receiver)])
~$from_source_valid(S_callback, pfrommethod[.FACTORY = (|S_callback.OBJECTS|)])
~$from_valid(S_callback, pfrommethod[.FACTORY = (|S_callback.OBJECTS|)])
~$from_source_valid(S_callback, pfrommethod[.SITE = porigin_create])
~$from_valid(S_callback, pfrommethod[.SITE = porigin_create])
~$from_source_valid(S_callback, pfrommethod[.SITE = porigin_alias])
~$from_valid(S_callback, pfrommethod[.SITE = porigin_alias])
S_saved_wrong_creation = S_callback[.OBJECTS[n_factory] = FROMCALLABLEFACTORY porigin_alias]
~$from_source_valid(S_saved_wrong_creation, pfrommethod)
~$from_valid(S_saved_wrong_creation, pfrommethod)
$from_source_valid(S_callback[.CURRENT = eps], pfrommethod)
$from_valid(S_callback[.CURRENT = eps], pfrommethod)
''')
    checks = genuine + controls
    text = prefix + INVOKE_PHASE + ALIAS_PHASE + '\ndec $main() : bool\ndef $main() = true\n'
    text += ''.join('  -- if ' + check + '\n' for check in checks)
    return text, checks, len(genuine), len(controls)
