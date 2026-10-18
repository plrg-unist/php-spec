"""Check mutable-empty getter array retirement before saved-receiver release."""
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

syntax pmutablervstage = MM_RV | MM_RESUME | MM_RAISED | MM_DTOR nat | MM_CATCH
dec $mm_output(pevent*) : ptbytes
def $mm_output(eps) = eps
def $mm_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $mm_output(pevent*)
dec $mm_stage(pstate,pmutablervstage) : bool
def $mm_stage(S,MM_RV) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask*
def $mm_stage(S,MM_RESUME) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask*
def $mm_stage(S,MM_RAISED) = true
  -- if S.CURRENT =/= eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
def $mm_stage(S,MM_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $mm_stage(S,MM_CATCH) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask*
def $mm_stage(S,pmutablervstage) = false -- otherwise
dec $mm_seek(pstate,pmutablervstage,nat) : pstate
def $mm_seek(S,pmutablervstage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $mm_stage(S,pmutablervstage) \/ n = 0
def $mm_seek(S,pmutablervstage,n) = $mm_seek($drive_steps(S[.COMPLETION = NORMAL],1),pmutablervstage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$mm_stage(S,pmutablervstage) /\ $(n > 0)
def $mm_seek(S,pmutablervstage,n) = $mm_seek($drive_steps(S,1),pmutablervstage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $mm_seek(S,pmutablervstage,n) = S -- otherwise
dec $mm_after(pstate,pstate) : pstate
def $mm_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $mm_guard(pstate) : bool
def $mm_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $gc_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''

COMMON = r'''
$mm_stage(S,MM_RV)
S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail*
n_child = ppropertyempty.OBJECT
S.RESULT = KNOWN (PARRAY n_rv)
HARRAY n_rv <- S.ALLOCATIONS /\ S.ARRAYS[n_rv].ITEMS = eps
S.ARRAYS[n_rv].NEXT = 1 /\ S.ARRAYS[n_rv].SERIAL = 1
~$array_immutable(S,n_rv) /\ $gc_possible_root(S,HARRAY n_rv)
HARRAY n_rv <- $gc_nodes(S.GC.BUFFER)
S.CURRENT = eps /\ S.FRAMES = eps /\ S.ORIGIN = (ppropertyempty.SITE)
$lookup(S.ENV,$ptascii("child")) = (n_child_cell)
S.STORE[n_child_cell] = DEFINED PNULL
$property_empty_valid(S,ppropertyempty) /\ ~$property_empty_capture(S,ppropertyempty)
$property_empty_rv_ready(S,ppropertyempty) /\ $property_empty_truth(S,PARRAY n_rv) = eps
$heap_owners($heap_graph(S),HOBJECT n_child) = 1 /\ $heap_owners($heap_graph(S),HARRAY n_rv) = n_rv_owners
$property_empty_guard(S,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S,n_child,$ptascii("value"))
$mm_output(S.EVENTS) = ptbytes_before_dtor /\ $mm_guard(S)
PhpStep: S ~> S_phase_raw
S_phase_raw.TODO = (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask_tail*
ppropertyemptyrv.EMPTY = ppropertyempty /\ ppropertyemptyrv.OWNER = 0 /\ ppropertyemptyrv.CALLER = eps /\ ppropertyemptyrv.TAIL = ptask_tail*
S_phase_raw.RESULT = KNOWN (PBOOL true) /\ S_phase_raw.EVENTS = S.EVENTS
$task_nodes(PROPERTY_EMPTY_RV ppropertyemptyrv) = [HOBJECT n_child]
$heap_owners($heap_graph(S_phase_raw),HARRAY n_rv) = $(n_rv_owners - 1)
S_disposing = $mm_after(S,S_phase_raw)
S_disposing.DESTRUCTION.OPERATIONS = pdestructionoperation_rv :: pdestructionoperation_old*
pdestructionoperation_rv.VALUE = KNOWN (PBOOL true) /\ pdestructionoperation_rv.PENDING = eps
S_resume_found = $mm_seek(S_disposing,MM_RESUME,1000)
S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET
S_resume = S_resume_found[.COMPLETION = NORMAL]
S_resume.TODO = (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask_tail*
S_resume.CURRENT = eps /\ S_resume.FRAMES = eps /\ S_resume.RESULT = KNOWN (PBOOL true)
S_resume.EVENTS = S.EVENTS /\ S_resume.DESTRUCTION.CALLED = S.DESTRUCTION.CALLED
$heap_owners($heap_graph(S_resume),HOBJECT n_child) = 1
$property_empty_rv_valid(S_resume,ppropertyemptyrv) /\ ~$property_empty_capture(S_resume,ppropertyempty)
$property_empty_guard(S_resume,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_resume,n_child,$ptascii("value"))
$mm_guard(S_resume)
'''.strip().splitlines()

SOLE = r'''
~(HARRAY n_rv <- S_resume.ALLOCATIONS) /\ ~(HARRAY n_rv <- $gc_nodes(S_resume.GC.BUFFER))
$heap_owners($heap_graph(S_resume),HARRAY n_rv) = 0
'''.strip().splitlines()

SHARED = r'''
HARRAY n_rv <- S_resume.ALLOCATIONS /\ HARRAY n_rv <- $gc_nodes(S_resume.GC.BUFFER)
$heap_owners($heap_graph(S_resume),HARRAY n_rv) = 1
$lookup(S_resume.ENV,$ptascii("held")) = (n_held_cell)
S_resume.STORE[n_held_cell] = DEFINED (PARRAY n_rv)
'''.strip().splitlines()

RELEASE = r'''
PhpStep: S_resume ~> S_release_raw
S_release_raw.TODO = ptask_tail* /\ S_release_raw.RESULT = KNOWN (PBOOL true)
S_release_raw.EVENTS = S_resume.EVENTS /\ S_release_raw.STORE = S_resume.STORE
$heap_owners($heap_graph(S_release_raw),HOBJECT n_child) = 0
~$property_empty_guard(S_release_raw,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_release_raw,n_child,$ptascii("value"))
S_released = $mm_after(S_resume,S_release_raw)
S_released.DESTRUCTION.OPERATIONS = pdestructionoperation_receiver :: pdestructionoperation_receiver_tail*
pdestructionoperation_receiver.VALUE = KNOWN (PBOOL true) /\ pdestructionoperation_receiver.PENDING = eps
S_dtor_found = $mm_seek(S_released,MM_DTOR n_child,1000)
S_dtor_found.COMPLETION = NORMAL \/ S_dtor_found.COMPLETION = BUDGET
S_dtor = S_dtor_found[.COMPLETION = NORMAL]
$mm_stage(S_dtor,MM_DTOR n_child)
$mm_output(S_dtor.EVENTS) = ptbytes_before_dtor
~$property_empty_guard(S_dtor,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_dtor,n_child,$ptascii("value"))
$mm_guard(S_dtor)
'''.strip().splitlines()

FINISH = r'''
S_final = $drive_steps(S_dtor,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$mm_output(S_final.EVENTS) = ptbytes_final
~(HOBJECT n_child <- S_final.ALLOCATIONS) /\ ~(HARRAY n_rv <- S_final.ALLOCATIONS) /\ ~(HARRAY n_rv <- $gc_nodes(S_final.GC.BUFFER))
$lookup(S_final.ENV,$ptascii("child")) = (n_child_final)
S_final.STORE[n_child_final] = DEFINED PNULL
$lookup(S_final.ENV,$ptascii("held")) = (n_held_final)
S_final.STORE[n_held_final] = DEFINED PNULL
$mm_guard(S_final)
S_budget = $drive_steps(S_resume,0)
S_budget.COMPLETION = BUDGET /\ S_budget.TODO = S_resume.TODO /\ S_budget.EVENTS = S_resume.EVENTS
$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final
'''.strip().splitlines()

THROW = r'''
S_raised_found = $mm_seek(S_dtor,MM_RAISED,1000)
S_raised_found.COMPLETION = NORMAL \/ S_raised_found.COMPLETION = BUDGET
S_raised = S_raised_found[.COMPLETION = NORMAL]
S_raised.TODO = (THROW_SEARCH n_error) :: ptask_throw*
S_raised.CURRENT = (pcallcontext_dtor)
$throwable_live(S_raised,n_error)
~(HARRAY n_rv <- S_raised.ALLOCATIONS) /\ ~(HARRAY n_rv <- $gc_nodes(S_raised.GC.BUFFER))
~$property_empty_guard(S_raised,n_child,$ptascii("value"))
S_catch_found = $mm_seek(S_raised,MM_CATCH,1000)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_try n_catch n_error) :: ptask_catch*
$throwable_live(S_catch,n_error) /\ $mm_output(S_catch.EVENTS) = ptbytes_before_dtor ++ $ptascii("D|")
~(HOBJECT n_child <- S_catch.ALLOCATIONS) /\ ~(HARRAY n_rv <- S_catch.ALLOCATIONS)
PhpStep: S_catch ~> S_catch_raw
$lookup(S_catch_raw.ENV,$ptascii("caught")) = (n_caught_cell)
S_catch_raw.STORE[n_caught_cell] = DEFINED (POBJECT n_error)
S_catch_done = $mm_after(S_catch,S_catch_raw)
S_catch_done.COMPLETION = NORMAL /\ $throwable_live(S_catch_done,n_error) /\ $mm_guard(S_catch_done)
$drive_steps(S_catch_done,10000) = S_final
'''.strip().splitlines()

DERIVED = r'''
S_bad_cache = S_resume[.RESULT = KNOWN PNULL]
$property_empty_rv_valid(S_bad_cache,ppropertyemptyrv)
PhpStep: S_bad_cache ~> S_bad_cache_done
S_bad_cache_done.COMPLETION = UNSUPPORTED "magic empty object RV continuation" /\ S_bad_cache_done.EVENTS = S_resume.EVENTS
S_bad_cache_done.STORE = S_resume.STORE /\ S_bad_cache_done.ALLOCATIONS = S_resume.ALLOCATIONS
parray_nonempty = S.ARRAYS[n_rv][.ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]]
S_nonempty = S[.ARRAYS[n_rv] = parray_nonempty]
$property_empty_rv_ready(S_nonempty,ppropertyempty) /\ $property_empty_truth(S_nonempty,PARRAY n_rv) = eps
PhpStep: S_nonempty ~> S_nonempty_raw
S_nonempty_raw.TODO = (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask_tail*
S_nonempty_raw.RESULT = KNOWN (PBOOL false) /\ S_nonempty_raw.EVENTS = S.EVENTS
S_nonempty_after = $mm_after(S_nonempty,S_nonempty_raw)
S_nonempty_found = $mm_seek(S_nonempty_after,MM_RESUME,1000)
S_nonempty_found.COMPLETION = NORMAL \/ S_nonempty_found.COMPLETION = BUDGET
S_nonempty_resume = S_nonempty_found[.COMPLETION = NORMAL]
S_nonempty_resume.TODO = (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask_tail*
S_nonempty_resume.RESULT = KNOWN (PBOOL false) /\ S_nonempty_resume.EVENTS = S.EVENTS
$property_empty_rv_valid(S_nonempty_resume,ppropertyemptyrv) /\ $mm_guard(S_nonempty_resume)
PhpStep: S_nonempty_resume ~> S_nonempty_done
S_nonempty_done.RESULT = KNOWN (PBOOL false) /\ S_nonempty_done.TODO = ptask_tail* /\ S_nonempty_done.EVENTS = S.EVENTS
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', choices=('sole', 'shared', 'throwing'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_empty_mutable_array_rv_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_gate_completed']
    for diagnostic in data['native_gc_diagnostic']['cases']:
        original = next(case for case in data['cases'] if case['id'] == diagnostic['id'].removeprefix('gc-'))
        prefix = "echo 'N:';" if original['id'] == 'sole' else "echo 'H:';"
        replacement = "echo 'S:';" if original['id'] == 'sole' else prefix
        bridged = original['source'].replace(prefix, replacement).replace("echo 'D|';", "echo 'D:', gc_status()['roots'], '|';")
        assert bridged == diagnostic['source']
        assert hashlib.sha256(diagnostic['source'].encode()).hexdigest() == diagnostic['source_sha256']
    assert data['native_gc_diagnostic']['source_agreements'] == 0
    selected = [case for case in data['cases'] if case['id'] in ('sole', 'shared', 'throwing')]
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
    out = Path(tempfile.mkdtemp(prefix='magic-empty-mutable-array-rv-protocol-', dir=ROOT / '.tools'))
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
            before_dtor = output[:output.index('D|')]
            setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $mm_seek(S_initial,MM_RV,1000)', r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]',
                     'n_rv_owners = ' + str(case['array_owners_at_rv']),
                     'ptbytes_before_dtor = $ptascii(' + json.dumps(before_dtor) + ')',
                     'ptbytes_final = $ptascii(' + json.dumps(output) + ')']
            lifetime = SHARED if name == 'shared' else SOLE
            at_dtor = [
                'HARRAY n_rv <- S_dtor.ALLOCATIONS /\\ HARRAY n_rv <- $gc_nodes(S_dtor.GC.BUFFER)',
                '$heap_owners($heap_graph(S_dtor),HARRAY n_rv) = 1',
            ] if name == 'shared' else [
                '~(HARRAY n_rv <- S_dtor.ALLOCATIONS) /\\ ~(HARRAY n_rv <- $gc_nodes(S_dtor.GC.BUFFER))',
            ]
            reached = setup + COMMON + lifetime + RELEASE + at_dtor + FINISH + [f'ppropertyempty.LINE = {case["empty_line"]}']
            if name == 'throwing':
                reached += THROW
            derived = DERIVED if name == 'sole' else []
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
