#!/usr/bin/env python3
"""Check current and saved CV class selection across warning-time rebinding."""
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
SOURCE=ROOT/'tests/semantics/deprecated_cv_class_constant/string-selector.php'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quoted=lambda s:'$base64('+json.dumps(base64.b64encode(s.encode()).decode())+')'
SELECTED=FETCH_SELECTED+r'''
dec $cv_selector_ready(pstate) : bool
def $cv_selector_ready(S) = true
  -- if S.TODO = (CLASS_CONST_CLASS (NExprVariable (BYTES text) metadata_variable) (NIdentifier phpType33 metadata_member) z) :: ptask*
  -- if $base64(text) = $ptascii("selector221")
def $cv_selector_ready(S) = false -- otherwise
dec $cv_selector_pause(pstate,nat) : pstate
def $cv_selector_pause(S,n) = S -- if $cv_selector_ready(S)
def $cv_selector_pause(S,n) = $cv_selector_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$cv_selector_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $cv_selector_pause(S,n) = S -- otherwise
'''


def fields(fixture):
    expected=json.loads((SOURCE.parent/'cases.json').read_text())['string-selector']['stdout']
    child=quoted('Ns221Select\\Child221');base=quoted('Ns221Select\\Base221');other=quoted('Ns221Select\\Other221')
    first='Constant Ns221Select\\Base221::C is deprecated|16384|'
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(SOURCE)).decode())+')',
        'S_start.COMPLETION = BUDGET','S_cv = $cv_selector_pause(S_start[.COMPLETION = NORMAL],30000)',
        '$cv_selector_ready(S_cv)',
        'S_cv.TODO = (CLASS_CONST_CLASS expression (NIdentifier (BYTES text_member) metadata_member) z) :: ptask_tail*',
        'expression = NExprVariable (BYTES text_variable) metadata_variable',
        'S_cv.RESULT = VARIABLE $base64(text_variable) z_variable',
        'S_read = $resolve_at(S_cv,S_cv.RESULT,z)','S_read.COMPLETION = NORMAL','S_read.RESULT = KNOWN pvalue_raw',
        '$string_bytes(pvalue_raw) = ('+quoted('nS221SeLeCt\\cHiLd221')+')',
        'S_cv.CURRENT = eps','S_cv.CONSTCONTEXT = eps','S_cv.EVENTS = eps',
        'S_selected = $class_constant_selector(S_cv,expression,z)','S_selected.COMPLETION = NORMAL',
        'S_selected.RESULT = KNOWN (PSTRING '+child+')',
        '$class_named(S_selected.CLASSNAMES,$ptlc('+child+')) = (porigin_requested)',
        '$class_at(S_selected.CLASSES,porigin_requested) = (pclassdesc)',
        '$class_constant_lookup(S_selected,porigin_requested,$base64(text_member),|S_selected.CLASSES|) = (pclassconstantdesc)',
        'pclassconstantdesc.OWNERNAME = '+base,'pclassconstantdesc.VISIBILITY = PROPERTY_PUBLIC','pclassconstantdesc.FOLDED',
        '$class_constant_cv_source(S_selected,pclassconstantdesc.ORIGIN,pclassdesc.NAME,$base64(text_member),z)',
        '$class_constant_cv_capture(S_selected,pclassconstantdesc.ORIGIN,pclassdesc.NAME,$base64(text_member),z)',
        '$class_constant_notice_valid(S_selected,pclassconstantdesc.ORIGIN,pclassdesc.NAME,$base64(text_member),z)',
        '~$class_constant_notice_valid(S_cv,pclassconstantdesc.ORIGIN,pclassdesc.NAME,$base64(text_member),z)',
        '$class_constant_selected_valid(S_selected,expression,KNOWN (PSTRING '+other+'))',
        '$class_named(S_selected.CLASSNAMES,$ptlc('+other+')) = (porigin_other)',
        '$class_constant_lookup(S_selected,porigin_other,$base64(text_member),|S_selected.CLASSES|) = (pclassconstantdesc_other)',
        'pclassconstantdesc_other.ORIGIN =/= pclassconstantdesc.ORIGIN',
        '$class_constant_cv_source(S_selected,pclassconstantdesc_other.ORIGIN,'+other+',$base64(text_member),z)',
        '~$class_constant_cv_capture(S_selected,pclassconstantdesc_other.ORIGIN,'+other+',$base64(text_member),z)',
        '~$class_constant_notice_valid(S_selected,pclassconstantdesc_other.ORIGIN,'+other+',$base64(text_member),z)',
        '$class_constant_cv_source(S_selected,pclassconstantdesc.ORIGIN,'+base+',$base64(text_member),z)',
        '~$class_constant_notice_valid(S_selected,pclassconstantdesc.ORIGIN,'+base+',$base64(text_member),z)',
        '~$class_constant_notice_valid(S_selected,pclassconstantdesc.ORIGIN,pclassdesc.NAME,$base64(text_member),$(z + 1))',
        '$call_descriptors_valid(S_cv)',
        'S_warn_one = $drive_steps(S_cv,1)','S_warn_one.COMPLETION = BUDGET','S_warn = S_warn_one[.COMPLETION = NORMAL]',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN pclassdesc.NAME ptbytes_member z',
        'ptbytes_member = $base64(text_member)',
        '$class_constant_cv_pending(ERROR_HANDLER_INVOKE perrorcall) = ((pclassconstantdesc.ORIGIN,pclassdesc.NAME,ptbytes_member,z))',
        'S_warn.RESULT = KNOWN PNULL','S_warn.CLASSCONSTANTINIT = eps','S_warn.CONSTCONTEXT = eps',
        'perrorcall.MESSAGE = '+quoted(first[:-7]),
        '$error_call_valid(S_warn,perrorcall)','$call_descriptors_valid(S_warn)',
        '$task_nodes(perrorcall.RESUME) = eps','$class_constant_notice_protected(S_warn,pclassconstantdesc.ORIGIN)',
        '$ccn_output(S_warn.EVENTS) = eps',
        'S_resume = $ccn_pause(S_warn,1,30000)','$ccn_ready(S_resume,1)',
        'S_resume.TODO = (DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN pclassdesc.NAME ptbytes_member z) :: ptask_resume*',
        'S_resume.RESULT = KNOWN PNULL','$ccn_output(S_resume.EVENTS) = '+quoted(first),
        'S_globals = $global_table_view(S_resume)','$lookup(S_globals.ENV,$ptascii("selector221")) = (n_cell)',
        'S_globals.STORE[n_cell] = DEFINED pvalue_current','$string_bytes(pvalue_current) = ('+other+')',
        '$class_constant_cv_source(S_resume,pclassconstantdesc.ORIGIN,pclassdesc.NAME,ptbytes_member,z)',
        '$class_constant_cv_capture(S_resume,pclassconstantdesc.ORIGIN,pclassdesc.NAME,ptbytes_member,z)',
        '$class_constant_notice_valid(S_resume,pclassconstantdesc.ORIGIN,pclassdesc.NAME,ptbytes_member,z)',
        '~$class_constant_notice_valid(S_resume,pclassconstantdesc_other.ORIGIN,'+other+',ptbytes_member,z)',
        '~$class_constant_notice_valid(S_resume,pclassconstantdesc.ORIGIN,pclassdesc.NAME,$ptascii("missing"),z)',
        '$call_descriptors_valid(S_resume)',
        'S_value_one = $drive_steps(S_resume,1)','S_value_one.COMPLETION = BUDGET','S_value = S_value_one[.COMPLETION = NORMAL]',
        'S_value.RESULT = KNOWN (PINT 7)','S_value.EVENTS = S_resume.EVENTS',
        'S_value.CLASSCONSTANTCACHE = S_resume.CLASSCONSTANTCACHE','S_value.CLASSCONSTANTHISTORY = S_resume.CLASSCONSTANTHISTORY',
        '~$class_constant_notice_protected(S_value,pclassconstantdesc.ORIGIN)',
        'S_other = $cv_selector_pause(S_value,30000)','$cv_selector_ready(S_other)',
        'S_other.TODO = (CLASS_CONST_CLASS expression_other phpType20_other z_other) :: ptask_other*',
        'S_other_read = $resolve_at(S_other,S_other.RESULT,z_other)','S_other_read.COMPLETION = NORMAL',
        'S_other_read.RESULT = KNOWN pvalue_other','$string_bytes(pvalue_other) = ('+other+')',
        'S_other_selected = $class_constant_selector(S_other,expression_other,z_other)',
        'S_other_selected.RESULT = KNOWN (PSTRING '+other+')',
        '$class_constant_notice_valid(S_other_selected,pclassconstantdesc_other.ORIGIN,'+other+',ptbytes_member,z_other)',
        '$compiled_read(S_other,pclassconstantdesc.INITIALIZER) = (PINT 7)',
        '$compiled_read(S_other,pclassconstantdesc_other.INITIALIZER) = (PINT 9)',
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
