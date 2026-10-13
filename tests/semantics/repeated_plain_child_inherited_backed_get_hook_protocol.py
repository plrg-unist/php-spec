"""Check original getter provenance and latest repeated plain-child storage at genuine source states."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()



PREFIX = ('dec $rpi_replace(pcoccurrence*,pcpath,pcnode) : pcoccurrence*\n'
 'def $rpi_replace(eps,pcpath,pcnode) = eps\n'
 'def $rpi_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = '
 '(PCOCCURRENCE pcpath pcnode) :: pcoccurrence*\n'
 'def $rpi_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*,pcpath,pcnode) = '
 '(PCOCCURRENCE pcpath_other pcnode_old) :: $rpi_replace(pcoccurrence*,pcpath,pcnode)\n'
 '  -- if pcpath_other =/= pcpath\n'
 'dec $rpi_stage(pstate,nat) : bool\n'
 'def $rpi_stage(S,0) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n'
 '  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n'
 '  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n'
 '  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n'
 '  -- if $ptlc(pclassdesc.NAME) = $ptascii("repeatedplainsecond55")\n'
 'def $rpi_stage(S,1) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n'
 '  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n'
 '  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n'
 '  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n'
 '  -- if $ptlc(pclassdesc.NAME) = $ptascii("repeatedplaingrand55")\n'
 '  -- if S.FRAMES = pframe :: pframe_tail*\n'
 '  -- if pframe.CONTEXT = (pcallcontext_read)\n'
 '  -- if $ptlc(pcallcontext_read.NAME) = $ptascii("repeatedplainparent55::parentread")\n'
 'def $rpi_stage(S,2) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.TODO = (ASSIGN_ARRAY pbase z b) :: ptask*\n'
 '  -- if S.RESULT = KNOWN (PINT 400)\n'
 'def $rpi_stage(S,3) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n'
 '  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n'
 '  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n'
 '  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n'
 '  -- if $ptlc(pclassdesc.NAME) = $ptascii("repeatedplaingrand55")\n'
 '  -- if $objectprops_at(S.OBJECTPROPS,ppropertyhook.OBJECT) = (ppropertyslot*)\n'
 '  -- if $property_slot_at(ppropertyslot*,$ptascii("value")) = (ppropertyslot_value)\n'
 '  -- if ppropertyslot_value.STATE = PROP_VALUE (DIRECT (PINT 400))\n'
 'def $rpi_stage(S,4) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*\n'
 'def $rpi_stage(S,5) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if $ptlc(pcallcontext.NAME) = $ptascii("repeatedplainparent55::answer")\n'
 'def $rpi_stage(S,n) = false -- otherwise\n'
 '\n'
 'dec $rpi_seek(pstate,nat,nat) : pstate\n'
 'def $rpi_seek(S,n_stage,n) = S\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if $rpi_stage(S,n_stage) \\/ n = 0\n'
 'def $rpi_seek(S,n_stage,n) = $rpi_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n '
 '- 1)))\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if ~$rpi_stage(S,n_stage) /\\ $(n > 0)\n'
 'def $rpi_seek(S,n_stage,n) = $rpi_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
 '  -- if $throwable_pending(S.COMPLETION) /\\ $(n > 0)\n'
 'def $rpi_seek(S,n_stage,n) = S -- otherwise\n'
 'dec $rpi_after(pstate,pstate) : pstate\n'
 'def $rpi_after(S,S_next) = '
 '$gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))\n'
 'dec $rpi_guard(pstate) : bool\n'
 'def $rpi_guard(S) = ($call_descriptors_valid(S) /\\ $declaration_history_valid(S) /\\ '
 '$property_state_valid(S) /\\ $heap_valid($heap_prune($heap_graph(S))))\n'
 'dec $rpi_class_replace(pclassdesc*,porigin,pclassdesc) : pclassdesc*\n'
 'def $rpi_class_replace(eps,porigin,pclassdesc) = eps\n'
 'def $rpi_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_new :: '
 'pclassdesc*\n'
 '  -- if pclassdesc_old.ORIGIN = porigin\n'
 'def $rpi_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_old :: '
 '$rpi_class_replace(pclassdesc*,porigin,pclassdesc_new)\n'
 '  -- if pclassdesc_old.ORIGIN =/= porigin\n'
 'dec $rpi_link_replace(pclasslink*,porigin,pclassparent) : pclasslink*\n'
 'def $rpi_link_replace(eps,porigin,pclassparent) = eps\n'
 'def $rpi_link_replace((CLASSLINK porigin pclassparent_old) :: pclasslink*,porigin,pclassparent) '
 '= (CLASSLINK porigin pclassparent) :: pclasslink*\n'
 'def $rpi_link_replace((CLASSLINK porigin_other pclassparent_old) :: '
 'pclasslink*,porigin,pclassparent) = (CLASSLINK porigin_other pclassparent_old) :: '
 '$rpi_link_replace(pclasslink*,porigin,pclassparent)\n'
 '  -- if porigin_other =/= porigin\n')

COMMON = ['$class_named(S.CLASSNAMES,$ptlc($ptascii("RepeatedPlainParent55"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("RepeatedPlainFirst55"))) = (porigin_first)',
 '$class_at(S.CLASSES,porigin_first) = (pclassdesc_first)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("RepeatedPlainBridge55"))) = (porigin_bridge)',
 '$class_at(S.CLASSES,porigin_bridge) = (pclassdesc_bridge)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("RepeatedPlainSecond55"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("RepeatedPlainGrand55"))) = (porigin_grand)',
 '$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
 '$class_link_at(S.LINKEDPARENTS,porigin_parent) = eps /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_first) = (SOURCE_PARENT porigin_parent) /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_bridge) = (SOURCE_PARENT porigin_first) /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_bridge) /\\ '
 '$class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_child)',
 '|pclassdesc_parent.PROPERTIES| = 1 /\\ |pclassdesc_first.PROPERTIES| = 1 /\\ '
 '|pclassdesc_child.PROPERTIES| = 1 /\\ pclassdesc_bridge.PROPERTIES = eps /\\ '
 'pclassdesc_grand.PROPERTIES = eps',
 'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc_first = pclassdesc_first.PROPERTIES[0]',
 'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
 'ppropertydesc_parent.TYPE = [PTBRANCH ([PTBUILTIN "int"])] /\\ ppropertydesc_first.TYPE = '
 'ppropertydesc_parent.TYPE /\\ ppropertydesc_child.TYPE = ppropertydesc_parent.TYPE /\\ '
 '$property_default_state(S,ppropertydesc_parent) = (PROP_VALUE (DIRECT (PINT 100))) /\\ '
 '$property_default_state(S,ppropertydesc_first) = (PROP_VALUE (DIRECT (PINT 200))) /\\ '
 '$property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT (PINT 300)))',
 '$property_layout(S,porigin_bridge,|S.CLASSES|) = [ppropertydesc_first] /\\ '
 '$property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_child]',
 '$property_hook_origin(S,ppropertydesc_parent) = (porigin_hook_parent)',
 '$property_hook_origin(S,ppropertydesc_first) = eps /\\ '
 '$property_hook_origin(S,ppropertydesc_child) = eps /\\ '
 '~$property_hook_override_backed(S,ppropertydesc_first) /\\ '
 '~$property_hook_override_backed(S,ppropertydesc_child) /\\ '
 '~$property_hook_inherited_backing(S,ppropertydesc_first) /\\ '
 '~$property_hook_inherited_backing(S,ppropertydesc_child) /\\ '
 '~$property_hook_virtual(S,ppropertydesc_first) /\\ '
 '~$property_hook_virtual(S,ppropertydesc_child)',
 '$property_hook_getter(S,ppropertydesc_first) = (ppropertydesc_parent) /\\ '
 '$property_hook_getter(S,ppropertydesc_child) = (ppropertydesc_parent) /\\ '
 '$property_hook_effective_origin(S,ppropertydesc_first) = (porigin_hook_parent) /\\ '
 '$property_hook_effective_origin(S,ppropertydesc_child) = (porigin_hook_parent)',
 '$property_hook_plain_edge(S,ppropertydesc_parent,ppropertydesc_first,|S.CLASSES|) /\\ '
 '$property_hook_plain_over_backed(S,ppropertydesc_parent,ppropertydesc_first,|S.CLASSES|) /\\ '
 '$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_first)',
 '$property_hook_plain_edge(S,ppropertydesc_first,ppropertydesc_child,|S.CLASSES|) /\\ '
 '$property_hook_plain_over_backed(S,ppropertydesc_first,ppropertydesc_child,|S.CLASSES|) /\\ '
 '$property_hook_override_pair(S,ppropertydesc_first,ppropertydesc_child) /\\ '
 '~$property_hook_plain_over_backed(S,ppropertydesc_parent,ppropertydesc_child,|S.CLASSES|) /\\ '
 '~$property_hook_override_shape(S,ppropertydesc_first,ppropertydesc_child)',
 '$property_hook_plain_getter_walk(S,ppropertydesc_first,|S.CLASSES|) = (ppropertydesc_parent) /\\ '
 '$property_hook_plain_getter_walk(S,ppropertydesc_child,|S.CLASSES|) = (ppropertydesc_parent)',
 '$property_hook_override_backed(S,ppropertydesc_parent) /\\ '
 '~$property_hook_virtual(S,ppropertydesc_parent) /\\ $rpi_guard(S)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("parentRead")) = (pmethoddesc_read)',
 '$method_named(pclassdesc_parent.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
 '$method_named(pclassdesc_first.METHODS,$ptascii("answer")) = (pmethoddesc_first_answer)',
 '$method_named(pclassdesc_child.METHODS,$ptascii("answer")) = (pmethoddesc_child_answer)',
 '$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
 'pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_answer.OWNER = porigin_parent '
 '/\\ pmethoddesc_first_answer.OWNER = porigin_first /\\ pmethoddesc_child_answer.OWNER = '
 'porigin_child /\\ pmethoddesc_grand_answer.OWNER = porigin_grand /\\ '
 'pmethoddesc_first_answer.VISIBILITY = PROPERTY_PRIVATE /\\ pmethoddesc_child_answer.VISIBILITY = '
 'PROPERTY_PRIVATE /\\ pmethoddesc_grand_answer.VISIBILITY = PROPERTY_PRIVATE /\\ '
 'pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_first_answer.FUNCTION.ORIGIN /\\ '
 'pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_child_answer.FUNCTION.ORIGIN /\\ '
 'pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_grand_answer.FUNCTION.ORIGIN',
 '$origin_node(S.SOURCES,porigin_hook_parent) = (NPropertyHook phpType14_hook phpType24_hook '
 'phpType4_hook phpType11_hook phpType16_hook phpType39_hook metadata_hook)',
 'ppropertydesc_child.ORIGIN = PORIGIN n_child pcpath_child',
 'pcpath_child_group = pcpath_child[0:$nabs($(|pcpath_child| - 2))]',
 '$origin_node(S.SOURCES,PORIGIN n_child pcpath_child_group) = (NStmtProperty phpType14_child '
 '(INTEGER flags_child) phpType18_child phpType56_child phpType37_child metadata_child)',
 'phpType14_child = SEQUENCE eps /\\ phpType37_child = SEQUENCE eps /\\ '
 '$hook_body_backed(phpType39_hook,ppropertydesc_parent.NAME)',
 'ppropertydesc_first.ORIGIN = PORIGIN n_first pcpath_first',
 'pcpath_first_group = pcpath_first[0:$nabs($(|pcpath_first| - 2))]',
 '$origin_node(S.SOURCES,PORIGIN n_first pcpath_first_group) = (NStmtProperty phpType14_first '
 '(INTEGER flags_first) phpType18_first phpType56_first phpType37_first metadata_first)',
 'phpType14_first = SEQUENCE eps /\\ phpType37_first = SEQUENCE eps /\\ flags_first <- [0,1] /\\ '
 'flags_child <- [0,1]']

CONTROLS = COMMON + ['$rpi_stage(S,0)']

ENTRY = COMMON + ['S.CURRENT = (pcallcontext_hook)',
 'pcallcontext_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook',
 'S.FRAMES = pframe_hook :: pframe_tail*',
 'S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin_child',
 'ppropertyhook.PROPERTY = ppropertydesc_child.ORIGIN /\\ ppropertyhook.HOOK = porigin_hook_parent '
 '/\\ pcallcontext_hook.FUNCTION = porigin_hook_parent /\\ pcallcontext_hook.RECEIVER = '
 '(ppropertyhook.OBJECT)',
 'pcallcontext_hook.LEXICAL_CLASS = (porigin_parent) /\\ pcallcontext_hook.CALLED_CLASS = '
 '(porigin_child)',
 '$property_hook_function(S,ppropertyhook) = (pfunction_hook)',
 'pfunction_hook.NAME = pclassdesc_parent.NAME ++ $ptascii("::$value::get") /\\ '
 'pfunction_hook.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_parent.TYPE, BYREF false} /\\ '
 'pfunction_hook.LINE = 4',
 '$property_effective_desc(S,ppropertyhook.OBJECT,$ptascii("value")) = (ppropertydesc_child)',
 '$objectprops_at(S.OBJECTPROPS,ppropertyhook.OBJECT) = ([{ DECL (ppropertydesc_child.ORIGIN), '
 'NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 300)) }])',
 '$property_hook_backing(S,ppropertyhook.OBJECT,ppropertydesc_child) /\\ '
 '~$property_hook_backing(S,ppropertyhook.OBJECT,ppropertydesc_parent)',
 '$trace_context_class(S,pcallcontext_hook) = (pclassdesc_parent.NAME) /\\ '
 '$trace_context_function(S,pcallcontext_hook) = $ptascii("$value::get") /\\ '
 '$trace_context_type(S,pcallcontext_hook) = ($ptascii("->"))',
 '$property_hook_frame(S,pcallcontext_hook,pframe_hook,ppropertyhook)',
 '$rpi_guard(S)',
 'S_answer_found = $rpi_seek(S,5,1000)',
 'S_answer_found.COMPLETION = NORMAL \\/ S_answer_found.COMPLETION = BUDGET',
 'S_answer = S_answer_found[.COMPLETION = NORMAL]',
 'S_answer.CURRENT = (pcallcontext_answer)',
 'pcallcontext_answer.FUNCTION = pmethoddesc_answer.FUNCTION.ORIGIN /\\ '
 'pcallcontext_answer.LEXICAL_CLASS = (porigin_parent) /\\ pcallcontext_answer.CALLED_CLASS = '
 '(porigin_child) /\\ pcallcontext_answer.RECEIVER = (ppropertyhook.OBJECT) /\\ '
 '$call_context_valid(S_answer,pcallcontext_answer,S_answer.CVS)',
 '$rpi_guard(S_answer)']

THIS = COMMON + ['S.CURRENT = (pcallcontext_hook)',
 'pcallcontext_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook',
 'S.FRAMES = pframe_hook :: pframe_tail*',
 'S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin_grand',
 'ppropertyhook.PROPERTY = ppropertydesc_child.ORIGIN /\\ ppropertyhook.HOOK = porigin_hook_parent '
 '/\\ pcallcontext_hook.FUNCTION = porigin_hook_parent /\\ pcallcontext_hook.RECEIVER = '
 '(ppropertyhook.OBJECT)',
 'pcallcontext_hook.LEXICAL_CLASS = (porigin_parent) /\\ pcallcontext_hook.CALLED_CLASS = '
 '(porigin_grand)',
 '$property_hook_function(S,ppropertyhook) = (pfunction_hook)',
 'pfunction_hook.NAME = pclassdesc_parent.NAME ++ $ptascii("::$value::get") /\\ '
 'pfunction_hook.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_parent.TYPE, BYREF false} /\\ '
 'pfunction_hook.LINE = 4',
 '$property_effective_desc(S,ppropertyhook.OBJECT,$ptascii("value")) = (ppropertydesc_child)',
 '$objectprops_at(S.OBJECTPROPS,ppropertyhook.OBJECT) = ([{ DECL (ppropertydesc_child.ORIGIN), '
 'NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 300)) }])',
 '$property_hook_backing(S,ppropertyhook.OBJECT,ppropertydesc_child) /\\ '
 '~$property_hook_backing(S,ppropertyhook.OBJECT,ppropertydesc_parent)',
 '$trace_context_class(S,pcallcontext_hook) = (pclassdesc_parent.NAME) /\\ '
 '$trace_context_function(S,pcallcontext_hook) = $ptascii("$value::get") /\\ '
 '$trace_context_type(S,pcallcontext_hook) = ($ptascii("->"))',
 '$property_hook_frame(S,pcallcontext_hook,pframe_hook,ppropertyhook)',
 '$rpi_guard(S)',
 'pframe_hook.CONTEXT = (pcallcontext_read)',
 'pcallcontext_read.FUNCTION = pmethoddesc_read.FUNCTION.ORIGIN /\\ '
 'pcallcontext_read.LEXICAL_CLASS = (porigin_parent) /\\ pcallcontext_read.CALLED_CLASS = '
 '(porigin_grand)',
 'S_answer_found = $rpi_seek(S,5,1000)',
 'S_answer_found.COMPLETION = NORMAL \\/ S_answer_found.COMPLETION = BUDGET',
 'S_answer = S_answer_found[.COMPLETION = NORMAL]',
 'S_answer.CURRENT = (pcallcontext_answer)',
 'pcallcontext_answer.FUNCTION = pmethoddesc_answer.FUNCTION.ORIGIN /\\ '
 'pcallcontext_answer.LEXICAL_CLASS = (porigin_parent) /\\ pcallcontext_answer.CALLED_CLASS = '
 '(porigin_grand) /\\ pcallcontext_answer.RECEIVER = (ppropertyhook.OBJECT) /\\ '
 '$call_context_valid(S_answer,pcallcontext_answer,S_answer.CVS)',
 '$rpi_guard(S_answer)']

WRITE = COMMON + ['S_write = S',
 'S_write.TODO = (ASSIGN_ARRAY pbase_write z_write b_write) :: ptask_write*',
 '$lookup(S_write.ENV,$ptascii("grand")) = (n_grand_cell)',
 'S_write.STORE[n_grand_cell] = DEFINED (POBJECT n_grand)',
 'S_write.OBJECTS[n_grand] = INSTANCE porigin_grand /\\ (HOBJECT n_grand) <- S_write.ALLOCATIONS',
 '$objectprops_at(S_write.OBJECTPROPS,n_grand) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME '
 'ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 300)) }])',
 '$property_pending_base(pbase_write) /\\ S_write.RESULT = KNOWN (PINT 400) /\\ z_write = 42 /\\ '
 '$call_task_valid(S_write,ASSIGN_ARRAY pbase_write z_write b_write) /\\ '
 '$heap_owners($heap_prune($heap_graph(S_write)),HOBJECT n_grand) = 1 /\\ $rpi_guard(S_write)',
 'PhpStep: S_write ~> S_write_raw',
 'S_write_raw.COMPLETION = NORMAL /\\ S_write_raw.RESULT = KNOWN (PINT 400) /\\ S_write_raw.EVENTS '
 '= S_write.EVENTS /\\ S_write_raw.TODO = ptask_write*',
 '$objectprops_at(S_write_raw.OBJECTPROPS,n_grand) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME '
 'ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 400)) }])',
 'S_written = $rpi_after(S_write,S_write_raw)',
 '$rpi_guard(S_written)',
 'S_entered_found = $rpi_seek(S_written,3,1000)',
 'S_entered_found.COMPLETION = NORMAL \\/ S_entered_found.COMPLETION = BUDGET',
 'S_entered = S_entered_found[.COMPLETION = NORMAL]',
 'S_entered.CURRENT = (pcallcontext_hook)',
 'pcallcontext_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook',
 'S_entered.FRAMES = pframe_hook :: pframe_tail*',
 'S_entered.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin_grand',
 'ppropertyhook.PROPERTY = ppropertydesc_child.ORIGIN /\\ ppropertyhook.HOOK = porigin_hook_parent '
 '/\\ pcallcontext_hook.FUNCTION = porigin_hook_parent /\\ pcallcontext_hook.RECEIVER = '
 '(ppropertyhook.OBJECT)',
 'pcallcontext_hook.LEXICAL_CLASS = (porigin_parent) /\\ pcallcontext_hook.CALLED_CLASS = '
 '(porigin_grand)',
 '$property_hook_function(S_entered,ppropertyhook) = (pfunction_hook)',
 'pfunction_hook.NAME = pclassdesc_parent.NAME ++ $ptascii("::$value::get") /\\ '
 'pfunction_hook.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc_parent.TYPE, BYREF false} /\\ '
 'pfunction_hook.LINE = 4',
 '$property_effective_desc(S_entered,ppropertyhook.OBJECT,$ptascii("value")) = '
 '(ppropertydesc_child)',
 '$objectprops_at(S_entered.OBJECTPROPS,ppropertyhook.OBJECT) = ([{ DECL '
 '(ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 400)) '
 '}])',
 '$property_hook_backing(S_entered,ppropertyhook.OBJECT,ppropertydesc_child) /\\ '
 '~$property_hook_backing(S_entered,ppropertyhook.OBJECT,ppropertydesc_parent)',
 '$trace_context_class(S_entered,pcallcontext_hook) = (pclassdesc_parent.NAME) /\\ '
 '$trace_context_function(S_entered,pcallcontext_hook) = $ptascii("$value::get") /\\ '
 '$trace_context_type(S_entered,pcallcontext_hook) = ($ptascii("->"))',
 '$property_hook_frame(S_entered,pcallcontext_hook,pframe_hook,ppropertyhook)',
 '$rpi_guard(S_entered)',
 'S_result_found = $rpi_seek(S_entered,4,1000)',
 'S_result_found.COMPLETION = NORMAL \\/ S_result_found.COMPLETION = BUDGET',
 'S_result = S_result_found[.COMPLETION = NORMAL]',
 'S_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask_result*',
 'S_result.RESULT = KNOWN (PINT 413) /\\ S_result.CURRENT = eps',
 '$objectprops_at(S_result.OBJECTPROPS,n_grand) = ([{ DECL (ppropertydesc_child.ORIGIN), NAME '
 'ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 400)) }])',
 '$rpi_guard(S_result)']

DERIVED = ['$property_hook_plain_getter_walk(S,ppropertydesc_child,0) = eps',
 '$property_hook_plain_getter_walk(S,ppropertydesc_child,1) = eps',
 '$property_hook_plain_getter_walk(S,ppropertydesc_child,2) = eps',
 '$property_hook_plain_getter_walk(S,ppropertydesc_child,3) = (ppropertydesc_parent)',
 '$property_hook_plain_getter_walk(S,ppropertydesc_first,1) = eps',
 '$property_hook_plain_getter_walk(S,ppropertydesc_first,2) = (ppropertydesc_parent)',
 '$property_hook_plain_getter_walk(S,ppropertydesc_parent,0) = eps',
 '$property_hook_plain_getter_walk(S,ppropertydesc_parent,1) = (ppropertydesc_parent)',
 '~$property_hook_plain_over_backed(S,ppropertydesc_first[.TYPE = '
 'eps],ppropertydesc_child,|S.CLASSES|)',
 '~$property_hook_plain_over_backed(S,ppropertydesc_first[.DEFAULT = PROP_LITERAL (PINT '
 '999)],ppropertydesc_child,|S.CLASSES|)',
 '~$property_hook_plain_over_backed(S,ppropertydesc_first[.NAME = '
 '$ptascii("other")],ppropertydesc_child,|S.CLASSES|)',
 '~$property_hook_plain_over_backed(S,ppropertydesc_first[.VISIBILITY = '
 'PROPERTY_PRIVATE],ppropertydesc_child,|S.CLASSES|)',
 '~$property_hook_plain_over_backed(S,ppropertydesc_first[.STATIC = '
 'true],ppropertydesc_child,|S.CLASSES|)',
 '~$property_hook_plain_over_backed(S,ppropertydesc_first[.READONLY = '
 'true],ppropertydesc_child,|S.CLASSES|)',
 '~$property_hook_plain_over_backed(S,ppropertydesc_first[.FINAL = '
 'true],ppropertydesc_child,|S.CLASSES|)',
 '~$property_hook_plain_over_backed(S,ppropertydesc_first[.SETVISIBILITY = '
 '(PROPERTY_PROTECTED)],ppropertydesc_child,|S.CLASSES|)',
 '~$property_hook_plain_over_backed(S,ppropertydesc_first,ppropertydesc_child[.TYPE = '
 'eps],|S.CLASSES|)',
 '~$property_hook_plain_over_backed(S,ppropertydesc_first,ppropertydesc_child[.NAME = '
 '$ptascii("other")],|S.CLASSES|)',
 '~$property_hook_plain_over_backed(S,ppropertydesc_first,ppropertydesc_child[.KEY = '
 '$ptascii("other")],|S.CLASSES|)',
 '~$property_hook_plain_over_backed(S,ppropertydesc_first,ppropertydesc_child[.DEFAULT = '
 'PROP_LITERAL (PINT 999)],|S.CLASSES|)',
 '~$property_hook_plain_over_backed(S,ppropertydesc_first,ppropertydesc_child[.VISIBILITY = '
 'PROPERTY_PRIVATE],|S.CLASSES|)',
 '~$property_hook_plain_over_backed(S,ppropertydesc_first,ppropertydesc_child[.STATIC = '
 'true],|S.CLASSES|)',
 '~$property_hook_plain_over_backed(S,ppropertydesc_first,ppropertydesc_child[.READONLY = '
 'true],|S.CLASSES|)',
 '~$property_hook_plain_over_backed(S,ppropertydesc_first,ppropertydesc_child[.FINAL = '
 'true],|S.CLASSES|)',
 '~$property_hook_plain_over_backed(S,ppropertydesc_first,ppropertydesc_child[.SETVISIBILITY = '
 '(PROPERTY_PROTECTED)],|S.CLASSES|)',
 'S_first_link = S[.LINKEDPARENTS = $rpi_link_replace(S.LINKEDPARENTS,porigin_first,SOURCE_PARENT '
 'porigin_first)]',
 '$property_hook_plain_edge(S_first_link,ppropertydesc_first,ppropertydesc_child,|S.CLASSES|)',
 '~$property_hook_plain_over_backed(S_first_link,ppropertydesc_first,ppropertydesc_child,|S.CLASSES|) '
 '/\\ $property_hook_plain_getter_walk(S_first_link,ppropertydesc_child,|S.CLASSES|) = eps',
 'S_child_link = S[.LINKEDPARENTS = $rpi_link_replace(S.LINKEDPARENTS,porigin_child,SOURCE_PARENT '
 'porigin_child)]',
 '~$property_hook_plain_over_backed(S_child_link,ppropertydesc_first,ppropertydesc_child,|S.CLASSES|)',
 'S_bridge_link = S[.LINKEDPARENTS = '
 '$rpi_link_replace(S.LINKEDPARENTS,porigin_bridge,SOURCE_PARENT porigin_bridge)]',
 '~$property_hook_plain_over_backed(S_bridge_link,ppropertydesc_first,ppropertydesc_child,|S.CLASSES|)',
 'S_child_own = S[.CLASSES = '
 '$rpi_class_replace(S.CLASSES,porigin_child,pclassdesc_child[.PROPERTIES = eps])]',
 '~$property_hook_plain_over_backed(S_child_own,ppropertydesc_first,ppropertydesc_child,|S.CLASSES|)',
 'S_first_own = S[.CLASSES = '
 '$rpi_class_replace(S.CLASSES,porigin_first,pclassdesc_first[.PROPERTIES = eps])]',
 '~$property_hook_plain_over_backed(S_first_own,ppropertydesc_first,ppropertydesc_child,|S.CLASSES|)',
 'S_parent_own = S[.CLASSES = '
 '$rpi_class_replace(S.CLASSES,porigin_parent,pclassdesc_parent[.PROPERTIES = eps])]',
 '$property_hook_plain_edge(S_parent_own,ppropertydesc_first,ppropertydesc_child,|S.CLASSES|) /\\ '
 '~$property_hook_plain_over_backed(S_parent_own,ppropertydesc_first,ppropertydesc_child,|S.CLASSES|)',
 'porigin_hook_parent = PORIGIN n_hook pcpath_hook',
 'S.SOURCES = pcunit :: pcunit_tail*',
 'pcunit.ID = n_hook',
 'S_byref = S[.SOURCES = pcunit[.OCCURRENCES = '
 '$rpi_replace(pcunit.OCCURRENCES,pcpath_hook,NPropertyHook phpType14_hook phpType24_hook (BOOLEAN '
 'true) phpType11_hook phpType16_hook phpType39_hook metadata_hook)] :: pcunit_tail*]',
 '~$property_hook_plain_over_backed(S_byref,ppropertydesc_first,ppropertydesc_child,|S.CLASSES|)',
 '$property_hook_properties(S,[ppropertydesc_child])',
 '~$property_hook_parent_match(S,ppropertydesc_child,(ppropertydesc_first))',
 '$property_hook_parent_match(S,ppropertydesc_child,(ppropertydesc_child))']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--group', choices=['controls', 'entry', 'this', 'write'], required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'repeated_plain_child_inherited_backed_get_hook_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    clauses, negatives, start_stage = {
        'controls': (CONTROLS, DERIVED, 0),
        'entry': (ENTRY, [], 0),
        'this': (THIS, [], 1),
        'write': (WRITE, [], 2),
    }[args.group]
    selections = [(args.group, clauses, negatives)]
    cases = [data['cases'][0]]
    sources = [HERE / 'repeated-plain-child-inherited-backed-get-hook.php']
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
    out = Path(tempfile.mkdtemp(prefix='repeated-plain-child-inherited-backed-get-hook-protocol-', dir=ROOT / '.tools'))
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
                     'S_found = $rpi_seek(S_initial,' + str(start_stage) + ',1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            content += '\ndec $rpi_' + name + '() : bool\ndef $rpi_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $rpi_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = (' + ' /\\ '.join('$rpi_' + name + '()' for name, _, _ in selections) + ')\n'
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
