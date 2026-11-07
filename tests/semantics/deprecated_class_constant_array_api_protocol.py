#!/usr/bin/env python3
"""Check literal pool ownership through array API notice/COW and throw."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_global_constant_protocol import PREFIX, nodes
from deprecated_class_constant_api_protocol import SELECTED as API_SELECTED
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT=Path(__file__).resolve().parents[2]
SELECTIONS={k:ROOT/'tests/semantics/deprecated_class_constant_array_api'/v for k,v in [('cow','notice-cow.php'),('throw','warm-notice-throw.php')]}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SELECTED=API_SELECTED+r'''
dec $array_ready(pstate,nat) : bool
def $array_ready(S,0) = $api_ready(S,0)
def $array_ready(S,1) = $api_ready(S,1)
def $array_ready(S,2) = true
  -- if S.CURRENT =/= eps
  -- if $api_output(S.EVENTS) = $ptascii("H|I|9|8|")
def $array_ready(S,3) = $api_ready(S,3)
def $array_ready(S,4) = $api_ready(S,4)
def $array_ready(S,5) = true
  -- if S.CURRENT = eps
  -- if $api_output(S.EVENTS) = $ptascii("H|I|9|8|1|2|O|1|2|M|4|5|")
def $array_ready(S,n) = false -- otherwise
dec $array_pause(pstate,nat,nat) : pstate
def $array_pause(S,n_mode,n) = S -- if $array_ready(S,n_mode)
def $array_pause(S,n_mode,n) = $array_pause(S_next[.COMPLETION = NORMAL],n_mode,$nabs($(n - 1)))
  -- if ~$array_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $array_pause(S,n_mode,n) = S -- otherwise
'''


def start(fixture,path,mode):
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(path)).decode())+')',
        'S_start.COMPLETION = BUDGET',f'S_warn = $array_pause(S_start[.COMPLETION = NORMAL],{mode},30000)',f'$array_ready(S_warn,{mode})',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl false',
        '$class_constant_api_selection(S_warn,pconfigcall) = (pclassconstantdesc)','pclassconstantdesc.ORIGIN = porigin_decl',
        'pclassconstantdesc.FOLDED',
        '$origin_node(S_warn.SOURCES,pclassconstantdesc.INITIALIZER) = (NExprArray (SEQUENCE phpType13*) metadata)',
        '$pool_value(S_warn.POOLS,pclassconstantdesc.INITIALIZER) = (PARRAY n_original)',
        '$pool_class(S_warn.POOLS,pclassconstantdesc.INITIALIZER) = (PVARRAY b (pkey,pvalueclass)*)',
        '~$class_constant_api_scalar(PVARRAY b (pkey,pvalueclass)*)',
        '$dynamic_class_constant_array_tree(S_warn,PARRAY n_original,PVARRAY b (pkey,pvalueclass)*)',
        '$task_nodes(perrorcall.RESUME) = $config_nodes(pconfigcall)','$config_nodes(pconfigcall) = eps',
        'S_warn.RESULT = KNOWN PNULL','S_warn.CLASSCONSTANTINIT = eps','S_warn.CLASSCONSTANTCACHE = eps',
        '$class_constant_notice_protected(S_warn,porigin_decl)',
        'n_pool = $heap_owners($heap_graph(S_warn),HARRAY n_original)',
        '$call_descriptors_valid(S_warn)']


def finish(path,state):
    expected=json.loads((path.parent/'cases.json').read_text())[path.stem]['stdout'].encode()
    return ['S_done = $drive_steps('+state+',30000)','S_done.COMPLETION = NORMAL',
        '$api_output(S_done.EVENTS) = $base64('+json.dumps(base64.b64encode(expected).decode())+')',
        '~$class_constant_notice_protected(S_done,porigin_decl)','$call_descriptors_valid(S_done)']


def cow(fixture,path):
    return start(fixture,path,0)+[
        '$entry_lookup(S_warn.ARRAYS[n_original].ITEMS,KINT 0) = (DIRECT (PINT 1))',
        '$entry_lookup(S_warn.ARRAYS[n_original].ITEMS,KINT 1) = (DIRECT (PARRAY n_original_inner))',
        '$entry_lookup(S_warn.ARRAYS[n_original_inner].ITEMS,KINT 0) = (DIRECT (PINT 2))',
        'S_local = $array_pause(S_warn,2,30000)','$array_ready(S_local,2)',
        '$lookup(S_local.ENV,$ptascii("copy")) = (n_copy_cell)','S_local.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)',
        'n_copy =/= n_original','(HARRAY n_copy) <- S_local.ALLOCATIONS',
        '$entry_lookup(S_local.ARRAYS[n_copy].ITEMS,KINT 0) = (DIRECT (PINT 9))',
        '$entry_lookup(S_local.ARRAYS[n_copy].ITEMS,KINT 1) = (DIRECT (PARRAY n_copy_inner))',
        'n_copy_inner =/= n_original_inner','(HARRAY n_copy_inner) <- S_local.ALLOCATIONS',
        '$entry_lookup(S_local.ARRAYS[n_copy_inner].ITEMS,KINT 0) = (DIRECT (PINT 8))',
        'S_local.ARRAYS[n_original] = S_warn.ARRAYS[n_original]',
        'S_local.ARRAYS[n_original_inner] = S_warn.ARRAYS[n_original_inner]',
        'S_resume = $array_pause(S_local,1,30000)','$array_ready(S_resume,1)',
        'S_resume.TODO = (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl false) :: ptask_resume*',
        '$api_output(S_resume.EVENTS) = $ptascii("H|I|9|8|1|2|")',
        '~((HARRAY n_copy) <- S_resume.ALLOCATIONS)','~((HARRAY n_copy_inner) <- S_resume.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_resume),HARRAY n_original) = n_pool',
        'S_one = $drive_steps(S_resume,1)','S_one.COMPLETION = BUDGET','S_after = S_one[.COMPLETION = NORMAL]',
        'S_after.RESULT = KNOWN (PARRAY n_original)',
        '$heap_owners($heap_graph(S_after),HARRAY n_original) = $(n_pool + 1)',
        'S_after.CLASSCONSTANTHISTORY = S_resume.CLASSCONSTANTHISTORY','S_after.CLASSCONSTANTCACHE = eps',
        'S_after.EVENTS = S_resume.EVENTS','$call_descriptors_valid(S_after)',
        'S_mutated = $array_pause(S_after,5,30000)','$array_ready(S_mutated,5)',
        '$lookup(S_mutated.ENV,$ptascii("value")) = (n_value)','S_mutated.STORE[n_value] = DEFINED (PARRAY n_result_copy)',
        'n_result_copy =/= n_original','$entry_lookup(S_mutated.ARRAYS[n_result_copy].ITEMS,KINT 0) = (DIRECT (PINT 4))',
        'S_mutated.ARRAYS[n_original] = S_warn.ARRAYS[n_original]',
        'S_mutated.ARRAYS[n_original_inner] = S_warn.ARRAYS[n_original_inner]',
        '$heap_owners($heap_graph(S_mutated),HARRAY n_original) = n_pool',
    ]+finish(path,'S_mutated')


def throw(fixture,path):
    return start(fixture,path,3)+[
        '$lookup(S_warn.ENV,$ptascii("value")) = (n_value)','S_warn.STORE[n_value] = DEFINED pvalue_old',
        '$string_bytes(pvalue_old) = ($ptascii("old"))',
        'S_catch = $array_pause(S_warn,4,30000)','$array_ready(S_catch,4)',
        'S_catch.STORE[n_value] = DEFINED pvalue_old',
        '$heap_owners($heap_graph(S_catch),HARRAY n_original) = n_pool',
        'S_catch.ARRAYS[n_original] = S_warn.ARRAYS[n_original]',
        'S_catch.CLASSCONSTANTCACHE = eps','S_catch.CLASSCONSTANTHISTORY = S_warn.CLASSCONSTANTHISTORY',
        '~$class_constant_notice_protected(S_catch,porigin_decl)','$call_descriptors_valid(S_catch)',
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
        'tests/semantics/deprecated_class_constant_api_protocol.py', 'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py',
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
