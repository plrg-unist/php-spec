"""Check backed-parent to body-unbacked child getter TYPE-presence errors and inherited storage controls."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()
byte_expr = lambda value: '[' + ','.join(str(byte) for byte in value) + ']'



PREFIX = ('dec $bu_replace(pcoccurrence*,pcpath,pcnode) : pcoccurrence*\n'
 'def $bu_replace(eps,pcpath,pcnode) = eps\n'
 'def $bu_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath '
 'pcnode) :: pcoccurrence*\n'
 'def $bu_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE '
 'pcpath_other pcnode_old) :: $bu_replace(pcoccurrence*,pcpath,pcnode)\n'
 '  -- if pcpath_other =/= pcpath\n'
 'dec $bu_output(pevent*) : ptbytes\n'
 'def $bu_output(eps) = eps\n'
 'def $bu_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $bu_output(pevent*)\n'
 'dec $bu_stage(pstate,nat) : bool\n'
 'def $bu_stage(S,0) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if $property_hook_plan(S[.COMPLETION = NORMAL]) = (ppropertyhook)\n'
 '  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n'
 '  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n'
 '  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n'
 '  -- if $ptlc(pclassdesc.NAME) = $ptascii("storagebodychild46")\n'
 'def $bu_stage(S,1) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if $property_hook_plan(S[.COMPLETION = NORMAL]) = (ppropertyhook)\n'
 '  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n'
 '  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n'
 '  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n'
 '  -- if $ptlc(pclassdesc.NAME) = $ptascii("storagebodygrand46")\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if $ptlc(pcallcontext.NAME) = $ptascii("storagebodyparent46::parentread")\n'
 'def $bu_stage(S,2) = true\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if $property_hook_context_kind(pcallcontext)\n'
 'def $bu_stage(S,3) = true\n'
 '  -- if S.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*\n'
 'def $bu_stage(S,4) = true\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if $ptlc(pcallcontext.NAME) = $ptascii("storagebodychild46::answer")\n'
 'def $bu_stage(S,5) = true\n'
 '  -- if S.TODO = (ASSIGN_ARRAY pbase z b) :: ptask*\n'
 '  -- if S.RESULT = KNOWN (PINT 300)\n'
 'def $bu_stage(S,6) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if $property_hook_plan(S[.COMPLETION = NORMAL]) = (ppropertyhook)\n'
 '  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n'
 '  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n'
 '  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n'
 '  -- if $ptlc(pclassdesc.NAME) = $ptascii("storagebodygrand46")\n'
 'def $bu_stage(S,n) = false -- otherwise\n'
 '\n'
 'dec $bu_seek(pstate,nat,nat) : pstate\n'
 'def $bu_seek(S,n_stage,n) = S\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if $bu_stage(S,n_stage) \\/ n = 0\n'
 'def $bu_seek(S,n_stage,n) = $bu_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if ~$bu_stage(S,n_stage) /\\ $(n > 0)\n'
 'def $bu_seek(S,n_stage,n) = $bu_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
 '  -- if $throwable_pending(S.COMPLETION) /\\ $(n > 0)\n'
 'def $bu_seek(S,n_stage,n) = S -- otherwise\n'
 'dec $bu_after(pstate,pstate) : pstate\n'
 'def $bu_after(S,S_next) = '
 '$gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))\n'
 'dec $bu_guard(pstate) : bool\n'
 'def $bu_guard(S) = ($call_descriptors_valid(S) /\\ $declaration_history_valid(S) /\\ '
 '$property_state_valid(S) /\\ $heap_valid($heap_prune($heap_graph(S))))\n')

REMOVE = ['S.COMPLETION = STATICBYTES ($ptascii("Declaration of StorageBodyRemoveChild46::$value::get() must be '
 'compatible with StorageBodyRemoveParent46::$value::get(): int")) 6 /\\ S.EVENTS = eps /\\ S.OBJECTS = eps '
 '/\\ S.OBJECTPROPS = eps',
 'S.CLASSES = [pclassdesc_parent,pclassdesc_child]',
 'pclassdesc_parent.NAME = $ptascii("StorageBodyRemoveParent46") /\\ pclassdesc_child.NAME = '
 '$ptascii("StorageBodyRemoveChild46") /\\ |pclassdesc_parent.PROPERTIES| = 1 /\\ '
 '|pclassdesc_child.PROPERTIES| = 1',
 'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
 'ppropertydesc_parent.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ ppropertydesc_child.TYPE = eps',
 '$property_default_state(S,ppropertydesc_parent) = (PROP_VALUE (DIRECT (PINT 100))) /\\ '
 '$property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT PNULL))',
 '$property_hook_origin(S,ppropertydesc_parent) = (porigin_parent_hook)',
 '$property_hook_origin(S,ppropertydesc_child) = (porigin_child_hook)',
 'porigin_child_hook = PORIGIN n_unit pcpath_child_hook',
 '$function_at(S.FUNCTIONS,porigin_parent_hook) = (pfunction_parent)',
 '$function_at(S.FUNCTIONS,porigin_child_hook) = (pfunction_child)',
 'pfunction_parent.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_parent.TYPE, BYREF false} /\\ '
 'pfunction_child.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_child.TYPE, BYREF false}',
 'pfunction_parent.NAME = pclassdesc_parent.NAME ++ $ptascii("::$value::get") /\\ pfunction_child.NAME = '
 'pclassdesc_child.NAME ++ $ptascii("::$value::get") /\\ pfunction_parent.LINE = 3 /\\ pfunction_child.LINE '
 '= 6',
 '$origin_node(S.SOURCES,porigin_child_hook) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook '
 'phpType11_hook phpType16_hook phpType39_hook metadata_hook)',
 '~$hook_body_backed(phpType39_hook,ppropertydesc_child.NAME) /\\ $source_line(metadata_hook) = 6 /\\ '
 'pclassdesc_child.LINE = 5 /\\ S.ERRORORIGIN = eps /\\ n_unit = 0 /\\ pcpath_child_hook =/= eps',
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_parent.NAME)) = (pclassdesc_parent.ORIGIN) /\\ '
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_child.NAME)) = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,pclassdesc_parent.ORIGIN) = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,pclassdesc_child.ORIGIN) = eps',
 '$property_hook_override_backed(S,ppropertydesc_parent) /\\ '
 '~$property_hook_override_backed(S,ppropertydesc_child) /\\ '
 '~$property_hook_virtual_chain(S,ppropertydesc_parent,|S.CLASSES|)',
 '~$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child)',
 '$property_hook_covariance(S,ppropertydesc_parent,ppropertydesc_child) = PVUNSUPPORTED text_presence',
 'S.TODO = eps /\\ S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.ENV = eps /\\ $declaration_history_valid(S) /\\ '
 '$class_links_valid(S)',
 '$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child)',
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) '
 '= ($ptascii("Declaration of StorageBodyRemoveChild46::$value::get() must be compatible with '
 'StorageBodyRemoveParent46::$value::get(): int"))',
 '$property_hook_covariance_error_site(S,[ppropertydesc_parent],ppropertydesc_child,$ptascii("Declaration of '
 'StorageBodyRemoveChild46::$value::get() must be compatible with StorageBodyRemoveParent46::$value::get(): '
 'int")) = ((porigin_child_hook,6))',
 '$property_hook_get_declaration(S,ppropertydesc_child) = '
 '($ptascii("StorageBodyRemoveChild46::$value::get()"))']

ADD = ['S.COMPLETION = STATICBYTES ($ptascii("Type of StorageBodyAddChild46::$value must be omitted to match the '
 'parent definition in class StorageBodyAddParent46")) 5 /\\ S.EVENTS = eps /\\ S.OBJECTS = eps /\\ '
 'S.OBJECTPROPS = eps',
 'S.CLASSES = [pclassdesc_parent,pclassdesc_child]',
 'pclassdesc_parent.NAME = $ptascii("StorageBodyAddParent46") /\\ pclassdesc_child.NAME = '
 '$ptascii("StorageBodyAddChild46") /\\ |pclassdesc_parent.PROPERTIES| = 1 /\\ |pclassdesc_child.PROPERTIES| '
 '= 1',
 'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
 'ppropertydesc_parent.TYPE = eps /\\ ppropertydesc_child.TYPE = [PTBRANCH ([PTBUILTIN "int"])]',
 '$property_default_state(S,ppropertydesc_parent) = (PROP_VALUE (DIRECT (PINT 100))) /\\ '
 '$property_default_state(S,ppropertydesc_child) = (PROP_INITIAL)',
 '$property_hook_origin(S,ppropertydesc_parent) = (porigin_parent_hook)',
 '$property_hook_origin(S,ppropertydesc_child) = (porigin_child_hook)',
 'porigin_child_hook = PORIGIN n_unit pcpath_child_hook',
 '$function_at(S.FUNCTIONS,porigin_parent_hook) = (pfunction_parent)',
 '$function_at(S.FUNCTIONS,porigin_child_hook) = (pfunction_child)',
 'pfunction_parent.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_parent.TYPE, BYREF false} /\\ '
 'pfunction_child.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_child.TYPE, BYREF false}',
 'pfunction_parent.NAME = pclassdesc_parent.NAME ++ $ptascii("::$value::get") /\\ pfunction_child.NAME = '
 'pclassdesc_child.NAME ++ $ptascii("::$value::get") /\\ pfunction_parent.LINE = 3 /\\ pfunction_child.LINE '
 '= 6',
 '$origin_node(S.SOURCES,porigin_child_hook) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook '
 'phpType11_hook phpType16_hook phpType39_hook metadata_hook)',
 '~$hook_body_backed(phpType39_hook,ppropertydesc_child.NAME) /\\ $source_line(metadata_hook) = 6 /\\ '
 'pclassdesc_child.LINE = 5 /\\ S.ERRORORIGIN = eps /\\ n_unit = 0 /\\ pcpath_child_hook =/= eps',
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_parent.NAME)) = (pclassdesc_parent.ORIGIN) /\\ '
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_child.NAME)) = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,pclassdesc_parent.ORIGIN) = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,pclassdesc_child.ORIGIN) = eps',
 '$property_hook_override_backed(S,ppropertydesc_parent) /\\ '
 '~$property_hook_override_backed(S,ppropertydesc_child) /\\ '
 '~$property_hook_virtual_chain(S,ppropertydesc_parent,|S.CLASSES|)',
 '~$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child)',
 '$property_hook_covariance(S,ppropertydesc_parent,ppropertydesc_child) = PVUNSUPPORTED text_presence',
 'S.TODO = eps /\\ S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.ENV = eps /\\ $declaration_history_valid(S) /\\ '
 '$class_links_valid(S)',
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child)',
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) '
 '= ($ptascii("Type of StorageBodyAddChild46::$value must be omitted to match the parent definition in class '
 'StorageBodyAddParent46"))',
 '$property_hook_covariance_error_site(S,[ppropertydesc_parent],ppropertydesc_child,$ptascii("Type of '
 'StorageBodyAddChild46::$value must be omitted to match the parent definition in class '
 'StorageBodyAddParent46")) = eps',
 '$property_hook_get_declaration(S,ppropertydesc_parent) = '
 '($ptascii("StorageBodyAddParent46::$value::get()"))']

DERIVED = ['~$property_hook_missing_return_parent(S,ppropertydesc_parent[.TYPE = eps],ppropertydesc_child) /\\ '
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child[.TYPE = '
 'ppropertydesc_parent.TYPE]) /\\ '
 '~$property_hook_missing_return_parent(S,ppropertydesc_child,ppropertydesc_parent)',
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent[.DEFAULT = PROP_NULL],ppropertydesc_child) '
 '/\\ ~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child[.DEFAULT = '
 'PROP_UNINITIALIZED]) /\\ '
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child[.DEFAULT = PROP_LITERAL '
 '(PINT 100)])',
 '~$property_hook_missing_return_parent(S[.SOURCES = eps],ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_missing_return_parent(S[.CLASSES = eps],ppropertydesc_parent,ppropertydesc_child)',
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child[.ORIGIN = '
 'ppropertydesc_parent.ORIGIN]) /\\ '
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child[.NAME = '
 '$ptascii("wrong")])',
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent[.FINAL = true],ppropertydesc_child) /\\ '
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child[.SETVISIBILITY = '
 '(PROPERTY_PROTECTED)])',
 '~$property_hook_missing_return_parent(S[.CLASSES = [pclassdesc_parent[.PROPERTIES = '
 'eps],pclassdesc_child]],ppropertydesc_parent,ppropertydesc_child)',
 '~$property_hook_missing_return_parent(S[.CLASSES = [pclassdesc_parent,pclassdesc_child[.PROPERTIES = '
 'eps]]],ppropertydesc_parent,ppropertydesc_child)',
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent[.TYPE = [PTBRANCH ([PTBUILTIN '
 '"string"])]],ppropertydesc_child)',
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child[.DEFAULT = PROP_LITERAL '
 'PNULL])',
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent[.FINAL '
 '= true],ppropertydesc_child) = ($ptascii("Cannot override final property '
 'StorageBodyRemoveParent46::$value"))',
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child[.STATIC '
 '= true]) = ($ptascii("Cannot redeclare non static StorageBodyRemoveParent46::$value as static '
 'StorageBodyRemoveChild46::$value"))',
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child[.READONLY '
 '= true]) = ($ptascii("Cannot redeclare non-readonly property StorageBodyRemoveParent46::$value as readonly '
 'StorageBodyRemoveChild46::$value"))',
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child[.VISIBILITY '
 '= PROPERTY_PROTECTED]) = ($ptascii("Access level to StorageBodyRemoveChild46::$value must be public (as in '
 'class StorageBodyRemoveParent46)"))',
 '$property_hook_covariance_error_site(S,[ppropertydesc_parent],ppropertydesc_child,$ptascii("Type of '
 'StorageBodyAddChild46::$value must be omitted to match the parent definition in class '
 'StorageBodyAddParent46")) = eps',
 'S.SOURCES = pcunit :: pcunit_tail*',
 'pcunit.ID = n_unit',
 'porigin_parent_hook = PORIGIN n_unit pcpath_parent_hook',
 '$origin_node(S.SOURCES,porigin_parent_hook) = (NPropertyHook phpType14_parent phpType24_parent '
 'phpType4_parent phpType11_parent phpType16_parent phpType39_parent metadata_parent)',
 'phpType38_parent_unbacked = NPropertyHook phpType14_parent phpType24_parent phpType4_parent '
 'phpType11_parent phpType16_parent (NScalarInt (INTEGER 7) metadata_parent) metadata_parent',
 'S_parent_unbacked = S[.SOURCES = pcunit[.OCCURRENCES = '
 '$bu_replace(pcunit.OCCURRENCES,pcpath_parent_hook,phpType38_parent_unbacked)] :: pcunit_tail*]',
 '~$property_hook_override_backed(S_parent_unbacked,ppropertydesc_parent) /\\ '
 '~$property_hook_missing_return_parent(S_parent_unbacked,ppropertydesc_parent,ppropertydesc_child)',
 'phpType38_child_byref = NPropertyHook phpType14_hook phpType24_hook (BOOLEAN true) phpType11_hook '
 'phpType16_hook phpType39_hook metadata_hook',
 'S_child_byref = S[.SOURCES = pcunit[.OCCURRENCES = '
 '$bu_replace(pcunit.OCCURRENCES,pcpath_child_hook,phpType38_child_byref)] :: pcunit_tail*]',
 '~$property_hook_missing_return_parent(S_child_byref,ppropertydesc_parent,ppropertydesc_child)']

CV = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("StorageBodyParent46"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("StorageBodyBridge46"))) = (porigin_bridge)',
 '$class_at(S.CLASSES,porigin_bridge) = (pclassdesc_bridge)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("StorageBodyChild46"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("StorageBodyGrand46"))) = (porigin_grand)',
 '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
 '$class_link_at(S.LINKEDPARENTS,porigin_parent) = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_bridge) = '
 '(SOURCE_PARENT porigin_parent) /\\ $class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT '
 'porigin_bridge) /\\ $class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_child)',
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ |pclassdesc_child.PROPERTIES| = 1 /\\ pclassdesc_bridge.PROPERTIES '
 '= eps /\\ pclassdesc_grand.PROPERTIES = eps',
 'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
 'ppropertydesc_parent.TYPE = eps /\\ ppropertydesc_child.TYPE = eps /\\ ppropertydesc_child.DEFAULT = '
 'PROP_NULL /\\ $property_default_state(S,ppropertydesc_parent) = (PROP_VALUE (DIRECT (PINT 100))) /\\ '
 '$property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT PNULL))',
 '$property_layout(S,porigin_bridge,|S.CLASSES|) = [ppropertydesc_parent] /\\ '
 '$property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_child]',
 '$property_hook_override_backed(S,ppropertydesc_parent) /\\ '
 '~$property_hook_override_backed(S,ppropertydesc_child) /\\ '
 '$property_hook_inherited_backing(S,ppropertydesc_child) /\\ '
 '$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_virtual(S,ppropertydesc_parent) /\\ ~$property_hook_virtual(S,ppropertydesc_child)',
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) '
 '= eps',
 'S_globals = $global_table_view(S)',
 '$lookup(S_globals.ENV,$ptascii("parent")) = (n_parent_cell)',
 'S.STORE[n_parent_cell] = DEFINED (POBJECT n_parent)',
 'S.OBJECTS[n_parent] = INSTANCE porigin_parent /\\ $objectprops_at(S.OBJECTPROPS,n_parent) = ([{ DECL '
 '(ppropertydesc_parent.ORIGIN), NAME ppropertydesc_parent.KEY, STATE PROP_VALUE (DIRECT (PINT 100)) }])',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("parentRead")) = (pmethoddesc_read)',
 '$method_named(pclassdesc_child.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
 '$method_named(pclassdesc_bridge.METHODS,$ptascii("answer")) = (pmethoddesc_bridge_answer)',
 '$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
 'pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.OWNER = porigin_child /\\ '
 'pmethoddesc_bridge_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_grand_answer.VISIBILITY = '
 'PROPERTY_PRIVATE /\\ pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_bridge_answer.FUNCTION.ORIGIN /\\ '
 'pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_grand_answer.FUNCTION.ORIGIN',
 'S_child = S',
 '$property_hook_plan(S_child) = (ppropertyhook_S_child)',
 'S_child.TODO = (PROPERTY_PREP phpType20_S_child z_S_child) :: (DIM_FETCH z_S_child) :: ptask_S_child*',
 '$property_effective_desc(S_child,ppropertyhook_S_child.OBJECT,$ptascii("value")) = (ppropertydesc_S_child)',
 '$property_hook_function(S_child,ppropertyhook_S_child) = (pfunction_S_child)',
 'S_child.OBJECTS[ppropertyhook_S_child.OBJECT] = INSTANCE porigin_child /\\ ppropertydesc_S_child = '
 'ppropertydesc_child /\\ ppropertyhook_S_child.PROPERTY = ppropertydesc_child.ORIGIN /\\ '
 'pfunction_S_child.SIGNATURE.RETURNS = eps',
 '$target_lexical_class(S_child,PROPERTY_HOOK_TARGET ppropertyhook_S_child) = (porigin_child) /\\ '
 '$target_called_class(S_child,PROPERTY_HOOK_TARGET ppropertyhook_S_child) = (porigin_child) /\\ '
 '~$property_hook_backing(S_child,ppropertyhook_S_child.OBJECT,ppropertydesc_child)',
 '$objectprops_at(S_child.OBJECTPROPS,ppropertyhook_S_child.OBJECT) = ([{ DECL (ppropertydesc_child.ORIGIN), '
 'NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT PNULL) }])',
 '$heap_owners($heap_prune($heap_graph(S_child)),HOBJECT ppropertyhook_S_child.OBJECT) = 1 /\\ '
 '$bu_guard(S_child)',
 'PhpStep: S_child ~> S_child_call_raw',
 'S_child_call_raw.TODO = [(CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook_S_child) eps 0 eps '
 '(ppropertyhook_S_child.SITE) z_S_child), PROPERTY_HOOK_RESULT ppropertyhook_S_child] ++ ptask_S_child*',
 'S_child_call_raw.RESULT = KNOWN PNULL /\\ S_child_call_raw.EVENTS = S_child.EVENTS /\\ '
 'S_child_call_raw.OBJECTPROPS = S_child.OBJECTPROPS',
 'S_child_call = $bu_after(S_child,S_child_call_raw)',
 '$property_hook_pending_call(S_child_call,ppropertyhook_S_child) /\\ '
 '$heap_owners($heap_prune($heap_graph(S_child_call)),HOBJECT ppropertyhook_S_child.OBJECT) = 2 /\\ '
 '$bu_guard(S_child_call)',
 'S_child_entered_found = $bu_seek(S_child_call,2,1000)',
 'S_child_entered_found.COMPLETION = NORMAL \\/ S_child_entered_found.COMPLETION = BUDGET',
 'S_child_entered = S_child_entered_found[.COMPLETION = NORMAL]',
 'S_child_entered.CURRENT = (pcallcontext_hook_S_child)',
 'S_child_entered.FRAMES = pframe_S_child :: pframe_tail_S_child*',
 'pframe_S_child.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_S_child) :: ptask_S_child* /\\ '
 'pcallcontext_hook_S_child.TARGET = PROPERTY_HOOK_TARGET ppropertyhook_S_child /\\ '
 'pcallcontext_hook_S_child.FUNCTION = ppropertyhook_S_child.HOOK /\\ pcallcontext_hook_S_child.RECEIVER = '
 '(ppropertyhook_S_child.OBJECT)',
 'pcallcontext_hook_S_child.LEXICAL_CLASS = (porigin_child) /\\ pcallcontext_hook_S_child.CALLED_CLASS = '
 '(porigin_child) /\\ pfunction_S_child.NAME = pclassdesc_child.NAME ++ $ptascii("::$value::get") /\\ '
 '$property_hook_frame(S_child_entered,pcallcontext_hook_S_child,pframe_S_child,ppropertyhook_S_child)',
 '~$property_hook_backing(S_child_entered,ppropertyhook_S_child.OBJECT,ppropertydesc_S_child) /\\ '
 '$heap_owners($heap_prune($heap_graph(S_child_entered)),HOBJECT ppropertyhook_S_child.OBJECT) = 2 /\\ '
 '$bu_guard(S_child_entered)',
 '$objectprops_at(S_child_entered.OBJECTPROPS,ppropertyhook_S_child.OBJECT) = ([{ DECL '
 '(ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT PNULL) }])',
 'S_child_answer_found = $bu_seek(S_child_entered,4,1000)',
 'S_child_answer_found.COMPLETION = NORMAL \\/ S_child_answer_found.COMPLETION = BUDGET',
 'S_child_answer = S_child_answer_found[.COMPLETION = NORMAL]',
 'S_child_answer.CURRENT = (pcallcontext_answer_S_child)',
 'pcallcontext_answer_S_child.FUNCTION = pmethoddesc_answer.FUNCTION.ORIGIN /\\ '
 'pcallcontext_answer_S_child.LEXICAL_CLASS = (porigin_child) /\\ pcallcontext_answer_S_child.CALLED_CLASS = '
 '(porigin_child) /\\ pcallcontext_answer_S_child.RECEIVER = (ppropertyhook_S_child.OBJECT) /\\ '
 '$call_context_valid(S_child_answer,pcallcontext_answer_S_child,S_child_answer.CVS)',
 '$objectprops_at(S_child_answer.OBJECTPROPS,ppropertyhook_S_child.OBJECT) = ([{ DECL '
 '(ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT PNULL) }])',
 'S_child_result_found = $bu_seek(S_child_answer,3,1000)',
 'S_child_result_found.COMPLETION = NORMAL \\/ S_child_result_found.COMPLETION = BUDGET',
 'S_child_result = S_child_result_found[.COMPLETION = NORMAL]',
 'S_child_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_S_child) :: ptask_S_child* /\\ '
 'S_child_result.RESULT = KNOWN (PINT 13) /\\ S_child_result.CURRENT = eps',
 '$objectprops_at(S_child_result.OBJECTPROPS,ppropertyhook_S_child.OBJECT) = ([{ DECL '
 '(ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT PNULL) }])',
 '$heap_owners($heap_prune($heap_graph(S_child_result)),HOBJECT ppropertyhook_S_child.OBJECT) = 1 /\\ '
 '$task_nodes(PROPERTY_HOOK_RESULT ppropertyhook_S_child) = eps /\\ '
 '~$property_hook_backing(S_child_result,ppropertyhook_S_child.OBJECT,ppropertydesc_child) /\\ '
 '$bu_guard(S_child_result)',
 'PhpStep: S_child_result ~> S_child_base_raw',
 'S_child_base_raw.RESULT = S_child_result.RESULT /\\ S_child_base_raw.BASE = BASE_VALUE '
 'S_child_result.RESULT /\\ S_child_base_raw.TODO = ptask_S_child* /\\ S_child_base_raw.EVENTS = '
 'S_child_result.EVENTS /\\ S_child_base_raw.OBJECTPROPS = S_child_result.OBJECTPROPS',
 'S_child_base = $bu_after(S_child_result,S_child_base_raw)',
 '$bu_guard(S_child_base)']

THIS = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("StorageBodyParent46"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("StorageBodyBridge46"))) = (porigin_bridge)',
 '$class_at(S.CLASSES,porigin_bridge) = (pclassdesc_bridge)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("StorageBodyChild46"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("StorageBodyGrand46"))) = (porigin_grand)',
 '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
 '$class_link_at(S.LINKEDPARENTS,porigin_parent) = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_bridge) = '
 '(SOURCE_PARENT porigin_parent) /\\ $class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT '
 'porigin_bridge) /\\ $class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_child)',
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ |pclassdesc_child.PROPERTIES| = 1 /\\ pclassdesc_bridge.PROPERTIES '
 '= eps /\\ pclassdesc_grand.PROPERTIES = eps',
 'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
 'ppropertydesc_parent.TYPE = eps /\\ ppropertydesc_child.TYPE = eps /\\ ppropertydesc_child.DEFAULT = '
 'PROP_NULL /\\ $property_default_state(S,ppropertydesc_parent) = (PROP_VALUE (DIRECT (PINT 100))) /\\ '
 '$property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT PNULL))',
 '$property_layout(S,porigin_bridge,|S.CLASSES|) = [ppropertydesc_parent] /\\ '
 '$property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_child]',
 '$property_hook_override_backed(S,ppropertydesc_parent) /\\ '
 '~$property_hook_override_backed(S,ppropertydesc_child) /\\ '
 '$property_hook_inherited_backing(S,ppropertydesc_child) /\\ '
 '$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_virtual(S,ppropertydesc_parent) /\\ ~$property_hook_virtual(S,ppropertydesc_child)',
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) '
 '= eps',
 'S_globals = $global_table_view(S)',
 '$lookup(S_globals.ENV,$ptascii("parent")) = (n_parent_cell)',
 'S.STORE[n_parent_cell] = DEFINED (POBJECT n_parent)',
 'S.OBJECTS[n_parent] = INSTANCE porigin_parent /\\ $objectprops_at(S.OBJECTPROPS,n_parent) = ([{ DECL '
 '(ppropertydesc_parent.ORIGIN), NAME ppropertydesc_parent.KEY, STATE PROP_VALUE (DIRECT (PINT 100)) }])',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("parentRead")) = (pmethoddesc_read)',
 '$method_named(pclassdesc_child.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
 '$method_named(pclassdesc_bridge.METHODS,$ptascii("answer")) = (pmethoddesc_bridge_answer)',
 '$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
 'pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.OWNER = porigin_child /\\ '
 'pmethoddesc_bridge_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_grand_answer.VISIBILITY = '
 'PROPERTY_PRIVATE /\\ pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_bridge_answer.FUNCTION.ORIGIN /\\ '
 'pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_grand_answer.FUNCTION.ORIGIN',
 'S_this = S',
 '$property_hook_plan(S_this) = (ppropertyhook_S_this)',
 'S_this.TODO = (PROPERTY_PREP phpType20_S_this z_S_this) :: (DIM_FETCH z_S_this) :: ptask_S_this*',
 '$property_effective_desc(S_this,ppropertyhook_S_this.OBJECT,$ptascii("value")) = (ppropertydesc_S_this)',
 '$property_hook_function(S_this,ppropertyhook_S_this) = (pfunction_S_this)',
 'S_this.OBJECTS[ppropertyhook_S_this.OBJECT] = INSTANCE porigin_grand /\\ ppropertydesc_S_this = '
 'ppropertydesc_child /\\ ppropertyhook_S_this.PROPERTY = ppropertydesc_child.ORIGIN /\\ '
 'pfunction_S_this.SIGNATURE.RETURNS = eps',
 '$target_lexical_class(S_this,PROPERTY_HOOK_TARGET ppropertyhook_S_this) = (porigin_child) /\\ '
 '$target_called_class(S_this,PROPERTY_HOOK_TARGET ppropertyhook_S_this) = (porigin_grand) /\\ '
 '~$property_hook_backing(S_this,ppropertyhook_S_this.OBJECT,ppropertydesc_child)',
 '$objectprops_at(S_this.OBJECTPROPS,ppropertyhook_S_this.OBJECT) = ([{ DECL (ppropertydesc_child.ORIGIN), '
 'NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT PNULL) }])',
 '$heap_owners($heap_prune($heap_graph(S_this)),HOBJECT ppropertyhook_S_this.OBJECT) = 3 /\\ '
 '$bu_guard(S_this)',
 'S_this.CURRENT = (pcallcontext_read)',
 'pcallcontext_read.FUNCTION = pmethoddesc_read.FUNCTION.ORIGIN /\\ pcallcontext_read.LEXICAL_CLASS = '
 '(porigin_parent) /\\ pcallcontext_read.CALLED_CLASS = (porigin_grand) /\\ $this_receiver(S_this) = '
 '(ppropertyhook_S_this.OBJECT)',
 'PhpStep: S_this ~> S_this_call_raw',
 'S_this_call_raw.TODO = [(CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook_S_this) eps 0 eps '
 '(ppropertyhook_S_this.SITE) z_S_this), PROPERTY_HOOK_RESULT ppropertyhook_S_this] ++ ptask_S_this*',
 'S_this_call_raw.RESULT = KNOWN PNULL /\\ S_this_call_raw.EVENTS = S_this.EVENTS /\\ '
 'S_this_call_raw.OBJECTPROPS = S_this.OBJECTPROPS',
 'S_this_call = $bu_after(S_this,S_this_call_raw)',
 '$property_hook_pending_call(S_this_call,ppropertyhook_S_this) /\\ '
 '$heap_owners($heap_prune($heap_graph(S_this_call)),HOBJECT ppropertyhook_S_this.OBJECT) = 3 /\\ '
 '$bu_guard(S_this_call)',
 'S_this_entered_found = $bu_seek(S_this_call,2,1000)',
 'S_this_entered_found.COMPLETION = NORMAL \\/ S_this_entered_found.COMPLETION = BUDGET',
 'S_this_entered = S_this_entered_found[.COMPLETION = NORMAL]',
 'S_this_entered.CURRENT = (pcallcontext_hook_S_this)',
 'S_this_entered.FRAMES = pframe_S_this :: pframe_tail_S_this*',
 'pframe_S_this.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_S_this) :: ptask_S_this* /\\ '
 'pcallcontext_hook_S_this.TARGET = PROPERTY_HOOK_TARGET ppropertyhook_S_this /\\ '
 'pcallcontext_hook_S_this.FUNCTION = ppropertyhook_S_this.HOOK /\\ pcallcontext_hook_S_this.RECEIVER = '
 '(ppropertyhook_S_this.OBJECT)',
 'pcallcontext_hook_S_this.LEXICAL_CLASS = (porigin_child) /\\ pcallcontext_hook_S_this.CALLED_CLASS = '
 '(porigin_grand) /\\ pfunction_S_this.NAME = pclassdesc_child.NAME ++ $ptascii("::$value::get") /\\ '
 '$property_hook_frame(S_this_entered,pcallcontext_hook_S_this,pframe_S_this,ppropertyhook_S_this)',
 '~$property_hook_backing(S_this_entered,ppropertyhook_S_this.OBJECT,ppropertydesc_S_this) /\\ '
 '$heap_owners($heap_prune($heap_graph(S_this_entered)),HOBJECT ppropertyhook_S_this.OBJECT) = 3 /\\ '
 '$bu_guard(S_this_entered)',
 '$objectprops_at(S_this_entered.OBJECTPROPS,ppropertyhook_S_this.OBJECT) = ([{ DECL '
 '(ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT PNULL) }])',
 'S_this_answer_found = $bu_seek(S_this_entered,4,1000)',
 'S_this_answer_found.COMPLETION = NORMAL \\/ S_this_answer_found.COMPLETION = BUDGET',
 'S_this_answer = S_this_answer_found[.COMPLETION = NORMAL]',
 'S_this_answer.CURRENT = (pcallcontext_answer_S_this)',
 'pcallcontext_answer_S_this.FUNCTION = pmethoddesc_answer.FUNCTION.ORIGIN /\\ '
 'pcallcontext_answer_S_this.LEXICAL_CLASS = (porigin_child) /\\ pcallcontext_answer_S_this.CALLED_CLASS = '
 '(porigin_grand) /\\ pcallcontext_answer_S_this.RECEIVER = (ppropertyhook_S_this.OBJECT) /\\ '
 '$call_context_valid(S_this_answer,pcallcontext_answer_S_this,S_this_answer.CVS)',
 '$objectprops_at(S_this_answer.OBJECTPROPS,ppropertyhook_S_this.OBJECT) = ([{ DECL '
 '(ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT PNULL) }])',
 'S_this_result_found = $bu_seek(S_this_answer,3,1000)',
 'S_this_result_found.COMPLETION = NORMAL \\/ S_this_result_found.COMPLETION = BUDGET',
 'S_this_result = S_this_result_found[.COMPLETION = NORMAL]',
 'S_this_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_S_this) :: ptask_S_this* /\\ S_this_result.RESULT '
 '= KNOWN (PINT 13) /\\ S_this_result.CURRENT = (pcallcontext_read)',
 '$objectprops_at(S_this_result.OBJECTPROPS,ppropertyhook_S_this.OBJECT) = ([{ DECL '
 '(ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT PNULL) }])',
 '$heap_owners($heap_prune($heap_graph(S_this_result)),HOBJECT ppropertyhook_S_this.OBJECT) = 2 /\\ '
 '$task_nodes(PROPERTY_HOOK_RESULT ppropertyhook_S_this) = eps /\\ '
 '~$property_hook_backing(S_this_result,ppropertyhook_S_this.OBJECT,ppropertydesc_child) /\\ '
 '$bu_guard(S_this_result)',
 'PhpStep: S_this_result ~> S_this_base_raw',
 'S_this_base_raw.RESULT = S_this_result.RESULT /\\ S_this_base_raw.BASE = BASE_VALUE S_this_result.RESULT '
 '/\\ S_this_base_raw.TODO = ptask_S_this* /\\ S_this_base_raw.EVENTS = S_this_result.EVENTS /\\ '
 'S_this_base_raw.OBJECTPROPS = S_this_result.OBJECTPROPS',
 'S_this_base = $bu_after(S_this_result,S_this_base_raw)',
 '$bu_guard(S_this_base)']

WRITE = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("StorageBodyParent46"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("StorageBodyBridge46"))) = (porigin_bridge)',
 '$class_at(S.CLASSES,porigin_bridge) = (pclassdesc_bridge)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("StorageBodyChild46"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("StorageBodyGrand46"))) = (porigin_grand)',
 '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
 '$class_link_at(S.LINKEDPARENTS,porigin_parent) = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_bridge) = '
 '(SOURCE_PARENT porigin_parent) /\\ $class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT '
 'porigin_bridge) /\\ $class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_child)',
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ |pclassdesc_child.PROPERTIES| = 1 /\\ pclassdesc_bridge.PROPERTIES '
 '= eps /\\ pclassdesc_grand.PROPERTIES = eps',
 'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
 'ppropertydesc_parent.TYPE = eps /\\ ppropertydesc_child.TYPE = eps /\\ ppropertydesc_child.DEFAULT = '
 'PROP_NULL /\\ $property_default_state(S,ppropertydesc_parent) = (PROP_VALUE (DIRECT (PINT 100))) /\\ '
 '$property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT PNULL))',
 '$property_layout(S,porigin_bridge,|S.CLASSES|) = [ppropertydesc_parent] /\\ '
 '$property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_child]',
 '$property_hook_override_backed(S,ppropertydesc_parent) /\\ '
 '~$property_hook_override_backed(S,ppropertydesc_child) /\\ '
 '$property_hook_inherited_backing(S,ppropertydesc_child) /\\ '
 '$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_virtual(S,ppropertydesc_parent) /\\ ~$property_hook_virtual(S,ppropertydesc_child)',
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) '
 '= eps',
 'S_globals = $global_table_view(S)',
 '$lookup(S_globals.ENV,$ptascii("parent")) = (n_parent_cell)',
 'S.STORE[n_parent_cell] = DEFINED (POBJECT n_parent)',
 'S.OBJECTS[n_parent] = INSTANCE porigin_parent /\\ $objectprops_at(S.OBJECTPROPS,n_parent) = ([{ DECL '
 '(ppropertydesc_parent.ORIGIN), NAME ppropertydesc_parent.KEY, STATE PROP_VALUE (DIRECT (PINT 100)) }])',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("parentRead")) = (pmethoddesc_read)',
 '$method_named(pclassdesc_child.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
 '$method_named(pclassdesc_bridge.METHODS,$ptascii("answer")) = (pmethoddesc_bridge_answer)',
 '$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
 'pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.OWNER = porigin_child /\\ '
 'pmethoddesc_bridge_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_grand_answer.VISIBILITY = '
 'PROPERTY_PRIVATE /\\ pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_bridge_answer.FUNCTION.ORIGIN /\\ '
 'pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_grand_answer.FUNCTION.ORIGIN',
 'S_write = S',
 'S_write.TODO = (ASSIGN_ARRAY pbase_write z_write b_write) :: ptask_write*',
 '$lookup(S_write.ENV,$ptascii("grand")) = (n_grand_cell)',
 'S_write.STORE[n_grand_cell] = DEFINED (POBJECT n_grand)',
 'S_write.OBJECTS[n_grand] = INSTANCE porigin_grand /\\ (HOBJECT n_grand) <- S_write.ALLOCATIONS',
 '$objectprops_at(S_write.OBJECTPROPS,n_grand) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME '
 'ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT PNULL) }])',
 '$property_pending_base(pbase_write) /\\ S_write.RESULT = KNOWN (PINT 300) /\\ z_write = 33 /\\ '
 '$call_task_valid(S_write,ASSIGN_ARRAY pbase_write z_write b_write) /\\ '
 '$heap_owners($heap_prune($heap_graph(S_write)),HOBJECT n_grand) = 1 /\\ $bu_guard(S_write)',
 'PhpStep: S_write ~> S_write_raw',
 'S_write_raw.COMPLETION = NORMAL /\\ S_write_raw.RESULT = KNOWN (PINT 300) /\\ S_write_raw.EVENTS = '
 'S_write.EVENTS /\\ S_write_raw.TODO = ptask_write*',
 '$objectprops_at(S_write_raw.OBJECTPROPS,n_grand) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME '
 'ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 300)) }])',
 'S_written = $bu_after(S_write,S_write_raw)',
 '$bu_guard(S_written)',
 'S_after_write_found = $bu_seek(S_written,6,1000)',
 'S_after_write_found.COMPLETION = NORMAL \\/ S_after_write_found.COMPLETION = BUDGET',
 'S_after_write = S_after_write_found[.COMPLETION = NORMAL]',
 '$property_hook_plan(S_after_write) = (ppropertyhook_S_after_write)',
 'S_after_write.TODO = (PROPERTY_PREP phpType20_S_after_write z_S_after_write) :: (DIM_FETCH '
 'z_S_after_write) :: ptask_S_after_write*',
 '$property_effective_desc(S_after_write,ppropertyhook_S_after_write.OBJECT,$ptascii("value")) = '
 '(ppropertydesc_S_after_write)',
 '$property_hook_function(S_after_write,ppropertyhook_S_after_write) = (pfunction_S_after_write)',
 'S_after_write.OBJECTS[ppropertyhook_S_after_write.OBJECT] = INSTANCE porigin_grand /\\ '
 'ppropertydesc_S_after_write = ppropertydesc_child /\\ ppropertyhook_S_after_write.PROPERTY = '
 'ppropertydesc_child.ORIGIN /\\ pfunction_S_after_write.SIGNATURE.RETURNS = eps',
 '$target_lexical_class(S_after_write,PROPERTY_HOOK_TARGET ppropertyhook_S_after_write) = (porigin_child) '
 '/\\ $target_called_class(S_after_write,PROPERTY_HOOK_TARGET ppropertyhook_S_after_write) = (porigin_grand) '
 '/\\ ~$property_hook_backing(S_after_write,ppropertyhook_S_after_write.OBJECT,ppropertydesc_child)',
 '$objectprops_at(S_after_write.OBJECTPROPS,ppropertyhook_S_after_write.OBJECT) = ([{ DECL '
 '(ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 300)) }])',
 '$heap_owners($heap_prune($heap_graph(S_after_write)),HOBJECT ppropertyhook_S_after_write.OBJECT) = 1 /\\ '
 '$bu_guard(S_after_write)',
 'S_after_write_result_found = $bu_seek(S_after_write,3,1000)',
 'S_after_write_result_found.COMPLETION = NORMAL \\/ S_after_write_result_found.COMPLETION = BUDGET',
 'S_after_write_result = S_after_write_result_found[.COMPLETION = NORMAL]',
 'S_after_write_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_S_after_write) :: ptask_S_after_write* /\\ '
 'S_after_write_result.RESULT = KNOWN (PINT 13) /\\ S_after_write_result.CURRENT = eps',
 '$objectprops_at(S_after_write_result.OBJECTPROPS,ppropertyhook_S_after_write.OBJECT) = ([{ DECL '
 '(ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 300)) }])',
 '$heap_owners($heap_prune($heap_graph(S_after_write_result)),HOBJECT ppropertyhook_S_after_write.OBJECT) = '
 '1 /\\ $task_nodes(PROPERTY_HOOK_RESULT ppropertyhook_S_after_write) = eps /\\ '
 '~$property_hook_backing(S_after_write_result,ppropertyhook_S_after_write.OBJECT,ppropertydesc_child) /\\ '
 '$bu_guard(S_after_write_result)',
 'PhpStep: S_after_write_result ~> S_after_write_base_raw',
 'S_after_write_base_raw.RESULT = S_after_write_result.RESULT /\\ S_after_write_base_raw.BASE = BASE_VALUE '
 'S_after_write_result.RESULT /\\ S_after_write_base_raw.TODO = ptask_S_after_write* /\\ '
 'S_after_write_base_raw.EVENTS = S_after_write_result.EVENTS /\\ S_after_write_base_raw.OBJECTPROPS = '
 'S_after_write_result.OBJECTPROPS',
 'S_after_write_base = $bu_after(S_after_write_result,S_after_write_base_raw)',
 '$bu_guard(S_after_write_base)',
 'ppropertyhook_S_after_write.OBJECT = n_grand',
 'S_done = $drive_steps(S_after_write_base,10000)',
 'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps /\\ $bu_output(S_done.EVENTS) = '
 'EXPECTED_OUTPUT /\\ $bu_guard(S_done)',
 '$objectprops_at(S_done.OBJECTPROPS,n_grand) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME '
 'ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 300)) }])']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--group', choices=['remove', 'add', 'cv', 'this', 'write'], required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'backed_parent_unbacked_get_hook_type_presence_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    clauses, negatives, case_index, start_stage = {
        'remove': (REMOVE, DERIVED, 0, None),
        'add': (ADD, [], 1, None),
        'cv': (CV, [], 2, 0),
        'this': (THIS, [], 2, 1),
        'write': (WRITE, [], 2, 5),
    }[args.group]
    selections = [(args.group, clauses, negatives)]
    cases = [data['cases'][case_index]]
    sources = [HERE / ('backed-parent-unbacked-get-hook-type-presence-' + ['remove', 'add', 'control'][case_index] + '.php')]
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
    out = Path(tempfile.mkdtemp(prefix='backed-parent-unbacked-get-hook-type-presence-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    derived = sum(len(row[2]) for row in selections)
    reached = sum((1 if args.group in ('remove', 'add') else 5) + len(row[1]) for row in selections)
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
                     'S_found = $bu_seek(S_initial,' + str(start_stage) + ',1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            if args.group in ('remove', 'add'):
                setup = [setup[0].replace('S_initial =', 'S =', 1)]
            content += '\ndec $bu_' + name + '() : bool\ndef $bu_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                condition = condition.replace('EXPECTED_OUTPUT', byte_expr(base64.b64decode(case['stdout_base64'])))
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $bu_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = (' + ' /\\ '.join('$bu_' + name + '()' for name, _, _ in selections) + ')\n'
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
