"""Reach inherited physical hook storage, writes, declaring scope and distinct payload cleanup."""
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

PREFIX = r'''dec $eh_replace(pcoccurrence*,pcpath,pcnode) : pcoccurrence*
def $eh_replace(eps,pcpath,pcnode) = eps
def $eh_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath pcnode) :: pcoccurrence*
def $eh_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath_other pcnode_old) :: $eh_replace(pcoccurrence*,pcpath,pcnode)
  -- if pcpath_other =/= pcpath
dec $eh_output(pevent*) : ptbytes
def $eh_output(eps) = eps
def $eh_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $eh_output(pevent*)
dec $eh_stage(pstate,nat) : bool
def $eh_stage(S,0) = true
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $property_hook_plan(S[.COMPLETION = NORMAL]) =/= eps
def $eh_stage(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $property_hook_context_kind(pcallcontext)
def $eh_stage(S,2) = true
  -- if S.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*
def $eh_stage(S,3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $ptlc(pcallcontext.NAME) = $ptascii("inheritedstoragechild37::answer")
def $eh_stage(S,4) = true
  -- if S.TODO = (ASSIGN_ARRAY pbase z b) :: ptask*
  -- if S.RESULT = KNOWN (PINT 300)
def $eh_stage(S,5) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES "Ym94") metadata)) :: ptask*
def $eh_stage(S,6) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
  -- if pdestructionoperation.SOURCE = UNSET (NExprVariable (BYTES "Ym94") metadata)
def $eh_stage(S,7) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $ptlc(pcallcontext.NAME) = $ptascii("inheritedstoragelifeparent37::__destruct")
def $eh_stage(S,8) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES "a2VwdA==") metadata)) :: ptask*
def $eh_stage(S,9) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
  -- if pdestructionoperation.SOURCE = UNSET (NExprVariable (BYTES "a2VwdA==") metadata)
def $eh_stage(S,10) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*
  -- if S.OBJECTS[pinstancestorage.OBJECT] = INSTANCE porigin
  -- if $class_at(S.CLASSES,porigin) = (pclassdesc)
  -- if $ptlc(pclassdesc.NAME) = $ptascii("inheritedstoragelifegrand37")
def $eh_stage(S,11) = true
  -- if S.TODO = (ASSIGN_ARRAY pbase z b) :: ptask*
  -- if S.RESULT = KNOWN (PINT 5)
def $eh_stage(S,n) = false -- otherwise
dec $eh_seek(pstate,nat,nat) : pstate
def $eh_seek(S,n_stage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $eh_stage(S,n_stage) \/ n = 0
def $eh_seek(S,n_stage,n) = $eh_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$eh_stage(S,n_stage) /\ $(n > 0)
def $eh_seek(S,n_stage,n) = $eh_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $eh_seek(S,n_stage,n) = S -- otherwise
dec $eh_after(pstate,pstate) : pstate
def $eh_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $eh_guard(pstate) : bool
def $eh_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $eh_slot(pstate,nat,ptbytes) : ppropstate?
def $eh_slot(S,n,ptbytes) = (ppropertyslot_value.STATE)
  -- if $objectprops_at(S.OBJECTPROPS,n) = (ppropertyslot*)
  -- if $property_slot_at(ppropertyslot*,ptbytes) = (ppropertyslot_value)
def $eh_slot(S,n,ptbytes) = eps -- otherwise
'''


def reach(name, previous, stage):
    return [f'{name}_found = $eh_seek({previous},{stage},1000)',
            fr'{name}_found.COMPLETION = NORMAL \/ {name}_found.COMPLETION = BUDGET',
            f'{name} = {name}_found[.COMPLETION = NORMAL]']


def classes(stem):
    answer=[]
    for role in ['Parent','Child','Grand']:
        name=role.lower()
        answer += [f'$class_named(S.CLASSNAMES,$ptlc($ptascii("{stem}{role}37"))) = (porigin_{name})',
                   f'$class_at(S.CLASSES,porigin_{name}) = (pclassdesc_{name})']
    answer += [r'$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_parent) /\ $class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_child)',
               r'|pclassdesc_parent.PROPERTIES| = 1 /\ |pclassdesc_child.PROPERTIES| = 1 /\ pclassdesc_grand.PROPERTIES = eps',
               r'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
               r'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
               r'$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child) /\ $property_hook_override_backed(S,ppropertydesc_parent) /\ ~$property_hook_override_backed(S,ppropertydesc_child) /\ $property_hook_inherited_backing(S,ppropertydesc_child) /\ ~$property_hook_virtual(S,ppropertydesc_child) /\ $property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_child] /\ $eh_guard(S)']
    return answer


def prep(s, owner, called, slot):
    return [f'$property_hook_plan({s}) = (ppropertyhook_{s})',
            f'{s}.TODO = (PROPERTY_PREP phpType20_{s} z_{s}) :: (DIM_FETCH z_{s}) :: ptask_{s}*',
            f'$property_effective_desc({s},ppropertyhook_{s}.OBJECT,$ptascii("value")) = (ppropertydesc_{s})',
            f'$property_hook_function({s},ppropertyhook_{s}) = (pfunction_{s})',
            f'{s}.OBJECTS[ppropertyhook_{s}.OBJECT] = INSTANCE porigin_{called} /\\ ppropertydesc_{s} = ppropertydesc_{owner} /\\ ppropertyhook_{s}.PROPERTY = ppropertydesc_{owner}.ORIGIN /\\ $property_declaring_class({s}.CLASSES,ppropertyhook_{s}.PROPERTY) = (porigin_{owner}) /\\ $property_layout({s},porigin_{called},|{s}.CLASSES|) = [ppropertydesc_{owner}]',
            f'$target_lexical_class({s},PROPERTY_HOOK_TARGET ppropertyhook_{s}) = (porigin_{owner}) /\\ $target_called_class({s},PROPERTY_HOOK_TARGET ppropertyhook_{s}) = (porigin_{called}) /\\ $eh_slot({s},ppropertyhook_{s}.OBJECT,$ptascii("value")) = ({slot}) /\\ $eh_guard({s})']


def entered(s, previous, owner, called):
    return [*reach(s+'_entered',previous,1),
            f'{s}_entered.CURRENT = (pcallcontext_hook_{s})',
            f'{s}_entered.FRAMES = pframe_{s} :: pframe_tail_{s}*',
            f'pframe_{s}.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_{s}) :: ptask_{s}* /\\ pcallcontext_hook_{s}.TARGET = PROPERTY_HOOK_TARGET ppropertyhook_{s} /\\ pcallcontext_hook_{s}.FUNCTION = ppropertyhook_{s}.HOOK /\\ pcallcontext_hook_{s}.RECEIVER = (ppropertyhook_{s}.OBJECT)',
            f'pcallcontext_hook_{s}.LEXICAL_CLASS = (porigin_{owner}) /\\ pcallcontext_hook_{s}.CALLED_CLASS = (porigin_{called}) /\\ pfunction_{s}.NAME = pclassdesc_{owner}.NAME ++ $ptascii("::$value::get") /\\ $property_hook_frame({s}_entered,pcallcontext_hook_{s},pframe_{s},ppropertyhook_{s}) /\\ ~$property_hook_backing({s}_entered,ppropertyhook_{s}.OBJECT,ppropertydesc_{s}) /\\ $eh_guard({s}_entered)']


def returned(s, previous, value, slot, caller=False):
    return [*reach(s+'_result',previous,2),
            f'{s}_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_{s}) :: ptask_{s}* /\\ {s}_result.RESULT = KNOWN ({value}) /\\ {s}_result.CURRENT = {"(pcallcontext_read)" if caller else "eps"}',
            f'$eh_slot({s}_result,ppropertyhook_{s}.OBJECT,$ptascii("value")) = ({slot}) /\\ $heap_owners($heap_prune($heap_graph({s}_result)),HOBJECT ppropertyhook_{s}.OBJECT) = {2 if caller else 1} /\\ $task_nodes(PROPERTY_HOOK_RESULT ppropertyhook_{s}) = eps /\\ $eh_guard({s}_result)',
            f'PhpStep: {s}_result ~> {s}_base_raw',
            f'{s}_base_raw.RESULT = {s}_result.RESULT /\\ {s}_base_raw.BASE = BASE_VALUE {s}_result.RESULT /\\ {s}_base_raw.TODO = ptask_{s}* /\\ {s}_base_raw.EVENTS = {s}_result.EVENTS',
            f'{s}_base = $eh_after({s}_result,{s}_base_raw)',
            f'$eh_guard({s}_base)']


SCALAR=classes('InheritedStorage')+[
    r'$property_default_state(S,ppropertydesc_parent) = (PROP_VALUE (DIRECT (PINT 100))) /\ ppropertydesc_child.DEFAULT = PROP_UNINITIALIZED /\ ppropertydesc_child.TYPE = ppropertydesc_parent.TYPE',
    r'$class_named(S.CLASSNAMES,$ptlc($ptascii("InheritedStorageUntypedParent37"))) = (porigin_untyped_parent)',
    r'$class_at(S.CLASSES,porigin_untyped_parent) = (pclassdesc_untyped_parent)',
    r'$class_named(S.CLASSNAMES,$ptlc($ptascii("InheritedStorageUntypedChild37"))) = (porigin_untyped_child)',
    r'$class_at(S.CLASSES,porigin_untyped_child) = (pclassdesc_untyped_child)',
    r'ppropertydesc_untyped_parent = pclassdesc_untyped_parent.PROPERTIES[0]',
    r'ppropertydesc_untyped_child = pclassdesc_untyped_child.PROPERTIES[0]',
    r'ppropertydesc_untyped_child.TYPE = eps /\ ppropertydesc_untyped_child.DEFAULT = PROP_NULL /\ $property_hook_override_pair(S,ppropertydesc_untyped_parent,ppropertydesc_untyped_child) /\ $property_hook_inherited_backing(S,ppropertydesc_untyped_child) /\ ~$property_hook_virtual(S,ppropertydesc_untyped_child)',
    r'$method_named(pclassdesc_child.METHODS,$ptascii("answer")) = (pmethoddesc_answer)',
    r'$method_named(pclassdesc_grand.METHODS,$ptascii("answer")) = (pmethoddesc_grand_answer)',
    r'$method_named(pclassdesc_parent.METHODS,$ptascii("parentRead")) = (pmethoddesc_read)',
    r'pmethoddesc_answer.VISIBILITY = PROPERTY_PRIVATE /\ pmethoddesc_answer.OWNER = porigin_child /\ pmethoddesc_grand_answer.OWNER = porigin_grand /\ pmethoddesc_answer.FUNCTION.ORIGIN =/= pmethoddesc_grand_answer.FUNCTION.ORIGIN',
    'S_parent = S',
]+prep('S_parent','parent','parent','PROP_VALUE (DIRECT (PINT 100))')+returned('S_parent','S_parent','PINT 101','PROP_VALUE (DIRECT (PINT 100))')+[
    *reach('S_child','S_parent_base',0),
]+prep('S_child','child','child','PROP_INITIAL')+entered('S_child','S_child','child','child')+returned('S_child','S_child_entered','PINT 7','PROP_INITIAL')+[
    *reach('S_this','S_child_base',0),
]+prep('S_this','child','grand','PROP_INITIAL')+[
    r'S_this.CURRENT = (pcallcontext_read)',
    r'pcallcontext_read.FUNCTION = pmethoddesc_read.FUNCTION.ORIGIN /\ pcallcontext_read.LEXICAL_CLASS = (porigin_parent) /\ pcallcontext_read.CALLED_CLASS = (porigin_grand) /\ $this_receiver(S_this) = (ppropertyhook_S_this.OBJECT) /\ $heap_owners($heap_prune($heap_graph(S_this)),HOBJECT ppropertyhook_S_this.OBJECT) = 3',
    r'PhpStep: S_this ~> S_this_call_raw',
    r'S_this_call_raw.TODO = [(CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook_S_this) eps 0 eps (ppropertyhook_S_this.SITE) z_S_this), PROPERTY_HOOK_RESULT ppropertyhook_S_this] ++ ptask_S_this*',
    r'S_this_call_raw.RESULT = KNOWN PNULL /\ S_this_call_raw.EVENTS = S_this.EVENTS /\ S_this_call_raw.OBJECTPROPS = S_this.OBJECTPROPS',
    r'S_this_call = $eh_after(S_this,S_this_call_raw)',
    r'$property_hook_pending_call(S_this_call,ppropertyhook_S_this) /\ $heap_owners($heap_prune($heap_graph(S_this_call)),HOBJECT ppropertyhook_S_this.OBJECT) = 3 /\ $eh_guard(S_this_call)',
]+entered('S_this','S_this_call','child','grand')+[
    r'pframe_S_this.CONTEXT = (pcallcontext_read) /\ $heap_owners($heap_prune($heap_graph(S_this_entered)),HOBJECT ppropertyhook_S_this.OBJECT) = 3',
    *reach('S_private','S_this_entered',3),
    r'S_private.CURRENT = (pcallcontext_private)',
    r'pcallcontext_private.FUNCTION = pmethoddesc_answer.FUNCTION.ORIGIN /\ pcallcontext_private.LEXICAL_CLASS = (porigin_child) /\ pcallcontext_private.CALLED_CLASS = (porigin_grand) /\ pcallcontext_private.RECEIVER = (ppropertyhook_S_this.OBJECT) /\ $eh_slot(S_private,ppropertyhook_S_this.OBJECT,$ptascii("value")) = (PROP_INITIAL) /\ $eh_guard(S_private)',
]+returned('S_this','S_private','PINT 7','PROP_INITIAL',True)+[
    *reach('S_write','S_this_base',4),
    r'S_write.TODO = (ASSIGN_ARRAY pbase_write z_write b_write) :: ptask_write*',
    r'$property_pending_base(pbase_write) /\ S_write.RESULT = KNOWN (PINT 300) /\ $eh_slot(S_write,ppropertyhook_S_this.OBJECT,$ptascii("value")) = (PROP_INITIAL) /\ $call_task_valid(S_write,ASSIGN_ARRAY pbase_write z_write b_write) /\ $eh_guard(S_write)',
    r'PhpStep: S_write ~> S_write_raw',
    r'S_write_raw.COMPLETION = NORMAL /\ $eh_slot(S_write_raw,ppropertyhook_S_this.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT 300))) /\ S_write_raw.EVENTS = S_write.EVENTS /\ S_write_raw.TODO = ptask_write*',
    r'S_written = $eh_after(S_write,S_write_raw)',
    *reach('S_after_write','S_written',0),
]+prep('S_after_write','child','grand','PROP_VALUE (DIRECT (PINT 300))')+returned('S_after_write','S_after_write','PINT 7','PROP_VALUE (DIRECT (PINT 300))')+[
    *reach('S_untyped','S_after_write_base',0),
]+prep('S_untyped','untyped_child','untyped_child','PROP_VALUE (DIRECT PNULL)')+returned('S_untyped','S_untyped','PBOOL false','PROP_VALUE (DIRECT PNULL)')+[
    *reach('S_untyped_write','S_untyped_base',11),
    r'S_untyped_write.TODO = (ASSIGN_ARRAY pbase_untyped_write z_untyped_write b_untyped_write) :: ptask_untyped_write*',
    r'$eh_slot(S_untyped_write,ppropertyhook_S_untyped.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT PNULL)) /\ $property_pending_base(pbase_untyped_write) /\ $call_task_valid(S_untyped_write,ASSIGN_ARRAY pbase_untyped_write z_untyped_write b_untyped_write)',
    r'PhpStep: S_untyped_write ~> S_untyped_raw',
    r'S_untyped_raw.COMPLETION = NORMAL /\ $eh_slot(S_untyped_raw,ppropertyhook_S_untyped.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT 5))) /\ S_untyped_raw.EVENTS = S_untyped_write.EVENTS',
    r'S_untyped_written = $eh_after(S_untyped_write,S_untyped_raw)',
    r'S_done = $drive(S_untyped_written,10000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $eh_output(S_done.EVENTS) = EXPECTED_OUTPUT /\ $eh_guard(S_done)',
]

LIFETIME=classes('InheritedStorageLife')+[
    r'ppropertydesc_child.DEFAULT = PROP_UNINITIALIZED /\ ppropertydesc_child.TYPE = ppropertydesc_parent.TYPE',
    r'$method_named(pclassdesc_parent.METHODS,$ptascii("parentRead")) = (pmethoddesc_read)',
    r'$method_named(pclassdesc_parent.METHODS,$ptascii("__destruct")) = (pmethoddesc_destructor)',
    'S_life = S',
    r'$property_hook_plan(S_life) = (ppropertyhook_S_life)',
    r'$eh_slot(S_life,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (POBJECT n_stored)))',
]+prep('S_life','child','grand','PROP_VALUE (DIRECT (POBJECT n_stored))')+[
    r'S_life.CURRENT = (pcallcontext_read)',
    r'pcallcontext_read.FUNCTION = pmethoddesc_read.FUNCTION.ORIGIN /\ pcallcontext_read.LEXICAL_CLASS = (porigin_parent) /\ pcallcontext_read.CALLED_CLASS = (porigin_grand) /\ $heap_owners($heap_prune($heap_graph(S_life)),HOBJECT ppropertyhook_S_life.OBJECT) = 3 /\ $heap_owners($heap_prune($heap_graph(S_life)),HOBJECT n_stored) = 1 /\ $eh_output(S_life.EVENTS) = $ptascii("EMPTY|STORED|")',
    r'PhpStep: S_life ~> S_life_call_raw',
    r'S_life_call_raw.TODO = [(CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook_S_life) eps 0 eps (ppropertyhook_S_life.SITE) z_S_life), PROPERTY_HOOK_RESULT ppropertyhook_S_life] ++ ptask_S_life*',
    r'S_life_call = $eh_after(S_life,S_life_call_raw)',
    r'$heap_owners($heap_prune($heap_graph(S_life_call)),HOBJECT ppropertyhook_S_life.OBJECT) = 3 /\ $heap_owners($heap_prune($heap_graph(S_life_call)),HOBJECT n_stored) = 1 /\ $property_hook_pending_call(S_life_call,ppropertyhook_S_life) /\ $eh_guard(S_life_call)',
]+entered('S_life','S_life_call','child','grand')+[
    r'pframe_S_life.CONTEXT = (pcallcontext_read) /\ $heap_owners($heap_prune($heap_graph(S_life_entered)),HOBJECT ppropertyhook_S_life.OBJECT) = 3 /\ $heap_owners($heap_prune($heap_graph(S_life_entered)),HOBJECT n_stored) = 1',
    *reach('S_result','S_life_entered',2),
    r'S_result.RESULT = KNOWN (POBJECT n_returned)',
    r'S_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_S_life) :: ptask_S_life* /\ S_result.CURRENT = (pcallcontext_read) /\ n_returned =/= n_stored /\ $heap_owners($heap_prune($heap_graph(S_result)),HOBJECT n_returned) = 1 /\ $heap_owners($heap_prune($heap_graph(S_result)),HOBJECT n_stored) = 1 /\ $heap_owners($heap_prune($heap_graph(S_result)),HOBJECT ppropertyhook_S_life.OBJECT) = 2 /\ $task_nodes(PROPERTY_HOOK_RESULT ppropertyhook_S_life) = eps /\ $eh_guard(S_result)',
    r'$eh_slot(S_result,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (POBJECT n_stored))) /\ (HOBJECT n_stored) <- $node_children(S_result,HOBJECT ppropertyhook_S_life.OBJECT) /\ ~((HOBJECT n_returned) <- $node_children(S_result,HOBJECT ppropertyhook_S_life.OBJECT))',
    r'S_result.GLOBALTABLE = (psymboltable_global)',
    r'$lookup(psymboltable_global.ENV,$ptascii("weak_returned")) = (n_weak_returned_cell)',
    r'S_result.STORE[n_weak_returned_cell] = DEFINED (POBJECT n_weak_returned)',
    r'$lookup(psymboltable_global.ENV,$ptascii("weak_stored")) = (n_weak_stored_cell)',
    r'S_result.STORE[n_weak_stored_cell] = DEFINED (POBJECT n_weak_stored)',
    r'$lookup(psymboltable_global.ENV,$ptascii("weak_box")) = (n_weak_box_cell)',
    r'S_result.STORE[n_weak_box_cell] = DEFINED (POBJECT n_weak_box)',
    r'$weakref_get(S_result,n_weak_returned) = POBJECT n_returned /\ $weakref_get(S_result,n_weak_stored) = POBJECT n_stored /\ $weakref_get(S_result,n_weak_box) = POBJECT ppropertyhook_S_life.OBJECT /\ $eh_output(S_result.EVENTS) = $ptascii("EMPTY|STORED|G|")',
    r'PhpStep: S_result ~> S_base_raw',
    r'S_base_raw.RESULT = KNOWN (POBJECT n_returned) /\ S_base_raw.BASE = BASE_VALUE (KNOWN (POBJECT n_returned)) /\ S_base_raw.TODO = ptask_S_life* /\ S_base_raw.EVENTS = S_result.EVENTS /\ $heap_owners($heap_prune($heap_graph(S_base_raw)),HOBJECT n_returned) = 2 /\ $heap_owners($heap_prune($heap_graph(S_base_raw)),HOBJECT n_stored) = 1',
    r'S_base = $eh_after(S_result,S_base_raw)',
    r'$heap_owners($heap_prune($heap_graph(S_base)),HOBJECT n_returned) = 2 /\ $heap_owners($heap_prune($heap_graph(S_base)),HOBJECT n_stored) = 1 /\ $eh_guard(S_base)',
    *reach('S_box_unset','S_base',5),
    r'$lookup(S_box_unset.ENV,$ptascii("kept")) = (n_kept_cell)',
    r'S_box_unset.STORE[n_kept_cell] = DEFINED (POBJECT n_returned)',
    r'$heap_owners($heap_prune($heap_graph(S_box_unset)),HOBJECT n_returned) = 1 /\ $heap_owners($heap_prune($heap_graph(S_box_unset)),HOBJECT n_stored) = 1 /\ $eh_output(S_box_unset.EVENTS) = $ptascii("EMPTY|STORED|G|HELD|") /\ $eh_slot(S_box_unset,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (POBJECT n_stored))) /\ $eh_guard(S_box_unset)',
    r'PhpStep: S_box_unset ~> S_box_raw',
    r'$lookup(S_box_raw.ENV,$ptascii("box")) = eps /\ $heap_owners($heap_prune($heap_graph(S_box_raw)),HOBJECT ppropertyhook_S_life.OBJECT) = 0 /\ S_box_raw.EVENTS = S_box_unset.EVENTS',
    r'S_box_release = $eh_after(S_box_unset,S_box_raw)',
    *reach('S_destructor','S_box_release',7),
    r'S_destructor.CURRENT = (pcallcontext_destructor)',
    r'pcallcontext_destructor.FUNCTION = pmethoddesc_destructor.FUNCTION.ORIGIN /\ pcallcontext_destructor.LEXICAL_CLASS = (porigin_parent) /\ pcallcontext_destructor.CALLED_CLASS = (porigin_grand) /\ pcallcontext_destructor.RECEIVER = (ppropertyhook_S_life.OBJECT) /\ $eh_slot(S_destructor,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (POBJECT n_stored))) /\ $eh_guard(S_destructor)',
    *reach('S_storage','S_destructor',10),
    r'S_storage.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_storage*',
    r'pinstancestorage.OBJECT = ppropertyhook_S_life.OBJECT /\ pinstancestorage.NEXT = 0 /\ $instance_storage_valid(S_storage,pinstancestorage) /\ $eh_slot(S_storage,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (POBJECT n_stored))) /\ $heap_owners($heap_prune($heap_graph(S_storage)),HOBJECT n_stored) = 1 /\ $heap_owners($heap_prune($heap_graph(S_storage)),HOBJECT n_returned) = 1 /\ $eh_output(S_storage.EVENTS) = $ptascii("EMPTY|STORED|G|HELD|BS|") /\ $eh_guard(S_storage)',
    r'PhpStep: S_storage ~> S_slot_raw',
    r'S_slot_raw.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_slot) :: (INSTANCE_STORAGE_STEP pinstancestorage_next) :: ptask_storage*',
    r'pinstancestorage_next = pinstancestorage[.NEXT = 1] /\ pdestructionrelease_slot.JOBS = [DESTRUCTION_VALUE (HOBJECT n_stored)] /\ $eh_slot(S_slot_raw,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (PROP_UNSET) /\ $heap_owners($heap_prune($heap_graph(S_slot_raw)),HOBJECT n_stored) = 1 /\ $heap_owners($heap_prune($heap_graph(S_slot_raw)),HOBJECT n_returned) = 1 /\ S_slot_raw.EVENTS = S_storage.EVENTS',
    r'S_slot_release = $eh_after(S_storage,S_slot_raw)',
    *reach('S_box_disposed','S_slot_release',6),
    r'~((HOBJECT ppropertyhook_S_life.OBJECT) <- S_box_disposed.ALLOCATIONS) /\ ~((HOBJECT n_stored) <- S_box_disposed.ALLOCATIONS) /\ (HOBJECT n_returned) <- S_box_disposed.ALLOCATIONS /\ $weakref_get(S_box_disposed,n_weak_box) = PNULL /\ $weakref_get(S_box_disposed,n_weak_stored) = PNULL /\ $weakref_get(S_box_disposed,n_weak_returned) = POBJECT n_returned /\ $heap_owners($heap_prune($heap_graph(S_box_disposed)),HOBJECT n_returned) = 1 /\ $eh_output(S_box_disposed.EVENTS) = $ptascii("EMPTY|STORED|G|HELD|BS|DS|") /\ $eh_guard(S_box_disposed)',
    *reach('S_kept_unset','S_box_disposed',8),
    r'$heap_owners($heap_prune($heap_graph(S_kept_unset)),HOBJECT n_returned) = 1 /\ $weakref_get(S_kept_unset,n_weak_returned) = POBJECT n_returned /\ $eh_output(S_kept_unset.EVENTS) = $ptascii("EMPTY|STORED|G|HELD|BS|DS|BN|SN|LIVE|") /\ $eh_guard(S_kept_unset)',
    r'PhpStep: S_kept_unset ~> S_kept_raw',
    r'$lookup(S_kept_raw.ENV,$ptascii("kept")) = eps /\ $heap_owners($heap_prune($heap_graph(S_kept_raw)),HOBJECT n_returned) = 0 /\ S_kept_raw.EVENTS = S_kept_unset.EVENTS',
    r'S_kept_release = $eh_after(S_kept_unset,S_kept_raw)',
    *reach('S_returned_disposed','S_kept_release',9),
    r'~((HOBJECT n_returned) <- S_returned_disposed.ALLOCATIONS) /\ $weakref_get(S_returned_disposed,n_weak_returned) = PNULL /\ $eh_output(S_returned_disposed.EVENTS) = $ptascii("EMPTY|STORED|G|HELD|BS|DS|BN|SN|LIVE|DR|") /\ $eh_guard(S_returned_disposed)',
    r'S_done = $drive(S_returned_disposed,10000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $weakref_get(S_done,n_weak_returned) = PNULL /\ $weakref_get(S_done,n_weak_stored) = PNULL /\ $weakref_get(S_done,n_weak_box) = PNULL /\ $eh_output(S_done.EVENTS) = EXPECTED_OUTPUT /\ $eh_guard(S_done)',
]

DERIVED=[
    r'~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.TYPE = eps]) /\ ~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.NAME = $ptascii("wrong")])',
    r'~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.FINAL = true]) /\ ~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.SETVISIBILITY = (PROPERTY_PROTECTED)]) /\ ~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.READONLY = true]) /\ ~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.VISIBILITY = PROPERTY_PROTECTED])',
    r'~$property_hook_override_pair(S,ppropertydesc_child,ppropertydesc_child) /\ $property_hook_parent_match(S,ppropertydesc_child,eps)',
    r'ppropertydesc_plain = ppropertydesc_parent[.ORIGIN = porigin_grand]',
    r'~$property_hook_override_pair(S,ppropertydesc_plain,ppropertydesc_child) /\ ~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_plain)',
    r'~$property_hook_inherited_backing(S[.LINKEDPARENTS = eps],ppropertydesc_child) /\ $property_hook_virtual(S[.LINKEDPARENTS = eps],ppropertydesc_child)',
    r'~$property_hook_inherited_backing(S[.CLASSES = eps],ppropertydesc_child) /\ ~$property_hook_inherited_backing(S[.SOURCES = eps],ppropertydesc_child)',
    r'~$property_hook_inherited_backing(S,ppropertydesc_child[.NAME = $ptascii("wrong")]) /\ ~$property_hook_inherited_backing(S,ppropertydesc_child[.ORIGIN = INTERNAL_PROPERTY "stdClass" $ptascii("value")])',
    r'S_rollback = $property_hook_link_finish(S,pclassdesc_child,S[.CLASSES = [pclassdesc_parent,pclassdesc_child[.PROPERTIES = [ppropertydesc_child[.TYPE = eps]]],pclassdesc_grand,pclassdesc_untyped_parent,pclassdesc_untyped_child]])',
    r'S_rollback.COMPLETION = UNSUPPORTED "inherited property hook override" /\ S_rollback.CLASSES = S.CLASSES /\ S_rollback.CLASSNAMES = S.CLASSNAMES /\ S_rollback.LINKEDPARENTS = S.LINKEDPARENTS /\ S_rollback.CLASSSTATICS = S.CLASSSTATICS',
    r'$origin_node(S.SOURCES,pclassdesc_child.ORIGIN) = (NStmtClass phpType14_class phpType24_class phpType3_class phpType44_class phpType42_class phpType23_class metadata_class)',
    r'pchheader_child = {KIND pclassdesc_child.KIND, NAME pclassdesc_child.NAME, ABSTRACT pclassdesc_child.ABSTRACT, FINAL pclassdesc_child.FINAL, READONLY pclassdesc_child.READONLY, PARENT pclassdesc_child.PARENT, INTERFACES pclassdesc_child.INTERFACES, BODY phpType23_class}',
    r'$origin_node(S.SOURCES,ppropertyhook_S_child.HOOK) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook phpType16_hook phpType39_hook metadata_hook)',
    r'$origin_node(S.SOURCES,ppropertyhook_S_child.PROPERTY) = (NPropertyItem phpType40_name phpType5_default metadata_property)',
    r'phpType38_hook = NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook phpType16_hook phpType39_hook metadata_hook',
    r'~$hook_body_backed(phpType39_hook,ppropertydesc_child.NAME) /\ phpType5_default = ABSENT /\ $pphook_class_shape(pchheader_child,phpType40_name,phpType38_hook) /\ ~$pphook_class_shape(pchheader_child[.ABSTRACT = true],phpType40_name,phpType38_hook) /\ ~$pphook_class_shape(pchheader_child[.FINAL = true],phpType40_name,phpType38_hook)',
    r'~$call_context_valid(S_this_entered,pcallcontext_hook_S_this[.LEXICAL_CLASS = (porigin_parent)],S_this_entered.CVS) /\ ~$call_context_valid(S_this_entered,pcallcontext_hook_S_this[.CALLED_CLASS = (porigin_child)],S_this_entered.CVS)',
]
DERIVED += [
    r'~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.DEFAULT = ppropertydesc_parent.DEFAULT])',
    r'S.SOURCES = pcunit :: pcunit_tail*',
    r'ppropertyhook_S_child.HOOK = PORIGIN n_unit pcpath_hook',
    r'pcunit.ID = n_unit',
    r'phpType38_byref = NPropertyHook phpType14_hook phpType24_hook (BOOLEAN true) phpType11_hook phpType16_hook phpType39_hook metadata_hook',
    r'S_byref = S[.SOURCES = pcunit[.OCCURRENCES = $eh_replace(pcunit.OCCURRENCES,pcpath_hook,phpType38_byref)] :: pcunit_tail*]',
    r'~$property_hook_override_pair(S_byref,ppropertydesc_parent,ppropertydesc_child) /\ ~$property_hook_inherited_backing(S_byref,ppropertydesc_child)',
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--group', choices=['all', 'scalar', 'lifetime'], default='all')
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'effective_backed_get_hook_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    selections = [('scalar', SCALAR, DERIVED), ('lifetime', LIFETIME, [])]
    cases = data['cases']
    if args.group == 'scalar':
        selections, cases = selections[:1], cases[:1]
    elif args.group == 'lifetime':
        selections, cases = selections[1:], cases[1:]
    sources = [HERE / ('effective-backed-get-hook-' + row[0] + '.php') for row in selections]
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
    out = Path(tempfile.mkdtemp(prefix='effective-backed-get-hook-protocol-', dir=ROOT / '.tools'))
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
                     'S_found = $eh_seek(S_initial,0,1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            content += '\ndec $eh_' + name + '() : bool\ndef $eh_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                condition = condition.replace('EXPECTED_OUTPUT', byte_expr(base64.b64decode(case['stdout_base64'])))
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $eh_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = (' + ' /\\ '.join('$eh_' + name + '()' for name, _, _ in selections) + ')\n'
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
