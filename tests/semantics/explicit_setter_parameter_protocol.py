"""Check explicit setter parameter source, original string results and error sites."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()

PREFIX = ('dec $esp_replace(pcoccurrence*,pcpath,pcnode) : pcoccurrence*\n'
 'def $esp_replace(eps,pcpath,pcnode) = eps\n'
 'def $esp_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath '
 'pcnode) :: pcoccurrence*\n'
 'def $esp_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE '
 'pcpath_other pcnode_old) :: $esp_replace(pcoccurrence*,pcpath,pcnode)\n'
 '  -- if pcpath_other =/= pcpath\n'
 'dec $esp_class_replace(pclassdesc*,porigin,pclassdesc) : pclassdesc*\n'
 'def $esp_class_replace(eps,porigin,pclassdesc) = eps\n'
 'def $esp_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_new :: '
 'pclassdesc*\n'
 '  -- if pclassdesc_old.ORIGIN = porigin\n'
 'def $esp_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_old :: '
 '$esp_class_replace(pclassdesc*,porigin,pclassdesc_new)\n'
 '  -- if pclassdesc_old.ORIGIN =/= porigin\n'
 'dec $esp_stage(pstate,nat) : bool\n'
 'def $esp_stage(S,0) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (ASSIGN_ARRAY pbase 17 false) :: ptask*\n'
 '  -- if S.RESULT = KNOWN pvalue\n'
 '  -- if $string_bytes(pvalue) = ($ptascii("20"))\n'
 'def $esp_stage(S,1) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_SET_TARGET ppropertyhook\n'
 '  -- if S.TODO = (ASSIGN_ARRAY pbase 6 false) :: ptask*\n'
 '  -- if S.RESULT = KNOWN (PINT 33)\n'
 'def $esp_stage(S,2) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (PROPERTY_SET_RESULT ppropertyhook pvalue) :: ptask*\n'
 '  -- if $string_bytes(pvalue) = ($ptascii("20"))\n'
 'def $esp_stage(S,3) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_SET_TARGET ppropertyhook\n'
 '  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: ptask*\n'
 '  -- if $lookup(S.ENV,$ptascii("incoming")) = (n_cell)\n'
 '  -- if S.STORE[n_cell] = DEFINED (PARRAY n_array)\n'
 'def $esp_stage(S,4) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) 26) :: (DIM_FETCH 26) :: '
 'ptask*\n'
 '  -- if $base64(text_name) = $ptascii("value")\n'
 'def $esp_stage(S,n) = false -- otherwise\n'
 'dec $esp_seek(pstate,nat,nat) : pstate\n'
 'def $esp_seek(S,n_stage,n) = S\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if $esp_stage(S,n_stage) \\/ n = 0\n'
 'def $esp_seek(S,n_stage,n) = $esp_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if ~$esp_stage(S,n_stage) /\\ $(n > 0)\n'
 'def $esp_seek(S,n_stage,n) = $esp_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
 '  -- if $throwable_pending(S.COMPLETION) /\\ $(n > 0)\n'
 'def $esp_seek(S,n_stage,n) = S -- otherwise\n'
 'dec $esp_after(pstate,pstate) : pstate\n'
 'def $esp_after(S,S_next) = '
 '$gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))\n'
 'dec $esp_guard(pstate) : bool\n'
 'def $esp_guard(S) = ($call_descriptors_valid(S) /\\ $declaration_history_valid(S) /\\ '
 '$property_state_valid(S) /\\ $heap_valid($heap_prune($heap_graph(S))))\n')

COMMON = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("ExplicitSetParent73"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ExplicitSetChild73"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 'pclassdesc_parent.KIND = "class" /\\ pclassdesc_parent.PARENT = eps /\\ ~pclassdesc_parent.READONLY /\\ '
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ pclassdesc_child.PROPERTIES = eps',
 '$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_parent)',
 'ppropertydesc = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc.ORIGIN = porigin_property',
 'ppropertydesc.NAME = $ptascii("value") /\\ ppropertydesc.KEY = ppropertydesc.NAME /\\ ppropertydesc.TYPE = '
 '([(PTBRANCH ([PTBUILTIN "int"]))]) /\\ ppropertydesc.VISIBILITY = PROPERTY_PUBLIC /\\ '
 'ppropertydesc.SETVISIBILITY = eps',
 '$property_default_state(S,ppropertydesc) = (PROP_VALUE (DIRECT (PINT 10))) /\\ ~ppropertydesc.STATIC /\\ '
 '~ppropertydesc.READONLY /\\ ~ppropertydesc.FINAL',
 '$property_layout(S,porigin_parent,|S.CLASSES|) = [ppropertydesc] /\\ '
 '$property_layout(S,porigin_child,|S.CLASSES|) = [ppropertydesc]',
 '$property_set_origin(S,ppropertydesc) = (porigin_hook)',
 '$property_hook_origin(S,ppropertydesc) = eps /\\ $property_hook_effective_origin(S,ppropertydesc) = eps /\\ '
 '~$property_hook_virtual(S,ppropertydesc)',
 '$function_at(S.FUNCTIONS,porigin_hook) = (pfunction_hook)',
 'pssignature_hook = pfunction_hook.SIGNATURE',
 'pssignature_hook.PARAMETERS = [psparam_incoming]',
 'pssignature_hook.RETURNS = ([(PTBRANCH ([PTBUILTIN "void"]))]) /\\ ~pssignature_hook.BYREF',
 'psparam_incoming.NAME = $ptascii("incoming") /\\ ~psparam_incoming.BYREF /\\ ~psparam_incoming.VARIADIC /\\ '
 'psparam_incoming.REQUIRED /\\ psparam_incoming.DEFAULT = PSNONE',
 '|psparam_incoming.TYPE| = 2 /\\ "int" <- $ptmasks(psparam_incoming.TYPE) /\\ "string" <- '
 '$ptmasks(psparam_incoming.TYPE)',
 'pfunction_hook.NAME = pclassdesc_parent.NAME ++ $ptascii("::$value::set") /\\ pfunction_hook.DEFAULTS = eps '
 '/\\ ~pfunction_hook.EARLY /\\ pfunction_hook.LINE = 4 /\\ pfunction_hook.ENDLINE = 7',
 'S.FUNCTIONS = [pfunction_hook] /\\ $ptascii("incoming") <- pfunction_hook.CVS /\\ ~($ptascii("value") <- '
 'pfunction_hook.CVS)',
 '$method_named(pclassdesc_parent.METHODS,$property_set_name(ppropertydesc.NAME)) = eps',
 'porigin_hook = PORIGIN n_source pcpath_hook',
 'pfunction_hook.BODY = pcpath_hook ++ [PCFIELD 5]',
 '$origin_node(S.SOURCES,porigin_hook) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook '
 'phpType11_hook phpType16_hook phpType39_hook metadata_hook)',
 'phpType14_hook = SEQUENCE eps /\\ phpType24_hook = INTEGER 0 /\\ phpType4_hook = BOOLEAN false',
 'phpType11_hook = NIdentifier (BYTES text_set) metadata_set',
 '$base64(text_set) = $ptascii("set") /\\ $hook_body_backed(phpType39_hook,ppropertydesc.NAME)',
 'phpType16_hook = SEQUENCE ([phpType17_parameter])',
 'phpType17_parameter = NParam (SEQUENCE eps) (INTEGER 0) phpType18_parameter (BOOLEAN false) (BOOLEAN false) '
 '(NExprVariable (BYTES text_incoming) metadata_variable) ABSENT (SEQUENCE eps) metadata_parameter',
 '$base64(text_incoming) = $ptascii("incoming") /\\ phpType18_parameter =/= ABSENT /\\ '
 '$psline(metadata_parameter) = 4',
 '$origin_node(S.SOURCES,PORIGIN n_source (pcpath_hook ++ [PCFIELD 4,PCINDEX 0])) = (phpType17_parameter)',
 '$property_set_parameters(phpType16_hook) /\\ phpType16_hook =/= SEQUENCE eps',
 'pcpath_group = pcpath_hook[0:$nabs($(|pcpath_hook| - 2))]',
 '$origin_node(S.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty phpType14_group phpType24_group '
 'phpType18_group phpType56_group (SEQUENCE ([NPropertyHook phpType14_hook phpType24_hook phpType4_hook '
 'phpType11_hook phpType16_hook phpType39_hook metadata_hook])) metadata_group)',
 'ptcontext_hook = {NAMESPACE pfunction_hook.ENV.NAMESPACE, IMPORTS pfunction_hook.ENV.CLASSES, SCOPE PTKNOWN '
 'pclassdesc_parent.NAME eps, POSITION PTRETURN, OWNER pclassdesc_parent.NAME, MEMBER '
 '$property_set_name(ppropertydesc.NAME), FILE $call_sourcefile(S.FILES,porigin_hook), LINE 4}',
 '$ptype_normalize(phpType18_group,ptcontext_hook[.POSITION = PTPROPERTY][.MEMBER = ppropertydesc.NAME][.LINE '
 '= $psline(metadata_group)]) = PTOK ptbranch_property* eps',
 'ptbranch_property* = ppropertydesc.TYPE',
 '$ptype_normalize(phpType18_parameter,ptcontext_hook[.POSITION = PTPARAMETER]) = PTOK ptbranch_parameter* eps',
 'ptbranch_parameter* = psparam_incoming.TYPE',
 '$property_set_explicit_signature(phpType16_hook,ptcontext_hook) = (pssignature_hook) /\\ '
 '$property_set_signature_at(S,ppropertydesc) = (pssignature_hook)',
 '$property_set_variance(ppropertydesc.TYPE,psparam_incoming.TYPE,pclassdesc_parent.NAME,pclassdesc_parent.FINAL) '
 '= PVCOMPATIBLE',
 '$code_at(S.CODE,n_source) = (pcode_source)',
 '$code_expression(pcode_source.EXPRESSIONS,pcpath_hook ++ [PCFIELD 4,PCINDEX 0]) = ((4,false))',
 '$property_declaring_class(S.CLASSES,porigin_property) = (porigin_parent)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("offset")) = (pmethoddesc_parent_offset)',
 '$method_named(pclassdesc_child.METHODS,$ptascii("offset")) = (pmethoddesc_child_offset)',
 'pmethoddesc_parent_offset.OWNER = porigin_parent /\\ pmethoddesc_parent_offset.VISIBILITY = PROPERTY_PRIVATE '
 '/\\ pmethoddesc_child_offset.OWNER = porigin_child /\\ pmethoddesc_child_offset.VISIBILITY = '
 'PROPERTY_PRIVATE',
 'S.OBJECTS[n_child] = INSTANCE porigin_child /\\ (HOBJECT n_child) <- S.ALLOCATIONS',
 '$property_effective_desc(S,n_child,$ptascii("value")) = (ppropertydesc) /\\ '
 '$property_hook_instance(S,n_child) /\\ $property_hook_declared(S,n_child,$ptascii("value"))',
 '~$property_hook_read_needed(S,n_child,$ptascii("value")) /\\ $property_resolve(S,n_child,$ptascii("value")) '
 '= PROPERTY_ACCESS ppropertydesc.KEY',
 '$esp_guard(S)']

RECEIVE = ['$esp_stage(S,0)',
 '$lookup(S.ENV,$ptascii("child")) = (n_child_cell)',
 'S.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
 'S.RESULT = KNOWN pvalue_input',
 '$string_bytes(pvalue_input) = ($ptascii("20"))',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ExplicitSetParent73"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ExplicitSetChild73"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 'pclassdesc_parent.KIND = "class" /\\ pclassdesc_parent.PARENT = eps /\\ ~pclassdesc_parent.READONLY /\\ '
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ pclassdesc_child.PROPERTIES = eps',
 '$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_parent)',
 'ppropertydesc = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc.ORIGIN = porigin_property',
 'ppropertydesc.NAME = $ptascii("value") /\\ ppropertydesc.KEY = ppropertydesc.NAME /\\ ppropertydesc.TYPE = '
 '([(PTBRANCH ([PTBUILTIN "int"]))]) /\\ ppropertydesc.VISIBILITY = PROPERTY_PUBLIC /\\ '
 'ppropertydesc.SETVISIBILITY = eps',
 '$property_default_state(S,ppropertydesc) = (PROP_VALUE (DIRECT (PINT 10))) /\\ ~ppropertydesc.STATIC /\\ '
 '~ppropertydesc.READONLY /\\ ~ppropertydesc.FINAL',
 '$property_layout(S,porigin_parent,|S.CLASSES|) = [ppropertydesc] /\\ '
 '$property_layout(S,porigin_child,|S.CLASSES|) = [ppropertydesc]',
 '$property_set_origin(S,ppropertydesc) = (porigin_hook)',
 '$property_hook_origin(S,ppropertydesc) = eps /\\ $property_hook_effective_origin(S,ppropertydesc) = eps /\\ '
 '~$property_hook_virtual(S,ppropertydesc)',
 '$function_at(S.FUNCTIONS,porigin_hook) = (pfunction_hook)',
 'pssignature_hook = pfunction_hook.SIGNATURE',
 'pssignature_hook.PARAMETERS = [psparam_incoming]',
 'pssignature_hook.RETURNS = ([(PTBRANCH ([PTBUILTIN "void"]))]) /\\ ~pssignature_hook.BYREF',
 'psparam_incoming.NAME = $ptascii("incoming") /\\ ~psparam_incoming.BYREF /\\ ~psparam_incoming.VARIADIC /\\ '
 'psparam_incoming.REQUIRED /\\ psparam_incoming.DEFAULT = PSNONE',
 '|psparam_incoming.TYPE| = 2 /\\ "int" <- $ptmasks(psparam_incoming.TYPE) /\\ "string" <- '
 '$ptmasks(psparam_incoming.TYPE)',
 'pfunction_hook.NAME = pclassdesc_parent.NAME ++ $ptascii("::$value::set") /\\ pfunction_hook.DEFAULTS = eps '
 '/\\ ~pfunction_hook.EARLY /\\ pfunction_hook.LINE = 4 /\\ pfunction_hook.ENDLINE = 7',
 'S.FUNCTIONS = [pfunction_hook] /\\ $ptascii("incoming") <- pfunction_hook.CVS /\\ ~($ptascii("value") <- '
 'pfunction_hook.CVS)',
 '$method_named(pclassdesc_parent.METHODS,$property_set_name(ppropertydesc.NAME)) = eps',
 'porigin_hook = PORIGIN n_source pcpath_hook',
 'pfunction_hook.BODY = pcpath_hook ++ [PCFIELD 5]',
 '$origin_node(S.SOURCES,porigin_hook) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook '
 'phpType11_hook phpType16_hook phpType39_hook metadata_hook)',
 'phpType14_hook = SEQUENCE eps /\\ phpType24_hook = INTEGER 0 /\\ phpType4_hook = BOOLEAN false',
 'phpType11_hook = NIdentifier (BYTES text_set) metadata_set',
 '$base64(text_set) = $ptascii("set") /\\ $hook_body_backed(phpType39_hook,ppropertydesc.NAME)',
 'phpType16_hook = SEQUENCE ([phpType17_parameter])',
 'phpType17_parameter = NParam (SEQUENCE eps) (INTEGER 0) phpType18_parameter (BOOLEAN false) (BOOLEAN false) '
 '(NExprVariable (BYTES text_incoming) metadata_variable) ABSENT (SEQUENCE eps) metadata_parameter',
 '$base64(text_incoming) = $ptascii("incoming") /\\ phpType18_parameter =/= ABSENT /\\ '
 '$psline(metadata_parameter) = 4',
 '$origin_node(S.SOURCES,PORIGIN n_source (pcpath_hook ++ [PCFIELD 4,PCINDEX 0])) = (phpType17_parameter)',
 '$property_set_parameters(phpType16_hook) /\\ phpType16_hook =/= SEQUENCE eps',
 'pcpath_group = pcpath_hook[0:$nabs($(|pcpath_hook| - 2))]',
 '$origin_node(S.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty phpType14_group phpType24_group '
 'phpType18_group phpType56_group (SEQUENCE ([NPropertyHook phpType14_hook phpType24_hook phpType4_hook '
 'phpType11_hook phpType16_hook phpType39_hook metadata_hook])) metadata_group)',
 'ptcontext_hook = {NAMESPACE pfunction_hook.ENV.NAMESPACE, IMPORTS pfunction_hook.ENV.CLASSES, SCOPE PTKNOWN '
 'pclassdesc_parent.NAME eps, POSITION PTRETURN, OWNER pclassdesc_parent.NAME, MEMBER '
 '$property_set_name(ppropertydesc.NAME), FILE $call_sourcefile(S.FILES,porigin_hook), LINE 4}',
 '$ptype_normalize(phpType18_group,ptcontext_hook[.POSITION = PTPROPERTY][.MEMBER = ppropertydesc.NAME][.LINE '
 '= $psline(metadata_group)]) = PTOK ptbranch_property* eps',
 'ptbranch_property* = ppropertydesc.TYPE',
 '$ptype_normalize(phpType18_parameter,ptcontext_hook[.POSITION = PTPARAMETER]) = PTOK ptbranch_parameter* eps',
 'ptbranch_parameter* = psparam_incoming.TYPE',
 '$property_set_explicit_signature(phpType16_hook,ptcontext_hook) = (pssignature_hook) /\\ '
 '$property_set_signature_at(S,ppropertydesc) = (pssignature_hook)',
 '$property_set_variance(ppropertydesc.TYPE,psparam_incoming.TYPE,pclassdesc_parent.NAME,pclassdesc_parent.FINAL) '
 '= PVCOMPATIBLE',
 '$code_at(S.CODE,n_source) = (pcode_source)',
 '$code_expression(pcode_source.EXPRESSIONS,pcpath_hook ++ [PCFIELD 4,PCINDEX 0]) = ((4,false))',
 '$property_declaring_class(S.CLASSES,porigin_property) = (porigin_parent)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("offset")) = (pmethoddesc_parent_offset)',
 '$method_named(pclassdesc_child.METHODS,$ptascii("offset")) = (pmethoddesc_child_offset)',
 'pmethoddesc_parent_offset.OWNER = porigin_parent /\\ pmethoddesc_parent_offset.VISIBILITY = PROPERTY_PRIVATE '
 '/\\ pmethoddesc_child_offset.OWNER = porigin_child /\\ pmethoddesc_child_offset.VISIBILITY = '
 'PROPERTY_PRIVATE',
 'S.OBJECTS[n_child] = INSTANCE porigin_child /\\ (HOBJECT n_child) <- S.ALLOCATIONS',
 '$property_effective_desc(S,n_child,$ptascii("value")) = (ppropertydesc) /\\ '
 '$property_hook_instance(S,n_child) /\\ $property_hook_declared(S,n_child,$ptascii("value"))',
 '~$property_hook_read_needed(S,n_child,$ptascii("value")) /\\ $property_resolve(S,n_child,$ptascii("value")) '
 '= PROPERTY_ACCESS ppropertydesc.KEY',
 '$esp_guard(S)',
 'S.ORIGIN = (porigin_site)',
 '$property_set_plan(S) = (ppropertyhook)',
 'ppropertyhook = {SITE porigin_site, OBJECT n_child, PROPERTY porigin_property, HOOK porigin_hook, LINE 17}',
 '$property_set_valid(S,ppropertyhook) /\\ $property_set_function(S,ppropertyhook) = (pfunction_hook) /\\ '
 '$property_set_pending(S)',
 '$objectprops_at(S.OBJECTPROPS,n_child) = ([{DECL (porigin_property), NAME ppropertydesc.KEY, STATE '
 'PROP_VALUE (DIRECT (PINT 10))}])',
 'PhpStep: S ~> S_call_raw',
 'S_call = $esp_after(S,S_call_raw)',
 'S_call.TODO = (CALL_ARGS (PROPERTY_SET_TARGET ppropertyhook) eps 1 ([KNOWN pvalue_input]) (porigin_site) 17) '
 ':: (PROPERTY_SET_RESULT ppropertyhook pvalue_input) :: ptask_caller*',
 '$property_set_pending_call(S_call,ppropertyhook) /\\ $call_task_valid(S_call,CALL_ARGS (PROPERTY_SET_TARGET '
 'ppropertyhook) eps 1 ([KNOWN pvalue_input]) (porigin_site) 17)',
 'S_call.CURRENT = eps /\\ S_call.EVENTS = S.EVENTS /\\ S_call.OBJECTPROPS = S.OBJECTPROPS /\\ '
 '$esp_guard(S_call)',
 'PhpStep: S_call ~> S_entered_raw',
 'S_entered = $esp_after(S_call,S_entered_raw)',
 'S_entered.CURRENT = (pcallcontext_set)',
 'pcallcontext_set.TARGET = PROPERTY_SET_TARGET ppropertyhook /\\ pcallcontext_set.FUNCTION = porigin_hook /\\ '
 'pcallcontext_set.ARGC = 1 /\\ pcallcontext_set.CALLSITE = (porigin_site) /\\ pcallcontext_set.LINE = 17',
 'pcallcontext_set.LEXICAL_CLASS = (porigin_parent) /\\ pcallcontext_set.CALLED_CLASS = (porigin_child) /\\ '
 'pcallcontext_set.RECEIVER = (n_child) /\\ pcallcontext_set.PARAMS = [$ptascii("incoming")]',
 'S_entered.TODO = [TYPE_RECEIVE porigin_hook 0] /\\ S_entered.ORIGIN = (porigin_hook)',
 '$lookup(S_entered.ENV,$ptascii("incoming")) = (n_incoming_cell)',
 'S_entered.STORE[n_incoming_cell] = DEFINED pvalue_input /\\ $lookup(S_entered.ENV,$ptascii("value")) = eps',
 '$property_set_explicit_origin(S_entered,porigin_hook)',
 '$default_parameter_origin(S_entered,porigin_hook,0) = PORIGIN n_source (pcpath_hook ++ [PCFIELD 4,PCINDEX '
 '0])',
 '$default_parameter_line(S_entered,porigin_hook,0) = 4 /\\ $typed_receive_valid(S_entered,porigin_hook,0) /\\ '
 '$named_receives_ready(S_entered,pfunction_hook)',
 '$typed_parameter_conversion(S_entered,psparam_incoming,pvalue_input) = TYPEVALUE pvalue_input',
 '$property_set_context_valid(S_entered,pcallcontext_set) /\\ $call_receiver_roots(pcallcontext_set) = eps /\\ '
 '$esp_guard(S_entered)',
 'PhpStep: S_entered ~> S_received_raw',
 'S_received = $esp_after(S_entered,S_received_raw)',
 'S_received.COMPLETION = NORMAL /\\ S_received.CURRENT = S_entered.CURRENT /\\ S_received.FRAMES = '
 'S_entered.FRAMES /\\ S_received.EVENTS = S.EVENTS /\\ S_received.OBJECTPROPS = S.OBJECTPROPS',
 'S_received.STORE[n_incoming_cell] = DEFINED pvalue_input',
 'phpType39_hook = SEQUENCE statement_body*',
 'S_received.TODO = $statement_tasks(statement_body*,(PORIGIN n_source pfunction_hook.BODY),0) ++ '
 '[$function_fallthrough(S_received,pfunction_hook)]',
 'S_received.TODO = $function_body_tasks(S_received,pfunction_hook) /\\ S_received.TODO =/= eps /\\ '
 '$esp_guard(S_received)',
 'S_backing_found = $esp_seek(S_received,1,1000)',
 'S_backing_found.COMPLETION = NORMAL \\/ S_backing_found.COMPLETION = BUDGET',
 'S_backing = S_backing_found[.COMPLETION = NORMAL]',
 '$esp_stage(S_backing,1) /\\ S_backing.CURRENT = (pcallcontext_set)',
 'S_backing.STORE[n_incoming_cell] = DEFINED pvalue_input /\\ '
 '$method_selected_scope(S_backing,n_child,$ptascii("offset"),(porigin_parent)) = (pmethoddesc_parent_offset)',
 '$property_set_backing(S_backing,n_child,ppropertydesc) /\\ '
 '~$property_set_needed(S_backing,n_child,$ptascii("value")) /\\ '
 '$property_set_context_valid(S_backing,pcallcontext_set)',
 'S_backing.TODO = (ASSIGN_ARRAY pbase_write 6 false) :: ptask_write*',
 'S_backing.RESULT = KNOWN (PINT 33) /\\ $call_task_valid(S_backing,ASSIGN_ARRAY pbase_write 6 false)',
 '$objectprops_at(S_backing.OBJECTPROPS,n_child) = ([{DECL (porigin_property), NAME ppropertydesc.KEY, STATE '
 'PROP_VALUE (DIRECT (PINT 10))}])',
 'PhpStep: S_backing ~> S_written_raw',
 'S_written = $esp_after(S_backing,S_written_raw)',
 'S_written.COMPLETION = NORMAL /\\ S_written.RESULT = KNOWN (PINT 33) /\\ S_written.CURRENT = '
 'S_backing.CURRENT /\\ S_written.FRAMES = S_backing.FRAMES',
 '$objectprops_at(S_written.OBJECTPROPS,n_child) = ([{DECL (porigin_property), NAME ppropertydesc.KEY, STATE '
 'PROP_VALUE (DIRECT (PINT 33))}])',
 '$esp_guard(S_written)',
 'S_return_found = $esp_seek(S_written,2,1000)',
 'S_return_found.COMPLETION = NORMAL \\/ S_return_found.COMPLETION = BUDGET',
 'S_return = S_return_found[.COMPLETION = NORMAL]',
 '$esp_stage(S_return,2)',
 'S_return.TODO = (PROPERTY_SET_RESULT ppropertyhook pvalue_input) :: ptask_return*',
 'S_return.RESULT = KNOWN PNULL /\\ S_return.CURRENT = eps /\\ S_return.FRAMES = eps /\\ S_return.ORIGIN = '
 '(ppropertyhook.SITE)',
 '$objectprops_at(S_return.OBJECTPROPS,n_child) = ([{DECL (porigin_property), NAME ppropertydesc.KEY, STATE '
 'PROP_VALUE (DIRECT (PINT 33))}])',
 '$call_task_valid(S_return,PROPERTY_SET_RESULT ppropertyhook pvalue_input) /\\ $esp_guard(S_return)',
 'PhpStep: S_return ~> S_result_raw',
 'S_result = $esp_after(S_return,S_result_raw)',
 'S_result.COMPLETION = NORMAL /\\ S_result.RESULT = KNOWN pvalue_input /\\ S_result.BASE = BASE_VALUE (KNOWN '
 'PNULL) /\\ S_result.TODO = ptask_return* /\\ S_result.OBJECTPROPS = S_return.OBJECTPROPS',
 '$string_bytes(pvalue_input) = ($ptascii("20")) /\\ $esp_guard(S_result)']

ERROR = ['$esp_stage(S,3)',
 'S.CURRENT = (pcallcontext_set)',
 'pcallcontext_set.RECEIVER = (n_child)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ExplicitSetParent73"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ExplicitSetChild73"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 'pclassdesc_parent.KIND = "class" /\\ pclassdesc_parent.PARENT = eps /\\ ~pclassdesc_parent.READONLY /\\ '
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ pclassdesc_child.PROPERTIES = eps',
 '$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_parent)',
 'ppropertydesc = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc.ORIGIN = porigin_property',
 'ppropertydesc.NAME = $ptascii("value") /\\ ppropertydesc.KEY = ppropertydesc.NAME /\\ ppropertydesc.TYPE = '
 '([(PTBRANCH ([PTBUILTIN "int"]))]) /\\ ppropertydesc.VISIBILITY = PROPERTY_PUBLIC /\\ '
 'ppropertydesc.SETVISIBILITY = eps',
 '$property_default_state(S,ppropertydesc) = (PROP_VALUE (DIRECT (PINT 10))) /\\ ~ppropertydesc.STATIC /\\ '
 '~ppropertydesc.READONLY /\\ ~ppropertydesc.FINAL',
 '$property_layout(S,porigin_parent,|S.CLASSES|) = [ppropertydesc] /\\ '
 '$property_layout(S,porigin_child,|S.CLASSES|) = [ppropertydesc]',
 '$property_set_origin(S,ppropertydesc) = (porigin_hook)',
 '$property_hook_origin(S,ppropertydesc) = eps /\\ $property_hook_effective_origin(S,ppropertydesc) = eps /\\ '
 '~$property_hook_virtual(S,ppropertydesc)',
 '$function_at(S.FUNCTIONS,porigin_hook) = (pfunction_hook)',
 'pssignature_hook = pfunction_hook.SIGNATURE',
 'pssignature_hook.PARAMETERS = [psparam_incoming]',
 'pssignature_hook.RETURNS = ([(PTBRANCH ([PTBUILTIN "void"]))]) /\\ ~pssignature_hook.BYREF',
 'psparam_incoming.NAME = $ptascii("incoming") /\\ ~psparam_incoming.BYREF /\\ ~psparam_incoming.VARIADIC /\\ '
 'psparam_incoming.REQUIRED /\\ psparam_incoming.DEFAULT = PSNONE',
 '|psparam_incoming.TYPE| = 2 /\\ "int" <- $ptmasks(psparam_incoming.TYPE) /\\ "string" <- '
 '$ptmasks(psparam_incoming.TYPE)',
 'pfunction_hook.NAME = pclassdesc_parent.NAME ++ $ptascii("::$value::set") /\\ pfunction_hook.DEFAULTS = eps '
 '/\\ ~pfunction_hook.EARLY /\\ pfunction_hook.LINE = 4 /\\ pfunction_hook.ENDLINE = 7',
 'S.FUNCTIONS = [pfunction_hook] /\\ $ptascii("incoming") <- pfunction_hook.CVS /\\ ~($ptascii("value") <- '
 'pfunction_hook.CVS)',
 '$method_named(pclassdesc_parent.METHODS,$property_set_name(ppropertydesc.NAME)) = eps',
 'porigin_hook = PORIGIN n_source pcpath_hook',
 'pfunction_hook.BODY = pcpath_hook ++ [PCFIELD 5]',
 '$origin_node(S.SOURCES,porigin_hook) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook '
 'phpType11_hook phpType16_hook phpType39_hook metadata_hook)',
 'phpType14_hook = SEQUENCE eps /\\ phpType24_hook = INTEGER 0 /\\ phpType4_hook = BOOLEAN false',
 'phpType11_hook = NIdentifier (BYTES text_set) metadata_set',
 '$base64(text_set) = $ptascii("set") /\\ $hook_body_backed(phpType39_hook,ppropertydesc.NAME)',
 'phpType16_hook = SEQUENCE ([phpType17_parameter])',
 'phpType17_parameter = NParam (SEQUENCE eps) (INTEGER 0) phpType18_parameter (BOOLEAN false) (BOOLEAN false) '
 '(NExprVariable (BYTES text_incoming) metadata_variable) ABSENT (SEQUENCE eps) metadata_parameter',
 '$base64(text_incoming) = $ptascii("incoming") /\\ phpType18_parameter =/= ABSENT /\\ '
 '$psline(metadata_parameter) = 4',
 '$origin_node(S.SOURCES,PORIGIN n_source (pcpath_hook ++ [PCFIELD 4,PCINDEX 0])) = (phpType17_parameter)',
 '$property_set_parameters(phpType16_hook) /\\ phpType16_hook =/= SEQUENCE eps',
 'pcpath_group = pcpath_hook[0:$nabs($(|pcpath_hook| - 2))]',
 '$origin_node(S.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty phpType14_group phpType24_group '
 'phpType18_group phpType56_group (SEQUENCE ([NPropertyHook phpType14_hook phpType24_hook phpType4_hook '
 'phpType11_hook phpType16_hook phpType39_hook metadata_hook])) metadata_group)',
 'ptcontext_hook = {NAMESPACE pfunction_hook.ENV.NAMESPACE, IMPORTS pfunction_hook.ENV.CLASSES, SCOPE PTKNOWN '
 'pclassdesc_parent.NAME eps, POSITION PTRETURN, OWNER pclassdesc_parent.NAME, MEMBER '
 '$property_set_name(ppropertydesc.NAME), FILE $call_sourcefile(S.FILES,porigin_hook), LINE 4}',
 '$ptype_normalize(phpType18_group,ptcontext_hook[.POSITION = PTPROPERTY][.MEMBER = ppropertydesc.NAME][.LINE '
 '= $psline(metadata_group)]) = PTOK ptbranch_property* eps',
 'ptbranch_property* = ppropertydesc.TYPE',
 '$ptype_normalize(phpType18_parameter,ptcontext_hook[.POSITION = PTPARAMETER]) = PTOK ptbranch_parameter* eps',
 'ptbranch_parameter* = psparam_incoming.TYPE',
 '$property_set_explicit_signature(phpType16_hook,ptcontext_hook) = (pssignature_hook) /\\ '
 '$property_set_signature_at(S,ppropertydesc) = (pssignature_hook)',
 '$property_set_variance(ppropertydesc.TYPE,psparam_incoming.TYPE,pclassdesc_parent.NAME,pclassdesc_parent.FINAL) '
 '= PVCOMPATIBLE',
 '$code_at(S.CODE,n_source) = (pcode_source)',
 '$code_expression(pcode_source.EXPRESSIONS,pcpath_hook ++ [PCFIELD 4,PCINDEX 0]) = ((4,false))',
 '$property_declaring_class(S.CLASSES,porigin_property) = (porigin_parent)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("offset")) = (pmethoddesc_parent_offset)',
 '$method_named(pclassdesc_child.METHODS,$ptascii("offset")) = (pmethoddesc_child_offset)',
 'pmethoddesc_parent_offset.OWNER = porigin_parent /\\ pmethoddesc_parent_offset.VISIBILITY = PROPERTY_PRIVATE '
 '/\\ pmethoddesc_child_offset.OWNER = porigin_child /\\ pmethoddesc_child_offset.VISIBILITY = '
 'PROPERTY_PRIVATE',
 'S.OBJECTS[n_child] = INSTANCE porigin_child /\\ (HOBJECT n_child) <- S.ALLOCATIONS',
 '$property_effective_desc(S,n_child,$ptascii("value")) = (ppropertydesc) /\\ '
 '$property_hook_instance(S,n_child) /\\ $property_hook_declared(S,n_child,$ptascii("value"))',
 '~$property_hook_read_needed(S,n_child,$ptascii("value")) /\\ $property_resolve(S,n_child,$ptascii("value")) '
 '= PROPERTY_ACCESS ppropertydesc.KEY',
 '$esp_guard(S)',
 'pcallcontext_set.TARGET = PROPERTY_SET_TARGET ppropertyhook',
 'ppropertyhook.OBJECT = n_child /\\ ppropertyhook.PROPERTY = porigin_property /\\ ppropertyhook.HOOK = '
 'porigin_hook /\\ ppropertyhook.LINE = 21',
 'pcallcontext_set.FUNCTION = porigin_hook /\\ pcallcontext_set.LEXICAL_CLASS = (porigin_parent) /\\ '
 'pcallcontext_set.CALLED_CLASS = (porigin_child) /\\ pcallcontext_set.ARGC = 1 /\\ pcallcontext_set.CALLSITE '
 '= (ppropertyhook.SITE) /\\ pcallcontext_set.LINE = 21',
 'S.TODO = [TYPE_RECEIVE porigin_hook 0] /\\ S.ORIGIN = (porigin_hook)',
 '$lookup(S.ENV,$ptascii("incoming")) = (n_incoming_cell)',
 'S.STORE[n_incoming_cell] = DEFINED (PARRAY n_array)',
 'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
 '$property_set_context_valid(S,pcallcontext_set) /\\ $typed_receive_valid(S,porigin_hook,0) /\\ '
 '$named_receives_ready(S,pfunction_hook) /\\ $default_parameter_line(S,porigin_hook,0) = 4',
 '$default_parameter_origin(S,porigin_hook,0) = PORIGIN n_source (pcpath_hook ++ [PCFIELD 4,PCINDEX 0]) /\\ '
 '$property_set_explicit_origin(S,porigin_hook)',
 '$objectprops_at(S.OBJECTPROPS,n_child) = ([{DECL (porigin_property), NAME ppropertydesc.KEY, STATE '
 'PROP_VALUE (DIRECT (PINT 33))}])',
 'ptbytes_message = pfunction_hook.NAME ++ $ptascii("(): Argument #1 ($incoming) must be of type string|int, '
 'array given, called in ") ++ $call_sourcefile(S.FILES,ppropertyhook.SITE) ++ $ptascii(" on line 21")',
 '$typed_parameter_conversion(S,pfunction_hook.SIGNATURE.PARAMETERS[0],PARRAY n_array) = TYPEREJECT',
 'PhpStep: S ~> S_error_raw',
 'S_error_raw.COMPLETION = THROWN "TypeError" ptbytes_message 4 /\\ S_error_raw.EVENTS = S.EVENTS /\\ '
 'S_error_raw.OBJECTPROPS = S.OBJECTPROPS /\\ S_error_raw.CURRENT = S.CURRENT /\\ S_error_raw.FRAMES = '
 'S.FRAMES',
 'S_error = $esp_after(S,S_error_raw)',
 'S_error.COMPLETION = THROWING n_error',
 '$object_name(S_error,n_error) = $ptascii("TypeError") /\\ $throwable_field(S_error,n_error,"message") = '
 'PSTRING ptbytes_message',
 '$objectprops_at(S_error.OBJECTPROPS,n_child) = ([{DECL (porigin_property), NAME ppropertydesc.KEY, STATE '
 'PROP_VALUE (DIRECT (PINT 33))}])',
 '$esp_guard(S_error)',
 'S_final_found = $esp_seek(S_error,4,1000)',
 'S_final_found.COMPLETION = NORMAL \\/ S_final_found.COMPLETION = BUDGET',
 'S_final = S_final_found[.COMPLETION = NORMAL]',
 '$esp_stage(S_final,4)',
 'S_final.CURRENT = eps /\\ S_final.FRAMES = eps /\\ $objectprops_at(S_final.OBJECTPROPS,n_child) = ([{DECL '
 '(porigin_property), NAME ppropertydesc.KEY, STATE PROP_VALUE (DIRECT (PINT 33))}])',
 '~$property_hook_pending(S_final) /\\ ~$property_hook_read_needed(S_final,n_child,$ptascii("value")) /\\ '
 '$esp_guard(S_final)',
 'PhpStep: S_final ~> S_fetch_raw',
 'S_fetch = $esp_after(S_final,S_fetch_raw)',
 'S_fetch.COMPLETION = NORMAL /\\ S_fetch.BASE = BASE_PROPERTY (POBJECT n_child) ppropertydesc.KEY /\\ '
 'S_fetch.CURRENT = eps /\\ S_fetch.FRAMES = eps',
 'PhpStep: S_fetch ~> S_read_raw',
 'S_read = $esp_after(S_fetch,S_read_raw)',
 'S_read.COMPLETION = NORMAL /\\ S_read.RESULT = KNOWN (PINT 33) /\\ S_read.CURRENT = eps /\\ S_read.FRAMES = '
 'eps /\\ S_read.OBJECTPROPS = S_final.OBJECTPROPS /\\ $esp_guard(S_read)']

DERIVED = ['~$property_set_explicit_origin(S_entered[.CURRENT = eps],porigin_hook)',
 '$property_set_signature_at(S,ppropertydesc[.TYPE = eps]) = eps',
 'ppropertydesc_wrong_type = ppropertydesc[.TYPE = ([(PTBRANCH ([PTBUILTIN "string"]))])]',
 'S_wrong_type = S[.CLASSES = $esp_class_replace(S.CLASSES,porigin_parent,pclassdesc_parent[.PROPERTIES = '
 '([ppropertydesc_wrong_type])])]',
 '$property_set_origin(S_wrong_type,ppropertydesc_wrong_type) = (porigin_hook)',
 '$property_set_variance(ppropertydesc_wrong_type.TYPE,psparam_incoming.TYPE,pclassdesc_parent.NAME,pclassdesc_parent.FINAL) '
 '= PVCOMPATIBLE',
 '$property_set_signature_at(S_wrong_type,ppropertydesc_wrong_type) = eps /\\ '
 '$property_set_function(S_wrong_type,ppropertyhook) = eps',
 '$source_unit(S.SOURCES,n_source) = (pcunit_source)',
 'S.SOURCES = [pcunit_source]',
 'phpType17_wrong_leaf = NParam (SEQUENCE eps) (INTEGER 0) phpType18_parameter (BOOLEAN false) (BOOLEAN false) '
 '(NExprVariable (BYTES "d3Jvbmc=") metadata_variable) ABSENT (SEQUENCE eps) metadata_parameter',
 'S_wrong_leaf = S[.SOURCES = ([pcunit_source[.OCCURRENCES = '
 '$esp_replace(pcunit_source.OCCURRENCES,pcpath_hook ++ [PCFIELD 4,PCINDEX 0],phpType17_wrong_leaf)]])]',
 '$property_set_origin(S_wrong_leaf,ppropertydesc) = (porigin_hook) /\\ '
 '$property_set_signature_at(S_wrong_leaf,ppropertydesc) = eps /\\ '
 '$property_set_function(S_wrong_leaf,ppropertyhook) = eps',
 'phpType17_narrow = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES "c3RyaW5n") eps) (BOOLEAN false) '
 '(BOOLEAN false) (NExprVariable (BYTES text_incoming) metadata_variable) ABSENT (SEQUENCE eps) '
 'metadata_parameter',
 'phpType16_narrow = SEQUENCE ([phpType17_narrow])',
 'phpType38_narrow = NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook phpType16_narrow '
 'phpType39_hook metadata_hook',
 'pcnode_group_narrow = NStmtProperty phpType14_group phpType24_group phpType18_group phpType56_group '
 '(SEQUENCE ([phpType38_narrow])) metadata_group',
 'S_narrow = S[.SOURCES = ([pcunit_source[.OCCURRENCES = '
 '$esp_replace($esp_replace($esp_replace(pcunit_source.OCCURRENCES,pcpath_hook ++ [PCFIELD 4,PCINDEX '
 '0],phpType17_narrow),pcpath_hook,phpType38_narrow),pcpath_group,pcnode_group_narrow)]])]',
 'pssignature_narrow = pssignature_hook[.PARAMETERS = ([psparam_incoming[.TYPE = ([(PTBRANCH ([PTBUILTIN '
 '"string"]))])]])]',
 'S_narrow_function = S_narrow[.FUNCTIONS = ([pfunction_hook[.SIGNATURE = pssignature_narrow]])]',
 '$property_set_origin(S_narrow_function,ppropertydesc) = (porigin_hook) /\\ '
 '$property_set_explicit_signature(phpType16_narrow,ptcontext_hook) = (pssignature_narrow)',
 '$property_set_variance(ppropertydesc.TYPE,pssignature_narrow.PARAMETERS[0].TYPE,pclassdesc_parent.NAME,pclassdesc_parent.FINAL) '
 '= PVINCOMPATIBLE',
 '$property_set_signature_at(S_narrow_function,ppropertydesc) = eps /\\ '
 '$property_set_function(S_narrow_function,ppropertyhook) = eps',
 '~$property_set_parameters(SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) phpType18_parameter (BOOLEAN true) '
 '(BOOLEAN false) (NExprVariable (BYTES text_incoming) metadata_variable) ABSENT (SEQUENCE eps) '
 'metadata_parameter]))',
 '~$property_set_parameters(SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) phpType18_parameter (BOOLEAN false) '
 '(BOOLEAN true) (NExprVariable (BYTES text_incoming) metadata_variable) ABSENT (SEQUENCE eps) '
 'metadata_parameter]))',
 '~$property_set_parameters(SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN false) (BOOLEAN '
 'false) (NExprVariable (BYTES text_incoming) metadata_variable) ABSENT (SEQUENCE eps) metadata_parameter]))',
 '~$property_set_parameters(SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) phpType18_parameter (BOOLEAN false) '
 '(BOOLEAN false) (NExprVariable (BYTES text_incoming) metadata_variable) (NScalarInt (INTEGER 1) eps) '
 '(SEQUENCE eps) metadata_parameter]))',
 '~$property_set_parameters(SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 1) phpType18_parameter (BOOLEAN false) '
 '(BOOLEAN false) (NExprVariable (BYTES text_incoming) metadata_variable) ABSENT (SEQUENCE eps) '
 'metadata_parameter]))',
 '$property_set_explicit_signature(SEQUENCE eps,ptcontext_hook) = eps',
 '$property_set_function(S[.FUNCTIONS = ([pfunction_hook[.BODY = eps]])],ppropertyhook) = eps',
 '~$property_set_backing(S_entered[.FRAMES = eps],n_child,ppropertydesc)',
 '~$property_set_backing(S_entered[.CURRENT = (pcallcontext_set[.RECEIVER = eps])],n_child,ppropertydesc)',
 '~$property_set_backing(S_entered[.CURRENT = (pcallcontext_set[.FUNCTION = '
 'porigin_parent])],n_child,ppropertydesc)']

NARROW = ['ptbytes_message = $ptascii("Type of parameter $incoming of hook NarrowSetParent73::$value::set must be '
 'compatible with property type")',
 'S.COMPLETION = STATICBYTES ptbytes_message 7 /\\ S.EVENTS = eps /\\ S.OBJECTS = eps /\\ S.OBJECTPROPS = eps',
 'S.CLASSES = eps /\\ S.CLASSNAMES = eps /\\ S.FUNCTIONS = eps /\\ S.CURRENT = eps /\\ S.FRAMES = eps /\\ '
 'S.TODO = eps',
 'S.DECLARATIONS = [PDENTER 0 eps z_reporting,PDEXIT 0 PCSCOMPILER]',
 '$declaration_history_valid(S)',
 '$source_unit(S.SOURCES,0) = (pcunit_source)',
 'S.SOURCES = [pcunit_source]',
 '$origin_node(S.SOURCES,PORIGIN 0 ([PCINDEX 0])) = (NStmtClass phpType14_class phpType24_class phpType3_class '
 'phpType44_class phpType42_class phpType23_class metadata_class)',
 'phpType3_class = NIdentifier (BYTES text_class) metadata_name',
 '$base64(text_class) = $ptascii("NarrowSetParent73") /\\ phpType44_class = ABSENT',
 'phpType23_class = SEQUENCE (statement_property :: statement_method :: eps)',
 'statement_property = NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18_property phpType56_property '
 '(SEQUENCE ([phpType38_hook])) metadata_property',
 'phpType38_hook = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) (NIdentifier (BYTES text_set) '
 'metadata_set) phpType16_parameter (SEQUENCE statement_body*) metadata_hook',
 '$base64(text_set) = $ptascii("set") /\\ $psline(metadata_hook) = 4 /\\ $psendline(metadata_hook) = 7',
 'phpType16_parameter = SEQUENCE ([phpType17_parameter])',
 'phpType17_parameter = NParam (SEQUENCE eps) (INTEGER 0) phpType18_parameter (BOOLEAN false) (BOOLEAN false) '
 '(NExprVariable (BYTES text_incoming) metadata_variable) ABSENT (SEQUENCE eps) metadata_parameter',
 '$base64(text_incoming) = $ptascii("incoming") /\\ $psline(metadata_parameter) = 4',
 'porigin_hook = PORIGIN 0 ([PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 4,PCINDEX 0])',
 '$origin_node(S.SOURCES,porigin_hook) = (phpType38_hook)',
 '$origin_node(S.SOURCES,PORIGIN 0 ([PCINDEX 0,PCFIELD 5,PCINDEX 0,PCFIELD 4,PCINDEX 0,PCFIELD 4,PCINDEX 0])) '
 '= (phpType17_parameter)',
 'ptcontext_hook = {NAMESPACE eps, IMPORTS eps, SCOPE PTKNOWN ($ptascii("NarrowSetParent73")) eps, POSITION '
 'PTRETURN, OWNER $ptascii("NarrowSetParent73"), MEMBER $ptascii("$value::set"), FILE '
 '$call_sourcefile(S.FILES,porigin_hook), LINE 4}',
 '$ptype_normalize(phpType18_property,ptcontext_hook[.POSITION = PTPROPERTY][.MEMBER = '
 '$ptascii("value")][.LINE = 3]) = PTOK ptbranch_property* eps',
 'ptbranch_property* = [PTBRANCH ([PTBUILTIN "int"])]',
 '$property_set_parameters(phpType16_parameter)',
 '$property_set_explicit_signature(phpType16_parameter,ptcontext_hook) = (pssignature_hook)',
 'pssignature_hook.PARAMETERS[0].NAME = $ptascii("incoming") /\\ pssignature_hook.PARAMETERS[0].TYPE = '
 '[PTBRANCH ([PTBUILTIN "string"])] /\\ pssignature_hook.RETURNS = [PTBRANCH ([PTBUILTIN "void"])]',
 '$property_set_variance(ptbranch_property*,pssignature_hook.PARAMETERS[0].TYPE,$ptascii("NarrowSetParent73"),false) '
 '= PVINCOMPATIBLE',
 '$class_named(S.CLASSNAMES,$ptascii("narrowsetparent73")) = eps /\\ '
 '$class_named(S.CLASSNAMES,$ptascii("narrowsetchild73")) = eps']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--group', choices=['receive', 'error', 'narrow'], required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'explicit_setter_parameter_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    clauses, negatives, case_index, start_stage = {
        'receive': (RECEIVE, DERIVED, 0, 0),
        'error': (ERROR, [], 0, 3),
        'narrow': (NARROW, [], 1, None),
    }[args.group]
    selections = [(args.group, clauses, negatives)]
    cases = [data['cases'][case_index]]
    sources = [HERE / ['explicit-setter-parameter.php', 'explicit-setter-parameter-narrow.php'][case_index]]
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
    out = Path(tempfile.mkdtemp(prefix='explicit-setter-parameter-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    derived = sum(len(row[2]) for row in selections)
    reached = sum((1 if start_stage is None else 5) + len(row[1]) for row in selections)
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
                     'S_found = $esp_seek(S_initial,' + str(start_stage) + ',1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            if start_stage is None:
                setup = ['S = $php_run(' + ast_fixture + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')']
            content += '\ndec $esp_' + name + '() : bool\ndef $esp_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $esp_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = (' + ' /\\ '.join('$esp_' + name + '()' for name, _, _ in selections) + ')\n'
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
