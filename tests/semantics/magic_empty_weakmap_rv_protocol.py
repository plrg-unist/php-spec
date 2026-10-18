"""Check WeakMap getter RV unregistering, value disposal and retained owners."""
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

syntax pmaprvstage = WM_RV | WM_RESUME | WM_OUTPUT ptbytes | WM_MAIN ptbytes | WM_RAISED | WM_THROW | WM_DTOR nat | WM_CATCH
dec $wm_output(pevent*) : ptbytes
def $wm_output(eps) = eps
def $wm_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $wm_output(pevent*)
dec $wm_stage(pstate,pmaprvstage) : bool
def $wm_stage(S,WM_RV) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask*
def $wm_stage(S,WM_RESUME) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask*
def $wm_stage(S,WM_OUTPUT ptbytes) = true
  -- if S.CURRENT =/= eps
  -- if $wm_output(S.EVENTS) = ptbytes
def $wm_stage(S,WM_MAIN ptbytes) = true
  -- if S.CURRENT = eps
  -- if $wm_output(S.EVENTS) = ptbytes
def $wm_stage(S,WM_RAISED) = true
  -- if S.CURRENT =/= eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
def $wm_stage(S,WM_THROW) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask*
def $wm_stage(S,WM_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $wm_stage(S,WM_CATCH) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask*
def $wm_stage(S,pmaprvstage) = false -- otherwise
dec $wm_seek(pstate,pmaprvstage,nat) : pstate
def $wm_seek(S,pmaprvstage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $wm_stage(S,pmaprvstage) \/ n = 0
def $wm_seek(S,pmaprvstage,n) = $wm_seek($drive_steps(S[.COMPLETION = NORMAL],1),pmaprvstage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$wm_stage(S,pmaprvstage) /\ $(n > 0)
def $wm_seek(S,pmaprvstage,n) = $wm_seek($drive_steps(S,1),pmaprvstage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $wm_seek(S,pmaprvstage,n) = S -- otherwise
dec $wm_after(pstate,pstate) : pstate
def $wm_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $wm_guard(pstate) : bool
def $wm_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $gc_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''

COMMON = r'''
$wm_stage(S,WM_RV)
S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail*
n_child = ppropertyempty.OBJECT
S.RESULT = KNOWN (POBJECT n_map)
S.OBJECTS[n_map] = WEAKMAP (pweakmapentry)
n_key = pweakmapentry.KEY
pweakmapentry.VALUE = POBJECT n_value
S.OBJECTS[n_key] = STDINSTANCE
S.OBJECTS[n_value] = INSTANCE porigin_value
$lookup(S.ENV,$ptascii("weak")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
S.OBJECTS[n_weak] = WEAKREFERENCE (n_key)
pweakmapentry.BEFORE = (n_weak)
$heap_unique([HOBJECT n_child,HOBJECT n_map,HOBJECT n_key,HOBJECT n_value,HOBJECT n_weak])
$node_children(S,HOBJECT n_map) = [HOBJECT n_value] /\ $node_children(S,HOBJECT n_value) = eps
$weakmap_key_maps(S,S.ALLOCATIONS,n_key) = [n_map]
$heap_owners($heap_graph(S),HOBJECT n_child) = 2 /\ $heap_owners($heap_graph(S),HOBJECT n_map) = n_map_owners
$heap_owners($heap_graph(S),HOBJECT n_key) = 1 /\ $heap_owners($heap_graph(S),HOBJECT n_value) = 1
$property_empty_capture(S,ppropertyempty) /\ $property_empty_rv_ready(S,ppropertyempty) /\ $property_empty_truth(S,POBJECT n_map) = eps
$wm_output(S.EVENTS) = ptbytes_get /\ $wm_guard(S)
PhpStep: S ~> S_phase_raw
S_phase_raw.TODO = (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask_tail*
S_phase_raw.RESULT = KNOWN (PBOOL false) /\ S_phase_raw.EVENTS = S.EVENTS
$task_nodes(PROPERTY_EMPTY_RV ppropertyemptyrv) = [HOBJECT n_child]
$heap_owners($heap_graph(S_phase_raw),HOBJECT n_map) = $(n_map_owners - 1)
S_disposing = $wm_after(S,S_phase_raw)
'''.strip().splitlines()

VALUE = r'''
S_value_found = $wm_seek(S_disposal,WM_DTOR n_value,1000)
S_value_found.COMPLETION = NORMAL \/ S_value_found.COMPLETION = BUDGET
S_value = S_value_found[.COMPLETION = NORMAL]
$wm_stage(S_value,WM_DTOR n_value)
S_value.CURRENT = (pcallcontext_value)
S_value.OBJECTS[n_map] = WEAKMAP eps
HOBJECT n_map <- S_value.ALLOCATIONS /\ $instance_storage_freeing(S_value,n_map)
$instance_storage_for(S_value,n_map) = (pinstancestorage)
pinstancestorage.OBJECT = n_map /\ pinstancestorage.SLOTS = eps /\ pinstancestorage.NEXT = 0
$weakmap_key_maps(S_value,S_value.ALLOCATIONS,n_key) = eps
$heap_owners($heap_graph(S_value),HOBJECT n_map) = 1
$instance_storage_basic(S_value,pinstancestorage)
$wm_output(S_value.EVENTS) = ptbytes_before_value /\ $wm_guard(S_value)
S_key_found = $wm_seek(S_value,WM_OUTPUT ptbytes_key,1000)
S_key_found.COMPLETION = NORMAL \/ S_key_found.COMPLETION = BUDGET
S_key = S_key_found[.COMPLETION = NORMAL]
$wm_stage(S_key,WM_OUTPUT ptbytes_key)
S_key.CURRENT = (pcallcontext_value)
~(HOBJECT n_key <- S_key.ALLOCATIONS) /\ S_key.OBJECTS[n_weak] = WEAKREFERENCE eps
HOBJECT n_weak <- S_key.ALLOCATIONS /\ HOBJECT n_map <- S_key.ALLOCATIONS
$instance_storage_freeing(S_key,n_map) /\ $wm_guard(S_key)
'''.strip().splitlines()

REBOUND = r'''
S_rebound_found = $wm_seek(S_key,WM_OUTPUT ptbytes_rebound,1000)
S_rebound_found.COMPLETION = NORMAL \/ S_rebound_found.COMPLETION = BUDGET
S_rebound = S_rebound_found[.COMPLETION = NORMAL]
$wm_stage(S_rebound,WM_OUTPUT ptbytes_rebound)
S_rebound.CURRENT = (pcallcontext_value)
$lookup(S_rebound.ENV,$ptascii("child")) = (n_child_cell)
S_rebound.STORE[n_child_cell] = DEFINED PNULL
$heap_owners($heap_graph(S_rebound),HOBJECT n_child) = 1
$property_empty_guard(S_rebound,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_rebound,n_child,$ptascii("value"))
$instance_storage_freeing(S_rebound,n_map) /\ $wm_guard(S_rebound)
'''.strip().splitlines()

NORMAL = r'''
S_resume_found = $wm_seek(S_rebound,WM_RESUME,1000)
S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET
S_resume = S_resume_found[.COMPLETION = NORMAL]
S_resume.TODO = (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask_tail*
S_resume.RESULT = KNOWN (PBOOL false) /\ S_resume.CURRENT = eps /\ S_resume.FRAMES = eps
~(HOBJECT n_map <- S_resume.ALLOCATIONS) /\ ~(HOBJECT n_value <- S_resume.ALLOCATIONS) /\ ~(HOBJECT n_key <- S_resume.ALLOCATIONS)
$heap_owners($heap_graph(S_resume),HOBJECT n_child) = 1
$property_empty_rv_valid(S_resume,ppropertyemptyrv) /\ ~$property_empty_capture(S_resume,ppropertyempty)
PhpStep: S_resume ~> S_release_raw
S_release_raw.TODO = ptask_tail* /\ S_release_raw.RESULT = KNOWN (PBOOL false) /\ S_release_raw.EVENTS = S_resume.EVENTS
$heap_owners($heap_graph(S_release_raw),HOBJECT n_child) = 0
S_released = $wm_after(S_resume,S_release_raw)
S_child_found = $wm_seek(S_released,WM_DTOR n_child,1000)
S_child_found.COMPLETION = NORMAL \/ S_child_found.COMPLETION = BUDGET
S_child = S_child_found[.COMPLETION = NORMAL]
$wm_stage(S_child,WM_DTOR n_child)
$wm_output(S_child.EVENTS) = ptbytes_rebound
~(HOBJECT n_map <- S_child.ALLOCATIONS) /\ ~(HOBJECT n_value <- S_child.ALLOCATIONS)
~$property_empty_guard(S_child,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_child,n_child,$ptascii("value"))
S_end = S_child
S_budget_start = S_rebound
'''.strip().splitlines()

THROW = r'''
S_raised_found = $wm_seek(S_rebound,WM_RAISED,1000)
S_raised_found.COMPLETION = NORMAL \/ S_raised_found.COMPLETION = BUDGET
S_raised = S_raised_found[.COMPLETION = NORMAL]
S_raised.TODO = (THROW_SEARCH n_error) :: ptask_throw*
S_raised.CURRENT = (pcallcontext_value)
$throwable_live(S_raised,n_error) /\ $property_empty_guard(S_raised,n_child,$ptascii("value"))
S_throw_found = $wm_seek(S_raised,WM_THROW,1000)
S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET
S_throw = S_throw_found[.COMPLETION = NORMAL]
S_throw.TODO = (THROW_SEARCH n_error) :: (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask_tail*
~(HOBJECT n_map <- S_throw.ALLOCATIONS) /\ ~(HOBJECT n_value <- S_throw.ALLOCATIONS) /\ ~(HOBJECT n_key <- S_throw.ALLOCATIONS)
$property_empty_rv_valid(S_throw,ppropertyemptyrv) /\ ~$property_empty_capture(S_throw,ppropertyempty)
$heap_owners($heap_graph(S_throw),HOBJECT n_child) = 1
PhpStep: S_throw ~> S_release_raw
S_release_raw.TODO = (THROW_SEARCH n_error) :: ptask_tail*
S_release_raw.RESULT = KNOWN PNULL /\ S_release_raw.EVENTS = S_throw.EVENTS /\ $throwable_live(S_release_raw,n_error)
$heap_owners($heap_graph(S_release_raw),HOBJECT n_child) = 0
S_released = $wm_after(S_throw,S_release_raw)
S_child_found = $wm_seek(S_released,WM_DTOR n_child,1000)
S_child_found.COMPLETION = NORMAL \/ S_child_found.COMPLETION = BUDGET
S_child = S_child_found[.COMPLETION = NORMAL]
$wm_stage(S_child,WM_DTOR n_child)
$wm_output(S_child.EVENTS) = ptbytes_rebound
~$property_empty_guard(S_child,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_child,n_child,$ptascii("value"))
S_catch_found = $wm_seek(S_child,WM_CATCH,1000)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_try n_catch n_error) :: ptask_catch*
$throwable_live(S_catch,n_error) /\ $wm_output(S_catch.EVENTS) = ptbytes_rebound ++ $ptascii("D|")
PhpStep: S_catch ~> S_catch_raw
$lookup(S_catch_raw.ENV,$ptascii("caught")) = (n_caught_cell)
S_catch_raw.STORE[n_caught_cell] = DEFINED (POBJECT n_error)
S_end = $wm_after(S_catch,S_catch_raw)
S_budget_start = S_rebound
'''.strip().splitlines()

HELD = r'''
S_resume_found = $wm_seek(S_disposing,WM_RESUME,1000)
S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET
S_resume = S_resume_found[.COMPLETION = NORMAL]
S_resume.TODO = (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask_tail*
S_resume.RESULT = KNOWN (PBOOL false) /\ S_resume.EVENTS = S.EVENTS
S_resume.OBJECTS[n_map] = WEAKMAP (pweakmapentry) /\ HOBJECT n_value <- S_resume.ALLOCATIONS
$heap_owners($heap_graph(S_resume),HOBJECT n_map) = 1 /\ $heap_owners($heap_graph(S_resume),HOBJECT n_child) = 2
S_resume.DESTRUCTION.CALLED = S.DESTRUCTION.CALLED /\ $wm_guard(S_resume)
PhpStep: S_resume ~> S_release_raw
S_release_raw.RESULT = KNOWN (PBOOL false) /\ S_release_raw.TODO = ptask_tail*
$heap_owners($heap_graph(S_release_raw),HOBJECT n_child) = 1
S_released = $wm_after(S_resume,S_release_raw)
S_main_found = $wm_seek(S_released,WM_MAIN ptbytes_before_value,1000)
S_main_found.COMPLETION = NORMAL \/ S_main_found.COMPLETION = BUDGET
S_main = S_main_found[.COMPLETION = NORMAL]
$wm_stage(S_main,WM_MAIN ptbytes_before_value)
S_main.OBJECTS[n_map] = WEAKMAP (pweakmapentry) /\ HOBJECT n_child <- S_main.ALLOCATIONS
$heap_owners($heap_graph(S_main),HOBJECT n_map) = 1 /\ $heap_owners($heap_graph(S_main),HOBJECT n_value) = 1
~$property_empty_guard(S_main,n_child,$ptascii("value"))
S_disposal = S_main
'''.strip().splitlines()

HELD_FINISH = r'''
~$property_empty_guard(S_key,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_key,n_child,$ptascii("value"))
$heap_owners($heap_graph(S_key),HOBJECT n_child) = 1
S_child_found = $wm_seek(S_key,WM_DTOR n_child,1000)
S_child_found.COMPLETION = NORMAL \/ S_child_found.COMPLETION = BUDGET
S_child = S_child_found[.COMPLETION = NORMAL]
$wm_stage(S_child,WM_DTOR n_child)
$wm_output(S_child.EVENTS) = ptbytes_key
HOBJECT n_map <- S_child.ALLOCATIONS /\ $instance_storage_freeing(S_child,n_map) /\ HOBJECT n_value <- S_child.ALLOCATIONS
~$property_empty_guard(S_child,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_child,n_child,$ptascii("value"))
S_tail_found = $wm_seek(S_child,WM_OUTPUT ptbytes_rebound,1000)
S_tail_found.COMPLETION = NORMAL \/ S_tail_found.COMPLETION = BUDGET
S_tail = S_tail_found[.COMPLETION = NORMAL]
$wm_stage(S_tail,WM_OUTPUT ptbytes_rebound)
S_tail.CURRENT = (pcallcontext_value)
~(HOBJECT n_child <- S_tail.ALLOCATIONS) /\ HOBJECT n_map <- S_tail.ALLOCATIONS
S_end = S_tail
S_budget_start = S_main
'''.strip().splitlines()

FINISH = r'''
S_final = $drive_steps(S_end,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$wm_output(S_final.EVENTS) = ptbytes_final
~(HOBJECT n_child <- S_final.ALLOCATIONS) /\ ~(HOBJECT n_map <- S_final.ALLOCATIONS) /\ ~(HOBJECT n_value <- S_final.ALLOCATIONS) /\ ~(HOBJECT n_key <- S_final.ALLOCATIONS)
$wm_guard(S_final)
S_budget = $drive_steps(S_budget_start,0)
S_budget.COMPLETION = BUDGET /\ S_budget.TODO = S_budget_start.TODO /\ S_budget.EVENTS = S_budget_start.EVENTS
$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final
'''.strip().splitlines()

DERIVED = r'''
S_wrapper = S[.RESULT = KNOWN (POBJECT n_weak)][.HELD = S.HELD ++ [HOBJECT n_map]]
$wm_guard(S_wrapper) /\ $property_empty_valid(S_wrapper,ppropertyempty)
~$property_empty_rv_ready(S_wrapper,ppropertyempty) /\ ~$property_empty_rv_kind(S_wrapper,S_wrapper.OBJECTS[n_weak])
PhpStep: S_wrapper ~> S_wrapper_done
S_wrapper_done.COMPLETION = UNSUPPORTED "magic empty getter result type" /\ S_wrapper_done.EVENTS = S.EVENTS
S_empty = S[.OBJECTS[n_map] = WEAKMAP eps][.HELD = S.HELD ++ [HOBJECT n_value]]
$wm_guard(S_empty) /\ $property_empty_rv_kind(S_empty,WEAKMAP eps)
$property_empty_rv_ready(S_empty,ppropertyempty) /\ $property_empty_truth(S_empty,POBJECT n_map) = eps
PhpStep: S_empty ~> S_empty_raw
S_empty_raw.RESULT = KNOWN (PBOOL false)
S_empty_after = $wm_after(S_empty,S_empty_raw)
S_empty_found = $wm_seek(S_empty_after,WM_RESUME,1000)
S_empty_found.COMPLETION = NORMAL \/ S_empty_found.COMPLETION = BUDGET
S_empty_resume = S_empty_found[.COMPLETION = NORMAL]
S_empty_resume.TODO = (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask_tail*
S_empty_resume.RESULT = KNOWN (PBOOL false) /\ S_empty_resume.EVENTS = S.EVENTS
~(HOBJECT n_map <- S_empty_resume.ALLOCATIONS) /\ HOBJECT n_value <- S_empty_resume.ALLOCATIONS
$heap_owners($heap_graph(S_empty_resume),HOBJECT n_child) = 2 /\ $wm_guard(S_empty_resume)
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', choices=('normal', 'held', 'throwing'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_empty_weakmap_rv_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_gate_completed']
    selected = [case for case in data['cases'] if case['id'] in ('normal', 'held', 'throwing')]
    assert len(selected) == 3
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
    out = Path(tempfile.mkdtemp(prefix='magic-empty-weakmap-rv-protocol-', dir=ROOT / '.tools'))
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
            get_output = output[:output.index('G|') + 2]
            before_value = get_output + ('F|' if name == 'held' else '')
            key_output = before_value + 'V|K|'
            rebound_output = key_output + ('D|v|' if name == 'held' else 'v|')
            setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $wm_seek(S_initial,WM_RV,1000)', r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]',
                     'n_map_owners = ' + str(case['map_owners_at_rv']),
                     'ptbytes_get = $ptascii(' + json.dumps(get_output) + ')',
                     'ptbytes_before_value = $ptascii(' + json.dumps(before_value) + ')',
                     'ptbytes_key = $ptascii(' + json.dumps(key_output) + ')',
                     'ptbytes_rebound = $ptascii(' + json.dumps(rebound_output) + ')',
                     'ptbytes_final = $ptascii(' + json.dumps(output) + ')']
            if name == 'held':
                reached = setup + COMMON + HELD + VALUE + HELD_FINISH + FINISH
            else:
                reached = setup + COMMON + ['S_disposal = S_disposing'] + VALUE + REBOUND + (THROW if name == 'throwing' else NORMAL) + FINISH
            reached += [f'ppropertyempty.LINE = {case["empty_line"]}']
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
