"""Check live owned Get references through local and receiver cleanup."""
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
syntax povstage = OV_EXIT ppropertyget | OV_THROW_COPY ppropertyget nat | OV_THROW_BASE ppropertyget nat pvalue
dec $ov_stage(pstate,povstage) : bool
def $ov_stage(S,OV_EXIT ppropertyget) = true
  -- if $property_get_recursive_exit(S,S.TODO,ppropertyget) = (pdestructionframe)
def $ov_stage(S,OV_THROW_COPY ppropertyget n_error) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: (PROPERTY_GET_BASE ppropertyget) :: ptask_tail*
def $ov_stage(S,OV_THROW_BASE ppropertyget n_error pvalue) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_BASE ppropertyget) :: (PROPERTY_GET_DROP ppropertyget pvalue) :: ptask_tail*
def $ov_stage(S,povstage) = false -- otherwise
dec $ov_seek(pstate,povstage,nat) : pstate
def $ov_seek(S,povstage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $ov_stage(S,povstage) \/ n = 0
def $ov_seek(S,povstage,n) = $ov_seek($drive_steps(S[.COMPLETION = NORMAL],1),povstage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$ov_stage(S,povstage) /\ $(n > 0)
def $ov_seek(S,povstage,n) = $ov_seek($drive_steps(S,1),povstage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $ov_seek(S,povstage,n) = S -- otherwise
"""

def reach(name,previous,stage):
    return [f'{name}_found = $ov_seek({previous},{stage},2000)',
        fr'{name}_found.COMPLETION = NORMAL \/ {name}_found.COMPLETION = BUDGET',
        f'{name} = {name}_found[.COMPLETION = NORMAL]',f'$ov_stage({name},{stage})']

FRONT = common.lines(r"""
$property_get_plan(S_front) = (ppropertyget)
n_owner = ppropertyget.OBJECT
ppropertyget.SITE = porigin_site /\ ppropertyget.LINE = z_read
ptbytes_name = ppropertyget.NAME
ptbytes_name = $ptascii("ghost")
S_front.CURRENT = (pcallcontext_read)
pcallcontext_read.RECEIVER = eps /\ $this_receiver(S_front) = eps
S_front.FRAMES = pframe_caller_tail*
$property_get_owned_source(S_front,ppropertyget)
~$property_get_this_source(S_front,ppropertyget)
$property_get_method(S_front,n_owner) = (pmethoddesc_get)
pmethoddesc_get.FUNCTION.SIGNATURE.BYREF /\ ~pmethoddesc_get.FUNCTION.CODE.STRICT
$property_get_lookup(S_front,ppropertyget) = PROPERTY_ACCESS ptbytes_key
ptbytes_key =/= ptbytes_name
$property_get_verify_desc(S_front,ppropertyget) = (ppropertydesc_parent)
ppropertyget.DECL = (ppropertydesc_parent.ORIGIN)
ppropertydesc_parent.KEY = ptbytes_key
ppropertydesc_parent.TYPE = [PTBRANCH ([PTBUILTIN "int"])]
$objectprops_at(S_front.OBJECTPROPS,n_owner) = (ppropertyslot_front_all*)
$property_slot_at(ppropertyslot_front_all*,ptbytes_key) = (ppropertyslot_front)
ppropertyslot_front.DECL = ppropertyget.DECL /\ ppropertyslot_front.STATE = PROP_UNSET
$property_get_owned_access(S_front,n_owner,ptbytes_name)
$property_get_history(S_front,ppropertyget) /\ $property_get_capture(S_front,ppropertyget)
$property_get_base_tasks(S_front,ppropertyget) = [PROPERTY_GET_BASE ppropertyget]
$heap_owners($heap_graph(S_front),HOBJECT n_owner) = 1
$gr_output(S_front.EVENTS) = ptbytes_prefix
~$gr_active(S_front,n_owner,ptbytes_name) /\ $gr_guard(S_front)
S_front.TODO = (PROPERTY_PREP phpType20_name z_read) :: (DIM_FETCH z_read) :: ptask_tail*
PhpStep: S_front ~> S_begin_raw
S_begin = $gr_after(S_front,S_begin_raw)
S_begin.TODO = [CALL_ARGS (PROPERTY_GET_TARGET n_owner ppropertyget.METHOD) eps 1 ([KNOWN (PSTRING ptbytes_name)]) (porigin_site) z_read, PROPERTY_GET_RESULT ppropertyget, PROPERTY_GET_BASE ppropertyget] ++ ptask_tail*
$heap_owners($heap_graph(S_begin),HOBJECT n_owner) = 2
""")
ENTER = common.lines(r"""
S_get.CURRENT = (pcallcontext_get)
S_get.FRAMES = pframe_get :: pframe_caller_tail*
pframe_get.CONTEXT = (pcallcontext_read)
pframe_get.TODO = [PROPERTY_GET_RESULT ppropertyget, PROPERTY_GET_BASE ppropertyget] ++ ptask_tail*
$property_get_frame(S_get,pcallcontext_get,pframe_get)
$call_receiver_roots(pcallcontext_get) = eps
S_global_get = $global_table_view(S_get)
$lookup(S_global_get.ENV,$ptascii("slot")) = (n_slot)
$property_get_history(S_get,ppropertyget)
$gr_active(S_get,n_owner,ptbytes_name) /\ $gr_guard(S_get)
""")
RESULT = common.lines(r"""
S_result.TODO = [PROPERTY_GET_RESULT ppropertyget, PROPERTY_GET_BASE ppropertyget] ++ ptask_tail*
S_result.CURRENT = (pcallcontext_read) /\ S_result.FRAMES = pframe_caller_tail*
S_result.RESULT = REFERENCE n_slot
S_result.STORE[n_slot] = DEFINED pvalue_raw
$typed_string_value(pvalue_raw)
$property_get_verify_desc(S_result,ppropertyget) = (ppropertydesc_parent)
$property_get_valid(S_result,ppropertyget,true) /\ $property_get_tail_valid(S_result,ppropertyget)
$parameter_backing_at(S_result.PARAMETERBACKINGS,n_slot) = eps
$heap_owners($heap_graph(S_result),HOBJECT n_owner) = 2
~$gr_active(S_result,n_owner,ptbytes_name) /\ $gr_guard(S_result)
""")


def conditions(case,checked):
    conflict = case['id'] == 'conflict-replace'
    reached = [
        'S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(HERE / case['source_file']).encode()).decode()) + ')',
        r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
        'ptbytes_file = $ptascii(' + json.dumps(str(HERE / case['source_file'])) + ')',
        'ptbytes_prefix = $ptascii(' + json.dumps('C:' if conflict else 'W:') + ')',
        'ptbytes_final = $ptascii(' + json.dumps(base64.b64decode(case['stdout_base64']).decode()) + ')',
        f'z_read = {case["read_line"]}']
    reached += scoped.reach('S_front','S_initial','SG_FRONT z_read')
    reached += ['S_front.ORIGIN = (porigin_site)'] + FRONT
    reached += scoped.reach('S_get','S_begin','SG_ENTER ppropertyget') + ENTER
    if not conflict:
        reached += ['n_probe = |S_get.OBJECTS|']
        reached += reach('S_exit','S_get','OV_EXIT ppropertyget') + common.lines(r"""
$property_get_recursive_exit(S_exit,S_exit.TODO,ppropertyget) = (pdestructionframe)
pdestructionframe.FUNCTION = ppropertyget.METHOD
pdestructionframe.VALUE = REFERENCE n_slot /\ pdestructionframe.PENDING = eps
pdestructionframe <- S_exit.DESTRUCTION.FRAMES
S_exit.STORE[n_slot] = DEFINED pvalue_before
$string_bytes(pvalue_before) = ($ptascii("7"))
$gr_output(S_exit.EVENTS) = $ptascii("W:G|")
$gr_active(S_exit,n_owner,ptbytes_name) /\ $gr_guard(S_exit)
""")
        reached += common.reach('S_probe','S_exit','GR_DTOR n_probe') + common.lines(r"""
S_probe.CURRENT = (pcallcontext_probe)
$destructor_context_call(pcallcontext_probe,S_probe.CURRENT,S_probe.FRAMES) = (pdestructorcall_probe)
pdestructorcall_probe.OBJECT = n_probe
pdestructorcall_probe.FRAME = (pdestructionframe) /\ pdestructorcall_probe.OPERATION = eps
pdestructionframe.VALUE = REFERENCE n_slot
$gr_active(S_probe,n_owner,ptbytes_name) /\ $gr_guard(S_probe)
""")
        reached += common.reach('S_changed','S_probe','GR_OUTPUT ($ptascii("W:G|L|"))') + common.lines(r"""
S_changed.STORE[n_slot] = DEFINED pvalue_changed
$typed_string_value(pvalue_changed)
$string_bytes(pvalue_changed) = ($ptascii("9"))
pdestructionframe <- S_changed.DESTRUCTION.FRAMES
pdestructionframe.VALUE = REFERENCE n_slot
S_live = $quiet_operand(S_changed,pdestructionframe.VALUE)
S_live.RESULT = KNOWN pvalue_changed
$gr_active(S_changed,n_owner,ptbytes_name) /\ $gr_guard(S_changed)
""")
    reached += scoped.reach('S_result','S_get' if conflict else 'S_changed','SG_RESULT ppropertyget') + RESULT
    if conflict:
        message = 'Reference with value of type string held by property OwnedConflictHolder128::$value of type string is not compatible with property OwnedConflictParent128::$ghost of type int'
        reached += ['ptbytes_message = $ptascii(' + json.dumps(message) + ')'] + common.lines(r"""
$string_bytes(pvalue_raw) = ($ptascii("7"))
S_global = $global_table_view(S_result)
$lookup(S_global.ENV,$ptascii("holder")) = (n_holder_cell)
S_result.STORE[n_holder_cell] = DEFINED (POBJECT n_holder)
$lookup(S_global.ENV,$ptascii("replacement")) = (n_h_cell)
S_result.STORE[n_h_cell] = DEFINED (POBJECT n_h)
$propref_at(S_result.PROPREFS,n_slot) = (ppropref)
ppropref.SOURCES = [OBJECT_PROP_SOURCE n_holder ($ptascii("value")) ppropertyid_holder]
$propref_descriptor(S_result,OBJECT_PROP_SOURCE n_holder ($ptascii("value")) ppropertyid_holder) = (ppropertydesc_holder)
ppropertydesc_holder.TYPE = [PTBRANCH ([PTBUILTIN "string"])]
$property_get_propref(S_result,ppropertyget,n_slot)
S_verified = $property_get_verify(S_result,ppropertyget,S_result.RESULT)
S_verified = S_result[.COMPLETION = THROWN "TypeError" ptbytes_message z_read]
$gr_output(S_result.EVENTS) = $ptascii("C:G|")
PhpStep: S_result ~> S_verified_raw
S_verified_raw.TODO = [PROPERTY_GET_COPY ppropertyget (REFERENCE n_slot), PROPERTY_GET_BASE ppropertyget] ++ ptask_tail*
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
        reached += reach('S_throw_copy','S_pending','OV_THROW_COPY ppropertyget n_error') + common.lines(r"""
S_throw_copy.STORE[n_slot] = DEFINED pvalue_raw
$heap_owners($heap_graph(S_throw_copy),HCELL n_slot) = 3
$heap_owners($heap_graph(S_throw_copy),HOBJECT n_owner) = 1
PhpStep: S_throw_copy ~> S_captured_raw
S_captured_raw.TODO = [THROW_SEARCH n_error, PROPERTY_GET_BASE ppropertyget, PROPERTY_GET_DROP ppropertyget pvalue_raw] ++ ptask_tail*
S_captured_raw.RESULT = KNOWN PNULL /\ S_captured_raw.BASE = BASE_VALUE (KNOWN PNULL)
S_captured_pending = $gr_after(S_throw_copy,S_captured_raw)
""")
        reached += reach('S_throw_base','S_captured_pending','OV_THROW_BASE ppropertyget n_error pvalue_raw') + common.lines(r"""
S_throw_base.STORE[n_slot] = DEFINED pvalue_raw
$heap_owners($heap_graph(S_throw_base),HCELL n_slot) = 2
$gr_output(S_throw_base.EVENTS) = $ptascii("C:G|")
$gr_guard(S_throw_base)
""")
        reached += common.reach('S_dtor','S_throw_base','GR_DTOR n_owner') + common.lines(r"""
S_dtor.CURRENT = (pcallcontext_dtor)
$destructor_context_call(pcallcontext_dtor,S_dtor.CURRENT,S_dtor.FRAMES) = (pdestructorcall)
pdestructorcall.PENDING = (n_error)
pdestructorcall.OPERATION = (pdestructionoperation)
pdestructionoperation.PENDING = (n_error)
S_dtor.STORE[n_slot] = DEFINED pvalue_raw
$gr_output(S_dtor.EVENTS) = $ptascii("C:G|")
~$gr_active(S_dtor,n_owner,ptbytes_name) /\ $gr_guard(S_dtor)
""")
        reached += scoped.reach('S_catch','S_dtor','SG_CATCH') + common.lines(r"""
S_catch.TODO = (CATCH_BIND porigin_catch n_index n_h) :: ptask_catch_tail*
$throwable_previous_id(S_catch,n_h) = (n_error)
$throwable_previous_id(S_catch,n_error) = eps
$lookup(S_catch.ENV,$ptascii("result")) = (n_result_cell)
S_catch.STORE[n_result_cell] = DEFINED (PINT 42)
S_catch.STORE[n_slot] = DEFINED pvalue_after
$string_bytes(pvalue_after) = ($ptascii("8"))
$propref_at(S_catch.PROPREFS,n_slot) = (ppropref)
~((HOBJECT n_owner) <- S_catch.ALLOCATIONS)
$gr_output(S_catch.EVENTS) = $ptascii("C:G|D|kept7|")
$gr_guard(S_catch)
S_end = S_catch
""")
    else:
        reached += common.lines(r"""
~((HOBJECT n_probe) <- S_result.ALLOCATIONS)
$string_bytes(pvalue_raw) = ($ptascii("9"))
$property_get_unconstrained(S_result,S_result.RESULT)
$propref_at(S_result.PROPREFS,n_slot) = eps
S_verified = $property_get_verify(S_result,ppropertyget,S_result.RESULT)
S_verified = S_result[.STORE[n_slot] = DEFINED (PINT 9)]
$gr_output(S_result.EVENTS) = $ptascii("W:G|L|")
PhpStep: S_result ~> S_copy_raw
S_copy_raw.TODO = [PROPERTY_GET_COPY ppropertyget (REFERENCE n_slot), PROPERTY_GET_BASE ppropertyget] ++ ptask_tail*
S_copy_raw.STORE[n_slot] = DEFINED (PINT 9)
S_copy_pending = $gr_after(S_result,S_copy_raw)
ptask_copy* = S_copy_raw.TODO
""")
        reached += scoped.reach('S_copy','S_copy_pending','SG_TAIL ptask_copy*') + common.lines(r"""
$heap_owners($heap_graph(S_copy),HOBJECT n_owner) = 1
PhpStep: S_copy ~> S_copied_raw
S_copied_raw.RESULT = KNOWN (PINT 9)
S_copied_raw.TODO = (PROPERTY_GET_BASE ppropertyget) :: ptask_tail*
S_base_pending = $gr_after(S_copy,S_copied_raw)
ptask_base* = S_copied_raw.TODO
""")
        reached += scoped.reach('S_base','S_base_pending','SG_TAIL ptask_base*') + common.lines(r"""
S_base.STORE[n_slot] = DEFINED (PINT 9)
$heap_owners($heap_graph(S_base),HCELL n_slot) = 1
$property_get_base_valid(S_base,ppropertyget)
PhpStep: S_base ~> S_released_raw
S_released_raw.RESULT = KNOWN (PINT 9) /\ S_released_raw.TODO = ptask_tail*
S_release_pending = $gr_after(S_base,S_released_raw)
""")
        reached += common.reach('S_dtor','S_release_pending','GR_DTOR n_owner') + common.lines(r"""
S_dtor.CURRENT = (pcallcontext_dtor)
$destructor_context_call(pcallcontext_dtor,S_dtor.CURRENT,S_dtor.FRAMES) = (pdestructorcall)
pdestructorcall.OPERATION = (pdestructionoperation)
pdestructionoperation.SOURCE = PROPERTY_GET_BASE ppropertyget
pdestructionoperation.VALUE = KNOWN (PINT 9) /\ pdestructionoperation.PENDING = eps
S_dtor.STORE[n_slot] = DEFINED (PINT 9)
~$gr_active(S_dtor,n_owner,ptbytes_name) /\ $gr_guard(S_dtor)
""")
        reached += scoped.reach('S_received','S_dtor','SG_TAIL ptask_tail*') + common.lines(r"""
S_received.RESULT = KNOWN (PINT 9)
S_received.STORE[n_slot] = DEFINED pvalue_after
$string_bytes(pvalue_after) = ($ptascii("free"))
$propref_at(S_received.PROPREFS,n_slot) = eps
~((HOBJECT n_owner) <- S_received.ALLOCATIONS)
$gr_output(S_received.EVENTS) = $ptascii("W:G|L|D|verified9|")
$gr_guard(S_received)
S_end = S_received
""")
    reached += [line.replace('n_child','n_owner') for line in common.FINISH[:-3]]
    return reached,common.FINISH[-3:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_get_owned_reference_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    assert [case['id'] for case in data['cases']] == ['weak-local', 'exact-source', 'conflict-replace', 'payload-drop', 'denied-source']
    assert [case['id'] for case in data['controls']] == []
    assert all(sha(HERE / case['source_file']) == case['source_sha256'] for case in data['cases'] + data['controls'])
    selected = [next(case for case in data['cases'] if case['id'] == identifier) for identifier in ('weak-local', 'conflict-replace')]
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
    out = Path(tempfile.mkdtemp(prefix='magic-get-owned-reference-protocol-', dir=ROOT / '.tools'))
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
            fixture = directory / 'owned-reference.watsup'
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
