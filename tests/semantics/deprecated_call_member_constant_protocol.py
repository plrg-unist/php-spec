#!/usr/bin/env python3
"""Check completed USER member calls and captured returned names."""
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
SOURCE=ROOT/'tests/semantics/deprecated_call_member_constant/call-member.php'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quoted=lambda s:'$base64('+json.dumps(base64.b64encode(s.encode()).decode())+')'
SELECTED=FETCH_SELECTED+r'''
dec $call_member_ready(pstate) : bool
def $call_member_ready(S) = true
  -- if S.TODO = (CLASS_CONST_MEMBER name poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES,porigin) = (NExprClassConstFetch name (NExprFuncCall name_function (SEQUENCE eps) metadata_call) metadata)
def $call_member_ready(S) = false -- otherwise
dec $call_member_pause(pstate,nat) : pstate
def $call_member_pause(S,n) = S -- if $call_member_ready(S)
def $call_member_pause(S,n) = $call_member_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$call_member_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $call_member_pause(S,n) = S -- otherwise
'''

def fields(fixture):
    expected=json.loads((SOURCE.parent/'cases.json').read_text())['call-member']['stdout']
    base=quoted('Ns227Call\\Base227');function=quoted('Ns227Call\\member227')
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(SOURCE)).decode())+')',
        'S_start.COMPLETION = BUDGET','S_pair = $call_member_pause(S_start[.COMPLETION = NORMAL],30000)','$call_member_ready(S_pair)',
        'S_pair.TODO = (CLASS_CONST_MEMBER name poperand z) :: (CLASS_CONST_CAPTURE porigin_site poperand z) :: ptask_tail*',
        'poperand = KNOWN (PSTRING '+base+')','porigin_site = PORIGIN n_unit pcpath',
        '$origin_node(S_pair.SOURCES,porigin_site) = (NExprClassConstFetch name (NExprFuncCall name_function (SEQUENCE eps) metadata_call) metadata)',
        'S_pair.CURRENT = eps','$ccn_output(S_pair.EVENTS) = $ptascii("O|M|")',
        'S_read = $resolve_at(S_pair,S_pair.RESULT,z)','S_read.RESULT = KNOWN pvalue_member','$string_bytes(pvalue_member) = ($ptascii("A"))',
        '$code_at(S_read.CODE,n_unit) = (pcode)','$code_expression(pcode.EXPRESSIONS,pcpath) = ((z,false))',
        'pcpath_member = pcpath ++ [PCFIELD 1]','$code_expression(pcode.EXPRESSIONS,pcpath_member) = ((z_member,false))',
        '$compiled_read(S_read,PORIGIN n_unit pcpath_member) = eps',
        '$code_name(pcode.NAMES,pcpath_member) = (('+function+',eps))',
        '$callable_at(S_read.CALLABLES,$ptlc('+function+')) = (porigin_function)',
        '$function_at(S_read.FUNCTIONS,porigin_function) = (pfunction)',
        '$parameter_named_callback_source(S_read,pfunction)','pfunction.SIGNATURE.PARAMETERS = eps',
        '~pfunction.SIGNATURE.BYREF','~$function_generator(S_read,pfunction)',
        '$call_selected_valid(S_read,porigin_function,(PORIGIN n_unit pcpath_member))',
        '$class_named(S_read.CLASSNAMES,$ptlc('+base+')) = (porigin_base)',
        '$class_constant_lookup(S_read,porigin_base,$ptascii("A"),|S_read.CLASSES|) = (pclassconstantdesc_a)',
        '$class_constant_lookup(S_read,porigin_base,$ptascii("B"),|S_read.CLASSES|) = (pclassconstantdesc_b)',
        'pclassconstantdesc_a.FOLDED','pclassconstantdesc_b.FOLDED',
        '$class_constant_notice_valid(S_read,pclassconstantdesc_a.ORIGIN,'+base+',$ptascii("A"),z)',
        '~$class_constant_notice_valid(S_read,pclassconstantdesc_b.ORIGIN,'+base+',$ptascii("B"),z)',
        '~$class_constant_notice_valid(S_read[.FUNCTIONS = eps],pclassconstantdesc_a.ORIGIN,'+base+',$ptascii("A"),z)',
        '~$class_constant_notice_valid(S_read[.CALLABLES = eps],pclassconstantdesc_a.ORIGIN,'+base+',$ptascii("A"),z)',
        'pcode_fallback = pcode[.NAMES = (CODENAME pcpath_member '+function+' ($ptascii("fallback227"))) :: pcode.NAMES]',
        'S_fallback = S_read[.CODE = [pcode_fallback]]',
        '$call_selected_valid(S_fallback,porigin_function,(PORIGIN n_unit pcpath_member))',
        '~$class_constant_notice_valid(S_fallback,pclassconstantdesc_a.ORIGIN,'+base+',$ptascii("A"),z)',
        'pcode_child_fold = pcode[.EXPRESSIONS = (CODEEXPR pcpath_member z_member true) :: pcode.EXPRESSIONS]',
        '~$class_constant_notice_valid(S_read[.CODE = [pcode_child_fold]],pclassconstantdesc_a.ORIGIN,'+base+',$ptascii("A"),z)',
        '~$class_constant_notice_valid(S_read,pclassconstantdesc_a.ORIGIN,'+base+',$ptascii("A"),$(z + 1))',
        '~$class_constant_notice_protected(S_read,pclassconstantdesc_a.ORIGIN)',
        '$call_descriptors_valid(S_pair)',
        'S_warn_one = $drive_steps(S_pair,1)','S_warn_one.COMPLETION = BUDGET','S_warn = S_warn_one[.COMPLETION = NORMAL]',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc_a.ORIGIN '+base+' $ptascii("A") z',
        '$error_call_valid(S_warn,perrorcall)','$task_nodes(perrorcall.RESUME) = eps',
        '$class_constant_notice_protected(S_warn,pclassconstantdesc_a.ORIGIN)',
        'S_inner = $call_member_pause(S_warn,30000)','$call_member_ready(S_inner)',
        'S_inner.TODO = (CLASS_CONST_MEMBER name_inner poperand_inner z_inner) :: (CLASS_CONST_CAPTURE porigin_inner poperand_inner z_inner) :: ptask_inner*',
        'porigin_inner = PORIGIN n_unit pcpath_inner','pcpath_inner =/= pcpath',
        'S_inner.CURRENT = (pcallcontext_handler)','pcallcontext_handler.FUNCTION =/= porigin_function',
        '$ccn_output(S_inner.EVENTS) = $ptascii("O|M|H|N|M|")',
        'S_inner_read = $resolve_at(S_inner,S_inner.RESULT,z_inner)','S_inner_read.RESULT = KNOWN pvalue_inner',
        '$string_bytes(pvalue_inner) = ($ptascii("A"))',
        '$call_selected_valid(S_inner_read,porigin_function,(PORIGIN n_unit (pcpath_inner ++ [PCFIELD 1])))',
        '$class_constant_notice_valid(S_inner_read,pclassconstantdesc_a.ORIGIN,'+base+',$ptascii("A"),z_inner)',
        '$class_constant_notice_protected(S_inner,pclassconstantdesc_a.ORIGIN)',
        'S_inner_one = $drive_steps(S_inner,1)','S_inner_one.COMPLETION = BUDGET','S_inner_value = S_inner_one[.COMPLETION = NORMAL]',
        'S_inner_value.RESULT = KNOWN (PINT 7)','S_inner_value.EVENTS = S_inner.EVENTS',
        'S_resume = $ccn_pause(S_inner_value,1,30000)','$ccn_ready(S_resume,1)',
        'S_resume.TODO = (DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc_a.ORIGIN '+base+' $ptascii("A") z) :: ptask_resume*',
        '$ccn_output(S_resume.EVENTS) = $ptascii("O|M|H|N|M|7|")','S_resume.CURRENT = eps',
        'S_globals = $global_table_view(S_resume)','$lookup(S_globals.ENV,$ptascii("return227")) = (n_return)',
        'S_globals.STORE[n_return] = DEFINED pvalue_now','$string_bytes(pvalue_now) = ($ptascii("B"))',
        '$class_constant_notice_valid(S_resume,pclassconstantdesc_a.ORIGIN,'+base+',$ptascii("A"),z)',
        '~$class_constant_notice_valid(S_resume[.RESULT = KNOWN (PSTRING $ptascii("B"))],pclassconstantdesc_b.ORIGIN,'+base+',$ptascii("B"),z)',
        'S_value_one = $drive_steps(S_resume,1)','S_value_one.COMPLETION = BUDGET','S_value = S_value_one[.COMPLETION = NORMAL]',
        'S_value.RESULT = KNOWN (PINT 7)','~$class_constant_notice_protected(S_value,pclassconstantdesc_a.ORIGIN)',
        'S_second = $call_member_pause(S_value,30000)','$call_member_ready(S_second)',
        'S_second.TODO = (CLASS_CONST_MEMBER name_second poperand_second z_second) :: (CLASS_CONST_CAPTURE porigin_second poperand_second z_second) :: ptask_second*',
        'S_second_read = $resolve_at(S_second,S_second.RESULT,z_second)','S_second_read.RESULT = KNOWN pvalue_second',
        '$string_bytes(pvalue_second) = ($ptascii("B"))',
        '$ccn_output(S_second.EVENTS) = $ptascii("O|M|H|N|M|7|7|F|M|")',
        '$class_constant_notice_valid(S_second_read,pclassconstantdesc_b.ORIGIN,'+base+',$ptascii("B"),z_second)',
        '~$class_constant_notice_valid(S_second_read,pclassconstantdesc_a.ORIGIN,'+base+',$ptascii("A"),z_second)',
        'S_done = $drive_steps(S_second,30000)','S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = '+quoted(expected),'S_done.CLASSCONSTANTCACHE = eps',
        'S_done.CLASSCONSTANTHISTORY = S_read.CLASSCONSTANTHISTORY',
        '~$class_constant_notice_protected(S_done,pclassconstantdesc_a.ORIGIN)',
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
