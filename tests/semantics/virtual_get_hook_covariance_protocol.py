"""Reach virtual getter covariance, inherited dispatch, rejection and Dog cleanup."""
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



PREFIX = r'''dec $vo_replace(pcoccurrence*,pcpath,pcnode) : pcoccurrence*
def $vo_replace(eps,pcpath,pcnode) = eps
def $vo_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath pcnode) :: pcoccurrence*
def $vo_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath_other pcnode_old) :: $vo_replace(pcoccurrence*,pcpath,pcnode)
  -- if pcpath_other =/= pcpath
dec $vo_output(pevent*) : ptbytes
def $vo_output(eps) = eps
def $vo_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $vo_output(pevent*)
dec $vo_stage(pstate,nat) : bool
def $vo_stage(S,0) = true
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $property_hook_plan(S[.COMPLETION = NORMAL]) = (ppropertyhook)
  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)
  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin
  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)
  -- if $ptlc(pclassdesc.NAME) = $ptascii("covchild40")
def $vo_stage(S,1) = true
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $property_hook_plan(S[.COMPLETION = NORMAL]) = (ppropertyhook)
  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)
  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin
  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)
  -- if $ptlc(pclassdesc.NAME) = $ptascii("covgrand40")
  -- if S.CURRENT = (pcallcontext)
  -- if $ptlc(pcallcontext.NAME) = $ptascii("covparent40::parentread")
def $vo_stage(S,2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $property_hook_context_kind(pcallcontext)
def $vo_stage(S,3) = true
  -- if S.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*
def $vo_stage(S,4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $ptlc(pcallcontext.NAME) = $ptascii("covchild40::answer")
def $vo_stage(S,5) = true
  -- if S.TODO = (ASSIGN_ARRAY pbase 28 b) :: ptask*
def $vo_stage(S,9) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES "Ym94") metadata)) :: ptask*
def $vo_stage(S,10) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
  -- if pdestructionoperation.SOURCE = UNSET (NExprVariable (BYTES "Ym94") metadata)
def $vo_stage(S,11) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $ptlc(pcallcontext.NAME) = $ptascii("covlifeparent40::__destruct")
def $vo_stage(S,12) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES "a2VwdA==") metadata)) :: ptask*
def $vo_stage(S,13) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
  -- if pdestructionoperation.SOURCE = UNSET (NExprVariable (BYTES "a2VwdA==") metadata)
def $vo_stage(S,15) = true
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $property_hook_plan(S[.COMPLETION = NORMAL]) = (ppropertyhook)
  -- if $(ppropertyhook.OBJECT < |S.OBJECTS|)
  -- if S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin
  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)
  -- if $ptlc(pclassdesc.NAME) = $ptascii("covlifegrand40")
def $vo_stage(S,n) = false -- otherwise

dec $vo_seek(pstate,nat,nat) : pstate
def $vo_seek(S,n_stage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $vo_stage(S,n_stage) \/ n = 0
def $vo_seek(S,n_stage,n) = $vo_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$vo_stage(S,n_stage) /\ $(n > 0)
def $vo_seek(S,n_stage,n) = $vo_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $vo_seek(S,n_stage,n) = S -- otherwise
dec $vo_after(pstate,pstate) : pstate
def $vo_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $vo_guard(pstate) : bool
def $vo_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $vo_slot(pstate,nat,ptbytes) : ppropstate?
def $vo_slot(S,n,ptbytes) = (ppropertyslot_value.STATE)
  -- if $objectprops_at(S.OBJECTPROPS,n) = (ppropertyslot*)
  -- if $property_slot_at(ppropertyslot*,ptbytes) = (ppropertyslot_value)
def $vo_slot(S,n,ptbytes) = eps -- otherwise
dec $vo_link_replace(pclasslink*,porigin,pclassparent) : pclasslink*
def $vo_link_replace(eps,porigin,pclassparent) = eps
def $vo_link_replace((CLASSLINK porigin pclassparent_old) :: pclasslink*,porigin,pclassparent) = (CLASSLINK porigin pclassparent) :: pclasslink*
def $vo_link_replace((CLASSLINK porigin_other pclassparent_old) :: pclasslink*,porigin,pclassparent) = (CLASSLINK porigin_other pclassparent_old) :: $vo_link_replace(pclasslink*,porigin,pclassparent)
  -- if porigin_other =/= porigin
dec $vo_class_replace(pclassdesc*,porigin,pclassdesc) : pclassdesc*
def $vo_class_replace(eps,porigin,pclassdesc) = eps
def $vo_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_new :: pclassdesc*
  -- if pclassdesc_old.ORIGIN = porigin
def $vo_class_replace(pclassdesc_old :: pclassdesc*,porigin,pclassdesc_new) = pclassdesc_old :: $vo_class_replace(pclassdesc*,porigin,pclassdesc_new)
  -- if pclassdesc_old.ORIGIN =/= porigin
'''

def reach(name, previous, stage):
    return [f'{name}_found = $vo_seek({previous},{stage},1000)',
            fr'{name}_found.COMPLETION = NORMAL \/ {name}_found.COMPLETION = BUDGET',
            f'{name} = {name}_found[.COMPLETION = NORMAL]']

def prep(s, called, owners):
    return [f'$property_hook_plan({s}) = (ppropertyhook_{s})',
            f'{s}.TODO = (PROPERTY_PREP phpType20_{s} z_{s}) :: (DIM_FETCH z_{s}) :: ptask_{s}*',
            f'$property_effective_desc({s},ppropertyhook_{s}.OBJECT,$ptascii("value")) = (ppropertydesc_{s})',
            f'$property_hook_function({s},ppropertyhook_{s}) = (pfunction_{s})',
            f'{s}.OBJECTS[ppropertyhook_{s}.OBJECT] = INSTANCE porigin_{called} /\\ ppropertydesc_{s} = ppropertydesc_child /\\ ppropertyhook_{s}.PROPERTY = ppropertydesc_child.ORIGIN /\\ pfunction_{s}.SIGNATURE.RETURNS = ppropertydesc_child.TYPE',
            f'$target_lexical_class({s},PROPERTY_HOOK_TARGET ppropertyhook_{s}) = (porigin_child) /\\ $target_called_class({s},PROPERTY_HOOK_TARGET ppropertyhook_{s}) = (porigin_{called}) /\\ $objectprops_at({s}.OBJECTPROPS,ppropertyhook_{s}.OBJECT) = (eps) /\\ $vo_slot({s},ppropertyhook_{s}.OBJECT,$ptascii("value")) = eps',
            f'$heap_owners($heap_prune($heap_graph({s})),HOBJECT ppropertyhook_{s}.OBJECT) = {owners} /\\ $vo_guard({s})']

def call(s, called, owners):
    return [f'PhpStep: {s} ~> {s}_call_raw',
            f'{s}_call_raw.TODO = [(CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook_{s}) eps 0 eps (ppropertyhook_{s}.SITE) z_{s}), PROPERTY_HOOK_RESULT ppropertyhook_{s}] ++ ptask_{s}*',
            f'{s}_call_raw.RESULT = KNOWN PNULL /\\ {s}_call_raw.EVENTS = {s}.EVENTS /\\ {s}_call_raw.OBJECTPROPS = {s}.OBJECTPROPS',
            f'{s}_call = $vo_after({s},{s}_call_raw)',
            f'$property_hook_pending_call({s}_call,ppropertyhook_{s}) /\\ $heap_owners($heap_prune($heap_graph({s}_call)),HOBJECT ppropertyhook_{s}.OBJECT) = {owners} /\\ $vo_guard({s}_call)',
            *reach(s+'_entered', s+'_call', 2),
            f'{s}_entered.CURRENT = (pcallcontext_hook_{s})',
            f'{s}_entered.FRAMES = pframe_{s} :: pframe_tail_{s}*',
            f'pframe_{s}.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_{s}) :: ptask_{s}* /\\ pcallcontext_hook_{s}.TARGET = PROPERTY_HOOK_TARGET ppropertyhook_{s} /\\ pcallcontext_hook_{s}.FUNCTION = ppropertyhook_{s}.HOOK /\\ pcallcontext_hook_{s}.RECEIVER = (ppropertyhook_{s}.OBJECT)',
            f'pcallcontext_hook_{s}.LEXICAL_CLASS = (porigin_child) /\\ pcallcontext_hook_{s}.CALLED_CLASS = (porigin_{called}) /\\ pfunction_{s}.NAME = pclassdesc_child.NAME ++ $ptascii("::$value::get") /\\ $property_hook_frame({s}_entered,pcallcontext_hook_{s},pframe_{s},ppropertyhook_{s})',
            f'~$property_hook_backing({s}_entered,ppropertyhook_{s}.OBJECT,ppropertydesc_{s}) /\\ $objectprops_at({s}_entered.OBJECTPROPS,ppropertyhook_{s}.OBJECT) = (eps) /\\ $heap_owners($heap_prune($heap_graph({s}_entered)),HOBJECT ppropertyhook_{s}.OBJECT) = {owners} /\\ $vo_guard({s}_entered)']

def answer(s, called):
    return [*reach(s+'_answer', s+'_entered', 4),
            f'{s}_answer.CURRENT = (pcallcontext_answer_{s})',
            f'pcallcontext_answer_{s}.FUNCTION = pmethoddesc_answer.FUNCTION.ORIGIN /\\ pcallcontext_answer_{s}.LEXICAL_CLASS = (porigin_child) /\\ pcallcontext_answer_{s}.CALLED_CLASS = (porigin_{called}) /\\ pcallcontext_answer_{s}.RECEIVER = (ppropertyhook_{s}.OBJECT) /\\ $call_context_valid({s}_answer,pcallcontext_answer_{s},{s}_answer.CVS)']

def returned(s, previous, value, caller):
    return [*reach(s+'_result', previous, 3),
            f'{s}_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_{s}) :: ptask_{s}* /\\ {s}_result.RESULT = KNOWN ({value}) /\\ {s}_result.CURRENT = {"(pcallcontext_read)" if caller else "eps"}',
            f'$objectprops_at({s}_result.OBJECTPROPS,ppropertyhook_{s}.OBJECT) = (eps) /\\ $heap_owners($heap_prune($heap_graph({s}_result)),HOBJECT ppropertyhook_{s}.OBJECT) = {2 if caller else 1} /\\ $task_nodes(PROPERTY_HOOK_RESULT ppropertyhook_{s}) = eps /\\ $vo_guard({s}_result)',
            f'PhpStep: {s}_result ~> {s}_base_raw',
            f'{s}_base_raw.RESULT = {s}_result.RESULT /\\ {s}_base_raw.BASE = BASE_VALUE {s}_result.RESULT /\\ {s}_base_raw.TODO = ptask_{s}* /\\ {s}_base_raw.EVENTS = {s}_result.EVENTS',
            f'{s}_base = $vo_after({s}_result,{s}_base_raw)',
            f'$vo_guard({s}_base)']

def write(s, line, value, class_name, owners, this=False):
    message = f'Property {class_name}::$value is read-only'
    rhs = f'VARIABLE ($ptascii("value")) {line}' if this else f'KNOWN (PINT {value})'
    clauses = [
        f'{s}.TODO = (ASSIGN_ARRAY (BASE_PROPERTY_PENDING pbase_{s} poperand_{s} z_receiver_{s}) z_{s} b_{s}) :: ptask_{s}*',
        f'z_{s} = {line} /\\ {s}.RESULT = {rhs} /\\ $call_task_valid({s},ASSIGN_ARRAY (BASE_PROPERTY_PENDING pbase_{s} poperand_{s} z_receiver_{s}) z_{s} b_{s}) /\\ $vo_guard({s})',
        f'{s}_receiver = $property_pending_resolve({s},pbase_{s},poperand_{s},PPW,z_receiver_{s},z_{s})',
        f'{s}_receiver.COMPLETION = NORMAL',
        f'{s}_receiver.BASE = BASE_PROPERTY (POBJECT n_{s}) ($ptascii("value"))',
        f'$property_effective_desc({s},n_{s},$ptascii("value")) = (ppropertydesc_{s})',
        f'$objectprops_at({s}.OBJECTPROPS,n_{s}) = (eps) /\\ $property_hook_virtual({s},ppropertydesc_{s}) /\\ $heap_owners($heap_prune($heap_graph({s})),HOBJECT n_{s}) = {owners}',
    ]
    if this:
        clauses += [f'{s}.CURRENT = (pcallcontext_write)',
                    f'$this_receiver({s}) = (n_{s}) /\\ pcallcontext_write.LEXICAL_CLASS = (porigin_parent) /\\ pcallcontext_write.CALLED_CLASS = (porigin_grand)',
                    f'{s}_rhs = $resolve({s},{s}.RESULT)',
                    f'{s}_rhs.COMPLETION = NORMAL /\\ {s}_rhs.RESULT = KNOWN (PINT {value})']
    clauses += [
        f'PhpStep: {s} ~> {s}_raw',
        f'{s}_raw.COMPLETION = THROWN "Error" ($ptascii("{message}")) z_{s} /\\ {s}_raw.TODO = ptask_{s}* /\\ {s}_raw.BASE = BASE_PROPERTY (POBJECT n_{s}) ($ptascii("value"))',
        f'{s}_raw.OBJECTPROPS = {s}.OBJECTPROPS /\\ {s}_raw.STORE = {s}.STORE /\\ {s}_raw.OBJECTS = {s}.OBJECTS /\\ {s}_raw.ALLOCATIONS = {s}.ALLOCATIONS /\\ {s}_raw.EVENTS = {s}.EVENTS /\\ {s}_raw.CLASSES = {s}.CLASSES',
        f'$heap_owners($heap_prune($heap_graph({s}_raw)),HOBJECT n_{s}) = {owners if this else owners+1}',
        f'{s}_throw = $vo_after({s},{s}_raw)',
        f'{s}_throw.COMPLETION = THROWING n_error_{s}',
        f'$throwable_field({s}_throw,n_error_{s},"message") = PSTRING ($ptascii("{message}")) /\\ $throwable_field({s}_throw,n_error_{s},"line") = PINT z_{s}',
        f'{s}_search_raw = $throwable_begin({s}_throw)',
        f'{s}_search_raw.COMPLETION = NORMAL /\\ {s}_search_raw.TODO = (THROW_SEARCH n_error_{s}) :: ptask_{s}* /\\ {s}_search_raw.BASE = BASE_VALUE (KNOWN PNULL) /\\ {s}_search_raw.RESULT = KNOWN PNULL',
        f'{s}_search = {s}_search_raw',
        f'$objectprops_at({s}_search.OBJECTPROPS,n_{s}) = (eps) /\\ $vo_guard({s}_search)',
    ]
    return clauses

def classes(stem):
    clauses = []
    for suffix, name in [('Parent','parent'),('Bridge','bridge'),('Child','child'),('Grand','grand')]:
        clauses += [f'$class_named(S.CLASSNAMES,$ptlc($ptascii("{stem}{suffix}40"))) = (porigin_{name})',
                    f'$class_at(S.CLASSES,porigin_{name}) = (pclassdesc_{name})']
    return clauses + [
        r'$class_link_at(S.LINKEDPARENTS,porigin_parent) = eps /\ pclassdesc_parent.PARENT = eps /\ $class_link_at(S.LINKEDPARENTS,porigin_bridge) = (SOURCE_PARENT porigin_parent) /\ $class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_bridge) /\ $class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_child)',
        r'|pclassdesc_parent.PROPERTIES| = 1 /\ |pclassdesc_child.PROPERTIES| = 1 /\ pclassdesc_bridge.PROPERTIES = eps /\ pclassdesc_grand.PROPERTIES = eps',
        r'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
        r'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
        r'ppropertydesc_parent.TYPE =/= eps /\ ppropertydesc_child.TYPE =/= eps /\ ppropertydesc_parent.TYPE =/= ppropertydesc_child.TYPE /\ ppropertydesc_parent.DEFAULT = PROP_UNINITIALIZED /\ ppropertydesc_child.DEFAULT = PROP_UNINITIALIZED',
        r'$property_layout(S,porigin_bridge,|S.CLASSES|) = [ppropertydesc_parent] /\ $property_declaring_class(S.CLASSES,ppropertydesc_parent.ORIGIN) = (porigin_parent) /\ porigin_parent =/= porigin_bridge',
        r'$property_layout(S,porigin_child,|S.CLASSES|) = [ppropertydesc_child] /\ $property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_child]',
        r'$property_hook_virtual(S,ppropertydesc_parent) /\ $property_hook_virtual(S,ppropertydesc_child) /\ ~$property_hook_override_backed(S,ppropertydesc_parent) /\ ~$property_hook_inherited_backing(S,ppropertydesc_child)',
        r'$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child) /\ $property_hook_covariance(S,ppropertydesc_parent,ppropertydesc_child) = PVCOMPATIBLE /\ $property_hook_covariance(S,ppropertydesc_child,ppropertydesc_parent) = PVINCOMPATIBLE',
        r'~$property_hook_override_shape(S,ppropertydesc_parent,ppropertydesc_child) /\ $property_hook_virtual_edge(S,ppropertydesc_parent,ppropertydesc_child) /\ $property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child)',
        r'$property_hook_virtual_chain(S,ppropertydesc_parent,|S.CLASSES|) /\ $property_hook_virtual_chain(S,ppropertydesc_child,|S.CLASSES|)',
        r'$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child) = eps /\ $property_initial_slots(S,porigin_child,[ppropertydesc_child]) = (eps) /\ $property_initial_slots(S,porigin_grand,[ppropertydesc_child]) = (eps) /\ $vo_guard(S)',
        r'$method_named(pclassdesc_parent.METHODS,$ptascii("parentRead")) = (pmethoddesc_read)',
    ]

CV = classes('Cov') + [
    r'|ppropertydesc_parent.TYPE| = 2 /\ (PTBRANCH ([PTBUILTIN "int"])) <- ppropertydesc_parent.TYPE /\ (PTBRANCH ([PTBUILTIN "string"])) <- ppropertydesc_parent.TYPE /\ ppropertydesc_child.TYPE = [PTBRANCH ([PTBUILTIN "int"])]',
    r'$method_named(pclassdesc_child.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
    r'$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
    r'pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\ pmethoddesc_answer.OWNER = porigin_child /\ pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_grand_answer.FUNCTION.ORIGIN',
    'S_child = S',
] + prep('S_child','child',1) + call('S_child','child',2) + answer('S_child','child') + returned('S_child','S_child_answer','PINT 13',False)

THIS = classes('Cov') + [
    r'$method_named(pclassdesc_child.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
    'S_this = S',
] + prep('S_this','grand',3) + [
    r'S_this.CURRENT = (pcallcontext_read)',
    r'pcallcontext_read.FUNCTION = pmethoddesc_read.FUNCTION.ORIGIN /\ pcallcontext_read.LEXICAL_CLASS = (porigin_parent) /\ pcallcontext_read.CALLED_CLASS = (porigin_grand) /\ $this_receiver(S_this) = (ppropertyhook_S_this.OBJECT)',
] + call('S_this','grand',3) + answer('S_this','grand') + returned('S_this','S_this_answer','PINT 13',True) + [
    *reach('S_write','S_this_base',5),
    r'$vo_output(S_write.EVENTS) = $ptascii("PE|P:CovParent40/CovParent40|root|CE|C:CovChild40/CovChild40|13|GE|C:CovChild40/CovGrand40|13|R|")',
] + write('S_write',28,300,'CovGrand40',1) + [
    r'S_done = $drive_steps(S_write_search,10000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ $vo_output(S_done.EVENTS) = EXPECTED_OUTPUT /\ $vo_guard(S_done)',
]

LIFETIME = classes('CovLife') + [
    'S_this = S',
] + prep('S_this','grand',3) + [
    r'S_this.CURRENT = (pcallcontext_read)',
    r'pcallcontext_read.FUNCTION = pmethoddesc_read.FUNCTION.ORIGIN /\ pcallcontext_read.LEXICAL_CLASS = (porigin_parent) /\ pcallcontext_read.CALLED_CLASS = (porigin_grand) /\ $this_receiver(S_this) = (ppropertyhook_S_this.OBJECT)',
] + call('S_this','grand',3) + [
    *reach('S_this_result','S_this_entered',3),
    r'S_this_result.RESULT = KNOWN (POBJECT n_leaf)',
    r'S_this_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_S_this) :: ptask_S_this* /\ S_this_result.CURRENT = (pcallcontext_read) /\ $objectprops_at(S_this_result.OBJECTPROPS,ppropertyhook_S_this.OBJECT) = (eps)',
    r'$heap_owners($heap_prune($heap_graph(S_this_result)),HOBJECT n_leaf) = 1 /\ $heap_owners($heap_prune($heap_graph(S_this_result)),HOBJECT ppropertyhook_S_this.OBJECT) = 2 /\ $task_nodes(PROPERTY_HOOK_RESULT ppropertyhook_S_this) = eps /\ $vo_guard(S_this_result)',
    r'PhpStep: S_this_result ~> S_this_base_raw',
    r'S_this_base_raw.RESULT = KNOWN (POBJECT n_leaf) /\ S_this_base_raw.BASE = BASE_VALUE (KNOWN (POBJECT n_leaf)) /\ S_this_base_raw.TODO = ptask_S_this* /\ S_this_base_raw.EVENTS = S_this_result.EVENTS /\ $heap_owners($heap_prune($heap_graph(S_this_base_raw)),HOBJECT n_leaf) = 2',
    r'S_this_base = $vo_after(S_this_result,S_this_base_raw)',
    *reach('S_box','S_this_base',9),
    r'$lookup(S_box.ENV,$ptascii("kept")) = (n_kept)',
    r'S_box.STORE[n_kept] = DEFINED (POBJECT n_leaf)',
    r'$lookup(S_box.ENV,$ptascii("weak_box")) = (n_weak_box_cell)',
    r'S_box.STORE[n_weak_box_cell] = DEFINED (POBJECT n_weak_box)',
    r'$lookup(S_box.ENV,$ptascii("weak_leaf")) = (n_weak_leaf_cell)',
    r'S_box.STORE[n_weak_leaf_cell] = DEFINED (POBJECT n_weak_leaf)',
    r'$heap_owners($heap_prune($heap_graph(S_box)),HOBJECT n_leaf) = 1 /\ $heap_owners($heap_prune($heap_graph(S_box)),HOBJECT ppropertyhook_S_this.OBJECT) = 1 /\ $objectprops_at(S_box.OBJECTPROPS,ppropertyhook_S_this.OBJECT) = (eps) /\ $vo_output(S_box.EVENTS) = $ptascii("H|DOG|EMPTY|LIVE|") /\ $vo_guard(S_box)',
    r'PhpStep: S_box ~> S_box_raw',
    r'$lookup(S_box_raw.ENV,$ptascii("box")) = eps /\ $heap_owners($heap_prune($heap_graph(S_box_raw)),HOBJECT ppropertyhook_S_this.OBJECT) = 0 /\ $heap_owners($heap_prune($heap_graph(S_box_raw)),HOBJECT n_leaf) = 1 /\ S_box_raw.EVENTS = S_box.EVENTS',
    r'S_box_release = $vo_after(S_box,S_box_raw)',
    *reach('S_destruct','S_box_release',11),
    r'S_destruct.CURRENT = (pcallcontext_destruct)',
    r'pcallcontext_destruct.LEXICAL_CLASS = (porigin_parent) /\ pcallcontext_destruct.CALLED_CLASS = (porigin_grand) /\ pcallcontext_destruct.RECEIVER = (ppropertyhook_S_this.OBJECT) /\ $objectprops_at(S_destruct.OBJECTPROPS,ppropertyhook_S_this.OBJECT) = (eps) /\ $heap_owners($heap_prune($heap_graph(S_destruct)),HOBJECT n_leaf) = 1 /\ $vo_guard(S_destruct)',
    *reach('S_box_exit','S_destruct',10),
    r'S_box_exit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_box) :: ptask_box_exit*',
    r'$vo_output(S_box_exit.EVENTS) = $ptascii("H|DOG|EMPTY|LIVE|BEMPTY|") /\ $heap_owners($heap_prune($heap_graph(S_box_exit)),HOBJECT n_leaf) = 1 /\ ~((HOBJECT ppropertyhook_S_this.OBJECT) <- S_box_exit.ALLOCATIONS)',
    r'$weakref_get(S_box_exit,n_weak_box) = PNULL /\ $weakref_get(S_box_exit,n_weak_leaf) = POBJECT n_leaf',
    r'PhpStep: S_box_exit ~> S_box_finished_raw',
    r'S_box_finished = $vo_after(S_box_exit,S_box_finished_raw)',
    *reach('S_kept','S_box_finished',12),
    r'$vo_output(S_kept.EVENTS) = $ptascii("H|DOG|EMPTY|LIVE|BEMPTY|BN|LIVE|") /\ $heap_owners($heap_prune($heap_graph(S_kept)),HOBJECT n_leaf) = 1 /\ $vo_guard(S_kept)',
    r'PhpStep: S_kept ~> S_kept_raw',
    r'$lookup(S_kept_raw.ENV,$ptascii("kept")) = eps /\ $heap_owners($heap_prune($heap_graph(S_kept_raw)),HOBJECT n_leaf) = 0 /\ S_kept_raw.EVENTS = S_kept.EVENTS',
    r'S_kept_release = $vo_after(S_kept,S_kept_raw)',
    *reach('S_leaf_exit','S_kept_release',13),
    r'$vo_output(S_leaf_exit.EVENTS) = $ptascii("H|DOG|EMPTY|LIVE|BEMPTY|BN|LIVE|DD|") /\ ~((HOBJECT n_leaf) <- S_leaf_exit.ALLOCATIONS) /\ $weakref_get(S_leaf_exit,n_weak_leaf) = PNULL',
    r'S_done = $drive_steps(S_leaf_exit,10000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ $vo_output(S_done.EVENTS) = EXPECTED_OUTPUT /\ $weakref_get(S_done,n_weak_box) = PNULL /\ $weakref_get(S_done,n_weak_leaf) = PNULL /\ $vo_guard(S_done)',
]

n_insert = LIFETIME.index(r'S_this_result.RESULT = KNOWN (POBJECT n_leaf)') + 1
LIFETIME = LIFETIME[:n_insert] + [
    r'$class_named(S_this_result.CLASSNAMES,$ptlc($ptascii("Animal40"))) = (porigin_animal)',
    r'$class_named(S_this_result.CLASSNAMES,$ptlc($ptascii("Dog40"))) = (porigin_dog)',
    r'S_this_result.OBJECTS[n_leaf] = INSTANCE porigin_dog /\ $class_link_at(S_this_result.LINKEDPARENTS,porigin_dog) = (SOURCE_PARENT porigin_animal) /\ ppropertydesc_parent.TYPE = [PTBRANCH ([PTCLASS ($ptascii("Animal40"))])] /\ ppropertydesc_child.TYPE = [PTBRANCH ([PTCLASS ($ptascii("Dog40"))])]',
] + LIFETIME[n_insert:]

DERIVED = ['~$property_hook_virtual_chain(S,ppropertydesc_parent,0) /\\ $property_hook_virtual_chain(S,ppropertydesc_parent,1) /\\ ~$property_hook_virtual_chain(S,ppropertydesc_child,0) /\\ ~$property_hook_virtual_chain(S,ppropertydesc_child,1) /\\ $property_hook_virtual_chain(S,ppropertydesc_child,2)', '~$property_hook_override_pair(S,ppropertydesc_child,ppropertydesc_child) /\\ ~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.TYPE = eps]) /\\ ~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.DEFAULT = PROP_NULL])', '~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.FINAL = true]) /\\ ~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.SETVISIBILITY = (PROPERTY_PROTECTED)]) /\\ ~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.VISIBILITY = PROPERTY_PROTECTED])', '~$property_hook_virtual_chain(S[.LINKEDPARENTS = eps],ppropertydesc_child,|S.CLASSES|) /\\ ~$property_hook_virtual_chain(S[.CLASSES = eps],ppropertydesc_child,|S.CLASSES|) /\\ ~$property_hook_virtual_chain(S[.SOURCES = eps],ppropertydesc_child,|S.CLASSES|)', 'S_bad_child = S[.LINKEDPARENTS = $vo_link_replace(S.LINKEDPARENTS,porigin_child,STDCLASS_PARENT)]', '~$property_hook_virtual_chain(S_bad_child,ppropertydesc_child,|S.CLASSES|) /\\ ~$property_hook_override_pair(S_bad_child,ppropertydesc_parent,ppropertydesc_child)', 'S_bad_bridge = S[.LINKEDPARENTS = $vo_link_replace(S.LINKEDPARENTS,porigin_bridge,STDCLASS_PARENT)]', '~$property_hook_virtual_chain(S_bad_bridge,ppropertydesc_child,|S.CLASSES|) /\\ ~$property_hook_override_pair(S_bad_bridge,ppropertydesc_parent,ppropertydesc_child)', 'S_bad_root = S[.LINKEDPARENTS = S.LINKEDPARENTS ++ [CLASSLINK porigin_parent (SOURCE_PARENT porigin_child)]]', '~$property_hook_virtual_chain(S_bad_root,ppropertydesc_parent,|S.CLASSES|) /\\ ~$property_hook_override_pair(S_bad_root,ppropertydesc_parent,ppropertydesc_child)', 'S_cycle = S[.CLASSES = $vo_class_replace(S.CLASSES,porigin_parent,pclassdesc_parent[.PARENT = (pclassdesc_child.NAME)])][.LINKEDPARENTS = S.LINKEDPARENTS ++ [CLASSLINK porigin_parent (SOURCE_PARENT porigin_child)]]', '~$property_hook_virtual_chain(S_cycle,ppropertydesc_child,|S.CLASSES|) /\\ ~$property_hook_virtual_chain(S_cycle,ppropertydesc_parent,|S.CLASSES|)', 'S.SOURCES = pcunit :: pcunit_tail*', '$property_hook_origin(S,ppropertydesc_parent) = (porigin_parent_hook)', 'porigin_parent_hook = PORIGIN n_unit pcpath_parent_hook', 'ppropertyhook_S_child.HOOK = PORIGIN n_unit pcpath_child_hook', 'pcunit.ID = n_unit', '$origin_node(S.SOURCES,porigin_parent_hook) = (NPropertyHook phpType14_parent phpType24_parent phpType4_parent phpType11_parent phpType16_parent phpType39_parent metadata_parent)', '$origin_node(S.SOURCES,ppropertyhook_S_child.HOOK) = (NPropertyHook phpType14_child phpType24_child phpType4_child phpType11_child phpType16_child phpType39_child metadata_child)', 'phpType38_parent_byref = NPropertyHook phpType14_parent phpType24_parent (BOOLEAN true) phpType11_parent phpType16_parent phpType39_parent metadata_parent', 'S_parent_byref = S[.SOURCES = pcunit[.OCCURRENCES = $vo_replace(pcunit.OCCURRENCES,pcpath_parent_hook,phpType38_parent_byref)] :: pcunit_tail*]', '~$property_hook_virtual_chain(S_parent_byref,ppropertydesc_parent,|S.CLASSES|) /\\ ~$property_hook_override_pair(S_parent_byref,ppropertydesc_parent,ppropertydesc_child)', 'phpType38_child_backed = NPropertyHook phpType14_child phpType24_child phpType4_child phpType11_child phpType16_child (NExprPropertyFetch (NExprVariable (BYTES "dGhpcw==") metadata_child) (NIdentifier (BYTES "dmFsdWU=") metadata_child) metadata_child) metadata_child', 'S_child_backed = S[.SOURCES = pcunit[.OCCURRENCES = $vo_replace(pcunit.OCCURRENCES,pcpath_child_hook,phpType38_child_backed)] :: pcunit_tail*]', '~$property_hook_virtual_chain(S_child_backed,ppropertydesc_child,|S.CLASSES|) /\\ ~$property_hook_override_pair(S_child_backed[.LINKEDPARENTS = $vo_link_replace(S.LINKEDPARENTS,porigin_child,STDCLASS_PARENT)],ppropertydesc_parent,ppropertydesc_child)', '~$property_slots_valid(S,[ppropertydesc_child],[{ DECL (ppropertyhook_S_child.PROPERTY), NAME ($ptascii("value")), STATE PROP_INITIAL }]) /\\ ~$property_slots_valid(S,[ppropertydesc_child],[{ DECL (ppropertyhook_S_child.PROPERTY), NAME ($ptascii("value")), STATE (PROP_VALUE (DIRECT (PINT 300))) }])', '~$property_hook_valid(S_child,ppropertyhook_S_child[.HOOK = porigin_parent_hook],false) /\\ ~$call_context_valid(S_child_entered,pcallcontext_hook_S_child[.LEXICAL_CLASS = (porigin_parent)],S_child_entered.CVS) /\\ ~$call_context_valid(S_child_entered,pcallcontext_hook_S_child[.CALLED_CLASS = (porigin_grand)],S_child_entered.CVS)']

DERIVED += [
    r'~$property_hook_virtual_edge(S,ppropertydesc_child,ppropertydesc_parent) /\ ~$property_hook_virtual_edge(S,ppropertydesc_parent[.TYPE = eps],ppropertydesc_child) /\ ~$property_hook_covariance_parent(S,ppropertydesc_parent[.TYPE = eps],ppropertydesc_child)',
    r'$property_hook_get_declaration(S,ppropertydesc_parent) = ($ptascii("CovParent40::$value::get(): string|int")) /\ $property_hook_get_declaration(S,ppropertydesc_child) = ($ptascii("CovChild40::$value::get(): int"))',
    r'phpType38_parent_backed = NPropertyHook phpType14_parent phpType24_parent phpType4_parent phpType11_parent phpType16_parent (NExprPropertyFetch (NExprVariable (BYTES "dGhpcw==") metadata_parent) (NIdentifier (BYTES "dmFsdWU=") metadata_parent) metadata_parent) metadata_parent',
    r'S_parent_backed = S[.SOURCES = pcunit[.OCCURRENCES = $vo_replace(pcunit.OCCURRENCES,pcpath_parent_hook,phpType38_parent_backed)] :: pcunit_tail*]',
    r'$property_hook_override_backed(S_parent_backed,ppropertydesc_parent) /\ ~$property_hook_virtual_chain(S_parent_backed,ppropertydesc_parent,|S.CLASSES|) /\ ~$property_hook_covariance_parent(S_parent_backed,ppropertydesc_parent,ppropertydesc_child) /\ ~$property_hook_override_pair(S_parent_backed,ppropertydesc_parent,ppropertydesc_child)',
    r'ppropertydesc_parent_unknown = ppropertydesc_parent[.TYPE = [PTBRANCH ([PTCLASS ($ptascii("MissingParent40"))])]]',
    r'ppropertydesc_child_unknown = ppropertydesc_child[.TYPE = [PTBRANCH ([PTCLASS ($ptascii("MissingChild40"))])]]',
    r'S_unknown = S[.CLASSES = $vo_class_replace($vo_class_replace(S.CLASSES,porigin_parent,pclassdesc_parent[.PROPERTIES = [ppropertydesc_parent_unknown]]),porigin_child,pclassdesc_child[.PROPERTIES = [ppropertydesc_child_unknown]])]',
    r'$property_hook_covariance(S_unknown,ppropertydesc_parent_unknown,ppropertydesc_child_unknown) = PVNEEDS ptbytes_missing*',
    r'$ptascii("MissingParent40") <- ptbytes_missing* /\ $ptascii("MissingChild40") <- ptbytes_missing* /\ $property_hook_covariance_parent(S_unknown,ppropertydesc_parent_unknown,ppropertydesc_child_unknown) /\ $trait_property_inherit_message(S_unknown,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent_unknown,ppropertydesc_child_unknown) = eps /\ ~$property_hook_override_pair(S_unknown,ppropertydesc_parent_unknown,ppropertydesc_child_unknown)',
    r'S_unknown_linked = $property_hook_link_finish(S,pclassdesc_child[.PROPERTIES = [ppropertydesc_child_unknown]],S_unknown)',
    r'S_unknown_linked.COMPLETION = UNSUPPORTED "inherited property hook override" /\ S_unknown_linked.CLASSES = S.CLASSES /\ S_unknown_linked.CLASSNAMES = S.CLASSNAMES /\ S_unknown_linked.LINKEDPARENTS = S.LINKEDPARENTS',
    r'$property_hook_covariance_message(S,ppropertydesc_parent,ppropertydesc_child,PVUNSUPPORTED "derived unknown") = eps /\ $property_hook_covariance_message(S,ppropertydesc_parent,ppropertydesc_child,PVNEEDS ptbytes_missing*) = eps',
    r'$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child[.STATIC = true]) = (ptbytes_static)',
    r'ptbytes_static = $ptascii("Cannot redeclare non static CovParent40::$value as static CovChild40::$value")',
    r'S_static_fatal = $property_hook_override_fatal(S,pclassdesc_child,ptbytes_static)',
    r'S_static_fatal.COMPLETION = STATICBYTES ptbytes_static pclassdesc_child.LINE /\ S_static_fatal.ERRORORIGIN = S.ERRORORIGIN',
    r'$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child[.READONLY = true]) = (ptbytes_readonly)',
    r'ptbytes_readonly = $ptascii("Cannot redeclare non-readonly property CovParent40::$value as readonly CovChild40::$value")',
    r'$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent,ppropertydesc_child[.VISIBILITY = PROPERTY_PROTECTED]) = (ptbytes_access)',
    r'ptbytes_access = $ptascii("Access level to CovChild40::$value must be public (as in class CovParent40)")',
    r'$trait_property_inherit_message(S,pclassdesc_child.NAME,pclassdesc_parent.NAME,ppropertydesc_parent[.FINAL = true],ppropertydesc_child) = (ptbytes_final)',
    r'ptbytes_final = $ptascii("Cannot override final property CovParent40::$value")',
]

INVALID = [
    r'S.COMPLETION = STATICBYTES ($ptascii("Declaration of CovInvalidChild40::$value::get(): string|int must be compatible with CovInvalidParent40::$value::get(): int")) 6 /\ S.EVENTS = eps /\ S.OBJECTS = eps /\ S.OBJECTPROPS = eps',
    r'S.CLASSES = [pclassdesc_parent,pclassdesc_child]',
    r'pclassdesc_parent.NAME = $ptascii("CovInvalidParent40") /\ pclassdesc_child.NAME = $ptascii("CovInvalidChild40") /\ pclassdesc_parent.PROPERTIES =/= eps /\ pclassdesc_child.PROPERTIES =/= eps',
    r'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
    r'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
    r'$property_hook_origin(S,ppropertydesc_child) = (porigin_hook)',
    r'porigin_hook = PORIGIN n_unit pcpath_hook',
    r'S.ERRORORIGIN = eps /\ pclassdesc_child.LINE = 5 /\ pcpath_hook =/= eps',
    r'$origin_node(S.SOURCES,porigin_hook) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook phpType16_hook phpType39_hook metadata_hook)',
    r'$source_line(metadata_hook) = 6 /\ $class_named(S.CLASSNAMES,$ptlc(pclassdesc_child.NAME)) = eps /\ $class_link_at(S.LINKEDPARENTS,pclassdesc_child.ORIGIN) = eps /\ $class_named(S.CLASSNAMES,$ptlc(pclassdesc_parent.NAME)) = (pclassdesc_parent.ORIGIN)',
    r'$property_hook_covariance_parent(S,ppropertydesc_parent,ppropertydesc_child) /\ $property_hook_covariance(S,ppropertydesc_parent,ppropertydesc_child) = PVINCOMPATIBLE /\ ~$property_hook_virtual_edge(S,ppropertydesc_parent,ppropertydesc_child)',
    r'$property_hook_covariance_error_site(S,[ppropertydesc_parent],ppropertydesc_child,$ptascii("Declaration of CovInvalidChild40::$value::get(): string|int must be compatible with CovInvalidParent40::$value::get(): int")) = ((porigin_hook,6))',
    r'S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps /\ S.ENV = eps /\ $declaration_history_valid(S) /\ $class_links_valid(S)',
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--group', choices=['cv', 'this', 'lifetime', 'invalid'], required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'virtual_get_hook_covariance_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    clauses, negatives, case_index, start_stage = {
        'cv': (CV, DERIVED, 0, 0),
        'this': (THIS, [], 0, 1),
        'lifetime': (LIFETIME, [], 1, 15),
        'invalid': (INVALID, [], 2, None),
    }[args.group]
    selections = [(args.group, clauses, negatives)]
    cases = [data['cases'][case_index]]
    sources = [HERE / ('virtual-get-hook-covariance-' + ['scalar', 'lifetime', 'invalid'][case_index] + '.php')]
    php, adapter, bridge, worker, runner, compiler = (ROOT / name for name in [
        '.tools/php/bin/php', '_build/default/adapter/main.exe', '.tools/php-file.so',
        'frontend/worker.php', 'tests/semantics/_build/default/numeric_runner.exe', '.tools/spectec/bin/p4spectec'])
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    assert sha(compiler) == '26d77fb9bfae2b2868e137a94051f55f9b607660c340e9b22ae8300fb0d8ce88'
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
    out = Path(tempfile.mkdtemp(prefix='virtual-get-hook-covariance-protocol-', dir=ROOT / '.tools'))
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
                     'S_found = $vo_seek(S_initial,' + str(start_stage) + ',1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            if args.group == 'invalid':
                setup = [setup[0].replace('S_initial =', 'S =', 1)]
            content += '\ndec $vo_' + name + '() : bool\ndef $vo_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                condition = condition.replace('EXPECTED_OUTPUT', byte_expr(base64.b64decode(case['stdout_base64'])))
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $vo_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = (' + ' /\\ '.join('$vo_' + name + '()' for name, _, _ in selections) + ')\n'
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
