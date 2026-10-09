"""Check genuine direct wrapper allocation, snapshot, getter and retirement controls."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker

PREFIX = r"""dec $direct_stage(pstate, nat) : bool
def $direct_stage(S, 0) = true
  -- if S.TODO = (EVAL (NExprNew phpType28 phpType6 metadata)) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if $new_source_name(S, porigin) = (ptbytes)
  -- if $ptlc(ptbytes) = $ptascii("sensitiveparametervalue")
def $direct_stage(S, 1) = true
  -- if S.TODO = (CTOR_SEND pctorcall) :: ptask*
  -- if pctorcall.BASE = "SensitiveParameterValue" /\ pctorcall.MODE = CTOR_NEW
def $direct_stage(S, 2) = true
  -- if S.TODO = (CTOR_INVOKE pctorcall) :: ptask*
  -- if pctorcall.BASE = "SensitiveParameterValue" /\ pctorcall.MODE = CTOR_NEW
def $direct_stage(S, 3) = true
  -- if S.TODO = (GETTER_INVOKE pgettercall) :: ptask*
  -- if pgettercall.METHOD = GET_SENSITIVE_VALUE
def $direct_stage(S, 4) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES "d3JhcHBlcg==") metadata)) :: ptask*
def $direct_stage(S, 5) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES "Y29weQ==") metadata)) :: ptask*
def $direct_stage(S, 6) = true
  -- if S.TODO = (CTOR_INVOKE pctorcall) :: ptask*
  -- if pctorcall.BASE = "SensitiveParameterValue" /\ pctorcall.MODE = CTOR_METHOD
def $direct_stage(S, 7) = true
  -- if S.TODO = METHOD_RESULT :: ptask*
def $direct_stage(S, n) = false -- otherwise
dec $direct_seek(pstate, nat, nat) : pstate
def $direct_seek(S, n_stage, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $direct_stage(S, n_stage) \/ n = 0
def $direct_seek(S, n_stage, n) = $direct_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$direct_stage(S, n_stage) /\ $(n > 0)
def $direct_seek(S, n_stage, n) = $direct_seek($drive_steps(S, 1), n_stage, $nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $direct_seek(S, n_stage, n) = S -- otherwise
dec $direct_after(pstate, pstate) : pstate
def $direct_after(S, S_next) = $gc_transition_owners(S, $destruction_transition_owners(S, $sensitive_trace_freeze($source_exception_transition(S, $throwable_transition(S, S_next)))))
dec $direct_guard(pstate) : bool
def $direct_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $direct_output(pevent*) : ptbytes
def $direct_output(eps) = eps
def $direct_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $direct_output(pevent*)
"""
HEAP_PRE = [
    'S.TODO = (EVAL expression_new) :: ptask_tail*',
    'S.ORIGIN = (porigin_new)',
    '$origin_node(S.SOURCES,porigin_new) = (expression_new)',
    '$lookup(S.ENV,$ptascii("leaf")) = (n_leaf_cell)',
    'S.STORE[n_leaf_cell] = DEFINED (POBJECT n_leaf)',
    '$lookup(S.ENV,$ptascii("weak")) = (n_weak_cell)',
    'S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
    '$weakref_get(S,n_weak) = POBJECT n_leaf',
    '$direct_guard(S)',
    'n_wrapper = |S.OBJECTS|',
    'PhpStep: S ~> S_alloc',
    'S_alloc.COMPLETION = NORMAL',
    'S_alloc.OBJECTS = S.OBJECTS ++ [SENSITIVEUNSET porigin_new]',
    'S_alloc.ALLOCATIONS = S.ALLOCATIONS ++ [HOBJECT n_wrapper]',
    'S_alloc.TODO = (CTOR_ARGS pctorcall_alloc) :: ptask_alloc*',
    'pctorcall_alloc.SITE = porigin_new /\\ pctorcall_alloc.RECEIVER = n_wrapper /\\ pctorcall_alloc.BASE = "SensitiveParameterValue" /\\ pctorcall_alloc.MODE = CTOR_NEW /\\ pctorcall_alloc.SENT = eps',
    '$node_children(S_alloc,HOBJECT n_wrapper) = eps /\\ $sensitive_value_live(S_alloc,n_wrapper)',
    'S_alloc.SOURCES = S.SOURCES /\\ S_alloc.EVENTS = S.EVENTS /\\ S_alloc.ENV = S.ENV /\\ S_alloc.STORE = S.STORE /\\ S_alloc.ARRAYS = S.ARRAYS',
    'S_ready = $direct_after(S,S_alloc)',
    '$direct_guard(S_ready)',
    'S_send_found = $direct_seek(S_ready,1,1000)',
    'S_send_found.COMPLETION = NORMAL \\/ S_send_found.COMPLETION = BUDGET',
    'S_send = S_send_found[.COMPLETION = NORMAL]',
    'S_send.TODO = (CTOR_SEND pctorcall_send) :: ptask_send*',
    'pctorcall_send.SITE = porigin_new /\\ pctorcall_send.RECEIVER = n_wrapper /\\ pctorcall_send.SENT = eps',
    '$call_task_valid(S_send,CTOR_SEND pctorcall_send) /\\ $direct_guard(S_send)',
    'PhpStep: S_send ~> S_sent',
    'S_sent.TODO = (CTOR_ARGS pctorcall_sent) :: ptask_send*',
    'pctorcall_sent.SENT = [(NAMED_SENT (KNOWN (POBJECT n_leaf)))] /\\ pctorcall_sent.INDEX = 1',
    'S_sent.OBJECTS[n_wrapper] = SENSITIVEUNSET porigin_new',
    'S_sent.STORE = S_send.STORE /\\ S_sent.EVENTS = S_send.EVENTS /\\ S_sent.ARRAYS = S_send.ARRAYS',
    '$ctor_nodes(pctorcall_sent) = [HOBJECT n_wrapper,HOBJECT n_leaf]',
    'S_sent_ready = $direct_after(S_send,S_sent)',
    'S_call_found = $direct_seek(S_sent_ready,2,1000)',
    'S_call_found.COMPLETION = NORMAL \\/ S_call_found.COMPLETION = BUDGET',
    'S_call = S_call_found[.COMPLETION = NORMAL]',
    'S_call.TODO = (CTOR_INVOKE pctorcall) :: ptask_call*',
    'pctorcall.SITE = porigin_new /\\ pctorcall.RECEIVER = n_wrapper /\\ pctorcall.SENT = [(NAMED_SENT (KNOWN (POBJECT n_leaf)))]',
    '$call_task_valid(S_call,CTOR_INVOKE pctorcall) /\\ $direct_guard(S_call)',
]
HEAP_DERIVED = [
    '~$ctor_selected(S_call,pctorcall[.SITE = PORIGIN 999 eps])',
    '~$ctor_selected(S_call,pctorcall[.BASE = "Error"])',
    '~$ctor_selected(S_call,pctorcall[.MODE = CTOR_METHOD])',
    '~$ctor_selected(S_call,pctorcall[.RECEIVER = n_leaf])',
    '~$ctor_selected(S_call,pctorcall[.RECEIVER = 999])',
    '~$ctor_selected(S_call[.ALLOCATIONS = eps],pctorcall)',
    '~$ctor_selected(S_call[.OBJECTS[n_wrapper] = SENSITIVEUNSET (PORIGIN 999 eps)],pctorcall)',
    '~$ctor_selected(S_call[.OBJECTS[n_wrapper] = SENSITIVEVALUE PNULL],pctorcall)',
    '~$call_task_valid(S_call,CTOR_INVOKE pctorcall[.INDEX = 999])',
    '~$call_task_valid(S_call,CTOR_INVOKE pctorcall[.LINE = 999])',
    '~$call_task_valid(S_call,CTOR_INVOKE pctorcall[.SENT = [(NAMED_SENT (VARIABLE $ptascii("leaf") 0))]])',
]
HEAP_POST = [
    'PhpStep: S_call ~> S_initialized',
    'S_initialized.COMPLETION = NORMAL /\\ S_initialized.RESULT = KNOWN (POBJECT n_wrapper) /\\ S_initialized.TODO = ptask_call*',
    'S_initialized.OBJECTS[n_wrapper] = SENSITIVEVALUE (POBJECT n_leaf)',
    'S_initialized.ALLOCATIONS = S_call.ALLOCATIONS /\\ S_initialized.ARRAYS = S_call.ARRAYS /\\ S_initialized.STORE = S_call.STORE /\\ S_initialized.EVENTS = S_call.EVENTS',
    '$node_children(S_initialized,HOBJECT n_wrapper) = [HOBJECT n_leaf]',
    '$heap_owners($heap_prune($heap_graph(S_initialized)),HOBJECT n_leaf) = $heap_owners($heap_prune($heap_graph(S_call)),HOBJECT n_leaf)',
    'S_initialized_ready = $direct_after(S_call,S_initialized)',
    '$direct_guard(S_initialized_ready)',
    'S_getter_found = $direct_seek(S_initialized_ready,3,1000)',
    'S_getter_found.COMPLETION = NORMAL \\/ S_getter_found.COMPLETION = BUDGET',
    'S_getter = S_getter_found[.COMPLETION = NORMAL]',
    'S_getter.TODO = (GETTER_INVOKE pgettercall) :: ptask_getter*',
    'pgettercall.RECEIVER = n_wrapper /\\ pgettercall.METHOD = GET_SENSITIVE_VALUE /\\ pgettercall.SENT = eps',
    '$lookup(S_getter.ENV,$ptascii("leaf")) = eps',
    '$weakref_get(S_getter,n_weak) = POBJECT n_leaf /\\ $node_children(S_getter,HOBJECT n_weak) = eps',
    '$heap_owners($heap_prune($heap_graph(S_getter)),HOBJECT n_leaf) = 1',
    '$call_task_valid(S_getter,GETTER_INVOKE pgettercall) /\\ $direct_guard(S_getter)',
    'PhpStep: S_getter ~> S_value_raw',
    'S_value_ready = $direct_after(S_getter,S_value_raw)',
    'S_value_found = $direct_seek(S_value_ready,7,1000)',
    'S_value_found.COMPLETION = NORMAL \\/ S_value_found.COMPLETION = BUDGET',
    'S_value = S_value_found[.COMPLETION = NORMAL]',
    'S_value.TODO = ptask_getter* /\\ S_value.RESULT = KNOWN (POBJECT n_leaf)',
    'S_value.OBJECTS = S_getter.OBJECTS /\\ S_value.ARRAYS = S_getter.ARRAYS /\\ S_value.ALLOCATIONS = S_getter.ALLOCATIONS',
    '$heap_owners($heap_prune($heap_graph(S_value)),HOBJECT n_leaf) = 2 /\\ $direct_guard(S_value)',
    'S_unset_found = $direct_seek(S_value,4,1000)',
    'S_unset_found.COMPLETION = NORMAL \\/ S_unset_found.COMPLETION = BUDGET',
    'S_unset = S_unset_found[.COMPLETION = NORMAL]',
    '$heap_owners($heap_prune($heap_graph(S_unset)),HOBJECT n_leaf) = 2 /\\ $direct_guard(S_unset)',
    'PhpStep: S_unset ~> S_unset_raw',
    'S_unset_ready = $direct_after(S_unset,S_unset_raw)',
    'S_copy_found = $direct_seek(S_unset_ready,5,1000)',
    'S_copy_found.COMPLETION = NORMAL \\/ S_copy_found.COMPLETION = BUDGET',
    'S_copy = S_copy_found[.COMPLETION = NORMAL]',
    '$lookup(S_copy.ENV,$ptascii("wrapper")) = eps /\\ ~((HOBJECT n_wrapper) <- S_copy.ALLOCATIONS)',
    '$heap_owners($heap_prune($heap_graph(S_copy)),HOBJECT n_leaf) = 1 /\\ $weakref_get(S_copy,n_weak) = POBJECT n_leaf /\\ $direct_guard(S_copy)',
    '$direct_output(S_copy.EVENTS) = $ptascii("L|L|")',
    'PhpStep: S_copy ~> S_copy_raw',
    'S_copy_ready = $direct_after(S_copy,S_copy_raw)',
    'S_done = $drive(S_copy_ready,1000)',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    '$direct_output(S_done.EVENTS) = $ptascii("L|L|D|N|")',
    '$weakref_get(S_done,n_weak) = PNULL /\\ ~((HOBJECT n_leaf) <- S_done.ALLOCATIONS) /\\ $direct_guard(S_done)',
]
REENTRY_PRE = [
    'S.TODO = (CTOR_INVOKE pctorcall) :: ptask_tail*',
    'pctorcall.BASE = "SensitiveParameterValue" /\\ pctorcall.MODE = CTOR_METHOD /\\ pctorcall.SENT = [(NAMED_SENT (KNOWN (PINT (+23))))]',
    'n_wrapper = pctorcall.RECEIVER',
    'S.OBJECTS[n_wrapper] = SENSITIVEVALUE (PINT (+7))',
    '$lookup(S.ENV,$ptascii("value")) = (n_value_cell)',
    '$lookup(S.ENV,$ptascii("alias")) = (n_value_cell)',
    'S.STORE[n_value_cell] = DEFINED (PINT (+17))',
    '$call_task_valid(S,CTOR_INVOKE pctorcall) /\\ $direct_guard(S)',
]
REENTRY_DERIVED = [
    '~$ctor_selected(S,pctorcall[.MODE = CTOR_NEW])',
    '~$ctor_selected(S,pctorcall[.SITE = PORIGIN 999 eps])',
    '~$ctor_selected(S,pctorcall[.BASE = "Exception"])',
    '~$ctor_selected(S[.ALLOCATIONS = eps],pctorcall)',
    'S_null = $sensitive_ctor_receive(S[.OBJECTS[n_wrapper] = SENSITIVEVALUE PNULL][.TODO = ptask_tail*],pctorcall)',
    'S_null.COMPLETION = THROWING n_null',
    'S_null.OBJECTS[n_wrapper] = SENSITIVEVALUE PNULL',
    'S_empty = $sensitive_ctor_receive(S[.OBJECTS[n_wrapper] = SENSITIVEUNSET pctorcall.SITE][.TODO = ptask_tail*],pctorcall)',
    'S_empty.COMPLETION = NORMAL /\\ S_empty.RESULT = KNOWN PNULL /\\ S_empty.OBJECTS[n_wrapper] = SENSITIVEVALUE (PINT (+23))',
]
REENTRY_POST = [
    'PhpStep: S ~> S_error',
    'S_error.COMPLETION = THROWING n_error',
    '$throwable_field(S_error,n_error,"message") = PSTRING $ptascii("Cannot modify readonly property SensitiveParameterValue::$value")',
    'S_error.OBJECTS[n_wrapper] = S.OBJECTS[n_wrapper]',
    '$node_children(S_error,HOBJECT n_wrapper) = eps',
    'S_error.STORE = S.STORE /\\ S_error.ENV = S.ENV /\\ S_error.SOURCES = S.SOURCES /\\ S_error.EVENTS = S.EVENTS',
    'S_error_ready = $direct_after(S,S_error)',
    'S_done = $drive(S_error_ready,1000)',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.FRAMES = eps',
    '$direct_output(S_done.EVENTS) = $ptascii("7|17|Cannot modify readonly property SensitiveParameterValue::$value|7")',
    '$direct_guard(S_done)',
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()
    catalogue = HERE/'sensitive_value_constructor_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = ROOT/'tests/semantics/profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    cases = {row['id']:row for row in data['cases']}
    sources = {'heap': HERE/'sensitive-value-heap.php', 'reentry': HERE/'sensitive-value-scalar.php'}
    names = {'heap':'wrapper-value-copy-lifetime', 'reentry':'scalar-reference-reentry'}
    for name,case in names.items():
        assert sources[name].read_bytes() == cases[case]['source'].encode()
        assert sha(sources[name]) == cases[case]['source_sha256']
        assert cases[case]['status'] == 'normal' and cases[case]['exit_status'] == 0
        assert not base64.b64decode(cases[case]['stderr_template_base64'])
    assert base64.b64decode(cases[names['heap']]['stdout_base64']) == b'L|L|D|N|'
    assert base64.b64decode(cases[names['reentry']]['stdout_base64']) == b'7|17|Cannot modify readonly property SensitiveParameterValue::$value|7'
    php,adapter,bridge,worker,runner,compiler = (ROOT/name for name in [
        '.tools/php/bin/php','_build/default/adapter/main.exe','.tools/php-file.so',
        'frontend/worker.php','tests/semantics/_build/default/numeric_runner.exe','.tools/spectec/bin/p4spectec'])
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    manifest = ROOT/'spec/semantics/modules.json'
    modules = [ROOT/name for name in json.loads(manifest.read_bytes())]
    watched = [Path(__file__),catalogue,profile_file,manifest,*modules,php,adapter,bridge,worker,runner,compiler,
               *sources.values(),ROOT/'spec/schema.json',ROOT/'tests/semantics/recorded_worker.py',ROOT/'tests/semantics/error_handler_run.py']
    revision,status = git('rev-parse','HEAD'),git('status','--short')
    assert revision == args.revision and not status
    before = {str(p):sha(p) for p in watched}
    out = Path(tempfile.mkdtemp(prefix='sensitive-value-protocol-',dir=ROOT/'.tools'))
    print(out,flush=True)
    report = {'revision':revision,'inputs':before,'profile':profile,'records':[],'module_count':len(modules),
              'mode':'SL','cache':False,'det':True,'evaluated':False,'application_invocations':0,
              'application_evaluations':0,'source_agreements':0,'budget_seconds':120,'passed':False,
              'derived_premises':len(HEAP_DERIVED)+len(REENTRY_DERIVED),
              'reached_premises':len(HEAP_PRE)+len(HEAP_POST)+len(REENTRY_PRE)+len(REENTRY_POST),
              'environment':{'LC_ALL':'C','TZ':'UTC','jobs':1}}
    try:
        flags = [part for k,v in profile.items() for part in ('-d',k+'='+v)]
        checked_sources = {}
        for name,source in sources.items():
            frontend = Worker([str(php),'-n',*flags,'-d','extension='+str(bridge),str(worker)],out/(name+'-frontend'))
            adapter_worker = None
            try:
                parsed = frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted']
                adapter_worker = Worker([str(adapter),str(ROOT)],out/(name+'-adapter'))
                checked = adapter_worker.request({'op':'check','ast':parsed['ast'],'fixture':True})
                assert checked['ok'] and checked['ast'] == parsed['ast']
                checked_sources[name] = checked
            finally:
                if adapter_worker: adapter_worker.close()
                frontend.close()
        content = PREFIX
        for name,source in sources.items():
            checked = checked_sources[name]
            setup = ['S_initial = $php_run('+checked['fixture']+',0,'+json.dumps(base64.b64encode(str(source).encode()).decode())+')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $direct_seek(S_initial,'+('0' if name=='heap' else '6')+',1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            conditions = HEAP_PRE+HEAP_DERIVED+HEAP_POST if name=='heap' else REENTRY_PRE+REENTRY_DERIVED+REENTRY_POST
            content += '\ndec $direct_'+name+'() : bool\ndef $direct_'+name+'() = true\n'
            for condition in setup+conditions:
                content += '  -- '+('' if condition.startswith('PhpStep:') else 'if ')+condition+'\n'
            content += 'def $direct_'+name+'() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = ($direct_heap() /\\ $direct_reentry())\n'
        fixture = out/'direct.watsup'
        fixture.write_text(content)
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
                      head_stable=revision==git('rev-parse','HEAD'),status_stable=status==git('status','--short'))
        report['passed'] = report['passed'] and all(report[k] for k in ('inputs_stable','head_stable','status_stable'))
        (out/('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({k:report[k] for k in ('passed','evaluated','derived_premises','reached_premises','inputs_stable','head_stable','status_stable')}),flush=True)
    assert report['passed']

if __name__ == '__main__': main()
