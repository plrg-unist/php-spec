#!/usr/bin/env python3
"""Check caller-method scope after effectful constant member completion."""
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
SOURCE=ROOT/'tests/semantics/deprecated_keyword_rvalue_member_constant/static-scopes.php'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quoted=lambda s:'$base64('+json.dumps(base64.b64encode(s.encode()).decode())+')'
SELECTED=FETCH_SELECTED+r'''
dec $keyword_rvalue_ready(pstate) : bool
def $keyword_rvalue_ready(S) = true
  -- if S.TODO = (CLASS_CONST_MEMBER name poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES,porigin) = (NExprClassConstFetch name expression_member metadata)
  -- if $ppscoped_keyword(name) /\ ~$method_receiver_is_variable(expression_member)
def $keyword_rvalue_ready(S) = false -- otherwise
dec $keyword_rvalue_pause(pstate,nat) : pstate
def $keyword_rvalue_pause(S,n) = S -- if $keyword_rvalue_ready(S)
def $keyword_rvalue_pause(S,n) = $keyword_rvalue_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$keyword_rvalue_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $keyword_rvalue_pause(S,n) = S -- otherwise
'''


def fields(fixture):
    expected=json.loads((SOURCE.parent/'cases.json').read_text())['static-scopes']['stdout']
    base=quoted('Ns232Static\\Base232');child=quoted('Ns232Static\\Child232')
    checks=['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(SOURCE)).decode())+')',
        'S_pair = $keyword_rvalue_pause(S_start[.COMPLETION = NORMAL],30000)','$keyword_rvalue_ready(S_pair)',
        'S_pair.TODO = (CLASS_CONST_MEMBER name_class poperand_class z) :: (CLASS_CONST_CAPTURE porigin_site poperand_class z) :: ptask_tail*',
        'poperand_class = KNOWN (PSTRING '+base+')','S_pair.RESULT = KNOWN pvalue_member',
        '$constant_value_class_valid(S_pair,pvalue_member,PVSTRING false)','$string_bytes(pvalue_member) = ($ptascii("A"))',
        '$value_nodes(pvalue_member) = eps','$ccn_output(S_pair.EVENTS) = $ptascii("S|M|")',
        'S_read = $resolve_at(S_pair,S_pair.RESULT,z)','S_read.RESULT = S_pair.RESULT',
        '$class_named(S_read.CLASSNAMES,$ptlc('+base+')) = (porigin_base_class)',
        '$class_constant_lookup(S_read,porigin_base_class,$ptascii("A"),|S_read.CLASSES|) = (pclassconstantdesc_a)',
        '$class_constant_lookup(S_read,porigin_base_class,$ptascii("B"),|S_read.CLASSES|) = (pclassconstantdesc_b)',
        'pclassconstantdesc_a.FOLDED','pclassconstantdesc_b.FOLDED',
        '$class_constant_keyword_rvalue_entry(S_read,S_pair.RESULT,name_class,poperand_class,z,ptask_tail*) = (pclassconstantdesc_a)',
        '$class_constant_keyword_rvalue_source(S_read,pclassconstantdesc_b.ORIGIN,'+base+',$ptascii("B"),z)',
        '~$class_constant_notice_valid(S_read,pclassconstantdesc_a.ORIGIN,'+base+',$ptascii("A"),z)',
        '$class_constant_keyword_rvalue_entry(S_read,KNOWN (PSTRING $ptascii("B")),name_class,poperand_class,z,ptask_tail*) = eps',
        '$class_constant_keyword_rvalue_entry(S_read,REFERENCE 0,name_class,poperand_class,z,ptask_tail*) = eps',
        '$class_constant_keyword_rvalue_entry(S_read,KNOWN PNULL,name_class,poperand_class,z,ptask_tail*) = eps',
        '$class_constant_keyword_rvalue_entry(S_read,S_pair.RESULT,name_class,poperand_class,z,DISCARD :: ptask_tail*) = eps',
        '$class_constant_keyword_rvalue_entry(S_read[.TODO = (CLASS_CONST_MEMBER name_class poperand_class z) :: ptask_tail*],S_pair.RESULT,name_class,poperand_class,z,ptask_tail*) = eps',
        '~$class_constant_keyword_method(S_read[.CURRENT = eps],porigin_site)',
        '~$class_constant_keyword_method(S_read[.CONSTCONTEXT = ({ORIGIN pclassconstantdesc_a.ORIGIN,LINE z,FACTS eps})],porigin_site)',
        'S_warn_one = $drive_steps(S_pair,1)','S_warn_one.COMPLETION = BUDGET','S_warn1 = S_warn_one[.COMPLETION = NORMAL]']
    previous=None
    for index,(keyword,member,requested,called,value) in enumerate([
        ('self','A',base,base,7),('static','B',base,base,8),
        ('self','A',base,child,7),('static','B',child,child,9)],1):
        w=f'S_warn{index}';v=f'S_resume{index}';a=f'S_value{index}';ctx=f'pcallcontext_{index}';desc=f'pclassconstantdesc_{index}';z=f'z_{index}';site=f'porigin_site{index}';fn=f'pfunction_{index}';path=f'pcpath_{index}'
        if previous is not None:checks += [w+' = $ccn_pause('+previous+',0,30000)','$ccn_ready('+w+',0)']
        checks += [w+'.TODO = (ERROR_HANDLER_INVOKE perrorcall_'+str(index)+') :: ptask_warn'+str(index)+'*',
            'perrorcall_'+str(index)+'.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl'+str(index)+' '+requested+' $ptascii("'+member+'") '+z,
            '$class_constant_origin('+w+'.CLASSES,porigin_decl'+str(index)+') = ('+desc+')',
            w+'.ORIGIN = ('+site+')',site+' = PORIGIN n_unit_'+str(index)+' '+path,
            '$origin_node('+w+'.SOURCES,'+site+') = (NExprClassConstFetch (NName (BYTES text_keyword'+str(index)+') metadata_keyword'+str(index)+') expression_member'+str(index)+' metadata_fetch'+str(index)+')',
            'expression_member'+str(index)+' = NExprFuncCall name_member'+str(index)+' (SEQUENCE eps) metadata_member'+str(index),
            '$ptlc($base64(text_keyword'+str(index)+')) = $ptascii("'+keyword+'")',
            w+'.CURRENT = ('+ctx+')',ctx+'.LEXICAL_CLASS = (porigin_base_class)',
            '$class_named('+w+'.CLASSNAMES,$ptlc('+called+')) = (porigin_called'+str(index)+')',ctx+'.CALLED_CLASS = (porigin_called'+str(index)+')',
            '$target_function('+w+','+ctx+'.TARGET) = ('+fn+')',ctx+'.FUNCTION = '+fn+'.ORIGIN',
            '$code_expression('+fn+'.CODE.EXPRESSIONS,'+path+' ++ [PCFIELD 1]) = ((z_member'+str(index)+',false))',
            '$class_constant_keyword_method('+w+','+site+')',
            '$class_constant_notice_valid('+w+','+desc+'.ORIGIN,'+requested+',$ptascii("'+member+'"),'+z+')',
            '$error_call_valid('+w+',perrorcall_'+str(index)+')',
            v+' = $ccn_pause('+w+',1,30000)','$ccn_ready('+v+',1)',v+'.CURRENT = ('+ctx+')',
            '$class_constant_notice_valid('+v+','+desc+'.ORIGIN,'+requested+',$ptascii("'+member+'"),'+z+')']
        if index==1:
            checks += [ctx+'.RECEIVER = eps','$task_nodes(perrorcall_1.RESUME) = eps','$call_descriptors_valid('+w+')',
                '$code_name('+fn+'.CODE.NAMES,'+path+' ++ [PCFIELD 1]) = ((ptbytes_member_fn,eps))',
                '$callable_at('+w+'.CALLABLES,$ptlc(ptbytes_member_fn)) = (porigin_member_fn)',
                'porigin_member_fn =/= '+fn+'.ORIGIN',
                'S_member_now = $global_table_view('+v+')','$lookup(S_member_now.ENV,$ptascii("member232")) = (n_member)',
                'S_member_now.STORE[n_member] = DEFINED pvalue_now','$string_bytes(pvalue_now) = ($ptascii("B"))',
                '~$class_constant_notice_valid('+v+'[.RESULT = KNOWN (PSTRING $ptascii("B"))],pclassconstantdesc_b.ORIGIN,'+base+',$ptascii("B"),'+z+')',
                '~$class_constant_notice_valid('+v+','+desc+'.ORIGIN,'+base+',$ptascii("A"),$('+z+' + 1))',
                '~$class_constant_keyword_method('+w+','+fn+'.ORIGIN)']
        if index==3:
            checks += [ctx+'.FUNCTION = pcallcontext_1.FUNCTION',ctx+'.CALLED_CLASS =/= pcallcontext_1.CALLED_CLASS',
                '~$class_constant_selected_valid('+w+',NName (BYTES text_keyword3) metadata_keyword3,KNOWN (PSTRING '+child+'))',
                '~$class_constant_keyword_method('+w+'[.CURRENT = ('+ctx+'[.LEXICAL_CLASS = '+ctx+'.CALLED_CLASS])],'+site+')']
        if index==4:
            checks += ['pclassconstantdesc_4.ORIGIN =/= pclassconstantdesc_2.ORIGIN',
                'pclassconstantdesc_4.OWNER = porigin_called4',
                '~$class_constant_selected_valid('+w+',NName (BYTES text_keyword4) metadata_keyword4,KNOWN (PSTRING '+base+'))',
                '~$class_constant_keyword_method('+w+'[.CURRENT = ('+ctx+'[.CALLED_CLASS = (porigin_base_class)])],'+site+')']
        checks += ['S_result_one'+str(index)+' = $drive_steps('+v+',1)','S_result_one'+str(index)+'.COMPLETION = BUDGET',
            a+' = S_result_one'+str(index)+'[.COMPLETION = NORMAL]',a+'.RESULT = KNOWN (PINT '+str(value)+')',
            a+'.EVENTS = '+v+'.EVENTS',a+'.CLASSCONSTANTCACHE = eps',a+'.CLASSCONSTANTHISTORY = '+v+'.CLASSCONSTANTHISTORY',
            '~$class_constant_notice_protected('+a+','+desc+'.ORIGIN)']
        previous=a
    checks += ['S_done = $drive_steps(S_value4,30000)','S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = '+quoted(expected),'S_done.CLASSCONSTANTCACHE = eps',
        '~$class_constant_keyword_method(S_done,porigin_site1)','$class_constant_state_valid(S_done)','$call_descriptors_valid(S_done)']
    return checks


def prepare(out):
    frontend=Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],out/'frontend')
    adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],out/'adapter')
    try:
        parsed=frontend.request({'op':'parse','source':base64.b64encode(SOURCE.read_bytes()).decode()});assert parsed['accepted'] and not parsed['diagnostics']
        checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True});assert checked['ok']
    finally:
        try:adapter.close()
        finally:frontend.close()
    checks=fields(checked['fixture'])
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
