#!/usr/bin/env python3
"""Check selected object-class bytes through notice-time source retirement."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_global_constant_protocol import PREFIX
from deprecated_class_constant_fetch_protocol import SELECTED as FETCH_SELECTED
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'tests/semantics/deprecated_class_selector_notice_review/object-selector.php'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
quoted = lambda value: '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'


SELECTED = FETCH_SELECTED + r'''
dec $selector_notice_ready(pstate) : bool
def $selector_notice_ready(S) = true
  -- if S.TODO = (CLASS_CONST_CLASS (NExprVariable (BYTES text) metadata_class) (NIdentifier (BYTES text_member) metadata_member) 20) :: ptask*
  -- if $base64(text) = $ptascii("selector221")
  -- if $base64(text_member) = $ptascii("C")
def $selector_notice_ready(S) = false -- otherwise
dec $selector_notice_pause(pstate,nat) : pstate
def $selector_notice_pause(S,n) = S -- if $selector_notice_ready(S)
def $selector_notice_pause(S,n) = $selector_notice_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$selector_notice_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $selector_notice_pause(S,n) = S -- otherwise
'''


def object_selector(fixture):
    expected = json.loads((SOURCE.parent / 'cases.json').read_text())[SOURCE.stem]['stdout']
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(SOURCE)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_selected = $selector_notice_pause(S_start[.COMPLETION = NORMAL],30000)',
        '$selector_notice_ready(S_selected)',
        'S_selected.CURRENT = eps',
        'S_selected.ORIGIN = (porigin_site)',
        '$origin_node(S_selected.SOURCES,porigin_site) = (NExprClassConstFetch (NExprVariable (BYTES text_cv) metadata_class) (NIdentifier (BYTES text_member) metadata_member) metadata_fetch)',
        '$base64(text_cv) = $ptascii("selector221")', '$base64(text_member) = $ptascii("C")',
        'S_read = $resolve_at(S_selected,S_selected.RESULT,20)',
        'S_read.RESULT = KNOWN (POBJECT n_source)',
        '(HOBJECT n_source) <- S_read.ALLOCATIONS',
        '$object_class_origin(S_read,n_source) = (porigin_selected)',
        '$class_at(S_read.CLASSES,porigin_selected) = (pclassdesc_selected)',
        'pclassdesc_selected.NAME = ' + quoted('Ns221Object\\Selector221'),
        'S_warn_raw = $drive_steps(S_selected,1)', 'S_warn_raw.COMPLETION = BUDGET',
        'S_warn = S_warn_raw[.COMPLETION = NORMAL]', '$ccn_ready(S_warn,0)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class ptbytes_member 20',
        'ptbytes_class = pclassdesc_selected.NAME', 'ptbytes_member = $ptascii("C")',
        '$class_constant_origin(S_warn.CLASSES,porigin_decl) = (pclassconstantdesc)',
        '$class_at(S_warn.CLASSES,pclassconstantdesc.OWNER) = (pclassdesc_owner)',
        'pclassdesc_owner.KIND = "interface"',
        'pclassconstantdesc.OWNERNAME = ' + quoted('Ns221Object\\Base221'),
        'pclassconstantdesc.FOLDED', 'pclassconstantdesc.VISIBILITY = PROPERTY_PUBLIC',
        '$class_constant_lookup(S_warn,porigin_selected,ptbytes_member,|S_warn.CLASSES|) = (pclassconstantdesc)',
        '$compiled_read(S_warn,pclassconstantdesc.INITIALIZER) = (PARRAY n_donor)',
        'S_warn.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        '$default_cache_at(S_warn.CLASSCONSTANTCACHE,porigin_decl) = eps',
        'S_warn.CLASSCONSTANTINIT = eps', 'S_warn.CONSTCONTEXT = eps',
        'S_warn.CURRENT = eps', '$call_context_roots(S_warn.CURRENT) = eps',
        'S_warn.RESULT = KNOWN PNULL', '$task_nodes(perrorcall.RESUME) = eps',
        '$heap_owners($heap_graph(S_warn),HOBJECT n_source) = 1',
        'S_global_warn = $global_table_view(S_warn)',
        '$lookup(S_global_warn.ENV,$ptascii("selector221")) = (n_selector)',
        'S_global_warn.STORE[n_selector] = DEFINED (POBJECT n_source)',
        '$class_constant_notice_valid(S_warn,porigin_decl,ptbytes_class,ptbytes_member,20)',
        'perrorcall.MESSAGE = $class_constant_notice_message(pclassconstantdesc,ptbytes_member)',
        'perrorcall.LEVEL = 16384', 'perrorcall.LINE = 20',
        '$error_call_valid(S_warn,perrorcall)', '$call_descriptors_valid(S_warn)',
        '~$class_constant_notice_valid(S_warn,porigin_decl,ptbytes_class,$ptascii("OTHER"),20)',
        '~$class_constant_notice_valid(S_warn,porigin_decl,ptbytes_class,ptbytes_member,6)',
        '$class_constant_notice_protected(S_warn,porigin_decl)',
        'S_resume = $ccn_pause(S_warn,1,30000)', '$ccn_ready(S_resume,1)',
        '$ccn_output(S_resume.EVENTS) = $ptascii("H|D|")',
        '~((HOBJECT n_source) <- S_resume.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_resume),HOBJECT n_source) = 0',
        'S_global_resume = $global_table_view(S_resume)',
        '$lookup(S_global_resume.ENV,$ptascii("selector221")) = (n_selector_resume)',
        'S_global_resume.STORE[n_selector_resume] = DEFINED PNULL',
        'S_resume.TODO = perrorcall.RESUME :: ptask_resume*',
        '$class_constant_notice_valid(S_resume,porigin_decl,ptbytes_class,ptbytes_member,20)',
        '~$class_constant_notice_valid(S_resume[.RESULT = KNOWN (PSTRING pclassconstantdesc.OWNERNAME)],porigin_decl,pclassconstantdesc.OWNERNAME,ptbytes_member,20)',
        '$call_task_valid(S_resume,perrorcall.RESUME)', '$call_descriptors_valid(S_resume)',
        '$class_constant_notice_valid(S_resume[.OBJECTS = eps],porigin_decl,ptbytes_class,ptbytes_member,20)',
        'S_resume.CLASSCONSTANTINIT = eps', 'S_resume.CLASSCONSTANTCACHE = eps',
        'S_resume.CLASSCONSTANTHISTORY = S_warn.CLASSCONSTANTHISTORY',
        'n_before = $heap_owners($heap_graph(S_resume),HARRAY n_donor)',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_resume',
        'S_one_raw = $drive_steps(S_resume,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]',
        'S_one.RESULT = KNOWN (PARRAY n_donor)',
        '$heap_owners($heap_graph(S_one),HARRAY n_donor) = $(n_before + 1)',
        '~$class_constant_notice_protected(S_one,porigin_decl)',
        'S_one.CLASSCONSTANTCACHE = eps',
        'S_warm = $ccn_pause(S_one,0,30000)', '$ccn_ready(S_warm,0)',
        'S_warm.TODO = (ERROR_HANDLER_INVOKE perrorcall_warm) :: ptask_warm*',
        'perrorcall_warm.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl pclassconstantdesc.OWNERNAME ptbytes_member 24',
        'perrorcall_warm.MESSAGE = perrorcall.MESSAGE', '$error_call_valid(S_warm,perrorcall_warm)',
        '$ccn_output(S_warm.EVENTS) = $ptascii("H|D|O|1|M|7|")',
        'S_warm.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        '~((HOBJECT n_source) <- S_warm.ALLOCATIONS)',
        'S_done = $drive(S_warm,30000)', 'S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = ' + quoted(expected),
        'S_global_done = $global_table_view(S_done)',
        '$lookup(S_global_done.ENV,$ptascii("value")) = (n_value)',
        '$lookup(S_global_done.ENV,$ptascii("again")) = (n_again)',
        'S_global_done.STORE[n_value] = DEFINED (PARRAY n_copy)',
        'S_global_done.STORE[n_again] = DEFINED (PARRAY n_donor)', 'n_copy =/= n_donor',
        'S_done.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
        'S_done.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        'S_done.CLASSCONSTANTCACHE = eps', 'S_done.CLASSCONSTANTINIT = eps',
        'S_done.CLASSCONSTANTHISTORY = S_warn.CLASSCONSTANTHISTORY',
        '~$class_constant_notice_protected(S_done,porigin_decl)',
        '$class_constant_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        '$drive(S_resume,30000) = S_done', '$drive(S_zero[.COMPLETION = NORMAL],30000) = S_done',
        '$drive(S_one,30000) = S_done']


def prepare(out):
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
        str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(SOURCE.read_bytes()).decode()})
        assert parsed['accepted'] and not parsed['diagnostics']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
    finally:
        try: adapter.close()
        finally: frontend.close()
    checks = object_selector(checked['fixture'])
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + SELECTED
        + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), SOURCE, SOURCE.parent / 'cases.json', *modules, *(ROOT / path for path in (
        'spec/semantics/modules.json', 'spec/schema.json', 'frontend/worker.php',
        'tests/semantics/deprecated_class_constant_fetch_protocol.py',
        'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py',
        'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py',
        '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        report['premises'] = prepare(out)
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
