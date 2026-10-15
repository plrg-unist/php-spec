"""Check terminal empty's primitive RV truth, byte carriers and result release."""
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
dec $ms_stage(pstate,ptbytes) : bool
def $ms_stage(S,ptbytes) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask*
  -- if ppropertyempty.NAME = ptbytes
def $ms_stage(S,ptbytes) = false -- otherwise
dec $ms_seek(pstate,ptbytes,nat) : pstate
def $ms_seek(S,ptbytes,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $ms_stage(S,ptbytes) \/ n = 0
def $ms_seek(S,ptbytes,n) = $ms_seek($drive_steps(S[.COMPLETION = NORMAL],1),ptbytes,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$ms_stage(S,ptbytes) /\ $(n > 0)
def $ms_seek(S,ptbytes,n) = S -- otherwise
dec $ms_after(pstate,pstate) : pstate
def $ms_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $ms_guard(pstate) : bool
def $ms_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $ms_output(pevent*) : ptbytes
def $ms_output(eps) = eps
def $ms_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $ms_output(pevent*)
'''

ROWS = [
    ('nullish', 'PNULL', 'true'), ('falsey', 'PBOOL false', 'true'),
    ('truthy', 'PBOOL true', 'false'), ('blank', 'PSTRING_CARRIER INTERNED_STRING eps', 'true'),
    ('zero', 'PSTRING_CARRIER INTERNED_STRING [48]', 'true'),
    ('doublezero', 'PSTRING_CARRIER INTERNED_STRING ([48,48])', 'false'),
    ('text', 'PSTRING_CARRIER INTERNED_STRING ([103,111])', 'false'),
    ('nul', 'PSTRING_CARRIER INTERNED_STRING [0]', 'false'),
    ('zeronul', 'PSTRING_CARRIER INTERNED_STRING ([48,0])', 'false'),
]

BODY = ['S_nullish = S']
previous = None
for name, value, result in ROWS:
    state = 'S_' + name
    if previous:
        BODY += [f'S_found_{name} = $ms_seek(S_done_{previous},$ptascii("{name}"),1000)',f'S_found_{name}.COMPLETION = NORMAL \\/ S_found_{name}.COMPLETION = BUDGET',f'{state} = S_found_{name}[.COMPLETION = NORMAL]']
    BODY += [f'$ms_stage({state},$ptascii("{name}"))',f'{state}.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty_{name} true) :: ptask_{name}*',f'{state}.RESULT = KNOWN ({value})',f'{state}.CURRENT = eps /\\ {state}.FRAMES = eps /\\ {state}.ORIGIN = (ppropertyempty_{name}.SITE)',f'$ms_guard({state})']
    if name == 'nullish': BODY += ['n_child = ppropertyempty_nullish.OBJECT']
    if name in ('nullish', 'nul'): BODY += [f'n_owners_{name} = $heap_owners($heap_graph({state}),HOBJECT n_child)']
    BODY += [f'PhpStep: {state} ~> S_raw_{name}',f'S_done_{name} = $ms_after({state},S_raw_{name})',f'S_done_{name}.COMPLETION = NORMAL /\\ S_done_{name}.RESULT = KNOWN (PBOOL {result}) /\\ S_done_{name}.TODO = ptask_{name}*',f'S_done_{name}.BASE = BASE_VALUE (KNOWN PNULL) /\\ S_done_{name}.EVENTS = {state}.EVENTS',f'S_done_{name}.STORE = {state}.STORE /\\ S_done_{name}.ENV = {state}.ENV /\\ S_done_{name}.OBJECTPROPS = {state}.OBJECTPROPS /\\ S_done_{name}.STRINGDATA = {state}.STRINGDATA']
    if name in ('nullish', 'nul'): BODY += [f'n_owners_{name} = $($heap_owners($heap_graph(S_done_{name}),HOBJECT n_child) + 1)']
    previous = name
BODY += [
'S_final = $drive_steps(S_done_zeronul,10000)',
'S_final.COMPLETION = NORMAL /\\ S_final.TODO = eps /\\ S_final.CURRENT = eps /\\ S_final.FRAMES = eps',
'$ms_output(S_final.EVENTS) = $ptascii("N:I:nullish|G:nullish|T|B:I:falsey|G:falsey|T|T:I:truthy|G:truthy|F|E:I:blank|G:blank|T|Z:I:zero|G:zero|T|D:I:doublezero|G:doublezero|F|S:I:text|G:text|F|U:I:nul|G:nul|F|Q:I:zeronul|G:zeronul|F|R:ONLY|")',
'S_final.OBJECTPROPS = S.OBJECTPROPS /\\ $ms_guard(S_final)',
'S_budget = $drive_steps(S_zeronul,0)',
'S_budget.COMPLETION = BUDGET /\\ S_budget.TODO = S_zeronul.TODO /\\ S_budget.RESULT = S_zeronul.RESULT',
'$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final'
]

# Constructed REQUEST controls authenticate existing identity metadata; no producer claim.
DERIVED = r'''
$property_empty_truth(S,PINT 0) = (true) /\ $property_empty_truth(S,PINT 13) = (false)
$property_empty_truth(S,PSTRING eps) = (true) /\ $property_empty_truth(S,PSTRING [48]) = (true)
$property_empty_truth(S,PSTRING ([48,48])) = (false) /\ $property_empty_truth(S,PSTRING [0]) = (false) /\ $property_empty_truth(S,PSTRING ([48,0])) = (false)
S_float = S_nullish[.RESULT = KNOWN (PFLOAT 0)]
PhpStep: S_float ~> S_float_done
S_float_done.COMPLETION = UNSUPPORTED "magic empty getter result type"
S_float_done.TODO = S_float.TODO /\ S_float_done.EVENTS = S_float.EVENTS /\ S_float_done.STORE = S_float.STORE
$property_empty_truth(S,PFLOAT 9221120237041090560) = eps
ptbytes_data* = S.STRINGDATA
n_string = |ptbytes_data*|
ptbytes_payload = [48,0]
pvalue_request = PSTRING_CARRIER (REQUEST_STRING n_string) ptbytes_payload
S_auth = S[.STRINGDATA = ptbytes_data* ++ [ptbytes_payload]][.RESULT = KNOWN pvalue_request]
$string_carrier_valid(S_auth,pvalue_request) /\ $property_empty_truth(S_auth,pvalue_request) = (false)
$value_nodes(pvalue_request) = eps /\ $ms_guard(S_auth)
PhpStep: S_auth ~> S_auth_raw
S_auth_done = $ms_after(S_auth,S_auth_raw)
S_auth_done.COMPLETION = NORMAL /\ S_auth_done.RESULT = KNOWN (PBOOL false) /\ S_auth_done.TODO = ptask_nullish*
S_auth_done.STRINGDATA = S_auth.STRINGDATA /\ S_auth_done.EVENTS = S_auth.EVENTS /\ S_auth_done.OBJECTPROPS = S_auth.OBJECTPROPS /\ $ms_guard(S_auth_done)
n_stale = $(n_string + 1)
$property_empty_truth(S_auth,PSTRING_CARRIER (REQUEST_STRING n_stale) ptbytes_payload) = eps
$property_empty_truth(S_auth,PSTRING_CARRIER (REQUEST_STRING n_string) [48]) = eps
$property_empty_truth(S_auth,PSTRING_CARRIER INTERNED_STRING [256]) = eps
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_empty_scalar_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file, source = HERE / 'profile.json', HERE / 'magic-empty-scalars.php'
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
    out = Path(tempfile.mkdtemp(prefix='magic-empty-scalar-protocol-', dir=ROOT / '.tools'))
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
                 'S_found = $ms_seek(S_initial,$ptascii("nullish"),1000)',
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
