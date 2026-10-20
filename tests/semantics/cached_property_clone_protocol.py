"""Check cached ordinary clone tables, singleton/held references and payload lifetime."""
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
syntax pcachedclonestage = CC_CLONE | CC_CATCH | CC_OUTPUT ptbytes | CC_DTOR nat
dec $cc_output(pevent*) : ptbytes
def $cc_output(eps) = eps
def $cc_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $cc_output(pevent*)
dec $cc_stage(pstate,pcachedclonestage) : bool
def $cc_stage(S,CC_CLONE) = true
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S_view = S[.COMPLETION = NORMAL]
  -- if S_view.TODO = (CLONE_RESULT porigin z) :: ptask_tail*
  -- if S_read = $resolve(S_view,S_view.RESULT)
  -- if S_read.COMPLETION = NORMAL
  -- if S_read.RESULT = KNOWN (POBJECT n_source)
  -- if $clone_cached_ready(S_view,n_source)
def $cc_stage(S,CC_CATCH) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask_tail*
def $cc_stage(S,CC_OUTPUT ptbytes) = ($cc_output(S.EVENTS) = ptbytes)
def $cc_stage(S,CC_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $cc_stage(S,pcachedclonestage) = false -- otherwise
dec $cc_seek(pstate,pcachedclonestage,nat) : pstate
def $cc_seek(S,pcachedclonestage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $cc_stage(S,pcachedclonestage) \/ n = 0
def $cc_seek(S,pcachedclonestage,n) = $cc_seek($drive_steps(S[.COMPLETION = NORMAL],1),pcachedclonestage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$cc_stage(S,pcachedclonestage) /\ $(n > 0)
def $cc_seek(S,pcachedclonestage,n) = $cc_seek($drive_steps(S,1),pcachedclonestage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $cc_seek(S,pcachedclonestage,n) = S -- otherwise
dec $cc_guard(pstate) : bool
def $cc_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $object_tables_valid(S) /\ $gc_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''

COMMON = r'''
S_front.TODO = (CLONE_RESULT porigin_clone z_clone) :: ptask_tail*
S_front.ORIGIN = (porigin_clone)
S_front.CURRENT = eps
$clone_task_valid(S_front,porigin_clone,z_clone)
$lookup(S_front.ENV,$ptascii("source")) = (n_source_cell)
S_front.STORE[n_source_cell] = DEFINED (POBJECT n_source)
$clone_cached_ready(S_front,n_source)
$objectprops_record_at(S_front.OBJECTPROPS,n_source) = (pobjectprops_source)
pobjectprops_source.MATERIALIZED
$clone_cached_slots(pobjectprops_source.SLOTS)
$object_table_at(S_front.OBJECTTABLES,n_source) = (n_table_source)
$node_children(S_front,HARRAY n_table_source) = eps
$heap_owners($heap_graph(S_front),HOBJECT n_source) = 1
$heap_owners($heap_graph(S_front),HARRAY n_table_source) = 1
$cc_output(S_front.EVENTS) = ptbytes_before
$cc_guard(S_front)
S_step = $drive_steps(S_front,1)
S_step.COMPLETION = NORMAL \/ S_step.COMPLETION = BUDGET
S_copy = S_step[.COMPLETION = NORMAL]
S_copy.RESULT = KNOWN (POBJECT n_copy)
n_copy = |S_front.OBJECTS|
S_copy.OBJECTS[n_copy] = S_front.OBJECTS[n_source]
$object_table_at(S_copy.OBJECTTABLES,n_copy) = (n_table_copy)
n_table_copy = |S_front.ARRAYS|
n_table_copy =/= n_table_source
$object_table_at(S_copy.OBJECTTABLES,n_source) = (n_table_source)
S_copy.ARRAYS[n_table_source] = S_front.ARRAYS[n_table_source]
$objectprops_record_at(S_copy.OBJECTPROPS,n_source) = (pobjectprops_source)
$objectprops_record_at(S_copy.OBJECTPROPS,n_copy) = (pobjectprops_copy)
pobjectprops_copy.MATERIALIZED
$node_children(S_copy,HARRAY n_table_source) = eps
$node_children(S_copy,HARRAY n_table_copy) = eps
$heap_owners($heap_graph(S_copy),HOBJECT n_source) = 1
$heap_owners($heap_graph(S_copy),HOBJECT n_copy) = 1
$heap_owners($heap_graph(S_copy),HARRAY n_table_source) = 1
$heap_owners($heap_graph(S_copy),HARRAY n_table_copy) = 1
S_copy.ALLOCATIONS = S_front.ALLOCATIONS ++ [HOBJECT n_copy,HARRAY n_table_copy]
$cc_output(S_copy.EVENTS) = ptbytes_before
$cc_guard(S_copy)
'''.strip().splitlines()

REFERENCE = r'''
$property_slot_at(pobjectprops_source.SLOTS,$ptascii("value")) = (ppropertyslot_source)
ppropertyslot_source.STATE = PROP_VALUE (ALIAS n_cell)
ppropertyslot_source.DECL = (porigin_property)
$propref_at(S_front.PROPREFS,n_cell) = (ppropref_source)
ppropref_source.SOURCES = [OBJECT_PROP_SOURCE n_source $ptascii("value") porigin_property]
$property_slot_at(pobjectprops_copy.SLOTS,$ptascii("value")) = (ppropertyslot_copy)
'''.strip().splitlines()

SINGLETON = r'''
$heap_owners($heap_graph(S_front),HCELL n_cell) = 1
ppropertyslot_copy.STATE = PROP_VALUE (DIRECT (PINT 1))
$heap_owners($heap_graph(S_copy),HCELL n_cell) = 1
$propref_at(S_copy.PROPREFS,n_cell) = (ppropref_source)
S_catch_found = $cc_seek(S_copy,CC_CATCH,1000)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_try n_catch n_error) :: ptask_catch*
S_catch.OBJECTS[n_error] = THROWABLE pthrowable_error
pthrowable_error.KIND = "TypeError"
$cc_output(S_catch.EVENTS) = $ptascii("U:1|7|")
$objectprops_record_at(S_catch.OBJECTPROPS,n_source) = (pobjectprops_source_catch)
$property_slot_at(pobjectprops_source_catch.SLOTS,$ptascii("value")) = (ppropertyslot_source_catch)
ppropertyslot_source_catch.STATE = PROP_VALUE (ALIAS n_cell)
S_catch.STORE[n_cell] = DEFINED (PINT 1)
$objectprops_record_at(S_catch.OBJECTPROPS,n_copy) = (pobjectprops_copy_catch)
$property_slot_at(pobjectprops_copy_catch.SLOTS,$ptascii("value")) = (ppropertyslot_copy_catch)
ppropertyslot_copy_catch.STATE = PROP_VALUE (DIRECT (PINT 7))
$propref_at(S_catch.PROPREFS,n_cell) = (ppropref_source)
$cc_guard(S_catch)
S_end = S_catch
'''.strip().splitlines()

HELD = r'''
$heap_owners($heap_graph(S_front),HCELL n_cell) = 2
ppropertyslot_copy.STATE = PROP_VALUE (ALIAS n_cell)
$heap_owners($heap_graph(S_copy),HCELL n_cell) = 3
$propref_at(S_copy.PROPREFS,n_cell) = (ppropref_copy)
ppropref_copy.SOURCES = [OBJECT_PROP_SOURCE n_source $ptascii("value") porigin_property,OBJECT_PROP_SOURCE n_copy $ptascii("value") porigin_property]
S_catch_found = $cc_seek(S_copy,CC_CATCH,1000)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_try n_catch n_error) :: ptask_catch*
S_catch.OBJECTS[n_error] = THROWABLE pthrowable_error
pthrowable_error.KIND = "TypeError"
$cc_output(S_catch.EVENTS) = $ptascii("H:7|7|7|8|8|")
$objectprops_record_at(S_catch.OBJECTPROPS,n_source) = (pobjectprops_source_catch)
$property_slot_at(pobjectprops_source_catch.SLOTS,$ptascii("value")) = (ppropertyslot_source_catch)
ppropertyslot_source_catch.STATE = PROP_UNSET
$propref_at(S_catch.PROPREFS,n_cell) = (ppropref_catch)
ppropref_catch.SOURCES = [OBJECT_PROP_SOURCE n_copy $ptascii("value") porigin_property]
S_catch.STORE[n_cell] = DEFINED (PINT 8)
$heap_owners($heap_graph(S_catch),HCELL n_cell) = 2
$cc_guard(S_catch)
S_free_found = $cc_seek(S_catch,CC_OUTPUT $ptascii("H:7|7|7|8|8|T|8|8|free|"),1000)
S_free_found.COMPLETION = NORMAL \/ S_free_found.COMPLETION = BUDGET
S_free = S_free_found[.COMPLETION = NORMAL]
$cc_output(S_free.EVENTS) = $ptascii("H:7|7|7|8|8|T|8|8|free|")
S_free.STORE[n_cell] = DEFINED (PSTRING $ptascii("free"))
$propref_at(S_free.PROPREFS,n_cell) = eps
$heap_owners($heap_graph(S_free),HCELL n_cell) = 1
$cc_guard(S_free)
S_end = S_free
'''.strip().splitlines()

FOREACH = r'''
pobjectprops_copy.SLOTS = pobjectprops_source.SLOTS
S_iterated_found = $cc_seek(S_copy,CC_OUTPUT $ptascii("F:a:2|b:10|S|a:1|b:30|U|b:10|"),1000)
S_iterated_found.COMPLETION = NORMAL \/ S_iterated_found.COMPLETION = BUDGET
S_iterated = S_iterated_found[.COMPLETION = NORMAL]
$cc_output(S_iterated.EVENTS) = $ptascii("F:a:2|b:10|S|a:1|b:30|U|b:10|")
$object_table_at(S_iterated.OBJECTTABLES,n_source) = (n_table_source)
$object_table_at(S_iterated.OBJECTTABLES,n_copy) = (n_table_copy)
S_iterated.ARRAYS[n_table_source].ITEMS = S_front.ARRAYS[n_table_source].ITEMS
S_iterated.ARRAYS[n_table_copy].ITEMS = S_copy.ARRAYS[n_table_copy].ITEMS
$objectprops_record_at(S_iterated.OBJECTPROPS,n_copy) = (pobjectprops_iterated)
$property_slot_at(pobjectprops_iterated.SLOTS,$ptascii("a")) = (ppropertyslot_unset)
ppropertyslot_unset.STATE = PROP_UNSET
$property_slot_at(pobjectprops_iterated.SLOTS,$ptascii("b")) = (ppropertyslot_b)
ppropertyslot_b.STATE = PROP_VALUE (DIRECT (PINT 10))
$cc_guard(S_iterated)
S_end = S_iterated
'''.strip().splitlines()

PAYLOAD = r'''
$property_slot_at(pobjectprops_source.SLOTS,$ptascii("payload")) = (ppropertyslot_payload)
ppropertyslot_payload.STATE = PROP_VALUE (DIRECT (POBJECT n_payload))
$property_slot_at(pobjectprops_copy.SLOTS,$ptascii("payload")) = (ppropertyslot_payload)
$heap_owners($heap_graph(S_front),HOBJECT n_payload) = 1
$heap_owners($heap_graph(S_copy),HOBJECT n_payload) = 2
S_source_dtor_found = $cc_seek(S_copy,CC_DTOR n_source,1000)
S_source_dtor_found.COMPLETION = NORMAL \/ S_source_dtor_found.COMPLETION = BUDGET
S_source_dtor = S_source_dtor_found[.COMPLETION = NORMAL]
$cc_stage(S_source_dtor,CC_DTOR n_source)
$cc_guard(S_source_dtor)
S_survived_found = $cc_seek(S_source_dtor,CC_OUTPUT $ptascii("P:S|D1|A|"),1000)
S_survived_found.COMPLETION = NORMAL \/ S_survived_found.COMPLETION = BUDGET
S_survived = S_survived_found[.COMPLETION = NORMAL]
$cc_output(S_survived.EVENTS) = $ptascii("P:S|D1|A|")
~(HOBJECT n_source <- S_survived.ALLOCATIONS)
~(HARRAY n_table_source <- S_survived.ALLOCATIONS)
(HOBJECT n_copy) <- S_survived.ALLOCATIONS
(HARRAY n_table_copy) <- S_survived.ALLOCATIONS
$heap_owners($heap_graph(S_survived),HOBJECT n_payload) = 1
$objectprops_record_at(S_survived.OBJECTPROPS,n_payload) = (pobjectprops_payload)
$property_slot_at(pobjectprops_payload.SLOTS,$ptascii("value")) = (ppropertyslot_payload_value)
ppropertyslot_payload_value.STATE = PROP_VALUE (DIRECT (PINT 7))
$node_children(S_survived,HARRAY n_table_copy) = eps
$cc_guard(S_survived)
S_payload_dtor_found = $cc_seek(S_survived,CC_DTOR n_payload,1000)
S_payload_dtor_found.COMPLETION = NORMAL \/ S_payload_dtor_found.COMPLETION = BUDGET
S_payload_dtor = S_payload_dtor_found[.COMPLETION = NORMAL]
$cc_stage(S_payload_dtor,CC_DTOR n_payload)
$cc_output(S_payload_dtor.EVENTS) = $ptascii("P:S|D1|A|D2|")
$cc_guard(S_payload_dtor)
S_end = S_payload_dtor
'''.strip().splitlines()

FINISH = r'''
S_final = $drive_steps(S_end,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$cc_output(S_final.EVENTS) = ptbytes_final
$cc_guard(S_final)
~(HOBJECT n_source <- S_final.ALLOCATIONS)
~(HOBJECT n_copy <- S_final.ALLOCATIONS)
~(HARRAY n_table_source <- S_final.ALLOCATIONS)
~(HARRAY n_table_copy <- S_final.ALLOCATIONS)
S_zero = $drive_steps(S_front,0)
S_zero = S_front[.COMPLETION = BUDGET]
S_resumed = $drive_steps(S_zero[.COMPLETION = NORMAL],10000)
S_resumed = S_final
'''.strip().splitlines()

DERIVED = r'''
$clone_cached_table(n_source,n_copy,([ENTRY (KSTRING $ptascii("a")) (DIRECT (PINT 1))]),$array_empty()) = eps
$clone_cached_table(n_source,n_copy,([ENTRY (KSTRING $ptascii("a")) (INDIRECT n_source $ptascii("b"))]),$array_empty()) = eps
$clone_cached_table($(n_source + 1),n_copy,S_front.ARRAYS[n_table_source].ITEMS,$array_empty()) = eps
~$clone_cached_slots([pobjectprops_source.SLOTS[0][.DECL = eps]])
S_wrong_cache = S_copy[.ARRAYS = $array_replace(S_copy.ARRAYS,n_table_copy,S_copy.ARRAYS[n_table_copy][.ITEMS = S_front.ARRAYS[n_table_source].ITEMS])]
~$object_tables_valid(S_wrong_cache)
S_oob = S_front[.OBJECTTABLES = [{OBJECT n_source,TABLE |S_front.ARRAYS|}]]
~$clone_cached_ready(S_oob,n_source)
S_refused = $clone_plain(S_oob,n_source)
S_refused.COMPLETION = UNSUPPORTED "cached ordinary property-table cloning"
S_refused.STORE = S_oob.STORE /\ S_refused.OBJECTS = S_oob.OBJECTS /\ S_refused.ARRAYS = S_oob.ARRAYS
~$clone_task_valid(S_front,porigin_clone,$(z_clone + 1))
'''.strip().splitlines()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', action='append', choices=('foreach', 'singleton', 'held', 'payload'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'cached_property_clone_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_observations_accepted']
    assert [case['id'] for case in data['cases']] == ['scalar', 'singleton', 'held', 'payload', 'foreach']
    case_map = {case['id']: case for case in data['cases']}
    selected = [case_map[name] for name in ('foreach', 'singleton', 'held', 'payload')]
    if args.case:
        assert len(args.case) == len(set(args.case))
        selected = [case for case in selected if case['id'] in args.case]
        assert len(selected) == len(args.case)
    php, adapter, bridge, worker, runner, compiler = (ROOT / name for name in [
        '.tools/php/bin/php', '_build/default/adapter/main.exe', '.tools/php-file.so',
        'frontend/worker.php', 'tests/semantics/_build/default/numeric_runner.exe', '.tools/spectec/bin/p4spectec'])
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    assert sha(compiler) == '26d77fb9bfae2b2868e137a94051f55f9b607660c340e9b22ae8300fb0d8ce88'
    assert sha(runner) == 'b57a2ed7daf86de23993a29d079083377cfef6da133739a164dbfdb9f11fd7a0'
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_bytes())]
    watched = [Path(__file__), Path(recorder.__file__), catalogue, profile_file, php, adapter, bridge, worker, runner, compiler,
               manifest, *modules, *(HERE / case['source_file'] for case in data['cases']),
               *(ROOT / name for name in ['spec/schema.json', 'spec/php.watsup', 'spec/nodes.json', 'frontend/target.php',
                    'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py'])]
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    assert revision == args.revision and not status, (revision, status)
    before = {str(path): sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='cached-property-clone-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    report = {'revision': revision, 'inputs': before, 'profile': profile, 'module_count': len(modules),
              'mode': 'SL', 'cache': False, 'det': True, 'records': [], 'fixtures': [], 'selection': [case['id'] for case in selected],
              'application_invocations': 0, 'application_evaluations': 0, 'source_agreements': 0,
              'premises': 0, 'reached_premises': 0, 'derived_premises': 0,
              'cap_seconds': 90, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent', 'jobs': 1}, 'passed': False}
    try:
        flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
        for case in selected:
            name = case['id']
            source = HERE / case['source_file']
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256']
            native_stderr = base64.b64decode(case['stderr_template_base64']).replace(b'{FILE}', case['original_source'].encode())
            native_tuple = base64.b64decode(case['stdout_base64']) + b'\0' + native_stderr + b'\0' + str(case['exit_status']).encode()
            assert hashlib.sha256(native_tuple).hexdigest() == case['native_raw_sha256']
            directory = out / name
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
            output = base64.b64decode(case['stdout_base64']).decode()
            before_output = {'foreach':'F:', 'singleton':'U:', 'held':'H:', 'payload':'P:'}[name]
            setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $cc_seek(S_initial,CC_CLONE,1000)', r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S_front = S_found[.COMPLETION = NORMAL]',
                     'ptbytes_before = $ptascii(' + json.dumps(before_output) + ')',
                     'ptbytes_final = $ptascii(' + json.dumps(output) + ')']
            reached = setup + COMMON
            keys = {'foreach':['a','b'], 'singleton':['value'], 'held':['value'], 'payload':['tag','payload']}[name]
            old_entries = ','.join('ENTRY (KSTRING $ptascii(' + json.dumps(key) + ')) (INDIRECT n_source $ptascii(' + json.dumps(key) + '))' for key in keys)
            new_entries = ','.join('ENTRY (KSTRING $ptascii(' + json.dumps(key) + ')) (INDIRECT n_copy $ptascii(' + json.dumps(key) + '))' for key in keys)
            positions = ','.join('POSITION (KSTRING $ptascii(' + json.dumps(key) + ')) ' + str(index) for index,key in enumerate(keys))
            reached += ['S_front.ARRAYS[n_table_source].ITEMS = [' + old_entries + ']',
                        'S_copy.ARRAYS[n_table_copy].ITEMS = [' + new_entries + ']',
                        'S_copy.ARRAYS[n_table_copy].POSITIONS = [' + positions + ']',
                        'S_copy.ARRAYS[n_table_copy].SERIAL = ' + str(len(keys)),
                        'S_copy.ARRAYS[n_table_copy].NEXT = $(-9223372036854775808)']
            if name == 'foreach':
                reached += FOREACH
            elif name == 'singleton':
                reached += REFERENCE + SINGLETON
            elif name == 'held':
                reached += REFERENCE + HELD
            else:
                reached += PAYLOAD
            reached += FINISH + [f'z_clone = {case["clone_line"]}']
            if name == 'payload':
                reached += ['~(HOBJECT n_payload <- S_final.ALLOCATIONS)']
            derived = DERIVED if name == 'foreach' else []
            content = PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
            for condition in reached + derived:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $main() = false -- otherwise\n'
            fixture = directory / 'clone.watsup'
            fixture.write_text(content)
            row = {'id': name, 'path': str(fixture), 'sha256': sha(fixture), 'reached_premises': len(reached), 'derived_premises': len(derived), 'premises': len(reached) + len(derived)}
            report['fixtures'].append(row)
            for key in ('premises', 'reached_premises', 'derived_premises'):
                report[key] += row[key]
        report.update(prepared=True, passed=True)
        if not args.prepare_only:
            for fixture in report['fixtures']:
                directory = Path(fixture['path']).parent
                process = recorder.recorded([str(compiler), 'algo', *map(str, modules), fixture['path']], directory / 'compiler', 90)
                passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and not (directory / 'compiler.stderr').read_bytes() and b'\ndef $main : bool =\n' in (directory / 'compiler.stdout').read_bytes()
                report['records'].append({'id': fixture['id'] + '-algorithmic-compilation', 'process': process, 'passed': passed, 'application_evaluations': 0})
                report['passed'] = passed
                assert passed
                report['application_invocations'] += 1
                process = recorder.recorded([str(runner), '--sl', *map(str, modules), fixture['path']], directory / 'state', 90)
                output = (directory / 'state.stdout').read_bytes()
                evaluated = process['exit'] == 0 and output in (b'true\n', b'false\n')
                report['application_evaluations'] += int(evaluated)
                passed = evaluated and not process['timeout'] and not process['group_after'] and not (directory / 'state.stderr').read_bytes() and output == b'true\n'
                report['records'].append({'id': fixture['id'] + '-strict-SL-application', 'process': process, 'passed': passed})
                report['passed'] = passed
                assert passed
    finally:
        report.update(inputs_stable=before == {str(path): sha(path) for path in watched},
                      fixtures_stable=all(row['sha256'] == sha(Path(row['path'])) for row in report['fixtures']),
                      head_stable=revision == git('rev-parse', 'HEAD'), status_stable=status == git('status', '--short'))
        report['passed'] = report['passed'] and all(report[key] for key in ('inputs_stable', 'fixtures_stable', 'head_stable', 'status_stable'))
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({key: report[key] for key in ('passed', 'application_evaluations', 'premises', 'reached_premises', 'derived_premises', 'inputs_stable', 'head_stable', 'status_stable')}), flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
