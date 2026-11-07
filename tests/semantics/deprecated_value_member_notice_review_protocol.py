#!/usr/bin/env python3
"""Check completed composed rvalues and tuple-only Deprecated resumption."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_value_member_notice_review/composed-member.php'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
quoted = lambda value: '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'


SELECTED = FETCH_SELECTED + r'''
dec $value_member_ready(pstate) : bool
def $value_member_ready(S) = true
  -- if S.TODO = (CLASS_CONST_MEMBER name poperand_class z) :: (CLASS_CONST_CAPTURE porigin poperand_class z) :: ptask*
def $value_member_ready(S) = false -- otherwise
dec $value_member_pause(pstate,nat) : pstate
def $value_member_pause(S,n) = S -- if $value_member_ready(S)
def $value_member_pause(S,n) = $value_member_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$value_member_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $value_member_pause(S,n) = S -- otherwise
'''


def member(fixture):
    expected = json.loads((SOURCE.parent / 'cases.json').read_text())[SOURCE.stem]['stdout']
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(SOURCE)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_pair = $value_member_pause(S_start[.COMPLETION = NORMAL],30000)', '$value_member_ready(S_pair)',
        'S_pair.TODO = (CLASS_CONST_MEMBER name poperand_class 26) :: (CLASS_CONST_CAPTURE porigin_site poperand_class 26) :: ptask_tail*',
        'S_pair.ORIGIN = (porigin_site)', 'porigin_site = PORIGIN n_unit pcpath',
        '$origin_node(S_pair.SOURCES,porigin_site) = (NExprClassConstFetch name expression_member metadata_fetch)',
        'expression_member = NExprBinaryOpConcat (NExprTernary (NExprVariable (BYTES text_pick) metadata_pick) phpType5_true expression_false metadata_ternary) (NScalarString (BYTES text_empty) metadata_empty) metadata_concat',
        '$base64(text_pick) = $ptascii("pick228")', '$base64(text_empty) = eps',
        '~$class_constant_legacy_call_member(expression_member)',
        'poperand_class = KNOWN (PSTRING ptbytes_class)',
        'ptbytes_class = ' + quoted('Ns228Value\\Child228'),
        '$ccn_output(S_pair.EVENTS) = $ptascii("A|")',
        'S_pair.CURRENT = eps', 'S_pair.FRAMES = eps', 'S_pair.HELD = eps',
        'S_pair.COMPLETION = NORMAL',
        'S_pair.RESULT = KNOWN pvalue_member',
        'pvalue_member = PSTRING_CARRIER (REQUEST_STRING n_string) ptbytes_member',
        'ptbytes_member = $ptascii("TREE")',
        '$string_carrier_valid(S_pair,pvalue_member)',
        '$constant_value_class_valid(S_pair,pvalue_member,PVSTRING false)',
        '$value_nodes(pvalue_member) = eps',
        '$code_at(S_pair.CODE,n_unit) = (pcode)',
        '$code_expression(pcode.EXPRESSIONS,pcpath) = ((26,false))',
        '$code_expression(pcode.EXPRESSIONS,pcpath ++ [PCFIELD 1]) = ((z_member,false))',
        '$compiled_read(S_pair,PORIGIN n_unit (pcpath ++ [PCFIELD 1])) = eps',
        '$class_constant_selected_valid(S_pair,name,poperand_class)',
        '$class_named(S_pair.CLASSNAMES,$ptlc(ptbytes_class)) = (porigin_requested)',
        '$class_constant_lookup(S_pair,porigin_requested,ptbytes_member,|S_pair.CLASSES|) = (pclassconstantdesc)',
        'porigin_decl = pclassconstantdesc.ORIGIN',
        'pclassconstantdesc.OWNERNAME = ' + quoted('Ns228Value\\Base228'),
        'pclassconstantdesc.FOLDED', 'pclassconstantdesc.VISIBILITY = PROPERTY_PUBLIC',
        '$compiled_read(S_pair,pclassconstantdesc.INITIALIZER) = (PARRAY n_donor)',
        'S_pair.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        '$class_constant_lookup(S_pair,porigin_requested,$ptascii("OTHER"),|S_pair.CLASSES|) = (pclassconstantdesc_other)',
        '$class_constant_deprecated(S_pair,pclassconstantdesc_other)',
        '$class_constant_visible(S_pair,pclassconstantdesc_other)',
        '$class_constant_rvalue_member_source(S_pair,porigin_decl,ptbytes_class,ptbytes_member,26)',
        '$class_constant_rvalue_member_entry(S_pair,S_pair.RESULT,name,poperand_class,26,ptask_tail*) = (pclassconstantdesc)',
        '~$class_constant_notice_valid(S_pair,porigin_decl,ptbytes_class,ptbytes_member,26)',
        '$call_task_valid(S_pair,CLASS_CONST_MEMBER name poperand_class 26)',
        '$call_descriptors_valid(S_pair)',
        'S_globals_pair = $global_table_view(S_pair)',
        '$lookup(S_globals_pair.ENV,$ptascii("pick228")) = (n_pick)',
        'S_globals_pair.STORE[n_pick] = DEFINED (PBOOL true)',
        '$lookup(S_globals_pair.ENV,$ptascii("source228")) = (n_source)',
        'S_globals_pair.STORE[n_source] = DEFINED pvalue_source',
        '$string_bytes(pvalue_source) = (ptbytes_member)',
        'S_warn_raw = $drive_steps(S_pair,1)', 'S_warn_raw.COMPLETION = BUDGET',
        'S_warn = S_warn_raw[.COMPLETION = NORMAL]', '$ccn_ready(S_warn,0)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class ptbytes_member 26',
        'perrorcall.LEVEL = 16384', 'perrorcall.LINE = 26',
        'perrorcall.MESSAGE = $class_constant_notice_message(pclassconstantdesc,ptbytes_member)',
        '$class_constant_notice_valid(S_warn,porigin_decl,ptbytes_class,ptbytes_member,26)',
        '$error_call_valid(S_warn,perrorcall)', '$call_descriptors_valid(S_warn)',
        '$task_nodes(perrorcall.RESUME) = eps',
        '$class_constant_notice_protected(S_warn,porigin_decl)',
        'S_warn.CLASSCONSTANTINIT = eps', 'S_warn.CLASSCONSTANTCACHE = eps',
        'S_resume = $ccn_pause(S_warn,1,30000)', '$ccn_ready(S_resume,1)',
        '$ccn_output(S_resume.EVENTS) = $ptascii("A|Ht|")',
        'S_resume.TODO = perrorcall.RESUME :: ptask_resume*',
        'S_globals_resume = $global_table_view(S_resume)',
        '$lookup(S_globals_resume.ENV,$ptascii("pick228")) = (n_pick)',
        'S_globals_resume.STORE[n_pick] = DEFINED (PBOOL false)',
        '$lookup(S_globals_resume.ENV,$ptascii("source228")) = (n_source)',
        'S_globals_resume.STORE[n_source] = DEFINED pvalue_now',
        '$string_bytes(pvalue_now) = ($ptascii("OTHER"))',
        '$class_constant_notice_valid(S_resume,porigin_decl,ptbytes_class,ptbytes_member,26)',
        '~$class_constant_notice_valid(S_resume[.RESULT = KNOWN (PSTRING $ptascii("OTHER"))],pclassconstantdesc_other.ORIGIN,ptbytes_class,$ptascii("OTHER"),26)',
        '$call_task_valid(S_resume,perrorcall.RESUME)', '$call_descriptors_valid(S_resume)',
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
        'S_second = $value_member_pause(S_one,30000)', '$value_member_ready(S_second)',
        'S_second.TODO = (CLASS_CONST_MEMBER name_second poperand_second 30) :: (CLASS_CONST_CAPTURE porigin_second poperand_second 30) :: ptask_second*',
        '$ccn_output(S_second.EVENTS) = $ptascii("A|Ht|O|1|M|7|B|")',
        'S_second.RESULT = KNOWN pvalue_second',
        'pvalue_second = PSTRING_CARRIER (REQUEST_STRING n_string_second) $ptascii("OTHER")',
        '$string_carrier_valid(S_second,pvalue_second)', 'n_string_second =/= n_string',
        '$class_constant_rvalue_member_entry(S_second,S_second.RESULT,name_second,poperand_second,30,ptask_second*) = (pclassconstantdesc_other)',
        '~$class_constant_notice_valid(S_second,pclassconstantdesc_other.ORIGIN,ptbytes_class,$ptascii("OTHER"),30)',
        'S_second_warn_raw = $drive_steps(S_second,1)', 'S_second_warn_raw.COMPLETION = BUDGET',
        'S_second_warn = S_second_warn_raw[.COMPLETION = NORMAL]',
        'S_second_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_second_warn*',
        'perrorcall_second.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc_other.ORIGIN ptbytes_class $ptascii("OTHER") 30',
        '$error_call_valid(S_second_warn,perrorcall_second)',
        'S_done = $drive(S_second_warn,30000)', 'S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = ' + quoted(expected),
        'S_global_done = $global_table_view(S_done)',
        '$lookup(S_global_done.ENV,$ptascii("value")) = (n_value)',
        '$lookup(S_global_done.ENV,$ptascii("again")) = (n_again)',
        '$lookup(S_global_done.ENV,$ptascii("other")) = (n_other)',
        'S_global_done.STORE[n_value] = DEFINED (PARRAY n_copy)',
        'S_global_done.STORE[n_again] = DEFINED (PARRAY n_donor)',
        'S_global_done.STORE[n_other] = DEFINED (PINT 9)', 'n_copy =/= n_donor',
        'S_done.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
        'S_done.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        'S_done.CLASSCONSTANTCACHE = eps', 'S_done.CLASSCONSTANTINIT = eps',
        'S_done.CLASSCONSTANTHISTORY = S_warn.CLASSCONSTANTHISTORY',
        '~$class_constant_notice_protected(S_done,porigin_decl)',
        '~$class_constant_notice_protected(S_done,pclassconstantdesc_other.ORIGIN)',
        '$class_constant_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        '$drive(S_zero[.COMPLETION = NORMAL],30000) = S_done',
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
