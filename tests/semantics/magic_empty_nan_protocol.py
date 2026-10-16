"""Check captured NaN empty warnings, callback guards and receiver cleanup."""
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
syntax pemptywarnstage = MN_RV | MN_REBOUND ptbytes | MN_RETURN | MN_CLEAN | MN_RESUME | MN_RAISED | MN_THROW | MN_DTOR
dec $mn_output(pevent*) : ptbytes
def $mn_output(eps) = eps
def $mn_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $mn_output(pevent*)
def $mn_output(pevent :: pevent_tail*) = $mn_output(pevent_tail*) -- otherwise
dec $mn_stage(pstate,pemptywarnstage) : bool
def $mn_stage(S,MN_RV) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask*
def $mn_stage(S,MN_REBOUND ptbytes) = true
  -- if S.CURRENT =/= eps
  -- if $mn_output(S.EVENTS) = ptbytes
def $mn_stage(S,MN_RETURN) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask*
def $mn_stage(S,MN_CLEAN) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (ERROR_HANDLER_CLEAN perrorcall) :: ptask*
def $mn_stage(S,MN_RESUME) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_EMPTY_NAN ppropertyemptynan) :: ptask*
def $mn_stage(S,MN_RAISED) = true
  -- if S.CURRENT =/= eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
def $mn_stage(S,MN_THROW) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask*
def $mn_stage(S,MN_DTOR) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_kind(S,pcallcontext)
def $mn_stage(S,pemptywarnstage) = false -- otherwise
dec $mn_seek(pstate,pemptywarnstage,nat) : pstate
def $mn_seek(S,pemptywarnstage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $mn_stage(S,pemptywarnstage) \/ n = 0
def $mn_seek(S,pemptywarnstage,n) = $mn_seek($drive_steps(S[.COMPLETION = NORMAL],1),pemptywarnstage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$mn_stage(S,pemptywarnstage) /\ $(n > 0)
def $mn_seek(S,pemptywarnstage,n) = $mn_seek($drive_steps(S,1),pemptywarnstage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $mn_seek(S,pemptywarnstage,n) = S -- otherwise
dec $mn_after(pstate,pstate) : pstate
def $mn_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $mn_guard(pstate) : bool
def $mn_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''

COMMON = r'''
$mn_stage(S,MN_RV)
S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail*
n_child = ppropertyempty.OBJECT
S.RESULT = KNOWN (PFLOAT 9221120237041090560)
S.CURRENT = eps /\ S.FRAMES = eps /\ S.ORIGIN = (ppropertyempty.SITE)
$property_empty_nan_ready(S,ppropertyempty) /\ $property_empty_truth(S,PFLOAT 9221120237041090560) = eps
$property_empty_capture(S,ppropertyempty) /\ $mn_guard(S)
$property_empty_guard(S,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S,n_child,$ptascii("value"))
$value_nodes(PFLOAT 9221120237041090560) = eps /\ $heap_owners($heap_graph(S),HOBJECT n_child) = 2
PhpStep: S ~> S_warning_raw
S_warning = $mn_after(S,S_warning_raw)
S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = PROPERTY_EMPTY_NAN ppropertyemptynan
ppropertyemptynan.EMPTY = ppropertyempty /\ ppropertyemptynan.FLOAT = 9221120237041090560
ppropertyemptynan.OWNER = 0 /\ ppropertyemptynan.CALLER = eps /\ ppropertyemptynan.TAIL = ptask_tail*
perrorcall.SITE = ppropertyempty.SITE /\ perrorcall.LINE = ppropertyempty.LINE /\ perrorcall.LEVEL = 2
perrorcall.MESSAGE = $ptascii("unexpected NAN value was coerced to bool") /\ perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE perrorcall.LINE
S_warning.RESULT = KNOWN PNULL /\ S_warning.BASE = BASE_VALUE (KNOWN PNULL) /\ S_warning.EVENTS = S.EVENTS
$property_empty_nan_valid(S_warning,ppropertyemptynan) /\ $error_call_valid(S_warning,perrorcall) /\ $mn_guard(S_warning)
$task_nodes(perrorcall.RESUME) = [HOBJECT n_child] /\ $heap_owners($heap_graph(S_warning),HOBJECT n_child) = 2
PhpStep: S_warning ~> S_entered_raw
S_entered = $mn_after(S_warning,S_entered_raw)
S_entered.CURRENT = (pcallcontext_handler)
S_entered.FRAMES = [pframe_handler]
pframe_handler.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*
perrorcall_entered = perrorcall[.TARGET = (pcallcontext_handler.TARGET)]
pframe_handler.CONTEXT = eps /\ pframe_handler.ORIGIN = (ppropertyempty.SITE)
$property_empty_guard(S_entered,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_entered,n_child,$ptascii("value"))
$mn_guard(S_entered)
S_rebound_found = $mn_seek(S_entered,MN_REBOUND ptbytes_handler,1000)
S_rebound_found.COMPLETION = NORMAL \/ S_rebound_found.COMPLETION = BUDGET
S_rebound = S_rebound_found[.COMPLETION = NORMAL]
$mn_stage(S_rebound,MN_REBOUND ptbytes_handler)
S_rebound.CURRENT = (pcallcontext_handler) /\ S_rebound.FRAMES = [pframe_handler]
S_caller = $constant_frame_scope(S_rebound,pframe_handler,eps)
$lookup(S_caller.ENV,$ptascii("child")) = (n_child_cell)
S_caller.STORE[n_child_cell] = DEFINED PNULL
$property_empty_valid(S_caller,ppropertyempty) /\ ~$property_empty_capture(S_caller,ppropertyempty)
$property_empty_nan_valid(S_caller,ppropertyemptynan) /\ $error_call_valid(S_caller,perrorcall_entered)
$property_empty_guard(S_rebound,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_rebound,n_child,$ptascii("value"))
$heap_owners($heap_graph(S_rebound),HOBJECT n_child) = 1 /\ $mn_guard(S_rebound)
'''.strip().splitlines()

RETURN = r'''
S_return_found = $mn_seek(S_rebound,MN_RETURN,1000)
S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET
S_return = S_return_found[.COMPLETION = NORMAL]
S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*
S_return.RESULT = KNOWN (PBOOL true) /\ S_return.CURRENT = eps /\ S_return.FRAMES = eps
$property_empty_nan_valid(S_return,ppropertyemptynan) /\ $call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)
$heap_owners($heap_graph(S_return),HOBJECT n_child) = 1 /\ $mn_output(S_return.EVENTS) = ptbytes_handler
S_clean_found = $mn_seek(S_return,MN_CLEAN,1000)
S_clean_found.COMPLETION = NORMAL \/ S_clean_found.COMPLETION = BUDGET
S_clean = S_clean_found[.COMPLETION = NORMAL]
S_clean.TODO = (ERROR_HANDLER_CLEAN perrorcall_entered) :: ptask_tail*
$error_cleanup_valid(S_clean,perrorcall_entered) /\ $property_empty_nan_valid(S_clean,ppropertyemptynan)
$property_empty_guard(S_clean,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_clean,n_child,$ptascii("value"))
$heap_owners($heap_graph(S_clean),HOBJECT n_child) = 1 /\ S_clean.EVENTS = S_return.EVENTS
S_resume_found = $mn_seek(S_clean,MN_RESUME,1000)
S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET
S_resume = S_resume_found[.COMPLETION = NORMAL]
S_resume.TODO = (PROPERTY_EMPTY_NAN ppropertyemptynan) :: ptask_tail*
S_resume.RESULT = KNOWN PNULL /\ S_resume.ERRORHANDLER = S_warning.ERRORHANDLER
$property_empty_nan_valid(S_resume,ppropertyemptynan) /\ ~$property_empty_capture(S_resume,ppropertyempty)
$property_empty_guard(S_resume,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_resume,n_child,$ptascii("value"))
PhpStep: S_resume ~> S_release_raw
S_release_raw.RESULT = KNOWN (PBOOL false) /\ S_release_raw.TODO = ptask_tail* /\ S_release_raw.EVENTS = S_resume.EVENTS
$heap_owners($heap_graph(S_release_raw),HOBJECT n_child) = 0
S_released = $mn_after(S_resume,S_release_raw)
S_released.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
pdestructionoperation.VALUE = KNOWN (PBOOL false) /\ pdestructionoperation.PENDING = eps
'''.strip().splitlines()

THROW = r'''
S_raised_found = $mn_seek(S_rebound,MN_RAISED,1000)
S_raised_found.COMPLETION = NORMAL \/ S_raised_found.COMPLETION = BUDGET
S_raised = S_raised_found[.COMPLETION = NORMAL]
S_raised.TODO = (THROW_SEARCH n_error) :: ptask_handler_throw*
S_raised.CURRENT = (pcallcontext_handler) /\ $throwable_live(S_raised,n_error)
$property_empty_guard(S_raised,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_raised,n_child,$ptascii("value"))
$heap_owners($heap_graph(S_raised),HOBJECT n_child) = 1
S_throw_found = $mn_seek(S_raised,MN_THROW,1000)
S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET
S_throw = S_throw_found[.COMPLETION = NORMAL]
S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*
S_throw.CURRENT = eps /\ S_throw.FRAMES = eps /\ $mn_output(S_throw.EVENTS) = ptbytes_handler
$property_empty_nan_valid(S_throw,ppropertyemptynan) /\ $error_entered_call_valid(S_throw,perrorcall_entered)
$property_empty_guard(S_throw,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_throw,n_child,$ptascii("value"))
$heap_owners($heap_graph(S_throw),HOBJECT n_child) = 1 /\ $throwable_live(S_throw,n_error)
PhpStep: S_throw ~> S_release_raw
S_release_raw.TODO = (THROW_SEARCH n_error) :: ptask_tail*
S_release_raw.COMPLETION = NORMAL /\ S_release_raw.RESULT = KNOWN PNULL /\ S_release_raw.BASE = BASE_VALUE (KNOWN PNULL)
S_release_raw.EVENTS = S_throw.EVENTS /\ S_release_raw.STORE = S_throw.STORE /\ S_release_raw.ERRORHANDLER = S_warning.ERRORHANDLER
$throwable_live(S_release_raw,n_error) /\ $heap_owners($heap_graph(S_release_raw),HOBJECT n_child) = 0
S_released = $mn_after(S_throw,S_release_raw)
S_released.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
pdestructionoperation.PENDING = (n_error) /\ pdestructionoperation.VALUE = KNOWN PNULL
'''.strip().splitlines()

FINISH = r'''
~$property_empty_guard(S_release_raw,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_release_raw,n_child,$ptascii("value"))
S_dtor_found = $mn_seek(S_released,MN_DTOR,1000)
S_dtor_found.COMPLETION = NORMAL \/ S_dtor_found.COMPLETION = BUDGET
S_dtor = S_dtor_found[.COMPLETION = NORMAL]
S_dtor.CURRENT = (pcallcontext_dtor)
$destructor_context_call(pcallcontext_dtor,S_dtor.CURRENT,S_dtor.FRAMES) = (pdestructorcall)
pdestructorcall.OBJECT = n_child /\ $mn_output(S_dtor.EVENTS) = ptbytes_handler
~$property_empty_guard(S_dtor,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_dtor,n_child,$ptascii("value"))
$mn_guard(S_dtor)
S_final = $drive_steps(S_dtor,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$mn_output(S_final.EVENTS) = ptbytes_final /\ ~(HOBJECT n_child <- S_final.ALLOCATIONS)
$lookup(S_final.ENV,$ptascii("child")) = (n_child_cell_final)
S_final.STORE[n_child_cell_final] = DEFINED PNULL
$mn_guard(S_final)
S_budget = $drive_steps(S_rebound,0)
S_budget.COMPLETION = BUDGET /\ S_budget.TODO = S_rebound.TODO /\ S_budget.EVENTS = S_rebound.EVENTS
$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final
'''.strip().splitlines()

# Derived controls alter only the reached record/value or warning registration.
DERIVED = r'''
S_invalid = S[.RESULT = KNOWN (PFLOAT 18446744073709551617)]
~$property_empty_nan_ready(S_invalid,ppropertyempty) /\ $property_empty_truth(S_invalid,PFLOAT 18446744073709551617) = eps
PhpStep: S_invalid ~> S_invalid_done
S_invalid_done.COMPLETION = UNSUPPORTED "magic empty getter result type" /\ S_invalid_done.TODO = S_invalid.TODO /\ S_invalid_done.EVENTS = S_invalid.EVENTS
ppropertyemptynan_badowner = ppropertyemptynan[.OWNER = 1]
S_badowner = S_resume[.TODO = (PROPERTY_EMPTY_NAN ppropertyemptynan_badowner) :: ptask_tail*]
~$property_empty_nan_valid(S_badowner,ppropertyemptynan_badowner) /\ ~$call_task_valid(S_badowner,PROPERTY_EMPTY_NAN ppropertyemptynan_badowner)
PhpStep: S_badowner ~> S_badowner_done
S_badowner_done.COMPLETION = UNSUPPORTED "magic empty NaN warning continuation" /\ S_badowner_done.TODO = S_badowner.TODO /\ S_badowner_done.EVENTS = S_badowner.EVENTS
~$property_empty_guard(S_badowner,n_child,$ptascii("value"))
ppropertyemptynan_badcaller = ppropertyemptynan[.CALLER = (pcallcontext_handler)]
S_badcaller = S_resume[.TODO = (PROPERTY_EMPTY_NAN ppropertyemptynan_badcaller) :: ptask_tail*]
~$property_empty_nan_valid(S_badcaller,ppropertyemptynan_badcaller)
ppropertyemptynan_badfloat = ppropertyemptynan[.FLOAT = 0]
S_badfloat = S_resume[.TODO = (PROPERTY_EMPTY_NAN ppropertyemptynan_badfloat) :: ptask_tail*]
~$property_empty_nan_valid(S_badfloat,ppropertyemptynan_badfloat)
ppropertyemptynan_badbits = ppropertyemptynan[.FLOAT = 18446744073709551616]
S_badbits = S_resume[.TODO = (PROPERTY_EMPTY_NAN ppropertyemptynan_badbits) :: ptask_tail*]
~$property_empty_nan_valid(S_badbits,ppropertyemptynan_badbits)
ppropertyemptynan_badtail = ppropertyemptynan[.TAIL = eps]
S_badtail = S_resume[.TODO = (PROPERTY_EMPTY_NAN ppropertyemptynan_badtail) :: ptask_tail*]
~$property_empty_nan_valid(S_badtail,ppropertyemptynan_badtail)
ppropertyempty_badline = ppropertyempty[.LINE = $(ppropertyempty.LINE + 1)]
ppropertyemptynan_badline = ppropertyemptynan[.EMPTY = ppropertyempty_badline]
S_badline = S_resume[.TODO = (PROPERTY_EMPTY_NAN ppropertyemptynan_badline) :: ptask_tail*]
~$property_empty_nan_valid(S_badline,ppropertyemptynan_badline)
porigin_get = ppropertyempty.GET
porigin_isset = ppropertyempty.ISSET
ppropertyempty_badsite = ppropertyempty[.SITE = porigin_get]
ppropertyemptynan_badsite = ppropertyemptynan[.EMPTY = ppropertyempty_badsite]
S_badsite = S_resume[.TODO = (PROPERTY_EMPTY_NAN ppropertyemptynan_badsite) :: ptask_tail*]
~$property_empty_nan_valid(S_badsite,ppropertyemptynan_badsite)
ppropertyempty_badmethod = ppropertyempty[.GET = porigin_isset]
ppropertyemptynan_badmethod = ppropertyemptynan[.EMPTY = ppropertyempty_badmethod]
S_badmethod = S_resume[.TODO = (PROPERTY_EMPTY_NAN ppropertyemptynan_badmethod) :: ptask_tail*]
~$property_empty_nan_valid(S_badmethod,ppropertyemptynan_badmethod)
~$error_call_valid(S_warning,perrorcall[.LEVEL = 1]) /\ ~$error_call_valid(S_warning,perrorcall[.LINE = $(perrorcall.LINE + 1)])
~$error_call_valid(S_warning,perrorcall[.MESSAGE = eps]) /\ ~$error_call_valid(S_warning,perrorcall[.EVENT = DIAGNOSTIC "Warning" eps perrorcall.LINE])
S_default = S[.ERRORHANDLER.CALLBACK = eps]
PhpStep: S_default ~> S_default_raw
S_default_warn = $mn_after(S_default,S_default_raw)
S_default_warn.TODO = (PROPERTY_EMPTY_NAN ppropertyemptynan) :: ptask_tail*
S_default_warn.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Warning" ($ptascii("unexpected NAN value was coerced to bool")) ppropertyempty.LINE]
$property_empty_nan_valid(S_default_warn,ppropertyemptynan) /\ $property_empty_guard(S_default_warn,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_default_warn,n_child,$ptascii("value"))
PhpStep: S_default_warn ~> S_default_done
S_default_done.RESULT = KNOWN (PBOOL false) /\ S_default_done.TODO = ptask_tail* /\ S_default_done.EVENTS = S_default_warn.EVENTS
$heap_owners($heap_graph(S_default_done),HOBJECT n_child) = 1
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_empty_nan_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_gate_completed']
    selected = [case for case in data['cases'] if case['id'] in ('returning', 'throwing')]
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
    out = Path(tempfile.mkdtemp(prefix='magic-empty-nan-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    report = {'revision': revision, 'inputs': before, 'profile': profile, 'module_count': len(modules),
              'mode': 'SL', 'cache': False, 'det': True, 'records': [], 'fixtures': [],
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
            handler_output = output[:output.index('D|')]
            setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $mn_seek(S_initial,MN_RV,1000)', r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]', 'ptbytes_handler = $ptascii(' + json.dumps(handler_output) + ')',
                     'ptbytes_final = $ptascii(' + json.dumps(output) + ')']
            reached = setup + COMMON + [f'ppropertyempty.LINE = {case["warning_line"]}'] + (RETURN if name == 'returning' else THROW) + FINISH
            if name == 'throwing':
                reached += ['$lookup(S_final.ENV,$ptascii("caught")) = (n_caught_cell)', 'S_final.STORE[n_caught_cell] = DEFINED (POBJECT n_error)']
            derived = DERIVED if name == 'returning' else []
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
