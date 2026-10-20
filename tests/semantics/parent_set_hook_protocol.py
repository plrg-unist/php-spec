"""Check real parent-set argument reception, borrowed This and assignment delivery."""
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
syntax pparentsetstage = PS_FRONT | PS_MUTATE | PS_RECEIVE | PS_BODY | PS_RETURN | PS_THROW | PS_INNER porigin | PS_DELIVERY | PS_DTOR nat | PS_CATCH
dec $ps_output(pevent*) : ptbytes
def $ps_output(eps) = eps
def $ps_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $ps_output(pevent*)
dec $ps_stage(pstate,pparentsetstage) : bool
def $ps_stage(S,PS_FRONT) = true
  -- if S.TODO = (EVAL expression) :: ptask*
  -- if $parent_set_hook_arg(expression) =/= eps
def $ps_stage(S,PS_MUTATE) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("mutate109")
  -- if S.TODO = (RETURN_UNWIND (KNOWN pvalue) porigin?) :: ptask*
def $ps_stage(S,PS_RECEIVE) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PARENT_HOOK_TARGET pparenthookcall
  -- if S.TODO = (TYPE_RECEIVE pparenthookcall.HOOK 0) :: ptask*
def $ps_stage(S,PS_BODY) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PARENT_HOOK_TARGET pparenthookcall
  -- if S.TODO = (STMT statement) :: ptask*
def $ps_stage(S,PS_RETURN) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PARENT_HOOK_TARGET pparenthookcall
  -- if S.TODO = (RETURN_UNWIND (KNOWN PNULL) porigin?) :: ptask*
def $ps_stage(S,PS_THROW) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PARENT_HOOK_TARGET pparenthookcall
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask*
def $ps_stage(S,PS_INNER porigin) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.FUNCTION = porigin
  -- if S.TODO = METHOD_RESULT :: ptask*
def $ps_stage(S,PS_DELIVERY) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_SET_RESULT ppropertyhook pvalue) :: ptask*
def $ps_stage(S,PS_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $ps_stage(S,PS_CATCH) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask*
def $ps_stage(S,pparentsetstage) = false -- otherwise
dec $ps_seek(pstate,pparentsetstage,nat) : pstate
def $ps_seek(S,pparentsetstage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $ps_stage(S,pparentsetstage) \/ n = 0
def $ps_seek(S,pparentsetstage,n) = $ps_seek($drive_steps(S[.COMPLETION = NORMAL],1),pparentsetstage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$ps_stage(S,pparentsetstage) /\ $(n > 0)
def $ps_seek(S,pparentsetstage,n) = $ps_seek($drive_steps(S,1),pparentsetstage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $ps_seek(S,pparentsetstage,n) = S -- otherwise
dec $ps_after(pstate,pstate) : pstate
def $ps_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $ps_guard(pstate) : bool
def $ps_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $gc_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''

COMMON = r'''
S_front.TODO = (EVAL expression_call) :: ptask_tail*
S_front.CURRENT = (pcallcontext_child)
pcallcontext_child.TARGET = PROPERTY_SET_TARGET ppropertyhook
pcallcontext_child.RECEIVER = (n_child)
S_front.FRAMES = pframe_main :: eps
S_main = $constant_frame_scope(S_front,pframe_main,eps)
S_main.CURRENT = eps
S_main.TODO = (PROPERTY_SET_RESULT ppropertyhook (PINT 20)) :: ptask_main_tail*
$lookup(S_main.ENV,$ptascii("child")) = (n_child_cell)
$lookup(S_main.ENV,$ptascii("result")) = (n_result_cell)
$lookup(S_main.ENV,$ptascii("rhs")) = (n_rhs_cell)
S_front.STORE[n_child_cell] = DEFINED (POBJECT n_child) /\ S_front.STORE[n_result_cell] = DEFINED (PINT 42)
S_front.STORE[n_rhs_cell] = DEFINED (PINT 7)
$lookup(S_front.ENV,$ptascii("value")) = (n_child_parameter_cell)
S_front.STORE[n_child_parameter_cell] = DEFINED (PINT 20)
$parent_hook_plan(S_front) = (pparenthookcall)
pparenthookcall.CALLER = pcallcontext_child /\ pparenthookcall.OBJECT = n_child
$parent_set_hook_function(S_front,pparenthookcall) = (pfunction_parent)
$parent_hook_function(S_front,pparenthookcall) = (pfunction_parent)
$parent_set_hook_arg(expression_call) = (phpType7)
pcallcontext_child.LEXICAL_CLASS = (porigin_child)
$class_at(S_front.CLASSES,porigin_child) = (pclassdesc_child)
pclassdesc_child.NAME = $ptascii("ParentSetChild109")
$property_set_function(S_front,ppropertyhook) = (pfunction_child)
pfunction_child.ORIGIN = pcallcontext_child.FUNCTION
S_front.OBJECTS[n_child] = INSTANCE porigin_grand
$class_at(S_front.CLASSES,porigin_grand) = (pclassdesc_grand)
pclassdesc_grand.NAME = $ptascii("ParentSetGrand109") /\ pcallcontext_child.CALLED_CLASS = (porigin_grand)
$class_at(S_front.CLASSES,pparenthookcall.CLASS) = (pclassdesc_parent)
pclassdesc_parent.NAME = $ptascii("ParentSetParent109")
$class_link_at(S_front.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT pparenthookcall.CLASS)
$hook_property_at(pclassdesc_parent.PROPERTIES,pparenthookcall.PROPERTY) = (ppropertydesc_parent)
$property_effective_desc(S_front,n_child,$ptascii("value")) = (ppropertydesc_child)
ppropertydesc_child.ORIGIN = ppropertyhook.PROPERTY /\ ppropertyhook.HOOK = pfunction_child.ORIGIN
$property_set_virtual_edge(S_front,ppropertydesc_parent,ppropertydesc_child)
$property_hook_virtual(S_front,ppropertydesc_parent) /\ $property_hook_virtual(S_front,ppropertydesc_child)
$call_receiver_roots(pcallcontext_child) = eps /\ $call_context_roots((pcallcontext_child)) = eps
$heap_owners($heap_graph(S_front),HOBJECT n_child) = 2 /\ $ps_guard(S_front)
PhpStep: S_front ~> S_raw_step
S_raw_step.TODO = (CALL_ARGS (PARENT_HOOK_TARGET pparenthookcall) ([phpType7]) 0 eps (pparenthookcall.SITE) pparenthookcall.LINE) :: METHOD_RESULT :: ptask_tail*
S_raw = $ps_after(S_front,S_raw_step)
$parent_hook_pending(S_raw,pparenthookcall) /\ $call_selected_valid(S_raw,PARENT_HOOK_TARGET pparenthookcall,(pparenthookcall.SITE))
$target_nodes(PARENT_HOOK_TARGET pparenthookcall) = eps /\ $target_instance(PARENT_HOOK_TARGET pparenthookcall) = eps
$heap_owners($heap_graph(S_raw),HOBJECT n_child) = 2 /\ $ps_guard(S_raw)
S_mutate_found = $ps_seek(S_raw,PS_MUTATE,1000)
S_mutate_found.COMPLETION = NORMAL \/ S_mutate_found.COMPLETION = BUDGET
S_mutate = S_mutate_found[.COMPLETION = NORMAL]
S_mutate.CURRENT = (pcallcontext_mutate)
pcallcontext_mutate.NAME = $ptascii("mutate109") /\ pcallcontext_mutate.RECEIVER = eps
S_mutate.TODO = (RETURN_UNWIND (KNOWN pvalue_argument) porigin_argument?) :: ptask_mutate_tail*
S_mutate.STORE[n_child_cell] = DEFINED PNULL /\ S_mutate.STORE[n_rhs_cell] = DEFINED (PINT 99)
S_mutate.STORE[n_result_cell] = DEFINED (PINT 42)
$ps_output(S_mutate.EVENTS) = ptbytes_before_parent
$parent_set_hook_function(S_mutate,pparenthookcall) = (pfunction_parent)
$parent_hook_plan(S_mutate) = eps /\ ~$parent_hook_pending(S_mutate,pparenthookcall)
S_mutate.FRAMES = pframe_argument :: pframe_main :: eps
pframe_argument.CONTEXT = (pcallcontext_child)
S_projected = $constant_frame_scope(S_mutate,pframe_argument,([pframe_main]))
$parent_hook_pending(S_projected,pparenthookcall)
$heap_owners($heap_graph(S_mutate),HOBJECT n_child) = 1 /\ $ps_guard(S_mutate)
S_receive_found = $ps_seek(S_mutate,PS_RECEIVE,1000)
S_receive_found.COMPLETION = NORMAL \/ S_receive_found.COMPLETION = BUDGET
S_receive = S_receive_found[.COMPLETION = NORMAL]
S_receive.TODO = (TYPE_RECEIVE pparenthookcall.HOOK 0) :: eps
S_receive.CURRENT = (pcallcontext_parent)
pcallcontext_parent.TARGET = PARENT_HOOK_TARGET pparenthookcall
pcallcontext_parent.RECEIVER = (n_child) /\ pcallcontext_parent.INSTANCE = eps /\ pcallcontext_parent.ARGC = 1
pcallcontext_parent.LEXICAL_CLASS = (pparenthookcall.CLASS) /\ pcallcontext_parent.CALLED_CLASS = (porigin_grand)
$call_receiver_roots(pcallcontext_parent) = eps /\ $call_context_roots((pcallcontext_parent)) = eps
$parent_hook_entered(S_receive,S_receive.CURRENT,S_receive.FRAMES,pparenthookcall)
$target_function(S_receive,pcallcontext_parent.TARGET) = (pfunction_parent)
$receiving_function(S_receive,pparenthookcall.HOOK) = (pfunction_parent)
$default_parameter_line(S_receive,pparenthookcall.HOOK,0) = 5
$property_private_scope(S_receive,n_child,$ptascii("secret"),(pparenthookcall.CLASS)) = (ppropertydesc_parent_secret)
$property_lexical_private(S_receive,n_child,$ptascii("secret")) = (ppropertydesc_parent_secret)
$objectprops_record_at(S_receive.OBJECTPROPS,n_child) = (pobjectprops_receive)
$property_slot_at(pobjectprops_receive.SLOTS,ppropertydesc_parent_secret.KEY) = (ppropertyslot_receive)
ppropertyslot_receive.STATE = PROP_VALUE (DIRECT (PINT 41))
$lookup(S_receive.ENV,$ptascii("value")) = (n_parameter_cell)
S_receive.STORE[n_parameter_cell] = DEFINED pvalue_argument
n_parameter_cell =/= n_child_parameter_cell
S_receive.STORE[n_child_parameter_cell] = DEFINED (PINT 20)
$trace_context_function(S_receive,pcallcontext_parent) = $ptascii("$value::set")
$trace_context_class(S_receive,pcallcontext_parent) = ($ptascii("ParentSetParent109"))
$trace_context_type(S_receive,pcallcontext_parent) = ($ptascii("->"))
$ps_output(S_receive.EVENTS) = ptbytes_before_parent
$heap_owners($heap_graph(S_receive),HOBJECT n_child) = 1 /\ $ps_guard(S_receive)
'''.strip().splitlines()

NORMAL = r'''
pvalue_argument = PINT 7
S_body_found = $ps_seek(S_receive,PS_BODY,1000)
S_body_found.COMPLETION = NORMAL \/ S_body_found.COMPLETION = BUDGET
S_body = S_body_found[.COMPLETION = NORMAL]
$ps_stage(S_body,PS_BODY) /\ S_body.CURRENT = (pcallcontext_parent)
$ps_output(S_body.EVENTS) = ptbytes_before_parent /\ $ps_guard(S_body)
'''.strip().splitlines()

RETURN = r'''
S_return_found = $ps_seek(S_body,PS_RETURN,1000)
S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET
S_return = S_return_found[.COMPLETION = NORMAL]
S_return.CURRENT = (pcallcontext_parent)
S_return.TODO = (RETURN_UNWIND (KNOWN PNULL) porigin_return?) :: ptask_return*
$ps_output(S_return.EVENTS) = ptbytes_parent
$objectprops_record_at(S_return.OBJECTPROPS,n_child) = (pobjectprops_return)
$property_slot_at(pobjectprops_return.SLOTS,ppropertydesc_parent_secret.KEY) = (ppropertyslot_return)
ppropertyslot_return.STATE = PROP_VALUE (DIRECT (PINT 7))
$heap_owners($heap_graph(S_return),HOBJECT n_child) = 1 /\ $ps_guard(S_return)
S_inner_found = $ps_seek(S_return,PS_INNER pfunction_child.ORIGIN,1000)
S_inner_found.COMPLETION = NORMAL \/ S_inner_found.COMPLETION = BUDGET
S_inner = S_inner_found[.COMPLETION = NORMAL]
S_inner.CURRENT = (pcallcontext_child) /\ S_inner.FRAMES = pframe_main :: eps
S_inner.TODO = METHOD_RESULT :: ptask_tail*
S_inner.RESULT = KNOWN PNULL
S_inner.STORE[n_child_parameter_cell] = DEFINED (PINT 20)
$ps_output(S_inner.EVENTS) = ptbytes_parent /\ $ps_guard(S_inner)
S_delivery_found = $ps_seek(S_inner,PS_DELIVERY,1000)
S_delivery_found.COMPLETION = NORMAL \/ S_delivery_found.COMPLETION = BUDGET
S_delivery = S_delivery_found[.COMPLETION = NORMAL]
S_delivery.TODO = (PROPERTY_SET_RESULT ppropertyhook (PINT 20)) :: ptask_main_tail*
S_delivery.RESULT = KNOWN PNULL /\ S_delivery.CURRENT = eps /\ S_delivery.FRAMES = eps
S_delivery.STORE[n_result_cell] = DEFINED (PINT 42)
$ps_output(S_delivery.EVENTS) = ptbytes_before_child
$heap_owners($heap_graph(S_delivery),HOBJECT n_child) = 1 /\ $ps_guard(S_delivery)
PhpStep: S_delivery ~> S_delivery_raw
S_delivery_raw.RESULT = KNOWN (PINT 20)
S_before_child = $ps_after(S_delivery,S_delivery_raw)
'''.strip().splitlines()

THROW = r'''
$lookup(S_main.ENV,$ptascii("error")) = (n_error_cell)
S_front.STORE[n_error_cell] = DEFINED (POBJECT n_error)
S_throw_found = $ps_seek(S_body,PS_THROW,1000)
S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET
S_throw = S_throw_found[.COMPLETION = NORMAL]
S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_throw*
S_throw.CURRENT = (pcallcontext_parent)
S_error_read = $resolve_at(S_throw,S_throw.RESULT,z_throw)
S_error_read.RESULT = KNOWN (POBJECT n_error)
$ps_output(S_throw.EVENTS) = ptbytes_before_child /\ $ps_guard(S_throw)
PhpStep: S_throw ~> S_throw_raw
S_throw_raw.COMPLETION = THROWING n_error
S_before_child = $ps_after(S_throw,S_throw_raw)
'''.strip().splitlines()

INVALID = r'''
pvalue_argument = PARRAY n_argument
HARRAY n_argument <- S_receive.ALLOCATIONS
PhpStep: S_receive ~> S_type_raw
S_raised = $ps_after(S_receive,S_type_raw)
S_raised.COMPLETION = THROWING n_error
S_raised.OBJECTS[n_error] = THROWABLE pthrowable_error
pthrowable_error.KIND = "TypeError"
$ps_output(S_raised.EVENTS) = ptbytes_before_parent
S_before_child = S_raised
'''.strip().splitlines()

CHILD = r'''
S_child_found = $ps_seek(S_before_child,PS_DTOR n_child,1000)
S_child_found.COMPLETION = NORMAL \/ S_child_found.COMPLETION = BUDGET
S_child = S_child_found[.COMPLETION = NORMAL]
$ps_stage(S_child,PS_DTOR n_child) /\ $ps_output(S_child.EVENTS) = ptbytes_before_child
S_child.CURRENT = (pcallcontext_dtor)
$destructor_context_call(pcallcontext_dtor,S_child.CURRENT,S_child.FRAMES) = (pdestructorcall_child)
pdestructorcall_child.OPERATION = (pdestructionoperation_child)
S_child.STORE[n_result_cell] = DEFINED (PINT 42) /\ S_child.STORE[n_child_cell] = DEFINED PNULL
$ps_guard(S_child)
'''.strip().splitlines()

CATCH = r'''
pdestructionoperation_child.PENDING = (n_error)
S_catch_found = $ps_seek(S_child,PS_CATCH,1000)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_try n_catch n_error) :: ptask_catch*
S_catch.STORE[n_result_cell] = DEFINED (PINT 42)
~(HOBJECT n_child <- S_catch.ALLOCATIONS) /\ $throwable_previous_id(S_catch,n_error) = eps
$ps_guard(S_catch)
PhpStep: S_catch ~> S_catch_raw
$lookup(S_catch_raw.ENV,$ptascii("caught")) = (n_caught_cell)
S_catch_raw.STORE[n_caught_cell] = DEFINED (POBJECT n_error)
S_end = $ps_after(S_catch,S_catch_raw)
'''.strip().splitlines()

FINISH = r'''
S_final = $drive_steps(S_end,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$ps_output(S_final.EVENTS) = ptbytes_final /\ $ps_guard(S_final)
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
~$property_set_virtual_edge(S_front,ppropertydesc_parent,ppropertydesc_child[.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))]])
~$property_set_virtual_edge(S_front,ppropertydesc_parent,ppropertydesc_child[.DEFAULT = PROP_LITERAL (PINT 0)])
expression_call = NExprStaticCall phpType19_parent phpType20_hook (SEQUENCE ([phpType7])) metadata_call
$parent_set_hook_arg(NExprStaticCall phpType19_parent phpType20_hook (SEQUENCE eps) metadata_call) = eps
phpType7 = NArg ABSENT expression_argument (BOOLEAN false) (BOOLEAN false) metadata_arg
$parent_set_hook_arg(NExprStaticCall phpType19_parent phpType20_hook (SEQUENCE ([NArg ABSENT expression_argument (BOOLEAN true) (BOOLEAN false) metadata_arg])) metadata_call) = eps
$parent_set_hook_arg(NExprStaticCall phpType19_parent phpType20_hook (SEQUENCE ([NArg ABSENT expression_argument (BOOLEAN false) (BOOLEAN true) metadata_arg])) metadata_call) = eps
S_wrong = S_raw[.TODO = (CALL_ARGS (PARENT_HOOK_TARGET (pparenthookcall[.LINE = $(pparenthookcall.LINE + 1)])) ([phpType7]) 0 eps (pparenthookcall.SITE) pparenthookcall.LINE) :: METHOD_RESULT :: ptask_tail*]
~$call_tasks_valid(S_wrong,S_wrong.TODO)
'''.strip().splitlines()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', action='append', choices=('selection', 'throwing', 'invalid'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'parent_set_hook_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_gate_completed']
    assert [case['id'] for case in data['cases']] == ['selection', 'throwing', 'invalid', 'wrong-kind']
    selected = [case for case in data['cases'] if case['id'] in ('selection', 'throwing', 'invalid')]
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
    out = Path(tempfile.mkdtemp(prefix='parent-set-hook-protocol-', dir=ROOT / '.tools'))
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
            before_output = {'selection':'N:B|C|M|', 'throwing':'X:B|C|M|', 'invalid':'T:B|C|M|'}[name]
            parent_output = {'selection':'N:B|C|M|P|ParentSetParent109|ParentSetGrand109|7|', 'throwing':'X:B|C|M|P|', 'invalid':before_output}[name]
            child_output = {'selection':parent_output+'Z|99|20|A|', 'throwing':parent_output, 'invalid':before_output}[name]
            setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $ps_seek(S_initial,PS_FRONT,1000)', r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S_front = S_found[.COMPLETION = NORMAL]',
                     'ptbytes_before_parent = $ptascii(' + json.dumps(before_output) + ')',
                     'ptbytes_parent = $ptascii(' + json.dumps(parent_output) + ')',
                     'ptbytes_before_child = $ptascii(' + json.dumps(child_output) + ')',
                     'ptbytes_final = $ptascii(' + json.dumps(output) + ')']
            reached = setup + COMMON
            if name == 'invalid':
                reached += INVALID + CHILD + CATCH
            else:
                reached += NORMAL
                if name == 'selection':
                    reached += RETURN + CHILD + [
                        'pdestructionoperation_child.SOURCE = PROPERTY_SET_RESULT ppropertyhook (PINT 20)',
                        r'pdestructionoperation_child.VALUE = KNOWN (PINT 20) /\ pdestructionoperation_child.PENDING = eps',
                        'S_end = S_child']
                    reached += [
                        '$property_private_scope(S_inner,n_child,$ptascii("secret"),(porigin_child)) = (ppropertydesc_child_secret)',
                        'ppropertydesc_child_secret.KEY =/= ppropertydesc_parent_secret.KEY',
                        '$property_lexical_private(S_inner,n_child,$ptascii("secret")) = (ppropertydesc_child_secret)',
                        '$objectprops_record_at(S_inner.OBJECTPROPS,n_child) = (pobjectprops_inner)',
                        '$property_slot_at(pobjectprops_inner.SLOTS,ppropertydesc_child_secret.KEY) = (ppropertyslot_child_secret)',
                        'ppropertyslot_child_secret.STATE = PROP_VALUE (DIRECT (PINT 99))']
                else:
                    reached += THROW + CHILD + CATCH
            reached += FINISH + [f'pparenthookcall.LINE = {case["call_line"]}']
            derived = DERIVED if name == 'selection' else []
            if name == 'selection':
                for control in [case for case in data['cases'] if case['id'] == 'wrong-kind']:
                    control_source = HERE / control['source_file']
                    assert control_source.read_bytes() == control['source'].encode() and sha(control_source) == control['source_sha256']
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
