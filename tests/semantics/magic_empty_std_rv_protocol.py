"""Check stdClass empty getter RV child disposal and captured receiver."""
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


syntax pemptystdstage = MS_RV | MS_STORAGE nat | MS_REBOUND ptbytes | MS_RESUME | MS_RAISED | MS_THROW | MS_DTOR nat | MS_CATCH
dec $ms_output(pevent*) : ptbytes
def $ms_output(eps) = eps
def $ms_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $ms_output(pevent*)
dec $ms_stage(pstate,pemptystdstage) : bool
def $ms_stage(S,MS_RV) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask*
def $ms_stage(S,MS_STORAGE n) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*
  -- if pinstancestorage.OBJECT = n
def $ms_stage(S,MS_REBOUND ptbytes) = true
  -- if S.CURRENT =/= eps
  -- if $ms_output(S.EVENTS) = ptbytes
def $ms_stage(S,MS_RESUME) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask*
def $ms_stage(S,MS_RAISED) = true
  -- if S.CURRENT =/= eps
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
def $ms_stage(S,MS_THROW) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask*
def $ms_stage(S,MS_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $ms_stage(S,MS_CATCH) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask*
def $ms_stage(S,pemptystdstage) = false -- otherwise
dec $ms_seek(pstate,pemptystdstage,nat) : pstate
def $ms_seek(S,pemptystdstage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $ms_stage(S,pemptystdstage) \/ n = 0
def $ms_seek(S,pemptystdstage,n) = $ms_seek($drive_steps(S[.COMPLETION = NORMAL],1),pemptystdstage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$ms_stage(S,pemptystdstage) /\ $(n > 0)
def $ms_seek(S,pemptystdstage,n) = $ms_seek($drive_steps(S,1),pemptystdstage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $ms_seek(S,pemptystdstage,n) = S -- otherwise
dec $ms_after(pstate,pstate) : pstate
def $ms_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $ms_guard(pstate) : bool
def $ms_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''

COMMON = r'''
$ms_stage(S,MS_RV)
S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail*
n_child = ppropertyempty.OBJECT
S.RESULT = KNOWN (POBJECT n_rv)
S.OBJECTS[n_rv] = STDINSTANCE
$objectprops_at(S.OBJECTPROPS,n_rv) = (ppropertyslot_rv*)
$property_slot_at(ppropertyslot_rv*,$ptascii("payload")) = (ppropertyslot_payload)
ppropertyslot_payload.STATE = PROP_VALUE (DIRECT (POBJECT n_payload))
ppropertyslot_payload.DECL = eps /\ n_child =/= n_rv /\ n_child =/= n_payload /\ n_rv =/= n_payload
S.OBJECTS[n_payload] = INSTANCE porigin_payload
S.CURRENT = eps /\ S.FRAMES = eps /\ S.ORIGIN = (ppropertyempty.SITE)
$property_empty_rv_ready(S,ppropertyempty) /\ $property_empty_truth(S,POBJECT n_rv) = eps
$property_empty_capture(S,ppropertyempty) /\ $ms_guard(S)
$heap_owners($heap_graph(S),HOBJECT n_child) = 2 /\ $heap_owners($heap_graph(S),HOBJECT n_rv) = 1 /\ $heap_owners($heap_graph(S),HOBJECT n_payload) = 1
PhpStep: S ~> S_phase_raw
S_phase_raw.TODO = (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask_tail*
ppropertyemptyrv.EMPTY = ppropertyempty /\ ppropertyemptyrv.OWNER = 0 /\ ppropertyemptyrv.CALLER = eps /\ ppropertyemptyrv.TAIL = ptask_tail*
S_phase_raw.RESULT = KNOWN (PBOOL false) /\ S_phase_raw.EVENTS = S.EVENTS
$task_nodes(PROPERTY_EMPTY_RV ppropertyemptyrv) = [HOBJECT n_child]
$heap_owners($heap_graph(S_phase_raw),HOBJECT n_rv) = 0
S_disposing = $ms_after(S,S_phase_raw)
S_storage_found = $ms_seek(S_disposing,MS_STORAGE n_rv,1000)
S_storage_found.COMPLETION = NORMAL \/ S_storage_found.COMPLETION = BUDGET
S_storage = S_storage_found[.COMPLETION = NORMAL]
S_storage.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_storage*
pinstancestorage.OBJECT = n_rv /\ pinstancestorage.NEXT = 0 /\ pinstancestorage.SLOTS = ppropertyslot_rv*
$instance_storage_valid(S_storage,pinstancestorage) /\ $instance_storage_freeing(S_storage,n_rv)
$property_empty_rv_valid(S_storage,ppropertyemptyrv) /\ $property_empty_guard(S_storage,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_storage,n_child,$ptascii("value"))
$heap_owners($heap_graph(S_storage),HOBJECT n_rv) = 1 /\ $heap_owners($heap_graph(S_storage),HOBJECT n_payload) = 1
$ms_guard(S_storage)
S_payload_found = $ms_seek(S_storage,MS_DTOR n_payload,1000)
S_payload_found.COMPLETION = NORMAL \/ S_payload_found.COMPLETION = BUDGET
S_payload = S_payload_found[.COMPLETION = NORMAL]
$ms_stage(S_payload,MS_DTOR n_payload)
S_payload.CURRENT = (pcallcontext_payload)
S_payload.FRAMES = [pframe_payload]
$instance_storage_for(S_payload,n_rv) = (pinstancestorage_payload)
pinstancestorage_payload.OBJECT = n_rv /\ pinstancestorage_payload.NEXT = 1
$instance_storage_basic(S_payload,pinstancestorage_payload) /\ $instance_storage_freeing(S_payload,n_rv)
$heap_owners($heap_graph(S_payload),HOBJECT n_rv) = 1
$property_empty_guard(S_payload,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_payload,n_child,$ptascii("value"))
$ms_guard(S_payload)
S_rebound_found = $ms_seek(S_payload,MS_REBOUND ptbytes_rebound,1000)
S_rebound_found.COMPLETION = NORMAL \/ S_rebound_found.COMPLETION = BUDGET
S_rebound = S_rebound_found[.COMPLETION = NORMAL]
$ms_stage(S_rebound,MS_REBOUND ptbytes_rebound)
S_rebound.CURRENT = (pcallcontext_payload)
S_rebound.FRAMES = [pframe_rebound]
S_caller = $constant_frame_scope(S_rebound,pframe_rebound,eps)
$lookup(S_caller.ENV,$ptascii("child")) = (n_child_cell)
S_caller.STORE[n_child_cell] = DEFINED PNULL
$property_empty_rv_valid(S_caller,ppropertyemptyrv) /\ ~$property_empty_capture(S_caller,ppropertyempty)
$property_empty_guard(S_rebound,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_rebound,n_child,$ptascii("value"))
$instance_storage_freeing(S_rebound,n_rv) /\ $heap_owners($heap_graph(S_rebound),HOBJECT n_rv) = 1
$heap_owners($heap_graph(S_rebound),HOBJECT n_child) = 1 /\ $ms_guard(S_rebound)
'''.strip().splitlines()

RETURN = r'''
S_resume_found = $ms_seek(S_rebound,MS_RESUME,1000)
S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET
S_resume = S_resume_found[.COMPLETION = NORMAL]
S_resume.TODO = (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask_tail*
S_resume.CURRENT = eps /\ S_resume.FRAMES = eps /\ S_resume.RESULT = KNOWN (PBOOL false)
~(HOBJECT n_rv <- S_resume.ALLOCATIONS) /\ ~(HOBJECT n_payload <- S_resume.ALLOCATIONS) /\ $heap_owners($heap_graph(S_resume),HOBJECT n_child) = 1
$property_empty_rv_valid(S_resume,ppropertyemptyrv) /\ ~$property_empty_capture(S_resume,ppropertyempty)
$property_empty_guard(S_resume,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_resume,n_child,$ptascii("value"))
PhpStep: S_resume ~> S_release_raw
S_release_raw.RESULT = KNOWN (PBOOL false) /\ S_release_raw.TODO = ptask_tail* /\ S_release_raw.EVENTS = S_resume.EVENTS
$heap_owners($heap_graph(S_release_raw),HOBJECT n_child) = 0
S_released = $ms_after(S_resume,S_release_raw)
S_released.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
pdestructionoperation.VALUE = KNOWN (PBOOL false) /\ pdestructionoperation.PENDING = eps
'''.strip().splitlines()

THROW = r'''
S_raised_found = $ms_seek(S_rebound,MS_RAISED,1000)
S_raised_found.COMPLETION = NORMAL \/ S_raised_found.COMPLETION = BUDGET
S_raised = S_raised_found[.COMPLETION = NORMAL]
S_raised.TODO = (THROW_SEARCH n_error) :: ptask_rv_throw*
S_raised.CURRENT = (pcallcontext_payload) /\ $throwable_live(S_raised,n_error)
$property_empty_guard(S_raised,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_raised,n_child,$ptascii("value"))
$heap_owners($heap_graph(S_raised),HOBJECT n_child) = 1
S_throw_found = $ms_seek(S_raised,MS_THROW,1000)
S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET
S_throw = S_throw_found[.COMPLETION = NORMAL]
S_throw.TODO = (THROW_SEARCH n_error) :: (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask_tail*
S_throw.CURRENT = eps /\ S_throw.FRAMES = eps /\ $ms_output(S_throw.EVENTS) = ptbytes_rebound
~(HOBJECT n_rv <- S_throw.ALLOCATIONS) /\ ~(HOBJECT n_payload <- S_throw.ALLOCATIONS) /\ $heap_owners($heap_graph(S_throw),HOBJECT n_child) = 1
$property_empty_rv_valid(S_throw,ppropertyemptyrv) /\ ~$property_empty_capture(S_throw,ppropertyempty)
$property_empty_guard(S_throw,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_throw,n_child,$ptascii("value"))
PhpStep: S_throw ~> S_release_raw
S_release_raw.TODO = (THROW_SEARCH n_error) :: ptask_tail*
S_release_raw.COMPLETION = NORMAL /\ S_release_raw.RESULT = KNOWN PNULL /\ S_release_raw.BASE = BASE_VALUE (KNOWN PNULL)
S_release_raw.EVENTS = S_throw.EVENTS /\ S_release_raw.STORE = S_throw.STORE
$throwable_live(S_release_raw,n_error) /\ $heap_owners($heap_graph(S_release_raw),HOBJECT n_child) = 0
S_released = $ms_after(S_throw,S_release_raw)
S_released.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
pdestructionoperation.PENDING = (n_error) /\ pdestructionoperation.VALUE = KNOWN PNULL
'''.strip().splitlines()

FINISH = r'''
~$property_empty_guard(S_release_raw,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_release_raw,n_child,$ptascii("value"))
S_dtor_found = $ms_seek(S_released,MS_DTOR n_child,1000)
S_dtor_found.COMPLETION = NORMAL \/ S_dtor_found.COMPLETION = BUDGET
S_dtor = S_dtor_found[.COMPLETION = NORMAL]
$ms_stage(S_dtor,MS_DTOR n_child)
$ms_output(S_dtor.EVENTS) = ptbytes_rebound
~$property_empty_guard(S_dtor,n_child,$ptascii("value")) /\ ~$property_empty_get_active(S_dtor,n_child,$ptascii("value"))
$ms_guard(S_dtor)
S_final = $drive_steps(S_dtor,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$ms_output(S_final.EVENTS) = ptbytes_final /\ ~(HOBJECT n_child <- S_final.ALLOCATIONS) /\ ~(HOBJECT n_rv <- S_final.ALLOCATIONS) /\ ~(HOBJECT n_payload <- S_final.ALLOCATIONS)
$lookup(S_final.ENV,$ptascii("child")) = (n_child_cell_final)
S_final.STORE[n_child_cell_final] = DEFINED PNULL
$ms_guard(S_final)
S_budget = $drive_steps(S_rebound,0)
S_budget.COMPLETION = BUDGET /\ S_budget.TODO = S_rebound.TODO /\ S_budget.EVENTS = S_rebound.EVENTS
$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final
'''.strip().splitlines()

DERIVED = r'''
$property_empty_rv_kind(S,STDINSTANCE) /\ $property_empty_rv_kind(S,S.OBJECTS[n_payload])
~$property_empty_rv_kind(S,WEAKMAP eps)
S_internal = S[.OBJECTS[n_rv] = WEAKMAP eps]
~$property_empty_rv_ready(S_internal,ppropertyempty)
PhpStep: S_internal ~> S_internal_done
S_internal_done.COMPLETION = UNSUPPORTED "magic empty getter result type" /\ S_internal_done.EVENTS = S.EVENTS
S_freeing = S_storage[.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: S_storage.TODO][.RESULT = KNOWN (POBJECT n_rv)][.BASE = BASE_VALUE (KNOWN PNULL)]
$property_empty_valid(S_freeing,ppropertyempty) /\ $property_empty_rv_kind(S_freeing,S_freeing.OBJECTS[n_rv])
$instance_storage_for(S_freeing,n_rv) = (pinstancestorage)
~$property_empty_rv_ready(S_freeing,ppropertyempty)
PhpStep: S_freeing ~> S_freeing_done
S_freeing_done.COMPLETION = UNSUPPORTED "magic empty getter result type" /\ S_freeing_done.EVENTS = S_storage.EVENTS
S_outofrange = S[.RESULT = KNOWN (POBJECT (|S.OBJECTS|))]
~$property_empty_rv_ready(S_outofrange,ppropertyempty)
'''.strip().splitlines()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', choices=('normal', 'throwing'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_empty_std_rv_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_gate_completed']
    selected = [case for case in data['cases'] if case['id'] in ('normal', 'throwing')]
    assert len(selected) == 2
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
    out = Path(tempfile.mkdtemp(prefix='magic-empty-std-rv-protocol-', dir=ROOT / '.tools'))
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
            rebound_output = output[:output.index('D|')]
            setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $ms_seek(S_initial,MS_RV,1000)', r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]', 'ptbytes_rebound = $ptascii(' + json.dumps(rebound_output) + ')',
                     'ptbytes_final = $ptascii(' + json.dumps(output) + ')']
            reached = setup + COMMON + [f'ppropertyempty.LINE = {case["empty_line"]}'] + (RETURN if name == 'normal' else THROW) + FINISH
            if name == 'throwing':
                # Request shutdown unbinds object-valued globals; inspect the
                # actual catch receive before terminal teardown instead.
                reached += [
                    'S_catch_found = $ms_seek(S_dtor,MS_CATCH,1000)',
                    r'S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET',
                    'S_catch = S_catch_found[.COMPLETION = NORMAL]',
                    'S_catch.TODO = (CATCH_BIND porigin_try n_catch n_error) :: ptask_catch*',
                    '$throwable_live(S_catch,n_error) /\\ $ms_output(S_catch.EVENTS) = ptbytes_rebound ++ $ptascii("D|")',
                    'PhpStep: S_catch ~> S_catch_raw',
                    '$lookup(S_catch_raw.ENV,$ptascii("caught")) = (n_caught_cell)',
                    'S_catch_raw.STORE[n_caught_cell] = DEFINED (POBJECT n_error)',
                    'S_catch_done = $ms_after(S_catch,S_catch_raw)',
                    'S_catch_done.COMPLETION = NORMAL /\\ $throwable_live(S_catch_done,n_error) /\\ $ms_guard(S_catch_done)',
                    '$drive_steps(S_catch_done,10000) = S_final',
                ]
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
