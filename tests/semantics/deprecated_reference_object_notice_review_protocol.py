#!/usr/bin/env python3
"""Check retained reference objects, retargeted cells and destructor cancellation."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import subprocess

from deprecated_global_constant_protocol import PREFIX
from deprecated_class_constant_fetch_protocol import SELECTED as FETCH_SELECTED
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = Path(__file__).with_name('deprecated_reference_object_notice_review')
NAMES = ['retained-object-cow', 'retargeted-object', 'destructor-throw']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = lambda s: '$base64(' + json.dumps(base64.b64encode(s.encode()).decode()) + ')'
SELECTED = FETCH_SELECTED + r'''
dec $reference_object_ready(pstate,nat) : bool
def $reference_object_ready(S,0) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask*
  -- if S.RESULT = REFERENCE n_reference
  -- if $call_reference_operand_valid(S,S.RESULT)
  -- if S.STORE[n_reference] = DEFINED (POBJECT n_receiver)
def $reference_object_ready(S,1) = true
  -- if S.TODO = (CLASS_CONST_MEMBER expression_class poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: (CLASS_CONST_OBJECT_CAPTURE porigin ptbytes_class z) :: ptask*
def $reference_object_ready(S,2) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
  -- if pdestructionoperation.PENDING = (n_exception)
  -- if pdestructionoperation.SOURCE = CLASS_CONST_OBJECT_CAPTURE porigin ptbytes_class z
def $reference_object_ready(S,3) = true
  -- if S.CURRENT =/= eps
  -- if $ccn_output(S.EVENTS) = $ptascii("B|C|H|D|")
def $reference_object_ready(S,4) = true
  -- if S.CURRENT =/= eps
  -- if $ccn_output(S.EVENTS) = $ptascii("B|C|M|H|D|")
def $reference_object_ready(S,n) = false -- otherwise
dec $reference_object_pause(pstate,nat,nat) : pstate
def $reference_object_pause(S,n_phase,n_budget) = S -- if $reference_object_ready(S,n_phase)
def $reference_object_pause(S,n_phase,n_budget) = $reference_object_pause(S_next[.COMPLETION = NORMAL],n_phase,$nabs($(n_budget - 1)))
  -- if ~$reference_object_ready(S,n_phase)
  -- if S.COMPLETION = NORMAL /\ $(n_budget > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $reference_object_pause(S,n_phase,n_budget) = S -- otherwise
'''


def raw_checks(fixture, source, child, retained):
    checks = ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(source)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_raw = $reference_object_pause(S_start[.COMPLETION = NORMAL],0,30000)', '$reference_object_ready(S_raw,0)',
        'S_raw.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask_tail*',
        'S_raw.ORIGIN = (porigin_site)', 'S_raw.RESULT = REFERENCE n_reference',
        'S_raw.STORE[n_reference] = DEFINED (POBJECT n_receiver)',
        '$call_reference_operand_valid(S_raw,S_raw.RESULT)',
        '(HCELL n_reference) <- S_raw.ALLOCATIONS', '(HOBJECT n_receiver) <- S_raw.ALLOCATIONS',
        'S_raw.OBJECTS[n_receiver] = INSTANCE porigin_child',
        '$objectprops_at(S_raw.OBJECTPROPS,n_receiver) = (eps)',
        '$object_table_at(S_raw.OBJECTTABLES,n_receiver) = eps',
        'S_raw.CURRENT = eps', 'S_raw.FRAMES = eps', 'S_raw.HELD = eps',
        '$machine_base_roots(S_raw) = eps',
        '$class_at(S_raw.CLASSES,porigin_child) = (pclassdesc_child)', 'pclassdesc_child.NAME = ' + child,
        '$class_constant_lookup(S_raw,porigin_child,$ptascii("TREE"),|S_raw.CLASSES|) = (pclassconstantdesc)',
        'porigin_decl = pclassconstantdesc.ORIGIN', 'pclassconstantdesc.FOLDED',
        '$compiled_read(S_raw,pclassconstantdesc.INITIALIZER) = (PARRAY n_donor)',
        '$heap_owners($heap_graph(S_raw),HCELL n_reference) = ' + ('2' if retained else '1'),
        '$heap_owners($heap_graph(S_raw),HOBJECT n_receiver) = 1',
        '$call_descriptors_valid(S_raw)', '$ccn_output(S_raw.EVENTS) = $ptascii("B|C|")',
        'S_class = $class_constant_selector(S_raw,expression_class,z)',
        'S_class.COMPLETION = NORMAL', 'S_class.RESULT = KNOWN (PSTRING ' + child + ')',
        'S_class.STORE = S_raw.STORE', 'S_class.OBJECTS = S_raw.OBJECTS',
        'S_class.OBJECTPROPS = S_raw.OBJECTPROPS', 'S_class.OBJECTTABLES = S_raw.OBJECTTABLES',
        '$heap_owners($heap_graph(S_class),HCELL n_reference) = ' + ('1' if retained else '0'),
        '$heap_owners($heap_graph(S_class),HOBJECT n_receiver) = 1',
        '$class_constant_reference_object_selector(S_class,REFERENCE n_reference) = (pclassdesc_child)',
        '$class_constant_reference_selector(S_class,REFERENCE n_reference) = eps',
        '$class_constant_reference_object_selector(S_class,KNOWN (POBJECT n_receiver)) = eps',
        '$class_constant_reference_object_selector(S_class[.ALLOCATIONS = eps],REFERENCE n_reference) = eps',
        '$class_constant_reference_object_selector(S_class[.ALLOCATIONS = $native_remove_one(S_class.ALLOCATIONS,HCELL n_reference)],REFERENCE n_reference) = eps',
        '$class_constant_reference_object_selector(S_class[.ALLOCATIONS = $native_remove_one(S_class.ALLOCATIONS,HOBJECT n_receiver)],REFERENCE n_reference) = eps',
        '$class_constant_reference_object_selector(S_class[.REFCELLS = eps],REFERENCE n_reference) = eps',
        '$class_constant_reference_object_selector(S_class[.STORE = $set_cell(S_class.STORE,n_reference,UNDEFINED)],REFERENCE n_reference) = eps',
        '$class_constant_reference_object_selector(S_class[.STORE = $set_cell(S_class.STORE,n_reference,DEFINED PNULL)],REFERENCE n_reference) = eps',
        '$class_constant_reference_object_selector(S_class[.STORE = $set_cell(S_class.STORE,n_reference,DEFINED (PSTRING ' + child + '))],REFERENCE n_reference) = eps',
        '$class_constant_reference_object_selector(S_class[.OBJECTPROPS = eps],REFERENCE n_reference) = eps',
        '$class_constant_reference_object_selector(S_class[.OBJECTPROPS = $objectprops_set(S_class.OBJECTPROPS,n_receiver,[{DECL eps,NAME $ptascii("x"),STATE PROP_VALUE (DIRECT (PINT 1))}])],REFERENCE n_reference) = eps',
        '$class_constant_reference_object_selector(S_class[.OBJECTTABLES = [{OBJECT n_receiver,TABLE n_donor}]],REFERENCE n_reference) = eps',
        '$class_constant_reference_object_selector(S_class[.RESULT = KNOWN PNULL],REFERENCE n_reference) = eps']
    return checks


def recipe(fixture, name, source):
    retained = name != 'destructor-throw'
    literal = name == 'retained-object-cow'
    namespace = {'retained-object-cow': 'Ns241Retained', 'retargeted-object': 'Ns241Retarget', 'destructor-throw': 'Ns241Throw'}[name]
    child = quoted(namespace + '\\Child241')
    checks = raw_checks(fixture, source, child, retained)
    if literal:
        checks += ['expression_member = NIdentifier (BYTES text_member) metadata_member',
            '$class_constant_reference_object_literal_entry(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*) = (pclassconstantdesc)',
            '$class_constant_object_entry(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*) = eps',
            '$class_constant_reference_object_literal_entry(S_class[.HELD = [HCELL n_reference]],S_raw.RESULT,expression_class,expression_member,z,ptask_tail*) = eps',
            '$class_constant_reference_object_literal_entry(S_class[.BASE = BASE_VALUE (REFERENCE n_reference)],S_raw.RESULT,expression_class,expression_member,z,ptask_tail*) = eps',
            'ptask_marker = CLASS_CONST_OBJECT_FETCH porigin_site ' + child + ' $ptascii("TREE") z']
    else:
        checks += ['$class_constant_reference_object_capture_entry(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
            '~$class_constant_object_class_entry(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
            '~$class_constant_reference_object_capture_entry(S_class[.HELD = [HCELL n_reference]],S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
            '~$class_constant_reference_object_capture_entry(S_class[.BASE = BASE_VALUE (REFERENCE n_reference)],S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
            'ptask_marker = CLASS_CONST_OBJECT_CAPTURE porigin_site ' + child + ' z',
            'ptask_member = $at_task($origin_child((porigin_site),[PCFIELD 1]),EVAL expression_member)']
    checks += ['S_neutral = $class_constant_class_forward(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        'S_neutral.COMPLETION = NORMAL', 'S_neutral.RESULT = KNOWN PNULL', 'S_neutral.BASE = BASE_VALUE (KNOWN PNULL)',
        '$task_nodes(ptask_marker) = eps', '~$class_constant_notice_protected(S_neutral,porigin_decl)',
        '$heap_owners($heap_graph(S_neutral),HCELL n_reference) = ' + ('1' if retained else '0'),
        '$heap_owners($heap_graph(S_neutral),HOBJECT n_receiver) = 1',
        '$eager_operation_source(S_raw,CLASS_CONST_CLASS expression_class expression_member z) = ptask_marker',
        'S_step = $drive_steps(S_raw,1)', 'S_step.COMPLETION = BUDGET', 'S_release = S_step[.COMPLETION = NORMAL]']
    checks += ['S_neutral.TODO = ptask_marker :: ptask_tail*'] if literal else [
        'S_neutral.TODO = ptask_member :: (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ' + child + ')) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING ' + child + ')) z) :: ptask_marker :: ptask_tail*']
    if retained:
        checks += ['$eager_slots(S_raw,S_neutral) = eps', 'S_release.TODO = S_neutral.TODO',
            'S_release.RESULT = KNOWN PNULL', 'S_release.BASE = BASE_VALUE (KNOWN PNULL)',
            'S_release.DESTRUCTION.OPERATIONS = eps',
            '$call_reference_operand_valid(S_release,REFERENCE n_reference)',
            '$call_descriptors_valid(S_release)']
        if not literal:
            checks += ['S_pair = $reference_object_pause(S_release,1,30000)', '$reference_object_ready(S_pair,1)',
                'S_pair.TODO = (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ' + child + ')) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING ' + child + ')) z) :: ptask_marker :: ptask_tail*',
                '$ccn_output(S_pair.EVENTS) = $ptascii("B|C|M|")',
                'S_pair.RESULT = KNOWN pvalue_member', '$string_bytes(pvalue_member) = ($ptascii("TREE"))',
                '$class_constant_object_member_entry(S_pair,S_pair.RESULT,expression_class,KNOWN (PSTRING ' + child + '),z,ptask_tail*) = (pclassconstantdesc)',
                '$class_constant_string_member_entry(S_pair,S_pair.RESULT,expression_class,KNOWN (PSTRING ' + child + '),z,ptask_tail*) = eps',
                '$heap_owners($heap_graph(S_pair),HCELL n_reference) = 1',
                '$heap_owners($heap_graph(S_pair),HOBJECT n_receiver) = 1']
        checks += ['S_warn = $ccn_pause(' + ('S_release' if literal else 'S_pair') + ',0,30000)', '$ccn_ready(S_warn,0)',
            'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
            'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ' + child + ' $ptascii("TREE") z',
            '$task_nodes(perrorcall.RESUME) = eps', '$class_constant_notice_protected(S_warn,porigin_decl)',
            '$error_call_valid(S_warn,perrorcall)', '$call_descriptors_valid(S_warn)',
            '$call_reference_operand_valid(S_warn,REFERENCE n_reference)',
            '$heap_owners($heap_graph(S_warn),HCELL n_reference) = 1',
            '$heap_owners($heap_graph(S_warn),HOBJECT n_receiver) = 1',
            'S_inner = $reference_object_pause(S_warn,' + ('3' if literal else '4') + ',30000)',
            '$reference_object_ready(S_inner,' + ('3' if literal else '4') + ')',
            '$class_constant_notice_protected(S_inner,porigin_decl)',
            '(HOBJECT n_receiver) <- S_inner.ALLOCATIONS', '$call_descriptors_valid(S_inner)',
            'S_resume = $ccn_pause(S_inner,1,30000)', '$ccn_ready(S_resume,1)',
            '$ccn_output(S_resume.EVENTS) = $ptascii("' + ('B|C|H|D|V|2|' if literal else 'B|C|M|H|D|V|2|') + '")',
            '~((HOBJECT n_receiver) <- S_resume.ALLOCATIONS)',
            '$class_constant_notice_valid(S_resume,porigin_decl,' + child + ',$ptascii("TREE"),z)',
            '~$class_constant_notice_valid(S_resume,porigin_decl,' + child + ',$ptascii("TREE"),$(z + 1))',
            '$call_descriptors_valid(S_resume)',
            '$class_constant_reference_object_selector(S_resume[.RESULT = KNOWN (PSTRING ' + child + ')],REFERENCE n_reference) = eps',
            'n_donor_owners = $heap_owners($heap_graph(S_resume),HARRAY n_donor)',
            'S_value_step = $drive_steps(S_resume,1)', 'S_value_step.COMPLETION = BUDGET',
            'S_value = S_value_step[.COMPLETION = NORMAL]', 'S_value.RESULT = KNOWN (PARRAY n_donor)',
            '$heap_owners($heap_graph(S_value),HARRAY n_donor) = $(n_donor_owners + 1)',
            '~$class_constant_notice_protected(S_value,porigin_decl)', 'S_done = $drive(S_value,30000)']
        if literal:
            checks += ['~((HCELL n_reference) <- S_resume.ALLOCATIONS)',
                '~$call_reference_operand_valid(S_resume,REFERENCE n_reference)',
                'S_global_done = $global_table_view(S_done)',
                '$lookup(S_global_done.ENV,$ptascii("first241")) = (n_first)',
                '$lookup(S_global_done.ENV,$ptascii("again241")) = (n_again)',
                'S_global_done.STORE[n_first] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_donor',
                'S_global_done.STORE[n_again] = DEFINED (PARRAY n_donor)',
                'S_done.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
                'S_done.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2))]']
        else:
            checks += ['$call_reference_operand_valid(S_resume,REFERENCE n_reference)',
                'S_resume.STORE[n_reference] = DEFINED (POBJECT n_other)', 'n_other =/= n_receiver',
                'S_resume.OBJECTS[n_other] = INSTANCE porigin_other',
                '$class_at(S_resume.CLASSES,porigin_other) = (pclassdesc_other)',
                'pclassdesc_other.NAME = ' + quoted(namespace + '\\Other241'),
                '$heap_owners($heap_graph(S_resume),HCELL n_reference) = 1',
                '$class_constant_reference_object_selector(S_resume[.RESULT = KNOWN (PSTRING pclassdesc_other.NAME)],REFERENCE n_reference) = (pclassdesc_other)',
                '~$class_constant_notice_valid(S_resume,porigin_decl,pclassdesc_other.NAME,$ptascii("TREE"),z)',
                'S_global_done = $global_table_view(S_done)',
                '$lookup(S_global_done.ENV,$ptascii("first241")) = (n_first)',
                '$lookup(S_global_done.ENV,$ptascii("later241")) = (n_later)',
                'S_global_done.STORE[n_first] = DEFINED (PARRAY n_donor)',
                'S_global_done.STORE[n_later] = DEFINED (PARRAY n_later_value)', 'n_later_value =/= n_donor',
                'S_done.ARRAYS[n_donor].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2))]',
                'S_done.ARRAYS[n_later_value].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 3))]']
    else:
        checks += ['$eager_slots(S_raw,S_neutral) = [HCELL n_reference]',
            'S_release.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
            'pdestructionoperation.SOURCE = ptask_marker', 'pdestructionoperation.VALUE = KNOWN PNULL',
            'pdestructionoperation.BASE = BASE_VALUE (KNOWN PNULL)', 'pdestructionoperation.COMPLETION = NORMAL',
            'pdestructionoperation.PENDING = eps', '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
            '$eager_operation_source_guard(S_release,pdestructionoperation)',
            '~$eager_operation_source_guard(S_release,pdestructionoperation[.VALUE = REFERENCE n_reference])',
            '~$eager_operation_source_guard(S_release,pdestructionoperation[.VALUE = KNOWN (POBJECT n_receiver)])',
            '~$eager_operation_source_guard(S_release,pdestructionoperation[.BASE = BASE_VALUE (REFERENCE n_reference)])',
            '$call_descriptors_valid(S_release)',
            'S_global = $global_table_view(S_raw)',
            '$lookup(S_global.ENV,$ptascii("exception241")) = (n_exception_slot)',
            'S_global.STORE[n_exception_slot] = DEFINED (POBJECT n_exception)',
            '$lookup(S_global.ENV,$ptascii("value241")) = (n_value_slot)',
            'S_pending = $reference_object_pause(S_release,2,30000)', '$reference_object_ready(S_pending,2)',
            'S_pending.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending) :: ptask_pending*',
            'pdestructionoperation_pending = pdestructionoperation[.PENDING = (n_exception)]',
            'ptask_pending* = S_neutral.TODO',
            '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending) = [HOBJECT n_exception]',
            '$eager_operation_source_guard(S_pending,pdestructionoperation_pending)',
            '$call_task_valid(S_pending[.COMPLETION = THROWING n_exception],ptask_marker)',
            '~((HCELL n_reference) <- S_pending.ALLOCATIONS)', '~((HOBJECT n_receiver) <- S_pending.ALLOCATIONS)',
            '~$call_reference_operand_valid(S_pending,REFERENCE n_reference)',
            '~$class_constant_notice_protected(S_pending,porigin_decl)',
            '$ccn_output(S_pending.EVENTS) = $ptascii("B|C|D|")',
            '$heap_owners($heap_graph(S_pending),HARRAY n_donor) = $heap_owners($heap_graph(S_raw),HARRAY n_donor)',
            'S_pending_global = $global_table_view(S_pending)',
            'S_pending_global.STORE[n_value_slot] = DEFINED pvalue_old', '$string_bytes(pvalue_old) = ($ptascii("old"))',
            '$call_descriptors_valid(S_pending)', 'S_done = $drive(S_pending,30000)']
    expected = json.loads((SOURCE_DIR / 'cases.json').read_text())[name]['stdout']
    checks += ['S_done.COMPLETION = NORMAL', '$ccn_output(S_done.EVENTS) = ' + quoted(expected),
        'S_done.DESTRUCTION.OPERATIONS = eps', 'S_done.CLASSCONSTANTCACHE = eps', 'S_done.CLASSCONSTANTINIT = eps',
        'S_done.CLASSCONSTANTHISTORY = S_raw.CLASSCONSTANTHISTORY',
        '$class_constant_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        'S_zero = $drive_steps(S_release,0)', 'S_zero.COMPLETION = BUDGET', 'S_zero[.COMPLETION = NORMAL] = S_release',
        'S_one = $drive_steps(S_release,1)', 'S_one.COMPLETION = BUDGET',
        '$drive(S_zero[.COMPLETION = NORMAL],30000) = S_done', '$drive(S_one[.COMPLETION = NORMAL],30000) = S_done']
    pattern = r'\b(U|S_[A-Za-z0-9_]+|n_[A-Za-z0-9_]+|porigin_[A-Za-z0-9_]+|expression_[A-Za-z0-9_]+|text_member|metadata_member|z|ptask_[A-Za-z0-9_]+|ptask_tail|pclassdesc_[A-Za-z0-9_]+|pclassconstantdesc|pdestructionoperation[A-Za-z0-9_]*|perrorcall|pvalue_[A-Za-z0-9_]+)\b'
    suffix = '_' + name.replace('-', '_')
    return [re.sub(pattern, lambda match: match.group() + suffix, check) for check in checks]


def prepare(out, names):
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    checks = []
    try:
        for name in names:
            source = SOURCE_DIR / (name + '.php')
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
            checks += recipe(checked['fixture'], name, source)
    finally:
        try: adapter.close()
        finally: frontend.close()
    (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    (out / 'protocol.watsup').write_text(PREFIX + SELECTED + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--select', help='comma-separated original names')
    args = parser.parse_args(); names = args.select.split(',') if args.select else NAMES
    assert names and len(set(names)) == len(names) and set(names) <= set(NAMES)
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), SOURCE_DIR / 'cases.json', SOURCE_DIR / 'hashes.json', *(SOURCE_DIR / (name + '.php') for name in names), *modules, *(ROOT / path for path in (
        'spec/semantics/modules.json', 'spec/schema.json', 'frontend/worker.php',
        'tests/semantics/deprecated_class_constant_fetch_protocol.py', 'tests/semantics/deprecated_parameter_default_protocol.py',
        'tests/semantics/deprecated_global_constant_protocol.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py', 'tests/semantics/profile.json',
        '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'selected': names, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        report['premises'] = prepare(out, names)
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in paths}
        report['passed'] = report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after'] and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable']
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    if not report['passed']: print(report.get('stdout', '')[:2000], report.get('stderr', '')[:4000])
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()
