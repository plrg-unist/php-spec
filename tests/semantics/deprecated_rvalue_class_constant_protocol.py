#!/usr/bin/env python3
"""Check completed class-selector rvalue dataflow after receiver cleanup."""
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
SOURCE=ROOT/'tests/semantics/deprecated_rvalue_class_constant/method-cleanup.php'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
quoted=lambda s:'$base64('+json.dumps(base64.b64encode(s.encode()).decode())+')'
SELECTED=FETCH_SELECTED+r'''
dec $rvalue_class_ready(pstate) : bool
def $rvalue_class_ready(S) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class phpType20_member z) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES,porigin) = (NExprClassConstFetch expression_class phpType20_member metadata)
  -- if expression_class = NExprMethodCall expression_receiver phpType20_method (SEQUENCE eps) metadata_call
def $rvalue_class_ready(S) = false -- otherwise
dec $rvalue_class_pause(pstate,nat) : pstate
def $rvalue_class_pause(S,n) = S -- if $rvalue_class_ready(S)
def $rvalue_class_pause(S,n) = $rvalue_class_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$rvalue_class_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $rvalue_class_pause(S,n) = S -- otherwise
'''


def fields(fixture):
    expected=json.loads((SOURCE.parent/'cases.json').read_text())['method-cleanup']['stdout']
    child=quoted('Ns229Method\\Child229')
    base=quoted('Ns229Method\\Base229')
    other=quoted('Ns229Method\\Other229')
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(SOURCE)).decode())+')',
        'S_start.COMPLETION = BUDGET','S_selected = $rvalue_class_pause(S_start[.COMPLETION = NORMAL],30000)','$rvalue_class_ready(S_selected)',
        'S_selected.TODO = (CLASS_CONST_CLASS expression_class phpType20_member z) :: ptask_tail*',
        'S_selected.ORIGIN = (PORIGIN n_unit pcpath)',
        '$origin_node(S_selected.SOURCES,PORIGIN n_unit pcpath) = (NExprClassConstFetch expression_class phpType20_member metadata)',
        'expression_class = NExprMethodCall expression_receiver phpType20_method (SEQUENCE eps) metadata_call',
        'phpType20_member = NIdentifier (BYTES text_member) metadata_member','$base64(text_member) = $ptascii("VALUE")',
        'S_selected.RESULT = KNOWN pvalue_raw','$constant_value_class_valid(S_selected,pvalue_raw,PVSTRING false)',
        '$string_bytes(pvalue_raw) = ('+child+')','$value_nodes(pvalue_raw) = eps',
        'S_selected.CURRENT = eps','S_selected.FRAMES = eps','S_selected.HELD = eps',
        '$ccn_output(S_selected.EVENTS) = $ptascii("B|M|D|")',
        '$heap_owners($heap_graph(S_selected),HOBJECT 0) = 0','~((HOBJECT 0) <- S_selected.ALLOCATIONS)',
        'S_globals = $global_table_view(S_selected)','$lookup(S_globals.ENV,$ptascii("producer229")) = (n_producer)',
        'S_globals.STORE[n_producer] = DEFINED PNULL',
        '$lookup(S_globals.ENV,$ptascii("selected229")) = (n_selected)','S_globals.STORE[n_selected] = DEFINED pvalue_selected',
        '$string_bytes(pvalue_selected) = ('+child+')',
        'S_class = $class_constant_selector(S_selected,expression_class,z)','S_class.COMPLETION = NORMAL',
        'S_class.RESULT = KNOWN (PSTRING '+child+')','S_class.TODO = S_selected.TODO','S_class.STORE = S_selected.STORE',
        '$code_at(S_class.CODE,n_unit) = (pcode)','$code_expression(pcode.EXPRESSIONS,pcpath) = ((z,false))',
        '$code_expression(pcode.EXPRESSIONS,pcpath ++ [PCFIELD 0]) = ((z_class,false))',
        '$compiled_read(S_class,PORIGIN n_unit (pcpath ++ [PCFIELD 0])) = eps','~$class_constant_literal(S_class,expression_class)',
        '$class_named(S_class.CLASSNAMES,$ptlc('+child+')) = (porigin_requested)',
        '$class_at(S_class.CLASSES,porigin_requested) = (pclassdesc_requested)','pclassdesc_requested.NAME = '+child,
        '$class_constant_lookup(S_class,porigin_requested,$ptascii("VALUE"),|S_class.CLASSES|) = (pclassconstantdesc)',
        'pclassconstantdesc.OWNERNAME = '+base,'pclassconstantdesc.FOLDED',
        '$class_constant_rvalue_class_source(S_class,pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        '$class_constant_rvalue_class_entry(S_class,S_selected.RESULT,expression_class,phpType20_member,z,ptask_tail*) = (pclassconstantdesc)',
        '$call_task_valid(S_class,CLASS_CONST_CLASS expression_class phpType20_member z)','$call_descriptors_valid(S_class)',
        '~$class_constant_notice_valid(S_class,pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        '~$class_constant_notice_protected(S_class,pclassconstantdesc.ORIGIN)',
        '$class_constant_selected_valid(S_class,expression_class,KNOWN (PSTRING '+base+'))',
        '$class_constant_rvalue_class_source(S_class,pclassconstantdesc.ORIGIN,'+base+',$ptascii("VALUE"),z)',
        '$class_constant_rvalue_class_entry(S_class[.RESULT = KNOWN (PSTRING '+base+')],S_selected.RESULT,expression_class,phpType20_member,z,ptask_tail*) = eps',
        '$class_constant_rvalue_class_entry(S_class,KNOWN (PSTRING '+base+'),expression_class,phpType20_member,z,ptask_tail*) = eps',
        '$class_constant_rvalue_class_entry(S_class,REFERENCE n_selected,expression_class,phpType20_member,z,ptask_tail*) = eps',
        '$class_constant_rvalue_class_entry(S_class,VARIABLE $ptascii("selected229") z,expression_class,phpType20_member,z,ptask_tail*) = eps',
        '$class_constant_rvalue_class_entry(S_class,KNOWN PNULL,expression_class,phpType20_member,z,ptask_tail*) = eps',
        '$class_constant_rvalue_class_entry(S_class,KNOWN (POBJECT 0),expression_class,phpType20_member,z,ptask_tail*) = eps',
        '$class_constant_rvalue_class_entry(S_class[.HELD = [KNOWN PNULL]],S_selected.RESULT,expression_class,phpType20_member,z,ptask_tail*) = eps',
        '$class_constant_rvalue_class_entry(S_class,S_selected.RESULT,expression_class,phpType20_member,z,DISCARD :: ptask_tail*) = eps',
        '$class_constant_rvalue_class_entry(S_class[.TODO = ptask_tail*],S_selected.RESULT,expression_class,phpType20_member,z,ptask_tail*) = eps',
        '$class_constant_rvalue_class_entry(S_class[.ORIGIN = (pclassconstantdesc.ORIGIN)],S_selected.RESULT,expression_class,phpType20_member,z,ptask_tail*) = eps',
        '~$class_constant_rvalue_class_source(S_class[.CONSTCONTEXT = ({ORIGIN pclassconstantdesc.ORIGIN,LINE z,FACTS eps})],pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        '~$class_constant_rvalue_class_source(S_class,pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),$(z + 1))',
        'S_warn_one = $drive_steps(S_selected,1)','S_warn_one.COMPLETION = BUDGET','S_warn = S_warn_one[.COMPLETION = NORMAL]',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN '+child+' $ptascii("VALUE") z',
        '$error_call_valid(S_warn,perrorcall)','$call_task_valid(S_warn,perrorcall.RESUME)',
        '$task_nodes(perrorcall.RESUME) = eps','$class_constant_notice_valid(S_warn,pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        '$class_constant_notice_protected(S_warn,pclassconstantdesc.ORIGIN)',
        'S_resume = $ccn_pause(S_warn,1,30000)','$ccn_ready(S_resume,1)',
        'S_resume.TODO = (DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN '+child+' $ptascii("VALUE") z) :: ptask_resume*',
        '$ccn_output(S_resume.EVENTS) = $ptascii("B|M|D|Hb|")',
        'S_after_globals = $global_table_view(S_resume)','$lookup(S_after_globals.ENV,$ptascii("selected229")) = (n_selected_after)',
        'S_after_globals.STORE[n_selected_after] = DEFINED pvalue_after','$string_bytes(pvalue_after) = ('+other+')',
        '$class_constant_notice_valid(S_resume,pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        '~$class_constant_notice_valid(S_resume[.RESULT = KNOWN (PSTRING '+base+')],pclassconstantdesc.ORIGIN,'+base+',$ptascii("VALUE"),z)',
        '~$class_constant_notice_valid(S_resume[.TODO = ptask_resume*],pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        'S_metadata_only = S_resume[.ENV = eps][.STORE = eps][.OBJECTS = eps][.ALLOCATIONS = eps]',
        '$class_constant_rvalue_class_source(S_metadata_only,pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        '$class_constant_notice_valid(S_metadata_only,pclassconstantdesc.ORIGIN,'+child+',$ptascii("VALUE"),z)',
        'S_value_one = $drive_steps(S_resume,1)','S_value_one.COMPLETION = BUDGET','S_value = S_value_one[.COMPLETION = NORMAL]',
        'S_value.RESULT = KNOWN (PINT 7)','S_value.EVENTS = S_resume.EVENTS',
        'S_value.CLASSCONSTANTCACHE = eps','S_value.CLASSCONSTANTHISTORY = S_resume.CLASSCONSTANTHISTORY',
        'S_second = $rvalue_class_pause(S_value,30000)','$rvalue_class_ready(S_second)',
        'S_second.TODO = (CLASS_CONST_CLASS expression_second phpType20_second z_second) :: ptask_second*',
        '$ccn_output(S_second.EVENTS) = $ptascii("B|M|D|Hb|O|7|F|M|D|")',
        'S_second.RESULT = KNOWN pvalue_second','$string_bytes(pvalue_second) = ('+other+')',
        '$heap_owners($heap_graph(S_second),HOBJECT 1) = 0','~((HOBJECT 1) <- S_second.ALLOCATIONS)',
        'S_second_class = $class_constant_selector(S_second,expression_second,z_second)',
        'S_second_class.RESULT = KNOWN (PSTRING '+other+')',
        '$class_constant_rvalue_class_entry(S_second_class,S_second.RESULT,expression_second,phpType20_second,z_second,ptask_second*) = (pclassconstantdesc_second)',
        'pclassconstantdesc_second.ORIGIN =/= pclassconstantdesc.ORIGIN',
        'S_done = $drive_steps(S_second,30000)','S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = '+quoted(expected),'S_done.CLASSCONSTANTCACHE = eps',
        'S_done.CLASSCONSTANTHISTORY = S_selected.CLASSCONSTANTHISTORY',
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
