#!/usr/bin/env python3
"""Check current, saved and nested quiet CV constant members."""
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
SOURCE=ROOT/'tests/semantics/deprecated_cv_member_constant/member-selector.php'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quoted=lambda s:'$base64('+json.dumps(base64.b64encode(s.encode()).decode())+')'
SELECTED=FETCH_SELECTED+r'''
dec $member_cv_ready(pstate,nat) : bool
def $member_cv_ready(S,n) = true
  -- if S.TODO = (CLASS_CONST_MEMBER name poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES,porigin) = (NExprClassConstFetch name (NExprVariable (BYTES text) metadata_variable) metadata)
  -- if (n = 0 /\ $base64(text) = $ptascii("member222")) \/ (n = 1 /\ $base64(text) = $ptascii("inside"))
def $member_cv_ready(S,n) = false -- otherwise
dec $member_cv_pause(pstate,nat,nat) : pstate
def $member_cv_pause(S,n_mode,n) = S -- if $member_cv_ready(S,n_mode)
def $member_cv_pause(S,n_mode,n) = $member_cv_pause(S_next[.COMPLETION = NORMAL],n_mode,$nabs($(n - 1)))
  -- if ~$member_cv_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $member_cv_pause(S,n_mode,n) = S -- otherwise
'''


def fields(fixture):
    expected=json.loads((SOURCE.parent/'cases.json').read_text())['member-selector']['stdout']
    child=quoted('Ns222Select\\Child222');base=quoted('Ns222Select\\Base222')
    prefix='Constant Ns222Select\\Base222::A is deprecated|16384|'
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(SOURCE)).decode())+')',
        'S_start.COMPLETION = BUDGET','S_member = $member_cv_pause(S_start[.COMPLETION = NORMAL],0,30000)',
        '$member_cv_ready(S_member,0)',
        'S_member.TODO = (CLASS_CONST_MEMBER name poperand_class z) :: (CLASS_CONST_CAPTURE porigin_site poperand_class z) :: ptask_tail*',
        'poperand_class = KNOWN (PSTRING '+child+')','S_member.CURRENT = eps','S_member.CONSTCONTEXT = eps',
        'S_member.RESULT = VARIABLE $ptascii("member222") z_variable',
        'S_read = $resolve_at(S_member,S_member.RESULT,z)','S_read.COMPLETION = NORMAL',
        'S_read.RESULT = KNOWN pvalue_member','$string_bytes(pvalue_member) = ($ptascii("A"))',
        '$origin_node(S_member.SOURCES,porigin_site) = (NExprClassConstFetch name expression_member metadata)',
        'expression_member = NExprVariable (BYTES text_variable) metadata_variable',
        '$class_constant_selected_valid(S_read,name,poperand_class)',
        '~$class_constant_selected_valid(S_read,name,KNOWN (PSTRING '+base+'))',
        '$class_named(S_read.CLASSNAMES,$ptlc('+child+')) = (porigin_requested)',
        '$class_constant_lookup(S_read,porigin_requested,$ptascii("A"),|S_read.CLASSES|) = (pclassconstantdesc)',
        '$class_constant_lookup(S_read,porigin_requested,$ptascii("B"),|S_read.CLASSES|) = (pclassconstantdesc_b)',
        'pclassconstantdesc.ORIGIN =/= pclassconstantdesc_b.ORIGIN','pclassconstantdesc.OWNER = pclassconstantdesc_b.OWNER',
        'pclassconstantdesc.OWNERNAME = '+base,r'pclassconstantdesc.FOLDED /\ pclassconstantdesc_b.FOLDED',
        '$class_constant_member_selected(S_read,expression_member,$ptascii("B"))',
        '$class_constant_member_cv_source(S_read,pclassconstantdesc.ORIGIN,'+child+',$ptascii("A"),z)',
        '$class_constant_member_cv_capture(S_read,pclassconstantdesc.ORIGIN,'+child+',$ptascii("A"),z)',
        '$class_constant_notice_valid(S_read,pclassconstantdesc.ORIGIN,'+child+',$ptascii("A"),z)',
        '~$class_constant_notice_valid(S_member,pclassconstantdesc.ORIGIN,'+child+',$ptascii("A"),z)',
        '~$class_constant_cv_capture(S_read,pclassconstantdesc.ORIGIN,'+child+',$ptascii("A"),z)',
        '$class_constant_member_cv_source(S_read,pclassconstantdesc_b.ORIGIN,'+child+',$ptascii("B"),z)',
        '~$class_constant_member_cv_capture(S_read,pclassconstantdesc_b.ORIGIN,'+child+',$ptascii("B"),z)',
        '~$class_constant_notice_valid(S_read,pclassconstantdesc_b.ORIGIN,'+child+',$ptascii("B"),z)',
        '~$class_constant_notice_valid(S_read,pclassconstantdesc.ORIGIN,'+base+',$ptascii("A"),z)',
        '$call_descriptors_valid(S_member)',
        'S_warn_one = $drive_steps(S_member,1)','S_warn_one.COMPLETION = BUDGET','S_warn = S_warn_one[.COMPLETION = NORMAL]',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN ptbytes_class ptbytes_member z',
        'ptbytes_class = '+child,'ptbytes_member = $ptascii("A")','S_warn.RESULT = KNOWN PNULL',
        '$error_call_valid(S_warn,perrorcall)','$call_descriptors_valid(S_warn)',
        '$task_nodes(perrorcall.RESUME) = eps','$class_constant_notice_protected(S_warn,pclassconstantdesc.ORIGIN)',
        'S_inner = $member_cv_pause(S_warn,1,30000)','$member_cv_ready(S_inner,1)',
        'S_inner.TODO = (CLASS_CONST_MEMBER name_inner poperand_inner z_inner) :: (CLASS_CONST_CAPTURE porigin_inner poperand_inner z_inner) :: ptask_inner*',
        r'z_inner =/= z /\ porigin_inner =/= porigin_site','poperand_inner = poperand_class',
        'S_inner.CURRENT = (pcallcontext)','$function_at(S_inner.FUNCTIONS,pcallcontext.FUNCTION) = (pfunction)',
        'pfunction.NAME = '+quoted('Ns222Select\\notice222'),
        'S_inner_read = $resolve_at(S_inner,S_inner.RESULT,z_inner)','S_inner_read.RESULT = KNOWN pvalue_inner',
        '$string_bytes(pvalue_inner) = ($ptascii("A"))',
        '$class_constant_notice_protected(S_inner_read,pclassconstantdesc.ORIGIN)',
        '$class_constant_cv_pending(CLASS_CONST_MEMBER name_inner poperand_inner z_inner) = eps',
        '$class_constant_member_cv_source(S_inner_read,pclassconstantdesc.ORIGIN,ptbytes_class,ptbytes_member,z_inner)',
        '$class_constant_member_cv_capture(S_inner_read,pclassconstantdesc.ORIGIN,ptbytes_class,ptbytes_member,z_inner)',
        '$class_constant_notice_valid(S_inner_read,pclassconstantdesc.ORIGIN,ptbytes_class,ptbytes_member,z_inner)',
        '$ccn_output(S_inner.EVENTS) = '+quoted(prefix+'I|'),
        '$call_descriptors_valid(S_inner)',
        'S_inner_one = $drive_steps(S_inner,1)','S_inner_one.COMPLETION = BUDGET',
        'S_after_inner = S_inner_one[.COMPLETION = NORMAL]','S_after_inner.RESULT = KNOWN (PINT 7)',
        'S_after_inner.EVENTS = S_inner.EVENTS','$class_constant_notice_protected(S_after_inner,pclassconstantdesc.ORIGIN)',
        'S_resume = $ccn_pause(S_after_inner,1,30000)','$ccn_ready(S_resume,1)',
        'S_resume.TODO = (DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN ptbytes_class ptbytes_member z) :: ptask_resume*',
        'S_resume.RESULT = KNOWN PNULL','$ccn_output(S_resume.EVENTS) = '+quoted(prefix+'I|7|'),
        'S_globals = $global_table_view(S_resume)','$lookup(S_globals.ENV,$ptascii("member222")) = (n_member)',
        'S_globals.STORE[n_member] = DEFINED pvalue_current','$string_bytes(pvalue_current) = ($ptascii("B"))',
        '$class_constant_member_cv_source(S_resume,pclassconstantdesc.ORIGIN,ptbytes_class,ptbytes_member,z)',
        '$class_constant_notice_valid(S_resume,pclassconstantdesc.ORIGIN,ptbytes_class,ptbytes_member,z)',
        '$class_constant_member_cv_source(S_resume,pclassconstantdesc_b.ORIGIN,ptbytes_class,$ptascii("B"),z)',
        '~$class_constant_notice_valid(S_resume,pclassconstantdesc_b.ORIGIN,ptbytes_class,$ptascii("B"),z)',
        '~$class_constant_notice_valid(S_resume[.RESULT = KNOWN (PSTRING $ptascii("B"))],pclassconstantdesc_b.ORIGIN,ptbytes_class,$ptascii("B"),z)',
        '~$class_constant_notice_valid(S_resume,pclassconstantdesc.ORIGIN,ptbytes_class,ptbytes_member,$(z + 1))',
        '$call_descriptors_valid(S_resume)',
        'S_value_one = $drive_steps(S_resume,1)','S_value_one.COMPLETION = BUDGET','S_value = S_value_one[.COMPLETION = NORMAL]',
        'S_value.RESULT = KNOWN (PINT 7)','S_value.EVENTS = S_resume.EVENTS',
        'S_value.CLASSCONSTANTCACHE = S_resume.CLASSCONSTANTCACHE','S_value.CLASSCONSTANTHISTORY = S_resume.CLASSCONSTANTHISTORY',
        '~$class_constant_notice_protected(S_value,pclassconstantdesc.ORIGIN)',
        'S_b = $member_cv_pause(S_value,0,30000)','$member_cv_ready(S_b,0)',
        'S_b.TODO = (CLASS_CONST_MEMBER name_b poperand_b z_b) :: (CLASS_CONST_CAPTURE porigin_b poperand_b z_b) :: ptask_b*',
        r'poperand_b = poperand_class /\ porigin_b =/= porigin_site',
        'S_b_read = $resolve_at(S_b,S_b.RESULT,z_b)','S_b_read.RESULT = KNOWN pvalue_b',
        '$string_bytes(pvalue_b) = ($ptascii("B"))',
        '$class_constant_notice_valid(S_b_read,pclassconstantdesc_b.ORIGIN,ptbytes_class,$ptascii("B"),z_b)',
        '~$class_constant_notice_valid(S_b_read,pclassconstantdesc.ORIGIN,ptbytes_class,$ptascii("A"),z_b)',
        'S_done = $drive_steps(S_b,30000)','S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = '+quoted(expected),'S_done.CLASSCONSTANTCACHE = eps',
        '~$class_constant_notice_protected(S_done,pclassconstantdesc.ORIGIN)',
        '~$class_constant_notice_protected(S_done,pclassconstantdesc_b.ORIGIN)',
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
