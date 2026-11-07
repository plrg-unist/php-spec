#!/usr/bin/env python3
"""Check private computed constant access before active notice protection."""
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
SOURCE=ROOT/'tests/semantics/deprecated_nonpublic_computed_constant/private-capture.php'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quoted=lambda s:'$base64('+json.dumps(base64.b64encode(s.encode()).decode())+')'
SELECTED=FETCH_SELECTED+r'''
dec $private_computed_ready(pstate,nat,porigin?) : bool
def $private_computed_ready(S,0,eps) = true
  -- if S.TODO = (CLASS_CONST_MEMBER name poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES,porigin) = (NExprClassConstFetch name (NExprVariable (BYTES text) metadata_member) metadata)
  -- if $ppscoped_keyword(name) /\ $base64(text) = $ptascii("member234")
def $private_computed_ready(S,1,(porigin_private)) = true
  -- if S.TODO = (CLASS_CONST_MEMBER name poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: ptask*
  -- if ~$ppscoped_keyword(name)
  -- if $method_current_scope(S) = eps
  -- if $class_constant_notice_protected(S,porigin_private)
def $private_computed_ready(S,2,eps) = true
  -- if S.TODO = (CLASS_CONST_MEMBER name poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES,porigin) = (NExprClassConstFetch name expression_member metadata)
  -- if $ppscoped_keyword(name) /\ ~$method_receiver_is_variable(expression_member)
def $private_computed_ready(S,n_mode,porigin?) = false -- otherwise
dec $private_computed_pause(pstate,nat,porigin?,nat) : pstate
def $private_computed_pause(S,n_mode,porigin?,n) = S -- if $private_computed_ready(S,n_mode,porigin?)
def $private_computed_pause(S,n_mode,porigin?,n) = $private_computed_pause(S_next[.COMPLETION = NORMAL],n_mode,porigin?,$nabs($(n - 1)))
  -- if ~$private_computed_ready(S,n_mode,porigin?)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $private_computed_pause(S,n_mode,porigin?,n) = S -- otherwise
'''


def fields(fixture):
    expected=json.loads((SOURCE.parent/'cases.json').read_text())['private-capture']['stdout']
    owner=quoted('Ns234Private\\Vault234')
    checks=['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(SOURCE)).decode())+')',
        'S_pair = $private_computed_pause(S_start[.COMPLETION = NORMAL],0,eps,30000)',
        '$private_computed_ready(S_pair,0,eps)',
        'S_pair.TODO = (CLASS_CONST_MEMBER name_class poperand_class z) :: (CLASS_CONST_CAPTURE porigin_site poperand_class z) :: ptask_tail*',
        'poperand_class = KNOWN (PSTRING '+owner+')','S_pair.RESULT = VARIABLE $ptascii("member234") z_variable',
        'S_read = $resolve_at(S_pair,S_pair.RESULT,z)','S_read.RESULT = KNOWN pvalue_member',
        '$string_bytes(pvalue_member) = ($ptascii("A"))',
        '$class_named(S_read.CLASSNAMES,$ptlc('+owner+')) = (porigin_owner)',
        '$class_constant_lookup(S_read,porigin_owner,$ptascii("A"),|S_read.CLASSES|) = (pclassconstantdesc_a)',
        '$class_constant_lookup(S_read,porigin_owner,$ptascii("B"),|S_read.CLASSES|) = (pclassconstantdesc_b)',
        'pclassconstantdesc_a.VISIBILITY = PROPERTY_PRIVATE','pclassconstantdesc_b.VISIBILITY = PROPERTY_PRIVATE',
        'pclassconstantdesc_a.FOLDED','pclassconstantdesc_b.FOLDED',
        '$class_constant_deprecated(S_read,pclassconstantdesc_a)',
        '~$class_constant_deprecated(S_read,pclassconstantdesc_a[.VISIBILITY = PROPERTY_PUBLIC])',
        '~$class_constant_deprecated(S_read,pclassconstantdesc_a[.VISIBILITY = PROPERTY_PROTECTED])',
        '$method_current_scope(S_read) = (porigin_owner)',
        '$class_constant_visible(S_read,pclassconstantdesc_a)',
        '$class_constant_keyword_method(S_read,porigin_site)',
        '$class_constant_notice_valid(S_read,pclassconstantdesc_a.ORIGIN,'+owner+',$ptascii("A"),z)',
        '~$class_constant_notice_valid(S_read,pclassconstantdesc_b.ORIGIN,'+owner+',$ptascii("B"),z)',
        '$call_descriptors_valid(S_read)',
        'S_warn1_raw = $drive_steps(S_pair,1)','S_warn1_raw.COMPLETION = BUDGET',
        'S_warn1 = S_warn1_raw[.COMPLETION = NORMAL]']
    for index,(member,value,prefix) in enumerate([
        ('A',7,'C|'),('A',7,'C|H|E|7|R|M|'),('B',8,'C|H|E|7|R|M|H|E|7|F|M|')],1):
        w=f'S_warn{index}';v=f'S_resume{index}';a=f'S_value{index}';ctx=f'pcallcontext_{index}';desc=f'pclassconstantdesc_{index}';line=f'z_{index}';site=f'porigin_site{index}'
        if index==2:
            checks += ['S_runtime_pair = $private_computed_pause(S_value1,2,eps,30000)',
                '$private_computed_ready(S_runtime_pair,2,eps)',
                'S_runtime_pair.TODO = (CLASS_CONST_MEMBER name_runtime poperand_class_runtime z_runtime) :: (CLASS_CONST_CAPTURE porigin_runtime poperand_class_runtime z_runtime) :: ptask_runtime_tail*',
                'S_runtime_pair.RESULT = KNOWN pvalue_runtime_member',
                '$string_bytes(pvalue_runtime_member) = ($ptascii("A"))',
                '$ccn_output(S_runtime_pair.EVENTS) = '+quoted(prefix),
                '$class_constant_keyword_rvalue_entry(S_runtime_pair,S_runtime_pair.RESULT,name_runtime,poperand_class_runtime,z_runtime,ptask_runtime_tail*) = (pclassconstantdesc_a)',
                '~$class_constant_notice_valid(S_runtime_pair,pclassconstantdesc_a.ORIGIN,'+owner+',$ptascii("A"),z_runtime)',
                'S_warn2_raw = $drive_steps(S_runtime_pair,1)','S_warn2_raw.COMPLETION = BUDGET',
                'S_warn2 = S_warn2_raw[.COMPLETION = NORMAL]']
        if index==3:
            checks += [w+' = $ccn_pause(S_value2,0,30000)','$ccn_ready('+w+',0)']
        checks += [w+'.TODO = (ERROR_HANDLER_INVOKE perrorcall_'+str(index)+') :: ptask_warn'+str(index)+'*',
            'perrorcall_'+str(index)+'.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl'+str(index)+' '+owner+' $ptascii("'+member+'") '+line,
            '$class_constant_origin('+w+'.CLASSES,porigin_decl'+str(index)+') = ('+desc+')',
            desc+'.VISIBILITY = PROPERTY_PRIVATE',w+'.ORIGIN = ('+site+')',
            w+'.CURRENT = ('+ctx+')',ctx+'.LEXICAL_CLASS = (porigin_owner)',ctx+'.CALLED_CLASS = (porigin_owner)',ctx+'.RECEIVER = eps',
            '$class_constant_keyword_method('+w+','+site+')',
            '$class_constant_visible('+w+','+desc+')',
            '$class_constant_notice_protected('+w+','+desc+'.ORIGIN)',
            '$class_constant_notice_valid('+w+','+desc+'.ORIGIN,'+owner+',$ptascii("'+member+'"),'+line+')',
            '$error_call_valid('+w+',perrorcall_'+str(index)+')','$call_descriptors_valid('+w+')',
            '$ccn_output('+w+'.EVENTS) = '+quoted(prefix)]
        if index==1:
            checks += ['S_denied = $private_computed_pause(S_warn1,1,(pclassconstantdesc_a.ORIGIN),30000)',
                '$private_computed_ready(S_denied,1,(pclassconstantdesc_a.ORIGIN))',
                'S_denied.TODO = (CLASS_CONST_MEMBER name_denied poperand_class_denied z_denied) :: (CLASS_CONST_CAPTURE porigin_denied poperand_class_denied z_denied) :: ptask_denied_tail*',
                'poperand_class_denied = KNOWN (PSTRING '+owner+')',
                'S_denied_read = $resolve_at(S_denied,S_denied.RESULT,z_denied)',
                'S_denied_read.RESULT = KNOWN pvalue_denied','$string_bytes(pvalue_denied) = ($ptascii("A"))',
                '$method_current_scope(S_denied_read) = eps',
                '$class_constant_deprecated(S_denied_read,pclassconstantdesc_a)',
                '~$class_constant_visible(S_denied_read,pclassconstantdesc_a)',
                '$class_constant_notice_protected(S_denied_read,pclassconstantdesc_a.ORIGIN)',
                '~$class_constant_notice_valid(S_denied_read,pclassconstantdesc_a.ORIGIN,'+owner+',$ptascii("A"),z_denied)',
                '~$call_task_valid(S_denied_read,DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc_a.ORIGIN '+owner+' $ptascii("A") z_denied)',
                '$call_descriptors_valid(S_denied_read)',
                '$ccn_output(S_denied_read.EVENTS) = $ptascii("C|H|")',
                'PhpStep: S_denied ~> S_taken',
                'S_taken.COMPLETION = THROWN "Error" '+quoted('Cannot access private constant Ns234Private\\Vault234::A')+' z_denied',
                'S_taken.EVENTS = S_denied.EVENTS','S_taken.CLASSCONSTANTCACHE = S_denied.CLASSCONSTANTCACHE',
                'S_taken.CLASSCONSTANTHISTORY = S_denied.CLASSCONSTANTHISTORY',
                v+' = $ccn_pause(S_denied,1,30000)']
        else: checks += [v+' = $ccn_pause('+w+',1,30000)']
        checks += ['$ccn_ready('+v+',1)',v+'.CURRENT = ('+ctx+')',
            '$class_constant_notice_valid('+v+','+desc+'.ORIGIN,'+owner+',$ptascii("'+member+'"),'+line+')',
            '$class_constant_visible('+v+','+desc+')',
            '$class_constant_notice_protected('+v+','+desc+'.ORIGIN)',
            '$call_descriptors_valid('+v+')']
        if index==1:
            checks += ['S_now = $resolve_at(S_resume1,VARIABLE $ptascii("member234") z_variable,z)',
                'S_now.RESULT = KNOWN pvalue_now','$string_bytes(pvalue_now) = ($ptascii("B"))']
        if index<3:
            checks += ['~$class_constant_notice_valid('+v+'[.RESULT = KNOWN (PSTRING $ptascii("B"))],pclassconstantdesc_b.ORIGIN,'+owner+',$ptascii("B"),'+line+')']
        checks += ['S_result_one'+str(index)+' = $drive_steps('+v+',1)',
            'S_result_one'+str(index)+'.COMPLETION = BUDGET',a+' = S_result_one'+str(index)+'[.COMPLETION = NORMAL]',
            a+'.RESULT = KNOWN (PINT '+str(value)+')',a+'.EVENTS = '+v+'.EVENTS',
            a+'.CLASSCONSTANTCACHE = eps',a+'.CLASSCONSTANTHISTORY = '+v+'.CLASSCONSTANTHISTORY',
            '~$class_constant_notice_protected('+a+','+desc+'.ORIGIN)']
    checks += ['S_done = $drive_steps(S_value3,30000)','S_done.COMPLETION = NORMAL',
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
    (out/'protocol.watsup').write_text(PREFIX+SELECTED+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- '+(c if c.startswith('PhpStep:') else 'if '+c)+'\n' for c in checks))
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
