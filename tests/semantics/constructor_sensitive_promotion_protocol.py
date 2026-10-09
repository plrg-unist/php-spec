"""Authentic promoted property writes, sensitive snapshots and abrupt compilation."""
from pathlib import Path
import argparse, base64, hashlib, json, re, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker

PARAM = ('NParam phpType14_param (INTEGER flags_param) phpType18_param '
         '(BOOLEAN b_ref) (BOOLEAN b_variadic) phpType10_param '
         'phpType5_default (SEQUENCE eps) metadata_param')
CLASS = ('NStmtClass phpType14_class phpType24_class phpType3_class '
         'phpType44_class phpType42_class phpType23_class metadata_class')
METHOD = ('NStmtClassMethod phpType14_method (INTEGER flags_method) '
          '(BOOLEAN b_ref_method) (NIdentifier (BYTES text_method) metadata_name) '
          '(SEQUENCE phpType17*) phpType18_method (SEQUENCE statement*) metadata_method')
PREFIX = r'''dec $sprom_stage(pstate, nat) : bool
def $sprom_stage(S, 0) = true
  -- if S.TODO = (PROMOTE_PARAMETER porigin 0) :: ptask*
def $sprom_stage(S, 1) = true
  -- if S.TODO = (EVAL (NExprNew phpType28 phpType6 metadata)) :: ptask*
  -- if S.CURRENT = (pcallcontext)
  -- if $function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction)
  -- if $sensitive_trace_parameter(S, pfunction, 0)
def $sprom_stage(S, 2) = true
  -- if S.TODO = (GETTER_INVOKE pgettercall) :: ptask*
  -- if pgettercall.METHOD = GET_TRACE_STRING
def $sprom_stage(S, n) = false -- otherwise
dec $sprom_seek(pstate, nat, nat) : pstate
def $sprom_seek(S, n_stage, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $sprom_seek(S, n_stage, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $sprom_stage(S, n_stage) \/ n = 0
def $sprom_seek(S, n_stage, n) = $sprom_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$sprom_stage(S, n_stage) /\ $(n > 0)
dec $sprom_after(pstate, pstate) : pstate
def $sprom_after(S, S_next) = $gc_transition_owners(S, $destruction_transition_owners(S, $sensitive_trace_freeze($source_exception_transition(S, $throwable_transition(S, S_next)))))
dec $sprom_replace(pcoccurrence*, pcpath, pcnode) : pcoccurrence*
def $sprom_replace(eps, pcpath, pcnode) = eps
def $sprom_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*, pcpath, pcnode) = (PCOCCURRENCE pcpath pcnode) :: pcoccurrence*
def $sprom_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*, pcpath, pcnode) = (PCOCCURRENCE pcpath_other pcnode_old) :: $sprom_replace(pcoccurrence*, pcpath, pcnode)
  -- if pcpath_other =/= pcpath
dec $sprom_properties(ppropertydesc*, porigin, ppropertydesc?) : ppropertydesc*
def $sprom_properties(eps, porigin, ppropertydesc_replacement?) = eps
def $sprom_properties(ppropertydesc :: ppropertydesc_tail*, porigin, eps) = ppropertydesc_tail*
  -- if ppropertydesc.ORIGIN = porigin
def $sprom_properties(ppropertydesc :: ppropertydesc_tail*, porigin, (ppropertydesc_new)) = ppropertydesc_new :: ppropertydesc_tail*
  -- if ppropertydesc.ORIGIN = porigin
def $sprom_properties(ppropertydesc :: ppropertydesc_tail*, porigin, ppropertydesc_replacement?) = ppropertydesc :: $sprom_properties(ppropertydesc_tail*, porigin, ppropertydesc_replacement?)
  -- if ppropertydesc.ORIGIN =/= porigin
dec $sprom_output(pevent*) : preqbytes
def $sprom_output(eps) = eps
def $sprom_output((OUTPUT preqbytes) :: pevent*) = preqbytes ++ $sprom_output(pevent*)
'''

CERTIFICATE = [
    'S.TODO = (PROMOTE_PARAMETER porigin 0) :: ptask_tail*',
    'S.CURRENT = (pcallcontext)',
    '$receiving_function(S,porigin) = (pfunction)',
    '$class_method_origin(S.CLASSES,porigin) = (pmethoddesc)',
    '$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
    '$promotion_raw(S,pfunction,0) = (psraw)',
    '$promotion_descriptor(S,pfunction,0) = (ppropertydesc)',
    '$lookup(S.ENV,psraw.NAME) = (n_cell)',
    'pcallcontext.RECEIVER = (n_receiver)',
    '$origin_source(pfunction.ORIGIN) = PORIGIN 0 pcpath_method',
    'pcpath_param = pcpath_method ++ [PCFIELD 4,PCINDEX 0]',
    'porigin_param = PORIGIN 0 pcpath_param',
    '$origin_node(S.SOURCES,porigin_param) = (PARAM)',
    'ppropertydesc.ORIGIN = porigin_param',
    '$pslower(PARAM) = PSINPUTATTRIBUTES psraw phpType14_param',
    r'psraw.FLAGS = 1 /\ ~psraw.VARIADIC /\ psraw.BYREF = EXPECTED_BYREF',
    r'$promotion_task_valid(S,porigin,0) /\ $sensitive_trace_parameter(S,pfunction,0)',
    r'~$promotion_override_property(S,pclassdesc,ppropertydesc) /\ ~$pspromotion_override_attribute($promotion_attribute_context(pfunction),phpType14_param)',
    '$promotion_override_issue(S,pclassdesc,eps,pclassdesc.PROPERTIES) = eps',
]
NEGATIVES = [
    'S.SOURCES = [pcunit]',
    r'pcunit = $pcsource(pcunit.ID,pcunit.AST) /\ S.CLASSES = [pclassdesc]',
    '~$sensitive_trace_parameter(S,pfunction,999)',
    '~$sensitive_trace_parameter(S,pfunction[.ORIGIN = PORIGIN 999 eps],0)',
]
for replacement in ['eps', '(ppropertydesc[.KEY = $ptascii("other")])',
                    '(ppropertydesc[.TYPE = eps])',
                    '(ppropertydesc[.ORIGIN = PORIGIN 999 eps])',
                    '(ppropertydesc[.VISIBILITY = PROPERTY_PRIVATE])']:
    NEGATIVES.append('~$sensitive_trace_parameter(S[.CLASSES = [pclassdesc[.PROPERTIES = $sprom_properties(pclassdesc.PROPERTIES,porigin_param,'+replacement+')]]],pfunction,0)')
for replacement in [PARAM.replace('phpType14_param','(SEQUENCE eps)'),
                    PARAM.replace('(INTEGER flags_param)','(INTEGER 0)'),
                    PARAM.replace('phpType10_param','(NExprVariable (BYTES "b3RoZXI=") metadata_param)')]:
    NEGATIVES.append('~$sensitive_trace_parameter(S[.SOURCES = [pcunit[.OCCURRENCES = $sprom_replace(pcunit.OCCURRENCES,pcpath_param,'+replacement+')]]],pfunction,0)')

QUEUE = [
    'ptask_tail* = (PROMOTE_PARAMETER porigin 1) :: ptask_body*',
    '$call_task_valid(S,PROMOTE_PARAMETER porigin 1)',
    '~$promotion_task_valid(S,porigin,1)',
    '~$call_task_valid(S,PROMOTE_PARAMETER porigin 999)',
    '~$call_task_valid(S,PROMOTE_PARAMETER (PORIGIN 999 eps) 1)',
    '~$call_task_valid(S[.TODO = (PROMOTE_PARAMETER porigin 0) :: ptask_body*],PROMOTE_PARAMETER porigin 1)',
    'porigin_pending = PORIGIN 0 (pcpath_method ++ [PCFIELD 4,PCINDEX 1])',
    '~$call_task_valid(S[.CLASSES = [pclassdesc[.PROPERTIES = $sprom_properties(pclassdesc.PROPERTIES,porigin_pending,eps)]]],PROMOTE_PARAMETER porigin 1)',
]
PROMOTION = [
    'S.STORE[n_cell] = DEFINED (PINT (+7))',
    '$objectprops_at(S.OBJECTPROPS,n_receiver) = (ppropertyslot*)',
    '$property_slot_at(ppropertyslot*,ppropertydesc.KEY) = (ppropertyslot_before)',
    r'ppropertyslot_before.DECL = (ppropertydesc.ORIGIN) /\ ppropertyslot_before.STATE = PROP_INITIAL',
    r'$call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S)))',
    'PhpStep: S ~> S_promoted',
    r'S_promoted.COMPLETION = NORMAL /\ S_promoted.TODO = ptask_tail*',
    r'S_promoted.CURRENT = S.CURRENT /\ S_promoted.ORIGIN = S.ORIGIN',
    r'S_promoted.EVENTS = S.EVENTS /\ S_promoted.STORE = S.STORE /\ S_promoted.ENV = S.ENV /\ S_promoted.ALLOCATIONS = S.ALLOCATIONS',
    '$objectprops_at(S_promoted.OBJECTPROPS,n_receiver) = (ppropertyslot_after*)',
    '$property_slot_at(ppropertyslot_after*,ppropertydesc.KEY) = (ppropertyslot_promoted)',
]
VALUE_WRITE = [
    'ppropertyslot_promoted.STATE = PROP_VALUE (DIRECT (PINT (+7)))',
    r'S_promoted.PROPREFS = S.PROPREFS /\ $node_children(S_promoted,HOBJECT n_receiver) = eps',
]
REFERENCE_WRITE = [
    'ppropertyslot_promoted.STATE = PROP_VALUE (ALIAS n_cell)',
    '$propref_at(S_promoted.PROPREFS,n_cell) = (ppropref)',
    'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_receiver ppropertydesc.KEY ppropertydesc.ORIGIN]',
    r'$propref_source_valid(S_promoted,n_cell,OBJECT_PROP_SOURCE n_receiver ppropertydesc.KEY ppropertydesc.ORIGIN) /\ $node_children(S_promoted,HOBJECT n_receiver) = [HCELL n_cell]',
]
CAPTURE = [
    'S_ready = $sprom_after(S,S_promoted)',
    'S_capture_found = $sprom_seek(S_ready,1,1000)',
    r'S_capture_found.COMPLETION = NORMAL \/ S_capture_found.COMPLETION = BUDGET',
    'S_capture = S_capture_found[.COMPLETION = NORMAL]',
    'S_capture.TODO = (EVAL expression_new) :: ptask_capture*',
    'S_capture.STORE[n_cell] = DEFINED (PINT (+17))',
    '$sensitive_trace_context(S_capture,S_capture.ENV,S_capture.CURRENT) = [ptraceframe]',
    'ptraceframe.ARGS = TRACE_ARGS',
    r'$call_descriptors_valid(S_capture) /\ $declaration_history_valid(S_capture) /\ $property_state_valid(S_capture) /\ $heap_valid($heap_prune($heap_graph(S_capture)))',
    'PhpStep: S_capture ~> S_new',
    'S_new.COMPLETION = NORMAL',
    'n_wrapper = |S_capture.OBJECTS|',
    'n_error = $(n_wrapper + 1)',
    r'$(|S_new.OBJECTS| = |S_capture.OBJECTS| + 2) /\ S_new.OBJECTS[n_wrapper] = SENSITIVEVALUE (PINT (+17))',
    '$throwable_field(S_new,n_error,"trace") = PARRAY n_trace',
    'S_new.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]',
    '$trace_array_field(S_new,n_frame,$ptascii("args")) = PARRAY n_args',
    'S_new.ARRAYS[n_args].ITEMS = PHYSICAL_ARGS',
    r'$trace_graph_valid(S_new,n_trace) /\ $sensitive_value_live(S_new,n_wrapper) /\ $node_children(S_new,HOBJECT n_wrapper) = eps',
    r'S_new.EVENTS = S_capture.EVENTS /\ S_new.STORE = S_capture.STORE /\ S_new.ENV = S_capture.ENV /\ S_new.CURRENT = S_capture.CURRENT',
    'S_materialized = $sprom_after(S_capture,S_new)',
    r'$call_descriptors_valid(S_materialized) /\ $declaration_history_valid(S_materialized) /\ $property_state_valid(S_materialized) /\ $heap_valid($heap_prune($heap_graph(S_materialized)))',
    'S_live_found = $sprom_seek(S_materialized,2,1000)',
    r'S_live_found.COMPLETION = NORMAL \/ S_live_found.COMPLETION = BUDGET',
    'S_live = S_live_found[.COMPLETION = NORMAL]',
    'S_live.TODO = (GETTER_INVOKE pgettercall_trace) :: ptask_trace*',
    r'pgettercall_trace.METHOD = GET_TRACE_STRING /\ pgettercall_trace.RECEIVER = n_error /\ $call_task_valid(S_live,GETTER_INVOKE pgettercall_trace)',
    'S_live.OBJECTS[n_wrapper] = SENSITIVEVALUE (PINT (+17))',
    '$objectprops_at(S_live.OBJECTPROPS,n_receiver) = (ppropertyslot_done_all*)',
    '$property_slot_at(ppropertyslot_done_all*,ppropertydesc.KEY) = (ppropertyslot_done)',
    'FINAL_PROPERTY',
    r'$call_descriptors_valid(S_live) /\ $declaration_history_valid(S_live) /\ $property_state_valid(S_live) /\ $heap_valid($heap_prune($heap_graph(S_live)))',
    'S_done = $drive(S_live,1000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps',
    '$sprom_output(S_done.EVENTS) = NATIVE_STDOUT',
    r'$call_descriptors_valid(S_done) /\ $declaration_history_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_prune($heap_graph(S_done)))',
]
ABRUPT = [
    'P_compiled = $ppstart(0,PROGRAM,$base64(FILE))',
    'P_compiled.COMPLETION = PPCABRUPT (STATICBYTES $ptascii("Cannot declare variadic promoted property") 3)',
    'P = P_compiled[.COMPLETION = PPCNORMAL][.DIAGNOSTICS = eps][.CLASSCONTEXT = eps]',
    'pcpath_class = CLASS_PATH',
    'pcpath_method = METHOD_PATH',
    '$origin_node([P.FOLD.SOURCE],PORIGIN 0 pcpath_class) = ('+CLASS+')',
    '$pchcompile('+CLASS+',false,$ppclass_context(P)) = PCHOK pchheader eps',
    '$origin_node([P.FOLD.SOURCE],PORIGIN 0 pcpath_method) = ('+METHOD+')',
    'ptcontext = $ppmethod_context(P,pchheader,$ptascii("__construct"),3)',
    '$psstep_start((SEQUENCE phpType17*),phpType18_method,b_ref_method,ptcontext) = PSSDEFAULTREQUEST pscontinuation',
    'psraw = pscontinuation.PARAMETER',
    '$psstep_resume(pscontinuation,PSNONE) = PSSDONE (PSOK pssignature psdiagnostic*)',
    'PPROPERTIES P_error ppropertydesc* = $pppromotion_parameter(P,pcpath_method ++ [PCFIELD 4,PCINDEX 0],flags_method,psraw,eps,pchheader)',
    r'P_error.COMPLETION = P_compiled.COMPLETION /\ ppropertydesc* = eps',
    '$ppmethod_step(P,P_error,pcpath_method,flags_method,$ptascii("__construct"),(SEQUENCE statement*),metadata_method,ppropertydesc*,eps,pchheader,PSSDEFAULTREQUEST pscontinuation) = PPMEMBERS P_error ppropertydesc* eps',
    '$ppmethod_step(P,P_error,pcpath_method,flags_method,$ptascii("__construct"),(SEQUENCE statement*),metadata_method,ppropertydesc*,eps,pchheader,PSSDONE (PSOK pssignature psdiagnostic*)) = PPMEMBERS P_error ppropertydesc* eps',
]

def walk(node, path=()):
    if isinstance(node, dict) and 'node' in node:
        yield node, path
        for n, field in enumerate(node['fields']):
            yield from walk(field, path+(('PCFIELD',n),))
    elif isinstance(node, list):
        for n, field in enumerate(node):
            yield from walk(field, path+(('PCINDEX',n),))

def render_path(path):
    return '['+', '.join(kind+' '+str(n) for kind,n in path)+']'

def clauses(conditions, replacements):
    lines=[]
    for condition in conditions:
        for token,value in replacements.items():
            condition=re.sub(r'\b'+token+r'\b',lambda match: value,condition)
        lines.append('  -- '+('' if condition.startswith('PhpStep:') else 'if ')+condition+'\n')
    return ''.join(lines)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--revision',required=True)
    parser.add_argument('--prepare-only',action='store_true')
    args=parser.parse_args()
    recorder.ROOT=ROOT
    sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    git=lambda *parts: subprocess.check_output(['git',*parts],cwd=ROOT,env=recorder.ENV).decode().strip()
    profile_path=ROOT/'tests/semantics/profile.json'
    profile=json.loads(profile_path.read_bytes())
    php,adapter,runner,bridge,worker=(ROOT/name for name in ['.tools/php/bin/php','_build/default/adapter/main.exe','tests/semantics/_build/default/numeric_runner.exe','.tools/php-file.so','frontend/worker.php'])
    manifest=ROOT/'spec/semantics/modules.json'
    modules=[ROOT/name for name in json.loads(manifest.read_bytes())]
    sources={'value':HERE/'sensitive-promotion-value.php','reference':HERE/'sensitive-promotion-reference.php','abrupt':HERE/'sensitive-promotion-variadic.php'}
    catalogue=HERE/'constructor_sensitive_promotion_cases.json'
    data=json.loads(catalogue.read_bytes())
    assert data['native_profile']==profile
    stdout_values={}
    for name,source in sources.items():
        row=next(row for row in data['cases'] if row['id']=={'value':'value-property-vs-cv','reference':'reference-property-snapshot','abrupt':'variadic-promotion-error'}[name])
        assert row['source_sha256']==sha(source)
        assert row['status']==('static_rejection' if name=='abrupt' else 'normal')
        assert row['exit_status']==(255 if name=='abrupt' else 0)
        stdout_values[name]=base64.b64decode(row.get('stdout_template_base64',row['stdout_base64'])).replace(b'{FILE}',str(source).encode())
        if name!='abrupt': assert not base64.b64decode(row['stderr_template_base64'])
    assert sha(php)=='b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    watched=[Path(__file__),manifest,*modules,php,adapter,runner,bridge,worker,profile_path,ROOT/'spec/schema.json',ROOT/'tests/semantics/error_handler_run.py',ROOT/'tests/semantics/recorded_worker.py',*sources.values(),catalogue]
    before={str(p):sha(p) for p in watched}
    revision,status=git('rev-parse','HEAD'),git('status','--short')
    assert revision==args.revision and not status,(revision,status)
    out=Path(tempfile.mkdtemp(prefix='sensitive-promotion-protocol-',dir=ROOT/'.tools'))
    print(out,flush=True)
    report={'revision':revision,'inputs':before,'profile':profile,'mode':'SL','cache':False,'det':True,'source_agreements':0,'application_invocations':0,'application_evaluations':0,'evaluated':False,'module_count':len(modules),'budget_seconds':120,'environment':{'LC_ALL':'C','TZ':'UTC','jobs':1},'passed':False,'records':[]}
    flags=[arg for k,v in profile.items() for arg in ('-d',k+'='+v)]
    try:
        checked_sources={}
        for name,source in sources.items():
            frontend=Worker([str(php),'-n',*flags,'-d','extension='+str(bridge),str(worker)],out/(name+'-frontend'))
            adapter_worker=None
            try:
                adapter_worker=Worker([str(adapter),str(ROOT)],out/(name+'-adapter'))
                parsed=frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted'],parsed
                checked=adapter_worker.request({'op':'check','ast':parsed['ast'],'fixture':True})
                assert checked['ok'],checked
                checked_sources[name]=(parsed,checked)
            finally:
                if adapter_worker: adapter_worker.close()
                frontend.close()
        content=PREFIX
        for name in ['value','reference']:
            parsed,checked=checked_sources[name]
            setup=['S_initial = $php_run('+checked['fixture']+',0,'+json.dumps(base64.b64encode(str(sources[name]).encode()).decode())+')',
                   r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                   'S_found = $sprom_seek(S_initial,0,1000)',
                   r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                   'S = S_found[.COMPLETION = NORMAL]']
            derived=CERTIFICATE+(NEGATIVES+QUEUE if name=='value' else [])
            reached=PROMOTION+(VALUE_WRITE if name=='value' else REFERENCE_WRITE)+CAPTURE
            if name=='value': reached.insert(reached.index('$objectprops_at(S_promoted.OBJECTPROPS,n_receiver) = (ppropertyslot_after*)'),'~$call_task_valid(S_promoted,PROMOTE_PARAMETER porigin 0)')
            if name=='reference': reached.insert(reached.index('FINAL_PROPERTY')+1,'S_live.STORE[n_cell] = DEFINED (PINT (+23))')
            replacements={'PARAM':PARAM,'EXPECTED_BYREF':'true' if name=='reference' else 'false',
                'TRACE_ARGS':'[(KINT 0,SENSITIVE_TRACE (PINT (+17)))'+(', (KINT 1,PINT (+9))' if name=='value' else '')+']',
                'PHYSICAL_ARGS':'[ENTRY (KINT 0) (DIRECT (POBJECT n_wrapper))'+(', ENTRY (KINT 1) (DIRECT (PINT (+9)))' if name=='value' else '')+']',
                'FINAL_PROPERTY':'ppropertyslot_done.STATE = PROP_VALUE '+('(ALIAS n_cell)' if name=='reference' else '(DIRECT (PINT (+7)))'),
                'NATIVE_STDOUT':'$base64('+json.dumps(base64.b64encode(stdout_values[name]).decode())+')'}
            content+='\ndec $sprom_'+name+'() : bool\ndef $sprom_'+name+'() = true\n'+clauses(setup+derived+reached,replacements)+'def $sprom_'+name+'() = false -- otherwise\n'
            report['records'].append({'id':name,'derived_premises':len(derived),'reached_premises':len(reached),'setup_premises':len(setup),'evaluated':False})
        parsed,checked=checked_sources['abrupt']
        class_path=next(path for node,path in walk(parsed['ast']['program']) if node['node']=='Stmt_Class')
        method_path=next(path for node,path in walk(parsed['ast']['program']) if node['node']=='Stmt_ClassMethod')
        content+='\ndec $sprom_abrupt() : bool\ndef $sprom_abrupt() = true\n'+clauses(ABRUPT,{'PROGRAM':checked['fixture'],'FILE':json.dumps(base64.b64encode(str(sources['abrupt']).encode()).decode()),'CLASS_PATH':render_path(class_path),'METHOD_PATH':render_path(method_path)})+'def $sprom_abrupt() = false -- otherwise\n'
        report['records'].append({'id':'abrupt','derived_premises':len(ABRUPT),'reached_premises':0,'setup_premises':0,'evaluated':False})
        content+='\ndec $main() : bool\ndef $main() = $sprom_value() /\\ $sprom_reference() /\\ $sprom_abrupt()\n'
        fixture=out/'promotion.watsup'
        fixture.write_text(content)
        report.update(fixture=str(fixture),fixture_sha256=sha(fixture),prepared=True,passed=True)
        report['derived_premises']=sum(row['derived_premises'] for row in report['records'])
        report['reached_premises']=sum(row['reached_premises'] for row in report['records'])
        if not args.prepare_only:
            report['application_invocations']=1
            report['process']=process=recorder.recorded([str(runner),'--sl',*map(str,modules),str(fixture)],out/'state',120)
            output=(out/'state.stdout').read_bytes()
            report['evaluated']=process['exit']==0 and output in (b'true\n',b'false\n')
            report['application_evaluations']=int(report['evaluated'])
            for row in report['records']: row['evaluated']=report['evaluated']
            report['passed']=process['exit']==0 and not process['timeout'] and not process['group_after'] and output==b'true\n' and not(out/'state.stderr').read_bytes()
    finally:
        report.update(inputs_stable=before=={str(p):sha(p) for p in watched},head_stable=revision==git('rev-parse','HEAD'),status_stable=status==git('status','--short'))
        report['passed']=report['passed'] and all(report[k] for k in ['inputs_stable','head_stable','status_stable'])
        (out/('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({k:report.get(k) for k in ['passed','evaluated','application_evaluations','derived_premises','reached_premises','inputs_stable','head_stable','status_stable']}),flush=True)
    assert report['passed']

if __name__=='__main__': main()
