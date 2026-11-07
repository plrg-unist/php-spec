#!/usr/bin/env python3
"""Check normal This retention through parent keyword runtime-member notice."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_parent_rvalue_member_notice_review/receiver-lifetime.php'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
quoted = lambda value: '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'


SELECTED = FETCH_SELECTED + r"""
dec $parent_member_ready(pstate) : bool
def $parent_member_ready(S) = true
  -- if S.COMPLETION = NORMAL
  -- if S.TODO = (CLASS_CONST_MEMBER name_class poperand_class z) :: (CLASS_CONST_CAPTURE porigin poperand_class z) :: ptask*
  -- if $ppscoped_keyword(name_class)
def $parent_member_ready(S) = false -- otherwise
dec $parent_member_pause(pstate,nat) : pstate
def $parent_member_pause(S,n) = S -- if $parent_member_ready(S)
def $parent_member_pause(S,n) = $parent_member_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$parent_member_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $parent_member_pause(S,n) = S -- otherwise
"""


def parent_member(fixture):
    expected = json.loads((SOURCE.parent / 'cases.json').read_text())[SOURCE.stem]['stdout']
    child = quoted('Ns232Parent\\Child232')
    base = quoted('Ns232Parent\\Base232')
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(SOURCE)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_pair = $parent_member_pause(S_start[.COMPLETION = NORMAL],30000)', '$parent_member_ready(S_pair)',
        'S_pair.TODO = (CLASS_CONST_MEMBER name_class (KNOWN (PSTRING ' + base + ')) 9) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING ' + base + ')) 9) :: ptask_tail*',
        'S_pair.ORIGIN = (porigin_site)', 'porigin_site = PORIGIN n_unit pcpath',
        '$origin_node(S_pair.SOURCES,porigin_site) = (NExprClassConstFetch name_class expression_member metadata_fetch)',
        'name_class = NName (BYTES text_parent) metadata_parent', '$base64(text_parent) = $ptascii("parent")',
        'expression_member = NExprFuncCall name_member (SEQUENCE eps) metadata_member',
        '$ccn_output(S_pair.EVENTS) = $ptascii("M|R|")',
        'S_pair.CURRENT = (pcallcontext)', 'pcallcontext.RECEIVER = (n_object)',
        'pcallcontext.ARGC = 0', 'pcallcontext.INSTANCE = eps',
        'pcallcontext.WRAPPER = eps', 'pcallcontext.CACHE = eps',
        '(HOBJECT n_object) <- S_pair.ALLOCATIONS',
        '$heap_owners($heap_graph(S_pair),HOBJECT n_object) = 1',
        'S_pair.HELD = eps',
        'S_globals_pair = $global_table_view(S_pair)',
        '$lookup(S_globals_pair.ENV,$ptascii("receiver232")) = (n_receiver)',
        'S_globals_pair.STORE[n_receiver] = DEFINED PNULL',
        '$target_function(S_pair,pcallcontext.TARGET) = (pfunction)',
        'pcallcontext.FUNCTION = pfunction.ORIGIN', 'pcallcontext.NAME = pfunction.NAME',
        '$parameter_method_source(S_pair,pfunction) = (pmethoddesc)',
        'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC',
        '$class_constant_keyword_method(S_pair,porigin_site)',
        '$code_expression(pfunction.CODE.EXPRESSIONS,pcpath) = ((9,false))',
        '$code_expression(pfunction.CODE.EXPRESSIONS,pcpath ++ [PCFIELD 1]) = ((z_member,false))',
        'S_pair.RESULT = KNOWN pvalue_member', '$string_bytes(pvalue_member) = ($ptascii("TREE"))',
        '$constant_value_class_valid(S_pair,pvalue_member,PVSTRING false)', '$value_nodes(pvalue_member) = eps',
        '$class_named(S_pair.CLASSNAMES,$ptlc(' + base + ')) = (porigin_requested)',
        '$class_constant_lookup(S_pair,porigin_requested,$ptascii("TREE"),|S_pair.CLASSES|) = (pclassconstantdesc)',
        'pclassconstantdesc.OWNERNAME = ' + base, 'porigin_decl = pclassconstantdesc.ORIGIN',
        'pclassconstantdesc.FOLDED', '$compiled_read(S_pair,pclassconstantdesc.INITIALIZER) = (PARRAY n_donor)',
        '$class_constant_selected_valid(S_pair,name_class,KNOWN (PSTRING ' + base + '))',
        '~$class_constant_selected_valid(S_pair,name_class,KNOWN (PSTRING ' + child + '))',
        '$task_nodes(CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING ' + base + ')) 9) = eps',
        '$call_task_valid(S_pair,CLASS_CONST_MEMBER name_class (KNOWN (PSTRING ' + base + ')) 9)',
        '$call_descriptors_valid(S_pair)',
        '$class_constant_keyword_rvalue_source(S_pair,porigin_decl,' + base + ',$ptascii("TREE"),9)',
        '$class_constant_keyword_rvalue_entry(S_pair,S_pair.RESULT,name_class,KNOWN (PSTRING ' + base + '),9,ptask_tail*) = (pclassconstantdesc)',
        '~$class_constant_notice_valid(S_pair,porigin_decl,' + base + ',$ptascii("TREE"),9)',
        '~$class_constant_notice_protected(S_pair,porigin_decl)',
        '~$class_constant_keyword_method(S_pair[.CURRENT = eps],porigin_site)',
        '~$class_constant_keyword_rvalue_source(S_pair[.CURRENT = eps],porigin_decl,' + base + ',$ptascii("TREE"),9)',
        '$class_constant_keyword_rvalue_entry(S_pair,REFERENCE n_receiver,name_class,KNOWN (PSTRING ' + base + '),9,ptask_tail*) = eps',
        '$class_constant_keyword_rvalue_entry(S_pair,KNOWN PNULL,name_class,KNOWN (PSTRING ' + base + '),9,ptask_tail*) = eps',
        '$class_constant_keyword_rvalue_entry(S_pair,S_pair.RESULT,name_class,KNOWN (PSTRING ' + base + '),9,DISCARD :: ptask_tail*) = eps',
        '$class_constant_keyword_rvalue_entry(S_pair[.TODO = (CLASS_CONST_MEMBER name_class (KNOWN (PSTRING ' + base + ')) 9) :: ptask_tail*],S_pair.RESULT,name_class,KNOWN (PSTRING ' + base + '),9,ptask_tail*) = eps',
        '~$class_constant_keyword_rvalue_source(S_pair,porigin_decl,' + child + ',$ptascii("TREE"),9)',
        '~$class_constant_keyword_rvalue_source(S_pair,porigin_decl,' + base + ',$ptascii("TREE"),10)',
        'S_warn_raw = $drive_steps(S_pair,1)', 'S_warn_raw.COMPLETION = BUDGET',
        'S_warn = S_warn_raw[.COMPLETION = NORMAL]', '$ccn_ready(S_warn,0)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ' + base + ' $ptascii("TREE") 9',
        'perrorcall.LEVEL = 16384', 'perrorcall.LINE = 9',
        '$error_call_valid(S_warn,perrorcall)', '$call_descriptors_valid(S_warn)',
        '$class_constant_notice_valid(S_warn,porigin_decl,' + base + ',$ptascii("TREE"),9)',
        '$task_nodes(perrorcall.RESUME) = eps', '$class_constant_notice_protected(S_warn,porigin_decl)',
        '(HOBJECT n_object) <- S_warn.ALLOCATIONS',
        '$heap_owners($heap_graph(S_warn),HOBJECT n_object) = 1',
        'S_warn.CLASSCONSTANTINIT = eps', 'S_warn.CLASSCONSTANTCACHE = eps',
        'S_resume = $ccn_pause(S_warn,1,30000)', '$ccn_ready(S_resume,1)',
        '$ccn_output(S_resume.EVENTS) = $ptascii("M|R|H|")',
        'S_resume.TODO = perrorcall.RESUME :: ptask_resume*',
        'S_resume.CURRENT = (pcallcontext_resume)', 'pcallcontext_resume.FUNCTION = pfunction.ORIGIN',
        'pcallcontext_resume.RECEIVER = (n_object)',
        '(HOBJECT n_object) <- S_resume.ALLOCATIONS',
        '$heap_owners($heap_graph(S_resume),HOBJECT n_object) = 1',
        '$class_constant_keyword_method(S_resume,porigin_site)',
        '$class_constant_notice_valid(S_resume,porigin_decl,' + base + ',$ptascii("TREE"),9)',
        '$call_descriptors_valid(S_resume)',
        'n_before = $heap_owners($heap_graph(S_resume),HARRAY n_donor)',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_resume',
        'S_one_raw = $drive_steps(S_resume,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]', 'S_one.RESULT = KNOWN (PARRAY n_donor)',
        '$heap_owners($heap_graph(S_one),HARRAY n_donor) = $(n_before + 1)',
        '(HOBJECT n_object) <- S_one.ALLOCATIONS',
        '$heap_owners($heap_graph(S_one),HOBJECT n_object) = 1',
        '~$class_constant_notice_protected(S_one,porigin_decl)',
        'S_done = $drive(S_one,30000)', 'S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = ' + quoted(expected),
        '~((HOBJECT n_object) <- S_done.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_done),HOBJECT n_object) = 0',
        '$(n_object < |S_done.OBJECTS|)',
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
    checks = parent_member(checked['fixture'])
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
