#!/usr/bin/env python3
"""Check class/global notice order and owning initializer release/retry."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_global_constant_protocol import PREFIX, nodes
from deprecated_interface_constant_protocol import SELECTED as CACHE_SELECTED
from deprecated_class_constant_fetch_protocol import SELECTED as NOTICE_SELECTED
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT=Path(__file__).resolve().parents[2]
SELECTIONS={k:ROOT/'tests/semantics/deprecated_owned_class_constant_notice'/v for k,v in [('computed','computed-reentry.php'),('retry','global-throw-retry.php')]}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SELECTED=CACHE_SELECTED+NOTICE_SELECTED+r'''
dec $owned_retry_ready(pstate) : bool
def $owned_retry_ready(S) = true
  -- if S.CURRENT = eps
  -- if $ic_output(S.EVENTS) = $ptascii("C|G|T|old|")
def $owned_retry_ready(S) = false -- otherwise
dec $owned_retry_pause(pstate,nat) : pstate
def $owned_retry_pause(S,n) = S -- if $owned_retry_ready(S)
def $owned_retry_pause(S,n) = $owned_retry_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$owned_retry_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $owned_retry_pause(S,n) = S -- otherwise
'''


def start(fixture,path):
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(path)).decode())+')',
        'S_start.COMPLETION = BUDGET','S_class = $ccn_pause(S_start[.COMPLETION = NORMAL],0,30000)','$ccn_ready(S_class,0)',
        'S_class.TODO = (ERROR_HANDLER_INVOKE perrorcall_class) :: ptask_class*',
        'perrorcall_class.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class ptbytes_member z',
        '$class_constant_origin(S_class.CLASSES,porigin_decl) = (pclassconstantdesc)',
        '$class_constant_deprecated(S_class,pclassconstantdesc)','$owned_class_constant_source(S_class,pclassconstantdesc)',
        '~pclassconstantdesc.FOLDED','pclassconstantdesc.ORIGIN = PORIGIN n_unit pcpath_decl',
        'pclassconstantdesc.INITIALIZER = PORIGIN n_unit (pcpath_decl ++ [PCFIELD 1])',
        '~$owned_class_constant_source(S_class,pclassconstantdesc[.INITIALIZER = porigin_decl])',
        '~$owned_class_constant_source(S_class,pclassconstantdesc[.VISIBILITY = PROPERTY_PRIVATE])',
        'S_class.CLASSCONSTANTINIT = eps','S_class.CONSTCONTEXT = eps',
        '$default_cache_at(S_class.CLASSCONSTANTCACHE,porigin_decl) = eps',
        '$class_constant_notice_protected(S_class,porigin_decl)','$ic_output(S_class.EVENTS) = eps',
        '$call_descriptors_valid(S_class)',
        'S_warn = $dep_pause(S_class,30000)','S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CONSTANT_RESULT pdeprecatedconstant',
        'S_warn.CONSTCONTEXT = (pconstantcontext)',
        'S_warn.CLASSCONSTANTINIT = pclassconstantcontext :: pclassconstantcontext_tail*',
        'pclassconstantcontext.DECL = porigin_decl','pconstantcontext.ORIGIN = porigin_decl',
        '$ic_output(S_warn.EVENTS) = $ptascii("C|")',
        '~$class_constant_notice_protected(S_warn,porigin_decl)',
        '$owned_class_constant_source(S_warn,pclassconstantdesc)',
        '$deprecated_constant_class_ast(S_warn,pdeprecatedconstant.SITE)',
        '$class_constant_pending_cache(S_warn,pclassconstantcontext)',
        '$default_cache_at(S_warn.CLASSCONSTANTCACHE,porigin_decl) = eps',
        'pdeprecatedconstant.VALUE = PARRAY n_donor','S_warn.ARRAYS[n_donor].ITEMS = eps',
        '$call_descriptors_valid(S_warn)']


def finish(path,state):
    expected=json.loads((path.parent/'cases.json').read_text())[path.stem]['stdout'].encode()
    return ['S_done = $drive_steps('+state+',30000)','S_done.COMPLETION = NORMAL',
        '$ic_output(S_done.EVENTS) = $base64('+json.dumps(base64.b64encode(expected).decode())+')',
        '$class_constant_state_valid(S_done)','$call_descriptors_valid(S_done)',
        '~$class_constant_notice_protected(S_done,porigin_decl)',
        '$machine_roots(S_done[.CLASSCONSTANTHISTORY = eps]) = $machine_roots(S_done)']


def computed(fixture,path):
    return start(fixture,path)+[
        'S_bind = $ic_parent_pause(S_warn,pclassconstantcontext,30000)','$ic_parent_ready(S_bind,pclassconstantcontext)',
        '$ic_output(S_bind.EVENTS) = $ptascii("C|G|I|9|")',
        '$default_cache_at(S_bind.CLASSCONSTANTCACHE,porigin_decl) = (pdefaultcache_old)',
        'pdefaultcache_old.VALUE = PARRAY n_old','S_bind.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]',
        'S_bind.RESULT = KNOWN (PARRAY n_new)','n_new =/= n_old',
        'S_bind.ARRAYS[n_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_donor))]',
        '$heap_owners($heap_graph(S_bind),HARRAY n_old) = 1','$heap_owners($heap_graph(S_bind),HARRAY n_new) = 1',
        '$call_descriptors_valid(S_bind)',
        'S_stage = $drive_steps(S_bind,1)','S_stage.COMPLETION = BUDGET',
        'S_stage.CLASSCONSTANTWRITES = [pclassreplacement]','pclassreplacement.OLD = pdefaultcache_old',
        '$class_write_live(S_stage,pclassreplacement)',
        'S_stage.CLASSCONSTANTCACHE = S_bind.CLASSCONSTANTCACHE','S_stage.CLASSCONSTANTHISTORY = S_bind.CLASSCONSTANTHISTORY',
        '~((HARRAY n_old) <- $class_constant_machine_roots(S_stage))',
        '$heap_owners($heap_graph(S_stage),HARRAY n_old) = 1',
        '$heap_owners($heap_graph(S_stage),HARRAY n_new) = 1',
        '$class_image_valid(pclassreplacement.IMAGE)','$call_descriptors_valid(S_stage)',
        'S_publish = $ic_publish_pause(S_stage[.COMPLETION = NORMAL],30000)','$ic_publish_ready(S_publish)',
        '~((HARRAY n_old) <- S_publish.ALLOCATIONS)','(HARRAY n_new) <- S_publish.ALLOCATIONS',
        'S_publish.CLASSCONSTANTHISTORY = S_bind.CLASSCONSTANTHISTORY',
        '$class_write_live(S_publish,pclassreplacement)','$call_descriptors_valid(S_publish)',
    ]+finish(path,'S_publish')+[
        '$default_cache_at(S_done.CLASSCONSTANTCACHE,porigin_decl) = (pdefaultcache_new)',
        'pdefaultcache_new.VALUE = PARRAY n_new',
        'S_done.ARRAYS[n_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_donor))]',
        '~((HARRAY n_old) <- S_done.ALLOCATIONS)',
    ]


def retry(fixture,path):
    return start(fixture,path)+[
        '$lookup(S_warn.ENV,$ptascii("value")) = (n_value)',
        'S_warn.STORE[n_value] = DEFINED pvalue_old','$string_bytes(pvalue_old) = ($ptascii("old"))',
        'S_catch = $owned_retry_pause(S_warn,30000)','$owned_retry_ready(S_catch)',
        'S_catch.STORE[n_value] = DEFINED pvalue_old','S_catch.CLASSCONSTANTINIT = eps','S_catch.CONSTCONTEXT = eps',
        '$default_cache_at(S_catch.CLASSCONSTANTCACHE,porigin_decl) = eps',
        '~$class_constant_notice_protected(S_catch,porigin_decl)',
        '$class_constant_state_valid(S_catch)','$call_descriptors_valid(S_catch)',
    ]+finish(path,'S_catch')+[
        '$default_cache_at(S_done.CLASSCONSTANTCACHE,porigin_decl) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_donor',
    ]


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
        'tests/semantics/deprecated_interface_constant_protocol.py', 'tests/semantics/deprecated_class_constant_fetch_protocol.py', 'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py',
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
