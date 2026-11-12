#!/usr/bin/env python3
"""Check singleton primitive selector fields and rootless acquisition."""
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
SOURCE=ROOT/'tests/semantics/deprecated_reference_object_scalar'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quoted=lambda s:'$base64('+json.dumps(base64.b64encode(s.encode()).decode())+')'
SELECTED=FETCH_SELECTED+r'''
dec $reference_scalar_ready(pstate,nat,nat) : bool
def $reference_scalar_ready(S,0,n_object) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask*
  -- if S.RESULT = REFERENCE n_reference
def $reference_scalar_ready(S,1,n_object) = true
  -- if $ccn_output(S.EVENTS) = $ptascii("B|C|D|N|H|9|")
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n_object)
def $reference_scalar_ready(S,2,n_object) = true
  -- if $instance_storage_for(S,n_object) = (pinstancestorage)
  -- if pinstancestorage.NEXT = 1
def $reference_scalar_ready(S,3,n_object) = true
  -- if S.TODO = (CLASS_CONST_MEMBER expression_class poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: (CLASS_CONST_OBJECT_CAPTURE porigin ptbytes_class z) :: ptask*
def $reference_scalar_ready(S,n_phase,n_object) = false -- otherwise
dec $reference_scalar_pause(pstate,nat,nat,nat) : pstate
def $reference_scalar_pause(S,n_phase,n_object,n_budget) = S -- if $reference_scalar_ready(S,n_phase,n_object)
def $reference_scalar_pause(S,n_phase,n_object,n_budget) = $reference_scalar_pause(S_next[.COMPLETION = NORMAL],n_phase,n_object,$nabs($(n_budget - 1)))
  -- if ~$reference_scalar_ready(S,n_phase,n_object)
  -- if S.COMPLETION = NORMAL /\ $(n_budget > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $reference_scalar_pause(S,n_phase,n_object,n_budget) = S -- otherwise
'''

def scalar(fixture,path):
 child=quoted('Ns245Scalar\\Child245')
 checks=['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(path)).decode())+')',
  'S_raw = $reference_scalar_pause(S_start[.COMPLETION = NORMAL],0,0,30000)','$reference_scalar_ready(S_raw,0,0)',
  'S_raw.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask_tail*',
  'S_raw.ORIGIN = (porigin_site)','S_raw.RESULT = REFERENCE n_reference',
  'S_raw.CURRENT = eps','S_raw.FRAMES = eps','S_raw.HELD = eps',
  '$call_reference_operand_valid(S_raw,S_raw.RESULT)',
  'S_raw.STORE[n_reference] = DEFINED (POBJECT n_object)',
  '(HCELL n_reference) <- S_raw.ALLOCATIONS','(HOBJECT n_object) <- S_raw.ALLOCATIONS',
  'S_raw.OBJECTS[n_object] = INSTANCE porigin_child',
  '$objectprops_at(S_raw.OBJECTPROPS,n_object) = ([ppropertyslot_tag])',
  'ppropertyslot_tag.STATE = PROP_VALUE (DIRECT PNULL)',
  '$property_slot_descriptor(S_raw,n_object,ppropertyslot_tag) = (ppropertydesc_tag)',
  'ppropertydesc_tag.KEY = $ptascii("tag")',
  '$class_at(S_raw.CLASSES,porigin_child) = (pclassdesc_child)',
  'pclassdesc_child.PROPERTIES = eps',
  '$class_constant_reference_object_fields(S_raw,n_object,[ppropertyslot_tag])',
  '$class_constant_reference_object_graph(S_raw,n_object,eps)',
  '$node_children(S_raw,HCELL n_reference) = [HOBJECT n_object]',
  '$node_children(S_raw,HOBJECT n_object) = eps',
  '$heap_owners($heap_graph(S_raw),HCELL n_reference) = 1',
  '$heap_owners($heap_graph(S_raw),HOBJECT n_object) = 1',
  '$machine_base_roots(S_raw) = eps','$call_descriptors_valid(S_raw)',
  '$ccn_output(S_raw.EVENTS) = $ptascii("B|C|")',
  'S_class = $class_constant_selector(S_raw,expression_class,z)','S_class.COMPLETION = NORMAL',
  'S_class.RESULT = KNOWN (PSTRING '+child+')',
  '$heap_owners($heap_graph(S_class),HCELL n_reference) = 0',
  '$heap_owners($heap_graph(S_class),HOBJECT n_object) = 1',
  '$eager_slots(S_raw,S_class) = [HCELL n_reference]',
  '$class_constant_reference_object_selector(S_class,S_raw.RESULT) = (pclassdesc_child)',
  '$class_constant_reference_object_capture_entry(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
  '$class_constant_object_capture_source(S_class,porigin_site,'+child+',z)',
  '$eager_operation_source(S_raw,CLASS_CONST_CLASS expression_class expression_member z) = CLASS_CONST_OBJECT_CAPTURE porigin_site '+child+' z']
 for value in ['PNULL','PBOOL false','PBOOL true','PINT 0','PINT (-17)']:
  checks.append('$class_constant_reference_object_scalar_value('+value+')')
 for value in ['PUNDEFINED','PFLOAT 0','PSTRING $ptascii("x")','PSTRING [0]','PARRAY 0','POBJECT n_object']:
  checks.append('~$class_constant_reference_object_scalar_value('+value+')')
 for name,value in [('bool','PBOOL false'),('int','PINT 17')]:
  view='S_'+name
  checks += [view+' = S_class[.OBJECTPROPS = $objectprops_set(S_class.OBJECTPROPS,n_object,[ppropertyslot_tag[.STATE = PROP_VALUE (DIRECT ('+value+'))]])]',
   '$class_constant_reference_object_fields('+view+',n_object,[ppropertyslot_tag[.STATE = PROP_VALUE (DIRECT ('+value+'))]])',
   '$class_constant_reference_object_graph('+view+',n_object,eps)',
   '$node_children('+view+',HOBJECT n_object) = eps',
   '$class_constant_reference_object_selector('+view+',S_raw.RESULT) = (pclassdesc_child)',
   '$class_constant_reference_object_capture_entry('+view+',S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)']
 for state in ['PROP_INITIAL','PROP_UNSET','PROP_VALUE (ALIAS n_reference)',
               'PROP_VALUE (DIRECT (POBJECT n_object))','PROP_VALUE (DIRECT (PFLOAT 0))',
               'PROP_VALUE (DIRECT (PSTRING $ptascii("x")))','PROP_VALUE (DIRECT (PSTRING [0]))',
               'PROP_VALUE (DIRECT (PARRAY 0))']:
  view='S_class[.OBJECTPROPS = $objectprops_set(S_class.OBJECTPROPS,n_object,[ppropertyslot_tag[.STATE = '+state+']])]'
  checks.append('$class_constant_reference_object_selector('+view+',S_raw.RESULT) = eps')
 checks += [
  'S_duplicate = S_class[.OBJECTPROPS = $objectprops_set(S_class.OBJECTPROPS,n_object,[ppropertyslot_tag,ppropertyslot_tag])]',
  '$class_constant_reference_object_selector(S_duplicate,S_raw.RESULT) = (pclassdesc_child)',
  '~$call_descriptors_valid(S_duplicate)',
  '~$class_constant_reference_object_capture_entry(S_duplicate,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
  '$class_constant_reference_object_selector(S_class[.RESULT = KNOWN PNULL],S_raw.RESULT) = eps',
  '$class_constant_reference_object_selector(S_class,KNOWN (POBJECT n_object)) = eps',
  '~$class_constant_reference_object_capture_entry(S_class[.HELD = [HCELL n_reference]],S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
  '~$class_constant_reference_object_capture_entry(S_class[.BASE = BASE_VALUE (REFERENCE n_reference)],S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
  'S_neutral = $class_constant_class_forward(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
  'ptask_marker = CLASS_CONST_OBJECT_CAPTURE porigin_site '+child+' z',
  'ptask_member = $at_task($origin_child((porigin_site),[PCFIELD 1]),EVAL expression_member)',
  'S_neutral.TODO = ptask_member :: (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING '+child+')) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING '+child+')) z) :: ptask_marker :: ptask_tail*',
  'S_neutral.STORE = S_class.STORE','S_neutral.OBJECTPROPS = S_class.OBJECTPROPS',
  'S_neutral.OBJECTS = S_class.OBJECTS','S_neutral.ALLOCATIONS = S_class.ALLOCATIONS',
  'S_neutral.RESULT = KNOWN PNULL','S_neutral.BASE = BASE_VALUE (KNOWN PNULL)',
  '$task_nodes(ptask_marker) = eps','$machine_base_roots(S_neutral) = eps',
  'S_step = $drive_steps(S_raw,1)','S_step.COMPLETION = BUDGET','S_release = S_step[.COMPLETION = NORMAL]',
  'S_release.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
  'pdestructionoperation.SOURCE = ptask_marker','pdestructionoperation.VALUE = KNOWN PNULL',
  'pdestructionoperation.BASE = BASE_VALUE (KNOWN PNULL)','pdestructionoperation.PENDING = eps',
  '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
  '$eager_operation_source_guard(S_release,pdestructionoperation)','$call_descriptors_valid(S_release)',
  'S_dtor = $reference_scalar_pause(S_release,1,n_object,30000)','$reference_scalar_ready(S_dtor,1,n_object)',
  'S_dtor.CURRENT = (pcallcontext_dtor)','pcallcontext_dtor.RECEIVER = (n_object)',
  '(HOBJECT n_object) <- S_dtor.ALLOCATIONS','$($heap_owners($heap_graph(S_dtor),HOBJECT n_object) > 0)',
  '$node_children(S_dtor,HOBJECT n_object) = eps',
  '$call_descriptors_valid(S_dtor)','$eager_operation_source_guard(S_dtor,pdestructionoperation)',
  'S_storage = $reference_scalar_pause(S_dtor,2,n_object,30000)','$reference_scalar_ready(S_storage,2,n_object)',
  '$instance_storage_for(S_storage,n_object) = (pinstancestorage)','pinstancestorage.NEXT = 1',
  'pinstancestorage.SLOTS = [ppropertyslot_tag]',
  '$objectprops_at(S_storage.OBJECTPROPS,n_object) = ([ppropertyslot_tag[.STATE = PROP_UNSET]])',
  '(HOBJECT n_object) <- S_storage.ALLOCATIONS','$node_children(S_storage,HOBJECT n_object) = eps',
  '$instance_storage_basic(S_storage,pinstancestorage)',
  '$call_descriptors_valid(S_storage)','$eager_operation_source_guard(S_storage,pdestructionoperation)',
  'S_pair = $reference_scalar_pause(S_storage,3,n_object,30000)','$reference_scalar_ready(S_pair,3,n_object)',
  'S_pair.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING '+child+')) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING '+child+')) z) :: ptask_marker :: ptask_tail*',
  'S_pair.RESULT = KNOWN pvalue_member','$string_bytes(pvalue_member) = ($ptascii("B"))',
  '$ccn_output(S_pair.EVENTS) = $ptascii("B|C|D|N|H|9|M|")',
  '~((HCELL n_reference) <- S_pair.ALLOCATIONS)','~((HOBJECT n_object) <- S_pair.ALLOCATIONS)',
  'S_pair.DESTRUCTION.OPERATIONS = eps',
  '$class_constant_object_member_entry(S_pair,S_pair.RESULT,expression_class,KNOWN (PSTRING '+child+'),z,ptask_tail*) = (pclassconstantdesc)',
  'S_warn = $ccn_pause(S_pair,0,30000)','$ccn_ready(S_warn,0)',
  'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
  'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN '+child+' $ptascii("B") z',
  '$task_nodes(perrorcall.RESUME) = eps','$error_call_valid(S_warn,perrorcall)',
  'S_resume = $ccn_pause(S_warn,1,30000)','$ccn_ready(S_resume,1)',
  '$ccn_output(S_resume.EVENTS) = $ptascii("B|C|D|N|H|9|M|H|")',
  'S_global_resume = $global_table_view(S_resume)',
  '$lookup(S_global_resume.ENV,$ptascii("member245")) = (n_member)',
  'S_global_resume.STORE[n_member] = DEFINED pvalue_now','$string_bytes(pvalue_now) = ($ptascii("A"))',
  '$class_constant_notice_valid(S_resume,pclassconstantdesc.ORIGIN,'+child+',$ptascii("B"),z)',
  'S_value_step = $drive_steps(S_resume,1)','S_value_step.COMPLETION = BUDGET',
  'S_value = S_value_step[.COMPLETION = NORMAL]','S_value.RESULT = KNOWN (PINT 10)',
  'S_value.EVENTS = S_resume.EVENTS','~$class_constant_notice_protected(S_value,pclassconstantdesc.ORIGIN)',
  'S_done = $drive_steps(S_value,30000)','S_done.COMPLETION = NORMAL',
  '$ccn_output(S_done.EVENTS) = '+quoted(json.loads((SOURCE/'cases.json').read_text())['null-bool-int']['stdout']),
  'S_done.CLASSCONSTANTCACHE = eps','S_done.CLASSCONSTANTHISTORY = S_raw.CLASSCONSTANTHISTORY',
  '$class_constant_state_valid(S_done)','$call_descriptors_valid(S_done)',
  'S_zero = $drive_steps(S_storage,0)','S_zero.COMPLETION = BUDGET','S_zero[.COMPLETION = NORMAL] = S_storage',
  'S_one = $drive_steps(S_storage,1)','S_one.COMPLETION = BUDGET',
  '$drive_steps(S_zero[.COMPLETION = NORMAL],30000) = S_done',
  '$drive_steps(S_one[.COMPLETION = NORMAL],30000) = S_done']
 return checks


def prepare(out):
    frontend=Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],out/'frontend')
    adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],out/'adapter')
    checks=[]
    try:
        for name in ['null-bool-int']:
            path=SOURCE/(name+'.php')
            parsed=frontend.request({'op':'parse','source':base64.b64encode(path.read_bytes()).decode()});assert parsed['accepted'] and not parsed['diagnostics']
            checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True});assert checked['ok']
            checks += scalar(checked['fixture'],path)
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
    paths=[Path(__file__),*(SOURCE/p for p in ['null-bool-int.php','cases.json','hashes.json']),*modules,*(ROOT/p for p in (
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
