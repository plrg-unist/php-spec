"""Reach backed get-hook overrides, declaring scope, merged slots and returned-object cleanup."""
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

PREFIX = r'''dec $ho_output(pevent*) : ptbytes
def $ho_output(eps) = eps
def $ho_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $ho_output(pevent*)
dec $ho_stage(pstate,nat) : bool
def $ho_stage(S,0) = true
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $property_hook_plan(S[.COMPLETION = NORMAL]) =/= eps
def $ho_stage(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $property_hook_context_kind(pcallcontext)
def $ho_stage(S,2) = true
  -- if S.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*
def $ho_stage(S,3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $property_hook_context_kind(pcallcontext)
  -- if S.TODO = (PROPERTY_PREP (NIdentifier (BYTES "dmFsdWU=") metadata) z) :: (DIM_FETCH z) :: ptask*
  -- if ~$property_hook_pending(S)
def $ho_stage(S,4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $ptlc(pcallcontext.NAME) = $ptascii("hookoverridechild36::bias")
def $ho_stage(S,5) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES "Ym94") metadata)) :: ptask*
def $ho_stage(S,6) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
  -- if pdestructionoperation.SOURCE = UNSET (NExprVariable (BYTES "Ym94") metadata)
def $ho_stage(S,7) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $ptlc(pcallcontext.NAME) = $ptascii("hookoverridelifeparent36::__destruct")
def $ho_stage(S,8) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES "a2VwdA==") metadata)) :: ptask*
def $ho_stage(S,9) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
  -- if pdestructionoperation.SOURCE = UNSET (NExprVariable (BYTES "a2VwdA==") metadata)
def $ho_stage(S,n) = false -- otherwise
dec $ho_seek(pstate,nat,nat) : pstate
def $ho_seek(S,n_stage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $ho_stage(S,n_stage) \/ n = 0
def $ho_seek(S,n_stage,n) = $ho_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$ho_stage(S,n_stage) /\ $(n > 0)
def $ho_seek(S,n_stage,n) = $ho_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $ho_seek(S,n_stage,n) = S -- otherwise
dec $ho_after(pstate,pstate) : pstate
def $ho_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $ho_guard(pstate) : bool
def $ho_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $ho_slot(pstate,nat,ptbytes) : ppropstate?
def $ho_slot(S,n,ptbytes) = (ppropertyslot_value.STATE)
  -- if $objectprops_at(S.OBJECTPROPS,n) = (ppropertyslot*)
  -- if $property_slot_at(ppropertyslot*,ptbytes) = (ppropertyslot_value)
def $ho_slot(S,n,ptbytes) = eps -- otherwise
'''


def reach(name, previous, stage):
    return [f'{name}_found = $ho_seek({previous},{stage},1000)',
            fr'{name}_found.COMPLETION = NORMAL \/ {name}_found.COMPLETION = BUDGET',
            f'{name} = {name}_found[.COMPLETION = NORMAL]']


def classes(stem):
    answer=[]
    for role in ['Parent','Child','Grand']:
        lower=role.lower()
        answer += [f'$class_named(S.CLASSNAMES,$ptlc($ptascii("{stem}{role}36"))) = (porigin_{lower})',
                   f'$class_at(S.CLASSES,porigin_{lower}) = (pclassdesc_{lower})']
    answer += [r'$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_parent) /\ $class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_child)',
               r'|pclassdesc_parent.PROPERTIES| = 1 /\ |pclassdesc_child.PROPERTIES| = 1 /\ pclassdesc_grand.PROPERTIES = eps',
               r'ppropertydesc_parent = pclassdesc_parent.PROPERTIES[0]',
               r'ppropertydesc_child = pclassdesc_child.PROPERTIES[0]',
               r'$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child) /\ ~$property_hook_parent_overlap(S,pclassdesc_child.PROPERTIES,$promotion_override_parent_layout(S,pclassdesc_child)) /\ $property_layout(S,porigin_grand,|S.CLASSES|) = [ppropertydesc_child] /\ $ho_guard(S)']
    return answer


def prep(s, owner, called, backing):
    return [f'$property_hook_plan({s}) = (ppropertyhook_{s})',
            f'{s}.TODO = (PROPERTY_PREP phpType20_{s} z_{s}) :: (DIM_FETCH z_{s}) :: ptask_{s}*',
            f'$property_effective_desc({s},ppropertyhook_{s}.OBJECT,$ptascii("value")) = (ppropertydesc_{s})',
            f'$property_hook_function({s},ppropertyhook_{s}) = (pfunction_{s})',
            f'{s}.OBJECTS[ppropertyhook_{s}.OBJECT] = INSTANCE porigin_{called} /\\ ppropertydesc_{s} = ppropertydesc_{owner} /\\ ppropertyhook_{s}.PROPERTY = ppropertydesc_{owner}.ORIGIN /\\ $property_declaring_class({s}.CLASSES,ppropertyhook_{s}.PROPERTY) = (porigin_{owner}) /\\ $property_layout({s},porigin_{called},|{s}.CLASSES|) = [ppropertydesc_{owner}]',
            f'$target_lexical_class({s},PROPERTY_HOOK_TARGET ppropertyhook_{s}) = (porigin_{owner}) /\\ $target_called_class({s},PROPERTY_HOOK_TARGET ppropertyhook_{s}) = (porigin_{called}) /\\ $ho_slot({s},ppropertyhook_{s}.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT {backing}))) /\\ $ho_guard({s})']


def entered(s, previous, owner, called):
    return [*reach(s+'_entered',previous,1),
            f'{s}_entered.CURRENT = (pcallcontext_hook_{s})',
            f'{s}_entered.FRAMES = pframe_{s} :: pframe_tail_{s}*',
            f'pframe_{s}.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_{s}) :: ptask_{s}* /\\ pcallcontext_hook_{s}.TARGET = PROPERTY_HOOK_TARGET ppropertyhook_{s} /\\ pcallcontext_hook_{s}.FUNCTION = ppropertyhook_{s}.HOOK /\\ pcallcontext_hook_{s}.RECEIVER = (ppropertyhook_{s}.OBJECT)',
            f'pcallcontext_hook_{s}.LEXICAL_CLASS = (porigin_{owner}) /\\ pcallcontext_hook_{s}.CALLED_CLASS = (porigin_{called}) /\\ pfunction_{s}.NAME = pclassdesc_{owner}.NAME ++ $ptascii("::$value::get") /\\ $property_hook_frame({s}_entered,pcallcontext_hook_{s},pframe_{s},ppropertyhook_{s}) /\\ $ho_guard({s}_entered)']


def backing_steps(s, previous, value):
    return [*reach(s+'_backing',previous,3),
            f'{s}_backing.TODO = (PROPERTY_PREP phpType20_backing_{s} z_backing_{s}) :: (DIM_FETCH z_backing_{s}) :: ptask_backing_{s}*',
            f'$property_hook_backing({s}_backing,ppropertyhook_{s}.OBJECT,ppropertydesc_{s}) /\\ ~$property_hook_read_needed({s}_backing,ppropertyhook_{s}.OBJECT,$ptascii("value")) /\\ ~$property_hook_pending({s}_backing) /\\ $ho_guard({s}_backing)',
            f'PhpStep: {s}_backing ~> {s}_backing_base_raw',
            f'{s}_backing_base_raw.BASE = BASE_PROPERTY (POBJECT ppropertyhook_{s}.OBJECT) ($ptascii("value")) /\\ {s}_backing_base_raw.TODO = (DIM_FETCH z_backing_{s}) :: ptask_backing_{s}* /\\ {s}_backing_base_raw.EVENTS = {s}_backing.EVENTS /\\ {s}_backing_base_raw.OBJECTPROPS = {s}_backing.OBJECTPROPS',
            f'{s}_backing_base = $ho_after({s}_backing,{s}_backing_base_raw)',
            f'PhpStep: {s}_backing_base ~> {s}_backing_value_raw',
            f'{s}_backing_value_raw.COMPLETION = NORMAL /\\ {s}_backing_value_raw.RESULT = KNOWN (PINT {value}) /\\ {s}_backing_value_raw.TODO = ptask_backing_{s}* /\\ {s}_backing_value_raw.EVENTS = {s}_backing.EVENTS /\\ {s}_backing_value_raw.OBJECTPROPS = {s}_backing.OBJECTPROPS',
            f'{s}_backing_value = $ho_after({s}_backing_base,{s}_backing_value_raw)',
            f'$ho_guard({s}_backing_value)']


SCALAR=classes('HookOverride')+[
    r'$method_named(pclassdesc_child.METHODS,$ptascii("bias")) = (pmethoddesc_bias)',
    r'$method_named(pclassdesc_grand.METHODS,$ptascii("bias")) = (pmethoddesc_grand_bias)',
    r'$method_named(pclassdesc_parent.METHODS,$ptascii("parentRead")) = (pmethoddesc_parent_read)',
    r'$method_named(pclassdesc_child.METHODS,$ptascii("childRead")) = (pmethoddesc_child_read)',
    r'pmethoddesc_bias.VISIBILITY = PROPERTY_PRIVATE /\ pmethoddesc_bias.OWNER = porigin_child /\ pmethoddesc_grand_bias.OWNER = porigin_grand /\ pmethoddesc_bias.FUNCTION.ORIGIN =/= pmethoddesc_grand_bias.FUNCTION.ORIGIN',
]
previous='S'
output=''
for label,owner,called,value,answer,prefix,caller in [
    ('parent','parent','parent',100,101,'P',None),
    ('child','child','child',200,207,'C',None),
    ('grand','child','grand',200,207,'V',None),
    ('parent_this','child','grand',200,207,'T','parent'),
    ('child_this','child','grand',200,207,'U','child'),
    ('written','child','grand',300,307,'W',None),
]:
    s='S_'+label
    SCALAR += [f'{s} = S'] if label=='parent' else reach(s,previous,0)
    SCALAR += prep(s,owner,called,value)
    output += prefix
    SCALAR += [f'$ho_output({s}.EVENTS) = $ptascii("{output}") /\\ $heap_owners($heap_prune($heap_graph({s})),HOBJECT ppropertyhook_{s}.OBJECT) = {3 if caller else 1}']
    if caller:
        SCALAR += [f'{s}.CURRENT = (pcallcontext_{s})',
                   f'pcallcontext_{s}.FUNCTION = pmethoddesc_{caller}_read.FUNCTION.ORIGIN /\\ pcallcontext_{s}.LEXICAL_CLASS = (porigin_{caller}) /\\ pcallcontext_{s}.CALLED_CLASS = (porigin_grand) /\\ $this_receiver({s}) = (ppropertyhook_{s}.OBJECT)']
    else:
        SCALAR += [f'{s}.CURRENT = eps']
    prior=s
    if label=='grand':
        SCALAR += [f'PhpStep: {s} ~> {s}_call_raw',
                   f'{s}_call_raw.TODO = [(CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook_{s}) eps 0 eps (ppropertyhook_{s}.SITE) z_{s}), PROPERTY_HOOK_RESULT ppropertyhook_{s}] ++ ptask_{s}*',
                   f'{s}_call_raw.RESULT = KNOWN PNULL /\\ {s}_call_raw.BASE = BASE_VALUE (KNOWN PNULL) /\\ {s}_call_raw.EVENTS = {s}.EVENTS /\\ {s}_call_raw.OBJECTPROPS = {s}.OBJECTPROPS',
                   f'{s}_call = $ho_after({s},{s}_call_raw)',
                   f'$property_hook_pending_call({s}_call,ppropertyhook_{s}) /\\ $heap_owners($heap_prune($heap_graph({s}_call)),HOBJECT ppropertyhook_{s}.OBJECT) = 2 /\\ $task_nodes(PROPERTY_HOOK_RESULT ppropertyhook_{s}) = eps /\\ $ho_guard({s}_call)']
        prior=s+'_call'
    SCALAR += entered(s,prior,owner,called)
    prior=s+'_entered'
    if label=='grand':
        SCALAR += backing_steps(s,prior,200)
        SCALAR += [*reach(s+'_private',s+'_backing_value',4),
                   f'{s}_private.CURRENT = (pcallcontext_private)',
                   f'pcallcontext_private.FUNCTION = pmethoddesc_bias.FUNCTION.ORIGIN /\\ pcallcontext_private.LEXICAL_CLASS = (porigin_child) /\\ pcallcontext_private.CALLED_CLASS = (porigin_grand) /\\ pcallcontext_private.RECEIVER = (ppropertyhook_{s}.OBJECT) /\\ $ho_guard({s}_private)']
        prior=s+'_private'
    SCALAR += [*reach(s+'_result',prior,2),
               f'{s}_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_{s}) :: ptask_{s}* /\\ {s}_result.RESULT = KNOWN (PINT {answer}) /\\ {s}_result.CURRENT = {"(pcallcontext_"+s+")" if caller else "eps"}',
               f'$heap_owners($heap_prune($heap_graph({s}_result)),HOBJECT ppropertyhook_{s}.OBJECT) = {2 if caller else 1} /\\ $ho_slot({s}_result,ppropertyhook_{s}.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT {value}))) /\\ $ho_guard({s}_result)']
    output += ('P:' if owner=='parent' else 'C:') + 'HookOverride'+owner.capitalize()+'36/HookOverride'+called.capitalize()+'36|'
    SCALAR += [f'$ho_output({s}_result.EVENTS) = $ptascii("{output}")',
               f'PhpStep: {s}_result ~> {s}_base_raw',
               f'{s}_base_raw.RESULT = {s}_result.RESULT /\\ {s}_base_raw.BASE = BASE_VALUE {s}_result.RESULT /\\ {s}_base_raw.TODO = ptask_{s}* /\\ {s}_base_raw.EVENTS = {s}_result.EVENTS',
               f'{s}_base = $ho_after({s}_result,{s}_base_raw)',
               f'$ho_guard({s}_base)']
    output += str(answer)+('|' if caller else ':ONE|')
    previous=s+'_base'
SCALAR += [f'S_done = $drive({previous},10000)',
           r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $ho_output(S_done.EVENTS) = EXPECTED_OUTPUT /\ $ho_guard(S_done)']

LIFETIME=classes('HookOverrideLife')+[
    r'$method_named(pclassdesc_parent.METHODS,$ptascii("parentRead")) = (pmethoddesc_read)',
    r'$method_named(pclassdesc_parent.METHODS,$ptascii("__destruct")) = (pmethoddesc_destructor)',
    'S_life = S',
]+prep('S_life','child','grand',200)+[
    r'S_life.CURRENT = (pcallcontext_read)',
    r'pcallcontext_read.FUNCTION = pmethoddesc_read.FUNCTION.ORIGIN /\ pcallcontext_read.LEXICAL_CLASS = (porigin_parent) /\ pcallcontext_read.CALLED_CLASS = (porigin_grand) /\ $heap_owners($heap_prune($heap_graph(S_life)),HOBJECT ppropertyhook_S_life.OBJECT) = 3 /\ $ho_output(S_life.EVENTS) = $ptascii("ONE|")',
    r'PhpStep: S_life ~> S_life_call_raw',
    r'S_life_call_raw.TODO = [(CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook_S_life) eps 0 eps (ppropertyhook_S_life.SITE) z_S_life), PROPERTY_HOOK_RESULT ppropertyhook_S_life] ++ ptask_S_life*',
    r'S_life_call = $ho_after(S_life,S_life_call_raw)',
    r'$heap_owners($heap_prune($heap_graph(S_life_call)),HOBJECT ppropertyhook_S_life.OBJECT) = 3 /\ $property_hook_pending_call(S_life_call,ppropertyhook_S_life) /\ $ho_guard(S_life_call)',
]+entered('S_life','S_life_call','child','grand')+[
    r'pframe_S_life.CONTEXT = (pcallcontext_read) /\ $heap_owners($heap_prune($heap_graph(S_life_entered)),HOBJECT ppropertyhook_S_life.OBJECT) = 3',
]+backing_steps('S_life','S_life_entered',200)+[
    *reach('S_result','S_life_backing_value',2),
    r'S_result.RESULT = KNOWN (POBJECT n_leaf)',
    r'S_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_S_life) :: ptask_S_life* /\ S_result.CURRENT = (pcallcontext_read) /\ $heap_owners($heap_prune($heap_graph(S_result)),HOBJECT n_leaf) = 1 /\ $heap_owners($heap_prune($heap_graph(S_result)),HOBJECT ppropertyhook_S_life.OBJECT) = 2 /\ $task_nodes(PROPERTY_HOOK_RESULT ppropertyhook_S_life) = eps /\ $node_children(S_result,HOBJECT ppropertyhook_S_life.OBJECT) = eps /\ $ho_guard(S_result)',
    r'S_result.GLOBALTABLE = (psymboltable_global)',
    r'$lookup(psymboltable_global.ENV,$ptascii("weak")) = (n_weak_cell)',
    r'S_result.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
    r'$lookup(psymboltable_global.ENV,$ptascii("weak_box")) = (n_weak_box_cell)',
    r'S_result.STORE[n_weak_box_cell] = DEFINED (POBJECT n_weak_box)',
    r'$weakref_get(S_result,n_weak) = POBJECT n_leaf /\ $weakref_get(S_result,n_weak_box) = POBJECT ppropertyhook_S_life.OBJECT /\ $ho_output(S_result.EVENTS) = $ptascii("ONE|C200|")',
    r'PhpStep: S_result ~> S_base_raw',
    r'S_base_raw.RESULT = KNOWN (POBJECT n_leaf) /\ S_base_raw.BASE = BASE_VALUE (KNOWN (POBJECT n_leaf)) /\ S_base_raw.TODO = ptask_S_life* /\ S_base_raw.EVENTS = S_result.EVENTS /\ $heap_owners($heap_prune($heap_graph(S_base_raw)),HOBJECT n_leaf) = 2',
    r'S_base = $ho_after(S_result,S_base_raw)',
    r'$heap_owners($heap_prune($heap_graph(S_base)),HOBJECT n_leaf) = 2 /\ $ho_guard(S_base)',
    *reach('S_box_unset','S_base',5),
    r'$lookup(S_box_unset.ENV,$ptascii("kept")) = (n_kept_cell)',
    r'S_box_unset.STORE[n_kept_cell] = DEFINED (POBJECT n_leaf)',
    r'$heap_owners($heap_prune($heap_graph(S_box_unset)),HOBJECT n_leaf) = 1 /\ $weakref_get(S_box_unset,n_weak) = POBJECT n_leaf /\ $ho_output(S_box_unset.EVENTS) = $ptascii("ONE|C200|HELD|") /\ $ho_slot(S_box_unset,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT 200))) /\ $ho_guard(S_box_unset)',
    r'PhpStep: S_box_unset ~> S_box_raw',
    r'$lookup(S_box_raw.ENV,$ptascii("box")) = eps /\ $heap_owners($heap_prune($heap_graph(S_box_raw)),HOBJECT ppropertyhook_S_life.OBJECT) = 0 /\ S_box_raw.EVENTS = S_box_unset.EVENTS',
    r'S_box_release = $ho_after(S_box_unset,S_box_raw)',
    *reach('S_destructor','S_box_release',7),
    r'S_destructor.CURRENT = (pcallcontext_destructor)',
    r'pcallcontext_destructor.FUNCTION = pmethoddesc_destructor.FUNCTION.ORIGIN /\ pcallcontext_destructor.LEXICAL_CLASS = (porigin_parent) /\ pcallcontext_destructor.CALLED_CLASS = (porigin_grand) /\ pcallcontext_destructor.RECEIVER = (ppropertyhook_S_life.OBJECT) /\ $heap_owners($heap_prune($heap_graph(S_destructor)),HOBJECT n_leaf) = 1 /\ $ho_slot(S_destructor,ppropertyhook_S_life.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT 200))) /\ $ho_guard(S_destructor)',
    *reach('S_box_disposed','S_destructor',6),
    r'~((HOBJECT ppropertyhook_S_life.OBJECT) <- S_box_disposed.ALLOCATIONS) /\ (HOBJECT n_leaf) <- S_box_disposed.ALLOCATIONS /\ $weakref_get(S_box_disposed,n_weak_box) = PNULL /\ $weakref_get(S_box_disposed,n_weak) = POBJECT n_leaf /\ $heap_owners($heap_prune($heap_graph(S_box_disposed)),HOBJECT n_leaf) = 1 /\ $ho_output(S_box_disposed.EVENTS) = $ptascii("ONE|C200|HELD|B200|") /\ $ho_guard(S_box_disposed)',
    *reach('S_kept_unset','S_box_disposed',8),
    r'$heap_owners($heap_prune($heap_graph(S_kept_unset)),HOBJECT n_leaf) = 1 /\ $weakref_get(S_kept_unset,n_weak) = POBJECT n_leaf /\ $ho_output(S_kept_unset.EVENTS) = $ptascii("ONE|C200|HELD|B200|BN|LIVE|") /\ $ho_guard(S_kept_unset)',
    r'PhpStep: S_kept_unset ~> S_kept_raw',
    r'$lookup(S_kept_raw.ENV,$ptascii("kept")) = eps /\ $heap_owners($heap_prune($heap_graph(S_kept_raw)),HOBJECT n_leaf) = 0 /\ S_kept_raw.EVENTS = S_kept_unset.EVENTS',
    r'S_kept_release = $ho_after(S_kept_unset,S_kept_raw)',
    *reach('S_leaf_disposed','S_kept_release',9),
    r'~((HOBJECT n_leaf) <- S_leaf_disposed.ALLOCATIONS) /\ $weakref_get(S_leaf_disposed,n_weak) = PNULL /\ $ho_output(S_leaf_disposed.EVENTS) = $ptascii("ONE|C200|HELD|B200|BN|LIVE|D|") /\ $ho_guard(S_leaf_disposed)',
    r'S_done = $drive(S_leaf_disposed,10000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $weakref_get(S_done,n_weak) = PNULL /\ $weakref_get(S_done,n_weak_box) = PNULL /\ $ho_output(S_done.EVENTS) = EXPECTED_OUTPUT /\ $ho_guard(S_done)',
]

DERIVED=[
    r'~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.TYPE = eps]) /\ ~$property_hook_override_pair(S,ppropertydesc_parent,ppropertydesc_child[.NAME = $ptascii("wrong")])',
    r'~$property_hook_override_backed(S,ppropertydesc_child[.FINAL = true]) /\ ~$property_hook_override_backed(S,ppropertydesc_child[.SETVISIBILITY = (PROPERTY_PROTECTED)]) /\ ~$property_hook_override_backed(S,ppropertydesc_child[.READONLY = true]) /\ ~$property_hook_override_backed(S,ppropertydesc_child[.VISIBILITY = PROPERTY_PROTECTED])',
    r'~$property_hook_override_backed(S[.SOURCES = eps],ppropertydesc_child) /\ ~$property_hook_override_backed(S,ppropertydesc_child[.ORIGIN = porigin_grand])',
    r'$property_hook_parent_match(S,ppropertydesc_child,eps) /\ ~$property_hook_parent_match(S,ppropertydesc_child,(ppropertydesc_parent))',
    r'ppropertydesc_plain = ppropertydesc_parent[.ORIGIN = porigin_grand]',
    r'$property_hook_parent_match(S,ppropertydesc_child,(ppropertydesc_plain)) /\ $property_hook_parent_match(S,ppropertydesc_plain,(ppropertydesc_parent))',
    r'S_rollback = $property_hook_link_finish(S,pclassdesc_child,S[.CLASSES = [pclassdesc_parent,pclassdesc_child[.PROPERTIES = [ppropertydesc_child[.TYPE = eps]]],pclassdesc_grand]])',
    r'S_rollback.COMPLETION = UNSUPPORTED "inherited property hook override" /\ S_rollback.CLASSES = S.CLASSES /\ S_rollback.CLASSNAMES = S.CLASSNAMES /\ S_rollback.LINKEDPARENTS = S.LINKEDPARENTS /\ S_rollback.CLASSSTATICS = S.CLASSSTATICS',
    r'$origin_node(S.SOURCES,pclassdesc_child.ORIGIN) = (NStmtClass phpType14_class phpType24_class phpType3_class phpType44_class phpType42_class phpType23_class metadata_class)',
    r'pchheader_child = {KIND pclassdesc_child.KIND, NAME pclassdesc_child.NAME, ABSTRACT pclassdesc_child.ABSTRACT, FINAL pclassdesc_child.FINAL, READONLY pclassdesc_child.READONLY, PARENT pclassdesc_child.PARENT, INTERFACES pclassdesc_child.INTERFACES, BODY phpType23_class}',
    r'$origin_node(S.SOURCES,ppropertyhook_S_child.HOOK) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook phpType16_hook phpType39_hook metadata_hook)',
    r'phpType38_hook = NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook phpType16_hook phpType39_hook metadata_hook',
    r'$origin_node(S.SOURCES,ppropertydesc_child.ORIGIN) = (NPropertyItem phpType40_name phpType5_default metadata_property)',
    r'$pphook_class_shape(pchheader_child,phpType40_name,phpType38_hook) /\ ~$pphook_class_shape(pchheader_child[.ABSTRACT = true],phpType40_name,phpType38_hook) /\ ~$pphook_class_shape(pchheader_child[.FINAL = true],phpType40_name,phpType38_hook)',
    r'phpType38_virtual = NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook phpType16_hook (NScalarInt (INTEGER 7) metadata_hook) metadata_hook',
    r'~$pphook_class_shape(pchheader_child,phpType40_name,phpType38_virtual) /\ $pphook_class_shape(pchheader_child[.PARENT = eps],phpType40_name,phpType38_virtual)',
    r'S.SOURCES = pcunit :: pcunit_tail*',
    r'porigin_hook_child = ppropertyhook_S_child.HOOK',
    r'porigin_hook_child = PORIGIN n_unit pcpath_hook',
    r'pcunit.ID = n_unit',
    r'S_virtual = S[.SOURCES = pcunit[.OCCURRENCES = $eval_order_set_occurrence(pcunit.OCCURRENCES,pcpath_hook,phpType38_virtual)] :: pcunit_tail*]',
    r'~$property_hook_override_pair(S_virtual,ppropertydesc_parent,ppropertydesc_child) /\ $property_hook_parent_match(S_virtual,ppropertydesc_child,(ppropertydesc_parent))',
    r'ppropertyhook_wrong = ppropertyhook_S_grand[.PROPERTY = ppropertyhook_S_parent.PROPERTY][.HOOK = ppropertyhook_S_parent.HOOK]',
    r'~$property_hook_valid(S_grand,ppropertyhook_wrong,true) /\ ~$property_hook_pending_call(S_grand_call,ppropertyhook_wrong)',
    r'~$property_hook_context_valid(S_grand_entered,pcallcontext_hook_S_grand[.LEXICAL_CLASS = (porigin_parent)]) /\ ~$property_hook_context_valid(S_grand_entered,pcallcontext_hook_S_grand[.CALLED_CLASS = (porigin_child)])',
]



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'backed_get_hook_override_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    selections = [('scalar', SCALAR, DERIVED), ('lifetime', LIFETIME, [])]
    cases = data['cases']
    sources = [HERE / ('backed-get-hook-override-' + row[0] + '.php') for row in selections]
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
    out = Path(tempfile.mkdtemp(prefix='backed-get-hook-override-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    derived = sum(len(row[2]) for row in selections)
    reached = sum(5 + len(row[1]) for row in selections)
    report = {'revision': revision, 'inputs': before, 'profile': profile, 'module_count': len(modules),
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
                     'S_found = $ho_seek(S_initial,0,1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            content += '\ndec $ho_' + name + '() : bool\ndef $ho_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                condition = condition.replace('EXPECTED_OUTPUT', byte_expr(base64.b64decode(case['stdout_base64'])))
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $ho_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = (' + ' /\\ '.join('$ho_' + name + '()' for name, _, _ in selections) + ')\n'
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
