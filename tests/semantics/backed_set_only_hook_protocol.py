"""Check implicit setter receives, backing writes and original assignment results."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()

PREFIX = ('dec $bso_replace(pcoccurrence*,pcpath,pcnode) : pcoccurrence*\n'
 'def $bso_replace(eps,pcpath,pcnode) = eps\n'
 'def $bso_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath pcnode) '
 ':: pcoccurrence*\n'
 'def $bso_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE '
 'pcpath_other pcnode_old) :: $bso_replace(pcoccurrence*,pcpath,pcnode)\n'
 '  -- if pcpath_other =/= pcpath\n'
 'dec $bso_class_replace(pclassdesc*,porigin,pclassdesc) : pclassdesc*\n'
 'def $bso_class_replace(eps,porigin,pclassdesc) = eps\n'
 'def $bso_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_new :: pclassdesc*\n'
 '  -- if pclassdesc_old.ORIGIN = porigin\n'
 'def $bso_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_old :: '
 '$bso_class_replace(pclassdesc*,porigin,pclassdesc_new)\n'
 '  -- if pclassdesc_old.ORIGIN =/= porigin\n'
 'dec $bso_stage(pstate,nat) : bool\n'
 'def $bso_stage(S,0) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (ASSIGN_ARRAY pbase 17 false) :: ptask*\n'
 '  -- if S.RESULT = KNOWN (PINT 20)\n'
 'def $bso_stage(S,1) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_SET_TARGET ppropertyhook\n'
 '  -- if S.TODO = (ASSIGN_ARRAY pbase 6 false) :: ptask*\n'
 '  -- if S.RESULT = KNOWN (PINT 33)\n'
 'def $bso_stage(S,2) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (PROPERTY_SET_RESULT ppropertyhook (PINT 20)) :: ptask*\n'
 'def $bso_stage(S,3) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_SET_TARGET ppropertyhook\n'
 '  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: ptask*\n'
 '  -- if $lookup(S.ENV,$ptascii("value")) = (n_cell)\n'
 '  -- if S.STORE[n_cell] = DEFINED (PARRAY n_array)\n'
 'def $bso_stage(S,4) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) 26) :: (DIM_FETCH 26) :: ptask*\n'
 '  -- if $base64(text_name) = $ptascii("value")\n'
 'def $bso_stage(S,n) = false -- otherwise\n'
 'dec $bso_seek(pstate,nat,nat) : pstate\n'
 'def $bso_seek(S,n_stage,n) = S\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if $bso_stage(S,n_stage) \\/ n = 0\n'
 'def $bso_seek(S,n_stage,n) = $bso_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if ~$bso_stage(S,n_stage) /\\ $(n > 0)\n'
 'def $bso_seek(S,n_stage,n) = $bso_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
 '  -- if $throwable_pending(S.COMPLETION) /\\ $(n > 0)\n'
 'def $bso_seek(S,n_stage,n) = S -- otherwise\n'
 'dec $bso_after(pstate,pstate) : pstate\n'
 'def $bso_after(S,S_next) = '
 '$gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))\n'
 'dec $bso_guard(pstate) : bool\n'
 'def $bso_guard(S) = ($call_descriptors_valid(S) /\\ $declaration_history_valid(S) /\\ $property_state_valid(S) /\\ '
 '$heap_valid($heap_prune($heap_graph(S))))\n')

COMMON = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("BackedSetParent71"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("BackedSetChild71"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 'pclassdesc_parent.KIND = "class" /\\ pclassdesc_parent.PARENT = eps /\\ ~pclassdesc_parent.READONLY /\\ '
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ pclassdesc_child.PROPERTIES = eps',
 '$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_parent)',
 'ppropertydesc = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc.ORIGIN = porigin_property',
 'ppropertydesc.NAME = $ptascii("value") /\\ ppropertydesc.KEY = ppropertydesc.NAME /\\ ppropertydesc.TYPE = '
 '([(PTBRANCH ([PTBUILTIN "int"]))]) /\\ ppropertydesc.VISIBILITY = PROPERTY_PUBLIC /\\ ppropertydesc.SETVISIBILITY '
 '= eps',
 '$property_default_state(S,ppropertydesc) = (PROP_VALUE (DIRECT (PINT 10))) /\\ ~ppropertydesc.STATIC /\\ '
 '~ppropertydesc.READONLY /\\ ~ppropertydesc.FINAL',
 '$property_layout(S,porigin_parent,|S.CLASSES|) = [ppropertydesc] /\\ $property_layout(S,porigin_child,|S.CLASSES|) '
 '= [ppropertydesc]',
 '$property_set_origin(S,ppropertydesc) = (porigin_hook)',
 '$property_hook_origin(S,ppropertydesc) = eps /\\ $property_hook_effective_origin(S,ppropertydesc) = eps /\\ '
 '~$property_hook_virtual(S,ppropertydesc)',
 '$function_at(S.FUNCTIONS,porigin_hook) = (pfunction_hook)',
 'pfunction_hook.SIGNATURE = $property_set_signature(ppropertydesc) /\\ pfunction_hook.SIGNATURE = {PARAMETERS '
 '([{NAME $ptascii("value"), TYPE ppropertydesc.TYPE, BYREF false, VARIADIC false, REQUIRED true, DEFAULT PSNONE}]), '
 'RETURNS ([(PTBRANCH ([PTBUILTIN "void"]))]), BYREF false}',
 'pfunction_hook.NAME = pclassdesc_parent.NAME ++ $ptascii("::$value::set") /\\ pfunction_hook.DEFAULTS = eps /\\ '
 '~pfunction_hook.EARLY /\\ pfunction_hook.LINE = 4 /\\ pfunction_hook.ENDLINE = 7',
 'S.FUNCTIONS = [pfunction_hook] /\\ $ptascii("value") <- pfunction_hook.CVS /\\ '
 '$method_named(pclassdesc_parent.METHODS,$property_set_name(ppropertydesc.NAME)) = eps',
 'porigin_hook = PORIGIN n_source pcpath_hook',
 'pfunction_hook.BODY = pcpath_hook ++ [PCFIELD 5]',
 '$origin_node(S.SOURCES,porigin_hook) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook '
 'phpType16_hook phpType39_hook metadata_hook)',
 'phpType14_hook = SEQUENCE eps /\\ phpType24_hook = INTEGER 0 /\\ phpType4_hook = BOOLEAN false /\\ phpType16_hook '
 '= SEQUENCE eps',
 'phpType11_hook = NIdentifier (BYTES text_set) metadata_set',
 '$base64(text_set) = $ptascii("set") /\\ $hook_body_backed(phpType39_hook,ppropertydesc.NAME)',
 '$property_declaring_class(S.CLASSES,porigin_property) = (porigin_parent)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("offset")) = (pmethoddesc_parent_offset)',
 '$method_named(pclassdesc_child.METHODS,$ptascii("offset")) = (pmethoddesc_child_offset)',
 'pmethoddesc_parent_offset.OWNER = porigin_parent /\\ pmethoddesc_parent_offset.VISIBILITY = PROPERTY_PRIVATE /\\ '
 'pmethoddesc_child_offset.OWNER = porigin_child /\\ pmethoddesc_child_offset.VISIBILITY = PROPERTY_PRIVATE',
 'S.OBJECTS[n_child] = INSTANCE porigin_child /\\ (HOBJECT n_child) <- S.ALLOCATIONS',
 '$property_effective_desc(S,n_child,$ptascii("value")) = (ppropertydesc) /\\ $property_hook_instance(S,n_child) /\\ '
 '$property_hook_declared(S,n_child,$ptascii("value"))',
 '~$property_hook_read_needed(S,n_child,$ptascii("value")) /\\ $property_resolve(S,n_child,$ptascii("value")) = '
 'PROPERTY_ACCESS ppropertydesc.KEY',
 '$bso_guard(S)']

CONTROLS = ['$bso_stage(S,0)',
 '$lookup(S.ENV,$ptascii("child")) = (n_child_cell)',
 'S.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("BackedSetParent71"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("BackedSetChild71"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 'pclassdesc_parent.KIND = "class" /\\ pclassdesc_parent.PARENT = eps /\\ ~pclassdesc_parent.READONLY /\\ '
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ pclassdesc_child.PROPERTIES = eps',
 '$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_parent)',
 'ppropertydesc = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc.ORIGIN = porigin_property',
 'ppropertydesc.NAME = $ptascii("value") /\\ ppropertydesc.KEY = ppropertydesc.NAME /\\ ppropertydesc.TYPE = '
 '([(PTBRANCH ([PTBUILTIN "int"]))]) /\\ ppropertydesc.VISIBILITY = PROPERTY_PUBLIC /\\ ppropertydesc.SETVISIBILITY '
 '= eps',
 '$property_default_state(S,ppropertydesc) = (PROP_VALUE (DIRECT (PINT 10))) /\\ ~ppropertydesc.STATIC /\\ '
 '~ppropertydesc.READONLY /\\ ~ppropertydesc.FINAL',
 '$property_layout(S,porigin_parent,|S.CLASSES|) = [ppropertydesc] /\\ $property_layout(S,porigin_child,|S.CLASSES|) '
 '= [ppropertydesc]',
 '$property_set_origin(S,ppropertydesc) = (porigin_hook)',
 '$property_hook_origin(S,ppropertydesc) = eps /\\ $property_hook_effective_origin(S,ppropertydesc) = eps /\\ '
 '~$property_hook_virtual(S,ppropertydesc)',
 '$function_at(S.FUNCTIONS,porigin_hook) = (pfunction_hook)',
 'pfunction_hook.SIGNATURE = $property_set_signature(ppropertydesc) /\\ pfunction_hook.SIGNATURE = {PARAMETERS '
 '([{NAME $ptascii("value"), TYPE ppropertydesc.TYPE, BYREF false, VARIADIC false, REQUIRED true, DEFAULT PSNONE}]), '
 'RETURNS ([(PTBRANCH ([PTBUILTIN "void"]))]), BYREF false}',
 'pfunction_hook.NAME = pclassdesc_parent.NAME ++ $ptascii("::$value::set") /\\ pfunction_hook.DEFAULTS = eps /\\ '
 '~pfunction_hook.EARLY /\\ pfunction_hook.LINE = 4 /\\ pfunction_hook.ENDLINE = 7',
 'S.FUNCTIONS = [pfunction_hook] /\\ $ptascii("value") <- pfunction_hook.CVS /\\ '
 '$method_named(pclassdesc_parent.METHODS,$property_set_name(ppropertydesc.NAME)) = eps',
 'porigin_hook = PORIGIN n_source pcpath_hook',
 'pfunction_hook.BODY = pcpath_hook ++ [PCFIELD 5]',
 '$origin_node(S.SOURCES,porigin_hook) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook '
 'phpType16_hook phpType39_hook metadata_hook)',
 'phpType14_hook = SEQUENCE eps /\\ phpType24_hook = INTEGER 0 /\\ phpType4_hook = BOOLEAN false /\\ phpType16_hook '
 '= SEQUENCE eps',
 'phpType11_hook = NIdentifier (BYTES text_set) metadata_set',
 '$base64(text_set) = $ptascii("set") /\\ $hook_body_backed(phpType39_hook,ppropertydesc.NAME)',
 '$property_declaring_class(S.CLASSES,porigin_property) = (porigin_parent)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("offset")) = (pmethoddesc_parent_offset)',
 '$method_named(pclassdesc_child.METHODS,$ptascii("offset")) = (pmethoddesc_child_offset)',
 'pmethoddesc_parent_offset.OWNER = porigin_parent /\\ pmethoddesc_parent_offset.VISIBILITY = PROPERTY_PRIVATE /\\ '
 'pmethoddesc_child_offset.OWNER = porigin_child /\\ pmethoddesc_child_offset.VISIBILITY = PROPERTY_PRIVATE',
 'S.OBJECTS[n_child] = INSTANCE porigin_child /\\ (HOBJECT n_child) <- S.ALLOCATIONS',
 '$property_effective_desc(S,n_child,$ptascii("value")) = (ppropertydesc) /\\ $property_hook_instance(S,n_child) /\\ '
 '$property_hook_declared(S,n_child,$ptascii("value"))',
 '~$property_hook_read_needed(S,n_child,$ptascii("value")) /\\ $property_resolve(S,n_child,$ptascii("value")) = '
 'PROPERTY_ACCESS ppropertydesc.KEY',
 '$bso_guard(S)',
 'S.ORIGIN = (porigin_site)',
 '$property_set_plan(S) = (ppropertyhook)',
 'ppropertyhook = {SITE porigin_site, OBJECT n_child, PROPERTY porigin_property, HOOK porigin_hook, LINE 17}',
 '$property_set_valid(S,ppropertyhook) /\\ $property_set_function(S,ppropertyhook) = (pfunction_hook) /\\ '
 '$property_set_pending(S)',
 '$property_set_needed(S,n_child,$ptascii("value")) /\\ ~$property_set_backing(S,n_child,ppropertydesc)',
 '$objectprops_at(S.OBJECTPROPS,n_child) = ([{DECL (porigin_property), NAME ppropertydesc.KEY, STATE PROP_VALUE '
 '(DIRECT (PINT 10))}])',
 'S_read = $property_read(S,POBJECT n_child,$ptascii("value"),17)',
 'S_read.COMPLETION = NORMAL /\\ S_read.RESULT = KNOWN (PINT 10) /\\ S_read.CURRENT = S.CURRENT /\\ S_read.FRAMES = '
 'S.FRAMES',
 'PhpStep: S ~> S_call_raw',
 'S_call = $bso_after(S,S_call_raw)',
 'S_call.TODO = (CALL_ARGS (PROPERTY_SET_TARGET ppropertyhook) eps 1 ([KNOWN (PINT 20)]) (porigin_site) 17) :: '
 '(PROPERTY_SET_RESULT ppropertyhook (PINT 20)) :: ptask_caller*',
 'S_call.CURRENT = eps /\\ S_call.OBJECTPROPS = S.OBJECTPROPS /\\ S_call.EVENTS = S.EVENTS /\\ S_call.ORIGIN = '
 '(porigin_site)',
 '$property_set_pending_call(S_call,ppropertyhook) /\\ $call_task_valid(S_call,CALL_ARGS (PROPERTY_SET_TARGET '
 'ppropertyhook) eps 1 ([KNOWN (PINT 20)]) (porigin_site) 17)',
 '$target_nodes(PROPERTY_SET_TARGET ppropertyhook) = eps /\\ $task_nodes(PROPERTY_SET_RESULT ppropertyhook (PINT '
 '20)) = [HOBJECT n_child]',
 '$bso_guard(S_call)',
 'PhpStep: S_call ~> S_entered_raw',
 'S_entered = $bso_after(S_call,S_entered_raw)',
 'S_entered.CURRENT = (pcallcontext_set)',
 'pcallcontext_set.TARGET = PROPERTY_SET_TARGET ppropertyhook /\\ pcallcontext_set.FUNCTION = porigin_hook /\\ '
 'pcallcontext_set.ARGC = 1 /\\ pcallcontext_set.CALLSITE = (porigin_site) /\\ pcallcontext_set.LINE = 17',
 'pcallcontext_set.LEXICAL_CLASS = (porigin_parent) /\\ pcallcontext_set.CALLED_CLASS = (porigin_child) /\\ '
 'pcallcontext_set.RECEIVER = (n_child) /\\ pcallcontext_set.INSTANCE = eps /\\ pcallcontext_set.PARAMS = '
 '[$ptascii("value")]',
 'S_entered.TODO = [TYPE_RECEIVE porigin_hook 0] /\\ S_entered.ORIGIN = (porigin_hook)',
 '$lookup(S_entered.ENV,$ptascii("value")) = (n_value_cell)',
 'S_entered.STORE[n_value_cell] = DEFINED (PINT 20)',
 '$typed_receive_valid(S_entered,porigin_hook,0) /\\ $named_receives_ready(S_entered,pfunction_hook) /\\ '
 '$default_parameter_line(S_entered,porigin_hook,0) = 4',
 '$property_set_context_valid(S_entered,pcallcontext_set) /\\ $call_receiver_roots(pcallcontext_set) = eps',
 'S_entered.OBJECTPROPS = S.OBJECTPROPS /\\ S_entered.EVENTS = S.EVENTS /\\ $bso_guard(S_entered)',
 'PhpStep: S_entered ~> S_received_raw',
 'S_received = $bso_after(S_entered,S_received_raw)',
 'S_received.COMPLETION = NORMAL /\\ S_received.CURRENT = S_entered.CURRENT /\\ S_received.FRAMES = S_entered.FRAMES '
 '/\\ S_received.EVENTS = S.EVENTS /\\ S_received.OBJECTPROPS = S.OBJECTPROPS',
 'S_received.TODO = $function_body_tasks(S_received,pfunction_hook) /\\ $bso_guard(S_received)']

BACKING = ['$bso_stage(S,1)',
 'S.CURRENT = (pcallcontext_set)',
 'pcallcontext_set.RECEIVER = (n_child)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("BackedSetParent71"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("BackedSetChild71"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 'pclassdesc_parent.KIND = "class" /\\ pclassdesc_parent.PARENT = eps /\\ ~pclassdesc_parent.READONLY /\\ '
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ pclassdesc_child.PROPERTIES = eps',
 '$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_parent)',
 'ppropertydesc = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc.ORIGIN = porigin_property',
 'ppropertydesc.NAME = $ptascii("value") /\\ ppropertydesc.KEY = ppropertydesc.NAME /\\ ppropertydesc.TYPE = '
 '([(PTBRANCH ([PTBUILTIN "int"]))]) /\\ ppropertydesc.VISIBILITY = PROPERTY_PUBLIC /\\ ppropertydesc.SETVISIBILITY '
 '= eps',
 '$property_default_state(S,ppropertydesc) = (PROP_VALUE (DIRECT (PINT 10))) /\\ ~ppropertydesc.STATIC /\\ '
 '~ppropertydesc.READONLY /\\ ~ppropertydesc.FINAL',
 '$property_layout(S,porigin_parent,|S.CLASSES|) = [ppropertydesc] /\\ $property_layout(S,porigin_child,|S.CLASSES|) '
 '= [ppropertydesc]',
 '$property_set_origin(S,ppropertydesc) = (porigin_hook)',
 '$property_hook_origin(S,ppropertydesc) = eps /\\ $property_hook_effective_origin(S,ppropertydesc) = eps /\\ '
 '~$property_hook_virtual(S,ppropertydesc)',
 '$function_at(S.FUNCTIONS,porigin_hook) = (pfunction_hook)',
 'pfunction_hook.SIGNATURE = $property_set_signature(ppropertydesc) /\\ pfunction_hook.SIGNATURE = {PARAMETERS '
 '([{NAME $ptascii("value"), TYPE ppropertydesc.TYPE, BYREF false, VARIADIC false, REQUIRED true, DEFAULT PSNONE}]), '
 'RETURNS ([(PTBRANCH ([PTBUILTIN "void"]))]), BYREF false}',
 'pfunction_hook.NAME = pclassdesc_parent.NAME ++ $ptascii("::$value::set") /\\ pfunction_hook.DEFAULTS = eps /\\ '
 '~pfunction_hook.EARLY /\\ pfunction_hook.LINE = 4 /\\ pfunction_hook.ENDLINE = 7',
 'S.FUNCTIONS = [pfunction_hook] /\\ $ptascii("value") <- pfunction_hook.CVS /\\ '
 '$method_named(pclassdesc_parent.METHODS,$property_set_name(ppropertydesc.NAME)) = eps',
 'porigin_hook = PORIGIN n_source pcpath_hook',
 'pfunction_hook.BODY = pcpath_hook ++ [PCFIELD 5]',
 '$origin_node(S.SOURCES,porigin_hook) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook '
 'phpType16_hook phpType39_hook metadata_hook)',
 'phpType14_hook = SEQUENCE eps /\\ phpType24_hook = INTEGER 0 /\\ phpType4_hook = BOOLEAN false /\\ phpType16_hook '
 '= SEQUENCE eps',
 'phpType11_hook = NIdentifier (BYTES text_set) metadata_set',
 '$base64(text_set) = $ptascii("set") /\\ $hook_body_backed(phpType39_hook,ppropertydesc.NAME)',
 '$property_declaring_class(S.CLASSES,porigin_property) = (porigin_parent)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("offset")) = (pmethoddesc_parent_offset)',
 '$method_named(pclassdesc_child.METHODS,$ptascii("offset")) = (pmethoddesc_child_offset)',
 'pmethoddesc_parent_offset.OWNER = porigin_parent /\\ pmethoddesc_parent_offset.VISIBILITY = PROPERTY_PRIVATE /\\ '
 'pmethoddesc_child_offset.OWNER = porigin_child /\\ pmethoddesc_child_offset.VISIBILITY = PROPERTY_PRIVATE',
 'S.OBJECTS[n_child] = INSTANCE porigin_child /\\ (HOBJECT n_child) <- S.ALLOCATIONS',
 '$property_effective_desc(S,n_child,$ptascii("value")) = (ppropertydesc) /\\ $property_hook_instance(S,n_child) /\\ '
 '$property_hook_declared(S,n_child,$ptascii("value"))',
 '~$property_hook_read_needed(S,n_child,$ptascii("value")) /\\ $property_resolve(S,n_child,$ptascii("value")) = '
 'PROPERTY_ACCESS ppropertydesc.KEY',
 '$bso_guard(S)',
 'pcallcontext_set.TARGET = PROPERTY_SET_TARGET ppropertyhook',
 'ppropertyhook.OBJECT = n_child /\\ ppropertyhook.PROPERTY = porigin_property /\\ ppropertyhook.HOOK = porigin_hook '
 '/\\ ppropertyhook.LINE = 17',
 'pcallcontext_set.FUNCTION = porigin_hook /\\ pcallcontext_set.LEXICAL_CLASS = (porigin_parent) /\\ '
 'pcallcontext_set.CALLED_CLASS = (porigin_child) /\\ pcallcontext_set.ARGC = 1',
 '$property_set_context_valid(S,pcallcontext_set) /\\ $property_set_entered(S,S.CURRENT,S.FRAMES,ppropertyhook)',
 '$lookup(S.ENV,$ptascii("value")) = (n_value_cell)',
 'S.STORE[n_value_cell] = DEFINED (PINT 20)',
 '$property_set_backing(S,n_child,ppropertydesc) /\\ ~$property_set_needed(S,n_child,$ptascii("value")) /\\ '
 '~$property_set_pending(S)',
 '$method_selected_scope(S,n_child,$ptascii("offset"),(porigin_parent)) = (pmethoddesc_parent_offset)',
 'S.TODO = (ASSIGN_ARRAY pbase_write 6 false) :: ptask_write*',
 'S.RESULT = KNOWN (PINT 33) /\\ $call_task_valid(S,ASSIGN_ARRAY pbase_write 6 false)',
 '$objectprops_at(S.OBJECTPROPS,n_child) = ([{DECL (porigin_property), NAME ppropertydesc.KEY, STATE PROP_VALUE '
 '(DIRECT (PINT 10))}])',
 'PhpStep: S ~> S_written_raw',
 'S_written = $bso_after(S,S_written_raw)',
 'S_written.COMPLETION = NORMAL /\\ S_written.RESULT = KNOWN (PINT 33) /\\ S_written.CURRENT = S.CURRENT /\\ '
 'S_written.FRAMES = S.FRAMES /\\ S_written.EVENTS = S.EVENTS',
 '$objectprops_at(S_written.OBJECTPROPS,n_child) = ([{DECL (porigin_property), NAME ppropertydesc.KEY, STATE '
 'PROP_VALUE (DIRECT (PINT 33))}])',
 '$bso_guard(S_written)',
 'S_return_found = $bso_seek(S_written,2,1000)',
 'S_return_found.COMPLETION = NORMAL \\/ S_return_found.COMPLETION = BUDGET',
 'S_return = S_return_found[.COMPLETION = NORMAL]',
 '$bso_stage(S_return,2)',
 'S_return.TODO = (PROPERTY_SET_RESULT ppropertyhook (PINT 20)) :: ptask_return*',
 'S_return.RESULT = KNOWN PNULL /\\ S_return.CURRENT = eps /\\ S_return.FRAMES = eps /\\ S_return.GLOBALTABLE = eps '
 '/\\ S_return.ORIGIN = (ppropertyhook.SITE)',
 '$objectprops_at(S_return.OBJECTPROPS,n_child) = ([{DECL (porigin_property), NAME ppropertydesc.KEY, STATE '
 'PROP_VALUE (DIRECT (PINT 33))}])',
 '$property_set_valid(S_return,ppropertyhook) /\\ $call_task_valid(S_return,PROPERTY_SET_RESULT ppropertyhook (PINT '
 '20)) /\\ $property_set_needed(S_return,n_child,$ptascii("value")) /\\ '
 '~$property_set_backing(S_return,n_child,ppropertydesc)',
 '$bso_guard(S_return)',
 'PhpStep: S_return ~> S_result_raw',
 'S_result = $bso_after(S_return,S_result_raw)',
 'S_result.COMPLETION = NORMAL /\\ S_result.RESULT = KNOWN (PINT 20) /\\ S_result.BASE = BASE_VALUE (KNOWN PNULL) '
 '/\\ S_result.TODO = ptask_return* /\\ S_result.OBJECTPROPS = S_return.OBJECTPROPS /\\ S_result.EVENTS = '
 'S_return.EVENTS',
 'S_read = $property_read(S_result,POBJECT n_child,$ptascii("value"),17)',
 'S_read.COMPLETION = NORMAL /\\ S_read.RESULT = KNOWN (PINT 33) /\\ '
 '~$property_hook_read_needed(S_result,n_child,$ptascii("value"))',
 '$bso_guard(S_result)']

ERROR = ['$bso_stage(S,3)',
 'S.CURRENT = (pcallcontext_set)',
 'pcallcontext_set.RECEIVER = (n_child)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("BackedSetParent71"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("BackedSetChild71"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 'pclassdesc_parent.KIND = "class" /\\ pclassdesc_parent.PARENT = eps /\\ ~pclassdesc_parent.READONLY /\\ '
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ pclassdesc_child.PROPERTIES = eps',
 '$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_parent)',
 'ppropertydesc = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc.ORIGIN = porigin_property',
 'ppropertydesc.NAME = $ptascii("value") /\\ ppropertydesc.KEY = ppropertydesc.NAME /\\ ppropertydesc.TYPE = '
 '([(PTBRANCH ([PTBUILTIN "int"]))]) /\\ ppropertydesc.VISIBILITY = PROPERTY_PUBLIC /\\ ppropertydesc.SETVISIBILITY '
 '= eps',
 '$property_default_state(S,ppropertydesc) = (PROP_VALUE (DIRECT (PINT 10))) /\\ ~ppropertydesc.STATIC /\\ '
 '~ppropertydesc.READONLY /\\ ~ppropertydesc.FINAL',
 '$property_layout(S,porigin_parent,|S.CLASSES|) = [ppropertydesc] /\\ $property_layout(S,porigin_child,|S.CLASSES|) '
 '= [ppropertydesc]',
 '$property_set_origin(S,ppropertydesc) = (porigin_hook)',
 '$property_hook_origin(S,ppropertydesc) = eps /\\ $property_hook_effective_origin(S,ppropertydesc) = eps /\\ '
 '~$property_hook_virtual(S,ppropertydesc)',
 '$function_at(S.FUNCTIONS,porigin_hook) = (pfunction_hook)',
 'pfunction_hook.SIGNATURE = $property_set_signature(ppropertydesc) /\\ pfunction_hook.SIGNATURE = {PARAMETERS '
 '([{NAME $ptascii("value"), TYPE ppropertydesc.TYPE, BYREF false, VARIADIC false, REQUIRED true, DEFAULT PSNONE}]), '
 'RETURNS ([(PTBRANCH ([PTBUILTIN "void"]))]), BYREF false}',
 'pfunction_hook.NAME = pclassdesc_parent.NAME ++ $ptascii("::$value::set") /\\ pfunction_hook.DEFAULTS = eps /\\ '
 '~pfunction_hook.EARLY /\\ pfunction_hook.LINE = 4 /\\ pfunction_hook.ENDLINE = 7',
 'S.FUNCTIONS = [pfunction_hook] /\\ $ptascii("value") <- pfunction_hook.CVS /\\ '
 '$method_named(pclassdesc_parent.METHODS,$property_set_name(ppropertydesc.NAME)) = eps',
 'porigin_hook = PORIGIN n_source pcpath_hook',
 'pfunction_hook.BODY = pcpath_hook ++ [PCFIELD 5]',
 '$origin_node(S.SOURCES,porigin_hook) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook '
 'phpType16_hook phpType39_hook metadata_hook)',
 'phpType14_hook = SEQUENCE eps /\\ phpType24_hook = INTEGER 0 /\\ phpType4_hook = BOOLEAN false /\\ phpType16_hook '
 '= SEQUENCE eps',
 'phpType11_hook = NIdentifier (BYTES text_set) metadata_set',
 '$base64(text_set) = $ptascii("set") /\\ $hook_body_backed(phpType39_hook,ppropertydesc.NAME)',
 '$property_declaring_class(S.CLASSES,porigin_property) = (porigin_parent)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("offset")) = (pmethoddesc_parent_offset)',
 '$method_named(pclassdesc_child.METHODS,$ptascii("offset")) = (pmethoddesc_child_offset)',
 'pmethoddesc_parent_offset.OWNER = porigin_parent /\\ pmethoddesc_parent_offset.VISIBILITY = PROPERTY_PRIVATE /\\ '
 'pmethoddesc_child_offset.OWNER = porigin_child /\\ pmethoddesc_child_offset.VISIBILITY = PROPERTY_PRIVATE',
 'S.OBJECTS[n_child] = INSTANCE porigin_child /\\ (HOBJECT n_child) <- S.ALLOCATIONS',
 '$property_effective_desc(S,n_child,$ptascii("value")) = (ppropertydesc) /\\ $property_hook_instance(S,n_child) /\\ '
 '$property_hook_declared(S,n_child,$ptascii("value"))',
 '~$property_hook_read_needed(S,n_child,$ptascii("value")) /\\ $property_resolve(S,n_child,$ptascii("value")) = '
 'PROPERTY_ACCESS ppropertydesc.KEY',
 '$bso_guard(S)',
 'pcallcontext_set.TARGET = PROPERTY_SET_TARGET ppropertyhook',
 'ppropertyhook.OBJECT = n_child /\\ ppropertyhook.PROPERTY = porigin_property /\\ ppropertyhook.HOOK = porigin_hook '
 '/\\ ppropertyhook.LINE = 21',
 'pcallcontext_set.FUNCTION = porigin_hook /\\ pcallcontext_set.LEXICAL_CLASS = (porigin_parent) /\\ '
 'pcallcontext_set.CALLED_CLASS = (porigin_child) /\\ pcallcontext_set.ARGC = 1 /\\ pcallcontext_set.CALLSITE = '
 '(ppropertyhook.SITE) /\\ pcallcontext_set.LINE = 21',
 'S.TODO = [TYPE_RECEIVE porigin_hook 0] /\\ S.ORIGIN = (porigin_hook)',
 '$lookup(S.ENV,$ptascii("value")) = (n_value_cell)',
 'S.STORE[n_value_cell] = DEFINED (PARRAY n_array)',
 'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
 '$property_set_context_valid(S,pcallcontext_set) /\\ $typed_receive_valid(S,porigin_hook,0) /\\ '
 '$named_receives_ready(S,pfunction_hook) /\\ $default_parameter_line(S,porigin_hook,0) = 4',
 '$objectprops_at(S.OBJECTPROPS,n_child) = ([{DECL (porigin_property), NAME ppropertydesc.KEY, STATE PROP_VALUE '
 '(DIRECT (PINT 33))}])',
 'ptbytes_message = pfunction_hook.NAME ++ $ptascii("(): Argument #1 ($value) must be of type int, array given, '
 'called in ") ++ $call_sourcefile(S.FILES,ppropertyhook.SITE) ++ $ptascii(" on line 21")',
 '$typed_parameter_conversion(S,pfunction_hook.SIGNATURE.PARAMETERS[0],PARRAY n_array) = TYPEREJECT',
 'PhpStep: S ~> S_error_raw',
 'S_error_raw.COMPLETION = THROWN "TypeError" ptbytes_message 4 /\\ S_error_raw.EVENTS = S.EVENTS /\\ '
 'S_error_raw.OBJECTPROPS = S.OBJECTPROPS /\\ S_error_raw.CURRENT = S.CURRENT /\\ S_error_raw.FRAMES = S.FRAMES',
 'S_error = $bso_after(S,S_error_raw)',
 'S_error.COMPLETION = THROWING n_error',
 '$object_name(S_error,n_error) = $ptascii("TypeError") /\\ $throwable_field(S_error,n_error,"message") = PSTRING '
 'ptbytes_message',
 '$objectprops_at(S_error.OBJECTPROPS,n_child) = ([{DECL (porigin_property), NAME ppropertydesc.KEY, STATE '
 'PROP_VALUE (DIRECT (PINT 33))}])',
 '$bso_guard(S_error)',
 'S_final_found = $bso_seek(S_error,4,1000)',
 'S_final_found.COMPLETION = NORMAL \\/ S_final_found.COMPLETION = BUDGET',
 'S_final = S_final_found[.COMPLETION = NORMAL]',
 '$bso_stage(S_final,4)',
 'S_final.CURRENT = eps /\\ S_final.FRAMES = eps /\\ $objectprops_at(S_final.OBJECTPROPS,n_child) = ([{DECL '
 '(porigin_property), NAME ppropertydesc.KEY, STATE PROP_VALUE (DIRECT (PINT 33))}])',
 '~$property_hook_pending(S_final) /\\ ~$property_hook_read_needed(S_final,n_child,$ptascii("value")) /\\ '
 '$bso_guard(S_final)',
 'PhpStep: S_final ~> S_fetch_raw',
 'S_fetch = $bso_after(S_final,S_fetch_raw)',
 'S_fetch.COMPLETION = NORMAL /\\ S_fetch.BASE = BASE_PROPERTY (POBJECT n_child) ppropertydesc.KEY /\\ '
 'S_fetch.CURRENT = eps /\\ S_fetch.FRAMES = eps',
 'PhpStep: S_fetch ~> S_read_raw',
 'S_read = $bso_after(S_fetch,S_read_raw)',
 'S_read.COMPLETION = NORMAL /\\ S_read.RESULT = KNOWN (PINT 33) /\\ S_read.CURRENT = eps /\\ S_read.FRAMES = eps '
 '/\\ S_read.OBJECTPROPS = S_final.OBJECTPROPS /\\ $bso_guard(S_read)']

DERIVED = ['~$property_set_backing(S_entered[.FRAMES = eps],n_child,ppropertydesc)',
 '~$property_set_backing(S_entered[.CURRENT = (pcallcontext_set[.RECEIVER = eps])],n_child,ppropertydesc)',
 '~$property_set_backing(S_entered[.CURRENT = (pcallcontext_set[.FUNCTION = porigin_parent])],n_child,ppropertydesc)',
 '~$property_set_pending_call(S_call[.TODO = ([(CALL_ARGS (PROPERTY_SET_TARGET ppropertyhook) eps 1 ([KNOWN (PINT '
 '20)]) (porigin_site) 17),(PROPERTY_SET_RESULT ppropertyhook (PINT 21))])],ppropertyhook)',
 '$property_set_origin(S,ppropertydesc[.TYPE = eps]) = eps /\\ $property_set_origin(S,ppropertydesc[.KEY = '
 '$ptascii("wrong")]) = eps /\\ $property_set_origin(S,ppropertydesc[.READONLY = true]) = eps',
 '$property_set_valid(S,ppropertyhook[.LINE = 18]) = false /\\ $property_set_function(S,ppropertyhook[.HOOK = '
 'porigin_parent]) = eps /\\ $property_set_function(S,ppropertyhook[.PROPERTY = porigin_parent]) = eps',
 '$property_set_valid(S,ppropertyhook[.SITE = porigin_hook]) = false',
 '$property_hook_parent_match(S,ppropertydesc,eps)',
 '$property_hook_parent_match(S,ppropertydesc,(ppropertydesc))',
 'S_wrong_owner = S[.CLASSES = $bso_class_replace(S.CLASSES,porigin_parent,pclassdesc_parent[.KIND = "trait"])]',
 '$property_set_origin(S_wrong_owner,ppropertydesc) = eps',
 'S_no_own = S[.CLASSES = $bso_class_replace(S.CLASSES,porigin_parent,pclassdesc_parent[.PROPERTIES = eps])]',
 '$property_set_origin(S_no_own,ppropertydesc) = eps /\\ $property_set_function(S_no_own,ppropertyhook) = eps',
 '$source_unit(S.SOURCES,n_source) = (pcunit_source)',
 'S.SOURCES = [pcunit_source]',
 'pcpath_group = pcpath_hook[0:$nabs($(|pcpath_hook| - 2))]',
 '$origin_node(S.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty phpType14_group phpType24_group '
 'phpType18_group phpType56_group (SEQUENCE ([NPropertyHook phpType14_hook phpType24_hook phpType4_hook '
 'phpType11_hook phpType16_hook phpType39_hook metadata_hook])) metadata_group)',
 'phpType38_ref = NPropertyHook phpType14_hook phpType24_hook (BOOLEAN true) phpType11_hook phpType16_hook '
 'phpType39_hook metadata_hook',
 'pcnode_group_ref = NStmtProperty phpType14_group phpType24_group phpType18_group phpType56_group (SEQUENCE '
 '([phpType38_ref])) metadata_group',
 'S_ref = S[.SOURCES = ([pcunit_source[.OCCURRENCES = '
 '$bso_replace($bso_replace(pcunit_source.OCCURRENCES,pcpath_hook,phpType38_ref),pcpath_group,pcnode_group_ref)]])]',
 '$property_set_origin(S_ref,ppropertydesc) = eps /\\ $property_set_function(S_ref,ppropertyhook) = eps',
 'phpType38_virtual = NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook phpType16_hook '
 '(SEQUENCE eps) metadata_hook',
 'pcnode_group_virtual = NStmtProperty phpType14_group phpType24_group phpType18_group phpType56_group (SEQUENCE '
 '([phpType38_virtual])) metadata_group',
 'S_virtual = S[.SOURCES = ([pcunit_source[.OCCURRENCES = '
 '$bso_replace($bso_replace(pcunit_source.OCCURRENCES,pcpath_hook,phpType38_virtual),pcpath_group,pcnode_group_virtual)]])]',
 '$property_set_origin(S_virtual,ppropertydesc) = eps',
 '$property_hook_trait_import_supported(S,pclassdesc_child,ppropertydesc) = false']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--group', choices=['controls', 'backing', 'error'], required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'backed_set_only_hook_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    clauses, negatives, case_index, start_stage = {
        'controls': (CONTROLS, DERIVED, 0, 0),
        'backing': (BACKING, [], 0, 1),
        'error': (ERROR, [], 0, 3),
    }[args.group]
    selections = [(args.group, clauses, negatives)]
    cases = [data['cases'][case_index]]
    sources = [HERE / 'backed-set-only-hook.php']
    php, adapter, bridge, worker, runner, compiler = (ROOT / name for name in [
        '.tools/php/bin/php', '_build/default/adapter/main.exe', '.tools/php-file.so',
        'frontend/worker.php', 'tests/semantics/_build/default/numeric_runner.exe', '.tools/spectec/bin/p4spectec'])
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    assert sha(compiler) == '26d77fb9bfae2b2868e137a94051f55f9b607660c340e9b22ae8300fb0d8ce88'
    assert sha(runner) == 'b57a2ed7daf86de23993a29d079083377cfef6da133739a164dbfdb9f11fd7a0'
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_bytes())]
    watched = [Path(__file__), Path(recorder.__file__), catalogue, *sources, profile_file, php,
               adapter, bridge, worker, runner, compiler, manifest, *modules, ROOT / 'spec/schema.json',
               ROOT / 'spec/php.watsup', ROOT / 'spec/nodes.json', ROOT / 'frontend/target.php',
               ROOT / 'frontend/wire.php', ROOT / 'frontend/wire.py',
               HERE / 'recorded_worker.py', HERE / 'static_types.py']
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    assert revision == args.revision and not status, (revision, status)
    before = {str(path): sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='backed-set-only-hook-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    derived = sum(len(row[2]) for row in selections)
    reached = sum(5 + len(row[1]) for row in selections)
    report = {'revision': revision, 'group': args.group, 'inputs': before, 'profile': profile, 'module_count': len(modules),
              'mode': 'SL', 'cache': False, 'det': True, 'records': [],
              'application_invocations': 0, 'application_evaluations': 0, 'source_agreements': 0,
              'derived_premises': derived, 'reached_premises': reached, 'premises': derived + reached,
              'cap_seconds': 90, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'jobs': 1}, 'passed': False}
    fixture = None
    try:
        flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
        fixtures = []
        for i, (source, case) in enumerate(zip(sources, cases)):
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256']
            frontend = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(bridge), str(worker)], out / ('frontend-' + str(i)))
            adapter_worker = None
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted'], parsed
                adapter_worker = Worker([str(adapter), str(ROOT)], out / ('adapter-' + str(i)))
                checked = adapter_worker.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                assert checked['ok'] and checked['ast'] == parsed['ast']
                fixtures.append(checked['fixture'])
            finally:
                if adapter_worker:
                    adapter_worker.close()
                frontend.close()
        content = PREFIX
        for selection, ast_fixture, source, case in zip(selections, fixtures, sources, cases):
            name, clauses, negatives = selection
            setup = ['S_initial = $php_run(' + ast_fixture + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $bso_seek(S_initial,' + str(start_stage) + ',1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            content += '\ndec $bso_' + name + '() : bool\ndef $bso_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $bso_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = (' + ' /\\ '.join('$bso_' + name + '()' for name, _, _ in selections) + ')\n'
        fixture = out / 'hook.watsup'
        fixture.write_text(content)
        report.update(fixture=str(fixture), fixture_sha256=sha(fixture), prepared=True, passed=True)
        if not args.prepare_only:
            process = recorder.recorded([str(compiler), 'algo', *map(str, modules), str(fixture)], out / 'compiler', 90)
            passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and not (out / 'compiler.stderr').read_bytes() and b'\ndef $main : bool =\n' in (out / 'compiler.stdout').read_bytes()
            report['records'].append({'id': 'algorithmic-compilation', 'process': process, 'passed': passed, 'application_evaluations': 0})
            report['passed'] = passed
            assert passed
            report['application_invocations'] = 1
            process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'state', 90)
            output = (out / 'state.stdout').read_bytes()
            evaluated = process['exit'] == 0 and output in (b'true\n', b'false\n')
            report['application_evaluations'] = int(evaluated)
            passed = evaluated and not process['timeout'] and not process['group_after'] and not (out / 'state.stderr').read_bytes() and output == b'true\n'
            report['records'].append({'id': 'strict-SL-application', 'process': process, 'passed': passed})
            report['passed'] = passed
    finally:
        report.update(inputs_stable=before == {str(path): sha(path) for path in watched},
                      fixture_stable=fixture is None or report['fixture_sha256'] == sha(fixture),
                      head_stable=revision == git('rev-parse', 'HEAD'), status_stable=status == git('status', '--short'))
        report['passed'] = report['passed'] and all(report[key] for key in ('inputs_stable', 'fixture_stable', 'head_stable', 'status_stable'))
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({key: report[key] for key in ('passed', 'application_evaluations', 'derived_premises', 'reached_premises', 'inputs_stable', 'head_stable', 'status_stable')}), flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
