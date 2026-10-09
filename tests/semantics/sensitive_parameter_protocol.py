"""Source certificates plus reached owning trace wrappers and getter/lifetime steps."""
from pathlib import Path
import argparse, ast, base64, hashlib, json, re, subprocess, sys, tempfile
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker

PREFIX = r"""dec $sensitive_fixture_stage(pstate, nat) : bool
def $sensitive_fixture_stage(S, 0) = true
  -- if S.TODO = (EVAL (NExprNew phpType28 phpType6 metadata)) :: ptask*
  -- if S.CURRENT = (pcallcontext)
  -- if $function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction)
  -- if $sensitive_trace_parameter(S, pfunction, 0)
def $sensitive_fixture_stage(S, 1) = true
  -- if S.TODO = (GETTER_INVOKE pgettercall) :: ptask*
  -- if pgettercall.METHOD = GET_SENSITIVE_VALUE
def $sensitive_fixture_stage(S, 2) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES "d3JhcHBlcg==") metadata)) :: ptask*
def $sensitive_fixture_stage(S, 3) = true
  -- if S.TODO = METHOD_RESULT :: ptask*
def $sensitive_fixture_stage(S, n) = false -- otherwise
dec $sensitive_fixture_seek(pstate, nat, nat) : pstate
def $sensitive_fixture_seek(S, n_stage, n) = S -- if $sensitive_fixture_stage(S, n_stage)
def $sensitive_fixture_seek(S, n_stage, n) = $sensitive_fixture_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$sensitive_fixture_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $sensitive_fixture_seek(S, n_stage, n) = S -- otherwise
dec $sensitive_fixture_after(pstate, pstate) : pstate
def $sensitive_fixture_after(S, S_next) = $gc_transition_owners(S, $destruction_transition_owners(S, $sensitive_trace_freeze($source_exception_transition(S, $throwable_transition(S, S_next)))))
dec $sensitive_fixture_replace(pcoccurrence*, pcpath, pcnode) : pcoccurrence*
def $sensitive_fixture_replace(eps, pcpath, pcnode) = eps
def $sensitive_fixture_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*, pcpath, pcnode) = (PCOCCURRENCE pcpath pcnode) :: pcoccurrence*
def $sensitive_fixture_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*, pcpath, pcnode) = (PCOCCURRENCE pcpath_other pcnode_old) :: $sensitive_fixture_replace(pcoccurrence*, pcpath, pcnode)
  -- if pcpath_other =/= pcpath
dec $sensitive_fixture_output(pevent*) : preqbytes
def $sensitive_fixture_output(eps) = eps
def $sensitive_fixture_output((OUTPUT preqbytes) :: pevent*) = preqbytes ++ $sensitive_fixture_output(pevent*)
"""
PARAM = 'NParam phpType14_param (INTEGER 0) phpType18_param (BOOLEAN b_ref) (BOOLEAN b_variadic) phpType10_param phpType5_default (SEQUENCE eps) metadata_param'
DERIVED = [
    'S.CURRENT = (pcallcontext)',
    '$function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction)',
    '$origin_source(pfunction.ORIGIN) = PORIGIN 0 pcpath_function',
    'S.SOURCES = [pcunit]',
    'pcunit = $pcsource(pcunit.ID, pcunit.AST)',
    '$origin_node(S.SOURCES,pfunction.ORIGIN) = (pcnode_function)',
    '$sensitive_source_parameters(pcnode_function) = ((n_field,phpType17*))',
    'phpType17* = [(PARAM)]',
    '$origin_child((pfunction.ORIGIN),[PCFIELD n_field,PCINDEX 0]) = (PORIGIN 0 pcpath_parameter)',
    '$origin_node(S.SOURCES,PORIGIN 0 pcpath_parameter) = (PARAM)',
    '$pslower(PARAM) = PSINPUTATTRIBUTES psraw phpType14_param',
    'ptcontext = {NAMESPACE pfunction.ENV.NAMESPACE, IMPORTS pfunction.ENV.CLASSES, SCOPE PTGLOBAL, POSITION PTPARAMETER, OWNER eps, MEMBER eps, FILE eps, LINE 0}',
    '$psattributes_supported(ptcontext,psraw,phpType14_param)',
    '$pssensitive_parameter_attribute(ptcontext,phpType14_param)',
    '$sensitive_trace_parameter(S,pfunction,0)',
    '~$sensitive_trace_parameter(S,pfunction,1)',
    '~$sensitive_trace_parameter(S,pfunction,999)',
    '~$sensitive_trace_parameter(S,pfunction[.ORIGIN = PORIGIN 999 eps],0)',
    '~$sensitive_trace_parameter(S,pfunction[.ENV.NAMESPACE = $ptascii("Forged")],0)',
    '~$sensitive_trace_parameter(S,pfunction[.ENV.CLASSES = [($ptascii("secret"),$ptascii("SensitiveParameter"))]],0)',
    'psparam = pfunction.SIGNATURE.PARAMETERS[0]',
    '~$sensitive_trace_parameter(S,pfunction[.SIGNATURE.PARAMETERS = [psparam[.NAME = $ptascii("other")]]],0)',
    '~$sensitive_trace_parameter(S,pfunction[.SIGNATURE.PARAMETERS = [psparam[.BYREF = ~psparam.BYREF]]],0)',
    '~$sensitive_trace_parameter(S,pfunction[.SIGNATURE.PARAMETERS = [psparam[.VARIADIC = ~psparam.VARIADIC]]],0)',
    '$psattributes_supported(ptcontext,psraw[.FLAGS = 1],phpType14_param)',
    '~$psattributes_supported(ptcontext,psraw[.EXTRA = true],phpType14_param)',
    '~$psattributes_supported(ptcontext,psraw,SEQUENCE eps)',
    'phpType14_param = SEQUENCE ([(NAttributeGroup (SEQUENCE ([(NAttribute name_attribute (SEQUENCE eps) metadata_attribute)])) metadata_group)])',
    '~$pssensitive_parameter_attribute(ptcontext,SEQUENCE ([(NAttributeGroup (SEQUENCE ([(NAttribute name_attribute (SEQUENCE eps) metadata_attribute),(NAttribute name_attribute (SEQUENCE eps) metadata_attribute)])) metadata_group)]))',
    '~$pssensitive_parameter_attribute(ptcontext,SEQUENCE ([(NAttributeGroup (SEQUENCE ([(NAttribute name_attribute (SEQUENCE ([(NArg ABSENT (NScalarInt (INTEGER 1) metadata_attribute) (BOOLEAN false) (BOOLEAN false) metadata_attribute)])) metadata_attribute)])) metadata_group)]))',
]
for replacement in [PARAM.replace('phpType14_param','(SEQUENCE eps)'),PARAM.replace('(INTEGER 0)','(INTEGER 1)'),PARAM.replace('phpType10_param','(NExprVariable (BYTES "b3RoZXI=") metadata_param)'),PARAM.replace('phpType18_param','(NIdentifier (BYTES "c3RyaW5n") metadata_param)')]:
    DERIVED.append('~$sensitive_trace_parameter(S[.SOURCES = [pcunit[.OCCURRENCES = $sensitive_fixture_replace(pcunit.OCCURRENCES,pcpath_parameter,'+replacement+')]]],pfunction,0)')

REACHED = [
    'S.TODO = (EVAL expression_new) :: ptask_tail*',
    'S.ORIGIN = (porigin_new)',
    '$origin_node(S.SOURCES,porigin_new) = (expression_new)',
    '$call_descriptors_valid(S) /\\ $declaration_history_valid(S) /\\ $property_state_valid(S)',
    '$lookup(S.ENV,psparam.NAME) = (n_parameter)',
    'S.STORE[n_parameter] = DEFINED (POBJECT n_leaf)',
    '$sensitive_trace_context(S,S.ENV,S.CURRENT) = [ptraceframe]',
    'ptraceframe.ARGS = [(KINT 0,SENSITIVE_TRACE (POBJECT n_leaf))]',
    '$trace_roots([ptraceframe]) = [HOBJECT n_leaf]',
    '$heap_valid($heap_prune($heap_graph(S)))',
    'PhpStep: S ~> S_new',
    'S_new.COMPLETION = NORMAL',
    'n_wrapper = |S.OBJECTS|',
    'n_error = $(n_wrapper + 1)',
    '$(|S_new.OBJECTS| = |S.OBJECTS| + 2)',
    'S_new.OBJECTS[n_wrapper] = SENSITIVEVALUE (POBJECT n_leaf)',
    'S_new.OBJECTS[n_error] = THROWABLE pthrowable',
    'pthrowable.KIND = "Error"',
    '(HOBJECT n_wrapper) <- S_new.ALLOCATIONS /\\ (HOBJECT n_error) <- S_new.ALLOCATIONS',
    '$sensitive_value_live(S_new,n_wrapper)',
    '$node_children(S_new,HOBJECT n_wrapper) = [HOBJECT n_leaf]',
    '$($heap_owners($heap_prune($heap_graph(S_new)),HOBJECT n_leaf) = $heap_owners($heap_prune($heap_graph(S)),HOBJECT n_leaf) + 1)',
    '$throwable_field(S_new,n_error,"trace") = PARRAY n_trace',
    '$trace_graph_valid(S_new,n_trace)',
    'S_new.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]',
    '$trace_array_field(S_new,n_frame,$ptascii("args")) = PARRAY n_args',
    'S_new.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_wrapper))]',
    'S_new.EVENTS = S.EVENTS /\\ S_new.ENV = S.ENV /\\ S_new.STORE = S.STORE',
    'S_new.SOURCES = S.SOURCES /\\ S_new.CURRENT = S.CURRENT /\\ S_new.FRAMES = S.FRAMES',
    'S_ready = $sensitive_fixture_after(S,S_new)',
    '$heap_valid($heap_prune($heap_graph(S_ready))) /\\ $property_state_valid(S_ready) /\\ $call_descriptors_valid(S_ready) /\\ $declaration_history_valid(S_ready)',
    'S_getter_found = $sensitive_fixture_seek(S_ready,1,1000)',
    'S_getter_found.COMPLETION = NORMAL \\/ S_getter_found.COMPLETION = BUDGET',
    'S_getter = S_getter_found[.COMPLETION = NORMAL]',
    'S_getter.TODO = (GETTER_INVOKE pgettercall) :: ptask_getter*',
    'pgettercall.METHOD = GET_SENSITIVE_VALUE /\\ pgettercall.RECEIVER = n_wrapper /\\ pgettercall.SENT = eps',
    '$call_task_valid(S_getter,GETTER_INVOKE pgettercall) /\\ $call_descriptors_valid(S_getter) /\\ $declaration_history_valid(S_getter) /\\ $property_state_valid(S_getter) /\\ $heap_valid($heap_prune($heap_graph(S_getter)))',
    '$lookup(S_getter.ENV,$ptascii("secret")) = eps',
    '$lookup(S_getter.ENV,$ptascii("weak")) = (n_weak_cell)',
    'S_getter.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
    '$node_children(S_getter,HOBJECT n_weak) = eps /\\ $weakref_get(S_getter,n_weak) = POBJECT n_leaf',
    '$heap_owners($heap_prune($heap_graph(S_getter)),HOBJECT n_leaf) = 1',
    '$node_children(S_getter,HOBJECT n_wrapper) = [HOBJECT n_leaf]',
    '~$sensitive_value_live(S_getter[.ALLOCATIONS = [HOBJECT n_wrapper]],n_wrapper)',
    '~$sensitive_value_live(S_getter[.ALLOCATIONS = eps],n_wrapper)',
    '~$call_task_valid(S_getter,GETTER_INVOKE pgettercall[.RECEIVER = n_leaf])',
    '~$call_task_valid(S_getter,GETTER_INVOKE pgettercall[.BASE = "Error"])',
    '~$call_task_valid(S_getter,GETTER_INVOKE pgettercall[.METHOD = GET_CODE])',
    '~$call_task_valid(S_getter,GETTER_INVOKE pgettercall[.SITE = PORIGIN 999 eps])',
    'PhpStep: S_getter ~> S_value_raw',
    'S_value_ready = $sensitive_fixture_after(S_getter,S_value_raw)',
    'S_value_found = $sensitive_fixture_seek(S_value_ready,3,1000)',
    'S_value_found.COMPLETION = NORMAL \\/ S_value_found.COMPLETION = BUDGET',
    'S_value = S_value_found[.COMPLETION = NORMAL]',
    'S_value.TODO = ptask_getter*',
    'S_value.COMPLETION = NORMAL /\\ S_value.RESULT = KNOWN (POBJECT n_leaf)',
    'S_value.OBJECTS = S_getter.OBJECTS /\\ S_value.ARRAYS = S_getter.ARRAYS /\\ S_value.ALLOCATIONS = S_getter.ALLOCATIONS',
    'S_value.EVENTS = S_getter.EVENTS /\\ S_value.ENV = S_getter.ENV /\\ S_value.STORE = S_getter.STORE /\\ $call_descriptors_valid(S_value) /\\ $declaration_history_valid(S_value) /\\ $property_state_valid(S_value) /\\ $heap_valid($heap_prune($heap_graph(S_value)))',
    '$heap_owners($heap_prune($heap_graph(S_value)),HOBJECT n_leaf) = 2',
    'S_release_found = $sensitive_fixture_seek(S_value,2,1000)',
    'S_release_found.COMPLETION = NORMAL \\/ S_release_found.COMPLETION = BUDGET',
    'S_release = S_release_found[.COMPLETION = NORMAL]',
    '$lookup(S_release.ENV,$ptascii("error")) = eps /\\ $lookup(S_release.ENV,$ptascii("trace")) = eps',
    '$lookup(S_release.ENV,$ptascii("wrapper")) = (n_wrapper_cell)',
    'S_release.STORE[n_wrapper_cell] = DEFINED (POBJECT n_wrapper)',
    '$heap_owners($heap_prune($heap_graph(S_release)),HOBJECT n_wrapper) = 1',
    '$heap_owners($heap_prune($heap_graph(S_release)),HOBJECT n_leaf) = 1',
    '$weakref_get(S_release,n_weak) = POBJECT n_leaf /\\ $call_descriptors_valid(S_release) /\\ $declaration_history_valid(S_release) /\\ $property_state_valid(S_release) /\\ $heap_valid($heap_prune($heap_graph(S_release)))',
    '$sensitive_fixture_output(S_release.EVENTS) = $ptascii("L|S|L|")',
    'PhpStep: S_release ~> S_unset',
    'S_unset.COMPLETION = NORMAL /\\ $lookup(S_unset.ENV,$ptascii("wrapper")) = eps',
    'S_unset_ready = $sensitive_fixture_after(S_release,S_unset)',
    'S_done = $drive(S_unset_ready,1000)',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    '$sensitive_fixture_output(S_done.EVENTS) = $ptascii("L|S|L|D|N|")',
    '$weakref_get(S_done,n_weak) = PNULL',
    '~((HOBJECT n_leaf) <- S_done.ALLOCATIONS) /\\ ~((HOBJECT n_wrapper) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_prune($heap_graph(S_done))) /\\ $declaration_history_valid(S_done) /\\ $call_descriptors_valid(S_done) /\\ $property_state_valid(S_done)',
]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--revision',required=True)
    parser.add_argument('--prepare-only',action='store_true')
    args=parser.parse_args()
    recorder.ROOT=ROOT
    sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    git=lambda *parts: subprocess.check_output(['git',*parts],cwd=ROOT,env=recorder.ENV).decode().strip()
    source=HERE/'sensitive-parameter-heap.php'
    catalogue=HERE/'sensitive_parameter_cases.json'
    data=json.loads(catalogue.read_bytes())
    original=next(row for row in data['cases'] if row['id']=='wrapper-heap-lifetime')
    profile_path=ROOT/'tests/semantics/profile.json'
    profile=json.loads(profile_path.read_bytes())
    php,adapter,runner,bridge,worker=(ROOT/name for name in ['.tools/php/bin/php','_build/default/adapter/main.exe','tests/semantics/_build/default/numeric_runner.exe','.tools/php-file.so','frontend/worker.php'])
    assert data['native_profile']==profile and original['source_sha256']==sha(source)
    assert original['status']=='normal' and original['exit_status']==0
    assert base64.b64decode(original['stdout_base64'])==b'L|S|L|D|N|' and not base64.b64decode(original['stderr_template_base64'])
    assert sha(php)=='b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    manifest=ROOT/'spec/semantics/modules.json'
    modules=[ROOT/name for name in json.loads(manifest.read_bytes())]
    watched=[Path(__file__),manifest,*modules,php,adapter,runner,bridge,worker,source,profile_path,catalogue,ROOT/'spec/schema.json',ROOT/'tests/semantics/error_handler_run.py',ROOT/'tests/semantics/recorded_worker.py']
    before={str(p):sha(p) for p in watched}
    revision,status=git('rev-parse','HEAD'),git('status','--short')
    assert revision==args.revision and not status,(revision,status)
    out=Path(tempfile.mkdtemp(prefix='sensitive-parameter-protocol-',dir=ROOT/'.tools'))
    print(out,flush=True)
    report={'revision':revision,'inputs':before,'profile':profile,'mode':'SL','cache':False,'det':True,'evaluated':False,'application_invocations':0,'application_evaluations':0,'source_agreements':0,'derived_premises':len(DERIVED),'reached_premises':len(REACHED),'budget_seconds':120,'environment':{'LC_ALL':'C','TZ':'UTC','jobs':1},'passed':False}
    flags=[arg for k,v in profile.items() for arg in ('-d',k+'='+v)]
    frontend=Worker([str(php),'-n',*flags,'-d','extension='+str(bridge),str(worker)],out/'frontend')
    adapter_worker=None
    try:
        adapter_worker=Worker([str(adapter),str(ROOT)],out/'adapter')
        parsed=frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'],parsed
        checked=adapter_worker.request({'op':'check','ast':parsed['ast'],'fixture':True})
        assert checked['ok'],checked
    finally:
        if adapter_worker: adapter_worker.close()
        frontend.close()
    try:
        content=PREFIX+'\ndec $main() : bool\ndef $main() = true\n'
        setup=['S_initial = $php_run('+checked['fixture']+',0,'+json.dumps(base64.b64encode(str(source).encode()).decode())+')',
               'S_initial.COMPLETION = NORMAL \\/ S_initial.COMPLETION = BUDGET',
               'S_found = $sensitive_fixture_seek(S_initial,0,1000)',
               'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
               'S = S_found[.COMPLETION = NORMAL]']
        for condition in setup+DERIVED+REACHED:
            condition=re.sub(r'\bPARAM\b',lambda match: PARAM,condition)
            content+='  -- '+('' if condition.startswith('PhpStep:') else 'if ')+condition+'\n'
        content+='def $main() = false -- otherwise\n'
        fixture=out/'heap.watsup'
        fixture.write_text(content)
        report.update(fixture=str(fixture),fixture_sha256=sha(fixture),prepared=True,passed=True)
        if not args.prepare_only:
            report['application_invocations']=1
            report['process']=process=recorder.recorded([str(runner),'--sl',*map(str,modules),str(fixture)],out/'heap',120)
            output=(out/'heap.stdout').read_bytes()
            report['evaluated']=process['exit']==0 and output in (b'true\n',b'false\n')
            report['application_evaluations']=int(report['evaluated'])
            report['passed']=process['exit']==0 and not process['timeout'] and not process['group_after'] and output==b'true\n' and not(out/'heap.stderr').read_bytes()
    finally:
        report.update(inputs_stable=before=={str(p):sha(p) for p in watched},head_stable=revision==git('rev-parse','HEAD'),status_stable=status==git('status','--short'))
        report['passed']=report['passed'] and all(report[k] for k in ['inputs_stable','head_stable','status_stable'])
        (out/('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({k:report[k] for k in ['passed','evaluated','application_evaluations','derived_premises','reached_premises','inputs_stable','head_stable','status_stable']}),flush=True)
    assert report['passed']

if __name__=='__main__': main()
