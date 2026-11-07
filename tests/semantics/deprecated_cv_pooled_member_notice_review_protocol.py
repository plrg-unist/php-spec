#!/usr/bin/env python3
"""Check immutable member authority with actual CV capture and reentry."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_cv_pooled_member_notice_review/capture-and-pool.php'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
quoted = lambda value: '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'

SELECTED = FETCH_SELECTED + r'''
dec $cv_pooled_ready(pstate,int) : bool
def $cv_pooled_ready(S,z) = true
  -- if S.COMPLETION = NORMAL
  -- if S.TODO = (CLASS_CONST_MEMBER expression_class poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: ptask*
  -- if S.ORIGIN = (porigin)
def $cv_pooled_ready(S,z) = false -- otherwise
dec $cv_pooled_pause(pstate,int,nat) : pstate
def $cv_pooled_pause(S,z,n) = S -- if $cv_pooled_ready(S,z)
def $cv_pooled_pause(S,z,n) = $cv_pooled_pause(S_next[.COMPLETION = NORMAL],z,$nabs($(n - 1)))
  -- if ~$cv_pooled_ready(S,z)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $cv_pooled_pause(S,z,n) = S -- otherwise
'''


def pooled(fixture):
    expected = json.loads((SOURCE.parent / 'cases.json').read_text())[SOURCE.stem]['stdout']
    child = quoted('Ns235Pool\\Child235')
    base = quoted('Ns235Pool\\Base235')
    other = quoted('Ns235Pool\\Other235')
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(SOURCE)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_pair = $cv_pooled_pause(S_start[.COMPLETION = NORMAL],32,30000)', '$cv_pooled_ready(S_pair,32)',
        'S_pair.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ' + child + ')) 32) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING ' + child + ')) 32) :: ptask_tail*',
        'S_pair.ORIGIN = (porigin_site)', 'porigin_site = PORIGIN n_unit pcpath',
        '$origin_node(S_pair.SOURCES,porigin_site) = (NExprClassConstFetch expression_class expression_member metadata)',
        'expression_class = NExprVariable (BYTES text_class) metadata_class',
        'expression_member = NExprBinaryOpConcat expression_left expression_right metadata_concat',
        'S_pair.CURRENT = eps', 'S_pair.FRAMES = eps', 'S_pair.HELD = eps',
        '$ccn_output(S_pair.EVENTS) = eps',
        'S_pair.RESULT = KNOWN pvalue_member', '$string_bytes(pvalue_member) = ($ptascii("TREE"))',
        '$constant_value_class_valid(S_pair,pvalue_member,PVSTRING false)', '$value_nodes(pvalue_member) = eps',
        '$code_at(S_pair.CODE,n_unit) = (pcode)',
        '$code_expression(pcode.EXPRESSIONS,pcpath) = ((32,false))',
        'pcpath_member = pcpath ++ [PCFIELD 1]',
        '$code_expression(pcode.EXPRESSIONS,pcpath_member) = ((z_member,true))',
        '$compiled_read(S_pair,PORIGIN n_unit (pcpath ++ [PCFIELD 0])) = eps',
        '$compiled_read(S_pair,PORIGIN n_unit pcpath_member) = (PSTRING $ptascii("TREE"))',
        '$class_named(S_pair.CLASSNAMES,$ptlc(' + child + ')) = (porigin_child)',
        '$class_at(S_pair.CLASSES,porigin_child) = (pclassdesc_child)',
        'pclassdesc_child.KIND = "interface"', 'pclassdesc_child.NAME = ' + child,
        '$class_constant_lookup(S_pair,porigin_child,$ptascii("TREE"),|S_pair.CLASSES|) = (pclassconstantdesc)',
        'porigin_decl = pclassconstantdesc.ORIGIN', 'pclassconstantdesc.OWNERNAME = ' + base,
        'pclassconstantdesc.FOLDED', '$compiled_read(S_pair,pclassconstantdesc.INITIALIZER) = (PARRAY n_donor)',
        '$class_named(S_pair.CLASSNAMES,$ptlc(' + other + ')) = (porigin_other)',
        '$class_constant_lookup(S_pair,porigin_other,$ptascii("TREE"),|S_pair.CLASSES|) = (pclassconstantdesc_other)',
        '$class_constant_pooled_dynamic_source(S_pair,porigin_decl,' + child + ',$ptascii("TREE"),32)',
        '$class_constant_pooled_dynamic_source(S_pair,pclassconstantdesc_other.ORIGIN,' + other + ',$ptascii("TREE"),32)',
        '$class_constant_pooled_cv_entry(S_pair,S_pair.RESULT,expression_class,KNOWN (PSTRING ' + child + '),32,ptask_tail*) = (pclassconstantdesc)',
        '$class_constant_pooled_cv_entry(S_pair,S_pair.RESULT,expression_class,KNOWN (PSTRING ' + other + '),32,ptask_tail*) = eps',
        '$class_constant_pooled_cv_entry(S_pair,S_pair.RESULT,expression_class,KNOWN (PSTRING ' + base + '),32,ptask_tail*) = eps',
        '~$class_constant_notice_valid(S_pair,porigin_decl,' + child + ',$ptascii("TREE"),32)',
        '$call_task_valid(S_pair,CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ' + child + ')) 32)',
        '$call_descriptors_valid(S_pair)',
        'pcode_hidden = pcode[.EXPRESSIONS = (CODEEXPR pcpath_member z_member false) :: pcode.EXPRESSIONS]',
        'S_hidden = S_pair[.CODE = [pcode_hidden]]',
        '$code_expression(pcode_hidden.EXPRESSIONS,pcpath) = ((32,false))',
        '$compiled_read(S_hidden,PORIGIN n_unit pcpath_member) = eps',
        '~$class_constant_pooled_dynamic_source(S_hidden,porigin_decl,' + child + ',$ptascii("TREE"),32)',
        '$class_constant_pooled_cv_entry(S_hidden,S_hidden.RESULT,expression_class,KNOWN (PSTRING ' + child + '),32,ptask_tail*) = eps',
        '$class_constant_pooled_cv_entry(S_pair,REFERENCE 0,expression_class,KNOWN (PSTRING ' + child + '),32,ptask_tail*) = eps',
        '$class_constant_pooled_cv_entry(S_pair,KNOWN PNULL,expression_class,KNOWN (PSTRING ' + child + '),32,ptask_tail*) = eps',
        '$class_constant_pooled_cv_entry(S_pair,S_pair.RESULT,expression_class,KNOWN (PSTRING ' + child + '),32,DISCARD :: ptask_tail*) = eps',
        '$class_constant_pooled_cv_entry(S_pair[.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ' + child + ')) 32) :: ptask_tail*],S_pair.RESULT,expression_class,KNOWN (PSTRING ' + child + '),32,ptask_tail*) = eps',
        'S_warn_raw = $drive_steps(S_pair,1)', 'S_warn_raw.COMPLETION = BUDGET',
        'S_warn = S_warn_raw[.COMPLETION = NORMAL]', '$ccn_ready(S_warn,0)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ' + child + ' $ptascii("TREE") 32',
        'perrorcall.LEVEL = 16384',
        'perrorcall.MESSAGE = $class_constant_notice_message(pclassconstantdesc,$ptascii("TREE"))',
        '$error_call_valid(S_warn,perrorcall)', '$call_descriptors_valid(S_warn)',
        '$task_nodes(perrorcall.RESUME) = eps', '$class_constant_notice_protected(S_warn,porigin_decl)',
        'S_inner = $cv_pooled_pause(S_warn,20,30000)', '$cv_pooled_ready(S_inner,20)',
        'S_inner.TODO = (CLASS_CONST_MEMBER expression_inner (KNOWN (PSTRING ' + child + ')) 20) :: (CLASS_CONST_CAPTURE porigin_inner (KNOWN (PSTRING ' + child + ')) 20) :: ptask_inner*',
        'S_inner.CURRENT = (pcallcontext_inner)',
        '$ccn_output(S_inner.EVENTS) = $ptascii("H|")',
        'S_inner.RESULT = KNOWN pvalue_inner', '$string_bytes(pvalue_inner) = ($ptascii("TREE"))',
        'S_inner.ORIGIN = (PORIGIN n_unit_inner pcpath_inner)',
        '$compiled_read(S_inner,PORIGIN n_unit_inner (pcpath_inner ++ [PCFIELD 1])) = (PSTRING $ptascii("TREE"))',
        '$class_constant_pooled_cv_entry(S_inner,S_inner.RESULT,expression_inner,KNOWN (PSTRING ' + child + '),20,ptask_inner*) = (pclassconstantdesc)',
        '$class_constant_notice_protected(S_inner,porigin_decl)',
        '~$class_constant_notice_valid(S_inner,porigin_decl,' + child + ',$ptascii("TREE"),20)',
        '$call_descriptors_valid(S_inner)',
        'n_inner_before = $heap_owners($heap_graph(S_inner),HARRAY n_donor)',
        'S_inner_raw = $drive_steps(S_inner,1)', 'S_inner_raw.COMPLETION = BUDGET',
        'S_inner_value = S_inner_raw[.COMPLETION = NORMAL]', 'S_inner_value.RESULT = KNOWN (PARRAY n_donor)',
        'S_inner_value.EVENTS = S_inner.EVENTS',
        '$heap_owners($heap_graph(S_inner_value),HARRAY n_donor) = $(n_inner_before + 1)',
        '$class_constant_notice_protected(S_inner_value,porigin_decl)',
        'S_resume = $ccn_pause(S_inner_value,1,30000)', '$ccn_ready(S_resume,1)',
        '$ccn_output(S_resume.EVENTS) = $ptascii("H|N|1|")',
        'S_resume.CURRENT = eps', 'S_resume.FRAMES = eps',
        'S_globals_resume = $global_table_view(S_resume)',
        '$lookup(S_globals_resume.ENV,$ptascii("class235")) = (n_class)',
        'S_globals_resume.STORE[n_class] = DEFINED pvalue_class_now',
        '$string_bytes(pvalue_class_now) = (' + other + ')',
        '$class_constant_notice_valid(S_resume,porigin_decl,' + child + ',$ptascii("TREE"),32)',
        '~$class_constant_notice_valid(S_resume[.RESULT = KNOWN (PSTRING ' + other + ')],pclassconstantdesc_other.ORIGIN,' + other + ',$ptascii("TREE"),32)',
        '~$class_constant_notice_valid(S_resume[.RESULT = KNOWN (PSTRING ' + base + ')],porigin_decl,' + base + ',$ptascii("TREE"),32)',
        '$class_constant_pooled_cv_entry(S_resume,KNOWN pvalue_member,expression_class,KNOWN (PSTRING ' + child + '),32,ptask_tail*) = eps',
        '$call_descriptors_valid(S_resume)',
        'n_before = $heap_owners($heap_graph(S_resume),HARRAY n_donor)',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_resume',
        'S_one_raw = $drive_steps(S_resume,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]', 'S_one.RESULT = KNOWN (PARRAY n_donor)',
        '$heap_owners($heap_graph(S_one),HARRAY n_donor) = $(n_before + 1)',
        '~$class_constant_notice_protected(S_one,porigin_decl)',
        'S_second = $cv_pooled_pause(S_one,36,30000)', '$cv_pooled_ready(S_second,36)',
        'S_second.TODO = (CLASS_CONST_MEMBER expression_second (KNOWN (PSTRING ' + other + ')) 36) :: (CLASS_CONST_CAPTURE porigin_second (KNOWN (PSTRING ' + other + ')) 36) :: ptask_second*',
        '$ccn_output(S_second.EVENTS) = $ptascii("H|N|1|A|1|MUT|7|")',
        '$class_constant_pooled_cv_entry(S_second,S_second.RESULT,expression_second,KNOWN (PSTRING ' + other + '),36,ptask_second*) = (pclassconstantdesc_other)',
        'S_done = $drive(S_second,30000)', 'S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = ' + quoted(expected),
        'S_globals = $global_table_view(S_done)',
        '$lookup(S_globals.ENV,$ptascii("first235")) = (n_first)',
        '$lookup(S_globals.ENV,$ptascii("second235")) = (n_second)',
        '$lookup(S_globals.ENV,$ptascii("again235")) = (n_again)',
        'S_globals.STORE[n_first] = DEFINED (PARRAY n_copy)',
        'S_globals.STORE[n_second] = DEFINED (PINT 9)',
        'S_globals.STORE[n_again] = DEFINED (PARRAY n_donor)', 'n_copy =/= n_donor',
        'S_done.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
        'S_done.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        'S_done.CLASSCONSTANTCACHE = eps', 'S_done.CLASSCONSTANTINIT = eps',
        'S_done.CLASSCONSTANTHISTORY = S_pair.CLASSCONSTANTHISTORY',
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
    checks = pooled(checked['fixture'])
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + SELECTED + '\ndec $main() : bool\ndef $main() = true\n'
        + ''.join('  -- if ' + check + '\n' for check in checks))
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
        report['inputs_stable'] = before == {str(path): sha(ROOT / path) for path in before}
        report['passed'] = report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after'] and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable']
    finally: (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    if not report['passed']: print(report.get('stdout', '')[:2000], report.get('stderr', '')[:4000])
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__':
    main()
