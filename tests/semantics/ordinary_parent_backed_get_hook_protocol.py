"""Check ordinary-parent to own-backed getter storage, dispatch and payload cleanup."""
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

PREFIX = 'dec $opb_replace(pcoccurrence*,pcpath,pcnode) : pcoccurrence*\ndef $opb_replace(eps,pcpath,pcnode) = eps\ndef $opb_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath pcnode) :: pcoccurrence*\ndef $opb_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath_other pcnode_old) :: $opb_replace(pcoccurrence*,pcpath,pcnode)\n  -- if pcpath_other =/= pcpath\ndec $opb_output(pevent*) : ptbytes\ndef $opb_output(eps) = eps\ndef $opb_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $opb_output(pevent*)\ndec $opb_stage(pstate,nat) : bool\ndef $opb_stage(S,0) = true\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $property_hook_plan(S[.COMPLETION = NORMAL]) = (ppropertyhook)\n  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n  -- if $ptlc(pclassdesc.NAME) = $ptascii("ordinarybackedchild49")\ndef $opb_stage(S,1) = true\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $property_hook_plan(S[.COMPLETION = NORMAL]) = (ppropertyhook)\n  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n  -- if $ptlc(pclassdesc.NAME) = $ptascii("ordinarybackedgrand49")\n  -- if S.CURRENT = (pcallcontext)\n  -- if $ptlc(pcallcontext.NAME) = $ptascii("ordinarybackedparent49::parentread")\ndef $opb_stage(S,2) = true\n  -- if S.CURRENT = (pcallcontext)\n  -- if $property_hook_context_kind(pcallcontext)\ndef $opb_stage(S,3) = true\n  -- if S.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*\ndef $opb_stage(S,4) = true\n  -- if S.CURRENT = (pcallcontext)\n  -- if $ptlc(pcallcontext.NAME) = $ptascii("ordinarybackedchild49::answer")\ndef $opb_stage(S,5) = true\n  -- if S.TODO = (ASSIGN_ARRAY pbase z b) :: ptask*\n  -- if S.RESULT = KNOWN (PINT 300)\ndef $opb_stage(S,6) = true\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $property_hook_plan(S[.COMPLETION = NORMAL]) = (ppropertyhook)\n  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)\n  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n  -- if $ptlc(pclassdesc.NAME) = $ptascii("ordinarybackedgrand49")\ndef $opb_stage(S,7) = true\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $property_hook_plan(S[.COMPLETION = NORMAL]) = (ppropertyhook)\n  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin\n  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n  -- if $ptlc(pclassdesc.NAME) = $ptascii("ordinarybackedlifegrand49")\n  -- if S.CURRENT = (pcallcontext)\n  -- if $ptlc(pcallcontext.NAME) = $ptascii("ordinarybackedlifeparent49::parentread")\ndef $opb_stage(S,10) = true\n  -- if S.TODO = (UNSET (NExprVariable (BYTES "Ym94") metadata)) :: ptask*\ndef $opb_stage(S,11) = true\n  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*\n  -- if pdestructionoperation.SOURCE = UNSET (NExprVariable (BYTES "Ym94") metadata)\ndef $opb_stage(S,12) = true\n  -- if S.CURRENT = (pcallcontext)\n  -- if $ptlc(pcallcontext.NAME) = $ptascii("ordinarybackedlifeparent49::__destruct")\ndef $opb_stage(S,13) = true\n  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*\n  -- if S.OBJECTS[pinstancestorage.OBJECT] = INSTANCE porigin\n  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)\n  -- if $ptlc(pclassdesc.NAME) = $ptascii("ordinarybackedlifegrand49")\ndef $opb_stage(S,14) = true\n  -- if S.TODO = (UNSET (NExprVariable (BYTES "a2VwdA==") metadata)) :: ptask*\ndef $opb_stage(S,15) = true\n  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*\n  -- if pdestructionoperation.SOURCE = UNSET (NExprVariable (BYTES "a2VwdA==") metadata)\ndef $opb_stage(S,n) = false -- otherwise\n\ndec $opb_seek(pstate,nat,nat) : pstate\ndef $opb_seek(S,n_stage,n) = S\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if $opb_stage(S,n_stage) \\/ n = 0\ndef $opb_seek(S,n_stage,n) = $opb_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))\n  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n  -- if ~$opb_stage(S,n_stage) /\\ $(n > 0)\ndef $opb_seek(S,n_stage,n) = $opb_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))\n  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n  -- if $throwable_pending(S.COMPLETION) /\\ $(n > 0)\ndef $opb_seek(S,n_stage,n) = S -- otherwise\ndec $opb_after(pstate,pstate) : pstate\ndef $opb_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))\ndec $opb_guard(pstate) : bool\ndef $opb_guard(S) = ($call_descriptors_valid(S) /\\ $declaration_history_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_prune($heap_graph(S))))\ndec $opb_slot(pstate,nat,ptbytes) : ppropstate?\ndef $opb_slot(S,n,ptbytes) = (ppropertyslot_value.STATE)\n  -- if $objectprops_at(S.OBJECTPROPS,n) = (ppropertyslot*)\n  -- if $property_slot_at(ppropertyslot*,ptbytes) = (ppropertyslot_value)\ndef $opb_slot(S,n,ptbytes) = eps -- otherwise\ndec $opb_class_replace(pclassdesc*,porigin,pclassdesc) : pclassdesc*\ndef $opb_class_replace(eps,porigin,pclassdesc) = eps\ndef $opb_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_new :: pclassdesc*\n  -- if pclassdesc_old.ORIGIN = porigin\ndef $opb_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_old :: $opb_class_replace(pclassdesc*,porigin,pclassdesc_new)\n  -- if pclassdesc_old.ORIGIN =/= porigin\ndec $opb_link_replace(pclasslink*,porigin,pclassparent) : pclasslink*\ndef $opb_link_replace(eps,porigin,pclassparent) = eps\ndef $opb_link_replace((CLASSLINK porigin pclassparent_old) :: pclasslink*,porigin,pclassparent) = (CLASSLINK porigin pclassparent) :: pclasslink*\ndef $opb_link_replace((CLASSLINK porigin_other pclassparent_old) :: pclasslink*,porigin,pclassparent) = (CLASSLINK porigin_other pclassparent_old) :: $opb_link_replace(pclasslink*,porigin,pclassparent)\n  -- if porigin_other =/= porigin\n'

def reach(name, previous, stage):
    return [f'{name}_found = $opb_seek({previous},{stage},1000)',
            fr'{name}_found.COMPLETION = NORMAL \/ {name}_found.COMPLETION = BUDGET',
            f'{name} = {name}_found[.COMPLETION = NORMAL]']

def slot(s, receiver, value):
    return f'$objectprops_at({s}.OBJECTPROPS,{receiver}) = ([{{ DECL (ppropertydesc_child.ORIGIN), NAME ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT {value})) }}])'

def prep(s, called, owners, value=200):
    return [f'$property_hook_plan({s}) = (ppropertyhook_{s})',
            f'{s}.TODO = (PROPERTY_PREP phpType20_{s} z_{s}) :: (DIM_FETCH z_{s}) :: ptask_{s}*',
            f'$property_effective_desc({s},ppropertyhook_{s}.OBJECT,$ptascii("value")) = (ppropertydesc_{s})',
            f'$property_hook_function({s},ppropertyhook_{s}) = (pfunction_{s})',
            fr'{s}.OBJECTS[ppropertyhook_{s}.OBJECT] = INSTANCE porigin_{called} /\ ppropertydesc_{s} = ppropertydesc_child /\ ppropertyhook_{s}.PROPERTY = ppropertydesc_child.ORIGIN /\ pfunction_{s}.SIGNATURE.RETURNS = ppropertydesc_child.TYPE',
            fr'$target_lexical_class({s},PROPERTY_HOOK_TARGET ppropertyhook_{s}) = (porigin_child) /\ $target_called_class({s},PROPERTY_HOOK_TARGET ppropertyhook_{s}) = (porigin_{called}) /\ ~$property_hook_backing({s},ppropertyhook_{s}.OBJECT,ppropertydesc_child)',
            slot(s, f'ppropertyhook_{s}.OBJECT', value),
            fr'$heap_owners($heap_prune($heap_graph({s})),HOBJECT ppropertyhook_{s}.OBJECT) = {owners} /\ $opb_guard({s})']

def call(s, called, owners, value=200):
    return [f'PhpStep: {s} ~> {s}_call_raw',
            f'{s}_call_raw.TODO = [(CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook_{s}) eps 0 eps (ppropertyhook_{s}.SITE) z_{s}), PROPERTY_HOOK_RESULT ppropertyhook_{s}] ++ ptask_{s}*',
            fr'{s}_call_raw.RESULT = KNOWN PNULL /\ {s}_call_raw.EVENTS = {s}.EVENTS /\ {s}_call_raw.OBJECTPROPS = {s}.OBJECTPROPS',
            f'{s}_call = $opb_after({s},{s}_call_raw)',
            fr'$property_hook_pending_call({s}_call,ppropertyhook_{s}) /\ $heap_owners($heap_prune($heap_graph({s}_call)),HOBJECT ppropertyhook_{s}.OBJECT) = {owners} /\ $opb_guard({s}_call)',
            *reach(s+'_entered', s+'_call', 2),
            f'{s}_entered.CURRENT = (pcallcontext_hook_{s})',
            f'{s}_entered.FRAMES = pframe_{s} :: pframe_tail_{s}*',
            fr'pframe_{s}.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_{s}) :: ptask_{s}* /\ pcallcontext_hook_{s}.TARGET = PROPERTY_HOOK_TARGET ppropertyhook_{s} /\ pcallcontext_hook_{s}.FUNCTION = ppropertyhook_{s}.HOOK /\ pcallcontext_hook_{s}.RECEIVER = (ppropertyhook_{s}.OBJECT)',
            fr'pcallcontext_hook_{s}.LEXICAL_CLASS = (porigin_child) /\ pcallcontext_hook_{s}.CALLED_CLASS = (porigin_{called}) /\ pfunction_{s}.NAME = pclassdesc_child.NAME ++ $ptascii("::$value::get") /\ $property_hook_frame({s}_entered,pcallcontext_hook_{s},pframe_{s},ppropertyhook_{s})',
            fr'$property_hook_backing({s}_entered,ppropertyhook_{s}.OBJECT,ppropertydesc_{s}) /\ $heap_owners($heap_prune($heap_graph({s}_entered)),HOBJECT ppropertyhook_{s}.OBJECT) = {owners} /\ $opb_guard({s}_entered)',
            slot(s+'_entered', f'ppropertyhook_{s}.OBJECT', value)]

def answer(s, called, value=200):
    return [*reach(s+'_answer', s+'_entered', 4),
            f'{s}_answer.CURRENT = (pcallcontext_answer_{s})',
            fr'pcallcontext_answer_{s}.FUNCTION = pmethoddesc_answer.FUNCTION.ORIGIN /\ pcallcontext_answer_{s}.LEXICAL_CLASS = (porigin_child) /\ pcallcontext_answer_{s}.CALLED_CLASS = (porigin_{called}) /\ pcallcontext_answer_{s}.RECEIVER = (ppropertyhook_{s}.OBJECT) /\ $call_context_valid({s}_answer,pcallcontext_answer_{s},{s}_answer.CVS)',
            slot(s+'_answer', f'ppropertyhook_{s}.OBJECT', value)]

def returned(s, previous, result, slot_value, caller=False):
    return [*reach(s+'_result', previous, 3),
            fr'{s}_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_{s}) :: ptask_{s}* /\ {s}_result.RESULT = KNOWN (PINT {result}) /\ {s}_result.CURRENT = {"(pcallcontext_read)" if caller else "eps"}',
            slot(s+'_result', f'ppropertyhook_{s}.OBJECT', slot_value),
            fr'$heap_owners($heap_prune($heap_graph({s}_result)),HOBJECT ppropertyhook_{s}.OBJECT) = {2 if caller else 1} /\ $task_nodes(PROPERTY_HOOK_RESULT ppropertyhook_{s}) = eps /\ ~$property_hook_backing({s}_result,ppropertyhook_{s}.OBJECT,ppropertydesc_child) /\ $opb_guard({s}_result)',
            f'PhpStep: {s}_result ~> {s}_base_raw',
            fr'{s}_base_raw.RESULT = {s}_result.RESULT /\ {s}_base_raw.BASE = BASE_VALUE {s}_result.RESULT /\ {s}_base_raw.TODO = ptask_{s}* /\ {s}_base_raw.EVENTS = {s}_result.EVENTS /\ {s}_base_raw.OBJECTPROPS = {s}_result.OBJECTPROPS',
            f'{s}_base = $opb_after({s}_result,{s}_base_raw)',
            f'$opb_guard({s}_base)']


def classes(stem='OrdinaryBacked', lifetime=False):
    clauses = []
    for suffix,name in [('Parent','parent'),('Bridge','bridge'),('Child','child'),('Grand','grand')]:
        clauses += [f'$class_named(S.CLASSNAMES,$ptlc($ptascii("{stem}{suffix}49"))) = (porigin_{name})',
                    f'$class_at(S.CLASSES,porigin_{name}) = (pclassdesc_{name})']
    clauses += [
        r'$class_link_at(S.LINKEDPARENTS,porigin_parent) = eps /\ $class_link_at(S.LINKEDPARENTS,porigin_bridge) = (SOURCE_PARENT porigin_parent) /\ $class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_bridge) /\ $class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_child)',
        r'|pclassdesc_parent.PROPERTIES| = 1 /\ |pclassdesc_child.PROPERTIES| = 1 /\ pclassdesc_bridge.PROPERTIES = eps /\ pclassdesc_grand.PROPERTIES = eps',
        'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
        'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
        f'ppropertydesc_parent.TYPE = [PTBRANCH ([PTBUILTIN "{"mixed" if lifetime else "int"}"])] /\\ ppropertydesc_child.TYPE = ppropertydesc_parent.TYPE /\\ $property_default_state(S,ppropertydesc_parent) = (PROP_VALUE (DIRECT ({"PNULL" if lifetime else "PINT 100"}))) /\\ $property_default_state(S,ppropertydesc_child) = (PROP_VALUE (DIRECT ({"PNULL" if lifetime else "PINT 200"})))',
        r'$property_layout(S,porigin_bridge,|S.CLASSES|) = [ppropertydesc_parent] /\ $property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_child]',
        r'$property_hook_origin(S,ppropertydesc_parent) = eps /\ ~$property_hook_virtual(S,ppropertydesc_parent) /\ ~$property_hook_override_backed(S,ppropertydesc_parent) /\ ~$property_hook_virtual_chain(S,ppropertydesc_parent,|S.CLASSES|)',
        r'$property_hook_override_backed(S,ppropertydesc_child) /\ ~$property_hook_virtual(S,ppropertydesc_child) /\ ~$property_hook_inherited_backing(S,ppropertydesc_child) /\ ~$property_hook_virtual_chain(S,ppropertydesc_child,|S.CLASSES|)',
        r'$property_hook_backed_over_ordinary(S,ppropertydesc_parent,ppropertydesc_child) /\ $property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child) /\ ~$property_hook_override_shape(S,ppropertydesc_parent,ppropertydesc_child) /\ ~$property_hook_backed_over_virtual(S,ppropertydesc_parent,ppropertydesc_child) /\ $opb_guard(S)',
        '$method_named(pclassdesc_parent.METHODS,$ptascii("parentRead")) = (pmethoddesc_read)',
    ]
    if lifetime:
        return clauses + ['$method_named(pclassdesc_parent.METHODS,$ptascii("__destruct")) = (pmethoddesc_destructor)']
    return clauses + [
        '$method_named(pclassdesc_child.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
        '$method_named(pclassdesc_bridge.METHODS,$ptascii("answer")) = (pmethoddesc_bridge_answer)',
        '$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
        r'pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\ pmethoddesc_answer.OWNER = porigin_child /\ pmethoddesc_bridge_answer.VISIBILITY = PROPERTY_PRIVATE /\ pmethoddesc_grand_answer.VISIBILITY = PROPERTY_PRIVATE /\ pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_bridge_answer.FUNCTION.ORIGIN /\ pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_grand_answer.FUNCTION.ORIGIN',
    ]


CV = classes() + [
    'S_globals = $global_table_view(S)',
    '$lookup(S_globals.ENV,$ptascii("parent")) = (n_parent_cell)',
    'S.STORE[n_parent_cell] = DEFINED (POBJECT n_parent)',
    r'S.OBJECTS[n_parent] = INSTANCE porigin_parent /\ $objectprops_at(S.OBJECTPROPS,n_parent) = ([{ DECL (ppropertydesc_parent.ORIGIN), NAME ppropertydesc_parent.KEY, STATE PROP_VALUE (DIRECT (PINT 100)) }])',
    'S_child = S',
] + prep('S_child','child',1) + call('S_child','child',2) + answer('S_child','child') + returned('S_child','S_child_answer',213,200)
THIS = classes() + ['S_this = S'] + prep('S_this','grand',3) + [
    'S_this.CURRENT = (pcallcontext_read)',
    r'pcallcontext_read.FUNCTION = pmethoddesc_read.FUNCTION.ORIGIN /\ pcallcontext_read.LEXICAL_CLASS = (porigin_parent) /\ pcallcontext_read.CALLED_CLASS = (porigin_grand) /\ $this_receiver(S_this) = (ppropertyhook_S_this.OBJECT)',
] + call('S_this','grand',3) + answer('S_this','grand') + returned('S_this','S_this_answer',213,200,True)
WRITE = classes() + [
    'S_write = S',
    'S_write.TODO = (ASSIGN_ARRAY pbase_write z_write b_write) :: ptask_write*',
    '$lookup(S_write.ENV,$ptascii("grand")) = (n_grand_cell)',
    'S_write.STORE[n_grand_cell] = DEFINED (POBJECT n_grand)',
    r'S_write.OBJECTS[n_grand] = INSTANCE porigin_grand /\ (HOBJECT n_grand) <- S_write.ALLOCATIONS',
    slot('S_write','n_grand',200),
    r'$property_pending_base(pbase_write) /\ S_write.RESULT = KNOWN (PINT 300) /\ z_write = 34 /\ $call_task_valid(S_write,ASSIGN_ARRAY pbase_write z_write b_write) /\ $heap_owners($heap_prune($heap_graph(S_write)),HOBJECT n_grand) = 1 /\ $opb_guard(S_write)',
    'PhpStep: S_write ~> S_write_raw',
    r'S_write_raw.COMPLETION = NORMAL /\ S_write_raw.RESULT = KNOWN (PINT 300) /\ S_write_raw.EVENTS = S_write.EVENTS /\ S_write_raw.TODO = ptask_write*',
    slot('S_write_raw','n_grand',300),
    'S_written = $opb_after(S_write,S_write_raw)',
    '$opb_guard(S_written)',
    *reach('S_after_write','S_written',6),
] + prep('S_after_write','grand',1,300) + returned('S_after_write','S_after_write',313,300) + [
    'ppropertyhook_S_after_write.OBJECT = n_grand',
    'S_done = $drive_steps(S_after_write_base,10000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $opb_output(S_done.EVENTS) = EXPECTED_OUTPUT /\ $opb_guard(S_done)',
    slot('S_done','n_grand',300),
]

DERIVED = ['~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.TYPE = eps]) /\\ '
 '~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.TYPE = [PTBRANCH ([PTBUILTIN '
 '"string"])]]) /\\ ~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.ORIGIN = '
 'ppropertydesc_parent.ORIGIN]) /\\ '
 '~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.NAME = $ptascii("wrong")])',
 '~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.DEFAULT = PROP_NULL]) /\\ '
 '~$property_hook_override_pair(S,ppropertydesc_parent[.DEFAULT = PROP_NULL],ppropertydesc_child)',
 '~$property_hook_override_pair(S,ppropertydesc_parent[.VISIBILITY = '
 'PROPERTY_PROTECTED],ppropertydesc_child) /\\ ~$property_hook_override_pair(S,ppropertydesc_parent[.STATIC '
 '= true],ppropertydesc_child) /\\ ~$property_hook_override_pair(S,ppropertydesc_parent[.READONLY = '
 'true],ppropertydesc_child) /\\ ~$property_hook_override_pair(S,ppropertydesc_parent[.FINAL = '
 'true],ppropertydesc_child) /\\ ~$property_hook_override_pair(S,ppropertydesc_parent[.SETVISIBILITY = '
 '(PROPERTY_PROTECTED)],ppropertydesc_child)',
 '~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.FINAL = true]) /\\ '
 '~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.SETVISIBILITY = '
 '(PROPERTY_PROTECTED)]) /\\ '
 '~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.READONLY = true]) /\\ '
 '~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.VISIBILITY = '
 'PROPERTY_PROTECTED])',
 '~$property_hook_backed_over_ordinary(S[.CLASSES = eps],ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_override_pair(S[.SOURCES = eps],ppropertydesc_parent,ppropertydesc_child)',
 'S_bad_child = S[.LINKEDPARENTS = $opb_link_replace(S.LINKEDPARENTS,porigin_child,STDCLASS_PARENT)]',
 '~$property_hook_backed_over_ordinary(S_bad_child,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_override_pair(S_bad_child,ppropertydesc_parent,ppropertydesc_child)',
 'S_bad_bridge = S[.LINKEDPARENTS = $opb_link_replace(S.LINKEDPARENTS,porigin_bridge,STDCLASS_PARENT)]',
 '~$property_hook_backed_over_ordinary(S_bad_bridge,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_override_pair(S_bad_bridge,ppropertydesc_parent,ppropertydesc_child)',
 'S_wrong_own = S[.CLASSES = $opb_class_replace(S.CLASSES,porigin_child,pclassdesc_child[.PROPERTIES = '
 '[ppropertydesc_child[.TYPE = eps]]])]',
 '~$property_hook_backed_over_ordinary(S_wrong_own,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_override_pair(S_wrong_own,ppropertydesc_parent,ppropertydesc_child)',
 'S_no_parent = S[.CLASSES = $opb_class_replace(S.CLASSES,porigin_parent,pclassdesc_parent[.PROPERTIES = '
 'eps])]',
 '~$property_hook_backed_over_ordinary(S_no_parent,ppropertydesc_parent,ppropertydesc_child) /\\ '
 '~$property_hook_override_pair(S_no_parent,ppropertydesc_parent,ppropertydesc_child)',
 'S.SOURCES = pcunit :: pcunit_tail*',
 'ppropertydesc_parent.ORIGIN = PORIGIN n_unit pcpath_parent_property',
 'pcpath_parent_group = pcpath_parent_property[0:$nabs($(|pcpath_parent_property| - 2))]',
 'pcpath_parent_property = pcpath_parent_group ++ [PCFIELD 3, PCINDEX 0]',
 '$origin_node(S.SOURCES,PORIGIN n_unit pcpath_parent_group) = (NStmtProperty phpType14_parent (INTEGER '
 'flags_parent) phpType18_parent phpType56_parent phpType37_parent metadata_parent)',
 'phpType14_parent = SEQUENCE eps /\\ phpType37_parent = SEQUENCE eps /\\ flags_parent <- [0,1]',
 'ppropertyhook_S_child.HOOK = PORIGIN n_unit pcpath_child_hook',
 'pcunit.ID = n_unit',
 '$origin_node(S.SOURCES,ppropertyhook_S_child.HOOK) = (NPropertyHook phpType14_child phpType24_child '
 'phpType4_child phpType11_child phpType16_child phpType39_child metadata_child)',
 'S_parent_attrs = S[.SOURCES = pcunit[.OCCURRENCES = '
 '$opb_replace(pcunit.OCCURRENCES,pcpath_parent_group,NStmtProperty (SEQUENCE ([NAttributeGroup (SEQUENCE '
 'eps) metadata_parent])) (INTEGER flags_parent) phpType18_parent phpType56_parent phpType37_parent '
 'metadata_parent)] :: pcunit_tail*]',
 '~$property_hook_override_pair(S_parent_attrs,ppropertydesc_parent,ppropertydesc_child)',
 'S_parent_flags = S[.SOURCES = pcunit[.OCCURRENCES = '
 '$opb_replace(pcunit.OCCURRENCES,pcpath_parent_group,NStmtProperty phpType14_parent (INTEGER 9) '
 'phpType18_parent phpType56_parent phpType37_parent metadata_parent)] :: pcunit_tail*]',
 '~$property_hook_override_pair(S_parent_flags,ppropertydesc_parent,ppropertydesc_child)',
 'S_parent_hook = S[.SOURCES = pcunit[.OCCURRENCES = '
 '$opb_replace(pcunit.OCCURRENCES,pcpath_parent_group,NStmtProperty phpType14_parent (INTEGER flags_parent) '
 'phpType18_parent phpType56_parent (SEQUENCE ([NPropertyHook phpType14_child phpType24_child phpType4_child '
 'phpType11_child phpType16_child phpType39_child metadata_child])) metadata_parent)] :: pcunit_tail*]',
 '~$property_hook_backed_over_ordinary(S_parent_hook,ppropertydesc_parent,ppropertydesc_child)',
 'S_child_byref = S[.SOURCES = pcunit[.OCCURRENCES = '
 '$opb_replace(pcunit.OCCURRENCES,pcpath_child_hook,NPropertyHook phpType14_child phpType24_child (BOOLEAN '
 'true) phpType11_child phpType16_child phpType39_child metadata_child)] :: pcunit_tail*]',
 '~$property_hook_override_pair(S_child_byref,ppropertydesc_parent,ppropertydesc_child)',
 'S_child_attrs = S[.SOURCES = pcunit[.OCCURRENCES = '
 '$opb_replace(pcunit.OCCURRENCES,pcpath_child_hook,NPropertyHook (SEQUENCE ([NAttributeGroup (SEQUENCE eps) '
 'metadata_child])) phpType24_child phpType4_child phpType11_child phpType16_child phpType39_child '
 'metadata_child)] :: pcunit_tail*]',
 '~$property_hook_override_pair(S_child_attrs,ppropertydesc_parent,ppropertydesc_child)',
 'S_child_name = S[.SOURCES = pcunit[.OCCURRENCES = '
 '$opb_replace(pcunit.OCCURRENCES,pcpath_child_hook,NPropertyHook phpType14_child phpType24_child '
 'phpType4_child (NIdentifier (BYTES "c2V0") metadata_child) phpType16_child phpType39_child '
 'metadata_child)] :: pcunit_tail*]',
 '~$property_hook_override_pair(S_child_name,ppropertydesc_parent,ppropertydesc_child)',
 'S_child_args = S[.SOURCES = pcunit[.OCCURRENCES = '
 '$opb_replace(pcunit.OCCURRENCES,pcpath_child_hook,NPropertyHook phpType14_child phpType24_child '
 'phpType4_child phpType11_child (SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN false) '
 '(BOOLEAN false) (NExprVariable (BYTES "eA==") metadata_child) ABSENT (SEQUENCE eps) metadata_child])) '
 'phpType39_child metadata_child)] :: pcunit_tail*]',
 '~$property_hook_override_pair(S_child_args,ppropertydesc_parent,ppropertydesc_child)',
 'S_child_unbacked = S[.SOURCES = pcunit[.OCCURRENCES = '
 '$opb_replace(pcunit.OCCURRENCES,pcpath_child_hook,NPropertyHook phpType14_child phpType24_child '
 'phpType4_child phpType11_child phpType16_child (SEQUENCE eps) metadata_child)] :: pcunit_tail*]',
 '~$property_hook_override_backed(S_child_unbacked,ppropertydesc_child) /\\ '
 '~$property_hook_override_pair(S_child_unbacked,ppropertydesc_parent,ppropertydesc_child)',
 '~$property_slots_valid(S,[ppropertydesc_parent],[{ DECL (ppropertydesc_child.ORIGIN), NAME '
 'ppropertydesc_parent.KEY, STATE PROP_VALUE (DIRECT (PINT 100)) }]) /\\ '
 '~$property_slots_valid(S,[ppropertydesc_child],[{ DECL (ppropertydesc_parent.ORIGIN), NAME '
 'ppropertydesc_child.KEY, STATE PROP_VALUE (DIRECT (PINT 200)) }])',
 'S_rollback = $property_hook_link_finish(S,pclassdesc_child,S_bad_child)',
 'S_rollback.COMPLETION = UNSUPPORTED "inherited property hook override" /\\ S_rollback.LINKEDPARENTS = '
 'S.LINKEDPARENTS /\\ S_rollback.CLASSNAMES = S.CLASSNAMES /\\ S_rollback.OBJECTPROPS = S.OBJECTPROPS']

LIFETIME = classes("OrdinaryBackedLife",True) + [
    'S_life = S',
    '$property_hook_plan(S_life) = (ppropertyhook_S_life)',
    '$opb_slot(S_life,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (POBJECT n_stored)))',
    'S_life.TODO = (PROPERTY_PREP phpType20_S_life z_S_life) :: (DIM_FETCH z_S_life) :: ptask_S_life*',
    '$property_effective_desc(S_life,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (ppropertydesc_S_life)',
    '$property_hook_function(S_life,ppropertyhook_S_life) = (pfunction_S_life)',
    'S_life.OBJECTS[ppropertyhook_S_life.OBJECT] = INSTANCE porigin_grand /\\ ppropertydesc_S_life = ppropertydesc_child /\\ pfunction_S_life.SIGNATURE.RETURNS = ppropertydesc_child.TYPE /\\ ppropertyhook_S_life.PROPERTY = ppropertydesc_child.ORIGIN /\\ $property_declaring_class(S_life.CLASSES,ppropertyhook_S_life.PROPERTY) = (porigin_child) /\\ $property_layout(S_life,porigin_grand,|S_life.CLASSES|) = [ppropertydesc_child]',
    '$target_lexical_class(S_life,PROPERTY_HOOK_TARGET ppropertyhook_S_life) = (porigin_child) /\\ $target_called_class(S_life,PROPERTY_HOOK_TARGET ppropertyhook_S_life) = (porigin_grand) /\\ $opb_slot(S_life,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (POBJECT n_stored))) /\\ $opb_guard(S_life)',
    'S_life.CURRENT = (pcallcontext_read)',
    'pcallcontext_read.FUNCTION = pmethoddesc_read.FUNCTION.ORIGIN /\\ pcallcontext_read.LEXICAL_CLASS = (porigin_parent) /\\ pcallcontext_read.CALLED_CLASS = (porigin_grand) /\\ $heap_owners($heap_prune($heap_graph(S_life)),HOBJECT ppropertyhook_S_life.OBJECT) = 3 /\\ $heap_owners($heap_prune($heap_graph(S_life)),HOBJECT n_stored) = 1 /\\ $opb_output(S_life.EVENTS) = $ptascii("NULL_SLOT|STORED|")',
    'PhpStep: S_life ~> S_life_call_raw',
    'S_life_call_raw.TODO = [(CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook_S_life) eps 0 eps (ppropertyhook_S_life.SITE) z_S_life), PROPERTY_HOOK_RESULT ppropertyhook_S_life] ++ ptask_S_life*',
    'S_life_call = $opb_after(S_life,S_life_call_raw)',
    '$heap_owners($heap_prune($heap_graph(S_life_call)),HOBJECT ppropertyhook_S_life.OBJECT) = 3 /\\ $heap_owners($heap_prune($heap_graph(S_life_call)),HOBJECT n_stored) = 1 /\\ $property_hook_pending_call(S_life_call,ppropertyhook_S_life) /\\ $opb_guard(S_life_call)',
    'S_life_entered_found = $opb_seek(S_life_call,2,1000)',
    'S_life_entered_found.COMPLETION = NORMAL \\/ S_life_entered_found.COMPLETION = BUDGET',
    'S_life_entered = S_life_entered_found[.COMPLETION = NORMAL]',
    'S_life_entered.CURRENT = (pcallcontext_hook_S_life)',
    'S_life_entered.FRAMES = pframe_S_life :: pframe_tail_S_life*',
    'pframe_S_life.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_S_life) :: ptask_S_life* /\\ pcallcontext_hook_S_life.TARGET = PROPERTY_HOOK_TARGET ppropertyhook_S_life /\\ pcallcontext_hook_S_life.FUNCTION = ppropertyhook_S_life.HOOK /\\ pcallcontext_hook_S_life.RECEIVER = (ppropertyhook_S_life.OBJECT)',
    'pcallcontext_hook_S_life.LEXICAL_CLASS = (porigin_child) /\\ pcallcontext_hook_S_life.CALLED_CLASS = (porigin_grand) /\\ pfunction_S_life.NAME = pclassdesc_child.NAME ++ $ptascii("::$value::get") /\\ $property_hook_frame(S_life_entered,pcallcontext_hook_S_life,pframe_S_life,ppropertyhook_S_life) /\\ $property_hook_backing(S_life_entered,ppropertyhook_S_life.OBJECT,ppropertydesc_S_life) /\\ $opb_guard(S_life_entered)',
    'pframe_S_life.CONTEXT = (pcallcontext_read) /\\ $heap_owners($heap_prune($heap_graph(S_life_entered)),HOBJECT ppropertyhook_S_life.OBJECT) = 3 /\\ $heap_owners($heap_prune($heap_graph(S_life_entered)),HOBJECT n_stored) = 1',
    'S_result_found = $opb_seek(S_life_entered,3,1000)',
    'S_result_found.COMPLETION = NORMAL \\/ S_result_found.COMPLETION = BUDGET',
    'S_result = S_result_found[.COMPLETION = NORMAL]',
    'S_result.RESULT = KNOWN (POBJECT n_returned)',
    'S_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_S_life) :: ptask_S_life* /\\ S_result.CURRENT = (pcallcontext_read) /\\ n_returned =/= n_stored /\\ $heap_owners($heap_prune($heap_graph(S_result)),HOBJECT n_returned) = 1 /\\ $heap_owners($heap_prune($heap_graph(S_result)),HOBJECT n_stored) = 1 /\\ $heap_owners($heap_prune($heap_graph(S_result)),HOBJECT ppropertyhook_S_life.OBJECT) = 2 /\\ $task_nodes(PROPERTY_HOOK_RESULT ppropertyhook_S_life) = eps /\\ $opb_guard(S_result)',
    '$opb_slot(S_result,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (POBJECT n_stored))) /\\ (HOBJECT n_stored) <- $node_children(S_result,HOBJECT ppropertyhook_S_life.OBJECT) /\\ ~((HOBJECT n_returned) <- $node_children(S_result,HOBJECT ppropertyhook_S_life.OBJECT))',
    'S_result.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("weak_returned")) = (n_weak_returned_cell)',
    'S_result.STORE[n_weak_returned_cell] = DEFINED (POBJECT n_weak_returned)',
    '$lookup(psymboltable_global.ENV,$ptascii("weak_stored")) = (n_weak_stored_cell)',
    'S_result.STORE[n_weak_stored_cell] = DEFINED (POBJECT n_weak_stored)',
    '$lookup(psymboltable_global.ENV,$ptascii("weak_box")) = (n_weak_box_cell)',
    'S_result.STORE[n_weak_box_cell] = DEFINED (POBJECT n_weak_box)',
    '$weakref_get(S_result,n_weak_returned) = POBJECT n_returned /\\ $weakref_get(S_result,n_weak_stored) = POBJECT n_stored /\\ $weakref_get(S_result,n_weak_box) = POBJECT ppropertyhook_S_life.OBJECT /\\ $opb_output(S_result.EVENTS) = $ptascii("NULL_SLOT|STORED|CS|GR|")',
    'PhpStep: S_result ~> S_base_raw',
    'S_base_raw.RESULT = KNOWN (POBJECT n_returned) /\\ S_base_raw.BASE = BASE_VALUE (KNOWN (POBJECT n_returned)) /\\ S_base_raw.TODO = ptask_S_life* /\\ S_base_raw.EVENTS = S_result.EVENTS /\\ $heap_owners($heap_prune($heap_graph(S_base_raw)),HOBJECT n_returned) = 2 /\\ $heap_owners($heap_prune($heap_graph(S_base_raw)),HOBJECT n_stored) = 1',
    'S_base = $opb_after(S_result,S_base_raw)',
    '$heap_owners($heap_prune($heap_graph(S_base)),HOBJECT n_returned) = 2 /\\ $heap_owners($heap_prune($heap_graph(S_base)),HOBJECT n_stored) = 1 /\\ $opb_guard(S_base)',
    'S_box_unset_found = $opb_seek(S_base,10,1000)',
    'S_box_unset_found.COMPLETION = NORMAL \\/ S_box_unset_found.COMPLETION = BUDGET',
    'S_box_unset = S_box_unset_found[.COMPLETION = NORMAL]',
    '$lookup(S_box_unset.ENV,$ptascii("kept")) = (n_kept_cell)',
    'S_box_unset.STORE[n_kept_cell] = DEFINED (POBJECT n_returned)',
    '$heap_owners($heap_prune($heap_graph(S_box_unset)),HOBJECT n_returned) = 1 /\\ $heap_owners($heap_prune($heap_graph(S_box_unset)),HOBJECT n_stored) = 1 /\\ $opb_output(S_box_unset.EVENTS) = $ptascii("NULL_SLOT|STORED|CS|GR|HR|SLOT_S|") /\\ $opb_slot(S_box_unset,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (POBJECT n_stored))) /\\ $opb_guard(S_box_unset)',
    'PhpStep: S_box_unset ~> S_box_raw',
    '$lookup(S_box_raw.ENV,$ptascii("box")) = eps /\\ $heap_owners($heap_prune($heap_graph(S_box_raw)),HOBJECT ppropertyhook_S_life.OBJECT) = 0 /\\ S_box_raw.EVENTS = S_box_unset.EVENTS',
    'S_box_release = $opb_after(S_box_unset,S_box_raw)',
    'S_destructor_found = $opb_seek(S_box_release,12,1000)',
    'S_destructor_found.COMPLETION = NORMAL \\/ S_destructor_found.COMPLETION = BUDGET',
    'S_destructor = S_destructor_found[.COMPLETION = NORMAL]',
    'S_destructor.CURRENT = (pcallcontext_destructor)',
    'pcallcontext_destructor.FUNCTION = pmethoddesc_destructor.FUNCTION.ORIGIN /\\ pcallcontext_destructor.LEXICAL_CLASS = (porigin_parent) /\\ pcallcontext_destructor.CALLED_CLASS = (porigin_grand) /\\ pcallcontext_destructor.RECEIVER = (ppropertyhook_S_life.OBJECT) /\\ $opb_slot(S_destructor,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (POBJECT n_stored))) /\\ $opb_guard(S_destructor)',
    'S_storage_found = $opb_seek(S_destructor,13,1000)',
    'S_storage_found.COMPLETION = NORMAL \\/ S_storage_found.COMPLETION = BUDGET',
    'S_storage = S_storage_found[.COMPLETION = NORMAL]',
    'S_storage.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_storage*',
    'pinstancestorage.OBJECT = ppropertyhook_S_life.OBJECT /\\ pinstancestorage.NEXT = 0 /\\ $instance_storage_valid(S_storage,pinstancestorage) /\\ $opb_slot(S_storage,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (POBJECT n_stored))) /\\ $heap_owners($heap_prune($heap_graph(S_storage)),HOBJECT n_stored) = 1 /\\ $heap_owners($heap_prune($heap_graph(S_storage)),HOBJECT n_returned) = 1 /\\ $opb_output(S_storage.EVENTS) = $ptascii("NULL_SLOT|STORED|CS|GR|HR|SLOT_S|BS|") /\\ $opb_guard(S_storage)',
    'PhpStep: S_storage ~> S_slot_raw',
    'S_slot_raw.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_slot) :: (INSTANCE_STORAGE_STEP pinstancestorage_next) :: ptask_storage*',
    'pinstancestorage_next = pinstancestorage[.NEXT = 1] /\\ pdestructionrelease_slot.JOBS = [DESTRUCTION_VALUE (HOBJECT n_stored)] /\\ $opb_slot(S_slot_raw,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (PROP_UNSET) /\\ $heap_owners($heap_prune($heap_graph(S_slot_raw)),HOBJECT n_stored) = 1 /\\ $heap_owners($heap_prune($heap_graph(S_slot_raw)),HOBJECT n_returned) = 1 /\\ S_slot_raw.EVENTS = S_storage.EVENTS',
    'S_slot_release = $opb_after(S_storage,S_slot_raw)',
    'S_box_disposed_found = $opb_seek(S_slot_release,11,1000)',
    'S_box_disposed_found.COMPLETION = NORMAL \\/ S_box_disposed_found.COMPLETION = BUDGET',
    'S_box_disposed = S_box_disposed_found[.COMPLETION = NORMAL]',
    '~((HOBJECT ppropertyhook_S_life.OBJECT) <- S_box_disposed.ALLOCATIONS) /\\ ~((HOBJECT n_stored) <- S_box_disposed.ALLOCATIONS) /\\ (HOBJECT n_returned) <- S_box_disposed.ALLOCATIONS /\\ $weakref_get(S_box_disposed,n_weak_box) = PNULL /\\ $weakref_get(S_box_disposed,n_weak_stored) = PNULL /\\ $weakref_get(S_box_disposed,n_weak_returned) = POBJECT n_returned /\\ $heap_owners($heap_prune($heap_graph(S_box_disposed)),HOBJECT n_returned) = 1 /\\ $opb_output(S_box_disposed.EVENTS) = $ptascii("NULL_SLOT|STORED|CS|GR|HR|SLOT_S|BS|DS|") /\\ $opb_guard(S_box_disposed)',
    'S_kept_unset_found = $opb_seek(S_box_disposed,14,1000)',
    'S_kept_unset_found.COMPLETION = NORMAL \\/ S_kept_unset_found.COMPLETION = BUDGET',
    'S_kept_unset = S_kept_unset_found[.COMPLETION = NORMAL]',
    '$heap_owners($heap_prune($heap_graph(S_kept_unset)),HOBJECT n_returned) = 1 /\\ $weakref_get(S_kept_unset,n_weak_returned) = POBJECT n_returned /\\ $opb_output(S_kept_unset.EVENTS) = $ptascii("NULL_SLOT|STORED|CS|GR|HR|SLOT_S|BS|DS|BN|SN|LIVE|") /\\ $opb_guard(S_kept_unset)',
    'PhpStep: S_kept_unset ~> S_kept_raw',
    '$lookup(S_kept_raw.ENV,$ptascii("kept")) = eps /\\ $heap_owners($heap_prune($heap_graph(S_kept_raw)),HOBJECT n_returned) = 0 /\\ S_kept_raw.EVENTS = S_kept_unset.EVENTS',
    'S_kept_release = $opb_after(S_kept_unset,S_kept_raw)',
    'S_returned_disposed_found = $opb_seek(S_kept_release,15,1000)',
    'S_returned_disposed_found.COMPLETION = NORMAL \\/ S_returned_disposed_found.COMPLETION = BUDGET',
    'S_returned_disposed = S_returned_disposed_found[.COMPLETION = NORMAL]',
    '~((HOBJECT n_returned) <- S_returned_disposed.ALLOCATIONS) /\\ $weakref_get(S_returned_disposed,n_weak_returned) = PNULL /\\ $opb_output(S_returned_disposed.EVENTS) = $ptascii("NULL_SLOT|STORED|CS|GR|HR|SLOT_S|BS|DS|BN|SN|LIVE|DR|") /\\ $opb_guard(S_returned_disposed)',
    'S_done = $drive_steps(S_returned_disposed,10000)',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps /\\ $weakref_get(S_done,n_weak_returned) = PNULL /\\ $weakref_get(S_done,n_weak_stored) = PNULL /\\ $weakref_get(S_done,n_weak_box) = PNULL /\\ $opb_output(S_done.EVENTS) = EXPECTED_OUTPUT /\\ $opb_guard(S_done)',
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--group', choices=['cv', 'this', 'write', 'lifetime'], required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'ordinary_parent_backed_get_hook_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    clauses, negatives, case_index, start_stage = {
        'cv': (CV, DERIVED, 0, 0),
        'this': (THIS, [], 0, 1),
        'write': (WRITE, [], 0, 5),
        'lifetime': (LIFETIME, [], 1, 7),
    }[args.group]
    selections = [(args.group, clauses, negatives)]
    cases = [data['cases'][case_index]]
    sources = [HERE / ('ordinary-parent-backed-get-hook-' + ['scalar', 'lifetime'][case_index] + '.php')]
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
    out = Path(tempfile.mkdtemp(prefix='ordinary-parent-backed-get-hook-protocol-', dir=ROOT / '.tools'))
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
                     'S_found = $opb_seek(S_initial,' + str(start_stage) + ',1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            content += '\ndec $opb_' + name + '() : bool\ndef $opb_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                condition = condition.replace('EXPECTED_OUTPUT', byte_expr(base64.b64decode(case['stdout_base64'])))
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $opb_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = (' + ' /\\ '.join('$opb_' + name + '()' for name, _, _ in selections) + ')\n'
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
