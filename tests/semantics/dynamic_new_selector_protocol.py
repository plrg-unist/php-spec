"""Check dynamic NEW selector disposal before allocation, access and arguments."""
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
syntax pdsstage = DS_CLASS | DS_START | DS_DTOR nat | DS_CATCH | DS_CTOR nat
dec $ds_output(pevent*) : ptbytes
def $ds_output(eps) = eps
def $ds_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $ds_output(pevent*)
dec $ds_stage(pstate,pdsstage) : bool
def $ds_stage(S,DS_CLASS) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (DYNAMIC_NEW_CLASS z z_fetch) :: ptask_tail*
def $ds_stage(S,DS_START) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (DYNAMIC_NEW_START pdynamicnew) :: ptask_tail*
def $ds_stage(S,DS_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $ds_stage(S,DS_CATCH) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask_tail*
def $ds_stage(S,DS_CTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $context_target(pcallcontext) = METHOD_TARGET n porigin
  -- if pcallcontext.NAME = $ptascii("Public103::__construct")
def $ds_stage(S,pdsstage) = false -- otherwise
dec $ds_seek(pstate,pdsstage,nat) : pstate
def $ds_seek(S,pdsstage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $ds_stage(S,pdsstage) \/ n = 0
def $ds_seek(S,pdsstage,n) = $ds_seek($drive_steps(S[.COMPLETION = NORMAL],1),pdsstage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$ds_stage(S,pdsstage) /\ $(n > 0)
def $ds_seek(S,pdsstage,n) = $ds_seek($drive_steps(S,1),pdsstage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $ds_seek(S,pdsstage,n) = S -- otherwise
dec $ds_after(pstate,pstate) : pstate
def $ds_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $ds_guard(pstate) : bool
def $ds_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $gc_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''

def lines(text): return [line for line in text.strip().splitlines() if line]

COMMON = lines(r'''
$ds_stage(S,DS_CLASS)
S.TODO = (DYNAMIC_NEW_CLASS z_new z_fetch) :: ptask_tail*
S.RESULT = KNOWN (POBJECT n_selector)
S.ORIGIN = (porigin_site)
$origin_node(S.SOURCES,porigin_site) = (NExprNew expression (SEQUENCE phpType7*) metadata)
$dynamic_new_value_name(S,porigin_site,POBJECT n_selector) = (ptbytes_class)
pdynamicnew = $dynamic_new_record(S,porigin_site,POBJECT n_selector,ptbytes_class,z_new,z_fetch)
$dynamic_new_valid(S,pdynamicnew)
$dynamic_new_live_value(S,POBJECT n_selector)
HOBJECT n_selector <- S.ALLOCATIONS
$heap_owners($heap_graph(S),HOBJECT n_selector) = n_selector_owners
$ds_output(S.EVENTS) = ptbytes_initial
$ds_guard(S)
S_clear = S[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]
PhpStep: S ~> S_queued
S_queued = S_clear[.TODO = (DYNAMIC_NEW_START pdynamicnew) :: ptask_tail*]
S_queued.OBJECTS = S.OBJECTS /\ S_queued.DESTRUCTION.CALLED = S.DESTRUCTION.CALLED
$task_nodes(DYNAMIC_NEW_START pdynamicnew) = eps
$call_task_valid(S_queued,DYNAMIC_NEW_START pdynamicnew)
$heap_owners($heap_graph(S_queued),HOBJECT n_selector) = n_after_owners
S_disposing = $ds_after(S,S_queued)
S_budget_start = S
''')

SOLE_D = lines(r'''
S_dtor_found = $ds_seek(S_disposing,DS_DTOR n_selector,1500)
S_dtor_found.COMPLETION = NORMAL \/ S_dtor_found.COMPLETION = BUDGET
S_dtor = S_dtor_found[.COMPLETION = NORMAL]
$ds_stage(S_dtor,DS_DTOR n_selector)
S_dtor.CURRENT = (pcallcontext_dtor)
$destructor_context_call(pcallcontext_dtor,S_dtor.CURRENT,S_dtor.FRAMES) = (pdestructorcall)
pdestructorcall.PENDING = eps
pdestructorcall.OPERATION = (pdestructionoperation)
pdestructionoperation.PENDING = eps /\ pdestructionoperation.COMPLETION = NORMAL
pdestructionoperation.VALUE = KNOWN PNULL
pdestructionoperation.SOURCE = DYNAMIC_NEW_CLASS z_new z_fetch
S_dtor.OBJECTS = S.OBJECTS
S_dtor.DESTRUCTION.CALLED = S.DESTRUCTION.CALLED ++ [n_selector]
$ds_output(S_dtor.EVENTS) = ptbytes_initial
S_dtor.FRAMES = pframe_dtor :: eps
S_saved = $constant_frame_view(S_dtor,pframe_dtor,eps)
S_saved.ORIGIN = (porigin_site)
$dynamic_new_start_valid(S_saved,pdynamicnew)
$call_task_valid(S_saved,DYNAMIC_NEW_START pdynamicnew)
$ds_guard(S_dtor)
''')

RESUME = lines(r'''
S_resume_found = $ds_seek(S_dtor,DS_START,1500)
S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET
S_resume = S_resume_found[.COMPLETION = NORMAL]
S_resume.TODO = (DYNAMIC_NEW_START pdynamicnew) :: ptask_tail*
S_resume.CURRENT = eps /\ S_resume.FRAMES = eps
$ds_output(S_resume.EVENTS) = ptbytes_initial ++ ptbytes_destructor
S_resume.OBJECTS = S.OBJECTS
S_resume.DESTRUCTION.CALLED = S.DESTRUCTION.CALLED ++ [n_selector]
~(HOBJECT n_selector <- S_resume.ALLOCATIONS)
~(HOBJECT n_selector <- $gc_nodes(S_resume.GC.BUFFER))
~$dynamic_new_live_value(S_resume,POBJECT n_selector)
$dynamic_new_value_name(S_resume,porigin_site,POBJECT n_selector) = (ptbytes_class)
$dynamic_new_start_valid(S_resume,pdynamicnew)
$call_task_valid(S_resume,DYNAMIC_NEW_START pdynamicnew)
$ds_guard(S_resume)
''')

ACCESS = lines(r'''
n_new = |S.OBJECTS|
PhpStep: S_resume ~> S_access
S_access.COMPLETION = THROWN "Error" ($ptascii("Call to private Private103::__construct() from global scope")) z_fetch
|S_access.OBJECTS| = $(|S.OBJECTS| + 1)
S_access.DESTRUCTION.CALLED = S_resume.DESTRUCTION.CALLED ++ [n_new]
S_raised = $ds_after(S_resume,S_access)
S_catch_found = $ds_seek(S_raised,DS_CATCH,1500)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_catch n_index n_access) :: ptask_catch*
S_catch.OBJECTS[n_access] = THROWABLE pthrowable_access
pthrowable_access.KIND = "Error"
S_catch.STORE[n_answer] = DEFINED (PINT 42)
$ds_guard(S_catch)
''')

THROW = lines(r'''
S_catch_found = $ds_seek(S_dtor,DS_CATCH,1500)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_catch n_index n_error) :: ptask_catch*
S_catch.OBJECTS[n_error] = THROWABLE pthrowable_error
pthrowable_error.KIND = "Exception" /\ $throwable_previous_id(S_catch,n_error) = eps
S_catch.OBJECTS = S.OBJECTS
S_catch.DESTRUCTION.CALLED = S.DESTRUCTION.CALLED ++ [n_selector]
~(HOBJECT n_selector <- S_catch.ALLOCATIONS)
S_catch.STORE[n_answer] = DEFINED (PINT 42)
$ds_output(S_catch.EVENTS) = ptbytes_initial ++ $ptascii("D|")
$ds_guard(S_catch)
S_end = S_catch
''')

HELD = lines(r'''
S_resume_found = $ds_seek(S_disposing,DS_START,1500)
S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET
S_resume = S_resume_found[.COMPLETION = NORMAL]
S_resume.TODO = (DYNAMIC_NEW_START pdynamicnew) :: ptask_tail*
$ds_output(S_resume.EVENTS) = ptbytes_initial
S_resume.OBJECTS = S.OBJECTS /\ S_resume.DESTRUCTION.CALLED = S.DESTRUCTION.CALLED
HOBJECT n_selector <- S_resume.ALLOCATIONS
$heap_owners($heap_graph(S_resume),HOBJECT n_selector) = 1
$dynamic_new_start_valid(S_resume,pdynamicnew)
$ds_guard(S_resume)
''')

HELD_LATE = lines(r'''
n_access =/= n_error
HOBJECT n_selector <- S_catch.ALLOCATIONS
$heap_owners($heap_graph(S_catch),HOBJECT n_selector) = 1
$ds_output(S_catch.EVENTS) = ptbytes_initial
S_late_found = $ds_seek(S_catch,DS_DTOR n_selector,1500)
S_late_found.COMPLETION = NORMAL \/ S_late_found.COMPLETION = BUDGET
S_late = S_late_found[.COMPLETION = NORMAL]
$ds_stage(S_late,DS_DTOR n_selector)
S_late.CURRENT = (pcallcontext_late)
$destructor_context_call(pcallcontext_late,S_late.CURRENT,S_late.FRAMES) = (pdestructorcall_late)
pdestructorcall_late.PENDING = eps
pdestructorcall_late.OPERATION = (pdestructionoperation_late)
pdestructionoperation_late.PENDING = eps
$ds_output(S_late.EVENTS) = ptbytes_initial ++ $ptascii("E|F|")
$ds_guard(S_late)
S_second_found = $ds_seek(S_late,DS_CATCH,1500)
S_second_found.COMPLETION = NORMAL \/ S_second_found.COMPLETION = BUDGET
S_second = S_second_found[.COMPLETION = NORMAL]
S_second.TODO = (CATCH_BIND porigin_second n_second n_error) :: ptask_second*
S_second.OBJECTS[n_error] = THROWABLE pthrowable_error
$throwable_previous_id(S_second,n_error) = eps
S_second.STORE[n_answer] = DEFINED (PINT 42)
~(HOBJECT n_selector <- S_second.ALLOCATIONS)
$ds_guard(S_second)
S_end = S_second
''')

PUBLIC = lines(r'''
n_new = |S.OBJECTS|
PhpStep: S_resume ~> S_started
S_started.COMPLETION = NORMAL
|S_started.OBJECTS| = $(|S.OBJECTS| + 1)
HOBJECT n_new <- S_started.ALLOCATIONS
~(HOBJECT n_selector <- S_started.ALLOCATIONS)
S_started.DESTRUCTION.CALLED = S_resume.DESTRUCTION.CALLED
$dynamic_new_valid(S_started,pdynamicnew)
S_received_found = $ds_seek($ds_after(S_resume,S_started),DS_CTOR n_new,1500)
S_received_found.COMPLETION = NORMAL \/ S_received_found.COMPLETION = BUDGET
S_received = S_received_found[.COMPLETION = NORMAL]
$ds_stage(S_received,DS_CTOR n_new)
S_received.CURRENT = (pcallcontext_ctor)
pcallcontext_ctor.ARGC = 1
$lookup(S_received.ENV,$ptascii("number")) = (n_number)
S_received.STORE[n_number] = DEFINED (PINT 99)
$ds_output(S_received.EVENTS) = ptbytes_initial ++ ptbytes_destructor ++ $ptascii("A|")
$ds_guard(S_received)
S_end = S_received
''')

FINISH = lines(r'''
S_final = $drive_steps(S_end,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$ds_output(S_final.EVENTS) = ptbytes_final
$ds_guard(S_final)
S_budget = $drive_steps(S_budget_start,0)
S_budget.COMPLETION = BUDGET /\ S_budget.TODO = S_budget_start.TODO /\ S_budget.EVENTS = S_budget_start.EVENTS
$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final
''')

REFUSALS = lines(r'''
pdynamicnew_bad = pdynamicnew[.FETCHLINE = $(z_fetch + 1)]
S_bad = S_resume[.TODO = (DYNAMIC_NEW_START pdynamicnew_bad) :: ptask_tail*]
~$dynamic_new_start_valid(S_bad,pdynamicnew_bad)
PhpStep: S_bad ~> S_bad_done
S_bad_done.COMPLETION = UNSUPPORTED "invalid dynamic new start"
S_origin = S_resume[.ORIGIN = eps]
~$call_task_valid(S_origin,DYNAMIC_NEW_START pdynamicnew)
PhpStep: S_origin ~> S_origin_done
S_origin_done.COMPLETION = UNSUPPORTED "invalid dynamic new start"
''')

NONOWNING = lines(r'''
poperand_borrowed = VARIABLE ($ptascii("held")) z_fetch
$operand_nodes(poperand_borrowed) = eps
$dynamic_new_selected_start(S_clear,poperand_borrowed,pdynamicnew,phpType7*) = $dynamic_new_start(S_clear[.TODO = (DYNAMIC_NEW_FINISH pdynamicnew) :: ptask_tail*],pdynamicnew,phpType7*)
$operand_nodes(KNOWN (PSTRING ptbytes_class)) = eps
$dynamic_new_selected_start(S_clear,KNOWN (PSTRING ptbytes_class),pdynamicnew,phpType7*) = $dynamic_new_start(S_clear[.TODO = (DYNAMIC_NEW_FINISH pdynamicnew) :: ptask_tail*],pdynamicnew,phpType7*)
''')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', action='append', choices=('normal', 'throwing', 'held', 'public'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'dynamic_new_selector_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_gate_completed']
    assert [case['id'] for case in data['cases']] == ['normal', 'throwing', 'held', 'public']
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
    out = Path(tempfile.mkdtemp(prefix='dynamic-new-selector-protocol-', dir=ROOT / '.tools'))
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
            initial_output = {'normal':'N|B|S|','throwing':'X|B|S|','held':'H|B|S|','public':'P|C0|S|'}[name]
            reached = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                'S_found = $ds_seek(S_initial,DS_CLASS,1500)', r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                'S = S_found[.COMPLETION = NORMAL]',
                'ptbytes_initial = $ptascii(' + json.dumps(initial_output) + ')',
                'ptbytes_final = $ptascii(' + json.dumps(output) + ')',
                'n_selector_owners = ' + ('2' if name == 'held' else '1'),
                'n_after_owners = ' + ('1' if name == 'held' else '0')]
            reached += COMMON + [fr'z_new = {case["new_line"]} /\ z_fetch = {case["new_line"]}']
            if name != 'public':
                reached += ['$lookup(S.ENV,$ptascii("error")) = (n_error_cell)', 'S.STORE[n_error_cell] = DEFINED (POBJECT n_error)',
                            '$lookup(S.ENV,$ptascii("answer")) = (n_answer)', 'S.STORE[n_answer] = DEFINED (PINT 42)']
            derived = []
            if name in ('normal','throwing','public'):
                reached += SOLE_D
                if name == 'throwing':
                    reached += THROW
                else:
                    reached += ['ptbytes_destructor = $ptascii(' + json.dumps('D0|d|' if name == 'public' else 'D|d|') + ')'] + RESUME
                    reached += PUBLIC if name == 'public' else ACCESS + ['S_end = S_catch']
                    if name == 'normal': derived = REFUSALS
            else:
                reached += HELD + ACCESS + HELD_LATE
                derived = NONOWNING
            reached += FINISH
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
