"""Check expression-hook implicit returns, saved string conversion and payload release."""
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

PREFIX = r'''dec $eh_output(pevent*) : ptbytes
dec $eh_stage(pstate, nat) : bool
def $eh_stage(S, 0) = ($property_hook_plan(S) =/= eps)
def $eh_stage(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $property_hook_context_kind(pcallcontext)
  -- if S.TODO = (RETURN_VALUE z) :: ptask*
def $eh_stage(S, 2) = true
  -- if S.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*
def $eh_stage(S, 3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $ptlc(pcallcontext.NAME) = $ptascii("hookexpressionstringvalue29::__tostring")
def $eh_stage(S, 5) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES "cmVzdWx0") metadata)) :: ptask*
def $eh_stage(S, n) = false -- otherwise
dec $eh_seek(pstate, nat, nat) : pstate
def $eh_seek(S, n_stage, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $eh_stage(S, n_stage) \/ n = 0
def $eh_seek(S, n_stage, n) = $eh_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$eh_stage(S, n_stage) /\ $(n > 0)
def $eh_seek(S, n_stage, n) = $eh_seek($drive_steps(S, 1), n_stage, $nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $eh_seek(S, n_stage, n) = S -- otherwise
dec $eh_after(pstate, pstate) : pstate
def $eh_after(S, S_next) = $gc_transition_owners(S, $destruction_transition_owners(S, $sensitive_trace_freeze($source_exception_transition(S, $throwable_transition(S, S_next)))))
dec $eh_guard(pstate) : bool
def $eh_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
def $eh_output(eps) = eps
def $eh_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $eh_output(pevent*)
dec $eh_slot(pstate, nat, ptbytes) : ppropstate?
def $eh_slot(S, n, ptbytes) = (ppropertyslot_value.STATE)
  -- if $objectprops_at(S.OBJECTPROPS, n) = (ppropertyslot*)
  -- if $property_slot_at(ppropertyslot*, ptbytes) = (ppropertyslot_value)
def $eh_slot(S, n, ptbytes) = eps -- otherwise
'''

UNTYPED = [
    r'$property_hook_plan(S) = (ppropertyhook)',
    r'$property_hook_function(S,ppropertyhook) = (pfunction_hook)',
    r'$property_effective_desc(S,ppropertyhook.OBJECT,$ptascii("value")) = (ppropertydesc)',
    r'$origin_node(S.SOURCES,PORIGIN pfunction_hook.CODE.UNIT pfunction_hook.BODY) = (expression_body)',
    r'$arrow_line(pfunction_hook.CODE.EXPRESSIONS,pfunction_hook.BODY) = (z_return)',
    r'pfunction_hook.SIGNATURE = {PARAMETERS eps,RETURNS eps,BYREF false} /\ ppropertydesc.TYPE = eps /\ $eh_guard(S)',
    r'S_return_found = $eh_seek(S,1,1000)',
    r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
    r'S_return = S_return_found[.COMPLETION = NORMAL]',
    r'S_return.CURRENT = (pcallcontext_hook)',
    r'pcallcontext_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook /\ pcallcontext_hook.FUNCTION = ppropertyhook.HOOK /\ S_return.ORIGIN = (ppropertyhook.HOOK)',
    r'S_return.TODO = (RETURN_VALUE z_return) :: ptask_return*',
    r'S_return.RESULT = KNOWN (PINT 8) /\ S_return.EVENTS = eps /\ $eh_slot(S_return,ppropertyhook.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT 7)))',
    r'$property_hook_expression_context(S_return) /\ $typed_return_task_valid(S_return,z_return) /\ $typed_return_source(S_return,ppropertyhook.HOOK,z_return)',
    r'$property_hook_expression_return(S_return,ppropertyhook.HOOK,z_return) = (expression_body) /\ $heap_owners($heap_prune($heap_graph(S_return)),HOBJECT ppropertyhook.OBJECT) = 2 /\ $eh_guard(S_return)',
    r'PhpStep: S_return ~> S_unwind_raw',
    r'S_unwind_raw.TODO = [RETURN_UNWIND (KNOWN (PINT 8)) (ppropertyhook.HOOK)] /\ S_unwind_raw.RESULT = KNOWN PNULL /\ S_unwind_raw.COMPLETION = NORMAL',
    r'S_unwind_raw.CURRENT = S_return.CURRENT /\ S_unwind_raw.OBJECTPROPS = S_return.OBJECTPROPS /\ S_unwind_raw.STORE = S_return.STORE /\ S_unwind_raw.EVENTS = S_return.EVENTS',
    r'S_unwind = $eh_after(S_return,S_unwind_raw)',
    r'$eh_guard(S_unwind)',
    r'S_result_found = $eh_seek(S_unwind,2,1000)',
    r'S_result_found.COMPLETION = NORMAL \/ S_result_found.COMPLETION = BUDGET',
    r'S_result = S_result_found[.COMPLETION = NORMAL]',
    r'S_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask_result*',
    r'S_result.RESULT = KNOWN (PINT 8) /\ S_result.CURRENT = eps /\ $eh_slot(S_result,ppropertyhook.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT 7)))',
    r'$heap_owners($heap_prune($heap_graph(S_result)),HOBJECT ppropertyhook.OBJECT) = 1 /\ $eh_guard(S_result)',
    r'PhpStep: S_result ~> S_result_raw',
    r'S_result_raw.TODO = ptask_result* /\ S_result_raw.RESULT = S_result.RESULT /\ S_result_raw.BASE = BASE_VALUE S_result.RESULT /\ S_result_raw.OBJECTPROPS = S_result.OBJECTPROPS',
    r'S_done = $drive($eh_after(S_result,S_result_raw),1000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $eh_guard(S_done)',
    r'$eh_output(S_done.EVENTS) = EXPECTED_OUTPUT',
]

DERIVED = [
    r'$property_hook_expression_return(S_return,ppropertyhook.SITE,z_return) = eps /\ $property_hook_expression_return(S_return,ppropertyhook.HOOK,999) = eps',
    r'$property_hook_expression_return(S_return[.SOURCES = eps],ppropertyhook.HOOK,z_return) = eps /\ $property_hook_expression_return(S_return[.CLASSES = eps],ppropertyhook.HOOK,z_return) = eps',
    r'$property_hook_expression_return(S_return[.FUNCTIONS = [pfunction_hook[.BODY = eps]]],ppropertyhook.HOOK,z_return) = eps',
    r'$property_hook_expression_return(S_return[.FUNCTIONS = [pfunction_hook[.NAME = $ptascii("wrong")]]],ppropertyhook.HOOK,z_return) = eps',
    r'$property_hook_expression_return(S_return[.FUNCTIONS = [pfunction_hook[.SIGNATURE.BYREF = true]]],ppropertyhook.HOOK,z_return) = eps',
    r'$property_hook_expression_return(S_return[.FUNCTIONS = [pfunction_hook[.SIGNATURE.RETURNS = [PTBRANCH ([PTBUILTIN "int"])]]]],ppropertyhook.HOOK,z_return) = eps',
    r'$property_hook_expression_return(S_return[.FUNCTIONS = [pfunction_hook[.CODE.EXPRESSIONS = eps]]],ppropertyhook.HOOK,z_return) = eps',
    r'$property_hook_expression_return(S_return[.FUNCTIONS = [pfunction_hook[.CODE.EXPRESSIONS = [CODEARROW pfunction_hook.BODY 999]]]],ppropertyhook.HOOK,z_return) = eps',
    r'~$typed_return_task_valid(S_return[.FUNCTIONS = [pfunction_hook[.CODE.EXPRESSIONS = eps]]],z_return)',
    r'~$typed_return_task_valid(S_return[.FUNCTIONS = [pfunction_hook[.CODE.EXPRESSIONS = [CODEARROW pfunction_hook.BODY 999]]]],z_return)',
    r'~$typed_return_task_valid(S_return[.ORIGIN = (ppropertyhook.SITE)],z_return) /\ ~$typed_return_task_valid(S_return,999)',
    r'~$typed_return_task_valid(S_return[.CURRENT = (pcallcontext_hook[.TARGET = PROPERTY_HOOK_TARGET ppropertyhook[.PROPERTY = ppropertyhook.HOOK]])],z_return)',
    r'~$typed_return_source(S_return[.FUNCTIONS = [pfunction_hook[.BODY = eps]]],ppropertyhook.HOOK,z_return)',
    r'~$typed_return_source(S_return,ppropertyhook.SITE,z_return) /\ ~$typed_return_source(S_return,ppropertyhook.HOOK,999)',
    r'~$declaration_history_valid(S_return[.FUNCTIONS = [pfunction_hook[.CODE.EXPRESSIONS = [CODEARROW pfunction_hook.BODY z_return]]]])',
]

STRING = [
    r'$property_hook_plan(S) = (ppropertyhook)',
    r'$property_hook_function(S,ppropertyhook) = (pfunction_hook)',
    r'$arrow_line(pfunction_hook.CODE.EXPRESSIONS,pfunction_hook.BODY) = (z_return)',
    r'$eh_slot(S,ppropertyhook.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT pvalue_backing))',
    r'$string_bytes(pvalue_backing) = ($ptascii("7")) /\ $eh_guard(S)',
    r'S_callback_found = $eh_seek(S,3,1000)',
    r'S_callback_found.COMPLETION = NORMAL \/ S_callback_found.COMPLETION = BUDGET',
    r'S_callback = S_callback_found[.COMPLETION = NORMAL]',
    r'S_callback.CURRENT = (pcallcontext_string)',
    r'S_callback.FRAMES = pframe_hook :: pframe_tail*',
    r'pframe_hook.CONTEXT = (pcallcontext_hook)',
    r'pcallcontext_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook /\ pcallcontext_hook.FUNCTION = ppropertyhook.HOOK /\ pcallcontext_string.FUNCTION =/= ppropertyhook.HOOK',
    r'pframe_hook.TODO = (STRINGIFY_RESULT n_string ppropertyhook.HOOK z_return) :: (RETURN_VALUE z_return) :: (TYPE_RETURN_THROW n_string ppropertyhook.HOOK z_return) :: ptask_return*',
    r'pcallcontext_string.RECEIVER = (n_string) /\ ~$property_hook_expression_context(S_callback)',
    r'$typed_return_source(S_callback,ppropertyhook.HOOK,z_return) /\ $stringify_source(S_callback,ppropertyhook.HOOK,z_return,RETURN_VALUE z_return) /\ $eh_guard(S_callback)',
    r'$heap_owners($heap_prune($heap_graph(S_callback)),HOBJECT ppropertyhook.OBJECT) = 2 /\ $eh_output(S_callback.EVENTS) = $ptascii("G7|")',
    r'S_return_found = $eh_seek(S_callback,1,1000)',
    r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
    r'S_return = S_return_found[.COMPLETION = NORMAL]',
    r'S_return.TODO = (RETURN_VALUE z_return) :: ptask_tail*',
    r'S_return.RESULT = KNOWN pvalue_text',
    r'$string_bytes(pvalue_text) = ($ptascii("19")) /\ $typed_return_task_valid(S_return,z_return) /\ $typed_return_source(S_return,ppropertyhook.HOOK,z_return)',
    r'$eh_output(S_return.EVENTS) = $ptascii("G7|S|") /\ $eh_slot(S_return,ppropertyhook.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT pvalue_backing)) /\ $eh_guard(S_return)',
    r'PhpStep: S_return ~> S_return_raw',
    r'S_return_raw.TODO = [RETURN_UNWIND (KNOWN pvalue_text) (ppropertyhook.HOOK)] /\ S_return_raw.RESULT = KNOWN PNULL /\ S_return_raw.COMPLETION = NORMAL',
    r'S_return_raw.EVENTS = S_return.EVENTS /\ S_return_raw.OBJECTPROPS = S_return.OBJECTPROPS',
    r'S_done = $drive($eh_after(S_return,S_return_raw),1000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $eh_guard(S_done)',
    r'$eh_output(S_done.EVENTS) = EXPECTED_OUTPUT',
]

HEAP = [
    r'$property_hook_plan(S) = (ppropertyhook)',
    r'$lookup(S.ENV,$ptascii("weak")) = (n_weak_cell)',
    r'S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
    r'$weakref_get(S,n_weak) = POBJECT n_leaf',
    r'$lookup(S.ENV,$ptascii("leaf")) = eps /\ $eh_guard(S)',
    r'$eh_slot(S,ppropertyhook.OBJECT,$ptascii("value")) = (PROP_VALUE (DIRECT (POBJECT n_leaf)))',
    r'$node_children(S,HOBJECT ppropertyhook.OBJECT) = [HOBJECT n_leaf] /\ $node_children(S,HOBJECT n_weak) = eps',
    r'$heap_owners($heap_prune($heap_graph(S)),HOBJECT ppropertyhook.OBJECT) = 1 /\ $heap_owners($heap_prune($heap_graph(S)),HOBJECT n_leaf) = 1',
    r'S_hold_found = $eh_seek(S,1,1000)',
    r'S_hold_found.COMPLETION = NORMAL \/ S_hold_found.COMPLETION = BUDGET',
    r'S_hold = S_hold_found[.COMPLETION = NORMAL]',
    r'S_hold.CURRENT = (pcallcontext_hold)',
    r'pcallcontext_hold.TARGET = PROPERTY_HOOK_TARGET ppropertyhook /\ pcallcontext_hold.RECEIVER = (ppropertyhook.OBJECT)',
    r'S_hold.TODO = (RETURN_VALUE z_return) :: ptask_hold*',
    r'S_hold.RESULT = KNOWN (POBJECT n_leaf) /\ $typed_return_task_valid(S_hold,z_return)',
    r'S_hold.GLOBALTABLE = (psymboltable_global)',
    r'$lookup(psymboltable_global.ENV,$ptascii("box")) = eps /\ $eh_output(S_hold.EVENTS) = $ptascii("G|")',
    r'$heap_owners($heap_prune($heap_graph(S_hold)),HOBJECT ppropertyhook.OBJECT) = 1 /\ $heap_owners($heap_prune($heap_graph(S_hold)),HOBJECT n_leaf) = 2 /\ $eh_guard(S_hold)',
    r'PhpStep: S_hold ~> S_return_raw',
    r'S_return_raw.TODO = [RETURN_UNWIND (KNOWN (POBJECT n_leaf)) (ppropertyhook.HOOK)] /\ S_return_raw.RESULT = KNOWN PNULL /\ S_return_raw.COMPLETION = NORMAL',
    r'S_return = $eh_after(S_hold,S_return_raw)',
    r'$eh_guard(S_return) /\ $heap_owners($heap_prune($heap_graph(S_return)),HOBJECT n_leaf) = 2',
    r'PhpStep: S_return ~> S_exit_raw',
    r'S_exit_raw.RESULT = KNOWN PNULL /\ S_exit_raw.COMPLETION = NORMAL /\ S_exit_raw.CURRENT = eps',
    r'S_exit_raw.DESTRUCTION.FRAMES = pdestructionframe_return :: pdestructionframe_tail*',
    r'pdestructionframe_return.VALUE = KNOWN (POBJECT n_leaf) /\ pdestructionframe_return.FUNCTION = ppropertyhook.HOOK /\ pdestructionframe_return.PENDING = eps',
    r'$task_nodes(DESTRUCTOR_FRAME_EXIT pdestructionframe_return) = [HOBJECT n_leaf]',
    r'S_result_found = $eh_seek($eh_after(S_return,S_exit_raw),2,1000)',
    r'S_result_found.COMPLETION = NORMAL \/ S_result_found.COMPLETION = BUDGET',
    r'S_result = S_result_found[.COMPLETION = NORMAL]',
    r'S_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask_result*',
    r'S_result.RESULT = KNOWN (POBJECT n_leaf) /\ S_result.CURRENT = eps',
    r'$eh_output(S_result.EVENTS) = $ptascii("G|B|") /\ ~((HOBJECT ppropertyhook.OBJECT) <- S_result.ALLOCATIONS)',
    r'$heap_owners($heap_prune($heap_graph(S_result)),HOBJECT n_leaf) = 1 /\ $weakref_get(S_result,n_weak) = POBJECT n_leaf /\ $eh_guard(S_result)',
    r'$property_hook_valid(S_result,ppropertyhook,false) /\ ~$property_hook_valid(S_result,ppropertyhook,true)',
    r'PhpStep: S_result ~> S_result_raw',
    r'S_result_raw.RESULT = KNOWN (POBJECT n_leaf) /\ S_result_raw.BASE = BASE_VALUE (KNOWN (POBJECT n_leaf)) /\ S_result_raw.TODO = ptask_result*',
    r'S_unset_found = $eh_seek($eh_after(S_result,S_result_raw),5,1000)',
    r'S_unset_found.COMPLETION = NORMAL \/ S_unset_found.COMPLETION = BUDGET',
    r'S_unset = S_unset_found[.COMPLETION = NORMAL]',
    r'$lookup(S_unset.ENV,$ptascii("result")) = (n_result_cell)',
    r'S_unset.STORE[n_result_cell] = DEFINED (POBJECT n_leaf)',
    r'$heap_owners($heap_prune($heap_graph(S_unset)),HOBJECT n_leaf) = 1 /\ $eh_output(S_unset.EVENTS) = $ptascii("G|B|L|") /\ $eh_guard(S_unset)',
    r'PhpStep: S_unset ~> S_unset_raw',
    r'S_done = $drive($eh_after(S_unset,S_unset_raw),1000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ $eh_guard(S_done)',
    r'$weakref_get(S_done,n_weak) = PNULL /\ ~((HOBJECT n_leaf) <- S_done.ALLOCATIONS) /\ $eh_output(S_done.EVENTS) = EXPECTED_OUTPUT',
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    profile_file = ROOT / 'tests/semantics/profile.json'
    profile = json.loads(profile_file.read_bytes())
    catalogue = HERE / 'expression_get_hook_cases.json'
    data = json.loads(catalogue.read_bytes())
    assert data['native_profile'] == profile
    selections = [('untyped', 'untyped-return', UNTYPED, DERIVED),
                  ('string', 'typed-string-callback', STRING, []),
                  ('heap', 'receiver-release-payload', HEAP, [])]
    sources = [HERE / ('expression-get-hook-' + suffix + '.php') for suffix in ('untyped','string','lifetime')]
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
    out = Path(tempfile.mkdtemp(prefix='expression-get-hook-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    derived = sum(len(row[3]) for row in selections)
    reached = sum(5 + len(row[2]) for row in selections)
    assert derived == 15 and reached == 122
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
            name, case_id, clauses, negatives = selection
            output = base64.b64decode(case['stdout_base64'])
            setup = ['S_initial = $php_run(' + ast_fixture + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $eh_seek(S_initial,0,1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            content += '\ndec $eh_' + name + '() : bool\ndef $eh_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                condition = condition.replace('EXPECTED_OUTPUT', byte_expr(output))
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $eh_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = ($eh_untyped() /\\ $eh_string() /\\ $eh_heap())\n'
        fixture = out / 'hook.watsup'
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
