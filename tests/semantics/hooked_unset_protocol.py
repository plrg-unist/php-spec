"""Reach direct hooked unset errors, backing preservation and real receiver/leaf disposal."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()
byte_expr = lambda value: '[' + ','.join(str(byte) for byte in value) + ']'

PREFIX = r'''dec $hu_output(pevent*) : ptbytes
def $hu_output(eps) = eps
def $hu_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $hu_output(pevent*)
dec $hu_stage(pstate,nat) : bool
def $hu_stage(S,0) = true
  -- if S.TODO = UNSET_ARRAY :: ptask*
  -- if S.BASE = BASE_PROPERTY_PENDING pbase poperand z
def $hu_stage(S,1) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES "Ym94") metadata)) :: ptask*
def $hu_stage(S,2) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*
def $hu_stage(S,3) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
  -- if pdestructionoperation.SOURCE = UNSET (NExprVariable (BYTES "Ym94") metadata)
def $hu_stage(S,n) = false -- otherwise
dec $hu_seek(pstate,nat,nat) : pstate
def $hu_seek(S,n_stage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $hu_stage(S,n_stage) \/ n = 0
def $hu_seek(S,n_stage,n) = $hu_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$hu_stage(S,n_stage) /\ $(n > 0)
def $hu_seek(S,n_stage,n) = $hu_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $hu_seek(S,n_stage,n) = S -- otherwise
dec $hu_after(pstate,pstate) : pstate
def $hu_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $hu_guard(pstate) : bool
def $hu_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $hu_slot(pstate,nat,ptbytes) : ppropstate?
def $hu_slot(S,n,ptbytes) = (ppropertyslot_value.STATE)
  -- if $objectprops_at(S.OBJECTPROPS,n) = (ppropertyslot*)
  -- if $property_slot_at(ppropertyslot*,ptbytes) = (ppropertyslot_value)
def $hu_slot(S,n,ptbytes) = eps -- otherwise
'''


def reach(name,previous,stage):
    return [f'{name}_found = $hu_seek({previous},{stage},1000)',
            fr'{name}_found.COMPLETION = NORMAL \/ {name}_found.COMPLETION = BUDGET',
            f'{name} = {name}_found[.COMPLETION = NORMAL]']


def unset_step(label,line,class_name,receiver,before_output,slot):
    s='S_'+label; n='n_'+label; base='pbase_'+label; op='poperand_'+label
    origin='porigin_'+label; tail='ptask_'+label+'*'; z='z_'+label
    expr_byte=base64.b64encode(receiver.encode()).decode()
    clauses=[
        f'{s}.TODO = UNSET_ARRAY :: {tail}',
        f'{s}.BASE = BASE_PROPERTY_PENDING {base} {op} {z}',
        f'{s}.ORIGIN = ({origin})',
        f'$origin_node({s}.SOURCES,{origin}) = (NExprPropertyFetch (NExprVariable (BYTES "{expr_byte}") metadata_receiver_{label}) (NIdentifier (BYTES "dmFsdWU=") metadata_name_{label}) metadata_property_{label})',
        f'S_resolved_{label} = $property_pending_resolve({s},{base},{op},PPUNSET,{z},$property_current_line({s}))',
        f'S_resolved_{label}.BASE = BASE_PROPERTY (POBJECT {n}) ptbytes_{label}',
        f'S_resolved_{label}.COMPLETION = NORMAL /\\ S_resolved_{label}.STORE = {s}.STORE /\\ S_resolved_{label}.EVENTS = {s}.EVENTS /\\ ptbytes_{label} = $ptascii("value") /\\ $property_current_line({s}) = {line} /\\ $property_hook_declared({s},{n},ptbytes_{label}) /\\ $object_name({s},{n}) = $ptascii("{class_name}") /\\ $hu_guard({s})',
        f'$hu_slot({s},{n},$ptascii("value")) = {slot}',
        f'$hu_output({s}.EVENTS) = $ptascii("{before_output}")',
    ]
    if receiver=='this':
        clauses += [f'{s}.CURRENT = (pcallcontext_{label})',
                    f'$this_receiver({s}) = ({n}) /\\ $base_nodes({s}.BASE) = [HOBJECT {n}] /\\ $heap_owners($heap_prune($heap_graph({s})),HOBJECT {n}) = 3']
    else:
        clauses += [f'{s}.CURRENT = eps /\\ {s}.FRAMES = eps /\\ $base_nodes({s}.BASE) = eps /\\ $heap_owners($heap_prune($heap_graph({s})),HOBJECT {n}) = 1']
    if label=='active':
        clauses += [f'pcallcontext_active.TARGET = PROPERTY_HOOK_TARGET ppropertyhook_active',
                    f'$property_effective_desc({s},{n},$ptascii("value")) = (ppropertydesc_active)',
                    f'$property_hook_context_valid({s},pcallcontext_active) /\\ ppropertyhook_active.OBJECT = {n} /\\ ~$property_hook_read_needed({s},{n},$ptascii("value")) /\\ $property_hook_backing({s},{n},ppropertydesc_active)']
    clauses += [f'PhpStep: {s} ~> {s}_raw',
                f'{s}_raw.COMPLETION = THROWN "Error" ($ptascii("Cannot unset hooked property {class_name}::$value")) {line} /\\ {s}_raw.TODO = {tail} /\\ {s}_raw.BASE = BASE_VALUE (KNOWN PNULL) /\\ {s}_raw.RESULT = KNOWN PNULL',
                f'{s}_raw.OBJECTPROPS = {s}.OBJECTPROPS /\\ {s}_raw.OBJECTTABLES = {s}.OBJECTTABLES /\\ {s}_raw.STORE = {s}.STORE /\\ {s}_raw.OBJECTS = {s}.OBJECTS /\\ {s}_raw.ALLOCATIONS = {s}.ALLOCATIONS /\\ {s}_raw.EVENTS = {s}.EVENTS /\\ {s}_raw.CURRENT = {s}.CURRENT /\\ {s}_raw.FRAMES = {s}.FRAMES /\\ {s}_raw.HELD = {s}.HELD',
                f'$heap_owners($heap_prune($heap_graph({s}_raw)),HOBJECT {n}) = {2 if receiver=="this" else 1}',
                f'{s}_after = $hu_after({s},{s}_raw)',
                f'{s}_after.EVENTS = {s}.EVENTS /\\ $hu_guard({s}_after)']
    return clauses


backed='Cannot unset hooked property HookUnsetBacked34::$value'
virtual='Cannot unset hooked property HookUnsetVirtual34::$value'
cv=f'CV:{backed}:34|7|'
method=cv+f'T:{backed}:13|7|READ:G|'
retired=method+f'A:{backed}:7|7|B|N|'
virtual_cv=retired+f'VCV:{virtual}:44|EMPTY|'
SCALAR=['S_cv = S']+unset_step('cv',34,'HookUnsetBacked34','box','', '(PROP_VALUE (DIRECT (PINT 7)))')
for label,line,klass,receiver,output,slot in [
    ('this',13,'HookUnsetBacked34','this',cv,'(PROP_VALUE (DIRECT (PINT 7)))'),
    ('active',7,'HookUnsetBacked34','this',method,'(PROP_VALUE (DIRECT (PINT 7)))'),
    ('virtual_cv',44,'HookUnsetVirtual34','virtual',retired,'eps'),
    ('virtual_this',24,'HookUnsetVirtual34','this',virtual_cv,'eps'),
]:
    prev='S_cv_after' if label=='this' else 'S_this_after' if label=='active' else 'S_active_after' if label=='virtual_cv' else 'S_virtual_cv_after'
    SCALAR += reach('S_'+label,prev,0)+unset_step(label,line,klass,receiver,output,slot)
SCALAR += ['S_done = $drive(S_virtual_this_after,10000)',
           r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $hu_guard(S_done) /\ $hu_output(S_done.EVENTS) = EXPECTED_OUTPUT']
DERIVED=[
    r'$property_unset_key(S_cv,POBJECT n_cv,$ptascii("value"),0).COMPLETION = UNSUPPORTED "missing source line"',
    r'$property_unset_key(S_cv[.COMPLETION = BUDGET],POBJECT n_cv,$ptascii("value"),34).COMPLETION = BUDGET',
    r'$property_unset_indirect_check(S_virtual_cv,n_virtual_cv,$ptascii("value"),44).COMPLETION = UNSUPPORTED "hooked property unset"',
]

leaf_error='Cannot unset hooked property HookUnsetBox34::$value'
leaf_cv=f'CV:{leaf_error}:19|'
leaf_before_unset=leaf_cv+f'T:{leaf_error}:7|LIVE|'
LIFETIME=['S_leaf_cv = S']+unset_step('leaf_cv',19,'HookUnsetBox34','box','','(PROP_VALUE (DIRECT (POBJECT n_leaf)))')
LIFETIME += [
    r'$lookup(S_leaf_cv.ENV,$ptascii("weakLeaf")) = (n_weak_leaf_cell)',
    r'S_leaf_cv.STORE[n_weak_leaf_cell] = DEFINED (POBJECT n_weak_leaf)',
    r'$lookup(S_leaf_cv.ENV,$ptascii("weakBox")) = (n_weak_box_cell)',
    r'S_leaf_cv.STORE[n_weak_box_cell] = DEFINED (POBJECT n_weak_box)',
    r'$weakref_get(S_leaf_cv,n_weak_leaf) = POBJECT n_leaf /\ $weakref_get(S_leaf_cv,n_weak_box) = POBJECT n_leaf_cv /\ $heap_owners($heap_prune($heap_graph(S_leaf_cv)),HOBJECT n_leaf) = 1 /\ $heap_owners($heap_prune($heap_graph(S_leaf_cv_raw)),HOBJECT n_leaf) = 1 /\ $heap_owners($heap_prune($heap_graph(S_leaf_cv_after)),HOBJECT n_leaf) = 1',
    *reach('S_leaf_this','S_leaf_cv_after',0),
    *unset_step('leaf_this',7,'HookUnsetBox34','this',leaf_cv,'(PROP_VALUE (DIRECT (POBJECT n_leaf)))'),
    r'n_leaf_this = n_leaf_cv /\ $weakref_get(S_leaf_this,n_weak_leaf) = POBJECT n_leaf /\ $heap_owners($heap_prune($heap_graph(S_leaf_this)),HOBJECT n_leaf) = 1 /\ $heap_owners($heap_prune($heap_graph(S_leaf_this_raw)),HOBJECT n_leaf) = 1 /\ $heap_owners($heap_prune($heap_graph(S_leaf_this_after)),HOBJECT n_leaf) = 1',
    *reach('S_box_unset','S_leaf_this_after',1),
    r'$hu_output(S_box_unset.EVENTS) = $ptascii("'+leaf_before_unset+r'") /\ $hu_slot(S_box_unset,n_leaf_cv,$ptascii("value")) = (PROP_VALUE (DIRECT (POBJECT n_leaf))) /\ $weakref_get(S_box_unset,n_weak_leaf) = POBJECT n_leaf /\ $weakref_get(S_box_unset,n_weak_box) = POBJECT n_leaf_cv /\ $heap_owners($heap_prune($heap_graph(S_box_unset)),HOBJECT n_leaf) = 1 /\ $hu_guard(S_box_unset)',
    r'PhpStep: S_box_unset ~> S_box_raw',
    r'$lookup(S_box_raw.ENV,$ptascii("box")) = eps /\ $heap_owners($heap_prune($heap_graph(S_box_raw)),HOBJECT n_leaf_cv) = 0 /\ S_box_raw.EVENTS = S_box_unset.EVENTS /\ S_box_raw.OBJECTPROPS = S_box_unset.OBJECTPROPS',
    r'S_box_after = $hu_after(S_box_unset,S_box_raw)',
    *reach('S_freeing','S_box_after',2),
    r'S_freeing.TODO = (INSTANCE_STORAGE_STEP pinstancestorage_box) :: ptask_freeing*',
    r'pinstancestorage_box.OBJECT = n_leaf_cv /\ pinstancestorage_box.NEXT = 0 /\ $instance_storage_valid(S_freeing,pinstancestorage_box) /\ $instance_storage_freeing(S_freeing,n_leaf_cv) /\ $hu_slot(S_freeing,n_leaf_cv,$ptascii("value")) = (PROP_VALUE (DIRECT (POBJECT n_leaf))) /\ $heap_owners($heap_prune($heap_graph(S_freeing)),HOBJECT n_leaf) = 1 /\ $weakref_get(S_freeing,n_weak_leaf) = POBJECT n_leaf /\ $weakref_get(S_freeing,n_weak_box) = PNULL /\ $hu_output(S_freeing.EVENTS) = $ptascii("'+leaf_before_unset+r'B|") /\ $hu_guard(S_freeing)',
    r'PhpStep: S_freeing ~> S_slot_raw',
    r'S_slot_raw.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_leaf) :: (INSTANCE_STORAGE_STEP pinstancestorage_next) :: ptask_freeing*',
    r'pinstancestorage_next = pinstancestorage_box[.NEXT = 1] /\ pdestructionrelease_leaf.JOBS = [DESTRUCTION_VALUE (HOBJECT n_leaf)] /\ $hu_slot(S_slot_raw,n_leaf_cv,$ptascii("value")) = (PROP_UNSET) /\ $heap_owners($heap_prune($heap_graph(S_slot_raw)),HOBJECT n_leaf) = 1 /\ S_slot_raw.EVENTS = S_freeing.EVENTS',
    r'S_slot_after = $hu_after(S_freeing,S_slot_raw)',
    *reach('S_disposed','S_slot_after',3),
    r'S_disposed.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_box) :: ptask_disposed*',
    r'pdestructionoperation_box.SOURCE = UNSET (NExprVariable (BYTES "Ym94") metadata_box)',
    r'~((HOBJECT n_leaf) <- S_disposed.ALLOCATIONS) /\ ~((HOBJECT n_leaf_cv) <- S_disposed.ALLOCATIONS) /\ $weakref_get(S_disposed,n_weak_leaf) = PNULL /\ $weakref_get(S_disposed,n_weak_box) = PNULL /\ $hu_output(S_disposed.EVENTS) = $ptascii("'+leaf_before_unset+r'B|D|") /\ $hu_guard(S_disposed)',
    r'S_done = $drive(S_disposed,10000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $weakref_get(S_done,n_weak_leaf) = PNULL /\ $weakref_get(S_done,n_weak_box) = PNULL /\ $hu_guard(S_done) /\ $hu_output(S_done.EVENTS) = EXPECTED_OUTPUT',
]
LIFETIME_DERIVED=[
    r'$property_unset_key(S_freeing,POBJECT n_leaf_cv,$ptascii("value"),19).COMPLETION = UNSUPPORTED "freeing instance property access"',
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'hooked_unset_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    selections = [('scalar', SCALAR, DERIVED), ('lifetime', LIFETIME, LIFETIME_DERIVED)]
    sources = [HERE / ('hooked-unset-' + row[0] + '.php') for row in selections]
    php, adapter, bridge, worker, runner, compiler = (ROOT / name for name in [
        '.tools/php/bin/php', '_build/default/adapter/main.exe', '.tools/php-file.so',
        'frontend/worker.php', 'tests/semantics/_build/default/numeric_runner.exe', '.tools/spectec/bin/p4spectec'])
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    assert sha(compiler) == '26d77fb9bfae2b2868e137a94051f55f9b607660c340e9b22ae8300fb0d8ce88'
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_bytes())]
    watched = [Path(__file__), Path(recorder.__file__), catalogue, *sources, profile_file, php,
               adapter, bridge, worker, runner, compiler, manifest, *modules, ROOT / 'spec/schema.json',
               ROOT / 'spec/php.watsup', ROOT / 'spec/nodes.json', ROOT / 'frontend/target.php',
               ROOT / 'frontend/wire.php', ROOT / 'frontend/wire.py',
               HERE / 'recorded_worker.py', HERE / 'static_types.py']
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    assert revision == args.revision and not status, (revision, status)
    before = {str(path): sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='hooked-unset-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    derived = sum(len(row[2]) for row in selections)
    reached = sum(5 + len(row[1]) for row in selections)
    report = {'revision': revision, 'inputs': before, 'profile': profile, 'module_count': len(modules),
              'mode': 'SL', 'cache': False, 'det': True, 'records': [],
              'application_invocations': 0, 'application_evaluations': 0, 'source_agreements': 0,
              'derived_premises': derived, 'reached_premises': reached, 'premises': derived + reached,
              'cap_seconds': 90, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'jobs': 1}, 'passed': False}
    fixture = None
    try:
        flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
        fixtures = []
        for i, (source, case) in enumerate(zip(sources, data['cases'])):
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256']
            frontend = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(bridge), str(worker)], out / ('frontend-' + str(i)))
            adapter_worker = None
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted'], parsed
                adapter_worker = Worker([str(adapter), str(ROOT)], out / ('adapter-' + str(i)))
                checked = adapter_worker.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                assert checked['ok'] and checked['ast'] == parsed['ast']
                fixtures.append(checked['fixture'])
            finally:
                if adapter_worker:
                    adapter_worker.close()
                frontend.close()
        content = PREFIX
        for selection, ast_fixture, source, case in zip(selections, fixtures, sources, data['cases']):
            name, clauses, negatives = selection
            setup = ['S_initial = $php_run(' + ast_fixture + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $hu_seek(S_initial,0,1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            content += '\ndec $hu_' + name + '() : bool\ndef $hu_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                condition = condition.replace('EXPECTED_OUTPUT', byte_expr(base64.b64decode(case['stdout_base64'])))
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $hu_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = ($hu_scalar() /\\ $hu_lifetime())\n'
        fixture = out / 'hook.watsup'
        fixture.write_text(content)
        report.update(fixture=str(fixture), fixture_sha256=sha(fixture), prepared=True, passed=True)
        if not args.prepare_only:
            process = recorder.recorded([str(compiler), 'algo', *map(str, modules), str(fixture)], out / 'compiler', 90)
            passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and not (out / 'compiler.stderr').read_bytes() and b'\ndef $main : bool =\n' in (out / 'compiler.stdout').read_bytes()
            report['records'].append({'id': 'algorithmic-compilation', 'process': process, 'passed': passed, 'application_evaluations': 0})
            report['passed'] = passed
            assert passed
            report['application_invocations'] = 1
            process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'state', 90)
            output = (out / 'state.stdout').read_bytes()
            evaluated = process['exit'] == 0 and output in (b'true\n', b'false\n')
            report['application_evaluations'] = int(evaluated)
            passed = evaluated and not process['timeout'] and not process['group_after'] and not (out / 'state.stderr').read_bytes() and output == b'true\n'
            report['records'].append({'id': 'strict-SL-application', 'process': process, 'passed': passed})
            report['passed'] = passed
    finally:
        report.update(inputs_stable=before == {str(path): sha(path) for path in watched},
                      fixture_stable=fixture is None or report['fixture_sha256'] == sha(fixture),
                      head_stable=revision == git('rev-parse', 'HEAD'), status_stable=status == git('status', '--short'))
        report['passed'] = report['passed'] and all(report[key] for key in ('inputs_stable', 'fixture_stable', 'head_stable', 'status_stable'))
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({key: report[key] for key in ('passed', 'application_evaluations', 'derived_premises', 'reached_premises', 'inputs_stable', 'head_stable', 'status_stable')}), flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
