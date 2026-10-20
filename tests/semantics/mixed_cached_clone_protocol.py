"""Check mixed declared/dynamic clone tables, wrappers and shallow lifetime."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()

def lines(text):
    return text.strip().splitlines()

PREFIX = r'''
syntax pmixedclonestage = MC_CLONE | MC_OUTPUT ptbytes | MC_DTOR nat
dec $mc_output(pevent*) : ptbytes
def $mc_output(eps) = eps
def $mc_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $mc_output(pevent*)
dec $mc_stage(pstate,pmixedclonestage) : bool
def $mc_stage(S,MC_CLONE) = true
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S_view = S[.COMPLETION = NORMAL]
  -- if S_view.TODO = (CLONE_RESULT porigin z) :: ptask_tail*
  -- if S_read = $resolve(S_view,S_view.RESULT)
  -- if S_read.COMPLETION = NORMAL
  -- if S_read.RESULT = KNOWN (POBJECT n_source)
  -- if $clone_mixed_ready(S_view,n_source)
def $mc_stage(S,MC_OUTPUT ptbytes) = ($mc_output(S.EVENTS) = ptbytes)
def $mc_stage(S,MC_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $mc_stage(S,pmixedclonestage) = false -- otherwise
dec $mc_seek(pstate,pmixedclonestage,nat) : pstate
def $mc_seek(S,pmixedclonestage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $mc_stage(S,pmixedclonestage) \/ n = 0
def $mc_seek(S,pmixedclonestage,n) = $mc_seek($drive_steps(S[.COMPLETION = NORMAL],1),pmixedclonestage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$mc_stage(S,pmixedclonestage) /\ $(n > 0)
def $mc_seek(S,pmixedclonestage,n) = $mc_seek($drive_steps(S,1),pmixedclonestage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $mc_seek(S,pmixedclonestage,n) = S -- otherwise
dec $mc_guard(pstate) : bool
def $mc_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $object_tables_valid(S) /\ $gc_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''

FRONT = lines(r'''
S_front.TODO = (CLONE_RESULT porigin_clone z_clone) :: ptask_tail*
S_front.ORIGIN = (porigin_clone)
S_front.CURRENT = eps
$clone_task_valid(S_front,porigin_clone,z_clone)
S_front.RESULT = VARIABLE $ptascii("source") z_source
$operand_nodes(S_front.RESULT) = eps
$lookup(S_front.ENV,$ptascii("source")) = (n_source_cell)
S_front.STORE[n_source_cell] = DEFINED (POBJECT n_source)
$lookup(S_front.ENV,$ptascii("key")) = eps
$lookup(S_front.ENV,$ptascii("value")) = eps
$clone_mixed_ready(S_front,n_source)
~$clone_cached_ready(S_front,n_source)
$objectprops_record_at(S_front.OBJECTPROPS,n_source) = (pobjectprops_source)
pobjectprops_source.MATERIALIZED
$object_table_at(S_front.OBJECTTABLES,n_source) = (n_table_source)
$node_children(S_front,HOBJECT n_source) = [HARRAY n_table_source]
$heap_owners($heap_graph(S_front),HOBJECT n_source) = 1
$heap_owners($heap_graph(S_front),HARRAY n_table_source) = 1
$mc_output(S_front.EVENTS) = ptbytes_before
$mc_guard(S_front)
''')

COPY = lines(r'''
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
S_copy.STORE = S_front.STORE
S_copy.PROPREFS = S_front.PROPREFS
$node_children(S_copy,HOBJECT n_source) = [HARRAY n_table_source]
$node_children(S_copy,HOBJECT n_copy) = [HARRAY n_table_copy]
$heap_owners($heap_graph(S_copy),HOBJECT n_source) = 1
$heap_owners($heap_graph(S_copy),HOBJECT n_copy) = 1
$heap_owners($heap_graph(S_copy),HARRAY n_table_source) = 1
$heap_owners($heap_graph(S_copy),HARRAY n_table_copy) = 1
S_copy.ALLOCATIONS = S_front.ALLOCATIONS ++ [HOBJECT n_copy,HARRAY n_table_copy]
$mc_output(S_copy.EVENTS) = ptbytes_before
$mc_guard(S_copy)
''')

SINGLETON = lines(r'''
$heap_owners($heap_graph(S_copy),HCELL n_cell) = 1
$node_children(S_copy,HARRAY n_table_copy) = eps
$node_children(S_copy,HARRAY n_table_source) = [HCELL n_cell]
S_changed_found = $mc_seek(S_copy,MC_OUTPUT $ptascii("U:1/7|9/7|"),1000)
S_changed_found.COMPLETION = NORMAL \/ S_changed_found.COMPLETION = BUDGET
S_changed = S_changed_found[.COMPLETION = NORMAL]
$mc_output(S_changed.EVENTS) = $ptascii("U:1/7|9/7|")
$objectprops_record_at(S_changed.OBJECTPROPS,n_source) = (pobjectprops_changed_source)
$property_slot_at(pobjectprops_changed_source.SLOTS,$ptascii("extra")) = (ppropertyslot_changed_source)
ppropertyslot_changed_source.DECL = eps /\ ppropertyslot_changed_source.STATE = PROP_VALUE (ALIAS n_cell)
$entry_lookup(S_changed.ARRAYS[n_table_source].ITEMS,KSTRING $ptascii("extra")) = (ALIAS n_cell)
S_changed.STORE[n_cell] = DEFINED (PINT 9)
$objectprops_record_at(S_changed.OBJECTPROPS,n_copy) = (pobjectprops_changed_copy)
$property_slot_at(pobjectprops_changed_copy.SLOTS,$ptascii("extra")) = (ppropertyslot_changed_copy)
ppropertyslot_changed_copy.DECL = eps /\ ppropertyslot_changed_copy.STATE = PROP_VALUE (DIRECT (PINT 7))
$entry_lookup(S_changed.ARRAYS[n_table_copy].ITEMS,KSTRING $ptascii("extra")) = (DIRECT (PINT 7))
$heap_owners($heap_graph(S_changed),HCELL n_cell) = 1
$propref_at(S_changed.PROPREFS,n_cell) = eps
$mc_guard(S_changed)
S_end = S_changed
''')

HELD = lines(r'''
$heap_owners($heap_graph(S_copy),HCELL n_cell) = 3
$node_children(S_copy,HARRAY n_table_copy) = [HCELL n_cell]
$node_children(S_copy,HARRAY n_table_source) = [HCELL n_cell]
S_changed_found = $mc_seek(S_copy,MC_OUTPUT $ptascii("H:7/7/7|9/9|"),1000)
S_changed_found.COMPLETION = NORMAL \/ S_changed_found.COMPLETION = BUDGET
S_changed = S_changed_found[.COMPLETION = NORMAL]
$mc_output(S_changed.EVENTS) = $ptascii("H:7/7/7|9/9|")
$objectprops_record_at(S_changed.OBJECTPROPS,n_source) = (pobjectprops_changed_source)
$property_slot_at(pobjectprops_changed_source.SLOTS,$ptascii("extra")) = (ppropertyslot_changed_source)
ppropertyslot_changed_source.DECL = eps /\ ppropertyslot_changed_source.STATE = PROP_UNSET
$entry_lookup(S_changed.ARRAYS[n_table_source].ITEMS,KSTRING $ptascii("extra")) = eps
$objectprops_record_at(S_changed.OBJECTPROPS,n_copy) = (pobjectprops_changed_copy)
$property_slot_at(pobjectprops_changed_copy.SLOTS,$ptascii("extra")) = (ppropertyslot_changed_copy)
ppropertyslot_changed_copy.DECL = eps /\ ppropertyslot_changed_copy.STATE = PROP_VALUE (ALIAS n_cell)
$entry_lookup(S_changed.ARRAYS[n_table_copy].ITEMS,KSTRING $ptascii("extra")) = (ALIAS n_cell)
S_changed.STORE[n_cell] = DEFINED (PINT 9)
$heap_owners($heap_graph(S_changed),HCELL n_cell) = 2
$mc_guard(S_changed)
S_free_found = $mc_seek(S_changed,MC_OUTPUT $ptascii("H:7/7/7|9/9|free|"),1000)
S_free_found.COMPLETION = NORMAL \/ S_free_found.COMPLETION = BUDGET
S_free = S_free_found[.COMPLETION = NORMAL]
$mc_output(S_free.EVENTS) = $ptascii("H:7/7/7|9/9|free|")
~(HOBJECT n_source <- S_free.ALLOCATIONS) /\ ~(HARRAY n_table_source <- S_free.ALLOCATIONS)
$objectprops_record_at(S_free.OBJECTPROPS,n_copy) = (pobjectprops_free_copy)
$property_slot_at(pobjectprops_free_copy.SLOTS,$ptascii("extra")) = (ppropertyslot_free_copy)
ppropertyslot_free_copy.STATE = PROP_UNSET
$entry_lookup(S_free.ARRAYS[n_table_copy].ITEMS,KSTRING $ptascii("extra")) = eps
$node_children(S_free,HARRAY n_table_copy) = eps
S_free.STORE[n_cell] = DEFINED (PSTRING_CARRIER INTERNED_STRING $ptascii("free"))
$propref_at(S_free.PROPREFS,n_cell) = eps
$heap_owners($heap_graph(S_free),HCELL n_cell) = 1
$mc_guard(S_free)
S_end = S_free
''')

PAYLOAD = lines(r'''
$heap_owners($heap_graph(S_front),HOBJECT n_payload) = 1
$heap_owners($heap_graph(S_copy),HOBJECT n_payload) = 2
$node_children(S_front,HARRAY n_table_source) = [HOBJECT n_payload]
$node_children(S_copy,HARRAY n_table_copy) = [HOBJECT n_payload]
S_source_dtor_found = $mc_seek(S_copy,MC_DTOR n_source,1000)
S_source_dtor_found.COMPLETION = NORMAL \/ S_source_dtor_found.COMPLETION = BUDGET
S_source_dtor = S_source_dtor_found[.COMPLETION = NORMAL]
$mc_stage(S_source_dtor,MC_DTOR n_source)
$mc_guard(S_source_dtor)
S_survived_found = $mc_seek(S_source_dtor,MC_OUTPUT $ptascii("P:D1|A|"),1000)
S_survived_found.COMPLETION = NORMAL \/ S_survived_found.COMPLETION = BUDGET
S_survived = S_survived_found[.COMPLETION = NORMAL]
$mc_output(S_survived.EVENTS) = $ptascii("P:D1|A|")
~(HOBJECT n_source <- S_survived.ALLOCATIONS) /\ ~(HARRAY n_table_source <- S_survived.ALLOCATIONS)
(HOBJECT n_copy) <- S_survived.ALLOCATIONS /\ (HARRAY n_table_copy) <- S_survived.ALLOCATIONS
$heap_owners($heap_graph(S_survived),HOBJECT n_payload) = 1
$objectprops_record_at(S_survived.OBJECTPROPS,n_payload) = (pobjectprops_payload)
$property_slot_at(pobjectprops_payload.SLOTS,$ptascii("value")) = (ppropertyslot_payload_value)
ppropertyslot_payload_value.STATE = PROP_VALUE (DIRECT (PINT 7))
$node_children(S_survived,HOBJECT n_copy) = [HARRAY n_table_copy]
$node_children(S_survived,HARRAY n_table_copy) = [HOBJECT n_payload]
$mc_guard(S_survived)
S_copy_dtor_found = $mc_seek(S_survived,MC_DTOR n_copy,1000)
S_copy_dtor_found.COMPLETION = NORMAL \/ S_copy_dtor_found.COMPLETION = BUDGET
S_copy_dtor = S_copy_dtor_found[.COMPLETION = NORMAL]
$mc_stage(S_copy_dtor,MC_DTOR n_copy)
$mc_output(S_copy_dtor.EVENTS) = $ptascii("P:D1|A|7|")
$mc_guard(S_copy_dtor)
S_payload_dtor_found = $mc_seek(S_copy_dtor,MC_DTOR n_payload,1000)
S_payload_dtor_found.COMPLETION = NORMAL \/ S_payload_dtor_found.COMPLETION = BUDGET
S_payload_dtor = S_payload_dtor_found[.COMPLETION = NORMAL]
$mc_stage(S_payload_dtor,MC_DTOR n_payload)
$mc_output(S_payload_dtor.EVENTS) = $ptascii("P:D1|A|7|D2|")
$mc_guard(S_payload_dtor)
S_end = S_payload_dtor
''')

FINISH = lines(r'''
S_final = $drive_steps(S_end,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$mc_output(S_final.EVENTS) = ptbytes_final
$mc_guard(S_final)
~(HOBJECT n_source <- S_final.ALLOCATIONS) /\ ~(HOBJECT n_copy <- S_final.ALLOCATIONS)
~(HARRAY n_table_source <- S_final.ALLOCATIONS) /\ ~(HARRAY n_table_copy <- S_final.ALLOCATIONS)
S_zero = $drive_steps(S_front,0)
S_zero = S_front[.COMPLETION = BUDGET]
S_resumed = $drive_steps(S_zero[.COMPLETION = NORMAL],10000)
S_resumed = S_final
''')

DERIVED = lines(r'''
$clone_mixed_table(S_front,n_source,n_copy,pobjectprops_source.SLOTS,[ENTRY (KSTRING $ptascii("declared")) (DIRECT (PINT 1))],$array_empty()) = eps
$clone_mixed_table(S_front,n_source,n_copy,pobjectprops_source.SLOTS,[ENTRY (KSTRING $ptascii("alpha")) (DIRECT (PINT 8))],$array_empty()) = eps
$clone_mixed_table(S_front,n_source,n_copy,pobjectprops_source.SLOTS,[ENTRY (KSTRING $ptascii("alpha")) UNINITIALIZED],$array_empty()) = eps
$clone_mixed_table(S_front,n_source,n_copy,pobjectprops_source.SLOTS,[ENTRY (KSTRING $ptascii("declared")) (INDIRECT n_source $ptascii("alpha"))],$array_empty()) = eps
$clone_mixed_table(S_front,$(n_source + 1),n_copy,pobjectprops_source.SLOTS,S_front.ARRAYS[n_table_source].ITEMS,$array_empty()) = eps
S_wrong_cache = S_copy[.ARRAYS = $array_replace(S_copy.ARRAYS,n_table_copy,S_front.ARRAYS[n_table_source])]
~$object_tables_valid(S_wrong_cache)
S_direct_declared = S_front[.ARRAYS = $array_replace(S_front.ARRAYS,n_table_source,S_front.ARRAYS[n_table_source][.ITEMS = [ENTRY (KSTRING $ptascii("declared")) (DIRECT (PINT 1)),ENTRY (KSTRING $ptascii("alpha")) (DIRECT (PINT 7)),ENTRY (KSTRING $ptascii("beta")) (DIRECT (PINT 9))]])]
$object_tables_valid(S_direct_declared)
~$clone_mixed_ready(S_direct_declared,n_source)
S_oob = S_front[.OBJECTTABLES = [{OBJECT n_source,TABLE (|S_front.ARRAYS|)}]]
~$clone_mixed_ready(S_oob,n_source)
S_refused = $clone_plain(S_oob,n_source)
S_refused.COMPLETION = UNSUPPORTED "cached ordinary property-table cloning"
S_refused.STORE = S_oob.STORE /\ S_refused.OBJECTS = S_oob.OBJECTS /\ S_refused.ARRAYS = S_oob.ARRAYS
~$clone_task_valid(S_front,porigin_clone,$(z_clone + 1))
S_late_input = S_iterated[.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]
$clone_mixed_ready(S_late_input,n_copy)
S_late = $clone_plain(S_late_input,n_copy)
S_late.COMPLETION = NORMAL
S_late.RESULT = KNOWN (POBJECT n_late)
n_late = |S_iterated.OBJECTS|
$object_table_at(S_late.OBJECTTABLES,n_late) = (n_table_late)
n_table_late = |S_iterated.ARRAYS|
S_late.ARRAYS[n_table_copy] = S_iterated.ARRAYS[n_table_copy]
$objectprops_record_at(S_late.OBJECTPROPS,n_copy) = (pobjectprops_iterated)
S_iterated.ARRAYS[n_table_copy].SERIAL = 4
S_late.ARRAYS[n_table_late].ITEMS = [ENTRY (KSTRING $ptascii("declared")) (INDIRECT n_late $ptascii("declared")),ENTRY (KSTRING $ptascii("beta")) (DIRECT (PINT 9)),ENTRY (KSTRING $ptascii("gamma")) (DIRECT (PINT 23))]
S_late.ARRAYS[n_table_late].POSITIONS = [POSITION (KSTRING $ptascii("declared")) 0,POSITION (KSTRING $ptascii("beta")) 1,POSITION (KSTRING $ptascii("gamma")) 2]
S_late.ARRAYS[n_table_late].SERIAL = 3
S_late.ARRAYS[n_table_late].NEXT = $(-9223372036854775808)
$objectprops_record_at(S_late.OBJECTPROPS,n_late) = (pobjectprops_late)
$property_slot_at(pobjectprops_late.SLOTS,$ptascii("alpha")) = (ppropertyslot_late_alpha)
ppropertyslot_late_alpha.DECL = eps /\ ppropertyslot_late_alpha.STATE = PROP_UNSET
$property_slot_at(pobjectprops_late.SLOTS,$ptascii("beta")) = (ppropertyslot_late_beta)
ppropertyslot_late_beta.DECL = eps /\ ppropertyslot_late_beta.STATE = PROP_VALUE (DIRECT (PINT 9))
$property_slot_at(pobjectprops_late.SLOTS,$ptascii("gamma")) = (ppropertyslot_late_gamma)
ppropertyslot_late_gamma.DECL = eps /\ ppropertyslot_late_gamma.STATE = PROP_VALUE (DIRECT (PINT 23))
$node_children(S_late,HOBJECT n_late) = [HARRAY n_table_late]
$node_children(S_late,HARRAY n_table_late) = eps
$mc_guard(S_late)
''')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', action='append', choices=('scalar', 'singleton', 'held', 'payload'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'mixed_cached_clone_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_observations_accepted']
    assert [case['id'] for case in data['cases']] == ['scalar', 'singleton', 'held', 'payload']
    case_map = {case['id']: case for case in data['cases']}
    selected = [case_map[name] for name in ('scalar', 'singleton', 'held', 'payload')]
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
    out = Path(tempfile.mkdtemp(prefix='mixed-cached-clone-protocol-', dir=ROOT / '.tools'))
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
            before_output = {'scalar':'M:declared:1|alpha:7|beta:9|', 'singleton':'U:', 'held':'H:', 'payload':'P:'}[name]
            setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $mc_seek(S_initial,MC_CLONE,1000)', r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S_front = S_found[.COMPLETION = NORMAL]',
                     'ptbytes_before = $ptascii(' + json.dumps(before_output) + ')',
                     'ptbytes_final = $ptascii(' + json.dumps(output) + ')']
            declared = 'tag' if name == 'payload' else 'declared'
            dynamics = ['alpha','beta'] if name == 'scalar' else ['payload' if name == 'payload' else 'extra']
            old_items = ['DIRECT (PINT 7)','DIRECT (PINT 9)'] if name == 'scalar' else ['DIRECT (POBJECT n_payload)' if name == 'payload' else 'ALIAS n_cell']
            new_items = ['DIRECT (PINT 1)'] if name == 'singleton' else old_items
            reached = setup + FRONT
            reached += ['$property_slot_at(pobjectprops_source.SLOTS,$ptascii(' + json.dumps(declared) + ')) = (ppropertyslot_declared)',
                        'ppropertyslot_declared.DECL = (porigin_property)',
                        'ppropertyslot_declared.STATE = PROP_VALUE (DIRECT (PINT 1))']
            if name in ('singleton','held'):
                reached += ['$property_slot_at(pobjectprops_source.SLOTS,$ptascii("extra")) = (ppropertyslot_extra)',
                            'ppropertyslot_extra.DECL = eps', 'ppropertyslot_extra.STATE = PROP_VALUE (ALIAS n_cell)',
                            'S_front.STORE[n_cell] = DEFINED (PINT 1)', '$propref_at(S_front.PROPREFS,n_cell) = eps',
                            '$heap_owners($heap_graph(S_front),HCELL n_cell) = ' + ('1' if name == 'singleton' else '2'),
                            '$lookup(S_front.ENV,$ptascii("alias")) = ' + ('eps' if name == 'singleton' else '(n_cell)')]
            if name == 'payload':
                reached += ['$property_slot_at(pobjectprops_source.SLOTS,$ptascii("payload")) = (ppropertyslot_source_payload)',
                            'ppropertyslot_source_payload.DECL = eps',
                            'ppropertyslot_source_payload.STATE = PROP_VALUE (DIRECT (POBJECT n_payload))']
            keys = [declared,*dynamics]
            def entries(owner,items):
                values = ['INDIRECT ' + owner + ' $ptascii(' + json.dumps(declared) + ')',*items]
                return '[' + ','.join('ENTRY (KSTRING $ptascii(' + json.dumps(key) + ')) (' + item + ')' for key,item in zip(keys,values)) + ']'
            reached += ['S_front.ARRAYS[n_table_source].ITEMS = ' + entries('n_source',old_items)]
            reached += COPY
            reached += ['S_copy.ARRAYS[n_table_copy].ITEMS = ' + entries('n_copy',new_items),
                        'S_copy.ARRAYS[n_table_copy].POSITIONS = [' + ','.join('POSITION (KSTRING $ptascii(' + json.dumps(key) + ')) ' + str(index) for index,key in enumerate(keys)) + ']',
                        'S_copy.ARRAYS[n_table_copy].SERIAL = ' + str(len(keys)),
                        'S_copy.ARRAYS[n_table_copy].NEXT = $(-9223372036854775808)',
                        '$property_slot_at(pobjectprops_copy.SLOTS,$ptascii(' + json.dumps(declared) + ')) = (ppropertyslot_declared)']
            for key,item in zip(dynamics,new_items):
                variable = 'ppropertyslot_copy_' + key
                reached += ['$property_slot_at(pobjectprops_copy.SLOTS,$ptascii(' + json.dumps(key) + ')) = (' + variable + ')',
                            variable + '.DECL = eps',variable + '.STATE = PROP_VALUE (' + item + ')']
            if name == 'scalar':
                late_output = output.split('s|')[0] + 's|'
                reached += ['$node_children(S_front,HARRAY n_table_source) = eps',
                            '$node_children(S_copy,HARRAY n_table_copy) = eps',
                            'S_iterated_found = $mc_seek(S_copy,MC_OUTPUT $ptascii(' + json.dumps(late_output) + '),1000)',
                            r'S_iterated_found.COMPLETION = NORMAL \/ S_iterated_found.COMPLETION = BUDGET',
                            'S_iterated = S_iterated_found[.COMPLETION = NORMAL]',
                            '$mc_output(S_iterated.EVENTS) = $ptascii(' + json.dumps(late_output) + ')',
                            '$object_table_at(S_iterated.OBJECTTABLES,n_source) = (n_table_source)',
                            '$object_table_at(S_iterated.OBJECTTABLES,n_copy) = (n_table_copy)',
                            'S_iterated.ARRAYS[n_table_source].ITEMS = [ENTRY (KSTRING $ptascii("declared")) (INDIRECT n_source $ptascii("declared")),ENTRY (KSTRING $ptascii("alpha")) (DIRECT (PINT 7)),ENTRY (KSTRING $ptascii("beta")) (DIRECT (PINT 19))]',
                            'S_iterated.ARRAYS[n_table_copy].ITEMS = [ENTRY (KSTRING $ptascii("declared")) (INDIRECT n_copy $ptascii("declared")),ENTRY (KSTRING $ptascii("beta")) (DIRECT (PINT 9)),ENTRY (KSTRING $ptascii("gamma")) (DIRECT (PINT 23))]',
                            '$objectprops_record_at(S_iterated.OBJECTPROPS,n_copy) = (pobjectprops_iterated)',
                            '$property_slot_at(pobjectprops_iterated.SLOTS,$ptascii("alpha")) = (ppropertyslot_unset)',
                            r'ppropertyslot_unset.DECL = eps /\ ppropertyslot_unset.STATE = PROP_UNSET',
                            '$property_slot_at(pobjectprops_iterated.SLOTS,$ptascii("declared")) = (ppropertyslot_iterated_declared)',
                            'ppropertyslot_iterated_declared.STATE = PROP_VALUE (DIRECT (PINT 2))',
                            '$objectprops_record_at(S_iterated.OBJECTPROPS,n_source) = (pobjectprops_iterated_source)',
                            '$property_slot_at(pobjectprops_iterated_source.SLOTS,$ptascii("declared")) = (ppropertyslot_declared)',
                            '$mc_guard(S_iterated)', 'S_end = S_iterated']
            elif name == 'singleton':
                reached += SINGLETON
            elif name == 'held':
                reached += HELD
            else:
                reached += PAYLOAD
            reached += FINISH + [f'z_clone = {case["clone_line"]}']
            if name in ('singleton','held'):
                reached += ['~(HCELL n_cell <- S_final.ALLOCATIONS)']
            if name == 'payload':
                reached += ['~(HOBJECT n_payload <- S_final.ALLOCATIONS)']
            derived = DERIVED if name == 'scalar' else []
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
            report['passed'] = (report['passed'] and len(report['records']) == 2 * len(selected)
                and all(row['passed'] for row in report['records'])
                and report['application_invocations'] == len(selected)
                and report['application_evaluations'] == len(selected))
        report['passed'] = report['passed'] and all(report[key] for key in ('inputs_stable', 'fixtures_stable', 'head_stable', 'status_stable'))
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({key: report[key] for key in ('passed', 'application_evaluations', 'premises', 'reached_premises', 'derived_premises', 'inputs_stable', 'head_stable', 'status_stable')}), flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
