"""Check current-This self calls, packed argument cleanup and outer receiver lifetime."""
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
syntax pmagicscopedstage = SC_FRONT | SC_PACK | SC_RECEIVE porigin | SC_ENTER nat ptbytes | SC_MUTATE nat nat | SC_DTOR nat | SC_INNER porigin | SC_OUTER | SC_CATCH
dec $sc_output(pevent*) : ptbytes
def $sc_output(eps) = eps
def $sc_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $sc_output(pevent*)
dec $sc_stage(pstate,pmagicscopedstage) : bool
def $sc_stage(S,SC_FRONT) = true
  -- if S.TODO = (SCOPED_CLASS phpType19 phpType20 phpType7* z) :: ptask*
def $sc_stage(S,SC_PACK) = true
  -- if S.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps n poperand* porigin? z) :: ptask*
def $sc_stage(S,SC_RECEIVE porigin) = true
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: ptask*
def $sc_stage(S,SC_ENTER n ptbytes) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = MAGIC_METHOD_TARGET pmagicmethodcall n_array pvalue*
  -- if S.STORE[n] = DEFINED PNULL
  -- if $sc_output(S.EVENTS) = ptbytes
def $sc_stage(S,SC_MUTATE n_child n_rhs) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.STORE[n_child] = DEFINED PNULL /\ S.STORE[n_rhs] = DEFINED (PINT 99)
  -- if $sc_output(S.EVENTS) = $ptascii("N:B|M|")
def $sc_stage(S,SC_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $sc_stage(S,SC_INNER porigin) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.FUNCTION = porigin
  -- if S.TODO = METHOD_RESULT :: ptask*
def $sc_stage(S,SC_OUTER) = true
  -- if S.CURRENT = eps
  -- if S.TODO = METHOD_RESULT :: ptask*
def $sc_stage(S,SC_CATCH) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask*
def $sc_stage(S,pmagicscopedstage) = false -- otherwise
dec $sc_seek(pstate,pmagicscopedstage,nat) : pstate
def $sc_seek(S,pmagicscopedstage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $sc_stage(S,pmagicscopedstage) \/ n = 0
def $sc_seek(S,pmagicscopedstage,n) = $sc_seek($drive_steps(S[.COMPLETION = NORMAL],1),pmagicscopedstage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$sc_stage(S,pmagicscopedstage) /\ $(n > 0)
def $sc_seek(S,pmagicscopedstage,n) = $sc_seek($drive_steps(S,1),pmagicscopedstage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $sc_seek(S,pmagicscopedstage,n) = S -- otherwise
dec $sc_after(pstate,pstate) : pstate
def $sc_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $sc_guard(pstate) : bool
def $sc_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $gc_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''

COMMON = r'''
S_front.TODO = (SCOPED_CLASS phpType19_self phpType20_missing phpType7_arguments* z_line) :: ptask_tail*
S_front.CURRENT = (pcallcontext_run)
pcallcontext_run.TARGET = METHOD_TARGET n_child pcallcontext_run.FUNCTION
pcallcontext_run.RECEIVER = (n_child)
S_front.FRAMES = pframe_run :: eps
S_main = $constant_frame_scope(S_front,pframe_run,eps)
S_main.CURRENT = eps
S_main.TODO = METHOD_RESULT :: ptask_main_tail*
$lookup(S_main.ENV,$ptascii("child")) = (n_child_cell)
$lookup(S_main.ENV,$ptascii("result")) = (n_result_cell)
$lookup(S_main.ENV,$ptascii("rhs")) = (n_rhs_cell)
S_front.STORE[n_child_cell] = DEFINED (POBJECT n_child) /\ S_front.STORE[n_result_cell] = DEFINED (PINT 42) /\ S_front.STORE[n_rhs_cell] = DEFINED (PINT 7)
$method_context_scope(S_front.CURRENT) = (porigin_parent)
pcallcontext_run.LEXICAL_CLASS = (porigin_parent)
$class_at(S_front.CLASSES,porigin_parent) = (pclassdesc_parent)
pclassdesc_parent.NAME = $ptascii("ScopedParent107")
S_front.OBJECTS[n_child] = INSTANCE porigin_child
$class_at(S_front.CLASSES,porigin_child) = (pclassdesc_child)
pclassdesc_child.NAME = $ptascii("ScopedChild107") /\ pcallcontext_run.CALLED_CLASS = (porigin_child)
$magic_method_scoped(S_front,porigin_parent) /\ ~$magic_static_method_needed(S_front,porigin_parent)
$magic_method_plan(S_front,n_child,$ptascii("MiSsInG"),phpType7_arguments*,z_line) = (pmagicmethodcall)
pmagicmethodcall.CALLER = S_front.CURRENT /\ pmagicmethodcall.OWNER = 1 /\ pmagicmethodcall.TAIL = ptask_tail*
pmagicmethodcall.CLASS = porigin_child /\ pmagicmethodcall.LINE = z_line
$magic_method_scoped_source(S_front,pmagicmethodcall) /\ $magic_method_capture(S_front,pmagicmethodcall)
$effective_method(S_front,porigin_child,pmagicmethodcall.NAME,|S_front.CLASSES|) = eps
$effective_method(S_front,porigin_child,$ptascii("__call"),|S_front.CLASSES|) = (pmethoddesc_call)
pfunction_call = pmethoddesc_call.FUNCTION
pmethoddesc_call.OWNER = porigin_parent
$heap_owners($heap_graph(S_front),HOBJECT n_child) = 2 /\ $sc_guard(S_front)
PhpStep: S_front ~> S_raw_step
S_raw_step.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) phpType7_arguments* 0 eps (pmagicmethodcall.SITE) z_line) :: METHOD_RESULT :: ptask_tail*
S_raw = $sc_after(S_front,S_raw_step)
$magic_method_raw_valid(S_raw,pmagicmethodcall) /\ $magic_method_capture(S_raw,pmagicmethodcall)
$target_nodes(MAGIC_METHOD_SEND_TARGET pmagicmethodcall) = [HOBJECT n_child]
$heap_owners($heap_graph(S_raw),HOBJECT n_child) = 3 /\ $sc_guard(S_raw)
'''.strip().splitlines()

SELECTION = r'''
$lookup(S_front.ENV,$ptascii("first")) = (n_first_cell)
S_front.STORE[n_first_cell] = DEFINED (PINT 7) /\ ~(n_first_cell <- S_front.REFCELLS)
S_mutate_found = $sc_seek(S_raw,SC_MUTATE n_child_cell n_rhs_cell,1000)
S_mutate_found.COMPLETION = NORMAL \/ S_mutate_found.COMPLETION = BUDGET
S_mutate = S_mutate_found[.COMPLETION = NORMAL]
$sc_stage(S_mutate,SC_MUTATE n_child_cell n_rhs_cell)
S_mutate.CURRENT = (pcallcontext_mutate)
pcallcontext_mutate.RECEIVER = eps /\ ~$magic_method_scoped(S_mutate,porigin_parent)
S_mutate.FRAMES = pframe_mutate :: pframe_run :: eps
S_mutate_saved = $constant_frame_scope(S_mutate,pframe_mutate,[pframe_run])
S_mutate_saved.TODO = (ORIGIN_RETURN (pmagicmethodcall.SITE)) :: (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN (PINT 7)]) (pmagicmethodcall.SITE) z_line) :: METHOD_RESULT :: ptask_tail*
S_selected = S_mutate_saved[.ORIGIN = (pmagicmethodcall.SITE)]
S_selected.CURRENT = S_front.CURRENT /\ S_selected.STORE[n_first_cell] = DEFINED (PINT 7)
$magic_method_capture(S_selected,pmagicmethodcall) /\ $magic_method_raw_valid(S_selected,pmagicmethodcall)
$magic_method_scoped_source(S_mutate,pmagicmethodcall) /\ $magic_method_descriptor(S_mutate,pmagicmethodcall)
$call_selected_valid(S_selected,MAGIC_METHOD_SEND_TARGET pmagicmethodcall,(pmagicmethodcall.SITE))
$heap_owners($heap_graph(S_mutate),HOBJECT n_child) = 2 /\ $sc_guard(S_mutate)
S_before_pack = S_mutate
'''.strip().splitlines()

PACK = r'''
S_pack_found = $sc_seek(S_before_pack,SC_PACK,1000)
S_pack_found.COMPLETION = NORMAL \/ S_pack_found.COMPLETION = BUDGET
S_pack = S_pack_found[.COMPLETION = NORMAL]
S_pack.CURRENT = S_front.CURRENT
S_pack.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps n_sent poperand_sent* (pmagicmethodcall.SITE) z_line) :: METHOD_RESULT :: ptask_tail*
n_sent = |phpType7_arguments*| /\ n_sent = |poperand_sent*|
$magic_method_values(S_pack,poperand_sent*) = (pvalue_sent*)
$target_function(S_pack,MAGIC_METHOD_SEND_TARGET pmagicmethodcall) = eps
~$call_parameter_reference(S_pack,MAGIC_METHOD_SEND_TARGET pmagicmethodcall,0)
$magic_method_raw_valid(S_pack,pmagicmethodcall) /\ $sc_guard(S_pack)
PhpStep: S_pack ~> S_packed_raw
S_packed_raw.TODO = (CALL_ARGS (MAGIC_METHOD_TARGET pmagicmethodcall n_array pvalue_sent*) eps 2 ([KNOWN (PSTRING pmagicmethodcall.NAME),KNOWN (PARRAY n_array)]) (pmagicmethodcall.SITE) z_line) :: METHOD_RESULT :: ptask_tail*
n_array = |S_pack.ARRAYS| /\ HARRAY n_array <- S_packed_raw.ALLOCATIONS
S_packed_raw.ARRAYS[n_array] = $magic_method_array(pvalue_sent*,0)
$heap_owners($heap_graph(S_packed_raw),HARRAY n_array) = 1
$magic_method_pending(S_packed_raw,pmagicmethodcall,n_array,pvalue_sent*) /\ $sc_guard(S_packed_raw)
S_packed = $sc_after(S_pack,S_packed_raw)
'''.strip().splitlines()

RECEIVE = r'''
S_receive_found = $sc_seek(S_packed,SC_RECEIVE pmagicmethodcall.METHOD,1000)
S_receive_found.COMPLETION = NORMAL \/ S_receive_found.COMPLETION = BUDGET
S_receive = S_receive_found[.COMPLETION = NORMAL]
S_receive.CURRENT = (pcallcontext_call)
pcallcontext_call.TARGET = MAGIC_METHOD_TARGET pmagicmethodcall n_array pvalue_sent*
pcallcontext_call.ARGC = 2 /\ pcallcontext_call.RECEIVER = (n_child) /\ pcallcontext_call.INSTANCE = eps
pcallcontext_call.LEXICAL_CLASS = (porigin_parent) /\ pcallcontext_call.CALLED_CLASS = (porigin_child)
$target_function(S_receive,pcallcontext_call.TARGET) = (pfunction_call) /\ $receiving_function(S_receive,pmagicmethodcall.METHOD) = (pfunction_call)
$lookup(S_receive.ENV,$ptascii("name")) = (n_name_cell)
$lookup(S_receive.ENV,$ptascii("arguments")) = (n_arguments_cell)
S_receive.STORE[n_name_cell] = DEFINED (PSTRING $ptascii("MiSsInG")) /\ S_receive.STORE[n_arguments_cell] = DEFINED (PARRAY n_array)
$heap_owners($heap_graph(S_receive),HARRAY n_array) = 1 /\ $sc_guard(S_receive)
S_enter_found = $sc_seek(S_receive,SC_ENTER n_child_cell ptbytes_enter,1000)
S_enter_found.COMPLETION = NORMAL \/ S_enter_found.COMPLETION = BUDGET
S_enter = S_enter_found[.COMPLETION = NORMAL]
$sc_stage(S_enter,SC_ENTER n_child_cell ptbytes_enter)
S_enter.CURRENT = (pcallcontext_enter)
pcallcontext_enter.TARGET = MAGIC_METHOD_TARGET pmagicmethodcall n_array pvalue_sent*
S_enter.FRAMES = pframe_call :: pframe_run :: eps
S_caller_saved = $constant_frame_scope(S_enter,pframe_call,[pframe_run])
$magic_method_caller(S_caller_saved,pmagicmethodcall) /\ $magic_method_capture(S_caller_saved,pmagicmethodcall)
~$magic_method_capture(S_enter,pmagicmethodcall) /\ $magic_method_scoped_source(S_enter,pmagicmethodcall)
$magic_method_entered(S_enter,S_enter.CURRENT,S_enter.FRAMES,pmagicmethodcall,n_array,pvalue_sent*)
$heap_owners($heap_graph(S_enter),HOBJECT n_child) = 2 /\ $sc_guard(S_enter)
'''.strip().splitlines()

PAYLOAD = r'''
S_payload_found = $sc_seek(S_enter,SC_DTOR n_payload,1000)
S_payload_found.COMPLETION = NORMAL \/ S_payload_found.COMPLETION = BUDGET
S_payload = S_payload_found[.COMPLETION = NORMAL]
$sc_stage(S_payload,SC_DTOR n_payload) /\ $sc_output(S_payload.EVENTS) = ptbytes_enter
S_payload.CURRENT = (pcallcontext_payload)
$destructor_context_call(pcallcontext_payload,S_payload.CURRENT,S_payload.FRAMES) = (pdestructorcall_payload)
pdestructorcall_payload.FRAME = (pdestructionframe_call)
pdestructionframe_call.FUNCTION = pmagicmethodcall.METHOD /\ pdestructionframe_call.VALUE = KNOWN (PINT 7) /\ pdestructionframe_call.PENDING = eps
pdestructionframe_call.CALLER = S_front.CURRENT
~(HARRAY n_array <- S_payload.ALLOCATIONS) /\ HOBJECT n_payload <- S_payload.ALLOCATIONS
S_payload.STORE[n_child_cell] = DEFINED PNULL /\ $heap_owners($heap_graph(S_payload),HOBJECT n_child) = 2
$magic_method_scoped_source(S_payload,pmagicmethodcall) /\ $magic_method_descriptor(S_payload,pmagicmethodcall)
$sc_guard(S_payload)
S_before_inner = S_payload
'''.strip().splitlines()

INNER = r'''
S_inner_found = $sc_seek(S_before_inner,SC_INNER pcallcontext_run.FUNCTION,1000)
S_inner_found.COMPLETION = NORMAL \/ S_inner_found.COMPLETION = BUDGET
S_inner = S_inner_found[.COMPLETION = NORMAL]
S_inner.CURRENT = S_front.CURRENT /\ S_inner.FRAMES = pframe_run :: eps
S_inner.TODO = METHOD_RESULT :: ptask_tail*
S_inner.RESULT = KNOWN (PINT 7) /\ S_inner.STORE[n_result_cell] = DEFINED (PINT 42)
S_inner.STORE[n_child_cell] = DEFINED PNULL /\ S_inner.STORE[n_rhs_cell] = DEFINED (PINT 99)
~(HARRAY n_array <- S_inner.ALLOCATIONS) /\ $heap_owners($heap_graph(S_inner),HOBJECT n_child) = 1
$sc_output(S_inner.EVENTS) = ptbytes_before_a /\ $sc_guard(S_inner)
S_before_child = S_inner
'''.strip().splitlines()

CHILD = r'''
S_child_found = $sc_seek(S_before_child,SC_DTOR n_child,1000)
S_child_found.COMPLETION = NORMAL \/ S_child_found.COMPLETION = BUDGET
S_child = S_child_found[.COMPLETION = NORMAL]
$sc_stage(S_child,SC_DTOR n_child) /\ $sc_output(S_child.EVENTS) = ptbytes_before_child
S_child.CURRENT = (pcallcontext_child)
$destructor_context_call(pcallcontext_child,S_child.CURRENT,S_child.FRAMES) = (pdestructorcall_child)
pdestructorcall_child.FRAME = (pdestructionframe_run)
pdestructionframe_run.FUNCTION = pcallcontext_run.FUNCTION /\ pdestructionframe_run.CALLER = eps
S_child.STORE[n_result_cell] = DEFINED (PINT 42) /\ S_child.STORE[n_child_cell] = DEFINED PNULL
~(HARRAY n_array <- S_child.ALLOCATIONS) /\ $sc_guard(S_child)
'''.strip().splitlines()

RETURN = r'''
pdestructionframe_run.VALUE = KNOWN (PINT 7) /\ pdestructionframe_run.PENDING = eps
S_result_found = $sc_seek(S_child,SC_OUTER,1000)
S_result_found.COMPLETION = NORMAL \/ S_result_found.COMPLETION = BUDGET
S_result = S_result_found[.COMPLETION = NORMAL]
S_result.TODO = METHOD_RESULT :: ptask_main_tail*
S_result.CURRENT = eps /\ S_result.FRAMES = eps /\ S_result.RESULT = KNOWN (PINT 7)
S_result.STORE[n_result_cell] = DEFINED (PINT 42) /\ ~(HOBJECT n_child <- S_result.ALLOCATIONS)
$sc_guard(S_result)
S_end = S_result
'''.strip().splitlines()

THROW = r'''
pdestructionframe_run.PENDING = (n_error)
$throwable_live(S_child,n_error)
S_catch_found = $sc_seek(S_child,SC_CATCH,1000)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_try n_catch n_error) :: ptask_catch*
S_catch.STORE[n_result_cell] = DEFINED (PINT 42) /\ S_catch.STORE[n_error_cell] = DEFINED (POBJECT n_error)
~(HOBJECT n_payload <- S_catch.ALLOCATIONS) /\ ~(HOBJECT n_child <- S_catch.ALLOCATIONS)
$sc_guard(S_catch)
PhpStep: S_catch ~> S_catch_raw
$lookup(S_catch_raw.ENV,$ptascii("caught")) = (n_caught_cell)
S_catch_raw.STORE[n_caught_cell] = DEFINED (POBJECT n_error)
S_end = $sc_after(S_catch,S_catch_raw)
'''.strip().splitlines()

FINISH = r'''
S_final = $drive_steps(S_end,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$sc_output(S_final.EVENTS) = ptbytes_final /\ $sc_guard(S_final)
~(HOBJECT n_child <- S_final.ALLOCATIONS) /\ ~(HARRAY n_array <- S_final.ALLOCATIONS)
S_budget = $drive_steps(S_front,0)
S_budget.COMPLETION = BUDGET /\ S_budget.TODO = S_front.TODO /\ S_budget.EVENTS = S_front.EVENTS
$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final
'''.strip().splitlines()

DERIVED = r'''
S_wrong_line = S_front[.TODO = (SCOPED_CLASS phpType19_self phpType20_missing phpType7_arguments* $(z_line + 1)) :: ptask_tail*]
PhpStep: S_wrong_line ~> S_wrong_line_done
S_wrong_line_done.COMPLETION = UNSUPPORTED "scoped magic method fallback"
S_wrong_line_done.EVENTS = S_front.EVENTS /\ S_wrong_line_done.STORE = S_front.STORE /\ S_wrong_line_done.ALLOCATIONS = S_front.ALLOCATIONS
pcallcontext_wrong = pcallcontext_run[.FUNCTION = pmagicmethodcall.METHOD][.TARGET = METHOD_TARGET n_child pmagicmethodcall.METHOD]
~$magic_method_scoped_source(S_front,pmagicmethodcall[.CALLER = (pcallcontext_wrong)])
~$magic_method_scoped_source(S_front,pmagicmethodcall[.CALLER = (pcallcontext_run[.RECEIVER = eps])])
~$magic_method_scoped_source(S_front,pmagicmethodcall[.LINE = $(z_line + 1)])
~$magic_method_scoped_source(S_front,pmagicmethodcall[.NAME = $ptascii("missing")])
S_ref = S_front[.REFCELLS = n_first_cell :: S_front.REFCELLS]
~$magic_method_capture(S_ref,pmagicmethodcall)
$magic_method_plan(S_ref,n_child,pmagicmethodcall.NAME,phpType7_arguments*,z_line) = eps
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', action='append', choices=('selection', 'owning', 'throwing'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_scoped_call_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_gate_completed']
    assert [case['id'] for case in data['cases']] == ['selection', 'owning', 'throwing', 'static']
    selected = [case for case in data['cases'] if case['id'] in ('selection', 'owning', 'throwing')]
    assert len(selected) == 3
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
    out = Path(tempfile.mkdtemp(prefix='magic-scoped-call-protocol-', dir=ROOT / '.tools'))
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
            enter_output = {'selection':'N:B|M|I|MiSsInG|7|2|ScopedParent107|ScopedChild107|', 'owning':'O:B|I|MiSsInG|', 'throwing':'X:B|I|MiSsInG|'}[name]
            before_a = enter_output + ('' if name == 'selection' else 'P|')
            setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $sc_seek(S_initial,SC_FRONT,1000)', r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S_front = S_found[.COMPLETION = NORMAL]',
                     'ptbytes_enter = $ptascii(' + json.dumps(enter_output) + ')',
                     'ptbytes_before_a = $ptascii(' + json.dumps(before_a) + ')',
                     'ptbytes_before_child = $ptascii(' + json.dumps(before_a + ('' if name == 'throwing' else 'A|')) + ')',
                     'ptbytes_final = $ptascii(' + json.dumps(output) + ')']
            reached = setup + COMMON + (SELECTION if name == 'selection' else ['S_before_pack = S_raw']) + PACK
            if name == 'selection':
                reached += ['pvalue_sent* = [PINT 7,PINT 2]', '$entry_lookup(S_packed_raw.ARRAYS[n_array].ITEMS,KINT 0) = (DIRECT (PINT 7))', '$entry_lookup(S_packed_raw.ARRAYS[n_array].ITEMS,KINT 1) = (DIRECT (PINT 2))']
            else:
                reached += ['pvalue_sent* = [POBJECT n_payload]', 'n_payload =/= n_child', 'S_pack.OBJECTS[n_payload] = INSTANCE porigin_payload', '$node_children(S_pack,HOBJECT n_payload) = eps', '$entry_lookup(S_packed_raw.ARRAYS[n_array].ITEMS,KINT 0) = (DIRECT (POBJECT n_payload))', r'$heap_owners($heap_graph(S_pack),HOBJECT n_payload) = 1 /\ $heap_owners($heap_graph(S_packed_raw),HOBJECT n_payload) = 1']
            reached += RECEIVE
            if name == 'selection':
                reached += ['S_enter.STORE[n_rhs_cell] = DEFINED (PINT 99)', 'S_before_inner = S_enter'] + INNER + CHILD + RETURN
            else:
                if name == 'throwing':
                    reached += ['$lookup(S_main.ENV,$ptascii("error")) = (n_error_cell)', 'S_front.STORE[n_error_cell] = DEFINED (POBJECT n_error)']
                reached += PAYLOAD
                if name == 'owning':
                    reached += INNER + ['~(HOBJECT n_payload <- S_inner.ALLOCATIONS)'] + CHILD + RETURN
                else:
                    reached += ['S_before_child = S_payload'] + CHILD + ['~(HOBJECT n_payload <- S_child.ALLOCATIONS)'] + THROW
            reached += FINISH + [f'pmagicmethodcall.LINE = {case["call_line"]}']
            derived = DERIVED if name == 'selection' else []
            content = PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
            for condition in reached + derived:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $main() = false -- otherwise\n'
            fixture = directory / 'hook.watsup'
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
