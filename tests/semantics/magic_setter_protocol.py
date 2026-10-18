"""Check inherited magic setter ownership and post-release scalar RHS delivery."""
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
syntax pmagicsetstage = MS_PLAN | MS_RECEIVE porigin | MS_RETURN | MS_DELIVERY | MS_OUTPUT ptbytes | MS_MAIN ptbytes | MS_RAISED | MS_THROW | MS_DTOR nat | MS_CATCH
dec $ms_output(pevent*) : ptbytes
def $ms_output(eps) = eps
def $ms_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $ms_output(pevent*)
dec $ms_stage(pstate,pmagicsetstage) : bool
def $ms_stage(S,MS_PLAN) = true
  -- if S.CURRENT = eps
  -- if $property_magic_set_plan(S) =/= eps
def $ms_stage(S,MS_RECEIVE porigin) = true
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: ptask*
def $ms_stage(S,MS_RETURN) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_MAGIC_SET_RESULT ppropertymagicset) :: ptask*
def $ms_stage(S,MS_DELIVERY) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_MAGIC_SET_DELIVERY ppropertymagicset) :: ptask*
def $ms_stage(S,MS_OUTPUT ptbytes) = true
  -- if S.CURRENT =/= eps
  -- if $ms_output(S.EVENTS) = ptbytes
def $ms_stage(S,MS_MAIN ptbytes) = true
  -- if S.CURRENT = eps
  -- if $ms_output(S.EVENTS) = ptbytes
def $ms_stage(S,MS_RAISED) = true
  -- if S.CURRENT =/= eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
def $ms_stage(S,MS_THROW) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: (PROPERTY_MAGIC_SET_RESULT ppropertymagicset) :: ptask*
def $ms_stage(S,MS_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $ms_stage(S,MS_CATCH) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask*
def $ms_stage(S,pmagicsetstage) = false -- otherwise
dec $ms_seek(pstate,pmagicsetstage,nat) : pstate
def $ms_seek(S,pmagicsetstage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $ms_stage(S,pmagicsetstage) \/ n = 0
def $ms_seek(S,pmagicsetstage,n) = $ms_seek($drive_steps(S[.COMPLETION = NORMAL],1),pmagicsetstage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$ms_stage(S,pmagicsetstage) /\ $(n > 0)
def $ms_seek(S,pmagicsetstage,n) = $ms_seek($drive_steps(S,1),pmagicsetstage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $ms_seek(S,pmagicsetstage,n) = S -- otherwise
dec $ms_after(pstate,pstate) : pstate
def $ms_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $ms_guard(pstate) : bool
def $ms_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $gc_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''

COMMON = r'''
$ms_stage(S,MS_PLAN)
$property_magic_set_plan(S) = (ppropertymagicset)
S.TODO = (ASSIGN_ARRAY (BASE_PROPERTY_PENDING pbase poperand_name z_receiver) z false) :: ptask_tail*
ppropertymagicset.TAIL = ptask_tail* /\ ppropertymagicset.INPUT = 7 /\ ppropertymagicset.CALLER = eps /\ ppropertymagicset.OWNER = 0
n_child = ppropertymagicset.OBJECT
$lookup(S.ENV,$ptascii("child")) = (n_child_cell)
$lookup(S.ENV,$ptascii("rhs")) = (n_rhs_cell)
$lookup(S.ENV,$ptascii("result")) = (n_result_cell)
S.STORE[n_child_cell] = DEFINED (POBJECT n_child)
S.STORE[n_rhs_cell] = DEFINED (PINT 7) /\ S.STORE[n_result_cell] = DEFINED (PINT 42)
~(n_rhs_cell <- S.REFCELLS)
$heap_owners($heap_graph(S),HOBJECT n_child) = n_initial_owners
$property_magic_set_method(S,n_child) = (pmethoddesc_set)
pfunction_set = pmethoddesc_set.FUNCTION
$ppmethod_set_signature(pfunction_set.SIGNATURE) /\ $property_magic_set_method_source(S,pmethoddesc_set)
$property_effective_desc(S,n_child,$ptascii("value")) = (ppropertydesc)
$objectprops_at(S.OBJECTPROPS,n_child) = (ppropertyslot_all*)
$property_slot_at(ppropertyslot_all*,ppropertydesc.KEY) = (ppropertyslot_private)
ppropertyslot_private.STATE = PROP_VALUE (DIRECT (PINT 1))
$property_slot_at(ppropertyslot_all*,$ptascii("ready")) = (ppropertyslot_ready)
ppropertyslot_ready.STATE = PROP_VALUE (DIRECT (PINT 5))
$property_magic_set_needed(S,n_child,$ptascii("value")) /\ ~$property_magic_set_needed(S,n_child,$ptascii("ready"))
$property_dynamic_capture(S,BASE_PROPERTY_PENDING pbase poperand_name z_receiver,z,false) = eps
$property_magic_set_rhs(S,ppropertymagicset) = (7) /\ $ms_guard(S)
S_target = $property_pending_resolve(S,pbase,poperand_name,PPW,z_receiver,z)
S_rhs = $resolve_at(S_target,S.RESULT,z)
PhpStep: S ~> S_call
S_call = S_rhs[.TODO = [(CALL_ARGS (PROPERTY_MAGIC_SET_TARGET ppropertymagicset) eps 2 ([KNOWN (PSTRING ppropertymagicset.NAME),KNOWN (PINT 7)]) (ppropertymagicset.SITE) ppropertymagicset.LINE),PROPERTY_MAGIC_SET_RESULT ppropertymagicset] ++ ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]
$property_magic_set_capture(S_call,ppropertymagicset) /\ $property_magic_set_pending_call(S_call,ppropertymagicset)
$task_nodes(PROPERTY_MAGIC_SET_RESULT ppropertymagicset) = [HOBJECT n_child]
$target_nodes(PROPERTY_MAGIC_SET_TARGET ppropertymagicset) = eps
$heap_owners($heap_graph(S_call),HOBJECT n_child) = $(n_initial_owners + 1)
$ms_guard(S_call)
'''.strip().splitlines()

CALL = r'''
S_receive_found = $ms_seek(S_call,MS_RECEIVE ppropertymagicset.METHOD,1000)
S_receive_found.COMPLETION = NORMAL \/ S_receive_found.COMPLETION = BUDGET
S_receive = S_receive_found[.COMPLETION = NORMAL]
S_receive.TODO = (TYPE_RECEIVE ppropertymagicset.METHOD 0) :: ptask_receive_tail*
S_receive.CURRENT = (pcallcontext_receive)
pcallcontext_receive.TARGET = PROPERTY_MAGIC_SET_TARGET ppropertymagicset
$target_function(S_receive,pcallcontext_receive.TARGET) = (pfunction_set)
$receiving_function(S_receive,ppropertymagicset.METHOD) = (pfunction_set)
$ms_guard(S_receive)
S_enter_found = $ms_seek(S_receive,MS_OUTPUT ptbytes_enter,1000)
S_enter_found.COMPLETION = NORMAL \/ S_enter_found.COMPLETION = BUDGET
S_enter = S_enter_found[.COMPLETION = NORMAL]
$ms_stage(S_enter,MS_OUTPUT ptbytes_enter)
S_enter.CURRENT = (pcallcontext_set)
pcallcontext_set.TARGET = PROPERTY_MAGIC_SET_TARGET ppropertymagicset
pcallcontext_set.LEXICAL_CLASS = (pmethoddesc_set.OWNER) /\ pcallcontext_set.CALLED_CLASS = (ppropertymagicset.CLASS)
$lookup(S_enter.ENV,$ptascii("incoming")) = (n_incoming)
S_enter.STORE[n_incoming] = DEFINED (PINT 7)
$property_magic_set_guard(S_enter,S_enter.CURRENT,S_enter.FRAMES,n_child,$ptascii("value"))
~$property_magic_set_needed(S_enter,n_child,$ptascii("value")) /\ $ms_guard(S_enter)
S_rebound_found = $ms_seek(S_enter,MS_OUTPUT ptbytes_rebound,1000)
S_rebound_found.COMPLETION = NORMAL \/ S_rebound_found.COMPLETION = BUDGET
S_rebound = S_rebound_found[.COMPLETION = NORMAL]
$ms_stage(S_rebound,MS_OUTPUT ptbytes_rebound)
S_rebound.CURRENT = (pcallcontext_set)
S_rebound.STORE[n_child_cell] = DEFINED PNULL /\ S_rebound.STORE[n_rhs_cell] = DEFINED (PINT 99)
$objectprops_at(S_rebound.OBJECTPROPS,n_child) = (ppropertyslot_rebound*)
$property_slot_at(ppropertyslot_rebound*,ppropertydesc.KEY) = (ppropertyslot_written)
ppropertyslot_written.STATE = PROP_VALUE (DIRECT (PINT 7))
$heap_owners($heap_graph(S_rebound),HOBJECT n_child) = n_saved_owners
$property_magic_set_guard(S_rebound,S_rebound.CURRENT,S_rebound.FRAMES,n_child,$ptascii("value"))
S_rebound.FRAMES = pframe_set :: eps
S_saved = $constant_frame_view(S_rebound,pframe_set,eps)
$property_magic_set_valid(S_saved,ppropertymagicset) /\ ~$property_magic_set_capture(S_saved,ppropertymagicset)
$ms_guard(S_rebound)
'''.strip().splitlines()

RETURN = r'''
S_return_found = $ms_seek(S_rebound,MS_RETURN,1000)
S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET
S_return = S_return_found[.COMPLETION = NORMAL]
S_return.TODO = (PROPERTY_MAGIC_SET_RESULT ppropertymagicset) :: ptask_tail*
S_return.RESULT = KNOWN PNULL /\ S_return.CURRENT = eps /\ S_return.FRAMES = eps
S_return.STORE[n_rhs_cell] = DEFINED (PINT 99)
n_rhs_cell <- S_return.REFCELLS
$property_magic_set_valid(S_return,ppropertymagicset) /\ ~$property_magic_set_capture(S_return,ppropertymagicset)
~$property_magic_set_guard(S_return,S_return.CURRENT,S_return.FRAMES,n_child,$ptascii("value"))
PhpStep: S_return ~> S_release_raw
S_release_raw = S_return[.TODO = (PROPERTY_MAGIC_SET_DELIVERY ppropertymagicset) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]
$task_nodes(PROPERTY_MAGIC_SET_DELIVERY ppropertymagicset) = eps
$heap_owners($heap_graph(S_release_raw),HOBJECT n_child) = $(n_saved_owners - 1)
S_releasing = $ms_after(S_return,S_release_raw)
'''.strip().splitlines()

DESTRUCTOR = r'''
S_child_found = $ms_seek(S_releasing,MS_DTOR n_child,1000)
S_child_found.COMPLETION = NORMAL \/ S_child_found.COMPLETION = BUDGET
S_child = S_child_found[.COMPLETION = NORMAL]
$ms_stage(S_child,MS_DTOR n_child)
$ms_output(S_child.EVENTS) = ptbytes_rebound
~$property_magic_set_guard(S_child,S_child.CURRENT,S_child.FRAMES,n_child,$ptascii("value"))
S_child.FRAMES = pframe_child :: eps
S_late_saved = $constant_frame_view(S_child,pframe_child,eps)
$property_magic_set_delivery_valid(S_late_saved,ppropertymagicset)
$call_task_valid(S_late_saved,PROPERTY_MAGIC_SET_DELIVERY ppropertymagicset) /\ $ms_guard(S_child)
S_delivery_found = $ms_seek(S_child,MS_DELIVERY,1000)
S_delivery_found.COMPLETION = NORMAL \/ S_delivery_found.COMPLETION = BUDGET
S_delivery = S_delivery_found[.COMPLETION = NORMAL]
~(HOBJECT n_child <- S_delivery.ALLOCATIONS)
S_delivery.STORE[n_rhs_cell] = DEFINED (PINT 123)
$target_function(S_delivery,METHOD_TARGET n_child ppropertymagicset.METHOD) = eps
'''.strip().splitlines()

DELIVER = r'''
S_delivery.TODO = (PROPERTY_MAGIC_SET_DELIVERY ppropertymagicset) :: ptask_tail*
$property_magic_set_delivery_valid(S_delivery,ppropertymagicset) /\ $property_magic_set_rhs(S_delivery,ppropertymagicset) = (i_delivered)
~$property_magic_set_guard(S_delivery,S_delivery.CURRENT,S_delivery.FRAMES,n_child,$ptascii("value"))
$ms_guard(S_delivery)
PhpStep: S_delivery ~> S_delivered_raw
S_delivered_raw = S_delivery[.TODO = ptask_tail*][.RESULT = KNOWN (PINT i_delivered)]
S_after_delivery = $ms_after(S_delivery,S_delivered_raw)
S_budget_start = S_return
'''.strip().splitlines()

HELD_START = r'''
S_delivery_found = $ms_seek(S_releasing,MS_DELIVERY,1000)
S_delivery_found.COMPLETION = NORMAL \/ S_delivery_found.COMPLETION = BUDGET
S_delivery = S_delivery_found[.COMPLETION = NORMAL]
HOBJECT n_child <- S_delivery.ALLOCATIONS /\ $heap_owners($heap_graph(S_delivery),HOBJECT n_child) = 1
S_delivery.EVENTS = S_return.EVENTS /\ S_delivery.STORE[n_rhs_cell] = DEFINED (PINT 99)
'''.strip().splitlines()

HELD_END = r'''
S_main_found = $ms_seek(S_after_delivery,MS_MAIN ptbytes_main,1000)
S_main_found.COMPLETION = NORMAL \/ S_main_found.COMPLETION = BUDGET
S_main = S_main_found[.COMPLETION = NORMAL]
$ms_stage(S_main,MS_MAIN ptbytes_main)
S_main.STORE[n_result_cell] = DEFINED (PINT 99) /\ S_main.STORE[n_rhs_cell] = DEFINED (PINT 99)
HOBJECT n_child <- S_main.ALLOCATIONS /\ $heap_owners($heap_graph(S_main),HOBJECT n_child) = 1
S_child_found = $ms_seek(S_main,MS_DTOR n_child,1000)
S_child_found.COMPLETION = NORMAL \/ S_child_found.COMPLETION = BUDGET
S_child = S_child_found[.COMPLETION = NORMAL]
$ms_stage(S_child,MS_DTOR n_child) /\ $ms_output(S_child.EVENTS) = ptbytes_main
~$property_magic_set_guard(S_child,S_child.CURRENT,S_child.FRAMES,n_child,$ptascii("value")) /\ $ms_guard(S_child)
S_end = S_child
'''.strip().splitlines()

THROW = r'''
S_raised_found = $ms_seek(S_rebound,MS_RAISED,1000)
S_raised_found.COMPLETION = NORMAL \/ S_raised_found.COMPLETION = BUDGET
S_raised = S_raised_found[.COMPLETION = NORMAL]
S_raised.TODO = (THROW_SEARCH n_error) :: ptask_throw*
S_raised.CURRENT = (pcallcontext_set)
$throwable_live(S_raised,n_error) /\ $property_magic_set_guard(S_raised,S_raised.CURRENT,S_raised.FRAMES,n_child,$ptascii("value"))
S_throw_found = $ms_seek(S_raised,MS_THROW,1000)
S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET
S_throw = S_throw_found[.COMPLETION = NORMAL]
S_throw.TODO = (THROW_SEARCH n_error) :: (PROPERTY_MAGIC_SET_RESULT ppropertymagicset) :: ptask_tail*
$property_magic_set_valid(S_throw,ppropertymagicset) /\ ~$property_magic_set_capture(S_throw,ppropertymagicset)
S_throw.STORE[n_result_cell] = DEFINED (PINT 42)
PhpStep: S_throw ~> S_release_raw
S_release_raw.TODO = (THROW_SEARCH n_error) :: ptask_tail*
S_release_raw.RESULT = KNOWN PNULL /\ $throwable_live(S_release_raw,n_error)
$heap_owners($heap_graph(S_release_raw),HOBJECT n_child) = 0
S_releasing = $ms_after(S_throw,S_release_raw)
S_child_found = $ms_seek(S_releasing,MS_DTOR n_child,1000)
S_child_found.COMPLETION = NORMAL \/ S_child_found.COMPLETION = BUDGET
S_child = S_child_found[.COMPLETION = NORMAL]
$ms_stage(S_child,MS_DTOR n_child) /\ $throwable_live(S_child,n_error)
~$property_magic_set_guard(S_child,S_child.CURRENT,S_child.FRAMES,n_child,$ptascii("value")) /\ $ms_guard(S_child)
S_catch_found = $ms_seek(S_child,MS_CATCH,1000)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_try n_catch n_error) :: ptask_catch*
$throwable_live(S_catch,n_error) /\ S_catch.STORE[n_result_cell] = DEFINED (PINT 42)
S_catch.STORE[n_rhs_cell] = DEFINED (PINT 123) /\ ~(HOBJECT n_child <- S_catch.ALLOCATIONS)
PhpStep: S_catch ~> S_catch_raw
$lookup(S_catch_raw.ENV,$ptascii("caught")) = (n_caught_cell)
S_catch_raw.STORE[n_caught_cell] = DEFINED (POBJECT n_error)
S_end = $ms_after(S_catch,S_catch_raw)
S_budget_start = S_rebound
'''.strip().splitlines()

FINISH = r'''
S_final = $drive_steps(S_end,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$ms_output(S_final.EVENTS) = ptbytes_final
~(HOBJECT n_child <- S_final.ALLOCATIONS) /\ $ms_guard(S_final)
S_budget = $drive_steps(S_budget_start,0)
S_budget.COMPLETION = BUDGET /\ S_budget.TODO = S_budget_start.TODO /\ S_budget.EVENTS = S_budget_start.EVENTS
$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final
'''.strip().splitlines()

DERIVED = r'''
~$property_magic_set_method_source(S[.SOURCES = eps],pmethoddesc_set)
~$ppmethod_set_signature(pfunction_set.SIGNATURE[.RETURNS = [PTBRANCH ([PTBUILTIN "bool"])]])
ppropertymagicset_wrong_cell = ppropertymagicset[.CELL = (n_result_cell)]
S_wrong_cell = S_call[.TODO = [(CALL_ARGS (PROPERTY_MAGIC_SET_TARGET ppropertymagicset_wrong_cell) eps 2 ([KNOWN (PSTRING ppropertymagicset.NAME),KNOWN (PINT 7)]) (ppropertymagicset.SITE) ppropertymagicset.LINE),PROPERTY_MAGIC_SET_RESULT ppropertymagicset_wrong_cell] ++ ptask_tail*]
$property_magic_set_capture(S_wrong_cell,ppropertymagicset_wrong_cell) /\ ~$property_magic_set_pending_call(S_wrong_cell,ppropertymagicset_wrong_cell)
ppropertymagicset_wrong_input = ppropertymagicset[.INPUT = 99]
S_wrong_input = S_call[.TODO = [(CALL_ARGS (PROPERTY_MAGIC_SET_TARGET ppropertymagicset_wrong_input) eps 2 ([KNOWN (PSTRING ppropertymagicset.NAME),KNOWN (PINT 99)]) (ppropertymagicset.SITE) ppropertymagicset.LINE),PROPERTY_MAGIC_SET_RESULT ppropertymagicset_wrong_input] ++ ptask_tail*]
$property_magic_set_capture(S_wrong_input,ppropertymagicset_wrong_input) /\ ~$property_magic_set_pending_call(S_wrong_input,ppropertymagicset_wrong_input)
S_referenced = S[.REFCELLS = n_rhs_cell :: S.REFCELLS]
$property_magic_set_pending(S_referenced) /\ $property_magic_set_plan(S_referenced) = eps
PhpStep: S_referenced ~> S_referenced_done
S_referenced_done.COMPLETION = UNSUPPORTED "magic setter source, RHS, or recursive write"
ppropertymagicset_wrong_line = ppropertymagicset[.LINE = $(ppropertymagicset.LINE + 1)]
~$property_magic_set_source(S_call,ppropertymagicset_wrong_line)
S_nonint = S_delivery[.STORE[n_rhs_cell] = DEFINED PNULL]
$property_magic_set_delivery_valid(S_nonint,ppropertymagicset) /\ $property_magic_set_rhs(S_nonint,ppropertymagicset) = eps /\ $ms_guard(S_nonint)
PhpStep: S_nonint ~> S_nonint_done
S_nonint_done.COMPLETION = UNSUPPORTED "magic setter RHS continuation"
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', choices=('normal', 'literal', 'held', 'throwing'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_setter_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_gate_completed']
    assert [case['id'] for case in data['cases']] == ['normal', 'literal', 'held', 'throwing']
    selected = list(data['cases'])
    assert len(selected) == 4
    if args.case:
        selected = [case for case in selected if case['id'] == args.case]
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
    out = Path(tempfile.mkdtemp(prefix='magic-setter-protocol-', dir=ROOT / '.tools'))
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
            prefix = output[:2]
            enter_output = prefix + 'S|value|7|'
            rebound_output = enter_output + 's|'
            setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $ms_seek(S_initial,MS_PLAN,1000)', r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]',
                     'n_initial_owners = ' + str(2 if name == 'held' else 1),
                     'n_saved_owners = ' + str(2 if name == 'held' else 1),
                     'i_delivered = ' + str(7 if name == 'literal' else 99 if name == 'held' else 123),
                     'ptbytes_enter = $ptascii(' + json.dumps(enter_output) + ')',
                     'ptbytes_rebound = $ptascii(' + json.dumps(rebound_output) + ')',
                     'ptbytes_main = $ptascii(' + json.dumps(rebound_output + '99|99|') + ')',
                     'ptbytes_final = $ptascii(' + json.dumps(output) + ')']
            reached = setup + COMMON + ['ppropertymagicset.CELL = ' + ('eps' if name == 'literal' else '(n_rhs_cell)')] + CALL
            if name == 'throwing':
                reached += THROW
            elif name == 'held':
                reached += RETURN + HELD_START + DELIVER + HELD_END
            else:
                reached += RETURN + DESTRUCTOR + DELIVER + ['S_end = S_after_delivery']
            reached += FINISH + [f'ppropertymagicset.LINE = {case["assignment_line"]}']
            derived = DERIVED if name == 'normal' else []
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
