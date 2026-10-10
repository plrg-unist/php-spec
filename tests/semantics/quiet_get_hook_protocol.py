"""Reach authentic quiet hook carriers, boolean results and returned-value disposal."""
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

PREFIX = r'''dec $qh_output(pevent*) : ptbytes
dec $qh_stage(pstate, nat, bool) : bool
def $qh_stage(S, 0, b) = true
  -- if $property_hook_isset_plan(S) = (ppropertyhook)
  -- if S.TODO = (PROPERTY_PREP phpType20 z) :: (ORIGIN_RETURN (ppropertyhook.SITE)) :: (ISSET_RESULT b z) :: ptask*
def $qh_stage(S, 1, b) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $property_hook_context_kind(pcallcontext)
def $qh_stage(S, 2, b) = true
  -- if S.TODO = (PROPERTY_HOOK_ISSET_RESULT ppropertyhook b) :: ptask*
def $qh_stage(S, 3, b) = true
  -- if $qh_stage(S, 0, b)
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprPropertyFetch (NExprVariable (BYTES "dGhpcw==") metadata_receiver) phpType20 metadata)
def $qh_stage(S, 4, b) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
def $qh_stage(S, n, b) = false -- otherwise
dec $qh_seek(pstate, nat, bool, nat) : pstate
def $qh_seek(S, n_stage, b, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $qh_stage(S, n_stage, b) \/ n = 0
def $qh_seek(S, n_stage, b, n) = $qh_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, b, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$qh_stage(S, n_stage, b) /\ $(n > 0)
def $qh_seek(S, n_stage, b, n) = S -- otherwise
dec $qh_after(pstate, pstate) : pstate
def $qh_after(S, S_next) = $gc_transition_owners(S, $destruction_transition_owners(S, $sensitive_trace_freeze($source_exception_transition(S, $throwable_transition(S, S_next)))))
dec $qh_guard(pstate) : bool
def $qh_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
def $qh_output(eps) = eps
def $qh_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $qh_output(pevent*)
dec $qh_slot(pstate, nat, ptbytes) : ppropstate?
def $qh_slot(S, n, ptbytes) = (ppropertyslot_value.STATE)
  -- if $objectprops_at(S.OBJECTPROPS, n) = (ppropertyslot*)
  -- if $property_slot_at(ppropertyslot*, ptbytes) = (ppropertyslot_value)
def $qh_slot(S, n, ptbytes) = eps -- otherwise
'''


def reach(name, previous, stage, mode):
    return [f'{name}_found = $qh_seek({previous},{stage},{mode},1000)',
            fr'{name}_found.COMPLETION = NORMAL \/ {name}_found.COMPLETION = BUDGET',
            f'{name} = {name}_found[.COMPLETION = NORMAL]']


SCALAR = [
    r'$property_hook_isset_plan(S) = (ppropertyhook)',
    r'S.TODO = (PROPERTY_PREP phpType20 z) :: (ORIGIN_RETURN (ppropertyhook.SITE)) :: (ISSET_RESULT false z) :: ptask_tail*',
    r'$property_hook_function(S,ppropertyhook) = (pfunction_hook) /\ S.ORIGIN = (ppropertyhook.SITE) /\ $qh_guard(S)',
    r'$qh_slot(S,ppropertyhook.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT PNULL)) /\ $heap_owners($heap_prune($heap_graph(S)),HOBJECT ppropertyhook.OBJECT) = 1',
    r'PhpStep: S ~> S_call_raw',
    r'S_call_raw.TODO = [(CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook) eps 0 eps (ppropertyhook.SITE) z), PROPERTY_HOOK_ISSET_RESULT ppropertyhook false, ORIGIN_RETURN (ppropertyhook.SITE)] ++ ptask_tail*',
    r'S_call_raw.RESULT = KNOWN PNULL /\ S_call_raw.BASE = BASE_VALUE (KNOWN PNULL) /\ S_call_raw.EVENTS = S.EVENTS /\ S_call_raw.STORE = S.STORE /\ S_call_raw.OBJECTPROPS = S.OBJECTPROPS',
    r'$target_nodes(PROPERTY_HOOK_TARGET ppropertyhook) = [HOBJECT ppropertyhook.OBJECT] /\ $task_nodes(PROPERTY_HOOK_ISSET_RESULT ppropertyhook false) = eps',
    r'S_call = $qh_after(S,S_call_raw)',
    r'$property_hook_pending_call(S_call,ppropertyhook) /\ $call_selected_valid(S_call,PROPERTY_HOOK_TARGET ppropertyhook,(ppropertyhook.SITE)) /\ $qh_guard(S_call)',
    r'$heap_owners($heap_prune($heap_graph(S_call)),HOBJECT ppropertyhook.OBJECT) = 2',
    *reach('S_entered', 'S_call', 1, 'false'),
    r'S_entered.CURRENT = (pcallcontext_hook) /\ S_entered.FRAMES = pframe_caller :: pframe_tail*',
    r'pcallcontext_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook /\ pcallcontext_hook.RECEIVER = (ppropertyhook.OBJECT) /\ pcallcontext_hook.INSTANCE = eps',
    r'pframe_caller.TODO = (PROPERTY_HOOK_ISSET_RESULT ppropertyhook false) :: (ORIGIN_RETURN (ppropertyhook.SITE)) :: ptask_tail*',
    r'$property_hook_context_valid(S_entered,pcallcontext_hook) /\ $call_receiver_roots(pcallcontext_hook) = [HOBJECT ppropertyhook.OBJECT] /\ $heap_owners($heap_prune($heap_graph(S_entered)),HOBJECT ppropertyhook.OBJECT) = 2 /\ $qh_guard(S_entered)',
    *reach('S_result', 'S_entered', 2, 'false'),
    r'S_result.TODO = (PROPERTY_HOOK_ISSET_RESULT ppropertyhook false) :: ptask_result* /\ S_result.RESULT = KNOWN PNULL /\ S_result.CURRENT = eps',
    r'$heap_owners($heap_prune($heap_graph(S_result)),HOBJECT ppropertyhook.OBJECT) = 1 /\ $qh_guard(S_result)',
    r'PhpStep: S_result ~> S_boolean_raw',
    r'S_boolean_raw.RESULT = KNOWN (PBOOL false) /\ S_boolean_raw.BASE = BASE_VALUE (KNOWN PNULL) /\ S_boolean_raw.TODO = ptask_result* /\ S_boolean_raw.EVENTS = S_result.EVENTS',
    *reach('S_empty', '$qh_after(S_result,S_boolean_raw)', 0, 'true'),
    r'$property_hook_isset_plan(S_empty) = (ppropertyhook_empty) /\ ppropertyhook_empty.OBJECT = ppropertyhook.OBJECT /\ $qh_guard(S_empty)',
    *reach('S_empty_result', 'S_empty', 2, 'true'),
    r'S_empty_result.RESULT = KNOWN PNULL /\ $qh_guard(S_empty_result)',
    r'PhpStep: S_empty_result ~> S_empty_boolean',
    r'S_empty_boolean.RESULT = KNOWN (PBOOL true) /\ S_empty_boolean.BASE = BASE_VALUE (KNOWN PNULL)',
    *reach('S_this', '$qh_after(S_empty_result,S_empty_boolean)', 3, 'false'),
    r'$property_hook_isset_plan(S_this) = (ppropertyhook_this) /\ S_this.CURRENT = (pcallcontext_method)',
    r'ppropertyhook_this.OBJECT = ppropertyhook.OBJECT /\ $this_receiver(S_this) = (ppropertyhook.OBJECT) /\ $heap_owners($heap_prune($heap_graph(S_this)),HOBJECT ppropertyhook.OBJECT) = 2 /\ $qh_guard(S_this)',
    r'PhpStep: S_this ~> S_this_call_raw',
    r'S_this_call = $qh_after(S_this,S_this_call_raw)',
    r'$property_hook_pending_call(S_this_call,ppropertyhook_this) /\ $heap_owners($heap_prune($heap_graph(S_this_call)),HOBJECT ppropertyhook.OBJECT) = 3 /\ $qh_guard(S_this_call)',
    *reach('S_this_entered', 'S_this_call', 1, 'false'),
    r'S_this_entered.CURRENT = (pcallcontext_this_hook) /\ S_this_entered.FRAMES = pframe_method :: pframe_method_tail*',
    r'pcallcontext_this_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook_this /\ pframe_method.CONTEXT = (pcallcontext_method) /\ $property_hook_context_valid(S_this_entered,pcallcontext_this_hook) /\ $qh_guard(S_this_entered)',
    *reach('S_this_result', 'S_this_entered', 2, 'false'),
    r'S_this_result.RESULT = KNOWN PNULL /\ S_this_result.CURRENT = (pcallcontext_method) /\ $heap_owners($heap_prune($heap_graph(S_this_result)),HOBJECT ppropertyhook.OBJECT) = 2 /\ $qh_guard(S_this_result)',
    r'PhpStep: S_this_result ~> S_this_boolean',
    r'S_this_boolean.RESULT = KNOWN (PBOOL false) /\ S_this_boolean.BASE = BASE_VALUE (KNOWN PNULL)',
    *reach('S_this_empty', '$qh_after(S_this_result,S_this_boolean)', 3, 'true'),
    r'$property_hook_isset_plan(S_this_empty) = (ppropertyhook_this_empty) /\ $qh_guard(S_this_empty)',
    *reach('S_this_empty_result', 'S_this_empty', 2, 'true'),
    r'S_this_empty_result.RESULT = KNOWN PNULL /\ S_this_empty_result.CURRENT = (pcallcontext_method) /\ $qh_guard(S_this_empty_result)',
    r'PhpStep: S_this_empty_result ~> S_this_empty_boolean',
    r'S_this_empty_boolean.RESULT = KNOWN (PBOOL true) /\ S_this_empty_boolean.BASE = BASE_VALUE (KNOWN PNULL)',
    r'S_done = $drive($qh_after(S_this_empty_result,S_this_empty_boolean),10000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $qh_guard(S_done) /\ $qh_output(S_done.EVENTS) = EXPECTED_OUTPUT',
]

DERIVED = [
    r'S_no_marker = S[.TODO = (PROPERTY_PREP phpType20 z) :: (ISSET_RESULT false z) :: ptask_tail*]',
    r'~$property_hook_isset_pending(S_no_marker) /\ $property_hook_isset_plan(S_no_marker) = eps',
    r'S_wrong_marker = S[.TODO = (PROPERTY_PREP phpType20 z) :: (ORIGIN_RETURN (ppropertyhook.HOOK)) :: (ISSET_RESULT false z) :: ptask_tail*]',
    r'~$property_hook_isset_pending(S_wrong_marker) /\ $property_hook_isset_plan(S_wrong_marker) = eps',
    r'S_wrong_mode = S[.TODO = (PROPERTY_PREP phpType20 z) :: (ORIGIN_RETURN (ppropertyhook.SITE)) :: (ISSET_RESULT true z) :: ptask_tail*]',
    r'~$property_hook_isset_pending(S_wrong_mode) /\ $property_hook_isset_plan(S_wrong_mode) = eps',
    r'$property_hook_isset_plan(S[.TODO = (PROPERTY_PREP phpType20 999) :: (ORIGIN_RETURN (ppropertyhook.SITE)) :: (ISSET_RESULT false 999) :: ptask_tail*]) = eps',
    r'$property_hook_isset_plan(S[.ORIGIN = (ppropertyhook.HOOK)]) = eps /\ $property_hook_isset_plan(S[.SOURCES = eps]) = eps',
    r'~$property_hook_valid(S,ppropertyhook[.PROPERTY = ppropertyhook.HOOK],true) /\ ~$property_hook_valid(S,ppropertyhook[.HOOK = ppropertyhook.PROPERTY],true) /\ ~$property_hook_valid(S,ppropertyhook[.LINE = 999],true)',
    r'$property_hook_isset_plan(S[.FUNCTIONS = [pfunction_hook[.NAME = $ptascii("wrong")]]]) = eps /\ $property_hook_isset_plan(S[.FUNCTIONS = [pfunction_hook[.SIGNATURE.BYREF = true]]]) = eps',
    r'~$call_task_valid(S_result,PROPERTY_HOOK_RESULT ppropertyhook) /\ ~$call_task_valid(S_result,PROPERTY_HOOK_ISSET_RESULT ppropertyhook true)',
    r'ppropertyhook.SITE = PORIGIN n pcpath /\ S.SOURCES = pcunit :: pcunit_tail* /\ pcunit.ID = n',
    r'pcpath_parent = pcpath[0:$nabs($( |pcpath| - 2))]',
    r'$origin_node(S.SOURCES,PORIGIN n pcpath_parent) = (NExprIsset (SEQUENCE ([expression_operand])) metadata_parent)',
    r'pcunit_coalesce = pcunit[.OCCURRENCES = [PCOCCURRENCE pcpath_parent (NExprBinaryOpCoalesce expression_operand (NScalarInt (INTEGER 7) metadata_parent) metadata_parent), PCOCCURRENCE pcpath expression_operand]]',
    r'S_coalesce = S[.SOURCES = pcunit_coalesce :: pcunit_tail*]',
    r'~$property_hook_isset_site(S_coalesce,ppropertyhook.SITE,false) /\ ~$property_hook_isset_pending(S_coalesce) /\ $property_hook_isset_plan(S_coalesce) = eps',
]

LIFETIME = [
    r'$property_hook_isset_plan(S) = (ppropertyhook) /\ $qh_slot(S,ppropertyhook.OBJECT,$ptascii("value")) = eps /\ $node_children(S,HOBJECT ppropertyhook.OBJECT) = eps /\ $qh_guard(S)',
    r'$heap_owners($heap_prune($heap_graph(S)),HOBJECT ppropertyhook.OBJECT) = 1',
    r'PhpStep: S ~> S_call_raw',
    r'S_call = $qh_after(S,S_call_raw)',
    r'$property_hook_pending_call(S_call,ppropertyhook) /\ $heap_owners($heap_prune($heap_graph(S_call)),HOBJECT ppropertyhook.OBJECT) = 2 /\ $qh_guard(S_call)',
    *reach('S_entered', 'S_call', 1, 'false'),
    r'S_entered.CURRENT = (pcallcontext_hook) /\ pcallcontext_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook /\ $property_hook_context_valid(S_entered,pcallcontext_hook) /\ $qh_guard(S_entered)',
    *reach('S_result', 'S_entered', 2, 'false'),
    r'S_result.TODO = (PROPERTY_HOOK_ISSET_RESULT ppropertyhook false) :: ptask_result* /\ S_result.RESULT = KNOWN (POBJECT n_leaf) /\ S_result.CURRENT = eps /\ S_result.FRAMES = eps',
    r'$lookup(S_result.ENV,$ptascii("weak")) = (n_weak_cell) /\ S_result.STORE[n_weak_cell] = DEFINED (POBJECT n_weak) /\ $weakref_get(S_result,n_weak) = POBJECT n_leaf',
    r'$heap_owners($heap_prune($heap_graph(S_result)),HOBJECT ppropertyhook.OBJECT) = 1 /\ $heap_owners($heap_prune($heap_graph(S_result)),HOBJECT n_leaf) = 1 /\ $node_children(S_result,HOBJECT ppropertyhook.OBJECT) = eps /\ $task_nodes(PROPERTY_HOOK_ISSET_RESULT ppropertyhook false) = eps /\ $qh_guard(S_result)',
    r'$qh_output(S_result.EVENTS) = $ptascii("G|")',
    r'PhpStep: S_result ~> S_boolean_raw',
    r'S_boolean_raw.RESULT = KNOWN (PBOOL true) /\ S_boolean_raw.BASE = BASE_VALUE (KNOWN PNULL) /\ S_boolean_raw.TODO = ptask_result* /\ S_boolean_raw.EVENTS = S_result.EVENTS',
    r'$heap_owners($heap_prune($heap_graph(S_boolean_raw)),HOBJECT n_leaf) = 0 /\ $heap_owners($heap_prune($heap_graph(S_boolean_raw)),HOBJECT ppropertyhook.OBJECT) = 1',
    r'S_release = $qh_after(S_result,S_boolean_raw)',
    r'S_release.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail* /\ pdestructionoperation.VALUE = KNOWN (PBOOL true) /\ pdestructionoperation.SOURCE = PROPERTY_HOOK_ISSET_RESULT ppropertyhook false /\ $qh_guard(S_release)',
    *reach('S_disposed', 'S_release', 4, 'false'),
    r'S_disposed.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_disposed* /\ $weakref_get(S_disposed,n_weak) = PNULL /\ ~((HOBJECT n_leaf) <- S_disposed.ALLOCATIONS)',
    r'$qh_output(S_disposed.EVENTS) = $ptascii("G|D|") /\ (HOBJECT ppropertyhook.OBJECT) <- S_disposed.ALLOCATIONS /\ $heap_owners($heap_prune($heap_graph(S_disposed)),HOBJECT ppropertyhook.OBJECT) = 1 /\ $qh_guard(S_disposed)',
    r'PhpStep: S_disposed ~> S_restore_raw',
    r'S_restore_raw.RESULT = KNOWN (PBOOL true) /\ S_restore_raw.TODO = ptask_disposed* /\ S_restore_raw.BASE = BASE_VALUE (KNOWN PNULL)',
    *reach('S_empty', '$qh_after(S_disposed,S_restore_raw)', 0, 'true'),
    r'$property_hook_isset_plan(S_empty) = (ppropertyhook_empty) /\ ppropertyhook_empty.OBJECT = ppropertyhook.OBJECT /\ $qh_output(S_empty.EVENTS) = $ptascii("G|D|I|N|") /\ $qh_guard(S_empty)',
    *reach('S_empty_result', 'S_empty', 2, 'true'),
    r'S_empty_result.RESULT = KNOWN (POBJECT n_leaf_empty) /\ S_empty_result.CURRENT = eps /\ S_empty_result.FRAMES = eps /\ $weakref_get(S_empty_result,n_weak) = POBJECT n_leaf_empty',
    r'$heap_owners($heap_prune($heap_graph(S_empty_result)),HOBJECT n_leaf_empty) = 1 /\ $heap_owners($heap_prune($heap_graph(S_empty_result)),HOBJECT ppropertyhook.OBJECT) = 1 /\ $task_nodes(PROPERTY_HOOK_ISSET_RESULT ppropertyhook_empty true) = eps /\ $qh_guard(S_empty_result)',
    r'PhpStep: S_empty_result ~> S_empty_boolean_raw',
    r'S_empty_boolean_raw.RESULT = KNOWN (PBOOL false) /\ S_empty_boolean_raw.BASE = BASE_VALUE (KNOWN PNULL) /\ $heap_owners($heap_prune($heap_graph(S_empty_boolean_raw)),HOBJECT n_leaf_empty) = 0',
    r'S_empty_release = $qh_after(S_empty_result,S_empty_boolean_raw)',
    r'S_empty_release.DESTRUCTION.OPERATIONS = pdestructionoperation_empty :: pdestructionoperation_empty_tail* /\ pdestructionoperation_empty.VALUE = KNOWN (PBOOL false) /\ $qh_guard(S_empty_release)',
    *reach('S_empty_disposed', 'S_empty_release', 4, 'true'),
    r'$weakref_get(S_empty_disposed,n_weak) = PNULL /\ ~((HOBJECT n_leaf_empty) <- S_empty_disposed.ALLOCATIONS) /\ $qh_output(S_empty_disposed.EVENTS) = $ptascii("G|D|I|N|G|D|") /\ $qh_guard(S_empty_disposed)',
    r'S_done = $drive(S_empty_disposed,10000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $qh_guard(S_done)',
    r'$weakref_get(S_done,n_weak) = PNULL /\ ~((HOBJECT ppropertyhook.OBJECT) <- S_done.ALLOCATIONS) /\ $qh_output(S_done.EVENTS) = EXPECTED_OUTPUT',
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'quiet_get_hook_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    selections = [('scalar', SCALAR, DERIVED), ('lifetime', LIFETIME, [])]
    sources = [HERE / ('quiet-get-hook-' + row[0] + '.php') for row in selections]
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
    out = Path(tempfile.mkdtemp(prefix='quiet-get-hook-protocol-', dir=ROOT / '.tools'))
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
                     'S_found = $qh_seek(S_initial,0,false,1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            content += '\ndec $qh_' + name + '() : bool\ndef $qh_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                condition = condition.replace('EXPECTED_OUTPUT', byte_expr(base64.b64decode(case['stdout_base64'])))
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $qh_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = ($qh_scalar() /\\ $qh_lifetime())\n'
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
