#!/usr/bin/env python3
"""Check class-constant notice phases, canonical guards and warm throw cleanup."""
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

ROOT = Path(__file__).resolve().parents[2]
SELECTIONS = {name: ROOT / 'tests/semantics/deprecated_class_constant_fetch' / source for name,source in [('order','notice-before-value.php'),('throw','warm-notice-throw.php')]}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
SELECTED = r'''
dec $ccn_output_item(pevent) : ptbytes
def $ccn_output_item(OUTPUT ptbytes) = ptbytes
def $ccn_output_item(pevent) = eps -- otherwise
dec $ccn_output(pevent*) : ptbytes
def $ccn_output(eps) = eps
def $ccn_output(pevent :: pevent_tail*) = $ccn_output_item(pevent) ++ $ccn_output(pevent_tail*)
dec $ccn_ready(pstate,nat) : bool
def $ccn_ready(S,0) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin ptbytes_class ptbytes_member z
def $ccn_ready(S,1) = true
  -- if S.TODO = (DEPRECATED_CLASS_CONSTANT_RESULT porigin ptbytes_class ptbytes_member z) :: ptask*
def $ccn_ready(S,2) = true
  -- if S.TODO = (CLASS_CONST_BIND porigin) :: ptask*
def $ccn_ready(S,3) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin ptbytes_class ptbytes_member z
  -- if $ccn_output(S.EVENTS) = $ptascii("H|S|7|")
def $ccn_ready(S,4) = true
  -- if S.CURRENT = eps
  -- if $ccn_output(S.EVENTS) = $ptascii("H|S|7|H|T|old|")
def $ccn_ready(S,n) = false -- otherwise
dec $ccn_pause(pstate,nat,nat) : pstate
def $ccn_pause(S,n_mode,n) = S -- if $ccn_ready(S,n_mode)
def $ccn_pause(S,n_mode,n) = $ccn_pause(S_next[.COMPLETION = NORMAL],n_mode,$nabs($(n - 1)))
  -- if ~$ccn_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $ccn_pause(S,n_mode,n) = S -- otherwise
'''


def start(fixture,path,mode):
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(path)).decode())+')',
        'S_start.COMPLETION = BUDGET',f'S_warn = $ccn_pause(S_start[.COMPLETION = NORMAL],{mode},30000)',f'$ccn_ready(S_warn,{mode})',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class ptbytes_member z',
        '$class_constant_origin(S_warn.CLASSES,porigin_decl) = (pclassconstantdesc)',
        '$class_constant_deprecated(S_warn,pclassconstantdesc)',
        '$class_constant_notice_valid(S_warn,porigin_decl,ptbytes_class,ptbytes_member,z)',
        'perrorcall.LEVEL = 16384','perrorcall.LINE = z',
        'perrorcall.MESSAGE = $class_constant_notice_message(pclassconstantdesc,ptbytes_member)',
        '$error_call_valid(S_warn,perrorcall)','$call_descriptors_valid(S_warn)',
        '$task_nodes(perrorcall.RESUME) = eps','S_warn.RESULT = KNOWN PNULL',
        'S_warn.CLASSCONSTANTINIT = eps','S_warn.CONSTCONTEXT = eps',
        '$class_constant_notice_protected(S_warn,porigin_decl)',
        '~$class_constant_notice_protected(S_warn[.TODO = ptask_warn*],porigin_decl)',
        '~$class_constant_notice_protected(S_warn,pclassconstantdesc.OWNER)',
        '~$class_constant_notice_valid(S_warn,porigin_decl,ptbytes_class,ptbytes_member,$(z + 1))',
        '~$error_call_valid(S_warn,perrorcall[.LEVEL = 8192])',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.OWNER ptbytes_class ptbytes_member z])',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class $ptascii("missing") z])',
    ]


def finish(path,state):
    expected=json.loads((path.parent/'cases.json').read_text())[path.stem]['stdout'].encode()
    return ['S_done = $drive_steps('+state+',30000)','S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = $base64('+json.dumps(base64.b64encode(expected).decode())+')',
        '~$class_constant_notice_protected(S_done,porigin_decl)','$call_descriptors_valid(S_done)']


def order(fixture,path):
    return start(fixture,path,0)+[
        '~pclassconstantdesc.FOLDED',
        '$default_cache_at(S_warn.CLASSCONSTANTCACHE,porigin_decl) = eps',
        '$ccn_output(S_warn.EVENTS) = eps',
        'S_child = $ccn_pause(S_warn,2,30000)','$ccn_ready(S_child,2)',
        'S_child.TODO = (CLASS_CONST_BIND porigin_decl) :: ptask_child*',
        'S_child.CLASSCONSTANTINIT = [pclassconstantcontext]',
        'pclassconstantcontext.DECL = porigin_decl',
        '$class_constant_notice_protected(S_child,porigin_decl)',
        '$ccn_output(S_child.EVENTS) = $ptascii("C|I|")',
        'S_child.RESULT = KNOWN (PINT 9)',
        '$default_cache_at(S_child.CLASSCONSTANTCACHE,porigin_decl) = eps',
        '$call_descriptors_valid(S_child)',
        'S_one_child = $drive_steps(S_child,1)','S_one_child.COMPLETION = BUDGET',
        'S_after_child = S_one_child[.COMPLETION = NORMAL]',
        '$default_cache_at(S_after_child.CLASSCONSTANTCACHE,porigin_decl) = (pdefaultcache_child)',
        'pdefaultcache_child.VALUE = PINT 9',
        'S_resume = $ccn_pause(S_after_child,1,30000)','$ccn_ready(S_resume,1)',
        'S_resume.TODO = (DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class ptbytes_member z) :: ptask_resume*',
        '$ccn_output(S_resume.EVENTS) = $ptascii("C|I|9|")',
        'S_resume.CLASSCONSTANTINIT = eps',
        '$default_cache_at(S_resume.CLASSCONSTANTCACHE,porigin_decl) = (pdefaultcache_child)',
        '$class_constant_notice_protected(S_resume,porigin_decl)',
        '$call_descriptors_valid(S_resume)',
        'S_one = $drive_steps(S_resume,1)','S_one.COMPLETION = BUDGET','S_after = S_one[.COMPLETION = NORMAL]',
        'S_after.RESULT = KNOWN (PINT 9)',
        'S_after.CLASSCONSTANTCACHE = S_resume.CLASSCONSTANTCACHE',
        'S_after.CLASSCONSTANTHISTORY = S_resume.CLASSCONSTANTHISTORY',
        'S_after.EVENTS = S_resume.EVENTS','S_after.CLASSCONSTANTINIT = eps',
        '~$class_constant_notice_protected(S_after,porigin_decl)',
        '$class_named(S_after.CLASSNAMES,$ptlc($base64("TnMyMTFPcmRlclxDaGlsZDIxMQ=="))) = (porigin_child)',
        '$class_constant_lookup(S_after,porigin_child,ptbytes_member,|S_after.CLASSES|) = (pclassconstantdesc)',
    ]+finish(path,'S_after')


def throw(fixture,path):
    return start(fixture,path,3)+[
        'pclassconstantdesc.FOLDED',
        '$pool_value(S_warn.POOLS,pclassconstantdesc.INITIALIZER) = (PINT 7)',
        '$class_constant_compile_value(S_warn,pclassconstantdesc) = eps',
        '$default_cache_at(S_warn.CLASSCONSTANTCACHE,porigin_decl) = eps',
        '$lookup(S_warn.ENV,$ptascii("value")) = (n_value)',
        'S_warn.STORE[n_value] = DEFINED pvalue_old',
        '$string_bytes(pvalue_old) = ($ptascii("old"))',
        'S_catch = $ccn_pause(S_warn,4,30000)','$ccn_ready(S_catch,4)',
        'S_catch.STORE[n_value] = DEFINED pvalue_old',
        '~$class_constant_notice_protected(S_catch,porigin_decl)',
        'S_catch.CLASSCONSTANTINIT = eps',
        'S_catch.CLASSCONSTANTCACHE = S_warn.CLASSCONSTANTCACHE',
        '$call_descriptors_valid(S_catch)',
    ]+finish(path,'S_catch')


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
