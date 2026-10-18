"""Check untyped __isset object-RV disposal before captured __get and throw cleanup."""
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
syntax pissetrvstage = IR_RV | IR_CACHE | IR_GET | IR_OUTPUT ptbytes | IR_MAIN ptbytes | IR_RAISED | IR_THROW | IR_DTOR nat | IR_CATCH
dec $ir_output(pevent*) : ptbytes
def $ir_output(eps) = eps
def $ir_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $ir_output(pevent*)
dec $ir_stage(pstate,pissetrvstage) : bool
def $ir_stage(S,IR_RV) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty false) :: ptask*
  -- if S.RESULT = KNOWN (POBJECT n)
def $ir_stage(S,IR_CACHE) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty false) :: ptask*
  -- if S.RESULT = KNOWN (PBOOL true)
def $ir_stage(S,IR_GET) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask*
def $ir_stage(S,IR_OUTPUT ptbytes) = true
  -- if S.CURRENT =/= eps
  -- if $ir_output(S.EVENTS) = ptbytes
def $ir_stage(S,IR_MAIN ptbytes) = true
  -- if S.CURRENT = eps
  -- if $ir_output(S.EVENTS) = ptbytes
def $ir_stage(S,IR_RAISED) = true
  -- if S.CURRENT =/= eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
def $ir_stage(S,IR_THROW) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: (PROPERTY_EMPTY_RESULT ppropertyempty false) :: ptask*
def $ir_stage(S,IR_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $ir_stage(S,IR_CATCH) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask*
def $ir_stage(S,pissetrvstage) = false -- otherwise
dec $ir_seek(pstate,pissetrvstage,nat) : pstate
def $ir_seek(S,pissetrvstage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $ir_stage(S,pissetrvstage) \/ n = 0
def $ir_seek(S,pissetrvstage,n) = $ir_seek($drive_steps(S[.COMPLETION = NORMAL],1),pissetrvstage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$ir_stage(S,pissetrvstage) /\ $(n > 0)
def $ir_seek(S,pissetrvstage,n) = $ir_seek($drive_steps(S,1),pissetrvstage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $ir_seek(S,pissetrvstage,n) = S -- otherwise
dec $ir_after(pstate,pstate) : pstate
def $ir_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $ir_guard(pstate) : bool
def $ir_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $gc_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''

COMMON = r'''
$ir_stage(S,IR_RV)
S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty false) :: ptask_tail*
n_child = ppropertyempty.OBJECT
S.RESULT = KNOWN (POBJECT n_rv)
S.OBJECTS[n_rv] = INSTANCE porigin_rv
$node_children(S,HOBJECT n_rv) = eps
$heap_unique([HOBJECT n_child,HOBJECT n_rv])
$lookup(S.ENV,$ptascii("child")) = (n_child_cell)
$lookup(S.ENV,$ptascii("next")) = (n_next_cell)
S.STORE[n_child_cell] = DEFINED (POBJECT n_child)
S.STORE[n_next_cell] = DEFINED (PINT 1)
$heap_owners($heap_graph(S),HOBJECT n_child) = 2
$heap_owners($heap_graph(S),HOBJECT n_rv) = n_rv_owners
$property_empty_method(S,n_child,false) = (pmethoddesc_isset)
pfunction_isset = pmethoddesc_isset.FUNCTION
$ppmethod_isset_signature(pfunction_isset.SIGNATURE) /\ pfunction_isset.SIGNATURE.RETURNS = eps
$property_empty_isset_source(S,pmethoddesc_isset) /\ ~$property_magic_method_source(S,pmethoddesc_isset,"__isset")
$property_empty_capture(S,ppropertyempty) /\ $property_empty_isset_rv_ready(S,ppropertyempty)
$property_empty_guard(S,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S,n_child,$ptascii("value"))
$ir_output(S.EVENTS) = ptbytes_isset /\ $ir_guard(S)
PhpStep: S ~> S_cached
S_cached = S[.RESULT = KNOWN (PBOOL true)]
$task_nodes(PROPERTY_EMPTY_RESULT ppropertyempty false) = [HOBJECT n_child]
$heap_owners($heap_graph(S_cached),HOBJECT n_rv) = $(n_rv_owners - 1)
S_disposing = $ir_after(S,S_cached)
'''.strip().splitlines()

VALUE = r'''
S_value_found = $ir_seek(S_disposing,IR_DTOR n_rv,1000)
S_value_found.COMPLETION = NORMAL \/ S_value_found.COMPLETION = BUDGET
S_value = S_value_found[.COMPLETION = NORMAL]
$ir_stage(S_value,IR_DTOR n_rv)
S_value.CURRENT = (pcallcontext_value)
$ir_output(S_value.EVENTS) = ptbytes_isset
$heap_owners($heap_graph(S_value),HOBJECT n_child) = 2
$property_empty_guard(S_value,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_value,n_child,$ptascii("value"))
$ir_guard(S_value)
S_rebound_found = $ir_seek(S_value,IR_OUTPUT ptbytes_rebound,1000)
S_rebound_found.COMPLETION = NORMAL \/ S_rebound_found.COMPLETION = BUDGET
S_rebound = S_rebound_found[.COMPLETION = NORMAL]
$ir_stage(S_rebound,IR_OUTPUT ptbytes_rebound)
S_rebound.CURRENT = (pcallcontext_value)
S_rebound.STORE[n_child_cell] = DEFINED PNULL
S_rebound.STORE[n_next_cell] = DEFINED (PINT 0)
$heap_owners($heap_graph(S_rebound),HOBJECT n_child) = 1
$property_empty_guard(S_rebound,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_rebound,n_child,$ptascii("value"))
S_rebound.FRAMES = pframe_value :: eps
S_saved = $constant_frame_view(S_rebound,pframe_value,eps)
S_saved.ORIGIN = (ppropertyempty.SITE)
$property_empty_valid(S_saved,ppropertyempty) /\ ~$property_empty_capture(S_saved,ppropertyempty)
$property_empty_rv_tasks(S_saved,pframe_value.TODO,n_child,$ptascii("value"))
$ir_guard(S_rebound)
'''.strip().splitlines()

NORMAL = r'''
S_resume_found = $ir_seek(S_rebound,IR_CACHE,1000)
S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET
S_resume = S_resume_found[.COMPLETION = NORMAL]
S_resume.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty false) :: ptask_tail*
S_resume.RESULT = KNOWN (PBOOL true) /\ S_resume.CURRENT = eps /\ S_resume.FRAMES = eps
~(HOBJECT n_rv <- S_resume.ALLOCATIONS)
$property_empty_valid(S_resume,ppropertyempty) /\ ~$property_empty_capture(S_resume,ppropertyempty)
$heap_owners($heap_graph(S_resume),HOBJECT n_child) = 1
PhpStep: S_resume ~> S_get_call
S_get_call.TODO = (CALL_ARGS (PROPERTY_EMPTY_TARGET ppropertyempty true) eps 1 ([KNOWN (PSTRING ppropertyempty.NAME)]) (ppropertyempty.SITE) ppropertyempty.LINE) :: (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail*
S_get_call.RESULT = KNOWN PNULL /\ S_get_call.EVENTS = S_resume.EVENTS
$property_empty_pending_call(S_get_call,ppropertyempty,true) /\ ~$property_empty_capture(S_get_call,ppropertyempty)
S_get_found = $ir_seek(S_get_call,IR_GET,1000)
S_get_found.COMPLETION = NORMAL \/ S_get_found.COMPLETION = BUDGET
S_get = S_get_found[.COMPLETION = NORMAL]
S_get.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail*
S_get.RESULT = KNOWN (PINT 0)
$ir_output(S_get.EVENTS) = ptbytes_rebound ++ $ptascii("G|")
~(HOBJECT n_rv <- S_get.ALLOCATIONS) /\ $heap_owners($heap_graph(S_get),HOBJECT n_child) = 1
PhpStep: S_get ~> S_release_raw
S_release_raw.TODO = ptask_tail* /\ S_release_raw.RESULT = KNOWN (PBOOL true)
$heap_owners($heap_graph(S_release_raw),HOBJECT n_child) = 0
S_released = $ir_after(S_get,S_release_raw)
S_child_found = $ir_seek(S_released,IR_DTOR n_child,1000)
S_child_found.COMPLETION = NORMAL \/ S_child_found.COMPLETION = BUDGET
S_child = S_child_found[.COMPLETION = NORMAL]
$ir_stage(S_child,IR_DTOR n_child)
$ir_output(S_child.EVENTS) = ptbytes_rebound ++ $ptascii("G|")
~$property_empty_guard(S_child,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_child,n_child,$ptascii("value"))
S_end = S_child
S_budget_start = S_rebound
'''.strip().splitlines()

HELD = r'''
S_resume_found = $ir_seek(S_disposing,IR_CACHE,1000)
S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET
S_resume = S_resume_found[.COMPLETION = NORMAL]
S_resume.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty false) :: ptask_tail*
S_resume.RESULT = KNOWN (PBOOL true) /\ S_resume.EVENTS = S.EVENTS
HOBJECT n_rv <- S_resume.ALLOCATIONS /\ $heap_owners($heap_graph(S_resume),HOBJECT n_rv) = 1
$heap_owners($heap_graph(S_resume),HOBJECT n_child) = 2 /\ $ir_guard(S_resume)
PhpStep: S_resume ~> S_get_call
S_get_found = $ir_seek(S_get_call,IR_GET,1000)
S_get_found.COMPLETION = NORMAL \/ S_get_found.COMPLETION = BUDGET
S_get = S_get_found[.COMPLETION = NORMAL]
S_get.RESULT = KNOWN (PINT 1) /\ HOBJECT n_rv <- S_get.ALLOCATIONS
$ir_output(S_get.EVENTS) = ptbytes_isset ++ $ptascii("G|")
PhpStep: S_get ~> S_release_raw
S_release_raw.RESULT = KNOWN (PBOOL false) /\ S_release_raw.TODO = ptask_tail*
$heap_owners($heap_graph(S_release_raw),HOBJECT n_child) = 1
S_released = $ir_after(S_get,S_release_raw)
ptbytes_main = ptbytes_isset ++ $ptascii("G|F|")
S_main_found = $ir_seek(S_released,IR_MAIN ptbytes_main,1000)
S_main_found.COMPLETION = NORMAL \/ S_main_found.COMPLETION = BUDGET
S_main = S_main_found[.COMPLETION = NORMAL]
$ir_stage(S_main,IR_MAIN ptbytes_main)
HOBJECT n_rv <- S_main.ALLOCATIONS /\ HOBJECT n_child <- S_main.ALLOCATIONS
$heap_owners($heap_graph(S_main),HOBJECT n_rv) = 1 /\ $heap_owners($heap_graph(S_main),HOBJECT n_child) = 1
~$property_empty_guard(S_main,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_main,n_child,$ptascii("value"))
S_value_found = $ir_seek(S_main,IR_DTOR n_rv,1000)
S_value_found.COMPLETION = NORMAL \/ S_value_found.COMPLETION = BUDGET
S_value = S_value_found[.COMPLETION = NORMAL]
$ir_stage(S_value,IR_DTOR n_rv)
S_value.CURRENT = (pcallcontext_value)
$ir_output(S_value.EVENTS) = ptbytes_isset ++ $ptascii("G|F|")
~$property_empty_guard(S_value,n_child,$ptascii("value"))
S_child_found = $ir_seek(S_value,IR_DTOR n_child,1000)
S_child_found.COMPLETION = NORMAL \/ S_child_found.COMPLETION = BUDGET
S_child = S_child_found[.COMPLETION = NORMAL]
$ir_stage(S_child,IR_DTOR n_child)
$ir_output(S_child.EVENTS) = ptbytes_isset ++ $ptascii("G|F|V|")
~$property_empty_guard(S_child,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_child,n_child,$ptascii("value"))
S_rebound_found = $ir_seek(S_child,IR_OUTPUT ptbytes_rebound,1000)
S_rebound_found.COMPLETION = NORMAL \/ S_rebound_found.COMPLETION = BUDGET
S_rebound = S_rebound_found[.COMPLETION = NORMAL]
$ir_stage(S_rebound,IR_OUTPUT ptbytes_rebound)
S_rebound.CURRENT = (pcallcontext_value)
S_rebound.STORE[n_child_cell] = DEFINED PNULL /\ S_rebound.STORE[n_next_cell] = DEFINED (PINT 0)
~(HOBJECT n_child <- S_rebound.ALLOCATIONS) /\ $ir_guard(S_rebound)
S_end = S_rebound
S_budget_start = S_rebound
'''.strip().splitlines()

THROW = r'''
S_raised_found = $ir_seek(S_rebound,IR_RAISED,1000)
S_raised_found.COMPLETION = NORMAL \/ S_raised_found.COMPLETION = BUDGET
S_raised = S_raised_found[.COMPLETION = NORMAL]
S_raised.TODO = (THROW_SEARCH n_error) :: ptask_throw*
S_raised.CURRENT = (pcallcontext_value)
$throwable_live(S_raised,n_error) /\ $property_empty_guard(S_raised,n_child,$ptascii("value"))
S_throw_found = $ir_seek(S_raised,IR_THROW,1000)
S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET
S_throw = S_throw_found[.COMPLETION = NORMAL]
S_throw.TODO = (THROW_SEARCH n_error) :: (PROPERTY_EMPTY_RESULT ppropertyempty false) :: ptask_tail*
~(HOBJECT n_rv <- S_throw.ALLOCATIONS) /\ $heap_owners($heap_graph(S_throw),HOBJECT n_child) = 1
$property_empty_throw_tail(S_throw,ppropertyempty,false) /\ ~$property_empty_capture(S_throw,ppropertyempty)
$ir_output(S_throw.EVENTS) = ptbytes_rebound
PhpStep: S_throw ~> S_release_raw
S_release_raw.TODO = (THROW_SEARCH n_error) :: ptask_tail*
S_release_raw.RESULT = KNOWN PNULL /\ S_release_raw.EVENTS = S_throw.EVENTS /\ $throwable_live(S_release_raw,n_error)
$heap_owners($heap_graph(S_release_raw),HOBJECT n_child) = 0
S_released = $ir_after(S_throw,S_release_raw)
S_child_found = $ir_seek(S_released,IR_DTOR n_child,1000)
S_child_found.COMPLETION = NORMAL \/ S_child_found.COMPLETION = BUDGET
S_child = S_child_found[.COMPLETION = NORMAL]
$ir_stage(S_child,IR_DTOR n_child)
$ir_output(S_child.EVENTS) = ptbytes_rebound
~$property_empty_guard(S_child,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_child,n_child,$ptascii("value"))
S_catch_found = $ir_seek(S_child,IR_CATCH,1000)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_try n_catch n_error) :: ptask_catch*
$throwable_live(S_catch,n_error) /\ $ir_output(S_catch.EVENTS) = ptbytes_rebound ++ $ptascii("D|")
PhpStep: S_catch ~> S_catch_raw
$lookup(S_catch_raw.ENV,$ptascii("caught")) = (n_caught_cell)
S_catch_raw.STORE[n_caught_cell] = DEFINED (POBJECT n_error)
S_end = $ir_after(S_catch,S_catch_raw)
S_budget_start = S_rebound
'''.strip().splitlines()

FINISH = r'''
S_final = $drive_steps(S_end,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$ir_output(S_final.EVENTS) = ptbytes_final
~(HOBJECT n_child <- S_final.ALLOCATIONS) /\ ~(HOBJECT n_rv <- S_final.ALLOCATIONS)
$ir_guard(S_final)
S_budget = $drive_steps(S_budget_start,0)
S_budget.COMPLETION = BUDGET /\ S_budget.TODO = S_budget_start.TODO /\ S_budget.EVENTS = S_budget_start.EVENTS
$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final
'''.strip().splitlines()

DERIVED = r'''
$ppmethod_isset_signature(pfunction_isset.SIGNATURE[.RETURNS = [PTBRANCH ([PTBUILTIN "bool"])]])
~$ppmethod_isset_signature(pfunction_isset.SIGNATURE[.RETURNS = [PTBRANCH ([PTBUILTIN "void"])]])
~$property_empty_isset_source(S[.SOURCES = eps],pmethoddesc_isset)
S_null = S[.RESULT = KNOWN PNULL][.HELD = S.HELD ++ [HOBJECT n_rv]]
$ir_guard(S_null) /\ $property_empty_valid(S_null,ppropertyempty) /\ ~$property_empty_isset_rv_ready(S_null,ppropertyempty)
PhpStep: S_null ~> S_null_done
S_null_done.COMPLETION = UNSUPPORTED "magic empty isset result type" /\ S_null_done.TODO = S.TODO /\ S_null_done.EVENTS = S.EVENTS
S_false = S[.RESULT = KNOWN (PBOOL false)][.HELD = S.HELD ++ [HOBJECT n_rv]]
$ir_guard(S_false) /\ $property_empty_valid(S_false,ppropertyempty)
PhpStep: S_false ~> S_false_done
S_false_done.RESULT = KNOWN (PBOOL true) /\ S_false_done.TODO = ptask_tail* /\ S_false_done.EVENTS = S.EVENTS
$heap_owners($heap_graph(S_false_done),HOBJECT n_child) = 1
'''.strip().splitlines()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', choices=('normal', 'held', 'throwing'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_empty_isset_rv_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_gate_completed']
    assert [case['id'] for case in data['cases']] == ['normal', 'held', 'throwing', 'false']
    selected = [case for case in data['cases'] if case['id'] != 'false']
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
    out = Path(tempfile.mkdtemp(prefix='magic-empty-isset-rv-protocol-', dir=ROOT / '.tools'))
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
            isset_output = output[:output.index('I|') + 2]
            rebound_output = isset_output + ('G|F|V|D|v|' if name == 'held' else 'V|v|')
            setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $ir_seek(S_initial,IR_RV,1000)', r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]',
                     'n_rv_owners = ' + str(2 if name == 'held' else 1),
                     'ptbytes_isset = $ptascii(' + json.dumps(isset_output) + ')',
                     'ptbytes_rebound = $ptascii(' + json.dumps(rebound_output) + ')',
                     'ptbytes_final = $ptascii(' + json.dumps(output) + ')']
            reached = setup + COMMON + (HELD if name == 'held' else VALUE + (THROW if name == 'throwing' else NORMAL)) + FINISH
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
