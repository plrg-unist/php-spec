#!/usr/bin/env python3
"""Check immutable compiled class authority and protected reentry."""
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
SOURCE=ROOT/'tests/semantics/deprecated_compiled_class_constant/compiled-class.php'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quoted=lambda s:'$base64('+json.dumps(base64.b64encode(s.encode()).decode())+')'
SELECTED=FETCH_SELECTED+r'''
dec $ccx_ready(pstate) : bool
def $ccx_ready(S) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class phpType20_member z) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES,porigin) = (NExprClassConstFetch expression_class phpType20_member metadata)
  -- if ~$method_receiver_is_variable(expression_class)
def $ccx_ready(S) = false -- otherwise
dec $ccx_pause(pstate,nat) : pstate
def $ccx_pause(S,n) = S -- if $ccx_ready(S)
def $ccx_pause(S,n) = $ccx_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$ccx_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $ccx_pause(S,n) = S -- otherwise
'''

def fields(fixture):
    expected=json.loads((SOURCE.parent/'cases.json').read_text())['compiled-class']['stdout']
    child=quoted('Ns226Pool\\Child226');base=quoted('Ns226Pool\\Base226');other=quoted('Ns226Pool\\Other226')
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(SOURCE)).decode())+')',
        'S_start.COMPLETION = BUDGET','S_select = $ccx_pause(S_start[.COMPLETION = NORMAL],30000)','$ccx_ready(S_select)',
        'S_select.TODO = (CLASS_CONST_CLASS expression_class phpType20_member z) :: ptask_tail*',
        'phpType20_member = NIdentifier (BYTES text_member) metadata_member','$base64(text_member) = $ptascii("VALUE")',
        'S_select.ORIGIN = (PORIGIN n_unit pcpath)',
        '$origin_node(S_select.SOURCES,PORIGIN n_unit pcpath) = (NExprClassConstFetch (NScalarString (BYTES text_class) metadata_class) phpType20_member metadata)',
        'expression_class = NScalarString (BYTES text_class) metadata_class',
        '$code_at(S_select.CODE,n_unit) = (pcode)','$code_expression(pcode.EXPRESSIONS,pcpath) = ((z,false))',
        'pcpath_class = pcpath ++ [PCFIELD 0]','$code_expression(pcode.EXPRESSIONS,pcpath_class) = ((z_class,true))',
        '$compiled_read(S_select,PORIGIN n_unit pcpath_class) = (PSTRING '+child+')',
        '$compiled_read(S_select,PORIGIN n_unit (pcpath ++ [PCFIELD 1])) = eps',
        '$class_constant_literal(S_select,expression_class)',
        '$class_constant_selected_valid(S_select,expression_class,KNOWN (PSTRING '+child+'))',
        '~$class_constant_selected_valid(S_select,expression_class,KNOWN (PSTRING '+other+'))',
        '$class_constant_compiled_member(S_select,PORIGIN n_unit (pcpath ++ [PCFIELD 1]),phpType20_member) = ($ptascii("VALUE"))',
        '$class_named(S_select.CLASSNAMES,$ptlc('+child+')) = (porigin_child)',
        '$class_named(S_select.CLASSNAMES,$ptlc('+other+')) = (porigin_other)',
        '$class_constant_lookup(S_select,porigin_child,$ptascii("VALUE"),|S_select.CLASSES|) = (pclassconstantdesc)',
        '$class_constant_lookup(S_select,porigin_other,$ptascii("VALUE"),|S_select.CLASSES|) = (pclassconstantdesc_other)',
        '$class_constant_lookup(S_select,porigin_child,$ptascii("OTHER"),|S_select.CLASSES|) = (pclassconstantdesc_member_other)',
        'pclassconstantdesc.OWNERNAME = '+base,'pclassconstantdesc.FOLDED',
        '$class_constant_deprecated(S_select,pclassconstantdesc_other)',
        '$class_constant_notice_valid(S_select,pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        '$class_constant_notice_valid(S_select[.RESULT = KNOWN (PSTRING '+other+')],pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        '~$class_constant_notice_valid(S_select,pclassconstantdesc_other.ORIGIN,'+other+',$ptascii("VALUE"),z)',
        '~$class_constant_notice_valid(S_select,pclassconstantdesc_member_other.ORIGIN,'+child+',$ptascii("OTHER"),z)',
        'pcode_missing_class = pcode[.EXPRESSIONS = (CODEEXPR pcpath_class z_class false) :: pcode.EXPRESSIONS]',
        'S_missing_class = S_select[.CODE = [pcode_missing_class]]',
        '$compiled_read(S_missing_class,PORIGIN n_unit pcpath_class) = eps',
        '$class_constant_selected_valid(S_missing_class,expression_class,KNOWN (PSTRING '+other+'))',
        '~$class_constant_notice_valid(S_missing_class,pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        '~$class_constant_notice_valid(S_missing_class,pclassconstantdesc_other.ORIGIN,'+other+',$ptascii("VALUE"),z)',
        'pcode_outer_fold = pcode[.EXPRESSIONS = (CODEEXPR pcpath z true) :: pcode.EXPRESSIONS]',
        '~$class_constant_notice_valid(S_select[.CODE = [pcode_outer_fold]],pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        '~$class_constant_notice_valid(S_select[.POOLS = eps],pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        '~$class_constant_notice_valid(S_select[.ORIGIN = (PORIGIN n_unit pcpath_class)],pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        '~$class_constant_notice_valid(S_select,pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),$(z + 1))',
        'S_selected = $class_constant_selector(S_select,expression_class,z)',
        'S_selected.RESULT = KNOWN (PSTRING '+child+')','S_selected.COMPLETION = NORMAL',
        '$call_descriptors_valid(S_select)',
        'S_warn_one = $drive_steps(S_select,1)','S_warn_one.COMPLETION = BUDGET','S_warn = S_warn_one[.COMPLETION = NORMAL]',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN '+child+' $ptascii("VALUE") z',
        '$error_call_valid(S_warn,perrorcall)','$task_nodes(perrorcall.RESUME) = eps',
        '$class_constant_notice_protected(S_warn,pclassconstantdesc.ORIGIN)',
        'S_inner = $ccx_pause(S_warn,30000)','$ccx_ready(S_inner)',
        'S_inner.TODO = (CLASS_CONST_CLASS expression_class_inner phpType20_inner z_inner) :: ptask_inner*',
        'S_inner.ORIGIN = (PORIGIN n_unit pcpath_inner)','pcpath_inner =/= pcpath',
        'S_inner.CURRENT = (pcallcontext_handler)',
        '$compiled_read(S_inner,PORIGIN n_unit (pcpath_inner ++ [PCFIELD 0])) = (PSTRING '+child+')',
        '$class_constant_notice_valid(S_inner,pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z_inner)',
        '$class_constant_notice_protected(S_inner,pclassconstantdesc.ORIGIN)',
        '$ccn_output(S_inner.EVENTS) = $ptascii("B|H|N|")',
        'S_inner_one = $drive_steps(S_inner,1)','S_inner_one.COMPLETION = BUDGET','S_inner_value = S_inner_one[.COMPLETION = NORMAL]',
        'S_inner_value.RESULT = KNOWN (PINT 7)','S_inner_value.EVENTS = S_inner.EVENTS',
        'S_resume = $ccn_pause(S_inner_value,1,30000)','$ccn_ready(S_resume,1)',
        '$ccn_output(S_resume.EVENTS) = $ptascii("B|H|N|7|")',
        '$class_constant_notice_valid(S_resume,pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        'S_result_one = $drive_steps(S_resume,1)','S_result_one.COMPLETION = BUDGET','S_value = S_result_one[.COMPLETION = NORMAL]',
        'S_value.RESULT = KNOWN (PINT 7)','~$class_constant_notice_protected(S_value,pclassconstantdesc.ORIGIN)',
        'S_second = $ccx_pause(S_value,30000)','$ccx_ready(S_second)',
        'S_second.TODO = (CLASS_CONST_CLASS expression_class_second phpType20_second z_second) :: ptask_second*',
        'S_second.ORIGIN = (PORIGIN n_unit pcpath_second)',
        'expression_class_second = NExprBinaryOpConcat expression_class_left expression_class_right metadata_class_second',
        'phpType20_second = NExprBinaryOpConcat expression_member_left expression_member_right metadata_member_second',
        '$compiled_read(S_second,PORIGIN n_unit (pcpath_second ++ [PCFIELD 0])) = (PSTRING '+child+')',
        '$compiled_read(S_second,PORIGIN n_unit (pcpath_second ++ [PCFIELD 1])) = (PSTRING $ptascii("VALUE"))',
        '$class_constant_compiled_member(S_second,PORIGIN n_unit (pcpath_second ++ [PCFIELD 1]),phpType20_second) = ($ptascii("VALUE"))',
        '$class_constant_notice_valid(S_second,pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z_second)',
        'S_second_warn = $ccn_pause(S_second,0,30000)','$ccn_ready(S_second_warn,0)',
        'S_second_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_second_warn*',
        'perrorcall_second.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN '+child+' $ptascii("VALUE") z_second',
        '$error_call_valid(S_second_warn,perrorcall_second)',
        'S_done = $drive_steps(S_second_warn,30000)','S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = '+quoted(expected),'S_done.CLASSCONSTANTCACHE = eps',
        'S_done.CLASSCONSTANTHISTORY = S_select.CLASSCONSTANTHISTORY',
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
