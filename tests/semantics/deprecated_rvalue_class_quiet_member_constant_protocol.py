#!/usr/bin/env python3
"""Check class effects before quiet member capture and input-kind contracts."""
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
SOURCE=ROOT/'tests/semantics/deprecated_rvalue_class_quiet_member_constant/class-before-member.php'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quoted=lambda s:'$base64('+json.dumps(base64.b64encode(s.encode()).decode())+')'
SELECTED=FETCH_SELECTED+r'''
dec $dual_pair_ready(pstate,bool) : bool
def $dual_pair_ready(S,false) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask*
def $dual_pair_ready(S,true) = true
  -- if S.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ptbytes_class)) z) :: (CLASS_CONST_CAPTURE porigin (KNOWN (PSTRING ptbytes_class)) z) :: (CLASS_CONST_STRING_CAPTURE porigin ptbytes_class z) :: ptask*
def $dual_pair_ready(S,b) = false -- otherwise
dec $dual_pair_pause(pstate,bool,nat) : pstate
def $dual_pair_pause(S,b,n) = S -- if $dual_pair_ready(S,b)
def $dual_pair_pause(S,b,n) = $dual_pair_pause(S_next[.COMPLETION = NORMAL],b,$nabs($(n - 1)))
  -- if ~$dual_pair_ready(S,b)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $dual_pair_pause(S,b,n) = S -- otherwise
'''


def fields(fixture):
    expected=json.loads((SOURCE.parent/'cases.json').read_text())['class-before-member']['stdout']
    child=quoted('Ns236Order\\Child236');base=quoted('Ns236Order\\Base236');other=quoted('Ns236Order\\Other236')
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(SOURCE)).decode())+')',
        'S_raw = $dual_pair_pause(S_start[.COMPLETION = NORMAL],false,30000)','$dual_pair_ready(S_raw,false)',
        'S_raw.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask_tail*','S_raw.ORIGIN = (porigin_site)',
        '$origin_node(S_raw.SOURCES,porigin_site) = (NExprClassConstFetch expression_class expression_member metadata)',
        'expression_member = NExprVariable (BYTES text_member) metadata_member','$base64(text_member) = $ptascii("member236")',
        'S_raw.RESULT = KNOWN pvalue_raw','$constant_value_class_valid(S_raw,pvalue_raw,PVSTRING false)',
        '$string_bytes(pvalue_raw) = ('+child+')','$value_nodes(pvalue_raw) = eps',
        '$ccn_output(S_raw.EVENTS) = $ptascii("O|C|")','S_raw.CURRENT = eps','S_raw.FRAMES = eps','S_raw.HELD = eps',
        'S_raw_globals = $global_table_view(S_raw)','$lookup(S_raw_globals.ENV,$ptascii("class236")) = (n_class)',
        '$lookup(S_raw_globals.ENV,$ptascii("member236")) = (n_member)',
        'S_raw_globals.STORE[n_member] = DEFINED pvalue_after_class','$string_bytes(pvalue_after_class) = ($ptascii("A"))',
        'S_class = $class_constant_selector(S_raw,expression_class,z)','S_class.RESULT = KNOWN (PSTRING '+child+')',
        '$class_constant_string_class_entry(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        '~$class_constant_string_class_entry(S_class,REFERENCE n_class,expression_class,expression_member,z,ptask_tail*)',
        '~$class_constant_string_class_entry(S_class,KNOWN PNULL,expression_class,expression_member,z,ptask_tail*)',
        'S_scheduled = $class_constant_class_forward(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        'S_scheduled.TODO = ptask_eval :: (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING '+child+')) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING '+child+')) z) :: (CLASS_CONST_STRING_CAPTURE porigin_site '+child+' z) :: ptask_tail*',
        'ptask_eval = $at_task($origin_child(S_raw.ORIGIN,[PCFIELD 1]),EVAL expression_member)',
        '$task_nodes(CLASS_CONST_STRING_CAPTURE porigin_site '+child+' z) = eps',
        '$call_task_valid(S_scheduled,CLASS_CONST_STRING_CAPTURE porigin_site '+child+' z)','$call_descriptors_valid(S_scheduled)',
        'S_pair = $dual_pair_pause(S_scheduled,true,30000)','$dual_pair_ready(S_pair,true)',
        'S_pair.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING '+child+')) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING '+child+')) z) :: (CLASS_CONST_STRING_CAPTURE porigin_site '+child+' z) :: ptask_tail*',
        'S_pair.RESULT = VARIABLE $ptascii("member236") z_member',
        'S_read = $resolve_at(S_pair,S_pair.RESULT,z)','S_read.RESULT = KNOWN pvalue_member',
        '$constant_value_class_valid(S_read,pvalue_member,PVSTRING false)','$string_bytes(pvalue_member) = ($ptascii("A"))',
        '$value_nodes(pvalue_member) = eps','$ccn_output(S_pair.EVENTS) = $ptascii("O|C|")',
        '$class_named(S_read.CLASSNAMES,$ptlc('+child+')) = (porigin_class)',
        '$class_constant_lookup(S_read,porigin_class,$ptascii("A"),|S_read.CLASSES|) = (pclassconstantdesc)',
        '$class_constant_lookup(S_read,porigin_class,$ptascii("B"),|S_read.CLASSES|) = (pclassconstantdesc_b)',
        'pclassconstantdesc.OWNERNAME = '+base,'pclassconstantdesc.FOLDED',
        '$class_constant_string_member_source(S_read,porigin_site,$ptascii("A"))',
        '$class_constant_string_member_source(S_read,porigin_site,$ptascii("B"))',
        '$class_constant_string_member_original(S_read,porigin_site,S_pair.RESULT,pvalue_member)',
        '~$class_constant_string_member_original(S_read,porigin_site,KNOWN pvalue_member,pvalue_member)',
        '$class_constant_string_member_entry(S_read,S_pair.RESULT,expression_class,KNOWN (PSTRING '+child+'),z,ptask_tail*) = (pclassconstantdesc)',
        '$class_constant_string_member_entry(S_read,KNOWN pvalue_member,expression_class,KNOWN (PSTRING '+child+'),z,ptask_tail*) = eps',
        '$class_constant_string_member_entry(S_read,REFERENCE n_member,expression_class,KNOWN (PSTRING '+child+'),z,ptask_tail*) = eps',
        '$class_constant_string_member_entry(S_read,KNOWN PNULL,expression_class,KNOWN (PSTRING '+child+'),z,ptask_tail*) = eps',
        '$class_constant_string_member_entry(S_read,VARIABLE $ptascii("wrong") z_member,expression_class,KNOWN (PSTRING '+child+'),z,ptask_tail*) = eps',
        '$class_constant_string_member_entry(S_read,S_pair.RESULT,expression_class,KNOWN (PSTRING '+child+'),z,DISCARD :: ptask_tail*) = eps',
        '~$class_constant_notice_valid(S_read,pclassconstantdesc.ORIGIN,'+child+',$ptascii("A"),z)',
        'S_missing = S_pair[.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING '+child+')) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING '+child+')) z) :: ptask_tail*]',
        'S_missing_read = $resolve_at(S_missing,S_missing.RESULT,z)','$call_descriptors_valid(S_missing_read)',
        '$class_constant_string_member_entry(S_missing_read,S_pair.RESULT,expression_class,KNOWN (PSTRING '+child+'),z,ptask_tail*) = eps',
        'S_missing_step = $drive_steps(S_missing,1)',
        'S_missing_step.COMPLETION = UNSUPPORTED "Deprecated class constant fetch"','S_missing_step.EVENTS = S_pair.EVENTS',
        'S_mismatch = S_read[.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING '+child+')) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING '+child+')) z) :: (CLASS_CONST_STRING_CAPTURE porigin_site '+other+' z) :: ptask_tail*]',
        '$call_task_valid(S_mismatch,CLASS_CONST_STRING_CAPTURE porigin_site '+other+' z)',
        '$class_constant_string_member_entry(S_mismatch,S_pair.RESULT,expression_class,KNOWN (PSTRING '+child+'),z,ptask_tail*) = eps',
        'S_metadata_only = S_read[.ENV = eps][.STORE = eps][.RESULT = KNOWN PNULL]',
        '$call_task_valid(S_metadata_only,CLASS_CONST_STRING_CAPTURE porigin_site '+child+' z)',
        '$class_constant_string_member_entry(S_metadata_only,S_pair.RESULT,expression_class,KNOWN (PSTRING '+child+'),z,ptask_tail*) = eps',
        'S_warn_one = $drive_steps(S_pair,1)','S_warn_one.COMPLETION = BUDGET','S_warn = S_warn_one[.COMPLETION = NORMAL]',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN '+child+' $ptascii("A") z',
        '$error_call_valid(S_warn,perrorcall)','$call_task_valid(S_warn,perrorcall.RESUME)',
        '$task_nodes(perrorcall.RESUME) = eps','$class_constant_notice_protected(S_warn,pclassconstantdesc.ORIGIN)',
        'S_resume = $ccn_pause(S_warn,1,30000)','$ccn_ready(S_resume,1)',
        '$ccn_output(S_resume.EVENTS) = $ptascii("O|C|H|")',
        'S_resume_globals = $global_table_view(S_resume)',
        'S_resume_globals.STORE[n_member] = DEFINED pvalue_member_now','$string_bytes(pvalue_member_now) = ($ptascii("B"))',
        'S_resume_globals.STORE[n_class] = DEFINED pvalue_class_now','$string_bytes(pvalue_class_now) = ('+other+')',
        '$class_named(S_resume.CLASSNAMES,$ptlc('+other+')) = (porigin_other)',
        '$class_constant_lookup(S_resume,porigin_other,$ptascii("A"),|S_resume.CLASSES|) = (pclassconstantdesc_other)',
        '$class_constant_notice_valid(S_resume,pclassconstantdesc.ORIGIN,'+child+',$ptascii("A"),z)',
        '~$class_constant_notice_valid(S_resume[.RESULT = KNOWN (PSTRING $ptascii("A"))],pclassconstantdesc_other.ORIGIN,'+other+',$ptascii("A"),z)',
        '~$class_constant_notice_valid(S_resume[.RESULT = KNOWN (PSTRING $ptascii("B"))],pclassconstantdesc_b.ORIGIN,'+child+',$ptascii("B"),z)',
        'S_value_one = $drive_steps(S_resume,1)','S_value_one.COMPLETION = BUDGET','S_value = S_value_one[.COMPLETION = NORMAL]',
        'S_value.RESULT = KNOWN (PINT 7)','S_value.EVENTS = S_resume.EVENTS',
        'S_second_raw = $dual_pair_pause(S_value,false,30000)','$dual_pair_ready(S_second_raw,false)',
        'S_second_raw.TODO = (CLASS_CONST_CLASS expression_second_class expression_second_member z_second) :: ptask_second*',
        'S_second_raw.ORIGIN = (porigin_second)','$ccn_output(S_second_raw.EVENTS) = $ptascii("O|C|H|7|F|C|")',
        'S_second_class = $class_constant_selector(S_second_raw,expression_second_class,z_second)',
        'S_second_class.RESULT = KNOWN (PSTRING '+other+')',
        '$class_constant_string_class_entry(S_second_class,S_second_raw.RESULT,expression_second_class,expression_second_member,z_second,ptask_second*)',
        'S_second_pair = $dual_pair_pause($class_constant_class_forward(S_second_class,S_second_raw.RESULT,expression_second_class,expression_second_member,z_second,ptask_second*),true,30000)',
        '$dual_pair_ready(S_second_pair,true)',
        'S_second_pair.TODO = (CLASS_CONST_MEMBER expression_second_class (KNOWN (PSTRING '+other+')) z_second) :: (CLASS_CONST_CAPTURE porigin_second (KNOWN (PSTRING '+other+')) z_second) :: (CLASS_CONST_STRING_CAPTURE porigin_second '+other+' z_second) :: ptask_second*',
        'S_second_pair.RESULT = VARIABLE $ptascii("member236") z_second_member',
        'S_second_read = $resolve_at(S_second_pair,S_second_pair.RESULT,z_second)',
        'S_second_read.RESULT = KNOWN pvalue_second_member','$string_bytes(pvalue_second_member) = ($ptascii("A"))',
        '$class_constant_string_member_entry(S_second_read,S_second_pair.RESULT,expression_second_class,KNOWN (PSTRING '+other+'),z_second,ptask_second*) = (pclassconstantdesc_other)',
        'S_done = $drive_steps(S_second_pair,30000)','S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = '+quoted(expected),'S_done.CLASSCONSTANTCACHE = eps',
        'S_done.CLASSCONSTANTHISTORY = S_pair.CLASSCONSTANTHISTORY',
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
