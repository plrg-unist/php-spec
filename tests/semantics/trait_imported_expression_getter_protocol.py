"""Check imported backed expression getter scope, implicit returns and writes."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()

PREFIX = ('dec $tie_replace(pcoccurrence*,pcpath,pcnode) : pcoccurrence*\n'
 'def $tie_replace(eps,pcpath,pcnode) = eps\n'
 'def $tie_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath pcnode) :: '
 'pcoccurrence*\n'
 'def $tie_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath_other '
 'pcnode_old) :: $tie_replace(pcoccurrence*,pcpath,pcnode)\n'
 '  -- if pcpath_other =/= pcpath\n'
 'dec $tie_stage(pstate,nat) : bool\n'
 'def $tie_stage(S,0) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n'
 '  -- if S.TODO = (AT porigin_body (EVAL expression_body)) :: (RETURN_VALUE z_return) :: ptask*\n'
 '  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n'
 '  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n'
 '  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n'
 '  -- if $ptlc(pclassdesc.NAME) = $ptascii("importedexpressiongetterconsumer65")\n'
 'def $tie_stage(S,2) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (ASSIGN_ARRAY pbase 25 b) :: ptask*\n'
 '  -- if S.RESULT = KNOWN (PINT 300)\n'
 'def $tie_stage(S,3) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n'
 '  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n'
 '  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n'
 '  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n'
 '  -- if $ptlc(pclassdesc.NAME) = $ptascii("importedexpressiongettergrand65")\n'
 '  -- if $objectprops_at(S.OBJECTPROPS,ppropertyhook.OBJECT) = (ppropertyslot*)\n'
 '  -- if $property_slot_at(ppropertyslot*,$ptascii("value")) = (ppropertyslot_value)\n'
 '  -- if ppropertyslot_value.STATE = PROP_VALUE (DIRECT (PINT 300))\n'
 'def $tie_stage(S,4) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*\n'
 'def $tie_stage(S,5) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if $ptlc(pcallcontext.NAME) = $ptascii("importedexpressiongetterconsumer65::answer")\n'
 'def $tie_stage(S,8) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n'
 '  -- if S.TODO = (RETURN_VALUE z_return) :: ptask*\n'
 'def $tie_stage(S,n) = false -- otherwise\n'
 '\n'
 'dec $tie_seek(pstate,nat,nat) : pstate\n'
 'def $tie_seek(S,n_stage,n) = S\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if $tie_stage(S,n_stage) \\/ n = 0\n'
 'def $tie_seek(S,n_stage,n) = $tie_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if ~$tie_stage(S,n_stage) /\\ $(n > 0)\n'
 'def $tie_seek(S,n_stage,n) = $tie_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
 '  -- if $throwable_pending(S.COMPLETION) /\\ $(n > 0)\n'
 'def $tie_seek(S,n_stage,n) = S -- otherwise\n'
 'dec $tie_after(pstate,pstate) : pstate\n'
 'def $tie_after(S,S_next) = '
 '$gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))\n'
 'dec $tie_guard(pstate) : bool\n'
 'def $tie_guard(S) = ($call_descriptors_valid(S) /\\ $declaration_history_valid(S) /\\ $property_state_valid(S) /\\ '
 '$heap_valid($heap_prune($heap_graph(S))))\n'
 'dec $tie_class_replace(pclassdesc*,porigin,pclassdesc) : pclassdesc*\n'
 'def $tie_class_replace(eps,porigin,pclassdesc) = eps\n'
 'def $tie_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_new :: pclassdesc*\n'
 '  -- if pclassdesc_old.ORIGIN = porigin\n'
 'def $tie_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_old :: '
 '$tie_class_replace(pclassdesc*,porigin,pclassdesc_new)\n'
 '  -- if pclassdesc_old.ORIGIN =/= porigin\n')

COMMON = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedExpressionGetterTrait65"))) = (porigin_trait)',
 '$class_at(S.CLASSES,porigin_trait) = (pclassdesc_trait)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedExpressionGetterConsumer65"))) = (porigin_consumer)',
 '$class_at(S.CLASSES,porigin_consumer) = (pclassdesc_consumer)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedExpressionGetterGrand65"))) = (porigin_grand)',
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
 'ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}]) /\\ $objectprops_at(S.OBJECTPROPS,n_grand) = ([{DECL '
 '(ppropertydesc_consumer.ORIGIN), NAME ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}])',
 '$tie_guard(S)',
 '$origin_node(S.SOURCES,PORIGIN n_source pfunction_hook.BODY) = (expression_hook)',
 'expression_hook = NExprBinaryOpPlus expression_backing expression_answer metadata_plus',
 '$arrow_line(pfunction_hook.CODE.EXPRESSIONS,pfunction_hook.BODY) = (z_return)',
 'pfunction_hook.BODY = pcpath_hook ++ [PCFIELD 5] /\\ pfunction_hook.CODE.UNIT = n_source /\\ phpType39_hook = '
 'expression_hook',
 '$function_body_tasks(S,pfunction_hook) = [(AT (PORIGIN n_source pfunction_hook.BODY) (EVAL expression_hook)),RETURN_VALUE '
 'z_return]']

CONTROLS = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedExpressionGetterTrait65"))) = (porigin_trait)',
 '$class_at(S.CLASSES,porigin_trait) = (pclassdesc_trait)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedExpressionGetterConsumer65"))) = (porigin_consumer)',
 '$class_at(S.CLASSES,porigin_consumer) = (pclassdesc_consumer)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedExpressionGetterGrand65"))) = (porigin_grand)',
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
 'ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}]) /\\ $objectprops_at(S.OBJECTPROPS,n_grand) = ([{DECL '
 '(ppropertydesc_consumer.ORIGIN), NAME ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}])',
 '$tie_guard(S)',
 '$origin_node(S.SOURCES,PORIGIN n_source pfunction_hook.BODY) = (expression_hook)',
 'expression_hook = NExprBinaryOpPlus expression_backing expression_answer metadata_plus',
 '$arrow_line(pfunction_hook.CODE.EXPRESSIONS,pfunction_hook.BODY) = (z_return)',
 'pfunction_hook.BODY = pcpath_hook ++ [PCFIELD 5] /\\ pfunction_hook.CODE.UNIT = n_source /\\ phpType39_hook = '
 'expression_hook',
 '$function_body_tasks(S,pfunction_hook) = [(AT (PORIGIN n_source pfunction_hook.BODY) (EVAL expression_hook)),RETURN_VALUE '
 'z_return]',
 '$tie_stage(S,0)']

ENTRY = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedExpressionGetterTrait65"))) = (porigin_trait)',
 '$class_at(S.CLASSES,porigin_trait) = (pclassdesc_trait)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedExpressionGetterConsumer65"))) = (porigin_consumer)',
 '$class_at(S.CLASSES,porigin_consumer) = (pclassdesc_consumer)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedExpressionGetterGrand65"))) = (porigin_grand)',
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
 'ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}]) /\\ $objectprops_at(S.OBJECTPROPS,n_grand) = ([{DECL '
 '(ppropertydesc_consumer.ORIGIN), NAME ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}])',
 '$tie_guard(S)',
 '$origin_node(S.SOURCES,PORIGIN n_source pfunction_hook.BODY) = (expression_hook)',
 'expression_hook = NExprBinaryOpPlus expression_backing expression_answer metadata_plus',
 '$arrow_line(pfunction_hook.CODE.EXPRESSIONS,pfunction_hook.BODY) = (z_return)',
 'pfunction_hook.BODY = pcpath_hook ++ [PCFIELD 5] /\\ pfunction_hook.CODE.UNIT = n_source /\\ phpType39_hook = '
 'expression_hook',
 '$function_body_tasks(S,pfunction_hook) = [(AT (PORIGIN n_source pfunction_hook.BODY) (EVAL expression_hook)),RETURN_VALUE '
 'z_return]',
 '$tie_stage(S,0)',
 'S.CURRENT = (pcallcontext_hook)',
 'pcallcontext_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook',
 'S.FRAMES = pframe_hook :: pframe_tail*',
 'ppropertyhook.OBJECT = n_consumer_object /\\ ppropertyhook.PROPERTY = ppropertydesc_consumer.ORIGIN /\\ '
 'ppropertyhook.HOOK = porigin_hook /\\ pcallcontext_hook.FUNCTION = porigin_hook /\\ pcallcontext_hook.RECEIVER = '
 '(n_consumer_object)',
 'pcallcontext_hook.LEXICAL_CLASS = (porigin_consumer) /\\ pcallcontext_hook.CALLED_CLASS = (porigin_consumer)',
 'S.TODO = (AT (PORIGIN n_source pfunction_hook.BODY) (EVAL expression_hook)) :: (RETURN_VALUE z_return) :: ptask_hook*',
 '$property_hook_function(S,ppropertyhook) = (pfunction_hook) /\\ $target_function(S,PROPERTY_HOOK_TARGET ppropertyhook) = '
 '(pfunction_hook)',
 '$property_hook_backing(S,n_consumer_object,ppropertydesc_consumer) /\\ '
 '~$property_hook_read_needed(S,n_consumer_object,ppropertydesc_consumer.NAME)',
 '$target_lexical_class(S,PROPERTY_HOOK_TARGET ppropertyhook) = (porigin_consumer) /\\ '
 '$target_called_class(S,PROPERTY_HOOK_TARGET ppropertyhook) = (porigin_consumer)',
 '$property_hook_frame(S,pcallcontext_hook,pframe_hook,ppropertyhook)',
 'S_answer_found = $tie_seek(S,5,1000)',
 'S_answer_found.COMPLETION = NORMAL \\/ S_answer_found.COMPLETION = BUDGET',
 'S_answer = S_answer_found[.COMPLETION = NORMAL]',
 'S_answer.CURRENT = (pcallcontext_answer)',
 'pcallcontext_answer.FUNCTION = pmethoddesc_answer.FUNCTION.ORIGIN /\\ pcallcontext_answer.LEXICAL_CLASS = '
 '(porigin_consumer) /\\ pcallcontext_answer.CALLED_CLASS = (porigin_consumer) /\\ pcallcontext_answer.ARGC = 1',
 '$lookup(S_answer.ENV,$ptascii("method")) = (n_method_cell)',
 'S_answer.STORE[n_method_cell] = DEFINED pvalue_method',
 '$string_bytes(pvalue_method) = (pclassdesc_trait.NAME ++ $ptascii("::$value::get"))',
 '$tie_guard(S_answer)',
 'S_return_found = $tie_seek(S_answer,8,1000)',
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
 '$tie_guard(S_return)',
 'PhpStep: S_return ~> S_unwind_raw',
 'S_unwind_raw.TODO = [RETURN_UNWIND (KNOWN (PINT 113)) (porigin_hook)] /\\ S_unwind_raw.RESULT = KNOWN PNULL /\\ '
 'S_unwind_raw.COMPLETION = NORMAL',
 'S_unwind_raw.CURRENT = S_return.CURRENT /\\ S_unwind_raw.OBJECTPROPS = S_return.OBJECTPROPS /\\ S_unwind_raw.EVENTS = '
 'S_return.EVENTS',
 'S_unwind = $tie_after(S_return,S_unwind_raw)',
 '$tie_guard(S_unwind)',
 'S_result_found = $tie_seek(S_unwind,4,1000)',
 'S_result_found.COMPLETION = NORMAL \\/ S_result_found.COMPLETION = BUDGET',
 'S_result = S_result_found[.COMPLETION = NORMAL]',
 'S_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask_result*',
 'S_result.RESULT = KNOWN (PINT 113) /\\ S_result.CURRENT = eps',
 '$objectprops_at(S_result.OBJECTPROPS,n_consumer_object) = ([{DECL (ppropertydesc_consumer.ORIGIN), NAME '
 'ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}])',
 '$tie_guard(S_result)']

WRITE = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedExpressionGetterTrait65"))) = (porigin_trait)',
 '$class_at(S.CLASSES,porigin_trait) = (pclassdesc_trait)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedExpressionGetterConsumer65"))) = (porigin_consumer)',
 '$class_at(S.CLASSES,porigin_consumer) = (pclassdesc_consumer)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedExpressionGetterGrand65"))) = (porigin_grand)',
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
 'ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}]) /\\ $objectprops_at(S.OBJECTPROPS,n_grand) = ([{DECL '
 '(ppropertydesc_consumer.ORIGIN), NAME ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 100))}])',
 '$tie_guard(S)',
 '$origin_node(S.SOURCES,PORIGIN n_source pfunction_hook.BODY) = (expression_hook)',
 'expression_hook = NExprBinaryOpPlus expression_backing expression_answer metadata_plus',
 '$arrow_line(pfunction_hook.CODE.EXPRESSIONS,pfunction_hook.BODY) = (z_return)',
 'pfunction_hook.BODY = pcpath_hook ++ [PCFIELD 5] /\\ pfunction_hook.CODE.UNIT = n_source /\\ phpType39_hook = '
 'expression_hook',
 '$function_body_tasks(S,pfunction_hook) = [(AT (PORIGIN n_source pfunction_hook.BODY) (EVAL expression_hook)),RETURN_VALUE '
 'z_return]',
 'S_write = S',
 'S_write.TODO = (ASSIGN_ARRAY pbase_write z_write b_write) :: ptask_write*',
 '$lookup(S_write.ENV,$ptascii("grand")) = (n_grand_cell)',
 'S_write.STORE[n_grand_cell] = DEFINED (POBJECT n_grand)',
 'S_write.OBJECTS[n_grand] = INSTANCE porigin_grand /\\ (HOBJECT n_grand) <- S_write.ALLOCATIONS',
 '$objectprops_at(S_write.OBJECTPROPS,n_grand) = ([{ DECL (ppropertydesc_consumer.ORIGIN), NAME ppropertydesc_consumer.KEY, '
 'STATE PROP_VALUE (DIRECT (PINT 100)) }])',
 '$property_pending_base(pbase_write) /\\ S_write.RESULT = KNOWN (PINT 300) /\\ z_write = 25 /\\ '
 '$call_task_valid(S_write,ASSIGN_ARRAY pbase_write z_write b_write) /\\ '
 '$heap_owners($heap_prune($heap_graph(S_write)),HOBJECT n_grand) = 1 /\\ $tie_guard(S_write)',
 'PhpStep: S_write ~> S_write_raw',
 'S_write_raw.COMPLETION = NORMAL /\\ S_write_raw.RESULT = KNOWN (PINT 300) /\\ S_write_raw.EVENTS = S_write.EVENTS /\\ '
 'S_write_raw.TODO = ptask_write*',
 '$objectprops_at(S_write_raw.OBJECTPROPS,n_grand) = ([{ DECL (ppropertydesc_consumer.ORIGIN), NAME '
 'ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 300)) }])',
 'S_written = $tie_after(S_write,S_write_raw)',
 '$tie_guard(S_written)',
 'S_entered_found = $tie_seek(S_written,3,1000)',
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
 '$tie_guard(S_entered)',
 'S_return_found = $tie_seek(S_entered,8,1000)',
 'S_return_found.COMPLETION = NORMAL \\/ S_return_found.COMPLETION = BUDGET',
 'S_return = S_return_found[.COMPLETION = NORMAL]',
 'S_return.CURRENT = (pcallcontext_return)',
 'pcallcontext_return.TARGET = PROPERTY_HOOK_TARGET ppropertyhook /\\ pcallcontext_return.FUNCTION = porigin_hook /\\ '
 'S_return.ORIGIN = (porigin_hook)',
 'S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*',
 'S_return.RESULT = KNOWN (PINT 313) /\\ $typed_return_task_valid(S_return,z_return) /\\ '
 '$typed_return_source(S_return,porigin_hook,z_return)',
 '$property_hook_expression_return(S_return,porigin_hook,z_return) = (expression_hook)',
 '$tie_guard(S_return)',
 'S_result_found = $tie_seek(S_return,4,1000)',
 'S_result_found.COMPLETION = NORMAL \\/ S_result_found.COMPLETION = BUDGET',
 'S_result = S_result_found[.COMPLETION = NORMAL]',
 'S_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask_result*',
 'S_result.RESULT = KNOWN (PINT 313) /\\ S_result.CURRENT = eps',
 '$objectprops_at(S_result.OBJECTPROPS,n_grand) = ([{ DECL (ppropertydesc_consumer.ORIGIN), NAME '
 'ppropertydesc_consumer.KEY, STATE PROP_VALUE (DIRECT (PINT 300)) }])',
 '$tie_guard(S_result)']

DERIVED = ['$hook_body_backed(expression_hook,ppropertydesc_source.NAME) /\\ '
 '~$hook_body_backed(expression_answer,ppropertydesc_source.NAME)',
 'porigin_property_source = PORIGIN n_source pcpath_property',
 'pcpath_property_group = pcpath_property[0:$nabs($(|pcpath_property| - 2))]',
 '$origin_node(S.SOURCES,PORIGIN n_source pcpath_property_group) = (NStmtProperty phpType14_property phpType24_property '
 'phpType18_property phpType56_property phpType37_property metadata_property)',
 'phpType56_property = SEQUENCE ([NPropertyItem phpType40_property phpType5_property metadata_item])',
 '$origin_node(S.SOURCES,porigin_trait) = (NStmtTrait phpType14_trait phpType3_trait phpType23_trait metadata_trait)',
 'pchheader_trait = {KIND pclassdesc_trait.KIND, NAME pclassdesc_trait.NAME, ABSTRACT pclassdesc_trait.ABSTRACT, FINAL '
 'pclassdesc_trait.FINAL, READONLY pclassdesc_trait.READONLY, PARENT pclassdesc_trait.PARENT, INTERFACES '
 'pclassdesc_trait.INTERFACES, BODY phpType23_trait}',
 '$pphook_owner_shape(pchheader_trait,phpType40_property,NPropertyHook phpType14_hook phpType24_hook phpType4_hook '
 'phpType11_hook phpType16_hook expression_hook metadata_hook,phpType5_property)',
 '$pphook_owner_shape(pchheader_trait,phpType40_property,NPropertyHook phpType14_hook phpType24_hook phpType4_hook '
 'phpType11_hook phpType16_hook expression_answer metadata_hook,ABSENT)',
 'S.SOURCES = pcunit :: pcunit_tail*',
 'pcunit.ID = n_source',
 'S_virtual_source = S[.SOURCES = pcunit[.OCCURRENCES = '
 '$tie_replace($tie_replace($tie_replace($tie_replace(pcunit.OCCURRENCES,pcpath_property_group,NStmtProperty '
 'phpType14_property phpType24_property phpType18_property (SEQUENCE ([NPropertyItem phpType40_property ABSENT '
 'metadata_item])) (SEQUENCE ([NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook phpType16_hook '
 'expression_answer metadata_hook])) metadata_property),pcpath_property,NPropertyItem phpType40_property ABSENT '
 'metadata_item),pcpath_hook,NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook phpType16_hook '
 'expression_answer metadata_hook),pfunction_source.BODY,expression_answer)] :: pcunit_tail*]',
 'S_virtual = S_virtual_source[.CLASSES = '
 '$tie_class_replace($tie_class_replace(S.CLASSES,porigin_trait,pclassdesc_trait[.PROPERTIES = '
 '[ppropertydesc_source[.DEFAULT = PROP_UNINITIALIZED]]]),porigin_consumer,pclassdesc_consumer[.PROPERTIES = '
 '[ppropertydesc_consumer[.DEFAULT = PROP_UNINITIALIZED]]])]',
 '$property_hook_origin(S_virtual,ppropertydesc_source[.DEFAULT = PROP_UNINITIALIZED]) = (porigin_hook_source) /\\ '
 '$property_hook_virtual(S_virtual,ppropertydesc_source[.DEFAULT = PROP_UNINITIALIZED])',
 '$property_hook_trait_import_supported(S_virtual,pclassdesc_consumer,ppropertydesc_source[.DEFAULT = PROP_UNINITIALIZED]) '
 '/\\ $property_hook_trait_origin(S_virtual,ppropertydesc_consumer[.DEFAULT = PROP_UNINITIALIZED]) = (porigin_hook)',
 '$property_hook_expression_return(S,porigin_hook,z_return) = (expression_hook)',
 '$property_hook_expression_return(S,TRAIT_ORIGIN porigin_grand porigin_hook_source '
 '($hook_name(ppropertydesc_consumer.NAME)),z_return) = eps',
 '$property_hook_expression_return(S,TRAIT_ORIGIN porigin_consumer porigin_hook_source ($ptascii("wrong")),z_return) = eps',
 '$property_hook_expression_return(S,porigin_hook,999) = eps',
 'S_no_import = S[.CLASSES = $tie_class_replace(S.CLASSES,porigin_consumer,pclassdesc_consumer[.PROPERTIES = eps])]',
 '$property_hook_expression_return(S_no_import,porigin_hook,z_return) = eps /\\ '
 '$property_hook_expression_return(S_no_import,porigin_hook_source,z_return) = (expression_hook)',
 '$property_hook_expression_return(S[.FUNCTIONS = eps],porigin_hook,z_return) = eps /\\ '
 '$property_hook_trait_origin(S[.FUNCTIONS = eps],ppropertydesc_consumer) = (porigin_hook)',
 '$property_hook_expression_return(S[.FUNCTIONS = [pfunction_source[.CODE.EXPRESSIONS = eps]]],porigin_hook,z_return) = eps']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--group', choices=['controls', 'entry', 'write'], required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'trait_imported_expression_getter_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    clauses, negatives, case_index, start_stage = {
        'controls': (CONTROLS, DERIVED, 0, 0),
        'entry': (ENTRY, [], 0, 0),
        'write': (WRITE, [], 0, 2),
    }[args.group]
    selections = [(args.group, clauses, negatives)]
    cases = [data['cases'][case_index]]
    sources = [HERE / 'trait-imported-expression-getter.php']
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
    out = Path(tempfile.mkdtemp(prefix='trait-imported-expression-getter-protocol-', dir=ROOT / '.tools'))
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
                     'S_found = $tie_seek(S_initial,' + str(start_stage) + ',1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            content += '\ndec $tie_' + name + '() : bool\ndef $tie_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $tie_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = (' + ' /\\ '.join('$tie_' + name + '()' for name, _, _ in selections) + ')\n'
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
