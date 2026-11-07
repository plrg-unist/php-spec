#!/usr/bin/env python3
"""Check quiet constructor fields at literal, API and private keyword notices."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_global_constant_protocol import PREFIX
from deprecated_class_constant_fetch_protocol import SELECTED as FETCH_SELECTED
from deprecated_class_constant_api_protocol import SELECTED as API_SELECTED
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'tests/semantics/deprecated_class_constant_message/class-fields.php'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quoted=lambda s:'$base64('+json.dumps(base64.b64encode(s.encode()).decode())+')'
SELECTED=FETCH_SELECTED+API_SELECTED+r'''
dec $message_private_ready(pstate) : bool
def $message_private_ready(S) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin ptbytes_class ptbytes_member z
  -- if $class_constant_origin(S.CLASSES,porigin) = (pclassconstantdesc)
  -- if pclassconstantdesc.VISIBILITY = PROPERTY_PRIVATE
def $message_private_ready(S) = false -- otherwise
dec $message_private_pause(pstate,nat) : pstate
def $message_private_pause(S,n) = S -- if $message_private_ready(S)
def $message_private_pause(S,n) = $message_private_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$message_private_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $message_private_pause(S,n) = S -- otherwise
'''


def fields(fixture):
    expected=json.loads((SOURCE.parent/'cases.json').read_text())['class-fields']['stdout']
    message='Constant Ns220Class\\Base220::C is deprecated since 2.0, Use fresh'
    secret='Constant Ns220Class\\Base220::SECRET is deprecated, private only'
    prefix=message+'|16384|7|'
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(SOURCE)).decode())+')',
        'S_start.COMPLETION = BUDGET','S_warn = $ccn_pause(S_start[.COMPLETION = NORMAL],0,30000)',
        '$ccn_ready(S_warn,0)','S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class ptbytes_member z',
        '$class_constant_origin(S_warn.CLASSES,porigin_decl) = (pclassconstantdesc)',
        'pclassconstantdesc.VISIBILITY = PROPERTY_PUBLIC','pclassconstantdesc.NAME = $ptascii("C")',
        'pclassconstantdesc.FOLDED','$class_at(S_warn.CLASSES,pclassconstantdesc.OWNER) = (pclassdesc)',
        'pclassdesc.CONSTANTS = [pclassconstantdesc,pclassconstantdesc_private]',
        'pclassconstantdesc_private.VISIBILITY = PROPERTY_PRIVATE',
        '$class_constant_message_metadata(S_warn,pclassconstantdesc) = DEPRECATED_ATTRIBUTE $ptascii("Use fresh") $ptascii("2.0")',
        '$class_constant_message_metadata(S_warn,pclassconstantdesc_private) = DEPRECATED_ATTRIBUTE $ptascii("private only") eps',
        '$class_constant_deprecated(S_warn,pclassconstantdesc)','$class_constant_deprecated(S_warn,pclassconstantdesc_private)',
        '$class_constant_message_metadata(S_warn,pclassconstantdesc[.VISIBILITY = PROPERTY_PRIVATE]) = NO_DEPRECATED',
        '$class_constant_message_metadata(S_warn,pclassconstantdesc_private[.VISIBILITY = PROPERTY_PUBLIC]) = NO_DEPRECATED',
        '$class_constant_notice_text(S_warn,pclassconstantdesc,ptbytes_member) = '+quoted(message),
        'perrorcall.MESSAGE = '+quoted(message),'perrorcall.LEVEL = 16384','perrorcall.LINE = z',
        '$class_constant_notice_valid(S_warn,porigin_decl,ptbytes_class,ptbytes_member,z)',
        '$error_call_valid(S_warn,perrorcall)','$call_descriptors_valid(S_warn)',
        '~$error_call_valid(S_warn,perrorcall[.MESSAGE = $class_constant_notice_message(pclassconstantdesc,ptbytes_member)])',
        '~$error_call_valid(S_warn,perrorcall[.MESSAGE = '+quoted('Constant Ns220Class\\Base220::C is deprecated, Use fresh since 2.0')+'])',
        '~$error_call_valid(S_warn,perrorcall[.LEVEL = 8192])',
        'S_warn.RESULT = KNOWN PNULL','S_warn.CLASSCONSTANTINIT = eps','S_warn.CONSTCONTEXT = eps',
        '$task_nodes(perrorcall.RESUME) = eps','$class_constant_notice_protected(S_warn,porigin_decl)',
        '$class_constant_attribute_group(S_warn.SOURCES,pclassconstantdesc) = ((PORIGIN n_unit pcpath_group,phpType15*))',
        '$source_unit(S_warn.SOURCES,n_unit) = (pcunit)','$code_at(S_warn.CODE,n_unit) = (pcode)',
        'pcpath_since = pcpath_group ++ [PCFIELD 0,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 1,PCINDEX 0,PCFIELD 1]',
        'pcpath_message = pcpath_group ++ [PCFIELD 0,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 1,PCINDEX 1,PCFIELD 1]',
        '$ppconstant_metadata_root(pcunit,pcpath_since)','$ppconstant_metadata_root(pcunit,pcpath_message)',
        '$ppconstant_deferred_context(pcunit,pcpath_since)','$constant_class_origin_allowed(pcunit,pcpath_message)',
        '$pool_value(S_warn.POOLS,PORIGIN n_unit pcpath_since) = (PSTRING $ptascii("2.0"))',
        '$pool_class(S_warn.POOLS,PORIGIN n_unit pcpath_since) = (PVSTRING false)',
        '$pool_value(S_warn.POOLS,PORIGIN n_unit pcpath_message) = (PSTRING $ptascii("Use fresh"))',
        '$code_expression(pcode.EXPRESSIONS,pcpath_since) = eps','$code_expression(pcode.EXPRESSIONS,pcpath_message) = eps',
        'pclassconstantdesc.INITIALIZER = PORIGIN n_unit pcpath_initializer',
        '~$ppconstant_metadata_root(pcunit,pcpath_initializer)',
        '~$ppconstant_metadata_root(pcunit,pcpath_since ++ [PCFIELD 0])',
        '$compilation_image_valid(S_warn,pcunit,$declaration_compiler_state($eval_source_ppstate(S_warn,pcunit)))',
        '$ccn_output(S_warn.EVENTS) = eps',
        'S_api = $api_pause(S_warn,0,30000)','$api_ready(S_api,0)',
        'S_api.TODO = (ERROR_HANDLER_INVOKE perrorcall_api) :: ptask_api*',
        'perrorcall_api.RESUME = DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl false',
        '$class_constant_api_selection(S_api,pconfigcall) = (pclassconstantdesc)',
        '$dynamic_defined_query(pconfigcall) = (('+quoted('Ns220Class\\Child220')+',$ptascii("C")))',
        '$ccn_output(S_api.EVENTS) = '+quoted(prefix*2),
        'perrorcall_api.MESSAGE = '+quoted(message),'perrorcall_api.LINE = pconfigcall.LINE',
        '$error_call_valid(S_api,perrorcall_api)','$call_descriptors_valid(S_api)',
        '~$error_call_valid(S_api,perrorcall_api[.MESSAGE = $class_constant_notice_message(pclassconstantdesc,$ptascii("C"))])',
        '$class_constant_notice_protected(S_api,porigin_decl)',
        '$task_nodes(perrorcall_api.RESUME) = $config_nodes(pconfigcall)',
        'S_api.RESULT = KNOWN PNULL','S_api.CLASSCONSTANTINIT = eps',
        'S_private = $message_private_pause(S_api,30000)','$message_private_ready(S_private)',
        'S_private.TODO = (ERROR_HANDLER_INVOKE perrorcall_private) :: ptask_private*',
        'perrorcall_private.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc_private.ORIGIN ptbytes_private_class ptbytes_private_member z_private',
        '$ccn_output(S_private.EVENTS) = '+quoted(prefix*3),
        '$method_current_scope(S_private) = (pclassconstantdesc_private.OWNER)',
        '$class_constant_visible(S_private,pclassconstantdesc_private)',
        '$class_constant_message_metadata(S_private,pclassconstantdesc_private) = DEPRECATED_ATTRIBUTE $ptascii("private only") eps',
        'perrorcall_private.MESSAGE = '+quoted(secret),
        '$class_constant_notice_valid(S_private,pclassconstantdesc_private.ORIGIN,ptbytes_private_class,ptbytes_private_member,z_private)',
        '$error_call_valid(S_private,perrorcall_private)','$call_descriptors_valid(S_private)',
        '~$error_call_valid(S_private,perrorcall_private[.MESSAGE = $class_constant_notice_message(pclassconstantdesc_private,ptbytes_private_member)])',
        '$class_constant_attribute_group(S_private.SOURCES,pclassconstantdesc_private) = ((PORIGIN n_unit pcpath_private_group,phpType15_private*))',
        'pcpath_null = pcpath_private_group ++ [PCFIELD 0,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 1,PCINDEX 1,PCFIELD 1]',
        '$ppconstant_metadata_root(pcunit,pcpath_null)',
        '$pool_value(S_private.POOLS,PORIGIN n_unit pcpath_null) = (PNULL)',
        '$pool_class(S_private.POOLS,PORIGIN n_unit pcpath_null) = (PVSCALAR)',
        '$code_expression(pcode.EXPRESSIONS,pcpath_null) = eps',
        '$task_nodes(perrorcall_private.RESUME) = eps','S_private.CLASSCONSTANTINIT = eps',
        'S_done = $drive_steps(S_private,30000)','S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = '+quoted(expected),
        '~$class_constant_notice_protected(S_done,porigin_decl)',
        '~$class_constant_notice_protected(S_done,pclassconstantdesc_private.ORIGIN)',
        'S_done.CLASSCONSTANTINIT = eps','$class_constant_state_valid(S_done)','$call_descriptors_valid(S_done)']


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
        'tests/semantics/deprecated_class_constant_fetch_protocol.py','tests/semantics/deprecated_class_constant_api_protocol.py',
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
