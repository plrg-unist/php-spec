#!/usr/bin/env python3
"""Check physical field order and repeated child edges across constant selection."""
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
SOURCE=ROOT/'tests/semantics/deprecated_reference_object_fields'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quoted=lambda s:'$base64('+json.dumps(base64.b64encode(s.encode()).decode())+')'
SELECTED=FETCH_SELECTED+r''' 
dec $reference_fields_ready(pstate,nat,ptbytes) : bool
def $reference_fields_ready(S,0,ptbytes) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask*
  -- if S.RESULT = REFERENCE n_reference
def $reference_fields_ready(S,1,ptbytes) = true
  -- if $ccn_output(S.EVENTS) = ptbytes
  -- if S.CURRENT = (pcallcontext)
def $reference_fields_ready(S,2,ptbytes) = true
  -- if S.TODO = (CLASS_CONST_MEMBER expression_class poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: (CLASS_CONST_OBJECT_CAPTURE porigin ptbytes_class z) :: ptask*
def $reference_fields_ready(S,n_phase,ptbytes) = false -- otherwise
dec $reference_fields_pause(pstate,nat,ptbytes,nat) : pstate
def $reference_fields_pause(S,n_phase,ptbytes,n_budget) = S -- if $reference_fields_ready(S,n_phase,ptbytes)
def $reference_fields_pause(S,n_phase,ptbytes,n_budget) = $reference_fields_pause(S_next[.COMPLETION = NORMAL],n_phase,ptbytes,$nabs($(n_budget - 1)))
  -- if ~$reference_fields_ready(S,n_phase,ptbytes)
  -- if S.COMPLETION = NORMAL /\ $(n_budget > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $reference_fields_pause(S,n_phase,ptbytes,n_budget) = S -- otherwise
'''


def fields(fixture,name,path):
    import re
    shared=name=='shared-child-once'
    child=quoted(('Ns243SharedChild' if shared else 'Ns243FieldOrder')+'\\Child243')
    member='B' if shared else 'C';value=10 if shared else 11
    midprefix='B|C|D|H|9|T0|' if shared else 'B|C|D|H|9|L|R|'
    pairprefix='B|C|D|H|9|T0|S|M|' if shared else 'B|C|D|H|9|L|R|M|'
    expected=json.loads((SOURCE/'cases.json').read_text())[name]['stdout']
    checks=['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(path)).decode())+')',
        'S_raw = $reference_fields_pause(S_start[.COMPLETION = NORMAL],0,eps,30000)',
        '$reference_fields_ready(S_raw,0,eps)',
        'S_raw.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask_tail*',
        'S_raw.RESULT = REFERENCE n_reference','S_raw.ORIGIN = (porigin_site)',
        'S_raw.CURRENT = eps','S_raw.FRAMES = eps','S_raw.HELD = eps',
        '$call_reference_operand_valid(S_raw,REFERENCE n_reference)',
        'S_raw.STORE[n_reference] = DEFINED (POBJECT n_owner)',
        '(HOBJECT n_owner) <- S_raw.ALLOCATIONS','S_raw.OBJECTS[n_owner] = INSTANCE porigin_owner',
        '$class_at(S_raw.CLASSES,porigin_owner) = (pclassdesc_owner)','pclassdesc_owner.NAME = '+child,
        '$objectprops_at(S_raw.OBJECTPROPS,n_owner) = (ppropertyslot*)',
        '$class_constant_reference_object_fields(S_raw,n_owner,ppropertyslot*)',
        '$heap_owners($heap_graph(S_raw),HCELL n_reference) = 1',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_owner) = 1',
        '$call_descriptors_valid(S_raw)','$ccn_output(S_raw.EVENTS) = $ptascii("B|C|")']
    if shared:
        checks += ['ppropertyslot* = [ppropertyslot_head,ppropertyslot_middle,ppropertyslot_tail]',
            'ppropertyslot_head.STATE = PROP_VALUE (DIRECT (POBJECT n_shared))',
            'ppropertyslot_tail.STATE = PROP_VALUE (DIRECT (POBJECT n_shared))',
            'ppropertyslot_middle.STATE = PROP_VALUE (DIRECT (POBJECT n_middle))','n_shared =/= n_middle',
            '$heap_owners($heap_graph(S_raw),HOBJECT n_shared) = 2',
            '$heap_owners($heap_graph(S_raw),HOBJECT n_middle) = 1']
        running='n_middle';gone='n_shared'
    else:
        checks += ['ppropertyslot* = [ppropertyslot_head,ppropertyslot_tag,ppropertyslot_empty,ppropertyslot_tail]',
            'ppropertyslot_head.STATE = PROP_VALUE (DIRECT (POBJECT n_left))',
            'ppropertyslot_tail.STATE = PROP_VALUE (DIRECT (POBJECT n_right))',
            'ppropertyslot_tag.STATE = PROP_VALUE (DIRECT (PINT 0))',
            'ppropertyslot_empty.STATE = PROP_VALUE (DIRECT PNULL)','$(n_right < n_left)',
            '$heap_owners($heap_graph(S_raw),HOBJECT n_left) = 1',
            '$heap_owners($heap_graph(S_raw),HOBJECT n_right) = 1']
        running='n_right';gone='n_left'
    checks += ['$property_slot_descriptor(S_raw,n_owner,ppropertyslot_head) = (ppropertydesc_head)',
        '$property_slot_descriptor(S_raw,n_owner,ppropertyslot_tail) = (ppropertydesc_tail)',
        'ppropertydesc_head.KEY = $ptascii("head")','ppropertydesc_tail.KEY = $ptascii("tail")',
        'pclassdesc_owner.PROPERTIES = [ppropertydesc_tail]',
        'S_class = $class_constant_selector(S_raw,expression_class,z)','S_class.COMPLETION = NORMAL',
        'S_class.RESULT = KNOWN (PSTRING '+child+')',
        '$heap_owners($heap_graph(S_class),HCELL n_reference) = 0',
        '$heap_owners($heap_graph(S_class),HOBJECT n_owner) = 1',
        '$class_constant_reference_object_selector(S_class,S_raw.RESULT) = (pclassdesc_owner)',
        '$class_constant_reference_object_capture_entry(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        '~$class_constant_object_class_entry(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        '~$class_constant_reference_capture_entry(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        '$class_constant_reference_object_selector(S_class,KNOWN (POBJECT n_owner)) = eps',
        '$class_constant_reference_object_selector(S_class[.RESULT = KNOWN PNULL],S_raw.RESULT) = eps',
        '~$class_constant_reference_object_capture_entry(S_class[.HELD = [HCELL n_reference]],S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        '~$class_constant_reference_object_capture_entry(S_class[.BASE = BASE_VALUE (REFERENCE n_reference)],S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        'ppropertyslot* = ppropertyslot_first :: ppropertyslot_rest*',
        'ppropertyslot_alias* = (ppropertyslot_first[.STATE = PROP_VALUE (ALIAS n_reference)]) :: ppropertyslot_rest*',
        '~$class_constant_reference_object_fields(S_class,n_owner,ppropertyslot_alias*)',
        'ppropertyslot_string* = (ppropertyslot_first[.STATE = PROP_VALUE (DIRECT (PSTRING $ptascii("x")))]) :: ppropertyslot_rest*',
        '~$class_constant_reference_object_fields(S_class,n_owner,ppropertyslot_string*)',
        '~$class_constant_reference_object_field_value(S_class,n_owner,PSTRING $ptascii("x"))',
        '~$class_constant_reference_object_field_value(S_class,n_owner,PARRAY 0)',
        '~$class_constant_reference_object_field_value(S_class,n_owner,POBJECT n_owner)',
        '$class_constant_lookup(S_class,porigin_owner,$ptascii("'+member+'"),|S_class.CLASSES|) = (pclassconstantdesc)',
        'S_neutral = $class_constant_class_forward(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        'ptask_marker = CLASS_CONST_OBJECT_CAPTURE porigin_site '+child+' z',
        'ptask_member = $at_task($origin_child((porigin_site),[PCFIELD 1]),EVAL expression_member)',
        'S_neutral.TODO = ptask_member :: (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING '+child+')) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING '+child+')) z) :: ptask_marker :: ptask_tail*',
        'S_neutral.OBJECTPROPS = S_class.OBJECTPROPS','S_neutral.OBJECTS = S_class.OBJECTS',
        'S_neutral.STORE = S_class.STORE','S_neutral.ALLOCATIONS = S_class.ALLOCATIONS',
        'S_neutral.RESULT = KNOWN PNULL','S_neutral.BASE = BASE_VALUE (KNOWN PNULL)',
        '$task_nodes(ptask_marker) = eps','$eager_slots(S_raw,S_neutral) = [HCELL n_reference]',
        '$eager_operation_source(S_raw,CLASS_CONST_CLASS expression_class expression_member z) = ptask_marker',
        'S_step = $drive_steps(S_raw,1)','S_step.COMPLETION = BUDGET','S_release = S_step[.COMPLETION = NORMAL]',
        'S_release.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
        'pdestructionoperation.SOURCE = ptask_marker','pdestructionoperation.VALUE = KNOWN PNULL',
        'pdestructionoperation.BASE = BASE_VALUE (KNOWN PNULL)','pdestructionoperation.COMPLETION = NORMAL',
        'pdestructionoperation.PENDING = eps','$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
        '$eager_operation_source_guard(S_release,pdestructionoperation)','$call_descriptors_valid(S_release)',
        'S_mid = $reference_fields_pause(S_release,1,'+quoted(midprefix)+',30000)',
        '$reference_fields_ready(S_mid,1,'+quoted(midprefix)+')',
        'S_mid.CURRENT = (pcallcontext_mid)','pcallcontext_mid.RECEIVER = ('+running+')',
        '(HOBJECT '+running+') <- S_mid.ALLOCATIONS',
        '$($heap_owners($heap_graph(S_mid),HOBJECT '+running+') > 0)',
        '$instance_storage_for(S_mid,n_owner) = (pinstancestorage_mid)','pinstancestorage_mid.OBJECT = n_owner',
        '$call_descriptors_valid(S_mid)',
        '$eager_operation_source_guard(S_mid,pdestructionoperation)']
    if shared:
        checks += ['(HOBJECT n_shared) <- S_mid.ALLOCATIONS',
            '$heap_owners($heap_graph(S_mid),HOBJECT n_shared) = 1',
            '~(n_shared <- S_mid.DESTRUCTION.CALLED)','n_middle <- S_mid.DESTRUCTION.CALLED',
            'S_global_mid = $global_table_view(S_mid)',
            '$lookup(S_global_mid.ENV,$ptascii("released243")) = (n_released)',
            'S_global_mid.STORE[n_released] = DEFINED (PBOOL false)']
    else:
        checks += ['~((HOBJECT n_left) <- S_mid.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_mid),HOBJECT n_left) = 0',
            'n_left <- S_mid.DESTRUCTION.CALLED','n_right <- S_mid.DESTRUCTION.CALLED']
    checks += ['S_pair = $reference_fields_pause(S_mid,2,eps,30000)','$reference_fields_ready(S_pair,2,eps)',
        'S_pair.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING '+child+')) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING '+child+')) z) :: ptask_marker :: ptask_tail*',
        'S_pair.RESULT = KNOWN pvalue_member','$string_bytes(pvalue_member) = ($ptascii("'+member+'"))',
        '$ccn_output(S_pair.EVENTS) = '+quoted(pairprefix),
        '~((HCELL n_reference) <- S_pair.ALLOCATIONS)','~((HOBJECT n_owner) <- S_pair.ALLOCATIONS)',
        '~((HOBJECT '+running+') <- S_pair.ALLOCATIONS)','~((HOBJECT '+gone+') <- S_pair.ALLOCATIONS)',
        'S_pair.DESTRUCTION.OPERATIONS = eps',
        '$class_constant_object_member_entry(S_pair,S_pair.RESULT,expression_class,KNOWN (PSTRING '+child+'),z,ptask_tail*) = (pclassconstantdesc)',
        'S_warn = $ccn_pause(S_pair,0,30000)','$ccn_ready(S_warn,0)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN '+child+' $ptascii("'+member+'") z',
        '$task_nodes(perrorcall.RESUME) = eps','$error_call_valid(S_warn,perrorcall)',
        'S_resume = $ccn_pause(S_warn,1,30000)','$ccn_ready(S_resume,1)',
        '$ccn_output(S_resume.EVENTS) = '+quoted(pairprefix+'H|'),
        'S_global_resume = $global_table_view(S_resume)',
        '$lookup(S_global_resume.ENV,$ptascii("member243")) = (n_member)',
        'S_global_resume.STORE[n_member] = DEFINED pvalue_now','$string_bytes(pvalue_now) = ($ptascii("A"))',
        '$class_constant_notice_valid(S_resume,pclassconstantdesc.ORIGIN,'+child+',$ptascii("'+member+'"),z)',
        'S_value_step = $drive_steps(S_resume,1)','S_value_step.COMPLETION = BUDGET',
        'S_value = S_value_step[.COMPLETION = NORMAL]','S_value.RESULT = KNOWN (PINT '+str(value)+')',
        'S_value.EVENTS = S_resume.EVENTS','~$class_constant_notice_protected(S_value,pclassconstantdesc.ORIGIN)',
        'S_done = $drive_steps(S_value,30000)','S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = '+quoted(expected),
        'S_done.CLASSCONSTANTCACHE = eps','S_done.CLASSCONSTANTHISTORY = S_raw.CLASSCONSTANTHISTORY',
        '$class_constant_state_valid(S_done)','$call_descriptors_valid(S_done)']
    if shared:
        checks += ['S_done_global = $global_table_view(S_done)',
            'S_done_global.STORE[n_released] = DEFINED (PBOOL true)',
            'S_zero = $drive_steps(S_mid,0)','S_zero.COMPLETION = BUDGET','S_zero[.COMPLETION = NORMAL] = S_mid',
            'S_one = $drive_steps(S_mid,1)','S_one.COMPLETION = BUDGET',
            '$drive_steps(S_zero[.COMPLETION = NORMAL],30000) = S_done',
            '$drive_steps(S_one[.COMPLETION = NORMAL],30000) = S_done']
    pattern=r'\b(U|S_[A-Za-z0-9_]+|n_[A-Za-z0-9_]+|porigin_[A-Za-z0-9_]+|expression_[A-Za-z0-9_]+|z|ptask_[A-Za-z0-9_]+|ppropertyslot[A-Za-z0-9_]*|ppropertydesc[A-Za-z0-9_]*|pclassdesc_[A-Za-z0-9_]+|pclassconstantdesc|pdestructionoperation|pcallcontext_mid|pinstancestorage_mid|perrorcall|pvalue_[A-Za-z0-9_]+)\b'
    suffix='_'+name.replace('-','_')
    return [re.sub(pattern,lambda match:match.group()+suffix,check) for check in checks]


def prepare(out):
    frontend=Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],out/'frontend')
    adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],out/'adapter')
    checks=[]
    try:
        for name in ['physical-field-order','shared-child-once']:
            path=SOURCE/(name+'.php')
            parsed=frontend.request({'op':'parse','source':base64.b64encode(path.read_bytes()).decode()});assert parsed['accepted'] and not parsed['diagnostics']
            checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True});assert checked['ok']
            checks += fields(checked['fixture'],name,path)
    finally:
        try:adapter.close()
        finally:frontend.close()
    (out/'assertions.json').write_text(json.dumps(checks,indent=2)+'\n')
    (out/'protocol.watsup').write_text(PREFIX+SELECTED+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+check+'\n' for check in checks))
    return len(checks)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    modules=[ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    paths=[Path(__file__),*(SOURCE/p for p in ['physical-field-order.php','shared-child-once.php','cases.json','hashes.json']),*modules,*(ROOT/p for p in (
        'spec/semantics/modules.json','spec/schema.json','frontend/worker.php',
        'tests/semantics/deprecated_class_constant_fetch_protocol.py',
        'tests/semantics/deprecated_parameter_default_protocol.py','tests/semantics/deprecated_global_constant_protocol.py',
        'tests/semantics/recorded_worker.py','tests/semantics/error_handler_run.py','tests/semantics/static_types.py','tests/semantics/profile.json',
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
