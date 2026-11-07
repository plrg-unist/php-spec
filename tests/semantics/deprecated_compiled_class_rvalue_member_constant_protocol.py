#!/usr/bin/env python3
"""Check late class publication during effectful member evaluation."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_global_constant_protocol import PREFIX
from deprecated_class_constant_fetch_protocol import SELECTED as FETCH_SELECTED
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'tests/semantics/deprecated_compiled_class_rvalue_member_constant/late-publication.php'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quoted=lambda s:'$base64('+json.dumps(base64.b64encode(s.encode()).decode())+')'
SELECTED=FETCH_SELECTED+r'''
dec $compiled_rvalue_ready(pstate,bool) : bool
def $compiled_rvalue_ready(S,false) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask*
def $compiled_rvalue_ready(S,true) = true
  -- if S.TODO = (CLASS_CONST_MEMBER expression_class poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: ptask*
def $compiled_rvalue_ready(S,b) = false -- otherwise
dec $compiled_rvalue_pause(pstate,bool,nat) : pstate
def $compiled_rvalue_pause(S,b,n) = S -- if $compiled_rvalue_ready(S,b)
def $compiled_rvalue_pause(S,b,n) = $compiled_rvalue_pause(S_next[.COMPLETION = NORMAL],b,$nabs($(n - 1)))
  -- if ~$compiled_rvalue_ready(S,b)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $compiled_rvalue_pause(S,b,n) = S -- otherwise
'''


def fields(fixture,response):
    expected=json.loads((SOURCE.parent/'cases.json').read_text())['late-publication']['stdout']
    target=quoted('Ns233Late\\Target233')
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(SOURCE)).decode())+')',
        'S_before = $compiled_rvalue_pause(S_start[.COMPLETION = NORMAL],false,30000)','$compiled_rvalue_ready(S_before,false)',
        'S_before.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask_tail*',
        'S_before.ORIGIN = (porigin_site)','porigin_site = PORIGIN n_unit pcpath',
        '$origin_node(S_before.SOURCES,porigin_site) = (NExprClassConstFetch expression_class expression_member metadata)',
        'expression_class = NExprBinaryOpConcat expression_left expression_right metadata_concat',
        'expression_member = NExprFuncCall name_member (SEQUENCE eps) metadata_member',
        '$ccn_output(S_before.EVENTS) = $ptascii("B|")',
        '$class_named(S_before.CLASSNAMES,$ptlc('+target+')) = eps',
        '$compiled_read(S_before,PORIGIN n_unit (pcpath ++ [PCFIELD 0])) = (PSTRING '+target+')',
        '$class_constant_literal(S_before,expression_class)',
        'S_class = $class_constant_selector(S_before,expression_class,z)','S_class.COMPLETION = NORMAL',
        'S_class.RESULT = KNOWN (PSTRING '+target+')',
        '$class_named(S_class.CLASSNAMES,$ptlc('+target+')) = eps',
        '$class_constant_selected_valid(S_class,expression_class,S_class.RESULT)',
        'S_scheduled_one = $drive_steps(S_before,1)','S_scheduled_one.COMPLETION = BUDGET',
        'S_scheduled = S_scheduled_one[.COMPLETION = NORMAL]',
        'S_scheduled.TODO = ptask_eval :: (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING '+target+')) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING '+target+')) z) :: ptask_tail*',
        'ptask_eval = $at_task($origin_child(S_before.ORIGIN,[PCFIELD 1]),EVAL expression_member)',
        '$class_named(S_scheduled.CLASSNAMES,$ptlc('+target+')) = eps',
        '$call_descriptors_valid(S_scheduled)',
        'S_request = $drive_steps(S_scheduled,30000)','S_request.COMPLETION = SOURCE_PENDING',
        '$ccn_output(S_request.EVENTS) = $ptascii("B|M|")',
        '$class_named(S_request.CLASSNAMES,$ptlc('+target+')) = eps',
        '$eval_response_valid(S_request,'+response+')',
        'S_entered = $eval_resume(S_request,'+response+')','S_entered.COMPLETION = NORMAL',
        'S_pair = $compiled_rvalue_pause(S_entered,true,30000)','$compiled_rvalue_ready(S_pair,true)',
        'S_pair.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING '+target+')) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING '+target+')) z) :: ptask_tail*',
        '$ccn_output(S_pair.EVENTS) = $ptascii("B|M|")','S_pair.CURRENT = eps','S_pair.FRAMES = eps','S_pair.HELD = eps',
        'S_pair.RESULT = KNOWN pvalue_member','$constant_value_class_valid(S_pair,pvalue_member,PVSTRING false)',
        '$string_bytes(pvalue_member) = ($ptascii("VALUE"))','$value_nodes(pvalue_member) = eps',
        '$(|S_pair.SOURCES|) = $(|S_before.SOURCES| + 1)',
        '$class_named(S_pair.CLASSNAMES,$ptlc('+target+')) = (porigin_target)',
        'porigin_target = PORIGIN n_eval pcpath_decl','n_eval =/= n_unit',
        '$class_at(S_pair.CLASSES,porigin_target) = (pclassdesc)','pclassdesc.NAME = '+target,
        '$class_constant_lookup(S_pair,porigin_target,$ptascii("VALUE"),|S_pair.CLASSES|) = (pclassconstantdesc)',
        'pclassconstantdesc.OWNER = porigin_target','pclassconstantdesc.FOLDED',
        '$class_constant_deprecated(S_pair,pclassconstantdesc)',
        '$eval_state_valid(S_pair)','$declaration_history_valid(S_pair)',
        '$compiled_read(S_pair,PORIGIN n_unit (pcpath ++ [PCFIELD 0])) = (PSTRING '+target+')',
        '$code_at(S_pair.CODE,n_unit) = (pcode)','$code_expression(pcode.EXPRESSIONS,pcpath) = ((z,false))',
        '$code_expression(pcode.EXPRESSIONS,pcpath ++ [PCFIELD 0]) = ((z_class,true))',
        '$code_expression(pcode.EXPRESSIONS,pcpath ++ [PCFIELD 1]) = ((z_member,false))',
        '$class_constant_compiled_rvalue_source(S_pair,pclassconstantdesc.ORIGIN,'+target+',$ptascii("VALUE"),z)',
        '$class_constant_compiled_rvalue_entry(S_pair,S_pair.RESULT,expression_class,KNOWN (PSTRING '+target+'),z,ptask_tail*) = (pclassconstantdesc)',
        '$call_task_valid(S_pair,CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING '+target+')) z)','$call_descriptors_valid(S_pair)',
        '~$class_constant_notice_valid(S_pair,pclassconstantdesc.ORIGIN,'+target+',$ptascii("VALUE"),z)',
        '~$class_constant_notice_protected(S_pair,pclassconstantdesc.ORIGIN)',
        '$class_constant_compiled_rvalue_entry(S_pair,REFERENCE 0,expression_class,KNOWN (PSTRING '+target+'),z,ptask_tail*) = eps',
        '$class_constant_compiled_rvalue_entry(S_pair,KNOWN PNULL,expression_class,KNOWN (PSTRING '+target+'),z,ptask_tail*) = eps',
        '$class_constant_compiled_rvalue_entry(S_pair,S_pair.RESULT,expression_class,KNOWN (PSTRING '+target+'),z,DISCARD :: ptask_tail*) = eps',
        '$class_constant_compiled_rvalue_entry(S_pair[.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING '+target+')) z) :: ptask_tail*],S_pair.RESULT,expression_class,KNOWN (PSTRING '+target+'),z,ptask_tail*) = eps',
        '~$class_constant_compiled_rvalue_source(S_pair,pclassconstantdesc.ORIGIN,'+target+',$ptascii("VALUE"),$(z + 1))',
        'S_warn_one = $drive_steps(S_pair,1)','S_warn_one.COMPLETION = BUDGET','S_warn = S_warn_one[.COMPLETION = NORMAL]',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN '+target+' $ptascii("VALUE") z',
        '$error_call_valid(S_warn,perrorcall)','$call_task_valid(S_warn,perrorcall.RESUME)',
        '$task_nodes(perrorcall.RESUME) = eps','$class_constant_notice_protected(S_warn,pclassconstantdesc.ORIGIN)',
        'S_resume = $ccn_pause(S_warn,1,30000)','$ccn_ready(S_resume,1)',
        '$ccn_output(S_resume.EVENTS) = $ptascii("B|M|H|")',
        'S_resume.TODO = perrorcall.RESUME :: ptask_resume*',
        '$class_constant_notice_valid(S_resume,pclassconstantdesc.ORIGIN,'+target+',$ptascii("VALUE"),z)',
        '~$class_constant_notice_valid(S_resume[.TODO = ptask_resume*],pclassconstantdesc.ORIGIN,'+target+',$ptascii("VALUE"),z)',
        'S_value_one = $drive_steps(S_resume,1)','S_value_one.COMPLETION = BUDGET','S_value = S_value_one[.COMPLETION = NORMAL]',
        'S_value.RESULT = KNOWN (PINT 7)','S_value.EVENTS = S_resume.EVENTS',
        'S_value.CLASSCONSTANTCACHE = eps','S_value.CLASSCONSTANTHISTORY = S_resume.CLASSCONSTANTHISTORY',
        'S_second_warn = $ccn_pause(S_value,0,30000)','$ccn_ready(S_second_warn,0)',
        '$ccn_output(S_second_warn.EVENTS) = $ptascii("B|M|H|O|7|")',
        'S_second_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_second*',
        'perrorcall_second.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN '+target+' $ptascii("VALUE") z_second',
        '$error_call_valid(S_second_warn,perrorcall_second)',
        'S_done = $drive_steps(S_second_warn,30000)','S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = '+quoted(expected),'S_done.CLASSCONSTANTCACHE = eps',
        '$(|S_done.SOURCES|) = $(|S_pair.SOURCES|)','$class_constant_state_valid(S_done)','$call_descriptors_valid(S_done)']


def prepare(out):
    frontend=Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],out/'frontend')
    adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],out/'adapter')
    try:
        parsed=frontend.request({'op':'parse','source':base64.b64encode(SOURCE.read_bytes()).decode()});assert parsed['accepted'] and not parsed['diagnostics']
        checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True});assert checked['ok']
        def nodes(value):
            if isinstance(value,dict):
                yield value
                for child in value.values():yield from nodes(child)
            elif isinstance(value,list):
                for child in value:yield from nodes(child)
        codes=[base64.b64decode(node['fields'][0]['bytes']) for node in nodes(parsed['ast']['program']) if node.get('node')=='Scalar_String' and base64.b64decode(node['fields'][0]['bytes']).startswith(b'namespace Ns233Late;')]
        assert len(codes)==1
        code=codes[0]
        parsed_eval=frontend.request({'op':'parse-eval','id':'1','mode':'eval','profile':'cli-raw-85','source':base64.b64encode(code).decode()})
        assert parsed_eval['accepted'] and not parsed_eval['diagnostics']
        checked_eval=adapter.request({'op':'check','ast':parsed_eval['ast'],'fixture':True});assert checked_eval['ok']
        response='SOURCE_ACCEPT 1 ('+quoted(code.decode())+') '+checked_eval['fixture']
        (out/'eval1.php').write_bytes(code)
    finally:
        try:adapter.close()
        finally:frontend.close()
    checks=fields(checked['fixture'],response)
    (out/'assertions.json').write_text(json.dumps(checks,indent=2)+'\n')
    (out/'protocol.watsup').write_text(PREFIX+SELECTED+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+c+'\n' for c in checks))
    return len(checks)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    modules=[ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    paths=[Path(__file__),SOURCE,SOURCE.parent/'cases.json',*modules,*(ROOT/p for p in (
        'spec/semantics/modules.json','spec/schema.json','frontend/worker.php',
        'tests/semantics/deprecated_class_constant_fetch_protocol.py',
        'tests/semantics/deprecated_parameter_default_protocol.py','tests/semantics/deprecated_global_constant_protocol.py',
        'tests/semantics/recorded_worker.py','tests/semantics/error_handler_run.py','tests/semantics/static_types.py',
        '.tools/php/bin/php','.tools/php-file.so','_build/default/adapter/main.exe','tests/semantics/_build/default/numeric_runner.exe'))]
    before={str(p.relative_to(ROOT)):sha(p) for p in paths};head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    report={'head':head,'inputs':before,'module_count':len(modules),'source_agreement_credit':0,'passed':False}
    try:
        report['premises']=prepare(out)
        report['process']=recorded([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),'--sl',*map(str,modules),str(out/'protocol.watsup')],out/'check',240)
        report['stdout']=(out/'check.stdout').read_text();report['stderr']=(out/'check.stderr').read_text()
        report['head_stable']=head==subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        report['inputs_stable']=before=={str(p.relative_to(ROOT)):sha(p) for p in paths}
        report['passed']=report['process']['exit']==0 and not report['process']['timeout'] and not report['process']['group_after'] and report['stdout']=='true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable']
    finally:(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    if not report['passed']:print(report.get('stdout','')[:2000],report.get('stderr','')[:4000])
    assert report['passed'];print('pass',report['premises'])


if __name__=='__main__':main()
