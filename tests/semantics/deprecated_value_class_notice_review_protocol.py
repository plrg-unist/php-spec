#!/usr/bin/env python3
"""Check completed class selectors and canonical Deprecated resumption."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_value_class_notice_review/composed-class.php'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
quoted = lambda value: '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'


SELECTED = FETCH_SELECTED + r"""
dec $value_class_ready(pstate) : bool
def $value_class_ready(S) = true
  -- if S.COMPLETION = NORMAL
  -- if S.TODO = (CLASS_CONST_CLASS expression_class (NIdentifier (BYTES text_member) metadata_member) z) :: ptask*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = (ptbytes)
def $value_class_ready(S) = false -- otherwise
dec $value_class_pause(pstate,nat) : pstate
def $value_class_pause(S,n) = S -- if $value_class_ready(S)
def $value_class_pause(S,n) = $value_class_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$value_class_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $value_class_pause(S,n) = S -- otherwise
"""


def class_selector(fixture):
    expected = json.loads((SOURCE.parent / 'cases.json').read_text())[SOURCE.stem]['stdout']
    child = quoted('Ns229Value\\Child229')
    base = quoted('Ns229Value\\Base229')
    other = quoted('Ns229Value\\Other229')
    raw = quoted('\\nS229vAlUe\\cHiLd229')
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(SOURCE)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_raw = $value_class_pause(S_start[.COMPLETION = NORMAL],30000)', '$value_class_ready(S_raw)',
        'S_raw.TODO = (CLASS_CONST_CLASS expression_class phpType20_member 32) :: ptask_tail*',
        'phpType20_member = NIdentifier (BYTES text_member) metadata_member',
        '$base64(text_member) = $ptascii("TREE")',
        'S_raw.ORIGIN = (porigin_site)', 'porigin_site = PORIGIN n_unit pcpath',
        '$origin_node(S_raw.SOURCES,porigin_site) = (NExprClassConstFetch expression_class phpType20_member metadata_fetch)',
        'expression_class = NExprBinaryOpConcat (NExprTernary (NExprVariable (BYTES text_pick) metadata_pick) phpType5_true expression_false metadata_ternary) (NScalarString (BYTES text_empty) metadata_empty) metadata_concat',
        '$base64(text_pick) = $ptascii("pick229")', '$base64(text_empty) = eps',
        '$ccn_output(S_raw.EVENTS) = $ptascii("T|C|old|A|")',
        'S_raw.CURRENT = eps', 'S_raw.FRAMES = eps', 'S_raw.HELD = eps',
        'S_raw.RESULT = KNOWN pvalue_raw',
        'pvalue_raw = PSTRING_CARRIER (REQUEST_STRING n_string) ptbytes_raw',
        'ptbytes_raw = ' + raw,
        '$constant_value_class_valid(S_raw,pvalue_raw,PVSTRING false)',
        '$string_carrier_valid(S_raw,pvalue_raw)', '$value_nodes(pvalue_raw) = eps',
        '$code_at(S_raw.CODE,n_unit) = (pcode)',
        '$code_expression(pcode.EXPRESSIONS,pcpath) = ((32,false))',
        '$code_expression(pcode.EXPRESSIONS,pcpath ++ [PCFIELD 0]) = ((z_class,false))',
        '$compiled_read(S_raw,PORIGIN n_unit (pcpath ++ [PCFIELD 0])) = eps',
        '$call_task_valid(S_raw,CLASS_CONST_CLASS expression_class phpType20_member 32)',
        '$call_descriptors_valid(S_raw)',
        'S_class = $class_constant_selector(S_raw,expression_class,32)',
        'S_class.COMPLETION = NORMAL', 'S_class.TODO = S_raw.TODO',
        'ptbytes_class = ' + child,
        'S_class.RESULT = KNOWN (PSTRING ptbytes_class)',
        'ptbytes_class =/= ptbytes_raw',
        '$class_named(S_class.CLASSNAMES,$ptlc($ppcall_literal_name(ptbytes_raw))) = (porigin_requested)',
        '$class_at(S_class.CLASSES,porigin_requested) = (pclassdesc)',
        'pclassdesc.NAME = ptbytes_class',
        '$class_constant_lookup(S_class,porigin_requested,$ptascii("TREE"),|S_class.CLASSES|) = (pclassconstantdesc)',
        'porigin_decl = pclassconstantdesc.ORIGIN',
        'pclassconstantdesc.OWNERNAME = ' + base,
        'pclassconstantdesc.FOLDED', 'pclassconstantdesc.VISIBILITY = PROPERTY_PUBLIC',
        '$compiled_read(S_class,pclassconstantdesc.INITIALIZER) = (PARRAY n_donor)',
        'S_class.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        '$class_named(S_class.CLASSNAMES,$ptlc(' + other + ')) = (porigin_other)',
        '$class_constant_lookup(S_class,porigin_other,$ptascii("TREE"),|S_class.CLASSES|) = (pclassconstantdesc_other)',
        '$class_constant_selected_valid(S_class,expression_class,KNOWN (PSTRING ' + other + '))',
        '$class_constant_rvalue_class_source(S_class,porigin_decl,ptbytes_class,$ptascii("TREE"),32)',
        '$class_constant_rvalue_class_entry(S_class,S_raw.RESULT,expression_class,phpType20_member,32,ptask_tail*) = (pclassconstantdesc)',
        '~$class_constant_notice_valid(S_class,porigin_decl,ptbytes_class,$ptascii("TREE"),32)',
        '$class_constant_rvalue_class_entry(S_class,REFERENCE 0,expression_class,phpType20_member,32,ptask_tail*) = eps',
        '$class_constant_rvalue_class_entry(S_class,VARIABLE $ptascii("class229") 27,expression_class,phpType20_member,32,ptask_tail*) = eps',
        '$class_constant_rvalue_class_entry(S_class,KNOWN PNULL,expression_class,phpType20_member,32,ptask_tail*) = eps',
        '$class_constant_rvalue_class_entry(S_class,KNOWN (PSTRING ' + other + '),expression_class,phpType20_member,32,ptask_tail*) = eps',
        '$class_constant_rvalue_class_entry(S_class[.RESULT = KNOWN (PSTRING ' + other + ')],S_raw.RESULT,expression_class,phpType20_member,32,ptask_tail*) = eps',
        '$class_constant_rvalue_class_entry(S_class[.TODO = ptask_tail*],S_raw.RESULT,expression_class,phpType20_member,32,ptask_tail*) = eps',
        '$class_constant_rvalue_class_entry(S_class,S_raw.RESULT,expression_class,phpType20_member,32,eps) = eps',
        '$class_constant_rvalue_class_entry(S_class[.COMPLETION = BUDGET],S_raw.RESULT,expression_class,phpType20_member,32,ptask_tail*) = eps',
        '$class_constant_rvalue_class_entry(S_class,S_raw.RESULT,expression_class,phpType20_member,6,ptask_tail*) = eps',
        'S_globals_raw = $global_table_view(S_raw)',
        '$lookup(S_globals_raw.ENV,$ptascii("pick229")) = (n_pick)',
        'S_globals_raw.STORE[n_pick] = DEFINED (PBOOL true)',
        '$lookup(S_globals_raw.ENV,$ptascii("class229")) = (n_source)',
        'S_globals_raw.STORE[n_source] = DEFINED pvalue_source',
        '$string_bytes(pvalue_source) = (ptbytes_raw)',
        '$lookup(S_globals_raw.ENV,$ptascii("failed")) = (n_failed)',
        'S_globals_raw.STORE[n_failed] = DEFINED pvalue_failed',
        '$string_bytes(pvalue_failed) = ($ptascii("old"))',
        'S_warn_raw = $drive_steps(S_raw,1)', 'S_warn_raw.COMPLETION = BUDGET',
        'S_warn = S_warn_raw[.COMPLETION = NORMAL]', '$ccn_ready(S_warn,0)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class $ptascii("TREE") 32',
        'perrorcall.LEVEL = 16384', 'perrorcall.LINE = 32',
        'perrorcall.MESSAGE = $class_constant_notice_message(pclassconstantdesc,$ptascii("TREE"))',
        '$class_constant_notice_valid(S_warn,porigin_decl,ptbytes_class,$ptascii("TREE"),32)',
        '$error_call_valid(S_warn,perrorcall)', '$call_descriptors_valid(S_warn)',
        '$task_nodes(perrorcall.RESUME) = eps', '$class_constant_notice_protected(S_warn,porigin_decl)',
        'S_warn.CLASSCONSTANTINIT = eps', 'S_warn.CLASSCONSTANTCACHE = eps',
        'S_resume = $ccn_pause(S_warn,1,30000)', '$ccn_ready(S_resume,1)',
        '$ccn_output(S_resume.EVENTS) = $ptascii("T|C|old|A|Ht|")',
        'S_resume.TODO = perrorcall.RESUME :: ptask_resume*',
        'S_globals_resume = $global_table_view(S_resume)',
        '$lookup(S_globals_resume.ENV,$ptascii("pick229")) = (n_pick)',
        'S_globals_resume.STORE[n_pick] = DEFINED (PBOOL false)',
        '$lookup(S_globals_resume.ENV,$ptascii("class229")) = (n_source)',
        'S_globals_resume.STORE[n_source] = DEFINED pvalue_now',
        '$string_bytes(pvalue_now) = (' + other + ')',
        '$class_constant_notice_valid(S_resume,porigin_decl,ptbytes_class,$ptascii("TREE"),32)',
        '~$class_constant_notice_valid(S_resume[.RESULT = KNOWN (PSTRING ' + other + ')],pclassconstantdesc_other.ORIGIN,' + other + ',$ptascii("TREE"),32)',
        '~$class_constant_notice_valid(S_resume,porigin_decl,' + base + ',$ptascii("TREE"),32)',
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
        'S_second = $value_class_pause(S_one,30000)', '$value_class_ready(S_second)',
        'S_second.TODO = (CLASS_CONST_CLASS expression_second phpType20_second 36) :: ptask_second*',
        '$ccn_output(S_second.EVENTS) = $ptascii("T|C|old|A|Ht|O|1|M|7|B|")',
        'S_second.RESULT = KNOWN pvalue_second',
        'pvalue_second = PSTRING_CARRIER (REQUEST_STRING n_string_second) ' + other,
        '$string_carrier_valid(S_second,pvalue_second)', 'n_string_second =/= n_string',
        'S_second_class = $class_constant_selector(S_second,expression_second,36)',
        'S_second_class.RESULT = KNOWN (PSTRING ' + other + ')',
        '$class_constant_rvalue_class_entry(S_second_class,S_second.RESULT,expression_second,phpType20_second,36,ptask_second*) = (pclassconstantdesc_other)',
        '~$class_constant_notice_valid(S_second_class,pclassconstantdesc_other.ORIGIN,' + other + ',$ptascii("TREE"),36)',
        'S_second_warn_raw = $drive_steps(S_second,1)', 'S_second_warn_raw.COMPLETION = BUDGET',
        'S_second_warn = S_second_warn_raw[.COMPLETION = NORMAL]',
        'S_second_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_second_warn*',
        'perrorcall_second.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc_other.ORIGIN ' + other + ' $ptascii("TREE") 36',
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
    checks = class_selector(checked['fixture'])
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
