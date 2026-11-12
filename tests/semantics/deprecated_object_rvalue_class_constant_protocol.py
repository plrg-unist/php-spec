#!/usr/bin/env python3
"""Check temporary object class selection, neutral retirement and saved notice."""
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
SOURCE=ROOT/'tests/semantics/deprecated_object_rvalue_class_constant/temporary-selector.php'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quoted=lambda s:'$base64('+json.dumps(base64.b64encode(s.encode()).decode())+')'
SELECTED=FETCH_SELECTED+r'''
dec $object_class_ready(pstate) : bool
def $object_class_ready(S) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class (NIdentifier (BYTES text_member) metadata_member) z) :: ptask*
  -- if S.RESULT = KNOWN (POBJECT n_receiver)
def $object_class_ready(S) = false -- otherwise
dec $object_class_pause(pstate,nat) : pstate
def $object_class_pause(S,n) = S -- if $object_class_ready(S)
def $object_class_pause(S,n) = $object_class_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$object_class_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $object_class_pause(S,n) = S -- otherwise
'''


def fields(fixture):
    expected=json.loads((SOURCE.parent/'cases.json').read_text())['temporary-selector']['stdout']
    child=quoted('Ns238Object\\Child238');base=quoted('Ns238Object\\Base238')
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(SOURCE)).decode())+')',
        'S_raw = $object_class_pause(S_start[.COMPLETION = NORMAL],30000)','$object_class_ready(S_raw)',
        'S_raw.TODO = (CLASS_CONST_CLASS expression_class (NIdentifier (BYTES text_member) metadata_member) z) :: ptask_tail*',
        '$base64(text_member) = $ptascii("A")','S_raw.ORIGIN = (porigin_site)',
        'S_raw.RESULT = KNOWN (POBJECT n_receiver)','S_raw.CURRENT = eps','S_raw.FRAMES = eps','S_raw.HELD = eps',
        '(HOBJECT n_receiver) <- S_raw.ALLOCATIONS','S_raw.OBJECTS[n_receiver] = INSTANCE porigin_child',
        '$class_at(S_raw.CLASSES,porigin_child) = (pclassdesc_child)','pclassdesc_child.NAME = '+child,
        '$class_named(S_raw.CLASSNAMES,$ptlc('+base+')) = (porigin_base)',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_receiver) = 1',
        '$call_descriptors_valid(S_raw)','$ccn_output(S_raw.EVENTS) = $ptascii("B|C|")',
        'S_class = $class_constant_selector(S_raw,expression_class,z)','S_class.COMPLETION = NORMAL',
        'S_class.RESULT = KNOWN (PSTRING '+child+')',
        '$heap_owners($heap_graph(S_class),HOBJECT n_receiver) = 0',
        '$class_constant_lookup(S_class,porigin_child,$ptascii("A"),|S_class.CLASSES|) = (pclassconstantdesc)',
        'pclassconstantdesc.OWNER = porigin_child','pclassconstantdesc.FOLDED',
        '$class_constant_object_entry(S_class,S_raw.RESULT,expression_class,NIdentifier (BYTES text_member) metadata_member,z,ptask_tail*) = (pclassconstantdesc)',
        '$class_constant_object_entry(S_class,REFERENCE 0,expression_class,NIdentifier (BYTES text_member) metadata_member,z,ptask_tail*) = eps',
        '$class_constant_object_entry(S_class,KNOWN PNULL,expression_class,NIdentifier (BYTES text_member) metadata_member,z,ptask_tail*) = eps',
        '$class_constant_object_entry(S_class,KNOWN (PSTRING '+child+'),expression_class,NIdentifier (BYTES text_member) metadata_member,z,ptask_tail*) = eps',
        '$class_constant_object_entry(S_class[.ALLOCATIONS = eps],S_raw.RESULT,expression_class,NIdentifier (BYTES text_member) metadata_member,z,ptask_tail*) = eps',
        '$class_constant_object_entry(S_class[.RESULT = KNOWN (PSTRING '+base+')],S_raw.RESULT,expression_class,NIdentifier (BYTES text_member) metadata_member,z,ptask_tail*) = eps',
        '$class_constant_rvalue_class_entry(S_class,S_raw.RESULT,expression_class,NIdentifier (BYTES text_member) metadata_member,z,ptask_tail*) = eps',
        'S_neutral = $class_constant_class_forward(S_class,S_raw.RESULT,expression_class,NIdentifier (BYTES text_member) metadata_member,z,ptask_tail*)',
        'S_neutral.COMPLETION = NORMAL','S_neutral.TODO = (CLASS_CONST_OBJECT_FETCH porigin_site '+child+' $ptascii("A") z) :: ptask_tail*',
        'S_neutral.RESULT = KNOWN PNULL','S_neutral.BASE = BASE_VALUE (KNOWN PNULL)',
        '(HOBJECT n_receiver) <- S_neutral.ALLOCATIONS',
        '$heap_owners($heap_graph(S_neutral),HOBJECT n_receiver) = 0',
        '$task_nodes(CLASS_CONST_OBJECT_FETCH porigin_site '+child+' $ptascii("A") z) = eps',
        '$class_constant_object_fetch_valid(S_neutral,porigin_site,'+child+',$ptascii("A"),z)',
        '$class_constant_object_fetch_valid(S_neutral[.COMPLETION = THROWING n_receiver],porigin_site,'+child+',$ptascii("A"),z)',
        '$class_constant_object_fetch_valid(S_neutral,porigin_site,'+base+',$ptascii("A"),z)',
        '~$class_constant_object_fetch_valid(S_neutral,porigin_site,'+child+',$ptascii("A"),$(z + 1))',
        '~$class_constant_object_fetch_valid(S_neutral,porigin_base,'+child+',$ptascii("A"),z)',
        '~$class_constant_object_fetch_valid(S_neutral,porigin_site,'+child+',$ptascii("MISSING"),z)',
        '~$class_constant_notice_protected(S_neutral,pclassconstantdesc.ORIGIN)',
        '$eager_slots(S_raw,S_neutral) = [HOBJECT n_receiver]',
        '$eager_operation_source(S_raw,CLASS_CONST_CLASS expression_class (NIdentifier (BYTES text_member) metadata_member) z) = CLASS_CONST_OBJECT_FETCH porigin_site '+child+' $ptascii("A") z',
        'S_step = $drive_steps(S_raw,1)','S_step.COMPLETION = BUDGET',
        'S_retire = S_step[.COMPLETION = NORMAL]',
        'S_retire.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
        'pdestructionoperation.SOURCE = CLASS_CONST_OBJECT_FETCH porigin_site '+child+' $ptascii("A") z',
        'pdestructionoperation.VALUE = KNOWN PNULL','pdestructionoperation.BASE = BASE_VALUE (KNOWN PNULL)',
        'pdestructionoperation.COMPLETION = NORMAL','pdestructionoperation.PENDING = eps',
        '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
        '$class_constant_object_operation(pdestructionoperation,$ref_return_retire_operation_scope(S_retire,pdestructionoperation))',
        '$eager_operation_source_guard(S_retire,pdestructionoperation)',
        '~$eager_operation_source_guard(S_retire,pdestructionoperation[.VALUE = KNOWN (PSTRING '+child+')])',
        '~$eager_operation_source_guard(S_retire,pdestructionoperation[.VALUE = KNOWN (POBJECT n_receiver)])',
        '~$eager_operation_source_guard(S_retire,pdestructionoperation[.BASE = BASE_VALUE (KNOWN (POBJECT n_receiver))])',
        '~$eager_operation_source_guard(S_retire,pdestructionoperation[.SOURCE = CLASS_CONST_OBJECT_FETCH porigin_site '+child+' $ptascii("A") $(z + 1)])',
        '~$eager_operation_source_guard(S_retire,pdestructionoperation[.SOURCE = CLASS_CONST_OBJECT_FETCH porigin_site '+base+' $ptascii("A") z])',
        '$destructor_operation_live(S_retire,pdestructionoperation)','$call_descriptors_valid(S_retire)',
        '~$class_constant_notice_protected(S_retire,pclassconstantdesc.ORIGIN)',
        '$ccn_output(S_retire.EVENTS) = $ptascii("B|C|")',
        'S_warn = $ccn_pause(S_retire,0,30000)','$ccn_ready(S_warn,0)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN '+child+' $ptascii("A") z',
        '$ccn_output(S_warn.EVENTS) = $ptascii("B|C|D|")',
        '~((HOBJECT n_receiver) <- S_warn.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_warn),HOBJECT n_receiver) = 0','S_warn.DESTRUCTION.OPERATIONS = eps',
        '$class_constant_rvalue_class_source(S_warn,pclassconstantdesc.ORIGIN,'+child+',$ptascii("A"),z)',
        '$class_constant_notice_valid(S_warn,pclassconstantdesc.ORIGIN,'+child+',$ptascii("A"),z)',
        '$task_nodes(perrorcall.RESUME) = eps','$error_call_valid(S_warn,perrorcall)','$call_descriptors_valid(S_warn)',
        'S_resume = $ccn_pause(S_warn,1,30000)','$ccn_ready(S_resume,1)',
        '$ccn_output(S_resume.EVENTS) = $ptascii("B|C|D|H|")',
        'S_value_step = $drive_steps(S_resume,1)','S_value_step.COMPLETION = BUDGET',
        'S_value = S_value_step[.COMPLETION = NORMAL]','S_value.RESULT = KNOWN (PINT 9)',
        'S_value.EVENTS = S_resume.EVENTS','S_value.CLASSCONSTANTCACHE = eps',
        'S_value.CLASSCONSTANTHISTORY = S_resume.CLASSCONSTANTHISTORY',
        '~$class_constant_notice_protected(S_value,pclassconstantdesc.ORIGIN)',
        'S_done = $drive_steps(S_value,30000)','S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = '+quoted(expected),
        '$class_constant_state_valid(S_done)','$call_descriptors_valid(S_done)']


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
