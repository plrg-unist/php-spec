#!/usr/bin/env python3
"""Check object class kind, member staging and selected notice after retirement."""
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
SOURCE=ROOT/'tests/semantics/deprecated_object_class_computed_member/destructor-before-member.php'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quoted=lambda s:'$base64('+json.dumps(base64.b64encode(s.encode()).decode())+')'
SELECTED=FETCH_SELECTED+r'''
dec $object_member_ready(pstate,nat) : bool
def $object_member_ready(S,0) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask*
  -- if S.RESULT = KNOWN (POBJECT n_receiver)
def $object_member_ready(S,1) = true
  -- if S.TODO = (CLASS_CONST_MEMBER expression_class poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: (CLASS_CONST_OBJECT_CAPTURE porigin ptbytes_class z) :: ptask*
  -- if S.ORIGIN = (porigin)
def $object_member_ready(S,n) = false -- otherwise
dec $object_member_pause(pstate,nat,nat) : pstate
def $object_member_pause(S,n_phase,n_budget) = S -- if $object_member_ready(S,n_phase)
def $object_member_pause(S,n_phase,n_budget) = $object_member_pause(S_next[.COMPLETION = NORMAL],n_phase,$nabs($(n_budget - 1)))
  -- if ~$object_member_ready(S,n_phase)
  -- if S.COMPLETION = NORMAL /\ $(n_budget > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $object_member_pause(S,n_phase,n_budget) = S -- otherwise
'''


def fields(fixture):
    expected=json.loads((SOURCE.parent/'cases.json').read_text())['destructor-before-member']['stdout']
    child=quoted('Ns239Object\\Child239');base=quoted('Ns239Object\\Base239')
    checks=['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(SOURCE)).decode())+')',
        'S_raw = $object_member_pause(S_start[.COMPLETION = NORMAL],0,30000)','$object_member_ready(S_raw,0)',
        'S_raw.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask_tail*',
        'S_raw.ORIGIN = (porigin_site)','S_raw.RESULT = KNOWN (POBJECT n_receiver)',
        'S_raw.CURRENT = eps','S_raw.FRAMES = eps','S_raw.HELD = eps',
        '(HOBJECT n_receiver) <- S_raw.ALLOCATIONS','S_raw.OBJECTS[n_receiver] = INSTANCE porigin_child',
        '$class_at(S_raw.CLASSES,porigin_child) = (pclassdesc_child)','pclassdesc_child.NAME = '+child,
        '$class_named(S_raw.CLASSNAMES,$ptlc('+base+')) = (porigin_base)',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_receiver) = 1',
        '$call_descriptors_valid(S_raw)','$ccn_output(S_raw.EVENTS) = $ptascii("B|C|")',
        'S_class = $class_constant_selector(S_raw,expression_class,z)','S_class.COMPLETION = NORMAL',
        'S_class.RESULT = KNOWN (PSTRING '+child+')',
        '$class_constant_lookup(S_class,porigin_child,$ptascii("B"),|S_class.CLASSES|) = (pclassconstantdesc)',
        '$class_constant_object_class_entry(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        '~$class_constant_object_class_entry(S_class,REFERENCE 0,expression_class,expression_member,z,ptask_tail*)',
        '~$class_constant_object_class_entry(S_class,KNOWN PNULL,expression_class,expression_member,z,ptask_tail*)',
        '~$class_constant_object_class_entry(S_class,KNOWN (PSTRING '+child+'),expression_class,expression_member,z,ptask_tail*)',
        '~$class_constant_object_class_entry(S_class[.ALLOCATIONS = eps],S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        '~$class_constant_object_class_entry(S_class[.RESULT = KNOWN (PSTRING '+base+')],S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        '~$class_constant_object_class_entry(S_class[.HELD = [HOBJECT n_receiver]],S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        '~$class_constant_string_class_entry(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        'S_neutral = $class_constant_class_forward(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        'ptask_marker = CLASS_CONST_OBJECT_CAPTURE porigin_site '+child+' z',
        'ptask_member = $at_task($origin_child((porigin_site),[PCFIELD 1]),EVAL expression_member)',
        'S_neutral.TODO = ptask_member :: (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING '+child+')) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING '+child+')) z) :: ptask_marker :: ptask_tail*',
        'S_neutral.COMPLETION = NORMAL','S_neutral.RESULT = KNOWN PNULL','S_neutral.BASE = BASE_VALUE (KNOWN PNULL)',
        '$task_nodes(ptask_marker) = eps',
        '~$class_constant_notice_task(ptask_marker,pclassconstantdesc.ORIGIN)',
        '~$class_constant_notice_protected(S_neutral,pclassconstantdesc.ORIGIN)',
        '$class_constant_object_capture_source(S_neutral,porigin_site,'+child+',z)',
        '$class_constant_object_capture_source(S_neutral[.COMPLETION = BUDGET],porigin_site,'+child+',z)',
        '$class_constant_object_capture_source(S_neutral,porigin_site,'+base+',z)',
        '$call_task_valid(S_neutral,ptask_marker)',
        '$eager_slots(S_raw,S_neutral) = [HOBJECT n_receiver]',
        '$eager_operation_source(S_raw,CLASS_CONST_CLASS expression_class expression_member z) = ptask_marker',
        'S_release_raw = $drive_steps(S_raw,1)','S_release_raw.COMPLETION = BUDGET',
        'S_release = S_release_raw[.COMPLETION = NORMAL]',
        'S_release.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
        'pdestructionoperation.SOURCE = ptask_marker','pdestructionoperation.PENDING = eps',
        'pdestructionoperation.COMPLETION = NORMAL','pdestructionoperation.VALUE = KNOWN PNULL',
        'pdestructionoperation.BASE = BASE_VALUE (KNOWN PNULL)',
        '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
        '$eager_operation_source_guard(S_release,pdestructionoperation)',
        '$destructor_operation_live(S_release,pdestructionoperation)','$call_descriptors_valid(S_release)',
        '$ccn_output(S_release.EVENTS) = $ptascii("B|C|")']
    for tag,change in [('class','.SOURCE = CLASS_CONST_OBJECT_CAPTURE porigin_site '+base+' z'),
                       ('value','.VALUE = KNOWN (PINT 1)'),('base','.BASE = BASE_VALUE (KNOWN (POBJECT n_receiver))'),
                       ('completion','.COMPLETION = BUDGET')]:
        checks += ['pdestructionoperation_'+tag+' = pdestructionoperation['+change+']',
            'S_counter_'+tag+' = S_neutral[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_'+tag+') :: S_neutral.TODO]',
            '~$class_constant_object_capture_operation(pdestructionoperation_'+tag+',(S_counter_'+tag+'))']
    checks += ['S_pair = $object_member_pause(S_release,1,30000)','$object_member_ready(S_pair,1)',
        'S_pair.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING '+child+')) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING '+child+')) z) :: ptask_marker :: ptask_tail*',
        'S_pair.RESULT = KNOWN pvalue_member','$string_bytes(pvalue_member) = ($ptascii("B"))',
        '$ccn_output(S_pair.EVENTS) = $ptascii("B|C|D|M|")',
        '~((HOBJECT n_receiver) <- S_pair.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_pair),HOBJECT n_receiver) = 0','S_pair.DESTRUCTION.OPERATIONS = eps',
        '$class_constant_lookup(S_pair,porigin_child,$ptascii("B"),|S_pair.CLASSES|) = (pclassconstantdesc)',
        '$class_constant_object_member_entry(S_pair,S_pair.RESULT,expression_class,KNOWN (PSTRING '+child+'),z,ptask_tail*) = (pclassconstantdesc)',
        '$class_constant_string_member_entry(S_pair,S_pair.RESULT,expression_class,KNOWN (PSTRING '+child+'),z,ptask_marker :: ptask_tail*) = eps',
        '$class_constant_object_member_entry(S_pair,REFERENCE 0,expression_class,KNOWN (PSTRING '+child+'),z,ptask_tail*) = eps',
        '$class_constant_object_member_entry(S_pair,KNOWN PNULL,expression_class,KNOWN (PSTRING '+child+'),z,ptask_tail*) = eps',
        '~$class_constant_notice_valid(S_pair,pclassconstantdesc.ORIGIN,'+child+',$ptascii("B"),z)',
        'S_missing = S_pair[.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING '+child+')) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING '+child+')) z) :: ptask_tail*]',
        '$class_constant_object_member_entry(S_missing,S_pair.RESULT,expression_class,KNOWN (PSTRING '+child+'),z,ptask_tail*) = eps',
        '$call_descriptors_valid(S_missing)',
        'PhpStep: S_missing ~> S_refused','S_refused.COMPLETION = UNSUPPORTED "Deprecated class constant fetch"',
        'S_refused.EVENTS = S_pair.EVENTS',
        'S_dispatch_step = $drive_steps(S_pair,1)','S_dispatch_step.COMPLETION = BUDGET',
        'S_warn = S_dispatch_step[.COMPLETION = NORMAL]',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN '+child+' $ptascii("B") z',
        '$ccn_output(S_warn.EVENTS) = $ptascii("B|C|D|M|")',
        '$class_constant_notice_valid(S_warn,pclassconstantdesc.ORIGIN,'+child+',$ptascii("B"),z)',
        '$task_nodes(perrorcall.RESUME) = eps','$error_call_valid(S_warn,perrorcall)','$call_descriptors_valid(S_warn)',
        'S_resume = $ccn_pause(S_warn,1,30000)','$ccn_ready(S_resume,1)',
        '$ccn_output(S_resume.EVENTS) = $ptascii("B|C|D|M|H|")',
        'S_global = $global_table_view(S_resume)',
        '$lookup(S_global.ENV,$ptascii("member239")) = (n_member_slot)',
        'S_global.STORE[n_member_slot] = DEFINED pvalue_now','$string_bytes(pvalue_now) = ($ptascii("A"))',
        'S_value_step = $drive_steps(S_resume,1)','S_value_step.COMPLETION = BUDGET',
        'S_value = S_value_step[.COMPLETION = NORMAL]','S_value.RESULT = KNOWN (PINT 10)',
        'S_value.EVENTS = S_resume.EVENTS','S_value.CLASSCONSTANTCACHE = eps',
        'S_value.CLASSCONSTANTHISTORY = S_resume.CLASSCONSTANTHISTORY',
        '~$class_constant_notice_protected(S_value,pclassconstantdesc.ORIGIN)',
        'S_done = $drive_steps(S_value,30000)','S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = '+quoted(expected),
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
