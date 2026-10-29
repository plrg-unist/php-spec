"""Provisional reached-state probes for dynamic-only cached clone."""
import base64
import argparse
import hashlib
import json
import os
import tempfile
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / 'tests/semantics'))
from recorded_worker import Worker
import error_handler_run as recorder

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
profile = json.loads((root / 'tests/semantics/profile.json').read_text())
flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
modules = [root / p for p in json.loads((root / 'spec/semantics/modules.json').read_text())]

prefix = r'''
syntax p141stage = DCLONE | DCLONE_ANY | DOUTPUT ptbytes
dec $d141_output(pevent*) : ptbytes
def $d141_output(eps) = eps
def $d141_output((OUTPUT ptbytes) :: pevent_tail*) = ptbytes ++ $d141_output(pevent_tail*)
dec $d141_stage(pstate,p141stage) : bool
def $d141_stage(S,DCLONE_ANY) = true
  -- if S.TODO = (CLONE_RESULT porigin z) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if $lookup(S.ENV,$ptascii("source")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (POBJECT n_source)
def $d141_stage(S,DCLONE) = true
  -- if $d141_stage(S,DCLONE_ANY)
  -- if $lookup(S.ENV,$ptascii("source")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (POBJECT n_source)
  -- if $clone_dynamic_share_ready(S,n_source)
def $d141_stage(S,DOUTPUT ptbytes) = ($d141_output(S.EVENTS) = ptbytes)
def $d141_stage(S,p141stage) = false -- otherwise
dec $d141_seek(pstate,p141stage,nat) : pstate
def $d141_seek(S,p141stage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $d141_stage(S,p141stage) \/ n = 0
def $d141_seek(S,p141stage,n) = $d141_seek($drive_steps(S[.COMPLETION = NORMAL],1),p141stage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$d141_stage(S,p141stage) /\ $(n > 0)
def $d141_seek(S,p141stage,n) = S -- otherwise
dec $d141_after(pstate,pstate) : pstate
def $d141_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $d141_guard(pstate) : bool
def $d141_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $object_tables_valid(S) /\ $gc_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''

live = r'''
S_front_found = $d141_seek(S_initial,DCLONE,3000)
S_front_found.COMPLETION = NORMAL \/ S_front_found.COMPLETION = BUDGET
S_front = S_front_found[.COMPLETION = NORMAL]
$d141_stage(S_front,DCLONE)
S_front.TODO = (CLONE_RESULT porigin_clone z_clone) :: ptask_tail*
S_front.ORIGIN = (porigin_clone)
$clone_task_valid(S_front,porigin_clone,z_clone)
$lookup(S_front.ENV,$ptascii("source")) = (n_source_cell)
S_front.STORE[n_source_cell] = DEFINED (POBJECT n_source)
S_front.OBJECTS[n_source] = INSTANCE porigin_class
$class_at(S_front.CLASSES,porigin_class) = (pclassdesc)
pclassdesc.PARENT = eps /\ $trait_plan(S_front,pclassdesc).TRAITS = eps
$class_dynamic_attribute(S_front,porigin_class)
$property_layout(S_front,porigin_class,|S_front.CLASSES|) = eps
$clone_method(S_front,n_source) = eps
$clone_dynamic_share_ready(S_front,n_source)
~$clone_cached_ready(S_front,n_source)
$object_table_ordinary(S_front,n_source)
$object_table_at(S_front.OBJECTTABLES,n_source) = (n_table)
$objectprops_record_at(S_front.OBJECTPROPS,n_source) = (pobjectprops_source)
pobjectprops_source.MATERIALIZED
$property_slot_at(pobjectprops_source.SLOTS,$ptascii("alpha")) = (ppropertyslot_alpha)
ppropertyslot_alpha.DECL = eps
ppropertyslot_alpha.STATE = PROP_VALUE (ALIAS n_alpha_cell)
$property_slot_at(pobjectprops_source.SLOTS,$ptascii("beta")) = (ppropertyslot_beta)
ppropertyslot_beta.DECL = eps /\ ppropertyslot_beta.STATE = PROP_VALUE (DIRECT (PINT 9))
$entry_lookup(S_front.ARRAYS[n_table].ITEMS,KSTRING $ptascii("beta")) = (DIRECT (PINT 9))
$heap_owners($heap_graph(S_front),HARRAY n_table) = 1
$d141_guard(S_front)
PhpStep: S_front ~> S_copy_raw
S_copy = $d141_after(S_front,S_copy_raw)
S_copy.RESULT = KNOWN (POBJECT n_copy)
n_copy = |S_front.OBJECTS|
S_copy.OBJECTS[n_copy] = S_front.OBJECTS[n_source]
S_copy.ARRAYS = S_front.ARRAYS
S_copy.ALLOCATIONS = S_front.ALLOCATIONS ++ [HOBJECT n_copy]
$object_table_at(S_copy.OBJECTTABLES,n_source) = (n_table)
$object_table_at(S_copy.OBJECTTABLES,n_copy) = (n_table)
$objectprops_record_at(S_copy.OBJECTPROPS,n_copy) = (pobjectprops_copy)
pobjectprops_copy.MATERIALIZED /\ pobjectprops_copy.SLOTS = pobjectprops_source.SLOTS
$heap_owners($heap_graph(S_copy),HARRAY n_table) = 2
$d141_guard(S_copy)
S_cow = $object_table_write(S_copy,n_copy)
$object_table_at(S_cow.OBJECTTABLES,n_source) = (n_table)
$object_table_at(S_cow.OBJECTTABLES,n_copy) = (n_cow_table)
n_cow_table = |S_copy.ARRAYS| /\ n_cow_table =/= n_table
$heap_owners($heap_graph(S_cow),HARRAY n_table) = 1
$heap_owners($heap_graph(S_cow),HARRAY n_cow_table) = 1
$d141_guard(S_cow)
S_promoted_found = $d141_seek(S_copy,DOUTPUT $ptascii("D:alpha=7|cloned|beta=9|wrote|"),3000)
S_promoted_found.COMPLETION = NORMAL \/ S_promoted_found.COMPLETION = BUDGET
S_promoted = S_promoted_found[.COMPLETION = NORMAL]
$d141_stage(S_promoted,DOUTPUT $ptascii("D:alpha=7|cloned|beta=9|wrote|"))
$object_table_at(S_promoted.OBJECTTABLES,n_source) = (n_table)
$object_table_at(S_promoted.OBJECTTABLES,n_copy) = (n_table)
$entry_lookup(S_promoted.ARRAYS[n_table].ITEMS,KSTRING $ptascii("beta")) = (ALIAS n_beta_cell)
S_promoted.STORE[n_beta_cell] = DEFINED (PINT 19)
$objectprops_record_at(S_promoted.OBJECTPROPS,n_source) = (pobjectprops_source_after)
$objectprops_record_at(S_promoted.OBJECTPROPS,n_copy) = (pobjectprops_copy_after)
$property_slot_at(pobjectprops_source_after.SLOTS,$ptascii("beta")) = (ppropertyslot_source_after)
$property_slot_at(pobjectprops_copy_after.SLOTS,$ptascii("beta")) = (ppropertyslot_copy_after)
ppropertyslot_source_after.STATE = PROP_VALUE (ALIAS n_beta_cell)
ppropertyslot_copy_after.STATE = PROP_VALUE (ALIAS n_beta_cell)
$heap_owners($heap_graph(S_promoted),HARRAY n_table) = 2
$d141_guard(S_promoted)
'''

observation = r'''
S_observed_found = $d141_seek(S_initial,DOUTPUT $ptascii("before:alpha=7|beta=9|"),3000)
S_observed_found.COMPLETION = NORMAL \/ S_observed_found.COMPLETION = BUDGET
S_observed = S_observed_found[.COMPLETION = NORMAL]
$d141_stage(S_observed,DOUTPUT $ptascii("before:alpha=7|beta=9|"))
$lookup(S_observed.ENV,$ptascii("source")) = (n_source_cell)
S_observed.STORE[n_source_cell] = DEFINED (POBJECT n_source)
S_observed.OBJECTS[n_source] = INSTANCE porigin_class
$property_layout(S_observed,porigin_class,|S_observed.CLASSES|) = eps
$class_dynamic_attribute(S_observed,porigin_class)
$object_table_ordinary(S_observed,n_source)
$object_table_at(S_observed.OBJECTTABLES,n_source) = (n_table)
$object_table_image(S_observed,n_source,n_table)
$object_tables_valid(S_observed)
$entry_lookup(S_observed.ARRAYS[n_table].ITEMS,KSTRING $ptascii("alpha")) = (DIRECT (PINT 7))
$entry_lookup(S_observed.ARRAYS[n_table].ITEMS,KSTRING $ptascii("beta")) = (DIRECT (PINT 9))
$d141_guard(S_observed)
'''

scalar_cow = r'''
S_front_found = $d141_seek(S_initial,DCLONE,3000)
S_front_found.COMPLETION = NORMAL \/ S_front_found.COMPLETION = BUDGET
S_front = S_front_found[.COMPLETION = NORMAL]
$d141_stage(S_front,DCLONE)
S_front.TODO = (CLONE_RESULT porigin_clone z_clone) :: ptask_tail*
$clone_task_valid(S_front,porigin_clone,z_clone)
$lookup(S_front.ENV,$ptascii("source")) = (n_source_cell)
S_front.STORE[n_source_cell] = DEFINED (POBJECT n_source)
$object_table_at(S_front.OBJECTTABLES,n_source) = (n_table)
$clone_method(S_front,n_source) = eps
$d141_guard(S_front)
PhpStep: S_front ~> S_copy_raw
S_copy = $d141_after(S_front,S_copy_raw)
S_copy.RESULT = KNOWN (POBJECT n_copy)
$object_table_at(S_copy.OBJECTTABLES,n_source) = (n_table)
$object_table_at(S_copy.OBJECTTABLES,n_copy) = (n_table)
$heap_owners($heap_graph(S_copy),HARRAY n_table) = 2
$d141_guard(S_copy)
S_written_found = $d141_seek(S_copy,DOUTPUT $ptascii("S:alpha=7|beta=9|C:alpha=7|beta=9|A:7/11|"),3000)
S_written_found.COMPLETION = NORMAL \/ S_written_found.COMPLETION = BUDGET
S_written = S_written_found[.COMPLETION = NORMAL]
$d141_stage(S_written,DOUTPUT $ptascii("S:alpha=7|beta=9|C:alpha=7|beta=9|A:7/11|"))
$object_table_at(S_written.OBJECTTABLES,n_source) = (n_table)
$object_table_at(S_written.OBJECTTABLES,n_copy) = (n_copy_table)
n_copy_table =/= n_table
$entry_lookup(S_written.ARRAYS[n_table].ITEMS,KSTRING $ptascii("alpha")) = (DIRECT (PINT 7))
$entry_lookup(S_written.ARRAYS[n_table].ITEMS,KSTRING $ptascii("beta")) = eps
$entry_lookup(S_written.ARRAYS[n_copy_table].ITEMS,KSTRING $ptascii("alpha")) = (DIRECT (PINT 11))
$entry_lookup(S_written.ARRAYS[n_copy_table].ITEMS,KSTRING $ptascii("beta")) = (DIRECT (PINT 9))
$entry_lookup(S_written.ARRAYS[n_copy_table].ITEMS,KSTRING $ptascii("gamma")) = (DIRECT (PINT 13))
$heap_owners($heap_graph(S_written),HARRAY n_table) = 1
$heap_owners($heap_graph(S_written),HARRAY n_copy_table) = 1
$d141_guard(S_written)
'''

history_share = r'''
S_front_found = $d141_seek(S_initial,DCLONE,3000)
S_front_found.COMPLETION = NORMAL \/ S_front_found.COMPLETION = BUDGET
S_front = S_front_found[.COMPLETION = NORMAL]
$d141_stage(S_front,DCLONE)
S_front.TODO = (CLONE_RESULT porigin_clone z_clone) :: ptask_tail*
$clone_task_valid(S_front,porigin_clone,z_clone)
$lookup(S_front.ENV,$ptascii("source")) = (n_source_cell)
S_front.STORE[n_source_cell] = DEFINED (POBJECT n_source)
S_front.OBJECTS[n_source] = INSTANCE porigin_class
$property_layout(S_front,porigin_class,|S_front.CLASSES|) = eps
$clone_method(S_front,n_source) = eps
$objectprops_record_at(S_front.OBJECTPROPS,n_source) = (pobjectprops_source)
pobjectprops_source.SLOTS = [{DECL eps, NAME $ptascii("alpha"), STATE PROP_UNSET}]
$property_slot_at(pobjectprops_source.SLOTS,$ptascii("alpha")) = eps
$object_table_dynamic_history(pobjectprops_source.SLOTS)
~$clone_mixed_dynamic(pobjectprops_source.SLOTS)
$object_table_at(S_front.OBJECTTABLES,n_source) = (n_table)
S_front.ARRAYS[n_table].ITEMS = eps
$clone_dynamic_share_ready(S_front,n_source)
$d141_guard(S_front)
PhpStep: S_front ~> S_copy_raw
S_copy = $d141_after(S_front,S_copy_raw)
S_copy.RESULT = KNOWN (POBJECT n_copy)
S_copy.ARRAYS = S_front.ARRAYS
S_copy.ALLOCATIONS = S_front.ALLOCATIONS ++ [HOBJECT n_copy]
$object_table_at(S_copy.OBJECTTABLES,n_source) = (n_table)
$object_table_at(S_copy.OBJECTTABLES,n_copy) = (n_table)
$heap_owners($heap_graph(S_copy),HARRAY n_table) = 2
$d141_guard(S_copy)
'''

history_callback = r'''
S_front_found = $d141_seek(S_initial,DCLONE_ANY,3000)
S_front_found.COMPLETION = NORMAL \/ S_front_found.COMPLETION = BUDGET
S_front = S_front_found[.COMPLETION = NORMAL]
$d141_stage(S_front,DCLONE_ANY)
S_front.TODO = (CLONE_RESULT porigin_clone z_clone) :: ptask_tail*
$clone_task_valid(S_front,porigin_clone,z_clone)
$lookup(S_front.ENV,$ptascii("source")) = (n_source_cell)
S_front.STORE[n_source_cell] = DEFINED (POBJECT n_source)
S_front.OBJECTS[n_source] = INSTANCE porigin_class
$property_layout(S_front,porigin_class,|S_front.CLASSES|) = eps
$clone_method(S_front,n_source) = (pmethoddesc_clone)
pmethoddesc_clone.VISIBILITY = PROPERTY_PUBLIC /\ ~pmethoddesc_clone.STATIC
$objectprops_record_at(S_front.OBJECTPROPS,n_source) = (pobjectprops_source)
pobjectprops_source.SLOTS = [{DECL eps, NAME $ptascii("alpha"), STATE PROP_UNSET}]
$property_slot_at(pobjectprops_source.SLOTS,$ptascii("alpha")) = eps
$object_table_dynamic_history(pobjectprops_source.SLOTS)
~$clone_mixed_dynamic(pobjectprops_source.SLOTS)
$object_table_at(S_front.OBJECTTABLES,n_source) = (n_table)
S_front.ARRAYS[n_table].ITEMS = eps
~$clone_dynamic_share_ready(S_front,n_source)
$clone_mixed_ready(S_front,n_source)
$d141_guard(S_front)
PhpStep: S_front ~> S_copy_raw
S_copy = $d141_after(S_front,S_copy_raw)
S_copy.TODO = (CLONE_CALLBACK_ENTER pcloneoperation) :: ptask_tail*
n_copy = pcloneoperation.TARGET
$object_table_at(S_copy.OBJECTTABLES,n_source) = (n_table)
$object_table_at(S_copy.OBJECTTABLES,n_copy) = (n_copy_table)
n_copy_table = |S_front.ARRAYS| /\ n_copy_table =/= n_table
S_copy.ARRAYS[n_copy_table].ITEMS = eps
S_copy.ALLOCATIONS = S_front.ALLOCATIONS ++ [HOBJECT n_copy,HARRAY n_copy_table]
$heap_owners($heap_graph(S_copy),HARRAY n_table) = 1
$heap_owners($heap_graph(S_copy),HARRAY n_copy_table) = 1
$d141_guard(S_copy)
'''

cases = [
    ('live', 'dynamic_only_live_foreach_clone_cases.json', 'dynamic-only-live-foreach-clone', live),
    ('scalar-cow', 'dynamic_only_cached_clone_cases.json', 'dynamic-scalar', scalar_cow),
    ('observation', 'dynamic_only_table_observation_cases.json', 'dynamic-only-cast-foreach', observation),
    ('history-share', 'dynamic_only_empty_history_clone_cases.json', 'empty-history-clone', history_share),
    ('history-callback', 'dynamic_only_empty_history_clone_cases.json', 'empty-history-callback', history_callback),
]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--cpu', type=int)
parser.add_argument('--case', action='append', choices=[case[0] for case in cases])
args = parser.parse_args()
affinity = sorted(os.sched_getaffinity(0))
if args.cpu is not None:
    assert affinity == [args.cpu]
if args.case:
    assert len(args.case) == len(set(args.case))
    cases = [case for case in cases if case[0] in args.case]
recorder.ROOT = root
expectations = root / 'tests/semantics/dynamic_only_cached_clone_expectations.json'
expected = json.loads(expectations.read_text())
assert sha(root / '.tools/php/bin/php') == expected['oracle_sha256']
watched = [Path(__file__).resolve(), expectations, root / 'tests/semantics/profile.json', root / '.tools/php/bin/php',
           root / '.tools/php-file.so', root / '_build/default/adapter/main.exe',
           root / 'tests/semantics/_build/default/numeric_runner.exe', root / '.tools/spectec/bin/p4spectec',
           root / 'frontend/worker.php', root / 'spec/semantics/modules.json', *modules]
watched += [root / 'tests/semantics' / item['file'] for item in expected['catalogues'].values()]
watched = list(dict.fromkeys(watched))
before = {str(path.relative_to(root)): sha(path) for path in watched}
assert before['spec/semantics/150-clone-runtime.watsup'] == '4944e488aeaff570e92ded6ed27dc361b2259be2b9d268f2184fbcef186cecba'
assert before['spec/semantics/261-object-casts.watsup'] == 'ee046c71bf74c8b0061d34f29adfdb52362e11cfcf7e03502e2aa7ed90fa98f5'
assert before['tests/semantics/profile.json'] == expected['native_profile_sha256']
for item in expected['catalogues'].values():
    assert before['tests/semantics/' + item['file']] == item['sha256']
out = Path(tempfile.mkdtemp(prefix='class141-state-', dir=root / '.tools'))
print(out, flush=True)
report = {'inputs_before': before, 'affinity': affinity, 'cpu': args.cpu, 'fixtures': {}, 'complete': False, 'passed': False}
try:
    for label, catalogue, key, body in cases:
        data = json.loads((root / 'tests/semantics' / catalogue).read_text())
        case = next(c for c in data['cases'] if c['id'] == key)
        source = out / (label + '.php')
        source.write_bytes(case['source'].encode())
        assert sha(source) == case['source_sha256']
        directory = out / label
        directory.mkdir()
        frontend = Worker([str(root / '.tools/php/bin/php'), '-n', *flags, '-d', 'extension=' + str(root / '.tools/php-file.so'), str(root / 'frontend/worker.php')], directory / 'frontend')
        adapter = None
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            adapter = Worker([str(root / '_build/default/adapter/main.exe'), str(root)], directory / 'adapter')
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] and checked['ast'] == parsed['ast']
        finally:
            if adapter:
                adapter.close()
            frontend.close()
        initial = 'S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')\nS_initial.COMPLETION = NORMAL \\/ S_initial.COMPLETION = BUDGET\n'
        conditions = [line for line in (initial + body).strip().splitlines() if line]
        fixture = directory / 'state.watsup'
        fixture.write_text(prefix + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- ' + ('' if line.startswith('PhpStep:') else 'if ') + line + '\n' for line in conditions))
        row = {'fixture_sha256': sha(fixture), 'premises': len(conditions), 'raw_steps': sum(line.startswith('PhpStep:') for line in conditions)}
        report['fixtures'][label] = row
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        for phase, cmd in [('compiler', [str(root / '.tools/spectec/bin/p4spectec'), 'algo', *map(str, modules), str(fixture)]), ('state', [str(root / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(fixture)])]:
            process = recorder.recorded(cmd, directory / phase, 120)
            stdout = (directory / (phase + '.stdout')).read_bytes()
            stderr = (directory / (phase + '.stderr')).read_bytes()
            row[phase] = {'process': process, 'stdout_sha256': sha(directory / (phase + '.stdout')), 'stderr_sha256': sha(directory / (phase + '.stderr')), 'passed': process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stderr == b'' and (b'\ndef $main : bool =\n' in stdout if phase == 'compiler' else stdout == b'true\n')}
            (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
            print(label, phase, 'PASS' if row[phase]['passed'] else 'FAIL',
                  process['exit'], row[phase]['stdout_sha256'], row[phase]['stderr_sha256'], flush=True)
            if not row[phase]['passed']:
                raise RuntimeError(label + ' ' + phase + ' failed')
    report['complete'] = True
    report['passed'] = True
finally:
    report['inputs_after'] = {str(path.relative_to(root)): sha(path) for path in watched}
    report['passed'] = report['passed'] and report['inputs_after'] == before
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
assert report['passed']
