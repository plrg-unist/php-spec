#!/usr/bin/env python3
"""Check compiled class normalization and two immutable operand fields."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_pooled_class_notice_review/interface-class.php'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
quoted = lambda value: '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'


SELECTED = FETCH_SELECTED + r'''
dec $compiled_class_notice_ready(pstate) : bool
def $compiled_class_notice_ready(S) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class phpType20_member 18) :: ptask*
def $compiled_class_notice_ready(S) = false -- otherwise
dec $compiled_class_notice_pause(pstate,nat) : pstate
def $compiled_class_notice_pause(S,n) = S -- if $compiled_class_notice_ready(S)
def $compiled_class_notice_pause(S,n) = $compiled_class_notice_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$compiled_class_notice_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $compiled_class_notice_pause(S,n) = S -- otherwise
'''


def member(fixture):
    expected = json.loads((SOURCE.parent / 'cases.json').read_text())[SOURCE.stem]['stdout']
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(SOURCE)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_class = $compiled_class_notice_pause(S_start[.COMPLETION = NORMAL],30000)',
        '$compiled_class_notice_ready(S_class)',
        'S_class.TODO = (CLASS_CONST_CLASS expression_class phpType20_member 18) :: ptask_class*',
        'S_class.ORIGIN = (porigin_site)', 'porigin_site = PORIGIN n_unit pcpath',
        '$origin_node(S_class.SOURCES,porigin_site) = (NExprClassConstFetch expression_class phpType20_member metadata_fetch)',
        'expression_class = NScalarString (BYTES text_class) metadata_class',
        'phpType20_member = NIdentifier (BYTES text_member) metadata_member',
        '$base64(text_member) = $ptascii("TREE")',
        'ptbytes_member = $ptascii("TREE")',
        'ptbytes_raw = ' + quoted('\\nS226cLaSsPoOl\\cHiLd226'),
        '$base64(text_class) = ptbytes_raw',
        'ptbytes_class = $ppcall_literal_name(ptbytes_raw)',
        'ptbytes_class = ' + quoted('nS226cLaSsPoOl\\cHiLd226'),
        '$code_at(S_class.CODE,n_unit) = (pcode)',
        '$code_expression(pcode.EXPRESSIONS,pcpath) = ((18,false))',
        'pcpath_class = pcpath ++ [PCFIELD 0]',
        'pcpath_member = pcpath ++ [PCFIELD 1]',
        '$code_expression(pcode.EXPRESSIONS,pcpath_class) = ((18,true))',
        '$compiled_read(S_class,PORIGIN n_unit pcpath_class) = (PSTRING ptbytes_raw)',
        '$compiled_read(S_class,porigin_site) = eps',
        '$compiled_read(S_class,PORIGIN n_unit pcpath_member) = eps',
        '$class_constant_literal(S_class,expression_class)',
        '$class_constant_selected_valid(S_class,expression_class,KNOWN (PSTRING ptbytes_class))',
        '$class_named(S_class.CLASSNAMES,$ptlc(ptbytes_class)) = (porigin_requested)',
        '$class_at(S_class.CLASSES,porigin_requested) = (pclassdesc_requested)',
        'pclassdesc_requested.KIND = "interface"',
        'pclassdesc_requested.NAME = ' + quoted('Ns226ClassPool\\Child226'),
        'pclassdesc_requested.NAME =/= ptbytes_class',
        '$class_constant_lookup(S_class,porigin_requested,ptbytes_member,|S_class.CLASSES|) = (pclassconstantdesc)',
        'porigin_decl = pclassconstantdesc.ORIGIN',
        'pclassconstantdesc.OWNERNAME = ' + quoted('Ns226ClassPool\\Base226'),
        'pclassconstantdesc.FOLDED', 'pclassconstantdesc.VISIBILITY = PROPERTY_PUBLIC',
        '$compiled_read(S_class,pclassconstantdesc.INITIALIZER) = (PARRAY n_donor)',
        'S_class.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        '$class_constant_lookup(S_class,porigin_requested,$ptascii("OTHER"),|S_class.CLASSES|) = (pclassconstantdesc_other)',
        '$class_constant_deprecated(S_class,pclassconstantdesc_other)',
        '$class_constant_visible(S_class,pclassconstantdesc_other)',
        '$class_constant_compiled_member(S_class,PORIGIN n_unit pcpath_member,phpType20_member) = (ptbytes_member)',
        '$class_constant_notice_valid(S_class,porigin_decl,ptbytes_class,ptbytes_member,18)',
        '$class_constant_notice_valid(S_class[.RESULT = KNOWN PNULL],porigin_decl,ptbytes_class,ptbytes_member,18)',
        '~$class_constant_notice_valid(S_class,porigin_decl,pclassdesc_requested.NAME,ptbytes_member,18)',
        '~$class_constant_notice_valid(S_class,porigin_decl,ptbytes_raw,ptbytes_member,18)',
        '~$class_constant_notice_valid(S_class,porigin_decl,' + quoted('Ns226ClassPool\\Implementer226') + ',ptbytes_member,18)',
        '~$class_constant_notice_valid(S_class,pclassconstantdesc_other.ORIGIN,ptbytes_class,$ptascii("OTHER"),18)',
        '~$class_constant_notice_valid(S_class[.POOLS = eps],porigin_decl,ptbytes_class,ptbytes_member,18)',
        'pcode_hidden = pcode[.EXPRESSIONS = (CODEEXPR pcpath_class 18 false) :: pcode.EXPRESSIONS]',
        'S_hidden = S_class[.CODE = [pcode_hidden]]',
        '$compiled_read(S_hidden,PORIGIN n_unit pcpath_class) = eps',
        '$class_constant_selected_valid(S_hidden,expression_class,KNOWN (PSTRING pclassdesc_requested.NAME))',
        '~$class_constant_notice_valid(S_hidden,porigin_decl,pclassdesc_requested.NAME,ptbytes_member,18)',
        'pcode_outer = pcode[.EXPRESSIONS = (CODEEXPR pcpath 18 true) :: pcode.EXPRESSIONS]',
        '~$class_constant_notice_valid(S_class[.CODE = [pcode_outer]],porigin_decl,ptbytes_class,ptbytes_member,18)',
        'S_class.CURRENT = eps', 'S_class.CONSTCONTEXT = eps', '$call_descriptors_valid(S_class)',
        'S_warn_raw = $drive_steps(S_class,1)', 'S_warn_raw.COMPLETION = BUDGET',
        'S_warn = S_warn_raw[.COMPLETION = NORMAL]', '$ccn_ready(S_warn,0)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class ptbytes_member 18',
        'S_warn.RESULT = KNOWN PNULL',
        '$class_constant_notice_valid(S_warn,porigin_decl,ptbytes_class,ptbytes_member,18)',
        'perrorcall.LEVEL = 16384', 'perrorcall.LINE = 18',
        'perrorcall.MESSAGE = $class_constant_notice_message(pclassconstantdesc,ptbytes_member)',
        '$error_call_valid(S_warn,perrorcall)', '$call_descriptors_valid(S_warn)',
        '$task_nodes(perrorcall.RESUME) = eps',
        '$class_constant_notice_protected(S_warn,porigin_decl)',
        'S_warn.CLASSCONSTANTINIT = eps', 'S_warn.CLASSCONSTANTCACHE = eps',
        'S_resume = $ccn_pause(S_warn,1,30000)', '$ccn_ready(S_resume,1)',
        '$ccn_output(S_resume.EVENTS) = $ptascii("H|")',
        'S_resume.TODO = perrorcall.RESUME :: ptask_resume*',
        '$class_constant_notice_valid(S_resume,porigin_decl,ptbytes_class,ptbytes_member,18)',
        '$class_constant_notice_valid(S_resume[.RESULT = KNOWN (PSTRING pclassdesc_requested.NAME)],porigin_decl,ptbytes_class,ptbytes_member,18)',
        '~$class_constant_notice_valid(S_resume,porigin_decl,pclassdesc_requested.NAME,ptbytes_member,18)',
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
        'S_warm = $ccn_pause(S_one,0,30000)', '$ccn_ready(S_warm,0)',
        'S_warm.TODO = (ERROR_HANDLER_INVOKE perrorcall_warm) :: ptask_warm*',
        'perrorcall_warm.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_warm_class ptbytes_member 22',
        'ptbytes_warm_class = ' + quoted('Ns226ClassPool\\Implementer226'),
        'S_warm.ORIGIN = (PORIGIN n_unit_warm pcpath_warm)',
        '$origin_node(S_warm.SOURCES,PORIGIN n_unit_warm pcpath_warm) = (NExprClassConstFetch (NExprBinaryOpConcat expression_class_left expression_class_right metadata_warm_class) (NExprBinaryOpConcat expression_member_left expression_member_right metadata_warm_member) metadata_warm)',
        '$compiled_read(S_warm,PORIGIN n_unit_warm (pcpath_warm ++ [PCFIELD 0])) = (PSTRING ptbytes_warm_raw)',
        'ptbytes_warm_raw = ' + quoted('\\Ns226ClassPool\\Implementer226'),
        '$ppcall_literal_name(ptbytes_warm_raw) = ptbytes_warm_class',
        'porigin_warm_member = PORIGIN n_unit_warm (pcpath_warm ++ [PCFIELD 1])',
        '$compiled_read(S_warm,porigin_warm_member) = (PSTRING ptbytes_member)',
        '$class_constant_compiled_member(S_warm,porigin_warm_member,NExprBinaryOpConcat expression_member_left expression_member_right metadata_warm_member) = (ptbytes_member)',
        '$class_constant_compiled_member(S_warm,porigin_warm_member,NExprVariable (BYTES text_member) metadata_member) = eps',
        '$compiled_read(S_warm,PORIGIN n_unit_warm pcpath_warm) = eps',
        '$code_at(S_warm.CODE,n_unit_warm) = (pcode_warm)',
        'pcode_missing_member = pcode_warm[.EXPRESSIONS = (CODEEXPR (pcpath_warm ++ [PCFIELD 1]) 22 false) :: pcode_warm.EXPRESSIONS]',
        '~$class_constant_notice_valid(S_warm[.CODE = [pcode_missing_member]],porigin_decl,ptbytes_warm_class,ptbytes_member,22)',
        'perrorcall_warm.MESSAGE = perrorcall.MESSAGE', '$error_call_valid(S_warm,perrorcall_warm)',
        '$ccn_output(S_warm.EVENTS) = $ptascii("H|O|1|M|7|")',
        'S_warm.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        'S_done = $drive(S_warm,30000)', 'S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = ' + quoted(expected),
        'S_global_done = $global_table_view(S_done)',
        '$lookup(S_global_done.ENV,$ptascii("value")) = (n_value)',
        '$lookup(S_global_done.ENV,$ptascii("again")) = (n_again)',
        '$lookup(S_global_done.ENV,$ptascii("last")) = (n_last)',
        'S_global_done.STORE[n_value] = DEFINED (PARRAY n_copy)',
        'S_global_done.STORE[n_again] = DEFINED (PARRAY n_donor)',
        'S_global_done.STORE[n_last] = DEFINED (PARRAY n_donor)', 'n_copy =/= n_donor',
        'S_done.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
        'S_done.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        'S_done.CLASSCONSTANTCACHE = eps', 'S_done.CLASSCONSTANTINIT = eps',
        'S_done.CLASSCONSTANTHISTORY = S_warn.CLASSCONSTANTHISTORY',
        '~$class_constant_notice_protected(S_done,porigin_decl)',
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
