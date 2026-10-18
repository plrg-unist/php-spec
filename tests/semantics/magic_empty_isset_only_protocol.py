"""Check terminal empty with inherited isset and no getter and captured receiver."""
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

syntax pemptyissetstage = MN_PENDING | MN_REBOUND ptbytes | MN_RESULT | MN_THROW | MN_DTOR nat | MN_CATCH
dec $mn_output(pevent*) : ptbytes
def $mn_output(eps) = eps
def $mn_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $mn_output(pevent*)
dec $mn_stage(pstate,pemptyissetstage) : bool
def $mn_stage(S,MN_PENDING) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (ISSET_RESULT true z) :: ptask*
  -- if S.BASE = BASE_PROPERTY (POBJECT n) ptbytes
  -- if $property_isset_needed(S,n,ptbytes)
def $mn_stage(S,MN_REBOUND ptbytes) = true
  -- if S.CURRENT =/= eps
  -- if $mn_output(S.EVENTS) = ptbytes
def $mn_stage(S,MN_RESULT) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask*
def $mn_stage(S,MN_THROW) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask*
def $mn_stage(S,MN_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $mn_stage(S,MN_CATCH) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask*
def $mn_stage(S,pemptyissetstage) = false -- otherwise
dec $mn_seek(pstate,pemptyissetstage,nat) : pstate
def $mn_seek(S,pemptyissetstage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $mn_stage(S,pemptyissetstage) \/ n = 0
def $mn_seek(S,pemptyissetstage,n) = $mn_seek($drive_steps(S[.COMPLETION = NORMAL],1),pemptyissetstage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$mn_stage(S,pemptyissetstage) /\ $(n > 0)
def $mn_seek(S,pemptyissetstage,n) = $mn_seek($drive_steps(S,1),pemptyissetstage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $mn_seek(S,pemptyissetstage,n) = S -- otherwise
dec $mn_after(pstate,pstate) : pstate
def $mn_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $mn_guard(pstate) : bool
def $mn_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''

COMMON = r'''
$mn_stage(S,MN_PENDING)
S.TODO = (ISSET_RESULT true z_empty) :: ptask_tail*
S.BASE = BASE_PROPERTY (POBJECT n_child) ptbytes_name
$property_isset_plan(S) = (ppropertyisset)
ppropertyisset.OBJECT = n_child /\ ppropertyisset.NAME = ptbytes_name /\ ppropertyisset.LINE = z_empty
$property_isset_empty(S,ppropertyisset) /\ $property_isset_source(S,ppropertyisset)
$property_isset_valid(S,ppropertyisset) /\ $property_isset_capture(S,ppropertyisset)
$property_get_method(S,n_child) = eps /\ $property_empty_plan(S) = eps
S.CURRENT = eps /\ S.FRAMES = eps /\ S.ORIGIN = (ppropertyisset.SITE)
$heap_owners($heap_graph(S),HOBJECT n_child) = 2 /\ $mn_guard(S)
PhpStep: S ~> S_call_raw
S_call_raw.TODO = (CALL_ARGS (PROPERTY_ISSET_TARGET ppropertyisset) eps 1 ([KNOWN (PSTRING ptbytes_name)]) (ppropertyisset.SITE) z_empty) :: (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*
S_call_raw.BASE = BASE_VALUE (KNOWN PNULL) /\ S_call_raw.RESULT = KNOWN PNULL /\ S_call_raw.EVENTS = S.EVENTS
$task_nodes(PROPERTY_ISSET_RESULT ppropertyisset) = [HOBJECT n_child] /\ $target_nodes(PROPERTY_ISSET_TARGET ppropertyisset) = eps
$property_isset_pending_call(S_call_raw,ppropertyisset)
S_call = $mn_after(S,S_call_raw)
S_rebound_found = $mn_seek(S_call,MN_REBOUND ptbytes_rebound,1000)
S_rebound_found.COMPLETION = NORMAL \/ S_rebound_found.COMPLETION = BUDGET
S_rebound = S_rebound_found[.COMPLETION = NORMAL]
$mn_stage(S_rebound,MN_REBOUND ptbytes_rebound)
S_rebound.CURRENT = (pcallcontext_isset)
S_rebound.FRAMES = [pframe_isset]
pcallcontext_isset.TARGET = PROPERTY_ISSET_TARGET ppropertyisset /\ pcallcontext_isset.RECEIVER = (n_child) /\ pcallcontext_isset.CALLED_CLASS = (ppropertyisset.CLASS)
pframe_isset.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*
$property_isset_context(S_rebound,pcallcontext_isset) /\ $call_receiver_roots(pcallcontext_isset) = eps
$property_isset_guard(S_rebound,S_rebound.CURRENT,S_rebound.FRAMES,n_child,ptbytes_name) /\ ~$property_empty_get_active(S_rebound,n_child,ptbytes_name)
S_caller = $constant_frame_scope(S_rebound,pframe_isset,eps)
$lookup(S_caller.ENV,$ptascii("child")) = (n_child_cell)
S_caller.STORE[n_child_cell] = DEFINED PNULL
$property_isset_valid(S_caller,ppropertyisset) /\ ~$property_isset_capture(S_caller,ppropertyisset)
$property_get_method(S_rebound,n_child) = eps /\ $heap_owners($heap_graph(S_rebound),HOBJECT n_child) = 1
$mn_guard(S_rebound)
'''.strip().splitlines()

RETURN = r'''
S_result_found = $mn_seek(S_rebound,MN_RESULT,1000)
S_result_found.COMPLETION = NORMAL \/ S_result_found.COMPLETION = BUDGET
S_result = S_result_found[.COMPLETION = NORMAL]
S_result.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*
S_result.CURRENT = eps /\ S_result.FRAMES = eps /\ S_result.RESULT = KNOWN (PBOOL b_callback)
$property_isset_empty(S_result,ppropertyisset) /\ $property_isset_valid(S_result,ppropertyisset) /\ ~$property_isset_capture(S_result,ppropertyisset)
$heap_owners($heap_graph(S_result),HOBJECT n_child) = 1
PhpStep: S_result ~> S_release_raw
S_release_raw.TODO = ptask_tail* /\ S_release_raw.RESULT = KNOWN (PBOOL true) /\ S_release_raw.EVENTS = S_result.EVENTS
$heap_owners($heap_graph(S_release_raw),HOBJECT n_child) = 0
S_released = $mn_after(S_result,S_release_raw)
S_released.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
pdestructionoperation.VALUE = KNOWN (PBOOL true) /\ pdestructionoperation.PENDING = eps
'''.strip().splitlines()

THROW = r'''
S_throw_found = $mn_seek(S_rebound,MN_THROW,1000)
S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET
S_throw = S_throw_found[.COMPLETION = NORMAL]
S_throw.TODO = (THROW_SEARCH n_error) :: (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*
S_throw.CURRENT = eps /\ S_throw.FRAMES = eps /\ $throwable_live(S_throw,n_error)
$property_isset_throw_tail(S_throw,ppropertyisset) /\ $property_isset_valid(S_throw,ppropertyisset) /\ ~$property_isset_capture(S_throw,ppropertyisset)
$heap_owners($heap_graph(S_throw),HOBJECT n_child) = 1 /\ $mn_output(S_throw.EVENTS) = ptbytes_rebound
PhpStep: S_throw ~> S_release_raw
S_release_raw.TODO = (THROW_SEARCH n_error) :: ptask_tail*
S_release_raw.COMPLETION = NORMAL /\ S_release_raw.EVENTS = S_throw.EVENTS /\ S_release_raw.STORE = S_throw.STORE
$throwable_live(S_release_raw,n_error) /\ $heap_owners($heap_graph(S_release_raw),HOBJECT n_child) = 0
S_released = $mn_after(S_throw,S_release_raw)
S_released.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
pdestructionoperation.PENDING = (n_error)
'''.strip().splitlines()

FINISH = r'''
~$property_isset_guard(S_release_raw,S_release_raw.CURRENT,S_release_raw.FRAMES,n_child,ptbytes_name) /\ ~$property_empty_get_active(S_release_raw,n_child,ptbytes_name)
S_dtor_found = $mn_seek(S_released,MN_DTOR n_child,1000)
S_dtor_found.COMPLETION = NORMAL \/ S_dtor_found.COMPLETION = BUDGET
S_dtor = S_dtor_found[.COMPLETION = NORMAL]
$mn_stage(S_dtor,MN_DTOR n_child)
$mn_output(S_dtor.EVENTS) = ptbytes_rebound
~$property_isset_guard(S_dtor,S_dtor.CURRENT,S_dtor.FRAMES,n_child,ptbytes_name) /\ ~$property_empty_get_active(S_dtor,n_child,ptbytes_name)
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

DERIVED = r'''
S_wrongflag = S[.TODO = (ISSET_RESULT false z_empty) :: ptask_tail*]
$property_isset_empty(S_wrongflag,ppropertyisset) /\ $property_isset_pending(S_wrongflag) /\ $property_isset_plan(S_wrongflag) = eps
PhpStep: S_wrongflag ~> S_wrongflag_done
S_wrongflag_done.COMPLETION = UNSUPPORTED "magic isset source, function, or recursive access" /\ S_wrongflag_done.EVENTS = S.EVENTS
S_wrongline = S[.TODO = (ISSET_RESULT true $(z_empty + 1)) :: ptask_tail*]
$property_isset_plan(S_wrongline) = eps /\ $property_empty_plan(S_wrongline) = eps
PhpStep: S_wrongline ~> S_wrongline_done
S_wrongline_done.COMPLETION = UNSUPPORTED "magic empty source, methods, or recursive access" /\ S_wrongline_done.EVENTS = S.EVENTS
ppropertyisset_name = ppropertyisset[.NAME = $ptascii("other")]
~$property_isset_empty(S,ppropertyisset_name) /\ ~$property_isset_valid(S,ppropertyisset_name)
porigin_wrong = ppropertyisset.PROPERTY
ppropertyisset_method = ppropertyisset[.METHOD = porigin_wrong]
$property_isset_empty(S,ppropertyisset_method) /\ ~$property_isset_valid(S,ppropertyisset_method)
S_missing = S[.SOURCES = eps]
$property_isset_plan(S_missing) = eps /\ $property_empty_plan(S_missing) = eps
PhpStep: S_missing ~> S_missing_done
S_missing_done.COMPLETION = UNSUPPORTED "magic empty source, methods, or recursive access" /\ S_missing_done.EVENTS = S.EVENTS
~$property_isset_guard(S_rebound,S_rebound.CURRENT,S_rebound.FRAMES,n_child,$ptascii("other"))
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', choices=('false', 'true', 'throwing'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_empty_isset_only_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_gate_completed']
    selected = [case for case in data['cases'] if case['id'] in ('false', 'true', 'throwing')]
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
    out = Path(tempfile.mkdtemp(prefix='magic-empty-isset-only-protocol-', dir=ROOT / '.tools'))
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
                     'S_found = $mn_seek(S_initial,MN_PENDING,1000)', r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]', 'ptbytes_rebound = $ptascii(' + json.dumps(rebound_output) + ')',
                     'ptbytes_final = $ptascii(' + json.dumps(output) + ')']
            reached = setup + ([f'b_callback = {name}'] if name != 'throwing' else []) + COMMON + (RETURN if name != 'throwing' else THROW) + FINISH + [f'ppropertyisset.LINE = {case["empty_line"]}']
            if name == 'throwing':
                # Request shutdown unbinds object-valued globals; inspect the
                # actual catch receive before terminal teardown instead.
                reached += [
                    'S_catch_found = $mn_seek(S_dtor,MN_CATCH,1000)',
                    r'S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET',
                    'S_catch = S_catch_found[.COMPLETION = NORMAL]',
                    'S_catch.TODO = (CATCH_BIND porigin_try n_catch n_error) :: ptask_catch*',
                    '$throwable_live(S_catch,n_error) /\\ $mn_output(S_catch.EVENTS) = ptbytes_rebound ++ $ptascii("D|")',
                    'PhpStep: S_catch ~> S_catch_raw',
                    '$lookup(S_catch_raw.ENV,$ptascii("caught")) = (n_caught_cell)',
                    'S_catch_raw.STORE[n_caught_cell] = DEFINED (POBJECT n_error)',
                    'S_catch_done = $mn_after(S_catch,S_catch_raw)',
                    'S_catch_done.COMPLETION = NORMAL /\\ $throwable_live(S_catch_done,n_error) /\\ $mn_guard(S_catch_done)',
                    '$drive_steps(S_catch_done,10000) = S_final',
                ]
            derived = DERIVED if name == 'false' else []
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
