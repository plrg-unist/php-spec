#!/usr/bin/env python3
"""Check API notice/acquisition phases and shared literal recursion."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_global_constant_protocol import PREFIX, nodes
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT=Path(__file__).resolve().parents[2]
SELECTIONS={k:ROOT/'tests/semantics/deprecated_class_constant_api'/v for k,v in [('order','notice-before-value.php'),('throw','warm-notice-throw.php'),('reentry','literal-api-reentry.php')]}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SELECTED=r'''
dec $api_output_item(pevent) : ptbytes
def $api_output_item(OUTPUT ptbytes) = ptbytes
def $api_output_item(pevent) = eps -- otherwise
dec $api_output(pevent*) : ptbytes
def $api_output(eps) = eps
def $api_output(pevent :: pevent_tail*) = $api_output_item(pevent) ++ $api_output(pevent_tail*)
dec $api_ready(pstate,nat) : bool
def $api_ready(S,0) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin false
def $api_ready(S,1) = true
  -- if S.TODO = (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin false) :: ptask*
def $api_ready(S,2) = true
  -- if S.TODO = (CLASS_CONST_BIND porigin) :: ptask*
def $api_ready(S,3) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin false
  -- if $api_output(S.EVENTS) = $ptascii("H|S|7|")
def $api_ready(S,4) = true
  -- if S.CURRENT = eps
  -- if $api_output(S.EVENTS) = $ptascii("H|S|7|H|T|old|")
def $api_ready(S,5) = true
  -- if S.TODO = (CLASS_CONST_BIND porigin) :: (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin true) :: ptask*
def $api_ready(S,n) = false -- otherwise
dec $api_pause(pstate,nat,nat) : pstate
def $api_pause(S,n_mode,n) = S -- if $api_ready(S,n_mode)
def $api_pause(S,n_mode,n) = $api_pause(S_next[.COMPLETION = NORMAL],n_mode,$nabs($(n - 1)))
  -- if ~$api_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $api_pause(S,n_mode,n) = S -- otherwise
'''


def initial(fixture,path):
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(path)).decode())+')','S_start.COMPLETION = BUDGET']


def start(fixture,path,mode):
    return initial(fixture,path)+[f'S_warn = $api_pause(S_start[.COMPLETION = NORMAL],{mode},30000)',f'$api_ready(S_warn,{mode})',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl false',
        '$class_constant_api_selection(S_warn,pconfigcall) = (pclassconstantdesc)','pclassconstantdesc.ORIGIN = porigin_decl',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_query)]','$string_carrier_valid(S_warn,pvalue_query)',
        '$task_nodes(perrorcall.RESUME) = $config_nodes(pconfigcall)','$config_nodes(pconfigcall) = eps',
        '$selected_task_nonce(perrorcall.RESUME) = pconfigcall.SELECTION',
        '$class_constant_notice_task(perrorcall.RESUME,porigin_decl)',
        '~$class_constant_notice_task(DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl true,porigin_decl)',
        '$class_constant_notice_protected(S_warn,porigin_decl)',
        '~$class_constant_query_readable(S_warn,pclassconstantdesc)','$dynamic_class_constant_deferred(S_warn,pconfigcall) = eps',
        '$error_call_valid(S_warn,perrorcall)','$call_descriptors_valid(S_warn)',
        'S_warn.RESULT = KNOWN PNULL','S_warn.CLASSCONSTANTINIT = eps','S_warn.CONSTCONTEXT = eps',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl true])']


def finish(path,state):
    expected=json.loads((path.parent/'cases.json').read_text())[path.stem]['stdout'].encode()
    return ['S_done = $drive_steps('+state+',30000)','S_done.COMPLETION = NORMAL',
        '$api_output(S_done.EVENTS) = $base64('+json.dumps(base64.b64encode(expected).decode())+')',
        '~$class_constant_notice_protected(S_done,porigin_decl)','$call_descriptors_valid(S_done)']


def order(fixture,path):
    return start(fixture,path,0)+['~pclassconstantdesc.FOLDED',
        '$default_cache_at(S_warn.CLASSCONSTANTCACHE,porigin_decl) = eps','$api_output(S_warn.EVENTS) = eps',
        'S_child = $api_pause(S_warn,2,30000)','$api_ready(S_child,2)',
        'S_child.CLASSCONSTANTINIT = [pclassconstantcontext]','pclassconstantcontext.DECL = porigin_decl',
        'pclassconstantcontext.SELECTION = CLASS_CONST_FETCH poperand_class ptbytes_member',
        '$class_constant_notice_protected(S_child,porigin_decl)','$api_output(S_child.EVENTS) = $ptascii("C|I|")',
        'S_child.RESULT = KNOWN (PINT 9)','$call_descriptors_valid(S_child)',
        'S_one_child = $drive_steps(S_child,1)','S_one_child.COMPLETION = BUDGET',
        'S_resume = $api_pause(S_one_child[.COMPLETION = NORMAL],1,30000)','$api_ready(S_resume,1)',
        'S_resume.TODO = (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl false) :: ptask_resume*',
        '$default_cache_at(S_resume.CLASSCONSTANTCACHE,porigin_decl) = (pdefaultcache)','pdefaultcache.VALUE = PINT 9',
        '$api_output(S_resume.EVENTS) = $ptascii("C|I|9|")','$class_constant_notice_protected(S_resume,porigin_decl)',
        'S_resume.CLASSCONSTANTINIT = eps','$call_descriptors_valid(S_resume)',
        'S_one = $drive_steps(S_resume,1)','S_one.COMPLETION = BUDGET','S_after = S_one[.COMPLETION = NORMAL]',
        'S_after.RESULT = KNOWN (PINT 9)','S_after.EVENTS = S_resume.EVENTS',
        'S_after.CLASSCONSTANTCACHE = S_resume.CLASSCONSTANTCACHE','S_after.CLASSCONSTANTHISTORY = S_resume.CLASSCONSTANTHISTORY',
        '~$class_constant_notice_protected(S_after,porigin_decl)']+finish(path,'S_after')


def throw(fixture,path):
    return start(fixture,path,3)+['~pclassconstantdesc.FOLDED',
        '$default_cache_at(S_warn.CLASSCONSTANTCACHE,porigin_decl) = (pdefaultcache)','pdefaultcache.VALUE = PINT 7',
        '$lookup(S_warn.ENV,$ptascii("value")) = (n_value)','S_warn.STORE[n_value] = DEFINED pvalue_old',
        '$string_bytes(pvalue_old) = ($ptascii("old"))',
        'S_catch = $api_pause(S_warn,4,30000)','$api_ready(S_catch,4)',
        'S_catch.STORE[n_value] = DEFINED pvalue_old','S_catch.CLASSCONSTANTCACHE = S_warn.CLASSCONSTANTCACHE',
        'S_catch.CLASSCONSTANTHISTORY = S_warn.CLASSCONSTANTHISTORY',
        '~$class_constant_notice_protected(S_catch,porigin_decl)','$call_descriptors_valid(S_catch)']+finish(path,'S_catch')


def reentry(fixture,path):
    return initial(fixture,path)+['S_bind = $api_pause(S_start[.COMPLETION = NORMAL],5,30000)','$api_ready(S_bind,5)',
        'S_bind.TODO = (CLASS_CONST_BIND porigin_decl) :: (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl true) :: ptask_tail*',
        '$class_constant_api_selection(S_bind,pconfigcall) = (pclassconstantdesc)','pclassconstantdesc.ORIGIN = porigin_decl',
        'S_bind.CLASSCONSTANTINIT = pclassconstantcontext :: pclassconstantcontext_tail*',
        'pclassconstantcontext.SELECTION = CLASS_CONST_CALL pconfigcall','pclassconstantcontext.DECL = porigin_decl',
        '$class_constant_api_resume_present(S_bind.TODO,porigin_decl,pconfigcall)',
        '~$class_constant_notice_task(DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl true,porigin_decl)',
        '$class_constant_notice_protected(S_bind,porigin_decl)',
        '~$class_constant_query_readable(S_bind,pclassconstantdesc)','$dynamic_class_constant_deferred(S_bind,pconfigcall) = eps',
        '$api_output(S_bind.EVENTS) = $ptascii("L|A|")','S_bind.RESULT = KNOWN (PINT 9)',
        '$task_nodes(DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl true) = $config_nodes(pconfigcall)',
        'S_view = $class_constant_restore(S_bind,pclassconstantcontext,pclassconstantcontext_tail*)',
        '$class_constant_selection_valid(S_view,pclassconstantcontext)',
        'S_wrong = S_view[.TODO = (CLASS_CONST_BIND porigin_decl) :: (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl false) :: ptask_tail*]',
        '~$class_constant_selection_valid(S_wrong,pclassconstantcontext)',
        'S_legacy = S_view[.TODO = (CLASS_CONST_BIND porigin_decl) :: (DYNAMIC_CLASS_CONSTANT_RESUME pconfigcall) :: ptask_tail*]',
        '~$class_constant_selection_valid(S_legacy,pclassconstantcontext)','$call_descriptors_valid(S_bind)',
        'S_one_bind = $drive_steps(S_bind,1)','S_one_bind.COMPLETION = BUDGET','S_value = S_one_bind[.COMPLETION = NORMAL]',
        'S_value.TODO = (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl true) :: ptask_tail*',
        '$default_cache_at(S_value.CLASSCONSTANTCACHE,porigin_decl) = (pdefaultcache)','pdefaultcache.VALUE = PINT 9',
        'S_one = $drive_steps(S_value,1)','S_one.COMPLETION = BUDGET','S_after = S_one[.COMPLETION = NORMAL]',
        'S_after.RESULT = KNOWN (PINT 9)','S_after.CLASSCONSTANTHISTORY = S_value.CLASSCONSTANTHISTORY',
        'S_after.EVENTS = S_value.EVENTS']+finish(path,'S_after')


def prepare(out,group):
    path=SELECTIONS[group]
    frontend=Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],out/'frontend')
    adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],out/'adapter')
    try:
        parsed=frontend.request({'op':'parse','source':base64.b64encode(path.read_bytes()).decode()});assert parsed['accepted'] and not parsed['diagnostics']
        checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True});assert checked['ok']
    finally:
        try:adapter.close()
        finally:frontend.close()
    checks=globals()[group](checked['fixture'],path)
    (out/'assertions.json').write_text(json.dumps(checks,indent=2)+'\n')
    (out/'protocol.watsup').write_text(PREFIX+SELECTED+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+c+'\n' for c in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--group', required=True, choices=tuple(SELECTIONS))
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), SELECTIONS[args.group], SELECTIONS[args.group].parent / 'cases.json', *modules, *(ROOT / path for path in (
        'spec/semantics/modules.json', 'spec/schema.json', 'frontend/worker.php',
        'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py',
        'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py',
        '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
        'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'group': args.group, 'inputs': before, 'module_count': len(modules),
        'source_agreement_credit': 0, 'passed': False}
    try:
        report['premises'] = prepare(out, args.group)
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
            *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in paths}
        report['passed'] = report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after'] and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable']
    finally: (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    if not report['passed']: print(report.get('stdout', '')[:2000], report.get('stderr', '')[:4000])
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()
