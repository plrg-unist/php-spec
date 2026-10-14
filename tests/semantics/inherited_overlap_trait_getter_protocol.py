"""Check ordinary inherited overlap, imported getter storage/scope and TYPE rejection."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()

PREFIX = ('dec $iotg_replace(pcoccurrence*,pcpath,pcnode) : pcoccurrence*\n'
 'def $iotg_replace(eps,pcpath,pcnode) = eps\n'
 'def $iotg_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath pcnode) :: '
 'pcoccurrence*\n'
 'def $iotg_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath_other '
 'pcnode_old) :: $iotg_replace(pcoccurrence*,pcpath,pcnode)\n'
 '  -- if pcpath_other =/= pcpath\n'
 'dec $iotg_stage(pstate,nat) : bool\n'
 'def $iotg_stage(S,0) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if $ptlc(pcallcontext.NAME) = $ptascii("inheritedoverlapgetterbase68::parentread")\n'
 '  -- if pcallcontext.RECEIVER = (n_receiver)\n'
 '  -- if $(n_receiver < |S.OBJECTS|)\n'
 '  -- if S.OBJECTS[n_receiver] = INSTANCE porigin\n'
 '  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n'
 '  -- if $ptlc(pclassdesc.NAME) = $ptascii("inheritedoverlapgetterconsumer68")\n'
 'def $iotg_stage(S,1) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n'
 '  -- if S.TODO = (AT porigin_body (EVAL expression_body)) :: (RETURN_VALUE z_return) :: ptask*\n'
 '  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n'
 '  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n'
 '  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n'
 '  -- if $ptlc(pclassdesc.NAME) = $ptascii("inheritedoverlapgetterconsumer68")\n'
 'def $iotg_stage(S,2) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (ASSIGN_ARRAY pbase 36 b) :: ptask*\n'
 '  -- if S.RESULT = KNOWN (PINT 300)\n'
 'def $iotg_stage(S,3) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n'
 '  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n'
 '  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n'
 '  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n'
 '  -- if $ptlc(pclassdesc.NAME) = $ptascii("inheritedoverlapgettergrand68")\n'
 '  -- if $objectprops_at(S.OBJECTPROPS,ppropertyhook.OBJECT) = (ppropertyslot*)\n'
 '  -- if $property_slot_at(ppropertyslot*,$ptascii("value")) = (ppropertyslot_value)\n'
 '  -- if ppropertyslot_value.STATE = PROP_VALUE (DIRECT (PINT 300))\n'
 'def $iotg_stage(S,4) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*\n'
 'def $iotg_stage(S,5) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if $ptlc(pcallcontext.NAME) = $ptascii("inheritedoverlapgetterconsumer68::answer")\n'
 'def $iotg_stage(S,8) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n'
 '  -- if S.TODO = (RETURN_VALUE z_return) :: ptask*\n'
 'def $iotg_stage(S,6) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata)) :: ptask*\n'
 '  -- if S.ORIGIN = (porigin)\n'
 '  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n'
 '  -- if pclassdesc.NAME = $ptascii("InheritedOverlapGetterConsumer68")\n'
 'def $iotg_stage(S,7) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata)) :: ptask*\n'
 '  -- if S.ORIGIN = (porigin)\n'
 '  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n'
 '  -- if pclassdesc.NAME = $ptascii("IncompatibleOverlapGetterConsumer68")\n'
 'def $iotg_stage(S,n) = false -- otherwise\n'
 '\n'
 'dec $iotg_seek(pstate,nat,nat) : pstate\n'
 'def $iotg_seek(S,n_stage,n) = S\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if $iotg_stage(S,n_stage) \\/ n = 0\n'
 'def $iotg_seek(S,n_stage,n) = $iotg_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if ~$iotg_stage(S,n_stage) /\\ $(n > 0)\n'
 'def $iotg_seek(S,n_stage,n) = $iotg_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
 '  -- if $throwable_pending(S.COMPLETION) /\\ $(n > 0)\n'
 'def $iotg_seek(S,n_stage,n) = S -- otherwise\n'
 'dec $iotg_after(pstate,pstate) : pstate\n'
 'def $iotg_after(S,S_next) = '
 '$gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))\n'
 'dec $iotg_guard(pstate) : bool\n'
 'def $iotg_guard(S) = ($call_descriptors_valid(S) /\\ $declaration_history_valid(S) /\\ $property_state_valid(S) /\\ '
 '$heap_valid($heap_prune($heap_graph(S))))\n'
 'dec $iotg_class_replace(pclassdesc*,porigin,pclassdesc) : pclassdesc*\n'
 'def $iotg_class_replace(eps,porigin,pclassdesc) = eps\n'
 'def $iotg_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_new :: pclassdesc*\n'
 '  -- if pclassdesc_old.ORIGIN = porigin\n'
 'def $iotg_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_old :: '
 '$iotg_class_replace(pclassdesc*,porigin,pclassdesc_new)\n'
 '  -- if pclassdesc_old.ORIGIN =/= porigin\n')

COMMON = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("InheritedOverlapGetterTrait68"))) = (porigin_trait)',
 '$class_at(S.CLASSES,porigin_trait) = (pclassdesc_trait)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("InheritedOverlapGetterConsumer68"))) = (porigin_consumer)',
 '$class_at(S.CLASSES,porigin_consumer) = (pclassdesc_consumer)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("InheritedOverlapGetterGrand68"))) = (porigin_grand)',
 '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("InheritedOverlapGetterBase68"))) = (porigin_base)',
 '$class_at(S.CLASSES,porigin_base) = (pclassdesc_base)',
 'pclassdesc_base.KIND = "class" /\\ pclassdesc_base.PARENT = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_base) = eps '
 '/\\ |pclassdesc_base.PROPERTIES| = 2',
 'ppropertydesc_parent = pclassdesc_base.PROPERTIES[0]',
 'ppropertydesc_marker = pclassdesc_base.PROPERTIES[1]',
 'ppropertydesc_parent.NAME = $ptascii("value") /\\ ppropertydesc_parent.KEY = ppropertydesc_parent.NAME /\\ '
 'ppropertydesc_parent.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ $property_default_state(S,ppropertydesc_parent) = '
 '(PROP_VALUE (DIRECT (PINT 10)))',
 'ppropertydesc_parent.VISIBILITY = PROPERTY_PUBLIC /\\ ~ppropertydesc_parent.STATIC /\\ ~ppropertydesc_parent.READONLY /\\ '
 '~ppropertydesc_parent.FINAL /\\ ppropertydesc_parent.SETVISIBILITY = eps /\\ '
 '~$property_hook_source_declared(S,ppropertydesc_parent)',
 'ppropertydesc_marker.NAME = $ptascii("marker") /\\ ppropertydesc_marker.KEY = ppropertydesc_marker.NAME /\\ '
 'ppropertydesc_marker.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ $property_default_state(S,ppropertydesc_marker) = '
 '(PROP_VALUE (DIRECT (PINT 700)))',
 '$property_declaring_class(S.CLASSES,ppropertydesc_parent.ORIGIN) = (porigin_base) /\\ '
 '$property_declaring_class(S.CLASSES,ppropertydesc_marker.ORIGIN) = (porigin_base)',
 '$ppproperty_desc_at($property_info_layout(S,porigin_base,|S.CLASSES|),$ptascii("value")) = (ppropertydesc_parent)',
 'pclassdesc_trait.KIND = "trait" /\\ pclassdesc_consumer.KIND = "class" /\\ pclassdesc_consumer.PARENT = '
 '(pclassdesc_base.NAME) /\\ $class_link_at(S.LINKEDPARENTS,porigin_consumer) = (SOURCE_PARENT porigin_base) /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_consumer)',
 '|pclassdesc_trait.PROPERTIES| = 1 /\\ |pclassdesc_consumer.PROPERTIES| = 1 /\\ pclassdesc_grand.PROPERTIES = eps /\\ '
 'pclassdesc_trait.METHODS = eps',
 'ppropertydesc_source = pclassdesc_trait.PROPERTIES[0]',
 'ppropertydesc_consumer = pclassdesc_consumer.PROPERTIES[0]',
 'ppropertydesc_source.ORIGIN = porigin_property_source',
 'ppropertydesc_consumer.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_consumer porigin_property_source /\\ ppropertydesc_consumer = '
 '$trait_data_property(pclassdesc_consumer,ppropertydesc_source)',
 'ppropertydesc_source.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ ppropertydesc_consumer.TYPE = ppropertydesc_source.TYPE '
 '/\\ $property_default_state(S,ppropertydesc_consumer) = (PROP_VALUE (DIRECT (PINT 100)))',
 '$property_layout(S,porigin_consumer,|S.CLASSES|) = [ppropertydesc_consumer,ppropertydesc_marker] /\\ '
 '$property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_consumer,ppropertydesc_marker]',
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
 '$origin_node(S.SOURCES,PORIGIN n_source (pcpath_hook ++ [PCFIELD 5,PCFIELD 1,PCFIELD 2,PCINDEX 0,PCFIELD 1])) = '
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
 'ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}, {DECL (ppropertydesc_marker.ORIGIN), NAME '
 'ppropertydesc_marker.KEY, STATE PROP_VALUE (DIRECT (PINT 700))}]) /\\ $objectprops_at(S.OBJECTPROPS,n_grand) = ([{DECL '
 '(ppropertydesc_consumer.ORIGIN), NAME ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}, {DECL '
 '(ppropertydesc_marker.ORIGIN), NAME ppropertydesc_marker.KEY, STATE PROP_VALUE (DIRECT (PINT 700))}])',
 '$iotg_guard(S)',
 '$origin_node(S.SOURCES,PORIGIN n_source pfunction_hook.BODY) = (expression_hook)',
 'expression_hook = NExprBinaryOpPlus expression_backing expression_answer metadata_plus',
 '$arrow_line(pfunction_hook.CODE.EXPRESSIONS,pfunction_hook.BODY) = (z_return)',
 'pfunction_hook.BODY = pcpath_hook ++ [PCFIELD 5] /\\ pfunction_hook.CODE.UNIT = n_source /\\ phpType39_hook = '
 'expression_hook',
 '$function_body_tasks(S,pfunction_hook) = [(AT (PORIGIN n_source pfunction_hook.BODY) (EVAL expression_hook)),RETURN_VALUE '
 'z_return]',
 '$method_named(pclassdesc_base.METHODS,$ptascii("parentRead")) = (pmethoddesc_parentread)',
 '$method_named(pclassdesc_base.METHODS,$ptascii("answer")) = (pmethoddesc_base_answer)',
 'pmethoddesc_parentread.OWNER = porigin_base /\\ pmethoddesc_parentread.VISIBILITY = PROPERTY_PUBLIC /\\ '
 'pmethoddesc_base_answer.OWNER = porigin_base /\\ pmethoddesc_base_answer.VISIBILITY = PROPERTY_PRIVATE /\\ '
 'pmethoddesc_base_answer.FUNCTION.ORIGIN =/= pmethoddesc_answer.FUNCTION.ORIGIN',
 '$property_hook_trait_parent_shape(S,pclassdesc_consumer,ppropertydesc_source.NAME) /\\ '
 '$property_hook_trait_parent_linked(S,pclassdesc_consumer)',
 '~$property_hook_parent_match(S,ppropertydesc_consumer,eps)',
 'ppropertydesc_consumer.NAME = ppropertydesc_parent.NAME /\\ ppropertydesc_consumer.KEY = ppropertydesc_parent.KEY /\\ '
 'ppropertydesc_consumer.TYPE = ppropertydesc_parent.TYPE /\\ ppropertydesc_consumer.ORIGIN =/= ppropertydesc_parent.ORIGIN',
 '$property_hook_backed_over_ordinary(S,ppropertydesc_parent,ppropertydesc_consumer) /\\ '
 '$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_consumer) /\\ '
 '~$property_hook_parent_match(S,ppropertydesc_consumer,(ppropertydesc_parent))',
 '$ppproperty_desc_at($property_info_layout(S,porigin_consumer,|S.CLASSES|),ppropertydesc_parent.NAME) = '
 '(ppropertydesc_consumer)']

CONTROLS = ['$iotg_stage(S,6)',
 'S.ORIGIN = (porigin_consumer)',
 '$class_at(S.CLASSES,porigin_consumer) = (pclassdesc_consumer)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("InheritedOverlapGetterTrait68"))) = (porigin_trait)',
 '$class_at(S.CLASSES,porigin_trait) = (pclassdesc_trait)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("InheritedOverlapGetterBase68"))) = (porigin_base)',
 '$class_at(S.CLASSES,porigin_base) = (pclassdesc_base)',
 'pclassdesc_base.KIND = "class" /\\ pclassdesc_base.PARENT = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_base) = eps '
 '/\\ |pclassdesc_base.PROPERTIES| = 2',
 'ppropertydesc_parent = pclassdesc_base.PROPERTIES[0]',
 'ppropertydesc_marker = pclassdesc_base.PROPERTIES[1]',
 'ppropertydesc_parent.NAME = $ptascii("value") /\\ ppropertydesc_parent.KEY = ppropertydesc_parent.NAME /\\ '
 'ppropertydesc_parent.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ $property_default_state(S,ppropertydesc_parent) = '
 '(PROP_VALUE (DIRECT (PINT 10)))',
 'ppropertydesc_parent.VISIBILITY = PROPERTY_PUBLIC /\\ ~ppropertydesc_parent.STATIC /\\ ~ppropertydesc_parent.READONLY /\\ '
 '~ppropertydesc_parent.FINAL /\\ ppropertydesc_parent.SETVISIBILITY = eps /\\ '
 '~$property_hook_source_declared(S,ppropertydesc_parent)',
 'ppropertydesc_marker.NAME = $ptascii("marker") /\\ ppropertydesc_marker.KEY = ppropertydesc_marker.NAME /\\ '
 'ppropertydesc_marker.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ $property_default_state(S,ppropertydesc_marker) = '
 '(PROP_VALUE (DIRECT (PINT 700)))',
 '$property_declaring_class(S.CLASSES,ppropertydesc_parent.ORIGIN) = (porigin_base) /\\ '
 '$property_declaring_class(S.CLASSES,ppropertydesc_marker.ORIGIN) = (porigin_base)',
 '$ppproperty_desc_at($property_info_layout(S,porigin_base,|S.CLASSES|),$ptascii("value")) = (ppropertydesc_parent)',
 'pclassdesc_consumer.KIND = "class" /\\ pclassdesc_consumer.PARENT = (pclassdesc_base.NAME) /\\ '
 'pclassdesc_consumer.PROPERTIES = eps /\\ |pclassdesc_trait.PROPERTIES| = 1',
 'ppropertydesc_source = pclassdesc_trait.PROPERTIES[0]',
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_consumer.NAME)) = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_consumer) = '
 'eps /\\ pclassdesc_consumer.LINE = 16',
 '$trait_plan(S,pclassdesc_consumer).TRAITS = [pclassdesc_trait.NAME]',
 '$property_hook_origin(S,ppropertydesc_source) = (porigin_hook_source)',
 '$function_at(S.FUNCTIONS,porigin_hook_source) = (pfunction_source)',
 '$property_hook_trait_parent_shape(S,pclassdesc_consumer,ppropertydesc_source.NAME) /\\ '
 '~$property_hook_trait_parent_linked(S,pclassdesc_consumer) /\\ '
 '$property_hook_trait_import_supported(S,pclassdesc_consumer,ppropertydesc_source)',
 '$property_hook_trait_origin(S,$trait_data_property(pclassdesc_consumer,ppropertydesc_source)) = eps',
 'S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.OBJECTS = eps /\\ S.EVENTS = eps',
 'S.TODO = (STMT statement_consumer) :: ptask_tail*',
 '$iotg_guard(S)',
 'PhpStep: S ~> S_raw',
 'S_raw.COMPLETION = NORMAL',
 'S_linked = $iotg_after(S,S_raw)',
 'S_linked.COMPLETION = NORMAL /\\ S_linked.FUNCTIONS = S.FUNCTIONS /\\ S_linked.OBJECTS = eps /\\ S_linked.EVENTS = '
 'S.EVENTS',
 '$class_named(S_linked.CLASSNAMES,$ptlc(pclassdesc_consumer.NAME)) = (porigin_consumer)',
 '$class_link_at(S_linked.LINKEDPARENTS,porigin_consumer) = (SOURCE_PARENT porigin_base)',
 '$class_at(S_linked.CLASSES,porigin_consumer) = (pclassdesc_imported)',
 '|pclassdesc_imported.PROPERTIES| = 1',
 'ppropertydesc_consumer = pclassdesc_imported.PROPERTIES[0]',
 'ppropertydesc_consumer = $trait_data_property(pclassdesc_imported,ppropertydesc_source)',
 '$property_hook_trait_parent_shape(S_linked,pclassdesc_imported,ppropertydesc_source.NAME) /\\ '
 '$property_hook_trait_parent_linked(S_linked,pclassdesc_imported)',
 '$property_hook_trait_origin(S_linked,ppropertydesc_consumer) = (porigin_hook)',
 'porigin_hook = TRAIT_ORIGIN porigin_consumer porigin_hook_source ($hook_name(ppropertydesc_source.NAME))',
 '$property_hook_trait_function(S_linked,ppropertydesc_consumer) = (pfunction_hook)',
 '$function_at($all_functions(S_linked),porigin_hook) = (pfunction_hook) /\\ $function_at(S_linked.FUNCTIONS,porigin_hook) '
 '= eps /\\ $method_named(pclassdesc_imported.METHODS,$hook_name(ppropertydesc_source.NAME)) = eps',
 'pfunction_hook.CODE = pfunction_source.CODE /\\ pfunction_hook.BODY = pfunction_source.BODY /\\ pfunction_hook.NAME = '
 'pclassdesc_consumer.NAME ++ $ptascii("::$value::get")',
 '~$property_hook_parent_match(S_linked,ppropertydesc_consumer,eps) /\\ '
 '$property_hook_parent_match(S_linked,ppropertydesc_source,eps)',
 '$iotg_guard(S_linked)',
 'ppropertydesc_parent.TYPE = ppropertydesc_consumer.TYPE /\\ ppropertydesc_parent.KEY = ppropertydesc_consumer.KEY /\\ '
 'ppropertydesc_parent.ORIGIN =/= ppropertydesc_consumer.ORIGIN /\\ '
 '$property_default_state(S_linked,ppropertydesc_consumer) = (PROP_VALUE (DIRECT (PINT 100)))',
 '$property_hook_backed_over_ordinary(S_linked,ppropertydesc_parent,ppropertydesc_consumer) /\\ '
 '$property_hook_override_pair(S_linked,ppropertydesc_parent,ppropertydesc_consumer) /\\ '
 '~$property_hook_parent_match(S_linked,ppropertydesc_consumer,(ppropertydesc_parent))',
 '$class_property_override_issue(S_linked,pclassdesc_imported,$property_info_layout(S_linked,porigin_base,|S_linked.CLASSES|),pclassdesc_imported.PROPERTIES) '
 '= eps',
 '$property_layout(S_linked,porigin_consumer,|S_linked.CLASSES|) = [ppropertydesc_consumer,ppropertydesc_marker]']

ENTRY = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("InheritedOverlapGetterTrait68"))) = (porigin_trait)',
 '$class_at(S.CLASSES,porigin_trait) = (pclassdesc_trait)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("InheritedOverlapGetterConsumer68"))) = (porigin_consumer)',
 '$class_at(S.CLASSES,porigin_consumer) = (pclassdesc_consumer)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("InheritedOverlapGetterGrand68"))) = (porigin_grand)',
 '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("InheritedOverlapGetterBase68"))) = (porigin_base)',
 '$class_at(S.CLASSES,porigin_base) = (pclassdesc_base)',
 'pclassdesc_base.KIND = "class" /\\ pclassdesc_base.PARENT = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_base) = eps '
 '/\\ |pclassdesc_base.PROPERTIES| = 2',
 'ppropertydesc_parent = pclassdesc_base.PROPERTIES[0]',
 'ppropertydesc_marker = pclassdesc_base.PROPERTIES[1]',
 'ppropertydesc_parent.NAME = $ptascii("value") /\\ ppropertydesc_parent.KEY = ppropertydesc_parent.NAME /\\ '
 'ppropertydesc_parent.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ $property_default_state(S,ppropertydesc_parent) = '
 '(PROP_VALUE (DIRECT (PINT 10)))',
 'ppropertydesc_parent.VISIBILITY = PROPERTY_PUBLIC /\\ ~ppropertydesc_parent.STATIC /\\ ~ppropertydesc_parent.READONLY /\\ '
 '~ppropertydesc_parent.FINAL /\\ ppropertydesc_parent.SETVISIBILITY = eps /\\ '
 '~$property_hook_source_declared(S,ppropertydesc_parent)',
 'ppropertydesc_marker.NAME = $ptascii("marker") /\\ ppropertydesc_marker.KEY = ppropertydesc_marker.NAME /\\ '
 'ppropertydesc_marker.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ $property_default_state(S,ppropertydesc_marker) = '
 '(PROP_VALUE (DIRECT (PINT 700)))',
 '$property_declaring_class(S.CLASSES,ppropertydesc_parent.ORIGIN) = (porigin_base) /\\ '
 '$property_declaring_class(S.CLASSES,ppropertydesc_marker.ORIGIN) = (porigin_base)',
 '$ppproperty_desc_at($property_info_layout(S,porigin_base,|S.CLASSES|),$ptascii("value")) = (ppropertydesc_parent)',
 'pclassdesc_trait.KIND = "trait" /\\ pclassdesc_consumer.KIND = "class" /\\ pclassdesc_consumer.PARENT = '
 '(pclassdesc_base.NAME) /\\ $class_link_at(S.LINKEDPARENTS,porigin_consumer) = (SOURCE_PARENT porigin_base) /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_consumer)',
 '|pclassdesc_trait.PROPERTIES| = 1 /\\ |pclassdesc_consumer.PROPERTIES| = 1 /\\ pclassdesc_grand.PROPERTIES = eps /\\ '
 'pclassdesc_trait.METHODS = eps',
 'ppropertydesc_source = pclassdesc_trait.PROPERTIES[0]',
 'ppropertydesc_consumer = pclassdesc_consumer.PROPERTIES[0]',
 'ppropertydesc_source.ORIGIN = porigin_property_source',
 'ppropertydesc_consumer.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_consumer porigin_property_source /\\ ppropertydesc_consumer = '
 '$trait_data_property(pclassdesc_consumer,ppropertydesc_source)',
 'ppropertydesc_source.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ ppropertydesc_consumer.TYPE = ppropertydesc_source.TYPE '
 '/\\ $property_default_state(S,ppropertydesc_consumer) = (PROP_VALUE (DIRECT (PINT 100)))',
 '$property_layout(S,porigin_consumer,|S.CLASSES|) = [ppropertydesc_consumer,ppropertydesc_marker] /\\ '
 '$property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_consumer,ppropertydesc_marker]',
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
 '$origin_node(S.SOURCES,PORIGIN n_source (pcpath_hook ++ [PCFIELD 5,PCFIELD 1,PCFIELD 2,PCINDEX 0,PCFIELD 1])) = '
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
 'ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}, {DECL (ppropertydesc_marker.ORIGIN), NAME '
 'ppropertydesc_marker.KEY, STATE PROP_VALUE (DIRECT (PINT 700))}]) /\\ $objectprops_at(S.OBJECTPROPS,n_grand) = ([{DECL '
 '(ppropertydesc_consumer.ORIGIN), NAME ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}, {DECL '
 '(ppropertydesc_marker.ORIGIN), NAME ppropertydesc_marker.KEY, STATE PROP_VALUE (DIRECT (PINT 700))}])',
 '$iotg_guard(S)',
 '$origin_node(S.SOURCES,PORIGIN n_source pfunction_hook.BODY) = (expression_hook)',
 'expression_hook = NExprBinaryOpPlus expression_backing expression_answer metadata_plus',
 '$arrow_line(pfunction_hook.CODE.EXPRESSIONS,pfunction_hook.BODY) = (z_return)',
 'pfunction_hook.BODY = pcpath_hook ++ [PCFIELD 5] /\\ pfunction_hook.CODE.UNIT = n_source /\\ phpType39_hook = '
 'expression_hook',
 '$function_body_tasks(S,pfunction_hook) = [(AT (PORIGIN n_source pfunction_hook.BODY) (EVAL expression_hook)),RETURN_VALUE '
 'z_return]',
 '$method_named(pclassdesc_base.METHODS,$ptascii("parentRead")) = (pmethoddesc_parentread)',
 '$method_named(pclassdesc_base.METHODS,$ptascii("answer")) = (pmethoddesc_base_answer)',
 'pmethoddesc_parentread.OWNER = porigin_base /\\ pmethoddesc_parentread.VISIBILITY = PROPERTY_PUBLIC /\\ '
 'pmethoddesc_base_answer.OWNER = porigin_base /\\ pmethoddesc_base_answer.VISIBILITY = PROPERTY_PRIVATE /\\ '
 'pmethoddesc_base_answer.FUNCTION.ORIGIN =/= pmethoddesc_answer.FUNCTION.ORIGIN',
 '$property_hook_trait_parent_shape(S,pclassdesc_consumer,ppropertydesc_source.NAME) /\\ '
 '$property_hook_trait_parent_linked(S,pclassdesc_consumer)',
 '~$property_hook_parent_match(S,ppropertydesc_consumer,eps)',
 'ppropertydesc_consumer.NAME = ppropertydesc_parent.NAME /\\ ppropertydesc_consumer.KEY = ppropertydesc_parent.KEY /\\ '
 'ppropertydesc_consumer.TYPE = ppropertydesc_parent.TYPE /\\ ppropertydesc_consumer.ORIGIN =/= ppropertydesc_parent.ORIGIN',
 '$property_hook_backed_over_ordinary(S,ppropertydesc_parent,ppropertydesc_consumer) /\\ '
 '$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_consumer) /\\ '
 '~$property_hook_parent_match(S,ppropertydesc_consumer,(ppropertydesc_parent))',
 '$ppproperty_desc_at($property_info_layout(S,porigin_consumer,|S.CLASSES|),ppropertydesc_parent.NAME) = '
 '(ppropertydesc_consumer)',
 '$iotg_stage(S,0)',
 'S.CURRENT = (pcallcontext_parentread)',
 'pcallcontext_parentread.FUNCTION = pmethoddesc_parentread.FUNCTION.ORIGIN /\\ pcallcontext_parentread.LEXICAL_CLASS = '
 '(porigin_base) /\\ pcallcontext_parentread.CALLED_CLASS = (porigin_consumer) /\\ pcallcontext_parentread.RECEIVER = '
 '(n_consumer_object)',
 '$target_function(S,pcallcontext_parentread.TARGET) = (pmethoddesc_parentread.FUNCTION)',
 '$trace_context_class(S,pcallcontext_parentread) = (pclassdesc_base.NAME) /\\ '
 '$trace_context_function(S,pcallcontext_parentread) = $ptascii("parentRead")',
 'S_hook_found = $iotg_seek(S,1,1000)',
 'S_hook_found.COMPLETION = NORMAL \\/ S_hook_found.COMPLETION = BUDGET',
 'S_hook = S_hook_found[.COMPLETION = NORMAL]',
 '$iotg_stage(S_hook,1)',
 'S_hook.CURRENT = (pcallcontext_hook)',
 'pcallcontext_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook',
 'S_hook.FRAMES = pframe_hook :: pframe_tail*',
 'ppropertyhook.OBJECT = n_consumer_object /\\ ppropertyhook.PROPERTY = ppropertydesc_consumer.ORIGIN /\\ '
 'ppropertyhook.HOOK = porigin_hook /\\ pcallcontext_hook.FUNCTION = porigin_hook /\\ pcallcontext_hook.RECEIVER = '
 '(n_consumer_object)',
 'pcallcontext_hook.LEXICAL_CLASS = (porigin_consumer) /\\ pcallcontext_hook.CALLED_CLASS = (porigin_consumer)',
 'S_hook.TODO = (AT (PORIGIN n_source pfunction_hook.BODY) (EVAL expression_hook)) :: (RETURN_VALUE z_return) :: '
 'ptask_hook*',
 '$property_hook_function(S_hook,ppropertyhook) = (pfunction_hook) /\\ $target_function(S_hook,PROPERTY_HOOK_TARGET '
 'ppropertyhook) = (pfunction_hook)',
 '$property_hook_backing(S_hook,n_consumer_object,ppropertydesc_consumer) /\\ '
 '~$property_hook_read_needed(S_hook,n_consumer_object,ppropertydesc_consumer.NAME)',
 '$target_lexical_class(S_hook,PROPERTY_HOOK_TARGET ppropertyhook) = (porigin_consumer) /\\ '
 '$target_called_class(S_hook,PROPERTY_HOOK_TARGET ppropertyhook) = (porigin_consumer)',
 '$property_hook_frame(S_hook,pcallcontext_hook,pframe_hook,ppropertyhook)',
 'S_answer_found = $iotg_seek(S_hook,5,1000)',
 'S_answer_found.COMPLETION = NORMAL \\/ S_answer_found.COMPLETION = BUDGET',
 'S_answer = S_answer_found[.COMPLETION = NORMAL]',
 'S_answer.CURRENT = (pcallcontext_answer)',
 'pcallcontext_answer.FUNCTION = pmethoddesc_answer.FUNCTION.ORIGIN /\\ pcallcontext_answer.LEXICAL_CLASS = '
 '(porigin_consumer) /\\ pcallcontext_answer.CALLED_CLASS = (porigin_consumer) /\\ pcallcontext_answer.ARGC = 1',
 '$lookup(S_answer.ENV,$ptascii("method")) = (n_method_cell)',
 'S_answer.STORE[n_method_cell] = DEFINED pvalue_method',
 '$string_bytes(pvalue_method) = (pclassdesc_trait.NAME ++ $ptascii("::$value::get"))',
 '$iotg_guard(S_answer)',
 'S_return_found = $iotg_seek(S_answer,8,1000)',
 'S_return_found.COMPLETION = NORMAL \\/ S_return_found.COMPLETION = BUDGET',
 'S_return = S_return_found[.COMPLETION = NORMAL]',
 'S_return.CURRENT = (pcallcontext_return)',
 'pcallcontext_return.TARGET = PROPERTY_HOOK_TARGET ppropertyhook /\\ pcallcontext_return.FUNCTION = porigin_hook /\\ '
 'S_return.ORIGIN = (porigin_hook)',
 'S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*',
 'S_return.RESULT = KNOWN (PINT 113) /\\ $property_hook_expression_context(S_return) /\\ '
 '$typed_return_task_valid(S_return,z_return) /\\ $typed_return_source(S_return,porigin_hook,z_return)',
 '$property_hook_expression_return(S_return,porigin_hook,z_return) = (expression_hook) /\\ '
 '$property_hook_expression_return(S_return,porigin_hook_source,z_return) = (expression_hook)',
 '$iotg_guard(S_return)',
 'PhpStep: S_return ~> S_unwind_raw',
 'S_unwind_raw.TODO = [RETURN_UNWIND (KNOWN (PINT 113)) (porigin_hook)] /\\ S_unwind_raw.RESULT = KNOWN PNULL /\\ '
 'S_unwind_raw.COMPLETION = NORMAL',
 'S_unwind_raw.CURRENT = S_return.CURRENT /\\ S_unwind_raw.OBJECTPROPS = S_return.OBJECTPROPS /\\ S_unwind_raw.EVENTS = '
 'S_return.EVENTS',
 'S_unwind = $iotg_after(S_return,S_unwind_raw)',
 '$iotg_guard(S_unwind)',
 'S_result_found = $iotg_seek(S_unwind,4,1000)',
 'S_result_found.COMPLETION = NORMAL \\/ S_result_found.COMPLETION = BUDGET',
 'S_result = S_result_found[.COMPLETION = NORMAL]',
 'S_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask_result*',
 'S_result.RESULT = KNOWN (PINT 113) /\\ S_result.CURRENT = (pcallcontext_parentread)',
 '$objectprops_at(S_result.OBJECTPROPS,n_consumer_object) = ([{DECL (ppropertydesc_consumer.ORIGIN), NAME '
 'ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}, {DECL (ppropertydesc_marker.ORIGIN), NAME '
 'ppropertydesc_marker.KEY, STATE PROP_VALUE (DIRECT (PINT 700))}])',
 '$iotg_guard(S_result)']

WRITE = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("InheritedOverlapGetterTrait68"))) = (porigin_trait)',
 '$class_at(S.CLASSES,porigin_trait) = (pclassdesc_trait)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("InheritedOverlapGetterConsumer68"))) = (porigin_consumer)',
 '$class_at(S.CLASSES,porigin_consumer) = (pclassdesc_consumer)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("InheritedOverlapGetterGrand68"))) = (porigin_grand)',
 '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("InheritedOverlapGetterBase68"))) = (porigin_base)',
 '$class_at(S.CLASSES,porigin_base) = (pclassdesc_base)',
 'pclassdesc_base.KIND = "class" /\\ pclassdesc_base.PARENT = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_base) = eps '
 '/\\ |pclassdesc_base.PROPERTIES| = 2',
 'ppropertydesc_parent = pclassdesc_base.PROPERTIES[0]',
 'ppropertydesc_marker = pclassdesc_base.PROPERTIES[1]',
 'ppropertydesc_parent.NAME = $ptascii("value") /\\ ppropertydesc_parent.KEY = ppropertydesc_parent.NAME /\\ '
 'ppropertydesc_parent.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ $property_default_state(S,ppropertydesc_parent) = '
 '(PROP_VALUE (DIRECT (PINT 10)))',
 'ppropertydesc_parent.VISIBILITY = PROPERTY_PUBLIC /\\ ~ppropertydesc_parent.STATIC /\\ ~ppropertydesc_parent.READONLY /\\ '
 '~ppropertydesc_parent.FINAL /\\ ppropertydesc_parent.SETVISIBILITY = eps /\\ '
 '~$property_hook_source_declared(S,ppropertydesc_parent)',
 'ppropertydesc_marker.NAME = $ptascii("marker") /\\ ppropertydesc_marker.KEY = ppropertydesc_marker.NAME /\\ '
 'ppropertydesc_marker.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ $property_default_state(S,ppropertydesc_marker) = '
 '(PROP_VALUE (DIRECT (PINT 700)))',
 '$property_declaring_class(S.CLASSES,ppropertydesc_parent.ORIGIN) = (porigin_base) /\\ '
 '$property_declaring_class(S.CLASSES,ppropertydesc_marker.ORIGIN) = (porigin_base)',
 '$ppproperty_desc_at($property_info_layout(S,porigin_base,|S.CLASSES|),$ptascii("value")) = (ppropertydesc_parent)',
 'pclassdesc_trait.KIND = "trait" /\\ pclassdesc_consumer.KIND = "class" /\\ pclassdesc_consumer.PARENT = '
 '(pclassdesc_base.NAME) /\\ $class_link_at(S.LINKEDPARENTS,porigin_consumer) = (SOURCE_PARENT porigin_base) /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_consumer)',
 '|pclassdesc_trait.PROPERTIES| = 1 /\\ |pclassdesc_consumer.PROPERTIES| = 1 /\\ pclassdesc_grand.PROPERTIES = eps /\\ '
 'pclassdesc_trait.METHODS = eps',
 'ppropertydesc_source = pclassdesc_trait.PROPERTIES[0]',
 'ppropertydesc_consumer = pclassdesc_consumer.PROPERTIES[0]',
 'ppropertydesc_source.ORIGIN = porigin_property_source',
 'ppropertydesc_consumer.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_consumer porigin_property_source /\\ ppropertydesc_consumer = '
 '$trait_data_property(pclassdesc_consumer,ppropertydesc_source)',
 'ppropertydesc_source.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ ppropertydesc_consumer.TYPE = ppropertydesc_source.TYPE '
 '/\\ $property_default_state(S,ppropertydesc_consumer) = (PROP_VALUE (DIRECT (PINT 100)))',
 '$property_layout(S,porigin_consumer,|S.CLASSES|) = [ppropertydesc_consumer,ppropertydesc_marker] /\\ '
 '$property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_consumer,ppropertydesc_marker]',
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
 '$origin_node(S.SOURCES,PORIGIN n_source (pcpath_hook ++ [PCFIELD 5,PCFIELD 1,PCFIELD 2,PCINDEX 0,PCFIELD 1])) = '
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
 'ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}, {DECL (ppropertydesc_marker.ORIGIN), NAME '
 'ppropertydesc_marker.KEY, STATE PROP_VALUE (DIRECT (PINT 700))}]) /\\ $objectprops_at(S.OBJECTPROPS,n_grand) = ([{DECL '
 '(ppropertydesc_consumer.ORIGIN), NAME ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}, {DECL '
 '(ppropertydesc_marker.ORIGIN), NAME ppropertydesc_marker.KEY, STATE PROP_VALUE (DIRECT (PINT 700))}])',
 '$iotg_guard(S)',
 '$origin_node(S.SOURCES,PORIGIN n_source pfunction_hook.BODY) = (expression_hook)',
 'expression_hook = NExprBinaryOpPlus expression_backing expression_answer metadata_plus',
 '$arrow_line(pfunction_hook.CODE.EXPRESSIONS,pfunction_hook.BODY) = (z_return)',
 'pfunction_hook.BODY = pcpath_hook ++ [PCFIELD 5] /\\ pfunction_hook.CODE.UNIT = n_source /\\ phpType39_hook = '
 'expression_hook',
 '$function_body_tasks(S,pfunction_hook) = [(AT (PORIGIN n_source pfunction_hook.BODY) (EVAL expression_hook)),RETURN_VALUE '
 'z_return]',
 '$method_named(pclassdesc_base.METHODS,$ptascii("parentRead")) = (pmethoddesc_parentread)',
 '$method_named(pclassdesc_base.METHODS,$ptascii("answer")) = (pmethoddesc_base_answer)',
 'pmethoddesc_parentread.OWNER = porigin_base /\\ pmethoddesc_parentread.VISIBILITY = PROPERTY_PUBLIC /\\ '
 'pmethoddesc_base_answer.OWNER = porigin_base /\\ pmethoddesc_base_answer.VISIBILITY = PROPERTY_PRIVATE /\\ '
 'pmethoddesc_base_answer.FUNCTION.ORIGIN =/= pmethoddesc_answer.FUNCTION.ORIGIN',
 '$property_hook_trait_parent_shape(S,pclassdesc_consumer,ppropertydesc_source.NAME) /\\ '
 '$property_hook_trait_parent_linked(S,pclassdesc_consumer)',
 '~$property_hook_parent_match(S,ppropertydesc_consumer,eps)',
 'ppropertydesc_consumer.NAME = ppropertydesc_parent.NAME /\\ ppropertydesc_consumer.KEY = ppropertydesc_parent.KEY /\\ '
 'ppropertydesc_consumer.TYPE = ppropertydesc_parent.TYPE /\\ ppropertydesc_consumer.ORIGIN =/= ppropertydesc_parent.ORIGIN',
 '$property_hook_backed_over_ordinary(S,ppropertydesc_parent,ppropertydesc_consumer) /\\ '
 '$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_consumer) /\\ '
 '~$property_hook_parent_match(S,ppropertydesc_consumer,(ppropertydesc_parent))',
 '$ppproperty_desc_at($property_info_layout(S,porigin_consumer,|S.CLASSES|),ppropertydesc_parent.NAME) = '
 '(ppropertydesc_consumer)',
 'S_write = S',
 'S_write.TODO = (ASSIGN_ARRAY pbase_write z_write b_write) :: ptask_write*',
 '$lookup(S_write.ENV,$ptascii("grand")) = (n_grand_cell)',
 'S_write.STORE[n_grand_cell] = DEFINED (POBJECT n_grand)',
 'S_write.OBJECTS[n_grand] = INSTANCE porigin_grand /\\ (HOBJECT n_grand) <- S_write.ALLOCATIONS',
 '$objectprops_at(S_write.OBJECTPROPS,n_grand) = ([{DECL (ppropertydesc_consumer.ORIGIN), NAME ppropertydesc_consumer.KEY, '
 'STATE PROP_VALUE (DIRECT (PINT 100))}, {DECL (ppropertydesc_marker.ORIGIN), NAME ppropertydesc_marker.KEY, STATE '
 'PROP_VALUE (DIRECT (PINT 700))}])',
 '$property_pending_base(pbase_write) /\\ S_write.RESULT = KNOWN (PINT 300) /\\ z_write = 36 /\\ '
 '$call_task_valid(S_write,ASSIGN_ARRAY pbase_write z_write b_write) /\\ '
 '$heap_owners($heap_prune($heap_graph(S_write)),HOBJECT n_grand) = 1 /\\ $iotg_guard(S_write)',
 'PhpStep: S_write ~> S_write_raw',
 'S_write_raw.COMPLETION = NORMAL /\\ S_write_raw.RESULT = KNOWN (PINT 300) /\\ S_write_raw.EVENTS = S_write.EVENTS /\\ '
 'S_write_raw.TODO = ptask_write*',
 '$objectprops_at(S_write_raw.OBJECTPROPS,n_grand) = ([{DECL (ppropertydesc_consumer.ORIGIN), NAME '
 'ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 300))}, {DECL (ppropertydesc_marker.ORIGIN), NAME '
 'ppropertydesc_marker.KEY, STATE PROP_VALUE (DIRECT (PINT 700))}])',
 'S_written = $iotg_after(S_write,S_write_raw)',
 '$iotg_guard(S_written)',
 'S_entered_found = $iotg_seek(S_written,3,1000)',
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
 '$objectprops_at(S_entered.OBJECTPROPS,ppropertyhook.OBJECT) = ([{DECL (ppropertydesc_consumer.ORIGIN), NAME '
 'ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 300))}, {DECL (ppropertydesc_marker.ORIGIN), NAME '
 'ppropertydesc_marker.KEY, STATE PROP_VALUE (DIRECT (PINT 700))}])',
 '$property_hook_backing(S_entered,ppropertyhook.OBJECT,ppropertydesc_consumer) /\\ '
 '~$property_hook_backing(S_entered,ppropertyhook.OBJECT,ppropertydesc_source)',
 '$trace_context_class(S_entered,pcallcontext_hook) = (pclassdesc_consumer.NAME) /\\ '
 '$trace_context_function(S_entered,pcallcontext_hook) = $ptascii("$value::get") /\\ '
 '$trace_context_type(S_entered,pcallcontext_hook) = ($ptascii("->"))',
 '$property_hook_frame(S_entered,pcallcontext_hook,pframe_hook,ppropertyhook)',
 '$iotg_guard(S_entered)',
 'S_return_found = $iotg_seek(S_entered,8,1000)',
 'S_return_found.COMPLETION = NORMAL \\/ S_return_found.COMPLETION = BUDGET',
 'S_return = S_return_found[.COMPLETION = NORMAL]',
 'S_return.CURRENT = (pcallcontext_return)',
 'pcallcontext_return.TARGET = PROPERTY_HOOK_TARGET ppropertyhook /\\ pcallcontext_return.FUNCTION = porigin_hook /\\ '
 'S_return.ORIGIN = (porigin_hook)',
 'S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*',
 'S_return.RESULT = KNOWN (PINT 313) /\\ $typed_return_task_valid(S_return,z_return) /\\ '
 '$typed_return_source(S_return,porigin_hook,z_return)',
 '$property_hook_expression_return(S_return,porigin_hook,z_return) = (expression_hook)',
 '$iotg_guard(S_return)',
 'S_result_found = $iotg_seek(S_return,4,1000)',
 'S_result_found.COMPLETION = NORMAL \\/ S_result_found.COMPLETION = BUDGET',
 'S_result = S_result_found[.COMPLETION = NORMAL]',
 'S_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask_result*',
 'S_result.RESULT = KNOWN (PINT 313) /\\ S_result.CURRENT = eps',
 '$objectprops_at(S_result.OBJECTPROPS,n_grand) = ([{DECL (ppropertydesc_consumer.ORIGIN), NAME ppropertydesc_consumer.KEY, '
 'STATE PROP_VALUE (DIRECT (PINT 300))}, {DECL (ppropertydesc_marker.ORIGIN), NAME ppropertydesc_marker.KEY, STATE '
 'PROP_VALUE (DIRECT (PINT 700))}]) /\\ $objectprops_at(S_result.OBJECTPROPS,n_consumer_object) = ([{DECL '
 '(ppropertydesc_consumer.ORIGIN), NAME ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}, {DECL '
 '(ppropertydesc_marker.ORIGIN), NAME ppropertydesc_marker.KEY, STATE PROP_VALUE (DIRECT (PINT 700))}])',
 '$iotg_guard(S_result)']

INVALID = ['$iotg_stage(S,7)',
 'S.ORIGIN = (porigin_consumer)',
 '$class_at(S.CLASSES,porigin_consumer) = (pclassdesc_consumer)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("IncompatibleOverlapGetterTrait68"))) = (porigin_trait)',
 '$class_at(S.CLASSES,porigin_trait) = (pclassdesc_trait)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("IncompatibleOverlapGetterBase68"))) = (porigin_base)',
 '$class_at(S.CLASSES,porigin_base) = (pclassdesc_base)',
 'pclassdesc_consumer.PARENT = (pclassdesc_base.NAME) /\\ pclassdesc_consumer.LINE = 16 /\\ pclassdesc_consumer.PROPERTIES '
 '= eps /\\ |pclassdesc_base.PROPERTIES| = 2 /\\ |pclassdesc_trait.PROPERTIES| = 1',
 'ppropertydesc_parent = pclassdesc_base.PROPERTIES[0]',
 'ppropertydesc_source = pclassdesc_trait.PROPERTIES[0]',
 'ppropertydesc_candidate = $trait_data_property(pclassdesc_consumer,ppropertydesc_source)',
 'ppropertydesc_parent.TYPE = [PTBRANCH ([PTBUILTIN "string"])] /\\ ppropertydesc_candidate.TYPE = [PTBRANCH ([PTBUILTIN '
 '"int"])] /\\ ppropertydesc_parent.NAME = ppropertydesc_candidate.NAME /\\ ppropertydesc_parent.KEY = '
 'ppropertydesc_candidate.KEY',
 '$property_default_state(S,ppropertydesc_parent) = (PROP_VALUE (DIRECT pvalue_parent_default))',
 '$string_bytes(pvalue_parent_default) = ($ptascii("base")) /\\ $property_default_state(S,ppropertydesc_candidate) = '
 '(PROP_VALUE (DIRECT (PINT 100)))',
 '$trait_plan(S,pclassdesc_consumer).TRAITS = [pclassdesc_trait.NAME] /\\ '
 '$property_hook_trait_parent_shape(S,pclassdesc_consumer,ppropertydesc_source.NAME) /\\ '
 '$property_hook_trait_import_supported(S,pclassdesc_consumer,ppropertydesc_source) /\\ '
 '~$property_hook_trait_parent_linked(S,pclassdesc_consumer)',
 '$property_hook_origin(S,ppropertydesc_source) = (porigin_hook_source)',
 'ptbytes_message = $ptascii("Type of IncompatibleOverlapGetterConsumer68::$value must be string (as in class '
 'IncompatibleOverlapGetterBase68)")',
 '$class_property_override_issue(S,pclassdesc_consumer,$property_info_layout(S,porigin_base,|S.CLASSES|),[ppropertydesc_candidate]) '
 '= (ptbytes_message)',
 '$property_hook_covariance_error_site(S,$property_info_layout(S,porigin_base,|S.CLASSES|),ppropertydesc_candidate,ptbytes_message) '
 '= eps',
 '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_consumer.NAME)) = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_consumer) = '
 'eps /\\ S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.OBJECTS = eps /\\ S.EVENTS = eps',
 'S.TODO = (STMT statement_consumer) :: ptask_tail*',
 '$iotg_guard(S)',
 'PhpStep: S ~> S_raw',
 'S_raw.COMPLETION = STATICBYTES ptbytes_message 16',
 'S_failed = $iotg_after(S,S_raw)',
 'S_failed.COMPLETION = S_raw.COMPLETION /\\ S_failed.CLASSNAMES = S.CLASSNAMES /\\ S_failed.CLASSES = S.CLASSES /\\ '
 'S_failed.FUNCTIONS = S.FUNCTIONS',
 '$class_named(S_failed.CLASSNAMES,$ptlc(pclassdesc_consumer.NAME)) = eps /\\ '
 '$class_link_at(S_failed.LINKEDPARENTS,porigin_consumer) = eps /\\ '
 '$class_named(S_failed.CLASSNAMES,$ptlc($ptascii("IncompatibleOverlapGetterGrand68"))) = eps',
 '$property_hook_trait_function(S_failed,ppropertydesc_candidate) = eps',
 '$iotg_guard(S_failed)']

DERIVED = ['$property_hook_trait_parent_shape(S,pclassdesc_consumer[.PARENT = eps],ppropertydesc_source.NAME)',
 '~$property_hook_trait_parent_shape(S,pclassdesc_consumer[.PARENT = (pclassdesc_trait.NAME)],ppropertydesc_source.NAME)',
 '~$property_hook_trait_parent_shape(S,pclassdesc_consumer[.PARENT = '
 '($ptascii("MissingParent68"))],ppropertydesc_source.NAME)',
 'S_wrong_kind = S[.CLASSES = $iotg_class_replace(S.CLASSES,porigin_base,pclassdesc_base[.KIND = "trait"])]',
 '~$property_hook_trait_parent_shape(S_wrong_kind,pclassdesc_consumer,ppropertydesc_source.NAME) /\\ '
 '~$property_hook_trait_import_supported(S_wrong_kind,pclassdesc_consumer,ppropertydesc_source)',
 'ppropertydesc_parent.ORIGIN = PORIGIN n_parent_source pcpath_parent',
 'pcpath_group = pcpath_parent[0:$nabs($(|pcpath_parent| - 2))]',
 '$origin_node(S.SOURCES,PORIGIN n_parent_source pcpath_group) = (NStmtProperty phpType14_parent phpType24_parent '
 'phpType18_parent phpType56_parent phpType37_parent metadata_parent)',
 'S.SOURCES = pcunit :: pcunit_tail*',
 'pcunit.ID = n_parent_source',
 'S_private_source = S[.SOURCES = pcunit[.OCCURRENCES = $iotg_replace(pcunit.OCCURRENCES,pcpath_group,NStmtProperty '
 'phpType14_parent (INTEGER 4) phpType18_parent phpType56_parent phpType37_parent metadata_parent)] :: pcunit_tail*]',
 '~$property_hook_trait_parent_shape(S_private_source,pclassdesc_consumer,ppropertydesc_source.NAME) /\\ '
 '~$property_hook_trait_import_supported(S_private_source,pclassdesc_consumer,ppropertydesc_source)',
 'S_no_own = S[.CLASSES = $iotg_class_replace(S.CLASSES,porigin_base,pclassdesc_base[.PROPERTIES = '
 '[ppropertydesc_marker]])]',
 '$property_hook_trait_parent_shape(S_no_own,pclassdesc_consumer,ppropertydesc_source.NAME)',
 'S_private = S[.CLASSES = $iotg_class_replace(S.CLASSES,porigin_base,pclassdesc_base[.PROPERTIES = '
 '[ppropertydesc_parent[.VISIBILITY = PROPERTY_PRIVATE],ppropertydesc_marker]])]',
 '~$property_hook_trait_parent_shape(S_private,pclassdesc_consumer,ppropertydesc_source.NAME) /\\ '
 '~$property_hook_trait_import_supported(S_private,pclassdesc_consumer,ppropertydesc_source)',
 'S_static = S[.CLASSES = $iotg_class_replace(S.CLASSES,porigin_base,pclassdesc_base[.PROPERTIES = '
 '[ppropertydesc_parent[.STATIC = true],ppropertydesc_marker]])]',
 '~$property_hook_trait_parent_shape(S_static,pclassdesc_consumer,ppropertydesc_source.NAME) /\\ '
 '~$property_hook_trait_import_supported(S_static,pclassdesc_consumer,ppropertydesc_source)',
 'S_readonly = S[.CLASSES = $iotg_class_replace(S.CLASSES,porigin_base,pclassdesc_base[.PROPERTIES = '
 '[ppropertydesc_parent[.READONLY = true],ppropertydesc_marker]])]',
 '~$property_hook_trait_parent_shape(S_readonly,pclassdesc_consumer,ppropertydesc_source.NAME) /\\ '
 '~$property_hook_trait_import_supported(S_readonly,pclassdesc_consumer,ppropertydesc_source)',
 'S_final = S[.CLASSES = $iotg_class_replace(S.CLASSES,porigin_base,pclassdesc_base[.PROPERTIES = '
 '[ppropertydesc_parent[.FINAL = true],ppropertydesc_marker]])]',
 '~$property_hook_trait_parent_shape(S_final,pclassdesc_consumer,ppropertydesc_source.NAME) /\\ '
 '~$property_hook_trait_import_supported(S_final,pclassdesc_consumer,ppropertydesc_source)',
 'S_setter = S[.CLASSES = $iotg_class_replace(S.CLASSES,porigin_base,pclassdesc_base[.PROPERTIES = '
 '[ppropertydesc_parent[.SETVISIBILITY = (SETVISPROTECTED)],ppropertydesc_marker]])]',
 '~$property_hook_trait_parent_shape(S_setter,pclassdesc_consumer,ppropertydesc_source.NAME) /\\ '
 '~$property_hook_trait_import_supported(S_setter,pclassdesc_consumer,ppropertydesc_source)',
 'S_untyped = S[.CLASSES = $iotg_class_replace(S.CLASSES,porigin_base,pclassdesc_base[.PROPERTIES = '
 '[ppropertydesc_parent[.TYPE = eps],ppropertydesc_marker]])]',
 '~$property_hook_trait_parent_shape(S_untyped,pclassdesc_consumer,ppropertydesc_source.NAME) /\\ '
 '~$property_hook_trait_import_supported(S_untyped,pclassdesc_consumer,ppropertydesc_source)',
 'S_key = S[.CLASSES = $iotg_class_replace(S.CLASSES,porigin_base,pclassdesc_base[.PROPERTIES = [ppropertydesc_parent[.KEY '
 '= $ptascii("wrong-key")],ppropertydesc_marker]])]',
 '~$property_hook_trait_parent_shape(S_key,pclassdesc_consumer,ppropertydesc_source.NAME) /\\ '
 '~$property_hook_trait_import_supported(S_key,pclassdesc_consumer,ppropertydesc_source)',
 'S_no_link = S_linked[.LINKEDPARENTS = eps]',
 '$property_hook_trait_parent_shape(S_no_link,pclassdesc_imported,ppropertydesc_source.NAME) /\\ '
 '~$property_hook_trait_parent_linked(S_no_link,pclassdesc_imported) /\\ '
 '$property_hook_trait_origin(S_no_link,ppropertydesc_consumer) = eps']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--group', choices=['controls', 'entry', 'write', 'invalid'], required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'inherited_overlap_trait_getter_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    clauses, negatives, case_index, start_stage = {
        'controls': (CONTROLS, DERIVED, 0, 6),
        'entry': (ENTRY, [], 0, 0),
        'write': (WRITE, [], 0, 2),
        'invalid': (INVALID, [], 1, 7),
    }[args.group]
    selections = [(args.group, clauses, negatives)]
    cases = [data['cases'][case_index]]
    sources = [HERE / ('inherited-overlap-trait-getter.php' if case_index == 0 else 'incompatible-overlap-trait-getter.php')]
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
    out = Path(tempfile.mkdtemp(prefix='inherited-overlap-trait-getter-protocol-', dir=ROOT / '.tools'))
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
                     'S_found = $iotg_seek(S_initial,' + str(start_stage) + ',1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            content += '\ndec $iotg_' + name + '() : bool\ndef $iotg_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $iotg_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = (' + ' /\\ '.join('$iotg_' + name + '()' for name, _, _ in selections) + ')\n'
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
