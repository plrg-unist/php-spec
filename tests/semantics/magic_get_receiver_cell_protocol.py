"""Check receiver-cell retargeting before COPY and pending input retirement."""
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
PREFIX = scoped.PREFIX

FRONT = common.lines(r"""
S_front.CURRENT = eps /\ S_front.FRAMES = eps
S_front.ORIGIN = (porigin_site)
S_front.TODO = (PROPERTY_PREP phpType20_name z_read) :: (DIM_FETCH z_read) :: ptask_tail*
S_front.RESULT = REFERENCE n_receiver
$call_reference_operand_valid(S_front,S_front.RESULT)
S_front.STORE[n_receiver] = DEFINED (POBJECT n_target)
$property_get_plan(S_front) = (ppropertyget)
ppropertyget.SITE = porigin_site /\ ppropertyget.LINE = z_read
ppropertyget.OBJECT = n_target /\ ppropertyget.NAME = $ptascii("ghost")
$property_get_reference_source(S_front,ppropertyget) /\ ~$property_get_owned_source(S_front,ppropertyget)
$property_get_factory(S_front,ppropertyget) = (pfunction_factory)
pfunction_factory.SIGNATURE.BYREF /\ ~$function_generator(S_front,pfunction_factory)
$property_get_method(S_front,n_target) = (pmethoddesc_get)
pmethoddesc_get.FUNCTION.SIGNATURE.BYREF /\ ~pmethoddesc_get.FUNCTION.CODE.STRICT
$property_get_verify_desc(S_front,ppropertyget) = (ppropertydesc_target)
ppropertyget.DECL = (ppropertydesc_target.ORIGIN)
ppropertydesc_target.TYPE = [PTBRANCH ([PTBUILTIN "int"])]
$objectprops_at(S_front.OBJECTPROPS,n_target) = (ppropertyslot_all*)
$property_slot_at(ppropertyslot_all*,ppropertyget.NAME) = (ppropertyslot)
ppropertyslot.DECL = ppropertyget.DECL /\ ppropertyslot.STATE = PROP_UNSET
$property_get_capture(S_front,ppropertyget)
$property_get_base_tasks(S_front,ppropertyget) = [PROPERTY_GET_INPUT ppropertyget n_receiver]
$property_get_base_count(S_front.TODO,n_target,porigin_site) = 0
$property_get_input_count(S_front.TODO,n_target,porigin_site) = 0
$task_nodes(PROPERTY_GET_INPUT ppropertyget n_receiver) = [HCELL n_receiver]
S_global = $global_table_view(S_front)
$lookup(S_global.ENV,$ptascii("receiver")) = (n_receiver)
$lookup(S_global.ENV,$ptascii("slot")) = (n_slot)
n_slot =/= n_receiver
S_front.STORE[n_slot] = DEFINED pvalue_seven
$string_bytes(pvalue_seven) = ($ptascii("7"))
S_front.PARAMETERBACKINGS = eps
n_target_owners = $heap_owners($heap_graph(S_front),HOBJECT n_target)
n_input_owners = $heap_owners($heap_graph(S_front),HCELL n_receiver)
$gr_output(S_front.EVENTS) = ptbytes_front
~$gr_active(S_front,n_target,ppropertyget.NAME) /\ $gr_guard(S_front)
PhpStep: S_front ~> S_begin_raw
S_begin = $gr_after(S_front,S_begin_raw)
S_begin.TODO = [(CALL_ARGS (PROPERTY_GET_TARGET n_target ppropertyget.METHOD) eps 1 ([KNOWN (PSTRING ppropertyget.NAME)]) (porigin_site) z_read), PROPERTY_GET_RESULT ppropertyget, PROPERTY_GET_INPUT ppropertyget n_receiver] ++ ptask_tail*
$heap_owners($heap_graph(S_begin),HOBJECT n_target) = $(n_target_owners + 1)
$heap_owners($heap_graph(S_begin),HCELL n_receiver) = n_input_owners
""")
ENTER = common.lines(r"""
S_get.CURRENT = (pcallcontext_get)
S_get.FRAMES = pframe_get :: eps
pframe_get.CONTEXT = eps
pframe_get.TODO = [PROPERTY_GET_RESULT ppropertyget, PROPERTY_GET_INPUT ppropertyget n_receiver] ++ ptask_tail*
$property_get_frame(S_get,pcallcontext_get,pframe_get)
$call_receiver_roots(pcallcontext_get) = eps
$property_get_history(S_get,ppropertyget)
$gr_active(S_get,n_target,ppropertyget.NAME) /\ $gr_guard(S_get)
""")
RESULT = common.lines(r"""
S_result.CURRENT = eps /\ S_result.FRAMES = eps
S_result.TODO = [PROPERTY_GET_RESULT ppropertyget, PROPERTY_GET_INPUT ppropertyget n_receiver] ++ ptask_tail*
S_result.RESULT = REFERENCE n_slot
S_result.STORE[n_slot] = DEFINED pvalue_seven
S_result.STORE[n_receiver] = DEFINED PNULL
$property_get_history(S_result,ppropertyget) /\ $property_get_tail_valid(S_result,ppropertyget)
$property_get_input_at(S_result.TODO,ppropertyget) = (n_receiver)
$property_get_input_valid(S_result,ppropertyget,n_receiver)
$property_get_valid(S_result,ppropertyget,true)
$call_reference_operand_valid(S_result,S_result.RESULT)
$heap_owners($heap_graph(S_result),HOBJECT n_target) = 1
$heap_owners($heap_graph(S_result),HCELL n_receiver) = n_input_owners
S_result.PARAMETERBACKINGS = eps
~$gr_active(S_result,n_target,ppropertyget.NAME) /\ $gr_guard(S_result)
""")
DTOR = common.lines(r"""
S_dtor.CURRENT = (pcallcontext_dtor)
$destructor_context_call(pcallcontext_dtor,S_dtor.CURRENT,S_dtor.FRAMES) = (pdestructorcall)
S_dtor.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
pdestructorcall.OPERATION = (pdestructionoperation)
pdestructionoperation.SOURCE = PROPERTY_GET_RESULT ppropertyget
pdestructionoperation.VALUE = KNOWN PNULL /\ pdestructionoperation.BASE = BASE_VALUE (KNOWN PNULL)
pdestructionoperation.ORIGIN = (porigin_site) /\ pdestructionoperation.CALLER = eps
S_dtor.STORE[n_receiver] = DEFINED PNULL
$property_get_history(S_dtor,ppropertyget)
~$gr_active(S_dtor,n_target,ppropertyget.NAME) /\ $gr_guard(S_dtor)
""")

def conditions(case, checked):
    conflict = case['id'] == 'conflict-retarget'
    reached = [
        'S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(HERE / case['source_file']).encode()).decode()) + ')',
        r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
        'ptbytes_file = $ptascii(' + json.dumps(str(HERE / case['source_file'])) + ')',
        'ptbytes_front = $ptascii(' + json.dumps('C:F|' if conflict else 'W:F|') + ')',
        'ptbytes_final = $ptascii(' + json.dumps(base64.b64decode(case['stdout_base64']).decode()) + ')',
        f'z_read = {case["read_line"]}']
    reached += common.reach('S_front','S_initial','GR_OUTER') + FRONT
    if conflict:
        reached += common.lines(r"""
$propref_at(S_front.PROPREFS,n_slot) = (ppropref)
ppropref.SOURCES = [OBJECT_PROP_SOURCE n_holder ($ptascii("value")) ppropertyid_holder]
$propref_descriptor(S_front,OBJECT_PROP_SOURCE n_holder ($ptascii("value")) ppropertyid_holder) = (ppropertydesc_holder)
ppropertydesc_holder.TYPE = [PTBRANCH ([PTBUILTIN "string"])]
$proprefs_valid(S_front)
$lookup(S_global.ENV,$ptascii("replacement")) = (n_replacement_cell)
S_front.STORE[n_replacement_cell] = DEFINED (POBJECT n_h)
""")
    else:
        reached += ['$propref_at(S_front.PROPREFS,n_slot) = eps']
    reached += scoped.reach('S_get','S_begin','SG_ENTER ppropertyget') + ENTER
    reached += scoped.reach('S_result','S_get','SG_RESULT ppropertyget') + RESULT
    if conflict:
        message = 'Reference with value of type string held by property CellConflictHolder131::$value of type string is not compatible with property CellConflictTarget131::$ghost of type int'
        reached += ['ptbytes_message = $ptascii(' + json.dumps(message) + ')'] + common.lines(r"""
$propref_at(S_result.PROPREFS,n_slot) = (ppropref)
$property_get_propref(S_result,ppropertyget,n_slot)
n_rv_cell_owners = $heap_owners($heap_graph(S_result),HCELL n_slot)
S_verified = $property_get_verify(S_result,ppropertyget,S_result.RESULT)
S_verified = S_result[.COMPLETION = THROWN "TypeError" ptbytes_message z_read]
PhpStep: S_result ~> S_verified_raw
S_verified_raw.TODO = [PROPERTY_GET_COPY ppropertyget (REFERENCE n_slot), PROPERTY_GET_INPUT ppropertyget n_receiver] ++ ptask_tail*
S_verified_raw.STORE = S_result.STORE /\ S_verified_raw.PROPREFS = S_result.PROPREFS
S_material = $throwable_transition(S_result,S_verified_raw)
S_material.COMPLETION = THROWING n_error
n_error = |S_result.OBJECTS|
$throwable_field(S_material,n_error,"message") = PSTRING ptbytes_message
$throwable_field(S_material,n_error,"file") = PSTRING ptbytes_file
$throwable_field(S_material,n_error,"line") = PINT z_read
$throwable_object_image_valid(S_material,n_error)
S_pending = $gr_after(S_result,S_verified_raw)
""")
        reached += common.reach('S_dtor','S_pending','GR_DTOR n_target') + DTOR + common.lines(r"""
pdestructionoperation.PENDING = (n_error) /\ pdestructorcall.PENDING = (n_error)
S_dtor.STORE[n_slot] = DEFINED pvalue_seven
$propref_at(S_dtor.PROPREFS,n_slot) = (ppropref)
$gr_output(S_dtor.EVENTS) = $ptascii("C:F|G|")
""")
        reached += common.reach('S_changed','S_dtor','GR_OUTPUT ($ptascii("C:F|G|D|kept7|d|"))') + common.lines(r"""
S_changed.STORE[n_slot] = DEFINED pvalue_eight
$string_bytes(pvalue_eight) = ($ptascii("8"))
ptask_input* = [THROW_SEARCH n_h, PROPERTY_GET_INPUT ppropertyget n_receiver, PROPERTY_GET_DROP ppropertyget pvalue_eight] ++ ptask_tail*
""")
        reached += scoped.reach('S_input','S_changed','SG_TAIL ptask_input*') + common.lines(r"""
S_input.CURRENT = eps /\ S_input.FRAMES = eps
S_input.RESULT = KNOWN PNULL /\ S_input.BASE = BASE_VALUE (KNOWN PNULL)
S_input.STORE[n_receiver] = DEFINED PNULL
S_input.STORE[n_slot] = DEFINED pvalue_eight
$heap_owners($heap_graph(S_input),HCELL n_slot) = $(n_rv_cell_owners - 1)
$heap_owners($heap_graph(S_input),HCELL n_receiver) = n_input_owners
~((HOBJECT n_target) <- S_input.ALLOCATIONS)
$call_task_valid(S_input,PROPERTY_GET_INPUT ppropertyget n_receiver)
$call_task_valid(S_input,PROPERTY_GET_DROP ppropertyget pvalue_eight)
$throwable_previous_id(S_input,n_h) = (n_error)
PhpStep: S_input ~> S_input_raw
ptask_drop* = [THROW_SEARCH n_h, PROPERTY_GET_DROP ppropertyget pvalue_eight] ++ ptask_tail*
S_input_raw.TODO = ptask_drop*
S_input_pending = $gr_after(S_input,S_input_raw)
""")
        reached += scoped.reach('S_drop','S_input_pending','SG_TAIL ptask_drop*') + common.lines(r"""
$heap_owners($heap_graph(S_drop),HCELL n_receiver) = $(n_input_owners - 1)
$propref_at(S_drop.PROPREFS,n_slot) = (ppropref)
$gr_guard(S_drop)
""")
        reached += scoped.reach('S_catch','S_drop','SG_CATCH') + common.lines(r"""
S_catch.TODO = (CATCH_BIND porigin_catch n_index n_h) :: ptask_catch_tail*
$throwable_previous_id(S_catch,n_h) = (n_error)
$throwable_previous_id(S_catch,n_error) = eps
$lookup(S_catch.ENV,$ptascii("result")) = (n_result_cell)
S_catch.STORE[n_result_cell] = DEFINED (PINT 42)
S_catch.STORE[n_slot] = DEFINED pvalue_eight
S_catch.STORE[n_receiver] = DEFINED PNULL
$propref_at(S_catch.PROPREFS,n_slot) = (ppropref)
$gr_output(S_catch.EVENTS) = $ptascii("C:F|G|D|kept7|d|")
$gr_guard(S_catch)
S_end = S_catch
""")
    else:
        reached += common.lines(r"""
$propref_at(S_result.PROPREFS,n_slot) = eps
$property_get_unconstrained(S_result,S_result.RESULT)
S_result.REFCOERCIONS = eps /\ S_result.CONTAINERINITS = eps
S_verified = $property_get_verify(S_result,ppropertyget,S_result.RESULT)
S_verified = S_result[.STORE[n_slot] = DEFINED (PINT 7)]
PhpStep: S_result ~> S_verified_raw
S_verified_raw.TODO = [PROPERTY_GET_COPY ppropertyget (REFERENCE n_slot), PROPERTY_GET_INPUT ppropertyget n_receiver] ++ ptask_tail*
S_verified_raw.STORE[n_slot] = DEFINED (PINT 7)
S_pending = $gr_after(S_result,S_verified_raw)
""")
        reached += common.reach('S_dtor','S_pending','GR_DTOR n_target') + DTOR + common.lines(r"""
pdestructionoperation.PENDING = eps /\ pdestructorcall.PENDING = eps
S_dtor.STORE[n_slot] = DEFINED (PINT 7)
$gr_output(S_dtor.EVENTS) = $ptascii("W:F|G|")
""")
        reached += common.reach('S_copy','S_dtor','GR_GET_COPY') + common.lines(r"""
S_copy.TODO = [PROPERTY_GET_COPY ppropertyget (REFERENCE n_slot), PROPERTY_GET_INPUT ppropertyget n_receiver] ++ ptask_tail*
S_copy.STORE[n_slot] = DEFINED pvalue_nine
$string_bytes(pvalue_nine) = ($ptascii("9"))
S_copy.STORE[n_receiver] = DEFINED PNULL
~((HOBJECT n_target) <- S_copy.ALLOCATIONS)
$property_get_valid(S_copy,ppropertyget,false) /\ $property_get_tail_valid(S_copy,ppropertyget)
$call_task_valid(S_copy,PROPERTY_GET_COPY ppropertyget (REFERENCE n_slot))
$gr_output(S_copy.EVENTS) = $ptascii("W:F|G|D|verified7|d|")
n_rv_cell_owners = $heap_owners($heap_graph(S_copy),HCELL n_slot)
PhpStep: S_copy ~> S_copied_raw
S_copied_raw.TODO = (PROPERTY_GET_INPUT ppropertyget n_receiver) :: ptask_tail*
S_copied_raw.RESULT = KNOWN pvalue_nine
S_copy_pending = $gr_after(S_copy,S_copied_raw)
ptask_input* = (PROPERTY_GET_INPUT ppropertyget n_receiver) :: ptask_tail*
""")
        reached += scoped.reach('S_input','S_copy_pending','SG_TAIL ptask_input*') + common.lines(r"""
S_input.RESULT = KNOWN pvalue_nine
$heap_owners($heap_graph(S_input),HCELL n_slot) = $(n_rv_cell_owners - 1)
$heap_owners($heap_graph(S_input),HCELL n_receiver) = n_input_owners
$call_task_valid(S_input,PROPERTY_GET_INPUT ppropertyget n_receiver)
PhpStep: S_input ~> S_input_raw
S_input_raw.TODO = ptask_tail* /\ S_input_raw.RESULT = KNOWN pvalue_nine
S_input_pending = $gr_after(S_input,S_input_raw)
""")
        reached += scoped.reach('S_read','S_input_pending','SG_TAIL ptask_tail*') + common.lines(r"""
S_read.RESULT = KNOWN pvalue_nine
$heap_owners($heap_graph(S_read),HCELL n_receiver) = $(n_input_owners - 1)
S_read.STORE[n_receiver] = DEFINED PNULL
$propref_at(S_read.PROPREFS,n_slot) = eps
$gr_guard(S_read)
S_end = S_read
""")
    finish = [line.replace('n_child','n_target') for line in common.FINISH]
    reached += finish[:-3]
    return reached, finish[-3:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_get_receiver_cell_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    assert [case['id'] for case in data['cases']] == ['weak-retarget', 'sole-cell-exact', 'conflict-retarget', 'payload-retirement']
    assert [case['id'] for case in data['controls']] == []
    assert all(sha(HERE / case['source_file']) == case['source_sha256'] for case in data['cases'] + data['controls'])
    selected = [next(case for case in data['cases'] if case['id'] == identifier) for identifier in ('weak-retarget', 'conflict-retarget')]
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
    out = Path(tempfile.mkdtemp(prefix='magic-get-receiver-cell-protocol-', dir=ROOT / '.tools'))
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
            fixture = directory / 'receiver-cell.watsup'
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
