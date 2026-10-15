"""Reached private setter access, implicit finality and original-result checks."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()

PREFIX = ('dec $psh_replace(pcoccurrence*,pcpath,pcnode) : pcoccurrence*\n'
 'def $psh_replace(eps,pcpath,pcnode) = eps\n'
 'def $psh_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath pcnode) :: '
 'pcoccurrence*\n'
 'def $psh_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath_other '
 'pcnode_old) :: $psh_replace(pcoccurrence*,pcpath,pcnode)\n'
 '  -- if pcpath_other =/= pcpath\n'
 'dec $psh_class_replace(pclassdesc*,porigin,pclassdesc) : pclassdesc*\n'
 'def $psh_class_replace(eps,porigin,pclassdesc) = eps\n'
 'def $psh_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_new :: pclassdesc*\n'
 '  -- if pclassdesc_old.ORIGIN = porigin\n'
 'def $psh_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_old :: '
 '$psh_class_replace(pclassdesc*,porigin,pclassdesc_new)\n'
 '  -- if pclassdesc_old.ORIGIN =/= porigin\n'
 'dec $psh_stage(pstate,nat) : bool\n'
 'def $psh_stage(S,0) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if S.TODO = (ASSIGN_ARRAY pbase 11 false) :: ptask*\n'
 '  -- if S.RESULT = VARIABLE ($ptascii("input")) 11\n'
 'def $psh_stage(S,1) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if S.TODO = (ASSIGN_ARRAY pbase 17 false) :: ptask*\n'
 '  -- if S.RESULT = VARIABLE ($ptascii("input")) 17\n'
 'def $psh_stage(S,2) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_SET_TARGET ppropertyhook\n'
 '  -- if S.TODO = (ASSIGN_ARRAY pbase 6 false) :: ptask*\n'
 '  -- if S.RESULT = KNOWN (PINT 33)\n'
 'def $psh_stage(S,3) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if S.TODO = (PROPERTY_SET_RESULT ppropertyhook (PINT 20)) :: ptask*\n'
 'def $psh_stage(S,4) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_SET_TARGET ppropertyhook\n'
 '  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: ptask*\n'
 '  -- if $lookup(S.ENV,$ptascii("value")) = (n_cell)\n'
 '  -- if S.STORE[n_cell] = DEFINED (PARRAY n_array)\n'
 'def $psh_stage(S,5) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) 42) :: (DIM_FETCH 42) :: ptask*\n'
 '  -- if $base64(text_name) = $ptascii("value")\n'
 'def $psh_stage(S,6) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (ASSIGN_ARRAY pbase 32 false) :: ptask*\n'
 'def $psh_stage(S,n) = false -- otherwise\n'
 'dec $psh_seek(pstate,nat,nat) : pstate\n'
 'def $psh_seek(S,n_stage,n) = S\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if $psh_stage(S,n_stage) \\/ n = 0\n'
 'def $psh_seek(S,n_stage,n) = $psh_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if ~$psh_stage(S,n_stage) /\\ $(n > 0)\n'
 'def $psh_seek(S,n_stage,n) = $psh_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
 '  -- if $throwable_pending(S.COMPLETION) /\\ $(n > 0)\n'
 'def $psh_seek(S,n_stage,n) = S -- otherwise\n'
 'dec $psh_after(pstate,pstate) : pstate\n'
 'def $psh_after(S,S_next) = '
 '$gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))\n'
 'dec $psh_guard(pstate) : bool\n'
 'def $psh_guard(S) = ($call_descriptors_valid(S) /\\ $declaration_history_valid(S) /\\ $property_state_valid(S) /\\ '
 '$heap_valid($heap_prune($heap_graph(S))))\n'
 'dec $psh_output(pevent*) : ptbytes\n'
 'def $psh_output(eps) = eps\n'
 'def $psh_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $psh_output(pevent*)\n')

COMMON = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("PrivateSetterParent80"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("PrivateSetterChild80"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 'pclassdesc_parent.KIND = "class" /\\ pclassdesc_parent.PARENT = eps /\\ ~pclassdesc_parent.READONLY /\\ '
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ pclassdesc_child.PROPERTIES = eps',
 '$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_parent)',
 'ppropertydesc = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc.ORIGIN = porigin_property',
 'ppropertydesc.NAME = $ptascii("value") /\\ ppropertydesc.KEY = ppropertydesc.NAME /\\ ppropertydesc.TYPE = '
 '([(PTBRANCH ([PTBUILTIN "int"]))]) /\\ ppropertydesc.VISIBILITY = PROPERTY_PUBLIC /\\ ppropertydesc.SETVISIBILITY = '
 '(PROPERTY_PRIVATE)',
 '$property_default_state(S,ppropertydesc) = (PROP_VALUE (DIRECT (PINT 10))) /\\ ~ppropertydesc.STATIC /\\ '
 '~ppropertydesc.READONLY /\\ ppropertydesc.FINAL',
 '$property_layout(S,porigin_parent,|S.CLASSES|) = [ppropertydesc] /\\ $property_layout(S,porigin_child,|S.CLASSES|) = '
 '[ppropertydesc]',
 '$property_set_origin(S,ppropertydesc) = (porigin_hook)',
 '$property_hook_origin(S,ppropertydesc) = eps /\\ $property_hook_effective_origin(S,ppropertydesc) = eps /\\ '
 '~$property_hook_virtual(S,ppropertydesc)',
 '$function_at(S.FUNCTIONS,porigin_hook) = (pfunction_hook)',
 'pfunction_hook.SIGNATURE = $property_set_signature(ppropertydesc) /\\ pfunction_hook.SIGNATURE = {PARAMETERS ([{NAME '
 '$ptascii("value"), TYPE ppropertydesc.TYPE, BYREF false, VARIADIC false, REQUIRED true, DEFAULT PSNONE}]), RETURNS '
 '([(PTBRANCH ([PTBUILTIN "void"]))]), BYREF false}',
 'pfunction_hook.NAME = pclassdesc_parent.NAME ++ $ptascii("::$value::set") /\\ pfunction_hook.DEFAULTS = eps /\\ '
 '~pfunction_hook.EARLY /\\ pfunction_hook.LINE = 4 /\\ pfunction_hook.ENDLINE = 7',
 'S.FUNCTIONS = [pfunction_hook] /\\ $ptascii("value") <- pfunction_hook.CVS /\\ '
 '$method_named(pclassdesc_parent.METHODS,$property_set_name(ppropertydesc.NAME)) = eps',
 'porigin_hook = PORIGIN n_source pcpath_hook',
 'pfunction_hook.BODY = pcpath_hook ++ [PCFIELD 5]',
 '$origin_node(S.SOURCES,porigin_hook) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook '
 'phpType16_hook phpType39_hook metadata_hook)',
 'phpType14_hook = SEQUENCE eps /\\ phpType24_hook = INTEGER 0 /\\ phpType4_hook = BOOLEAN false /\\ phpType16_hook = '
 'SEQUENCE eps',
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
 '$psh_guard(S)',
 'porigin_property = PORIGIN n_source pcpath_property',
 'pcpath_group = pcpath_hook[0:$nabs($( |pcpath_hook| - 2))]',
 '$origin_node(S.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty phpType14_group phpType24_group '
 'phpType18_group phpType56_group phpType37_group metadata_group)',
 'phpType14_group = SEQUENCE eps /\\ phpType24_group = INTEGER 513',
 'phpType37_group = SEQUENCE ([NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook phpType16_hook '
 'phpType39_hook metadata_hook])',
 '$ppproperty_visibility(513) = PROPERTY_PUBLIC /\\ $ppproperty_set_visibility(513) = (PROPERTY_PRIVATE) /\\ '
 '$ppproperty_final(513)',
 '$source_unit(S.SOURCES,n_source) = (pcunit_source)',
 '$origin_node(S.SOURCES,pclassdesc_parent.ORIGIN) = (statement_parent)',
 '$pchlower(statement_parent) = PCHRAW pchraw_parent',
 'pchraw_parent.KIND = "class" /\\ pchraw_parent.PARENT = ABSENT']

RECEIVE = ['$psh_stage(S,0)',
 'S.CURRENT = (pcallcontext_writer)',
 'pcallcontext_writer.RECEIVER = (n_child)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("PrivateSetterParent80"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("PrivateSetterChild80"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 'pclassdesc_parent.KIND = "class" /\\ pclassdesc_parent.PARENT = eps /\\ ~pclassdesc_parent.READONLY /\\ '
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ pclassdesc_child.PROPERTIES = eps',
 '$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_parent)',
 'ppropertydesc = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc.ORIGIN = porigin_property',
 'ppropertydesc.NAME = $ptascii("value") /\\ ppropertydesc.KEY = ppropertydesc.NAME /\\ ppropertydesc.TYPE = '
 '([(PTBRANCH ([PTBUILTIN "int"]))]) /\\ ppropertydesc.VISIBILITY = PROPERTY_PUBLIC /\\ ppropertydesc.SETVISIBILITY = '
 '(PROPERTY_PRIVATE)',
 '$property_default_state(S,ppropertydesc) = (PROP_VALUE (DIRECT (PINT 10))) /\\ ~ppropertydesc.STATIC /\\ '
 '~ppropertydesc.READONLY /\\ ppropertydesc.FINAL',
 '$property_layout(S,porigin_parent,|S.CLASSES|) = [ppropertydesc] /\\ $property_layout(S,porigin_child,|S.CLASSES|) = '
 '[ppropertydesc]',
 '$property_set_origin(S,ppropertydesc) = (porigin_hook)',
 '$property_hook_origin(S,ppropertydesc) = eps /\\ $property_hook_effective_origin(S,ppropertydesc) = eps /\\ '
 '~$property_hook_virtual(S,ppropertydesc)',
 '$function_at(S.FUNCTIONS,porigin_hook) = (pfunction_hook)',
 'pfunction_hook.SIGNATURE = $property_set_signature(ppropertydesc) /\\ pfunction_hook.SIGNATURE = {PARAMETERS ([{NAME '
 '$ptascii("value"), TYPE ppropertydesc.TYPE, BYREF false, VARIADIC false, REQUIRED true, DEFAULT PSNONE}]), RETURNS '
 '([(PTBRANCH ([PTBUILTIN "void"]))]), BYREF false}',
 'pfunction_hook.NAME = pclassdesc_parent.NAME ++ $ptascii("::$value::set") /\\ pfunction_hook.DEFAULTS = eps /\\ '
 '~pfunction_hook.EARLY /\\ pfunction_hook.LINE = 4 /\\ pfunction_hook.ENDLINE = 7',
 'S.FUNCTIONS = [pfunction_hook] /\\ $ptascii("value") <- pfunction_hook.CVS /\\ '
 '$method_named(pclassdesc_parent.METHODS,$property_set_name(ppropertydesc.NAME)) = eps',
 'porigin_hook = PORIGIN n_source pcpath_hook',
 'pfunction_hook.BODY = pcpath_hook ++ [PCFIELD 5]',
 '$origin_node(S.SOURCES,porigin_hook) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook '
 'phpType16_hook phpType39_hook metadata_hook)',
 'phpType14_hook = SEQUENCE eps /\\ phpType24_hook = INTEGER 0 /\\ phpType4_hook = BOOLEAN false /\\ phpType16_hook = '
 'SEQUENCE eps',
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
 '$psh_guard(S)',
 'porigin_property = PORIGIN n_source pcpath_property',
 'pcpath_group = pcpath_hook[0:$nabs($( |pcpath_hook| - 2))]',
 '$origin_node(S.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty phpType14_group phpType24_group '
 'phpType18_group phpType56_group phpType37_group metadata_group)',
 'phpType14_group = SEQUENCE eps /\\ phpType24_group = INTEGER 513',
 'phpType37_group = SEQUENCE ([NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook phpType16_hook '
 'phpType39_hook metadata_hook])',
 '$ppproperty_visibility(513) = PROPERTY_PUBLIC /\\ $ppproperty_set_visibility(513) = (PROPERTY_PRIVATE) /\\ '
 '$ppproperty_final(513)',
 '$source_unit(S.SOURCES,n_source) = (pcunit_source)',
 '$origin_node(S.SOURCES,pclassdesc_parent.ORIGIN) = (statement_parent)',
 '$pchlower(statement_parent) = PCHRAW pchraw_parent',
 'pchraw_parent.KIND = "class" /\\ pchraw_parent.PARENT = ABSENT',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("write")) = (pmethoddesc_writer)',
 'pcallcontext_writer.FUNCTION = pmethoddesc_writer.FUNCTION.ORIGIN /\\ pcallcontext_writer.LEXICAL_CLASS = '
 '(porigin_parent) /\\ pcallcontext_writer.CALLED_CLASS = (porigin_child)',
 '$lookup(S.ENV,$ptascii("input")) = (n_input)',
 'S.STORE[n_input] = DEFINED (PINT 20)',
 '$class_static_set_allowed(S,ppropertydesc) /\\ ~$property_set_denied(S,n_child,ppropertydesc.KEY)',
 'S.ORIGIN = (porigin_site)',
 'S.TODO = (ASSIGN_ARRAY pbase 11 false) :: ptask_caller*',
 '$property_set_plan(S) = (ppropertyhook)',
 'ppropertyhook = {SITE porigin_site, OBJECT n_child, PROPERTY porigin_property, HOOK porigin_hook, LINE 11}',
 '$property_set_valid(S,ppropertyhook) /\\ $property_set_access_allowed(S,ppropertyhook) /\\ '
 '$property_set_denied_plan(S) = eps /\\ $property_set_virtual_write_error(S) = eps',
 '$target_function(S,PROPERTY_SET_TARGET ppropertyhook) = (pfunction_hook)',
 '$objectprops_at(S.OBJECTPROPS,n_child) = ([{DECL (porigin_property), NAME ppropertydesc.KEY, STATE PROP_VALUE '
 '(DIRECT (PINT 10))}])',
 'pbase = BASE_PROPERTY_PENDING pbase_receiver poperand_name z_receiver',
 'S_target = $property_pending_resolve(S,pbase_receiver,poperand_name,PPW,z_receiver,11)',
 'S_rhs = $resolve_at(S_target,S.RESULT,11)',
 'S_rhs.COMPLETION = NORMAL /\\ S_rhs.RESULT = KNOWN (PINT 20)',
 'PhpStep: S ~> S_call_raw',
 'S_call = $psh_after(S,S_call_raw)',
 'S_call.TODO = (CALL_ARGS (PROPERTY_SET_TARGET ppropertyhook) eps 1 ([KNOWN (PINT 20)]) (porigin_site) 11) :: '
 '(PROPERTY_SET_RESULT ppropertyhook (PINT 20)) :: ptask_caller*',
 'S_call.CURRENT = S.CURRENT /\\ S_call.FRAMES = S.FRAMES /\\ S_call.OBJECTPROPS = S.OBJECTPROPS /\\ S_call.EVENTS = '
 'S.EVENTS',
 '$property_set_pending_call(S_call,ppropertyhook) /\\ $call_task_valid(S_call,CALL_ARGS (PROPERTY_SET_TARGET '
 'ppropertyhook) eps 1 ([KNOWN (PINT 20)]) (porigin_site) 11) /\\ $psh_guard(S_call)',
 'PhpStep: S_call ~> S_entered_raw',
 'S_entered = $psh_after(S_call,S_entered_raw)',
 'S_entered.CURRENT = (pcallcontext_set)',
 'pcallcontext_set.TARGET = PROPERTY_SET_TARGET ppropertyhook /\\ pcallcontext_set.FUNCTION = porigin_hook /\\ '
 'pcallcontext_set.ARGC = 1 /\\ pcallcontext_set.CALLSITE = (porigin_site) /\\ pcallcontext_set.LINE = 11',
 'pcallcontext_set.LEXICAL_CLASS = (porigin_parent) /\\ pcallcontext_set.CALLED_CLASS = (porigin_child) /\\ '
 'pcallcontext_set.RECEIVER = (n_child)',
 'S_entered.FRAMES = pframe_set :: pframe_caller*',
 'pframe_set.CONTEXT = S.CURRENT /\\ pframe_caller* = S.FRAMES',
 'S_entered.TODO = [TYPE_RECEIVE porigin_hook 0] /\\ S_entered.ORIGIN = (porigin_hook)',
 '$lookup(S_entered.ENV,$ptascii("value")) = (n_value_cell)',
 'S_entered.STORE[n_value_cell] = DEFINED (PINT 20)',
 '$property_set_context_valid(S_entered,pcallcontext_set) /\\ $typed_receive_valid(S_entered,porigin_hook,0) /\\ '
 '$named_receives_ready(S_entered,pfunction_hook)',
 '$property_set_frame(S_entered,pcallcontext_set,pframe_set,ppropertyhook) /\\ $property_set_tail(S_entered[.CURRENT = '
 'pframe_set.CONTEXT],ppropertyhook,pframe_set.TODO)',
 '$property_set_access_allowed(S_entered[.CURRENT = pframe_set.CONTEXT],ppropertyhook) /\\ $psh_guard(S_entered)',
 'PhpStep: S_entered ~> S_received_raw',
 'S_received = $psh_after(S_entered,S_received_raw)',
 'S_received.COMPLETION = NORMAL /\\ S_received.CURRENT = S_entered.CURRENT /\\ S_received.FRAMES = S_entered.FRAMES '
 '/\\ S_received.TODO = $function_body_tasks(S_received,pfunction_hook)',
 'S_back_found = $psh_seek(S_received,2,1000)',
 'S_back_found.COMPLETION = NORMAL \\/ S_back_found.COMPLETION = BUDGET',
 'S_back = S_back_found[.COMPLETION = NORMAL]',
 '$psh_stage(S_back,2)',
 'S_back.CURRENT = S_entered.CURRENT /\\ S_back.FRAMES = S_entered.FRAMES',
 '$property_set_context_valid(S_back,pcallcontext_set) /\\ $property_set_backing(S_back,n_child,ppropertydesc) /\\ '
 '~$property_set_needed(S_back,n_child,$ptascii("value")) /\\ ~$property_set_denied(S_back,n_child,ppropertydesc.KEY)',
 '$method_selected_scope(S_back,n_child,$ptascii("offset"),(porigin_parent)) = (pmethoddesc_parent_offset)',
 'S_back.TODO = (ASSIGN_ARRAY pbase_back 6 false) :: ptask_back*',
 '$call_task_valid(S_back,ASSIGN_ARRAY pbase_back 6 false) /\\ $psh_guard(S_back)',
 'PhpStep: S_back ~> S_written_raw',
 'S_written = $psh_after(S_back,S_written_raw)',
 'S_written.COMPLETION = NORMAL /\\ S_written.RESULT = KNOWN (PINT 33) /\\ S_written.TODO = ptask_back* /\\ '
 'S_written.CURRENT = S_back.CURRENT /\\ S_written.FRAMES = S_back.FRAMES /\\ S_written.EVENTS = S_back.EVENTS',
 '$objectprops_at(S_written.OBJECTPROPS,n_child) = ([{DECL (porigin_property), NAME ppropertydesc.KEY, STATE '
 'PROP_VALUE (DIRECT (PINT 33))}])',
 '$psh_guard(S_written)',
 'S_return_found = $psh_seek(S_written,3,1000)',
 'S_return_found.COMPLETION = NORMAL \\/ S_return_found.COMPLETION = BUDGET',
 'S_return = S_return_found[.COMPLETION = NORMAL]',
 '$psh_stage(S_return,3)',
 'S_return.TODO = (PROPERTY_SET_RESULT ppropertyhook (PINT 20)) :: ptask_return*',
 'S_return.RESULT = KNOWN PNULL /\\ S_return.CURRENT = S.CURRENT /\\ S_return.FRAMES = S.FRAMES /\\ S_return.ENV = '
 'S.ENV /\\ S_return.GLOBALTABLE = S.GLOBALTABLE /\\ S_return.ORIGIN = (porigin_site)',
 '$property_set_access_allowed(S_return,ppropertyhook) /\\ $call_task_valid(S_return,PROPERTY_SET_RESULT ppropertyhook '
 '(PINT 20)) /\\ $psh_guard(S_return)',
 'PhpStep: S_return ~> S_result_raw',
 'S_result = $psh_after(S_return,S_result_raw)',
 'S_result.COMPLETION = NORMAL /\\ S_result.RESULT = KNOWN (PINT 20) /\\ S_result.TODO = ptask_return* /\\ '
 'S_result.OBJECTPROPS = S_return.OBJECTPROPS /\\ S_result.CURRENT = S.CURRENT /\\ S_result.FRAMES = S.FRAMES',
 '$objectprops_at(S_result.OBJECTPROPS,n_child) = ([{DECL (porigin_property), NAME ppropertydesc.KEY, STATE PROP_VALUE '
 '(DIRECT (PINT 33))}])',
 'S_public_read = $property_read(S_result,POBJECT n_child,$ptascii("value"),11)',
 'S_public_read.COMPLETION = NORMAL /\\ S_public_read.RESULT = KNOWN (PINT 33)',
 '$psh_output(S_result.EVENTS) = '
 '$ptascii("I:10/10|SET:PrivateSetterParent80/PrivateSetterChild80/PrivateSetterParent80::$value::set/20|")',
 '$psh_guard(S_result)']

ERRORS = ['$psh_stage(S,1)',
 'S.CURRENT = (pcallcontext_denied)',
 'pcallcontext_denied.RECEIVER = (n_child)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("PrivateSetterParent80"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("PrivateSetterChild80"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 'pclassdesc_parent.KIND = "class" /\\ pclassdesc_parent.PARENT = eps /\\ ~pclassdesc_parent.READONLY /\\ '
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ pclassdesc_child.PROPERTIES = eps',
 '$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_parent)',
 'ppropertydesc = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc.ORIGIN = porigin_property',
 'ppropertydesc.NAME = $ptascii("value") /\\ ppropertydesc.KEY = ppropertydesc.NAME /\\ ppropertydesc.TYPE = '
 '([(PTBRANCH ([PTBUILTIN "int"]))]) /\\ ppropertydesc.VISIBILITY = PROPERTY_PUBLIC /\\ ppropertydesc.SETVISIBILITY = '
 '(PROPERTY_PRIVATE)',
 '$property_default_state(S,ppropertydesc) = (PROP_VALUE (DIRECT (PINT 10))) /\\ ~ppropertydesc.STATIC /\\ '
 '~ppropertydesc.READONLY /\\ ppropertydesc.FINAL',
 '$property_layout(S,porigin_parent,|S.CLASSES|) = [ppropertydesc] /\\ $property_layout(S,porigin_child,|S.CLASSES|) = '
 '[ppropertydesc]',
 '$property_set_origin(S,ppropertydesc) = (porigin_hook)',
 '$property_hook_origin(S,ppropertydesc) = eps /\\ $property_hook_effective_origin(S,ppropertydesc) = eps /\\ '
 '~$property_hook_virtual(S,ppropertydesc)',
 '$function_at(S.FUNCTIONS,porigin_hook) = (pfunction_hook)',
 'pfunction_hook.SIGNATURE = $property_set_signature(ppropertydesc) /\\ pfunction_hook.SIGNATURE = {PARAMETERS ([{NAME '
 '$ptascii("value"), TYPE ppropertydesc.TYPE, BYREF false, VARIADIC false, REQUIRED true, DEFAULT PSNONE}]), RETURNS '
 '([(PTBRANCH ([PTBUILTIN "void"]))]), BYREF false}',
 'pfunction_hook.NAME = pclassdesc_parent.NAME ++ $ptascii("::$value::set") /\\ pfunction_hook.DEFAULTS = eps /\\ '
 '~pfunction_hook.EARLY /\\ pfunction_hook.LINE = 4 /\\ pfunction_hook.ENDLINE = 7',
 'S.FUNCTIONS = [pfunction_hook] /\\ $ptascii("value") <- pfunction_hook.CVS /\\ '
 '$method_named(pclassdesc_parent.METHODS,$property_set_name(ppropertydesc.NAME)) = eps',
 'porigin_hook = PORIGIN n_source pcpath_hook',
 'pfunction_hook.BODY = pcpath_hook ++ [PCFIELD 5]',
 '$origin_node(S.SOURCES,porigin_hook) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook '
 'phpType16_hook phpType39_hook metadata_hook)',
 'phpType14_hook = SEQUENCE eps /\\ phpType24_hook = INTEGER 0 /\\ phpType4_hook = BOOLEAN false /\\ phpType16_hook = '
 'SEQUENCE eps',
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
 '$psh_guard(S)',
 'porigin_property = PORIGIN n_source pcpath_property',
 'pcpath_group = pcpath_hook[0:$nabs($( |pcpath_hook| - 2))]',
 '$origin_node(S.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty phpType14_group phpType24_group '
 'phpType18_group phpType56_group phpType37_group metadata_group)',
 'phpType14_group = SEQUENCE eps /\\ phpType24_group = INTEGER 513',
 'phpType37_group = SEQUENCE ([NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook phpType16_hook '
 'phpType39_hook metadata_hook])',
 '$ppproperty_visibility(513) = PROPERTY_PUBLIC /\\ $ppproperty_set_visibility(513) = (PROPERTY_PRIVATE) /\\ '
 '$ppproperty_final(513)',
 '$source_unit(S.SOURCES,n_source) = (pcunit_source)',
 '$origin_node(S.SOURCES,pclassdesc_parent.ORIGIN) = (statement_parent)',
 '$pchlower(statement_parent) = PCHRAW pchraw_parent',
 'pchraw_parent.KIND = "class" /\\ pchraw_parent.PARENT = ABSENT',
 '$method_named(pclassdesc_child.METHODS,$ptascii("denied")) = (pmethoddesc_denied)',
 'pcallcontext_denied.FUNCTION = pmethoddesc_denied.FUNCTION.ORIGIN /\\ pcallcontext_denied.LEXICAL_CLASS = '
 '(porigin_child) /\\ pcallcontext_denied.CALLED_CLASS = (porigin_child)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("write")) = (pmethoddesc_writer)',
 '$lookup(S.ENV,$ptascii("input")) = (n_input_cell)',
 'S.STORE[n_input_cell] = DEFINED (PARRAY n_array_denied)',
 'S.ORIGIN = (porigin_site_denied)',
 'S.TODO = (ASSIGN_ARRAY pbase_denied 17 false) :: ptask_denied*',
 'pbase_denied = BASE_PROPERTY_PENDING pbase_receiver poperand_name z_receiver',
 'S_target = $property_pending_resolve(S,pbase_receiver,poperand_name,PPW,z_receiver,17)',
 'S_rhs = $resolve_at(S_target,S.RESULT,17)',
 'S_rhs.COMPLETION = NORMAL /\\ S_rhs.RESULT = KNOWN (PARRAY n_array_denied)',
 'S.ARRAYS[n_array_denied].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
 '$typed_parameter_conversion_at(S,pfunction_hook.SIGNATURE.PARAMETERS[0].TYPE,PARRAY n_array_denied,false) = '
 'TYPEREJECT',
 '$property_protected_allowed(S,ppropertydesc) /\\ ~$class_static_set_allowed(S,ppropertydesc) /\\ '
 '$property_set_denied(S,n_child,ppropertydesc.KEY)',
 'ppropertyhook_denied = {SITE porigin_site_denied, OBJECT n_child, PROPERTY porigin_property, HOOK porigin_hook, LINE '
 '17}',
 '$property_set_denied_plan(S) = (ppropertyhook_denied)',
 '$property_set_valid(S,ppropertyhook_denied) /\\ ~$property_set_access_allowed(S,ppropertyhook_denied) /\\ '
 '$property_set_plan(S) = eps /\\ $property_set_pending(S)',
 '$property_set_function(S,ppropertyhook_denied) = (pfunction_hook) /\\ $target_function(S,PROPERTY_SET_TARGET '
 'ppropertyhook_denied) = eps',
 '$objectprops_at(S.OBJECTPROPS,n_child) = ([{DECL (porigin_property), NAME ppropertydesc.KEY, STATE PROP_VALUE '
 '(DIRECT (PINT 33))}])',
 'ptbytes_denied = $ptascii("Cannot modify private(set) property PrivateSetterParent80::$value from scope '
 'PrivateSetterChild80")',
 'PhpStep: S ~> S_denied_raw',
 'S_denied_raw = $property_set_check(S_rhs[.TODO = ptask_denied*],n_child,ppropertydesc.KEY,$ptascii("modify"),17)',
 'S_denied_raw.COMPLETION = THROWN "Error" ptbytes_denied 17 /\\ S_denied_raw.TODO = ptask_denied* /\\ '
 'S_denied_raw.CURRENT = S.CURRENT /\\ S_denied_raw.FRAMES = S.FRAMES /\\ S_denied_raw.OBJECTPROPS = S.OBJECTPROPS /\\ '
 'S_denied_raw.EVENTS = S.EVENTS',
 'S_denied = $psh_after(S,S_denied_raw)',
 'S_denied.COMPLETION = THROWING n_error_denied',
 '$object_name(S_denied,n_error_denied) = $ptascii("Error") /\\ $throwable_field(S_denied,n_error_denied,"message") = '
 'PSTRING ptbytes_denied /\\ $psh_guard(S_denied)',
 'S_global_found = $psh_seek(S_denied,6,1000)',
 'S_global_found.COMPLETION = NORMAL \\/ S_global_found.COMPLETION = BUDGET',
 'S_global = S_global_found[.COMPLETION = NORMAL]',
 '$psh_stage(S_global,6) /\\ S_global.CURRENT = eps /\\ S_global.FRAMES = eps',
 '$lookup(S_global.ENV,$ptascii("child")) = (n_child_cell)',
 'S_global.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
 'S_global.RESULT = KNOWN (PARRAY n_array_global)',
 'S_global.ARRAYS[n_array_global].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
 'S_global.ORIGIN = (porigin_site_global)',
 'S_global.TODO = (ASSIGN_ARRAY pbase_global 32 false) :: ptask_global*',
 'pbase_global = BASE_PROPERTY_PENDING pbase_receiver_global poperand_name_global z_receiver_global',
 'S_global_target = '
 '$property_pending_resolve(S_global,pbase_receiver_global,poperand_name_global,PPW,z_receiver_global,32)',
 'S_global_rhs = $resolve_at(S_global_target,S_global.RESULT,32)',
 'S_global_rhs.COMPLETION = NORMAL /\\ S_global_rhs.RESULT = KNOWN (PARRAY n_array_global)',
 'ppropertyhook_global = {SITE porigin_site_global, OBJECT n_child, PROPERTY porigin_property, HOOK porigin_hook, LINE '
 '32}',
 '$property_set_denied_plan(S_global) = (ppropertyhook_global) /\\ $property_set_valid(S_global,ppropertyhook_global)',
 '$property_set_plan(S_global) = eps /\\ ~$property_set_access_allowed(S_global,ppropertyhook_global) /\\ '
 '$target_function(S_global,PROPERTY_SET_TARGET ppropertyhook_global) = eps',
 'ptbytes_global = $ptascii("Cannot modify private(set) property PrivateSetterParent80::$value from global scope")',
 'PhpStep: S_global ~> S_global_raw',
 'S_global_raw = $property_set_check(S_global_rhs[.TODO = '
 'ptask_global*],n_child,ppropertydesc.KEY,$ptascii("modify"),32)',
 'S_global_raw.COMPLETION = THROWN "Error" ptbytes_global 32 /\\ S_global_raw.TODO = ptask_global* /\\ '
 'S_global_raw.CURRENT = eps /\\ S_global_raw.FRAMES = eps /\\ S_global_raw.OBJECTPROPS = S_global.OBJECTPROPS /\\ '
 'S_global_raw.EVENTS = S_global.EVENTS',
 'S_global_error = $psh_after(S_global,S_global_raw)',
 'S_global_error.COMPLETION = THROWING n_error_global',
 '$object_name(S_global_error,n_error_global) = $ptascii("Error") /\\ '
 '$throwable_field(S_global_error,n_error_global,"message") = PSTRING ptbytes_global /\\ $psh_guard(S_global_error)',
 'S_bad_found = $psh_seek(S_global_error,4,1000)',
 'S_bad_found.COMPLETION = NORMAL \\/ S_bad_found.COMPLETION = BUDGET',
 'S_bad = S_bad_found[.COMPLETION = NORMAL]',
 '$psh_stage(S_bad,4)',
 'S_bad.CURRENT = (pcallcontext_bad)',
 'pcallcontext_bad.TARGET = PROPERTY_SET_TARGET ppropertyhook_bad',
 'ppropertyhook_bad.OBJECT = n_child /\\ ppropertyhook_bad.PROPERTY = porigin_property /\\ ppropertyhook_bad.HOOK = '
 'porigin_hook /\\ ppropertyhook_bad.LINE = 11',
 'pcallcontext_bad.FUNCTION = porigin_hook /\\ pcallcontext_bad.LEXICAL_CLASS = (porigin_parent) /\\ '
 'pcallcontext_bad.CALLED_CLASS = (porigin_child) /\\ pcallcontext_bad.ARGC = 1',
 'S_bad.TODO = [TYPE_RECEIVE porigin_hook 0] /\\ S_bad.ORIGIN = (porigin_hook)',
 'S_bad.FRAMES = pframe_bad :: pframe_bad_tail*',
 'pframe_bad.CONTEXT = (pcallcontext_bad_writer)',
 'pcallcontext_bad_writer.LEXICAL_CLASS = (porigin_parent) /\\ pcallcontext_bad_writer.CALLED_CLASS = (porigin_child) '
 '/\\ pcallcontext_bad_writer.FUNCTION = pmethoddesc_writer.FUNCTION.ORIGIN',
 '$property_set_access_allowed(S_bad[.CURRENT = pframe_bad.CONTEXT],ppropertyhook_bad) /\\ '
 '$property_set_frame(S_bad,pcallcontext_bad,pframe_bad,ppropertyhook_bad)',
 '$lookup(S_bad.ENV,$ptascii("value")) = (n_value_cell)',
 'S_bad.STORE[n_value_cell] = DEFINED (PARRAY n_array_bad)',
 'S_bad.ARRAYS[n_array_bad].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
 '$property_set_context_valid(S_bad,pcallcontext_bad) /\\ $typed_receive_valid(S_bad,porigin_hook,0) /\\ '
 '$named_receives_ready(S_bad,pfunction_hook) /\\ $default_parameter_line(S_bad,porigin_hook,0) = 4',
 '$objectprops_at(S_bad.OBJECTPROPS,n_child) = ([{DECL (porigin_property), NAME ppropertydesc.KEY, STATE PROP_VALUE '
 '(DIRECT (PINT 33))}])',
 'ptbytes_type = pfunction_hook.NAME ++ $ptascii("(): Argument #1 ($value) must be of type int, array given, called in '
 '") ++ $call_sourcefile(S_bad.FILES,ppropertyhook_bad.SITE) ++ $ptascii(" on line 11")',
 'PhpStep: S_bad ~> S_type_raw',
 'S_type_raw.COMPLETION = THROWN "TypeError" ptbytes_type 4 /\\ S_type_raw.EVENTS = S_bad.EVENTS /\\ '
 'S_type_raw.OBJECTPROPS = S_bad.OBJECTPROPS /\\ S_type_raw.CURRENT = S_bad.CURRENT /\\ S_type_raw.FRAMES = '
 'S_bad.FRAMES',
 'S_type = $psh_after(S_bad,S_type_raw)',
 'S_type.COMPLETION = THROWING n_error_type',
 '$object_name(S_type,n_error_type) = $ptascii("TypeError") /\\ $throwable_field(S_type,n_error_type,"message") = '
 'PSTRING ptbytes_type /\\ $psh_guard(S_type)',
 'S_final_found = $psh_seek(S_type,5,1000)',
 'S_final_found.COMPLETION = NORMAL \\/ S_final_found.COMPLETION = BUDGET',
 'S_final = S_final_found[.COMPLETION = NORMAL]',
 '$psh_stage(S_final,5)',
 'S_final.CURRENT = eps /\\ S_final.FRAMES = eps /\\ $objectprops_at(S_final.OBJECTPROPS,n_child) = ([{DECL '
 '(porigin_property), NAME ppropertydesc.KEY, STATE PROP_VALUE (DIRECT (PINT 33))}])',
 'PhpStep: S_final ~> S_fetch_raw',
 'S_fetch = $psh_after(S_final,S_fetch_raw)',
 'S_fetch.COMPLETION = NORMAL /\\ S_fetch.BASE = BASE_PROPERTY (POBJECT n_child) ppropertydesc.KEY',
 'PhpStep: S_fetch ~> S_read_raw',
 'S_read = $psh_after(S_fetch,S_read_raw)',
 'S_read.COMPLETION = NORMAL /\\ S_read.RESULT = KNOWN (PINT 33) /\\ S_read.CURRENT = eps /\\ S_read.FRAMES = eps /\\ '
 'S_read.OBJECTPROPS = S_final.OBJECTPROPS /\\ $psh_guard(S_read)',
 'S_end = $drive_steps(S_read,1000)',
 'S_end.COMPLETION = NORMAL',
 '$psh_output(S_end.EVENTS) = '
 '$ptascii("I:10/10|SET:PrivateSetterParent80/PrivateSetterChild80/PrivateSetterParent80::$value::set/20|R:20/33/33|CHILD:") '
 '++ ptbytes_denied ++ $ptascii("|GLOBAL:") ++ ptbytes_global ++ $ptascii("|TYPE:") ++ ptbytes_type ++ '
 '$ptascii("|F:33/33|")']

DERIVED = ['S_global = S[.CURRENT = eps]',
 '$class_static_set_allowed(S_global,ppropertydesc) = false /\\ $property_set_access_allowed(S_global,ppropertyhook) = '
 'false /\\ $target_function(S_global,PROPERTY_SET_TARGET ppropertyhook) = eps',
 '$property_set_access_allowed(S[.CURRENT = (pcallcontext_writer[.LEXICAL_CLASS = eps])],ppropertyhook) = false',
 '$property_set_access_allowed(S[.CURRENT = (pcallcontext_writer[.CALLED_CLASS = (porigin_parent)])],ppropertyhook)',
 'S_wrong_flags = S[.SOURCES = ([pcunit_source[.OCCURRENCES = '
 '$psh_replace(pcunit_source.OCCURRENCES,pcpath_group,NStmtProperty phpType14_group (INTEGER 1) phpType18_group '
 'phpType56_group phpType37_group metadata_group)]])]',
 '$property_set_origin(S_wrong_flags,ppropertydesc) = eps',
 'ppropertydesc_no_set = ppropertydesc[.SETVISIBILITY = eps]',
 'S_no_set = S[.CLASSES = $psh_class_replace(S.CLASSES,porigin_parent,pclassdesc_parent[.PROPERTIES = '
 '[ppropertydesc_no_set]])]',
 '$property_set_origin(S_no_set,ppropertydesc_no_set) = eps',
 'ppropertydesc_wrong_key = ppropertydesc[.KEY = $ptascii("wrong")]',
 'S_wrong_key = S[.CLASSES = $psh_class_replace(S.CLASSES,porigin_parent,pclassdesc_parent[.PROPERTIES = '
 '[ppropertydesc_wrong_key]])]',
 '$property_set_origin(S_wrong_key,ppropertydesc_wrong_key) = eps',
 'S_trait = S[.CLASSES = $psh_class_replace(S.CLASSES,porigin_parent,pclassdesc_parent[.KIND = "trait"])]',
 '$property_set_origin(S_trait,ppropertydesc) = eps',
 'S_parented = S[.CLASSES = $psh_class_replace(S.CLASSES,porigin_parent,pclassdesc_parent[.PARENT = '
 '(pclassdesc_child.NAME)])]',
 '$property_set_origin(S_parented,ppropertydesc) = eps',
 'phpType16_explicit = SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) phpType18_group (BOOLEAN false) (BOOLEAN false) '
 '(NExprVariable (BYTES text_set) metadata_set) ABSENT (SEQUENCE eps) metadata_hook])',
 '$property_set_parameters(phpType16_explicit)',
 'phpType38_explicit = NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook phpType16_explicit '
 'phpType39_hook metadata_hook',
 'pcnode_group_explicit = NStmtProperty phpType14_group phpType24_group phpType18_group phpType56_group (SEQUENCE '
 '([phpType38_explicit])) metadata_group',
 'S_explicit = S[.SOURCES = ([pcunit_source[.OCCURRENCES = '
 '$psh_replace($psh_replace(pcunit_source.OCCURRENCES,pcpath_hook,phpType38_explicit),pcpath_group,pcnode_group_explicit)]])]',
 '$property_set_origin(S_explicit,ppropertydesc) = eps',
 'phpType38_virtual = NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook phpType16_hook '
 '(SEQUENCE eps) metadata_hook',
 'pcnode_group_virtual = NStmtProperty phpType14_group phpType24_group phpType18_group phpType56_group (SEQUENCE '
 '([phpType38_virtual])) metadata_group',
 'S_virtual = S[.SOURCES = ([pcunit_source[.OCCURRENCES = '
 '$psh_replace($psh_replace(pcunit_source.OCCURRENCES,pcpath_hook,phpType38_virtual),pcpath_group,pcnode_group_virtual)]])]',
 '$property_set_origin(S_virtual,ppropertydesc) = eps',
 'S_call_denied = S_call[.CURRENT = (pcallcontext_writer[.LEXICAL_CLASS = eps])]',
 '$property_set_access_allowed(S_call_denied,ppropertyhook) = false /\\ '
 '$property_set_pending_call(S_call_denied,ppropertyhook) = false /\\ $call_task_valid(S_call_denied,CALL_ARGS '
 '(PROPERTY_SET_TARGET ppropertyhook) eps 1 ([KNOWN (PINT 20)]) (porigin_site) 11) = false',
 'S_frame_denied = S_entered[.FRAMES = (pframe_set[.CONTEXT = (pcallcontext_writer[.LEXICAL_CLASS = eps])]) :: '
 'pframe_caller*]',
 '$property_set_access_allowed(S_frame_denied[.CURRENT = (pcallcontext_writer[.LEXICAL_CLASS = eps])],ppropertyhook) = '
 'false /\\ $property_set_frame(S_frame_denied,pcallcontext_set,pframe_set[.CONTEXT = '
 '(pcallcontext_writer[.LEXICAL_CLASS = eps])],ppropertyhook) = false',
 'S_result_denied = S_return[.CURRENT = (pcallcontext_writer[.LEXICAL_CLASS = eps])]',
 '$property_set_tail(S_result_denied,ppropertyhook,S_result_denied.TODO) = false',
 'S_indirect_allowed = $property_instance_indirect_check(S,n_child,ppropertydesc.KEY,false,11)',
 'S_indirect_allowed.COMPLETION = UNSUPPORTED "set hook indirect access"',
 'ppropertydesc_no_final = ppropertydesc[.FINAL = false]',
 'S_no_final = S[.CLASSES = $psh_class_replace(S.CLASSES,porigin_parent,pclassdesc_parent[.PROPERTIES = '
 '[ppropertydesc_no_final]])]',
 '$ppproperty_final(513) /\\ $property_set_origin(S_no_final,ppropertydesc_no_final) = eps',
 'S_explicit_final = S[.SOURCES = ([pcunit_source[.OCCURRENCES = '
 '$psh_replace(pcunit_source.OCCURRENCES,pcpath_group,NStmtProperty phpType14_group (INTEGER 545) phpType18_group '
 'phpType56_group phpType37_group metadata_group)]])]',
 '$ppproperty_final(545) /\\ $ppproperty_set_visibility(545) = (PROPERTY_PRIVATE) /\\ '
 '$property_set_origin(S_explicit_final,ppropertydesc) = eps',
 'ppropertydesc_protected_final = ppropertydesc[.SETVISIBILITY = (PROPERTY_PROTECTED)]',
 'S_protected_final = S[.CLASSES = $psh_class_replace(S.CLASSES,porigin_parent,pclassdesc_parent[.PROPERTIES = '
 '[ppropertydesc_protected_final]])][.SOURCES = ([pcunit_source[.OCCURRENCES = '
 '$psh_replace(pcunit_source.OCCURRENCES,pcpath_group,NStmtProperty phpType14_group (INTEGER 257) phpType18_group '
 'phpType56_group phpType37_group metadata_group)]])]',
 '~$ppproperty_final(257) /\\ $ppproperty_set_visibility(257) = ppropertydesc_protected_final.SETVISIBILITY /\\ '
 '$property_set_origin(S_protected_final,ppropertydesc_protected_final) = eps',
 '$property_set_access_allowed(S[.CURRENT = (pcallcontext_writer[.LEXICAL_CLASS = (porigin_child)])],ppropertyhook) = '
 'false',
 '$ppproperty_inherit_message(pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc,ppropertydesc[.TYPE = '
 '([(PTBRANCH ([PTBUILTIN "string"]))])]) = ($ptascii("Cannot override final property PrivateSetterParent80::$value"))']

ERROR_DERIVED = ['$property_set_access_allowed(S[.CURRENT = (pcallcontext_denied[.CALLED_CLASS = '
 '(porigin_parent)])],ppropertyhook_denied) = false',
 'S_call_forged = S_global[.TODO = (CALL_ARGS (PROPERTY_SET_TARGET ppropertyhook_global) eps 1 ([KNOWN (PARRAY '
 'n_array_global)]) (porigin_site_global) 32) :: (PROPERTY_SET_RESULT ppropertyhook_global (PARRAY n_array_global)) :: '
 'ptask_global*][.ORIGIN = (porigin_site_global)][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
 '$property_set_valid(S_call_forged,ppropertyhook_global) /\\ '
 '$property_set_function(S_call_forged,ppropertyhook_global) = (pfunction_hook)',
 '$property_set_access_allowed(S_call_forged,ppropertyhook_global) = false /\\ '
 '$property_set_pending_call(S_call_forged,ppropertyhook_global) = false /\\ $call_task_valid(S_call_forged,CALL_ARGS '
 '(PROPERTY_SET_TARGET ppropertyhook_global) eps 1 ([KNOWN (PARRAY n_array_global)]) (porigin_site_global) 32) = false',
 '$property_set_tail(S_call_forged,ppropertyhook_global,[(PROPERTY_SET_RESULT ppropertyhook_global (PARRAY '
 'n_array_global))]) = false',
 'S_indirect = $property_instance_indirect_check(S_global,n_child,ppropertydesc.KEY,false,32)',
 'ptbytes_indirect = $ptascii("Cannot indirectly modify private(set) property PrivateSetterParent80::$value from '
 'global scope")',
 'S_indirect.COMPLETION = THROWN "Error" ptbytes_indirect 32',
 '$property_set_denied_plan(S_global[.RESULT = KNOWN (PINT 20)]) = (ppropertyhook_global)']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--group', choices=['receive', 'errors'], required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'private_set_backed_hook_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    clauses, negatives, case_index, start_stage = {
        'receive': (RECEIVE, DERIVED, 0, 0),
        'errors': (ERRORS, ERROR_DERIVED, 0, 1),
    }[args.group]
    selections = [(args.group, clauses, negatives)]
    cases = [data['cases'][case_index]]
    sources = [HERE / 'private-set-backed-hook.php']
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
    out = Path(tempfile.mkdtemp(prefix='private-set-backed-hook-protocol-', dir=ROOT / '.tools'))
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
                     'S_found = $psh_seek(S_initial,' + str(start_stage) + ',1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            content += '\ndec $psh_' + name + '() : bool\ndef $psh_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $psh_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = (' + ' /\\ '.join('$psh_' + name + '()' for name, _, _ in selections) + ')\n'
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
