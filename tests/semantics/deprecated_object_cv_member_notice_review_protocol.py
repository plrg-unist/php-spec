#!/usr/bin/env python3
"""Check class-object CV retirement during completed member evaluation."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_object_cv_member_notice_review/source-retirement.php'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
quoted = lambda value: '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'


SELECTED = FETCH_SELECTED + r"""
dec $object_cv_ready(pstate,bool) : bool
def $object_cv_ready(S,false) = true
  -- if S.COMPLETION = NORMAL
  -- if S.TODO = (CLASS_CONST_CLASS (NExprVariable (BYTES text_class) metadata_class) expression_member z) :: ptask*
def $object_cv_ready(S,true) = true
  -- if S.COMPLETION = NORMAL
  -- if S.TODO = (CLASS_CONST_MEMBER (NExprVariable (BYTES text_class) metadata_class) poperand_class z) :: (CLASS_CONST_CAPTURE porigin poperand_class z) :: ptask*
def $object_cv_ready(S,b) = false -- otherwise
dec $object_cv_pause(pstate,bool,nat) : pstate
def $object_cv_pause(S,b,n) = S -- if $object_cv_ready(S,b)
def $object_cv_pause(S,b,n) = $object_cv_pause(S_next[.COMPLETION = NORMAL],b,$nabs($(n - 1)))
  -- if ~$object_cv_ready(S,b)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $object_cv_pause(S,b,n) = S -- otherwise
"""


def object_selector(fixture):
    expected = json.loads((SOURCE.parent / 'cases.json').read_text())[SOURCE.stem]['stdout']
    impl = quoted('Ns231Object\\Impl231')
    base = quoted('Ns231Object\\Base231')
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(SOURCE)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_live = $object_cv_pause(S_start[.COMPLETION = NORMAL],false,30000)', '$object_cv_ready(S_live,false)',
        'S_live.TODO = (CLASS_CONST_CLASS expression_class expression_member 26) :: ptask_tail*',
        'expression_class = NExprVariable (BYTES text_class) metadata_class',
        '$base64(text_class) = $ptascii("class231")',
        'S_live.RESULT = VARIABLE $ptascii("class231") 26',
        'S_live.ORIGIN = (porigin_site)', 'porigin_site = PORIGIN n_unit pcpath',
        '$origin_node(S_live.SOURCES,porigin_site) = (NExprClassConstFetch expression_class expression_member metadata_fetch)',
        'expression_member = NExprFuncCall name_member (SEQUENCE eps) metadata_member',
        'S_globals_live = $global_table_view(S_live)',
        '$lookup(S_globals_live.ENV,$ptascii("class231")) = (n_class)',
        'S_globals_live.STORE[n_class] = DEFINED (POBJECT n_object)',
        '(HOBJECT n_object) <- S_live.ALLOCATIONS',
        '$heap_owners($heap_graph(S_live),HOBJECT n_object) = 1',
        'S_live.CURRENT = eps', 'S_live.FRAMES = eps', 'S_live.HELD = eps',
        '$ccn_output(S_live.EVENTS) = eps',
        'S_class = $class_constant_selector(S_live,expression_class,26)',
        'S_class.COMPLETION = NORMAL', 'S_class.RESULT = KNOWN (PSTRING ' + impl + ')',
        'S_class.STORE = S_live.STORE',
        '$class_named(S_class.CLASSNAMES,$ptlc(' + impl + ')) = (porigin_requested)',
        '$class_at(S_class.CLASSES,porigin_requested) = (pclassdesc)',
        '$class_constant_lookup(S_class,porigin_requested,$ptascii("TREE"),|S_class.CLASSES|) = (pclassconstantdesc)',
        'pclassconstantdesc.OWNERNAME = ' + base, 'porigin_decl = pclassconstantdesc.ORIGIN',
        'pclassconstantdesc.FOLDED', '$compiled_read(S_class,pclassconstantdesc.INITIALIZER) = (PARRAY n_donor)',
        'S_scheduled_raw = $drive_steps(S_live,1)', 'S_scheduled_raw.COMPLETION = BUDGET',
        'S_scheduled = S_scheduled_raw[.COMPLETION = NORMAL]',
        'S_scheduled.TODO = ptask_eval :: (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ' + impl + ')) 26) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING ' + impl + ')) 26) :: ptask_tail*',
        'ptask_eval = $at_task($origin_child(S_live.ORIGIN,[PCFIELD 1]),EVAL expression_member)',
        '$task_nodes(CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING ' + impl + ')) 26) = eps',
        '$heap_owners($heap_graph(S_scheduled),HOBJECT n_object) = 1',
        '$call_descriptors_valid(S_scheduled)',
        'S_pair = $object_cv_pause(S_scheduled,true,30000)', '$object_cv_ready(S_pair,true)',
        'S_pair.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ' + impl + ')) 26) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING ' + impl + ')) 26) :: ptask_tail*',
        '$ccn_output(S_pair.EVENTS) = $ptascii("M|D|R|")',
        '~((HOBJECT n_object) <- S_pair.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_pair),HOBJECT n_object) = 0',
        '$(n_object < |S_pair.OBJECTS|)',
        'S_pair.CURRENT = eps', 'S_pair.FRAMES = eps', 'S_pair.HELD = eps',
        'S_pair.RESULT = KNOWN pvalue_member', '$string_bytes(pvalue_member) = ($ptascii("TREE"))',
        '$constant_value_class_valid(S_pair,pvalue_member,PVSTRING false)', '$value_nodes(pvalue_member) = eps',
        'S_globals_pair = $global_table_view(S_pair)',
        '$lookup(S_globals_pair.ENV,$ptascii("class231")) = (n_class)',
        'S_globals_pair.STORE[n_class] = DEFINED PNULL',
        '$code_at(S_pair.CODE,n_unit) = (pcode)',
        '$code_expression(pcode.EXPRESSIONS,pcpath) = ((26,false))',
        '$code_expression(pcode.EXPRESSIONS,pcpath ++ [PCFIELD 1]) = ((z_member,false))',
        '$compiled_read(S_pair,PORIGIN n_unit (pcpath ++ [PCFIELD 0])) = eps',
        '$call_task_valid(S_pair,CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ' + impl + ')) 26)',
        '$call_descriptors_valid(S_pair)',
        '$class_constant_cv_rvalue_source(S_pair,porigin_decl,' + impl + ',$ptascii("TREE"),26)',
        '$class_constant_cv_rvalue_entry(S_pair,S_pair.RESULT,expression_class,KNOWN (PSTRING ' + impl + '),26,ptask_tail*) = (pclassconstantdesc)',
        '~$class_constant_notice_valid(S_pair,porigin_decl,' + impl + ',$ptascii("TREE"),26)',
        '~$class_constant_notice_protected(S_pair,porigin_decl)',
        '$class_constant_cv_rvalue_entry(S_pair,REFERENCE n_class,expression_class,KNOWN (PSTRING ' + impl + '),26,ptask_tail*) = eps',
        '$class_constant_cv_rvalue_entry(S_pair,KNOWN PNULL,expression_class,KNOWN (PSTRING ' + impl + '),26,ptask_tail*) = eps',
        '$class_constant_cv_rvalue_entry(S_pair,S_pair.RESULT,expression_class,KNOWN (PSTRING ' + impl + '),26,DISCARD :: ptask_tail*) = eps',
        '$class_constant_cv_rvalue_entry(S_pair[.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ' + impl + ')) 26) :: ptask_tail*],S_pair.RESULT,expression_class,KNOWN (PSTRING ' + impl + '),26,ptask_tail*) = eps',
        '$class_constant_selected_valid(S_pair,expression_class,KNOWN (PSTRING ' + base + '))',
        '$class_constant_cv_rvalue_source(S_pair,porigin_decl,' + base + ',$ptascii("TREE"),26)',
        '$class_constant_cv_rvalue_entry(S_pair,S_pair.RESULT,expression_class,KNOWN (PSTRING ' + base + '),26,ptask_tail*) = eps',
        'S_warn_raw = $drive_steps(S_pair,1)', 'S_warn_raw.COMPLETION = BUDGET',
        'S_warn = S_warn_raw[.COMPLETION = NORMAL]', '$ccn_ready(S_warn,0)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ' + impl + ' $ptascii("TREE") 26',
        'perrorcall.LEVEL = 16384', 'perrorcall.LINE = 26',
        '$error_call_valid(S_warn,perrorcall)', '$call_descriptors_valid(S_warn)',
        '$class_constant_notice_valid(S_warn,porigin_decl,' + impl + ',$ptascii("TREE"),26)',
        '$task_nodes(perrorcall.RESUME) = eps', '$class_constant_notice_protected(S_warn,porigin_decl)',
        'S_warn.CLASSCONSTANTINIT = eps', 'S_warn.CLASSCONSTANTCACHE = eps',
        'S_resume = $ccn_pause(S_warn,1,30000)', '$ccn_ready(S_resume,1)',
        '$ccn_output(S_resume.EVENTS) = $ptascii("M|D|R|H|")',
        'S_resume.TODO = perrorcall.RESUME :: ptask_resume*',
        '$class_constant_notice_valid(S_resume,porigin_decl,' + impl + ',$ptascii("TREE"),26)',
        '~$class_constant_notice_valid(S_resume[.RESULT = KNOWN (PSTRING ' + base + ')],porigin_decl,' + base + ',$ptascii("TREE"),26)',
        '$call_descriptors_valid(S_resume)',
        'n_before = $heap_owners($heap_graph(S_resume),HARRAY n_donor)',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_resume',
        'S_one_raw = $drive_steps(S_resume,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]', 'S_one.RESULT = KNOWN (PARRAY n_donor)',
        '$heap_owners($heap_graph(S_one),HARRAY n_donor) = $(n_before + 1)',
        '~$class_constant_notice_protected(S_one,porigin_decl)',
        'S_done = $drive(S_one,30000)', 'S_done.COMPLETION = NORMAL',
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
