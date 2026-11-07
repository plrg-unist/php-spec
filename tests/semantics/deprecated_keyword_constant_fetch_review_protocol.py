#!/usr/bin/env python3
"""Check parent constant selection and normal receiver lifetime."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_keyword_constant_fetch_review'
SELECTIONS = {'receiver': SOURCE / 'parent-receiver.php'}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
quoted = lambda value: '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'


def receiver(fixture, path):
    expected = json.loads((SOURCE / 'cases.json').read_text())[path.stem]['stdout']
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_warn = $interface_notice_review_pause(S_start[.COMPLETION = NORMAL],0,30000)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class ptbytes_member 10',
        'ptbytes_member = $ptascii("C")', 'perrorcall.LEVEL = 16384',
        'S_warn.ORIGIN = (perrorcall.SITE)',
        'S_warn.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = METHOD_TARGET n_receiver porigin_method',
        'pcallcontext.RECEIVER = (n_receiver)',
        'pcallcontext.LEXICAL_CLASS = (porigin_child)',
        'pcallcontext.CALLED_CLASS = (porigin_child)',
        '$target_function(S_warn,pcallcontext.TARGET) = (pfunction)',
        '$parameter_method_source(S_warn,pfunction) = (pmethoddesc)',
        'pmethoddesc.OWNER = porigin_child', 'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC',
        '$call_current_valid(S_warn)',
        '$class_at(S_warn.CLASSES,porigin_child) = (pclassdesc_child)',
        '$class_link_at(S_warn.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_parent)',
        '$class_at(S_warn.CLASSES,porigin_parent) = (pclassdesc_parent)',
        'pclassdesc_parent.NAME = ptbytes_class',
        '$class_constant_origin(S_warn.CLASSES,porigin_decl) = (pclassconstantdesc)',
        'pclassconstantdesc.OWNER = porigin_parent', '~pclassconstantdesc.FOLDED',
        '$origin_node(S_warn.SOURCES,perrorcall.SITE) = (NExprClassConstFetch name (NIdentifier (BYTES text_member) metadata_member) metadata)',
        '$ppscoped_keyword(name)', '$pfclassname_keyword(name) = $ptascii("parent")',
        '$scoped_source_name(S_warn,name) = (ptbytes_class)',
        '$class_constant_selected_valid(S_warn,name,KNOWN (PSTRING ptbytes_class))',
        '$class_constant_notice_valid(S_warn,porigin_decl,ptbytes_class,ptbytes_member,10)',
        '~$class_constant_notice_valid(S_warn,porigin_decl,pclassdesc_child.NAME,ptbytes_member,10)',
        '$class_constant_notice_protected(S_warn,porigin_decl)',
        'S_warn.CONSTCONTEXT = eps', 'S_warn.CLASSCONSTANTINIT = eps',
        '$default_cache_at(S_warn.CLASSCONSTANTCACHE,porigin_decl) = (pdefaultcache)',
        'pdefaultcache.VALUE = PARRAY n_donor',
        '$class_constant_row_payload_valid(S_warn,pclassconstantdesc,pdefaultcache)',
        '$task_nodes(perrorcall.RESUME) = eps', '$error_call_valid(S_warn,perrorcall)',
        '$call_descriptors_valid(S_warn)',
        'S_resume = $interface_notice_review_pause(S_warn,1,30000)',
        'S_resume.TODO = (DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class ptbytes_member 10) :: ptask_tail*',
        'S_resume.CURRENT = (pcallcontext)',
        'S_globals = $global_table_view(S_resume)',
        '$lookup(S_globals.ENV,$ptascii("receiver")) = (n_slot)',
        'S_globals.STORE[n_slot] = DEFINED PNULL',
        '(HOBJECT n_receiver) <- S_resume.ALLOCATIONS',
        '$heap_owners($heap_graph(S_resume),HOBJECT n_receiver) = 1',
        '$class_constant_notice_valid(S_resume,porigin_decl,ptbytes_class,ptbytes_member,10)',
        '~$class_constant_notice_valid(S_resume[.CURRENT = (pcallcontext[.LEXICAL_CLASS = (porigin_parent)])],porigin_decl,ptbytes_class,ptbytes_member,10)',
        '~$class_constant_notice_valid(S_resume[.CURRENT = (pcallcontext[.CALLED_CLASS = (porigin_parent)])],porigin_decl,ptbytes_class,ptbytes_member,10)',
        '~$class_constant_notice_valid(S_resume[.CURRENT = (pcallcontext[.TARGET = CLOSURE_TARGET n_receiver])],porigin_decl,ptbytes_class,ptbytes_member,10)',
        '$call_current_valid(S_resume)', '$call_descriptors_valid(S_resume)',
        'S_resume.RESULT =/= KNOWN (PARRAY n_donor)',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero.COMPLETION = BUDGET',
        'S_one = $drive_steps(S_resume,1)', 'S_one.COMPLETION = BUDGET',
        'S_after = S_one[.COMPLETION = NORMAL]',
        'S_after.CURRENT = (pcallcontext)', 'S_after.CLASSCONSTANTINIT = eps',
        'S_after.CONSTCONTEXT = eps', 'S_after.RESULT = KNOWN (PARRAY n_donor)',
        'S_after.CLASSCONSTANTCACHE = S_resume.CLASSCONSTANTCACHE',
        'S_after.CLASSCONSTANTHISTORY = S_resume.CLASSCONSTANTHISTORY',
        '$heap_owners($heap_graph(S_after),HARRAY n_donor) = $($heap_owners($heap_graph(S_resume),HARRAY n_donor) + 1)',
        '$heap_owners($heap_graph(S_after),HOBJECT n_receiver) = 1',
        '~$class_constant_notice_protected(S_after,porigin_decl)',
        '$call_current_valid(S_after)', '$call_descriptors_valid(S_after)',
        'S_warm = $interface_notice_review_pause(S_after,0,30000)',
        'S_warm.TODO = (ERROR_HANDLER_INVOKE perrorcall_warm) :: ptask_warm*',
        'perrorcall_warm.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class ptbytes_member 25',
        'S_warm.CURRENT = eps',
        '$interface_notice_review_output(S_warm.EVENTS) = $ptascii("H|D|R|1|")',
        '~((HOBJECT n_receiver) <- S_warm.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_warm),HOBJECT n_receiver) = 0',
        '$class_constant_history_valid(S_warm)',
        '$class_constant_row_payload_valid(S_warm,pclassconstantdesc,pdefaultcache)',
        'S_erased = S_warm[.OBJECTS = eps]',
        '$class_constant_history_valid(S_erased)',
        '$class_constant_row_payload_valid(S_erased,pclassconstantdesc,pdefaultcache)',
        'S_done = $drive(S_warm,30000)', 'S_done.COMPLETION = NORMAL',
        '$interface_notice_review_output(S_done.EVENTS) = ' + quoted(expected),
        '$class_constant_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        '$drive(S_zero[.COMPLETION = NORMAL],30000) = S_done',
        '$drive(S_one[.COMPLETION = NORMAL],30000) = S_done',
        '$machine_roots(S_done[.CLASSCONSTANTHISTORY = eps]) = $machine_roots(S_done)']


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
    (out / 'protocol.watsup').write_text(PREFIX + NOTICE + '\ndec $main() : bool\ndef $main() = true\n'
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
