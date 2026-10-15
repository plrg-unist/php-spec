"""Check terminal empty's non-NaN float RV truth and explicit boundaries."""
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
dec $mf_stage(pstate,ptbytes) : bool
def $mf_stage(S,ptbytes) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask*
  -- if ppropertyempty.NAME = ptbytes
def $mf_stage(S,ptbytes) = false -- otherwise
dec $mf_seek(pstate,ptbytes,nat) : pstate
def $mf_seek(S,ptbytes,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $mf_stage(S,ptbytes) \/ n = 0
def $mf_seek(S,ptbytes,n) = $mf_seek($drive_steps(S[.COMPLETION = NORMAL],1),ptbytes,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$mf_stage(S,ptbytes) /\ $(n > 0)
def $mf_seek(S,ptbytes,n) = S -- otherwise
dec $mf_after(pstate,pstate) : pstate
def $mf_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $mf_guard(pstate) : bool
def $mf_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $mf_output(pevent*) : ptbytes
def $mf_output(eps) = eps
def $mf_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $mf_output(pevent*)
'''

ROWS = [
    ('pluszero', 'PFLOAT 0', 'true'),
    ('minuszero', 'PFLOAT 9223372036854775808', 'true'),
    ('positive', 'PFLOAT 4609434218613702656', 'false'),
    ('negative', 'PFLOAT 13836183955189006336', 'false'),
    ('tiny', 'PFLOAT 1', 'false'),
    ('minustiny', 'PFLOAT 9223372036854775809', 'false'),
    ('largest', 'PFLOAT 9218868437227405311', 'false'),
    ('infinity', 'PFLOAT 9218868437227405312', 'false'),
    ('minusinf', 'PFLOAT 18442240474082181120', 'false'),
]

BODY = ['S_pluszero = S']
previous = None
for name, value, result in ROWS:
    state = 'S_' + name
    if previous:
        BODY += [f'S_found_{name} = $mf_seek(S_done_{previous},$ptascii("{name}"),1000)', f'S_found_{name}.COMPLETION = NORMAL \\/ S_found_{name}.COMPLETION = BUDGET', f'{state} = S_found_{name}[.COMPLETION = NORMAL]']
    BODY += [f'$mf_stage({state},$ptascii("{name}"))', f'{state}.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty_{name} true) :: ptask_{name}*', f'{state}.RESULT = KNOWN ({value})', f'{state}.CURRENT = eps /\\ {state}.FRAMES = eps /\\ {state}.ORIGIN = (ppropertyempty_{name}.SITE)', f'$mf_guard({state})']
    if name == 'pluszero': BODY += ['n_child = ppropertyempty_pluszero.OBJECT']
    if name in ('pluszero', 'minusinf'): BODY += [f'n_owners_{name} = $heap_owners($heap_graph({state}),HOBJECT n_child)']
    BODY += [f'PhpStep: {state} ~> S_raw_{name}', f'S_done_{name} = $mf_after({state},S_raw_{name})', f'S_done_{name}.COMPLETION = NORMAL /\\ S_done_{name}.RESULT = KNOWN (PBOOL {result}) /\\ S_done_{name}.TODO = ptask_{name}*', f'S_done_{name}.BASE = BASE_VALUE (KNOWN PNULL) /\\ S_done_{name}.EVENTS = {state}.EVENTS', f'S_done_{name}.STORE = {state}.STORE /\\ S_done_{name}.ENV = {state}.ENV /\\ S_done_{name}.OBJECTPROPS = {state}.OBJECTPROPS /\\ S_done_{name}.STRINGDATA = {state}.STRINGDATA']
    if name in ('pluszero', 'minusinf'): BODY += [f'n_owners_{name} = $($heap_owners($heap_graph(S_done_{name}),HOBJECT n_child) + 1)']
    previous = name
BODY += [
    'S_final = $drive_steps(S_done_minusinf,10000)',
    'S_final.COMPLETION = NORMAL /\\ S_final.TODO = eps /\\ S_final.CURRENT = eps /\\ S_final.FRAMES = eps',
    '$mf_output(S_final.EVENTS) = $ptascii("A:I:pluszero|G:pluszero|T|B:I:minuszero|G:minuszero|T|C:I:positive|G:positive|F|D:I:negative|G:negative|F|E:I:tiny|G:tiny|F|F:I:minustiny|G:minustiny|F|G:I:largest|G:largest|F|H:I:infinity|G:infinity|F|I:I:minusinf|G:minusinf|F|R:ONLY|")',
    'S_final.OBJECTPROPS = S.OBJECTPROPS /\\ $mf_guard(S_final)',
    'S_budget = $drive_steps(S_minusinf,0)',
    'S_budget.COMPLETION = BUDGET /\\ S_budget.TODO = S_minusinf.TODO /\\ S_budget.RESULT = S_minusinf.RESULT',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final',
]

# Constructed NaN/invalid-bit refusals do not claim warning execution or new producers.
DERIVED = r'''
pvalue_nan = PFLOAT 9221120237041090560
S_nan = S_pluszero[.RESULT = KNOWN pvalue_nan]
$property_empty_truth(S_nan,pvalue_nan) = eps
PhpStep: S_nan ~> S_nan_done
S_nan_done.COMPLETION = UNSUPPORTED "magic empty getter result type"
S_nan_done.TODO = S_nan.TODO /\ S_nan_done.EVENTS = S_nan.EVENTS /\ S_nan_done.STORE = S_nan.STORE
$property_empty_truth(S,PFLOAT 18444492273895866368) = eps /\ $property_empty_truth(S,PFLOAT 9218868437227405313) = eps
S_invalid = S_pluszero[.RESULT = KNOWN (PFLOAT 18446744073709551616)]
$property_empty_truth(S_invalid,PFLOAT 18446744073709551616) = eps
PhpStep: S_invalid ~> S_invalid_done
S_invalid_done.COMPLETION = UNSUPPORTED "magic empty getter result type" /\ S_invalid_done.TODO = S_invalid.TODO /\ S_invalid_done.EVENTS = S_invalid.EVENTS
$property_empty_truth(S,PFLOAT 18446744073709551617) = eps
$value_nodes(PFLOAT 1) = eps
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_empty_float_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file, source = HERE / 'profile.json', HERE / 'magic-empty-floats.php'
    profile = json.loads(profile_file.read_bytes())
    case = data['cases'][0]
    assert data['native_profile'] == profile
    assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256']
    php, adapter, bridge, worker, runner, compiler = (ROOT / name for name in [
        '.tools/php/bin/php', '_build/default/adapter/main.exe', '.tools/php-file.so',
        'frontend/worker.php', 'tests/semantics/_build/default/numeric_runner.exe', '.tools/spectec/bin/p4spectec'])
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    assert sha(compiler) == '26d77fb9bfae2b2868e137a94051f55f9b607660c340e9b22ae8300fb0d8ce88'
    assert sha(runner) == 'b57a2ed7daf86de23993a29d079083377cfef6da133739a164dbfdb9f11fd7a0'
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_bytes())]
    watched = [Path(__file__), Path(recorder.__file__), catalogue, source, profile_file, php,
               adapter, bridge, worker, runner, compiler, manifest, *modules, ROOT / 'spec/schema.json',
               ROOT / 'spec/php.watsup', ROOT / 'spec/nodes.json', ROOT / 'frontend/target.php',
               ROOT / 'frontend/wire.php', ROOT / 'frontend/wire.py', HERE / 'recorded_worker.py', HERE / 'static_types.py']
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    assert revision == args.revision and not status, (revision, status)
    before = {str(path): sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='magic-empty-float-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    report = {'revision': revision, 'inputs': before, 'profile': profile, 'module_count': len(modules),
              'mode': 'SL', 'cache': False, 'det': True, 'records': [],
              'application_invocations': 0, 'application_evaluations': 0, 'source_agreements': 0,
              'derived_premises': len(DERIVED), 'reached_premises': 5 + len(BODY), 'premises': 5 + len(BODY) + len(DERIVED),
              'cap_seconds': 90, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'jobs': 1}, 'passed': False}
    fixture = None
    try:
        flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
        frontend = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(bridge), str(worker)], out / 'frontend')
        adapter_worker = None
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'], parsed
            adapter_worker = Worker([str(adapter), str(ROOT)], out / 'adapter')
            checked = adapter_worker.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] and checked['ast'] == parsed['ast']
        finally:
            if adapter_worker:
                adapter_worker.close()
            frontend.close()
        setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                 r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                 'S_found = $mf_seek(S_initial,$ptascii("pluszero"),1000)',
                 r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                 'S = S_found[.COMPLETION = NORMAL]']
        content = PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
        for condition in setup + BODY + DERIVED:
            content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
        content += 'def $main() = false -- otherwise\n'
        fixture = out / 'hook.watsup'
        fixture.write_text(content)
        report.update(fixture=str(fixture), fixture_sha256=sha(fixture), prepared=True, passed=True)
        if not args.prepare_only:
            process = recorder.recorded([str(compiler), 'algo', *map(str, modules), str(fixture)], out / 'compiler', 90)
            passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and not (out / 'compiler.stderr').read_bytes() and b'\ndef $main : bool =\n' in (out / 'compiler.stdout').read_bytes()
            report['records'].append({'id': 'algorithmic-compilation', 'process': process, 'passed': passed, 'application_evaluations': 0})
            report['passed'] = passed
            assert passed
            report['application_invocations'] = 1
            process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'state', 90)
            output = (out / 'state.stdout').read_bytes()
            evaluated = process['exit'] == 0 and output in (b'true\n', b'false\n')
            report['application_evaluations'] = int(evaluated)
            passed = evaluated and not process['timeout'] and not process['group_after'] and not (out / 'state.stderr').read_bytes() and output == b'true\n'
            report['records'].append({'id': 'strict-SL-application', 'process': process, 'passed': passed})
            report['passed'] = passed
    finally:
        report.update(inputs_stable=before == {str(path): sha(path) for path in watched},
                      fixture_stable=fixture is None or report['fixture_sha256'] == sha(fixture),
                      head_stable=revision == git('rev-parse', 'HEAD'), status_stable=status == git('status', '--short'))
        report['passed'] = report['passed'] and all(report[key] for key in ('inputs_stable', 'fixture_stable', 'head_stable', 'status_stable'))
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({key: report[key] for key in ('passed', 'application_evaluations', 'derived_premises', 'reached_premises', 'inputs_stable', 'head_stable', 'status_stable')}), flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
