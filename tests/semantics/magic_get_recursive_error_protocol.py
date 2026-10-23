"""Check typed UNSET getter reentry, local recovery and abrupt cleanup."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import error_handler_run as recorder
import magic_get_recursion_protocol as common
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()

PREFIX = common.PREFIX + r'''
syntax ptestage = TE_INNER int | TE_CATCH
dec $te_stage(pstate,ptestage) : bool
def $te_stage(S,TE_INNER z) = true
  -- if S.TODO = (PROPERTY_PREP (NIdentifier (BYTES text) metadata_name) z) :: (DIM_FETCH z) :: ptask_tail*
  -- if $base64(text) = $ptascii("ghost")
  -- if S.CURRENT =/= eps
def $te_stage(S,TE_CATCH) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask_tail*
def $te_stage(S,ptestage) = false -- otherwise
dec $te_seek(pstate,ptestage,nat) : pstate
def $te_seek(S,ptestage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $te_stage(S,ptestage) \/ n = 0
def $te_seek(S,ptestage,n) = $te_seek($drive_steps(S[.COMPLETION = NORMAL],1),ptestage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$te_stage(S,ptestage) /\ $(n > 0)
def $te_seek(S,ptestage,n) = $te_seek($drive_steps(S,1),ptestage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $te_seek(S,ptestage,n) = S -- otherwise
'''


def reach(name, previous, stage):
    return [f'{name}_found = $te_seek({previous},{stage},2000)',
            fr'{name}_found.COMPLETION = NORMAL \/ {name}_found.COMPLETION = BUDGET',
            f'{name} = {name}_found[.COMPLETION = NORMAL]', f'$te_stage({name},{stage})']


def replace(lines, old, new):
    assert lines.count(old) == 1, old
    return [part for line in lines for part in (new if line == old else [line])]


FRONT = replace(common.FRONT,
    r'ppropertyget.NAME = ptbytes_name /\ ppropertyget.DECL = eps',
    ['ppropertyget.NAME = ptbytes_name', 'ppropertyget.DECL = (ppropertyid)'])
FRONT = replace(FRONT,
    '$property_effective_desc(S_front,n_child,ptbytes_name) = eps',
    common.lines(r'''
$property_effective_desc(S_front,n_child,ptbytes_name) = (ppropertydesc)
ppropertydesc.ORIGIN = ppropertyid /\ ppropertydesc.TYPE =/= eps
ppropertydesc.VISIBILITY = PROPERTY_PUBLIC /\ ~ppropertydesc.STATIC /\ ppropertydesc.KEY = ptbytes_name
$objectprops_at(S_front.OBJECTPROPS,n_child) = (ppropertyslot_front_all*)
$property_slot_at(ppropertyslot_front_all*,ptbytes_name) = (ppropertyslot_front)
ppropertyslot_front.DECL = (ppropertyid) /\ ppropertyslot_front.STATE = PROP_UNSET
$property_get_recursive_error_plan(S_front) = eps
'''))

INNER = common.lines(r'''
S_inner.TODO = (PROPERTY_PREP phpType20_inner z_inner) :: (DIM_FETCH z_inner) :: ptask_inner_tail*
S_inner.ORIGIN = (porigin_inner)
$property_get_recursive_error_plan(S_inner) = (ppropertydesc)
$property_effective_desc(S_inner,n_child,ptbytes_name) = (ppropertydesc)
$objectprops_at(S_inner.OBJECTPROPS,n_child) = (ppropertyslot_inner_all*)
$property_slot_at(ppropertyslot_inner_all*,ptbytes_name) = (ppropertyslot_inner)
ppropertyslot_inner.DECL = (ppropertyid) /\ ppropertyslot_inner.STATE = PROP_UNSET
$property_null_read_valid(S_inner,{SITE porigin_inner, NAME ptbytes_name, LINE z_inner})
$property_get_recursive_plan(S_inner) = eps /\ $property_get_plan(S_inner) = eps
~$property_get_recursive_untyped(S_inner,n_child,ptbytes_name)
$gr_active(S_inner,n_child,ptbytes_name) /\ $gr_guard(S_inner)
$gr_output(S_inner.EVENTS) = ptbytes_before_error
PhpStep: S_inner ~> S_raw
S_raw.COMPLETION = THROWN "Error" ptbytes_message z_inner
S_raw.TODO = S_inner.TODO /\ S_raw.OBJECTS = S_inner.OBJECTS
S_material = $throwable_transition(S_inner,S_raw)
S_material.COMPLETION = THROWING n_error
S_material.OBJECTS = S_inner.OBJECTS ++ [THROWABLE pthrowable_error]
n_error = |S_inner.OBJECTS|
pthrowable_error.KIND = "Error" /\ pthrowable_error.ORIGIN = (porigin_inner)
$throwable_field(S_material,n_error,"message") = PSTRING ptbytes_message
$throwable_field(S_material,n_error,"file") = PSTRING ptbytes_file
$throwable_field(S_material,n_error,"line") = PINT z_inner
$throwable_field(S_material,n_error,"previous") = PNULL
$throwable_object_image_valid(S_material,n_error)
S_material.EVENTS = S_inner.EVENTS
S_material.TODO = (DIM_FETCH z_inner) :: ptask_inner_tail*
S_pending = $gr_after(S_inner,S_raw)
''')

CATCH = common.lines(r'''
S_catch.TODO = (CATCH_BIND porigin_catch n_index n_caught) :: ptask_catch_tail*
$gr_output(S_catch.EVENTS) = ptbytes_before_catch
$gr_guard(S_catch)
$throwable_field(S_catch,n_error,"message") = PSTRING ptbytes_message
$throwable_field(S_catch,n_error,"file") = PSTRING ptbytes_file
$throwable_field(S_catch,n_error,"line") = PINT z_inner
''')


def conditions(case, checked):
    name = case['id']
    prefix = {'recover': 'N:', 'replacement': 'R:', 'cleanup': 'L:'}[name]
    before_error = prefix + ('G|g|V|' if name == 'cleanup' else 'G|')
    declaring = {'recover': 'NullableGet121', 'replacement': 'ReplaceBase121', 'cleanup': 'CleanupGet121'}[name]
    reached = [
        'S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(HERE / case['source_file']).encode()).decode()) + ')',
        r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
        'ptbytes_file = $ptascii(' + json.dumps(str(HERE / case['source_file'])) + ')',
        'ptbytes_prefix = $ptascii(' + json.dumps(prefix) + ')',
        'ptbytes_before_error = $ptascii(' + json.dumps(before_error) + ')',
        'ptbytes_before_catch = $ptascii(' + json.dumps(before_error + ('D|' if name == 'replacement' else '')) + ')',
        'ptbytes_final = $ptascii(' + json.dumps(base64.b64decode(case['stdout_base64']).decode()) + ')',
        'ptbytes_message = $ptascii(' + json.dumps('Typed property ' + declaring + '::$ghost must not be accessed before initialization') + ')',
        f'z_inner = {case["recursive_line"]}']
    reached += common.reach('S_front', 'S_initial', 'GR_OUTER') + FRONT
    reached += common.reach('S_get', 'S_call', 'GR_ENTER ppropertyget.METHOD') + common.ENTER
    if name == 'cleanup':
        reached += common.reach('S_exit', 'S_get', 'GR_EXIT') + common.lines(r'''
S_exit.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
pdestructionframe.FUNCTION = ppropertyget.METHOD /\ pdestructionframe.VALUE = KNOWN (PINT 7)
pdestructionframe <- S_exit.DESTRUCTION.FRAMES
$property_get_recursive_exit(S_exit,S_exit.TODO,ppropertyget) = (pdestructionframe)
$gr_active(S_exit,n_child,ptbytes_name) /\ $gr_guard(S_exit)
''')
        reached += reach('S_inner', 'S_exit', 'TE_INNER z_inner') + common.lines(r'''
S_inner.CURRENT = (pcallcontext_probe)
$destructor_context_call(pcallcontext_probe,S_inner.CURRENT,S_inner.FRAMES) = (pdestructorcall_probe)
pdestructorcall_probe.FRAME = (pdestructionframe) /\ pdestructorcall_probe.OPERATION = eps
pdestructionframe <- S_inner.DESTRUCTION.FRAMES
$lookup(S_inner.ENV,$ptascii("receiver")) = (n_receiver_cell)
S_inner.STORE[n_receiver_cell] = DEFINED (POBJECT n_child)
''')
    else:
        reached += reach('S_inner', 'S_get', 'TE_INNER z_inner') + [
            'S_inner.CURRENT = (pcallcontext_get)', 'S_inner.FRAMES = [pframe_get]',
            '$property_get_recursive_frame(S_inner,pcallcontext_get,pframe_get,n_child,ptbytes_name)']
    reached += INNER
    reached += reach('S_catch', 'S_pending', 'TE_CATCH') + CATCH
    if name == 'replacement':
        reached += common.lines(r'''
S_inner.STORE[n_child_cell] = DEFINED PNULL
$heap_owners($heap_graph(S_inner),HOBJECT n_child) = 2
$lookup(S_front.ENV,$ptascii("failure")) = (n_failure_cell)
S_front.STORE[n_failure_cell] = DEFINED (POBJECT n_failure)
n_caught = n_failure /\ n_failure =/= n_error
$throwable_field(S_catch,n_failure,"previous") = POBJECT n_error
$throwable_chain_valid(S_catch,n_failure)
~((HOBJECT n_child) <- S_catch.ALLOCATIONS)
~$gr_active(S_catch,n_child,ptbytes_name)
$lookup(S_catch.ENV,$ptascii("result")) = (n_result_cell)
S_catch.STORE[n_result_cell] = DEFINED (PINT 42)
S_end = S_catch
''')
    else:
        reached += ['n_caught = n_error', '$gr_active(S_catch,n_child,ptbytes_name)']
        if name == 'recover':
            reached += reach('S_null', 'S_catch', 'TE_INNER 15') + common.lines(r'''
S_null.CURRENT = (pcallcontext_get) /\ S_null.FRAMES = [pframe_get]
$property_effective_desc(S_null,n_child,ptbytes_name) = (ppropertydesc)
$objectprops_at(S_null.OBJECTPROPS,n_child) = (ppropertyslot_null_all*)
$property_slot_at(ppropertyslot_null_all*,ptbytes_name) = (ppropertyslot_null)
ppropertyslot_null.DECL = (ppropertyid) /\ ppropertyslot_null.STATE = PROP_VALUE (DIRECT PNULL)
$gr_active(S_null,n_child,ptbytes_name) /\ $gr_guard(S_null)
$property_get_recursive_error_plan(S_null) = eps /\ $property_get_plan(S_null) = eps
S_null.TODO = (PROPERTY_PREP phpType20_null 15) :: (DIM_FETCH 15) :: ptask_null_tail*
PhpStep: S_null ~> S_null_prepared_raw
S_null_prepared = $gr_after(S_null,S_null_prepared_raw)
S_null_prepared.BASE = BASE_PROPERTY (POBJECT n_child) ptbytes_name
PhpStep: S_null_prepared ~> S_null_value_raw
S_null_value_raw.TODO = ptask_null_tail* /\ S_null_value_raw.RESULT = KNOWN PNULL
''')
            reached += common.reach('S_again', 'S_null', 'GR_OUTER') + common.lines(r'''
$property_get_plan(S_again) = (ppropertyget_again)
ppropertyget_again.OBJECT = n_child /\ ppropertyget_again.DECL = (ppropertyid)
$objectprops_at(S_again.OBJECTPROPS,n_child) = (ppropertyslot_again_all*)
$property_slot_at(ppropertyslot_again_all*,ptbytes_name) = (ppropertyslot_again)
ppropertyslot_again.STATE = PROP_UNSET
~$gr_active(S_again,n_child,ptbytes_name)
S_end = S_again
''')
        else:
            reached += common.reach('S_result', 'S_catch', 'GR_GET_RESULT') + common.lines(r'''
S_result.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
S_result.RESULT = KNOWN (PINT 7)
~$gr_active(S_result,n_child,ptbytes_name)
$objectprops_at(S_result.OBJECTPROPS,n_child) = (ppropertyslot_result_all*)
$property_slot_at(ppropertyslot_result_all*,ptbytes_name) = (ppropertyslot_result)
ppropertyslot_result.DECL = (ppropertyid) /\ ppropertyslot_result.STATE = PROP_UNSET
$gr_guard(S_result)
S_end = S_result
''')
    reached += common.FINISH[:-3]
    derived = [
        'S_budget = $drive_steps(S_inner,0)', 'S_budget = S_inner[.COMPLETION = BUDGET]',
        '$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final']
    return reached, derived

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_get_recursive_error_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    assert [case['id'] for case in data['cases']] == ['propagate', 'recover', 'replacement', 'cleanup']
    assert [case['id'] for case in data['controls']] == ['private-fence', 'other-receiver']
    assert all(sha(HERE / case['source_file']) == case['source_sha256'] for case in data['cases'] + data['controls'])
    selected = [case for case in data['cases'] if case['id'] in ('recover', 'replacement', 'cleanup')]
    php, adapter, bridge, worker, runner, compiler = (ROOT / name for name in [
        '.tools/php/bin/php', '_build/default/adapter/main.exe', '.tools/php-file.so',
        'frontend/worker.php', 'tests/semantics/_build/default/numeric_runner.exe', '.tools/spectec/bin/p4spectec'])
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    assert sha(compiler) == '26d77fb9bfae2b2868e137a94051f55f9b607660c340e9b22ae8300fb0d8ce88'
    assert sha(runner) == 'b57a2ed7daf86de23993a29d079083377cfef6da133739a164dbfdb9f11fd7a0'
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_bytes())]
    watched = [Path(__file__), Path(common.__file__), Path(recorder.__file__), catalogue, profile_file,
        php, adapter, bridge, worker, runner, compiler, manifest, *modules,
        *(HERE / case['source_file'] for case in data['cases'] + data['controls']),
        *(ROOT / name for name in ['spec/schema.json', 'spec/php.watsup', 'spec/nodes.json',
            'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py',
            'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py'])]
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    assert revision == args.revision and not status, (revision, status)
    before = {str(path): sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='magic-get-recursive-error-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    report = {'revision': revision, 'inputs': before, 'profile': profile, 'module_count': len(modules),
        'mode': 'SL', 'cache': False, 'det': True, 'records': [], 'fixtures': [],
        'selection': [case['id'] for case in selected], 'application_invocations': 0,
        'application_evaluations': 0, 'source_agreements': 0, 'premises': 0,
        'reached_premises': 0, 'derived_premises': 0, 'cap_seconds': 90,
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent', 'jobs': 1},
        'passed': False}
    try:
        flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
        for case in selected:
            source = HERE / case['source_file']
            assert sha(source) == case['source_sha256']
            raw = base64.b64decode(case['stdout_base64']) + b'\0' + base64.b64decode(case['stderr_base64']) + b'\0' + str(case['exit_status']).encode()
            assert hashlib.sha256(raw).hexdigest() == case['native_raw_sha256']
            directory = out / case['id']
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
            reached, derived = conditions(case, checked)
            content = PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
            content += ''.join('  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n' for condition in reached + derived)
            content += 'def $main() = false -- otherwise\n'
            fixture = directory / 'typed-recursion.watsup'
            fixture.write_text(content)
            row = {'id': case['id'], 'path': str(fixture), 'sha256': sha(fixture),
                'reached_premises': len(reached), 'derived_premises': len(derived), 'premises': len(reached) + len(derived)}
            report['fixtures'].append(row)
            for key in ('premises', 'reached_premises', 'derived_premises'):
                report[key] += row[key]
        report.update(prepared=True, passed=True)
        if not args.prepare_only:
            for fixture in report['fixtures']:
                directory = Path(fixture['path']).parent
                process = recorder.recorded([str(compiler), 'algo', *map(str, modules), fixture['path']], directory / 'compiler', 90)
                passed = process['exit'] == 0 and not process['timeout'] and not process['interruption'] and not process['group_after'] and not (directory / 'compiler.stderr').read_bytes() and b'\ndef $main : bool =\n' in (directory / 'compiler.stdout').read_bytes()
                report['records'].append({'id': fixture['id'] + '-algorithmic-compilation', 'process': process, 'passed': passed, 'application_evaluations': 0})
                report['passed'] = passed
                assert passed
                report['application_invocations'] += 1
                process = recorder.recorded([str(runner), '--sl', *map(str, modules), fixture['path']], directory / 'state', 90)
                output = (directory / 'state.stdout').read_bytes()
                evaluated = process['exit'] == 0 and output in (b'true\n', b'false\n')
                report['application_evaluations'] += int(evaluated)
                passed = evaluated and not process['timeout'] and not process['interruption'] and not process['group_after'] and not (directory / 'state.stderr').read_bytes() and output == b'true\n'
                report['records'].append({'id': fixture['id'] + '-strict-SL-application', 'process': process, 'passed': passed})
                report['passed'] = passed
                assert passed
    finally:
        report.update(inputs_stable=before == {str(path): sha(path) for path in watched},
            fixtures_stable=all(row['sha256'] == sha(Path(row['path'])) for row in report['fixtures']),
            head_stable=revision == git('rev-parse', 'HEAD'), status_stable=status == git('status', '--short'))
        if not args.prepare_only:
            report['passed'] = report['passed'] and len(report['records']) == 2 * len(selected) and all(row['passed'] for row in report['records']) and report['application_invocations'] == len(selected) and report['application_evaluations'] == len(selected)
        report['passed'] = report['passed'] and all(report[key] for key in ('inputs_stable', 'fixtures_stable', 'head_stable', 'status_stable'))
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({key: report[key] for key in ('passed', 'application_evaluations', 'premises', 'reached_premises', 'derived_premises', 'inputs_stable', 'head_stable', 'status_stable')}), flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
