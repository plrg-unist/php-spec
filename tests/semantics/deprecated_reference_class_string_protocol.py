#!/usr/bin/env python3
"""Check local reference class-string acquisition and retirement before notices."""
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
SOURCE=ROOT/'tests/semantics/deprecated_reference_class_string/local-class-selector.php'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quoted=lambda s:'$base64('+json.dumps(base64.b64encode(s.encode()).decode())+')'
SELECTED=FETCH_SELECTED+r'''
dec $reference_ready(pstate,nat) : bool
def $reference_ready(S,0) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class (NIdentifier phpType33 metadata_member) z) :: ptask*
  -- if S.RESULT = REFERENCE n_reference
def $reference_ready(S,1) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask*
  -- if S.RESULT = REFERENCE n_reference
def $reference_ready(S,2) = true
  -- if S.TODO = (AT porigin_member (EVAL expression_member)) :: (CLASS_CONST_MEMBER expression_class poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: (CLASS_CONST_STRING_CAPTURE porigin ptbytes_class z) :: ptask*
def $reference_ready(S,3) = true
  -- if S.TODO = (CLASS_CONST_MEMBER expression_class poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: (CLASS_CONST_STRING_CAPTURE porigin ptbytes_class z) :: ptask*
def $reference_ready(S,n) = false -- otherwise
dec $reference_pause(pstate,nat,nat) : pstate
def $reference_pause(S,n_phase,n_budget) = S -- if $reference_ready(S,n_phase)
def $reference_pause(S,n_phase,n_budget) = $reference_pause(S_next[.COMPLETION = NORMAL],n_phase,$nabs($(n_budget - 1)))
  -- if ~$reference_ready(S,n_phase)
  -- if S.COMPLETION = NORMAL /\ $(n_budget > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $reference_pause(S,n_phase,n_budget) = S -- otherwise
'''


def fields(fixture):
    expected=json.loads((SOURCE.parent/'cases.json').read_text())['local-class-selector']['stdout']
    child=quoted('Ns240Ref\\Child240');base=quoted('Ns240Ref\\Base240')
    checks=['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(SOURCE)).decode())+')']
    previous='S_start[.COMPLETION = NORMAL]'
    for i,(phase,prefix,warnprefix) in enumerate([(0,'L|C|','L|C|'),(1,'L|C|H|9|R|C|','L|C|H|9|R|C|M|')],1):
        raw=f'S_raw{i}';cl=f'S_class{i}';w=f'S_warn{i}';r=f'S_resume{i}';v=f'S_value{i}';n=f'n_reference{i}';fn=f'expression_class{i}';m=f'phpType20_member{i}';z=f'z_{i}';tail=f'ptask_tail{i}*';site=f'porigin_site{i}';desc=f'pclassconstantdesc_{i}';ctx=f'pclassdesc_{i}';payload=f'pvalue_payload{i}'
        checks += [raw+' = $reference_pause('+previous+','+str(phase)+',30000)','$reference_ready('+raw+','+str(phase)+')',
            raw+'.TODO = (CLASS_CONST_CLASS '+fn+' '+m+' '+z+') :: '+tail,
            raw+'.ORIGIN = ('+site+')',raw+'.RESULT = REFERENCE '+n,
            raw+'.CURRENT = eps',raw+'.FRAMES = eps',raw+'.HELD = eps',
            '$call_reference_operand_valid('+raw+',REFERENCE '+n+')',
            '('+n+' <- '+raw+'.REFCELLS)','(HCELL '+n+') <- '+raw+'.ALLOCATIONS',
            raw+'.STORE['+n+'] = DEFINED '+payload,'$string_bytes('+payload+') = ('+child+')',
            '$constant_value_class_valid('+raw+','+payload+',PVSTRING false)','$value_nodes('+payload+') = eps',
            '$heap_owners($heap_graph('+raw+'),HCELL '+n+') = 1',
            '$machine_base_roots('+raw+') = eps','$call_descriptors_valid('+raw+')',
            '$ccn_output('+raw+'.EVENTS) = '+quoted(prefix),
            cl+' = $class_constant_selector('+raw+','+fn+','+z+')',cl+'.COMPLETION = NORMAL',
            cl+'.RESULT = KNOWN (PSTRING '+child+')',
            '$heap_owners($heap_graph('+cl+'),HCELL '+n+') = 0',
            '(HCELL '+n+') <- $eager_slots('+raw+','+cl+')',
            '$class_constant_reference_selector('+cl+',REFERENCE '+n+') = ('+ctx+')',ctx+'.NAME = '+child,
            '$class_constant_reference_selector('+cl+',KNOWN '+payload+') = eps',
            '$class_constant_reference_selector('+cl+'[.ALLOCATIONS = eps],REFERENCE '+n+') = eps',
            '$class_constant_reference_selector('+cl+'[.REFCELLS = eps],REFERENCE '+n+') = eps',
            '$class_constant_reference_selector('+cl+'[.STORE = $set_cell('+cl+'.STORE,'+n+',UNDEFINED)],REFERENCE '+n+') = eps',
            '$class_constant_reference_selector('+cl+'[.STORE = $set_cell('+cl+'.STORE,'+n+',DEFINED PNULL)],REFERENCE '+n+') = eps',
            '$class_constant_reference_selector('+cl+'[.RESULT = KNOWN (PSTRING '+base+')],REFERENCE '+n+') = eps',
            '$class_constant_lookup('+cl+','+ctx+'.ORIGIN,$ptascii("A"),|'+cl+'.CLASSES|) = ('+desc+')']
        if phase==0:
            checks += ['$class_constant_reference_literal_entry('+cl+',REFERENCE '+n+','+fn+','+m+','+z+','+tail+') = ('+desc+')',
                '$class_constant_rvalue_class_entry('+cl+',REFERENCE '+n+','+fn+','+m+','+z+','+tail+') = eps',
                '$class_constant_reference_literal_entry('+cl+',KNOWN '+payload+','+fn+','+m+','+z+','+tail+') = eps',
                '$class_constant_reference_literal_entry('+cl+'[.HELD = [HCELL '+n+']],REFERENCE '+n+','+fn+','+m+','+z+','+tail+') = eps',
                '$class_constant_reference_literal_entry('+cl+'[.BASE = BASE_VALUE (REFERENCE '+n+')],REFERENCE '+n+','+fn+','+m+','+z+','+tail+') = eps']
        else:
            checks += ['$class_constant_reference_capture_entry('+cl+',REFERENCE '+n+','+fn+','+m+','+z+','+tail+')',
                '~$class_constant_string_class_entry('+cl+',REFERENCE '+n+','+fn+','+m+','+z+','+tail+')',
                '~$class_constant_reference_capture_entry('+cl+',KNOWN '+payload+','+fn+','+m+','+z+','+tail+')',
                '~$class_constant_reference_capture_entry('+cl+'[.HELD = [HCELL '+n+']],REFERENCE '+n+','+fn+','+m+','+z+','+tail+')',
                '~$class_constant_reference_capture_entry('+cl+'[.BASE = BASE_VALUE (REFERENCE '+n+')],REFERENCE '+n+','+fn+','+m+','+z+','+tail+')',
                'S_member = $reference_pause('+raw+',2,30000)','$reference_ready(S_member,2)',
                '$ccn_output(S_member.EVENTS) = '+quoted(prefix),
                '~((HCELL '+n+') <- S_member.ALLOCATIONS)',
                '$heap_owners($heap_graph(S_member),HCELL '+n+') = 0',
                '$task_nodes(CLASS_CONST_STRING_CAPTURE '+site+' '+child+' '+z+') = eps',
                '$class_constant_string_capture_source(S_member,'+site+','+child+','+z+')',
                'S_pair = $reference_pause(S_member,3,30000)','$reference_ready(S_pair,3)',
                'S_pair.TODO = (CLASS_CONST_MEMBER '+fn+' (KNOWN (PSTRING '+child+')) '+z+') :: (CLASS_CONST_CAPTURE '+site+' (KNOWN (PSTRING '+child+')) '+z+') :: (CLASS_CONST_STRING_CAPTURE '+site+' '+child+' '+z+') :: '+tail,
                'S_pair.RESULT = KNOWN pvalue_member','$string_bytes(pvalue_member) = ($ptascii("A"))',
                '$class_constant_string_member_entry(S_pair,S_pair.RESULT,'+fn+',KNOWN (PSTRING '+child+'),'+z+','+tail+') = ('+desc+')',
                '$ccn_output(S_pair.EVENTS) = '+quoted(warnprefix)]
        checks += [w+' = $ccn_pause('+(raw if phase==0 else 'S_pair')+',0,30000)','$ccn_ready('+w+',0)',
            w+'.TODO = (ERROR_HANDLER_INVOKE perrorcall_'+str(i)+') :: ptask_warn'+str(i)+'*',
            'perrorcall_'+str(i)+'.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT '+desc+'.ORIGIN '+child+' $ptascii("A") '+z,
            '$ccn_output('+w+'.EVENTS) = '+quoted(warnprefix),
            '~((HCELL '+n+') <- '+w+'.ALLOCATIONS)',
            '$heap_owners($heap_graph('+w+'),HCELL '+n+') = 0',
            '~$call_reference_operand_valid('+w+',REFERENCE '+n+')',
            '$class_constant_reference_selector('+w+'[.RESULT = KNOWN (PSTRING '+child+')],REFERENCE '+n+') = eps',
            'S_stale'+str(i)+' = '+w+'[.REFCELLS = '+cl+'.REFCELLS][.STORE = '+cl+'.STORE][.RESULT = KNOWN (PSTRING '+child+')]',
            '$class_constant_reference_selector(S_stale'+str(i)+',REFERENCE '+n+') = eps',
            '$class_constant_notice_valid('+w+','+desc+'.ORIGIN,'+child+',$ptascii("A"),'+z+')',
            '$task_nodes(perrorcall_'+str(i)+'.RESUME) = eps','$error_call_valid('+w+',perrorcall_'+str(i)+')','$call_descriptors_valid('+w+')',
            r+' = $ccn_pause('+w+',1,30000)','$ccn_ready('+r+',1)',
            '$class_constant_notice_valid('+r+','+desc+'.ORIGIN,'+child+',$ptascii("A"),'+z+')',
            'S_step'+str(i)+' = $drive_steps('+r+',1)','S_step'+str(i)+'.COMPLETION = BUDGET',
            v+' = S_step'+str(i)+'[.COMPLETION = NORMAL]',v+'.RESULT = KNOWN (PINT 9)',
            v+'.EVENTS = '+r+'.EVENTS',v+'.CLASSCONSTANTCACHE = eps',v+'.CLASSCONSTANTHISTORY = '+r+'.CLASSCONSTANTHISTORY',
            '~$class_constant_notice_protected('+v+','+desc+'.ORIGIN)']
        previous=v
    checks += ['S_done = $drive_steps(S_value2,30000)','S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = '+quoted(expected),'$class_constant_state_valid(S_done)','$call_descriptors_valid(S_done)']
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
