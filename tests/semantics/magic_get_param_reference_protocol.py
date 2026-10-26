"""Check real parameter-receipt production through Get conflict and conversion."""
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
PREFIX = scoped.PREFIX + r"""
syntax ppcstage = PC_RECEIVE | PC_THROW_COPY ppropertyget nat | PC_THROW_DROP ppropertyget nat pvalue | PC_CATCH porigin
dec $pc_stage(pstate,ppcstage) : bool
def $pc_stage(S,PC_RECEIVE) = true
  -- if S.TODO = [PARAMETER_STRING_RESULT pparameterstring]
  -- if S.RESULT = KNOWN pvalue_string
  -- if $string_bytes(pvalue_string) = ($ptascii("7"))
def $pc_stage(S,PC_THROW_COPY ppropertyget n_error) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_tail*
def $pc_stage(S,PC_THROW_DROP ppropertyget n_error pvalue) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_DROP ppropertyget pvalue) :: ptask_tail*
def $pc_stage(S,PC_CATCH porigin_driver) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.FUNCTION = porigin_driver
def $pc_stage(S,ppcstage) = false -- otherwise
dec $pc_seek(pstate,ppcstage,nat) : pstate
def $pc_seek(S,ppcstage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $pc_stage(S,ppcstage) \/ n = 0
def $pc_seek(S,ppcstage,n) = $pc_seek($drive_steps(S[.COMPLETION = NORMAL],1),ppcstage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$pc_stage(S,ppcstage) /\ $(n > 0)
def $pc_seek(S,ppcstage,n) = $pc_seek($drive_steps(S,1),ppcstage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $pc_seek(S,ppcstage,n) = S -- otherwise
"""

def reach(name, previous, stage):
    return [f'{name}_found = $pc_seek({previous},{stage},2000)',
        fr'{name}_found.COMPLETION = NORMAL \/ {name}_found.COMPLETION = BUDGET',
        f'{name} = {name}_found[.COMPLETION = NORMAL]', f'$pc_stage({name},{stage})']

RECEIVE = common.lines(r"""
S_receive.TODO = [PARAMETER_STRING_RESULT pparameterstring]
S_receive.CURRENT = (pcallcontext_receive)
porigin_driver = pparameterstring.FUNCTION
pcallcontext_receive.FUNCTION = porigin_driver
pparameterstring.INDEX = 0 /\ pparameterstring.LINE = z_parameter
n_slot = pparameterstring.CELL
n_stringable = pparameterstring.OBJECT
S_receive.RESULT = KNOWN pvalue_string
$string_bytes(pvalue_string) = ($ptascii("7"))
S_receive.STORE[n_slot] = DEFINED (POBJECT n_stringable)
S_receive.PARAMETERBACKINGS = eps
$parameter_string_scope_valid(S_receive,pparameterstring)
$propref_at(S_receive.PROPREFS,n_slot) = (ppropref)
ppropref.SOURCES = [OBJECT_PROP_SOURCE n_holder ($ptascii("value")) ppropertyid_holder]
$propref_descriptor(S_receive,OBJECT_PROP_SOURCE n_holder ($ptascii("value")) ppropertyid_holder) = (ppropertydesc_holder)
ppropertydesc_holder.TYPE = [PTBRANCH ([PTBUILTIN "object"])]
$typed_exact(ppropertydesc_holder.TYPE,POBJECT n_stringable)
$proprefs_valid(S_receive)
$parameter_backing_admission(S_receive,pparameterstring,$ptascii("7"))
$function_at($all_functions(S_receive),porigin_driver) = (pfunction_driver)
psparam = pfunction_driver.SIGNATURE.PARAMETERS[0]
psparam.BYREF /\ psparam.TYPE = [PTBRANCH ([PTBUILTIN "string"])]
n_receive_cell_owners = $heap_owners($heap_graph(S_receive),HCELL n_slot)
$gr_output(S_receive.EVENTS) = ptbytes_receive
PhpStep: S_receive ~> S_backed_raw
S_backed_raw.STORE[n_slot] = DEFINED pvalue_string
S_backed_raw.PARAMETERBACKINGS = [pparameterbacking]
pparameterbacking = {FUNCTION porigin_driver, INDEX 0, CELL n_slot, LINE z_parameter, VALUE $ptascii("7")}
$parameter_backing_row_valid(S_backed_raw,pparameterbacking)
$parameter_backings_valid(S_backed_raw) /\ $proprefs_valid(S_backed_raw)
~$typed_exact(ppropertydesc_holder.TYPE,pvalue_string)
~$typed_object_exact(S_backed_raw,ppropertydesc_holder.TYPE,pvalue_string)
$parameter_backing_value(S_backed_raw,n_slot,pvalue_string)
$heap_owners($heap_graph(S_backed_raw),HCELL n_slot) = $(n_receive_cell_owners - 1)
S_backed = $gr_after(S_receive,S_backed_raw)
""")
FRONT = common.lines(r"""
S_front.CURRENT = (pcallcontext_reader)
pcallcontext_reader.FUNCTION = porigin_driver /\ pcallcontext_reader.RECEIVER = eps
S_front.FRAMES = pframe_caller_tail*
S_front.RESULT = VARIABLE ($ptascii("target")) z_read
S_front.ORIGIN = (porigin_site)
S_front.TODO = (PROPERTY_PREP phpType20_name z_read) :: (DIM_FETCH z_read) :: ptask_tail*
$property_get_plan(S_front) = (ppropertyget)
n_child = ppropertyget.OBJECT
ppropertyget.SITE = porigin_site /\ ppropertyget.LINE = z_read
$property_get_source(S_front,ppropertyget) /\ ~$property_get_owned_source(S_front,ppropertyget)
$property_get_base_tasks(S_front,ppropertyget) = eps
$property_get_verify_desc(S_front,ppropertyget) = (ppropertydesc_target)
ppropertyget.DECL = (ppropertydesc_target.ORIGIN)
ppropertydesc_target.TYPE = [PTBRANCH ([PTBUILTIN "int"])]
$property_get_method(S_front,n_child) = (pmethoddesc_get)
pmethoddesc_get.FUNCTION.SIGNATURE.BYREF /\ ~pmethoddesc_get.FUNCTION.CODE.STRICT
S_global = $global_table_view(S_front)
$lookup(S_global.ENV,$ptascii("slot")) = (n_slot)
$lookup(S_front.ENV,$ptascii("cell")) = (n_slot)
S_front.STORE[n_slot] = DEFINED pvalue_string
S_front.PARAMETERBACKINGS = [pparameterbacking]
$parameter_backings_valid(S_front)
$property_get_capture(S_front,ppropertyget) /\ $property_get_history(S_front,ppropertyget)
$gr_output(S_front.EVENTS) = ptbytes_front
n_target_owners = $heap_owners($heap_graph(S_front),HOBJECT n_child)
~$gr_active(S_front,n_child,ppropertyget.NAME) /\ $gr_guard(S_front)
PhpStep: S_front ~> S_begin_raw
S_begin = $gr_after(S_front,S_begin_raw)
S_begin.TODO = (CALL_ARGS (PROPERTY_GET_TARGET n_child ppropertyget.METHOD) eps 1 ([KNOWN (PSTRING ppropertyget.NAME)]) (porigin_site) z_read) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
$heap_owners($heap_graph(S_begin),HOBJECT n_child) = $(n_target_owners + 1)
""")
ENTER = common.lines(r"""
S_get.CURRENT = (pcallcontext_get)
pcallcontext_get.FUNCTION =/= pparameterbacking.FUNCTION
S_get.FRAMES = pframe_get :: pframe_caller_tail*
pframe_get.CONTEXT = (pcallcontext_reader)
$property_get_frame(S_get,pcallcontext_get,pframe_get)
$call_receiver_roots(pcallcontext_get) = eps
$parameter_backing_at(S_get.PARAMETERBACKINGS,n_slot) = (pparameterbacking)
$parameter_backing_row_valid(S_get,pparameterbacking)
$gr_active(S_get,n_child,ppropertyget.NAME) /\ $gr_guard(S_get)
""")
RESULT = common.lines(r"""
S_result.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
S_result.CURRENT = (pcallcontext_reader)
S_result.RESULT = REFERENCE n_slot
S_result.STORE[n_slot] = DEFINED pvalue_string
S_result.PARAMETERBACKINGS = [pparameterbacking]
$call_reference_operand_valid(S_result,S_result.RESULT)
$parameter_backings_valid(S_result)
$property_get_verify_desc(S_result,ppropertyget) = (ppropertydesc_target)
$property_get_valid(S_result,ppropertyget,true) /\ $property_get_tail_valid(S_result,ppropertyget)
~$gr_active(S_result,n_child,ppropertyget.NAME) /\ $gr_guard(S_result)
""")

def conditions(case,checked):
    conflict = case['id'] == 'source-conflict'
    reached = [
        'S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(HERE / case['source_file']).encode()).decode()) + ')',
        r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
        'ptbytes_file = $ptascii(' + json.dumps(str(HERE / case['source_file'])) + ')',
        'ptbytes_receive = $ptascii(' + json.dumps('C:S|' if conflict else 'D:S|') + ')',
        'ptbytes_front = $ptascii(' + json.dumps('C:S|R|' if conflict else 'D:S|R|u|') + ')',
        'ptbytes_final = $ptascii(' + json.dumps(base64.b64decode(case['stdout_base64']).decode()) + ')',
        f'z_parameter = {case["parameter_line"]}', f'z_read = {case["read_line"]}']
    reached += reach('S_receive','S_initial','PC_RECEIVE') + RECEIVE
    reached += scoped.reach('S_front','S_backed','SG_FRONT z_read') + FRONT
    if conflict:
        reached += common.lines(r"""
$propref_at(S_front.PROPREFS,n_slot) = (ppropref)
""")
    else:
        reached += common.lines(r"""
$propref_at(S_front.PROPREFS,n_slot) = eps
$objectprops_at(S_front.OBJECTPROPS,n_holder) = (ppropertyslot_holder_all*)
$property_slot_at(ppropertyslot_holder_all*,$ptascii("value")) = (ppropertyslot_holder)
ppropertyslot_holder.DECL = (ppropertydesc_holder.ORIGIN) /\ ppropertyslot_holder.STATE = PROP_UNSET
""")
    reached += scoped.reach('S_get','S_begin','SG_ENTER ppropertyget') + ENTER
    reached += scoped.reach('S_result','S_get','SG_RESULT ppropertyget') + RESULT
    if conflict:
        message = 'Reference with value of type string held by property ParamConflictHolder130::$value of type object is not compatible with property ParamConflictTarget130::$ghost of type int'
        reached += ['ptbytes_message = $ptascii(' + json.dumps(message) + ')'] + common.lines(r"""
$propref_at(S_result.PROPREFS,n_slot) = (ppropref)
$property_get_propref(S_result,ppropertyget,n_slot)
S_verified = $property_get_verify(S_result,ppropertyget,S_result.RESULT)
S_verified = S_result[.COMPLETION = THROWN "TypeError" ptbytes_message z_read]
PhpStep: S_result ~> S_verified_raw
S_verified_raw.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_slot)) :: ptask_tail*
S_verified_raw.RESULT = KNOWN PNULL
S_material = $throwable_transition(S_result,S_verified_raw)
S_material.COMPLETION = THROWING n_error
n_error = |S_result.OBJECTS|
$throwable_field(S_material,n_error,"message") = PSTRING ptbytes_message
$throwable_field(S_material,n_error,"file") = PSTRING ptbytes_file
$throwable_field(S_material,n_error,"line") = PINT z_read
$throwable_object_image_valid(S_material,n_error)
S_pending = $gr_after(S_result,S_verified_raw)
""")
        reached += common.lines(r"""
S_pending.COMPLETION = THROWING n_error
S_throw_copy = $throwable_begin(S_pending)
S_throw_copy.COMPLETION = NORMAL
$pc_stage(S_throw_copy,PC_THROW_COPY ppropertyget n_error)
S_throw_copy.CURRENT = (pcallcontext_reader)
S_throw_copy.PARAMETERBACKINGS = [pparameterbacking]
n_copy_cell_owners = $heap_owners($heap_graph(S_throw_copy),HCELL n_slot)
PhpStep: S_throw_copy ~> S_captured_raw
S_captured_raw.TODO = [THROW_SEARCH n_error, PROPERTY_GET_DROP ppropertyget pvalue_string] ++ ptask_tail*
S_captured_raw.RESULT = KNOWN PNULL /\ S_captured_raw.BASE = BASE_VALUE (KNOWN PNULL)
S_captured_pending = $gr_after(S_throw_copy,S_captured_raw)
""")
        reached += reach('S_drop','S_captured_pending','PC_THROW_DROP ppropertyget n_error pvalue_string') + common.lines(r"""
$heap_owners($heap_graph(S_drop),HCELL n_slot) = $(n_copy_cell_owners - 1)
S_drop.STORE[n_slot] = DEFINED pvalue_string
S_drop.PARAMETERBACKINGS = [pparameterbacking]
$propref_at(S_drop.PROPREFS,n_slot) = (ppropref)
$parameter_backing_value(S_drop,n_slot,pvalue_string) /\ $gr_guard(S_drop)
""")
        reached += reach('S_catch','S_drop','PC_CATCH porigin_driver') + common.lines(r"""
S_catch.TODO = (CATCH_BIND porigin_catch n_index n_error) :: ptask_catch_tail*
S_catch.CURRENT = (pcallcontext_catch)
pcallcontext_catch.FUNCTION = porigin_driver
S_catch.STORE[n_slot] = DEFINED pvalue_string
S_catch.PARAMETERBACKINGS = [pparameterbacking]
$propref_at(S_catch.PROPREFS,n_slot) = (ppropref)
$parameter_backings_valid(S_catch) /\ $proprefs_valid(S_catch)
$lookup(S_catch.ENV,$ptascii("got")) = (n_got_cell)
S_catch.STORE[n_got_cell] = DEFINED (PINT 42)
$throwable_previous_id(S_catch,n_error) = eps
$gr_output(S_catch.EVENTS) = $ptascii("C:S|R|G|")
$gr_guard(S_catch)
S_end = S_catch
""")
    else:
        reached += common.lines(r"""
$propref_at(S_result.PROPREFS,n_slot) = eps
$property_get_unconstrained(S_result,S_result.RESULT)
S_result.REFCOERCIONS = eps /\ S_result.CONTAINERINITS = eps
S_verified = $property_get_verify(S_result,ppropertyget,S_result.RESULT)
S_verified = $parameter_backing_clear(S_result,n_slot)[.STORE[n_slot] = DEFINED (PINT 7)]
S_verified.PARAMETERBACKINGS = eps
PhpStep: S_result ~> S_copy_raw
S_copy_raw.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_slot)) :: ptask_tail*
S_copy_raw.STORE[n_slot] = DEFINED (PINT 7)
S_copy_raw.PARAMETERBACKINGS = eps
S_copy_pending = $gr_after(S_result,S_copy_raw)
ptask_copy* = S_copy_raw.TODO
""")
        reached += scoped.reach('S_copy','S_copy_pending','SG_TAIL ptask_copy*') + common.lines(r"""
S_copy.CURRENT = (pcallcontext_reader)
$heap_owners($heap_graph(S_copy),HOBJECT n_child) = n_target_owners
n_copy_cell_owners = $heap_owners($heap_graph(S_copy),HCELL n_slot)
$call_task_valid(S_copy,PROPERTY_GET_COPY ppropertyget (REFERENCE n_slot))
PhpStep: S_copy ~> S_copied_raw
S_copied_raw.TODO = ptask_tail* /\ S_copied_raw.RESULT = KNOWN (PINT 7)
S_read_pending = $gr_after(S_copy,S_copied_raw)
""")
        reached += scoped.reach('S_read_value','S_read_pending','SG_TAIL ptask_tail*') + common.lines(r"""
S_read_value.RESULT = KNOWN (PINT 7)
S_read_value.CURRENT = (pcallcontext_reader)
$heap_owners($heap_graph(S_read_value),HCELL n_slot) = $(n_copy_cell_owners - 1)
S_read_value.PARAMETERBACKINGS = eps
$propref_at(S_read_value.PROPREFS,n_slot) = eps
""")
        reached += common.reach('S_marker','S_read_value','GR_OUTPUT ($ptascii("D:S|R|u|G|int7|cell7|write|"))') + common.lines(r"""
S_marker.CURRENT = (pcallcontext_marker)
pcallcontext_marker.FUNCTION = porigin_driver
$lookup(S_marker.ENV,$ptascii("got")) = (n_got_cell)
S_marker.STORE[n_got_cell] = DEFINED (PINT 7)
S_marker.STORE[n_slot] = DEFINED pvalue_free
$string_bytes(pvalue_free) = ($ptascii("free"))
S_marker.PARAMETERBACKINGS = eps
$propref_at(S_marker.PROPREFS,n_slot) = eps
$gr_guard(S_marker)
S_end = S_marker
""")
    reached += common.FINISH[:-3]
    return reached, common.FINISH[-3:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_get_param_reference_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    assert [case['id'] for case in data['cases']] == ['exact-receipt', 'source-conflict', 'detached-conversion']
    assert [case['id'] for case in data['controls']] == []
    assert all(sha(HERE / case['source_file']) == case['source_sha256'] for case in data['cases'] + data['controls'])
    selected = [next(case for case in data['cases'] if case['id'] == identifier) for identifier in ('detached-conversion', 'source-conflict')]
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
    out = Path(tempfile.mkdtemp(prefix='magic-get-param-reference-protocol-', dir=ROOT / '.tools'))
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
            fixture = directory / 'param-reference.watsup'
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
