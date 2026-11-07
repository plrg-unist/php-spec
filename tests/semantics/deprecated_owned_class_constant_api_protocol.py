#!/usr/bin/env python3
"""Check owning API cold/reentrant bind and authenticated warm acquisition."""
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
SELECTIONS={'array':ROOT/'tests/semantics/deprecated_owned_class_constant_api/cold-array-reentry.php'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SELECTED=API_SELECTED+r'''
dec $owned_api_ready(pstate,nat) : bool
def $owned_api_ready(S,0) = true
  -- if S.TODO = (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin false) :: ptask*
  -- if $api_output(S.EVENTS) = $ptascii("C|G|I|1|O|1|R|8|M|7|C|")
def $owned_api_ready(S,n) = false -- otherwise
dec $owned_api_pause(pstate,nat,nat) : pstate
def $owned_api_pause(S,n_mode,n) = S -- if $owned_api_ready(S,n_mode)
def $owned_api_pause(S,n_mode,n) = $owned_api_pause(S_next[.COMPLETION = NORMAL],n_mode,$nabs($(n - 1)))
  -- if ~$owned_api_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $owned_api_pause(S,n_mode,n) = S -- otherwise
'''


def array(fixture,path):
    expected=json.loads((path.parent/'cases.json').read_text())[path.stem]['stdout'].encode()
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(path)).decode())+')',
        'S_start.COMPLETION = BUDGET','S_class = $api_pause(S_start[.COMPLETION = NORMAL],0,30000)','$api_ready(S_class,0)',
        'S_class.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_class*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl false',
        '$class_constant_api_selection(S_class,pconfigcall) = (pclassconstantdesc)',
        'pclassconstantdesc.ORIGIN = porigin_decl','~pclassconstantdesc.FOLDED','pclassconstantdesc.TYPE = eps',
        '$class_constant_api_owned_global(S_class,pclassconstantdesc) = (puserconstant)',
        'puserconstant.VALUE = PARRAY n_donor','S_class.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        '~$deprecated_global_nonowning(puserconstant.VALUE)','$constant_value_class_valid(S_class,puserconstant.VALUE,puserconstant.CLASS)',
        '$dynamic_class_constant_global(S_class,pclassconstantdesc) = (ptbytes_global)',
        '~$class_constant_api_global_scalar(S_class,ptbytes_global)',
        '~$dynamic_class_constant_initializer(S_class,pclassconstantdesc)',
        '$class_constant_query_readable(S_class,pclassconstantdesc) = false',
        '$task_nodes(perrorcall.RESUME) = eps','$config_nodes(pconfigcall) = eps',
        'S_class.RESULT = KNOWN PNULL','S_class.CLASSCONSTANTINIT = eps','S_class.CONSTCONTEXT = eps',
        '$class_constant_notice_protected(S_class,porigin_decl)','$api_output(S_class.EVENTS) = eps',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_query)]',
        '$string_bytes(pvalue_query) = ($base64("TnMyMTZBcnJheVxDaGlsZDIxNjo6VkFMVUU="))',
        '$call_descriptors_valid(S_class)',
        'S_global = $dep_pause(S_class,30000)',
        'S_global.TODO = (ERROR_HANDLER_INVOKE perrorcall_global) :: ptask_global*',
        'perrorcall_global.RESUME = DEPRECATED_CONSTANT_RESULT pdeprecatedconstant',
        'pdeprecatedconstant.COPIED = eps','$api_output(S_global.EVENTS) = $ptascii("C|")',
        '~$class_constant_notice_protected(S_global,porigin_decl)',
        'S_global.CLASSCONSTANTINIT = [pclassconstantcontext_parent]',
        'pclassconstantcontext_parent.DECL = porigin_decl','pclassconstantcontext_parent.SELECTION = CLASS_CONST_CALL pconfigcall',
        '$class_constant_protected(pclassconstantcontext_parent.SELECTION,pclassconstantcontext_parent.PREVIOUS)',
        '$class_constant_visited(S_global.CLASSCONSTANTINIT,porigin_decl)',
        'S_globals = $global_table_view(S_global)',
        '$lookup(S_globals.ENV,$ptascii("query")) = (n_query)',
        'S_globals.STORE[n_query] = DEFINED pvalue_changed',
        '$string_bytes(pvalue_changed) = ($base64("TnMyMTZBcnJheVxPdGhlcjIxNjo6VkFMVUU="))',
        '$deprecated_constant_value(S_global[.USERCONSTANTS = S_global.USERCONSTANTS[0:pdeprecatedconstant.PREFIX]],pdeprecatedconstant.SITE) = PARRAY n_donor',
        '$call_descriptors_valid(S_global)',
        'S_child = $api_pause(S_global,2,30000)','$api_ready(S_child,2)',
        'S_child.CLASSCONSTANTINIT = [pclassconstantcontext_child,pclassconstantcontext_parent]',
        'pclassconstantcontext_child.DECL = porigin_decl',
        'pclassconstantcontext_child.SELECTION = CLASS_CONST_FETCH poperand_class ptbytes_member',
        '~$class_constant_protected(pclassconstantcontext_child.SELECTION,pclassconstantcontext_child.PREVIOUS)',
        'S_child.RESULT = KNOWN (PARRAY n_donor)',
        '$default_cache_at(S_child.CLASSCONSTANTCACHE,porigin_decl) = eps','$call_descriptors_valid(S_child)',
        'S_child_one = $drive_steps(S_child,1)','S_child_one.COMPLETION = BUDGET',
        'S_parent = $api_pause(S_child_one[.COMPLETION = NORMAL],5,30000)','$api_ready(S_parent,5)',
        'S_parent.TODO = (CLASS_CONST_BIND porigin_decl) :: (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl true) :: ptask_parent*',
        'S_parent.CLASSCONSTANTINIT = [pclassconstantcontext_parent]',
        '$api_output(S_parent.EVENTS) = $ptascii("C|G|I|1|")','S_parent.RESULT = KNOWN (PARRAY n_donor)',
        '$default_cache_at(S_parent.CLASSCONSTANTCACHE,porigin_decl) = (pdefaultcache_child)',
        'pdefaultcache_child.VALUE = PARRAY n_donor','pdefaultcache_child.CLASS = puserconstant.CLASS',
        'S_view = $class_constant_restore(S_parent,pclassconstantcontext_parent,eps)',
        '$class_constant_selection_valid(S_view,pclassconstantcontext_parent)',
        '$class_constant_row_payload_valid(S_view,pclassconstantdesc,pdefaultcache_child)',
        '$call_descriptors_valid(S_parent)',
        'S_parent_one = $drive_steps(S_parent,1)','S_parent_one.COMPLETION = BUDGET',
        'S_value = S_parent_one[.COMPLETION = NORMAL]',
        'S_value.TODO = (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall porigin_decl true) :: ptask_parent*',
        '$default_cache_at(S_value.CLASSCONSTANTCACHE,porigin_decl) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_donor','pdefaultcache.CLASS = puserconstant.CLASS',
        '$class_constant_row_payload_valid(S_value,pclassconstantdesc,pdefaultcache)',
        '~$class_constant_notice_protected(S_value,porigin_decl)',
        'S_after = $class_constant_api_value(S_value,pconfigcall,pclassconstantdesc)',
        'S_after.RESULT = KNOWN (PARRAY n_donor)','S_after.CLASSCONSTANTCACHE = S_value.CLASSCONSTANTCACHE',
        'S_after.CLASSCONSTANTHISTORY = S_value.CLASSCONSTANTHISTORY','$call_descriptors_valid(S_after)',
        'S_warm = $owned_api_pause(S_after,0,30000)','$owned_api_ready(S_warm,0)',
        'S_warm.TODO = (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall_warm porigin_decl false) :: ptask_warm*',
        'pconfigcall_warm =/= pconfigcall','$class_constant_api_valid(S_warm,pconfigcall_warm,porigin_decl)',
        'S_globals_warm = $global_table_view(S_warm)','$lookup(S_globals_warm.ENV,$ptascii("value")) = (n_value)',
        'S_globals_warm.STORE[n_value] = DEFINED (PARRAY n_copy)','n_copy =/= n_donor',
        'S_warm.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
        'S_warm.ARRAYS[n_donor].ITEMS = S_class.ARRAYS[n_donor].ITEMS',
        'S_warm.RESULT = KNOWN PNULL','$class_constant_notice_protected(S_warm,porigin_decl)',
        'S_ready = S_warm[.TODO = (DEPRECATED_CLASS_CONSTANT_API_RESULT pconfigcall_warm porigin_decl true) :: ptask_warm*]',
        '$class_constant_api_owned_global(S_ready,pclassconstantdesc) = (puserconstant)',
        '$class_constant_row_payload_valid(S_ready,pclassconstantdesc,pdefaultcache)',
        'S_wrong = S_ready[.CLASSCONSTANTCACHE = [pdefaultcache[.VALUE = PARRAY n_copy]]]',
        '$class_constant_api_value(S_wrong,pconfigcall_warm,pclassconstantdesc).COMPLETION = UNSUPPORTED "Deprecated class constant API value"',
        'S_history = S_ready[.CLASSCONSTANTHISTORY = eps]',
        '$class_constant_cache_value_valid(S_history,pdefaultcache)',
        '~$class_constant_row_payload_valid(S_history,pclassconstantdesc,pdefaultcache)',
        '$class_constant_api_value(S_history,pconfigcall_warm,pclassconstantdesc).COMPLETION = UNSUPPORTED "Deprecated class constant API value"',
        'n_before = $heap_owners($heap_graph(S_warm),HARRAY n_donor)',
        'S_warm_one = $drive_steps(S_warm,1)','S_warm_one.COMPLETION = BUDGET',
        'S_acquired = S_warm_one[.COMPLETION = NORMAL]','S_acquired.RESULT = KNOWN (PARRAY n_donor)',
        '$heap_owners($heap_graph(S_acquired),HARRAY n_donor) = $(n_before + 1)',
        'S_acquired.CLASSCONSTANTCACHE = S_warm.CLASSCONSTANTCACHE',
        'S_acquired.CLASSCONSTANTHISTORY = S_warm.CLASSCONSTANTHISTORY',
        '$call_descriptors_valid(S_acquired)',
        'S_done = $drive_steps(S_acquired,30000)','S_done.COMPLETION = NORMAL',
        '$api_output(S_done.EVENTS) = $base64('+json.dumps(base64.b64encode(expected).decode())+')',
        '$class_constant_state_valid(S_done)','$call_descriptors_valid(S_done)',
        '$machine_roots(S_done[.CLASSCONSTANTHISTORY = eps]) = $machine_roots(S_done)',
        'S_done.ARRAYS[n_donor].ITEMS = S_class.ARRAYS[n_donor].ITEMS']


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
