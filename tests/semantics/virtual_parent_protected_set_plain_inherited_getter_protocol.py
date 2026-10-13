"""Check virtual inherited getters and protected setter scopes at genuine source states."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()



PREFIX = ('dec $psp_replace(pcoccurrence*,pcpath,pcnode) : pcoccurrence*\n'
 'def $psp_replace(eps,pcpath,pcnode) = eps\n'
 'def $psp_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath '
 'pcnode) :: pcoccurrence*\n'
 'def $psp_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE '
 'pcpath_other pcnode_old) :: $psp_replace(pcoccurrence*,pcpath,pcnode)\n'
 '  -- if pcpath_other =/= pcpath\n'
 'dec $psp_stage(pstate,nat) : bool\n'
 'def $psp_stage(S,0) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n'
 '  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n'
 '  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n'
 '  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n'
 '  -- if $ptlc(pclassdesc.NAME) = $ptascii("protectedsetplainchild60")\n'
 'def $psp_stage(S,1) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.TODO = (ASSIGN_ARRAY pbase 40 b) :: ptask*\n'
 '  -- if S.RESULT = KNOWN (PINT 999)\n'
 'def $psp_stage(S,2) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.TODO = (ASSIGN_ARRAY pbase 22 b) :: ptask*\n'
 '  -- if S.RESULT = KNOWN (PINT 300)\n'
 'def $psp_stage(S,3) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.TODO = (ASSIGN_ARRAY pbase 13 b) :: ptask*\n'
 '  -- if S.RESULT = KNOWN (PINT 400)\n'
 'def $psp_stage(S,4) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n'
 '  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n'
 '  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n'
 '  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n'
 '  -- if $ptlc(pclassdesc.NAME) = $ptascii("protectedsetplaingrand60")\n'
 '  -- if $objectprops_at(S.OBJECTPROPS,ppropertyhook.OBJECT) = (ppropertyslot*)\n'
 '  -- if $property_slot_at(ppropertyslot*,$ptascii("value")) = (ppropertyslot_value)\n'
 '  -- if ppropertyslot_value.STATE = PROP_VALUE (DIRECT (PINT 300))\n'
 'def $psp_stage(S,5) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n'
 '  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n'
 '  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n'
 '  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n'
 '  -- if $ptlc(pclassdesc.NAME) = $ptascii("protectedsetplaingrand60")\n'
 '  -- if $objectprops_at(S.OBJECTPROPS,ppropertyhook.OBJECT) = (ppropertyslot*)\n'
 '  -- if $property_slot_at(ppropertyslot*,$ptascii("value")) = (ppropertyslot_value)\n'
 '  -- if ppropertyslot_value.STATE = PROP_VALUE (DIRECT (PINT 400))\n'
 'def $psp_stage(S,7) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*\n'
 'def $psp_stage(S,n) = false -- otherwise\n'
 '\n'
 'dec $psp_seek(pstate,nat,nat) : pstate\n'
 'def $psp_seek(S,n_stage,n) = S\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if $psp_stage(S,n_stage) \\/ n = 0\n'
 'def $psp_seek(S,n_stage,n) = $psp_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if ~$psp_stage(S,n_stage) /\\ $(n > 0)\n'
 'def $psp_seek(S,n_stage,n) = $psp_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
 '  -- if $throwable_pending(S.COMPLETION) /\\ $(n > 0)\n'
 'def $psp_seek(S,n_stage,n) = S -- otherwise\n'
 'dec $psp_after(pstate,pstate) : pstate\n'
 'def $psp_after(S,S_next) = '
 '$gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))\n'
 'dec $psp_guard(pstate) : bool\n'
 'def $psp_guard(S) = ($call_descriptors_valid(S) /\\ $declaration_history_valid(S) /\\ '
 '$property_state_valid(S) /\\ $heap_valid($heap_prune($heap_graph(S))))\n'
 'dec $psp_class_replace(pclassdesc*,porigin,pclassdesc) : pclassdesc*\n'
 'def $psp_class_replace(eps,porigin,pclassdesc) = eps\n'
 'def $psp_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_new :: '
 'pclassdesc*\n'
 '  -- if pclassdesc_old.ORIGIN = porigin\n'
 'def $psp_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_old :: '
 '$psp_class_replace(pclassdesc*,porigin,pclassdesc_new)\n'
 '  -- if pclassdesc_old.ORIGIN =/= porigin\n'
 'dec $psp_link_replace(pclasslink*,porigin,pclassparent) : pclasslink*\n'
 'def $psp_link_replace(eps,porigin,pclassparent) = eps\n'
 'def $psp_link_replace((CLASSLINK porigin pclassparent_old) :: pclasslink*,porigin,pclassparent) = '
 '(CLASSLINK porigin pclassparent) :: pclasslink*\n'
 'def $psp_link_replace((CLASSLINK porigin_other pclassparent_old) :: pclasslink*,porigin,pclassparent) = '
 '(CLASSLINK porigin_other pclassparent_old) :: $psp_link_replace(pclasslink*,porigin,pclassparent)\n'
 '  -- if porigin_other =/= porigin\n')

COMMON = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("ProtectedSetPlainParent60"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ProtectedSetPlainBridge60"))) = (porigin_bridge)',
 '$class_at(S.CLASSES,porigin_bridge) = (pclassdesc_bridge)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ProtectedSetPlainChild60"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ProtectedSetPlainGrand60"))) = (porigin_grand)',
 '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
 'pclassdesc_parent.PARENT = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_parent) = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_bridge) = (SOURCE_PARENT porigin_parent) /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_bridge) /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_child)',
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ |pclassdesc_child.PROPERTIES| = 1 /\\ pclassdesc_bridge.PROPERTIES '
 '= eps /\\ pclassdesc_grand.PROPERTIES = eps',
 'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
 'ppropertydesc_parent.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ ppropertydesc_child.TYPE = '
 'ppropertydesc_parent.TYPE /\\ $property_default_state(S,ppropertydesc_parent) = (PROP_INITIAL) /\\ '
 '$property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT (PINT 200)))',
 '$property_layout(S,porigin_bridge,|S.CLASSES|) = [ppropertydesc_parent] /\\ '
 '$property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_child]',
 '$property_hook_origin(S,ppropertydesc_parent) = (porigin_hook_parent)',
 '$property_hook_origin(S,ppropertydesc_child) = eps /\\ '
 '~$property_hook_override_backed(S,ppropertydesc_parent) /\\ '
 '~$property_hook_inherited_backing(S,ppropertydesc_parent) /\\ '
 '~$property_hook_ordinary_backing(S,ppropertydesc_parent,|S.CLASSES|) /\\ '
 '$property_hook_virtual(S,ppropertydesc_parent) /\\ '
 '$property_hook_virtual_chain(S,ppropertydesc_parent,|S.CLASSES|) /\\ '
 '~$property_hook_virtual(S,ppropertydesc_child)',
 '$property_hook_getter(S,ppropertydesc_child) = (ppropertydesc_parent) /\\ '
 '$property_hook_effective_origin(S,ppropertydesc_child) = (porigin_hook_parent) /\\ '
 '$property_hook_plain_getter_walk(S,ppropertydesc_child,|S.CLASSES|) = (ppropertydesc_parent)',
 '$property_hook_plain_edge(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) /\\ '
 '$property_hook_plain_over_backed(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) /\\ '
 '$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_override_shape(S,ppropertydesc_parent,ppropertydesc_child) /\\ $psp_guard(S)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("parentRead")) = (pmethoddesc_read)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
 '$method_named(pclassdesc_child.METHODS,$ptascii("answer")) = (pmethoddesc_child_answer)',
 '$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
 'pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.OWNER = porigin_parent /\\ '
 'pmethoddesc_child_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_grand_answer.VISIBILITY = '
 'PROPERTY_PRIVATE /\\ pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_child_answer.FUNCTION.ORIGIN /\\ '
 'pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_grand_answer.FUNCTION.ORIGIN',
 '$origin_node(S.SOURCES,porigin_hook_parent) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook '
 'phpType11_hook phpType16_hook phpType39_hook metadata_hook)',
 '~$hook_body_backed(phpType39_hook,ppropertydesc_parent.NAME) /\\ ppropertydesc_parent.DEFAULT = '
 'PROP_UNINITIALIZED',
 'ppropertydesc_child.ORIGIN = PORIGIN n_child pcpath_child',
 'pcpath_child_group = pcpath_child[0:$nabs($(|pcpath_child| - 2))]',
 '$origin_node(S.SOURCES,PORIGIN n_child pcpath_child_group) = (NStmtProperty phpType14_child (INTEGER '
 'flags_child) phpType18_child phpType56_child phpType37_child metadata_child)',
 'phpType14_child = SEQUENCE eps /\\ phpType37_child = SEQUENCE eps /\\ flags_child = 257',
 'S_global = $global_table_view(S)',
 '$lookup(S_global.ENV,$ptascii("parent")) = (n_parent_cell)',
 'S_global.STORE[n_parent_cell] = DEFINED (POBJECT n_parent)',
 'S_global.OBJECTS[n_parent] = INSTANCE porigin_parent /\\ $objectprops_at(S_global.OBJECTPROPS,n_parent) = '
 '(eps)',
 'ppropertydesc_parent.SETVISIBILITY = eps /\\ ppropertydesc_child.SETVISIBILITY = (PROPERTY_PROTECTED) /\\ '
 '~ppropertydesc_child.FINAL',
 '$property_hook_plain_protected_set_parent(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|)',
 '$trait_property_source_fast_equal(S,ppropertydesc_parent,ppropertydesc_child)',
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) '
 '= eps']

CONTROLS = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("ProtectedSetPlainParent60"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ProtectedSetPlainBridge60"))) = (porigin_bridge)',
 '$class_at(S.CLASSES,porigin_bridge) = (pclassdesc_bridge)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ProtectedSetPlainChild60"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ProtectedSetPlainGrand60"))) = (porigin_grand)',
 '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
 'pclassdesc_parent.PARENT = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_parent) = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_bridge) = (SOURCE_PARENT porigin_parent) /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_bridge) /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_child)',
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ |pclassdesc_child.PROPERTIES| = 1 /\\ pclassdesc_bridge.PROPERTIES '
 '= eps /\\ pclassdesc_grand.PROPERTIES = eps',
 'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
 'ppropertydesc_parent.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ ppropertydesc_child.TYPE = '
 'ppropertydesc_parent.TYPE /\\ $property_default_state(S,ppropertydesc_parent) = (PROP_INITIAL) /\\ '
 '$property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT (PINT 200)))',
 '$property_layout(S,porigin_bridge,|S.CLASSES|) = [ppropertydesc_parent] /\\ '
 '$property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_child]',
 '$property_hook_origin(S,ppropertydesc_parent) = (porigin_hook_parent)',
 '$property_hook_origin(S,ppropertydesc_child) = eps /\\ '
 '~$property_hook_override_backed(S,ppropertydesc_parent) /\\ '
 '~$property_hook_inherited_backing(S,ppropertydesc_parent) /\\ '
 '~$property_hook_ordinary_backing(S,ppropertydesc_parent,|S.CLASSES|) /\\ '
 '$property_hook_virtual(S,ppropertydesc_parent) /\\ '
 '$property_hook_virtual_chain(S,ppropertydesc_parent,|S.CLASSES|) /\\ '
 '~$property_hook_virtual(S,ppropertydesc_child)',
 '$property_hook_getter(S,ppropertydesc_child) = (ppropertydesc_parent) /\\ '
 '$property_hook_effective_origin(S,ppropertydesc_child) = (porigin_hook_parent) /\\ '
 '$property_hook_plain_getter_walk(S,ppropertydesc_child,|S.CLASSES|) = (ppropertydesc_parent)',
 '$property_hook_plain_edge(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) /\\ '
 '$property_hook_plain_over_backed(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) /\\ '
 '$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_override_shape(S,ppropertydesc_parent,ppropertydesc_child) /\\ $psp_guard(S)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("parentRead")) = (pmethoddesc_read)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
 '$method_named(pclassdesc_child.METHODS,$ptascii("answer")) = (pmethoddesc_child_answer)',
 '$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
 'pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.OWNER = porigin_parent /\\ '
 'pmethoddesc_child_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_grand_answer.VISIBILITY = '
 'PROPERTY_PRIVATE /\\ pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_child_answer.FUNCTION.ORIGIN /\\ '
 'pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_grand_answer.FUNCTION.ORIGIN',
 '$origin_node(S.SOURCES,porigin_hook_parent) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook '
 'phpType11_hook phpType16_hook phpType39_hook metadata_hook)',
 '~$hook_body_backed(phpType39_hook,ppropertydesc_parent.NAME) /\\ ppropertydesc_parent.DEFAULT = '
 'PROP_UNINITIALIZED',
 'ppropertydesc_child.ORIGIN = PORIGIN n_child pcpath_child',
 'pcpath_child_group = pcpath_child[0:$nabs($(|pcpath_child| - 2))]',
 '$origin_node(S.SOURCES,PORIGIN n_child pcpath_child_group) = (NStmtProperty phpType14_child (INTEGER '
 'flags_child) phpType18_child phpType56_child phpType37_child metadata_child)',
 'phpType14_child = SEQUENCE eps /\\ phpType37_child = SEQUENCE eps /\\ flags_child = 257',
 'S_global = $global_table_view(S)',
 '$lookup(S_global.ENV,$ptascii("parent")) = (n_parent_cell)',
 'S_global.STORE[n_parent_cell] = DEFINED (POBJECT n_parent)',
 'S_global.OBJECTS[n_parent] = INSTANCE porigin_parent /\\ $objectprops_at(S_global.OBJECTPROPS,n_parent) = '
 '(eps)',
 'ppropertydesc_parent.SETVISIBILITY = eps /\\ ppropertydesc_child.SETVISIBILITY = (PROPERTY_PROTECTED) /\\ '
 '~ppropertydesc_child.FINAL',
 '$property_hook_plain_protected_set_parent(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|)',
 '$trait_property_source_fast_equal(S,ppropertydesc_parent,ppropertydesc_child)',
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) '
 '= eps',
 'S.CURRENT = (pcallcontext_hook)',
 'pcallcontext_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook',
 'S.FRAMES = pframe_hook :: pframe_tail*',
 'S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin_child',
 'ppropertyhook.PROPERTY = ppropertydesc_child.ORIGIN /\\ ppropertyhook.HOOK = porigin_hook_parent /\\ '
 'pcallcontext_hook.FUNCTION = porigin_hook_parent /\\ pcallcontext_hook.RECEIVER = (ppropertyhook.OBJECT)',
 'pcallcontext_hook.LEXICAL_CLASS = (porigin_parent) /\\ pcallcontext_hook.CALLED_CLASS = (porigin_child)',
 '$property_hook_function(S,ppropertyhook) = (pfunction_hook)',
 'pfunction_hook.NAME = pclassdesc_parent.NAME ++ $ptascii("::$value::get") /\\ pfunction_hook.SIGNATURE = '
 '{PARAMETERS eps, RETURNS ppropertydesc_parent.TYPE, BYREF false} /\\ pfunction_hook.LINE = 4',
 '$property_effective_desc(S,ppropertyhook.OBJECT,$ptascii("value")) = (ppropertydesc_child)',
 '$objectprops_at(S.OBJECTPROPS,ppropertyhook.OBJECT) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME '
 'ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 200)) }])',
 '~$property_hook_backing(S,ppropertyhook.OBJECT,ppropertydesc_child) /\\ '
 '~$property_hook_backing(S,ppropertyhook.OBJECT,ppropertydesc_parent)',
 '$trace_context_class(S,pcallcontext_hook) = (pclassdesc_parent.NAME) /\\ '
 '$trace_context_function(S,pcallcontext_hook) = $ptascii("$value::get") /\\ '
 '$trace_context_type(S,pcallcontext_hook) = ($ptascii("->"))',
 '$property_hook_frame(S,pcallcontext_hook,pframe_hook,ppropertyhook)',
 '$psp_guard(S)',
 '$psp_stage(S,0)']

DENIED = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("ProtectedSetPlainParent60"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ProtectedSetPlainBridge60"))) = (porigin_bridge)',
 '$class_at(S.CLASSES,porigin_bridge) = (pclassdesc_bridge)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ProtectedSetPlainChild60"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ProtectedSetPlainGrand60"))) = (porigin_grand)',
 '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
 'pclassdesc_parent.PARENT = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_parent) = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_bridge) = (SOURCE_PARENT porigin_parent) /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_bridge) /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_child)',
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ |pclassdesc_child.PROPERTIES| = 1 /\\ pclassdesc_bridge.PROPERTIES '
 '= eps /\\ pclassdesc_grand.PROPERTIES = eps',
 'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
 'ppropertydesc_parent.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ ppropertydesc_child.TYPE = '
 'ppropertydesc_parent.TYPE /\\ $property_default_state(S,ppropertydesc_parent) = (PROP_INITIAL) /\\ '
 '$property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT (PINT 200)))',
 '$property_layout(S,porigin_bridge,|S.CLASSES|) = [ppropertydesc_parent] /\\ '
 '$property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_child]',
 '$property_hook_origin(S,ppropertydesc_parent) = (porigin_hook_parent)',
 '$property_hook_origin(S,ppropertydesc_child) = eps /\\ '
 '~$property_hook_override_backed(S,ppropertydesc_parent) /\\ '
 '~$property_hook_inherited_backing(S,ppropertydesc_parent) /\\ '
 '~$property_hook_ordinary_backing(S,ppropertydesc_parent,|S.CLASSES|) /\\ '
 '$property_hook_virtual(S,ppropertydesc_parent) /\\ '
 '$property_hook_virtual_chain(S,ppropertydesc_parent,|S.CLASSES|) /\\ '
 '~$property_hook_virtual(S,ppropertydesc_child)',
 '$property_hook_getter(S,ppropertydesc_child) = (ppropertydesc_parent) /\\ '
 '$property_hook_effective_origin(S,ppropertydesc_child) = (porigin_hook_parent) /\\ '
 '$property_hook_plain_getter_walk(S,ppropertydesc_child,|S.CLASSES|) = (ppropertydesc_parent)',
 '$property_hook_plain_edge(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) /\\ '
 '$property_hook_plain_over_backed(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) /\\ '
 '$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_override_shape(S,ppropertydesc_parent,ppropertydesc_child) /\\ $psp_guard(S)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("parentRead")) = (pmethoddesc_read)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
 '$method_named(pclassdesc_child.METHODS,$ptascii("answer")) = (pmethoddesc_child_answer)',
 '$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
 'pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.OWNER = porigin_parent /\\ '
 'pmethoddesc_child_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_grand_answer.VISIBILITY = '
 'PROPERTY_PRIVATE /\\ pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_child_answer.FUNCTION.ORIGIN /\\ '
 'pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_grand_answer.FUNCTION.ORIGIN',
 '$origin_node(S.SOURCES,porigin_hook_parent) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook '
 'phpType11_hook phpType16_hook phpType39_hook metadata_hook)',
 '~$hook_body_backed(phpType39_hook,ppropertydesc_parent.NAME) /\\ ppropertydesc_parent.DEFAULT = '
 'PROP_UNINITIALIZED',
 'ppropertydesc_child.ORIGIN = PORIGIN n_child pcpath_child',
 'pcpath_child_group = pcpath_child[0:$nabs($(|pcpath_child| - 2))]',
 '$origin_node(S.SOURCES,PORIGIN n_child pcpath_child_group) = (NStmtProperty phpType14_child (INTEGER '
 'flags_child) phpType18_child phpType56_child phpType37_child metadata_child)',
 'phpType14_child = SEQUENCE eps /\\ phpType37_child = SEQUENCE eps /\\ flags_child = 257',
 'S_global = $global_table_view(S)',
 '$lookup(S_global.ENV,$ptascii("parent")) = (n_parent_cell)',
 'S_global.STORE[n_parent_cell] = DEFINED (POBJECT n_parent)',
 'S_global.OBJECTS[n_parent] = INSTANCE porigin_parent /\\ $objectprops_at(S_global.OBJECTPROPS,n_parent) = '
 '(eps)',
 'ppropertydesc_parent.SETVISIBILITY = eps /\\ ppropertydesc_child.SETVISIBILITY = (PROPERTY_PROTECTED) /\\ '
 '~ppropertydesc_child.FINAL',
 '$property_hook_plain_protected_set_parent(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|)',
 '$trait_property_source_fast_equal(S,ppropertydesc_parent,ppropertydesc_child)',
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) '
 '= eps',
 '$psp_stage(S,1)',
 'S.TODO = (ASSIGN_ARRAY pbase_write z_write b_write) :: ptask_write*',
 '$lookup(S_global.ENV,$ptascii("grand")) = (n_grand_cell)',
 'S_global.STORE[n_grand_cell] = DEFINED (POBJECT n_grand)',
 'S.OBJECTS[n_grand] = INSTANCE porigin_grand',
 '$objectprops_at(S.OBJECTPROPS,n_grand) = ([{DECL (ppropertydesc_child.ORIGIN), NAME '
 'ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 200))}])',
 'S.CURRENT = eps /\\ S.RESULT = KNOWN (PINT 999) /\\ z_write = 40 /\\ $property_pending_base(pbase_write) '
 '/\\ $call_task_valid(S,ASSIGN_ARRAY pbase_write z_write b_write)',
 '$property_instance_set_desc(S,n_grand,$ptascii("value")) = (ppropertydesc_child)',
 '~$class_static_set_allowed(S,ppropertydesc_child) /\\ $property_set_denied(S,n_grand,$ptascii("value")) '
 '/\\ $psp_guard(S)',
 'ptbytes_denied = $ptascii("Cannot modify protected(set) property ProtectedSetPlainChild60::$value from '
 'global scope")',
 '$class_static_set_message(S,ppropertydesc_child,$ptascii("modify")) = ptbytes_denied',
 'PhpStep: S ~> S_denied_raw',
 'S_denied_raw.COMPLETION = THROWN "Error" ptbytes_denied 40 /\\ S_denied_raw.EVENTS = S.EVENTS',
 '$objectprops_at(S_denied_raw.OBJECTPROPS,n_grand) = ([{DECL (ppropertydesc_child.ORIGIN), NAME '
 'ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 200))}])',
 'S_denied = $psp_after(S,S_denied_raw)',
 'S_denied.COMPLETION = THROWING n_error',
 '$object_name(S_denied,n_error) = $ptascii("Error")',
 '$throwable_field(S_denied,n_error,"message") = PSTRING ptbytes_denied',
 '$objectprops_at(S_denied.OBJECTPROPS,n_grand) = ([{DECL (ppropertydesc_child.ORIGIN), NAME '
 'ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 200))}])',
 '$psp_guard(S_denied)',
 'S_child_found = $psp_seek(S_denied,2,1000)',
 'S_child_found.COMPLETION = NORMAL \\/ S_child_found.COMPLETION = BUDGET',
 'S_child = S_child_found[.COMPLETION = NORMAL]',
 '$psp_stage(S_child,2)',
 '$objectprops_at(S_child.OBJECTPROPS,n_grand) = ([{DECL (ppropertydesc_child.ORIGIN), NAME '
 'ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 200))}])',
 '$psp_guard(S_child)']

CHILD_WRITE = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("ProtectedSetPlainParent60"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ProtectedSetPlainBridge60"))) = (porigin_bridge)',
 '$class_at(S.CLASSES,porigin_bridge) = (pclassdesc_bridge)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ProtectedSetPlainChild60"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ProtectedSetPlainGrand60"))) = (porigin_grand)',
 '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
 'pclassdesc_parent.PARENT = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_parent) = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_bridge) = (SOURCE_PARENT porigin_parent) /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_bridge) /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_child)',
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ |pclassdesc_child.PROPERTIES| = 1 /\\ pclassdesc_bridge.PROPERTIES '
 '= eps /\\ pclassdesc_grand.PROPERTIES = eps',
 'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
 'ppropertydesc_parent.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ ppropertydesc_child.TYPE = '
 'ppropertydesc_parent.TYPE /\\ $property_default_state(S,ppropertydesc_parent) = (PROP_INITIAL) /\\ '
 '$property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT (PINT 200)))',
 '$property_layout(S,porigin_bridge,|S.CLASSES|) = [ppropertydesc_parent] /\\ '
 '$property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_child]',
 '$property_hook_origin(S,ppropertydesc_parent) = (porigin_hook_parent)',
 '$property_hook_origin(S,ppropertydesc_child) = eps /\\ '
 '~$property_hook_override_backed(S,ppropertydesc_parent) /\\ '
 '~$property_hook_inherited_backing(S,ppropertydesc_parent) /\\ '
 '~$property_hook_ordinary_backing(S,ppropertydesc_parent,|S.CLASSES|) /\\ '
 '$property_hook_virtual(S,ppropertydesc_parent) /\\ '
 '$property_hook_virtual_chain(S,ppropertydesc_parent,|S.CLASSES|) /\\ '
 '~$property_hook_virtual(S,ppropertydesc_child)',
 '$property_hook_getter(S,ppropertydesc_child) = (ppropertydesc_parent) /\\ '
 '$property_hook_effective_origin(S,ppropertydesc_child) = (porigin_hook_parent) /\\ '
 '$property_hook_plain_getter_walk(S,ppropertydesc_child,|S.CLASSES|) = (ppropertydesc_parent)',
 '$property_hook_plain_edge(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) /\\ '
 '$property_hook_plain_over_backed(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) /\\ '
 '$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_override_shape(S,ppropertydesc_parent,ppropertydesc_child) /\\ $psp_guard(S)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("parentRead")) = (pmethoddesc_read)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
 '$method_named(pclassdesc_child.METHODS,$ptascii("answer")) = (pmethoddesc_child_answer)',
 '$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
 'pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.OWNER = porigin_parent /\\ '
 'pmethoddesc_child_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_grand_answer.VISIBILITY = '
 'PROPERTY_PRIVATE /\\ pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_child_answer.FUNCTION.ORIGIN /\\ '
 'pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_grand_answer.FUNCTION.ORIGIN',
 '$origin_node(S.SOURCES,porigin_hook_parent) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook '
 'phpType11_hook phpType16_hook phpType39_hook metadata_hook)',
 '~$hook_body_backed(phpType39_hook,ppropertydesc_parent.NAME) /\\ ppropertydesc_parent.DEFAULT = '
 'PROP_UNINITIALIZED',
 'ppropertydesc_child.ORIGIN = PORIGIN n_child pcpath_child',
 'pcpath_child_group = pcpath_child[0:$nabs($(|pcpath_child| - 2))]',
 '$origin_node(S.SOURCES,PORIGIN n_child pcpath_child_group) = (NStmtProperty phpType14_child (INTEGER '
 'flags_child) phpType18_child phpType56_child phpType37_child metadata_child)',
 'phpType14_child = SEQUENCE eps /\\ phpType37_child = SEQUENCE eps /\\ flags_child = 257',
 'S_global = $global_table_view(S)',
 '$lookup(S_global.ENV,$ptascii("parent")) = (n_parent_cell)',
 'S_global.STORE[n_parent_cell] = DEFINED (POBJECT n_parent)',
 'S_global.OBJECTS[n_parent] = INSTANCE porigin_parent /\\ $objectprops_at(S_global.OBJECTPROPS,n_parent) = '
 '(eps)',
 'ppropertydesc_parent.SETVISIBILITY = eps /\\ ppropertydesc_child.SETVISIBILITY = (PROPERTY_PROTECTED) /\\ '
 '~ppropertydesc_child.FINAL',
 '$property_hook_plain_protected_set_parent(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|)',
 '$trait_property_source_fast_equal(S,ppropertydesc_parent,ppropertydesc_child)',
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) '
 '= eps',
 '$method_named(pclassdesc_child.METHODS,$ptascii("putChild")) = (pmethoddesc_write)',
 'S.CURRENT = (pcallcontext_write)',
 'S.TODO = (ASSIGN_ARRAY pbase_write z_write b_write) :: ptask_write*',
 '$lookup(S_global.ENV,$ptascii("grand")) = (n_grand_cell)',
 'S_global.STORE[n_grand_cell] = DEFINED (POBJECT n_grand)',
 'S.OBJECTS[n_grand] = INSTANCE porigin_grand',
 'pcallcontext_write.FUNCTION = pmethoddesc_write.FUNCTION.ORIGIN /\\ pcallcontext_write.LEXICAL_CLASS = '
 '(porigin_child) /\\ pcallcontext_write.CALLED_CLASS = (porigin_grand) /\\ pcallcontext_write.RECEIVER = '
 '(n_grand)',
 '$objectprops_at(S.OBJECTPROPS,n_grand) = ([{DECL (ppropertydesc_child.ORIGIN), NAME '
 'ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 200))}])',
 '$property_pending_base(pbase_write) /\\ S.RESULT = KNOWN (PINT 300) /\\ z_write = 22 /\\ '
 '$call_task_valid(S,ASSIGN_ARRAY pbase_write z_write b_write) /\\ $psp_guard(S)',
 '$property_instance_set_desc(S,n_grand,$ptascii("value")) = (ppropertydesc_child)',
 '$property_protected_allowed(S,ppropertydesc_child) /\\ $class_static_set_allowed(S,ppropertydesc_child) '
 '/\\ ~$property_set_denied(S,n_grand,$ptascii("value"))',
 'PhpStep: S ~> S_write_raw',
 'S_write_raw.COMPLETION = NORMAL /\\ S_write_raw.RESULT = KNOWN (PINT 300) /\\ S_write_raw.EVENTS = '
 'S.EVENTS /\\ S_write_raw.TODO = ptask_write* /\\ S_write_raw.CURRENT = S.CURRENT',
 '$objectprops_at(S_write_raw.OBJECTPROPS,n_grand) = ([{DECL (ppropertydesc_child.ORIGIN), NAME '
 'ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 300))}])',
 'S_written = $psp_after(S,S_write_raw)',
 '$psp_guard(S_written)',
 'S_entered_found = $psp_seek(S_written,4,1000)',
 'S_entered_found.COMPLETION = NORMAL \\/ S_entered_found.COMPLETION = BUDGET',
 'S_entered = S_entered_found[.COMPLETION = NORMAL]',
 'S_entered.CURRENT = (pcallcontext_hook)',
 'pcallcontext_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook',
 'S_entered.FRAMES = pframe_hook :: pframe_tail*',
 'S_entered.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin_grand',
 'ppropertyhook.PROPERTY = ppropertydesc_child.ORIGIN /\\ ppropertyhook.HOOK = porigin_hook_parent /\\ '
 'pcallcontext_hook.FUNCTION = porigin_hook_parent /\\ pcallcontext_hook.RECEIVER = (ppropertyhook.OBJECT)',
 'pcallcontext_hook.LEXICAL_CLASS = (porigin_parent) /\\ pcallcontext_hook.CALLED_CLASS = (porigin_grand)',
 '$property_hook_function(S_entered,ppropertyhook) = (pfunction_hook)',
 'pfunction_hook.NAME = pclassdesc_parent.NAME ++ $ptascii("::$value::get") /\\ pfunction_hook.SIGNATURE = '
 '{PARAMETERS eps, RETURNS ppropertydesc_parent.TYPE, BYREF false} /\\ pfunction_hook.LINE = 4',
 '$property_effective_desc(S_entered,ppropertyhook.OBJECT,$ptascii("value")) = (ppropertydesc_child)',
 '$objectprops_at(S_entered.OBJECTPROPS,ppropertyhook.OBJECT) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME '
 'ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 300)) }])',
 '~$property_hook_backing(S_entered,ppropertyhook.OBJECT,ppropertydesc_child) /\\ '
 '~$property_hook_backing(S_entered,ppropertyhook.OBJECT,ppropertydesc_parent)',
 '$trace_context_class(S_entered,pcallcontext_hook) = (pclassdesc_parent.NAME) /\\ '
 '$trace_context_function(S_entered,pcallcontext_hook) = $ptascii("$value::get") /\\ '
 '$trace_context_type(S_entered,pcallcontext_hook) = ($ptascii("->"))',
 '$property_hook_frame(S_entered,pcallcontext_hook,pframe_hook,ppropertyhook)',
 '$psp_guard(S_entered)',
 'S_result_found = $psp_seek(S_entered,7,1000)',
 'S_result_found.COMPLETION = NORMAL \\/ S_result_found.COMPLETION = BUDGET',
 'S_result = S_result_found[.COMPLETION = NORMAL]',
 'S_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask_result*',
 'S_result.RESULT = KNOWN (PINT 13) /\\ S_result.CURRENT = eps',
 '$objectprops_at(S_result.OBJECTPROPS,n_grand) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME '
 'ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 300)) }])',
 '$psp_guard(S_result)']

PARENT_WRITE = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("ProtectedSetPlainParent60"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ProtectedSetPlainBridge60"))) = (porigin_bridge)',
 '$class_at(S.CLASSES,porigin_bridge) = (pclassdesc_bridge)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ProtectedSetPlainChild60"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ProtectedSetPlainGrand60"))) = (porigin_grand)',
 '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
 'pclassdesc_parent.PARENT = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_parent) = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_bridge) = (SOURCE_PARENT porigin_parent) /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_bridge) /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_child)',
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ |pclassdesc_child.PROPERTIES| = 1 /\\ pclassdesc_bridge.PROPERTIES '
 '= eps /\\ pclassdesc_grand.PROPERTIES = eps',
 'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
 'ppropertydesc_parent.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ ppropertydesc_child.TYPE = '
 'ppropertydesc_parent.TYPE /\\ $property_default_state(S,ppropertydesc_parent) = (PROP_INITIAL) /\\ '
 '$property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT (PINT 200)))',
 '$property_layout(S,porigin_bridge,|S.CLASSES|) = [ppropertydesc_parent] /\\ '
 '$property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_child]',
 '$property_hook_origin(S,ppropertydesc_parent) = (porigin_hook_parent)',
 '$property_hook_origin(S,ppropertydesc_child) = eps /\\ '
 '~$property_hook_override_backed(S,ppropertydesc_parent) /\\ '
 '~$property_hook_inherited_backing(S,ppropertydesc_parent) /\\ '
 '~$property_hook_ordinary_backing(S,ppropertydesc_parent,|S.CLASSES|) /\\ '
 '$property_hook_virtual(S,ppropertydesc_parent) /\\ '
 '$property_hook_virtual_chain(S,ppropertydesc_parent,|S.CLASSES|) /\\ '
 '~$property_hook_virtual(S,ppropertydesc_child)',
 '$property_hook_getter(S,ppropertydesc_child) = (ppropertydesc_parent) /\\ '
 '$property_hook_effective_origin(S,ppropertydesc_child) = (porigin_hook_parent) /\\ '
 '$property_hook_plain_getter_walk(S,ppropertydesc_child,|S.CLASSES|) = (ppropertydesc_parent)',
 '$property_hook_plain_edge(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) /\\ '
 '$property_hook_plain_over_backed(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) /\\ '
 '$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_override_shape(S,ppropertydesc_parent,ppropertydesc_child) /\\ $psp_guard(S)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("parentRead")) = (pmethoddesc_read)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
 '$method_named(pclassdesc_child.METHODS,$ptascii("answer")) = (pmethoddesc_child_answer)',
 '$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
 'pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.OWNER = porigin_parent /\\ '
 'pmethoddesc_child_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_grand_answer.VISIBILITY = '
 'PROPERTY_PRIVATE /\\ pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_child_answer.FUNCTION.ORIGIN /\\ '
 'pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_grand_answer.FUNCTION.ORIGIN',
 '$origin_node(S.SOURCES,porigin_hook_parent) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook '
 'phpType11_hook phpType16_hook phpType39_hook metadata_hook)',
 '~$hook_body_backed(phpType39_hook,ppropertydesc_parent.NAME) /\\ ppropertydesc_parent.DEFAULT = '
 'PROP_UNINITIALIZED',
 'ppropertydesc_child.ORIGIN = PORIGIN n_child pcpath_child',
 'pcpath_child_group = pcpath_child[0:$nabs($(|pcpath_child| - 2))]',
 '$origin_node(S.SOURCES,PORIGIN n_child pcpath_child_group) = (NStmtProperty phpType14_child (INTEGER '
 'flags_child) phpType18_child phpType56_child phpType37_child metadata_child)',
 'phpType14_child = SEQUENCE eps /\\ phpType37_child = SEQUENCE eps /\\ flags_child = 257',
 'S_global = $global_table_view(S)',
 '$lookup(S_global.ENV,$ptascii("parent")) = (n_parent_cell)',
 'S_global.STORE[n_parent_cell] = DEFINED (POBJECT n_parent)',
 'S_global.OBJECTS[n_parent] = INSTANCE porigin_parent /\\ $objectprops_at(S_global.OBJECTPROPS,n_parent) = '
 '(eps)',
 'ppropertydesc_parent.SETVISIBILITY = eps /\\ ppropertydesc_child.SETVISIBILITY = (PROPERTY_PROTECTED) /\\ '
 '~ppropertydesc_child.FINAL',
 '$property_hook_plain_protected_set_parent(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|)',
 '$trait_property_source_fast_equal(S,ppropertydesc_parent,ppropertydesc_child)',
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) '
 '= eps',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("putParent")) = (pmethoddesc_write)',
 'S.CURRENT = (pcallcontext_write)',
 'S.TODO = (ASSIGN_ARRAY pbase_write z_write b_write) :: ptask_write*',
 '$lookup(S_global.ENV,$ptascii("grand")) = (n_grand_cell)',
 'S_global.STORE[n_grand_cell] = DEFINED (POBJECT n_grand)',
 'S.OBJECTS[n_grand] = INSTANCE porigin_grand',
 'pcallcontext_write.FUNCTION = pmethoddesc_write.FUNCTION.ORIGIN /\\ pcallcontext_write.LEXICAL_CLASS = '
 '(porigin_parent) /\\ pcallcontext_write.CALLED_CLASS = (porigin_grand) /\\ pcallcontext_write.RECEIVER = '
 '(n_grand)',
 '$objectprops_at(S.OBJECTPROPS,n_grand) = ([{DECL (ppropertydesc_child.ORIGIN), NAME '
 'ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 300))}])',
 '$property_pending_base(pbase_write) /\\ S.RESULT = KNOWN (PINT 400) /\\ z_write = 13 /\\ '
 '$call_task_valid(S,ASSIGN_ARRAY pbase_write z_write b_write) /\\ $psp_guard(S)',
 '$property_instance_set_desc(S,n_grand,$ptascii("value")) = (ppropertydesc_child)',
 '$property_protected_allowed(S,ppropertydesc_child) /\\ $class_static_set_allowed(S,ppropertydesc_child) '
 '/\\ ~$property_set_denied(S,n_grand,$ptascii("value"))',
 'PhpStep: S ~> S_write_raw',
 'S_write_raw.COMPLETION = NORMAL /\\ S_write_raw.RESULT = KNOWN (PINT 400) /\\ S_write_raw.EVENTS = '
 'S.EVENTS /\\ S_write_raw.TODO = ptask_write* /\\ S_write_raw.CURRENT = S.CURRENT',
 '$objectprops_at(S_write_raw.OBJECTPROPS,n_grand) = ([{DECL (ppropertydesc_child.ORIGIN), NAME '
 'ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 400))}])',
 'S_written = $psp_after(S,S_write_raw)',
 '$psp_guard(S_written)',
 'S_entered_found = $psp_seek(S_written,5,1000)',
 'S_entered_found.COMPLETION = NORMAL \\/ S_entered_found.COMPLETION = BUDGET',
 'S_entered = S_entered_found[.COMPLETION = NORMAL]',
 'S_entered.CURRENT = (pcallcontext_hook)',
 'pcallcontext_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook',
 'S_entered.FRAMES = pframe_hook :: pframe_tail*',
 'S_entered.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin_grand',
 'ppropertyhook.PROPERTY = ppropertydesc_child.ORIGIN /\\ ppropertyhook.HOOK = porigin_hook_parent /\\ '
 'pcallcontext_hook.FUNCTION = porigin_hook_parent /\\ pcallcontext_hook.RECEIVER = (ppropertyhook.OBJECT)',
 'pcallcontext_hook.LEXICAL_CLASS = (porigin_parent) /\\ pcallcontext_hook.CALLED_CLASS = (porigin_grand)',
 '$property_hook_function(S_entered,ppropertyhook) = (pfunction_hook)',
 'pfunction_hook.NAME = pclassdesc_parent.NAME ++ $ptascii("::$value::get") /\\ pfunction_hook.SIGNATURE = '
 '{PARAMETERS eps, RETURNS ppropertydesc_parent.TYPE, BYREF false} /\\ pfunction_hook.LINE = 4',
 '$property_effective_desc(S_entered,ppropertyhook.OBJECT,$ptascii("value")) = (ppropertydesc_child)',
 '$objectprops_at(S_entered.OBJECTPROPS,ppropertyhook.OBJECT) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME '
 'ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 400)) }])',
 '~$property_hook_backing(S_entered,ppropertyhook.OBJECT,ppropertydesc_child) /\\ '
 '~$property_hook_backing(S_entered,ppropertyhook.OBJECT,ppropertydesc_parent)',
 '$trace_context_class(S_entered,pcallcontext_hook) = (pclassdesc_parent.NAME) /\\ '
 '$trace_context_function(S_entered,pcallcontext_hook) = $ptascii("$value::get") /\\ '
 '$trace_context_type(S_entered,pcallcontext_hook) = ($ptascii("->"))',
 '$property_hook_frame(S_entered,pcallcontext_hook,pframe_hook,ppropertyhook)',
 '$psp_guard(S_entered)',
 'S_result_found = $psp_seek(S_entered,7,1000)',
 'S_result_found.COMPLETION = NORMAL \\/ S_result_found.COMPLETION = BUDGET',
 'S_result = S_result_found[.COMPLETION = NORMAL]',
 'S_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask_result*',
 'S_result.RESULT = KNOWN (PINT 13) /\\ S_result.CURRENT = eps',
 '$objectprops_at(S_result.OBJECTPROPS,n_grand) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME '
 'ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 400)) }])',
 '$psp_guard(S_result)']

BACKED = ['ptbytes_message = $ptascii("Set access level of ProtectedSetBackedChild60::$value must be omitted (as in '
 'class ProtectedSetBackedParent60)")',
 'S.COMPLETION = STATICBYTES ptbytes_message 11 /\\ S.EVENTS = eps /\\ S.OBJECTS = eps /\\ S.OBJECTPROPS = '
 'eps',
 'S.CLASSES = [pclassdesc_parent,pclassdesc_bridge,pclassdesc_child]',
 'pclassdesc_parent.NAME = $ptascii("ProtectedSetBackedParent60") /\\ pclassdesc_bridge.NAME = '
 '$ptascii("ProtectedSetBackedBridge60") /\\ pclassdesc_child.NAME = $ptascii("ProtectedSetBackedChild60")',
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ |pclassdesc_child.PROPERTIES| = 1 /\\ pclassdesc_bridge.PROPERTIES '
 '= eps',
 'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
 'ppropertydesc_parent.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ ppropertydesc_child.TYPE = '
 'ppropertydesc_parent.TYPE',
 'ppropertydesc_parent.SETVISIBILITY = eps /\\ ppropertydesc_child.SETVISIBILITY = (PROPERTY_PROTECTED) /\\ '
 '~ppropertydesc_parent.FINAL /\\ ~ppropertydesc_child.FINAL',
 '$property_default_state(S,ppropertydesc_parent) = (PROP_VALUE (DIRECT (PINT 100))) /\\ '
 '$property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT (PINT 200)))',
 '$property_hook_origin(S,ppropertydesc_parent) = (porigin_hook_parent)',
 '$property_hook_origin(S,ppropertydesc_child) = eps /\\ '
 '$property_hook_get_declaration(S,ppropertydesc_child) = eps',
 '$function_at(S.FUNCTIONS,porigin_hook_parent) = (pfunction_hook)',
 'pfunction_hook.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_parent.TYPE, BYREF false} /\\ '
 'pfunction_hook.LINE = 4',
 '$property_layout(S,pclassdesc_bridge.ORIGIN,|S.CLASSES|) = [ppropertydesc_parent]',
 'pclassdesc_parent.PARENT = eps /\\ pclassdesc_bridge.PARENT = (pclassdesc_parent.NAME) /\\ '
 'pclassdesc_child.PARENT = (pclassdesc_bridge.NAME) /\\ pclassdesc_child.LINE = 11',
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_parent.NAME)) = (pclassdesc_parent.ORIGIN) /\\ '
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_bridge.NAME)) = (pclassdesc_bridge.ORIGIN) /\\ '
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_child.NAME)) = eps',
 '$class_link_at(S.LINKEDPARENTS,pclassdesc_parent.ORIGIN) = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,pclassdesc_bridge.ORIGIN) = (SOURCE_PARENT pclassdesc_parent.ORIGIN) /\\ '
 '$class_link_at(S.LINKEDPARENTS,pclassdesc_child.ORIGIN) = eps',
 '$property_hook_override_backed(S,ppropertydesc_parent) /\\ ~$property_hook_virtual(S,ppropertydesc_parent) '
 '/\\ ~$property_hook_virtual_chain(S,ppropertydesc_parent,|S.CLASSES|)',
 '~$property_hook_plain_protected_set_parent(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) /\\ '
 '~$property_hook_plain_edge(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) /\\ '
 '~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child)',
 '$trait_property_source_fast_equal(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '$ppproperty_set_narrowed(ppropertydesc_parent,ppropertydesc_child)',
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) '
 '= (ptbytes_message)',
 '$property_hook_covariance_error_site(S,[ppropertydesc_parent],ppropertydesc_child,ptbytes_message) = eps',
 'S.TODO = eps /\\ S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.ENV = eps /\\ S.ERRORORIGIN = eps /\\ '
 '$declaration_history_valid(S) /\\ $class_links_valid(S)']

DERIVED = ['$property_hook_plain_protected_set_parent(S,ppropertydesc_parent,ppropertydesc_child,0) = false',
 '$property_hook_plain_protected_set_parent(S,ppropertydesc_parent,ppropertydesc_child,1)',
 '$property_hook_plain_getter_walk(S,ppropertydesc_child,0) = eps',
 '$property_hook_plain_getter_walk(S,ppropertydesc_child,1) = eps',
 '$property_hook_plain_getter_walk(S,ppropertydesc_child,2) = eps',
 '$property_hook_plain_getter_walk(S,ppropertydesc_child,3) = (ppropertydesc_parent)',
 'S_parent_link = S[.LINKEDPARENTS = (CLASSLINK porigin_parent (SOURCE_PARENT porigin_parent)) :: '
 'S.LINKEDPARENTS]',
 '~$property_hook_plain_protected_set_parent(S_parent_link,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) '
 '/\\ ~$property_hook_plain_edge(S_parent_link,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|)',
 'S_child_link = S[.LINKEDPARENTS = $psp_link_replace(S.LINKEDPARENTS,porigin_child,SOURCE_PARENT '
 'porigin_child)]',
 '$property_hook_plain_protected_set_parent(S_child_link,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) '
 '/\\ ~$property_hook_plain_edge(S_child_link,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|)',
 'S_bridge_link = S[.LINKEDPARENTS = $psp_link_replace(S.LINKEDPARENTS,porigin_bridge,SOURCE_PARENT '
 'porigin_bridge)]',
 '$property_hook_plain_protected_set_parent(S_bridge_link,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) '
 '/\\ ~$property_hook_plain_over_backed(S_bridge_link,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|)',
 'S_child_own = S[.CLASSES = $psp_class_replace(S.CLASSES,porigin_child,pclassdesc_child[.PROPERTIES = '
 'eps])]',
 '~$property_hook_plain_protected_set_parent(S_child_own,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|)',
 'S_parent_own = S[.CLASSES = $psp_class_replace(S.CLASSES,porigin_parent,pclassdesc_parent[.PROPERTIES = '
 'eps])]',
 '~$property_hook_plain_protected_set_parent(S_parent_own,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|)',
 '~$property_hook_plain_protected_set_parent(S,ppropertydesc_parent[.TYPE = '
 'eps],ppropertydesc_child,|S.CLASSES|)',
 '~$property_hook_plain_protected_set_parent(S,ppropertydesc_parent[.DEFAULT = PROP_LITERAL (PINT '
 '999)],ppropertydesc_child,|S.CLASSES|)',
 '~$property_hook_plain_protected_set_parent(S,ppropertydesc_parent[.VISIBILITY = '
 'PROPERTY_PROTECTED],ppropertydesc_child,|S.CLASSES|)',
 '~$property_hook_plain_protected_set_parent(S,ppropertydesc_parent[.STATIC = '
 'true],ppropertydesc_child,|S.CLASSES|)',
 '~$property_hook_plain_protected_set_parent(S,ppropertydesc_parent[.READONLY = '
 'true],ppropertydesc_child,|S.CLASSES|)',
 '~$property_hook_plain_protected_set_parent(S,ppropertydesc_parent[.FINAL = '
 'true],ppropertydesc_child,|S.CLASSES|)',
 '~$property_hook_plain_protected_set_parent(S,ppropertydesc_parent[.SETVISIBILITY = '
 '(PROPERTY_PROTECTED)],ppropertydesc_child,|S.CLASSES|)',
 '~$property_hook_plain_protected_set_parent(S,ppropertydesc_parent,ppropertydesc_child[.TYPE = '
 'eps],|S.CLASSES|)',
 '~$property_hook_plain_protected_set_parent(S,ppropertydesc_parent,ppropertydesc_child[.TYPE = [PTBRANCH '
 '([PTBUILTIN "mixed"])]],|S.CLASSES|)',
 '~$property_hook_plain_protected_set_parent(S,ppropertydesc_parent,ppropertydesc_child[.DEFAULT = '
 'PROP_LITERAL (PINT 999)],|S.CLASSES|)',
 '~$property_hook_plain_protected_set_parent(S,ppropertydesc_parent,ppropertydesc_child[.VISIBILITY = '
 'PROPERTY_PROTECTED],|S.CLASSES|)',
 '~$property_hook_plain_protected_set_parent(S,ppropertydesc_parent,ppropertydesc_child[.STATIC = '
 'true],|S.CLASSES|)',
 '~$property_hook_plain_protected_set_parent(S,ppropertydesc_parent,ppropertydesc_child[.READONLY = '
 'true],|S.CLASSES|)',
 '~$property_hook_plain_protected_set_parent(S,ppropertydesc_parent,ppropertydesc_child[.FINAL = '
 'true],|S.CLASSES|)',
 '~$property_hook_plain_protected_set_parent(S,ppropertydesc_parent,ppropertydesc_child[.SETVISIBILITY = '
 'eps],|S.CLASSES|)',
 '~$property_hook_plain_protected_set_parent(S,ppropertydesc_parent,ppropertydesc_child[.SETVISIBILITY = '
 '(PROPERTY_PRIVATE)],|S.CLASSES|)',
 'porigin_hook_parent = PORIGIN n_hook pcpath_hook',
 'S.SOURCES = pcunit :: pcunit_tail*',
 'pcunit.ID = n_hook /\\ n_child = n_hook',
 'S_byref = S[.SOURCES = pcunit[.OCCURRENCES = $psp_replace(pcunit.OCCURRENCES,pcpath_hook,NPropertyHook '
 'phpType14_hook phpType24_hook (BOOLEAN true) phpType11_hook phpType16_hook phpType39_hook metadata_hook)] '
 ':: pcunit_tail*]',
 '~$property_hook_plain_protected_set_parent(S_byref,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|)',
 'S_flags = S[.SOURCES = pcunit[.OCCURRENCES = '
 '$psp_replace(pcunit.OCCURRENCES,pcpath_child_group,NStmtProperty phpType14_child (INTEGER 1) '
 'phpType18_child phpType56_child phpType37_child metadata_child)] :: pcunit_tail*]',
 '~$property_hook_plain_protected_set_parent(S_flags,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) '
 '/\\ ~$property_hook_plain_edge(S_flags,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|)',
 'S_child_hooks = S[.SOURCES = pcunit[.OCCURRENCES = '
 '$psp_replace(pcunit.OCCURRENCES,pcpath_child_group,NStmtProperty phpType14_child (INTEGER flags_child) '
 'phpType18_child phpType56_child (SEQUENCE ([NPropertyHook phpType14_hook phpType24_hook phpType4_hook '
 'phpType11_hook phpType16_hook phpType39_hook metadata_hook])) metadata_child)] :: pcunit_tail*]',
 '~$property_hook_plain_protected_set_parent(S_child_hooks,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|)',
 '$property_hook_properties(S,[ppropertydesc_child])',
 '~$property_hook_parent_match(S,ppropertydesc_child,(ppropertydesc_parent)) /\\ '
 '$property_hook_parent_match(S,ppropertydesc_child,(ppropertydesc_child))']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--group', choices=['controls', 'denied', 'child_write', 'parent_write', 'backed'], required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'virtual_parent_protected_set_plain_inherited_getter_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    clauses, negatives, case_index, start_stage = {
        'controls': (CONTROLS, DERIVED, 0, 0),
        'denied': (DENIED, [], 0, 1),
        'child_write': (CHILD_WRITE, [], 0, 2),
        'parent_write': (PARENT_WRITE, [], 0, 3),
        'backed': (BACKED, [], 1, 0),
    }[args.group]
    selections = [(args.group, clauses, negatives)]
    cases = [data['cases'][case_index]]
    sources = [HERE / ['virtual-parent-protected-set-plain-inherited-getter.php', 'virtual-parent-protected-set-plain-inherited-getter-backed.php'][case_index]]
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
    out = Path(tempfile.mkdtemp(prefix='virtual-parent-protected-set-plain-inherited-getter-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    derived = sum(len(row[2]) for row in selections)
    reached = sum((1 if args.group == 'backed' else 5) + len(row[1]) for row in selections)
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
                     'S_found = $psp_seek(S_initial,' + str(start_stage) + ',1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            if args.group == 'backed':
                setup = [setup[0].replace('S_initial =', 'S =', 1)]
            content += '\ndec $psp_' + name + '() : bool\ndef $psp_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $psp_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = (' + ' /\\ '.join('$psp_' + name + '()' for name, _, _ in selections) + ')\n'
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
