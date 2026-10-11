"""Reach backed get-hook += values, selected receiver stores and RV-first error cleanup."""
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

PREFIX = r'''dec $hac_output(pevent*) : ptbytes
def $hac_output(eps) = eps
def $hac_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $hac_output(pevent*)
dec $hac_stage(pstate,nat) : bool
def $hac_stage(S,0) = true
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $property_hook_compound_plan(S[.COMPLETION = NORMAL]) = (ppropertyhook)
def $hac_stage(S,1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $property_hook_context_kind(pcallcontext)
def $hac_stage(S,2) = true
  -- if S.TODO = (PROPERTY_HOOK_COMPOUND_RESULT ppropertyhook pbase i z) :: ptask*
def $hac_stage(S,3) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
  -- if pdestructionoperation.SOURCE = PROPERTY_HOOK_COMPOUND_FINISH ppropertyhook pbase i z
def $hac_stage(S,4) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
  -- if pdestructionoperation.SOURCE = PROPERTY_HOOK_COMPOUND_RESULT ppropertyhook pbase i z
def $hac_stage(S,5) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n) :: ptask*
def $hac_stage(S,n) = false -- otherwise
dec $hac_seek(pstate,nat,nat) : pstate
def $hac_seek(S,n_stage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $hac_stage(S,n_stage) \/ n = 0
def $hac_seek(S,n_stage,n) = $hac_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$hac_stage(S,n_stage) /\ $(n > 0)
def $hac_seek(S,n_stage,n) = $hac_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $hac_seek(S,n_stage,n) = S -- otherwise
dec $hac_after(pstate,pstate) : pstate
def $hac_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $hac_guard(pstate) : bool
def $hac_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $hac_slot(pstate,nat,ptbytes) : ppropstate?
def $hac_slot(S,n,ptbytes) = (ppropertyslot_value.STATE)
  -- if $objectprops_at(S.OBJECTPROPS,n) = (ppropertyslot*)
  -- if $property_slot_at(ppropertyslot*,ptbytes) = (ppropertyslot_value)
def $hac_slot(S,n,ptbytes) = eps -- otherwise
'''


def reach(name, previous, stage):
    return [f'{name}_found = $hac_seek({previous},{stage},1000)',
            fr'{name}_found.COMPLETION = NORMAL \/ {name}_found.COMPLETION = BUDGET',
            f'{name} = {name}_found[.COMPLETION = NORMAL]']


def prep(s):
    return [f'$property_hook_compound_plan({s}) = (ppropertyhook_{s})',
            f'{s}.TODO = (COMPOUND_APPLY ADD pbase_{s} false z_{s}) :: ptask_{s}*',
            f'pbase_{s} = BASE_PROPERTY_PENDING pbase_receiver_{s} poperand_name_{s} z_receiver_{s}',
            f'{s}.ORIGIN = (porigin_{s})',
            f'$origin_node({s}.SOURCES,porigin_{s}) = (NExprAssignOpPlus expression_target_{s} expression_rhs_{s} metadata_{s})',
            f'{s}.RESULT = KNOWN (PINT 3) /\\ $property_hook_compound_source({s},ppropertyhook_{s},pbase_{s},z_{s}) /\\ $hac_slot({s},ppropertyhook_{s}.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT 100))) /\\ $hac_guard({s})']


def result(s, previous, returned):
    return [*reach(s+'_result',previous,2),
            f'{s}_result.TODO = (PROPERTY_HOOK_COMPOUND_RESULT ppropertyhook_{s} pbase_{s} 3 z_{s}) :: (ORIGIN_RETURN (porigin_{s})) :: (COMPOUND_PREP ADD expression_target_{s} expression_rhs_{s} z_{s}) :: ptask_{s}*',
            f'{s}_result.RESULT = KNOWN ({returned}) /\\ $property_hook_result_tail({s}_result,ppropertyhook_{s},{s}_result.TODO) /\\ $call_task_valid({s}_result,PROPERTY_HOOK_COMPOUND_RESULT ppropertyhook_{s} pbase_{s} 3 z_{s}) /\\ $task_nodes(PROPERTY_HOOK_COMPOUND_RESULT ppropertyhook_{s} pbase_{s} 3 z_{s}) = [HOBJECT ppropertyhook_{s}.OBJECT] /\\ $hac_slot({s}_result,ppropertyhook_{s}.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT 100))) /\\ $hac_guard({s}_result)']


def math(s, answer):
    return [f'PhpStep: {s}_result ~> {s}_math_raw',
            f'{s}_math_raw.TODO = (PROPERTY_HOOK_COMPOUND_FINISH ppropertyhook_{s} pbase_{s} 3 z_{s}) :: (ORIGIN_RETURN (porigin_{s})) :: (COMPOUND_PREP ADD expression_target_{s} expression_rhs_{s} z_{s}) :: ptask_{s}* /\\ {s}_math_raw.COMPLETION = NORMAL /\\ {s}_math_raw.RESULT = KNOWN (PINT {answer}) /\\ {s}_math_raw.BASE = BASE_VALUE (KNOWN PNULL) /\\ {s}_math_raw.EVENTS = {s}_result.EVENTS /\\ $hac_slot({s}_math_raw,ppropertyhook_{s}.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT {answer})))',
            f'{s}_math = $hac_after({s}_result,{s}_math_raw)',
            f'$call_task_valid({s}_math,PROPERTY_HOOK_COMPOUND_FINISH ppropertyhook_{s} pbase_{s} 3 z_{s}) /\\ $task_nodes(PROPERTY_HOOK_COMPOUND_FINISH ppropertyhook_{s} pbase_{s} 3 z_{s}) = [HOBJECT ppropertyhook_{s}.OBJECT] /\\ $hac_guard({s}_math)',
            f'PhpStep: {s}_math ~> {s}_finish_raw',
            f'{s}_finish_raw.TODO = (ORIGIN_RETURN (porigin_{s})) :: ptask_{s}* /\\ {s}_finish_raw.RESULT = KNOWN (PINT {answer}) /\\ {s}_finish_raw.EVENTS = {s}_result.EVENTS',
            f'{s}_finish = $hac_after({s}_math,{s}_finish_raw)']


SCALAR = []
previous = 'S'
output = ''
for mode, returned, answer in [('null','PNULL',3),('false','PBOOL false',3),('zero','PINT 0',3),('seven','PINT 7',10)]:
    for receiver in ['cv','this']:
        s='S_'+mode+'_'+receiver
        SCALAR += [f'{s} = S'] if not SCALAR else reach(s,previous,0)
        SCALAR += prep(s)
        owners=1 if receiver=='cv' else 3
        output += 'R|'
        SCALAR += [f'$hac_slot({s},ppropertyhook_{s}.OBJECT,$ptascii("returned")) = (PROP_VALUE (DIRECT ({returned}))) /\\ $heap_owners($heap_prune($heap_graph({s})),HOBJECT ppropertyhook_{s}.OBJECT) = {owners} /\\ $hac_output({s}.EVENTS) = $ptascii("{output}")']
        if receiver=='this':
            SCALAR += [f'{s}.CURRENT = (pcallcontext_{s})',f'$this_receiver({s}) = (ppropertyhook_{s}.OBJECT) /\\ $base_nodes(pbase_{s}) = [HOBJECT ppropertyhook_{s}.OBJECT]']
        else:
            SCALAR += [f'{s}.CURRENT = eps /\\ $base_nodes(pbase_{s}) = eps']
        if mode=='null':
            SCALAR += [f'PhpStep: {s} ~> {s}_call_raw',
                       f'{s}_call_raw.TODO = [(CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook_{s}) eps 0 eps (ppropertyhook_{s}.SITE) ppropertyhook_{s}.LINE), PROPERTY_HOOK_COMPOUND_RESULT ppropertyhook_{s} pbase_{s} 3 z_{s}, ORIGIN_RETURN (porigin_{s}), COMPOUND_PREP ADD expression_target_{s} expression_rhs_{s} z_{s}] ++ ptask_{s}*',
                       f'{s}_call_raw.ORIGIN = (ppropertyhook_{s}.SITE) /\\ {s}_call_raw.RESULT = KNOWN PNULL /\\ {s}_call_raw.BASE = BASE_VALUE (KNOWN PNULL) /\\ {s}_call_raw.OBJECTPROPS = {s}.OBJECTPROPS /\\ {s}_call_raw.EVENTS = {s}.EVENTS',
                       f'{s}_call = $hac_after({s},{s}_call_raw)',
                       f'$property_hook_pending_call({s}_call,ppropertyhook_{s}) /\\ $call_task_valid({s}_call,PROPERTY_HOOK_COMPOUND_RESULT ppropertyhook_{s} pbase_{s} 3 z_{s}) /\\ $heap_owners($heap_prune($heap_graph({s}_call)),HOBJECT ppropertyhook_{s}.OBJECT) = {3 if receiver=="cv" else 4} /\\ $hac_guard({s}_call)',
                       *reach(s+'_entered',s+'_call',1),
                       f'{s}_entered.CURRENT = (pcallcontext_hook_{s})',
                       f'{s}_entered.FRAMES = pframe_{s} :: pframe_tail_{s}*',
                       f'pframe_{s}.TODO = (PROPERTY_HOOK_COMPOUND_RESULT ppropertyhook_{s} pbase_{s} 3 z_{s}) :: (ORIGIN_RETURN (porigin_{s})) :: (COMPOUND_PREP ADD expression_target_{s} expression_rhs_{s} z_{s}) :: ptask_{s}*',
                       f'pcallcontext_hook_{s}.TARGET = PROPERTY_HOOK_TARGET ppropertyhook_{s} /\\ pcallcontext_hook_{s}.RECEIVER = (ppropertyhook_{s}.OBJECT) /\\ $property_hook_frame({s}_entered,pcallcontext_hook_{s},pframe_{s},ppropertyhook_{s}) /\\ $heap_owners($heap_prune($heap_graph({s}_entered)),HOBJECT ppropertyhook_{s}.OBJECT) = {3 if receiver=="cv" else 4} /\\ $hac_guard({s}_entered)']
            prior=s+'_entered'
        else: prior=s
        SCALAR += result(s,prior,returned)
        output += 'G|'
        SCALAR += [f'{s}_result.CURRENT = {"eps" if receiver=="cv" else "(pcallcontext_"+s+")"} /\\ $heap_owners($heap_prune($heap_graph({s}_result)),HOBJECT ppropertyhook_{s}.OBJECT) = {2 if receiver=="cv" else 3} /\\ $hac_output({s}_result.EVENTS) = $ptascii("{output}")']
        SCALAR += math(s,answer)
        SCALAR += [f'~$destructor_operational({s}_finish) /\\ {s}_finish.DESTRUCTION.OPERATIONS = eps /\\ $heap_owners($heap_prune($heap_graph({s}_math)),HOBJECT ppropertyhook_{s}.OBJECT) = {2 if receiver=="cv" else 3} /\\ $heap_owners($heap_prune($heap_graph({s}_finish)),HOBJECT ppropertyhook_{s}.OBJECT) = {1 if receiver=="cv" else 2} /\\ $hac_guard({s}_finish)',
                   f'PhpStep: {s}_finish ~> {s}_parent_raw',
                   f'{s}_parent_raw.ORIGIN = (porigin_{s}) /\\ {s}_parent_raw.TODO = ptask_{s}* /\\ {s}_parent_raw.RESULT = KNOWN (PINT {answer}) /\\ {s}_parent_raw.EVENTS = {s}_result.EVENTS',
                   f'{s}_parent = $hac_after({s}_finish,{s}_parent_raw)',
                   f'$hac_guard({s}_parent)']
        output += ('C' if receiver=='cv' else 'T')+f'{answer}:{answer}|'
        previous=s+'_parent'
SCALAR += [f'S_done = $drive({previous},10000)',r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $hac_guard(S_done) /\ $hac_output(S_done.EVENTS) = EXPECTED_OUTPUT']

REBIND = ['S_rhs = S']+prep('S_rhs')+[
    r'$lookup(S_rhs.ENV,$ptascii("weak")) = (n_weak_rhs_cell)',
    r'S_rhs.STORE[n_weak_rhs_cell] = DEFINED (POBJECT n_weak_rhs)',
    r'$weakref_get(S_rhs,n_weak_rhs) = PNULL /\ $hac_slot(S_rhs,ppropertyhook_S_rhs.OBJECT,$ptascii("label")) = (PROP_VALUE (DIRECT (PINT 2))) /\ $base_nodes(pbase_S_rhs) = eps /\ $heap_owners($heap_prune($heap_graph(S_rhs)),HOBJECT ppropertyhook_S_rhs.OBJECT) = 1 /\ $hac_output(S_rhs.EVENTS) = $ptascii("R0|D1:100|RN|")',
]+result('S_rhs','S_rhs','PINT 7')+math('S_rhs',10)+[
    r'$heap_owners($heap_prune($heap_graph(S_rhs_result)),HOBJECT ppropertyhook_S_rhs.OBJECT) = 2 /\ $heap_owners($heap_prune($heap_graph(S_rhs_finish)),HOBJECT ppropertyhook_S_rhs.OBJECT) = 1 /\ $hac_output(S_rhs_finish.EVENTS) = $ptascii("R0|D1:100|RN|G2|") /\ $hac_guard(S_rhs_finish)',
    *reach('S_getter','S_rhs_finish',0),
]+prep('S_getter')+[
    r'$lookup(S_getter.ENV,$ptascii("weak")) = (n_weak_getter_cell)',
    r'S_getter.STORE[n_weak_getter_cell] = DEFINED (POBJECT n_weak_getter)',
    r'$weakref_get(S_getter,n_weak_getter) = POBJECT ppropertyhook_S_getter.OBJECT /\ $hac_slot(S_getter,ppropertyhook_S_getter.OBJECT,$ptascii("label")) = (PROP_VALUE (DIRECT (PINT 1))) /\ $hac_output(S_getter.EVENTS) = $ptascii("R0|D1:100|RN|G2|10:10|D2:10|R|")',
]+result('S_getter','S_getter','PINT 7')+[
    r'$lookup(S_getter_result.ENV,$ptascii("box")) = (n_box_getter_cell)',
    r'S_getter_result.STORE[n_box_getter_cell] = DEFINED (POBJECT n_getter_replacement)',
    r'n_getter_replacement =/= ppropertyhook_S_getter.OBJECT /\ $weakref_get(S_getter_result,n_weak_getter) = POBJECT ppropertyhook_S_getter.OBJECT /\ $heap_owners($heap_prune($heap_graph(S_getter_result)),HOBJECT ppropertyhook_S_getter.OBJECT) = 1 /\ $heap_owners($heap_prune($heap_graph(S_getter_result)),HOBJECT n_getter_replacement) = 1 /\ $hac_slot(S_getter_result,n_getter_replacement,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT 100))) /\ $hac_output(S_getter_result.EVENTS) = $ptascii("R0|D1:100|RN|G2|10:10|D2:10|R|G1|GL|")',
]+math('S_getter',10)+[
    r'$hac_slot(S_getter_math,n_getter_replacement,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT 100))) /\ $heap_owners($heap_prune($heap_graph(S_getter_math)),HOBJECT ppropertyhook_S_getter.OBJECT) = 1 /\ $heap_owners($heap_prune($heap_graph(S_getter_finish_raw)),HOBJECT ppropertyhook_S_getter.OBJECT) = 0 /\ $weakref_get(S_getter_finish,n_weak_getter) = POBJECT ppropertyhook_S_getter.OBJECT',
    r'S_getter_finish.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_getter) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_getter) :: (ORIGIN_RETURN (porigin_S_getter)) :: ptask_S_getter*',
    r'pdestructionoperation_getter.SOURCE = PROPERTY_HOOK_COMPOUND_FINISH ppropertyhook_S_getter pbase_S_getter 3 z_S_getter /\ pdestructionoperation_getter.VALUE = KNOWN (PINT 10) /\ pdestructionoperation_getter.PENDING = eps /\ pdestructionrelease_getter.JOBS = [DESTRUCTION_VALUE (HOBJECT ppropertyhook_S_getter.OBJECT)] /\ $hac_guard(S_getter_finish)',
    *reach('S_getter_disposed','S_getter_finish',3),
    r'S_getter_disposed.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_getter) :: (ORIGIN_RETURN (porigin_S_getter)) :: ptask_S_getter*',
    r'~((HOBJECT ppropertyhook_S_getter.OBJECT) <- S_getter_disposed.ALLOCATIONS) /\ $weakref_get(S_getter_disposed,n_weak_getter) = PNULL /\ $hac_slot(S_getter_disposed,n_getter_replacement,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT 100))) /\ $hac_output(S_getter_disposed.EVENTS) = $ptascii("R0|D1:100|RN|G2|10:10|D2:10|R|G1|GL|D1:10|") /\ $hac_guard(S_getter_disposed)',
    r'PhpStep: S_getter_disposed ~> S_getter_clean_raw',
    r'S_getter_clean_raw.RESULT = KNOWN (PINT 10) /\ S_getter_clean_raw.TODO = (ORIGIN_RETURN (porigin_S_getter)) :: ptask_S_getter* /\ S_getter_clean_raw.DESTRUCTION.OPERATIONS = eps',
    r'S_getter_clean = $hac_after(S_getter_disposed,S_getter_clean_raw)',
    r'S_done = $drive(S_getter_clean,10000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $weakref_get(S_done,n_weak_getter) = PNULL /\ $hac_guard(S_done) /\ $hac_output(S_done.EVENTS) = EXPECTED_OUTPUT',
]

LIFETIME = ['S_rv = S']+prep('S_rv')+[
    r'$lookup(S_rv.ENV,$ptascii("weak_box")) = (n_weak_box_cell)',
    r'S_rv.STORE[n_weak_box_cell] = DEFINED (POBJECT n_weak_box)',
    r'$weakref_get(S_rv,n_weak_box) = POBJECT ppropertyhook_S_rv.OBJECT /\ $heap_owners($heap_prune($heap_graph(S_rv)),HOBJECT ppropertyhook_S_rv.OBJECT) = 1 /\ z_S_rv = 32 /\ $hac_output(S_rv.EVENTS) = $ptascii("R|")',
    *reach('S_rv_result','S_rv',2),
    r'S_rv_result.TODO = (PROPERTY_HOOK_COMPOUND_RESULT ppropertyhook_S_rv pbase_S_rv 3 z_S_rv) :: (ORIGIN_RETURN (porigin_S_rv)) :: (COMPOUND_PREP ADD expression_target_S_rv expression_rhs_S_rv z_S_rv) :: ptask_S_rv*',
    r'S_rv_result.RESULT = KNOWN (POBJECT n_leaf)',
    r'$lookup(S_rv_result.ENV,$ptascii("weak_leaf")) = (n_weak_leaf_cell)',
    r'S_rv_result.STORE[n_weak_leaf_cell] = DEFINED (POBJECT n_weak_leaf)',
    r'$lookup(S_rv_result.ENV,$ptascii("box")) = (n_box_cell)',
    r'S_rv_result.STORE[n_box_cell] = DEFINED (POBJECT n_rv_replacement)',
    r'n_rv_replacement =/= ppropertyhook_S_rv.OBJECT /\ S_rv_result.CURRENT = eps /\ S_rv_result.FRAMES = eps /\ $property_hook_result_tail(S_rv_result,ppropertyhook_S_rv,S_rv_result.TODO) /\ $call_task_valid(S_rv_result,PROPERTY_HOOK_COMPOUND_RESULT ppropertyhook_S_rv pbase_S_rv 3 z_S_rv) /\ $task_nodes(PROPERTY_HOOK_COMPOUND_RESULT ppropertyhook_S_rv pbase_S_rv 3 z_S_rv) = [HOBJECT ppropertyhook_S_rv.OBJECT] /\ $heap_owners($heap_prune($heap_graph(S_rv_result)),HOBJECT n_leaf) = 1 /\ $heap_owners($heap_prune($heap_graph(S_rv_result)),HOBJECT ppropertyhook_S_rv.OBJECT) = 1 /\ $weakref_get(S_rv_result,n_weak_box) = POBJECT ppropertyhook_S_rv.OBJECT /\ $weakref_get(S_rv_result,n_weak_leaf) = POBJECT n_leaf /\ $hac_slot(S_rv_result,ppropertyhook_S_rv.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT 100))) /\ $hac_slot(S_rv_result,n_rv_replacement,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT 100))) /\ $hac_output(S_rv_result.EVENTS) = $ptascii("R|G|") /\ $hac_guard(S_rv_result)',
    r'PhpStep: S_rv_result ~> S_rv_math_raw',
    r'S_rv_math_raw.COMPLETION = THROWN "TypeError" ($ptascii("Unsupported operand types: HookCompoundLeaf35 + int")) 32 /\ S_rv_math_raw.RESULT = KNOWN PNULL /\ S_rv_math_raw.BASE = BASE_VALUE (KNOWN PNULL) /\ S_rv_math_raw.TODO = (PROPERTY_HOOK_COMPOUND_FINISH ppropertyhook_S_rv pbase_S_rv 3 z_S_rv) :: (ORIGIN_RETURN (porigin_S_rv)) :: (COMPOUND_PREP ADD expression_target_S_rv expression_rhs_S_rv z_S_rv) :: ptask_S_rv* /\ S_rv_math_raw.OBJECTPROPS = S_rv_result.OBJECTPROPS /\ S_rv_math_raw.EVENTS = S_rv_result.EVENTS /\ $heap_owners($heap_prune($heap_graph(S_rv_math_raw)),HOBJECT n_leaf) = 0 /\ $heap_owners($heap_prune($heap_graph(S_rv_math_raw)),HOBJECT ppropertyhook_S_rv.OBJECT) = 1',
    r'S_rv_throw = $throwable_transition(S_rv_result,S_rv_math_raw)',
    r'S_rv_throw.COMPLETION = THROWING n_error',
    r'S_rv_throw.TODO = S_rv_math_raw.TODO /\ S_rv_throw.RESULT = KNOWN PNULL /\ $call_task_valid(S_rv_throw,PROPERTY_HOOK_COMPOUND_FINISH ppropertyhook_S_rv pbase_S_rv 3 z_S_rv) /\ $heap_owners($heap_prune($heap_graph(S_rv_throw)),HOBJECT ppropertyhook_S_rv.OBJECT) = 1',
    r'S_rv_release = $hac_after(S_rv_result,S_rv_math_raw)',
    r'S_rv_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_leaf) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_leaf) :: (PROPERTY_HOOK_COMPOUND_FINISH ppropertyhook_S_rv pbase_S_rv 3 z_S_rv) :: (ORIGIN_RETURN (porigin_S_rv)) :: (COMPOUND_PREP ADD expression_target_S_rv expression_rhs_S_rv z_S_rv) :: ptask_S_rv*',
    r'pdestructionrelease_leaf.JOBS = [DESTRUCTION_VALUE (HOBJECT n_leaf)] /\ pdestructionoperation_leaf.SOURCE = PROPERTY_HOOK_COMPOUND_RESULT ppropertyhook_S_rv pbase_S_rv 3 z_S_rv /\ pdestructionoperation_leaf.PENDING = (n_error) /\ pdestructionoperation_leaf.VALUE = KNOWN PNULL /\ S_rv_release.COMPLETION = NORMAL /\ $heap_owners($heap_prune($heap_graph(S_rv_release)),HOBJECT n_leaf) = 1 /\ $heap_owners($heap_prune($heap_graph(S_rv_release)),HOBJECT ppropertyhook_S_rv.OBJECT) = 1 /\ $weakref_get(S_rv_release,n_weak_leaf) = POBJECT n_leaf /\ $hac_output(S_rv_release.EVENTS) = $ptascii("R|G|") /\ $hac_guard(S_rv_release)',
    *reach('S_leaf_disposed','S_rv_release',4),
    r'S_leaf_disposed.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_leaf) :: (PROPERTY_HOOK_COMPOUND_FINISH ppropertyhook_S_rv pbase_S_rv 3 z_S_rv) :: (ORIGIN_RETURN (porigin_S_rv)) :: (COMPOUND_PREP ADD expression_target_S_rv expression_rhs_S_rv z_S_rv) :: ptask_S_rv*',
    r'~((HOBJECT n_leaf) <- S_leaf_disposed.ALLOCATIONS) /\ (HOBJECT ppropertyhook_S_rv.OBJECT) <- S_leaf_disposed.ALLOCATIONS /\ $weakref_get(S_leaf_disposed,n_weak_leaf) = PNULL /\ $weakref_get(S_leaf_disposed,n_weak_box) = POBJECT ppropertyhook_S_rv.OBJECT /\ $heap_owners($heap_prune($heap_graph(S_leaf_disposed)),HOBJECT ppropertyhook_S_rv.OBJECT) = 1 /\ $hac_output(S_leaf_disposed.EVENTS) = $ptascii("R|G|D|BL|") /\ $hac_guard(S_leaf_disposed)',
    r'PhpStep: S_leaf_disposed ~> S_leaf_clean_raw',
    r'S_leaf_clean_raw.TODO = (THROW_SEARCH n_error) :: (PROPERTY_HOOK_COMPOUND_FINISH ppropertyhook_S_rv pbase_S_rv 3 z_S_rv) :: (ORIGIN_RETURN (porigin_S_rv)) :: (COMPOUND_PREP ADD expression_target_S_rv expression_rhs_S_rv z_S_rv) :: ptask_S_rv* /\ S_leaf_clean_raw.COMPLETION = NORMAL /\ S_leaf_clean_raw.DESTRUCTION.OPERATIONS = eps /\ S_leaf_clean_raw.RESULT = KNOWN PNULL',
    r'S_leaf_clean = $hac_after(S_leaf_disposed,S_leaf_clean_raw)',
    r'PhpStep: S_leaf_clean ~> S_receiver_discard_raw',
    r'S_receiver_discard_raw.TODO = (THROW_SEARCH n_error) :: (ORIGIN_RETURN (porigin_S_rv)) :: (COMPOUND_PREP ADD expression_target_S_rv expression_rhs_S_rv z_S_rv) :: ptask_S_rv* /\ S_receiver_discard_raw.EVENTS = S_leaf_disposed.EVENTS /\ $heap_owners($heap_prune($heap_graph(S_receiver_discard_raw)),HOBJECT ppropertyhook_S_rv.OBJECT) = 0',
    r'S_receiver_discard = $hac_after(S_leaf_clean,S_receiver_discard_raw)',
    *reach('S_catch','S_receiver_discard',5),
    r'S_catch.TODO = (CATCH_BIND porigin_catch n_index n_error) :: ptask_catch*',
    r'~((HOBJECT ppropertyhook_S_rv.OBJECT) <- S_catch.ALLOCATIONS) /\ $weakref_get(S_catch,n_weak_box) = PNULL /\ $weakref_get(S_catch,n_weak_leaf) = PNULL /\ $hac_slot(S_catch,n_rv_replacement,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT 100))) /\ $hac_output(S_catch.EVENTS) = $ptascii("R|G|D|BL|B1:100|") /\ $hac_guard(S_catch)',
    r'S_done = $drive(S_catch,10000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $weakref_get(S_done,n_weak_leaf) = PNULL /\ $weakref_get(S_done,n_weak_box) = PNULL /\ $hac_guard(S_done) /\ $hac_output(S_done.EVENTS) = EXPECTED_OUTPUT',
]

DERIVED = [
    r'$property_hook_compound_plan(S_null_cv[.RESULT = KNOWN (PSTRING ($ptascii("3")))]) = eps /\ $property_hook_compound_plan(S_null_cv[.ORIGIN = (ppropertyhook_S_null_cv.SITE)]) = eps /\ $property_hook_compound_plan(S_null_cv[.SOURCES = eps]) = eps /\ $property_hook_compound_plan(S_null_cv[.FUNCTIONS = eps]) = eps',
    r'$property_hook_compound_plan(S_null_cv[.TODO = (COMPOUND_APPLY SUBTRACT pbase_S_null_cv false z_S_null_cv) :: ptask_S_null_cv*]) = eps /\ $property_hook_compound_plan(S_null_cv[.TODO = (COMPOUND_APPLY ADD pbase_S_null_cv true z_S_null_cv) :: ptask_S_null_cv*]) = eps /\ $property_hook_compound_plan(S_null_cv[.TODO = (COMPOUND_APPLY ADD pbase_S_null_cv false $(z_S_null_cv + 1)) :: ptask_S_null_cv*]) = eps',
    r'~$property_hook_result_tail(S_null_cv_result,ppropertyhook_S_null_cv,[PROPERTY_HOOK_RESULT ppropertyhook_S_null_cv]) /\ ~$property_hook_result_tail(S_null_cv_result,ppropertyhook_S_null_cv,[PROPERTY_HOOK_ISSET_RESULT ppropertyhook_S_null_cv false])',
]
for label, tail in [
    ('missing', 'ptask_S_null_cv*'),
    ('marker', '(ORIGIN_RETURN (ppropertyhook_S_null_cv.SITE)) :: (COMPOUND_PREP ADD expression_target_S_null_cv expression_rhs_S_null_cv z_S_null_cv) :: ptask_S_null_cv*'),
    ('mode', '(ORIGIN_RETURN (porigin_S_null_cv)) :: (COMPOUND_PREP SUBTRACT expression_target_S_null_cv expression_rhs_S_null_cv z_S_null_cv) :: ptask_S_null_cv*'),
    ('rhs', '(ORIGIN_RETURN (porigin_S_null_cv)) :: (COMPOUND_PREP ADD expression_target_S_null_cv (NScalarInt (INTEGER 8) metadata_S_null_cv) z_S_null_cv) :: ptask_S_null_cv*'),
    ('line', '(ORIGIN_RETURN (porigin_S_null_cv)) :: (COMPOUND_PREP ADD expression_target_S_null_cv expression_rhs_S_null_cv $(z_S_null_cv + 1)) :: ptask_S_null_cv*')]:
    DERIVED += [f'S_bad_{label} = S_null_cv_result[.TODO = (PROPERTY_HOOK_COMPOUND_RESULT ppropertyhook_S_null_cv pbase_S_null_cv 3 z_S_null_cv) :: {tail}]',
                f'~$property_hook_result_tail(S_bad_{label},ppropertyhook_S_null_cv,S_bad_{label}.TODO) /\\ ~$call_task_valid(S_bad_{label},PROPERTY_HOOK_COMPOUND_RESULT ppropertyhook_S_null_cv pbase_S_null_cv 3 z_S_null_cv)']
DERIVED += [
    r'S_bad_base = S_null_cv_result[.TODO = (PROPERTY_HOOK_COMPOUND_RESULT ppropertyhook_S_null_cv (BASE_VALUE (KNOWN PNULL)) 3 z_S_null_cv) :: (ORIGIN_RETURN (porigin_S_null_cv)) :: (COMPOUND_PREP ADD expression_target_S_null_cv expression_rhs_S_null_cv z_S_null_cv) :: ptask_S_null_cv*]',
    r'~$property_hook_result_tail(S_bad_base,ppropertyhook_S_null_cv,S_bad_base.TODO) /\ ~$call_task_valid(S_bad_base,PROPERTY_HOOK_COMPOUND_RESULT ppropertyhook_S_null_cv (BASE_VALUE (KNOWN PNULL)) 3 z_S_null_cv)',
    r'S_bad_allocation = S_null_cv_result[.ALLOCATIONS = $destruction_node_delete(S_null_cv_result.ALLOCATIONS,HOBJECT ppropertyhook_S_null_cv.OBJECT)]',
    r'~$property_hook_result_tail(S_bad_allocation,ppropertyhook_S_null_cv,S_bad_allocation.TODO) /\ ~$call_task_valid(S_bad_allocation,PROPERTY_HOOK_COMPOUND_RESULT ppropertyhook_S_null_cv pbase_S_null_cv 3 z_S_null_cv)',
    r'S_bad_freeing = $instance_storage_begin(S_null_cv_result,ppropertyhook_S_null_cv.OBJECT)',
    r'~$property_hook_result_tail(S_bad_freeing,ppropertyhook_S_null_cv,S_bad_freeing.TODO) /\ ~$call_task_valid(S_bad_freeing,PROPERTY_HOOK_COMPOUND_RESULT ppropertyhook_S_null_cv pbase_S_null_cv 3 z_S_null_cv)',
    r'~$call_task_valid(S_null_cv_call,PROPERTY_HOOK_COMPOUND_RESULT ppropertyhook_S_null_cv pbase_S_null_cv 4 z_S_null_cv) /\ ~$call_task_valid(S_null_cv_call,PROPERTY_HOOK_COMPOUND_RESULT ppropertyhook_S_null_cv (BASE_VALUE (KNOWN PNULL)) 3 z_S_null_cv)',
    r'S_bad_finish_allocation = S_null_cv_math[.ALLOCATIONS = $destruction_node_delete(S_null_cv_math.ALLOCATIONS,HOBJECT ppropertyhook_S_null_cv.OBJECT)]',
    r'~$call_task_valid(S_bad_finish_allocation,PROPERTY_HOOK_COMPOUND_FINISH ppropertyhook_S_null_cv pbase_S_null_cv 3 z_S_null_cv)',
    r'S_bad_finish_freeing = $instance_storage_begin(S_null_cv_math,ppropertyhook_S_null_cv.OBJECT)',
    r'~$call_task_valid(S_bad_finish_freeing,PROPERTY_HOOK_COMPOUND_FINISH ppropertyhook_S_null_cv pbase_S_null_cv 3 z_S_null_cv)',
    r'~$property_hook_result_tail(S_null_cv_result[.FUNCTIONS = eps],ppropertyhook_S_null_cv,S_null_cv_result.TODO) /\ ~$property_hook_result_tail(S_null_cv_result[.SOURCES = eps],ppropertyhook_S_null_cv,S_null_cv_result.TODO)',
    r'~$property_hook_result_tail(S_null_cv_result,ppropertyhook_S_null_cv[.LINE = $(ppropertyhook_S_null_cv.LINE + 1)],S_null_cv_result.TODO) /\ ~$property_hook_result_tail(S_null_cv_result,ppropertyhook_S_null_cv[.PROPERTY = porigin_S_null_cv],S_null_cv_result.TODO)',
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'backed_get_hook_addassign_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    selections = [('scalar', SCALAR, DERIVED), ('rebind', REBIND, []), ('lifetime', LIFETIME, [])]
    sources = [HERE / ('backed-get-hook-addassign-' + row[0] + '.php') for row in selections]
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
    out = Path(tempfile.mkdtemp(prefix='backed-get-hook-addassign-protocol-', dir=ROOT / '.tools'))
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
                     'S_found = $hac_seek(S_initial,0,1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            content += '\ndec $hac_' + name + '() : bool\ndef $hac_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                condition = condition.replace('EXPECTED_OUTPUT', byte_expr(base64.b64decode(case['stdout_base64'])))
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $hac_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = ($hac_scalar() /\\ $hac_rebind() /\\ $hac_lifetime())\n'
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
