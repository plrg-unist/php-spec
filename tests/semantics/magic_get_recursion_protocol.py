"""Check per-name implicit Get recursion, captured NULL and local-exit authority."""
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
syntax pgrstage = GR_OUTER | GR_ENTER porigin | GR_RECURSE | GR_INVOKE | GR_HANDLER | GR_WARNING_RESULT | GR_WARNING_THROW | GR_GET_RESULT | GR_GET_COPY | GR_GET_THROW | GR_EXIT | GR_DTOR nat | GR_CATCH | GR_OUTPUT ptbytes | GR_TAIL ptask*
dec $gr_output(pevent*) : ptbytes
dec $gr_output_event(pevent) : bool
def $gr_output(eps) = eps
def $gr_output((OUTPUT ptbytes) :: pevent_tail*) = ptbytes ++ $gr_output(pevent_tail*)
def $gr_output(pevent :: pevent_tail*) = $gr_output(pevent_tail*) -- if ~$gr_output_event(pevent)
def $gr_output_event(OUTPUT ptbytes) = true
def $gr_output_event(pevent) = false -- otherwise
dec $gr_stage(pstate,pgrstage) : bool
def $gr_stage(S,GR_OUTER) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if $property_get_plan(S) =/= eps
;; Complete untyped arguments enter the body directly, without TYPE_RECEIVE.
def $gr_stage(S,GR_ENTER porigin) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_GET_TARGET n porigin
  -- if pcallcontext.FUNCTION = porigin /\ S.ORIGIN = (porigin)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if $property_get_frame(S,pcallcontext,pframe)
def $gr_stage(S,GR_RECURSE) = ($property_get_recursive_plan(S) =/= eps)
def $gr_stage(S,GR_INVOKE) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning
def $gr_stage(S,GR_HANDLER) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning
def $gr_stage(S,GR_WARNING_RESULT) = true
  -- if S.TODO = (PROPERTY_UNDEFINED_RESULT ppropertywarning) :: ptask_tail*
def $gr_stage(S,GR_WARNING_THROW) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning
def $gr_stage(S,GR_GET_RESULT) = true
  -- if S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $gr_stage(S,GR_GET_COPY) = true
  -- if S.TODO = (PROPERTY_GET_COPY ppropertyget poperand) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $gr_stage(S,GR_GET_THROW) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $gr_stage(S,GR_EXIT) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $gr_stage(S,GR_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $gr_stage(S,GR_CATCH) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask_tail*
  -- if S.CURRENT = eps
def $gr_stage(S,GR_OUTPUT ptbytes) = ($gr_output(S.EVENTS) = ptbytes)
def $gr_stage(S,GR_TAIL ptask*) = (S.TODO = ptask*)
def $gr_stage(S,pgrstage) = false -- otherwise
dec $gr_seek(pstate,pgrstage,nat) : pstate
def $gr_seek(S,pgrstage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $gr_stage(S,pgrstage) \/ n = 0
def $gr_seek(S,pgrstage,n) = $gr_seek($drive_steps(S[.COMPLETION = NORMAL],1),pgrstage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$gr_stage(S,pgrstage) /\ $(n > 0)
def $gr_seek(S,pgrstage,n) = $gr_seek($drive_steps(S,1),pgrstage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $gr_seek(S,pgrstage,n) = S -- otherwise
dec $gr_after(pstate,pstate) : pstate
def $gr_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $gr_guard(pstate) : bool
def $gr_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $object_tables_valid(S) /\ $gc_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $gr_active(pstate,nat,ptbytes) : bool
def $gr_active(S,n,ptbytes) = $property_get_recursive_guard(S,S.CURRENT,S.FRAMES,n,ptbytes)
'''

def lines(text): return [line for line in text.strip().splitlines() if line]
def reach(name, previous, stage):
    return [f'{name}_found = $gr_seek({previous},{stage},2000)',
            fr'{name}_found.COMPLETION = NORMAL \/ {name}_found.COMPLETION = BUDGET',
            f'{name} = {name}_found[.COMPLETION = NORMAL]', f'$gr_stage({name},{stage})']

FRONT = lines(r'''
$property_get_plan(S_front) = (ppropertyget)
n_child = ppropertyget.OBJECT
ptbytes_name = $ptascii("ghost")
ppropertyget.NAME = ptbytes_name /\ ppropertyget.DECL = eps
S_front.TODO = (PROPERTY_PREP phpType20_outer ppropertyget.LINE) :: (DIM_FETCH ppropertyget.LINE) :: ptask_tail*
S_front.ORIGIN = (ppropertyget.SITE)
$lookup(S_front.ENV,$ptascii("child")) = (n_child_cell)
S_front.STORE[n_child_cell] = DEFINED (POBJECT n_child)
$property_get_source(S_front,ppropertyget) /\ $property_get_capture(S_front,ppropertyget)
$property_effective_desc(S_front,n_child,ptbytes_name) = eps
$property_get_method(S_front,n_child) = (pmethoddesc_get)
pmethoddesc_get.FUNCTION.ORIGIN = ppropertyget.METHOD
ppropertyget.SITE =/= ppropertyget.METHOD
$heap_owners($heap_graph(S_front),HOBJECT n_child) = 1
~$gr_active(S_front,n_child,ptbytes_name)
$property_get_recursive_plan(S_front) = eps
$gr_output(S_front.EVENTS) = ptbytes_prefix
$gr_guard(S_front)
PhpStep: S_front ~> S_call_raw
S_call = $gr_after(S_front,S_call_raw)
S_call.TODO = (CALL_ARGS (PROPERTY_GET_TARGET n_child ppropertyget.METHOD) eps 1 ([KNOWN (PSTRING ptbytes_name)]) (ppropertyget.SITE) ppropertyget.LINE) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
$property_get_pending_call(S_call,PROPERTY_GET_TARGET n_child ppropertyget.METHOD,ppropertyget.SITE)
$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_child]
$target_nodes(PROPERTY_GET_TARGET n_child ppropertyget.METHOD) = eps
$heap_owners($heap_graph(S_call),HOBJECT n_child) = 2
~$gr_active(S_call,n_child,ptbytes_name) /\ $gr_guard(S_call)
''')
ENTER = lines(r'''
S_get.CURRENT = (pcallcontext_get)
pcallcontext_get.TARGET = PROPERTY_GET_TARGET n_child ppropertyget.METHOD
S_get.FRAMES = [pframe_get]
pframe_get.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
$lookup(S_get.ENV,$ptascii("name")) = (n_name_cell)
S_get.STORE[n_name_cell] = DEFINED (PSTRING ptbytes_name)
$property_get_frame(S_get,pcallcontext_get,pframe_get)
$property_get_recursive_frame(S_get,pcallcontext_get,pframe_get,n_child,ptbytes_name)
$property_get_recursive_guard(S_get,S_get.CURRENT,S_get.FRAMES,n_child,ptbytes_name)
$call_receiver_roots(pcallcontext_get) = eps
$heap_owners($heap_graph(S_get),HOBJECT n_child) = 2
$gr_guard(S_get)
''')
INNER = lines(r'''
S_inner.TODO = (PROPERTY_PREP phpType20_inner z_inner) :: (DIM_FETCH z_inner) :: ptask_inner_tail*
S_inner.ORIGIN = (porigin_inner)
$property_get_recursive_plan(S_inner) = (ppropertywarning)
ppropertywarning = {READ {SITE porigin_inner, NAME ptbytes_name, LINE z_inner}, OBJECT n_child, KEY ptbytes_name, FREEING false, BORROWED true, CELL eps}
$property_null_read_valid(S_inner,ppropertywarning.READ)
$property_get_recursive_history(S_inner,ppropertywarning)
$property_undefined_read_valid(S_inner,ppropertywarning)
$property_undefined_slot(S_inner,n_child,ptbytes_name)
$property_undefined_cv_receiver(S_inner,ppropertywarning)
$property_get_plan(S_inner) = eps
$gr_active(S_inner,n_child,ptbytes_name) /\ $gr_guard(S_inner)
$property_get_recursive_guard(S_inner,S_inner.CURRENT,S_inner.FRAMES,n_child,$ptascii("other")) = false
$property_get_recursive_guard(S_inner,S_inner.CURRENT,S_inner.FRAMES,|S_inner.OBJECTS|,ptbytes_name) = false
PhpStep: S_inner ~> S_invoke_raw
S_invoke_pending = $gr_after(S_inner,S_invoke_raw)
''')
INVOKE = lines(r'''
S_invoke.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_inner_tail*
perrorcall.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning
perrorcall.TARGET = eps
perrorcall.SITE = porigin_inner /\ perrorcall.LINE = z_inner /\ perrorcall.LEVEL = 2
perrorcall.MESSAGE = $ptascii("Undefined property: RecursiveGet119::$ghost")
perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE z_inner
$error_call_valid(S_invoke,perrorcall)
$task_nodes(PROPERTY_UNDEFINED_RESULT ppropertywarning) = eps
S_invoke.RESULT = KNOWN PNULL /\ S_invoke.BASE = BASE_VALUE (KNOWN PNULL)
$heap_owners($heap_graph(S_invoke),HOBJECT n_child) = n_warning_owners
$gr_output(S_invoke.EVENTS) = ptbytes_before_warning
$gr_active(S_invoke,n_child,ptbytes_name) /\ $gr_guard(S_invoke)
''')
HANDLER = lines(r'''
S_handler.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_inner_tail*
perrorcall_entered.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning
perrorcall_entered.TARGET =/= eps
S_handler.RESULT = KNOWN (PBOOL true)
$error_entered_call_valid(S_handler,perrorcall_entered)
$property_get_recursive_history(S_handler,ppropertywarning)
$property_undefined_read_valid(S_handler,ppropertywarning)
$heap_owners($heap_graph(S_handler),HOBJECT n_child) = n_after_warning_owners
$gr_output(S_handler.EVENTS) = ptbytes_after_warning
$gr_active(S_handler,n_child,ptbytes_name) /\ $gr_guard(S_handler)
''')
RESUME = lines(r'''
S_resume.TODO = (PROPERTY_UNDEFINED_RESULT ppropertywarning) :: ptask_inner_tail*
$call_task_valid(S_resume,PROPERTY_UNDEFINED_RESULT ppropertywarning)
S_resume.RESULT = KNOWN PNULL /\ S_resume.BASE = BASE_VALUE (KNOWN PNULL)
$heap_owners($heap_graph(S_resume),HOBJECT n_child) = n_after_warning_owners
$property_get_recursive_history(S_resume,ppropertywarning)
$gr_active(S_resume,n_child,ptbytes_name) /\ $gr_guard(S_resume)
PhpStep: S_resume ~> S_read_raw
S_read_raw = S_resume[.TODO = ptask_inner_tail*]
S_read = $gr_after(S_resume,S_read_raw)
S_read.RESULT = KNOWN PNULL /\ S_read.BASE = BASE_VALUE (KNOWN PNULL)
$gr_guard(S_read)
''')
RESULT = lines(r'''
S_result.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
S_result.RESULT = KNOWN pvalue_result
$property_get_valid(S_result,ppropertyget,true)
$property_get_verify(S_result,ppropertyget,S_result.RESULT) = S_result
~$gr_active(S_result,n_child,ptbytes_name)
$heap_owners($heap_graph(S_result),HOBJECT n_child) = n_at_result_owners
$gr_output(S_result.EVENTS) = ptbytes_before_result
$gr_guard(S_result)
PhpStep: S_result ~> S_copy_raw
S_copy_raw.TODO = (PROPERTY_GET_COPY ppropertyget (KNOWN pvalue_result)) :: ptask_tail*
$task_nodes(PROPERTY_GET_COPY ppropertyget (KNOWN pvalue_result)) = eps
S_copy_pending = $gr_after(S_result,S_copy_raw)
''')
COPY = lines(r'''
S_copy.TODO = (PROPERTY_GET_COPY ppropertyget (KNOWN pvalue_result)) :: ptask_tail*
S_copy.TODO = S_copy_raw.TODO
~$gr_active(S_copy,n_child,ptbytes_name)
$heap_owners($heap_graph(S_copy),HOBJECT n_child) = n_external_owners
$call_task_valid(S_copy,PROPERTY_GET_COPY ppropertyget (KNOWN pvalue_result))
$gr_guard(S_copy)
PhpStep: S_copy ~> S_copied_raw
S_copied_raw.TODO = ptask_tail*
S_copied_raw.RESULT = KNOWN pvalue_result
S_copied = $gr_after(S_copy,S_copied_raw)
$gr_guard(S_copied)
''')
CHILD = lines(r'''
S_child.CURRENT = (pcallcontext_child)
$destructor_context_call(pcallcontext_child,S_child.CURRENT,S_child.FRAMES) = (pdestructorcall_child)
pdestructorcall_child.OBJECT = n_child
pdestructorcall_child.OPERATION = (pdestructionoperation_child)
S_child.FRAMES = [pframe_child]
~$gr_active(S_child,n_child,ptbytes_name)
$gr_guard(S_child)
''')
RESET = lines(r'''
$property_get_plan(S_again) = (ppropertyget_again)
ppropertyget_again.OBJECT = n_child /\ ppropertyget_again.NAME = ptbytes_name /\ ppropertyget_again.METHOD = ppropertyget.METHOD
ppropertyget_again.SITE =/= ppropertyget.SITE
$property_get_capture(S_again,ppropertyget_again)
$property_get_recursive_plan(S_again) = eps
~$gr_active(S_again,n_child,ptbytes_name)
$heap_owners($heap_graph(S_again),HOBJECT n_child) = 1
$gr_guard(S_again)
''')
FINISH = lines(r'''
S_final = $drive_steps(S_end,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$gr_output(S_final.EVENTS) = ptbytes_final
~((HOBJECT n_child) <- S_final.ALLOCATIONS) /\ $gr_guard(S_final)
S_budget = $drive_steps(S_front,0)
S_budget = S_front[.COMPLETION = BUDGET]
$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final
''')
DERIVED = lines(r'''
~$property_get_recursive_frame(S_get,pcallcontext_get[.TARGET = METHOD_TARGET n_child ppropertyget.METHOD],pframe_get,n_child,ptbytes_name)
~$property_get_recursive_history(S_inner,ppropertywarning[.READ.LINE = 999])
~$property_get_recursive_history(S_inner,ppropertywarning[.READ.NAME = $ptascii("other")])
~$property_get_recursive_history(S_inner,ppropertywarning[.KEY = $ptascii("other")])
~$property_get_recursive_history(S_inner,ppropertywarning[.BORROWED = false])
~$property_get_recursive_history(S_inner,ppropertywarning[.FREEING = true])
~$property_get_recursive_history(S_inner,ppropertywarning[.OBJECT = |S_inner.OBJECTS|])
S_no_call = S_inner[.CURRENT = eps][.FRAMES = eps]
~$gr_active(S_no_call,n_child,ptbytes_name)
$property_get_recursive_plan(S_no_call) = eps
S_queued = S_get[.CURRENT = eps][.FRAMES = eps][.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*]
~$gr_active(S_queued,n_child,ptbytes_name)
''')
POPULATED = lines(r'''
$objectprops_at(S_handler.OBJECTPROPS,n_child) = (ppropertyslot_populated_all*)
$property_slot_at(ppropertyslot_populated_all*,ptbytes_name) = (ppropertyslot_populated)
ppropertyslot_populated.DECL = eps /\ ppropertyslot_populated.STATE = PROP_VALUE (DIRECT (PINT 9))
~$property_undefined_slot(S_handler,n_child,ptbytes_name)
$property_get_recursive_history(S_handler,ppropertywarning)
S_populated_read = S_inner[.OBJECTPROPS = S_handler.OBJECTPROPS]
$gr_active(S_populated_read,n_child,ptbytes_name)
$property_get_recursive_plan(S_populated_read) = eps
$property_get_plan(S_populated_read) = eps
PhpStep: S_populated_read ~> S_populated_raw
S_populated_raw.TODO = (DIM_FETCH z_inner) :: ptask_inner_tail*
S_populated_value = $gr_after(S_populated_read,S_populated_raw)
S_populated_value.BASE = BASE_PROPERTY (POBJECT n_child) ptbytes_name
PhpStep: S_populated_value ~> S_populated_fetched_raw
S_populated_fetched_raw.TODO = ptask_inner_tail*
S_populated_fetched_raw.RESULT = KNOWN (PINT 9)
S_populated_pending = $gr_after(S_populated_value,S_populated_fetched_raw)
S_populated_pending.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_populated) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_populated) :: ptask_inner_tail*
S_populated_pending.RESULT = KNOWN PNULL
pdestructionoperation_populated.SOURCE = DIM_FETCH z_inner
pdestructionoperation_populated.VALUE = KNOWN (PINT 9) /\ pdestructionoperation_populated.PENDING = eps
S_populated_fetched_found = $gr_seek(S_populated_pending,GR_TAIL ptask_inner_tail*,2000)
S_populated_fetched_found.COMPLETION = NORMAL \/ S_populated_fetched_found.COMPLETION = BUDGET
S_populated_fetched = S_populated_fetched_found[.COMPLETION = NORMAL]
$gr_stage(S_populated_fetched,GR_TAIL ptask_inner_tail*)
S_populated_fetched.TODO = ptask_inner_tail*
S_populated_fetched.RESULT = KNOWN (PINT 9)
S_populated_fetched.EVENTS = S_inner.EVENTS
$gr_guard(S_populated_fetched)
''')
# S_probe_saved is a control projection; its guard checks that projection,
# not reachability of an actual saved-parent scope.
CLEANUP = lines(r'''
S_exit.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
pdestructionframe.FUNCTION = ppropertyget.METHOD /\ pdestructionframe.VALUE = KNOWN (PINT 7)
pdestructionframe <- S_exit.DESTRUCTION.FRAMES
$property_get_recursive_exit(S_exit,S_exit.TODO,ppropertyget) = (pdestructionframe)
$gr_active(S_exit,n_child,ptbytes_name) /\ $gr_guard(S_exit)
S_inner.CURRENT = (pcallcontext_probe)
$destructor_context_call(pcallcontext_probe,S_inner.CURRENT,S_inner.FRAMES) = (pdestructorcall_probe)
pdestructorcall_probe.FRAME = (pdestructionframe) /\ pdestructorcall_probe.OPERATION = eps
pdestructorcall_probe.CALLER = eps
pdestructionframe <- S_inner.DESTRUCTION.FRAMES
S_inner.FRAMES = [pframe_probe]
S_probe_saved = $constant_frame_view(S_inner,pframe_probe,eps)
S_probe_saved.TODO = (DESTRUCTOR_RESULT pdestructorcall_probe) :: (DESTRUCTOR_RELEASE pdestructionrelease_after) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
pdestructorcall_probe.RELEASE = (pdestructionrelease_before)
pdestructionrelease_before.JOBS = pdestructionjob_head :: pdestructionjob_tail*
$destruction_job_node(pdestructionjob_head) = (HOBJECT pdestructorcall_probe.OBJECT)
pdestructionrelease_after = pdestructionrelease_before[.JOBS = pdestructionjob_tail*]
$property_get_recursive_exit(S_probe_saved,S_probe_saved.TODO,ppropertyget) = (pdestructionframe)
$property_get_recursive_exit_task(S_probe_saved,PROPERTY_GET_RESULT ppropertyget,n_child,ptbytes_name)
$gr_guard(S_probe_saved)
$lookup(S_inner.ENV,$ptascii("receiver")) = (n_receiver_cell)
S_inner.STORE[n_receiver_cell] = DEFINED (POBJECT n_child)
''')
CLEANUP_DERIVED = lines(r'''
S_missing_frame = S_exit[.DESTRUCTION.FRAMES = eps]
$property_get_recursive_exit(S_missing_frame,S_missing_frame.TODO,ppropertyget) = (pdestructionframe)
~$property_get_recursive_exit_task(S_missing_frame,PROPERTY_GET_RESULT ppropertyget,n_child,ptbytes_name)
~$gr_active(S_missing_frame,n_child,ptbytes_name)
pdestructionframe_wrong = pdestructionframe[.FUNCTION = ppropertyget.SITE]
S_wrong_function = S_exit[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe_wrong) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*][.DESTRUCTION.FRAMES = [pdestructionframe_wrong]]
$property_get_recursive_exit(S_wrong_function,S_wrong_function.TODO,ppropertyget) = eps
pdestructionrelease_wrong = pdestructionrelease[.USER = ~pdestructionrelease.USER]
S_wrong_release = S_exit[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_wrong) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*]
$property_get_recursive_exit(S_wrong_release,S_wrong_release.TODO,ppropertyget) = eps
S_wrong_probe = S_probe_saved[.TODO = (DESTRUCTOR_RESULT pdestructorcall_probe[.RELEASE = eps]) :: (DESTRUCTOR_RELEASE pdestructionrelease_after) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*]
$property_get_recursive_exit(S_wrong_probe,S_wrong_probe.TODO,ppropertyget) = eps
''')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', action='append', choices=('populate','sole','throwing','cleanup'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_get_recursion_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_observations_accepted']
    assert [case['id'] for case in data['cases']] == ['populate','sole','throwing','cleanup']
    selected = data['cases']
    if args.case:
        assert len(args.case) == len(set(args.case))
        selected = [case for case in selected if case['id'] in args.case]
        assert len(selected) == len(args.case)
    php, adapter, bridge, worker, runner, compiler = (ROOT / name for name in [
        '.tools/php/bin/php','_build/default/adapter/main.exe','.tools/php-file.so',
        'frontend/worker.php','tests/semantics/_build/default/numeric_runner.exe','.tools/spectec/bin/p4spectec'])
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    assert sha(compiler) == '26d77fb9bfae2b2868e137a94051f55f9b607660c340e9b22ae8300fb0d8ce88'
    assert sha(runner) == 'b57a2ed7daf86de23993a29d079083377cfef6da133739a164dbfdb9f11fd7a0'
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_bytes())]
    watched = [Path(__file__),Path(recorder.__file__),catalogue,profile_file,php,adapter,bridge,worker,runner,compiler,
        manifest,*modules,*(HERE / case['source_file'] for case in data['cases']),
        *(ROOT / name for name in ['spec/schema.json','spec/php.watsup','spec/nodes.json','frontend/target.php',
            'frontend/wire.php','frontend/wire.py','tests/semantics/recorded_worker.py','tests/semantics/static_types.py'])]
    revision,status = git('rev-parse','HEAD'),git('status','--short')
    assert revision == args.revision and not status,(revision,status)
    before = {str(path):sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='magic-get-recursion-protocol-',dir=ROOT / '.tools'))
    print(out,flush=True)
    report = {'revision':revision,'inputs':before,'profile':profile,'module_count':len(modules),
        'mode':'SL','cache':False,'det':True,'records':[],'fixtures':[],'selection':[case['id'] for case in selected],
        'application_invocations':0,'application_evaluations':0,'source_agreements':0,
        'premises':0,'reached_premises':0,'derived_premises':0,'cap_seconds':90,
        'environment':{'LC_ALL':'C','TZ':'UTC','PHP_SPEC_SCRIPT_ENCODING':'absent','jobs':1},'passed':False}
    try:
        flags = [part for key,value in profile.items() for part in ('-d',key + '=' + value)]
        for case in selected:
            name = case['id']
            source = HERE / case['source_file']
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256']
            native_stderr = base64.b64decode(case['stderr_template_base64']).replace(b'{FILE}',case['original_source'].encode())
            native_tuple = base64.b64decode(case['stdout_base64']) + b'\0' + native_stderr + b'\0' + str(case['exit_status']).encode()
            assert hashlib.sha256(native_tuple).hexdigest() == case['native_raw_sha256']
            directory = out / name
            directory.mkdir()
            frontend = Worker([str(php),'-n',*flags,'-d','extension=' + str(bridge),str(worker)],directory / 'frontend')
            adapter_worker = None
            try:
                parsed = frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted'],parsed
                adapter_worker = Worker([str(adapter),str(ROOT)],directory / 'adapter')
                checked = adapter_worker.request({'op':'check','ast':parsed['ast'],'fixture':True})
                assert checked['ok'] and checked['ast'] == parsed['ast']
            finally:
                if adapter_worker:
                    adapter_worker.close()
                frontend.close()
            output = base64.b64decode(case['stdout_base64']).decode()
            prefix = {'populate':'P:','sole':'S:','throwing':'X:','cleanup':'L:'}[name]
            before_warning = prefix + ('G|g|V|' if name == 'cleanup' else 'G|')
            after_warning = before_warning + 'W|w|'
            before_result = after_warning + ('g|' if name == 'populate' else 'n|g|' if name == 'sole' else 'n|v|')
            setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                'ptbytes_prefix = $ptascii(' + json.dumps(prefix) + ')',
                'ptbytes_before_warning = $ptascii(' + json.dumps(before_warning) + ')',
                'ptbytes_after_warning = $ptascii(' + json.dumps(after_warning) + ')',
                'ptbytes_before_result = $ptascii(' + json.dumps(before_result) + ')',
                'ptbytes_final = $ptascii(' + json.dumps(output) + ')',
                'n_warning_owners = ' + ('3' if name == 'cleanup' else '2'),
                'n_after_warning_owners = ' + ('3' if name == 'cleanup' else '1' if name in ('sole','throwing') else '2'),
                'n_at_result_owners = ' + ('1' if name in ('sole','throwing') else '2'),
                'n_external_owners = ' + ('0' if name in ('sole','throwing') else '1'),
                'pvalue_result = ' + ('PNULL' if name == 'populate' else 'PINT 7')]
            reached = setup + reach('S_front','S_initial','GR_OUTER') + FRONT
            if name == 'throwing':
                reached += ['$lookup(S_front.ENV,$ptascii("error")) = (n_error_cell)',
                    'S_front.STORE[n_error_cell] = DEFINED (POBJECT n_error)',
                    '$lookup(S_front.ENV,$ptascii("result")) = (n_result_cell)',
                    'S_front.STORE[n_result_cell] = DEFINED (PINT 42)']
            else:
                reached += ['$lookup(S_front.ENV,$ptascii(' + json.dumps('first' if name == 'populate' else 'result') + ')) = eps']
            if name == 'sole':
                reached += ['$lookup(S_front.ENV,$ptascii("live")) = (n_live_cell)',
                    'S_front.STORE[n_live_cell] = DEFINED (PINT 7)']
            reached += reach('S_get','S_call','GR_ENTER ppropertyget.METHOD') + ENTER
            if name == 'cleanup':
                reached += reach('S_exit','S_get','GR_EXIT')
                reached += reach('S_inner','S_exit','GR_RECURSE') + INNER + CLEANUP
            else:
                reached += reach('S_inner','S_get','GR_RECURSE') + INNER + [
                    'S_inner.CURRENT = (pcallcontext_get)', 'S_inner.FRAMES = [pframe_get]',
                    '$property_get_recursive_frame(S_inner,pcallcontext_get,pframe_get,n_child,ptbytes_name)']
            reached += reach('S_invoke','S_invoke_pending','GR_INVOKE') + INVOKE
            if name == 'throwing':
                reached += reach('S_warning_throw','S_invoke','GR_WARNING_THROW') + [
                    'S_warning_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_inner_tail*',
                    'perrorcall_throw.RESUME = PROPERTY_UNDEFINED_RESULT ppropertywarning',
                    'perrorcall_throw.TARGET =/= eps',
                    '$error_entered_call_valid(S_warning_throw,perrorcall_throw)',
                    '$property_get_recursive_history(S_warning_throw,ppropertywarning)',
                    'S_warning_throw.STORE[n_child_cell] = DEFINED PNULL',
                    '$heap_owners($heap_graph(S_warning_throw),HOBJECT n_child) = 1',
                    '$gr_output(S_warning_throw.EVENTS) = ptbytes_after_warning',
                    '$gr_active(S_warning_throw,n_child,ptbytes_name)', '$gr_guard(S_warning_throw)']
                reached += reach('S_get_throw','S_warning_throw','GR_GET_THROW') + [
                    'S_get_throw.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*',
                    '$heap_owners($heap_graph(S_get_throw),HOBJECT n_child) = 1',
                    r'~$gr_active(S_get_throw,n_child,ptbytes_name) /\ $gr_guard(S_get_throw)',
                    'PhpStep: S_get_throw ~> S_throw_raw',
                    'S_throw_raw.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_COPY ppropertyget (KNOWN PNULL)) :: ptask_tail*',
                    'S_throw_releasing = $gr_after(S_get_throw,S_throw_raw)']
                reached += reach('S_child','S_throw_releasing','GR_DTOR n_child') + CHILD + [
                    'pdestructionoperation_child.SOURCE = THROW_SEARCH n_error',
                    'pdestructionoperation_child.PENDING = (n_error)',
                    'pdestructionoperation_child.VALUE = KNOWN PNULL',
                    'S_child.STORE[n_result_cell] = DEFINED (PINT 42)',
                    '$gr_output(S_child.EVENTS) = ptbytes_after_warning']
                reached += reach('S_catch','S_child','GR_CATCH') + [
                    'S_catch.TODO = (CATCH_BIND porigin_catch n_catch n_error) :: ptask_catch_tail*',
                    'S_catch.STORE[n_result_cell] = DEFINED (PINT 42)',
                    '~((HOBJECT n_child) <- S_catch.ALLOCATIONS)',
                    '$gr_output(S_catch.EVENTS) = $ptascii("X:G|W|w|D|")',
                    '$gr_guard(S_catch)', 'S_end = S_catch']
            else:
                reached += reach('S_handler','S_invoke','GR_HANDLER') + HANDLER
                if name == 'sole':
                    reached += ['S_handler.STORE[n_child_cell] = DEFINED PNULL',
                        'S_handler_main = $constant_frame_scope(S_handler,pframe_get,eps)',
                        '$lookup(S_handler_main.ENV,$ptascii("child")) = (n_child_cell)',
                        '~$property_get_capture(S_handler_main,ppropertyget)']
                reached += reach('S_resume','S_handler','GR_WARNING_RESULT') + RESUME
                reached += reach('S_result','S_read','GR_GET_RESULT') + RESULT
                if name == 'sole':
                    reached += reach('S_child','S_copy_pending','GR_DTOR n_child') + CHILD + [
                        'pdestructionoperation_child.SOURCE = PROPERTY_GET_RESULT ppropertyget',
                        'pdestructionoperation_child.PENDING = eps',
                        'pdestructionoperation_child.VALUE = KNOWN PNULL',
                        '(PROPERTY_GET_COPY ppropertyget (KNOWN (PINT 7))) <- pframe_child.TODO',
                        'S_child.STORE[n_live_cell] = DEFINED (PINT 7)',
                        '$gr_output(S_child.EVENTS) = ptbytes_before_result']
                    reached += reach('S_copy','S_child','GR_GET_COPY') + COPY + [
                        'S_copy.STORE[n_live_cell] = DEFINED (PINT 99)',
                        '~((HOBJECT n_child) <- S_copy.ALLOCATIONS)',
                        '$lookup(S_copy.ENV,$ptascii("result")) = eps']
                    reached += reach('S_delivered','S_copied','GR_OUTPUT $ptascii("S:G|W|w|n|g|D|A|7/99|")') + [
                        '$lookup(S_delivered.ENV,$ptascii("result")) = (n_result_cell)',
                        'S_delivered.STORE[n_result_cell] = DEFINED (PINT 7)',
                        'S_end = S_delivered']
                else:
                    reached += reach('S_copy','S_copy_pending','GR_GET_COPY') + COPY
                    reached += reach('S_again','S_copied','GR_OUTER') + RESET
                    destination = 'first' if name == 'populate' else 'result'
                    reached += ['$lookup(S_again.ENV,$ptascii(' + json.dumps(destination) + ')) = (n_result_cell)',
                        'S_again.STORE[n_result_cell] = DEFINED pvalue_result', 'S_end = S_again']
            reached += FINISH + [f'z_inner = {case["recursive_line"]}']
            derived = list(DERIVED)
            if name == 'populate':
                derived += POPULATED
            if name == 'cleanup':
                derived += CLEANUP_DERIVED
            content = PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
            for condition in reached + derived:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $main() = false -- otherwise\n'
            fixture = directory / 'getter-recursion.watsup'
            fixture.write_text(content)
            row = {'id':name,'path':str(fixture),'sha256':sha(fixture),'reached_premises':len(reached),
                'derived_premises':len(derived),'premises':len(reached) + len(derived)}
            report['fixtures'].append(row)
            for key in ('premises','reached_premises','derived_premises'):
                report[key] += row[key]
        report.update(prepared=True,passed=True)
        if not args.prepare_only:
            for fixture in report['fixtures']:
                directory = Path(fixture['path']).parent
                process = recorder.recorded([str(compiler),'algo',*map(str,modules),fixture['path']],directory / 'compiler',90)
                passed = process['exit'] == 0 and not process['timeout'] and not process['interruption'] and not process['group_after'] and not (directory / 'compiler.stderr').read_bytes() and b'\ndef $main : bool =\n' in (directory / 'compiler.stdout').read_bytes()
                report['records'].append({'id':fixture['id'] + '-algorithmic-compilation','process':process,'passed':passed,'application_evaluations':0})
                report['passed'] = passed
                assert passed
                report['application_invocations'] += 1
                process = recorder.recorded([str(runner),'--sl',*map(str,modules),fixture['path']],directory / 'state',90)
                output = (directory / 'state.stdout').read_bytes()
                evaluated = process['exit'] == 0 and output in (b'true\n',b'false\n')
                report['application_evaluations'] += int(evaluated)
                passed = evaluated and not process['timeout'] and not process['interruption'] and not process['group_after'] and not (directory / 'state.stderr').read_bytes() and output == b'true\n'
                report['records'].append({'id':fixture['id'] + '-strict-SL-application','process':process,'passed':passed})
                report['passed'] = passed
                assert passed
    finally:
        report.update(inputs_stable=before == {str(path):sha(path) for path in watched},
            fixtures_stable=all(row['sha256'] == sha(Path(row['path'])) for row in report['fixtures']),
            head_stable=revision == git('rev-parse','HEAD'),status_stable=status == git('status','--short'))
        if not args.prepare_only:
            report['passed'] = (report['passed'] and len(report['records']) == 2 * len(selected)
                and all(row['passed'] for row in report['records'])
                and report['application_invocations'] == len(selected)
                and report['application_evaluations'] == len(selected))
        report['passed'] = report['passed'] and all(report[key] for key in ('inputs_stable','fixtures_stable','head_stable','status_stable'))
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report,indent=2) + '\n')
        print(json.dumps({key:report[key] for key in ('passed','application_evaluations','premises','reached_premises','derived_premises','inputs_stable','head_stable','status_stable')}),flush=True)
    assert report['passed']

if __name__ == '__main__':
    main()
