#!/usr/bin/env python3
"""Check lexical and called-class authority for keyword constant notices."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_global_constant_protocol import PREFIX, nodes
from deprecated_class_constant_fetch_protocol import SELECTED as NOTICE_SELECTED
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT=Path(__file__).resolve().parents[2]
SELECTIONS={'scope':ROOT/'tests/semantics/deprecated_keyword_class_constant/self-static.php'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SELECTED=NOTICE_SELECTED


def scope(fixture,path):
    expected=json.loads((path.parent/'cases.json').read_text())[path.stem]['stdout'].encode()
    checks=['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(path)).decode())+')',
        'S_start.COMPLETION = BUDGET','S_self = $ccn_pause(S_start[.COMPLETION = NORMAL],0,30000)','$ccn_ready(S_self,0)',
        'S_self.TODO = (ERROR_HANDLER_INVOKE perrorcall_self) :: ptask_self*',
        'perrorcall_self.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_base ptbytes_base ptbytes_member z',
        'S_self.ORIGIN = (PORIGIN n_unit pcpath_self)',
        '$origin_node(S_self.SOURCES,PORIGIN n_unit pcpath_self) = (NExprClassConstFetch (NName (BYTES text_self) metadata_self) (NIdentifier (BYTES text_member) metadata_member) metadata_fetch)',
        '$ptlc($base64(text_self)) = $ptascii("self")',
        '$class_constant_origin(S_self.CLASSES,porigin_base) = (pclassconstantdesc_base)',
        '$class_constant_lookup(S_self,pclassconstantdesc_base.OWNER,ptbytes_member,|S_self.CLASSES|) = (pclassconstantdesc_base)',
        'S_self.CURRENT = (pcallcontext_base)',
        '$target_function(S_self,pcallcontext_base.TARGET) = (pfunction)',
        '$parameter_method_source(S_self,pfunction) = (pmethoddesc)','pmethoddesc.VISIBILITY = PROPERTY_PUBLIC',
        'pcallcontext_base.FUNCTION = pfunction.ORIGIN','pcallcontext_base.LEXICAL_CLASS = (pmethoddesc.OWNER)',
        'pcallcontext_base.CALLED_CLASS = (pmethoddesc.OWNER)',
        'pcallcontext_base.RECEIVER = eps','pcallcontext_base.INSTANCE = eps',
        'pcallcontext_base.WRAPPER = eps','pcallcontext_base.CACHE = eps',
        'pcallcontext_base.CALLSITE = (porigin_call_base)',
        '$parameter_cv_method_selected(S_self,pcallcontext_base.TARGET,porigin_call_base)',
        '~$parameter_cv_method_selected(S_self,OUTPUT_BORROWED_TARGET pcallcontext_base.TARGET,porigin_call_base)',
        '$class_constant_keyword_method(S_self,PORIGIN n_unit pcpath_self)',
        'pfunction.ORIGIN = PORIGIN n_unit pcpath_method',
        'pcpath_body = pcpath_method ++ [PCFIELD 6]',
        'pcpath_self[0:|pcpath_body|] = pcpath_body',
        '$code_expression(pfunction.CODE.EXPRESSIONS,pcpath_self) = ((z_code,false))',
        '~$class_constant_keyword_method(S_self,pfunction.ORIGIN)',
        '~$class_constant_keyword_method(S_self,PORIGIN n_unit (pcpath_method ++ [PCFIELD 4]))',
        '~$class_constant_keyword_method(S_self[.CONSTCONTEXT = ({ORIGIN porigin_base,LINE z,FACTS eps})],PORIGIN n_unit pcpath_self)',
        '$scoped_source_name(S_self,NName (BYTES text_self) metadata_self) = (ptbytes_base)',
        '$class_constant_notice_valid(S_self,porigin_base,ptbytes_base,ptbytes_member,z)',
        '$class_constant_notice_protected(S_self,porigin_base)',
        '~$class_constant_query_readable(S_self,pclassconstantdesc_base)',
        'S_self.CLASSCONSTANTINIT = eps','S_self.CONSTCONTEXT = eps','S_self.RESULT = KNOWN PNULL',
        '$default_cache_at(S_self.CLASSCONSTANTCACHE,porigin_base) = eps',
        '$task_nodes(perrorcall_self.RESUME) = eps','$error_call_valid(S_self,perrorcall_self)',
        '$call_task_valid(S_self,perrorcall_self.RESUME)','$call_descriptors_valid(S_self)',
        'S_one_self = $drive_steps(S_self,1)','S_one_self.COMPLETION = BUDGET',
        'S_static = $ccn_pause(S_one_self[.COMPLETION = NORMAL],0,30000)','$ccn_ready(S_static,0)',
        'S_static.TODO = (ERROR_HANDLER_INVOKE perrorcall_static) :: ptask_static*',
        'perrorcall_static.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_base ptbytes_base ptbytes_member z_static',
        'S_static.ORIGIN = (PORIGIN n_unit pcpath_static)',
        '$origin_node(S_static.SOURCES,PORIGIN n_unit pcpath_static) = (NExprClassConstFetch (NName (BYTES text_static) metadata_static) (NIdentifier (BYTES text_member) metadata_member_static) metadata_fetch_static)',
        '$ptlc($base64(text_static)) = $ptascii("static")',
        'S_static.CURRENT = (pcallcontext_base)',
        '$scoped_source_name(S_static,NName (BYTES text_static) metadata_static) = (ptbytes_base)',
        '$default_cache_at(S_static.CLASSCONSTANTCACHE,porigin_base) = (pdefaultcache)',
        'pdefaultcache.VALUE = PINT 7','$ccn_output(S_static.EVENTS) = $ptascii("S|B|7|L|")',
        '$class_constant_keyword_method(S_static,PORIGIN n_unit pcpath_static)','$call_descriptors_valid(S_static)',
        'S_one_static = $drive_steps(S_static,1)','S_one_static.COMPLETION = BUDGET',
        'S_child_self = $ccn_pause(S_one_static[.COMPLETION = NORMAL],0,30000)','$ccn_ready(S_child_self,0)',
        'S_child_self.TODO = (ERROR_HANDLER_INVOKE perrorcall_child_self) :: ptask_child_self*',
        'perrorcall_child_self.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_base ptbytes_base ptbytes_member z',
        'S_child_self.CURRENT = (pcallcontext_child)',
        'pcallcontext_child.FUNCTION = pfunction.ORIGIN','pcallcontext_child.LEXICAL_CLASS = (pmethoddesc.OWNER)',
        'pcallcontext_child.CALLED_CLASS = (porigin_called_child)','porigin_called_child =/= pmethoddesc.OWNER',
        'S_child_self.ORIGIN = (PORIGIN n_unit pcpath_self)',
        '$scoped_source_name(S_child_self,NName (BYTES text_self) metadata_self) = (ptbytes_base)',
        '$class_at(S_child_self.CLASSES,porigin_called_child) = (pclassdesc_child)',
        '$class_constant_lookup(S_child_self,porigin_called_child,ptbytes_member,|S_child_self.CLASSES|) = (pclassconstantdesc_child)',
        'pclassconstantdesc_child.ORIGIN =/= porigin_base','pclassconstantdesc_child.OWNER = porigin_called_child',
        '$class_constant_notice_valid(S_child_self,porigin_base,ptbytes_base,ptbytes_member,z)',
        '~$class_constant_notice_valid(S_child_self,porigin_base,pclassdesc_child.NAME,ptbytes_member,z)',
        'S_bad_lexical = S_self[.CURRENT = (pcallcontext_base[.LEXICAL_CLASS = (porigin_called_child)])]',
        '~$class_constant_keyword_method(S_bad_lexical,PORIGIN n_unit pcpath_self)',
        '$class_constant_keyword_method(S_child_self,PORIGIN n_unit pcpath_self)',
        '$default_cache_at(S_child_self.CLASSCONSTANTCACHE,porigin_base) = (pdefaultcache)',
        '$ccn_output(S_child_self.EVENTS) = $ptascii("S|B|7|L|B|7|S|")','$call_descriptors_valid(S_child_self)',
        'S_one_child = $drive_steps(S_child_self,1)','S_one_child.COMPLETION = BUDGET',
        'S_child_static = $ccn_pause(S_one_child[.COMPLETION = NORMAL],0,30000)','$ccn_ready(S_child_static,0)',
        'S_child_static.TODO = (ERROR_HANDLER_INVOKE perrorcall_child_static) :: ptask_child_static*',
        'perrorcall_child_static.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc_child.ORIGIN pclassdesc_child.NAME ptbytes_member z_static',
        'S_child_static.CURRENT = (pcallcontext_child)','S_child_static.ORIGIN = (PORIGIN n_unit pcpath_static)',
        '$scoped_source_name(S_child_static,NName (BYTES text_static) metadata_static) = (pclassdesc_child.NAME)',
        '$class_constant_keyword_method(S_child_static,PORIGIN n_unit pcpath_static)',
        '~$class_constant_notice_valid(S_child_static,porigin_base,pclassdesc_child.NAME,ptbytes_member,z_static)',
        'S_bad_called = S_child_static[.CURRENT = (pcallcontext_child[.CALLED_CLASS = (pmethoddesc.OWNER)])]',
        '~$class_constant_keyword_method(S_bad_called,PORIGIN n_unit pcpath_static)',
        '$class_constant_notice_protected(S_child_static,pclassconstantdesc_child.ORIGIN)',
        '~$class_constant_notice_protected(S_child_static,porigin_base)',
        '$default_cache_at(S_child_static.CLASSCONSTANTCACHE,porigin_base) = (pdefaultcache)',
        '$default_cache_at(S_child_static.CLASSCONSTANTCACHE,pclassconstantdesc_child.ORIGIN) = eps',
        '$ccn_output(S_child_static.EVENTS) = $ptascii("S|B|7|L|B|7|S|B|7|L|")',
        '$error_call_valid(S_child_static,perrorcall_child_static)','$call_descriptors_valid(S_child_static)',
        'S_done = $drive_steps(S_child_static,30000)','S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = $base64('+json.dumps(base64.b64encode(expected).decode())+')',
        '$default_cache_at(S_done.CLASSCONSTANTCACHE,porigin_base) = (pdefaultcache)',
        '$default_cache_at(S_done.CLASSCONSTANTCACHE,pclassconstantdesc_child.ORIGIN) = eps',
        '~$class_constant_keyword_method(S_done,PORIGIN n_unit pcpath_self)',
        '$class_constant_state_valid(S_done)','$call_descriptors_valid(S_done)']
    return checks


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
        'tests/semantics/deprecated_class_constant_fetch_protocol.py', 'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py',
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
