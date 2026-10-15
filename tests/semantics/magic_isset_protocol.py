"""Check terminal magic isset callbacks, boolean delivery and receiver cleanup."""
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
 'dec $mi_replace(pcoccurrence*,pcpath,pcnode) : pcoccurrence*\n'
 'def $mi_replace(eps,pcpath,pcnode) = eps\n'
 'def $mi_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath pcnode) :: '
 'pcoccurrence*\n'
 'def $mi_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE '
 'pcpath_other pcnode_old) :: $mi_replace(pcoccurrence*,pcpath,pcnode)\n'
 '  -- if pcpath_other =/= pcpath\n'
 'dec $mi_class_replace(pclassdesc*,porigin,pclassdesc) : pclassdesc*\n'
 'def $mi_class_replace(eps,porigin,pclassdesc) = eps\n'
 'def $mi_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_new :: pclassdesc*\n'
 '  -- if pclassdesc_old.ORIGIN = porigin\n'
 'def $mi_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_old :: '
 '$mi_class_replace(pclassdesc*,porigin,pclassdesc_new)\n'
 '  -- if pclassdesc_old.ORIGIN =/= porigin\n'
 'dec $mi_method_replace(pmethoddesc*,porigin,pmethoddesc) : pmethoddesc*\n'
 'def $mi_method_replace(eps,porigin,pmethoddesc) = eps\n'
 'def $mi_method_replace(pmethoddesc_old :: pmethoddesc*,porigin,pmethoddesc_new) = pmethoddesc_new :: pmethoddesc*\n'
 '  -- if pmethoddesc_old.FUNCTION.ORIGIN = porigin\n'
 'def $mi_method_replace(pmethoddesc_old :: pmethoddesc*,porigin,pmethoddesc_new) = pmethoddesc_old :: '
 '$mi_method_replace(pmethoddesc*,porigin,pmethoddesc_new)\n'
 '  -- if pmethoddesc_old.FUNCTION.ORIGIN =/= porigin\n'
 'dec $mi_stage(pstate,nat) : bool\n'
 'def $mi_stage(S,0) = true\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (ISSET_RESULT false 17) :: ptask*\n'
 '  -- if S.BASE = BASE_PROPERTY (POBJECT n) ($ptascii("ready"))\n'
 'def $mi_stage(S,1) = true\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (ISSET_RESULT false 17) :: ptask*\n'
 '  -- if S.BASE = BASE_PROPERTY (POBJECT n) ($ptascii("pending"))\n'
 'def $mi_stage(S,2) = true\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (ISSET_RESULT false 18) :: ptask*\n'
 '  -- if S.BASE = BASE_PROPERTY (POBJECT n) ($ptascii("hidden"))\n'
 'def $mi_stage(S,3) = true\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_ISSET_TARGET ppropertyisset\n'
 '  -- if S.TODO = (ISSET_RESULT false 9) :: ptask*\n'
 '  -- if S.BASE = BASE_PROPERTY (POBJECT n) ($ptascii("hidden"))\n'
 'def $mi_stage(S,4) = true\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask*\n'
 '  -- if ppropertyisset.NAME = $ptascii("hidden")\n'
 'def $mi_stage(S,5) = true\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (ISSET_RESULT false 19) :: ptask*\n'
 '  -- if S.BASE = BASE_PROPERTY (POBJECT n) ($ptascii("other"))\n'
 'def $mi_stage(S,6) = true\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask*\n'
 '  -- if ppropertyisset.NAME = $ptascii("other")\n'
 'def $mi_stage(S,7) = true\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (THROW_SEARCH n) :: (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask*\n'
 'def $mi_stage(S,8) = true\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (ISSET_NEXT expression* n_index) :: ptask*\n'
 '  -- if S.RESULT = KNOWN (PBOOL false)\n'
 'def $mi_stage(S,n) = false -- otherwise\n'
 'dec $mi_seek(pstate,nat,nat) : pstate\n'
 'def $mi_seek(S,n_stage,n) = S\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if $mi_stage(S,n_stage) \\/ n = 0\n'
 'def $mi_seek(S,n_stage,n) = $mi_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if ~$mi_stage(S,n_stage) /\\ $(n > 0)\n'
 'def $mi_seek(S,n_stage,n) = $mi_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
 '  -- if $throwable_pending(S.COMPLETION) /\\ $(n > 0)\n'
 'def $mi_seek(S,n_stage,n) = S -- otherwise\n'
 'dec $mi_after(pstate,pstate) : pstate\n'
 'def $mi_after(S,S_next) = '
 '$gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))\n'
 'dec $mi_guard(pstate) : bool\n'
 'def $mi_guard(S) = ($call_descriptors_valid(S) /\\ $declaration_history_valid(S) /\\ $property_state_valid(S) /\\ '
 '$heap_valid($heap_prune($heap_graph(S))))\n'
 'dec $mi_output(pevent*) : ptbytes\n'
 'def $mi_output(eps) = eps\n'
 'def $mi_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $mi_output(pevent*)\n')

BODY = ['$mi_stage(S,0)',
 '$lookup(S.ENV,$ptascii("child")) = (n_child_cell)',
 'S.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("MagicIssetParent82"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("MagicIssetChild82"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 '$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_parent)',
 'S.OBJECTS[n_child] = INSTANCE porigin_child',
 'ppropertydesc_hidden = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc_other = pclassdesc_parent.PROPERTIES[1]',
 'ppropertydesc_ready = pclassdesc_parent.PROPERTIES[2]',
 'ppropertydesc_pending = pclassdesc_parent.PROPERTIES[3]',
 'porigin_hidden = ppropertydesc_hidden.ORIGIN',
 'ppropertydesc_hidden.KEY = [0] ++ $ptascii("MagicIssetParent82") ++ [0] ++ $ptascii("hidden") /\\ '
 'ppropertydesc_hidden.VISIBILITY = PROPERTY_PRIVATE',
 '$objectprops_at(S.OBJECTPROPS,n_child) = (ppropertyslot_initial*)',
 '$property_slot_at(ppropertyslot_initial*,ppropertydesc_hidden.KEY) = (ppropertyslot_hidden)',
 '$property_slot_at(ppropertyslot_initial*,ppropertydesc_other.KEY) = (ppropertyslot_other)',
 '$property_slot_at(ppropertyslot_initial*,ppropertydesc_ready.KEY) = (ppropertyslot_ready)',
 '$property_slot_at(ppropertyslot_initial*,ppropertydesc_pending.KEY) = (ppropertyslot_pending)',
 'ppropertyslot_hidden.STATE = PROP_VALUE (DIRECT (PINT 10)) /\\ ppropertyslot_other.STATE = PROP_VALUE (DIRECT '
 '(PINT 0))',
 'ppropertyslot_ready.STATE = PROP_VALUE (DIRECT (PINT 0)) /\\ ppropertyslot_pending.STATE = PROP_INITIAL',
 'S.TODO = (ISSET_RESULT false 17) :: ptask_ready_tail*',
 '~$property_isset_needed(S,n_child,$ptascii("ready")) /\\ ~$property_isset_pending(S) /\\ $property_isset_plan(S) = '
 'eps',
 '$mi_guard(S)',
 'PhpStep: S ~> S_ready_raw',
 'S_ready = $mi_after(S,S_ready_raw)',
 'S_ready.RESULT = KNOWN (PBOOL true) /\\ S_ready.TODO = ptask_ready_tail* /\\ S_ready.EVENTS = S.EVENTS /\\ '
 'S_ready.OBJECTPROPS = S.OBJECTPROPS',
 'S_pending_found = $mi_seek(S_ready,1,1000)',
 'S_pending_found.COMPLETION = NORMAL \\/ S_pending_found.COMPLETION = BUDGET',
 'S_pending = S_pending_found[.COMPLETION = NORMAL]',
 '$mi_stage(S_pending,1)',
 'S_pending.TODO = (ISSET_RESULT false 17) :: ptask_pending_tail*',
 '~$property_isset_needed(S_pending,n_child,$ptascii("pending")) /\\ ~$property_isset_pending(S_pending)',
 'PhpStep: S_pending ~> S_pending_raw',
 'S_pending_done = $mi_after(S_pending,S_pending_raw)',
 'S_pending_done.RESULT = KNOWN (PBOOL false) /\\ S_pending_done.TODO = ptask_pending_tail* /\\ '
 'S_pending_done.EVENTS = S_pending.EVENTS',
 'S_hidden_found = $mi_seek(S_pending_done,2,1000)',
 'S_hidden_found.COMPLETION = NORMAL \\/ S_hidden_found.COMPLETION = BUDGET',
 'S_hidden = S_hidden_found[.COMPLETION = NORMAL]',
 '$mi_stage(S_hidden,2)',
 '$mi_output(S_hidden.EVENTS) = $ptascii("P:T/F|H:")',
 'S_hidden.TODO = (ISSET_RESULT false 18) :: ptask_hidden_tail*',
 'S_hidden.ORIGIN = (porigin_site)',
 '$origin_node(S_hidden.SOURCES,porigin_site) = (expression_site)',
 'expression_site = NExprPropertyFetch (NExprVariable (BYTES text_child) metadata_child) (NIdentifier (BYTES '
 'text_hidden) metadata_hidden) metadata_site',
 '$base64(text_child) = $ptascii("child") /\\ $base64(text_hidden) = $ptascii("hidden")',
 '$property_resolve(S_hidden,n_child,$ptascii("hidden")) = PROPERTY_ACCESS ($ptascii("hidden"))',
 '$property_isset_needed(S_hidden,n_child,$ptascii("hidden")) /\\ $property_isset_pending(S_hidden)',
 '$property_isset_plan(S_hidden) = (ppropertyisset)',
 'ppropertyisset.SITE = porigin_site /\\ ppropertyisset.OBJECT = n_child /\\ ppropertyisset.CLASS = porigin_child '
 '/\\ ppropertyisset.PROPERTY = porigin_hidden /\\ ppropertyisset.NAME = $ptascii("hidden") /\\ ppropertyisset.LINE '
 '= 18',
 '$property_isset_method(S_hidden,n_child) = (pmethoddesc_isset)',
 'pmethoddesc_isset.FUNCTION = pfunction_isset',
 'porigin_method = pfunction_isset.ORIGIN',
 'ppropertyisset.METHOD = porigin_method /\\ pmethoddesc_isset.OWNER = porigin_parent /\\ '
 'pmethoddesc_isset.VISIBILITY = PROPERTY_PUBLIC /\\ ~pmethoddesc_isset.STATIC',
 'porigin_parent = PORIGIN n_source pcpath_parent',
 'porigin_method = PORIGIN n_source pcpath_method',
 'pcpath_method = pcpath_parent ++ [PCFIELD 5,PCINDEX 4]',
 'pfunction_isset.NAME = $ptascii("MagicIssetParent82::__isset") /\\ pfunction_isset.LINE = 7 /\\ '
 'pfunction_isset.ENDLINE = 10',
 'pfunction_isset.BODY = pcpath_method ++ [PCFIELD 6] /\\ pfunction_isset.DEFAULTS = eps',
 'pfunction_isset.SIGNATURE.PARAMETERS = [psparam_name]',
 'psparam_name.NAME = $ptascii("name") /\\ psparam_name.TYPE = [PTBRANCH ([PTBUILTIN "string"])] /\\ '
 '~psparam_name.BYREF /\\ ~psparam_name.VARIADIC /\\ psparam_name.REQUIRED /\\ psparam_name.DEFAULT = PSNONE',
 '$ppmethod_isset_signature(pfunction_isset.SIGNATURE) /\\ pfunction_isset.SIGNATURE.RETURNS = [PTBRANCH ([PTBUILTIN '
 '"bool"])]',
 '$property_magic_method_source(S_hidden,pmethoddesc_isset,"__isset") /\\ '
 '~$property_magic_method_source(S_hidden,pmethoddesc_isset,"__unset")',
 '$property_isset_function(S_hidden,ppropertyisset) = (pfunction_isset)',
 '$property_isset_source(S_hidden,ppropertyisset) /\\ $property_isset_valid(S_hidden,ppropertyisset) /\\ '
 '$property_isset_capture(S_hidden,ppropertyisset)',
 '~$property_isset_guard(S_hidden,S_hidden.CURRENT,S_hidden.FRAMES,n_child,$ptascii("hidden"))',
 '$source_unit(S_hidden.SOURCES,n_source) = (pcunit_source)',
 'S_hidden.SOURCES = [pcunit_source]',
 '$origin_node(S_hidden.SOURCES,porigin_method) = (statement_method)',
 'statement_method = NStmtClassMethod phpType14_method phpType24_method phpType4_method phpType11_method '
 'phpType16_method phpType18_method (SEQUENCE statement_body*) metadata_method',
 'phpType16_method = SEQUENCE ([phpType17_parameter])',
 'phpType17_parameter = NParam phpType14_parameter phpType24_parameter phpType18_parameter phpType4_byref '
 'phpType4_variadic phpType10_parameter phpType5_default phpType37_hooks metadata_parameter',
 'phpType18_parameter = NIdentifier (BYTES text_parameter_type) metadata_parameter_type',
 '$origin_node(S_hidden.SOURCES,PORIGIN n_source (pcpath_method ++ [PCFIELD 4,PCINDEX 0])) = (phpType17_parameter)',
 '$property_unset_body_source(S_hidden.SOURCES,n_source,pfunction_isset.BODY,statement_body*,0) /\\ '
 '$mi_guard(S_hidden)',
 'PhpStep: S_hidden ~> S_call_raw',
 'S_call = $mi_after(S_hidden,S_call_raw)',
 'S_call.TODO = (CALL_ARGS (PROPERTY_ISSET_TARGET ppropertyisset) eps 1 ([KNOWN (PSTRING ($ptascii("hidden")))]) '
 '(porigin_site) 18) :: (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_hidden_tail*',
 'S_call.BASE = BASE_VALUE (KNOWN PNULL) /\\ S_call.RESULT = KNOWN PNULL /\\ S_call.HELD = S_hidden.HELD /\\ '
 'S_call.CURRENT = eps /\\ S_call.FRAMES = eps /\\ S_call.EVENTS = S_hidden.EVENTS',
 '$task_nodes(PROPERTY_ISSET_RESULT ppropertyisset) = [HOBJECT n_child] /\\ $target_nodes(PROPERTY_ISSET_TARGET '
 'ppropertyisset) = eps',
 '$heap_owners($heap_graph(S_hidden),HOBJECT n_child) = $heap_owners($heap_graph(S_call),HOBJECT n_child)',
 '$property_isset_pending_call(S_call,ppropertyisset) /\\ $call_task_valid(S_call,CALL_ARGS (PROPERTY_ISSET_TARGET '
 'ppropertyisset) eps 1 ([KNOWN (PSTRING ($ptascii("hidden")))]) (porigin_site) 18) /\\ $mi_guard(S_call)',
 'PhpStep: S_call ~> S_entered_raw',
 'S_entered = $mi_after(S_call,S_entered_raw)',
 'S_entered.CURRENT = (pcallcontext_isset)',
 'pcallcontext_isset.TARGET = PROPERTY_ISSET_TARGET ppropertyisset /\\ pcallcontext_isset.FUNCTION = porigin_method '
 '/\\ pcallcontext_isset.RECEIVER = (n_child) /\\ pcallcontext_isset.LEXICAL_CLASS = (porigin_parent) /\\ '
 'pcallcontext_isset.CALLED_CLASS = (porigin_child)',
 'S_entered.FRAMES = [pframe_isset]',
 'pframe_isset.CONTEXT = eps /\\ pframe_isset.ORIGIN = (porigin_site) /\\ pframe_isset.TODO = (PROPERTY_ISSET_RESULT '
 'ppropertyisset) :: ptask_hidden_tail*',
 'S_entered.TODO = [TYPE_RECEIVE porigin_method 0] /\\ S_entered.ORIGIN = (porigin_method)',
 '$lookup(S_entered.ENV,$ptascii("name")) = (n_name_cell)',
 'S_entered.STORE[n_name_cell] = DEFINED (PSTRING ($ptascii("hidden")))',
 '$typed_receive_valid(S_entered,porigin_method,0) /\\ $default_parameter_line(S_entered,porigin_method,0) = 7',
 '$property_isset_context(S_entered,pcallcontext_isset) /\\ '
 '$property_isset_frame(S_entered,pcallcontext_isset,pframe_isset,ppropertyisset)',
 '$property_isset_guard(S_entered,S_entered.CURRENT,S_entered.FRAMES,n_child,$ptascii("hidden")) /\\ '
 '$call_receiver_roots(pcallcontext_isset) = eps /\\ $mi_guard(S_entered)',
 'PhpStep: S_entered ~> S_received_raw',
 'S_received = $mi_after(S_entered,S_received_raw)',
 'S_received.TODO = $function_body_tasks(S_received,pfunction_isset) /\\ S_received.CURRENT = S_entered.CURRENT /\\ '
 'S_received.FRAMES = S_entered.FRAMES',
 'S_inner_found = $mi_seek(S_received,3,1000)',
 'S_inner_found.COMPLETION = NORMAL \\/ S_inner_found.COMPLETION = BUDGET',
 'S_inner = S_inner_found[.COMPLETION = NORMAL]',
 '$mi_stage(S_inner,3)',
 'S_inner.CURRENT = S_entered.CURRENT /\\ S_inner.FRAMES = S_entered.FRAMES',
 'S_inner.TODO = (ISSET_RESULT false 9) :: ptask_inner_tail*',
 '$property_resolve(S_inner,n_child,$ptascii("hidden")) = PROPERTY_ACCESS ppropertydesc_hidden.KEY',
 '~$property_isset_needed(S_inner,n_child,$ptascii("hidden")) /\\ ~$property_isset_pending(S_inner)',
 'PhpStep: S_inner ~> S_inner_raw',
 'S_inner_done = $mi_after(S_inner,S_inner_raw)',
 'S_inner_done.TODO = ptask_inner_tail* /\\ S_inner_done.RESULT = KNOWN (PBOOL true) /\\ S_inner_done.EVENTS = '
 'S_inner.EVENTS',
 '$method_selected_scope(S_inner_done,n_child,$ptascii("answer"),(porigin_parent)) = (pmethoddesc_answer)',
 'pmethoddesc_answer.OWNER = porigin_parent /\\ pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE',
 '$method_named(pclassdesc_child.METHODS,$ptascii("answer")) = (pmethoddesc_child_answer)',
 'pmethoddesc_child_answer.OWNER = porigin_child /\\ pmethoddesc_child_answer.FUNCTION.ORIGIN =/= '
 'pmethoddesc_answer.FUNCTION.ORIGIN',
 'S_result_found = $mi_seek(S_inner_done,4,1000)',
 'S_result_found.COMPLETION = NORMAL \\/ S_result_found.COMPLETION = BUDGET',
 'S_result = S_result_found[.COMPLETION = NORMAL]',
 '$mi_stage(S_result,4)',
 'S_result.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_hidden_tail* /\\ S_result.CURRENT = eps /\\ '
 'S_result.FRAMES = eps /\\ S_result.ORIGIN = (porigin_site)',
 'S_result.RESULT = KNOWN (PBOOL true) /\\ S_result.BASE = BASE_VALUE (KNOWN PNULL)',
 '$property_isset_valid(S_result,ppropertyisset) /\\ $property_isset_tail(S_result,ppropertyisset,S_result.TODO) /\\ '
 '$mi_guard(S_result)',
 'n_result_owners = $heap_owners($heap_graph(S_result),HOBJECT n_child)',
 'PhpStep: S_result ~> S_result_raw',
 'S_done = $mi_after(S_result,S_result_raw)',
 'S_done.TODO = ptask_hidden_tail* /\\ S_done.RESULT = KNOWN (PBOOL true) /\\ S_done.CURRENT = eps /\\ S_done.FRAMES '
 '= eps',
 'n_result_owners = $($heap_owners($heap_graph(S_done),HOBJECT n_child) + 1)',
 'S_other_found = $mi_seek(S_done,5,1000)',
 'S_other_found.COMPLETION = NORMAL \\/ S_other_found.COMPLETION = BUDGET',
 'S_other = S_other_found[.COMPLETION = NORMAL]',
 '$mi_stage(S_other,5)',
 '$property_isset_plan(S_other) = (ppropertyisset_other)',
 'ppropertyisset_other.NAME = $ptascii("other") /\\ ppropertyisset_other.LINE = 19 /\\ ppropertyisset_other.OBJECT = '
 'n_child /\\ ppropertyisset_other.METHOD = porigin_method',
 'S_false_found = $mi_seek(S_other,6,1000)',
 'S_false_found.COMPLETION = NORMAL \\/ S_false_found.COMPLETION = BUDGET',
 'S_false = S_false_found[.COMPLETION = NORMAL]',
 '$mi_stage(S_false,6)',
 'S_false.TODO = (PROPERTY_ISSET_RESULT ppropertyisset_other) :: ptask_false_tail*',
 'S_false.RESULT = KNOWN (PBOOL false) /\\ S_false.CURRENT = eps /\\ S_false.FRAMES = eps /\\ S_false.OBJECTPROPS = '
 'S.OBJECTPROPS',
 '$mi_output(S_false.EVENTS) = '
 '$ptascii("P:T/F|H:I:hidden/MagicIssetParent82/MagicIssetChild82/MagicIssetParent82::__isset|T|O:I:other/MagicIssetParent82/MagicIssetChild82/MagicIssetParent82::__isset|")',
 'PhpStep: S_false ~> S_false_raw',
 'S_false_done = $mi_after(S_false,S_false_raw)',
 'S_false_done.RESULT = KNOWN (PBOOL false) /\\ S_false_done.TODO = ptask_false_tail* /\\ S_false_done.EVENTS = '
 'S_false.EVENTS',
 'S_next_found = $mi_seek(S_false_done,8,1000)',
 'S_next_found.COMPLETION = NORMAL \\/ S_next_found.COMPLETION = BUDGET',
 'S_next = S_next_found[.COMPLETION = NORMAL]',
 '$mi_stage(S_next,8)',
 'S_next.TODO = (ISSET_NEXT ([expression_next]) 1) :: ptask_next_tail*',
 'expression_next = NExprPropertyFetch (NExprVariable (BYTES text_child) metadata_next_child) (NIdentifier (BYTES '
 'text_hidden) metadata_next_name) metadata_next',
 'S_next.RESULT = KNOWN (PBOOL false)',
 'PhpStep: S_next ~> S_short_raw',
 'S_short = $mi_after(S_next,S_short_raw)',
 'S_short.TODO = ptask_next_tail* /\\ S_short.RESULT = KNOWN (PBOOL false) /\\ S_short.EVENTS = S_next.EVENTS',
 'S_final = $drive_steps(S_short,10000)',
 'S_final.COMPLETION = NORMAL /\\ S_final.TODO = eps /\\ S_final.CURRENT = eps /\\ S_final.FRAMES = eps',
 '$mi_output(S_final.EVENTS) = '
 '$ptascii("P:T/F|H:I:hidden/MagicIssetParent82/MagicIssetChild82/MagicIssetParent82::__isset|T|O:I:other/MagicIssetParent82/MagicIssetChild82/MagicIssetParent82::__isset|F|F:ONLY|")',
 'S_final.OBJECTPROPS = S.OBJECTPROPS',
 '$lookup(S_final.ENV,$ptascii("raw")) = (n_raw_cell)',
 'S_final.STORE[n_raw_cell] = DEFINED (PARRAY n_raw)',
 'S_final.ARRAYS[n_raw].ITEMS = [ENTRY (KSTRING ppropertydesc_hidden.KEY) (DIRECT (PINT 10)),ENTRY (KSTRING '
 'ppropertydesc_other.KEY) (DIRECT (PINT 0)),ENTRY (KSTRING ($ptascii("ready"))) (DIRECT (PINT 0))]',
 '$mi_guard(S_final)']

DERIVED = ['S_badname = S_hidden[.BASE = BASE_PROPERTY (POBJECT n_child) ([0] ++ $ptascii("hidden"))]',
 '$property_resolve(S_badname,n_child,[0] ++ $ptascii("hidden")) = PROPERTY_BADNAME',
 '$property_isset_needed(S_badname,n_child,[0] ++ $ptascii("hidden")) /\\ $property_isset_pending(S_badname) /\\ '
 '$property_isset_plan(S_badname) = eps',
 '$property_quiet(S_badname,POBJECT n_child,[0] ++ $ptascii("hidden"),18).COMPLETION = UNSUPPORTED "magic isset '
 'quiet consumer"',
 'S_empty = S_hidden[.TODO = (ISSET_RESULT true 18) :: ptask_hidden_tail*]',
 '$property_isset_pending(S_empty) /\\ $property_isset_plan(S_empty) = eps',
 '$property_quiet(S_hidden,POBJECT n_child,$ptascii("hidden"),18).COMPLETION = UNSUPPORTED "magic isset quiet '
 'consumer"',
 '$property_isset_method(S_pending,n_child) = (pmethoddesc_isset) /\\ '
 '~$property_isset_needed(S_pending,n_child,$ptascii("pending"))',
 'S_unset = S_pending[.OBJECTPROPS = '
 '$objectprops_set(S_pending.OBJECTPROPS,n_child,$property_slot_set(ppropertyslot_initial*,ppropertydesc_pending.KEY,PROP_UNSET))]',
 '$property_isset_needed(S_unset,n_child,$ptascii("pending")) /\\ $property_isset_pending(S_unset) /\\ '
 '$property_isset_plan(S_unset) = eps',
 'S_source_missing = S_hidden[.SOURCES = ([pcunit_source[.OCCURRENCES = '
 '$mi_replace(pcunit_source.OCCURRENCES,pcpath_method,NStmtNop metadata_method)]])]',
 '$property_isset_method(S_source_missing,n_child) = (pmethoddesc_isset) /\\ '
 '$property_isset_needed(S_source_missing,n_child,$ptascii("hidden")) /\\ $property_isset_pending(S_source_missing) '
 '/\\ $property_isset_function(S_source_missing,ppropertyisset) = eps /\\ $property_isset_plan(S_source_missing) = '
 'eps',
 'pmethoddesc_wrong_owner = pmethoddesc_isset[.OWNER = porigin_child]',
 'S_wrong_owner = S_hidden[.CLASSES = $mi_class_replace(S_hidden.CLASSES,porigin_parent,pclassdesc_parent[.METHODS = '
 '$mi_method_replace(pclassdesc_parent.METHODS,porigin_method,pmethoddesc_wrong_owner)])]',
 '$property_isset_function(S_wrong_owner,ppropertyisset) = eps /\\ $property_isset_plan(S_wrong_owner) = eps',
 'pmethoddesc_wrong_name = pmethoddesc_isset[.FUNCTION = pfunction_isset[.NAME = $ptascii("Forged::__isset")]]',
 'S_wrong_name = S_hidden[.CLASSES = $mi_class_replace(S_hidden.CLASSES,porigin_parent,pclassdesc_parent[.METHODS = '
 '$mi_method_replace(pclassdesc_parent.METHODS,porigin_method,pmethoddesc_wrong_name)])]',
 '$property_isset_function(S_wrong_name,ppropertyisset) = eps /\\ $property_isset_plan(S_wrong_name) = eps',
 'phpType17_bad = NParam phpType14_parameter phpType24_parameter (NIdentifier (BYTES "aW50") '
 'metadata_parameter_type) phpType4_byref phpType4_variadic phpType10_parameter phpType5_default phpType37_hooks '
 'metadata_parameter',
 'S_wrong_param = S_hidden[.SOURCES = ([pcunit_source[.OCCURRENCES = '
 '$mi_replace(pcunit_source.OCCURRENCES,pcpath_method ++ [PCFIELD 4,PCINDEX 0],phpType17_bad)]])]',
 '$property_isset_function(S_wrong_param,ppropertyisset) = eps /\\ $property_isset_plan(S_wrong_param) = eps',
 'S_wrong_body = S_hidden[.SOURCES = ([pcunit_source[.OCCURRENCES = '
 '$mi_replace(pcunit_source.OCCURRENCES,pfunction_isset.BODY ++ [PCINDEX 0],NStmtNop metadata_method)]])]',
 '~$property_unset_body_source(S_wrong_body.SOURCES,n_source,pfunction_isset.BODY,statement_body*,0) /\\ '
 '$property_isset_function(S_wrong_body,ppropertyisset) = eps /\\ $property_isset_plan(S_wrong_body) = eps',
 '~$ppmethod_isset_signature(pfunction_isset.SIGNATURE[.RETURNS = [PTBRANCH ([PTBUILTIN "void"])]])',
 '~$property_isset_valid(S_hidden,ppropertyisset[.PROPERTY = ppropertydesc_ready.ORIGIN])',
 'S_no_result = S_call[.TODO = (CALL_ARGS (PROPERTY_ISSET_TARGET ppropertyisset) eps 1 ([KNOWN (PSTRING '
 '($ptascii("hidden")))]) (porigin_site) 18) :: ptask_hidden_tail*]',
 '$property_isset_function(S_no_result,ppropertyisset) = (pfunction_isset) /\\ '
 '~$property_isset_pending_call(S_no_result,ppropertyisset)',
 'S_wrong_arg = S_call[.TODO = (CALL_ARGS (PROPERTY_ISSET_TARGET ppropertyisset) eps 1 ([KNOWN (PSTRING '
 '($ptascii("other")))]) (porigin_site) 18) :: (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_hidden_tail*]',
 '~$property_isset_pending_call(S_wrong_arg,ppropertyisset)',
 'S_direct = S_entered[.CURRENT = (pcallcontext_isset[.TARGET = METHOD_TARGET n_child porigin_method])]',
 '~$property_isset_guard(S_direct,S_direct.CURRENT,S_direct.FRAMES,n_child,$ptascii("hidden"))',
 '~$property_isset_guard(S_entered,S_entered.CURRENT,eps,n_child,$ptascii("hidden")) /\\ '
 '~$property_isset_guard(S_entered,S_entered.CURRENT,S_entered.FRAMES,n_child,$ptascii("other"))',
 'S_rebound = S_result[.STORE[n_child_cell] = DEFINED PNULL]',
 '$property_isset_valid(S_rebound,ppropertyisset) /\\ $property_isset_tail(S_rebound,ppropertyisset,S_rebound.TODO) '
 '/\\ ~$property_isset_capture(S_rebound,ppropertyisset)',
 'S_abrupt = $throwable_materialize($throw_scalar(S_received,"Error",$ptascii("cleanup"),8))',
 'S_abrupt.COMPLETION = THROWING n_throw',
 '$property_isset_guard(S_abrupt,S_abrupt.CURRENT,S_abrupt.FRAMES,n_child,$ptascii("hidden"))',
 'S_throw_found = $mi_seek(S_abrupt,7,1000)',
 'S_throw_found.COMPLETION = NORMAL \\/ S_throw_found.COMPLETION = BUDGET',
 'S_throw_result = S_throw_found[.COMPLETION = NORMAL]',
 '$mi_stage(S_throw_result,7)',
 'S_throw_result.TODO = (THROW_SEARCH n_throw) :: (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_hidden_tail* /\\ '
 'S_throw_result.CURRENT = eps /\\ S_throw_result.FRAMES = eps /\\ S_throw_result.ORIGIN = (porigin_site)',
 '$property_isset_throw_tail(S_throw_result,ppropertyisset) /\\ '
 '$call_task_valid(S_throw_result,PROPERTY_ISSET_RESULT ppropertyisset) /\\ $mi_guard(S_throw_result)',
 '~$property_isset_guard(S_throw_result,S_throw_result.CURRENT,S_throw_result.FRAMES,n_child,$ptascii("hidden"))',
 'n_throw_owners = $heap_owners($heap_graph(S_throw_result),HOBJECT n_child)',
 'PhpStep: S_throw_result ~> S_throw_raw',
 'S_throw_discard = $mi_after(S_throw_result,S_throw_raw)',
 'S_throw_discard.TODO = (THROW_SEARCH n_throw) :: ptask_hidden_tail* /\\ S_throw_discard.CURRENT = eps /\\ '
 'S_throw_discard.FRAMES = eps /\\ S_throw_discard.EVENTS = S_throw_result.EVENTS',
 'n_throw_owners = $($heap_owners($heap_graph(S_throw_discard),HOBJECT n_child) + 1)',
 '~$property_isset_throw_tail(S_throw_discard,ppropertyisset) /\\ $mi_guard(S_throw_discard)']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--group', choices=['magic'], required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_isset_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    clauses, negatives, case_index, start_stage = {
        'magic': (BODY, DERIVED, 0, 0),
    }[args.group]
    selections = [(args.group, clauses, negatives)]
    cases = [data['cases'][case_index]]
    sources = [HERE / 'magic-isset.php']
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
    out = Path(tempfile.mkdtemp(prefix='magic-isset-protocol-', dir=ROOT / '.tools'))
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
                     'S_found = $mi_seek(S_initial,' + str(start_stage) + ',1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            content += '\ndec $mi_' + name + '() : bool\ndef $mi_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $mi_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = (' + ' /\\ '.join('$mi_' + name + '()' for name, _, _ in selections) + ')\n'
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
