"""Reach magic-property coalesce calls, guard changes and receiver/RV disposal."""
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
syntax ppcstage = PC_PREP | PC_ENTER bool | PC_EXIT bool | PC_RESULT bool | PC_DTOR nat | PC_DELIVERY | PC_THROW | PC_CATCH | PC_MAIN ptbytes
dec $pc_output(pevent*) : ptbytes
def $pc_output(eps) = eps
def $pc_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $pc_output(pevent*)
dec $pc_stage(pstate,ppcstage) : bool
def $pc_stage(S,PC_PREP) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) z) :: (ORIGIN_RETURN (porigin)) :: (COALESCE_QUIET expression_right z_left z_right) :: ptask_tail*
def $pc_stage(S,PC_ENTER b_get) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_COALESCE_TARGET ppropertycoalesce b_get
def $pc_stage(S,PC_EXIT b_get) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (PROPERTY_COALESCE_RESULT ppropertycoalesce b_get) :: ptask_tail*
def $pc_stage(S,PC_RESULT b_get) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce b_get) :: ptask_tail*
def $pc_stage(S,PC_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $pc_stage(S,PC_DELIVERY) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (ORIGIN_RETURN (porigin)) :: (COALESCE_RESULT expression_right z_left z_right) :: ptask_tail*
def $pc_stage(S,PC_THROW) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ptask_tail*
def $pc_stage(S,PC_CATCH) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CATCH_BIND porigin n_index n) :: ptask_tail*
def $pc_stage(S,PC_MAIN ptbytes) = (S.CURRENT = eps /\ S.FRAMES = eps /\ $pc_output(S.EVENTS) = ptbytes)
def $pc_stage(S,ppcstage) = false -- otherwise
dec $pc_seek(pstate,ppcstage,nat) : pstate
def $pc_seek(S,ppcstage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $pc_stage(S,ppcstage) \/ n = 0
def $pc_seek(S,ppcstage,n) = $pc_seek($drive_steps(S[.COMPLETION = NORMAL],1),ppcstage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$pc_stage(S,ppcstage) /\ $(n > 0)
def $pc_seek(S,ppcstage,n) = $pc_seek($drive_steps(S,1),ppcstage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $pc_seek(S,ppcstage,n) = S -- otherwise
dec $pc_after(pstate,pstate) : pstate
def $pc_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $pc_guard(pstate) : bool
def $pc_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $gc_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $pc_in_isset(pstate,nat) : bool
def $pc_in_isset(S,n) = $property_isset_guard(S,S.CURRENT,S.FRAMES,n,$ptascii("value"))
dec $pc_in_get(pstate,nat) : bool
def $pc_in_get(S,n) = ($property_get_guard_tasks(S.TODO,n,$ptascii("value")) \/ $property_get_guard_frames(S.FRAMES,n,$ptascii("value")) \/ $property_empty_get_active(S,n,$ptascii("value")))
'''

def lines(text): return [line for line in text.strip().splitlines() if line]
def reach(name, previous, stage):
    return [f'{name}_found = $pc_seek({previous},{stage},2000)',
            fr'{name}_found.COMPLETION = NORMAL \/ {name}_found.COMPLETION = BUDGET',
            f'{name} = {name}_found[.COMPLETION = NORMAL]', f'$pc_stage({name},{stage})']

COMMON = lines(r'''
S_prep.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) z_site) :: (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_QUIET expression_right z_left z_right) :: ptask_tail*
$base64(text_name) = $ptascii("value")
S_prep.RESULT = VARIABLE ($ptascii("child")) z_child
$lookup(S_prep.ENV,$ptascii("child")) = (n_child_cell)
S_prep.STORE[n_child_cell] = DEFINED (POBJECT n_child)
$lookup(S_prep.ENV,$ptascii("error")) = (n_error_cell)
S_prep.STORE[n_error_cell] = DEFINED (POBJECT n_error)
$lookup(S_prep.ENV,$ptascii("result")) = (n_result_cell)
S_prep.STORE[n_result_cell] = DEFINED (PINT 42)
$property_coalesce_plan(S_prep) = (ppropertycoalesce)
porigin_site = ppropertycoalesce.SITE
S_prep.ORIGIN = (porigin_site)
ppropertycoalesce.OBJECT = n_child /\ ppropertycoalesce.LINE = z_site /\ z_site = z_left
ppropertycoalesce.CALLER = eps /\ ppropertycoalesce.OWNER = 0
ppropertycoalesce.TAIL = (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_QUIET expression_right z_left z_right) :: ptask_tail*
$property_coalesce_prepare(S_prep) /\ $property_empty_prepare(S_prep) /\ ~$property_get_pending(S_prep)
$pc_output(S_prep.EVENTS) = ptbytes_prefix /\ $heap_owners($heap_graph(S_prep),HOBJECT n_child) = 1
~$pc_in_isset(S_prep,n_child) /\ ~$pc_in_get(S_prep,n_child) /\ $pc_guard(S_prep)
PhpStep: S_prep ~> S_call_raw
S_call = $pc_after(S_prep,S_call_raw)
$property_coalesce_pending_call(S_call,ppropertycoalesce,false)
$property_coalesce_capture(S_call,ppropertycoalesce) /\ $property_coalesce_valid(S_call,ppropertycoalesce)
$property_isset_method(S_call,n_child) = (pmethoddesc_isset)
$property_get_method(S_call,n_child) = (pmethoddesc_get)
$property_magic_method_source(S_call,pmethoddesc_isset,"__isset") /\ $property_empty_get_source(S_call,pmethoddesc_get)
$target_function(S_call,PROPERTY_COALESCE_TARGET ppropertycoalesce false) = (pmethoddesc_isset.FUNCTION)
$target_function(S_call,PROPERTY_COALESCE_TARGET ppropertycoalesce true) = (pmethoddesc_get.FUNCTION)
$target_nodes(PROPERTY_COALESCE_TARGET ppropertycoalesce false) = eps
$task_nodes(PROPERTY_COALESCE_RESULT ppropertycoalesce false) = [HOBJECT n_child]
$heap_owners($heap_graph(S_call),HOBJECT n_child) = 2 /\ $pc_guard(S_call)
''')
ISSET_ENTER = lines(r'''
S_isset_enter.CURRENT = (pcallcontext_isset)
pcallcontext_isset.TARGET = PROPERTY_COALESCE_TARGET ppropertycoalesce false
pcallcontext_isset.LEXICAL_CLASS = (pmethoddesc_isset.OWNER) /\ pcallcontext_isset.CALLED_CLASS = (ppropertycoalesce.CLASS)
pmethoddesc_isset.OWNER =/= ppropertycoalesce.CLASS
$target_function(S_isset_enter,pcallcontext_isset.TARGET) = (pmethoddesc_isset.FUNCTION)
$receiving_function(S_isset_enter,pmethoddesc_isset.FUNCTION.ORIGIN) = (pmethoddesc_isset.FUNCTION)
$pc_in_isset(S_isset_enter,n_child) /\ ~$pc_in_get(S_isset_enter,n_child) /\ $pc_guard(S_isset_enter)
''')
ISSET_EXIT = lines(r'''
S_isset_exit.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_isset) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe_isset) :: (PROPERTY_COALESCE_RESULT ppropertycoalesce false) :: ptask_isset_tail*
pdestructionframe_isset.FUNCTION = ppropertycoalesce.ISSET
pdestructionframe_isset.VALUE = KNOWN (PBOOL b_isset) /\ pdestructionframe_isset.PENDING = eps
$property_coalesce_exit(S_isset_exit,S_isset_exit.TODO,ppropertycoalesce,false) = (pdestructionframe_isset)
pdestructionframe_isset <- S_isset_exit.DESTRUCTION.FRAMES
S_isset_exit.STORE[n_child_cell] = DEFINED PNULL
$heap_owners($heap_graph(S_isset_exit),HOBJECT n_child) = 1
~$property_coalesce_capture(S_isset_exit,ppropertycoalesce)
$pc_output(S_isset_exit.EVENTS) = ptbytes_isset
$pc_in_isset(S_isset_exit,n_child) /\ ~$pc_in_get(S_isset_exit,n_child) /\ $pc_guard(S_isset_exit)
''')
ISSET_RESULT = lines(r'''
S_isset_result.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce false) :: ptask_isset_tail*
S_isset_result.RESULT = KNOWN (PBOOL b_isset)
$property_coalesce_valid(S_isset_result,ppropertycoalesce) /\ ~$property_coalesce_capture(S_isset_result,ppropertycoalesce)
~$pc_in_isset(S_isset_result,n_child) /\ ~$pc_in_get(S_isset_result,n_child)
$heap_owners($heap_graph(S_isset_result),HOBJECT n_child) = 1 /\ $pc_guard(S_isset_result)
''')
GET_CALL = lines(r'''
PhpStep: S_isset_result ~> S_get_call_raw
S_get_call = $pc_after(S_isset_result,S_get_call_raw)
$property_coalesce_pending_call(S_get_call,ppropertycoalesce,true)
~$property_coalesce_capture(S_get_call,ppropertycoalesce)
$heap_owners($heap_graph(S_get_call),HOBJECT n_child) = 1 /\ $pc_guard(S_get_call)
''')
GET_ENTER = lines(r'''
S_get_enter.CURRENT = (pcallcontext_get)
pcallcontext_get.TARGET = PROPERTY_COALESCE_TARGET ppropertycoalesce true
pcallcontext_get.LEXICAL_CLASS = (pmethoddesc_get.OWNER) /\ pcallcontext_get.CALLED_CLASS = (ppropertycoalesce.CLASS)
$property_coalesce_context(S_get_enter,pcallcontext_get)
~$pc_in_isset(S_get_enter,n_child) /\ $pc_in_get(S_get_enter,n_child) /\ $pc_guard(S_get_enter)
$heap_owners($heap_graph(S_get_enter),HOBJECT n_child) = 1
''')
GET_EXIT = lines(r'''
S_get_exit.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_get) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe_get) :: (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ptask_get_tail*
pdestructionframe_get.FUNCTION = pmethoddesc_get.FUNCTION.ORIGIN
$property_coalesce_exit(S_get_exit,S_get_exit.TODO,ppropertycoalesce,true) = (pdestructionframe_get)
pdestructionframe_get <- S_get_exit.DESTRUCTION.FRAMES
~$pc_in_isset(S_get_exit,n_child) /\ $pc_in_get(S_get_exit,n_child) /\ $pc_guard(S_get_exit)
$pc_output(S_get_exit.EVENTS) = ptbytes_get
''')
GET_RESULT = lines(r'''
S_get_result.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ptask_get_tail*
S_get_result.RESULT = KNOWN pvalue_return
S_get_result.BASE = BASE_VALUE (KNOWN PNULL)
~$pc_in_isset(S_get_result,n_child) /\ ~$pc_in_get(S_get_result,n_child)
$heap_owners($heap_graph(S_get_result),HOBJECT n_child) = 1 /\ $pc_guard(S_get_result)
S_before_release = S_get_result
b_get = true
''')
RELEASE = lines(r'''
PhpStep: S_before_release ~> S_release_raw
S_release_raw.TODO = (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_RESULT expression_right z_left z_right) :: ptask_tail*
S_release_raw.RESULT = KNOWN pvalue_return /\ S_release_raw.BASE = BASE_VALUE (KNOWN PNULL)
$heap_owners($heap_graph(S_release_raw),HOBJECT n_child) = 0
S_disposing = $pc_after(S_before_release,S_release_raw)
''')
CHILD = lines(r'''
$pc_output(S_child.EVENTS) = ptbytes_before_dtor
~$pc_in_isset(S_child,n_child) /\ ~$pc_in_get(S_child,n_child)
S_child.CURRENT = (pcallcontext_child)
$destructor_context_call(pcallcontext_child,S_child.CURRENT,S_child.FRAMES) = (pdestructorcall_child)
pdestructorcall_child.OPERATION = (pdestructionoperation_child)
pdestructionoperation_child.SOURCE = PROPERTY_COALESCE_RESULT ppropertycoalesce b_get
pdestructionoperation_child.VALUE = KNOWN pvalue_return
pdestructionoperation_child.BASE = BASE_VALUE (KNOWN PNULL)
$pc_guard(S_child)
''')
DELIVERY = lines(r'''
S_delivery.TODO = (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_RESULT expression_right z_left z_right) :: ptask_tail*
S_delivery.RESULT = KNOWN pvalue_return /\ S_delivery.BASE = BASE_VALUE (KNOWN PNULL)
~(HOBJECT n_child <- S_delivery.ALLOCATIONS)
S_delivery.STORE[n_child_cell] = DEFINED PNULL
$lookup(S_delivery.ENV,$ptascii("fallback")) = (n_fallback_cell)
S_delivery.STORE[n_fallback_cell] = DEFINED (PINT 99)
$pc_output(S_delivery.EVENTS) = ptbytes_before_dtor ++ $ptascii("D|")
~$pc_in_isset(S_delivery,n_child) /\ ~$pc_in_get(S_delivery,n_child) /\ $pc_guard(S_delivery)
S_end = S_delivery
''')
THROW = lines(r'''
S_throw.TODO = (THROW_SEARCH n_error) :: (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ptask_throw_tail*
$property_coalesce_throw_tail(S_throw,ppropertycoalesce,true)
S_throw.STORE[n_result_cell] = DEFINED (PINT 42)
~$pc_in_isset(S_throw,n_child) /\ ~$pc_in_get(S_throw,n_child) /\ $pc_guard(S_throw)
PhpStep: S_throw ~> S_throw_raw
S_throw_raw.TODO = (THROW_SEARCH n_error) :: ptask_throw_tail*
S_throw_raw.RESULT = KNOWN PNULL /\ S_throw_raw.BASE = BASE_VALUE (KNOWN PNULL)
$heap_owners($heap_graph(S_throw_raw),HOBJECT n_child) = 0
S_disposing = $pc_after(S_throw,S_throw_raw)
''')
CATCH = lines(r'''
S_catch.TODO = (CATCH_BIND porigin_catch n_index n_error) :: ptask_catch_tail*
S_catch.STORE[n_result_cell] = DEFINED (PINT 42)
S_catch.STORE[n_error_cell] = DEFINED (POBJECT n_error)
~(HOBJECT n_child <- S_catch.ALLOCATIONS)
$pc_output(S_catch.EVENTS) = ptbytes_get ++ $ptascii("D|")
$pc_guard(S_catch)
S_end = S_catch
''')
FINISH = lines(r'''
S_final = $drive_steps(S_end,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$pc_output(S_final.EVENTS) = ptbytes_final
~(HOBJECT n_child <- S_final.ALLOCATIONS) /\ $pc_guard(S_final)
S_budget = $drive_steps(S_prep,0)
S_budget.COMPLETION = BUDGET /\ S_budget.TODO = S_prep.TODO /\ S_budget.EVENTS = S_prep.EVENTS
$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final
''')
REFUSALS = lines(r'''
S_source = S_prep[.ORIGIN = eps]
$property_coalesce_plan(S_source) = eps /\ ~$property_coalesce_prepare(S_source)
S_mode = S_prep[.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) z_site) :: (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_RESULT expression_right z_left z_right) :: ptask_tail*]
$property_coalesce_plan(S_mode) = eps
ppropertycoalesce_line = ppropertycoalesce[.LINE = $(z_site + 1)]
~$property_coalesce_source(S_call,ppropertycoalesce_line)
ppropertycoalesce_tail = ppropertycoalesce[.TAIL = eps]
~$property_coalesce_source(S_call,ppropertycoalesce_tail)
ppropertycoalesce_caller = ppropertycoalesce[.CALLER = (pcallcontext_isset)]
~$property_coalesce_valid(S_isset_result,ppropertycoalesce_caller)
S_isset_exit.DESTRUCTION.FRAMES = pdestructionframe_isset :: pdestructionframe_tail*
pdestructionframe_wrong = pdestructionframe_isset[.FUNCTION = pmethoddesc_get.FUNCTION.ORIGIN]
S_wrong_exit = S_isset_exit[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_isset) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe_wrong) :: (PROPERTY_COALESCE_RESULT ppropertycoalesce false) :: ptask_isset_tail*][.DESTRUCTION.FRAMES = pdestructionframe_wrong :: pdestructionframe_tail*]
$property_coalesce_exit(S_wrong_exit,S_wrong_exit.TODO,ppropertycoalesce,false) = eps
~$pc_in_isset(S_wrong_exit,n_child) /\ ~$call_task_valid(S_wrong_exit,PROPERTY_COALESCE_RESULT ppropertycoalesce false)
''')
ZERO_BRIDGE = lines(r'''
S_zero = S_delivery[.TODO = (COALESCE_RESULT expression_right z_left z_right) :: ptask_tail*][.ORIGIN = (porigin_parent)][.RESULT = KNOWN (PINT 0)]
$pc_guard(S_zero)
PhpStep: S_zero ~> S_zero_done
S_zero_done.TODO = ptask_tail* /\ S_zero_done.RESULT = KNOWN (PINT 0) /\ S_zero_done.EVENTS = S_zero.EVENTS
''')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', action='append', choices=('false','null','owning','throwing'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_coalesce_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_gate_completed']
    assert [case['id'] for case in data['cases']] == ['false','zero','null','owning','throwing']
    selected = [case for case in data['cases'] if case['id'] in ('false','null','owning','throwing')]
    assert len(selected) == 4
    if args.case:
        selected = [case for case in selected if case['id'] in args.case]
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
               *(ROOT / name for name in ['spec/schema.json','spec/php.watsup','spec/nodes.json','frontend/target.php',
                    'frontend/wire.php','frontend/wire.py','tests/semantics/recorded_worker.py','tests/semantics/static_types.py'])]
    revision, status = git('rev-parse','HEAD'), git('status','--short')
    assert revision == args.revision and not status, (revision,status)
    before = {str(path):sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='magic-coalesce-protocol-',dir=ROOT / '.tools'))
    print(out,flush=True)
    report = {'revision':revision,'inputs':before,'profile':profile,'module_count':len(modules),
              'mode':'SL','cache':False,'det':True,'records':[],'fixtures':[],'selection':[case['id'] for case in selected],
              'application_invocations':0,'application_evaluations':0,'source_agreements':0,
              'premises':0,'reached_premises':0,'derived_premises':0,'cap_seconds':90,
              'environment':{'LC_ALL':'C','TZ':'UTC','PHP_SPEC_SCRIPT_ENCODING':'absent','jobs':1},'passed':False}
    try:
        flags = [part for key,value in profile.items() for part in ('-d',key+'='+value)]
        for case in selected:
            name = case['id']
            source = HERE / case['source_file']
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256']
            native_stderr = base64.b64decode(case['stderr_template_base64']).replace(b'{FILE}',case['original_source'].encode())
            native_tuple = base64.b64decode(case['stdout_base64'])+b'\0'+native_stderr+b'\0'+str(case['exit_status']).encode()
            assert hashlib.sha256(native_tuple).hexdigest() == case['native_raw_sha256']
            directory = out / name
            directory.mkdir()
            frontend = Worker([str(php),'-n',*flags,'-d','extension='+str(bridge),str(worker)],directory / 'frontend')
            adapter_worker = None
            try:
                parsed = frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted'],parsed
                adapter_worker = Worker([str(adapter),str(ROOT)],directory / 'adapter')
                checked = adapter_worker.request({'op':'check','ast':parsed['ast'],'fixture':True})
                assert checked['ok'] and checked['ast'] == parsed['ast']
            finally:
                if adapter_worker:
                    adapter_worker.close()
                frontend.close()
            prefix = {'false':'F:','null':'N:','owning':'O:','throwing':'X:'}[name]
            before_dtor = prefix+'I|'+('G|' if name != 'false' else '')
            reached = ['S_initial = $php_run('+checked['fixture']+',0,'+json.dumps(base64.b64encode(str(source).encode()).decode())+')',
                       r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET']
            reached += reach('S_prep','S_initial','PC_PREP')
            reached += ['ptbytes_prefix = $ptascii('+json.dumps(prefix)+')',
                        'ptbytes_isset = $ptascii('+json.dumps(prefix+'I|')+')',
                        'ptbytes_get = $ptascii('+json.dumps(prefix+'I|G|')+')',
                        'ptbytes_before_dtor = $ptascii('+json.dumps(before_dtor)+')',
                        'ptbytes_final = $ptascii('+json.dumps(base64.b64decode(case['stdout_base64']).decode())+')',
                        'b_isset = '+('false' if name == 'false' else 'true')]
            reached += COMMON + [f'z_site = {case["coalesce_line"]}']
            reached += reach('S_isset_enter','S_call','PC_ENTER false') + ISSET_ENTER
            reached += reach('S_isset_exit','S_isset_enter','PC_EXIT false') + ISSET_EXIT
            reached += reach('S_isset_result','S_isset_exit','PC_RESULT false') + ISSET_RESULT
            if name != 'false':
                reached += GET_CALL + reach('S_get_enter','S_get_call','PC_ENTER true') + GET_ENTER
                reached += reach('S_get_exit','S_get_enter','PC_EXIT true') + GET_EXIT
                if name == 'throwing':
                    reached += ['pdestructionframe_get.PENDING = (n_error)']
                else:
                    reached += ['pdestructionframe_get.PENDING = eps']
                    if name == 'owning':
                        reached += ['pdestructionframe_get.VALUE = KNOWN (POBJECT n_payload)',
                                    'pvalue_return = POBJECT n_payload',
                                    '$heap_owners($heap_graph(S_get_exit),HOBJECT n_payload) = 1']
                    else:
                        reached += ['pvalue_return = PNULL','pdestructionframe_get.VALUE = KNOWN pvalue_return']
                    reached += reach('S_get_result','S_get_exit','PC_RESULT true') + GET_RESULT
            else:
                reached += ['S_before_release = S_isset_result','pvalue_return = PNULL','b_get = false']
            if name == 'throwing':
                reached += reach('S_throw','S_get_exit','PC_THROW') + THROW
                reached += reach('S_child','S_disposing','PC_DTOR n_child')
                reached += ['$pc_output(S_child.EVENTS) = ptbytes_get',
                            r'~$pc_in_isset(S_child,n_child) /\ ~$pc_in_get(S_child,n_child) /\ $pc_guard(S_child)']
                reached += reach('S_catch','S_child','PC_CATCH') + CATCH
            else:
                reached += RELEASE + reach('S_child','S_disposing','PC_DTOR n_child') + CHILD
                if name == 'owning':
                    reached += ['$heap_owners($heap_graph(S_child),HOBJECT n_payload) = 1']
                reached += reach('S_delivery','S_child','PC_DELIVERY') + (DELIVERY[:-1] if name == 'owning' else DELIVERY)
                if name == 'owning':
                    reached += ['$heap_owners($heap_graph(S_delivery),HOBJECT n_payload) = 1']
                    reached += reach('S_main','S_delivery','PC_MAIN ($ptascii("O:I|G|D|A|"))')
                    reached += ['S_main.STORE[n_result_cell] = DEFINED (POBJECT n_payload)',
                                r'$heap_owners($heap_graph(S_main),HOBJECT n_payload) = 1 /\ $pc_guard(S_main)']
                    reached += reach('S_payload','S_main','PC_DTOR n_payload')
                    reached += ['$pc_output(S_payload.EVENTS) = $ptascii("O:I|G|D|A|")',
                                r'S_payload.STORE[n_result_cell] = DEFINED PNULL /\ $pc_guard(S_payload)',
                                'S_end = S_payload']
            reached += FINISH
            if name in ('false','null'):
                reached += ['S_final.STORE[n_result_cell] = DEFINED (PINT 99)']
            elif name == 'owning':
                reached += ['~(HOBJECT n_payload <- S_final.ALLOCATIONS)']
            else:
                reached += ['S_final.STORE[n_result_cell] = DEFINED (PINT 42)']
            derived = REFUSALS + ZERO_BRIDGE if name == 'null' else []
            content = PREFIX+'\ndec $main() : bool\ndef $main() = true\n'
            for condition in reached+derived:
                content += '  -- '+('' if condition.startswith('PhpStep:') else 'if ')+condition+'\n'
            content += 'def $main() = false -- otherwise\n'
            fixture = directory / 'hook.watsup'
            fixture.write_text(content)
            row = {'id':name,'path':str(fixture),'sha256':sha(fixture),'reached_premises':len(reached),
                   'derived_premises':len(derived),'premises':len(reached)+len(derived)}
            report['fixtures'].append(row)
            for key in ('premises','reached_premises','derived_premises'):
                report[key] += row[key]
        report.update(prepared=True,passed=True)
        if not args.prepare_only:
            for fixture in report['fixtures']:
                directory = Path(fixture['path']).parent
                process = recorder.recorded([str(compiler),'algo',*map(str,modules),fixture['path']],directory / 'compiler',90)
                passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and not (directory / 'compiler.stderr').read_bytes() and b'\ndef $main : bool =\n' in (directory / 'compiler.stdout').read_bytes()
                report['records'].append({'id':fixture['id']+'-algorithmic-compilation','process':process,'passed':passed,'application_evaluations':0})
                report['passed'] = passed
                assert passed
                report['application_invocations'] += 1
                process = recorder.recorded([str(runner),'--sl',*map(str,modules),fixture['path']],directory / 'state',90)
                output = (directory / 'state.stdout').read_bytes()
                evaluated = process['exit'] == 0 and output in (b'true\n',b'false\n')
                report['application_evaluations'] += int(evaluated)
                passed = evaluated and not process['timeout'] and not process['group_after'] and not (directory / 'state.stderr').read_bytes() and output == b'true\n'
                report['records'].append({'id':fixture['id']+'-strict-SL-application','process':process,'passed':passed})
                report['passed'] = passed
                assert passed
    finally:
        report.update(inputs_stable=before == {str(path):sha(path) for path in watched},
                      fixtures_stable=all(row['sha256'] == sha(Path(row['path'])) for row in report['fixtures']),
                      head_stable=revision == git('rev-parse','HEAD'),status_stable=status == git('status','--short'))
        report['passed'] = report['passed'] and all(report[key] for key in ('inputs_stable','fixtures_stable','head_stable','status_stable'))
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({key:report[key] for key in ('passed','application_evaluations','premises','reached_premises','derived_premises','inputs_stable','head_stable','status_stable')}),flush=True)
    assert report['passed']

if __name__ == '__main__':
    main()
