"""Reach get-hook coalesce assignment values, fallback stores and current-CV writes."""
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

PREFIX = r'''dec $cha_output(pevent*) : ptbytes
dec $cha_stage(pstate, nat) : bool
def $cha_stage(S, 0) = true
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $property_hook_assign_plan(S[.COMPLETION = NORMAL]) = (ppropertyhook)
  -- if $property_hook_assign_parent(S,ppropertyhook.SITE) =/= eps
def $cha_stage(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $property_hook_context_kind(pcallcontext)
def $cha_stage(S, 2) = true
  -- if S.TODO = (PROPERTY_HOOK_ASSIGN_RESULT ppropertyhook pbase) :: ptask*
def $cha_stage(S, 4) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES "Ym94") metadata)) :: ptask*
def $cha_stage(S, 5) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES "a2VwdA==") metadata)) :: ptask*
def $cha_stage(S, 6) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
def $cha_stage(S, 7) = true
  -- if S.TODO = (COALESCE_ASSIGN_WRITE pbase b z) :: ptask*
def $cha_stage(S,n) = false -- otherwise
dec $cha_seek(pstate,nat,nat) : pstate
def $cha_seek(S,n_stage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $cha_stage(S,n_stage) \/ n = 0
def $cha_seek(S,n_stage,n) = $cha_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$cha_stage(S,n_stage) /\ $(n > 0)
def $cha_seek(S,n_stage,n) = S -- otherwise
dec $cha_after(pstate,pstate) : pstate
def $cha_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $cha_guard(pstate) : bool
def $cha_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
def $cha_output(eps) = eps
def $cha_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $cha_output(pevent*)
dec $cha_slot(pstate,nat,ptbytes) : ppropstate?
def $cha_slot(S,n,ptbytes) = (ppropertyslot_value.STATE)
  -- if $objectprops_at(S.OBJECTPROPS,n) = (ppropertyslot*)
  -- if $property_slot_at(ppropertyslot*,ptbytes) = (ppropertyslot_value)
def $cha_slot(S,n,ptbytes) = eps -- otherwise
'''

def reach(name, previous, stage):
    return [f'{name}_found = $cha_seek({previous},{stage},1000)',
            fr'{name}_found.COMPLETION = NORMAL \/ {name}_found.COMPLETION = BUDGET',
            f'{name} = {name}_found[.COMPLETION = NORMAL]']


SCALAR = []
previous = 'S'
for label, mode, returned in [('false', 0, 'PBOOL false'), ('zero', 1, 'PINT 0'), ('null', 2, 'PNULL')]:
    for receiver in ['cv', 'this']:
        suffix = label + '_' + receiver
        state, hook, parent, base = ('S_' + suffix, 'ppropertyhook_' + suffix, 'porigin_' + suffix, 'pbase_' + suffix)
        target, rhs, line, tail = ('expression_target_' + suffix, 'expression_rhs_' + suffix, 'z_' + suffix, 'ptask_' + suffix + '*')
        prep_owners, call_owners = (1, 2) if receiver == 'cv' else (3, 4)
        SCALAR += [f'{state} = S'] if not SCALAR else reach(state, previous, 0)
        SCALAR += [
            f'$property_hook_assign_plan({state}) = ({hook})',
            f'{state}.TODO = (COALESCE_ASSIGN_PREP {target} {rhs} {line}) :: {tail}',
            f'{state}.ORIGIN = ({parent})',
            f'{base} = {state}.BASE',
            f'{base} = BASE_PROPERTY_PENDING pbase_receiver_{suffix} poperand_name_{suffix} z_receiver_{suffix}',
            f'{state}.RESULT = KNOWN PNULL /\\ $property_hook_assign_parent({state},{hook}.SITE) = ({parent}) /\\ $property_hook_assign_source({state},{hook},{base},{line}) /\\ $cha_slot({state},{hook}.OBJECT,$ptascii("mode")) = (PROP_VALUE (DIRECT (PINT {mode}))) /\\ $cha_slot({state},{hook}.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT PNULL)) /\\ $heap_owners($heap_prune($heap_graph({state})),HOBJECT {hook}.OBJECT) = {prep_owners} /\\ $cha_guard({state})',
        ]
        if receiver == 'cv':
            SCALAR += [f'$base_nodes({base}) = eps']
        else:
            SCALAR += [f'{state}.CURRENT = (pcallcontext_{suffix})',
                       f'$this_receiver({state}) = ({hook}.OBJECT) /\\ $base_nodes({base}) = [HOBJECT {hook}.OBJECT]']
        if label == 'false':
            SCALAR += [
                f'PhpStep: {state} ~> {state}_call_raw',
                f'{state}_call_raw.TODO = [(CALL_ARGS (PROPERTY_HOOK_TARGET {hook}) eps 0 eps ({hook}.SITE) {hook}.LINE), PROPERTY_HOOK_ASSIGN_RESULT {hook} {base}, ORIGIN_RETURN ({parent}), COALESCE_ASSIGN_PREP {target} {rhs} {line}] ++ {tail}',
                f'{state}_call_raw.ORIGIN = ({hook}.SITE) /\\ {state}_call_raw.RESULT = KNOWN PNULL /\\ {state}_call_raw.BASE = BASE_VALUE (KNOWN PNULL) /\\ {state}_call_raw.EVENTS = {state}.EVENTS /\\ {state}_call_raw.STORE = {state}.STORE /\\ {state}_call_raw.OBJECTPROPS = {state}.OBJECTPROPS',
                f'{state}_call = $cha_after({state},{state}_call_raw)',
                f'$property_hook_pending_call({state}_call,{hook}) /\\ $call_task_valid({state}_call,PROPERTY_HOOK_ASSIGN_RESULT {hook} {base}) /\\ $task_nodes(PROPERTY_HOOK_ASSIGN_RESULT {hook} {base}) = $base_nodes({base}) /\\ $heap_owners($heap_prune($heap_graph({state}_call)),HOBJECT {hook}.OBJECT) = {call_owners} /\\ $cha_guard({state}_call)',
                *reach(state + '_entered', state + '_call', 1),
                f'{state}_entered.CURRENT = (pcallcontext_hook_{suffix})',
                f'{state}_entered.FRAMES = pframe_{suffix} :: pframe_tail_{suffix}*',
                f'pframe_{suffix}.TODO = (PROPERTY_HOOK_ASSIGN_RESULT {hook} {base}) :: (ORIGIN_RETURN ({parent})) :: (COALESCE_ASSIGN_PREP {target} {rhs} {line}) :: {tail}',
                f'pcallcontext_hook_{suffix}.TARGET = PROPERTY_HOOK_TARGET {hook} /\\ pcallcontext_hook_{suffix}.RECEIVER = ({hook}.OBJECT) /\\ $property_hook_context_valid({state}_entered,pcallcontext_hook_{suffix}) /\\ $property_hook_frame({state}_entered,pcallcontext_hook_{suffix},pframe_{suffix},{hook}) /\\ $heap_owners($heap_prune($heap_graph({state}_entered)),HOBJECT {hook}.OBJECT) = {call_owners} /\\ $cha_guard({state}_entered)',
            ]
            prior = state + '_entered'
        else:
            prior = state
        SCALAR += [
            *reach(state + '_result', prior, 2),
            f'{state}_result.TODO = (PROPERTY_HOOK_ASSIGN_RESULT {hook} {base}) :: (ORIGIN_RETURN ({parent})) :: (COALESCE_ASSIGN_PREP {target} {rhs} {line}) :: {tail}',
            f'{state}_result.RESULT = KNOWN ({returned}) /\\ {state}_result.CURRENT = {"eps" if receiver == "cv" else "(pcallcontext_" + suffix + ")"} /\\ $property_hook_result_tail({state}_result,{hook},{state}_result.TODO) /\\ $call_task_valid({state}_result,PROPERTY_HOOK_ASSIGN_RESULT {hook} {base}) /\\ $heap_owners($heap_prune($heap_graph({state}_result)),HOBJECT {hook}.OBJECT) = {prep_owners} /\\ $cha_slot({state}_result,{hook}.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT PNULL)) /\\ $cha_guard({state}_result)',
            f'PhpStep: {state}_result ~> {state}_selected_raw',
        ]
        if label != 'null':
            SCALAR += [
                f'{state}_selected_raw.TODO = (ORIGIN_RETURN ({parent})) :: {tail} /\\ {state}_selected_raw.RESULT = KNOWN ({returned}) /\\ {state}_selected_raw.BASE = BASE_VALUE (KNOWN PNULL) /\\ {state}_selected_raw.EVENTS = {state}_result.EVENTS /\\ $cha_slot({state}_selected_raw,{hook}.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT PNULL)) /\\ $heap_owners($heap_prune($heap_graph({state}_selected_raw)),HOBJECT {hook}.OBJECT) = {1 if receiver == "cv" else 2}',
                f'{state}_selected = $cha_after({state}_result,{state}_selected_raw)',
            ]
            selected = state + '_selected'
            if receiver == 'this' and label == 'false':
                SCALAR += [
                    f'~$destructor_operational({selected}) /\\ {selected}.RESULT = KNOWN ({returned}) /\\ {selected}.TODO = (ORIGIN_RETURN ({parent})) :: {tail} /\\ {selected}.DESTRUCTION.OPERATIONS = eps /\\ $heap_owners($heap_prune($heap_graph({selected})),HOBJECT {hook}.OBJECT) = 2 /\\ {selected}.EVENTS = {state}_result.EVENTS /\\ $cha_guard({selected})',
                ]
            if receiver == 'cv' or label == 'false':
                SCALAR += [
                    f'PhpStep: {selected} ~> {state}_parent_raw',
                    f'{state}_parent_raw.ORIGIN = ({parent}) /\\ {state}_parent_raw.TODO = {tail} /\\ {state}_parent_raw.RESULT = KNOWN ({returned}) /\\ {state}_parent_raw.EVENTS = {state}_result.EVENTS',
                    f'{state}_parent = $cha_after({selected},{state}_parent_raw)',
                    f'$cha_guard({state}_parent)',
                ]
                previous = state + '_parent'
            else:
                previous = selected
        else:
            SCALAR += [
                f'{state}_selected_raw.TODO = [(ORIGIN_RETURN ({parent})), $at_task($origin_child(({parent}),[PCFIELD 1]),EVAL {rhs}), COALESCE_ASSIGN_WRITE {base} $assignment_self({target},{rhs}) {line}] ++ {tail}',
                f'{state}_selected_raw.RESULT = KNOWN PNULL /\\ {state}_selected_raw.BASE = BASE_VALUE (KNOWN PNULL) /\\ {state}_selected_raw.EVENTS = {state}_result.EVENTS /\\ $heap_owners($heap_prune($heap_graph({state}_selected_raw)),HOBJECT {hook}.OBJECT) = {prep_owners}',
                f'{state}_selected = $cha_after({state}_result,{state}_selected_raw)',
                f'PhpStep: {state}_selected ~> {state}_parent_raw',
                f'{state}_parent_raw.ORIGIN = ({parent}) /\\ {state}_parent_raw.TODO = [$at_task($origin_child(({parent}),[PCFIELD 1]),EVAL {rhs}), COALESCE_ASSIGN_WRITE {base} $assignment_self({target},{rhs}) {line}] ++ {tail} /\\ {state}_parent_raw.EVENTS = {state}_result.EVENTS',
                f'{state}_parent = $cha_after({state}_selected,{state}_parent_raw)',
                *reach(state + '_write', state + '_parent', 7),
                f'{state}_write.TODO = (COALESCE_ASSIGN_WRITE {base} $assignment_self({target},{rhs}) {line}) :: {tail} /\\ {state}_write.ORIGIN = ({parent}) /\\ {state}_write.RESULT = KNOWN (PINT 13) /\\ $cha_slot({state}_write,{hook}.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT PNULL)) /\\ $heap_owners($heap_prune($heap_graph({state}_write)),HOBJECT {hook}.OBJECT) = {prep_owners} /\\ $cha_guard({state}_write)',
                f'PhpStep: {state}_write ~> {state}_written_raw',
                f'{state}_written_raw.TODO = {tail} /\\ {state}_written_raw.RESULT = KNOWN (PINT 13) /\\ $cha_slot({state}_written_raw,{hook}.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT 13))) /\\ {state}_written_raw.EVENTS = {state}_write.EVENTS',
                f'{state}_written = $cha_after({state}_write,{state}_written_raw)',
                f'$cha_guard({state}_written)',
            ]
            previous = state + '_written'
SCALAR += [f'S_done = $drive({previous},10000)',
           r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $cha_guard(S_done) /\ $cha_output(S_done.EVENTS) = EXPECTED_OUTPUT']


LIFETIME = [
    r'$property_hook_assign_plan(S) = (ppropertyhook)',
    r'S.TODO = (COALESCE_ASSIGN_PREP expression_target expression_rhs z) :: ptask_tail*',
    r'S.ORIGIN = (porigin_parent)',
    r'pbase = S.BASE',
    r'$cha_slot(S,ppropertyhook.OBJECT,$ptascii("value")) = eps /\ $base_nodes(pbase) = eps /\ $heap_owners($heap_prune($heap_graph(S)),HOBJECT ppropertyhook.OBJECT) = 1 /\ $cha_guard(S)',
    r'PhpStep: S ~> S_call_raw',
    r'S_call = $cha_after(S,S_call_raw)',
    r'$property_hook_pending_call(S_call,ppropertyhook) /\ $call_task_valid(S_call,PROPERTY_HOOK_ASSIGN_RESULT ppropertyhook pbase) /\ $heap_owners($heap_prune($heap_graph(S_call)),HOBJECT ppropertyhook.OBJECT) = 2 /\ $cha_guard(S_call)',
    *reach('S_result','S_call',2),
    r'S_result.TODO = (PROPERTY_HOOK_ASSIGN_RESULT ppropertyhook pbase) :: (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_ASSIGN_PREP expression_target expression_rhs z) :: ptask_tail*',
    r'S_result.RESULT = KNOWN (POBJECT n_leaf)',
    r'$lookup(S_result.ENV,$ptascii("weak")) = (n_weak_cell)',
    r'S_result.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
    r'$weakref_get(S_result,n_weak) = POBJECT n_leaf /\ S_result.CURRENT = eps /\ S_result.FRAMES = eps /\ $task_nodes(PROPERTY_HOOK_ASSIGN_RESULT ppropertyhook pbase) = eps /\ $heap_owners($heap_prune($heap_graph(S_result)),HOBJECT n_leaf) = 1 /\ $heap_owners($heap_prune($heap_graph(S_result)),HOBJECT ppropertyhook.OBJECT) = 1 /\ $cha_output(S_result.EVENTS) = $ptascii("G|") /\ $cha_guard(S_result)',
    r'PhpStep: S_result ~> S_selected_raw',
    r'S_selected_raw.TODO = (ORIGIN_RETURN (porigin_parent)) :: ptask_tail* /\ S_selected_raw.RESULT = KNOWN (POBJECT n_leaf) /\ S_selected_raw.BASE = BASE_VALUE (KNOWN PNULL) /\ S_selected_raw.EVENTS = S_result.EVENTS /\ $heap_owners($heap_prune($heap_graph(S_selected_raw)),HOBJECT n_leaf) = 1',
    r'S_selected = $cha_after(S_result,S_selected_raw)',
    r'S_selected.DESTRUCTION.OPERATIONS = eps /\ $weakref_get(S_selected,n_weak) = POBJECT n_leaf /\ $heap_owners($heap_prune($heap_graph(S_selected)),HOBJECT n_leaf) = 1 /\ $cha_guard(S_selected)',
    r'PhpStep: S_selected ~> S_parent_raw',
    r'S_parent_raw.ORIGIN = (porigin_parent) /\ S_parent_raw.TODO = ptask_tail* /\ S_parent_raw.RESULT = KNOWN (POBJECT n_leaf) /\ S_parent_raw.EVENTS = S_result.EVENTS',
    r'S_parent = $cha_after(S_selected,S_parent_raw)',
    r'$heap_owners($heap_prune($heap_graph(S_parent)),HOBJECT n_leaf) = 1 /\ S_parent.DESTRUCTION.OPERATIONS = eps /\ $cha_guard(S_parent)',
    *reach('S_box_unset','S_parent',4),
    r'$lookup(S_box_unset.ENV,$ptascii("kept")) = (n_kept_cell)',
    r'S_box_unset.STORE[n_kept_cell] = DEFINED (POBJECT n_leaf)',
    r'$heap_owners($heap_prune($heap_graph(S_box_unset)),HOBJECT n_leaf) = 1 /\ $weakref_get(S_box_unset,n_weak) = POBJECT n_leaf /\ $cha_output(S_box_unset.EVENTS) = $ptascii("G|HELD|") /\ $cha_guard(S_box_unset)',
    *reach('S_box_disposed','S_box_unset',6),
    r'S_box_disposed.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_box) :: ptask_box*',
    r'pdestructionoperation_box.SOURCE = UNSET (NExprVariable (BYTES "Ym94") metadata_box)',
    r'~((HOBJECT ppropertyhook.OBJECT) <- S_box_disposed.ALLOCATIONS) /\ (HOBJECT n_leaf) <- S_box_disposed.ALLOCATIONS /\ $weakref_get(S_box_disposed,n_weak) = POBJECT n_leaf /\ $heap_owners($heap_prune($heap_graph(S_box_disposed)),HOBJECT n_leaf) = 1 /\ $cha_output(S_box_disposed.EVENTS) = $ptascii("G|HELD|B|") /\ $cha_guard(S_box_disposed)',
    *reach('S_kept_unset','S_box_disposed',5),
    r'S_kept_unset.STORE[n_kept_cell] = DEFINED (POBJECT n_leaf) /\ $heap_owners($heap_prune($heap_graph(S_kept_unset)),HOBJECT n_leaf) = 1 /\ $weakref_get(S_kept_unset,n_weak) = POBJECT n_leaf /\ $cha_output(S_kept_unset.EVENTS) = $ptascii("G|HELD|B|LIVE|") /\ $cha_guard(S_kept_unset)',
    r'PhpStep: S_kept_unset ~> S_unset_raw',
    r'$lookup(S_unset_raw.ENV,$ptascii("kept")) = eps /\ $heap_owners($heap_prune($heap_graph(S_unset_raw)),HOBJECT n_leaf) = 0 /\ S_unset_raw.EVENTS = S_kept_unset.EVENTS',
    r'S_release = $cha_after(S_kept_unset,S_unset_raw)',
    *reach('S_disposed','S_release',6),
    r'$weakref_get(S_disposed,n_weak) = PNULL /\ ~((HOBJECT n_leaf) <- S_disposed.ALLOCATIONS) /\ $cha_output(S_disposed.EVENTS) = $ptascii("G|HELD|B|LIVE|D|") /\ $cha_guard(S_disposed)',
    r'S_done = $drive(S_disposed,10000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $weakref_get(S_done,n_weak) = PNULL /\ $cha_guard(S_done) /\ $cha_output(S_done.EVENTS) = EXPECTED_OUTPUT',
]


REBIND = [
    r'$property_hook_assign_plan(S) = (ppropertyhook)',
    r'S.TODO = (COALESCE_ASSIGN_PREP expression_target expression_rhs z) :: ptask_tail*',
    r'S.ORIGIN = (porigin_parent)',
    r'pbase = S.BASE',
    r'$base_nodes(pbase) = eps /\ $heap_owners($heap_prune($heap_graph(S)),HOBJECT ppropertyhook.OBJECT) = 1 /\ $cha_guard(S)',
    r'$lookup(S.ENV,$ptascii("weak")) = (n_weak_cell)',
    r'S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
    *reach('S_result','S',2),
    r'S_result.TODO = (PROPERTY_HOOK_ASSIGN_RESULT ppropertyhook pbase) :: (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_ASSIGN_PREP expression_target expression_rhs z) :: ptask_tail*',
    r'S_result.RESULT = KNOWN PNULL /\ $task_nodes(PROPERTY_HOOK_ASSIGN_RESULT ppropertyhook pbase) = eps /\ $weakref_get(S_result,n_weak) = POBJECT ppropertyhook.OBJECT /\ $heap_owners($heap_prune($heap_graph(S_result)),HOBJECT ppropertyhook.OBJECT) = 1 /\ $cha_output(S_result.EVENTS) = $ptascii("G|") /\ $cha_guard(S_result)',
    r'PhpStep: S_result ~> S_rhs_raw',
    r'S_rhs_raw.TODO = [ORIGIN_RETURN (porigin_parent), $at_task($origin_child((porigin_parent),[PCFIELD 1]),EVAL expression_rhs), COALESCE_ASSIGN_WRITE pbase $assignment_self(expression_target,expression_rhs) z] ++ ptask_tail* /\ S_rhs_raw.RESULT = KNOWN PNULL /\ S_rhs_raw.EVENTS = S_result.EVENTS',
    r'S_rhs = $cha_after(S_result,S_rhs_raw)',
    *reach('S_write','S_rhs',7),
    r'S_write.TODO = (COALESCE_ASSIGN_WRITE pbase $assignment_self(expression_target,expression_rhs) z) :: ptask_tail*',
    r'$lookup(S_write.ENV,$ptascii("box")) = (n_box_cell)',
    r'S_write.STORE[n_box_cell] = DEFINED (POBJECT n_replacement)',
    r'n_replacement =/= ppropertyhook.OBJECT /\ S_write.ORIGIN = (porigin_parent) /\ S_write.RESULT = KNOWN (PINT 23) /\ ~((HOBJECT ppropertyhook.OBJECT) <- S_write.ALLOCATIONS) /\ (HOBJECT n_replacement) <- S_write.ALLOCATIONS /\ $weakref_get(S_write,n_weak) = PNULL /\ $cha_slot(S_write,n_replacement,$ptascii("value")) = (PROP_VALUE (DIRECT PNULL)) /\ $heap_owners($heap_prune($heap_graph(S_write)),HOBJECT n_replacement) = 1 /\ $cha_output(S_write.EVENTS) = $ptascii("G|R0|H|RN|") /\ $cha_guard(S_write)',
    r'PhpStep: S_write ~> S_written_raw',
    r'S_written_raw.TODO = ptask_tail* /\ S_written_raw.RESULT = KNOWN (PINT 23) /\ $cha_slot(S_written_raw,n_replacement,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT 23))) /\ $weakref_get(S_written_raw,n_weak) = PNULL /\ ~((HOBJECT ppropertyhook.OBJECT) <- S_written_raw.ALLOCATIONS) /\ S_written_raw.EVENTS = S_write.EVENTS',
    r'S_written = $cha_after(S_write,S_written_raw)',
    r'$cha_guard(S_written)',
    r'S_done = $drive(S_written,10000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $cha_guard(S_done) /\ $cha_output(S_done.EVENTS) = EXPECTED_OUTPUT',
]


DERIVED = [
    r'$property_hook_function(S_false_cv,ppropertyhook_false_cv) = (pfunction_hook)',
    r'$property_hook_assign_plan(S_false_cv[.ORIGIN = (ppropertyhook_false_cv.SITE)]) = eps /\ $property_hook_assign_plan(S_false_cv[.SOURCES = eps]) = eps',
    r'$property_hook_assign_plan(S_false_cv[.TODO = (COALESCE_ASSIGN_PREP expression_target_false_cv expression_rhs_false_cv 999) :: ptask_false_cv*]) = eps',
    r'$property_hook_assign_plan(S_false_cv[.BASE = BASE_PROPERTY_PENDING pbase_receiver_false_cv poperand_name_false_cv 999]) = eps',
    r'$property_hook_assign_plan(S_false_cv[.BASE = BASE_PROPERTY_PENDING pbase_receiver_false_cv (KNOWN (PSTRING $ptascii("wrong"))) z_receiver_false_cv]) = eps',
    r'$property_hook_assign_plan(S_false_cv[.BASE = BASE_PROPERTY_PENDING (BASE_VALUE (KNOWN (POBJECT ppropertyhook_false_cv.OBJECT))) poperand_name_false_cv z_receiver_false_cv]) = eps',
    r'$property_hook_assign_plan(S_false_cv[.FUNCTIONS = [pfunction_hook[.NAME = $ptascii("wrong")]]]) = eps /\ $property_hook_assign_plan(S_false_cv[.FUNCTIONS = [pfunction_hook[.SIGNATURE.BYREF = true]]]) = eps',
    r'~$property_hook_valid(S_false_cv,ppropertyhook_false_cv[.PROPERTY = ppropertyhook_false_cv.HOOK],true) /\ ~$property_hook_valid(S_false_cv,ppropertyhook_false_cv[.HOOK = ppropertyhook_false_cv.PROPERTY],true) /\ ~$property_hook_valid(S_false_cv,ppropertyhook_false_cv[.LINE = 999],true)',
    r'~$call_task_valid(S_false_cv_call,PROPERTY_HOOK_ASSIGN_RESULT ppropertyhook_false_cv (BASE_VALUE (KNOWN PNULL))) /\ ~$call_task_valid(S_false_cv_result,PROPERTY_HOOK_ASSIGN_RESULT ppropertyhook_false_cv (BASE_VALUE (KNOWN PNULL)))',
    r'~$call_task_valid(S_false_cv_result,PROPERTY_HOOK_RESULT ppropertyhook_false_cv) /\ ~$call_task_valid(S_false_cv_result,PROPERTY_HOOK_ISSET_RESULT ppropertyhook_false_cv false)',
    r'$origin_node(S_false_cv.SOURCES,porigin_false_cv) = (NExprAssignOpCoalesce expression_target_false_cv expression_rhs_false_cv metadata_parent)',
    r'porigin_false_cv = PORIGIN n_source pcpath_parent',
    r'$code_at(S_false_cv.CODE,n_source) = (pcode)',
    r'pcode_missing = pcode[.EXPRESSIONS = eps]',
    r'pcode_duplicate = pcode[.EXPRESSIONS = [CODEWRITE (pcpath_parent ++ [PCFIELD 0]) z_false_cv, CODEWRITE (pcpath_parent ++ [PCFIELD 0]) z_false_cv]]',
    r'$property_hook_assign_plan(S_false_cv[.CODE = [pcode_missing]]) = eps /\ $property_hook_assign_plan(S_false_cv[.CODE = [pcode_duplicate]]) = eps',
    r'S_false_cv.SOURCES = pcunit :: pcunit_tail*',
    r'pcunit.ID = n_source',
    r'pcunit_wrong = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_parent (NExprBinaryOpCoalesce expression_target_false_cv expression_rhs_false_cv metadata_parent)) :: pcunit.OCCURRENCES]',
    r'S_wrong_parent = S_false_cv[.SOURCES = pcunit_wrong :: pcunit_tail*]',
    r'$property_hook_assign_plan(S_wrong_parent) = eps /\ ~$property_hook_result_tail(S_false_cv_result[.SOURCES = S_wrong_parent.SOURCES],ppropertyhook_false_cv,S_false_cv_result.TODO)',
    r'pcunit_rhs = pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_parent (NExprAssignOpCoalesce expression_target_false_cv (NScalarInt (INTEGER 7) metadata_parent) metadata_parent)) :: pcunit.OCCURRENCES]',
    r'S_wrong_rhs = S_false_cv_result[.SOURCES = pcunit_rhs :: pcunit_tail*]',
    r'$property_hook_valid(S_wrong_rhs,ppropertyhook_false_cv,false) /\ ~$property_hook_result_tail(S_wrong_rhs,ppropertyhook_false_cv,S_wrong_rhs.TODO) /\ ~$call_task_valid(S_wrong_rhs,PROPERTY_HOOK_ASSIGN_RESULT ppropertyhook_false_cv pbase_false_cv)',
    r'~$property_hook_assign_task_head([(CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook_false_cv) eps 0 eps (ppropertyhook_false_cv.SITE) 999), PROPERTY_HOOK_ASSIGN_RESULT ppropertyhook_false_cv pbase_false_cv],ppropertyhook_false_cv,pbase_false_cv)',
    r'~$property_hook_assign_task_head([(CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook_false_cv) eps 0 eps (porigin_false_cv) ppropertyhook_false_cv.LINE), PROPERTY_HOOK_ASSIGN_RESULT ppropertyhook_false_cv pbase_false_cv],ppropertyhook_false_cv,pbase_false_cv)',
]
for bad_tail in [
    r'(COALESCE_ASSIGN_PREP expression_target_false_cv expression_rhs_false_cv z_false_cv) :: ptask_false_cv*',
    r'(ORIGIN_RETURN (ppropertyhook_false_cv.SITE)) :: (COALESCE_ASSIGN_PREP expression_target_false_cv expression_rhs_false_cv z_false_cv) :: ptask_false_cv*',
    r'(ORIGIN_RETURN (porigin_false_cv)) :: ptask_false_cv*',
    r'(ORIGIN_RETURN (porigin_false_cv)) :: (COALESCE_ASSIGN_PREP expression_target_false_cv (NScalarInt (INTEGER 7) metadata_parent) z_false_cv) :: ptask_false_cv*',
    r'(ORIGIN_RETURN (porigin_false_cv)) :: (COALESCE_ASSIGN_PREP (NScalarInt (INTEGER 7) metadata_parent) expression_rhs_false_cv z_false_cv) :: ptask_false_cv*',
    r'(ORIGIN_RETURN (porigin_false_cv)) :: (COALESCE_ASSIGN_PREP expression_target_false_cv expression_rhs_false_cv 999) :: ptask_false_cv*',
]:
    i = len(DERIVED)
    name = 'ptask_bad_' + str(i) + '*'
    DERIVED += [
        f'{name} = {bad_tail}',
        f'~$property_hook_pending_call(S_false_cv_call[.TODO = (CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook_false_cv) eps 0 eps (ppropertyhook_false_cv.SITE) ppropertyhook_false_cv.LINE) :: (PROPERTY_HOOK_ASSIGN_RESULT ppropertyhook_false_cv pbase_false_cv) :: {name}],ppropertyhook_false_cv) /\\ ~$property_hook_frame(S_false_cv_entered,pcallcontext_hook_false_cv,pframe_false_cv[.TODO = (PROPERTY_HOOK_ASSIGN_RESULT ppropertyhook_false_cv pbase_false_cv) :: {name}],ppropertyhook_false_cv)',
        f'~$property_hook_result_tail(S_false_cv_result,ppropertyhook_false_cv,(PROPERTY_HOOK_ASSIGN_RESULT ppropertyhook_false_cv pbase_false_cv) :: {name}) /\\ ~$call_task_valid(S_false_cv_result[.TODO = (PROPERTY_HOOK_ASSIGN_RESULT ppropertyhook_false_cv pbase_false_cv) :: {name}],PROPERTY_HOOK_ASSIGN_RESULT ppropertyhook_false_cv pbase_false_cv)',
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'coalesce_assignment_get_hook_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    selections = [('scalar', SCALAR, DERIVED), ('lifetime', LIFETIME, []), ('rebind', REBIND, [])]
    sources = [HERE / ('coalesce-assignment-get-hook-' + row[0] + '.php') for row in selections]
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
    out = Path(tempfile.mkdtemp(prefix='coalesce-assignment-get-hook-protocol-', dir=ROOT / '.tools'))
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
                     'S_found = $cha_seek(S_initial,0,1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            content += '\ndec $cha_' + name + '() : bool\ndef $cha_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                condition = condition.replace('EXPECTED_OUTPUT', byte_expr(base64.b64decode(case['stdout_base64'])))
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $cha_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = ($cha_scalar() /\\ $cha_lifetime() /\\ $cha_rebind())\n'
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
