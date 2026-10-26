"""Check selected scoped getter declarations, population and caller-site rejection."""
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
syntax psgstage = SG_FRONT int | SG_ENTER ppropertyget | SG_POPULATED ppropertyget ptbytes | SG_RESULT ppropertyget | SG_CATCH | SG_TAIL ptask*
dec $sg_stage(pstate,psgstage) : bool
def $sg_stage(S,SG_FRONT z) = true
  -- if S.TODO = (PROPERTY_PREP (NIdentifier (BYTES text) metadata_name) z) :: (DIM_FETCH z) :: ptask_tail*
  -- if $base64(text) = $ptascii("ghost")
  -- if S.CURRENT =/= eps
def $sg_stage(S,SG_ENTER ppropertyget) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_GET_TARGET ppropertyget.OBJECT ppropertyget.METHOD
  -- if pcallcontext.FUNCTION = ppropertyget.METHOD /\ S.ORIGIN = (ppropertyget.METHOD)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
def $sg_stage(S,SG_POPULATED ppropertyget ptbytes_key) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_GET_TARGET ppropertyget.OBJECT ppropertyget.METHOD
  -- if $objectprops_at(S.OBJECTPROPS,ppropertyget.OBJECT) = (ppropertyslot_all*)
  -- if $property_slot_at(ppropertyslot_all*,ptbytes_key) = (ppropertyslot)
  -- if ppropertyslot.STATE = PROP_VALUE (DIRECT (PINT 99))
def $sg_stage(S,SG_RESULT ppropertyget) = true
  -- if S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
def $sg_stage(S,SG_CATCH) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask_tail*
  -- if S.CURRENT = eps
def $sg_stage(S,SG_TAIL ptask*) = (S.TODO = ptask*)
def $sg_stage(S,psgstage) = false -- otherwise
dec $sg_seek(pstate,psgstage,nat) : pstate
def $sg_seek(S,psgstage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $sg_stage(S,psgstage) \/ n = 0
def $sg_seek(S,psgstage,n) = $sg_seek($drive_steps(S[.COMPLETION = NORMAL],1),psgstage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$sg_stage(S,psgstage) /\ $(n > 0)
def $sg_seek(S,psgstage,n) = $sg_seek($drive_steps(S,1),psgstage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $sg_seek(S,psgstage,n) = S -- otherwise
'''


def reach(name, previous, stage):
    return [f'{name}_found = $sg_seek({previous},{stage},2000)',
            fr'{name}_found.COMPLETION = NORMAL \/ {name}_found.COMPLETION = BUDGET',
            f'{name} = {name}_found[.COMPLETION = NORMAL]', f'$sg_stage({name},{stage})']


FRONT = common.lines(r'''
S_front.CURRENT = (pcallcontext_read)
S_front.FRAMES = pframe_caller_tail*
$property_lookup_scope(S_front) = $closure_source_class(S_front,porigin_site)
$property_get_plan(S_front) = (ppropertyget)
ppropertyget.SITE = porigin_site /\ ppropertyget.LINE = z_read
n_child = ppropertyget.OBJECT
ptbytes_name = ppropertyget.NAME
ptbytes_name = $ptascii("ghost")
ppropertyget.DECL = (ppropertyid)
$property_resolve(S_front,n_child,ptbytes_name) = PROPERTY_ACCESS ptbytes_key
ptbytes_key =/= ptbytes_name
$property_get_access_desc(S_front,n_child,ptbytes_name,PROPERTY_ACCESS ptbytes_key) = (ppropertydesc)
ppropertydesc.KEY = ptbytes_key /\ ppropertydesc.ORIGIN = ppropertyid
ppropertydesc.TYPE = ptbranch_expected* /\ ppropertydesc.VISIBILITY = ppropertyvisibility_expected
$property_get_access_decl(S_front,n_child,ptbytes_name,PROPERTY_ACCESS ptbytes_key) = (ppropertyid)
$property_get_decl(S_front,ppropertyget.CLASS,ptbytes_name) = eps
$property_get_scoped_desc(S_front,ppropertyget) = (ppropertydesc)
$objectprops_at(S_front.OBJECTPROPS,n_child) = (ppropertyslot_front_all*)
$property_slot_at(ppropertyslot_front_all*,ptbytes_key) = (ppropertyslot_front)
ppropertyslot_front.DECL = (ppropertyid) /\ ppropertyslot_front.STATE = PROP_UNSET
$lookup(S_front.ENV,$ptascii("receiver")) = (n_receiver_cell)
S_front.STORE[n_receiver_cell] = DEFINED (POBJECT n_child)
S_front.TODO = (PROPERTY_PREP phpType20_name z_read) :: (DIM_FETCH z_read) :: ptask_tail*
$property_get_history(S_front,ppropertyget) /\ $property_get_capture(S_front,ppropertyget)
~$gr_active(S_front,n_child,ptbytes_name) /\ $gr_guard(S_front)
$gr_output(S_front.EVENTS) = ptbytes_prefix
n_owners_front = $heap_owners($heap_graph(S_front),HOBJECT n_child)
PhpStep: S_front ~> S_begin_raw
S_begin = $gr_after(S_front,S_begin_raw)
S_begin.TODO = (CALL_ARGS (PROPERTY_GET_TARGET n_child ppropertyget.METHOD) eps 1 ([KNOWN (PSTRING ptbytes_name)]) (ppropertyget.SITE) z_read) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
$property_get_pending_call(S_begin,PROPERTY_GET_TARGET n_child ppropertyget.METHOD,ppropertyget.SITE)
$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_child]
$target_nodes(PROPERTY_GET_TARGET n_child ppropertyget.METHOD) = eps
$heap_owners($heap_graph(S_begin),HOBJECT n_child) = $(n_owners_front + 1)
$gr_guard(S_begin)
''')

ENTER = common.lines(r'''
S_get.CURRENT = (pcallcontext_get)
pcallcontext_get.TARGET = PROPERTY_GET_TARGET n_child ppropertyget.METHOD
S_get.FRAMES = pframe_get :: pframe_caller_tail*
pframe_get.CONTEXT = (pcallcontext_read)
pframe_get.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
$property_get_frame(S_get,pcallcontext_get,pframe_get)
$property_get_scoped_desc(S_get,ppropertyget) = (ppropertydesc)
$property_get_history(S_get,ppropertyget)
$gr_active(S_get,n_child,ptbytes_name) /\ $gr_guard(S_get)
$heap_owners($heap_graph(S_get),HOBJECT n_child) = $(n_owners_front + 1)
''')

RESULT = common.lines(r'''
S_result.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
S_result.CURRENT = (pcallcontext_read) /\ S_result.FRAMES = pframe_caller_tail*
S_result.RESULT = KNOWN pvalue_return
$property_get_scoped_desc(S_result,ppropertyget) = (ppropertydesc)
$property_get_history(S_result,ppropertyget) /\ $property_get_valid(S_result,ppropertyget,true)
~$gr_active(S_result,n_child,ptbytes_name) /\ $gr_guard(S_result)
$gr_output(S_result.EVENTS) = ptbytes_prefix ++ $ptascii("G|")
PhpStep: S_result ~> S_verified_raw
S_verified_raw.TODO = (PROPERTY_GET_COPY ppropertyget (KNOWN pvalue_return)) :: ptask_tail*
S_verified_raw.RESULT = KNOWN PNULL
''')


def conditions(case, checked):
    reject = case['id'] == 'private-reject'
    prefix = 'B:' if reject else 'T:'
    reached = [
        'S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(HERE / case['source_file']).encode()).decode()) + ')',
        r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
        'ptbytes_file = $ptascii(' + json.dumps(str(HERE / case['source_file'])) + ')',
        'ptbytes_prefix = $ptascii(' + json.dumps(prefix) + ')',
        'ptbytes_final = $ptascii(' + json.dumps(base64.b64decode(case['stdout_base64']).decode()) + ')',
        'pvalue_return = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps('bad' if reject else 'ok') + '))',
        'ppropertyvisibility_expected = ' + ('PROPERTY_PRIVATE' if reject else 'PROPERTY_PROTECTED'),
        'ptbranch_expected* = ' + ('[(PTBRANCH ([PTBUILTIN "int"]))]' if reject else 'eps'),
        f'z_read = {case["read_line"]}']
    reached += reach('S_front', 'S_initial', 'SG_FRONT z_read')
    reached += ['S_front.ORIGIN = (porigin_site)'] + FRONT
    reached += reach('S_get', 'S_begin', 'SG_ENTER ppropertyget') + ENTER
    if not reject:
        reached += reach('S_populated', 'S_get', 'SG_POPULATED ppropertyget ptbytes_key') + common.lines(r'''
S_populated.CURRENT = (pcallcontext_get)
S_populated.FRAMES = pframe_get :: pframe_caller_tail*
$objectprops_at(S_populated.OBJECTPROPS,n_child) = (ppropertyslot_populated_all*)
$property_slot_at(ppropertyslot_populated_all*,ptbytes_key) = (ppropertyslot_populated)
ppropertyslot_populated.DECL = (ppropertyid) /\ ppropertyslot_populated.STATE = PROP_VALUE (DIRECT (PINT 99))
$property_get_scoped_desc(S_populated,ppropertyget) = (ppropertydesc)
$property_get_history(S_populated,ppropertyget) /\ $property_get_frame(S_populated,pcallcontext_get,pframe_get)
~$property_get_capture(S_populated,ppropertyget)
$gr_active(S_populated,n_child,ptbytes_name) /\ $gr_guard(S_populated)
''')
    reached += reach('S_result', 'S_get' if reject else 'S_populated', 'SG_RESULT ppropertyget') + RESULT
    if reject:
        message = 'Value of type string returned from RejectParent123::__get() must be compatible with unset property RejectParent123::$ghost of type int'
        reached += ['ptbytes_message = $ptascii(' + json.dumps(message) + ')'] + common.lines(r'''
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
        reached += reach('S_catch', 'S_pending', 'SG_CATCH') + common.lines(r'''
S_catch.TODO = (CATCH_BIND porigin_catch n_catch_index n_error) :: ptask_catch_tail*
S_catch.CURRENT = eps /\ S_catch.FRAMES = eps
$gr_output(S_catch.EVENTS) = ptbytes_prefix ++ $ptascii("G|")
$lookup(S_catch.ENV,$ptascii("result")) = (n_result_cell)
S_catch.STORE[n_result_cell] = DEFINED (PINT 42)
$throwable_object_image_valid(S_catch,n_error) /\ $gr_guard(S_catch)
S_end = S_catch
''')
    else:
        reached += common.lines(r'''
S_verified_raw.COMPLETION = NORMAL
$property_get_verify(S_result,ppropertyget,S_result.RESULT) = S_result
S_copy_pending = $gr_after(S_result,S_verified_raw)
ptask_copy* = (PROPERTY_GET_COPY ppropertyget (KNOWN pvalue_return)) :: ptask_tail*
''')
        reached += reach('S_copy', 'S_copy_pending', 'SG_TAIL ptask_copy*') + common.lines(r'''
PhpStep: S_copy ~> S_copy_raw
S_copy_raw.TODO = ptask_tail* /\ S_copy_raw.RESULT = KNOWN pvalue_return
S_read_pending = $gr_after(S_copy,S_copy_raw)
''')
        reached += reach('S_read', 'S_read_pending', 'SG_TAIL ptask_tail*') + common.lines(r'''
S_read.RESULT = KNOWN pvalue_return
S_read.CURRENT = (pcallcontext_read) /\ S_read.FRAMES = pframe_caller_tail*
$objectprops_at(S_read.OBJECTPROPS,n_child) = (ppropertyslot_read_all*)
$property_slot_at(ppropertyslot_read_all*,ptbytes_key) = (ppropertyslot_read)
ppropertyslot_read.DECL = (ppropertyid) /\ ppropertyslot_read.STATE = PROP_VALUE (DIRECT (PINT 99))
$heap_owners($heap_graph(S_read),HOBJECT n_child) = n_owners_front
$gr_guard(S_read)
S_end = S_read
''')
    reached += common.FINISH[:-3]
    derived = ['S_budget = $drive_steps(S_front,0)', 'S_budget = S_front[.COMPLETION = BUDGET]',
               '$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final']
    return reached, derived

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_get_scoped_unset_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    assert [case['id'] for case in data['cases']] == ['private-shadow', 'private-reject', 'protected-populate']
    assert [case['id'] for case in data['controls']] == ['private-initial']
    assert all(sha(HERE / case['source_file']) == case['source_sha256'] for case in data['cases'] + data['controls'])
    selected = [case for case in data['cases'] if case['id'] in ('private-reject', 'protected-populate')]
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
    out = Path(tempfile.mkdtemp(prefix='magic-get-scoped-unset-protocol-', dir=ROOT / '.tools'))
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
            fixture = directory / 'scoped-unset.watsup'
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
