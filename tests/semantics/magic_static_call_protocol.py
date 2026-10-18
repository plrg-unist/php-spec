"""Check selected missing static calls and real argument-array cleanup."""
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
syntax pmagicstaticcallstage = MSC_RAW | MSC_PACK | MSC_RECEIVE porigin | MSC_OUTPUT ptbytes | MSC_DTOR nat | MSC_RESULT | MSC_RAISED | MSC_CATCH
dec $msc_output(pevent*) : ptbytes
def $msc_output(eps) = eps
def $msc_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $msc_output(pevent*)
dec $msc_stage(pstate,pmagicstaticcallstage) : bool
def $msc_stage(S,MSC_RAW) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_ARGS (MAGIC_STATIC_METHOD_SEND_TARGET pmagicstaticmethodcall) phpType7* 0 eps porigin? z) :: ptask*
def $msc_stage(S,MSC_PACK) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CALL_ARGS (MAGIC_STATIC_METHOD_SEND_TARGET pmagicstaticmethodcall) eps n poperand* porigin? z) :: ptask*
def $msc_stage(S,MSC_RECEIVE porigin) = true
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: ptask*
def $msc_stage(S,MSC_OUTPUT ptbytes) = true
  -- if S.CURRENT =/= eps
  -- if $msc_output(S.EVENTS) = ptbytes
def $msc_stage(S,MSC_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $msc_stage(S,MSC_RESULT) = true
  -- if S.CURRENT = eps
  -- if S.TODO = METHOD_RESULT :: ptask*
def $msc_stage(S,MSC_RAISED) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $magic_method_target(pcallcontext.TARGET)
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
def $msc_stage(S,MSC_CATCH) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask*
def $msc_stage(S,pmagicstaticcallstage) = false -- otherwise
dec $msc_seek(pstate,pmagicstaticcallstage,nat) : pstate
def $msc_seek(S,pmagicstaticcallstage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $msc_stage(S,pmagicstaticcallstage) \/ n = 0
def $msc_seek(S,pmagicstaticcallstage,n) = $msc_seek($drive_steps(S[.COMPLETION = NORMAL],1),pmagicstaticcallstage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$msc_stage(S,pmagicstaticcallstage) /\ $(n > 0)
def $msc_seek(S,pmagicstaticcallstage,n) = $msc_seek($drive_steps(S,1),pmagicstaticcallstage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $msc_seek(S,pmagicstaticcallstage,n) = S -- otherwise
dec $msc_after(pstate,pstate) : pstate
def $msc_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $msc_guard(pstate) : bool
def $msc_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $gc_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''

COMMON = r'''
S_raw.TODO = (CALL_ARGS (MAGIC_STATIC_METHOD_SEND_TARGET pmagicstaticmethodcall) phpType7_arguments* 0 eps (porigin_site) z_line) :: METHOD_RESULT :: ptask_tail*
porigin_site = pmagicstaticmethodcall.SITE /\ z_line = pmagicstaticmethodcall.LINE
pmagicstaticmethodcall.ARGUMENTS = phpType7_arguments* /\ pmagicstaticmethodcall.TAIL = ptask_tail* /\ pmagicstaticmethodcall.CALLER = eps /\ pmagicstaticmethodcall.OWNER = 0
pmagicstaticmethodcall.NAME = $ptascii("MiSsInG")
$lookup(S_raw.ENV,$ptascii("answer")) = (n_answer_cell)
S_raw.STORE[n_answer_cell] = DEFINED (PINT 42)
$magic_static_method_capture(S_raw,pmagicstaticmethodcall) /\ $magic_static_method_raw_valid(S_raw,pmagicstaticmethodcall)
$magic_static_method_needed(S_raw,pmagicstaticmethodcall.CLASS) /\ ~$magic_method_scoped(S_raw,pmagicstaticmethodcall.CLASS)
$effective_method(S_raw,pmagicstaticmethodcall.CLASS,pmagicstaticmethodcall.NAME,|S_raw.CLASSES|) = eps
$effective_method(S_raw,pmagicstaticmethodcall.CLASS,$ptascii("__callstatic"),|S_raw.CLASSES|) = (pmethoddesc_call)
pfunction_call = pmethoddesc_call.FUNCTION
$magic_static_method_source(S_raw,pmethoddesc_call) /\ $ppmethod_call_signature(pfunction_call.SIGNATURE)
$target_nodes(MAGIC_STATIC_METHOD_SEND_TARGET pmagicstaticmethodcall) = eps
$target_function(S_raw,MAGIC_STATIC_METHOD_SEND_TARGET pmagicstaticmethodcall) = eps
~$call_parameter_reference(S_raw,MAGIC_STATIC_METHOD_SEND_TARGET pmagicstaticmethodcall,0) /\ ~$call_parameter_reference(S_raw,MAGIC_STATIC_METHOD_SEND_TARGET pmagicstaticmethodcall,1)
$msc_guard(S_raw)
'''.strip().splitlines()

SNAPSHOT = r'''
$lookup(S_raw.ENV,$ptascii("rhs")) = (n_rhs_cell)
S_raw.STORE[n_rhs_cell] = DEFINED (PINT 7) /\ ~(n_rhs_cell <- S_raw.REFCELLS)
S_mutate_found = $msc_seek(S_raw,MSC_OUTPUT $ptascii("N:A|"),1000)
S_mutate_found.COMPLETION = NORMAL \/ S_mutate_found.COMPLETION = BUDGET
S_mutate = S_mutate_found[.COMPLETION = NORMAL]
S_mutate.STORE[n_rhs_cell] = DEFINED (PINT 99) /\ n_rhs_cell <- S_mutate.REFCELLS
S_mutate.FRAMES = pframe_mutate :: eps
S_mutate_saved = $constant_frame_scope(S_mutate,pframe_mutate,eps)
S_mutate_saved.TODO = (ORIGIN_RETURN (pmagicstaticmethodcall.SITE)) :: (CALL_SEND (MAGIC_STATIC_METHOD_SEND_TARGET pmagicstaticmethodcall) eps 1 ([KNOWN (PINT 7)]) (pmagicstaticmethodcall.SITE) pmagicstaticmethodcall.LINE) :: METHOD_RESULT :: ptask_tail*
S_selected = S_mutate_saved[.ORIGIN = (pmagicstaticmethodcall.SITE)]
$magic_static_method_raw_valid(S_selected,pmagicstaticmethodcall) /\ ~$magic_static_method_capture(S_selected,pmagicstaticmethodcall)
$call_selected_valid(S_selected,MAGIC_STATIC_METHOD_SEND_TARGET pmagicstaticmethodcall,(pmagicstaticmethodcall.SITE))
$target_nodes(MAGIC_STATIC_METHOD_SEND_TARGET pmagicstaticmethodcall) = eps /\ $msc_guard(S_mutate)
S_before_pack = S_mutate
'''.strip().splitlines()

PACK = r'''
S_pack_found = $msc_seek(S_before_pack,MSC_PACK,1000)
S_pack_found.COMPLETION = NORMAL \/ S_pack_found.COMPLETION = BUDGET
S_pack = S_pack_found[.COMPLETION = NORMAL]
S_pack.TODO = (CALL_ARGS (MAGIC_STATIC_METHOD_SEND_TARGET pmagicstaticmethodcall) eps n_sent poperand_sent* (pmagicstaticmethodcall.SITE) pmagicstaticmethodcall.LINE) :: METHOD_RESULT :: ptask_tail*
n_sent = |phpType7_arguments*| /\ n_sent = |poperand_sent*|
$magic_method_values(S_pack,poperand_sent*) = (pvalue_sent*)
$magic_static_method_raw_valid(S_pack,pmagicstaticmethodcall) /\ $msc_guard(S_pack)
PhpStep: S_pack ~> S_packed_raw
S_packed_raw.TODO = (CALL_ARGS (MAGIC_STATIC_METHOD_TARGET pmagicstaticmethodcall n_array pvalue_sent*) eps 2 ([KNOWN (PSTRING pmagicstaticmethodcall.NAME),KNOWN (PARRAY n_array)]) (pmagicstaticmethodcall.SITE) pmagicstaticmethodcall.LINE) :: METHOD_RESULT :: ptask_tail*
n_array = |S_pack.ARRAYS| /\ HARRAY n_array <- S_packed_raw.ALLOCATIONS
S_packed_raw.ARRAYS[n_array] = $magic_method_array(pvalue_sent*,0)
S_packed_raw.ARRAYS[n_array].SERIAL = n_sent /\ S_packed_raw.ARRAYS[n_array].NEXT = n_sent
$target_nodes(MAGIC_STATIC_METHOD_TARGET pmagicstaticmethodcall n_array pvalue_sent*) = eps
$heap_owners($heap_graph(S_packed_raw),HARRAY n_array) = 1
$magic_static_method_pending(S_packed_raw,pmagicstaticmethodcall,n_array,pvalue_sent*) /\ $msc_guard(S_packed_raw)
$target_function(S_packed_raw,MAGIC_STATIC_METHOD_TARGET pmagicstaticmethodcall n_array pvalue_sent*) = (pfunction_call)
$named_call_shape(S_packed_raw,MAGIC_STATIC_METHOD_TARGET pmagicstaticmethodcall n_array pvalue_sent*,(pmagicstaticmethodcall.SITE)) = {SLOTS ([NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN PNULL)]),NAMED eps}
S_packed = $msc_after(S_pack,S_packed_raw)
'''.strip().splitlines()

RECEIVE = r'''
S_receive_found = $msc_seek(S_packed,MSC_RECEIVE pmagicstaticmethodcall.METHOD,1000)
S_receive_found.COMPLETION = NORMAL \/ S_receive_found.COMPLETION = BUDGET
S_receive = S_receive_found[.COMPLETION = NORMAL]
S_receive.CURRENT = (pcallcontext_call)
pcallcontext_call.TARGET = MAGIC_STATIC_METHOD_TARGET pmagicstaticmethodcall n_array pvalue_sent*
pcallcontext_call.ARGC = 2 /\ pcallcontext_call.INSTANCE = eps /\ pcallcontext_call.RECEIVER = eps
pcallcontext_call.LEXICAL_CLASS = (pmethoddesc_call.OWNER) /\ pcallcontext_call.CALLED_CLASS = (pmagicstaticmethodcall.CLASS)
$target_nodes(pcallcontext_call.TARGET) = eps /\ $call_receiver_roots(pcallcontext_call) = eps
$target_function(S_receive,pcallcontext_call.TARGET) = (pfunction_call) /\ $receiving_function(S_receive,pmagicstaticmethodcall.METHOD) = (pfunction_call)
$lookup(S_receive.ENV,$ptascii("name")) = (n_name_cell)
$lookup(S_receive.ENV,$ptascii("arguments")) = (n_arguments_cell)
S_receive.STORE[n_name_cell] = DEFINED (PSTRING $ptascii("MiSsInG")) /\ S_receive.STORE[n_arguments_cell] = DEFINED (PARRAY n_array)
$heap_owners($heap_graph(S_receive),HARRAY n_array) = 1 /\ $msc_guard(S_receive)
S_enter_found = $msc_seek(S_receive,MSC_OUTPUT ptbytes_enter,1000)
S_enter_found.COMPLETION = NORMAL \/ S_enter_found.COMPLETION = BUDGET
S_enter = S_enter_found[.COMPLETION = NORMAL]
S_enter.CURRENT = (pcallcontext_enter)
pcallcontext_enter.TARGET = MAGIC_STATIC_METHOD_TARGET pmagicstaticmethodcall n_array pvalue_sent*
pcallcontext_enter.RECEIVER = eps /\ pcallcontext_enter.INSTANCE = eps /\ $msc_guard(S_enter)
S_enter.FRAMES = pframe_call :: eps
S_caller_saved = $constant_frame_scope(S_enter,pframe_call,eps)
$magic_static_method_caller(S_caller_saved,pmagicstaticmethodcall)
$magic_static_method_entered(S_enter,S_enter.CURRENT,S_enter.FRAMES,pmagicstaticmethodcall,n_array,pvalue_sent*)
'''.strip().splitlines()

PAYLOAD = r'''
S_payload_found = $msc_seek(S_cleanup,MSC_DTOR n_payload,1000)
S_payload_found.COMPLETION = NORMAL \/ S_payload_found.COMPLETION = BUDGET
S_payload = S_payload_found[.COMPLETION = NORMAL]
$msc_stage(S_payload,MSC_DTOR n_payload) /\ $msc_output(S_payload.EVENTS) = ptbytes_enter
~(HARRAY n_array <- S_payload.ALLOCATIONS) /\ HOBJECT n_payload <- S_payload.ALLOCATIONS
$target_nodes(MAGIC_STATIC_METHOD_TARGET pmagicstaticmethodcall n_array pvalue_sent*) = eps /\ $msc_guard(S_payload)
S_payload.DESTRUCTION.FRAMES = pdestructionframe_cached :: pdestructionframe_rest*
pdestructionframe_cached.FUNCTION = pmagicstaticmethodcall.METHOD
'''.strip().splitlines()

RETURN = r'''
S_result_found = $msc_seek(S_before_result,MSC_RESULT,1000)
S_result_found.COMPLETION = NORMAL \/ S_result_found.COMPLETION = BUDGET
S_result = S_result_found[.COMPLETION = NORMAL]
S_result.TODO = METHOD_RESULT :: ptask_tail*
S_result.RESULT = KNOWN (PINT 7) /\ S_result.CURRENT = eps /\ S_result.FRAMES = eps
~(HARRAY n_array <- S_result.ALLOCATIONS)
S_result.STORE[n_answer_cell] = DEFINED (PINT 42) /\ $msc_guard(S_result)
S_end = S_result
'''.strip().splitlines()

THROW_START = r'''
$lookup(S_raw.ENV,$ptascii("error")) = (n_error_cell)
S_raw.STORE[n_error_cell] = DEFINED (POBJECT n_error)
S_raised_found = $msc_seek(S_enter,MSC_RAISED,1000)
S_raised_found.COMPLETION = NORMAL \/ S_raised_found.COMPLETION = BUDGET
S_raised = S_raised_found[.COMPLETION = NORMAL]
S_raised.TODO = (THROW_SEARCH n_error) :: ptask_throw*
S_raised.CURRENT = (pcallcontext_raised)
pcallcontext_raised.TARGET = MAGIC_STATIC_METHOD_TARGET pmagicstaticmethodcall n_array pvalue_sent*
$throwable_live(S_raised,n_error) /\ S_raised.STORE[n_answer_cell] = DEFINED (PINT 42) /\ $msc_guard(S_raised)
S_cleanup = S_raised
'''.strip().splitlines()

THROW_END = r'''
$throwable_live(S_payload,n_error)
S_catch_found = $msc_seek(S_payload,MSC_CATCH,1000)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_try n_catch n_error) :: ptask_catch*
S_catch.STORE[n_answer_cell] = DEFINED (PINT 42) /\ $throwable_live(S_catch,n_error)
~(HOBJECT n_payload <- S_catch.ALLOCATIONS) /\ ~(HARRAY n_array <- S_catch.ALLOCATIONS)
$msc_guard(S_catch)
PhpStep: S_catch ~> S_catch_raw
$lookup(S_catch_raw.ENV,$ptascii("caught")) = (n_caught_cell)
S_catch_raw.STORE[n_caught_cell] = DEFINED (POBJECT n_error)
S_end = $msc_after(S_catch,S_catch_raw)
'''.strip().splitlines()

FINISH = r'''
S_final = $drive_steps(S_end,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$msc_output(S_final.EVENTS) = ptbytes_final
~(HARRAY n_array <- S_final.ALLOCATIONS) /\ $msc_guard(S_final)
S_budget = $drive_steps(S_packed,0)
S_budget.COMPLETION = BUDGET /\ S_budget.TODO = S_packed.TODO /\ S_budget.EVENTS = S_packed.EVENTS
$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final
'''.strip().splitlines()

DERIVED = r'''
~$magic_static_method_source(S_raw[.SOURCES = eps],pmethoddesc_call)
~$ppmethod_call_signature(pfunction_call.SIGNATURE[.RETURNS = [PTBRANCH ([PTBUILTIN "int"])]])
pmagicstaticmethodcall_wrong_name = pmagicstaticmethodcall[.NAME = $ptascii("missing")]
~$magic_static_method_descriptor(S_raw,pmagicstaticmethodcall_wrong_name)
pmagicstaticmethodcall_wrong_line = pmagicstaticmethodcall[.LINE = $(pmagicstaticmethodcall.LINE + 1)]
~$magic_static_method_descriptor(S_raw,pmagicstaticmethodcall_wrong_line)
S_wrong_count = S_pack[.TODO = (CALL_ARGS (MAGIC_STATIC_METHOD_SEND_TARGET pmagicstaticmethodcall) eps $(n_sent + 1) poperand_sent* (pmagicstaticmethodcall.SITE) pmagicstaticmethodcall.LINE) :: METHOD_RESULT :: ptask_tail*]
PhpStep: S_wrong_count ~> S_wrong_count_done
S_wrong_count_done.COMPLETION = UNSUPPORTED "magic static method send continuation"
S_wrong_value = S_pack[.TODO = (CALL_ARGS (MAGIC_STATIC_METHOD_SEND_TARGET pmagicstaticmethodcall) eps 2 ([KNOWN (PINT 7),KNOWN PNULL]) (pmagicstaticmethodcall.SITE) pmagicstaticmethodcall.LINE) :: METHOD_RESULT :: ptask_tail*]
PhpStep: S_wrong_value ~> S_wrong_value_done
S_wrong_value_done.COMPLETION = UNSUPPORTED "magic static method send continuation"
parray_packed = S_packed_raw.ARRAYS[n_array]
S_wrong_array = S_packed_raw[.ARRAYS[n_array] = $array_insert(parray_packed,KINT 0,DIRECT (PINT 99))]
~$magic_static_method_pending(S_wrong_array,pmagicstaticmethodcall,n_array,pvalue_sent*)
$target_function(S_wrong_array,MAGIC_STATIC_METHOD_TARGET pmagicstaticmethodcall n_array pvalue_sent*) = eps
S_ref = S_raw[.REFCELLS = n_rhs_cell :: S_raw.REFCELLS]
~$magic_static_method_capture(S_ref,pmagicstaticmethodcall)
$magic_static_method_plan(S_ref,pmagicstaticmethodcall.CLASS,pmagicstaticmethodcall.NAME,phpType7_arguments*,pmagicstaticmethodcall.LINE) = eps
S_enter.CLASSES = pclassdesc_parent :: pclassdesc_rest*
pclassdesc_parent.ORIGIN = pmethoddesc_call.OWNER
pmethoddesc_priority = pmethoddesc_call[.NAME = $ptascii("__call")][.STATIC = false]
pclassdesc_priority = pclassdesc_parent[.METHODS = pclassdesc_parent.METHODS ++ [pmethoddesc_priority]]
n_priority = |S_enter.OBJECTS|
S_priority = S_enter[.CLASSES = pclassdesc_priority :: pclassdesc_rest*][.OBJECTS = S_enter.OBJECTS ++ [INSTANCE pmagicstaticmethodcall.CLASS]][.ALLOCATIONS = S_enter.ALLOCATIONS ++ [HOBJECT n_priority]][.CURRENT = (pcallcontext_enter[.RECEIVER = (n_priority)])]
$magic_method_scoped(S_priority,pmagicstaticmethodcall.CLASS)
~$magic_static_method_needed(S_priority,pmagicstaticmethodcall.CLASS)
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', choices=('snapshot', 'owning', 'throwing'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_static_call_cases.json'
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
    out = Path(tempfile.mkdtemp(prefix='magic-static-call-protocol-', dir=ROOT / '.tools'))
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
            enter_output = {'snapshot':'N:A|M|MiSsInG|MagicStaticParent100|MagicStaticChild100|7|2|m|', 'owning':'O:M|MiSsInG|MagicStaticParent100|MagicStaticChild100|A|m|', 'throwing':'X:M|MiSsInG|MagicStaticParent100|MagicStaticChild100|A|m|'}[name]
            setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $msc_seek(S_initial,MSC_RAW,1000)', r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S_raw = S_found[.COMPLETION = NORMAL]',
                     'ptbytes_enter = $ptascii(' + json.dumps(enter_output) + ')',
                     'ptbytes_final = $ptascii(' + json.dumps(output) + ')']
            reached = setup + COMMON + (SNAPSHOT if name == 'snapshot' else ['S_before_pack = S_raw']) + PACK
            if name == 'snapshot':
                reached += ['pvalue_sent* = [PINT 7,PINT 2]', '$entry_lookup(S_packed_raw.ARRAYS[n_array].ITEMS,KINT 0) = (DIRECT (PINT 7))', '$entry_lookup(S_packed_raw.ARRAYS[n_array].ITEMS,KINT 1) = (DIRECT (PINT 2))']
            else:
                reached += ['pvalue_sent* = [POBJECT n_payload]', 'S_pack.OBJECTS[n_payload] = INSTANCE porigin_payload', '$node_children(S_pack,HOBJECT n_payload) = eps', '$entry_lookup(S_packed_raw.ARRAYS[n_array].ITEMS,KINT 0) = (DIRECT (POBJECT n_payload))', r'$heap_owners($heap_graph(S_pack),HOBJECT n_payload) = 1 /\ $heap_owners($heap_graph(S_packed_raw),HOBJECT n_payload) = 1']
            reached += RECEIVE
            if name == 'snapshot':
                reached += ['S_enter.STORE[n_rhs_cell] = DEFINED (PINT 99)', '$entry_lookup(S_enter.ARRAYS[n_array].ITEMS,KINT 0) = (DIRECT (PINT 7))', 'S_before_result = S_enter'] + RETURN
            else:
                reached += (THROW_START if name == 'throwing' else ['S_cleanup = S_enter']) + PAYLOAD
                reached += ['$lookup(S_raw.ENV,$ptascii("value")) = (n_value_cell)', 'S_payload.STORE[n_value_cell] = DEFINED (PINT 7)']
                if name == 'throwing':
                    reached += ['pdestructionframe_cached.PENDING = (n_error)'] + THROW_END + ['S_catch.STORE[n_value_cell] = DEFINED (PINT 99)']
                else:
                    reached += ['pdestructionframe_cached.PENDING = eps', 'pdestructionframe_cached.VALUE = KNOWN (PINT 7)', 'S_before_result = S_payload'] + RETURN
                    reached += ['S_result.STORE[n_value_cell] = DEFINED (PINT 99)', '~(HOBJECT n_payload <- S_result.ALLOCATIONS)']
            reached += FINISH + [f'pmagicstaticmethodcall.LINE = {case["call_line"]}']
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
