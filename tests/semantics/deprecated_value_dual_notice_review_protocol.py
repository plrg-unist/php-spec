#!/usr/bin/env python3
"""Check string acquisition tags through computed-member throw and resumption."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_value_dual_notice_review/member-throw.php'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
quoted = lambda value: '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'


SELECTED = FETCH_SELECTED + r"""
dec $dual_ready(pstate,nat) : bool
def $dual_ready(S,0) = true
  -- if S.COMPLETION = NORMAL
  -- if S.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = (ptbytes)
def $dual_ready(S,1) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CLASS_CONST_STRING_CAPTURE porigin ptbytes z) :: ptask*
def $dual_ready(S,2) = true
  -- if S.COMPLETION = NORMAL
  -- if S.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ptbytes)) z) :: (CLASS_CONST_CAPTURE porigin (KNOWN (PSTRING ptbytes)) z) :: (CLASS_CONST_STRING_CAPTURE porigin ptbytes z) :: ptask*
def $dual_ready(S,n) = false -- otherwise
dec $dual_pause(pstate,nat,nat) : pstate
def $dual_pause(S,n_stage,n) = S -- if $dual_ready(S,n_stage)
def $dual_pause(S,n_stage,n) = $dual_pause(S_next[.COMPLETION = NORMAL],n_stage,$nabs($(n - 1)))
  -- if ~$dual_ready(S,n_stage)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $dual_pause(S,n_stage,n) = S -- otherwise
"""


def composed(fixture):
    expected = json.loads((SOURCE.parent / 'cases.json').read_text())[SOURCE.stem]['stdout']
    child = quoted('Ns230Value\\Child230')
    base = quoted('Ns230Value\\Base230')
    other = quoted('Ns230Value\\Other230')
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(SOURCE)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_raw = $dual_pause(S_start[.COMPLETION = NORMAL],0,30000)', '$dual_ready(S_raw,0)',
        'S_raw.TODO = (CLASS_CONST_CLASS expression_class expression_member 35) :: ptask_tail*',
        'S_raw.ORIGIN = (porigin_site)', 'porigin_site = PORIGIN n_unit pcpath',
        '$origin_node(S_raw.SOURCES,porigin_site) = (NExprClassConstFetch expression_class expression_member metadata_fetch)',
        'expression_class = NExprFuncCall name_class (SEQUENCE eps) metadata_class',
        'expression_member = NExprFuncCall name_member (SEQUENCE eps) metadata_member',
        '$ccn_output(S_raw.EVENTS) = $ptascii("C|")',
        'S_raw.RESULT = KNOWN pvalue_raw', '$string_bytes(pvalue_raw) = (' + child + ')',
        '$constant_value_class_valid(S_raw,pvalue_raw,PVSTRING false)', '$value_nodes(pvalue_raw) = eps',
        'S_raw.CURRENT = eps', 'S_raw.FRAMES = eps', 'S_raw.HELD = eps',
        '$code_at(S_raw.CODE,n_unit) = (pcode)',
        '$code_expression(pcode.EXPRESSIONS,pcpath) = ((35,false))',
        '$code_expression(pcode.EXPRESSIONS,pcpath ++ [PCFIELD 0]) = ((z_class,false))',
        '$code_expression(pcode.EXPRESSIONS,pcpath ++ [PCFIELD 1]) = ((z_member,false))',
        'S_class = $class_constant_selector(S_raw,expression_class,35)',
        'S_class.RESULT = KNOWN (PSTRING ' + child + ')',
        '$class_named(S_class.CLASSNAMES,$ptlc(' + child + ')) = (porigin_requested)',
        '$class_constant_lookup(S_class,porigin_requested,$ptascii("TREE"),|S_class.CLASSES|) = (pclassconstantdesc)',
        'porigin_decl = pclassconstantdesc.ORIGIN', 'pclassconstantdesc.OWNERNAME = ' + base,
        'pclassconstantdesc.FOLDED', '$compiled_read(S_class,pclassconstantdesc.INITIALIZER) = (PARRAY n_donor)',
        'S_tag_raw = $drive_steps(S_raw,1)', 'S_tag_raw.COMPLETION = BUDGET',
        'S_tag = S_tag_raw[.COMPLETION = NORMAL]',
        'S_tag.TODO = ptask_eval :: (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ' + child + ')) 35) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING ' + child + ')) 35) :: (CLASS_CONST_STRING_CAPTURE porigin_site ' + child + ' 35) :: ptask_tail*',
        'ptask_eval = $at_task((PORIGIN n_unit (pcpath ++ [PCFIELD 1])),EVAL expression_member)',
        '$task_nodes(CLASS_CONST_STRING_CAPTURE porigin_site ' + child + ' 35) = eps',
        '$call_task_valid(S_tag,CLASS_CONST_STRING_CAPTURE porigin_site ' + child + ' 35)',
        '$call_descriptors_valid(S_tag)',
        'S_tag.RESULT = KNOWN PNULL',
        'S_orphan = $dual_pause(S_tag,1,30000)', '$dual_ready(S_orphan,1)',
        'S_orphan.TODO = (THROW_SEARCH n_exception) :: (CLASS_CONST_STRING_CAPTURE porigin_site ' + child + ' 35) :: ptask_unwind*',
        '$ccn_output(S_orphan.EVENTS) = $ptascii("C|M|")',
        'S_orphan.CURRENT = eps', 'S_orphan.FRAMES = eps',
        '$call_task_valid(S_orphan,CLASS_CONST_STRING_CAPTURE porigin_site ' + child + ' 35)',
        '$call_descriptors_valid(S_orphan)',
        '~$class_constant_notice_protected(S_orphan,porigin_decl)',
        'S_drop_raw = $drive_steps(S_orphan,1)', 'S_drop_raw.COMPLETION = BUDGET',
        'S_drop = S_drop_raw[.COMPLETION = NORMAL]',
        'S_drop.TODO = (THROW_SEARCH n_exception) :: ptask_unwind*',
        'S_drop.EVENTS = S_orphan.EVENTS', '$call_descriptors_valid(S_drop)',
        'S_second = $dual_pause(S_drop,0,30000)', '$dual_ready(S_second,0)',
        'S_second.TODO = (CLASS_CONST_CLASS expression_second expression_member_second 38) :: ptask_second*',
        '$ccn_output(S_second.EVENTS) = $ptascii("C|M|T|old|C|")',
        'S_second.RESULT = KNOWN pvalue_second', '$string_bytes(pvalue_second) = (' + child + ')',
        'S_globals_second = $global_table_view(S_second)',
        '$lookup(S_globals_second.ENV,$ptascii("value")) = (n_value_before)',
        'S_globals_second.STORE[n_value_before] = DEFINED pvalue_old',
        '$string_bytes(pvalue_old) = ($ptascii("old"))',
        'S_pair = $dual_pause(S_second,2,30000)', '$dual_ready(S_pair,2)',
        'S_pair.TODO = (CLASS_CONST_MEMBER expression_second (KNOWN (PSTRING ' + child + ')) 38) :: (CLASS_CONST_CAPTURE porigin_second (KNOWN (PSTRING ' + child + ')) 38) :: (CLASS_CONST_STRING_CAPTURE porigin_second ' + child + ' 38) :: ptask_outer*',
        'S_pair.ORIGIN = (porigin_second)',
        '$ccn_output(S_pair.EVENTS) = $ptascii("C|M|T|old|C|M|")',
        'S_pair.CURRENT = eps', 'S_pair.FRAMES = eps', 'S_pair.HELD = eps',
        'S_pair.RESULT = KNOWN pvalue_member', '$string_bytes(pvalue_member) = ($ptascii("TREE"))',
        '$constant_value_class_valid(S_pair,pvalue_member,PVSTRING false)', '$value_nodes(pvalue_member) = eps',
        '$call_descriptors_valid(S_pair)',
        '~$class_constant_notice_valid(S_pair,porigin_decl,' + child + ',$ptascii("TREE"),38)',
        'S_globals_pair = $global_table_view(S_pair)',
        '$lookup(S_globals_pair.ENV,$ptascii("class230")) = (n_class)',
        'S_globals_pair.STORE[n_class] = DEFINED pvalue_now', '$string_bytes(pvalue_now) = (' + other + ')',
        '$class_named(S_pair.CLASSNAMES,$ptlc(' + other + ')) = (porigin_other)',
        '$class_constant_lookup(S_pair,porigin_other,$ptascii("TREE"),|S_pair.CLASSES|) = (pclassconstantdesc_other)',
        '$class_constant_string_notice_source(S_pair,pclassconstantdesc_other.ORIGIN,' + other + ',$ptascii("TREE"),38)',
        'S_without_kind = S_pair[.TODO = (CLASS_CONST_MEMBER expression_second (KNOWN (PSTRING ' + child + ')) 38) :: (CLASS_CONST_CAPTURE porigin_second (KNOWN (PSTRING ' + child + ')) 38) :: ptask_outer*]',
        '$call_descriptors_valid(S_without_kind)',
        'S_refuse = $drive_steps(S_without_kind,1)',
        'S_refuse.COMPLETION = UNSUPPORTED "Deprecated class constant fetch"',
        'S_refuse.EVENTS = S_pair.EVENTS',
        'S_warn_raw = $drive_steps(S_pair,1)', 'S_warn_raw.COMPLETION = BUDGET',
        'S_warn = S_warn_raw[.COMPLETION = NORMAL]', '$ccn_ready(S_warn,0)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ' + child + ' $ptascii("TREE") 38',
        'perrorcall.LEVEL = 16384', 'perrorcall.LINE = 38',
        '$error_call_valid(S_warn,perrorcall)', '$call_descriptors_valid(S_warn)',
        '$class_constant_notice_valid(S_warn,porigin_decl,' + child + ',$ptascii("TREE"),38)',
        '$task_nodes(perrorcall.RESUME) = eps', '$class_constant_notice_protected(S_warn,porigin_decl)',
        'S_warn.CLASSCONSTANTINIT = eps', 'S_warn.CLASSCONSTANTCACHE = eps',
        'S_resume = $ccn_pause(S_warn,1,30000)', '$ccn_ready(S_resume,1)',
        '$ccn_output(S_resume.EVENTS) = $ptascii("C|M|T|old|C|M|Ht|")',
        'S_resume.TODO = perrorcall.RESUME :: ptask_resume*',
        '$class_constant_notice_valid(S_resume,porigin_decl,' + child + ',$ptascii("TREE"),38)',
        '~$class_constant_notice_valid(S_resume[.RESULT = KNOWN (PSTRING ' + other + ')],pclassconstantdesc_other.ORIGIN,' + other + ',$ptascii("TREE"),38)',
        '$call_descriptors_valid(S_resume)',
        'n_before = $heap_owners($heap_graph(S_resume),HARRAY n_donor)',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_resume',
        'S_one_raw = $drive_steps(S_resume,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]', 'S_one.RESULT = KNOWN (PARRAY n_donor)',
        '$heap_owners($heap_graph(S_one),HARRAY n_donor) = $(n_before + 1)',
        '~$class_constant_notice_protected(S_one,porigin_decl)',
        'S_third = $dual_pause(S_one,2,30000)', '$dual_ready(S_third,2)',
        'S_third.TODO = (CLASS_CONST_MEMBER expression_third (KNOWN (PSTRING ' + other + ')) 42) :: (CLASS_CONST_CAPTURE porigin_third (KNOWN (PSTRING ' + other + ')) 42) :: (CLASS_CONST_STRING_CAPTURE porigin_third ' + other + ' 42) :: ptask_third*',
        '$ccn_output(S_third.EVENTS) = $ptascii("C|M|T|old|C|M|Ht|O|1|MUT|7|C|M|")',
        '$call_descriptors_valid(S_third)',
        'S_third.RESULT = KNOWN pvalue_third', '$string_bytes(pvalue_third) = ($ptascii("TREE"))',
        '$class_named(S_third.CLASSNAMES,$ptlc(' + other + ')) = (porigin_other)',
        '$class_constant_lookup(S_third,porigin_other,$ptascii("TREE"),|S_third.CLASSES|) = (pclassconstantdesc_other)',
        'pclassconstantdesc_other.ORIGIN =/= porigin_decl',
        'S_done = $drive(S_third,30000)', 'S_done.COMPLETION = NORMAL',
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
    checks = composed(checked['fixture'])
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
