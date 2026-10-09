"""Prepare genuine captured constructor sends, readonly errors and final releases."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker

PREFIX = r"""dec $sc_stage(pstate, nat) : bool
def $sc_stage(S, 0) = true
  -- if S.TODO = (METHOD_PREP phpType20 phpType7* false b_base z) :: ptask*
  -- if $ppfirstclass(phpType7*)
  -- if $method_source_name(phpType20, $ptascii("__construct"))
def $sc_stage(S, 1) = true
  -- if S.TODO = (CTOR_SEND pctorcall) :: ptask*
  -- if pctorcall.MODE = CTOR_CAPTURE n
def $sc_stage(S, 2) = true
  -- if S.TODO = (CTOR_INVOKE pctorcall) :: ptask*
  -- if pctorcall.MODE = CTOR_CAPTURE n
def $sc_stage(S, 3) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES "Y29uc3RydWN0b3I=") metadata)) :: ptask*
def $sc_stage(S, 4) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES "ZXJyb3I=") metadata)) :: ptask*
def $sc_stage(S, 5) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $target_function(S, pcallcontext.TARGET) = (pfunction)
  -- if $ptlc(pfunction.NAME) = $ptascii("sensitive_ctor_arg26")
def $sc_stage(S, n) = false -- otherwise
dec $sc_capture_mode(pctorcallmode) : bool
def $sc_capture_mode(CTOR_CAPTURE n) = true
def $sc_capture_mode(pctorcallmode) = false -- otherwise
dec $sc_saved_task(ptask) : pctorcall?
def $sc_saved_task(CTOR_SEND pctorcall) = (pctorcall)
  -- if $sc_capture_mode(pctorcall.MODE)
def $sc_saved_task(ptask) = eps -- otherwise
dec $sc_saved_call(ptask*) : pctorcall?
def $sc_saved_call(ptask :: ptask_tail*) = (pctorcall)
  -- if $sc_saved_task(ptask) = (pctorcall)
def $sc_saved_call(ptask :: ptask_tail*) = $sc_saved_call(ptask_tail*)
  -- if $sc_saved_task(ptask) = eps
def $sc_saved_call(eps) = eps
dec $sc_seek(pstate, nat, nat) : pstate
def $sc_seek(S, n_stage, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $sc_stage(S, n_stage) \/ n = 0
def $sc_seek(S, n_stage, n) = $sc_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$sc_stage(S, n_stage) /\ $(n > 0)
def $sc_seek(S, n_stage, n) = $sc_seek($drive_steps(S, 1), n_stage, $nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $sc_seek(S, n_stage, n) = S -- otherwise
dec $sc_after(pstate, pstate) : pstate
def $sc_after(S, S_next) = $gc_transition_owners(S, $destruction_transition_owners(S, $sensitive_trace_freeze($source_exception_transition(S, $throwable_transition(S, S_next)))))
dec $sc_guard(pstate) : bool
def $sc_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $sc_output(pevent*) : ptbytes
def $sc_output(eps) = eps
def $sc_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $sc_output(pevent*)
"""

CAPTURE = [
    r'S.TODO = (METHOD_PREP phpType20 phpType7* false b_base z) :: ptask_tail*',
    r'$ppfirstclass(phpType7*) /\ $method_source_name(phpType20,$ptascii("__construct"))',
    r'S.ORIGIN = (porigin_creation)',
    r'$origin_node(S.SOURCES,porigin_creation) = (NExprMethodCall expression phpType20 (SEQUENCE phpType7*) metadata)',
    r'$lookup(S.ENV,$ptascii("wrapper")) = (n_wrapper_cell)',
    r'S.STORE[n_wrapper_cell] = DEFINED (POBJECT n_wrapper)',
    r'S.OBJECTS[n_wrapper] = SENSITIVEVALUE (POBJECT n_old)',
    r'$lookup(S.ENV,$ptascii("weak")) = (n_weak_cell)',
    r'S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
    r'$weakref_get(S,n_weak) = POBJECT n_old /\ $sc_guard(S)',
    r'n_closure = |S.OBJECTS|',
    r'PhpStep: S ~> S_capture',
    r'S_capture.COMPLETION = NORMAL /\ S_capture.RESULT = KNOWN (POBJECT n_closure) /\ S_capture.TODO = ptask_tail*',
    r'S_capture.OBJECTS = S.OBJECTS ++ [CTORCLOSURE n_wrapper "SensitiveParameterValue" porigin_creation]',
    r'S_capture.ALLOCATIONS = S.ALLOCATIONS ++ [HOBJECT n_closure]',
    r'S_capture.SOURCES = S.SOURCES /\ S_capture.EVENTS = S.EVENTS /\ S_capture.ENV = S.ENV /\ S_capture.STORE = S.STORE /\ S_capture.ARRAYS = S.ARRAYS',
    r'$node_children(S_capture,HOBJECT n_closure) = [HOBJECT n_wrapper]',
    r'$node_children(S_capture,HOBJECT n_wrapper) = [HOBJECT n_old] /\ $node_children(S_capture,HOBJECT n_weak) = eps',
    r'$ctor_capture_live(S_capture,n_closure)',
    r'S_ready = $sc_after(S,S_capture)',
    r'$sc_guard(S_ready) /\ $closure_callable(S_ready,n_closure)',
]
DERIVED_CAPTURE = [
    r'~$ctor_capture_live(S_ready[.OBJECTS[n_closure] = CTORCLOSURE n_wrapper "Error" porigin_creation],n_closure)',
    r'~$ctor_capture_live(S_ready[.OBJECTS[n_closure] = CTORCLOSURE n_wrapper "SensitiveParameterValue" (PORIGIN 999 eps)],n_closure)',
    r'$origin_child((porigin_creation),[PCFIELD 0]) = (porigin_child)',
    r'~$ctor_capture_live(S_ready[.OBJECTS[n_closure] = CTORCLOSURE n_wrapper "SensitiveParameterValue" porigin_child],n_closure)',
    r'~$ctor_capture_live(S_ready[.OBJECTS[n_closure] = CTORCLOSURE n_old "SensitiveParameterValue" porigin_creation],n_closure)',
    r'~$ctor_capture_live(S_ready[.OBJECTS[n_closure] = CTORCLOSURE n_closure "SensitiveParameterValue" porigin_creation],n_closure)',
    r'~$ctor_capture_live(S_ready[.OBJECTS[n_closure] = CTORCLOSURE 999 "SensitiveParameterValue" porigin_creation],n_closure)',
    r'~$ctor_capture_live(S_ready[.ALLOCATIONS = eps],n_closure)',
    r'~$ctor_capture_live(S_ready[.SOURCES = eps],n_closure)',
    r'~$ctor_capture_live(S_ready[.OBJECTS[n_wrapper] = SENSITIVEUNSET porigin_creation],n_closure)',
    r'~$ctor_capture_live(S_ready[.OBJECTS[n_wrapper] = SENSITIVEVALUE (POBJECT 999)],n_closure)',
    r'~$ctor_capture_live(S_ready[.OBJECTS[n_closure] = SENSITIVEVALUE PNULL],n_closure)',
]
SEND = [
    r'S_send_found = $sc_seek(S_ready,1,1000)',
    r'S_send_found.COMPLETION = NORMAL \/ S_send_found.COMPLETION = BUDGET',
    r'S_send = S_send_found[.COMPLETION = NORMAL]',
    r'S_send.TODO = (CTOR_SEND pctorcall_send) :: ptask_send*',
    r'pctorcall_send.RECEIVER = n_wrapper /\ pctorcall_send.BASE = "SensitiveParameterValue" /\ pctorcall_send.MODE = CTOR_CAPTURE n_closure /\ pctorcall_send.INDEX = 0 /\ pctorcall_send.SENT = eps',
    r'porigin_call = pctorcall_send.SITE',
    r'porigin_call =/= porigin_creation /\ $ctor_capture_site(S_send,porigin_call)',
    r'$origin_node(S_send.SOURCES,porigin_call) = (NExprFuncCall expression_call (SEQUENCE phpType7_call*) metadata_call)',
    r'$lookup(S_send.ENV,$ptascii("leaf")) = eps /\ $lookup(S_send.ENV,$ptascii("wrapper")) = eps',
    r'$lookup(S_send.ENV,$ptascii("replacement")) = (n_replacement_cell)',
    r'S_send.STORE[n_replacement_cell] = DEFINED (POBJECT n_replacement)',
    r'$lookup(S_send.ENV,$ptascii("replacementWeak")) = (n_replacement_weak_cell)',
    r'S_send.STORE[n_replacement_weak_cell] = DEFINED (POBJECT n_replacement_weak)',
    r'$weakref_get(S_send,n_replacement_weak) = POBJECT n_replacement /\ $weakref_get(S_send,n_weak) = POBJECT n_old',
    r'$ctor_selected(S_send,pctorcall_send) /\ $call_task_valid(S_send,CTOR_SEND pctorcall_send) /\ $sc_guard(S_send)',
    r'$heap_owners($heap_prune($heap_graph(S_send)),HOBJECT n_old) = 1',
    r'PhpStep: S_send ~> S_sent_raw',
    r'pctorcall_sent = pctorcall_send[.INDEX = 1][.SENT = [NAMED_SENT (KNOWN (POBJECT n_replacement))]]',
    r'S_sent_raw.TODO = (CTOR_ARGS pctorcall_sent) :: ptask_send* /\ S_sent_raw.COMPLETION = NORMAL /\ S_sent_raw.RESULT = KNOWN PNULL',
    r'S_sent_raw.OBJECTS = S_send.OBJECTS /\ S_sent_raw.STORE = S_send.STORE /\ S_sent_raw.ARRAYS = S_send.ARRAYS /\ S_sent_raw.EVENTS = S_send.EVENTS',
    r'$ctor_nodes(pctorcall_sent) = [HOBJECT n_wrapper,HOBJECT n_closure,HOBJECT n_replacement]',
    r'S_sent = $sc_after(S_send,S_sent_raw)',
    r'$heap_owners($heap_prune($heap_graph(S_sent)),HOBJECT n_replacement) = 2 /\ $sc_guard(S_sent)',
]
DERIVED_SEND = [
    r'~$ctor_selected(S_send,pctorcall_send[.MODE = CTOR_NEW]) /\ ~$ctor_selected(S_send,pctorcall_send[.MODE = CTOR_METHOD])',
    r'~$ctor_selected(S_send,pctorcall_send[.MODE = CTOR_CAPTURE n_wrapper])',
    r'~$ctor_selected(S_send,pctorcall_send[.RECEIVER = n_replacement]) /\ ~$ctor_selected(S_send,pctorcall_send[.BASE = "Error"])',
    r'~$ctor_selected(S_send,pctorcall_send[.SITE = porigin_creation]) /\ ~$ctor_selected(S_send,pctorcall_send[.SITE = PORIGIN 999 eps])',
    r'~$call_task_valid(S_send,CTOR_SEND pctorcall_send[.INDEX = 999]) /\ ~$call_task_valid(S_send,CTOR_SEND pctorcall_send[.LINE = 999])',
    r'~$ctor_selected(S_send[.TODO = [CTOR_SEND pctorcall_send]][.FRAMES = eps],pctorcall_send)',
    r'~$ctor_selected(S_send[.TODO = [CTOR_SEND pctorcall_send,CTOR_CAPTURE_RESULT n_wrapper porigin_call]][.FRAMES = eps],pctorcall_send)',
    r'~$ctor_selected(S_send[.TODO = [CTOR_SEND pctorcall_send,CTOR_CAPTURE_RESULT n_closure porigin_creation]][.FRAMES = eps],pctorcall_send)',
    r'$ctor_selected(S_send[.TODO = [CTOR_SEND pctorcall_send,CTOR_CAPTURE_RESULT n_closure porigin_call]][.FRAMES = eps],pctorcall_send)',
    r'~$call_task_valid(S_send,CTOR_CAPTURE_RESULT n_wrapper porigin_call) /\ ~$call_task_valid(S_send,CTOR_CAPTURE_RESULT n_closure porigin_creation)',
]
ERROR_RELEASE = [
    r'S_invoke_found = $sc_seek(S_sent,2,1000)',
    r'S_invoke_found.COMPLETION = NORMAL \/ S_invoke_found.COMPLETION = BUDGET',
    r'S_invoke = S_invoke_found[.COMPLETION = NORMAL]',
    r'S_invoke.TODO = (CTOR_INVOKE pctorcall_sent) :: ptask_invoke*',
    r'$call_task_valid(S_invoke,CTOR_INVOKE pctorcall_sent) /\ $sc_guard(S_invoke)',
    r'n_error = |S_invoke.OBJECTS|',
    r'PhpStep: S_invoke ~> S_error_raw',
    r'S_error_raw.COMPLETION = THROWING n_error /\ S_error_raw.TODO = ptask_invoke*',
    r'S_error_raw.OBJECTS[n_wrapper] = SENSITIVEVALUE (POBJECT n_old)',
    r'S_error_raw.OBJECTS[n_closure] = CTORCLOSURE n_wrapper "SensitiveParameterValue" porigin_creation',
    r'S_error_raw.STORE = S_invoke.STORE /\ S_error_raw.ENV = S_invoke.ENV /\ S_error_raw.EVENTS = S_invoke.EVENTS',
    r'$throwable_field(S_error_raw,n_error,"message") = PSTRING ($ptascii("Cannot modify readonly property SensitiveParameterValue::$value"))',
    r'S_error_ready = $sc_after(S_invoke,S_error_raw)',
    r'S_unset_found = $sc_seek(S_error_ready,3,1000)',
    r'S_unset_found.COMPLETION = NORMAL \/ S_unset_found.COMPLETION = BUDGET',
    r'S_unset = S_unset_found[.COMPLETION = NORMAL]',
    r'$lookup(S_unset.ENV,$ptascii("error")) = (n_error_cell)',
    r'S_unset.STORE[n_error_cell] = DEFINED (POBJECT n_error)',
    r'$lookup(S_unset.ENV,$ptascii("replacement")) = eps',
    r'$sc_output(S_unset.EVENTS) = $ptascii("LO|E|LR|") /\ $sc_guard(S_unset)',
    r'$heap_owners($heap_prune($heap_graph(S_unset)),HOBJECT n_old) = 1 /\ $heap_owners($heap_prune($heap_graph(S_unset)),HOBJECT n_replacement) = 1',
    r'$weakref_get(S_unset,n_weak) = POBJECT n_old /\ $weakref_get(S_unset,n_replacement_weak) = POBJECT n_replacement',
    r'PhpStep: S_unset ~> S_unset_raw',
    r'S_unset_ready = $sc_after(S_unset,S_unset_raw)',
    r'S_error_unset_found = $sc_seek(S_unset_ready,4,1000)',
    r'S_error_unset_found.COMPLETION = NORMAL \/ S_error_unset_found.COMPLETION = BUDGET',
    r'S_error_unset = S_error_unset_found[.COMPLETION = NORMAL]',
    r'$lookup(S_error_unset.ENV,$ptascii("constructor")) = eps',
    r'~((HOBJECT n_closure) <- S_error_unset.ALLOCATIONS) /\ ~((HOBJECT n_wrapper) <- S_error_unset.ALLOCATIONS) /\ ~((HOBJECT n_old) <- S_error_unset.ALLOCATIONS)',
    r'$weakref_get(S_error_unset,n_weak) = PNULL /\ $weakref_get(S_error_unset,n_replacement_weak) = POBJECT n_replacement',
    r'$heap_owners($heap_prune($heap_graph(S_error_unset)),HOBJECT n_replacement) = 1 /\ $sc_guard(S_error_unset)',
    r'$sc_output(S_error_unset.EVENTS) = $ptascii("LO|E|LR|O|NO|LR|")',
    r'PhpStep: S_error_unset ~> S_error_unset_raw',
    r'S_error_unset_ready = $sc_after(S_error_unset,S_error_unset_raw)',
    r'S_done = $drive(S_error_unset_ready,1000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps',
    r'$sc_output(S_done.EVENTS) = $ptascii("LO|E|LR|O|NO|LR|R|NR|")',
    r'$weakref_get(S_done,n_replacement_weak) = PNULL /\ ~((HOBJECT n_replacement) <- S_done.ALLOCATIONS) /\ $sc_guard(S_done)',
]
NESTED = [
    r'S_nested_found = $sc_seek(S_nested_initial,5,1000)',
    r'S_nested_found.COMPLETION = NORMAL \/ S_nested_found.COMPLETION = BUDGET',
    r'S_nested = S_nested_found[.COMPLETION = NORMAL]',
    r'S_nested.CURRENT = (pcallcontext_nested)',
    r'$target_function(S_nested,pcallcontext_nested.TARGET) = (pfunction_nested)',
    r'$ptlc(pfunction_nested.NAME) = $ptascii("sensitive_ctor_arg26") /\ $sc_guard(S_nested)',
    r'$(|S_nested.FRAMES| > 0)',
    r'pframe_ctor = S_nested.FRAMES[0]',
    r'$sc_saved_call(pframe_ctor.TODO) = (pctorcall_nested)',
    r'pctorcall_nested.MODE = CTOR_CAPTURE n_nested',
    r'$ctor_capture_live(S_nested,n_nested) /\ $ctor_selected(S_nested,pctorcall_nested)',
    r'~$ctor_capture_tasks(S_nested.TODO,n_nested,pctorcall_nested.SITE)',
    r'$ctor_capture_frames(S_nested.FRAMES,n_nested,pctorcall_nested.SITE)',
]
DERIVED_NESTED = [
    r'~$ctor_selected(S_nested[.FRAMES = eps],pctorcall_nested)',
    r'~$ctor_selected(S_nested[.FRAMES = [pframe_ctor[.TODO = [CTOR_SEND pctorcall_nested]]]],pctorcall_nested)',
    r'~$ctor_selected(S_nested[.FRAMES = [pframe_ctor[.TODO = [CTOR_SEND pctorcall_nested,CTOR_CAPTURE_RESULT pctorcall_nested.RECEIVER pctorcall_nested.SITE]]]],pctorcall_nested)',
    r'~$ctor_selected(S_nested[.FRAMES = [pframe_ctor[.TODO = [CTOR_SEND pctorcall_nested,CTOR_CAPTURE_RESULT n_nested (PORIGIN 999 eps)]]]],pctorcall_nested)',
    r'$ctor_selected(S_nested[.FRAMES = [pframe_ctor[.TODO = [CTOR_SEND pctorcall_nested,CTOR_CAPTURE_RESULT n_nested pctorcall_nested.SITE]]]],pctorcall_nested)',
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()
    catalogue = HERE / 'sensitive_value_constructor_callable_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = ROOT / 'tests/semantics/profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    sources = [HERE / 'sensitive-value-constructor-callable-heap.php',
               HERE / 'sensitive-value-constructor-callable-args.php']
    names = ['captured-constructor-lifetime', 'scalar-readonly-arity']
    for name, source in zip(names, sources):
        case = next(row for row in data['cases'] if row['id'] == name)
        assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256']
        assert case['status'] == 'normal' and case['exit_status'] == 0
    php, adapter, bridge, worker, runner, compiler = (ROOT / name for name in [
        '.tools/php/bin/php', '_build/default/adapter/main.exe', '.tools/php-file.so',
        'frontend/worker.php', 'tests/semantics/_build/default/numeric_runner.exe', '.tools/spectec/bin/p4spectec'])
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_bytes())]
    watched = [Path(__file__), Path(recorder.__file__), catalogue, *sources, profile_file, php,
               adapter, bridge, worker, runner, compiler, manifest, *modules,
               ROOT / 'spec/schema.json', ROOT / 'tests/semantics/recorded_worker.py']
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    assert revision == args.revision and not status
    before = {str(p): sha(p) for p in watched}
    out = Path(tempfile.mkdtemp(prefix='sensitive-constructor-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    derived = len(DERIVED_CAPTURE) + len(DERIVED_SEND) + len(DERIVED_NESTED)
    reached = 5 + len(CAPTURE) + len(SEND) + len(ERROR_RELEASE) + 2 + len(NESTED)
    report = {'revision': revision, 'inputs': before, 'profile': profile, 'module_count': len(modules),
              'mode': 'SL', 'cache': False, 'det': True, 'evaluated': False, 'records': [],
              'application_invocations': 0, 'application_evaluations': 0, 'source_agreements': 0,
              'derived_premises': derived, 'reached_premises': reached,
              'budget_seconds': 120, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'jobs': 1}, 'passed': False}
    fixture = None
    try:
        flags = [part for k, v in profile.items() for part in ('-d', k + '=' + v)]
        fixtures = []
        for i, source in enumerate(sources):
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
        setup = ['S_initial = $php_run(' + fixtures[0] + ',0,' + json.dumps(base64.b64encode(str(sources[0]).encode()).decode()) + ')',
                 r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                 'S_found = $sc_seek(S_initial,0,1000)',
                 r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                 'S = S_found[.COMPLETION = NORMAL]']
        content = PREFIX + '\ndec $sc_heap() : bool\ndef $sc_heap() = true\n'
        for condition in setup + CAPTURE + DERIVED_CAPTURE + SEND + DERIVED_SEND + ERROR_RELEASE:
            content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
        content += 'def $sc_heap() = false -- otherwise\n\ndec $sc_nested() : bool\ndef $sc_nested() = true\n'
        nested_setup = ['S_nested_initial = $php_run(' + fixtures[1] + ',0,' + json.dumps(base64.b64encode(str(sources[1]).encode()).decode()) + ')',
                        r'S_nested_initial.COMPLETION = NORMAL \/ S_nested_initial.COMPLETION = BUDGET']
        for condition in nested_setup + NESTED + DERIVED_NESTED:
            content += '  -- if ' + condition + '\n'
        content += 'def $sc_nested() = false -- otherwise\n\ndec $main() : bool\ndef $main() = ($sc_heap() /\\ $sc_nested())\n'
        fixture = out / 'constructor.watsup'
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
        report.update(inputs_stable=before == {str(p): sha(p) for p in watched},
                      fixture_stable=fixture is None or report['fixture_sha256'] == sha(fixture),
                      head_stable=revision == git('rev-parse', 'HEAD'), status_stable=status == git('status', '--short'))
        report['passed'] = report['passed'] and all(report[k] for k in ('inputs_stable', 'fixture_stable', 'head_stable', 'status_stable'))
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({k: report[k] for k in ('passed', 'evaluated', 'derived_premises', 'reached_premises', 'inputs_stable', 'head_stable', 'status_stable')}), flush=True)
    assert report['passed']

if __name__ == '__main__':
    main()
