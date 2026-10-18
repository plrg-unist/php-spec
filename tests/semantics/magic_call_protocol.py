"""Check selected missing instance calls and real argument-array cleanup."""
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
syntax pmagiccallstage = MC_RAW | MC_PACK | MC_RECEIVE porigin | MC_OUTPUT ptbytes | MC_DTOR nat | MC_RESULT | MC_RAISED | MC_CATCH
dec $mc_output(pevent*) : ptbytes
def $mc_output(eps) = eps
def $mc_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $mc_output(pevent*)
dec $mc_stage(pstate,pmagiccallstage) : bool
def $mc_stage(S,MC_RAW) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) phpType7* 0 eps porigin? z) :: ptask*
def $mc_stage(S,MC_PACK) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps n poperand* porigin? z) :: ptask*
def $mc_stage(S,MC_RECEIVE porigin) = true
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: ptask*
def $mc_stage(S,MC_OUTPUT ptbytes) = true
  -- if S.CURRENT =/= eps
  -- if $mc_output(S.EVENTS) = ptbytes
def $mc_stage(S,MC_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $mc_stage(S,MC_RESULT) = true
  -- if S.CURRENT = eps
  -- if S.TODO = METHOD_RESULT :: ptask*
def $mc_stage(S,MC_RAISED) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $magic_method_target(pcallcontext.TARGET)
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
def $mc_stage(S,MC_CATCH) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask*
def $mc_stage(S,pmagiccallstage) = false -- otherwise
dec $mc_seek(pstate,pmagiccallstage,nat) : pstate
def $mc_seek(S,pmagiccallstage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $mc_stage(S,pmagiccallstage) \/ n = 0
def $mc_seek(S,pmagiccallstage,n) = $mc_seek($drive_steps(S[.COMPLETION = NORMAL],1),pmagiccallstage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$mc_stage(S,pmagiccallstage) /\ $(n > 0)
def $mc_seek(S,pmagiccallstage,n) = $mc_seek($drive_steps(S,1),pmagiccallstage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $mc_seek(S,pmagiccallstage,n) = S -- otherwise
dec $mc_after(pstate,pstate) : pstate
def $mc_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $mc_guard(pstate) : bool
def $mc_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $gc_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''

COMMON = r'''
S_raw.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) phpType7_arguments* 0 eps (porigin_site) z_line) :: METHOD_RESULT :: ptask_tail*
porigin_site = pmagicmethodcall.SITE /\ z_line = pmagicmethodcall.LINE
pmagicmethodcall.ARGUMENTS = phpType7_arguments* /\ pmagicmethodcall.TAIL = ptask_tail* /\ pmagicmethodcall.CALLER = eps /\ pmagicmethodcall.OWNER = 0
pmagicmethodcall.NAME = $ptascii("MiSsInG")
n_child = pmagicmethodcall.OBJECT
$lookup(S_raw.ENV,$ptascii("child")) = (n_child_cell)
$lookup(S_raw.ENV,$ptascii("answer")) = (n_answer_cell)
S_raw.STORE[n_child_cell] = DEFINED (POBJECT n_child) /\ S_raw.STORE[n_answer_cell] = DEFINED (PINT 42)
$magic_method_capture(S_raw,pmagicmethodcall) /\ $magic_method_raw_valid(S_raw,pmagicmethodcall)
$effective_method(S_raw,pmagicmethodcall.CLASS,pmagicmethodcall.NAME,|S_raw.CLASSES|) = eps
$effective_method(S_raw,pmagicmethodcall.CLASS,$ptascii("__call"),|S_raw.CLASSES|) = (pmethoddesc_call)
pfunction_call = pmethoddesc_call.FUNCTION
$magic_method_source(S_raw,pmethoddesc_call) /\ $ppmethod_call_signature(pfunction_call.SIGNATURE)
$target_nodes(MAGIC_METHOD_SEND_TARGET pmagicmethodcall) = [HOBJECT n_child]
$target_function(S_raw,MAGIC_METHOD_SEND_TARGET pmagicmethodcall) = eps
~$call_parameter_reference(S_raw,MAGIC_METHOD_SEND_TARGET pmagicmethodcall,0) /\ ~$call_parameter_reference(S_raw,MAGIC_METHOD_SEND_TARGET pmagicmethodcall,1)
$heap_owners($heap_graph(S_raw),HOBJECT n_child) = 2
$mc_guard(S_raw)
'''.strip().splitlines()

SNAPSHOT = r'''
$lookup(S_raw.ENV,$ptascii("rhs")) = (n_rhs_cell)
S_raw.STORE[n_rhs_cell] = DEFINED (PINT 7) /\ ~(n_rhs_cell <- S_raw.REFCELLS)
S_mutate_found = $mc_seek(S_raw,MC_OUTPUT $ptascii("N:A|"),1000)
S_mutate_found.COMPLETION = NORMAL \/ S_mutate_found.COMPLETION = BUDGET
S_mutate = S_mutate_found[.COMPLETION = NORMAL]
S_mutate.STORE[n_child_cell] = DEFINED PNULL /\ S_mutate.STORE[n_rhs_cell] = DEFINED (PINT 99)
S_mutate.FRAMES = pframe_mutate :: eps
S_mutate_saved = $constant_frame_scope(S_mutate,pframe_mutate,eps)
S_mutate_saved.TODO = (ORIGIN_RETURN (pmagicmethodcall.SITE)) :: (CALL_SEND (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 1 ([KNOWN (PINT 7)]) (pmagicmethodcall.SITE) pmagicmethodcall.LINE) :: METHOD_RESULT :: ptask_tail*
S_selected = S_mutate_saved[.ORIGIN = (pmagicmethodcall.SITE)]
$magic_method_raw_valid(S_selected,pmagicmethodcall) /\ ~$magic_method_capture(S_selected,pmagicmethodcall)
$call_selected_valid(S_selected,MAGIC_METHOD_SEND_TARGET pmagicmethodcall,(pmagicmethodcall.SITE))
$heap_owners($heap_graph(S_mutate),HOBJECT n_child) = 1 /\ $mc_guard(S_mutate)
S_before_pack = S_mutate
'''.strip().splitlines()

PACK = r'''
S_pack_found = $mc_seek(S_before_pack,MC_PACK,1000)
S_pack_found.COMPLETION = NORMAL \/ S_pack_found.COMPLETION = BUDGET
S_pack = S_pack_found[.COMPLETION = NORMAL]
S_pack.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps n_sent poperand_sent* (pmagicmethodcall.SITE) pmagicmethodcall.LINE) :: METHOD_RESULT :: ptask_tail*
n_sent = |phpType7_arguments*| /\ n_sent = |poperand_sent*|
$magic_method_values(S_pack,poperand_sent*) = (pvalue_sent*)
$magic_method_raw_valid(S_pack,pmagicmethodcall) /\ $mc_guard(S_pack)
PhpStep: S_pack ~> S_packed_raw
S_packed_raw.TODO = (CALL_ARGS (MAGIC_METHOD_TARGET pmagicmethodcall n_array pvalue_sent*) eps 2 ([KNOWN (PSTRING pmagicmethodcall.NAME),KNOWN (PARRAY n_array)]) (pmagicmethodcall.SITE) pmagicmethodcall.LINE) :: METHOD_RESULT :: ptask_tail*
n_array = |S_pack.ARRAYS| /\ HARRAY n_array <- S_packed_raw.ALLOCATIONS
S_packed_raw.ARRAYS[n_array] = $magic_method_array(pvalue_sent*,0)
S_packed_raw.ARRAYS[n_array].SERIAL = n_sent /\ S_packed_raw.ARRAYS[n_array].NEXT = n_sent
$target_nodes(MAGIC_METHOD_TARGET pmagicmethodcall n_array pvalue_sent*) = [HOBJECT n_child]
$heap_owners($heap_graph(S_packed_raw),HARRAY n_array) = 1
$magic_method_pending(S_packed_raw,pmagicmethodcall,n_array,pvalue_sent*) /\ $mc_guard(S_packed_raw)
$target_function(S_packed_raw,MAGIC_METHOD_TARGET pmagicmethodcall n_array pvalue_sent*) = (pfunction_call)
$named_call_shape(S_packed_raw,MAGIC_METHOD_TARGET pmagicmethodcall n_array pvalue_sent*,(pmagicmethodcall.SITE)) = {SLOTS ([NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN PNULL)]),NAMED eps}
S_packed = $mc_after(S_pack,S_packed_raw)
'''.strip().splitlines()

RECEIVE = r'''
S_receive_found = $mc_seek(S_packed,MC_RECEIVE pmagicmethodcall.METHOD,1000)
S_receive_found.COMPLETION = NORMAL \/ S_receive_found.COMPLETION = BUDGET
S_receive = S_receive_found[.COMPLETION = NORMAL]
S_receive.CURRENT = (pcallcontext_call)
pcallcontext_call.TARGET = MAGIC_METHOD_TARGET pmagicmethodcall n_array pvalue_sent*
pcallcontext_call.ARGC = 2 /\ pcallcontext_call.INSTANCE = eps /\ pcallcontext_call.RECEIVER = (n_child)
pcallcontext_call.LEXICAL_CLASS = (pmethoddesc_call.OWNER) /\ pcallcontext_call.CALLED_CLASS = (pmagicmethodcall.CLASS)
$target_function(S_receive,pcallcontext_call.TARGET) = (pfunction_call) /\ $receiving_function(S_receive,pmagicmethodcall.METHOD) = (pfunction_call)
$lookup(S_receive.ENV,$ptascii("name")) = (n_name_cell)
$lookup(S_receive.ENV,$ptascii("arguments")) = (n_arguments_cell)
S_receive.STORE[n_name_cell] = DEFINED (PSTRING $ptascii("MiSsInG")) /\ S_receive.STORE[n_arguments_cell] = DEFINED (PARRAY n_array)
$heap_owners($heap_graph(S_receive),HARRAY n_array) = 1 /\ $mc_guard(S_receive)
S_enter_found = $mc_seek(S_receive,MC_OUTPUT ptbytes_enter,1000)
S_enter_found.COMPLETION = NORMAL \/ S_enter_found.COMPLETION = BUDGET
S_enter = S_enter_found[.COMPLETION = NORMAL]
S_enter.CURRENT = (pcallcontext_enter)
pcallcontext_enter.TARGET = MAGIC_METHOD_TARGET pmagicmethodcall n_array pvalue_sent*
S_enter.STORE[n_child_cell] = DEFINED PNULL
$heap_owners($heap_graph(S_enter),HOBJECT n_child) = 1 /\ $mc_guard(S_enter)
S_enter.FRAMES = pframe_call :: eps
S_caller_saved = $constant_frame_scope(S_enter,pframe_call,eps)
$magic_method_caller(S_caller_saved,pmagicmethodcall) /\ ~$magic_method_capture(S_caller_saved,pmagicmethodcall)
$magic_method_entered(S_enter,S_enter.CURRENT,S_enter.FRAMES,pmagicmethodcall,n_array,pvalue_sent*)
'''.strip().splitlines()

PAYLOAD = r'''
S_payload_found = $mc_seek(S_cleanup,MC_DTOR n_payload,1000)
S_payload_found.COMPLETION = NORMAL \/ S_payload_found.COMPLETION = BUDGET
S_payload = S_payload_found[.COMPLETION = NORMAL]
$mc_stage(S_payload,MC_DTOR n_payload) /\ $mc_output(S_payload.EVENTS) = ptbytes_enter
~(HARRAY n_array <- S_payload.ALLOCATIONS) /\ HOBJECT n_payload <- S_payload.ALLOCATIONS
HOBJECT n_child <- S_payload.ALLOCATIONS /\ $heap_owners($heap_graph(S_payload),HOBJECT n_child) = 1
S_payload.STORE[n_child_cell] = DEFINED PNULL /\ $mc_guard(S_payload)
S_before_child = S_payload
'''.strip().splitlines()

CHILD = r'''
S_child_found = $mc_seek(S_before_child,MC_DTOR n_child,1000)
S_child_found.COMPLETION = NORMAL \/ S_child_found.COMPLETION = BUDGET
S_child = S_child_found[.COMPLETION = NORMAL]
$mc_stage(S_child,MC_DTOR n_child) /\ $mc_output(S_child.EVENTS) = ptbytes_before_child
~(HARRAY n_array <- S_child.ALLOCATIONS) /\ S_child.STORE[n_child_cell] = DEFINED PNULL
$mc_guard(S_child)
'''.strip().splitlines()

RETURN = r'''
S_result_found = $mc_seek(S_child,MC_RESULT,1000)
S_result_found.COMPLETION = NORMAL \/ S_result_found.COMPLETION = BUDGET
S_result = S_result_found[.COMPLETION = NORMAL]
S_result.TODO = METHOD_RESULT :: ptask_tail*
S_result.RESULT = KNOWN (PINT 7) /\ S_result.CURRENT = eps /\ S_result.FRAMES = eps
~(HOBJECT n_child <- S_result.ALLOCATIONS) /\ ~(HARRAY n_array <- S_result.ALLOCATIONS)
S_result.STORE[n_answer_cell] = DEFINED (PINT 42) /\ $mc_guard(S_result)
S_end = S_result
'''.strip().splitlines()

THROW_START = r'''
$lookup(S_raw.ENV,$ptascii("error")) = (n_error_cell)
S_raw.STORE[n_error_cell] = DEFINED (POBJECT n_error)
S_raised_found = $mc_seek(S_enter,MC_RAISED,1000)
S_raised_found.COMPLETION = NORMAL \/ S_raised_found.COMPLETION = BUDGET
S_raised = S_raised_found[.COMPLETION = NORMAL]
S_raised.TODO = (THROW_SEARCH n_error) :: ptask_throw*
S_raised.CURRENT = (pcallcontext_raised)
pcallcontext_raised.TARGET = MAGIC_METHOD_TARGET pmagicmethodcall n_array pvalue_sent*
$throwable_live(S_raised,n_error) /\ S_raised.STORE[n_answer_cell] = DEFINED (PINT 42) /\ $mc_guard(S_raised)
S_cleanup = S_raised
'''.strip().splitlines()

THROW_END = r'''
$throwable_live(S_payload,n_error) /\ $throwable_live(S_child,n_error)
S_catch_found = $mc_seek(S_child,MC_CATCH,1000)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_try n_catch n_error) :: ptask_catch*
S_catch.STORE[n_answer_cell] = DEFINED (PINT 42) /\ $throwable_live(S_catch,n_error)
~(HOBJECT n_payload <- S_catch.ALLOCATIONS) /\ ~(HOBJECT n_child <- S_catch.ALLOCATIONS) /\ ~(HARRAY n_array <- S_catch.ALLOCATIONS)
$mc_guard(S_catch)
PhpStep: S_catch ~> S_catch_raw
$lookup(S_catch_raw.ENV,$ptascii("caught")) = (n_caught_cell)
S_catch_raw.STORE[n_caught_cell] = DEFINED (POBJECT n_error)
S_end = $mc_after(S_catch,S_catch_raw)
'''.strip().splitlines()

FINISH = r'''
S_final = $drive_steps(S_end,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$mc_output(S_final.EVENTS) = ptbytes_final
~(HOBJECT n_child <- S_final.ALLOCATIONS) /\ ~(HARRAY n_array <- S_final.ALLOCATIONS) /\ $mc_guard(S_final)
S_budget = $drive_steps(S_packed,0)
S_budget.COMPLETION = BUDGET /\ S_budget.TODO = S_packed.TODO /\ S_budget.EVENTS = S_packed.EVENTS
$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final
'''.strip().splitlines()

DERIVED = r'''
~$magic_method_source(S_raw[.SOURCES = eps],pmethoddesc_call)
~$ppmethod_call_signature(pfunction_call.SIGNATURE[.RETURNS = [PTBRANCH ([PTBUILTIN "int"])]])
pmagicmethodcall_wrong_name = pmagicmethodcall[.NAME = $ptascii("missing")]
~$magic_method_descriptor(S_raw,pmagicmethodcall_wrong_name)
pmagicmethodcall_wrong_line = pmagicmethodcall[.LINE = $(pmagicmethodcall.LINE + 1)]
~$magic_method_descriptor(S_raw,pmagicmethodcall_wrong_line)
S_wrong_count = S_pack[.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps $(n_sent + 1) poperand_sent* (pmagicmethodcall.SITE) pmagicmethodcall.LINE) :: METHOD_RESULT :: ptask_tail*]
PhpStep: S_wrong_count ~> S_wrong_count_done
S_wrong_count_done.COMPLETION = UNSUPPORTED "magic method send continuation"
S_wrong_value = S_pack[.TODO = (CALL_ARGS (MAGIC_METHOD_SEND_TARGET pmagicmethodcall) eps 2 ([KNOWN (PINT 7),KNOWN PNULL]) (pmagicmethodcall.SITE) pmagicmethodcall.LINE) :: METHOD_RESULT :: ptask_tail*]
PhpStep: S_wrong_value ~> S_wrong_value_done
S_wrong_value_done.COMPLETION = UNSUPPORTED "magic method send continuation"
parray_packed = S_packed_raw.ARRAYS[n_array]
S_wrong_array = S_packed_raw[.ARRAYS[n_array] = $array_insert(parray_packed,KINT 0,DIRECT (PINT 99))]
~$magic_method_pending(S_wrong_array,pmagicmethodcall,n_array,pvalue_sent*)
$target_function(S_wrong_array,MAGIC_METHOD_TARGET pmagicmethodcall n_array pvalue_sent*) = eps
S_ref = S_raw[.REFCELLS = n_rhs_cell :: S_raw.REFCELLS]
~$magic_method_capture(S_ref,pmagicmethodcall)
$magic_method_plan(S_ref,n_child,pmagicmethodcall.NAME,phpType7_arguments*,pmagicmethodcall.LINE) = eps
$magic_method_scoped(S_enter,pmethoddesc_call.OWNER)
~$magic_method_scoped(S_raw,pmethoddesc_call.OWNER)
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', choices=('snapshot', 'owning', 'throwing'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_call_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_gate_completed']
    assert [case['id'] for case in data['cases']] == ['snapshot', 'owning', 'throwing', 'public']
    selected = [case for case in data['cases'] if case['id'] in ('snapshot', 'owning', 'throwing')]
    assert len(selected) == 3
    if args.case:
        selected = [case for case in selected if case['id'] == args.case]
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
    out = Path(tempfile.mkdtemp(prefix='magic-call-protocol-', dir=ROOT / '.tools'))
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
            enter_output = {'snapshot':'N:A|M|MiSsInG|41|7|2|m|', 'owning':'O:M|MiSsInG|41|A|m|', 'throwing':'X:M|MiSsInG|41|A|m|'}[name]
            setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $mc_seek(S_initial,MC_RAW,1000)', r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S_raw = S_found[.COMPLETION = NORMAL]',
                     'ptbytes_enter = $ptascii(' + json.dumps(enter_output) + ')',
                     'ptbytes_before_child = $ptascii(' + json.dumps(enter_output + ('' if name == 'snapshot' else 'P|K|p|')) + ')',
                     'ptbytes_final = $ptascii(' + json.dumps(output) + ')']
            reached = setup + COMMON + (SNAPSHOT if name == 'snapshot' else ['S_before_pack = S_raw']) + PACK
            if name == 'snapshot':
                reached += ['pvalue_sent* = [PINT 7,PINT 2]', '$entry_lookup(S_packed_raw.ARRAYS[n_array].ITEMS,KINT 0) = (DIRECT (PINT 7))', '$entry_lookup(S_packed_raw.ARRAYS[n_array].ITEMS,KINT 1) = (DIRECT (PINT 2))']
            else:
                reached += ['pvalue_sent* = [POBJECT n_payload]', 'n_payload =/= n_child', 'S_pack.OBJECTS[n_payload] = INSTANCE porigin_payload', '$node_children(S_pack,HOBJECT n_payload) = eps', '$entry_lookup(S_packed_raw.ARRAYS[n_array].ITEMS,KINT 0) = (DIRECT (POBJECT n_payload))', r'$heap_owners($heap_graph(S_pack),HOBJECT n_payload) = 1 /\ $heap_owners($heap_graph(S_packed_raw),HOBJECT n_payload) = 1']
            reached += RECEIVE
            if name == 'snapshot':
                reached += ['S_enter.STORE[n_rhs_cell] = DEFINED (PINT 99)', '$entry_lookup(S_enter.ARRAYS[n_array].ITEMS,KINT 0) = (DIRECT (PINT 7))', 'S_before_child = S_enter'] + CHILD + RETURN
            else:
                reached += (THROW_START if name == 'throwing' else ['S_cleanup = S_enter']) + PAYLOAD + CHILD
                reached += ['~(HOBJECT n_payload <- S_child.ALLOCATIONS)']
                reached += (THROW_END if name == 'throwing' else RETURN)
            reached += FINISH + [f'pmagicmethodcall.LINE = {case["call_line"]}']
            derived = DERIVED if name == 'snapshot' else []
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
