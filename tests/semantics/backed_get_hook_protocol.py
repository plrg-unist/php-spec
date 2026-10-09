"""Check backed get-hook entry, backing access, throw and receiver lifetime."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()
byte_expr = lambda value: '[' + ','.join(str(byte) for byte in value) + ']'

PREFIX = r'''dec $bh_output(pevent*) : ptbytes
dec $bh_stage(pstate, nat) : bool
def $bh_stage(S, 0) = ($property_hook_plan(S) =/= eps)
def $bh_stage(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $property_hook_context_kind(pcallcontext)
def $bh_stage(S, 2) = true
  -- if S.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*
def $bh_stage(S, 3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $property_hook_context_kind(pcallcontext)
  -- if S.TODO = (PROPERTY_PREP (NIdentifier (BYTES "dmFsdWU=") metadata) z) :: (DIM_FETCH z) :: ptask*
  -- if ~$property_hook_pending(S)
def $bh_stage(S, 4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $property_hook_context_kind(pcallcontext)
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask*
def $bh_stage(S, 5) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $property_hook_context_kind(pcallcontext)
  -- if S.TODO = (STMT (NStmtReturn expression metadata)) :: ptask*
  -- if S.GLOBALTABLE = (psymboltable)
  -- if $lookup(psymboltable.ENV, $ptascii("box")) = eps
  -- if $bh_output(S.EVENTS) = $ptascii("G|")
def $bh_stage(S, 6) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES "Y29weQ==") metadata)) :: ptask*
def $bh_stage(S, 7) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $ptlc(pcallcontext.NAME) = $ptascii("hook_read28")
def $bh_stage(S, 8) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $property_hook_context_kind(pcallcontext)
  -- if S.TODO = [RETURN_UNWIND (KNOWN (POBJECT n)) porigin?]
def $bh_stage(S, n) = false -- otherwise
dec $bh_seek(pstate, nat, nat) : pstate
def $bh_seek(S, n_stage, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $bh_stage(S, n_stage) \/ n = 0
def $bh_seek(S, n_stage, n) = $bh_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$bh_stage(S, n_stage) /\ $(n > 0)
def $bh_seek(S, n_stage, n) = $bh_seek($drive_steps(S, 1), n_stage, $nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $bh_seek(S, n_stage, n) = S -- otherwise
dec $bh_after(pstate, pstate) : pstate
def $bh_after(S, S_next) = $gc_transition_owners(S, $destruction_transition_owners(S, $sensitive_trace_freeze($source_exception_transition(S, $throwable_transition(S, S_next)))))
dec $bh_guard(pstate) : bool
def $bh_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
def $bh_output(eps) = eps
def $bh_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $bh_output(pevent*)
dec $bh_slot(pstate, nat, ptbytes) : ppropstate?
def $bh_slot(S, n, ptbytes) = (ppropertyslot_value.STATE)
  -- if $objectprops_at(S.OBJECTPROPS, n) = (ppropertyslot*)
  -- if $property_slot_at(ppropertyslot*, ptbytes) = (ppropertyslot_value)
def $bh_slot(S, n, ptbytes) = eps -- otherwise
'''


BASIC = [
    r'$property_hook_plan(S) = (ppropertyhook)',
    r'S.TODO = (PROPERTY_PREP phpType20 z) :: (DIM_FETCH z) :: ptask_tail*',
    r'$property_effective_desc(S,ppropertyhook.OBJECT,$ptascii("value")) = (ppropertydesc)',
    r'$property_hook_origin(S,ppropertydesc) = (ppropertyhook.HOOK)',
    r'$property_hook_function(S,ppropertyhook) = (pfunction_hook)',
    r'S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin_class',
    r'$effective_method(S,porigin_class,$hook_name(ppropertydesc.NAME),|S.CLASSES|) = eps /\ $callable_at(S.CALLABLES,$ptlc(pfunction_hook.NAME)) = eps',
    r'pfunction_hook.SIGNATURE.PARAMETERS = eps /\ pfunction_hook.SIGNATURE.RETURNS = ppropertydesc.TYPE /\ ~pfunction_hook.EARLY',
    r'$bh_slot(S,ppropertyhook.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT 7))) /\ $bh_guard(S)',
    r'$heap_owners($heap_prune($heap_graph(S)),HOBJECT ppropertyhook.OBJECT) = 1',
    r'PhpStep: S ~> S_call_raw',
    r'S_call_raw.TODO = [(CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook) eps 0 eps (ppropertyhook.SITE) ppropertyhook.LINE), PROPERTY_HOOK_RESULT ppropertyhook] ++ ptask_tail*',
    r'S_call_raw.RESULT = KNOWN PNULL /\ S_call_raw.BASE = BASE_VALUE (KNOWN PNULL) /\ S_call_raw.COMPLETION = NORMAL',
    r'S_call_raw.OBJECTS = S.OBJECTS /\ S_call_raw.OBJECTPROPS = S.OBJECTPROPS /\ S_call_raw.STORE = S.STORE /\ S_call_raw.EVENTS = S.EVENTS',
    r'$target_nodes(PROPERTY_HOOK_TARGET ppropertyhook) = [HOBJECT ppropertyhook.OBJECT] /\ $task_nodes(PROPERTY_HOOK_RESULT ppropertyhook) = eps',
    r'S_call = $bh_after(S,S_call_raw)',
    r'$property_hook_pending_call(S_call,ppropertyhook) /\ $call_selected_valid(S_call,PROPERTY_HOOK_TARGET ppropertyhook,(ppropertyhook.SITE)) /\ $bh_guard(S_call)',
    r'$heap_owners($heap_prune($heap_graph(S_call)),HOBJECT ppropertyhook.OBJECT) = 2',
    r'S_entered_found = $bh_seek(S_call,1,1000)',
    r'S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET',
    r'S_entered = S_entered_found[.COMPLETION = NORMAL]',
    r'S_entered.CURRENT = (pcallcontext_hook)',
    r'pcallcontext_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook /\ pcallcontext_hook.RECEIVER = (ppropertyhook.OBJECT) /\ pcallcontext_hook.INSTANCE = eps',
    r'S_entered.FRAMES = pframe_caller :: pframe_tail*',
    r'pframe_caller.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask_tail*',
    r'$property_hook_context_valid(S_entered,pcallcontext_hook) /\ $call_receiver_roots(pcallcontext_hook) = [HOBJECT ppropertyhook.OBJECT] /\ $bh_guard(S_entered)',
    r'$heap_owners($heap_prune($heap_graph(S_entered)),HOBJECT ppropertyhook.OBJECT) = 2',
    r'S_backing_found = $bh_seek(S_entered,3,1000)',
    r'S_backing_found.COMPLETION = NORMAL \/ S_backing_found.COMPLETION = BUDGET',
    r'S_backing = S_backing_found[.COMPLETION = NORMAL]',
    r'S_backing.TODO = (PROPERTY_PREP phpType20_backing z_backing) :: (DIM_FETCH z_backing) :: ptask_backing*',
    r'$property_hook_backing(S_backing,ppropertyhook.OBJECT,ppropertydesc) /\ ~$property_hook_read_needed(S_backing,ppropertyhook.OBJECT,$ptascii("value")) /\ ~$property_hook_pending(S_backing)',
    r'$bh_output(S_backing.EVENTS) = $ptascii("G|") /\ $bh_guard(S_backing)',
    r'PhpStep: S_backing ~> S_base_raw',
    r'S_base_raw.BASE = BASE_PROPERTY (POBJECT ppropertyhook.OBJECT) ($ptascii("value")) /\ S_base_raw.TODO = (DIM_FETCH z_backing) :: ptask_backing*',
    r'S_base_raw.EVENTS = S_backing.EVENTS /\ S_base_raw.OBJECTPROPS = S_backing.OBJECTPROPS',
    r'S_base = $bh_after(S_backing,S_base_raw)',
    r'PhpStep: S_base ~> S_value_raw',
    r'S_value_raw.COMPLETION = NORMAL /\ S_value_raw.RESULT = KNOWN (PINT 7) /\ S_value_raw.TODO = ptask_backing*',
    r'S_value_raw.EVENTS = S_backing.EVENTS /\ S_value_raw.OBJECTPROPS = S_backing.OBJECTPROPS',
    r'S_value = $bh_after(S_base,S_value_raw)',
    r'S_result_found = $bh_seek(S_value,2,1000)',
    r'S_result_found.COMPLETION = NORMAL \/ S_result_found.COMPLETION = BUDGET',
    r'S_result = S_result_found[.COMPLETION = NORMAL]',
    r'S_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask_tail* /\ S_result.CURRENT = eps /\ S_result.RESULT = KNOWN (PINT 8)',
    r'$bh_slot(S_result,ppropertyhook.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT 7))) /\ $bh_guard(S_result)',
    r'$heap_owners($heap_prune($heap_graph(S_result)),HOBJECT ppropertyhook.OBJECT) = 1',
    r'PhpStep: S_result ~> S_result_raw',
    r'S_result_raw.TODO = ptask_tail* /\ S_result_raw.RESULT = S_result.RESULT /\ S_result_raw.BASE = BASE_VALUE S_result.RESULT',
    r'S_result_raw.STORE = S_result.STORE /\ S_result_raw.OBJECTPROPS = S_result.OBJECTPROPS /\ S_result_raw.EVENTS = S_result.EVENTS',
    r'S_done = $drive($bh_after(S_result,S_result_raw),1000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $bh_guard(S_done)',
    r'$bh_output(S_done.EVENTS) = EXPECTED_OUTPUT',
]


DERIVED = [
    r'~$property_hook_source(S,ppropertyhook[.SITE = ppropertyhook.HOOK]) /\ ~$property_hook_source(S,ppropertyhook[.LINE = 999])',
    r'$property_hook_function(S,ppropertyhook[.PROPERTY = ppropertyhook.HOOK]) = eps /\ $property_hook_function(S,ppropertyhook[.HOOK = ppropertyhook.SITE]) = eps',
    r'$property_hook_function(S[.FUNCTIONS = [pfunction_hook[.EARLY = true]]],ppropertyhook) = eps',
    r'$property_hook_function(S[.FUNCTIONS = [pfunction_hook[.NAME = $ptascii("wrong")]]],ppropertyhook) = eps',
    r'$property_hook_function(S[.FUNCTIONS = [pfunction_hook[.SIGNATURE.BYREF = true]]],ppropertyhook) = eps',
    r'$property_hook_function(S[.FUNCTIONS = [pfunction_hook[.BODY = eps]]],ppropertyhook) = eps',
    r'$property_hook_function(S[.CLASSNAMES = eps],ppropertyhook) = eps /\ ~$property_hook_source(S[.SOURCES = eps],ppropertyhook)',
    r'~$property_hook_valid(S[.ALLOCATIONS = eps],ppropertyhook,true) /\ $property_hook_valid(S[.ALLOCATIONS = eps],ppropertyhook,false)',
    r'~$property_hook_pending_call(S_call[.TODO = [CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook) eps 0 eps (ppropertyhook.SITE) ppropertyhook.LINE]],ppropertyhook)',
    r'~$property_hook_pending_call(S_call[.TODO[1] = PROPERTY_HOOK_RESULT ppropertyhook[.LINE = 999]],ppropertyhook)',
    r'~$property_hook_context_valid(S_entered,pcallcontext_hook[.CALLSITE = (ppropertyhook.HOOK)]) /\ ~$property_hook_context_valid(S_entered,pcallcontext_hook[.LINE = 999])',
    r'~$property_hook_context_valid(S_entered,pcallcontext_hook[.ARGC = 1]) /\ ~$property_hook_context_valid(S_entered,pcallcontext_hook[.EXTRA = [KNOWN (PINT 7)]])',
    r'~$property_hook_context_valid(S_entered,pcallcontext_hook[.NAMED = [($ptascii("extra"),KNOWN (PINT 7))]])',
    r'~$property_hook_context_valid(S_entered,pcallcontext_hook[.WRAPPER = ({SLOTS eps,NAMED eps})]) /\ ~$property_hook_context_valid(S_entered,pcallcontext_hook[.HOLES = [0]])',
    r'~$property_hook_context_valid(S_entered[.FRAMES[0].TODO = eps],pcallcontext_hook)',
    r'~$property_hook_backing(S_backing[.CURRENT = eps],ppropertyhook.OBJECT,ppropertydesc) /\ $property_hook_read_needed(S_backing[.CURRENT = eps],ppropertyhook.OBJECT,$ptascii("value"))',
]


HELPER = [
    r'S_helper_found = $bh_seek(S,7,1000)',
    r'S_helper_found.COMPLETION = NORMAL \/ S_helper_found.COMPLETION = BUDGET',
    r'S_helper = S_helper_found[.COMPLETION = NORMAL]',
    r'S_helper.CURRENT = (pcallcontext_helper)',
    r'pcallcontext_helper.NAME = $ptascii("hook_read28") /\ ~$property_hook_context_kind(pcallcontext_helper)',
    r'S_helper.FRAMES = pframe_helper :: pframe_helper_tail*',
    r'pframe_helper.CONTEXT = (pcallcontext_saved)',
    r'pcallcontext_saved.TARGET = PROPERTY_HOOK_TARGET ppropertyhook_saved',
    r'$property_effective_desc(S_helper,ppropertyhook_saved.OBJECT,$ptascii("value")) = (ppropertydesc_saved)',
    r'$property_hook_context_valid(S_helper,pcallcontext_saved) /\ $bh_guard(S_helper)',
    r'~$property_hook_backing(S_helper,ppropertyhook_saved.OBJECT,ppropertydesc_saved) /\ $property_hook_read_needed(S_helper,ppropertyhook_saved.OBJECT,$ptascii("value"))',
    r'S_read_found = $bh_seek(S_helper,0,1000)',
    r'S_read_found.COMPLETION = NORMAL \/ S_read_found.COMPLETION = BUDGET',
    r'S_read = S_read_found[.COMPLETION = NORMAL]',
    r'$property_hook_plan(S_read) = (ppropertyhook_read)',
    r'ppropertyhook_read.OBJECT = ppropertyhook_saved.OBJECT /\ ppropertyhook_read.PROPERTY = ppropertyhook_saved.PROPERTY /\ ppropertyhook_read.HOOK = ppropertyhook_saved.HOOK /\ ppropertyhook_read.SITE =/= ppropertyhook_saved.SITE',
    r'$bh_output(S_read.EVENTS) = $ptascii("G7|H|") /\ $bh_guard(S_read)',
    r'PhpStep: S_read ~> S_read_raw',
    r'S_read_raw.TODO[0] = CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook_read) eps 0 eps (ppropertyhook_read.SITE) ppropertyhook_read.LINE',
    r'S_done = $drive($bh_after(S_read,S_read_raw),1000)',
    r'S_done.COMPLETION = NORMAL /\ $bh_guard(S_done) /\ $bh_output(S_done.EVENTS) = EXPECTED_OUTPUT',
]


HELPER_DERIVED = [
    r'~$property_hook_context_valid(S_helper,pcallcontext_saved[.ARGC = 1])',
    r'~$property_hook_context_valid(S_helper,pcallcontext_saved[.EXTRA = [KNOWN (PINT 17)]])',
    r'~$property_hook_context_valid(S_helper[.FRAMES[0].CONTEXT = (pcallcontext_saved[.ARGC = 1])],pcallcontext_saved)',
]


HEAP = [
    r'$property_hook_plan(S) = (ppropertyhook)',
    r'$lookup(S.ENV,$ptascii("weak")) = (n_weak_cell)',
    r'S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
    r'$weakref_get(S,n_weak) = POBJECT n_leaf',
    r'$lookup(S.ENV,$ptascii("leaf")) = eps /\ $bh_guard(S)',
    r'$bh_slot(S,ppropertyhook.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (POBJECT n_leaf)))',
    r'$node_children(S,HOBJECT ppropertyhook.OBJECT) = [HOBJECT n_leaf] /\ $node_children(S,HOBJECT n_weak) = eps',
    r'$heap_owners($heap_prune($heap_graph(S)),HOBJECT ppropertyhook.OBJECT) = 1 /\ $heap_owners($heap_prune($heap_graph(S)),HOBJECT n_leaf) = 1',
    r'S_hold_found = $bh_seek(S,5,1000)',
    r'S_hold_found.COMPLETION = NORMAL \/ S_hold_found.COMPLETION = BUDGET',
    r'S_hold = S_hold_found[.COMPLETION = NORMAL]',
    r'S_hold.CURRENT = (pcallcontext_hold)',
    r'pcallcontext_hold.TARGET = PROPERTY_HOOK_TARGET ppropertyhook /\ pcallcontext_hold.RECEIVER = (ppropertyhook.OBJECT)',
    r'S_hold.GLOBALTABLE = (psymboltable_global)',
    r'$lookup(psymboltable_global.ENV,$ptascii("box")) = eps /\ $bh_output(S_hold.EVENTS) = $ptascii("G|")',
    r'$heap_owners($heap_prune($heap_graph(S_hold)),HOBJECT ppropertyhook.OBJECT) = 1 /\ $heap_owners($heap_prune($heap_graph(S_hold)),HOBJECT n_leaf) = 1 /\ $bh_guard(S_hold)',
    r'S_return_found = $bh_seek(S_hold,8,1000)',
    r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
    r'S_return = S_return_found[.COMPLETION = NORMAL]',
    r'S_return.TODO = [RETURN_UNWIND (KNOWN (POBJECT n_leaf)) porigin_return?]',
    r'S_return.CURRENT = (pcallcontext_hold) /\ $bh_output(S_return.EVENTS) = $ptascii("G|") /\ $bh_guard(S_return)',
    r'$heap_owners($heap_prune($heap_graph(S_return)),HOBJECT ppropertyhook.OBJECT) = 1 /\ $heap_owners($heap_prune($heap_graph(S_return)),HOBJECT n_leaf) = 2',
    r'PhpStep: S_return ~> S_return_raw',
    r'S_return_raw.RESULT = KNOWN PNULL /\ S_return_raw.COMPLETION = NORMAL /\ S_return_raw.CURRENT = eps',
    r'S_return_raw.DESTRUCTION.FRAMES = pdestructionframe_return :: pdestructionframe_tail*',
    r'pdestructionframe_return.VALUE = KNOWN (POBJECT n_leaf) /\ pdestructionframe_return.FUNCTION = ppropertyhook.HOOK /\ pdestructionframe_return.PENDING = eps',
    r'$task_nodes(DESTRUCTOR_FRAME_EXIT pdestructionframe_return) = [HOBJECT n_leaf]',
    r'S_return_ready = $bh_after(S_return,S_return_raw)',
    r'S_result_found = $bh_seek(S_return_ready,2,1000)',
    r'S_result_found.COMPLETION = NORMAL \/ S_result_found.COMPLETION = BUDGET',
    r'S_result = S_result_found[.COMPLETION = NORMAL]',
    r'S_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask_result*',
    r'S_result.RESULT = KNOWN (POBJECT n_leaf) /\ S_result.CURRENT = eps',
    r'$bh_output(S_result.EVENTS) = $ptascii("G|B|") /\ ~((HOBJECT ppropertyhook.OBJECT) <- S_result.ALLOCATIONS)',
    r'$heap_owners($heap_prune($heap_graph(S_result)),HOBJECT n_leaf) = 1 /\ $weakref_get(S_result,n_weak) = POBJECT n_leaf /\ $bh_guard(S_result)',
    r'$property_hook_valid(S_result,ppropertyhook,false) /\ ~$property_hook_valid(S_result,ppropertyhook,true)',
    r'PhpStep: S_result ~> S_result_raw',
    r'S_result_raw.RESULT = KNOWN (POBJECT n_leaf) /\ S_result_raw.BASE = BASE_VALUE (KNOWN (POBJECT n_leaf)) /\ S_result_raw.TODO = ptask_result*',
    r'S_unset_found = $bh_seek($bh_after(S_result,S_result_raw),6,1000)',
    r'S_unset_found.COMPLETION = NORMAL \/ S_unset_found.COMPLETION = BUDGET',
    r'S_unset = S_unset_found[.COMPLETION = NORMAL]',
    r'$lookup(S_unset.ENV,$ptascii("copy")) = (n_copy_cell)',
    r'S_unset.STORE[n_copy_cell] = DEFINED (POBJECT n_leaf)',
    r'$heap_owners($heap_prune($heap_graph(S_unset)),HOBJECT n_leaf) = 1 /\ $bh_output(S_unset.EVENTS) = $ptascii("G|B|L|") /\ $bh_guard(S_unset)',
    r'PhpStep: S_unset ~> S_unset_raw',
    r'S_done = $drive($bh_after(S_unset,S_unset_raw),1000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $bh_guard(S_done)',
    r'$weakref_get(S_done,n_weak) = PNULL /\ ~((HOBJECT n_leaf) <- S_done.ALLOCATIONS) /\ $bh_output(S_done.EVENTS) = EXPECTED_OUTPUT',
]


THROW = [
    r'S_throw_found = $bh_seek(S,4,1000)',
    r'S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET',
    r'S_throw = S_throw_found[.COMPLETION = NORMAL]',
    r'S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_throw*',
    r'S_throw.CURRENT = (pcallcontext_hook)',
    r'S_throw.RESULT = KNOWN (POBJECT n_error)',
    r'$property_hook_context_kind(pcallcontext_hook) /\ $property_hook_context_valid(S_throw,pcallcontext_hook) /\ $bh_guard(S_throw)',
    r'$trace_context_function(S_throw,pcallcontext_hook) = $ptascii("$value::get")',
    r'$trace_context_class(S_throw,pcallcontext_hook) = ($ptascii("HookThrows28")) /\ $trace_context_type(S_throw,pcallcontext_hook) = ($ptascii("->"))',
    r'$throwable_field(S_throw,n_error,"trace") = PARRAY n_trace',
    r'$trace_array_string(S_throw,n_trace) = EXPECTED_TRACE',
    r'PhpStep: S_throw ~> S_throw_raw',
    r'S_throw_raw.COMPLETION = THROWING n_error /\ S_throw_raw.OBJECTS = S_throw.OBJECTS /\ S_throw_raw.OBJECTPROPS = S_throw.OBJECTPROPS /\ S_throw_raw.EVENTS = S_throw.EVENTS',
    r'S_done = $drive($bh_after(S_throw,S_throw_raw),1000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $bh_guard(S_done)',
    r'$bh_output(S_done.EVENTS) = EXPECTED_OUTPUT',
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'backed_get_hook_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = ROOT / 'tests/semantics/profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    selections = [('basic', 'backing-read-write', 'read-write', BASIC, DERIVED),
                  ('helper', 'nested-helper-read', 'nested', HELPER, HELPER_DERIVED),
                  ('heap', 'receiver-unset-return', 'lifetime', HEAP, []),
                  ('throw', 'hook-throw-resume', 'throws', THROW, [])]
    sources, cases = [], []
    for _, case_id, suffix, _, _ in selections:
        source = HERE / ('backed-get-hook-' + suffix + '.php')
        case = next(row for row in data['cases'] if row['id'] == case_id)
        assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256']
        sources.append(source)
        cases.append(case)
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
    assert revision == args.revision and not status
    before = {str(path): sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='backed-get-hook-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    derived = sum(len(row[4]) for row in selections)
    reached = sum(5 + len(row[3]) for row in selections)
    assert derived == 19 and reached == 158
    report = {'revision': revision, 'inputs': before, 'profile': profile, 'module_count': len(modules),
              'mode': 'SL', 'cache': False, 'det': True, 'evaluated': False, 'records': [],
              'application_invocations': 0, 'application_evaluations': 0, 'source_agreements': 0,
              'derived_premises': derived, 'reached_premises': reached, 'premises': derived + reached,
              'budget_seconds': 120, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'jobs': 1}, 'passed': False}
    fixture = None
    try:
        flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
        fixtures = []
        for i, source in enumerate(sources):
            frontend = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(bridge), str(worker)], out / ('frontend-' + str(i)))
            adapter_worker = None
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted']
                adapter_worker = Worker([str(adapter), str(ROOT)], out / ('adapter-' + str(i)))
                checked = adapter_worker.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                assert checked['ok'] and checked['ast'] == parsed['ast']
                fixtures.append(checked['fixture'])
            finally:
                if adapter_worker: adapter_worker.close()
                frontend.close()
        content = PREFIX
        for selection, ast_fixture, source, case in zip(selections, fixtures, sources, cases):
            name, _, _, clauses, negatives = selection
            output = base64.b64decode(case.get('stdout_template_base64', case['stdout_base64']))
            output = output.replace(b'{FILE}', str(source).encode())
            trace = output.split(b'caught|', 1)[1].split(b'|resume|', 1)[0] if name == 'throw' else b''
            setup = ['S_initial = $php_run(' + ast_fixture + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $bh_seek(S_initial,0,1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            content += '\ndec $bh_' + name + '() : bool\ndef $bh_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                condition = condition.replace('EXPECTED_OUTPUT', byte_expr(output)).replace('EXPECTED_TRACE', byte_expr(trace))
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $bh_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = ($bh_basic() /\\ $bh_helper() /\\ $bh_heap() /\\ $bh_throw())\n'
        fixture = out / 'hook.watsup'
        fixture.write_text(content)
        report.update(fixture=str(fixture), fixture_sha256=sha(fixture), prepared=True, passed=True)
        if not args.prepare_only:
            process = recorder.recorded([str(compiler), 'algo', *map(str, modules), str(fixture)], out / 'compiler', 120)
            main_present = b'\ndef $main : bool =\n' in (out / 'compiler.stdout').read_bytes()
            passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and not (out / 'compiler.stderr').read_bytes() and main_present
            report['records'].append({'id': 'algorithmic-compilation', 'process': process, 'passed': passed, 'main_present': main_present, 'application_evaluations': 0})
            report['passed'] = passed
            assert passed
            report['application_invocations'] = 1
            process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'state', 120)
            output = (out / 'state.stdout').read_bytes()
            report['evaluated'] = process['exit'] == 0 and output in (b'true\n', b'false\n')
            report['application_evaluations'] = int(report['evaluated'])
            passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and not (out / 'state.stderr').read_bytes() and output == b'true\n'
            report['records'].append({'id': 'strict-SL-application', 'process': process, 'passed': passed})
            report['passed'] = passed
    finally:
        report.update(inputs_stable=before == {str(path): sha(path) for path in watched},
                      fixture_stable=fixture is None or report['fixture_sha256'] == sha(fixture),
                      head_stable=revision == git('rev-parse', 'HEAD'), status_stable=status == git('status', '--short'))
        report['passed'] = report['passed'] and all(report[key] for key in ('inputs_stable', 'fixture_stable', 'head_stable', 'status_stable'))
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({key: report[key] for key in ('passed', 'evaluated', 'derived_premises', 'reached_premises', 'inputs_stable', 'head_stable', 'status_stable')}), flush=True)
    assert report['passed']

if __name__ == '__main__':
    main()
