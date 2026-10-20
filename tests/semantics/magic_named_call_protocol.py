"""Check direct named magic calls, sent snapshots and retained named-table cleanup."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()
lines = lambda text: text.strip().splitlines()

PREFIX = r'''
syntax pmagicnamedstage = MN_RAW | MN_PACK | MN_RECEIVE porigin | MN_RETURN porigin int | MN_MARKER | MN_DTOR nat | MN_RESULT | MN_CATCH
dec $mn_output(pevent*) : ptbytes
def $mn_output(eps) = eps
def $mn_output((OUTPUT ptbytes) :: pevent_tail*) = ptbytes ++ $mn_output(pevent_tail*)
dec $mn_stage(pstate,pmagicnamedstage) : bool
def $mn_stage(S,MN_RAW) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (MAGIC_METHOD_NAMED_ARGS pmagicmethodcall 0 eps) :: ptask_tail*
def $mn_stage(S,MN_PACK) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (MAGIC_METHOD_NAMED_ARGS pmagicmethodcall n poperand_sent*) :: ptask_tail*
  -- if n = |pmagicmethodcall.ARGUMENTS|
def $mn_stage(S,MN_RECEIVE porigin) = true
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: ptask_tail*
def $mn_stage(S,MN_RETURN porigin i) = true
  -- if S.CURRENT = (pcallcontext_return)
  -- if pcallcontext_return.FUNCTION = porigin
  -- if S.TODO = (RETURN_UNWIND (KNOWN (PINT i)) porigin_return?) :: ptask_tail*
def $mn_stage(S,MN_MARKER) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (MAGIC_METHOD_NAMED_RESULT pmagicmethodcall n_arguments n_named pvalue_sent*) :: ptask_tail*
def $mn_stage(S,MN_DTOR n) = true
  -- if S.CURRENT = (pcallcontext_dtor)
  -- if $destructor_context_call(pcallcontext_dtor,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $mn_stage(S,MN_RESULT) = true
  -- if S.CURRENT = eps
  -- if S.TODO = METHOD_RESULT :: ptask_tail*
def $mn_stage(S,MN_CATCH) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CATCH_BIND porigin_try n_catch n_error) :: ptask_tail*
def $mn_stage(S,pmagicnamedstage) = false -- otherwise
dec $mn_seek(pstate,pmagicnamedstage,nat) : pstate
def $mn_seek(S,pmagicnamedstage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $mn_stage(S,pmagicnamedstage) \/ n = 0
def $mn_seek(S,pmagicnamedstage,n) = $mn_seek($drive_steps(S[.COMPLETION = NORMAL],1),pmagicnamedstage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$mn_stage(S,pmagicnamedstage) /\ $(n > 0)
def $mn_seek(S,pmagicnamedstage,n) = $mn_seek($drive_steps(S,1),pmagicnamedstage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $mn_seek(S,pmagicnamedstage,n) = S -- otherwise
dec $mn_after(pstate,pstate) : pstate
def $mn_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $mn_guard(pstate) : bool
def $mn_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $gc_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''

def reach(target, source, stage):
    return [f'{target}_found = $mn_seek({source},{stage},1000)',
            f'{target}_found.COMPLETION = NORMAL \\/ {target}_found.COMPLETION = BUDGET',
            f'{target} = {target}_found[.COMPLETION = NORMAL]',
            f'$mn_stage({target},{stage})']

COMMON = lines(r'''
S_raw.TODO = (MAGIC_METHOD_NAMED_ARGS pmagicmethodcall 0 eps) :: METHOD_RESULT :: ptask_outer_tail*
pmagicmethodcall.TAIL = ptask_outer_tail* /\ pmagicmethodcall.CALLER = eps /\ pmagicmethodcall.OWNER = 0
pmagicmethodcall.NAME = $ptascii("MiSs")
n_child = pmagicmethodcall.OBJECT
$lookup(S_raw.ENV,$ptascii("child")) = (n_child_cell)
S_raw.STORE[n_child_cell] = DEFINED (POBJECT n_child)
$magic_method_capture(S_raw,pmagicmethodcall) /\ $magic_method_raw_valid(S_raw,pmagicmethodcall)
$magic_named_source(S_raw,pmagicmethodcall) /\ $magic_named_raw_valid(S_raw,pmagicmethodcall,0,eps,false)
$magic_method_arguments_source(S_raw,pmagicmethodcall.SITE,pmagicmethodcall.ARGUMENTS,0) = false
$magic_named_keys(pmagicmethodcall.ARGUMENTS,0,false,eps) = (pkey_sent_all*)
$effective_method(S_raw,pmagicmethodcall.CLASS,pmagicmethodcall.NAME,|S_raw.CLASSES|) = eps
$effective_method(S_raw,pmagicmethodcall.CLASS,$ptascii("__call"),|S_raw.CLASSES|) = (pmethoddesc_call)
pfunction_call = pmethoddesc_call.FUNCTION
$magic_method_source(S_raw,pmethoddesc_call) /\ $ppmethod_call_signature(pfunction_call.SIGNATURE)
$target_nodes(MAGIC_METHOD_SEND_TARGET pmagicmethodcall) = [HOBJECT n_child]
$task_nodes(MAGIC_METHOD_NAMED_ARGS pmagicmethodcall 0 eps) = [HOBJECT n_child]
$target_function(S_raw,MAGIC_METHOD_SEND_TARGET pmagicmethodcall) = eps
~$call_parameter_reference(S_raw,MAGIC_METHOD_SEND_TARGET pmagicmethodcall,0) /\ ~$call_parameter_reference(S_raw,MAGIC_METHOD_SEND_TARGET pmagicmethodcall,1)
$heap_owners($heap_graph(S_raw),HOBJECT n_child) = 2
$mn_guard(S_raw)
''')

SNAPSHOT = lines(r'''
$lookup(S_raw.ENV,$ptascii("first")) = (n_first_cell)
S_raw.STORE[n_first_cell] = DEFINED (PINT 7) /\ ~(n_first_cell <- S_raw.REFCELLS)
$call_target(S_raw,$ptascii("mutate114"),eps) = (pfunction_mutate)
S_mutate_found = $mn_seek(S_raw,MN_RETURN pfunction_mutate.ORIGIN 2,1000)
S_mutate_found.COMPLETION = NORMAL \/ S_mutate_found.COMPLETION = BUDGET
S_mutate = S_mutate_found[.COMPLETION = NORMAL]
$mn_stage(S_mutate,MN_RETURN pfunction_mutate.ORIGIN 2)
$lookup(S_mutate.ENV,$ptascii("first")) = (n_first_cell)
S_mutate.STORE[n_first_cell] = DEFINED (PINT 99) /\ S_mutate.STORE[n_child_cell] = DEFINED PNULL
S_mutate.CURRENT = (pcallcontext_mutate)
pcallcontext_mutate.RECEIVER = eps /\ pcallcontext_mutate.INSTANCE = eps
S_mutate.FRAMES = pframe_mutate :: eps
S_mutate_saved = $constant_frame_scope(S_mutate,pframe_mutate,eps)
S_mutate_saved.TODO = (ORIGIN_RETURN (pmagicmethodcall.SITE)) :: (MAGIC_METHOD_NAMED_SEND pmagicmethodcall 1 ([KNOWN (PINT 7)])) :: METHOD_RESULT :: ptask_outer_tail*
S_selected = S_mutate_saved[.ORIGIN = (pmagicmethodcall.SITE)]
$magic_named_raw_valid(S_selected,pmagicmethodcall,1,[KNOWN (PINT 7)],true) /\ ~$magic_method_capture(S_selected,pmagicmethodcall)
$magic_method_raw_valid(S_selected,pmagicmethodcall) /\ $call_selected_valid(S_selected,MAGIC_METHOD_SEND_TARGET pmagicmethodcall,(pmagicmethodcall.SITE))
$heap_owners($heap_graph(S_mutate),HOBJECT n_child) = 1 /\ $mn_guard(S_mutate)
$mn_output(S_mutate.EVENTS) = $ptascii("N:M|")
S_before_pack = S_mutate
''')

PACK = lines(r'''
S_pack.TODO = (MAGIC_METHOD_NAMED_ARGS pmagicmethodcall n_sent poperand_sent_all*) :: METHOD_RESULT :: ptask_outer_tail*
n_sent = |pmagicmethodcall.ARGUMENTS| /\ n_sent = |poperand_sent_all*|
$magic_method_values(S_pack,poperand_sent_all*) = (pvalue_sent_all*)
$magic_named_raw_valid(S_pack,pmagicmethodcall,n_sent,poperand_sent_all*,false) /\ $mn_guard(S_pack)
PhpStep: S_pack ~> S_packed_raw
S_packed_raw.TODO = (CALL_ARGS (MAGIC_METHOD_NAMED_TARGET pmagicmethodcall n_arguments n_named pvalue_sent_all*) eps 2 ([KNOWN (PSTRING pmagicmethodcall.NAME),KNOWN (PARRAY n_arguments)]) (pmagicmethodcall.SITE) pmagicmethodcall.LINE) :: (MAGIC_METHOD_NAMED_RESULT pmagicmethodcall n_arguments n_named pvalue_sent_all*) :: METHOD_RESULT :: ptask_outer_tail*
n_named = |S_pack.ARRAYS|
HARRAY n_named <- S_packed_raw.ALLOCATIONS /\ HARRAY n_arguments <- S_packed_raw.ALLOCATIONS
ptask_marker = MAGIC_METHOD_NAMED_RESULT pmagicmethodcall n_arguments n_named pvalue_sent_all*
pcalltarget_named = MAGIC_METHOD_NAMED_TARGET pmagicmethodcall n_arguments n_named pvalue_sent_all*
$target_nodes(pcalltarget_named) = eps /\ $target_instance(pcalltarget_named) = eps
$task_nodes(ptask_marker) = [HARRAY n_named,HOBJECT n_child]
$magic_named_pending(S_packed_raw,pmagicmethodcall,n_arguments,n_named,pvalue_sent_all*) /\ $magic_named_buffer(S_packed_raw,pmagicmethodcall,n_arguments,n_named,pvalue_sent_all*)
$target_function(S_packed_raw,pcalltarget_named) = (pfunction_call)
$named_call_valid(S_packed_raw,pcalltarget_named,(pmagicmethodcall.SITE))
$named_call_shape(S_packed_raw,pcalltarget_named,(pmagicmethodcall.SITE)) = {SLOTS ([NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN PNULL)]),NAMED eps}
$mn_guard(S_packed_raw)
S_packed = $mn_after(S_pack,S_packed_raw)
''')

RECEIVE = lines(r'''
S_receive.CURRENT = (pcallcontext_call)
pcallcontext_call.TARGET = pcalltarget_named
pcallcontext_call.ARGC = 2 /\ pcallcontext_call.INSTANCE = eps /\ pcallcontext_call.RECEIVER = (n_child)
pcallcontext_call.LEXICAL_CLASS = (pmethoddesc_call.OWNER) /\ pcallcontext_call.CALLED_CLASS = (pmagicmethodcall.CLASS)
pcallcontext_call.NAMED = eps /\ pcallcontext_call.EXTRA = eps
$call_context_roots(S_receive.CURRENT) = eps /\ $call_receiver_roots(pcallcontext_call) = eps
$target_function(S_receive,pcalltarget_named) = (pfunction_call) /\ $receiving_function(S_receive,pmagicmethodcall.METHOD) = (pfunction_call)
$lookup(S_receive.ENV,$ptascii("name")) = (n_name_cell)
$lookup(S_receive.ENV,$ptascii("arguments")) = (n_arguments_cell)
S_receive.STORE[n_name_cell] = DEFINED (PSTRING $ptascii("MiSs"))
S_receive.STORE[n_arguments_cell] = DEFINED (PARRAY n_arguments)
$magic_named_entered(S_receive,S_receive.CURRENT,S_receive.FRAMES,pmagicmethodcall,n_arguments,n_named,pvalue_sent_all*) /\ $mn_guard(S_receive)
''')

RETURN = lines(r'''
S_return.CURRENT = (pcallcontext_return)
pcallcontext_return.TARGET = pcalltarget_named
S_return.STORE[n_child_cell] = DEFINED PNULL
$heap_owners($heap_graph(S_return),HOBJECT n_child) = 1
$call_context_roots(S_return.CURRENT) = eps
S_return.FRAMES = pframe_call :: eps
S_saved = $constant_frame_scope(S_return,pframe_call,eps)
$magic_method_caller(S_saved,pmagicmethodcall) /\ ~$magic_method_capture(S_saved,pmagicmethodcall)
$magic_named_entered(S_return,S_return.CURRENT,S_return.FRAMES,pmagicmethodcall,n_arguments,n_named,pvalue_sent_all*)
$mn_output(S_return.EVENTS) = ptbytes_body
$mn_guard(S_return)
''')

MARKER = lines(r'''
S_marker.TODO = ptask_marker :: METHOD_RESULT :: ptask_outer_tail*
S_marker.RESULT = KNOWN (PINT 7) /\ S_marker.BASE = BASE_VALUE (KNOWN PNULL)
S_marker.CURRENT = eps /\ S_marker.FRAMES = eps
S_marker.STORE[n_child_cell] = DEFINED PNULL
$magic_named_result_valid(S_marker,pmagicmethodcall,n_arguments,n_named,pvalue_sent_all*)
$heap_owners($heap_graph(S_marker),HARRAY n_named) = 1 /\ $heap_owners($heap_graph(S_marker),HOBJECT n_child) = 1
~$magic_named_entered(S_marker,S_marker.CURRENT,S_marker.FRAMES,pmagicmethodcall,n_arguments,n_named,pvalue_sent_all*)
$mn_output(S_marker.EVENTS) = ptbytes_body /\ $mn_guard(S_marker)
PhpStep: S_marker ~> S_drop_raw
S_drop_raw.TODO = METHOD_RESULT :: ptask_outer_tail*
S_drop_raw.RESULT = KNOWN (PINT 7) /\ S_drop_raw.BASE = BASE_VALUE (KNOWN PNULL)
$heap_owners($heap_graph(S_drop_raw),HARRAY n_named) = 0 /\ $heap_owners($heap_graph(S_drop_raw),HOBJECT n_child) = 0
S_releasing = $mn_after(S_marker,S_drop_raw)
''')

PAYLOAD = lines(r'''
S_payload.CURRENT = (pcallcontext_payload)
$destructor_context_call(pcallcontext_payload,S_payload.CURRENT,S_payload.FRAMES) = (pdestructorcall_payload)
pdestructorcall_payload.OBJECT = n_payload
pdestructorcall_payload.OPERATION = (pdestructionoperation_payload)
pdestructionoperation_payload.SOURCE = ptask_marker
pdestructionoperation_payload.VALUE = KNOWN (PINT 7) /\ pdestructionoperation_payload.BASE = BASE_VALUE (KNOWN PNULL)
pdestructionoperation_payload.PENDING = eps
~(HARRAY n_named <- S_payload.ALLOCATIONS) /\ HOBJECT n_payload <- S_payload.ALLOCATIONS
HOBJECT n_child <- S_payload.ALLOCATIONS
S_payload.STORE[n_rhs_cell] = DEFINED (PINT 7)
$mn_output(S_payload.EVENTS) = ptbytes_body
$magic_named_history(S_payload,pmagicmethodcall,n_arguments,n_named,pvalue_sent_all*) /\ ~$magic_named_buffer(S_payload,pmagicmethodcall,n_arguments,n_named,pvalue_sent_all*)
$mn_guard(S_payload)
S_before_child = S_payload
''')

CHILD = lines(r'''
S_child.CURRENT = (pcallcontext_child)
$destructor_context_call(pcallcontext_child,S_child.CURRENT,S_child.FRAMES) = (pdestructorcall_child)
pdestructorcall_child.OBJECT = n_child
pdestructorcall_child.OPERATION = (pdestructionoperation_child)
pdestructionoperation_child.SOURCE = ptask_marker
pdestructionoperation_child.VALUE = KNOWN (PINT 7) /\ pdestructionoperation_child.BASE = BASE_VALUE (KNOWN PNULL)
~(HARRAY n_arguments <- S_child.ALLOCATIONS) /\ ~(HARRAY n_named <- S_child.ALLOCATIONS)
S_child.STORE[n_child_cell] = DEFINED PNULL
$mn_output(S_child.EVENTS) = ptbytes_before_child
$magic_named_history(S_child,pmagicmethodcall,n_arguments,n_named,pvalue_sent_all*) /\ ~$magic_named_buffer(S_child,pmagicmethodcall,n_arguments,n_named,pvalue_sent_all*)
$mn_guard(S_child)
''')

FINISH = lines(r'''
S_final = $drive_steps(S_end,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$mn_output(S_final.EVENTS) = ptbytes_final
$lookup(S_final.ENV,$ptascii("result")) = (n_result_cell)
S_final.STORE[n_result_cell] = DEFINED (PINT i_result)
~(HOBJECT n_child <- S_final.ALLOCATIONS) /\ ~(HARRAY n_named <- S_final.ALLOCATIONS) /\ ~(HARRAY n_arguments <- S_final.ALLOCATIONS)
$mn_guard(S_final)
S_budget = $drive_steps(S_raw,0)
S_budget = S_raw[.COMPLETION = BUDGET]
$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final
''')

DERIVED = lines(r'''
~$magic_named_source(S_raw[.SOURCES = eps],pmagicmethodcall)
pmagicmethodcall_wrong_name = pmagicmethodcall[.NAME = $ptascii("missing")]
~$magic_method_descriptor(S_raw,pmagicmethodcall_wrong_name)
pmagicmethodcall_wrong_line = pmagicmethodcall[.LINE = $(pmagicmethodcall.LINE + 1)]
~$magic_method_descriptor(S_raw,pmagicmethodcall_wrong_line)
pmagicmethodcall_wrong_owner = pmagicmethodcall[.OWNER = 1]
~$magic_method_capture(S_raw,pmagicmethodcall_wrong_owner)
S_wrong_buffer = S_packed_raw[.ARRAYS[n_named].ITEMS = [ENTRY (KSTRING ($ptascii("name"))) (DIRECT (PINT 99))]]
~$magic_named_buffer(S_wrong_buffer,pmagicmethodcall,n_arguments,n_named,pvalue_sent_all*)
~$magic_named_pending(S_wrong_buffer,pmagicmethodcall,n_arguments,n_named,pvalue_sent_all*)
$target_function(S_wrong_buffer,pcalltarget_named) = eps
~$magic_named_history(S_packed_raw,pmagicmethodcall,n_arguments,$nabs($(n_named + 1)),pvalue_sent_all*)
S_wrong_source = S_marker[.ORIGIN = eps]
~$magic_named_result_valid(S_wrong_source,pmagicmethodcall,n_arguments,n_named,pvalue_sent_all*)
S_wrong_caller = S_marker[.CURRENT = (pcallcontext_call)]
~$magic_named_result_valid(S_wrong_caller,pmagicmethodcall,n_arguments,n_named,pvalue_sent_all*)
S_ref = S_raw[.REFCELLS = n_first_cell :: S_raw.REFCELLS]
~$magic_method_capture(S_ref,pmagicmethodcall)
~$magic_named_raw_valid(S_pack,pmagicmethodcall,$nabs($(n_sent + 1)),poperand_sent_all*,false)
$magic_named_keys([pmagicmethodcall.ARGUMENTS[1],pmagicmethodcall.ARGUMENTS[0]],0,false,eps) = eps
$magic_named_keys([pmagicmethodcall.ARGUMENTS[1],pmagicmethodcall.ARGUMENTS[1]],0,false,eps) = eps
$destructor_return_discarded([ptask_marker,METHOD_RESULT,DISCARD])
~$destructor_return_discarded(ptask_marker :: METHOD_RESULT :: ptask_outer_tail*)
''')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', action='append', choices=('selection', 'owning', 'throwing'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_named_call_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = ROOT / 'tests/semantics/profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_observations_accepted']
    assert [case['id'] for case in data['cases']] == ['selection', 'owning', 'throwing', 'compile-order']
    selected = [case for case in data['cases'] if case['role'] == 'agreement']
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
    for case in data['cases']:
        source = HERE / case['source_file']
        assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256']
    out = Path(tempfile.mkdtemp(prefix='magic-named-call-protocol-', dir=ROOT / '.tools'))
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
            body_output = {'selection':'N:M|C|MiSs|MagicNamedParent114|MagicNamedChild114|0:7|name:2|c|',
                           'owning':'O:C|second|first|A|', 'throwing':'X:C|second|first|A|'}[name]
            setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'ptbytes_body = $ptascii(' + json.dumps(body_output) + ')',
                     'ptbytes_before_child = $ptascii(' + json.dumps(body_output + ('' if name == 'selection' else 'V|')) + ')',
                     'ptbytes_final = $ptascii(' + json.dumps(base64.b64decode(case['stdout_base64']).decode()) + ')']
            reached = setup + reach('S_raw','S_initial','MN_RAW') + COMMON
            if name == 'selection':
                reached += SNAPSHOT
            else:
                reached += ['S_before_pack = S_raw', '$lookup(S_raw.ENV,$ptascii("rhs")) = (n_rhs_cell)', 'S_raw.STORE[n_rhs_cell] = DEFINED (PINT 7)']
                if name == 'throwing':
                    reached += ['$lookup(S_raw.ENV,$ptascii("result")) = (n_result_cell)',
                                'S_raw.STORE[n_result_cell] = DEFINED (PINT 42)',
                                '$lookup(S_raw.ENV,$ptascii("error")) = (n_error_cell)',
                                'S_raw.STORE[n_error_cell] = DEFINED (POBJECT n_error)']
            reached += reach('S_pack','S_before_pack','MN_PACK') + PACK
            if name == 'selection':
                reached += lines(r'''
pvalue_sent_all* = [PINT 7,PINT 2]
pkey_sent_all* = [KINT 0,KSTRING ($ptascii("name"))]
n_arguments = $(n_named + 1)
S_packed.ARRAYS[n_arguments].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7)),ENTRY (KSTRING ($ptascii("name"))) (DIRECT (PINT 2))]
S_packed.ARRAYS[n_arguments].POSITIONS = [POSITION (KINT 0) 0,POSITION (KSTRING ($ptascii("name"))) 1]
S_packed.ARRAYS[n_arguments].SERIAL = 2 /\ S_packed.ARRAYS[n_arguments].NEXT = 1
S_packed.ARRAYS[n_named].ITEMS = [ENTRY (KSTRING ($ptascii("name"))) (DIRECT (PINT 2))]
S_packed.ARRAYS[n_named].POSITIONS = [POSITION (KSTRING ($ptascii("name"))) 0]
S_packed.ARRAYS[n_named].SERIAL = 1 /\ S_packed.ARRAYS[n_named].NEXT = $(-9223372036854775808)
$heap_owners($heap_graph(S_packed),HARRAY n_arguments) = 1 /\ $heap_owners($heap_graph(S_packed),HARRAY n_named) = 1
$heap_owners($heap_graph(S_packed),HOBJECT n_child) = 1
''')
            else:
                reached += lines(r'''
pvalue_sent_all* = [POBJECT n_payload,PINT 7]
pkey_sent_all* = [KSTRING ($ptascii("second")),KSTRING ($ptascii("first"))]
n_arguments = n_named
S_packed.ARRAYS[n_named].ITEMS = [ENTRY (KSTRING ($ptascii("second"))) (DIRECT (POBJECT n_payload)),ENTRY (KSTRING ($ptascii("first"))) (DIRECT (PINT 7))]
S_packed.ARRAYS[n_named].POSITIONS = [POSITION (KSTRING ($ptascii("second"))) 0,POSITION (KSTRING ($ptascii("first"))) 1]
S_packed.ARRAYS[n_named].SERIAL = 2 /\ S_packed.ARRAYS[n_named].NEXT = $(-9223372036854775808)
$heap_owners($heap_graph(S_packed),HARRAY n_named) = 2
n_payload =/= n_child /\ $node_children(S_packed,HOBJECT n_payload) = eps
$heap_owners($heap_graph(S_pack),HOBJECT n_payload) = 1 /\ $heap_owners($heap_graph(S_packed),HOBJECT n_payload) = 1
$heap_owners($heap_graph(S_packed),HOBJECT n_child) = 2
''')
            reached += reach('S_receive','S_packed','MN_RECEIVE pmagicmethodcall.METHOD') + RECEIVE
            reached += [('$heap_owners($heap_graph(S_receive),HARRAY n_named) = ' + ('1' if name == 'selection' else '2'))]
            if name != 'selection':
                reached += ['$heap_owners($heap_graph(S_receive),HOBJECT n_payload) = 1']
            reached += reach('S_return','S_receive','MN_RETURN pmagicmethodcall.METHOD 7') + RETURN
            if name == 'selection':
                reached += ['S_return.STORE[n_first_cell] = DEFINED (PINT 99)',
                            'S_return.STORE[n_arguments_cell] = DEFINED (PARRAY n_arguments)']
            else:
                reached += lines(r'''
$lookup(S_return.ENV,$ptascii("arguments")) = eps
~(HCELL n_arguments_cell <- S_return.ALLOCATIONS)
$lookup(S_return.ENV,$ptascii("cached")) = (n_cached_cell)
S_return.STORE[n_cached_cell] = DEFINED (PINT 7) /\ S_return.STORE[n_rhs_cell] = DEFINED (PINT 7)
$heap_owners($heap_graph(S_return),HARRAY n_named) = 1 /\ $heap_owners($heap_graph(S_return),HOBJECT n_payload) = 1
$magic_named_buffer(S_return,pmagicmethodcall,n_arguments,n_named,pvalue_sent_all*)
''')
            reached += reach('S_marker','S_return','MN_MARKER') + MARKER
            if name == 'selection':
                reached += ['~(HARRAY n_arguments <- S_marker.ALLOCATIONS)', 'S_before_child = S_releasing']
            else:
                reached += ['$heap_owners($heap_graph(S_marker),HOBJECT n_payload) = 1']
                reached += reach('S_payload','S_releasing','MN_DTOR n_payload') + PAYLOAD
            reached += reach('S_child','S_before_child','MN_DTOR n_child') + CHILD
            if name != 'selection':
                reached += ['~(HOBJECT n_payload <- S_child.ALLOCATIONS)', 'S_child.STORE[n_rhs_cell] = DEFINED (PINT 99)']
            if name == 'throwing':
                reached += ['pdestructionoperation_child = pdestructionoperation_payload[.PENDING = (n_error)]',
                            '$throwable_live(S_child,n_error)']
                reached += reach('S_catch','S_child','MN_CATCH') + lines(r'''
S_catch.TODO = (CATCH_BIND porigin_try n_catch n_error) :: ptask_catch_tail*
S_catch.STORE[n_result_cell] = DEFINED (PINT 42) /\ $throwable_live(S_catch,n_error)
~(HOBJECT n_child <- S_catch.ALLOCATIONS) /\ ~(HOBJECT n_payload <- S_catch.ALLOCATIONS)
$mn_guard(S_catch)
PhpStep: S_catch ~> S_catch_raw
$lookup(S_catch_raw.ENV,$ptascii("caught")) = (n_caught_cell)
S_catch_raw.STORE[n_caught_cell] = DEFINED (POBJECT n_error)
S_end = $mn_after(S_catch,S_catch_raw)
i_result = 42
''')
            else:
                reached += ['pdestructionoperation_child.PENDING = eps']
                if name == 'owning':
                    reached += ['pdestructionoperation_child = pdestructionoperation_payload']
                reached += reach('S_result','S_child','MN_RESULT') + lines(r'''
S_result.TODO = METHOD_RESULT :: ptask_outer_tail*
S_result.RESULT = KNOWN (PINT 7) /\ S_result.CURRENT = eps /\ S_result.FRAMES = eps
~(HOBJECT n_child <- S_result.ALLOCATIONS) /\ ~(HARRAY n_named <- S_result.ALLOCATIONS)
$lookup(S_result.ENV,$ptascii("result")) = eps
$mn_guard(S_result)
S_end = S_result
i_result = 7
''')
            reached += FINISH
            derived = DERIVED if name == 'selection' else []
            content = PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
            for condition in reached + derived:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $main() = false -- otherwise\n'
            fixture = directory / 'hook.watsup'
            fixture.write_text(content)
            row = {'id': name, 'path': str(fixture), 'sha256': sha(fixture), 'reached_premises': len(reached),
                   'derived_premises': len(derived), 'premises': len(reached) + len(derived)}
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
        report['passed'] = report['passed'] and all(report[key] for key in ('inputs_stable', 'fixtures_stable', 'head_stable', 'status_stable'))
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({key: report[key] for key in ('passed', 'application_evaluations', 'premises', 'reached_premises', 'derived_premises', 'inputs_stable', 'head_stable', 'status_stable')}), flush=True)
    assert report['passed']

if __name__ == '__main__':
    main()
