#!/usr/bin/env python3
"""Check protected computed access, scoped notice authority and array COW."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_protected_computed_notice_review/access-and-cow.php'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
quoted = lambda value: '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'

SELECTED = FETCH_SELECTED + r'''
dec $protected_computed_ready(pstate,int) : bool
def $protected_computed_ready(S,z) = true
  -- if S.COMPLETION = NORMAL
  -- if S.TODO = (CLASS_CONST_MEMBER expression_class poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: ptask*
  -- if S.ORIGIN = (porigin)
def $protected_computed_ready(S,z) = false -- otherwise
dec $protected_computed_pause(pstate,int,nat) : pstate
def $protected_computed_pause(S,z,n) = S -- if $protected_computed_ready(S,z)
def $protected_computed_pause(S,z,n) = $protected_computed_pause(S_next[.COMPLETION = NORMAL],z,$nabs($(n - 1)))
  -- if ~$protected_computed_ready(S,z)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $protected_computed_pause(S,z,n) = S -- otherwise
'''


def protected(fixture):
    expected = json.loads((SOURCE.parent / 'cases.json').read_text())[SOURCE.stem]['stdout']
    denied = expected.split('|')[1]
    child = quoted('Ns234Protected\\Child234')
    base = quoted('Ns234Protected\\Base234')
    raw = quoted('\\nS234pRoTeCtEd\\cHiLd234')
    spelling = quoted('nS234pRoTeCtEd\\cHiLd234')
    prefix = 'C|' + denied + '|S|'
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(SOURCE)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_cold = $protected_computed_pause(S_start[.COMPLETION = NORMAL],32,30000)',
        '$protected_computed_ready(S_cold,32)',
        'S_cold.TODO = (CLASS_CONST_MEMBER expression_cold (KNOWN (PSTRING ' + child + ')) 32) :: (CLASS_CONST_CAPTURE porigin_cold (KNOWN (PSTRING ' + child + ')) 32) :: ptask_cold*',
        'S_cold.CURRENT = eps', 'S_cold.FRAMES = eps',
        '$ccn_output(S_cold.EVENTS) = $ptascii("C|")',
        '$class_named(S_cold.CLASSNAMES,$ptlc(' + child + ')) = (porigin_child)',
        '$class_at(S_cold.CLASSES,porigin_child) = (pclassdesc_child)',
        '$class_named(S_cold.CLASSNAMES,$ptlc(' + base + ')) = (porigin_base)',
        '$class_constant_lookup(S_cold,porigin_child,$ptascii("TREE"),|S_cold.CLASSES|) = (pclassconstantdesc)',
        'porigin_decl = pclassconstantdesc.ORIGIN',
        'pclassconstantdesc.OWNER = porigin_base', 'pclassconstantdesc.VISIBILITY = PROPERTY_PROTECTED',
        'pclassconstantdesc.FOLDED',
        '$compiled_read(S_cold,pclassconstantdesc.INITIALIZER) = (PARRAY n_donor)',
        '$class_constant_deprecated(S_cold,pclassconstantdesc)',
        '~$class_constant_visible(S_cold,pclassconstantdesc)',
        '~$class_constant_deprecated(S_cold,pclassconstantdesc[.VISIBILITY = PROPERTY_PUBLIC])',
        '~$class_constant_deprecated(S_cold,pclassconstantdesc[.VISIBILITY = PROPERTY_PRIVATE])',
        '$class_constant_attribute_group(S_cold.SOURCES,pclassconstantdesc[.VISIBILITY = PROPERTY_PUBLIC]) =/= eps',
        '~$class_constant_inline_allowed(S_cold.SOURCES,pclassconstantdesc[.VISIBILITY = PROPERTY_PUBLIC])',
        '~$class_constant_query_readable(S_cold,pclassconstantdesc[.VISIBILITY = PROPERTY_PUBLIC])',
        '~$class_constant_dual_cv_source(S_cold,porigin_decl,' + child + ',$ptascii("TREE"),32)',
        '~$class_constant_notice_valid(S_cold,porigin_decl,' + child + ',$ptascii("TREE"),32)',
        '~$call_task_valid(S_cold,DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ' + child + ' $ptascii("TREE") 32)',
        '$call_descriptors_valid(S_cold)',
        'PhpStep: S_cold ~> S_denied',
        'S_denied.COMPLETION = THROWN "Error" ' + quoted(denied) + ' 32',
        'S_denied.EVENTS = S_cold.EVENTS',
        'S_denied.CLASSCONSTANTCACHE = S_cold.CLASSCONSTANTCACHE',
        'S_denied.CLASSCONSTANTHISTORY = S_cold.CLASSCONSTANTHISTORY',
        'S_pair = $protected_computed_pause(S_cold,11,30000)', '$protected_computed_ready(S_pair,11)',
        'S_pair.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ' + child + ')) 11) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING ' + child + ')) 11) :: ptask_tail*',
        '$ccn_output(S_pair.EVENTS) = ' + quoted(prefix),
        'S_pair.CURRENT = (pcallcontext)',
        'pcallcontext.LEXICAL_CLASS = (porigin_child)', 'pcallcontext.CALLED_CLASS = (porigin_child)',
        'pcallcontext.RECEIVER = eps', 'pcallcontext.WRAPPER = eps',
        '$class_link_at(S_pair.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_base)',
        '$method_current_scope(S_pair) = (porigin_child)',
        '$class_constant_visible(S_pair,pclassconstantdesc)',
        '$call_current_valid(S_pair)', '$call_descriptors_valid(S_pair)',
        'S_pair.RESULT = VARIABLE preqbytes_member z_variable',
        'S_name = $resolve_at(S_pair,S_pair.RESULT,11)', 'S_name.COMPLETION = NORMAL',
        'S_name.RESULT = KNOWN pvalue_member', '$string_bytes(pvalue_member) = ($ptascii("TREE"))',
        '$class_constant_dual_cv_source(S_name,porigin_decl,' + child + ',$ptascii("TREE"),11)',
        '$class_constant_dual_cv_entry(S_name,expression_class,KNOWN (PSTRING ' + child + '),11,ptask_tail*) = (pclassconstantdesc)',
        '~$class_constant_notice_valid(S_name,porigin_decl,' + child + ',$ptascii("TREE"),11)',
        '~$class_constant_visible(S_name[.CURRENT = eps],pclassconstantdesc)',
        '~$class_constant_dual_cv_source(S_name[.CURRENT = eps],porigin_decl,' + child + ',$ptascii("TREE"),11)',
        '$class_constant_dual_cv_entry(S_name,expression_class,KNOWN (PSTRING ' + base + '),11,ptask_tail*) = eps',
        'S_warn_raw = $drive_steps(S_pair,1)', 'S_warn_raw.COMPLETION = BUDGET',
        'S_warn = S_warn_raw[.COMPLETION = NORMAL]', '$ccn_ready(S_warn,0)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ' + child + ' $ptascii("TREE") 11',
        'perrorcall.LEVEL = 16384',
        'perrorcall.MESSAGE = $class_constant_notice_message(pclassconstantdesc,$ptascii("TREE"))',
        '$error_call_valid(S_warn,perrorcall)', '$call_descriptors_valid(S_warn)',
        '$class_constant_notice_valid(S_warn,porigin_decl,' + child + ',$ptascii("TREE"),11)',
        '$class_constant_notice_protected(S_warn,porigin_decl)', '$task_nodes(perrorcall.RESUME) = eps',
        'S_resume = $ccn_pause(S_warn,1,30000)', '$ccn_ready(S_resume,1)',
        'S_resume.CURRENT = S_pair.CURRENT',
        '$ccn_output(S_resume.EVENTS) = ' + quoted(prefix + 'H|'),
        '$class_constant_visible(S_resume,pclassconstantdesc)',
        '$class_constant_notice_valid(S_resume,porigin_decl,' + child + ',$ptascii("TREE"),11)',
        '~$class_constant_notice_valid(S_resume[.CURRENT = eps],porigin_decl,' + child + ',$ptascii("TREE"),11)',
        '~$class_constant_notice_valid(S_resume[.RESULT = KNOWN (PSTRING ' + base + ')],porigin_decl,' + base + ',$ptascii("TREE"),11)',
        '$call_descriptors_valid(S_resume)',
        'n_before = $heap_owners($heap_graph(S_resume),HARRAY n_donor)',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_resume',
        'S_one_raw = $drive_steps(S_resume,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]', 'S_one.RESULT = KNOWN (PARRAY n_donor)',
        '$heap_owners($heap_graph(S_one),HARRAY n_donor) = $(n_before + 1)',
        'S_second = $protected_computed_pause(S_one,15,30000)', '$protected_computed_ready(S_second,15)',
        'S_second.TODO = (CLASS_CONST_MEMBER expression_second (KNOWN (PSTRING ' + spelling + ')) 15) :: (CLASS_CONST_CAPTURE porigin_second (KNOWN (PSTRING ' + spelling + ')) 15) :: ptask_second*',
        '$ccn_output(S_second.EVENTS) = ' + quoted(prefix + 'H|A|1|MUT|7|'),
        'S_second.CURRENT = S_pair.CURRENT',
        'S_second.ORIGIN = (PORIGIN n_unit pcpath_second)',
        '$compiled_read(S_second,PORIGIN n_unit (pcpath_second ++ [PCFIELD 0])) = (PSTRING ' + raw + ')',
        '$compiled_read(S_second,PORIGIN n_unit (pcpath_second ++ [PCFIELD 1])) = (PSTRING $ptascii("TREE"))',
        '$class_constant_visible(S_second,pclassconstantdesc)',
        '$class_constant_notice_valid(S_second,porigin_decl,' + spelling + ',$ptascii("TREE"),15)',
        '~$class_constant_notice_valid(S_second[.CURRENT = eps],porigin_decl,' + spelling + ',$ptascii("TREE"),15)',
        '$lookup(S_second.ENV,$ptascii("first234")) = (n_first)',
        'S_second.STORE[n_first] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_donor',
        'S_second.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
        'S_second.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        '$call_descriptors_valid(S_second)',
        'S_warm = $protected_computed_pause(S_second,43,30000)', '$protected_computed_ready(S_warm,43)',
        'S_warm.CURRENT = eps', 'S_warm.FRAMES = eps',
        '$class_constant_deprecated(S_warm,pclassconstantdesc)',
        '~$class_constant_visible(S_warm,pclassconstantdesc)',
        '~$class_constant_notice_valid(S_warm,porigin_decl,' + spelling + ',$ptascii("TREE"),43)',
        '~$call_task_valid(S_warm,DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ' + spelling + ' $ptascii("TREE") 43)',
        '~$class_constant_notice_protected(S_warm,porigin_decl)',
        '$call_descriptors_valid(S_warm)',
        'PhpStep: S_warm ~> S_denied_warm',
        'S_denied_warm.COMPLETION = THROWN "Error" ' + quoted(denied) + ' 43',
        'S_denied_warm.EVENTS = S_warm.EVENTS',
        'S_denied_warm.CLASSCONSTANTCACHE = S_warm.CLASSCONSTANTCACHE',
        'S_done = $drive(S_warm,30000)', 'S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = ' + quoted(expected),
        'S_globals = $global_table_view(S_done)',
        '$lookup(S_globals.ENV,$ptascii("result234")) = (n_result)',
        '$lookup(S_globals.ENV,$ptascii("plain234")) = (n_plain)',
        'S_globals.STORE[n_result] = DEFINED (PARRAY n_donor)',
        'S_globals.STORE[n_plain] = DEFINED (PARRAY n_donor)',
        'S_done.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]',
        'S_done.CLASSCONSTANTCACHE = eps', 'S_done.CLASSCONSTANTINIT = eps',
        'S_done.CLASSCONSTANTHISTORY = S_cold.CLASSCONSTANTHISTORY',
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
    checks = protected(checked['fixture'])
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + SELECTED + '\ndec $main() : bool\ndef $main() = true\n'
        + ''.join('  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks))
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
