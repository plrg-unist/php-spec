#!/usr/bin/env python3
"""Check scoped compiled member authority and lexical/called visibility."""
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
SOURCE=ROOT/'tests/semantics/deprecated_scoped_compiled_member_constant/self-static.php'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quoted=lambda s:'$base64('+json.dumps(base64.b64encode(s.encode()).decode())+')'
SELECTED=FETCH_SELECTED+r'''
dec $scoped_pool_ready(pstate) : bool
def $scoped_pool_ready(S) = true
  -- if S.TODO = (CLASS_CONST_MEMBER name poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if porigin = PORIGIN n_unit pcpath
  -- if $compiled_read(S,PORIGIN n_unit (pcpath ++ [PCFIELD 1])) = (PSTRING ptbytes_member)
  -- if $origin_node(S.SOURCES,porigin) = (NExprClassConstFetch name expression_member metadata)
  -- if $ppscoped_keyword(name) /\ ~$method_receiver_is_variable(expression_member)
def $scoped_pool_ready(S) = false -- otherwise
dec $scoped_pool_pause(pstate,nat) : pstate
def $scoped_pool_pause(S,n) = S -- if $scoped_pool_ready(S)
def $scoped_pool_pause(S,n) = $scoped_pool_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$scoped_pool_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $scoped_pool_pause(S,n) = S -- otherwise
'''


def fields(fixture):
    expected=json.loads((SOURCE.parent/'cases.json').read_text())['self-static']['stdout']
    base=quoted('Ns235Scope\\Base235');child=quoted('Ns235Scope\\Child235')
    checks=['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(SOURCE)).decode())+')',
        'S_pair = $scoped_pool_pause(S_start[.COMPLETION = NORMAL],30000)','$scoped_pool_ready(S_pair)',
        'S_pair.TODO = (CLASS_CONST_MEMBER name_class poperand_class z) :: (CLASS_CONST_CAPTURE porigin_site poperand_class z) :: ptask_tail*',
        'poperand_class = KNOWN (PSTRING '+base+')','porigin_site = PORIGIN n_unit pcpath',
        'S_pair.RESULT = KNOWN pvalue_member','$string_bytes(pvalue_member) = ($ptascii("A"))',
        '$compiled_read(S_pair,PORIGIN n_unit (pcpath ++ [PCFIELD 1])) = (PSTRING $ptascii("A"))',
        '$code_at(S_pair.CODE,n_unit) = (pcode)',
        '$code_expression(pcode.EXPRESSIONS,pcpath) = ((z,false))',
        '$code_expression(pcode.EXPRESSIONS,pcpath ++ [PCFIELD 1]) = ((z_member,true))',
        '$class_named(S_pair.CLASSNAMES,$ptlc('+base+')) = (porigin_base_class)',
        '$class_constant_lookup(S_pair,porigin_base_class,$ptascii("A"),|S_pair.CLASSES|) = (pclassconstantdesc_a)',
        '$class_constant_lookup(S_pair,porigin_base_class,$ptascii("B"),|S_pair.CLASSES|) = (pclassconstantdesc_b)',
        'pclassconstantdesc_a.VISIBILITY = PROPERTY_PRIVATE',
        'pclassconstantdesc_b.VISIBILITY = PROPERTY_PROTECTED',
        '$class_constant_pooled_dynamic_source(S_pair,pclassconstantdesc_a.ORIGIN,'+base+',$ptascii("A"),z)',
        '~$class_constant_pooled_dynamic_source(S_pair,pclassconstantdesc_b.ORIGIN,'+base+',$ptascii("B"),z)',
        '$class_constant_notice_valid(S_pair[.RESULT = KNOWN (PSTRING $ptascii("B"))],pclassconstantdesc_a.ORIGIN,'+base+',$ptascii("A"),z)',
        '~$class_constant_notice_valid(S_pair[.RESULT = KNOWN (PSTRING $ptascii("B"))],pclassconstantdesc_b.ORIGIN,'+base+',$ptascii("B"),z)',
        '$class_constant_pooled_cv_entry(S_pair,S_pair.RESULT,name_class,poperand_class,z,ptask_tail*) = eps',
        'pcode_no_member = pcode[.EXPRESSIONS = (CODEEXPR (pcpath ++ [PCFIELD 1]) z_member false) :: pcode.EXPRESSIONS]',
        'S_no_member = S_pair[.CODE = [pcode_no_member]]',
        '$class_constant_keyword_method(S_no_member,porigin_site)',
        '$compiled_read(S_no_member,PORIGIN n_unit (pcpath ++ [PCFIELD 1])) = eps',
        '~$class_constant_notice_valid(S_no_member,pclassconstantdesc_a.ORIGIN,'+base+',$ptascii("A"),z)',
        '~$class_constant_notice_valid(S_pair[.POOLS = eps],pclassconstantdesc_a.ORIGIN,'+base+',$ptascii("A"),z)',
        'S_warn_one = $drive_steps(S_pair,1)','S_warn_one.COMPLETION = BUDGET','S_warn1 = S_warn_one[.COMPLETION = NORMAL]']
    previous=None
    for index,(keyword,member,requested,called,visibility,value) in enumerate([
        ('self','A',base,base,'PRIVATE',7),('static','B',base,base,'PROTECTED',8),
        ('self','A',base,child,'PRIVATE',7),('static','B',child,child,'PROTECTED',9)],1):
        w=f'S_warn{index}';v=f'S_resume{index}';a=f'S_value{index}';ctx=f'pcallcontext_{index}';desc=f'pclassconstantdesc_{index}';line=f'z_{index}';site=f'porigin_site{index}';fn=f'pfunction_{index}';path=f'pcpath_{index}'
        if previous is not None:checks += [w+' = $ccn_pause('+previous+',0,30000)','$ccn_ready('+w+',0)']
        checks += [w+'.TODO = (ERROR_HANDLER_INVOKE perrorcall_'+str(index)+') :: ptask_warn'+str(index)+'*',
            'perrorcall_'+str(index)+'.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl'+str(index)+' '+requested+' $ptascii("'+member+'") '+line,
            '$class_constant_origin('+w+'.CLASSES,porigin_decl'+str(index)+') = ('+desc+')',
            desc+'.VISIBILITY = PROPERTY_'+visibility,desc+'.FOLDED',
            w+'.ORIGIN = ('+site+')',site+' = PORIGIN n_unit_'+str(index)+' '+path,
            '$origin_node('+w+'.SOURCES,'+site+') = (NExprClassConstFetch (NName (BYTES text_keyword'+str(index)+') metadata_keyword'+str(index)+') expression_member'+str(index)+' metadata_fetch'+str(index)+')',
            'expression_member'+str(index)+' = NExprBinaryOpConcat expression_left'+str(index)+' expression_right'+str(index)+' metadata_concat'+str(index),
            '$ptlc($base64(text_keyword'+str(index)+')) = $ptascii("'+keyword+'")',
            w+'.CURRENT = ('+ctx+')',ctx+'.LEXICAL_CLASS = (porigin_base_class)',
            '$class_named('+w+'.CLASSNAMES,$ptlc('+called+')) = (porigin_called'+str(index)+')',ctx+'.CALLED_CLASS = (porigin_called'+str(index)+')',
            ctx+'.RECEIVER = eps',
            '$target_function('+w+','+ctx+'.TARGET) = ('+fn+')',ctx+'.FUNCTION = '+fn+'.ORIGIN',
            '$code_expression('+fn+'.CODE.EXPRESSIONS,'+path+') = (('+line+',false))',
            '$code_expression('+fn+'.CODE.EXPRESSIONS,'+path+' ++ [PCFIELD 1]) = ((z_member'+str(index)+',true))',
            '$compiled_read('+w+',PORIGIN n_unit_'+str(index)+' ('+path+' ++ [PCFIELD 1])) = (PSTRING $ptascii("'+member+'"))',
            '$class_constant_keyword_method('+w+','+site+')',
            '$class_constant_visible('+w+','+desc+')',
            '$class_constant_pooled_dynamic_source('+w+','+desc+'.ORIGIN,'+requested+',$ptascii("'+member+'"),'+line+')',
            '$class_constant_notice_valid('+w+','+desc+'.ORIGIN,'+requested+',$ptascii("'+member+'"),'+line+')',
            '$error_call_valid('+w+',perrorcall_'+str(index)+')','$call_descriptors_valid('+w+')',
            v+' = $ccn_pause('+w+',1,30000)','$ccn_ready('+v+',1)',v+'.CURRENT = ('+ctx+')',
            '$class_constant_notice_valid('+v+','+desc+'.ORIGIN,'+requested+',$ptascii("'+member+'"),'+line+')']
        if index==1:
            checks += ['$task_nodes(perrorcall_1.RESUME) = eps',
                '~$class_constant_notice_valid('+v+'[.RESULT = KNOWN (PSTRING $ptascii("B"))],pclassconstantdesc_b.ORIGIN,'+base+',$ptascii("B"),'+line+')',
                '~$class_constant_notice_valid('+v+','+desc+'.ORIGIN,'+base+',$ptascii("A"),$('+line+' + 1))',
                '~$class_constant_pooled_dynamic_source('+v+'[.CURRENT = eps],'+desc+'.ORIGIN,'+base+',$ptascii("A"),'+line+')']
        if index==3:
            checks += [ctx+'.FUNCTION = pcallcontext_1.FUNCTION',ctx+'.CALLED_CLASS =/= pcallcontext_1.CALLED_CLASS',
                site+' = porigin_site1',desc+'.ORIGIN = pclassconstantdesc_1.ORIGIN',
                '~$class_constant_selected_valid('+w+',NName (BYTES text_keyword3) metadata_keyword3,KNOWN (PSTRING '+child+'))']
        if index==4:
            checks += ['pclassconstantdesc_4.ORIGIN =/= pclassconstantdesc_2.ORIGIN',
                'pclassconstantdesc_4.OWNER = porigin_called4',
                '~$class_constant_selected_valid('+w+',NName (BYTES text_keyword4) metadata_keyword4,KNOWN (PSTRING '+base+'))']
        checks += ['S_result_one'+str(index)+' = $drive_steps('+v+',1)','S_result_one'+str(index)+'.COMPLETION = BUDGET',
            a+' = S_result_one'+str(index)+'[.COMPLETION = NORMAL]',a+'.RESULT = KNOWN (PINT '+str(value)+')',
            a+'.EVENTS = '+v+'.EVENTS',a+'.CLASSCONSTANTCACHE = eps',a+'.CLASSCONSTANTHISTORY = '+v+'.CLASSCONSTANTHISTORY',
            '~$class_constant_notice_protected('+a+','+desc+'.ORIGIN)']
        previous=a
    checks += ['S_done = $drive_steps(S_value4,30000)','S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = '+quoted(expected),'S_done.CLASSCONSTANTCACHE = eps',
        '$class_constant_state_valid(S_done)','$call_descriptors_valid(S_done)']
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
