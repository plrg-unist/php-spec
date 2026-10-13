"""Check getter TYPE-presence priority and ordinary backing at genuine source states."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()



PREFIX = r'''dec $obp_replace(pcoccurrence*,pcpath,pcnode) : pcoccurrence*
def $obp_replace(eps,pcpath,pcnode) = eps
def $obp_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath pcnode) :: pcoccurrence*
def $obp_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath_other pcnode_old) :: $obp_replace(pcoccurrence*,pcpath,pcnode)
  -- if pcpath_other =/= pcpath
dec $obp_stage(pstate,nat) : bool
def $obp_stage(S,0) = true
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $property_hook_plan(S[.COMPLETION = NORMAL]) = (ppropertyhook)
  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)
  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin
  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)
  -- if $ptlc(pclassdesc.NAME) = $ptascii("ordinarypresencesecond52")
def $obp_stage(S,n) = false -- otherwise

dec $obp_seek(pstate,nat,nat) : pstate
def $obp_seek(S,n_stage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $obp_stage(S,n_stage) \/ n = 0
def $obp_seek(S,n_stage,n) = $obp_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$obp_stage(S,n_stage) /\ $(n > 0)
def $obp_seek(S,n_stage,n) = $obp_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $obp_seek(S,n_stage,n) = S -- otherwise
dec $obp_guard(pstate) : bool
def $obp_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''

REMOVE = ['S.COMPLETION = STATICBYTES ($ptascii("Declaration of OrdinaryRemoveSecond52::$value::get() must '
 'be compatible with OrdinaryRemoveFirst52::$value::get(): int")) 10 /\\ S.EVENTS = eps /\\ '
 'S.OBJECTS = eps /\\ S.OBJECTPROPS = eps',
 'S.CLASSES = [pclassdesc_root,pclassdesc_parent,pclassdesc_bridge,pclassdesc_child]',
 'pclassdesc_parent.NAME = $ptascii("OrdinaryRemoveFirst52") /\\ pclassdesc_child.NAME = '
 '$ptascii("OrdinaryRemoveSecond52") /\\ |pclassdesc_parent.PROPERTIES| = 1 /\\ '
 '|pclassdesc_child.PROPERTIES| = 1 /\\ pclassdesc_root.NAME = $ptascii("OrdinaryRemoveRoot52") '
 '/\\ pclassdesc_bridge.NAME = $ptascii("OrdinaryRemoveBridge52") /\\ |pclassdesc_root.PROPERTIES| '
 '= 1 /\\ pclassdesc_bridge.PROPERTIES = eps',
 'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
 'ppropertydesc_parent.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ ppropertydesc_child.TYPE = eps',
 '$property_default_state(S,ppropertydesc_parent) = (PROP_INITIAL) /\\ '
 '$property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT PNULL))',
 '$property_hook_origin(S,ppropertydesc_parent) = (porigin_parent_hook)',
 '$property_hook_origin(S,ppropertydesc_child) = (porigin_child_hook)',
 'ppropertydesc_root = pclassdesc_root.PROPERTIES[0]',
 '$property_default_state(S,ppropertydesc_root) = (PROP_VALUE (DIRECT (PINT 100))) /\\ '
 '$property_hook_origin(S,ppropertydesc_root) = eps /\\ '
 '~$property_hook_override_backed(S,ppropertydesc_root) /\\ '
 '$property_hook_override_pair(S,ppropertydesc_root,ppropertydesc_parent)',
 '$property_layout(S,pclassdesc_bridge.ORIGIN,|S.CLASSES|) = [ppropertydesc_parent] /\\ '
 '$property_declaring_class(S.CLASSES,ppropertydesc_parent.ORIGIN) = (pclassdesc_parent.ORIGIN)',
 'pclassdesc_parent.PARENT = (pclassdesc_root.NAME) /\\ pclassdesc_bridge.PARENT = '
 '(pclassdesc_parent.NAME) /\\ pclassdesc_child.PARENT = (pclassdesc_bridge.NAME)',
 '$origin_node(S.SOURCES,porigin_parent_hook) = (NPropertyHook phpType14_parent phpType24_parent '
 'phpType4_parent phpType11_parent phpType16_parent phpType39_parent metadata_parent)',
 '~$hook_body_backed(phpType39_parent,ppropertydesc_parent.NAME) /\\ $source_line(metadata_parent) '
 '= 6',
 'porigin_child_hook = PORIGIN n_unit pcpath_child_hook',
 '$function_at(S.FUNCTIONS,porigin_parent_hook) = (pfunction_parent)',
 '$function_at(S.FUNCTIONS,porigin_child_hook) = (pfunction_child)',
 'pfunction_parent.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_parent.TYPE, BYREF false} '
 '/\\ pfunction_child.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_child.TYPE, BYREF false}',
 'pfunction_parent.NAME = pclassdesc_parent.NAME ++ $ptascii("::$value::get") /\\ '
 'pfunction_child.NAME = pclassdesc_child.NAME ++ $ptascii("::$value::get") /\\ '
 'pfunction_parent.LINE = 6 /\\ pfunction_child.LINE = 10',
 '$origin_node(S.SOURCES,porigin_child_hook) = (NPropertyHook phpType14_hook phpType24_hook '
 'phpType4_hook phpType11_hook phpType16_hook phpType39_hook metadata_hook)',
 '~$hook_body_backed(phpType39_hook,ppropertydesc_child.NAME) /\\ $source_line(metadata_hook) = 10 '
 '/\\ pclassdesc_child.LINE = 9 /\\ S.ERRORORIGIN = eps /\\ n_unit = 0 /\\ pcpath_child_hook =/= '
 'eps',
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_root.NAME)) = (pclassdesc_root.ORIGIN) /\\ '
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_parent.NAME)) = (pclassdesc_parent.ORIGIN) /\\ '
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_bridge.NAME)) = (pclassdesc_bridge.ORIGIN) /\\ '
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_child.NAME)) = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,pclassdesc_root.ORIGIN) = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,pclassdesc_parent.ORIGIN) = (SOURCE_PARENT '
 'pclassdesc_root.ORIGIN) /\\ $class_link_at(S.LINKEDPARENTS,pclassdesc_bridge.ORIGIN) = '
 '(SOURCE_PARENT pclassdesc_parent.ORIGIN) /\\ '
 '$class_link_at(S.LINKEDPARENTS,pclassdesc_child.ORIGIN) = eps',
 '~$property_hook_override_backed(S,ppropertydesc_parent) /\\ '
 '~$property_hook_override_backed(S,ppropertydesc_child) /\\ '
 '~$property_hook_inherited_backing(S,ppropertydesc_parent) /\\ '
 '$property_hook_ordinary_backing(S,ppropertydesc_parent,|S.CLASSES|) /\\ '
 '~$property_hook_virtual_chain(S,ppropertydesc_parent,|S.CLASSES|)',
 '~$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child)',
 '$property_hook_covariance(S,ppropertydesc_parent,ppropertydesc_child) = PVUNSUPPORTED '
 'text_presence',
 'S.TODO = eps /\\ S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.ENV = eps /\\ '
 '$declaration_history_valid(S) /\\ $class_links_valid(S)',
 '$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child)',
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) '
 '= ($ptascii("Declaration of OrdinaryRemoveSecond52::$value::get() must be compatible with '
 'OrdinaryRemoveFirst52::$value::get(): int"))',
 '$property_hook_covariance_error_site(S,[ppropertydesc_parent],ppropertydesc_child,$ptascii("Declaration '
 'of OrdinaryRemoveSecond52::$value::get() must be compatible with '
 'OrdinaryRemoveFirst52::$value::get(): int")) = ((porigin_child_hook,10))',
 '$property_hook_get_declaration(S,ppropertydesc_child) = '
 '($ptascii("OrdinaryRemoveSecond52::$value::get()"))']

ADD = ['S.COMPLETION = STATICBYTES ($ptascii("Type of OrdinaryAddSecond52::$value must be omitted to '
 'match the parent definition in class OrdinaryAddFirst52")) 9 /\\ S.EVENTS = eps /\\ S.OBJECTS = '
 'eps /\\ S.OBJECTPROPS = eps',
 'S.CLASSES = [pclassdesc_root,pclassdesc_parent,pclassdesc_bridge,pclassdesc_child]',
 'pclassdesc_parent.NAME = $ptascii("OrdinaryAddFirst52") /\\ pclassdesc_child.NAME = '
 '$ptascii("OrdinaryAddSecond52") /\\ |pclassdesc_parent.PROPERTIES| = 1 /\\ '
 '|pclassdesc_child.PROPERTIES| = 1 /\\ pclassdesc_root.NAME = $ptascii("OrdinaryAddRoot52") /\\ '
 'pclassdesc_bridge.NAME = $ptascii("OrdinaryAddBridge52") /\\ |pclassdesc_root.PROPERTIES| = 1 '
 '/\\ pclassdesc_bridge.PROPERTIES = eps',
 'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
 'ppropertydesc_parent.TYPE = eps /\\ ppropertydesc_child.TYPE = [PTBRANCH ([PTBUILTIN "int"])]',
 '$property_default_state(S,ppropertydesc_parent) = (PROP_VALUE (DIRECT PNULL)) /\\ '
 '$property_default_state(S,ppropertydesc_child) = (PROP_INITIAL)',
 '$property_hook_origin(S,ppropertydesc_parent) = (porigin_parent_hook)',
 '$property_hook_origin(S,ppropertydesc_child) = (porigin_child_hook)',
 'ppropertydesc_root = pclassdesc_root.PROPERTIES[0]',
 '$property_default_state(S,ppropertydesc_root) = (PROP_VALUE (DIRECT (PINT 100))) /\\ '
 '$property_hook_origin(S,ppropertydesc_root) = eps /\\ '
 '~$property_hook_override_backed(S,ppropertydesc_root) /\\ '
 '$property_hook_override_pair(S,ppropertydesc_root,ppropertydesc_parent)',
 '$property_layout(S,pclassdesc_bridge.ORIGIN,|S.CLASSES|) = [ppropertydesc_parent] /\\ '
 '$property_declaring_class(S.CLASSES,ppropertydesc_parent.ORIGIN) = (pclassdesc_parent.ORIGIN)',
 'pclassdesc_parent.PARENT = (pclassdesc_root.NAME) /\\ pclassdesc_bridge.PARENT = '
 '(pclassdesc_parent.NAME) /\\ pclassdesc_child.PARENT = (pclassdesc_bridge.NAME)',
 '$origin_node(S.SOURCES,porigin_parent_hook) = (NPropertyHook phpType14_parent phpType24_parent '
 'phpType4_parent phpType11_parent phpType16_parent phpType39_parent metadata_parent)',
 '~$hook_body_backed(phpType39_parent,ppropertydesc_parent.NAME) /\\ $source_line(metadata_parent) '
 '= 6',
 'porigin_child_hook = PORIGIN n_unit pcpath_child_hook',
 '$function_at(S.FUNCTIONS,porigin_parent_hook) = (pfunction_parent)',
 '$function_at(S.FUNCTIONS,porigin_child_hook) = (pfunction_child)',
 'pfunction_parent.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_parent.TYPE, BYREF false} '
 '/\\ pfunction_child.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_child.TYPE, BYREF false}',
 'pfunction_parent.NAME = pclassdesc_parent.NAME ++ $ptascii("::$value::get") /\\ '
 'pfunction_child.NAME = pclassdesc_child.NAME ++ $ptascii("::$value::get") /\\ '
 'pfunction_parent.LINE = 6 /\\ pfunction_child.LINE = 10',
 '$origin_node(S.SOURCES,porigin_child_hook) = (NPropertyHook phpType14_hook phpType24_hook '
 'phpType4_hook phpType11_hook phpType16_hook phpType39_hook metadata_hook)',
 '~$hook_body_backed(phpType39_hook,ppropertydesc_child.NAME) /\\ $source_line(metadata_hook) = 10 '
 '/\\ pclassdesc_child.LINE = 9 /\\ S.ERRORORIGIN = eps /\\ n_unit = 0 /\\ pcpath_child_hook =/= '
 'eps',
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_root.NAME)) = (pclassdesc_root.ORIGIN) /\\ '
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_parent.NAME)) = (pclassdesc_parent.ORIGIN) /\\ '
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_bridge.NAME)) = (pclassdesc_bridge.ORIGIN) /\\ '
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_child.NAME)) = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,pclassdesc_root.ORIGIN) = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,pclassdesc_parent.ORIGIN) = (SOURCE_PARENT '
 'pclassdesc_root.ORIGIN) /\\ $class_link_at(S.LINKEDPARENTS,pclassdesc_bridge.ORIGIN) = '
 '(SOURCE_PARENT pclassdesc_parent.ORIGIN) /\\ '
 '$class_link_at(S.LINKEDPARENTS,pclassdesc_child.ORIGIN) = eps',
 '~$property_hook_override_backed(S,ppropertydesc_parent) /\\ '
 '~$property_hook_override_backed(S,ppropertydesc_child) /\\ '
 '~$property_hook_inherited_backing(S,ppropertydesc_parent) /\\ '
 '$property_hook_ordinary_backing(S,ppropertydesc_parent,|S.CLASSES|) /\\ '
 '~$property_hook_virtual_chain(S,ppropertydesc_parent,|S.CLASSES|)',
 '~$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child)',
 '$property_hook_covariance(S,ppropertydesc_parent,ppropertydesc_child) = PVUNSUPPORTED '
 'text_presence',
 'S.TODO = eps /\\ S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.ENV = eps /\\ '
 '$declaration_history_valid(S) /\\ $class_links_valid(S)',
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child)',
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) '
 '= ($ptascii("Type of OrdinaryAddSecond52::$value must be omitted to match the parent definition '
 'in class OrdinaryAddFirst52"))',
 '$property_hook_covariance_error_site(S,[ppropertydesc_parent],ppropertydesc_child,$ptascii("Type '
 'of OrdinaryAddSecond52::$value must be omitted to match the parent definition in class '
 'OrdinaryAddFirst52")) = eps',
 '$property_hook_get_declaration(S,ppropertydesc_parent) = '
 '($ptascii("OrdinaryAddFirst52::$value::get()"))']

DERIVED = ['~$property_hook_missing_return_parent(S,ppropertydesc_parent[.TYPE = eps],ppropertydesc_child) '
 '/\\ ~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child[.TYPE = '
 'ppropertydesc_parent.TYPE]) /\\ '
 '~$property_hook_missing_return_parent(S,ppropertydesc_child,ppropertydesc_parent)',
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent[.DEFAULT = '
 'PROP_NULL],ppropertydesc_child) /\\ '
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child[.DEFAULT = '
 'PROP_UNINITIALIZED]) /\\ '
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child[.DEFAULT = '
 'PROP_LITERAL (PINT 100)])',
 '~$property_hook_missing_return_parent(S[.SOURCES = '
 'eps],ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_missing_return_parent(S[.CLASSES = '
 'eps],ppropertydesc_parent,ppropertydesc_child)',
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child[.ORIGIN = '
 'ppropertydesc_parent.ORIGIN]) /\\ '
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child[.NAME = '
 '$ptascii("wrong")])',
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent[.FINAL = true],ppropertydesc_child) '
 '/\\ '
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child[.SETVISIBILITY '
 '= (PROPERTY_PROTECTED)])',
 '~$property_hook_missing_return_parent(S[.CLASSES = '
 '[pclassdesc_root,pclassdesc_parent[.PROPERTIES = '
 'eps],pclassdesc_bridge,pclassdesc_child]],ppropertydesc_parent,ppropertydesc_child)',
 '~$property_hook_missing_return_parent(S[.CLASSES = '
 '[pclassdesc_root,pclassdesc_parent,pclassdesc_bridge,pclassdesc_child[.PROPERTIES = '
 'eps]]],ppropertydesc_parent,ppropertydesc_child)',
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent[.TYPE = [PTBRANCH ([PTBUILTIN '
 '"string"])]],ppropertydesc_child)',
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child[.DEFAULT = '
 'PROP_LITERAL PNULL])',
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent[.FINAL '
 '= true],ppropertydesc_child) = ($ptascii("Cannot override final property '
 'OrdinaryRemoveFirst52::$value"))',
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child[.STATIC '
 '= true]) = ($ptascii("Cannot redeclare non static OrdinaryRemoveFirst52::$value as static '
 'OrdinaryRemoveSecond52::$value"))',
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child[.READONLY '
 '= true]) = ($ptascii("Cannot redeclare non-readonly property OrdinaryRemoveFirst52::$value as '
 'readonly OrdinaryRemoveSecond52::$value"))',
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child[.VISIBILITY '
 '= PROPERTY_PROTECTED]) = ($ptascii("Access level to OrdinaryRemoveSecond52::$value must be '
 'public (as in class OrdinaryRemoveFirst52)"))',
 '$property_hook_covariance_error_site(S,[ppropertydesc_parent],ppropertydesc_child,$ptascii("Type '
 'of OrdinaryRemoveSecond52::$value must be int (as in class OrdinaryRemoveFirst52)")) = eps',
 '~$property_hook_ordinary_backing(S,ppropertydesc_parent,0) /\\ '
 '~$property_hook_ordinary_backing(S,ppropertydesc_parent,1) /\\ '
 '$property_hook_ordinary_backing(S,ppropertydesc_parent,2)',
 '~$property_hook_missing_return_parent(S[.LINKEDPARENTS = '
 'eps],ppropertydesc_parent,ppropertydesc_child)',
 '~$property_hook_missing_return_parent(S[.CLASSES = [pclassdesc_root[.PROPERTIES = '
 'eps],pclassdesc_parent,pclassdesc_bridge,pclassdesc_child]],ppropertydesc_parent,ppropertydesc_child)',
 'S_root_type = S[.CLASSES = [pclassdesc_root[.PROPERTIES = [ppropertydesc_root[.TYPE = [PTBRANCH '
 '([PTBUILTIN "string"])]]]],pclassdesc_parent,pclassdesc_bridge,pclassdesc_child]]',
 '~$property_hook_ordinary_backing(S_root_type,ppropertydesc_parent,|S.CLASSES|) /\\ '
 '~$property_hook_missing_return_parent(S_root_type,ppropertydesc_parent,ppropertydesc_child)',
 'S.SOURCES = pcunit :: pcunit_tail*',
 'pcunit.ID = n_unit',
 'ppropertydesc_root.ORIGIN = PORIGIN n_unit pcpath_root_property',
 'pcpath_root_group = pcpath_root_property[0:$nabs($(|pcpath_root_property| - 2))]',
 'pcpath_root_property = pcpath_root_group ++ [PCFIELD 3, PCINDEX 0]',
 '$origin_node(S.SOURCES,PORIGIN n_unit pcpath_root_group) = (NStmtProperty phpType14_root '
 '(INTEGER flags_root) phpType18_root phpType56_root phpType37_root metadata_root)',
 'phpType14_root = SEQUENCE eps /\\ phpType37_root = SEQUENCE eps /\\ flags_root <- [0,1]',
 'S_root_flags = S[.SOURCES = pcunit[.OCCURRENCES = '
 '$obp_replace(pcunit.OCCURRENCES,pcpath_root_group,NStmtProperty phpType14_root (INTEGER 9) '
 'phpType18_root phpType56_root phpType37_root metadata_root)] :: pcunit_tail*]',
 '~$property_hook_ordinary_backing(S_root_flags,ppropertydesc_parent,|S.CLASSES|) /\\ '
 '~$property_hook_missing_return_parent(S_root_flags,ppropertydesc_parent,ppropertydesc_child)',
 'S_child_byref = S[.SOURCES = pcunit[.OCCURRENCES = '
 '$obp_replace(pcunit.OCCURRENCES,pcpath_child_hook,NPropertyHook phpType14_hook phpType24_hook '
 '(BOOLEAN true) phpType11_hook phpType16_hook phpType39_hook metadata_hook)] :: pcunit_tail*]',
 '~$property_hook_missing_return_parent(S_child_byref,ppropertydesc_parent,ppropertydesc_child)']

CONTROL = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("OrdinaryPresenceRoot52"))) = (porigin_root)',
 '$class_at(S.CLASSES,porigin_root) = (pclassdesc_root)',
 'ppropertydesc_root = pclassdesc_root.PROPERTIES[0]',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("OrdinaryPresenceFirst52"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("OrdinaryPresenceBridge52"))) = (porigin_bridge)',
 '$class_at(S.CLASSES,porigin_bridge) = (pclassdesc_bridge)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("OrdinaryPresenceSecond52"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("OrdinaryPresenceGrand52"))) = (porigin_grand)',
 '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
 '$class_link_at(S.LINKEDPARENTS,porigin_root) = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_parent) = (SOURCE_PARENT porigin_root) /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_bridge) = (SOURCE_PARENT porigin_parent) /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_bridge) /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_child)',
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ |pclassdesc_child.PROPERTIES| = 1 /\\ '
 'pclassdesc_bridge.PROPERTIES = eps /\\ pclassdesc_grand.PROPERTIES = eps /\\ '
 '|pclassdesc_root.PROPERTIES| = 1',
 'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
 'ppropertydesc_root.TYPE = eps /\\ ppropertydesc_parent.TYPE = eps /\\ ppropertydesc_child.TYPE = '
 'eps /\\ ppropertydesc_parent.DEFAULT = PROP_NULL /\\ ppropertydesc_child.DEFAULT = PROP_NULL /\\ '
 '$property_default_state(S,ppropertydesc_root) = (PROP_VALUE (DIRECT (PINT 100))) /\\ '
 '$property_default_state(S,ppropertydesc_parent) = (PROP_VALUE (DIRECT PNULL)) /\\ '
 '$property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT PNULL))',
 '$property_layout(S,porigin_bridge,|S.CLASSES|) = [ppropertydesc_parent] /\\ '
 '$property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_child]',
 '$property_hook_origin(S,ppropertydesc_root) = eps /\\ '
 '~$property_hook_override_backed(S,ppropertydesc_root) /\\ '
 '~$property_hook_override_backed(S,ppropertydesc_parent) /\\ '
 '~$property_hook_override_backed(S,ppropertydesc_child) /\\ '
 '~$property_hook_inherited_backing(S,ppropertydesc_parent) /\\ '
 '$property_hook_ordinary_backing(S,ppropertydesc_parent,|S.CLASSES|) /\\ '
 '$property_hook_inherited_backing(S,ppropertydesc_child) /\\ '
 '$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_virtual(S,ppropertydesc_parent) /\\ '
 '~$property_hook_virtual(S,ppropertydesc_child)',
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) '
 '= eps',
 'S_globals = $global_table_view(S)',
 '$lookup(S_globals.ENV,$ptascii("parent")) = (n_root_cell)',
 'S.STORE[n_root_cell] = DEFINED (POBJECT n_root)',
 'S.OBJECTS[n_root] = INSTANCE porigin_root /\\ $objectprops_at(S.OBJECTPROPS,n_root) = ([{ DECL '
 '(ppropertydesc_root.ORIGIN), NAME ppropertydesc_root.KEY, STATE PROP_VALUE (DIRECT (PINT 100)) '
 '}])',
 '$lookup(S_globals.ENV,$ptascii("first")) = (n_first_cell)',
 'S.STORE[n_first_cell] = DEFINED (POBJECT n_first)',
 'S.OBJECTS[n_first] = INSTANCE porigin_parent /\\ $objectprops_at(S.OBJECTPROPS,n_first) = ([{ '
 'DECL (ppropertydesc_parent.ORIGIN), NAME ppropertydesc_parent.KEY, STATE PROP_VALUE (DIRECT '
 'PNULL) }])',
 '$method_named(pclassdesc_root.METHODS,$ptascii("parentRead")) = (pmethoddesc_read)',
 '$method_named(pclassdesc_child.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
 '$method_named(pclassdesc_bridge.METHODS,$ptascii("answer")) = (pmethoddesc_bridge_answer)',
 '$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
 'pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.OWNER = porigin_child '
 '/\\ pmethoddesc_bridge_answer.VISIBILITY = PROPERTY_PRIVATE /\\ '
 'pmethoddesc_grand_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.FUNCTION.ORIGIN '
 '=/= pmethoddesc_bridge_answer.FUNCTION.ORIGIN /\\ pmethoddesc_answer.FUNCTION.ORIGIN =/= '
 'pmethoddesc_grand_answer.FUNCTION.ORIGIN',
 '$property_hook_plan(S) = (ppropertyhook)',
 '$lookup(S_globals.ENV,$ptascii("child")) = (n_child_cell)',
 'S.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
 'S.OBJECTS[n_child] = INSTANCE porigin_child /\\ ppropertyhook.OBJECT = n_child /\\ '
 'ppropertyhook.PROPERTY = ppropertydesc_child.ORIGIN /\\ '
 '~$property_hook_backing(S,n_child,ppropertydesc_child)',
 '$property_effective_desc(S,n_child,$ptascii("value")) = (ppropertydesc_child)',
 '$objectprops_at(S.OBJECTPROPS,n_child) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME '
 'ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT PNULL) }])',
 '$origin_node(S.SOURCES,ppropertyhook.HOOK) = (NPropertyHook phpType14_hook phpType24_hook '
 'phpType4_hook phpType11_hook phpType16_hook phpType39_hook metadata_hook)',
 '~$hook_body_backed(phpType39_hook,ppropertydesc_child.NAME)',
 '$function_at(S.FUNCTIONS,ppropertyhook.HOOK) = (pfunction_hook)',
 'pfunction_hook.SIGNATURE = {PARAMETERS eps, RETURNS eps, BYREF false} /\\ pfunction_hook.NAME = '
 'pclassdesc_child.NAME ++ $ptascii("::$value::get") /\\ pfunction_hook.LINE = 17',
 '$obp_guard(S)']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--group', choices=['remove', 'add', 'control'], required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'ordinary_backed_parent_unbacked_get_hook_type_presence_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    clauses, negatives, case_index, start_stage = {
        'remove': (REMOVE, DERIVED, 0, None),
        'add': (ADD, [], 1, None),
        'control': (CONTROL, [], 2, 0),
    }[args.group]
    selections = [(args.group, clauses, negatives)]
    cases = [data['cases'][case_index]]
    sources = [HERE / ('ordinary-backed-parent-unbacked-get-hook-type-presence-' + ['remove', 'add', 'control'][case_index] + '.php')]
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
    out = Path(tempfile.mkdtemp(prefix='ordinary-backed-parent-unbacked-get-hook-type-presence-protocol-', dir=ROOT / '.tools'))
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
                     'S_found = $obp_seek(S_initial,' + str(start_stage) + ',1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            if args.group in ('remove', 'add'):
                setup = [setup[0].replace('S_initial =', 'S =', 1)]
            content += '\ndec $obp_' + name + '() : bool\ndef $obp_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $obp_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = (' + ' /\\ '.join('$obp_' + name + '()' for name, _, _ in selections) + ')\n'
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
