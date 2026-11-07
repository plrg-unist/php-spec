#!/usr/bin/env python3
"""Check class-CV capture across completed member effects."""
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
SOURCE=ROOT/'tests/semantics/deprecated_cv_class_rvalue_member_constant/string-rebind.php'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quoted=lambda s:'$base64('+json.dumps(base64.b64encode(s.encode()).decode())+')'
SELECTED=FETCH_SELECTED+r'''
dec $cv_rvalue_ready(pstate,bool) : bool
def $cv_rvalue_ready(S,false) = true
  -- if S.TODO = (CLASS_CONST_CLASS (NExprVariable (BYTES text) metadata) expression_member z) :: ptask*
def $cv_rvalue_ready(S,true) = true
  -- if S.TODO = (CLASS_CONST_MEMBER (NExprVariable (BYTES text) metadata) poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: ptask*
def $cv_rvalue_ready(S,b) = false -- otherwise
dec $cv_rvalue_pause(pstate,bool,nat) : pstate
def $cv_rvalue_pause(S,b,n) = S -- if $cv_rvalue_ready(S,b)
def $cv_rvalue_pause(S,b,n) = $cv_rvalue_pause(S_next[.COMPLETION = NORMAL],b,$nabs($(n - 1)))
  -- if ~$cv_rvalue_ready(S,b)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $cv_rvalue_pause(S,b,n) = S -- otherwise
'''


def fields(fixture):
    expected=json.loads((SOURCE.parent/'cases.json').read_text())['string-rebind']['stdout']
    child=quoted('Ns231String\\Child231')
    base=quoted('Ns231String\\Base231')
    other=quoted('Ns231String\\Other231')
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(SOURCE)).decode())+')',
        'S_raw = $cv_rvalue_pause(S_start[.COMPLETION = NORMAL],false,30000)','$cv_rvalue_ready(S_raw,false)',
        'S_raw.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask_tail*',
        'S_raw.ORIGIN = (porigin_site)','porigin_site = PORIGIN n_unit pcpath',
        '$origin_node(S_raw.SOURCES,porigin_site) = (NExprClassConstFetch expression_class expression_member metadata)',
        'expression_class = NExprVariable (BYTES text_class) metadata_class','$base64(text_class) = $ptascii("class231")',
        'S_read = $resolve_at(S_raw,S_raw.RESULT,z)','S_read.RESULT = KNOWN pvalue_class',
        '$string_bytes(pvalue_class) = ('+child+')','$ccn_output(S_raw.EVENTS) = eps',
        'S_class = $class_constant_selector(S_raw,expression_class,z)','S_class.RESULT = KNOWN (PSTRING '+child+')',
        'S_scheduled_one = $drive_steps(S_raw,1)','S_scheduled_one.COMPLETION = BUDGET',
        'S_scheduled = S_scheduled_one[.COMPLETION = NORMAL]',
        'S_scheduled.TODO = ptask_eval :: (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING '+child+')) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING '+child+')) z) :: ptask_tail*',
        'ptask_eval = $at_task($origin_child(S_raw.ORIGIN,[PCFIELD 1]),EVAL expression_member)',
        'S_scheduled.RESULT = KNOWN PNULL','$call_descriptors_valid(S_scheduled)',
        'S_pair = $cv_rvalue_pause(S_scheduled,true,30000)','$cv_rvalue_ready(S_pair,true)',
        'S_pair.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING '+child+')) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING '+child+')) z) :: ptask_tail*',
        'S_pair.RESULT = KNOWN pvalue_member','$constant_value_class_valid(S_pair,pvalue_member,PVSTRING false)',
        '$string_bytes(pvalue_member) = ($ptascii("A"))','$value_nodes(pvalue_member) = eps',
        '$ccn_output(S_pair.EVENTS) = $ptascii("M|")','S_pair.CURRENT = eps','S_pair.FRAMES = eps','S_pair.HELD = eps',
        'S_pair_globals = $global_table_view(S_pair)','$lookup(S_pair_globals.ENV,$ptascii("class231")) = (n_class)',
        'S_pair_globals.STORE[n_class] = DEFINED pvalue_class_now','$string_bytes(pvalue_class_now) = ('+other+')',
        '$code_at(S_pair.CODE,n_unit) = (pcode)','$code_expression(pcode.EXPRESSIONS,pcpath) = ((z,false))',
        '$code_expression(pcode.EXPRESSIONS,pcpath ++ [PCFIELD 1]) = ((z_member,false))',
        '$compiled_read(S_pair,PORIGIN n_unit (pcpath ++ [PCFIELD 0])) = eps',
        '~$class_constant_string_capture_source(S_pair,porigin_site,'+child+',z)',
        '$class_named(S_pair.CLASSNAMES,$ptlc('+child+')) = (porigin_class)',
        '$class_constant_lookup(S_pair,porigin_class,$ptascii("A"),|S_pair.CLASSES|) = (pclassconstantdesc)',
        'pclassconstantdesc.OWNERNAME = '+base,'pclassconstantdesc.FOLDED',
        '$class_constant_cv_rvalue_source(S_pair,pclassconstantdesc.ORIGIN,'+child+',$ptascii("A"),z)',
        '$class_constant_cv_rvalue_entry(S_pair,S_pair.RESULT,expression_class,KNOWN (PSTRING '+child+'),z,ptask_tail*) = (pclassconstantdesc)',
        '$call_task_valid(S_pair,CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING '+child+')) z)','$call_descriptors_valid(S_pair)',
        '~$class_constant_notice_valid(S_pair,pclassconstantdesc.ORIGIN,'+child+',$ptascii("A"),z)',
        '~$class_constant_notice_protected(S_pair,pclassconstantdesc.ORIGIN)',
        '$class_constant_cv_rvalue_source(S_pair,pclassconstantdesc.ORIGIN,'+base+',$ptascii("A"),z)',
        '$class_constant_cv_rvalue_entry(S_pair,S_pair.RESULT,expression_class,KNOWN (PSTRING '+base+'),z,ptask_tail*) = eps',
        '$class_constant_cv_rvalue_entry(S_pair,REFERENCE n_class,expression_class,KNOWN (PSTRING '+child+'),z,ptask_tail*) = eps',
        '$class_constant_cv_rvalue_entry(S_pair,KNOWN PNULL,expression_class,KNOWN (PSTRING '+child+'),z,ptask_tail*) = eps',
        '$class_constant_cv_rvalue_entry(S_pair,S_pair.RESULT,expression_class,KNOWN (PSTRING '+child+'),z,DISCARD :: ptask_tail*) = eps',
        'S_missing = S_pair[.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING '+child+')) z) :: ptask_tail*]',
        '$class_constant_cv_rvalue_entry(S_missing,S_pair.RESULT,expression_class,KNOWN (PSTRING '+child+'),z,ptask_tail*) = eps',
        '~$call_task_valid(S_missing,CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING '+child+')) z)',
        '~$class_constant_cv_rvalue_source(S_pair,pclassconstantdesc.ORIGIN,'+child+',$ptascii("A"),$(z + 1))',
        'S_warn_one = $drive_steps(S_pair,1)','S_warn_one.COMPLETION = BUDGET','S_warn = S_warn_one[.COMPLETION = NORMAL]',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN '+child+' $ptascii("A") z',
        '$error_call_valid(S_warn,perrorcall)','$call_task_valid(S_warn,perrorcall.RESUME)',
        '$task_nodes(perrorcall.RESUME) = eps','$class_constant_notice_protected(S_warn,pclassconstantdesc.ORIGIN)',
        'S_resume = $ccn_pause(S_warn,1,30000)','$ccn_ready(S_resume,1)',
        '$ccn_output(S_resume.EVENTS) = $ptascii("M|Ha|")',
        'S_resume.TODO = perrorcall.RESUME :: ptask_resume*',
        'S_resume_globals = $global_table_view(S_resume)','$lookup(S_resume_globals.ENV,$ptascii("member231")) = (n_member)',
        'S_resume_globals.STORE[n_member] = DEFINED pvalue_member_now','$string_bytes(pvalue_member_now) = ($ptascii("B"))',
        '$class_named(S_resume.CLASSNAMES,$ptlc('+other+')) = (porigin_other)',
        '$class_constant_lookup(S_resume,porigin_other,$ptascii("B"),|S_resume.CLASSES|) = (pclassconstantdesc_other)',
        '$class_constant_notice_valid(S_resume,pclassconstantdesc.ORIGIN,'+child+',$ptascii("A"),z)',
        '~$class_constant_notice_valid(S_resume[.RESULT = KNOWN (PSTRING $ptascii("A"))],pclassconstantdesc.ORIGIN,'+base+',$ptascii("A"),z)',
        '~$class_constant_notice_valid(S_resume[.RESULT = KNOWN (PSTRING $ptascii("B"))],pclassconstantdesc_other.ORIGIN,'+other+',$ptascii("B"),z)',
        'S_metadata_only = S_resume[.ENV = eps][.STORE = eps][.OBJECTS = eps][.ALLOCATIONS = eps]',
        '$class_constant_notice_valid(S_metadata_only,pclassconstantdesc.ORIGIN,'+child+',$ptascii("A"),z)',
        'S_value_one = $drive_steps(S_resume,1)','S_value_one.COMPLETION = BUDGET','S_value = S_value_one[.COMPLETION = NORMAL]',
        'S_value.RESULT = KNOWN (PINT 7)','S_value.EVENTS = S_resume.EVENTS',
        'S_second = $cv_rvalue_pause(S_value,true,30000)','$cv_rvalue_ready(S_second,true)',
        'S_second.TODO = (CLASS_CONST_MEMBER expression_second (KNOWN (PSTRING '+other+')) z_second) :: (CLASS_CONST_CAPTURE porigin_second (KNOWN (PSTRING '+other+')) z_second) :: ptask_second*',
        '$ccn_output(S_second.EVENTS) = $ptascii("M|Ha|O|7|M|")',
        'S_second.RESULT = KNOWN pvalue_second','$string_bytes(pvalue_second) = ($ptascii("B"))',
        '$class_constant_cv_rvalue_entry(S_second,S_second.RESULT,expression_second,KNOWN (PSTRING '+other+'),z_second,ptask_second*) = (pclassconstantdesc_other)',
        'S_done = $drive_steps(S_second,30000)','S_done.COMPLETION = NORMAL',
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
