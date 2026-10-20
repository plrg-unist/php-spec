"""Check real parent get-hook dispatch, borrowed This and return/throw lifetime."""
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
syntax pparentgetstage = PG_FRONT | PG_PARENT | PG_RETURN | PG_THROW | PG_INNER porigin | PG_DELIVERY | PG_DTOR nat | PG_UNSET | PG_CATCH
dec $pg_output(pevent*) : ptbytes
def $pg_output(eps) = eps
def $pg_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $pg_output(pevent*)
dec $pg_stage(pstate,pparentgetstage) : bool
def $pg_stage(S,PG_FRONT) = true
  -- if S.TODO = (EVAL expression) :: ptask*
  -- if $parent_hook_syntax(expression)
def $pg_stage(S,PG_PARENT) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PARENT_HOOK_TARGET pparenthookcall
def $pg_stage(S,PG_RETURN) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PARENT_HOOK_TARGET pparenthookcall
  -- if S.TODO = (RETURN_UNWIND poperand porigin?) :: ptask*
def $pg_stage(S,PG_THROW) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PARENT_HOOK_TARGET pparenthookcall
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask*
def $pg_stage(S,PG_INNER porigin) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.FUNCTION = porigin
  -- if S.TODO = METHOD_RESULT :: ptask*
def $pg_stage(S,PG_DELIVERY) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*
def $pg_stage(S,PG_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $pg_stage(S,PG_UNSET) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES "cmVzdWx0") metadata)) :: ptask*
def $pg_stage(S,PG_CATCH) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask*
def $pg_stage(S,pparentgetstage) = false -- otherwise
dec $pg_seek(pstate,pparentgetstage,nat) : pstate
def $pg_seek(S,pparentgetstage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $pg_stage(S,pparentgetstage) \/ n = 0
def $pg_seek(S,pparentgetstage,n) = $pg_seek($drive_steps(S[.COMPLETION = NORMAL],1),pparentgetstage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$pg_stage(S,pparentgetstage) /\ $(n > 0)
def $pg_seek(S,pparentgetstage,n) = $pg_seek($drive_steps(S,1),pparentgetstage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $pg_seek(S,pparentgetstage,n) = S -- otherwise
dec $pg_after(pstate,pstate) : pstate
def $pg_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $pg_guard(pstate) : bool
def $pg_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $gc_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''

COMMON = r'''
S_front.TODO = (EVAL expression_call) :: ptask_tail*
S_front.CURRENT = (pcallcontext_child)
pcallcontext_child.TARGET = PROPERTY_HOOK_TARGET ppropertyhook
pcallcontext_child.RECEIVER = (n_child)
S_front.FRAMES = pframe_main :: eps
S_main = $constant_frame_scope(S_front,pframe_main,eps)
S_main.CURRENT = eps
S_main.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask_main_tail*
$lookup(S_main.ENV,$ptascii("child")) = (n_child_cell)
$lookup(S_main.ENV,$ptascii("result")) = (n_result_cell)
S_front.STORE[n_child_cell] = DEFINED (POBJECT n_child) /\ S_front.STORE[n_result_cell] = DEFINED (PINT 42)
$parent_hook_plan(S_front) = (pparenthookcall)
pparenthookcall.CALLER = pcallcontext_child /\ pparenthookcall.OBJECT = n_child
$parent_hook_function(S_front,pparenthookcall) = (pfunction_parent)
pcallcontext_child.LEXICAL_CLASS = (porigin_child)
$class_at(S_front.CLASSES,porigin_child) = (pclassdesc_child)
pclassdesc_child.NAME = $ptascii("ParentGetChild108")
$property_hook_function(S_front,ppropertyhook) = (pfunction_child)
pfunction_child.ORIGIN = pcallcontext_child.FUNCTION
S_front.OBJECTS[n_child] = INSTANCE porigin_grand
$class_at(S_front.CLASSES,porigin_grand) = (pclassdesc_grand)
pclassdesc_grand.NAME = $ptascii("ParentGetGrand108") /\ pcallcontext_child.CALLED_CLASS = (porigin_grand)
$class_at(S_front.CLASSES,pparenthookcall.CLASS) = (pclassdesc_parent)
pclassdesc_parent.NAME = $ptascii("ParentGetParent108")
$class_link_at(S_front.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT pparenthookcall.CLASS)
pparenthookcall.CLASS =/= porigin_child /\ pparenthookcall.CLASS =/= porigin_grand
$hook_property_at(pclassdesc_parent.PROPERTIES,pparenthookcall.PROPERTY) = (ppropertydesc_parent)
$property_effective_desc(S_front,n_child,$ptascii("value")) = (ppropertydesc_child)
ppropertydesc_child.ORIGIN = ppropertyhook.PROPERTY /\ ppropertyhook.HOOK = pfunction_child.ORIGIN
$property_hook_virtual(S_front,ppropertydesc_parent) /\ $property_hook_virtual(S_front,ppropertydesc_child)
$heap_owners($heap_graph(S_front),HOBJECT n_child) = 2 /\ $pg_guard(S_front)
PhpStep: S_front ~> S_raw_step
S_raw_step.TODO = (CALL_ARGS (PARENT_HOOK_TARGET pparenthookcall) eps 0 eps (pparenthookcall.SITE) pparenthookcall.LINE) :: METHOD_RESULT :: ptask_tail*
S_raw = $pg_after(S_front,S_raw_step)
$parent_hook_pending(S_raw,pparenthookcall) /\ $call_selected_valid(S_raw,PARENT_HOOK_TARGET pparenthookcall,(pparenthookcall.SITE))
$target_nodes(PARENT_HOOK_TARGET pparenthookcall) = eps /\ $target_instance(PARENT_HOOK_TARGET pparenthookcall) = eps
$heap_owners($heap_graph(S_raw),HOBJECT n_child) = 2 /\ $pg_guard(S_raw)
S_enter_found = $pg_seek(S_raw,PG_PARENT,1000)
S_enter_found.COMPLETION = NORMAL \/ S_enter_found.COMPLETION = BUDGET
S_enter = S_enter_found[.COMPLETION = NORMAL]
S_enter.CURRENT = (pcallcontext_parent)
pcallcontext_parent.TARGET = PARENT_HOOK_TARGET pparenthookcall
pcallcontext_parent.RECEIVER = (n_child) /\ pcallcontext_parent.INSTANCE = eps /\ pcallcontext_parent.ARGC = 0
pcallcontext_parent.LEXICAL_CLASS = (pparenthookcall.CLASS) /\ pcallcontext_parent.CALLED_CLASS = (porigin_grand)
$call_receiver_roots(pcallcontext_parent) = eps /\ $call_context_roots((pcallcontext_parent)) = eps
$parent_hook_entered(S_enter,S_enter.CURRENT,S_enter.FRAMES,pparenthookcall)
$target_function(S_enter,pcallcontext_parent.TARGET) = (pfunction_parent)
S_enter.FRAMES = pframe_child :: pframe_main :: eps
pframe_child.CONTEXT = (pcallcontext_child) /\ pframe_child.ORIGIN = (pparenthookcall.SITE)
pframe_child.TODO = METHOD_RESULT :: ptask_tail*
$call_receiver_roots(pcallcontext_child) = [HOBJECT n_child]
$pg_output(S_enter.EVENTS) = ptbytes_before_parent
$heap_owners($heap_graph(S_enter),HOBJECT n_child) = 2 /\ $pg_guard(S_enter)
'''.strip().splitlines()

RETURN = r'''
S_return_found = $pg_seek(S_enter,PG_RETURN,1000)
S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET
S_return = S_return_found[.COMPLETION = NORMAL]
S_return.TODO = (RETURN_UNWIND (KNOWN pvalue_return) porigin_return?) :: ptask_return*
S_return.CURRENT = (pcallcontext_parent)
S_return.STORE[n_child_cell] = DEFINED PNULL /\ S_return.STORE[n_result_cell] = DEFINED (PINT 42)
$pg_output(S_return.EVENTS) = ptbytes_parent
$heap_owners($heap_graph(S_return),HOBJECT n_child) = 1 /\ HOBJECT n_child <- S_return.ALLOCATIONS
$call_context_roots(S_return.CURRENT) = eps
$parent_hook_function(S_return,pparenthookcall) = (pfunction_parent)
$parent_hook_entered(S_return,S_return.CURRENT,S_return.FRAMES,pparenthookcall) /\ $pg_guard(S_return)
S_inner_found = $pg_seek(S_return,PG_INNER pfunction_child.ORIGIN,1000)
S_inner_found.COMPLETION = NORMAL \/ S_inner_found.COMPLETION = BUDGET
S_inner = S_inner_found[.COMPLETION = NORMAL]
S_inner.CURRENT = (pcallcontext_child) /\ S_inner.FRAMES = pframe_main :: eps
S_inner.TODO = METHOD_RESULT :: ptask_tail*
S_inner.RESULT = KNOWN pvalue_return /\ S_inner.STORE[n_child_cell] = DEFINED PNULL
$pg_output(S_inner.EVENTS) = ptbytes_parent
$heap_owners($heap_graph(S_inner),HOBJECT n_child) = 1 /\ $pg_guard(S_inner)
S_before_child = S_inner
'''.strip().splitlines()

CHILD = r'''
S_child_found = $pg_seek(S_before_child,PG_DTOR n_child,1000)
S_child_found.COMPLETION = NORMAL \/ S_child_found.COMPLETION = BUDGET
S_child = S_child_found[.COMPLETION = NORMAL]
$pg_stage(S_child,PG_DTOR n_child) /\ $pg_output(S_child.EVENTS) = ptbytes_before_child
S_child.CURRENT = (pcallcontext_dtor)
$destructor_context_call(pcallcontext_dtor,S_child.CURRENT,S_child.FRAMES) = (pdestructorcall_child)
pdestructorcall_child.FRAME = (pdestructionframe_child)
pdestructionframe_child.FUNCTION = pfunction_child.ORIGIN /\ pdestructionframe_child.CALLER = eps
S_child.STORE[n_result_cell] = DEFINED (PINT 42) /\ S_child.STORE[n_child_cell] = DEFINED PNULL
$pg_guard(S_child)
'''.strip().splitlines()

DELIVERY = r'''
pdestructionframe_child.VALUE = KNOWN pvalue_return /\ pdestructionframe_child.PENDING = eps
S_delivery_found = $pg_seek(S_child,PG_DELIVERY,1000)
S_delivery_found.COMPLETION = NORMAL \/ S_delivery_found.COMPLETION = BUDGET
S_delivery = S_delivery_found[.COMPLETION = NORMAL]
S_delivery.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask_main_tail*
S_delivery.CURRENT = eps /\ S_delivery.FRAMES = eps /\ S_delivery.RESULT = KNOWN pvalue_return
S_delivery.STORE[n_result_cell] = DEFINED (PINT 42) /\ ~(HOBJECT n_child <- S_delivery.ALLOCATIONS)
$pg_output(S_delivery.EVENTS) = ptbytes_before_child ++ $ptascii("D|")
$pg_guard(S_delivery)
'''.strip().splitlines()

OWNING = r'''
pvalue_return = POBJECT n_payload
n_payload =/= n_child
HOBJECT n_payload <- S_return.ALLOCATIONS /\ $heap_owners($heap_graph(S_return),HOBJECT n_payload) = 1
HOBJECT n_payload <- S_child.ALLOCATIONS /\ $heap_owners($heap_graph(S_child),HOBJECT n_payload) = 1
HOBJECT n_payload <- S_delivery.ALLOCATIONS /\ $heap_owners($heap_graph(S_delivery),HOBJECT n_payload) = 1
S_unset_found = $pg_seek(S_delivery,PG_UNSET,1000)
S_unset_found.COMPLETION = NORMAL \/ S_unset_found.COMPLETION = BUDGET
S_unset = S_unset_found[.COMPLETION = NORMAL]
S_unset.STORE[n_result_cell] = DEFINED (POBJECT n_payload)
$pg_output(S_unset.EVENTS) = $ptascii("O:C|P|A|D|M|")
$heap_owners($heap_graph(S_unset),HOBJECT n_payload) = 1 /\ $pg_guard(S_unset)
S_payload_found = $pg_seek(S_unset,PG_DTOR n_payload,1000)
S_payload_found.COMPLETION = NORMAL \/ S_payload_found.COMPLETION = BUDGET
S_payload = S_payload_found[.COMPLETION = NORMAL]
$pg_stage(S_payload,PG_DTOR n_payload) /\ ~(HOBJECT n_child <- S_payload.ALLOCATIONS)
$pg_output(S_payload.EVENTS) = $ptascii("O:C|P|A|D|M|") /\ $pg_guard(S_payload)
S_end = S_payload
'''.strip().splitlines()

THROW = r'''
$lookup(S_main.ENV,$ptascii("error")) = (n_error_cell)
S_front.STORE[n_error_cell] = DEFINED (POBJECT n_error)
S_throw_found = $pg_seek(S_enter,PG_THROW,1000)
S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET
S_throw = S_throw_found[.COMPLETION = NORMAL]
S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_throw*
S_throw.CURRENT = (pcallcontext_parent)
S_throw.STORE[n_child_cell] = DEFINED PNULL /\ S_throw.STORE[n_result_cell] = DEFINED (PINT 42)
S_error_read = $resolve_at(S_throw,S_throw.RESULT,z_throw)
S_error_read.RESULT = KNOWN (POBJECT n_error)
$pg_output(S_throw.EVENTS) = $ptascii("X:C|P|")
$heap_owners($heap_graph(S_throw),HOBJECT n_child) = 1 /\ $call_context_roots(S_throw.CURRENT) = eps
$parent_hook_entered(S_throw,S_throw.CURRENT,S_throw.FRAMES,pparenthookcall) /\ $pg_guard(S_throw)
PhpStep: S_throw ~> S_throw_raw
S_throw_raw.COMPLETION = THROWING n_error
S_before_child = $pg_after(S_throw,S_throw_raw)
'''.strip().splitlines()

CATCH = r'''
pdestructionframe_child.PENDING = (n_error)
S_catch_found = $pg_seek(S_child,PG_CATCH,1000)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_try n_catch n_error) :: ptask_catch*
S_catch.STORE[n_result_cell] = DEFINED (PINT 42) /\ S_catch.STORE[n_error_cell] = DEFINED (POBJECT n_error)
~(HOBJECT n_child <- S_catch.ALLOCATIONS) /\ $throwable_previous_id(S_catch,n_error) = eps
$pg_guard(S_catch)
PhpStep: S_catch ~> S_catch_raw
$lookup(S_catch_raw.ENV,$ptascii("caught")) = (n_caught_cell)
S_catch_raw.STORE[n_caught_cell] = DEFINED (POBJECT n_error)
S_end = $pg_after(S_catch,S_catch_raw)
'''.strip().splitlines()

FINISH = r'''
S_final = $drive_steps(S_end,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$pg_output(S_final.EVENTS) = ptbytes_final /\ $pg_guard(S_final)
~(HOBJECT n_child <- S_final.ALLOCATIONS)
S_zero = $drive_steps(S_front,0)
S_zero = S_front[.COMPLETION = BUDGET]
S_resumed = $drive_steps(S_zero[.COMPLETION = NORMAL],10000)
S_whole = $drive_steps(S_front,10000)
S_resumed = S_whole /\ S_resumed = S_final
'''.strip().splitlines()

DERIVED = r'''
$parent_hook_function(S_front,pparenthookcall[.LINE = $(pparenthookcall.LINE + 1)]) = eps
$parent_hook_function(S_front,pparenthookcall[.CLASS = porigin_grand]) = eps
$parent_hook_function(S_front,pparenthookcall[.PROPERTY = ppropertyhook.PROPERTY]) = eps
$parent_hook_function(S_front,pparenthookcall[.CALLER = pcallcontext_child[.RECEIVER = eps]]) = eps
$parent_hook_function(S_front,pparenthookcall[.CALLER = pcallcontext_child[.TARGET = METHOD_TARGET n_child pfunction_child.ORIGIN]]) = eps
S_wrong = S_raw[.TODO = (CALL_ARGS (PARENT_HOOK_TARGET (pparenthookcall[.LINE = $(pparenthookcall.LINE + 1)])) eps 0 eps (pparenthookcall.SITE) pparenthookcall.LINE) :: METHOD_RESULT :: ptask_tail*]
~$call_tasks_valid(S_wrong,S_wrong.TODO)
expression_call = NExprStaticCall (NExprStaticPropertyFetch phpType19_parent phpType31_property metadata_fetch) phpType20_hook (SEQUENCE eps) metadata_call
$parent_hook_file_start(metadata_call) = (z_file)
$source_token_start(metadata_call) = (z_token)
~$parent_hook_syntax(NExprStaticCall (NExprStaticPropertyFetch phpType19_parent phpType31_property metadata_fetch) phpType20_hook (SEQUENCE eps) ([MstartFilePos $(z_file - 1),MstartTokenPos $(z_token - 1)] ++ metadata_call))
'''.strip().splitlines()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', action='append', choices=('selection', 'owning', 'throwing'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'parent_get_hook_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_gate_completed']
    assert [case['id'] for case in data['cases']] == ['selection', 'owning', 'throwing', 'outside', 'wrong-property', 'trace']
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
    out = Path(tempfile.mkdtemp(prefix='parent-get-hook-protocol-', dir=ROOT / '.tools'))
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
            parent_output = {'selection':'N:C|P|ParentGetParent108|ParentGetGrand108|', 'owning':'O:C|P|', 'throwing':'X:C|P|'}[name]
            setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $pg_seek(S_initial,PG_FRONT,1000)', r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S_front = S_found[.COMPLETION = NORMAL]',
                     'ptbytes_before_parent = $ptascii(' + json.dumps({'selection':'N:C|','owning':'O:C|','throwing':'X:C|'}[name]) + ')',
                     'ptbytes_parent = $ptascii(' + json.dumps(parent_output) + ')',
                     'ptbytes_before_child = $ptascii(' + json.dumps(parent_output + ('' if name == 'throwing' else 'A|')) + ')',
                     'ptbytes_final = $ptascii(' + json.dumps(output) + ')']
            reached = setup + COMMON
            if name == 'selection':
                reached += ['$trace_context_function(S_enter,pcallcontext_parent) = $ptascii("$value::get")',
                            '$trace_context_class(S_enter,pcallcontext_parent) = ($ptascii("ParentGetParent108"))',
                            '$trace_context_type(S_enter,pcallcontext_parent) = ($ptascii("->"))']
            if name == 'throwing':
                reached += THROW + CHILD + CATCH
            else:
                reached += RETURN + CHILD + DELIVERY
                if name == 'selection':
                    reached += ['pvalue_return = PINT 41', '$lookup(S_main.ENV,$ptascii("rhs")) = (n_rhs_cell)',
                                'S_front.STORE[n_rhs_cell] = DEFINED (PINT 7)', 'S_child.STORE[n_rhs_cell] = DEFINED (PINT 7)',
                                'S_delivery.STORE[n_rhs_cell] = DEFINED (PINT 99)', 'S_end = S_delivery']
                else:
                    reached += OWNING
            reached += FINISH + [f'pparenthookcall.LINE = {case["call_line"]}']
            derived = DERIVED if name == 'selection' else []
            if name == 'selection':
                for control in [case for case in data['cases'] if case['id'] in ('outside', 'wrong-property')]:
                    control_source = HERE / control['source_file']
                    control_dir = directory / control['id']
                    control_dir.mkdir()
                    control_frontend = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(bridge), str(worker)], control_dir / 'frontend')
                    control_adapter = None
                    try:
                        control_parsed = control_frontend.request({'op':'parse', 'source':base64.b64encode(control_source.read_bytes()).decode()})
                        assert control_parsed['accepted']
                        control_adapter = Worker([str(adapter), str(ROOT)],control_dir / 'adapter')
                        control_checked = control_adapter.request({'op':'check','ast':control_parsed['ast'],'fixture':True})
                        assert control_checked['ok'] and control_checked['ast'] == control_parsed['ast']
                    finally:
                        if control_adapter:
                            control_adapter.close()
                        control_frontend.close()
                    variable = 'S_' + control['id'].replace('-','_')
                    message = base64.b64decode(control['stderr_template_base64']).decode().split('Fatal error: ',1)[1].split(' in {FILE}',1)[0]
                    reached += [variable + ' = $php_run(' + control_checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(control_source).encode()).decode()) + ')',
                                variable + '.COMPLETION = STATICBYTES $ptascii(' + json.dumps(message) + ') ' + str(control['call_line']),
                                variable + '.EVENTS = eps', variable + '.CURRENT = eps /\\ ' + variable + '.FRAMES = eps']
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
