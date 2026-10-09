"""Reach the eval compiler pause and authenticate ordinary parameter targets."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker

PARAM = ('NParam phpType14_param (INTEGER flags_param) phpType18_param '
         '(BOOLEAN b_ref_param) (BOOLEAN b_variadic_param) phpType10_param '
         'phpType5_default phpType37_hooks metadata_param')
FIRST = PARAM.replace('_param', '_first').replace('_default', '_first_default').replace('_hooks', '_first_hooks')
METHOD = ('NStmtClassMethod phpType14_method (INTEGER flags_method) (BOOLEAN b_ref_method) '
          '(NIdentifier (BYTES text_method) metadata_method_name) '
          '(SEQUENCE ([(' + FIRST + '), (' + PARAM + ')])) phpType18_method '
          '(SEQUENCE statement*) metadata_method')
CLASS = ('NStmtClass phpType14_class phpType24_class phpType3_class '
         'phpType44_class phpType42_class phpType23_class metadata_class')
ATTR = '(NAttribute name_attribute (SEQUENCE eps) metadata_attribute)'
GROUP = '(NAttributeGroup (SEQUENCE ([' + ATTR + '])) metadata_group)'
ATTRS = '(SEQUENCE ([' + GROUP + ']))'
USER = '(NName (BYTES "T3RoZXI=") metadata_attribute)'
ARG = '(NArg ABSENT (NScalarInt (INTEGER 1) metadata_param) (BOOLEAN false) (BOOLEAN false) metadata_param)'
HOOK = '(NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) (NIdentifier (BYTES "Z2V0") metadata_param) (SEQUENCE eps) (NScalarInt (INTEGER 1) metadata_param) metadata_param)'

PREFIX = r'''dec $ptarget_stage(pstate) : bool
def $ptarget_stage(S) = true -- if S.TODO = (EVAL_COMPILE_RESUME pevalcompile) :: ptask_tail*
def $ptarget_stage(S) = false -- otherwise
dec $ptarget_await(pstate,nat) : pstate
def $ptarget_await(S,n) = S -- if S.COMPLETION = SOURCE_PENDING
def $ptarget_await(S,n) = $ptarget_await($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if $(n > 0)
def $ptarget_await(S,n) = S -- otherwise
dec $ptarget_seek(pstate,nat) : pstate
def $ptarget_seek(S,n) = S -- if $ptarget_stage(S)
def $ptarget_seek(S,n) = $ptarget_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if ~$ptarget_stage(S) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if $(n > 0)
def $ptarget_seek(S,n) = S -- otherwise
dec $ptarget_replace(pcoccurrence*,pcpath,pcnode) : pcoccurrence*
def $ptarget_replace(eps,pcpath,pcnode) = eps
def $ptarget_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath pcnode) :: pcoccurrence*
def $ptarget_replace((PCOCCURRENCE pcpath_old pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath_old pcnode_old) :: $ptarget_replace(pcoccurrence*,pcpath,pcnode)
  -- if pcpath_old =/= pcpath
'''

DERIVED = [
    'S.SOURCES = pcunit_main :: pcunit :: eps',
    'pcunit.ID = 1 /\\ pcunit = $pcsource(1,pcunit.AST)',
    'P_compiled = $eval_source_ppstate(S,pcunit)',
    'P_compiled.COMPLETION = pevalcompile.PLAN.COMPLETION',
    'P_compiled.PUBLICATIONS = eps /\\ P_compiled.CLASSES = eps /\\ P_compiled.FUNCTIONS = eps',
    'P_reset = P_compiled[.COMPLETION = PPCNORMAL][.DIAGNOSTICS = eps][.CLASSCONTEXT = eps]',
    'pcpath_class = CLASS_PATH',
    'pcpath_method = METHOD_PATH',
    'pcpath_parameter = pcpath_method ++ [PCFIELD 4, PCINDEX 1]',
    '$origin_node(S.SOURCES,PORIGIN 1 pcpath_class) = (' + CLASS + ')',
    '$pchcompile(' + CLASS + ',false,$ppclass_context(P_reset)) = PCHOK pchheader eps',
    '$origin_node(S.SOURCES,PORIGIN 1 pcpath_method) = (' + METHOD + ')',
    '$origin_node(S.SOURCES,PORIGIN 1 pcpath_parameter) = (' + PARAM + ')',
    'text_method = "X19jb25zdHJ1Y3Q=" /\\ ~b_ref_method',
    'ptcontext = $ppmethod_context(P_reset,pchheader,$ptascii("__construct"),1)',
    '$psstep_start((SEQUENCE ([(' + FIRST + '), (' + PARAM + ')])),phpType18_method,false,ptcontext) = PSSDEFAULTREQUEST pscontinuation_first',
    'phpType5_first_default = (NScalarInt (INTEGER 1) metadata_default)',
    '$psstep_resume(pscontinuation_first,PSDEFAULT phpType5_first_default "int") = PSSATTRIBUTETARGETREQUEST pscontinuation phpType14_param',
    'pscontinuation.SIGNATURE.PARAMETERS = [psparam_first]',
    'psraw = pscontinuation.PARAMETER',
    'psraw.DEFAULT = ABSENT /\\ psraw.LINE = 1 /\\ psraw.FLAGS = 0 /\\ ~psraw.EXTRA /\\ ~psraw.BYREF /\\ ~psraw.VARIADIC',
    '$pslower(' + PARAM + ') = PSINPUTATTRIBUTES psraw phpType14_param',
    '$origin_node(S.SOURCES,PORIGIN 1 (pcpath_parameter ++ [PCFIELD 2])) = (NIdentifier (BYTES text_type) metadata_type)',
    'phpType14_param = ' + ATTRS,
    '$psattribute_target(ptcontext,psraw,phpType14_param) = ($ptascii("Override"))',
    '~$psattributes_supported(ptcontext,psraw,phpType14_param)',
    'pscontinuation.DIAGNOSTICS = [psdiagnostic_notice]',
    '$psmessage(psdiagnostic_notice) = NOTICE_MESSAGE',
    'P = P_reset[.GOTOROOT = pcpath_method][.CLASSCONTEXT = (ptcontext)]',
    '$ppsignature_attribute_valid(P,pcpath_parameter,pscontinuation,phpType14_param)',
    '$ppsignature_attribute($ppsignature_diagnostics(P,pscontinuation.DIAGNOSTICS),pcpath_parameter,pscontinuation,phpType14_param).COMPLETION = PPCABRUPT (FATAL TARGET_MESSAGE 1)',
    '$psattribute_result(pscontinuation,phpType14_param,PSNONE) = PSERROR (pscontinuation.DIAGNOSTICS ++ [$psissue(ptcontext[.LINE = 1][.POSITION = PTPARAMETER],"error","attribute-target",[$ptascii("Override")])])',
    '~$ppsignature_attribute_valid(P,pcpath_method ++ [PCFIELD 4,PCINDEX 0],pscontinuation,phpType14_param)',
    '~$ppsignature_attribute_valid(P,pcpath_method ++ [PCFIELD 4,PCINDEX 2],pscontinuation,phpType14_param)',
    '~$ppsignature_attribute_valid(P[.GOTOROOT = pcpath_class],pcpath_parameter,pscontinuation,phpType14_param)',
    '~$ppsignature_attribute_valid(P[.ENV.NAMESPACE = $ptascii("Other")],pcpath_parameter,pscontinuation,phpType14_param)',
    '~$ppsignature_attribute_valid(P[.ENV.CLASSES = [($ptascii("alias"),$ptascii("Other"))]],pcpath_parameter,pscontinuation,phpType14_param)',
    '~$ppsignature_attribute_valid(P[.LOCATION.FILE = $ptascii("other.php")],pcpath_parameter,pscontinuation,phpType14_param)',
    '~$ppsignature_attribute_valid(P,pcpath_parameter,pscontinuation[.SIGNATURE.PARAMETERS = eps],phpType14_param)',
]
for field, value in [('NAME','$ptascii("other")'),('TYPE','ABSENT'),('BYREF','true'),
                     ('VARIADIC','true'),('DEFAULT','(NScalarInt (INTEGER 1) metadata_param)'),
                     ('LINE','2'),('FLAGS','1'),('EXTRA','true')]:
    DERIVED.append('~$ppsignature_attribute_valid(P,pcpath_parameter,pscontinuation[.PARAMETER = psraw[.' + field + ' = ' + value + ']],phpType14_param)')
for attrs in [ATTRS.replace('name_attribute',USER),
              '(SEQUENCE ([' + GROUP + ', ' + GROUP + ']))',
              ATTRS.replace(ATTR,ATTR + ', ' + ATTR.replace('name_attribute',USER)),
              ATTRS.replace('(SEQUENCE eps)','(SEQUENCE ([' + ARG + ']))',1)]:
    DERIVED += ['$psattribute_target(ptcontext,psraw,' + attrs + ') = eps',
                '~$ppsignature_attribute_valid(P,pcpath_parameter,pscontinuation,' + attrs + ')']
DERIVED += [
    '$psattribute_target(ptcontext,psraw[.FLAGS = 1],phpType14_param) = eps',
    '$psattribute_target(ptcontext,psraw[.EXTRA = true],phpType14_param) = eps',
    '$pslower(' + PARAM.replace('phpType37_hooks','(SEQUENCE ([' + HOOK + ']))') + ') = PSINPUT (psraw[.EXTRA = true])',
    'pcunit_forged = pcunit[.OCCURRENCES = $ptarget_replace(pcunit.OCCURRENCES,pcpath_parameter,' + PARAM.replace('phpType14_param',ATTRS.replace('name_attribute',USER)) + ')]',
    '~$ppsignature_attribute_valid(P[.FOLD.SOURCE = pcunit_forged],pcpath_parameter,pscontinuation,phpType14_param)',
    'pcunit_parent_forged = pcunit[.OCCURRENCES = $ptarget_replace(pcunit.OCCURRENCES,pcpath_method,' + METHOD.replace('phpType14_param',ATTRS.replace('name_attribute',USER)) + ')]',
    '~$ppsignature_attribute_valid(P[.FOLD.SOURCE = pcunit_parent_forged],pcpath_parameter,pscontinuation,phpType14_param)',
    '$psattribute_parameter_line(ABSENT,6) = 6 /\\ $psline(metadata_type) = 1',
    '$psattribute_parameter_line((NNullableType (NIdentifier (BYTES text_type) metadata_type) ([(MstartLine 9)])),6) = 1',
    '$psattribute_parameter_line((NUnionType (SEQUENCE ([(NIdentifier (BYTES text_type) metadata_type),(NIdentifier (BYTES "c3RyaW5n") ([(MstartLine 9)]))])) ([(MstartLine 9)])),6) = 1',
    '$psattribute_parameter_line((NIntersectionType (SEQUENCE ([(NIdentifier (BYTES text_type) metadata_type),(NIdentifier (BYTES "b3RoZXI=") ([(MstartLine 9)]))])) ([(MstartLine 9)])),6) = 1',
    '$psdefaultready(ptcontext,psraw,eps,PSDEFAULT (NExprConstFetch name_attribute eps) "deferred") = PSONEUNSUPPORTED "missing deferred default compiler line"',
    '$psattribute_result(pscontinuation,phpType14_param,PSDEFAULT (NExprConstFetch name_attribute eps) "deferred") = PSUNSUPPORTED "missing deferred default compiler line"',
]

RUNTIME = [
    '$call_descriptors_valid(S) /\\ $declaration_history_valid(S)',
    '$eval_compile_owners_valid(S) /\\ $eval_compile_cursor_valid(S,pevalcompile)',
    'pevalcontext = S.EVALCONTEXTS[0]',
    'S.EVALCONTEXTS = [pevalcontext] /\\ pevalcontext.UNIT = 1 /\\ pevalcontext.PHASE = EVAL_COMPILE /\\ ptask_tail* = (EVAL_COMPILE_END 1) :: pevalcontext.TAIL',
    'pevalcompile.PLAN.UNIT = 1 /\\ pevalcompile.PLAN.PUBLICATIONS = eps',
    'pevalcompile.CHECKPOINT = 0 /\\ pevalcompile.DIAGNOSTIC = 1 /\\ pevalcompile.PENDING = NORMAL',
    'pevalcompile.PLAN.DIAGNOSTICS = [pldiagnostic]',
    'pldiagnostic = PLDIAGNOSTIC "deprecated" "function-message" ([NOTICE_MESSAGE]) pllocation',
    'pllocation.UNIT = 1 /\\ pllocation.LINE = 1',
    'pevalcompile.PLAN.COMPLETION = PPCABRUPT (FATAL TARGET_MESSAGE 1)',
    'S.EVENTS = [OUTPUT $ptascii("BEFORE|"), $compiler_event("Deprecated",NOTICE_MESSAGE,pllocation)]',
    '$class_named(S.CLASSNAMES,$ptascii("parameteroverrideeval21")) = eps',
    '$task_nodes(EVAL_COMPILE_RESUME pevalcompile) = eps',
    '$declaration_unit_complete(S.DECLARATIONS,1) = false',
    '$eval_compile_waiting(S.DECLARATIONS) = [(1,0,1,n_ordinal,[(COMPILER_NOTICE pldiagnostic)])]',
    'S.DECLARATIONS[n_ordinal] = PDEVALPAUSE 1 0 1 ([(COMPILER_NOTICE pldiagnostic)])',
    '~$eval_compile_cursor_valid(S,pevalcompile[.CHECKPOINT = 1])',
    '~$eval_compile_cursor_valid(S,pevalcompile[.DIAGNOSTIC = 0])',
    '~$eval_compile_cursor_valid(S,pevalcompile[.PLAN.UNIT = 0])',
    '~$eval_compile_owners_valid(S[.TODO = (EVAL_COMPILE_RESUME pevalcompile) :: S.TODO])',
    '$declaration_images(S,S.SOURCES) = DECLIMAGES (n_image,P_image)*',
    '$eval_compile_plan_list_valid([pevalcompile],(n_image,P_image)*)',
    '~$eval_compile_plan_list_valid([(pevalcompile[.PLAN.COMPLETION = PPCNORMAL])],(n_image,P_image)*)',
    '~$eval_compile_plan_list_valid([(pevalcompile[.PLAN.DIAGNOSTICS = eps])],(n_image,P_image)*)',
    'PhpStep: S ~> S_error',
    'S_error.COMPLETION = FATAL TARGET_MESSAGE 1',
    'S_error.ERRORORIGIN = (PORIGIN 1 eps) /\\ S_error.TRACE = eps',
    'S_error.EVENTS = S.EVENTS /\\ S_error.TODO = pevalcontext.TAIL',
    'S_error.EVALCONTEXTS = eps /\\ S_error.SERVICELEFT = eps /\\ S_error.COMPILESTOP',
    'S_error.DECLARATIONS = S.DECLARATIONS ++ [PDEVALRESUME 1 S.REPORTING,PDEXIT 1 PCSCOMPILER]',
    '$eval_compile_waiting(S_error.DECLARATIONS) = eps',
    'S_error.ENV = S.ENV /\\ S_error.STORE = S.STORE /\\ S_error.REFCELLS = S.REFCELLS',
    'S_error.OBJECTS = S.OBJECTS /\\ S_error.OBJECTPROPS = S.OBJECTPROPS /\\ S_error.PROPREFS = S.PROPREFS',
    'S_error.ARRAYS = S.ARRAYS /\\ S_error.ALLOCATIONS = S.ALLOCATIONS',
    'S_error.CLASSES = S.CLASSES /\\ S_error.CLASSNAMES = S.CLASSNAMES /\\ S_error.FUNCTIONS = S.FUNCTIONS',
    'S_error.SOURCES = S.SOURCES /\\ S_error.CODE = S.CODE /\\ S_error.CURRENT = S.CURRENT /\\ S_error.FRAMES = S.FRAMES',
    '$class_named(S_error.CLASSNAMES,$ptascii("parameteroverrideeval21")) = eps',
    '$call_descriptors_valid(S_error) /\\ $declaration_history_valid(S_error)',
    '$eval_compile_owners_valid(S_error)',
    '$heap_graph(S_error) = $heap_graph(S)',
    '$heap_valid($heap_prune($heap_graph(S_error)))',
]

def locate(node, kind, path=()):
    if isinstance(node, dict) and node.get('node'):
        if node['node'] == kind:
            yield path, node
        for index, field in enumerate(node['fields']):
            yield from locate(field,kind,path + (('PCFIELD',index),))
    elif isinstance(node,dict) and 'program' in node:
        yield from locate(node['program'],kind,path)
    elif isinstance(node,list):
        for index, value in enumerate(node):
            yield from locate(value,kind,path + (('PCINDEX',index),))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision',required=True)
    parser.add_argument('--prepare-only',action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    git = lambda *parts: subprocess.check_output(['git',*parts],cwd=ROOT,env=recorder.ENV).decode().strip()
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_bytes())]
    php,adapter,runner,bridge,worker = (ROOT / name for name in ['.tools/php/bin/php','_build/default/adapter/main.exe',
        'tests/semantics/_build/default/numeric_runner.exe','.tools/php-file.so','frontend/worker.php'])
    source = HERE / 'parameter-override-eval.php'
    catalogue = HERE / 'parameter_override_cases.json'
    profile_path = ROOT / 'tests/semantics/profile.json'
    profile = json.loads(profile_path.read_bytes())
    catalogue_data = json.loads(catalogue.read_bytes())
    original = next(row for row in catalogue_data['cases'] if row['id'] == 'eval-target-uncatchable')
    assert sha(source) == original['source_sha256']
    assert catalogue_data['native_profile'] == profile and original['exit_status'] == 255
    assert original['status'] == 'php_error'
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    assert base64.b64decode(original['stdout_base64']) == b'BEFORE|'
    native_stderr = base64.b64decode(original['stderr_template_base64']).decode()
    notice = native_stderr.splitlines()[0].removeprefix('Deprecated: ').split(' in ',1)[0]
    watched = [Path(__file__),manifest,*modules,php,adapter,runner,bridge,worker,source,catalogue,profile_path,ROOT / 'spec/schema.json',ROOT / 'tests/semantics/recorded_worker.py',
        ROOT / 'tests/semantics/error_handler_run.py']
    before = {str(path):sha(path) for path in watched}
    revision,status = git('rev-parse','HEAD'),git('status','--short')
    assert not status and revision == args.revision,(revision,status)
    out = Path(tempfile.mkdtemp(prefix='parameter-override-protocol-',dir=ROOT / '.tools'))
    print(out,flush=True)
    report = {'revision':revision,'inputs':before,'profile':profile,'mode':'SL','cache':False,'det':True,
        'evaluated':False,'application_evaluations':0,'source_agreements':0,'derived_premises':len(DERIVED),
        'reached_premises':len(RUNTIME),'budget_seconds':120,'environment':{'LC_ALL':'C','TZ':'UTC','jobs':1}}
    flags = [arg for key,value in profile.items() for arg in ('-d',key + '=' + value)]
    frontend = Worker([str(php),'-n',*flags,'-d','extension=' + str(bridge),str(worker)],out / 'frontend')
    adapter_worker = None
    try:
        adapter_worker = Worker([str(adapter),str(ROOT)],out / 'adapter')
        parsed = frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'],parsed
        checked = adapter_worker.request({'op':'check','ast':parsed['ast'],'fixture':True})
        eval_node = next(locate(parsed['ast'],'Expr_Eval'))[1]
        code = base64.b64decode(eval_node['fields'][0]['fields'][0]['bytes'])
        parsed_unit = frontend.request({'op':'parse-eval','source':base64.b64encode(code).decode(),
            'id':'1','mode':'eval','profile':'cli-raw-85'})
        assert parsed_unit['accepted'],parsed_unit
        unit = adapter_worker.request({'op':'check','ast':parsed_unit['ast'],'fixture':True})
    finally:
        if adapter_worker:
            adapter_worker.close()
        frontend.close()
    try:
        paths = {kind:next(locate(parsed_unit['ast'],kind))[0] for kind in ['Stmt_Class','Stmt_ClassMethod']}
        path = lambda kind: '[' + ','.join(atom + ' ' + str(index) for atom,index in paths[kind]) + ']'
        replacements = {'CLASS_PATH':path('Stmt_Class'),'METHOD_PATH':path('Stmt_ClassMethod'),
            'NOTICE_MESSAGE':'$ptascii(' + json.dumps(notice) + ')',
            'TARGET_MESSAGE':'$ptascii("Attribute \\\"Override\\\" cannot target parameter (allowed targets: method, property)")'}
        checks = DERIVED + RUNTIME
        content = PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
        content += '  -- if S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')\n'
        content += '  -- if S_initial.COMPLETION = NORMAL \\/ S_initial.COMPLETION = BUDGET\n'
        content += '  -- if S_pending = $ptarget_await(S_initial,1000)\n  -- if S_pending.COMPLETION = SOURCE_PENDING\n'
        content += '  -- if S_accepted = $eval_resume(S_pending,SOURCE_ACCEPT 1 (' + str(list(code)) + ') ' + unit['fixture'] + ')\n'
        content += '  -- if S_accepted.COMPLETION = NORMAL \\/ S_accepted.COMPLETION = BUDGET\n'
        content += '  -- if S_found = $ptarget_seek(S_accepted,1000)\n'
        content += '  -- if S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET\n'
        content += '  -- if S = S_found[.COMPLETION = NORMAL]\n  -- if S.TODO = (EVAL_COMPILE_RESUME pevalcompile) :: ptask_tail*\n'
        for check in checks:
            for key,value in replacements.items():
                check = check.replace(key,value)
            content += '  -- ' + ('' if check.startswith('PhpStep:') else 'if ') + check + '\n'
        content += 'def $main() = false -- otherwise\n'
        fixture = out / 'target.watsup'
        fixture.write_text(content)
        report.update(fixture=str(fixture),fixture_sha256=sha(fixture),unit_sha256=hashlib.sha256(code).hexdigest(),passed=True)
        if not args.prepare_only:
            report['application_invocations'] = 1
            report['process'] = process = recorder.recorded([str(runner),'--sl',*map(str,modules),str(fixture)],out / 'target',120)
            report['evaluated'] = process['exit'] == 0 and (out / 'target.stdout').read_bytes() in (b'true\n',b'false\n')
            report['application_evaluations'] = int(report['evaluated'])
            report['passed'] = (process['exit'] == 0 and not process['timeout'] and not process['group_after']
                and (out / 'target.stdout').read_bytes() == b'true\n' and not (out / 'target.stderr').read_bytes())
            print('target',report['passed'],flush=True)
    finally:
        report.update(inputs_stable=before == {str(path):sha(path) for path in watched},
            head_stable=revision == git('rev-parse','HEAD'),status_stable=status == git('status','--short'))
        report['passed'] = report.get('passed',False) and all(report[key] for key in ['inputs_stable','head_stable','status_stable'])
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report,indent=2) + '\n')
    assert report['passed']

if __name__ == '__main__':
    main()
