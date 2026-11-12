#!/usr/bin/env python3
"""Check nested shared and retained object graph selection and release."""
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
SOURCE=ROOT/'tests/semantics/deprecated_reference_object_graph'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quoted=lambda s:'$base64('+json.dumps(base64.b64encode(s.encode()).decode())+')'
SELECTED=FETCH_SELECTED+r'''
dec $reference_graph_ready(pstate,nat,nat) : bool
def $reference_graph_ready(S,0,n_middle) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask*
  -- if S.RESULT = REFERENCE n_reference
def $reference_graph_ready(S,1,n_middle) = true
  -- if $ccn_output(S.EVENTS) = $ptascii("B|C|D|H|9|I|H|9|")
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n_middle)
def $reference_graph_ready(S,2,n_middle) = true
  -- if $instance_storage_for(S,n_middle) = (pinstancestorage)
  -- if pinstancestorage.NEXT = 1
  -- if pinstancestorage.SLOTS = ppropertyslot :: ppropertyslot_tail*
  -- if ppropertyslot.STATE = PROP_VALUE (DIRECT (POBJECT n_shared))
  -- if $heap_owners($heap_graph(S),HOBJECT n_shared) = 1
def $reference_graph_ready(S,3,n_middle) = true
  -- if S.TODO = (CLASS_CONST_MEMBER expression_class poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: (CLASS_CONST_OBJECT_CAPTURE porigin ptbytes_class z) :: ptask*
def $reference_graph_ready(S,n_phase,n_middle) = false -- otherwise
dec $reference_graph_pause(pstate,nat,nat,nat) : pstate
def $reference_graph_pause(S,n_phase,n_middle,n_budget) = S -- if $reference_graph_ready(S,n_phase,n_middle)
def $reference_graph_pause(S,n_phase,n_middle,n_budget) = $reference_graph_pause(S_next[.COMPLETION = NORMAL],n_phase,n_middle,$nabs($(n_budget - 1)))
  -- if ~$reference_graph_ready(S,n_phase,n_middle)
  -- if S.COMPLETION = NORMAL /\ $(n_budget > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $reference_graph_pause(S,n_phase,n_middle,n_budget) = S -- otherwise
'''

def graph(fixture,path):
 child=quoted('Ns244Nested\\Child244')
 checks=['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(path)).decode())+')',
  'S_raw = $reference_graph_pause(S_start[.COMPLETION = NORMAL],0,0,30000)','$reference_graph_ready(S_raw,0,0)',
  'S_raw.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask_tail*',
  'S_raw.ORIGIN = (porigin_site)','S_raw.RESULT = REFERENCE n_reference',
  'S_raw.CURRENT = eps','S_raw.FRAMES = eps','S_raw.HELD = eps',
  '$call_reference_operand_valid(S_raw,S_raw.RESULT)',
  'S_raw.STORE[n_reference] = DEFINED (POBJECT n_object)',
  '(HCELL n_reference) <- S_raw.ALLOCATIONS','(HOBJECT n_object) <- S_raw.ALLOCATIONS',
  'S_raw.OBJECTS[n_object] = INSTANCE porigin_child',
  '$objectprops_at(S_raw.OBJECTPROPS,n_object) = ([ppropertyslot_head,ppropertyslot_flag,ppropertyslot_empty,ppropertyslot_tail])',
  'ppropertyslot_head.STATE = PROP_VALUE (DIRECT (POBJECT n_middle))',
  'ppropertyslot_tail.STATE = PROP_VALUE (DIRECT (POBJECT n_shared))',
  'ppropertyslot_flag.STATE = PROP_VALUE (DIRECT (PBOOL false))','ppropertyslot_empty.STATE = PROP_VALUE (DIRECT PNULL)',
  '$property_slot_descriptor(S_raw,n_object,ppropertyslot_head) = (ppropertydesc_head)',
  '$property_slot_descriptor(S_raw,n_object,ppropertyslot_tail) = (ppropertydesc_tail)',
  'ppropertydesc_head.KEY = $ptascii("head")','ppropertydesc_tail.KEY = $ptascii("tail")',
  '$class_at(S_raw.CLASSES,porigin_child) = (pclassdesc_child)',
  'pclassdesc_child.PROPERTIES = [ppropertydesc_tail]',
  '(HOBJECT n_middle) <- S_raw.ALLOCATIONS','(HOBJECT n_shared) <- S_raw.ALLOCATIONS',
  'S_raw.OBJECTS[n_middle] = INSTANCE porigin_middle','S_raw.OBJECTS[n_shared] = INSTANCE porigin_shared',
  '$objectprops_at(S_raw.OBJECTPROPS,n_middle) = ([ppropertyslot_deep,ppropertyslot_tag,ppropertyslot_retained])',
  'ppropertyslot_deep.STATE = PROP_VALUE (DIRECT (POBJECT n_shared))',
  'ppropertyslot_tag.STATE = PROP_VALUE (DIRECT (PINT 0))',
  'ppropertyslot_retained.STATE = PROP_VALUE (DIRECT (POBJECT n_retained))',
  '$objectprops_at(S_raw.OBJECTPROPS,n_shared) = (eps)','$objectprops_at(S_raw.OBJECTPROPS,n_retained) = (eps)',
  '$object_table_at(S_raw.OBJECTTABLES,n_object) = eps',
  '$object_table_at(S_raw.OBJECTTABLES,n_middle) = eps',
  '$heap_owners($heap_graph(S_raw),HCELL n_reference) = 1',
  '$heap_owners($heap_graph(S_raw),HOBJECT n_object) = 1',
  '$heap_owners($heap_graph(S_raw),HOBJECT n_middle) = 1',
  '$heap_owners($heap_graph(S_raw),HOBJECT n_shared) = 2',
  '$heap_owners($heap_graph(S_raw),HOBJECT n_retained) = 2',
  '$machine_base_roots(S_raw) = eps','$call_descriptors_valid(S_raw)',
  '$ccn_output(S_raw.EVENTS) = $ptascii("B|C|")',
  'S_class = $class_constant_selector(S_raw,expression_class,z)','S_class.COMPLETION = NORMAL',
  'S_class.RESULT = KNOWN (PSTRING '+child+')',
  '$heap_owners($heap_graph(S_class),HCELL n_reference) = 0',
  '$heap_owners($heap_graph(S_class),HOBJECT n_object) = 1',
  '$eager_slots(S_raw,S_class) = [HCELL n_reference]',
  '~$class_constant_reference_object_fields(S_class,n_object,[ppropertyslot_head,ppropertyslot_flag,ppropertyslot_empty,ppropertyslot_tail])',
  '$class_constant_reference_object_graph(S_class,n_object,eps)',
  '$class_constant_reference_object_graph(S_class,n_middle,[n_object])',
  '$class_constant_reference_object_graph_value(S_class,POBJECT n_shared,[n_object,n_middle])',
  '~$class_constant_reference_object_graph(S_class,n_object,[n_object])',
  '$class_constant_reference_object_selector(S_class,S_raw.RESULT) = (pclassdesc_child)',
  '$class_constant_reference_object_capture_entry(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
  '$class_constant_object_capture_source(S_class,porigin_site,'+child+',z)',
  '$eager_operation_source(S_raw,CLASS_CONST_CLASS expression_class expression_member z) = CLASS_CONST_OBJECT_CAPTURE porigin_site '+child+' z']
 for name,state in [('root_cycle','PROP_VALUE (DIRECT (POBJECT n_object))'),
                    ('self_cycle','PROP_VALUE (DIRECT (POBJECT n_middle))'),
                    ('alias','PROP_VALUE (ALIAS n_reference)'),
                    ('string','PROP_VALUE (DIRECT (PSTRING $ptascii("x")))'),
                    ('array','PROP_VALUE (DIRECT (PARRAY 0))'),('unset','PROP_UNSET')]:
  view='S_'+name
  checks += [view+' = S_class[.OBJECTPROPS = $objectprops_set(S_class.OBJECTPROPS,n_middle,[ppropertyslot_deep[.STATE = '+state+'],ppropertyslot_tag,ppropertyslot_retained])]',
   '~$class_constant_reference_object_graph('+view+',n_object,eps)',
   '$class_constant_reference_object_selector('+view+',S_raw.RESULT) = eps']
 for name,slots in [('reordered','[ppropertyslot_retained,ppropertyslot_tag,ppropertyslot_deep]'),
                    ('duplicate','[ppropertyslot_deep,ppropertyslot_tag,ppropertyslot_deep]')]:
  view='S_'+name
  checks += [view+' = S_class[.OBJECTPROPS = $objectprops_set(S_class.OBJECTPROPS,n_middle,'+slots+')]',
   '$class_constant_reference_object_graph('+view+',n_object,eps)',
   '$class_constant_reference_object_selector('+view+',S_raw.RESULT) = (pclassdesc_child)',
   '~$call_descriptors_valid('+view+')',
   '~$class_constant_reference_object_capture_entry('+view+',S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)']
 checks += [
  '~$class_constant_reference_object_capture_entry(S_class[.HELD = [HCELL n_reference]],S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
  '~$class_constant_reference_object_capture_entry(S_class[.BASE = BASE_VALUE (REFERENCE n_reference)],S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
  '$class_constant_reference_object_selector(S_class[.RESULT = KNOWN PNULL],S_raw.RESULT) = eps',
  '$class_constant_reference_object_selector(S_class,KNOWN (POBJECT n_object)) = eps',
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
  'S_middle = $reference_graph_pause(S_release,1,n_middle,30000)','$reference_graph_ready(S_middle,1,n_middle)',
  'S_middle.CURRENT = (pcallcontext_middle)','pcallcontext_middle.RECEIVER = (n_middle)',
  '$instance_storage_for(S_middle,n_object) = (pinstancestorage_owner)',
  'pinstancestorage_owner.OBJECT = n_object','pinstancestorage_owner.NEXT = 1',
  '$heap_owners($heap_graph(S_middle),HOBJECT n_shared) = 2',
  '$heap_owners($heap_graph(S_middle),HOBJECT n_retained) = 2',
  '~(n_shared <- S_middle.DESTRUCTION.CALLED)','~(n_retained <- S_middle.DESTRUCTION.CALLED)',
  '$call_descriptors_valid(S_middle)','$eager_operation_source_guard(S_middle,pdestructionoperation)',
  'S_edge = $reference_graph_pause(S_middle,2,n_middle,30000)','$reference_graph_ready(S_edge,2,n_middle)',
  '$instance_storage_for(S_edge,n_middle) = (pinstancestorage_middle)','pinstancestorage_middle.NEXT = 1',
  '$instance_storage_for(S_edge,n_object) = (pinstancestorage_root)','pinstancestorage_root.NEXT = 1',
  '$objectprops_at(S_edge.OBJECTPROPS,n_middle) = ([ppropertyslot_deep[.STATE = PROP_UNSET],ppropertyslot_tag,ppropertyslot_retained])',
  '$objectprops_at(S_edge.OBJECTPROPS,n_object) = ([ppropertyslot_head[.STATE = PROP_UNSET],ppropertyslot_flag,ppropertyslot_empty,ppropertyslot_tail])',
  '$heap_owners($heap_graph(S_edge),HOBJECT n_shared) = 1',
  '$heap_owners($heap_graph(S_edge),HOBJECT n_retained) = 2',
  '(HOBJECT n_object) <- S_edge.ALLOCATIONS','(HOBJECT n_middle) <- S_edge.ALLOCATIONS',
  '(HOBJECT n_shared) <- S_edge.ALLOCATIONS','~(n_shared <- S_edge.DESTRUCTION.CALLED)',
  '$call_descriptors_valid(S_edge)','$eager_operation_source_guard(S_edge,pdestructionoperation)',
  'S_pair = $reference_graph_pause(S_edge,3,n_middle,30000)','$reference_graph_ready(S_pair,3,n_middle)',
  'S_pair.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING '+child+')) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING '+child+')) z) :: ptask_marker :: ptask_tail*',
  'S_pair.RESULT = KNOWN pvalue_member','$string_bytes(pvalue_member) = ($ptascii("B"))',
  '$ccn_output(S_pair.EVENTS) = $ptascii("B|C|D|H|9|I|H|9|G|M|")',
  '~((HCELL n_reference) <- S_pair.ALLOCATIONS)','~((HOBJECT n_object) <- S_pair.ALLOCATIONS)',
  '~((HOBJECT n_middle) <- S_pair.ALLOCATIONS)','~((HOBJECT n_shared) <- S_pair.ALLOCATIONS)',
  '(HOBJECT n_retained) <- S_pair.ALLOCATIONS','$heap_owners($heap_graph(S_pair),HOBJECT n_retained) = 1',
  '~(n_retained <- S_pair.DESTRUCTION.CALLED)','S_pair.DESTRUCTION.OPERATIONS = eps',
  '$class_constant_object_member_entry(S_pair,S_pair.RESULT,expression_class,KNOWN (PSTRING '+child+'),z,ptask_tail*) = (pclassconstantdesc)',
  'S_warn = $ccn_pause(S_pair,0,30000)','$ccn_ready(S_warn,0)',
  'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
  'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN '+child+' $ptascii("B") z',
  '$task_nodes(perrorcall.RESUME) = eps','$error_call_valid(S_warn,perrorcall)',
  'S_resume = $ccn_pause(S_warn,1,30000)','$ccn_ready(S_resume,1)',
  '$ccn_output(S_resume.EVENTS) = $ptascii("B|C|D|H|9|I|H|9|G|M|H|")',
  'S_global_resume = $global_table_view(S_resume)',
  '$lookup(S_global_resume.ENV,$ptascii("member244")) = (n_member)',
  'S_global_resume.STORE[n_member] = DEFINED pvalue_now','$string_bytes(pvalue_now) = ($ptascii("A"))',
  '$class_constant_notice_valid(S_resume,pclassconstantdesc.ORIGIN,'+child+',$ptascii("B"),z)',
  'S_value_step = $drive_steps(S_resume,1)','S_value_step.COMPLETION = BUDGET',
  'S_value = S_value_step[.COMPLETION = NORMAL]','S_value.RESULT = KNOWN (PINT 10)',
  'S_value.EVENTS = S_resume.EVENTS','~$class_constant_notice_protected(S_value,pclassconstantdesc.ORIGIN)',
  'S_done = $drive_steps(S_value,30000)','S_done.COMPLETION = NORMAL',
  '$ccn_output(S_done.EVENTS) = '+quoted(json.loads((SOURCE/'cases.json').read_text())['nested-shared-retained']['stdout']),
  '~((HOBJECT n_retained) <- S_done.ALLOCATIONS)','n_retained <- S_done.DESTRUCTION.CALLED',
  'S_done.CLASSCONSTANTCACHE = eps','S_done.CLASSCONSTANTHISTORY = S_raw.CLASSCONSTANTHISTORY',
  '$class_constant_state_valid(S_done)','$call_descriptors_valid(S_done)',
  'S_zero = $drive_steps(S_edge,0)','S_zero.COMPLETION = BUDGET','S_zero[.COMPLETION = NORMAL] = S_edge',
  'S_one = $drive_steps(S_edge,1)','S_one.COMPLETION = BUDGET',
  '$drive_steps(S_zero[.COMPLETION = NORMAL],30000) = S_done',
  '$drive_steps(S_one[.COMPLETION = NORMAL],30000) = S_done']
 return checks


def prepare(out):
    frontend=Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],out/'frontend')
    adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],out/'adapter')
    checks=[]
    try:
        for name in ['nested-shared-retained']:
            path=SOURCE/(name+'.php')
            parsed=frontend.request({'op':'parse','source':base64.b64encode(path.read_bytes()).decode()});assert parsed['accepted'] and not parsed['diagnostics']
            checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True});assert checked['ok']
            checks += graph(checked['fixture'],path)
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
    paths=[Path(__file__),*(SOURCE/p for p in ['nested-shared-retained.php','cases.json','hashes.json']),*modules,*(ROOT/p for p in (
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
