#!/usr/bin/env python3
"""Check actual current This class across constant member phases."""
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
SOURCE=ROOT/'tests/semantics/deprecated_this_class_constant/actual-child.php'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quoted=lambda s:'$base64('+json.dumps(base64.b64encode(s.encode()).decode())+')'
SELECTED=FETCH_SELECTED+r'''
dec $this_notice_ready(pstate) : bool
def $this_notice_ready(S) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin ptbytes_class ptbytes_member z
def $this_notice_ready(S) = false -- otherwise
dec $this_rvalue_ready(pstate) : bool
def $this_rvalue_ready(S) = true
  -- if S.TODO = (CLASS_CONST_MEMBER expression_this poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES,porigin) = (NExprClassConstFetch expression_this (NExprFuncCall name (SEQUENCE eps) metadata_call) metadata)
  -- if poperand = KNOWN (PSTRING ptbytes_class)
  -- if $class_constant_this_selector(S,porigin,ptbytes_class)
def $this_rvalue_ready(S) = false -- otherwise
dec $this_rvalue_pause(pstate,nat) : pstate
def $this_rvalue_pause(S,n) = S -- if $this_rvalue_ready(S)
def $this_rvalue_pause(S,n) = $this_rvalue_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$this_rvalue_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $this_rvalue_pause(S,n) = S -- otherwise
'''


def fields(fixture):
    expected=json.loads((SOURCE.parent/'cases.json').read_text())['actual-child']['stdout']
    child=quoted('Ns237This\\Child237');base=quoted('Ns237This\\Base237')
    checks=['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(SOURCE)).decode())+')',
        'S_warn1 = $ccn_pause(S_start[.COMPLETION = NORMAL],0,30000)','$this_notice_ready(S_warn1)',
        '$class_named(S_warn1.CLASSNAMES,$ptlc('+child+')) = (porigin_child)',
        '$class_named(S_warn1.CLASSNAMES,$ptlc('+base+')) = (porigin_base)',
        '$class_constant_lookup(S_warn1,porigin_child,$ptascii("A"),|S_warn1.CLASSES|) = (pclassconstantdesc_child_a)',
        '$class_constant_lookup(S_warn1,porigin_child,$ptascii("B"),|S_warn1.CLASSES|) = (pclassconstantdesc_child_b)',
        '$class_constant_lookup(S_warn1,porigin_base,$ptascii("A"),|S_warn1.CLASSES|) = (pclassconstantdesc_base_a)',
        'pclassconstantdesc_child_a.ORIGIN =/= pclassconstantdesc_base_a.ORIGIN']
    previous=None
    for i,(member,value,mode,prefix) in enumerate([
        ('A',9,'literal','L|'),('A',9,'pool','L|H|9|P|'),
        ('A',9,'cv','L|H|9|P|H|9|V|'),('B',10,'rvalue','L|H|9|P|H|9|V|H|9|R|M|'),
        ('A',7,'self','L|H|9|P|H|9|V|H|9|R|M|H|10|S|')],1):
        w=f'S_warn{i}';r=f'S_resume{i}';v=f'S_value{i}';ctx=f'pcallcontext_{i}';site=f'porigin_site{i}';desc=f'pclassconstantdesc_{i}';line=f'z_{i}';fn=f'pfunction_{i}';path=f'pcpath_{i}';requested=base if mode=='self' else child
        if mode=='rvalue':
            checks += ['S_pair = $this_rvalue_pause(S_value3,30000)','$this_rvalue_ready(S_pair)',
                'S_pair.TODO = (CLASS_CONST_MEMBER expression_this_pair (KNOWN (PSTRING '+child+')) z_pair) :: (CLASS_CONST_CAPTURE porigin_pair (KNOWN (PSTRING '+child+')) z_pair) :: ptask_pair_tail*',
                'S_pair.RESULT = KNOWN pvalue_pair','$string_bytes(pvalue_pair) = ($ptascii("B"))',
                '$class_constant_this_rvalue_entry(S_pair,S_pair.RESULT,expression_this_pair,KNOWN (PSTRING '+child+'),z_pair,ptask_pair_tail*) = (pclassconstantdesc_child_b)',
                '$class_constant_this_rvalue_entry(S_pair,REFERENCE 0,expression_this_pair,KNOWN (PSTRING '+child+'),z_pair,ptask_pair_tail*) = eps',
                '$class_constant_this_rvalue_entry(S_pair,KNOWN PNULL,expression_this_pair,KNOWN (PSTRING '+child+'),z_pair,ptask_pair_tail*) = eps',
                '~$class_constant_notice_valid(S_pair,pclassconstantdesc_child_b.ORIGIN,'+child+',$ptascii("B"),z_pair)',
                'S_pair_step = $drive_steps(S_pair,1)','S_pair_step.COMPLETION = BUDGET',w+' = S_pair_step[.COMPLETION = NORMAL]']
        elif previous is not None:checks += [w+' = $ccn_pause('+previous+',0,30000)','$this_notice_ready('+w+')']
        checks += [w+'.TODO = (ERROR_HANDLER_INVOKE perrorcall_'+str(i)+') :: ptask_warn'+str(i)+'*',
            'perrorcall_'+str(i)+'.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl'+str(i)+' '+requested+' $ptascii("'+member+'") '+line,
            '$class_constant_origin('+w+'.CLASSES,porigin_decl'+str(i)+') = ('+desc+')',desc+'.FOLDED',
            w+'.ORIGIN = ('+site+')',site+' = PORIGIN n_unit_'+str(i)+' '+path,
            w+'.CURRENT = ('+ctx+')',ctx+'.RECEIVER = (n_receiver_'+str(i)+')',
            w+'.OBJECTS[n_receiver_'+str(i)+'] = INSTANCE porigin_child',
            '(HOBJECT n_receiver_'+str(i)+') <- '+w+'.ALLOCATIONS',ctx+'.LEXICAL_CLASS = (porigin_base)',
            '$target_function('+w+','+ctx+'.TARGET) = ('+fn+')',
            '$class_constant_keyword_method('+w+','+site+')',
            '$class_constant_notice_valid('+w+','+desc+'.ORIGIN,'+requested+',$ptascii("'+member+'"),'+line+')',
            '$error_call_valid('+w+',perrorcall_'+str(i)+')','$call_descriptors_valid('+w+')',
            '$ccn_output('+w+'.EVENTS) = '+quoted(prefix)]
        if mode!='self':
            checks += ['$origin_node('+w+'.SOURCES,'+site+') = (NExprClassConstFetch (NExprVariable (BYTES text_this'+str(i)+') metadata_this'+str(i)+') phpType20_member'+str(i)+' metadata_fetch'+str(i)+')',
                '$direct_this(BYTES text_this'+str(i)+')',
                '$class_constant_this_selector('+w+','+site+','+child+')',
                '~$class_constant_this_selector('+w+','+site+','+base+')',
                '~$class_constant_this_selector('+w+'[.CURRENT = eps],'+site+','+child+')',
                '~$class_constant_this_selector('+w+'[.ALLOCATIONS = eps],'+site+','+child+')']
        if mode=='literal':
            checks += ['phpType20_member1 = NIdentifier (BYTES text_a) metadata_a','$base64(text_a) = $ptascii("A")',
                '~$class_constant_notice_valid('+w+',pclassconstantdesc_base_a.ORIGIN,'+base+',$ptascii("A"),'+line+')',
                '$task_nodes(perrorcall_1.RESUME) = eps']
        if mode=='pool':
            checks += ['phpType20_member2 = expression_member2',
                '$code_expression('+fn+'.CODE.EXPRESSIONS,'+path+' ++ [PCFIELD 1]) = ((z_member2,true))',
                '$compiled_read('+w+',PORIGIN n_unit_2 ('+path+' ++ [PCFIELD 1])) = (PSTRING $ptascii("A"))',
                '$class_constant_notice_valid('+w+'[.RESULT = KNOWN (PSTRING $ptascii("B"))],'+desc+'.ORIGIN,'+child+',$ptascii("A"),'+line+')',
                '~$class_constant_notice_valid('+w+'[.RESULT = KNOWN (PSTRING $ptascii("B"))],pclassconstantdesc_child_b.ORIGIN,'+child+',$ptascii("B"),'+line+')']
        if mode=='cv':
            checks += ['phpType20_member3 = NExprVariable (BYTES text_member3) metadata_member3',
                '$base64(text_member3) = $ptascii("member237")']
        if mode=='rvalue':
            checks += ['phpType20_member4 = expression_member4',
                '$code_expression('+fn+'.CODE.EXPRESSIONS,'+path+' ++ [PCFIELD 1]) = ((z_member4,false))',
                '$class_constant_this_rvalue_source('+w+','+desc+'.ORIGIN,'+child+',$ptascii("B"),'+line+')']
        if mode=='self':checks += [desc+'.ORIGIN = pclassconstantdesc_base_a.ORIGIN',
            '~$class_constant_this_selector('+w+','+site+','+base+')']
        checks += [r+' = $ccn_pause('+w+',1,30000)','$ccn_ready('+r+',1)',r+'.CURRENT = ('+ctx+')',
            '$class_constant_notice_valid('+r+','+desc+'.ORIGIN,'+requested+',$ptascii("'+member+'"),'+line+')']
        if mode=='cv':checks += ['S_cv_now = $resolve_at('+r+',VARIABLE $ptascii("member237") '+line+','+line+')',
            'S_cv_now.RESULT = KNOWN pvalue_now','$string_bytes(pvalue_now) = ($ptascii("B"))',
            '~$class_constant_notice_valid('+r+'[.RESULT = KNOWN (PSTRING $ptascii("B"))],pclassconstantdesc_child_b.ORIGIN,'+child+',$ptascii("B"),'+line+')']
        checks += ['S_step'+str(i)+' = $drive_steps('+r+',1)','S_step'+str(i)+'.COMPLETION = BUDGET',
            v+' = S_step'+str(i)+'[.COMPLETION = NORMAL]',v+'.RESULT = KNOWN (PINT '+str(value)+')',
            v+'.EVENTS = '+r+'.EVENTS',v+'.CLASSCONSTANTCACHE = eps',
            v+'.CLASSCONSTANTHISTORY = '+r+'.CLASSCONSTANTHISTORY',
            '~$class_constant_notice_protected('+v+','+desc+'.ORIGIN)']
        previous=v
    checks += ['S_done = $drive_steps(S_value5,30000)','S_done.COMPLETION = NORMAL',
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
