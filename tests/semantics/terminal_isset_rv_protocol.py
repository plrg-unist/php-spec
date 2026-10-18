"""Check terminal __isset truth, owning RV disposal and saved receiver lifetime."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()

PREFIX = r'''
syntax ptistage = TI_PREP | TI_CALL | TI_RV | TI_CACHE | TI_OUTPUT ptbytes | TI_MAIN ptbytes | TI_DTOR nat | TI_RAISED | TI_THROW | TI_CATCH
dec $ti_output(pevent*) : ptbytes
def $ti_output(eps) = eps
def $ti_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $ti_output(pevent*)
dec $ti_stage(pstate,ptistage) : bool
def $ti_stage(S,TI_PREP) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) z) :: (ORIGIN_RETURN (porigin)) :: (ISSET_RESULT false z) :: ptask_tail*
def $ti_stage(S,TI_CALL) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_ARGS (PROPERTY_ISSET_TARGET ppropertyisset) eps 1 poperand* porigin? z) :: (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*
def $ti_stage(S,TI_RV) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue
  -- if $value_nodes(pvalue) =/= eps
def $ti_stage(S,TI_CACHE) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*
  -- if S.RESULT = KNOWN (PBOOL b)
def $ti_stage(S,TI_OUTPUT ptbytes) = ($ti_output(S.EVENTS) = ptbytes)
def $ti_stage(S,TI_MAIN ptbytes) = (S.CURRENT = eps /\ S.FRAMES = eps /\ $ti_output(S.EVENTS) = ptbytes)
def $ti_stage(S,TI_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $ti_stage(S,TI_RAISED) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask_tail*
def $ti_stage(S,TI_THROW) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*
def $ti_stage(S,TI_CATCH) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask_tail*
def $ti_stage(S,ptistage) = false -- otherwise
dec $ti_seek(pstate,ptistage,nat) : pstate
def $ti_seek(S,ptistage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $ti_stage(S,ptistage) \/ n = 0
def $ti_seek(S,ptistage,n) = $ti_seek($drive_steps(S[.COMPLETION = NORMAL],1),ptistage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$ti_stage(S,ptistage) /\ $(n > 0)
def $ti_seek(S,ptistage,n) = $ti_seek($drive_steps(S,1),ptistage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $ti_seek(S,ptistage,n) = S -- otherwise
dec $ti_after(pstate,pstate) : pstate
def $ti_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $ti_guard(pstate) : bool
def $ti_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $gc_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $ti_in_isset(pstate,nat) : bool
def $ti_in_isset(S,n) = $property_isset_guard(S,S.CURRENT,S.FRAMES,n,$ptascii("value"))
dec $ti_in_get(pstate,nat) : bool
def $ti_in_get(S,n) = ($property_get_guard_tasks(S.TODO,n,$ptascii("value")) \/ $property_get_guard_frames(S.FRAMES,n,$ptascii("value")) \/ $property_empty_get_active(S,n,$ptascii("value")))
'''

def lines(text): return [line for line in text.strip().splitlines() if line]

PREP = lines(r'''
$ti_stage(S_prep,TI_PREP)
S_prep.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) z_site) :: (ORIGIN_RETURN (porigin_site)) :: (ISSET_RESULT false z_site) :: ptask_prep_tail*
S_prep.ORIGIN = (porigin_site)
$base64(text_name) = $ptascii("value")
S_prep.RESULT = VARIABLE ($ptascii("child")) z_child
$lookup(S_prep.ENV,$ptascii("child")) = (n_child_cell)
S_prep.STORE[n_child_cell] = DEFINED (POBJECT n_child)
$property_empty_prepare(S_prep) /\ ~$property_get_pending(S_prep)
$ti_output(S_prep.EVENTS) = ptbytes_prefix /\ $ti_guard(S_prep)
S_call_found = $ti_seek(S_prep,TI_CALL,1500)
S_call_found.COMPLETION = NORMAL \/ S_call_found.COMPLETION = BUDGET
S_call = S_call_found[.COMPLETION = NORMAL]
S_call.TODO = (CALL_ARGS (PROPERTY_ISSET_TARGET ppropertyisset) eps 1 poperand_sent* porigin_call? z_call) :: (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*
ppropertyisset.OBJECT = n_child /\ ppropertyisset.SITE = porigin_site /\ ppropertyisset.LINE = z_site
porigin_call? = (porigin_site) /\ z_call = z_site
poperand_sent* = [KNOWN (PSTRING ($ptascii("value")))]
$property_isset_untyped(S_call,ppropertyisset) /\ $property_isset_valid(S_call,ppropertyisset) /\ $property_isset_capture(S_call,ppropertyisset)
$property_isset_pending_call(S_call,ppropertyisset)
$property_isset_method(S_call,n_child) = (pmethoddesc_isset)
pfunction_isset = pmethoddesc_isset.FUNCTION
pfunction_isset.SIGNATURE.RETURNS = eps /\ $property_empty_isset_source(S_call,pmethoddesc_isset)
~$property_magic_method_source(S_call,pmethoddesc_isset,"__isset")
$target_function(S_call,PROPERTY_ISSET_TARGET ppropertyisset) = (pfunction_isset)
$target_lexical_class(S_call,PROPERTY_ISSET_TARGET ppropertyisset) = (pmethoddesc_isset.OWNER)
$target_called_class(S_call,PROPERTY_ISSET_TARGET ppropertyisset) = (ppropertyisset.CLASS)
$task_nodes(PROPERTY_ISSET_RESULT ppropertyisset) = [HOBJECT n_child] /\ $target_nodes(PROPERTY_ISSET_TARGET ppropertyisset) = eps
$heap_owners($heap_graph(S_call),HOBJECT n_child) = 2 /\ $ti_guard(S_call)
S_rv_found = $ti_seek(S_call,TI_RV,1500)
S_rv_found.COMPLETION = NORMAL \/ S_rv_found.COMPLETION = BUDGET
S = S_rv_found[.COMPLETION = NORMAL]
S.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*
S.CURRENT = eps /\ S.FRAMES = eps
$ti_output(S.EVENTS) = ptbytes_isset
$property_isset_rv_ready(S,ppropertyisset) /\ $ti_in_isset(S,n_child) /\ ~$ti_in_get(S,n_child)
$ti_guard(S)
''')
CACHE = lines(r'''
PhpStep: S ~> S_cached
S_cached = S[.RESULT = KNOWN (PBOOL b_truth)]
$heap_owners($heap_graph(S_cached),pnode_rv) = $(n_rv_owners - 1)
$ti_in_isset(S_cached,n_child)
S_disposing = $ti_after(S,S_cached)
''')
VALUE = lines(r'''
S_value_found = $ti_seek(S_disposing,TI_DTOR n_payload,1500)
S_value_found.COMPLETION = NORMAL \/ S_value_found.COMPLETION = BUDGET
S_value = S_value_found[.COMPLETION = NORMAL]
$ti_stage(S_value,TI_DTOR n_payload)
S_value.CURRENT = (pcallcontext_value)
$ti_output(S_value.EVENTS) = ptbytes_isset
$heap_owners($heap_graph(S_value),HOBJECT n_child) = 2
$ti_in_isset(S_value,n_child) /\ ~$ti_in_get(S_value,n_child)
S_value.FRAMES = pframe_value :: eps
S_saved = $constant_frame_view(S_value,pframe_value,eps)
S_saved.ORIGIN = (ppropertyisset.SITE)
$property_isset_cleanup(S_saved,ppropertyisset) /\ $call_task_valid(S_saved,PROPERTY_ISSET_RESULT ppropertyisset)
$ti_guard(S_value)
''')
NORMAL = lines(r'''
S_rebound_found = $ti_seek(S_value,TI_OUTPUT ptbytes_rebound,1500)
S_rebound_found.COMPLETION = NORMAL \/ S_rebound_found.COMPLETION = BUDGET
S_rebound = S_rebound_found[.COMPLETION = NORMAL]
S_rebound.CURRENT = (pcallcontext_value)
S_rebound.STORE[n_child_cell] = DEFINED PNULL
$heap_owners($heap_graph(S_rebound),HOBJECT n_child) = 1
$ti_in_isset(S_rebound,n_child) /\ ~$ti_in_get(S_rebound,n_child)
$property_isset_valid(S_rebound,ppropertyisset) /\ ~$property_isset_capture(S_rebound,ppropertyisset)
$ti_guard(S_rebound)
S_resume_found = $ti_seek(S_rebound,TI_CACHE,1500)
S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET
S_resume = S_resume_found[.COMPLETION = NORMAL]
S_resume.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*
S_resume.RESULT = KNOWN (PBOOL true)
~(HOBJECT n_payload <- S_resume.ALLOCATIONS)
$heap_owners($heap_graph(S_resume),HOBJECT n_child) = 1
$ti_guard(S_resume)
PhpStep: S_resume ~> S_release_raw
S_release_raw.TODO = ptask_tail* /\ S_release_raw.RESULT = KNOWN (PBOOL true)
$heap_owners($heap_graph(S_release_raw),HOBJECT n_child) = 0
S_child_found = $ti_seek($ti_after(S_resume,S_release_raw),TI_DTOR n_child,1500)
S_child_found.COMPLETION = NORMAL \/ S_child_found.COMPLETION = BUDGET
S_child = S_child_found[.COMPLETION = NORMAL]
$ti_stage(S_child,TI_DTOR n_child) /\ $ti_output(S_child.EVENTS) = ptbytes_rebound
~$ti_in_isset(S_child,n_child) /\ ~$ti_in_get(S_child,n_child)
$ti_guard(S_child)
S_end = S_child
''')
HELD = lines(r'''
S_resume_found = $ti_seek(S_disposing,TI_CACHE,1500)
S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET
S_resume = S_resume_found[.COMPLETION = NORMAL]
S_resume.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*
S_resume.RESULT = KNOWN (PBOOL true) /\ S_resume.EVENTS = S.EVENTS
HARRAY n_rv <- S_resume.ALLOCATIONS /\ $heap_owners($heap_graph(S_resume),HARRAY n_rv) = 1
$node_children(S_resume,HARRAY n_rv) = [HOBJECT n_payload]
~(n_payload <- S_resume.DESTRUCTION.CALLED) /\ $heap_owners($heap_graph(S_resume),HOBJECT n_child) = 2
$ti_guard(S_resume)
PhpStep: S_resume ~> S_release_raw
S_release_raw.RESULT = KNOWN (PBOOL true) /\ S_release_raw.TODO = ptask_tail*
$heap_owners($heap_graph(S_release_raw),HOBJECT n_child) = 1
ptbytes_main = ptbytes_isset ++ $ptascii("T|F|")
S_main_found = $ti_seek($ti_after(S_resume,S_release_raw),TI_MAIN ptbytes_main,1500)
S_main_found.COMPLETION = NORMAL \/ S_main_found.COMPLETION = BUDGET
S_main = S_main_found[.COMPLETION = NORMAL]
$ti_stage(S_main,TI_MAIN ptbytes_main)
$heap_owners($heap_graph(S_main),HARRAY n_rv) = 1 /\ $heap_owners($heap_graph(S_main),HOBJECT n_child) = 1
~$ti_in_isset(S_main,n_child) /\ $ti_guard(S_main)
S_value_found = $ti_seek(S_main,TI_DTOR n_payload,1500)
S_value_found.COMPLETION = NORMAL \/ S_value_found.COMPLETION = BUDGET
S_value = S_value_found[.COMPLETION = NORMAL]
$ti_stage(S_value,TI_DTOR n_payload)
~(HARRAY n_rv <- S_value.ALLOCATIONS) /\ ~(HARRAY n_rv <- $gc_nodes(S_value.GC.BUFFER))
S_value.CURRENT = (pcallcontext_value)
$ti_output(S_value.EVENTS) = ptbytes_main
$ti_guard(S_value) /\ ~$ti_in_isset(S_value,n_child)
S_child_found = $ti_seek(S_value,TI_DTOR n_child,1500)
S_child_found.COMPLETION = NORMAL \/ S_child_found.COMPLETION = BUDGET
S_child = S_child_found[.COMPLETION = NORMAL]
$ti_stage(S_child,TI_DTOR n_child) /\ $ti_output(S_child.EVENTS) = ptbytes_main ++ $ptascii("V|")
$ti_guard(S_child)
~$ti_in_isset(S_child,n_child) /\ ~$ti_in_get(S_child,n_child)
S_rebound_found = $ti_seek(S_child,TI_OUTPUT ptbytes_rebound,1500)
S_rebound_found.COMPLETION = NORMAL \/ S_rebound_found.COMPLETION = BUDGET
S_rebound = S_rebound_found[.COMPLETION = NORMAL]
S_rebound.CURRENT = (pcallcontext_value)
S_rebound.STORE[n_child_cell] = DEFINED PNULL /\ ~(HOBJECT n_child <- S_rebound.ALLOCATIONS)
$ti_guard(S_rebound)
S_end = S_rebound
''')
THROW = lines(r'''
S_raised_found = $ti_seek(S_value,TI_RAISED,1500)
S_raised_found.COMPLETION = NORMAL \/ S_raised_found.COMPLETION = BUDGET
S_raised = S_raised_found[.COMPLETION = NORMAL]
S_raised.CURRENT = (pcallcontext_value)
S_raised.TODO = (THROW_SEARCH n_error) :: ptask_throw*
S_raised.STORE[n_child_cell] = DEFINED PNULL
$throwable_live(S_raised,n_error) /\ $ti_in_isset(S_raised,n_child)
$ti_output(S_raised.EVENTS) = ptbytes_rebound
S_throw_found = $ti_seek(S_raised,TI_THROW,1500)
S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET
S_throw = S_throw_found[.COMPLETION = NORMAL]
S_throw.TODO = (THROW_SEARCH n_error) :: (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*
~(HARRAY n_rv <- S_throw.ALLOCATIONS) /\ ~(HOBJECT n_payload <- S_throw.ALLOCATIONS)
$heap_owners($heap_graph(S_throw),HOBJECT n_child) = 1
$property_isset_throw_tail(S_throw,ppropertyisset) /\ ~$property_isset_capture(S_throw,ppropertyisset)
$ti_guard(S_throw)
PhpStep: S_throw ~> S_release_raw
S_release_raw.TODO = (THROW_SEARCH n_error) :: ptask_tail*
S_release_raw.RESULT = KNOWN PNULL /\ S_release_raw.EVENTS = S_throw.EVENTS
$heap_owners($heap_graph(S_release_raw),HOBJECT n_child) = 0
S_child_found = $ti_seek($ti_after(S_throw,S_release_raw),TI_DTOR n_child,1500)
S_child_found.COMPLETION = NORMAL \/ S_child_found.COMPLETION = BUDGET
S_child = S_child_found[.COMPLETION = NORMAL]
$ti_stage(S_child,TI_DTOR n_child) /\ $ti_output(S_child.EVENTS) = ptbytes_rebound
~$ti_in_isset(S_child,n_child) /\ ~$ti_in_get(S_child,n_child)
$ti_guard(S_child)
S_catch_found = $ti_seek(S_child,TI_CATCH,1500)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_try n_catch n_error) :: ptask_catch*
$lookup(S_catch.ENV,$ptascii("answer")) = (n_answer)
S_catch.STORE[n_answer] = DEFINED (PINT 42)
$throwable_live(S_catch,n_error) /\ $ti_guard(S_catch)
PhpStep: S_catch ~> S_catch_raw
$lookup(S_catch_raw.ENV,$ptascii("caught")) = (n_caught)
S_catch_raw.STORE[n_caught] = DEFINED (POBJECT n_error)
S_end = $ti_after(S_catch,S_catch_raw)
''')
EMPTY = lines(r'''
S.STORE[n_child_cell] = DEFINED PNULL /\ ~$property_isset_capture(S,ppropertyisset)
S_resume_found = $ti_seek(S_disposing,TI_CACHE,1500)
S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET
S_resume = S_resume_found[.COMPLETION = NORMAL]
S_resume.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*
S_resume.RESULT = KNOWN (PBOOL false) /\ S_resume.EVENTS = S.EVENTS
~(HARRAY n_rv <- S_resume.ALLOCATIONS) /\ ~(HARRAY n_rv <- $gc_nodes(S_resume.GC.BUFFER))
$heap_owners($heap_graph(S_resume),HOBJECT n_child) = 1 /\ $ti_in_isset(S_resume,n_child) /\ $ti_guard(S_resume)
PhpStep: S_resume ~> S_release_raw
S_release_raw.TODO = ptask_tail* /\ S_release_raw.RESULT = KNOWN (PBOOL false)
$heap_owners($heap_graph(S_release_raw),HOBJECT n_child) = 0
S_child_found = $ti_seek($ti_after(S_resume,S_release_raw),TI_DTOR n_child,1500)
S_child_found.COMPLETION = NORMAL \/ S_child_found.COMPLETION = BUDGET
S_child = S_child_found[.COMPLETION = NORMAL]
$ti_stage(S_child,TI_DTOR n_child) /\ $ti_output(S_child.EVENTS) = ptbytes_isset
~(HARRAY n_rv <- S_child.ALLOCATIONS)
~$ti_in_isset(S_child,n_child) /\ ~$ti_in_get(S_child,n_child)
$ti_guard(S_child)
S_end = S_child
''')
FINISH = lines(r'''
S_final = $drive_steps(S_end,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$ti_output(S_final.EVENTS) = ptbytes_final
~(HOBJECT n_child <- S_final.ALLOCATIONS) /\ ~(pnode_rv <- S_final.ALLOCATIONS)
$ti_guard(S_final)
S_budget = $drive_steps(S_prep,0)
S_budget.COMPLETION = BUDGET /\ S_budget.TODO = S_prep.TODO /\ S_budget.EVENTS = S_prep.EVENTS
$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final
''')
REFUSALS = lines(r'''
S_flag = S_prep[.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) z_site) :: (ORIGIN_RETURN (porigin_site)) :: (ISSET_RESULT true z_site) :: ptask_prep_tail*]
~$property_empty_prepare(S_flag) /\ $property_get_pending(S_flag)
PhpStep: S_flag ~> S_flag_done
S_flag_done.COMPLETION = UNSUPPORTED "magic getter receiver, signature or recursive access"
S_source = S_prep[.ORIGIN = eps]
~$property_empty_prepare(S_source)
S_std_created = $new_class(S,$ptascii("stdClass"),z_site)
S_std_created.RESULT = KNOWN (POBJECT n_std)
S_std = S_std_created[.HELD = S.HELD ++ [HOBJECT n_payload]]
$ti_guard(S_std) /\ ~$property_isset_rv_ready(S_std,ppropertyisset)
PhpStep: S_std ~> S_std_done
S_std_done.COMPLETION = UNSUPPORTED "magic isset result type"
S_saved.TODO = (DESTRUCTOR_RESULT pdestructorcall_saved) :: (DESTRUCTOR_RELEASE pdestructionrelease_saved) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_saved) :: (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_saved_tail*
S_saved.DESTRUCTION.CALLS = pdestructorcall_saved :: pdestructorcall_tail*
S_saved.DESTRUCTION.OPERATIONS = pdestructionoperation_saved :: pdestructionoperation_tail*
pdestructionoperation_source = pdestructionoperation_saved[.SOURCE = ISSET_RESULT false z_site]
pdestructorcall_source = pdestructorcall_saved[.OPERATION = (pdestructionoperation_source)]
S_wrong_source = S_saved[.TODO = (DESTRUCTOR_RESULT pdestructorcall_source) :: (DESTRUCTOR_RELEASE pdestructionrelease_saved) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_source) :: (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_saved_tail*][.DESTRUCTION.CALLS = pdestructorcall_source :: pdestructorcall_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_source :: pdestructionoperation_tail*]
~$property_isset_cleanup(S_wrong_source,ppropertyisset) /\ ~$call_task_valid(S_wrong_source,PROPERTY_ISSET_RESULT ppropertyisset)
pdestructionoperation_value = pdestructionoperation_saved[.VALUE = KNOWN (PBOOL false)]
pdestructorcall_value = pdestructorcall_saved[.OPERATION = (pdestructionoperation_value)]
S_wrong_value = S_saved[.TODO = (DESTRUCTOR_RESULT pdestructorcall_value) :: (DESTRUCTOR_RELEASE pdestructionrelease_saved) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_value) :: (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_saved_tail*][.DESTRUCTION.CALLS = pdestructorcall_value :: pdestructorcall_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_value :: pdestructionoperation_tail*]
~$property_isset_cleanup(S_wrong_value,ppropertyisset) /\ ~$call_task_valid(S_wrong_value,PROPERTY_ISSET_RESULT ppropertyisset)
''')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', action='append', choices=('normal', 'held', 'throwing', 'empty'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'terminal_isset_rv_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_gate_completed']
    assert [case['id'] for case in data['cases']] == ['normal', 'held', 'throwing', 'empty']
    selected = list(data['cases'])
    assert len(selected) == 4
    if args.case:
        selected = [case for case in selected if case['id'] in args.case]
    php, adapter, bridge, worker, runner, compiler = (ROOT / name for name in [
        '.tools/php/bin/php', '_build/default/adapter/main.exe', '.tools/php-file.so',
        'frontend/worker.php', 'tests/semantics/_build/default/numeric_runner.exe', '.tools/spectec/bin/p4spectec'])
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    assert sha(compiler) == '26d77fb9bfae2b2868e137a94051f55f9b607660c340e9b22ae8300fb0d8ce88'
    assert sha(runner) == 'b57a2ed7daf86de23993a29d079083377cfef6da133739a164dbfdb9f11fd7a0'
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_bytes())]
    watched = [Path(__file__), Path(recorder.__file__), catalogue, profile_file, php, adapter, bridge, worker, runner, compiler,
               manifest, *modules, *(HERE / case['source_file'] for case in data['cases']),
               *(ROOT / name for name in ['spec/schema.json', 'spec/php.watsup', 'spec/nodes.json', 'frontend/target.php',
                    'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py'])]
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    assert revision == args.revision and not status, (revision, status)
    before = {str(path): sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='terminal-isset-rv-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    report = {'revision': revision, 'inputs': before, 'profile': profile, 'module_count': len(modules),
              'mode': 'SL', 'cache': False, 'det': True, 'records': [], 'fixtures': [], 'selection': [case['id'] for case in selected],
              'application_invocations': 0, 'application_evaluations': 0, 'source_agreements': 0,
              'premises': 0, 'reached_premises': 0, 'derived_premises': 0,
              'cap_seconds': 90, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent', 'jobs': 1}, 'passed': False}
    try:
        flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
        for case in selected:
            name = case['id']
            source = HERE / case['source_file']
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256']
            native_stderr = base64.b64decode(case['stderr_template_base64']).replace(b'{FILE}', case['original_source'].encode())
            native_tuple = base64.b64decode(case['stdout_base64']) + b'\0' + native_stderr + b'\0' + str(case['exit_status']).encode()
            assert hashlib.sha256(native_tuple).hexdigest() == case['native_raw_sha256']
            directory = out / name
            directory.mkdir()
            frontend = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(bridge), str(worker)], directory / 'frontend')
            adapter_worker = None
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted'], parsed
                adapter_worker = Worker([str(adapter), str(ROOT)], directory / 'adapter')
                checked = adapter_worker.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                assert checked['ok'] and checked['ast'] == parsed['ast']
            finally:
                if adapter_worker:
                    adapter_worker.close()
                frontend.close()
            name = case['id']
            output = base64.b64decode(case['stdout_base64']).decode()
            prefix = {'normal':'N:', 'held':'H:', 'throwing':'X:', 'empty':'F:'}[name]
            isset = prefix + 'I|'
            rebound = isset + {'normal':'V|v|', 'held':'T|F|V|D|v|', 'throwing':'V|', 'empty':''}[name]
            reached = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                'S_prep_found = $ti_seek(S_initial,TI_PREP,2000)',
                r'S_prep_found.COMPLETION = NORMAL \/ S_prep_found.COMPLETION = BUDGET',
                'S_prep = S_prep_found[.COMPLETION = NORMAL]',
                'ptbytes_prefix = $ptascii(' + json.dumps(prefix) + ')',
                'ptbytes_isset = $ptascii(' + json.dumps(isset) + ')',
                'ptbytes_rebound = $ptascii(' + json.dumps(rebound) + ')',
                'ptbytes_final = $ptascii(' + json.dumps(output) + ')',
                'b_truth = ' + ('false' if name == 'empty' else 'true'),
                'n_rv_owners = ' + ('2' if name == 'held' else '1')]
            reached += PREP + [f'z_site = {case["isset_line"]}']
            if case['has_get']:
                reached += ['$property_get_method(S_call,n_child) = (pmethoddesc_get)',
                            '$target_function(S_call,METHOD_TARGET n_child pmethoddesc_get.FUNCTION.ORIGIN) = (pmethoddesc_get.FUNCTION)']
            else:
                reached += ['$property_get_method(S_call,n_child) = eps']
            if name == 'normal':
                reached += ['S.RESULT = KNOWN (POBJECT n_rv)', 'n_payload = n_rv', 'pnode_rv = HOBJECT n_rv']
            else:
                reached += ['S.RESULT = KNOWN (PARRAY n_rv)', 'pnode_rv = HARRAY n_rv', 'parray_rv = S.ARRAYS[n_rv]',
                            r'parray_rv.NEXT = 1 /\ parray_rv.SERIAL = 1 /\ ~$array_immutable(S,n_rv)']
                if name != 'empty':
                    reached += ['$entry_lookup(parray_rv.ITEMS,KINT 0) = (DIRECT (POBJECT n_payload))',
                                '$node_children(S,HARRAY n_rv) = [HOBJECT n_payload]']
                else:
                    reached += ['parray_rv.ITEMS = eps', '$node_children(S,HARRAY n_rv) = eps']
            reached += ['pnode_rv <- S.ALLOCATIONS', '$heap_owners($heap_graph(S),pnode_rv) = n_rv_owners',
                        '$truth(S,' + ('POBJECT' if name == 'normal' else 'PARRAY') + ' n_rv) = b_truth'] + CACHE
            if name == 'normal':
                reached += VALUE + NORMAL
            elif name == 'held':
                reached += HELD
            elif name == 'throwing':
                reached += ['$lookup(S.ENV,$ptascii("error")) = (n_error_cell)', 'S.STORE[n_error_cell] = DEFINED (POBJECT n_error)'] + VALUE + THROW
            else:
                reached += EMPTY
            reached += FINISH
            if name != 'empty':
                reached += ['~(HOBJECT n_payload <- S_final.ALLOCATIONS)']
            derived = REFUSALS if name == 'normal' else []
            content = PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
            for condition in reached + derived:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $main() = false -- otherwise\n'
            fixture = directory / 'hook.watsup'
            fixture.write_text(content)
            row = {'id': name, 'path': str(fixture), 'sha256': sha(fixture), 'reached_premises': len(reached), 'derived_premises': len(derived), 'premises': len(reached) + len(derived)}
            report['fixtures'].append(row)
            for key in ('premises', 'reached_premises', 'derived_premises'):
                report[key] += row[key]
        report.update(prepared=True, passed=True)
        if not args.prepare_only:
            for fixture in report['fixtures']:
                directory = Path(fixture['path']).parent
                process = recorder.recorded([str(compiler), 'algo', *map(str, modules), fixture['path']], directory / 'compiler', 90)
                passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and not (directory / 'compiler.stderr').read_bytes() and b'\ndef $main : bool =\n' in (directory / 'compiler.stdout').read_bytes()
                report['records'].append({'id': fixture['id'] + '-algorithmic-compilation', 'process': process, 'passed': passed, 'application_evaluations': 0})
                report['passed'] = passed
                assert passed
                report['application_invocations'] += 1
                process = recorder.recorded([str(runner), '--sl', *map(str, modules), fixture['path']], directory / 'state', 90)
                output = (directory / 'state.stdout').read_bytes()
                evaluated = process['exit'] == 0 and output in (b'true\n', b'false\n')
                report['application_evaluations'] += int(evaluated)
                passed = evaluated and not process['timeout'] and not process['group_after'] and not (directory / 'state.stderr').read_bytes() and output == b'true\n'
                report['records'].append({'id': fixture['id'] + '-strict-SL-application', 'process': process, 'passed': passed})
                report['passed'] = passed
                assert passed
    finally:
        report.update(inputs_stable=before == {str(path): sha(path) for path in watched},
                      fixtures_stable=all(row['sha256'] == sha(Path(row['path'])) for row in report['fixtures']),
                      head_stable=revision == git('rev-parse', 'HEAD'), status_stable=status == git('status', '--short'))
        report['passed'] = report['passed'] and all(report[key] for key in ('inputs_stable', 'fixtures_stable', 'head_stable', 'status_stable'))
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({key: report[key] for key in ('passed', 'application_evaluations', 'premises', 'reached_premises', 'derived_premises', 'inputs_stable', 'head_stable', 'status_stable')}), flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
