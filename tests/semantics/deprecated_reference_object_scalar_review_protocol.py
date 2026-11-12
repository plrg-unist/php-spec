#!/usr/bin/env python3
"""Check a singleton scalar receiver through protected same-cell retargeting."""
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
SOURCE = Path(__file__).with_name('deprecated_reference_object_scalar_review') / 'retained-bool-retarget.php'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = lambda s: '$base64(' + json.dumps(base64.b64encode(s.encode()).decode()) + ')'
SELECTED = FETCH_SELECTED + r'''
dec $scalar_peer_ready(pstate,nat) : bool
def $scalar_peer_ready(S,0) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask*
  -- if S.RESULT = REFERENCE n_reference
  -- if $call_reference_operand_valid(S,S.RESULT)
  -- if S.STORE[n_reference] = DEFINED (POBJECT n_receiver)
def $scalar_peer_ready(S,1) = true
  -- if S.TODO = (AT porigin_member (EVAL expression_member)) :: (CLASS_CONST_MEMBER expression_class poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: (CLASS_CONST_OBJECT_CAPTURE porigin ptbytes_class z) :: ptask*
  -- if S.DESTRUCTION.OPERATIONS = eps
def $scalar_peer_ready(S,2) = true
  -- if S.CURRENT =/= eps
  -- if $ccn_output(S.EVENTS) = $ptascii("B|C|M|H|D|T|")
def $scalar_peer_ready(S,n) = false -- otherwise
dec $scalar_peer_pause(pstate,nat,nat) : pstate
def $scalar_peer_pause(S,n_phase,n_budget) = S -- if $scalar_peer_ready(S,n_phase)
def $scalar_peer_pause(S,n_phase,n_budget) = $scalar_peer_pause(S_next[.COMPLETION = NORMAL],n_phase,$nabs($(n_budget - 1)))
  -- if ~$scalar_peer_ready(S,n_phase)
  -- if S.COMPLETION = NORMAL /\ $(n_budget > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $scalar_peer_pause(S,n_phase,n_budget) = S -- otherwise
'''


def fields(fixture):
    selected = quoted('Ns245ScalarRetarget\\Selected245')
    other = quoted('Ns245ScalarRetarget\\Other245')
    checks = ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(SOURCE)).decode()) + ')',
        'S_start.COMPLETION = BUDGET',
        'S_raw = $scalar_peer_pause(S_start[.COMPLETION = NORMAL],0,30000)', '$scalar_peer_ready(S_raw,0)',
        'S_raw.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask_tail*',
        'S_raw.ORIGIN = (porigin_site)', 'S_raw.RESULT = REFERENCE n_reference',
        'S_raw.STORE[n_reference] = DEFINED (POBJECT n_receiver)',
        '(HCELL n_reference) <- S_raw.ALLOCATIONS', '(HOBJECT n_receiver) <- S_raw.ALLOCATIONS',
        'S_raw.OBJECTS[n_receiver] = INSTANCE porigin_selected',
        '$objectprops_at(S_raw.OBJECTPROPS,n_receiver) = ([ppropertyslot])',
        'ppropertyslot.STATE = PROP_VALUE (DIRECT (PBOOL true))',
        '$property_slot_descriptor(S_raw,n_receiver,ppropertyslot) = (ppropertydesc)',
        'ppropertydesc.VISIBILITY = PROPERTY_PUBLIC', 'ppropertydesc.SETVISIBILITY = eps',
        'ppropertydesc.TYPE = eps', '~ppropertydesc.STATIC', '~ppropertydesc.READONLY',
        '~$property_hook_source_declared(S_raw,ppropertydesc)',
        '~$property_hook_declared(S_raw,n_receiver,ppropertyslot.NAME)',
        '$object_table_at(S_raw.OBJECTTABLES,n_receiver) = eps',
        '$node_children(S_raw,HOBJECT n_receiver) = eps',
        '$node_children(S_raw,HCELL n_reference) = [HOBJECT n_receiver]',
        'S_raw.CURRENT = eps', 'S_raw.FRAMES = eps', 'S_raw.HELD = eps',
        '$class_at(S_raw.CLASSES,porigin_selected) = (pclassdesc_selected)',
        'pclassdesc_selected.NAME = ' + selected,
        '$class_named(S_raw.CLASSNAMES,$ptlc(' + other + ')) = (porigin_other)',
        '$class_at(S_raw.CLASSES,porigin_other) = (pclassdesc_other)',
        '$class_constant_lookup(S_raw,porigin_selected,$ptascii("B"),|S_raw.CLASSES|) = (pclassconstantdesc)',
        'porigin_decl = pclassconstantdesc.ORIGIN', 'pclassconstantdesc.FOLDED',
        '$compiled_read(S_raw,pclassconstantdesc.INITIALIZER) = (PINT 10)',
        '$heap_owners($heap_graph(S_raw),HCELL n_reference) = 2',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_receiver) = 1',
        '$call_descriptors_valid(S_raw)', '$ccn_output(S_raw.EVENTS) = $ptascii("B|C|")',
        'S_class = $class_constant_selector(S_raw,expression_class,z)',
        'S_class.COMPLETION = NORMAL', 'S_class.RESULT = KNOWN (PSTRING ' + selected + ')',
        'S_class.STORE = S_raw.STORE', 'S_class.OBJECTS = S_raw.OBJECTS',
        'S_class.OBJECTPROPS = S_raw.OBJECTPROPS', 'S_class.ALLOCATIONS = S_raw.ALLOCATIONS',
        '$heap_owners($heap_graph(S_class),HCELL n_reference) = 1',
        '$class_constant_reference_object_graph(S_class,n_receiver,eps)',
        '$class_constant_reference_object_fields(S_class,n_receiver,[ppropertyslot])',
        '$class_constant_reference_object_selector(S_class,S_raw.RESULT) = (pclassdesc_selected)',
        '$class_constant_reference_selector(S_class,S_raw.RESULT) = eps',
        '$class_constant_reference_object_capture_entry(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        '~$class_constant_reference_object_capture_entry(S_class[.HELD = [HCELL n_reference]],S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        '~$class_constant_reference_object_capture_entry(S_class[.BASE = BASE_VALUE (REFERENCE n_reference)],S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        '~$class_constant_reference_object_capture_entry(S_class,S_raw.RESULT,expression_class,expression_member,$(z + 1),ptask_tail*)']
    for value in ['PSTRING $ptascii("x")', 'PFLOAT 0', 'PARRAY 0', 'POBJECT n_receiver']:
        view = 'S_class[.OBJECTPROPS = $objectprops_set(S_class.OBJECTPROPS,n_receiver,[ppropertyslot[.STATE = PROP_VALUE (DIRECT (' + value + '))]])]'
        checks += ['$class_constant_reference_object_selector(' + view + ',S_raw.RESULT) = eps']
    for state in ['PROP_INITIAL', 'PROP_UNSET', 'PROP_VALUE (ALIAS n_reference)']:
        view = 'S_class[.OBJECTPROPS = $objectprops_set(S_class.OBJECTPROPS,n_receiver,[ppropertyslot[.STATE = ' + state + ']])]'
        checks += ['$class_constant_reference_object_selector(' + view + ',S_raw.RESULT) = eps']
    for change in ['.RESULT = KNOWN PNULL',
                   '.ALLOCATIONS = $native_remove_one(S_class.ALLOCATIONS,HCELL n_reference)',
                   '.ALLOCATIONS = $native_remove_one(S_class.ALLOCATIONS,HOBJECT n_receiver)',
                   '.REFCELLS = eps', '.OBJECTTABLES = [{OBJECT n_receiver,TABLE 0}]']:
        checks += ['$class_constant_reference_object_selector(S_class[' + change + '],S_raw.RESULT) = eps']
    checks += ['S_neutral = $class_constant_class_forward(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        'ptask_marker = CLASS_CONST_OBJECT_CAPTURE porigin_site ' + selected + ' z',
        'ptask_member = $at_task($origin_child((porigin_site),[PCFIELD 1]),EVAL expression_member)',
        'S_neutral.TODO = ptask_member :: (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ' + selected + ')) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING ' + selected + ')) z) :: ptask_marker :: ptask_tail*',
        'S_neutral.RESULT = KNOWN PNULL', 'S_neutral.BASE = BASE_VALUE (KNOWN PNULL)',
        '$task_nodes(ptask_marker) = eps', '$machine_base_roots(S_neutral) = eps',
        '~$class_constant_notice_protected(S_neutral,porigin_decl)',
        '$eager_slots(S_raw,S_neutral) = [HCELL n_reference]',
        '$eager_operation_source(S_raw,CLASS_CONST_CLASS expression_class expression_member z) = ptask_marker',
        'S_step = $drive_steps(S_raw,1)', 'S_step.COMPLETION = BUDGET', 'S_release = S_step[.COMPLETION = NORMAL]',
        'S_release.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
        'pdestructionoperation.SOURCE = ptask_marker', 'pdestructionoperation.VALUE = KNOWN PNULL',
        'pdestructionoperation.BASE = BASE_VALUE (KNOWN PNULL)', 'pdestructionoperation.PENDING = eps',
        '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
        '$eager_operation_source_guard(S_release,pdestructionoperation)', '$call_descriptors_valid(S_release)',
        'S_drained = $scalar_peer_pause(S_release,1,30000)', '$scalar_peer_ready(S_drained,1)',
        'S_drained.TODO = S_neutral.TODO', '$ccn_output(S_drained.EVENTS) = $ptascii("B|C|")',
        '$heap_owners($heap_graph(S_drained),HCELL n_reference) = 1',
        '$heap_owners($heap_graph(S_drained),HOBJECT n_receiver) = 1',
        '$call_descriptors_valid(S_drained)',
        'S_warn = $ccn_pause(S_drained,0,30000)', '$ccn_ready(S_warn,0)',
        '$ccn_output(S_warn.EVENTS) = $ptascii("B|C|M|")',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT porigin_decl ' + selected + ' $ptascii("B") z',
        '$task_nodes(perrorcall.RESUME) = eps', '$class_constant_notice_protected(S_warn,porigin_decl)',
        '$error_call_valid(S_warn,perrorcall)', '$call_descriptors_valid(S_warn)',
        '$heap_owners($heap_graph(S_warn),HCELL n_reference) = 1',
        '$heap_owners($heap_graph(S_warn),HOBJECT n_receiver) = 1',
        'S_inner = $scalar_peer_pause(S_warn,2,30000)', '$scalar_peer_ready(S_inner,2)',
        'S_inner.CURRENT = (pcallcontext)', 'pcallcontext.TARGET = METHOD_TARGET n_receiver porigin_destructor',
        '$class_constant_notice_protected(S_inner,porigin_decl)',
        '(HOBJECT n_receiver) <- S_inner.ALLOCATIONS',
        '$objectprops_at(S_inner.OBJECTPROPS,n_receiver) = ([ppropertyslot])',
        '$node_children(S_inner,HOBJECT n_receiver) = eps', '$call_descriptors_valid(S_inner)',
        'S_resume = $ccn_pause(S_inner,1,30000)', '$ccn_ready(S_resume,1)',
        '$ccn_output(S_resume.EVENTS) = $ptascii("B|C|M|H|D|T|10|H2|")',
        '~((HOBJECT n_receiver) <- S_resume.ALLOCATIONS)',
        '$objectprops_at(S_resume.OBJECTPROPS,n_receiver) = eps',
        '$call_reference_operand_valid(S_resume,REFERENCE n_reference)',
        'S_resume.STORE[n_reference] = DEFINED pvalue_other', '$string_bytes(pvalue_other) = (' + other + ')',
        '$heap_owners($heap_graph(S_resume),HCELL n_reference) = 1',
        '$class_constant_notice_valid(S_resume,porigin_decl,' + selected + ',$ptascii("B"),z)',
        '~$class_constant_notice_valid(S_resume,porigin_decl,' + other + ',$ptascii("B"),z)',
        '~$class_constant_notice_valid(S_resume,porigin_decl,' + selected + ',$ptascii("B"),$(z + 1))',
        '$class_constant_reference_object_selector(S_resume[.RESULT = KNOWN (PSTRING ' + selected + ')],REFERENCE n_reference) = eps',
        '$class_constant_reference_selector(S_resume[.RESULT = KNOWN (PSTRING ' + other + ')],REFERENCE n_reference) = (pclassdesc_other)',
        '$call_descriptors_valid(S_resume)',
        'S_value_step = $drive_steps(S_resume,1)', 'S_value_step.COMPLETION = BUDGET',
        'S_value = S_value_step[.COMPLETION = NORMAL]', 'S_value.RESULT = KNOWN (PINT 10)',
        '~$class_constant_notice_protected(S_value,porigin_decl)',
        'S_done = $drive(S_value,30000)', 'S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = $ptascii("B|C|M|H|D|T|10|H2|R|10|W|80|Z|")',
        'S_done.DESTRUCTION.OPERATIONS = eps', 'S_done.CLASSCONSTANTCACHE = eps',
        'S_done.CLASSCONSTANTHISTORY = S_raw.CLASSCONSTANTHISTORY',
        '$class_constant_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        'S_zero = $drive_steps(S_inner,0)', 'S_zero.COMPLETION = BUDGET', 'S_zero[.COMPLETION = NORMAL] = S_inner',
        'S_one = $drive_steps(S_inner,1)', 'S_one.COMPLETION = BUDGET',
        '$drive(S_zero[.COMPLETION = NORMAL],30000) = S_done', '$drive(S_one[.COMPLETION = NORMAL],30000) = S_done']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), SOURCE, *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
        'tests/semantics/deprecated_class_constant_fetch_protocol.py', 'tests/semantics/deprecated_parameter_default_protocol.py',
        'tests/semantics/deprecated_global_constant_protocol.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py', 'tests/semantics/profile.json',
        '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
        'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(SOURCE.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = fields(checked['fixture']); report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out / 'protocol.watsup').write_text(PREFIX + SELECTED + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after']
            and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    if not report['passed']: print(report.get('stdout', '')[:2000], report.get('stderr', '')[:4000])
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()
