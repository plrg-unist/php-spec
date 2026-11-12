#!/usr/bin/env python3
"""Check object member capture, COW and supplied throw cancellation."""
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
SOURCE_DIR = ROOT / 'tests/semantics/deprecated_object_member_notice_review'
SOURCES = {name: SOURCE_DIR / (name + '.php') for name in ('late-cv-and-pool', 'destructor-throw')}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
quoted = lambda value: '$base64(' + json.dumps(base64.b64encode(value.encode()).decode()) + ')'

SELECTED = FETCH_SELECTED + r'''
dec $object_member_ready(pstate,nat) : bool
def $object_member_ready(S,0) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class phpType20 z) :: ptask*
  -- if S.RESULT = KNOWN (POBJECT n)
  -- if S.OBJECTS[n] = INSTANCE porigin
def $object_member_ready(S,1) = true
  -- if S.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ptbytes_class)) z) :: (CLASS_CONST_CAPTURE porigin (KNOWN (PSTRING ptbytes_class)) z) :: (CLASS_CONST_OBJECT_CAPTURE porigin ptbytes_class z) :: ptask*
  -- if S.ORIGIN = (porigin)
def $object_member_ready(S,2) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
  -- if pdestructionoperation.SOURCE = CLASS_CONST_OBJECT_CAPTURE porigin ptbytes_class z
  -- if pdestructionoperation.PENDING = (n)
def $object_member_ready(S,n) = false -- otherwise
dec $object_member_pause(pstate,nat,nat) : pstate
def $object_member_pause(S,n_mode,n) = S -- if $object_member_ready(S,n_mode)
def $object_member_pause(S,n_mode,n) = $object_member_pause(S_next[.COMPLETION = NORMAL],n_mode,$nabs($(n - 1)))
  -- if ~$object_member_ready(S,n_mode)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $object_member_pause(S,n_mode,n) = S -- otherwise
'''


def raw_checks(seed):
    return ['S_raw = $object_member_pause(' + seed + ',0,30000)', '$object_member_ready(S_raw,0)',
        'S_raw.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask_tail*',
        'S_raw.RESULT = KNOWN (POBJECT n_receiver)', 'S_raw.ORIGIN = (porigin_site)',
        'S_raw.OBJECTS[n_receiver] = INSTANCE porigin_child',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_receiver) = 1',
        'S_class = $class_constant_selector(S_raw,expression_class,z)', 'S_class.RESULT = KNOWN (PSTRING ptbytes_class)',
        '$class_constant_object_class_entry(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        '~$class_constant_string_class_entry(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        '~$class_constant_object_class_entry(S_class,REFERENCE 0,expression_class,expression_member,z,ptask_tail*)',
        'PhpStep: S_raw ~> S_staged',
        'ptask_marker = CLASS_CONST_OBJECT_CAPTURE porigin_site ptbytes_class z',
        'S_staged.TODO = ptask_member :: (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ptbytes_class)) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING ptbytes_class)) z) :: ptask_marker :: ptask_tail*',
        'ptask_member = $at_task($origin_child((porigin_site),[PCFIELD 1]),EVAL expression_member)',
        'S_staged.RESULT = KNOWN PNULL', 'S_staged.BASE = BASE_VALUE (KNOWN PNULL)',
        '$task_nodes(ptask_marker) = eps', '~$class_constant_notice_task(ptask_marker,porigin_child)',
        '$call_task_valid(S_staged,ptask_marker)',
        'S_release_raw = $drive_steps(S_raw,1)', 'S_release_raw.COMPLETION = BUDGET',
        'S_release = S_release_raw[.COMPLETION = NORMAL]',
        'S_release.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
        'pdestructionoperation.SOURCE = ptask_marker', 'pdestructionoperation.PENDING = eps',
        '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
        '$eager_operation_source_guard(S_release,pdestructionoperation)', '$call_descriptors_valid(S_release)']


def renamed(checks, suffix):
    import re
    return [re.sub(r'\b(S_[A-Za-z0-9_]+|n_[A-Za-z0-9_]+|porigin_[A-Za-z0-9_]+|expression_[A-Za-z0-9_]+|ptbytes_[A-Za-z0-9_]+|ptask_[A-Za-z0-9_]+|pclassconstantdesc|pdestructionoperation[A-Za-z0-9_]*|perrorcall|pvalue_[A-Za-z0-9_]+|z)\b', lambda match: match.group() + suffix, check) for check in checks]


def recipe(fixture, name, source):
    checks = ['U_' + name.replace('-', '_') + ' = ' + fixture,
        'S_start = $php_run(U_' + name.replace('-', '_') + ',0,' + json.dumps(base64.b64encode(bytes(source)).decode()) + ')',
        'S_start.COMPLETION = BUDGET']
    checks += raw_checks('S_start[.COMPLETION = NORMAL]')
    namespace = 'Ns239Pool' if name == 'late-cv-and-pool' else 'Ns239Throw'
    child = quoted(namespace + '\\Child239')
    checks += ['ptbytes_class = ' + child,
        '$class_named(S_raw.CLASSNAMES,$ptlc(ptbytes_class)) = (porigin_child)']
    if name == 'destructor-throw':
        checks += ['S_global = $global_table_view(S_raw)',
            '$lookup(S_global.ENV,$ptascii("exception239")) = (n_exception_slot)',
            'S_global.STORE[n_exception_slot] = DEFINED (POBJECT n_exception)',
            '$lookup(S_global.ENV,$ptascii("value239")) = (n_value_slot)',
            '$class_constant_lookup(S_raw,porigin_child,$ptascii("TREE"),|S_raw.CLASSES|) = (pclassconstantdesc)',
            'porigin_decl = pclassconstantdesc.ORIGIN',
            '$compiled_read(S_raw,pclassconstantdesc.INITIALIZER) = (PARRAY n_donor)',
            'S_pending = $object_member_pause(S_release,2,30000)', '$object_member_ready(S_pending,2)',
            'S_pending.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending) :: ptask_pending*',
            'pdestructionoperation_pending = pdestructionoperation[.PENDING = (n_exception)]',
            'ptask_pending* = ptask_member :: (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ptbytes_class)) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING ptbytes_class)) z) :: ptask_marker :: ptask_tail*',
            '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending) = [HOBJECT n_exception]',
            '$task_nodes(ptask_marker) = eps',
            '$eager_operation_source_guard(S_pending,pdestructionoperation_pending)',
            '$class_constant_object_capture_source(S_pending,porigin_site,ptbytes_class,z)',
            '$call_task_valid(S_pending[.COMPLETION = THROWING n_exception],ptask_marker)',
            '~((HOBJECT n_receiver) <- S_pending.ALLOCATIONS)',
            '~$class_constant_notice_protected(S_pending,porigin_decl)',
            '$ccn_output(S_pending.EVENTS) = $ptascii("B|C|D|")',
            '$heap_owners($heap_graph(S_pending),HARRAY n_donor) = $heap_owners($heap_graph(S_raw),HARRAY n_donor)',
            'S_pending_global = $global_table_view(S_pending)',
            'S_pending_global.STORE[n_value_slot] = DEFINED pvalue_old', '$string_bytes(pvalue_old) = ($ptascii("old"))',
            '$call_descriptors_valid(S_pending)', 'S_done = $drive(S_pending,30000)']
    else:
        checks += ['S_pair = $object_member_pause(S_release,1,30000)', '$object_member_ready(S_pair,1)',
            '$ccn_output(S_pair.EVENTS) = $ptascii("B|C|D|")',
            '~((HOBJECT n_receiver) <- S_pair.ALLOCATIONS)',
            'S_pair.RESULT = VARIABLE $ptascii("member239") z_member',
            'S_name = $resolve_at(S_pair,S_pair.RESULT,z)', 'S_name.RESULT = KNOWN pvalue_member',
            '$string_bytes(pvalue_member) = ($ptascii("TREE"))',
            '$class_constant_lookup(S_name,porigin_child,$ptascii("TREE"),|S_name.CLASSES|) = (pclassconstantdesc)',
            'porigin_decl = pclassconstantdesc.ORIGIN',
            '$compiled_read(S_name,pclassconstantdesc.INITIALIZER) = (PARRAY n_donor)',
            '$class_constant_object_member_entry(S_name,S_pair.RESULT,expression_class,KNOWN (PSTRING ptbytes_class),z,ptask_tail*) = (pclassconstantdesc)',
            '$class_constant_object_member_entry(S_name,KNOWN pvalue_member,expression_class,KNOWN (PSTRING ptbytes_class),z,ptask_tail*) = eps',
            '$class_constant_object_member_entry(S_name,REFERENCE 0,expression_class,KNOWN (PSTRING ptbytes_class),z,ptask_tail*) = eps',
            'S_without = S_name[.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ptbytes_class)) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING ptbytes_class)) z) :: ptask_tail*]',
            '$class_constant_object_member_entry(S_without,S_pair.RESULT,expression_class,KNOWN (PSTRING ptbytes_class),z,ptask_tail*) = eps',
            'S_warn_raw = $drive_steps(S_pair,1)', 'S_warn_raw.COMPLETION = BUDGET',
            'S_warn = S_warn_raw[.COMPLETION = NORMAL]', '$ccn_ready(S_warn,0)',
            'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
            'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ptbytes_class $ptascii("TREE") z',
            '$task_nodes(perrorcall.RESUME) = eps',
            'S_resume = $ccn_pause(S_warn,1,30000)', '$ccn_ready(S_resume,1)',
            '$ccn_output(S_resume.EVENTS) = $ptascii("B|C|D|H|")',
            'S_global = $global_table_view(S_resume)', '$lookup(S_global.ENV,$ptascii("member239")) = (n_member_slot)',
            'S_global.STORE[n_member_slot] = DEFINED pvalue_now', '$string_bytes(pvalue_now) = ($ptascii("A"))',
            '$class_constant_notice_valid(S_resume,porigin_decl,ptbytes_class,$ptascii("TREE"),z)',
            'S_value_raw = $drive_steps(S_resume,1)', 'S_value_raw.COMPLETION = BUDGET',
            'S_value = S_value_raw[.COMPLETION = NORMAL]', 'S_value.RESULT = KNOWN (PARRAY n_donor)',
            '$heap_owners($heap_graph(S_value),HARRAY n_donor) = $($heap_owners($heap_graph(S_resume),HARRAY n_donor) + 1)',
            '~$class_constant_notice_protected(S_value,porigin_decl)',
            'S_raw_next = $object_member_pause(S_value,0,30000)', '$object_member_ready(S_raw_next,0)',
            'S_raw_next.TODO = (CLASS_CONST_CLASS expression_next expression_member_next z_next) :: ptask_next_tail*',
            'S_raw_next.RESULT = KNOWN (POBJECT n_next)', 'S_raw_next.ORIGIN = (porigin_next)',
            'S_next_class = $class_constant_selector(S_raw_next,expression_next,z_next)',
            '$class_constant_object_class_entry(S_next_class,S_raw_next.RESULT,expression_next,expression_member_next,z_next,ptask_next_tail*)',
            'S_pool_pair = $object_member_pause(S_raw_next,1,30000)', '$object_member_ready(S_pool_pair,1)',
            'S_pool_pair.TODO = (CLASS_CONST_MEMBER expression_next (KNOWN (PSTRING ptbytes_class)) z_next) :: (CLASS_CONST_CAPTURE porigin_next (KNOWN (PSTRING ptbytes_class)) z_next) :: (CLASS_CONST_OBJECT_CAPTURE porigin_next ptbytes_class z_next) :: ptask_next_tail*',
            'S_pool_pair.RESULT = KNOWN pvalue_pool', '$string_bytes(pvalue_pool) = ($ptascii("TREE"))',
            '~((HOBJECT n_next) <- S_pool_pair.ALLOCATIONS)',
            '$ccn_output(S_pool_pair.EVENTS) = $ptascii("B|C|D|H|R|2|MUT|7|C|D|")',
            '$class_constant_string_member_source(S_pool_pair,porigin_next,$ptascii("TREE"))',
            '~$class_constant_string_member_source(S_pool_pair,porigin_next,$ptascii("A"))',
            '$class_constant_object_member_entry(S_pool_pair,S_pool_pair.RESULT,expression_next,KNOWN (PSTRING ptbytes_class),z_next,ptask_next_tail*) = (pclassconstantdesc)',
            '$lookup(S_pool_pair.ENV,$ptascii("first239")) = (n_first_slot)',
            'S_pool_pair.STORE[n_first_slot] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_donor',
            'S_pool_pair.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
            'S_pool_pair.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2))]',
            '$call_descriptors_valid(S_pool_pair)', 'S_done = $drive(S_pool_pair,30000)']
    expected = json.loads((SOURCE_DIR / 'cases.json').read_text())[name]['stdout']
    checks += ['S_done.COMPLETION = NORMAL', '$ccn_output(S_done.EVENTS) = ' + quoted(expected),
        'S_done.DESTRUCTION.OPERATIONS = eps', 'S_done.CLASSCONSTANTINIT = eps', 'S_done.CLASSCONSTANTCACHE = eps',
        'S_done.CLASSCONSTANTHISTORY = S_raw.CLASSCONSTANTHISTORY',
        '$class_constant_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        'S_zero = $drive_steps(S_release,0)', 'S_zero.COMPLETION = BUDGET', 'S_zero[.COMPLETION = NORMAL] = S_release',
        'S_one = $drive_steps(S_release,1)', 'S_one.COMPLETION = BUDGET',
        '$drive(S_zero[.COMPLETION = NORMAL],30000) = S_done', '$drive(S_one[.COMPLETION = NORMAL],30000) = S_done']
    suffix = '_pool' if name == 'late-cv-and-pool' else '_throw'
    return renamed(checks,suffix)



def prepare(out):
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    checks = []
    try:
        for name, source in SOURCES.items():
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
            checks += recipe(checked['fixture'], name, source)
    finally:
        try: adapter.close()
        finally: frontend.close()
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + SELECTED + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), *SOURCES.values(), SOURCE_DIR / 'cases.json', *modules, *(ROOT / path for path in (
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
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in paths}
        report['passed'] = report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after'] and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable']
    finally: (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    if not report['passed']: print(report.get('stdout', '')[:2000], report.get('stderr', '')[:4000])
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__':
    main()
