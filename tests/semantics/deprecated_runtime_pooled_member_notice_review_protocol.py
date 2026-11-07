#!/usr/bin/env python3
"""Check runtime class-string kind and immutable member contracts."""
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
SOURCE = ROOT / 'tests/semantics/deprecated_runtime_pooled_member_notice_review/request-and-pool.php'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
quoted = lambda value: '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'

SELECTED = FETCH_SELECTED + r'''
dec $runtime_pool_ready(pstate,int,bool) : bool
def $runtime_pool_ready(S,z,false) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask*
def $runtime_pool_ready(S,z,true) = true
  -- if S.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ptbytes_class)) z) :: (CLASS_CONST_CAPTURE porigin (KNOWN (PSTRING ptbytes_class)) z) :: (CLASS_CONST_STRING_CAPTURE porigin ptbytes_class z) :: ptask*
def $runtime_pool_ready(S,z,b) = false -- otherwise
dec $runtime_pool_pause(pstate,int,bool,nat) : pstate
def $runtime_pool_pause(S,z,b,n) = S -- if $runtime_pool_ready(S,z,b)
def $runtime_pool_pause(S,z,b,n) = $runtime_pool_pause(S_next[.COMPLETION = NORMAL],z,b,$nabs($(n - 1)))
  -- if ~$runtime_pool_ready(S,z,b)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $runtime_pool_pause(S,z,b,n) = S -- otherwise
'''


def pooled(fixture):
    expected = json.loads((SOURCE.parent / 'cases.json').read_text())[SOURCE.stem]['stdout']
    child = quoted('Ns236Pool\\Child236')
    base = quoted('Ns236Pool\\Base236')
    other = quoted('Ns236Pool\\Other236')
    raw = quoted('\\nS236pOoL\\cHiLd236')
    return ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(SOURCE)).decode()) + ')',
        'S_raw = $runtime_pool_pause(S_start[.COMPLETION = NORMAL],34,false,30000)',
        '$runtime_pool_ready(S_raw,34,false)',
        'S_raw.TODO = (CLASS_CONST_CLASS expression_class expression_member 34) :: ptask_tail*',
        'S_raw.ORIGIN = (porigin_site)', 'porigin_site = PORIGIN n_unit pcpath',
        '$origin_node(S_raw.SOURCES,porigin_site) = (NExprClassConstFetch expression_class expression_member metadata)',
        'expression_class = NExprBinaryOpConcat expression_prefix expression_suffix metadata_class',
        'expression_member = NExprBinaryOpConcat expression_left expression_right metadata_member',
        'S_raw.RESULT = KNOWN pvalue_raw',
        'pvalue_raw = PSTRING_CARRIER (REQUEST_STRING n_request) ptbytes_raw',
        'ptbytes_raw = ' + raw, '$string_carrier_valid(S_raw,pvalue_raw)',
        '$constant_value_class_valid(S_raw,pvalue_raw,PVSTRING false)', '$value_nodes(pvalue_raw) = eps',
        'S_raw.CURRENT = eps', 'S_raw.FRAMES = eps', 'S_raw.HELD = eps',
        '$ccn_output(S_raw.EVENTS) = eps',
        '$code_at(S_raw.CODE,n_unit) = (pcode)',
        '$code_expression(pcode.EXPRESSIONS,pcpath) = ((34,false))',
        '$code_expression(pcode.EXPRESSIONS,pcpath ++ [PCFIELD 0]) = ((z_class,false))',
        'pcpath_member = pcpath ++ [PCFIELD 1]',
        '$code_expression(pcode.EXPRESSIONS,pcpath_member) = ((z_member,true))',
        '$compiled_read(S_raw,PORIGIN n_unit pcpath_member) = (PSTRING $ptascii("TREE"))',
        'S_class = $class_constant_selector(S_raw,expression_class,34)',
        'S_class.COMPLETION = NORMAL', 'S_class.RESULT = KNOWN (PSTRING ' + child + ')',
        '$class_constant_string_class_entry(S_class,S_raw.RESULT,expression_class,expression_member,34,ptask_tail*)',
        '~$class_constant_string_class_entry(S_class,REFERENCE 0,expression_class,expression_member,34,ptask_tail*)',
        'S_schedule_raw = $drive_steps(S_raw,1)', 'S_schedule_raw.COMPLETION = BUDGET',
        'S_schedule = S_schedule_raw[.COMPLETION = NORMAL]',
        'S_schedule.TODO = ptask_eval :: (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ' + child + ')) 34) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING ' + child + ')) 34) :: (CLASS_CONST_STRING_CAPTURE porigin_site ' + child + ' 34) :: ptask_tail*',
        'ptask_eval = $at_task($origin_child(S_raw.ORIGIN,[PCFIELD 1]),EVAL expression_member)',
        '$task_nodes(CLASS_CONST_STRING_CAPTURE porigin_site ' + child + ' 34) = eps',
        '$call_task_valid(S_schedule,CLASS_CONST_STRING_CAPTURE porigin_site ' + child + ' 34)',
        '$call_descriptors_valid(S_schedule)',
        'S_pair = $runtime_pool_pause(S_schedule,34,true,30000)', '$runtime_pool_ready(S_pair,34,true)',
        'S_pair.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ' + child + ')) 34) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING ' + child + ')) 34) :: (CLASS_CONST_STRING_CAPTURE porigin_site ' + child + ' 34) :: ptask_tail*',
        'S_pair.RESULT = KNOWN pvalue_member', '$string_bytes(pvalue_member) = ($ptascii("TREE"))',
        '$class_named(S_pair.CLASSNAMES,$ptlc(' + child + ')) = (porigin_child)',
        '$class_constant_lookup(S_pair,porigin_child,$ptascii("TREE"),|S_pair.CLASSES|) = (pclassconstantdesc)',
        'porigin_decl = pclassconstantdesc.ORIGIN', 'pclassconstantdesc.OWNERNAME = ' + base,
        'pclassconstantdesc.FOLDED', '$compiled_read(S_pair,pclassconstantdesc.INITIALIZER) = (PARRAY n_donor)',
        '$class_constant_string_member_source(S_pair,porigin_site,$ptascii("TREE"))',
        '~$class_constant_string_member_source(S_pair,porigin_site,$ptascii("WRONG"))',
        '~$class_constant_string_member_source(S_pair[.POOLS = eps],porigin_site,$ptascii("TREE"))',
        '$class_constant_string_member_original(S_pair,porigin_site,S_pair.RESULT,pvalue_member)',
        '~$class_constant_string_member_original(S_pair,porigin_site,VARIABLE $ptascii("suffix236") 34,pvalue_member)',
        '$class_constant_string_member_entry(S_pair,S_pair.RESULT,expression_class,KNOWN (PSTRING ' + child + '),34,ptask_tail*) = (pclassconstantdesc)',
        '$class_constant_string_member_entry(S_pair,REFERENCE 0,expression_class,KNOWN (PSTRING ' + child + '),34,ptask_tail*) = eps',
        '~$class_constant_notice_valid(S_pair,porigin_decl,' + child + ',$ptascii("TREE"),34)',
        '$call_descriptors_valid(S_pair)',
        'pcode_runtime = pcode[.EXPRESSIONS = (CODEEXPR pcpath_member z_member false) :: pcode.EXPRESSIONS]',
        'S_runtime_view = S_pair[.CODE = [pcode_runtime]]',
        '$compiled_read(S_runtime_view,PORIGIN n_unit pcpath_member) = eps',
        '$class_constant_string_member_source(S_runtime_view,porigin_site,$ptascii("WRONG"))',
        'S_missing = S_pair[.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ' + child + ')) 34) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING ' + child + ')) 34) :: ptask_tail*]',
        '$call_descriptors_valid(S_missing)',
        '$class_constant_string_member_entry(S_missing,S_missing.RESULT,expression_class,KNOWN (PSTRING ' + child + '),34,ptask_tail*) = eps',
        'S_missing_step = $drive_steps(S_missing,1)',
        'S_missing_step.COMPLETION = UNSUPPORTED "Deprecated class constant fetch"',
        'S_missing_step.EVENTS = S_pair.EVENTS',
        'S_metadata = S_pair[.ENV = eps][.STORE = eps][.RESULT = KNOWN PNULL]',
        '$call_task_valid(S_metadata,CLASS_CONST_STRING_CAPTURE porigin_site ' + child + ' 34)',
        '$class_constant_string_member_entry(S_metadata,S_pair.RESULT,expression_class,KNOWN (PSTRING ' + child + '),34,ptask_tail*) = eps',
        'S_warn_raw = $drive_steps(S_pair,1)', 'S_warn_raw.COMPLETION = BUDGET',
        'S_warn = S_warn_raw[.COMPLETION = NORMAL]', '$ccn_ready(S_warn,0)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ' + child + ' $ptascii("TREE") 34',
        'perrorcall.LEVEL = 16384',
        'perrorcall.MESSAGE = $class_constant_notice_message(pclassconstantdesc,$ptascii("TREE"))',
        '$error_call_valid(S_warn,perrorcall)', '$call_descriptors_valid(S_warn)',
        '$class_constant_notice_protected(S_warn,porigin_decl)',
        'S_inner_raw = $runtime_pool_pause(S_warn,21,false,30000)', '$runtime_pool_ready(S_inner_raw,21,false)',
        'S_inner_raw.TODO = (CLASS_CONST_CLASS expression_inner_class expression_inner_member 21) :: ptask_inner*',
        'S_inner_raw.ORIGIN = (porigin_inner)',
        'S_inner_raw.RESULT = KNOWN pvalue_inner_class',
        'pvalue_inner_class = PSTRING_CARRIER (REQUEST_STRING n_inner_request) ptbytes_inner_raw',
        '$string_bytes(pvalue_inner_class) = (' + quoted('\\nS236pOoL\\Child236') + ')',
        '$class_constant_notice_protected(S_inner_raw,porigin_decl)',
        'S_inner = $runtime_pool_pause(S_inner_raw,21,true,30000)', '$runtime_pool_ready(S_inner,21,true)',
        'S_inner.TODO = (CLASS_CONST_MEMBER expression_inner_class (KNOWN (PSTRING ' + child + ')) 21) :: (CLASS_CONST_CAPTURE porigin_inner (KNOWN (PSTRING ' + child + ')) 21) :: (CLASS_CONST_STRING_CAPTURE porigin_inner ' + child + ' 21) :: ptask_inner*',
        '$ccn_output(S_inner.EVENTS) = $ptascii("H|")',
        '$class_constant_string_member_entry(S_inner,S_inner.RESULT,expression_inner_class,KNOWN (PSTRING ' + child + '),21,ptask_inner*) = (pclassconstantdesc)',
        '~$class_constant_notice_valid(S_inner,porigin_decl,' + child + ',$ptascii("TREE"),21)',
        '$call_descriptors_valid(S_inner)',
        'n_inner_before = $heap_owners($heap_graph(S_inner),HARRAY n_donor)',
        'S_inner_value_raw = $drive_steps(S_inner,1)', 'S_inner_value_raw.COMPLETION = BUDGET',
        'S_inner_value = S_inner_value_raw[.COMPLETION = NORMAL]',
        'S_inner_value.RESULT = KNOWN (PARRAY n_donor)', 'S_inner_value.EVENTS = S_inner.EVENTS',
        '$heap_owners($heap_graph(S_inner_value),HARRAY n_donor) = $(n_inner_before + 1)',
        'S_resume = $ccn_pause(S_inner_value,1,30000)', '$ccn_ready(S_resume,1)',
        '$ccn_output(S_resume.EVENTS) = $ptascii("H|N|1|")',
        'S_globals_resume = $global_table_view(S_resume)',
        '$lookup(S_globals_resume.ENV,$ptascii("suffix236")) = (n_suffix)',
        'S_globals_resume.STORE[n_suffix] = DEFINED pvalue_suffix',
        '$string_bytes(pvalue_suffix) = ($ptascii("Other236"))',
        '$class_named(S_resume.CLASSNAMES,$ptlc(' + other + ')) = (porigin_other)',
        '$class_constant_lookup(S_resume,porigin_other,$ptascii("TREE"),|S_resume.CLASSES|) = (pclassconstantdesc_other)',
        '$class_constant_notice_valid(S_resume,porigin_decl,' + child + ',$ptascii("TREE"),34)',
        '~$class_constant_notice_valid(S_resume[.RESULT = KNOWN (PSTRING $ptascii("TREE"))],pclassconstantdesc_other.ORIGIN,' + other + ',$ptascii("TREE"),34)',
        '$call_descriptors_valid(S_resume)',
        'n_before = $heap_owners($heap_graph(S_resume),HARRAY n_donor)',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S_resume',
        'S_one_raw = $drive_steps(S_resume,1)', 'S_one_raw.COMPLETION = BUDGET',
        'S_one = S_one_raw[.COMPLETION = NORMAL]', 'S_one.RESULT = KNOWN (PARRAY n_donor)',
        '$heap_owners($heap_graph(S_one),HARRAY n_donor) = $(n_before + 1)',
        'S_second_raw = $runtime_pool_pause(S_one,38,false,30000)', '$runtime_pool_ready(S_second_raw,38,false)',
        'S_second_raw.TODO = (CLASS_CONST_CLASS expression_second_class expression_second_member 38) :: ptask_second*',
        'S_second_raw.ORIGIN = (porigin_second)',
        'S_second_raw.RESULT = KNOWN pvalue_second_class',
        'pvalue_second_class = PSTRING_CARRIER (REQUEST_STRING n_second_request) ptbytes_second_raw',
        '$string_bytes(pvalue_second_class) = (' + quoted('\\nS236pOoL\\Other236') + ')',
        '$ccn_output(S_second_raw.EVENTS) = $ptascii("H|N|1|A|1|MUT|7|")',
        'S_second = $runtime_pool_pause(S_second_raw,38,true,30000)', '$runtime_pool_ready(S_second,38,true)',
        '$class_constant_string_member_source(S_second,porigin_second,$ptascii("TREE"))',
        'S_second.TODO = (CLASS_CONST_MEMBER expression_second_class (KNOWN (PSTRING ' + other + ')) 38) :: (CLASS_CONST_CAPTURE porigin_second (KNOWN (PSTRING ' + other + ')) 38) :: (CLASS_CONST_STRING_CAPTURE porigin_second ' + other + ' 38) :: ptask_second*',
        '$class_constant_string_member_entry(S_second,S_second.RESULT,expression_second_class,KNOWN (PSTRING ' + other + '),38,ptask_second*) = (pclassconstantdesc_other)',
        'S_done = $drive(S_second,30000)', 'S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = ' + quoted(expected),
        'S_globals = $global_table_view(S_done)',
        '$lookup(S_globals.ENV,$ptascii("first236")) = (n_first)',
        '$lookup(S_globals.ENV,$ptascii("second236")) = (n_second)',
        '$lookup(S_globals.ENV,$ptascii("again236")) = (n_again)',
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
