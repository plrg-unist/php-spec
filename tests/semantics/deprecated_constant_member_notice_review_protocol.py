#!/usr/bin/env python3
"""Check dynamic constant member bytes through warning-time CV removal."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_constant_member_notice_review/interface-member.php'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
quoted = lambda value: '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'


SELECTED = FETCH_SELECTED + r'''
dec $member_notice_ready(pstate) : bool
def $member_notice_ready(S) = true
  -- if S.TODO = (CLASS_CONST_MEMBER name poperand_class 19) :: (CLASS_CONST_CAPTURE porigin poperand_class 19) :: ptask*
def $member_notice_ready(S) = false -- otherwise
dec $member_notice_pause(pstate,nat) : pstate
def $member_notice_pause(S,n) = S -- if $member_notice_ready(S)
def $member_notice_pause(S,n) = $member_notice_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$member_notice_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $member_notice_pause(S,n) = S -- otherwise
'''


def member(fixture):
    expected = json.loads((SOURCE.parent / 'cases.json').read_text())[SOURCE.stem]['stdout']
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(SOURCE)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_member = $member_notice_pause(S_start[.COMPLETION = NORMAL],30000)', '$member_notice_ready(S_member)',
        'S_member.TODO = (CLASS_CONST_MEMBER name poperand_class 19) :: (CLASS_CONST_CAPTURE porigin_site poperand_class 19) :: ptask_member*',
        'S_member.ORIGIN = (porigin_site)',
        '$origin_node(S_member.SOURCES,porigin_site) = (NExprClassConstFetch name (NExprVariable (BYTES text_variable) metadata_variable) metadata_fetch)',
        '$base64(text_variable) = $ptascii("member222")',
        'S_member.RESULT = VARIABLE $ptascii("member222") z_variable',
        'poperand_class = KNOWN (PSTRING ptbytes_class)',
        'ptbytes_class = ' + quoted('Ns222Member\\Child222'),
        '$class_constant_selected_valid(S_member,name,poperand_class)',
        'S_read = $resolve_at(S_member,S_member.RESULT,19)', 'S_read.COMPLETION = NORMAL',
        'S_read.RESULT = KNOWN (PSTRING_CARRIER (REQUEST_STRING n_input) ptbytes_member)',
        'ptbytes_member = $ptascii("C")',
        'pvalue_member = PSTRING_CARRIER (REQUEST_STRING n_input) ptbytes_member',
        '$string_carrier_valid(S_read,pvalue_member)', '$value_nodes(pvalue_member) = eps',
        '$string_bytes(pvalue_member) = (ptbytes_member)',
        '$class_named(S_read.CLASSNAMES,$ptlc(ptbytes_class)) = (porigin_requested)',
        '$class_constant_lookup(S_read,porigin_requested,ptbytes_member,|S_read.CLASSES|) = (pclassconstantdesc)',
        'porigin_decl = pclassconstantdesc.ORIGIN',
        '$class_at(S_read.CLASSES,pclassconstantdesc.OWNER) = (pclassdesc_owner)',
        'pclassdesc_owner.KIND = "interface"',
        'pclassconstantdesc.OWNERNAME = ' + quoted('Ns222Member\\Base222'),
        'pclassconstantdesc.FOLDED', 'pclassconstantdesc.VISIBILITY = PROPERTY_PUBLIC',
        '$compiled_read(S_read,pclassconstantdesc.INITIALIZER) = (PARRAY n_donor)',
        'S_read.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        'S_member.CURRENT = eps', 'S_member.CONSTCONTEXT = eps', 'S_member.EVENTS = eps',
        '$class_constant_notice_valid(S_read,porigin_decl,ptbytes_class,ptbytes_member,19)',
        '~$class_constant_notice_valid(S_member,porigin_decl,ptbytes_class,ptbytes_member,19)',
        '$call_descriptors_valid(S_member)',
        'S_warn_raw = $drive_steps(S_member,1)', 'S_warn_raw.COMPLETION = BUDGET',
        'S_warn = S_warn_raw[.COMPLETION = NORMAL]', '$ccn_ready(S_warn,0)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class ptbytes_member 19',
        'S_warn.RESULT = KNOWN PNULL',
        '$class_constant_cv_pending(ERROR_HANDLER_INVOKE perrorcall) = ((porigin_decl,ptbytes_class,ptbytes_member,19))',
        '$class_constant_notice_valid(S_warn,porigin_decl,ptbytes_class,ptbytes_member,19)',
        'perrorcall.LEVEL = 16384', 'perrorcall.LINE = 19',
        'perrorcall.MESSAGE = $class_constant_notice_message(pclassconstantdesc,ptbytes_member)',
        '$error_call_valid(S_warn,perrorcall)', '$call_descriptors_valid(S_warn)',
        '$task_nodes(perrorcall.RESUME) = eps',
        '$class_constant_notice_protected(S_warn,porigin_decl)',
        'S_warn.CLASSCONSTANTINIT = eps', 'S_warn.CLASSCONSTANTCACHE = eps',
        'S_global_warn = $global_table_view(S_warn)',
        '$lookup(S_global_warn.ENV,$ptascii("member222")) = (n_member)',
        'S_global_warn.STORE[n_member] = DEFINED pvalue_member',
        'S_resume = $ccn_pause(S_warn,1,30000)', '$ccn_ready(S_resume,1)',
        '$ccn_output(S_resume.EVENTS) = $ptascii("H|")',
        'S_resume.TODO = perrorcall.RESUME :: ptask_resume*',
        'S_global_resume = $global_table_view(S_resume)',
        '$lookup(S_global_resume.ENV,$ptascii("member222")) = eps',
        '$class_constant_notice_valid(S_resume,porigin_decl,ptbytes_class,ptbytes_member,19)',
        '$call_task_valid(S_resume,perrorcall.RESUME)', '$call_descriptors_valid(S_resume)',
        '~$class_constant_notice_valid(S_resume,porigin_decl,ptbytes_class,ptbytes_member,6)',
        '~$error_call_valid(S_warn,perrorcall[.LINE = 6])',
        'S_resume.CLASSCONSTANTINIT = eps', 'S_resume.CLASSCONSTANTCACHE = eps',
        'S_resume.CLASSCONSTANTHISTORY = S_warn.CLASSCONSTANTHISTORY',
        'n_before = $heap_owners($heap_graph(S_resume),HARRAY n_donor)',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_resume',
        'S_one_raw = $drive_steps(S_resume,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]', 'S_one.RESULT = KNOWN (PARRAY n_donor)',
        '$heap_owners($heap_graph(S_one),HARRAY n_donor) = $(n_before + 1)',
        '~$class_constant_notice_protected(S_one,porigin_decl)',
        'S_warm = $ccn_pause(S_one,0,30000)', '$ccn_ready(S_warm,0)',
        'S_warm.TODO = (ERROR_HANDLER_INVOKE perrorcall_warm) :: ptask_warm*',
        'perrorcall_warm.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_warm_class ptbytes_member 23',
        'ptbytes_warm_class = ' + quoted('Ns222Member\\Implementer222'),
        'perrorcall_warm.MESSAGE = perrorcall.MESSAGE', '$error_call_valid(S_warm,perrorcall_warm)',
        '$ccn_output(S_warm.EVENTS) = $ptascii("H|O|1|M|7|")',
        'S_warm.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        'S_done = $drive(S_warm,30000)', 'S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = ' + quoted(expected),
        'S_global_done = $global_table_view(S_done)',
        '$lookup(S_global_done.ENV,$ptascii("member222")) = eps',
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
    checks = member(checked['fixture'])
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
