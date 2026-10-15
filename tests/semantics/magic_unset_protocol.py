"""Check inherited magic unset selection, callback and receiver cleanup."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()

PREFIX = ('\n'
 'dec $mu_replace(pcoccurrence*,pcpath,pcnode) : pcoccurrence*\n'
 'def $mu_replace(eps,pcpath,pcnode) = eps\n'
 'def $mu_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath pcnode) :: '
 'pcoccurrence*\n'
 'def $mu_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath_other '
 'pcnode_old) :: $mu_replace(pcoccurrence*,pcpath,pcnode)\n'
 '  -- if pcpath_other =/= pcpath\n'
 'dec $mu_class_replace(pclassdesc*,porigin,pclassdesc) : pclassdesc*\n'
 'def $mu_class_replace(eps,porigin,pclassdesc) = eps\n'
 'def $mu_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_new :: pclassdesc*\n'
 '  -- if pclassdesc_old.ORIGIN = porigin\n'
 'def $mu_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_old :: '
 '$mu_class_replace(pclassdesc*,porigin,pclassdesc_new)\n'
 '  -- if pclassdesc_old.ORIGIN =/= porigin\n'
 'dec $mu_method_replace(pmethoddesc*,porigin,pmethoddesc) : pmethoddesc*\n'
 'def $mu_method_replace(eps,porigin,pmethoddesc) = eps\n'
 'def $mu_method_replace(pmethoddesc_old :: pmethoddesc*,porigin,pmethoddesc_new) = pmethoddesc_new :: pmethoddesc*\n'
 '  -- if pmethoddesc_old.FUNCTION.ORIGIN = porigin\n'
 'def $mu_method_replace(pmethoddesc_old :: pmethoddesc*,porigin,pmethoddesc_new) = pmethoddesc_old :: '
 '$mu_method_replace(pmethoddesc*,porigin,pmethoddesc_new)\n'
 '  -- if pmethoddesc_old.FUNCTION.ORIGIN =/= porigin\n'
 'dec $mu_stage(pstate,nat) : bool\n'
 'def $mu_stage(S,0) = true\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = UNSET_ARRAY :: ptask*\n'
 '  -- if $property_current_line(S) = 18\n'
 'def $mu_stage(S,1) = true\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = UNSET_ARRAY :: ptask*\n'
 '  -- if $property_current_line(S) = 21\n'
 'def $mu_stage(S,2) = true\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_UNSET_TARGET ppropertyunset\n'
 '  -- if S.TODO = UNSET_ARRAY :: ptask*\n'
 '  -- if $property_current_line(S) = 7\n'
 'def $mu_stage(S,3) = true\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (PROPERTY_UNSET_RESULT ppropertyunset) :: ptask*\n'
 'def $mu_stage(S,4) = true\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_UNSET_TARGET ppropertyunset\n'
 '  -- if S.TODO = (ASSIGN_ARRAY pbase 8 false) :: ptask*\n'
 '  -- if S.RESULT = KNOWN (PINT 13)\n'
 'def $mu_stage(S,5) = true\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (THROW_SEARCH n) :: (PROPERTY_UNSET_RESULT ppropertyunset) :: ptask*\n'
 'def $mu_stage(S,n) = false -- otherwise\n'
 'dec $mu_seek(pstate,nat,nat) : pstate\n'
 'def $mu_seek(S,n_stage,n) = S\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if $mu_stage(S,n_stage) \\/ n = 0\n'
 'def $mu_seek(S,n_stage,n) = $mu_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if ~$mu_stage(S,n_stage) /\\ $(n > 0)\n'
 'def $mu_seek(S,n_stage,n) = $mu_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
 '  -- if $throwable_pending(S.COMPLETION) /\\ $(n > 0)\n'
 'def $mu_seek(S,n_stage,n) = S -- otherwise\n'
 'dec $mu_after(pstate,pstate) : pstate\n'
 'def $mu_after(S,S_next) = '
 '$gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))\n'
 'dec $mu_guard(pstate) : bool\n'
 'def $mu_guard(S) = ($call_descriptors_valid(S) /\\ $declaration_history_valid(S) /\\ $property_state_valid(S) /\\ '
 '$heap_valid($heap_prune($heap_graph(S))))\n'
 'dec $mu_output(pevent*) : ptbytes\n'
 'def $mu_output(eps) = eps\n'
 'def $mu_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $mu_output(pevent*)\n')

BODY = ['$mu_stage(S,0)',
 '$lookup(S.ENV,$ptascii("child")) = (n_child_cell)',
 'S.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("MagicUnsetParent81"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("MagicUnsetChild81"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 'pclassdesc_parent.KIND = "class" /\\ pclassdesc_parent.PARENT = eps /\\ ~pclassdesc_parent.READONLY',
 '$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_parent)',
 'S.OBJECTS[n_child] = INSTANCE porigin_child',
 'ppropertydesc_hidden = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc_seen = pclassdesc_parent.PROPERTIES[1]',
 'porigin_hidden = ppropertydesc_hidden.ORIGIN',
 'porigin_seen = ppropertydesc_seen.ORIGIN',
 'ppropertydesc_hidden.NAME = $ptascii("hidden") /\\ ppropertydesc_hidden.KEY = [0] ++ $ptascii("MagicUnsetParent81") '
 '++ [0] ++ $ptascii("hidden") /\\ ppropertydesc_hidden.VISIBILITY = PROPERTY_PRIVATE',
 'ppropertydesc_seen.NAME = $ptascii("seen") /\\ ppropertydesc_seen.KEY = $ptascii("seen") /\\ '
 'ppropertydesc_seen.VISIBILITY = PROPERTY_PUBLIC',
 '$objectprops_at(S.OBJECTPROPS,n_child) = (ppropertyslot_initial*)',
 '$property_slot_at(ppropertyslot_initial*,ppropertydesc_hidden.KEY) = (ppropertyslot_hidden)',
 'ppropertyslot_hidden.STATE = PROP_VALUE (DIRECT (PINT 10))',
 '$property_slot_at(ppropertyslot_initial*,ppropertydesc_seen.KEY) = (ppropertyslot_seen)',
 'ppropertyslot_seen.STATE = PROP_VALUE (DIRECT (PINT 0))',
 'S.TODO = UNSET_ARRAY :: ptask_public_tail*',
 'S.BASE = BASE_PROPERTY_PENDING pbase_public (KNOWN (PSTRING ($ptascii("seen")))) z_public',
 '$property_unset_pending_receiver(S,pbase_public) = (n_child)',
 '$property_resolve(S,n_child,$ptascii("seen")) = PROPERTY_ACCESS ($ptascii("seen"))',
 '~$property_unset_needed(S,n_child,$ptascii("seen")) /\\ ~$property_unset_pending(S) /\\ $property_unset_plan(S) = '
 'eps',
 '$mu_guard(S)',
 'PhpStep: S ~> S_public_raw',
 'S_public = $mu_after(S,S_public_raw)',
 'S_public.TODO = ptask_public_tail* /\\ S_public.CURRENT = eps /\\ S_public.FRAMES = eps /\\ S_public.EVENTS = '
 'S.EVENTS',
 '$objectprops_at(S_public.OBJECTPROPS,n_child) = (ppropertyslot_public*)',
 '$property_slot_at(ppropertyslot_public*,ppropertydesc_seen.KEY) = (ppropertyslot_seen_unset)',
 'ppropertyslot_seen_unset.STATE = PROP_UNSET',
 '$property_slot_at(ppropertyslot_public*,ppropertydesc_hidden.KEY) = (ppropertyslot_hidden)',
 'S_private_found = $mu_seek(S_public,1,1000)',
 'S_private_found.COMPLETION = NORMAL \\/ S_private_found.COMPLETION = BUDGET',
 'S_private = S_private_found[.COMPLETION = NORMAL]',
 '$mu_stage(S_private,1)',
 '$mu_output(S_private.EVENTS) = $ptascii("I:10/0|P:ONLY|")',
 'S_private.TODO = UNSET_ARRAY :: ptask_private_tail*',
 'S_private.BASE = BASE_PROPERTY_PENDING pbase_private poperand_private z_private',
 'S_private.ORIGIN = (porigin_site)',
 '$origin_node(S_private.SOURCES,porigin_site) = (expression_site)',
 'expression_site = NExprPropertyFetch (NExprVariable (BYTES text_child) metadata_child) (NIdentifier (BYTES '
 'text_hidden) metadata_hidden) metadata_site',
 '$base64(text_child) = $ptascii("child") /\\ $base64(text_hidden) = $ptascii("hidden")',
 '$property_pending_source_base(S_private,S_private.BASE,expression_site)',
 '$property_unset_pending_receiver(S_private,pbase_private) = (n_child)',
 'S_resolution = $property_pending_resolve(S_private,pbase_private,poperand_private,PPUNSET,z_private,21)',
 'S_resolution.COMPLETION = NORMAL /\\ S_resolution.BASE = BASE_PROPERTY (POBJECT n_child) ($ptascii("hidden"))',
 '$location_slot(S_resolution,ROOT n_child_cell) = DEFINED (POBJECT n_child)',
 '$property_resolve(S_private,n_child,$ptascii("hidden")) = PROPERTY_ACCESS ($ptascii("hidden"))',
 '$property_declaring_class(S_private.CLASSES,porigin_hidden) = (porigin_parent)',
 '$property_unset_needed(S_private,n_child,$ptascii("hidden")) /\\ $property_unset_pending(S_private)',
 '$property_unset_plan(S_private) = (ppropertyunset)',
 'ppropertyunset.SITE = porigin_site /\\ ppropertyunset.OBJECT = n_child /\\ ppropertyunset.CLASS = porigin_child /\\ '
 'ppropertyunset.PROPERTY = porigin_hidden /\\ ppropertyunset.NAME = $ptascii("hidden") /\\ ppropertyunset.LINE = 21',
 '$property_unset_method(S_private,n_child) = (pmethoddesc_unset)',
 'pmethoddesc_unset.FUNCTION = pfunction_unset',
 'porigin_method = pfunction_unset.ORIGIN',
 'ppropertyunset.METHOD = porigin_method /\\ pmethoddesc_unset.OWNER = porigin_parent /\\ pmethoddesc_unset.VISIBILITY '
 '= PROPERTY_PUBLIC /\\ ~pmethoddesc_unset.STATIC',
 '$method_origin(pclassdesc_parent.METHODS,porigin_method) = (pmethoddesc_unset)',
 'porigin_parent = PORIGIN n_source pcpath_parent',
 'porigin_method = PORIGIN n_source pcpath_method',
 'pcpath_method = pcpath_parent ++ [PCFIELD 5,PCINDEX 2]',
 'pfunction_unset.NAME = $ptascii("MagicUnsetParent81::__unset") /\\ pfunction_unset.LINE = 5 /\\ '
 'pfunction_unset.ENDLINE = 9',
 'pfunction_unset.BODY = pcpath_method ++ [PCFIELD 6] /\\ pfunction_unset.DEFAULTS = eps',
 'pfunction_unset.SIGNATURE.PARAMETERS = [psparam_name]',
 'psparam_name.NAME = $ptascii("name") /\\ psparam_name.TYPE = [PTBRANCH ([PTBUILTIN "string"])] /\\ '
 '~psparam_name.BYREF /\\ ~psparam_name.VARIADIC /\\ psparam_name.REQUIRED /\\ psparam_name.DEFAULT = PSNONE',
 '$ppmethod_unset_signature(pfunction_unset.SIGNATURE)',
 '$property_unset_function(S_private,ppropertyunset) = (pfunction_unset)',
 '$property_unset_source(S_private,ppropertyunset) /\\ $property_unset_valid(S_private,ppropertyunset) /\\ '
 '$property_unset_capture(S_private,ppropertyunset)',
 '~$property_unset_guard(S_private,S_private.CURRENT,S_private.FRAMES,n_child,$ptascii("hidden"))',
 '$source_unit(S_private.SOURCES,n_source) = (pcunit_source)',
 'S_private.SOURCES = [pcunit_source]',
 '$origin_node(S_private.SOURCES,porigin_method) = (statement_method)',
 'statement_method = NStmtClassMethod phpType14_method phpType24_method phpType4_method phpType11_method '
 'phpType16_method phpType18_method (SEQUENCE statement_body*) metadata_method',
 'phpType16_method = SEQUENCE ([phpType17_parameter])',
 'phpType17_parameter = NParam phpType14_parameter phpType24_parameter phpType18_parameter phpType4_byref '
 'phpType4_variadic phpType10_parameter phpType5_default phpType37_hooks metadata_parameter',
 'phpType18_parameter = NIdentifier (BYTES text_parameter_type) metadata_parameter_type',
 '$origin_node(S_private.SOURCES,PORIGIN n_source (pcpath_method ++ [PCFIELD 4,PCINDEX 0])) = (phpType17_parameter)',
 '$property_unset_body_source(S_private.SOURCES,n_source,pfunction_unset.BODY,statement_body*,0)',
 '$mu_guard(S_private)',
 'PhpStep: S_private ~> S_call_raw',
 'S_call = $mu_after(S_private,S_call_raw)',
 'S_call.TODO = (CALL_ARGS (PROPERTY_UNSET_TARGET ppropertyunset) eps 1 ([KNOWN (PSTRING ($ptascii("hidden")))]) '
 '(porigin_site) 21) :: (PROPERTY_UNSET_RESULT ppropertyunset) :: ptask_private_tail*',
 'S_call.BASE = BASE_VALUE (KNOWN PNULL) /\\ S_call.RESULT = KNOWN PNULL /\\ S_call.HELD = S_private.HELD /\\ '
 'S_call.CURRENT = eps /\\ S_call.FRAMES = eps /\\ S_call.EVENTS = S_private.EVENTS',
 '$task_nodes(PROPERTY_UNSET_RESULT ppropertyunset) = [HOBJECT n_child] /\\ $target_nodes(PROPERTY_UNSET_TARGET '
 'ppropertyunset) = eps',
 '$property_unset_pending_call(S_call,ppropertyunset) /\\ $call_task_valid(S_call,CALL_ARGS (PROPERTY_UNSET_TARGET '
 'ppropertyunset) eps 1 ([KNOWN (PSTRING ($ptascii("hidden")))]) (porigin_site) 21) /\\ $mu_guard(S_call)',
 'PhpStep: S_call ~> S_entered_raw',
 'S_entered = $mu_after(S_call,S_entered_raw)',
 'S_entered.CURRENT = (pcallcontext_unset)',
 'pcallcontext_unset.TARGET = PROPERTY_UNSET_TARGET ppropertyunset /\\ pcallcontext_unset.FUNCTION = porigin_method '
 '/\\ pcallcontext_unset.RECEIVER = (n_child) /\\ pcallcontext_unset.LEXICAL_CLASS = (porigin_parent) /\\ '
 'pcallcontext_unset.CALLED_CLASS = (porigin_child)',
 'pcallcontext_unset.CALLSITE = (porigin_site) /\\ pcallcontext_unset.LINE = 21 /\\ pcallcontext_unset.ARGC = 1 /\\ '
 'pcallcontext_unset.EXTRA = eps /\\ pcallcontext_unset.NAMED = eps',
 'S_entered.FRAMES = [pframe_unset]',
 'pframe_unset.CONTEXT = eps /\\ pframe_unset.ORIGIN = (porigin_site) /\\ pframe_unset.TODO = (PROPERTY_UNSET_RESULT '
 'ppropertyunset) :: ptask_private_tail*',
 'S_entered.TODO = [TYPE_RECEIVE porigin_method 0] /\\ S_entered.ORIGIN = (porigin_method)',
 '$lookup(S_entered.ENV,$ptascii("name")) = (n_name_cell)',
 'S_entered.STORE[n_name_cell] = DEFINED (PSTRING ($ptascii("hidden")))',
 '$typed_receive_valid(S_entered,porigin_method,0) /\\ $default_parameter_line(S_entered,porigin_method,0) = 5',
 '$property_unset_context(S_entered,pcallcontext_unset) /\\ '
 '$property_unset_frame(S_entered,pcallcontext_unset,pframe_unset,ppropertyunset)',
 '$property_unset_guard(S_entered,S_entered.CURRENT,S_entered.FRAMES,n_child,$ptascii("hidden"))',
 '$call_receiver_roots(pcallcontext_unset) = eps /\\ $mu_guard(S_entered)',
 'PhpStep: S_entered ~> S_received_raw',
 'S_received = $mu_after(S_entered,S_received_raw)',
 'S_received.TODO = $function_body_tasks(S_received,pfunction_unset) /\\ S_received.CURRENT = S_entered.CURRENT /\\ '
 'S_received.FRAMES = S_entered.FRAMES /\\ S_received.EVENTS = S_entered.EVENTS',
 'S_inner_found = $mu_seek(S_received,2,1000)',
 'S_inner_found.COMPLETION = NORMAL \\/ S_inner_found.COMPLETION = BUDGET',
 'S_inner = S_inner_found[.COMPLETION = NORMAL]',
 '$mu_stage(S_inner,2)',
 'S_inner.CURRENT = S_entered.CURRENT /\\ S_inner.FRAMES = S_entered.FRAMES',
 'S_inner.TODO = UNSET_ARRAY :: ptask_inner_tail*',
 'S_inner.BASE = BASE_PROPERTY_PENDING (BASE_VALUE (KNOWN (POBJECT n_child))) (KNOWN (PSTRING ($ptascii("hidden")))) '
 'z_inner',
 '$property_resolve(S_inner,n_child,$ptascii("hidden")) = PROPERTY_ACCESS ppropertydesc_hidden.KEY',
 '~$property_unset_needed(S_inner,n_child,$ptascii("hidden")) /\\ ~$property_unset_pending(S_inner)',
 '$mu_output(S_inner.EVENTS) = '
 '$ptascii("I:10/0|P:ONLY|U:hidden/MagicUnsetParent81/MagicUnsetChild81/MagicUnsetParent81::__unset|")',
 'PhpStep: S_inner ~> S_inner_raw',
 'S_inner_done = $mu_after(S_inner,S_inner_raw)',
 'S_inner_done.TODO = ptask_inner_tail* /\\ S_inner_done.CURRENT = S_inner.CURRENT /\\ S_inner_done.FRAMES = '
 'S_inner.FRAMES /\\ S_inner_done.EVENTS = S_inner.EVENTS',
 '$objectprops_at(S_inner_done.OBJECTPROPS,n_child) = (ppropertyslot_inner*)',
 '$property_slot_at(ppropertyslot_inner*,ppropertydesc_hidden.KEY) = (ppropertyslot_hidden_unset)',
 'ppropertyslot_hidden_unset.STATE = PROP_UNSET',
 'S_store_found = $mu_seek(S_inner_done,4,1000)',
 'S_store_found.COMPLETION = NORMAL \\/ S_store_found.COMPLETION = BUDGET',
 'S_store = S_store_found[.COMPLETION = NORMAL]',
 '$mu_stage(S_store,4)',
 'S_store.CURRENT = S_entered.CURRENT /\\ S_store.FRAMES = S_entered.FRAMES /\\ S_store.RESULT = KNOWN (PINT 13)',
 '$method_selected_scope(S_store,n_child,$ptascii("offset"),(porigin_parent)) = (pmethoddesc_offset)',
 'pmethoddesc_offset.OWNER = porigin_parent /\\ pmethoddesc_offset.VISIBILITY = PROPERTY_PRIVATE',
 '$method_named(pclassdesc_child.METHODS,$ptascii("offset")) = (pmethoddesc_child_offset)',
 'pmethoddesc_child_offset.OWNER = porigin_child /\\ pmethoddesc_child_offset.FUNCTION.ORIGIN =/= '
 'pmethoddesc_offset.FUNCTION.ORIGIN',
 '~$property_set_needed(S_store,n_child,$ptascii("seen"))',
 'PhpStep: S_store ~> S_store_raw',
 'S_stored = $mu_after(S_store,S_store_raw)',
 '$objectprops_at(S_stored.OBJECTPROPS,n_child) = (ppropertyslot_stored*)',
 '$property_slot_at(ppropertyslot_stored*,ppropertydesc_seen.KEY) = (ppropertyslot_seen_final)',
 'ppropertyslot_seen_final.STATE = PROP_VALUE (DIRECT (PINT 13))',
 '$property_slot_at(ppropertyslot_stored*,ppropertydesc_hidden.KEY) = (ppropertyslot_hidden_unset)',
 'S_result_found = $mu_seek(S_stored,3,1000)',
 'S_result_found.COMPLETION = NORMAL \\/ S_result_found.COMPLETION = BUDGET',
 'S_result = S_result_found[.COMPLETION = NORMAL]',
 '$mu_stage(S_result,3)',
 'S_result.CURRENT = eps /\\ S_result.FRAMES = eps /\\ S_result.TODO = (PROPERTY_UNSET_RESULT ppropertyunset) :: '
 'ptask_private_tail*',
 'S_result.ORIGIN = (porigin_site) /\\ S_result.RESULT = KNOWN PNULL /\\ S_result.BASE = BASE_VALUE (KNOWN PNULL)',
 '$property_unset_valid(S_result,ppropertyunset) /\\ $property_unset_tail(S_result,ppropertyunset,S_result.TODO) /\\ '
 '$mu_guard(S_result)',
 '~$property_unset_guard(S_result,S_result.CURRENT,S_result.FRAMES,n_child,$ptascii("hidden"))',
 'n_result_owners = $heap_owners($heap_graph(S_result),HOBJECT n_child)',
 'PhpStep: S_result ~> S_result_raw',
 'S_done = $mu_after(S_result,S_result_raw)',
 'S_done.TODO = ptask_private_tail* /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.RESULT = KNOWN PNULL '
 '/\\ S_done.BASE = BASE_VALUE (KNOWN PNULL)',
 'n_result_owners = $($heap_owners($heap_graph(S_done),HOBJECT n_child) + 1)',
 '$mu_guard(S_done)',
 'S_final = $drive_steps(S_done,10000)',
 'S_final.COMPLETION = NORMAL /\\ S_final.TODO = eps /\\ S_final.CURRENT = eps /\\ S_final.FRAMES = eps',
 '$mu_output(S_final.EVENTS) = '
 '$ptascii("I:10/0|P:ONLY|U:hidden/MagicUnsetParent81/MagicUnsetChild81/MagicUnsetParent81::__unset|F:ONLY/13|")',
 '$lookup(S_final.ENV,$ptascii("raw")) = (n_raw_cell)',
 'S_final.STORE[n_raw_cell] = DEFINED (PARRAY n_raw)',
 'S_final.ARRAYS[n_raw].ITEMS = [ENTRY (KSTRING ($ptascii("seen"))) (DIRECT (PINT 13))]',
 '$objectprops_at(S_final.OBJECTPROPS,n_child) = (ppropertyslot_final*)',
 '$property_slot_at(ppropertyslot_final*,ppropertydesc_hidden.KEY) = (ppropertyslot_hidden_unset)',
 '$property_slot_at(ppropertyslot_final*,ppropertydesc_seen.KEY) = (ppropertyslot_seen_final)',
 '$mu_guard(S_final)']

DERIVED = ['S_unknown = S_private[.BASE = BASE_PROPERTY_PENDING (BASE_DIM pbase_private (KNOWN (PINT 0)) 21) poperand_private '
 'z_private]',
 '$property_unset_pending_receiver(S_unknown,BASE_DIM pbase_private (KNOWN (PINT 0)) 21) = eps /\\ '
 '$property_unset_present(S_unknown.CLASSES) /\\ $property_unset_pending(S_unknown) /\\ '
 '$property_unset_plan(S_unknown) = eps',
 'S_name = S_private[.BASE = BASE_PROPERTY_PENDING pbase_private (VARIABLE ($ptascii("dynamic")) 21) z_private]',
 '~$property_unset_known_name(VARIABLE ($ptascii("dynamic")) 21) /\\ $property_unset_pending(S_name) /\\ '
 '$property_unset_plan(S_name) = eps',
 'S_this_missing = S_inner_done[.TODO = UNSET_ARRAY :: ptask_inner_tail*][.BASE = S_inner.BASE][.ORIGIN = '
 'S_inner.ORIGIN]',
 '$property_unset_needed(S_this_missing,n_child,$ptascii("hidden")) /\\ $property_unset_pending(S_this_missing) /\\ '
 '$property_unset_plan(S_this_missing) = eps',
 'S_source_missing = S_private[.SOURCES = ([pcunit_source[.OCCURRENCES = '
 '$mu_replace(pcunit_source.OCCURRENCES,pcpath_method,NStmtNop metadata_method)]])]',
 '$property_unset_method(S_source_missing,n_child) = (pmethoddesc_unset) /\\ '
 '$property_unset_needed(S_source_missing,n_child,$ptascii("hidden")) /\\ $property_unset_pending(S_source_missing) '
 '/\\ $property_unset_function(S_source_missing,ppropertyunset) = eps /\\ $property_unset_plan(S_source_missing) = eps',
 'pmethoddesc_wrong_owner = pmethoddesc_unset[.OWNER = porigin_child]',
 'S_wrong_owner = S_private[.CLASSES = $mu_class_replace(S_private.CLASSES,porigin_parent,pclassdesc_parent[.METHODS = '
 '$mu_method_replace(pclassdesc_parent.METHODS,porigin_method,pmethoddesc_wrong_owner)])]',
 '$property_unset_method(S_wrong_owner,n_child) = (pmethoddesc_wrong_owner) /\\ '
 '$property_unset_function(S_wrong_owner,ppropertyunset) = eps /\\ $property_unset_plan(S_wrong_owner) = eps',
 'pmethoddesc_wrong_name = pmethoddesc_unset[.FUNCTION = pfunction_unset[.NAME = $ptascii("Forged::__unset")]]',
 'S_wrong_name = S_private[.CLASSES = $mu_class_replace(S_private.CLASSES,porigin_parent,pclassdesc_parent[.METHODS = '
 '$mu_method_replace(pclassdesc_parent.METHODS,porigin_method,pmethoddesc_wrong_name)])]',
 '$property_unset_pending(S_wrong_name) /\\ $property_unset_function(S_wrong_name,ppropertyunset) = eps /\\ '
 '$property_unset_plan(S_wrong_name) = eps',
 'phpType17_bad = NParam phpType14_parameter phpType24_parameter (NIdentifier (BYTES "aW50") metadata_parameter_type) '
 'phpType4_byref phpType4_variadic phpType10_parameter phpType5_default phpType37_hooks metadata_parameter',
 'S_wrong_param = S_private[.SOURCES = ([pcunit_source[.OCCURRENCES = '
 '$mu_replace(pcunit_source.OCCURRENCES,pcpath_method ++ [PCFIELD 4,PCINDEX 0],phpType17_bad)]])]',
 '$property_unset_pending(S_wrong_param) /\\ $property_unset_function(S_wrong_param,ppropertyunset) = eps /\\ '
 '$property_unset_plan(S_wrong_param) = eps',
 'S_wrong_body = S_private[.SOURCES = ([pcunit_source[.OCCURRENCES = '
 '$mu_replace(pcunit_source.OCCURRENCES,pfunction_unset.BODY ++ [PCINDEX 0],NStmtNop metadata_method)]])]',
 '~$property_unset_body_source(S_wrong_body.SOURCES,n_source,pfunction_unset.BODY,statement_body*,0) /\\ '
 '$property_unset_function(S_wrong_body,ppropertyunset) = eps /\\ $property_unset_plan(S_wrong_body) = eps',
 '~$property_unset_valid(S_private,ppropertyunset[.PROPERTY = porigin_seen])',
 '~$property_unset_access_valid(S_private[.OBJECTS[n_child] = INSTANCE '
 'porigin_parent],n_child,$ptascii("hidden"),ppropertydesc_hidden,PROPERTY_ACCESS ($ptascii("hidden")))',
 'S_no_result = S_call[.TODO = (CALL_ARGS (PROPERTY_UNSET_TARGET ppropertyunset) eps 1 ([KNOWN (PSTRING '
 '($ptascii("hidden")))]) (porigin_site) 21) :: ptask_private_tail*]',
 '$property_unset_function(S_no_result,ppropertyunset) = (pfunction_unset) /\\ '
 '~$property_unset_pending_call(S_no_result,ppropertyunset)',
 'S_wrong_arg = S_call[.TODO = (CALL_ARGS (PROPERTY_UNSET_TARGET ppropertyunset) eps 1 ([KNOWN (PSTRING '
 '($ptascii("seen")))]) (porigin_site) 21) :: (PROPERTY_UNSET_RESULT ppropertyunset) :: ptask_private_tail*]',
 '~$property_unset_pending_call(S_wrong_arg,ppropertyunset)',
 'S_direct = S_entered[.CURRENT = (pcallcontext_unset[.TARGET = METHOD_TARGET n_child porigin_method])]',
 '~$property_unset_guard(S_direct,S_direct.CURRENT,S_direct.FRAMES,n_child,$ptascii("hidden"))',
 '~$property_unset_guard(S_entered,S_entered.CURRENT,eps,n_child,$ptascii("hidden"))',
 '~$property_unset_guard(S_entered,S_entered.CURRENT,S_entered.FRAMES,n_child,$ptascii("seen"))',
 'S_rebound = S_result[.STORE[n_child_cell] = DEFINED PNULL]',
 '$property_unset_valid(S_rebound,ppropertyunset) /\\ $property_unset_tail(S_rebound,ppropertyunset,S_rebound.TODO) '
 '/\\ ~$property_unset_capture(S_rebound,ppropertyunset)',
 'S_abrupt = $throwable_materialize($throw_scalar(S_received,"Error",$ptascii("cleanup"),5))',
 'S_abrupt.COMPLETION = THROWING n_throw',
 '$property_unset_guard(S_abrupt,S_abrupt.CURRENT,S_abrupt.FRAMES,n_child,$ptascii("hidden"))',
 'S_throw_found = $mu_seek(S_abrupt,5,1000)',
 'S_throw_found.COMPLETION = NORMAL \\/ S_throw_found.COMPLETION = BUDGET',
 'S_throw_result = S_throw_found[.COMPLETION = NORMAL]',
 '$mu_stage(S_throw_result,5)',
 'S_throw_result.TODO = (THROW_SEARCH n_throw) :: (PROPERTY_UNSET_RESULT ppropertyunset) :: ptask_private_tail* /\\ '
 'S_throw_result.CURRENT = eps /\\ S_throw_result.FRAMES = eps /\\ S_throw_result.ORIGIN = (porigin_site)',
 '$property_unset_throw_tail(S_throw_result,ppropertyunset) /\\ $call_task_valid(S_throw_result,PROPERTY_UNSET_RESULT '
 'ppropertyunset) /\\ $mu_guard(S_throw_result)',
 '~$property_unset_guard(S_throw_result,S_throw_result.CURRENT,S_throw_result.FRAMES,n_child,$ptascii("hidden"))',
 'n_throw_owners = $heap_owners($heap_graph(S_throw_result),HOBJECT n_child)',
 'PhpStep: S_throw_result ~> S_throw_discard_raw',
 'S_throw_discard = $mu_after(S_throw_result,S_throw_discard_raw)',
 'S_throw_discard.TODO = (THROW_SEARCH n_throw) :: ptask_private_tail* /\\ S_throw_discard.CURRENT = eps /\\ '
 'S_throw_discard.FRAMES = eps /\\ S_throw_discard.EVENTS = S_throw_result.EVENTS /\\ S_throw_discard.OBJECTPROPS = '
 'S_throw_result.OBJECTPROPS',
 'n_throw_owners = $($heap_owners($heap_graph(S_throw_discard),HOBJECT n_child) + 1)',
 '~$property_unset_throw_tail(S_throw_discard,ppropertyunset) /\\ $mu_guard(S_throw_discard)']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--group', choices=['magic'], required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_unset_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    clauses, negatives, case_index, start_stage = {
        'magic': (BODY, DERIVED, 0, 0),
    }[args.group]
    selections = [(args.group, clauses, negatives)]
    cases = [data['cases'][case_index]]
    sources = [HERE / 'magic-unset.php']
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
    out = Path(tempfile.mkdtemp(prefix='magic-unset-protocol-', dir=ROOT / '.tools'))
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
                     'S_found = $mu_seek(S_initial,' + str(start_stage) + ',1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            content += '\ndec $mu_' + name + '() : bool\ndef $mu_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $mu_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = (' + ' /\\ '.join('$mu_' + name + '()' for name, _, _ in selections) + ')\n'
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
