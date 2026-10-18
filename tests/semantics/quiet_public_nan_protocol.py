"""Check borrowed public NaN property truth after live warning-handler writes."""
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
syntax ppublicnanstage = PN_PREP | PN_REBOUND ptbytes | PN_RETURN | PN_CLEAN | PN_RESUME | PN_THROW | PN_CATCH | PN_DTOR nat
dec $pn_output(pevent*) : ptbytes
def $pn_output(eps) = eps
def $pn_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $pn_output(pevent*)
def $pn_output((DIAGNOSTIC text ptbytes z) :: pevent*) = $pn_output(pevent*)
dec $pn_stage(pstate,ppublicnanstage) : bool
def $pn_stage(S,PN_PREP) = true
  -- if S.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) z) :: (ORIGIN_RETURN (porigin)) :: (ISSET_RESULT true z) :: ptask*
  -- if $base64(text_name) = $ptascii("value")
def $pn_stage(S,PN_REBOUND ptbytes) = true
  -- if S.CURRENT =/= eps
  -- if $pn_output(S.EVENTS) = ptbytes
def $pn_stage(S,PN_RETURN) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask*
def $pn_stage(S,PN_CLEAN) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (ERROR_HANDLER_CLEAN perrorcall) :: ptask*
def $pn_stage(S,PN_RESUME) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_PUBLIC_NAN ppropertypublicnan) :: ptask*
def $pn_stage(S,PN_THROW) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask*
def $pn_stage(S,PN_CATCH) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask*
def $pn_stage(S,PN_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $pn_stage(S,ppublicnanstage) = false -- otherwise
dec $pn_seek(pstate,ppublicnanstage,nat) : pstate
def $pn_seek(S,ppublicnanstage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $pn_stage(S,ppublicnanstage) \/ n = 0
def $pn_seek(S,ppublicnanstage,n) = $pn_seek($drive_steps(S[.COMPLETION = NORMAL],1),ppublicnanstage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$pn_stage(S,ppublicnanstage) /\ $(n > 0)
def $pn_seek(S,ppublicnanstage,n) = $pn_seek($drive_steps(S,1),ppublicnanstage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $pn_seek(S,ppublicnanstage,n) = S -- otherwise
dec $pn_after(pstate,pstate) : pstate
def $pn_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $pn_guard(pstate) : bool
def $pn_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''

COMMON = r'''
$pn_stage(S,PN_PREP)
S.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) z_empty) :: (ORIGIN_RETURN (porigin_site)) :: (ISSET_RESULT true z_empty) :: ptask_tail*
S.CURRENT = eps /\ S.FRAMES = eps /\ S.ORIGIN = (porigin_site)
S.BASE = BASE_VALUE (KNOWN PNULL) /\ $operand_nodes(S.RESULT) = eps /\ $machine_base_roots(S) = eps
S_read = $quiet_operand(S,S.RESULT)
S_read.COMPLETION = NORMAL
S_read.RESULT = KNOWN (POBJECT n_child)
$property_public_nan_plan(S) = (ppropertypublicnan)
ptask_return* = (ORIGIN_RETURN (porigin_site)) :: ptask_tail*
ppropertypublicnan.OBJECT = n_child /\ ppropertypublicnan.FLOAT = 9221120237041090560
ppropertypublicnan.READ.SITE = porigin_site /\ ppropertypublicnan.READ.NAME = $ptascii("value") /\ ppropertypublicnan.READ.LINE = z_empty
ppropertypublicnan.OWNER = 0 /\ ppropertypublicnan.CALLER = eps /\ ppropertypublicnan.TAIL = ptask_return*
$property_public_nan_source(S,ppropertypublicnan.READ) /\ $property_public_nan_descriptor(S,ppropertypublicnan)
$property_public_nan_slot(S,ppropertypublicnan) = (9221120237041090560)
$property_public_nan_prepare(S) /\ ~$property_empty_get_skip(S) /\ ~$property_empty_prepare(S)
$heap_owners($heap_graph(S),HOBJECT n_child) = 2 /\ $pn_guard(S)
PhpStep: S ~> S_warning_raw
S_warning = $pn_after(S,S_warning_raw)
S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_return*
perrorcall.RESUME = PROPERTY_PUBLIC_NAN ppropertypublicnan
perrorcall.SITE = porigin_site /\ perrorcall.LINE = z_empty /\ perrorcall.LEVEL = 2
perrorcall.MESSAGE = $ptascii("unexpected NAN value was coerced to bool") /\ perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE z_empty
S_warning.RESULT = KNOWN PNULL /\ S_warning.BASE = BASE_VALUE (KNOWN PNULL) /\ S_warning.EVENTS = S.EVENTS
$property_public_nan_valid(S_warning,ppropertypublicnan) /\ $error_call_valid(S_warning,perrorcall)
$task_nodes(perrorcall.RESUME) = eps /\ $task_nodes(ERROR_HANDLER_INVOKE perrorcall) = eps
$heap_owners($heap_graph(S_warning),HOBJECT n_child) = 2 /\ S_warning.GC = S.GC /\ S_warning.DESTRUCTION = S.DESTRUCTION
PhpStep: S_warning ~> S_entered_raw
S_entered = $pn_after(S_warning,S_entered_raw)
S_entered.CURRENT = (pcallcontext_handler)
S_entered.FRAMES = [pframe_handler]
pframe_handler.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_return*
perrorcall_entered = perrorcall[.TARGET = (pcallcontext_handler.TARGET)]
pframe_handler.CONTEXT = eps /\ pframe_handler.ORIGIN = (porigin_site)
$pn_guard(S_entered)
S_rebound_found = $pn_seek(S_entered,PN_REBOUND ptbytes_handler,1000)
S_rebound_found.COMPLETION = NORMAL \/ S_rebound_found.COMPLETION = BUDGET
S_rebound = S_rebound_found[.COMPLETION = NORMAL]
S_rebound.CURRENT = (pcallcontext_handler) /\ S_rebound.FRAMES = [pframe_handler]
$pn_output(S_rebound.EVENTS) = ptbytes_handler
S_caller = $constant_frame_scope(S_rebound,pframe_handler,eps)
$lookup(S_caller.ENV,$ptascii("child")) = (n_child_cell)
S_caller.STORE[n_child_cell] = DEFINED PNULL
$lookup(S_caller.ENV,$ptascii("saved")) = (n_saved_cell)
S_caller.STORE[n_saved_cell] = DEFINED (POBJECT n_child)
$property_public_nan_valid(S_caller,ppropertypublicnan) /\ $error_call_valid(S_caller,perrorcall_entered)
S_null = $quiet_operand(S_caller,VARIABLE $ptascii("child") z_empty)
S_null.COMPLETION = NORMAL /\ S_null.RESULT = KNOWN PNULL
$property_public_nan_slot(S_caller,ppropertypublicnan) = (n_current_float)
$heap_owners($heap_graph(S_rebound),HOBJECT n_child) = 1 /\ $machine_base_roots(S_caller) = eps
~$property_empty_guard(S_rebound,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_rebound,n_child,$ptascii("value"))
~$property_isset_guard(S_rebound,S_rebound.CURRENT,S_rebound.FRAMES,n_child,$ptascii("value")) /\ $pn_guard(S_rebound)
'''.strip().splitlines()

RETURN = r'''
S_return_found = $pn_seek(S_rebound,PN_RETURN,1000)
S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET
S_return = S_return_found[.COMPLETION = NORMAL]
S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_return*
S_return.RESULT = KNOWN (PBOOL b_callback) /\ S_return.EVENTS = S_rebound.EVENTS
$property_public_nan_valid(S_return,ppropertypublicnan) /\ $call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)
S_clean_found = $pn_seek(S_return,PN_CLEAN,1000)
S_clean_found.COMPLETION = NORMAL \/ S_clean_found.COMPLETION = BUDGET
S_clean = S_clean_found[.COMPLETION = NORMAL]
S_clean.TODO = (ERROR_HANDLER_CLEAN perrorcall_entered) :: ptask_return*
$error_cleanup_valid(S_clean,perrorcall_entered) /\ $property_public_nan_valid(S_clean,ppropertypublicnan)
S_clean.EVENTS = S_return.EVENTS ++ pevent_warning*
S_resume_found = $pn_seek(S_clean,PN_RESUME,1000)
S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET
S_resume = S_resume_found[.COMPLETION = NORMAL]
S_resume.TODO = (PROPERTY_PUBLIC_NAN ppropertypublicnan) :: ptask_return*
S_resume.RESULT = KNOWN PNULL /\ S_resume.ERRORHANDLER = S_warning.ERRORHANDLER
$property_public_nan_valid(S_resume,ppropertypublicnan) /\ $property_public_nan_slot(S_resume,ppropertypublicnan) = (n_current_float)
$task_nodes(PROPERTY_PUBLIC_NAN ppropertypublicnan) = eps /\ $machine_base_roots(S_resume) = eps
$heap_owners($heap_graph(S_resume),HOBJECT n_child) = 1 /\ S_resume.EVENTS = S_clean.EVENTS
PhpStep: S_resume ~> S_done_raw
S_done_raw.RESULT = KNOWN (PBOOL b_empty) /\ S_done_raw.TODO = ptask_return* /\ S_done_raw.EVENTS = S_resume.EVENTS
S_done_raw.STORE = S_resume.STORE /\ S_done_raw.OBJECTPROPS = S_resume.OBJECTPROPS
S_after = $pn_after(S_resume,S_done_raw)
S_after.GC = S_resume.GC /\ S_after.DESTRUCTION = S_resume.DESTRUCTION /\ $heap_owners($heap_graph(S_after),HOBJECT n_child) = 1
$property_public_nan_slot(S_after,ppropertypublicnan) = (n_current_float) /\ $pn_guard(S_after)
'''.strip().splitlines()

THROW = r'''
S_throw_found = $pn_seek(S_rebound,PN_THROW,1000)
S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET
S_throw = S_throw_found[.COMPLETION = NORMAL]
S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_return*
S_throw.CURRENT = eps /\ S_throw.FRAMES = eps /\ $pn_output(S_throw.EVENTS) = ptbytes_handler
$property_public_nan_valid(S_throw,ppropertypublicnan) /\ $error_entered_call_valid(S_throw,perrorcall_entered)
$throwable_live(S_throw,n_error) /\ $heap_owners($heap_graph(S_throw),HOBJECT n_child) = 1
PhpStep: S_throw ~> S_discard_raw
S_discard_raw.TODO = (THROW_SEARCH n_error) :: ptask_return*
S_discard_raw.COMPLETION = NORMAL /\ S_discard_raw.RESULT = KNOWN PNULL /\ S_discard_raw.BASE = BASE_VALUE (KNOWN PNULL)
S_discard_raw.EVENTS = S_throw.EVENTS /\ S_discard_raw.STORE = S_throw.STORE /\ S_discard_raw.OBJECTPROPS = S_throw.OBJECTPROPS
S_discard_raw.ERRORHANDLER = S_warning.ERRORHANDLER /\ $throwable_live(S_discard_raw,n_error)
S_discard = $pn_after(S_throw,S_discard_raw)
$heap_owners($heap_graph(S_discard),HOBJECT n_child) = 1 /\ S_discard.GC = S_throw.GC
S_discard.DESTRUCTION = S_throw.DESTRUCTION /\ $pn_guard(S_discard)
S_catch_found = $pn_seek(S_discard,PN_CATCH,1000)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_try n_catch n_error) :: ptask_catch*
$throwable_live(S_catch,n_error) /\ $pn_output(S_catch.EVENTS) = ptbytes_handler
PhpStep: S_catch ~> S_catch_raw
$lookup(S_catch_raw.ENV,$ptascii("caught")) = (n_caught_cell)
S_catch_raw.STORE[n_caught_cell] = DEFINED (POBJECT n_error)
S_after = $pn_after(S_catch,S_catch_raw)
S_after.COMPLETION = NORMAL /\ $throwable_live(S_after,n_error) /\ $heap_owners($heap_graph(S_after),HOBJECT n_child) = 1
$property_public_nan_slot(S_after,ppropertypublicnan) = (n_current_float) /\ $pn_guard(S_after)
'''.strip().splitlines()

FINISH = r'''
S_dtor_found = $pn_seek(S_after,PN_DTOR n_child,1000)
S_dtor_found.COMPLETION = NORMAL \/ S_dtor_found.COMPLETION = BUDGET
S_dtor = S_dtor_found[.COMPLETION = NORMAL]
$pn_stage(S_dtor,PN_DTOR n_child) /\ $pn_output(S_dtor.EVENTS) = ptbytes_before_dtor
~$property_empty_guard(S_dtor,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_dtor,n_child,$ptascii("value"))
$pn_guard(S_dtor)
S_final = $drive_steps(S_dtor,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$pn_output(S_final.EVENTS) = ptbytes_final /\ ~(HOBJECT n_child <- S_final.ALLOCATIONS)
$pn_guard(S_final)
S_budget = $drive_steps(S_rebound,0)
S_budget.COMPLETION = BUDGET /\ S_budget.TODO = S_rebound.TODO /\ S_budget.EVENTS = S_rebound.EVENTS
$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final
'''.strip().splitlines()

DERIVED = r'''
S_missing = S[.SOURCES = eps]
$property_public_nan_plan(S_missing) = eps /\ ~$property_public_nan_prepare(S_missing)
S_false = S[.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) z_empty) :: (ORIGIN_RETURN (porigin_site)) :: (ISSET_RESULT false z_empty) :: ptask_tail*]
$property_public_nan_plan(S_false) = eps
S_ancestor = S[.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) z_empty) :: (ORIGIN_RETURN (porigin_site)) :: (DIM_FETCH z_empty) :: ptask_tail*]
$property_public_nan_plan(S_ancestor) = eps
S_owning = S[.RESULT = KNOWN (POBJECT n_child)]
$operand_nodes(S_owning.RESULT) = [HOBJECT n_child] /\ $property_public_nan_plan(S_owning) = eps
S_other = $write_name($write_name(S,$ptascii("other"),POBJECT n_child),$ptascii("child"),PNULL)[.RESULT = VARIABLE $ptascii("other") z_empty]
S_other_read = $quiet_operand(S_other,S_other.RESULT)
S_other_read.COMPLETION = NORMAL /\ S_other_read.RESULT = KNOWN (POBJECT n_child) /\ $property_public_nan_plan(S_other) = eps
ppropertypublicnan_badowner = ppropertypublicnan[.OWNER = 1]
S_badowner = S_resume[.TODO = (PROPERTY_PUBLIC_NAN ppropertypublicnan_badowner) :: ptask_return*]
~$property_public_nan_valid(S_badowner,ppropertypublicnan_badowner) /\ ~$call_task_valid(S_badowner,PROPERTY_PUBLIC_NAN ppropertypublicnan_badowner)
PhpStep: S_badowner ~> S_badowner_done
S_badowner_done.COMPLETION = UNSUPPORTED "public empty NaN property continuation" /\ S_badowner_done.EVENTS = S_resume.EVENTS
ppropertypublicnan_badcaller = ppropertypublicnan[.CALLER = (pcallcontext_handler)]
S_badcaller = S_resume[.TODO = (PROPERTY_PUBLIC_NAN ppropertypublicnan_badcaller) :: ptask_return*]
~$property_public_nan_valid(S_badcaller,ppropertypublicnan_badcaller)
ppropertypublicnan_badfloat = ppropertypublicnan[.FLOAT = 0]
S_badfloat = S_resume[.TODO = (PROPERTY_PUBLIC_NAN ppropertypublicnan_badfloat) :: ptask_return*]
~$property_public_nan_valid(S_badfloat,ppropertypublicnan_badfloat)
ppropertypublicnan_badbits = ppropertypublicnan[.FLOAT = 18446744073709551616]
S_badbits = S_resume[.TODO = (PROPERTY_PUBLIC_NAN ppropertypublicnan_badbits) :: ptask_return*]
~$property_public_nan_valid(S_badbits,ppropertypublicnan_badbits)
ppropertypublicnan_badtail = ppropertypublicnan[.TAIL = eps]
S_badtail = S_resume[.TODO = (PROPERTY_PUBLIC_NAN ppropertypublicnan_badtail) :: ptask_return*]
~$property_public_nan_valid(S_badtail,ppropertypublicnan_badtail)
pnameread_original = ppropertypublicnan.READ
pnameread_badline = pnameread_original[.LINE = $(z_empty + 1)]
ppropertypublicnan_badline = ppropertypublicnan[.READ = pnameread_badline]
S_badline = S_resume[.TODO = (PROPERTY_PUBLIC_NAN ppropertypublicnan_badline) :: ptask_return*]
~$property_public_nan_valid(S_badline,ppropertypublicnan_badline)
ppropertypublicnan_badproperty = ppropertypublicnan[.PROPERTY = porigin_site]
S_badproperty = S_resume[.TODO = (PROPERTY_PUBLIC_NAN ppropertypublicnan_badproperty) :: ptask_return*]
~$property_public_nan_valid(S_badproperty,ppropertypublicnan_badproperty)
$objectprops_at(S_resume.OBJECTPROPS,n_child) = (ppropertyslot_all*)
S_unset = S_resume[.OBJECTPROPS = $objectprops_set(S_resume.OBJECTPROPS,n_child,$property_slot_set(ppropertyslot_all*,$ptascii("value"),PROP_UNSET))]
$property_public_nan_valid(S_unset,ppropertypublicnan) /\ $property_public_nan_slot(S_unset,ppropertypublicnan) = eps
PhpStep: S_unset ~> S_unset_done
S_unset_done.COMPLETION = UNSUPPORTED "public empty NaN property continuation" /\ S_unset_done.EVENTS = S_resume.EVENTS
S_invalid = S_resume[.OBJECTPROPS = $objectprops_set(S_resume.OBJECTPROPS,n_child,$property_slot_set(ppropertyslot_all*,$ptascii("value"),PROP_VALUE (DIRECT (PFLOAT 18446744073709551616))))]
$property_public_nan_valid(S_invalid,ppropertypublicnan) /\ $property_public_nan_slot(S_invalid,ppropertypublicnan) = eps
S_nonfloat = S_resume[.OBJECTPROPS = $objectprops_set(S_resume.OBJECTPROPS,n_child,$property_slot_set(ppropertyslot_all*,$ptascii("value"),PROP_VALUE (DIRECT (PINT 1))))]
$property_public_nan_valid(S_nonfloat,ppropertypublicnan) /\ $property_public_nan_slot(S_nonfloat,ppropertypublicnan) = eps
S_retired = S_resume[.ALLOCATIONS = $call_remove_owner(S_resume.ALLOCATIONS,HOBJECT n_child)]
~$property_public_nan_valid(S_retired,ppropertypublicnan)
PhpStep: S_retired ~> S_retired_done
S_retired_done.COMPLETION = UNSUPPORTED "public empty NaN property continuation" /\ S_retired_done.EVENTS = S_resume.EVENTS
~$error_call_valid(S_warning,perrorcall[.LEVEL = 1]) /\ ~$error_call_valid(S_warning,perrorcall[.LINE = $(z_empty + 1)])
~$error_call_valid(S_warning,perrorcall[.MESSAGE = eps]) /\ ~$error_call_valid(S_warning,perrorcall[.EVENT = DIAGNOSTIC "Warning" eps z_empty])
S_default = S[.ERRORHANDLER.CALLBACK = eps]
PhpStep: S_default ~> S_default_raw
S_default_warn = $pn_after(S_default,S_default_raw)
S_default_warn.TODO = (PROPERTY_PUBLIC_NAN ppropertypublicnan) :: ptask_return*
S_default_warn.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Warning" ($ptascii("unexpected NAN value was coerced to bool")) z_empty]
$heap_owners($heap_graph(S_default_warn),HOBJECT n_child) = 2 /\ $task_nodes(PROPERTY_PUBLIC_NAN ppropertypublicnan) = eps
PhpStep: S_default_warn ~> S_default_done
S_default_done.RESULT = KNOWN (PBOOL false) /\ S_default_done.TODO = ptask_return* /\ S_default_done.EVENTS = S_default_warn.EVENTS
$heap_owners($heap_graph(S_default_done),HOBJECT n_child) = 2
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', choices=('zero', 'one-default', 'unchanged', 'throwing'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'quiet_public_nan_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = ROOT / 'tests/semantics/profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_gate_completed']
    selected = [case for case in data['cases'] if not args.case or case['id'] == args.case]
    assert selected
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
    out = Path(tempfile.mkdtemp(prefix='quiet-public-nan-protocol-', dir=ROOT / '.tools'))
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
            output = base64.b64decode(case['stdout_base64']).decode()
            warning = ('[DIAGNOSTIC "Warning" ($ptascii("unexpected NAN value was coerced to bool")) ' + str(case['empty_line']) + ']') if name == 'one-default' else 'eps'
            setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $pn_seek(S_initial,PN_PREP,1000)', r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]', 'ptbytes_handler = $ptascii(' + json.dumps(output[:8]) + ')',
                     'ptbytes_before_dtor = $ptascii(' + json.dumps(output[:output.index('D|')]) + ')',
                     'ptbytes_final = $ptascii(' + json.dumps(output) + ')',
                     'n_current_float = ' + str(case['resumed_float_bits']), 'z_empty = ' + str(case['empty_line'])]
            if name != 'throwing':
                setup += ['b_callback = ' + str(name != 'one-default').lower(), 'b_empty = ' + str(name == 'zero').lower(),
                          'pevent_warning* = ' + warning]
            reached = setup + COMMON + (THROW if name == 'throwing' else RETURN) + FINISH
            derived = DERIVED if name == 'zero' else []
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
