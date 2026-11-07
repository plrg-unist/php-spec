#!/usr/bin/env python3
"""Check genuine dual CV capture pairs and notice dispatch."""
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
SOURCE=ROOT/'tests/semantics/deprecated_dual_cv_constant/dual-selector.php'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quoted=lambda s:'$base64('+json.dumps(base64.b64encode(s.encode()).decode())+')'
SELECTED=FETCH_SELECTED+r'''
dec $dual_cv_ready(pstate) : bool
def $dual_cv_ready(S) = true
  -- if S.TODO = (CLASS_CONST_MEMBER expression_class poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES,porigin) = (NExprClassConstFetch (NExprVariable (BYTES text_class) metadata_class) (NExprVariable (BYTES text_member) metadata_member) metadata)
  -- if $base64(text_class) = $ptascii("class223") /\ $base64(text_member) = $ptascii("member223")
def $dual_cv_ready(S) = false -- otherwise
dec $dual_cv_pause(pstate,nat) : pstate
def $dual_cv_pause(S,n) = S -- if $dual_cv_ready(S)
def $dual_cv_pause(S,n) = $dual_cv_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$dual_cv_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $dual_cv_pause(S,n) = S -- otherwise
'''


def fields(fixture):
    expected=json.loads((SOURCE.parent/'cases.json').read_text())['dual-selector']['stdout']
    child=quoted('Ns223Select\\Child223');base=quoted('Ns223Select\\Base223');other=quoted('Ns223Select\\Other223')
    prefix='Constant Ns223Select\\Base223::A is deprecated|16384|'
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(SOURCE)).decode())+')',
        'S_start.COMPLETION = BUDGET','S_pair = $dual_cv_pause(S_start[.COMPLETION = NORMAL],30000)','$dual_cv_ready(S_pair)',
        'S_pair.TODO = (CLASS_CONST_MEMBER expression_class poperand_class z) :: (CLASS_CONST_CAPTURE porigin_site poperand_class z) :: ptask_tail*',
        'poperand_class = KNOWN (PSTRING '+child+')','S_pair.RESULT = VARIABLE $ptascii("member223") z_member',
        'S_read = $resolve_at(S_pair,S_pair.RESULT,z)','S_read.COMPLETION = NORMAL',
        'S_read.RESULT = KNOWN pvalue_member','$string_bytes(pvalue_member) = ($ptascii("A"))',
        '$class_constant_pair_head(S_read.TODO,porigin_site,expression_class,poperand_class,z)',
        '$class_constant_pairs_valid(S_read.TODO)',
        '$class_named(S_read.CLASSNAMES,$ptlc('+child+')) = (porigin_requested)',
        '$class_constant_lookup(S_read,porigin_requested,$ptascii("A"),|S_read.CLASSES|) = (pclassconstantdesc)',
        'pclassconstantdesc.OWNERNAME = '+base,'pclassconstantdesc.FOLDED',
        '$class_constant_dual_cv_source(S_read,pclassconstantdesc.ORIGIN,'+child+',$ptascii("A"),z)',
        '$class_constant_dual_cv_entry(S_read,expression_class,poperand_class,z,ptask_tail*) = (pclassconstantdesc)',
        '$class_constant_dual_cv_entry(S_read[.TODO = (CLASS_CONST_MEMBER expression_class poperand_class z) :: ptask_tail*],expression_class,poperand_class,z,ptask_tail*) = eps',
        '$class_constant_dual_cv_entry(S_read[.TODO = (CLASS_CONST_MEMBER expression_class poperand_class z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING '+base+')) z) :: ptask_tail*],expression_class,poperand_class,z,ptask_tail*) = eps',
        '$class_constant_dual_cv_entry(S_read[.TODO = (CLASS_CONST_MEMBER expression_class poperand_class z) :: (CLASS_CONST_CAPTURE pclassconstantdesc.ORIGIN poperand_class z) :: ptask_tail*],expression_class,poperand_class,z,ptask_tail*) = eps',
        '$class_constant_dual_cv_entry(S_read,expression_class,poperand_class,z,DISCARD :: ptask_tail*) = eps',
        '$class_constant_dual_cv_entry(S_read,expression_class,KNOWN (PSTRING '+other+'),z,ptask_tail*) = eps',
        '$class_constant_selected_valid(S_read,expression_class,KNOWN (PSTRING '+other+'))',
        'S_consumed = S_read[.TODO = ptask_tail*]',
        '$class_constant_dual_cv_entry(S_consumed,expression_class,poperand_class,z,ptask_tail*) = eps',
        '~$class_constant_notice_valid(S_read,pclassconstantdesc.ORIGIN,'+child+',$ptascii("A"),z)',
        '~$class_constant_notice_valid(S_consumed,pclassconstantdesc.ORIGIN,'+child+',$ptascii("A"),z)',
        '~$class_constant_notice_protected(S_read,pclassconstantdesc.ORIGIN)',
        'S_read.CLASSCONSTANTINIT = eps','$call_descriptors_valid(S_pair)',
        'S_warn_one = $drive_steps(S_pair,1)','S_warn_one.COMPLETION = BUDGET','S_warn = S_warn_one[.COMPLETION = NORMAL]',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN ptbytes_class ptbytes_member z',
        'ptbytes_class = '+child,'ptbytes_member = $ptascii("A")','S_warn.RESULT = KNOWN PNULL',
        'perrorcall.MESSAGE = '+quoted(prefix[:-7]),
        '$class_constant_notice_valid(S_warn,pclassconstantdesc.ORIGIN,ptbytes_class,ptbytes_member,z)',
        '$error_call_valid(S_warn,perrorcall)','$call_descriptors_valid(S_warn)',
        '$task_nodes(perrorcall.RESUME) = eps','$class_constant_notice_protected(S_warn,pclassconstantdesc.ORIGIN)',
        '$ccn_output(S_warn.EVENTS) = eps',
        'S_resume = $ccn_pause(S_warn,1,30000)','$ccn_ready(S_resume,1)',
        'S_resume.TODO = (DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN ptbytes_class ptbytes_member z) :: ptask_resume*',
        '$ccn_output(S_resume.EVENTS) = '+quoted(prefix),'S_resume.RESULT = KNOWN PNULL',
        'S_globals = $global_table_view(S_resume)','$lookup(S_globals.ENV,$ptascii("class223")) = (n_class)',
        '$lookup(S_globals.ENV,$ptascii("member223")) = (n_member)',
        'S_globals.STORE[n_class] = DEFINED pvalue_class_new','$string_bytes(pvalue_class_new) = ('+other+')',
        'S_globals.STORE[n_member] = DEFINED pvalue_member_new','$string_bytes(pvalue_member_new) = ($ptascii("B"))',
        '$class_constant_notice_valid(S_resume,pclassconstantdesc.ORIGIN,ptbytes_class,ptbytes_member,z)',
        '$class_named(S_resume.CLASSNAMES,$ptlc('+other+')) = (porigin_other)',
        '$class_constant_lookup(S_resume,porigin_other,$ptascii("B"),|S_resume.CLASSES|) = (pclassconstantdesc_other)',
        '$class_constant_dual_cv_source(S_resume,pclassconstantdesc_other.ORIGIN,'+other+',$ptascii("B"),z)',
        '~$class_constant_notice_valid(S_resume,pclassconstantdesc_other.ORIGIN,'+other+',$ptascii("B"),z)',
        '~$class_constant_notice_valid(S_resume[.RESULT = KNOWN (PSTRING $ptascii("B"))],pclassconstantdesc_other.ORIGIN,'+other+',$ptascii("B"),z)',
        '~$class_constant_notice_valid(S_resume,pclassconstantdesc.ORIGIN,ptbytes_class,ptbytes_member,$(z + 1))',
        '$call_descriptors_valid(S_resume)',
        'S_value_one = $drive_steps(S_resume,1)','S_value_one.COMPLETION = BUDGET','S_value = S_value_one[.COMPLETION = NORMAL]',
        'S_value.RESULT = KNOWN (PINT 7)','S_value.EVENTS = S_resume.EVENTS',
        'S_value.CLASSCONSTANTCACHE = S_resume.CLASSCONSTANTCACHE','S_value.CLASSCONSTANTHISTORY = S_resume.CLASSCONSTANTHISTORY',
        '~$class_constant_notice_protected(S_value,pclassconstantdesc.ORIGIN)',
        'S_other = $dual_cv_pause(S_value,30000)','$dual_cv_ready(S_other)',
        'S_other.TODO = (CLASS_CONST_MEMBER expression_class_other poperand_other z_other) :: (CLASS_CONST_CAPTURE porigin_other_site poperand_other z_other) :: ptask_other*',
        'poperand_other = KNOWN (PSTRING '+other+')',
        'S_other_read = $resolve_at(S_other,S_other.RESULT,z_other)','S_other_read.RESULT = KNOWN pvalue_other_member',
        '$string_bytes(pvalue_other_member) = ($ptascii("B"))',
        '$class_constant_dual_cv_entry(S_other_read,expression_class_other,poperand_other,z_other,ptask_other*) = (pclassconstantdesc_other)',
        'S_done = $drive_steps(S_other,30000)','S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = '+quoted(expected),'S_done.CLASSCONSTANTCACHE = eps',
        '~$class_constant_notice_protected(S_done,pclassconstantdesc.ORIGIN)',
        '~$class_constant_notice_protected(S_done,pclassconstantdesc_other.ORIGIN)',
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
