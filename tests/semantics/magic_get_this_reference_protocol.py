"""Check literal-this references through local cleanup and ordinary method retirement."""
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
import magic_get_owned_reference_protocol as owned
PREFIX = owned.PREFIX + r"""
syntax ptrstage = TR_THROW_COPY ppropertyget nat | TR_THROW_DROP ppropertyget nat pvalue
dec $tr_stage(pstate,ptrstage) : bool
def $tr_stage(S,TR_THROW_COPY ppropertyget n_error) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_COPY ppropertyget (REFERENCE n_cell)) :: ptask_tail*
def $tr_stage(S,TR_THROW_DROP ppropertyget n_error pvalue) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_DROP ppropertyget pvalue) :: ptask_tail*
def $tr_stage(S,ptrstage) = false -- otherwise
dec $tr_seek(pstate,ptrstage,nat) : pstate
def $tr_seek(S,ptrstage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $tr_stage(S,ptrstage) \/ n = 0
def $tr_seek(S,ptrstage,n) = $tr_seek($drive_steps(S[.COMPLETION = NORMAL],1),ptrstage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$tr_stage(S,ptrstage) /\ $(n > 0)
def $tr_seek(S,ptrstage,n) = $tr_seek($drive_steps(S,1),ptrstage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $tr_seek(S,ptrstage,n) = S -- otherwise
"""

def reach(name, previous, stage):
    return [f'{name}_found = $tr_seek({previous},{stage},2000)',
        fr'{name}_found.COMPLETION = NORMAL \/ {name}_found.COMPLETION = BUDGET',
        f'{name} = {name}_found[.COMPLETION = NORMAL]', f'$tr_stage({name},{stage})']

FRONT = common.lines(r"""
S_front.CURRENT = (pcallcontext_read)
pcallcontext_read.TARGET = METHOD_TARGET n_child porigin_read
pcallcontext_read.RECEIVER = (n_child) /\ $this_receiver(S_front) = (n_child)
S_front.FRAMES = pframe_caller_tail*
S_front.RESULT = KNOWN (POBJECT n_child) /\ S_front.BASE = BASE_VALUE (KNOWN PNULL)
$lookup(S_front.ENV,$ptascii("this")) = eps
$property_get_plan(S_front) = (ppropertyget)
ppropertyget.OBJECT = n_child /\ ppropertyget.SITE = porigin_site /\ ppropertyget.LINE = z_read
ptbytes_name = ppropertyget.NAME
ptbytes_name = $ptascii("ghost")
$property_get_this_source(S_front,ppropertyget) /\ $property_get_source(S_front,ppropertyget)
~$property_get_owned_source(S_front,ppropertyget) /\ $property_get_base_tasks(S_front,ppropertyget) = eps
$property_get_method(S_front,n_child) = (pmethoddesc_get)
pmethoddesc_get.FUNCTION.SIGNATURE.BYREF /\ ~pmethoddesc_get.FUNCTION.CODE.STRICT
$property_effective_desc(S_front,n_child,ptbytes_name) = (ppropertydesc_child)
ppropertydesc_child.VISIBILITY = PROPERTY_PUBLIC /\ ppropertydesc_child.TYPE = [PTBRANCH ([PTBUILTIN "string"])]
$property_get_lookup(S_front,ppropertyget) = PROPERTY_ACCESS ptbytes_key
ptbytes_key =/= ptbytes_name
$property_get_verify_desc(S_front,ppropertyget) = (ppropertydesc_parent)
ppropertyget.DECL = (ppropertydesc_parent.ORIGIN)
ppropertydesc_parent.KEY = ptbytes_key /\ ppropertydesc_parent.TYPE = [PTBRANCH ([PTBUILTIN "int"])]
$objectprops_at(S_front.OBJECTPROPS,n_child) = (ppropertyslot_front_all*)
$property_slot_at(ppropertyslot_front_all*,ptbytes_key) = (ppropertyslot_parent)
ppropertyslot_parent.DECL = ppropertyget.DECL /\ ppropertyslot_parent.STATE = PROP_UNSET
$property_get_capture(S_front,ppropertyget) /\ $property_get_history(S_front,ppropertyget)
S_front.TODO = (PROPERTY_PREP phpType20_name z_read) :: (DIM_FETCH z_read) :: ptask_tail*
$call_receiver_roots(pcallcontext_read) = [HOBJECT n_child]
n_owners_front = $heap_owners($heap_graph(S_front),HOBJECT n_child)
$gr_output(S_front.EVENTS) = ptbytes_prefix
~$gr_active(S_front,n_child,ptbytes_name) /\ $gr_guard(S_front)
PhpStep: S_front ~> S_begin_raw
S_begin = $gr_after(S_front,S_begin_raw)
S_begin.TODO = (CALL_ARGS (PROPERTY_GET_TARGET n_child ppropertyget.METHOD) eps 1 ([KNOWN (PSTRING ptbytes_name)]) (porigin_site) z_read) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
$heap_owners($heap_graph(S_begin),HOBJECT n_child) = n_owners_front
$property_get_base_count(S_begin.TODO,n_child,porigin_site) = 0
""")
ENTER = common.lines(r"""
S_get.CURRENT = (pcallcontext_get)
S_get.FRAMES = pframe_get :: pframe_caller_tail*
pframe_get.CONTEXT = (pcallcontext_read)
pframe_get.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
$property_get_frame(S_get,pcallcontext_get,pframe_get)
$call_receiver_roots(pcallcontext_get) = eps
$property_get_history(S_get,ppropertyget) /\ $property_get_this_source(S_get,ppropertyget)
S_global_get = $global_table_view(S_get)
$lookup(S_global_get.ENV,$ptascii("owner")) = (n_owner_cell)
$lookup(S_global_get.ENV,$ptascii("slot")) = (n_slot)
$gr_active(S_get,n_child,ptbytes_name) /\ $gr_guard(S_get)
""")
RESULT = common.lines(r"""
S_result.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
S_result.CURRENT = (pcallcontext_read) /\ S_result.FRAMES = pframe_caller_tail*
S_result.RESULT = REFERENCE n_slot
S_result.STORE[n_slot] = DEFINED pvalue_raw
$typed_string_value(pvalue_raw)
$property_get_verify_desc(S_result,ppropertyget) = (ppropertydesc_parent)
$property_get_valid(S_result,ppropertyget,true) /\ $property_get_tail_valid(S_result,ppropertyget)
$parameter_backing_at(S_result.PARAMETERBACKINGS,n_slot) = eps
~$gr_active(S_result,n_child,ptbytes_name) /\ $gr_guard(S_result)
""")

def conditions(case, checked):
    conflict = case['id'] == 'source-conflict'
    reached = [
        'S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(HERE / case['source_file']).encode()).decode()) + ')',
        r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
        'ptbytes_file = $ptascii(' + json.dumps(str(HERE / case['source_file'])) + ')',
        'ptbytes_prefix = $ptascii(' + json.dumps('C:r|' if conflict else 'W:') + ')',
        'ptbytes_final = $ptascii(' + json.dumps(base64.b64decode(case['stdout_base64']).decode()) + ')',
        f'z_read = {case["read_line"]}']
    reached += scoped.reach('S_front','S_initial','SG_FRONT z_read')
    reached += ['S_front.ORIGIN = (porigin_site)'] + FRONT
    reached += scoped.reach('S_get','S_begin','SG_ENTER ppropertyget') + ENTER
    if not conflict:
        reached += ['n_probe = |S_get.OBJECTS|']
        reached += owned.reach('S_exit','S_get','OV_EXIT ppropertyget') + common.lines(r"""
$property_get_recursive_exit(S_exit,S_exit.TODO,ppropertyget) = (pdestructionframe_get)
pdestructionframe_get.FUNCTION = ppropertyget.METHOD
pdestructionframe_get.VALUE = REFERENCE n_slot /\ pdestructionframe_get.PENDING = eps
pdestructionframe_get <- S_exit.DESTRUCTION.FRAMES
S_exit.STORE[n_slot] = DEFINED pvalue_before
$string_bytes(pvalue_before) = ($ptascii("7"))
$gr_output(S_exit.EVENTS) = $ptascii("W:G|")
$gr_active(S_exit,n_child,ptbytes_name) /\ $gr_guard(S_exit)
""")
        reached += common.reach('S_probe','S_exit','GR_DTOR n_probe') + common.lines(r"""
S_probe.CURRENT = (pcallcontext_probe)
$destructor_context_call(pcallcontext_probe,S_probe.CURRENT,S_probe.FRAMES) = (pdestructorcall_probe)
pdestructorcall_probe.FRAME = (pdestructionframe_get) /\ pdestructorcall_probe.OPERATION = eps
pdestructionframe_get.VALUE = REFERENCE n_slot
$gr_active(S_probe,n_child,ptbytes_name) /\ $gr_guard(S_probe)
""")
        reached += common.reach('S_changed','S_probe','GR_OUTPUT ($ptascii("W:G|L|"))') + common.lines(r"""
S_changed.STORE[n_slot] = DEFINED pvalue_changed
$string_bytes(pvalue_changed) = ($ptascii("9"))
pdestructionframe_get <- S_changed.DESTRUCTION.FRAMES
pdestructionframe_get.VALUE = REFERENCE n_slot
S_live = $quiet_operand(S_changed,pdestructionframe_get.VALUE)
S_live.RESULT = KNOWN pvalue_changed
$gr_active(S_changed,n_child,ptbytes_name) /\ $gr_guard(S_changed)
""")
    reached += scoped.reach('S_result','S_get' if conflict else 'S_changed','SG_RESULT ppropertyget') + RESULT
    if conflict:
        message = 'Reference with value of type string held by property ThisConflictHolder129::$value of type string is not compatible with property ThisConflictParent129::$ghost of type int'
        reached += ['ptbytes_message = $ptascii(' + json.dumps(message) + ')'] + common.lines(r"""
S_result.STORE[n_owner_cell] = DEFINED PNULL
$string_bytes(pvalue_raw) = ($ptascii("7"))
$propref_at(S_result.PROPREFS,n_slot) = (ppropref)
ppropref.SOURCES = [OBJECT_PROP_SOURCE n_holder ($ptascii("value")) ppropertyid_holder]
$propref_descriptor(S_result,OBJECT_PROP_SOURCE n_holder ($ptascii("value")) ppropertyid_holder) = (ppropertydesc_holder)
ppropertydesc_holder.TYPE = [PTBRANCH ([PTBUILTIN "string"])]
$property_get_propref(S_result,ppropertyget,n_slot)
S_global = $global_table_view(S_result)
$lookup(S_global.ENV,$ptascii("replacement")) = (n_h_cell)
S_result.STORE[n_h_cell] = DEFINED (POBJECT n_h)
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
        reached += reach('S_throw_copy','S_pending','TR_THROW_COPY ppropertyget n_error') + common.lines(r"""
S_throw_copy.CURRENT = (pcallcontext_read)
$call_receiver_roots(pcallcontext_read) = [HOBJECT n_child]
$heap_owners($heap_graph(S_throw_copy),HOBJECT n_child) = 1
$heap_owners($heap_graph(S_throw_copy),HCELL n_slot) = 3
$property_get_base_count(S_throw_copy.TODO,n_child,porigin_site) = 0
S_throw_copy.STORE[n_slot] = DEFINED pvalue_raw
PhpStep: S_throw_copy ~> S_captured_raw
S_captured_raw.TODO = [THROW_SEARCH n_error, PROPERTY_GET_DROP ppropertyget pvalue_raw] ++ ptask_tail*
S_captured_raw.RESULT = KNOWN PNULL /\ S_captured_raw.BASE = BASE_VALUE (KNOWN PNULL)
S_captured_pending = $gr_after(S_throw_copy,S_captured_raw)
""")
        reached += reach('S_drop','S_captured_pending','TR_THROW_DROP ppropertyget n_error pvalue_raw') + common.lines(r"""
S_drop.CURRENT = (pcallcontext_read)
$heap_owners($heap_graph(S_drop),HOBJECT n_child) = 1
$heap_owners($heap_graph(S_drop),HCELL n_slot) = 2
$propref_at(S_drop.PROPREFS,n_slot) = (ppropref)
$gr_output(S_drop.EVENTS) = $ptascii("C:r|G|")
$gr_guard(S_drop)
""")
        reached += common.reach('S_dtor','S_drop','GR_DTOR n_child') + common.lines(r"""
S_dtor.CURRENT = (pcallcontext_dtor)
$destructor_context_call(pcallcontext_dtor,S_dtor.CURRENT,S_dtor.FRAMES) = (pdestructorcall)
pdestructorcall.PENDING = (n_error)
pdestructorcall.FRAME = (pdestructionframe_read)
pdestructorcall.OPERATION = eps
pdestructionframe_read.FUNCTION = porigin_read /\ pdestructionframe_read.PENDING = (n_error)
S_dtor.STORE[n_slot] = DEFINED pvalue_raw
$gr_output(S_dtor.EVENTS) = $ptascii("C:r|G|")
~$gr_active(S_dtor,n_child,ptbytes_name) /\ $gr_guard(S_dtor)
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
~((HOBJECT n_child) <- S_catch.ALLOCATIONS)
$gr_output(S_catch.EVENTS) = $ptascii("C:r|G|D|kept7|")
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
PhpStep: S_result ~> S_copy_raw
S_copy_raw.TODO = (PROPERTY_GET_COPY ppropertyget (REFERENCE n_slot)) :: ptask_tail*
S_copy_raw.STORE[n_slot] = DEFINED (PINT 9)
S_copy_pending = $gr_after(S_result,S_copy_raw)
ptask_copy* = S_copy_raw.TODO
""")
        reached += scoped.reach('S_copy','S_copy_pending','SG_TAIL ptask_copy*') + common.lines(r"""
S_copy.CURRENT = (pcallcontext_read)
$heap_owners($heap_graph(S_copy),HOBJECT n_child) = $(n_owners_front - 1)
$property_get_base_count(S_copy.TODO,n_child,porigin_site) = 0
n_slot_owners = $heap_owners($heap_graph(S_copy),HCELL n_slot)
PhpStep: S_copy ~> S_copied_raw
S_copied_raw.RESULT = KNOWN (PINT 9) /\ S_copied_raw.TODO = ptask_tail*
S_read_pending = $gr_after(S_copy,S_copied_raw)
""")
        reached += scoped.reach('S_read_value','S_read_pending','SG_TAIL ptask_tail*') + common.lines(r"""
S_read_value.RESULT = KNOWN (PINT 9)
S_read_value.CURRENT = (pcallcontext_read)
$heap_owners($heap_graph(S_read_value),HCELL n_slot) = $(n_slot_owners - 1)
$propref_at(S_read_value.PROPREFS,n_slot) = eps
S_read_value.STORE[n_owner_cell] = DEFINED (POBJECT n_child)
""")
        reached += common.reach('S_marker','S_read_value','GR_OUTPUT ($ptascii("W:G|L|r|copied9|"))') + common.lines(r"""
S_marker.CURRENT = (pcallcontext_read)
S_marker.STORE[n_owner_cell] = DEFINED PNULL
$lookup(S_marker.ENV,$ptascii("value")) = (n_value_cell)
S_marker.STORE[n_value_cell] = DEFINED (PINT 9)
S_marker.STORE[n_slot] = DEFINED pvalue_free
$string_bytes(pvalue_free) = ($ptascii("free"))
$propref_at(S_marker.PROPREFS,n_slot) = eps
$call_receiver_roots(pcallcontext_read) = [HOBJECT n_child]
$heap_owners($heap_graph(S_marker),HOBJECT n_child) = 1
(HOBJECT n_child) <- S_marker.ALLOCATIONS
~$gr_active(S_marker,n_child,ptbytes_name) /\ $gr_guard(S_marker)
""")
        reached += common.reach('S_dtor','S_marker','GR_DTOR n_child') + common.lines(r"""
S_dtor.CURRENT = (pcallcontext_dtor)
$destructor_context_call(pcallcontext_dtor,S_dtor.CURRENT,S_dtor.FRAMES) = (pdestructorcall)
pdestructorcall.FRAME = (pdestructionframe_read)
pdestructorcall.OPERATION = eps
pdestructionframe_read.FUNCTION = porigin_read /\ pdestructionframe_read.PENDING = eps
pdestructionframe_read.VALUE = KNOWN (PINT 9)
S_dtor.STORE[n_slot] = DEFINED pvalue_free
$gr_output(S_dtor.EVENTS) = $ptascii("W:G|L|r|copied9|")
~$gr_active(S_dtor,n_child,ptbytes_name) /\ $gr_guard(S_dtor)
S_end = S_dtor
""")
    reached += common.FINISH[:-3]
    return reached, common.FINISH[-3:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_get_this_reference_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    assert [case['id'] for case in data['cases']] == ['weak-local', 'source-conflict', 'exact-source']
    assert [case['id'] for case in data['controls']] == []
    assert all(sha(HERE / case['source_file']) == case['source_sha256'] for case in data['cases'] + data['controls'])
    selected = [next(case for case in data['cases'] if case['id'] == identifier) for identifier in ('weak-local', 'source-conflict')]
    php, adapter, bridge, worker, runner, compiler = (ROOT / name for name in [
        '.tools/php/bin/php', '_build/default/adapter/main.exe', '.tools/php-file.so',
        'frontend/worker.php', 'tests/semantics/_build/default/numeric_runner.exe', '.tools/spectec/bin/p4spectec'])
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    assert sha(compiler) == '26d77fb9bfae2b2868e137a94051f55f9b607660c340e9b22ae8300fb0d8ce88'
    assert sha(runner) == 'b57a2ed7daf86de23993a29d079083377cfef6da133739a164dbfdb9f11fd7a0'
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_bytes())]
    watched = [Path(__file__), Path(common.__file__), Path(scoped.__file__), Path(owned.__file__), Path(recorder.__file__), catalogue, profile_file,
        php, adapter, bridge, worker, runner, compiler, manifest, *modules,
        *(HERE / case['source_file'] for case in data['cases'] + data['controls']),
        *(ROOT / name for name in ['spec/schema.json', 'spec/php.watsup', 'spec/nodes.json',
            'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py',
            'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py'])]
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    assert revision == args.revision and not status, (revision, status)
    before = {str(path): sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='magic-get-this-reference-protocol-', dir=ROOT / '.tools'))
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
            fixture = directory / 'this-reference.watsup'
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
