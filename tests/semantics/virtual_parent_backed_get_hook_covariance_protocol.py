"""Source-driven covariant virtual-parent/backed-child getter checks."""
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

PREFIX = 'dec $bc_replace(pcoccurrence*,pcpath,pcnode) : pcoccurrence*\ndef $bc_replace(eps,pcpath,pcnode) = eps\ndef $bc_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath pcnode) :: pcoccurrence*\ndef $bc_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath_other pcnode_old) :: $bc_replace(pcoccurrence*,pcpath,pcnode)\n  -- if pcpath_other =/= pcpath\ndec $bc_output(pevent*) : ptbytes\ndef $bc_output(eps) = eps\ndef $bc_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $bc_output(pevent*)\ndec $bc_stage(pstate,nat) : bool\ndef $bc_stage(S,0) = true\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $property_hook_plan(S[.COMPLETION = NORMAL]) = (ppropertyhook)\n  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n  -- if $ptlc(pclassdesc.NAME) = $ptascii("covbackedchild44")\ndef $bc_stage(S,1) = true\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $property_hook_plan(S[.COMPLETION = NORMAL]) = (ppropertyhook)\n  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n  -- if $ptlc(pclassdesc.NAME) = $ptascii("covbackedgrand44")\n  -- if S.CURRENT = (pcallcontext)\n  -- if $ptlc(pcallcontext.NAME) = $ptascii("covbackedparent44::parentread")\ndef $bc_stage(S,2) = true\n  -- if S.CURRENT = (pcallcontext)\n  -- if $property_hook_context_kind(pcallcontext)\ndef $bc_stage(S,3) = true\n  -- if S.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*\ndef $bc_stage(S,4) = true\n  -- if S.CURRENT = (pcallcontext)\n  -- if $ptlc(pcallcontext.NAME) = $ptascii("covbackedchild44::answer")\ndef $bc_stage(S,5) = true\n  -- if S.TODO = (ASSIGN_ARRAY pbase z b) :: ptask*\n  -- if S.RESULT = KNOWN (PINT 300)\ndef $bc_stage(S,6) = true\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $property_hook_plan(S[.COMPLETION = NORMAL]) = (ppropertyhook)\n  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n  -- if $ptlc(pclassdesc.NAME) = $ptascii("covbackedgrand44")\ndef $bc_stage(S,7) = true\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $property_hook_plan(S[.COMPLETION = NORMAL]) = (ppropertyhook)\n  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n  -- if $ptlc(pclassdesc.NAME) = $ptascii("covbackedlifegrand44")\n  -- if S.CURRENT = (pcallcontext)\n  -- if $ptlc(pcallcontext.NAME) = $ptascii("covbackedlifeparent44::parentread")\ndef $bc_stage(S,10) = true\n  -- if S.TODO = (UNSET (NExprVariable (BYTES "Ym94") metadata)) :: ptask*\ndef $bc_stage(S,11) = true\n  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*\n  -- if pdestructionoperation.SOURCE = UNSET (NExprVariable (BYTES "Ym94") metadata)\ndef $bc_stage(S,12) = true\n  -- if S.CURRENT = (pcallcontext)\n  -- if $ptlc(pcallcontext.NAME) = $ptascii("covbackedlifeparent44::__destruct")\ndef $bc_stage(S,13) = true\n  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*\n  -- if S.OBJECTS[pinstancestorage.OBJECT] = INSTANCE porigin\n  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n  -- if $ptlc(pclassdesc.NAME) = $ptascii("covbackedlifegrand44")\ndef $bc_stage(S,14) = true\n  -- if S.TODO = (UNSET (NExprVariable (BYTES "a2VwdA==") metadata)) :: ptask*\ndef $bc_stage(S,15) = true\n  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*\n  -- if pdestructionoperation.SOURCE = UNSET (NExprVariable (BYTES "a2VwdA==") metadata)\ndef $bc_stage(S,8) = true\n  -- if S.TODO = (ASSIGN_ARRAY pbase z b) :: ptask*\n  -- if z = 36 /\\ S.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("bad")))\ndef $bc_stage(S,n) = false -- otherwise\n\ndec $bc_seek(pstate,nat,nat) : pstate\ndef $bc_seek(S,n_stage,n) = S\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $bc_stage(S,n_stage) \\/ n = 0\ndef $bc_seek(S,n_stage,n) = $bc_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if ~$bc_stage(S,n_stage) /\\ $(n > 0)\ndef $bc_seek(S,n_stage,n) = $bc_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))\n  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n  -- if $throwable_pending(S.COMPLETION) /\\ $(n > 0)\ndef $bc_seek(S,n_stage,n) = S -- otherwise\ndec $bc_after(pstate,pstate) : pstate\ndef $bc_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))\ndec $bc_guard(pstate) : bool\ndef $bc_guard(S) = ($call_descriptors_valid(S) /\\ $declaration_history_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_prune($heap_graph(S))))\ndec $bc_slot(pstate,nat,ptbytes) : ppropstate?\ndef $bc_slot(S,n,ptbytes) = (ppropertyslot_value.STATE)\n  -- if $objectprops_at(S.OBJECTPROPS,n) = (ppropertyslot*)\n  -- if $property_slot_at(ppropertyslot*,ptbytes) = (ppropertyslot_value)\ndef $bc_slot(S,n,ptbytes) = eps -- otherwise\ndec $bc_class_replace(pclassdesc*,porigin,pclassdesc) : pclassdesc*\ndef $bc_class_replace(eps,porigin,pclassdesc) = eps\ndef $bc_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_new :: pclassdesc*\n  -- if pclassdesc_old.ORIGIN = porigin\ndef $bc_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_old :: $bc_class_replace(pclassdesc*,porigin,pclassdesc_new)\n  -- if pclassdesc_old.ORIGIN =/= porigin\ndec $bc_link_replace(pclasslink*,porigin,pclassparent) : pclasslink*\ndef $bc_link_replace(eps,porigin,pclassparent) = eps\ndef $bc_link_replace((CLASSLINK porigin pclassparent_old) :: pclasslink*,porigin,pclassparent) = (CLASSLINK porigin pclassparent) :: pclasslink*\ndef $bc_link_replace((CLASSLINK porigin_other pclassparent_old) :: pclasslink*,porigin,pclassparent) = (CLASSLINK porigin_other pclassparent_old) :: $bc_link_replace(pclasslink*,porigin,pclassparent)\n  -- if porigin_other =/= porigin\n'

CV = [
    '$class_named(S.CLASSNAMES,$ptlc($ptascii("CovBackedParent44"))) = (porigin_parent)',
    '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
    '$class_named(S.CLASSNAMES,$ptlc($ptascii("CovBackedBridge44"))) = (porigin_bridge)',
    '$class_at(S.CLASSES,porigin_bridge) = (pclassdesc_bridge)',
    '$class_named(S.CLASSNAMES,$ptlc($ptascii("CovBackedChild44"))) = (porigin_child)',
    '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
    '$class_named(S.CLASSNAMES,$ptlc($ptascii("CovBackedGrand44"))) = (porigin_grand)',
    '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
    '$class_link_at(S.LINKEDPARENTS,porigin_parent) = eps /\\ pclassdesc_parent.PARENT = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_bridge) = (SOURCE_PARENT porigin_parent) /\\ $class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_bridge) /\\ $class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_child)',
    '|pclassdesc_parent.PROPERTIES| = 1 /\\ |pclassdesc_child.PROPERTIES| = 1 /\\ pclassdesc_bridge.PROPERTIES = eps /\\ pclassdesc_grand.PROPERTIES = eps',
    'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
    'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
    'ppropertydesc_parent.TYPE =/= eps /\\ ppropertydesc_child.TYPE =/= eps /\\ ppropertydesc_parent.TYPE =/= ppropertydesc_child.TYPE /\\ ppropertydesc_parent.DEFAULT = PROP_UNINITIALIZED /\\ $property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT (PINT 200)))',
    '$property_layout(S,porigin_bridge,|S.CLASSES|) = [ppropertydesc_parent] /\\ $property_declaring_class(S.CLASSES,ppropertydesc_parent.ORIGIN) = (porigin_parent) /\\ $property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_child]',
    '$property_hook_virtual_chain(S,ppropertydesc_parent,|S.CLASSES|) /\\ $property_hook_virtual(S,ppropertydesc_parent) /\\ ~$property_hook_override_backed(S,ppropertydesc_parent)',
    '$property_hook_override_backed(S,ppropertydesc_child) /\\ ~$property_hook_virtual(S,ppropertydesc_child) /\\ ~$property_hook_inherited_backing(S,ppropertydesc_child) /\\ ~$property_hook_virtual_chain(S,ppropertydesc_child,|S.CLASSES|)',
    '~$property_hook_override_shape(S,ppropertydesc_parent,ppropertydesc_child) /\\ $property_hook_virtual_edge(S,ppropertydesc_parent,ppropertydesc_child) /\\ $property_hook_backed_over_virtual(S,ppropertydesc_parent,ppropertydesc_child) /\\ $property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child)',
    '$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ $property_hook_covariance(S,ppropertydesc_parent,ppropertydesc_child) = PVCOMPATIBLE /\\ $property_hook_covariance(S,ppropertydesc_child,ppropertydesc_parent) = PVINCOMPATIBLE',
    '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) = eps /\\ $property_initial_slots(S,porigin_parent,[ppropertydesc_parent]) = (eps) /\\ $bc_guard(S)',
    '$method_named(pclassdesc_parent.METHODS,$ptascii("parentRead")) = (pmethoddesc_read)',
    '|ppropertydesc_parent.TYPE| = 2 /\\ (PTBRANCH ([PTBUILTIN "int"])) <- ppropertydesc_parent.TYPE /\\ (PTBRANCH ([PTBUILTIN "string"])) <- ppropertydesc_parent.TYPE /\\ ppropertydesc_child.TYPE = [PTBRANCH ([PTBUILTIN "int"])]',
    '$method_named(pclassdesc_child.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
    '$method_named(pclassdesc_bridge.METHODS,$ptascii("answer")) = (pmethoddesc_bridge_answer)',
    '$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
    'pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.OWNER = porigin_child /\\ pmethoddesc_bridge_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_grand_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_bridge_answer.FUNCTION.ORIGIN /\\ pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_grand_answer.FUNCTION.ORIGIN',
    '$lookup(S.ENV,$ptascii("parent")) = (n_parent_cell)',
    'S.STORE[n_parent_cell] = DEFINED (POBJECT n_parent)',
    'S.OBJECTS[n_parent] = INSTANCE porigin_parent /\\ $objectprops_at(S.OBJECTPROPS,n_parent) = (eps)',
    'S_child = S',
    '$property_hook_plan(S_child) = (ppropertyhook_S_child)',
    'S_child.TODO = (PROPERTY_PREP phpType20_S_child z_S_child) :: (DIM_FETCH z_S_child) :: ptask_S_child*',
    '$property_effective_desc(S_child,ppropertyhook_S_child.OBJECT,$ptascii("value")) = (ppropertydesc_S_child)',
    '$property_hook_function(S_child,ppropertyhook_S_child) = (pfunction_S_child)',
    'S_child.OBJECTS[ppropertyhook_S_child.OBJECT] = INSTANCE porigin_child /\\ ppropertydesc_S_child = ppropertydesc_child /\\ ppropertyhook_S_child.PROPERTY = ppropertydesc_child.ORIGIN /\\ pfunction_S_child.SIGNATURE.RETURNS = ppropertydesc_child.TYPE',
    '$target_lexical_class(S_child,PROPERTY_HOOK_TARGET ppropertyhook_S_child) = (porigin_child) /\\ $target_called_class(S_child,PROPERTY_HOOK_TARGET ppropertyhook_S_child) = (porigin_child) /\\ ~$property_hook_backing(S_child,ppropertyhook_S_child.OBJECT,ppropertydesc_child)',
    '$objectprops_at(S_child.OBJECTPROPS,ppropertyhook_S_child.OBJECT) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 200)) }])',
    '$heap_owners($heap_prune($heap_graph(S_child)),HOBJECT ppropertyhook_S_child.OBJECT) = 1 /\\ $bc_guard(S_child)',
    'PhpStep: S_child ~> S_child_call_raw',
    'S_child_call_raw.TODO = [(CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook_S_child) eps 0 eps (ppropertyhook_S_child.SITE) z_S_child), PROPERTY_HOOK_RESULT ppropertyhook_S_child] ++ ptask_S_child*',
    'S_child_call_raw.RESULT = KNOWN PNULL /\\ S_child_call_raw.EVENTS = S_child.EVENTS /\\ S_child_call_raw.OBJECTPROPS = S_child.OBJECTPROPS',
    'S_child_call = $bc_after(S_child,S_child_call_raw)',
    '$property_hook_pending_call(S_child_call,ppropertyhook_S_child) /\\ $heap_owners($heap_prune($heap_graph(S_child_call)),HOBJECT ppropertyhook_S_child.OBJECT) = 2 /\\ $bc_guard(S_child_call)',
    'S_child_entered_found = $bc_seek(S_child_call,2,1000)',
    'S_child_entered_found.COMPLETION = NORMAL \\/ S_child_entered_found.COMPLETION = BUDGET',
    'S_child_entered = S_child_entered_found[.COMPLETION = NORMAL]',
    'S_child_entered.CURRENT = (pcallcontext_hook_S_child)',
    'S_child_entered.FRAMES = pframe_S_child :: pframe_tail_S_child*',
    'pframe_S_child.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_S_child) :: ptask_S_child* /\\ pcallcontext_hook_S_child.TARGET = PROPERTY_HOOK_TARGET ppropertyhook_S_child /\\ pcallcontext_hook_S_child.FUNCTION = ppropertyhook_S_child.HOOK /\\ pcallcontext_hook_S_child.RECEIVER = (ppropertyhook_S_child.OBJECT)',
    'pcallcontext_hook_S_child.LEXICAL_CLASS = (porigin_child) /\\ pcallcontext_hook_S_child.CALLED_CLASS = (porigin_child) /\\ pfunction_S_child.NAME = pclassdesc_child.NAME ++ $ptascii("::$value::get") /\\ $property_hook_frame(S_child_entered,pcallcontext_hook_S_child,pframe_S_child,ppropertyhook_S_child)',
    '$property_hook_backing(S_child_entered,ppropertyhook_S_child.OBJECT,ppropertydesc_S_child) /\\ $heap_owners($heap_prune($heap_graph(S_child_entered)),HOBJECT ppropertyhook_S_child.OBJECT) = 2 /\\ $bc_guard(S_child_entered)',
    '$objectprops_at(S_child_entered.OBJECTPROPS,ppropertyhook_S_child.OBJECT) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 200)) }])',
    'S_child_answer_found = $bc_seek(S_child_entered,4,1000)',
    'S_child_answer_found.COMPLETION = NORMAL \\/ S_child_answer_found.COMPLETION = BUDGET',
    'S_child_answer = S_child_answer_found[.COMPLETION = NORMAL]',
    'S_child_answer.CURRENT = (pcallcontext_answer_S_child)',
    'pcallcontext_answer_S_child.FUNCTION = pmethoddesc_answer.FUNCTION.ORIGIN /\\ pcallcontext_answer_S_child.LEXICAL_CLASS = (porigin_child) /\\ pcallcontext_answer_S_child.CALLED_CLASS = (porigin_child) /\\ pcallcontext_answer_S_child.RECEIVER = (ppropertyhook_S_child.OBJECT) /\\ $call_context_valid(S_child_answer,pcallcontext_answer_S_child,S_child_answer.CVS)',
    '$objectprops_at(S_child_answer.OBJECTPROPS,ppropertyhook_S_child.OBJECT) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 200)) }])',
    'S_child_result_found = $bc_seek(S_child_answer,3,1000)',
    'S_child_result_found.COMPLETION = NORMAL \\/ S_child_result_found.COMPLETION = BUDGET',
    'S_child_result = S_child_result_found[.COMPLETION = NORMAL]',
    'S_child_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_S_child) :: ptask_S_child* /\\ S_child_result.RESULT = KNOWN (PINT 213) /\\ S_child_result.CURRENT = eps',
    '$objectprops_at(S_child_result.OBJECTPROPS,ppropertyhook_S_child.OBJECT) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 200)) }])',
    '$heap_owners($heap_prune($heap_graph(S_child_result)),HOBJECT ppropertyhook_S_child.OBJECT) = 1 /\\ $task_nodes(PROPERTY_HOOK_RESULT ppropertyhook_S_child) = eps /\\ ~$property_hook_backing(S_child_result,ppropertyhook_S_child.OBJECT,ppropertydesc_child) /\\ $bc_guard(S_child_result)',
    'PhpStep: S_child_result ~> S_child_base_raw',
    'S_child_base_raw.RESULT = S_child_result.RESULT /\\ S_child_base_raw.BASE = BASE_VALUE S_child_result.RESULT /\\ S_child_base_raw.TODO = ptask_S_child* /\\ S_child_base_raw.EVENTS = S_child_result.EVENTS /\\ S_child_base_raw.OBJECTPROPS = S_child_result.OBJECTPROPS',
    'S_child_base = $bc_after(S_child_result,S_child_base_raw)',
    '$bc_guard(S_child_base)',
]

THIS = [
    '$class_named(S.CLASSNAMES,$ptlc($ptascii("CovBackedParent44"))) = (porigin_parent)',
    '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
    '$class_named(S.CLASSNAMES,$ptlc($ptascii("CovBackedBridge44"))) = (porigin_bridge)',
    '$class_at(S.CLASSES,porigin_bridge) = (pclassdesc_bridge)',
    '$class_named(S.CLASSNAMES,$ptlc($ptascii("CovBackedChild44"))) = (porigin_child)',
    '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
    '$class_named(S.CLASSNAMES,$ptlc($ptascii("CovBackedGrand44"))) = (porigin_grand)',
    '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
    '$class_link_at(S.LINKEDPARENTS,porigin_parent) = eps /\\ pclassdesc_parent.PARENT = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_bridge) = (SOURCE_PARENT porigin_parent) /\\ $class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_bridge) /\\ $class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_child)',
    '|pclassdesc_parent.PROPERTIES| = 1 /\\ |pclassdesc_child.PROPERTIES| = 1 /\\ pclassdesc_bridge.PROPERTIES = eps /\\ pclassdesc_grand.PROPERTIES = eps',
    'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
    'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
    'ppropertydesc_parent.TYPE =/= eps /\\ ppropertydesc_child.TYPE =/= eps /\\ ppropertydesc_parent.TYPE =/= ppropertydesc_child.TYPE /\\ ppropertydesc_parent.DEFAULT = PROP_UNINITIALIZED /\\ $property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT (PINT 200)))',
    '$property_layout(S,porigin_bridge,|S.CLASSES|) = [ppropertydesc_parent] /\\ $property_declaring_class(S.CLASSES,ppropertydesc_parent.ORIGIN) = (porigin_parent) /\\ $property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_child]',
    '$property_hook_virtual_chain(S,ppropertydesc_parent,|S.CLASSES|) /\\ $property_hook_virtual(S,ppropertydesc_parent) /\\ ~$property_hook_override_backed(S,ppropertydesc_parent)',
    '$property_hook_override_backed(S,ppropertydesc_child) /\\ ~$property_hook_virtual(S,ppropertydesc_child) /\\ ~$property_hook_inherited_backing(S,ppropertydesc_child) /\\ ~$property_hook_virtual_chain(S,ppropertydesc_child,|S.CLASSES|)',
    '~$property_hook_override_shape(S,ppropertydesc_parent,ppropertydesc_child) /\\ $property_hook_virtual_edge(S,ppropertydesc_parent,ppropertydesc_child) /\\ $property_hook_backed_over_virtual(S,ppropertydesc_parent,ppropertydesc_child) /\\ $property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child)',
    '$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ $property_hook_covariance(S,ppropertydesc_parent,ppropertydesc_child) = PVCOMPATIBLE /\\ $property_hook_covariance(S,ppropertydesc_child,ppropertydesc_parent) = PVINCOMPATIBLE',
    '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) = eps /\\ $property_initial_slots(S,porigin_parent,[ppropertydesc_parent]) = (eps) /\\ $bc_guard(S)',
    '$method_named(pclassdesc_parent.METHODS,$ptascii("parentRead")) = (pmethoddesc_read)',
    '|ppropertydesc_parent.TYPE| = 2 /\\ (PTBRANCH ([PTBUILTIN "int"])) <- ppropertydesc_parent.TYPE /\\ (PTBRANCH ([PTBUILTIN "string"])) <- ppropertydesc_parent.TYPE /\\ ppropertydesc_child.TYPE = [PTBRANCH ([PTBUILTIN "int"])]',
    '$method_named(pclassdesc_child.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
    '$method_named(pclassdesc_bridge.METHODS,$ptascii("answer")) = (pmethoddesc_bridge_answer)',
    '$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
    'pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.OWNER = porigin_child /\\ pmethoddesc_bridge_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_grand_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_bridge_answer.FUNCTION.ORIGIN /\\ pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_grand_answer.FUNCTION.ORIGIN',
    'S_this = S',
    '$property_hook_plan(S_this) = (ppropertyhook_S_this)',
    'S_this.TODO = (PROPERTY_PREP phpType20_S_this z_S_this) :: (DIM_FETCH z_S_this) :: ptask_S_this*',
    '$property_effective_desc(S_this,ppropertyhook_S_this.OBJECT,$ptascii("value")) = (ppropertydesc_S_this)',
    '$property_hook_function(S_this,ppropertyhook_S_this) = (pfunction_S_this)',
    'S_this.OBJECTS[ppropertyhook_S_this.OBJECT] = INSTANCE porigin_grand /\\ ppropertydesc_S_this = ppropertydesc_child /\\ ppropertyhook_S_this.PROPERTY = ppropertydesc_child.ORIGIN /\\ pfunction_S_this.SIGNATURE.RETURNS = ppropertydesc_child.TYPE',
    '$target_lexical_class(S_this,PROPERTY_HOOK_TARGET ppropertyhook_S_this) = (porigin_child) /\\ $target_called_class(S_this,PROPERTY_HOOK_TARGET ppropertyhook_S_this) = (porigin_grand) /\\ ~$property_hook_backing(S_this,ppropertyhook_S_this.OBJECT,ppropertydesc_child)',
    '$objectprops_at(S_this.OBJECTPROPS,ppropertyhook_S_this.OBJECT) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 200)) }])',
    '$heap_owners($heap_prune($heap_graph(S_this)),HOBJECT ppropertyhook_S_this.OBJECT) = 3 /\\ $bc_guard(S_this)',
    'S_this.CURRENT = (pcallcontext_read)',
    'pcallcontext_read.FUNCTION = pmethoddesc_read.FUNCTION.ORIGIN /\\ pcallcontext_read.LEXICAL_CLASS = (porigin_parent) /\\ pcallcontext_read.CALLED_CLASS = (porigin_grand) /\\ $this_receiver(S_this) = (ppropertyhook_S_this.OBJECT)',
    'PhpStep: S_this ~> S_this_call_raw',
    'S_this_call_raw.TODO = [(CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook_S_this) eps 0 eps (ppropertyhook_S_this.SITE) z_S_this), PROPERTY_HOOK_RESULT ppropertyhook_S_this] ++ ptask_S_this*',
    'S_this_call_raw.RESULT = KNOWN PNULL /\\ S_this_call_raw.EVENTS = S_this.EVENTS /\\ S_this_call_raw.OBJECTPROPS = S_this.OBJECTPROPS',
    'S_this_call = $bc_after(S_this,S_this_call_raw)',
    '$property_hook_pending_call(S_this_call,ppropertyhook_S_this) /\\ $heap_owners($heap_prune($heap_graph(S_this_call)),HOBJECT ppropertyhook_S_this.OBJECT) = 3 /\\ $bc_guard(S_this_call)',
    'S_this_entered_found = $bc_seek(S_this_call,2,1000)',
    'S_this_entered_found.COMPLETION = NORMAL \\/ S_this_entered_found.COMPLETION = BUDGET',
    'S_this_entered = S_this_entered_found[.COMPLETION = NORMAL]',
    'S_this_entered.CURRENT = (pcallcontext_hook_S_this)',
    'S_this_entered.FRAMES = pframe_S_this :: pframe_tail_S_this*',
    'pframe_S_this.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_S_this) :: ptask_S_this* /\\ pcallcontext_hook_S_this.TARGET = PROPERTY_HOOK_TARGET ppropertyhook_S_this /\\ pcallcontext_hook_S_this.FUNCTION = ppropertyhook_S_this.HOOK /\\ pcallcontext_hook_S_this.RECEIVER = (ppropertyhook_S_this.OBJECT)',
    'pcallcontext_hook_S_this.LEXICAL_CLASS = (porigin_child) /\\ pcallcontext_hook_S_this.CALLED_CLASS = (porigin_grand) /\\ pfunction_S_this.NAME = pclassdesc_child.NAME ++ $ptascii("::$value::get") /\\ $property_hook_frame(S_this_entered,pcallcontext_hook_S_this,pframe_S_this,ppropertyhook_S_this)',
    '$property_hook_backing(S_this_entered,ppropertyhook_S_this.OBJECT,ppropertydesc_S_this) /\\ $heap_owners($heap_prune($heap_graph(S_this_entered)),HOBJECT ppropertyhook_S_this.OBJECT) = 3 /\\ $bc_guard(S_this_entered)',
    '$objectprops_at(S_this_entered.OBJECTPROPS,ppropertyhook_S_this.OBJECT) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 200)) }])',
    'S_this_answer_found = $bc_seek(S_this_entered,4,1000)',
    'S_this_answer_found.COMPLETION = NORMAL \\/ S_this_answer_found.COMPLETION = BUDGET',
    'S_this_answer = S_this_answer_found[.COMPLETION = NORMAL]',
    'S_this_answer.CURRENT = (pcallcontext_answer_S_this)',
    'pcallcontext_answer_S_this.FUNCTION = pmethoddesc_answer.FUNCTION.ORIGIN /\\ pcallcontext_answer_S_this.LEXICAL_CLASS = (porigin_child) /\\ pcallcontext_answer_S_this.CALLED_CLASS = (porigin_grand) /\\ pcallcontext_answer_S_this.RECEIVER = (ppropertyhook_S_this.OBJECT) /\\ $call_context_valid(S_this_answer,pcallcontext_answer_S_this,S_this_answer.CVS)',
    '$objectprops_at(S_this_answer.OBJECTPROPS,ppropertyhook_S_this.OBJECT) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 200)) }])',
    'S_this_result_found = $bc_seek(S_this_answer,3,1000)',
    'S_this_result_found.COMPLETION = NORMAL \\/ S_this_result_found.COMPLETION = BUDGET',
    'S_this_result = S_this_result_found[.COMPLETION = NORMAL]',
    'S_this_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_S_this) :: ptask_S_this* /\\ S_this_result.RESULT = KNOWN (PINT 213) /\\ S_this_result.CURRENT = (pcallcontext_read)',
    '$objectprops_at(S_this_result.OBJECTPROPS,ppropertyhook_S_this.OBJECT) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 200)) }])',
    '$heap_owners($heap_prune($heap_graph(S_this_result)),HOBJECT ppropertyhook_S_this.OBJECT) = 2 /\\ $task_nodes(PROPERTY_HOOK_RESULT ppropertyhook_S_this) = eps /\\ ~$property_hook_backing(S_this_result,ppropertyhook_S_this.OBJECT,ppropertydesc_child) /\\ $bc_guard(S_this_result)',
    'PhpStep: S_this_result ~> S_this_base_raw',
    'S_this_base_raw.RESULT = S_this_result.RESULT /\\ S_this_base_raw.BASE = BASE_VALUE S_this_result.RESULT /\\ S_this_base_raw.TODO = ptask_S_this* /\\ S_this_base_raw.EVENTS = S_this_result.EVENTS /\\ S_this_base_raw.OBJECTPROPS = S_this_result.OBJECTPROPS',
    'S_this_base = $bc_after(S_this_result,S_this_base_raw)',
    '$bc_guard(S_this_base)',
]

WRITE = [
    '$class_named(S.CLASSNAMES,$ptlc($ptascii("CovBackedParent44"))) = (porigin_parent)',
    '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
    '$class_named(S.CLASSNAMES,$ptlc($ptascii("CovBackedBridge44"))) = (porigin_bridge)',
    '$class_at(S.CLASSES,porigin_bridge) = (pclassdesc_bridge)',
    '$class_named(S.CLASSNAMES,$ptlc($ptascii("CovBackedChild44"))) = (porigin_child)',
    '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
    '$class_named(S.CLASSNAMES,$ptlc($ptascii("CovBackedGrand44"))) = (porigin_grand)',
    '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
    '$class_link_at(S.LINKEDPARENTS,porigin_parent) = eps /\\ pclassdesc_parent.PARENT = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_bridge) = (SOURCE_PARENT porigin_parent) /\\ $class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_bridge) /\\ $class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_child)',
    '|pclassdesc_parent.PROPERTIES| = 1 /\\ |pclassdesc_child.PROPERTIES| = 1 /\\ pclassdesc_bridge.PROPERTIES = eps /\\ pclassdesc_grand.PROPERTIES = eps',
    'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
    'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
    'ppropertydesc_parent.TYPE =/= eps /\\ ppropertydesc_child.TYPE =/= eps /\\ ppropertydesc_parent.TYPE =/= ppropertydesc_child.TYPE /\\ ppropertydesc_parent.DEFAULT = PROP_UNINITIALIZED /\\ $property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT (PINT 200)))',
    '$property_layout(S,porigin_bridge,|S.CLASSES|) = [ppropertydesc_parent] /\\ $property_declaring_class(S.CLASSES,ppropertydesc_parent.ORIGIN) = (porigin_parent) /\\ $property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_child]',
    '$property_hook_virtual_chain(S,ppropertydesc_parent,|S.CLASSES|) /\\ $property_hook_virtual(S,ppropertydesc_parent) /\\ ~$property_hook_override_backed(S,ppropertydesc_parent)',
    '$property_hook_override_backed(S,ppropertydesc_child) /\\ ~$property_hook_virtual(S,ppropertydesc_child) /\\ ~$property_hook_inherited_backing(S,ppropertydesc_child) /\\ ~$property_hook_virtual_chain(S,ppropertydesc_child,|S.CLASSES|)',
    '~$property_hook_override_shape(S,ppropertydesc_parent,ppropertydesc_child) /\\ $property_hook_virtual_edge(S,ppropertydesc_parent,ppropertydesc_child) /\\ $property_hook_backed_over_virtual(S,ppropertydesc_parent,ppropertydesc_child) /\\ $property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child)',
    '$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ $property_hook_covariance(S,ppropertydesc_parent,ppropertydesc_child) = PVCOMPATIBLE /\\ $property_hook_covariance(S,ppropertydesc_child,ppropertydesc_parent) = PVINCOMPATIBLE',
    '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) = eps /\\ $property_initial_slots(S,porigin_parent,[ppropertydesc_parent]) = (eps) /\\ $bc_guard(S)',
    '$method_named(pclassdesc_parent.METHODS,$ptascii("parentRead")) = (pmethoddesc_read)',
    '|ppropertydesc_parent.TYPE| = 2 /\\ (PTBRANCH ([PTBUILTIN "int"])) <- ppropertydesc_parent.TYPE /\\ (PTBRANCH ([PTBUILTIN "string"])) <- ppropertydesc_parent.TYPE /\\ ppropertydesc_child.TYPE = [PTBRANCH ([PTBUILTIN "int"])]',
    '$method_named(pclassdesc_child.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
    '$method_named(pclassdesc_bridge.METHODS,$ptascii("answer")) = (pmethoddesc_bridge_answer)',
    '$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
    'pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.OWNER = porigin_child /\\ pmethoddesc_bridge_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_grand_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_bridge_answer.FUNCTION.ORIGIN /\\ pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_grand_answer.FUNCTION.ORIGIN',
    'S_write = S',
    'S_write.TODO = (ASSIGN_ARRAY pbase_write z_write b_write) :: ptask_write*',
    '$lookup(S_write.ENV,$ptascii("grand")) = (n_grand_cell)',
    'S_write.STORE[n_grand_cell] = DEFINED (POBJECT n_grand)',
    'S_write.OBJECTS[n_grand] = INSTANCE porigin_grand /\\ (HOBJECT n_grand) <- S_write.ALLOCATIONS',
    '$objectprops_at(S_write.OBJECTPROPS,n_grand) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 200)) }])',
    '$property_pending_base(pbase_write) /\\ S_write.RESULT = KNOWN (PINT 300) /\\ z_write = 34 /\\ $call_task_valid(S_write,ASSIGN_ARRAY pbase_write z_write b_write) /\\ $heap_owners($heap_prune($heap_graph(S_write)),HOBJECT n_grand) = 1 /\\ $bc_guard(S_write)',
    'PhpStep: S_write ~> S_write_raw',
    'S_write_raw.COMPLETION = NORMAL /\\ S_write_raw.RESULT = KNOWN (PINT 300) /\\ S_write_raw.EVENTS = S_write.EVENTS /\\ S_write_raw.TODO = ptask_write*',
    '$objectprops_at(S_write_raw.OBJECTPROPS,n_grand) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 300)) }])',
    'S_written = $bc_after(S_write,S_write_raw)',
    '$bc_guard(S_written)',
    'S_bad_found = $bc_seek(S_written,8,1000)',
    'S_bad_found.COMPLETION = NORMAL \\/ S_bad_found.COMPLETION = BUDGET',
    'S_bad = S_bad_found[.COMPLETION = NORMAL]',
    'S_bad.TODO = (ASSIGN_ARRAY (BASE_PROPERTY_PENDING pbase_bad poperand_bad z_receiver_bad) z_bad b_bad) :: ptask_bad*',
    'z_bad = 36 /\\ S_bad.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("bad"))) /\\ $call_task_valid(S_bad,ASSIGN_ARRAY (BASE_PROPERTY_PENDING pbase_bad poperand_bad z_receiver_bad) z_bad b_bad) /\\ $bc_guard(S_bad)',
    'S_bad_receiver = $property_pending_resolve(S_bad,pbase_bad,poperand_bad,PPW,z_receiver_bad,z_bad)',
    'S_bad_receiver.COMPLETION = NORMAL',
    'S_bad_receiver.BASE = BASE_PROPERTY (POBJECT n_grand) ($ptascii("value")) /\\ $property_effective_desc(S_bad,n_grand,$ptascii("value")) = (ppropertydesc_child)',
    '$objectprops_at(S_bad.OBJECTPROPS,n_grand) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 300)) }])',
    '$heap_owners($heap_prune($heap_graph(S_bad)),HOBJECT n_grand) = 1 /\\ $bc_output(S_bad.EVENTS) = $bc_output(S_written.EVENTS) ++ $ptascii("G300|R|")',
    'PhpStep: S_bad ~> S_bad_raw',
    'S_bad_raw.COMPLETION = THROWN "TypeError" ($ptascii("Cannot assign string to property CovBackedChild44::$value of type int")) 36 /\\ S_bad_raw.TODO = ptask_bad* /\\ S_bad_raw.BASE = BASE_PROPERTY (POBJECT n_grand) ($ptascii("value")) /\\ S_bad_raw.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("bad")))',
    'S_bad_raw.OBJECTPROPS = S_bad.OBJECTPROPS /\\ S_bad_raw.STORE = S_bad.STORE /\\ S_bad_raw.OBJECTS = S_bad.OBJECTS /\\ S_bad_raw.ALLOCATIONS = S_bad.ALLOCATIONS /\\ S_bad_raw.EVENTS = S_bad.EVENTS /\\ S_bad_raw.CLASSES = S_bad.CLASSES /\\ $heap_owners($heap_prune($heap_graph(S_bad_raw)),HOBJECT n_grand) = 2',
    'S_bad_throw = $bc_after(S_bad,S_bad_raw)',
    'S_bad_throw.COMPLETION = THROWING n_error',
    '$throwable_field(S_bad_throw,n_error,"message") = PSTRING ($ptascii("Cannot assign string to property CovBackedChild44::$value of type int")) /\\ $throwable_field(S_bad_throw,n_error,"line") = PINT 36',
    'S_bad_search = $throwable_begin(S_bad_throw)',
    'S_bad_search.COMPLETION = NORMAL /\\ S_bad_search.TODO = (THROW_SEARCH n_error) :: ptask_bad* /\\ S_bad_search.RESULT = KNOWN PNULL /\\ S_bad_search.BASE = BASE_VALUE (KNOWN PNULL) /\\ $heap_owners($heap_prune($heap_graph(S_bad_search)),HOBJECT n_grand) = 1 /\\ $bc_guard(S_bad_search)',
    '$objectprops_at(S_bad_search.OBJECTPROPS,n_grand) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 300)) }])',
    'S_after_write_found = $bc_seek(S_bad_search,6,1000)',
    'S_after_write_found.COMPLETION = NORMAL \\/ S_after_write_found.COMPLETION = BUDGET',
    'S_after_write = S_after_write_found[.COMPLETION = NORMAL]',
    '$property_hook_plan(S_after_write) = (ppropertyhook_S_after_write)',
    'S_after_write.TODO = (PROPERTY_PREP phpType20_S_after_write z_S_after_write) :: (DIM_FETCH z_S_after_write) :: ptask_S_after_write*',
    '$property_effective_desc(S_after_write,ppropertyhook_S_after_write.OBJECT,$ptascii("value")) = (ppropertydesc_S_after_write)',
    '$property_hook_function(S_after_write,ppropertyhook_S_after_write) = (pfunction_S_after_write)',
    'S_after_write.OBJECTS[ppropertyhook_S_after_write.OBJECT] = INSTANCE porigin_grand /\\ ppropertydesc_S_after_write = ppropertydesc_child /\\ ppropertyhook_S_after_write.PROPERTY = ppropertydesc_child.ORIGIN /\\ pfunction_S_after_write.SIGNATURE.RETURNS = ppropertydesc_child.TYPE',
    '$target_lexical_class(S_after_write,PROPERTY_HOOK_TARGET ppropertyhook_S_after_write) = (porigin_child) /\\ $target_called_class(S_after_write,PROPERTY_HOOK_TARGET ppropertyhook_S_after_write) = (porigin_grand) /\\ ~$property_hook_backing(S_after_write,ppropertyhook_S_after_write.OBJECT,ppropertydesc_child)',
    '$objectprops_at(S_after_write.OBJECTPROPS,ppropertyhook_S_after_write.OBJECT) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 300)) }])',
    '$heap_owners($heap_prune($heap_graph(S_after_write)),HOBJECT ppropertyhook_S_after_write.OBJECT) = 1 /\\ $bc_guard(S_after_write)',
    'S_after_write_result_found = $bc_seek(S_after_write,3,1000)',
    'S_after_write_result_found.COMPLETION = NORMAL \\/ S_after_write_result_found.COMPLETION = BUDGET',
    'S_after_write_result = S_after_write_result_found[.COMPLETION = NORMAL]',
    'S_after_write_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_S_after_write) :: ptask_S_after_write* /\\ S_after_write_result.RESULT = KNOWN (PINT 313) /\\ S_after_write_result.CURRENT = eps',
    '$objectprops_at(S_after_write_result.OBJECTPROPS,ppropertyhook_S_after_write.OBJECT) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 300)) }])',
    '$heap_owners($heap_prune($heap_graph(S_after_write_result)),HOBJECT ppropertyhook_S_after_write.OBJECT) = 1 /\\ $task_nodes(PROPERTY_HOOK_RESULT ppropertyhook_S_after_write) = eps /\\ ~$property_hook_backing(S_after_write_result,ppropertyhook_S_after_write.OBJECT,ppropertydesc_child) /\\ $bc_guard(S_after_write_result)',
    'PhpStep: S_after_write_result ~> S_after_write_base_raw',
    'S_after_write_base_raw.RESULT = S_after_write_result.RESULT /\\ S_after_write_base_raw.BASE = BASE_VALUE S_after_write_result.RESULT /\\ S_after_write_base_raw.TODO = ptask_S_after_write* /\\ S_after_write_base_raw.EVENTS = S_after_write_result.EVENTS /\\ S_after_write_base_raw.OBJECTPROPS = S_after_write_result.OBJECTPROPS',
    'S_after_write_base = $bc_after(S_after_write_result,S_after_write_base_raw)',
    '$bc_guard(S_after_write_base)',
    'ppropertyhook_S_after_write.OBJECT = n_grand',
    'S_done = $drive_steps(S_after_write_base,10000)',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps /\\ $bc_output(S_done.EVENTS) = EXPECTED_OUTPUT /\\ $bc_guard(S_done)',
    '$objectprops_at(S_done.OBJECTPROPS,n_grand) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 300)) }])',
]

DERIVED = [
    '~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.TYPE = eps]) /\\ ~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.TYPE = [PTBRANCH ([PTBUILTIN "bool"])]])',
    '~$property_hook_backed_over_virtual(S,ppropertydesc_parent,ppropertydesc_child[.DEFAULT = PROP_NULL]) /\\ ~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.DEFAULT = PROP_NULL])',
    '~$property_hook_override_pair(S,ppropertydesc_parent[.DEFAULT = PROP_NULL],ppropertydesc_child) /\\ ~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.ORIGIN = ppropertydesc_parent.ORIGIN]) /\\ ~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.NAME = $ptascii("wrong")])',
    '~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.FINAL = true]) /\\ ~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.SETVISIBILITY = (PROPERTY_PROTECTED)]) /\\ ~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.READONLY = true]) /\\ ~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.VISIBILITY = PROPERTY_PROTECTED])',
    '~$property_hook_backed_over_virtual(S[.CLASSES = eps],ppropertydesc_parent,ppropertydesc_child) /\\ ~$property_hook_override_pair(S[.SOURCES = eps],ppropertydesc_parent,ppropertydesc_child)',
    '~$property_hook_virtual_chain(S,ppropertydesc_parent,0) /\\ $property_hook_virtual_chain(S,ppropertydesc_parent,1)',
    'S_bad_child = S[.LINKEDPARENTS = $bc_link_replace(S.LINKEDPARENTS,porigin_child,STDCLASS_PARENT)]',
    '~$property_hook_backed_over_virtual(S_bad_child,ppropertydesc_parent,ppropertydesc_child) /\\ ~$property_hook_override_pair(S_bad_child,ppropertydesc_parent,ppropertydesc_child)',
    'S_bad_bridge = S[.LINKEDPARENTS = $bc_link_replace(S.LINKEDPARENTS,porigin_bridge,STDCLASS_PARENT)]',
    '~$property_hook_backed_over_virtual(S_bad_bridge,ppropertydesc_parent,ppropertydesc_child) /\\ ~$property_hook_override_pair(S_bad_bridge,ppropertydesc_parent,ppropertydesc_child)',
    'S_bad_root = S[.LINKEDPARENTS = S.LINKEDPARENTS ++ [CLASSLINK porigin_parent (SOURCE_PARENT porigin_child)]]',
    '~$property_hook_virtual_chain(S_bad_root,ppropertydesc_parent,|S.CLASSES|) /\\ ~$property_hook_override_pair(S_bad_root,ppropertydesc_parent,ppropertydesc_child)',
    'S_wrong_own = S[.CLASSES = $bc_class_replace(S.CLASSES,porigin_child,pclassdesc_child[.PROPERTIES = [ppropertydesc_child[.TYPE = eps]]])]',
    '~$property_hook_backed_over_virtual(S_wrong_own,ppropertydesc_parent,ppropertydesc_child) /\\ ~$property_hook_override_pair(S_wrong_own,ppropertydesc_parent,ppropertydesc_child)',
    'S_no_parent = S[.CLASSES = $bc_class_replace(S.CLASSES,porigin_parent,pclassdesc_parent[.PROPERTIES = eps])]',
    '~$property_hook_backed_over_virtual(S_no_parent,ppropertydesc_parent,ppropertydesc_child) /\\ ~$property_hook_override_pair(S_no_parent,ppropertydesc_parent,ppropertydesc_child)',
    'S.SOURCES = pcunit :: pcunit_tail*',
    '$property_hook_origin(S,ppropertydesc_parent) = (porigin_parent_hook)',
    'porigin_parent_hook = PORIGIN n_unit pcpath_parent_hook',
    'ppropertyhook_S_child.HOOK = PORIGIN n_unit pcpath_child_hook',
    'pcunit.ID = n_unit',
    '$origin_node(S.SOURCES,porigin_parent_hook) = (NPropertyHook phpType14_parent phpType24_parent phpType4_parent phpType11_parent phpType16_parent phpType39_parent metadata_parent)',
    '$origin_node(S.SOURCES,ppropertyhook_S_child.HOOK) = (NPropertyHook phpType14_child phpType24_child phpType4_child phpType11_child phpType16_child phpType39_child metadata_child)',
    'phpType38_parent_byref = NPropertyHook phpType14_parent phpType24_parent (BOOLEAN true) phpType11_parent phpType16_parent phpType39_parent metadata_parent',
    'S_parent_byref = S[.SOURCES = pcunit[.OCCURRENCES = $bc_replace(pcunit.OCCURRENCES,pcpath_parent_hook,phpType38_parent_byref)] :: pcunit_tail*]',
    '~$property_hook_virtual_chain(S_parent_byref,ppropertydesc_parent,|S.CLASSES|) /\\ ~$property_hook_override_pair(S_parent_byref,ppropertydesc_parent,ppropertydesc_child)',
    'phpType38_child_byref = NPropertyHook phpType14_child phpType24_child (BOOLEAN true) phpType11_child phpType16_child phpType39_child metadata_child',
    'S_child_byref = S[.SOURCES = pcunit[.OCCURRENCES = $bc_replace(pcunit.OCCURRENCES,pcpath_child_hook,phpType38_child_byref)] :: pcunit_tail*]',
    '~$property_hook_override_pair(S_child_byref,ppropertydesc_parent,ppropertydesc_child)',
    'phpType38_child_unbacked = NPropertyHook phpType14_child phpType24_child phpType4_child phpType11_child phpType16_child phpType39_parent metadata_child',
    'S_child_unbacked = S[.SOURCES = pcunit[.OCCURRENCES = $bc_replace(pcunit.OCCURRENCES,pcpath_child_hook,phpType38_child_unbacked)] :: pcunit_tail*]',
    '~$property_hook_override_backed(S_child_unbacked,ppropertydesc_child) /\\ ~$property_hook_override_pair(S_child_unbacked,ppropertydesc_parent,ppropertydesc_child)',
    '~$property_slots_valid(S,[ppropertydesc_parent],[{ DECL (ppropertyhook_S_child.PROPERTY), NAME ppropertydesc_parent.KEY, STATE PROP_VALUE (DIRECT (PINT 200)) }]) /\\ ~$property_slots_valid(S,[ppropertydesc_child],[{ DECL (porigin_parent_hook), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 200)) }])',
    'S_rollback = $property_hook_link_finish(S,pclassdesc_child,S_bad_child)',
    'S_rollback.COMPLETION = UNSUPPORTED "inherited property hook override" /\\ S_rollback.LINKEDPARENTS = S.LINKEDPARENTS /\\ S_rollback.CLASSNAMES = S.CLASSNAMES /\\ S_rollback.OBJECTPROPS = S.OBJECTPROPS',
    '~$property_hook_virtual_edge(S,ppropertydesc_child,ppropertydesc_parent) /\\ ~$property_hook_covariance_parent(S,ppropertydesc_parent[.TYPE = eps],ppropertydesc_child) /\\ ~$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child[.TYPE = eps])',
    '~$property_hook_covariance_parent(S_wrong_own,ppropertydesc_parent,ppropertydesc_child) /\\ ~$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child[.DEFAULT = PROP_NULL])',
    'S_prelink = S[.CLASSNAMES = eps][.LINKEDPARENTS = [CLASSLINK porigin_bridge (SOURCE_PARENT porigin_parent)]]',
    '$class_named(S_prelink.CLASSNAMES,$ptlc(pclassdesc_child.NAME)) = eps /\\ $class_link_at(S_prelink.LINKEDPARENTS,porigin_child) = eps /\\ $property_hook_covariance_parent(S_prelink,ppropertydesc_parent,ppropertydesc_child) /\\ $property_hook_covariance(S_prelink,ppropertydesc_parent,ppropertydesc_child) = PVCOMPATIBLE /\\ ~$property_hook_backed_over_virtual(S_prelink,ppropertydesc_parent,ppropertydesc_child)',
    'phpType38_parent_backed = NPropertyHook phpType14_parent phpType24_parent phpType4_parent phpType11_parent phpType16_parent phpType39_child metadata_parent',
    'S_parent_backed = S[.SOURCES = pcunit[.OCCURRENCES = $bc_replace(pcunit.OCCURRENCES,pcpath_parent_hook,phpType38_parent_backed)] :: pcunit_tail*]',
    '$property_hook_override_backed(S_parent_backed,ppropertydesc_parent) /\\ ~$property_hook_virtual_chain(S_parent_backed,ppropertydesc_parent,|S.CLASSES|) /\\ ~$property_hook_covariance_parent(S_parent_backed,ppropertydesc_parent,ppropertydesc_child) /\\ ~$property_hook_override_pair(S_parent_backed,ppropertydesc_parent,ppropertydesc_child)',
    'ppropertydesc_effective = ppropertydesc_child[.TYPE = ppropertydesc_parent.TYPE][.DEFAULT = PROP_UNINITIALIZED]',
    'phpType38_child_virtual = NPropertyHook phpType14_child phpType24_child phpType4_child phpType11_child phpType16_child phpType39_parent metadata_child',
    'S_effective = S_parent_backed[.CLASSES = $bc_class_replace(S_parent_backed.CLASSES,porigin_child,pclassdesc_child[.PROPERTIES = [ppropertydesc_effective]])][.SOURCES = pcunit[.OCCURRENCES = $bc_replace($bc_replace(pcunit.OCCURRENCES,pcpath_parent_hook,phpType38_parent_backed),pcpath_child_hook,phpType38_child_virtual)] :: pcunit_tail*]',
    '~$property_hook_override_backed(S_effective,ppropertydesc_effective) /\\ $property_hook_inherited_backing(S_effective,ppropertydesc_effective) /\\ ~$property_hook_virtual(S_effective,ppropertydesc_effective) /\\ ~$property_hook_virtual_chain(S_effective,ppropertydesc_effective,|S_effective.CLASSES|)',
    '$property_hook_covariance(S_effective,ppropertydesc_effective,ppropertydesc_parent[.TYPE = ppropertydesc_child.TYPE]) = PVCOMPATIBLE /\\ ~$property_hook_covariance_parent(S_effective,ppropertydesc_effective,ppropertydesc_parent[.TYPE = ppropertydesc_child.TYPE]) /\\ ~$property_hook_override_pair(S_effective,ppropertydesc_effective,ppropertydesc_parent[.TYPE = ppropertydesc_child.TYPE])',
    'ppropertydesc_parent_unknown = ppropertydesc_parent[.TYPE = [PTBRANCH ([PTCLASS ($ptascii("MissingParent44"))])]]',
    'ppropertydesc_child_unknown = ppropertydesc_child[.TYPE = [PTBRANCH ([PTCLASS ($ptascii("MissingChild44"))])]]',
    'S_unknown = S[.CLASSES = $bc_class_replace($bc_class_replace(S.CLASSES,porigin_parent,pclassdesc_parent[.PROPERTIES = [ppropertydesc_parent_unknown]]),porigin_child,pclassdesc_child[.PROPERTIES = [ppropertydesc_child_unknown]])]',
    '$property_hook_covariance(S_unknown,ppropertydesc_parent_unknown,ppropertydesc_child_unknown) = PVNEEDS ptbytes_missing*',
    '$ptascii("MissingParent44") <- ptbytes_missing* /\\ $ptascii("MissingChild44") <- ptbytes_missing* /\\ $property_hook_covariance_parent(S_unknown,ppropertydesc_parent_unknown,ppropertydesc_child_unknown) /\\ $trait_property_inherit_message(S_unknown,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent_unknown,ppropertydesc_child_unknown) = eps /\\ ~$property_hook_override_pair(S_unknown,ppropertydesc_parent_unknown,ppropertydesc_child_unknown)',
    'S_unknown_linked = $property_hook_link_finish(S,pclassdesc_child[.PROPERTIES = [ppropertydesc_child_unknown]],S_unknown)',
    'S_unknown_linked.COMPLETION = UNSUPPORTED "inherited property hook override" /\\ S_unknown_linked.CLASSES = S.CLASSES /\\ S_unknown_linked.CLASSNAMES = S.CLASSNAMES /\\ S_unknown_linked.LINKEDPARENTS = S.LINKEDPARENTS',
    '$property_hook_covariance_message(S,ppropertydesc_parent,ppropertydesc_child,PVUNSUPPORTED "derived unknown") = eps /\\ $property_hook_covariance_message(S,ppropertydesc_parent,ppropertydesc_child,PVNEEDS ptbytes_missing*) = eps',
    '$property_hook_covariance(S,ppropertydesc_parent,ppropertydesc_child[.TYPE = [PTBRANCH ([PTBUILTIN "bool"])]]) = PVINCOMPATIBLE /\\ ~$property_hook_virtual_edge(S,ppropertydesc_parent,ppropertydesc_child[.TYPE = [PTBRANCH ([PTBUILTIN "bool"])]])',
]


LIFETIME = [
    '$class_named(S.CLASSNAMES,$ptlc($ptascii("CovBackedLifeParent44"))) = (porigin_parent)',
    '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
    '$class_named(S.CLASSNAMES,$ptlc($ptascii("CovBackedLifeBridge44"))) = (porigin_bridge)',
    '$class_at(S.CLASSES,porigin_bridge) = (pclassdesc_bridge)',
    '$class_named(S.CLASSNAMES,$ptlc($ptascii("CovBackedLifeChild44"))) = (porigin_child)',
    '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
    '$class_named(S.CLASSNAMES,$ptlc($ptascii("CovBackedLifeGrand44"))) = (porigin_grand)',
    '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
    '$class_link_at(S.LINKEDPARENTS,porigin_parent) = eps /\\ pclassdesc_parent.PARENT = eps /\\ $class_link_at(S.LINKEDPARENTS,porigin_bridge) = (SOURCE_PARENT porigin_parent) /\\ $class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_bridge) /\\ $class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_child)',
    '|pclassdesc_parent.PROPERTIES| = 1 /\\ |pclassdesc_child.PROPERTIES| = 1 /\\ pclassdesc_bridge.PROPERTIES = eps /\\ pclassdesc_grand.PROPERTIES = eps',
    'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
    'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
    'ppropertydesc_parent.TYPE =/= eps /\\ ppropertydesc_child.TYPE =/= eps /\\ ppropertydesc_parent.TYPE =/= ppropertydesc_child.TYPE /\\ ppropertydesc_parent.DEFAULT = PROP_UNINITIALIZED /\\ $property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT (PNULL)))',
    '$property_layout(S,porigin_bridge,|S.CLASSES|) = [ppropertydesc_parent] /\\ $property_declaring_class(S.CLASSES,ppropertydesc_parent.ORIGIN) = (porigin_parent) /\\ $property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_child]',
    '$property_hook_virtual_chain(S,ppropertydesc_parent,|S.CLASSES|) /\\ $property_hook_virtual(S,ppropertydesc_parent) /\\ ~$property_hook_override_backed(S,ppropertydesc_parent)',
    '$property_hook_override_backed(S,ppropertydesc_child) /\\ ~$property_hook_virtual(S,ppropertydesc_child) /\\ ~$property_hook_inherited_backing(S,ppropertydesc_child) /\\ ~$property_hook_virtual_chain(S,ppropertydesc_child,|S.CLASSES|)',
    '~$property_hook_override_shape(S,ppropertydesc_parent,ppropertydesc_child) /\\ $property_hook_virtual_edge(S,ppropertydesc_parent,ppropertydesc_child) /\\ $property_hook_backed_over_virtual(S,ppropertydesc_parent,ppropertydesc_child) /\\ $property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child)',
    '$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ $property_hook_covariance(S,ppropertydesc_parent,ppropertydesc_child) = PVCOMPATIBLE /\\ $property_hook_covariance(S,ppropertydesc_child,ppropertydesc_parent) = PVINCOMPATIBLE',
    '$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) = eps /\\ $property_initial_slots(S,porigin_parent,[ppropertydesc_parent]) = (eps) /\\ $bc_guard(S)',
    '$method_named(pclassdesc_parent.METHODS,$ptascii("parentRead")) = (pmethoddesc_read)',
    '$method_named(pclassdesc_parent.METHODS,$ptascii("__destruct")) = (pmethoddesc_destructor)',
    '$class_named(S.CLASSNAMES,$ptlc($ptascii("CovBackedAnimal44"))) = (porigin_animal)',
    '$class_named(S.CLASSNAMES,$ptlc($ptascii("CovBackedDog44"))) = (porigin_dog)',
    '$class_link_at(S.LINKEDPARENTS,porigin_dog) = (SOURCE_PARENT porigin_animal) /\\ |ppropertydesc_parent.TYPE| = 2 /\\ |ppropertydesc_child.TYPE| = 2 /\\ (PTBRANCH ([PTBUILTIN "null"])) <- ppropertydesc_parent.TYPE /\\ (PTBRANCH ([PTBUILTIN "null"])) <- ppropertydesc_child.TYPE /\\ (PTBRANCH ([PTCLASS ($ptascii("CovBackedAnimal44"))])) <- ppropertydesc_parent.TYPE /\\ (PTBRANCH ([PTCLASS ($ptascii("CovBackedDog44"))])) <- ppropertydesc_child.TYPE',
    '$pvcovariant(ppropertydesc_child.TYPE,$trait_data_scope(S,pclassdesc_child),ppropertydesc_parent.TYPE,$trait_data_scope(S,pclassdesc_parent),$method_active_registry(S,S.CLASSNAMES)) = PVCOMPATIBLE',
    'S_life = S',
    '$property_hook_plan(S_life) = (ppropertyhook_S_life)',
    '$bc_slot(S_life,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (POBJECT n_stored)))',
    'S_life.TODO = (PROPERTY_PREP phpType20_S_life z_S_life) :: (DIM_FETCH z_S_life) :: ptask_S_life*',
    '$property_effective_desc(S_life,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (ppropertydesc_S_life)',
    '$property_hook_function(S_life,ppropertyhook_S_life) = (pfunction_S_life)',
    'S_life.OBJECTS[ppropertyhook_S_life.OBJECT] = INSTANCE porigin_grand /\\ ppropertydesc_S_life = ppropertydesc_child /\\ ppropertyhook_S_life.PROPERTY = ppropertydesc_child.ORIGIN /\\ $property_declaring_class(S_life.CLASSES,ppropertyhook_S_life.PROPERTY) = (porigin_child) /\\ $property_layout(S_life,porigin_grand,|S_life.CLASSES|) = [ppropertydesc_child]',
    '$target_lexical_class(S_life,PROPERTY_HOOK_TARGET ppropertyhook_S_life) = (porigin_child) /\\ $target_called_class(S_life,PROPERTY_HOOK_TARGET ppropertyhook_S_life) = (porigin_grand) /\\ $bc_slot(S_life,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (POBJECT n_stored))) /\\ $bc_guard(S_life)',
    'S_life.CURRENT = (pcallcontext_read)',
    'pcallcontext_read.FUNCTION = pmethoddesc_read.FUNCTION.ORIGIN /\\ pcallcontext_read.LEXICAL_CLASS = (porigin_parent) /\\ pcallcontext_read.CALLED_CLASS = (porigin_grand) /\\ $heap_owners($heap_prune($heap_graph(S_life)),HOBJECT ppropertyhook_S_life.OBJECT) = 3 /\\ $heap_owners($heap_prune($heap_graph(S_life)),HOBJECT n_stored) = 1 /\\ $bc_output(S_life.EVENTS) = $ptascii("NULL_SLOT|STORED|")',
    'PhpStep: S_life ~> S_life_call_raw',
    'S_life_call_raw.TODO = [(CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook_S_life) eps 0 eps (ppropertyhook_S_life.SITE) z_S_life), PROPERTY_HOOK_RESULT ppropertyhook_S_life] ++ ptask_S_life*',
    'S_life_call = $bc_after(S_life,S_life_call_raw)',
    '$heap_owners($heap_prune($heap_graph(S_life_call)),HOBJECT ppropertyhook_S_life.OBJECT) = 3 /\\ $heap_owners($heap_prune($heap_graph(S_life_call)),HOBJECT n_stored) = 1 /\\ $property_hook_pending_call(S_life_call,ppropertyhook_S_life) /\\ $bc_guard(S_life_call)',
    'S_life_entered_found = $bc_seek(S_life_call,2,1000)',
    'S_life_entered_found.COMPLETION = NORMAL \\/ S_life_entered_found.COMPLETION = BUDGET',
    'S_life_entered = S_life_entered_found[.COMPLETION = NORMAL]',
    'S_life_entered.CURRENT = (pcallcontext_hook_S_life)',
    'S_life_entered.FRAMES = pframe_S_life :: pframe_tail_S_life*',
    'pframe_S_life.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_S_life) :: ptask_S_life* /\\ pcallcontext_hook_S_life.TARGET = PROPERTY_HOOK_TARGET ppropertyhook_S_life /\\ pcallcontext_hook_S_life.FUNCTION = ppropertyhook_S_life.HOOK /\\ pcallcontext_hook_S_life.RECEIVER = (ppropertyhook_S_life.OBJECT)',
    'pcallcontext_hook_S_life.LEXICAL_CLASS = (porigin_child) /\\ pcallcontext_hook_S_life.CALLED_CLASS = (porigin_grand) /\\ pfunction_S_life.NAME = pclassdesc_child.NAME ++ $ptascii("::$value::get") /\\ $property_hook_frame(S_life_entered,pcallcontext_hook_S_life,pframe_S_life,ppropertyhook_S_life) /\\ $property_hook_backing(S_life_entered,ppropertyhook_S_life.OBJECT,ppropertydesc_S_life) /\\ $bc_guard(S_life_entered)',
    'pframe_S_life.CONTEXT = (pcallcontext_read) /\\ $heap_owners($heap_prune($heap_graph(S_life_entered)),HOBJECT ppropertyhook_S_life.OBJECT) = 3 /\\ $heap_owners($heap_prune($heap_graph(S_life_entered)),HOBJECT n_stored) = 1',
    'S_result_found = $bc_seek(S_life_entered,3,1000)',
    'S_result_found.COMPLETION = NORMAL \\/ S_result_found.COMPLETION = BUDGET',
    'S_result = S_result_found[.COMPLETION = NORMAL]',
    'S_result.RESULT = KNOWN (POBJECT n_returned)',
    'S_result.OBJECTS[n_stored] = INSTANCE porigin_dog /\\ S_result.OBJECTS[n_returned] = INSTANCE porigin_dog /\\ $class_link_at(S_result.LINKEDPARENTS,porigin_dog) = (SOURCE_PARENT porigin_animal)',
    'S_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_S_life) :: ptask_S_life* /\\ S_result.CURRENT = (pcallcontext_read) /\\ n_returned =/= n_stored /\\ $heap_owners($heap_prune($heap_graph(S_result)),HOBJECT n_returned) = 1 /\\ $heap_owners($heap_prune($heap_graph(S_result)),HOBJECT n_stored) = 1 /\\ $heap_owners($heap_prune($heap_graph(S_result)),HOBJECT ppropertyhook_S_life.OBJECT) = 2 /\\ $task_nodes(PROPERTY_HOOK_RESULT ppropertyhook_S_life) = eps /\\ $bc_guard(S_result)',
    '$bc_slot(S_result,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (POBJECT n_stored))) /\\ (HOBJECT n_stored) <- $node_children(S_result,HOBJECT ppropertyhook_S_life.OBJECT) /\\ ~((HOBJECT n_returned) <- $node_children(S_result,HOBJECT ppropertyhook_S_life.OBJECT))',
    'S_result.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("weak_returned")) = (n_weak_returned_cell)',
    'S_result.STORE[n_weak_returned_cell] = DEFINED (POBJECT n_weak_returned)',
    '$lookup(psymboltable_global.ENV,$ptascii("weak_stored")) = (n_weak_stored_cell)',
    'S_result.STORE[n_weak_stored_cell] = DEFINED (POBJECT n_weak_stored)',
    '$lookup(psymboltable_global.ENV,$ptascii("weak_box")) = (n_weak_box_cell)',
    'S_result.STORE[n_weak_box_cell] = DEFINED (POBJECT n_weak_box)',
    '$weakref_get(S_result,n_weak_returned) = POBJECT n_returned /\\ $weakref_get(S_result,n_weak_stored) = POBJECT n_stored /\\ $weakref_get(S_result,n_weak_box) = POBJECT ppropertyhook_S_life.OBJECT /\\ $bc_output(S_result.EVENTS) = $ptascii("NULL_SLOT|STORED|CS|GR|")',
    'PhpStep: S_result ~> S_base_raw',
    'S_base_raw.RESULT = KNOWN (POBJECT n_returned) /\\ S_base_raw.BASE = BASE_VALUE (KNOWN (POBJECT n_returned)) /\\ S_base_raw.TODO = ptask_S_life* /\\ S_base_raw.EVENTS = S_result.EVENTS /\\ $heap_owners($heap_prune($heap_graph(S_base_raw)),HOBJECT n_returned) = 2 /\\ $heap_owners($heap_prune($heap_graph(S_base_raw)),HOBJECT n_stored) = 1',
    'S_base = $bc_after(S_result,S_base_raw)',
    '$heap_owners($heap_prune($heap_graph(S_base)),HOBJECT n_returned) = 2 /\\ $heap_owners($heap_prune($heap_graph(S_base)),HOBJECT n_stored) = 1 /\\ $bc_guard(S_base)',
    'S_box_unset_found = $bc_seek(S_base,10,1000)',
    'S_box_unset_found.COMPLETION = NORMAL \\/ S_box_unset_found.COMPLETION = BUDGET',
    'S_box_unset = S_box_unset_found[.COMPLETION = NORMAL]',
    '$lookup(S_box_unset.ENV,$ptascii("kept")) = (n_kept_cell)',
    'S_box_unset.STORE[n_kept_cell] = DEFINED (POBJECT n_returned)',
    '$heap_owners($heap_prune($heap_graph(S_box_unset)),HOBJECT n_returned) = 1 /\\ $heap_owners($heap_prune($heap_graph(S_box_unset)),HOBJECT n_stored) = 1 /\\ $bc_output(S_box_unset.EVENTS) = $ptascii("NULL_SLOT|STORED|CS|GR|HR|SLOT_S|") /\\ $bc_slot(S_box_unset,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (POBJECT n_stored))) /\\ $bc_guard(S_box_unset)',
    'PhpStep: S_box_unset ~> S_box_raw',
    '$lookup(S_box_raw.ENV,$ptascii("box")) = eps /\\ $heap_owners($heap_prune($heap_graph(S_box_raw)),HOBJECT ppropertyhook_S_life.OBJECT) = 0 /\\ S_box_raw.EVENTS = S_box_unset.EVENTS',
    'S_box_release = $bc_after(S_box_unset,S_box_raw)',
    'S_destructor_found = $bc_seek(S_box_release,12,1000)',
    'S_destructor_found.COMPLETION = NORMAL \\/ S_destructor_found.COMPLETION = BUDGET',
    'S_destructor = S_destructor_found[.COMPLETION = NORMAL]',
    'S_destructor.CURRENT = (pcallcontext_destructor)',
    'pcallcontext_destructor.FUNCTION = pmethoddesc_destructor.FUNCTION.ORIGIN /\\ pcallcontext_destructor.LEXICAL_CLASS = (porigin_parent) /\\ pcallcontext_destructor.CALLED_CLASS = (porigin_grand) /\\ pcallcontext_destructor.RECEIVER = (ppropertyhook_S_life.OBJECT) /\\ $bc_slot(S_destructor,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (POBJECT n_stored))) /\\ $bc_guard(S_destructor)',
    'S_storage_found = $bc_seek(S_destructor,13,1000)',
    'S_storage_found.COMPLETION = NORMAL \\/ S_storage_found.COMPLETION = BUDGET',
    'S_storage = S_storage_found[.COMPLETION = NORMAL]',
    'S_storage.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_storage*',
    'pinstancestorage.OBJECT = ppropertyhook_S_life.OBJECT /\\ pinstancestorage.NEXT = 0 /\\ $instance_storage_valid(S_storage,pinstancestorage) /\\ $bc_slot(S_storage,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (POBJECT n_stored))) /\\ $heap_owners($heap_prune($heap_graph(S_storage)),HOBJECT n_stored) = 1 /\\ $heap_owners($heap_prune($heap_graph(S_storage)),HOBJECT n_returned) = 1 /\\ $bc_output(S_storage.EVENTS) = $ptascii("NULL_SLOT|STORED|CS|GR|HR|SLOT_S|BS|") /\\ $bc_guard(S_storage)',
    'PhpStep: S_storage ~> S_slot_raw',
    'S_slot_raw.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_slot) :: (INSTANCE_STORAGE_STEP pinstancestorage_next) :: ptask_storage*',
    'pinstancestorage_next = pinstancestorage[.NEXT = 1] /\\ pdestructionrelease_slot.JOBS = [DESTRUCTION_VALUE (HOBJECT n_stored)] /\\ $bc_slot(S_slot_raw,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (PROP_UNSET) /\\ $heap_owners($heap_prune($heap_graph(S_slot_raw)),HOBJECT n_stored) = 1 /\\ $heap_owners($heap_prune($heap_graph(S_slot_raw)),HOBJECT n_returned) = 1 /\\ S_slot_raw.EVENTS = S_storage.EVENTS',
    'S_slot_release = $bc_after(S_storage,S_slot_raw)',
    'S_box_disposed_found = $bc_seek(S_slot_release,11,1000)',
    'S_box_disposed_found.COMPLETION = NORMAL \\/ S_box_disposed_found.COMPLETION = BUDGET',
    'S_box_disposed = S_box_disposed_found[.COMPLETION = NORMAL]',
    '~((HOBJECT ppropertyhook_S_life.OBJECT) <- S_box_disposed.ALLOCATIONS) /\\ ~((HOBJECT n_stored) <- S_box_disposed.ALLOCATIONS) /\\ (HOBJECT n_returned) <- S_box_disposed.ALLOCATIONS /\\ $weakref_get(S_box_disposed,n_weak_box) = PNULL /\\ $weakref_get(S_box_disposed,n_weak_stored) = PNULL /\\ $weakref_get(S_box_disposed,n_weak_returned) = POBJECT n_returned /\\ $heap_owners($heap_prune($heap_graph(S_box_disposed)),HOBJECT n_returned) = 1 /\\ $bc_output(S_box_disposed.EVENTS) = $ptascii("NULL_SLOT|STORED|CS|GR|HR|SLOT_S|BS|DS|") /\\ $bc_guard(S_box_disposed)',
    'S_kept_unset_found = $bc_seek(S_box_disposed,14,1000)',
    'S_kept_unset_found.COMPLETION = NORMAL \\/ S_kept_unset_found.COMPLETION = BUDGET',
    'S_kept_unset = S_kept_unset_found[.COMPLETION = NORMAL]',
    '$heap_owners($heap_prune($heap_graph(S_kept_unset)),HOBJECT n_returned) = 1 /\\ $weakref_get(S_kept_unset,n_weak_returned) = POBJECT n_returned /\\ $bc_output(S_kept_unset.EVENTS) = $ptascii("NULL_SLOT|STORED|CS|GR|HR|SLOT_S|BS|DS|BN|SN|LIVE|") /\\ $bc_guard(S_kept_unset)',
    'PhpStep: S_kept_unset ~> S_kept_raw',
    '$lookup(S_kept_raw.ENV,$ptascii("kept")) = eps /\\ $heap_owners($heap_prune($heap_graph(S_kept_raw)),HOBJECT n_returned) = 0 /\\ S_kept_raw.EVENTS = S_kept_unset.EVENTS',
    'S_kept_release = $bc_after(S_kept_unset,S_kept_raw)',
    'S_returned_disposed_found = $bc_seek(S_kept_release,15,1000)',
    'S_returned_disposed_found.COMPLETION = NORMAL \\/ S_returned_disposed_found.COMPLETION = BUDGET',
    'S_returned_disposed = S_returned_disposed_found[.COMPLETION = NORMAL]',
    '~((HOBJECT n_returned) <- S_returned_disposed.ALLOCATIONS) /\\ $weakref_get(S_returned_disposed,n_weak_returned) = PNULL /\\ $bc_output(S_returned_disposed.EVENTS) = $ptascii("NULL_SLOT|STORED|CS|GR|HR|SLOT_S|BS|DS|BN|SN|LIVE|DR|") /\\ $bc_guard(S_returned_disposed)',
    'S_done = $drive_steps(S_returned_disposed,10000)',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps /\\ $weakref_get(S_done,n_weak_returned) = PNULL /\\ $weakref_get(S_done,n_weak_stored) = PNULL /\\ $weakref_get(S_done,n_weak_box) = PNULL /\\ $bc_output(S_done.EVENTS) = EXPECTED_OUTPUT /\\ $bc_guard(S_done)',
]

INVALID = [
    'S.COMPLETION = STATICBYTES ($ptascii("Declaration of CovBackedBadChild44::$value::get(): string|int must be compatible with CovBackedBadParent44::$value::get(): int")) 6 /\\ S.EVENTS = eps /\\ S.OBJECTS = eps /\\ S.OBJECTPROPS = eps',
    'S.CLASSES = [pclassdesc_parent,pclassdesc_child]',
    'pclassdesc_parent.NAME = $ptascii("CovBackedBadParent44") /\\ pclassdesc_child.NAME = $ptascii("CovBackedBadChild44") /\\ pclassdesc_parent.PROPERTIES =/= eps /\\ pclassdesc_child.PROPERTIES =/= eps',
    'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
    'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
    '$property_hook_origin(S,ppropertydesc_parent) = (porigin_parent_hook)',
    '$property_hook_origin(S,ppropertydesc_child) = (porigin_hook)',
    'porigin_hook = PORIGIN n_unit pcpath_hook',
    'S.ERRORORIGIN = eps /\\ pclassdesc_child.LINE = 5 /\\ n_unit = 0 /\\ pcpath_hook =/= eps',
    '$origin_node(S.SOURCES,porigin_hook) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook phpType16_hook phpType39_hook metadata_hook)',
    '$source_line(metadata_hook) = 6 /\\ $class_named(S.CLASSNAMES,$ptlc(pclassdesc_child.NAME)) = eps /\\ $class_link_at(S.LINKEDPARENTS,pclassdesc_child.ORIGIN) = eps /\\ $class_named(S.CLASSNAMES,$ptlc(pclassdesc_parent.NAME)) = (pclassdesc_parent.ORIGIN)',
    '$function_at(S.FUNCTIONS,porigin_parent_hook) = (pfunction_parent)',
    '$function_at(S.FUNCTIONS,porigin_hook) = (pfunction_child)',
    'pfunction_parent.SIGNATURE.RETURNS = ppropertydesc_parent.TYPE /\\ pfunction_child.SIGNATURE.RETURNS = ppropertydesc_child.TYPE /\\ ppropertydesc_parent.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ |ppropertydesc_child.TYPE| = 2 /\\ (PTBRANCH ([PTBUILTIN "int"])) <- ppropertydesc_child.TYPE /\\ (PTBRANCH ([PTBUILTIN "string"])) <- ppropertydesc_child.TYPE',
    '$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child) /\\ $property_hook_covariance(S,ppropertydesc_parent,ppropertydesc_child) = PVINCOMPATIBLE /\\ ~$property_hook_virtual_edge(S,ppropertydesc_parent,ppropertydesc_child) /\\ $property_hook_override_backed(S,ppropertydesc_child) /\\ $property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT (PINT 200)))',
    '$property_hook_covariance_error_site(S,[ppropertydesc_parent],ppropertydesc_child,$ptascii("Declaration of CovBackedBadChild44::$value::get(): string|int must be compatible with CovBackedBadParent44::$value::get(): int")) = ((porigin_hook,6))',
    'S.TODO = eps /\\ S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.ENV = eps /\\ $declaration_history_valid(S) /\\ $class_links_valid(S)',
]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--group', choices=['cv', 'this', 'write', 'lifetime', 'invalid'], required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'virtual_parent_backed_get_hook_covariance_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    clauses, negatives, case_index, start_stage = {
        'cv': (CV, DERIVED, 0, 0),
        'this': (THIS, [], 0, 1),
        'write': (WRITE, [], 0, 5),
        'lifetime': (LIFETIME, [], 1, 7),
        'invalid': (INVALID, [], 2, None),
    }[args.group]
    selections = [(args.group, clauses, negatives)]
    cases = [data['cases'][case_index]]
    sources = [HERE / ('virtual-parent-backed-get-hook-covariance-' + ['scalar', 'lifetime', 'invalid'][case_index] + '.php')]
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
    out = Path(tempfile.mkdtemp(prefix='virtual-parent-backed-get-hook-covariance-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    derived = sum(len(row[2]) for row in selections)
    reached = sum((1 if args.group == 'invalid' else 5) + len(row[1]) for row in selections)
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
                     'S_found = $bc_seek(S_initial,' + str(start_stage) + ',1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            if args.group == 'invalid':
                setup = [setup[0].replace('S_initial =', 'S =', 1)]
            content += '\ndec $bc_' + name + '() : bool\ndef $bc_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                condition = condition.replace('EXPECTED_OUTPUT', byte_expr(base64.b64decode(case['stdout_base64'])))
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $bc_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = (' + ' /\\ '.join('$bc_' + name + '()' for name, _, _ in selections) + ')\n'
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


if __name__ == "__main__":
    main()
