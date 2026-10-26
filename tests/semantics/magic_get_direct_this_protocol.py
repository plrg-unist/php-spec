"""Check literal-this Get history through a handler and borrowed method lifetime."""
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

PREFIX = scoped.PREFIX + r'''
syntax pthstage = TH_HANDLER ptbytes | TH_CLEARED ppropertyget
dec $th_stage(pstate,pthstage) : bool
def $th_stage(S,TH_HANDLER ptbytes) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = eps
  -- if $gr_output(S.EVENTS) = ptbytes
def $th_stage(S,TH_CLEARED ppropertyget) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_GET_TARGET ppropertyget.OBJECT ppropertyget.METHOD
  -- if S.GLOBALTABLE = (psymboltable)
  -- if $lookup(psymboltable.ENV,$ptascii("child")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED PNULL
  -- if $gr_output(S.EVENTS) = $ptascii("L:G|g|")
def $th_stage(S,pthstage) = false -- otherwise
dec $th_seek(pstate,pthstage,nat) : pstate
def $th_seek(S,pthstage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $th_stage(S,pthstage) \/ n = 0
def $th_seek(S,pthstage,n) = $th_seek($drive_steps(S[.COMPLETION = NORMAL],1),pthstage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$th_stage(S,pthstage) /\ $(n > 0)
def $th_seek(S,pthstage,n) = S -- otherwise
'''

def th_reach(name, previous, stage):
    return [f'{name}_found = $th_seek({previous},{stage},2000)',
            r'%s_found.COMPLETION = NORMAL \/ %s_found.COMPLETION = BUDGET' % (name, name),
            f'{name} = {name}_found[.COMPLETION = NORMAL]', f'$th_stage({name},{stage})']

FRONT = common.lines(r'''
S_front.CURRENT = (pcallcontext_read)
pcallcontext_read.TARGET = METHOD_TARGET n_child porigin_read
pcallcontext_read.RECEIVER = (n_child) /\ $this_receiver(S_front) = (n_child)
S_front.FRAMES = pframe_caller_tail*
S_front.RESULT = KNOWN (POBJECT n_child) /\ S_front.BASE = BASE_VALUE (KNOWN PNULL)
$lookup(S_front.ENV,$ptascii("this")) = eps
$property_get_plan(S_front) = (ppropertyget)
ppropertyget.OBJECT = n_child /\ ppropertyget.SITE = porigin_site /\ ppropertyget.LINE = z_outer
ptbytes_name = ppropertyget.NAME
ptbytes_name = $ptascii("ghost")
$property_effective_desc(S_front,n_child,ptbytes_name) = (ppropertydesc)
ppropertyget.DECL = (ppropertydesc.ORIGIN)
ppropertydesc.TYPE = eps /\ ppropertydesc.VISIBILITY = PROPERTY_PUBLIC /\ ppropertydesc.KEY = ptbytes_name
$objectprops_at(S_front.OBJECTPROPS,n_child) = (ppropertyslot_front_all*)
$property_slot_at(ppropertyslot_front_all*,ptbytes_name) = (ppropertyslot_front)
ppropertyslot_front.DECL = ppropertyget.DECL /\ ppropertyslot_front.STATE = PROP_UNSET
$property_get_this_source(S_front,ppropertyget) /\ $property_get_source(S_front,ppropertyget)
$property_get_capture(S_front,ppropertyget) /\ $property_get_history(S_front,ppropertyget)
~$property_get_owned_source(S_front,ppropertyget) /\ $property_get_base_tasks(S_front,ppropertyget) = eps
S_front.TODO = (PROPERTY_PREP phpType20_outer z_outer) :: (DIM_FETCH z_outer) :: ptask_tail*
~$gr_active(S_front,n_child,ptbytes_name) /\ $gr_guard(S_front)
$gr_output(S_front.EVENTS) = ptbytes_prefix
n_owners_front = $heap_owners($heap_graph(S_front),HOBJECT n_child)
$call_receiver_roots(pcallcontext_read) = [HOBJECT n_child]
PhpStep: S_front ~> S_begin_raw
S_begin = $gr_after(S_front,S_begin_raw)
S_begin.TODO = (CALL_ARGS (PROPERTY_GET_TARGET n_child ppropertyget.METHOD) eps 1 ([KNOWN (PSTRING ptbytes_name)]) (ppropertyget.SITE) z_outer) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
$property_get_pending_call(S_begin,PROPERTY_GET_TARGET n_child ppropertyget.METHOD,ppropertyget.SITE)
$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_child]
$target_nodes(PROPERTY_GET_TARGET n_child ppropertyget.METHOD) = eps
$heap_owners($heap_graph(S_begin),HOBJECT n_child) = n_owners_front
$property_get_base_count(S_begin.TODO,n_child,porigin_site) = 0
$gr_guard(S_begin)
''')
ENTER = common.lines(r'''
S_get.CURRENT = (pcallcontext_get)
pcallcontext_get.TARGET = PROPERTY_GET_TARGET n_child ppropertyget.METHOD
S_get.FRAMES = pframe_get :: pframe_caller_tail*
pframe_get.CONTEXT = (pcallcontext_read)
pframe_get.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
$lookup(S_get.ENV,$ptascii("name")) = (n_name_cell)
S_get.STORE[n_name_cell] = DEFINED (PSTRING ptbytes_name)
$property_get_frame(S_get,pcallcontext_get,pframe_get)
$property_get_this_source(S_get,ppropertyget) /\ $property_get_history(S_get,ppropertyget)
$call_receiver_roots(pcallcontext_get) = eps
$gr_active(S_get,n_child,ptbytes_name) /\ $gr_guard(S_get)
$heap_owners($heap_graph(S_get),HOBJECT n_child) = n_owners_front
''')
RESULT = common.lines(r'''
S_result.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
S_result.CURRENT = (pcallcontext_read) /\ S_result.FRAMES = pframe_caller_tail*
S_result.RESULT = KNOWN pvalue_return
$property_get_this_source(S_result,ppropertyget) /\ $property_get_valid(S_result,ppropertyget,true)
$property_get_verify(S_result,ppropertyget,S_result.RESULT) = S_result
~$gr_active(S_result,n_child,ptbytes_name) /\ $gr_guard(S_result)
$gr_output(S_result.EVENTS) = ptbytes_before_result
PhpStep: S_result ~> S_copy_raw
S_copy_raw.TODO = (PROPERTY_GET_COPY ppropertyget (KNOWN pvalue_return)) :: ptask_tail*
S_copy_raw.RESULT = KNOWN PNULL
$task_nodes(PROPERTY_GET_COPY ppropertyget (KNOWN pvalue_return)) = eps
S_copy_pending = $gr_after(S_result,S_copy_raw)
ptask_copy* = S_copy_raw.TODO
''')
COPY = common.lines(r'''
S_copy.TODO = ptask_copy*
S_copy.CURRENT = (pcallcontext_read) /\ S_copy.FRAMES = pframe_caller_tail*
~$gr_active(S_copy,n_child,ptbytes_name) /\ $gr_guard(S_copy)
$property_get_base_count(S_copy.TODO,n_child,porigin_site) = 0
$call_task_valid(S_copy,PROPERTY_GET_COPY ppropertyget (KNOWN pvalue_return))
PhpStep: S_copy ~> S_copied_raw
S_copied_raw.TODO = ptask_tail* /\ S_copied_raw.RESULT = KNOWN pvalue_return
S_read_pending = $gr_after(S_copy,S_copied_raw)
''')

def conditions(case, checked):
    recursive = case['id'] == 'recursive-handler'
    reached = [
        'S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(HERE / case['source_file']).encode()).decode()) + ')',
        r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
        'ptbytes_prefix = $ptascii(' + json.dumps('R:' if recursive else 'L:') + ')',
        'ptbytes_final = $ptascii(' + json.dumps(base64.b64decode(case['stdout_base64']).decode()) + ')',
        'pvalue_return = ' + ('PNULL' if recursive else 'PINT 7'),
        'z_outer = ' + str(case['outer_line'] if recursive else case['read_line'])]
    reached += scoped.reach('S_front','S_initial','SG_FRONT z_outer')
    reached += ['S_front.ORIGIN = (porigin_site)'] + FRONT
    reached += scoped.reach('S_get','S_begin','SG_ENTER ppropertyget') + ENTER
    if recursive:
        warning = 'W|severity|message|line|file|w|'
        reached += ['z_inner = ' + str(case['read_line'])]
        reached += scoped.reach('S_inner','S_get','SG_FRONT z_inner') + common.INNER
        reached += [
            'n_warning_owners = n_owners_front',
            'n_after_warning_owners = n_owners_front',
            'ptbytes_before_warning = $ptascii("R:G|")',
            'ptbytes_after_warning = $ptascii(' + json.dumps('R:G|' + warning) + ')']
        reached += common.reach('S_invoke','S_invoke_pending','GR_INVOKE')
        reached += [row.replace('RecursiveGet119','RecursiveThis124') for row in common.INVOKE]
        reached += th_reach('S_handler_body','S_invoke','TH_HANDLER ptbytes_after_warning')
        reached += common.lines(r'''
S_handler_body.CURRENT = (pcallcontext_handler)
pcallcontext_handler.RECEIVER = eps /\ $this_receiver(S_handler_body) = eps
$call_receiver_roots(pcallcontext_handler) = eps
$property_get_this_source(S_handler_body,ppropertyget)
$property_get_history(S_handler_body,ppropertyget) /\ $property_get_valid(S_handler_body,ppropertyget,true)
$property_get_entered(S_handler_body,S_handler_body.CURRENT,S_handler_body.FRAMES,PROPERTY_GET_TARGET n_child ppropertyget.METHOD,porigin_site)
$error_context_anchor(S_handler_body,pcallcontext_handler,S_handler_body.CURRENT,S_handler_body.FRAMES)
S_handler_body.ORIGIN =/= (ppropertywarning.READ.SITE)
~$property_get_recursive_history(S_handler_body,ppropertywarning)
$gr_active(S_handler_body,n_child,ptbytes_name) /\ $gr_guard(S_handler_body)
$objectprops_at(S_handler_body.OBJECTPROPS,n_child) = (ppropertyslot_populated_all*)
$property_slot_at(ppropertyslot_populated_all*,ptbytes_name) = (ppropertyslot_populated)
ppropertyslot_populated.DECL = ppropertyget.DECL /\ ppropertyslot_populated.STATE = PROP_VALUE (DIRECT (PINT 9))
~$property_undefined_slot(S_handler_body,n_child,ptbytes_name)
~$property_get_needed(S_handler_body,n_child,ptbytes_name)
~$property_get_capture(S_handler_body,ppropertyget)
''')
        reached += common.reach('S_handler','S_handler_body','GR_HANDLER') + common.HANDLER
        reached += common.reach('S_resume','S_handler','GR_WARNING_RESULT') + common.RESUME
        reached += ['ptbytes_before_result = $ptascii(' + json.dumps('R:G|' + warning + 'g|') + ')']
    else:
        reached += th_reach('S_cleared','S_get','TH_CLEARED ppropertyget')
        reached += common.lines(r'''
S_cleared.CURRENT = (pcallcontext_get)
S_cleared.FRAMES = pframe_get :: pframe_caller_tail*
S_cleared.GLOBALTABLE = (psymboltable_global)
$lookup(psymboltable_global.ENV,$ptascii("child")) = (n_child_cell)
S_cleared.STORE[n_child_cell] = DEFINED PNULL
(HOBJECT n_child) <- S_cleared.ALLOCATIONS
$property_get_history(S_cleared,ppropertyget) /\ $property_get_frame(S_cleared,pcallcontext_get,pframe_get)
$call_receiver_roots(pcallcontext_read) = [HOBJECT n_child]
$heap_owners($heap_graph(S_cleared),HOBJECT n_child) = $(n_owners_front - 1)
$gr_active(S_cleared,n_child,ptbytes_name) /\ $gr_guard(S_cleared)
ptbytes_before_result = $ptascii("L:G|g|")
''')
    reached += scoped.reach('S_result','S_read' if recursive else 'S_cleared','SG_RESULT ppropertyget') + RESULT
    reached += scoped.reach('S_copy','S_copy_pending','SG_TAIL ptask_copy*') + COPY
    reached += scoped.reach('S_read_value','S_read_pending','SG_TAIL ptask_tail*')
    reached += common.lines(r'''
S_read_value.RESULT = KNOWN pvalue_return
S_read_value.CURRENT = (pcallcontext_read) /\ S_read_value.FRAMES = pframe_caller_tail*
$call_receiver_roots(pcallcontext_read) = [HOBJECT n_child]
(HOBJECT n_child) <- S_read_value.ALLOCATIONS
~$gr_active(S_read_value,n_child,ptbytes_name) /\ $gr_guard(S_read_value)
$gr_output(S_read_value.EVENTS) = ptbytes_before_result
''')
    if recursive:
        reached += common.lines(r'''
$heap_owners($heap_graph(S_read_value),HOBJECT n_child) = $(n_owners_front - 1)
$objectprops_at(S_read_value.OBJECTPROPS,n_child) = (ppropertyslot_read_all*)
$property_slot_at(ppropertyslot_read_all*,ptbytes_name) = (ppropertyslot_populated)
''')
        reached += scoped.reach('S_again','S_read_value','SG_FRONT z_outer')
        reached += common.lines(r'''
S_again.CURRENT = (pcallcontext_read_again)
pcallcontext_read_again.TARGET = METHOD_TARGET n_child porigin_read
$this_receiver(S_again) = (n_child) /\ S_again.RESULT = KNOWN (POBJECT n_child)
$property_get_plan(S_again) = (ppropertyget)
$property_get_capture(S_again,ppropertyget) /\ $property_get_this_source(S_again,ppropertyget)
$objectprops_at(S_again.OBJECTPROPS,n_child) = (ppropertyslot_again_all*)
$property_slot_at(ppropertyslot_again_all*,ptbytes_name) = (ppropertyslot_front)
~$gr_active(S_again,n_child,ptbytes_name) /\ $gr_guard(S_again)
$gr_output(S_again.EVENTS) = ptbytes_before_result ++ $ptascii("A|null|9|")
S_end = S_again
''')
    else:
        reached += common.lines(r'''
$heap_owners($heap_graph(S_copy),HOBJECT n_child) = $(n_owners_front - 2)
$heap_owners($heap_graph(S_read_value),HOBJECT n_child) = $(n_owners_front - 2)
S_read_value.STORE[n_child_cell] = DEFINED PNULL
''')
        reached += common.reach('S_marker','S_read_value','GR_OUTPUT ($ptascii("L:G|g|m|"))')
        reached += common.lines(r'''
S_marker.CURRENT = (pcallcontext_read)
(HOBJECT n_child) <- S_marker.ALLOCATIONS
$call_receiver_roots(pcallcontext_read) = [HOBJECT n_child]
$heap_owners($heap_graph(S_marker),HOBJECT n_child) = $(n_owners_front - 2)
~$gr_active(S_marker,n_child,ptbytes_name) /\ $gr_guard(S_marker)
''')
        reached += common.reach('S_dtor','S_marker','GR_DTOR n_child')
        reached += common.lines(r'''
S_dtor.CURRENT = (pcallcontext_dtor)
$destructor_context_call(pcallcontext_dtor,S_dtor.CURRENT,S_dtor.FRAMES) = (pdestructorcall)
pdestructorcall.OBJECT = n_child
$gr_output(S_dtor.EVENTS) = $ptascii("L:G|g|m|")
~$gr_active(S_dtor,n_child,ptbytes_name) /\ $gr_guard(S_dtor)
S_end = S_dtor
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
    catalogue = HERE / 'magic_get_direct_this_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    assert [case['id'] for case in data['cases']] == ['private-shadow', 'private-reject', 'recursive-handler', 'borrowed-lifetime']
    assert [case['id'] for case in data['controls']] == ['private-initial']
    assert all(sha(HERE / case['source_file']) == case['source_sha256'] for case in data['cases'] + data['controls'])
    selected = [case for case in data['cases'] if case['id'] in ('recursive-handler', 'borrowed-lifetime')]
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
    out = Path(tempfile.mkdtemp(prefix='magic-get-direct-this-protocol-', dir=ROOT / '.tools'))
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
            fixture = directory / 'direct-this.watsup'
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
