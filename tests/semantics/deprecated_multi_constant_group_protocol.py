#!/usr/bin/env python3
"""Check multi-item group origins, sibling guards and compiler boundaries."""
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
SELECTIONS={'class':ROOT/'tests/semantics/deprecated_multi_constant_group/class-sibling-guards.php'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SELECTED=NOTICE_SELECTED+r'''
dec $group_ready(pstate) : bool
def $group_ready(S) = true
  -- if S.CURRENT = eps
  -- if $ccn_output(S.EVENTS) = $ptascii("H|A|a|7|b|8|7|")
def $group_ready(S) = false -- otherwise
dec $group_pause(pstate,nat) : pstate
def $group_pause(S,n) = S -- if $group_ready(S)
def $group_pause(S,n) = $group_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$group_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $group_pause(S,n) = S -- otherwise
'''


def class_group(fixture,path):
    expected=json.loads((path.parent/'cases.json').read_text())[path.stem]['stdout'].encode()
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(path)).decode())+')',
        'S_start.COMPLETION = BUDGET','S_first = $ccn_pause(S_start[.COMPLETION = NORMAL],0,30000)','$ccn_ready(S_first,0)',
        'S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_first*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_first ptbytes_requested ptbytes_member z',
        '$class_constant_origin(S_first.CLASSES,porigin_first) = (pclassconstantdesc_first)',
        '$class_at(S_first.CLASSES,pclassconstantdesc_first.OWNER) = (pclassdesc)',
        'pclassdesc.KIND = "class"','pclassdesc.CONSTANTS = [pclassconstantdesc_first,pclassconstantdesc_second]',
        'pclassconstantdesc_first.NAME = $ptascii("FIRST")','pclassconstantdesc_second.NAME = $ptascii("SECOND")',
        'pclassconstantdesc_second.OWNER = pclassconstantdesc_first.OWNER',
        'pclassconstantdesc_first.ORIGIN = PORIGIN n_unit pcpath_first',
        'pclassconstantdesc_second.ORIGIN = PORIGIN n_unit pcpath_second',
        'pclassconstantdesc_first.ORIGIN =/= pclassconstantdesc_second.ORIGIN',
        '$class_constant_attribute_group(S_first.SOURCES,pclassconstantdesc_first) = ((PORIGIN n_unit pcpath_group,phpType15*))',
        '$class_constant_attribute_group(S_first.SOURCES,pclassconstantdesc_second) = ((PORIGIN n_unit pcpath_group,phpType15*))',
        'pcpath_first = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        'pcpath_second = pcpath_group ++ [PCFIELD 3,PCINDEX 1]',
        '$origin_node(S_first.SOURCES,PORIGIN n_unit pcpath_group) = (NStmtClassConst (SEQUENCE phpType15*) phpType24 phpType18 (SEQUENCE ([phpType46_first,phpType46_second])) metadata_group)',
        '$source_line(metadata_group) = 5',
        'phpType46_first = NConst phpType11_first expression_first metadata_first',
        'phpType46_second = NConst phpType11_second expression_second metadata_second',
        '$source_line(metadata_first) = 7','$source_line(metadata_second) = 8',
        'pclassconstantdesc_first.LINE = 7','pclassconstantdesc_second.LINE = 7',
        '$class_constant_deprecated(S_first,pclassconstantdesc_first)','$class_constant_deprecated(S_first,pclassconstantdesc_second)',
        '~$class_constant_deprecated(S_first,pclassconstantdesc_second[.VISIBILITY = PROPERTY_PRIVATE])',
        '$class_constant_attribute_group(S_first.SOURCES,pclassconstantdesc_second[.NAME = $ptascii("FIRST")]) = eps',
        '~pclassconstantdesc_first.FOLDED','pclassconstantdesc_second.FOLDED',
        '$compiled_read(S_first,pclassconstantdesc_second.INITIALIZER) = (PINT 8)',
        '~$class_constant_inline_allowed(S_first.SOURCES,pclassconstantdesc_first)',
        '~$class_constant_inline_allowed(S_first.SOURCES,pclassconstantdesc_second)',
        '$class_constant_compile_value(S_first,pclassconstantdesc_second) = eps',
        '$class_constant_notice_protected(S_first,porigin_first)',
        '~$class_constant_notice_protected(S_first,pclassconstantdesc_second.ORIGIN)',
        '~$class_constant_notice_task(perrorcall.RESUME,pclassconstantdesc_second.ORIGIN)',
        'S_first.CLASSCONSTANTINIT = eps','S_first.CONSTCONTEXT = eps','S_first.RESULT = KNOWN PNULL',
        '$default_cache_at(S_first.CLASSCONSTANTCACHE,porigin_first) = eps',
        '$task_nodes(perrorcall.RESUME) = eps','$error_call_valid(S_first,perrorcall)',
        '$call_descriptors_valid(S_first)',
        'S_child = $ccn_pause(S_first,2,30000)','$ccn_ready(S_child,2)',
        'S_child.TODO = (CLASS_CONST_BIND porigin_first) :: ptask_child*',
        'S_child.CLASSCONSTANTINIT = [pclassconstantcontext]',
        'pclassconstantcontext.DECL = porigin_first',
        'pclassconstantcontext.SELECTION = CLASS_CONST_FETCH poperand ptbytes_member',
        '$class_constant_notice_protected(S_child,porigin_first)',
        '~$class_constant_notice_protected(S_child,pclassconstantdesc_second.ORIGIN)',
        'S_child.RESULT = KNOWN (PINT 7)','$ccn_output(S_child.EVENTS) = $ptascii("H|A|a|")',
        '$call_descriptors_valid(S_child)',
        'S_after_first = $group_pause(S_child,30000)','$group_ready(S_after_first)',
        '$default_cache_at(S_after_first.CLASSCONSTANTCACHE,porigin_first) = (pdefaultcache)',
        'pdefaultcache.VALUE = PINT 7',
        '$default_cache_at(S_after_first.CLASSCONSTANTCACHE,pclassconstantdesc_second.ORIGIN) = eps',
        '~$class_constant_notice_protected(S_after_first,porigin_first)',
        '~$class_constant_notice_protected(S_after_first,pclassconstantdesc_second.ORIGIN)',
        '$class_constant_compile_value(S_after_first,pclassconstantdesc_first) = eps',
        '$call_descriptors_valid(S_after_first)',
        'S_second = $ccn_pause(S_after_first,0,30000)','$ccn_ready(S_second,0)',
        'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_second*',
        'perrorcall_second.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc_second.ORIGIN ptbytes_requested_second ptbytes_member_second z_second',
        'perrorcall_second.MESSAGE = $class_constant_notice_message(pclassconstantdesc_second,ptbytes_member_second)',
        'ptbytes_member_second = $ptascii("SECOND")','perrorcall_second.LEVEL = 16384','z_second = 22',
        '$class_constant_notice_protected(S_second,pclassconstantdesc_second.ORIGIN)',
        '~$class_constant_notice_protected(S_second,porigin_first)',
        'S_second.CLASSCONSTANTCACHE = S_after_first.CLASSCONSTANTCACHE',
        '$error_call_valid(S_second,perrorcall_second)','$call_descriptors_valid(S_second)',
        'S_done = $drive_steps(S_second,30000)','S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = $base64('+json.dumps(base64.b64encode(expected).decode())+')',
        '~$class_constant_notice_protected(S_done,porigin_first)',
        '~$class_constant_notice_protected(S_done,pclassconstantdesc_second.ORIGIN)',
        '$class_constant_state_valid(S_done)','$call_descriptors_valid(S_done)',
        '$default_cache_at(S_done.CLASSCONSTANTCACHE,porigin_first) = (pdefaultcache)',
        '$default_cache_at(S_done.CLASSCONSTANTCACHE,pclassconstantdesc_second.ORIGIN) = eps']


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
    checks=class_group(checked['fixture'],path)
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
