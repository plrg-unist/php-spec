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
