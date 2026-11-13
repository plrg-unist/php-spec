#!/usr/bin/env python3
"""Check an initialized exact-int singleton and ordinary field retirement."""
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
SOURCE = Path(__file__).with_name('deprecated_reference_object_typed_int') / 'literal-singleton.php'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
SELECTED = FETCH_SELECTED + r'''
dec $typed_int_ready(pstate,nat,nat) : bool
def $typed_int_ready(S,0,n_object) = true
  -- if S.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask*
  -- if S.RESULT = REFERENCE n_reference
def $typed_int_ready(S,1,n_object) = true
  -- if $ccn_output(S.EVENTS) = $ptascii("B|C|D|T|")
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n_object)
def $typed_int_ready(S,2,n_object) = true
  -- if $instance_storage_for(S,n_object) = (pinstancestorage)
  -- if pinstancestorage.NEXT = 1
def $typed_int_ready(S,3,n_object) = true
  -- if S.TODO = (CLASS_CONST_MEMBER expression_class poperand z) :: (CLASS_CONST_CAPTURE porigin poperand z) :: (CLASS_CONST_OBJECT_CAPTURE porigin ptbytes_class z) :: ptask*
def $typed_int_ready(S,n_phase,n_object) = false -- otherwise
dec $typed_int_pause(pstate,nat,nat,nat) : pstate
def $typed_int_pause(S,n_phase,n_object,n_budget) = S -- if $typed_int_ready(S,n_phase,n_object)
def $typed_int_pause(S,n_phase,n_object,n_budget) = $typed_int_pause(S_next[.COMPLETION = NORMAL],n_phase,n_object,$nabs($(n_budget - 1)))
  -- if ~$typed_int_ready(S,n_phase,n_object)
  -- if S.COMPLETION = NORMAL /\ $(n_budget > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $typed_int_pause(S,n_phase,n_object,n_budget) = S -- otherwise
'''


def fields(fixture):
    child = '$base64(' + json.dumps(base64.b64encode(b'Ns250Int\\Selected250').decode()) + ')'
    checks = ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(SOURCE)).decode()) + ')',
        'S_raw = $typed_int_pause(S_start[.COMPLETION = NORMAL],0,0,30000)', '$typed_int_ready(S_raw,0,0)',
        'S_raw.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask_tail*',
        'S_raw.ORIGIN = (porigin_site)', 'S_raw.RESULT = REFERENCE n_reference',
        '$call_reference_operand_valid(S_raw,S_raw.RESULT)',
        'S_raw.STORE[n_reference] = DEFINED (POBJECT n_object)',
        '(HCELL n_reference) <- S_raw.ALLOCATIONS', '(HOBJECT n_object) <- S_raw.ALLOCATIONS',
        'S_raw.CURRENT = eps', 'S_raw.FRAMES = eps', 'S_raw.HELD = eps',
        'S_raw.OBJECTS[n_object] = INSTANCE porigin_child',
        '$class_at(S_raw.CLASSES,porigin_child) = (pclassdesc_child)', 'pclassdesc_child.NAME = ' + child,
        '$objectprops_at(S_raw.OBJECTPROPS,n_object) = ([ppropertyslot_tag])',
        'ppropertyslot_tag.STATE = PROP_VALUE (DIRECT pvalue_tag)',
        'pvalue_tag = PINT z_tag', 'z_tag = 17', '$value_nodes(pvalue_tag) = eps',
        '$property_slot_descriptor(S_raw,n_object,ppropertyslot_tag) = (ppropertydesc_tag)',
        'pclassdesc_child.PROPERTIES = [ppropertydesc_tag]',
        'ppropertydesc_tag.TYPE = [PTBRANCH ([PTBUILTIN "int"])]', '$typed_exact(ppropertydesc_tag.TYPE,pvalue_tag)',
        'ppropertydesc_tag.DEFAULT = PROP_UNINITIALIZED',
        'ppropertydesc_tag.VISIBILITY = PROPERTY_PUBLIC', 'ppropertydesc_tag.SETVISIBILITY = eps',
        '~ppropertydesc_tag.STATIC', '~ppropertydesc_tag.READONLY',
        '~$property_hook_source_declared(S_raw,ppropertydesc_tag)',
        '~$property_hook_declared(S_raw,n_object,ppropertyslot_tag.NAME)',
        'S_raw.PROPREFS = eps', '$property_slot_release_job(S_raw,n_object,ppropertyslot_tag) = eps',
        '$object_table_at(S_raw.OBJECTTABLES,n_object) = eps',
        '$node_children(S_raw,HCELL n_reference) = [HOBJECT n_object]', '$node_children(S_raw,HOBJECT n_object) = eps',
        '$heap_owners($heap_graph(S_raw),HCELL n_reference) = 1', '$heap_owners($heap_graph(S_raw),HOBJECT n_object) = 1',
        '$machine_base_roots(S_raw) = eps', '$call_descriptors_valid(S_raw)', '$ccn_output(S_raw.EVENTS) = $ptascii("B|C|")',
        'S_class = $class_constant_selector(S_raw,expression_class,z)', 'S_class.COMPLETION = NORMAL',
        'S_class.RESULT = KNOWN (PSTRING ' + child + ')', 'S_class.STORE = S_raw.STORE',
        'S_class.OBJECTPROPS = S_raw.OBJECTPROPS', 'S_class.STRINGDATA = S_raw.STRINGDATA',
        '$class_constant_reference_object_field_type(S_class,ppropertydesc_tag,ppropertyslot_tag)',
        '$class_constant_reference_object_flat_field_type(S_class,n_object,ppropertydesc_tag,ppropertyslot_tag)',
        '$class_constant_reference_object_graph_value(S_class,pvalue_tag,[n_object])',
        '$class_constant_reference_object_scalar_value(pvalue_tag)',
        '$class_constant_reference_object_field_value(S_class,n_object,pvalue_tag)',
        '$class_constant_reference_object_graph(S_class,n_object,eps)',
        '$class_constant_reference_object_fields(S_class,n_object,[ppropertyslot_tag])',
        '$class_constant_reference_object_selector(S_class,S_raw.RESULT) = (pclassdesc_child)',
        '$class_constant_reference_object_capture_entry(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)']
    for type_ in ['[PTBRANCH ([PTBUILTIN "float"])]', '[PTBRANCH ([PTBUILTIN "string"])]',
                  '[PTBRANCH ([PTBUILTIN "Int"])]',
                  '[PTBRANCH ([PTBUILTIN "int",PTBUILTIN "string"])]']:
        desc = 'ppropertydesc_tag[.TYPE = ' + type_ + ']'
        state = 'S_class[.CLASSES = $trait_class_set(S_class.CLASSES,pclassdesc_child[.PROPERTIES = [' + desc + ']])]'
        checks += ['~$class_constant_reference_object_field_type(S_class,' + desc + ',ppropertyslot_tag)',
                   '~$class_constant_reference_object_flat_field_type(S_class,n_object,' + desc + ',ppropertyslot_tag)',
                   '~$class_constant_reference_object_graph(' + state + ',n_object,eps)',
                   '$class_constant_reference_object_selector(' + state + ',S_raw.RESULT) = eps']
    for slot_state in ['PROP_INITIAL', 'PROP_UNSET', 'PROP_VALUE (ALIAS n_reference)',
                       'PROP_VALUE (DIRECT PNULL)', 'PROP_VALUE (DIRECT (PBOOL false))',
                       'PROP_VALUE (DIRECT (PFLOAT 4609434218613702656))', 'PROP_VALUE (DIRECT (PSTRING_CARRIER INTERNED_STRING $ptascii("tag")))',
                       'PROP_VALUE (DIRECT (POBJECT n_object))', 'PROP_VALUE (DIRECT (PARRAY 0))',
                       'PROP_VALUE (DIRECT (PSTRING $ptascii("tag")))',
                       'PROP_VALUE (DIRECT (PSTRING_CARRIER (REQUEST_STRING (|S_class.STRINGDATA|)) $ptascii("tag")))',
                       'PROP_VALUE (DIRECT (PSTRING_CARRIER INTERNED_STRING $base64("dGEAZw==")))']:
        slot = 'ppropertyslot_tag[.STATE = ' + slot_state + ']'
        state = 'S_class[.OBJECTPROPS = $objectprops_set(S_class.OBJECTPROPS,n_object,[' + slot + '])]'
        checks += ['~$class_constant_reference_object_field_type(S_class,ppropertydesc_tag,' + slot + ')',
                   '~$class_constant_reference_object_flat_field_type(S_class,n_object,ppropertydesc_tag,' + slot + ')',
                   '~$class_constant_reference_object_graph(' + state + ',n_object,eps)',
                   '$class_constant_reference_object_selector(' + state + ',S_raw.RESULT) = eps']
    for policy in ['.SETVISIBILITY = (PROPERTY_PRIVATE)', '.STATIC = true']:
        state = 'S_class[.CLASSES = $trait_class_set(S_class.CLASSES,pclassdesc_child[.PROPERTIES = [ppropertydesc_tag[' + policy + ']]])]'
        checks += ['~$class_constant_reference_object_graph(' + state + ',n_object,eps)',
                   '$class_constant_reference_object_selector(' + state + ',S_raw.RESULT) = eps']
    checks += ['S_untyped = S_class[.CLASSES = $trait_class_set(S_class.CLASSES,pclassdesc_child[.PROPERTIES = [ppropertydesc_tag[.TYPE = eps]]])]',
        '$class_constant_reference_object_graph(S_untyped,n_object,eps)',
        '$class_constant_reference_object_selector(S_untyped,S_raw.RESULT) = (pclassdesc_child[.PROPERTIES = [ppropertydesc_tag[.TYPE = eps]]])',
        'pvalue_forged = PSTRING_CARRIER (REQUEST_STRING (|S_class.STRINGDATA|)) $ptascii("tag")',
        '~$class_constant_reference_object_field_value(S_class,n_object,pvalue_forged)',
        'S_neutral = $class_constant_class_forward(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        'ptask_marker = CLASS_CONST_OBJECT_CAPTURE porigin_site ' + child + ' z',
        'ptask_member = $at_task($origin_child((porigin_site),[PCFIELD 1]),EVAL expression_member)',
        'S_neutral.TODO = ptask_member :: (CLASS_CONST_MEMBER expression_class (KNOWN (PSTRING ' + child + ')) z) :: (CLASS_CONST_CAPTURE porigin_site (KNOWN (PSTRING ' + child + ')) z) :: ptask_marker :: ptask_tail*',
        'S_neutral.RESULT = KNOWN PNULL', 'S_neutral.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_neutral.PROPREFS = eps', 'S_neutral.STRINGDATA = S_raw.STRINGDATA',
        '$task_nodes(ptask_marker) = eps', '$machine_base_roots(S_neutral) = eps',
        '$eager_operation_source(S_raw,CLASS_CONST_CLASS expression_class expression_member z) = ptask_marker',
        'S_step = $drive_steps(S_raw,1)', 'S_step.COMPLETION = BUDGET', 'S_release = S_step[.COMPLETION = NORMAL]',
        'S_release.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
        'pdestructionoperation.SOURCE = ptask_marker', 'pdestructionoperation.VALUE = KNOWN PNULL',
        'pdestructionoperation.BASE = BASE_VALUE (KNOWN PNULL)', 'pdestructionoperation.PENDING = eps',
        '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
        '$eager_operation_source_guard(S_release,pdestructionoperation)', '$call_descriptors_valid(S_release)',
        'S_dtor = $typed_int_pause(S_release,1,n_object,30000)', '$typed_int_ready(S_dtor,1,n_object)',
        '(HOBJECT n_object) <- S_dtor.ALLOCATIONS', '$node_children(S_dtor,HOBJECT n_object) = eps',
        '$objectprops_at(S_dtor.OBJECTPROPS,n_object) = ([ppropertyslot_tag])',
        '$eager_operation_source_guard(S_dtor,pdestructionoperation)', '$call_descriptors_valid(S_dtor)',
        'S_storage = $typed_int_pause(S_dtor,2,n_object,30000)', '$typed_int_ready(S_storage,2,n_object)',
        '$instance_storage_for(S_storage,n_object) = (pinstancestorage)', 'pinstancestorage.NEXT = 1',
        'pinstancestorage.SLOTS = [ppropertyslot_tag]',
        '$objectprops_at(S_storage.OBJECTPROPS,n_object) = ([ppropertyslot_tag[.STATE = PROP_UNSET]])',
        '(HOBJECT n_object) <- S_storage.ALLOCATIONS', '$node_children(S_storage,HOBJECT n_object) = eps',
        'S_storage.PROPREFS = eps', 'S_storage.STRINGDATA = S_raw.STRINGDATA',
        '$instance_storage_basic(S_storage,pinstancestorage)', '$call_descriptors_valid(S_storage)',
        '$eager_operation_source_guard(S_storage,pdestructionoperation)',
        'S_pair = $typed_int_pause(S_storage,3,n_object,30000)', '$typed_int_ready(S_pair,3,n_object)',
        '$ccn_output(S_pair.EVENTS) = $ptascii("B|C|D|T|M|")',
        'S_pair.RESULT = KNOWN pvalue_member', '$string_bytes(pvalue_member) = ($ptascii("B"))',
        '~((HCELL n_reference) <- S_pair.ALLOCATIONS)', '~((HOBJECT n_object) <- S_pair.ALLOCATIONS)',
        'S_pair.DESTRUCTION.OPERATIONS = eps', 'S_pair.PROPREFS = eps', '$call_descriptors_valid(S_pair)',
        '$class_constant_object_member_entry(S_pair,S_pair.RESULT,expression_class,KNOWN (PSTRING ' + child + '),z,ptask_tail*) = (pclassconstantdesc)',
        'S_warn = $ccn_pause(S_pair,0,30000)', '$ccn_ready(S_warn,0)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CLASS_CONSTANT_RESULT pclassconstantdesc.ORIGIN ' + child + ' $ptascii("B") z',
        '$task_nodes(perrorcall.RESUME) = eps', '$error_call_valid(S_warn,perrorcall)',
        'S_resume = $ccn_pause(S_warn,1,30000)', '$ccn_ready(S_resume,1)',
        '$ccn_output(S_resume.EVENTS) = $ptascii("B|C|D|T|M|H|")',
        'S_global = $global_table_view(S_resume)', '$lookup(S_global.ENV,$ptascii("member250int")) = (n_member)',
        'S_global.STORE[n_member] = DEFINED pvalue_now', '$string_bytes(pvalue_now) = ($ptascii("A"))',
        '$class_constant_notice_valid(S_resume,pclassconstantdesc.ORIGIN,' + child + ',$ptascii("B"),z)',
        'S_value_step = $drive_steps(S_resume,1)', 'S_value_step.COMPLETION = BUDGET',
        'S_value = S_value_step[.COMPLETION = NORMAL]', 'S_value.RESULT = KNOWN (PINT 10)',
        '~$class_constant_notice_protected(S_value,pclassconstantdesc.ORIGIN)',
        'S_done = $drive_steps(S_value,30000)', 'S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = $ptascii("B|C|D|T|M|H|10|Z|")',
        'S_done.CLASSCONSTANTCACHE = eps', 'S_done.CLASSCONSTANTHISTORY = S_raw.CLASSCONSTANTHISTORY',
        '$class_constant_state_valid(S_done)', '$call_descriptors_valid(S_done)',
        'S_zero = $drive_steps(S_storage,0)', 'S_zero.COMPLETION = BUDGET', 'S_zero[.COMPLETION = NORMAL] = S_storage',
        'S_one = $drive_steps(S_storage,1)', 'S_one.COMPLETION = BUDGET',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],30000) = S_done', '$drive_steps(S_one[.COMPLETION = NORMAL],30000) = S_done']
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
