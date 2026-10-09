"""Check virtual-get storage omission, pending writes and returned-value ownership."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()
byte_expr = lambda value: '[' + ','.join(str(byte) for byte in value) + ']'

PREFIX = r'''dec $vh_output(pevent*) : ptbytes
dec $vh_stage(pstate, nat) : bool
def $vh_stage(S, 0) = ($property_hook_plan(S) =/= eps)
def $vh_stage(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $property_hook_context_kind(pcallcontext)
  -- if S.TODO = (RETURN_VALUE z) :: ptask*
def $vh_stage(S, 2) = true
  -- if S.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*
def $vh_stage(S, 3) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES "cmVzdWx0") metadata)) :: ptask*
def $vh_stage(S, 4) = true
  -- if S.TODO = (ASSIGN_ARRAY (BASE_PROPERTY_PENDING pbase (KNOWN (PSTRING ptbytes)) z_receiver) z b) :: ptask*
  -- if ptbytes = $ptascii("value")
def $vh_stage(S, 5) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES "Ym94") metadata)) :: ptask*
def $vh_stage(S, 8) = true
  -- if S.TODO = (ASSIGN_ARRAY (BASE_PROPERTY_PENDING pbase (KNOWN (PSTRING ptbytes)) z_receiver) z b) :: ptask*
  -- if ptbytes = $ptascii("other")
def $vh_stage(S, n) = false -- otherwise
dec $vh_seek(pstate, nat, nat) : pstate
def $vh_seek(S, n_stage, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $vh_stage(S, n_stage) \/ n = 0
def $vh_seek(S, n_stage, n) = $vh_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$vh_stage(S, n_stage) /\ $(n > 0)
def $vh_seek(S, n_stage, n) = $vh_seek($drive_steps(S, 1), n_stage, $nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $vh_seek(S, n_stage, n) = S -- otherwise
dec $vh_after(pstate, pstate) : pstate
def $vh_after(S, S_next) = $gc_transition_owners(S, $destruction_transition_owners(S, $sensitive_trace_freeze($source_exception_transition(S, $throwable_transition(S, S_next)))))
dec $vh_guard(pstate) : bool
def $vh_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
def $vh_output(eps) = eps
def $vh_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $vh_output(pevent*)
'''

SCALAR = [
    r'$property_hook_plan(S) = (ppropertyhook)',
    r'$property_effective_desc(S,ppropertyhook.OBJECT,$ptascii("value")) = (ppropertydesc)',
    r'$property_hook_function(S,ppropertyhook) = (pfunction_hook)',
    r'$property_hook_virtual(S,ppropertydesc) /\ pfunction_hook.SIGNATURE = {PARAMETERS eps,RETURNS ppropertydesc.TYPE,BYREF false}',
    r'S.OBJECTS[ppropertyhook.OBJECT] = INSTANCE porigin_class',
    r'$class_at(S.CLASSES,porigin_class) = (pclassdesc)',
    r'$objectprops_at(S.OBJECTPROPS,ppropertyhook.OBJECT) = (eps) /\ $property_initial_slots(S,porigin_class,pclassdesc.PROPERTIES) = (eps) /\ $vh_guard(S)',
    r'S.TODO = (PROPERTY_PREP phpType20 z) :: (DIM_FETCH z) :: ptask_read*',
    r'PhpStep: S ~> S_call_raw',
    r'S_call_raw.TODO = [(CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook) eps 0 eps (ppropertyhook.SITE) ppropertyhook.LINE),PROPERTY_HOOK_RESULT ppropertyhook] ++ ptask_read*',
    r'S_call = $vh_after(S,S_call_raw)',
    r'$heap_owners($heap_prune($heap_graph(S_call)),HOBJECT ppropertyhook.OBJECT) = 2 /\ $vh_guard(S_call)',
    r'S_return_found = $vh_seek(S_call,1,1000)',
    r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
    r'S_return = S_return_found[.COMPLETION = NORMAL]',
    r'S_return.CURRENT = (pcallcontext_hook)',
    r'pcallcontext_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook /\ S_return.RESULT = KNOWN (PINT 7)',
    r'~$property_hook_backing(S_return,ppropertyhook.OBJECT,ppropertydesc) /\ $vh_guard(S_return)',
    r'S_write_found = $vh_seek(S_return,4,1000)',
    r'S_write_found.COMPLETION = NORMAL \/ S_write_found.COMPLETION = BUDGET',
    r'S_write = S_write_found[.COMPLETION = NORMAL]',
    r'S_write.TODO = (ASSIGN_ARRAY (BASE_PROPERTY_PENDING pbase_receiver (KNOWN (PSTRING ptbytes_key)) z_receiver) z_write false) :: ptask_write*',
    r'S_receiver = $property_receiver_fetch(S_write,pbase_receiver,PPW,z_receiver)',
    r'S_receiver.RESULT = KNOWN (POBJECT n_receiver)',
    r'S_receiver.COMPLETION = NORMAL /\ n_receiver = ppropertyhook.OBJECT /\ ptbytes_key = $ptascii("value") /\ S_write.RESULT = KNOWN (PINT 23)',
    r'$vh_output(S_write.EVENTS) = $ptascii("G|7|G|7|W|R23|") /\ $objectprops_at(S_write.OBJECTPROPS,n_receiver) = (eps) /\ $vh_guard(S_write)',
    r'PhpStep: S_write ~> S_error_raw',
    r'S_error_raw.COMPLETION = THROWN "Error" ($ptascii("Property VirtualGetter30::$value is read-only")) z_write',
    r'$objectprops_at(S_error_raw.OBJECTPROPS,n_receiver) = (eps) /\ S_error_raw.STORE = S_write.STORE /\ S_error_raw.EVENTS = S_write.EVENTS',
    r'S_done = $drive($vh_after(S_write,S_error_raw),1000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $vh_guard(S_done)',
    r'$vh_output(S_done.EVENTS) = EXPECTED_OUTPUT',
]

DERIVED = [
    r'~$property_hook_virtual(S,ppropertydesc[.NAME = $ptascii("wrong")]) /\ ~$property_hook_virtual(S,ppropertydesc[.KEY = $ptascii("wrong")])',
    r'~$property_hook_virtual(S,ppropertydesc[.TYPE = eps]) /\ ~$property_hook_virtual(S,ppropertydesc[.DEFAULT = PROP_NULL])',
    r'~$property_hook_virtual(S,ppropertydesc[.ORIGIN = INTERNAL_PROPERTY "stdClass" $ptascii("value")])',
    r'~$property_hook_virtual(S[.SOURCES = eps],ppropertydesc) /\ ~$property_hook_virtual(S[.CLASSES = eps],ppropertydesc)',
    r'S_ghost = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,ppropertyhook.OBJECT,[{DECL (ppropertydesc.ORIGIN),NAME $ptascii("value"),STATE PROP_VALUE (DIRECT (PINT 7))}])]',
    r'~$property_state_valid(S_ghost)',
    r'S_shadow = $objectprops_mark(S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,ppropertyhook.OBJECT,[{DECL eps,NAME $ptascii("value"),STATE PROP_VALUE (DIRECT (PINT 7))}])],ppropertyhook.OBJECT)',
    r'~$property_dynamic_no_shadow(S_shadow,porigin_class,[{DECL eps,NAME $ptascii("value"),STATE PROP_VALUE (DIRECT (PINT 7))}]) /\ ~$property_state_valid(S_shadow)',
    r'$property_hook_instance(S,ppropertyhook.OBJECT)',
    r'S_iter_reset = $object_foreach_reset(S,ppropertyhook.OBJECT)',
    r'S_iter_reset.COMPLETION = UNSUPPORTED "property hook iteration" /\ S_iter_reset.OBJECTPROPS = S.OBJECTPROPS /\ S_iter_reset.EVENTS = S.EVENTS',
    r'S_iter_select = $object_foreach_select(S,ppropertyhook.OBJECT)',
    r'S_iter_select.COMPLETION = UNSUPPORTED "property hook iteration" /\ S_iter_select.OBJECTPROPS = S.OBJECTPROPS /\ S_iter_select.EVENTS = S.EVENTS',
]

HEAP = [
    r'$property_hook_plan(S) = (ppropertyhook)',
    r'$property_effective_desc(S,ppropertyhook.OBJECT,$ptascii("value")) = (ppropertydesc)',
    r'$property_hook_virtual(S,ppropertydesc) /\ $objectprops_at(S.OBJECTPROPS,ppropertyhook.OBJECT) = (eps) /\ $vh_guard(S)',
    r'S_return_found = $vh_seek(S,1,1000)',
    r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
    r'S_return = S_return_found[.COMPLETION = NORMAL]',
    r'S_return.CURRENT = (pcallcontext_hook)',
    r'pcallcontext_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook',
    r'S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*',
    r'S_return.RESULT = KNOWN (POBJECT n_leaf)',
    r'$typed_return_task_valid(S_return,z_return)',
    r'~((HOBJECT n_leaf) <- $node_children(S_return,HOBJECT ppropertyhook.OBJECT)) /\ ~$property_hook_backing(S_return,ppropertyhook.OBJECT,ppropertydesc)',
    r'$heap_owners($heap_prune($heap_graph(S_return)),HOBJECT n_leaf) = 1 /\ $heap_owners($heap_prune($heap_graph(S_return)),HOBJECT ppropertyhook.OBJECT) = 2 /\ $vh_output(S_return.EVENTS) = $ptascii("G|") /\ $vh_guard(S_return)',
    r'PhpStep: S_return ~> S_unwind_raw',
    r'S_unwind_raw.TODO = [RETURN_UNWIND (KNOWN (POBJECT n_leaf)) (ppropertyhook.HOOK)] /\ S_unwind_raw.RESULT = KNOWN PNULL /\ S_unwind_raw.COMPLETION = NORMAL',
    r'S_result_found = $vh_seek($vh_after(S_return,S_unwind_raw),2,1000)',
    r'S_result_found.COMPLETION = NORMAL \/ S_result_found.COMPLETION = BUDGET',
    r'S_result = S_result_found[.COMPLETION = NORMAL]',
    r'S_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask_result*',
    r'S_result.RESULT = KNOWN (POBJECT n_leaf) /\ S_result.CURRENT = eps /\ $objectprops_at(S_result.OBJECTPROPS,ppropertyhook.OBJECT) = (eps)',
    r'$heap_owners($heap_prune($heap_graph(S_result)),HOBJECT n_leaf) = 1 /\ $heap_owners($heap_prune($heap_graph(S_result)),HOBJECT ppropertyhook.OBJECT) = 1 /\ $vh_guard(S_result)',
    r'PhpStep: S_result ~> S_result_raw',
    r'S_result_raw.RESULT = S_result.RESULT /\ S_result_raw.BASE = BASE_VALUE S_result.RESULT /\ S_result_raw.TODO = ptask_result*',
    r'S_first_found = $vh_seek($vh_after(S_result,S_result_raw),3,1000)',
    r'S_first_found.COMPLETION = NORMAL \/ S_first_found.COMPLETION = BUDGET',
    r'S_first = S_first_found[.COMPLETION = NORMAL]',
    r'$lookup(S_first.ENV,$ptascii("result")) = (n_result_cell)',
    r'S_first.STORE[n_result_cell] = DEFINED (POBJECT n_leaf)',
    r'$lookup(S_first.ENV,$ptascii("weak")) = (n_weak_cell)',
    r'S_first.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
    r'$lookup(S_first.ENV,$ptascii("box")) = (n_box_cell)',
    r'S_first.STORE[n_box_cell] = DEFINED (POBJECT ppropertyhook.OBJECT)',
    r'$weakref_get(S_first,n_weak) = POBJECT n_leaf /\ $heap_owners($heap_prune($heap_graph(S_first)),HOBJECT n_leaf) = 1 /\ $vh_output(S_first.EVENTS) = $ptascii("G|L|") /\ $vh_guard(S_first)',
    r'PhpStep: S_first ~> S_first_raw',
    r'S_box_found = $vh_seek($vh_after(S_first,S_first_raw),5,1000)',
    r'S_box_found.COMPLETION = NORMAL \/ S_box_found.COMPLETION = BUDGET',
    r'S_box = S_box_found[.COMPLETION = NORMAL]',
    r'$weakref_get(S_box,n_weak) = PNULL /\ ~((HOBJECT n_leaf) <- S_box.ALLOCATIONS) /\ (HOBJECT ppropertyhook.OBJECT) <- S_box.ALLOCATIONS',
    r'S_box.STORE[n_box_cell] = DEFINED (POBJECT ppropertyhook.OBJECT)',
    r'$lookup(S_box.ENV,$ptascii("result")) = (n_result2_cell)',
    r'S_box.STORE[n_result2_cell] = DEFINED (POBJECT n_leaf2)',
    r'$lookup(S_box.ENV,$ptascii("weak2")) = (n_weak2_cell)',
    r'S_box.STORE[n_weak2_cell] = DEFINED (POBJECT n_weak2)',
    r'n_leaf2 =/= n_leaf /\ $weakref_get(S_box,n_weak2) = POBJECT n_leaf2 /\ ~((HOBJECT n_leaf2) <- $node_children(S_box,HOBJECT ppropertyhook.OBJECT))',
    r'$heap_owners($heap_prune($heap_graph(S_box)),HOBJECT n_leaf2) = 1 /\ $vh_output(S_box.EVENTS) = $ptascii("G|L|D|N|G|") /\ $vh_guard(S_box)',
    r'PhpStep: S_box ~> S_box_raw',
    r'S_last_found = $vh_seek($vh_after(S_box,S_box_raw),3,1000)',
    r'S_last_found.COMPLETION = NORMAL \/ S_last_found.COMPLETION = BUDGET',
    r'S_last = S_last_found[.COMPLETION = NORMAL]',
    r'~((HOBJECT ppropertyhook.OBJECT) <- S_last.ALLOCATIONS) /\ $weakref_get(S_last,n_weak2) = POBJECT n_leaf2 /\ S_last.STORE[n_result2_cell] = DEFINED (POBJECT n_leaf2)',
    r'$heap_owners($heap_prune($heap_graph(S_last)),HOBJECT n_leaf2) = 1 /\ $vh_output(S_last.EVENTS) = $ptascii("G|L|D|N|G|B|L|") /\ $vh_guard(S_last)',
    r'PhpStep: S_last ~> S_last_raw',
    r'S_done = $drive($vh_after(S_last,S_last_raw),1000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $vh_guard(S_done)',
    r'$weakref_get(S_done,n_weak2) = PNULL /\ ~((HOBJECT n_leaf2) <- S_done.ALLOCATIONS) /\ $vh_output(S_done.EVENTS) = EXPECTED_OUTPUT',
]

LITERAL = [
    r'S.TODO = (ASSIGN_ARRAY (BASE_PROPERTY_PENDING pbase_receiver (KNOWN (PSTRING ptbytes_key)) z_receiver) z false) :: ptask_tail*',
    r'S_receiver = $property_receiver_fetch(S,pbase_receiver,PPW,z_receiver)',
    r'S_receiver.RESULT = KNOWN (POBJECT n_box)',
    r'S_receiver.COMPLETION = NORMAL /\ ptbytes_key = $ptascii("value") /\ S.RESULT = KNOWN (PINT 7)',
    r'$property_effective_desc(S,n_box,$ptascii("value")) = (ppropertydesc_value)',
    r'$property_effective_desc(S,n_box,$ptascii("other")) = (ppropertydesc_other)',
    r'$property_hook_origin(S,ppropertydesc_value) = (porigin_value)',
    r'$property_hook_origin(S,ppropertydesc_other) = (porigin_other)',
    r'$origin_node(S.SOURCES,porigin_value) = (NPropertyHook phpType14 phpType24 phpType4 phpType11 phpType16 expression_value metadata_value)',
    r'$origin_node(S.SOURCES,porigin_other) = (NPropertyHook phpType14_other phpType24_other phpType4_other phpType11_other phpType16_other expression_other metadata_other)',
    r'$hook_body_backed(expression_value,$ptascii("value")) /\ $hook_body_backed(expression_other,$ptascii("other"))',
    r'~$property_hook_virtual(S,ppropertydesc_value) /\ ~$property_hook_virtual(S,ppropertydesc_other) /\ $vh_guard(S)',
    r'PhpStep: S ~> S_value_raw',
    r'S_value = $vh_after(S,S_value_raw)',
    r'$objectprops_at(S_value.OBJECTPROPS,n_box) = (ppropertyslot*)',
    r'$property_slot_at(ppropertyslot*,$ptascii("value")) = (ppropertyslot_value)',
    r'ppropertyslot_value.STATE = PROP_VALUE (DIRECT (PINT 7)) /\ $vh_guard(S_value)',
    r'S_other_found = $vh_seek(S_value,8,1000)',
    r'S_other_found.COMPLETION = NORMAL \/ S_other_found.COMPLETION = BUDGET',
    r'S_other = S_other_found[.COMPLETION = NORMAL]',
    r'S_other.RESULT = KNOWN (PINT 9)',
    r'PhpStep: S_other ~> S_other_raw',
    r'S_done = $drive($vh_after(S_other,S_other_raw),1000)',
    r'S_done.COMPLETION = NORMAL /\ $vh_output(S_done.EVENTS) = EXPECTED_OUTPUT /\ $vh_guard(S_done)',
]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    profile_file = ROOT / 'tests/semantics/profile.json'
    profile = json.loads(profile_file.read_bytes())
    catalogue = HERE / 'virtual_get_hook_cases.json'
    data = json.loads(catalogue.read_bytes())
    assert data['native_profile'] == profile
    selections = [('scalar', 'repeated-read-denied-write', SCALAR, DERIVED, 0),
                  ('heap', 'result-without-backing-owner', HEAP, [], 0),
                  ('literal', 'literal-backing-slots', LITERAL, [], 4)]
    sources = [HERE / ('virtual-get-hook-' + suffix + '.php') for suffix in ('scalar','lifetime','literal')]
    cases = [next(row for row in data['cases'] if row['id'] == selection[1]) for selection in selections]
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
               ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/static_types.py']
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    assert revision == args.revision and not status
    before = {str(path): sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='virtual-get-hook-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    derived = sum(len(row[3]) for row in selections)
    reached = sum(5 + len(row[2]) for row in selections)
    assert derived == 13 and reached == 126
    report = {'revision': revision, 'inputs': before, 'profile': profile, 'module_count': len(modules),
              'modules': list(map(str,modules)), 'selections': [row[1] for row in selections],
              'mode': 'SL', 'cache': False, 'det': True, 'evaluated': False, 'records': [],
              'application_invocations': 0, 'application_evaluations': 0, 'source_agreements': 0,
              'derived_premises': derived, 'reached_premises': reached, 'premises': derived + reached,
              'budget_seconds': 120, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'jobs': 1}, 'passed': False}
    fixture = None
    try:
        flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
        fixtures = []
        for i, (source, case) in enumerate(zip(sources,cases)):
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256']
            frontend = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(bridge), str(worker)], out / ('frontend-' + str(i)))
            adapter_worker = None
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted']
                adapter_worker = Worker([str(adapter), str(ROOT)], out / ('adapter-' + str(i)))
                checked = adapter_worker.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                assert checked['ok'] and checked['ast'] == parsed['ast']
                fixtures.append(checked['fixture'])
            finally:
                if adapter_worker: adapter_worker.close()
                frontend.close()
        content = PREFIX
        for selection, ast_fixture, source, case in zip(selections, fixtures, sources, cases):
            name, case_id, clauses, negatives, stage = selection
            output = base64.b64decode(case['stdout_base64'])
            setup = ['S_initial = $php_run(' + ast_fixture + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $vh_seek(S_initial,' + str(stage) + ',1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            content += '\ndec $vh_' + name + '() : bool\ndef $vh_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                condition = condition.replace('EXPECTED_OUTPUT', byte_expr(output))
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $vh_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = ($vh_scalar() /\\ $vh_heap() /\\ $vh_literal())\n'
        fixture = out / 'virtual.watsup'
        fixture.write_text(content)
        report.update(fixture=str(fixture), fixture_sha256=sha(fixture), prepared=True, passed=True)
        if not args.prepare_only:
            process = recorder.recorded([str(compiler), 'algo', *map(str, modules), str(fixture)], out / 'compiler', 120)
            main_present = b'\ndef $main : bool =\n' in (out / 'compiler.stdout').read_bytes()
            passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and not (out / 'compiler.stderr').read_bytes() and main_present
            report['records'].append({'id': 'algorithmic-compilation', 'process': process, 'passed': passed, 'main_present': main_present, 'application_evaluations': 0})
            report['passed'] = passed
            assert passed
            report['application_invocations'] = 1
            process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'state', 120)
            output = (out / 'state.stdout').read_bytes()
            report['evaluated'] = process['exit'] == 0 and output in (b'true\n', b'false\n')
            report['application_evaluations'] = int(report['evaluated'])
            passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and not (out / 'state.stderr').read_bytes() and output == b'true\n'
            report['records'].append({'id': 'strict-SL-application', 'process': process, 'passed': passed})
            report['passed'] = passed
    finally:
        report.update(inputs_stable=before == {str(path): sha(path) for path in watched},
                      fixture_stable=fixture is None or report['fixture_sha256'] == sha(fixture),
                      head_stable=revision == git('rev-parse', 'HEAD'), status_stable=status == git('status', '--short'))
        report['passed'] = report['passed'] and all(report[key] for key in ('inputs_stable', 'fixture_stable', 'head_stable', 'status_stable'))
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({key: report[key] for key in ('passed', 'evaluated', 'derived_premises', 'reached_premises', 'inputs_stable', 'head_stable', 'status_stable')}), flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
