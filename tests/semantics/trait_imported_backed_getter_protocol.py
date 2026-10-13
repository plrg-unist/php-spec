"""Check imported backed getter identity, scope, physical stores and hooked conflicts."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()

PREFIX = ('dec $tih_replace(pcoccurrence*,pcpath,pcnode) : pcoccurrence*\n'
 'def $tih_replace(eps,pcpath,pcnode) = eps\n'
 'def $tih_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath pcnode) :: '
 'pcoccurrence*\n'
 'def $tih_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath_other '
 'pcnode_old) :: $tih_replace(pcoccurrence*,pcpath,pcnode)\n'
 '  -- if pcpath_other =/= pcpath\n'
 'dec $tih_stage(pstate,nat) : bool\n'
 'def $tih_stage(S,0) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n'
 '  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n'
 '  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n'
 '  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n'
 '  -- if $ptlc(pclassdesc.NAME) = $ptascii("importedbackedgetterconsumer63")\n'
 'def $tih_stage(S,2) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (ASSIGN_ARRAY pbase 30 b) :: ptask*\n'
 '  -- if S.RESULT = KNOWN (PINT 300)\n'
 'def $tih_stage(S,3) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n'
 '  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n'
 '  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n'
 '  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n'
 '  -- if $ptlc(pclassdesc.NAME) = $ptascii("importedbackedgettergrand63")\n'
 '  -- if $objectprops_at(S.OBJECTPROPS,ppropertyhook.OBJECT) = (ppropertyslot*)\n'
 '  -- if $property_slot_at(ppropertyslot*,$ptascii("value")) = (ppropertyslot_value)\n'
 '  -- if ppropertyslot_value.STATE = PROP_VALUE (DIRECT (PINT 300))\n'
 'def $tih_stage(S,4) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*\n'
 'def $tih_stage(S,5) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if $ptlc(pcallcontext.NAME) = $ptascii("importedbackedgetterconsumer63::answer")\n'
 'def $tih_stage(S,6) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata)) :: ptask*\n'
 '  -- if S.ORIGIN = (porigin)\n'
 '  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n'
 '  -- if pclassdesc.NAME = $ptascii("ImportedBackedCollisionConsumer63")\n'
 'def $tih_stage(S,n) = false -- otherwise\n'
 '\n'
 'dec $tih_seek(pstate,nat,nat) : pstate\n'
 'def $tih_seek(S,n_stage,n) = S\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if $tih_stage(S,n_stage) \\/ n = 0\n'
 'def $tih_seek(S,n_stage,n) = $tih_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if ~$tih_stage(S,n_stage) /\\ $(n > 0)\n'
 'def $tih_seek(S,n_stage,n) = $tih_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
 '  -- if $throwable_pending(S.COMPLETION) /\\ $(n > 0)\n'
 'def $tih_seek(S,n_stage,n) = S -- otherwise\n'
 'dec $tih_after(pstate,pstate) : pstate\n'
 'def $tih_after(S,S_next) = '
 '$gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))\n'
 'dec $tih_guard(pstate) : bool\n'
 'def $tih_guard(S) = ($call_descriptors_valid(S) /\\ $declaration_history_valid(S) /\\ $property_state_valid(S) /\\ '
 '$heap_valid($heap_prune($heap_graph(S))))\n'
 'dec $tih_class_replace(pclassdesc*,porigin,pclassdesc) : pclassdesc*\n'
 'def $tih_class_replace(eps,porigin,pclassdesc) = eps\n'
 'def $tih_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_new :: pclassdesc*\n'
 '  -- if pclassdesc_old.ORIGIN = porigin\n'
 'def $tih_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_old :: '
 '$tih_class_replace(pclassdesc*,porigin,pclassdesc_new)\n'
 '  -- if pclassdesc_old.ORIGIN =/= porigin\n')

COMMON = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedBackedGetterTrait63"))) = (porigin_trait)',
 '$class_at(S.CLASSES,porigin_trait) = (pclassdesc_trait)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedBackedGetterConsumer63"))) = (porigin_consumer)',
 '$class_at(S.CLASSES,porigin_consumer) = (pclassdesc_consumer)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedBackedGetterGrand63"))) = (porigin_grand)',
 '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
 'pclassdesc_trait.KIND = "trait" /\\ pclassdesc_consumer.KIND = "class" /\\ pclassdesc_consumer.PARENT = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_consumer) = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT '
 'porigin_consumer)',
 '|pclassdesc_trait.PROPERTIES| = 1 /\\ |pclassdesc_consumer.PROPERTIES| = 1 /\\ pclassdesc_grand.PROPERTIES = eps /\\ '
 'pclassdesc_trait.METHODS = eps',
 'ppropertydesc_source = pclassdesc_trait.PROPERTIES[0]',
 'ppropertydesc_consumer = pclassdesc_consumer.PROPERTIES[0]',
 'ppropertydesc_source.ORIGIN = porigin_property_source',
 'ppropertydesc_consumer.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_consumer porigin_property_source /\\ ppropertydesc_consumer = '
 '$trait_data_property(pclassdesc_consumer,ppropertydesc_source)',
 'ppropertydesc_source.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ ppropertydesc_consumer.TYPE = ppropertydesc_source.TYPE '
 '/\\ $property_default_state(S,ppropertydesc_consumer) = (PROP_VALUE (DIRECT (PINT 100)))',
 '$property_layout(S,porigin_consumer,|S.CLASSES|) = [ppropertydesc_consumer] /\\ '
 '$property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_consumer]',
 '$trait_plan(S,pclassdesc_consumer).TRAITS = [pclassdesc_trait.NAME] /\\ $trait_plan(S,pclassdesc_consumer).PRECEDENCES = '
 'eps /\\ $trait_plan(S,pclassdesc_consumer).ALIASES = eps',
 '$property_hook_origin(S,ppropertydesc_source) = (porigin_hook_source)',
 '$property_hook_trait_origin(S,ppropertydesc_consumer) = (porigin_hook)',
 'porigin_hook = TRAIT_ORIGIN porigin_consumer porigin_hook_source ($hook_name(ppropertydesc_consumer.NAME)) /\\ '
 '$property_hook_origin(S,ppropertydesc_consumer) = (porigin_hook)',
 '$property_hook_getter(S,ppropertydesc_consumer) = (ppropertydesc_consumer) /\\ '
 '$property_hook_effective_origin(S,ppropertydesc_consumer) = (porigin_hook) /\\ '
 '~$property_hook_virtual(S,ppropertydesc_consumer)',
 '$function_at(S.FUNCTIONS,porigin_hook_source) = (pfunction_source)',
 'S.FUNCTIONS = [pfunction_source] /\\ $function_at(S.FUNCTIONS,porigin_hook) = eps /\\ '
 '$method_named(pclassdesc_consumer.METHODS,$hook_name(ppropertydesc_consumer.NAME)) = eps',
 '$property_hook_trait_function(S,ppropertydesc_consumer) = (pfunction_hook)',
 '$function_at($all_functions(S),porigin_hook) = (pfunction_hook)',
 'pfunction_hook.ORIGIN = porigin_hook /\\ pfunction_hook.NAME = pclassdesc_consumer.NAME ++ $ptascii("::$value::get") /\\ '
 'pfunction_source.NAME = pclassdesc_trait.NAME ++ $ptascii("::$value::get")',
 'pfunction_hook.CODE = pfunction_source.CODE /\\ pfunction_hook.BODY = pfunction_source.BODY /\\ pfunction_hook.CVS = '
 'pfunction_source.CVS /\\ pfunction_hook.ENV = pfunction_source.ENV',
 'pfunction_hook.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_consumer.TYPE, BYREF false} /\\ '
 'pfunction_hook.SIGNATURE = pfunction_source.SIGNATURE /\\ pfunction_hook.DEFAULTS = eps /\\ ~pfunction_hook.EARLY /\\ '
 'pfunction_hook.LINE = 4',
 'porigin_hook_source = PORIGIN n_source pcpath_hook',
 '$origin_node(S.SOURCES,porigin_hook_source) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook '
 'phpType16_hook phpType39_hook metadata_hook)',
 '$hook_body_backed(phpType39_hook,ppropertydesc_source.NAME) /\\ $property_hook_source_declared(S,ppropertydesc_source) '
 '/\\ $property_hook_source_declared(S,ppropertydesc_consumer) /\\ '
 '$property_hook_trait_import_supported(S,pclassdesc_consumer,ppropertydesc_source)',
 '$origin_node(S.SOURCES,PORIGIN n_source (pcpath_hook ++ [PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 5])) = '
 '(NScalarMagicConstMethod metadata_magic)',
 '$method_named(pclassdesc_consumer.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
 '$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
 'pmethoddesc_answer.OWNER = porigin_consumer /\\ pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\\ '
 'pmethoddesc_grand_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.FUNCTION.ORIGIN =/= '
 'pmethoddesc_grand_answer.FUNCTION.ORIGIN',
 'S_global = $global_table_view(S)',
 '$lookup(S_global.ENV,$ptascii("consumer")) = (n_consumer_cell)',
 'S_global.STORE[n_consumer_cell] = DEFINED (POBJECT n_consumer_object)',
 '$lookup(S_global.ENV,$ptascii("grand")) = (n_grand_cell)',
 'S_global.STORE[n_grand_cell] = DEFINED (POBJECT n_grand)',
 'S.OBJECTS[n_consumer_object] = INSTANCE porigin_consumer /\\ S.OBJECTS[n_grand] = INSTANCE porigin_grand',
 '$objectprops_at(S.OBJECTPROPS,n_consumer_object) = ([{DECL (ppropertydesc_consumer.ORIGIN), NAME '
 'ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}]) /\\ $objectprops_at(S.OBJECTPROPS,n_grand) = ([{DECL '
 '(ppropertydesc_consumer.ORIGIN), NAME ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}])',
 '$tih_guard(S)']

CONTROLS = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedBackedGetterTrait63"))) = (porigin_trait)',
 '$class_at(S.CLASSES,porigin_trait) = (pclassdesc_trait)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedBackedGetterConsumer63"))) = (porigin_consumer)',
 '$class_at(S.CLASSES,porigin_consumer) = (pclassdesc_consumer)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedBackedGetterGrand63"))) = (porigin_grand)',
 '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
 'pclassdesc_trait.KIND = "trait" /\\ pclassdesc_consumer.KIND = "class" /\\ pclassdesc_consumer.PARENT = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_consumer) = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT '
 'porigin_consumer)',
 '|pclassdesc_trait.PROPERTIES| = 1 /\\ |pclassdesc_consumer.PROPERTIES| = 1 /\\ pclassdesc_grand.PROPERTIES = eps /\\ '
 'pclassdesc_trait.METHODS = eps',
 'ppropertydesc_source = pclassdesc_trait.PROPERTIES[0]',
 'ppropertydesc_consumer = pclassdesc_consumer.PROPERTIES[0]',
 'ppropertydesc_source.ORIGIN = porigin_property_source',
 'ppropertydesc_consumer.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_consumer porigin_property_source /\\ ppropertydesc_consumer = '
 '$trait_data_property(pclassdesc_consumer,ppropertydesc_source)',
 'ppropertydesc_source.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ ppropertydesc_consumer.TYPE = ppropertydesc_source.TYPE '
 '/\\ $property_default_state(S,ppropertydesc_consumer) = (PROP_VALUE (DIRECT (PINT 100)))',
 '$property_layout(S,porigin_consumer,|S.CLASSES|) = [ppropertydesc_consumer] /\\ '
 '$property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_consumer]',
 '$trait_plan(S,pclassdesc_consumer).TRAITS = [pclassdesc_trait.NAME] /\\ $trait_plan(S,pclassdesc_consumer).PRECEDENCES = '
 'eps /\\ $trait_plan(S,pclassdesc_consumer).ALIASES = eps',
 '$property_hook_origin(S,ppropertydesc_source) = (porigin_hook_source)',
 '$property_hook_trait_origin(S,ppropertydesc_consumer) = (porigin_hook)',
 'porigin_hook = TRAIT_ORIGIN porigin_consumer porigin_hook_source ($hook_name(ppropertydesc_consumer.NAME)) /\\ '
 '$property_hook_origin(S,ppropertydesc_consumer) = (porigin_hook)',
 '$property_hook_getter(S,ppropertydesc_consumer) = (ppropertydesc_consumer) /\\ '
 '$property_hook_effective_origin(S,ppropertydesc_consumer) = (porigin_hook) /\\ '
 '~$property_hook_virtual(S,ppropertydesc_consumer)',
 '$function_at(S.FUNCTIONS,porigin_hook_source) = (pfunction_source)',
 'S.FUNCTIONS = [pfunction_source] /\\ $function_at(S.FUNCTIONS,porigin_hook) = eps /\\ '
 '$method_named(pclassdesc_consumer.METHODS,$hook_name(ppropertydesc_consumer.NAME)) = eps',
 '$property_hook_trait_function(S,ppropertydesc_consumer) = (pfunction_hook)',
 '$function_at($all_functions(S),porigin_hook) = (pfunction_hook)',
 'pfunction_hook.ORIGIN = porigin_hook /\\ pfunction_hook.NAME = pclassdesc_consumer.NAME ++ $ptascii("::$value::get") /\\ '
 'pfunction_source.NAME = pclassdesc_trait.NAME ++ $ptascii("::$value::get")',
 'pfunction_hook.CODE = pfunction_source.CODE /\\ pfunction_hook.BODY = pfunction_source.BODY /\\ pfunction_hook.CVS = '
 'pfunction_source.CVS /\\ pfunction_hook.ENV = pfunction_source.ENV',
 'pfunction_hook.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_consumer.TYPE, BYREF false} /\\ '
 'pfunction_hook.SIGNATURE = pfunction_source.SIGNATURE /\\ pfunction_hook.DEFAULTS = eps /\\ ~pfunction_hook.EARLY /\\ '
 'pfunction_hook.LINE = 4',
 'porigin_hook_source = PORIGIN n_source pcpath_hook',
 '$origin_node(S.SOURCES,porigin_hook_source) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook '
 'phpType16_hook phpType39_hook metadata_hook)',
 '$hook_body_backed(phpType39_hook,ppropertydesc_source.NAME) /\\ $property_hook_source_declared(S,ppropertydesc_source) '
 '/\\ $property_hook_source_declared(S,ppropertydesc_consumer) /\\ '
 '$property_hook_trait_import_supported(S,pclassdesc_consumer,ppropertydesc_source)',
 '$origin_node(S.SOURCES,PORIGIN n_source (pcpath_hook ++ [PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 5])) = '
 '(NScalarMagicConstMethod metadata_magic)',
 '$method_named(pclassdesc_consumer.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
 '$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
 'pmethoddesc_answer.OWNER = porigin_consumer /\\ pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\\ '
 'pmethoddesc_grand_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.FUNCTION.ORIGIN =/= '
 'pmethoddesc_grand_answer.FUNCTION.ORIGIN',
 'S_global = $global_table_view(S)',
 '$lookup(S_global.ENV,$ptascii("consumer")) = (n_consumer_cell)',
 'S_global.STORE[n_consumer_cell] = DEFINED (POBJECT n_consumer_object)',
 '$lookup(S_global.ENV,$ptascii("grand")) = (n_grand_cell)',
 'S_global.STORE[n_grand_cell] = DEFINED (POBJECT n_grand)',
 'S.OBJECTS[n_consumer_object] = INSTANCE porigin_consumer /\\ S.OBJECTS[n_grand] = INSTANCE porigin_grand',
 '$objectprops_at(S.OBJECTPROPS,n_consumer_object) = ([{DECL (ppropertydesc_consumer.ORIGIN), NAME '
 'ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}]) /\\ $objectprops_at(S.OBJECTPROPS,n_grand) = ([{DECL '
 '(ppropertydesc_consumer.ORIGIN), NAME ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}])',
 '$tih_guard(S)',
 '$tih_stage(S,0)']

ENTRY = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedBackedGetterTrait63"))) = (porigin_trait)',
 '$class_at(S.CLASSES,porigin_trait) = (pclassdesc_trait)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedBackedGetterConsumer63"))) = (porigin_consumer)',
 '$class_at(S.CLASSES,porigin_consumer) = (pclassdesc_consumer)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedBackedGetterGrand63"))) = (porigin_grand)',
 '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
 'pclassdesc_trait.KIND = "trait" /\\ pclassdesc_consumer.KIND = "class" /\\ pclassdesc_consumer.PARENT = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_consumer) = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT '
 'porigin_consumer)',
 '|pclassdesc_trait.PROPERTIES| = 1 /\\ |pclassdesc_consumer.PROPERTIES| = 1 /\\ pclassdesc_grand.PROPERTIES = eps /\\ '
 'pclassdesc_trait.METHODS = eps',
 'ppropertydesc_source = pclassdesc_trait.PROPERTIES[0]',
 'ppropertydesc_consumer = pclassdesc_consumer.PROPERTIES[0]',
 'ppropertydesc_source.ORIGIN = porigin_property_source',
 'ppropertydesc_consumer.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_consumer porigin_property_source /\\ ppropertydesc_consumer = '
 '$trait_data_property(pclassdesc_consumer,ppropertydesc_source)',
 'ppropertydesc_source.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ ppropertydesc_consumer.TYPE = ppropertydesc_source.TYPE '
 '/\\ $property_default_state(S,ppropertydesc_consumer) = (PROP_VALUE (DIRECT (PINT 100)))',
 '$property_layout(S,porigin_consumer,|S.CLASSES|) = [ppropertydesc_consumer] /\\ '
 '$property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_consumer]',
 '$trait_plan(S,pclassdesc_consumer).TRAITS = [pclassdesc_trait.NAME] /\\ $trait_plan(S,pclassdesc_consumer).PRECEDENCES = '
 'eps /\\ $trait_plan(S,pclassdesc_consumer).ALIASES = eps',
 '$property_hook_origin(S,ppropertydesc_source) = (porigin_hook_source)',
 '$property_hook_trait_origin(S,ppropertydesc_consumer) = (porigin_hook)',
 'porigin_hook = TRAIT_ORIGIN porigin_consumer porigin_hook_source ($hook_name(ppropertydesc_consumer.NAME)) /\\ '
 '$property_hook_origin(S,ppropertydesc_consumer) = (porigin_hook)',
 '$property_hook_getter(S,ppropertydesc_consumer) = (ppropertydesc_consumer) /\\ '
 '$property_hook_effective_origin(S,ppropertydesc_consumer) = (porigin_hook) /\\ '
 '~$property_hook_virtual(S,ppropertydesc_consumer)',
 '$function_at(S.FUNCTIONS,porigin_hook_source) = (pfunction_source)',
 'S.FUNCTIONS = [pfunction_source] /\\ $function_at(S.FUNCTIONS,porigin_hook) = eps /\\ '
 '$method_named(pclassdesc_consumer.METHODS,$hook_name(ppropertydesc_consumer.NAME)) = eps',
 '$property_hook_trait_function(S,ppropertydesc_consumer) = (pfunction_hook)',
 '$function_at($all_functions(S),porigin_hook) = (pfunction_hook)',
 'pfunction_hook.ORIGIN = porigin_hook /\\ pfunction_hook.NAME = pclassdesc_consumer.NAME ++ $ptascii("::$value::get") /\\ '
 'pfunction_source.NAME = pclassdesc_trait.NAME ++ $ptascii("::$value::get")',
 'pfunction_hook.CODE = pfunction_source.CODE /\\ pfunction_hook.BODY = pfunction_source.BODY /\\ pfunction_hook.CVS = '
 'pfunction_source.CVS /\\ pfunction_hook.ENV = pfunction_source.ENV',
 'pfunction_hook.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_consumer.TYPE, BYREF false} /\\ '
 'pfunction_hook.SIGNATURE = pfunction_source.SIGNATURE /\\ pfunction_hook.DEFAULTS = eps /\\ ~pfunction_hook.EARLY /\\ '
 'pfunction_hook.LINE = 4',
 'porigin_hook_source = PORIGIN n_source pcpath_hook',
 '$origin_node(S.SOURCES,porigin_hook_source) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook '
 'phpType16_hook phpType39_hook metadata_hook)',
 '$hook_body_backed(phpType39_hook,ppropertydesc_source.NAME) /\\ $property_hook_source_declared(S,ppropertydesc_source) '
 '/\\ $property_hook_source_declared(S,ppropertydesc_consumer) /\\ '
 '$property_hook_trait_import_supported(S,pclassdesc_consumer,ppropertydesc_source)',
 '$origin_node(S.SOURCES,PORIGIN n_source (pcpath_hook ++ [PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 5])) = '
 '(NScalarMagicConstMethod metadata_magic)',
 '$method_named(pclassdesc_consumer.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
 '$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
 'pmethoddesc_answer.OWNER = porigin_consumer /\\ pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\\ '
 'pmethoddesc_grand_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.FUNCTION.ORIGIN =/= '
 'pmethoddesc_grand_answer.FUNCTION.ORIGIN',
 'S_global = $global_table_view(S)',
 '$lookup(S_global.ENV,$ptascii("consumer")) = (n_consumer_cell)',
 'S_global.STORE[n_consumer_cell] = DEFINED (POBJECT n_consumer_object)',
 '$lookup(S_global.ENV,$ptascii("grand")) = (n_grand_cell)',
 'S_global.STORE[n_grand_cell] = DEFINED (POBJECT n_grand)',
 'S.OBJECTS[n_consumer_object] = INSTANCE porigin_consumer /\\ S.OBJECTS[n_grand] = INSTANCE porigin_grand',
 '$objectprops_at(S.OBJECTPROPS,n_consumer_object) = ([{DECL (ppropertydesc_consumer.ORIGIN), NAME '
 'ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}]) /\\ $objectprops_at(S.OBJECTPROPS,n_grand) = ([{DECL '
 '(ppropertydesc_consumer.ORIGIN), NAME ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}])',
 '$tih_guard(S)',
 'S.CURRENT = (pcallcontext_hook)',
 'pcallcontext_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook',
 'S.FRAMES = pframe_hook :: pframe_tail*',
 'ppropertyhook.OBJECT = n_consumer_object /\\ ppropertyhook.PROPERTY = ppropertydesc_consumer.ORIGIN /\\ '
 'ppropertyhook.HOOK = porigin_hook /\\ pcallcontext_hook.FUNCTION = porigin_hook /\\ pcallcontext_hook.RECEIVER = '
 '(n_consumer_object)',
 'pcallcontext_hook.LEXICAL_CLASS = (porigin_consumer) /\\ pcallcontext_hook.CALLED_CLASS = (porigin_consumer)',
 '$property_hook_function(S,ppropertyhook) = (pfunction_hook) /\\ $target_function(S,PROPERTY_HOOK_TARGET ppropertyhook) = '
 '(pfunction_hook)',
 '$property_hook_backing(S,n_consumer_object,ppropertydesc_consumer) /\\ '
 '~$property_hook_backing(S,n_consumer_object,ppropertydesc_source) /\\ '
 '~$property_hook_read_needed(S,n_consumer_object,ppropertydesc_consumer.NAME)',
 '~$property_hook_backing(S[.CURRENT = eps],n_consumer_object,ppropertydesc_consumer) /\\ '
 '$property_hook_read_needed(S[.CURRENT = eps],n_consumer_object,ppropertydesc_consumer.NAME)',
 '$target_lexical_class(S,PROPERTY_HOOK_TARGET ppropertyhook) = (porigin_consumer) /\\ '
 '$target_called_class(S,PROPERTY_HOOK_TARGET ppropertyhook) = (porigin_consumer)',
 '$trace_context_class(S,pcallcontext_hook) = (pclassdesc_consumer.NAME) /\\ $trace_context_function(S,pcallcontext_hook) = '
 '$ptascii("$value::get") /\\ $trace_context_type(S,pcallcontext_hook) = ($ptascii("->"))',
 '$property_hook_frame(S,pcallcontext_hook,pframe_hook,ppropertyhook)',
 'S_answer_found = $tih_seek(S,5,1000)',
 'S_answer_found.COMPLETION = NORMAL \\/ S_answer_found.COMPLETION = BUDGET',
 'S_answer = S_answer_found[.COMPLETION = NORMAL]',
 'S_answer.CURRENT = (pcallcontext_answer)',
 'pcallcontext_answer.FUNCTION = pmethoddesc_answer.FUNCTION.ORIGIN /\\ pcallcontext_answer.LEXICAL_CLASS = '
 '(porigin_consumer) /\\ pcallcontext_answer.CALLED_CLASS = (porigin_consumer)',
 '$tih_guard(S_answer)',
 'S_result_found = $tih_seek(S_answer,4,1000)',
 'S_result_found.COMPLETION = NORMAL \\/ S_result_found.COMPLETION = BUDGET',
 'S_result = S_result_found[.COMPLETION = NORMAL]',
 'S_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask_result*',
 'S_result.RESULT = KNOWN (PINT 113) /\\ S_result.CURRENT = eps',
 '$objectprops_at(S_result.OBJECTPROPS,n_consumer_object) = ([{DECL (ppropertydesc_consumer.ORIGIN), NAME '
 'ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}])',
 '$tih_guard(S_result)']

WRITE = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedBackedGetterTrait63"))) = (porigin_trait)',
 '$class_at(S.CLASSES,porigin_trait) = (pclassdesc_trait)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedBackedGetterConsumer63"))) = (porigin_consumer)',
 '$class_at(S.CLASSES,porigin_consumer) = (pclassdesc_consumer)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedBackedGetterGrand63"))) = (porigin_grand)',
 '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
 'pclassdesc_trait.KIND = "trait" /\\ pclassdesc_consumer.KIND = "class" /\\ pclassdesc_consumer.PARENT = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_consumer) = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT '
 'porigin_consumer)',
 '|pclassdesc_trait.PROPERTIES| = 1 /\\ |pclassdesc_consumer.PROPERTIES| = 1 /\\ pclassdesc_grand.PROPERTIES = eps /\\ '
 'pclassdesc_trait.METHODS = eps',
 'ppropertydesc_source = pclassdesc_trait.PROPERTIES[0]',
 'ppropertydesc_consumer = pclassdesc_consumer.PROPERTIES[0]',
 'ppropertydesc_source.ORIGIN = porigin_property_source',
 'ppropertydesc_consumer.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_consumer porigin_property_source /\\ ppropertydesc_consumer = '
 '$trait_data_property(pclassdesc_consumer,ppropertydesc_source)',
 'ppropertydesc_source.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ ppropertydesc_consumer.TYPE = ppropertydesc_source.TYPE '
 '/\\ $property_default_state(S,ppropertydesc_consumer) = (PROP_VALUE (DIRECT (PINT 100)))',
 '$property_layout(S,porigin_consumer,|S.CLASSES|) = [ppropertydesc_consumer] /\\ '
 '$property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_consumer]',
 '$trait_plan(S,pclassdesc_consumer).TRAITS = [pclassdesc_trait.NAME] /\\ $trait_plan(S,pclassdesc_consumer).PRECEDENCES = '
 'eps /\\ $trait_plan(S,pclassdesc_consumer).ALIASES = eps',
 '$property_hook_origin(S,ppropertydesc_source) = (porigin_hook_source)',
 '$property_hook_trait_origin(S,ppropertydesc_consumer) = (porigin_hook)',
 'porigin_hook = TRAIT_ORIGIN porigin_consumer porigin_hook_source ($hook_name(ppropertydesc_consumer.NAME)) /\\ '
 '$property_hook_origin(S,ppropertydesc_consumer) = (porigin_hook)',
 '$property_hook_getter(S,ppropertydesc_consumer) = (ppropertydesc_consumer) /\\ '
 '$property_hook_effective_origin(S,ppropertydesc_consumer) = (porigin_hook) /\\ '
 '~$property_hook_virtual(S,ppropertydesc_consumer)',
 '$function_at(S.FUNCTIONS,porigin_hook_source) = (pfunction_source)',
 'S.FUNCTIONS = [pfunction_source] /\\ $function_at(S.FUNCTIONS,porigin_hook) = eps /\\ '
 '$method_named(pclassdesc_consumer.METHODS,$hook_name(ppropertydesc_consumer.NAME)) = eps',
 '$property_hook_trait_function(S,ppropertydesc_consumer) = (pfunction_hook)',
 '$function_at($all_functions(S),porigin_hook) = (pfunction_hook)',
 'pfunction_hook.ORIGIN = porigin_hook /\\ pfunction_hook.NAME = pclassdesc_consumer.NAME ++ $ptascii("::$value::get") /\\ '
 'pfunction_source.NAME = pclassdesc_trait.NAME ++ $ptascii("::$value::get")',
 'pfunction_hook.CODE = pfunction_source.CODE /\\ pfunction_hook.BODY = pfunction_source.BODY /\\ pfunction_hook.CVS = '
 'pfunction_source.CVS /\\ pfunction_hook.ENV = pfunction_source.ENV',
 'pfunction_hook.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_consumer.TYPE, BYREF false} /\\ '
 'pfunction_hook.SIGNATURE = pfunction_source.SIGNATURE /\\ pfunction_hook.DEFAULTS = eps /\\ ~pfunction_hook.EARLY /\\ '
 'pfunction_hook.LINE = 4',
 'porigin_hook_source = PORIGIN n_source pcpath_hook',
 '$origin_node(S.SOURCES,porigin_hook_source) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook '
 'phpType16_hook phpType39_hook metadata_hook)',
 '$hook_body_backed(phpType39_hook,ppropertydesc_source.NAME) /\\ $property_hook_source_declared(S,ppropertydesc_source) '
 '/\\ $property_hook_source_declared(S,ppropertydesc_consumer) /\\ '
 '$property_hook_trait_import_supported(S,pclassdesc_consumer,ppropertydesc_source)',
 '$origin_node(S.SOURCES,PORIGIN n_source (pcpath_hook ++ [PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 5])) = '
 '(NScalarMagicConstMethod metadata_magic)',
 '$method_named(pclassdesc_consumer.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
 '$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
 'pmethoddesc_answer.OWNER = porigin_consumer /\\ pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\\ '
 'pmethoddesc_grand_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.FUNCTION.ORIGIN =/= '
 'pmethoddesc_grand_answer.FUNCTION.ORIGIN',
 'S_global = $global_table_view(S)',
 '$lookup(S_global.ENV,$ptascii("consumer")) = (n_consumer_cell)',
 'S_global.STORE[n_consumer_cell] = DEFINED (POBJECT n_consumer_object)',
 '$lookup(S_global.ENV,$ptascii("grand")) = (n_grand_cell)',
 'S_global.STORE[n_grand_cell] = DEFINED (POBJECT n_grand)',
 'S.OBJECTS[n_consumer_object] = INSTANCE porigin_consumer /\\ S.OBJECTS[n_grand] = INSTANCE porigin_grand',
 '$objectprops_at(S.OBJECTPROPS,n_consumer_object) = ([{DECL (ppropertydesc_consumer.ORIGIN), NAME '
 'ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}]) /\\ $objectprops_at(S.OBJECTPROPS,n_grand) = ([{DECL '
 '(ppropertydesc_consumer.ORIGIN), NAME ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}])',
 '$tih_guard(S)',
 'S_write = S',
 'S_write.TODO = (ASSIGN_ARRAY pbase_write z_write b_write) :: ptask_write*',
 '$lookup(S_write.ENV,$ptascii("grand")) = (n_grand_cell)',
 'S_write.STORE[n_grand_cell] = DEFINED (POBJECT n_grand)',
 'S_write.OBJECTS[n_grand] = INSTANCE porigin_grand /\\ (HOBJECT n_grand) <- S_write.ALLOCATIONS',
 '$objectprops_at(S_write.OBJECTPROPS,n_grand) = ([{ DECL (ppropertydesc_consumer.ORIGIN), NAME ppropertydesc_consumer.KEY, '
 'STATE PROP_VALUE (DIRECT (PINT 100)) }])',
 '$property_pending_base(pbase_write) /\\ S_write.RESULT = KNOWN (PINT 300) /\\ z_write = 30 /\\ '
 '$call_task_valid(S_write,ASSIGN_ARRAY pbase_write z_write b_write) /\\ '
 '$heap_owners($heap_prune($heap_graph(S_write)),HOBJECT n_grand) = 1 /\\ $tih_guard(S_write)',
 'PhpStep: S_write ~> S_write_raw',
 'S_write_raw.COMPLETION = NORMAL /\\ S_write_raw.RESULT = KNOWN (PINT 300) /\\ S_write_raw.EVENTS = S_write.EVENTS /\\ '
 'S_write_raw.TODO = ptask_write*',
 '$objectprops_at(S_write_raw.OBJECTPROPS,n_grand) = ([{ DECL (ppropertydesc_consumer.ORIGIN), NAME '
 'ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 300)) }])',
 'S_written = $tih_after(S_write,S_write_raw)',
 '$tih_guard(S_written)',
 'S_entered_found = $tih_seek(S_written,3,1000)',
 'S_entered_found.COMPLETION = NORMAL \\/ S_entered_found.COMPLETION = BUDGET',
 'S_entered = S_entered_found[.COMPLETION = NORMAL]',
 'S_entered.CURRENT = (pcallcontext_hook)',
 'pcallcontext_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook',
 'S_entered.FRAMES = pframe_hook :: pframe_tail*',
 'S_entered.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin_grand',
 'ppropertyhook.PROPERTY = ppropertydesc_consumer.ORIGIN /\\ ppropertyhook.HOOK = porigin_hook /\\ '
 'pcallcontext_hook.FUNCTION = porigin_hook /\\ pcallcontext_hook.RECEIVER = (ppropertyhook.OBJECT)',
 'pcallcontext_hook.LEXICAL_CLASS = (porigin_consumer) /\\ pcallcontext_hook.CALLED_CLASS = (porigin_grand)',
 '$property_hook_function(S_entered,ppropertyhook) = (pfunction_hook)',
 'pfunction_hook.NAME = pclassdesc_consumer.NAME ++ $ptascii("::$value::get") /\\ pfunction_hook.SIGNATURE = {PARAMETERS '
 'eps, RETURNS ppropertydesc_source.TYPE, BYREF false} /\\ pfunction_hook.LINE = 4',
 '$property_effective_desc(S_entered,ppropertyhook.OBJECT,$ptascii("value")) = (ppropertydesc_consumer)',
 '$objectprops_at(S_entered.OBJECTPROPS,ppropertyhook.OBJECT) = ([{ DECL (ppropertydesc_consumer.ORIGIN), NAME '
 'ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 300)) }])',
 '$property_hook_backing(S_entered,ppropertyhook.OBJECT,ppropertydesc_consumer) /\\ '
 '~$property_hook_backing(S_entered,ppropertyhook.OBJECT,ppropertydesc_source)',
 '$trace_context_class(S_entered,pcallcontext_hook) = (pclassdesc_consumer.NAME) /\\ '
 '$trace_context_function(S_entered,pcallcontext_hook) = $ptascii("$value::get") /\\ '
 '$trace_context_type(S_entered,pcallcontext_hook) = ($ptascii("->"))',
 '$property_hook_frame(S_entered,pcallcontext_hook,pframe_hook,ppropertyhook)',
 '$tih_guard(S_entered)',
 'S_result_found = $tih_seek(S_entered,4,1000)',
 'S_result_found.COMPLETION = NORMAL \\/ S_result_found.COMPLETION = BUDGET',
 'S_result = S_result_found[.COMPLETION = NORMAL]',
 'S_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask_result*',
 'S_result.RESULT = KNOWN (PINT 313) /\\ S_result.CURRENT = eps',
 '$objectprops_at(S_result.OBJECTPROPS,n_grand) = ([{ DECL (ppropertydesc_consumer.ORIGIN), NAME '
 'ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 300)) }])',
 '$tih_guard(S_result)']

DERIVED = ['$property_hook_trait_origin(S,ppropertydesc_source) = eps',
 '$property_hook_trait_origin(S,ppropertydesc_consumer[.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_grand '
 'porigin_property_source]) = eps',
 '$property_hook_trait_origin(S,ppropertydesc_consumer[.NAME = $ptascii("other")]) = eps',
 '$property_hook_trait_origin(S,ppropertydesc_consumer[.KEY = $ptascii("other")]) = eps',
 '$property_hook_trait_origin(S,ppropertydesc_consumer[.TYPE = eps]) = eps',
 '$property_hook_trait_origin(S,ppropertydesc_consumer[.DEFAULT = PROP_LITERAL (PINT 999)]) = eps',
 '$property_hook_trait_origin(S,ppropertydesc_consumer[.VISIBILITY = PROPERTY_PRIVATE]) = eps',
 '$property_hook_trait_origin(S,ppropertydesc_consumer[.STATIC = true]) = eps',
 '$property_hook_trait_origin(S,ppropertydesc_consumer[.READONLY = true]) = eps',
 'S_no_import = S[.CLASSES = $tih_class_replace(S.CLASSES,porigin_consumer,pclassdesc_consumer[.PROPERTIES = eps])]',
 '$property_hook_trait_origin(S_no_import,ppropertydesc_consumer) = eps /\\ '
 '$property_hook_trait_function(S_no_import,ppropertydesc_consumer) = eps',
 'S_no_trait_property = S[.CLASSES = $tih_class_replace(S.CLASSES,porigin_trait,pclassdesc_trait[.PROPERTIES = eps])]',
 '$property_hook_trait_origin(S_no_trait_property,ppropertydesc_consumer) = eps',
 'porigin_consumer = PORIGIN n_consumer_source pcpath_consumer',
 '$origin_node(S.SOURCES,porigin_consumer) = (NStmtClass phpType14_consumer phpType24_consumer phpType3_consumer '
 'phpType44_consumer phpType42_consumer phpType23_consumer metadata_consumer)',
 'S.SOURCES = pcunit :: pcunit_tail*',
 'pcunit.ID = n_source /\\ n_consumer_source = n_source',
 'S_no_use = S[.SOURCES = pcunit[.OCCURRENCES = $tih_replace(pcunit.OCCURRENCES,pcpath_consumer,NStmtClass '
 'phpType14_consumer phpType24_consumer phpType3_consumer phpType44_consumer phpType42_consumer (SEQUENCE eps) '
 'metadata_consumer)] :: pcunit_tail*]',
 '$property_hook_trait_origin(S_no_use,ppropertydesc_consumer) = eps',
 'S_byref = S[.SOURCES = pcunit[.OCCURRENCES = $tih_replace(pcunit.OCCURRENCES,pcpath_hook,NPropertyHook phpType14_hook '
 'phpType24_hook (BOOLEAN true) phpType11_hook phpType16_hook phpType39_hook metadata_hook)] :: pcunit_tail*]',
 '$property_hook_trait_origin(S_byref,ppropertydesc_consumer) = eps /\\ '
 '$property_hook_trait_function(S_byref,ppropertydesc_consumer) = eps',
 'S_no_function = S[.FUNCTIONS = eps]',
 '$property_hook_trait_origin(S_no_function,ppropertydesc_consumer) = (porigin_hook) /\\ '
 '$property_hook_trait_function(S_no_function,ppropertydesc_consumer) = eps /\\ '
 '$function_at($all_functions(S_no_function),porigin_hook) = eps',
 '$property_hook_trait_function(S[.FUNCTIONS = [pfunction_source[.NAME = $ptascii("wrong")]]],ppropertydesc_consumer) = eps',
 '$property_hook_trait_function(S[.FUNCTIONS = [pfunction_source[.SIGNATURE = pfunction_source.SIGNATURE[.RETURNS = '
 'eps]]]],ppropertydesc_consumer) = eps',
 '$property_hook_trait_function(S[.FUNCTIONS = [pfunction_source[.SIGNATURE = pfunction_source.SIGNATURE[.BYREF = '
 'true]]]],ppropertydesc_consumer) = eps',
 '$property_hook_trait_function(S[.FUNCTIONS = [pfunction_source[.EARLY = true]]],ppropertydesc_consumer) = eps',
 '$property_hook_trait_function(S[.FUNCTIONS = [pfunction_source[.BODY = eps]]],ppropertydesc_consumer) = eps',
 '~$property_hook_trait_import_supported(S,pclassdesc_consumer[.PARENT = (pclassdesc_trait.NAME)],ppropertydesc_source)',
 '~$property_hook_trait_import_supported(S,pclassdesc_consumer[.KIND = "trait"],ppropertydesc_source)',
 '~$property_hook_trait_import_supported(S,pclassdesc_consumer[.READONLY = true],ppropertydesc_source)',
 'porigin_property_source = PORIGIN n_source pcpath_property',
 'pcpath_property_group = pcpath_property[0:$nabs($(|pcpath_property| - 2))]',
 '$origin_node(S.SOURCES,PORIGIN n_source pcpath_property_group) = (NStmtProperty phpType14_property phpType24_property '
 'phpType18_property phpType56_property phpType37_property metadata_property)',
 'S_plain = S[.SOURCES = pcunit[.OCCURRENCES = $tih_replace(pcunit.OCCURRENCES,pcpath_property_group,NStmtProperty '
 'phpType14_property phpType24_property phpType18_property phpType56_property (SEQUENCE eps) metadata_property)] :: '
 'pcunit_tail*]',
 '~$property_hook_source_declared(S_plain,ppropertydesc_source) /\\ '
 '$property_hook_trait_import_supported(S_plain,pclassdesc_trait,ppropertydesc_source)']

COLLISION = ['$tih_stage(S,6)',
 'S.ORIGIN = (porigin_consumer)',
 '$class_at(S.CLASSES,porigin_consumer) = (pclassdesc_consumer)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedBackedCollisionTrait63"))) = (porigin_trait)',
 '$class_at(S.CLASSES,porigin_trait) = (pclassdesc_trait)',
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_consumer.NAME)) = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_consumer) = '
 'eps /\\ pclassdesc_consumer.LINE = 10',
 '|pclassdesc_trait.PROPERTIES| = 1 /\\ |pclassdesc_consumer.PROPERTIES| = 1',
 'ppropertydesc_source = pclassdesc_trait.PROPERTIES[0]',
 'ppropertydesc_consumer = pclassdesc_consumer.PROPERTIES[0]',
 'ppropertydesc_consumer.TYPE = ppropertydesc_source.TYPE /\\ ppropertydesc_consumer.NAME = ppropertydesc_source.NAME /\\ '
 'ppropertydesc_consumer.VISIBILITY = ppropertydesc_source.VISIBILITY /\\ $property_default_state(S,ppropertydesc_consumer) '
 '= (PROP_VALUE (DIRECT (PINT 100))) /\\ $property_default_state(S,ppropertydesc_source) = (PROP_VALUE (DIRECT (PINT 100)))',
 '$property_hook_source_declared(S,ppropertydesc_source) /\\ ~$property_hook_source_declared(S,ppropertydesc_consumer)',
 '$property_hook_origin(S,ppropertydesc_source) = (porigin_hook_source) /\\ $property_hook_origin(S,ppropertydesc_consumer) '
 '= eps',
 '$function_at(S.FUNCTIONS,porigin_hook_source) = (pfunction_source)',
 '$property_hook_trait_function(S,ppropertydesc_consumer) = eps /\\ '
 '$method_named(pclassdesc_consumer.METHODS,$hook_name(ppropertydesc_consumer.NAME)) = eps',
 '$trait_plan(S,pclassdesc_consumer).TRAITS = [pclassdesc_trait.NAME]',
 'S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.EVENTS = eps /\\ S.OBJECTS = eps',
 'S.TODO = (STMT statement_consumer) :: ptask_tail*',
 '$tih_guard(S)',
 'PhpStep: S ~> S_raw',
 'ptbytes_message = $ptascii("ImportedBackedCollisionConsumer63 and ImportedBackedCollisionTrait63 define the same hooked '
 'property ($value) in the composition of ImportedBackedCollisionConsumer63. Conflict resolution between hooked properties '
 'is currently not supported. Class was composed")',
 'S_raw.COMPLETION = REQUESTFATAL $ptascii("CompileError") ptbytes_message 10',
 'S_failed = $tih_after(S,S_raw)',
 'S_failed.COMPLETION = S_raw.COMPLETION /\\ S_failed.CLASSNAMES = S.CLASSNAMES /\\ S_failed.CLASSES = S.CLASSES',
 '$class_named(S_failed.CLASSNAMES,$ptlc(pclassdesc_consumer.NAME)) = eps /\\ '
 '$class_link_at(S_failed.LINKEDPARENTS,porigin_consumer) = eps',
 '$property_hook_trait_function(S_failed,ppropertydesc_consumer) = eps',
 '$tih_guard(S_failed)']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--group', choices=['controls', 'entry', 'write', 'collision'], required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'trait_imported_backed_getter_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    clauses, negatives, case_index, start_stage = {
        'controls': (CONTROLS, DERIVED, 0, 0),
        'entry': (ENTRY, [], 0, 0),
        'write': (WRITE, [], 0, 2),
        'collision': (COLLISION, [], 1, 6),
    }[args.group]
    selections = [(args.group, clauses, negatives)]
    cases = [data['cases'][case_index]]
    sources = [HERE / ['trait-imported-backed-getter.php', 'trait-imported-backed-getter-collision.php'][case_index]]
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
    out = Path(tempfile.mkdtemp(prefix='trait-imported-backed-getter-protocol-', dir=ROOT / '.tools'))
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
                     'S_found = $tih_seek(S_initial,' + str(start_stage) + ',1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            content += '\ndec $tih_' + name + '() : bool\ndef $tih_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $tih_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = (' + ' /\\ '.join('$tih_' + name + '()' for name, _, _ in selections) + ')\n'
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
