"""Check selected Parent Get types across public shadow and owned retirement."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import error_handler_run as recorder
import magic_get_recursion_protocol as common
import magic_get_scoped_unset_protocol as scoped
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()
PREFIX = scoped.PREFIX

FRONT = common.lines(r'''
S_front.CURRENT = (pcallcontext_read)
S_front.RESULT = KNOWN (POBJECT n_child)
S_front.FRAMES = pframe_caller_tail*
pcallcontext_read.LEXICAL_CLASS = (porigin_parent)
$closure_source_class(S_front,porigin_site) = (porigin_parent)
$property_get_plan(S_front) = (ppropertyget)
ppropertyget.OBJECT = n_child /\ ppropertyget.SITE = porigin_site /\ ppropertyget.LINE = z_read
ptbytes_name = ppropertyget.NAME
ptbytes_name = $ptascii("ghost")
$property_get_public(S_front,n_child,ptbytes_name)
$property_effective_desc(S_front,n_child,ptbytes_name) = (ppropertydesc_child)
ppropertydesc_child.KEY = ptbytes_name /\ ppropertydesc_child.VISIBILITY = PROPERTY_PUBLIC
ppropertydesc_child.TYPE = [PTBRANCH ([PTBUILTIN "string"])]
$property_resolve(S_front,n_child,ptbytes_name) = PROPERTY_ACCESS ptbytes_parent_key
$property_get_lookup(S_front,ppropertyget) = PROPERTY_ACCESS ptbytes_parent_key
$property_get_access_desc(S_front,n_child,ptbytes_name,PROPERTY_ACCESS ptbytes_parent_key) = (ppropertydesc_parent)
ppropertydesc_parent.KEY = ptbytes_parent_key /\ ptbytes_parent_key =/= ptbytes_name
ppropertydesc_parent.VISIBILITY = PROPERTY_PRIVATE /\ ppropertydesc_parent.TYPE = [PTBRANCH ([PTBUILTIN "int"])]
ppropertyget.DECL = (ppropertydesc_parent.ORIGIN)
$property_get_decl(S_front,ppropertyget.CLASS,ptbytes_name) = (ppropertydesc_child.ORIGIN)
ppropertydesc_parent.ORIGIN =/= ppropertydesc_child.ORIGIN
$property_get_scoped_desc(S_front,ppropertyget) = (ppropertydesc_parent)
$objectprops_at(S_front.OBJECTPROPS,n_child) = (ppropertyslot_front_all*)
$property_slot_at(ppropertyslot_front_all*,ptbytes_parent_key) = (ppropertyslot_parent)
ppropertyslot_parent.DECL = ppropertyget.DECL /\ ppropertyslot_parent.STATE = PROP_UNSET
$property_slot_at(ppropertyslot_front_all*,ptbytes_name) = (ppropertyslot_child)
ppropertyslot_child.DECL = (ppropertydesc_child.ORIGIN)
ppropertyslot_child.STATE = PROP_VALUE pitem_child
$string_bytes($entry_read_value(S_front,pitem_child)) = ($ptascii("hidden"))
$property_get_history(S_front,ppropertyget) /\ $property_get_capture(S_front,ppropertyget)
S_front.TODO = (PROPERTY_PREP phpType20_name z_read) :: (DIM_FETCH z_read) :: ptask_tail*
~$gr_active(S_front,n_child,ptbytes_name) /\ $gr_guard(S_front)
n_owners_front = $heap_owners($heap_graph(S_front),HOBJECT n_child)
$gr_output(S_front.EVENTS) = ptbytes_prefix
''')
BEGIN = common.lines(r'''
PhpStep: S_front ~> S_begin_raw
S_begin = $gr_after(S_front,S_begin_raw)
S_begin.TODO = [CALL_ARGS (PROPERTY_GET_TARGET n_child ppropertyget.METHOD) eps 1 ([KNOWN (PSTRING ptbytes_name)]) (porigin_site) z_read, PROPERTY_GET_RESULT ppropertyget] ++ ptask_base* ++ ptask_tail*
$property_get_pending_call(S_begin,PROPERTY_GET_TARGET n_child ppropertyget.METHOD,porigin_site)
$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_child]
$target_nodes(PROPERTY_GET_TARGET n_child ppropertyget.METHOD) = eps
$property_get_tail_valid(S_begin,ppropertyget) /\ $gr_guard(S_begin)
''')
ENTER = common.lines(r'''
S_get.CURRENT = (pcallcontext_get)
pcallcontext_get.TARGET = PROPERTY_GET_TARGET n_child ppropertyget.METHOD
S_get.FRAMES = pframe_get :: pframe_caller_tail*
pframe_get.CONTEXT = (pcallcontext_read)
pframe_get.TODO = [PROPERTY_GET_RESULT ppropertyget] ++ ptask_base* ++ ptask_tail*
$property_get_frame(S_get,pcallcontext_get,pframe_get)
$property_lookup_scope(S_get) =/= $closure_source_class(S_get,porigin_site)
$property_resolve(S_get,n_child,ptbytes_name) = PROPERTY_ACCESS ptbytes_name
$property_get_lookup(S_get,ppropertyget) = PROPERTY_ACCESS ptbytes_parent_key
$property_get_scoped_desc(S_get,ppropertyget) = (ppropertydesc_parent)
$property_get_history(S_get,ppropertyget)
$gr_active(S_get,n_child,ptbytes_name) /\ $gr_guard(S_get)
''')
RESULT = common.lines(r'''
S_result.TODO = [PROPERTY_GET_RESULT ppropertyget] ++ ptask_base* ++ ptask_tail*
S_result.CURRENT = (pcallcontext_read) /\ S_result.FRAMES = pframe_caller_tail*
S_result.RESULT = KNOWN pvalue_raw
$property_get_scoped_desc(S_result,ppropertyget) = (ppropertydesc_parent)
$property_get_history(S_result,ppropertyget) /\ $property_get_valid(S_result,ppropertyget,true)
~$gr_active(S_result,n_child,ptbytes_name) /\ $gr_guard(S_result)
$gr_output(S_result.EVENTS) = ptbytes_prefix ++ $ptascii("G|")
''')

def conditions(case, checked):
    owned = case['id'] == 'owned-priority'
    reached = [
        'S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(HERE / case['source_file']).encode()).decode()) + ')',
        r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
        'ptbytes_file = $ptascii(' + json.dumps(str(HERE / case['source_file'])) + ')',
        'ptbytes_prefix = $ptascii(' + json.dumps('F:' if owned else 'T:') + ')',
        'ptbytes_final = $ptascii(' + json.dumps(base64.b64decode(case['stdout_base64']).decode()) + ')',
        'pvalue_raw = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps('7' if owned else 'bad') + '))',
        'z_read = ' + str(case['read_line'])]
    reached += scoped.reach('S_front','S_initial','SG_FRONT z_read')
    reached += ['S_front.ORIGIN = (porigin_site)'] + FRONT
    if owned:
        reached += common.lines(r'''
pcallcontext_read.RECEIVER = eps /\ $this_receiver(S_front) = eps
$call_receiver_roots(pcallcontext_read) = eps
$property_get_owned_source(S_front,ppropertyget)
~$property_get_this_source(S_front,ppropertyget)
ptask_base* = [PROPERTY_GET_BASE ppropertyget]
$property_get_base_tasks(S_front,ppropertyget) = ptask_base*
n_owners_front = 1
''')
    else:
        reached += common.lines(r'''
pcallcontext_read.RECEIVER = (n_child) /\ $this_receiver(S_front) = (n_child)
$call_receiver_roots(pcallcontext_read) = [HOBJECT n_child]
$property_get_this_source(S_front,ppropertyget)
~$property_get_owned_source(S_front,ppropertyget)
ptask_base* = eps
$property_get_base_tasks(S_front,ppropertyget) = eps
''')
    reached += BEGIN
    reached += ['$heap_owners($heap_graph(S_begin),HOBJECT n_child) = ' + ('$(n_owners_front + 1)' if owned else 'n_owners_front')]
    reached += scoped.reach('S_get','S_begin','SG_ENTER ppropertyget') + ENTER
    reached += ['$heap_owners($heap_graph(S_get),HOBJECT n_child) = ' + ('$(n_owners_front + 1)' if owned else 'n_owners_front')]
    reached += scoped.reach('S_result','S_get','SG_RESULT ppropertyget') + RESULT
    if owned:
        reached += common.lines(r'''
$property_get_verify(S_result,ppropertyget,S_result.RESULT) = S_result[.RESULT = KNOWN (PINT 7)]
PhpStep: S_result ~> S_copy_raw
S_copy_raw.TODO = [PROPERTY_GET_COPY ppropertyget (KNOWN (PINT 7)), PROPERTY_GET_BASE ppropertyget] ++ ptask_tail*
S_copy_raw.RESULT = KNOWN PNULL /\ S_copy_raw.COMPLETION = NORMAL
S_copy_pending = $gr_after(S_result,S_copy_raw)
ptask_copy* = S_copy_raw.TODO
''')
        reached += scoped.reach('S_copy','S_copy_pending','SG_TAIL ptask_copy*')
        reached += common.lines(r'''
S_copy.CURRENT = (pcallcontext_read) /\ S_copy.FRAMES = pframe_caller_tail*
$heap_owners($heap_graph(S_copy),HOBJECT n_child) = n_owners_front
$property_get_base_valid(S_copy,ppropertyget)
~$gr_active(S_copy,n_child,ptbytes_name) /\ $gr_guard(S_copy)
PhpStep: S_copy ~> S_copied_raw
S_copied_raw.TODO = (PROPERTY_GET_BASE ppropertyget) :: ptask_tail*
S_copied_raw.RESULT = KNOWN (PINT 7)
S_base_pending = $gr_after(S_copy,S_copied_raw)
ptask_base_tail* = S_copied_raw.TODO
''')
        reached += scoped.reach('S_base','S_base_pending','SG_TAIL ptask_base_tail*')
        reached += common.lines(r'''
S_base.RESULT = KNOWN (PINT 7)
S_base.CURRENT = (pcallcontext_read)
$heap_owners($heap_graph(S_base),HOBJECT n_child) = 1
$property_get_base_valid(S_base,ppropertyget)
$gr_output(S_base.EVENTS) = $ptascii("F:G|")
~$gr_active(S_base,n_child,ptbytes_name) /\ $gr_guard(S_base)
PhpStep: S_base ~> S_released_raw
S_released_raw.TODO = ptask_tail* /\ S_released_raw.RESULT = KNOWN (PINT 7)
S_release_pending = $gr_after(S_base,S_released_raw)
''')
        reached += common.reach('S_dtor','S_release_pending','GR_DTOR n_child')
        reached += common.lines(r'''
S_dtor.CURRENT = (pcallcontext_dtor)
$destructor_context_call(pcallcontext_dtor,S_dtor.CURRENT,S_dtor.FRAMES) = (pdestructorcall)
pdestructorcall.OBJECT = n_child
pdestructorcall.OPERATION = (pdestructionoperation)
pdestructionoperation.SOURCE = PROPERTY_GET_BASE ppropertyget
pdestructionoperation.VALUE = KNOWN (PINT 7)
pdestructionoperation.CALLER = (pcallcontext_read) /\ pdestructionoperation.PENDING = eps
$gr_output(S_dtor.EVENTS) = $ptascii("F:G|")
~$gr_active(S_dtor,n_child,ptbytes_name) /\ $gr_guard(S_dtor)
''')
        reached += scoped.reach('S_received','S_dtor','SG_TAIL ptask_tail*')
        reached += common.lines(r'''
S_received.RESULT = KNOWN (PINT 7)
S_received.CURRENT = (pcallcontext_read) /\ S_received.FRAMES = pframe_caller_tail*
~((HOBJECT n_child) <- S_received.ALLOCATIONS)
$gr_output(S_received.EVENTS) = $ptascii("F:G|D|")
$property_get_base_count(S_received.TODO,n_child,porigin_site) = 0
$gr_guard(S_received)
S_end = S_received
''')
    else:
        message = 'Value of type string returned from RejectParent125::__get() must be compatible with unset property RejectParent125::$ghost of type int'
        reached += ['ptbytes_message = $ptascii(' + json.dumps(message) + ')'] + common.lines(r'''
PhpStep: S_result ~> S_verified_raw
S_verified_raw.TODO = (PROPERTY_GET_COPY ppropertyget (KNOWN pvalue_raw)) :: ptask_tail*
S_verified_raw.RESULT = KNOWN PNULL
S_verified_raw.COMPLETION = THROWN "TypeError" ptbytes_message z_read
S_material = $throwable_transition(S_result,S_verified_raw)
S_material.COMPLETION = THROWING n_error
S_material.OBJECTS[n_error] = THROWABLE pthrowable_error
S_material.OBJECTS = S_result.OBJECTS ++ [THROWABLE pthrowable_error]
n_error = |S_result.OBJECTS|
pthrowable_error.KIND = "TypeError" /\ pthrowable_error.ORIGIN = (porigin_site)
$throwable_field(S_material,n_error,"message") = PSTRING ptbytes_message
$throwable_field(S_material,n_error,"file") = PSTRING ptbytes_file
$throwable_field(S_material,n_error,"line") = PINT z_read
$throwable_field(S_material,n_error,"previous") = PNULL
$throwable_object_image_valid(S_material,n_error)
S_pending = $gr_after(S_result,S_verified_raw)
''')
        reached += scoped.reach('S_catch','S_pending','SG_CATCH')
        reached += common.lines(r'''
S_catch.TODO = (CATCH_BIND porigin_catch n_catch_index n_error) :: ptask_catch_tail*
S_catch.CURRENT = eps /\ S_catch.FRAMES = eps
$gr_output(S_catch.EVENTS) = $ptascii("T:G|")
$lookup(S_catch.ENV,$ptascii("result")) = (n_result_cell)
S_catch.STORE[n_result_cell] = DEFINED (PINT 42)
(HOBJECT n_child) <- S_catch.ALLOCATIONS
$throwable_object_image_valid(S_catch,n_error)
~$gr_active(S_catch,n_child,ptbytes_name) /\ $gr_guard(S_catch)
S_end = S_catch
''')
    reached += common.FINISH[:-3]
    derived = common.FINISH[-3:]
    return reached, derived


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_get_lexical_selection_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    assert [case['id'] for case in data['cases']] == ['cv-priority', 'this-reject', 'owned-priority']
    assert [case['id'] for case in data['controls']] == ['initial-bypass', 'public-fallback']
    assert all(sha(HERE / case['source_file']) == case['source_sha256'] for case in data['cases'] + data['controls'])
    selected = [next(case for case in data['cases'] if case['id'] == identifier) for identifier in ('owned-priority', 'this-reject')]
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
    out = Path(tempfile.mkdtemp(prefix='magic-get-lexical-selection-protocol-', dir=ROOT / '.tools'))
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
            fixture = directory / 'lexical-selection.watsup'
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
