#!/usr/bin/env python3
"""Check private metadata, handler access and denied keyword continuations."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_global_constant_protocol import PREFIX
from deprecated_class_constant_fetch_protocol import SELECTED as NOTICE_SELECTED
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT=Path(__file__).resolve().parents[2]
SELECTIONS={'private':ROOT/'tests/semantics/deprecated_nonpublic_class_constant/private-access.php'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SELECTED=NOTICE_SELECTED+r'''
dec $private_ready(pstate,porigin,nat) : bool
def $private_ready(S,porigin,0) = true
  -- if S.TODO = (CLASS_CONST_CLASS name (NIdentifier (BYTES text) metadata_member) z) :: ptask*
  -- if $base64(text) = $ptascii("SECRET")
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.LEXICAL_CLASS = eps
  -- if $class_constant_notice_protected(S,porigin)
def $private_ready(S,porigin,1) = true
  -- if S.TODO = (CLASS_CONST_CLASS name (NIdentifier (BYTES text) metadata_member) z) :: ptask*
  -- if $base64(text) = $ptascii("SECRET")
  -- if $ppscoped_keyword(name)
  -- if $class_constant_origin(S.CLASSES,porigin) = (pclassconstantdesc)
  -- if ~$class_constant_visible(S,pclassconstantdesc)
def $private_ready(S,porigin,n) = false -- otherwise
dec $private_pause(pstate,porigin,nat,nat) : pstate
def $private_pause(S,porigin,n_mode,n) = S -- if $private_ready(S,porigin,n_mode)
def $private_pause(S,porigin,n_mode,n) = $private_pause(S_next[.COMPLETION = NORMAL],porigin,n_mode,$nabs($(n - 1)))
  -- if ~$private_ready(S,porigin,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $private_pause(S,porigin,n_mode,n) = S -- otherwise
'''


def private(fixture,path):
    expected=json.loads((path.parent/'cases.json').read_text())[path.stem]['stdout']
    error=expected.split('|')[1]
    quoted=lambda v:'$base64('+json.dumps(base64.b64encode(v.encode()).decode())+')'
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(path)).decode())+')',
        'S_start.COMPLETION = BUDGET','S_warn = $ccn_pause(S_start[.COMPLETION = NORMAL],0,30000)','$ccn_ready(S_warn,0)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_private ptbytes_class ptbytes_member z',
        '$class_constant_origin(S_warn.CLASSES,porigin_private) = (pclassconstantdesc_private)',
        'pclassconstantdesc_private.VISIBILITY = PROPERTY_PRIVATE','pclassconstantdesc_private.FOLDED',
        'pclassconstantdesc_private.NAME = $ptascii("SECRET")',
        '$class_at(S_warn.CLASSES,pclassconstantdesc_private.OWNER) = (pclassdesc)',
        'pclassdesc.KIND = "class"','pclassdesc.CONSTANTS = [pclassconstantdesc_private,pclassconstantdesc_public]',
        'pclassconstantdesc_public.NAME = $ptascii("OPEN")','pclassconstantdesc_public.VISIBILITY = PROPERTY_PUBLIC',
        '$class_constant_deprecated(S_warn,pclassconstantdesc_private)','$class_constant_deprecated(S_warn,pclassconstantdesc_public)',
        '~$class_constant_deprecated(S_warn,pclassconstantdesc_private[.VISIBILITY = PROPERTY_PUBLIC])',
        '~$class_constant_deprecated(S_warn,pclassconstantdesc_private[.VISIBILITY = PROPERTY_PROTECTED])',
        '~$class_constant_deprecated(S_warn,pclassconstantdesc_public[.VISIBILITY = PROPERTY_PRIVATE])',
        '~$class_constant_deprecated(S_warn,pclassconstantdesc_public[.VISIBILITY = PROPERTY_PROTECTED])',
        '$class_constant_attribute_group(S_warn.SOURCES,pclassconstantdesc_private[.VISIBILITY = PROPERTY_PUBLIC]) =/= eps',
        '~$class_constant_inline_allowed(S_warn.SOURCES,pclassconstantdesc_private[.VISIBILITY = PROPERTY_PUBLIC])',
        '~$class_constant_query_readable(S_warn,pclassconstantdesc_private[.VISIBILITY = PROPERTY_PUBLIC])',
        '$class_constant_attribute_group(S_warn.SOURCES,pclassconstantdesc_public[.VISIBILITY = PROPERTY_PRIVATE]) =/= eps',
        '~$class_constant_inline_allowed(S_warn.SOURCES,pclassconstantdesc_public[.VISIBILITY = PROPERTY_PRIVATE])',
        '~$class_constant_query_readable(S_warn,pclassconstantdesc_public[.VISIBILITY = PROPERTY_PRIVATE])',
        '$method_current_scope(S_warn) = (pclassconstantdesc_private.OWNER)',
        '$class_constant_visible(S_warn,pclassconstantdesc_private)',
        '$class_constant_notice_valid(S_warn,porigin_private,ptbytes_class,ptbytes_member,z)',
        '$class_constant_notice_protected(S_warn,porigin_private)',
        '$call_task_valid(S_warn,perrorcall.RESUME)','$error_call_valid(S_warn,perrorcall)',
        'S_warn.RESULT = KNOWN PNULL','S_warn.CONSTCONTEXT = eps','S_warn.CLASSCONSTANTINIT = eps',
        '$task_nodes(perrorcall.RESUME) = eps',
        '$compiled_read(S_warn,pclassconstantdesc_private.INITIALIZER) = (PINT 7)',
        '$ccn_output(S_warn.EVENTS) = '+quoted('C|'+error+'|V|'),
        '$call_descriptors_valid(S_warn)',
        'S_handler = $private_pause(S_warn,porigin_private,0,30000)','$private_ready(S_handler,porigin_private,0)',
        'S_handler.TODO = (CLASS_CONST_CLASS name_handler (NIdentifier (BYTES text) metadata_member_handler) z_handler) :: ptask_handler*',
        '$method_current_scope(S_handler) = eps','~$ppscoped_keyword(name_handler)',
        '$class_constant_deprecated(S_handler,pclassconstantdesc_private)',
        '~$class_constant_visible(S_handler,pclassconstantdesc_private)',
        '$class_constant_notice_protected(S_handler,porigin_private)',
        '~$class_constant_notice_valid(S_handler,porigin_private,ptbytes_class,ptbytes_member,z_handler)',
        '~$call_task_valid(S_handler,DEPRECATED_CLASS_CONSTANT_RESULT porigin_private ptbytes_class ptbytes_member z_handler)',
        'PhpStep: S_handler ~> S_handler_raw',
        'S_handler_raw.COMPLETION = THROWN "Error" '+quoted(error)+' z_handler',
        'S_handler_raw.EVENTS = S_handler.EVENTS','S_handler_raw.CLASSCONSTANTCACHE = S_handler.CLASSCONSTANTCACHE',
        'S_handler_raw.CLASSCONSTANTHISTORY = S_handler.CLASSCONSTANTHISTORY',
        '$call_descriptors_valid(S_handler)',
        'S_bad = $private_pause(S_handler,porigin_private,1,30000)','$private_ready(S_bad,porigin_private,1)',
        'S_bad.TODO = (CLASS_CONST_CLASS name_bad (NIdentifier (BYTES text) metadata_member_bad) z_bad) :: ptask_bad*',
        'S_bad.ORIGIN = (porigin_bad)','$class_constant_keyword_method(S_bad,porigin_bad)',
        '$scoped_source_name(S_bad,name_bad) = (ptbytes_class)',
        '$class_constant_selected_valid(S_bad,name_bad,KNOWN (PSTRING ptbytes_class))',
        'S_bad.CURRENT = (pcallcontext_bad)',
        'pcallcontext_bad.LEXICAL_CLASS = (porigin_child)','porigin_child =/= pclassconstantdesc_private.OWNER',
        '$method_current_scope(S_bad) = (porigin_child)',
        '$class_constant_deprecated(S_bad,pclassconstantdesc_private)',
        '~$class_constant_visible(S_bad,pclassconstantdesc_private)',
        '~$class_constant_notice_protected(S_bad,porigin_private)',
        '~$class_constant_notice_valid(S_bad,porigin_private,ptbytes_class,ptbytes_member,z_bad)',
        '~$call_task_valid(S_bad,DEPRECATED_CLASS_CONSTANT_RESULT porigin_private ptbytes_class ptbytes_member z_bad)',
        'PhpStep: S_bad ~> S_bad_raw',
        'S_bad_raw.COMPLETION = THROWN "Error" '+quoted(error)+' z_bad',
        'S_bad_raw.EVENTS = S_bad.EVENTS','S_bad_raw.CLASSCONSTANTCACHE = S_bad.CLASSCONSTANTCACHE',
        'S_bad_raw.CLASSCONSTANTHISTORY = S_bad.CLASSCONSTANTHISTORY','$call_descriptors_valid(S_bad)',
        'S_done = $drive_steps(S_bad,30000)','S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = '+quoted(expected),
        '~$class_constant_notice_protected(S_done,porigin_private)',
        '$default_cache_at(S_done.CLASSCONSTANTCACHE,porigin_private) = eps',
        '$default_cache_at(S_done.CLASSCONSTANTCACHE,pclassconstantdesc_public.ORIGIN) = eps',
        '$class_constant_state_valid(S_done)','$call_descriptors_valid(S_done)']


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
    (out/'protocol.watsup').write_text(PREFIX+SELECTED+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- '+(c if c.startswith('PhpStep:') else 'if '+c)+'\n' for c in checks))
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
