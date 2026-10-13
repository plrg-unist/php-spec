"""Check plain-child TYPE-presence diagnostics and the inherited untyped getter contract."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()



PREFIX = ('dec $ppres_replace(pcoccurrence*,pcpath,pcnode) : pcoccurrence*\n'
 'def $ppres_replace(eps,pcpath,pcnode) = eps\n'
 'def $ppres_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath pcnode) :: '
 'pcoccurrence*\n'
 'def $ppres_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath_other '
 'pcnode_old) :: $ppres_replace(pcoccurrence*,pcpath,pcnode)\n'
 '  -- if pcpath_other =/= pcpath\n'
 'dec $ppres_stage(pstate,nat) : bool\n'
 'def $ppres_stage(S,0) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n'
 '  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n'
 '  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n'
 '  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n'
 '  -- if $ptlc(pclassdesc.NAME) = $ptascii("presenceplain61child")\n'
 'def $ppres_stage(S,4) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*\n'
 'def $ppres_stage(S,5) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if $ptlc(pcallcontext.NAME) = $ptascii("presenceplain61parent::answer")\n'
 'def $ppres_stage(S,n) = false -- otherwise\n'
 '\n'
 'dec $ppres_seek(pstate,nat,nat) : pstate\n'
 'def $ppres_seek(S,n_stage,n) = S\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if $ppres_stage(S,n_stage) \\/ n = 0\n'
 'def $ppres_seek(S,n_stage,n) = $ppres_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if ~$ppres_stage(S,n_stage) /\\ $(n > 0)\n'
 'def $ppres_seek(S,n_stage,n) = $ppres_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
 '  -- if $throwable_pending(S.COMPLETION) /\\ $(n > 0)\n'
 'def $ppres_seek(S,n_stage,n) = S -- otherwise\n'
 'dec $ppres_guard(pstate) : bool\n'
 'def $ppres_guard(S) = ($call_descriptors_valid(S) /\\ $declaration_history_valid(S) /\\ $property_state_valid(S) /\\ '
 '$heap_valid($heap_prune($heap_graph(S))))\n'
 'dec $ppres_class_replace(pclassdesc*,porigin,pclassdesc) : pclassdesc*\n'
 'def $ppres_class_replace(eps,porigin,pclassdesc) = eps\n'
 'def $ppres_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_new :: pclassdesc*\n'
 '  -- if pclassdesc_old.ORIGIN = porigin\n'
 'def $ppres_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_old :: '
 '$ppres_class_replace(pclassdesc*,porigin,pclassdesc_new)\n'
 '  -- if pclassdesc_old.ORIGIN =/= porigin\n')

REMOVE = ['ptbytes_message = $ptascii("Type of PresencePlainRemove61Child::$value must be subtype of int (as in class '
 'PresencePlainRemove61Parent)")',
 'S.COMPLETION = STATICBYTES ptbytes_message 13 /\\ S.EVENTS = eps /\\ S.OBJECTS = eps /\\ S.OBJECTPROPS = eps',
 'S.CLASSES = [pclassdesc_parent,pclassdesc_bridge,pclassdesc_child,pclassdesc_grand]',
 'pclassdesc_parent.NAME = $ptascii("PresencePlainRemove61Parent") /\\ pclassdesc_bridge.NAME = '
 '$ptascii("PresencePlainRemove61Bridge") /\\ pclassdesc_child.NAME = $ptascii("PresencePlainRemove61Child") /\\ '
 'pclassdesc_grand.NAME = $ptascii("PresencePlainRemove61Grand")',
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ |pclassdesc_child.PROPERTIES| = 1 /\\ pclassdesc_bridge.PROPERTIES = eps /\\ '
 'pclassdesc_grand.PROPERTIES = eps',
 'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
 'ppropertydesc_parent.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ ppropertydesc_child.TYPE = eps',
 '$property_default_state(S,ppropertydesc_parent) = (PROP_INITIAL) /\\ $property_default_state(S,ppropertydesc_child) = '
 '(PROP_VALUE (DIRECT (PINT 200)))',
 '$property_hook_origin(S,ppropertydesc_parent) = (porigin_hook_parent)',
 '$property_hook_origin(S,ppropertydesc_child) = eps /\\ $property_hook_get_declaration(S,ppropertydesc_child) = eps',
 '$function_at(S.FUNCTIONS,porigin_hook_parent) = (pfunction_hook)',
 'pfunction_hook.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_parent.TYPE, BYREF false} /\\ pfunction_hook.NAME = '
 'pclassdesc_parent.NAME ++ $ptascii("::$value::get") /\\ pfunction_hook.LINE = 4',
 '$property_layout(S,pclassdesc_bridge.ORIGIN,|S.CLASSES|) = [ppropertydesc_parent]',
 'pclassdesc_parent.PARENT = eps /\\ pclassdesc_bridge.PARENT = (pclassdesc_parent.NAME) /\\ pclassdesc_child.PARENT = '
 '(pclassdesc_bridge.NAME) /\\ pclassdesc_child.LINE = 13',
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_parent.NAME)) = (pclassdesc_parent.ORIGIN) /\\ '
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_bridge.NAME)) = (pclassdesc_bridge.ORIGIN) /\\ '
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_child.NAME)) = eps /\\ $class_named(S.CLASSNAMES,$ptlc(pclassdesc_grand.NAME)) = '
 'eps',
 '$class_link_at(S.LINKEDPARENTS,pclassdesc_parent.ORIGIN) = eps /\\ $class_link_at(S.LINKEDPARENTS,pclassdesc_bridge.ORIGIN) = '
 '(SOURCE_PARENT pclassdesc_parent.ORIGIN) /\\ $class_link_at(S.LINKEDPARENTS,pclassdesc_child.ORIGIN) = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,pclassdesc_grand.ORIGIN) = eps',
 '$property_hook_virtual(S,ppropertydesc_parent) /\\ $property_hook_virtual_chain(S,ppropertydesc_parent,1) /\\ '
 '~$property_hook_override_backed(S,ppropertydesc_parent) /\\ '
 '~$property_hook_ordinary_backing(S,ppropertydesc_parent,|S.CLASSES|) /\\ '
 '~$property_hook_inherited_backing(S,ppropertydesc_parent)',
 '$property_hook_plain_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child,1) /\\ '
 '$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child)',
 '$property_hook_covariance(S,ppropertydesc_parent,ppropertydesc_child) = PVUNSUPPORTED "covariance requires two present '
 'normalized types and named class contexts"',
 '~$property_hook_plain_edge(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) /\\ '
 '~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child) /\\ $property_hook_getter(S,ppropertydesc_child) = '
 'eps',
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) = '
 '(ptbytes_message)',
 '$property_hook_covariance_message(S,ppropertydesc_parent,ppropertydesc_child,PVINCOMPATIBLE) = (ptbytes_message)',
 '$property_hook_covariance_error_site(S,[ppropertydesc_parent],ppropertydesc_child,ptbytes_message) = eps',
 'S.TODO = eps /\\ S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.ENV = eps /\\ S.ERRORORIGIN = eps /\\ $declaration_history_valid(S) '
 '/\\ $class_links_valid(S)',
 'porigin_parent = pclassdesc_parent.ORIGIN',
 'porigin_child = pclassdesc_child.ORIGIN',
 '$origin_node(S.SOURCES,porigin_hook_parent) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook '
 'phpType16_hook phpType39_hook metadata_hook)',
 'porigin_hook_parent = PORIGIN n_hook pcpath_hook',
 'S.SOURCES = pcunit :: pcunit_tail*',
 'pcunit.ID = n_hook',
 'ppropertydesc_child.ORIGIN = PORIGIN n_child pcpath_child',
 'pcpath_child_group = pcpath_child[0:$nabs($(|pcpath_child| - 2))]',
 '$origin_node(S.SOURCES,PORIGIN n_child pcpath_child_group) = (NStmtProperty phpType14_child (INTEGER flags_child) '
 'phpType18_child phpType56_child phpType37_child metadata_child)',
 'phpType14_child = SEQUENCE eps /\\ phpType37_child = SEQUENCE eps /\\ flags_child <- [0,1] /\\ '
 '$trait_property_source_type(S,ppropertydesc_child) = eps']

ADD = ['ptbytes_message = $ptascii("Type of PresencePlainAdd61Child::$value must be omitted to match the parent definition in class '
 'PresencePlainAdd61Parent")',
 'S.COMPLETION = STATICBYTES ptbytes_message 13 /\\ S.EVENTS = eps /\\ S.OBJECTS = eps /\\ S.OBJECTPROPS = eps',
 'S.CLASSES = [pclassdesc_parent,pclassdesc_bridge,pclassdesc_child,pclassdesc_grand]',
 'pclassdesc_parent.NAME = $ptascii("PresencePlainAdd61Parent") /\\ pclassdesc_bridge.NAME = '
 '$ptascii("PresencePlainAdd61Bridge") /\\ pclassdesc_child.NAME = $ptascii("PresencePlainAdd61Child") /\\ pclassdesc_grand.NAME '
 '= $ptascii("PresencePlainAdd61Grand")',
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ |pclassdesc_child.PROPERTIES| = 1 /\\ pclassdesc_bridge.PROPERTIES = eps /\\ '
 'pclassdesc_grand.PROPERTIES = eps',
 'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
 'ppropertydesc_parent.TYPE = eps /\\ ppropertydesc_child.TYPE = [PTBRANCH ([PTBUILTIN "int"])]',
 '$property_default_state(S,ppropertydesc_parent) = (PROP_VALUE (DIRECT PNULL)) /\\ '
 '$property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT (PINT 200)))',
 '$property_hook_origin(S,ppropertydesc_parent) = (porigin_hook_parent)',
 '$property_hook_origin(S,ppropertydesc_child) = eps /\\ $property_hook_get_declaration(S,ppropertydesc_child) = eps',
 '$function_at(S.FUNCTIONS,porigin_hook_parent) = (pfunction_hook)',
 'pfunction_hook.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_parent.TYPE, BYREF false} /\\ pfunction_hook.NAME = '
 'pclassdesc_parent.NAME ++ $ptascii("::$value::get") /\\ pfunction_hook.LINE = 4',
 '$property_layout(S,pclassdesc_bridge.ORIGIN,|S.CLASSES|) = [ppropertydesc_parent]',
 'pclassdesc_parent.PARENT = eps /\\ pclassdesc_bridge.PARENT = (pclassdesc_parent.NAME) /\\ pclassdesc_child.PARENT = '
 '(pclassdesc_bridge.NAME) /\\ pclassdesc_child.LINE = 13',
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_parent.NAME)) = (pclassdesc_parent.ORIGIN) /\\ '
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_bridge.NAME)) = (pclassdesc_bridge.ORIGIN) /\\ '
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_child.NAME)) = eps /\\ $class_named(S.CLASSNAMES,$ptlc(pclassdesc_grand.NAME)) = '
 'eps',
 '$class_link_at(S.LINKEDPARENTS,pclassdesc_parent.ORIGIN) = eps /\\ $class_link_at(S.LINKEDPARENTS,pclassdesc_bridge.ORIGIN) = '
 '(SOURCE_PARENT pclassdesc_parent.ORIGIN) /\\ $class_link_at(S.LINKEDPARENTS,pclassdesc_child.ORIGIN) = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,pclassdesc_grand.ORIGIN) = eps',
 '$property_hook_virtual(S,ppropertydesc_parent) /\\ $property_hook_virtual_chain(S,ppropertydesc_parent,1) /\\ '
 '~$property_hook_override_backed(S,ppropertydesc_parent) /\\ '
 '~$property_hook_ordinary_backing(S,ppropertydesc_parent,|S.CLASSES|) /\\ '
 '~$property_hook_inherited_backing(S,ppropertydesc_parent)',
 '~$property_hook_plain_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child,1) /\\ '
 '~$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child)',
 '$property_hook_covariance(S,ppropertydesc_parent,ppropertydesc_child) = PVUNSUPPORTED "covariance requires two present '
 'normalized types and named class contexts"',
 '~$property_hook_plain_edge(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) /\\ '
 '~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child) /\\ $property_hook_getter(S,ppropertydesc_child) = '
 'eps',
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) = '
 '(ptbytes_message)',
 '$property_hook_covariance_message(S,ppropertydesc_parent,ppropertydesc_child,PVINCOMPATIBLE) = eps /\\ '
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child)',
 '$property_hook_covariance_error_site(S,[ppropertydesc_parent],ppropertydesc_child,ptbytes_message) = eps',
 'S.TODO = eps /\\ S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.ENV = eps /\\ S.ERRORORIGIN = eps /\\ $declaration_history_valid(S) '
 '/\\ $class_links_valid(S)']

COMMON = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("PresencePlain61Parent"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("PresencePlain61Bridge"))) = (porigin_bridge)',
 '$class_at(S.CLASSES,porigin_bridge) = (pclassdesc_bridge)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("PresencePlain61Child"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("PresencePlain61Grand"))) = (porigin_grand)',
 '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
 'pclassdesc_parent.PARENT = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_parent) = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_bridge) = (SOURCE_PARENT porigin_parent) /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_bridge) /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_child)',
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ |pclassdesc_child.PROPERTIES| = 1 /\\ pclassdesc_bridge.PROPERTIES = eps /\\ '
 'pclassdesc_grand.PROPERTIES = eps',
 'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
 'ppropertydesc_parent.TYPE = eps /\\ ppropertydesc_child.TYPE = eps /\\ $property_default_state(S,ppropertydesc_parent) = '
 '(PROP_VALUE (DIRECT PNULL)) /\\ $property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT (PINT 200)))',
 '$property_layout(S,porigin_bridge,|S.CLASSES|) = [ppropertydesc_parent] /\\ $property_layout(S,porigin_grand,|S.CLASSES|) = '
 '[ppropertydesc_child]',
 '$property_hook_origin(S,ppropertydesc_parent) = (porigin_hook_parent)',
 '$property_hook_origin(S,ppropertydesc_child) = eps /\\ ~$property_hook_override_backed(S,ppropertydesc_parent) /\\ '
 '~$property_hook_inherited_backing(S,ppropertydesc_parent) /\\ '
 '~$property_hook_ordinary_backing(S,ppropertydesc_parent,|S.CLASSES|) /\\ $property_hook_virtual(S,ppropertydesc_parent) /\\ '
 '$property_hook_virtual_chain(S,ppropertydesc_parent,|S.CLASSES|) /\\ ~$property_hook_virtual(S,ppropertydesc_child)',
 '$property_hook_getter(S,ppropertydesc_child) = (ppropertydesc_parent) /\\ '
 '$property_hook_effective_origin(S,ppropertydesc_child) = (porigin_hook_parent) /\\ '
 '$property_hook_plain_getter_walk(S,ppropertydesc_child,|S.CLASSES|) = (ppropertydesc_parent)',
 '$property_hook_plain_edge(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) /\\ '
 '$property_hook_plain_over_backed(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) /\\ '
 '$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_override_shape(S,ppropertydesc_parent,ppropertydesc_child) /\\ $ppres_guard(S)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("parentRead")) = (pmethoddesc_read)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
 '$method_named(pclassdesc_child.METHODS,$ptascii("answer")) = (pmethoddesc_child_answer)',
 '$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
 'pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.OWNER = porigin_parent /\\ '
 'pmethoddesc_child_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_grand_answer.VISIBILITY = PROPERTY_PRIVATE /\\ '
 'pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_child_answer.FUNCTION.ORIGIN /\\ pmethoddesc_answer.FUNCTION.ORIGIN =/= '
 'pmethoddesc_grand_answer.FUNCTION.ORIGIN',
 '$origin_node(S.SOURCES,porigin_hook_parent) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook '
 'phpType16_hook phpType39_hook metadata_hook)',
 '~$hook_body_backed(phpType39_hook,ppropertydesc_parent.NAME) /\\ ppropertydesc_parent.DEFAULT = PROP_NULL',
 'ppropertydesc_child.ORIGIN = PORIGIN n_child pcpath_child',
 'pcpath_child_group = pcpath_child[0:$nabs($(|pcpath_child| - 2))]',
 '$origin_node(S.SOURCES,PORIGIN n_child pcpath_child_group) = (NStmtProperty phpType14_child (INTEGER flags_child) '
 'phpType18_child phpType56_child phpType37_child metadata_child)',
 'phpType14_child = SEQUENCE eps /\\ phpType37_child = SEQUENCE eps /\\ flags_child <- [0,1]',
 'S_global = $global_table_view(S)',
 '$lookup(S_global.ENV,$ptascii("parent")) = (n_parent_cell)',
 'S_global.STORE[n_parent_cell] = DEFINED (POBJECT n_parent)',
 'S_global.OBJECTS[n_parent] = INSTANCE porigin_parent /\\ $objectprops_at(S_global.OBJECTPROPS,n_parent) = (eps)',
 '~$property_hook_plain_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) /\\ '
 '~$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '$property_hook_covariance(S,ppropertydesc_parent,ppropertydesc_child) = PVUNSUPPORTED "covariance requires two present '
 'normalized types and named class contexts"',
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) = eps']

CONTROL = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("PresencePlain61Parent"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("PresencePlain61Bridge"))) = (porigin_bridge)',
 '$class_at(S.CLASSES,porigin_bridge) = (pclassdesc_bridge)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("PresencePlain61Child"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("PresencePlain61Grand"))) = (porigin_grand)',
 '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
 'pclassdesc_parent.PARENT = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_parent) = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_bridge) = (SOURCE_PARENT porigin_parent) /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_bridge) /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_child)',
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ |pclassdesc_child.PROPERTIES| = 1 /\\ pclassdesc_bridge.PROPERTIES = eps /\\ '
 'pclassdesc_grand.PROPERTIES = eps',
 'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
 'ppropertydesc_parent.TYPE = eps /\\ ppropertydesc_child.TYPE = eps /\\ $property_default_state(S,ppropertydesc_parent) = '
 '(PROP_VALUE (DIRECT PNULL)) /\\ $property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT (PINT 200)))',
 '$property_layout(S,porigin_bridge,|S.CLASSES|) = [ppropertydesc_parent] /\\ $property_layout(S,porigin_grand,|S.CLASSES|) = '
 '[ppropertydesc_child]',
 '$property_hook_origin(S,ppropertydesc_parent) = (porigin_hook_parent)',
 '$property_hook_origin(S,ppropertydesc_child) = eps /\\ ~$property_hook_override_backed(S,ppropertydesc_parent) /\\ '
 '~$property_hook_inherited_backing(S,ppropertydesc_parent) /\\ '
 '~$property_hook_ordinary_backing(S,ppropertydesc_parent,|S.CLASSES|) /\\ $property_hook_virtual(S,ppropertydesc_parent) /\\ '
 '$property_hook_virtual_chain(S,ppropertydesc_parent,|S.CLASSES|) /\\ ~$property_hook_virtual(S,ppropertydesc_child)',
 '$property_hook_getter(S,ppropertydesc_child) = (ppropertydesc_parent) /\\ '
 '$property_hook_effective_origin(S,ppropertydesc_child) = (porigin_hook_parent) /\\ '
 '$property_hook_plain_getter_walk(S,ppropertydesc_child,|S.CLASSES|) = (ppropertydesc_parent)',
 '$property_hook_plain_edge(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) /\\ '
 '$property_hook_plain_over_backed(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) /\\ '
 '$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_override_shape(S,ppropertydesc_parent,ppropertydesc_child) /\\ $ppres_guard(S)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("parentRead")) = (pmethoddesc_read)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
 '$method_named(pclassdesc_child.METHODS,$ptascii("answer")) = (pmethoddesc_child_answer)',
 '$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
 'pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.OWNER = porigin_parent /\\ '
 'pmethoddesc_child_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_grand_answer.VISIBILITY = PROPERTY_PRIVATE /\\ '
 'pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_child_answer.FUNCTION.ORIGIN /\\ pmethoddesc_answer.FUNCTION.ORIGIN =/= '
 'pmethoddesc_grand_answer.FUNCTION.ORIGIN',
 '$origin_node(S.SOURCES,porigin_hook_parent) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook '
 'phpType16_hook phpType39_hook metadata_hook)',
 '~$hook_body_backed(phpType39_hook,ppropertydesc_parent.NAME) /\\ ppropertydesc_parent.DEFAULT = PROP_NULL',
 'ppropertydesc_child.ORIGIN = PORIGIN n_child pcpath_child',
 'pcpath_child_group = pcpath_child[0:$nabs($(|pcpath_child| - 2))]',
 '$origin_node(S.SOURCES,PORIGIN n_child pcpath_child_group) = (NStmtProperty phpType14_child (INTEGER flags_child) '
 'phpType18_child phpType56_child phpType37_child metadata_child)',
 'phpType14_child = SEQUENCE eps /\\ phpType37_child = SEQUENCE eps /\\ flags_child <- [0,1]',
 'S_global = $global_table_view(S)',
 '$lookup(S_global.ENV,$ptascii("parent")) = (n_parent_cell)',
 'S_global.STORE[n_parent_cell] = DEFINED (POBJECT n_parent)',
 'S_global.OBJECTS[n_parent] = INSTANCE porigin_parent /\\ $objectprops_at(S_global.OBJECTPROPS,n_parent) = (eps)',
 '~$property_hook_plain_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) /\\ '
 '~$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '$property_hook_covariance(S,ppropertydesc_parent,ppropertydesc_child) = PVUNSUPPORTED "covariance requires two present '
 'normalized types and named class contexts"',
 '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) = eps',
 'S.CURRENT = (pcallcontext_hook)',
 'pcallcontext_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook',
 'S.FRAMES = pframe_hook :: pframe_tail*',
 'S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin_child',
 'ppropertyhook.PROPERTY = ppropertydesc_child.ORIGIN /\\ ppropertyhook.HOOK = porigin_hook_parent /\\ '
 'pcallcontext_hook.FUNCTION = porigin_hook_parent /\\ pcallcontext_hook.RECEIVER = (ppropertyhook.OBJECT)',
 'pcallcontext_hook.LEXICAL_CLASS = (porigin_parent) /\\ pcallcontext_hook.CALLED_CLASS = (porigin_child)',
 '$property_hook_function(S,ppropertyhook) = (pfunction_hook)',
 'pfunction_hook.NAME = pclassdesc_parent.NAME ++ $ptascii("::$value::get") /\\ pfunction_hook.SIGNATURE = {PARAMETERS eps, '
 'RETURNS ppropertydesc_parent.TYPE, BYREF false} /\\ pfunction_hook.LINE = 4',
 '$property_effective_desc(S,ppropertyhook.OBJECT,$ptascii("value")) = (ppropertydesc_child)',
 '$objectprops_at(S.OBJECTPROPS,ppropertyhook.OBJECT) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, '
 'STATE PROP_VALUE (DIRECT (PINT 200)) }])',
 '~$property_hook_backing(S,ppropertyhook.OBJECT,ppropertydesc_child) /\\ '
 '~$property_hook_backing(S,ppropertyhook.OBJECT,ppropertydesc_parent)',
 '$trace_context_class(S,pcallcontext_hook) = (pclassdesc_parent.NAME) /\\ $trace_context_function(S,pcallcontext_hook) = '
 '$ptascii("$value::get") /\\ $trace_context_type(S,pcallcontext_hook) = ($ptascii("->"))',
 '$property_hook_frame(S,pcallcontext_hook,pframe_hook,ppropertyhook)',
 '$ppres_guard(S)',
 'S_answer_found = $ppres_seek(S,5,1000)',
 'S_answer_found.COMPLETION = NORMAL \\/ S_answer_found.COMPLETION = BUDGET',
 'S_answer = S_answer_found[.COMPLETION = NORMAL]',
 'S_answer.CURRENT = (pcallcontext_answer)',
 'pcallcontext_answer.FUNCTION = pmethoddesc_answer.FUNCTION.ORIGIN /\\ pcallcontext_answer.LEXICAL_CLASS = (porigin_parent) /\\ '
 'pcallcontext_answer.CALLED_CLASS = (porigin_child) /\\ pcallcontext_answer.RECEIVER = (ppropertyhook.OBJECT) /\\ '
 '$call_context_valid(S_answer,pcallcontext_answer,S_answer.CVS)',
 '$ppres_guard(S_answer)',
 'S_entry_result_found = $ppres_seek(S_answer,4,1000)',
 'S_entry_result_found.COMPLETION = NORMAL \\/ S_entry_result_found.COMPLETION = BUDGET',
 'S_entry_result = S_entry_result_found[.COMPLETION = NORMAL]',
 'S_entry_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask_entry_result*',
 'S_entry_result.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("13"))) /\\ S_entry_result.CURRENT = eps',
 '$objectprops_at(S_entry_result.OBJECTPROPS,ppropertyhook.OBJECT) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME '
 'ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 200)) }])',
 '$string_carrier_valid(S_entry_result,PSTRING_CARRIER INTERNED_STRING ($ptascii("13"))) /\\ $ppres_guard(S_entry_result)']

DERIVED = ['~$property_hook_plain_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child,0)',
 '$property_hook_plain_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child,1)',
 '~$property_hook_virtual_chain(S,ppropertydesc_parent,0) /\\ $property_hook_virtual_chain(S,ppropertydesc_parent,1)',
 '~$property_hook_plain_covariance_parent(S,ppropertydesc_parent[.TYPE = eps],ppropertydesc_child,|S.CLASSES|)',
 '~$property_hook_plain_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child[.TYPE = [PTBRANCH ([PTBUILTIN '
 '"int"])]],|S.CLASSES|)',
 '~$property_hook_plain_covariance_parent(S,ppropertydesc_parent[.STATIC = true],ppropertydesc_child,|S.CLASSES|)',
 '~$property_hook_plain_covariance_parent(S,ppropertydesc_parent[.READONLY = true],ppropertydesc_child,|S.CLASSES|)',
 '~$property_hook_plain_covariance_parent(S,ppropertydesc_parent[.FINAL = true],ppropertydesc_child,|S.CLASSES|)',
 '~$property_hook_plain_covariance_parent(S,ppropertydesc_parent[.VISIBILITY = '
 'PROPERTY_PRIVATE],ppropertydesc_child,|S.CLASSES|)',
 '~$property_hook_plain_covariance_parent(S,ppropertydesc_parent[.SETVISIBILITY = '
 '(PROPERTY_PROTECTED)],ppropertydesc_child,|S.CLASSES|)',
 '~$property_hook_plain_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child[.STATIC = true],|S.CLASSES|)',
 '~$property_hook_plain_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child[.READONLY = true],|S.CLASSES|)',
 '~$property_hook_plain_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child[.FINAL = true],|S.CLASSES|)',
 '~$property_hook_plain_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child[.VISIBILITY = '
 'PROPERTY_PRIVATE],|S.CLASSES|)',
 '~$property_hook_plain_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child[.SETVISIBILITY = '
 '(PROPERTY_PROTECTED)],|S.CLASSES|)',
 'S_child_own = S[.CLASSES = $ppres_class_replace(S.CLASSES,porigin_child,pclassdesc_child[.PROPERTIES = eps])]',
 '~$property_hook_plain_covariance_parent(S_child_own,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|)',
 'S_parent_own = S[.CLASSES = $ppres_class_replace(S.CLASSES,porigin_parent,pclassdesc_parent[.PROPERTIES = eps])]',
 '~$property_hook_plain_covariance_parent(S_parent_own,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|)',
 'S_parent_link = S[.LINKEDPARENTS = (CLASSLINK porigin_parent (SOURCE_PARENT porigin_parent)) :: S.LINKEDPARENTS]',
 '~$property_hook_plain_covariance_parent(S_parent_link,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|)',
 'S_byref = S[.SOURCES = pcunit[.OCCURRENCES = $ppres_replace(pcunit.OCCURRENCES,pcpath_hook,NPropertyHook phpType14_hook '
 'phpType24_hook (BOOLEAN true) phpType11_hook phpType16_hook phpType39_hook metadata_hook)] :: pcunit_tail*]',
 '~$property_hook_plain_covariance_parent(S_byref,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|)',
 'S_name = S[.SOURCES = pcunit[.OCCURRENCES = $ppres_replace(pcunit.OCCURRENCES,pcpath_hook,NPropertyHook phpType14_hook '
 'phpType24_hook phpType4_hook (NIdentifier (BYTES "c2V0") metadata_hook) phpType16_hook phpType39_hook metadata_hook)] :: '
 'pcunit_tail*]',
 '~$property_hook_plain_covariance_parent(S_name,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|)',
 'S_child_hooks = S[.SOURCES = pcunit[.OCCURRENCES = $ppres_replace(pcunit.OCCURRENCES,pcpath_child_group,NStmtProperty '
 'phpType14_child (INTEGER flags_child) phpType18_child phpType56_child (SEQUENCE ([NPropertyHook phpType14_hook phpType24_hook '
 'phpType4_hook phpType11_hook phpType16_hook phpType39_hook metadata_hook])) metadata_child)] :: pcunit_tail*]',
 '~$property_hook_plain_covariance_parent(S_child_hooks,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|)',
 'S_child_flags = S[.SOURCES = pcunit[.OCCURRENCES = $ppres_replace(pcunit.OCCURRENCES,pcpath_child_group,NStmtProperty '
 'phpType14_child (INTEGER 2) phpType18_child phpType56_child phpType37_child metadata_child)] :: pcunit_tail*]',
 '~$property_hook_plain_covariance_parent(S_child_flags,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|)',
 'ppropertydesc_parent_default = ppropertydesc_parent[.DEFAULT = PROP_LITERAL (PINT 999)]',
 'S_parent_default = S[.CLASSES = $ppres_class_replace(S.CLASSES,porigin_parent,pclassdesc_parent[.PROPERTIES = '
 '[ppropertydesc_parent_default]])]',
 '~$property_hook_plain_covariance_parent(S_parent_default,ppropertydesc_parent_default,ppropertydesc_child,|S.CLASSES|)',
 '$property_hook_covariance_error_site(S,[ppropertydesc_parent],ppropertydesc_child,$ptascii("Type of '
 'PresencePlainRemove61Child::$value must be int (as in class PresencePlainRemove61Parent)")) = eps',
 '~$property_hook_missing_return_parent(S,ppropertydesc_parent,ppropertydesc_child)',
 '$property_hook_covariance_message(S,ppropertydesc_parent,ppropertydesc_child,PVCOMPATIBLE) = eps']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--group', choices=['remove', 'add', 'control'], required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'virtual_parent_plain_type_presence_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    clauses, negatives, case_index, start_stage = {
        'remove': (REMOVE, DERIVED, 0, 0),
        'add': (ADD, [], 1, 0),
        'control': (CONTROL, [], 2, 0),
    }[args.group]
    selections = [(args.group, clauses, negatives)]
    cases = [data['cases'][case_index]]
    sources = [HERE / ['virtual-parent-plain-type-presence-remove.php', 'virtual-parent-plain-type-presence-add.php', 'virtual-parent-plain-type-presence.php'][case_index]]
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
    out = Path(tempfile.mkdtemp(prefix='virtual-parent-plain-type-presence-protocol-', dir=ROOT / '.tools'))
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
                     'S_found = $ppres_seek(S_initial,' + str(start_stage) + ',1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            if args.group in ('remove', 'add'):
                setup = [setup[0].replace('S_initial =', 'S =', 1)]
            content += '\ndec $ppres_' + name + '() : bool\ndef $ppres_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $ppres_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = (' + ' /\\ '.join('$ppres_' + name + '()' for name, _, _ in selections) + ')\n'
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
