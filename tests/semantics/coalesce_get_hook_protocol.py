"""Reach source-derived hook coalescing, fallback and retained returned values."""
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

PREFIX = r'''dec $ch_output(pevent*) : ptbytes
dec $ch_stage(pstate, nat) : bool
def $ch_stage(S, 0) = true
  -- if $property_hook_plan(S) = (ppropertyhook)
  -- if $property_hook_coalesce_parent(S,ppropertyhook.SITE) =/= eps
def $ch_stage(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $property_hook_context_kind(pcallcontext)
def $ch_stage(S, 2) = true
  -- if S.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*
def $ch_stage(S, 3) = true
  -- if $ch_stage(S,0)
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES,porigin) = (NExprPropertyFetch (NExprVariable (BYTES "dGhpcw==") metadata_receiver) phpType20 metadata)
def $ch_stage(S, 4) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES "Ym94") metadata)) :: ptask*
def $ch_stage(S, 5) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES "a2VwdA==") metadata)) :: ptask*
def $ch_stage(S, 6) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
def $ch_stage(S,n) = false -- otherwise
dec $ch_seek(pstate,nat,nat) : pstate
def $ch_seek(S,n_stage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $ch_stage(S,n_stage) \/ n = 0
def $ch_seek(S,n_stage,n) = $ch_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$ch_stage(S,n_stage) /\ $(n > 0)
def $ch_seek(S,n_stage,n) = S -- otherwise
dec $ch_after(pstate,pstate) : pstate
def $ch_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $ch_guard(pstate) : bool
def $ch_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
def $ch_output(eps) = eps
def $ch_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $ch_output(pevent*)
dec $ch_slot(pstate,nat,ptbytes) : ppropstate?
def $ch_slot(S,n,ptbytes) = (ppropertyslot_value.STATE)
  -- if $objectprops_at(S.OBJECTPROPS,n) = (ppropertyslot*)
  -- if $property_slot_at(ppropertyslot*,ptbytes) = (ppropertyslot_value)
def $ch_slot(S,n,ptbytes) = eps -- otherwise
'''


def reach(name, previous, stage):
    return [f'{name}_found = $ch_seek({previous},{stage},1000)',
            fr'{name}_found.COMPLETION = NORMAL \/ {name}_found.COMPLETION = BUDGET',
            f'{name} = {name}_found[.COMPLETION = NORMAL]']


SCALAR = [
    r'$property_hook_plan(S) = (ppropertyhook)',
    r'S.TODO = (PROPERTY_PREP phpType20 z) :: (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_QUIET expression_right z z_right) :: ptask_tail*',
    r'$property_hook_function(S,ppropertyhook) = (pfunction_hook)',
    r'S.ORIGIN = (ppropertyhook.SITE) /\ $property_hook_coalesce_parent(S,ppropertyhook.SITE) = (porigin_parent) /\ $ch_guard(S)',
    r'$ch_slot(S,ppropertyhook.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT PNULL)) /\ $heap_owners($heap_prune($heap_graph(S)),HOBJECT ppropertyhook.OBJECT) = 1',
    r'PhpStep: S ~> S_call_raw',
    r'S_call_raw.TODO = [(CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook) eps 0 eps (ppropertyhook.SITE) z), PROPERTY_HOOK_RESULT ppropertyhook, ORIGIN_RETURN (porigin_parent), COALESCE_QUIET expression_right z z_right] ++ ptask_tail*',
    r'S_call_raw.RESULT = KNOWN PNULL /\ S_call_raw.BASE = BASE_VALUE (KNOWN PNULL) /\ S_call_raw.EVENTS = S.EVENTS /\ S_call_raw.STORE = S.STORE /\ S_call_raw.OBJECTPROPS = S.OBJECTPROPS',
    r'$target_nodes(PROPERTY_HOOK_TARGET ppropertyhook) = [HOBJECT ppropertyhook.OBJECT] /\ $task_nodes(PROPERTY_HOOK_RESULT ppropertyhook) = eps',
    r'S_call = $ch_after(S,S_call_raw)',
    r'$property_hook_pending_call(S_call,ppropertyhook) /\ $call_task_valid(S_call,PROPERTY_HOOK_RESULT ppropertyhook) /\ $heap_owners($heap_prune($heap_graph(S_call)),HOBJECT ppropertyhook.OBJECT) = 2 /\ $ch_guard(S_call)',
    *reach('S_entered','S_call',1),
    r'S_entered.CURRENT = (pcallcontext_hook)',
    r'S_entered.FRAMES = pframe_caller :: pframe_tail*',
    r'pcallcontext_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook /\ pcallcontext_hook.RECEIVER = (ppropertyhook.OBJECT) /\ pcallcontext_hook.INSTANCE = eps',
    r'pframe_caller.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_QUIET expression_right z z_right) :: ptask_tail*',
    r'$property_hook_context_valid(S_entered,pcallcontext_hook) /\ $call_receiver_roots(pcallcontext_hook) = [HOBJECT ppropertyhook.OBJECT] /\ $heap_owners($heap_prune($heap_graph(S_entered)),HOBJECT ppropertyhook.OBJECT) = 2 /\ $ch_guard(S_entered)',
    *reach('S_result','S_entered',2),
    r'S_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_QUIET expression_right z z_right) :: ptask_tail*',
    r'S_result.RESULT = KNOWN PNULL /\ S_result.CURRENT = eps /\ S_result.FRAMES = eps /\ $heap_owners($heap_prune($heap_graph(S_result)),HOBJECT ppropertyhook.OBJECT) = 1 /\ $ch_guard(S_result)',
    r'PhpStep: S_result ~> S_base_raw',
    r'S_base_raw.RESULT = KNOWN PNULL /\ S_base_raw.BASE = BASE_VALUE (KNOWN PNULL) /\ S_base_raw.EVENTS = S_result.EVENTS',
    r'S_base = $ch_after(S_result,S_base_raw)',
    r'PhpStep: S_base ~> S_parent_raw',
    r'S_parent_raw.ORIGIN = (porigin_parent) /\ S_parent_raw.TODO = (COALESCE_QUIET expression_right z z_right) :: ptask_tail* /\ S_parent_raw.RESULT = KNOWN PNULL',
    r'S_parent = $ch_after(S_base,S_parent_raw)',
    r'PhpStep: S_parent ~> S_rhs_raw',
    r'S_rhs_raw.TODO = [AT $origin_child((porigin_parent),[PCFIELD 1]) (EVAL expression_right), VALUE_COPY z_right] ++ ptask_tail*',
    r'S_rhs_raw.ORIGIN = (porigin_parent) /\ S_rhs_raw.RESULT = KNOWN PNULL /\ S_rhs_raw.BASE = BASE_VALUE (KNOWN PNULL) /\ S_rhs_raw.EVENTS = S_result.EVENTS',
    r'S_rhs = $ch_after(S_parent,S_rhs_raw)',
    r'$ch_guard(S_rhs)',
    *reach('S_this','S_rhs',3),
    r'$property_hook_plan(S_this) = (ppropertyhook_this)',
    r'S_this.TODO = (PROPERTY_PREP phpType20_this z_this) :: (ORIGIN_RETURN (porigin_parent_this)) :: (COALESCE_QUIET expression_right_this z_this z_right_this) :: ptask_this*',
    r'S_this.CURRENT = (pcallcontext_method)',
    r'ppropertyhook_this.OBJECT = ppropertyhook.OBJECT /\ $this_receiver(S_this) = (ppropertyhook.OBJECT) /\ S_this.RESULT = KNOWN (POBJECT ppropertyhook.OBJECT) /\ $heap_owners($heap_prune($heap_graph(S_this)),HOBJECT ppropertyhook.OBJECT) = 3 /\ $ch_output(S_this.EVENTS) = $ptascii("G|R|13|") /\ $ch_guard(S_this)',
    r'PhpStep: S_this ~> S_this_call_raw',
    r'S_this_call = $ch_after(S_this,S_this_call_raw)',
    r'$property_hook_pending_call(S_this_call,ppropertyhook_this) /\ $heap_owners($heap_prune($heap_graph(S_this_call)),HOBJECT ppropertyhook.OBJECT) = 3 /\ $ch_guard(S_this_call)',
    *reach('S_this_entered','S_this_call',1),
    r'S_this_entered.CURRENT = (pcallcontext_this_hook)',
    r'S_this_entered.FRAMES = pframe_method :: pframe_method_tail*',
    r'pcallcontext_this_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook_this /\ pframe_method.CONTEXT = (pcallcontext_method) /\ $property_hook_context_valid(S_this_entered,pcallcontext_this_hook) /\ $ch_guard(S_this_entered)',
    *reach('S_this_result','S_this_entered',2),
    r'S_this_result.RESULT = KNOWN PNULL /\ S_this_result.CURRENT = (pcallcontext_method) /\ $heap_owners($heap_prune($heap_graph(S_this_result)),HOBJECT ppropertyhook.OBJECT) = 2 /\ $ch_guard(S_this_result)',
    r'S_this_rhs_found = $drive_steps(S_this_result,3)',
    r'S_this_rhs_found.COMPLETION = NORMAL \/ S_this_rhs_found.COMPLETION = BUDGET',
    r'S_this_rhs = S_this_rhs_found[.COMPLETION = NORMAL]',
    r'S_this_rhs.TODO = [AT $origin_child((porigin_parent_this),[PCFIELD 1]) (EVAL expression_right_this), VALUE_COPY z_right_this] ++ ptask_this*',
    r'S_this_rhs.ORIGIN = (porigin_parent_this) /\ S_this_rhs.RESULT = KNOWN PNULL /\ S_this_rhs.BASE = BASE_VALUE (KNOWN PNULL) /\ S_this_rhs.EVENTS = S_this_result.EVENTS /\ $ch_guard(S_this_rhs)',
]

# Each branch is reached by executing the preceding original source states.
previous = 'S_this_rhs'
for label, backing, returned in [('zero','PINT 0','PINT 0'),('false','PBOOL false','PINT 7'),('seven','PINT 7','PBOOL false')]:
    for mode, stage, owners in [('cv',0,1),('this',3,2)]:
        name = 'S_' + label + '_' + mode
        hook = 'ppropertyhook_' + label + '_' + mode
        parent = 'porigin_' + label + '_' + mode
        tail = 'ptask_' + label + '_' + mode + '*'
        right = 'expression_' + label + '_' + mode
        line, right_line = 'z_' + label + '_' + mode, 'z_right_' + label + '_' + mode
        SCALAR += [
            *reach(name,previous,stage),
            f'$property_hook_plan({name}) = ({hook})',
            f'$ch_slot({name},{hook}.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT ({backing}))) /\\ {hook}.OBJECT = ppropertyhook.OBJECT /\\ $ch_guard({name})',
            *reach(name + '_result',name,2),
            f'{name}_result.TODO = (PROPERTY_HOOK_RESULT {hook}) :: (ORIGIN_RETURN ({parent})) :: (COALESCE_QUIET {right} {line} {right_line}) :: {tail}',
            f'{name}_result.RESULT = KNOWN ({returned}) /\\ $heap_owners($heap_prune($heap_graph({name}_result)),HOBJECT ppropertyhook.OBJECT) = {owners} /\\ $ch_guard({name}_result)',
            f'{name}_selected_found = $drive_steps({name}_result,3)',
            fr'{name}_selected_found.COMPLETION = NORMAL \/ {name}_selected_found.COMPLETION = BUDGET',
            f'{name}_selected = {name}_selected_found[.COMPLETION = NORMAL]',
            f'{name}_selected.ORIGIN = ({parent}) /\\ {name}_selected.TODO = {tail} /\\ {name}_selected.RESULT = KNOWN ({returned}) /\\ {name}_selected.BASE = BASE_VALUE (KNOWN PNULL) /\\ {name}_selected.EVENTS = {name}_result.EVENTS /\\ $ch_guard({name}_selected)',
        ]
        previous = name + '_selected'
SCALAR += [
    f'S_done = $drive({previous},10000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $ch_guard(S_done) /\ $ch_output(S_done.EVENTS) = EXPECTED_OUTPUT',
]

DERIVED = [
    r'S_no_marker = S[.TODO = (PROPERTY_PREP phpType20 z) :: (COALESCE_QUIET expression_right z z_right) :: ptask_tail*]',
    r'~$property_hook_pending(S_no_marker) /\ $property_hook_plan(S_no_marker) = eps',
    r'S_wrong_marker = S[.TODO = (PROPERTY_PREP phpType20 z) :: (ORIGIN_RETURN (ppropertyhook.SITE)) :: (COALESCE_QUIET expression_right z z_right) :: ptask_tail*]',
    r'$property_hook_pending(S_wrong_marker) /\ $property_hook_plan(S_wrong_marker) = eps',
    r'ptask_bad* = [ORIGIN_RETURN (ppropertyhook.SITE), COALESCE_QUIET expression_right z z_right] ++ ptask_tail*',
    r'~$property_hook_pending_call(S_call[.TODO = (CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook) eps 0 eps (ppropertyhook.SITE) z) :: (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask_bad*],ppropertyhook)',
    r'~$property_hook_frame(S_entered,pcallcontext_hook,pframe_caller[.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask_bad*],ppropertyhook)',
    r'~$property_hook_result_tail(S_result,ppropertyhook,(PROPERTY_HOOK_RESULT ppropertyhook) :: ptask_bad*) /\ ~$call_task_valid(S_result[.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask_bad*],PROPERTY_HOOK_RESULT ppropertyhook)',
    r'$property_hook_plan(S[.TODO = (PROPERTY_PREP phpType20 999) :: (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_QUIET expression_right 999 z_right) :: ptask_tail*]) = eps',
    r'$property_hook_plan(S[.TODO = (PROPERTY_PREP phpType20 z) :: (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_QUIET expression_right 999 z_right) :: ptask_tail*]) = eps',
    r'$property_hook_plan(S[.TODO = (PROPERTY_PREP phpType20 z) :: (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_QUIET expression_right z 999) :: ptask_tail*]) = eps',
    r'$property_hook_plan(S[.TODO = (PROPERTY_PREP phpType20 z) :: (ORIGIN_RETURN (porigin_parent)) :: (ISSET_RESULT false z) :: ptask_tail*]) = eps',
    r'~$call_task_valid(S_result,PROPERTY_HOOK_ISSET_RESULT ppropertyhook false) /\ ~$call_task_valid(S_result,PROPERTY_HOOK_ISSET_RESULT ppropertyhook true)',
    r'$property_hook_plan(S[.ORIGIN = (ppropertyhook.HOOK)]) = eps /\ $property_hook_plan(S[.SOURCES = eps]) = eps',
    r'~$property_hook_valid(S,ppropertyhook[.PROPERTY = ppropertyhook.HOOK],true) /\ ~$property_hook_valid(S,ppropertyhook[.HOOK = ppropertyhook.PROPERTY],true) /\ ~$property_hook_valid(S,ppropertyhook[.LINE = 999],true)',
    r'$property_hook_plan(S[.FUNCTIONS = [pfunction_hook[.NAME = $ptascii("wrong")]]]) = eps /\ $property_hook_plan(S[.FUNCTIONS = [pfunction_hook[.SIGNATURE.BYREF = true]]]) = eps',
    r'$origin_node(S.SOURCES,porigin_parent) = (NExprBinaryOpCoalesce expression_left expression_right metadata_parent)',
    r'$property_hook_plan(S[.TODO = (PROPERTY_PREP phpType20 z) :: (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_QUIET (NScalarInt (INTEGER 7) metadata_parent) z z_right) :: ptask_tail*]) = eps',
    r'porigin_parent = PORIGIN n pcpath_parent',
    r'S.SOURCES = pcunit :: pcunit_tail*',
    r'pcunit.ID = n',
    r'pcunit_empty = pcunit[.OCCURRENCES = [PCOCCURRENCE pcpath_parent (NExprEmpty expression_left metadata_parent), PCOCCURRENCE (pcpath_parent ++ [PCFIELD 0]) expression_left]]',
    r'S_empty_parent = S[.SOURCES = pcunit_empty :: pcunit_tail*]',
    r'$property_hook_plan(S_empty_parent) = eps /\ ~$property_hook_coalesce_tail(S_empty_parent,ppropertyhook,(ORIGIN_RETURN (porigin_parent)) :: (COALESCE_QUIET expression_right z z_right) :: ptask_tail*)',
    r'~$property_hook_result_tail(S_empty_parent,ppropertyhook,(PROPERTY_HOOK_RESULT ppropertyhook) :: (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_QUIET expression_right z z_right) :: ptask_tail*)',
]

LIFETIME = [
    r'$property_hook_plan(S) = (ppropertyhook)',
    r'S.TODO = (PROPERTY_PREP phpType20 z) :: (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_QUIET expression_right z z_right) :: ptask_tail*',
    r'$ch_slot(S,ppropertyhook.OBJECT,$ptascii("value")) = eps /\ $node_children(S,HOBJECT ppropertyhook.OBJECT) = eps /\ $heap_owners($heap_prune($heap_graph(S)),HOBJECT ppropertyhook.OBJECT) = 1 /\ $ch_guard(S)',
    r'PhpStep: S ~> S_call_raw',
    r'S_call = $ch_after(S,S_call_raw)',
    r'$property_hook_pending_call(S_call,ppropertyhook) /\ $heap_owners($heap_prune($heap_graph(S_call)),HOBJECT ppropertyhook.OBJECT) = 2 /\ $ch_guard(S_call)',
    *reach('S_entered','S_call',1),
    r'S_entered.CURRENT = (pcallcontext_hook)',
    r'pcallcontext_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook /\ $property_hook_context_valid(S_entered,pcallcontext_hook) /\ $ch_guard(S_entered)',
    *reach('S_result','S_entered',2),
    r'S_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_QUIET expression_right z z_right) :: ptask_tail*',
    r'S_result.RESULT = KNOWN (POBJECT n_leaf)',
    r'S_result.CURRENT = eps /\ S_result.FRAMES = eps',
    r'$lookup(S_result.ENV,$ptascii("weak")) = (n_weak_cell)',
    r'S_result.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
    r'$weakref_get(S_result,n_weak) = POBJECT n_leaf',
    r'$heap_owners($heap_prune($heap_graph(S_result)),HOBJECT n_leaf) = 1 /\ $heap_owners($heap_prune($heap_graph(S_result)),HOBJECT ppropertyhook.OBJECT) = 1 /\ $node_children(S_result,HOBJECT ppropertyhook.OBJECT) = eps /\ $task_nodes(PROPERTY_HOOK_RESULT ppropertyhook) = eps /\ $ch_guard(S_result)',
    r'$ch_output(S_result.EVENTS) = $ptascii("G|")',
    r'PhpStep: S_result ~> S_base_raw',
    r'S_base_raw.RESULT = KNOWN (POBJECT n_leaf) /\ S_base_raw.BASE = BASE_VALUE (KNOWN (POBJECT n_leaf)) /\ S_base_raw.EVENTS = S_result.EVENTS /\ $heap_owners($heap_prune($heap_graph(S_base_raw)),HOBJECT n_leaf) = 2',
    r'S_base = $ch_after(S_result,S_base_raw)',
    r'S_base.DESTRUCTION.OPERATIONS = eps /\ $weakref_get(S_base,n_weak) = POBJECT n_leaf /\ $heap_owners($heap_prune($heap_graph(S_base)),HOBJECT n_leaf) = 2 /\ $ch_guard(S_base)',
    r'PhpStep: S_base ~> S_parent_raw',
    r'S_parent_raw.ORIGIN = (porigin_parent) /\ S_parent_raw.TODO = (COALESCE_QUIET expression_right z z_right) :: ptask_tail* /\ S_parent_raw.RESULT = KNOWN (POBJECT n_leaf) /\ S_parent_raw.BASE = BASE_VALUE (KNOWN (POBJECT n_leaf))',
    r'S_parent = $ch_after(S_base,S_parent_raw)',
    r'$heap_owners($heap_prune($heap_graph(S_parent)),HOBJECT n_leaf) = 2 /\ S_parent.DESTRUCTION.OPERATIONS = eps /\ $ch_guard(S_parent)',
    r'PhpStep: S_parent ~> S_selected_raw',
    r'S_selected_raw.TODO = ptask_tail* /\ S_selected_raw.RESULT = KNOWN (POBJECT n_leaf) /\ S_selected_raw.BASE = BASE_VALUE (KNOWN PNULL) /\ S_selected_raw.EVENTS = S_result.EVENTS /\ $heap_owners($heap_prune($heap_graph(S_selected_raw)),HOBJECT n_leaf) = 1',
    r'S_selected = $ch_after(S_parent,S_selected_raw)',
    r'$weakref_get(S_selected,n_weak) = POBJECT n_leaf /\ S_selected.DESTRUCTION.OPERATIONS = eps /\ $heap_owners($heap_prune($heap_graph(S_selected)),HOBJECT n_leaf) = 1 /\ $ch_guard(S_selected)',
    *reach('S_box_unset','S_selected',4),
    r'$lookup(S_box_unset.ENV,$ptascii("kept")) = (n_kept_cell)',
    r'S_box_unset.STORE[n_kept_cell] = DEFINED (POBJECT n_leaf)',
    r'$heap_owners($heap_prune($heap_graph(S_box_unset)),HOBJECT n_leaf) = 1 /\ $weakref_get(S_box_unset,n_weak) = POBJECT n_leaf /\ $ch_output(S_box_unset.EVENTS) = $ptascii("G|HELD|") /\ $ch_guard(S_box_unset)',
    *reach('S_box_disposed','S_box_unset',6),
    r'~((HOBJECT ppropertyhook.OBJECT) <- S_box_disposed.ALLOCATIONS) /\ (HOBJECT n_leaf) <- S_box_disposed.ALLOCATIONS /\ $weakref_get(S_box_disposed,n_weak) = POBJECT n_leaf /\ $heap_owners($heap_prune($heap_graph(S_box_disposed)),HOBJECT n_leaf) = 1 /\ $ch_output(S_box_disposed.EVENTS) = $ptascii("G|HELD|B|") /\ $ch_guard(S_box_disposed)',
    *reach('S_kept_unset','S_box_disposed',5),
    r'S_kept_unset.STORE[n_kept_cell] = DEFINED (POBJECT n_leaf) /\ $heap_owners($heap_prune($heap_graph(S_kept_unset)),HOBJECT n_leaf) = 1 /\ $weakref_get(S_kept_unset,n_weak) = POBJECT n_leaf /\ $ch_output(S_kept_unset.EVENTS) = $ptascii("G|HELD|B|LIVE|") /\ $ch_guard(S_kept_unset)',
    r'PhpStep: S_kept_unset ~> S_unset_raw',
    r'S_unset_raw.STORE[n_kept_cell] = UNDEFINED /\ $heap_owners($heap_prune($heap_graph(S_unset_raw)),HOBJECT n_leaf) = 0 /\ S_unset_raw.EVENTS = S_kept_unset.EVENTS',
    r'S_release = $ch_after(S_kept_unset,S_unset_raw)',
    r'S_release.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
    r'$ch_guard(S_release)',
    *reach('S_disposed','S_release',6),
    r'$weakref_get(S_disposed,n_weak) = PNULL /\ ~((HOBJECT n_leaf) <- S_disposed.ALLOCATIONS) /\ $ch_output(S_disposed.EVENTS) = $ptascii("G|HELD|B|LIVE|D|") /\ $ch_guard(S_disposed)',
    r'S_done = $drive(S_disposed,10000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $weakref_get(S_done,n_weak) = PNULL /\ $ch_guard(S_done) /\ $ch_output(S_done.EVENTS) = EXPECTED_OUTPUT',
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'coalesce_get_hook_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    selections = [('scalar', SCALAR, DERIVED), ('lifetime', LIFETIME, [])]
    sources = [HERE / ('coalesce-get-hook-' + row[0] + '.php') for row in selections]
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
    out = Path(tempfile.mkdtemp(prefix='coalesce-get-hook-protocol-', dir=ROOT / '.tools'))
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
        for i, (source, case) in enumerate(zip(sources, data['cases'])):
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
        for selection, ast_fixture, source, case in zip(selections, fixtures, sources, data['cases']):
            name, clauses, negatives = selection
            setup = ['S_initial = $php_run(' + ast_fixture + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $ch_seek(S_initial,0,1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            content += '\ndec $ch_' + name + '() : bool\ndef $ch_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                condition = condition.replace('EXPECTED_OUTPUT', byte_expr(base64.b64decode(case['stdout_base64'])))
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $ch_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = ($ch_scalar() /\\ $ch_lifetime())\n'
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
