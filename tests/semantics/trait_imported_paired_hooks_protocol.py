"""Check atomic imported GET/SET clones, crossed backing access and assignment results."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()

PREFIX = ('dec $tpp_replace(pcoccurrence*,pcpath,pcnode) : pcoccurrence*\n'
 'def $tpp_replace(eps,pcpath,pcnode) = eps\n'
 'def $tpp_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath '
 'pcnode) :: pcoccurrence*\n'
 'def $tpp_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE '
 'pcpath_other pcnode_old) :: $tpp_replace(pcoccurrence*,pcpath,pcnode)\n'
 '  -- if pcpath_other =/= pcpath\n'
 'dec $tpp_class_replace(pclassdesc*,porigin,pclassdesc) : pclassdesc*\n'
 'def $tpp_class_replace(eps,porigin,pclassdesc) = eps\n'
 'def $tpp_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_new :: pclassdesc*\n'
 '  -- if pclassdesc_old.ORIGIN = porigin\n'
 'def $tpp_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_old :: '
 '$tpp_class_replace(pclassdesc*,porigin,pclassdesc_new)\n'
 '  -- if pclassdesc_old.ORIGIN =/= porigin\n'
 'dec $tpp_stage(pstate,nat) : bool\n'
 'def $tpp_stage(S,0) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (PROPERTY_PREP phpType20 24) :: (DIM_FETCH 24) :: ptask*\n'
 'def $tpp_stage(S,1) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_SET_TARGET ppropertyhook\n'
 '  -- if S.TODO = (PROPERTY_PREP phpType20 10) :: (DIM_FETCH 10) :: ptask*\n'
 'def $tpp_stage(S,2) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_SET_TARGET ppropertyhook\n'
 '  -- if S.TODO = (ASSIGN_ARRAY pbase 11 false) :: ptask*\n'
 '  -- if S.RESULT = KNOWN (PINT 33)\n'
 'def $tpp_stage(S,3) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (PROPERTY_SET_RESULT ppropertyhook (PINT 20)) :: ptask*\n'
 'def $tpp_stage(S,4) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*\n'
 '  -- if S.RESULT = KNOWN (PINT 23)\n'
 'def $tpp_stage(S,5) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*\n'
 '  -- if S.RESULT = KNOWN (PINT 46)\n'
 'def $tpp_stage(S,6) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n'
 '  -- if S.TODO = (ASSIGN_ARRAY pbase 6 false) :: ptask*\n'
 '  -- if S.RESULT = KNOWN (PINT 10)\n'
 'def $tpp_stage(S,7) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (ASSIGN_ARRAY pbase 25 false) :: ptask*\n'
 '  -- if S.RESULT = KNOWN (PINT 20)\n'
 'def $tpp_stage(S,n) = false -- otherwise\n'
 'dec $tpp_seek(pstate,nat,nat) : pstate\n'
 'def $tpp_seek(S,n_stage,n) = S\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if $tpp_stage(S,n_stage) \\/ n = 0\n'
 'def $tpp_seek(S,n_stage,n) = $tpp_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if ~$tpp_stage(S,n_stage) /\\ $(n > 0)\n'
 'def $tpp_seek(S,n_stage,n) = $tpp_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
 '  -- if $throwable_pending(S.COMPLETION) /\\ $(n > 0)\n'
 'def $tpp_seek(S,n_stage,n) = S -- otherwise\n'
 'dec $tpp_after(pstate,pstate) : pstate\n'
 'def $tpp_after(S,S_next) = '
 '$gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))\n'
 'dec $tpp_guard(pstate) : bool\n'
 'def $tpp_guard(S) = ($call_descriptors_valid(S) /\\ $declaration_history_valid(S) /\\ $property_state_valid(S) '
 '/\\ $heap_valid($heap_prune($heap_graph(S))))\n'
 'dec $tpp_is_output(pevent) : bool\n'
 'def $tpp_is_output(OUTPUT ptbytes) = true\n'
 'def $tpp_is_output(pevent) = false -- otherwise\n'
 'dec $tpp_output(pevent*) : ptbytes\n'
 'def $tpp_output(eps) = eps\n'
 'def $tpp_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $tpp_output(pevent*)\n'
 'def $tpp_output(pevent :: pevent_tail*) = $tpp_output(pevent_tail*)\n'
 '  -- if ~$tpp_is_output(pevent)\n')

COMMON = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedPairedHookTrait76"))) = (porigin_trait)',
 '$class_at(S.CLASSES,porigin_trait) = (pclassdesc_trait)',
 'pclassdesc_trait.KIND = "trait" /\\ pclassdesc_trait.PARENT = eps /\\ ~pclassdesc_trait.READONLY /\\ '
 '|pclassdesc_trait.PROPERTIES| = 1 /\\ pclassdesc_trait.METHODS = eps',
 '$origin_node(S.SOURCES,porigin_trait) = (NStmtTrait phpType14_trait phpType3_trait (SEQUENCE '
 'statement_trait_body*) metadata_trait)',
 '$trait_plan(S,pclassdesc_trait).TRAITS = eps',
 'ppropertydesc_source = pclassdesc_trait.PROPERTIES[0]',
 'ppropertydesc_source.ORIGIN = porigin_property_source',
 'porigin_property_source = PORIGIN n_source pcpath_property',
 'ppropertydesc_source.NAME = $ptascii("value") /\\ ppropertydesc_source.KEY = ppropertydesc_source.NAME /\\ '
 'ppropertydesc_source.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ ppropertydesc_source.VISIBILITY = '
 'PROPERTY_PUBLIC /\\ ppropertydesc_source.SETVISIBILITY = eps',
 '$property_default_state(S,ppropertydesc_source) = (PROP_VALUE (DIRECT (PINT 10))) /\\ '
 '~ppropertydesc_source.STATIC /\\ ~ppropertydesc_source.READONLY /\\ ~ppropertydesc_source.FINAL',
 '$property_hook_pair_declared(S,ppropertydesc_source)',
 '$property_hook_pair_origins(S,ppropertydesc_source) = porigin_get_source :: porigin_set_source :: eps',
 '$property_hook_origin(S,ppropertydesc_source) = (porigin_get_source) /\\ '
 '$property_set_origin(S,ppropertydesc_source) = (porigin_set_source) /\\ '
 '~$property_hook_virtual(S,ppropertydesc_source)',
 'porigin_get_source = PORIGIN n_source pcpath_get',
 'porigin_set_source = PORIGIN n_source pcpath_set',
 'pcpath_group = pcpath_property[0:$nabs($(|pcpath_property| - 2))]',
 'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0] /\\ pcpath_get = pcpath_group ++ [PCFIELD 4,PCINDEX 0] '
 '/\\ pcpath_set = pcpath_group ++ [PCFIELD 4,PCINDEX 1]',
 '$origin_node(S.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER flags) '
 'phpType18_group phpType56_group (SEQUENCE ([phpType38_get,phpType38_set])) metadata_group)',
 '$origin_node(S.SOURCES,porigin_get_source) = (phpType38_get)',
 '$origin_node(S.SOURCES,porigin_set_source) = (phpType38_set)',
 'phpType38_get = NPropertyHook phpType14_get phpType24_get phpType4_get phpType11_get phpType16_get (SEQUENCE '
 'statement_get*) metadata_get',
 'phpType38_set = NPropertyHook phpType14_set phpType24_set phpType4_set phpType11_set phpType16_set (SEQUENCE '
 'statement_set*) metadata_set',
 '$hook_pair_headers(phpType38_get,phpType38_set,ppropertydesc_source.NAME) /\\ $hook_body_backed(SEQUENCE '
 'statement_get*,ppropertydesc_source.NAME) /\\ $hook_body_backed(SEQUENCE '
 'statement_set*,ppropertydesc_source.NAME)',
 '$property_declaring_class(S.CLASSES,porigin_property_source) = (porigin_trait)',
 '$function_at(S.FUNCTIONS,porigin_get_source) = (pfunction_get_source)',
 '$function_at(S.FUNCTIONS,porigin_set_source) = (pfunction_set_source)',
 'S.FUNCTIONS = [pfunction_get_source,pfunction_set_source]',
 'pfunction_get_source.ORIGIN = porigin_get_source /\\ pfunction_set_source.ORIGIN = porigin_set_source /\\ '
 'pfunction_get_source.BODY = pcpath_get ++ [PCFIELD 5] /\\ pfunction_set_source.BODY = pcpath_set ++ [PCFIELD 5]',
 'pfunction_get_source.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_source.TYPE, BYREF false} /\\ '
 'pfunction_set_source.SIGNATURE = $property_set_signature(ppropertydesc_source)',
 'pfunction_get_source.NAME = pclassdesc_trait.NAME ++ $ptascii("::$value::get") /\\ pfunction_set_source.NAME = '
 'pclassdesc_trait.NAME ++ $ptascii("::$value::set")',
 'pfunction_get_source.DEFAULTS = eps /\\ pfunction_set_source.DEFAULTS = eps /\\ ~pfunction_get_source.EARLY /\\ '
 '~pfunction_set_source.EARLY /\\ pfunction_get_source.LINE = 4 /\\ pfunction_get_source.ENDLINE = 8 /\\ '
 'pfunction_set_source.LINE = 9 /\\ pfunction_set_source.ENDLINE = 12',
 '$property_hook_pair_raw_functions(S,ppropertydesc_source) = pfunction_get_source :: pfunction_set_source :: eps',
 '$origin_node(S.SOURCES,PORIGIN n_source (pcpath_get ++ [PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 5])) = '
 '(NScalarMagicConstMethod metadata_get_method)',
 '$origin_node(S.SOURCES,PORIGIN n_source (pcpath_get ++ [PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 7])) = '
 '(NScalarMagicConstTrait metadata_get_trait)',
 '$origin_node(S.SOURCES,PORIGIN n_source (pcpath_set ++ [PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 5])) = '
 '(NScalarMagicConstMethod metadata_set_method)',
 '$origin_node(S.SOURCES,PORIGIN n_source (pcpath_set ++ [PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 7])) = '
 '(NScalarMagicConstTrait metadata_set_trait)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedPairedHookConsumer76"))) = (porigin_consumer)',
 '$class_at(S.CLASSES,porigin_consumer) = (pclassdesc_consumer)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedPairedHookGrand76"))) = (porigin_grand)',
 '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
 'pclassdesc_consumer.KIND = "class" /\\ pclassdesc_consumer.PARENT = eps /\\ ~pclassdesc_consumer.READONLY /\\ '
 '|pclassdesc_consumer.PROPERTIES| = 1 /\\ pclassdesc_grand.PROPERTIES = eps',
 '$class_link_at(S.LINKEDPARENTS,porigin_consumer) = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_grand) = '
 '(SOURCE_PARENT porigin_consumer)',
 'ppropertydesc = pclassdesc_consumer.PROPERTIES[0]',
 'ppropertydesc.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_consumer porigin_property_source /\\ ppropertydesc = '
 '$trait_data_property(pclassdesc_consumer,ppropertydesc_source)',
 'ppropertydesc.ORIGIN = porigin_property',
 '$property_hook_pair_declared(S,ppropertydesc) /\\ $property_hook_pair_origins(S,ppropertydesc) = eps',
 '$property_set_trait_source(S,pclassdesc_consumer,ppropertydesc_source) = (porigin_set_source) /\\ '
 '$property_hook_trait_import_supported(S,pclassdesc_consumer,ppropertydesc_source)',
 '$property_hook_trait_origin(S,ppropertydesc) = (porigin_get)',
 '$property_set_trait_origin(S,ppropertydesc) = (porigin_set)',
 'porigin_get = TRAIT_ORIGIN porigin_consumer porigin_get_source ($hook_name(ppropertydesc.NAME))',
 'porigin_set = TRAIT_ORIGIN porigin_consumer porigin_set_source ($property_set_name(ppropertydesc.NAME))',
 '$property_hook_effective_origin(S,ppropertydesc) = (porigin_get) /\\ $property_set_origin(S,ppropertydesc) = '
 '(porigin_set) /\\ porigin_get =/= porigin_set /\\ ~$property_hook_virtual(S,ppropertydesc)',
 '$property_hook_trait_pair_functions(S,ppropertydesc) = pfunction_get :: pfunction_set :: eps',
 '$property_hook_trait_property_functions(S,[ppropertydesc]) = [pfunction_get,pfunction_set] /\\ '
 '$property_hook_trait_property_functions(S,[ppropertydesc_source]) = eps',
 '$property_hook_trait_function(S,ppropertydesc) = eps /\\ $property_hook_trait_function(S,ppropertydesc_source) '
 '= eps',
 '$function_at($all_functions(S),porigin_get) = (pfunction_get) /\\ $function_at($all_functions(S),porigin_set) = '
 '(pfunction_set) /\\ $function_at(S.FUNCTIONS,porigin_get) = eps /\\ $function_at(S.FUNCTIONS,porigin_set) = eps',
 'pfunction_get = pfunction_get_source[.ORIGIN = porigin_get][.NAME = pclassdesc_consumer.NAME ++ '
 '$ptascii("::$value::get")]',
 'pfunction_set = pfunction_set_source[.ORIGIN = porigin_set][.NAME = pclassdesc_consumer.NAME ++ '
 '$ptascii("::$value::set")]',
 '$origin_source(porigin_get) = porigin_get_source /\\ $origin_source(porigin_set) = porigin_set_source',
 '$property_declaring_class(S.CLASSES,porigin_property) = (porigin_consumer)',
 '$property_layout(S,porigin_consumer,|S.CLASSES|) = [ppropertydesc] /\\ '
 '$property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc]',
 '$method_named(pclassdesc_consumer.METHODS,$ptascii("offset")) = (pmethoddesc_consumer_offset)',
 '$method_named(pclassdesc_grand.METHODS,$ptascii("offset")) = (pmethoddesc_grand_offset)',
 'pmethoddesc_consumer_offset.OWNER = porigin_consumer /\\ pmethoddesc_consumer_offset.VISIBILITY = '
 'PROPERTY_PRIVATE /\\ pmethoddesc_grand_offset.OWNER = porigin_grand /\\ pmethoddesc_grand_offset.VISIBILITY = '
 'PROPERTY_PRIVATE',
 '$lookup(S.ENV,$ptascii("grand")) = (n_grand_cell)',
 'S.STORE[n_grand_cell] = DEFINED (POBJECT n_grand)',
 'S.OBJECTS[n_grand] = INSTANCE porigin_grand /\\ (HOBJECT n_grand) <- S.ALLOCATIONS',
 '$property_effective_desc(S,n_grand,$ptascii("value")) = (ppropertydesc) /\\ $property_hook_instance(S,n_grand) '
 '/\\ $property_hook_declared(S,n_grand,$ptascii("value"))',
 '$property_resolve(S,n_grand,$ptascii("value")) = PROPERTY_ACCESS ppropertydesc.KEY',
 '$objectprops_at(S.OBJECTPROPS,n_grand) = ([{DECL (porigin_property), NAME ppropertydesc.KEY, STATE PROP_VALUE '
 '(DIRECT (PINT 10))}])',
 '$tpp_guard(S)']

GET = ['$tpp_stage(S,0)',
 'S.CURRENT = eps /\\ S.FRAMES = eps',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedPairedHookTrait76"))) = (porigin_trait)',
 '$class_at(S.CLASSES,porigin_trait) = (pclassdesc_trait)',
 'pclassdesc_trait.KIND = "trait" /\\ pclassdesc_trait.PARENT = eps /\\ ~pclassdesc_trait.READONLY /\\ '
 '|pclassdesc_trait.PROPERTIES| = 1 /\\ pclassdesc_trait.METHODS = eps',
 '$origin_node(S.SOURCES,porigin_trait) = (NStmtTrait phpType14_trait phpType3_trait (SEQUENCE '
 'statement_trait_body*) metadata_trait)',
 '$trait_plan(S,pclassdesc_trait).TRAITS = eps',
 'ppropertydesc_source = pclassdesc_trait.PROPERTIES[0]',
 'ppropertydesc_source.ORIGIN = porigin_property_source',
 'porigin_property_source = PORIGIN n_source pcpath_property',
 'ppropertydesc_source.NAME = $ptascii("value") /\\ ppropertydesc_source.KEY = ppropertydesc_source.NAME /\\ '
 'ppropertydesc_source.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ ppropertydesc_source.VISIBILITY = '
 'PROPERTY_PUBLIC /\\ ppropertydesc_source.SETVISIBILITY = eps',
 '$property_default_state(S,ppropertydesc_source) = (PROP_VALUE (DIRECT (PINT 10))) /\\ '
 '~ppropertydesc_source.STATIC /\\ ~ppropertydesc_source.READONLY /\\ ~ppropertydesc_source.FINAL',
 '$property_hook_pair_declared(S,ppropertydesc_source)',
 '$property_hook_pair_origins(S,ppropertydesc_source) = porigin_get_source :: porigin_set_source :: eps',
 '$property_hook_origin(S,ppropertydesc_source) = (porigin_get_source) /\\ '
 '$property_set_origin(S,ppropertydesc_source) = (porigin_set_source) /\\ '
 '~$property_hook_virtual(S,ppropertydesc_source)',
 'porigin_get_source = PORIGIN n_source pcpath_get',
 'porigin_set_source = PORIGIN n_source pcpath_set',
 'pcpath_group = pcpath_property[0:$nabs($(|pcpath_property| - 2))]',
 'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0] /\\ pcpath_get = pcpath_group ++ [PCFIELD 4,PCINDEX 0] '
 '/\\ pcpath_set = pcpath_group ++ [PCFIELD 4,PCINDEX 1]',
 '$origin_node(S.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER flags) '
 'phpType18_group phpType56_group (SEQUENCE ([phpType38_get,phpType38_set])) metadata_group)',
 '$origin_node(S.SOURCES,porigin_get_source) = (phpType38_get)',
 '$origin_node(S.SOURCES,porigin_set_source) = (phpType38_set)',
 'phpType38_get = NPropertyHook phpType14_get phpType24_get phpType4_get phpType11_get phpType16_get (SEQUENCE '
 'statement_get*) metadata_get',
 'phpType38_set = NPropertyHook phpType14_set phpType24_set phpType4_set phpType11_set phpType16_set (SEQUENCE '
 'statement_set*) metadata_set',
 '$hook_pair_headers(phpType38_get,phpType38_set,ppropertydesc_source.NAME) /\\ $hook_body_backed(SEQUENCE '
 'statement_get*,ppropertydesc_source.NAME) /\\ $hook_body_backed(SEQUENCE '
 'statement_set*,ppropertydesc_source.NAME)',
 '$property_declaring_class(S.CLASSES,porigin_property_source) = (porigin_trait)',
 '$function_at(S.FUNCTIONS,porigin_get_source) = (pfunction_get_source)',
 '$function_at(S.FUNCTIONS,porigin_set_source) = (pfunction_set_source)',
 'S.FUNCTIONS = [pfunction_get_source,pfunction_set_source]',
 'pfunction_get_source.ORIGIN = porigin_get_source /\\ pfunction_set_source.ORIGIN = porigin_set_source /\\ '
 'pfunction_get_source.BODY = pcpath_get ++ [PCFIELD 5] /\\ pfunction_set_source.BODY = pcpath_set ++ [PCFIELD 5]',
 'pfunction_get_source.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_source.TYPE, BYREF false} /\\ '
 'pfunction_set_source.SIGNATURE = $property_set_signature(ppropertydesc_source)',
 'pfunction_get_source.NAME = pclassdesc_trait.NAME ++ $ptascii("::$value::get") /\\ pfunction_set_source.NAME = '
 'pclassdesc_trait.NAME ++ $ptascii("::$value::set")',
 'pfunction_get_source.DEFAULTS = eps /\\ pfunction_set_source.DEFAULTS = eps /\\ ~pfunction_get_source.EARLY /\\ '
 '~pfunction_set_source.EARLY /\\ pfunction_get_source.LINE = 4 /\\ pfunction_get_source.ENDLINE = 8 /\\ '
 'pfunction_set_source.LINE = 9 /\\ pfunction_set_source.ENDLINE = 12',
 '$property_hook_pair_raw_functions(S,ppropertydesc_source) = pfunction_get_source :: pfunction_set_source :: eps',
 '$origin_node(S.SOURCES,PORIGIN n_source (pcpath_get ++ [PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 5])) = '
 '(NScalarMagicConstMethod metadata_get_method)',
 '$origin_node(S.SOURCES,PORIGIN n_source (pcpath_get ++ [PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 7])) = '
 '(NScalarMagicConstTrait metadata_get_trait)',
 '$origin_node(S.SOURCES,PORIGIN n_source (pcpath_set ++ [PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 5])) = '
 '(NScalarMagicConstMethod metadata_set_method)',
 '$origin_node(S.SOURCES,PORIGIN n_source (pcpath_set ++ [PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 7])) = '
 '(NScalarMagicConstTrait metadata_set_trait)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedPairedHookConsumer76"))) = (porigin_consumer)',
 '$class_at(S.CLASSES,porigin_consumer) = (pclassdesc_consumer)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedPairedHookGrand76"))) = (porigin_grand)',
 '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
 'pclassdesc_consumer.KIND = "class" /\\ pclassdesc_consumer.PARENT = eps /\\ ~pclassdesc_consumer.READONLY /\\ '
 '|pclassdesc_consumer.PROPERTIES| = 1 /\\ pclassdesc_grand.PROPERTIES = eps',
 '$class_link_at(S.LINKEDPARENTS,porigin_consumer) = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_grand) = '
 '(SOURCE_PARENT porigin_consumer)',
 'ppropertydesc = pclassdesc_consumer.PROPERTIES[0]',
 'ppropertydesc.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_consumer porigin_property_source /\\ ppropertydesc = '
 '$trait_data_property(pclassdesc_consumer,ppropertydesc_source)',
 'ppropertydesc.ORIGIN = porigin_property',
 '$property_hook_pair_declared(S,ppropertydesc) /\\ $property_hook_pair_origins(S,ppropertydesc) = eps',
 '$property_set_trait_source(S,pclassdesc_consumer,ppropertydesc_source) = (porigin_set_source) /\\ '
 '$property_hook_trait_import_supported(S,pclassdesc_consumer,ppropertydesc_source)',
 '$property_hook_trait_origin(S,ppropertydesc) = (porigin_get)',
 '$property_set_trait_origin(S,ppropertydesc) = (porigin_set)',
 'porigin_get = TRAIT_ORIGIN porigin_consumer porigin_get_source ($hook_name(ppropertydesc.NAME))',
 'porigin_set = TRAIT_ORIGIN porigin_consumer porigin_set_source ($property_set_name(ppropertydesc.NAME))',
 '$property_hook_effective_origin(S,ppropertydesc) = (porigin_get) /\\ $property_set_origin(S,ppropertydesc) = '
 '(porigin_set) /\\ porigin_get =/= porigin_set /\\ ~$property_hook_virtual(S,ppropertydesc)',
 '$property_hook_trait_pair_functions(S,ppropertydesc) = pfunction_get :: pfunction_set :: eps',
 '$property_hook_trait_property_functions(S,[ppropertydesc]) = [pfunction_get,pfunction_set] /\\ '
 '$property_hook_trait_property_functions(S,[ppropertydesc_source]) = eps',
 '$property_hook_trait_function(S,ppropertydesc) = eps /\\ $property_hook_trait_function(S,ppropertydesc_source) '
 '= eps',
 '$function_at($all_functions(S),porigin_get) = (pfunction_get) /\\ $function_at($all_functions(S),porigin_set) = '
 '(pfunction_set) /\\ $function_at(S.FUNCTIONS,porigin_get) = eps /\\ $function_at(S.FUNCTIONS,porigin_set) = eps',
 'pfunction_get = pfunction_get_source[.ORIGIN = porigin_get][.NAME = pclassdesc_consumer.NAME ++ '
 '$ptascii("::$value::get")]',
 'pfunction_set = pfunction_set_source[.ORIGIN = porigin_set][.NAME = pclassdesc_consumer.NAME ++ '
 '$ptascii("::$value::set")]',
 '$origin_source(porigin_get) = porigin_get_source /\\ $origin_source(porigin_set) = porigin_set_source',
 '$property_declaring_class(S.CLASSES,porigin_property) = (porigin_consumer)',
 '$property_layout(S,porigin_consumer,|S.CLASSES|) = [ppropertydesc] /\\ '
 '$property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc]',
 '$method_named(pclassdesc_consumer.METHODS,$ptascii("offset")) = (pmethoddesc_consumer_offset)',
 '$method_named(pclassdesc_grand.METHODS,$ptascii("offset")) = (pmethoddesc_grand_offset)',
 'pmethoddesc_consumer_offset.OWNER = porigin_consumer /\\ pmethoddesc_consumer_offset.VISIBILITY = '
 'PROPERTY_PRIVATE /\\ pmethoddesc_grand_offset.OWNER = porigin_grand /\\ pmethoddesc_grand_offset.VISIBILITY = '
 'PROPERTY_PRIVATE',
 '$lookup(S.ENV,$ptascii("grand")) = (n_grand_cell)',
 'S.STORE[n_grand_cell] = DEFINED (POBJECT n_grand)',
 'S.OBJECTS[n_grand] = INSTANCE porigin_grand /\\ (HOBJECT n_grand) <- S.ALLOCATIONS',
 '$property_effective_desc(S,n_grand,$ptascii("value")) = (ppropertydesc) /\\ $property_hook_instance(S,n_grand) '
 '/\\ $property_hook_declared(S,n_grand,$ptascii("value"))',
 '$property_resolve(S,n_grand,$ptascii("value")) = PROPERTY_ACCESS ppropertydesc.KEY',
 '$objectprops_at(S.OBJECTPROPS,n_grand) = ([{DECL (porigin_property), NAME ppropertydesc.KEY, STATE PROP_VALUE '
 '(DIRECT (PINT 10))}])',
 '$tpp_guard(S)',
 'S.ORIGIN = (porigin_site)',
 'S.TODO = (PROPERTY_PREP phpType20_read 24) :: (DIM_FETCH 24) :: ptask_caller*',
 '$property_hook_plan(S) = (ppropertyhook_get)',
 'ppropertyhook_get = {SITE porigin_site, OBJECT n_grand, PROPERTY porigin_property, HOOK porigin_get, LINE 24}',
 '$property_hook_function(S,ppropertyhook_get) = (pfunction_get) /\\ $property_hook_pending(S) /\\ '
 '$property_hook_read_needed(S,n_grand,$ptascii("value"))',
 'PhpStep: S ~> S_call_raw',
 'S_call = $tpp_after(S,S_call_raw)',
 'S_call.TODO = (CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook_get) eps 0 eps (porigin_site) 24) :: '
 '(PROPERTY_HOOK_RESULT ppropertyhook_get) :: ptask_caller*',
 'S_call.CURRENT = eps /\\ S_call.OBJECTPROPS = S.OBJECTPROPS /\\ S_call.EVENTS = S.EVENTS /\\ S_call.ORIGIN = '
 '(porigin_site)',
 '$property_hook_pending_call(S_call,ppropertyhook_get) /\\ $call_task_valid(S_call,CALL_ARGS '
 '(PROPERTY_HOOK_TARGET ppropertyhook_get) eps 0 eps (porigin_site) 24) /\\ $tpp_guard(S_call)',
 'PhpStep: S_call ~> S_entered_raw',
 'S_entered = $tpp_after(S_call,S_entered_raw)',
 'S_entered.CURRENT = (pcallcontext_get)',
 'pcallcontext_get.TARGET = PROPERTY_HOOK_TARGET ppropertyhook_get /\\ pcallcontext_get.FUNCTION = porigin_get '
 '/\\ pcallcontext_get.LEXICAL_CLASS = (porigin_consumer) /\\ pcallcontext_get.CALLED_CLASS = (porigin_grand) /\\ '
 'pcallcontext_get.RECEIVER = (n_grand) /\\ pcallcontext_get.ARGC = 0',
 '$property_hook_context_valid(S_entered,pcallcontext_get) /\\ '
 '$property_hook_entered(S_entered,S_entered.CURRENT,S_entered.FRAMES,ppropertyhook_get) /\\ '
 '$tpp_guard(S_entered)',
 'S_cross_found = $tpp_seek(S_entered,6,1000)',
 'S_cross_found.COMPLETION = NORMAL \\/ S_cross_found.COMPLETION = BUDGET',
 'S_cross = S_cross_found[.COMPLETION = NORMAL]',
 '$tpp_stage(S_cross,6)',
 'S_cross.CURRENT = S_entered.CURRENT /\\ S_cross.FRAMES = S_entered.FRAMES /\\ S_cross.OBJECTPROPS = '
 'S.OBJECTPROPS',
 '$property_hook_backing(S_cross,n_grand,ppropertydesc) /\\ $property_set_backing(S_cross,n_grand,ppropertydesc) '
 '/\\ ~$property_hook_read_needed(S_cross,n_grand,$ptascii("value")) /\\ '
 '~$property_set_needed(S_cross,n_grand,$ptascii("value")) /\\ ~$property_set_pending(S_cross)',
 '$method_selected_scope(S_cross,n_grand,$ptascii("offset"),(porigin_consumer)) = (pmethoddesc_consumer_offset)',
 'S_cross.TODO = (ASSIGN_ARRAY pbase_write 6 false) :: ptask_write*',
 'S_cross.RESULT = KNOWN (PINT 10) /\\ $call_task_valid(S_cross,ASSIGN_ARRAY pbase_write 6 false)',
 '$tpp_output(S_cross.EVENTS) = '
 '$ptascii("I:10/GET:ImportedPairedHookConsumer76/ImportedPairedHookGrand76/ImportedPairedHookTrait76::$value::get/ImportedPairedHookTrait76|")',
 'PhpStep: S_cross ~> S_written_raw',
 'S_written = $tpp_after(S_cross,S_written_raw)',
 'S_written.COMPLETION = NORMAL /\\ S_written.RESULT = KNOWN (PINT 10) /\\ S_written.CURRENT = S_cross.CURRENT '
 '/\\ S_written.FRAMES = S_cross.FRAMES /\\ S_written.EVENTS = S_cross.EVENTS /\\ S_written.OBJECTPROPS = '
 'S_cross.OBJECTPROPS',
 '$tpp_guard(S_written)',
 'S_return_found = $tpp_seek(S_written,4,1000)',
 'S_return_found.COMPLETION = NORMAL \\/ S_return_found.COMPLETION = BUDGET',
 'S_return = S_return_found[.COMPLETION = NORMAL]',
 '$tpp_stage(S_return,4)',
 'S_return.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_get) :: ptask_return*',
 'S_return.CURRENT = eps /\\ S_return.FRAMES = eps /\\ S_return.RESULT = KNOWN (PINT 23) /\\ S_return.OBJECTPROPS '
 '= S.OBJECTPROPS /\\ S_return.ORIGIN = (porigin_site)',
 '$call_task_valid(S_return,PROPERTY_HOOK_RESULT ppropertyhook_get) /\\ '
 '$property_hook_read_needed(S_return,n_grand,$ptascii("value")) /\\ '
 '$property_set_needed(S_return,n_grand,$ptascii("value")) /\\ '
 '~$property_set_backing(S_return,n_grand,ppropertydesc) /\\ $tpp_guard(S_return)',
 'PhpStep: S_return ~> S_result_raw',
 'S_result = $tpp_after(S_return,S_result_raw)',
 'S_result.COMPLETION = NORMAL /\\ S_result.RESULT = KNOWN (PINT 23) /\\ S_result.BASE = BASE_VALUE (KNOWN (PINT '
 '23)) /\\ S_result.TODO = ptask_return* /\\ S_result.OBJECTPROPS = S.OBJECTPROPS',
 '$tpp_guard(S_result)']

SET = ['$tpp_stage(S,7)',
 'S.CURRENT = eps /\\ S.FRAMES = eps',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedPairedHookTrait76"))) = (porigin_trait)',
 '$class_at(S.CLASSES,porigin_trait) = (pclassdesc_trait)',
 'pclassdesc_trait.KIND = "trait" /\\ pclassdesc_trait.PARENT = eps /\\ ~pclassdesc_trait.READONLY /\\ '
 '|pclassdesc_trait.PROPERTIES| = 1 /\\ pclassdesc_trait.METHODS = eps',
 '$origin_node(S.SOURCES,porigin_trait) = (NStmtTrait phpType14_trait phpType3_trait (SEQUENCE '
 'statement_trait_body*) metadata_trait)',
 '$trait_plan(S,pclassdesc_trait).TRAITS = eps',
 'ppropertydesc_source = pclassdesc_trait.PROPERTIES[0]',
 'ppropertydesc_source.ORIGIN = porigin_property_source',
 'porigin_property_source = PORIGIN n_source pcpath_property',
 'ppropertydesc_source.NAME = $ptascii("value") /\\ ppropertydesc_source.KEY = ppropertydesc_source.NAME /\\ '
 'ppropertydesc_source.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ ppropertydesc_source.VISIBILITY = '
 'PROPERTY_PUBLIC /\\ ppropertydesc_source.SETVISIBILITY = eps',
 '$property_default_state(S,ppropertydesc_source) = (PROP_VALUE (DIRECT (PINT 10))) /\\ '
 '~ppropertydesc_source.STATIC /\\ ~ppropertydesc_source.READONLY /\\ ~ppropertydesc_source.FINAL',
 '$property_hook_pair_declared(S,ppropertydesc_source)',
 '$property_hook_pair_origins(S,ppropertydesc_source) = porigin_get_source :: porigin_set_source :: eps',
 '$property_hook_origin(S,ppropertydesc_source) = (porigin_get_source) /\\ '
 '$property_set_origin(S,ppropertydesc_source) = (porigin_set_source) /\\ '
 '~$property_hook_virtual(S,ppropertydesc_source)',
 'porigin_get_source = PORIGIN n_source pcpath_get',
 'porigin_set_source = PORIGIN n_source pcpath_set',
 'pcpath_group = pcpath_property[0:$nabs($(|pcpath_property| - 2))]',
 'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0] /\\ pcpath_get = pcpath_group ++ [PCFIELD 4,PCINDEX 0] '
 '/\\ pcpath_set = pcpath_group ++ [PCFIELD 4,PCINDEX 1]',
 '$origin_node(S.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER flags) '
 'phpType18_group phpType56_group (SEQUENCE ([phpType38_get,phpType38_set])) metadata_group)',
 '$origin_node(S.SOURCES,porigin_get_source) = (phpType38_get)',
 '$origin_node(S.SOURCES,porigin_set_source) = (phpType38_set)',
 'phpType38_get = NPropertyHook phpType14_get phpType24_get phpType4_get phpType11_get phpType16_get (SEQUENCE '
 'statement_get*) metadata_get',
 'phpType38_set = NPropertyHook phpType14_set phpType24_set phpType4_set phpType11_set phpType16_set (SEQUENCE '
 'statement_set*) metadata_set',
 '$hook_pair_headers(phpType38_get,phpType38_set,ppropertydesc_source.NAME) /\\ $hook_body_backed(SEQUENCE '
 'statement_get*,ppropertydesc_source.NAME) /\\ $hook_body_backed(SEQUENCE '
 'statement_set*,ppropertydesc_source.NAME)',
 '$property_declaring_class(S.CLASSES,porigin_property_source) = (porigin_trait)',
 '$function_at(S.FUNCTIONS,porigin_get_source) = (pfunction_get_source)',
 '$function_at(S.FUNCTIONS,porigin_set_source) = (pfunction_set_source)',
 'S.FUNCTIONS = [pfunction_get_source,pfunction_set_source]',
 'pfunction_get_source.ORIGIN = porigin_get_source /\\ pfunction_set_source.ORIGIN = porigin_set_source /\\ '
 'pfunction_get_source.BODY = pcpath_get ++ [PCFIELD 5] /\\ pfunction_set_source.BODY = pcpath_set ++ [PCFIELD 5]',
 'pfunction_get_source.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_source.TYPE, BYREF false} /\\ '
 'pfunction_set_source.SIGNATURE = $property_set_signature(ppropertydesc_source)',
 'pfunction_get_source.NAME = pclassdesc_trait.NAME ++ $ptascii("::$value::get") /\\ pfunction_set_source.NAME = '
 'pclassdesc_trait.NAME ++ $ptascii("::$value::set")',
 'pfunction_get_source.DEFAULTS = eps /\\ pfunction_set_source.DEFAULTS = eps /\\ ~pfunction_get_source.EARLY /\\ '
 '~pfunction_set_source.EARLY /\\ pfunction_get_source.LINE = 4 /\\ pfunction_get_source.ENDLINE = 8 /\\ '
 'pfunction_set_source.LINE = 9 /\\ pfunction_set_source.ENDLINE = 12',
 '$property_hook_pair_raw_functions(S,ppropertydesc_source) = pfunction_get_source :: pfunction_set_source :: eps',
 '$origin_node(S.SOURCES,PORIGIN n_source (pcpath_get ++ [PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 5])) = '
 '(NScalarMagicConstMethod metadata_get_method)',
 '$origin_node(S.SOURCES,PORIGIN n_source (pcpath_get ++ [PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 7])) = '
 '(NScalarMagicConstTrait metadata_get_trait)',
 '$origin_node(S.SOURCES,PORIGIN n_source (pcpath_set ++ [PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 5])) = '
 '(NScalarMagicConstMethod metadata_set_method)',
 '$origin_node(S.SOURCES,PORIGIN n_source (pcpath_set ++ [PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 7])) = '
 '(NScalarMagicConstTrait metadata_set_trait)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedPairedHookConsumer76"))) = (porigin_consumer)',
 '$class_at(S.CLASSES,porigin_consumer) = (pclassdesc_consumer)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("ImportedPairedHookGrand76"))) = (porigin_grand)',
 '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
 'pclassdesc_consumer.KIND = "class" /\\ pclassdesc_consumer.PARENT = eps /\\ ~pclassdesc_consumer.READONLY /\\ '
 '|pclassdesc_consumer.PROPERTIES| = 1 /\\ pclassdesc_grand.PROPERTIES = eps',
 '$class_link_at(S.LINKEDPARENTS,porigin_consumer) = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_grand) = '
 '(SOURCE_PARENT porigin_consumer)',
 'ppropertydesc = pclassdesc_consumer.PROPERTIES[0]',
 'ppropertydesc.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_consumer porigin_property_source /\\ ppropertydesc = '
 '$trait_data_property(pclassdesc_consumer,ppropertydesc_source)',
 'ppropertydesc.ORIGIN = porigin_property',
 '$property_hook_pair_declared(S,ppropertydesc) /\\ $property_hook_pair_origins(S,ppropertydesc) = eps',
 '$property_set_trait_source(S,pclassdesc_consumer,ppropertydesc_source) = (porigin_set_source) /\\ '
 '$property_hook_trait_import_supported(S,pclassdesc_consumer,ppropertydesc_source)',
 '$property_hook_trait_origin(S,ppropertydesc) = (porigin_get)',
 '$property_set_trait_origin(S,ppropertydesc) = (porigin_set)',
 'porigin_get = TRAIT_ORIGIN porigin_consumer porigin_get_source ($hook_name(ppropertydesc.NAME))',
 'porigin_set = TRAIT_ORIGIN porigin_consumer porigin_set_source ($property_set_name(ppropertydesc.NAME))',
 '$property_hook_effective_origin(S,ppropertydesc) = (porigin_get) /\\ $property_set_origin(S,ppropertydesc) = '
 '(porigin_set) /\\ porigin_get =/= porigin_set /\\ ~$property_hook_virtual(S,ppropertydesc)',
 '$property_hook_trait_pair_functions(S,ppropertydesc) = pfunction_get :: pfunction_set :: eps',
 '$property_hook_trait_property_functions(S,[ppropertydesc]) = [pfunction_get,pfunction_set] /\\ '
 '$property_hook_trait_property_functions(S,[ppropertydesc_source]) = eps',
 '$property_hook_trait_function(S,ppropertydesc) = eps /\\ $property_hook_trait_function(S,ppropertydesc_source) '
 '= eps',
 '$function_at($all_functions(S),porigin_get) = (pfunction_get) /\\ $function_at($all_functions(S),porigin_set) = '
 '(pfunction_set) /\\ $function_at(S.FUNCTIONS,porigin_get) = eps /\\ $function_at(S.FUNCTIONS,porigin_set) = eps',
 'pfunction_get = pfunction_get_source[.ORIGIN = porigin_get][.NAME = pclassdesc_consumer.NAME ++ '
 '$ptascii("::$value::get")]',
 'pfunction_set = pfunction_set_source[.ORIGIN = porigin_set][.NAME = pclassdesc_consumer.NAME ++ '
 '$ptascii("::$value::set")]',
 '$origin_source(porigin_get) = porigin_get_source /\\ $origin_source(porigin_set) = porigin_set_source',
 '$property_declaring_class(S.CLASSES,porigin_property) = (porigin_consumer)',
 '$property_layout(S,porigin_consumer,|S.CLASSES|) = [ppropertydesc] /\\ '
 '$property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc]',
 '$method_named(pclassdesc_consumer.METHODS,$ptascii("offset")) = (pmethoddesc_consumer_offset)',
 '$method_named(pclassdesc_grand.METHODS,$ptascii("offset")) = (pmethoddesc_grand_offset)',
 'pmethoddesc_consumer_offset.OWNER = porigin_consumer /\\ pmethoddesc_consumer_offset.VISIBILITY = '
 'PROPERTY_PRIVATE /\\ pmethoddesc_grand_offset.OWNER = porigin_grand /\\ pmethoddesc_grand_offset.VISIBILITY = '
 'PROPERTY_PRIVATE',
 '$lookup(S.ENV,$ptascii("grand")) = (n_grand_cell)',
 'S.STORE[n_grand_cell] = DEFINED (POBJECT n_grand)',
 'S.OBJECTS[n_grand] = INSTANCE porigin_grand /\\ (HOBJECT n_grand) <- S.ALLOCATIONS',
 '$property_effective_desc(S,n_grand,$ptascii("value")) = (ppropertydesc) /\\ $property_hook_instance(S,n_grand) '
 '/\\ $property_hook_declared(S,n_grand,$ptascii("value"))',
 '$property_resolve(S,n_grand,$ptascii("value")) = PROPERTY_ACCESS ppropertydesc.KEY',
 '$objectprops_at(S.OBJECTPROPS,n_grand) = ([{DECL (porigin_property), NAME ppropertydesc.KEY, STATE PROP_VALUE '
 '(DIRECT (PINT 10))}])',
 '$tpp_guard(S)',
 'S.ORIGIN = (porigin_site)',
 '$property_set_plan(S) = (ppropertyhook_set)',
 'ppropertyhook_set = {SITE porigin_site, OBJECT n_grand, PROPERTY porigin_property, HOOK porigin_set, LINE 25}',
 '$property_set_valid(S,ppropertyhook_set) /\\ $property_set_function(S,ppropertyhook_set) = (pfunction_set) /\\ '
 '$property_set_pending(S)',
 '$property_set_needed(S,n_grand,$ptascii("value")) /\\ ~$property_set_backing(S,n_grand,ppropertydesc)',
 'PhpStep: S ~> S_call_raw',
 'S_call = $tpp_after(S,S_call_raw)',
 'S_call.TODO = (CALL_ARGS (PROPERTY_SET_TARGET ppropertyhook_set) eps 1 ([KNOWN (PINT 20)]) (porigin_site) 25) '
 ':: (PROPERTY_SET_RESULT ppropertyhook_set (PINT 20)) :: ptask_caller*',
 'S_call.CURRENT = eps /\\ S_call.OBJECTPROPS = S.OBJECTPROPS /\\ S_call.EVENTS = S.EVENTS /\\ S_call.ORIGIN = '
 '(porigin_site)',
 '$property_set_pending_call(S_call,ppropertyhook_set) /\\ $call_task_valid(S_call,CALL_ARGS (PROPERTY_SET_TARGET '
 'ppropertyhook_set) eps 1 ([KNOWN (PINT 20)]) (porigin_site) 25) /\\ $tpp_guard(S_call)',
 'PhpStep: S_call ~> S_entered_raw',
 'S_entered = $tpp_after(S_call,S_entered_raw)',
 'S_entered.CURRENT = (pcallcontext_set)',
 'pcallcontext_set.TARGET = PROPERTY_SET_TARGET ppropertyhook_set /\\ pcallcontext_set.FUNCTION = porigin_set /\\ '
 'pcallcontext_set.ARGC = 1 /\\ pcallcontext_set.CALLSITE = (porigin_site) /\\ pcallcontext_set.LINE = 25',
 'pcallcontext_set.LEXICAL_CLASS = (porigin_consumer) /\\ pcallcontext_set.CALLED_CLASS = (porigin_grand) /\\ '
 'pcallcontext_set.RECEIVER = (n_grand) /\\ pcallcontext_set.PARAMS = [$ptascii("value")]',
 'S_entered.TODO = [TYPE_RECEIVE porigin_set 0] /\\ S_entered.ORIGIN = (porigin_set)',
 '$lookup(S_entered.ENV,$ptascii("value")) = (n_value_cell)',
 'S_entered.STORE[n_value_cell] = DEFINED (PINT 20)',
 '$typed_receive_valid(S_entered,porigin_set,0) /\\ $named_receives_ready(S_entered,pfunction_set) /\\ '
 '$default_parameter_line(S_entered,porigin_set,0) = 9',
 '$property_set_context_valid(S_entered,pcallcontext_set) /\\ '
 '$property_set_entered(S_entered,S_entered.CURRENT,S_entered.FRAMES,ppropertyhook_set) /\\ '
 '$call_receiver_roots(pcallcontext_set) = eps',
 'S_entered.OBJECTPROPS = S.OBJECTPROPS /\\ S_entered.EVENTS = S.EVENTS /\\ $tpp_guard(S_entered)',
 'PhpStep: S_entered ~> S_received_raw',
 'S_received = $tpp_after(S_entered,S_received_raw)',
 'S_received.COMPLETION = NORMAL /\\ S_received.CURRENT = S_entered.CURRENT /\\ S_received.FRAMES = '
 'S_entered.FRAMES /\\ S_received.EVENTS = S.EVENTS /\\ S_received.OBJECTPROPS = S.OBJECTPROPS',
 'S_received.TODO = $function_body_tasks(S_received,pfunction_set) /\\ S_received.TODO = '
 '$statement_tasks(statement_set*,(PORIGIN n_source pfunction_set_source.BODY),0) ++ '
 '[$function_fallthrough(S_received,pfunction_set)] /\\ $tpp_guard(S_received)',
 'S_cross_found = $tpp_seek(S_received,1,1000)',
 'S_cross_found.COMPLETION = NORMAL \\/ S_cross_found.COMPLETION = BUDGET',
 'S_cross = S_cross_found[.COMPLETION = NORMAL]',
 '$tpp_stage(S_cross,1)',
 'S_cross.CURRENT = S_entered.CURRENT /\\ S_cross.FRAMES = S_entered.FRAMES /\\ S_cross.OBJECTPROPS = '
 'S.OBJECTPROPS',
 '$property_set_function(S_cross,ppropertyhook_set) = (pfunction_set) /\\ '
 '$property_set_context_valid(S_cross,pcallcontext_set) /\\ '
 '$property_set_entered(S_cross,S_cross.CURRENT,S_cross.FRAMES,ppropertyhook_set)',
 '$lookup(S_cross.ENV,$ptascii("value")) = (n_value_cell)',
 'S_cross.STORE[n_value_cell] = DEFINED (PINT 20)',
 '~$property_hook_backing(S_cross,n_grand,ppropertydesc) /\\ $property_set_backing(S_cross,n_grand,ppropertydesc) '
 '/\\ ~$property_hook_read_needed(S_cross,n_grand,$ptascii("value")) /\\ '
 '~$property_set_needed(S_cross,n_grand,$ptascii("value"))',
 '$default_parameter_line(S_cross,porigin_set,0) = 9',
 'S_cross.TODO = (PROPERTY_PREP phpType20_read 10) :: (DIM_FETCH 10) :: ptask_read*',
 'S_cross.RESULT = KNOWN (POBJECT n_grand)',
 'PhpStep: S_cross ~> S_prepared_raw',
 'S_prepared = $tpp_after(S_cross,S_prepared_raw)',
 'S_prepared.COMPLETION = NORMAL /\\ S_prepared.BASE = BASE_PROPERTY (POBJECT n_grand) ppropertydesc.KEY /\\ '
 'S_prepared.CURRENT = S_cross.CURRENT /\\ S_prepared.FRAMES = S_cross.FRAMES /\\ S_prepared.EVENTS = '
 'S_cross.EVENTS /\\ S_prepared.OBJECTPROPS = S_cross.OBJECTPROPS',
 'S_prepared.TODO = (DIM_FETCH 10) :: ptask_read*',
 '$tpp_guard(S_prepared)',
 'PhpStep: S_prepared ~> S_read_raw',
 'S_read = $tpp_after(S_prepared,S_read_raw)',
 'S_read.COMPLETION = NORMAL /\\ S_read.RESULT = KNOWN (PINT 10) /\\ S_read.CURRENT = S_cross.CURRENT /\\ '
 'S_read.FRAMES = S_cross.FRAMES /\\ S_read.EVENTS = S_cross.EVENTS /\\ S_read.OBJECTPROPS = S_cross.OBJECTPROPS '
 '/\\ S_read.TODO = ptask_read*',
 '$tpp_guard(S_read)',
 'S_write_found = $tpp_seek(S_read,2,1000)',
 'S_write_found.COMPLETION = NORMAL \\/ S_write_found.COMPLETION = BUDGET',
 'S_write = S_write_found[.COMPLETION = NORMAL]',
 '$tpp_stage(S_write,2)',
 'S_write.CURRENT = S_cross.CURRENT /\\ S_write.FRAMES = S_cross.FRAMES /\\ S_write.OBJECTPROPS = '
 'S_cross.OBJECTPROPS /\\ $property_set_backing(S_write,n_grand,ppropertydesc) /\\ '
 '~$property_set_pending(S_write)',
 'S_write.TODO = (ASSIGN_ARRAY pbase_write 11 false) :: ptask_write*',
 'S_write.RESULT = KNOWN (PINT 33) /\\ $tpp_guard(S_write)',
 'PhpStep: S_write ~> S_written_raw',
 'S_written = $tpp_after(S_write,S_written_raw)',
 'S_written.COMPLETION = NORMAL /\\ S_written.RESULT = KNOWN (PINT 33) /\\ S_written.CURRENT = S_cross.CURRENT '
 '/\\ S_written.FRAMES = S_cross.FRAMES /\\ S_written.EVENTS = S_write.EVENTS',
 '$objectprops_at(S_written.OBJECTPROPS,n_grand) = ([{DECL (porigin_property), NAME ppropertydesc.KEY, STATE '
 'PROP_VALUE (DIRECT (PINT 33))}])',
 '$tpp_guard(S_written)',
 'S_return_found = $tpp_seek(S_written,3,1000)',
 'S_return_found.COMPLETION = NORMAL \\/ S_return_found.COMPLETION = BUDGET',
 'S_return = S_return_found[.COMPLETION = NORMAL]',
 '$tpp_stage(S_return,3)',
 'S_return.TODO = (PROPERTY_SET_RESULT ppropertyhook_set (PINT 20)) :: ptask_return*',
 'S_return.RESULT = KNOWN PNULL /\\ S_return.CURRENT = eps /\\ S_return.FRAMES = eps /\\ S_return.ORIGIN = '
 '(ppropertyhook_set.SITE)',
 '$objectprops_at(S_return.OBJECTPROPS,n_grand) = ([{DECL (porigin_property), NAME ppropertydesc.KEY, STATE '
 'PROP_VALUE (DIRECT (PINT 33))}])',
 '$property_set_valid(S_return,ppropertyhook_set) /\\ $call_task_valid(S_return,PROPERTY_SET_RESULT '
 'ppropertyhook_set (PINT 20)) /\\ $property_set_needed(S_return,n_grand,$ptascii("value")) /\\ '
 '~$property_set_backing(S_return,n_grand,ppropertydesc)',
 '$tpp_guard(S_return)',
 'PhpStep: S_return ~> S_result_raw',
 'S_result = $tpp_after(S_return,S_result_raw)',
 'S_result.COMPLETION = NORMAL /\\ S_result.RESULT = KNOWN (PINT 20) /\\ S_result.BASE = BASE_VALUE (KNOWN PNULL) '
 '/\\ S_result.TODO = ptask_return* /\\ S_result.OBJECTPROPS = S_return.OBJECTPROPS',
 '$tpp_guard(S_result)',
 'S_get_found = $tpp_seek(S_result,5,1000)',
 'S_get_found.COMPLETION = NORMAL \\/ S_get_found.COMPLETION = BUDGET',
 'S_get = S_get_found[.COMPLETION = NORMAL]',
 '$tpp_stage(S_get,5)',
 'S_get.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_get_after) :: ptask_get*',
 'ppropertyhook_get_after.OBJECT = n_grand /\\ ppropertyhook_get_after.PROPERTY = porigin_property /\\ '
 'ppropertyhook_get_after.HOOK = porigin_get /\\ ppropertyhook_get_after.LINE = 27',
 'S_get.RESULT = KNOWN (PINT 46) /\\ S_get.CURRENT = eps /\\ S_get.FRAMES = eps',
 '$objectprops_at(S_get.OBJECTPROPS,n_grand) = ([{DECL (porigin_property), NAME ppropertydesc.KEY, STATE '
 'PROP_VALUE (DIRECT (PINT 33))}])',
 '$property_hook_function(S_get,ppropertyhook_get_after) = (pfunction_get) /\\ '
 '$call_task_valid(S_get,PROPERTY_HOOK_RESULT ppropertyhook_get_after) /\\ $tpp_guard(S_get)',
 'PhpStep: S_get ~> S_got_raw',
 'S_got = $tpp_after(S_get,S_got_raw)',
 'S_got.COMPLETION = NORMAL /\\ S_got.RESULT = KNOWN (PINT 46) /\\ S_got.BASE = BASE_VALUE (KNOWN (PINT 46)) /\\ '
 'S_got.TODO = ptask_get* /\\ S_got.OBJECTPROPS = S_get.OBJECTPROPS',
 '$tpp_guard(S_got)']

DERIVED = ['S_missing_set = S[.FUNCTIONS = [pfunction_get_source]]',
 '$property_hook_pair_declared(S_missing_set,ppropertydesc) /\\ '
 '$property_hook_pair_origins(S_missing_set,ppropertydesc_source) = porigin_get_source :: porigin_set_source :: '
 'eps',
 '$property_hook_trait_origin(S_missing_set,ppropertydesc) = (porigin_get) /\\ '
 '$property_set_trait_origin(S_missing_set,ppropertydesc) = (porigin_set)',
 '$property_hook_read_needed(S_missing_set,n_grand,$ptascii("value")) /\\ $property_hook_pending(S_missing_set)',
 '$property_hook_pair_raw_functions(S_missing_set,ppropertydesc_source) = eps /\\ '
 '$property_hook_trait_pair_functions(S_missing_set,ppropertydesc) = eps /\\ '
 '$property_hook_trait_property_functions(S_missing_set,[ppropertydesc]) = eps',
 '$property_hook_trait_function(S_missing_set,ppropertydesc) = eps /\\ '
 '$function_at($all_functions(S_missing_set),porigin_get) = eps /\\ '
 '$function_at($all_functions(S_missing_set),porigin_set) = eps',
 '$property_hook_function(S_missing_set,ppropertyhook_get) = eps /\\ $property_hook_plan(S_missing_set) = eps /\\ '
 '~$property_hook_trait_import_supported(S_missing_set,pclassdesc_consumer,ppropertydesc_source)',
 '$property_hook_pair_raw_functions(S[.FUNCTIONS = [pfunction_get_source,pfunction_set_source[.NAME = '
 '$ptascii("wrong")]]],ppropertydesc_source) = eps',
 '$property_hook_pair_raw_functions(S[.FUNCTIONS = [pfunction_get_source,pfunction_set_source[.SIGNATURE = '
 'pfunction_set_source.SIGNATURE[.PARAMETERS = eps]]]],ppropertydesc_source) = eps',
 '$property_hook_pair_raw_functions(S[.FUNCTIONS = [pfunction_get_source[.BODY = '
 'eps],pfunction_set_source]],ppropertydesc_source) = eps',
 '$property_hook_pair_raw_functions(S[.FUNCTIONS = [pfunction_get_source,pfunction_set_source[.EARLY = '
 'true]]],ppropertydesc_source) = eps',
 '$property_hook_pair_raw_functions(S[.FUNCTIONS = [pfunction_get_source[.SIGNATURE = '
 'pfunction_get_source.SIGNATURE[.BYREF = true]],pfunction_set_source]],ppropertydesc_source) = eps',
 '$source_unit(S.SOURCES,n_source) = (pcunit_source)',
 'S.SOURCES = [pcunit_source]',
 'phpType38_set_ref = NPropertyHook phpType14_set phpType24_set (BOOLEAN true) phpType11_set phpType16_set '
 '(SEQUENCE statement_set*) metadata_set',
 'pcnode_group_ref = NStmtProperty (SEQUENCE eps) (INTEGER flags) phpType18_group phpType56_group (SEQUENCE '
 '([phpType38_get,phpType38_set_ref])) metadata_group',
 'S_ref = S[.SOURCES = ([pcunit_source[.OCCURRENCES = '
 '$tpp_replace($tpp_replace(pcunit_source.OCCURRENCES,pcpath_group,pcnode_group_ref),pcpath_set,phpType38_set_ref)]])]',
 '$property_hook_pair_declared(S_ref,ppropertydesc_source) /\\ '
 '$property_hook_pair_origins(S_ref,ppropertydesc_source) = eps /\\ '
 '~$property_hook_trait_import_supported(S_ref,pclassdesc_consumer,ppropertydesc_source) /\\ '
 '$property_hook_trait_pair_functions(S_ref,ppropertydesc) = eps',
 'S_leaf = S[.SOURCES = ([pcunit_source[.OCCURRENCES = '
 '$tpp_replace(pcunit_source.OCCURRENCES,pcpath_set,phpType38_get)]])]',
 '$property_hook_pair_declared(S_leaf,ppropertydesc_source) /\\ '
 '$property_hook_pair_raw_functions(S_leaf,ppropertydesc_source) = eps /\\ '
 '$property_hook_trait_pair_functions(S_leaf,ppropertydesc) = eps',
 'S_no_frames = S_cross[.FRAMES = eps]',
 '~$property_set_backing(S_no_frames,n_grand,ppropertydesc) /\\ '
 '$property_set_needed(S_no_frames,n_grand,$ptascii("value"))',
 '~$property_set_backing(S_cross[.CURRENT = (pcallcontext_get[.RECEIVER = eps])],n_grand,ppropertydesc)',
 '~$property_set_backing(S_cross[.CURRENT = (pcallcontext_get[.FUNCTION = '
 'porigin_get_source])],n_grand,ppropertydesc)',
 'S_raw_row = S[.CLASSES = $tpp_class_replace(S.CLASSES,porigin_consumer,pclassdesc_consumer[.PROPERTIES = '
 '([ppropertydesc_source])])]',
 '$property_effective_desc(S_raw_row,n_grand,$ptascii("value")) = (ppropertydesc_source) /\\ '
 '$property_hook_origin(S_raw_row,ppropertydesc_source) = (porigin_get_source)',
 '$property_hook_function(S_raw_row,ppropertyhook_get[.PROPERTY = porigin_property_source][.HOOK = '
 'porigin_get_source]) = eps',
 '$property_set_trait_source(S,pclassdesc_consumer[.PARENT = (pclassdesc_grand.NAME)],ppropertydesc_source) = eps '
 '/\\ ~$property_hook_trait_import_supported(S,pclassdesc_consumer[.PARENT = '
 '(pclassdesc_grand.NAME)],ppropertydesc_source)',
 'ppropertydesc_wrong_type = ppropertydesc_source[.TYPE = [PTBRANCH ([PTBUILTIN "string"])]]',
 'S_type = S[.CLASSES = $tpp_class_replace(S.CLASSES,porigin_trait,pclassdesc_trait[.PROPERTIES = '
 '([ppropertydesc_wrong_type])])][.FUNCTIONS = [pfunction_get_source[.SIGNATURE = '
 'pfunction_get_source.SIGNATURE[.RETURNS = ppropertydesc_wrong_type.TYPE]],pfunction_set_source[.SIGNATURE = '
 '$property_set_signature(ppropertydesc_wrong_type)]]]',
 '$property_hook_pair_origins(S_type,ppropertydesc_wrong_type) = porigin_get_source :: porigin_set_source :: eps '
 '/\\ $property_hook_pair_raw_functions(S_type,ppropertydesc_wrong_type) = eps',
 'porigin_consumer = PORIGIN n_source pcpath_consumer',
 '$origin_node(S.SOURCES,porigin_consumer) = (NStmtClass phpType14_consumer phpType24_consumer phpType3_consumer '
 'ABSENT phpType42_consumer (SEQUENCE statement_consumer_body*) metadata_consumer)',
 'S_outer = S[.CLASSES = $tpp_class_replace(S.CLASSES,porigin_consumer,pclassdesc_consumer[.KIND = '
 '"trait"])][.SOURCES = ([pcunit_source[.OCCURRENCES = '
 '$tpp_replace(pcunit_source.OCCURRENCES,pcpath_consumer,NStmtTrait phpType14_consumer phpType3_consumer '
 '(SEQUENCE statement_consumer_body*) metadata_consumer)]])]',
 '$code_at(S.CODE,n_source) = (pcode_source)',
 'S.CODE = [pcode_source]',
 'S_outer_resolved = S_outer[.CODE = ([pcode_source[.NAMES = pcode_source.NAMES ++ [(CODENAME (pcpath_consumer ++ '
 '[PCFIELD 2,PCINDEX 0,PCFIELD 0,PCINDEX 0]) pclassdesc_trait.NAME eps)]]])]',
 '$trait_plan(S_outer_resolved,pclassdesc_consumer[.KIND = "trait"]).TRAITS = [pclassdesc_trait.NAME]',
 '$property_hook_trait_export(S_outer_resolved,pclassdesc_consumer[.KIND = "trait"],ppropertydesc_source) = '
 '(ppropertydesc_source)',
 '$property_hook_pair_origins(S_outer_resolved,ppropertydesc_source) = porigin_get_source :: porigin_set_source '
 ':: eps /\\ ~$property_hook_trait_import_supported(S_outer_resolved,pclassdesc_consumer[.KIND = '
 '"trait"],ppropertydesc_source)']

SET_DERIVED = ['S_missing_get = S[.FUNCTIONS = [pfunction_set_source]]',
 '$property_hook_pair_declared(S_missing_get,ppropertydesc) /\\ '
 '$property_hook_pair_origins(S_missing_get,ppropertydesc_source) = porigin_get_source :: porigin_set_source :: '
 'eps',
 '$property_hook_trait_origin(S_missing_get,ppropertydesc) = (porigin_get) /\\ '
 '$property_set_trait_origin(S_missing_get,ppropertydesc) = (porigin_set)',
 '$property_set_needed(S_missing_get,n_grand,$ptascii("value")) /\\ $property_set_pending(S_missing_get)',
 '$property_hook_pair_raw_functions(S_missing_get,ppropertydesc_source) = eps /\\ '
 '$property_hook_trait_pair_functions(S_missing_get,ppropertydesc) = eps /\\ '
 '$property_hook_trait_property_functions(S_missing_get,[ppropertydesc]) = eps',
 '$property_hook_trait_function(S_missing_get,ppropertydesc) = eps /\\ '
 '$function_at($all_functions(S_missing_get),porigin_get) = eps /\\ '
 '$function_at($all_functions(S_missing_get),porigin_set) = eps',
 '$property_set_function(S_missing_get,ppropertyhook_set) = eps /\\ $property_set_plan(S_missing_get) = eps',
 '~$property_set_backing(S_cross[.FRAMES = eps],n_grand,ppropertydesc) /\\ '
 '$property_hook_read_needed(S_cross[.FRAMES = eps],n_grand,$ptascii("value"))',
 '~$property_set_backing(S_cross[.CURRENT = (pcallcontext_set[.RECEIVER = eps])],n_grand,ppropertydesc) /\\ '
 '$property_hook_read_needed(S_cross[.CURRENT = (pcallcontext_set[.RECEIVER = eps])],n_grand,$ptascii("value"))',
 '~$property_set_backing(S_cross[.CURRENT = (pcallcontext_set[.FUNCTION = '
 'porigin_set_source])],n_grand,ppropertydesc) /\\ $property_hook_read_needed(S_cross[.CURRENT = '
 '(pcallcontext_set[.FUNCTION = porigin_set_source])],n_grand,$ptascii("value"))',
 'S_raw_row = S[.CLASSES = $tpp_class_replace(S.CLASSES,porigin_consumer,pclassdesc_consumer[.PROPERTIES = '
 '([ppropertydesc_source])])]',
 '$property_effective_desc(S_raw_row,n_grand,$ptascii("value")) = (ppropertydesc_source) /\\ '
 '$property_set_origin(S_raw_row,ppropertydesc_source) = (porigin_set_source)',
 '$property_set_function(S_raw_row,ppropertyhook_set[.PROPERTY = porigin_property_source][.HOOK = '
 'porigin_set_source]) = eps']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--group', choices=['get', 'set'], required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'trait_imported_paired_hooks_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    clauses, negatives, case_index, start_stage = {
        'get': (GET, DERIVED, 0, 0),
        'set': (SET, SET_DERIVED, 0, 7),
    }[args.group]
    selections = [(args.group, clauses, negatives)]
    cases = [data['cases'][case_index]]
    sources = [HERE / 'trait-imported-paired-hooks.php']
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
    out = Path(tempfile.mkdtemp(prefix='trait-imported-paired-hooks-protocol-', dir=ROOT / '.tools'))
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
                     'S_found = $tpp_seek(S_initial,' + str(start_stage) + ',1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            content += '\ndec $tpp_' + name + '() : bool\ndef $tpp_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $tpp_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = (' + ' /\\ '.join('$tpp_' + name + '()' for name, _, _ in selections) + ')\n'
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
