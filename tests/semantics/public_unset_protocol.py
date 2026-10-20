"""Check public unset phase selection, recursion guards and local cleanup."""
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
syntax ppustage = PU_LINE int | PU_PLAN | PU_RECEIVE porigin | PU_RETURN | PU_THROW | PU_INNER | PU_EXIT | PU_RESULT | PU_DISCARD | PU_DTOR nat | PU_CATCH
dec $pu_output(pevent*) : ptbytes
def $pu_output(eps) = eps
def $pu_output((OUTPUT ptbytes) :: pevent_tail*) = ptbytes ++ $pu_output(pevent_tail*)
dec $pu_stage(pstate,ppustage) : bool
def $pu_stage(S,PU_LINE z) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = UNSET_ARRAY :: ptask_tail*
  -- if $property_current_line(S) = z
def $pu_stage(S,PU_PLAN) = true
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if $property_unset_plan(S[.COMPLETION = NORMAL]) =/= eps
def $pu_stage(S,PU_RECEIVE porigin) = true
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: ptask_tail*
def $pu_stage(S,PU_RETURN) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_UNSET_TARGET ppropertyunset
  -- if S.TODO = (RETURN_UNWIND (KNOWN PNULL) porigin?) :: ptask_tail*
def $pu_stage(S,PU_THROW) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_UNSET_TARGET ppropertyunset
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_tail*
def $pu_stage(S,PU_INNER) = true
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $property_unset_public_guarded_plan(S[.COMPLETION = NORMAL]) =/= eps
def $pu_stage(S,PU_EXIT) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (PROPERTY_UNSET_RESULT ppropertyunset) :: ptask_tail*
def $pu_stage(S,PU_RESULT) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_UNSET_RESULT ppropertyunset) :: ptask_tail*
def $pu_stage(S,PU_DISCARD) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_UNSET_RESULT ppropertyunset) :: ptask_tail*
def $pu_stage(S,PU_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $pu_stage(S,PU_CATCH) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask_tail*
def $pu_stage(S,ppustage) = false -- otherwise
dec $pu_seek(pstate,ppustage,nat) : pstate
def $pu_seek(S,ppustage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $pu_stage(S,ppustage) \/ n = 0
def $pu_seek(S,ppustage,n) = $pu_seek($drive_steps(S[.COMPLETION = NORMAL],1),ppustage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$pu_stage(S,ppustage) /\ $(n > 0)
def $pu_seek(S,ppustage,n) = $pu_seek($drive_steps(S,1),ppustage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $pu_seek(S,ppustage,n) = S -- otherwise
dec $pu_after(pstate,pstate) : pstate
def $pu_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $pu_guard(pstate) : bool
def $pu_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $object_tables_valid(S) /\ $gc_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $pu_active(pstate,nat) : bool
def $pu_active(S,n) = $property_unset_guard(S,S.CURRENT,S.FRAMES,n,$ptascii("value"))
'''

def lines(text): return [line for line in text.strip().splitlines() if line]
def reach(name, previous, stage):
    return [f'{name}_found = $pu_seek({previous},{stage},2000)',
            fr'{name}_found.COMPLETION = NORMAL \/ {name}_found.COMPLETION = BUDGET',
            f'{name} = {name}_found[.COMPLETION = NORMAL]', f'$pu_stage({name},{stage})']

INITIAL = lines(r'''
$lookup(S_initial_unset.ENV,$ptascii("child")) = (n_initial_cell)
S_initial_unset.STORE[n_initial_cell] = DEFINED (POBJECT n_initial_object)
$objectprops_at(S_initial_unset.OBJECTPROPS,n_initial_object) = (ppropertyslot_initial_all*)
$property_slot_at(ppropertyslot_initial_all*,$ptascii("value")) = (ppropertyslot_initial)
ppropertyslot_initial.STATE = PROP_INITIAL
~$property_unset_needed(S_initial_unset,n_initial_object,$ptascii("value")) /\ ~$property_unset_pending(S_initial_unset)
$property_unset_plan(S_initial_unset) = eps /\ ~$pu_active(S_initial_unset,n_initial_object) /\ $pu_guard(S_initial_unset)
PhpStep: S_initial_unset ~> S_initial_raw
S_initial_raw.EVENTS = S_initial_unset.EVENTS
S_initial_deleted = $pu_after(S_initial_unset,S_initial_raw)
$objectprops_at(S_initial_deleted.OBJECTPROPS,n_initial_object) = (ppropertyslot_deleted_all*)
$property_slot_at(ppropertyslot_deleted_all*,$ptascii("value")) = (ppropertyslot_deleted)
ppropertyslot_deleted.STATE = PROP_UNSET
$pu_guard(S_initial_deleted)
''')
COMMON = lines(r'''
S_front.TODO = UNSET_ARRAY :: ptask_tail*
S_front.ORIGIN = (porigin_site)
S_front.CURRENT = eps /\ S_front.FRAMES = eps
S_front.BASE = BASE_PROPERTY_PENDING pbase_receiver (KNOWN (PSTRING ptbytes_name)) z_receiver
ptbytes_name = $ptascii("value")
$lookup(S_front.ENV,$ptascii("child")) = (n_child_cell)
S_front.STORE[n_child_cell] = DEFINED (POBJECT n_child)
$property_unset_plan(S_front) = (ppropertyunset)
ppropertyunset.SITE = porigin_site /\ ppropertyunset.OBJECT = n_child /\ ppropertyunset.NAME = ptbytes_name
$property_effective_desc(S_front,n_child,ptbytes_name) = (ppropertydesc)
ppropertydesc.VISIBILITY = PROPERTY_PUBLIC /\ ~ppropertydesc.STATIC /\ ~ppropertydesc.READONLY /\ ppropertydesc.SETVISIBILITY = eps
ppropertydesc.NAME = ptbytes_name /\ ppropertydesc.KEY = ptbytes_name
ppropertydesc.TYPE = [PTBRANCH ([PTBUILTIN "int"])]
$property_unset_public_desc(S_front,n_child,ptbytes_name,ppropertydesc)
$objectprops_at(S_front.OBJECTPROPS,n_child) = (ppropertyslot_front_all*)
$property_slot_at(ppropertyslot_front_all*,ptbytes_name) = (ppropertyslot_front)
ppropertyslot_front.STATE = PROP_UNSET
$property_unset_method(S_front,n_child) = (pmethoddesc_unset)
pmethoddesc_unset.FUNCTION = pfunction_unset
pmethoddesc_unset.FUNCTION.ORIGIN = ppropertyunset.METHOD /\ pmethoddesc_unset.OWNER =/= ppropertyunset.CLASS
$property_magic_method_source(S_front,pmethoddesc_unset,"__unset") /\ $ppmethod_unset_signature(pfunction_unset.SIGNATURE)
$property_unset_source(S_front,ppropertyunset) /\ $property_unset_valid(S_front,ppropertyunset)
$property_unset_capture_state(S_front,ppropertyunset) /\ $property_unset_capture(S_front,ppropertyunset)
$property_unset_pending(S_front) /\ $property_unset_needed(S_front,n_child,ptbytes_name)
$property_unset_public_guarded_plan(S_front) = eps
$heap_owners($heap_graph(S_front),HOBJECT n_child) = 1
$pu_output(S_front.EVENTS) = ptbytes_prefix
~$pu_active(S_front,n_child) /\ $pu_guard(S_front)
PhpStep: S_front ~> S_call_raw
S_call = $pu_after(S_front,S_call_raw)
S_call.TODO = (CALL_ARGS (PROPERTY_UNSET_TARGET ppropertyunset) eps 1 ([KNOWN (PSTRING ptbytes_name)]) (porigin_site) ppropertyunset.LINE) :: (PROPERTY_UNSET_RESULT ppropertyunset) :: ptask_tail*
$target_nodes(PROPERTY_UNSET_TARGET ppropertyunset) = eps /\ $target_instance(PROPERTY_UNSET_TARGET ppropertyunset) = eps
$task_nodes(PROPERTY_UNSET_RESULT ppropertyunset) = [HOBJECT n_child]
$property_unset_capture(S_call,ppropertyunset) /\ $property_unset_pending_call(S_call,ppropertyunset)
$heap_owners($heap_graph(S_call),HOBJECT n_child) = 2 /\ $pu_guard(S_call)
''')
RECEIVE = lines(r'''
S_receive.CURRENT = (pcallcontext_unset)
pcallcontext_unset.TARGET = PROPERTY_UNSET_TARGET ppropertyunset
pcallcontext_unset.FUNCTION = ppropertyunset.METHOD /\ pcallcontext_unset.RECEIVER = (n_child)
pcallcontext_unset.LEXICAL_CLASS = (pmethoddesc_unset.OWNER) /\ pcallcontext_unset.CALLED_CLASS = (ppropertyunset.CLASS)
S_receive.TODO = [TYPE_RECEIVE ppropertyunset.METHOD 0]
$receiving_function(S_receive,ppropertyunset.METHOD) = (pfunction_unset)
$typed_receive_valid(S_receive,ppropertyunset.METHOD,0)
$call_receiver_roots(pcallcontext_unset) = eps
$lookup(S_receive.ENV,$ptascii("name")) = (n_name_cell)
S_receive.STORE[n_name_cell] = DEFINED (PSTRING ptbytes_name)
$property_unset_entered(S_receive,S_receive.CURRENT,S_receive.FRAMES,ppropertyunset)
$heap_owners($heap_graph(S_receive),HOBJECT n_child) = 2
$pu_active(S_receive,n_child) /\ $pu_guard(S_receive)
''')
RETURN = lines(r'''
S_return.CURRENT = (pcallcontext_unset)
S_return.TODO = (RETURN_UNWIND (KNOWN PNULL) porigin_return?) :: ptask_return*
S_return.FRAMES = [pframe_unset]
S_saved = $constant_frame_view(S_return,pframe_unset,eps)
$property_unset_valid(S_saved,ppropertyunset)
$property_unset_entered(S_return,S_return.CURRENT,S_return.FRAMES,ppropertyunset)
$pu_active(S_return,n_child) /\ $pu_guard(S_return)
''')
RESULT = lines(r'''
S_result.TODO = (PROPERTY_UNSET_RESULT ppropertyunset) :: ptask_tail*
S_result.RESULT = KNOWN PNULL
$property_unset_valid(S_result,ppropertyunset)
~$pu_active(S_result,n_child) /\ $pu_guard(S_result)
PhpStep: S_result ~> S_result_raw
S_result_raw.TODO = ptask_tail*
S_result_raw.RESULT = KNOWN PNULL /\ S_result_raw.BASE = BASE_VALUE (KNOWN PNULL)
S_releasing = $pu_after(S_result,S_result_raw)
''')
INNER = lines(r'''
S_inner.TODO = UNSET_ARRAY :: ptask_inner_tail*
S_inner.ORIGIN = (porigin_inner)
$property_unset_public_guarded_plan(S_inner) = (S_inner_target)
$property_unset_plan(S_inner) = eps /\ $property_unset_pending(S_inner)
$pu_active(S_inner,n_child) /\ $pu_guard(S_inner)
PhpStep: S_inner ~> S_inner_raw
S_inner_raw.TODO = ptask_inner_tail*
S_inner_raw.RESULT = KNOWN PNULL /\ S_inner_raw.BASE = BASE_VALUE (KNOWN PNULL)
S_inner_raw.OBJECTPROPS = S_inner.OBJECTPROPS /\ S_inner_raw.STORE = S_inner.STORE /\ S_inner_raw.EVENTS = S_inner.EVENTS /\ S_inner_raw.ALLOCATIONS = S_inner.ALLOCATIONS
S_inner_done = $pu_after(S_inner,S_inner_raw)
$pu_guard(S_inner_done)
''')
RESET = lines(r'''
$property_unset_plan(S_again) = (ppropertyunset_again)
ppropertyunset_again.OBJECT = n_child /\ ppropertyunset_again.METHOD = ppropertyunset.METHOD /\ ppropertyunset_again.PROPERTY = ppropertyunset.PROPERTY
ppropertyunset_again.SITE =/= ppropertyunset.SITE
$property_unset_capture(S_again,ppropertyunset_again) /\ ~$pu_active(S_again,n_child) /\ $pu_guard(S_again)
S_end = S_again
''')
CHILD = lines(r'''
S_child.CURRENT = (pcallcontext_child)
$destructor_context_call(pcallcontext_child,S_child.CURRENT,S_child.FRAMES) = (pdestructorcall_child)
pdestructorcall_child.OPERATION = (pdestructionoperation_child)
pdestructionoperation_child.VALUE = KNOWN PNULL /\ pdestructionoperation_child.BASE = BASE_VALUE (KNOWN PNULL)
$pu_output(S_child.EVENTS) = ptbytes_before_child
~$pu_active(S_child,n_child) /\ $pu_guard(S_child)
''')
FINISH = lines(r'''
S_final = $drive_steps(S_end,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$pu_output(S_final.EVENTS) = ptbytes_final
~(HOBJECT n_child <- S_final.ALLOCATIONS) /\ $pu_guard(S_final)
S_budget = $drive_steps(S_budget_start,0)
S_budget = S_budget_start[.COMPLETION = BUDGET]
$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final
''')
INITIAL_DERIVED = lines(r'''
S_value_unset = S_return[.ORIGIN = S_inner.ORIGIN][.TODO = UNSET_ARRAY :: eps][.BASE = S_inner.BASE]
$pu_active(S_value_unset,n_child)
~$property_unset_needed(S_value_unset,n_child,ptbytes_name) /\ ~$property_unset_pending(S_value_unset)
$property_unset_public_guarded_plan(S_value_unset) = eps
PhpStep: S_value_unset ~> S_value_deleted
$objectprops_at(S_value_deleted.OBJECTPROPS,n_child) = (ppropertyslot_value_deleted_all*)
$property_slot_at(ppropertyslot_value_deleted_all*,ptbytes_name) = (ppropertyslot_value_deleted)
ppropertyslot_value_deleted.STATE = PROP_UNSET
S_value_deleted.EVENTS = S_value_unset.EVENTS /\ S_value_deleted.STORE = S_value_unset.STORE /\ S_value_deleted.ALLOCATIONS = S_value_unset.ALLOCATIONS
''')
CLEANUP_DERIVED = lines(r'''
S_missing_frame = S_exit[.DESTRUCTION.FRAMES = eps]
$property_unset_public_exit(S_missing_frame,S_missing_frame.TODO,ppropertyunset) = (pdestructionframe)
~$property_unset_public_exit_guard(S_missing_frame,PROPERTY_UNSET_RESULT ppropertyunset,n_child,ptbytes_name)
~$pu_active(S_missing_frame,n_child)
pdestructionframe_wrong = pdestructionframe[.VALUE = KNOWN (PINT 1)]
S_wrong_value = S_exit[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe_wrong) :: (PROPERTY_UNSET_RESULT ppropertyunset) :: ptask_tail*][.DESTRUCTION.FRAMES = [pdestructionframe_wrong]]
$property_unset_public_exit(S_wrong_value,S_wrong_value.TODO,ppropertyunset) = eps /\ ~$pu_active(S_wrong_value,n_child)
pdestructionrelease_wrong = pdestructionrelease[.USER = ~pdestructionrelease.USER]
S_wrong_release = S_exit[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_wrong) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (PROPERTY_UNSET_RESULT ppropertyunset) :: ptask_tail*]
$property_unset_public_exit(S_wrong_release,S_wrong_release.TODO,ppropertyunset) = eps /\ ~$pu_active(S_wrong_release,n_child)
ppropertyunset_wrong = ppropertyunset[.LINE = $(ppropertyunset.LINE + 1)]
S_wrong_source = S_exit[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (PROPERTY_UNSET_RESULT ppropertyunset_wrong) :: ptask_tail*]
~$property_unset_source(S_wrong_source,ppropertyunset_wrong)
$property_unset_public_exit(S_wrong_source,S_wrong_source.TODO,ppropertyunset_wrong) = eps /\ ~$pu_active(S_wrong_source,n_child)
''')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', action='append', choices=('initial', 'normal', 'throwing', 'cleanup'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'public_unset_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_observations_accepted']
    assert [case['id'] for case in data['cases']] == ['initial', 'normal', 'throwing', 'cleanup']
    selected = data['cases']
    if args.case:
        assert len(args.case) == len(set(args.case))
        selected = [case for case in selected if case['id'] in args.case]
        assert len(selected) == len(args.case)
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
    out = Path(tempfile.mkdtemp(prefix='public-unset-protocol-', dir=ROOT / '.tools'))
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
            before_output = {'initial':'I:B|', 'normal':'N:', 'throwing':'X:', 'cleanup':'L:'}[name]
            setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'ptbytes_prefix = $ptascii(' + json.dumps(before_output) + ')',
                     'ptbytes_final = $ptascii(' + json.dumps(output) + ')']
            reached = setup
            if name == 'initial':
                reached += reach('S_initial_unset','S_initial',f'PU_LINE {case["first_unset_line"]}') + INITIAL
                reached += ['S_budget_start = S_initial_unset']
                reached += reach('S_front','S_initial_deleted','PU_PLAN')
            else:
                reached += reach('S_front','S_initial','PU_PLAN') + ['S_budget_start = S_front']
            reached += COMMON + reach('S_receive','S_call','PU_RECEIVE ppropertyunset.METHOD') + RECEIVE
            if name == 'initial':
                reached += reach('S_inner','S_receive','PU_INNER') + INNER
                reached += ['$pu_output(S_inner.EVENTS) = $ptascii("I:B|U|")']
                reached += reach('S_return','S_inner_done','PU_RETURN') + RETURN
                reached += lines(r"""
S_return.STORE[n_child_cell] = DEFINED (POBJECT n_child)
$objectprops_at(S_return.OBJECTPROPS,n_child) = (ppropertyslot_return_all*)
$property_slot_at(ppropertyslot_return_all*,ptbytes_name) = (ppropertyslot_return)
ppropertyslot_return.STATE = PROP_VALUE (DIRECT (PINT 7))
~$property_unset_capture_state(S_saved,ppropertyunset) /\ ~$property_unset_capture(S_saved,ppropertyunset)
$heap_owners($heap_graph(S_return),HOBJECT n_child) = 2
$pu_output(S_return.EVENTS) = $ptascii("I:B|U|u|")
""")
                reached += reach('S_result','S_return','PU_RESULT') + RESULT
                reached += lines(r"""
~$property_unset_capture_state(S_result,ppropertyunset)
$heap_owners($heap_graph(S_result_raw),HOBJECT n_child) = 1
""")
                reached += reach('S_value_front','S_releasing',f'PU_LINE {case["value_unset_line"]}')
                reached += lines(r"""
$objectprops_at(S_value_front.OBJECTPROPS,n_child) = (ppropertyslot_return_all*)
~$property_unset_needed(S_value_front,n_child,ptbytes_name) /\ ~$property_unset_pending(S_value_front)
$property_unset_plan(S_value_front) = eps /\ ~$pu_active(S_value_front,n_child) /\ $pu_guard(S_value_front)
PhpStep: S_value_front ~> S_value_raw
S_value_raw.EVENTS = S_value_front.EVENTS
S_value_done = $pu_after(S_value_front,S_value_raw)
$objectprops_at(S_value_done.OBJECTPROPS,n_child) = (ppropertyslot_value_done_all*)
$property_slot_at(ppropertyslot_value_done_all*,ptbytes_name) = (ppropertyslot_value_done)
ppropertyslot_value_done.STATE = PROP_UNSET
$pu_guard(S_value_done)
""")
                reached += reach('S_again','S_value_done','PU_PLAN') + RESET
                reached += ['$pu_output(S_again.EVENTS) = $ptascii("I:B|U|u|7|C|")']
                derived = INITIAL_DERIVED
            elif name == 'normal':
                reached += reach('S_return','S_receive','PU_RETURN') + RETURN
                reached += lines(r"""
S_return.STORE[n_child_cell] = DEFINED PNULL
~$property_unset_capture(S_saved,ppropertyunset)
$heap_owners($heap_graph(S_return),HOBJECT n_child) = 1
$pu_output(S_return.EVENTS) = $ptascii("N:U|u|")
""")
                reached += reach('S_result','S_return','PU_RESULT') + RESULT
                reached += ['~$property_unset_capture(S_result,ppropertyunset)', '$heap_owners($heap_graph(S_result_raw),HOBJECT n_child) = 0', 'ptbytes_before_child = $ptascii("N:U|u|")']
                reached += reach('S_child','S_releasing','PU_DTOR n_child') + CHILD
                reached += ['pdestructionoperation_child.SOURCE = PROPERTY_UNSET_RESULT ppropertyunset', 'pdestructionoperation_child.PENDING = eps', 'S_end = S_child']
                derived = []
            elif name == 'throwing':
                reached += lines(r"""
$lookup(S_front.ENV,$ptascii("error")) = (n_error_cell)
S_front.STORE[n_error_cell] = DEFINED (POBJECT n_error)
$lookup(S_front.ENV,$ptascii("after")) = (n_after_cell)
S_front.STORE[n_after_cell] = DEFINED (PINT 42)
""")
                reached += reach('S_throw','S_receive','PU_THROW')
                reached += lines(r"""
S_throw.CURRENT = (pcallcontext_unset)
S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_throw_tail*
S_throw.STORE[n_child_cell] = DEFINED PNULL
S_throw.FRAMES = [pframe_unset]
S_throw_saved = $constant_frame_view(S_throw,pframe_unset,eps)
$property_unset_valid(S_throw_saved,ppropertyunset) /\ ~$property_unset_capture(S_throw_saved,ppropertyunset)
$heap_owners($heap_graph(S_throw),HOBJECT n_child) = 1
S_error_read = $resolve_at(S_throw,S_throw.RESULT,z_throw)
S_error_read.COMPLETION = NORMAL
S_error_read.RESULT = KNOWN (POBJECT n_error)
$pu_active(S_throw,n_child) /\ $pu_guard(S_throw)
""")
                reached += reach('S_discard','S_throw','PU_DISCARD')
                reached += lines(r"""
S_discard.TODO = (THROW_SEARCH n_error) :: (PROPERTY_UNSET_RESULT ppropertyunset) :: ptask_tail*
$property_unset_valid(S_discard,ppropertyunset) /\ ~$property_unset_capture(S_discard,ppropertyunset)
~$pu_active(S_discard,n_child) /\ $pu_guard(S_discard)
PhpStep: S_discard ~> S_discard_raw
S_discard_raw.TODO = (THROW_SEARCH n_error) :: ptask_tail*
S_discard_raw.RESULT = KNOWN PNULL /\ S_discard_raw.BASE = BASE_VALUE (KNOWN PNULL)
$heap_owners($heap_graph(S_discard_raw),HOBJECT n_child) = 0
S_throw_releasing = $pu_after(S_discard,S_discard_raw)
ptbytes_before_child = $ptascii("X:U|")
""")
                reached += reach('S_child','S_throw_releasing','PU_DTOR n_child') + CHILD
                reached += ['pdestructionoperation_child.SOURCE = THROW_SEARCH n_error', 'pdestructionoperation_child.PENDING = (n_error)', 'S_child.STORE[n_after_cell] = DEFINED (PINT 42)']
                reached += reach('S_catch','S_child','PU_CATCH')
                reached += lines(r"""
S_catch.TODO = (CATCH_BIND porigin_catch n_catch_index n_error) :: ptask_catch_tail*
S_catch.STORE[n_after_cell] = DEFINED (PINT 42)
S_catch.STORE[n_child_cell] = DEFINED PNULL
~(HOBJECT n_child <- S_catch.ALLOCATIONS)
$throwable_previous_id(S_catch,n_error) = eps
$pu_output(S_catch.EVENTS) = $ptascii("X:U|D|")
~$pu_active(S_catch,n_child) /\ $pu_guard(S_catch)
S_end = S_catch
""")
                derived = []
            else:
                reached += reach('S_return','S_receive','PU_RETURN') + RETURN
                reached += lines(r"""
$lookup(S_return.ENV,$ptascii("local")) = (n_local_cell)
S_return.STORE[n_local_cell] = DEFINED (POBJECT n_probe)
S_return.STORE[n_child_cell] = DEFINED (POBJECT n_child)
$heap_owners($heap_graph(S_return),HOBJECT n_child) = 2
$heap_owners($heap_graph(S_return),HOBJECT n_probe) = 1
$pu_output(S_return.EVENTS) = $ptascii("L:U|u|")
""")
                reached += reach('S_exit','S_return','PU_EXIT')
                reached += lines(r"""
S_exit.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (PROPERTY_UNSET_RESULT ppropertyunset) :: ptask_tail*
pdestructionframe.FUNCTION = ppropertyunset.METHOD /\ pdestructionframe.VALUE = KNOWN PNULL
pdestructionframe <- S_exit.DESTRUCTION.FRAMES
$property_unset_public_exit(S_exit,S_exit.TODO,ppropertyunset) = (pdestructionframe)
$property_unset_public_exit_guard(S_exit,PROPERTY_UNSET_RESULT ppropertyunset,n_child,ptbytes_name)
$pu_active(S_exit,n_child) /\ $pu_guard(S_exit)
""")
                reached += reach('S_probe','S_exit','PU_DTOR n_probe')
                reached += lines(r"""
S_probe.CURRENT = (pcallcontext_probe)
$destructor_context_call(pcallcontext_probe,S_probe.CURRENT,S_probe.FRAMES) = (pdestructorcall_probe)
pdestructorcall_probe.FRAME = (pdestructionframe) /\ pdestructorcall_probe.OPERATION = eps
pdestructionframe <- S_probe.DESTRUCTION.FRAMES
~$property_unset_entered(S_probe,S_probe.CURRENT,S_probe.FRAMES,ppropertyunset)
S_probe.FRAMES = [pframe_probe]
S_probe_saved = $constant_frame_view(S_probe,pframe_probe,eps)
S_probe_saved.TODO = (DESTRUCTOR_RESULT pdestructorcall_probe) :: (DESTRUCTOR_RELEASE pdestructionrelease_after) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (PROPERTY_UNSET_RESULT ppropertyunset) :: ptask_tail*
pdestructorcall_probe.RELEASE = (pdestructionrelease_before)
pdestructionrelease_before.JOBS = pdestructionjob_probe :: pdestructionjob_tail*
$destruction_job_node(pdestructionjob_probe) = (HOBJECT n_probe)
pdestructionrelease_after = pdestructionrelease_before[.JOBS = pdestructionjob_tail*]
$pu_guard(S_probe_saved)
$property_unset_public_exit(S_probe_saved,S_probe_saved.TODO,ppropertyunset) = (pdestructionframe)
$pu_active(S_probe,n_child) /\ $pu_guard(S_probe)
""")
                reached += reach('S_inner','S_probe','PU_INNER') + INNER
                reached += lines(r"""
$pu_output(S_inner.EVENTS) = $ptascii("L:U|u|V|")
~$property_unset_entered(S_inner,S_inner.CURRENT,S_inner.FRAMES,ppropertyunset)
pdestructionframe <- S_inner.DESTRUCTION.FRAMES
""")
                reached += reach('S_result','S_inner_done','PU_RESULT') + RESULT
                reached += lines(r"""
~(HOBJECT n_probe <- S_result.ALLOCATIONS)
$objectprops_at(S_result.OBJECTPROPS,n_child) = (ppropertyslot_after_probe_all*)
$property_slot_at(ppropertyslot_after_probe_all*,ptbytes_name) = (ppropertyslot_after_probe)
ppropertyslot_after_probe.STATE = PROP_UNSET
$property_unset_capture(S_result,ppropertyunset)
$heap_owners($heap_graph(S_result),HOBJECT n_child) = 2
$heap_owners($heap_graph(S_result_raw),HOBJECT n_child) = 1
$pu_output(S_result.EVENTS) = $ptascii("L:U|u|V|v|")
""")
                reached += reach('S_again','S_releasing','PU_PLAN') + RESET
                reached += ['$pu_output(S_again.EVENTS) = $ptascii("L:U|u|V|v|A|")']
                derived = CLEANUP_DERIVED
            reached += FINISH
            content = PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
            for condition in reached + derived:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $main() = false -- otherwise\n'
            fixture = directory / 'public-unset.watsup'
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
                passed = process['exit'] == 0 and not process['timeout'] and not process['interruption'] and not process['group_after'] and not (directory / 'compiler.stderr').read_bytes() and b'\ndef $main : bool =\n' in (directory / 'compiler.stdout').read_bytes()
                report['records'].append({'id': fixture['id'] + '-algorithmic-compilation', 'process': process, 'passed': passed, 'application_evaluations': 0})
                report['passed'] = passed
                assert passed
                report['application_invocations'] += 1
                process = recorder.recorded([str(runner), '--sl', *map(str, modules), fixture['path']], directory / 'state', 90)
                output = (directory / 'state.stdout').read_bytes()
                evaluated = process['exit'] == 0 and output in (b'true\n', b'false\n')
                report['application_evaluations'] += int(evaluated)
                passed = evaluated and not process['timeout'] and not process['interruption'] and not process['group_after'] and not (directory / 'state.stderr').read_bytes() and output == b'true\n'
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

