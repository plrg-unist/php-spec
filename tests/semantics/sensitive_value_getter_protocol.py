"""Prepare authentic first-class getter capture, invocation and final release controls."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker

PREFIX = r"""dec $sg_stage(pstate, nat) : bool
def $sg_stage(S, 0) = true
  -- if S.TODO = (METHOD_PREP phpType20 phpType7* false b_base z) :: ptask*
  -- if $ppfirstclass(phpType7*)
  -- if $method_source_name(phpType20, $ptascii("getValue"))
def $sg_stage(S, 1) = true
  -- if S.TODO = (GETTER_INVOKE pgettercall) :: ptask*
  -- if pgettercall.METHOD = GET_SENSITIVE_VALUE /\ pgettercall.CAPTURE =/= eps
def $sg_stage(S, 2) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES "Z2V0dGVy") metadata)) :: ptask*
def $sg_stage(S, 3) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES "Y29weQ==") metadata)) :: ptask*
def $sg_stage(S, 4) = true
  -- if S.TODO = (GETTER_CAPTURE_RESULT n porigin) :: ptask*
def $sg_stage(S, n) = false -- otherwise
dec $sg_seek(pstate, nat, nat) : pstate
def $sg_seek(S, n_stage, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $sg_stage(S, n_stage) \/ n = 0
def $sg_seek(S, n_stage, n) = $sg_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$sg_stage(S, n_stage) /\ $(n > 0)
def $sg_seek(S, n_stage, n) = $sg_seek($drive_steps(S, 1), n_stage, $nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $sg_seek(S, n_stage, n) = S -- otherwise
dec $sg_after(pstate, pstate) : pstate
def $sg_after(S, S_next) = $gc_transition_owners(S, $destruction_transition_owners(S, $sensitive_trace_freeze($source_exception_transition(S, $throwable_transition(S, S_next)))))
dec $sg_guard(pstate) : bool
def $sg_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $sg_output(pevent*) : ptbytes
def $sg_output(eps) = eps
def $sg_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $sg_output(pevent*)
"""
PRE = [
    r'S.TODO = (METHOD_PREP phpType20 phpType7* false b_base z) :: ptask_tail*',
    r'$ppfirstclass(phpType7*) /\ $method_source_name(phpType20,$ptascii("getValue"))',
    r'S.ORIGIN = (porigin_site)',
    r'$origin_node(S.SOURCES,porigin_site) = (NExprMethodCall expression phpType20 (SEQUENCE phpType7*) metadata)',
    r'$lookup(S.ENV,$ptascii("wrapper")) = (n_wrapper_cell)',
    r'S.STORE[n_wrapper_cell] = DEFINED (POBJECT n_wrapper)',
    r'S.OBJECTS[n_wrapper] = SENSITIVEVALUE (POBJECT n_leaf)',
    r'$lookup(S.ENV,$ptascii("weak")) = (n_weak_cell)',
    r'S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
    r'$weakref_get(S,n_weak) = POBJECT n_leaf',
    r'$sensitive_value_live(S,n_wrapper) /\ $sg_guard(S)',
    r'n_getter = |S.OBJECTS|',
    r'PhpStep: S ~> S_capture',
    r'S_capture.COMPLETION = NORMAL /\ S_capture.RESULT = KNOWN (POBJECT n_getter) /\ S_capture.TODO = ptask_tail*',
    r'S_capture.OBJECTS = S.OBJECTS ++ [GETTERCLOSURE n_wrapper GET_SENSITIVE_VALUE "SensitiveParameterValue" porigin_site]',
    r'S_capture.ALLOCATIONS = S.ALLOCATIONS ++ [HOBJECT n_getter]',
    r'S_capture.SOURCES = S.SOURCES /\ S_capture.EVENTS = S.EVENTS /\ S_capture.ENV = S.ENV /\ S_capture.STORE = S.STORE /\ S_capture.ARRAYS = S.ARRAYS',
    r'$node_children(S_capture,HOBJECT n_getter) = [HOBJECT n_wrapper]',
    r'$node_children(S_capture,HOBJECT n_wrapper) = [HOBJECT n_leaf] /\ $node_children(S_capture,HOBJECT n_weak) = eps',
    r'$getter_capture_live(S_capture,n_getter)',
    r'S_ready = $sg_after(S,S_capture)',
    r'$sg_guard(S_ready) /\ $closure_callable(S_ready,n_getter)',
]
DERIVED = [
    r'~$getter_capture_live(S_ready[.OBJECTS[n_getter] = GETTERCLOSURE n_wrapper GET_CODE "SensitiveParameterValue" porigin_site],n_getter)',
    r'~$getter_capture_live(S_ready[.OBJECTS[n_getter] = GETTERCLOSURE n_wrapper GET_SENSITIVE_VALUE "Error" porigin_site],n_getter)',
    r'~$getter_capture_live(S_ready[.OBJECTS[n_getter] = GETTERCLOSURE n_wrapper GET_SENSITIVE_VALUE "SensitiveParameterValue" (PORIGIN 999 eps)],n_getter)',
    r'$origin_child((porigin_site),[PCFIELD 0]) = (porigin_child)',
    r'~$getter_capture_live(S_ready[.OBJECTS[n_getter] = GETTERCLOSURE n_wrapper GET_SENSITIVE_VALUE "SensitiveParameterValue" porigin_child],n_getter)',
    r'~$getter_capture_live(S_ready[.OBJECTS[n_getter] = GETTERCLOSURE n_leaf GET_SENSITIVE_VALUE "SensitiveParameterValue" porigin_site],n_getter)',
    r'~$getter_capture_live(S_ready[.OBJECTS[n_getter] = GETTERCLOSURE n_getter GET_SENSITIVE_VALUE "SensitiveParameterValue" porigin_site],n_getter)',
    r'~$getter_capture_live(S_ready[.OBJECTS[n_getter] = GETTERCLOSURE 999 GET_SENSITIVE_VALUE "SensitiveParameterValue" porigin_site],n_getter)',
    r'~$getter_capture_live(S_ready[.ALLOCATIONS = eps],n_getter)',
    r'~$getter_capture_live(S_ready[.OBJECTS[n_wrapper] = SENSITIVEUNSET porigin_site],n_getter)',
    r'~$getter_capture_live(S_ready[.OBJECTS[n_wrapper] = SENSITIVEVALUE (POBJECT 999)],n_getter)',
    r'~$getter_capture_live(S_ready[.OBJECTS[n_getter] = SENSITIVEVALUE PNULL],n_getter)',
]
POST = [
    r'S_getter_found = $sg_seek(S_ready,1,1000)',
    r'S_getter_found.COMPLETION = NORMAL \/ S_getter_found.COMPLETION = BUDGET',
    r'S_getter = S_getter_found[.COMPLETION = NORMAL]',
    r'S_getter.TODO = (GETTER_INVOKE pgettercall) :: ptask_getter*',
    r'pgettercall.RECEIVER = n_wrapper /\ pgettercall.METHOD = GET_SENSITIVE_VALUE /\ pgettercall.BASE = "SensitiveParameterValue" /\ pgettercall.CAPTURE = (n_getter) /\ pgettercall.SENT = eps',
    r'$lookup(S_getter.ENV,$ptascii("leaf")) = eps /\ $lookup(S_getter.ENV,$ptascii("wrapper")) = eps',
    r'$weakref_get(S_getter,n_weak) = POBJECT n_leaf /\ $getter_capture_live(S_getter,n_getter)',
    r'$heap_owners($heap_prune($heap_graph(S_getter)),HOBJECT n_leaf) = 1',
    r'$call_task_valid(S_getter,GETTER_INVOKE pgettercall) /\ $sg_guard(S_getter)',
    r'~$getter_selected(S_getter,pgettercall[.CAPTURE = eps]) /\ ~$getter_selected(S_getter,pgettercall[.CAPTURE = (n_wrapper)])',
    r'~$getter_selected(S_getter,pgettercall[.METHOD = GET_CODE]) /\ ~$getter_selected(S_getter,pgettercall[.BASE = "Error"])',
    r'~$getter_selected(S_getter,pgettercall[.SITE = PORIGIN 999 eps]) /\ ~$call_task_valid(S_getter,GETTER_INVOKE pgettercall[.LINE = 999])',
    r'PhpStep: S_getter ~> S_value_raw',
    r'S_value_raw.COMPLETION = NORMAL /\ S_value_raw.RESULT = KNOWN (POBJECT n_leaf) /\ S_value_raw.TODO = ptask_getter*',
    r'S_value_raw.OBJECTS = S_getter.OBJECTS /\ S_value_raw.STORE = S_getter.STORE /\ S_value_raw.ARRAYS = S_getter.ARRAYS /\ S_value_raw.EVENTS = S_getter.EVENTS',
    r'S_value_ready = $sg_after(S_getter,S_value_raw)',
    r'S_value_found = $sg_seek(S_value_ready,4,1000)',
    r'S_value_found.COMPLETION = NORMAL \/ S_value_found.COMPLETION = BUDGET',
    r'S_value = S_value_found[.COMPLETION = NORMAL]',
    r'S_value.TODO = ptask_getter* /\ S_value.RESULT = KNOWN (POBJECT n_leaf)',
    r'$heap_owners($heap_prune($heap_graph(S_value)),HOBJECT n_leaf) = 2 /\ $sg_guard(S_value)',
    r'S_unset_found = $sg_seek(S_value,2,1000)',
    r'S_unset_found.COMPLETION = NORMAL \/ S_unset_found.COMPLETION = BUDGET',
    r'S_unset = S_unset_found[.COMPLETION = NORMAL]',
    r'$lookup(S_unset.ENV,$ptascii("copy")) = (n_copy_cell)',
    r'S_unset.STORE[n_copy_cell] = DEFINED (POBJECT n_leaf)',
    r'$heap_owners($heap_prune($heap_graph(S_unset)),HOBJECT n_leaf) = 2 /\ $sg_guard(S_unset)',
    r'PhpStep: S_unset ~> S_unset_raw',
    r'S_unset_ready = $sg_after(S_unset,S_unset_raw)',
    r'S_copy_found = $sg_seek(S_unset_ready,3,1000)',
    r'S_copy_found.COMPLETION = NORMAL \/ S_copy_found.COMPLETION = BUDGET',
    r'S_copy = S_copy_found[.COMPLETION = NORMAL]',
    r'$lookup(S_copy.ENV,$ptascii("getter")) = eps /\ ~((HOBJECT n_getter) <- S_copy.ALLOCATIONS) /\ ~((HOBJECT n_wrapper) <- S_copy.ALLOCATIONS)',
    r'S_copy.STORE[n_copy_cell] = DEFINED (POBJECT n_leaf)',
    r'$heap_owners($heap_prune($heap_graph(S_copy)),HOBJECT n_leaf) = 1 /\ $weakref_get(S_copy,n_weak) = POBJECT n_leaf /\ $sg_guard(S_copy)',
    r'$sg_output(S_copy.EVENTS) = $ptascii("L|L|")',
    r'PhpStep: S_copy ~> S_copy_raw',
    r'S_copy_ready = $sg_after(S_copy,S_copy_raw)',
    r'S_done = $drive(S_copy_ready,1000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps',
    r'$sg_output(S_done.EVENTS) = $ptascii("L|L|D|N|")',
    r'$weakref_get(S_done,n_weak) = PNULL /\ ~((HOBJECT n_leaf) <- S_done.ALLOCATIONS) /\ $sg_guard(S_done)',
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    git = lambda *parts: subprocess.check_output(['git',*parts],cwd=ROOT,env=recorder.ENV).decode().strip()
    catalogue = HERE/'sensitive_value_getter_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = ROOT/'tests/semantics/profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    case = next(row for row in data['cases'] if row['id']=='captured-receiver-value-lifetime')
    source = HERE/'sensitive-value-getter-heap.php'
    assert source.read_bytes() == case['source'].encode() and sha(source)==case['source_sha256']
    assert case['status']=='normal' and case['exit_status']==0
    assert base64.b64decode(case['stdout_base64'])==b'L|L|D|N|'
    assert not base64.b64decode(case['stderr_template_base64'])
    php,adapter,bridge,worker,runner,compiler = (ROOT/name for name in [
        '.tools/php/bin/php','_build/default/adapter/main.exe','.tools/php-file.so',
        'frontend/worker.php','tests/semantics/_build/default/numeric_runner.exe','.tools/spectec/bin/p4spectec'])
    assert sha(php)=='b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    manifest = ROOT/'spec/semantics/modules.json'
    modules = [ROOT/name for name in json.loads(manifest.read_bytes())]
    watched = [Path(__file__),catalogue,profile_file,manifest,*modules,php,adapter,bridge,worker,runner,compiler,
               source,ROOT/'spec/schema.json',ROOT/'tests/semantics/recorded_worker.py',Path(recorder.__file__)]
    revision,status = git('rev-parse','HEAD'),git('status','--short')
    assert revision==args.revision and not status
    before = {str(p):sha(p) for p in watched}
    out = Path(tempfile.mkdtemp(prefix='sensitive-getter-protocol-',dir=ROOT/'.tools'))
    print(out,flush=True)
    report = {'revision':revision,'inputs':before,'profile':profile,'records':[],'module_count':len(modules),
              'mode':'SL','cache':False,'det':True,'evaluated':False,'application_invocations':0,
              'application_evaluations':0,'source_agreements':0,'budget_seconds':120,'passed':False,
              'derived_premises':len(DERIVED)+3,'reached_premises':len(PRE)+len(POST)-3,
              'environment':{'LC_ALL':'C','TZ':'UTC','jobs':1}}
    fixture = None
    try:
        flags = [part for k,v in profile.items() for part in ('-d',k+'='+v)]
        frontend = Worker([str(php),'-n',*flags,'-d','extension='+str(bridge),str(worker)],out/'frontend')
        adapter_worker = None
        try:
            parsed = frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            adapter_worker = Worker([str(adapter),str(ROOT)],out/'adapter')
            checked = adapter_worker.request({'op':'check','ast':parsed['ast'],'fixture':True})
            assert checked['ok'] and checked['ast']==parsed['ast']
        finally:
            if adapter_worker: adapter_worker.close()
            frontend.close()
        setup = ['S_initial = $php_run('+checked['fixture']+',0,'+json.dumps(base64.b64encode(str(source).encode()).decode())+')',
                 r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                 'S_found = $sg_seek(S_initial,0,1000)',
                 r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                 'S = S_found[.COMPLETION = NORMAL]']
        content = PREFIX+'\ndec $sg_heap() : bool\ndef $sg_heap() = true\n'
        for condition in setup+PRE+DERIVED+POST:
            content += '  -- '+('' if condition.startswith('PhpStep:') else 'if ')+condition+'\n'
        content += 'def $sg_heap() = false -- otherwise\n\ndec $main() : bool\ndef $main() = $sg_heap()\n'
        fixture = out/'getter.watsup';fixture.write_text(content)
        report.update(fixture=str(fixture),fixture_sha256=sha(fixture),prepared=True,passed=True)
        if not args.prepare_only:
            process = recorder.recorded([str(compiler),'algo',*map(str,modules),str(fixture)],out/'compiler',120)
            output = (out/'compiler.stdout').read_bytes()
            main_present = b'\ndef $main : bool =\n' in output
            passed = process['exit']==0 and not process['timeout'] and not process['group_after'] and not(out/'compiler.stderr').read_bytes() and main_present
            report['records'].append({'id':'algorithmic-compilation','process':process,'passed':passed,'main_present':main_present,'application_evaluations':0})
            assert passed
            report['application_invocations'] = 1
            process = recorder.recorded([str(runner),'--sl',*map(str,modules),str(fixture)],out/'state',120)
            output = (out/'state.stdout').read_bytes()
            report['evaluated'] = process['exit']==0 and output in (b'true\n',b'false\n')
            report['application_evaluations'] = int(report['evaluated'])
            passed = process['exit']==0 and not process['timeout'] and not process['group_after'] and not(out/'state.stderr').read_bytes() and output==b'true\n'
            report['records'].append({'id':'strict-SL-application','process':process,'passed':passed})
            report['passed'] = passed
    finally:
        report.update(inputs_stable=before=={str(p):sha(p) for p in watched},
                      fixture_stable=fixture is None or report['fixture_sha256']==sha(fixture),
                      head_stable=revision==git('rev-parse','HEAD'),status_stable=status==git('status','--short'))
        report['passed'] = report['passed'] and all(report[k] for k in ('inputs_stable','fixture_stable','head_stable','status_stable'))
        (out/('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({k:report[k] for k in ('passed','evaluated','derived_premises','reached_premises','inputs_stable','head_stable','status_stable')}),flush=True)
    assert report['passed']

if __name__ == '__main__': main()
