#!/usr/bin/env python3
"""Check completed rvalue member dataflow after receiver cleanup."""
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
SOURCE=ROOT/'tests/semantics/deprecated_rvalue_member_constant/method-cleanup.php'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quoted=lambda s:'$base64('+json.dumps(base64.b64encode(s.encode()).decode())+')'
SELECTED=FETCH_SELECTED+r'''
dec $rvalue_pair_ready(pstate) : bool
def $rvalue_pair_ready(S) = true
  -- if S.TODO = (CLASS_CONST_MEMBER name poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES,porigin) = (NExprClassConstFetch name (NExprMethodCall expression_receiver phpType20 (SEQUENCE eps) metadata_call) metadata)
def $rvalue_pair_ready(S) = false -- otherwise
dec $rvalue_pair_pause(pstate,nat) : pstate
def $rvalue_pair_pause(S,n) = S -- if $rvalue_pair_ready(S)
def $rvalue_pair_pause(S,n) = $rvalue_pair_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$rvalue_pair_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $rvalue_pair_pause(S,n) = S -- otherwise
'''

def fields(fixture):
    expected=json.loads((SOURCE.parent/'cases.json').read_text())['method-cleanup']['stdout']
    target=quoted('Ns228Method\\Target228')
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(SOURCE)).decode())+')',
        'S_start.COMPLETION = BUDGET','S_pair = $rvalue_pair_pause(S_start[.COMPLETION = NORMAL],30000)','$rvalue_pair_ready(S_pair)',
        'S_pair.TODO = (CLASS_CONST_MEMBER name_class poperand_class z) :: (CLASS_CONST_CAPTURE porigin_site poperand_class z) :: ptask_tail*',
        'poperand_class = KNOWN (PSTRING '+target+')','porigin_site = PORIGIN n_unit pcpath',
        '$origin_node(S_pair.SOURCES,porigin_site) = (NExprClassConstFetch name_class expression_member metadata)',
        'expression_member = NExprMethodCall expression_receiver phpType20_method (SEQUENCE eps) metadata_call',
        'S_pair.RESULT = KNOWN pvalue_member','$constant_value_class_valid(S_pair,pvalue_member,PVSTRING false)',
        '$string_bytes(pvalue_member) = ($ptascii("VALUE"))','$value_nodes(pvalue_member) = eps',
        'S_pair.CURRENT = eps','S_pair.FRAMES = eps','S_pair.HELD = eps',
        '$ccn_output(S_pair.EVENTS) = $ptascii("B|M|D|")',
        '$heap_owners($heap_graph(S_pair),HOBJECT 0) = 0','~((HOBJECT 0) <- S_pair.ALLOCATIONS)',
        'S_globals = $global_table_view(S_pair)','$lookup(S_globals.ENV,$ptascii("producer228")) = (n_producer)',
        'S_globals.STORE[n_producer] = DEFINED PNULL',
        'S_read = $resolve_at(S_pair,S_pair.RESULT,z)','S_read.RESULT = S_pair.RESULT',
        '$code_at(S_read.CODE,n_unit) = (pcode)','$code_expression(pcode.EXPRESSIONS,pcpath) = ((z,false))',
        '$code_expression(pcode.EXPRESSIONS,pcpath ++ [PCFIELD 1]) = ((z_member,false))',
        '$compiled_read(S_read,PORIGIN n_unit (pcpath ++ [PCFIELD 1])) = eps',
        '~$class_constant_legacy_call_member(expression_member)',
        '$class_constant_legacy_call_member(NExprFuncCall name_class (SEQUENCE eps) metadata_call)',
        '$class_named(S_read.CLASSNAMES,$ptlc('+target+')) = (porigin_target)',
        '$class_constant_lookup(S_read,porigin_target,$ptascii("VALUE"),|S_read.CLASSES|) = (pclassconstantdesc)',
        'pclassconstantdesc.FOLDED',
        '$class_constant_rvalue_member_source(S_read,pclassconstantdesc.ORIGIN,'+target+',$ptascii("VALUE"),z)',
        '$class_constant_rvalue_member_entry(S_read,S_pair.RESULT,name_class,poperand_class,z,ptask_tail*) = (pclassconstantdesc)',
        '~$class_constant_notice_valid(S_read,pclassconstantdesc.ORIGIN,'+target+',$ptascii("VALUE"),z)',
        '~$class_constant_notice_protected(S_read,pclassconstantdesc.ORIGIN)',
        '$call_task_valid(S_read,CLASS_CONST_MEMBER name_class poperand_class z)','$call_descriptors_valid(S_read)',
        '$class_constant_rvalue_member_entry(S_read,REFERENCE n_producer,name_class,poperand_class,z,ptask_tail*) = eps',
        '$class_constant_rvalue_member_entry(S_read,VARIABLE $ptascii("producer228") z,name_class,poperand_class,z,ptask_tail*) = eps',
        '$class_constant_rvalue_member_entry(S_read,KNOWN PNULL,name_class,poperand_class,z,ptask_tail*) = eps',
        '$class_constant_rvalue_member_entry(S_read,KNOWN (PSTRING $ptascii("OTHER")),name_class,poperand_class,z,ptask_tail*) = eps',
        '$class_constant_rvalue_member_entry(S_read[.RESULT = KNOWN PNULL],S_pair.RESULT,name_class,poperand_class,z,ptask_tail*) = eps',
        '$class_constant_rvalue_member_entry(S_read[.TODO = (CLASS_CONST_MEMBER name_class poperand_class z) :: ptask_tail*],S_pair.RESULT,name_class,poperand_class,z,ptask_tail*) = eps',
        '$class_constant_rvalue_member_entry(S_read[.TODO = (CLASS_CONST_MEMBER name_class poperand_class z) :: (CLASS_CONST_CAPTURE pclassconstantdesc.ORIGIN poperand_class z) :: ptask_tail*],S_pair.RESULT,name_class,poperand_class,z,ptask_tail*) = eps',
        '$class_constant_rvalue_member_entry(S_read,S_pair.RESULT,name_class,poperand_class,z,DISCARD :: ptask_tail*) = eps',
        '~$class_constant_rvalue_member_source(S_read[.CONSTCONTEXT = ({ORIGIN pclassconstantdesc.ORIGIN,LINE z,FACTS eps})],pclassconstantdesc.ORIGIN,'+target+',$ptascii("VALUE"),z)',
        '~$class_constant_rvalue_member_source(S_read,pclassconstantdesc.ORIGIN,'+target+',$ptascii("VALUE"),$(z + 1))',
        'S_consumed = S_read[.TODO = ptask_tail*]',
        '$class_constant_rvalue_member_entry(S_consumed,S_pair.RESULT,name_class,poperand_class,z,ptask_tail*) = eps',
        '~$class_constant_notice_valid(S_consumed,pclassconstantdesc.ORIGIN,'+target+',$ptascii("VALUE"),z)',
        'S_warn_one = $drive_steps(S_pair,1)','S_warn_one.COMPLETION = BUDGET','S_warn = S_warn_one[.COMPLETION = NORMAL]',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN '+target+' $ptascii("VALUE") z',
        '$error_call_valid(S_warn,perrorcall)','$call_task_valid(S_warn,perrorcall.RESUME)',
        '$task_nodes(perrorcall.RESUME) = eps','$class_constant_notice_valid(S_warn,pclassconstantdesc.ORIGIN,'+target+',$ptascii("VALUE"),z)',
        '$class_constant_notice_protected(S_warn,pclassconstantdesc.ORIGIN)',
        'S_resume = $ccn_pause(S_warn,1,30000)','$ccn_ready(S_resume,1)',
        'S_resume.TODO = (DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN '+target+' $ptascii("VALUE") z) :: ptask_resume*',
        '$ccn_output(S_resume.EVENTS) = $ptascii("B|M|D|H|")',
        '$class_constant_notice_valid(S_resume,pclassconstantdesc.ORIGIN,'+target+',$ptascii("VALUE"),z)',
        'S_metadata_only = S_resume[.ENV = eps][.STORE = eps][.OBJECTS = eps][.ALLOCATIONS = eps]',
        '$class_constant_rvalue_member_source(S_metadata_only,pclassconstantdesc.ORIGIN,'+target+',$ptascii("VALUE"),z)',
        '$class_constant_notice_valid(S_metadata_only,pclassconstantdesc.ORIGIN,'+target+',$ptascii("VALUE"),z)',
        '~$class_constant_notice_valid(S_resume[.TODO = ptask_resume*],pclassconstantdesc.ORIGIN,'+target+',$ptascii("VALUE"),z)',
        '~$class_constant_notice_valid(S_resume,pclassconstantdesc.ORIGIN,'+target+',$ptascii("VALUE"),$(z + 1))',
        'S_value_one = $drive_steps(S_resume,1)','S_value_one.COMPLETION = BUDGET','S_value = S_value_one[.COMPLETION = NORMAL]',
        'S_value.RESULT = KNOWN (PINT 7)','S_value.EVENTS = S_resume.EVENTS',
        'S_value.CLASSCONSTANTCACHE = eps','S_value.CLASSCONSTANTHISTORY = S_resume.CLASSCONSTANTHISTORY',
        '~$class_constant_notice_protected(S_value,pclassconstantdesc.ORIGIN)',
        'S_done = $drive_steps(S_value,30000)','S_done.COMPLETION = NORMAL',
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
