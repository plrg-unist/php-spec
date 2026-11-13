#!/usr/bin/env python3
"""Check descendant guards and nested storage after a supplied exception."""
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
SOURCE = Path(__file__).with_name('deprecated_reference_object_graph_review') / 'deep-child-throw.php'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = lambda s: '$base64(' + json.dumps(base64.b64encode(s.encode()).decode()) + ')'
SELECTED = FETCH_SELECTED + r'''
dec $reference_graph_peer_ready(pstate,nat) : bool
def $reference_graph_peer_ready(S,0) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask*
  -- if S.RESULT = REFERENCE n_reference
  -- if $call_reference_operand_valid(S,S.RESULT)
def $reference_graph_peer_ready(S,1) = true
  -- if S.CURRENT =/= eps
  -- if $ccn_output(S.EVENTS) = $ptascii("C|D|I|G|")
def $reference_graph_peer_ready(S,2) = true
  -- if S.CURRENT =/= eps
  -- if $ccn_output(S.EVENTS) = $ptascii("C|D|I|G|R|")
def $reference_graph_peer_ready(S,3) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask*
  -- if pdestructionoperation.PENDING = (n_exception)
  -- if pdestructionoperation.SOURCE = CLASS_CONST_OBJECT_CAPTURE porigin ptbytes_class z
def $reference_graph_peer_ready(S,n) = false -- otherwise
dec $reference_graph_peer_pause(pstate,nat,nat) : pstate
def $reference_graph_peer_pause(S,n_phase,n_budget) = S -- if $reference_graph_peer_ready(S,n_phase)
def $reference_graph_peer_pause(S,n_phase,n_budget) = $reference_graph_peer_pause(S_next[.COMPLETION = NORMAL],n_phase,$nabs($(n_budget - 1)))
  -- if ~$reference_graph_peer_ready(S,n_phase)
  -- if S.COMPLETION = NORMAL /\ $(n_budget > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $reference_graph_peer_pause(S,n_phase,n_budget) = S -- otherwise
dec $reference_graph_peer_classes(pclassdesc*,porigin,pclassdesc) : pclassdesc*
def $reference_graph_peer_classes(eps,porigin,pclassdesc_replacement) = eps
def $reference_graph_peer_classes(pclassdesc :: pclassdesc_tail*,porigin,pclassdesc_replacement) = pclassdesc_replacement :: pclassdesc_tail*
  -- if pclassdesc.ORIGIN = porigin
def $reference_graph_peer_classes(pclassdesc :: pclassdesc_tail*,porigin,pclassdesc_replacement) = pclassdesc :: $reference_graph_peer_classes(pclassdesc_tail*,porigin,pclassdesc_replacement)
  -- if pclassdesc.ORIGIN =/= porigin
'''


def fields(fixture):
    root = quoted('Ns244DeepThrow\\Root244')
    base = quoted('Ns244DeepThrow\\Base244')
    checks = ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(SOURCE)).decode()) + ')',
        'S_raw = $reference_graph_peer_pause(S_start[.COMPLETION = NORMAL],0,30000)',
        '$reference_graph_peer_ready(S_raw,0)',
        'S_raw.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask_tail*',
        'S_raw.ORIGIN = (porigin_site)', 'S_raw.RESULT = REFERENCE n_reference',
        'S_raw.CURRENT = eps', 'S_raw.FRAMES = eps', 'S_raw.HELD = eps',
        'S_raw.STORE[n_reference] = DEFINED (POBJECT n_receiver)',
        '(HCELL n_reference) <- S_raw.ALLOCATIONS', '(HOBJECT n_receiver) <- S_raw.ALLOCATIONS',
        'S_raw.OBJECTS[n_receiver] = INSTANCE porigin_root',
        '$class_at(S_raw.CLASSES,porigin_root) = (pclassdesc_root)', 'pclassdesc_root.NAME = ' + root,
        '$objectprops_at(S_raw.OBJECTPROPS,n_receiver) = ([ppropertyslot_first,ppropertyslot_padding,ppropertyslot_tail])',
        'ppropertyslot_first.STATE = PROP_VALUE (DIRECT (POBJECT n_middle))',
        'ppropertyslot_padding.STATE = PROP_VALUE (DIRECT (PBOOL false))',
        'ppropertyslot_tail.STATE = PROP_VALUE (DIRECT (POBJECT n_last))',
        '$(n_last < n_middle)', '(HOBJECT n_middle) <- S_raw.ALLOCATIONS',
        'S_raw.OBJECTS[n_middle] = INSTANCE porigin_middle',
        '$class_at(S_raw.CLASSES,porigin_middle) = (pclassdesc_middle)',
        '$objectprops_at(S_raw.OBJECTPROPS,n_middle) = ([ppropertyslot_deep])',
        'ppropertyslot_deep.STATE = PROP_VALUE (DIRECT (POBJECT n_deep))',
        '(HOBJECT n_deep) <- S_raw.ALLOCATIONS', 'S_raw.OBJECTS[n_deep] = INSTANCE porigin_deep',
        '$class_at(S_raw.CLASSES,porigin_deep) = (pclassdesc_deep)',
        '$objectprops_at(S_raw.OBJECTPROPS,n_deep) = (eps)', '$objectprops_at(S_raw.OBJECTPROPS,n_last) = (eps)',
        '$property_slot_descriptor(S_raw,n_receiver,ppropertyslot_first) = (ppropertydesc_first)',
        '$property_slot_descriptor(S_raw,n_receiver,ppropertyslot_tail) = (ppropertydesc_tail)',
        '$property_slot_descriptor(S_raw,n_middle,ppropertyslot_deep) = (ppropertydesc_deep)',
        'pclassdesc_root.PROPERTIES = [ppropertydesc_tail]',
        'pclassdesc_middle.PROPERTIES = [ppropertydesc_deep]',
        '$property_declaring_class(S_raw.CLASSES,ppropertydesc_first.ORIGIN) = (porigin_base)',
        '$class_at(S_raw.CLASSES,porigin_base) = (pclassdesc_base)', 'pclassdesc_base.NAME = ' + base,
        '$node_children(S_raw,HCELL n_reference) = [HOBJECT n_receiver]',
        '$node_children(S_raw,HOBJECT n_receiver) = [HOBJECT n_middle,HOBJECT n_last]',
        '$node_children(S_raw,HOBJECT n_middle) = [HOBJECT n_deep]',
        '$heap_owners($heap_graph(S_raw),HCELL n_reference) = 1',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_receiver) = 1',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_middle) = 1',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_deep) = 1',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_last) = 1',
        '$call_descriptors_valid(S_raw)', '$ccn_output(S_raw.EVENTS) = $ptascii("C|")',
        'S_global = $global_table_view(S_raw)',
        '$lookup(S_global.ENV,$ptascii("exception244peer")) = (n_exception_slot)',
        'S_global.STORE[n_exception_slot] = DEFINED (POBJECT n_exception)',
        '$lookup(S_global.ENV,$ptascii("value244peer")) = (n_value_slot)',
        'S_class = $class_constant_selector(S_raw,expression_class,z)',
        'S_class.COMPLETION = NORMAL', 'S_class.RESULT = KNOWN (PSTRING ' + root + ')',
        'S_class.STORE = S_raw.STORE', 'S_class.OBJECTS = S_raw.OBJECTS',
        'S_class.OBJECTPROPS = S_raw.OBJECTPROPS', 'S_class.ALLOCATIONS = S_raw.ALLOCATIONS',
        '$heap_owners($heap_graph(S_class),HCELL n_reference) = 0',
        '$class_constant_reference_object_graph(S_class,n_receiver,eps)',
        '$class_constant_reference_object_graph(S_class,n_middle,[n_receiver])',
        '~$class_constant_reference_object_fields(S_class,n_receiver,[ppropertyslot_first,ppropertyslot_padding,ppropertyslot_tail])',
        '~$class_constant_reference_object_field_value(S_class,n_receiver,POBJECT n_middle)',
        '$class_constant_reference_object_selector(S_class,S_raw.RESULT) = (pclassdesc_root)',
        '$class_constant_reference_object_capture_entry(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)']
    for state in ['PROP_INITIAL', 'PROP_UNSET', 'PROP_VALUE (ALIAS n_reference)',
                  'PROP_VALUE (DIRECT (PSTRING $ptascii("x")))',
                  'PROP_VALUE (DIRECT (PARRAY 0))', 'PROP_VALUE (DIRECT (POBJECT n_exception))']:
        view = 'S_class[.OBJECTPROPS = $objectprops_set(S_class.OBJECTPROPS,n_middle,[ppropertyslot_deep[.STATE = ' + state + ']])]'
        checks += ['~$class_constant_reference_object_graph(' + view + ',n_receiver,eps)',
                   '$class_constant_reference_object_selector(' + view + ',S_raw.RESULT) = eps']
    for node in ['n_middle', 'n_deep']:
        for change in ['.ALLOCATIONS = $native_remove_one(S_class.ALLOCATIONS,HOBJECT ' + node + ')',
                       '.OBJECTTABLES = [{OBJECT ' + node + ',TABLE 0}]']:
            checks += ['~$class_constant_reference_object_graph(S_class[' + change + '],n_receiver,eps)',
                       '$class_constant_reference_object_selector(S_class[' + change + '],S_raw.RESULT) = eps']
    for origin, desc in [('porigin_middle', 'pclassdesc_middle'), ('porigin_deep', 'pclassdesc_deep')]:
        for change in ['.NAME = $ptascii("Unregistered244")', '.KIND = "interface"']:
            view = 'S_class[.CLASSES = $reference_graph_peer_classes(S_class.CLASSES,' + origin + ',' + desc + '[' + change + '])]'
            checks += ['~$class_constant_reference_object_graph(' + view + ',n_receiver,eps)',
                       '$class_constant_reference_object_selector(' + view + ',S_raw.RESULT) = eps']
    for policy in ['.SETVISIBILITY = (PROPERTY_PRIVATE)',
                   '.STATIC = true', '.READONLY = true']:
        view = 'S_class[.CLASSES = $reference_graph_peer_classes(S_class.CLASSES,porigin_middle,pclassdesc_middle[.PROPERTIES = [ppropertydesc_deep[' + policy + ']]])]'
        checks += ['~$class_constant_reference_object_graph(' + view + ',n_receiver,eps)',
                   '$class_constant_reference_object_selector(' + view + ',S_raw.RESULT) = eps']
    checks += ['S_class.SOURCES = [pcunit]', 'ppropertydesc_deep.ORIGIN = PORIGIN n_unit pcpath_property',
        'pcunit.ID = n_unit', 'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3, PCINDEX 0]',
        '$origin_node(S_class.SOURCES,PORIGIN n_unit pcpath_group) = (NStmtProperty phpType14_attrs phpType24_flags phpType18_type phpType56_props (SEQUENCE eps) metadata_prop)',
        'pcnode_source_hook = NStmtProperty phpType14_attrs phpType24_flags phpType18_type phpType56_props (SEQUENCE ([NPropertyHook (SEQUENCE eps) (INTEGER 8) (BOOLEAN false) (NIdentifier (BYTES "Z2V0") eps) (SEQUENCE eps) (NScalarInt (INTEGER 1) eps) eps])) metadata_prop',
        'S_source_hook = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group pcnode_source_hook) :: pcunit.OCCURRENCES]]]',
        '$property_hook_source_declared(S_source_hook,ppropertydesc_deep)',
        '~$property_hook_declared(S_source_hook,n_middle,ppropertyslot_deep.NAME)',
        '~$class_constant_reference_object_graph(S_source_hook,n_receiver,eps)',
        '$class_constant_reference_object_selector(S_source_hook,S_raw.RESULT) = eps',
        'pcnode_effective_hook = NStmtProperty phpType14_attrs phpType24_flags phpType18_type phpType56_props (SEQUENCE ([NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) (NIdentifier (BYTES "Z2V0") eps) (SEQUENCE eps) (NScalarInt (INTEGER 1) eps) eps])) metadata_prop',
        'S_effective_hook = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group pcnode_effective_hook) :: pcunit.OCCURRENCES]]]',
        '$property_hook_source_declared(S_effective_hook,ppropertydesc_deep)',
        '$property_hook_declared(S_effective_hook,n_middle,ppropertyslot_deep.NAME)',
        '~$class_constant_reference_object_graph(S_effective_hook,n_receiver,eps)',
        '$class_constant_reference_object_selector(S_effective_hook,S_raw.RESULT) = eps',
        'S_neutral = $class_constant_class_forward(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        'ptask_marker = CLASS_CONST_OBJECT_CAPTURE porigin_site ' + root + ' z',
        'ptask_member = $at_task($origin_child((porigin_site),[PCFIELD 1]),EVAL expression_member)',
        'S_neutral.TODO = ptask_member :: (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ' + root + ')) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING ' + root + ')) z) :: ptask_marker :: ptask_tail*',
        'S_neutral.RESULT = KNOWN PNULL', 'S_neutral.BASE = BASE_VALUE (KNOWN PNULL)',
        '$task_nodes(ptask_marker) = eps', '$machine_base_roots(S_neutral) = eps',
        '$class_constant_lookup(S_class,porigin_root,$ptascii("A"),|S_class.CLASSES|) = (pclassconstantdesc)',
        '~$class_constant_notice_protected(S_neutral,pclassconstantdesc.ORIGIN)',
        '$eager_slots(S_raw,S_neutral) = [HCELL n_reference]',
        '$eager_operation_source(S_raw,CLASS_CONST_CLASS expression_class expression_member z) = ptask_marker',
        'S_step = $drive_steps(S_raw,1)', 'S_step.COMPLETION = BUDGET', 'S_release = S_step[.COMPLETION = NORMAL]',
        'S_release.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
        'pdestructionoperation.SOURCE = ptask_marker', 'pdestructionoperation.VALUE = KNOWN PNULL',
        'pdestructionoperation.BASE = BASE_VALUE (KNOWN PNULL)', 'pdestructionoperation.COMPLETION = NORMAL',
        'pdestructionoperation.PENDING = eps', '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
        '$eager_operation_source_guard(S_release,pdestructionoperation)',
        'S_deep = $reference_graph_peer_pause(S_release,1,30000)', '$reference_graph_peer_ready(S_deep,1)',
        'S_deep.CURRENT = (pcallcontext_deep)', 'pcallcontext_deep.TARGET = METHOD_TARGET n_deep porigin_deep_destructor',
        '$instance_storage_for(S_deep,n_receiver) = (pinstancestorage_root)', 'pinstancestorage_root.NEXT = 1',
        '$instance_storage_for(S_deep,n_middle) = (pinstancestorage_middle)', 'pinstancestorage_middle.NEXT = 1',
        '$objectprops_at(S_deep.OBJECTPROPS,n_receiver) = ([ppropertyslot_first[.STATE = PROP_UNSET],ppropertyslot_padding,ppropertyslot_tail])',
        '$objectprops_at(S_deep.OBJECTPROPS,n_middle) = ([ppropertyslot_deep[.STATE = PROP_UNSET]])',
        '(HOBJECT n_receiver) <- S_deep.ALLOCATIONS', '(HOBJECT n_middle) <- S_deep.ALLOCATIONS',
        '(HOBJECT n_deep) <- S_deep.ALLOCATIONS', '(HOBJECT n_last) <- S_deep.ALLOCATIONS',
        '$($heap_owners($heap_graph(S_deep),HOBJECT n_deep) > 0)',
        '$heap_owners($heap_graph(S_deep),HOBJECT n_last) = 1',
        '$eager_operation_source_guard(S_deep,pdestructionoperation)', '$call_descriptors_valid(S_deep)',
        '$ccn_output(S_deep.EVENTS) = $ptascii("C|D|I|G|")',
        'S_last = $reference_graph_peer_pause(S_deep,2,30000)', '$reference_graph_peer_ready(S_last,2)',
        'S_last.CURRENT = (pcallcontext_last)', 'pcallcontext_last.TARGET = METHOD_TARGET n_last porigin_last_destructor',
        'pdestructionoperation_pending = pdestructionoperation[.PENDING = (n_exception)]',
        'S_last.DESTRUCTION.OPERATIONS = [pdestructionoperation_pending]',
        'S_last.DESTRUCTION.CALLS = [pdestructorcall_last]', 'pdestructorcall_last.OBJECT = n_last',
        'pdestructorcall_last.PENDING = (n_exception)', 'pdestructorcall_last.OPERATION = (pdestructionoperation_pending)',
        '$instance_storage_for(S_last,n_receiver) = (pinstancestorage_last)', 'pinstancestorage_last.NEXT = 3',
        '$objectprops_at(S_last.OBJECTPROPS,n_receiver) = ([ppropertyslot_first[.STATE = PROP_UNSET],ppropertyslot_padding[.STATE = PROP_UNSET],ppropertyslot_tail[.STATE = PROP_UNSET]])',
        '(HOBJECT n_receiver) <- S_last.ALLOCATIONS', '~((HOBJECT n_middle) <- S_last.ALLOCATIONS)',
        '~((HOBJECT n_deep) <- S_last.ALLOCATIONS)', '(HOBJECT n_last) <- S_last.ALLOCATIONS',
        '$instance_storage_for(S_last,n_middle) = eps',
        '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending) = [HOBJECT n_exception]',
        '$eager_operation_source_guard(S_last,pdestructionoperation_pending)',
        '$destructor_operation_live(S_last,pdestructionoperation_pending)',
        '$ccn_output(S_last.EVENTS) = $ptascii("C|D|I|G|R|")', '$call_descriptors_valid(S_last)',
        'S_pending = $reference_graph_peer_pause(S_last,3,30000)', '$reference_graph_peer_ready(S_pending,3)',
        'S_pending.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending) :: S_neutral.TODO',
        '~((HCELL n_reference) <- S_pending.ALLOCATIONS)', '~((HOBJECT n_receiver) <- S_pending.ALLOCATIONS)',
        '~((HOBJECT n_middle) <- S_pending.ALLOCATIONS)', '~((HOBJECT n_deep) <- S_pending.ALLOCATIONS)',
        '~((HOBJECT n_last) <- S_pending.ALLOCATIONS)',
        '$eager_operation_source_guard(S_pending,pdestructionoperation_pending)',
        '~$class_constant_notice_protected(S_pending,pclassconstantdesc.ORIGIN)',
        '$ccn_output(S_pending.EVENTS) = $ptascii("C|D|I|G|R|")',
        'S_pending_global = $global_table_view(S_pending)',
        'S_pending_global.STORE[n_value_slot] = DEFINED (PINT 71)', '$call_descriptors_valid(S_pending)',
        'S_done = $drive(S_pending,30000)', 'S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = $ptascii("C|D|I|G|R|S|71|Z|")',
        'S_done.DESTRUCTION.OPERATIONS = eps', 'S_done.CLASSCONSTANTCACHE = eps',
        'S_done.CLASSCONSTANTHISTORY = S_raw.CLASSCONSTANTHISTORY',
        '$class_constant_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        'S_zero = $drive_steps(S_deep,0)', 'S_zero.COMPLETION = BUDGET', 'S_zero[.COMPLETION = NORMAL] = S_deep',
        'S_one = $drive_steps(S_deep,1)', 'S_one.COMPLETION = BUDGET',
        '$drive(S_zero[.COMPLETION = NORMAL],30000) = S_done', '$drive(S_one[.COMPLETION = NORMAL],30000) = S_done']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), SOURCE, *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json', 'spec/schema.json', 'frontend/worker.php',
        'tests/semantics/deprecated_class_constant_fetch_protocol.py',
        'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py',
        'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py',
        'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
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
