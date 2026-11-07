#!/usr/bin/env python3
"""Check immutable compiled member authority and protected reentry."""
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
SOURCE=ROOT/'tests/semantics/deprecated_pooled_member_constant/pooled-member.php'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quoted=lambda s:'$base64('+json.dumps(base64.b64encode(s.encode()).decode())+')'
SELECTED=FETCH_SELECTED+r'''
dec $pooled_pair_ready(pstate) : bool
def $pooled_pair_ready(S) = true
  -- if S.TODO = (CLASS_CONST_MEMBER name poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES,porigin) = (NExprClassConstFetch name expression_member metadata)
  -- if $ppscoped_named(name) /\ ~$ppscoped_keyword(name)
def $pooled_pair_ready(S) = false -- otherwise
dec $pooled_pair_pause(pstate,nat) : pstate
def $pooled_pair_pause(S,n) = S -- if $pooled_pair_ready(S)
def $pooled_pair_pause(S,n) = $pooled_pair_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$pooled_pair_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $pooled_pair_pause(S,n) = S -- otherwise
'''

def fields(fixture):
    expected=json.loads((SOURCE.parent/'cases.json').read_text())['pooled-member']['stdout']
    child=quoted('Ns225Pool\\Child225');base=quoted('Ns225Pool\\Base225')
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(SOURCE)).decode())+')',
        'S_start.COMPLETION = BUDGET','S_pair = $pooled_pair_pause(S_start[.COMPLETION = NORMAL],30000)','$pooled_pair_ready(S_pair)',
        'S_pair.TODO = (CLASS_CONST_MEMBER name poperand z) :: (CLASS_CONST_CAPTURE porigin_site poperand z) :: ptask_tail*',
        'poperand = KNOWN (PSTRING '+child+')','porigin_site = PORIGIN n_unit pcpath',
        '$origin_node(S_pair.SOURCES,porigin_site) = (NExprClassConstFetch name expression_member metadata)',
        'expression_member = NScalarString (BYTES text_member) metadata_member',
        '$code_at(S_pair.CODE,n_unit) = (pcode)','$code_expression(pcode.EXPRESSIONS,pcpath) = ((z,false))',
        'pcpath_member = pcpath ++ [PCFIELD 1]','$code_expression(pcode.EXPRESSIONS,pcpath_member) = ((z_member,true))',
        '$compiled_read(S_pair,PORIGIN n_unit pcpath_member) = (PSTRING $ptascii("VALUE"))',
        'S_read = $resolve_at(S_pair,S_pair.RESULT,z)','S_read.RESULT = KNOWN pvalue_member',
        '$string_bytes(pvalue_member) = ($ptascii("VALUE"))',
        '$class_named(S_read.CLASSNAMES,$ptlc('+child+')) = (porigin_child)',
        '$class_constant_lookup(S_read,porigin_child,$ptascii("VALUE"),|S_read.CLASSES|) = (pclassconstantdesc)',
        '$class_constant_lookup(S_read,porigin_child,$ptascii("OTHER"),|S_read.CLASSES|) = (pclassconstantdesc_other)',
        'pclassconstantdesc.OWNERNAME = '+base,'pclassconstantdesc.FOLDED',
        '$class_constant_deprecated(S_read,pclassconstantdesc_other)',
        '$class_constant_notice_valid(S_read,pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        '$class_constant_notice_valid(S_read[.RESULT = KNOWN PNULL],pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        '~$class_constant_notice_valid(S_read,pclassconstantdesc_other.ORIGIN,'+child+',$ptascii("OTHER"),z)',
        '~$class_constant_notice_valid(S_read[.RESULT = KNOWN (PSTRING $ptascii("OTHER"))],pclassconstantdesc_other.ORIGIN,'+child+',$ptascii("OTHER"),z)',
        '~$class_constant_notice_valid(S_read,pclassconstantdesc.ORIGIN,'+base+',$ptascii("VALUE"),z)',
        '~$class_constant_notice_valid(S_read,pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),$(z + 1))',
        '~$class_constant_notice_valid(S_read[.ORIGIN = (PORIGIN n_unit pcpath_member)],pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        '~$class_constant_notice_valid(S_read[.CONSTCONTEXT = ({ORIGIN pclassconstantdesc.ORIGIN,LINE z,FACTS eps})],pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        'pcode_bad_fold = pcode[.EXPRESSIONS = (CODEEXPR pcpath z true) :: pcode.EXPRESSIONS]',
        '~$class_constant_notice_valid(S_read[.CODE = [pcode_bad_fold]],pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        'pcode_bad_child = pcode[.EXPRESSIONS = (CODEEXPR pcpath_member z_member false) :: pcode.EXPRESSIONS]',
        '~$class_constant_notice_valid(S_read[.CODE = [pcode_bad_child]],pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        'pclassconstantdesc_other.INITIALIZER = PORIGIN n_unit pcpath_other',
        'S_wrong_pool = S_read[.POOLS = [{UNIT n_unit,CONSTANTS [PCONSTANT pcpath_other (PSTRING $ptascii("VALUE"))]}]]',
        '$compiled_read(S_wrong_pool,PORIGIN n_unit pcpath_other) = (PSTRING $ptascii("VALUE"))',
        '$compiled_read(S_wrong_pool,PORIGIN n_unit pcpath_member) = eps',
        '~$class_constant_notice_valid(S_wrong_pool,pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        'S_read.CLASSCONSTANTCACHE = eps','~$class_constant_notice_protected(S_read,pclassconstantdesc.ORIGIN)',
        '$call_descriptors_valid(S_pair)',
        'S_warn_one = $drive_steps(S_pair,1)','S_warn_one.COMPLETION = BUDGET','S_warn = S_warn_one[.COMPLETION = NORMAL]',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN '+child+' $ptascii("VALUE") z',
        '$task_nodes(perrorcall.RESUME) = eps','$error_call_valid(S_warn,perrorcall)','$call_descriptors_valid(S_warn)',
        '$class_constant_notice_protected(S_warn,pclassconstantdesc.ORIGIN)',
        'S_inner = $pooled_pair_pause(S_warn,30000)','$pooled_pair_ready(S_inner)',
        'S_inner.TODO = (CLASS_CONST_MEMBER name_inner poperand_inner z_inner) :: (CLASS_CONST_CAPTURE porigin_inner poperand_inner z_inner) :: ptask_inner*',
        'porigin_inner = PORIGIN n_unit pcpath_inner','S_inner.CURRENT = (pcallcontext_handler)',
        'pcpath_inner =/= pcpath','poperand_inner = KNOWN (PSTRING '+child+')',
        '$origin_node(S_inner.SOURCES,porigin_inner) = (NExprClassConstFetch name_inner (NExprBinaryOpConcat expression_left expression_right metadata_concat) metadata_inner)',
        '$compiled_read(S_inner,PORIGIN n_unit (pcpath_inner ++ [PCFIELD 1])) = (PSTRING $ptascii("VALUE"))',
        '$code_at(S_inner.CODE,n_unit) = (pcode_inner)','$code_expression(pcode_inner.EXPRESSIONS,pcpath_inner) = ((z_inner,false))',
        '$class_constant_notice_protected(S_inner,pclassconstantdesc.ORIGIN)',
        '$class_constant_notice_valid(S_inner,pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z_inner)',
        '$ccn_output(S_inner.EVENTS) = $ptascii("B|H|N|")',
        'S_inner_one = $drive_steps(S_inner,1)','S_inner_one.COMPLETION = BUDGET','S_inner_value = S_inner_one[.COMPLETION = NORMAL]',
        'S_inner_value.RESULT = KNOWN (PINT 7)','S_inner_value.EVENTS = S_inner.EVENTS',
        '$class_constant_notice_protected(S_inner_value,pclassconstantdesc.ORIGIN)',
        'S_resume = $ccn_pause(S_inner_value,1,30000)','$ccn_ready(S_resume,1)',
        'S_resume.TODO = (DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN '+child+' $ptascii("VALUE") z) :: ptask_resume*',
        '$ccn_output(S_resume.EVENTS) = $ptascii("B|H|N|7|")',
        '$class_constant_notice_valid(S_resume,pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        '$class_constant_notice_valid(S_resume[.RESULT = KNOWN (PSTRING $ptascii("OTHER"))],pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        '~$class_constant_notice_valid(S_resume,pclassconstantdesc_other.ORIGIN,'+child+',$ptascii("OTHER"),z)',
        'S_value_one = $drive_steps(S_resume,1)','S_value_one.COMPLETION = BUDGET','S_value = S_value_one[.COMPLETION = NORMAL]',
        'S_value.RESULT = KNOWN (PINT 7)','~$class_constant_notice_protected(S_value,pclassconstantdesc.ORIGIN)',
        'S_second = $pooled_pair_pause(S_value,30000)','$pooled_pair_ready(S_second)',
        'S_second.TODO = (CLASS_CONST_MEMBER name_second poperand_second z_second) :: (CLASS_CONST_CAPTURE porigin_second poperand_second z_second) :: ptask_second*',
        'porigin_second = PORIGIN n_unit pcpath_second','S_second.CURRENT = eps','pcpath_second =/= pcpath_inner',
        '$origin_node(S_second.SOURCES,porigin_second) = (NExprClassConstFetch name_second (NExprBinaryOpConcat expression_second_left expression_second_right metadata_second_concat) metadata_second)',
        '$compiled_read(S_second,PORIGIN n_unit (pcpath_second ++ [PCFIELD 1])) = (PSTRING $ptascii("VALUE"))',
        '$class_constant_notice_valid(S_second,pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z_second)',
        'S_second_one = $drive_steps(S_second,1)','S_second_one.COMPLETION = BUDGET','S_second_warn = S_second_one[.COMPLETION = NORMAL]',
        'S_second_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_second_warn*',
        'perrorcall_second.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN '+child+' $ptascii("VALUE") z_second',
        '$error_call_valid(S_second_warn,perrorcall_second)',
        'S_done = $drive_steps(S_second_warn,30000)','S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = '+quoted(expected),'S_done.CLASSCONSTANTCACHE = eps',
        'S_done.CLASSCONSTANTHISTORY = S_read.CLASSCONSTANTHISTORY',
        '~$class_constant_notice_protected(S_done,pclassconstantdesc.ORIGIN)',
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
