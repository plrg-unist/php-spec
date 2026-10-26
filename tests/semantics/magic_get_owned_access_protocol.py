"""Check owned nonpublic Get history, hidden types and original-receiver cleanup."""
from pathlib import Path
import argparse, base64, hashlib, json, os, subprocess, sys, tempfile
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import error_handler_run as recorder
import magic_get_recursion_protocol as common
import magic_get_scoped_unset_protocol as scoped
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()
# The denied source read runs globally, without a current PHP call.
PREFIX = scoped.PREFIX.replace('  -- if S.CURRENT =/= eps\n', '', 1)

FRONT = common.lines(r'''
$property_get_plan(S_front) = (ppropertyget)
n_child = ppropertyget.OBJECT
ppropertyget.SITE = porigin_site /\ ppropertyget.LINE = z_read
ptbytes_name = ppropertyget.NAME
ptbytes_name = $ptascii("ghost")
$property_get_method(S_front,n_child) = (pmethoddesc_get)
pmethoddesc_get.FUNCTION.ORIGIN = ppropertyget.METHOD
~pmethoddesc_get.FUNCTION.SIGNATURE.BYREF
~$property_get_public(S_front,n_child,ptbytes_name)
$property_get_owned_access(S_front,n_child,ptbytes_name)
$property_get_owned_source(S_front,ppropertyget)
~$property_get_this_source(S_front,ppropertyget)
$property_get_history(S_front,ppropertyget) /\ $property_get_capture(S_front,ppropertyget)
$property_effective_desc(S_front,n_child,ptbytes_name) = (ppropertydesc)
ptbytes_key = ppropertydesc.KEY
ptbytes_key =/= ptbytes_name
$objectprops_at(S_front.OBJECTPROPS,n_child) = (ppropertyslot_front_all*)
$property_slot_at(ppropertyslot_front_all*,ptbytes_key) = (ppropertyslot_front)
ppropertyslot_front.DECL = (ppropertydesc.ORIGIN)
S_front.FRAMES = pframe_caller_tail*
S_front.TODO = (PROPERTY_PREP phpType20_name z_read) :: (DIM_FETCH z_read) :: ptask_tail*
$property_get_base_tasks(S_front,ppropertyget) = [PROPERTY_GET_BASE ppropertyget]
$heap_owners($heap_graph(S_front),HOBJECT n_child) = 1
~$gr_active(S_front,n_child,ptbytes_name) /\ $gr_guard(S_front)
$gr_output(S_front.EVENTS) = ptbytes_prefix
''')
BEGIN = common.lines(r'''
PhpStep: S_front ~> S_begin_raw
S_begin = $gr_after(S_front,S_begin_raw)
S_begin.TODO = [CALL_ARGS (PROPERTY_GET_TARGET n_child ppropertyget.METHOD) eps 1 ([KNOWN (PSTRING ptbytes_name)]) (porigin_site) z_read, PROPERTY_GET_RESULT ppropertyget, PROPERTY_GET_BASE ppropertyget] ++ ptask_tail*
$property_get_pending_call(S_begin,PROPERTY_GET_TARGET n_child ppropertyget.METHOD,porigin_site)
$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_child]
$task_nodes(PROPERTY_GET_BASE ppropertyget) = [HOBJECT n_child]
$target_nodes(PROPERTY_GET_TARGET n_child ppropertyget.METHOD) = eps
$heap_owners($heap_graph(S_begin),HOBJECT n_child) = 2
$property_get_tail_valid(S_begin,ppropertyget) /\ $gr_guard(S_begin)
''')
ENTER = common.lines(r'''
S_get.CURRENT = (pcallcontext_get)
pcallcontext_get.TARGET = PROPERTY_GET_TARGET n_child ppropertyget.METHOD
S_get.FRAMES = pframe_get :: pframe_caller_tail*
pframe_get.CONTEXT = S_front.CURRENT
pframe_get.TODO = [PROPERTY_GET_RESULT ppropertyget, PROPERTY_GET_BASE ppropertyget] ++ ptask_tail*
$property_get_frame(S_get,pcallcontext_get,pframe_get)
$call_receiver_roots(pcallcontext_get) = eps
$property_get_history(S_get,ppropertyget)
$heap_owners($heap_graph(S_get),HOBJECT n_child) = 2
$gr_active(S_get,n_child,ptbytes_name) /\ $gr_guard(S_get)
''')
RESULT = common.lines(r'''
S_result.TODO = [PROPERTY_GET_RESULT ppropertyget, PROPERTY_GET_BASE ppropertyget] ++ ptask_tail*
S_result.CURRENT = S_front.CURRENT /\ S_result.FRAMES = pframe_caller_tail*
S_result.RESULT = KNOWN pvalue_return
$property_get_history(S_result,ppropertyget) /\ $property_get_valid(S_result,ppropertyget,true)
$property_get_verify(S_result,ppropertyget,S_result.RESULT) = S_result
$heap_owners($heap_graph(S_result),HOBJECT n_child) = 2
~$gr_active(S_result,n_child,ptbytes_name) /\ $gr_guard(S_result)
$gr_output(S_result.EVENTS) = ptbytes_before_result
PhpStep: S_result ~> S_copy_raw
S_copy_raw.TODO = [PROPERTY_GET_COPY ppropertyget (KNOWN pvalue_return), PROPERTY_GET_BASE ppropertyget] ++ ptask_tail*
S_copy_raw.RESULT = KNOWN PNULL /\ S_copy_raw.COMPLETION = NORMAL
S_copy_pending = $gr_after(S_result,S_copy_raw)
ptask_copy* = S_copy_raw.TODO
''')
LIFETIME = common.lines(r'''
S_copy.CURRENT = S_front.CURRENT /\ S_copy.FRAMES = pframe_caller_tail*
$heap_owners($heap_graph(S_copy),HOBJECT n_child) = 1
$property_get_base_valid(S_copy,ppropertyget)
$call_task_valid(S_copy,PROPERTY_GET_COPY ppropertyget (KNOWN pvalue_return))
~$gr_active(S_copy,n_child,ptbytes_name) /\ $gr_guard(S_copy)
PhpStep: S_copy ~> S_copied_raw
S_copied_raw.TODO = (PROPERTY_GET_BASE ppropertyget) :: ptask_tail*
S_copied_raw.RESULT = KNOWN pvalue_return
S_base_pending = $gr_after(S_copy,S_copied_raw)
ptask_base* = S_copied_raw.TODO
''')
BASE = common.lines(r'''
S_base.RESULT = KNOWN pvalue_return
S_base.CURRENT = S_front.CURRENT /\ S_base.FRAMES = pframe_caller_tail*
$heap_owners($heap_graph(S_base),HOBJECT n_child) = 1
$property_get_base_valid(S_base,ppropertyget)
$gr_output(S_base.EVENTS) = ptbytes_before_result
~$gr_active(S_base,n_child,ptbytes_name) /\ $gr_guard(S_base)
PhpStep: S_base ~> S_released_raw
S_released_raw.TODO = ptask_tail* /\ S_released_raw.RESULT = KNOWN pvalue_return
S_release_pending = $gr_after(S_base,S_released_raw)
''')
DTOR = common.lines(r'''
S_dtor.CURRENT = (pcallcontext_dtor)
$destructor_context_call(pcallcontext_dtor,S_dtor.CURRENT,S_dtor.FRAMES) = (pdestructorcall)
pdestructorcall.OBJECT = n_child
pdestructorcall.OPERATION = (pdestructionoperation)
pdestructionoperation.SOURCE = PROPERTY_GET_BASE ppropertyget
pdestructionoperation.VALUE = KNOWN pvalue_return
pdestructionoperation.CALLER = S_front.CURRENT /\ pdestructionoperation.PENDING = eps
$gr_output(S_dtor.EVENTS) = ptbytes_before_result
~$gr_active(S_dtor,n_child,ptbytes_name) /\ $gr_guard(S_dtor)
''')
RECEIVED = common.lines(r'''
S_received.RESULT = KNOWN pvalue_return
S_received.CURRENT = S_front.CURRENT /\ S_received.FRAMES = pframe_caller_tail*
~((HOBJECT n_child) <- S_received.ALLOCATIONS)
$gr_output(S_received.EVENTS) = ptbytes_before_received
$property_get_base_count(S_received.TODO,n_child,porigin_site) = 0
$gr_guard(S_received)
S_end = S_received
''')


def conditions(case, checked):
    protected = case['id'] == 'protected-populate'
    reached = [
        'S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(HERE / case['source_file']).encode()).decode()) + ')',
        r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
        'ptbytes_prefix = $ptascii(' + json.dumps('P:' if protected else 'X:') + ')',
        'ptbytes_before_result = $ptascii(' + json.dumps('P:G|g|' if protected else 'X:G|') + ')',
        'ptbytes_before_received = $ptascii(' + json.dumps('P:G|g|D99|' if protected else 'X:G|D|') + ')',
        'ptbytes_final = $ptascii(' + json.dumps(base64.b64decode(case['stdout_base64']).decode()) + ')',
        'pvalue_return = PSTRING_CARRIER INTERNED_STRING ($ptascii("ok"))',
        f'z_read = {case["read_line"]}']
    reached += scoped.reach('S_front','S_initial','SG_FRONT z_read')
    reached += ['S_front.ORIGIN = (porigin_site)'] + FRONT
    if protected:
        reached += common.lines(r'''
S_front.CURRENT = (pcallcontext_read)
pcallcontext_read.RECEIVER = eps /\ $this_receiver(S_front) = eps
$property_lookup_scope(S_front) = $closure_source_class(S_front,porigin_site)
ppropertydesc.VISIBILITY = PROPERTY_PROTECTED /\ ppropertydesc.TYPE = eps
ppropertyslot_front.STATE = PROP_UNSET
ppropertyget.DECL = (ppropertydesc.ORIGIN)
$property_get_lookup(S_front,ppropertyget) = PROPERTY_ACCESS ptbytes_key
$property_get_scoped_desc(S_front,ppropertyget) = (ppropertydesc)
''')
    else:
        reached += common.lines(r'''
S_front.CURRENT = eps /\ S_front.FRAMES = eps
$this_receiver(S_front) = eps
ppropertydesc.VISIBILITY = PROPERTY_PRIVATE
ppropertydesc.TYPE = [PTBRANCH ([PTBUILTIN "int"])]
ppropertyslot_front.STATE = PROP_INITIAL
ppropertyget.DECL = eps
$property_resolve(S_front,n_child,ptbytes_name) = PROPERTY_DENIED ppropertydesc
$property_get_lookup(S_front,ppropertyget) = PROPERTY_DENIED ppropertydesc
$property_get_access_desc(S_front,n_child,ptbytes_name,PROPERTY_DENIED ppropertydesc) = eps
$property_get_scoped_desc(S_front,ppropertyget) = eps
''')
    reached += BEGIN
    reached += scoped.reach('S_get','S_begin','SG_ENTER ppropertyget') + ENTER
    if protected:
        reached += scoped.reach('S_populated','S_get','SG_POPULATED ppropertyget ptbytes_key') + common.lines(r'''
S_populated.CURRENT = (pcallcontext_get)
S_populated.FRAMES = pframe_get :: pframe_caller_tail*
$objectprops_at(S_populated.OBJECTPROPS,n_child) = (ppropertyslot_populated_all*)
$property_slot_at(ppropertyslot_populated_all*,ptbytes_key) = (ppropertyslot_populated)
ppropertyslot_populated.DECL = (ppropertydesc.ORIGIN)
ppropertyslot_populated.STATE = PROP_VALUE (DIRECT (PINT 99))
$property_get_lookup(S_populated,ppropertyget) = PROPERTY_ACCESS ptbytes_key
$property_get_scoped_desc(S_populated,ppropertyget) = (ppropertydesc)
$property_get_owned_access(S_populated,n_child,ptbytes_name)
$property_get_history(S_populated,ppropertyget)
$property_get_frame(S_populated,pcallcontext_get,pframe_get)
~$property_get_capture(S_populated,ppropertyget)
$gr_active(S_populated,n_child,ptbytes_name) /\ $gr_guard(S_populated)
''')
    else:
        reached += common.lines(r'''
$property_resolve(S_get,n_child,ptbytes_name) = PROPERTY_ACCESS ptbytes_key
$property_get_lookup(S_get,ppropertyget) = PROPERTY_DENIED ppropertydesc
$property_get_scoped_desc(S_get,ppropertyget) = eps
''')
    reached += scoped.reach('S_result','S_populated' if protected else 'S_get','SG_RESULT ppropertyget')
    reached += common.lines(r'''
$objectprops_at(S_result.OBJECTPROPS,n_child) = (ppropertyslot_result_all*)
$property_slot_at(ppropertyslot_result_all*,ptbytes_key) = (ppropertyslot_result)
''')
    reached += ['ppropertyslot_result.STATE = ' + ('PROP_VALUE (DIRECT (PINT 99))' if protected else 'PROP_INITIAL'),
        '$property_get_scoped_desc(S_result,ppropertyget) = ' + ('(ppropertydesc)' if protected else 'eps')]
    reached += RESULT
    reached += scoped.reach('S_copy','S_copy_pending','SG_TAIL ptask_copy*') + LIFETIME
    reached += scoped.reach('S_base','S_base_pending','SG_TAIL ptask_base*') + BASE
    reached += common.reach('S_dtor','S_release_pending','GR_DTOR n_child') + DTOR
    reached += scoped.reach('S_received','S_dtor','SG_TAIL ptask_tail*') + RECEIVED
    reached += common.FINISH[:-3]
    return reached, common.FINISH[-3:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_get_owned_access_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    assert [case['id'] for case in data['cases']] == ['private-typed', 'protected-populate', 'denied-typed']
    assert [case['id'] for case in data['controls']] == ['public-reference', 'private-initial']
    assert all(sha(HERE / case['source_file']) == case['source_sha256'] for case in data['cases'] + data['controls'])
    selected = [next(case for case in data['cases'] if case['id'] == identifier) for identifier in ('protected-populate', 'denied-typed')]
    php, adapter, bridge, worker, runner, compiler = (ROOT / name for name in [
        '.tools/php/bin/php', '_build/default/adapter/main.exe', '.tools/php-file.so',
        'frontend/worker.php', 'tests/semantics/_build/default/numeric_runner.exe', '.tools/spectec/bin/p4spectec'])
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    assert sha(compiler) == '26d77fb9bfae2b2868e137a94051f55f9b607660c340e9b22ae8300fb0d8ce88'
    assert sha(runner) == 'b57a2ed7daf86de23993a29d079083377cfef6da133739a164dbfdb9f11fd7a0'
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_bytes())]
    watched = [Path(__file__), Path(common.__file__), Path(scoped.__file__), Path(recorder.__file__), catalogue, profile_file,
        php, adapter, bridge, worker, runner, compiler, manifest, *modules,
        *(HERE / case['source_file'] for case in data['cases'] + data['controls']),
        *(ROOT / name for name in ['spec/schema.json', 'spec/php.watsup', 'spec/nodes.json',
            'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py',
            'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py'])]
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    assert revision == args.revision and not status, (revision, status)
    before = {str(path): sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='magic-get-owned-access-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    report = {'revision': revision, 'inputs': before, 'profile': profile, 'module_count': len(modules),
        'mode': 'SL', 'cache': False, 'det': True, 'affinity': sorted(os.sched_getaffinity(0)),
        'records': [], 'fixtures': [],
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
            fixture = directory / 'owned-access.watsup'
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
