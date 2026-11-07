#!/usr/bin/env python3
"""Check parent member selection, shared-CV mutation and normal receiver lifetime."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_global_constant_protocol import PREFIX
from deprecated_interface_constant_read_review_protocol import EXTRA as NOTICE
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tests/semantics/deprecated_keyword_member_cv_review'
SELECTIONS = {'receiver': SOURCE / 'parent-member.php'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
quoted = lambda value: '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'

PAIR = r'''
dec $keyword_parent_member_ready(pstate) : bool
def $keyword_parent_member_ready(S) = true
  -- if S.TODO = (CLASS_CONST_MEMBER name poperand_class 11) :: (CLASS_CONST_CAPTURE porigin poperand_class 11) :: ptask*
  -- if $ppscoped_keyword(name)
def $keyword_parent_member_ready(S) = false -- otherwise
dec $keyword_parent_member_pause(pstate,nat) : pstate
def $keyword_parent_member_pause(S,n) = S -- if $keyword_parent_member_ready(S)
def $keyword_parent_member_pause(S,n) = $keyword_parent_member_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$keyword_parent_member_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $keyword_parent_member_pause(S,n) = S -- otherwise
'''


def receiver(fixture, path):
    expected = json.loads((SOURCE / 'cases.json').read_text())[path.stem]['stdout']
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_pair = $keyword_parent_member_pause(S_start[.COMPLETION = NORMAL],30000)',
        '$keyword_parent_member_ready(S_pair)',
        'S_pair.TODO = (CLASS_CONST_MEMBER name poperand_class 11) :: (CLASS_CONST_CAPTURE porigin_site poperand_class 11) :: ptask_pair*',
        'S_pair.ORIGIN = (porigin_site)',
        '$origin_node(S_pair.SOURCES,porigin_site) = (NExprClassConstFetch name (NExprVariable (BYTES text_member) metadata_member) metadata_fetch)',
        '$base64(text_member) = $ptascii("member224")',
        '$pfclassname_keyword(name) = $ptascii("parent")',
        'poperand_class = KNOWN (PSTRING ptbytes_class)',
        'ptbytes_class = ' + quoted('Ns224Parent\\Base224'),
        '$class_constant_keyword_method(S_pair,porigin_site)',
        '$class_constant_selected_valid(S_pair,name,poperand_class)',
        'S_read = $resolve_at(S_pair,S_pair.RESULT,11)', 'S_read.COMPLETION = NORMAL',
        'S_read.RESULT = KNOWN pvalue_member',
        '$string_bytes(pvalue_member) = ($ptascii("A"))',
        '$class_named(S_read.CLASSNAMES,$ptlc(ptbytes_class)) = (porigin_parent)',
        '$class_constant_lookup(S_read,porigin_parent,$ptascii("A"),|S_read.CLASSES|) = (pclassconstantdesc)',
        'porigin_decl = pclassconstantdesc.ORIGIN', 'pclassconstantdesc.OWNER = porigin_parent',
        'pclassconstantdesc.VISIBILITY = PROPERTY_PUBLIC', 'pclassconstantdesc.FOLDED',
        '$compiled_read(S_read,pclassconstantdesc.INITIALIZER) = (PARRAY n_donor)',
        'S_read.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        '$class_constant_notice_valid(S_read,porigin_decl,ptbytes_class,$ptascii("A"),11)',
        '~$class_constant_notice_valid(S_pair,porigin_decl,ptbytes_class,$ptascii("A"),11)',
        '$call_descriptors_valid(S_pair)',
        'S_warn_raw = $drive_steps(S_pair,1)', 'S_warn_raw.COMPLETION = BUDGET',
        'S_warn = S_warn_raw[.COMPLETION = NORMAL]',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class ptbytes_member 11',
        'ptbytes_member = $ptascii("A")', 'perrorcall.LEVEL = 16384', 'perrorcall.LINE = 11',
        'S_warn.ORIGIN = (perrorcall.SITE)', 'perrorcall.SITE = porigin_site',
        'S_warn.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = METHOD_TARGET n_receiver porigin_method',
        'pcallcontext.RECEIVER = (n_receiver)',
        'pcallcontext.LEXICAL_CLASS = (porigin_child)',
        'pcallcontext.CALLED_CLASS = (porigin_child)',
        '$target_function(S_warn,pcallcontext.TARGET) = (pfunction)',
        '$parameter_method_source(S_warn,pfunction) = (pmethoddesc)',
        'pmethoddesc.OWNER = porigin_child', 'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC',
        '$call_current_valid(S_warn)',
        '$class_link_at(S_warn.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_parent)',
        '$scoped_source_name(S_warn,name) = (ptbytes_class)',
        '$class_constant_keyword_method(S_warn,porigin_site)',
        '$class_constant_notice_valid(S_warn,porigin_decl,ptbytes_class,ptbytes_member,11)',
        '~$class_constant_notice_valid(S_warn,porigin_decl,' + quoted('Ns224Parent\\Child224') + ',ptbytes_member,11)',
        '$class_constant_notice_protected(S_warn,porigin_decl)',
        'S_warn.CONSTCONTEXT = eps', 'S_warn.CLASSCONSTANTINIT = eps', 'S_warn.CLASSCONSTANTCACHE = eps',
        '$task_nodes(perrorcall.RESUME) = eps', '$error_call_valid(S_warn,perrorcall)',
        '~$error_call_valid(S_warn,perrorcall[.LINE = 6])',
        '$call_descriptors_valid(S_warn)',
        'S_resume = $interface_notice_review_pause(S_warn,1,30000)',
        'S_resume.TODO = perrorcall.RESUME :: ptask_resume*',
        'S_resume.CURRENT = (pcallcontext)',
        '$interface_notice_review_output(S_resume.EVENTS) = $ptascii("H|")',
        'S_globals = $global_table_view(S_resume)',
        '$lookup(S_globals.ENV,$ptascii("receiver224")) = (n_receiver_slot)',
        'S_globals.STORE[n_receiver_slot] = DEFINED PNULL',
        '$lookup(S_globals.ENV,$ptascii("member224")) = (n_member_slot)',
        'S_globals.STORE[n_member_slot] = DEFINED PNULL',
        'S_member_now = $resolve_at(S_resume,VARIABLE $ptascii("member224") 11,11)',
        'S_member_now.RESULT = KNOWN PNULL',
        '(HOBJECT n_receiver) <- S_resume.ALLOCATIONS',
        '$heap_owners($heap_graph(S_resume),HOBJECT n_receiver) = 1',
        '$class_constant_keyword_method(S_resume,porigin_site)',
        '$class_constant_notice_valid(S_resume,porigin_decl,ptbytes_class,ptbytes_member,11)',
        '~$class_constant_notice_valid(S_resume,porigin_decl,ptbytes_class,ptbytes_member,6)',
        '~$class_constant_notice_valid(S_resume[.CURRENT = (pcallcontext[.LEXICAL_CLASS = (porigin_parent)])],porigin_decl,ptbytes_class,ptbytes_member,11)',
        '~$class_constant_notice_valid(S_resume[.CURRENT = (pcallcontext[.CALLED_CLASS = (porigin_parent)])],porigin_decl,ptbytes_class,ptbytes_member,11)',
        '~$class_constant_notice_valid(S_resume[.CURRENT = (pcallcontext[.TARGET = CLOSURE_TARGET n_receiver])],porigin_decl,ptbytes_class,ptbytes_member,11)',
        '~$class_constant_keyword_method(S_resume[.CURRENT = eps],porigin_site)',
        '~$class_constant_keyword_method(S_resume[.CONSTCONTEXT = ({ORIGIN porigin_decl,LINE 11,FACTS eps})],porigin_site)',
        '$call_current_valid(S_resume)', '$call_descriptors_valid(S_resume)',
        'S_resume.RESULT =/= KNOWN (PARRAY n_donor)',
        'S_resume.CLASSCONSTANTCACHE = eps',
        'S_resume.CLASSCONSTANTHISTORY = S_warn.CLASSCONSTANTHISTORY',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_resume',
        'S_one = $drive_steps(S_resume,1)', 'S_one.COMPLETION = BUDGET',
        'S_after = S_one[.COMPLETION = NORMAL]',
        'S_after.CURRENT = (pcallcontext)', 'S_after.CLASSCONSTANTINIT = eps',
        'S_after.CONSTCONTEXT = eps', 'S_after.RESULT = KNOWN (PARRAY n_donor)',
        'S_after.CLASSCONSTANTCACHE = eps',
        'S_after.CLASSCONSTANTHISTORY = S_resume.CLASSCONSTANTHISTORY',
        '$heap_owners($heap_graph(S_after),HARRAY n_donor) = $($heap_owners($heap_graph(S_resume),HARRAY n_donor) + 1)',
        '$heap_owners($heap_graph(S_after),HOBJECT n_receiver) = 1',
        '~$class_constant_notice_protected(S_after,porigin_decl)',
        '$call_current_valid(S_after)', '$call_descriptors_valid(S_after)',
        'S_warm = $interface_notice_review_pause(S_after,0,30000)',
        'S_warm.TODO = (ERROR_HANDLER_INVOKE perrorcall_warm) :: ptask_warm*',
        'perrorcall_warm.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class ptbytes_member 29',
        'S_warm.CURRENT = eps',
        '$interface_notice_review_output(S_warm.EVENTS) = $ptascii("H|D|R|1|M|7|")',
        '~((HOBJECT n_receiver) <- S_warm.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_warm),HOBJECT n_receiver) = 0',
        'S_warm.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        '$class_constant_history_valid(S_warm)',
        'S_done = $drive(S_warm,30000)', 'S_done.COMPLETION = NORMAL',
        '$interface_notice_review_output(S_done.EVENTS) = ' + quoted(expected),
        'S_globals_done = $global_table_view(S_done)',
        '$lookup(S_globals_done.ENV,$ptascii("value")) = (n_value_slot)',
        '$lookup(S_globals_done.ENV,$ptascii("again")) = (n_again_slot)',
        'S_globals_done.STORE[n_value_slot] = DEFINED (PARRAY n_copy)',
        'S_globals_done.STORE[n_again_slot] = DEFINED (PARRAY n_donor)',
        'n_copy =/= n_donor',
        'S_done.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
        'S_done.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        'S_done.CLASSCONSTANTCACHE = eps', 'S_done.CLASSCONSTANTINIT = eps',
        'S_done.CLASSCONSTANTHISTORY = S_warn.CLASSCONSTANTHISTORY',
        '~$class_constant_notice_protected(S_done,porigin_decl)',
        '~$class_constant_keyword_method(S_done,porigin_site)',
        '$class_constant_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        '$drive(S_zero[.COMPLETION = NORMAL],30000) = S_done',
        '$drive(S_one[.COMPLETION = NORMAL],30000) = S_done']


def prepare(out, group):
    path = SELECTIONS[group]
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
        str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(path.read_bytes()).decode()})
        assert parsed['accepted'] and not parsed['diagnostics']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok']
    finally:
        try: adapter.close()
        finally: frontend.close()
    checks = globals()[group](checked['fixture'], path)
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + NOTICE + PAIR + '\ndec $main() : bool\ndef $main() = true\n'
        + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--group', required=True, choices=tuple(SELECTIONS))
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), SELECTIONS[args.group], SOURCE / 'cases.json', *modules, *(ROOT / path for path in (
        'spec/semantics/modules.json', 'spec/schema.json', 'frontend/worker.php',
        'tests/semantics/deprecated_interface_constant_read_review_protocol.py',
        'tests/semantics/deprecated_global_constant_protocol.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py',
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
